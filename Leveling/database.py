import sqlite3
import asyncio
from datetime import datetime, timedelta
import json
from typing import Optional, Dict, Any, List
import os

class LevelingDatabase:
    def __init__(self, db_path: str = "economy.db"):
        self.db_path = db_path
        self.init_tables()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_tables(self):
        """Initialize leveling tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create leveling stats table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS leveling_stats (
                    user_id INTEGER,
                    guild_id INTEGER,
                    level INTEGER DEFAULT 1,
                    xp INTEGER DEFAULT 0,
                    total_xp INTEGER DEFAULT 0,
                    messages INTEGER DEFAULT 0,
                    voice_minutes INTEGER DEFAULT 0,
                    last_message_xp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    voice_join_time TIMESTAMP,
                    daily_messages INTEGER DEFAULT 0,
                    last_daily_reset DATE DEFAULT CURRENT_DATE,
                    achievements TEXT DEFAULT '[]',
                    custom_bg TEXT DEFAULT NULL,
                    custom_color TEXT DEFAULT NULL,
                    PRIMARY KEY (user_id, guild_id)
                )
            ''')
            
            # Create achievements table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_achievements (
                    user_id INTEGER,
                    guild_id INTEGER,
                    achievement_id TEXT,
                    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, guild_id, achievement_id)
                )
            ''')
            
            # Create guild leveling config table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS leveling_config (
                    guild_id INTEGER PRIMARY KEY,
                    level_up_channel INTEGER,
                    xp_channels TEXT DEFAULT '[]',
                    disabled_channels TEXT DEFAULT '[]',
                    level_roles TEXT DEFAULT '{}',
                    announcement_enabled INTEGER DEFAULT 1,
                    custom_message TEXT DEFAULT NULL
                )
            ''')
            
            conn.commit()
    
    def get_user_stats(self, user_id: int, guild_id: int) -> Dict[str, Any]:
        """Get user leveling stats"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT level, xp, total_xp, messages, voice_minutes, 
                       achievements, custom_bg, custom_color, daily_messages, last_daily_reset
                FROM leveling_stats 
                WHERE user_id = ? AND guild_id = ?
            ''', (user_id, guild_id))
            
            row = cursor.fetchone()
            if row:
                # Check if need to reset daily messages
                today = datetime.now().date()
                last_reset = datetime.strptime(row[9], '%Y-%m-%d').date() if row[9] else today
                daily_messages = row[8] if last_reset == today else 0
                
                if last_reset != today:
                    # Reset daily messages
                    cursor.execute('''
                        UPDATE leveling_stats 
                        SET daily_messages = 0, last_daily_reset = ?
                        WHERE user_id = ? AND guild_id = ?
                    ''', (today.isoformat(), user_id, guild_id))
                    conn.commit()
                
                return {
                    'level': row[0],
                    'xp': row[1],
                    'total_xp': row[2],
                    'messages': row[3],
                    'voice_minutes': row[4],
                    'achievements': json.loads(row[5]) if row[5] else [],
                    'custom_bg': row[6],
                    'custom_color': row[7],
                    'daily_messages': daily_messages
                }
            else:
                # Create new user entry
                cursor.execute('''
                    INSERT INTO leveling_stats (user_id, guild_id)
                    VALUES (?, ?)
                ''', (user_id, guild_id))
                conn.commit()
                return {
                    'level': 1,
                    'xp': 0,
                    'total_xp': 0,
                    'messages': 0,
                    'voice_minutes': 0,
                    'achievements': [],
                    'custom_bg': None,
                    'custom_color': None,
                    'daily_messages': 0
                }
    
    def add_xp(self, user_id: int, guild_id: int, xp_amount: int, source: str = 'message') -> Dict[str, Any]:
        """Add XP to user and return if leveled up"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get current stats
            stats = self.get_user_stats(user_id, guild_id)
            old_level = stats['level']
            
            # Calculate new XP and level
            new_xp = stats['xp'] + xp_amount
            new_total_xp = stats['total_xp'] + xp_amount
            new_level = self.calculate_level(new_total_xp)
            
            # If leveled up, reset current XP
            if new_level > old_level:
                xp_for_current_level = self.xp_for_level(new_level)
                new_xp = new_total_xp - xp_for_current_level
            
            # Update stats based on source
            if source == 'message':
                cursor.execute('''
                    UPDATE leveling_stats 
                    SET xp = ?, total_xp = ?, level = ?, messages = messages + 1,
                        last_message_xp = CURRENT_TIMESTAMP, daily_messages = daily_messages + 1
                    WHERE user_id = ? AND guild_id = ?
                ''', (new_xp, new_total_xp, new_level, user_id, guild_id))
            elif source == 'voice':
                cursor.execute('''
                    UPDATE leveling_stats 
                    SET xp = ?, total_xp = ?, level = ?, voice_minutes = voice_minutes + 1
                    WHERE user_id = ? AND guild_id = ?
                ''', (new_xp, new_total_xp, new_level, user_id, guild_id))
            else:
                cursor.execute('''
                    UPDATE leveling_stats 
                    SET xp = ?, total_xp = ?, level = ?
                    WHERE user_id = ? AND guild_id = ?
                ''', (new_xp, new_total_xp, new_level, user_id, guild_id))
            
            conn.commit()
            
            return {
                'leveled_up': new_level > old_level,
                'old_level': old_level,
                'new_level': new_level,
                'xp_gained': xp_amount,
                'new_xp': new_xp,
                'new_total_xp': new_total_xp
            }
    
    def set_voice_join_time(self, user_id: int, guild_id: int, join_time: Optional[datetime] = None):
        """Set voice channel join time"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if join_time is None:
                join_time = datetime.now()
            
            cursor.execute('''
                UPDATE leveling_stats 
                SET voice_join_time = ?
                WHERE user_id = ? AND guild_id = ?
            ''', (join_time.isoformat(), user_id, guild_id))
            
            if cursor.rowcount == 0:
                # Create entry if doesn't exist
                cursor.execute('''
                    INSERT INTO leveling_stats (user_id, guild_id, voice_join_time)
                    VALUES (?, ?, ?)
                ''', (user_id, guild_id, join_time.isoformat()))
            
            conn.commit()
    
    def calculate_voice_time_and_xp(self, user_id: int, guild_id: int) -> int:
        """Calculate voice time and return XP earned"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT voice_join_time FROM leveling_stats
                WHERE user_id = ? AND guild_id = ?
            ''', (user_id, guild_id))
            
            row = cursor.fetchone()
            if not row or not row[0]:
                return 0
            
            join_time = datetime.fromisoformat(row[0])
            minutes_spent = int((datetime.now() - join_time).total_seconds() / 60)
            
            # Clear join time
            cursor.execute('''
                UPDATE leveling_stats 
                SET voice_join_time = NULL
                WHERE user_id = ? AND guild_id = ?
            ''', (user_id, guild_id))
            conn.commit()
            
            return minutes_spent
    
    @staticmethod
    def calculate_level(total_xp: int) -> int:
        """Calculate level from total XP"""
        if total_xp < 100:
            return 1
        
        level = 1
        xp_needed = 100
        
        while total_xp >= xp_needed:
            total_xp -= xp_needed
            level += 1
            xp_needed = int(100 * (1.2 ** (level - 1)))
        
        return level
    
    @staticmethod
    def xp_for_level(level: int) -> int:
        """Calculate total XP needed to reach a level"""
        if level <= 1:
            return 0
        
        total_xp = 0
        for i in range(1, level):
            total_xp += int(100 * (1.2 ** (i - 1)))
        
        return total_xp
    
    @staticmethod
    def xp_for_next_level(current_level: int) -> int:
        """Calculate XP needed for next level"""
        return int(100 * (1.2 ** (current_level - 1)))
    
    def unlock_achievement(self, user_id: int, guild_id: int, achievement_id: str) -> bool:
        """Unlock achievement for user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if already unlocked
            cursor.execute('''
                SELECT 1 FROM user_achievements
                WHERE user_id = ? AND guild_id = ? AND achievement_id = ?
            ''', (user_id, guild_id, achievement_id))
            
            if cursor.fetchone():
                return False  # Already unlocked
            
            # Unlock achievement
            cursor.execute('''
                INSERT INTO user_achievements (user_id, guild_id, achievement_id)
                VALUES (?, ?, ?)
            ''', (user_id, guild_id, achievement_id))
            
            # Add to achievements list in leveling_stats
            stats = self.get_user_stats(user_id, guild_id)
            achievements = stats['achievements']
            if achievement_id not in achievements:
                achievements.append(achievement_id)
                
                cursor.execute('''
                    UPDATE leveling_stats 
                    SET achievements = ?
                    WHERE user_id = ? AND guild_id = ?
                ''', (json.dumps(achievements), user_id, guild_id))
            
            conn.commit()
            return True
    
    def get_user_achievements(self, user_id: int, guild_id: int) -> List[Dict[str, Any]]:
        """Get user's unlocked achievements"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT achievement_id, unlocked_at 
                FROM user_achievements
                WHERE user_id = ? AND guild_id = ?
                ORDER BY unlocked_at DESC
            ''', (user_id, guild_id))
            
            return [{'id': row[0], 'unlocked_at': row[1]} for row in cursor.fetchall()]
    
    def get_leaderboard(self, guild_id: int, limit: int = 10, sort_by: str = 'level') -> List[Dict[str, Any]]:
        """Get guild leaderboard"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if sort_by == 'level':
                order_clause = 'ORDER BY level DESC, total_xp DESC'
            elif sort_by == 'xp':
                order_clause = 'ORDER BY total_xp DESC'
            elif sort_by == 'messages':
                order_clause = 'ORDER BY messages DESC'
            elif sort_by == 'voice':
                order_clause = 'ORDER BY voice_minutes DESC'
            else:
                order_clause = 'ORDER BY level DESC, total_xp DESC'
            
            cursor.execute(f'''
                SELECT user_id, level, xp, total_xp, messages, voice_minutes
                FROM leveling_stats 
                WHERE guild_id = ?
                {order_clause}
                LIMIT ?
            ''', (guild_id, limit))
            
            results = []
            for i, row in enumerate(cursor.fetchall(), 1):
                results.append({
                    'rank': i,
                    'user_id': row[0],
                    'level': row[1],
                    'xp': row[2],
                    'total_xp': row[3],
                    'messages': row[4],
                    'voice_minutes': row[5]
                })
            
            return results
    
    def get_guild_config(self, guild_id: int) -> Dict[str, Any]:
        """Get guild leveling configuration"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT level_up_channel, xp_channels, disabled_channels, 
                       level_roles, announcement_enabled, custom_message
                FROM leveling_config
                WHERE guild_id = ?
            ''', (guild_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'level_up_channel': row[0],
                    'xp_channels': json.loads(row[1]) if row[1] else [],
                    'disabled_channels': json.loads(row[2]) if row[2] else [],
                    'level_roles': json.loads(row[3]) if row[3] else {},
                    'announcement_enabled': bool(row[4]),
                    'custom_message': row[5]
                }
            else:
                # Create default config
                default_config = {
                    'level_up_channel': None,
                    'xp_channels': [],
                    'disabled_channels': [],
                    'level_roles': {},
                    'announcement_enabled': True,
                    'custom_message': None
                }
                self.update_guild_config(guild_id, default_config)
                return default_config
    
    def update_guild_config(self, guild_id: int, config: Dict[str, Any]):
        """Update guild leveling configuration"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO leveling_config 
                (guild_id, level_up_channel, xp_channels, disabled_channels, 
                 level_roles, announcement_enabled, custom_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                guild_id,
                config.get('level_up_channel'),
                json.dumps(config.get('xp_channels', [])),
                json.dumps(config.get('disabled_channels', [])),
                json.dumps(config.get('level_roles', {})),
                int(config.get('announcement_enabled', True)),
                config.get('custom_message')
            ))
            conn.commit()
    
    def update_user_customization(self, user_id: int, guild_id: int, custom_bg: str = None, custom_color: str = None):
        """Update user profile customization"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Ensure user exists
            self.get_user_stats(user_id, guild_id)
            
            cursor.execute('''
                UPDATE leveling_stats 
                SET custom_bg = ?, custom_color = ?
                WHERE user_id = ? AND guild_id = ?
            ''', (custom_bg, custom_color, user_id, guild_id))
            conn.commit()