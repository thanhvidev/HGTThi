"""
Leveling System Module

A comprehensive Discord bot leveling system with:
- XP tracking for messages and voice activity
- Level progression and ranking
- Achievement system
- Profile cards with customizable backgrounds
- Leaderboards and statistics
- Administrative commands for management

Author: AI Assistant
Version: 1.0.0
"""

from .database import LevelingDatabase
from .commands import LevelingCommands
from .events import LevelingEvents
from .image_generator import ProfileImageGenerator, AchievementImageGenerator
from .utils import *

__version__ = "1.0.0"
__author__ = "AI Assistant"

__all__ = [
    'LevelingDatabase',
    'LevelingCommands', 
    'LevelingEvents',
    'ProfileImageGenerator',
    'AchievementImageGenerator'
]