import asyncio
import discord
import random
import aiosqlite
from discord.ext import commands

# --- Phần kết nối SQLite với aiosqlite ---
async def get_database_connection():
    conn = await aiosqlite.connect('economy.db')
    await conn.execute('PRAGMA journal_mode=WAL;')
    return conn

async def is_registered(user_id):
    conn = await get_database_connection()
    async with conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
        result = await cursor.fetchone()
    await conn.close()
    return result is not None

async def update_balance(user_id, amount):
    """Cập nhật balance của người chơi."""
    conn = await get_database_connection()
    await conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    await conn.commit()
    await conn.close()

# Bảng roulette: gồm các số từ 0 đến 36 và các màu tương ứng
ROULETTE = {
    0: "🟢", 1: "🔴", 2: "⚫️", 3: "🔴", 4: "⚫️", 5: "🔴", 6: "⚫️",
    7: "🔴", 8: "⚫️", 9: "🔴", 10: "⚫️", 11: "⚫️", 12: "🔴", 13: "⚫️",
    14: "🔴", 15: "⚫️", 16: "🔴", 17: "⚫️", 18: "🔴", 19: "🔴",
    20: "⚫️", 21: "🔴", 22: "⚫️", 23: "🔴", 24: "⚫️", 25: "🔴",
    26: "⚫️", 27: "🔴", 28: "⚫️", 29: "🔴", 30: "⚫️", 31: "⚫️",
    32: "🔴", 33: "⚫️", 34: "🔴", 35: "⚫️", 36: "🔴"
}

# Danh sách các GIF prefab animation
GIF_CHOICES = [
    'wheel_fast.gif',   # quay nhanh
    'wheel_medium.gif', # quay trung bình
    'wheel_slow.gif'    # quay chậm
]

class Roulette(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="roulette", aliases=["quayso", "rou"])
    async def roulette(self, ctx, bet_amount: int, bet_type: str):
        """
        Chơi roulette: !roulette <số tiền> <phân loại cược>
        """
        user_id = ctx.author.id

        # Kiểm tra đăng ký và số dư
        if not await is_registered(user_id):
            return await ctx.send("Bạn chưa đăng ký tài khoản.")
        if bet_amount <= 0:
            return await ctx.send("Số tiền cược phải lớn hơn 0.")

        conn = await get_database_connection()
        async with conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
        await conn.close()
        balance = row[0] if row else 0
        if bet_amount > balance:
            return await ctx.send("Bạn không đủ tiền để cược số tiền này.")

        # Quay roulette và tính thắng thua
        result_num = random.randint(0, 36)
        result_color = ROULETTE[result_num]
        win = False
        payout = 0
        bet = bet_type.lower()
        # ... logic cược (giữ nguyên) ...
        if bet == "color_red" and result_color == "🔴": win, payout = True, bet_amount*2
        elif bet == "color_black" and result_color == "⚫️": win, payout = True, bet_amount*2
        elif bet == "color_green" and result_color == "🟢": win, payout = True, bet_amount*14
        elif bet.startswith("number_"):
            try:
                num = int(bet.split("_")[1])
                if num == result_num: win, payout = True, bet_amount*36
            except: pass
        elif bet == "odd" and result_num != 0 and result_num % 2 == 1: win, payout = True, bet_amount*2
        elif bet == "even" and result_num != 0 and result_num % 2 == 0: win, payout = True, bet_amount*2
        elif bet == "dozen1" and 1 <= result_num <= 12: win, payout = True, bet_amount*3
        elif bet == "dozen2" and 13 <= result_num <= 24: win, payout = True, bet_amount*3
        elif bet == "dozen3" and 25 <= result_num <= 36: win, payout = True, bet_amount*3

        # Cập nhật balance
        await update_balance(user_id, (payout - bet_amount) if win else -bet_amount)

        # Tạo embed kết quả
        embed = discord.Embed(title="Kết quả Roulette", color=discord.Color.blue())
        embed.add_field(name="Số quay", value=f"**{result_num}** {result_color}", inline=False)
        embed.add_field(name="Cược", value=f"{bet_amount} coins vào **{bet}**", inline=False)
        if win:
            embed.add_field(name="🎉 Bạn thắng!", value=f"+{payout-bet_amount} coins (Tổng: {payout})", inline=False)
        else:
            embed.add_field(name="😞 Bạn thua", value=f"-{bet_amount} coins", inline=False)

        # Chọn GIF prefab ngẫu nhiên
        selected_gif = random.choice(GIF_CHOICES)
        try:
            gif_file = discord.File(selected_gif, filename='spin.gif')
            embed.set_image(url='attachment://spin.gif')
            await ctx.send(file=gif_file, embed=embed)
        except Exception:
            await ctx.send(embed=embed)

async def setup(client):
    await client.add_cog(Roulette(client))