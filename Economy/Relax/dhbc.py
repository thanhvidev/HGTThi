import asyncio
import sqlite3
import discord
from discord.ext import commands
import json
import random

import easy_pil
import requests
from Economy.Relax.cache.list_color import list_color
import os
from Commands.Mod.list_emoji import list_emoji, lambanh_emoji, profile_emoji, sinhnhat_emoji
from utils.checks import is_bot_owner, is_admin, is_mod

# Kết nối tới cơ sở dữ liệu SQLite
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
        allowed_channel_ids = [993153068378116127, 1147355133622108262, 1152710848284991549, 1079170812709458031, 1207593935359320084, 1215331218124574740, 1215331281878130738, 1051454917702848562, 1210296290026455140, 1210417888272318525, 1256198177246285825, 1050649044160094218, 1091208904920281098, 1238177759289806878, 1243264114483138600, 1251418765665505310, 1243440233685712906, 1237810926913323110, 1247072223861280768, 1270031327999164548, 1022533822031601766, 1065348266193063979, 1027622168181350400, 1072536912562241546, 1045395054954565652, 1273768834830041301, 1273768884882326, 1273769291099144222, 1026627301573677147, 1035183712582766673, 1090897131486842990, 1213122881802997770, 1104362707580375120]
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

# Emoji được sử dụng
maytinh = "<:buttim:1271289982220369984>"
dongho = "<:dongho_giaitri:1419189478882541678>"
hopqua = "<:dhbc_hopqua:1419189489460580498>"
pinkcoin = "<:timcoin:1192458078294122526>"
dung = "<:huychuong:1271289997231788032>"
dk = "<:profile:1181400074127945799>"
votay = "<a:votay:1271305102011138048>"
sai = "<:sai:1271305088350027853>"

