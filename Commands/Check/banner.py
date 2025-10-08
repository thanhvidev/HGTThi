import re
import discord
from discord.ext import commands
import datetime
import pytz
import sqlite3

mayanh = "<:camera:1339291110127702098>"

def is_guild_owner_or_bot_owner():
    async def predicate(ctx):
        return ctx.author == ctx.guild.owner or ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222
    return commands.check(predicate)

class Banner(commands.Cog):
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

    @commands.hybrid_command(aliases=["bn", "bnr"], description="Kiểm tra banner của người trong giang hồ")
    async def banner(self, ctx, member: discord.Member = None):
        if await self.check_command_disabled(ctx):
            return
        if member is None:
            member = ctx.author

        # Lấy thông tin user đầy đủ (để truy cập banner cá nhân)
        user = await self.client.fetch_user(member.id)
        personal_banner = user.banner  # Banner cá nhân (global)
        # Lấy banner của máy chủ nếu có (sử dụng getattr để tránh lỗi nếu không tồn tại)
        guild_banner = getattr(member, "guild_banner", None)

        timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        current_time = datetime.datetime.now(timezone)

        if personal_banner and guild_banner:
            embed = discord.Embed(
                title="",
                description=f"{mayanh} **Ảnh nển** {member.mention}",
                color=discord.Color.from_rgb(242, 205, 255),
                timestamp=current_time
            )
            embed.set_image(url=personal_banner.url)
            embed.set_thumbnail(url=guild_banner.url)
            embed.set_footer(text=f"Người thực hiện: {ctx.author.name}")
            await ctx.send(embed=embed)
        elif personal_banner:
            embed = discord.Embed(
                title="",
                description=f"{mayanh} **Ảnh nển Cá Nhân** {member.mention}",
                color=discord.Color.from_rgb(242, 205, 255),
                timestamp=current_time
            )
            embed.set_image(url=personal_banner.url)
            embed.set_footer(text=f"Người thực hiện: {ctx.author.name}")
            await ctx.send(embed=embed)
        elif guild_banner:
            embed = discord.Embed(
                title="",
                description=f"{mayanh} **Ảnh nển Máy Chủ** {member.mention}",
                color=discord.Color.from_rgb(242, 205, 255),
                timestamp=current_time
            )
            embed.set_image(url=guild_banner.url)
            embed.set_footer(text=f"Người thực hiện: {ctx.author.name}")
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                description=f"{member} không có ảnh nển.",
                color=discord.Color.from_rgb(242, 205, 255)
            )
            await ctx.send(embed=embed)


    @commands.command(name="check_mr")
    @is_guild_owner_or_bot_owner()
    async def check_mr(self, ctx):
        guild = ctx.guild
        conn = sqlite3.connect("economy.db")
        cursor = conn.cursor()

        # Lấy tất cả các hàng có cột 'marry' không rỗng
        cursor.execute("SELECT user_id, marry FROM users WHERE marry <> ''")
        rows = cursor.fetchall()
        pattern = r"<@(\d+)>\s+đã kết hôn với\s+<@(\d+)>"

        processed_pairs = set()
        messages = []

        for row in rows:
            db_user_id, marry_info = row
            if not marry_info.strip():
                continue

            match = re.search(pattern, marry_info)
            if not match:
                continue

            id1 = int(match.group(1))
            id2 = int(match.group(2))
            # Đảm bảo xử lý mỗi cặp một lần
            pair = tuple(sorted((id1, id2)))
            if pair in processed_pairs:
                continue
            processed_pairs.add(pair)

            # Kiểm tra thành viên có còn trong server hay không
            member1 = guild.get_member(id1)
            member2 = guild.get_member(id2)

            if member1 is None and member2 is not None:
                cursor.execute("DELETE FROM users WHERE user_id = ?", (id1,))
                cursor.execute("""
                    UPDATE users 
                    SET marry = '', love_marry = 0, setup_marry1 = '', setup_marry2 = ''
                    WHERE user_id = ?
                """, (id2,))
                messages.append(f"Đã xoá dữ liệu của thành viên ID `{id1}` (không còn trong server) và cập nhật thông tin của ID `{id2}`.")
            # Nếu member2 không có nhưng member1 còn, cập nhật member1 và xoá member2
            elif member2 is None and member1 is not None:
                cursor.execute("DELETE FROM users WHERE user_id = ?", (id2,))
                cursor.execute("""
                    UPDATE users 
                    SET marry = '', love_marry = 0, setup_marry1 = '', setup_marry2 = ''
                    WHERE user_id = ?
                """, (id1,))
                messages.append(f"Đã xoá dữ liệu của thành viên ID `{id2}` (không còn trong server) và cập nhật thông tin của ID `{id1}`.")
            # Nếu cả hai thành viên không còn trong server, xoá dữ liệu của cả hai
            elif member1 is None and member2 is None:
                cursor.execute("DELETE FROM users WHERE user_id IN (?, ?)", (id1, id2))
                messages.append(f"Đã xoá dữ liệu của cả hai thành viên ID `{id1}` và `{id2}` (không còn trong server).")
            else:
                # Cả hai thành viên vẫn còn trong server
                messages.append(f"Cả hai thành viên ID `{id1}` và `{id2}` đều còn trong server. Không có thay đổi.")

        conn.commit()

        content = "\n".join(messages)
        if len(content) > 2000:
            for i in range(0, len(content), 2000):
                await ctx.send(content[i:i+2000])
        else:
            await ctx.send(content)


        cursor.close()
        conn.close()

async def setup(client):
    await client.add_cog(Banner(client))