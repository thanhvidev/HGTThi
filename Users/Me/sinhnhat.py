import asyncio
import discord
import sqlite3
import random
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from Commands.Mod.list_emoji import list_emoji, profile_emoji, sinhnhat_emoji
from utils.checks import is_bot_owner, is_admin, is_mod
import json
import pytz
from typing import Optional, Tuple

# Helper functions for date-safe birthday calculations
def safe_birthday_in_year(bd: datetime, year: int) -> datetime:
    """Return birthday date in a specific year; handle Feb 29 by using Feb 28 in non-leap years."""
    try:
        return bd.replace(year=year)
    except ValueError:
        # Feb 29 -> Feb 28 for non-leap years
        return bd.replace(year=year, day=28)

def compute_next_birthday(bd: datetime, tz: str = 'Asia/Ho_Chi_Minh') -> Tuple[datetime, int]:
    """Compute next birthday date (date-only) and days until from now in the given timezone.
    Returns (next_birthday_date, days_until).
    """
    timezone = pytz.timezone(tz)
    now_dt = datetime.now(timezone)
    today = now_dt.date()
    this_year_bd = safe_birthday_in_year(bd, today.year).date()
    if this_year_bd < today:
        next_bd = safe_birthday_in_year(bd, today.year + 1).date()
    else:
        next_bd = this_year_bd
    days_until = (next_bd - today).days
    return datetime.combine(next_bd, datetime.min.time()), days_until

# Kết nối database
conn = sqlite3.connect('economy.db')
cursor = conn.cursor()

# Channel ID để thông báo sinh nhật
BIRTHDAY_CHANNELID = 1417754513770680370

# Random birthday messages
BIRTHDAY_MESSAGES = [
    f"{sinhnhat_emoji.chu_sn} Happy Birthday bestie ! Chúc bạn tuổi mới auto xinh, auto giàu, auto hạnh phúc. Deadline thì né, may mắn thì ghé, crush thì tự động đổ. Nhớ quẩy cho nhiệt nha! {sinhnhat_emoji.nhay_sn2}",
    f"{sinhnhat_emoji.chu_sn} Happy b-day. Chúc bạn tuổi mới sống hết mình như trending TikTok, vui như lúc có lương, và rực rỡ như ảnh có filter xịn. Bỏ hết lo âu, chỉ giữ niềm vui và cái mood \"slay\" thôi nha. {sinhnhat_emoji.nhay_sn2}",
    f"{sinhnhat_emoji.chu_sn} Chúc mừng sinh nhật. Chúc bạn tuổi mới full năng lượng, bớt lười, thêm may mắn. Cười to như meme, yêu đời như crush rep nhanh. Đừng quên mình sinh ra là để toả sáng nha! {sinhnhat_emoji.nhay_sn2}",
    f"{sinhnhat_emoji.chu_sn} Happy Birthday! Chúc bạn tuổi mới luôn xinh xẻo, nhiều tiền nhiều duyên, hết buồn hết phiền. Hôm nay phải chill tới bến nhaaa! {sinhnhat_emoji.nhay_sn2}",
    f"{sinhnhat_emoji.chu_sn} Sinh nhật zui zẻ. Mong bạn luôn tỏa sáng, sống đúng chất mình, và được yêu thương nhiều như bạn yêu đời. {sinhnhat_emoji.nhay_sn2}",
    f"{sinhnhat_emoji.chu_sn} Tuổi mới xịn sò ghê . Chúc bạn đủ may mắn để cười mỗi ngày, đủ kiên nhẫn để đạt ước mơ, và đủ \"cháy\" để không ai quên được. {sinhnhat_emoji.nhay_sn2}",
    f"{sinhnhat_emoji.chu_sn} Happy b-day. Chúc bạn tuổi mới học ít mà nhớ nhiều, ăn nhiều mà không mập, chơi vui mà không lo deadline dí. {sinhnhat_emoji.nhay_sn2}",
    f"{sinhnhat_emoji.chu_sn} Happy Birthday bạn iu! Chúc bạn tuổi mới lúc nào cũng vui vẻ, yêu đời, và được bao quanh bởi những người thật sự quan tâm. Mong mọi ước mơ đều thành hiện thực, từ nhỏ bé nhất tới lớn lao nhất. Nhớ là luôn giữ nụ cười tươi như ánh mặt trời, vì nó làm cả thế giới xung quanh rực rỡ hơn đó. {sinhnhat_emoji.nhay_sn2}",
    f"{sinhnhat_emoji.chu_sn} Sinh nhật vui vẻ nha bestie! Chúc mày thêm tuổi mới thì thêm may mắn, thêm sức khoẻ và thêm cả cơ hội để làm những điều mày thích. Mong mọi dự định đều suôn sẻ, mọi niềm vui thì nhân đôi, còn buồn phiền thì nhân chia cho hết. Năm nay phải \"quẩy\" thật cháy để đáng nhớ nha! {sinhnhat_emoji.nhay_sn2}",
    f"{sinhnhat_emoji.chu_sn} Tuổi mới lại tới rồi. Chúc bạn càng lớn càng xinh đẹp, càng giỏi giang và càng thành công. Mong cho mỗi ngày đều là một trang mới tràn ngập tiếng cười, cơ hội mới và những trải nghiệm tuyệt vời. Và quan trọng nhất: luôn có bạn bè ở bên cạnh để chia sẻ mọi thứ cùng nhau. {sinhnhat_emoji.nhay_sn2}",
    f"{sinhnhat_emoji.chu_sn} Happy b-day! Chúc bạn tuổi mới đầy năng lượng, đủ dũng cảm để theo đuổi ước mơ, đủ mạnh mẽ để vượt qua khó khăn, và đủ kiên nhẫn để tận hưởng từng khoảnh khắc. Hãy nhớ là cuộc sống này luôn đáng yêu, nhất là khi có những ngày đặc biệt như hôm nay để ta thấy mình thật sự được trân trọng. {sinhnhat_emoji.nhay_sn2}",
    f"{sinhnhat_emoji.chu_sn} Sinh nhật hạnh phúc nha bạn hiền. Mong tuổi mới của bạn sẽ là một hành trình đầy màu sắc, với nhiều trải nghiệm mới mẻ và đáng nhớ. Chúc bạn ăn ngon không mập, ngủ nhiều vẫn khoẻ, học ít nhưng điểm cao, làm gì cũng thuận lợi. {sinhnhat_emoji.nhay_sn2}"
]

