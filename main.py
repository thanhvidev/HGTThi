import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread
from discord.utils import get
import sys
import config
import json
import asyncio
import logging
from dotenv import load_dotenv
from utils.checks import is_bot_owner, is_admin, is_mod
from datetime import datetime, timezone



# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_prefix(client, message):
    if not message.guild:
        return config.BOT_PREFIX
    
    try:
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
            # Nếu guild có prefix thì trả về list [prefix.lower, prefix.upper]
            prefix = prefixes.get(str(message.guild.id), ['z', 'Z'])
            return commands.when_mentioned_or(*prefix)(client, message)
    except:
        # Nếu lỗi (file chưa có / bị hỏng) thì fallback sang prefix mặc định
        return commands.when_mentioned_or(config.BOT_PREFIX)(client, message)

# Setup bot with optimized intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.messages = True
intents.reactions = True
intents.voice_states = True

client = commands.Bot(
    command_prefix=get_prefix, 
    intents=intents,
    help_command=None,  # We'll use custom help command
    case_insensitive=True,
    max_messages=5000,  # Message cache for better performance
)

# Store bot token
BOT_TOKEN = config.BOT_TOKEN
BOT_OWNER_IDS = config.BOT_OWNER_IDS



# Global rate limiter for commands
command_cooldowns = {}

async def load_extensions():
    """Load all extensions/cogs dynamically"""
    extensions_loaded = 0
    extensions_failed = []
    
    # List of cogs to import
    cog_classes = [
        # Commands.Check
        ('Commands.Check.avatar', 'Avatar'),
        ('Commands.Check.banner', 'Banner'),
        ('Commands.Check.bxh', 'Bxh'),
        ('Commands.Check.stats', 'Stats'),
        
        # Commands.Funs
        # ('Commands.Funs.fun', 'Fun'),
        # ('Commands.Funs.hpbd', 'HPBD'),
        # ('Commands.Funs.loto', 'Loto'),
        # ('Commands.Funs.ship', 'Ship'),
        # ('Commands.Funs.theard_food', 'Theard_food'),
        # ('Commands.Funs.gameso', 'Gameso'),
        # ('Commands.Funs.gametu', 'Gametu'),
        # ('Commands.Funs.noitutv', 'Noitutv'),
        
        # Commands.Mod
        # ('Commands.Mod.automess', 'AutoMessage'),
        # ('Commands.Mod.confession', 'Confession'),
        ('Commands.Mod.emoji', 'Emoji'),
        ('Commands.Mod.giveaway', 'Giveaway'),
        ('Commands.Mod.help', 'Help'),
        # ('Commands.Mod.lock', 'Lock'),
        ('Commands.Mod.moderation', 'Moderation'),
        # ('Commands.Mod.nsfw', 'Nsfw'),
        ('Commands.Mod.ping', 'Ping'),
        ('Commands.Mod.prefix', 'Prefix'),
        ('Commands.Mod.reaction', 'Reaction'),
        ('Commands.Mod.reponse', 'Reponse'),
        ('Commands.Mod.role', 'Role'),
        ('Commands.Mod.say', 'Say'),
        ('Commands.Mod.server', 'Server'),
        ('Commands.Mod.snipe', 'Snipe'),
        # ('Commands.Mod.welcome', 'Welcome'),
        ('Commands.Mod.toggle', 'Toggle'),
        ('Commands.Mod.link_invite', 'InviteLink'),
        ('Commands.Mod.giveaway_option', 'GiveAway_Option'),
        
        # Commands.More
        # ('Commands.More.instagram', 'Instagram'),
        # ('Commands.More.speak', 'Speak'),
        # ('Commands.More.marry', 'Marry'),
        # ('Commands.More.tiktok', 'Tiktok'),
        # ('Commands.More.facebook', 'Facebook'),
        
        # Economy.Gambles
        # ('Economy.Gambles.baucua', 'Baucua'),
        # ('Economy.Gambles.blackjack', 'Blackjack'),
        # ('Economy.Gambles.bet', 'Bet'),
        # ('Economy.Gambles.coinflip', 'Coinflip'),
        # ('Economy.Gambles.slot', 'Slot'),
        # ('Economy.Gambles.taixiu', 'Taixiu'),
        # ('Economy.Gambles.vietlott', 'Vietlott'),
        # ('Economy.Gambles.pikachu', 'Pikachu'),
        # ('Economy.Gambles.roulette', 'Roulette'),
        
        # Economy.Relax
        # ('Economy.Relax.keobuabao', 'KeoBuaBao'),
        # ('Economy.Relax.dhbc', 'Dhbc'),
        # ('Economy.Relax.drop', 'DropPickup'),
        # ('Economy.Relax.lamtoannhanh', 'Lamtoan'),
        # ('Economy.Relax.vuatiengviet', 'Vtv'),
        
        # Economy
        # ('Economy.economy', 'Economy'),
        # ('Economy.shop', 'Shop'),
        
        # Events
        # ('Events.Fishing.eventfish', 'EventFish'),
        # ('Events.Fishing.fishingshop', 'Fishingshop'),
        # ('Events.Trungthu.lambanh', 'Lambanh'),
        # ('Events.Halloween.cooking_candy', 'Naukeo'),
        # ('Events.Halloween.sanma', 'Sanma'),
        # ('Events.Event_30_4.cauhoi_30_4', 'Cauhoi30_4'),
        # ('Events.Event_30_4.daily_30_4', 'Daily_30_4'),
        # ('Events.Event_30_4.checkin', 'Checkin'),
        # ('Events.level', 'Level'),
        # ('Events.quest', 'Quest'),
        # ('Events.ve', 'Ve'),
        # ('Events.velenh', 'Velenh'),
        # ('Events.Valentine_2025.unbox', 'Valentine2025'),
        ('Events.Trungthu_2025.lambanh', 'Lambanh'),  
        ('Events.Trungthu_2025.quaylongden', 'Quaylongden'),      

        # Users
        ('Users.Me.bio', 'Bio'),
        ('Users.Me.sinhnhat', 'Birthday'),

        # Leveling System
        ('Leveling.level_status', 'LevelingSystem'),
    
    ]

    # Load cogs one by one
    for module_path, class_name in cog_classes:
        try:
            # Dynamic import
            module = __import__(module_path, fromlist=[class_name])
            cog_class = getattr(module, class_name)
            
            # Add cog
            await client.add_cog(cog_class(client))
            extensions_loaded += 1
            logger.info(f"✅ Loaded cog: {class_name} from {module_path}")
            
        except ImportError as e:
            extensions_failed.append((f"{module_path}.{class_name}", f"Import error: {str(e)}"))
            logger.error(f"❌ Failed to import {module_path}.{class_name}: {e}")
        except AttributeError as e:
            extensions_failed.append((f"{module_path}.{class_name}", f"Class not found: {str(e)}"))
            logger.error(f"❌ Class {class_name} not found in {module_path}: {e}")
        except Exception as e:
            extensions_failed.append((f"{module_path}.{class_name}", f"Unknown error: {str(e)}"))
            logger.error(f"❌ Failed to load cog {class_name}: {e}")
    
    logger.info(f"Extensions loaded: {extensions_loaded}, Failed: {len(extensions_failed)}")
    if extensions_failed:
        logger.info("Failed extensions:")
        for name, error in extensions_failed[:10]:  # Show first 10 errors
            logger.error(f"  - {name}: {error}")


