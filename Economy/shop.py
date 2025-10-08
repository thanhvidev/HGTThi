import asyncio
import json
import re
import discord
import sqlite3
from discord.ext import commands

conn = sqlite3.connect('economy.db', isolation_level=None)
cursor = conn.cursor()
conn.execute('pragma journal_mode=wal')

# Tạo bảng trong cơ sở dữ liệu (nếu chưa tồn tại)
cursor.execute('''CREATE TABLE IF NOT EXISTS shops
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              price INTEGER NOT NULL,
              emoji_id TEXT NOT NULL,
              love TEXT)''')
conn.commit()

def is_registered(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None

def is_allowed_channel_checkmarry():
    async def predicate(ctx):
        allowed_channel_ids = [1273769188988682360, 1273769137985818624, 1273768884885000326, 1273768834830041301]
        if ctx.channel.id in allowed_channel_ids:
            return False
        return True
    return commands.check(predicate)

canhtrai ='<:shop1:1339298735913701417>'
canhphai ='<:shop1:1339298735913701417>'
pinkcoin = "<:timcoin:1192458078294122526>"
gach = "<a:line:1181341865786740796>"
emojitimhong = "<a:hgtt_tim:1096818657864200324>"
emojibuy = "<:muaqua:1202483418240131092>"
emojiqua = "<:shopqua_hong:1339298763381932184>"
emojinhan = "<:shop_hong:1339298726497357927>"
emojidaucong = "<:daucong:1202483312250200094>"
emojimuiten = "<:muiten:1202483264250581023>"
sai = "<:hgtt_sai:1186839020974657657>"
shopemoji1 = "<:emoji_53:1272533490285674609>"
shopemoji2 = "<:emoji_52:1272533340733444188>"
nhan1 = "<:nhan_1:1339260319666671728>"
nhan2 = "<:nhan_2:1339260358006804480>"
nhan3 = "<:nhan_3:1339260367611625515>"
nhan4 = "<:nhan_4:1339260384653082675>"
nhan5 = "<:nhan_5:1339674465021333597>"
nhan6 = "<:nhan_6:1339260414890082381>"
nhan7 = "<:nhan_7:1339260426600321085>"
nhan8 = "<:nhan_8:1339260452256878643>"
nhan9 = "<:nhan_9:1339260464848175196>"
nhan10 = "<:nhan_10:1339260958408966235>"
nhan11 = "<:nhan_11:1339505848979820595>"
nhan12 = "<a:nhan_12:1339506181508694017>"
nhan13 = "<a:nhan_13:1339505868655427605>"
nhan14 = "<a:nhan_14:1339506479056814102>"
tienhatgiong = "<:timcoin:1192458078294122526>"
tuixachtim = "<:tuiqua_hong:1339298756876828722>"
so1 = '<:1_:1267453141771878523>'
so2 = '<:2_:1267453158305566791>'
so3 = '<:3_:1267453168560640081>'
so4 = '<:4_:1267453179247984651>'
so5 = '<:5_:1267453189414846574>'
so6 = '<:6_:1267453199070269473>'
so7 = '<:7_:1267453210193301544>'
so8 = '<:8_:1267453220448370761>'
so9 = '<:9_:1267453232158867495>'
so0 = '<:0_:1267455519149527142>'
so10 = '<:so10:1272842835300843644>'
so11 = '<:so11:1339298228784468040>'
so12 = '<:so12:1339298238318252163>'
so13 = '<:so13:1339298247935660142>'
so14 = '<:so14:1339298256844361738>'
chang1 = "<:chang1:1273829645514575874>"
chang2 = "<:chang2:1273829654565748777>"
chang3 = "<:chang3:1273829665819070604>"
chang4 = "<:chang4:1273829674287628308>"
chang5 = "<:chang5:1273829682743218227>"
laplanh = "<a:laplanh:1272858881487540234>"
pre = "<:muitenhong_trai:1339301198104100915>"
nex = "<:muitenhong_phai:1339301206752755875>"
hoa = "<a:hoahong_2025:1339516229618237502>"
quatraitim = "<:emoji_43:1273617890716811355>"
nuochoa = "<a:nuochoa:1339516275055136809>"
gau = "<:gaubong:1194442133575319692> "
keotraitim = '<a:keotraitim:1339516240552656957>'
hopsocola = '<:hopsocola:1339516253144088617>'
carybara = '<a:carybarahong:1339516263533383690>'
iphone = '<:iphone:1339516297720893460>'
apple = '<:applewatch:1339516367451324448>'
xecon = "<:xehoihong:1339516310190817351>"
shopqua = "<:shopqua_hong:1339298763381932184>"
shopnhan = "<:hopnhan_hong:1339298746256720032>"
thanmat = "<a:emoji_50:1273622387358957618>"
tuixachvang = "<:emoji_52:1273632489965097057>"
hopqua = '<:qua:1192540636700745728>'
timqua = "<a:timqua:1273655499191095306>"
matcuoi = "<:shop_hong:1339298726497357927>"
nhanlove = '<a:nhan_love:1339523828161708105>'
xu_love = '<a:xu_love_2025:1339490786840150087>'

prices = ["215,000", "415,000", "615,000", "1,215,000", "2,215,000", "2,950,000", "3,850,000", "4,680,000", "5,950,000", "6,850,000","8,650,000","9,950,000","26,999,000","99,000,000", "50,000", "100,000", "200,000", "300,000", "400,000", "500,000", "1,000,000", "10,000,000"]

diemlove = ["1", "2", "6", "8", "10", "12", "25", "300"]

names =[
    "Nhẫn bạc đính đá cầu vồng",
    "Nhẫn bạc đính đá tím",
    "Nhẫn bạc đá lửa xanh hình bướm dễ thương",
    "Nhẫn bạc nơ hồng đính đá",
    "Nhẫn bạc đính đá hình hoa",
    "Nhẫn bạc đính đá trái tim",
    "Nhẫn vàng trắng hoa đá ruby",
    "Nhẫn vàng 14K đính đá",
    "Nhẫn vàng trắng 14K đính đá xanh",
    "Nhẫn vàng đính đá hồng",
    "Nhẫn vàng trắng 14K đính ngọc trai", #11
    "Nhẫn kim cương vàng trắng 18K vương miện", #12
    "Nhẫn kim cương vàng trắng 18K",#13
    "Nhẫn kim cương vàng trắng 18K giới hạn", #14
    "Hoa hồng", #15
    "Kẹo trái tim", #16
    "Chocolate", #17
    "Gấu bông Capybara",  #18
    "Nước hoa",  #19
    "Đồng hồ", #20
    "Iphone pink", #21
    "Xe hơi dễ thương"  #22
]
image_urls = [
    "https://cdn.discordapp.com/attachments/1338238106381582378/1338757713420746814/nhan_1.png", #1
    "https://cdn.discordapp.com/attachments/1338238106381582378/1338758270579507270/nhann_10.png", #2
    "https://cdn.discordapp.com/attachments/1338238106381582378/1338758760474083355/hgtt_15.png", #3
    "https://media.discordapp.net/attachments/1338238106381582379/1338942460088287364/silver-diamond-ring-with-a-bow-in-pink-.png", #4
    "https://cdn.discordapp.com/attachments/1339303289753309225/1339330049148584068/hgtt_36.png", #5
    "https://media.discordapp.net/attachments/1338238106381582379/1338942863035207892/diamond-silver--ring-light-pink-heart_3.png", #6
    "https://cdn.discordapp.com/attachments/1338238106381582378/1338762864231452672/nhann_5.png", #7
    "https://cdn.discordapp.com/attachments/1338238106381582378/1338764203367858226/13.png", #8
    "https://cdn.discordapp.com/attachments/1338238106381582378/1338764518343442432/16.png", #19
    "https://media.discordapp.net/attachments/1338238106381582379/1338770372740386877/pink-diamond-ring_2.png", #10
    "https://cdn.discordapp.com/attachments/1338238106381582378/1338765185476984924/nhan_5.png", #11
    "https://cdn.discordapp.com/attachments/1339303289753309225/1339307844595355802/hgtt_5.gif", #12
    "https://cdn.discordapp.com/attachments/1339303289753309225/1339319783350337537/hgtt_12.gif", #13
    "https://cdn.discordapp.com/attachments/1339303289753309225/1339309276748972170/hgtt_6.gif", #14
    "https://media.discordapp.net/attachments/1339303289753309225/1339493315137110037/hgtt_33.gif", #15
    "https://media.discordapp.net/attachments/1339303289753309225/1339492618530459728/hgtt_32.gif", #16
    "https://media.discordapp.net/attachments/1339303289753309225/1339493315539632148/hgtt_49.png", #17
    "https://media.discordapp.net/attachments/1339303289753309225/1339495033027559505/hgtt_35.gif", #18
    "https://cdn.discordapp.com/attachments/1339303289753309225/1339495032406933606/hgtt_34.gif", #19
    "https://media.discordapp.net/attachments/1339303289753309225/1339492618173677588/hgtt_47.png", #20
    "https://media.discordapp.net/attachments/1339303289753309225/1339492619104817243/hgtt_48.png", #21
    "https://media.discordapp.net/attachments/1339303289753309225/1339492619767513102/hgtt_4.png", #22                                                           
]



def is_guild_owner_or_bot_owner():
    async def predicate(ctx):
        guild_owner = ctx.author == ctx.guild.owner
        bot_owner = ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222
        specific_role = any(role.id == 1113463122515214427 for role in ctx.author.roles)

        return guild_owner or bot_owner or specific_role
    
    return commands.check(predicate)

def format_gia(gia):
    if gia >= 1000000:
        return f"{gia // 1000000}M"
    elif gia >= 1000:
        return f"{gia // 1000}k"
    else:
        return str(gia)

class ShopView(discord.ui.View):  
    def __init__(self, enable_buttons, default_embed: discord.Embed, embeds: list[discord.Embed], timeout: float | None = 180):  
        super().__init__(timeout=timeout)  
        self.enable_buttons = enable_buttons  
        self.default_embed = default_embed  
        self.embeds = embeds  
        self.current_page = 0  
        self.selected_shop = None  # Thêm thuộc tính lưu trữ lựa chọn hiện tại  

        options = [  
            discord.SelectOption(label='Shop nhẫn', emoji=emojinhan, value='shopnhan'),  
            discord.SelectOption(label='Shop quà', emoji=emojiqua, value='shopqua'),  
        ]  

        self.select = discord.ui.Select(placeholder='Chọn Shop', options=options)  
        self.select.callback = self.select_callback  
        self.add_item(self.select)  
        self.add_item(PreviousButton())  
        self.add_item(NextButton())  

    async def select_callback(self, interaction: discord.Interaction):  

        selected_value = self.select.values[0]  
        self.selected_shop = selected_value  

        if selected_value == 'shopnhan':
            self.select.placeholder = "Shop Nhẫn" 
            embed = discord.Embed(  
                color=discord.Color.from_rgb(227,85,155),  
                description=f'# {shopnhan} **SHOP NHẪN** {shopnhan}\nㅤ\n{tuixachtim} **Chào mừng {interaction.user.mention} đến với cửa hàng nhẫn cưới của server**\nㅤ\n{so1} {nhan1} {so2} {nhan2} {so3} {nhan3} {so4} {nhan4} {so5} {nhan5} {so6} {nhan6} {so7} {nhan7}\n {so8} {nhan8} {so9} {nhan9} {so10} {nhan10} {so11} {nhan11} {so12} {nhan12} {so13} {nhan13} {so14} {nhan14}\nㅤ\n- **`zbuy + ID`** : mua nhẫn\n- **`zmarry + @user + ID`** : kết hôn\n- **`zup + ID`** : nâng cấp nhẫn'  
            )  
            await interaction.response.edit_message(embed=embed, view=self)   

        elif selected_value == 'shopqua':
            self.select.placeholder = "Shop Quà"   
            embed = discord.Embed(  
                color=discord.Color.from_rgb(227,85,155),  
                description=f'# {shopqua} **SHOP QUÀ TẶNG** {shopqua}\nㅤ\n{tuixachvang} **Chào mừng {interaction.user.mention} đến với cửa hàng quà tặng của server**\nㅤ\n**15.** {hoa} **16.** {keotraitim} **17.** {hopsocola} **18.** {carybara}\n**19.** {nuochoa} **20.** {apple} **21.** {iphone} **22.** {xecon}\n- **`zqua + ID`** : mua và tặng quà'  
            )  
            await interaction.response.edit_message(embed=embed, view=self)  
        else:
            return

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.enable_buttons:
            return True
        else:
            await interaction.response.send_message("Không phải bảng của bạn", ephemeral=True)
            return False

    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)
    
    async def enable_all_items(self):
        for item in self.children:
            item.disabled = False
        await self.message.edit(view=self)

    async def disable_button_for(self, button_name: str, duration: int):
        button = getattr(self, button_name)
        button.disabled = True
        await self.message.edit(view=self)
        await asyncio.sleep(duration)
        button.disabled = False
        await self.message.edit(view=self)

    async def on_timeout(self) -> None:
        await self.disable_all_items()
        return await super().on_timeout()
    
    async def on_click(self, interaction: discord.Interaction):
        if interaction.user.id == self.enable_buttons:
            await self.process_components(interaction)
    
    async def update_embed(self, interaction: discord.Interaction):  
        embed = None  # Khởi tạo biến embed mặc định là None
        if self.selected_shop == 'shopnhan':  
            if 1 <= self.current_page <= 14:  
                embed = self.embeds[self.current_page - 1]  
        elif self.selected_shop == 'shopqua':   
            if 15 <= self.current_page <= 22:  
                embed = self.embeds[self.current_page - 1]  
        
        # Kiểm tra nếu embed vẫn là None, tức là không hợp lệ
        if embed is None:
            return
        # Nếu embed hợp lệ, tiếp tục chỉnh sửa tin nhắn
        await interaction.response.edit_message(embed=embed, view=self)

