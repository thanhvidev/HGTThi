import asyncio
from typing import Optional, Tuple
from db import DB
import aiosqlite


async def ensure_guild(guild_id: int) -> None:
    await DB.ensure_users_schema(guild_id)


async def is_registered(guild_id: int, user_id: int) -> bool:
    await ensure_guild(guild_id)
    conn = await DB.get_conn(guild_id)
    async with conn.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,)) as cur:
        row = await cur.fetchone()
    return row is not None


async def register_user(guild_id: int, user_id: int, initial_balance: int = 0) -> bool:
    await ensure_guild(guild_id)
    conn = await DB.get_conn(guild_id)
    lock = DB.get_lock(guild_id)
    async with lock:
        async with conn.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
        if row:
            return False
        await conn.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, initial_balance))
        await conn.commit()
        return True


async def get_balance(guild_id: int, user_id: int) -> Optional[int]:
    await ensure_guild(guild_id)
    conn = await DB.get_conn(guild_id)
    async with conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)) as cur:
        row = await cur.fetchone()
    return int(row[0]) if row and row[0] is not None else None


async def add_balance(guild_id: int, user_id: int, delta: int) -> None:
    conn = await DB.get_conn(guild_id)
    lock = DB.get_lock(guild_id)
    async with lock:
        await conn.execute("UPDATE users SET balance = COALESCE(balance, 0) + ? WHERE user_id = ?", (delta, user_id))
        await conn.commit()


async def transfer(guild_id: int, sender_id: int, receiver_id: int, amount: int) -> Tuple[bool, str]:
    if amount <= 0:
        return False, "Số tiền không hợp lệ"
    conn = await DB.get_conn(guild_id)
    lock = DB.get_lock(guild_id)
    async with lock:
        async with conn.execute("SELECT balance FROM users WHERE user_id = ?", (sender_id,)) as cur:
            row = await cur.fetchone()
        bal = int(row[0]) if row and row[0] is not None else 0
        if bal < amount:
            return False, "Số dư không đủ"
        await conn.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, sender_id))
        await conn.execute("UPDATE users SET balance = COALESCE(balance,0) + ? WHERE user_id = ?", (amount, receiver_id))
        await conn.commit()
    return True, "OK"


async def get_user_field(guild_id: int, user_id: int, field: str):
    conn = await DB.get_conn(guild_id)
    async with conn.execute(f"SELECT {field} FROM users WHERE user_id = ?", (user_id,)) as cur:
        row = await cur.fetchone()
    return row[0] if row else None


async def set_user_field(guild_id: int, user_id: int, field: str, value) -> None:
    conn = await DB.get_conn(guild_id)
    lock = DB.get_lock(guild_id)
    async with lock:
        await conn.execute(f"UPDATE users SET {field} = ? WHERE user_id = ?", (value, user_id))
        await conn.commit()


async def inc_user_fields(guild_id: int, user_id: int, updates: dict) -> None:
    # updates: {field: delta}
    conn = await DB.get_conn(guild_id)
    lock = DB.get_lock(guild_id)
    async with lock:
        for field, delta in updates.items():
            await conn.execute(f"UPDATE users SET {field} = COALESCE({field}, 0) + ? WHERE user_id = ?", (delta, user_id))
        await conn.commit()
