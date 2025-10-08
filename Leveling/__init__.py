"""
Gaming/Cypher Leveling System Module

A comprehensive Discord bot leveling system with gaming/cypher theme:
- XP tracking for messages and voice activity with gaming multipliers
- Level progression with tier system (Bronze to Challenger)
- Achievement system with beautiful gaming badges
- Gaming-themed profile cards with cyber aesthetics
- Leaderboards with competitive styling
- Administrative commands for management
- Beautiful achievement unlock notifications

Author: AI Assistant  
Version: 2.0.0 - Gaming Edition
"""

from .database import LevelingDatabase
from .level import LevelingCommands
from .gaming_commands import GamingLevelingCommands
from .events import LevelingEvents
from .image_generator import ProfileImageGenerator, AchievementImageGenerator
from .gaming_image_generator import GamingImageGenerator
from .achievement_generator import AchievementCardGenerator
from .utils import *

__version__ = "2.0.0"
__author__ = "AI Assistant"
__theme__ = "Gaming/Cypher"

__all__ = [
    'LevelingDatabase',
    'LevelingCommands',
    'GamingLevelingCommands',
    'LevelingEvents', 
    'ProfileImageGenerator',
    'AchievementImageGenerator',
    'GamingImageGenerator',
    'AchievementCardGenerator'
]