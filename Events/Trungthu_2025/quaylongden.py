import asyncio
import random
import re
import typing
import discord
import sqlite3
from discord.ext import commands
from discord.ui import Button, View
from Commands.Mod.list_emoji import list_emoji
from utils.checks import is_bot_owner, is_admin, is_mod
import json

conn = sqlite3.connect('economy.db', isolation_level=None)
conn.execute('pragma journal_mode=wal')
cursor = conn.cursor()

def is_registered(user_id):  # Hàm kiểm tra xem người dùng đã được đăng ký hay chưa
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None

def get_superscript(n):
    superscripts = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    return str(n).translate(superscripts)

def is_allowed_channel():
    async def predicate(ctx):
        allowed_channel_id = 1295144686536888340
        if ctx.channel.id != allowed_channel_id:
            await ctx.send(f"{list_emoji.tick_check} **Dùng lệnh** **`zquay`** [__**ở đây**__](<https://discord.com/channels/832579380634451969/1295144686536888340>)")
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

# quà
checkin = list_emoji.checkin
lacovn = list_emoji.xu_event
dk = list_emoji.dk
timvn = list_emoji.timvn
trong = list_emoji.trong
quaylongden = '<a:quaylongden:1418269667461431456>'
lan = '<a:lan1:1417825538629697587>'
lan2 = '<a:lan1:1331757350238945290>'
dotnhay = "<a:hgtt_decor_dep:1413741256596525056>"
nhayxanh = "<a:nhayxanhduong:1418271199473045665>"
nhaylongden = "<a:nhaylongden:1418271345380298874>"

 
class Quaylongden(commands.Cog):
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

    @commands.hybrid_command(aliases=["ld", "longden"], description="")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @is_allowed_channel()
    async def quay(self, ctx):
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
        message1 = await ctx.channel.send(f"{lan}  **Quay lồng đèn đi chơi Trung Thu!**  {lan2}",)
        message2 = await ctx.channel.send(f"{trong}{nhayxanh}  {quaylongden}  {nhayxanh}{trong}")

        cursor.execute("UPDATE users SET xu_hlw = xu_hlw - 1 WHERE user_id = ?", (user_id,))
        conn.commit()

        chosen_random = random.choices(options, weights=weights, k=1)[0]

        await asyncio.sleep(9)
        await self.cap_nhat_checkin(ctx, chosen_random)

        if chosen_random == 1:
            await message1.edit(content=f"{lacovn} **{ctx.author.mention} quay được lồng đèn con thỏ** {longdentho}")
            await message2.edit(content=f"{trong}{nhaylongden}  {longdentho}  {nhaylongden}{trong}")
        elif chosen_random == 2:
            await message1.edit(content=f"{lacovn} **{ctx.author.mention} quay được lồng đèn ngôi sao** {longdensao}")
            await message2.edit(content=f"{trong}{nhaylongden}  {longdensao}  {nhaylongden}{trong}")
        elif chosen_random == 3:
            await message1.edit(content=f"{lacovn} **{ctx.author.mention} quay được lồng đèn gấu dâu** {longdengaudau}")
            await message2.edit(content=f"{trong}{nhaylongden}  {longdengaudau}  {nhaylongden}{trong}")
        elif chosen_random == 4:
            await message1.edit(content=f"{lacovn} **{ctx.author.mention} quay được lồng đèn con gà** {longdenga}")
            await message2.edit(content=f"{trong}{dotnhay}  {longdenga}  {dotnhay}{trong}")
        elif chosen_random == 5:
            await message1.edit(content=f"{lacovn} **{ctx.author.mention} quay được lồng đèn marsupilami** {longdenmarsupilami}")
            await message2.edit(content=f"{trong}{nhaylongden}  {longdenmarsupilami}  {nhaylongden}{trong}")
        elif chosen_random == 6:
            await message1.edit(content=f"{lacovn} **{ctx.author.mention} quay được lồng đèn con cá** {longdenca}")
            await message2.edit(content=f"{trong}{dotnhay}  {longdenca}  {dotnhay}{trong}")
        elif chosen_random == 7:
            await message1.edit(content=f"{lacovn} **{ctx.author.mention} quay được lồng đèn Đô rê mi** {longdendoremi}")
            await message2.edit(content=f"{trong}{dotnhay}  {longdendoremi}  {dotnhay}{trong}")
        elif chosen_random == 8:
            await message1.edit(content=f"{lacovn} **{ctx.author.mention} quay được lồng đèn Đầu Lân** {longdenlan}")
            await message2.edit(content=f"{trong}{dotnhay}  {longdenlan}  {dotnhay}{trong}")
        elif chosen_random == 9:
            await message1.edit(content=f"{lacovn} **{ctx.author.mention} quay được lồng đèn con heo** {longdenheo}")
            await message2.edit(content=f"{trong}{dotnhay}  {longdenheo}  {dotnhay}{trong}")
        elif chosen_random == 10:
            await message1.edit(content=f"{lacovn} **{ctx.author.mention} quay được lồng đèn Pikachu** {longdenpikachu}")
            await message2.edit(content=f"{trong}{dotnhay}  {longdenpikachu}  {dotnhay}{trong}")
        elif chosen_random == 11:
            await message1.edit(content=f"{lacovn} **{ctx.author.mention} quay được lồng đèn Lobby** {longdenlobby}")
            await message2.edit(content=f"{trong}{dotnhay}  {longdenlobby}  {dotnhay}{trong}")
        elif chosen_random == 12:
            await message1.edit(content=f"{lacovn} **{ctx.author.mention} quay được lồng đèn Captain** {longdencaptain}")
            await message2.edit(content=f"{trong}{dotnhay}  {longdencaptain}  {dotnhay}{trong}")
        elif chosen_random == 13:
            await message1.edit(content=f"{lacovn} **{ctx.author.mention} quay được lồng đèn Đô rê mon** {longdendoremon}")
            await message2.edit(content=f"{trong}{dotnhay}  {longdendoremon}  {dotnhay}{trong}")
        elif chosen_random == 14:
            await message1.edit(content=f"{lacovn} **{ctx.author.mention} quay được lồng đèn người nhện** {longdennguoinhen}")
            await message2.edit(content=f"{trong}{dotnhay}  {longdennguoinhen}  {dotnhay}{trong}")
        elif chosen_random == 15:
            await message1.edit(content=f"{lacovn} **{ctx.author.mention} quay được lồng đèn con bướm** {longdenbuom}")
            await message2.edit(content=f"{trong}{dotnhay}  {longdenbuom}  {dotnhay}{trong}")

    async def cap_nhat_checkin(self, ctx, chosen_random):
        user_id = ctx.author.id  
        cursor.execute("SELECT open_items FROM users WHERE user_id = ?", (user_id,))  
        result = cursor.fetchone()  
        open_items_data = result[0] if result else None  
        open_items_dict = json.loads(open_items_data) if open_items_data else {}  

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

    @quay.error
    async def quay_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = divmod(int(error.retry_after), 60)  # Chia cho 60 để có phút và giây
            formatted_time = f"{remaining_time[0]}m{remaining_time[1]}s"
            message = await ctx.send(f"{list_emoji.tick_check} | Vui lòng đợi thêm `{formatted_time}` để có thể sử dụng lệnh này!!")
            await asyncio.sleep(2)
            await message.delete()
            await ctx.message.delete()
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @is_bot_owner()
    async def tileld(self, ctx, *, new_weights: str):
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
    @is_bot_owner()
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
    @is_bot_owner()
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

    @commands.command(description="Thêm lồng đèn vào kho người dùng")
    @is_bot_owner()
    async def them_ev(self, ctx, member: discord.Member, longden_id: int, so_luong: int):
        if member is None:
            member = ctx.author
            
        if not is_registered(member.id):
            await ctx.send(f"{dk} **{member.display_name}** chưa đăng ký tài khoản")
            return
            
        if so_luong <= 0:
            await ctx.send(f"{sai} Số lượng phải lớn hơn 0")
            return
            
        if longden_id < 1 or longden_id > 15:
            await ctx.send(f"{sai} ID lồng đèn phải từ 1-15")
            return
            
        # Dictionary ánh xạ ID với thông tin lồng đèn
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
        
        try:
            cursor.execute("SELECT open_items FROM users WHERE user_id = ?", (member.id,))  
            result = cursor.fetchone()  
            open_items_data = result[0] if result else None  
            open_items_dict = json.loads(open_items_data) if open_items_data else {}
            
            item_name = reward_items[longden_id]["name"]  
            item_emoji = reward_items[longden_id]["emoji"]
            
            if item_name in open_items_dict:  
                open_item = open_items_dict[item_name]  
                open_item["emoji"] = item_emoji
                open_item["so_luong"] += so_luong
            else:  
                open_items_dict[item_name] = {  
                    "emoji": item_emoji,  
                    "name_phanthuong": item_name,  
                    "so_luong": so_luong
                }
            
            # Sắp xếp theo emoji
            sorted_open_items = dict(  
                sorted(open_items_dict.items(), key=lambda item: item[1]["emoji"]))  
            open_items_data = json.dumps(sorted_open_items)  
            
            cursor.execute("UPDATE users SET open_items = ? WHERE user_id = ?", (open_items_data, member.id))  
            conn.commit()
            
            await ctx.send(f"{dung} **Đã thêm {so_luong} {item_emoji} {item_name} vào kho của {member.display_name}**")
            
        except Exception as e:
            await ctx.send(f"{sai} **Lỗi:** {str(e)}")


async def setup(client):
    await client.add_cog(Checkin(client))