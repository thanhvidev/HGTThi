import discord
from PIL import Image, ImageDraw, ImageFont
import io
import requests
from typing import Optional, Tuple, Dict, Any
import os
import config
import random
from datetime import datetime, timedelta

def get_user_multiplier(member: discord.Member) -> float:
    """Calculate XP multiplier based on user roles"""
    multiplier = 1.0
    
    # Check for VIP roles
    vip_role_names = ['vip', 'premium', 'supporter', 'donator']
    for role in member.roles:
        if any(vip_name in role.name.lower() for vip_name in vip_role_names):
            multiplier = max(multiplier, config.LEVELING_CONFIG['vip_multiplier'])
    
    # Check for server boost
    if member.premium_since:
        multiplier = max(multiplier, config.LEVELING_CONFIG['boost_multiplier'])
    
    return multiplier

def calculate_message_xp() -> int:
    """Calculate random XP for a message"""
    min_xp, max_xp = config.LEVELING_CONFIG['exp_per_message_range']
    return random.randint(min_xp, max_xp)

def format_time(minutes: int) -> str:
    """Format minutes into readable time string"""
    if minutes < 60:
        return f"{minutes} phút"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if hours < 24:
        if remaining_minutes > 0:
            return f"{hours}h {remaining_minutes}m"
        return f"{hours} giờ"
    
    days = hours // 24
    remaining_hours = hours % 24
    
    if remaining_hours > 0:
        return f"{days}d {remaining_hours}h"
    return f"{days} ngày"

def get_level_role(guild: discord.Guild, level: int, level_roles: Dict[str, int]) -> Optional[discord.Role]:
    """Get role that should be assigned for the level"""
    highest_role_level = 0
    target_role = None
    
    for role_id_str, required_level in level_roles.items():
        try:
            role_id = int(role_id_str)
            role = guild.get_role(role_id)
            
            if role and level >= required_level and required_level > highest_role_level:
                highest_role_level = required_level
                target_role = role
        except (ValueError, AttributeError):
            continue
    
    return target_role

async def assign_level_roles(member: discord.Member, new_level: int, level_roles: Dict[str, int]):
    """Assign appropriate level roles to user"""
    if not level_roles:
        return
    
    try:
        # Get all level roles in the guild
        level_role_objects = []
        for role_id_str in level_roles.keys():
            try:
                role_id = int(role_id_str)
                role = member.guild.get_role(role_id)
                if role:
                    level_role_objects.append(role)
            except ValueError:
                continue
        
        # Remove all existing level roles
        roles_to_remove = [role for role in member.roles if role in level_role_objects]
        if roles_to_remove:
            await member.remove_roles(*roles_to_remove, reason="Level role update")
        
        # Add appropriate role for current level
        target_role = get_level_role(member.guild, new_level, level_roles)
        if target_role:
            await member.add_roles(target_role, reason=f"Reached level {new_level}")
    
    except discord.Forbidden:
        pass  # Bot doesn't have permission
    except discord.HTTPException:
        pass  # Rate limited or other issue

def check_achievements(stats: Dict[str, Any], achievements_config: Dict[str, Any]) -> list:
    """Check which achievements should be unlocked"""
    unlocked_achievements = []
    current_achievements = stats.get('achievements', [])
    
    for achievement_id, achievement in achievements_config.items():
        if achievement_id not in current_achievements:
            try:
                if achievement['requirement'](stats):
                    unlocked_achievements.append(achievement_id)
            except Exception:
                continue  # Skip if requirement function fails
    
    return unlocked_achievements

