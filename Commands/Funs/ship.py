import discord
from discord.ext import commands
from PIL import Image, ImageDraw
import aiohttp
import io

class Ship(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="ship", description="Kiểm tra sự hợp nhau giữa hai người bằng cách ghép avatar và tính điểm.")
    async def ship(self, ctx):
        user1 = ctx.author
        user2 = ctx.message.mentions[0] if ctx.message.mentions else None
        if user2 is None:
            embed = discord.Embed(description="Hãy đề cập đến crush của bạn.", color=discord.Color.from_rgb(242, 205, 255))
            await ctx.send(embed=embed)
            return
        elif user1 == user2:
            await ctx.send("Yêu bản thân là tốt nhưng bạn cần một người khác!")
            return
        elif user2.bot:
            embed = discord.Embed(description="Không thể ghép đôi với bot!", color=discord.Color.from_rgb(242, 205, 255))
            await ctx.send(embed=embed)
            return
        else:
            score = (hash(user1.display_name + user2.display_name) % 100) + 1
            if 50 <= score < 100:
                icon = "❤️"
            elif score == 100:
                icon = "❤️‍🔥"
            elif 10 <= score < 50:
                icon = "❤️‍🩹"
            else:
                icon = "💔"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(str(user1.avatar.url)) as response1:
                    avatar1_data = await response1.read()
                
                async with session.get(str(user2.avatar.url)) as response2:
                    avatar2_data = await response2.read()
                
            avatar1 = Image.open(io.BytesIO(avatar1_data))
            avatar2 = Image.open(io.BytesIO(avatar2_data))

            # Chuyển đổi ảnh GIF thành ảnh PNG
            if avatar1.format == 'GIF':
                avatar1 = avatar1.convert('RGBA')
            if avatar2.format == 'GIF':
                avatar2 = avatar2.convert('RGBA')

            # Resize ảnh để có cùng kích thước
            avatar1 = avatar1.resize((256, 256))
            avatar2 = avatar2.resize((256, 256))
            heart = Image.open("heart.png")
            heart = heart.resize((256, 256))
            
            # Tạo ảnh mới để ghép avatar vào
            heart_image = Image.new('RGBA', (768, 256), (255, 255, 255, 0))

            # Ghép avatar vào ảnh mới
            heart_image.alpha_composite(avatar1, (0, 0))
            heart_image.alpha_composite(avatar2, (512, 0))
            heart_image.alpha_composite(heart, (256, 0))

            # Tạo tệp PNG mới
            png_output = io.BytesIO()
            heart_image.save(png_output, format='PNG')
            png_output.seek(0)

            # Thêm ảnh ghép vào embed message
            embed = discord.Embed(description=f"Độ hợp nhau giữa **{user1.mention}** và **{user2.mention}** là: **{score}**% {icon}", color=discord.Color.from_rgb(242, 205, 255))
            embed.set_image(url="attachment://result.png")
            await ctx.send(file=discord.File(png_output, filename='result.png'), embed=embed)

async def setup(client):
    await client.add_cog(Ship(client))