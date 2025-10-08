import asyncio
import discord
import random
import sqlite3
import datetime
from discord.ext import commands

# Kết nối và tạo bảng trong SQLite
conn = sqlite3.connect('economy.db')
cursor = conn.cursor()


def is_registered(user_id):  # Hàm kiểm tra xem người dùng đã được đăng ký hay chưa
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None


def get_formatted_balance(user_id):  # Hàm lấy số tiền hiện có của người dùng
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    balance = cursor.fetchone()
    if balance:
        # Định dạng số tiền có dấu phẩy
        formatted_balance = "{:,}".format(balance[0])
        return formatted_balance
    return None


def get_balance(user_id):  # Hàm lấy số tiền hiện có của người dùng
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    balance = cursor.fetchone()
    if balance:
        return balance[0]
    return None


class Lock(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    # Khoá người dùng khi có hành vi gian lận
    async def lock(self, ctx, cheater: discord.User):
        if ctx.author.guild_permissions.administrator:
            cursor.execute(
                "UPDATE users SET is_locked = 1 WHERE user_id = ?", (cheater.id,))
            conn.commit()
            await ctx.send(f"{cheater.mention} đã bị khoá tài khoản vì hành vi gian lận.")
        else:
            await ctx.send("Bạn không có quyền thực hiện tác vụ này.")

    @commands.command()
    # Xác thực người dùng là con người bằng cách gửi mã Captcha
    async def captcha(self, ctx):
        user_id = ctx.author.id
        cursor.execute(
            "SELECT captcha_attempts FROM users WHERE user_id = ?", (user_id,))
        attempts = cursor.fetchone()[0]

        if attempts >= 5:
            await ctx.send("Bạn đã nhập sai quá 5 lần. Tài khoản của bạn đã bị khoá 1 ngày.")
            cursor.execute(
                "UPDATE users SET is_locked = 1 WHERE user_id = ?", (user_id,))
        else:
            captcha_code = random.randint(1000, 9999)
            await ctx.send(f"{ctx.author.mention}, nhập mã sau để xác thực: {captcha_code}")

            def check(msg):
                return msg.author == ctx.author and msg.content.isdigit()

            try:
                msg = await self.client.wait_for('message', check=check, timeout=30)
                if int(msg.content) == captcha_code:
                    await ctx.send("Xác thực thành công!")
                    cursor.execute(
                        "UPDATE users SET captcha_attempts = 0 WHERE user_id = ?", (user_id,))
                    conn.commit()
                else:
                    await ctx.send("Mã xác thực sai. Vui lòng thử lại.")
                    cursor.execute(
                        "UPDATE users SET captcha_attempts = captcha_attempts + 1 WHERE user_id = ?", (user_id,))
                conn.commit()
            except asyncio.TimeoutError:
                await ctx.send("Hết thời gian xác thực. Vui lòng thử lại sau.")
                cursor.execute(
                    "UPDATE users SET captcha_attempts = captcha_attempts + 1 WHERE user_id = ?", (user_id,))
                conn.commit()

async def setup(client):
    await client.add_cog(Lock(client))