def create_progress_bar(current: int, maximum: int, width: int = 20, filled_char: str = "█", empty_char: str = "░") -> str:
    """Create a text progress bar"""
    if maximum <= 0:
        return empty_char * width
    
    filled_length = int(width * current // maximum)
    filled_length = min(filled_length, width)  # Ensure it doesn't exceed width
    
    bar = filled_char * filled_length + empty_char * (width - filled_length)
    return f"[{bar}]"

async def download_image(url: str, max_size: Tuple[int, int] = (512, 512)) -> Optional[Image.Image]:
    """Download and resize image from URL"""
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        image = Image.open(io.BytesIO(response.content))
        image = image.convert("RGBA")
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        return image
    except Exception:
        return None

def get_default_avatar() -> Image.Image:
    """Get default avatar image"""
    try:
        if os.path.exists("default_avatar.png"):
            return Image.open("default_avatar.png").convert("RGBA")
    except Exception:
        pass
    
    # Create a simple default avatar
    img = Image.new("RGBA", (128, 128), (100, 100, 100, 255))
    draw = ImageDraw.Draw(img)
    draw.ellipse([16, 16, 112, 112], fill=(200, 200, 200, 255))
    return img

def create_rounded_rectangle(size: Tuple[int, int], radius: int, color: Tuple[int, int, int, int]) -> Image.Image:
    """Create a rounded rectangle image"""
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    width, height = size
    
    # Draw rounded rectangle
    draw.rounded_rectangle([0, 0, width, height], radius=radius, fill=color)
    
    return img

def get_font(size: int = 20) -> ImageFont.FreeTypeFont:
    """Get font for text rendering"""
    try:
        # Try to load a nice font
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        try:
            return ImageFont.truetype("/System/Library/Fonts/Arial.ttf", size)
        except Exception:
            try:
                return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
            except Exception:
                return ImageFont.load_default()

def create_circular_avatar(avatar_image: Image.Image, size: Tuple[int, int] = (128, 128)) -> Image.Image:
    """Create circular avatar from image"""
    # Resize avatar
    avatar = avatar_image.resize(size, Image.Resampling.LANCZOS)
    
    # Create mask for circular crop
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse([0, 0, size[0], size[1]], fill=255)
    
    # Apply mask
    avatar.putalpha(mask)
    
    return avatar

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple"""
    if hex_color.startswith('#'):
        hex_color = hex_color[1:]
    
    try:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except (ValueError, IndexError):
        return (255, 255, 255)  # Default white

def get_level_color(level: int) -> Tuple[int, int, int]:
    """Get color based on level"""
    if level >= 50:
        return (255, 215, 0)  # Gold
    elif level >= 25:
        return (192, 192, 192)  # Silver
    elif level >= 10:
        return (205, 127, 50)  # Bronze
    elif level >= 5:
        return (50, 205, 50)  # Lime green
    else:
        return (100, 149, 237)  # Cornflower blue

def create_gradient_background(size: Tuple[int, int], start_color: Tuple[int, int, int], end_color: Tuple[int, int, int]) -> Image.Image:
    """Create a gradient background"""
    width, height = size
    img = Image.new("RGB", size)
    
    for y in range(height):
        ratio = y / height
        r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
        g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
        b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
        
        for x in range(width):
            img.putpixel((x, y), (r, g, b))
    
    return img

def format_number(num: int) -> str:
    """Format number with K, M suffixes"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    else:
        return str(num)

def get_achievement_emoji(achievement_id: str) -> str:
    """Get emoji for achievement"""
    emoji_map = {
        'first_message': '💬',
        'chatterbox': '💭', 
        'social_butterfly': '🦋',
        'voice_newcomer': '🎤',
        'voice_enthusiast': '🎧',
        'voice_legend': '👑',
        'level_5': '⭐',
        'level_10': '🌟',
        'level_25': '✨',
        'level_50': '💎',
        'daily_active': '📅'
    }
    
    return emoji_map.get(achievement_id, '🏆')

def is_user_on_cooldown(user_id: int, guild_id: int, last_message_time: Optional[datetime], cooldown_seconds: int = 60) -> bool:
    """Check if user is on XP cooldown"""
    if not last_message_time:
        return False
    
    if isinstance(last_message_time, str):
        try:
            last_message_time = datetime.fromisoformat(last_message_time.replace('Z', '+00:00'))
        except ValueError:
            return False
    
    return (datetime.now() - last_message_time).total_seconds() < cooldown_seconds

def create_level_up_embed(member: discord.Member, old_level: int, new_level: int, xp_gained: int) -> discord.Embed:
    """Create level up announcement embed"""
    embed = discord.Embed(
        title="🎉 Cấp Độ Mới!",
        description=f"{member.mention} đã lên cấp độ **{new_level}**!",
        color=discord.Color.from_rgb(*get_level_color(new_level))
    )
    
    embed.add_field(
        name="Thông Tin",
        value=f"Cấp độ: {old_level} → **{new_level}**\nKinh nghiệm nhận: +{xp_gained} XP",
        inline=False
    )
    
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.timestamp = datetime.now()
    
    return embed

def create_achievement_embed(member: discord.Member, achievement_id: str, achievement: Dict[str, Any]) -> discord.Embed:
    """Create achievement unlock embed"""
    embed = discord.Embed(
        title="🏆 Thành Tựu Mới!",
        description=f"{member.mention} đã mở khóa thành tựu **{achievement['name']}**!",
        color=discord.Color.gold()
    )
    
    embed.add_field(
        name=f"{achievement['icon']} {achievement['name']}",
        value=achievement['description'],
        inline=False
    )
    
    if achievement.get('reward_xp', 0) > 0:
        embed.add_field(
            name="Phần Thưởng",
            value=f"+{achievement['reward_xp']} XP",
            inline=True
        )
    
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.timestamp = datetime.now()
    
    return embed