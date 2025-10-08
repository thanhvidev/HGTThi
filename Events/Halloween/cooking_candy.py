import asyncio
import random
import discord
import sqlite3
from datetime import datetime, timedelta
from discord.ext import commands, tasks
import json
from discord.ui import Button, View
import pytz
import datetime

conn = sqlite3.connect('economy.db', isolation_level=None)
conn.execute('pragma journal_mode=wal')
cursor = conn.cursor()

def is_registered(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None

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

def is_allowed_channel():
    async def predicate(ctx):
        allowed_channel_ids = [1147355133622108262, 1147035278465310720]
        if ctx.channel.id not in allowed_channel_ids:
            await ctx.send(f"{dauxdo} **Dùng lệnh** **`zlamkeo`** [__**ở đây**__](<https://discord.com/channels/832579380634451969/1147355133622108262>)")
            return False
        return True
    return commands.check(predicate)

dauxdo = "<a:hgtt_check:1246910030444495008>"
emojidung = "<:sushi_thanhcong:1215621188059926538>"
emojisai = "<:hgtt_sai:1186839020974657657>"
noicom = "<:sushi_nau:1215607752005652480>"
dongho = "<a:hgtt_timee:1159077258535907328>"
bot = "<:bot:1284435485015539774>"
thapcam = "<:nhanthapcam:1284440549608263742>"
dauxanh = "<:nhandauxanh:1284445471842111508>"
trungmuoi = "<:trungmuoi:1284454670097453127>"
congthuc = "<:congthuchlw:1295382257850388534>"
lambanh1 = "<:lambanh:1284515681584549909>"
tickmauxanh = "<:naukeohlw:1295382268482945134>"
banhthapcam = "<:cookthapcam:1284428897093550155>"
banhdauxanh = "<:cookdauxanh:1284429245342421103>"
naubanh = "<:cook:1284446539997118494>"
banhthapcam1 = "<:banhthapcam:1284431708640382996>"
banhdauxanh1 = "<:banhdauxanh:1284431752764588103>"
checkbanh = "<:check:1282056692930187387>"
tienhatgiong = "<:timcoin:1192458078294122526>"
duong = "<:duong:1295342064644521984>"
tao = "<:tao:1295342021690527765>"
ngo = "<:ngo:1295341799690473523>"
keongo = "<:keongo:1295384172197838910>"
keotao = "<:keotao:1295384182775742466>"
dangnau = "<:naukeo:1295384192078712912>"
nauthanhcong = "<a:nauthanhcong:1295384201205649480>"
nhaynaukeo = "<a:nhaynaukeo:1295385720499994625>"
dk = "<:profile:1181400074127945799>"

class Naukeo(commands.Cog):
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

    @commands.command(description="Nấu ăn")
    @commands.cooldown(1, 600, commands.BucketType.user)
    @is_allowed_channel()
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def lamkeo(self, ctx):
        if await self.check_command_disabled(ctx):
            return
        if ctx.channel.id == 993153068378116127 or ctx.channel.id == 1207593935359320084 or ctx.channel.id == 1215331218124574740 or ctx.channel.id == 1215331281878130738 or ctx.channel.id == 1295144686536888340:
            return None
        else:
            if not is_registered(ctx.author.id):
                await ctx.send(f"{dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
                return
            prize_ids = [24, 25, 26]
            prize_info = []
            user_id = ctx.author.id
            embed = discord.Embed(
                color=discord.Color.from_rgb(28,202,9), description=f"")
            if ctx.author.avatar:
                avatar_url = ctx.author.avatar.url
            else:
                avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
            embed.set_author(name=f"😈 {ctx.author.display_name} làm kẹo ", icon_url=avatar_url)
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1053799649938505889/1295196104069222491/discord_fake_avatar_decorations_1728865419300.gif")
            fields_value = ""
            for prize_id in prize_ids:
                cursor.execute("SELECT name_phanthuong, emoji_phanthuong FROM phan_thuong WHERE id = ?", (prize_id,))
                prize_info = cursor.fetchone()
                if prize_info:
                    name_phanthuong = prize_info[0]
                    emoji_phanthuong = prize_info[1]
                    cursor.execute("SELECT open_items FROM users WHERE user_id = ?", (user_id,))
                    result = cursor.fetchone()
                    if result and result[0]:
                        try:
                            open_items_data = json.loads(result[0])
                            quantity = open_items_data.get(name_phanthuong, {}).get("so_luong", 0)
                            emoji = open_items_data.get(name_phanthuong, {}).get("emoji", emoji_phanthuong)
                            superscript_quantity = get_superscript(quantity)
                            fields_value += f"**{emoji} {superscript_quantity}** "
                        except json.JSONDecodeError as e:
                            print(f"Lỗi giải mã JSON: {e}")
                    else:
                        fields_value += f"**{emoji_phanthuong} ⁰** "
            embed.add_field(name="", value=f"**{congthuc} : {ngo} ² / {duong} ² + {tao} ² + 50k {tienhatgiong}**", inline=False)
            embed.add_field(name="", value=f"**{tickmauxanh} :** {fields_value}", inline=True)
            enable_buttons = ctx.author.id
            view = LamkeoView(enable_buttons)
            message = await ctx.send(embed=embed, view=view)
            view.message = message
            await view.wait()
    
    @lamkeo.error
    async def lamkeo_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            message = await ctx.send(f"{dongho} **| {ctx.author.mention} vui lòng chờ {error.retry_after:.0f} giây trước khi sử dụng lệnh này.**")
            await asyncio.sleep(2)
            await message.delete()
            await ctx.message.delete()
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error

class LamkeoView(discord.ui.View):
    def __init__(self,enable_buttons, timeout: float = 180.0):
        super().__init__(timeout=timeout)
        self.enable_buttons = enable_buttons

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.enable_buttons:
            return True
        else:
            await interaction.response.send_message("Bảng nấu kẹo này của người khác", ephemeral=True)
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
        self.nau_keongo.disabled = True  
        self.nau_keotao.disabled = True  
        await self.message.edit(view=self)  # Cập nhật giao diện  
        await asyncio.sleep(duration)  # Chờ trong thời gian đã chỉ định  
        # Kích hoạt lại cả hai nút  
        self.nau_keongo.disabled = False  
        self.nau_keotao.disabled = False  
        await self.message.edit(view=self)  # Cập nhật giao diện  


    async def on_timeout(self) -> None:
        await self.disable_all_items()
        return await super().on_timeout()

    @discord.ui.button(label="Nấu", style=discord.ButtonStyle.gray, emoji="<:keongo:1295384172197838910>", custom_id="keongo", disabled=False)
    async def nau_keongo(self, interaction: discord.Interaction, Button: discord.ui.Button):
        user_id = interaction.user.id
        cursor.execute("SELECT open_items, balance FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        if result and result[1] >= 50000:          
            if result and result[0]:
                open_items_data = json.loads(result[0])
                # Kiểm tra xem nguyên liệu có đủ không
                kiemtra_nguyenlieu = (
                    open_items_data.get("ng\u00f4", {}).get("so_luong", 0) >= 2
                )
                if kiemtra_nguyenlieu:
                    # Trừ đi số lượng nguyên liệu
                    open_items_data["ng\u00F4"]["so_luong"] -= 2
                    updated_open_item = json.dumps(open_items_data)
                    cursor.execute(
                        "UPDATE users SET open_items = ? WHERE user_id = ?", (updated_open_item, user_id))
                    conn.commit()
                    if "k\u1EB9o ng\u00F4" in open_items_data:
                        open_items_data["k\u1EB9o ng\u00F4"]["so_luong"] += 1
                    else:
                        open_items_data["k\u1EB9o ng\u00F4"] = {
                            "emoji": "<:keongo:1295384172197838910>",
                            "name_phanthuong": "k\u1EB9o ng\u00F4",
                            "so_luong": 1
                        }
                    await interaction.response.send_message(content=f'> {dangnau} **{interaction.user.mention} đang nấu** __**kẹo ngô halloween**__, **vui lòng chờ 10 phút {nhaynaukeo} {keongo} {nhaynaukeo}**')
                    # await self.disable_button_for("nau_keongo", 600)
                    await self.disable_buttons(600)  
                    # Cập nhật lại cột open_items
                    updated_open_items = json.dumps(open_items_data)
                    cursor.execute(
                        "UPDATE users SET open_items = ? WHERE user_id = ?", (updated_open_items, user_id))
                    conn.commit()
                    await interaction.channel.send(content=f'> {nauthanhcong} **{interaction.user.mention} làm** __**kẹo ngô halloween**__ **thành công. Bấm `zinv` để xem nhé** {nhaynaukeo}')
                else:
                    await interaction.response.send_message(content=f"{emojisai} **| {interaction.user.mention} không đủ nguyên liệu để làm**", ephemeral=True)
            else:
                await interaction.response.send_message(content=f"{emojisai} **| {interaction.user.mention} không đủ nguyên liệu để làm**", ephemeral=True)
        else:
            await interaction.response.send_message(content=f"{emojisai} **| {interaction.user.mention} không đủ tiền để làm**", ephemeral=True)

    @discord.ui.button(label="Nấu", style=discord.ButtonStyle.gray, emoji="<:keotao:1295384182775742466>", custom_id="keotao", disabled=False)
    async def nau_keotao(self, interaction: discord.Interaction, Button: discord.ui.Button):
        user_id = interaction.user.id
        cursor.execute("SELECT open_items, balance FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        if result and result[1]:       
            if result and result[0]:
                open_items_data = json.loads(result[0])
                # Kiểm tra xem nguyên liệu có đủ không
                kiemtra_nguyenlieu = (
                    open_items_data.get("\u0111\u01b0\u1eddng", {}).get("so_luong", 0) >= 2
                    and open_items_data.get("t\u00e1o", {}).get("so_luong", 0) >= 2
                )
                if kiemtra_nguyenlieu:
                    # Trừ đi số lượng nguyên liệu
                    open_items_data["\u0111\u01b0\u1eddng"]["so_luong"] -= 2
                    open_items_data["t\u00e1o"]["so_luong"] -= 2
                    updated_open_item = json.dumps(open_items_data)
                    cursor.execute(
                        "UPDATE users SET open_items = ? WHERE user_id = ?", (updated_open_item, user_id))
                    conn.commit()
                    if "k\u1EB9o t\u00e1o" in open_items_data:
                        open_items_data["k\u1EB9o t\u00e1o"]["so_luong"] += 1
                    else:
                        open_items_data["k\u1EB9o t\u00e1o"] = {
                            "emoji": "<:keotao:1295384182775742466>",
                            "name_phanthuong": "k\u1EB9o t\u00e1o",
                            "so_luong": 1
                        }
                    await interaction.response.send_message(content=f'> {dangnau} **{interaction.user.mention} đang nấu** __**kẹo táo halloween**__, **vui lòng chờ 10 phút {nhaynaukeo} {keotao} {nhaynaukeo}**')
                    # disabled nút 10p
                    # await self.disable_button_for("nau_keotao", 600)
                    await self.disable_buttons(600)  
                    # Cập nhật lại cột open_items
                    updated_open_items = json.dumps(open_items_data)
                    cursor.execute(
                        "UPDATE users SET open_items = ? WHERE user_id = ?", (updated_open_items, user_id))
                    conn.commit()
                    await interaction.channel.send(content=f'> {nauthanhcong} **{interaction.user.mention} làm** __**kẹo táo halloween**__ **thành công. Bấm `zinv` để xem nhé** {nhaynaukeo}')
                else:
                    await interaction.response.send_message(content=f"{emojisai} **| {interaction.user.mention} không đủ nguyên liệu để làm**", ephemeral=True)
            else:
                await interaction.response.send_message(content=f"{emojisai} **| {interaction.user.mention} không đủ nguyên liệu để làm**", ephemeral=True)
        else:
            await interaction.response.send_message(content=f"{emojisai} **| {interaction.user.mention} không đủ tiền để làm**", ephemeral=True)

async def setup(client):
    await client.add_cog(Naukeo(client))