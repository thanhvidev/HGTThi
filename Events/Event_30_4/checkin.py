import asyncio
import random
import re
import typing
import discord
import sqlite3
from discord.ext import commands
from discord.ui import Button, View
from Commands.Mod.list_emoji import list_emoji
import json

conn = sqlite3.connect('economy.db', isolation_level=None)
conn.execute('pragma journal_mode=wal')
cursor = conn.cursor()

def is_registered(user_id):  # Hàm kiểm tra xem người dùng đã được đăng ký hay chưa
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None


def is_guild_owner_or_bot_owner():
    async def predicate(ctx):
        return ctx.author == ctx.guild.owner or ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222 or ctx.author.id == 1307765539896033312 or ctx.author.id == 928879945000833095 or ctx.author.id == 1242425610303836251
    return commands.check(predicate)


def is_staff():
    async def predicate(ctx):
        guild_owner = ctx.author == ctx.guild.owner
        bot_owner = ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222
        specific_role = any(role.id == 1113463122515214427 for role in ctx.author.roles)
        return guild_owner or bot_owner or specific_role
    return commands.check(predicate)

def is_marry():
    async def predicate(ctx):
        role_marry = any(role.id == 1339482195907186770 for role in ctx.author.roles)
        return role_marry
    return commands.check(predicate)

def get_superscript(n):
    superscripts = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    return str(n).translate(superscripts)

def is_allowed_channel():
    async def predicate(ctx):
        allowed_channel_id = 1295144686536888340
        if ctx.channel.id != allowed_channel_id:
            await ctx.send(f"{dauxdo} **Dùng lệnh** **`zvn`** [__**ở đây**__](<https://discord.com/channels/832579380634451969/1295144686536888340>)")
            return False
        return True
    return commands.check(predicate)

# Đọc giá trị từ blindbox.json
def load_blindbox_data():
    with open('blindbox.json', 'r') as f:
        data = json.load(f)
        return data['options'], data['weights']

# Lấy giá trị options và weights từ file
options, weights = load_blindbox_data()


dung = '<a:dung1:1340173892681072743>'
sai = '<a:sai1:1340173872535703562>'
dauxdo = "<a:hgtt_check:1246910030444495008>"
emojidung = "<a:nhan_love:1339523828161708105>"
emojisai = "<:hgtt_sai:1186839020974657657>"
# Định nghĩa các biến
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

# quà
checkin = list_emoji.checkin
lacovn = list_emoji.xu_event
dk = list_emoji.dk
timvn = list_emoji.timvn
trong = list_emoji.trong
vn_hcm = '<:vn_hcm:1363271581375140020>'
vn_hoasen = '<:vn_hoasen:1363271592175734865>'
vn_hoasen2 = '<:vn_hoasen2:1363284334005452840>'
vn_rua = '<:vn_rua:1363271606343831652>'
vn_aodai = '<:vn_aodai:1363271629236338819>'
vn_nui = '<:vn_nui:1363271619564405006>'
vn_hoian = '<a:vn_hoian:1363271656134541322>'
vn_linh = '<:vn_linh:1363271665525592144>'
vn_linh2 = '<:vn_linh2:1364057985080627250>'
vn_maybay = '<a:vn_maybay:1363271676347027677>'
vn_thuyen = '<:vn_thuyen:1363271681497366668>'
vn_bongbong = '<:vn_bongbong:1363285925999808603>'
 
