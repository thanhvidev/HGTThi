"""
Database Helper Functions for Discord Bot
Provides easy-to-use functions for database operations
"""

from typing import Optional, Dict, Any, List, Tuple
import asyncio
from database_manager import db_manager
import logging

logger = logging.getLogger(__name__)

class UserDatabase:
    """Helper class for user-related database operations"""
    
    @staticmethod
    async def is_registered(guild_id: int, user_id: int) -> bool:
        """Check if user is registered in a guild"""
        user = await db_manager.get_user(guild_id, user_id)
        return user is not None
    
    @staticmethod
    async def register_user(guild_id: int, user_id: int, initial_balance: int = 200000) -> bool:
        """Register a new user with initial balance"""
        try:
            success = await db_manager.create_user(guild_id, user_id, initial_balance)
            if success:
                logger.info(f"Registered user {user_id} in guild {guild_id}")
            return success
        except Exception as e:
            logger.error(f"Failed to register user {user_id}: {e}")
            return False
    
    @staticmethod
    async def get_balance(guild_id: int, user_id: int) -> Optional[int]:
        """Get user balance"""
        user = await db_manager.get_user(guild_id, user_id)
        return user['balance'] if user else None
    
    @staticmethod
    async def get_formatted_balance(guild_id: int, user_id: int) -> Optional[str]:
        """Get formatted user balance with thousand separators"""
        balance = await UserDatabase.get_balance(guild_id, user_id)
        return "{:,}".format(balance) if balance is not None else None
    
    @staticmethod
    async def add_balance(guild_id: int, user_id: int, amount: int) -> bool:
        """Add to user balance"""
        return await db_manager.update_user_balance(guild_id, user_id, amount, "add")
    
    @staticmethod
    async def subtract_balance(guild_id: int, user_id: int, amount: int) -> bool:
        """Subtract from user balance"""
        return await db_manager.update_user_balance(guild_id, user_id, amount, "subtract")
    
    @staticmethod
    async def set_balance(guild_id: int, user_id: int, amount: int) -> bool:
        """Set user balance to specific amount"""
        return await db_manager.update_user_balance(guild_id, user_id, amount, "set")
    
    @staticmethod
    async def has_enough_balance(guild_id: int, user_id: int, amount: int) -> bool:
        """Check if user has enough balance"""
        balance = await UserDatabase.get_balance(guild_id, user_id)
        return balance is not None and balance >= amount
    
    @staticmethod
    async def transfer_money(guild_id: int, from_user_id: int, to_user_id: int, amount: int) -> bool:
        """Transfer money between users"""
        return await db_manager.transfer_money(guild_id, from_user_id, to_user_id, amount)
    
    @staticmethod
    async def get_user_data(guild_id: int, user_id: int, fields: List[str] = None) -> Optional[Dict]:
        """Get specific user data fields"""
        user = await db_manager.get_user(guild_id, user_id)
        if not user:
            return None
        
        if fields:
            return {field: user.get(field) for field in fields}
        return user
    
    @staticmethod
    async def update_user_field(guild_id: int, user_id: int, field: str, value: Any) -> bool:
        """Update a specific user field"""
        try:
            query = f"UPDATE users SET {field} = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?"
            await db_manager.execute_async(guild_id, query, (value, user_id))
            
            # Clear cache
            cache_key = f"{guild_id}:user:{user_id}"
            db_manager.cache.pop(cache_key, None)
            
            return True
        except Exception as e:
            logger.error(f"Failed to update user field {field}: {e}")
            return False
    
    @staticmethod
    async def increment_field(guild_id: int, user_id: int, field: str, amount: int = 1) -> bool:
        """Increment a numeric field"""
        try:
            query = f"UPDATE users SET {field} = {field} + ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?"
            await db_manager.execute_async(guild_id, query, (amount, user_id))
            
            # Clear cache
            cache_key = f"{guild_id}:user:{user_id}"
            db_manager.cache.pop(cache_key, None)
            
            return True
        except Exception as e:
            logger.error(f"Failed to increment field {field}: {e}")
            return False

