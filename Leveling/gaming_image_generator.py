#!/usr/bin/env python3
"""
Gaming/Cypher Theme Profile & Achievement Image Generator
Tối ưu hóa cho theme gaming với thiết kế đẹp mắt
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import io
import discord
from typing import Dict, Any, Optional, Tuple, List
import asyncio
import aiohttp
from datetime import datetime
import config
from .achievement_generator import AchievementCardGenerator

class GamingImageGenerator:
    def __init__(self):
        self.width = 900  # Tăng kích thước cho đẹp hơn
        self.height = 500
        self.avatar_size = (140, 140)  # Lớn hơn để nổi bật
        self.margin = 25
        
        # Gaming color scheme
        self.colors = config.GAMING_COLORS
        self.level_colors = config.LEVEL_COLORS
        
        # Load gaming fonts
        self.fonts = self._load_gaming_fonts()
    
    def _load_gaming_fonts(self) -> Dict[str, ImageFont.FreeTypeFont]:
        """Load gaming-themed fonts with fallbacks"""
        fonts = {}
        
        font_configs = [
            ('title', 32, 'bold'),
            ('subtitle', 24, 'medium'),
            ('body', 16, 'regular'),
            ('mono', 14, 'mono'),
            ('large', 42, 'bold'),
            ('small', 12, 'regular')
        ]
        
        for font_type, size, weight in font_configs:
            fonts[font_type] = self._get_font_with_fallback(size, weight)
        
        return fonts
    
    def _get_font_with_fallback(self, size: int, weight: str = 'regular') -> ImageFont.FreeTypeFont:
        """Get font with multiple fallbacks for better compatibility"""
        font_paths = {
            'bold': [
                "fonts/Orbitron-Bold.ttf",  # Gaming font
                "DejaVuSans-Bold.ttf",
                "arial.ttf"
            ],
            'medium': [
                "fonts/Roboto-Medium.ttf",
                "DejaVuSans.ttf",
                "arial.ttf"
            ],
            'regular': [
                "fonts/Roboto-Regular.ttf", 
                "DejaVuSans.ttf",
                "arial.ttf"
            ],
            'mono': [
                "fonts/RobotoMono-Regular.ttf",
                "DejaVuSansMono.ttf",
                "consola.ttf"
            ]
        }
        
        for font_path in font_paths.get(weight, font_paths['regular']):
            try:
                return ImageFont.truetype(font_path, size)
            except (OSError, IOError):
                continue
        
        return ImageFont.load_default()
    
    async def create_gaming_profile_card(self, member: discord.Member, stats: Dict[str, Any], 
                                       rank: int, total_members: int) -> io.BytesIO:
        """Create gaming-themed profile card"""
        # Create base image
        img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        
        # Create cyber background
        background = await self._create_cyber_background(stats['level'])
        img.paste(background, (0, 0))
        
        # Add user avatar with gaming border
        await self._add_gaming_avatar(img, member, stats['level'])
        
        # Add gaming HUD elements
        self._add_gaming_hud(img, member, stats, rank, total_members)
        
        # Add level progress with gaming style
        self._add_gaming_progress_bars(img, stats)
        
        # Add achievements showcase
        self._add_achievements_showcase(img, stats)
        
        # Add gaming effects
        self._add_gaming_effects(img, stats['level'])
        
        # Convert to bytes
        output = io.BytesIO()
        img.save(output, format="PNG", quality=config.IMAGE_CONFIG['quality'])
        output.seek(0)
        
        return output
    
    async def _create_cyber_background(self, level: int) -> Image.Image:
        """Create cyberpunk/gaming background"""
        bg = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        
        # Base dark background
        base_bg = Image.new("RGBA", (self.width, self.height), self.colors['dark_bg'])
        
        # Add gradient based on level tier
        level_tier = self._get_level_tier(level)
        tier_color = self.level_colors[level_tier]
        gradient = self._create_gaming_gradient(tier_color)
        
        # Composite layers
        bg = Image.alpha_composite(base_bg, gradient)
        
        # Add cyber grid pattern
        grid = self._create_cyber_grid()
        bg = Image.alpha_composite(bg, grid)
        
        # Add scanlines effect
        scanlines = self._create_scanlines()
        bg = Image.alpha_composite(bg, scanlines)
        
        return bg
    
    def _get_level_tier(self, level: int) -> str:
        """Determine level tier for color scheme"""
        if level >= 100:
            return "challenger"
        elif level >= 75:
            return "grandmaster" 
        elif level >= 50:
            return "master"
        elif level >= 40:
            return "diamond"
        elif level >= 30:
            return "platinum"
        elif level >= 20:
            return "gold"
        elif level >= 10:
            return "silver"
        else:
            return "bronze"
    
    def _create_gaming_gradient(self, base_color: Tuple[int, int, int]) -> Image.Image:
        """Create diagonal gaming-style gradient"""
        gradient = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(gradient)
        
        # Create diagonal gradient from top-left to bottom-right
        for y in range(self.height):
            for x in range(self.width):
                # Calculate diagonal position
                diagonal_pos = (x + y) / (self.width + self.height)
                
                # Color interpolation
                start_alpha = 0.4
                end_alpha = 0.1
                alpha = int(255 * (start_alpha + (end_alpha - start_alpha) * diagonal_pos))
                
                if alpha > 0:
                    draw.point((x, y), (*base_color, alpha))
        
        return gradient
    
    def _create_cyber_grid(self) -> Image.Image:
        """Create subtle cyber grid overlay"""
        grid = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(grid)
        
        grid_color = (*self.colors['cyber_blue'], 25)
        
        # Vertical lines
        for x in range(0, self.width, 50):
            draw.line([(x, 0), (x, self.height)], fill=grid_color, width=1)
        
        # Horizontal lines
        for y in range(0, self.height, 40):
            draw.line([(0, y), (self.width, y)], fill=grid_color, width=1)
        
        # Diagonal accent lines
        for i in range(0, self.width + self.height, 150):
            draw.line([(i, 0), (i - self.height, self.height)], 
                     fill=(*self.colors['matrix_green'], 15), width=2)
        
        return grid
    
    def _create_scanlines(self) -> Image.Image:
        """Create retro scanlines effect"""
        scanlines = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(scanlines)
        
        # Add horizontal scanlines
        for y in range(0, self.height, 4):
            draw.line([(0, y), (self.width, y)], 
                     fill=(0, 0, 0, 20), width=1)
        
        return scanlines
    
    async def _add_gaming_avatar(self, img: Image.Image, member: discord.Member, level: int):
        """Add avatar with gaming-style border and effects"""
        # Position avatar
        avatar_x = self.margin + 30
        avatar_y = self.margin + 30
        
        # Get avatar image
        avatar = await self._get_user_avatar(member)
        avatar = self._create_gaming_circular_avatar(avatar, self.avatar_size)
        
        # Add glow effect based on level tier
        level_tier = self._get_level_tier(level)
        glow_color = self.level_colors[level_tier]
        self._add_avatar_glow(img, avatar_x, avatar_y, self.avatar_size, glow_color)
        
        # Paste avatar
        img.paste(avatar, (avatar_x, avatar_y), avatar)
        
        # Add animated-style border
        self._add_gaming_avatar_border(img, avatar_x, avatar_y, self.avatar_size, glow_color)
    
    async def _get_user_avatar(self, member: discord.Member) -> Image.Image:
        """Download and process user avatar"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(str(member.display_avatar.url)) as response:
                    if response.status == 200:
                        avatar_data = await response.read()
                        return Image.open(io.BytesIO(avatar_data)).convert("RGBA")
        except Exception:
            pass
        
        # Fallback to default avatar
        return self._create_default_avatar()
    
    def _create_default_avatar(self) -> Image.Image:
        """Create default gaming-style avatar"""
        avatar = Image.new("RGBA", (128, 128), self.colors['card_bg'])
        draw = ImageDraw.Draw(avatar)
        
        # Add gaming icon
        draw.ellipse([(32, 32), (96, 96)], fill=self.colors['cyber_blue'])
        draw.text((52, 52), "👤", fill=(255, 255, 255), font=self.fonts['large'])
        
        return avatar
    
    def _create_gaming_circular_avatar(self, img: Image.Image, size: Tuple[int, int]) -> Image.Image:
        """Create circular avatar with gaming effects"""
        # Resize image
        img = img.resize(size, Image.Resampling.LANCZOS)
        
        # Enhance image for gaming look
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.1)
        
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.05)
        
        # Create circular mask
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        
        # Apply mask
        result = Image.new("RGBA", size, (0, 0, 0, 0))
        result.paste(img, (0, 0))
        result.putalpha(mask)
        
        return result
    
    def _add_avatar_glow(self, img: Image.Image, x: int, y: int, 
                        size: Tuple[int, int], color: Tuple[int, int, int]):
        """Add glow effect around avatar"""
        draw = ImageDraw.Draw(img)
        
        # Multiple glow layers for better effect
        glow_layers = [
            (10, 60),  # Outer glow
            (7, 80),   # Middle glow  
            (4, 100)   # Inner glow
        ]
        
        for glow_size, alpha in glow_layers:
            draw.ellipse([
                x - glow_size, y - glow_size,
                x + size[0] + glow_size, y + size[1] + glow_size
            ], fill=(*color, alpha))
    
    def _add_gaming_avatar_border(self, img: Image.Image, x: int, y: int,
                                 size: Tuple[int, int], color: Tuple[int, int, int]):
        """Add gaming-style animated border around avatar"""
        draw = ImageDraw.Draw(img)
        
        # Main border
        border_width = 3
        draw.ellipse([
            x - border_width, y - border_width,
            x + size[0] + border_width, y + size[1] + border_width
        ], outline=color + (255,), width=border_width)
        
        # Accent corners (gaming UI style)
        corner_size = 15
        corner_color = (*self.colors['electric_yellow'], 200)
        
        # Top-left corner
        draw.line([(x - 10, y - 5), (x - 5, y - 10)], fill=corner_color, width=3)
        draw.line([(x - 10, y - 5), (x - 10 + corner_size, y - 5)], fill=corner_color, width=3)
        draw.line([(x - 5, y - 10), (x - 5, y - 10 + corner_size)], fill=corner_color, width=3)
    
    def _add_gaming_hud(self, img: Image.Image, member: discord.Member, stats: Dict[str, Any],
                       rank: int, total_members: int):
        """Add gaming HUD elements with user info"""
        draw = ImageDraw.Draw(img)
        
        # Starting position (to the right of avatar)
        info_x = self.margin + 30 + self.avatar_size[0] + 40
        info_y = self.margin + 40
        
        # Player name with gaming styling
        username = member.display_name[:18] + ("..." if len(member.display_name) > 18 else "")
        draw.text((info_x, info_y), "PLAYER:", 
                 fill=self.colors['hacker_orange'], font=self.fonts['mono'])
        info_y += 25
        draw.text((info_x, info_y), username, 
                 fill=(255, 255, 255), font=self.fonts['title'])
        info_y += 45
        
        # Level with tier styling
        level_tier = self._get_level_tier(stats['level'])
        tier_color = self.level_colors[level_tier]
        tier_name = level_tier.upper().replace("_", " ")
        
        draw.text((info_x, info_y), f"LV.{stats['level']}", 
                 fill=tier_color, font=self.fonts['large'])
        draw.text((info_x + 120, info_y + 10), tier_name, 
                 fill=tier_color, font=self.fonts['subtitle'])
        info_y += 60
        
        # Rank with medal styling
        rank_color = self.colors['electric_yellow'] if rank <= 10 else (200, 200, 200)
        draw.text((info_x, info_y), f"RANK #{rank:,}", 
                 fill=rank_color, font=self.fonts['subtitle'])
        draw.text((info_x + 150, info_y), f"/ {total_members:,}", 
                 fill=(150, 150, 150), font=self.fonts['body'])
        info_y += 35
        
        # Gaming stats
        stats_data = [
            ("MSG", f"{stats['messages']:,}"),
            ("VOICE", f"{stats['voice_minutes']//60}h {stats['voice_minutes']%60}m"),
            ("XP", f"{stats['total_xp']:,}")
        ]
        
        stat_x = info_x
        for label, value in stats_data:
            draw.text((stat_x, info_y), label, 
                     fill=self.colors['cyber_blue'], font=self.fonts['mono'])
            draw.text((stat_x, info_y + 18), value, 
                     fill=(255, 255, 255), font=self.fonts['body'])
            stat_x += 120
    
    def _add_gaming_progress_bars(self, img: Image.Image, stats: Dict[str, Any]):
        """Add gaming-style progress bars"""
        draw = ImageDraw.Draw(img)
        
        # Progress bar area
        bar_x = self.margin + 50
        bar_y = self.height - 120
        bar_width = self.width - 2 * self.margin - 100
        bar_height = 25
        
        # Calculate XP progress
        current_xp = stats['xp']
        next_level_xp = self._calculate_xp_for_next_level(stats['level'])
        progress = current_xp / next_level_xp if next_level_xp > 0 else 0
        
        # Background bar with gaming style
        bg_color = (*self.colors['dark_bg'], 180)
        draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height],
                             radius=12, fill=bg_color)
        
        # Border
        level_tier = self._get_level_tier(stats['level'])
        border_color = self.level_colors[level_tier]
        draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height],
                             radius=12, outline=border_color, width=2)
        
        # Progress fill with gradient effect
        if progress > 0:
            fill_width = int(bar_width * progress)
            # Create gradient fill
            for i in range(fill_width):
                alpha = 255 - int(50 * (i / fill_width))
                color = (*border_color, alpha)
                draw.line([(bar_x + i, bar_y + 2), (bar_x + i, bar_y + bar_height - 2)], 
                         fill=color, width=1)
        
        # Progress text
        progress_text = f"{current_xp:,} / {next_level_xp:,} XP ({progress*100:.1f}%)"
        text_bbox = draw.textbbox((0, 0), progress_text, font=self.fonts['body'])
        text_w = text_bbox[2] - text_bbox[0]
        text_x = bar_x + (bar_width - text_w) // 2
        draw.text((text_x, bar_y + 5), progress_text, 
                 fill=(255, 255, 255), font=self.fonts['body'])
        
        # Next level indicator
        next_level_text = f"NEXT: LV.{stats['level'] + 1}"
        draw.text((bar_x + bar_width + 10, bar_y + 5), next_level_text,
                 fill=self.colors['electric_yellow'], font=self.fonts['mono'])
    
    def _calculate_xp_for_next_level(self, level: int) -> int:
        """Calculate XP required for next level"""
        if level == 0:
            return 100
        return int(100 * (1.2 ** (level - 1)))
    
    def _add_achievements_showcase(self, img: Image.Image, stats: Dict[str, Any]):
        """Add mini achievements showcase"""
        if not stats.get('achievements'):
            return
        
        draw = ImageDraw.Draw(img)
        
        # Achievements area
        ach_x = self.width - 250
        ach_y = self.margin + 50
        
        # Header
        draw.text((ach_x, ach_y), "ACHIEVEMENTS", 
                 fill=self.colors['hacker_orange'], font=self.fonts['mono'])
        ach_y += 25
        
        # Show last 3 achievements
        recent_achievements = stats['achievements'][-3:]
        for i, achievement_id in enumerate(recent_achievements):
            achievement = config.ACHIEVEMENTS.get(achievement_id)
            if not achievement:
                continue
            
            y_pos = ach_y + i * 35
            
            # Achievement icon
            draw.text((ach_x, y_pos), achievement['icon'], 
                     fill=(255, 255, 255), font=self.fonts['subtitle'])
            
            # Achievement name (truncated)
            name = achievement['name'][:15] + ("..." if len(achievement['name']) > 15 else "")
            rarity_color = config.RARITY_COLORS.get(achievement['rarity'], (200, 200, 200))
            draw.text((ach_x + 30, y_pos), name, 
                     fill=rarity_color, font=self.fonts['small'])
        
        # Total count
        total_text = f"{len(stats['achievements'])}/{len(config.ACHIEVEMENTS)} unlocked"
        draw.text((ach_x, ach_y + 120), total_text, 
                 fill=(150, 150, 150), font=self.fonts['mono'])
    
    def _add_gaming_effects(self, img: Image.Image, level: int):
        """Add special gaming effects for high levels"""
        if level >= 50:
            self._add_particle_effects(img, level)
        
        if level >= 100:
            self._add_legendary_glow(img)
    
    def _add_particle_effects(self, img: Image.Image, level: int):
        """Add particle effects for high level players"""
        draw = ImageDraw.Draw(img)
        
        # Determine particle color based on level
        level_tier = self._get_level_tier(level)
        particle_color = self.level_colors[level_tier]
        
        # Simple particle effect
        import random
        random.seed(level)  # Consistent particles based on level
        
        particle_count = min(20, level // 5)
        for _ in range(particle_count):
            x = random.randint(20, self.width - 20)
            y = random.randint(20, self.height - 20)
            size = random.randint(2, 5)
            alpha = random.randint(100, 200)
            
            draw.ellipse([
                (x - size, y - size), 
                (x + size, y + size)
            ], fill=(*particle_color, alpha))
    
    def _add_legendary_glow(self, img: Image.Image):
        """Add special glow for legendary players (level 100+)"""
        # Create glow overlay
        glow = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(glow)
        
        # Golden glow around entire card
        glow_color = self.colors['electric_yellow']
        for i in range(8):
            alpha = int(40 * (1 - i/8))
            draw.rectangle([
                (-i, -i),
                (self.width + i, self.height + i)
            ], outline=(*glow_color, alpha), width=3)
        
        # Apply glow
        img = Image.alpha_composite(img.convert("RGBA"), glow)
    
    async def create_gaming_rank_card(self, member: discord.Member, stats: Dict[str, Any], 
                                    rank: int) -> io.BytesIO:
        """Create compact gaming rank card"""
        width, height = 650, 220
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        
        # Simple gaming background
        level_tier = self._get_level_tier(stats['level'])
        bg_color = self.level_colors[level_tier]
        
        # Dark base
        base = Image.new("RGBA", (width, height), (*self.colors['dark_bg'], 200))
        
        # Gradient overlay
        gradient = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw_grad = ImageDraw.Draw(gradient)
        for x in range(width):
            alpha = int(100 * (1 - x/width))
            draw_grad.line([(x, 0), (x, height)], fill=(*bg_color, alpha))
        
        img = Image.alpha_composite(base, gradient)
        
        # Add avatar
        avatar = await self._get_user_avatar(member)
        avatar = self._create_gaming_circular_avatar(avatar, (90, 90))
        img.paste(avatar, (25, 65), avatar)
        
        # Add info
        draw = ImageDraw.Draw(img)
        
        # Username
        username = member.display_name[:20] + ("..." if len(member.display_name) > 20 else "")
        draw.text((140, 45), username, fill=(255, 255, 255), font=self.fonts['title'])
        
        # Level and rank
        draw.text((140, 80), f"Level {stats['level']}", fill=bg_color, font=self.fonts['subtitle'])
        draw.text((140, 110), f"Rank #{rank}", fill=self.colors['electric_yellow'], font=self.fonts['body'])
        
        # XP Progress bar
        bar_x, bar_y = 140, 140
        bar_w, bar_h = 400, 20
        
        current_xp = stats['xp']
        next_level_xp = self._calculate_xp_for_next_level(stats['level'])
        progress = current_xp / next_level_xp if next_level_xp > 0 else 0
        
        # Background
        draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + bar_h], 
                             radius=10, fill=(50, 50, 50))
        
        # Progress
        if progress > 0:
            fill_w = int(bar_w * progress)
            draw.rounded_rectangle([bar_x, bar_y, bar_x + fill_w, bar_y + bar_h],
                                 radius=10, fill=bg_color)
        
        # XP text
        xp_text = f"{current_xp:,} / {next_level_xp:,} XP"
        draw.text((bar_x, bar_y + 25), xp_text, fill=(200, 200, 200), font=self.fonts['small'])
        
        # Convert to bytes
        output = io.BytesIO()
        img.save(output, format="PNG", quality=config.IMAGE_CONFIG['quality'])
        output.seek(0)
        
        return output


# Quick utility functions
async def create_gaming_profile(member: discord.Member, stats: Dict[str, Any], 
                              rank: int, total_members: int) -> io.BytesIO:
    """Quick function to create gaming profile card"""
    generator = GamingImageGenerator()
    return await generator.create_gaming_profile_card(member, stats, rank, total_members)

async def create_gaming_rank_card(member: discord.Member, stats: Dict[str, Any], 
                                rank: int) -> io.BytesIO:
    """Quick function to create gaming rank card"""
    generator = GamingImageGenerator()
    return await generator.create_gaming_rank_card(member, stats, rank)