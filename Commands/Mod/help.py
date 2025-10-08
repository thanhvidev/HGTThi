import random
import discord
from discord.ext import commands
from Commands.Mod.list_emoji import list_emoji, lambanh_emoji, profile_emoji, sinhnhat_emoji
from utils.checks import is_bot_owner, is_admin, is_mod

vevang = "<:vevang:1192461054131847260>"
casino = "<:casino:1272143953709498400>"
nhankc = "<:nhanhop:1191617855356162088>"
giveaway = "<:gaqua:1272143979491758115>"
fun = "<a:fun:1272143969450594325>"
line = "<a:line1:1272147987035983963>"
fishcoin = "<:fishcoin:1213027788672737300>"
banhrang = "<:suacan:1213359207705743400>"
bc = "<a:hgtt_lac:1090551045823922240>"
tx = "<a:danglac:1090171480639275008>"
bot = "<:bxh:1272143014688456726>"
pinkcoin = "<:timcoin:1192458078294122526>"
owners = "<:hgtt_h_cong2:1056515709871607889>"
lich_hlw  = "<:lich_hlw:1295979007124439050>"
chamthando = "<:chamthando:1295979015957512214>"
bingo = "<:qua_kco:1331708141917966528>"
coin_xu = "<a:xu_love_2025:1339490786840150087>"
nhayxanh = "<a:nhayxanh:1314886457151983648>"
nhayvang = "<a:nhayvang:1329072503645274183>"
benphai = "<:phai_quest:1314667889525129286>"

def is_guild_owner_or_bot_owner():
    async def predicate(ctx):
        return ctx.author == ctx.guild.owner or ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222
    return commands.check(predicate)

