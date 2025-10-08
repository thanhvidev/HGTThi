#!/usr/bin/env python3
"""
Test file for the leveling system
"""

import asyncio
import sys
sys.path.append('.')

from Leveling.database import LevelingDatabase
import config

async def test_leveling_system():
    """Test the leveling system functionality"""
    print("🔧 Testing Leveling System...")
    
    # Initialize database
    db = LevelingDatabase()
    print("✅ Database initialized")
    
    # Test user stats
    user_id = 123456789
    guild_id = 987654321
    
    print(f"\n📊 Testing user stats for User ID: {user_id}")
    
    # Get initial stats
    stats = db.get_user_stats(user_id, guild_id)
    print(f"Initial stats: {stats}")
    
    # Add some XP
    result = db.add_xp(user_id, guild_id, 150, 'message')
    print(f"Added XP result: {result}")
    
    # Get updated stats
    stats = db.get_user_stats(user_id, guild_id)
    print(f"Updated stats: {stats}")
    
    # Test achievements
    print(f"\n🏆 Testing achievements...")
    from Leveling.utils import check_achievements
    
    new_achievements = check_achievements(stats, config.ACHIEVEMENTS)
    print(f"New achievements to unlock: {new_achievements}")
    
    for achievement_id in new_achievements:
        unlocked = db.unlock_achievement(user_id, guild_id, achievement_id)
        if unlocked:
            achievement = config.ACHIEVEMENTS[achievement_id]
            print(f"✅ Unlocked achievement: {achievement['name']}")
    
    # Test leaderboard
    print(f"\n🏆 Testing leaderboard...")
    leaderboard = db.get_leaderboard(guild_id, limit=5)
    print(f"Leaderboard: {leaderboard}")
    
    # Test guild config
    print(f"\n⚙️ Testing guild config...")
    guild_config = db.get_guild_config(guild_id)
    print(f"Guild config: {guild_config}")
    
    print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_leveling_system())