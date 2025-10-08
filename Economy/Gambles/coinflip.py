import asyncio
import json
import typing
import discord
import random
import sqlite3
import datetime
from discord.ext import commands
from Commands.Mod.list_emoji import list_emoji, lambanh_emoji, profile_emoji, sinhnhat_emoji
from utils.checks import is_bot_owner, is_admin, is_mod

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

def is_allowed_channel_check():
    async def predicate(ctx):
        allowed_channel_ids = [993153068378116127, 1147355133622108262, 1152710848284991549, 1079170812709458031, 1207593935359320084, 1215331218124574740,1215331281878130738, 1051454917702848562, 1210296290026455140, 1210417888272318525, 1256198177246285825, 1050649044160094218, 1091208904920281098, 1238177759289806878, 1243264114483138600, 1251418765665505310, 1243440233685712906, 1237810926913323110, 1247072223861280768, 1270031327999164548, 1022533822031601766, 1065348266193063979, 1027622168181350400, 1072536912562241546, 1045395054954565652, 1273769137985818624,1273769188988682360, 1273769291099144222, 1026627301573677147, 1035183712582766673, 1090897131486842990, 1213122881802997770, 1104362707580375120]
        if ctx.channel.id in allowed_channel_ids:
            return False
        return True
    return commands.check(predicate)

emojicoin = '<a:owoflipcoin:1193899894302318673>'
emojicoin1 = '<:owocoin:1193900263132635206>'
tienhatgiong = "<:timcoin:1192458078294122526>"
dk = "<:profile:1181400074127945799>"

class Coinflip(commands.Cog):
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

    @commands.command(aliases=['cf'])
    @commands.cooldown(1, 20, commands.BucketType.user)
    @is_allowed_channel_check()
    async def coinflip(self, ctx, bet_amount: typing.Union[int, str] = 1, choice: str = None):
        if await self.check_command_disabled(ctx):
            return
        if not is_registered(ctx.author.id):
            await ctx.send(f"{dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
            return

        valid_choices = {'s': 'sấp', 'n': 'ngửa'}
        
        if choice and choice.lower() not in valid_choices.keys():
            await ctx.send(f"Vui lòng chọn mặt đồng xu hợp lệ: {', '.join(valid_choices.keys())}!")
            return
        elif not choice:
            choice = random.choice(list(valid_choices.keys()))
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
        
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (bet_amount, ctx.author.id))
        conn.commit()
        message = await ctx.send(f"> **{ctx.author.display_name}** đã cược __**{bet_amount:,}**__ {list_emoji.pinkcoin} và chọn mặt **`{valid_choices[choice.lower()]}`**\n> Tung đồng xu {emojicoin}...")
        await asyncio.sleep(2)
        winnings = bet_amount + bet_amount
        # Random kết quả và thông báo cho người dùng
        result_coinflip = random.choice(list(valid_choices.keys()))
        if result_coinflip == choice.lower():
            cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (winnings, ctx.author.id))
            conn.commit()
            await message.edit(content=f"> **{ctx.author.display_name}** đã cược __**{bet_amount:,}**__ {list_emoji.pinkcoin} và chọn mặt **`{valid_choices[choice.lower()]}`**\n> Tung đồng xu {emojicoin1}...ra mặt **`{valid_choices[result_coinflip]}`**, **bạn thắng** __**{bet_amount:,}**__ {list_emoji.pinkcoin}")
        else:
            await message.edit(content=f"> **{ctx.author.display_name}** đã cược __**{bet_amount:,}**__ {list_emoji.pinkcoin} và chọn mặt **`{valid_choices[choice.lower()]}`**\n> Tung đồng xu {emojicoin1}...ra mặt **`{valid_choices[result_coinflip]}`**, **bạn thua** __**{bet_amount:,}**__ {list_emoji.pinkcoin}")

    @coinflip.error
    async def coinflip_error(self, ctx, error):
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
    await client.add_cog(Coinflip(client))