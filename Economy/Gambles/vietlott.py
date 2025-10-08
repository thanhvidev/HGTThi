import random
import discord
import sqlite3
import datetime
from discord.ext import commands
import json

conn = sqlite3.connect('economy.db')
cursor = conn.cursor()


def is_registered(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None


def is_guild_owner_or_bot_owner():
    async def predicate(ctx):
        # or any(role.id == 1113463122515214427 for role in ctx.author.roles)
        return ctx.author == ctx.guild.owner or ctx.author.id in [573768344960892928, 919879676187508787]
    return commands.check(predicate)


def is_allowed_channel_vl():
    async def predicate(ctx):
        allowed_channel_id = 1156990030628261929  # ID của kênh văn bản cho phép
        if ctx.channel.id != allowed_channel_id:
            await ctx.send("Hãy dùng lệnh `zvl` ở kênh <#1156990030628261929>")
            return False
        return True
    return commands.check(predicate)


def is_allowed_channel_check():
    async def predicate(ctx):
        allowed_channel_ids = [1147355133622108262, 1090897131486842990,
                               1026627301573677147, 1035183712582766673]  # Danh sách ID của các kênh cho phép
        if ctx.channel.id not in allowed_channel_ids:
            await ctx.send("Hãy dùng lệnh `kho` ở các kênh <#1147355133622108262> <#1090897131486842990> <#1026627301573677147> <#1035183712582766673>")
            return False
        return True
    return commands.check(predicate)


class Vietlott(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.dk = None
        self.vevietlottery = None
        self.tangqua = None
        self.inv = None
        self.ga = None

    async def cog_load(self):
        """Called when the cog is loaded - Discord.py 2.0+ recommended way"""
        await self.init_emojis()

    async def init_emojis(self):
        self.guild = self.client.get_guild(1090136467541590066)
        self.vevietlottery = await self.guild.fetch_emoji(1155442146069991456)
        self.dk = await self.guild.fetch_emoji(1181400074127945799)
        self.tangqua = await self.guild.fetch_emoji(1179397064426278932)
        self.inv = await self.guild.fetch_emoji(1147387806226841671)
        self.ga = await self.guild.fetch_emoji(1146820050351820970)

    @commands.hybrid_command(aliases=["zgive"], description="tặng vé cho người khác", help="tặng vé cho người khác")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def give(self, ctx, nguoi_nhan: discord.User, so_luong: int):
        if not is_registered(ctx.author.id):
            await ctx.send(f"{self.dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
        else:
            if nguoi_nhan is None or so_luong is None or so_luong < 1:
                await ctx.send("Vd: ztang `user` `1`")
                return
            if nguoi_nhan.bot:  # Không cho phép trao đổi với bot
                await ctx.send("Không thể thực hiện trao đổi với bot.")
                return
            if nguoi_nhan.id == ctx.author.id:  # Không cho phép trao đổi với chính mình
                await ctx.send("Không thể thực hiện trao đổi với chính mình.")
                return
            cursor.execute(
                "SELECT vietlottery_tickets FROM users WHERE user_id = ?", (ctx.author.id,))
            sender_result = cursor.fetchone()
            if not sender_result:
                await ctx.send("Không thể tải thông tin vé của bạn.")
                return
            ve_type = "vietlottery_tickets"
            sender_ve = sender_result[0]
            if sender_ve < so_luong:
                await ctx.send(f" Bạn không đủ vé {self.vevietlottery} để tặng. Vui lòng `mua vé` tại kênh <#1156990030628261929>")
                return
            cursor.execute("SELECT id, " + ve_type +
                           " FROM users WHERE user_id = ?", (nguoi_nhan.id,))
            receiver_result = cursor.fetchone()
            if not receiver_result:
                await ctx.send(f"{self.dk} người nhận chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
                return
            if ctx.author.id == 919879676187508787 or ctx.author.id == 962627128204075039:
                new_receiver_ve = receiver_result[1] + so_luong
                cursor.execute("UPDATE users SET " + ve_type +
                               " = ? WHERE id = ?", (new_receiver_ve, receiver_result[0]))
            else:
                new_sender_ve = sender_ve - so_luong
                new_receiver_ve = receiver_result[1] + so_luong
                cursor.execute("UPDATE users SET " + ve_type +
                               " = ? WHERE user_id = ?", (new_sender_ve, ctx.author.id))
                cursor.execute("UPDATE users SET " + ve_type +
                               " = ? WHERE id = ?", (new_receiver_ve, receiver_result[0]))
            conn.commit()
            await ctx.send(f"{self.tangqua} **| {ctx.author.mention} đã tặng <@{nguoi_nhan.id}> {so_luong} {self.vevietlottery}**.")

    @commands.hybrid_command(aliases=["openvietlott", "movl"], description="Mở vé Vietlott", help="Mở vé Vietlott")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @is_allowed_channel_vl()
    async def vl(self, ctx, so_luong: int = None):
        if not is_registered(ctx.author.id):
            await ctx.send(f"{self.dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
        else:
            if so_luong is None:
                so_luong = 1
            elif so_luong < 1:
                await ctx.send("Vd: zvl `so_luong`")
                return
            elif so_luong > 50:
                await ctx.send("Bạn chỉ có thể mở tối đa 50 vé mỗi lần.")
                return
            cursor.execute(
                "SELECT vietlottery_tickets FROM users WHERE user_id = ?", (ctx.author.id,))
            sender_result = cursor.fetchone()

            if not sender_result:
                await ctx.send("Không thể tải thông tin vé của bạn.")
                return
            ve_type = "vietlottery_tickets"
            ve_numbers_type = "vietlottery_numbers"
            sender_ve = sender_result[0]
            if sender_ve < so_luong:
                await ctx.send(f" Bạn không đủ vé {self.vevietlottery} để mở. Vui lòng `mua vé`")
                return
            new_sender_ve = sender_ve - so_luong
            ve_numbers = []
            for _ in range(so_luong):
                ve_number = ' - '.join(sorted(random.sample(
                    [str(i).zfill(2) for i in range(1, 56)], k=6)))
                ve_numbers.append(f"{ve_number}")

            opened_numbers = "\n- ".join(ve_numbers)
            await ctx.send(f"{self.ga} **{ctx.author.mention} đã mở {so_luong} vé {self.vevietlottery}**:\n\n>>> - {opened_numbers}")
            cursor.execute("UPDATE users SET " + ve_type +
                           " = ? WHERE user_id = ?", (new_sender_ve, ctx.author.id))
            cursor.execute("SELECT " + ve_numbers_type +
                           " FROM users WHERE user_id = ?", (ctx.author.id,))
            existing_ve_numbers = cursor.fetchone()[0]
            if existing_ve_numbers:
                ve_numbers = json.loads(existing_ve_numbers) + ve_numbers
            ve_numbers = sorted(ve_numbers)
            cursor.execute("UPDATE users SET " + ve_numbers_type +
                           " = ? WHERE user_id = ?", (json.dumps(ve_numbers), ctx.author.id))
            conn.commit()

    @commands.hybrid_command(aliases=["checkvl", "vietlott"], description="Kiểm tra vé Vietlott", help="Kiểm tra vé Vietlott")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @is_allowed_channel_check()
    async def kho(self, ctx):
        if ctx.message.content != ctx.prefix + "kho":
            return
        if not is_registered(ctx.author.id):
            await ctx.send(f"{self.dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
        else:
            cursor.execute(
                "SELECT vietlottery_numbers FROM users WHERE user_id = ?", (ctx.author.id,))
            result = cursor.fetchone()
            if not result:
                await ctx.send("Không thể tải thông tin vé của bạn.")
                return
            ve_numbers = result[0]
            if not ve_numbers:
                await ctx.send("Bạn chưa mở vé vietlott nào cả. Vui lòng `mua` và `mở vé` tại kênh <#1156990030628261929>")
                return
            ve_numbers = json.loads(ve_numbers)
            if not ve_numbers:
                await ctx.send("Bạn chưa mở vé vietlott nào cả. Vui lòng `mua` và `mở vé` tại kênh <#1156990030628261929>")
                return

            # Tách nội dung thành các phần nhỏ
            chunk_size = 40
            chunks = [ve_numbers[i:i+chunk_size]
                      for i in range(0, len(ve_numbers), chunk_size)]

            formatted_header = f"{self.inv} **Số vé của {ctx.author.mention} đã mở trong kì này: {len(ve_numbers)} {self.vevietlottery}\n\n**"
            # Gửi tiêu đề ở mỗi tin nhắn
            await ctx.send(f"{formatted_header}")
            for chunk in chunks:
                formatted_chunk = "\n".join(
                    [f"- {'-'.join(ve.split('-'))}" for ve in chunk])

                # Tách thành các phần nhỏ hơn nếu quá dài
                while formatted_chunk:
                    send_chunk, formatted_chunk = formatted_chunk[:1900], formatted_chunk[1900:]
                    await ctx.send(f">>> {send_chunk}")

    @commands.hybrid_command(aliases=["rsvl", "resetvietlott"], description="reset vé", help="reset vé")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @is_guild_owner_or_bot_owner()
    async def rsvietlott(self, ctx):
        cursor.execute(
            "UPDATE users SET vietlottery_numbers = '' WHERE vietlottery_numbers != ''")
        conn.commit()
        await ctx.send("Đã thực hiện reset vé vietlott thành công")

async def setup(client):
    await client.add_cog(Vietlott(client))