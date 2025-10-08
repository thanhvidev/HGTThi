import asyncio
import sqlite3
import discord
from discord.ext import commands
import random
from Economy.Relax.cache.list_color import list_color
import time as pyTime
from Commands.Mod.list_emoji import list_emoji, lambanh_emoji, profile_emoji, sinhnhat_emoji

def get_database_connection():
    conn = sqlite3.connect('economy.db', isolation_level=None)
    conn.execute('PRAGMA journal_mode=WAL;')
    return conn

def is_registered(user_id):
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def get_balance(user_id):  
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    balance = cursor.fetchone()
    conn.close()
    if balance:
        return balance[0]
    return None

def is_allowed_channel_check():
    async def predicate(ctx):
        allowed_channel_ids = [993153068378116127, 1147355133622108262, 1152710848284991549, 1079170812709458031, 1207593935359320084, 1215331218124574740, 1215331281878130738, 1051454917702848562, 1210296290026455140, 1210417888272318525, 1256198177246285825, 1050649044160094218, 1091208904920281098, 1238177759289806878, 1243264114483138600, 1251418765665505310, 1243440233685712906, 1237810926913323110, 1247072223861280768, 1270031327999164548, 1022533822031601766, 1065348266193063979, 1027622168181350400, 1072536912562241546, 1045395054954565652, 1273768834830041301, 1273768884885000326, 1273769291099144222, 1026627301573677147, 1035183712582766673, 1090897131486842990, 1213122881802997770, 1104362707580375120]
        if ctx.channel.id in allowed_channel_ids:
            return False
        return True
    return commands.check(predicate)

def is_allowed_channel():
    async def predicate(ctx):
        allowed_channel_id = 1273769137985818624
        if ctx.channel.id != allowed_channel_id:
            message = await ctx.reply(f"**Dùng lệnh** [__**ở đây**__](<https://discord.com/channels/832579380634451969/1273769137985818624>)")
            await asyncio.sleep(10)
            await message.delete()
            await ctx.message.delete()
            return False
        return True
    return commands.check(predicate)

maytinh = "<:maytinh:1271305161989427250>"
butchi = "<:butchixanh:1271305180519858238>"
dongho = "<:emoji_53:1273750148778033152>"
hopqua = "<:emoji_54:1273750182445711512>"
pinkcoin = "<:timcoin:1192458078294122526>"
dung = "<a:dung:1271305150492835924>"
sai = "<:sai:1271305088350027853>"
dk = "<:profile:1181400074127945799>"
streak = "<:huychuong:1271289997231788032>"
xulove = '<a:xu_love_2025:1339490786840150087>'

