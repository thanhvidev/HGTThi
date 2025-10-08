#!/usr/bin/env python3
"""
Gaming/Cypher Achievement Card Generator
Tạo achievement cards với thiết kế gaming đẹp mắt như Discord
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import discord
from typing import Dict, Any, Optional, Tuple, List
import asyncio
import aiohttp
from datetime import datetime
import config

class AchievementCardGenerator:
    def __init__(self):
        self.card_width = 600
        self.card_height = 180
        self.margin = 20
        self.icon_size = (80, 80)
        
        # Gaming/Cypher color scheme
        self.colors = config.GAMING_COLORS
        self.rarity_colors = config.RARITY_COLORS
        
        # Font paths
        self.fonts = {
            'title': self._get_font('title', 22),
            'subtitle': self._get_font('subtitle', 16), 
            'body': self._get_font('body', 14),
            'mono': self._get_font('mono', 12)
        }
    
    def _get_font(self, font_type: str, size: int) -> ImageFont.FreeTypeFont:
        """Get font with fallback"""
        try:
            font_path = config.GAMING_FONTS.get(font_type)
            if font_path:
                return ImageFont.truetype(font_path, size)
        except (OSError, IOError):
            pass
        
        # Fallback fonts
        try:
            if font_type == 'mono':
                return ImageFont.truetype("DejaVuSansMono.ttf", size)
            elif font_type in ['title', 'subtitle']:
                return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
            else:
                return ImageFont.truetype("DejaVuSans.ttf", size)
        except (OSError, IOError):
            return ImageFont.load_default()
    
    async def create_achievement_unlock_card(self, achievement_id: str, user: discord.Member, 
                                           timestamp: Optional[datetime] = None) -> io.BytesIO:
        """Create achievement unlock notification card"""
        achievement = config.ACHIEVEMENTS.get(achievement_id)
        if not achievement:
            raise ValueError(f"Achievement {achievement_id} not found")
        
        # Create base image with dark gaming background
        img = Image.new("RGBA", (self.card_width, self.card_height), (0, 0, 0, 0))
        
        # Create gaming-style background
        bg = self._create_gaming_background(achievement['rarity'])
        img.paste(bg, (0, 0))
        
        # Add border based on rarity
        self._add_rarity_border(img, achievement['rarity'])
        
        # Add achievement icon/image
        await self._add_achievement_icon(img, achievement_id, achievement)
        
        # Add text content
        self._add_achievement_text(img, achievement, user, timestamp)
        
        # Add gaming effects (glow, particles, etc.)
        self._add_gaming_effects(img, achievement['rarity'])
        
        # Convert to bytes
        output = io.BytesIO()
        img.save(output, format="PNG", quality=config.IMAGE_CONFIG['quality'])
        output.seek(0)
        
        return output
    
    def _create_gaming_background(self, rarity: str) -> Image.Image:
        """Create gaming-style background with gradients"""
        bg = Image.new("RGBA", (self.card_width, self.card_height), (0, 0, 0, 0))
        
        # Base dark background
        base_color = self.colors['dark_bg']
        bg_base = Image.new("RGBA", (self.card_width, self.card_height), (*base_color, 200))
        
        # Create gradient overlay based on rarity
        rarity_color = self.rarity_colors.get(rarity, self.rarity_colors['common'])
        gradient = self._create_diagonal_gradient(rarity_color, 0.3, 0.1)
        
        # Composite layers
        bg = Image.alpha_composite(bg_base, gradient)
        
        # Add subtle pattern/texture
        pattern = self._create_cyber_pattern()
        bg = Image.alpha_composite(bg, pattern)
        
        return bg
    
    def _create_diagonal_gradient(self, color: Tuple[int, int, int], 
                                start_alpha: float, end_alpha: float) -> Image.Image:
        """Create diagonal gradient for gaming effect"""
        gradient = Image.new("RGBA", (self.card_width, self.card_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(gradient)
        
        # Create diagonal gradient
        for y in range(self.card_height):
            for x in range(self.card_width):
                # Calculate position along diagonal
                diagonal_pos = (x + y) / (self.card_width + self.card_height)
                alpha = int(255 * (start_alpha + (end_alpha - start_alpha) * diagonal_pos))
                draw.point((x, y), (*color, alpha))
        
        return gradient
    
    def _create_cyber_pattern(self) -> Image.Image:
        """Create subtle cyber/circuit pattern"""
        pattern = Image.new("RGBA", (self.card_width, self.card_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(pattern)
        
        # Add subtle grid lines
        grid_color = (*self.colors['cyber_blue'], 20)
        
        # Vertical lines
        for x in range(0, self.card_width, 40):
            draw.line([(x, 0), (x, self.card_height)], fill=grid_color, width=1)
        
        # Horizontal lines  
        for y in range(0, self.card_height, 30):
            draw.line([(0, y), (self.card_width, y)], fill=grid_color, width=1)
        
        return pattern
    
    def _add_rarity_border(self, img: Image.Image, rarity: str):
        """Add glowing border based on rarity"""
        border_color = self.rarity_colors.get(rarity, self.rarity_colors['common'])
        draw = ImageDraw.Draw(img)
        
        # Multiple border layers for glow effect
        border_width = 3 if rarity in ['legendary', 'mythic'] else 2
        
        for i in range(border_width):
            alpha = 255 - (i * 60)
            if alpha < 0:
                alpha = 0
            
            # Draw border rectangle
            draw.rectangle([
                (i, i), 
                (self.card_width - 1 - i, self.card_height - 1 - i)
            ], outline=(*border_color, alpha), width=1)
    
    async def _add_achievement_icon(self, img: Image.Image, achievement_id: str, achievement: Dict):
        """Add achievement icon with gaming effects"""
        icon_x = self.margin
        icon_y = (self.card_height - self.icon_size[1]) // 2
        
        # Create icon background with glow
        icon_bg = self._create_icon_background(achievement['rarity'])
        img.paste(icon_bg, (icon_x - 10, icon_y - 10), icon_bg)
        
        # Try to load custom achievement image
        try:
            icon_img = await self._load_achievement_image(achievement_id, achievement)
            if icon_img:
                # Resize and make circular
                icon_img = icon_img.resize(self.icon_size, Image.Resampling.LANCZOS)
                icon_img = self._make_circular_image(icon_img)
                img.paste(icon_img, (icon_x, icon_y), icon_img)
            else:
                # Fallback to emoji icon
                self._draw_emoji_icon(img, achievement['icon'], icon_x, icon_y)
        except Exception:
            # Fallback to emoji icon
            self._draw_emoji_icon(img, achievement['icon'], icon_x, icon_y)
    
    def _create_icon_background(self, rarity: str) -> Image.Image:
        """Create glowing background for achievement icon"""
        size = (self.icon_size[0] + 20, self.icon_size[1] + 20)
        bg = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(bg)
        
        rarity_color = self.rarity_colors.get(rarity, self.rarity_colors['common'])
        
        # Create glow effect
        for i in range(10, 0, -1):
            alpha = int(80 * (i / 10))
            draw.ellipse([
                (10 - i, 10 - i),
                (size[0] - 10 + i, size[1] - 10 + i)
            ], fill=(*rarity_color, alpha))
        
        return bg
    
    async def _load_achievement_image(self, achievement_id: str, achievement: Dict) -> Optional[Image.Image]:
        """Load custom achievement image from URL or local file"""
        image_path = achievement.get('image')
        if not image_path:
            return None
        
        try:
            if image_path.startswith(('http://', 'https://')):
                # Load from URL
                async with aiohttp.ClientSession() as session:
                    async with session.get(image_path) as response:
                        if response.status == 200:
                            image_data = await response.read()
                            return Image.open(io.BytesIO(image_data)).convert("RGBA")
            else:
                # Load from local file
                return Image.open(image_path).convert("RGBA")
        except Exception as e:
            print(f"Failed to load achievement image {image_path}: {e}")
            return None
    
    def _make_circular_image(self, img: Image.Image) -> Image.Image:
        """Make image circular with smooth edges"""
        size = img.size
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        
        # Apply mask
        result = Image.new("RGBA", size, (0, 0, 0, 0))
        result.paste(img, (0, 0))
        result.putalpha(mask)
        
        return result
    
    def _draw_emoji_icon(self, img: Image.Image, emoji: str, x: int, y: int):
        """Draw emoji as fallback icon"""
        draw = ImageDraw.Draw(img)
        
        # Create circular background
        bg_color = self.colors['card_bg']
        draw.ellipse([
            (x, y),
            (x + self.icon_size[0], y + self.icon_size[1])
        ], fill=bg_color)
        
        # Draw emoji (simplified - in real implementation you'd use proper emoji font)
        font = ImageFont.truetype("DejaVuSans.ttf", 40)
        text_bbox = draw.textbbox((0, 0), emoji, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        
        text_x = x + (self.icon_size[0] - text_w) // 2
        text_y = y + (self.icon_size[1] - text_h) // 2
        
        draw.text((text_x, text_y), emoji, fill=(255, 255, 255), font=font)
    
    def _add_achievement_text(self, img: Image.Image, achievement: Dict, 
                            user: discord.Member, timestamp: Optional[datetime]):
        """Add achievement text with gaming typography"""
        draw = ImageDraw.Draw(img)
        
        text_x = self.margin + self.icon_size[0] + 20
        text_y = self.margin
        
        # Achievement unlocked header
        header_color = self.colors['hacker_orange']
        draw.text((text_x, text_y), "ACHIEVEMENT UNLOCKED!", 
                 fill=header_color, font=self.fonts['mono'])
        text_y += 25
        
        # Achievement name with rarity color
        name_color = self.rarity_colors.get(achievement['rarity'], (255, 255, 255))
        draw.text((text_x, text_y), achievement['name'], 
                 fill=name_color, font=self.fonts['title'])
        text_y += 30
        
        # Description
        desc_lines = self._wrap_text(achievement['description'], 45)
        for line in desc_lines:
            draw.text((text_x, text_y), line, 
                     fill=(200, 200, 200), font=self.fonts['body'])
            text_y += 18
        
        # Reward XP
        text_y = self.card_height - 50
        xp_color = self.colors['electric_yellow'] 
        draw.text((text_x, text_y), f"+{achievement['reward_xp']:,} XP", 
                 fill=xp_color, font=self.fonts['subtitle'])
        
        # User info
        text_y += 20
        draw.text((text_x, text_y), f"@{user.display_name}", 
                 fill=(150, 150, 150), font=self.fonts['body'])
        
        # Timestamp
        if timestamp:
            time_str = timestamp.strftime("%d/%m/%Y %H:%M")
            time_bbox = draw.textbbox((0, 0), time_str, font=self.fonts['mono'])
            time_w = time_bbox[2] - time_bbox[0]
            draw.text((self.card_width - time_w - self.margin, 
                      self.card_height - 30), time_str, 
                     fill=(100, 100, 100), font=self.fonts['mono'])
    
    def _wrap_text(self, text: str, max_chars: int) -> List[str]:
        """Wrap text to fit within specified character limit"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= max_chars:
                current_line += (" " + word) if current_line else word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _add_gaming_effects(self, img: Image.Image, rarity: str):
        """Add special gaming effects for high rarity achievements"""
        if rarity in ['legendary', 'mythic']:
            # Add particle effects
            self._add_particles(img, rarity)
            
        if rarity == 'mythic':
            # Add extra glow for mythic
            self._add_mythic_glow(img)
    
    def _add_particles(self, img: Image.Image, rarity: str):
        """Add particle effects around the card"""
        draw = ImageDraw.Draw(img)
        particle_color = self.rarity_colors.get(rarity, (255, 255, 255))
        
        # Simple particle effect - dots around the edges
        import random
        random.seed(42)  # Consistent particles
        
        for _ in range(15):
            x = random.randint(10, self.card_width - 10)
            y = random.randint(10, self.card_height - 10) 
            size = random.randint(2, 4)
            alpha = random.randint(100, 200)
            
            draw.ellipse([
                (x - size, y - size),
                (x + size, y + size)
            ], fill=(*particle_color, alpha))
    
    def _add_mythic_glow(self, img: Image.Image):
        """Add special glow effect for mythic achievements"""
        # Create a glow overlay
        glow = Image.new("RGBA", (self.card_width, self.card_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(glow)
        
        # Subtle golden glow around entire card
        glow_color = self.rarity_colors['mythic']
        for i in range(5):
            alpha = int(30 * (1 - i/5))
            draw.rectangle([
                (-i, -i),
                (self.card_width + i, self.card_height + i)
            ], outline=(*glow_color, alpha), width=2)
        
        # Apply glow
        img = Image.alpha_composite(img.convert("RGBA"), glow)
        
    async def create_achievement_showcase(self, user: discord.Member, 
                                        achievements: List[str]) -> io.BytesIO:
        """Create showcase of multiple achievements"""
        showcase_width = 800
        showcase_height = 600
        
        img = Image.new("RGBA", (showcase_width, showcase_height), self.colors['dark_bg'])
        draw = ImageDraw.Draw(img)
        
        # Title
        title = f"🏆 Thành Tựu của {user.display_name}"
        title_font = self.fonts['title'] 
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_w = title_bbox[2] - title_bbox[0]
        draw.text(((showcase_width - title_w) // 2, 30), title, 
                 fill=self.colors['electric_yellow'], font=title_font)
        
        # Grid of achievements
        cols = 3
        rows = 4
        card_w = 240
        card_h = 100
        spacing = 20
        start_x = (showcase_width - (cols * card_w + (cols-1) * spacing)) // 2
        start_y = 100
        
        for i, achievement_id in enumerate(achievements[:12]):  # Max 12 achievements
            if achievement_id not in config.ACHIEVEMENTS:
                continue
                
            achievement = config.ACHIEVEMENTS[achievement_id]
            
            col = i % cols
            row = i // cols
            
            x = start_x + col * (card_w + spacing)
            y = start_y + row * (card_h + spacing)
            
            # Mini achievement card
            self._draw_mini_achievement(img, achievement, x, y, card_w, card_h)
        
        # Stats
        stats_y = start_y + rows * (card_h + spacing) + 20
        total_xp = sum(config.ACHIEVEMENTS[aid]['reward_xp'] for aid in achievements 
                      if aid in config.ACHIEVEMENTS)
        
        stats_text = f"Tổng cộng: {len(achievements)} thành tựu • {total_xp:,} XP"
        draw.text((start_x, stats_y), stats_text, 
                 fill=(200, 200, 200), font=self.fonts['body'])
        
        # Convert to bytes
        output = io.BytesIO()
        img.save(output, format="PNG", quality=config.IMAGE_CONFIG['quality'])
        output.seek(0)
        
        return output
    
    def _draw_mini_achievement(self, img: Image.Image, achievement: Dict, 
                             x: int, y: int, w: int, h: int):
        """Draw mini achievement card in showcase"""
        draw = ImageDraw.Draw(img)
        
        # Background
        bg_color = self.colors['card_bg']
        draw.rectangle([(x, y), (x + w, y + h)], fill=bg_color)
        
        # Border
        border_color = self.rarity_colors.get(achievement['rarity'], (100, 100, 100))
        draw.rectangle([(x, y), (x + w, y + h)], outline=border_color, width=2)
        
        # Icon
        icon_size = 24
        draw.text((x + 10, y + 10), achievement['icon'], 
                 fill=(255, 255, 255), font=self.fonts['body'])
        
        # Name
        name = achievement['name']
        if len(name) > 20:
            name = name[:17] + "..."
        draw.text((x + 45, y + 12), name, 
                 fill=border_color, font=self.fonts['body'])
        
        # XP
        xp_text = f"+{achievement['reward_xp']} XP"
        draw.text((x + 10, y + h - 25), xp_text, 
                 fill=self.colors['electric_yellow'], font=self.fonts['mono'])


# Utility function for easy usage
async def create_achievement_card(achievement_id: str, user: discord.Member, 
                                timestamp: Optional[datetime] = None) -> io.BytesIO:
    """Quick function to create achievement unlock card"""
    generator = AchievementCardGenerator()
    return await generator.create_achievement_unlock_card(achievement_id, user, timestamp)