class PreviousButton(discord.ui.Button):  
    def __init__(self):  
        super().__init__(label="", style=discord.ButtonStyle.gray, emoji=pre)  

    async def callback(self, interaction: discord.Interaction):  
        view: ShopView = self.view  
        if view.selected_shop == 'shopnhan':  
            if view.current_page > 1:  
                view.current_page -= 1  
            else:  
                view.current_page = 14  
        elif view.selected_shop == 'shopqua':  
            if view.current_page > 15:  
                view.current_page -= 1  
            else:  
                view.current_page = 22  

        await view.update_embed(interaction)  

class NextButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="", style=discord.ButtonStyle.gray, emoji=nex)

    async def callback(self, interaction: discord.Interaction):
        view: ShopView = self.view
        if view.selected_shop == 'shopnhan':
            if view.current_page < 14:
                view.current_page += 1
            else:
                view.current_page = 1  # Quay lại trang đầu tiên của 'shopnhan'
        elif view.selected_shop == 'shopqua':
            if view.current_page < 15:  # Đảm bảo trang bắt đầu từ 15 cho 'shopqua'
                view.current_page = 15
            elif view.current_page < 22:
                view.current_page += 1
            else:
                view.current_page = 15  # Quay lại trang đầu tiên của 'shopqua'

        await view.update_embed(interaction)