class Help(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.client.remove_command("help")
        # self.client.loop.create_task(self.setup())
        self.responses = [
            "Có vấn đề gì mà tag mình vậy bạn?",
            "Tag lần nữa là chết moẹ m với t",
            "Tag tao ăn lon à?",
            "Lo ăn cơm đi, tag cc",
            "Những đứa ế thường hay tag tao",
            "Em đang bận, đừng tag nữa",
            "Tag lần nữa là bắn sì sọ",
            "Tag cc, đang ngủ rồi",
            # Thêm các câu trả lời khác tại đây
        ]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.mentions:
            return

        if self.client.user in message.mentions and not message.reference:
            response = random.choice(self.responses)
            await message.reply(response)

    @commands.hybrid_command(description="Xem các lệnh của bot")
    async def help(self, ctx):
        embed = discord.Embed(title=f"{list_emoji.ngoisaohelp}**HƯỚNG DẪN DÙNG BOT**{list_emoji.ngoisaohelp}", description=f"ㅤ\n{list_emoji.quabicuop} **Hello {ctx.author.mention}**\nㅤ\n{list_emoji.quabicuop} **Mình là bot HGTT - được phát triển bởi <@1006945140901937222>, <@962627128204075039> và được sử dụng duy nhất tại sv Hạt Giống Tâm Thần**\nㅤ\n{list_emoji.quabicuop} **Dưới đây là danh mục hướng dẫn chi tiết dành cho bạn**",
                              color=discord.Color.from_rgb(255,255,255))
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1211199649667616768/1339640608515424328/discord_fake_avatar_decorations_1739289265966.gif")
        # embed.set_image(url="https://cdn.discordapp.com/attachments/1211199649667616768/1330469545114075197/discord_fake_avatar_decorations_1737278405998.gif")
        # if ctx.author.avatar:
        #     avatar_url = ctx.author.avatar.url
        # else:
        #     avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
        # embed.set_author(name=f"𝗛𝗲𝗹𝗽 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀", icon_url=avatar_url)
        # embed.set_footer(text="Chọn một trong các lựa chọn để xem chi tiết lệnh") 
        user_id = ctx.author.id  
        help = HelpSelectMenu(enable_buttons=user_id)
        view = HelpView(help)
        await ctx.send(embed=embed, view=view)

class HelpSelectMenu(discord.ui.Select):
    def __init__(self, enable_buttons):
        self.enable_buttons = enable_buttons
        options=[
                    discord.SelectOption(label='𝐄𝐯𝐞𝐧𝐭 𝐓𝐫𝐮𝐧𝐠 𝐓𝐡𝐮', value='valentine',emoji= list_emoji.xu_event),
                    discord.SelectOption(label='Vé Vàng', value='vemauvang',emoji= vevang),
                    discord.SelectOption(label='Casino', value='tien',emoji= casino),
                    discord.SelectOption(label='Giải Trí', value='fun', emoji= fun),
                    discord.SelectOption(label='Marry', value='marry',emoji= nhankc),
                    discord.SelectOption(label='Giveaway', value='giveaway',emoji= giveaway),
                    discord.SelectOption(label='Moderation', value='moderation', emoji= banhrang),
                    discord.SelectOption(label='Owner', value='owner', emoji= owners),
                ]
        super().__init__(placeholder='Chọn Trợ Giúp', options=options)

    async def interaction_check(self, interaction: discord.Interaction) ->  bool:
        if interaction.user.id == self.enable_buttons:
            return True
        else:
            await interaction.response.send_message("BXH này do người khác mở", ephemeral=True)
            return False

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == 'valentine':
            embed = discord.Embed(title="",description=f"**{list_emoji.xu_event} Hướng dẫn tham gia 𝐄𝐯𝐞𝐧𝐭 𝐓𝐫𝐮𝐧𝐠 𝐓𝐡𝐮 {list_emoji.xu_event}**", color=discord.Color.from_rgb(242, 226, 6))
            embed.add_field(name=f"",
                            value=f"- **`zdk`** | đăng ký\n- **`zcash`** | check tiền - vé - xu\n- [**`zdaily`**](<https://discord.com/channels/832579380634451969/1147355133622108262>) | điểm danh - nhận xu vào 14h mỗi ngày\n- [**`zq`**](<https://discord.com/channels/832579380634451969/1147355133622108262>) | làm nhiệm vụ - kiếm xu {pinkcoin}{list_emoji.xu_event}\n- [**`zlambanh`**](<https://discord.com/channels/832579380634451969/1147355133622108262>) | kiếm nguyên liệu làm bánh {lambanh_emoji.banhtrungthu}\n- [**`zquay`**](<https://discord.com/channels/832579380634451969/1295144686536888340>) | dùng {list_emoji.xu_event} quay lồng đèn", inline=False)
            embed.set_image(url="https://cdn.discordapp.com/attachments/1414911120791048242/1416318153075724338/discord_fake_avatar_decorations_1757743534578.gif")
            await interaction.response.edit_message(embed=embed)

        elif self.values[0] == 'vemauvang':
            embed = discord.Embed(title="",description=f"# **{vevang} Lệnh vé vàng {vevang}**", color=discord.Color.gold())
            embed.add_field(name=f"",
                            value=f"- **`zdk  `** : đăng ký tài khoản\n- **`zcash`** : kiểm tra vé & tiền\n- **`zmoqua`** : mở vé \n- **`zinv `** : kiểm tra kho sự kiện\n- **`ztop `** : xem bảng xếp hạng vé & tiền", inline=False)
            embed.set_image(url="https://media.discordapp.net/attachments/1211199649667616768/1274631413202948096/CutlineOnlyCD.png")
            await interaction.response.edit_message(embed=embed)

        elif self.values[0] == 'tien':
            embed = discord.Embed(title="",description=f"# **{casino} Lệnh cờ bạc {casino}**", color=discord.Color.from_rgb(242, 205, 255))
            embed.add_field(name=f"",
                            value=f"- **`zbj + số tiền hoặc all`** : chơi bài xì zách\n- **`zcf + số tiền hoặc all + sấp hoặc ngửa`** : chơi lật đồng xu\n- **`zslot + số tiền hoặc all`** : tìm 3 slot giống nhau\n- **`zbc + số tiền hoặc all + tên con `** : chơi bầu cua\n- **`ztx + số tiền hoặc all + tên cửa`** : chơi tài xỉu\n- **`zbet`** : 50K, mỗi ngày mua được 1 vé và quay 1 giải", inline=False)
            embed.set_image(url="https://media.discordapp.net/attachments/1211199649667616768/1274631413202948096/CutlineOnlyCD.png")
            await interaction.response.edit_message(embed=embed)

        elif self.values[0] == 'fun':
            embed = discord.Embed(title="",description=f"# **{fun} Lệnh giải trí {fun}**", color=discord.Color.from_rgb(242, 205, 255))
            embed.add_field(name=f"",
                            value=f"- **`ztoan`** : làm toán -  20K {pinkcoin}/ 1 câu đúng\n- **`zdhbc`** : nhìn emoji đoán chữ - 20K {pinkcoin} / 1 câu đúng\n- **`zvtv` **  : chơi ghép chữ - 100K {pinkcoin}/ 1 câu đúng\n- **`zwork`** : thăm ngàn - kẹp ngân ( 1 - 10K {pinkcoin})\n- **`zkbb + @user`** : chơi oẳn tù tì\n- **`zpray`** : thắp nhang cầu nguyện\n- **`zxinso`** :  xin số đánh con lô\n- **`ztat + @user`** : tát người mình ghét\n- **`zhun + @user`** : hun người mình thích\n- **`zkhen + @user`** : khen người khác", inline=False)
            embed.set_image(url="https://media.discordapp.net/attachments/1211199649667616768/1274631413202948096/CutlineOnlyCD.png")
            await interaction.response.edit_message(embed=embed)

        elif self.values[0] == 'marry':
            embed = discord.Embed(title="",description=f"# **{nhankc} Lệnh marry {nhankc}**", color=discord.Color.from_rgb(242, 205, 255))
            embed.add_field(name=f"",
                            value=f"- **`zshop`** : xem nhẫn\n- **`zbuy + ID`** : mua nhẫn\n- **`zmarry + @user + ID nhẫn`** : cầu hôn\n- **`zmarry`** : xem giấy kết hôn\n- **`zlove`** : cày điểm thân mật\n- **`zqua + ID quà`**: tặng quà cho người iu\n- **`zdivorce`** : ly hôn\n- **`zsetmarry`** : tạo hình và trạng thái", inline=False)
            embed.set_image(url="https://media.discordapp.net/attachments/1211199649667616768/1274631413202948096/CutlineOnlyCD.png")
            await interaction.response.edit_message(embed=embed)

        elif self.values[0] == 'giveaway':
            embed = discord.Embed(title="",description=f"# **{giveaway} Lệnh giveaway {giveaway}**", color=discord.Color.from_rgb(242, 205, 255))
            embed.add_field(name=f"",
                            value=f"- **`zga`** : làm giveaway\n- **`zrr`** : reroll giveaway\n- **`zend`** : kết thúc giveaway", inline=False)
            embed.set_image(url="https://media.discordapp.net/attachments/1211199649667616768/1274631413202948096/CutlineOnlyCD.png")
            await interaction.response.edit_message(embed=embed)

        elif self.values[0] == 'moderation':
            embed = discord.Embed(title="",description=f"**{banhrang} MODERATION {banhrang}**", color=discord.Color.from_rgb(242, 205, 255))
            embed.add_field(name=f"",
                            value=f"- **`znick`** : tag người dùng và đổi tên\n- **`zreponse`** : tag người dùng và tạo phản hồi\n- **`zreaction`** : tag người dùng và tạo phản hồi\n- **`zxoareact`** or **`zxoarepon`** : tag người dùng và xoá phản hồi hoặc phản ứng\n- **`zcuopemoji`** : nhập emoji và tên emoji\n- **`zloto`** : chơi lô tô\n- **`zrsloto`** : reset lại trò chơi\n- **`zds`** : xem danh sách số đã kêu", inline=False)
            embed.set_image(url="https://media.discordapp.net/attachments/1211199649667616768/1274631413202948096/CutlineOnlyCD.png")
            embed.set_footer(text="Lệnh này chỉ dành cho role >= STAFF")
            await interaction.response.edit_message(embed=embed)
        elif self.values[0] == 'owner':  
            user = interaction.user
            guild_owner_id = interaction.guild.owner_id
            bot_owner_id = 928879945000833095  # Replace with the actual bot owner's ID.

            # Check if the user is either the guild owner or the bot owner
            if user.id == guild_owner_id or user.id == bot_owner_id:
                embed = discord.Embed(title="", description=f"# **{owners} SETUP BOT {owners}**", color=discord.Color.from_rgb(242, 205, 255))  
                embed.add_field(name="", value=f"- **zsettien + số + @user** : tiền hồng\n- **zve + @user** : tặng vé vàng\n- **zsetve + @user + loại + số** : set vé kc or vàng\n- **zsetlove** : set điểm love\n- **zsetxuvlt** : set xu valentine\n- **zsetdiemvlt** : set điểm valentine\n- **zsettongve + @user** : set tổng vé vàng nhận được\n- **zsetxu + số + @user** : set xu nhiệm vụ\n- **zrsdaily + ** : reset vé ngày\n- **zrsquest** : reset nhiệm vụ ngày\n- **zrsve** : reset tất cả\n- **zrslevel** : reset voice\n- **zrsdaily** : reset vé hằng ngày\n- **zrsxu** : reset xu event\n- **zrstien** : reset pinkcoin\n- **zremind + id kênh + msg** : nhắc nhở\n- **zxoaremind + id kênh** : xoá nhắc nhở\n- **ztile** : tỉ lệ ra vé\n- **ztilequa** : tỉ lệ ra quà\n- **zsend** : gửi tới mọi người\n- **znhapdulieu** : cập nhật database", inline=False)  
                embed.set_image(url="https://media.discordapp.net/attachments/1211199649667616768/1274631413202948096/CutlineOnlyCD.png")  
                await interaction.response.edit_message(embed=embed)  
            else:  
                await interaction.response.send_message("Bạn không có quyền xem lệnh này.", ephemeral=True)

        else:  
            await interaction.response.send_message("Lỗi")  

class HelpView(discord.ui.View):
    def __init__(self, helpselectmenu: discord.ui.Select):
        super().__init__(timeout=180)
        self.add_item(helpselectmenu)

async def setup(client):
    await client.add_cog(Help(client))