class Lamtoan(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def check_command_disabled(self, ctx):  
        guild_id = str(ctx.guild.id)  
        command_name = ctx.command.name.lower()  
        if guild_id in self.client.get_cog('Toggle').toggles:  
            if command_name in self.client.get_cog('Toggle').toggles[guild_id]:  
                if ctx.channel.id in self.client.get_cog('Toggle').toggles[guild_id][command_name]:  
                    await ctx.send(f"Lệnh `{command_name}` đã bị tắt ở kênh này.")  
                    return True  
        return False 

    @commands.hybrid_command(aliases=["toan"], description="Trò chơi LÀM TOÁN NHANH")
    @commands.cooldown(1, 30, commands.BucketType.user)
    # @is_allowed_channel_check()
    @is_allowed_channel()
    async def mathquiz(self, ctx):
        if ctx.author.avatar:
            avatar_url = ctx.author.avatar.url
        else:
            avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
        if await self.check_command_disabled(ctx):
            return
        if not is_registered(ctx.author.id):
            await ctx.send(f"{dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
            return
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?",
                       (ctx.author.id,))
        result = cursor.fetchone()
        balance = result[2]

        # Tạo bài toán ngẫu nhiên
        operators = ['+', '-', '*', '/']
        operator = random.choice(operators)
        if operator == '*':
            num1 = random.randint(1, 100)
            num2 = random.randint(1, num1)
            answer = num1 * num2
        elif operator == '/':
            num2 = random.randint(1, 40)
            answer = random.randint(1, 40)
            num1 = num2 * answer
        else:
            num1 = random.randint(1, 2000)
            num2 = random.randint(1, num1)  # Đảm bảo num1 lớn hơn num2
            if operator == '+':
                answer = num1 + num2
            elif operator == '-':
                answer = num1 - num2

        question = f"**{num1} {operator} {num2} =**"

        embed = discord.Embed(
            title=f"{maytinh} **LÀM TOÁN NHANH**",
            description=f"ㅤ\n# {butchi} {question} **?**\nㅤ\n{dongho} **`10s`** | {hopqua} **`2k`** {list_emoji.pinkcoin}",
            color=discord.Color.from_rgb(0, 255, 0)
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1211199649667616768/1271441774551896104/8042750.png")
        embed.set_footer(text=f"{ctx.author.name}", icon_url=avatar_url) 
        send = await ctx.send(embed=embed)

        def check(m):
            return m.author.id == ctx.author.id and m.channel == ctx.channel and m.reference is not None and m.reference.message_id == send.id

        timeout = 15
        timer_task = asyncio.create_task(
            self.update_timer(ctx, send, question, timeout))

        try:
            message = await self.client.wait_for("message", timeout=timeout, check=check)
            timer_task.cancel()  # Hủy tác vụ đếm ngược nếu người dùng trả lời
            try:
                user_answer = int(message.content)
                if user_answer == answer:
                    if discord.utils.get(ctx.author.roles, id=1339482195907186770):
                        cursor.execute(
                            "UPDATE users SET balance = balance + 2000, streak_toan = streak_toan + 1, xu_love = xu_love + 1 WHERE user_id = ?", (ctx.author.id,))
                        cursor.execute(
                            "SELECT streak_toan FROM users WHERE user_id = ?", (ctx.author.id,))
                        streak_toan = cursor.fetchone()[0]

                        embed.description = f"ㅤ\n# {butchi} {question} **{answer}**\nㅤ\n{dongho} **`0s`** | {hopqua} **`2k`** {list_emoji.pinkcoin}"
                        embed.color = discord.Color.from_rgb(0, 255, 0)
                        await ctx.send(f"{dung} **Wow, {ctx.author.mention} thông minh lắm! Bạn được thưởng 2k {list_emoji.pinkcoin}** | __**Streak**__ **{streak_toan}**")
                    else:
                        cursor.execute(
                            "UPDATE users SET balance = balance + 2000, streak_toan = streak_toan + 1 WHERE user_id = ?", (ctx.author.id,))
                        cursor.execute(
                            "SELECT streak_toan FROM users WHERE user_id = ?", (ctx.author.id,))
                        streak_toan = cursor.fetchone()[0]

                        embed.description = f"ㅤ\n# {butchi} {question} **{answer}**\nㅤ\n{dongho} **`0s`** | {hopqua} **`2k`** {list_emoji.pinkcoin}"
                        embed.color = discord.Color.from_rgb(0, 255, 0)
                        await ctx.send(f"{dung} **Wow, {ctx.author.mention} thông minh lắm! Bạn được thưởng 2k {list_emoji.pinkcoin}** | __**Streak**__ **{streak_toan}**")
                    if streak_toan % 10 == 0:
                        await ctx.send(f"{streak} **Quá xuất sắc, {ctx.author.mention} đạt streak** __**{streak_toan}**__")
                    # if streak_toan % 10 == 0:
                    #     bonus_amount = streak_toan * 1000 + 1000
                    #     cursor.execute(
                    #         "UPDATE users SET balance = balance + ? WHERE user_id = ?", (bonus_amount, ctx.author.id,))
                    #     await ctx.send(f"{streak} **Quá xuất sắc, {ctx.author.mention} đạt streak** __**{streak_toan}**__ **và được thưởng {bonus_amount} {list_emoji.pinkcoin}**")
                else:
                    cursor.execute(
                        "UPDATE users SET streak_toan = 0 WHERE user_id = ?", (ctx.author.id,))
                    embed.description = f"ㅤ\n# {butchi} {question} **{answer}**\nㅤ\n{dongho} **`0s`** | {hopqua} **`2k`** {list_emoji.pinkcoin}"
                    embed.color = discord.Color.from_rgb(255, 0, 0)
                    await ctx.send(f"{sai} **Uiii, {ctx.author.mention} không được thông minh lắm nhỉ**")
                conn.commit()
                await send.edit(embed=embed)
            except ValueError:
                await ctx.send("Vui lòng nhập một con số hợp lệ!")
        except asyncio.TimeoutError:
            cursor.execute(
                "UPDATE users SET streak_toan = 0 WHERE user_id = ?", (ctx.author.id,))
            conn.commit()
            await ctx.send(f"{sai} **Đã quá 10s, {ctx.author.mention} cần cố gắng nhiều hơn!**")
        conn.close()

    async def update_timer(self, ctx, send, question, timeout):
        # Lấy avatar của người dùng
        if ctx.author.avatar:
            avatar_url = ctx.author.avatar.url
        else:
            avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
        remaining = timeout

        # Cập nhật embed ngay lúc bắt đầu
        embed = discord.Embed(
            title=f"{maytinh} **LÀM TOÁN NHANH**",
            description=f"ㅤ\n# {butchi} {question} **?**\nㅤ\n{dongho} **`{remaining}s`** | {hopqua} **`2k`** {list_emoji.pinkcoin}",
            color=discord.Color.from_rgb(0, 255, 0)
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1211199649667616768/1271441774551896104/8042750.png")
        embed.set_footer(text=f"{ctx.author.name}", icon_url=avatar_url)
        try:
            await send.edit(embed=embed)
        except discord.HTTPException as e:
            print("Lỗi khi cập nhật embed ban đầu:", e)

        # Chỉ cập nhật mỗi khi thời gian còn lại <=5s hoặc chia hết cho 5 (với remaining > 5)
        while remaining > 0:
            if remaining <= 5 or remaining % 5 == 0:
                embed = discord.Embed(
                    title=f"{maytinh} **LÀM TOÁN NHANH**",
                    description=f"ㅤ\n# {butchi} {question} **?**\nㅤ\n{dongho} **`{remaining}s`** | {hopqua} **`2k`** {list_emoji.pinkcoin}",
                    color=discord.Color.from_rgb(0, 255, 0)
                )
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1211199649667616768/1271441774551896104/8042750.png")
                embed.set_footer(text=f"{ctx.author.name}", icon_url=avatar_url)
                try:
                    await send.edit(embed=embed)
                except discord.HTTPException as e:
                    print("Lỗi khi cập nhật embed:", e)
                    await asyncio.sleep(1)
            await asyncio.sleep(1)
            remaining -= 1

        # Sau khi hết giờ, cập nhật embed hiển thị "Hết giờ!"
        embed = discord.Embed(
            title=f"{maytinh} **LÀM TOÁN NHANH**",
            description=f"ㅤ\n# {butchi} {question} **?**\nㅤ\n{dongho} **`Hết giờ!`** | {hopqua} **`2k`** {list_emoji.pinkcoin}",
            color=discord.Color.from_rgb(255, 255, 0)
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1211199649667616768/1271441774551896104/8042750.png")
        embed.set_footer(text=f"{ctx.author.name}", icon_url=avatar_url)
        try:
            await send.edit(embed=embed)
        except discord.HTTPException as e:
            print("Lỗi khi cập nhật embed cuối cùng:", e)

    @mathquiz.error
    async def mathquiz_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            message = await ctx.send(f"Vui lòng đợi `{error.retry_after:.0f}s` trước khi sử dụng lệnh này!")
            await asyncio.sleep(2)
            await message.delete()
        elif isinstance(error, commands.CheckFailure):
            pass 
        else:
            raise error

async def setup(client):
    await client.add_cog(Lamtoan(client))