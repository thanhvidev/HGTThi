import asyncio
import random  
import discord  
from discord.ext import commands  
import json  
import os  
from Commands.Mod.list_emoji import list_emoji, profile_emoji
from utils.checks import is_bot_owner, is_admin, is_mod

class Toggle(commands.Cog):  
    def __init__(self, client):  
        self.client = client  
        self.toggle_file = "toggle.json"  
        self.toggles = {}  # Khởi tạo một từ điển cho toggles  
        self.load_toggles()  
        self.set_default_toggles(guild_id="832579380634451969")  # Gọi phương thức để thiết lập các lệnh mặc định cho guild cụ thể  

    def load_toggles(self):  
        if os.path.exists(self.toggle_file):  
            with open(self.toggle_file, "r") as f:  
                try:  
                    self.toggles = json.load(f)  
                except json.JSONDecodeError:  
                    self.toggles = {}  
                    self.save_toggles()  # Tạo lại tệp với dữ liệu khởi tạo  
        else:  
            self.toggles = {}  
            self.save_toggles()  # Tạo tệp mới với dữ liệu mặc định  

    def save_toggles(self):  
        with open(self.toggle_file, "w") as f:  
            json.dump(self.toggles, f, indent=4)  # Thêm indent để dễ đọc  

    def set_default_toggles(self, guild_id):  
        # Thiết lập các lệnh mặc định cho guild cụ thể  
        if guild_id not in self.toggles:  
            self.toggles[guild_id] = {}  # Thêm một dict cho guild nếu chưa có  
        
        # Lặp qua tất cả các Cog  
        for cog in self.client.cogs.values():  
            for command in cog.get_commands():  # Lấy tất cả các lệnh từ Cog  
                command_name = command.name.lower()  
                if command_name not in self.toggles[guild_id]:  
                    self.toggles[guild_id][command_name] = []  # Thêm một danh sách rỗng nếu lệnh chưa có   

        self.save_toggles()  # Cập nhật lại tệp toggle.json  

    @commands.command(description="Enable a command", help="Enable a command")
    @commands.cooldown(1, 2, commands.BucketType.user)  
    @is_bot_owner()
    async def enable(self, ctx, command: str):  
        command = command.lower()  
        
        if command == "all":  
            # Bật tất cả lệnh  
            if str(ctx.guild.id) not in self.toggles:  
                self.toggles[str(ctx.guild.id)] = {}  
            for cmd in self.toggles[str(ctx.guild.id)].keys():  
                if ctx.channel.id in self.toggles[str(ctx.guild.id)][cmd]:  
                    self.toggles[str(ctx.guild.id)][cmd].remove(ctx.channel.id)  
            self.save_toggles()  
            await ctx.send(f"Tất cả lệnh đã được bật lại ở kênh <#{ctx.channel.id}>.")  
        else:  
            if command in self.toggles.get(str(ctx.guild.id), {}):  
                if ctx.channel.id in self.toggles[str(ctx.guild.id)][command]:  
                    self.toggles[str(ctx.guild.id)][command].remove(ctx.channel.id)  
                    self.save_toggles()  
                    await ctx.send(f"Lệnh `{command}` đã được bật lại ở kênh <#{ctx.channel.id}>.")  
                else:  
                    await ctx.send(f"Lệnh `{command}` hiện không bị tắt ở kênh <#{ctx.channel.id}>.")  
            else:  
                await ctx.send(f"Lệnh `{command}` không tồn tại.")  

    @enable.error
    async def enable_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = divmod(int(error.retry_after), 60)  # Chia cho 60 để có phút và giây
            formatted_time = f"{remaining_time[0]}m{remaining_time[1]}s"
            message = await ctx.send(f"{self.chamthan} | Vui lòng đợi thêm `{formatted_time}` để có thể sử dụng lệnh này!!")
            await asyncio.sleep(2)
            await message.delete()
            await ctx.message.delete()
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error

    @commands.command(description="Disable a command", help="Disable a command") 
    @commands.cooldown(1, 2, commands.BucketType.user)   
    @is_bot_owner()
    async def disable(self, ctx, command: str):  
        command = command.lower()  
        
        if command == "all":  
            # Tắt tất cả lệnh  
            if str(ctx.guild.id) not in self.toggles:  
                self.toggles[str(ctx.guild.id)] = {}  
            for cmd in self.toggles[str(ctx.guild.id)].keys():  
                if ctx.channel.id not in self.toggles[str(ctx.guild.id)][cmd]:  
                    self.toggles[str(ctx.guild.id)][cmd].append(ctx.channel.id)  
            self.save_toggles()  
            await ctx.send(f"Tất cả lệnh đã bị tắt ở kênh <#{ctx.channel.id}>.")  
        else:  
            if command in self.toggles.get(str(ctx.guild.id), {}):  
                if ctx.channel.id not in self.toggles[str(ctx.guild.id)][command]:  
                    self.toggles[str(ctx.guild.id)][command].append(ctx.channel.id)  
                    self.save_toggles()  
                    message = await ctx.send(f"Lệnh `{command}` đã bị tắt ở kênh <#{ctx.channel.id}>.")  
                    await asyncio.sleep(5)
                    await message.delete()
                else:  
                    await ctx.send(f"Lệnh `{command}` đã bị tắt ở kênh <#{ctx.channel.id}> rồi.")  
            else:  
                if command not in ['help', 'enable', 'disable']:  
                    if str(ctx.guild.id) not in self.toggles:  
                        self.toggles[str(ctx.guild.id)] = {}  
                    self.toggles[str(ctx.guild.id)][command] = [ctx.channel.id]  
                    self.save_toggles()  
                    message = await ctx.send(f"Lệnh `{command}` đã bị tắt ở kênh <#{ctx.channel.id}>.")  
                    await asyncio.sleep(2)
                    await message.delete()
                else:  
                    await ctx.send(f"Không thể tắt lệnh `{command}`.")  

    @disable.error
    async def disable_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = divmod(int(error.retry_after), 60)  # Chia cho 60 để có phút và giây
            formatted_time = f"{remaining_time[0]}m{remaining_time[1]}s"
            message = await ctx.send(f"{self.chamthan} | Vui lòng đợi thêm `{formatted_time}` để có thể sử dụng lệnh này!!")
            await asyncio.sleep(2)
            await message.delete()
            await ctx.message.delete()
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error

    @commands.Cog.listener()  
    async def on_command(self, ctx):  
        command_name = ctx.command.name.lower()  
        guild_id = str(ctx.guild.id)  

        if guild_id in self.toggles and command_name in self.toggles[guild_id]:  
            if ctx.channel.id in self.toggles[guild_id][command_name]:  
                return

async def setup(client):  
    await client.add_cog(Toggle(client))