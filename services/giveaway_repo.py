from typing import List, Tuple
from db import DB


async def ensure_guild(guild_id: int) -> None:
    await DB.ensure_giveaways_schema(guild_id)


async def create_giveaway(guild_id: int, end_unix: int, prize: str, message_id: int, host_id: int, winners: int) -> None:
    await ensure_guild(guild_id)
    conn = await DB.get_conn(guild_id)
    await conn.execute(
        "INSERT INTO giveaways (time, prize, message, participants, winners, finished, host, win) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (end_unix, prize, message_id, "[]", "[]", False, host_id, winners)
    )
    await conn.commit()


async def get_giveaway(guild_id: int, message_id: int):
    conn = await DB.get_conn(guild_id)
    async with conn.execute("SELECT * FROM giveaways WHERE message = ?", (message_id,)) as cur:
        return await cur.fetchone()


async def update_participants(guild_id: int, message_id: int, participants: str) -> None:
    conn = await DB.get_conn(guild_id)
    await conn.execute("UPDATE giveaways SET participants = ? WHERE message = ?", (participants, message_id))
    await conn.commit()


async def end_giveaway(guild_id: int, message_id: int, winners: str) -> None:
    conn = await DB.get_conn(guild_id)
    await conn.execute("UPDATE giveaways SET finished = 1, winners = ? WHERE message = ?", (winners, message_id))
    await conn.commit()


async def clean_finished(guild_id: int) -> None:
    conn = await DB.get_conn(guild_id)
    await conn.execute("DELETE FROM giveaways WHERE finished = 1")
    await conn.commit()
