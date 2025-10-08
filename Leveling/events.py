import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Set
import config
from .database import LevelingDatabase
from .utils import (
    get_user_multiplier, calculate_message_xp, is_user_on_cooldown,
    check_achievements, assign_level_roles, create_level_up_embed,
    create_achievement_embed
)

class LevelingEvents(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = LevelingDatabase()
        
        # Voice tracking
        self.voice_sessions: Dict[int, Dict[int, datetime]] = {}  # guild_id -> {user_id: join_time}
        
        # Message cooldowns
        self.message_cooldowns: Dict[int, Dict[int, datetime]] = {}  # guild_id -> {user_id: last_message_time}
        
        # Start background tasks
        self.voice_xp_updater.start()
        self.cleanup_voice_sessions.start()
    
    def cog_unload(self):
        """Cleanup when cog is unloaded"""
        self.voice_xp_updater.cancel()
        self.cleanup_voice_sessions.cancel()
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Handle message XP"""
        # Ignore bots and DMs
        if message.author.bot or not message.guild:
            return
        
        # Check if leveling is enabled for this channel
        guild_config = self.db.get_guild_config(message.guild.id)
        
        # Check disabled channels
        if message.channel.id in guild_config.get('disabled_channels', []):
            return
        
        # Check XP channels (if specified, only give XP in those channels)
        xp_channels = guild_config.get('xp_channels', [])
        if xp_channels and message.channel.id not in xp_channels:
            return
        
        # Check message cooldown
        guild_id = message.guild.id
        user_id = message.author.id
        
        if guild_id not in self.message_cooldowns:
            self.message_cooldowns[guild_id] = {}
        
        now = datetime.now()
        last_message = self.message_cooldowns[guild_id].get(user_id)
        
        if last_message and is_user_on_cooldown(user_id, guild_id, last_message, 
                                               config.LEVELING_CONFIG['message_cooldown']):
            return
        
        # Update cooldown
        self.message_cooldowns[guild_id][user_id] = now
        
        # Calculate XP
        base_xp = calculate_message_xp()
        
        # Apply multipliers
        if hasattr(message.author, 'roles'):  # Ensure it's a Member object
            multiplier = get_user_multiplier(message.author)
            xp_to_give = int(base_xp * multiplier)
        else:
            xp_to_give = base_xp
        
        # Add XP to user
        result = self.db.add_xp(user_id, guild_id, xp_to_give, 'message')
        
        # Check for level up
        if result['leveled_up']:
            await self.handle_level_up(message.author, message.guild, result, guild_config)
        
        # Check for new achievements
        await self.check_and_award_achievements(message.author, message.guild)
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, 
                                   after: discord.VoiceState):
        """Handle voice channel XP tracking"""
        guild_id = member.guild.id
        user_id = member.id
        
        if guild_id not in self.voice_sessions:
            self.voice_sessions[guild_id] = {}
        
        # User joined a voice channel
        if before.channel is None and after.channel is not None:
            # Don't track AFK channels
            if after.channel != member.guild.afk_channel:
                self.voice_sessions[guild_id][user_id] = datetime.now()
                self.db.set_voice_join_time(user_id, guild_id, datetime.now())
        
        # User left a voice channel
        elif before.channel is not None and after.channel is None:
            if user_id in self.voice_sessions[guild_id]:
                # Calculate time spent and award XP
                join_time = self.voice_sessions[guild_id][user_id]
                time_spent = datetime.now() - join_time
                minutes = int(time_spent.total_seconds() / 60)
                
                if minutes > 0:
                    # Calculate voice XP
                    base_xp = minutes * config.LEVELING_CONFIG['exp_per_minute_voice']
                    
                    # Apply multipliers
                    multiplier = get_user_multiplier(member)
                    xp_to_give = int(base_xp * multiplier)
                    
                    # Add XP
                    result = self.db.add_xp(user_id, guild_id, xp_to_give, 'voice')
                    
                    # Check for level up
                    guild_config = self.db.get_guild_config(guild_id)
                    if result['leveled_up']:
                        await self.handle_level_up(member, member.guild, result, guild_config)
                    
                    # Check achievements
                    await self.check_and_award_achievements(member, member.guild)
                
                # Remove from tracking
                del self.voice_sessions[guild_id][user_id]
        
        # User switched channels (but stayed in voice)
        elif (before.channel is not None and after.channel is not None and 
              before.channel != after.channel):
            # Handle AFK channel transitions
            if before.channel == member.guild.afk_channel and after.channel != member.guild.afk_channel:
                # Started participating again
                self.voice_sessions[guild_id][user_id] = datetime.now()
                self.db.set_voice_join_time(user_id, guild_id, datetime.now())
            elif before.channel != member.guild.afk_channel and after.channel == member.guild.afk_channel:
                # Went AFK, calculate XP for time before AFK
                if user_id in self.voice_sessions[guild_id]:
                    join_time = self.voice_sessions[guild_id][user_id]
                    time_spent = datetime.now() - join_time
                    minutes = int(time_spent.total_seconds() / 60)
                    
                    if minutes > 0:
                        base_xp = minutes * config.LEVELING_CONFIG['exp_per_minute_voice']
                        multiplier = get_user_multiplier(member)
                        xp_to_give = int(base_xp * multiplier)
                        
                        result = self.db.add_xp(user_id, guild_id, xp_to_give, 'voice')
                        
                        guild_config = self.db.get_guild_config(guild_id)
                        if result['leveled_up']:
                            await self.handle_level_up(member, member.guild, result, guild_config)
                        
                        await self.check_and_award_achievements(member, member.guild)
                    
                    # Remove from tracking since they're AFK
                    del self.voice_sessions[guild_id][user_id]
    
    async def handle_level_up(self, member: discord.Member, guild: discord.Guild, 
                            result: Dict, guild_config: Dict):
        """Handle level up announcement and role assignment"""
        new_level = result['new_level']
        old_level = result['old_level']
        
        # Assign level roles
        level_roles = guild_config.get('level_roles', {})
        if level_roles:
            await assign_level_roles(member, new_level, level_roles)
        
        # Send level up announcement
        if guild_config.get('announcement_enabled', True):
            channel_id = guild_config.get('level_up_channel')
            channel = None
            
            if channel_id:
                channel = guild.get_channel(channel_id)
            
            if not channel:
                # Try to find a general channel
                for ch in guild.text_channels:
                    if any(name in ch.name.lower() for name in ['general', 'chat', 'main', 'level']):
                        channel = ch
                        break
                
                # If still no channel, use the first available text channel
                if not channel and guild.text_channels:
                    channel = guild.text_channels[0]
            
            if channel:
                try:
                    # Check for custom message
                    custom_message = guild_config.get('custom_message')
                    if custom_message:
                        # Replace placeholders
                        message = custom_message.replace('{user}', member.mention)
                        message = message.replace('{level}', str(new_level))
                        message = message.replace('{old_level}', str(old_level))
                        await channel.send(message)
                    else:
                        # Default embed
                        embed = create_level_up_embed(member, old_level, new_level, result['xp_gained'])
                        await channel.send(embed=embed)
                
                except discord.Forbidden:
                    pass  # Bot doesn't have permission to send messages
                except discord.HTTPException:
                    pass  # Rate limited or other issue
    
    async def check_and_award_achievements(self, member: discord.Member, guild: discord.Guild):
        """Check and award new achievements"""
        user_stats = self.db.get_user_stats(member.id, guild.id)
        new_achievements = check_achievements(user_stats, config.ACHIEVEMENTS)
        
        for achievement_id in new_achievements:
            # Unlock achievement
            if self.db.unlock_achievement(member.id, guild.id, achievement_id):
                achievement = config.ACHIEVEMENTS[achievement_id]
                
                # Award XP reward if any
                if achievement.get('reward_xp', 0) > 0:
                    self.db.add_xp(member.id, guild.id, achievement['reward_xp'], 'achievement')
                
                # Send achievement announcement
                guild_config = self.db.get_guild_config(guild.id)
                if guild_config.get('announcement_enabled', True):
                    channel_id = guild_config.get('level_up_channel')
                    channel = guild.get_channel(channel_id) if channel_id else None
                    
                    if not channel:
                        # Find suitable channel
                        for ch in guild.text_channels:
                            if any(name in ch.name.lower() for name in ['general', 'chat', 'achievements']):
                                channel = ch
                                break
                        
                        if not channel and guild.text_channels:
                            channel = guild.text_channels[0]
                    
                    if channel:
                        try:
                            embed = create_achievement_embed(member, achievement_id, achievement)
                            await channel.send(embed=embed)
                        except (discord.Forbidden, discord.HTTPException):
                            pass
    
    @tasks.loop(minutes=1)
    async def voice_xp_updater(self):
        """Update XP for users in voice channels every minute"""
        for guild_id, users in self.voice_sessions.items():
            guild = self.bot.get_guild(guild_id)
            if not guild:
                continue
            
            for user_id, join_time in list(users.items()):
                member = guild.get_member(user_id)
                if not member:
                    # User left guild, remove from tracking
                    del users[user_id]
                    continue
                
                # Check if user is still in voice and not AFK
                if (member.voice and member.voice.channel and 
                    member.voice.channel != guild.afk_channel):
                    
                    # Check if it's time to give XP (every minute)
                    time_since_join = datetime.now() - join_time
                    if time_since_join.total_seconds() >= 60:
                        # Give 1 minute worth of XP
                        base_xp = config.LEVELING_CONFIG['exp_per_minute_voice']
                        multiplier = get_user_multiplier(member)
                        xp_to_give = int(base_xp * multiplier)
                        
                        result = self.db.add_xp(user_id, guild_id, xp_to_give, 'voice')
                        
                        # Check for level up
                        guild_config = self.db.get_guild_config(guild_id)
                        if result['leveled_up']:
                            await self.handle_level_up(member, guild, result, guild_config)
                        
                        # Check achievements
                        await self.check_and_award_achievements(member, guild)
                        
                        # Update join time for next minute
                        users[user_id] = datetime.now()
                else:
                    # User left voice or went AFK
                    del users[user_id]
    
    @tasks.loop(hours=1)
    async def cleanup_voice_sessions(self):
        """Clean up old voice sessions"""
        now = datetime.now()
        
        for guild_id, users in list(self.voice_sessions.items()):
            for user_id, join_time in list(users.items()):
                # Remove sessions older than 1 hour
                if (now - join_time).total_seconds() > 3600:
                    del users[user_id]
            
            # Remove empty guild entries
            if not users:
                del self.voice_sessions[guild_id]
    
    @voice_xp_updater.before_loop
    async def before_voice_xp_updater(self):
        """Wait for bot to be ready before starting task"""
        await self.bot.wait_until_ready()
    
    @cleanup_voice_sessions.before_loop
    async def before_cleanup_voice_sessions(self):
        """Wait for bot to be ready before starting task"""
        await self.bot.wait_until_ready()

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(LevelingEvents(bot))