import discord
from discord.ext import commands
import json
import os
from utils.checks import is_bot_owner, is_admin, is_mod


intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "donate_config.json"

# ===================== UTIL =====================
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def main_embed(guild: discord.Guild) -> discord.Embed:
    embed = discord.Embed(
        title="",
        description=(
            f"# {button23} 𝐆𝐈𝐕𝐄𝐀𝐖𝐀𝐘 𝐇𝐆𝐓𝐓 {button23}"
        ),
        color=discord.Color.from_rgb(245, 252, 255)
    )

    embed.add_field(
        name="",
        value=(
            f"{button58} **Xin chào, bạn chọn các mục bên dưới để tham khảo nha, "
            f"nếu có thắc mắc hãy hỏi để bọn mình tư vấn**\n\n"
            f"{button31} **Lưu ý**\n"
            "- Đổi ý không làm nữa vui lòng thông báo và đóng ticket\n"
            "- Tạo xong tag nhiều lần không rep = ban"
        ),
        inline=False
    )

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    embed.set_image(
        url="https://media.discordapp.net/attachments/1053799649938505889/1412701563863961610/Tutor_Group_Google_Classroom_Header_in_Colorful_Doodle_Style_1.png"
    )

    return embed


button23 = "<a:button23:1412534422565158962>"
button58 = '<a:button58:1412534176888000622>'
button31 = '<a:button31:1412534355418419221>'
button19 = '<a:button19:1412692811165466754>'
button34 = '<a:button34:1412534332823834644>'
button17 = '<a:button17:1412692823425286175>'
button32 = '<a:button32:1412534347621335100>'
button54 = '<a:button54:1412534200308859073>'
button39 = '<a:button39:1412534301710618645>'
button35 = '<a:button35:1412534327526297700>'
button33 = '<a:button33:1412534340285370489>'
button36 = '<a:button36:1412534318084919428>'
button15 = '<a:button15:1412692847332950088>'
button57 = '<a:button57:1412534181912772628>'
button16 = '<a:button16:1412692833210466356>'
button28 = '<a:button28:1412534386473177158>'
button38 = '<a:button38:1412534308039688273>'
button11 = '<a:button11:1412692891574468688>'
button45 = '<a:button45:1412534253044105376>'
banking  = '<a:banking:1414201407539515543>'
hgtt_tienowo = '<:hgtt_tienowo:1204791085327720448>'
hgtt_tien_vnd = '<:hgtt_tien_vnd:1235115910445142037>'
hgtt_muiten2hong = '<:hgtt_muiten2hong:1414203740562526299>'
hgtt_muiten3trang = '<:hgtt_muiten3trang:1414204805471277117>'

