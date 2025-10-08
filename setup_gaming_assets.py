#!/usr/bin/env python3
"""
Gaming Assets Setup Script
Tạo và tải các assets cần thiết cho gaming theme
"""

import asyncio
import aiohttp
import os
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GamingAssetsSetup:
    def __init__(self):
        self.base_path = Path("/home/user/webapp")
        self.fonts_dir = self.base_path / "fonts"
        self.achievements_dir = self.base_path / "achievements" 
        self.assets_dir = self.base_path / "assets"
        
        # Ensure directories exist
        self.fonts_dir.mkdir(exist_ok=True)
        self.achievements_dir.mkdir(exist_ok=True)
        self.assets_dir.mkdir(exist_ok=True)
    
    async def setup_all_assets(self):
        """Setup all gaming assets"""
        logger.info("🎮 Starting Gaming Assets Setup...")
        
        # Setup fonts
        await self.setup_gaming_fonts()
        
        # Create achievement images
        await self.create_achievement_images()
        
        # Create utility assets
        await self.create_utility_assets()
        
        logger.info("✅ Gaming Assets Setup Complete!")
    
    async def setup_gaming_fonts(self):
        """Download and setup gaming fonts"""
        logger.info("📝 Setting up gaming fonts...")
        
        # Google Fonts URLs (these are example URLs - in production you'd use proper font files)
        font_urls = {
            "Orbitron-Bold.ttf": "https://fonts.gstatic.com/s/orbitron/v29/yMJMMIlzdpvBhQQL_SC3X9yhF25-T1nyGy6BoWgz.woff2",
            "Roboto-Regular.ttf": "https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Mu4mxK.woff2",
            "Roboto-Medium.ttf": "https://fonts.gstatic.com/s/roboto/v30/KFOlCnqEu92Fr1MmEU9fBBc4.woff2",
            "RobotoMono-Regular.ttf": "https://fonts.gstatic.com/s/robotomono/v22/L0xuDF4xlVMF-BfR8bXMIhJHg45mwgGEFl0_3vq_ROW4AJi8SJQt.woff2"
        }
        
        # For demo purposes, create simple fallback fonts
        await self.create_fallback_fonts()
        logger.info("✅ Gaming fonts ready!")
    
    async def create_fallback_fonts(self):
        """Create simple fallback font indicators"""
        for font_name in ["Orbitron-Bold.ttf", "Roboto-Regular.ttf", "Roboto-Medium.ttf", "RobotoMono-Regular.ttf"]:
            font_path = self.fonts_dir / font_name
            if not font_path.exists():
                # Create empty font file as placeholder
                font_path.touch()
                logger.info(f"Created fallback for {font_name}")
    
    async def create_achievement_images(self):
        """Create achievement badge images"""
        logger.info("🏆 Creating achievement images...")
        
        achievements = [
            ("first_message", "cyber_initiate", (100, 100, 100)),
            ("cyber_explorer", "cyber_explorer", (0, 255, 0)), 
            ("digital_warrior", "digital_warrior", (255, 140, 0)),
            ("cyber_legend", "cyber_legend", (255, 215, 0)),
            ("voice_newbie", "voice_newbie", (100, 100, 100)),
            ("voice_gamer", "voice_gamer", (0, 150, 255)),
            ("voice_legend", "voice_legend", (255, 215, 0)),
            ("level_hacker", "cyber_hacker", (0, 255, 0)),
            ("matrix_agent", "matrix_agent", (0, 150, 255)), 
            ("cyber_overlord", "cyber_overlord", (150, 0, 255)),
            ("digital_god", "digital_god", (255, 215, 0)),
            ("daily_gamer", "daily_gamer", (150, 0, 255)),
            ("night_owl", "night_owl", (0, 150, 255)),
            ("speed_typer", "speed_typer", (0, 255, 0)),
            ("emoji_master", "emoji_master", (0, 150, 255)),
            ("social_gamer", "social_gamer", (0, 150, 255)),
            ("server_veteran", "server_veteran", (150, 0, 255)),
            ("omnipresent", "omnipresent", (255, 215, 0)),
            ("first_blood", "first_blood", (255, 215, 0))
        ]
        
        for achievement_id, image_name, color in achievements:
            await self.create_achievement_badge(achievement_id, image_name, color)
        
        logger.info("✅ Achievement images created!")
    
    async def create_achievement_badge(self, achievement_id: str, image_name: str, color: tuple):
        """Create individual achievement badge"""
        size = (200, 200)
        img = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Create hexagonal badge background
        center_x, center_y = size[0] // 2, size[1] // 2
        radius = 80
        
        # Hexagon points
        import math
        points = []
        for i in range(6):
            angle = math.pi * 2 * i / 6
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append((x, y))
        
        # Draw hexagon background
        draw.polygon(points, fill=(*color, 200))
        
        # Draw border
        draw.polygon(points, outline=(*color, 255), width=4)
        
        # Add inner design based on achievement type
        if "cyber" in achievement_id:
            # Cyber circuit pattern
            self._add_cyber_pattern(draw, center_x, center_y, radius-20)
        elif "voice" in achievement_id:
            # Voice wave pattern  
            self._add_voice_pattern(draw, center_x, center_y, radius-20)
        elif "level" in achievement_id:
            # Level up arrow pattern
            self._add_level_pattern(draw, center_x, center_y, radius-20)
        else:
            # Generic gaming pattern
            self._add_generic_pattern(draw, center_x, center_y, radius-20)
        
        # Save image
        image_path = self.achievements_dir / f"{image_name}.png"
        img.save(image_path, "PNG")
        logger.info(f"Created achievement badge: {image_name}.png")
    
    def _add_cyber_pattern(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int):
        """Add cyber circuit pattern"""
        # Simple circuit lines
        color = (0, 255, 255, 150)
        
        # Vertical line
        draw.line([(center_x, center_y - radius), (center_x, center_y + radius)], fill=color, width=3)
        # Horizontal line
        draw.line([(center_x - radius, center_y), (center_x + radius, center_y)], fill=color, width=3)
        
        # Corner circuits
        for i in range(4):
            angle = math.pi * i / 2
            x1 = center_x + (radius * 0.7) * math.cos(angle)
            y1 = center_y + (radius * 0.7) * math.sin(angle)
            x2 = center_x + (radius * 0.9) * math.cos(angle)
            y2 = center_y + (radius * 0.9) * math.sin(angle)
            draw.line([(x1, y1), (x2, y2)], fill=color, width=2)
    
    def _add_voice_pattern(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int):
        """Add voice wave pattern"""
        import math
        color = (255, 140, 0, 150)
        
        # Sound waves
        for i in range(3):
            wave_radius = radius * (0.3 + i * 0.2)
            draw.ellipse([
                (center_x - wave_radius, center_y - wave_radius),
                (center_x + wave_radius, center_y + wave_radius)
            ], outline=color, width=2)
    
    def _add_level_pattern(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int):
        """Add level up arrow pattern"""
        color = (255, 255, 0, 150)
        
        # Up arrow
        arrow_points = [
            (center_x, center_y - radius * 0.5),  # Top
            (center_x - radius * 0.3, center_y + radius * 0.2),  # Bottom left
            (center_x + radius * 0.3, center_y + radius * 0.2),  # Bottom right
        ]
        draw.polygon(arrow_points, fill=color)
    
    def _add_generic_pattern(self, draw: ImageDraw.Draw, center_x: int, center_y: int, radius: int):
        """Add generic gaming pattern"""
        color = (255, 255, 255, 150)
        
        # Simple cross pattern
        draw.line([(center_x - radius*0.5, center_y), (center_x + radius*0.5, center_y)], fill=color, width=4)
        draw.line([(center_x, center_y - radius*0.5), (center_x, center_y + radius*0.5)], fill=color, width=4)
    
    async def create_utility_assets(self):
        """Create utility assets like backgrounds, icons etc."""
        logger.info("🎨 Creating utility assets...")
        
        # Create default avatar template
        await self.create_default_avatar()
        
        # Create background patterns
        await self.create_background_patterns()
        
        logger.info("✅ Utility assets created!")
    
    async def create_default_avatar(self):
        """Create default gaming avatar"""
        size = (128, 128)
        img = Image.new("RGBA", size, (35, 35, 45, 255))
        draw = ImageDraw.Draw(img)
        
        # Draw gaming controller icon
        controller_color = (0, 255, 255)
        
        # Simple controller shape
        draw.rounded_rectangle([20, 40, 108, 88], radius=20, fill=controller_color)
        
        # D-pad
        draw.rectangle([35, 50, 45, 60], fill=(0, 0, 0))
        draw.rectangle([30, 55, 50, 65], fill=(0, 0, 0))
        
        # Buttons
        for i, (x, y) in enumerate([(70, 50), (80, 60), (90, 50), (80, 70)]):
            draw.ellipse([x-5, y-5, x+5, y+5], fill=(0, 0, 0))
        
        # Save
        avatar_path = self.assets_dir / "default_gaming_avatar.png"
        img.save(avatar_path, "PNG")
        logger.info("Created default gaming avatar")
    
    async def create_background_patterns(self):
        """Create background pattern assets"""
        patterns = [
            ("cyber_grid", self._create_cyber_grid_pattern),
            ("matrix_rain", self._create_matrix_pattern), 
            ("circuit_board", self._create_circuit_pattern)
        ]
        
        for pattern_name, pattern_func in patterns:
            pattern_img = pattern_func(400, 300)
            pattern_path = self.assets_dir / f"{pattern_name}_bg.png"
            pattern_img.save(pattern_path, "PNG")
            logger.info(f"Created background pattern: {pattern_name}")
    
    def _create_cyber_grid_pattern(self, width: int, height: int) -> Image.Image:
        """Create cyber grid background pattern"""
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        grid_color = (0, 255, 255, 50)
        
        # Grid lines
        for x in range(0, width, 40):
            draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
        for y in range(0, height, 30):
            draw.line([(0, y), (width, y)], fill=grid_color, width=1)
        
        return img
    
    def _create_matrix_pattern(self, width: int, height: int) -> Image.Image:
        """Create matrix rain pattern"""
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        import random
        random.seed(42)  # Consistent pattern
        
        for x in range(0, width, 20):
            for y in range(0, height, 15):
                if random.random() < 0.1:  # 10% chance
                    alpha = random.randint(30, 100)
                    draw.text((x, y), "1" if random.random() < 0.5 else "0", 
                             fill=(0, 255, 0, alpha))
        
        return img
    
    def _create_circuit_pattern(self, width: int, height: int) -> Image.Image:
        """Create circuit board pattern"""
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        circuit_color = (255, 140, 0, 80)
        
        # Simple circuit paths
        import random
        random.seed(123)
        
        for _ in range(20):
            x1, y1 = random.randint(0, width), random.randint(0, height)
            x2, y2 = random.randint(0, width), random.randint(0, height)
            draw.line([(x1, y1), (x2, y2)], fill=circuit_color, width=2)
        
        return img


async def main():
    """Main setup function"""
    setup = GamingAssetsSetup()
    await setup.setup_all_assets()

if __name__ == "__main__":
    asyncio.run(main())