import asyncio
import typing
import discord
import random
import sqlite3
import datetime
from discord.ext import commands
from Commands.Mod.list_emoji import list_emoji, lambanh_emoji, profile_emoji, sinhnhat_emoji
from utils.checks import is_bot_owner, is_admin, is_mod

# Kết nối và tạo bảng trong SQLite
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

slots0 = '<a:slot_gif:1195041934750785676>'
slots1 = '<:slot1:1271305120495439882>'
slots2 = '<:slot2:1271305112111022162>'
slots3 = '<:slot3:1271305131115155486>'
slots4 = '<:slot4:1271305140649070664>'
slots5 = '<a:hgtt_vuongmieng:1253582309387407451>'
slots6 = '<a:hgtt_star2:1056247523007795320>'
tienhatgiong = "<:timcoin:1192458078294122526>"
dk = "<:profile:1181400074127945799>"

def is_allowed_channel_check():
    async def predicate(ctx):
        allowed_channel_ids = [993153068378116127, 1147355133622108262, 1152710848284991549, 1079170812709458031, 1207593935359320084, 1215331218124574740,1215331281878130738, 1051454917702848562, 1210296290026455140, 1210417888272318525, 1256198177246285825, 1050649044160094218, 1091208904920281098, 1238177759289806878, 1243264114483138600, 1251418765665505310, 1243440233685712906, 1237810926913323110, 1247072223861280768, 1270031327999164548, 1022533822031601766, 1065348266193063979, 1027622168181350400, 1072536912562241546, 1045395054954565652, 1273769137985818624,1273769188988682360, 1273769291099144222, 1026627301573677147, 1035183712582766673, 1090897131486842990, 1213122881802997770, 1104362707580375120]
        if ctx.channel.id in allowed_channel_ids:
            return False
        return True
    return commands.check(predicate)

class Slot(commands.Cog):
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

    async def get_slot_result(self):  
        emojis = [slots1, slots2, slots3, slots4, slots5, slots6]  
        weights = [70, 40, 10, 5, 2, 1]  
        result = random.choices(emojis, weights=weights, k=3)  

        if random.random() < 0.4:   
            chosen_slot = random.choices(emojis, weights=weights, k=1)[0]  
            result = [chosen_slot, chosen_slot, chosen_slot]  

        return result  

    async def display_slots(self, ctx, result, bet_amount, win_amount):
        emojis_default = [slots0, slots0, slots0]
        machine = f"**  `___SLOTS___`**\n` ` {' '.join(emojis_default)} ` ` **{ctx.author.display_name}** đặt cược {bet_amount:,} {list_emoji.pinkcoin}\n  `|         |`\n  `|         |`"
        message = await ctx.send(machine)
        await asyncio.sleep(1)
        # Hiển thị kết quả từng emoji một
        for i in range(3):
            await asyncio.sleep(1)  # Đợi một khoảng thời gian trước khi hiển thị emoji tiếp theo
            result_message = f"**  `___SLOTS___`**\n` ` {' '.join(result[:i+1] + [slots0] * (2-i))} ` ` **{ctx.author.display_name}** đặt cược {bet_amount:,} {list_emoji.pinkcoin}\n  `|         |`\n  `|         |`"
            await message.edit(content=result_message)
        
        if win_amount > 0:
            result_message = f"**  `___SLOTS___`**\n` ` {' '.join(result)} ` ` **{ctx.author.display_name}** đặt cược {bet_amount:,} {list_emoji.pinkcoin}\n  `|         |`   và **thắng** {win_amount:,} {list_emoji.pinkcoin}\n  `|         |`"
            await message.edit(content=result_message)
        else:
            result_message = f"**  `___SLOTS___`**\n` ` {' '.join(result)} ` ` **{ctx.author.display_name}** đặt cược {bet_amount:,} {list_emoji.pinkcoin}\n  `|         |`   và **thua** {bet_amount:,} {list_emoji.pinkcoin}\n  `|         |`"
            await message.edit(content=result_message)

    @commands.command(aliases=["sl"], description="Chơi trò chơi máy đánh bạc")
    @commands.cooldown(1, 20, commands.BucketType.user)
    @is_allowed_channel_check()
    async def slot(self, ctx, bet_amount: typing.Union[int, str] = 1):
        if await self.check_command_disabled(ctx):
            return
        if not is_registered(ctx.author.id):
            await ctx.send(f"{dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
            return
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (ctx.author.id,))
        result = cursor.fetchone()
        balance = result[2] if result[2] is not None else 0

        if balance == 0:
            await ctx.send("Còn ngàn bạc đâu mà chơi")
            return

        if bet_amount == "all":
            if balance >= 100000:
                bet_amount = 100000
            elif 0 < balance < 100000:
                bet_amount = balance
        else:
            try:
                bet_amount = int(bet_amount)
                if bet_amount > 100000:
                    await ctx.send("Bạn chỉ có thể đặt cược tối đa 100.000!")
                    return
            except ValueError:
                await ctx.send("Số tiền đặt cược không hợp lệ!")
                return
            
        if bet_amount < 0:
            await ctx.send("Số tiền đặt cược không hợp lệ!")
            return
        elif bet_amount > balance:
            await ctx.send("Bạn không đủ tiền cược!")
            return

        # Lấy kết quả từ hàm get_slot_result
        result = await self.get_slot_result()

        # Xác định giải thưởng dựa trên kết quả
        if result[0] == result[1] == result[2] == slots1:
            win_amount = bet_amount
        elif result[0] == result[1] == result[2] == slots2:
            win_amount = bet_amount * 2
        elif result[0] == result[1] == result[2] == slots3:
            win_amount = bet_amount * 3
        elif result[0] == result[1] == result[2] == slots4:
            win_amount = bet_amount * 4
        elif result[0] == result[1] == result[2] == slots5:
            win_amount = bet_amount * 5
        elif result[0] == result[1] == result[2] == slots6:
            win_amount = bet_amount * 10
        else:
            win_amount = 0
        # Cập nhật số dư của người chơi trong cơ sở dữ liệu
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ? AND balance >= ?", (win_amount - bet_amount, ctx.author.id, bet_amount))
        conn.commit()
        # Hiển thị kết quả trên máy đánh bạc
        await self.display_slots(ctx, result, bet_amount, win_amount)
    
    @slot.error
    async def slot_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            message = await ctx.send("Vui lòng nhập số tiền cược!")
            await asyncio.sleep(2)
            await message.delete()
        elif isinstance(error, commands.BadArgument):
            message = await ctx.send("Số tiền cược không hợp lệ!")
            await asyncio.sleep(2)
            await message.delete()
        elif isinstance(error, commands.CommandOnCooldown):
            message = await ctx.send(f"Vui lòng đợi `{error.retry_after:.0f}s` trước khi sử dụng lệnh này!")
            await asyncio.sleep(2)
            await message.delete()
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error

async def setup(client):
    await client.add_cog(Slot(client))