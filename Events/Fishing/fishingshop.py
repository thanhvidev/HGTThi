import asyncio
import discord
import sqlite3
import random
from discord.ext import commands
from discord.ui import Button, View
import json

conn = sqlite3.connect('economy.db')
cursor = conn.cursor()

fishcoin = "<:fishcoin:1213027788672737300>"
moicau = "<:moicauca:1213073602996477972>"
cancau50 = "<:can50:1213177065931804752>"
cancau80 = "<:can80:1213179176291536926>"
cancau100 = "<:can100:1213182598990274651>"
line = "<a:hgtt_ogach:1024039534452813824>"
checkcauca = "<:checkcauca:1213359415080517714>"
khongdutien = "<:khongdutien:1211921509514477568>"
canhbao = "<:chamthan:1213200604495749201>"
dk = "<:profile:1181400074127945799>"

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

class FishingshopView(discord.ui.View):
    def __init__(self, enable_buttons, timeout: float = 180.0):
        super().__init__(timeout=timeout)
        self.enable_buttons = enable_buttons

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.enable_buttons:
            return True
        else:
            await interaction.response.send_message("Bạn không có quyền sử dụng menu này", ephemeral=True)
            return False

    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self) 
    
    async def on_timeout(self) -> None:
        await self.disable_all_items()
        return await super().on_timeout()
        
    @discord.ui.button(label="Mồi X1", style=discord.ButtonStyle.blurple, emoji="<:moicauca:1213073602996477972> ", row=1, disabled=True)
    async def moicau1(self, interaction: discord.Interaction, button: discord.ui.Button):
        cursor.execute("SELECT coin_kc, kho_moi FROM users WHERE user_id = ?", (interaction.user.id,))
        result = cursor.fetchone()
        if result:
            coin_kc, existing_items_json = result
            if coin_kc >= 20:
                new_coin_kc = coin_kc - 20
                cursor.execute("UPDATE users SET coin_kc = ? WHERE user_id = ?", (new_coin_kc, interaction.user.id))

                if existing_items_json:
                    existing_items = json.loads(existing_items_json)
                else:
                    existing_items = []

                item_index = None
                for index, item in enumerate(existing_items):
                    if item["name"] == "Moi cau":
                        item_index = index
                        break

                if item_index is not None:
                    existing_items[item_index]["quantity"] += 1
                    quantity = existing_items[item_index]["quantity"]
                else:
                    existing_items.append({"name": "Moi cau", "emoji": "<:moicauca:1213073602996477972>", "quantity": 1})
                    quantity = 1

                cursor.execute("UPDATE users SET kho_moi = ? WHERE user_id = ?", (json.dumps(existing_items), interaction.user.id))
                conn.commit()
                await interaction.response.send_message(f"{checkcauca} **{interaction.user.mention} mua thành công 1 {moicau}, bạn đang có {quantity} {moicau}**")
            else:
                await interaction.response.send_message(f"{khongdutien} **{interaction.user.mention}, bạn không đủ {fishcoin} để mua mồi câu**", ephemeral=True)
        else:
            await interaction.response.send_message(f"{khongdutien} **{interaction.user.mention}, bạn không đủ {fishcoin} để mua mồi câu**", ephemeral=True)
    
    @discord.ui.button(label="Mồi X5", style=discord.ButtonStyle.blurple, emoji="<:moicauca:1213073602996477972> ", row=1, disabled=True)
    async def moicau5(self, interaction: discord.Interaction, button: discord.ui.Button):
        cursor.execute("SELECT coin_kc, kho_moi FROM users WHERE user_id = ?", (interaction.user.id,))
        result = cursor.fetchone()
        if result:
            coin_kc, existing_items_json = result
            if coin_kc >= 100:
                new_coin_kc = coin_kc - 100
                cursor.execute("UPDATE users SET coin_kc = ? WHERE user_id = ?", (new_coin_kc, interaction.user.id))

                if existing_items_json:
                    existing_items = json.loads(existing_items_json)
                else:
                    existing_items = []

                item_index = None
                for index, item in enumerate(existing_items):
                    if item["name"] == "Moi cau":
                        item_index = index
                        break

                if item_index is not None:
                    existing_items[item_index]["quantity"] += 5
                    quantity = existing_items[item_index]["quantity"]
                else:
                    existing_items.append({"name": "Moi cau", "emoji": "<:moicauca:1213073602996477972>", "quantity": 5})
                    quantity = 5

                cursor.execute("UPDATE users SET kho_moi = ? WHERE user_id = ?", (json.dumps(existing_items), interaction.user.id))
                conn.commit()
                await interaction.response.send_message(f"{checkcauca} **{interaction.user.mention} mua thành công 5 {moicau}, bạn đang có {quantity} {moicau}**")
            else:
                await interaction.response.send_message(f"{khongdutien} **{interaction.user.mention}, bạn không đủ {fishcoin} để mua mồi câu**", ephemeral=True)
        else:
            await interaction.response.send_message(f"{khongdutien} **{interaction.user.mention}, bạn không đủ {fishcoin} để mua mồi câu**", ephemeral=True)

    @discord.ui.button(label="Mồi X10", style=discord.ButtonStyle.blurple, emoji="<:moicauca:1213073602996477972> ", row=1, disabled=True)
    async def moicau10(self, interaction: discord.Interaction, button: discord.ui.Button):
        cursor.execute("SELECT coin_kc, kho_moi FROM users WHERE user_id = ?", (interaction.user.id,))
        result = cursor.fetchone()
        if result:
            coin_kc, existing_items_json = result
            if coin_kc >= 200:
                new_coin_kc = coin_kc - 200
                cursor.execute("UPDATE users SET coin_kc = ? WHERE user_id = ?", (new_coin_kc, interaction.user.id))

                if existing_items_json:
                    existing_items = json.loads(existing_items_json)
                else:
                    existing_items = []

                item_index = None
                for index, item in enumerate(existing_items):
                    if item["name"] == "Moi cau":
                        item_index = index
                        break

                if item_index is not None:
                    existing_items[item_index]["quantity"] += 10
                    quantity = existing_items[item_index]["quantity"]
                else:
                    existing_items.append({"name": "Moi cau", "emoji": "<:moicauca:1213073602996477972>", "quantity": 10})
                    quantity = 10

                cursor.execute("UPDATE users SET kho_moi = ? WHERE user_id = ?", (json.dumps(existing_items), interaction.user.id))
                conn.commit()
                await interaction.response.send_message(f"{checkcauca} **{interaction.user.mention} mua thành công 10 {moicau}, bạn đang có {quantity} {moicau}**")
            else:
                await interaction.response.send_message(f"{khongdutien} **{interaction.user.mention}, bạn không đủ {fishcoin} để mua mồi câu**", ephemeral=True)
        else:
            await interaction.response.send_message(f"{khongdutien} **{interaction.user.mention}, bạn không đủ {fishcoin} để mua mồi câu**", ephemeral=True)

    @discord.ui.button(label="Cần 50%", style=discord.ButtonStyle.blurple, emoji="<:can50:1213177065931804752> ", row=2, disabled=True)
    async def cancau50(self, interaction: discord.Interaction, button: discord.ui.Button):
        cursor.execute("SELECT coin_kc, kho_can FROM users WHERE user_id = ?", (interaction.user.id,))
        result = cursor.fetchone()
        if result:
            coin_kc, existing_items_json = result
            if coin_kc >= 250:
                new_coin_kc = coin_kc - 250
                cursor.execute("UPDATE users SET coin_kc = ? WHERE user_id = ?", (new_coin_kc, interaction.user.id))
                if existing_items_json:
                    existing_items = json.loads(existing_items_json)
                else:
                    existing_items = []
                item_index = None
                for index, item in enumerate(existing_items):
                    if item["name"] == "Can 50":
                        item_index = index
                        break
                if item_index is not None:
                    await interaction.response.send_message(f"{canhbao} **{interaction.user.mention} đã có cần {cancau50} rồi, không thể mua thêm**", ephemeral=True)
                    return
                else:
                    # Kiểm tra nếu trong cột kho_can đã có dữ liệu thì không thể mua cần câu mới
                    if existing_items:
                        await interaction.response.send_message(f"{canhbao} **{interaction.user.mention}, bạn đã có cần câu vip hơn, không thể mua**", ephemeral=True)
                        return
                    existing_items.append({"name": "Can 50", "emoji": "<:can50:1213177065931804752>", "used": 10})
                cursor.execute("UPDATE users SET kho_can = ? WHERE user_id = ?", (json.dumps(existing_items), interaction.user.id))
                conn.commit()
                await interaction.response.send_message(f"{checkcauca} **{interaction.user.mention} mua thành công cần 50% {cancau50}**")
            else:
                await interaction.response.send_message(f"{khongdutien} **{interaction.user.mention}, bạn không đủ {fishcoin} để mua cần câu**", ephemeral=True)
        else:
            await interaction.response.send_message(f"{khongdutien} **{interaction.user.mention}, bạn không đủ {fishcoin} để mua cần câu**", ephemeral=True)

    @discord.ui.button(label="Up 80%", style=discord.ButtonStyle.blurple, emoji="<:can80:1213179176291536926> ", row=2, disabled=True)
    async def cancau80(self, interaction: discord.Interaction, button: discord.ui.Button):
        cursor.execute("SELECT coin_kc, kho_can FROM users WHERE user_id = ?", (interaction.user.id,))
        result = cursor.fetchone()
        if result:
            coin_kc, existing_items_json = result
            if coin_kc >= 2500:  # Kiểm tra xem người dùng có đủ coin_kc để nâng cấp không
                if existing_items_json:
                    existing_items = json.loads(existing_items_json)
                else:
                    existing_items = []
                for item in existing_items:
                    if item["name"] == "Can 50":
                        # Nếu có cần 50 thì thực hiện nâng cấp
                        item["name"] = "Can 80"
                        item["emoji"] = "<:can80:1213179176291536926>"
                        item["used"] = 10  # Số lượng mặc định khi nâng cấp
                        cursor.execute("UPDATE users SET kho_can = ?, coin_kc = coin_kc - 2500 WHERE user_id = ?", (json.dumps(existing_items), interaction.user.id))
                        conn.commit()
                        await interaction.response.send_message(f"{checkcauca} **{interaction.user.mention} đã nâng cấp cần câu lên 80% thành công {cancau80}**")
                        return
                # Nếu không có cần 50 trong kho_can
                await interaction.response.send_message(f"{canhbao} **{interaction.user.mention} bạn cần cần 50% {cancau50} để có thể nâng cấp lên cần 80%**", ephemeral=True)
            else:
                await interaction.response.send_message(f"{khongdutien} **{interaction.user.mention}, bạn không đủ {fishcoin} để nâng cấp cần câu**", ephemeral=True)
        else:
            await interaction.response.send_message(f"{khongdutien} **{interaction.user.mention}, bạn không đủ {fishcoin} để nâng cấp cần câu**", ephemeral=True)

    @discord.ui.button(label="Up 100%", style=discord.ButtonStyle.blurple, emoji="<:can100:1213182598990274651> ", row=2, disabled=True)
    async def cancau100(self, interaction: discord.Interaction, button: discord.ui.Button):
        cursor.execute("SELECT coin_kc, kho_can FROM users WHERE user_id = ?", (interaction.user.id,))
        result = cursor.fetchone()
        if result:
            coin_kc, existing_items_json = result
            if coin_kc >= 5500:
                if existing_items_json:
                    existing_items = json.loads(existing_items_json)
                else:
                    existing_items = []
                for item in existing_items:
                    if item["name"] == "Can 80":
                        item["name"] = "Can 100"
                        item["emoji"] = "<:can100:1213182598990274651>"
                        item["used"] = 10
                        cursor.execute("UPDATE users SET kho_can = ?, coin_kc = coin_kc - 5500 WHERE user_id = ?", (json.dumps(existing_items), interaction.user.id))
                        conn.commit()
                        await interaction.response.send_message(f"{checkcauca} **{interaction.user.mention} đã nâng cấp cần câu lên 100% thành công {cancau100}**")
                        return
                await interaction.response.send_message(f"{canhbao} **{interaction.user.mention} bạn cần cần 80% {cancau80} để có thể nâng cấp lên cần 100%**", ephemeral=True)
            else:
                await interaction.response.send_message(f"{khongdutien} **{interaction.user.mention}, bạn không đủ {fishcoin} để nâng cấp cần câu**", ephemeral=True)
        else:
            await interaction.response.send_message(f"{khongdutien} **{interaction.user.mention}, bạn không đủ {fishcoin} để nâng cấp cần câu**", ephemeral=True)

