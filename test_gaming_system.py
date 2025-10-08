#!/usr/bin/env python3
"""
Gaming Leveling System Test Script
Test các tính năng gaming/cypher theme mới
"""

import asyncio
import sys
sys.path.append('.')

from Leveling.database import LevelingDatabase
from Leveling.gaming_image_generator import GamingImageGenerator
from Leveling.achievement_generator import AchievementCardGenerator
from Leveling.utils import check_achievements, format_time, format_number, get_achievement_emoji
import config
from datetime import datetime

class MockMember:
    """Mock Discord Member for testing"""
    def __init__(self, user_id: int, name: str, avatar_url: str = None):
        self.id = user_id
        self.display_name = name
        self.name = name
        self.display_avatar = MockAvatar(avatar_url or "https://cdn.discordapp.com/embed/avatars/0.png")
        self.bot = False

class MockAvatar:
    """Mock Discord Avatar for testing"""
    def __init__(self, url: str):
        self.url = url

async def test_gaming_system():
    """Test gaming leveling system"""
    print("🎮 Testing Gaming Leveling System")
    print("=" * 60)
    
    # Initialize components
    db = LevelingDatabase()
    gaming_generator = GamingImageGenerator()
    achievement_generator = AchievementCardGenerator()
    
    # Mock test users
    test_users = [
        MockMember(111111111, "CyberWarrior", "https://cdn.discordapp.com/embed/avatars/1.png"),
        MockMember(222222222, "MatrixHacker", "https://cdn.discordapp.com/embed/avatars/2.png"),
        MockMember(333333333, "DigitalNinja", "https://cdn.discordapp.com/embed/avatars/3.png")
    ]
    
    guild_id = 999999999
    
    print("🔧 Setting up test data...")
    
    # Create test data for each user
    for i, user in enumerate(test_users):
        print(f"\n👤 Setting up {user.display_name}...")
        
        # Different progression levels
        if i == 0:  # CyberWarrior - High level
            await simulate_user_activity(db, user.id, guild_id, {
                'messages': 1500,
                'voice_minutes': 2400,  # 40 hours
                'target_level': 35
            })
        elif i == 1:  # MatrixHacker - Medium level  
            await simulate_user_activity(db, user.id, guild_id, {
                'messages': 800,
                'voice_minutes': 900,  # 15 hours
                'target_level': 20
            })
        else:  # DigitalNinja - Lower level
            await simulate_user_activity(db, user.id, guild_id, {
                'messages': 200,
                'voice_minutes': 300,  # 5 hours
                'target_level': 8
            })
    
    print("\n🏆 Testing Achievement System...")
    
    # Test achievement unlocking
    for user in test_users:
        stats = db.get_user_stats(user.id, guild_id)
        new_achievements = check_achievements(stats, config.ACHIEVEMENTS)
        
        for achievement_id in new_achievements:
            if db.unlock_achievement(user.id, guild_id, achievement_id):
                achievement = config.ACHIEVEMENTS[achievement_id]
                print(f"  🎉 {user.display_name} unlocked: {achievement['name']}")
    
    print("\n🎨 Testing Gaming Image Generation...")
    
    # Test gaming profile cards
    for user in test_users:
        try:
            stats = db.get_user_stats(user.id, guild_id)
            rank = await get_user_rank(db, user.id, guild_id)
            
            print(f"  🖼️ Generating gaming profile for {user.display_name}...")
            profile_img = await gaming_generator.create_gaming_profile_card(
                user, stats, rank, len(test_users)
            )
            
            # Save to file for inspection
            output_path = f"/home/user/webapp/test_gaming_profile_{user.display_name}.png"
            with open(output_path, 'wb') as f:
                f.write(profile_img.getvalue())
            print(f"    ✅ Saved to: {output_path}")
            
        except Exception as e:
            print(f"    ❌ Error generating profile for {user.display_name}: {e}")
    
    # Test achievement cards
    print("\n🏅 Testing Achievement Cards...")
    
    test_achievements = ["cyber_explorer", "voice_gamer", "level_hacker", "digital_god"]
    
    for ach_id in test_achievements:
        if ach_id in config.ACHIEVEMENTS:
            try:
                print(f"  🎨 Generating achievement card: {ach_id}")
                ach_card = await achievement_generator.create_achievement_unlock_card(
                    ach_id, test_users[0], datetime.now()
                )
                
                # Save to file
                output_path = f"/home/user/webapp/test_achievement_{ach_id}.png"
                with open(output_path, 'wb') as f:
                    f.write(ach_card.getvalue())
                print(f"    ✅ Saved to: {output_path}")
                
            except Exception as e:
                print(f"    ❌ Error generating {ach_id}: {e}")
    
    # Test rank cards
    print("\n🏆 Testing Gaming Rank Cards...")
    
    for user in test_users:
        try:
            stats = db.get_user_stats(user.id, guild_id)
            rank = await get_user_rank(db, user.id, guild_id)
            
            print(f"  🎯 Generating rank card for {user.display_name}...")
            rank_img = await gaming_generator.create_gaming_rank_card(user, stats, rank)
            
            # Save to file
            output_path = f"/home/user/webapp/test_gaming_rank_{user.display_name}.png"
            with open(output_path, 'wb') as f:
                f.write(rank_img.getvalue())
            print(f"    ✅ Saved to: {output_path}")
            
        except Exception as e:
            print(f"    ❌ Error generating rank card for {user.display_name}: {e}")
    
    # Display final statistics
    print("\n📊 Final Gaming Statistics:")
    print("-" * 40)
    
    leaderboard = db.get_leaderboard(guild_id, limit=10)
    
    for entry in leaderboard:
        user = next((u for u in test_users if u.id == entry["user_id"]), None)
        if user:
            stats = db.get_user_stats(user.id, guild_id)
            tier_name = get_level_tier_name(stats['level'])
            
            print(f"\n🎮 {user.display_name} ({tier_name}):")
            print(f"   Level: {stats['level']} (Rank #{entry['rank']})")
            print(f"   XP: {stats['xp']:,} / {calculate_xp_for_next_level(stats['level']):,}")
            print(f"   Total XP: {format_number(stats['total_xp'])}")
            print(f"   Messages: {format_number(stats['messages'])}")
            print(f"   Voice Time: {format_time(stats['voice_minutes'])}")
            print(f"   Achievements: {len(stats.get('achievements', []))}/{len(config.ACHIEVEMENTS)}")
            
            if stats.get('achievements'):
                recent_achievements = stats['achievements'][-3:]
                achievement_names = []
                for ach_id in recent_achievements:
                    achievement = config.ACHIEVEMENTS.get(ach_id, {})
                    if achievement:
                        achievement_names.append(achievement['name'])
                
                if achievement_names:
                    print(f"   Recent: {', '.join(achievement_names)}")
    
    print(f"\n✅ Gaming System Test Complete!")
    print(f"💡 Check the generated PNG files to see the gaming theme in action!")

