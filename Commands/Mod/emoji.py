import asyncio
import discord
from discord.ext import commands
import requests

def is_guild_owner_or_bot_owner():
    async def predicate(ctx):
        guild_owner = ctx.author == ctx.guild.owner
        bot_owner = ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222
        specific_role = any(role.id == 1113463122515214427 for role in ctx.author.roles)

        return guild_owner or bot_owner or specific_role
    
    return commands.check(predicate)


class Emoji(commands.Cog):
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

    @commands.command(aliases=["phongtoemoji"], description="Phóng to emoji")
    async def emoji(self, ctx, emoji: discord.PartialEmoji = None):
        if await self.check_command_disabled(ctx):
            return
        if emoji is None:
            async for message in ctx.channel.history(limit=5):
                for reaction in message.reactions:
                    if isinstance(reaction.emoji, discord.PartialEmoji):
                        emoji = reaction.emoji
                        break
                if emoji:
                    break
            if not emoji:
                msg = await ctx.send("Không tìm thấy emoji nào gần đây trong kênh!")
                await asyncio.sleep(3)
                await msg.delete()
                return
        if not emoji.is_unicode_emoji() and not emoji.is_custom_emoji():
            msg1 = await ctx.send("Đây không phải là emoji hợp lệ!")
            await asyncio.sleep(3)
            await msg1.delete()
            return
        embed = discord.Embed(
            color=discord.Color.from_rgb(191, 62, 255), description=f"")
        if ctx.author.avatar:
            avatar_url = ctx.author.avatar.url
        else:
            avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"  
        embed.set_author(name=f"EMOJI PHÓNG TO", icon_url=avatar_url)
        embed.set_image(url=emoji.url)
        embed.add_field(name="", value=f"**EMOJI**: `{emoji.name}` `{emoji.id}`", inline=False)

        await ctx.send(embed=embed)
    
    @commands.command( description="cướp và thêm emoji")
    @is_guild_owner_or_bot_owner()
    async def cuopemoji(self, ctx, emoji: discord.PartialEmoji, ten_emoji: str):
        if await self.check_command_disabled(ctx):
            return
        if len(ten_emoji) > 32:
            msg = await ctx.send("Tên emoji quá dài!")
            await asyncio.sleep(3)
            await msg.delete()
            return
        try:
            response = requests.get(str(emoji.url))
            image_data = response.content
            await ctx.guild.create_custom_emoji(name=ten_emoji, image=image_data)
            await ctx.send(f'Đã cướp thành công emoji với tên `{ten_emoji}`.')
        except discord.Forbidden:
            await ctx.send('Bot không có quyền đủ để thêm emoji.')
    
    @cuopemoji.error
    async def cuopemoji_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            msg = await ctx.send("Vui lòng nhập đủ thông tin: `emoji` và `tên_emoji`!")
            await asyncio.sleep(3)
            await msg.delete()
            return
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Emoji không hợp lệ!")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send("Bot không có quyền đủ để thêm emoji.")
        else:
            await ctx.send(f"Đã có lỗi xảy ra: `{error}`")

async def setup(client):
    await client.add_cog(Emoji(client))