def get_vietnamese_weekday(weekday_name):
    """Chuyển đổi tên ngày từ tiếng Anh sang tiếng Việt"""
    weekday_map = {
        'monday': 'Thứ hai',
        'tuesday': 'Thứ ba', 
        'wednesday': 'Thứ tư',
        'thursday': 'Thứ năm',
        'friday': 'Thứ sáu',
        'saturday': 'Thứ bảy',
        'sunday': 'Chủ nhật'
    }
    return weekday_map.get(weekday_name.lower(), weekday_name)

def ensure_user_exists(user_id):
    """Đảm bảo user tồn tại trong bảng users và profiles"""
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, 0))
    
    cursor.execute("SELECT user_id FROM profiles WHERE user_id = ?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO profiles (user_id) VALUES (?)", (user_id,))
    
    conn.commit()

class BirthdaySetModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Thiết lập sinh nhật", timeout=300)

    birthday = discord.ui.TextInput(
        label="Ngày sinh",
        placeholder="DD/MM/YYYY (ví dụ: 26/03/2000)",
        max_length=10,
        required=True
    )

    async def update_birthday_embed(self, interaction):
        """Cập nhật embed birthday sau khi thiết lập sinh nhật"""
        user_id = interaction.user.id
        target_user = interaction.user
        
        # Đảm bảo user tồn tại
        ensure_user_exists(user_id)
        
        # Lấy thông tin sinh nhật
        cursor.execute("SELECT birthday FROM profiles WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        birthday_str = result[0] if result and result[0] else None
        
        # Tạo embed
        embed = discord.Embed(title=f"", description=f"# {sinhnhat_emoji.lich_sn} Your Birthday {sinhnhat_emoji.lich_sn}", color=0xFF89FA)
        # embed.add_field(name=f"{sinhnhat_emoji.banh_sn} Your Birthday {sinhnhat_emoji.banh_sn}", value="", inline=False)
        embed.set_thumbnail(url=target_user.display_avatar.url)
        
        if birthday_str:
            try:
                birthday_date = datetime.strptime(birthday_str, "%d/%m/%Y")
                next_birthday_dt, days_until = compute_next_birthday(birthday_date)

                if days_until == 0:
                    next_text = "**HÔM NAY!**"
                elif days_until == 1:
                    next_text = "**Ngày mai**"
                else:
                    vietnamese_weekday = get_vietnamese_weekday(next_birthday_dt.strftime('%A'))
                    next_text = f"{vietnamese_weekday}, {next_birthday_dt.strftime('%d-%m-%Y')} (còn {days_until} ngày)"

                birthday_text = f"{sinhnhat_emoji.nhay_sn} **Date:** **`{birthday_str}`**\n"
                # Chỉ hiển thị "Next:" khi không phải hôm nay
                if days_until == 0:
                    birthday_text += f"{sinhnhat_emoji.nhay_sn} {next_text}"
                else:
                    birthday_text += f"{sinhnhat_emoji.nhay_sn} **Next: {next_text}**"

            except ValueError:
                birthday_text = f"{sinhnhat_emoji.nhay_sn} **Date:** **`{birthday_str}`**\n"
                birthday_text += f"{sinhnhat_emoji.nhay_sn} **Next:** Không xác định được"
        else:
            birthday_text = f"{sinhnhat_emoji.nhay_sn} Chưa thiết lập sinh nhật\n"
            birthday_text += f"{sinhnhat_emoji.nhay_sn} Hãy bấm nút bên dưới để thiết lập!"
        
        embed.add_field(name="", value=birthday_text, inline=False)
        
        # Footer
        timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        current_time = datetime.now(timezone).strftime("%H:%M:%S")
        footer_text = f"𝑯𝒂̣𝒕 𝒈𝒊𝒐̂́𝒏𝒈 𝒕𝒂̂̀𝒎 𝒕𝒉𝒂̂̀𝒏 • {current_time}"
        
        if interaction.guild and interaction.guild.icon:
            embed.set_footer(text=footer_text, icon_url=interaction.guild.icon.url)
        else:
            embed.set_footer(text=footer_text)
        
        # Tạo view mới
        view = BirthdayView(user_id)
        
        # Tìm tin nhắn birthday gốc để cập nhật thay vì gửi mới
        try:
            found_message = False
            async for message in interaction.channel.history(limit=100):
                if (message.author == interaction.client.user and 
                    message.embeds and 
                    len(message.embeds) > 0 and
                    message.embeds[0].description and
                    "Your Birthday" in str(message.embeds[0].description)):
                    # Kiểm tra xem đây có phải tin nhắn birthday của user hiện tại không
                    # So sánh bằng cách kiểm tra thumbnail hoặc view components
                    if (message.embeds[0].thumbnail and str(target_user.id) in str(message.embeds[0].thumbnail.url)) or \
                       (hasattr(message, 'components') and message.components):
                        print(f"Tìm thấy message birthday để cập nhật cho user {target_user.id}")
                        await message.edit(embed=embed, view=view)
                        found_message = True
                        break
            
            if not found_message:
                print(f"Không tìm thấy message birthday cũ, có thể message đã bị xóa hoặc ngoài tầm tìm kiếm")
                        
        except Exception as e:
            print(f"Lỗi cập nhật embed birthday: {e}")

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
        cursor.execute("UPDATE profiles SET birthday = ? WHERE user_id = ?", (birthday_str, user_id))
        conn.commit()
        
        # Gửi tin nhắn thành công trước
        await interaction.response.send_message(
            f"{list_emoji.tickdung} Đã thiết lập sinh nhật của bạn: **{birthday_str}**!", 
            ephemeral=True
        )
        
        # Cập nhật embed birthday
        await self.update_birthday_embed(interaction)

class BirthdayDeleteConfirmView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=60)
        self.user_id = user_id

    async def update_birthday_embed(self, interaction):
        """Cập nhật embed birthday sau khi xóa sinh nhật"""
        user_id = self.user_id
        target_user = interaction.user
        
        # Đảm bảo user tồn tại
        ensure_user_exists(user_id)
        
        # Lấy thông tin sinh nhật (sẽ là None sau khi xóa)
        cursor.execute("SELECT birthday FROM profiles WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        birthday_str = result[0] if result and result[0] else None
        
        # Tạo embed
        embed = discord.Embed(title=f"", description=f"# {sinhnhat_emoji.lich_sn} Your Birthday {sinhnhat_emoji.lich_sn}", color=0xFF89FA)
        # embed.add_field(name=f"{sinhnhat_emoji.banh_sn} Your Birthday {sinhnhat_emoji.banh_sn}", value="", inline=False)
        embed.set_thumbnail(url=target_user.display_avatar.url)
        
        # Sau khi xóa sẽ là trạng thái chưa thiết lập
        birthday_text = f"{sinhnhat_emoji.nhay_sn} Chưa thiết lập sinh nhật\n"
        birthday_text += f"{sinhnhat_emoji.nhay_sn} Hãy bấm nút bên dưới để thiết lập!"
        
        embed.add_field(name="", value=birthday_text, inline=False)
        
        # Footer
        timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        current_time = datetime.now(timezone).strftime("%H:%M:%S")
        footer_text = f"𝑯𝒂̣𝒕 𝒈𝒊𝒐̂́𝒏𝒈 𝒕𝒂̂̀𝒎 𝒕𝒉𝒂̂̀𝒏 • {current_time}"
        
        if interaction.guild and interaction.guild.icon:
            embed.set_footer(text=footer_text, icon_url=interaction.guild.icon.url)
        else:
            embed.set_footer(text=footer_text)
        
        # Tạo view mới
        view = BirthdayView(user_id)
        
        # Tìm tin nhắn birthday gốc để cập nhật
        try:
            found_message = False
            async for message in interaction.channel.history(limit=100):
                if (message.author == interaction.client.user and 
                    message.embeds and 
                    len(message.embeds) > 0 and
                    message.embeds[0].description and
                    "Your Birthday" in str(message.embeds[0].description)):
                    # Kiểm tra xem đây có phải tin nhắn birthday của user hiện tại không
                    if (message.embeds[0].thumbnail and str(target_user.id) in str(message.embeds[0].thumbnail.url)) or \
                       (hasattr(message, 'components') and message.components):
                        print(f"Tìm thấy message birthday để cập nhật sau khi xóa cho user {target_user.id}")
                        await message.edit(embed=embed, view=view)
                        found_message = True
                        break
            
            if not found_message:
                print(f"Không tìm thấy message birthday cũ để cập nhật sau khi xóa")
                        
        except Exception as e:
            print(f"Lỗi cập nhật embed birthday: {e}")

    @discord.ui.button(label="", style=discord.ButtonStyle.grey, emoji=f"{sinhnhat_emoji.xoa_sn}")
    async def confirm_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{list_emoji.tick_check} Bạn không thể thực hiện hành động này!", ephemeral=True)
            return
        
        # Xóa sinh nhật
        cursor.execute("UPDATE profiles SET birthday = NULL WHERE user_id = ?", (self.user_id,))
        conn.commit()
        
        await interaction.response.edit_message(
            content=f"{list_emoji.tickdung} Đã xóa thông tin sinh nhật của bạn!",
            view=None
        )
        
        # Cập nhật embed birthday
        await self.update_birthday_embed(interaction)

    @discord.ui.button(label="", style=discord.ButtonStyle.gray, emoji=f"{list_emoji.tick_check}")
    async def cancel_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{list_emoji.tick_check} Bạn không thể thực hiện hành động này!", ephemeral=True)
            return
        
        await interaction.response.edit_message(
            content="Đã hủy xóa sinh nhật.",
            view=None
        )

class BirthdayView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=180)
        self.user_id = user_id

    @discord.ui.button(emoji=f"{sinhnhat_emoji.lich_sn}", label="", style=discord.ButtonStyle.grey)
    async def set_birthday(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = BirthdaySetModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(emoji=f"{sinhnhat_emoji.next_sn}", label="", style=discord.ButtonStyle.grey)
    async def birthday_list(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Lấy danh sách 10 người có sinh nhật gần nhất
        timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        today_dt = datetime.now(timezone)
        
        cursor.execute("""
            SELECT user_id, birthday FROM profiles 
            WHERE birthday IS NOT NULL AND birthday != ''
        """)
        
        birthdays = cursor.fetchall()
        upcoming_birthdays = []
        
        for user_id, birthday_str in birthdays:
            try:
                birthday_date = datetime.strptime(birthday_str, "%d/%m/%Y")
                next_bd_dt, days_until = compute_next_birthday(birthday_date)
                upcoming_birthdays.append((user_id, birthday_str, days_until, next_bd_dt))
            except ValueError:
                continue
        
        # Sắp xếp theo ngày gần nhất
        upcoming_birthdays.sort(key=lambda x: x[2])
        
        if not upcoming_birthdays:
            await interaction.response.send_message("Chưa có ai thiết lập sinh nhật!", ephemeral=True)
            return
        
        # Nhóm người có cùng ngày sinh nhật và lấy tối đa 10 entries
        grouped_birthdays = []
        current_day = None
        current_group = []
        
        for user_id, birthday_str, days_until, birthday_date in upcoming_birthdays:
            if current_day != days_until:
                if current_group:
                    grouped_birthdays.append((current_day, current_group))
                current_day = days_until
                current_group = [(user_id, birthday_str, birthday_date)]
            else:
                current_group.append((user_id, birthday_str, birthday_date))
        
        if current_group:
            grouped_birthdays.append((current_day, current_group))
        
        embed = discord.Embed(
            title=f"",
            color=0xFF89FA,
            description=f"# {sinhnhat_emoji.lich_sn2} Sinh nhật sắp tới  {sinhnhat_emoji.lich_sn2}"
        )
        
        birthday_list_text = ""
        entry_count = 0
        
        for days_until, group in grouped_birthdays:
            if entry_count >= 10:
                break
                
            # Tạo status message cho nhóm
            if days_until == 0:
                status = f"{sinhnhat_emoji.muiten_sn} **HÔM NAY!**"
            elif days_until == 1:
                status = f"{sinhnhat_emoji.muiten_sn} **Ngày mai**"
            else:
                # Lấy ngày từ người đầu tiên trong nhóm
                sample_date = datetime.strptime(group[0][1], "%d/%m/%Y")
                next_bd_dt, _ = compute_next_birthday(sample_date)
                vietnamese_weekday = get_vietnamese_weekday(next_bd_dt.strftime('%A'))
                status = f"{sinhnhat_emoji.muiten_sn} {vietnamese_weekday}, {next_bd_dt.strftime('%d-%m-%Y')} • còn **{days_until}** ngày"
            
            # Hiển thị tất cả người trong cùng ngày
            for user_id, birthday_str, birthday_date in group:
                if entry_count >= 10:
                    break
                    
                try:
                    user = interaction.client.get_user(user_id) or await interaction.client.fetch_user(user_id)
                    username = user.mention if user else f"User {user_id}"
                    
                    entry_count += 1
                    birthday_list_text += f"`{entry_count:2d}.` {username}\n"
                    birthday_list_text += f"      {birthday_str} {status}\n\n"
                except:
                    continue
        
        embed.description = birthday_list_text
        
        # Footer
        timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        current_time = datetime.now(timezone).strftime("%H:%M:%S")
        embed.set_footer(
            text=f"𝑯𝒂̣𝒕 𝒈𝒊𝒐̂́𝒏𝒈 𝒕𝒂̂𝒎 𝒕𝒉𝒂̂̀𝒏 • {current_time}",
            icon_url=interaction.guild.icon.url if interaction.guild and interaction.guild.icon else None
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=False)

    @discord.ui.button(emoji=f"{sinhnhat_emoji.xoa_sn}", label="", style=discord.ButtonStyle.grey)
    async def delete_birthday(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(f"{list_emoji.tick_check} Bạn chỉ có thể xóa sinh nhật của chính mình!", ephemeral=True)
            return
        
        # Kiểm tra xem có sinh nhật để xóa không
        cursor.execute("SELECT birthday FROM profiles WHERE user_id = ?", (self.user_id,))
        result = cursor.fetchone()
        
        if not result or not result[0]:
            await interaction.response.send_message(f"{list_emoji.tick_check} Bạn chưa thiết lập sinh nhật!", ephemeral=True)
            return
        
        view = BirthdayDeleteConfirmView(self.user_id)
        await interaction.response.send_message(
            f"{sinhnhat_emoji.xoa_sn} Bạn có chắc muốn xoá thiết lập sinh nhật này không?",
            view=view,
            ephemeral=True
        )

class Birthday(commands.Cog):
    def __init__(self, client):
        self.client = client
        # Khởi động task kiểm tra sinh nhật
        self.birthday_check.start()
    #     self.debug_task.start()  # Task debug

    # @tasks.loop(seconds=30)  # Debug task chạy mỗi 30 giây
    # async def debug_task(self):
    #     """Debug task để kiểm tra xem task có chạy không"""
    #     try:
    #         vietnam_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
    #         vietnam_now = datetime.now(vietnam_timezone)
    #         print(f"[DEBUG] Task đang chạy: {vietnam_now.strftime('%H:%M:%S')} (GMT+7)")
    #     except Exception as e:
    #         print(f"[DEBUG] Lỗi trong debug task: {e}")

    # @debug_task.error
    # async def debug_task_error(self, error):
    #     """Error handler cho debug task"""
    #     print(f"[DEBUG] Task gặp lỗi: {error}")

    # @debug_task.before_loop
    # async def before_debug_task(self):
    #     """Đợi bot sẵn sàng trước khi chạy debug task"""
    #     await self.client.wait_until_ready()
    #     print("[DEBUG] Debug task đã khởi động!")

    async def check_command_disabled(self, ctx):
        """Kiểm tra lệnh có bị vô hiệu hóa không"""
        try:
            with open('toggle.json', 'r', encoding='utf-8') as f:
                toggle_data = json.load(f)
                guild_id = str(ctx.guild.id)
                if guild_id in toggle_data and not toggle_data[guild_id].get('birthday', True):
                    return True
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return False

    @commands.command(aliases=["testbirthday", "testbd"], description="Test birthday check manually (owner only)")
    @is_bot_owner()
    async def test_birthday_check(self, ctx):
        """Test birthday check manually"""
        await ctx.send("🔄 Đang kiểm tra sinh nhật thủ công...")
        await self.birthday_check()
        await ctx.send("✅ Hoàn thành kiểm tra sinh nhật!")

    @commands.command(aliases=["sinhnhat", "sn"], description="Xem sinh nhật của bản thân hoặc người khác")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def birthday(self, ctx, member: discord.Member = None):
        """Lệnh xem sinh nhật"""
        if await self.check_command_disabled(ctx):
            return
        
        target_user = member or ctx.author
        user_id = target_user.id
        
        # Đảm bảo user tồn tại
        ensure_user_exists(user_id)
        
        # Lấy thông tin sinh nhật
        cursor.execute("SELECT birthday FROM profiles WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        birthday_str = result[0] if result and result[0] else None
        
        # Tạo embed
        embed = discord.Embed(title=f"", description=f"# {sinhnhat_emoji.lich_sn} Your Birthday {sinhnhat_emoji.lich_sn}", color=0xFF89FA)
        # embed.add_field(name=f"{sinhnhat_emoji.lich_sn} Your Birthday {sinhnhat_emoji.banh_sn}", value="", inline=False)
        embed.set_thumbnail(url=target_user.display_avatar.url)
        
        if birthday_str:
            try:
                birthday_date = datetime.strptime(birthday_str, "%d/%m/%Y")
                next_birthday_dt, days_until = compute_next_birthday(birthday_date)

                if days_until == 0:
                    next_text = "**HÔM NAY!** "
                elif days_until == 1:
                    next_text = "**Ngày mai** "
                else:
                    vietnamese_weekday = get_vietnamese_weekday(next_birthday_dt.strftime('%A'))
                    next_text = f"{vietnamese_weekday}, {next_birthday_dt.strftime('%d-%m-%Y')} (còn {days_until} ngày)"

                birthday_text = f"{sinhnhat_emoji.nhay_sn} **Date:** **`{birthday_str}`**\n"
                # Chỉ hiển thị "Next:" khi không phải hôm nay
                if days_until == 0:
                    birthday_text += f"{sinhnhat_emoji.nhay_sn} {next_text}"
                else:
                    birthday_text += f"{sinhnhat_emoji.nhay_sn} **Next: {next_text}**"

            except ValueError:
                birthday_text = f"{sinhnhat_emoji.nhay_sn} **Date:** **`{birthday_str}`**\n"
                birthday_text += f"{sinhnhat_emoji.nhay_sn} **Next:** Không xác định được"
        else:
            birthday_text = f"{sinhnhat_emoji.nhay_sn} Chưa thiết lập sinh nhật\n"
            birthday_text += f"{sinhnhat_emoji.nhay_sn} Hãy bấm nút bên dưới để thiết lập!"

        embed.add_field(name="", value=birthday_text, inline=False)
        
        # Footer
        timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        current_time = datetime.now(timezone).strftime("%H:%M:%S")
        footer_text = f"𝑯𝒂̣𝒕 𝒈𝒊𝒐̂́𝒏𝒈 𝒕𝒂̂𝒎 𝒕𝒉𝒂̂̀𝒏 • {current_time}"
        
        if ctx.guild and ctx.guild.icon:
            embed.set_footer(text=footer_text, icon_url=ctx.guild.icon.url)
        else:
            embed.set_footer(text=footer_text)
        
        # Chỉ hiện view nếu xem sinh nhật của chính mình
        if target_user == ctx.author:
            view = BirthdayView(user_id)
            await ctx.send(embed=embed, view=view)
        else:
            await ctx.send(embed=embed)

    @tasks.loop(minutes=1)  # Chạy mỗi phút để test
    async def birthday_check(self):
        """Task kiểm tra sinh nhật hàng ngày"""
        # Sử dụng múi giờ Việt Nam
        vietnam_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        vietnam_now = datetime.now(vietnam_timezone)
        
        # print(f"[BIRTHDAY CHECK] Task chạy lúc: {vietnam_now.strftime('%H:%M:%S')} (GMT+7)")

        # Chỉ chạy vào 00:00 mỗi ngày 
        if vietnam_now.hour != 0 or vietnam_now.minute != 0:
            # print(f"[BIRTHDAY CHECK] Chưa tới giờ check (hiện tại: {vietnam_now.hour}:{vietnam_now.minute:02d})")
            return
        
        print(f"[BIRTHDAY CHECK] Bắt đầu kiểm tra sinh nhật lúc {vietnam_now.strftime('%H:%M:%S')} (GMT+7)")
        try:
            # Tạo kết nối database riêng cho task
            today_str = vietnam_now.strftime("%d/%m")  # DD/MM format
            print(f"[BIRTHDAY CHECK] Ngày hôm nay: {today_str} (GMT+7)")
            
            # Tìm những người có sinh nhật hôm nay - Debug thêm thông tin
            cursor.execute("""
                SELECT user_id, birthday FROM profiles 
                WHERE birthday IS NOT NULL 
                AND birthday != '' 
                AND substr(birthday, 1, 5) = ?
            """, (today_str,))
            
            birthday_users = cursor.fetchall()
            print(f"[BIRTHDAY CHECK] Tìm thấy {len(birthday_users)} người có sinh nhật hôm nay")
            
            # Debug: In ra tất cả sinh nhật trong database để kiểm tra
            cursor.execute("""
                SELECT user_id, birthday FROM profiles 
                WHERE birthday IS NOT NULL 
                AND birthday != ''
            """)
            all_birthdays = cursor.fetchall()
            print(f"[BIRTHDAY CHECK] DEBUG - Tất cả sinh nhật trong DB:")
            for uid, bd in all_birthdays:
                print(f"  User {uid}: {bd} (first 5 chars: '{bd[:5] if bd else 'None'}')")
            
            print(f"[BIRTHDAY CHECK] DEBUG - Tìm kiếm pattern: '{today_str}'")
            
            if not birthday_users:
                print("[BIRTHDAY CHECK] Không có ai có sinh nhật hôm nay")
                return
            
            # Duyệt qua tất cả các guild để gửi thông báo sinh nhật
            for guild in self.client.guilds:
                # Tìm kênh để gửi thông báo - CHỈ gửi đến BIRTHDAY_CHANNELID
                channel = None
                
                # Chỉ tìm channel theo ID đã cấu hình trước
                if BIRTHDAY_CHANNELID:
                    channel = guild.get_channel(BIRTHDAY_CHANNELID)
                    if not channel:
                        print(f"[BIRTHDAY CHECK] Không tìm thấy channel {BIRTHDAY_CHANNELID} trong guild {guild.name}")
                        continue
                    if not channel.permissions_for(guild.me).send_messages:
                        print(f"[BIRTHDAY CHECK] Không có quyền gửi tin nhắn trong channel {channel.name} (guild: {guild.name})")
                        continue
                else:
                    print(f"[BIRTHDAY CHECK] BIRTHDAY_CHANNELID chưa được cấu hình")
                    continue
                
                # Kiểm tra xem có ai trong guild có sinh nhật hôm nay không
                guild_birthday_count = 0
                for user_id, birthday_str in birthday_users:
                    try:
                        member = guild.get_member(user_id)
                        if not member:
                            print(f"[BIRTHDAY CHECK] User {user_id} không có trong guild {guild.name}")
                            continue
                        
                        guild_birthday_count += 1
                        print(f"[BIRTHDAY CHECK] Gửi thông báo sinh nhật cho {member.name} trong guild {guild.name}")
                        
                        # Tạo embed sinh nhật
                        embed = discord.Embed(color=0xFF89FA)
                        # Sử dụng avatar của member, nếu không có thì dùng default_avatar.png từ project
                        if member.avatar:
                            avatar_url = member.avatar.url
                        else:
                            # Sử dụng default_avatar.png từ project thay vì Discord default
                            avatar_url = "attachment://default_avatar.png"
                        
                        # Đặt title và thumbnail thay vì set_author
                        embed.description = f"{sinhnhat_emoji.phaohoa_sn} 𝑯𝒂𝒑𝒑𝒚 𝑩𝒊𝒓𝒕𝒉𝒅𝒂𝒚 {sinhnhat_emoji.phaohoa_sn}"
                        embed.set_thumbnail(url=avatar_url)
                        
                        embed.add_field(
                            name="",
                            value=f"{sinhnhat_emoji.banh_sn} **Hôm nay là sinh nhật của {member.mention}**",
                            inline=False
                        )
                        
                        # Random message
                        random_message = random.choice(BIRTHDAY_MESSAGES)
                        embed.add_field(
                            name="",
                            value=random_message,
                            inline=False
                        )
                        
                        # Footer với avatar server
                        embed.set_footer(
                            text="𝑭𝒓𝒐𝒎 𝑯𝒂̣𝒕 𝒈𝒊𝒐̂́𝒏𝒈 𝒕𝒂̂𝒎 𝒕𝒉𝒂̂̀𝒏",
                            icon_url=guild.icon.url if guild.icon else None
                        )
                        
                        context = f"{sinhnhat_emoji.tuoi_sn} **Cùng nhau gửi lời chúc mừng sinh nhật đến {member.mention} nha**"
                        
                        # Gửi embed với file attachment nếu cần
                        if member.avatar:
                            # Có avatar, gửi bình thường
                            await channel.send(content=context, embed=embed)
                        else:
                            # Không có avatar, gửi kèm default_avatar.png
                            file = discord.File("default_avatar.png", filename="default_avatar.png")
                            await channel.send(content=context, embed=embed, file=file)
                        print(f"[BIRTHDAY CHECK] ✅ Đã gửi thành công thông báo sinh nhật cho {member.name} trong channel {channel.name}")
                        
                    except Exception as e:
                        print(f"[BIRTHDAY CHECK] ❌ Lỗi gửi thông báo sinh nhật cho {user_id}: {e}")
                        continue
                
                if guild_birthday_count == 0:
                    print(f"[BIRTHDAY CHECK] Không có thành viên nào có sinh nhật hôm nay trong guild {guild.name}")
                        
        except Exception as e:
            print(f"[BIRTHDAY CHECK] ❌ Lỗi task kiểm tra sinh nhật: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"[BIRTHDAY CHECK] Kết thúc kiểm tra sinh nhật lúc {vietnam_now.strftime('%H:%M:%S')} (GMT+7)")

    @birthday_check.before_loop
    async def before_birthday_check(self):
        """Đợi bot sẵn sàng trước khi chạy task"""
        await self.client.wait_until_ready()

    @birthday_check.error
    async def birthday_check_error(self, error):
        """Error handler cho birthday check task"""
        print(f"[BIRTHDAY CHECK] Task gặp lỗi: {error}")
        import traceback
        traceback.print_exc()

    @birthday.error
    async def birthday_error(self, ctx, error):
        """Xử lý lỗi lệnh birthday"""
        if isinstance(error, commands.CommandOnCooldown):
            em = discord.Embed(
                description=f"{list_emoji.tick_check} Bạn đang sử dụng lệnh quá nhanh! Vui lòng thử lại sau **{error.retry_after:.1f}s**",
                color=0xFF89FA
            )
            await ctx.send(embed=em, delete_after=error.retry_after)
        else:
            print(f"Lỗi lệnh birthday: {error}")

    def cog_unload(self):
        """Dừng task khi unload cog"""
        self.birthday_check.cancel()
        # self.debug_task.cancel()

async def setup(client):
    await client.add_cog(Birthday(client))
