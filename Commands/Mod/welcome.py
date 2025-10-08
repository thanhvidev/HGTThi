import asyncio
import discord
from discord import File
from discord.ext import commands
from discord.utils import get
from easy_pil import Editor, load_image_async, Font
import sqlite3
import re
import random
from datetime import datetime
import pytz
from Commands.Mod.list_emoji import list_emoji, profile_emoji, sinhnhat_emoji

wlc0 = "<a:hgtt_sky:1212268235693621248>"
wlc1 = "<a:wlc1:1418464439182692442>"
wlc2 = "<:wlc2:1418464455670370405>"
wlc3 = "<:wlc3:1418464465921511554>"
wlc4 = "<:wcl4:1418464475526205544>"
wlc5 = "<a:wlc5:1418464487127777332>"
wlc6 = "<a:wlc6:1418464494874656909>"
wlc7 = "<:wlc7:1418464504018374708>"
wlc8 = "<a:wlc8:1418464514390757506>"
wlc9 = "<a:wlc9:1418464523182014485>"
wlc10 = "<:wlc10:1418464532157829150>"
wlc11 = "<a:wlc11:1418464544790937661>"
wlc12 = "<:wlc12:1418464553771073586>"
wlc13 = "<a:wlc13:1418464566202994769>"

sinhnhat = "<a:hgtt_sinhnhat:1058137898228138001>"

wlchgtt = "<a:hgtt_a:1058137898228137994>"
wlcH = "<a:chu_h:1215227436954812416>"
wlcG = "<a:chu_g:1215227494408523827>"
wlcT = "<a:chu_t:1215227539858128956>"
traitim = "<a:wlc1:1418464439182692442>"
wel_1 = '<a:wel_1:1358235882657808527>'
wel_2 = '<:wel_2:1358235933442441276>'
wel_3 = '<a:wel_3:1358235939972841654>'
wel_4 = '<a:phaohoahong:1358024352318357574>'
wel_5 = '<:wel_5:1358235947547885738>'
button33 = '<a:button33:1412534340285370489>'
button58 = '<a:button58:1412534176888000622>'
hearts = '<:hearts:1414235687989018695>'
button45 = '<a:button45:1412534253044105376>'
pc = '<a:pc:1414238570041970802>'

# Kết nối database
def get_economy_connection():
    """Kết nối đến database economy"""
    return sqlite3.connect('economy.db')

def is_registered_in_economy(user_id):
    """Kiểm tra user đã đăng ký trong bảng users (economy) chưa"""
    conn = get_economy_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def is_registered_in_profiles(user_id):
    """Kiểm tra user đã có profile chưa"""
    conn = get_economy_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM profiles WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def register_user_economy(user_id):
    """Đăng ký user trong bảng economy"""
    conn = get_economy_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, 200000))
    cursor.execute("UPDATE users SET captcha_attempts = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def register_user_profile(user_id):
    """Tạo profile cho user"""
    conn = get_economy_connection()
    cursor = conn.cursor()
    cursor.execute("""INSERT OR IGNORE INTO profiles 
                     (user_id, name, nickname, birthday, location, hobby, relationship_status, profile_image) 
                     VALUES (?, '', '', '', '', '', '', '')""", (user_id,))
    conn.commit()
    conn.close()

def ensure_user_exists(user_id):
    """Đảm bảo user tồn tại trong bảng users trước khi tạo profile"""
    conn = get_economy_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if not cursor.fetchone():
        # Tạo user mới trong bảng users với balance mặc định
        cursor.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, 200000))
        cursor.execute("UPDATE users SET captcha_attempts = 0 WHERE user_id = ?", (user_id,))
        conn.commit()
    conn.close()

class BirthdaySetModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Thiết lập sinh nhật", timeout=300)

    birthday = discord.ui.TextInput(
        label="Ngày sinh",
        placeholder="DD/MM/YYYY (ví dụ: 26/03/2000)",
        max_length=10,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        birthday_str = self.birthday.value.strip()
        
        # Validate birthday format
        try:
            birthday_date = datetime.strptime(birthday_str, "%d/%m/%Y")
            # Kiểm tra năm hợp lệ (từ 1900 đến năm hiện tại)
            current_year = datetime.now().year
            if birthday_date.year < 1900 or birthday_date.year > current_year:
                await interaction.response.send_message(
                    f"{list_emoji.tick_check} Năm sinh không hợp lệ! Vui lòng nhập năm từ 1900 đến {current_year}.", 
                    ephemeral=True
                )
                return
        except ValueError:
            await interaction.response.send_message(
                f"{list_emoji.tick_check} Định dạng không hợp lệ! Vui lòng nhập theo định dạng DD/MM/YYYY (ví dụ: 26/03/2000).", 
                ephemeral=True
            )
            return
        
        # Đảm bảo user tồn tại
        ensure_user_exists(user_id)
        
        # Cập nhật sinh nhật
        conn = get_economy_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE profiles SET birthday = ? WHERE user_id = ?", (birthday_str, user_id))
        conn.commit()
        conn.close()
        
        # Gửi tin nhắn thành công
        await interaction.response.send_message(
            f"{list_emoji.tickdung} Đã thiết lập sinh nhật của bạn: **{birthday_str}**!\n\n{sinhnhat_emoji.lich_sn} Hãy đến <#1417754513770680370> để xem thông tin sinh nhật chi tiết!", 
            ephemeral=True
        )

class WelcomeView(discord.ui.View):
    def __init__(self, member: discord.Member, enable_buttons=True, timeout: float = 600.0):
        super().__init__(timeout=timeout)
        self.member = member  # Người mới vào server
        self.enable_buttons = enable_buttons
        self.message = None  # Sẽ được gán sau khi gửi message
        self.clicked_users = set()  # Lưu trữ các user đã nhấn nút
        self.counter = 0

    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        if self.message:
            await self.message.edit(view=self)

    async def disable_buttons(self, duration: int):  
        self.welcome.disabled = True
        await self.message.edit(view=self)  
        await asyncio.sleep(duration)  
        self.welcome.disabled = False
        await self.message.edit(view=self)  

    async def on_timeout(self) -> None:
        await self.disable_all_items()
        return await super().on_timeout()

    @discord.ui.button(label="", style=discord.ButtonStyle.grey, emoji="<a:wlc8:1418464514390757506>", custom_id="welcome", disabled=False)
    async def welcome(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Kiểm tra nếu user đã nhấn rồi thì trả lời ephemeral và dừng
        if interaction.user.id in self.clicked_users:
            await interaction.response.send_message("Bạn đã nhấn rồi nè", ephemeral=True)
            return
        
        # Đánh dấu user đã nhấn
        self.clicked_users.add(interaction.user.id)

        # Danh sách emoji để random
        list_emoji_welcome = [
            wlc1, wlc2, wlc3, wlc4, wlc5, wlc6, wlc7, wlc8, wlc9, wlc10, wlc11, wlc12, wlc13, wel_1, wel_2, wel_3, wel_4, wel_5
        ]

        list_loichao = [
            "{emoji} **Chào người đẹp {member}**",
            "{emoji} **Helu {member}, mời bạn** https://discord.com/channels/832579380634451969/1024754536566505513",
            "{emoji} **Chào mừng {member} đến với bình nguyên vô tận**",
            "{emoji} **Chào mừng {member} đến với địa ngục trần gian**",
            "{emoji} **Chào mừng {member} đến với xứ sở thần tiên**",
        ]

        # Random emoji và câu chào
        random_emoji = random.choice(list_emoji_welcome)
        message_text = random.choice(list_loichao).format(
            emoji=random_emoji,
            user=interaction.user.mention,
            member=self.member.mention
        )

        await interaction.channel.send(message_text)
        
        # Tăng bộ đếm sau mỗi lần nhấn thành công
        self.counter += 1
        
        # Nếu đã nhấn 5 lần thì disable nút
        if self.counter >= 5:
            button.disabled = True
            if self.message:
                await self.message.edit(view=self)

    @discord.ui.button(label="", style=discord.ButtonStyle.grey, emoji="<a:tienhong:1416278321792290917>", custom_id="dangki", disabled=False)
    async def dangki(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        
        # Kiểm tra xem user đã đăng ký chưa
        if is_registered_in_economy(user_id):
            await interaction.response.send_message(f"{list_emoji.tick_check} Bạn đã đăng ký tài khoản rồi!", ephemeral=True)
            return
            
        try:
            # Đăng ký user trong bảng economy (users)
            register_user_economy(user_id)
            
            # Tạo profile cho user
            register_user_profile(user_id)
            
            # Fetch emoji đăng ký thành công
            guild = interaction.client.get_guild(1090136467541590066)
            if guild:
                try:
                    users_emoji = await guild.fetch_emoji(1181400074127945799)
                    success_message = f"{users_emoji} **| {interaction.user.display_name} đăng ký tài khoản thành công, bạn được tặng** __**200k**__ {list_emoji.pinkcoin}"
                except:
                    success_message = f"{list_emoji.tickdung} **| {interaction.user.display_name} đăng ký tài khoản thành công, bạn được tặng** __**200k**__ {list_emoji.pinkcoin}"
            else:
                success_message = f"{list_emoji.tickdung} **| {interaction.user.display_name} đăng ký tài khoản thành công, bạn được tặng** __**200k**__ {list_emoji.pinkcoin}"
                
            await interaction.response.send_message(success_message, ephemeral=False)
            
        except Exception as e:
            await interaction.response.send_message(f"{list_emoji.tick_check} Có lỗi xảy ra khi đăng ký: {str(e)}", ephemeral=True)

    @discord.ui.button(label="", style=discord.ButtonStyle.grey, emoji="<:profile:1181400074127945799>", custom_id="profile", disabled=False)
    async def profile(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Chuyển hướng đến channel profile
        channel_id = 1417748798515576842
        channel_mention = f"<#{channel_id}>"
        
        embed = discord.Embed(
            description=f"{profile_emoji.profile_card} **Hãy đến {channel_mention} để xem profile của bạn!**",
            color=discord.Color.from_rgb(255, 182, 224)
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="", style=discord.ButtonStyle.grey, emoji="<a:sinhnhat1:1418464576500138076>", custom_id="sinhnhat", disabled=False)
    async def sinhnhat(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        
        # Kiểm tra xem user đã đăng ký chưa
        if not is_registered_in_economy(user_id):
            embed = discord.Embed(
                description=f"{list_emoji.tick_check} **Bạn chưa đăng ký tài khoản!**\n\n{sinhnhat_emoji.lich_sn} Hãy bấm nút {list_emoji.pinkcoin} để đăng ký trước khi thiết lập sinh nhật.",
                color=discord.Color.from_rgb(255, 137, 250)
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        # Nếu đã đăng ký, hiển thị modal nhập sinh nhật
        modal = BirthdaySetModal()
        await interaction.response.send_modal(modal)

class Welcome(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id != 832579380634451969:
            return

        channel = self.client.get_channel(993153068378116127)
        # tạo embed
        embed = discord.Embed(
            description=(
                f"# ㅤㅤ{button33} 𝐇𝐆𝐓𝐓 𝐗𝐢𝐧 𝐂𝐡𝐚̀𝐨 {button33}\nㅤ\n"
                f"{button58} Để có một trải nghiệm tốt nhất tại sv, bạn vui lòng làm theo các bước sau để bật **hiện tất cả các kênh** nha\n\n"
                f"{pc} **Trên máy tính (PC)**\n"
                "- B1 :  Chuột phải vào tên sv 𝙝𝙖̣𝙩 𝙜𝙞𝙤̂́𝙣𝙜 𝙩𝙖̂𝙢 𝙩𝙝𝙖̂̀𝙣 ở trên cùng màn hình\n"
                "- B2 : Tick vào ô **hiện tất cả các kênh**\n\n\n"
                f"{hearts} **Trên điện thoại**\n"
                "- B1 : Bấm vào tên sv 𝙝𝙖̣𝙩 𝙜𝙞𝙤̂́𝙣𝙜 𝙩𝙖̂𝙢 𝙩𝙝𝙖̂̀𝙣 ở trên cùng màn hình\n"
                "- B2 : Kéo xuống và chọn mục **hiện tất cả các kênh**\n"
                "\n"
            ),
            color=discord.Color.from_rgb(245, 252, 255)
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1053799649938505889/1412703034764558356/image.png")

        # Tạo button link đến kênh 🗨️│nói-khùm-nói-điên
        channel = discord.utils.get(member.guild.text_channels, name="🗨️│nói-khùm-nói-điên")
        view = None
        if channel:
            button = discord.ui.Button(
                label=f"Bấm vào đây ",
                style=discord.ButtonStyle.link,
                url=f"https://discord.com/channels/{member.guild.id}/{channel.id}"
            )
            view = discord.ui.View()
            view.add_item(button)

        # thử gửi DM
        try:
            await member.send(embed=embed, view=view)
        except discord.Forbidden:
            print(f"[!] Không thể nhắn tin cho {member} (chặn DM).")
            return

        await asyncio.sleep(1)
        # await channel.send(f"# **{traitim} Hé lô {member.mention} nha**")
        view = WelcomeView(member=member)  # Truyền member vào
        message = await channel.send(content= f"# **{traitim} Xin chào {member.mention} nha**", view=view)
        view.message = message
        await view.wait()


    # @commands.Cog.listener()
    # async def on_member_join(self, member):
    #     channel = self.client.get_channel(993153068378116127)
    #     # Lấy các vai trò cần thêm bằng id
    #     role_ids = [1003769660291960912, 1183603041987997756, 1083663296827232306, 1083599160055431268, 1083599309091635240, 1083599263675727912]
    #     roles = [member.guild.get_role(role_id) for role_id in role_ids]
    #     await member.add_roles(*roles)
    #     pos = sum(m.joined_at < member.joined_at for m in member.guild.members if  m.joined_at is not None)
    #     if pos == 1:
    #         te = "st"
    #     elif pos == 2:
    #         te = "nd"
    #     elif pos == 3:
    #         te = "rd"
    #     else:
    #         te = "th"
    #     background = Editor("welcome.png")
    #     if member.avatar:
    #         profile_image = await load_image_async(str(member.avatar.url))
    #     else:
    #         profile_image = "default_avatar.png"

    #     profile = Editor(profile_image).resize((500, 500)).circle_image()  # Thay đổi kích thước profile thành 400x400
    #     poppins = Font.poppins(size=(100), variant=('bold'))
    #     poppins_small = Font.poppins(size=(80), variant=('bold'))

    #     # Tính toán vị trí cho paste profile
    #     background_image = background.image
    #     profile_image = profile.image

    #     background_size = background_image.size
    #     profile_size = profile_image.size

    #     profile_position = ((background_size[0] - profile_size[0]) // 2, 200)  # Nằm ở giữa ngang và cách trên một khoảng

    #     background.paste(profile, profile_position)
    #     background.ellipse(profile_position, 500, 500, outline="white", stroke_width=10)  # Sửa kích thước ellipse tương ứng

    #     text_position = (background_size[0] // 2, profile_position[1] + profile_size[1] + 20)  # Cách dưới profile một khoảng
    #     text_above = (background_size[0] // 2, profile_position[1] - 120) 

    #     background.text(text_above, f"WELCOME", color="#FFA5E7", font=poppins, align="center")
    #     background.text((text_position[0], text_position[1] + 20), f"{member.name}", color="white", font=poppins_small, align="center")
    #     background.text((text_position[0], text_position[1] + 120), f"♡ {pos}{te} ♡", color="#FF9966", font=poppins_small, align="center")

    #     file = File(fp=background.image_bytes, filename="welcome.png")

    #     await channel.send(f"**{wlc0} Ú oà, {member.mention} đã bị bắt cóc đến {wlcH}{wlcG}{wlcT}{wlcT}**\nㅤ\n**{wlc0} 1 là pick roles 2 là iu tao <#1024754536566505513>\nㅤ**",file=file)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # Kiểm tra nếu không phải máy chủ với id 832579380634451969 thì thoát
        if member.guild.id != 832579380634451969:
            return

        user_id = member.id
        conn = sqlite3.connect("economy.db")
        cursor = conn.cursor()

        cursor.execute("SELECT marry FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        if result is None:
            conn.close()
            return
        
        marry_info = result[0]
        
        if marry_info.strip() != "":
            pattern = r"<@(\d+)>\s+đã kết hôn với\s+<@(\d+)>"
            match = re.search(pattern, marry_info)
            if match:
                id1 = int(match.group(1))
                id2 = int(match.group(2))
                # Xác định đối tác: nếu thành viên rời đi là id1 thì partner là id2, ngược lại thì partner là id1
                if user_id == id1:
                    partner_id = id2
                elif user_id == id2:
                    partner_id = id1
                else:
                    partner_id = None
            else:
                partner_id = None

            # Xoá người dùng rời khỏi bảng
            cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            
            # Nếu tìm được partner_id, cập nhật lại dữ liệu của đối tác
            if partner_id:
                cursor.execute("""
                    UPDATE users 
                    SET marry = '', love_marry = 0, setup_marry1 = '', setup_marry2 = ''
                    WHERE user_id = ?
                """, (partner_id,))
        else:
            # Nếu không có thông tin hôn nhân, chỉ cần xoá người dùng khỏi bảng
            cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        
        conn.commit()

        channel = self.client.get_channel(1020298594441494538)
        pos = sum(m.joined_at < member.joined_at for m in member.guild.members if  m.joined_at is not None)
        if pos == 1:
            te = "st"
        elif pos == 2:
            te = "nd"
        elif pos == 3:
            te = "rd"
        else:
            te = "th"
        background = Editor("welcome.png")
        if member.avatar:
            profile_image = await load_image_async(str(member.avatar.url))
        else:
            profile_image = "default_avatar.png"

        profile = Editor(profile_image).resize((500, 500)).circle_image()  # Thay đổi kích thước profile thành 400x400
        poppins = Font.poppins(size=(100), variant=('bold'))
        poppins_small = Font.poppins(size=(80), variant=('bold'))

        # Tính toán vị trí cho paste profile
        background_image = background.image
        profile_image = profile.image

        background_size = background_image.size
        profile_size = profile_image.size

        profile_position = ((background_size[0] - profile_size[0]) // 2, 200)  # Nằm ở giữa ngang và cách trên một khoảng

        background.paste(profile, profile_position)
        background.ellipse(profile_position, 500, 500, outline="white", stroke_width=10)  # Sửa kích thước ellipse tương ứng

        text_position = (background_size[0] // 2, profile_position[1] + profile_size[1] + 20)  # Cách dưới profile một khoảng
        text_above = (background_size[0] // 2, profile_position[1] - 120) 

        background.text(text_above, f"GOODBYE", color="#FFA5E7", font=poppins, align="center")
        background.text((text_position[0], text_position[1] + 20), f"{member.name}", color="white", font=poppins_small, align="center")
        background.text((text_position[0], text_position[1] + 120), f"{pos}{te}", color="#FF9966", font=poppins_small, align="center")

        file = File(fp=background.image_bytes, filename="welcome.png")

        await channel.send(f"**{wlc0} Bye bye, {member.mention} đã cúc khỏi server**",file=file)

async def setup(client):
    await client.add_cog(Welcome(client))