@client.event
async def on_ready():
    """Bot ready event handler"""
    await client.wait_until_ready()
    
    # Set bot start time
    client.start_time = datetime.now(timezone.utc)
    
    if client.user is not None:
        logger.info(f'✅ Bot logged in as {client.user} (ID: {client.user.id})')
    else:
        logger.info('✅ Bot logged in, but client.user is None')
    logger.info(f'📊 Connected to {len(client.guilds)} guilds')
    
    # Initialize databases for all guilds
    for guild in client.guilds:
        try:
            # This will create database if it doesn't exist
            # pool = db_manager.get_pool(guild.id)
            logger.info(f"📁 Initialized database for guild: {guild.name} (ID: {guild.id})")
        except Exception as e:
            logger.error(f"❌ Failed to initialize database for guild {guild.id}: {e}")
    
    # Set bot presence
    await client.change_presence(
        activity=discord.Streaming(
            name="𝗛𝗮̣𝘁 𝗚𝗶𝗼̂́𝗻𝗴 𝗧𝗮̂𝗺 𝗧𝗵𝗮̂̀𝗻 | zhelp",
            url="https://www.twitch.tv/thanhvidev"
        )
    )
    
    # Initialize default prefixes file if not exists
    if not os.path.exists('prefixes.json'):
        default_prefixes = {}
        for guild in client.guilds:
            default_prefixes[str(guild.id)] = [
                config.BOT_PREFIX.lower(),
                config.BOT_PREFIX.upper()
            ]
        with open('prefixes.json', 'w') as f:
            json.dump(default_prefixes, f, indent=4)
    
    # Load all extensions
    await load_extensions()

    # Sync slash commands
    try:
        # Lấy tất cả commands hiện tại
        current_commands = await client.tree.fetch_commands()
        
        # Tìm Entry Point command nếu có
        entry_point = None
        for cmd in current_commands:
            if hasattr(cmd, 'is_entry_point') and cmd.is_entry_point:
                entry_point = cmd
                break
        
        # Sync commands
        if entry_point:
            # Nếu có Entry Point, sync riêng lẻ
            synced = await client.tree.sync()
        else:
            # Sync bình thường
            synced = await client.tree.sync()
            
        logger.info(f"🔄 Synced {len(synced)} slash commands")
    except discord.HTTPException as e:
        if "Entry Point command" in str(e):
            logger.warning("⚠️ Entry Point command conflict, commands may not sync properly")
            # Có thể thử sync từng guild riêng lẻ
            for guild in client.guilds:
                try:
                    await client.tree.sync(guild=guild)
                except:
                    pass
        else:
            logger.error(f"❌ Failed to sync commands: {e}")

