import asyncio
import random
import typing
import discord
import sqlite3
from datetime import datetime, timedelta
from discord.ext import commands, tasks
import json
from discord.ui import Button, View
import pytz
import datetime
from Commands.Mod.list_emoji import list_emoji
from utils.checks import is_bot_owner, is_admin, is_mod

conn = sqlite3.connect('economy.db', isolation_level=None)
conn.execute('pragma journal_mode=wal')
cursor = conn.cursor()

# Tạo bảng ve_database nếu chưa tồn tại
cursor.execute('''CREATE TABLE IF NOT EXISTS phan_thuong (
                  id INTEGER PRIMARY KEY,
                  name_phanthuong TEXT NOT NULL,
                  soluong_phanthuong INTEGER NOT NULL,
                  emoji_phanthuong INTEGER NOT NULL
               )''')
conn.commit()


def is_registered(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None


def is_allowed_channel():
    async def predicate(ctx):
        allowed_channel_id = 1147035278465310720
        if ctx.channel.id != allowed_channel_id:
            message = await ctx.reply(f"{list_emoji.tick_check} **Dùng lệnh** **`zmoqua`** **để mở vé** [__**ở đây**__](<https://discord.com/channels/832579380634451969/1147035278465310720>)")
            await asyncio.sleep(10)
            await message.delete()
            await ctx.message.delete()
            return False
        return True
    return commands.check(predicate)

def is_allowed_channel_kc():
    async def predicate(ctx):
        allowed_channel_ids = [993153068378116127, 1147035278465310720]
        if ctx.channel.id not in allowed_channel_ids:
            message = await ctx.reply(f"{list_emoji.tick_check} **Dùng lệnh** **`zmoqua kc`** **để mở vé kim cương** [__**ở đây**__](<https://discord.com/channels/832579380634451969/1147035278465310720>) **hoặc** [__**ở đây**__](<https://discord.com/channels/832579380634451969/993153068378116127>)")
            await asyncio.sleep(10)
            await message.delete()
            await ctx.message.delete()
            return False
        return True
    return commands.check(predicate)


def is_allowed_channel_check():
    async def predicate(ctx):
        allowed_channel_ids = [1273768834830041301, 1273769137985818624, 993153068378116127, 1026627301573677147, 1035183712582766673, 1090897131486842990, 1213122881802997770, 1147355133622108262, 1295144686536888340, 1207593935359320084, 1147035278465310720]
        if ctx.channel.id not in allowed_channel_ids:
            await ctx.send(f"{list_emoji.tick_check} **Dùng lệnh** **`zinv`** [__**ở đây**__](<https://discord.com/channels/832579380634451969/1147355133622108262>)")
            return False
        return True
    return commands.check(predicate)

def is_marry():
    async def predicate(ctx):
        role_marry = any(role.id == 1339482195907186770 for role in ctx.author.roles)
        return role_marry
    return commands.check(predicate)

def is_daily_channel():
    async def predicate(ctx):
        allowed_channel_id = 1147355133622108262
        if ctx.channel.id != allowed_channel_id:
            await ctx.send(f"{list_emoji.tick_check} **Dùng lệnh** **`zdaily`** [__**ở đây**__](<https://discord.com/channels/832579380634451969/1147355133622108262>)")
            return False
        return True
    return commands.check(predicate)

def is_guild_owner_or_bot_owner():
    async def predicate(ctx):
        return ctx.author == ctx.guild.owner or ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222
    return commands.check(predicate)

def is_staff():
    async def predicate(ctx):
        guild_owner = ctx.author == ctx.guild.owner
        bot_owner = ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222
        specific_role = any(
            role.id == 1113463122515214427 for role in ctx.author.roles)
        return guild_owner or bot_owner or specific_role
    return commands.check(predicate)


def get_superscript(n):
    superscripts = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    return str(n).translate(superscripts)

married = "<a:emoji_31:1271993759378440192>"
fishcoin = "<:fishcoin:1213027788672737300>"
emojidung = "<:sushi_thanhcong:1215621188059926538> "
emojisai = "<:hgtt_sai:1186839020974657657>"
noicom = "<:sushi_nau:1215607752005652480>"
dongho = "<a:hgtt_timee:1159077258535907328>"
tickdung = "<:hgtt_dung:1186838952544575538>"
quaxanh = "<:hgtt_quaxanhdatroi:1202482871063805992>"
quatim = "<:hgtt_quatim:1202482829397860382>"
quasua = "<:hgtt_qua:1179397064426278932>"
quataocherry = "<:ticketqua3:1198800796054208593>"
quasushi = "<:ss:1214794754542276648>"
quacam = "<:hgtt_qua:1170591248256618506>"
quahongdong = "<a:hgtt_qua:1180122434746200104>"
cakhoc = "<:khongdutien:1211921509514477568>"
congthuc = "<a:congthuc:1214570098879373343>"
daily_streak1 = "<:lich7mau:1417899858160910509>"
daily_streak2 = "<:lich:1313829453826359398>"
chamthan = "<:chamthann:1233135104281411757>"
nhayvang = "<a:dotvang:1215606222942896128>"
nhaysao = "<a:nhaysao:1284496637623926784>"
quatienpink = "<:qua:1242529922870673528>"
ngoisao = "<a:ngoisao:1284490593829130250>"
momo = "<:momo:1180104032208048209>"
time_daily = "<:dongho7mau:1417899872748572722>"
daily_love = "<a:daily_love:1314586830082932806>"
chamthanvang = "<:chamthanvang:1331908568521248779>"



# Emoji quà
kco = "<:0noel_hgtt_chamthan:1313775980141350954>"
tienvnd = "<:hgtt_tien_vnd:1235115910445142037>"
quatienowo_hong = "<:quadaily7mau:1417899865341694132>"
nhayxanh = "<a:dotxanh:1215606225492774993>"
nhayhong = "<a:dothong:1215606220367466506>"
nhayvang = "<a:nhayvang1:1331714375370932336>"
nhayhong1 = "<a:nhayhong:1331714335919046657>"
phaohoa = "<a:phaohoatron:1331714384107671642>"
quatienowo = "<a:quaxanhowo:1417886430759223477>"
quatienhong ="<a:quahongpink:1417886441828257895>"
quathantai = "<:vekc:1146756758665175040>"
quaran = "<:qua_ran:1331708134305304716>"
quahuongduong = "<:qua_huongduong:1331708102579326976>"
quahatde = "<:qua_hatde:1331708108837355560>"
quahoamai = "<:qua_hoamai:1331708126977724539>"
quahoadao = "<:qua_hoadao:1331708119839146045>"
quakco = "<:qua_kco:1331708141917966528>"
quanglieu = "<:qua_nglieu:1331708149240954891>"
meotrasua = "<:meotrasua:1331713432822747166>"
quanuhon = "<a:hgtt_decor_tim:1281600533601325137>"
quaxu = "<:quaxu:1417886456134762547>"
qualongden = "<:qualongden:1417887284493156413>"
quacainit = "<:quacainit:1417887976666431488>"
dungset = '<a:dung1:1340173892681072743>'
saiset = '<a:sai1:1340173872535703562>'
muitenxeo = "<a:muitenxeo:1417883887962554399>"
quabicuop = "<a:quabicuop:1417887960925212692>"
dotvang = "<a:dotvang:1417891081881915533>"
quavang = "<:quavang:1417887944542523533>"
qualongden2 = "<:qualongden2:1417892569525780620>"
dotmau = "<a:dotmau:1417892591805923338>"

longdentho = '<:1_longdentho:1418267182705545317>'
longdensao = '<a:2_longdensao:1418267192654561320>'
longdengaudau = '<:3_longdengaudau:1418267200674070540>'
longdenga = '<:4_longdenga:1418267223612588092>'
longdenmarsupilami = '<a:5_longdenmarsupilami:1418267208236138608>'
longdenca = '<:6_longdenca:1418267234047889418>'
longdendoremi = '<:7_longdendoremi:1418267248916697200>'
longdenlan = '<:8_longdendaulan:1418267260640039044>'
longdenheo = '<:9_longdenheo:1418267269766840321>'
longdenpikachu = '<:10_longdenpikachu:1418267281401839828>'
longdenlobby = '<a:11_longdenlobby:1418267300913615041>'
longdencaptain = '<:12_longdencaptain:1418267289404571658>'
longdendoremon = '<a:13_longdendoremon:1418267327165759569>'
longdennguoinhen = '<:14_longdennguoinhen:1418267335554240662>'
longdenbuom = '<:15_longdenbuom:1418267344316137492>'
quaylongden = '<a:quaylongden:1418269667461431456>'

# class MoquaView(discord.ui.View):
#     def __init__(self, enable_buttons, phan_thuong, timeout: float = 20.0):
#         super().__init__(timeout=timeout)
#         self.enable_buttons = enable_buttons
#         self.phan_thuong = phan_thuong
#         self.message = None

#     async def interaction_check(self, interaction: discord.Interaction) -> bool:
#         if interaction.user.id == self.enable_buttons:
#             return True
#         else:
#             await interaction.response.send_message("Nút mở quà này của người khác", ephemeral=True)
#             return False

#     async def disable_all_items(self):
#         for item in self.children:
#             item.disabled = True
#         await self.message.edit(view=self)

#     @discord.ui.button(
#         label="Mở vé kim cương",
#         style=discord.ButtonStyle.green,
#         emoji="<:ga_lixitet:1331667458024669335>",
#         custom_id="rutlixi",
#         disabled=False
#         )
#     async def rutlixi(self, interaction: discord.Interaction, button: discord.ui.Button):
#         await self.disable_all_items()
#         cursor.execute("SELECT balance, xu_hlw FROM users WHERE user_id = ?", (interaction.user.id,))
#         result = cursor.fetchone()
#         balance = result[0]
#         xu_hlw = result[1]

#         phan_thuong = self.phan_thuong
#         if phan_thuong[0] in {1, 2, 3}:
#             embed = discord.Embed(
#                 title=f"{quathantai} **Chúc mừng {interaction.user.mention}, bạn trúng phần quà** **{phan_thuong[1]}** {phan_thuong[3]}",
#                 description="",
#                 color=discord.Color.from_rgb(158,230,255),
#             )
#             embed.set_thumbnail(
#                 url=""
#             )
#             await interaction.response.send_message(embed=embed)
#         elif phan_thuong[0] == 4:   
#             embed = discord.Embed(
#                 title=f"{quathantai} **Chúc mừng {interaction.user.mention}, bạn trúng phần quà** **{phan_thuong[1]}** {phan_thuong[3]}",
#                 description="",
#                 color=discord.Color.from_rgb(158,230,255),
#             )
#             embed.set_thumbnail(
#                 url=""
#             )
#             await interaction.response.send_message(embed=embed)
#         elif phan_thuong[0] == 5:
#             embed = discord.Embed(
#                 title=f"",
#                 description=f"# {quathantai} **Chúc mừng {interaction.user.mention}, bạn trúng phần quà** **{phan_thuong[1]}** {phan_thuong[3]}\n-# {muitenxeo} Sưu tầm đủ 5 labubu để nhận quà 20K {phan_thuong[3]} nha",
#                 color=discord.Color.from_rgb(158,230,255),
#             )
#             embed.set_thumbnail(
#                 url="https://cdn.discordapp.com/attachments/1211199649667616768/1417831679040684072/discord_fake_avatar_decorations_1758107598903.gif"
#             )
#             await interaction.response.send_message(embed=embed)
#         elif phan_thuong[0] in {6, 7, 8, 9, 10}:
#             await interaction.response.send_message(
#                 f"{quatienowo} **Chúc mừng {interaction.user.mention}, bạn trúng phần quà** {nhayxanh}**{phan_thuong[1]}**{nhayxanh} {phan_thuong[3]}"
#             )
#         elif phan_thuong[0] == 11:
#             await interaction.response.send_message(
#                 f"{quatienhong} **Chúc mừng {interaction.user.mention}**, **bạn trúng phần quà** {nhayhong}**{phan_thuong[1]}**{nhayhong} {phan_thuong[3]}"
#             )
#         elif phan_thuong[0] == 12:
#             await interaction.response.send_message(
#                 f"{quatienhong} **Chúc mừng {interaction.user.mention},  bạn trúng phần quà** {nhayhong}**{phan_thuong[1]}**{nhayhong} {phan_thuong[3]}"
#             )
#         elif phan_thuong[0] == 13:
#             await interaction.response.send_message(
#                 f"{quaxu} **Chúc mừng {interaction.user.mention},  bạn trúng quà** {nhayhong}**{phan_thuong[1]}**{nhayhong} {phan_thuong[3]}")

class Velenh(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.reset_daily_task.start()
        self.guild = None
        self.vevang = None
        self.vekc = None
        self.dk = None
        self.clock = None
        self.users = None
        self.inv = None
        self.chamthan = None
        self.nauan = None
        self.tickdunghong = None


    async def cog_load(self):
        """Called when the cog is loaded - Discord.py 2.0+ recommended way"""
        await self.init_emojis()

    async def init_emojis(self):
        """Khởi tạo emoji với xử lý lỗi tốt hơn"""
        try:
            # Thử lấy guild
            self.guild = self.client.get_guild(1090136467541590066)
            
            if self.guild is None:
                print(f"⚠️ Warning: Guild 1090136467541590066 not found. Using default emojis.")
                return
            
            # Dictionary mapping emoji IDs với emoji mặc định fallback
            emoji_mappings = {
                1192461054131847260: ("vevang", "🎫"),
                1146756758665175040: ("vekc", "💎"),
                1181378307548250163: ("users", "👥"),
                1181400074127945799: ("dk", "📝"),
                1159077258535907328: ("inv", "📦"),
                1159077258535907328: ("clock", "⏰"),
                1179452469017858129: ("chamthan", "❗"),
                1192458078294122526: ("tienhatgiong", "💰"),
                1192458078294122526: ("nauan", "🍳"),
                1186838952544575538: ("tickdunghong", "✅")
            }
            
            # Thử fetch từng emoji
            for emoji_id, (attr_name, default_emoji) in emoji_mappings.items():
                try:
                    emoji = await self.guild.fetch_emoji(emoji_id)
                    setattr(self, attr_name, emoji)
                except discord.NotFound:
                    print(f"⚠️ Emoji {emoji_id} not found, using default for {attr_name}")
                    setattr(self, attr_name, default_emoji)
                except discord.HTTPException as e:
                    print(f"⚠️ HTTP error fetching emoji {emoji_id}: {e}")
                    setattr(self, attr_name, default_emoji)
                    
        except Exception as e:
            print(f"⚠️ Error in init_emojis: {e}. Using all default emojis.")

    # async def init_emojis(self):
    #     self.guild = self.client.get_guild(1090136467541590066)
    #     self.vevang = await self.guild.fetch_emoji(1192461054131847260)
    #     self.vekc = await self.guild.fetch_emoji(1146756758665175040)
    #     self.users = await self.guild.fetch_emoji(1181378307548250163)
    #     self.dk = await self.guild.fetch_emoji(1181400074127945799)
    #     self.inv = await self.guild.fetch_emoji(1159077258535907328)
    #     self.clock = await self.guild.fetch_emoji(1159077258535907328)
    #     self.chamthan = await self.guild.fetch_emoji(1179452469017858129)
    #     self.tangqua = await self.guild.fetch_emoji(1170709400470687806)
    #     self.quadaily = await self.guild.fetch_emoji(1179397064426278932)
    #     self.nauan = await self.guild.fetch_emoji(1192458078294122526)
    #     self.tickdunghong = await self.guild.fetch_emoji(1186838952544575538)

    async def init_drop_rates(self, user_id):
        """Khởi tạo bảng drop_rates cho từng user nếu chưa tồn tại"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_drop_rates (
                user_id INTEGER,
                item_id INTEGER,
                rate REAL DEFAULT 1.0,
                last_reset DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_opens INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, item_id)
            )
        """)
        
        # Khởi tạo drop rates cho tất cả phần thưởng của user này
        for i in range(1, 33):  # ID 1-32
            if i <= 5:  # Vé kim cương
                initial_rate = 0.5 if i == 3 else 1.0  # ID 3 có tỷ lệ thấp hơn
            else:  # Vé vàng
                initial_rate = 1.0
            cursor.execute("""
                INSERT OR IGNORE INTO user_drop_rates (user_id, item_id, rate) VALUES (?, ?, ?)
            """, (user_id, i, initial_rate))
        conn.commit()

    async def get_weighted_selection(self, phan_thuong_list, loai_ve, user_id):
        """Lấy phần thưởng dựa trên dynamic drop rates của từng user"""
        # Lấy drop rates từ database cho user này
        ids = [pt[0] for pt in phan_thuong_list]
        placeholders = ','.join('?' * len(ids))
        cursor.execute(f"SELECT item_id, rate FROM user_drop_rates WHERE user_id = ? AND item_id IN ({placeholders})", 
                      [user_id] + ids)
        rates_data = dict(cursor.fetchall())
        
        # Tạo weights dựa trên drop rates với bias cho ID 20-32
        weights = []
        for pt in phan_thuong_list:
            base_rate = rates_data.get(pt[0], 1.0)
            
            # Tăng weight cho ID 20-32 (tăng 2.0x tỷ lệ)
            if 20 <= pt[0] <= 32:
                enhanced_rate = base_rate * 2.0
            else:
                enhanced_rate = base_rate
                
            weights.append(enhanced_rate)
        
        # Chọn phần thưởng theo trọng số
        selected = random.choices(phan_thuong_list, weights=weights)[0]
        
        # Cập nhật drop rates sau khi chọn
        await self.update_drop_rates(selected[0], loai_ve, user_id)
        
        return selected

    async def update_drop_rates(self, selected_id, loai_ve, user_id):
        """Cập nhật drop rates sau khi mở quà cho từng user"""
        if loai_ve == "vang":  # ID 6-32
            # Giảm rate của món vừa trúng cho user này
            cursor.execute("""
                UPDATE user_drop_rates 
                SET rate = CASE 
                    WHEN rate > 0.1 THEN rate * 0.8 
                    ELSE 0.1 
                END,
                total_opens = total_opens + 1
                WHERE user_id = ? AND item_id = ?
            """, (user_id, selected_id))
            
            # Tăng rate của các món khác trong range 6-32 cho user này
            cursor.execute("""
                UPDATE user_drop_rates 
                SET rate = CASE 
                    WHEN rate < 2.0 THEN rate * 1.05 
                    ELSE 2.0 
                END
                WHERE user_id = ? AND item_id >= 6 AND item_id <= 32 AND item_id != ?
            """, (user_id, selected_id))
        
        # Cập nhật tổng số lần mở cho user này (dùng item_id = 1 làm counter)
        cursor.execute("""
            UPDATE user_drop_rates 
            SET total_opens = total_opens + 1 
            WHERE user_id = ? AND item_id = 1
        """, (user_id,))
        conn.commit()
        
        # Kiểm tra nếu cần reset (sau 10 lần mở)
        cursor.execute("SELECT total_opens FROM user_drop_rates WHERE user_id = ? AND item_id = 1", (user_id,))
        result = cursor.fetchone()
        total_opens = result[0] if result else 0
        if total_opens >= 10:
            await self.reset_drop_rates(user_id)

    async def reset_drop_rates(self, user_id):
        """Reset drop rates về mức ban đầu cho từng user"""
        cursor.execute("""
            UPDATE user_drop_rates 
            SET rate = CASE 
                WHEN item_id = 3 THEN 0.5 
                WHEN item_id >= 1 AND item_id <= 5 THEN 1.0 
                ELSE 1.0 
            END,
            total_opens = 0,
            last_reset = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (user_id,))
        conn.commit()

    async def check_command_disabled(self, ctx):  
        guild_id = str(ctx.guild.id)  
        command_name = ctx.command.name.lower()  
        if guild_id in self.client.get_cog('Toggle').toggles:  
            if command_name in self.client.get_cog('Toggle').toggles[guild_id]:  
                if ctx.channel.id in self.client.get_cog('Toggle').toggles[guild_id][command_name]:  
                    await ctx.send(f"Lệnh `{command_name}` đã bị tắt ở kênh này.")  
                    return True  
        return False 

    @commands.hybrid_command(description="xem có bao nhiêu vé")
    @is_bot_owner()
    async def check(self, ctx):
        if is_registered(ctx.author.id):
            cursor.execute(
                "SELECT num_gold_tickets_available, num_diamond_tickets_available, quantity_tickets FROM ve_database WHERE id = ?", (1,))
            ve_db_result = cursor.fetchone()

            if ve_db_result:
                num_gold_tickets_available = ve_db_result[0]
                num_diamond_tickets_available = ve_db_result[1]
                quantity_tickets = ve_db_result[2]
                soluongconlai = 128 - quantity_tickets
                embed = discord.Embed(
                    title=f"", color=discord.Color.magenta())
                embed.add_field(
                    name="", value=f"Số vé còn lại trong ngày: {soluongconlai} {list_emoji.pinkcoin}", inline=False)
                embed.add_field(
                    name="", value=f"Số vé còn lại trong tháng: {num_gold_tickets_available} {self.vevang} và {num_diamond_tickets_available} {self.vekc}", inline=False)
                await ctx.send(embed=embed, ephemeral=True)
            else:
                return None
        else:
            await ctx.send(f"{self.dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")

    @commands.command(description="Xem bảng phần thưởng")
    @is_bot_owner()
    async def phanthuong(self, ctx):
        """Lệnh xem tất cả phần thưởng trong bảng phan_thuong"""
        cursor.execute("SELECT id, name_phanthuong, soluong_phanthuong FROM phan_thuong ORDER BY id")
        phan_thuong_list = cursor.fetchall()
        
        if not phan_thuong_list:
            await ctx.send("Bảng phần thưởng trống!")
            return
        
        # Tìm độ dài tên dài nhất để căn chỉnh
        max_name_length = max(len(name) for _, name, _ in phan_thuong_list)
        
        # Tạo nội dung code block
        result_text = "📦 BẢNG PHẦN THƯỞNG\n\n"
        
        for reward_id, name, quantity in phan_thuong_list:
            # Format với padding để căn chỉnh số lượng thẳng hàng
            result_text += f"{reward_id:2d}. {name:<{max_name_length}} - Còn: {quantity:>6,}\n"
        
        # Thêm thông tin tổng kết
        total_items = len(phan_thuong_list)
        total_quantity = sum(quantity for _, _, quantity in phan_thuong_list)
        
        result_text += f"\nTổng cộng: {total_items} loại • {total_quantity:,} phần thưởng còn lại"
        
        # Bọc toàn bộ trong code block
        final_message = f"```\n{result_text}\n```"
        
        # Chia nhỏ message nếu quá dài (Discord giới hạn 2000 ký tự)
        if len(final_message) > 1900:
            # Gửi từng phần với code block
            lines = result_text.split('\n')
            current_msg = "BẢNG PHẦN THƯỞNG\n\n"
            
            for line in lines[2:]:  # Bỏ qua header
                if len(f"```\n{current_msg + line + chr(10)}\n```") > 1900:
                    await ctx.send(f"```\n{current_msg}\n```")
                    current_msg = line + '\n'
                else:
                    current_msg += line + '\n'
            
            if current_msg.strip():
                await ctx.send(f"```\n{current_msg}\n```")
        else:
            await ctx.send(final_message)

    @commands.command(description="Xem drop rates hiện tại của một user")
    @is_bot_owner()
    async def droprates(self, ctx, member: discord.Member = None):
        """Lệnh xem drop rates hiện tại của user"""
        target_user = member or ctx.author
        user_id = target_user.id
        
        cursor.execute("SELECT item_id, rate, total_opens FROM user_drop_rates WHERE user_id = ? ORDER BY item_id", (user_id,))
        rates_data = cursor.fetchall()
        
        if not rates_data:
            await ctx.send(f"User {target_user.display_name} chưa có dữ liệu drop rates!")
            return
            
        # Tạo message hiển thị
        result_text = f"📊 DROP RATES CỦA {target_user.display_name.upper()}\n\n"
        result_text += "🔹 VÉ KIM CƯƠNG (ID 1-5):\n"
        
        for item_id, rate, opens in rates_data:
            if item_id <= 5:
                result_text += f"  ID {item_id:2d}: {rate:5.2f}x\n"
        
        result_text += "\n🔹 VÉ VÀNG (ID 6-32):\n"
        vang_rates = []
        for item_id, rate, opens in rates_data:
            if 6 <= item_id <= 32:
                vang_rates.append(f"ID{item_id:2d}:{rate:4.2f}x")
        
        # Chia thành nhiều dòng, mỗi dòng 6 items
        for i in range(0, len(vang_rates), 6):
            result_text += "  " + " ".join(vang_rates[i:i+6]) + "\n"
        
        # Thêm thông tin tổng (lấy từ item_id = 1)
        total_opens = next((opens for item_id, rate, opens in rates_data if item_id == 1), 0)
        result_text += f"\nTổng lần mở: {total_opens}/10 (Reset khi đạt 10)"
        
        await ctx.send(f"```\n{result_text}\n```")

    @commands.command(description="Reset drop rates của một user")
    @is_bot_owner()
    async def resetdrop(self, ctx, member: discord.Member = None):
        """Lệnh reset drop rates về mặc định cho một user"""
        target_user = member or ctx.author
        user_id = target_user.id
        
        await self.reset_drop_rates(user_id)
        await ctx.send(f"✅ Đã reset drop rates của {target_user.display_name} về mặc định!")

    @commands.command( description="Tặng vé vàng cho người dùng")
    @is_bot_owner()
    async def ve(self, ctx, nguoi_nhan: discord.User, so_luong: int):
        # Kiểm tra xem kênh có ID là 1147035278465310720 hay không
        if ctx.channel.id == 1104362707580375120:
            return None
        else:
            if not is_registered(ctx.author.id):
                await ctx.send(f"{self.dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
            else:
                if nguoi_nhan is None or so_luong is None or so_luong < 1:
                    await ctx.send("Vd: ztang `user` `1`")
                    return
                if nguoi_nhan.bot:  # Không cho phép trao đổi với bot
                    await ctx.send("Không thể thực hiện trao đổi với bot.")
                    return
                if ctx.author.id == nguoi_nhan.id:
                    await ctx.send("Không thể tặng vé cho bản thân")
                    return
                # Kiểm tra người dùng chưa đăng ký
                if not is_registered(ctx.author.id):
                    await ctx.send(f"{self.dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
                    return
                cursor.execute(
                    "SELECT num_gold_tickets FROM users WHERE user_id = ?", (ctx.author.id,))
                sender_result = cursor.fetchone()
                if not sender_result:
                    await ctx.send("Không thể tải thông tin vé của bạn.")
                    return
                ve_type = "num_gold_tickets"
                sender_ve = sender_result[0]
                if sender_ve < so_luong:
                    await ctx.send(f"{self.chamthan} Bạn k đủ vé {self.vevang} để tặng. **Chăm chat & voice** trong sv để sở hữu thêm vé nha")
                    return
                cursor.execute("SELECT id, kimcuong, " + ve_type +
                            " FROM users WHERE user_id = ?", (nguoi_nhan.id,))
                receiver_result = cursor.fetchone()
                if not receiver_result:
                    await ctx.send(f"{self.dk} người nhận chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
                    return
                new_sender_ve = sender_ve - so_luong
                new_receiver_ve = receiver_result[2] + so_luong  # Cập nhật cột "num_gold_tickets"
                new_receiver_kimcuong = receiver_result[1] + so_luong  # Thêm vào cột "kimcuong"
                cursor.execute("UPDATE users SET " + ve_type +
                            " = ? WHERE user_id = ?", (new_sender_ve, ctx.author.id))
                cursor.execute("UPDATE users SET " + ve_type + " = ?, kimcuong = ? WHERE id = ?", (new_receiver_ve, new_receiver_kimcuong, receiver_result[0]))
                conn.commit()
                await ctx.send(f"{self.tangqua} **| {ctx.author.mention} đã tặng {nguoi_nhan.mention} {so_luong} {self.vevang}**.")

    @commands.command(description="Mở vé vàng hoặc kim cương")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def moqua(self, ctx, loai_ve: str = None):
        cursor.execute("SELECT balance, xu_hlw FROM users WHERE user_id = ?", (ctx.author.id,))
        result = cursor.fetchone()
        balance = result[0]
        xu_hlw = result[1]
        if await self.check_command_disabled(ctx):
            return
        
        # Kiểm tra loại vé trước
        if loai_ve is None:
            loai_ve = "vang"
        elif loai_ve not in ["vang", "kc"]:
            await ctx.send("Vui lòng chỉ mở vé vàng (`vang`) hoặc vé kim cương (`kc`).")
            return
            
        # Kiểm tra kênh tùy theo loại vé
        if loai_ve == "vang":
            # Vé vàng chỉ dùng ở kênh 1147035278465310720
            if ctx.channel.id != 1147035278465310720:
                message = await ctx.reply(f"{list_emoji.tick_check} **Dùng lệnh** **`zmoqua`** **để mở vé vàng** [__**ở đây**__](<https://discord.com/channels/832579380634451969/1147035278465310720>)")
                await asyncio.sleep(10)
                await message.delete()
                await ctx.message.delete()
                return
        elif loai_ve == "kc":
            # Vé kim cương dùng ở 2 kênh
            if ctx.channel.id not in [993153068378116127, 1147035278465310720]:
                message = await ctx.reply(f"{list_emoji.tick_check} **Dùng lệnh** **`zmoqua kc`** **để mở vé kim cương** [__**ở đây**__](<https://discord.com/channels/832579380634451969/1147035278465310720>) **hoặc** [__**ở đây**__](<https://discord.com/channels/832579380634451969/993153068378116127>)")
                await asyncio.sleep(10)
                await message.delete()
                await ctx.message.delete()
                return
        
        if not is_registered(ctx.author.id):
            await ctx.send(f"{self.chamthan} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` tại kênh <#1147355133622108262> để đăng kí")
        else:
            user_id = ctx.author.id
            # Khởi tạo drop rates nếu chưa có cho user này
            await self.init_drop_rates(user_id)
            
            if loai_ve == "kc":
                min_id = 1
                max_id = 5
            elif loai_ve == "vang":
                min_id = 6
                max_id = 32
                random_id = random.randint(min_id, max_id)
            cursor.execute(
                "SELECT * FROM phan_thuong WHERE id >= ? AND id <= ?", (min_id, max_id))
            phan_thuong_list = cursor.fetchall()

            user_id = ctx.author.id
            ve_column = "num_gold_tickets" if loai_ve == "vang" else "num_diamond_tickets"
            cursor.execute(
                f"SELECT {ve_column} FROM users WHERE user_id = ?", (user_id,))
            ve_con_lai = cursor.fetchone()[0]
            if ve_con_lai <= 0:
                await ctx.send(f"{self.chamthan} Bạn k có vé nào để mở. **Chăm chat & voice**  trong sv để sở hữu thêm vé {self.vevang} nha")
                return
            phan_thuong_co_the_mo = [
                pt for pt in phan_thuong_list if pt[2] > 0]
            if not phan_thuong_co_the_mo:
                await ctx.send("Không còn phần thưởng nào để mở.")
                return
            
            # Sử dụng dynamic drop rates thay vì random.choice
            selected_phan_thuong = await self.get_weighted_selection(phan_thuong_co_the_mo, loai_ve, user_id)
            phan_thuong_id = selected_phan_thuong[0]
            cursor.execute(
                "UPDATE phan_thuong SET soluong_phanthuong = soluong_phanthuong - 1 WHERE id = ?", (phan_thuong_id,))
            conn.commit()
            await self.trao_thuong(ctx, selected_phan_thuong)
            await self.cap_nhat_ve(user_id, loai_ve, selected_phan_thuong)

    @moqua.error
    async def moqua_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            message = await ctx.send(f"{dongho} **| {ctx.author.mention} vui lòng chờ {error.retry_after:.0f} giây trước khi sử dụng lệnh này.**")
            await asyncio.sleep(2)
            await message.delete()
            await ctx.message.delete()
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error

    async def cap_nhat_ve(self, user_id, loai_ve, phan_thuong):
        ve_column = "num_gold_tickets" if loai_ve == "vang" else "num_diamond_tickets"
        cursor.execute(
            f"UPDATE users SET {ve_column} = {ve_column} - 1 WHERE user_id = ?", (user_id,))
        conn.commit()

        cursor.execute(
            f"SELECT open_items FROM users WHERE user_id = ?", (user_id,))
        open_items_data = cursor.fetchone()[0]
        open_items_dict = json.loads(
            open_items_data) if open_items_data else {}

        if phan_thuong[1] in open_items_dict:
            open_item = open_items_dict[phan_thuong[1]]
            open_item["emoji"] = phan_thuong[3]  # emoji_phanthuong
            open_item["so_luong"] += 1
        else:
            open_item = {
                "emoji": phan_thuong[3],  # emoji_phanthuong
                "name_phanthuong": phan_thuong[1],
                "so_luong": 1
            }
            open_items_dict[phan_thuong[1]] = open_item

        # Sắp xếp lại các mục trong open_items theo emoji_phanthuong
        sorted_open_items = dict(
            sorted(open_items_dict.items(), key=lambda item: item[1]["emoji"]))

        updated_open_items = json.dumps(sorted_open_items)
        cursor.execute(
            f"UPDATE users SET open_items = ? WHERE user_id = ?", (updated_open_items, user_id))
        conn.commit()

    async def trao_thuong(self, ctx, phan_thuong):
        cursor.execute("SELECT balance, xu_hlw FROM users WHERE user_id = ?", (ctx.author.id,))
        result = cursor.fetchone()
        balance = result[0]
        xu_hlw = result[1]

        enable_buttons = ctx.author.id
        # view = MoquaView(enable_buttons, phan_thuong)
              
        # if phan_thuong[0] in {1, 2, 3, 4}:
        #     message = await ctx.reply(view=view)
        #     view.message = message
        # if phan_thuong[0] == 5:
        #     # Cập nhật xu_hlw
        #     cursor.execute(
        #         "UPDATE users SET xu_hlw = xu_hlw + 5 WHERE user_id = ?", (ctx.author.id,))
        #     conn.commit()
        #     message = await ctx.reply(view=view)
        #     view.message = message
        # elif phan_thuong[0] in {6, 7, 8, 9, 10}:
        #     message = await ctx.reply(view=view)
        #     view.message = message
        # elif phan_thuong[0] == 11:
        #     # Cập nhật balance
        #     cursor.execute(
        #         "UPDATE users SET balance = balance + 100000 WHERE user_id = ?", (ctx.author.id,))
        #     conn.commit()
        #     message = await ctx.reply(view=view)
        #     view.message = message
        # elif phan_thuong[0] == 12:
        #     # Cập nhật balance
        #     cursor.execute(
        #         "UPDATE users SET balance = balance + 200000 WHERE user_id = ?", (ctx.author.id,))
        #     conn.commit()
        #     message = await ctx.reply(view=view)
        #     view.message = message
        # elif phan_thuong[0] == 13:
        #     # Cập nhật xu_hlw
        #     cursor.execute(
        #         "UPDATE users SET xu_hlw = xu_hlw + 1 WHERE user_id = ?", (ctx.author.id,))
        #     conn.commit()
        #     message = await ctx.reply(view=view)
        #     view.message = message

        if phan_thuong[0] in {1, 2, 3}:
            await ctx.send(f"# {quathantai} **Chúc mừng {ctx.author.mention}, bạn trúng phần quà** **{phan_thuong[1]}** {phan_thuong[3]}")
            # embed = discord.Embed(
            #     title=f"{quathantai} **Chúc mừng {ctx.author.mention}, bạn trúng phần quà** **{phan_thuong[1]}** {phan_thuong[3]}",
            #     description="",
            #     color=discord.Color.from_rgb(158,230,255),
            # )
            # embed.set_thumbnail(
            #     url=""
            # )
            # await ctx.send(embed=embed)
        elif phan_thuong[0] == 4:
            embed = discord.Embed(
                title=f"",
                description=f"# {quathantai} **Chúc mừng {ctx.author.mention}, bạn trúng phần quà** **{phan_thuong[1]}** {phan_thuong[3]}\n-# {muitenxeo} Sưu tầm đủ 5 labubu để nhận quà 20K {phan_thuong[3]} nha",
                color=discord.Color.from_rgb(158,230,255),
            )
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/1211199649667616768/1417831679040684072/discord_fake_avatar_decorations_1758107598903.gif"
            )
            await ctx.send(embed=embed)   
        elif phan_thuong[0] == 5:
            # Cập nhật xu_hlw
            cursor.execute(
                "UPDATE users SET xu_hlw = xu_hlw + 5 WHERE user_id = ?", (ctx.author.id,))
            conn.commit()

            await ctx.send(f"# {quathantai} **Chúc mừng {ctx.author.mention}, bạn trúng phần quà** **{phan_thuong[1]}** {phan_thuong[3]}")

            # embed = discord.Embed(
            #     title=f"# {quathantai} **Chúc mừng {ctx.author.mention}, bạn trúng phần quà** **{phan_thuong[1]}** {phan_thuong[3]}",
            #     description="",
            #     color=discord.Color.from_rgb(158,230,255),
            # )
            # embed.set_thumbnail(
            #     url=""
            # )
            # await ctx.send(embed=embed)

        elif phan_thuong[0] in {6, 7, 8, 9, 10}:
            await ctx.send(
                f"{quatienowo} **Chúc mừng {ctx.author.mention}, bạn trúng phần quà** {nhayxanh}**{phan_thuong[1]}**{nhayxanh} {phan_thuong[3]}"
            )
        elif phan_thuong[0] == 11:
            # Cập nhật balance
            cursor.execute(
                "UPDATE users SET balance = balance + 10000 WHERE user_id = ?", (ctx.author.id,))
            conn.commit()
            await ctx.send(
                f"{quatienhong} **Chúc mừng {ctx.author.mention}**, **bạn trúng phần quà** {nhayhong}**{phan_thuong[1]}**{nhayhong} {phan_thuong[3]}"
            )
        elif phan_thuong[0] == 12:
            # Cập nhật balance
            cursor.execute(
                "UPDATE users SET balance = balance + 20000 WHERE user_id = ?", (ctx.author.id,))
            conn.commit()
            await ctx.send(
                f"{quatienhong} **Chúc mừng {ctx.author.mention},  bạn trúng phần quà** {nhayhong}**{phan_thuong[1]}**{nhayhong} {phan_thuong[3]}"
            )
        elif phan_thuong[0] == 13:
            # Cập nhật xu_hlw
            cursor.execute(
                "UPDATE users SET xu_hlw = xu_hlw + 1 WHERE user_id = ?", (ctx.author.id,))
            conn.commit()
            await ctx.send(
                f"{quaxu} **Chúc mừng {ctx.author.mention},  bạn trúng quà** {nhayhong}**{phan_thuong[1]}**{nhayhong} {phan_thuong[3]}")

        elif phan_thuong[0] == 14:
            await ctx.send(f"{quanuhon} **Chúc mừng {ctx.author.mention}, bạn nhận được 1** __**{phan_thuong[1]}**__ **của chị hằng**")
        elif phan_thuong[0] == 15:
            await ctx.send(f"{quacainit} **Chúc mừng {ctx.author.mention}, bạn nhận được 1** __**{phan_thuong[1]}**__ {phan_thuong[3]}")
        elif phan_thuong[0] == 16:
            await ctx.send(f"{quabicuop} **Chia buồn cùng {ctx.author.mention} nha, bạn bị kẻ gian cướp mất quà rồi**")
        elif phan_thuong[0] in {17, 18, 21, 22, 23}:
            await ctx.send(f"{qualongden2} **Chúc mừng {ctx.author.mention}, bạn được tặng 1** __**{phan_thuong[1]}**__ {dotmau}{phan_thuong[3]}{dotmau}")                        
        elif phan_thuong[0] in {24, 25}:
            await ctx.send(f"{qualongden} **Chúc mừng {ctx.author.mention}, bạn được tặng 1** {dotvang}__**{phan_thuong[1]}**__ {phan_thuong[3]}{dotvang}")
        elif phan_thuong[0] in  {19, 20, 26, 27, 28}:
            await ctx.send(f"{quavang} **Chúc mừng {ctx.author.mention}, bạn được tặng 1** __**{phan_thuong[1]}**__ {phan_thuong[3]}")  
        elif phan_thuong[0] == 29:
            await ctx.send(f"{quaxu} **Chúc mừng {ctx.author.mention} , bạn được tặng 1** __**{phan_thuong[1]}**__ {phan_thuong[3]}") 
        elif phan_thuong[0] in {30, 31, 32}:
            await ctx.send(f"{quavang} **{ctx.author.mention} bạn nhận được 1** __**{phan_thuong[1]}**__ {phan_thuong[3]} **để làm bánh, bấm lệnh ** [__**`zlambanh`**__](<https://discord.com/channels/832579380634451969/1147355133622108262>) **để xem nhé**")               

    @commands.command(aliases=["inv"], description="Hiển thị danh sách inventory")
    @is_allowed_channel_check()
    async def inventory(self, ctx):
        if await self.check_command_disabled(ctx):
            return
        if not is_registered(ctx.author.id):
            await ctx.send(f"{self.dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
        else:
            user_id = ctx.author.id
            cursor.execute("SELECT open_items, daily_streak FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()

            open_items_data = result[0]
            daily_streak = result[1]

            open_items_dict = json.loads(open_items_data) if open_items_data else {}

            embed = discord.Embed(title=f"",
                                color=discord.Color.from_rgb(242, 226, 6))
            if ctx.author.avatar:
                avatar_url = ctx.author.avatar.url
            else:
                avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
            embed.set_author(name=f"Kho quà của {ctx.author.display_name}", icon_url=avatar_url)

            if not open_items_dict:
                embed.add_field(
                    name=f"", value=f"{chamthan} **Kho trống, chat & voice tại sv để nhận {self.vevang} nha**")
            else:
                # Tách items thành 2 nhóm: các items thường và reward_items
                reward_items = {  
                    1: {"name": "1_longdentho", "emoji": longdentho},  
                    2: {"name": "2_longdensao", "emoji": longdensao},
                    3: {"name": "3_longdengaudau", "emoji": longdengaudau},
                    4: {"name": "4_longdenga", "emoji": longdenga},
                    5: {"name": "5_longdenmarsupilami", "emoji": longdenmarsupilami},
                    6: {"name": "6_longdenca", "emoji": longdenca},
                    7: {"name": "7_longdendoremi", "emoji": longdendoremi},
                    8: {"name": "8_longdenlan", "emoji": longdenlan},
                    9: {"name": "9_longdenheo", "emoji": longdenheo},
                    10: {"name": "10_longdenpikachu", "emoji": longdenpikachu},
                    11: {"name": "11_longdenlobby", "emoji": longdenlobby},
                    12: {"name": "12_longdencaptain", "emoji": longdencaptain},
                    13: {"name": "13_longdendoremon", "emoji": longdendoremon},
                    14: {"name": "14_longdennguoinhen", "emoji": longdennguoinhen},
                    15: {"name": "15_longdenbuom", "emoji": longdenbuom},  
                }
                reward_item_names = {reward["name"] for reward in reward_items.values()}
                
                # Tách items thành 2 danh sách: thường và reward_items
                normal_items = {}
                reward_items_data = {}
                
                for item_name, item_data in open_items_dict.items():
                    if item_name in reward_item_names:
                        reward_items_data[item_name] = item_data
                    else:
                        normal_items[item_name] = item_data
                
                # Sắp xếp từng nhóm riêng biệt
                sorted_normal_items = dict(sorted(normal_items.items(), key=lambda item: item[1]["emoji"]))
                sorted_reward_items = dict(sorted(reward_items_data.items(), key=lambda item: item[1]["emoji"]))
                
                # Ghép lại: normal items trước, reward items sau
                final_sorted_items = {**sorted_normal_items, **sorted_reward_items}
                
                item_fields = []
                items_per_inline = 6  # Số lượng item trong mỗi trường

                for i, (item_name, item_data) in enumerate(final_sorted_items.items()):
                    emoji_str = item_data["emoji"] 
                    item_quantity = get_superscript(item_data["so_luong"])  
                    if item_name in ["10k", "20k", "50k", "100k", "200k", "500k", "100,000", "200,000","500,000", "1,000,000","2,000,000","20,000"]:  
                        if item_name == "20,000":  
                            item_name = "20k"  
                        elif item_name == "100,000":  
                            item_name = "100k"
                        elif item_name == "200,000":
                            item_name = "200k"  
                        elif item_name == "500,000":
                            item_name = "500k"
                        elif item_name == "1,000,000":  
                            item_name = "1M"
                        elif item_name == "2,000,000":
                            item_name = "2M"
                        item_fields.append(f"**{item_name}** {emoji_str} **{item_quantity}**")  
                    else:  
                        item_fields.append(f"{emoji_str} **{item_quantity}**")  

                    if (i + 1) % items_per_inline == 0 or (i + 1) == len(final_sorted_items):  
                        embed.add_field(name="",  
                                        value="  ".join(item_fields), inline=False)  
                        item_fields = []   
                    
                embed.add_field(name="",
                                value=f"{daily_streak1} **Daily streak:** __**{daily_streak}**__ **ngày**", inline=False)
                
                # Đếm số lượng reward_items
                songuqua = len([name for name in final_sorted_items.keys() if name in reward_item_names])
                                
                if songuqua == 0:
                    embed.add_field(name="", value=f"**{quaylongden} ** __**0/15**__", inline=False)
                else:
                    embed.add_field(name="", value=f"**{quaylongden} ** __**{songuqua}/15**__", inline=False)
            await ctx.send(embed=embed)

    @commands.command(description="Reset các cột trong các bảng dữ liệu")
    @is_bot_owner()
    async def rsve(self, ctx):
        # Reset bảng users
        cursor.execute(
            "UPDATE users SET num_gold_tickets = 0, num_diamond_tickets = 0, open_items = '', total_tickets = 0, daily_streak = 0, last_daily = 0, daily_tickets = 0, kimcuong = 0")
        # Reset bảng ve_database
        cursor.execute(
            "UPDATE ve_database SET num_gold_tickets_available = 8890, num_diamond_tickets_available = 70, quantity_tickets = 0, tong_tickets = 0, daily_keo = 0, daily_bonus1 = 0, daily_bonus2 = 0, daily_bonus3 = 0, daily_bonus4 = 0, daily_nglieu1 = 0, daily_nglieu2 = 0, daily_nglieu3 = 0, daily_nglieu4 = 0")
        # Xóa và thêm lại các dòng trong bảng phan_thuong theo danh sách mới
        danh_sach_phan_thuong = [
            ("500,000", 5, 1284735146515365959),  # 1 vé kim cương
            ("1,000,000", 5, 1284735146515365959),  # 2 vé kim cương
            ("20,000", 3, 1417881928971063316),  # 3 vé kim cương
            ("lồng đèn labubu", 45, 1417876294414110792),  # 4 vé kim cương
            ("5 xu", 12, 1417817584295870525),  # 5 vé kim cương
            ("10k", 50, 1284735146515365959),  # 6
            ("20k", 50, 1284735146515365959),  # 7
            ("50k", 50, 1284735146515365959),  # 8
            ("100k", 20, 1284735146515365959),  # 9
            ("200k", 10, 1284735146515365959),  # 10
            ("10,000", 30, 1416278321792290917),  # 11
            ("20,000", 30, 1416278321792290917),  # 12
            ("1 xu", 50, 1417817584295870525),  # 13
            ("nụ hôn", 30, 1419150041758699651),  # 14
            ("cái nịt", 30, 1284474488909598741),  # 15
            ("bị cướp", 40, 1416358222151024712),  # 16
            ("lồng đèn giấy hồng", 40, 1416358467341389925),  # 17
            ("lồng đèn giấy đỏ", 30, 1416358452569309225),  # 18 
            ("bánh trung thu hạt sen", 30, 1416358490766835867),  # 19
            ("bánh trung thu socola", 40, 1416358517576826981),  # 20
            ("lồng đèn giấy vàng", 250, 1416358460349743154),  # 21 ------ quà bonus
            ("lồng đèn giấy xanh", 280, 1416358476216668262),  # 22
            ("lồng đèn giấy xanh lá cây", 300, 1416358483145527316),  # 23
            ("lồng đèn cá chép đỏ", 260, 1416357998229459015),  # 24
            ("lồng đèn cá chép xanh", 250, 1416357977438425088),  # 25 
            ("bánh trung thu matcha", 250, 1416358510006112296),  # 26 
            ("bánh trung thu đậu đỏ", 280, 1416358501823025233),  # 27 
            ("bánh trung thu khoai môn", 300, 1416358524547498034),  # 28 
            ("gấu bông thỏ", 290, 1417820533164212295),  # 29
            ("bột", 2700, 1416358091884335174),  # 30 ------ quà daily
            ("trứng muối", 1600, 1416358111438045334),  # 31
            ("đậu xanh", 1600, 1416358140685058208),  # 32
        ]

        # Xóa toàn bộ dữ liệu cũ trong bảng phan_thuong
        cursor.execute("DELETE FROM phan_thuong")

        for phan_thuong in danh_sach_phan_thuong:
            emoji = None
            # Duyệt qua tất cả các server mà bot đang tham gia
            for guild in self.client.guilds:
                emoji = discord.utils.get(guild.emojis, id=phan_thuong[2])
                if emoji:
                    break  # Nếu tìm thấy emoji thì dừng lại

            emoji_str = f"{emoji}" if emoji else ""
            cursor.execute(
                "INSERT OR IGNORE INTO phan_thuong (name_phanthuong, soluong_phanthuong, emoji_phanthuong) VALUES (?, ?, ?)", 
                (phan_thuong[0], phan_thuong[1], emoji_str)
            )
            conn.commit()

        await ctx.send("Đã thực hiện reset các cột trong các bảng dữ liệu.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.channel.id == 1147035278465310720 and any(keyword in message.content.lower() for keyword in ["zve", "ogive", "zsetve"]):
            await asyncio.sleep(10)
            await message.delete()

    def cog_unload(self):
        self.reset_daily_task.cancel()

    @tasks.loop(seconds=60)
    async def reset_daily_task(self):
        timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        now = datetime.datetime.now(timezone)
        if now.hour == 14 and now.minute == 0:  # Nếu là 14:00 giờ +7
            # Thực hiện lệnh resetdaily
            cursor.execute(
                "UPDATE users SET last_daily = 0, quest = '', quest_mess = 0, quest_time = 0")
            cursor.execute("UPDATE ve_database SET daily_keo = 0, daily_bonus1 = 0, daily_bonus2 = 0, daily_bonus3 = 0, daily_bonus4 = 0, daily_nglieu1 = 0, daily_nglieu2 = 0, daily_nglieu3 = 0, daily_nglieu4 = 0")
            conn.commit()
            channel = self.client.get_channel(1147355133622108262)
            await channel.send(f"# ĐÃ RESET DAILY THÀNH CÔNG <@&1182739180871225465> !!!")

    @reset_daily_task.before_loop
    async def before_reset_daily_task(self):
        await self.client.wait_until_ready()

    @commands.command(description="Điểm danh mỗi ngày")
    @is_daily_channel()
    async def daily(self, ctx):
        if await self.check_command_disabled(ctx):
            return
        if not is_registered(ctx.author.id):
            await ctx.send(f"{self.dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
            return
        user_id = ctx.author.id
        now = datetime.datetime.utcnow() + timedelta(hours=7)  # Điều chỉnh múi giờ
        cursor.execute(
            "SELECT last_daily, daily_streak FROM users WHERE user_id = ?", (user_id,))
        last_daily, daily_streak = cursor.fetchone()
        cursor.execute(
            "SELECT daily_keo, daily_bonus1, daily_bonus2, daily_bonus3, daily_bonus4, daily_nglieu1, daily_nglieu2, daily_nglieu3, daily_nglieu4 FROM ve_database")
        result = cursor.fetchone()
        daily_keo = result[0]
        daily_bonus1 = result[1]
        daily_bonus2 = result[2]
        daily_bonus3 = result[3]
        daily_bonus4 = result[4]
        daily_nglieu1 = result[5]
        daily_nglieu2 = result[6]
        daily_nglieu3 = result[7]
        daily_nglieu4 = result[8]

        # Tính thời gian còn lại đến reset daily
        reset_time = datetime.datetime(now.year, now.month, now.day,
                                       14, 0) + timedelta(days=1)
        time_left = reset_time - now
        # Định dạng lại thời gian còn lại
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_left_str = f"{hours}h{minutes}m{seconds}s"
        # Lấy lại giá trị của daily_streak sau khi cập nhật
        cursor.execute(
            "SELECT last_daily FROM users WHERE user_id = ?", (user_id,))
        last_daily = cursor.fetchone()[0]
        if last_daily != 0:
            await ctx.send(f"{time_daily} | Bạn đã điểm danh hôm nay rồi! Lượt điểm danh tiếp theo còn: **{time_left_str}**")
            return
        # Cập nhật Daily streak
        cursor.execute(
            "UPDATE users SET daily_streak = daily_streak + 1 WHERE user_id = ?", (user_id,))
        # Cập nhật last_daily
        cursor.execute(
            "UPDATE users SET last_daily = ? WHERE user_id = ?", (now, user_id))
        # Lấy lại giá trị của daily_streak sau khi cập nhật
        cursor.execute(
            "SELECT daily_streak FROM users WHERE user_id = ?", (user_id,))
        daily_streak = cursor.fetchone()[0]
        # Kiểm tra nếu user thuộc các role DONATOR
        donator_roles = [1021383533178134620, 1082887622311022603, 1056244443184906361,
                         1055759097133277204, 1055758414678069308, 1055519421424222208, 1117282898052141188]
        # domdom_roles = [1311874053786566688, 1071865893103075468]
        if any(role.id in donator_roles for role in ctx.author.roles):
            balance_increase = 20000
            coin_kc_increase = 1
            cursor.execute(
                "UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ? WHERE user_id = ?", (balance_increase, coin_kc_increase, user_id))
        else:
            balance_increase = 10000
            coin_kc_increase = 1
            cursor.execute(
                "UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ? WHERE user_id = ?", (balance_increase, coin_kc_increase, user_id))
        donator_role_id = None  # ID của role DONATOR nếu người dùng có
        for role in ctx.author.roles:
            if role.id in donator_roles:
                donator_role_id = role.id  # Lưu ID của role DONATOR của người dùng
        if donator_role_id:  # Nếu người dùng có role thuộc danh sách DONATOR
            donator_info = f"- <@&{donator_role_id}>: **20k {list_emoji.pinkcoin}**"
        else:
            donator_info = f"- <@&{1021383533178134620}>: **20k {list_emoji.pinkcoin}**"
            
        # if any(role.id in domdom_roles for role in ctx.author.roles):
        #     balance_increase = 50000
        #     noel_coin = 1
        #     cursor.execute(
        #         "UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ? WHERE user_id = ?", (balance_increase, noel_coin, user_id))
        #     domdom_info = f"- <@&{1311874053786566688}>: **50k {list_emoji.pinkcoin} + 1 {list_emoji.xu_event}**"
        # else:
        #     domdom_info = f"- <@&{1311874053786566688}>: **Không có**"
        #nếu người dùng có marry thì cộng thêm tiền
        # cursor.execute("SELECT marry FROM users WHERE user_id = ?", (user_id,))
        # marry = cursor.fetchone()[0]
        # if marry:
        #     cursor.execute(
        #         "UPDATE users SET balance = balance + 20000, xu_hlw = xu_hlw + 1 WHERE user_id = ?", 
        #         (user_id,)
        #     )
        #     conn.commit()
        #     marry_info = f"- {daily_love} | Married: 20k {list_emoji.pinkcoin} + 1 {list_emoji.xu_event}"
        # else:
        #     marry_info = "- 💔 | **single**"

        # Random tỉ lệ 80%
        if random.random() <= 0.9 and daily_keo <= 120 and (daily_bonus1 <=15 or daily_bonus2 <=15 or daily_bonus3 <=15 or daily_bonus4 <=15) and (daily_nglieu1 <= 30 or daily_nglieu2 <= 10 or daily_nglieu3 <= 10 or daily_nglieu4 <= 10):
            min_id = 21
            max_id = 32
            exclude_ids = [21, 22, 23, 24, 25, 26, 27, 28, 29]  # IDs của các phần thưởng không được chọn
            quabiboqua_ids = [30, 31, 32]  # IDs của các phần thưởng là nguyên liệu
            cursor.execute(
                "SELECT * FROM phan_thuong WHERE id >= ? AND id <= ?", (min_id, max_id))
            phan_thuong_list = cursor.fetchall()
            phan_thuong_con_lai = [
                pt for pt in phan_thuong_list if pt[0] not in exclude_ids and pt[2] > 0
            ]
            phan_thuong_nguyen_lieu = [
                pt for pt in phan_thuong_list if pt[0] not in quabiboqua_ids and pt[2] > 0
            ]
            selected_phan_thuong = random.choice(phan_thuong_con_lai)
            selected_nguyen_lieu = random.choice(phan_thuong_nguyen_lieu)

            # if selected_phan_thuong[0] == 28:  # Kiểm tra nếu là item 28
            #     cursor.execute(
            #         "UPDATE users SET coin_kc = coin_kc + 10 WHERE user_id = ?", (user_id,))

            await self.cap_nhat_ve_daily(user_id, selected_phan_thuong, selected_nguyen_lieu)

            conn.commit()
            embed = discord.Embed(title="",
                                  color=discord.Color.from_rgb(255,167,249))

            if ctx.author.avatar:
                avatar_url = ctx.author.avatar.url
            else:
                avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"

            embed.set_author(
                name=f"{ctx.author.display_name} daily thành công", icon_url=avatar_url)
            if any(role.id in donator_roles for role in ctx.author.roles):
                embed.add_field(
                    name=f"", value=f"- {daily_streak1} | Daily streak __**{daily_streak}**__\n- {quatienowo_hong} | Quà daily: **20k {list_emoji.pinkcoin} + 1 {list_emoji.xu_event}**\n{donator_info}\n- {selected_nguyen_lieu[3]} | Quà bonus: **{selected_nguyen_lieu[1]}**\n- {selected_phan_thuong[3]} | Nguyên liệu: **{selected_phan_thuong[1]}** \n- {time_daily} | Next daily: **`{time_left_str}`**", inline=False)
            else:
                embed.add_field(
                    name=f"", value=f"- {daily_streak1} | Daily streak __**{daily_streak}**__\n- {quatienowo_hong} | Quà daily: **20k {list_emoji.pinkcoin} + 1 {list_emoji.xu_event}**\n{donator_info}\n- {selected_nguyen_lieu[3]} | Quà bonus: **{selected_nguyen_lieu[1]}**\n- {selected_phan_thuong[3]} | Nguyên liệu: **{selected_phan_thuong[1]}** \n- {time_daily} | Next daily: **`{time_left_str}`**", inline=False)
            await ctx.send(embed=embed)
            daily_mapping = {  
                14: "daily_bonus1",  
                15: "daily_bonus2",  
                16: "daily_bonus3",  
                17: "daily_bonus4",  
                18: "daily_nglieu1",  
                19: "daily_nglieu2",  
                20: "daily_nglieu3",  
                21: "daily_nglieu4"  
            }  
            column_name = daily_mapping.get(selected_phan_thuong[0])  

            if column_name:  
                cursor.execute(f"UPDATE ve_database SET {column_name} = {column_name} + 1") 
            cursor.execute(
                "UPDATE phan_thuong SET soluong_phanthuong = soluong_phanthuong - 1 WHERE id = ?", (selected_phan_thuong[0],))
            cursor.execute(
                "UPDATE phan_thuong SET soluong_phanthuong = soluong_phanthuong - 1 WHERE id = ?", (selected_nguyen_lieu[0],))
            cursor.execute(
                "UPDATE ve_database SET daily_keo = daily_keo + 1")
            conn.commit()
        else:
            # Không trong 80%, không ra nguyên liệu và phần thưởng, không ghi vào database
            embed = discord.Embed(title="",
                                  color=discord.Color.from_rgb(255,167,249))
            if ctx.author.avatar:
                avatar_url = ctx.author.avatar.url
            else:
                avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
            embed.set_author(
                name=f"{ctx.author.display_name} daily thành công", icon_url=avatar_url)
            if any(role.id in donator_roles for role in ctx.author.roles):
                embed.add_field(
                    name=f"", value=f"- {daily_streak1} | Daily streak __**{daily_streak}**__\n- {quatienowo_hong} | Quà daily: **20k {list_emoji.pinkcoin} + 1 {list_emoji.xu_event}**\n{donator_info}\n- {quavang} | Quà bonus: **Không có**\n- {quavang} | Nguyên liệu: **Không có** \n- {time_daily} | Next daily: **`{time_left_str}`**", inline=False)
            else:
                embed.add_field(
                    name=f"", value=f"- {daily_streak1} | Daily streak __**{daily_streak}**__\n- {quatienowo_hong} | Quà daily: **20k {list_emoji.pinkcoin} + 1 {list_emoji.xu_event}**\n{donator_info}\n- {quavang} | Quà bonus: **Không có**\n- {quavang} | Nguyên liệu: **Không có**\n- {time_daily} | Next daily: **`{time_left_str}`**", inline=False)
            await ctx.send(embed=embed)
            cursor.execute(
                "UPDATE ve_database SET daily_keo = daily_keo + 1")
            conn.commit()
            return

    async def cap_nhat_ve_daily(self, user_id, phan_thuong, nguyen_lieu):
        cursor.execute(
            f"SELECT open_items FROM users WHERE user_id = ?", (user_id,))
        open_items_data = cursor.fetchone()[0]
        open_items_dict = json.loads(
            open_items_data) if open_items_data else {}

        if phan_thuong[1] in open_items_dict:
            open_item = open_items_dict[phan_thuong[1]]
            open_item["emoji"] = phan_thuong[3]  # emoji_phanthuong
            open_item["so_luong"] += 1
        else:
            open_item = {
                "emoji": phan_thuong[3],  # emoji_phanthuong
                "name_phanthuong": phan_thuong[1],
                "so_luong": 1
            }
            open_items_dict[phan_thuong[1]] = open_item

        if nguyen_lieu[1] in open_items_dict:
            open_item = open_items_dict[nguyen_lieu[1]]
            open_item["emoji"] = nguyen_lieu[3]
            open_item["so_luong"] += 1
        else:
            open_item = {
                "emoji": nguyen_lieu[3],
                "name_phanthuong": nguyen_lieu[1],
                "so_luong": 1
            }
            open_items_dict[nguyen_lieu[1]] = open_item

        # Sắp xếp lại các mục trong open_items theo emoji_phanthuong
        sorted_open_items = dict(
            sorted(open_items_dict.items(), key=lambda item: item[1]["emoji"]))
        updated_open_items = json.dumps(sorted_open_items)
        cursor.execute(
            f"UPDATE users SET open_items = ? WHERE user_id = ?", (updated_open_items, user_id))
        conn.commit()
        
    @commands.command( description="set lại số vé hàng ngày")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @is_bot_owner()
    async def rsdaily(self, ctx):
        msg = await ctx.send("Bạn có chắc chắn muốn set lại số vé hàng ngày? ")
        await msg.add_reaction(dungset)
        await msg.add_reaction(saiset)
        
        def check(reaction, user):
            return (
                user == ctx.author
                and str(reaction.emoji) in [dungset, saiset]
                and reaction.message.id == msg.id
            )
        
        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=30.0, check=check)
            if str(reaction.emoji) == dungset:
                cursor.execute("UPDATE ve_database SET quantity_tickets = 0")
                cursor.execute("UPDATE users SET daily_tickets = 0")
                conn.commit()
                await msg.edit(content="Đã set lại số vé hàng ngày")
            else:
                await msg.edit(content="Lệnh đã bị hủy.")
        except asyncio.TimeoutError:
            await msg.edit(content="Bạn không phản ứng kịp thời, lệnh đã bị hủy.")

    @commands.command( description="set lại số vé hàng ngày")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @is_bot_owner()
    async def rsdailyly(self, ctx):
        msg = await ctx.send("Bạn có chắc chắn muốn set lại daily? ")
        await msg.add_reaction(dungset)
        await msg.add_reaction(saiset)
        
        def check(reaction, user):
            return (
                user == ctx.author
                and str(reaction.emoji) in [dungset, saiset]
                and reaction.message.id == msg.id
            )
        
        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=30.0, check=check)
            if str(reaction.emoji) == dungset:
                cursor.execute("UPDATE users SET last_daily = 0")
                conn.commit()
                await msg.edit(content="Đã set lại daily")
            else:
                await msg.edit(content="Lệnh đã bị hủy.")
        except asyncio.TimeoutError:
            await msg.edit(content="Bạn không phản ứng kịp thời, lệnh đã bị hủy.")

    @commands.command( description="set tổng số vé nhận được cho người khác")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @is_bot_owner()
    async def settongve(self, ctx, user: discord.User, so_luong: int):
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user.id,))
        user_data = cursor.fetchone()
        if user_data is None:
            await ctx.send(f"{self.dk} người nhận chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
            return
        cursor.execute("UPDATE users SET kimcuong = kimcuong + ? WHERE user_id = ? ", (so_luong, user.id))
        conn.commit()

    @commands.command(description="Set số lượng cho cột num_gold_tickets và num_diamond_tickets bảng users")
    @is_bot_owner()
    async def setve(self, ctx, user: discord.User, loai_ve: str, so_luong: int):
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user.id,))
        user_data = cursor.fetchone()

        if user_data is None:
            await ctx.send(f"{self.dk} người nhận chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
            return
        if loai_ve is None:
            loai_ve = "vang"
        elif loai_ve not in ["vang", "kc"]:
            await ctx.send("Nhập vé vàng (`vang`) hoặc vé kim cương (`kc`).")
            return

        ve_column = "num_gold_tickets" if loai_ve == "vang" else "num_diamond_tickets"
        # Lấy dữ liệu hiện có của cột vé
        cursor.execute(
            f"SELECT {ve_column} FROM users WHERE user_id = ?", (user.id,))
        current_tickets = cursor.fetchone()[0]
        # Tính toán số lượng mới bằng cách cộng với dữ liệu hiện có (hoặc 0 nếu không có dữ liệu)
        new_tickets = so_luong + current_tickets if current_tickets is not None else so_luong
        # Cập nhật cột vé với giá trị mới
        cursor.execute(
            f"UPDATE users SET {ve_column} = ?, kimcuong = kimcuong + ? WHERE user_id = ?", (new_tickets, so_luong, user.id))
        conn.commit()
        # Kiểm tra và xử lý cột num_diamond_tickets_available hoặc num_gold_tickets_available
        if loai_ve == 'vang':
            ve_available_column = "num_gold_tickets_available"
        elif loai_ve == 'kc':
            ve_available_column = "num_diamond_tickets_available"
        cursor.execute(f"SELECT {ve_available_column} FROM ve_database")
        available_tickets = cursor.fetchone()[0]
        cursor.execute(
            'SELECT tong_tickets FROM ve_database')
        ve_data = cursor.fetchone()
        if available_tickets is not None and ve_data:
            tong_tickets = ve_data[0]
            # Trừ đi số lượng vé đã set từ số lượng vé có sẵn
            updated_available_tickets = available_tickets - so_luong
            new_tong_tickets = tong_tickets + so_luong
            # Cập nhật cột vé có sẵn với giá trị mới
            cursor.execute(
                f"UPDATE ve_database SET tong_tickets = ?, {ve_available_column} = ?", (new_tong_tickets, updated_available_tickets,))
            conn.commit()

        if loai_ve == 'vang':
            await ctx.send(f"**HGTT** gửi tặng **{so_luong} vé {self.vevang}** cho {user.mention}.")
        elif loai_ve == 'kc':
            await ctx.send(f"**HGTT** gửi tặng **{so_luong} vé {self.vekc}** cho {user.mention}.")

    @commands.command( description="Gửi tin nhắn đến người dùng khả dụng trong database")
    @is_bot_owner()
    async def send(self, ctx, member: typing.Optional[discord.Member] = None, *, message):
        cursor.execute("SELECT user_id FROM users")
        user_ids = cursor.fetchall()
        
        # Kiểm tra trường hợp gửi đến tất cả người dùng
        if member is None:
            confirmation_msg = await ctx.send("Bạn có chắc chắn muốn gửi tin nhắn này đến **tất cả người dùng** không?")
        else:
            # Kiểm tra trường hợp gửi đến một người cụ thể
            confirmation_msg = await ctx.send(f"Bạn có chắc chắn muốn gửi tin nhắn này đến {member.mention} không?")
        
        # Thêm reaction emoji để xác nhận
        await confirmation_msg.add_reaction(dungset)
        await confirmation_msg.add_reaction(saiset)
        
        def check(reaction, user):
            return user == ctx.author and reaction.message.id == confirmation_msg.id and str(reaction.emoji) in [dungset, saiset]
        
        try:
            reaction, user = await self.client.wait_for("reaction_add", timeout=30.0, check=check)  # Chờ tối đa 30 giây
        except asyncio.TimeoutError:
            await ctx.send("Hết thời gian chờ. Lệnh đã bị hủy.")
            return
        
        # Hủy lệnh nếu người dùng chọn ❌
        if str(reaction.emoji) == saiset:
            await ctx.send("Lệnh đã bị hủy.")
            return

        # Xử lý gửi tin nhắn
        if member is None:
            for user_id in user_ids:
                try:
                    user = await self.client.fetch_user(user_id[0])
                    await user.send(message)
                except discord.Forbidden:
                    pass
            await ctx.send("Đã gửi tin nhắn đến tất cả người dùng trong database.")
        else:
            if member.bot:
                await ctx.send("Không thể gửi tin nhắn đến bot.")
                return
            try:
                await member.send(message)
                await ctx.send(f"Đã gửi tin nhắn đến {member.mention}.")
            except discord.Forbidden:
                await ctx.send(f"Không thể gửi tin nhắn đến {member.mention}. Bạn không có quyền gửi tin nhắn.")

    @commands.command(description="Thêm phần thưởng vào kho người dùng")
    @is_bot_owner()
    async def them_data(self, ctx, member: discord.Member, id_phanthuong: int, so_luong: int):
        """Thêm phần thưởng vào kho người dùng và trừ số lượng trong bảng phan_thuong
        
        Usage: !them_data @user 5 10
        - Thêm 10 phần thưởng ID 5 vào kho của user
        - Trừ 10 từ số lượng của phần thưởng ID 5 trong bảng phan_thuong
        """
        await self._execute_them_data(ctx, member, id_phanthuong, so_luong)

    @them_data.error
    async def them_data_error(self, ctx, error):
        """Xử lý lỗi cho lệnh them_data"""
        if isinstance(error, commands.MemberNotFound):
            await ctx.send(f"❌ Không tìm thấy member: {error.argument}\n💡 Hãy thử dùng `!them_data_id <user_id> <id_phanthuong> <so_luong>` thay thế")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Tham số không hợp lệ. Sử dụng: `!them_data @user <id_phanthuong> <so_luong>`")
        else:
            await ctx.send(f"❌ Lỗi: {str(error)}")

    @commands.command(description="Thêm phần thưởng vào kho người dùng bằng ID")
    @is_bot_owner()
    async def them_data_id(self, ctx, user_id: int, id_phanthuong: int, so_luong: int):
        """Thêm phần thưởng vào kho người dùng bằng user ID
        
        Usage: !them_data_id 123456789 5 10
        - Thêm 10 phần thưởng ID 5 vào kho của user có ID 123456789
        """
        try:
            member = await self.client.fetch_user(user_id)
            await self._execute_them_data(ctx, member, id_phanthuong, so_luong)
        except discord.NotFound:
            await ctx.send(f"❌ Không tìm thấy user với ID: {user_id}")
        except Exception as e:
            await ctx.send(f"❌ Lỗi: {str(e)}")

    async def _execute_them_data(self, ctx, member, id_phanthuong: int, so_luong: int):
        """Logic chính để thêm phần thưởng vào kho người dùng"""
        if so_luong <= 0:
            await ctx.send("❌ Số lượng phải lớn hơn 0")
            return
            
        # Kiểm tra user có trong database không
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (member.id,))
        if not cursor.fetchone():
            await ctx.send("❌ User chưa được đăng ký trong hệ thống")
            return
            
        # Lấy thông tin phần thưởng
        cursor.execute("SELECT id, name_phanthuong, soluong_phanthuong, emoji_phanthuong FROM phan_thuong WHERE id = ?", (id_phanthuong,))
        phan_thuong_data = cursor.fetchone()
        
        if not phan_thuong_data:
            await ctx.send(f"❌ Không tìm thấy phần thưởng với ID {id_phanthuong}")
            return
            
        phan_thuong_id, ten_phanthuong, soluong_hientai, emoji_phanthuong = phan_thuong_data
        
        # Kiểm tra số lượng có đủ không
        if soluong_hientai < so_luong:
            await ctx.send(f"❌ Không đủ số lượng! Hiện tại chỉ còn {soluong_hientai} {ten_phanthuong}")
            return
            
        try:
            # Bắt đầu transaction
            conn.execute('BEGIN TRANSACTION')
            
            # Lấy open_items của user
            cursor.execute("SELECT open_items FROM users WHERE user_id = ?", (member.id,))
            result = cursor.fetchone()
            open_items_data = result[0] if result else None
            open_items_dict = json.loads(open_items_data) if open_items_data else {}
            
            # Cập nhật hoặc thêm mới phần thưởng vào kho user
            if ten_phanthuong in open_items_dict:
                # Đã có phần thưởng này, cộng thêm số lượng
                open_items_dict[ten_phanthuong]["so_luong"] += so_luong
            else:
                # Chưa có, tạo mới
                open_items_dict[ten_phanthuong] = {
                    "emoji": emoji_phanthuong,
                    "name_phanthuong": ten_phanthuong,
                    "so_luong": so_luong
                }
            
            # Sắp xếp lại theo emoji
            sorted_open_items = dict(
                sorted(open_items_dict.items(), key=lambda item: item[1]["emoji"]))
            updated_open_items = json.dumps(sorted_open_items)
            
            # Cập nhật kho của user
            cursor.execute("UPDATE users SET open_items = ? WHERE user_id = ?", (updated_open_items, member.id))
            
            # Trừ số lượng trong bảng phan_thuong
            new_quantity = soluong_hientai - so_luong
            cursor.execute("UPDATE phan_thuong SET soluong_phanthuong = ? WHERE id = ?", (new_quantity, id_phanthuong))
            
            # Commit transaction
            conn.commit()
            
            # Tạo embed báo thành công
            embed = discord.Embed(
                title="✅ Thêm phần thưởng thành công",
                color=0x00ff00
            )
            
            emoji_str = f"<:emoji:{emoji_phanthuong}>" if str(emoji_phanthuong).isdigit() else str(emoji_phanthuong)
            
            embed.add_field(
                name="👤 Người nhận", 
                value=member.mention, 
                inline=True
            )
            embed.add_field(
                name="🎁 Phần thưởng", 
                value=f"{emoji_str} {ten_phanthuong}", 
                inline=True
            )
            embed.add_field(
                name="📊 Số lượng", 
                value=f"**+{so_luong:,}**", 
                inline=True
            )
            # embed.add_field(
            #     name="🏪 Còn lại trong kho", 
            #     value=f"{new_quantity:,}", 
            #     inline=True
            # )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            # Rollback nếu có lỗi
            conn.rollback()
            await ctx.send(f"❌ Có lỗi xảy ra: {str(e)}")

async def setup(client):
    await client.add_cog(Velenh(client))