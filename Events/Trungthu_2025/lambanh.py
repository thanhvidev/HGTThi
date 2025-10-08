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
from Commands.Mod.list_emoji import list_emoji, lambanh_emoji
from utils.checks import is_bot_owner, is_admin, is_mod

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
        allowed_channel_ids =  [1147355133622108262, 993153068378116127, 1147035278465310720]
        if ctx.channel.id not in allowed_channel_ids:
            await ctx.send(f"{list_emoji.tick_check} **Dùng lệnh** **`zlambanh`** [__**ở đây**__](<https://discord.com/channels/832579380634451969/1147355133622108262>)")
            return False
        return True
    return commands.check(predicate)

emojidung = "<a:tickdung:1418226478558089336>"
emojisai = "<a:ticksai:1418226491279540264>"
noicom = "<:sushi_nau:1215607752005652480>"
dongho = "<a:donghocat:1418225433240932402>"
bot = "<:lambanh_bot:1416358091884335174>"
thapcam = "<:nhanthapcam:1284440549608263742>"
dauxanh = "<:lambanh_dauxanh:1416358140685058208>"
trungmuoi = "<:lambanh_trungmuoi:1416358111438045334>"
congthuc = "<:congthuc:1418225385723789372>"
lambanh1 = "<a:sach:1418225404908404796>"
tickmauxanh = "<a:tichxanh:1284504996330733610>"
banhthapcam = "<:cookthapcam:1284428897093550155>"
banhdauxanh = "<:cookdauxanh:1284429245342421103>"
naubanh = "<:cook:1284446539997118494>"
banhthapcam1 = "<:banhthapcam:1284431708640382996>"
banhdauxanh1 = "<:lambanhtrungthu:1418225491705462864>"
checkbanh = "<:check:1282056692930187387>"
timkiem = "<a:timkiem:1418227003080970351>"
so1tim = "<:so1tim:1418227935558500583>"
so2tim = "<:so2tim:1418227943456378950>"
so3tim = "<:so3tim:1418227951362768996>"
so4tim = "<:so4tim:1418227960242245763>"
hopquatrungthu = "<a:hopquatrungthu:1418227594708648059>"

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
            prize_ids = [30, 31, 32]  # IDs của các phần thưởng cần lấy thông tin
            prize_info = []
            user_id = ctx.author.id
            embed = discord.Embed(
                color=discord.Color.from_rgb(253,255,210), description=f"")
            if ctx.author.avatar:
                avatar_url = ctx.author.avatar.url
            else:
                avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
            embed.set_author(name=f"🧑‍🍳 {ctx.author.display_name} làm bánh ", icon_url=avatar_url)
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1414911120791048242/1416318153075724338/discord_fake_avatar_decorations_1757743534578.gif")
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
            embed.add_field(name="", value=f"{lambanh1} **`công thức`**: **{bot} ² + {trungmuoi} ¹ + {dauxanh} ¹**", inline=False)
            embed.add_field(name="", value=f"{congthuc} **`bạn đang có`**: {fields_value}", inline=True)
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

    @commands.command(description="Tặng combo nguyên liệu làm bánh")
    @is_bot_owner()
    async def banh(self, ctx, nguoi_nhan: discord.User, combo: int = 1):
        """Tặng combo nguyên liệu làm bánh cho người dùng"""
        if not is_registered(nguoi_nhan.id):
            await ctx.send(f"{list_emoji.tick_check} **{nguoi_nhan.display_name}** chưa đăng ký tài khoản. Cần bấm `zdk` để đăng ký")
            return
            
        if combo <= 0:
            await ctx.send(f"{list_emoji.tick_check} **Số combo phải lớn hơn 0**")
            return
            
        # Tên nguyên liệu trong database
        ingredients = {
            "bột": {"emoji": bot, "name": "bột"},
            "đậu xanh": {"emoji": dauxanh, "name": "đậu xanh"}, 
            "trứng muối": {"emoji": trungmuoi, "name": "trứng muối"}
        }
        
        total_items = 0
        combo_details = []
        
        for _ in range(combo):
            # Mỗi combo có tối thiểu mỗi nguyên liệu 1 cái
            combo_items = {"bột": 1, "đậu xanh": 1, "trứng muối": 1}
            remaining = 7  # Còn lại 7 cái để phân phối random
            
            # Phân phối 7 cái còn lại random
            for _ in range(remaining):
                random_ingredient = random.choice(list(combo_items.keys()))
                combo_items[random_ingredient] += 1
                
            combo_details.append(combo_items)
            total_items += sum(combo_items.values())
        
        # Tổng hợp tất cả combo
        total_ingredients = {"bột": 0, "đậu xanh": 0, "trứng muối": 0}
        for combo_item in combo_details:
            for ingredient, amount in combo_item.items():
                total_ingredients[ingredient] += amount
        
        # Lấy dữ liệu kho hiện tại của người nhận
        cursor.execute("SELECT open_items FROM users WHERE user_id = ?", (nguoi_nhan.id,))
        result = cursor.fetchone()
        
        if result and result[0]:
            try:
                open_items_data = json.loads(result[0])
            except json.JSONDecodeError:
                open_items_data = {}
        else:
            open_items_data = {}
        
        # Cập nhật kho với nguyên liệu mới
        for ingredient_key, total_amount in total_ingredients.items():
            ingredient_info = ingredients[ingredient_key]
            
            if ingredient_key in open_items_data:
                # Đã có trong kho, cộng thêm
                open_items_data[ingredient_key]["so_luong"] += total_amount
            else:
                # Chưa có trong kho, thêm mới
                open_items_data[ingredient_key] = {
                    "emoji": ingredient_info["emoji"],
                    "name_phanthuong": ingredient_info["name"],
                    "so_luong": total_amount
                }
        
        # Lưu lại vào database
        updated_open_items = json.dumps(open_items_data)
        cursor.execute("UPDATE users SET open_items = ? WHERE user_id = ?", (updated_open_items, nguoi_nhan.id))
        conn.commit()
        
        # Tạo thông báo với số lượng dạng superscript
        ingredients_text = ""
        for ingredient_key, total_amount in total_ingredients.items():
            ingredient_info = ingredients[ingredient_key]
            superscript_amount = get_superscript(total_amount)
            ingredients_text += f"{ingredient_info['emoji']}{superscript_amount}  "
        
        result_text = f"**{lambanh_emoji.hopqua_lambanh} {nguoi_nhan.mention} nhận được {combo} combo x10 món:  {ingredients_text}**"
        
        await ctx.send(result_text)

    @commands.command(description="Thêm bánh trung thu vào kho người dùng")
    @is_bot_owner()
    async def thembanh(self, ctx, nguoi_dung: discord.Member, so_luong: int):
        """Thêm bánh trung thu đậu xanh vào kho người dùng"""
        if not is_registered(nguoi_dung.id):
            await ctx.send(f"{emojisai} **{nguoi_dung.display_name}** chưa đăng ký tài khoản. Cần bấm `zdk` để đăng ký")
            return
            
        if so_luong <= 0:
            await ctx.send(f"{emojisai} **Số lượng phải lớn hơn 0**")
            return
        
        try:
            # Lấy dữ liệu kho hiện tại của người dùng
            cursor.execute("SELECT open_items FROM users WHERE user_id = ?", (nguoi_dung.id,))
            result = cursor.fetchone()
            
            if result and result[0]:
                try:
                    open_items_data = json.loads(result[0])
                except json.JSONDecodeError:
                    open_items_data = {}
            else:
                open_items_data = {}
            
            # Tên bánh trong database
            banh_name = "b\u1ea3nh t\u1ee7ng th\u1ee7 \u0111\u1ea7u xanh"
            
            # Cập nhật số lượng bánh
            if banh_name in open_items_data:
                open_items_data[banh_name]["so_luong"] += so_luong
            else:
                open_items_data[banh_name] = {
                    "emoji": banhdauxanh1,
                    "name_phanthuong": banh_name,
                    "so_luong": so_luong
                }
            
            # Lưu lại vào database
            updated_open_items = json.dumps(open_items_data)
            cursor.execute("UPDATE users SET open_items = ? WHERE user_id = ?", (updated_open_items, nguoi_dung.id))
            conn.commit()
            
            # Tạo thông báo với số lượng dạng superscript
            superscript_amount = get_superscript(so_luong)
            
            await ctx.send(f"{emojidung} **Đã thêm {banhdauxanh1}{superscript_amount} bánh trung thu đậu xanh vào kho của {nguoi_dung.mention}**")
            
        except Exception as e:
            await ctx.send(f"{emojisai} **Lỗi:** {str(e)}")

