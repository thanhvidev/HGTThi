import asyncio
import random
import aiohttp
import discord
from discord.ext import commands
import requests
#from pyvi import ViTokenizer, ViPosTagger
import asyncio
import io
import os
import aiohttp
from PIL import Image, ImageDraw

daulau = '<:daulau:1372217056963068024>'
lich = '<a:lich_daily:1362248474166427759>'

class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.last_message = ""
        self.last_author = None  # Thêm biến lưu trữ người gửi tin nhắn cuối cùng
        # Đường dẫn tới các file ảnh
        self.RIP_TEMPLATE = "rip.png"
        self.DEFAULT_AVATAR = "default_avatar.png"

    def get_guild_emojis(self, guild_id):
        # Thay đổi tham số đầu vào thành guild_id thay vì guild
        emoji_list = [
            ("<:hun:1146520409840304368>", "hun dô má"),
            ("<:hun:1146520409840304368>", "hun dô mỏ"),
            ("<:hun:1146520409840304368>", "hun dô zú"),
            ("<:hun:1146520409840304368>", "hun dô nách"),
            ("<:hun:1146520409840304368>", "hun dô tay"),
            ("<:hun:1146520409840304368>", "nút lưỡi")
        ]
        return emoji_list

    async def check_command_disabled(self, ctx):  
        guild_id = str(ctx.guild.id)  
        command_name = ctx.command.name.lower()  
        if guild_id in self.client.get_cog('Toggle').toggles:  
            if command_name in self.client.get_cog('Toggle').toggles[guild_id]:  
                if ctx.channel.id in self.client.get_cog('Toggle').toggles[guild_id][command_name]:  
                    await ctx.send(f"Lệnh `{command_name}` đã bị tắt ở kênh này.")  
                    return True  
        return False 

    @commands.command()
    async def hun(self, ctx, *, member: discord.Member = None):
        if await self.check_command_disabled(ctx):
            return
        if member:
            author_name = ctx.author.mention
            tagged_user_name = member.mention

            guild_id = 1090136467541590066
            # Sử dụng guild_id thay vì ctx.guild
            guild_emojis = self.get_guild_emojis(guild_id)

            if guild_emojis:
                random_emoji, action = random.choice(guild_emojis)

                if member.bot:  # Kiểm tra xem người được tag có phải là bot
                    response = f"{author_name}, **FA** hay sao mà tag bot để hun?"
                elif member == ctx.author:  # Kiểm tra xem người được tag có phải là bản thân người gửi lệnh không
                    response = f"{author_name}, **FA** hay sao mà tự hun mình?"
                else:
                    response = f"{random_emoji}  {author_name} **đã {action}** {tagged_user_name}"
                await ctx.send(response)
            else:
                await ctx.send("Không tìm thấy emoji trong guild.")
        else:
            await ctx.send("Tag crush vào để hun đi")

    @commands.command()
    async def xinso(self, ctx):
        guild = self.client.get_guild(1090136467541590066)
        emojis = await guild.fetch_emoji(1119613953014767676)
        number = random.randint(0, 99)
        embed = discord.Embed(
            title="", description=f"{emojis} Chào {ctx.author.mention}, tao là nhà tiên tri đến từ tương lai\nHôm nay tao sẽ cho mày số: **{number:02d}** {emojis}", color=discord.Color.from_rgb(242, 205, 255))
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/1106774950464983140/1208387766837317652/huanhoahong-1ugww-1603860149561719888008-1603873413854-16038734202391656232023.png?ex=65e319ce&is=65d0a4ce&hm=81ec06a86dde3fd428c4c8eee05b70781aa27ce3ae291f060c7bc5f80ca40cb4&")
        await ctx.send(embed=embed)

    @commands.command(name="pick", aliases=["p", "picks"])
    async def pick(self, ctx, *, keywords: str):
        # Tách các từ khoá bằng dấu ","
        keyword_list = keywords.split(',')
        # Loại bỏ khoảng trắng ở đầu và cuối mỗi từ khoá
        keyword_list = [keyword.strip() for keyword in keyword_list]
        # Kiểm tra xem có ít nhất 2 từ khoá để chọn lựa
        if len(keyword_list) < 2:
            await ctx.send("Nhập ít nhất 2 từ cách nhau bằng dấu ','")
            return
        # Chọn ngẫu nhiên một từ trong danh sách từ khoá
        chosen_keyword = random.choice(keyword_list)
        await ctx.send(f"__**{chosen_keyword}**__")

    @commands.command(aliases=['Tát'], description="Tát một người nào đó")
    async def tat(self, ctx, member: discord.Member):
        if member.bot:
            await ctx.send("Bot không thể bị tát")
            return
        if member == ctx.author:
            await ctx.send("Không thể tự tát")
            return
        damage = random.randint(1, 999)
        # List các hình ảnh để random
        images = ["https://media.discordapp.net/attachments/1053799649938505889/1424246866886918194/Angry_Slap_Sticker_by_SOWINGHONG.gif?ex=68e340c2&is=68e1ef42&hm=1225845b6962b16408d50c8b195cd4c2ab331ccb40c2a50bd43e5f29ecf981d0&=", 
                  "https://media.discordapp.net/attachments/1053799649938505889/1424246867646222439/Angry_War_Sticker_by_Shibuya_Station.gif?ex=68e340c2&is=68e1ef42&hm=1adeb585b23f993b97f759766a1fe5c829fe701eb8cc5af0ba24b12cdef409d4&=", 
                  "https://media.discordapp.net/attachments/1053799649938505889/1424246868094750761/Couple_Slapping_Sticker_by_Jin.gif?ex=68e340c2&is=68e1ef42&hm=854f49498cd6f7cef76459020191aa726d595ed285c0c51567320d776c8956bd&=",
                  "https://media.discordapp.net/attachments/1053799649938505889/1424246868438814761/Angry_Face_Sticker_by_Jin.gif?ex=68e340c2&is=68e1ef42&hm=e1a2fcd7370423d33cda5f2fc4eb19cc263ad68c1fca038da348f89f469fb1c4&=",
                  "https://media.discordapp.net/attachments/1053799649938505889/1424246868895862815/Angry_Chicken_Sticker.gif?ex=68e340c2&is=68e1ef42&hm=a9787043921f297ceb8a0f1e083d826a6904c7f26eafca98ed7c8c9df4f1bb73&=",
                  "https://media.discordapp.net/attachments/1053799649938505889/1424246869231538298/Comedy_Oops_Sticker_by_kwaesam.gif?ex=68e340c2&is=68e1ef42&hm=d15031e9aa43051616a78610da1933d778b811384b1638b5a1a2b70556e63016&=",
                  "https://media.discordapp.net/attachments/1053799649938505889/1424246869621473362/I_Hate_You_Twitch_Sticker.gif?ex=68e340c2&is=68e1ef42&hm=4e9c94f2b686468d973a2b155bd975f6c63cfc678051772181a96f9f76479841&=",
                  "https://media.discordapp.net/attachments/1053799649938505889/1424246869982187529/Slap_Hit_Sticker_by_Tonton_Friends.gif?ex=68e340c3&is=68e1ef43&hm=6b490fc5c8aab70da5a6744b239c3f4983dfdf5c0572a9f4e316e2726c54744f&="]  # Thay đổi link thật
        # Random một hình ảnh từ list
        image = random.choice(images)
        # Tạo embed
        embed = discord.Embed(title=f"{ctx.author.display_name} đã tát {member.display_name}!", description=f"Số lần: **{damage}** cái !!!", color=discord.Color.from_rgb(242, 205, 255))
        embed.set_thumbnail(url=image)
        # Gửi embed
        await ctx.send(embed=embed)


    @commands.command( description="Đắp mộ một người nào đó")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def rip(self, ctx, member: discord.Member):
        if member.bot:
            await ctx.send("🤖 Bot không thể bị RIP")
            return
        if member == ctx.author:
            await ctx.send("Bạn không thể tự RIP chính mình!")
            return

        # 1) Mở ảnh nền RIP
        try:
            base = Image.open(self.RIP_TEMPLATE).convert("RGBA")
        except FileNotFoundError:
            await ctx.send("❌ Không tìm thấy file rip.png")
            return

        # 2) Lấy URL avatar server nếu có
        avatar_url = None
        # discord.py 2.x: member.guild_avatar; 1.x: member.avatar_url_as()
        if hasattr(member, "guild_avatar") and member.guild_avatar:
            avatar_url = member.guild_avatar.url
        elif hasattr(member, "avatar_url") and member.avatar_url:
            avatar_url = str(member.avatar_url_as(format="png", size=256))
        elif hasattr(member, "avatar") and member.avatar:
            avatar_url = member.avatar.url

        # 3) Tải avatar hoặc load default
        avatar_bytes = None
        if avatar_url:
            async with aiohttp.ClientSession() as session:
                async with session.get(avatar_url) as resp:
                    if resp.status == 200:
                        avatar_bytes = await resp.read()
        if not avatar_bytes:
            # Dùng default_avatar.png
            try:
                with open(self.DEFAULT_AVATAR, "rb") as f:
                    avatar_bytes = f.read()
            except FileNotFoundError:
                await ctx.send("❌ Không tìm thấy file default_avatar.png")
                return
            
        # 4) Xử lý avatar: mở, resize, mask thành circle
        avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
        AVATAR_SIZE = (512, 512)  # Kích thước avatar

        # Chọn filter tương ứng với phiên bản Pillow
        try:
            resample_filter = Image.Resampling.LANCZOS
        except AttributeError:
            resample_filter = Image.LANCZOS

        avatar = avatar.resize(AVATAR_SIZE, resample=resample_filter)

        # Tạo mask circle
        mask = Image.new("L", AVATAR_SIZE, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, AVATAR_SIZE[0], AVATAR_SIZE[1]), fill=255)
        avatar.putalpha(mask)

        # 5) Xác định vị trí paste trên ảnh nền (điều chỉnh x,y theo template)
        position = (1100, 850)  # ví dụ: cách trái 125px, cách trên 200px

        base.paste(avatar, position, avatar)

        # 6) Xuất ra buffer và gửi về Discord
        buffer = io.BytesIO()
        base.save(buffer, format="PNG")
        buffer.seek(0)
        file = discord.File(fp=buffer, filename="rip_result.png")
        # Gửi file
        years = random.randint(1, 100)

        await ctx.send(f"{daulau} **{member.display_name}** đã bị chôn sống {years} năm {lich}", file=file)

async def setup(client):
    await client.add_cog(Fun(client))