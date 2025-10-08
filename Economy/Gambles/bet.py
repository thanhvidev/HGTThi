import asyncio
import sqlite3
import discord
from discord.ext import commands, tasks
import random
from datetime import datetime, timedelta
import datetime
import pytz

# Kết nối và tạo bảng trong SQLite
conn = sqlite3.connect('economy.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS gamble (
               lottery INTEGER DEFAULT 0, 
               participants TEXT DEFAULT '',
               winner_id INTEGER DEFAULT 0,
               drop_pickupcobac INTEGER DEFAULT 0,
               drop_pickupowo1 INTEGER DEFAULT 0,
               drop_pickupowo2 INTEGER DEFAULT 0,
               drop_pickupowo3 INTEGER DEFAULT 0,
               drop_pickupowo4 INTEGER DEFAULT 0,
               drop_pickupsanh INTEGER DEFAULT 0,
               drop_pickuptalkshow INTEGER DEFAULT 0
               )''')

def is_allowed_channel():
    async def predicate(ctx):
        allowed_channel_id = 1204054397747990558  # ID của kênh văn bản cho phép
        if ctx.channel.id != allowed_channel_id:
            message = await ctx.send("Hãy dùng lệnh `zbet` ở kênh <#1204054397747990558>")
            await asyncio.sleep(2)
            await message.delete()
            await ctx.message.delete()
            return False
        return True
    return commands.check(predicate)

tienhatgiong = "<:timcoin:1192458078294122526>"
qua = "<a:hgtt_qua:1179913448600109066>"
thoigian = "<a:hgtt_timee:1159077258535907328>"
win = "<a:hgtt_qua:1024498010018828288>"
shiba = "<a:lottery:1297110769996922891>"
chay = "<a:hgtt_fire:1295137544215986206>"
owo = "<:hgtt_tienowo:1204791085327720448>"
winn = "<:ga:1263766055252398124>"
nhay = "<a:hgtt_flash:1079127237900640366>"
dauxdo = "<a:hgtt_check:1246910030444495008>"

def format_amount(num):
    if num >= 1000:
        return f'{num // 1000}K'
    return str(num)

class Bet(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.check_bet.start()

    def cog_unload(self):
        self.check_bet.cancel()

    async def check_command_disabled(self, ctx):  
        guild_id = str(ctx.guild.id)  
        command_name = ctx.command.name.lower()  
        if guild_id in self.client.get_cog('Toggle').toggles:  
            if command_name in self.client.get_cog('Toggle').toggles[guild_id]:  
                if ctx.channel.id in self.client.get_cog('Toggle').toggles[guild_id][command_name]:  
                    await ctx.send(f"Lệnh `{command_name}` đã bị tắt ở kênh này.")  
                    return True  
        return False 

    @tasks.loop(minutes=1)
    async def check_bet(self):
        timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        now = datetime.datetime.now(timezone)
        cursor.execute("SELECT * FROM gamble")
        gamble_data = cursor.fetchone()
        if now.hour == 15 and now.minute == 40:  # Nếu là 18:00
            participants = gamble_data[1].split(',') if gamble_data[1] else []
            if participants:
                winner_id = random.choice(participants)
                cursor.execute("UPDATE gamble SET winner_id = ?", (winner_id,))
                cursor.execute(f"UPDATE users SET balance = balance + {gamble_data[0]}, xu_hlw = xu_hlw + 10 WHERE user_id = {winner_id}")
                conn.commit()
                bot_avatar = self.client.user.avatar.url
                # embed = discord.Embed(title=f"{shiba} LOTTERY HGTT {shiba}",
                #     color=discord.Color.from_rgb(0, 245, 255))
                # embed.add_field(name="", value=f"- **Chúc mừng, bạn đã thắng giải thưởng lottery hôm nay với trị giá `{gamble_data[0]:,}` {tienhatgiong}**", inline=False)
                # embed.set_footer(icon_url=bot_avatar, text = "")
                winner_user = self.client.get_user(int(winner_id))
                # await winner_user.send(f"# {shiba} LOTTERY HGTT {shiba}\n**Chúc mừng, bạn đã thắng giải thưởng lottery hôm nay với trị giá** __**{gamble_data[0]:,}**__ {tienhatgiong}")
                tiengiai = gamble_data[0]
                format_tiengiai = format_amount(tiengiai)
                # embed1 = discord.Embed(title=f"{shiba} LOTTERY HGTT {shiba}",
                #     color=discord.Color.from_rgb(0, 245, 255), description=f"")
                # embed1.add_field(name="", value=f"- **Chúc mừng {winner_user.mention}, bạn đã thắng giải thưởng lottery hôm nay với trị giá `{tiengiai:,}` {tienhatgiong}**", inline=False)
                # embed1.set_footer(icon_url=bot_avatar, text = "")
                channel = self.client.get_channel(1204054397747990558)  # ID kênh log
                await channel.send(f"# {shiba} NGƯỜI MAY MẮN {shiba}\n{winn} **Chúc mừng {winner_user.mention}, bạn là người may mắn trúng giải thưởng hôm nay với tổng giá trị là** {nhay} __**{format_tiengiai} {tienhatgiong} + 500K {owo}**__ {nhay}")
                cursor.execute("UPDATE gamble SET lottery = 0, participants = '', winner_id = 0")
                conn.commit()

    @commands.command(aliases=["lottery"], description="Tham gia lottery (yêu cầu balance >= 50000)")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @is_allowed_channel()
    async def bet(self, ctx, bet_amount: int = 50000):
        if await self.check_command_disabled(ctx):
            return
        cursor.execute(f"SELECT balance, xu_hlw FROM users WHERE user_id = {ctx.author.id}")
        balance = cursor.fetchone()[0]
        now = datetime.datetime.utcnow() + timedelta(hours=7)
        reset_time = datetime.datetime(now.year, now.month, now.day,
                            18, 0) + timedelta(days=1)
        time_left = reset_time - now
        # Định dạng lại thời gian còn lại
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_left_str = f"{hours}h{minutes}m{seconds}s"

        if balance < bet_amount:
            msg1 = await ctx.send(f"**Bạn cần có {bet_amount:,} để tham gia lottery!**")
            await asyncio.sleep(5)
            await ctx.message.delete()
            await msg1.delete()
            return
        if bet_amount < 50000:
            msg2 = await ctx.send("**Số tiền cược tối thiểu là 50000!**")
            await asyncio.sleep(5)
            await ctx.message.delete()
            await msg2.delete()
            return

        cursor.execute(f"SELECT * FROM gamble")
        gamble_data = cursor.fetchone()
        if gamble_data is None:
            participants = [] 
        else:
            participants = gamble_data[1].split(',') if gamble_data[1] else []
        if str(ctx.author.id) in participants:
            msg = await ctx.send("Bạn đã tham gia lottery rồi!")
            await asyncio.sleep(5)
            await ctx.message.delete()
            await msg.delete()
            return
        cursor.execute(f"UPDATE users SET balance = balance - {bet_amount} WHERE user_id = {ctx.author.id}")
        cursor.execute(f"UPDATE gamble SET lottery = {gamble_data[0] + bet_amount}, participants = '{','.join(participants + [str(ctx.author.id)])}'")
        conn.commit()

        embed = discord.Embed(title=f"**{chay} Người may mắn {chay}**",
            color=discord.Color.from_rgb(255, 69, 0))
        # if ctx.author.avatar:
        #     avatar_url = ctx.author.avatar.url
        # else:
        #     avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"  
        # embed.set_author(name=f"LOTTERY HGTT", icon_url=avatar_url)
        tiengiai = gamble_data[0] + bet_amount
        format_tiengiai = format_amount(tiengiai)
        format_amounts = format_amount(bet_amount)
        embed.add_field(name="", value=f"- **{ctx.author.mention} bet `{format_amounts}` {tienhatgiong} để tham gia. Đón xem kết quả vào lúc 18h chiều nay để biết bạn có phải là người được chọn hay không nhé!**\n- **Tổng giải thưởng: `{format_tiengiai}` {tienhatgiong} + `500K` {owo}**\n- {thoigian} **Đếm ngược: `{time_left_str}`**", inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1053799649938505889/1297117972179189791/466568f7f2856c4f9cf9494ef805534f.gif")
        await ctx.send(embed=embed)

    @bet.error
    async def bet_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            message = await ctx.send(f"{dauxdo} | Bạn đã bet rồi!!")
            await asyncio.sleep(2)
            await message.delete()
            await ctx.message.delete()
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error

async def setup(client):
    await client.add_cog(Bet(client))