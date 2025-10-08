import asyncio
import discord
import sqlite3
import re
from discord.ext import commands
from Commands.Mod.list_emoji import list_emoji, profile_emoji
from utils.checks import is_bot_owner, is_admin, is_mod
import json
from datetime import datetime
import pytz

def is_valid_url(url):
    """Kiểm tra URL có hợp lệ cho Discord embed không"""
    if not url or not url.strip():
        return False
    url = url.strip()
    
    # Sửa một số lỗi URL phổ biến
    if url.startswith('https://cdn.dishttps//'):
        url = url.replace('https://cdn.dishttps//', 'https://cdn.discordapp.com/')
    if url.startswith('http://cdn.dishttps//'):
        url = url.replace('http://cdn.dishttps//', 'https://cdn.discordapp.com/')
    
    # Kiểm tra cơ bản
    if not (url.startswith(('http://', 'https://')) and len(url) > 10):
        return False
    
    # Kiểm tra các ký tự không hợp lệ
    invalid_chars = ['\n', '\r', '\t', '"', "'", '`', ' ']
    if any(char in url for char in invalid_chars):
        return False
    
    # Kiểm tra độ dài hợp lý
    if len(url) > 2000:  # Discord URL limit
        return False
        
    # Kiểm tra format URL cơ bản
    import re
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'  # domain...
        r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # host...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))

# Kết nối và tạo bảng trong SQLite
conn = sqlite3.connect('economy.db', isolation_level=None)
conn.execute('pragma journal_mode=wal')
cursor = conn.cursor()

# Tạo bảng profiles riêng với foreign key liên kết đến users
cursor.execute('''CREATE TABLE IF NOT EXISTS profiles (
    user_id INTEGER PRIMARY KEY,
    name TEXT DEFAULT '',
    nickname TEXT DEFAULT '',
    birthday TEXT DEFAULT '',
    location TEXT DEFAULT '',
    hobby TEXT DEFAULT '',
    relationship_status TEXT DEFAULT '',
    profile_image TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
)''')
conn.commit()

def ensure_user_exists(user_id):
    """Đảm bảo user tồn tại trong bảng users trước khi tạo profile"""
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if not cursor.fetchone():
        # Tạo user mới trong bảng users với balance mặc định
        cursor.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, 0))
        conn.commit()

def migrate_users_to_profiles():
    """Migrate toàn bộ user_id từ bảng users sang bảng profiles"""
    try:
        # Lấy tất cả user_id từ bảng users
        cursor.execute("SELECT DISTINCT user_id FROM users")
        all_users = cursor.fetchall()
        
        migrated_count = 0
        for (user_id,) in all_users:
            # Kiểm tra xem user đã có trong profiles chưa
            cursor.execute("SELECT user_id FROM profiles WHERE user_id = ?", (user_id,))
            if not cursor.fetchone():
                # Tạo profile rỗng cho user
                cursor.execute('''INSERT INTO profiles (user_id, created_at, updated_at) 
                                 VALUES (?, ?, ?)''', 
                              (user_id, datetime.now(), datetime.now()))
                migrated_count += 1
        
        conn.commit()
        print(f"{list_emoji.tickdung} Migration hoàn tất: {migrated_count} users được thêm vào bảng profiles")
        return migrated_count
        
    except Exception as e:
        print(f"Lỗi migration: {e}")
        return 0

# Thực hiện migration khi khởi động
migration_count = migrate_users_to_profiles()

class ProfileModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Cập nhật thông tin cá nhân", timeout=300)

    name = discord.ui.TextInput(
        label="Tên",
        placeholder="Nhập tên của bạn (tối đa 20 ký tự)",
        max_length=20,
        required=False
    )
    
    nickname = discord.ui.TextInput(
        label="Biệt danh", 
        placeholder="Nhập biệt danh của bạn (tối đa 20 ký tự)",
        max_length=20,
        required=False
    )
    
    birthday = discord.ui.TextInput(
        label="Ngày sinh",
        placeholder="DD/MM/YYYY (ví dụ: 26/03/2000)",
        max_length=10,
        required=False
    )
    
    location = discord.ui.TextInput(
        label="Nơi ở",
        placeholder="Nhập nơi ở của bạn (tối đa 20 ký tự)",
        max_length=20,
        required=False
    )
    
    hobby = discord.ui.TextInput(
        label="Sở thích",
        placeholder="Nhập sở thích của bạn (tối đa 50 ký tự)",
        max_length=50,
        required=False,
        style=discord.TextStyle.paragraph
    )

    async def update_profile_embed(self, interaction):
        """Cập nhật embed profile sau khi chỉnh sửa"""
        user_id = interaction.user.id
        target_user = interaction.user
        
        # Lấy thông tin profile mới từ database
        cursor.execute('''SELECT p.name, p.nickname, p.birthday, p.location, p.hobby, 
                                p.relationship_status, p.profile_image, u.marry
                         FROM profiles p
                         LEFT JOIN users u ON p.user_id = u.user_id
                         WHERE p.user_id = ?''', (user_id,))
        profile = cursor.fetchone()
        
        # Nếu không có profile, lấy thông tin marry từ users
        if not profile:
            cursor.execute("SELECT marry FROM users WHERE user_id = ?", (user_id,))
            user_data = cursor.fetchone()
            marry_data = user_data[0] if user_data else None
            profile = (None, None, None, None, None, None, None, marry_data)
        
        # Tạo embed mới
        embed = discord.Embed(title=f"", description=f"# {profile_emoji.profile_card} BIO CARD {profile_emoji.profile_card}", color=0xFFB2E0)
        # embed.add_field(name=f"{profile_emoji.profile_card} PROFILE CARD {profile_emoji.profile_card}", value="", inline=False)
        embed.set_thumbnail(url=target_user.display_avatar.url)
        
        # Thông tin cơ bản
        profile_text = f"{profile_emoji.nhay7mau} Acc: {target_user.mention}\n"
        
        if profile and profile[0] is not None:  # Có profile data
            profile_text += f"{profile_emoji.nhay7mau} Tên: **{profile[0] or 'ㅤ'}**\n"            
            profile_text += f"{profile_emoji.nhay7mau} Biệt danh: **{profile[1] or 'ㅤ'}**\n" 
            profile_text += f"{profile_emoji.nhay7mau} Ngày sinh: **{profile[2] or 'ㅤ'}**\n"
            profile_text += f"{profile_emoji.nhay7mau} Nơi ở: **{profile[3] or 'ㅤ'}**\n"
            profile_text += f"{profile_emoji.nhay7mau} Sở thích: **{profile[4] or 'ㅤ'}**\n"

            # Xử lý mối quan hệ
            relationship_text = ""
            if profile[7] and profile[7].strip():  # marry field từ users có dữ liệu
                # Parse dữ liệu marry như trong marry.py
                import re
                marry_status = profile[7]
                matches = re.findall(r'<@(\d+)>', marry_status)
                name_match = re.search(r'(?<=bằng\s)[^<]+', marry_status)
                emoji_match = re.search(r'(<a?:\w+:\d+>)', marry_status)
                date_match = re.search(r'Ngày kết hôn:  (\d{2}/\d{2}/\d{4})', marry_status)
                
                if len(matches) >= 2 and name_match and emoji_match and date_match:
                    # Xác định partner (user khác với target_user)
                    partner_id = int(matches[0]) if int(matches[0]) != target_user.id else int(matches[1])
                    partner = interaction.client.get_user(partner_id)
                    ring_name = name_match.group().strip()
                    emoji = emoji_match.group(0)
                    wedding_date = date_match.group(1)
                    
                    # Tính số ngày đã kết hôn
                    try:
                        wedding_datetime = datetime.strptime(wedding_date, "%d/%m/%Y")
                        current_datetime = datetime.now()
                        days_married = (current_datetime - wedding_datetime).days
                        
                        if partner:
                            relationship_text = f"**đã kết hôn với {partner.mention} ({days_married} days)**"
                        else:
                            relationship_text = f"**đã kết hôn ({days_married} days)**"
                    except ValueError:
                        # Fallback nếu không parse được ngày
                        if partner:
                            relationship_text = f"**đã kết hôn với {partner.mention}**"
                        else:
                            relationship_text = "**đã kết hôn**"
                else:
                    # Fallback nếu format không đúng
                    relationship_text = "**đã kết hôn**"
                    
            elif profile[5]:  # relationship_status từ profiles (chưa kết hôn)
                status_map = {
                    "unclear": "Mập mờ",
                    "complicated": "Phức tạp",
                    "single_fun": "Độc thân vui tính",
                    "crush_pending": "Crush chưa đổ",
                    "waiting_fate": "Đang đợi duyên",
                    "flirting": "Thả thính dạo",
                    "forever_single": "Ế từ trong trứng",
                    "taken": "Hoa đã có chủ",
                    "dating": "Đang hẹn hò"
                }
                relationship_text = f"**{status_map.get(profile[5], profile[5])}**"

            profile_text += f"{profile_emoji.nhay7mau} MQH: {relationship_text}\n"

            # Thêm ảnh to nếu có - với validation URL
            if profile[6] and is_valid_url(profile[6]):  # profile_image
                try:
                    embed.set_image(url=profile[6].strip())
                except Exception:
                    pass  # Bỏ qua nếu URL không hợp lệ
        else:
            # Profile mặc định chưa điền gì
            profile_text += f"{profile_emoji.nhay7mau} Tên: ㅤ\n"
            profile_text += f"{profile_emoji.nhay7mau} Biệt danh: ㅤ\n"
            profile_text += f"{profile_emoji.nhay7mau} Ngày sinh: ㅤ\n"
            profile_text += f"{profile_emoji.nhay7mau} Nơi ở: ㅤ\n"
            profile_text += f"{profile_emoji.nhay7mau} Sở thích: ㅤ\n"

            # Vẫn kiểm tra marry từ users table
            relationship_text = ""
            if profile[7] and profile[7].strip():  # marry field có dữ liệu
                # Parse dữ liệu marry như trong marry.py
                import re
                marry_status = profile[7]
                matches = re.findall(r'<@(\d+)>', marry_status)
                name_match = re.search(r'(?<=bằng\s)[^<]+', marry_status)
                emoji_match = re.search(r'(<a?:\w+:\d+>)', marry_status)
                date_match = re.search(r'Ngày kết hôn:  (\d{2}/\d{2}/\d{4})', marry_status)
                
                if len(matches) >= 2 and name_match and emoji_match and date_match:
                    # Xác định partner (user khác với target_user)
                    partner_id = int(matches[0]) if int(matches[0]) != target_user.id else int(matches[1])
                    partner = interaction.client.get_user(partner_id)
                    ring_name = name_match.group().strip()
                    emoji = emoji_match.group(0)
                    wedding_date = date_match.group(1)
                    
                    # Tính số ngày đã kết hôn
                    try:
                        wedding_datetime = datetime.strptime(wedding_date, "%d/%m/%Y")
                        current_datetime = datetime.now()
                        days_married = (current_datetime - wedding_datetime).days
                        
                        if partner:
                            relationship_text = f"**đã kết hôn với {partner.mention} ({days_married} days)**"
                        else:
                            relationship_text = f"**đã kết hôn ({days_married} days)**"
                    except ValueError:
                        # Fallback nếu không parse được ngày
                        if partner:
                            relationship_text = f"**đã kết hôn với {partner.mention}**"
                        else:
                            relationship_text = "**đã kết hôn**"
                else:
                    # Fallback nếu format không đúng
                    relationship_text = "**đã kết hôn**"
            
            profile_text += f"{profile_emoji.nhay7mau} MQH: {relationship_text}\n"
        
        embed.add_field(name="", value=profile_text, inline=False)
        
        # Footer với avatar server và thời gian
        timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        current_time = datetime.now(timezone).strftime("%H:%M:%S")
        footer_text = f"𝑯𝒂̣𝒕 𝒈𝒊𝒐̂́𝒏𝒈 𝒕𝒂̂̀𝒎 𝒕𝒉𝒂̂̀𝒏 • {current_time}"
        
        if interaction.guild and interaction.guild.icon:
            embed.set_footer(text=footer_text, icon_url=interaction.guild.icon.url)
        else:
            embed.set_footer(text=footer_text)
        
        # Tạo view mới với marry status
        marry_status = profile[7] if profile else None
        view = ProfileView(user_id, marry_status)
        
        # Tìm tin nhắn gốc profile để cập nhật
        try:
            # Tìm tin nhắn profile của chính user này trong channel
            found_message = False
            async for message in interaction.channel.history(limit=200):
                if (message.author == interaction.client.user and 
                    message.embeds and 
                    len(message.embeds) > 0 and
                    message.embeds[0].description and
                    "BIO CARD" in message.embeds[0].description and
                    message.embeds[0].fields and
                    len(message.embeds[0].fields) > 0 and
                    # Kiểm tra mention của user và view components
                    f"<@{user_id}>" in message.embeds[0].fields[0].value and
                    message.components):  # Profile embed có view components (buttons)
                    await message.edit(embed=embed, view=view)
                    found_message = True
                    break
            
            # Nếu không tìm được, gửi embed mới
            if not found_message:
                await interaction.followup.send(embed=embed, view=view)
                
        except Exception as e:
            # Fallback: gửi embed mới nếu có lỗi
            try:
                await interaction.followup.send(embed=embed, view=view)
            except:
                pass

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        
        # Validate birthday format
        birthday_valid = True
        if self.birthday.value:
            try:
                datetime.strptime(self.birthday.value, "%d/%m/%Y")
            except ValueError:
                birthday_valid = False
        
        if not birthday_valid and self.birthday.value:
            await interaction.response.send_message(f"{list_emoji.tick_check} Ngày sinh không đúng định dạng DD/MM/YYYY!", ephemeral=True)
            return
            
        # Đảm bảo user tồn tại trong bảng users
        ensure_user_exists(user_id)
        
        # Lấy thông tin profile hiện tại để giữ lại các field khác
        cursor.execute("SELECT relationship_status, profile_image FROM profiles WHERE user_id = ?", (user_id,))
        existing_profile = cursor.fetchone()
        
        if existing_profile:
            # Cập nhật chỉ các field thông tin cá nhân, giữ nguyên relationship_status và profile_image
            cursor.execute('''UPDATE profiles 
                             SET name = ?, nickname = ?, birthday = ?, location = ?, hobby = ?, updated_at = ?
                             WHERE user_id = ?''', 
                          (self.name.value, self.nickname.value, self.birthday.value, 
                           self.location.value, self.hobby.value, datetime.now(), user_id))
        else:
            # Tạo mới nếu chưa có profile
            cursor.execute('''INSERT INTO profiles 
                             (user_id, name, nickname, birthday, location, hobby, updated_at) 
                             VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                          (user_id, self.name.value, self.nickname.value, 
                           self.birthday.value, self.location.value, self.hobby.value, datetime.now()))
        conn.commit()
        
        # Gửi tin nhắn thành công trước
        await interaction.response.send_message(f"{list_emoji.tickdung} Đã cập nhật thông tin cá nhân!", ephemeral=True)
        
        # Cập nhật embed profile
        await self.update_profile_embed(interaction)

class RelationshipSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Mập mờ", value="unclear", emoji=f"{profile_emoji.traitim_profile}"),
            discord.SelectOption(label="Phức tạp", value="complicated", emoji=f"{profile_emoji.traitim_profile}"),
            discord.SelectOption(label="Độc thân vui tính", value="single_fun", emoji=f"{profile_emoji.traitim_profile}"),
            discord.SelectOption(label="Crush chưa đổ", value="crush_pending", emoji=f"{profile_emoji.traitim_profile}"),
            discord.SelectOption(label="Đang đợi duyên", value="waiting_fate", emoji=f"{profile_emoji.traitim_profile}"),
            discord.SelectOption(label="Thả thính dạo", value="flirting", emoji=f"{profile_emoji.traitim_profile}"),
            discord.SelectOption(label="Ế từ trong trứng", value="forever_single", emoji=f"{profile_emoji.traitim_profile}"),
            discord.SelectOption(label="Hoa đã có chủ", value="taken", emoji=f"{profile_emoji.traitim_profile}"),
            discord.SelectOption(label="Đang hẹn hò", value="dating", emoji=f"{profile_emoji.traitim_profile}"),
        ]
        super().__init__(placeholder="Chọn tình trạng mối quan hệ...", options=options)

    async def update_profile_embed(self, interaction):
        """Sử dụng lại phương thức từ ProfileModal"""
        modal = ProfileModal()
        await modal.update_profile_embed(interaction)

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        
        # Đảm bảo user tồn tại trong bảng users
        ensure_user_exists(user_id)
        
        # Lấy thông tin profile hiện tại để giữ lại các field khác
        cursor.execute("SELECT name, nickname, birthday, location, hobby, profile_image FROM profiles WHERE user_id = ?", (user_id,))
        existing_profile = cursor.fetchone()
        
        if existing_profile:
            # Cập nhật chỉ relationship_status, giữ nguyên các field khác
            cursor.execute('''UPDATE profiles 
                             SET relationship_status = ?, updated_at = ?
                             WHERE user_id = ?''', 
                          (self.values[0], datetime.now(), user_id))
        else:
            # Tạo mới nếu chưa có profile
            cursor.execute('''INSERT INTO profiles 
                             (user_id, relationship_status, updated_at) 
                             VALUES (?, ?, ?)''', 
                          (user_id, self.values[0], datetime.now()))
        conn.commit()
        
        status_map = {
            "unclear": "Mập mờ",
            "complicated": "Phức tạp",
            "single_fun": "Độc thân vui tính",
            "crush_pending": "Crush chưa đổ",
            "waiting_fate": "Đang đợi duyên",
            "flirting": "Thả thính dạo",
            "forever_single": "Ế từ trong trứng",
            "taken": "Hoa đã có chủ",
            "dating": "Đang hẹn hò"
        }
        
        # Gửi tin nhắn thành công trước
        await interaction.response.send_message(f"{list_emoji.tickdung} Đã cập nhật tình trạng mối quan hệ: {status_map[self.values[0]]}", ephemeral=True)
        
        # Cập nhật embed profile
        await self.update_profile_embed(interaction)

class ProfileImageModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Cập nhật ảnh profile", timeout=300)

    image_url = discord.ui.TextInput(
        label="Link ảnh",
        placeholder="Nhập link ảnh profile của bạn",
        required=False,
        style=discord.TextStyle.long
    )

    async def update_profile_embed(self, interaction):
        """Sử dụng lại phương thức từ ProfileModal"""
        modal = ProfileModal()
        await modal.update_profile_embed(interaction)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        image_url = self.image_url.value
        
        # Validate URL nếu có nhập
        if image_url and not is_valid_url(image_url):
            await interaction.response.send_message(f"{list_emoji.tick_check} Link ảnh không hợp lệ! Vui lòng nhập URL hợp lệ (http/https)", ephemeral=True)
            return
        
        # Đảm bảo user tồn tại trong bảng users
        ensure_user_exists(user_id)
        
        # Lấy thông tin profile hiện tại để giữ lại các field khác
        cursor.execute("SELECT name, nickname, birthday, location, hobby, relationship_status FROM profiles WHERE user_id = ?", (user_id,))
        existing_profile = cursor.fetchone()
        
        if existing_profile:
            # Cập nhật chỉ profile_image, giữ nguyên các field khác
            cursor.execute('''UPDATE profiles 
                             SET profile_image = ?, updated_at = ?
                             WHERE user_id = ?''', 
                          (self.image_url.value, datetime.now(), user_id))
        else:
            # Tạo mới nếu chưa có profile
            cursor.execute('''INSERT INTO profiles 
                             (user_id, profile_image, updated_at) 
                             VALUES (?, ?, ?)''', 
                          (user_id, self.image_url.value, datetime.now()))
        conn.commit()
        
        # Gửi tin nhắn thành công trước
        await interaction.response.send_message(f"{list_emoji.tickdung} Đã cập nhật ảnh profile!", ephemeral=True)
        
        # Cập nhật embed profile
        await self.update_profile_embed(interaction)

class ProfileView(discord.ui.View):
    def __init__(self, user_id, marry_status=None, timeout=180):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.marry_status = marry_status
        
        # Nếu đã kết hôn thì disable button MQH
        self.is_married = marry_status and marry_status.strip()
        
        # Disable button MQH nếu đã kết hôn
        if self.is_married:
            for item in self.children:
                if hasattr(item, 'custom_id') and item.custom_id == 'mqh_button':
                    item.disabled = True
                    break

    @discord.ui.button(emoji=f"{profile_emoji.setting_profile}", style=discord.ButtonStyle.gray)
    async def settings_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{list_emoji.tick_check} Bạn không thể chỉnh sửa profile của người khác!", ephemeral=True)
            return
            
        # Lấy thông tin hiện tại từ bảng profiles
        cursor.execute("SELECT name, nickname, birthday, location, hobby FROM profiles WHERE user_id = ?", (self.user_id,))
        profile = cursor.fetchone()
        
        modal = ProfileModal()
        if profile:
            modal.name.default = profile[0] or ""
            modal.nickname.default = profile[1] or ""  
            modal.birthday.default = profile[2] or ""
            modal.location.default = profile[3] or ""
            modal.hobby.default = profile[4] or ""
            
        await interaction.response.send_modal(modal)

    @discord.ui.button(emoji=f"{profile_emoji.mqh_profile}", style=discord.ButtonStyle.gray, custom_id="mqh_button")
    async def relationship_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{list_emoji.tick_check} Bạn không thể chỉnh sửa profile của người khác!", ephemeral=True)
            return
        
        # Kiểm tra nếu đã kết hôn thì không cho phép chọn relationship status
        if self.is_married:
            await interaction.response.send_message("💍 Bạn đã kết hôn rồi, không thể thay đổi tình trạng mối quan hệ!", ephemeral=True)
            return
            
        view = discord.ui.View()
        view.add_item(RelationshipSelect())
        await interaction.response.send_message("Chọn tình trạng mối quan hệ:", view=view, ephemeral=True)

    @discord.ui.button(emoji=f"{profile_emoji.img_profile}", style=discord.ButtonStyle.gray)
    async def image_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{list_emoji.tick_check} Bạn không thể chỉnh sửa profile của người khác!", ephemeral=True)
            return
            
        modal = ProfileImageModal()
        cursor.execute("SELECT profile_image FROM profiles WHERE user_id = ?", (self.user_id,))
        result = cursor.fetchone()
        if result and result[0]:
            modal.image_url.default = result[0]
            
        await interaction.response.send_modal(modal)

    @discord.ui.button(emoji=f"{profile_emoji.marry_profile}", style=discord.ButtonStyle.grey)
    async def help_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title=f"{profile_emoji.marry_card} Hướng dẫn marry {profile_emoji.marry_card}", color=0xFFFFFF)
        embed.description = f"""
            - **Đảm bảo là bạn đã** **`zdk`** **và** **`zcash`** **có đủ tiền {list_emoji.pinkcoin} để mua nhẫn**

            {profile_emoji.so1_profile} **`zshop`** để chọn nhẫn
            {profile_emoji.so2_profile} **`zbuy`** + ID nhẫn (zbuy 1) 
            {profile_emoji.so3_profile} **`zmarry`** @user ID nhẫn
            {profile_emoji.so4_profile} **`zmarry`** để xem profile"""
        # Thêm avatar server và text
        if interaction.guild and interaction.guild.icon:
            embed.set_footer(text="𝑯𝒂̣𝒕 𝒈𝒊𝒐̂́𝒏𝒈 𝒕𝒂̂̀𝒎 𝒕𝒉𝒂̂̀𝒏", icon_url=interaction.guild.icon.url)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class Profile(commands.Cog):
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

    @commands.command(aliases=["bio"], description="Xem profile cá nhân")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def profile(self, ctx, member: discord.Member = None):
        if await self.check_command_disabled(ctx):
            return
        
        # Xử lý trường hợp member không tồn tại
        target_user = member or ctx.author
        
        # Kiểm tra nếu member là None nhưng có argument (có thể là ID không hợp lệ)
        if member is None and len(ctx.message.content.split()) > 1:
            # Có argument nhưng không parse được thành Member
            await ctx.send(f"{list_emoji.tick_check} Không tìm thấy người dùng này trong server!")
            return
        
        user_id = target_user.id
        
        # Lấy thông tin profile từ bảng profiles và marry từ bảng users
        cursor.execute('''SELECT p.name, p.nickname, p.birthday, p.location, p.hobby, 
                                p.relationship_status, p.profile_image, u.marry
                         FROM profiles p
                         LEFT JOIN users u ON p.user_id = u.user_id
                         WHERE p.user_id = ?''', (user_id,))
        profile = cursor.fetchone()
        
        # Nếu không có profile, lấy thông tin marry từ users
        if not profile:
            cursor.execute("SELECT marry FROM users WHERE user_id = ?", (user_id,))
            user_data = cursor.fetchone()
            marry_data = user_data[0] if user_data else None
            profile = (None, None, None, None, None, None, None, marry_data)
        
        # Tạo embed với line màu
        embed = discord.Embed(title=f"", description=f"# {profile_emoji.profile_card} BIO CARD {profile_emoji.profile_card}", color=0xFFB2E0)        
        # Title với emoji
        # embed.add_field(name=f"{profile_emoji.profile_card} PROFILE CARD {profile_emoji.profile_card}", value="", inline=False)
        
        # Set avatar nhỏ bên phải
        embed.set_thumbnail(url=target_user.display_avatar.url)
        
        # Thông tin cơ bản - Acc luôn hiển thị với mention người dùng
        profile_text = f"{profile_emoji.nhay7mau} Acc: {target_user.mention}\n"
        
        if profile and profile[0] is not None:  # Có profile data
            profile_text += f"{profile_emoji.nhay7mau} Tên: **{profile[0] or 'ㅤ'}**\n"            
            profile_text += f"{profile_emoji.nhay7mau} Biệt danh: **{profile[1] or 'ㅤ'}**\n" 
            profile_text += f"{profile_emoji.nhay7mau} Ngày sinh: **{profile[2] or 'ㅤ'}**\n"
            profile_text += f"{profile_emoji.nhay7mau} Nơi ở: **{profile[3] or 'ㅤ'}**\n"
            profile_text += f"{profile_emoji.nhay7mau} Sở thích: **{profile[4] or 'ㅤ'}**\n"

            # Xử lý mối quan hệ
            relationship_text = ""
            if profile[7] and profile[7].strip():  # marry field từ users có dữ liệu
                # Parse dữ liệu marry như trong marry.py
                import re
                marry_status = profile[7]
                matches = re.findall(r'<@(\d+)>', marry_status)
                name_match = re.search(r'(?<=bằng\s)[^<]+', marry_status)
                emoji_match = re.search(r'(<a?:\w+:\d+>)', marry_status)
                date_match = re.search(r'Ngày kết hôn:  (\d{2}/\d{2}/\d{4})', marry_status)
                
                if len(matches) >= 2 and name_match and emoji_match and date_match:
                    # Xác định partner (user khác với target_user)
                    partner_id = int(matches[0]) if int(matches[0]) != target_user.id else int(matches[1])
                    partner = self.client.get_user(partner_id)
                    ring_name = name_match.group().strip()
                    emoji = emoji_match.group(0)
                    wedding_date = date_match.group(1)
                    
                    # Tính số ngày đã kết hôn
                    try:
                        wedding_datetime = datetime.strptime(wedding_date, "%d/%m/%Y")
                        current_datetime = datetime.now()
                        days_married = (current_datetime - wedding_datetime).days
                        
                        if partner:
                            relationship_text = f"**đã kết hôn với {partner.mention} ({days_married} days)**"
                        else:
                            relationship_text = f"**đã kết hôn ({days_married} days)**"
                    except ValueError:
                        # Fallback nếu không parse được ngày
                        if partner:
                            relationship_text = f"**đã kết hôn với {partner.mention}**"
                        else:
                            relationship_text = "**đã kết hôn**"
                else:
                    # Fallback nếu format không đúng
                    relationship_text = "**đã kết hôn**"
                    
            elif profile[5]:  # relationship_status từ profiles (chưa kết hôn)
                status_map = {
                    "unclear": "Mập mờ",
                    "complicated": "Phức tạp",
                    "single_fun": "Độc thân vui tính",
                    "crush_pending": "Crush chưa đổ",
                    "waiting_fate": "Đang đợi duyên",
                    "flirting": "Thả thính dạo",
                    "forever_single": "Ế từ trong trứng",
                    "taken": "Hoa đã có chủ",
                    "dating": "Đang hẹn hò"
                }
                relationship_text = f"**{status_map.get(profile[5], profile[5])}**"

            profile_text += f"{profile_emoji.nhay7mau} MQH: {relationship_text}\n"

            # Thêm ảnh to nếu có - với validation URL
            if profile[6] and is_valid_url(profile[6]):  # profile_image
                try:
                    embed.set_image(url=profile[6].strip())
                except Exception:
                    pass  # Bỏ qua nếu URL không hợp lệ
        else:
            # Profile mặc định chưa điền gì - vẫn hiển thị Acc
            profile_text += f"{profile_emoji.nhay7mau} Tên: ㅤ\n"
            profile_text += f"{profile_emoji.nhay7mau} Biệt danh: ㅤ\n"
            profile_text += f"{profile_emoji.nhay7mau} Ngày sinh: ㅤ\n"
            profile_text += f"{profile_emoji.nhay7mau} Nơi ở: ㅤ\n"
            profile_text += f"{profile_emoji.nhay7mau} Sở thích: ㅤ\n"

            # Vẫn kiểm tra marry từ users table
            relationship_text = ""
            if profile[7] and profile[7].strip():  # marry field có dữ liệu
                # Parse dữ liệu marry như trong marry.py
                import re
                marry_status = profile[7]
                matches = re.findall(r'<@(\d+)>', marry_status)
                name_match = re.search(r'(?<=bằng\s)[^<]+', marry_status)
                emoji_match = re.search(r'(<a?:\w+:\d+>)', marry_status)
                date_match = re.search(r'Ngày kết hôn:  (\d{2}/\d{2}/\d{4})', marry_status)
                
                if len(matches) >= 2 and name_match and emoji_match and date_match:
                    # Xác định partner (user khác với target_user)
                    partner_id = int(matches[0]) if int(matches[0]) != target_user.id else int(matches[1])
                    partner = self.client.get_user(partner_id)
                    ring_name = name_match.group().strip()
                    emoji = emoji_match.group(0)
                    wedding_date = date_match.group(1)
                    
                    # Tính số ngày đã kết hôn
                    try:
                        wedding_datetime = datetime.strptime(wedding_date, "%d/%m/%Y")
                        current_datetime = datetime.now()
                        days_married = (current_datetime - wedding_datetime).days
                        
                        if partner:
                            relationship_text = f"**đã kết hôn với {partner.mention} ({days_married} days)**"
                        else:
                            relationship_text = f"**đã kết hôn ({days_married} days)**"
                    except ValueError:
                        # Fallback nếu không parse được ngày
                        if partner:
                            relationship_text = f"**đã kết hôn với {partner.mention}**"
                        else:
                            relationship_text = "**đã kết hôn**"
                else:
                    # Fallback nếu format không đúng
                    relationship_text = "**đã kết hôn**"
            
            profile_text += f"{profile_emoji.nhay7mau} MQH: {relationship_text}\n"
        
        embed.add_field(name="", value=profile_text, inline=False)
        
        # Footer với avatar server và thời gian
        timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        current_time = datetime.now(timezone).strftime("%H:%M:%S")
        
        footer_text = f"𝑯𝒂̣𝒕 𝒈𝒊𝒐̂́𝒏𝒈 𝒕𝒂̂̀𝒎 𝒕𝒉𝒂̂̀𝒏 • {current_time}"
        
        if ctx.guild and ctx.guild.icon:
            embed.set_footer(text=footer_text, icon_url=ctx.guild.icon.url)
        else:
            embed.set_footer(text=footer_text)
        
        # Chỉ hiện buttons nếu là profile của chính mình
        if target_user.id == ctx.author.id:
            marry_status = profile[7] if profile else None
            view = ProfileView(user_id, marry_status)
            await ctx.send(embed=embed, view=view)
        else:
            await ctx.send(embed=embed)

    @profile.error
    async def profile_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = divmod(int(error.retry_after), 60)
            formatted_time = f"{remaining_time[0]}m{remaining_time[1]}s"
            message = await ctx.send(f"{list_emoji.tick_check} Vui lòng đợi thêm `{formatted_time}` để sử dụng lệnh này!")
            await asyncio.sleep(3)
            await message.delete()
            try:
                await ctx.message.delete()
            except:
                pass
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(f"{list_emoji.tick_check} Không tìm thấy người dùng `{error.argument}` trong server này!")
            return  # Không raise error nữa
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"{list_emoji.tick_check} Đối số không hợp lệ! Sử dụng: `zprofile [@user]`")
            return  # Không raise error nữa
        else:
            print(f"Profile command error: {error}")
            raise error

    @commands.command(name="migrate_profiles", description="Migrate users từ bảng users sang profiles")
    @is_bot_owner()
    async def migrate_profiles_command(self, ctx):
        """Command để migrate toàn bộ user_id từ users sang profiles"""
        embed = discord.Embed(
            title="🔄 Đang thực hiện migration...",
            description="Đang chuyển dữ liệu user từ bảng `users` sang `profiles`",
            color=0xFFA500
        )
        message = await ctx.send(embed=embed)
        
        try:
            # Thực hiện migration
            migrated_count = migrate_users_to_profiles()
            
            # Lấy thống kê sau migration
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM profiles")
            total_profiles = cursor.fetchone()[0]
            
            # Cập nhật embed với kết quả
            embed = discord.Embed(
                title=f"{list_emoji.tickdung} Migration hoàn tất!",
                color=0x00FF00
            )
            embed.add_field(name="📊 Thống kê", value=f"""
**Tổng users trong bảng `users`:** {total_users:,}
**Tổng profiles trong bảng `profiles`:** {total_profiles:,}
**Users được migrate:** {migrated_count:,}
            """, inline=False)
            
            if migrated_count > 0:
                embed.add_field(name="✨ Kết quả", 
                              value=f"Đã thêm {migrated_count:,} users vào bảng profiles", 
                              inline=False)
            else:
                embed.add_field(name="ℹ️ Thông tin", 
                              value="Tất cả users đã có trong bảng profiles", 
                              inline=False)
                
            await message.edit(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="Migration thất bại!",
                description=f"Lỗi: {str(e)}",
                color=0xFF0000
            )
            await message.edit(embed=embed)

    @commands.command(name="profile_stats", description="Xem thống kê bảng profiles")
    @is_bot_owner()
    async def profile_stats_command(self, ctx):
        """Command để xem thống kê bảng profiles"""
        try:
            # Lấy thống kê
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM profiles")
            total_profiles = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM profiles WHERE name != '' OR nickname != '' OR birthday != '' OR location != '' OR hobby != ''")
            filled_profiles = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM profiles WHERE profile_image != ''")
            profiles_with_images = cursor.fetchone()[0]
            
            embed = discord.Embed(
                title="📊 Thống kê Profile System",
                color=0xFFB2E0
            )
            
            embed.add_field(name="👥 Dữ liệu cơ bản", value=f"""
**Users trong `users`:** {total_users:,}
**Profiles trong `profiles`:** {total_profiles:,}
**Profiles đã điền thông tin:** {filled_profiles:,}
**Profiles có ảnh:** {profiles_with_images:,}
            """, inline=False)
            
            completion_rate = (filled_profiles / total_profiles * 100) if total_profiles > 0 else 0
            embed.add_field(name="📈 Tỷ lệ hoàn thành", 
                          value=f"{completion_rate:.1f}% users đã điền profile", 
                          inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"{list_emoji.tick_check} Lỗi khi lấy thống kê: {e}")

    @commands.command(name="xoa_img", description="Xóa các URL ảnh không hợp lệ")
    @is_bot_owner()
    async def xoa_img(self, ctx):
        """Command để xóa các URL ảnh không hợp lệ trong database"""
        try:
            # Lấy tất cả profile có ảnh
            cursor.execute("SELECT user_id, profile_image FROM profiles WHERE profile_image != '' AND profile_image IS NOT NULL")
            profiles_with_images = cursor.fetchall()
            
            invalid_count = 0
            cleaned_profiles = []
            
            for user_id, image_url in profiles_with_images:
                if not is_valid_url(image_url):
                    # Xóa URL không hợp lệ
                    cursor.execute("UPDATE profiles SET profile_image = '', updated_at = ? WHERE user_id = ?", 
                                 (datetime.now(), user_id))
                    invalid_count += 1
                    cleaned_profiles.append((user_id, image_url))
            
            conn.commit()
            
            embed = discord.Embed(
                title=f"{list_emoji.tickdung} Dọn dẹp hoàn tất!",
                color=0x00FF00
            )
            
            embed.add_field(name="📊 Kết quả", value=f"""
**Tổng profiles có ảnh:** {len(profiles_with_images):,}
**URLs không hợp lệ đã xóa:** {invalid_count:,}
**URLs hợp lệ giữ lại:** {len(profiles_with_images) - invalid_count:,}
            """, inline=False)
            
            if invalid_count > 0:
                # Hiển thị một vài ví dụ URL không hợp lệ (tối đa 3)
                examples = cleaned_profiles[:3]
                example_text = "\n".join([f"<@{user_id}>: `{url[:50]}...`" if len(url) > 50 else f"<@{user_id}>: `{url}`" 
                                        for user_id, url in examples])
                embed.add_field(name="🗑️ Ví dụ URLs đã xóa", value=example_text, inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"{list_emoji.tick_check} Lỗi khi dọn dẹp: {e}")

async def setup(client):
    await client.add_cog(Profile(client))
