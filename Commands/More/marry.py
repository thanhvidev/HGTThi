import asyncio
import json
import discord
import random
import sqlite3
import datetime
from discord.ui import View, Button
from discord.ext import commands
from Commands.Mod.list_emoji import list_emoji, lambanh_emoji
from utils.checks import is_bot_owner, is_admin, is_mod

import re 

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

# def is_guild_owner_or_bot_owner():
#     async def predicate(ctx):
#         guild_owner = ctx.author == ctx.guild.owner
#         bot_owner = ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222
#         specific_role = any(role.id == 1113463122515214427 for role in ctx.author.roles)

#         return guild_owner or bot_owner or specific_role
    
#     return commands.check(predicate)

def is_allowed_channel_check():
    async def predicate(ctx):
        allowed_channel_ids = [1147355133622108262, 1152710848284991549, 1079170812709458031, 1207593935359320084, 1215331218124574740,1215331281878130738, 1051454917702848562, 1210296290026455140, 1210417888272318525, 1256198177246285825, 1050649044160094218, 1091208904920281098, 1238177759289806878, 1243264114483138600, 1251418765665505310, 1243440233685712906, 1237810926913323110, 1247072223861280768, 1270031327999164548, 1022533822031601766, 1065348266193063979, 1027622168181350400, 1072536912562241546, 1045395054954565652]
        if ctx.channel.id in allowed_channel_ids:
            return False
        return True
    return commands.check(predicate)

def is_allowed_channel_checkmarry():
    async def predicate(ctx):
        allowed_channel_ids = [1273769188988682360, 1273769137985818624, 1273768884885000326, 1273768834830041301]
        if ctx.channel.id in allowed_channel_ids:
            return False
        return True
    return commands.check(predicate)

# def sethinhanh():
#     async def predicate(ctx):
#         guild_owner = ctx.author == ctx.guild.owner
#         bot_owner = ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222
#         specific_role = any(role.id == 1273442134783037440 for role in ctx.author.roles)

#         return guild_owner or bot_owner or specific_role
    
#     return commands.check(predicate)

# def settho():
#     async def predicate(ctx):
#         guild_owner = ctx.author == ctx.guild.owner
#         bot_owner = ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222
#         specific_role = any(role.id == 1273442026314137681 for role in ctx.author.roles)

#         return guild_owner or bot_owner or specific_role
    
#     return commands.check(predicate)

def set_marry():
    async def predicate(ctx):
        guild_owner = ctx.author == ctx.guild.owner
        bot_owner = ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222
        specific_role = any(role.id == 1273868227457454111 for role in ctx.author.roles)

        return guild_owner or bot_owner or specific_role
    
    return commands.check(predicate)

emojidung = "<:hgtt_dung:1186838952544575538>"
emojisai = "<:hgtt_sai:1186839020974657657>"
emojichamthan = "<:hgtt_chamthan:1179452469017858129>"
emojitimxanh = "<:love:1192058678812090440>"
emojitim7mau = "<a:aedgy_heartflow:1192058758625505332>"
emojihopnhan = "<:nhanhop:1191617855356162088>"
emojilaplanh = "<:decor:1193055673324421120>"
emojigau = "<a:married:1193057770124091474>"
emojidongho = "<a:hgtt_timee:1159077258535907328>"
emojitimhong = "<a:emoji_50:1273622387358957618>"
bbtim = "<:emoji_49:1272794255563292743>"
marry1 = "<a:emoji_31:1271993759378440192>"
lich = "<:emoji_48:1272794223195721728>"
cauhon = "<:emoji_51:1272803273299984384>"
thanmat = "<:emoji_47:1272794189771440172>"
lyhon = "<:emoji_52:1272808176567193705>"
lyhon1 = "<:warn:1262757428374798338>"
loihenuoc ="<:loihenuoc:1273550049585926228>"
nhanmarry = "<:emoji_52:1272537100276989974>"
tuyenbo = "<:emoji_51:1273595540453724203>"
ngay = "<:emoji_52:1273603977828896830>"
line = "<a:hgtt_gach:1273235979750342737>"
bling = "<a:bling:1273617325089751103>"
linemarry = "<a:linemarry:1274167325934878740>"
dungset = '<a:dung1:1340173892681072743>'
saiset = '<a:sai1:1340173872535703562>'

