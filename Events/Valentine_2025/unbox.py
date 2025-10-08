import asyncio
import random
import re
import typing
import discord
import sqlite3
from discord.ext import commands
from discord.ui import Button, View
import json

conn = sqlite3.connect('economy.db', isolation_level=None)
conn.execute('pragma journal_mode=wal')
cursor = conn.cursor()

def is_registered(user_id):  # Hàm kiểm tra xem người dùng đã được đăng ký hay chưa
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None


def is_guild_owner_or_bot_owner():
    async def predicate(ctx):
        return ctx.author == ctx.guild.owner or ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222
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
            await ctx.send(f"{dauxdo} **Dùng lệnh** **`ztet`** [__**ở đây**__](<https://discord.com/channels/832579380634451969/1295144686536888340>)")
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

dk = "<:profile:1181400074127945799>"
dauxdo = "<a:hgtt_check:1246910030444495008>"
emojidung = "<a:nhan_love:1339523828161708105>"
emojisai = "<:hgtt_sai:1186839020974657657>"
load = "<a:decor_load:1314595908771385405>"
onggia = "<:0noel_hgtt_santa:1313775940236738652>"
so0 = "<a:babythree:1314464947979419679>"
box1 = "<:box1:1314622910929047642>"
box2 = "<a:box2:1314623812192567296>"
daucach = "<:trong:1314626864639115275>"
noelcoin = "<a:xutet_2025:1329244935945195530>"
xmas = "<:xmas:1314888946785976350>"
wow = "<:wow:1315178872005853225>"
trong = "<:trong:1314626864639115275>"
nhanlove = '<a:nhan_love:1339523828161708105>'
xulove = '<a:xulove_2025:1339490786840150087>'
nhanlove = '<a:nhan_love:1339523828161708105>'

# quà
hoa = "<a:hoahong_2025:1339516229618237502>"
nuochoa = "<a:nuochoa:1339516275055136809>"
keotraitim = '<a:keotraitim:1339516240552656957>'
hopsocola = '<:hopsocola:1339516253144088617>'
carybara = '<a:carybarahong:1339516263533383690>'
iphone = '<:iphone:1339516297720893460>'
apple = '<:applewatch:1339516367451324448>'
xecon = "<:xehoihong:1339516310190817351>"
start_qua = '<a:start_qua:1339659691546120414>'
end_qua = '<a:end_qua:1339659701637615687>'
hopqua = '<:quadaily_vlt:1339536375392768071>'
end_trai = '<:end_trai:1339660040931508366>'
enh_phai = '<:end_phai:1339660047344734228>'
muiten_end = '<a:muiten_end:1339660293554307225>'
traitim ='<a:traitim_tim:1339661134646607995>'
qua_hut = '<:qua_khongtrung:1339663877855776810>'
cainit = '<:cainit:1339671369985691712>'
dung = '<a:dung1:1340173892681072743>'
sai = '<a:sai1:1340173872535703562>'

