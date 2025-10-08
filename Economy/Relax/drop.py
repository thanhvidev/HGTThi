import asyncio
import sqlite3
import discord
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

def is_guild_owner_or_bot_owner():
    async def predicate(ctx):
        return ctx.author == ctx.guild.owner or ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222
    return commands.check(predicate)

chamthan = "<:roles:1222819473237479534>"
tienhatgiong = "<:timcoin:1192458078294122526>"
canhbao = "<:chamthann:1233135104281411757>"
lumtien = "<a:drop2:1424366096986935467>"
thatien = "<a:drop1:1424366095128596551>"
thathemtien = "<a:drop3:1424366098568056842>"
lum1 = "<a:drop4:1424366107921219614>"
lum2 = "<a:drop5:1424366116066693283>"

class DropPickup(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command( description="Rơi tiền ra đường")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def drop(self, ctx, amount: int = None):
        if ctx.channel.id not in [1193936442045505546, 1026627301573677147, 1035183712582766673, 1090897131486842990, 1213122881802997770, 993153068378116127, 1079170812709458031]:
            return None
        if not is_registered(ctx.author.id):
            await ctx.send(f"{chamthan} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` tại kênh <#1147355133622108262> để đăng kí")
            return           
        user_id = ctx.author.id
        conn = get_database_connection()
        cursor = conn.cursor()
        # Kiểm tra balance của người dùng
        cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
        user_balance = cursor.fetchone()[0]

        if amount is None:
            message0 = await ctx.send("Vui lòng nhập số tiền bạn muốn đánh rơi.")
            await asyncio.sleep(2)
            await message0.delete()
            return

        if amount <= 0 or amount > user_balance:
            message2 = await ctx.send("Có đủ tiền đâu mà bày đặt drop?")
            await asyncio.sleep(2)
            await message2.delete()            
            return
        
        if ctx.channel.id == 1193936442045505546:
            cursor.execute("UPDATE gamble SET drop_pickupcobac = drop_pickupcobac + ?;", (amount,))
        elif ctx.channel.id == 1026627301573677147:
            cursor.execute("UPDATE gamble SET drop_pickupowo1 = drop_pickupowo1 + ?;", (amount,))
        elif ctx.channel.id == 1035183712582766673:
            cursor.execute("UPDATE gamble SET drop_pickupowo2 = drop_pickupowo2 + ?;", (amount,))
        elif ctx.channel.id == 1090897131486842990:
            cursor.execute("UPDATE gamble SET drop_pickupowo3 = drop_pickupowo3 + ?;", (amount,))
        elif ctx.channel.id == 1213122881802997770:
            cursor.execute("UPDATE gamble SET drop_pickupowo4 = drop_pickupowo4 + ?;", (amount,))
        elif ctx.channel.id == 993153068378116127:
            cursor.execute("UPDATE gamble SET drop_pickupsanh = drop_pickupsanh + ?;", (amount,))
        elif ctx.channel.id == 1079170812709458031:
            cursor.execute("UPDATE gamble SET drop_pickuptalkshow = drop_pickuptalkshow + ?;", (amount,)) 
        conn.commit()
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id=?;", (amount, user_id))
        conn.commit()
        await ctx.send(f"# {thatien} | {ctx.author.display_name} đã thả __{amount:,}__ {list_emoji.pinkcoin} xuống sàn {ctx.channel.name} {thatien}")

    @drop.error
    async def drop_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            message = await ctx.send("Vui lòng nhập số tiền đánh rơi")
            await asyncio.sleep(2)
            await message.delete()
        elif isinstance(error, commands.BadArgument):
            message = await ctx.send("Số tiền đánh rơi không hợp lệ!")
            await asyncio.sleep(2)
            await message.delete()
        elif isinstance(error, commands.CommandOnCooldown):
            message = await ctx.send(f"{canhbao} Còn `{error.retry_after:.0f}s` để thực hiện lệnh này")
            await asyncio.sleep(2)
            await message.delete()
        else:
            raise error

    @commands.command(description="Nhặt tiền từ người khác làm rơi")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def lum(self, ctx, amount: int = None):
        if ctx.channel.id not in [1193936442045505546, 1026627301573677147, 1035183712582766673, 1090897131486842990, 1213122881802997770, 993153068378116127, 1079170812709458031]:
            return None
        if not is_registered(ctx.author.id):
            await ctx.send(f"{chamthan} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` tại kênh <#1147355133622108262> để đăng kí")
            return            
        user_id = ctx.author.id
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
        user_balance = cursor.fetchone()[0]  # Di chuyển việc lấy balance lên đây

        # Lấy số lượng drop_pickup của người dùng
        cursor.execute("SELECT drop_pickupcobac, drop_pickupowo1, drop_pickupowo2, drop_pickupowo3, drop_pickupowo4, drop_pickupsanh, drop_pickuptalkshow FROM gamble")
        drop_pickup = cursor.fetchone()
        if ctx.channel.id == 1193936442045505546:
            drop_pickup = drop_pickup[0]
        elif ctx.channel.id == 1026627301573677147:
            drop_pickup = drop_pickup[1]
        elif ctx.channel.id == 1035183712582766673:
            drop_pickup = drop_pickup[2]
        elif ctx.channel.id == 1090897131486842990:
            drop_pickup = drop_pickup[3]
        elif ctx.channel.id == 1213122881802997770:
            drop_pickup = drop_pickup[4]
        elif ctx.channel.id == 993153068378116127:
            drop_pickup = drop_pickup[5]
        elif ctx.channel.id == 1079170812709458031:
            drop_pickup = drop_pickup[6]

        if amount is None:
            message8 = await ctx.send("Vui lòng nhập số tiền bạn muốn nhặt.")
            await asyncio.sleep(2)
            await message8.delete()
            return
        
        if amount <= drop_pickup:
            # Cộng tiền vào balance của người dùng và trừ amount từ drop_pickup của bảng gamble
            if ctx.channel.id == 1193936442045505546:
                cursor.execute("UPDATE gamble SET drop_pickupcobac = drop_pickupcobac - ?;", (amount,))
            elif ctx.channel.id == 1026627301573677147:
                cursor.execute("UPDATE gamble SET drop_pickupowo1 = drop_pickupowo1 - ?;", (amount,))
            elif ctx.channel.id == 1035183712582766673:
                cursor.execute("UPDATE gamble SET drop_pickupowo2 = drop_pickupowo2 - ?;", (amount,))
            elif ctx.channel.id == 1090897131486842990:
                cursor.execute("UPDATE gamble SET drop_pickupowo3 = drop_pickupowo3 - ?;", (amount,))
            elif ctx.channel.id == 1213122881802997770:
                cursor.execute("UPDATE gamble SET drop_pickupowo4 = drop_pickupowo4 - ?;", (amount,))
            elif ctx.channel.id == 993153068378116127:
                cursor.execute("UPDATE gamble SET drop_pickupsanh = drop_pickupsanh - ?;", (amount,))
            elif ctx.channel.id == 1079170812709458031:
                cursor.execute("UPDATE gamble SET drop_pickuptalkshow = drop_pickuptalkshow - ?;", (amount,))
            conn.commit()
            cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id=?;", (amount, user_id))
            conn.commit()
            await ctx.send(f"**{lumtien} | {ctx.author.display_name}** may mắn lụm được __**{amount:,}**__ {list_emoji.pinkcoin} ai đó làm rớt {lum1}")
        # elif drop_pickup > user_balance:
        #     message1 = await ctx.send(f"**{canhbao} | {ctx.author.display_name}**, bạn phải có tương đương số tiền thì mới lụm được!")
        #     await asyncio.sleep(3)
        #     await message1.delete()
        #     return
        else:
            if user_balance < amount:
                message1 = await ctx.send(f"**{canhbao} | {ctx.author.display_name}**, bạn phải có tương đương số tiền thì mới lụm được!")
                await asyncio.sleep(3)
                await message1.delete()
            else:
                # Cộng tiền vào drop_pickup của bảng gamble và trừ amount từ balance của người dùng
                if ctx.channel.id == 1193936442045505546:
                    cursor.execute("UPDATE gamble SET drop_pickupcobac = drop_pickupcobac + ?;", (amount,))
                elif ctx.channel.id == 1026627301573677147:
                    cursor.execute("UPDATE gamble SET drop_pickupowo1 = drop_pickupowo1 + ?;", (amount,))
                elif ctx.channel.id == 1035183712582766673:
                    cursor.execute("UPDATE gamble SET drop_pickupowo2 = drop_pickupowo2 + ?;", (amount,))
                elif ctx.channel.id == 1090897131486842990:
                    cursor.execute("UPDATE gamble SET drop_pickupowo3 = drop_pickupowo3 + ?;", (amount,))
                elif ctx.channel.id == 1213122881802997770:
                    cursor.execute("UPDATE gamble SET drop_pickupowo4 = drop_pickupowo4 + ?;", (amount,))
                elif ctx.channel.id == 993153068378116127:
                    cursor.execute("UPDATE gamble SET drop_pickupsanh = drop_pickupsanh + ?;", (amount,))
                elif ctx.channel.id == 1079170812709458031:
                    cursor.execute("UPDATE gamble SET drop_pickuptalkshow = drop_pickuptalkshow + ?;", (amount,))
                conn.commit()
                cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id=?;", (amount, user_id))
                conn.commit()
                await ctx.send(f"{thathemtien} | **{ctx.author.display_name}** chơi ngu nên làm rớt __**{amount:,}**__ {list_emoji.pinkcoin} xuống sàn {lum2}")

    @lum.error
    async def lum_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            message = await ctx.send("Vui lòng nhập số tiền nhặt")
            await asyncio.sleep(2)
            await message.delete()
        elif isinstance(error, commands.BadArgument):
            message = await ctx.send("Số tiền nhặt không hợp lệ!")
            await asyncio.sleep(2)
            await message.delete()
        elif isinstance(error, commands.CommandOnCooldown):
            message = await ctx.send(f"{canhbao} Còn `{error.retry_after:.0f}s` để thực hiện lệnh này")
            await asyncio.sleep(2)
            await message.delete()
        else:
            raise error
        
    @commands.command( description="Xem số tiền đang rơi")
    @is_bot_owner()
    async def dropcash(self, ctx):
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT drop_pickupcobac, drop_pickupowo1, drop_pickupowo2, drop_pickupowo3, drop_pickupowo4, drop_pickupsanh, drop_pickuptalkshow FROM gamble")
        drop_pickup = cursor.fetchone()
        drop_pickupcobac = drop_pickup[0]
        drop_pickupowo1 = drop_pickup[1]
        drop_pickupowo2 = drop_pickup[2]
        drop_pickupowo3 = drop_pickup[3]
        drop_pickupowo4 = drop_pickup[4]
        drop_pickupsanh = drop_pickup[5]
        drop_pickuptalkshow = drop_pickup[6]
        embed = discord.Embed(title="Số tiền đang rơi", color=discord.Color.from_rgb(0, 245, 255))
        embed.add_field(name="Cobac", value=f"Cobac: __**{drop_pickupcobac:,}**__ {list_emoji.pinkcoin}\nOwo1: __**{drop_pickupowo1:,}**__ {list_emoji.pinkcoin}\nOwo2: __**{drop_pickupowo2:,}**__ {list_emoji.pinkcoin}\nOwo3: __**{drop_pickupowo3:,}**__ {list_emoji.pinkcoin}\nOwo4: __**{drop_pickupowo4:,}**__ {list_emoji.pinkcoin}\nSanh:  __**{drop_pickupsanh:,}**__ {list_emoji.pinkcoin}\nTalkshow: __**{drop_pickuptalkshow:,}**__ {list_emoji.pinkcoin}", inline=False)
        await ctx.send(embed=embed)
    
async def setup(client):
    await client.add_cog(DropPickup(client))