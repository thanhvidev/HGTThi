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

emoji_start = '<a:hgtt_lac:1090551045823922240>'
emoji = [
    {'key': '<:bc_bau:1419189459643011084>', 'number': 1},
    {'key': '<a:bc_cua:1419189452152242268>', 'number': 2},
    {'key': '<a:bc_tom:1419189701256024094>', 'number': 3},
    {'key': '<:bc_ca:1419189468220489739>', 'number': 4},
    {'key': '<a:bc_ga:1419189438029762611>', 'number': 5},
    {'key': '<:bc_nai:1419189422364295299>', 'number': 6}
]
tienhatgiong = "<:timcoin:1192458078294122526>"
dk = "<:profile:1181400074127945799>"

def is_allowed_channel_check():
    async def predicate(ctx):
        allowed_channel_ids = [993153068378116127, 1147355133622108262, 1152710848284991549, 1079170812709458031, 1207593935359320084, 1215331218124574740,1215331281878130738, 1051454917702848562, 1210296290026455140, 1210417888272318525, 1256198177246285825, 1050649044160094218, 1091208904920281098, 1238177759289806878, 1243264114483138600, 1251418765665505310, 1243440233685712906, 1237810926913323110, 1247072223861280768, 1270031327999164548, 1022533822031601766, 1065348266193063979, 1027622168181350400, 1072536912562241546, 1045395054954565652, 1273769137985818624,1273769188988682360, 1273769291099144222, 1026627301573677147, 1035183712582766673, 1090897131486842990, 1213122881802997770, 1104362707580375120]
        if ctx.channel.id in allowed_channel_ids:
            return False
        return True
    return commands.check(predicate)

class Baucua(commands.Cog):
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

    async def get_baucua_result(self):
        result = [random.choice(emoji) for _ in range(3)]
        if random.random() < 0.2:  
            result[0] = result[1] = result[2] = random.choice(emoji)
        return result
    
    async def display_baucua(self, ctx, result, bet_amount, win_amount, choice):
        if choice == "b":
            choice = "bầu"
        elif choice == "cu":
            choice = "cua"
        elif choice == "t":
            choice = "tôm"
        elif choice == "c":
            choice = "cá"
        elif choice == "g":
            choice = "gà"
        elif choice == "n":
            choice = "nai"
        else:
            choice = choice.lower()
        emojis_default = [emoji_start, emoji_start, emoji_start]
        machine = f"**  `___BAUCUA___`**\n` ` {' '.join(emojis_default)} ` ` **{ctx.author.display_name}** đặt cược **{choice}**  {bet_amount:,} {list_emoji.pinkcoin}\n  `|         |`\n  `|         |`"
        message = await ctx.send(machine)
        await asyncio.sleep(1)
        for i in range(3):
            await asyncio.sleep(1)  
            emoji_to_display = [emoji_start] * 3
            for j in range(i + 1):
                emoji_to_display[j] = result[j]['key']

            result_message = f"**  `___BAUCUA___`**\n` ` {' '.join(emoji_to_display)} ` ` **{ctx.author.display_name}** đặt cược **{choice}**  {bet_amount:,} {list_emoji.pinkcoin}\n  `|         |`\n  `|         |`"
            await message.edit(content=result_message)

        result_numbers = [emoji['number'] for emoji in result]
        text_list = []
        for number in result_numbers:
            if number == 1:
                text_list.append("bầu")
            elif number == 2:
                text_list.append("cua")
            elif number == 3:
                text_list.append("tôm")
            elif number == 4:
                text_list.append("cá")
            elif number == 5:
                text_list.append("gà")
            elif number == 6:
                text_list.append("nai")
            else:
                text_list.append(str(number))

        text = " - ".join(text_list)

        if win_amount > 0:
            result_message = f"**  `___BAUCUA___`**\n` ` {' '.join(emoji_to_display)} ` ` **{ctx.author.display_name}** đặt cược **{choice}**  {bet_amount:,} {list_emoji.pinkcoin}\n  `|         |`     Kết quả: **{text}**\n  `|         |`     bạn **thắng** {win_amount:,} {list_emoji.pinkcoin}"
            await message.edit(content=result_message)
        else:
            result_message = f"**  `___BAUCUA___`**\n` ` {' '.join(emoji_to_display)} ` ` **{ctx.author.display_name}** đặt cược **{choice}**  {bet_amount:,} {list_emoji.pinkcoin}\n  `|         |`     Kết quả: **{text}**\n  `|         |`     bạn **thua** {bet_amount:,} {list_emoji.pinkcoin}"
            await message.edit(content=result_message)

    @commands.command(aliases=['bc'])
    @commands.cooldown(1, 20, commands.BucketType.user)
    @is_allowed_channel_check()
    async def baucua(self, ctx, bet_amount: typing.Union[int, str] = 1, choice: str = None):
        if await self.check_command_disabled(ctx):
            return
        if not is_registered(ctx.author.id):
            await ctx.send(f"{dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
            return
        
        valid_choices = {'b': 'bầu', 'cu': 'cua', 't': 'tôm', 'c': 'cá', 'g': 'gà', 'n': 'nai', 
                         'bầu': 'b', 'cua': 'cu', 'tôm': 't', 'cá': 'c', 'gà': 'g', 'nai': 'n'
                        }
        
        if choice and choice.lower() not in valid_choices.keys():
            await ctx.send(f"Vui lòng chọn: {', '.join(valid_choices.keys())}!")
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

        result = await self.get_baucua_result()

        total_appearance = sum(1 for dice in result if dice['number'] == 1 and (valid_choices[choice] == 'bầu' or valid_choices[choice] == 'b'))
        total_appearance += sum(1 for dice in result if dice['number'] == 2 and (valid_choices[choice] == 'cua' or valid_choices[choice] == 'cu'))
        total_appearance += sum(1 for dice in result if dice['number'] == 3 and (valid_choices[choice] == 'tôm' or valid_choices[choice] == 't'))
        total_appearance += sum(1 for dice in result if dice['number'] == 4 and (valid_choices[choice] == 'cá' or valid_choices[choice] == 'c'))
        total_appearance += sum(1 for dice in result if dice['number'] == 5 and (valid_choices[choice] == 'gà' or valid_choices[choice] == 'g'))
        total_appearance += sum(1 for dice in result if dice['number'] == 6 and (valid_choices[choice] == 'nai' or valid_choices[choice] == 'n'))

        if total_appearance > 0:
            win_amount = bet_amount * total_appearance
        else:
            win_amount = 0 - bet_amount

        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (win_amount + bet_amount, ctx.author.id))
        conn.commit()

        await self.display_baucua(ctx, result, bet_amount, win_amount, choice)

    @baucua.error
    async def baucua_error(self, ctx, error):
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
    await client.add_cog(Baucua(client))