import random
import discord
from discord.ext import commands
import config
import datetime
# import sqlite3

# conn = sqlite3.connect('warns.db')
# c = conn.cursor()

# # Tạo bảng để lưu trữ thông tin cảnh cáo
# c.execute('''CREATE TABLE IF NOT EXISTS warns
#              (id INTEGER PRIMARY KEY, moderator_name TEXT, member_name TEXT, member_id INTEGER, reason TEXT, timestamp TEXT)''')
# conn.commit()

rolehost = config.ROLE_HOST
log_channels = config.LOG_CHANNEL

khen1 = "<:zkhen1:1278647063411818558>"
khen2 = "<a:zkhen2:1278647072949538848>"
ban1 = "<:zban1:1278656705298960438>"
ban2 = "<:zban2:1278656714769694852>"

class Moderation(commands.Cog):
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

    @commands.command(name="kickbot")
    @commands.is_owner()
    async def kickbot(self, ctx, server_id: int):
        server = self.client.get_guild(server_id)
        if server:
            # Gửi tin nhắn trước khi rời khỏi server
            message = ("Mình là bot HGTT - được phát triển bởi <@1006945140901937222>, "
                       "<@962627128204075039> và được sử dụng duy nhất tại sv Hạt Giống Tâm Thần")
            await server.text_channels[0].send(message)
            
            await server.leave()
            await ctx.send(f"Bot đã rời khỏi server: {server.name}")
        else:
            await ctx.send("Không tìm thấy server với ID này.")

    @commands.hybrid_command(description="khen thành viên")
    async def khen(self, ctx: discord.Interaction, member: discord.Member = None, *, reason=None):
        if await self.check_command_disabled(ctx):
            return
        if member is None:
            await ctx.reply("> Tag người cần khen + lý do(nếu có)")
        else:
            embed1 = discord.Embed(title="",description=f"{khen1} **{member.mention}** {khen1}\nㅤ\n{khen2} ***{member.mention} được khen vì : {reason}***", color=discord.Color.from_rgb(255, 255, 153))
            if member.avatar:
                avatar_url = member.avatar.url
            else:
                avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"  # Sử dụng avatar mặc định
            embed1.set_thumbnail(url=avatar_url)
            await ctx.channel.send(embed=embed1)

    @commands.hybrid_command(name="xoa", description="Xóa thật nhiều tin nhắn")
    async def xoa(self, ctx: discord.Interaction, amount=0, option=None, member: discord.Member=None):
        if await self.check_command_disabled(ctx):
            return
        if not (ctx.author.guild_permissions.administrator or any(role.name == rolehost for role in ctx.author.roles)):
            await ctx.reply("Bạn cần role `STAFF` để sử dụng lệnh này!")
        else:
            pinned_messages = [msg async for msg in ctx.channel.history(limit=None) if msg.pinned]
            if option == "bot":
                check = lambda msg: msg.author.bot and msg.id not in [msg.id for msg in pinned_messages]
            elif option == "member" and member:
                check = lambda msg: msg.author == member and msg.id not in [msg.id for msg in pinned_messages]
            else:
                check = lambda msg: msg.id not in [msg.id for msg in pinned_messages]

            # Tính thời gian tối đa để xoá
            max_days = 30
            date_limit = datetime.datetime.utcnow() - datetime.timedelta(days=max_days)

            def check_date(msg):
                return msg.created_at > date_limit

            # Kết hợp cả hai điều kiện check và check_date
            final_check = lambda msg: check(msg) and check_date(msg)

            await ctx.channel.purge(limit=amount+1, check=final_check)
            await ctx.channel.send(f"Đã xóa {amount} tin nhắn", delete_after=5)

    @commands.hybrid_command(name="ban", description="ban giả")
    async def ban(self, ctx: discord.Interaction, member: discord.Member = None, *, reason=None):
        if await self.check_command_disabled(ctx):
            return
        sonam = random.randint(1, 50)
        if member is None:
            await ctx.reply("> Tag người cần fkban + lý do(nếu có)")
        else:
            embed1 = discord.Embed(title=f"{ban1} **TOÀ TUYÊN ÁN** {ban1}",description=f"{ban2} **Bị cáo {member.mention} bị phạt đi tù** __**{sonam} năm**__ **vì tội  danh** : **{reason}**", color=discord.Color.from_rgb(255, 0, 0))
            embed1.set_thumbnail(url="https://cdn.discordapp.com/attachments/1053799649938505889/1278656090409664573/11426588.png")
            await ctx.channel.send(embed=embed1)      

    @commands.hybrid_command(name="mute", description="mute giả")
    async def mute(self, ctx: discord.Interaction, member: discord.Member = None, *, reason=None):
        if await self.check_command_disabled(ctx):
            return
        guild = self.client.get_guild(1090136467541590066)
        emojis = await guild.fetch_emoji(1105941866022719508)
        if not (ctx.author.guild_permissions.administrator or any(role.name == rolehost for role in ctx.author.roles)):
            await ctx.reply("> Bạn không có tuổi để sử dụng lệnh này!")
        elif member is None:
            await ctx.reply("> Tag người cần fkmute + lý do(nếu có)")
        else:
            embed1 = discord.Embed(title="",description=f"**{member.mention}** **đã bị khoá mõm** {emojis} || **{reason}**", color=discord.Color.from_rgb(242, 205, 255))
            await ctx.channel.send(embed=embed1)
    
    @commands.hybrid_command(name="kick",  description="kick giả")
    async def kick(self, ctx: discord.Interaction, member: discord.Member = None, *, reason=None):
        if await self.check_command_disabled(ctx):
            return
        guild = self.client.get_guild(1090136467541590066)
        emojis = await guild.fetch_emoji(1105941866022719508)
        if not (ctx.author.guild_permissions.administrator or any(role.name == rolehost for role in ctx.author.roles)):
            await ctx.reply("> Bạn không có tuổi để sử dụng lệnh này!")
        elif member is None:
            await ctx.reply("> Tag người cần fkkick + lý do(nếu có)")
        else:
            embed1 = discord.Embed(title="",description=f"**{member.mention}** **đã bị kick** {emojis} || **{reason}**", color=discord.Color.from_rgb(242, 205, 255))
            await ctx.channel.send(embed=embed1)
    
    @commands.hybrid_command(name="warn",  description="warn giả")
    async def warn(self, ctx: discord.Interaction, member: discord.Member = None, *, reason=None):
        if await self.check_command_disabled(ctx):
            return
        guild = self.client.get_guild(1090136467541590066)
        emojis = await guild.fetch_emoji(1105941866022719508)
        if not (ctx.author.guild_permissions.administrator or any(role.name == rolehost for role in ctx.author.roles)):
            await ctx.reply("> Bạn không có tuổi để sử dụng lệnh này!")
        elif member is None:
            await ctx.reply("> Tag người cần fkwarn + lý do(nếu có)")
        else:
            embed1 = discord.Embed(title="",description=f"**{member.mention}** **đã bị cảnh cáo** {emojis} || **{reason}**", color=discord.Color.from_rgb(242, 205, 255))
            await ctx.channel.send(embed=embed1)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == 1285969498058522668:
                # Xoá tin nhắn ngay lập tức
                await message.delete()
                
    # @commands.hybrid_command(name="kick", description="Đá người ra khỏi máy chủ")
    # async def kick(self, ctx: discord.Interaction, member: discord.Member = None, *, reason=None):
    #     if not (ctx.author.guild_permissions.administrator or any(role.id in [role1, role2, role3, role4] for role in ctx.author.roles)):
    #         await ctx.reply("> Bạn không có tuổi để sử dụng lệnh này!")
    #     elif member is None:
    #         await ctx.reply("> Tag người cần kick + lý do(nếu có)")
    #     else:
    #         await member.kick(reason=reason)
    #         log_channel = ctx.guild.get_channel(log_channels)
    #         embed = discord.Embed(title="", color=discord.Color.from_rgb(242, 205, 255))
    #         embed .add_field(name="Loại bỏ:", value=f"{member.mention} đã bị loại khỏi giang hồ.", inline=False)
    #         embed.add_field(name="Lý do:", value=reason,inline=False)
    #         embed.set_footer(icon_url=ctx.author.avatar.url,
    #                 text=f"{ctx.author.name}ㅤㅤ")
    #         embed.timestamp = datetime.datetime.utcnow()
    #         embed1 = discord.Embed(title="",description=f"**{member.name}** đã bị loại khỏi giang hồ || {reason}", color=discord.Color.from_rgb(242, 205, 255))
    #         await ctx.channel.send(embed=embed1)
    #         await log_channel.send(embed=embed)

    # @commands.hybrid_command(name="ban", description="Cấm người dùng truy cập vào máy chủ")
    # async def ban(self, ctx: discord.Interaction, member: discord.Member = None, *, reason=None):
    #     if not (ctx.author.guild_permissions.administrator or 
    #     ctx.author.top_role.id == role1 or ctx.author.top_role.id == role2 or ctx.author.top_role.id == role3 or ctx.author.top_role.id == role4):
    #         await ctx.reply("> Bạn không có tuổi để sử dụng lệnh này!")
    #     elif member is None:
    #         await ctx.reply("> Tag người cần ban + lý do(nếu có)")
    #     else:
    #         await ctx.guild.ban(member)
    #         log_channel = ctx.guild.get_channel(log_channels)
    #         embed = discord.Embed(title="", color=discord.Color.from_rgb(242, 205, 255))
    #         embed .add_field(name="Cấm:", value=f"{member.mention} đã bị cấm truy cập vào giang hồ.", inline=False)
    #         embed.add_field(name="Lý do:", value=reason,inline=False)
    #         embed.set_footer(icon_url=ctx.author.avatar.url,
    #                 text=f"{ctx.author.name}ㅤㅤ")
    #         embed.timestamp = datetime.datetime.utcnow()
    #         embed1 = discord.Embed(title="",description=f"**{member.name}** đã bị cấm truy cập vào giang hồ || {reason}", color=discord.Color.from_rgb(242, 205, 255))
    #         await ctx.channel.send(embed=embed1)
    #         await log_channel.send(embed=embed)
    
    # @commands.hybrid_command(name="unban", description="Bỏ cấm người dùng truy cập vào máy chủ")
    # @commands.guild_only()
    # async def unban(self, ctx, *, member = None):
    #     if not (ctx.author.guild_permissions.administrator or 
    #     ctx.author.top_role.id == role1 or ctx.author.top_role.id == role2 or ctx.author.top_role.id == role3 or ctx.author.top_role.id == role4):
    #         await ctx.reply("> Bạn không có tuổi để sử dụng lệnh này!")
    #     elif member is None:
    #         await ctx.reply("> ID người cần unban")
    #     else:
    #         user = discord.Object(id=member)       
    #         await ctx.guild.unban(user)
    #         log_channel = ctx.guild.get_channel(log_channels)
    #         embed = discord.Embed(title="", color=discord.Color.from_rgb(242, 205, 255))
    #         embed .add_field(name="Bỏ cấm:", value=f"<@{member}> đã được bỏ cấm truy cập vào giang hồ.", inline=False)
    #         embed.set_footer(icon_url=ctx.author.avatar.url,
    #                 text=f"{ctx.author.name}ㅤㅤ")
    #         embed.timestamp = datetime.datetime.utcnow()
    #         embed1 = discord.Embed(title="",description=f"**<@{member}>** đã được bỏ cấm truy cập vào giang hồ", color=discord.Color.from_rgb(242, 205, 255))
    #         await ctx.channel.send(embed=embed1)
    #         await log_channel.send(embed=embed)
                    
    # @commands.hybrid_command(name="mute", description="Cấm người dùng nói chuyện trong máy chủ")
    # async def mute(self, ctx: discord.Interaction, member: discord.Member = None, *, reason=None):
    #     if not (ctx.author.guild_permissions.administrator or 
    #     ctx.author.top_role.id == role1 or ctx.author.top_role.id == role2 or ctx.author.top_role.id == role3 or ctx.author.top_role.id == role4):
    #         await ctx.reply("> Bạn không có tuổi để sử dụng lệnh này!")
    #     elif member is None:
    #         await ctx.reply("> Tag người cần mute + lý do(nếu có)")
    #     else:
    #         role = discord.utils.get(ctx.guild.roles, name="Muted")
    #         await member.add_roles(role)
    #         log_channel = ctx.guild.get_channel(log_channels)
    #         embed = discord.Embed(title="", color=discord.Color.from_rgb(242, 205, 255))
    #         embed .add_field(name="Cấm nói chuyện:", value=f"{member.mention} đã bị cấm nói chuyện trong giang hồ.", inline=False)
    #         embed.add_field(name="Lý do:", value=reason,inline=False)
    #         embed.set_footer(icon_url=ctx.author.avatar.url,
    #                 text=f"{ctx.author.name}ㅤㅤ")
    #         embed.timestamp = datetime.datetime.utcnow()
    #         embed1 = discord.Embed(title="",description=f"**{member.name}** đã bị cấm nói chuyện trong giang hồ || {reason}", color=discord.Color.from_rgb(242, 205, 255))
    #         await ctx.channel.send(embed=embed1)
    #         await log_channel.send(embed=embed)
    
    # @commands.hybrid_command(name="unmute", description="Bỏ cấm người dùng nói chuyện trong máy chủ")
    # async def unmute(self, ctx: discord.Interaction, member: discord.Member = None):
    #     if not (ctx.author.guild_permissions.administrator or 
    #     ctx.author.top_role.id == role1 or ctx.author.top_role.id == role2 or ctx.author.top_role.id == role3 or ctx.author.top_role.id == role4):
    #         await ctx.reply("> Bạn không có tuổi để sử dụng lệnh này!")
    #     elif member is None:
    #         await ctx.reply("> Tag người cần unmute")
    #     else:
    #         role = discord.utils.get(ctx.guild.roles, name="Muted")
    #         await member.remove_roles(role)
    #         log_channel = ctx.guild.get_channel(log_channels)
    #         embed = discord.Embed(title="", color=discord.Color.from_rgb(242, 205, 255))
    #         embed .add_field(name="Bỏ cấm nói chuyện:", value=f"{member.mention} đã được bỏ cấm nói chuyện trong giang hồ.", inline=False)
    #         embed.set_footer(icon_url=ctx.author.avatar.url,
    #                 text=f"{ctx.author.name}ㅤㅤ")
    #         embed.timestamp = datetime.datetime.utcnow()
    #         embed1 = discord.Embed(title="",description=f"**{member.name}** đã được bỏ cấm nói chuyện trong giang hồ", color=discord.Color.from_rgb(242, 205, 255))
    #         await ctx.channel.send(embed=embed1)
    #         await log_channel.send(embed=embed)

    # @commands.hybrid_command(name="warn", description="Cảnh cáo người dùng")
    # async def warn(self, ctx: discord.Interaction, member: discord.Member = None, *, reason=None):
    #     if not (ctx.author.guild_permissions.administrator or any(role.id in [role1, role2, role3, role4] for role in ctx.author.roles)):
    #         await ctx.reply("> Bạn không có tuổi để sử dụng lệnh này!")
    #     elif member is None:
    #         await ctx.reply("> Tag người cần cảnh cáo + lý do(nếu có)")
    #     else:
    #         log_channel = ctx.guild.get_channel(log_channels)
    #         embed = discord.Embed(title="", color=discord.Color.from_rgb(242, 205, 255))
    #         embed .add_field(name="Cảnh cáo:", value=f"{member.mention} đã bị cảnh cáo.", inline=False)
    #         embed.add_field(name="Lý do:", value=reason,inline=False)
    #         embed.set_footer(icon_url=ctx.author.avatar.url,
    #                 text=f"{ctx.author.name}ㅤㅤ")
    #         embed.timestamp = datetime.datetime.utcnow()
    #         embed1 = discord.Embed(title="",description=f"**{member.name}** đã bị cảnh cáo || {reason}", color=discord.Color.from_rgb(242, 205, 255))
    #         await ctx.channel.send(embed=embed1)
    #         await log_channel.send(embed=embed)

    #         # Thêm thông tin cảnh cáo vào cơ sở dữ liệu
    #         c.execute("INSERT INTO warns (id, moderator_name, member_name, member_id, reason, timestamp) VALUES (NULL, ?, ?, ?, ?, ?)", (ctx.author.name, member.name, member.id, reason, datetime.datetime.utcnow()))
    #         conn.commit()

    # @commands.hybrid_command(name="warns", description="Xem cảnh cáo của member")
    # async def warns(self, ctx: discord.Interaction, member: discord.Member = None):
    #     if not (ctx.author.guild_permissions.administrator or any(role.id in [role1, role2, role3, role4] for role in ctx.author.roles)):
    #         await ctx.reply("> Bạn không có tuổi để sử dụng lệnh này!")
    #     elif member is None:
    #         await ctx.reply("> Tag người cần xem cảnh cáo")
    #     else:
    #         # Thực hiện truy vấn SELECT
    #         c.execute("SELECT * FROM warns WHERE member_id = ?", (member.id,))
    #         rows = c.fetchall()
    #         if len(rows) == 0:
    #             embed = discord.Embed(title="",description=f"**{member.name}** không có cảnh cáo nào", color=discord.Color.from_rgb(242, 205, 255))
    #             await ctx.channel.send(embed=embed)
    #         else:
    #             embed = discord.Embed(title=f"Danh sách cảnh cáo của {member.name}", color=discord.Color.from_rgb(242, 205, 255))
    #             for row in rows:
    #                 embed.add_field(name=f"{row[0]} • `{row[2]}` cảnh cáo bởi `{row[1]}` vào lúc {row[5]}", value=f"Lý do: {row[4]}", inline=False)
    #             await ctx.channel.send(embed=embed)
    
    # @commands.hybrid_command(name="unwarn", description="Xóa danh sách cảnh cáo")
    # async def unwarn(self, ctx: discord.Interaction, member: discord.Member = None):
    #     if not (ctx.author.guild_permissions.administrator or any(role.id in [role1, role2, role3, role4] for role in ctx.author.roles)):
    #         await ctx.reply("Bạn không có tuổi để sử dụng lệnh này!")
    #     elif member is None:
    #         await ctx.reply("Tag người cần xóa cảnh cáo")
    #     else:
    #         # Thực hiện truy vấn DELETE
    #         c.execute("DELETE FROM warns WHERE member_id = ?", (member.id,))
    #         conn.commit()
    #         log_channel = ctx.guild.get_channel(log_channels)
    #         embed = discord.Embed(title="",description=f"**{member.name}** đã được xóa danh sách cảnh cáo", color=discord.Color.from_rgb(242, 205, 255))
    #         embed1 = discord.Embed(title="",description=f"**{member.name}** đã được xóa danh sách cảnh cáo", color=discord.Color.from_rgb(242, 205, 255))
    #         embed1.set_footer(icon_url=ctx.author.avatar.url,
    #                 text=f"{ctx.author.name}ㅤㅤ")
    #         embed1.timestamp = datetime.datetime.utcnow()
    #         await ctx.channel.send(embed=embed)
    #         await log_channel.send(embed=embed1)

    # @commands.hybrid_command(name="warning", description="lấy danh sách tất cả cảnh báo")
    # async def warning(self, ctx: discord.Interaction):
    #     if not (ctx.author.guild_permissions.administrator or any(role.id in [role1, role2, role3, role4] for role in ctx.author.roles)):
    #         await ctx.reply("Bạn không có tuổi để sử dụng lệnh này!")
    #     else:
    #         # Thực hiện truy vấn SELECT
    #         c.execute("SELECT * FROM warns")
    #         rows = c.fetchall()
    #         if len(rows) == 0:
    #             embed = discord.Embed(title="",description=f"Không có cảnh cáo nào", color=discord.Color.from_rgb(242, 205, 255))
    #             await ctx.channel.send(embed=embed)
    #         else:
    #             embed = discord.Embed(title=f"Danh sách cảnh cáo", color=discord.Color.from_rgb(242, 205, 255))
    #             for row in rows:
    #                 embed.add_field(name=f"{row[0]} • `{row[2]}` cảnh cáo bởi `{row[1]}` vào lúc {row[5]}", value=f"Lý do: {row[4]}", inline=False)
    #             await ctx.channel.send(embed=embed)


async def setup(client):
    await client.add_cog(Moderation(client))