import typing
import discord
from discord.ext import commands
import config

rolehost = config.ROLE_HOST


class Role(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.hybrid_command(name="role", description="Thêm role cho người trong giang hồ")
    async def role(self, ctx: discord.Interaction, member: discord.Member = None, *, role: discord.Role = None):
        if role.permissions.administrator:
            await ctx.reply("Bạn không thể thêm role cho role có quyền quản lý!")
        elif not (ctx.author.guild_permissions.administrator or any(role.name == rolehost for role in ctx.author.roles)):
            await ctx.reply("Bạn không có quyền để sử dụng lệnh này!")
        elif member is None or role is None:
            await ctx.reply("Vui lòng tag người và role!")
        else:
            await member.add_roles(role)
            embed = discord.Embed(
                description=f"Role {role.mention} đã được thêm cho {member.mention}", color=discord.Color.from_rgb(242, 205, 255))
            await ctx.send(embed=embed)

    @commands.hybrid_command(aliases=["rolecreate", "roleadd", "addrole"], description="Tạo role trong giang hồ")
    async def role_add(self, ctx: discord.Interaction, name: typing.Optional[str] = None, color: discord.Color = None):
        if not (ctx.author.guild_permissions.administrator or any(role.name == rolehost for role in ctx.author.roles)):
            await ctx.reply("Bạn không có quyền để sử dụng lệnh này!")
        elif name is None or color is None:
            await ctx.reply("Vui lòng cung cấp tên và màu cho role!")
        else:
            role = await ctx.guild.create_role(name=name, color=color)
            embed = discord.Embed(
                description=f"Role {role.mention} tạo thành công", color=color)
            await ctx.send(embed=embed)


    @commands.hybrid_command(aliases=["roledel","delrole"], description="Xóa role trong giang hồ")
    async def role_delete(self, ctx: discord.Interaction, *, role: discord.Role = None):
        if role.permissions.administrator:
            await ctx.reply("Bạn không thể xóa role có quyền quản lý!")
        elif not (ctx.author.guild_permissions.administrator or any(role.name == rolehost for role in ctx.author.roles)):
            await ctx.reply("Bạn không có quyền để sử dụng lệnh này!")
        elif role is None:
            await ctx.reply("Vui lòng tag role cần xóa!")
        else:
            await role.delete()
            embed = discord.Embed(
                description=f"Role {role.mention} đã được xóa!", color=discord.Color.from_rgb(242, 205, 255))
            await ctx.send(embed=embed)

    @commands.hybrid_command(aliases=["rmrole", "roleremove"], description="Xóa role của người trong giang hồ")
    async def role_remove(self, ctx: discord.Interaction, member: discord.Member = None, *, role: discord.Role = None):
        if role.permissions.administrator:
            await ctx.reply("Bạn không thể xóa role của role có quyền quản lý!")
        elif not (ctx.author.guild_permissions.administrator or any(role.name == rolehost for role in ctx.author.roles)):
            await ctx.reply("Bạn không có quyền để sử dụng lệnh này!")
        elif member is None or role is None:
            await ctx.reply("Vui lòng tag người và role cần xoá!")
        else:
            await member.remove_roles(role)
            embed = discord.Embed(
                description=f"Role {role.mention} đã gỡ khỏi {member.mention}", color=discord.Color.from_rgb(242, 205, 255))
            await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="roles", description="Xem role của người trong giang hồ")
    async def roles(self, ctx: discord.Interaction, member: discord.Member = None):
        if member is None:
            member = ctx.author
        else:
            roles = member.roles
            embed = discord.Embed(
                description=f"Role của {member.mention} là: {roles}", color=discord.Color.from_rgb(242, 205, 255))
            await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="rolelist", description="Xem danh sách role trong giang hồ")
    async def rolelist(self, ctx: discord.Interaction):
        roles = ctx.guild.roles
        embed = discord.Embed(
            description=f"Danh sách role trong giang hồ là: {roles}", color=discord.Color.from_rgb(242, 205, 255))
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="roleinfo", description="Hiển thị thông tin về một role")
    async def roleinfo(self, ctx: commands.Context, *, role: discord.Role = None):
        if role is None:
            await ctx.reply("Vui lòng tag role cần xem thông tin")
        else:
            members = [member.name for member in role.members]
            created_at = role.created_at.strftime("%d/%m/%Y %H:%M:%S")
            embed = discord.Embed(description=f"Thông tin role {role.mention}", color=role.color)
            embed.add_field(name="Ngày tạo", value=created_at, inline=False)
            embed.add_field(name="Số lượng thành viên", value=len(members), inline=False)
            embed.add_field(name="Danh sách thành viên", value="\n".join(members) if members else "Không có thành viên", inline=False)
            await ctx.send(embed=embed)

async def setup(client):
    await client.add_cog(Role(client))