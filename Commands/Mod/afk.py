import discord
from discord.ext import commands
import json


class AFK(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.afk_users = set()

    @commands.hybrid_command(name="afk", aliases=["Afk", "AFK"], description="Đặt chế độ AFK")
    async def afk(self, ctx, *, reason=None):
        with open('afk.json', 'r') as f:
            afk = json.load(f)
        afk[str(ctx.author.id)] = {
            "reason": reason,
            "guild_id": ctx.guild.id
        }
        with open('afk.json', 'w') as f:
            json.dump(afk, f, indent=4)
        self.afk_users.add(ctx.author.id)
        if ctx.author == ctx.guild.owner:
            await ctx.reply("Bạn không thể thay đổi biệt danh cho chủ server.")
        else:
            original_name = ctx.author.display_name
            await ctx.author.edit(nick="[AFK] " + original_name)
        if reason:
            await ctx.send(f"{ctx.author.mention} đã đặt chế độ AFK với lý do: {reason}")
        else:
            await ctx.send(f"{ctx.author.mention} đã đặt chế độ AFK")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.mentions:
            for user in message.mentions:
                with open('afk.json', 'r') as f:
                    afk = json.load(f)
                if str(user.id) in afk:
                    afk_data = afk[str(user.id)]
                    if afk_data["guild_id"] == message.guild.id:
                        embed = discord.Embed(
                            description=f"**{user.display_name}** đang AFK với lý do: **{afk_data['reason']}**",
                            color=discord.Color.from_rgb(242, 205, 255))
                        await message.channel.send(embed=embed)
        else:
            with open('afk.json', 'r') as f:
                afk = json.load(f)
            if str(message.author.id) in afk:
                afk_data = afk[str(message.author.id)]
                if message.author.id in self.afk_users:
                    self.afk_users.remove(message.author.id)
                else:
                    if afk_data["guild_id"] == message.guild.id:
                        if message.author.id == message.guild.owner_id:
                            afk.pop(str(message.author.id))
                            with open('afk.json', 'w') as f:
                                json.dump(afk, f, indent=4)
                            embed = discord.Embed(
                                description=f"**{message.author.display_name}** đã hủy chế độ AFK",
                                color=discord.Color.from_rgb(242, 205, 255))
                            await message.channel.send(embed=embed)
                        else:
                            original_name = message.author.display_name.split("[AFK] ")[1]
                            embed = discord.Embed(
                                description=f"**{original_name}** đã hủy chế độ AFK",
                                color=discord.Color.from_rgb(242, 205, 255))
                            await message.channel.send(embed=embed)
                            afk.pop(str(message.author.id))
                            with open('afk.json', 'w') as f:
                                json.dump(afk, f, indent=4)
                            await message.author.edit(nick=original_name)
            else:
                return
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        with open('afk.json', 'r') as f:
            afk = json.load(f)
        if str(member.id) in afk:
            afk.pop(str(member.id))
            with open('afk.json', 'w') as f:
                json.dump(afk, f, indent=4)


