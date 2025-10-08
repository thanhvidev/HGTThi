"""
Main integration file for the leveling system.

This file contains the main cog that combines all leveling functionality
and can be loaded directly into the Discord bot.
"""

import discord
from discord.ext import commands
import asyncio
import logging
from .commands import LevelingCommands
from .events import LevelingEvents
from .database import LevelingDatabase

logger = logging.getLogger(__name__)

class LevelingSystem(commands.Cog):
    """Main leveling system cog that combines all functionality"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = LevelingDatabase()
        
        # Initialize sub-components
        self.commands_cog = None
        self.events_cog = None
        
        logger.info("✅ Leveling system initialized")
    
    async def cog_load(self):
        """Called when the cog is loaded"""
        try:
            # Add the commands cog
            self.commands_cog = LevelingCommands(self.bot)
            await self.bot.add_cog(self.commands_cog)
            
            # Add the events cog
            self.events_cog = LevelingEvents(self.bot)
            await self.bot.add_cog(self.events_cog)
            
            logger.info("✅ Leveling system components loaded successfully")
        
        except Exception as e:
            logger.error(f"❌ Failed to load leveling system components: {e}")
            raise
    
    async def cog_unload(self):
        """Called when the cog is unloaded"""
        try:
            # Remove sub-cogs
            if self.commands_cog:
                await self.bot.remove_cog('LevelingCommands')
            
            if self.events_cog:
                await self.bot.remove_cog('LevelingEvents')
            
            logger.info("✅ Leveling system components unloaded")
        
        except Exception as e:
            logger.error(f"❌ Error unloading leveling system: {e}")
    
    @commands.command(name="levelstatus", hidden=True)
    @commands.is_owner()
    async def level_status(self, ctx: commands.Context):
        """Check leveling system status (Owner only)"""
        embed = discord.Embed(
            title="🔧 Leveling System Status",
            color=discord.Color.blue()
        )
        
        # Check database
        try:
            total_users = 0
            guild_count = 0
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM leveling_stats")
                total_users = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(DISTINCT guild_id) FROM leveling_stats")
                guild_count = cursor.fetchone()[0]
            
            embed.add_field(
                name="📊 Database Stats",
                value=f"Total Users: {total_users:,}\nGuilds: {guild_count:,}",
                inline=True
            )
            
        except Exception as e:
            embed.add_field(
                name="❌ Database Error",
                value=str(e)[:100],
                inline=True
            )
        
        # Check cog status
        commands_loaded = self.commands_cog is not None
        events_loaded = self.events_cog is not None
        
        embed.add_field(
            name="🔌 Components",
            value=f"Commands: {'✅' if commands_loaded else '❌'}\nEvents: {'✅' if events_loaded else '❌'}",
            inline=True
        )
        
        # Voice tracking status
        if self.events_cog:
            voice_sessions = len(self.events_cog.voice_sessions)
            embed.add_field(
                name="🎤 Voice Tracking",
                value=f"Active Sessions: {voice_sessions}",
                inline=True
            )
        
        embed.set_footer(text="Leveling System v1.0.0")
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    """Setup function to load the leveling system"""
    await bot.add_cog(LevelingSystem(bot))
    logger.info("🎯 Leveling system main cog added to bot")