@client.event
async def on_guild_join(guild):
    """Handle bot joining a new guild"""
    logger.info(f"🎉 Joined new guild: {guild.name} (ID: {guild.id})")
    
    # Initialize database for new guild
    try:
        pool = db_manager.get_pool(guild.id)
        logger.info(f"📁 Created database for new guild: {guild.name}")
    except Exception as e:
        logger.error(f"❌ Failed to create database for guild {guild.id}: {e}")
    
    # Add default prefix
    try:
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
        prefixes[str(guild.id)] = [
            config.BOT_PREFIX.lower(),
            config.BOT_PREFIX.upper()
        ]
        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)
    except Exception as e:
        logger.error(f"Failed to set default prefix: {e}")

@client.event
async def on_guild_remove(guild):
    """Handle bot leaving a guild"""
    logger.info(f"👋 Left guild: {guild.name} (ID: {guild.id})")
    
    # Optional: Keep database for potential rejoin
    # If you want to delete data, uncomment below:
    # db_path = db_manager.get_guild_db_path(guild.id)
    # if os.path.exists(db_path):
    #     os.remove(db_path)
    #     logger.info(f"🗑️ Deleted database for guild {guild.id}")

# @client.event
# async def on_command_error(ctx, error):
#     """Global error handler"""
#     if isinstance(error, commands.CommandNotFound):
#         return  # Ignore command not found
#     elif isinstance(error, commands.MissingRequiredArgument):
#         await ctx.send(f"❌ Thiếu tham số: `{error.param.name}`")
#     elif isinstance(error, commands.BadArgument):
#         await ctx.send(f"❌ Tham số không hợp lệ: {error}")
#     elif isinstance(error, commands.CommandOnCooldown):
#         await ctx.send(f"⏱️ Vui lòng đợi {error.retry_after:.1f}s để dùng lệnh này")
#     elif isinstance(error, commands.CheckFailure):
#         await ctx.send("❌ Bạn không có quyền sử dụng lệnh này")
#     elif isinstance(error, commands.DisabledCommand):
#         await ctx.send("❌ Lệnh này đã bị tắt")
#     else:
#         logger.error(f"Unhandled error in command {ctx.command}: {error}", exc_info=True)
#         await ctx.send(f"❌ Đã xảy ra lỗi khi thực hiện lệnh")

@client.event
async def on_message(message):
    """Handle message events"""
    # Ignore bot messages
    if message.author.bot:
        return
    
    # Process commands
    await client.process_commands(message)

@client.command(name='ping', description='Kiểm tra độ trễ của bot')
async def ping_command(ctx):
    """Check bot latency"""
    latency = round(client.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Độ trễ: **{latency}ms**",
        color=discord.Color.green() if latency < 100 else discord.Color.yellow()
    )
    await ctx.send(embed=embed)

# @client.command(name='stats', description='Xem thống kê bot')
# @is_bot_owner()
# async def stats_command(ctx):
#     """Show bot statistics"""
#     embed = discord.Embed(
#         title="📊 Thống Kê Bot",
#         color=discord.Color.blue()
#     )
#     embed.add_field(name="Số Server", value=f"{len(client.guilds)}", inline=True)
#     embed.add_field(name="Số Người Dùng", value=f"{sum((g.member_count or 0) for g in client.guilds)}", inline=True)
#     embed.add_field(name="Độ Trễ", value=f"{round(client.latency * 1000)}ms", inline=True)
#     embed.add_field(name="Python Version", value=f"{sys.version.split()[0]}", inline=True)
#     embed.add_field(name="Discord.py Version", value=f"{discord.__version__}", inline=True)
    
#     await ctx.send(embed=embed)

@client.command(name='reload', description='Reload a cog')
@is_bot_owner()
async def reload_command(ctx, extension: str = None):
    """Reload a specific extension or all extensions"""
    if extension:
        try:
            # Try to reload by removing and re-adding cog
            cog = client.get_cog(extension)
            if cog:
                await client.remove_cog(extension)
            
            # Re-import and add cog (you'll need to specify the module path)
            await ctx.send(f"⚠️ Reload individual cogs not fully implemented. Use reload without parameter for all cogs.")
        except Exception as e:
            await ctx.send(f"❌ Failed to reload {extension}: {e}")
    else:
        # Remove all cogs first
        cogs_to_remove = list(client.cogs.keys())
        for cog_name in cogs_to_remove:
            try:
                await client.remove_cog(cog_name)
            except:
                pass
        
        # Reload all extensions
        await load_extensions()
        await ctx.send("✅ Reloaded all extensions")

# Cleanup on shutdown
def cleanup():
    """Cleanup resources on shutdown"""
    logger.info("🔄 Shutting down bot...")
    try:
        db_manager.close_all()
        logger.info("✅ Database connections closed")
    except:
        logger.warning("⚠️ Could not close database connections properly")

# Run the bot
async def main():
    """Main async function to run the bot"""
    try:
        # Check if BOT_TOKEN is set
        if not BOT_TOKEN:
            logger.error("❌ BOT_TOKEN is not set in environment variables.")
            return
        
        # Run bot
        await client.start(BOT_TOKEN)
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Program interrupted by user")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}", exc_info=True)
        cleanup()