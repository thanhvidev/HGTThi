import asyncio
import random
import typing
import discord
from discord.ext import commands
import config
from utils.checks import is_bot_owner, is_admin, is_mod

rolehost = config.ROLE_HOST
boost = "<a:boost:1304725346767081503>"
phaohoa = "<a:phaohoahong:1358024352318357574>"
tick = "<:tick_xanhduong:1358024340653740072>"
nhay ="<a:nhayvang_loto:1421745142909374514>"

class Say(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.channel_id_concho = 1239563133094334504
        self.channel_id_line = 1360360505717297270

    @commands.hybrid_command(name="say", description="Trao lời yêu thương")
    async def say(self, ctx, *, msg: typing.Optional[str] = None):
        if not (ctx.author.guild_permissions.administrator or any(role.name == rolehost for role in ctx.author.roles)):
            await ctx.send("Bạn không có tuổi để sử dụng lệnh này!")
        elif msg is None:
            await ctx.send("Bạn chưa nhập nội dung!")
        else:
            await ctx.channel.send(msg)

    @commands.command(description="Đổi biệt danh")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def nick(self, ctx, member_or_new_nickname=None, *, new_nickname=None):
        if member_or_new_nickname is None:
            msg1 = await ctx.send("Bạn chưa nhập biệt danh!")
            await asyncio.sleep(2)
            await msg1.delete()
            return

        if isinstance(member_or_new_nickname, str) and member_or_new_nickname.startswith("<@") and member_or_new_nickname.endswith(">"):
            member_or_new_nickname = ctx.message.mentions[0]
            staff_roles = [1113463122515214427, 1042332372730921030]
            if any(role.id in staff_roles for role in ctx.author.roles):
                if new_nickname is None:
                    msg = await ctx.send("Bạn chưa nhập biệt danh mới!")
                    await asyncio.sleep(2)
                    await msg.delete()
                    return
                if len(new_nickname) <= 32:
                    await member_or_new_nickname.edit(nick=new_nickname)
                    await ctx.send(f'{tick} Đã đổi biệt danh của {member_or_new_nickname.display_name} thành `{new_nickname}`.')
                else:
                    msg = await ctx.send("Biệt danh mới quá dài. Vui lòng giảm độ dài xuống 32 ký tự.")
                    await asyncio.sleep(2)
                    await msg.delete()
            else:
                message2 = await ctx.send('Cần role `STAFF` để sử dụng lệnh này!')
                await asyncio.sleep(2)
                await message2.delete()
        else:
            required_roles = [1113463122515214427, 1021383533178134620, 1053284883956510805, 1193388434660806767, 1055758414678069308,
                              1055519421424222208, 1055759097133277204, 1082887622311022603, 1056244443184906361, 1146330846874312805, 1146332331150413844]
            if any(role.id in required_roles for role in ctx.author.roles):
                if new_nickname is None:
                    new_nickname = f"{member_or_new_nickname}"
                else:
                    new_nickname = f"{member_or_new_nickname} {new_nickname}"
                if len(new_nickname) <= 32:
                    await ctx.author.edit(nick=new_nickname)
                    await ctx.send(f'{tick} Đã đổi biệt danh của bạn thành `{new_nickname}`.')
                else:
                    msg = await ctx.send("Biệt danh mới quá dài. Vui lòng giảm độ dài xuống 32 ký tự.")
                    await asyncio.sleep(3)
                    await msg.delete()
            else:
                message1 = await ctx.reply(f'{phaohoa} **Hãy** __**boost**__ **sv hoặc** __**ủng hộ**__ **tại** https://discord.com/channels/832579380634451969/1072536912562241546 **để sử dụng chức năng này!**')
                # await asyncio.sleep(10)
                # await message1.delete()

    @nick.error
    async def nick_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = await ctx.send(f"Bạn còn `{error.retry_after:.0f}s` nữa mới có thể sử dụng lệnh này!")
            await asyncio.sleep(2)
            await msg.delete()
        elif isinstance(error, commands.MissingPermissions):
            msg = await ctx.send("Bot không đủ quyền để thay đổi biệt danh.")
            await asyncio.sleep(2)
            await msg.delete()
        else:
            raise error

    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     if message.author.bot:
    #         return
    #     if message.channel.id == 1156906752953024592 and ("done" in message.content or "Done" in message.content or "xong" in message.content or "Xong" in message.content or "DONE" in message.content or "XONG" in message.content) :
    #         await asyncio.sleep(600)
    #         await message.delete()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if "con chó" in message.content.strip().lower():
            channel_id = self.client.get_channel(self.channel_id_concho)
            if channel_id and channel_id.id not in [1210296290026455140, 1210417888272318525]:
                channel = channel_id
                images = []
                async for msg in channel.history(limit=200):
                    images.append(msg)
                # Lấy URL của hình ảnh
                image_urls = [
                    msg.attachments[0].url for msg in images if msg.attachments]
                if image_urls:
                    random_image_url = random.choice(
                        image_urls)  # Chọn ngẫu nhiên một URL
                    # Gửi URL hình ảnh ngẫu nhiên
                    await message.channel.send(random_image_url)
                else:
                    # Nếu không có hình ảnh
                    await message.channel.send("Không tìm thấy hình ảnh.")
            else:
                # Nếu không tìm thấy kênh hoặc ID kênh không phù hợp
                await message.channel.send("Không thể tìm thấy kênh hoặc không thực hiện do ID kênh.")

        if len(message.content.split()) == 1:
            word1 = message.content.strip().lower()
            if word1 == "line":
                channel = self.client.get_channel(self.channel_id_line)
                if channel:
                    images = []
                    async for msg in channel.history(limit=200):
                        images.append(msg)
                    image_urls = [msg.attachments[0].url for msg in images if msg.attachments]  # Lấy URL của hình ảnh
                    if image_urls:
                        random_image_url = random.choice(image_urls)  # Chọn ngẫu nhiên một URL
                        await message.channel.send(random_image_url)  # Gửi URL hình ảnh ngẫu nhiên
                    else:
                        await message.channel.send("Không tìm thấy hình ảnh.")  # Nếu không có hình ảnh
                else:
                    await message.channel.send("Không thể tìm thấy kênh.")  # Nếu không tìm thấy kênh
        if len(message.content.split()) == 1:
            word = message.content.strip().lower()  # Chuyển đổi thành chữ thường và loại bỏ các khoảng trắng đầu cuối
            if word in ["line", "kẻ", "gạch"]:
                await asyncio.sleep(2)
                await message.delete()
        if len(message.content.split()) == 1:
            word2 = message.content.strip().lower()
            if word2 == "ga":
                embed = discord.Embed(title="", description =f"{nhay} <@&1311874053786566688> **x2**\n\n{nhay} <@&1021383533178134620> **x3**", color=discord.Color.from_rgb(242, 205, 255))
                embed.set_footer(
                    text="𝑯𝒂̣𝒕 𝒈𝒊𝒐̂́𝒏𝒈 𝒕𝒂̂𝒎 𝒕𝒉𝒂̂̀𝒏",
                    icon_url=message.guild.icon.url if message.guild and message.guild.icon else None
                )
                await message.channel.send(embed=embed)

async def setup(client):
    await client.add_cog(Say(client))