class Fishingshop(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.command()
    async def shopca(self, ctx):
        if ctx.channel.id not in [1193936442045505546, 1026627301573677147, 1035183712582766673, 1090897131486842990, 1213122881802997770, 1107957984266563656, 1215331218124574740, 1215331281878130738]:
            return None
        if not is_registered(ctx.author.id):
            await ctx.send(f"{dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
        else:
            cursor.execute("SELECT coin_kc FROM users WHERE user_id = ?", (ctx.author.id,))
            result = cursor.fetchone()
            if result:
                result = result[0]
            else:
                result = 0
            embed = discord.Embed(title="**CỬA HÀNG CÂU CÁ**",
                color=discord.Color.from_rgb(255,255,255), description=f"")
            if ctx.author.avatar:
                avatar_url = ctx.author.avatar.url
            else:
                avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1053799649938505889/1213121495845314588/Red_and_Gold_Modern_Happy_Chinese_New_Year_Instagram_Post_7.png")
            embed.add_field(name="", value=f"**Mồi câu {moicau} / 20 {fishcoin} / 1 lượt câu**", inline=False)
            embed.add_field(name="", value=f"{cancau50} **tỉ lệ câu 50% - 250 {fishcoin}**\n{cancau80} **tỉ lệ câu 80% - 2500** {fishcoin}\n{cancau100} **tỉ lệ câu 100% - 5500** {fishcoin}\n {line}{line}{line}{line}{line}{line}{line}\n **Bạn đang có: {result} {fishcoin}**", inline=False)
            enable_buttons = ctx.author.id
            view = FishingshopView(enable_buttons)
            message = await ctx.send(embed=embed, view=view)
            view.message = message
            await view.wait()
            
async def setup(client):
    await client.add_cog(Fishingshop(client))