class Valentine2025View(discord.ui.View):
    def __init__(self,enable_buttons, timeout: float = 180.0):
        super().__init__(timeout=timeout)
        self.enable_buttons = enable_buttons

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.enable_buttons:
            return True
        else:
            await interaction.response.send_message("Bảng quà này của người khác", ephemeral=True)
            return False

    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    # async def disable_button_for(self, button_name: str, duration: int):
    #     button = getattr(self, button_name)
    #     button.disabled = True
    #     await self.message.edit(view=self)
    #     await asyncio.sleep(duration)
    #     button.disabled = False
    #     await self.message.edit(view=self)

    async def disable_buttons(self, duration: int):  
        # Vô hiệu hóa cả hai nút  
        self.qua.disabled = True
        await self.message.edit(view=self)  # Cập nhật giao diện  
        await asyncio.sleep(duration)  # Chờ trong thời gian đã chỉ định  
        self.qua.disabled = False
        await self.message.edit(view=self)  # Cập nhật giao diện  

    async def on_timeout(self) -> None:
        await self.disable_all_items()
        return await super().on_timeout()

    @discord.ui.button(label="Quay", style=discord.ButtonStyle.gray, emoji="<a:start_qua:1339659691546120414>", custom_id="qua", disabled=False)
    async def qua(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        user_id = interaction.user.id
        cursor.execute("SELECT xu_love, marry, bxh_love FROM users WHERE user_id = ?", (user_id,))  
        result = cursor.fetchone()
        if result:
            xu_love = result[0]
        else:
            xu_love = 0
        if xu_love < 25:
            await interaction.followup.send(f"> **{interaction.user.mention} k đủ {xulove} để quay quà, hãy làm nhiệm vụ để có thêm xu nhé!**")
            return
        message1 = await interaction.channel.send(f"# {hopqua} Quay quà tặng người iu cùng {interaction.user.mention}",)
        message2 = await interaction.channel.send(f"{trong} {traitim}{trong}{start_qua}{trong}{traitim}")
        cursor.execute("UPDATE users SET xu_love = xu_love - 25 WHERE user_id = ?", (user_id,))
        conn.commit()
        chosen_random = random.choices(options, weights=weights, k=1)[0]

        await self.disable_buttons(9)

        if chosen_random == 1:
            cursor.execute("UPDATE users SET bxh_love = bxh_love + 15 WHERE user_id = ? OR marry LIKE ?", (user_id, f"%{interaction.user.mention}%"))
            await message1.edit(content=f"# {end_qua} Là __Hoa hồng__ {muiten_end}{interaction.user.mention} và ng ấy được + __15 điểm__ 𝑽𝒂𝒍𝒆𝒏𝒕𝒊𝒏𝒆 {end_qua}")
            await message2.edit(content=f"{trong}{end_trai}{trong}{hoa}{trong}{enh_phai}")
        elif chosen_random == 2:
            cursor.execute("UPDATE users SET bxh_love = bxh_love + 20 WHERE user_id = ? OR marry LIKE ?", (user_id, f"%{interaction.user.mention}%"))
            await message1.edit(content=f"# {end_qua} Là __Kẹo trái tim__ {muiten_end}{interaction.user.mention} và ng ấy được + __20 điểm__ 𝑽𝒂𝒍𝒆𝒏𝒕𝒊𝒏𝒆 {end_qua}")
            await message2.edit(content=f"{trong}{end_trai}{trong}{keotraitim}{trong}{enh_phai}")
        elif chosen_random == 3:
            cursor.execute("UPDATE users SET bxh_love = bxh_love + 25 WHERE user_id = ? OR marry LIKE ?", (user_id, f"%{interaction.user.mention}%"))
            await message1.edit(content=f"# {end_qua} Là __Socola__ {muiten_end}{interaction.user.mention} và ng ấy được + __25 điểm__ 𝑽𝒂𝒍𝒆𝒏𝒕𝒊𝒏𝒆 {end_qua}")
            await message2.edit(content=f"{trong}{end_trai}{trong}{hopsocola}{trong}{enh_phai}")
        elif chosen_random == 4:
            cursor.execute("UPDATE users SET bxh_love = bxh_love + 30 WHERE user_id = ? OR marry LIKE ?", (user_id, f"%{interaction.user.mention}%"))
            await message1.edit(content=f"# {end_qua} Là __Gấu bông Capybara__ {muiten_end}{interaction.user.mention} và ng ấy được + __30 điểm__ 𝑽𝒂𝒍𝒆𝒏𝒕𝒊𝒏𝒆 {end_qua}")
            await message2.edit(content=f"{trong}{end_trai}{trong}{carybara}{trong}{enh_phai}")
        elif chosen_random == 5:
            cursor.execute("UPDATE users SET bxh_love = bxh_love + 35 WHERE user_id = ? OR marry LIKE ?", (user_id, f"%{interaction.user.mention}%"))
            await message1.edit(content=f"# {end_qua} Là __Nước hoa__ {muiten_end}{interaction.user.mention} và ng ấy được + __35 điểm__ 𝑽𝒂𝒍𝒆𝒏𝒕𝒊𝒏𝒆 {end_qua}")
            await message2.edit(content=f"{trong}{end_trai}{trong}{nuochoa}{trong}{enh_phai}")
        elif chosen_random == 6:
            cursor.execute("UPDATE users SET bxh_love = bxh_love + 45 WHERE user_id = ? OR marry LIKE ?", (user_id, f"%{interaction.user.mention}%"))
            await message1.edit(content=f"# {end_qua} Là __Đồng hồ__ {muiten_end}{interaction.user.mention} và ng ấy được + __45 điểm__ 𝑽𝒂𝒍𝒆𝒏𝒕𝒊𝒏𝒆 {end_qua}")
            await message2.edit(content=f"{trong}{end_trai}{trong}{apple}{trong}{enh_phai}")
        elif chosen_random == 7:
            cursor.execute("UPDATE users SET bxh_love = bxh_love + 50 WHERE user_id = ? OR marry LIKE ?", (user_id, f"%{interaction.user.mention}%"))
            await message1.edit(content=f"# {end_qua} Là __Iphone pink__ {muiten_end}{interaction.user.mention} và ng ấy được + __50 điểm__ 𝑽𝒂𝒍𝒆𝒏𝒕𝒊𝒏𝒆 {end_qua}")
            await message2.edit(content=f"{trong}{end_trai}{trong}{iphone}{trong}{enh_phai}")
        elif chosen_random == 8:
            cursor.execute("UPDATE users SET bxh_love = bxh_love + 60 WHERE user_id = ? OR marry LIKE ?", (user_id, f"%{interaction.user.mention}%"))
            await message1.edit(content=f"# {end_qua} Là __Xe Hơi__ {muiten_end}{interaction.user.mention} và ng ấy được + __60 điểm__ 𝑽𝒂𝒍𝒆𝒏𝒕𝒊𝒏𝒆 {end_qua}")
            await message2.edit(content=f"{trong}{end_trai}{trong}{xecon}{trong}{enh_phai}")
        else:
            await message1.edit(content=f"# {qua_hut} *~~Xịt rồi, chúc {interaction.user.mention} may mắn lần sau!~~*")
            await message2.edit(content=f"{trong}{end_trai}{trong}{cainit}{trong}{enh_phai}")
        conn.commit()
 
class Valentine2025(commands.Cog):
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

    @commands.hybrid_command( description="Quay quà tặng")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @is_allowed_channel()
    @is_marry()
    async def qua1(self, ctx):
        if await self.check_command_disabled(ctx):
            return
        user_id = ctx.author.id
        if not is_registered(user_id):
            await ctx.send(f"{dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
            return

        enable_buttons = user_id
        view = Valentine2025View(enable_buttons)
        message = await ctx.reply(view=view)
        view.message = message
        await view.wait()

    @qua1.error
    async def tet_error(self, ctx, error):
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
    async def tilequa(self, ctx, *, new_weights: str):
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

    @commands.command( description="reset xu valentine")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @is_guild_owner_or_bot_owner()
    async def rsxuvlt(self, ctx):
        # Gửi thông báo xác nhận reset cho tất cả thành viên
        msg = await ctx.send("Bạn có chắc chắn muốn reset xu love của tất cả thành viên?")
        await msg.add_reaction(dung)
        await msg.add_reaction(sai)

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in [dung, sai] and reaction.message.id == msg.id

        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=30.0, check=check)
            if str(reaction.emoji) == dung:
                cursor.execute("UPDATE users SET xu_love = 0")
                conn.commit()
                await msg.edit(content="Đã reset xu của tất cả thành viên")
            else:
                await msg.edit(content="Lệnh đã bị hủy.")
        except asyncio.TimeoutError:
            await msg.edit(content="Bạn không phản ứng kịp thời, lệnh đã bị hủy.")

    @commands.command( description="set xu love cho người khác")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @is_guild_owner_or_bot_owner()
    async def setxuvlt(self, ctx, amount: int, member: typing.Optional[discord.Member] = None):
        formatted_amount = "{:,}".format(amount)
        if member is None:  # Nếu không nhập người dùng, set cho tất cả người dùng trong bảng users
            msg = await ctx.send(f"Bạn có chắc chắn muốn trao tặng **{formatted_amount}** {xulove} cho tất cả thành viên?")
            await msg.add_reaction(dung)
            await msg.add_reaction(sai)
            
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in [dung, sai] and reaction.message.id == msg.id
            
            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=30.0, check=check)
                if str(reaction.emoji) == dung:
                    cursor.execute("UPDATE users SET xu_love = xu_love + ?", (amount,))
                    conn.commit()
                    await msg.edit(content=f"**HGTT đã trao tặng** __**{formatted_amount}**__ {xulove} **cho tất cả thành viên**")
                else:
                    await msg.edit(content="Lệnh đã bị hủy.")
            except asyncio.TimeoutError:
                await msg.edit(content="Bạn không phản ứng kịp thời, lệnh đã bị hủy.")
        elif is_registered(member.id):
            msg = await ctx.send(f"Bạn có chắc chắn muốn trao tặng **{formatted_amount}** {xulove} cho {member.display_name}?")
            await msg.add_reaction(dung)
            await msg.add_reaction(sai)
            
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in [dung, sai] and reaction.message.id == msg.id
            
            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=30.0, check=check)
                if str(reaction.emoji) == dung:
                    cursor.execute("UPDATE users SET xu_love = xu_love + ? WHERE user_id = ?", (amount, member.id))
                    conn.commit()
                    await msg.edit(content=f"**HGTT đã trao tặng** __**{formatted_amount}**__ {xulove} **cho {member.display_name}**")
                else:
                    await msg.edit(content="Lệnh đã bị hủy.")
            except asyncio.TimeoutError:
                await msg.edit(content="Bạn không phản ứng kịp thời, lệnh đã bị hủy.")
        else:
            await ctx.send("Bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")


    @commands.command(description="set điểm valentine cho người khác")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @is_guild_owner_or_bot_owner()
    async def setdiemvlt(self, ctx, amount: int, member: typing.Optional[discord.Member] = None):
        if member is None:
            return await ctx.send("**Hãy điền tên người cần set**")
        
        # Lấy thông tin tài khoản của người dùng
        cursor.execute("SELECT marry, bxh_love, xu_love FROM users WHERE user_id = ?", (member.id,))
        result = cursor.fetchone()
        if result is None:
            return await ctx.send("Không tìm thấy thông tin tài khoản của người dùng.")
        
        marry_status = result[0]
        matches = re.findall(r'<@(\d+)>', marry_status)

        if len(matches) == 2:
            formatted_amount = "{:,}".format(amount)
            msg = await ctx.send(f"Bạn có chắc chắn muốn trao tặng **{formatted_amount}** {nhanlove} cho {member.display_name}?")
            await msg.add_reaction(dung)
            await msg.add_reaction(sai)
            
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in [dung, sai] and reaction.message.id == msg.id
            
            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=30.0, check=check)
                if str(reaction.emoji) == dung:
                    user1_id = int(matches[0])
                    user2_id = int(matches[1])
                    cursor.execute(
                        "UPDATE users SET bxh_love = bxh_love + ? WHERE user_id = ? OR user_id = ?",
                        (amount, user1_id, user2_id)
                    )
                    conn.commit()
                    await msg.edit(content=f"**HGTT đã trao tặng** __**{formatted_amount}**__ {nhanlove} **cho {member.display_name}**")
                else:
                    await msg.edit(content="Lệnh đã bị hủy.")
            except asyncio.TimeoutError:
                await msg.edit(content="Bạn không phản ứng kịp thời, lệnh đã bị hủy.")
        else:
            await ctx.send(f"**{member.display_name}** chưa kết hôn")

async def setup(client):
    await client.add_cog(Valentine2025(client))