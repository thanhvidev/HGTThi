import asyncio
import typing
import discord
from discord.ext import commands
from discord.ui import Button, View
import sqlite3
import random
from Commands.Mod.list_emoji import list_emoji, profile_emoji
from utils.checks import is_bot_owner, is_admin, is_mod

conn = sqlite3.connect('economy.db')
cursor = conn.cursor()

def is_registered(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None

def update_balance(user_id, amount):
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()

def is_allowed_channel_check():
    async def predicate(ctx):
        allowed_channel_ids = [1147355133622108262, 1152710848284991549, 1079170812709458031, 1207593935359320084, 1215331218124574740,1215331281878130738, 1051454917702848562, 1210296290026455140, 1210417888272318525, 1256198177246285825, 1050649044160094218, 1091208904920281098, 1238177759289806878, 1243264114483138600, 1251418765665505310, 1243440233685712906, 1237810926913323110, 1247072223861280768, 1270031327999164548, 1022533822031601766, 1065348266193063979, 1027622168181350400, 1072536912562241546, 1045395054954565652, 1273768834830041301, 1273768884885000326, 1273769291099144222, 1026627301573677147, 1035183712582766673, 1090897131486842990, 1213122881802997770, 1104362707580375120]
        if ctx.channel.id in allowed_channel_ids:
            return False
        return True
    return commands.check(predicate)

#emojji
canhbao = "<:chamthan:1213200604495749201>"
dk = "<:profile:1181400074127945799>"
tienhatgiong = "<:timcoin:1192458078294122526>"
vs = "<:vs_keobuabao:1419198096620912780>"
star = "<a:hgtt_star:1244742447360249907>"
fire = ""
phone = "<a:hgtt_kbb:1244978980168269846>"

class KeoBuaBaoView(discord.ui.View):
    def __init__(self, player1, player2=None, amount=None, timeout=15.0, against_bot=False):
        super().__init__(timeout=timeout)
        self.player1 = player1
        self.player2 = player2
        self.amount = amount
        self.choices = {player1.id: None}
        self.against_bot = against_bot
        if player2:
            self.choices[player2.id] = None
        else:
            self.bot_choice = random.choice(['Bao', 'Búa', 'Kéo'])

    async def interaction_check(self, interaction):
        if interaction.user.id in self.choices:
            return True
        await interaction.response.send_message("Có chơi với mày đâu mà bấm?", ephemeral=True)
        return False

    async def button_callback(self, interaction, button, choice):
        user_id = interaction.user.id
        if self.choices[user_id] is not None:
            await interaction.response.send_message("Chọn 1 lần thôi, ham hố thế!", ephemeral=True)
            return 
        self.choices[user_id] = choice
        await interaction.response.send_message(f"Bạn đã chọn {choice}!", ephemeral=True)  
        if all(choice is not None for choice in self.choices.values()):
            await self.disable_all_items()
            await asyncio.sleep(1)
            await self.process_results()

    async def process_results(self): 
        p1_choice = self.choices[self.player1.id]
        p2_choice = self.bot_choice if self.against_bot else self.choices[self.player2.id]

        result_message = f"{star} {self.player1.mention} chọn **{p1_choice}**, "
        if self.against_bot:
            result_message += f"**HGTT** chọn **{p2_choice}**.\n"
        else:
            result_message += f"{self.player2.mention} chọn **{p2_choice}**.\n"
        embed = discord.Embed(title="", color=discord.Color.from_rgb(242, 205, 255), description="")
        embed.set_author(name="Kết Quả", icon_url="https://cdn.discordapp.com/avatars/1063071492520280144/3ab3ec3af03f5acd5bf8b6757ebf8cb9.png")

        if p1_choice == p2_choice:
            result_message += f"{star} Kết quả: **Hòa**!"
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1053799649938505889/1244958788990275615/Gradient_Fun_Quiz_Time_Instagram_Post_35.png")            
            if self.amount and not self.against_bot:
                update_balance(self.player1.id, self.amount)
                update_balance(self.player2.id, self.amount)
            if self.amount and self.against_bot:
                update_balance(self.player1.id, self.amount)
        else:
            win_conditions = {'Kéo': 'Bao', 'Búa': 'Kéo', 'Bao': 'Búa'}
            if win_conditions[p1_choice] == p2_choice:
                if self.amount:
                    result_message += f"{star} Kết quả: {self.player1.mention} thắng **{self.amount:,}** {list_emoji.pinkcoin} !"
                    update_balance(self.player1.id, self.amount * 2)
                    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1053799649938505889/1244958789556502613/61.png")
                else:
                    result_message += f"{star} Kết quả: {self.player1.mention} thắng!"
                    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1053799649938505889/1244958789556502613/61.png")
            else:
                if self.amount:
                    if self.against_bot:
                        result_message += f"{star} Kết quả: {self.player1.mention} thua **{self.amount:,}** {list_emoji.pinkcoin} !"
                        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1053799649938505889/1244958789992448052/62.png")
                    else:
                        result_message += f"{star} Kết quả: {self.player1.mention} thua **{self.amount:,}** {list_emoji.pinkcoin} !"
                        update_balance(self.player2.id, self.amount * 2)
                        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1053799649938505889/1244958789992448052/62.png")
                else:
                    if self.against_bot:
                        result_message += f"{star} Kết quả: {self.player1.mention} **thua**!"
                        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1053799649938505889/1244958789992448052/62.png")
                    else:
                        result_message += f"{star} Kết quả: {self.player1.mention} **thua**!"
                        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1053799649938505889/1244958789992448052/62.png")
#        embed = self.message.embeds[0]
        embed.add_field(name="", value=result_message, inline=False)
        await self.message.edit(embed=embed, view=self)

    async def on_timeout(self) -> None:
        await self.disable_all_items()
        if self.amount:
            if self.against_bot:
                # Chỉ cần kiểm tra lựa chọn của player1 nếu chơi với bot
                if self.choices[self.player1.id] is None:
                    update_balance(self.player1.id, self.amount)
            else:
                # Với trò chơi 2 người, kiểm tra cả 2 người chơi
                if self.choices[self.player1.id] is None or self.choices[self.player2.id] is None:
                    update_balance(self.player1.id, self.amount)
                    update_balance(self.player2.id, self.amount)
        return await super().on_timeout()


    # async def on_timeout(self) -> None:
    #     await self.disable_all_items()  
    #     if self.choices[self.player1.id] is None or self.choices[self.player2.id] is None :
    #         if self.amount and not self.against_bot :  
    #             update_balance(self.player1.id, self.amount) 
    #             update_balance(self.player2.id, self.amount)
    #         if self.amount and self.against_bot:
    #             update_balance(self.player1.id, self.amount)
    #     return await super().on_timeout()
    
    async def disable_button_for(self, button_name: str, duration: int):
        button = getattr(self, button_name)
        button.disabled = True
        await self.message.edit(view=self)
        await asyncio.sleep(duration)
        button.disabled = False
        await self.message.edit(view=self)

    @discord.ui.button(label="Kéo", style=discord.ButtonStyle.grey, emoji="<:keovang:1419198519436378173>")
    async def keo_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.button_callback(interaction, button, 'Kéo')

    @discord.ui.button(label="Búa", style=discord.ButtonStyle.grey, emoji="<:buavang:1419198527921328169>")
    async def bua_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.button_callback(interaction, button, 'Búa')

    @discord.ui.button(label="Bao", style=discord.ButtonStyle.grey  , emoji="<:baovang:1419198536393687111>")
    async def bao_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.button_callback(interaction, button, 'Bao')

    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

class KeoBuaBao(commands.Cog):
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

    @commands.command(name='KEOBUABAO', aliases=["kbb"])
    @commands.cooldown(1, 15, commands.BucketType.user)
    @is_allowed_channel_check()
    async def keobuabao(self, ctx, member: typing.Optional[discord.Member] = None, amount: typing.Optional[int] = None):
        if await self.check_command_disabled(ctx):
            return
        if member is not None and member == ctx.author:
            await ctx.send("Bạn không thể tự chơi với chính mình.")
            return
        if amount and amount <= 0:
            await ctx.send("Số tiền cược phải lớn hơn 0.")
            return
        if amount and amount > 500000:
            await ctx.send("Số tiền cược phải nhỏ hơn hoặc bằng 500,000.")
            return
        if amount and not is_registered(ctx.author.id):
            await ctx.send("Bạn phải đăng ký `zdk` tài khoản trước.")
            return
        if member and not is_registered(member.id):
            await ctx.send("Người chơi phải đăng ký `zdk` tài khoản trước.")
            return
        if member and amount:
            cursor.execute("SELECT balance FROM users WHERE user_id = ?", (ctx.author.id,))
            author_balance = cursor.fetchone()
            cursor.execute("SELECT balance FROM users WHERE user_id = ?", (member.id,))
            member_balance = cursor.fetchone()
            if author_balance[0] < amount or member_balance[0] < amount:
                await ctx.send("Cả hai người chơi phải có đủ số tiền cược.")
                return
            update_balance(ctx.author.id, -amount)
            update_balance(member.id, -amount)
        elif amount:
            cursor.execute("SELECT balance FROM users WHERE user_id = ?", (ctx.author.id,))
            author_balance = cursor.fetchone()
            if author_balance[0] < amount:
                await ctx.send("Bạn phải có đủ số tiền cược.")
                return
            update_balance(ctx.author.id, -amount)

        against_bot = member is None
        view = KeoBuaBaoView(ctx.author, member, amount, against_bot=against_bot)
        embed = discord.Embed(title="", color=discord.Color.from_rgb(242, 205, 255), description="")
        embed.set_author(name="Kéo Búa Bao", icon_url="https://cdn.discordapp.com/avatars/1063071492520280144/3ab3ec3af03f5acd5bf8b6757ebf8cb9.png")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1053799649938505889/1244958788990275615/Gradient_Fun_Quiz_Time_Instagram_Post_35.png")
        if member:
            embed.add_field(name="", value=f"{phone} {ctx.author.mention} {vs} {member.mention}", inline=True)
        else:
            embed.add_field(name="", value=f"{phone} {ctx.author.mention} {vs} **HGTT**", inline=True)
        if amount:
            embed.add_field(name="", value=f"{phone} Tiền cược: **{amount:,}** {list_emoji.pinkcoin}", inline=False)
        embed.timestamp = ctx.message.created_at
        message = await ctx.send(embed=embed, view=view)
        view.message = message

    @keobuabao.error
    async def keobuabao_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = divmod(int(error.retry_after), 60)  # Chia cho 60 để có phút và giây
            formatted_time = f"{remaining_time[1]}s"
            message = await ctx.send(f"{canhbao} | Vui lòng đợi thêm `{formatted_time}` để có thể sử dụng lệnh này!!")
            await asyncio.sleep(3)
            await message.delete()
            await ctx.message.delete()
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error