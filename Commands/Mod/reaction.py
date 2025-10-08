import asyncio
import discord
import random
import sqlite3
from discord.ext import commands

# Kết nối và tạo bảng trong SQLite
conn = sqlite3.connect('economy.db', isolation_level=None)
conn.execute('pragma journal_mode=wal')
cursor = conn.cursor()

def is_guild_owner_or_bot_owner():
    async def predicate(ctx):
        guild_owner = ctx.author == ctx.guild.owner
        bot_owner = ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222
        specific_role = any(role.id == 1113463122515214427 for role in ctx.author.roles)

        return guild_owner or bot_owner or specific_role
    
    return commands.check(predicate)

class Reaction(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.hybrid_command(name="reaction", description="reaction tin nhắn người dùng")
    @is_guild_owner_or_bot_owner()
    async def reaction(self, ctx, user: discord.User, *, content):
        if (content.startswith("<:") or content.startswith("<a:")) and content.endswith(">"):
            cursor.execute("SELECT * FROM users WHERE user_id=?", (user.id,))
            result = cursor.fetchone()
            if result is None:
                cursor.execute("INSERT INTO users (user_id, reaction) VALUES (?, ?)", (user.id, content))
            else:
                cursor.execute("UPDATE users SET reaction=? WHERE user_id=?", (content, user.id))
            conn.commit()
            await ctx.send(f"Reaction đã được lưu cho {user.mention}")
            await asyncio.sleep(5)
            await ctx.message.delete()
        else:
            await ctx.send("Vui lòng nhập đúng định dạng emoji.")
            await asyncio.sleep(5)
            await ctx.message.delete()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.reference:
            return 
        mentioned_users = message.mentions
        for user in mentioned_users:
            cursor.execute("SELECT reaction FROM users WHERE user_id=?", (user.id,))
            result = cursor.fetchone()
            if result is not None and result[0]:
                await message.add_reaction(result[0])

    @commands.hybrid_command(description="Hiển thị DANH SÁCH trả lời của người dùng")
    @is_guild_owner_or_bot_owner()
    async def xoareaction(self, ctx, user: discord.User):
        cursor.execute("SELECT reaction FROM users WHERE user_id=?", (user.id,))
        result = cursor.fetchone()
        if result is not None:
            cursor.execute("UPDATE users SET reaction=? WHERE user_id=?", ("", user.id))
            conn.commit()
            await ctx.send(f"Đã xóa reaction cho {user.mention}")
            await asyncio.sleep(5)
            await ctx.message.delete()
        else:
            await ctx.send(f"{user.mention} chưa có reaction được lưu.")
            await asyncio.sleep(5)
            await ctx.message.delete()

async def setup(client):
    await client.add_cog(Reaction(client))