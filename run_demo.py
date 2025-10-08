#!/usr/bin/env python3
"""
Demo script to test the leveling system without running the full bot
"""

import asyncio
import sys
sys.path.append('.')

async def demo_leveling():
    """Demo the leveling system functionality"""
    print("🎯 Discord Bot Leveling System Demo")
    print("=" * 50)
    
    # Import after path setup
    from Leveling.database import LevelingDatabase
    from Leveling.utils import check_achievements, format_time, format_number, get_achievement_emoji
    import config
    
    # Initialize database
    print("📊 Initializing database...")
    db = LevelingDatabase()
    
    # Demo users
    users = [
        {"id": 111111111, "name": "Alice"},
        {"id": 222222222, "name": "Bob"},
        {"id": 333333333, "name": "Charlie"}
    ]
    
    guild_id = 999999999
    
    print(f"\n👥 Creating demo data for {len(users)} users...")
    
    # Simulate user activity
    for i, user in enumerate(users):
        user_id = user["id"]
        name = user["name"]
        
        print(f"\n🔧 Simulating activity for {name}...")
        
        # Add varying amounts of XP
        message_xp = 50 + (i * 100)  # Alice: 50, Bob: 150, Charlie: 250
        voice_minutes = 30 + (i * 60)  # Alice: 30, Bob: 90, Charlie: 150
        
        # Add message XP
        for j in range(message_xp // 20):  # Simulate multiple messages
            result = db.add_xp(user_id, guild_id, 20, 'message')
            if result['leveled_up']:
                print(f"  🎉 {name} reached level {result['new_level']}!")
        
        # Add voice XP
        for j in range(voice_minutes):  # Simulate minutes in voice
            db.add_xp(user_id, guild_id, 10, 'voice')
        
        # Check achievements
        stats = db.get_user_stats(user_id, guild_id)
        new_achievements = check_achievements(stats, config.ACHIEVEMENTS)
        
        for achievement_id in new_achievements:
            if db.unlock_achievement(user_id, guild_id, achievement_id):
                achievement = config.ACHIEVEMENTS[achievement_id]
                emoji = get_achievement_emoji(achievement_id)
                print(f"  🏆 {name} unlocked: {emoji} {achievement['name']}")
    
    # Show final stats
    print(f"\n📊 Final Statistics:")
    print("-" * 30)
    
    for user in users:
        user_id = user["id"]
        name = user["name"]
        stats = db.get_user_stats(user_id, guild_id)
        
        print(f"\n👤 {name}:")
        print(f"   Level: {stats['level']}")
        print(f"   XP: {stats['xp']:,} / {db.xp_for_next_level(stats['level']):,}")
        print(f"   Total XP: {format_number(stats['total_xp'])}")
        print(f"   Messages: {stats['messages']}")
        print(f"   Voice Time: {format_time(stats['voice_minutes'])}")
        print(f"   Achievements: {len(stats['achievements'])}")
        
        if stats['achievements']:
            print(f"   🏆 Unlocked: ", end="")
            for achievement_id in stats['achievements']:
                emoji = get_achievement_emoji(achievement_id)
                print(f"{emoji} ", end="")
            print()
    
    # Show leaderboard
    print(f"\n🏆 Leaderboard (Top 3):")
    print("-" * 25)
    
    leaderboard = db.get_leaderboard(guild_id, limit=3)
    medals = ["🥇", "🥈", "🥉"]
    
    for entry in leaderboard:
        user = next((u for u in users if u["id"] == entry["user_id"]), None)
        if user:
            medal = medals[entry["rank"] - 1] if entry["rank"] <= 3 else f"{entry['rank']}."
            print(f"{medal} {user['name']} - Level {entry['level']} ({format_number(entry['total_xp'])} XP)")
    
    # Test config
    print(f"\n⚙️ Guild Configuration:")
    print("-" * 20)
    
    guild_config = db.get_guild_config(guild_id)
    print(f"Level up channel: {guild_config['level_up_channel'] or 'Not set'}")
    print(f"Announcements: {'Enabled' if guild_config['announcement_enabled'] else 'Disabled'}")
    print(f"XP channels: {len(guild_config['xp_channels'])} configured")
    print(f"Disabled channels: {len(guild_config['disabled_channels'])} configured")
    
    print(f"\n✅ Demo completed successfully!")
    print(f"💡 Use 'python3 main.py' to run the full bot with leveling system.")

if __name__ == "__main__":
    asyncio.run(demo_leveling())