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
            message = await ctx.reply(f"{dauxdo} **Dùng lệnh** **`zmoqua`** **để mở vé** [__**ở đây**__](<https://discord.com/channels/832579380634451969/1147035278465310720>)")
            await asyncio.sleep(10)
            await message.delete()
            await ctx.message.delete()
            return False
        return True
    return commands.check(predicate)


def is_allowed_channel_check():
    async def predicate(ctx):
        allowed_channel_ids = [1273768834830041301, 1273769137985818624, 993153068378116127, 1026627301573677147, 1035183712582766673, 1090897131486842990, 1213122881802997770, 1147355133622108262, 1295144686536888340, 1207593935359320084]
        if ctx.channel.id not in allowed_channel_ids:
            await ctx.send(f"{dauxdo} **Dùng lệnh** **`zinv`** [__**ở đây**__](<https://discord.com/channels/832579380634451969/1147355133622108262>)")
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
            await ctx.send(f"{dauxdo} **Dùng lệnh** **`zdaily`** [__**ở đây**__](<https://discord.com/channels/832579380634451969/1147355133622108262>)")
            return False
        return True
    return commands.check(predicate)

def is_guild_owner_or_bot_owner():
    async def predicate(ctx):
        return ctx.author == ctx.guild.owner or ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222 or ctx.author.id == 1307765539896033312 or ctx.author.id == 928879945000833095 or ctx.author.id == 962627128204075039
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
dauxdo = "<a:hgtt_check:1246910030444495008>"
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
daily_streak1 = "<a:lich_daily:1362248474166427759>"
daily_streak2 = "<:lich:1313829453826359398>"
chamthan = "<:chamthann:1233135104281411757>"
quatienowo = "<:qua:1183804744725168148>"
nhayvang = "<a:dotvang:1215606222942896128>"
nhaysao = "<a:nhaysao:1284496637623926784>"
quatienpink = "<:qua:1242529922870673528>"
ngoisao = "<a:ngoisao:1284490593829130250>"
momo = "<:momo:1180104032208048209>"
time_daily = "<a:dongho_daily:1362251621974802492>"
daily_love = "<a:daily_love:1314586830082932806>"
chamthanvang = "<:chamthanvang:1331908568521248779>"

# Emoji quà
kco = "<:0noel_hgtt_chamthan:1313775980141350954>"
tienvnd = "<:hgtt_tien_vnd:1235115910445142037>"
quatienowo_hong = "<:qua_daily:1362768668899016885>"
nhayxanh = "<a:dotxanh:1215606225492774993>"
nhayhong = "<a:dothong:1215606220367466506>"
nhayvang = "<a:nhayvang1:1331714375370932336>"
nhayhong1 = "<a:nhayhong:1331714335919046657>"
phaohoa = "<a:phaohoatron:1331714384107671642>"
quatienowo = "<:qua_tien:1331708095180701736>"
quathantai = "<:qua_thantai:1331708087714713680>"
quaphaohoa = '<a:qua_phaohoa:1362785063376257024>'
quahoasen = '<a:qua_hoasen:1362785074843746636>'
quanonla = '<a:qua_nonla:1362785090198831156>'
quaaodai = '<a:qua_aodai:1362785102458781726>'
quakc = '<:qua_kc:1364061782733357147>'

dungset = '<a:dung1:1340173892681072743>'
saiset = '<a:sai1:1340173872535703562>'
trong = '<:trong:1314626864639115275>'

cotco = '<:1_cotco:1363275556451520512>'
langbac = '<:2_langbac:1363275565968396389>'
chuamotcot = '<:3_chuamotcot:1363275576403693700>'
vanmieu = '<:4_vanmieu:1363275589083070546>'
thaprua = '<:5_thaprua:1363275597304037497>'
vinhhl = '<:6_vhl:1363275619474866256>'
chuathienmu = '<:7_chuathienmu:1363275628861722806>'
codohue = '<:8_codohue:1363275643906687087>'
cauvang = '<:9_cauvang:1363275652656271563>'
hoian = '<:10_hoian:1363275662659686682>'
chobenthanh = '<:11_chobenthanh:1363275671727509704>'
nhatho = '<:12_nhatho:1363275680942395512>'
dinhdoclap = '<:13_dinhdoclap:1363277847770431570>'
bennharong = '<:14_benhanrong:1363275703088447539>'
chonoi = '<:15_chonoi:1363275712211189760>'

