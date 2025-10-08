import asyncio
import random
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


def get_superscript(n):
    superscripts = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    return str(n).translate(superscripts)

def get_superscript(n):
    superscripts = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    return str(n).translate(superscripts)

def is_allowed_channel():
    async def predicate(ctx):
        allowed_channel_id = 1295144686536888340
        if ctx.channel.id != allowed_channel_id:
            await ctx.send(f"{dauxdo} **Dùng lệnh** **`zsanma`** [__**ở đây**__](<https://discord.com/channels/832579380634451969/1295144686536888340>)")
            return False
        return True
    return commands.check(predicate)

dk = "<:profile:1181400074127945799>"
dauxdo = "<a:hgtt_check:1246910030444495008>"
emojidung = "<:sushi_thanhcong:1215621188059926538>"
emojisai = "<:hgtt_sai:1186839020974657657>"
xu = "<:0hgtt_halloween:1295140616233287690>"
muitencam = "<a:hgtt_muiten1:1294532028762689538>"
maxanhla = "<:maxanhla:1295557632764940380>"
maxanhduong = "<:maxanhduong:1295557613798559835>"
mado = "<:mado:1295557623894118420>"
mahong = "<:mahong:1295557641283833998>"
mavang = "<:mavang:1295557649286561853>"
matim = "<:matim:1295557658622955612>"
quasanma = "<:quasanma:1295626488951083028>"
sanma0 = "<a:sanma0:1295626501294915676>"
sanma2 = "<:sanma2:1295614902567960676>"
sanma3 = "<:sanma3:1295614912571244554>"
sanma4 = "<:sanma4:1295614925007360011>"
ksanma = "<:khongsanma:1295614935279206450>"
bupbe = "<:zannabell:1295614847010209875>"
valak = "<:zvalak:1295614854975066236>"
heit = "<:zheit:1295614874671517727>"
zombie = "<:zombie:1295614883617964042>"
vodien = "<:zvodien:1295614892786581537>"
macarong = "<a:macarong:1295621715250118686>"
cuongthi = "<:zcuongthi:1295621724465008641>"
phuthuy = "<:zphuthuy:1295621733050613895>"
 