async def simulate_user_activity(db: LevelingDatabase, user_id: int, guild_id: int, config_data: dict):
    """Simulate user activity to reach target level"""
    target_messages = config_data['messages']
    target_voice_minutes = config_data['voice_minutes'] 
    target_level = config_data['target_level']
    
    # Add messages
    for i in range(target_messages):
        xp_gain = 15  # Base XP per message
        result = db.add_xp(user_id, guild_id, xp_gain, 'message')
        if result['leveled_up'] and result['new_level'] >= target_level:
            break
    
    # Add voice time
    for i in range(target_voice_minutes):
        xp_gain = 10  # Base XP per minute
        db.add_xp(user_id, guild_id, xp_gain, 'voice')
    
    print(f"    Simulated {target_messages} messages and {target_voice_minutes} voice minutes")

async def get_user_rank(db: LevelingDatabase, user_id: int, guild_id: int) -> int:
    """Get user's rank in guild"""
    leaderboard = db.get_leaderboard(guild_id, limit=1000)
    for entry in leaderboard:
        if entry['user_id'] == user_id:
            return entry['rank']
    return len(leaderboard) + 1

def get_level_tier_name(level: int) -> str:
    """Get level tier name for display"""
    if level >= 100:
        return "🌟 CHALLENGER"
    elif level >= 75:
        return "💎 GRANDMASTER"
    elif level >= 50:
        return "⚡ MASTER"
    elif level >= 40:
        return "💠 DIAMOND"
    elif level >= 30:
        return "⚪ PLATINUM"
    elif level >= 20:
        return "🟨 GOLD"
    elif level >= 10:
        return "⚫ SILVER"
    else:
        return "🟤 BRONZE"

def calculate_xp_for_next_level(level: int) -> int:
    """Calculate XP required for next level"""
    if level == 0:
        return 100
    return int(100 * (1.2 ** (level - 1)))

if __name__ == "__main__":
    asyncio.run(test_gaming_system())