class Shop(commands.Cog):
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

    @commands.command( description="cửa hàng")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def shop(self, ctx):
        if await self.check_command_disabled(ctx):
            return
        if ctx.channel.id == 1215331218124574740 or ctx.channel.id == 1215331281878130738:
            return None
        await ctx.defer()
        user_id = ctx.author.id
        if not is_registered(user_id):
            await ctx.send(f"**{ctx.author.display_name}**, bạn chưa đăng ký. Dùng `zdk` viết liền để đăng ký tài khoản.")
        else:
            default_embed = discord.Embed(
                color=discord.Color.from_rgb(227,85,155), description=f'# {canhtrai} **SHOP HGTT** {canhphai}\nㅤ\n{matcuoi} **Chào mừng {ctx.author.mention} đến với cửa hàng của server. Chúc bạn có trải nghiệm vui vẻ tại đây nhé!**')
            # embed.set_thumbnail(
            #     url='https://cdn.discordapp.com/avatars/1100755217290641438/e0c56196df99764e3ba086fa989d4e99.png')
            # embed.set_footer(text=f"Người thực hiện: {ctx.author.name}")

            cursor.execute("SELECT * FROM shops")
            rings = cursor.fetchall()
            new_items = [
                ("Nhẫn bạc đính đá cầu vồng", 215000, nhan1, ''), #1
                ("Nhẫn bạc đính đá tím", 415000, nhan2, ''), #2 
                ("Nhẫn bạc đá lửa xanh hình bướm dễ thương", 615000, nhan3, ''), #3 
                ("Nhẫn bạc nơ hồng đính đá", 1215000, nhan4, ''), #4 
                ("Nhẫn bạc đính đá hình hoa", 2215000, nhan5, ''), #5
                ("Nhẫn bạc đính đá trái tim", 2950000, nhan6, ''), #6
                ("Nhẫn vàng trắng hoa đá ruby", 3850000, nhan7, ''), #7
                ("Nhẫn vàng 14K đính đá", 4680000, nhan8, ''), #8
                ("Nhẫn vàng trắng 14K đính đá xanh", 5950000, nhan9, ''), #9
                ("Nhẫn vàng đính đá hồng", 6850000, nhan10, ''), #10
                ("Nhẫn vàng trắng 14K đính ngọc trai", 8650000, nhan11, ''), #11
                ("Nhẫn kim cương vàng trắng 18K vương miện", 9950000, nhan12, ''), #12
                ("Nhẫn kim cương vàng trắng 18K", 26999000, nhan13, ''), #13
                ("Nhẫn kim cương vàng trắng 18K giới hạn", 99000000, nhan14, ''), #14
                ("Hoa hồng", 50000, hoa, '1 điểm love'), #15
                ("Kẹo trái tim", 100000, keotraitim, '2 điểm love'), #16
                ("Chocolate", 200000, hopsocola, '6 điểm love'), #17
                ("Gấu bông Capybara", 300000, carybara, '8 điểm love'), #18
                ("Nước hoa", 400000, nuochoa, '10 điểm love'), #19
                ("Đồng hồ", 500000, apple, '12 điểm love'), #20
                ("Iphone pink", 1000000, iphone, '25 điểm love'), #21
                ("Xe hơi dễ thương", 10000000, xecon, '300 điểm love'), #22
            ]
            for item in new_items:
                name = item[0]
                cursor.execute("SELECT * FROM shops WHERE name = ?", (name,))
                existing_item = cursor.fetchone()
                if existing_item is None:
                    cursor.execute(
                        "INSERT INTO shops (name, price, emoji_id, love) VALUES (?, ?, ?, ?)", (item[0], item[1], item[2], item[3]))
                    conn.commit()

            embeds = []
            for i in range(22):
                if i < 14:
                    embed = discord.Embed(
                        color=discord.Color.from_rgb(227,85,155), 
                        description=f'# {laplanh} **{names[i]}** {laplanh}\n{tuixachtim} **Giá: {prices[i]}₫**\n{tuixachtim} **Mã: {1 + i}**'
                    )
                else:
                    embed = discord.Embed(
                        color=discord.Color.from_rgb(227,85,155), 
                        description=f'# {timqua} **{names[i]}** {timqua}\n{tuixachvang} **Giá: {prices[i]}đ -** **Mã: {1 + i}**\n{nhanlove} **Điểm love : + {diemlove[i - 14]}**'
                    )
                embed.set_thumbnail(url=image_urls[i])
                embeds.append(embed)

            enable_buttons = ctx.author.id
            view = ShopView(enable_buttons, default_embed=default_embed, embeds=embeds)
            message = await ctx.send(embed=default_embed, view=view)
            view.message = message
            await view.wait()

    @shop.error
    async def shop_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            message = await ctx.send(f"Vui lòng đợi thêm `{error.retry_after:.0f}s` để có thể sử dụng lệnh này!!")
            await asyncio.sleep(2)
            await message.delete()
            await ctx.message.delete()
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error


    @commands.command( description="Mua nhẫn từ cửa hàng")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def buy(self, ctx, item_id: int):
        if await self.check_command_disabled(ctx):
            return
        if ctx.channel.id == 1215331218124574740 or ctx.channel.id == 1215331281878130738:
            return None
        user_id = ctx.author.id

        if not is_registered(user_id):
            await ctx.send(f"**{ctx.author.display_name}**, bạn chưa đăng ký. Dùng `zdk` viết liền để đăng ký tài khoản.")
            return
        
        cursor.execute("SELECT * FROM shops WHERE id = ?", (item_id,))
        item = cursor.fetchone()

        if item is None:
            await ctx.send("Không tìm thấy vật phẩm có ID này trong cửa hàng.")
        # Lấy thông tin về người dùng từ cơ sở dữ liệu
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user_info = cursor.fetchone()
        user_balance = user_info[2]  # Số dư của người dùng
        if item_id < 1 or item_id > 14:
            if user_balance < item[2]:
                    await ctx.send(f" **Đến tiền mua nhẫn còn không đủ thì đòi cưới ai?**")
                    return
            else:
                await ctx.send(f" **ID của nhẫn từ `1 đến 14` thôi bạn**")
                return
            
        if user_balance < item[2]:
                await ctx.send(f" **Đến tiền mua nhẫn còn không đủ thì đòi cưới ai?**")
                return
        # Trừ tiền và cập nhật số dư
        new_balance = user_balance - item[2]
        cursor.execute(
            "UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))

        # Xử lý thông tin về vật phẩm đã mua
        purchased_items = user_info[6]
        purchased_item_ids = [item_info.split(
            ":")[0] for item_info in purchased_items.split(",")]

        if str(item[0]) in purchased_item_ids:
            # Nếu đã mua trước đó, cập nhật số lượng
            new_purchased_items = []

            for item_info in purchased_items.split(","):
                parts = item_info.split(":")
                if parts[0] == str(item[0]):
                    new_quantity = int(parts[2]) + 1
                    emoji_string = item_info.split("<")[1].split(">")[0]
                    parts[3] = f"<{emoji_string}>"
                    new_purchased_items.append(
                        f"{parts[0]}:{parts[1]}:{new_quantity}:{parts[3]}")
                else:
                    new_purchased_items.append(item_info)
            new_purchased_items_str = ",".join(new_purchased_items)
        else:
            # Nếu chưa mua, thêm vật phẩm vào cột 'purchased_items'
            new_item_info = f"{item[0]}:{item[1]}:1:{item[3]}"
            new_purchased_items_str = purchased_items + "," + \
                new_item_info if purchased_items else new_item_info

        # Cập nhật cơ sở dữ liệu
        cursor.execute("UPDATE users SET purchased_items = ? WHERE user_id = ?",
                       (new_purchased_items_str, user_id))
        conn.commit()

        formatted_gia = "{:,}".format(item[2])
        if 1 <= item[0] <= 14:
            await ctx.send(f"{tuixachtim} | **{ctx.author.mention}**, **mua thành công** __**{item[1]}**__ {item[3]} **với giá** __**{formatted_gia}**__ {tienhatgiong}")

    @buy.error
    async def buy_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            message = await ctx.send(f"Vui lòng đợi thêm `{error.retry_after:.0f}s` để có thể sử dụng lệnh này!!")
            await asyncio.sleep(2)
            await message.delete()
            await ctx.message.delete()
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Vui lòng nhập ID của vật phẩm bạn muốn mua.")
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error

    @commands.command( description="Sử dụng quà tặng")
    @is_allowed_channel_checkmarry()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def qua(self, ctx, item_id: int):
        if await self.check_command_disabled(ctx):
            return
        if ctx.channel.id == 1215331218124574740 or ctx.channel.id == 1215331281878130738:
            return None
        if not is_registered(ctx.author.id):
            await ctx.send(f"**{ctx.author.display_name}**, Dùng `zdk` để đăng ký tài khoản.")
            return
        cursor.execute("SELECT marry, love_marry, balance FROM users WHERE user_id = ?", (ctx.author.id,))
        result = cursor.fetchone()
        marry_status = result[0]
        love_point = result[1]
        user_balance = result[2]

        cursor.execute("SELECT * FROM shops WHERE id = ?", (item_id,))
        item = cursor.fetchone()

        if item is None:
            await ctx.send("Không thấy vật phẩm ID này trong cửa hàng.")
            return

        matches = re.findall(r'<@(\d+)>', marry_status)

        if marry_status == '':
            await ctx.send("Bạn chưa kết hôn!")
            return
        
        if user_balance < item[2]:
            await ctx.send(f" **Đến tiền mua quà còn không đủ thì tặng ai?**")
            return

        if len(matches) == 2:  
            user1_id = int(matches[0])
            user2_id = int(matches[1])
            if 15 <= item_id <= 22:

                if item is None:
                    await ctx.send("Không tìm thấy vật phẩm có ID này trong cửa hàng.")
                    return
                points_dict = {15: 1, 16: 2, 17: 6, 18: 8, 19: 10, 20: 12, 21: 25, 22: 300} 

                if item_id in points_dict:
                    points = points_dict[item_id]
                else:
                    points = 0

                love_marry_points = love_point + points
                new_balance = user_balance - item[2]
                cursor.execute("UPDATE users SET balance = ?, love_marry = ? WHERE user_id = ?", (new_balance, love_marry_points, ctx.author.id))
                conn.commit()

                await ctx.send(f"{hopqua} **{ctx.author.mention} tặng** __**{item[1]}**__ {item[3]} **cho <@{user2_id}>, 2 bạn được cộng** __**{points} điểm**__ ** Love**")

                # embed = discord.Embed(title="", description=f"",
                #                     color=discord.Color.from_rgb(255, 192, 203))
                # embed.add_field(name="", value=f"{tuixachvang} **{ctx.author.mention} tặng {item[1]} {item[3]} cho <@{user2_id}>, 2 bạn được cộng ** __**{points}**__ **điểm love!**", inline=False)
                # await ctx.send(embed=embed)
            else:
                await ctx.send(f"ID của quà từ `15 đến 22` thôi bạn")

    @qua.error
    async def tang_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            message = await ctx.send(f"Vui lòng đợi thêm `{error.retry_after:.0f}s` để có thể sử dụng lệnh này!!")
            await asyncio.sleep(2)
            await message.delete()
            await ctx.message.delete()
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Vui lòng nhập ID của vật phẩm bạn muốn mua.")
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error

    @commands.command()
    @is_guild_owner_or_bot_owner()
    async def reset1(self, ctx):
        cursor.execute("UPDATE users SET balance = ?, purchased_items = ?, marry = ?, open_items = ?, love_marry = ?, setup_marry1 = ?, setup_marry2 = ?, streak_toan = ?, pray = ? ", (0,'','','',0,'','',0,0))
        conn.commit()
        await ctx.send("Đã reset các mục: tiền, vật phâm đã mua, marry, quả đã mở, điểm love, setanh, setchu")

    # @commands.command(aliases=["SELL"], description="Bán nhẫn từ cửa hàng")
    # @commands.cooldown(1, 3, commands.BucketType.user)
    # async def sell(self, ctx, item_id: int):
    #     if ctx.channel.id == 1215331218124574740 or ctx.channel.id == 1215331281878130738:
    #         return None
    #     user_id = ctx.author.id
    #     if not is_registered(user_id):
    #         await ctx.send(f"**{ctx.author.display_name}**, bạn chưa đăng ký. Dùng `prefix +dk` viết liền để đăng ký tài khoản.")
    #         return

    #     cursor.execute("SELECT * FROM shops WHERE id = ?", (item_id,))
    #     item = cursor.fetchone()

    #     if item is None:
    #         await ctx.send("Không tìm thấy vật phẩm có ID này trong cửa hàng.")
    #         return

    #     # Lấy thông tin về người dùng từ cơ sở dữ liệu
    #     cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    #     user_info = cursor.fetchone()

    #     # Xử lý thông tin về vật phẩm đã mua
    #     purchased_items = user_info[6]
    #     purchased_item_list = purchased_items.split(",")
    #     purchased_item_dict = {item.split(":")[0]: item for item in purchased_item_list}

    #     sell_item_id = str(item[0])
    #     if sell_item_id not in purchased_item_dict:
    #         await ctx.send("Bạn không có vật phẩm này để bán.")
    #         return
    #     sell_item_info = purchased_item_dict[sell_item_id].split(":")
    #     sell_item_quantity = int(sell_item_info[2]) - 1

    #     if sell_item_quantity == 0:
    #         del purchased_item_dict[sell_item_id]
    #     else:
    #         sell_item_info[2] = str(sell_item_quantity)
    #         purchased_item_dict[sell_item_id] = ":".join(sell_item_info)

    #     sell_price = int(item[2] * 0.75)
    #     new_balance = user_info[2] + sell_price
    #     cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))

    #     new_purchased_items_str = ",".join(purchased_item_dict.values())
    #     cursor.execute("UPDATE users SET purchased_items = ? WHERE user_id = ?", (new_purchased_items_str, user_id))
    #     conn.commit()

    #     emoji = discord.utils.get(emoji_guild.emojis, id=item[3])
    #     emoji_str = f"{emoji}" if emoji else ""
    #     formatted_gia = "{:,}".format(sell_price)
    #     await ctx.send(f" 🛒 | **{ctx.author.display_name}**, bạn đã bán thành công **{item[1]}** {item[3]} với giá **{formatted_gia}** {tienhatgiong}")

    # @sell.error
    # async def sell_error(self, ctx, error):
    #     if isinstance(error, commands.CommandOnCooldown):
    #         message = await ctx.send(f" | Vui lòng đợi thêm `{error.retry_after:.0f}s` để có thể sử dụng lệnh này!!")
    #         await asyncio.sleep(2)
    #         await message.delete()
    #         await ctx.message.delete()

    # @commands.command(aliases=["khonhan", "TUI"], description="Liệt kê nhẫn trong kho")
    # async def tui(self, ctx):
    #     if ctx.channel.id == 1215331218124574740 or ctx.channel.id == 1215331281878130738:
    #         return None
    #     user_id = ctx.author.id
    #     if not is_registered(user_id):
    #         await ctx.send(f"**{ctx.author.display_name}**, bạn chưa đăng ký. Dùng `zdk` viết liền để đăng ký tài khoản.")
    #         return
    #     # Lấy thông tin về người dùng từ cơ sở dữ liệu
    #     cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    #     user_info = cursor.fetchone()

    #     inventory_items = user_info[6].split(",") if user_info[6] else []
    #     all_shop_items = [
    #         item for item in cursor.execute("SELECT * FROM shops")]

    #     embed = discord.Embed(
    #         color=discord.Color.from_rgb(222, 204, 87), description=f"")
    #     if ctx.author.avatar:
    #         avatar_url = ctx.author.avatar.url
    #     else:
    #         avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"  
    #     embed.set_author(name=f"Kho đồ của {ctx.author.display_name}", icon_url=avatar_url)
    #     for item in all_shop_items:
    #         item_id = int(item[0])
    #         item_quantity = 0
    #         for item_info in inventory_items:
    #             item_parts = item_info.split(":")
    #             if int(item_parts[0]) == item_id:
    #                 item_quantity = int(item_parts[2])
    #                 break
    #         embed.add_field(
    #             name=f"", value=f"**`{item[0]}`** {item[3]} {item_quantity}", inline=True)
    #     # tui = TuiSelectMenu()
    #     # view = TuiView(tui)
    #     # await ctx.send(embed=embed, view=view)
    #     await ctx.send(embed=embed)


# class TuiSelectMenu(discord.ui.Select):
#     def __init__(self):
#         options=[
#                     discord.SelectOption(label='KHO ĐỒ', emoji= emojinhan, value='khonhan', description='Kho nhẫn và quà tặng'),
#                     discord.SelectOption(label='KHO QUÀ ĐƯỢC TẶNG',emoji= emojiqua, value='khoqua', description='Những quà tặng bạn nhận được từ người yêu'),
#                 ]
#         super().__init__(placeholder='Chọn Kho', options=options)

#     async def callback(self, interaction: discord.Interaction):
#         if self.values[0] == 'khonhan':
#             user_id = interaction.user.id
#             cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
#             user_info = cursor.fetchone()

#             inventory_items = user_info[6].split(",") if user_info[6] else []
#             all_shop_items = [
#                 item for item in cursor.execute("SELECT * FROM shops")]

#             embed = discord.Embed(
#                 color=discord.Color.from_rgb(222, 204, 87), description=f"")
#             if interaction.user.avatar:
#                 avatar_url = interaction.user.avatar.url
#             else:
#                 avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"  
#             embed.set_author(name=f"Kho đồ của {interaction.user.display_name}", icon_url=avatar_url)
#             for item in all_shop_items:
#                 item_id = int(item[0])
#                 item_quantity = 0
#                 for item_info in inventory_items:
#                     item_parts = item_info.split(":")
#                     if int(item_parts[0]) == item_id:
#                         item_quantity = int(item_parts[2])
#                         break
#                 embed.add_field(
#                     name=f"", value=f"**`{item[0]}`** {item[3]} {item_quantity}", inline=True)

#             await interaction.response.edit_message(embed=embed)

#         elif self.values[0] == 'khoqua':
#             user_id = interaction.user.id
#             cursor.execute("SELECT love_items FROM users WHERE user_id = ?", (user_id,))
#             love_items_str = cursor.fetchone()[0]
#             embed = discord.Embed(title="", color=discord.Color.from_rgb(255, 192, 203))
#             if interaction.user.avatar:
#                 avatar_url = interaction.user.avatar.url
#             else:
#                 avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"  
#             embed.set_author(name=f"Kho Quà Tặng Của {interaction.user.display_name}", icon_url=avatar_url)
#             if not love_items_str:
#                 await interaction.response.edit_message(embed=embed)
#                 return

#             love_items_list = love_items_str.split(",")
#             love_items_list = sorted(love_items_list, key=lambda x: int(x.split(":")[0]) if x else 0)
#             for item_info_str in love_items_list:
#                 if not item_info_str:
#                     continue  
#                 item_info = item_info_str.split(":")
#                 if not item_info[0]:
#                     continue 
#                 try:
#                     item_id = int(item_info[0])
#                 except ValueError:
#                     print(f"Invalid item ID: {item_info[0]}")
#                     continue
#                 emoji = ":".join(item_info[3:]).strip()

#                 item_name = item_info[1]
#                 item_quantity = int(item_info[2])
#                 embed.add_field(name=f"", value=f"- {emoji} **{item_name}**: **`{item_quantity}`**", inline=False)
            
#             await interaction.response.edit_message(embed=embed)

# class TuiView(discord.ui.View):
#     def __init__(self, TuiSelectMenu: discord.ui.Select):
#         super().__init__(timeout=180)
#         self.add_item(TuiSelectMenu)

async def setup(client):
    await client.add_cog(Shop(client))