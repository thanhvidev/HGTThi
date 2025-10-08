#!/usr/bin/env python3
"""
Simple Gaming System Test - No Discord Dependencies
"""

import sys
sys.path.append('.')
import config

def test_config():
    """Test gaming configuration"""
    print("🎮 Testing Gaming Configuration")
    print("=" * 50)
    
    # Test achievements
    print(f"\n🏆 Achievements: {len(config.ACHIEVEMENTS)} total")
    
    categories = {}
    for ach_id, ach_data in config.ACHIEVEMENTS.items():
        category = ach_data.get('category', 'unknown')
        if category not in categories:
            categories[category] = []
        categories[category].append(ach_data['name'])
    
    for category, achievements in categories.items():
        print(f"  📂 {category.title()}: {len(achievements)} achievements")
        for ach_name in achievements[:3]:  # Show first 3
            print(f"    - {ach_name}")
        if len(achievements) > 3:
            print(f"    ... and {len(achievements) - 3} more")
    
    # Test rarity system
    print(f"\n💎 Rarity System:")
    rarities = {}
    for ach_data in config.ACHIEVEMENTS.values():
        rarity = ach_data.get('rarity', 'common')
        if rarity not in rarities:
            rarities[rarity] = 0
        rarities[rarity] += 1
    
    for rarity, count in rarities.items():
        color = config.RARITY_COLORS.get(rarity, (128, 128, 128))
        print(f"  {rarity.title()}: {count} achievements (RGB{color})")
    
    # Test gaming colors
    print(f"\n🎨 Gaming Color Scheme:")
    for color_name, rgb in config.GAMING_COLORS.items():
        print(f"  {color_name}: RGB{rgb}")
    
    # Test level tiers
    print(f"\n⚡ Level Tier System:")
    for tier, color in config.LEVEL_COLORS.items():
        print(f"  {tier.title()}: RGB{color}")
    
    # Test achievement categories
    print(f"\n📁 Achievement Categories:")
    for cat_id, cat_data in config.ACHIEVEMENT_CATEGORIES.items():
        print(f"  {cat_data['icon']} {cat_data['name']}: RGB{cat_data['color']}")
    
    print(f"\n✅ Gaming Configuration Test Complete!")
    
    # Test assets exist
    import os
    print(f"\n📁 Assets Check:")
    
    assets_dirs = ['fonts', 'achievements', 'assets']
    for dirname in assets_dirs:
        if os.path.exists(dirname):
            files = os.listdir(dirname)
            print(f"  📂 {dirname}: {len(files)} files")
            if files:
                for filename in files[:3]:  # Show first 3
                    print(f"    - {filename}")
                if len(files) > 3:
                    print(f"    ... and {len(files) - 3} more")
        else:
            print(f"  ❌ {dirname}: Directory not found")

def test_achievement_requirements():
    """Test achievement requirement logic"""
    print(f"\n🧪 Testing Achievement Requirements:")
    
    # Mock user stats
    test_stats = {
        'level': 25,
        'messages': 500,
        'voice_minutes': 1200,
        'achievements': []
    }
    
    print(f"Test user stats: Level {test_stats['level']}, {test_stats['messages']} messages, {test_stats['voice_minutes']} voice minutes")
    
    eligible_achievements = []
    for ach_id, ach_data in config.ACHIEVEMENTS.items():
        requirement = ach_data.get('requirement', {})
        
        # Check if user meets requirements
        meets_requirements = True
        for req_type, req_value in requirement.items():
            if req_type == 'level' and test_stats['level'] < req_value:
                meets_requirements = False
                break
            elif req_type == 'messages' and test_stats['messages'] < req_value:
                meets_requirements = False
                break
            elif req_type == 'voice_minutes' and test_stats['voice_minutes'] < req_value:
                meets_requirements = False
                break
        
        if meets_requirements:
            eligible_achievements.append((ach_id, ach_data))
    
    print(f"\n🎯 Eligible Achievements: {len(eligible_achievements)}")
    for ach_id, ach_data in eligible_achievements:
        rarity = ach_data.get('rarity', 'common')
        print(f"  🏆 {ach_data['name']} ({rarity}) - +{ach_data['reward_xp']} XP")

if __name__ == "__main__":
    test_config()
    test_achievement_requirements()