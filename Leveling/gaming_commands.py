#!/usr/bin/env python3
"""
Gaming/Cypher Themed Leveling Commands
Tối ưu hóa các lệnh với theme gaming đẹp mắt
"""

import discord
from discord.ext import commands
from typing import Optional, Union, List
import asyncio
from datetime import datetime
import config
from .database import LevelingDatabase
from .gaming_image_generator import GamingImageGenerator, create_gaming_profile, create_gaming_rank_card
from .achievement_generator import AchievementCardGenerator, create_achievement_card
from .utils import format_time, format_number, get_achievement_emoji

class GamingLevelingCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = LevelingDatabase()
        self.gaming_generator = GamingImageGenerator()
        self.achievement_generator = AchievementCardGenerator()
        
        # Gaming emojis for better UX
        self.gaming_emojis = {
            'profile': '👤',
            'rank': '🏆', 
            'achievements': '🎮',
            'leaderboard': '📊',
            'level_up': '⚡',
            'xp': '✨',
            'loading': '🔄'
        }

    @commands.hybrid_command(name="gprofile", aliases=["gp", "profile"], 
                           description="🎮 Xem gaming profile với thiết kế cyber đẹp mắt")
    async def gaming_profile_command(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        """Display user's gaming profile with cyber theme"""
        target_member = member or ctx.author
        
        if target_member.bot:
            embed = self._create_error_embed("❌ System Error", "Bot không có dữ liệu player!")
            return await ctx.send(embed=embed)
        
        # Send loading message
        loading_msg = await ctx.send(f"{self.gaming_emojis['loading']} **Đang tải player data...**")
        
        try:
            # Get user stats
            stats = self.db.get_user_stats(target_member.id, ctx.guild.id)
            
            # Get user rank
            user_rank = await self._get_user_rank(target_member.id, ctx.guild.id)
            total_members = len([m for m in ctx.guild.members if not m.bot])
            
            # Generate gaming profile image
            profile_image = await create_gaming_profile(target_member, stats, user_rank, total_members)
            
            # Create gaming-themed embed
            embed = self._create_gaming_profile_embed(target_member, stats, user_rank, total_members)
            
            # Send image with embed
            file = discord.File(profile_image, filename="gaming_profile.png")
            embed.set_image(url="attachment://gaming_profile.png")
            
            # Update loading message
            await loading_msg.edit(content=None, embed=embed, attachments=[file])
        
        except Exception as e:
            print(f"Gaming profile error: {e}")
            # Fallback to text-only embed
            embed = self._create_fallback_profile_embed(target_member, stats, user_rank, total_members)
            await loading_msg.edit(content=None, embed=embed)

    @commands.hybrid_command(name="grank", aliases=["gr", "rank"],
                           description="🏆 Xem gaming rank card nhanh")  
    async def gaming_rank_command(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        """Display compact gaming rank card"""
        target_member = member or ctx.author
        
        if target_member.bot:
            embed = self._create_error_embed("❌ Access Denied", "Bot không có player rank!")
            return await ctx.send(embed=embed)
        
        try:
            # Get user stats and rank
            stats = self.db.get_user_stats(target_member.id, ctx.guild.id)
            user_rank = await self._get_user_rank(target_member.id, ctx.guild.id)
            
            # Generate gaming rank card
            rank_image = await create_gaming_rank_card(target_member, stats, user_rank)
            
            # Create minimal embed
            embed = discord.Embed(color=self._get_level_color(stats['level']))
            embed.set_author(name=f"{target_member.display_name} - Gaming Rank", 
                           icon_url=target_member.display_avatar.url)
            
            # Send image
            file = discord.File(rank_image, filename="gaming_rank.png")
            embed.set_image(url="attachment://gaming_rank.png")
            
            await ctx.send(file=file, embed=embed)
            
        except Exception as e:
            print(f"Gaming rank error: {e}")
            # Fallback text rank
            embed = self._create_text_rank_embed(target_member, stats, user_rank)
            await ctx.send(embed=embed)

    @commands.hybrid_command(name="gachievements", aliases=["gach", "achievements"],
                           description="🎮 Xem gaming achievements với thiết kế đẹp")
    async def gaming_achievements_command(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        """Display user's gaming achievements"""
        target_member = member or ctx.author
        
        if target_member.bot:
            embed = self._create_error_embed("❌ Invalid Target", "Bot không có achievement system!")
            return await ctx.send(embed=embed)
        
        # Get user stats
        stats = self.db.get_user_stats(target_member.id, ctx.guild.id)
        achievements = stats.get('achievements', [])
        
        if not achievements:
            embed = self._create_error_embed("🎮 No Achievements", 
                                           f"{target_member.display_name} chưa unlock achievement nào!")
            return await ctx.send(embed=embed)
        
        try:
            # Generate achievement showcase
            showcase_image = await self.achievement_generator.create_achievement_showcase(
                target_member, achievements
            )
            
            # Create embed
            embed = self._create_achievements_embed(target_member, achievements)
            
            # Send image
            file = discord.File(showcase_image, filename="gaming_achievements.png")
            embed.set_image(url="attachment://gaming_achievements.png")
            
            await ctx.send(file=file, embed=embed)
            
        except Exception as e:
            print(f"Gaming achievements error: {e}")
            # Fallback text achievements
            embed = self._create_text_achievements_embed(target_member, achievements)
            await ctx.send(embed=embed)

    @commands.hybrid_command(name="gleaderboard", aliases=["glb", "leaderboard"],
                           description="📊 Xem gaming leaderboard server")
    async def gaming_leaderboard_command(self, ctx: commands.Context, sort_by: str = "level"):
        """Display gaming leaderboard"""
        valid_sorts = ["level", "xp", "messages", "voice"]
        if sort_by not in valid_sorts:
            sort_by = "level"
        
        # Get leaderboard data
        leaderboard = self.db.get_leaderboard(ctx.guild.id, sort_by=sort_by, limit=15)
        
        if not leaderboard:
            embed = self._create_error_embed("📊 Empty Server", "Server này chưa có dữ liệu player nào!")
            return await ctx.send(embed=embed)
        
        # Create gaming leaderboard embed
        embed = self._create_gaming_leaderboard_embed(ctx.guild, leaderboard, sort_by)
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="gunlock", aliases=["unlock"],
                           description="🏆 Mô phỏng unlock achievement (owner only)")
    @commands.is_owner()
    async def gaming_unlock_achievement(self, ctx: commands.Context, member: discord.Member, achievement_id: str):
        """Simulate achievement unlock (owner only)"""
        if achievement_id not in config.ACHIEVEMENTS:
            available = ", ".join(list(config.ACHIEVEMENTS.keys())[:5])
            embed = self._create_error_embed("❌ Invalid Achievement", 
                                           f"Achievement không tồn tại! Available: {available}...")
            return await ctx.send(embed=embed)
        
        try:
            # Unlock achievement in database
            if self.db.unlock_achievement(member.id, ctx.guild.id, achievement_id):
                # Generate achievement unlock card
                achievement_card = await create_achievement_card(
                    achievement_id, member, datetime.now()
                )
                
                # Send achievement notification
                file = discord.File(achievement_card, filename="achievement_unlock.png")
                
                embed = discord.Embed(
                    title="🎉 Achievement Unlocked!",
                    description=f"{member.display_name} đã unlock achievement mới!",
                    color=0x00ff00
                )
                embed.set_image(url="attachment://achievement_unlock.png")
                
                await ctx.send(file=file, embed=embed)
            else:
                embed = self._create_error_embed("⚠️ Already Unlocked", 
                                               f"{member.display_name} đã có achievement này rồi!")
                await ctx.send(embed=embed)
                
        except Exception as e:
            print(f"Gaming unlock error: {e}")
            embed = self._create_error_embed("❌ System Error", "Lỗi khi unlock achievement!")
            await ctx.send(embed=embed)

    # Helper Methods
    async def _get_user_rank(self, user_id: int, guild_id: int) -> int:
        """Get user's rank in guild"""
        leaderboard = self.db.get_leaderboard(guild_id, limit=1000)
        for entry in leaderboard:
            if entry['user_id'] == user_id:
                return entry['rank']
        return len(leaderboard) + 1

    def _create_error_embed(self, title: str, description: str) -> discord.Embed:
        """Create gaming-themed error embed"""
        embed = discord.Embed(
            title=title,
            description=description,
            color=0xff0040  # Gaming red
        )
        embed.set_footer(text="Gaming System v2.0", icon_url="https://cdn.discordapp.com/emojis/1234567890.png")
        return embed

    def _create_gaming_profile_embed(self, member: discord.Member, stats: Dict, 
                                   rank: int, total_members: int) -> discord.Embed:
        """Create gaming-themed profile embed"""
        level_tier = self._get_level_tier_name(stats['level'])
        embed_color = self._get_level_color(stats['level'])
        
        embed = discord.Embed(
            title=f"🎮 Gaming Profile - {member.display_name}",
            description=f"**{level_tier}** • Level {stats['level']} Player",
            color=embed_color
        )
        
        # Gaming stats
        xp_needed = self._calculate_xp_for_next_level(stats['level'])
        progress_percent = (stats['xp'] / xp_needed * 100) if xp_needed > 0 else 100
        
        embed.add_field(
            name="⚡ Combat Stats",
            value=f"""**Level:** {stats['level']} ({level_tier})
**Rank:** #{rank:,} / {total_members:,}
**XP:** {stats['xp']:,} / {xp_needed:,} ({progress_percent:.1f}%)
**Total XP:** {format_number(stats['total_xp'])}""",
            inline=True
        )
        
        embed.add_field(
            name="📊 Activity Stats", 
            value=f"""**Messages:** {format_number(stats['messages'])}
**Voice Time:** {format_time(stats['voice_minutes'])}
**Achievements:** {len(stats.get('achievements', []))}/{len(config.ACHIEVEMENTS)}
**Daily Streak:** {stats.get('daily_streak', 0)} days""",
            inline=True
        )
        
        # Recent achievements
        if stats.get('achievements'):
            recent = stats['achievements'][-3:]
            achievement_text = ""
            for ach_id in recent:
                achievement = config.ACHIEVEMENTS.get(ach_id, {})
                if achievement:
                    rarity = achievement.get('rarity', 'common')
                    rarity_emoji = self._get_rarity_emoji(rarity)
                    achievement_text += f"{rarity_emoji} {achievement['name']}\n"
            
            embed.add_field(
                name="🏆 Recent Unlocks",
                value=achievement_text or "No achievements yet",
                inline=False
            )
        
        embed.set_footer(text=f"Gaming System • Player ID: {member.id}")
        embed.set_thumbnail(url=member.display_avatar.url)
        
        return embed

    def _create_fallback_profile_embed(self, member: discord.Member, stats: Dict,
                                     rank: int, total_members: int) -> discord.Embed:
        """Create text-only fallback profile embed"""
        embed = discord.Embed(
            title=f"🎯 Profile - {member.display_name}",
            color=self._get_level_color(stats['level'])
        )
        
        xp_needed = self._calculate_xp_for_next_level(stats['level'])
        progress_percent = (stats['xp'] / xp_needed * 100) if xp_needed > 0 else 100
        
        embed.description = f"""
**Level:** {stats['level']} • **Rank:** #{rank}/{total_members}
**XP:** {stats['xp']:,} / {xp_needed:,} ({progress_percent:.1f}%)
**Messages:** {format_number(stats['messages'])} • **Voice:** {format_time(stats['voice_minutes'])}
**Achievements:** {len(stats.get('achievements', []))}/{len(config.ACHIEVEMENTS)}
"""
        
        embed.set_thumbnail(url=member.display_avatar.url)
        return embed

    def _create_text_rank_embed(self, member: discord.Member, stats: Dict, rank: int) -> discord.Embed:
        """Create text-only rank embed"""
        embed = discord.Embed(
            title=f"🏆 Rank - {member.display_name}",
            color=self._get_level_color(stats['level'])
        )
        
        xp_needed = self._calculate_xp_for_next_level(stats['level'])
        progress = (stats['xp'] / xp_needed * 100) if xp_needed > 0 else 100
        
        embed.description = f"""
**Level {stats['level']}** • Rank #{rank}
**{stats['xp']:,} / {xp_needed:,} XP** ({progress:.1f}%)
**Total XP:** {format_number(stats['total_xp'])}
"""
        
        embed.set_thumbnail(url=member.display_avatar.url)
        return embed

    def _create_achievements_embed(self, member: discord.Member, achievements: List[str]) -> discord.Embed:
        """Create achievements showcase embed"""
        total_xp = sum(config.ACHIEVEMENTS.get(aid, {}).get('reward_xp', 0) for aid in achievements)
        
        embed = discord.Embed(
            title=f"🎮 Gaming Achievements - {member.display_name}",
            description=f"**{len(achievements)}/{len(config.ACHIEVEMENTS)}** achievements unlocked • **{total_xp:,} XP** earned",
            color=0x00ff88
        )
        
        # Group by rarity
        by_rarity = {}
        for ach_id in achievements:
            achievement = config.ACHIEVEMENTS.get(ach_id, {})
            rarity = achievement.get('rarity', 'common')
            if rarity not in by_rarity:
                by_rarity[rarity] = []
            by_rarity[rarity].append(achievement['name'])
        
        # Display by rarity
        for rarity, names in by_rarity.items():
            if names:
                rarity_emoji = self._get_rarity_emoji(rarity)
                embed.add_field(
                    name=f"{rarity_emoji} {rarity.title()} ({len(names)})",
                    value="\n".join(names[:5]) + ("..." if len(names) > 5 else ""),
                    inline=True
                )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        return embed

    def _create_text_achievements_embed(self, member: discord.Member, achievements: List[str]) -> discord.Embed:
        """Create text-only achievements embed"""
        embed = discord.Embed(
            title=f"🏆 Achievements - {member.display_name}",
            color=0x00ff88
        )
        
        achievement_list = []
        for ach_id in achievements[-10:]:  # Show last 10
            achievement = config.ACHIEVEMENTS.get(ach_id, {})
            if achievement:
                rarity_emoji = self._get_rarity_emoji(achievement.get('rarity', 'common'))
                achievement_list.append(f"{rarity_emoji} {achievement['name']}")
        
        embed.description = "\n".join(achievement_list) if achievement_list else "No achievements unlocked"
        embed.add_field(name="Total", value=f"{len(achievements)}/{len(config.ACHIEVEMENTS)}", inline=True)
        
        return embed

    def _create_gaming_leaderboard_embed(self, guild: discord.Guild, leaderboard: List[Dict], 
                                       sort_by: str) -> discord.Embed:
        """Create gaming leaderboard embed"""
        embed = discord.Embed(
            title=f"🏆 Gaming Leaderboard - {guild.name}",
            description=f"Top players sorted by **{sort_by}**",
            color=0x00ff88
        )
        
        medals = ["🥇", "🥈", "🥉"]
        
        for i, entry in enumerate(leaderboard[:15]):
            try:
                user = self.bot.get_user(entry['user_id'])
                if not user:
                    continue
                
                medal = medals[i] if i < 3 else f"`{i+1:2d}.`"
                
                if sort_by == "level":
                    value = f"Level {entry['level']}"
                elif sort_by == "xp":
                    value = f"{format_number(entry['total_xp'])} XP"
                elif sort_by == "messages":
                    value = f"{format_number(entry['messages'])} msgs"
                else:  # voice
                    value = format_time(entry['voice_minutes'])
                
                embed.add_field(
                    name=f"{medal} {user.display_name}",
                    value=value,
                    inline=True
                )
                
                if (i + 1) % 3 == 0:  # Add empty field every 3 for better formatting
                    embed.add_field(name="", value="", inline=True)
            except Exception:
                continue
        
        embed.set_footer(text=f"Gaming System • {len(leaderboard)} active players")
        return embed

    def _get_level_tier_name(self, level: int) -> str:
        """Get level tier name for display"""
        if level >= 100:
            return "🌟 CHALLENGER"
        elif level >= 75:
            return "💎 GRANDMASTER"
        elif level >= 50:
            return "⚡ MASTER"
        elif level >= 40:
            return "💠 DIAMOND"
        elif level >= 30:
            return "⚪ PLATINUM"
        elif level >= 20:
            return "🟨 GOLD"
        elif level >= 10:
            return "⚫ SILVER"
        else:
            return "🟤 BRONZE"

    def _get_level_color(self, level: int) -> int:
        """Get color based on level tier"""
        tier_colors = {
            "bronze": 0xCD7F32,
            "silver": 0xC0C0C0,
            "gold": 0xFFD700,
            "platinum": 0xE5E4E2,
            "diamond": 0xB9F2FF,
            "master": 0xFF1493,
            "grandmaster": 0x8A2BE2,
            "challenger": 0xFFFFFF
        }
        
        if level >= 100:
            return tier_colors["challenger"]
        elif level >= 75:
            return tier_colors["grandmaster"]
        elif level >= 50:
            return tier_colors["master"]
        elif level >= 40:
            return tier_colors["diamond"]
        elif level >= 30:
            return tier_colors["platinum"]
        elif level >= 20:
            return tier_colors["gold"]
        elif level >= 10:
            return tier_colors["silver"]
        else:
            return tier_colors["bronze"]

    def _get_rarity_emoji(self, rarity: str) -> str:
        """Get emoji for achievement rarity"""
        rarity_emojis = {
            "common": "⚪",
            "uncommon": "🟢",
            "rare": "🔵",
            "epic": "🟣", 
            "legendary": "🟠",
            "mythic": "🟡"
        }
        return rarity_emojis.get(rarity, "⚪")

    def _calculate_xp_for_next_level(self, level: int) -> int:
        """Calculate XP required for next level"""
        if level == 0:
            return 100
        return int(100 * (1.2 ** (level - 1)))


async def setup(bot: commands.Bot):
    """Setup function for cog loading"""
    await bot.add_cog(GamingLevelingCommands(bot))