class Dhbc(commands.Cog):
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

    @commands.hybrid_command(aliases=["dhbc"], description="Trò chơi vua tiếng việt")  
    # @is_allowed_channel_check()
    @is_allowed_channel()
    @commands.cooldown(1, 30, commands.BucketType.user)  
    async def duoihinhbatchu(self, ctx):
        if ctx.author.avatar:
            avatar_url = ctx.author.avatar.url
        else:
            avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
        if await self.check_command_disabled(ctx):
            return
        if not is_registered(ctx.author.id):  
            await ctx.send(f"{dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")  
            return  
        await ctx.defer()  
        conn = get_database_connection()
        cursor = conn.cursor()
        try:
            # Lấy dữ liệu từ API
            api_keys = ['T3OiUYEB', 'puHH3Bfj', 'Y7ULVSgD', 'TMy7LOH9', 'cfLqZUJb', 'Rf9Uph9i', 'dyi8v9DG', 'gGF25UxX', 'bwk3gmNa', 'BVLdIpEN', 'aMvGNmpv']
            selected_key = random.choice(api_keys)  
            get_DHBC = requests.get(f'https://nguyenmanh.name.vn/api/dhbcemoji?apikey={selected_key}')  
            data_DHBC = get_DHBC.text  
            json_DHBC = json.loads(data_DHBC)  

            emoji1 = json_DHBC['result']['emoji1']  
            emoji2 = json_DHBC['result']['emoji2']  
            dapan = json_DHBC['result']['wordcomplete']  
            embed = discord.Embed(  
                title=f"{maytinh} **ĐUỔI HÌNH BẮT CHỮ**",  
                description=f"ㅤ\n# {emoji1}{emoji2}\nㅤ\n{dongho} **`15s`** | {hopqua} **`2k`** {list_emoji.pinkcoin}",  
                color=discord.Color.from_rgb(216, 82, 255)  
            )
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1211199649667616768/1271283119063961630/1200px-Logo_uoi_hinh_bat_chu_sieu_toc2.jpg")
            embed.set_footer(text=f"{ctx.author.name}", icon_url=avatar_url)  
            send = await ctx.send(embed=embed)  

            def check(m):  
                return (  
                    m.author.id == ctx.author.id  
                    and m.channel == ctx.channel  
                    and m.reference is not None  
                    and m.reference.message_id == send.id  
                )  

            timeout = 20  
            # Khởi tạo task cập nhật đồng hồ
            timer_task = asyncio.create_task(self.update_timer(ctx, send, emoji1, emoji2, timeout))  

            try:  
                message = await self.client.wait_for("message", timeout=timeout, check=check)  
                timer_task.cancel()  
                if message:  
                    if str(message.content.lower()) == str(dapan).lower():
                        if discord.utils.get(ctx.author.roles, id=1339482195907186770):  
                            cursor.execute("UPDATE users SET balance = balance + 2000 WHERE user_id = ?", (ctx.author.id,))  
                            embed.description = f"ㅤ\n# {emoji1}{emoji2}\nㅤ\n{dongho} **`0s`** | {hopqua} **`2k`** {list_emoji.pinkcoin}"  
                            embed.color = discord.Color.from_rgb(0, 255, 0)  
                            await ctx.send(f"{votay} **Chính xác, đáp án là :** __**{dapan}**__. **Bạn được thưởng 2k** {list_emoji.pinkcoin}")
                        else:
                            cursor.execute("UPDATE users SET balance = balance + 2000 WHERE user_id = ?", (ctx.author.id,))  
                            embed.description = f"ㅤ\n# {emoji1}{emoji2}\nㅤ\n{dongho} **`0s`** | {hopqua} **`2k`** {list_emoji.pinkcoin}"  
                            embed.color = discord.Color.from_rgb(0, 255, 0)  
                            await ctx.send(f"{votay} **Chính xác, đáp án là :** __**{dapan}**__. **Bạn được thưởng 2k** {list_emoji.pinkcoin}")         
                    else:  
                        embed.description = f"ㅤ\n# {emoji1}{emoji2}\nㅤ\n{dongho} **`0s`** | {hopqua} **`2k`** {list_emoji.pinkcoin}"  
                        embed.color = discord.Color.from_rgb(255, 0, 0)  
                        await ctx.send(f'{sai} **Sai rồi má, đáp án là** : "**{dapan}**"')  
                    conn.commit()
                    await send.edit(embed=embed)  

            except asyncio.TimeoutError:  
                await ctx.send(f"{dongho} **Hết giờ rồi {ctx.author.mention} ơi, làm lại ván mới đi**")
            conn.close()
        except Exception as e:  
            print(e)  
            await ctx.send('Hiện tại lệnh bạn đang sử dụng đã gặp lỗi, hãy thử lại sau. Xin lỗi vì sự cố này')  

    async def update_timer(self, ctx, send, emoji1, emoji2, timeout):
        # Lấy avatar của người dùng để hiển thị ở footer
        avatar_url = ctx.author.avatar.url if ctx.author.avatar else "https://cdn.discordapp.com/embed/avatars/0.png"
        remaining = timeout

        # Cập nhật ngay lúc bắt đầu
        embed = discord.Embed(
            title=f"{maytinh} **ĐUỔI HÌNH BẮT CHỮ**",
            description=f"ㅤ\n# {emoji1}{emoji2}\nㅤ\n{dongho} **`{remaining}s`** | {hopqua} **`2k`** {list_emoji.pinkcoin}",
            color=discord.Color.from_rgb(216, 82, 255)
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1211199649667616768/1271283119063961630/1200px-Logo_uoi_hinh_bat_chu_sieu_toc2.jpg")
        embed.set_footer(text=f"{ctx.author.name}", icon_url=avatar_url)
        try:
            await send.edit(embed=embed)
        except discord.HTTPException as e:
            print("Lỗi khi cập nhật embed ban đầu:", e)

        # Trong khoảng thời gian đầu, cập nhật mỗi 5 giây; trong 5 giây cuối, cập nhật mỗi giây
        while remaining > 0:
            # Cập nhật nếu:
            # - Đây là lần cập nhật đầu (đã cập nhật ở trên)
            # - Hoặc thời gian còn lại chia hết cho 5 (đối với khoảng thời gian >5s)
            # - Hoặc còn dưới 5s (cập nhật liên tục)
            if remaining <= 5 or remaining % 5 == 0:
                embed = discord.Embed(
                    title=f"{maytinh} **ĐUỔI HÌNH BẮT CHỮ**",
                    description=f"ㅤ\n# {emoji1}{emoji2}\nㅤ\n{dongho} **`{remaining}s`** | {hopqua} **`2k`** {list_emoji.pinkcoin}",
                    color=discord.Color.from_rgb(216, 82, 255)
                )
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1211199649667616768/1271283119063961630/1200px-Logo_uoi_hinh_bat_chu_sieu_toc2.jpg")
                embed.set_footer(text=f"{ctx.author.name}", icon_url=avatar_url)
                try:
                    await send.edit(embed=embed)
                except discord.HTTPException as e:
                    print("Lỗi khi cập nhật embed:", e)
                    # Nếu gặp lỗi (ví dụ do rate limit) thì chờ thêm chút thời gian
                    await asyncio.sleep(1)
            await asyncio.sleep(1)
            remaining -= 1

        # Sau khi hết giờ, cập nhật embed hiển thị "Hết giờ!"
        embed = discord.Embed(
            title=f"{maytinh} **ĐUỔI HÌNH BẮT CHỮ**",
            description=f"ㅤ\n# {emoji1}{emoji2}\nㅤ\n{dongho} **`Hết giờ!`** | {hopqua} **`2k`** {list_emoji.pinkcoin}",
            color=discord.Color.from_rgb(255, 255, 0)
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1211199649667616768/1271283119063961630/1200px-Logo_uoi_hinh_bat_chu_sieu_toc2.jpg")
        embed.set_footer(text=f"{ctx.author.name}", icon_url=avatar_url)
        try:
            await send.edit(embed=embed)
        except discord.HTTPException as e:
            print("Lỗi khi cập nhật embed cuối cùng:", e)

    @duoihinhbatchu.error
    async def duoihinhbatchu_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            message = await ctx.send(f"Vui lòng đợi `{error.retry_after:.0f}s` trước khi sử dụng lệnh này!")
            await asyncio.sleep(2)
            await message.delete()
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error

async def setup(client):
    await client.add_cog(Dhbc(client))