class Marry(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.confirm_threshold_choices = [3, 4, 5, 6, 7]

    async def check_command_disabled(self, ctx):  
        guild_id = str(ctx.guild.id)  
        command_name = ctx.command.name.lower()  
        if guild_id in self.client.get_cog('Toggle').toggles:  
            if command_name in self.client.get_cog('Toggle').toggles[guild_id]:  
                if ctx.channel.id in self.client.get_cog('Toggle').toggles[guild_id][command_name]:  
                    await ctx.send(f"Lệnh `{command_name}` đã bị tắt ở kênh này.")  
                    return True  
        return False 

    @commands.command( description="Kết hôn với người nào đó bằng nhẫn hoặc hiển thị thông tin kết hôn của bạn")
    @is_allowed_channel_checkmarry()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def marry(self, ctx, user_mention: discord.User = None, ring_id: int = None):
        if await self.check_command_disabled(ctx):
            return
        if ctx.channel.id == 1215331218124574740 or ctx.channel.id == 1215331281878130738:
            return None
        # Lấy thông tin người dùng hiện tại
        author_id = ctx.author.id
        author_name = ctx.author.name
        conn = get_database_connection()
        cursor = conn.cursor()
        if ring_id is not None and user_mention is not None:
            # Kiểm tra xem người dùng đã đăng ký chưa
            if not is_registered(author_id):
                await ctx.send("Bạn chưa đăng ký trong hệ thống.")
                return
            # Kiểm tra xem người được tag có trong cơ sở dữ liệu không
            if not is_registered(user_mention.id):
                await ctx.send("Người được tag không có trong hệ thống.")
                return
            # Kiểm tra id nhẫn trong purchased_items của người dùng hiện tại
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (author_id,))
            user_data = cursor.fetchone()
            purchased_items = user_data[6]
            if purchased_items == '':
                await ctx.send("Bạn chưa sở hữa chiếc nhẫn nào cả.")
                return
            if ring_id not in [int(item.split(":")[0]) for item in purchased_items.split(",")]:
                await ctx.send("Bạn chưa mua nhẫn này.")
                return
            ring_quantity = next(int(item.split(":")[2]) for item in purchased_items.split(",") if int(item.split(":")[0]) == ring_id)
            if ring_quantity == 0:
                await ctx.send("Bạn chưa mua nhẫn này.")
                return
            cursor.execute("SELECT marry FROM users WHERE user_id = ? OR user_id = ?", (author_id, user_mention.id))
            marry_status = cursor.fetchall()
            if marry_status[0][0] != '' or marry_status[1][0] != '':
                await ctx.send("Ai đó đã kết hôn rồi, tính ngoại tình à?")
                return

            if user_mention.bot or user_mention.id == author_id:
                await ctx.send("Không thể tự kết hôn hoặc kết hôn với bot.")
                return
            current_time = datetime.datetime.now().strftime('%d/%m/%Y')        
            items = purchased_items.split(",")
            name_ring = ""
            emoji_ring = ""

            for item in items:
                parts = item.split(":")
                if int(parts[0]) == ring_id:
                    emoji_string = item.split("<")[1].split(">")[0]
                    name_ring = parts[1]
                    emoji_ring = f"<{emoji_string}>"
                    break
            embed = discord.Embed(
                title=f"{nhanmarry} **𝗗𝗢 𝗬𝗢𝗨 𝗠𝗔𝗥𝗥𝗬 𝗠𝗘?** {nhanmarry}",
                description=f"**{ctx.author.mention} đã cầu hôn {user_mention.mention} bằng {name_ring} {emoji_ring}**",
                color=discord.Color.from_rgb(255, 192, 203)
            )
            embed.add_field(name="", value=f"**React {emojidung} để đồng ý hoặc {emojisai} để từ chối.**", inline=False)
            embed.set_image(url="https://cdn.discordapp.com/attachments/1339303289753309225/1339395247557312533/Colorful_Children_Illustrations_Recipe_for_Friendship_SEL_Presentation.png")
            proposal_msg = await ctx.send(embed=embed)
            await proposal_msg.add_reaction(emojidung)  # Tick xanh
            await proposal_msg.add_reaction(emojisai)   # Tick đỏ

            def check(reaction, user):
                return user == user_mention and str(reaction.emoji) in [emojidung, emojisai] and reaction.message.id == proposal_msg.id

            try:
                reaction, _ = await self.client.wait_for('reaction_add', timeout=120, check=check)
            except asyncio.TimeoutError:
                await ctx.send(f"{emojidongho} **Thời gian cầu hôn đã hết. {user_mention.mention} không phản ứng.**")
                return

            if str(reaction.emoji) == emojisai:
                await ctx.send(f"{user_mention.mention} **từ chối cầu hôn của {ctx.author.mention}.**")
                return

            # Cập nhật trạng thái kết hôn trong database
            cursor.execute(
                "UPDATE users SET marry = ? WHERE user_id = ?",
                (f"{ctx.author.mention} đã kết hôn với {user_mention.mention} bằng {name_ring} {emoji_ring}\nNgày kết hôn:  {current_time} id nhẫn: {ring_id}", author_id)
            )
            cursor.execute(
                "UPDATE users SET marry = ? WHERE user_id = ?",
                (f"{user_mention.mention} đã kết hôn với {ctx.author.mention} bằng {name_ring} {emoji_ring}\nNgày kết hôn:  {current_time} id nhẫn: {ring_id}", user_mention.id)
            )
            purchased_items_list = purchased_items.split(",")

            for i, item in enumerate(purchased_items_list):
                parts = item.split(":")
                if int(parts[0]) == ring_id:
                    parts[2] = str(int(parts[2]) - 1)
                    updated_item = ":".join(parts)
                    purchased_items_list[i] = updated_item

            # Cập nhật purchased_items trong cơ sở dữ liệu
            updated_purchased_items = ",".join(purchased_items_list)
            cursor.execute("UPDATE users SET purchased_items = ? WHERE user_id = ?", (updated_purchased_items, author_id))
            conn.commit()

            # --- Thêm đoạn kiểm tra và thêm role cho 2 người ---
            # marry_role = ctx.guild.get_role(1339482195907186770)
            # if marry_role:
            #     if marry_role not in ctx.author.roles:
            #         await ctx.author.add_roles(marry_role, reason="Marry role addition")
            #     partner_member = ctx.guild.get_member(user_mention.id)
            #     if partner_member and marry_role not in partner_member.roles:
            #         await partner_member.add_roles(marry_role, reason="Marry role addition")
            # -----------------------------------------------------

            embedmarry = discord.Embed(
                title="",
                description=f"# {emojigau} **LỄ CƯỚI** {emojigau}\nㅤ\n{ctx.author.mention} {nhanmarry} {user_mention.mention}\nㅤ\n{tuyenbo} **Ta tuyên bố từ nay 2 người chính thức trở thành vợ chồng. Hãy gắn bó yêu thương nhau và sống hạnh phúc đến suốt đời nhé!**\nㅤ\n{ngay} **Ngày cưới: {current_time}**\n# {linemarry}{linemarry}{linemarry}{linemarry}{linemarry}",
                color=discord.Color.from_rgb(160, 32, 240)
            )
            embedmarry.set_thumbnail(url="https://cdn.discordapp.com/attachments/1053799649938505889/1339752308849901670/hgtt_50.png")
            await ctx.send(embed=embedmarry)
        else:
            cursor.execute("SELECT marry, love_marry, setup_marry1, setup_marry2 FROM users WHERE user_id = ?", (author_id,))
            result = cursor.fetchone()
            marry_status = result[0]
            love_marry_points = result[1]
            setup_marry1 = result[2]
            setup_marry2 = result[3]
            # Dùng biểu thức chính quy để lấy các ID người dùng và biểu tượng cảm xúc  
            matches = re.findall(r'<@(\d+)>', marry_status)
            name_match = re.search(r'(?<=bằng\s)[^<]+', marry_status) 
            emoji_match = re.search(r'(<a?:\w+:\d+>)', marry_status)  
            date_match = re.search(r'Ngày kết hôn:  (\d{2}/\d{2}/\d{4})', marry_status)  

            if marry_status != '':
                if len(matches) == 2 and emoji_match and date_match:  
                    user1_id = f"<@{matches[0]}>"
                    user2_id = f"<@{matches[1]}>"
                    ring_name = name_match.group().strip()
                    emoji = emoji_match.group(0)
                    wedding_date = date_match.group(1)

                    # Tạo Embed  
                    embed = discord.Embed(
                        title=f"{bbtim} 𝗖𝗢𝗨𝗣𝗟𝗘 𝗜𝗡 𝗟𝗢𝗩𝗘 {bbtim}",
                        description=f"**{user1_id} {marry1} {user2_id}**\nㅤ\n{lich} **Ngày cưới: {wedding_date}**\nㅤ\n{cauhon} **Nhẫn Cưới: {ring_name}**\nㅤ\n{thanmat} **Điểm thân mật: {love_marry_points}**",
                        color=discord.Color.from_rgb(255, 0, 0)
                    )
                    if ring_name == "Nhẫn bạc đính đá cầu vồng":  #1
                        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1338238106381582378/1338757713420746814/nhan_1.png")
                    elif ring_name == "Nhẫn bạc đính đá tím":  #2
                        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1338238106381582378/1338758270579507270/nhann_10.png")
                    elif ring_name == "Nhẫn bạc đá lửa xanh hình bướm dễ thương":  #3
                        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1338238106381582378/1338758760474083355/hgtt_15.png")
                    elif ring_name == "Nhẫn bạc nơ hồng đính đá":  #4
                        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1338238106381582379/1338942460088287364/silver-diamond-ring-with-a-bow-in-pink-.png")
                    elif ring_name == "Nhẫn bạc đính đá hình hoa":  #5
                        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1339303289753309225/1339330049148584068/hgtt_36.png")
                    elif ring_name == "Nhẫn bạc đính đá trái tim":  #6
                        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1338238106381582379/1338942863035207892/diamond-silver--ring-light-pink-heart_3.png")
                    elif ring_name == "Nhẫn vàng trắng hoa đá ruby":  #7
                        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1338238106381582378/1338762864231452672/nhann_5.png")
                    elif ring_name == "Nhẫn vàng 14K đính đá":  #8
                        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1338238106381582378/1338764203367858226/13.png")
                    elif ring_name == "Nhẫn vàng trắng 14K đính đá xanh":  #9
                        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1338238106381582378/1338764518343442432/16.png")
                    elif ring_name == "Nhẫn vàng đính đá hồng":  #10
                        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1338238106381582379/1338770372740386877/pink-diamond-ring_2.png")
                    elif ring_name == "Nhẫn vàng trắng 14K đính ngọc trai":  #11
                        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1338238106381582378/1338765185476984924/nhan_5.png")
                    elif ring_name == "Nhẫn kim cương vàng trắng 18K vương miện":  #12
                        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1339303289753309225/1339325945273913447/discord_fake_avatar_decorations_1739390548435.gif")
                    elif ring_name == "Nhẫn kim cương vàng trắng 18K":  #13
                        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1339303289753309225/1339325946108444713/discord_fake_avatar_decorations_1739390496816.gif")
                    elif ring_name == "Nhẫn kim cương vàng trắng 18K giới hạn":  #14
                        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1339303289753309225/1339325945709858898/discord_fake_avatar_decorations_1739390521224.gif")
                    if setup_marry2 != '':
                        embed.add_field(name=f"{loihenuoc} Trạng thái:", value=f"{setup_marry2}", inline=False)
                    if setup_marry1 != '':
                        embed.set_image(url=f"{setup_marry1}")
                    await ctx.send(embed=embed)
            else:
                await ctx.send(f"{emojichamthan} **Lo kiếm tiền mua nhẫn rồi kết hôn đi đồ ế**")


    @marry.error
    async def marry_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = divmod(int(error.retry_after), 60)  # Chia cho 60 để có phút và giây
            formatted_time = f"{remaining_time[0]}m{remaining_time[1]}s"
            message = await ctx.send(f"{emojichamthan} | Còn `{formatted_time}` nữa bạn mới có thể kết hôn!")
            await asyncio.sleep(2)
            await message.delete()
            await ctx.message.delete()
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error


    @commands.command(description="setup hình ảnh marry")
    @is_allowed_channel_checkmarry()
    @set_marry()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def setmarry(self, ctx, image_marry: str = None, *, poem_marry: str = None):
        if await self.check_command_disabled(ctx):
            return
        if image_marry is None and poem_marry is None:
            await ctx.send("Hãy nhập zsetmarry `<url ảnh>` `<trạng thái>`")
            return 

        author_id = ctx.author.id
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT marry, setup_marry1, setup_marry2 FROM users WHERE user_id = ?", (author_id,))
        result = cursor.fetchone()

        if result is None:  
            await ctx.send(f"**{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
            return 
        
        marry_status = result[0]

        if marry_status is None or marry_status == '':
            await ctx.send("Một trong hai người chưa kết hôn.")
            return
        matches = re.findall(r'<@(\d+)>', marry_status)
        if len(matches) == 2:  
            user1_id = int(matches[0])
            user2_id = int(matches[1])
            if author_id == user1_id:
                if re.match(r'^(http|https)://', image_marry):  
                    if poem_marry:  
                        cursor.execute("UPDATE users SET setup_marry1 = ?, setup_marry2 = ? WHERE user_id = ? OR user_id = ?",   
                                    (image_marry, poem_marry, user1_id, user2_id))  
                        await ctx.send("Hình ảnh và trạng thái đã được cài đặt thành công.")  
                    else:  
                        cursor.execute("UPDATE users SET setup_marry1 = ? WHERE user_id = ? OR user_id = ?",   
                                    (image_marry, user1_id, user2_id))  
                        await ctx.send("Hình ảnh đã được cài đặt thành công.")  
                else:   
                    if poem_marry:   
                        poem_marry = f"{image_marry} {poem_marry}"  
                    
                    cursor.execute("UPDATE users SET setup_marry2 = ? WHERE user_id = ? OR user_id = ?",   
                                (poem_marry, user1_id, user2_id))  
                    await ctx.send("Trạng thái đã được cài đặt thành công.")  
                conn.commit()

    @setmarry.error
    async def setmarry_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = divmod(int(error.retry_after), 60)  # Chia cho 60 để có phút và giây
            formatted_time = f"{remaining_time[0]}m{remaining_time[1]}s"
            message = await ctx.send(f"{emojichamthan} | Còn `{formatted_time}` nữa bạn mới có thể cài đặt marry!")
            await asyncio.sleep(2)
            await message.delete()
            await ctx.message.delete()
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error


    @commands.command( description="Ly hôn với người bạn đã kết hôn")
    @is_allowed_channel_checkmarry()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def divorce(self, ctx):
        if await self.check_command_disabled(ctx):
            return
        if ctx.channel.id == 1215331218124574740 or ctx.channel.id == 1215331281878130738:
            return None

        author_id = ctx.author.id
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT marry FROM users WHERE user_id = ?", (author_id,))
        marry_status = cursor.fetchone()[0]

        # Dùng biểu thức chính quy để lấy các ID người dùng và biểu tượng cảm xúc  
        matches = re.findall(r'<@(\d+)>', marry_status)
        name_match = re.search(r'(?<=bằng\s)[^<]+', marry_status)
        emoji_match = re.search(r'(<a?:\w+:\d+>)', marry_status)
        date_match = re.search(r'Ngày kết hôn:  (\d{2}/\d{2}/\d{4})', marry_status)

        if marry_status == '':
            await ctx.send("Bạn chưa kết hôn nên không thể ly hôn.")
            return

        if len(matches) == 2 and emoji_match and date_match:
            user1_id = f"<@{matches[0]}>"
            user2_id = f"<@{matches[1]}>"
            ring_name = name_match.group().strip() if name_match else ""
            emoji = emoji_match.group(0)
            wedding_date = date_match.group(1)

        # Tạo embed thông báo
        embed = discord.Embed(
            title="",
            description=f"# {lyhon} **LY HÔN** {lyhon}\n{lyhon1} **Bạn và {user2_id} sẽ đường ai nấy đi. Bạn có chắc muốn thực hiện lệnh này? Hãy suy nghĩ thật kĩ nhé!**",
            color=discord.Color.from_rgb(255, 192, 203)
        )

        msg = await ctx.send(embed=embed)
        await msg.add_reaction(emojidung)
        await msg.add_reaction(emojisai)

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in [emojidung, emojisai] and reaction.message.id == msg.id

        try:
            reaction, _ = await self.client.wait_for('reaction_add', timeout=60, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Hết thời gian phản ứng. Thao tác ly hôn đã bị hủy.")
            return

        if str(reaction.emoji) == emojidung:
            # Thực hiện lệnh ly hôn trong database
            cursor.execute(
                "UPDATE users SET marry = '', love_marry = 0, setup_marry1 = '', setup_marry2 = '', bxh_love = 0 WHERE user_id = ? OR marry LIKE ?",
                (author_id, f"%{ctx.author.mention}%")
            )
            conn.commit()

            # Xác định thành viên đối tác (lấy id không khớp với ctx.author)
            partner_id = int(matches[0]) if int(matches[0]) != ctx.author.id else int(matches[1])
            partner_member = ctx.guild.get_member(partner_id)

            # Kiểm tra và xoá role có id 1339482195907186770 của cả 2 người nếu có
            divorce_role1 = ctx.guild.get_role(1339482195907186770)
            if divorce_role1:
                if divorce_role1 in ctx.author.roles:
                    await ctx.author.remove_roles(divorce_role1, reason="Divorce role removal")
                if partner_member and divorce_role1 in partner_member.roles:
                    await partner_member.remove_roles(divorce_role1, reason="Divorce role removal")

            # Kiểm tra và xoá role có id 1273868227457454111 của cả 2 người nếu có
            divorce_role2 = ctx.guild.get_role(1273868227457454111)
            if divorce_role2:
                if divorce_role2 in ctx.author.roles:
                    await ctx.author.remove_roles(divorce_role2, reason="Divorce role removal")
                if partner_member and divorce_role2 in partner_member.roles:
                    await partner_member.remove_roles(divorce_role2, reason="Divorce role removal")

            await ctx.send("✅ **Ly hôn thành công!** Bạn và đối tác đã chính thức độc thân.")
        elif str(reaction.emoji) == emojisai:
            await ctx.send("❌ **Lệnh ly hôn đã bị hủy bởi bạn.** Phew, may mắn lắm đó!")

    @divorce.error
    async def divorce_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = divmod(int(error.retry_after), 60)  # Chia cho 60 để có phút và giây
            formatted_time = f"{remaining_time[0]}m{remaining_time[1]}s"
            message = await ctx.send(f"{emojichamthan} | Còn `{formatted_time}` nữa bạn mới có thể ly hôn!")
            await asyncio.sleep(2)
            await message.delete()
            await ctx.message.delete
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error

    @commands.command( description="Tăng điểm love_marry cho bạn và đối tác")
    @is_allowed_channel_check()
    @commands.cooldown(1, 900, commands.BucketType.user)
    async def love(self, ctx):
        if await self.check_command_disabled(ctx):
            return
        forbidden = {1210296290026455140, 1210417888272318525, 1215331218124574740, 1215331281878130738}
        if ctx.channel.id in forbidden:
            return

        user_id = ctx.author.id
        conn_ = get_database_connection()
        cur_ = conn_.cursor()
        row = cur_.execute(
            "SELECT marry FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        marry_status = row[0] if row else ''
        if not marry_status:
            return await ctx.send(f"{emojichamthan}, **ế mốc ra thì lấy đâu tình yêu mà tăng điểm love**")

        row2 = cur_.execute(
            "SELECT love_so, love_time FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        counter, threshold = row2 if row2 else (0, None)

        if threshold is None:
            threshold = random.choice(self.confirm_threshold_choices)
            cur_.execute(
                "UPDATE users SET love_time = ? WHERE user_id = ?",
                (threshold, user_id)
            )
            conn_.commit()

        if counter + 1 > threshold:
            confirmed = False
            view = View(timeout=30)
            button = Button(label="Xác nhận love", style=discord.ButtonStyle.danger)
            view.add_item(button)

            async def confirm_cb(interaction: discord.Interaction):
                nonlocal confirmed
                if interaction.user.id != user_id:
                    return await interaction.response.send_message(
                        "Chỉ người thực hiện lệnh mới xác nhận.", ephemeral=True
                    )
                confirmed = True
                await interaction.response.defer()

                partner = cur_.execute(
                    "SELECT user_id, love_marry FROM users WHERE marry LIKE ? AND user_id != ?",
                    (f"%{ctx.author.mention}%", user_id)
                ).fetchone()
                if partner:
                    partner_id, pts = partner
                    new_pts = pts + 1
                    # Cập nhật điểm và reset counter
                    cur_.execute(
                        "UPDATE users SET love_marry = ? WHERE user_id IN (?, ?)",
                        (new_pts, user_id, partner_id)
                    )
                    cur_.execute(
                        "UPDATE users SET love_so = 0, love_time = ? WHERE user_id = ?",
                        (random.choice(self.confirm_threshold_choices), user_id)
                    )
                    conn_.commit()

                    # Xóa prompt và gửi embed kết quả
                    await interaction.message.delete()
                    embed = discord.Embed(color=discord.Color.from_rgb(255, 192, 203))
                    embed.add_field(
                        name="",
                        value=(f"{emojitimhong} ***{ctx.author.mention} nói iu <@{partner_id}> rất nhiều. "
                               f"2 bạn có*** __***{new_pts}***__ ***điểm love!*** {emojitimhong}"),
                        inline=False
                    )
                    await interaction.followup.send(embed=embed)

                view.stop()

            button.callback = confirm_cb

            prompt = await ctx.send(
                view=view
            )
            await view.wait()
            if not confirmed:
                await prompt.delete()

        else:
            # Auto tăng love
            cur_.execute(
                "UPDATE users SET love_marry = love_marry + 1, love_so = love_so + 1 "
                "WHERE user_id = ? OR marry LIKE ?",
                (user_id, f"%{ctx.author.mention}%")
            )
            conn_.commit()
            new_points = cur_.execute(
                "SELECT love_marry FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()[0]

            parts = marry_status.split()
            mention1, mention2 = parts[0], parts[5]
            partner = mention2 if ctx.author.mention == mention1 else mention1

            embed = discord.Embed(color=discord.Color.from_rgb(255, 192, 203))
            embed.add_field(
                name="",
                value=(f"{emojitimhong} ***{ctx.author.mention} nói iu {partner} rất nhiều. "
                       f"2 bạn có*** __***{new_points}***__ ***điểm love!*** {emojitimhong}"),
                inline=False
            )
            await ctx.send(embed=embed)

    @love.error
    async def love_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            mins, secs = divmod(int(error.retry_after), 60)
            msg = await ctx.send(
                f"{emojichamthan} | Còn `{mins}m{secs}s` nữa bạn mới có thể nói lời yêu tiếp!"
            )
            await asyncio.sleep(2)
            await msg.delete()
            await ctx.message.delete()
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error

    @commands.command(description="Nâng cấp nhẫn cưới")
    @is_allowed_channel_checkmarry()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def upgrade_nhan(self, ctx, ring_id: int):
        if await self.check_command_disabled(ctx):
            return
        if ctx.channel.id == 1215331218124574740 or ctx.channel.id == 1215331281878130738:
            return None
        author_id = ctx.author.id

        if not is_registered(author_id):
            await ctx.send(f"**{ctx.author.display_name}**, bạn chưa đăng ký. Dùng `zdk` viết liền để đăng ký tài khoản.")
            return
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT marry, purchased_items FROM users WHERE user_id = ?", (author_id,))
        result = cursor.fetchone()
        marry_status = result[0]
        purchased_items = result[1]

        if not marry_status:
            await ctx.send(f"{emojichamthan}, **ế mốc ra thì lấy đâu nhẫn cưới mà nâng cấp**")
            return

        if not purchased_items:
            await ctx.send(f"{emojichamthan}, **bạn chưa mua nhẫn nào cả**")
            return

        if ring_id not in [int(item.split(":")[0]) for item in purchased_items.split(",")]:
            await ctx.send(f"{emojichamthan}, **bạn chưa mua nhẫn này**")
            return

        cursor.execute("SELECT marry FROM users WHERE user_id = ?", (author_id,))
        marry_status = cursor.fetchone()[0]
        matches = re.findall(r'<@(\d+)>', marry_status)
        name_match = re.search(r'(?<=bằng\s)[^<]+', marry_status)
        emoji_match = re.search(r'(<a?:\w+:\d+>)', marry_status)
        date_match = re.search(r'Ngày kết hôn:  (\d{2}/\d{2}/\d{4})', marry_status)
        ring_id_match = re.search(r'id nhẫn: (\d+)', marry_status)

        if len(matches) == 2 and emoji_match and date_match:
            user1_id = f"<@{matches[0]}>"
            user2_id = f"<@{matches[1]}>"
            ring_name = name_match.group().strip()
            emoji = emoji_match.group(0)
            wedding_date = date_match.group(1)
            current_ring_id = int(ring_id_match.group(1))

        if ring_id <= current_ring_id:
            await ctx.send(f"{emojichamthan}, **bạn không thể nâng cấp nhẫn cưới hơn nhẫn hiện tại**")
            return

        items = purchased_items.split(",")
        for i, item in enumerate(items):
            parts = item.split(":")
            if int(parts[0]) == ring_id:
                parts[2] = str(int(parts[2]) - 1)
                updated_item = ":".join(parts)
                items[i] = updated_item
        updated_purchased_items = ",".join(items)

        name_ring = ""
        emoji_ring = ""
        for item in items:
            parts = item.split(":")
            if int(parts[0]) == ring_id:
                emoji_string = item.split("<")[1].split(">")[0]
                name_ring = parts[1]
                emoji_ring = f"<{emoji_string}>"
                break

        cursor.execute("UPDATE users SET purchased_items = ? WHERE user_id = ?", (updated_purchased_items, author_id))
        cursor.execute("UPDATE users SET marry = ? WHERE user_id = ?", (f"{user1_id} đã kết hôn với {user2_id} bằng {name_ring} {emoji_ring}\nNgày kết hôn:  {wedding_date} id nhẫn: {ring_id}", author_id))
        cursor.execute("UPDATE users SET marry = ? WHERE user_id = ?", (f"{user2_id} đã kết hôn với {user1_id} bằng {name_ring} {emoji_ring}\nNgày kết hôn:  {wedding_date} id nhẫn: {ring_id}", matches[1]))
        conn.commit()

        # Tạo embed thông báo
        embed = discord.Embed(
            title="",
            description=f"# {lich} **UPGRADE RING** {lich}\n{cauhon} **Bạn đã nâng cấp {ring_name} thành {name_ring}**",
            color=discord.Color.from_rgb(255, 192, 203)
        )

        if name_ring == "Nhẫn bạc đính đá cầu vồng": #1
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1338238106381582378/1338757713420746814/nhan_1.png")  
        elif name_ring == "Nhẫn bạc đính đá tím": #2
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1338238106381582378/1338758270579507270/nhann_10.png")
        elif name_ring == "Nhẫn bạc đá lửa xanh hình bướm dễ thương": #3
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1338238106381582378/1338758760474083355/hgtt_15.png")
        elif name_ring == "Nhẫn bạc nơ hồng đính đá": #4
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1338238106381582379/1338942460088287364/silver-diamond-ring-with-a-bow-in-pink-.png")
        elif name_ring == "Nhẫn bạc đính đá hình hoa": #5
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1339303289753309225/1339330049148584068/hgtt_36.png")
        elif name_ring == "Nhẫn bạc đính đá trái tim": # 6
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1338238106381582379/1338942863035207892/diamond-silver--ring-light-pink-heart_3.png")
        elif name_ring == "Nhẫn vàng trắng hoa đá ruby": # 7
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1338238106381582378/1338762864231452672/nhann_5.png")
        elif name_ring == "Nhẫn vàng 14K đính đá": #8
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1338238106381582378/1338764203367858226/13.png")
        elif name_ring == "Nhẫn vàng trắng 14K đính đá xanh": # 9
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1338238106381582378/1338764518343442432/16.png")
        elif name_ring == "Nhẫn vàng đính đá hồng": #10
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1338238106381582379/1338770372740386877/pink-diamond-ring_2.png")
        elif name_ring == "Nhẫn vàng trắng 14K đính ngọc trai": #11
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1338238106381582378/1338765185476984924/nhan_5.png")
        elif name_ring == "Nhẫn kim cương vàng trắng 18K vương miện": #12
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1339303289753309225/1339325945273913447/discord_fake_avatar_decorations_1739390548435.gif")
        elif name_ring == "Nhẫn kim cương vàng trắng 18K": #13
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1339303289753309225/1339325946108444713/discord_fake_avatar_decorations_1739390496816.gif")
        elif name_ring == "Nhẫn kim cương vàng trắng 18K giới hạn": #14
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1339303289753309225/1339325945709858898/discord_fake_avatar_decorations_1739390521224.gif")

        await ctx.send(embed=embed)

    @upgrade_nhan.error
    async def upgrade_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = divmod(int(error.retry_after), 60)  # Chia cho 60 để có phút và giây
            formatted_time = f"{remaining_time[0]}m{remaining_time[1]}s"
            message = await ctx.send(f"{emojichamthan} | Còn `{formatted_time}` nữa bạn mới có thể nâng cấp nhẫn!")
            await asyncio.sleep(2)
            await message.delete()
            await ctx.message.delete()
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error

    @commands.command(description="Nâng cấp điểm love")
    @is_bot_owner()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def setlove(self, ctx, love_marry_points: int = None, user_mention: discord.User = None):
        if await self.check_command_disabled(ctx):
            return
        if user_mention is None or love_marry_points is None:
            await ctx.send("Nhập thiếu thông tin.")
            return
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT marry FROM users WHERE user_id = ?", (user_mention.id,))
        marry_status = cursor.fetchone()[0]

        if marry_status == '':
            await ctx.send("Người này chưa kết hôn.")
            return
        cursor.execute("UPDATE users SET love_marry = love_marry + ? WHERE user_id = ? OR marry LIKE ?", (love_marry_points, user_mention.id, f"%{user_mention.mention}%"))
        conn.commit()
        conn.close()
        await ctx.send(f"**Đã + {love_marry_points} {thanmat} cho {user_mention.mention}**")
    
    @setlove.error
    async def setlove_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = divmod(int(error.retry_after), 60)  # Chia cho 60 để có phút và giây
            formatted_time = f"{remaining_time[0]}m{remaining_time[1]}s"
            message = await ctx.send(f"{emojichamthan} | Còn `{formatted_time}` nữa bạn mới có thể cập nhật điểm love!")
            await asyncio.sleep(2)
            await message.delete()
            await ctx.message.delete()
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise

async def setup(client):
    await client.add_cog(Marry(client))