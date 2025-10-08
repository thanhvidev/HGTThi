#!/usr/bin/env python3
"""
Test Gaming Configuration - Standalone
"""

# Gaming/Cypher Themed Achievements System
ACHIEVEMENTS = {
    # 🎮 Gaming Starter Achievements
    "first_message": {
        "name": "Kẻ Lãm Lời", 
        "description": "Gửi tin nhắn đầu tiên trong server - khởi đầu của hành trình cyber",
        "requirement": {"messages": 1},
        "reward_xp": 50,
        "category": "starter",
        "icon": "🔓",
        "rarity": "common",
        "image": "achievements/cyber_initiate.png"
    },
    "cyber_explorer": {
        "name": "Thám Hiểm Cyber",
        "description": "Gửi 50 tin nhắn - khám phá không gian số",  
        "requirement": {"messages": 50},
        "reward_xp": 200,
        "category": "message",
        "icon": "🌐",
        "rarity": "common",
        "image": "achievements/cyber_explorer.png"
    },
    "digital_warrior": {
        "name": "Chiến Binh Số",
        "description": "Gửi 250 tin nhắn - trở thành chiến binh trong thế giới số",
        "requirement": {"messages": 250},
        "reward_xp": 750,
        "category": "message", 
        "icon": "⚔️",
        "rarity": "uncommon",
        "image": "achievements/digital_warrior.png"
    },
    "cyber_legend": {
        "name": "Huyền Thoại Cyber",
        "description": "Gửi 1000 tin nhắn - danh hiệu huyền thoại trong không gian mạng",
        "requirement": {"messages": 1000},
        "reward_xp": 2500,
        "category": "message",
        "icon": "👑", 
        "rarity": "legendary",
        "image": "achievements/cyber_legend.png"
    },
    "voice_newbie": {
        "name": "Chưa Té Lắm Lời",
        "description": "Dành 60 phút trong voice channel - bắt đầu giao tiếp bằng giọng nói",
        "requirement": {"voice_minutes": 60},
        "reward_xp": 300,
        "category": "voice",
        "icon": "🎙️",
        "rarity": "common",
        "image": "achievements/voice_newbie.png"
    },
    "level_hacker": {
        "name": "Cyber Hacker", 
        "description": "Đạt level 5 - hack được vào server này rồi",
        "requirement": {"level": 5},
        "reward_xp": 400,
        "category": "level",
        "icon": "💻",
        "rarity": "uncommon",
        "image": "achievements/cyber_hacker.png"
    },
}

# Achievement Rarity Colors (Gaming Theme)
RARITY_COLORS = {
    "common": (100, 100, 100),      # Gray - Phổ thông
    "uncommon": (0, 255, 0),        # Green - Không phổ biến  
    "rare": (0, 150, 255),          # Blue - Hiếm
    "epic": (150, 0, 255),          # Purple - Sử thi
    "legendary": (255, 165, 0),     # Orange - Huyền thoại
    "mythic": (255, 215, 0)         # Gold - Thần thoại
}

# Gaming/Cypher Color Scheme
GAMING_COLORS = {
    "cyber_blue": (0, 255, 255),
    "matrix_green": (0, 255, 0), 
    "hacker_orange": (255, 140, 0),
    "digital_purple": (138, 43, 226),
    "neon_pink": (255, 20, 147),
    "electric_yellow": (255, 255, 0),
    "dark_bg": (25, 25, 35),
    "card_bg": (35, 35, 45)
}

