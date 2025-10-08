import datetime
import discord
import random
import os
from discord.ext import commands

emojis = "<a:hgtt_hpbd:1143666408148967434> "

class HPBD(commands.Cog):
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

    @commands.hybrid_command(name="happybirthday", aliases=["hpbd", "cmsn"], description="Chúc mừng sinh nhật")
    async def happy_birthday(self, ctx):
        if await self.check_command_disabled(ctx):
            return
        images = ["trang.png", "trang1.png", "trang2.png"]  
        random_image = random.choice(images)  
        file = discord.File(random_image, filename=random_image)
        # await ctx.send(f"**Mọi đóng góp để tìm kiếm bé nhanh hơn xin gửi về STK\n🏦 1018377277 - VCB\nTRAN TRONG NGHIA **")  
        await ctx.send(file=file)  
   
    # @commands.hybrid_command(name="happybirthday", aliases=["hpbd", "cmsn"], description="Chúc mừng sinh nhật")
    # async def happybirthday(self, ctx, member: discord.Member = None):
    #     if member is None:
    #         member = ctx.author
    #     now = datetime.datetime.now() 
    #     embed = discord.Embed(title=f"Hôm nay {now.strftime('%d/%m/%Y')} là 1 ngày đặc biệt", description=f"{emojis} **Chúc {member.mention} 1 ngày sinh nhật thật hạnh phúc**! {emojis}", color=discord.Color.from_rgb(242, 205, 255))
    #     if ctx.author.avatar:
    #         avatar_url = ctx.author.avatar.url
    #     else:
    #         avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
    #     embed.set_image(url=avatar_url)
    #     await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(HPBD(client))