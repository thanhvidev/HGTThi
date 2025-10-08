import discord
from discord.ext import commands
import datetime
import pytz

mayanh = "<:camera:1339291110127702098>"

class Avatar(commands.Cog):
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

    @commands.hybrid_command(aliases=["av", "avt"], description="Kiểm tra avatar của người trong giang hồ")
    async def avatar(self, ctx, user: discord.Member = None):
        if await self.check_command_disabled(ctx):
            return
        if user is None:
            user = ctx.author

        embed = discord.Embed(color=discord.Color.from_rgb(242, 205, 255))
        # Lấy múi giờ hiện tại của Việt Nam
        timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        current_time = datetime.datetime.now(timezone)

        if user.avatar and user.guild_avatar:
            embed = discord.Embed(title="", description=f"{mayanh} **Avatar** {user.mention}", color=discord.Color.from_rgb(242, 205, 255), timestamp=current_time)
            embed.set_image(url=user.guild_avatar.url)
            embed.set_thumbnail(url=user.avatar.url)
            embed.set_footer(text=f"Người thực hiện: {ctx.author.name}")
            await ctx.send(embed=embed)

        elif user.avatar:
            embed = discord.Embed(title="", description=f"{mayanh} **Avatar Cá Nhân** {user.mention}", color=discord.Color.from_rgb(242, 205, 255), timestamp=current_time)
            embed.set_image(url=user.avatar.url)
            embed.set_footer(text=f"Người thực hiện: {ctx.author.name}")
            await ctx.send(embed=embed)

        elif user.guild_avatar:
            embed = discord.Embed(title="", description=f"{mayanh} **Avatar Máy Chủ** {user.mention}", color=discord.Color.from_rgb(242, 205, 255), timestamp=current_time)
            embed.set_image(url=user.guild_avatar.url)
            embed.set_footer(text=f"Người thực hiện: {ctx.author.name}")
            await ctx.send(embed=embed)

        else:
            embed.add_field(name="Không có ảnh hồ sơ", value="\u200b")
            await ctx.send(embed=embed)

async def setup(client):
    await client.add_cog(Avatar(client))
    