class Daily_30_4(commands.Cog):
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
        self.tangqua = None
        self.tienhatgiong = None
        self.nauan = None
        self.tickdunghong = None

    async def cog_load(self):
        """Called when the cog is loaded - Discord.py 2.0+ recommended way"""
        await self.init_emojis()

    async def init_emojis(self):
        self.guild = self.client.get_guild(1090136467541590066)
        self.vevang = await self.guild.fetch_emoji(1192461054131847260)
        self.vekc = await self.guild.fetch_emoji(1146756758665175040)
        self.users = await self.guild.fetch_emoji(1181378307548250163)
        self.dk = await self.guild.fetch_emoji(1181400074127945799)
        self.inv = await self.guild.fetch_emoji(1159077258535907328)
        self.clock = await self.guild.fetch_emoji(1159077258535907328)
        self.chamthan = await self.guild.fetch_emoji(1179452469017858129)
        self.tangqua = await self.guild.fetch_emoji(1170709400470687806)
        self.tienhatgiong = await self.guild.fetch_emoji(1192458078294122526)
        self.nauan = await self.guild.fetch_emoji(1192458078294122526)
        self.tickdunghong = await self.guild.fetch_emoji(1186838952544575538)

    async def check_command_disabled(self, ctx):  
        guild_id = str(ctx.guild.id)  
        command_name = ctx.command.name.lower()  
        if guild_id in self.client.get_cog('Toggle').toggles:  
            if command_name in self.client.get_cog('Toggle').toggles[guild_id]:  
                if ctx.channel.id in self.client.get_cog('Toggle').toggles[guild_id][command_name]:  
                    await ctx.send(f"Lệnh `{command_name}` đã bị tắt ở kênh này.")  
                    return True  
        return False 

    # @commands.hybrid_command(aliases=["CHECK", "Check"], description="xem có bao nhiêu vé")
    # @is_guild_owner_or_bot_owner()
    # async def check(self, ctx):
    #     if is_registered(ctx.author.id):
    #         cursor.execute(
    #             "SELECT num_gold_tickets_available, num_diamond_tickets_available, quantity_tickets FROM ve_database WHERE id = ?", (1,))
    #         ve_db_result = cursor.fetchone()

    #         if ve_db_result:
    #             num_gold_tickets_available = ve_db_result[0]
    #             num_diamond_tickets_available = ve_db_result[1]
    #             quantity_tickets = ve_db_result[2]
    #             soluongconlai = 50 - quantity_tickets
    #             embed = discord.Embed(
    #                 title=f"", color=discord.Color.magenta())
    #             embed.add_field(
    #                 name="", value=f"Số vé còn lại trong ngày: {soluongconlai} {self.tienhatgiong}", inline=False)
    #             embed.add_field(
    #                 name="", value=f"Số vé còn lại trong tháng: {num_gold_tickets_available} {self.vevang} và {num_diamond_tickets_available} {self.vekc}", inline=False)
    #             await ctx.send(embed=embed, ephemeral=True)
    #         else:
    #             return None
    #     else:
    #         await ctx.send(f"{self.dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")

    # @commands.command(aliases=["VE", "Ve"], description="Tặng vé vàng cho người dùng")
    # @is_guild_owner_or_bot_owner()
    # async def ve(self, ctx, nguoi_nhan: discord.User, so_luong: int):
    #     # Kiểm tra xem kênh có ID là 1147035278465310720 hay không
    #     if ctx.channel.id == 1104362707580375120:
    #         return None
    #     else:
    #         if not is_registered(ctx.author.id):
    #             await ctx.send(f"{self.dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
    #         else:
    #             if nguoi_nhan is None or so_luong is None or so_luong < 1:
    #                 await ctx.send("Vd: ztang `user` `1`")
    #                 return
    #             if nguoi_nhan.bot:  # Không cho phép trao đổi với bot
    #                 await ctx.send("Không thể thực hiện trao đổi với bot.")
    #                 return
    #             if ctx.author.id == nguoi_nhan.id:
    #                 await ctx.send("Không thể tặng vé cho bản thân")
    #                 return
    #             # Kiểm tra người dùng chưa đăng ký
    #             if not is_registered(ctx.author.id):
    #                 await ctx.send(f"{self.dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
    #                 return
    #             cursor.execute(
    #                 "SELECT num_gold_tickets FROM users WHERE user_id = ?", (ctx.author.id,))
    #             sender_result = cursor.fetchone()
    #             if not sender_result:
    #                 await ctx.send("Không thể tải thông tin vé của bạn.")
    #                 return
    #             ve_type = "num_gold_tickets"
    #             sender_ve = sender_result[0]
    #             if sender_ve < so_luong:
    #                 await ctx.send(f"{self.chamthan} Bạn k đủ vé {self.vevang} để tặng. **Chăm chat & voice** trong sv để sở hữu thêm vé nha")
    #                 return
    #             cursor.execute("SELECT id, kimcuong, " + ve_type +
    #                         " FROM users WHERE user_id = ?", (nguoi_nhan.id,))
    #             receiver_result = cursor.fetchone()
    #             if not receiver_result:
    #                 await ctx.send(f"{self.dk} người nhận chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
    #                 return
    #             new_sender_ve = sender_ve - so_luong
    #             new_receiver_ve = receiver_result[2] + so_luong  # Cập nhật cột "num_gold_tickets"
    #             new_receiver_kimcuong = receiver_result[1] + so_luong  # Thêm vào cột "kimcuong"
    #             cursor.execute("UPDATE users SET " + ve_type +
    #                         " = ? WHERE user_id = ?", (new_sender_ve, ctx.author.id))
    #             cursor.execute("UPDATE users SET " + ve_type + " = ?, kimcuong = ? WHERE id = ?", (new_receiver_ve, new_receiver_kimcuong, receiver_result[0]))
    #             conn.commit()
    #             await ctx.send(f"{self.tangqua} **| {ctx.author.mention} đã tặng {nguoi_nhan.mention} {so_luong} {self.vevang}**.")

    @commands.command( description="Mở vé vàng hoặc kim cương")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @is_allowed_channel()
    async def moqua(self, ctx, loai_ve: str = None):
        if await self.check_command_disabled(ctx):
            return
        if not is_registered(ctx.author.id):
            await ctx.send(f"{self.chamthan} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` tại kênh <#1147355133622108262> để đăng kí")
        else:
            if loai_ve is None:
                loai_ve = "vang"
            elif loai_ve not in ["vang", "kc"]:
                await ctx.send("Vui lòng chỉ mở vé vàng (`vang`) hoặc vé kim cương (`kc`).")
                return
            if loai_ve == "kc":
                min_id = 1
                max_id = 4
            elif loai_ve == "vang":
                min_id = 5
                max_id = 28
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
            selected_phan_thuong = random.choice(phan_thuong_co_the_mo)
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

        if phan_thuong[0] == 1 or phan_thuong[0] == 2:
            embed = discord.Embed(
                title=f"{quakc} **Chúc mừng {ctx.author.mention}, bạn nhận được** __**{phan_thuong[1]}**__ {phan_thuong[3]}", color=discord.Color.from_rgb(51, 0, 255))
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/1053799649938505889/1364060812800561172/discord_fake_avatar_decorations_1745287827020.gif"
            )
            await ctx.send(embed=embed)
        elif phan_thuong[0] == 3:
            embed = discord.Embed(
                title=f"{quakc} **Chúc mừng {ctx.author.mention}, bạn nhận được** __**{phan_thuong[1]}k**__ {phan_thuong[3]}", color=discord.Color.from_rgb(51, 0, 255))
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/1211199649667616768/1331718238522048663/discord_fake_avatar_decorations_1737574867767.gif"
            )
            await ctx.send(embed=embed)
        elif phan_thuong[0] == 4:
            cursor.execute(
                "UPDATE users SET xu_hlw = xu_hlw + 5 WHERE user_id = ?", (ctx.author.id,))
            conn.commit()
            embed = discord.Embed(
                title=f"{quakc} **Chúc mừng {ctx.author.mention}, bạn nhận được** __**{phan_thuong[1]}**__ {phan_thuong[3]}", color=discord.Color.from_rgb(51, 0, 255))
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/1053799649938505889/1364060812800561172/discord_fake_avatar_decorations_1745287827020.gif"
            )
            await ctx.send(embed=embed) 
        elif phan_thuong[0] == 5:
            await ctx.send(f"{quaphaohoa} **Chúc mừng {ctx.author.mention}, bạn đã bốc trúng síc rịt:** **{phan_thuong[1]}** {phan_thuong[3]}")    
        elif phan_thuong[0] == 6 or phan_thuong[0] == 7 or phan_thuong[0] == 8 or phan_thuong[0] == 9 or phan_thuong[0] == 10:
            await ctx.send(f"{quatienowo} **Chúc mừng {ctx.author.mention}, bạn nhận được** __**{phan_thuong[1]}**__ {phan_thuong[3]}")
        elif phan_thuong[0] == 11:
            cursor.execute(
                "UPDATE users SET balance = balance + 100000 WHERE user_id = ?", (ctx.author.id,))
            conn.commit()
            await ctx.send(f"{quatienowo_hong} **Chúc mừng {ctx.author.mention}, bạn nhận được** **{phan_thuong[1]}** {phan_thuong[3]}")
        elif phan_thuong[0] == 12:
            cursor.execute(
                "UPDATE users SET balance = balance + 200000 WHERE user_id = ?", (ctx.author.id,))
            conn.commit()
            await ctx.send(f"{quatienowo_hong} **Chúc mừng {ctx.author.mention}, bạn nhận được** **{phan_thuong[1]}** {phan_thuong[3]}")
        elif phan_thuong[0] == 13 or phan_thuong[0] == 14 or phan_thuong[0] == 26 or phan_thuong[0] == 27 or phan_thuong[0] == 28:
            await ctx.send(f"# {phan_thuong[3]} Mời {ctx.author.mention} thưởng thức món __{phan_thuong[1]}__")
        elif phan_thuong[0] == 15:
            await ctx.send(f"{quaphaohoa} **Chúc mừng {ctx.author.mention}, , bạn được tặng 1** **{phan_thuong[1]}** {phan_thuong[3]}{phan_thuong[3]}{phan_thuong[3]}")
        elif phan_thuong[0] == 16:
            await ctx.send(f"{quaphaohoa} **Chúc mừng {ctx.author.mention}, , bạn được xem {phan_thuong[1]} miễn phí** {phan_thuong[3]}{phan_thuong[3]}{phan_thuong[3]}")
        elif phan_thuong[0] == 17 or phan_thuong[0] == 18 or phan_thuong[0] == 19 or phan_thuong[0] == 20 or phan_thuong[0] == 21 :
            await ctx.send(f"{quaaodai} **Chúc mừng {ctx.author.mention}, bạn được tặng 1** **{phan_thuong[1]}**\n# {trong}{trong}{trong} {list_emoji.xu_event}  {phan_thuong[3]}  {list_emoji.xu_event}")
        elif phan_thuong[0] == 22:
            await ctx.send(f"{quahoasen} **{ctx.author.mention} được tặng 1** __**{phan_thuong[1]}**__ {phan_thuong[3]}")
        elif phan_thuong[0] == 23:
            await ctx.send(f"{quatienowo_hong} **{ctx.author.mention} được tặng 1** __**{phan_thuong[1]}**__ {phan_thuong[3]}")
        elif phan_thuong[0] == 24 or phan_thuong[0] == 25:
            await ctx.send(f"{quanonla} **{ctx.author.mention} được tặng 1** __**{phan_thuong[1]}**__ {phan_thuong[3]}")

    @commands.command(aliases=["inv", "INV","Inv"], description="Hiển thị danh sách inventory")
    #@is_allowed_channel_check()
    async def inventory(self, ctx):
        if await self.check_command_disabled(ctx):
            return
        if not is_registered(ctx.author.id):
            await ctx.send(f"{self.dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
            return

        user_id = ctx.author.id
        cursor.execute("SELECT open_items, daily_streak FROM users WHERE user_id = ?", (user_id,))
        open_items_data, daily_streak = cursor.fetchone()
        open_items_dict = json.loads(open_items_data) if open_items_data else {}

        # Định nghĩa các tập tên
        monetary_names = {"10k", "20k", "50k", "100k", "200k", "500k",
                        "100,000", "200,000", "500,000",
                        "1,000,000", "2,000,000", "20,000", "20"}
        reward_mapping = {
            "1_cotco": cotco, "2_langbac": langbac, "3_chuamotcot": chuamotcot,
            "4_vanmieu": vanmieu, "5_thaprua": thaprua, "6_vinhhl": vinhhl,
            "7_chuathienmu": chuathienmu, "8_codohue": codohue, "9_cauvang": cauvang,
            "10_hoian": hoian, "11_chobenthanh": chobenthanh, "12_nhatho": nhatho,
            "13_dinhdoclap": dinhdoclap, "14_benhanrong": bennharong, "15_chonoi": chonoi
        }
        reward_names = set(reward_mapping.keys())

        # Phân loại items
        normal_items   = []
        monetary_items = []
        reward_items   = []

        for name, data in open_items_dict.items():
            if name in reward_names:
                reward_items.append((name, data))
            elif name in monetary_names:
                monetary_items.append((name, data))
            else:
                normal_items.append((name, data))

        # Hàm hỗ trợ sort theo emoji
        sort_key = lambda kv: kv[1]["emoji"]

        normal_items.sort(key=sort_key)
        monetary_items.sort(key=sort_key)
        reward_items.sort(key=sort_key)

        # Embed cơ bản
        embed = discord.Embed(color=discord.Color.from_rgb(242, 226, 6))
        avatar_url = ctx.author.avatar.url if ctx.author.avatar else "https://cdn.discordapp.com/embed/avatars/0.png"
        embed.set_author(name=f"Kho của {ctx.author.display_name}", icon_url=avatar_url)

        if not open_items_dict:
            embed.add_field(
                name=f"", value=f"{chamthan} **Kho trống, chat & voice tại sv để nhận {self.vevang} nha**")
        else:
            # Hàm thêm group items vào embed
            def add_group(group_list):
                if not group_list:
                    return
                items_per_line = 6
                line_fields = []
                for idx, (name, data) in enumerate(group_list, start=1):
                    emoji_str = data["emoji"]
                    qty_sup   = get_superscript(data["so_luong"])

                    # Chuẩn hoá tên hiển thị tiền tệ
                    disp_name = name
                    mapping = {
                        "20,000": "20k", "100,000": "100k", "200,000": "200k",
                        "500,000": "500k", "1,000,000": "1M", "2,000,000": "2M"
                    }
                    if name in mapping:
                        disp_name = mapping[name]
                    # Nếu là tiền tệ thì in đậm tên
                    if disp_name in {"10k","20k","50k","100k","200k","500k","1M","2M"}:
                        field_text = f"**{disp_name}** {emoji_str} **{qty_sup}**"
                    # Nếu là reward thì chỉ emoji + số lượng
                    elif name in reward_names:
                        field_text = f"{emoji_str} **{qty_sup}**"
                    else:
                        field_text = f"{emoji_str} **{qty_sup}**"

                    line_fields.append(field_text)
                    if idx % items_per_line == 0 or idx == len(group_list):
                        embed.add_field(name="", value="  ".join(line_fields), inline=False)
                        line_fields = []

            # 1) Normal → 2) Monetary → 3) Reward
            add_group(normal_items)
            add_group(monetary_items)
            add_group(reward_items)

            # 4) Daily streak
            embed.add_field(
                name="", 
                value=f"{daily_streak1} **Daily streak:** __**{daily_streak}**__ **ngày**",
                inline=False
            )

            # 5) Check‑in count (số reward đã thu thập)
            checkin_count = sum(1 for name, data in reward_items if data["so_luong"] > 0)
            embed.add_field(
                name="", 
                value=f"**{list_emoji.checkin} Địa điểm** __**{checkin_count}/15**__", 
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(description="Reset các cột trong các bảng dữ liệu")
    @is_guild_owner_or_bot_owner()
    async def rsve(self, ctx):
        # Reset bảng users
        cursor.execute(
            "UPDATE users SET num_gold_tickets = 0, num_diamond_tickets = 0, open_items = '', total_tickets = 0, daily_streak = 0, last_daily = 0, daily_tickets = 0, kimcuong = 0")
        # Reset bảng ve_database
        cursor.execute(
            "UPDATE ve_database SET num_gold_tickets_available = 3385, num_diamond_tickets_available = 55, quantity_tickets = 0, tong_tickets = 0, daily_keo = 0, daily_bonus1 = 0, daily_bonus2 = 0, daily_bonus3 = 0, daily_bonus4 = 0, daily_nglieu1 = 0, daily_nglieu2 = 0, daily_nglieu3 = 0, daily_nglieu4 = 0")
        # Xóa và thêm lại các dòng trong bảng phan_thuong theo danh sách mới
        danh_sach_phan_thuong = [
            ("500,000", 20, 1284735146515365959),  # 1 vé kim cương
            ("1,000,000", 10, 1284735146515365959),  # 2 vé kim cương
            ("20", 5, 1180104032208048209),  # 3 vé kim cương
            ("5 lá cờ", 20, 1361079100609003610),  # 4 vé kim cương
            ("cái nịt", 20, 1284474488909598741),  # 5 
            ("10k", 30, 1284735146515365959),  # 6
            ("20k", 30, 1284735146515365959),  # 7
            ("50k", 50, 1284735146515365959),  # 8
            ("100k", 30, 1284735146515365959),  # 9
            ("200k", 20, 1284735146515365959),  # 10
            ("100,000", 30, 1192458078294122526),  # 11
            ("200,000", 30, 1192458078294122526),  # 12
            ("phở", 40, 1361788630988886126),  # 13
            ("gỏi cuốn", 70, 1360462338620129376),  # 14
            ("tràng pháo tay", 20, 1362774481873014894),  # 15
            ("pháo hoa", 30, 1362774537518977125),  # 16
            ("áo dài xanh lá", 60, 1360872151346839562),  # 17
            ("áo dài vàng", 40, 1360870448803352586),  # 18 ------ quà bonus
            ("áo dài trắng", 50, 1361557143152492805),  # 19
            ("áo dài đỏ", 350, 1360872246251491419),  # 20
            ("áo dài xanh dương", 350, 1360870445683052694),  # 21
            ("hoa sen", 225, 1360872799534842036),  # 22
            ("quạt giấy", 370, 1364059902556770304),  # 23
            ("nón lá", 205, 1360877147207504023),  # 24 
            ("đôi dép tổ ong", 205, 1361047861139214456),  # 25 ------ quà daily
            ("cà phê trứng", 475, 1360462351505297583),  # 26
            ("bánh mì", 475, 1360462358908109010),  # 27
            ("bánh xèo", 175, 1360462343875596589),  # 28
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
            await channel.send(f"# ĐÃ RESET DAILY THÀNH CÔNG!!!")

    @reset_daily_task.before_loop
    async def before_reset_daily_task(self):
        await self.client.wait_until_ready()

    @commands.command(aliases=["DAILY", "Daily"], description="Điểm danh mỗi ngày")
    @is_daily_channel()
    async def daily(self, ctx):
        if await self.check_command_disabled(ctx):
            return

        if not is_registered(ctx.author.id):
            await ctx.send(f"{trong} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
            return

        user_id = ctx.author.id
        now = datetime.datetime.utcnow() + timedelta(hours=7)

        cursor.execute("SELECT last_daily, daily_streak FROM users WHERE user_id = ?", (user_id,))
        last_daily, daily_streak = cursor.fetchone()

        cursor.execute("SELECT daily_keo, daily_bonus1, daily_bonus2, daily_bonus3, daily_bonus4, daily_nglieu1, daily_nglieu2, daily_nglieu3, daily_nglieu4 FROM ve_database")
        (daily_keo, daily_bonus1, daily_bonus2, daily_bonus3, daily_bonus4,
         daily_nglieu1, daily_nglieu2, daily_nglieu3, daily_nglieu4) = cursor.fetchone()

        reset_time = datetime.datetime(now.year, now.month, now.day, 15, 0) + timedelta(days=1)
        time_left = reset_time - now
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_left_str = f"{hours}h{minutes}m{seconds}s"

        if last_daily != 0:
            await ctx.send(f"{time_daily} | Bạn đã điểm danh hôm nay rồi! Lượt điểm danh tiếp theo còn: **{time_left_str}**")
            return

        cursor.execute("UPDATE users SET daily_streak = daily_streak + 1, last_daily = ? WHERE user_id = ?", (now, user_id))
        conn.commit()

        cursor.execute("SELECT daily_streak FROM users WHERE user_id = ?", (user_id,))
        daily_streak = cursor.fetchone()[0]

        donator_roles = [1021383533178134620, 1082887622311022603, 1056244443184906361,
                         1055759097133277204, 1055758414678069308, 1055519421424222208, 1117282898052141188]
        is_donator = any(role.id in donator_roles for role in ctx.author.roles)
        balance_increase = 20000 if is_donator else 10000
        coin_kc_increase = 3 if is_donator else 1

        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ? WHERE user_id = ?", (balance_increase, coin_kc_increase, user_id))
        conn.commit()

        donator_role_id = next((role.id for role in ctx.author.roles if role.id in donator_roles), None)
        donator_info = f"- <@&{donator_role_id or donator_roles[0]}>: **10k {self.tienhatgiong} + 2 {list_emoji.xu_event}**"

        got_bonus = False
        selected_phan_thuong = None

        if random.random() <= 0.9 and daily_keo <= 120 and \
            (daily_bonus1 <= 15 or daily_bonus2 <= 15 or daily_bonus3 <= 15 or daily_bonus4 <= 15) and \
            (daily_nglieu1 <= 30 or daily_nglieu2 <= 10 or daily_nglieu3 <= 10 or daily_nglieu4 <= 10):
            cursor.execute("SELECT * FROM phan_thuong WHERE id BETWEEN 20 AND 28")
            phan_thuong_list = cursor.fetchall()
            phan_thuong_con_lai = [pt for pt in phan_thuong_list if pt[2] > 0]
            if phan_thuong_con_lai:
                selected_phan_thuong = random.choice(phan_thuong_con_lai)
                await self.cap_nhat_ve_daily(user_id, selected_phan_thuong)
                got_bonus = True

        embed = discord.Embed(title="", color=discord.Color.from_rgb(255, 122, 228))
        avatar_url = ctx.author.avatar.url if ctx.author.avatar else "https://cdn.discordapp.com/embed/avatars/0.png"
        embed.set_author(name=f"{ctx.author.display_name} daily thành công", icon_url=avatar_url)

        if got_bonus:
            embed.add_field(
                name="",
                value=f"- {daily_streak1} | Daily streak __**{daily_streak}**__\n"
                      f"- {quatienowo_hong} | Quà daily: **10k {self.tienhatgiong} + 1 {list_emoji.xu_event}**\n"
                      f"{donator_info}\n"
                      f"- {selected_phan_thuong[3]} | Quà bonus: **{selected_phan_thuong[1]}**\n"
                      f"- {time_daily} | Next daily: **`{time_left_str}`**",
                inline=False
            )
            daily_mapping = {
                20: "daily_bonus1", 21: "daily_bonus2", 22: "daily_bonus3", 23: "daily_bonus4",
                24: "daily_nglieu1", 25: "daily_nglieu2", 26: "daily_nglieu3", 27: "daily_nglieu4", 28: "daily_nglieu4"
            }
            column_name = daily_mapping.get(selected_phan_thuong[0])
            if column_name:
                cursor.execute(f"UPDATE ve_database SET {column_name} = {column_name} + 1")
            cursor.execute("UPDATE phan_thuong SET soluong_phanthuong = soluong_phanthuong - 1 WHERE id = ?", (selected_phan_thuong[0],))
        else:
            embed.add_field(
                name="",
                value=f"- {daily_streak1} | Daily streak __**{daily_streak}**__\n"
                      f"- {quatienowo_hong} | Quà daily: **10k {self.tienhatgiong} + 1 {list_emoji.xu_event}**\n"
                      f"{donator_info}\n"
                      f"- {trong} | Quà bonus: không có\n"
                      f"- {time_daily} | Next daily: **`{time_left_str}`**",
                inline=False
            )

        cursor.execute("UPDATE ve_database SET daily_keo = daily_keo + 1")
        conn.commit()
        await ctx.send(embed=embed)

    async def cap_nhat_ve_daily(self, user_id, phan_thuong):
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
        
    @commands.command(aliases=["RSDAILY", "Rsdaily"], description="set lại số vé hàng ngày")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @is_guild_owner_or_bot_owner()
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

    @commands.command(aliases=["RSDAILYly", "Rsdailyly"], description="set lại số vé hàng ngày")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @is_guild_owner_or_bot_owner()
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

    @commands.command(aliases=["SETTONGVE", "Settongve"], description="set tổng số vé nhận được cho người khác")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @is_guild_owner_or_bot_owner()
    async def settongve(self, ctx, user: discord.User, so_luong: int):
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user.id,))
        user_data = cursor.fetchone()
        if user_data is None:
            await ctx.send(f"{self.dk} người nhận chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
            return
        cursor.execute("UPDATE users SET kimcuong = kimcuong + ? WHERE user_id = ? ", (so_luong, user.id))
        conn.commit()

    @commands.command(aliases=["SETVE", "Setve"], description="Set số lượng cho cột num_gold_tickets và num_diamond_tickets bảng users")
    @is_guild_owner_or_bot_owner()
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

    @commands.command(aliases=["SEND", "Send"], description="Gửi tin nhắn đến người dùng khả dụng trong database")
    @is_guild_owner_or_bot_owner()
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

async def setup(client):
    await client.add_cog(Daily_30_4(client))