class GuildDatabase:
    """Helper class for guild-related database operations"""
    
    @staticmethod
    async def get_setting(guild_id: int, key: str, default: Any = None) -> Any:
        """Get guild setting"""
        result = await db_manager.execute_async(
            guild_id,
            "SELECT setting_value FROM guild_settings WHERE setting_key = ?",
            (key,)
        )
        
        if result:
            import json
            try:
                return json.loads(result[0]['setting_value'])
            except:
                return result[0]['setting_value']
        return default
    
    @staticmethod
    async def set_setting(guild_id: int, key: str, value: Any) -> bool:
        """Set guild setting"""
        import json
        value_str = json.dumps(value) if not isinstance(value, str) else value
        
        try:
            await db_manager.execute_async(
                guild_id,
                """INSERT INTO guild_settings (setting_key, setting_value) 
                   VALUES (?, ?) 
                   ON CONFLICT(setting_key) 
                   DO UPDATE SET setting_value = ?, updated_at = CURRENT_TIMESTAMP""",
                (key, value_str, value_str)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to set guild setting {key}: {e}")
            return False
    
    @staticmethod
    async def get_all_users(guild_id: int) -> List[Dict]:
        """Get all users in a guild"""
        result = await db_manager.execute_async(
            guild_id,
            "SELECT * FROM users ORDER BY balance DESC",
            ()
        )
        return [dict(row) for row in result]
    
    @staticmethod
    async def get_top_users(guild_id: int, limit: int = 10, field: str = "balance") -> List[Dict]:
        """Get top users by a specific field"""
        result = await db_manager.execute_async(
            guild_id,
            f"SELECT user_id, {field} FROM users ORDER BY {field} DESC LIMIT ?",
            (limit,)
        )
        return [dict(row) for row in result]
    
    @staticmethod
    async def reset_all_balances(guild_id: int) -> bool:
        """Reset all user balances in a guild"""
        try:
            await db_manager.execute_async(
                guild_id,
                "UPDATE users SET balance = 0, updated_at = CURRENT_TIMESTAMP",
                ()
            )
            db_manager.clear_cache(guild_id)
            return True
        except Exception as e:
            logger.error(f"Failed to reset balances: {e}")
            return False
    
    @staticmethod
    async def add_balance_to_all(guild_id: int, amount: int) -> bool:
        """Add balance to all users in a guild"""
        try:
            await db_manager.execute_async(
                guild_id,
                "UPDATE users SET balance = balance + ?, updated_at = CURRENT_TIMESTAMP",
                (amount,)
            )
            db_manager.clear_cache(guild_id)
            return True
        except Exception as e:
            logger.error(f"Failed to add balance to all: {e}")
            return False

class TransactionDatabase:
    """Helper class for transaction-related database operations"""
    
    @staticmethod
    async def log_transaction(guild_id: int, from_user_id: Optional[int], to_user_id: Optional[int], 
                             amount: int, transaction_type: str, description: str = "") -> bool:
        """Log a transaction"""
        try:
            await db_manager.execute_async(
                guild_id,
                """INSERT INTO transactions (from_user_id, to_user_id, amount, transaction_type, description)
                   VALUES (?, ?, ?, ?, ?)""",
                (from_user_id, to_user_id, amount, transaction_type, description)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to log transaction: {e}")
            return False
    
    @staticmethod
    async def get_user_transactions(guild_id: int, user_id: int, limit: int = 10) -> List[Dict]:
        """Get user's recent transactions"""
        result = await db_manager.execute_async(
            guild_id,
            """SELECT * FROM transactions 
               WHERE from_user_id = ? OR to_user_id = ?
               ORDER BY timestamp DESC LIMIT ?""",
            (user_id, user_id, limit)
        )
        return [dict(row) for row in result]
    
    @staticmethod
    async def get_recent_transactions(guild_id: int, limit: int = 20) -> List[Dict]:
        """Get recent transactions in guild"""
        result = await db_manager.execute_async(
            guild_id,
            "SELECT * FROM transactions ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        return [dict(row) for row in result]

class LeaderboardDatabase:
    """Helper class for leaderboard operations"""
    
    @staticmethod
    async def get_balance_leaderboard(guild_id: int, limit: int = 10) -> List[Dict]:
        """Get balance leaderboard"""
        return await db_manager.get_leaderboard(guild_id, limit)
    
    @staticmethod
    async def get_user_rank(guild_id: int, user_id: int, field: str = "balance") -> Optional[int]:
        """Get user's rank in a specific field"""
        result = await db_manager.execute_async(
            guild_id,
            f"""SELECT COUNT(*) + 1 as rank FROM users 
                WHERE {field} > (SELECT {field} FROM users WHERE user_id = ?)""",
            (user_id,)
        )
        
        if result:
            return result[0]['rank']
        return None
    
    @staticmethod
    async def get_field_leaderboard(guild_id: int, field: str, limit: int = 10) -> List[Dict]:
        """Get leaderboard for any field"""
        cache_key = f"{guild_id}:leaderboard:{field}:{limit}"
        cached = db_manager.get_cached(cache_key)
        if cached:
            return cached
        
        result = await db_manager.execute_async(
            guild_id,
            f"SELECT user_id, {field} FROM users WHERE {field} > 0 ORDER BY {field} DESC LIMIT ?",
            (limit,)
        )
        
        leaderboard = [dict(row) for row in result]
        db_manager.set_cached(cache_key, leaderboard)
        return leaderboard

# Utility functions for backwards compatibility
async def is_registered(user_id: int, guild_id: int) -> bool:
    """Check if user is registered (backwards compatible)"""
    return await UserDatabase.is_registered(guild_id, user_id)

async def get_balance(user_id: int, guild_id: int) -> Optional[int]:
    """Get user balance (backwards compatible)"""
    return await UserDatabase.get_balance(guild_id, user_id)

async def get_formatted_balance(user_id: int, guild_id: int) -> Optional[str]:
    """Get formatted balance (backwards compatible)"""
    return await UserDatabase.get_formatted_balance(guild_id, user_id)