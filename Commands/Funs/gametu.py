import asyncio
import random
import typing  
import discord  
from discord.ext import commands  

def is_guild_owner_or_bot_owner():  
    async def predicate(ctx):  
        return ctx.author == ctx.guild.owner or ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222  
    return commands.check(predicate)

class Gametu(commands.Cog):
    def __init__(self, client):  
        self.client = client
        self.active_game = False  # Biến kiểm tra game đang chạy
        self.answer = None  # Lưu đáp án của game hiện tại
        self.game_task = None  # Lưu task của game để có thể hủy

    async def check_command_disabled(self, ctx):  
        guild_id = str(ctx.guild.id)  
        command_name = ctx.command.name.lower()  
        if guild_id in self.client.get_cog('Toggle').toggles:  
            if command_name in self.client.get_cog('Toggle').toggles[guild_id]:  
                if ctx.channel.id in self.client.get_cog('Toggle').toggles[guild_id][command_name]:  
                    await ctx.send(f"Lệnh `{command_name}` đã bị tắt ở kênh này.")  
                    return True  
        return False

    @commands.hybrid_command(name="gametu", description="đoán từ")
    @is_guild_owner_or_bot_owner()
    async def gametu(self, ctx, *, cauhoi: typing.Optional[str] = None, traloi: typing.Optional[str] = None):
        if await self.check_command_disabled(ctx):
            return
        if self.active_game:
            await ctx.channel.send("Đang có trò chơi đoán từ khác đang diễn ra. Vui lòng chờ.")
            return
        
        if cauhoi is None or traloi is None:
            await ctx.channel.send("Vui lòng nhập đầy đủ câu hỏi và đáp án!")
            return
        
        self.answer = traloi.lower()
        self.active_game = True
        await ctx.channel.send(f"# Đoán từ trong 15 giây: {cauhoi}")

        # Tạo một task để đếm thời gian 15 giây
        self.game_task = asyncio.create_task(self.end_game(ctx, 15))

    async def end_game(self, ctx, time_limit):
        # Đếm ngược 15 giây
        await asyncio.sleep(time_limit)
        if self.active_game:
            await ctx.channel.send(f"Hết thời gian! Đáp án đúng là: {self.answer}")
            self.reset_game()

    @commands.hybrid_command(name="gamestop_chu", description="Dừng trò chơi đoán từ")
    @is_guild_owner_or_bot_owner()
    async def gamestop_chu(self, ctx):
        if not self.active_game:
            await ctx.channel.send("Hiện không có trò chơi đoán từ nào đang diễn ra.")
        else:
            if self.game_task:
                self.game_task.cancel()  # Hủy task đang đếm thời gian
            await ctx.channel.send("Trò chơi đoán chữ đã bị dừng.")
            self.reset_game()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not self.active_game:
            return

        try:
            if message.content.lower() == self.answer:
                await message.reply(f"Chúc mừng bạn đã đoán đúng từ `{self.answer}`!")
                self.reset_game()
        except Exception as e:
            print(e)

    def reset_game(self):
        self.active_game = False
        self.answer = None
        self.game_task = None

async def setup(client):
    await client.add_cog(Gametu(client))