# ===================== SELECT MENU =====================
class GiveAway_OptionView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.select(
        placeholder="CHỌN MỤC Ở ĐÂY",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Sv đã partner", emoji=button19),
            discord.SelectOption(label="Sv chưa partner", emoji=button35),
            discord.SelectOption(label="Sv booking/shop", emoji=button33),
            discord.SelectOption(label="Mạng xã hội", emoji=button36),
            discord.SelectOption(label="Ga trong sv", emoji=button28),
            discord.SelectOption(label="Thanh toán", emoji=button38),
            discord.SelectOption(label="Quay về", emoji=button45),
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        # if interaction.user.id != self.user_id:
        #     return await interaction.response.send_message("❌ Bạn không có quyền chọn!", ephemeral=True)

        chosen = select.values[0]
        embed = discord.Embed(color=discord.Color.from_rgb(245, 252, 255))

        # ===================== OPTION CONTENT =====================
        if "Sv đã partner" in chosen:
            embed.description = (
                f"# {button19}  Sv đã partner"
            )
            embed.add_field(name="", value=
                f"{button34} **Nhận các ga : kéo vote, kéo mem, pr sự kiện**\n\n"
                f"{button17} **GA MIN 3M {hgtt_tienowo} | PHÍ 2M {hgtt_tienowo}**\n\n"
                f"{button32} __**Phí thời gian**__\n**12H {hgtt_muiten3trang} 1M | 24H {hgtt_muiten3trang} 2M | 48H {hgtt_muiten3trang} 4M**\n\n"
                f"{button54} **Quy đổi : 1M {hgtt_tienowo} = 10K {hgtt_tien_vnd}**\n\n"
                f"{button39} **Danh sách các sv đã pn :** https://discord.com/channels/832579380634451969/1094249961652228226", inline=False)
            embed.set_image(url="https://cdn.discordapp.com/attachments/1053799649938505889/1412702371791769701/image0-1-2.gif")
                
        elif "Sv chưa partner" in chosen:
            embed.description = (
                f"# {button35}  Sv chưa partner"
            )
            embed.add_field(name="", value=
                f"{button34} **Nhận các ga : kéo vote, kéo mem,...**\n\n"
                f"{button17} **GA MIN 5M {hgtt_tienowo} | PHÍ 3M {hgtt_tienowo}**\n\n"
                f"-# {hgtt_muiten2hong} sv dưới 2k mem\n"
                f"-# {hgtt_muiten2hong} sv k có nội dung cờ bạc, toxic, war, bll...\n\n"
                f"{button32} __**Phí thời gian**__ \n**12H {hgtt_muiten3trang} 1M | 24H {hgtt_muiten3trang} 2M | 48H {hgtt_muiten3trang} 4M**\n\n"
                f"{button54} **Quy đổi : 1M {hgtt_tienowo} = 10K {hgtt_tien_vnd}**", inline=False)
            embed.set_image(url="https://cdn.discordapp.com/attachments/1053799649938505889/1412702371791769701/image0-1-2.gif")

        elif "Sv booking/shop" in chosen:
            embed.description = (
                f"# {button33}  Sv booking/shop"
            )
            embed.add_field(name="", value=
                f"{button34} **Nhận các ga : kéo vote, kéo mem**\n\n"
                f"{button17} **GA MIN 50K {hgtt_tien_vnd} | PHÍ 30K {hgtt_tien_vnd}**\n\n"
                f"{button32} __**Phí thời gian**__ :\n**12H {hgtt_muiten3trang} 1M | 24H {hgtt_muiten3trang} 2M | 48H {hgtt_muiten3trang} 4M**\n\n"
                f"{button31} **Booking & shop chỉ nhận vnđ**", inline=False)
            embed.set_image(url="https://cdn.discordapp.com/attachments/1053799649938505889/1412702371791769701/image0-1-2.gif")

        elif "Mạng xã hội" in chosen:
            embed.description = (
                f"# {button36}  Mạng xã hội"
            )
            embed.add_field(name="", value=
                f"{button34} **Nhận các ga tương tác mạng xã hội {button15}{button57}{button16}**\n\n"
                f"{button17} **GA MIN 3M {hgtt_tienowo} | PHÍ 3M {hgtt_tienowo}**\n\n"
                f"{button32} __**Phí thời gian**__ \n**12H {hgtt_muiten3trang} 1M | 24H {hgtt_muiten3trang} 2M | 48H {hgtt_muiten3trang} 4M**\n\n"
                f"{button54} **Quy đổi : 1M {hgtt_tienowo} = 10K {hgtt_tien_vnd}**", inline=False)
            embed.set_image(url="https://cdn.discordapp.com/attachments/1053799649938505889/1412702371791769701/image0-1-2.gif")

        elif "Ga trong sv" in chosen:
            embed.description = (
                f"# {button28}  Ga trong sv"
            )
            embed.add_field(name="", value=
                f"{button34} **Ga noreq trên 500K**\n"
                f"{button34} **Ga : orep, opray, tag tên, chúc mừng...**\n\n"
                f"{button17} **GA MIN 2M {hgtt_tienowo} | 0 phí**\n\n"
                f"{button32} __**Phí thời gian**__ \n**12H {hgtt_muiten3trang} 1M | 24H {hgtt_muiten3trang} 2M | 48H {hgtt_muiten3trang} 4M**\n\n"
                f"{button54} **Quy đổi : 1M {hgtt_tienowo} = 10K {hgtt_tien_vnd}**", inline=False)
            embed.set_image(url="https://cdn.discordapp.com/attachments/1053799649938505889/1412702371791769701/image0-1-2.gif")

        elif "Thanh toán" in chosen:
            embed.description = (
                f"# {button38}  Thanh toán"
            )
            embed.add_field(name="", value=
                f"{banking} **`9357474513` Nguyen Hoai Thanh Vi**\n\n"
                f"{button11} **Bank xong bạn vui lòng gửi bill nhé**", inline=False)
            embed.set_image(url="https://cdn.discordapp.com/attachments/1053799649938505889/1412702371791769701/image0-1-2.gif")
            embed.set_image(url="https://media.discordapp.net/attachments/1053799649938505889/1412701565017657394/image.png")
        elif "Quay về" in chosen:
            embed = main_embed(interaction.guild)

        # embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else discord.Embed.Empty)
        # embed.set_image(url="https://cdn.discordapp.com/attachments/1053799649938505889/1412702371791769701/image0-1-2.gif")

        await interaction.response.edit_message(embed=embed, view=self)

class GiveAway_Option(commands.Cog):  
    def __init__(self, client):  
        self.client = client  

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)  
    # @is_mod()
    async def keovote(self, ctx):


        embed = main_embed(ctx.guild)
        view = GiveAway_OptionView(ctx.author.id)
        await ctx.send(embed=embed, view=view)


    @bot.group()
    async def setkeovote(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("❌ Hãy dùng: `zsetkeovote channel #kênh`")


    @setkeovote.command(name="channel")
    @is_bot_owner()
    async def setdonate_channel(self, ctx, channel: discord.TextChannel):
        data = load_data()
        data[str(ctx.guild.id)] = channel.id
        save_data(data)
        await ctx.send(f"✅ Kênh donate đã đặt là {channel.mention}")
