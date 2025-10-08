import discord
from discord.ext import commands

class Snipe(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.sniped_messages = {}

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        attachments = message.attachments
        if attachments:
            attachment = attachments[0]
            self.sniped_messages[message.channel.id] = (message.content, message.author, message.created_at, attachment.url)
        elif message.stickers:
            sticker = message.stickers[0]
            self.sniped_messages[message.channel.id] = (None, message.author, message.created_at, sticker.url)
        else:
            self.sniped_messages[message.channel.id] = (message.content, message.author, message.created_at, None)

    @commands.hybrid_command(name="snipe")
    async def snipe(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        try:
            contents, author, time, image_url = self.sniped_messages[channel.id]
        except KeyError:
            await ctx.channel.send("Không tìm thấy tin nhắn để snipe trên kênh này!")
            return

        embed = discord.Embed(description=contents,
                              color=discord.Color.from_rgb(242, 205, 255), timestamp=time)
        if ctx.author.avatar:
            avatar_url = ctx.author.avatar.url
        else:
            avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
        embed.set_author(
            name=f"{author.name}#{author.discriminator}", icon_url=avatar_url)
        embed.set_footer(text=f"Đã xóa trong: #{channel.name}")

        if image_url:
            embed.set_image(url=image_url)

        await ctx.channel.send(embed=embed)

async def setup(client):
    await client.add_cog(Snipe(client))