def test_gaming_config():
    """Test gaming configuration"""
    print("🎮 Testing Gaming/Cypher Theme Configuration")
    print("=" * 60)
    
    # Test achievements
    print(f"\n🏆 Gaming Achievements: {len(ACHIEVEMENTS)} total")
    
    categories = {}
    rarities = {}
    total_xp = 0
    
    for ach_id, ach_data in ACHIEVEMENTS.items():
        category = ach_data.get('category', 'unknown')
        rarity = ach_data.get('rarity', 'common')
        
        # Count by category
        if category not in categories:
            categories[category] = []
        categories[category].append(ach_data['name'])
        
        # Count by rarity
        if rarity not in rarities:
            rarities[rarity] = 0
        rarities[rarity] += 1
        
        # Sum XP rewards
        total_xp += ach_data.get('reward_xp', 0)
    
    print(f"\n📂 Achievement Categories:")
    for category, achievements in categories.items():
        print(f"  🎯 {category.title()}: {len(achievements)} achievements")
        for ach_name in achievements:
            print(f"    - {ach_name}")
    
    print(f"\n💎 Rarity Distribution:")
    for rarity, count in rarities.items():
        color = RARITY_COLORS.get(rarity, (128, 128, 128))
        percentage = (count / len(ACHIEVEMENTS)) * 100
        print(f"  {rarity.upper()}: {count} ({percentage:.1f}%) - RGB{color}")
    
    print(f"\n✨ Total XP Rewards: {total_xp:,} XP available")
    
    # Test gaming colors
    print(f"\n🎨 Gaming/Cypher Color Palette:")
    for color_name, rgb in GAMING_COLORS.items():
        print(f"  {color_name.replace('_', ' ').title()}: RGB{rgb}")
    
    # Test achievement requirements
    print(f"\n🎯 Achievement Requirements Analysis:")
    
    # Mock user progression
    test_levels = [1, 5, 10, 25, 50]
    test_messages = [10, 100, 500, 1000]
    test_voice = [30, 180, 600, 1440]  # minutes
    
    for level in test_levels:
        eligible = []
        for ach_id, ach_data in ACHIEVEMENTS.items():
            req = ach_data.get('requirement', {})
            if 'level' in req and req['level'] <= level:
                eligible.append(ach_data['name'])
        
        if eligible:
            print(f"  Level {level}: {len(eligible)} achievements unlockable")
    
    for msg_count in test_messages:
        eligible = []
        for ach_id, ach_data in ACHIEVEMENTS.items():
            req = ach_data.get('requirement', {})
            if 'messages' in req and req['messages'] <= msg_count:
                eligible.append(ach_data['name'])
        
        if eligible:
            print(f"  {msg_count} messages: {len(eligible)} achievements unlockable")
    
    # Test gaming theme elements
    print(f"\n🎮 Gaming Theme Features:")
    print(f"  🔥 Cyber/Matrix aesthetic with neon colors")
    print(f"  ⚡ Gaming terminology (Hacker, Warrior, Legend)")
    print(f"  🎯 Vietnamese gaming slang integration")
    print(f"  🏆 Tiered rarity system like games")
    print(f"  💫 Achievement progression rewards")
    
    print(f"\n✅ Gaming Configuration Test Complete!")
    print(f"🎉 Theme successfully integrates gaming/cypher aesthetics!")

def test_achievement_progression():
    """Test achievement unlock progression"""
    print(f"\n🧪 Testing Achievement Progression Logic:")
    
    # Simulate user progression
    user_stats = {
        'level': 0,
        'messages': 0, 
        'voice_minutes': 0,
        'unlocked_achievements': []
    }
    
    progression_steps = [
        {'messages': 1, 'voice_minutes': 0, 'level': 1},      # First message
        {'messages': 50, 'voice_minutes': 60, 'level': 3},    # Early activity
        {'messages': 250, 'voice_minutes': 180, 'level': 8},  # Regular user
        {'messages': 500, 'voice_minutes': 600, 'level': 15}, # Active user
        {'messages': 1000, 'voice_minutes': 1440, 'level': 25} # Power user
    ]
    
    for i, step in enumerate(progression_steps):
        user_stats.update(step)
        
        print(f"\n📊 Progression Step {i+1}: Level {user_stats['level']}, {user_stats['messages']} msgs, {user_stats['voice_minutes']} voice mins")
        
        newly_unlocked = []
        for ach_id, ach_data in ACHIEVEMENTS.items():
            if ach_id in user_stats['unlocked_achievements']:
                continue
                
            req = ach_data.get('requirement', {})
            meets_req = True
            
            for req_type, req_value in req.items():
                if req_type in user_stats and user_stats[req_type] < req_value:
                    meets_req = False
                    break
            
            if meets_req:
                newly_unlocked.append((ach_id, ach_data))
                user_stats['unlocked_achievements'].append(ach_id)
        
        if newly_unlocked:
            print(f"  🎉 New Achievements Unlocked:")
            total_xp_gained = 0
            for ach_id, ach_data in newly_unlocked:
                xp = ach_data['reward_xp']
                total_xp_gained += xp
                print(f"    🏆 {ach_data['name']} ({ach_data['rarity']}) - +{xp} XP")
            print(f"  ✨ Total XP Gained: +{total_xp_gained}")
        else:
            print(f"  📝 No new achievements this step")
        
        print(f"  📈 Total Unlocked: {len(user_stats['unlocked_achievements'])}/{len(ACHIEVEMENTS)}")

if __name__ == "__main__":
    test_gaming_config()
    test_achievement_progression()