class SanmaView(discord.ui.View):
    def __init__(self, enable_buttons, timeout: float = 180.0):
        super().__init__(timeout=timeout)
        self.enable_buttons = enable_buttons

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.enable_buttons:
            return True
        else:
            await interaction.response.send_message("Bạn không có quyền sử dụng menu này", ephemeral=True)
            return False

    async def disable_all_items_for(self, disable_time: int = 10):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)
        # Sau 10 giây, bật lại các button
        await asyncio.sleep(disable_time)
        for item in self.children:
            item.disabled = False
        await self.message.edit(view=self)    

    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self) 

    async def on_timeout(self) -> None:
        await self.disable_all_items()
        return await super().on_timeout()

    # Hàm xử lý khi button được ấn
    async def button_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.disable_all_items()
        user_id = interaction.user.id  
        cursor.execute("SELECT xu_hlw, open_items FROM users WHERE user_id = ?", (user_id,))  
        result = cursor.fetchone()
        if result:
            
            xu_hlw = result[0]
        else:
            xu_hlw = 0

        if xu_hlw < 1:
            await interaction.followup.send(f"> **{interaction.user.mention} k đủ {xu} để chơi rồi, hãy làm nhiệm vụ để có thêm xu nhé!**")
            return
        
        message = await interaction.followup.send(f"# {quasanma} úm ba la, con ma gì ra {quasanma}\n# ㅤㅤㅤㅤ{sanma0}{sanma0}{sanma0}")
        cursor.execute("UPDATE users SET xu_hlw = xu_hlw - 1 WHERE user_id = ?", (user_id,))
        conn.commit()
            # 1: {"name": "Annabelle", "emoji": bupbe},  
            # 2: {"name": "Valak", "emoji": valak},  
            # 3: {"name": "Heit", "emoji": heit},  
            # 4: {"name": "plantvs", "emoji": zombie},  
            # 5: {"name": "Vô Diện", "emoji": vodien},  
            # 6: {"name": "Dracula", "emoji": macarong},  
            # 7: {"name": "Cương Thi", "emoji": cuongthi},  
            # 8: {"name": "Phù Thủy", "emoji": phuthuy}  
        options = [1, 2, 3, 4, 5, 6, 7, 8, 9]  
        weights = [15, 11, 1, 15, 5, 15, 15, 1, 22] 
        chosen_random = random.choices(options, weights=weights, k=1)[0]

        await asyncio.sleep(9)
        await self.cap_nhat_ma(interaction, chosen_random)
          
        if chosen_random == 1:
            await message.edit(content=f"{sanma2} **{interaction.user.mention} Triệu hồi thành công Búp bê ma Annabelle**\n# ㅤㅤㅤㅤ{bupbe}{bupbe}{bupbe}\n-# **Nhanh tay hoàn thành bst ma quỷ để nhận quà nhé!**")
        elif chosen_random == 2:
            await message.edit(content=f"{sanma2} **{interaction.user.mention} Triệu hồi thành công Ác quỷ ma sơ Valak**\n# ㅤㅤㅤㅤ{valak}{valak}{valak}\n-# **Nhanh tay hoàn thành bst ma quỷ để nhận quà nhé!**")
        elif chosen_random == 3:
            await message.edit(content=f"{sanma2} **{interaction.user.mention} Triệu hồi thành công Gã hề ma quái**\n# ㅤㅤㅤㅤ{heit}{heit}{heit}\n-# **Nhanh tay hoàn thành bst ma quỷ để nhận quà nhé!**")
        elif chosen_random == 4:
            await message.edit(content=f"{sanma2} **{interaction.user.mention} Triệu hồi thành công Zombie **\n# ㅤㅤㅤㅤ{zombie}{zombie}{zombie}\n-# **Nhanh tay hoàn thành bst ma quỷ để nhận quà nhé!**")
        elif chosen_random == 5:
            await message.edit(content=f"{sanma2} **{interaction.user.mention} Triệu hồi thành công Quỷ vô diện**\n# ㅤㅤㅤㅤ{vodien}{vodien}{vodien}\n-# **Nhanh tay hoàn thành bst ma quỷ để nhận quà nhé!**")
        elif chosen_random == 6:
            await message.edit(content=f"{sanma2} **{interaction.user.mention} Triệu hồi thành công Ma cà rồng Dracula**\n# ㅤㅤㅤㅤ{macarong}{macarong}{macarong}\n-# **Nhanh tay hoàn thành bst ma quỷ để nhận quà nhé!**")
        elif chosen_random == 7:
            await message.edit(content=f"{sanma2} **{interaction.user.mention} Triệu hồi thành công Ma Cương Thi**\n# ㅤㅤㅤㅤ{cuongthi}{cuongthi}{cuongthi}\n-# **Nhanh tay hoàn thành bst ma quỷ để nhận quà nhé!**")
        elif chosen_random == 8:
            await message.edit(content=f"{sanma2} **{interaction.user.mention} Triệu hồi thành công mụ Phù Thủy**\n# ㅤㅤㅤㅤ{phuthuy}{phuthuy}{phuthuy}\n-# **Nhanh tay hoàn thành bst ma quỷ để nhận quà nhé!**")
        elif chosen_random == 9:
            await message.edit(content=f"# {sanma4} Boo! k có con ma nào {sanma4}\n# ㅤㅤㅤㅤ{ksanma}{ksanma}{ksanma}\n-# **Nhanh tay hoàn thành bst ma quỷ để nhận quà nhé!**")

    async def cap_nhat_ma(self, interaction: discord.Interaction, chosen_random):
        user_id = interaction.user.id  
        cursor.execute("SELECT open_items FROM users WHERE user_id = ?", (user_id,))  
        result = cursor.fetchone()  
        open_items_data = result[0] if result else None  
        open_items_dict = json.loads(open_items_data) if open_items_data else {}  

        reward_items = {  
            1: {"name": "Annabelle", "emoji": bupbe},  
            2: {"name": "Valak", "emoji": valak},  
            3: {"name": "Heit", "emoji": heit},  
            4: {"name": "plantvs", "emoji": zombie},  
            5: {"name": "Vô Diện", "emoji": vodien},  
            6: {"name": "Dracula", "emoji": macarong},  
            7: {"name": "Cương Thi", "emoji": cuongthi},  
            8: {"name": "Phù Thủy", "emoji": phuthuy}  
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

    @discord.ui.button(label="", style=discord.ButtonStyle.gray, emoji="<:maxanhduong:1295557613798559835>", row=1)
    async def button_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.button_callback(interaction)
    
    @discord.ui.button(label="", style=discord.ButtonStyle.gray, emoji="<:maxanhla:1295557632764940380>", row=1)
    async def button_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.button_callback(interaction)
    
    @discord.ui.button(label="", style=discord.ButtonStyle.gray, emoji="<:matim:1295557658622955612>", row=1)
    async def button_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.button_callback(interaction)

    @discord.ui.button(label="", style=discord.ButtonStyle.gray, emoji="<:mavang:1295557649286561853>", row=2)
    async def button_4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.button_callback(interaction)

    @discord.ui.button(label="", style=discord.ButtonStyle.gray, emoji="<:mahong:1295557641283833998>", row=2)
    async def button_5(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.button_callback(interaction)

    @discord.ui.button(label="", style=discord.ButtonStyle.gray, emoji="<:mahong:1295557641283833998>", row=2)
    async def button_6(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.button_callback(interaction)


class Sanma(commands.Cog):
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

    @commands.hybrid_command(description="Mở hộp halloween", help="Mở hộp halloween")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @is_allowed_channel()
    async def sanma(self, ctx):
        if await self.check_command_disabled(ctx):
            return
        user_id = ctx.author.id
        if not is_registered(user_id):
            await ctx.send(f"{dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
            return
        enable_buttons = user_id
        view = SanmaView(enable_buttons)
        message = await ctx.send(f"{sanma3} **{ctx.author.mention} -1 {xu} để chơi săn ma {sanma3}**\n-# **Chọn 1 trong những ô bên dưới**", view=view)
        view.message = message
        await view.wait()

    @sanma.error
    async def sanma_error(self, ctx, error):
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
        
    @commands.command(description="set xu cho người khác")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @is_guild_owner_or_bot_owner()
    async def setxuhlww(self, ctx, amount: int, member: typing.Optional[discord.Member] = None):
        if member is None:  # Nếu không nhập người dùng, set cho tất cả người dùng trong bảng users
            cursor.execute("UPDATE users SET xu_hlw = xu_hlw + ?", (amount,))
            conn.commit()
            formatted_amount = "{:,}".format(amount)
            await ctx.send(f"**HGTT đã trao tặng** __**{formatted_amount}**__ {xu} **cho tất cả thành viên**")
        elif is_registered(member.id):
            cursor.execute(
                "UPDATE users SET xu_hlw = xu_hlw + ? WHERE user_id = ?", (amount, member.id))
            conn.commit()
            formatted_amount = "{:,}".format(amount)
            await ctx.send(f"**HGTT đã trao tặng** __**{formatted_amount}**__ {xu} **cho {member.display_name}**")
        else:
            await ctx.send("Bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")

async def setup(client):
    await client.add_cog(Sanma(client))