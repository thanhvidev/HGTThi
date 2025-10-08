import datetime
import discord
from discord.ext import commands

# Thời gian bắt đầu hoạt động của bot
start_time = datetime.datetime.now()

maytinh = "<:maytinh_hgtt:1267330765545410590>"

class Ping(commands.Cog):
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
    
    # Events
    @commands.hybrid_command(description="Kiểm tra đường truyền của bot")
    async def pin(self, ctx):
        embed = discord.Embed(
            description=f"🏓 Ping của bot là **{round(self.client.latency * 1000)}** ms", color=discord.Color.from_rgb(242, 205, 255))
        await ctx.send(embed=embed)

    @commands.command()
    async def uptime(self, ctx):
        """Hiển thị thời gian hoạt động của bot"""
        delta = datetime.datetime.now() - start_time
        days, seconds = delta.days, delta.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        embed = discord.Embed(
            title="Thời gian hoạt động của bot", color=discord.Color.green())
        embed.add_field(name="Bot đã hoạt động trong:",
                        value=f"{hours} giờ, {minutes} phút và {seconds} giây.", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def m(self, ctx, *, expression):
        if await self.check_command_disabled(ctx):
            return
        try:
            result = eval(expression)
            await ctx.send(f"{maytinh} Kết quả: **{result}**")
        except Exception as e:
            await ctx.send(f"**ghi sai lệnh rồi con chó**")

async def setup(client):
    await client.add_cog(Ping(client))