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

def is_allowed_channel():
    async def predicate(ctx):
        allowed_channel_id = 1147355133622108262
        if ctx.channel.id != allowed_channel_id:
            await ctx.send(f"{dauxdo} **Dùng lệnh** **`zlambanh`** [__**ở đây**__](<https://discord.com/channels/832579380634451969/1147355133622108262>)")
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
congthuc = "<:openbook_8091010:1284446868192890890>"
lambanh1 = "<:lambanh:1284515681584549909>"
tickmauxanh = "<a:tichxanh:1284504996330733610>"
banhthapcam = "<:cookthapcam:1284428897093550155>"
banhdauxanh = "<:cookdauxanh:1284429245342421103>"
naubanh = "<:cook:1284446539997118494>"
banhthapcam1 = "<:banhthapcam:1284431708640382996>"
banhdauxanh1 = "<:banhdauxanh:1284431752764588103>"
checkbanh = "<:check:1282056692930187387>"

class Lambanh(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.command( description="Nấu ăn")
    @is_allowed_channel()
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def lambanh(self, ctx):
        if ctx.channel.id == 993153068378116127 or ctx.channel.id == 1207593935359320084 or ctx.channel.id == 1215331218124574740 or ctx.channel.id == 1215331281878130738:
            return None
        else:
            if not is_registered(ctx.author.id):
                await ctx.send(f"{self.dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
                return
            prize_ids = [18, 19, 20, 21]
            prize_info = []
            user_id = ctx.author.id
            embed = discord.Embed(
                color=discord.Color.from_rgb(255, 255, 0), description=f"")
            if ctx.author.avatar:
                avatar_url = ctx.author.avatar.url
            else:
                avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
            embed.set_author(name=f"🧑‍🍳 {ctx.author.display_name} làm bánh ", icon_url=avatar_url)
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1053799649938505889/1284534534875906142/discord_fake_avatar_decorations_1726327270637.gif")
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
            embed.add_field(name="", value=f"**{tickmauxanh} :** {fields_value}", inline=True)
            embed.add_field(name="", value=f"**{congthuc} : {bot} ³ + {thapcam} ² / {dauxanh} ²  {trungmuoi} ²**", inline=False)
            enable_buttons = ctx.author.id
            view = LambanhView(enable_buttons)
            message = await ctx.send(embed=embed, view=view)
            view.message = message
            await view.wait()
    
    @lambanh.error
    async def lambanh_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            message = await ctx.send(f"{dongho} **| {ctx.author.mention} vui lòng chờ {error.retry_after:.0f} giây trước khi sử dụng lệnh này.**")
            await asyncio.sleep(2)
            await message.delete()
            await ctx.message.delete()
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error

class LambanhView(discord.ui.View):
    def __init__(self,enable_buttons, timeout: float = 180.0):
        super().__init__(timeout=timeout)
        self.enable_buttons = enable_buttons

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.enable_buttons:
            return True
        else:
            await interaction.response.send_message("Bảng nấu sushi này của người khác", ephemeral=True)
            return False

    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
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

    @discord.ui.button(label="Nấu", style=discord.ButtonStyle.primary, emoji="<:cookthapcam:1284428897093550155>", custom_id="banhthapcam", disabled=False)
    async def nau_thapcam(self, interaction: discord.Interaction, Button: discord.ui.Button):
        user_id = interaction.user.id
        cursor.execute("SELECT open_items FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        if result and result[0]:
            open_items_data = json.loads(result[0])
            # Kiểm tra xem nguyên liệu có đủ không
            kiemtra_nguyenlieu = (
                open_items_data.get("b\u1ed9t", {}).get("so_luong", 0) >= 3
                and open_items_data.get("nh\u00e2n th\u1eadp c\u1ea9m", {}).get("so_luong", 0) >= 2
            )
            if kiemtra_nguyenlieu:
                # Trừ đi số lượng nguyên liệu
                open_items_data["b\u1ed9t"]["so_luong"] -= 3
                open_items_data["nh\u00e2n th\u1eadp c\u1ea9m"]["so_luong"] -= 2
                updated_open_item = json.dumps(open_items_data)
                cursor.execute(
                    "UPDATE users SET open_items = ? WHERE user_id = ?", (updated_open_item, user_id))
                conn.commit()
                if "b\u1ea3nh t\u1ee7ng th\u1ee7 th\u1eadp c\u1ea9m" in open_items_data:
                    open_items_data["b\u1ea3nh t\u1ee7ng th\u1ee7 th\u1eadp c\u1ea9m"]["so_luong"] += 1
                else:
                    open_items_data["b\u1ea3nh t\u1ee7ng th\u1ee7 th\u1eadp c\u1ea9m"] = {
                        "emoji": "<:banhthapcam:1284431708640382996>",
                        "name_phanthuong": "b\u1ea3nh t\u1ee7ng th\u1ee7 th\u1eadp c\u1ea9m",
                        "so_luong": 1
                    }
                await interaction.response.send_message(content=f'> {naubanh} **{interaction.user.mention} đang làm "bánh trung thu thập cẩm", vui lòng chờ 10 phút {banhthapcam1}**')
                # disabled nút 10s
                await self.disable_button_for("nau_thapcam", 600)
                # Cập nhật lại cột open_items
                updated_open_items = json.dumps(open_items_data)
                cursor.execute(
                    "UPDATE users SET open_items = ? WHERE user_id = ?", (updated_open_items, user_id))
                conn.commit()
                await interaction.channel.send(content=f'> {checkbanh} **{interaction.user.mention} làm "bánh trung thu thập cẩm" thành công.** **Bấm** **`zinv`** **để xem nhé** ')
            else:
                await interaction.response.send_message(content=f"{emojisai} **| {interaction.user.mention} không đủ nguyên liệu để làm**", ephemeral=True)
        else:
            await interaction.response.send_message(content=f"{emojisai} **| {interaction.user.mention} không đủ nguyên liệu để làm**", ephemeral=True)

    @discord.ui.button(label="Nấu", style=discord.ButtonStyle.primary, emoji="<:cookdauxanh:1284429245342421103>", custom_id="banhdauxanh", disabled=False)
    async def nau_dauxanh(self, interaction: discord.Interaction, Button: discord.ui.Button):
        user_id = interaction.user.id
        cursor.execute("SELECT open_items FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        if result and result[0]:
            open_items_data = json.loads(result[0])
            # Kiểm tra xem nguyên liệu có đủ không
            kiemtra_nguyenlieu = (
                open_items_data.get("nh\u00e2n \u0111\u1eadu xanh", {}).get("so_luong", 0) >= 2
                and open_items_data.get("tr\u1ee9ng mu\u1ed1i", {}).get("so_luong", 0) >= 2
            )
            if kiemtra_nguyenlieu:
                # Trừ đi số lượng nguyên liệu
                open_items_data["nh\u00e2n \u0111\u1eadu xanh"]["so_luong"] -= 2
                open_items_data["tr\u1ee9ng mu\u1ed1i"]["so_luong"] -= 2
                updated_open_item = json.dumps(open_items_data)
                cursor.execute(
                    "UPDATE users SET open_items = ? WHERE user_id = ?", (updated_open_item, user_id))
                conn.commit()
                if "b\u1ea3nh t\u1ee7ng th\u1ee7 \u0111\u1ea7u xanh" in open_items_data:
                    open_items_data["b\u1ea3nh t\u1ee7ng th\u1ee7 \u0111\u1ea7u xanh"]["so_luong"] += 1
                else:
                    open_items_data["b\u1ea3nh t\u1ee7ng th\u1ee7 \u0111\u1ea7u xanh"] = {
                        "emoji": "<:banhdauxanh:1284431752764588103>",
                        "name_phanthuong": "b\u1ea3nh t\u1ee7ng th\u1ee7 \u0111\u1ea7u xanh",
                        "so_luong": 1
                    }
                await interaction.response.send_message(content=f'> {naubanh} **{interaction.user.mention} đang làm "bánh trung thu đậu xanh", vui lòng chờ 10 phút {banhdauxanh1}**')
                # disabled nút 10p
                await self.disable_button_for("nau_dauxanh", 600)
                # Cập nhật lại cột open_items
                updated_open_items = json.dumps(open_items_data)
                cursor.execute(
                    "UPDATE users SET open_items = ? WHERE user_id = ?", (updated_open_items, user_id))
                conn.commit()
                await interaction.channel.send(content=f'> {checkbanh} **{interaction.user.mention} làm "bánh trung thu đậu xanh" thành công.** **Bấm** **`zinv`** **để xem nhé** ')
            else:
                await interaction.response.send_message(content=f"{emojisai} **| {interaction.user.mention} không đủ nguyên liệu để làm**", ephemeral=True)
        else:
            await interaction.response.send_message(content=f"{emojisai} **| {interaction.user.mention} không đủ nguyên liệu để làm**", ephemeral=True)


async def setup(client):
    await client.add_cog(Lambanh(client))