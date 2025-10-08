from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import discord
from typing import Dict, Any, Optional, Tuple
from .utils import (
    download_image, get_default_avatar, create_circular_avatar,
    get_font, hex_to_rgb, get_level_color, create_gradient_background,
    format_number, format_time, create_progress_bar, get_achievement_emoji
)
import config

class ProfileImageGenerator:
    def __init__(self):
        self.width = 800
        self.height = 400
        self.avatar_size = (120, 120)
        self.margin = 20
    
    async def create_profile_card(self, member: discord.Member, stats: Dict[str, Any], 
                                rank: int, total_members: int) -> io.BytesIO:
        """Create profile card image"""
        # Create base image
        img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        
        # Create background
        bg_color = self.get_background_color(stats)
        background = self.create_background(bg_color, stats.get('custom_bg'))
        img.paste(background, (0, 0))
        
        # Get avatar
        avatar = await self.get_user_avatar(member)
        avatar = create_circular_avatar(avatar, self.avatar_size)
        
        # Position avatar
        avatar_x = self.margin + 20
        avatar_y = self.margin + 20
        img.paste(avatar, (avatar_x, avatar_y), avatar)
        
        # Add border around avatar
        self.add_avatar_border(img, avatar_x, avatar_y, self.avatar_size, get_level_color(stats['level']))
        
        # Add user info text
        self.add_user_info(img, member, stats, rank, total_members, avatar_x + self.avatar_size[0] + 30)
        
        # Add progress bars
        self.add_progress_section(img, stats)
        
        # Add achievement section
        self.add_achievement_section(img, stats)
        
        # Convert to bytes
        output = io.BytesIO()
        img.save(output, format="PNG", quality=95)
        output.seek(0)
        
        return output
    
    async def create_rank_card(self, member: discord.Member, stats: Dict[str, Any], 
                             rank: int) -> io.BytesIO:
        """Create compact rank card image"""
        width, height = 600, 200
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        
        # Create simple background
        bg_color = get_level_color(stats['level'])
        background = create_gradient_background(
            (width, height),
            (bg_color[0] // 3, bg_color[1] // 3, bg_color[2] // 3),
            (bg_color[0] // 2, bg_color[1] // 2, bg_color[2] // 2)
        )
        img.paste(background, (0, 0))
        
        # Add semi-transparent overlay
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 100))
        img = Image.alpha_composite(img.convert("RGBA"), overlay)
        
        # Get and add avatar
        avatar = await self.get_user_avatar(member)
        avatar = create_circular_avatar(avatar, (80, 80))
        img.paste(avatar, (20, 60), avatar)
        
        # Add user info
        draw = ImageDraw.Draw(img)
        
        # Username
        name_font = get_font(28)
        username = member.display_name[:20] + ("..." if len(member.display_name) > 20 else "")
        draw.text((120, 40), username, fill=(255, 255, 255), font=name_font)
        
        # Level and XP
        level_font = get_font(22)
        xp_needed = self.calculate_xp_for_next_level(stats['level'])
        draw.text((120, 75), f"Cấp độ {stats['level']}", fill=bg_color, font=level_font)
        draw.text((120, 105), f"XP: {stats['xp']:,} / {xp_needed:,}", fill=(200, 200, 200), font=get_font(16))
        
        # Progress bar
        bar_x, bar_y = 120, 130
        bar_width, bar_height = 400, 20
        
        # Background bar
        draw.rounded_rectangle(
            [bar_x, bar_y, bar_x + bar_width, bar_y + bar_height],
            radius=10, fill=(50, 50, 50)
        )
        
        # Progress bar
        progress = stats['xp'] / xp_needed if xp_needed > 0 else 0
        progress_width = int(bar_width * progress)
        if progress_width > 0:
            draw.rounded_rectangle(
                [bar_x, bar_y, bar_x + progress_width, bar_y + bar_height],
                radius=10, fill=bg_color
            )
        
        # Rank
        rank_font = get_font(24)
        rank_text = f"Hạng #{rank}"
        draw.text((width - 150, 40), rank_text, fill=(255, 215, 0), font=rank_font)
        
        # Convert to bytes
        output = io.BytesIO()
        img.save(output, format="PNG", quality=95)
        output.seek(0)
        
        return output
    
    def create_background(self, color: Tuple[int, int, int], custom_bg: Optional[str] = None) -> Image.Image:
        """Create background for profile card"""
        if custom_bg:
            # Try to load custom background
            try:
                if custom_bg.startswith('http'):
                    bg_img = download_image(custom_bg, (self.width, self.height))
                    if bg_img:
                        # Resize and apply blur
                        bg_img = bg_img.resize((self.width, self.height), Image.Resampling.LANCZOS)
                        bg_img = bg_img.filter(ImageFilter.GaussianBlur(radius=2))
                        
                        # Add dark overlay
                        overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 120))
                        bg_img = Image.alpha_composite(bg_img.convert("RGBA"), overlay)
                        return bg_img
            except Exception:
                pass
        
        # Create gradient background
        start_color = (color[0] // 4, color[1] // 4, color[2] // 4)
        end_color = (color[0] // 2, color[1] // 2, color[2] // 2)
        
        return create_gradient_background((self.width, self.height), start_color, end_color)
    
    def get_background_color(self, stats: Dict[str, Any]) -> Tuple[int, int, int]:
        """Get background color based on user settings or level"""
        if stats.get('custom_color'):
            return hex_to_rgb(stats['custom_color'])
        
        return get_level_color(stats['level'])
    
    async def get_user_avatar(self, member: discord.Member) -> Image.Image:
        """Get user avatar image"""
        avatar = await download_image(str(member.display_avatar.url))
        if avatar:
            return avatar
        return get_default_avatar()
    
    def add_avatar_border(self, img: Image.Image, x: int, y: int, size: Tuple[int, int], color: Tuple[int, int, int]):
        """Add border around avatar"""
        draw = ImageDraw.Draw(img)
        border_width = 4
        
        # Draw border
        draw.ellipse([
            x - border_width, y - border_width,
            x + size[0] + border_width, y + size[1] + border_width
        ], outline=color + (255,), width=border_width)
    
    def add_user_info(self, img: Image.Image, member: discord.Member, stats: Dict[str, Any], 
                     rank: int, total_members: int, start_x: int):
        """Add user information text"""
        draw = ImageDraw.Draw(img)
        y_offset = 40
        
        # Username
        name_font = get_font(36)
        username = member.display_name[:15] + ("..." if len(member.display_name) > 15 else "")
        draw.text((start_x, y_offset), username, fill=(255, 255, 255), font=name_font)
        y_offset += 50
        
        # Level
        level_font = get_font(28)
        level_color = get_level_color(stats['level'])
        draw.text((start_x, y_offset), f"Cấp độ {stats['level']}", fill=level_color, font=level_font)
        
        # Rank
        rank_text = f"Hạng #{rank}/{total_members}"
        draw.text((start_x + 200, y_offset), rank_text, fill=(255, 215, 0), font=get_font(20))
        y_offset += 40
        
        # Stats
        stats_font = get_font(16)
        stats_color = (200, 200, 200)
        
        # Messages and Voice time on same line
        messages_text = f"📝 {format_number(stats['messages'])} tin nhắn"
        voice_text = f"🎤 {format_time(stats['voice_minutes'])}"
        
        draw.text((start_x, y_offset), messages_text, fill=stats_color, font=stats_font)
        draw.text((start_x + 200, y_offset), voice_text, fill=stats_color, font=stats_font)
        y_offset += 25
        
        # Total XP and achievements
        total_xp_text = f"💎 {format_number(stats['total_xp'])} tổng XP"
        achievements_text = f"🏆 {len(stats['achievements'])} thành tựu"
        
        draw.text((start_x, y_offset), total_xp_text, fill=stats_color, font=stats_font)
        draw.text((start_x + 200, y_offset), achievements_text, fill=stats_color, font=stats_font)
    
    def add_progress_section(self, img: Image.Image, stats: Dict[str, Any]):
        """Add XP progress bar section"""
        draw = ImageDraw.Draw(img)
        
        # Calculate XP for next level
        xp_needed = self.calculate_xp_for_next_level(stats['level'])
        
        # Progress bar position
        bar_x = self.margin + 180
        bar_y = self.height - 80
        bar_width = self.width - bar_x - self.margin - 150
        bar_height = 25
        
        # XP text
        xp_font = get_font(16)
        xp_text = f"XP: {stats['xp']:,} / {xp_needed:,}"
        draw.text((bar_x, bar_y - 25), xp_text, fill=(255, 255, 255), font=xp_font)
        
        # Progress bar background
        draw.rounded_rectangle(
            [bar_x, bar_y, bar_x + bar_width, bar_y + bar_height],
            radius=12, fill=(50, 50, 50)
        )
        
        # Progress bar fill
        progress = stats['xp'] / xp_needed if xp_needed > 0 else 0
        progress_width = int(bar_width * progress)
        
        if progress_width > 0:
            color = get_level_color(stats['level'])
            draw.rounded_rectangle(
                [bar_x, bar_y, bar_x + progress_width, bar_y + bar_height],
                radius=12, fill=color
            )
        
        # Percentage text
        percentage_text = f"{int(progress * 100)}%"
        draw.text((bar_x + bar_width + 10, bar_y + 3), percentage_text, fill=(255, 255, 255), font=get_font(14))
    
    def add_achievement_section(self, img: Image.Image, stats: Dict[str, Any]):
        """Add achievement badges"""
        if not stats['achievements']:
            return
        
        draw = ImageDraw.Draw(img)
        
        # Title
        achievement_font = get_font(18)
        draw.text((self.margin + 20, self.height - 140), "Thành Tựu Gần Đây:", fill=(255, 255, 255), font=achievement_font)
        
        # Show latest achievements (max 5)
        recent_achievements = stats['achievements'][-5:]
        x_offset = self.margin + 20
        y_offset = self.height - 115
        
        for i, achievement_id in enumerate(recent_achievements):
            if i >= 5:  # Max 5 achievements
                break
            
            # Get achievement info
            achievement = config.ACHIEVEMENTS.get(achievement_id, {})
            if not achievement:
                continue
            
            # Achievement badge background
            badge_size = 35
            badge_x = x_offset + (i * 45)
            badge_y = y_offset
            
            # Draw badge circle
            draw.ellipse([
                badge_x, badge_y, badge_x + badge_size, badge_y + badge_size
            ], fill=(255, 215, 0), outline=(255, 255, 255), width=2)
            
            # Draw achievement emoji/icon
            emoji = get_achievement_emoji(achievement_id)
            badge_font = get_font(20)
            
            # Center the emoji in the badge
            bbox = draw.textbbox((0, 0), emoji, font=badge_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            text_x = badge_x + (badge_size - text_width) // 2
            text_y = badge_y + (badge_size - text_height) // 2
            
            draw.text((text_x, text_y), emoji, font=badge_font)
        
        # "..." if more achievements
        if len(stats['achievements']) > 5:
            more_x = x_offset + (5 * 45)
            draw.text((more_x, y_offset + 10), "...", fill=(200, 200, 200), font=get_font(16))
    
    @staticmethod
    def calculate_xp_for_next_level(current_level: int) -> int:
        """Calculate XP needed for next level"""
        return int(100 * (1.2 ** (current_level - 1)))

class AchievementImageGenerator:
    @staticmethod
    async def create_achievement_showcase(member: discord.Member, achievements: list, 
                                        achievement_data: Dict[str, Any]) -> io.BytesIO:
        """Create achievement showcase image"""
        width, height = 800, 600
        img = Image.new("RGBA", (width, height), (30, 30, 40, 255))
        draw = ImageDraw.Draw(img)
        
        # Title
        title_font = get_font(32)
        title = f"Thành Tựu của {member.display_name}"
        draw.text((50, 30), title, fill=(255, 255, 255), font=title_font)
        
        # Achievement grid
        cols = 4
        rows = (len(achievements) + cols - 1) // cols
        
        badge_size = 80
        spacing = 20
        start_x = (width - (cols * badge_size + (cols - 1) * spacing)) // 2
        start_y = 100
        
        for i, achievement_id in enumerate(achievements):
            achievement = achievement_data.get(achievement_id, {})
            if not achievement:
                continue
            
            row = i // cols
            col = i % cols
            
            x = start_x + col * (badge_size + spacing)
            y = start_y + row * (badge_size + spacing + 30)
            
            # Achievement badge
            draw.ellipse([x, y, x + badge_size, y + badge_size], 
                        fill=(255, 215, 0), outline=(255, 255, 255), width=3)
            
            # Achievement icon
            emoji = get_achievement_emoji(achievement_id)
            emoji_font = get_font(40)
            
            bbox = draw.textbbox((0, 0), emoji, font=emoji_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            text_x = x + (badge_size - text_width) // 2
            text_y = y + (badge_size - text_height) // 2
            
            draw.text((text_x, text_y), emoji, font=emoji_font)
            
            # Achievement name
            name_font = get_font(12)
            name = achievement.get('name', 'Unknown')
            name_bbox = draw.textbbox((0, 0), name, font=name_font)
            name_width = name_bbox[2] - name_bbox[0]
            
            name_x = x + (badge_size - name_width) // 2
            name_y = y + badge_size + 5
            
            draw.text((name_x, name_y), name, fill=(200, 200, 200), font=name_font)
        
        # Convert to bytes
        output = io.BytesIO()
        img.save(output, format="PNG", quality=95)
        output.seek(0)
        
        return output