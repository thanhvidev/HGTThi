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

emoji_start = '<a:danglac:1090171480639275008>'
emoji = [
    {'key': '<:xx1:1329249708463493181>', 'number': 1},
    {'key': '<:xx2:1329249718068445194>', 'number': 2},
    {'key': '<:xx3:1329249726515646475>', 'number': 3},
    {'key': '<:xx4:1329249737786003611>', 'number': 4},
    {'key': '<:xx5:1329249746614751253>', 'number': 5},
    {'key': '<:xx6:1329249756161249302>', 'number': 6}
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

class Taixiu(commands.Cog):
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

    async def get_taixiu_result(self):
        result = [random.choice(emoji) for _ in range(3)]
        if random.random() < 0.05:  
            result[0] = result[1] = result[2] = random.choice(emoji)
        return result
    
    async def display_taixiu(self, ctx, result, bet_amount, win_amount, choice):
        if choice == "x":
            choice = "xỉu"
        elif choice == "t":
            choice = "tài"
        elif choice == "hủ":
            choice = "hũ"
        elif choice == "c":
            choice = "chẵn"
        elif choice == "l":
            choice = "lẻ"
        else:
            choice = choice.lower()
        emojis_default = [emoji_start, emoji_start, emoji_start]
        machine = f"**  `___TAIXIU___`**\n` ` {' '.join(emojis_default)} ` ` **{ctx.author.display_name}** đặt cược **{choice}**  {bet_amount:,} {list_emoji.pinkcoin}\n  `|         |`\n  `|         |`"
        message = await ctx.send(machine)
        await asyncio.sleep(1)
        for i in range(3):
            await asyncio.sleep(1)  
            emoji_to_display = [emoji_start] * 3
            for j in range(i + 1):
                emoji_to_display[j] = result[j]['key']

            result_message = f"**  `___TAIXIU___`**\n` ` {' '.join(emoji_to_display)} ` ` **{ctx.author.display_name}** đặt cược **{choice}**  {bet_amount:,} {list_emoji.pinkcoin}\n  `|         |`\n  `|         |`"
            await message.edit(content=result_message)

        # Tính tổng số điểm của 3 con xúc xắc
        total_dice_number = sum(emoji['number'] for emoji in result)

        # Xác định kết quả của cuộc chơi
        if total_dice_number == 3 or total_dice_number == 18:
            result_text = "Hũ"
        elif total_dice_number >= 4 and total_dice_number <= 10:
            result_text = "Xỉu"
        else:
            result_text = "Tài"
        if total_dice_number % 2 == 0 and total_dice_number != 3 and total_dice_number != 18:
            result_text += " - Chẵn"
        else:
            result_text += " - Lẻ"

        if win_amount > 0:
            result_message = f"**  `___TAIXIU___`**\n` ` {' '.join([result[i]['key'] for i in range(3)])} ` ` **{ctx.author.display_name}** đặt cược **{choice}**  {bet_amount:,} {list_emoji.pinkcoin}\n  `|         |`    Kết quả: **{total_dice_number} - {result_text}**\n  `|         |`    bạn **thắng** {win_amount:,} {list_emoji.pinkcoin}"
        else:
            result_message = f"**  `___TAIXIU___`**\n` ` {' '.join([result[i]['key'] for i in range(3)])} ` ` {ctx.author.display_name} đặt cược **{choice}**  {bet_amount:,} {list_emoji.pinkcoin}\n  `|         |`    Kết quả: **{total_dice_number} - {result_text}**\n  `|         |`    bạn **thua** {bet_amount:,} {list_emoji.pinkcoin}"

        await message.edit(content=result_message)

    @commands.command(aliases=['tx'])
    @commands.cooldown(1, 20, commands.BucketType.user)
    @is_allowed_channel_check()
    async def taixiu(self, ctx, bet_amount: typing.Union[int, str] = 1, choice: str = None):
        if await self.check_command_disabled(ctx):
            return
        if not is_registered(ctx.author.id):
            await ctx.send(f"{dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
            return
        valid_choices = {'t': 'tài', 'x': 'xỉu', 'hũ': 'hủ', 'tài': 't', 'xỉu': 'x', 'hủ': 'hũ', 'c': 'chẵn', 'l': 'lẻ', 'chẵn': 'c', 'lẻ': 'l'}
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
                await ctx.send("ztx (số tiền) (t/x/hủ)")
                return
            
        if bet_amount < 0:
            await ctx.send("ztx (số tiền) (t/x/hủ)")
            return
        elif bet_amount > balance:
            await ctx.send("Bạn không đủ tiền cược!")
            return
        
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (bet_amount, ctx.author.id))
        conn.commit()

        result = await self.get_taixiu_result()
        total_number = sum(emoji['number'] for emoji in result)

        win_amount = 0

        if (total_number == 3 or total_number == 18) and (choice in valid_choices.values() and (valid_choices[choice] == "hủ" or valid_choices[choice] == "hũ")):
            win_amount = bet_amount * 9
        elif total_number >= 4 and total_number <= 10 and (choice in valid_choices.values() and (valid_choices[choice] == "xỉu" or valid_choices[choice] == "x")):
            win_amount = bet_amount
        elif total_number >= 11 and total_number <= 17 and (choice in valid_choices.values() and (valid_choices[choice] == "tài" or valid_choices[choice] == "t")):
            win_amount = bet_amount
        elif total_number % 2 == 0 and (choice in valid_choices.values() and (valid_choices[choice] == "chẵn" or valid_choices[choice] == "c")):
            win_amount = bet_amount
        elif total_number % 2 != 0 and (choice in valid_choices.values() and (valid_choices[choice] == "lẻ" or valid_choices[choice] == "l")):
            win_amount = bet_amount
        else:
            win_amount = 0 - bet_amount

        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (win_amount + bet_amount, ctx.author.id))
        conn.commit()

        await self.display_taixiu(ctx, result, bet_amount, win_amount, choice)

    @taixiu.error
    async def taixiu_error(self, ctx, error):
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
    await client.add_cog(Taixiu(client))