class LambanhView(discord.ui.View):
    def __init__(self,enable_buttons, timeout: float = 590.0):
        super().__init__(timeout=timeout)
        self.enable_buttons = enable_buttons

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.enable_buttons:
            return True
        else:
            await interaction.response.send_message("Bảng nấu bánh này của người khác", ephemeral=True)
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

    @discord.ui.button(label="", style=discord.ButtonStyle.grey, emoji="<:lambanhtrungthu:1418225491705462864>", custom_id="banhdauxanh", disabled=False)
    async def nau_dauxanh(self, interaction: discord.Interaction, Button: discord.ui.Button):
        user_id = interaction.user.id
        
        # Lần 1: Kiểm tra và trừ nguyên liệu + tiền
        cursor.execute("SELECT open_items, balance FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        
        if not result or result[1] is None or result[1] < 20000:
            await interaction.response.send_message(content=f"{emojisai} **Bạn không đủ phí 20K {list_emoji.pinkcoin} để làm bánh**", ephemeral=True)
            return
            
        if not result[0]:
            await interaction.response.send_message(content=f"{emojisai} **Bạn không đủ nguyên liệu để làm bánh**", ephemeral=True)
            return
            
        try:
            open_items_data = json.loads(result[0])
        except json.JSONDecodeError:
            await interaction.response.send_message(content=f"{emojisai} **Bạn không đủ nguyên liệu để làm bánh**", ephemeral=True)
            return
        
        # Kiểm tra xem nguyên liệu có đủ không
        kiemtra_nguyenlieu = (
            open_items_data.get("b\u1ed9t", {}).get("so_luong", 0) >= 2
            and open_items_data.get("tr\u1ee9ng mu\u1ed1i", {}).get("so_luong", 0) >= 1
            and open_items_data.get("\u0111\u1eadu xanh", {}).get("so_luong", 0) >= 1
        )
        
        if not kiemtra_nguyenlieu:
            await interaction.response.send_message(content=f"{emojisai} **Bạn không đủ nguyên liệu để làm bánh**", ephemeral=True)
            return
        
        # Update lần 1: Trừ nguyên liệu và tiền
        open_items_data["b\u1ed9t"]["so_luong"] -= 2
        open_items_data["tr\u1ee9ng mu\u1ed1i"]["so_luong"] -= 1
        open_items_data["\u0111\u1eadu xanh"]["so_luong"] -= 1
        
        updated_open_items = json.dumps(open_items_data)
        new_balance = result[1] - 20000
        
        cursor.execute(
            "UPDATE users SET open_items = ?, balance = ? WHERE user_id = ?", 
            (updated_open_items, new_balance, user_id)
        )
        conn.commit()
        
        await interaction.response.send_message(content=f'> {dongho} **Đang tiến hành làm bánh, {interaction.user.mention} đợi 10p nhé!**')
        
        # Disable nút trong 10 phút
        await self.disable_button_for("nau_dauxanh", 600)
        
        # Chờ 10 phút rồi thêm bánh
        await asyncio.sleep(600)
        
        # Update lần 2: Lấy dữ liệu hiện tại và thêm bánh
        cursor.execute("SELECT open_items FROM users WHERE user_id = ?", (user_id,))
        current_result = cursor.fetchone()
        
        if current_result and current_result[0]:
            try:
                current_open_items = json.loads(current_result[0])
            except json.JSONDecodeError:
                current_open_items = {}
        else:
            current_open_items = {}
        
        # Thêm bánh vào kho
        banh_name = "b\u1ea3nh t\u1ee7ng th\u1ee7 \u0111\u1ea7u xanh"
        if banh_name in current_open_items:
            current_open_items[banh_name]["so_luong"] += 1
        else:
            current_open_items[banh_name] = {
                "emoji": "<:lambanhtrungthu:1418225491705462864>",
                "name_phanthuong": banh_name,
                "so_luong": 1
            }
        
        # Cập nhật database
        final_open_items = json.dumps(current_open_items)
        cursor.execute("UPDATE users SET open_items = ? WHERE user_id = ?", (final_open_items, user_id))
        conn.commit()
        
        await interaction.channel.send(content=f'> {emojidung} **Bánh chín rồi, {interaction.user.mention} ơi, bạn có 1 __bánh trung thu đậu xanh__ {banhdauxanh1}**')

    @discord.ui.button(label="", style=discord.ButtonStyle.grey, emoji="<a:timkiem:1418227003080970351>", custom_id="timkiem", disabled=False)
    async def timkiem(self, interaction: discord.Interaction, Button: discord.ui.Button):
        user_id = interaction.user.id
        embed = discord.Embed(
            color=discord.Color.from_rgb(253,255,210), description=f"# {timkiem} **Cách tìm nguyên liệu**")
        embed.add_field(name="", value=f"{so1tim} **`zdaily`** **để nhận nguyên liệu ngẫu nhiên**\n\n{so2tim} **`zquest`** **và hoàn thành 3 nhiệm vụ nhận combo x10 món**\n\n{so3tim} **Tham gia chat trên sảnh để có {list_emoji.vevang} mở ra nguyên liệu**\n\n{so4tim} **Mua combo x10 món với giá 1M {list_emoji.tienowo} mỗi ngày**\n{list_emoji.muitenxeo} **give tiền cho** <@962627128204075039>", inline=False)
        server = interaction.guild  # Get the server (guild) object
        server_avatar = server.icon.url if server.icon else "https://cdn.discordapp.com/embed/avatars/0.png"  # Default avatar if none exists
        current_time = datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y")  # Format the current time

        embed.set_footer(text=f"Thời gian: {current_time}", icon_url=server_avatar)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="", style=discord.ButtonStyle.grey, emoji="<a:hopquatrungthu:1418227594708648059>", custom_id="chitietsukien", disabled=False)
    async def chitietsukien(self, interaction: discord.Interaction, Button: discord.ui.Button):
        user_id = interaction.user.id
        
        content = f"""*** Chi tiết sự kiện đua top làm bánh Trung Thu***
# {lambanh_emoji.lambanh_cup} Cuộc thi làm bánh {lambanh_emoji.lambanh_cup}

> **{lambanh_emoji.lambanh_s1}  {lambanh_emoji.banhtrungthu} １５０Ｋ {list_emoji.tienvnd} + ５Ｍ {list_emoji.tienowo} 
> {lambanh_emoji.lambanh_s2}  {lambanh_emoji.banhtrungthu} １００Ｋ {list_emoji.tienvnd} + ３Ｍ {list_emoji.tienowo} 
> {lambanh_emoji.lambanh_s3}  {lambanh_emoji.banhtrungthu} ５０Ｋ     {list_emoji.tienvnd} +  １Ｍ {list_emoji.tienowo}**

-# *Người chơi sẽ thi nhau tìm 3 nguyên liệu {bot} {dauxanh} {trungmuoi}  để làm bánh Trung Thu, cuối mùa sv sẽ tổng kết top và trao giải. Đặc biệt sv sẽ mua lại bánh của các bạn từ top 4 -7 với giá ||bí mật||, nên đừng vội nản mà hãy ráng đua để vào top 10 nha*

> -# https://discord.com/channels/832579380634451969/1215941884053295114 sự kiện tổng
> -# **`ztop`**   : xem top bánh 
> -# **`zhelp`** : xem toàn bộ hướng dẫn
> -# thời gian : 21/9 - hết ngày 8/10"""
        
        await interaction.response.send_message(content=content, ephemeral=True)

    # @discord.ui.button(label="Nấu", style=discord.ButtonStyle.primary, emoji="<:lambanhtrungthu:1418225491705462864>", custom_id="banhdauxanh", disabled=False)
    # async def nau_dauxanh(self, interaction: discord.Interaction, Button: discord.ui.Button):
    #     user_id = interaction.user.id
    #     cursor.execute("SELECT open_items FROM users WHERE user_id = ?", (user_id,))
    #     result = cursor.fetchone()
    #     if result and result[0]:
    #         open_items_data = json.loads(result[0])
    #         # Kiểm tra xem nguyên liệu có đủ không
    #         kiemtra_nguyenlieu = (
    #             open_items_data.get("nh\u00e2n \u0111\u1eadu xanh", {}).get("so_luong", 0) >= 2
    #             and open_items_data.get("tr\u1ee9ng mu\u1ed1i", {}).get("so_luong", 0) >= 2
    #         )
    #         if kiemtra_nguyenlieu:
    #             # Trừ đi số lượng nguyên liệu
    #             open_items_data["nh\u00e2n \u0111\u1eadu xanh"]["so_luong"] -= 2
    #             open_items_data["tr\u1ee9ng mu\u1ed1i"]["so_luong"] -= 2
    #             updated_open_item = json.dumps(open_items_data)
    #             cursor.execute(
    #                 "UPDATE users SET open_items = ? WHERE user_id = ?", (updated_open_item, user_id))
    #             conn.commit()
    #             if "b\u1ea3nh t\u1ee7ng th\u1ee7 \u0111\u1ea7u xanh" in open_items_data:
    #                 open_items_data["b\u1ea3nh t\u1ee7ng th\u1ee7 \u0111\u1ea7u xanh"]["so_luong"] += 1
    #             else:
    #                 open_items_data["b\u1ea3nh t\u1ee7ng th\u1ee7 \u0111\u1ea7u xanh"] = {
    #                     "emoji": "<:banhdauxanh:1284431752764588103>",
    #                     "name_phanthuong": "b\u1ea3nh t\u1ee7ng th\u1ee7 \u0111\u1ea7u xanh",
    #                     "so_luong": 1
    #                 }
    #             await interaction.response.send_message(content=f'> {naubanh} **{interaction.user.mention} đang làm "bánh trung thu đậu xanh", vui lòng chờ 10 phút {banhdauxanh1}**')
    #             # disabled nút 10p
    #             await self.disable_button_for("nau_dauxanh", 600)
    #             # Cập nhật lại cột open_items
    #             updated_open_items = json.dumps(open_items_data)
    #             cursor.execute(
    #                 "UPDATE users SET open_items = ? WHERE user_id = ?", (updated_open_items, user_id))
    #             conn.commit()
    #             await interaction.channel.send(content=f'> {checkbanh} **{interaction.user.mention} làm "bánh trung thu đậu xanh" thành công.** **Bấm** **`zinv`** **để xem nhé** ')
    #         else:
    #             await interaction.response.send_message(content=f"{emojisai} **| {interaction.user.mention} không đủ nguyên liệu để làm**", ephemeral=True)
    #     else:
    #         await interaction.response.send_message(content=f"{emojisai} **| {interaction.user.mention} không đủ nguyên liệu để làm**", ephemeral=True)


async def setup(client):
    await client.add_cog(Lambanh(client))