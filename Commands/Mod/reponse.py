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


class Reponse(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.channel_id = 993153068378116127

    @commands.hybrid_command(name="reponse", description="bot phản hồi lại tin nhắn của người dùng")
    @is_guild_owner_or_bot_owner()
    async def reponse(self, ctx, user: discord.User, *, content):
        cursor.execute("SELECT * FROM users WHERE user_id=?", (user.id,))
        result = cursor.fetchone()
        if result is None:
            cursor.execute("INSERT INTO users (user_id, reponse) VALUES (?, ?)", (user.id, content))
        else:
            cursor.execute("UPDATE users SET reponse=? WHERE user_id=?", (content, user.id))
        conn.commit()
        await ctx.send(f"Phản ứng đã được lưu cho {user.mention}")
        await asyncio.sleep(5)
        await ctx.message.delete()
        
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.reference or message.channel.id == 1210296290026455140 or message.channel.id == 1210417888272318525 or message.channel.id == 1256198177246285825:
            return
        mentioned_users = message.mentions
        for user in mentioned_users:
            cursor.execute("SELECT reponse FROM users WHERE user_id=?", (user.id,))
            result = cursor.fetchone()
            if result is not None and result[0]:
                msg = await message.channel.send(result[0])
                try:
                    await asyncio.sleep(30)
                    await msg.delete()
                except discord.errors.NotFound:
                    pass  # Bỏ qua lỗi nếu tin nhắn không còn tồn tại
    
    @commands.hybrid_command(description="Hiển thị DANH SÁCH trả lời của người dùng")
    @is_guild_owner_or_bot_owner()
    async def xoareponse(self, ctx, user: discord.User):
        cursor.execute("SELECT reponse FROM users WHERE user_id=?", (user.id,))
        result = cursor.fetchone()
        if result is not None:
            cursor.execute("UPDATE users SET reponse=? WHERE user_id=?", ("", user.id))
            conn.commit()
            await ctx.send(f"Đã xóa phản hồi cho {user.mention}")
            await asyncio.sleep(5)
            await ctx.message.delete()
        else:
            await ctx.send(f"{user.mention} chưa có phản hồi được lưu.")
            await asyncio.sleep(5)
            await ctx.message.delete()


    @commands.hybrid_command(name="show_reponse", description="Hiển thị DANH SÁCH trả lời của người dùng")
    @is_guild_owner_or_bot_owner()
    async def show_reponse(self, ctx, user: discord.User = None):
        if user is None:
            cursor.execute("SELECT user_id, reponse FROM users")
            results = cursor.fetchall()
            if results:
                reponse_list = "\n".join([f"{ctx.guild.get_member(result[0])}: {result[1]}" for result in results])
                await ctx.send(f"Danh sách nội dung đã lưu:\n{reponse_list}")
            else:
                await ctx.send("Không có nội dung nào được lưu.")
        else:
            cursor.execute("SELECT reponse FROM users WHERE user_id=?", (user.id,))
            result = cursor.fetchone()
            if result is not None:
                await ctx.send(f"Nội dung cho {user.mention}: {result[0]}")
            else:
                await ctx.send(f"{user.mention} chưa có nội dung được lưu.")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        if before.channel.id != self.channel_id:
            return
        original_content = before.content
        await asyncio.sleep(0.5)
        try:
            if before.content != after.content:
                channel = before.channel
                msg = await after.reply(f"Chơi chỉnh sửa tn kìa bây! Chat gì tầm bậy hả?")
                await asyncio.sleep(2)
                await msg.delete()
        except discord.errors.NotFound:
            pass

async def setup(client):
    await client.add_cog(Reponse(client))