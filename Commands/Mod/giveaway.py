import datetime
import discord
from discord.ext import commands
import asyncio
import time as pyTime
import time
import random
import sqlite3
import config
import json
import os
from discord import File
from utils.checks import is_mod, is_admin, is_mod

rolehost = config.ROLE_HOST

conn = sqlite3.connect('giveaways.db')
c = conn.cursor()

# Tạo bảng để lưu trữ thông tin giveaway
c.execute('''CREATE TABLE IF NOT EXISTS giveaways
             (id INTEGER PRIMARY KEY, time INTEGER, prize TEXT, message INTEGER, participants TEXT, winners INTEGER, finished BOOL, host INTEGER, win INTEGER)''')
conn.commit()

gacanhtrai = "<a:canhtrai_ga:1296345003697766400>"
gacanhphai = "<a:canhphai_ga:1296345015978557492>"
gabongbong = "<a:phaohoaga:1417822007390765146>"
gatim = "<:gatim:1417821987522215997>"
ganoel = "<a:ganoel:1417819687818887198>"
# qua = "<:ganoel3:1314524900458758154>"

emoji_numbers = ['<:1_:1267453141771878523>', '<:2_:1267453158305566791>', '<:3_:1267453168560640081>', '<:4_:1267453179247984651>', '<:5_:1267453189414846574>', '<:6_:1267453199070269473>', '<:7_:1267453210193301544>', '<:8_:1267453220448370761>', '<:9_:1267453232158867495>', '<:0_:1267455519149527142>']

# Hàm để load và lưu dữ liệu từ file JSON
def load_banned_users():
    try:
        with open("giveawayban.json", "r") as f:
            banned_users = json.load(f)
            if not isinstance(banned_users, list):  # Đảm bảo là list
                banned_users = []
        return banned_users
    except FileNotFoundError:
        return []

def save_banned_users(banned_users):
    with open("giveawayban.json", "w") as f:
        json.dump(banned_users, f)

# Đường dẫn tới tệp ảnh bạn muốn gửi
image_path = 'ga.gif'

# Tạo một đối tượng File từ đường dẫn tới ảnh
file = File(image_path)