class Checkin(commands.Cog):
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

    @commands.hybrid_command(aliases=["vietnam"], description="")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @is_allowed_channel()
    async def vn(self, ctx):
        if await self.check_command_disabled(ctx):
            return
        user_id = ctx.author.id
        if not is_registered(user_id):
            await ctx.send(f"{dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
            return
        cursor.execute("SELECT xu_hlw, open_items FROM users WHERE user_id = ?", (user_id,))  
        result = cursor.fetchone()
        if result:
            xu_hlw = result[0]
        else:
            xu_hlw = 0
        if xu_hlw < 1:
            await ctx.send(f"> **{ctx.author.mention} k đủ {lacovn} để chơi rồi, hãy làm nhiệm vụ để có thêm xu nhé!**")
            return
        message1 = await ctx.channel.send(f"# Du lịch Việt Nam thôiii!\n# {trong} {lacovn} {vn_maybay} {vn_maybay} {vn_maybay} {lacovn}",)

        cursor.execute("UPDATE users SET xu_hlw = xu_hlw - 1 WHERE user_id = ?", (user_id,))
        conn.commit()

        chosen_random = random.choices(options, weights=weights, k=1)[0]

        await asyncio.sleep(9)
        await self.cap_nhat_checkin(ctx, chosen_random)

        if chosen_random == 1:
            await message1.edit(content=f"# {checkin} {ctx.author.mention} đã checkin tại cột cờ Lũng cú - cực Bắc của Tổ Quốc\n# {trong}{trong}{trong}{timvn}   {cotco}   {timvn}")
        elif chosen_random == 2:
            await message1.edit(content=f"# {checkin} {ctx.author.mention} viếng thăm Lăng Chủ tịch Hồ Chí Minh\n# {trong}{trong}{trong}{vn_hcm}   {langbac}   {vn_hcm}")
        elif chosen_random == 3:
            await message1.edit(content=f"{checkin} {ctx.author.mention} **đã ghé thăm Chùa Một Cột - biểu tượng văn hóa ngàn năm của Hà Nội**\n# {trong}{trong}{trong}{vn_hoasen}   {chuamotcot}   {vn_hoasen2}")
        elif chosen_random == 4:
            await message1.edit(content=f"{checkin} {ctx.author.mention} **đã đến tham quan Văn Miếu – Quốc Tử Giám - ngôi trường Đại học đầu tiên ở nước ta**\n# {trong}{trong}{trong}{vn_rua}   {vanmieu}   {vn_rua}")
        elif chosen_random == 5:
            await message1.edit(content=f"{checkin} {ctx.author.mention} **đã check in tại Tháp Rùa Hồ Gươm - viên ngọc sáng của thủ đô Hà Nội**\n# {trong}{trong}{trong}{timvn}   {thaprua}   {timvn}")
        elif chosen_random == 6:
            await message1.edit(content=f"{checkin} {ctx.author.mention} **đã du lịch đến Vịnh Hạ Long - di sản thiên nhiên thế giới kỳ vĩ**\n# {trong}{trong}{trong}{vn_nui}   {vinhhl}   {vn_nui}")
        elif chosen_random == 7:
            await message1.edit(content=f"{checkin} {ctx.author.mention} **đã ghé thăm Chùa Thiên Mụ - ngôi chùa cổ bậc nhất cố đô Huế**\n# {trong}{trong}{trong}{timvn}   {chuathienmu}   {timvn}")
        elif chosen_random == 8:
            await message1.edit(content=f"# {checkin} {ctx.author.mention} đã đến tham quan quần thể di tích cố đô Huế cổ kính\n# {trong}{trong}{trong}{vn_aodai}   {codohue}   {vn_aodai}")
        elif chosen_random == 9:
            await message1.edit(content=f"{checkin} {ctx.author.mention} **đã check in tại Cầu Vàng Đà Nẵng - kiệt tác kiến trúc độc đáo trên đỉnh Bà Nà**\n# {trong}{trong}{trong}{timvn}   {cauvang}   {timvn}")
        elif chosen_random == 10:
            await message1.edit(content=f"# {checkin} {ctx.author.mention} đã du lịch đến Phố cổ Hội An - di sản văn hóa thế giới\n# {trong}{trong}{trong}{vn_hoian}   {hoian}   {vn_hoian}")
        elif chosen_random == 11:
            await message1.edit(content=f"# {checkin} {ctx.author.mention} đã check in tại chợ Bến Thành - ngôi chợ trải qua 4 thế kỷ ở Sài Gòn\n# {trong}{trong}{trong}{timvn}   {chobenthanh}   {timvn}")
        elif chosen_random == 12:
            await message1.edit(content=f"# {checkin} {ctx.author.mention} đã check in tại nhà thờ Đức Bà Paris - Sài Gòn\n# {trong}{trong}{trong}{timvn}   {nhatho}   {timvn}")
        elif chosen_random == 13:
            await message1.edit(content=f"# {checkin} {ctx.author.mention} đã đến tham quan Dinh Độc Lập\n# {trong}{trong}{trong}{vn_linh}   {dinhdoclap}   {vn_linh2}")
        elif chosen_random == 14:
            await message1.edit(content=f"# {checkin} {ctx.author.mention} đã đến tham quan Bến Nhà Rồng - nơi in dấu chân Bác\n# {trong}{trong}{trong}{vn_bongbong}   {bennharong}   {vn_bongbong}")
        elif chosen_random == 15:
            await message1.edit(content=f"# {checkin} {ctx.author.mention} đã đến tham quan và trải nghiệm chợ nổi miền Tây\n# {trong}{trong}{trong}{vn_thuyen}   {chonoi}   {vn_thuyen}")
                    
    async def cap_nhat_checkin(self, ctx, chosen_random):
        user_id = ctx.author.id  
        cursor.execute("SELECT open_items FROM users WHERE user_id = ?", (user_id,))  
        result = cursor.fetchone()  
        open_items_data = result[0] if result else None  
        open_items_dict = json.loads(open_items_data) if open_items_data else {}  

        reward_items = {  
            1: {"name": "1_cotco", "emoji": cotco},  
            2: {"name": "2_langbac", "emoji": langbac},
            3: {"name": "3_chuamotcot", "emoji": chuamotcot},
            4: {"name": "4_vanmieu", "emoji": vanmieu},
            5: {"name": "5_thaprua", "emoji": thaprua},
            6: {"name": "6_vinhhl", "emoji": vinhhl},
            7: {"name": "7_chuathienmu", "emoji": chuathienmu},
            8: {"name": "8_codohue", "emoji": codohue},
            9: {"name": "9_cauvang", "emoji": cauvang},
            10: {"name": "10_hoian", "emoji": hoian},
            11: {"name": "11_chobenthanh", "emoji": chobenthanh},
            12: {"name": "12_nhatho", "emoji": nhatho},
            13: {"name": "13_dinhdoclap", "emoji": dinhdoclap},
            14: {"name": "14_benhanrong", "emoji": bennharong},
            15: {"name": "15_chonoi", "emoji": chonoi},  
        }  

        if chosen_random in reward_items:  
            item_name = reward_items[chosen_random]["name"]  
            item_emoji = reward_items[chosen_random]["emoji"]  
            
            if item_name in open_items_dict:  
                open_item = open_items_dict[item_name]  
                open_item["emoji"] = item_emoji  # Updating the emoji  
                open_item["so_luong"] += 1       # Incrementing quantity  
            else:  
                open_items_dict[item_name] = {  
                    "emoji": item_emoji,  
                    "name_phanthuong": item_name,  
                    "so_luong": 1  
                }  

        # Sorting the items based on emoji  
        sorted_open_items = dict(  
            sorted(open_items_dict.items(), key=lambda item: item[1]["emoji"]))  
        open_items_data = json.dumps(sorted_open_items)  
        
        cursor.execute("UPDATE users SET open_items = ? WHERE user_id = ?", (open_items_data, user_id))  
        conn.commit()

    @vn.error
    async def vn_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = divmod(int(error.retry_after), 60)  # Chia cho 60 để có phút và giây
            formatted_time = f"{remaining_time[0]}m{remaining_time[1]}s"
            message = await ctx.send(f"{dauxdo} | Vui lòng đợi thêm `{formatted_time}` để có thể sử dụng lệnh này!!")
            await asyncio.sleep(2)
            await message.delete()
            await ctx.message.delete()
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @is_guild_owner_or_bot_owner()
    async def tilequa1(self, ctx, *, new_weights: str):
        try:
            # Chuyển chuỗi new_weights thành danh sách số nguyên
            weights_list = list(map(int, new_weights.split(",")))

            # Kiểm tra xem số lượng trọng số có khớp với danh sách options không
            if len(weights_list) != len(options):
                await ctx.send(f"{emojisai} Số lượng trọng số phải đúng bằng số lượng options ({len(options)}).")
                return

            # Cập nhật giá trị weights trong file JSON
            with open('blindbox.json', 'r') as f:
                data = json.load(f)

            data['weights'] = weights_list

            with open('blindbox.json', 'w') as f:
                json.dump(data, f, indent=4)

            # Cập nhật giá trị weights trong bộ nhớ
            global weights
            weights = weights_list

            await ctx.send(f"{emojidung} đã thay đổi tỉ lệ : {weights_list}")

        except ValueError:
            await ctx.send(f"{emojisai} Vui lòng nhập các số cách nhau bởi dấu phẩy.")
        except Exception as e:
            await ctx.send(f"{emojisai} Đã xảy ra lỗi: {e}")

    @commands.command( description="reset xu event")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @is_guild_owner_or_bot_owner()
    async def rsxu(self, ctx):
        # Gửi thông báo xác nhận reset cho tất cả thành viên
        msg = await ctx.send("Bạn có chắc chắn muốn reset xu love của tất cả thành viên?")
        await msg.add_reaction(dung)
        await msg.add_reaction(sai)

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in [dung, sai] and reaction.message.id == msg.id

        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=30.0, check=check)
            if str(reaction.emoji) == dung:
                cursor.execute("UPDATE users SET xu_hlw = 0")
                conn.commit()
                await msg.edit(content="Đã reset xu của tất cả thành viên")
            else:
                await msg.edit(content="Lệnh đã bị hủy.")
        except asyncio.TimeoutError:
            await msg.edit(content="Bạn không phản ứng kịp thời, lệnh đã bị hủy.")

    @commands.command( description="set xu event cho người khác")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @is_guild_owner_or_bot_owner()
    async def setxu(self, ctx, amount: int, member: typing.Optional[discord.Member] = None):
        formatted_amount = "{:,}".format(amount)
        if member is None:  # Nếu không nhập người dùng, set cho tất cả người dùng trong bảng users
            msg = await ctx.send(f"Bạn có chắc chắn muốn trao tặng **{formatted_amount}** {lacovn} cho tất cả thành viên?")
            await msg.add_reaction(dung)
            await msg.add_reaction(sai)
            
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in [dung, sai] and reaction.message.id == msg.id
            
            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=30.0, check=check)
                if str(reaction.emoji) == dung:
                    cursor.execute("UPDATE users SET xu_hlw = xu_hlw + ?", (amount,))
                    conn.commit()
                    await msg.edit(content=f"**HGTT đã trao tặng** __**{formatted_amount}**__ {lacovn} **cho tất cả thành viên**")
                else:
                    await msg.edit(content="Lệnh đã bị hủy.")
            except asyncio.TimeoutError:
                await msg.edit(content="Bạn không phản ứng kịp thời, lệnh đã bị hủy.")
        elif is_registered(member.id):
            msg = await ctx.send(f"Bạn có chắc chắn muốn trao tặng **{formatted_amount}** {lacovn} cho {member.display_name}?")
            await msg.add_reaction(dung)
            await msg.add_reaction(sai)
            
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in [dung, sai] and reaction.message.id == msg.id
            
            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=30.0, check=check)
                if str(reaction.emoji) == dung:
                    cursor.execute("UPDATE users SET xu_hlw = xu_hlw + ? WHERE user_id = ?", (amount, member.id))
                    conn.commit()
                    await msg.edit(content=f"**HGTT đã trao tặng** __**{formatted_amount}**__ {lacovn} **cho {member.display_name}**")
                else:
                    await msg.edit(content="Lệnh đã bị hủy.")
            except asyncio.TimeoutError:
                await msg.edit(content="Bạn không phản ứng kịp thời, lệnh đã bị hủy.")
        else:
            await ctx.send("Bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")


async def setup(client):
    await client.add_cog(Checkin(client))