class Giveaway(commands.Cog):
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

    @commands.command(aliases=["setgacam"], description="")
    @is_mod()
    async def camgiveaway(self, ctx, member: discord.Member):
        banned_users = load_banned_users()
        
        # Kiểm tra nếu ID người dùng đã tồn tại trong danh sách
        if member.id not in banned_users:
            banned_users.append(member.id)
            save_banned_users(banned_users)
            await ctx.send(f"{member.mention} đã bị cấm tham gia giveaway.")
        else:
            await ctx.send(f"{member.mention} đã có trong cấm giveaway.")

    @commands.command(aliases=["setgamo"], description="")
    @is_mod()
    async def mogiveaway(self, ctx, member: discord.Member):
        banned_users = load_banned_users()
        if member == "all":
            banned_users.clear()
            save_banned_users(banned_users)
            await ctx.send("Đã gỡ all cấm giveaway.")
            return
        # Kiểm tra nếu người dùng có trong danh sách cấm
        if member.id in banned_users:
            banned_users.remove(member.id)  # Xoá người dùng khỏi danh sách
            save_banned_users(banned_users)  # Lưu lại danh sách
            await ctx.send(f"{member.mention} đã được gỡ cấm giveaway.")
        else:
            await ctx.send(f"{member.mention} không có trong cấm giveaway.")

    @commands.command(aliases=["setgatrung"], description="")
    @is_mod()
    async def setgiveaway(self, ctx, message: int, *users: discord.Member):
        try:
            # Kiểm tra nếu message_id có tồn tại trong bảng giveaways và lấy số lượng win
            c.execute("SELECT win FROM giveaways WHERE message = ?", (message,))
            result = c.fetchone()
            if not result:
                await ctx.send("Không tìm thấy giveaways.")
                return

            win_sl = result[0]

            # Kiểm tra nếu số lượng users được set không đủ với winners
            if len(users) < win_sl:
                await ctx.send(f"Cần ít nhất {win_sl} người thắng.")
                return
            
            if any(user.bot for user in users):
                    await ctx.send("Không thể thêm bot vào danh sách người tham gia.")
                    return
            # Xoá hết dữ liệu trong cột participants của message
            c.execute("UPDATE giveaways SET participants = '' WHERE message = ?", (message,))

            # Thêm ID của từng user vào participants (cách nhau bởi dấu phẩy)
            participants = " ".join(str(user.id) for user in users)
            c.execute("UPDATE giveaways SET participants = ? WHERE message = ?", (participants, message))

            conn.commit()
            await ctx.send(f"Đã cập nhật {len(users)} win với message_id {message}.")

        except sqlite3.Error as e:
            await ctx.send("Có lỗi xảy ra khi cập nhật dữ liệu.")
            print(e)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        # Kiểm tra nếu user trong danh sách cấm
        banned_users = load_banned_users()
        if user.id in banned_users:
            return
        # Tiếp tục phần còn lại của code nếu user không nằm trong danh sách cấm
        channel = reaction.message.channel
        c.execute("SELECT * FROM giveaways WHERE message = ?", (reaction.message.id,))
        data = c.fetchone()
        guild = self.client.get_guild(1090136467541590066)
        ganoel2 = await guild.fetch_emoji(1417817584295870525)
        if data is None:
            return
        if reaction.emoji == ganoel2:
            current_time = datetime.datetime.now()
            end_time = datetime.datetime.fromtimestamp(int(data[1]))
            if current_time > end_time:
                return
            participants = list(filter(lambda p: p != "[]", data[4].split(" ")))
            if str(user.id) not in participants:
                participants.append(str(user.id))
                c.execute("UPDATE giveaways SET participants = ? WHERE message = ?", (" ".join(participants), reaction.message.id))
                conn.commit()

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if user.bot:
            return
        channel = reaction.message.channel
        c.execute("SELECT * FROM giveaways WHERE message = ?",
                  (reaction.message.id,))
        data = c.fetchone()
        guild = self.client.get_guild(1090136467541590066)
        ganoel2 = await guild.fetch_emoji(1417817584295870525)
        if data is None:
            return
        if reaction.emoji == ganoel2:
            current_time = datetime.datetime.now()
            end_time = datetime.datetime.fromtimestamp(
                int(data[1]))  # Chuyển đổi thành datetime
            if current_time > end_time:
                return
            participants = list(
                filter(lambda p: p != "[]", data[4].split(" ")))
            if str(user.id) in participants:
                participants.remove(str(user.id))
                if participants:
                    c.execute("UPDATE giveaways SET participants = ? WHERE message = ?", (" ".join(
                        participants), reaction.message.id))
                else:
                    c.execute(
                        "UPDATE giveaways SET participants = ? WHERE message = ?", ("[]", reaction.message.id))
                conn.commit()

    @commands.hybrid_command(aliases=["gstart", "ga"],  description="Tạo give away")
    async def giveaway(self, ctx, time=None, winners: str = None, *, prize: str = None):
        if await self.check_command_disabled(ctx):
            return
        if prize is None or time is None or winners is None:
            await ctx.reply("Điền đầy đủ thông tin (vd: zga 20s 1w 50k)")
            return
        if time.endswith("s"):
            time = int(time[:-1])
            time = time
        elif time.endswith("m"):
            time = int(time[:-1])
            time = time * 60
        elif time.endswith("h"):
            time = int(time[:-1])
            time = time * 60 * 60
        elif time.endswith("d"):
            time = int(time[:-1])
            time = time * 60 * 60 * 24
        else:
            await ctx.reply("Điền đúng định dạng của thời gian ̣(s,m,h)")
        guild = self.client.get_guild(1090136467541590066)
        guild1 = self.client.get_guild(832579380634451969)
        ganoel2 = await guild.fetch_emoji(1417817584295870525)
        gacontent1 = f"ㅤ{ganoel} **GIVEAWAY ĐÃ BẮT ĐẦU** {ganoel}"
        gacontent2 = f"ㅤ{ganoel} **GIVEAWAY ĐÃ KẾT THÚC** {ganoel}"
        if winners.endswith("w"):
            winners = int(winners[:-1])
            end_time = pyTime.time()
            timestamp = datetime.datetime.fromtimestamp(time + end_time)
            embed = discord.Embed(
                title=f"**{prize}**", description=f"{gatim} Ends: <t:{int(time + end_time)}:R>\n{gatim} Winners: {winners}\n{gatim} Hosted by: {ctx.author.mention}", color=discord.Color.from_rgb(255,158,244))
            # <t:{int(time + end_time)}:t>
            # Thêm avatar của Tổ chức bởi vào embed
            if ctx.author.avatar:
                avatar_url = ctx.author.avatar.url
            else:
                avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"  # Sử dụng avatar mặc định
            # Đặt avatar vào hình thu nhỏ của embed
            embed.set_thumbnail(url=avatar_url)
            embed.set_footer(text=f"{winners} win | Ends at", icon_url=guild1.icon.url)
            embed.timestamp = timestamp
            msg = await ctx.send(content = gacontent1,embed=embed)
            await msg.add_reaction(ganoel2)
            try:
                await ctx.message.delete()
            except discord.NotFound:
                # Nếu không tìm thấy tin nhắn để xóa, không làm gì cả
                pass
            c.execute("INSERT INTO giveaways VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (None, int(
                time + end_time), prize, msg.id, "[]", "[]", False, ctx.author.id, winners))
            conn.commit()
            await asyncio.sleep(time)
            c.execute("SELECT * FROM giveaways WHERE message = ?", (msg.id,))
            data = c.fetchone()
            if data[4] == "[]":
                embed = discord.Embed(
                    title=f"**{prize}**", description=f"{gatim} Ends:  <t:{data[1]}:R>\n{gatim} Winners: 0 \n{gatim} Hosted by: {ctx.author.mention}", color=discord.Color.from_rgb(158,230,255))
                # Thêm avatar của Tổ chức bởi vào embed
                if ctx.author.avatar:
                    avatar_url = ctx.author.avatar.url
                else:
                    avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"  # Sử dụng avatar mặc định
                # Đặt avatar vào hình thu nhỏ của embed
                embed.set_thumbnail(url=avatar_url)
                embed.set_footer(text=f"Ends at", icon_url=guild1.icon.url)
                embed.timestamp = timestamp
                await msg.edit(content = gacontent2 ,embed=embed)
                embed1 = discord.Embed(
                    description=f"Không một ai tham gia giveaway ", color=discord.Color.from_rgb(158,230,255))
                await msg.reply(embed=embed1)
                c.execute(
                    "UPDATE giveaways SET finished = ? WHERE message = ?", (True, msg.id))
                conn.commit()
            else:
                if data[6] == False:
                    c.execute(
                        "UPDATE giveaways SET win = ? WHERE id = ?", (winners, msg.id))
                    conn.commit()
                    c.execute(
                        "SELECT * FROM giveaways WHERE message = ?", (msg.id,))
                    data = c.fetchone()
                    participants = list(
                        filter(lambda p: p != "[]", data[4].split(" ")))
                    if not bool(participants):
                        await ctx.reply("> Không ai tham gia vào giveaway này")
                        return
                    else:
                        winners = []
                        if len(participants) >= int(data[8]):
                            for i in range(int(data[8])):
                                # remaining_participants = participants.copy()
                                winner = random.choice(participants)
                                winners.append(winner)
                                participants.remove(winner)
                            winners_str = ""
                            for w in winners:
                                winners_str += f"<@{w}> "
                            # winners_content = ""
                            # for idx, w in enumerate(winners, start=1):
                            #     emoji = emoji_numbers[idx - 1] if idx - 1 < len(emoji_numbers) else f"{idx}️⃣"
                            #     winners_content += f" {emoji}<@{w}>"                         
                            embed = discord.Embed(
                                title=f"**{prize}**", description=f"{gatim} Ends:  <t:{data[1]}:R>\n{gatim} Winners: {winners_str}\n{gatim} Hosted by: {ctx.author.mention}", color=discord.Color.from_rgb(158,230,255))
                            # Thêm avatar của Tổ chức bởi vào embed
                            if ctx.author.avatar:
                                avatar_url = ctx.author.avatar.url
                            else:
                                avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"  # Sử dụng avatar mặc định
                            # Đặt avatar vào hình thu nhỏ của embed
                            embed.set_thumbnail(url=avatar_url)
                            embed.set_footer(text=f"Ends at", icon_url=guild1.icon.url)
                            embed.timestamp = timestamp
                            await msg.edit(content = gacontent2, embed=embed)
                            await msg.reply(
                                content=f"{gabongbong} **Chúc mừng** {winners_str}**đã thắng giải thưởng** __**{prize}**__ **của** {ctx.author.mention}\n"
                            )
                            # with open(image_path, 'rb') as f:
                            #     file = File(f)

                            #     await msg.reply(
                            #         content=f"{gabongbong} **Chúc mừng**{winners_content}**đã thắng giải thưởng** __**{prize}**__ **của** {ctx.author.mention}\n",
                            #         file=file
                            #     )
                            winners_strs = ' '.join(map(str, winners))
                            c.execute(
                                "UPDATE giveaways SET finished = ?, winners = ? WHERE message = ?", (True, winners_strs, msg.id))
                            conn.commit()
                        else:
                            embed = discord.Embed(
                                title=f"**{prize}**", description=f"{gatim} Ends:  <t:{data[1]}:R>\n{gatim} Winners: 0 \n{gatim} Hosted by: {ctx.author.mention}", color=discord.Color.from_rgb(158,230,255))
                        # Thêm avatar của Tổ chức bởi vào embed
                            if ctx.author.avatar:
                                avatar_url = ctx.author.avatar.url
                            else:
                                avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"  # Sử dụng avatar mặc định
                            # Đặt avatar vào hình thu nhỏ của embed
                            embed.set_thumbnail(url=avatar_url)
                            # embed.set_author(name=f"{prize}", icon_url=ctx.guild.icon.url)
                            embed.set_footer(text=f"Ends at", icon_url=guild1.icon.url)
                            embed.timestamp = timestamp
                            await msg.edit(content = gacontent2, embed=embed)
                            embed1 = discord.Embed(
                                description=f"Số lượng người tham gia không đủ", color=discord.Color.from_rgb(158,230,255))
                            await msg.reply(embed=embed1)
                            c.execute(
                                "UPDATE giveaways SET finished = ? WHERE message = ?", (True, msg.id))
                            conn.commit()
        else:
            await ctx.reply("winners phải kết thúc bằng chữ 'w'.")

    @commands.hybrid_command(aliases=["gend", "gaend", "end"],  description="Kết thúc give away")
    async def giveawayend(self, ctx, msg: discord.Message = None):
        if await self.check_command_disabled(ctx):
            return
        if not (ctx.author.guild_permissions.administrator or any(role.name == rolehost for role in ctx.author.roles) or ctx.author.id == msg.author.id):
            await ctx.reply("> Bạn không có tuổi để sử dụng lệnh này!")
        if msg is None or isinstance(msg, str):
            await ctx.reply("Điền id tin nhắn giveaway")
            return
        c.execute("SELECT * FROM giveaways WHERE message = ?", (msg.id,))
        data = c.fetchone()
        gacontent2 = f"ㅤ{ganoel} **GIVEAWAY ĐÃ KẾT THÚC** {ganoel}"
        if data is None:
            await ctx.reply("Không tìm thấy giveaway này!")
            return
        timestamp = datetime.datetime.fromtimestamp(data[1])
        guild1 = self.client.get_guild(832579380634451969)
        if data[4] == "":
            embed = discord.Embed(
                title=f"**{data[2]}**", description=f"{gatim} Ends:  <t:{data[1]}:R>\n{gatim} Winners: 0 \n{gatim} Hosted by: <@{data[7]}>", color=discord.Color.from_rgb(158,230,255))
            # embed.set_author(name=f"{data[2]}", icon_url=ctx.guild.icon.url)
            # Thêm avatar của Tổ chức bởi vào embed
            user = await self.client.fetch_user(data[7])
            # Kiểm tra nếu user có avatar
            if user.avatar:
                avatar_url = user.avatar.url
            else:
                avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"  # Sử dụng avatar mặc định
            # Đặt avatar vào hình thu nhỏ của embed
            embed.set_thumbnail(url=avatar_url)
            embed.set_footer(text=f"Ends at", icon_url=guild1.icon.url)
            embed.timestamp = timestamp
            await msg.edit(content = gacontent2, embed=embed)
            embed1 = discord.Embed(
                description=f"Không một ai tham gia giveaway ", color=discord.Color.from_rgb(158,230,255))
            await msg.reply(embed=embed1)
            c.execute(
                "UPDATE giveaways SET finished = ? WHERE message = ?", (True, msg.id))
            conn.commit()
        else:
            if data[6] == False:
                c.execute("SELECT * FROM giveaways WHERE message = ?", (msg.id,))
                data = c.fetchone()
                participants = list(
                    filter(lambda p: p != "[]", data[4].split(" ")))
                if not bool(participants):
                    await ctx.reply("Không có ai tham gia vào giveaway này")
                    return
                else:
                    winners = []
                    if len(participants) >= int(data[8]):
                        for i in range(int(data[8])):
                            # remaining_participants = participants.copy()
                            winner = random.choice(participants)
                            winners.append(winner)
                            participants.remove(winner)
                        winners_str = ""
                        for w in winners:
                            winners_str += f"<@{w}> "
                        # winners_content = ""
                        # for idx, w in enumerate(winners, start=1):
                        #     emoji = emoji_numbers[idx - 1] if idx - 1 < len(emoji_numbers) else f"{idx}️⃣"
                        #     winners_content += f" {emoji}<@{w}>" 
                        embed = discord.Embed(
                            title=f"**{data[2]}**", description=f"{gatim} Ends:  <t:{data[1]}:R>\n{gatim} Winners: {winners_str}\n{gatim} Hosted by: <@{data[7]}>", color=discord.Color.from_rgb(158,230,255))
                        # Thêm avatar của Tổ chức bởi vào embed
                        user = await self.client.fetch_user(data[7])
                        # Kiểm tra nếu user có avatar
                        if user.avatar:
                            avatar_url = user.avatar.url
                        else:
                            avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png" # Sử dụng avatar mặc định
                        # Đặt avatar vào hình thu nhỏ của embed
                        embed.set_thumbnail(url=avatar_url)
                        embed.set_footer(text=f"Ends at", icon_url=guild1.icon.url)
                        embed.timestamp = timestamp
                        await msg.edit(content = gacontent2, embed=embed)
                        await msg.reply(
                            content=f"{gabongbong} **Chúc mừng** {winners_str}**đã thắng giải thưởng** __**{data[2]}**__ **của** <@{data[7]}>\n"
                        )
                        # with open(image_path, 'rb') as f:
                        #     file = File(f)

                        #     await msg.reply(
                        #         content=f"{gabongbong} **Chúc mừng**{winners_content}**đã thắng giải thưởng** __**{data[2]}**__ **của** <@{data[7]}>\n",
                        #         file=file
                        #     )
                        winners_strs = ' '.join(map(str, winners))
                        c.execute(
                            "UPDATE giveaways SET finished = ?, winners = ? WHERE message = ?", (True, winners_strs, msg.id))
                        conn.commit()
                    else:
                        embed = discord.Embed(
                            title=f"**{data[2]}**", description=f"{gatim} Ends:  <t:{data[1]}:R>\n{gatim} Winners: 0 \n{gatim} Hosted by: <@{data[7]}>", color=discord.Color.from_rgb(158,230,255))
                        # Thêm avatar của Tổ chức bởi vào embed
                        if ctx.author.avatar:
                            avatar_url = ctx.author.avatar.url
                        else:
                            avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"  # Sử dụng avatar mặc định
                        # Đặt avatar vào hình thu nhỏ của embed
                        embed.set_thumbnail(url=avatar_url)
                        embed.set_footer(text=f"Ends at", icon_url=guild1.icon.url)
                        embed.timestamp = timestamp
                        await msg.edit(content = gacontent2, embed=embed)
                        embed1 = discord.Embed(
                            description=f"Số lượng người tham gia không đủ", color=discord.Color.from_rgb(158,230,255))
                        await msg.reply(embed=embed1)
                        c.execute(
                            "UPDATE giveaways SET finished = ? WHERE message = ?", (True, msg.id))
                        conn.commit()
            else:
                await ctx.reply("> Giveaway này Kết thúc!")

    @commands.hybrid_command(aliases=["rr", "garr"], description="reroll")
    async def giveaway_reroll(self, ctx, msg: discord.Message = None):
        if await self.check_command_disabled(ctx):
            return
        c.execute("SELECT * FROM giveaways WHERE message = ?", (msg.id,))
        data = c.fetchone()
        if not (ctx.author.guild_permissions.administrator or any(role.name == rolehost for role in ctx.author.roles) or ctx.author.id == data[7]):
            await ctx.reply("> Bạn cần role `host` để sử dụng lệnh này!!")
            return
        if msg is None:
            await ctx.reply("Nhập ID tin nhắn giveaway cần reroll.")
            return
        if data is None:
            await ctx.reply("Không tìm thấy giveaway này!")
            return
        if not data[6]:
            await ctx.reply("Giveaway này chưa kết thúc!")
            return
        participants = list(filter(lambda p: p != "[]", data[4].split(" ")))
        if len(participants) < int(data[8]):
            await ctx.reply("Số lượng người tham gia chưa đủ để reroll.")
            return
        winners = []
        for i in range(int(data[8])):
            # remaining_participants = participants.copy()
            winner = random.choice(participants)
            winners.append(winner)
            participants.remove(winner)
        winners_str = ""
        for w in winners:
            winners_str += f"<@{w}> "
        # winners_content = ""
        # for idx, w in enumerate(winners, start=1):
        #     emoji = emoji_numbers[idx - 1] if idx - 1 < len(emoji_numbers) else f"{idx}️⃣"
        #     winners_content += f" {emoji}<@{w}>"  
        # winners_str = " ".join(f"<@{winner}>" for winner in winners)
        c.execute("UPDATE giveaways SET winners = ?, finished = ? WHERE message = ?",
                  (winners_str, True, msg.id))
        conn.commit()
        gacontent2 = f"ㅤ{ganoel} **GIVEAWAY ĐÃ KẾT THÚC** {ganoel}"
        timestamp = datetime.datetime.fromtimestamp(data[1])
        guild1 = self.client.get_guild(832579380634451969)
        embed = discord.Embed(
            title=f"**{data[2]}**", description=f"{gatim} Ends:  <t:{data[1]}:R>\n{gatim} Winners: {winners_str}\n{gatim} Hosted by: <@{data[7]}>", color=discord.Color.from_rgb(158,230,255))
        # Lấy user object từ ID
        user = await self.client.fetch_user(data[7])
        # Kiểm tra nếu user có avatar
        if user.avatar:
            avatar_url = user.avatar.url
        else:
            avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"  # Sử dụng avatar mặc định
        # Đặt avatar vào hình thu nhỏ của embed
        embed.set_thumbnail(url=avatar_url)
        embed.set_footer(text=f"Ends at", icon_url=guild1.icon.url)
        embed.timestamp = timestamp
        await msg.edit(content = gacontent2, embed=embed)
        await msg.reply(
            content=f"{gabongbong} **Chúc mừng** {winners_str}**đã thắng giải thưởng** __**{data[2]}**__ **của** <@{data[7]}>\n"
        )
        # with open(image_path, 'rb') as f:
        #     file = File(f)

        #     await msg.reply(
        #         content=f"{gabongbong} **Chúc mừng**{winners_content}**đã thắng giải thưởng** __**{data[2]}**__ **của** <@{data[7]}>\n",
        #         file=file
        #     )

    # @commands.hybrid_command(aliases=["gdelete", "del", "gremove"],  description="Xóa giveaway")
    # async def giveawaydelete(self, ctx, msg: discord.Message = None):
    #     if not (ctx.author.guild_permissions.administrator or any(role.name == rolehost for role in ctx.author.roles)):
    #         await ctx.reply("> Bạn không có quyền sử dụng lệnh này!")
    #     if msg is None or isinstance(msg, str):
    #         await ctx.reply("Vui lòng cung cấp id tin nhắn giveaway.")
    #         return
    #     c.execute("SELECT * FROM giveaways WHERE message = ?", (msg.id,))
    #     data = c.fetchone()
    #     if data is None:
    #         await ctx.reply("Không tìm thấy giveaway này.")
    #     else:
    #         c.execute("DELETE FROM giveaways WHERE message = ?", (msg.id,))
    #         conn.commit()
    #         await ctx.reply("Đã xóa giveaway thành công.")

    @commands.hybrid_command(aliases=["endall", "gendall"],  description="Kết thúc tất cả giveaway")
    async def giveawayendall(self, ctx):
        if await self.check_command_disabled(ctx):
            return
        if not (ctx.author.guild_permissions.administrator or any(role.name == rolehost for role in ctx.author.roles)):
            await ctx.reply("> Bạn cần role `host` để sử dụng lệnh này!")
        c.execute("SELECT * FROM giveaways WHERE finished = 0")
        data = c.fetchall()
        if data is None:
            await ctx.reply("Không có giveaway nào.")
        else:
            for i in data:
                msg = await ctx.fetch_message(i[3])
                await self.giveawayend(ctx, msg)
            await ctx.reply("Kết thúc tất cả giveaway.")
            
    @commands.hybrid_command(aliases=["resetga", "rsga"], description="Reset dữ liệu giveaway")
    @is_mod()
    async def giveawayreset(self, ctx):
        if await self.check_command_disabled(ctx):
            return
        c.execute("DELETE FROM giveaways WHERE finished = 1")  # Xoá dữ liệu các hàng có cột `finished` bằng 1
        conn.commit()
        await ctx.reply("Đã reset dữ liệu giveaway đã kết thúc.")

async def setup(client):
    await client.add_cog(Giveaway(client))