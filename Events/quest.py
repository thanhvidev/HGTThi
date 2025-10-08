import asyncio
import discord
import sqlite3
import random
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from Commands.Mod.list_emoji import list_emoji
from utils.checks import is_bot_owner, is_admin, is_mod
import json

import pytz

# Kết nối và tạo bảng trong SQLite
conn = sqlite3.connect('economy.db', isolation_level=None)
conn.execute('pragma journal_mode=wal')
cursor = conn.cursor()

import logging
logger = logging.getLogger(__name__)

def ensure_data_consistency():
    """Đảm bảo đọc dữ liệu mới nhất từ database"""
    conn.execute('BEGIN IMMEDIATE;')
    conn.execute('COMMIT;')


def format_number(num):  
    if num >= 1000:  
        return f"{num//1000}k"  
    return str(num) 

def number_to_superscript(num):
    """Chuyển đổi số thành dạng superscript"""
    superscript_map = {
        '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
        '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'
    }
    return ''.join(superscript_map.get(digit, digit) for digit in str(num))

def validate_and_fix_quest_data(quest_data_str, user_id):
    """Kiểm tra và sửa quest data nếu có thể"""
    if not quest_data_str:
        return None
    
    try:
        # Thử parse JSON
        quest_dict = json.loads(quest_data_str)
        return quest_dict
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Quest data validation failed for user {user_id}: {e}")
        logger.error(f"Raw data: {repr(quest_data_str)}")
        
        # Thử một số fix cơ bản
        try:
            # Fix single quotes thành double quotes
            fixed_data = quest_data_str.replace("'", '"')
            quest_dict = json.loads(fixed_data)
            logger.info(f"Fixed quest data for user {user_id} by replacing single quotes")
            return quest_dict
        except:
            # Nếu không sửa được, return None để reset
            logger.error(f"Cannot fix quest data for user {user_id}, will reset")
            return None

def generate_random_combo_rewards():
    """Tạo phần thưởng combo ngẫu nhiên với tổng = 10"""
    # Đảm bảo mỗi loại ít nhất 1, còn lại 7 để phân phối
    base_amounts = {"bột": 1, "đậu xanh": 1, "trứng muối": 1}
    remaining = 7
    
    # Random phân phối 7 còn lại
    for i, item in enumerate(base_amounts.keys()):
        if i == 2:  # Item cuối cùng nhận hết số còn lại
            base_amounts[item] += remaining
        else:
            # Random từ 0 đến remaining
            add_amount = random.randint(0, remaining)
            base_amounts[item] += add_amount
            remaining -= add_amount
    
    # Tạo dict với emoji
    rewards = {
        "bột": {"emoji": "<:bot:1416358091884335174>", "so_luong": base_amounts["bột"]},
        "đậu xanh": {"emoji": "<:dauxanh:1416358140685058208>", "so_luong": base_amounts["đậu xanh"]},
        "trứng muối": {"emoji": "<:trungmuoi:1416358111438045334>", "so_luong": base_amounts["trứng muối"]},
    }
    return rewards

bot = "<:lambanh_bot:1416358091884335174>"
dauxanh = "<:lambanh_dauxanh:1416358140685058208>"
trungmuoi = "<:lambanh_trungmuoi:1416358111438045334>"
trang2 = "<:quest_muiten1:1419171264458653726>"
trang1 = "<:quest_muiten2:1419171265968734308>"


def is_registered(user_id):
    cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None

def is_daily_channel():
    async def predicate(ctx):
        allowed_channel_ids = [1147355133622108262, 1026627301573677147, 1035183712582766673, 1090897131486842990, 1213122881802997770]
        if ctx.channel.id not in allowed_channel_ids:
            await ctx.send(f"{list_emoji.tick_check} **Dùng lệnh** **`zquest`** [__**ở đây**__](<https://discord.com/channels/832579380634451969/1147355133622108262>)")
            return False
        return True
    return commands.check(predicate)

def format_number(num):  
    if num >= 1000:  
        return f"{num // 1000}k"  
    return str(num) 

NOTIFY_CHANNEL_ID = 993153068378116127  # Thay đổi thành ID kênh bạn muốn gửi thông báo

quest = "<:scroll:1245071210157576252>"
tickxanh = "<a:tickdung:1418226478558089336>"
lich = "<:quest_so:1362252580868194304>"
questso1 = "<:so17mau:1418605628691316866>"
questso2 = "<:so27mau:1418605640800145588>"
questso3 = "<:so37mau:1418605651570987018>"

bongden = "<:quest7mau:1418605661377527878>"
cham = "<:muiten_quest:1362254110383931493>"
cham1 = "<:muiten_quest:1362254110383931493>"
dauxdo = "<a:hgtt_check:1246910030444495008>"
benphai = "<:quest7mau:1418605661377527878>"
pre = "<:muitenhong_trai:1339301198104100915>"
nex = "<:muitenhong_phai:1339301206752755875>"


class QuestView(discord.ui.View):
    def __init__(self, enable_buttons, quest_data, timeout: float = 180.0):
        super().__init__(timeout=timeout)
        self.enable_buttons = enable_buttons
        self.quest_data = quest_data
        self.page = 1  # Trang hiện tại

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.enable_buttons:
            return True
        else:
            await interaction.response.send_message("Bạn không thể sử dụng nút này.", ephemeral=True)
            return False

    @discord.ui.button(label="", emoji=f"{trang1}", style=discord.ButtonStyle.grey)
    async def page_one(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = 1
        await self.update_embed(interaction)

    @discord.ui.button(label="", emoji=f"{trang2}", style=discord.ButtonStyle.grey)
    async def page_two(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = 2
        await self.update_embed(interaction)

    async def update_embed(self, interaction: discord.Interaction):
        cursor.execute("SELECT user_id, quest, quest_time, quest_mess, quest_image, quest_done, quest_CASINO, quest_GIAITRI, quest_PRAY, quest_done2, balance FROM users WHERE user_id = ?", (interaction.user.id,))
        result = cursor.fetchone()
        if not result:
            return
        user_id, quest, quest_time, quest_mess, quest_image, quest_done, quest_CASINO, quest_GIAITRI, quest_PRAY, quest_done2, balance = result
        # Giải mã quest từ chuỗi JSON

        quest_dict = self.quest_data
        # quest_dict = json.loads(quest)
        is_time_completed = quest_time >= quest_dict.get('voice_time', 0)
        is_mess_completed = quest_mess >= quest_dict.get('messages', 0)
        is_image_completed = quest_image >= quest_dict.get('image', 0)
        is_casino_completed = quest_CASINO >= quest_dict.get('casino_times', 0)
        is_giaitri_completed = quest_GIAITRI >= quest_dict.get('giaitri_times', 0)
        is_pray_completed = quest_PRAY >= quest_dict.get('pray_times', 0)
        embed = discord.Embed(title="", color=discord.Color.from_rgb(255, 255, 255))
        if interaction.user.avatar:
            avatar_url = interaction.user.avatar.url
        else:
            avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
        embed.set_author(name=f"{interaction.user.display_name}'s daily quest", icon_url=avatar_url)
        if self.page == 1:
            # Trang 1: Nhiệm vụ chat, treo voice, gửi ảnh
            embed.add_field(
                name="", 
                value=f"{questso1} **Chat** __**{quest_dict.get('messages', 0)} tin**__ tại [__**sảnh chat**__](<https://discord.com/channels/832579380634451969/{quest_dict.get('message_channel', 0)}>)\n-# {list_emoji.trong}`‣ Tiến độ:` **{quest_mess}/{quest_dict.get('messages', 0)}**\n-# {list_emoji.trong}`‣ Thưởng :` **{format_number(quest_dict.get('balance_mess', 0))} {list_emoji.pinkcoin} + {quest_dict.get('mess_noel', 0)} {list_emoji.xu_event}**" if not is_mess_completed else f"{questso1} **Chat** __**{quest_dict.get('messages', 0)} tin**__ tại [__**sảnh chat**__](<https://discord.com/channels/832579380634451969/{quest_dict.get('message_channel', 0)}>)\n-# {list_emoji.trong}`‣ Tiến độ:` {tickxanh}\n-# {list_emoji.trong}`‣ Thưởng :` **{format_number(quest_dict.get('balance_mess', 0))} {list_emoji.pinkcoin} + {quest_dict.get('mess_noel', 0)} {list_emoji.xu_event}**",
                inline=False
            )
            embed.add_field(
                name="",
                value=f"{questso2} **Treo voice** __**{quest_dict.get('voice_time', 0)}h**__\n-# {list_emoji.trong}`‣ Tiến độ:` **{quest_time}/{quest_dict.get('voice_time', 0)}**\n-# {list_emoji.trong}`‣ Thưởng :` **{format_number(quest_dict.get('balance_voice', 0))} {list_emoji.pinkcoin} + {quest_dict.get('voice_noel', 0)} {list_emoji.xu_event}**" if not is_time_completed else f"{questso2} **Treo voice** __**{quest_dict.get('voice_time', 0)}h**__\n-# {list_emoji.trong}`‣ Tiến độ:` {tickxanh} \n-# {list_emoji.trong}`‣ Thưởng :` **{format_number(quest_dict.get('balance_voice', 0))} {list_emoji.pinkcoin} + {quest_dict.get('voice_noel', 0)} {list_emoji.xu_event}**",
                inline=False
            )
            if quest_dict.get('message_image', 0) == 1052625475769471127:
                embed.add_field(
                    name="",
                    value=f"{questso3} **Gửi một ảnh meme vào** [__**đây**__](<https://discord.com/channels/832579380634451969/1052625475769471127>)"if not is_image_completed else f"{questso3} **Gửi một ảnh meme vào** [__**đây**__](<https://discord.com/channels/832579380634451969/1052625475769471127>) {tickxanh}",
                    inline=False
                )
            elif quest_dict.get('message_image', 0) == 1021646306567016498:
                embed.add_field(
                    name="",
                    value=f"{questso3} **Gửi một ảnh đồ ăn vào** [__**đây**__](<https://discord.com/channels/832579380634451969/1021646306567016498>)"if not is_image_completed else f"{questso3} **Gửi một ảnh đồ ăn vào** [__**đây**__](<https://discord.com/channels/832579380634451969/1021646306567016498>) {tickxanh}",
                    inline=False)
            embed.add_field(name="", value=f"-# {benphai} Hoàn thành cả ba + **1 {list_emoji.xu_event} & 1 combo x10**\n-# {benphai} Voice nhớ out ra vào lại, kh tắt loa", inline=False)

        elif self.page == 2:
            # Trang 2: Nhiệm vụ casino, giải trí, pray
            embed.add_field(
                name="",
                value=f"{questso1} **Chơi** [__**casino**__](<https://discord.com/channels/832579380634451969/1273768834830041301>) __**{quest_dict.get('casino_times', 0)} lần**__\n-# {list_emoji.trong}`‣ Tiến độ:` **{quest_CASINO}/{quest_dict.get('casino_times', 0)}**\n-# {list_emoji.trong}`‣ Thưởng :` **{format_number(quest_dict.get('casino_xu', 0))} {list_emoji.pinkcoin}**" if not is_casino_completed else f"{questso1} **Chơi** [__**casino**__](<https://discord.com/channels/832579380634451969/1273768834830041301>) __**{quest_dict.get('casino_times', 0)} lần**__\n-# {list_emoji.trong}`‣ Tiến độ:` {tickxanh} \n-# {list_emoji.trong}`‣ Thưởng :` **{format_number(quest_dict.get('casino_xu', 0))} {list_emoji.pinkcoin}**",
                inline=False
            )
            embed.add_field(
                name="",
                value=f"{questso2} **Chơi** [__**giải trí**__](<https://discord.com/channels/832579380634451969/1273769137985818624>) __**{quest_dict.get('giaitri_times', 0)} lần**__\n-# {list_emoji.trong}`‣ Tiến độ:` **{quest_GIAITRI}/{quest_dict.get('giaitri_times', 0)}**\n-# {list_emoji.trong}`‣ Thưởng :` **{format_number(quest_dict.get('giaitri_xu', 0))} {list_emoji.pinkcoin}**" if not is_giaitri_completed else f"{questso2} **Chơi** [__**giải trí**__](<https://discord.com/channels/832579380634451969/1273769137985818624>) __**{quest_dict.get('giaitri_times', 0)} lần**__\n-# {list_emoji.trong}`‣ Tiến độ:` {tickxanh} \n-# {list_emoji.trong}`‣ Thưởng :` **{format_number(quest_dict.get('giaitri_xu', 0))} {list_emoji.pinkcoin}**",
                inline=False
            )

            if quest_dict.get('pray_choice', 0) == 'zpray':
                embed.add_field(
                    name="",
                    value=f"{questso3} [__**zpray**__](<https://discord.com/channels/832579380634451969/1273768834830041301>) __**{quest_dict.get('pray_times', 0)} lần**__\n-# {list_emoji.trong}`‣ Tiến độ:` **{quest_PRAY}/{quest_dict.get('pray_times', 0)}**\n-# {list_emoji.trong}`‣ Thưởng :` **{format_number(quest_dict.get('pray_xu', 0))} {list_emoji.pinkcoin}**" if not is_pray_completed else f"{questso3} [__**zpray**__](<https://discord.com/channels/832579380634451969/1273768834830041301>) __**{quest_dict.get('pray_times', 0)} lần**__\n-# {list_emoji.trong}`‣ Tiến độ:` {tickxanh} \n-# {list_emoji.trong}`‣ Thưởng :` **{format_number(quest_dict.get('pray_xu', 0))} {list_emoji.pinkcoin}**",
                    inline=False
                )
            # if quest_dict.get('pray_choice', 0) == 'zlove':
            #     embed.add_field(
            #         name="",
            #         value=f"{questso3} [__**zlove**__](<https://discord.com/channels/832579380634451969/1273768834830041301>) __**{quest_dict.get('pray_times', 0)} lần**__\n-# {list_emoji.trong}`‣ Tiến độ:` **{quest_PRAY}/{quest_dict.get('pray_times', 0)}**\n-# {list_emoji.trong}`‣ Thưởng :` **{format_number(quest_dict.get('pray_xu', 0))} {list_emoji.pinkcoin}**" if not is_pray_completed else f"{questso3} [__**zlove**__](<https://discord.com/channels/832579380634451969/1273768834830041301>) __**{quest_dict.get('pray_times', 0)} lần**__\n-# {list_emoji.trong}`‣ Tiến độ:` {tickxanh} \n-# {list_emoji.trong}`‣ Thưởng :` **{format_number(quest_dict.get('pray_xu', 0))} {list_emoji.pinkcoin}**",
            #         inline=False
            #     )
            embed.add_field(name="", value=f"-# {benphai} Hoàn thành cả ba + **1 {list_emoji.xu_event}**\n-# {benphai} Voice nhớ out ra vào lại, kh tắt loa", inline=False)
        icon_url = interaction.guild.icon.url if interaction.guild.icon else None
        embed.set_footer(text="Quests reset at 14:00 every day.", icon_url=icon_url)
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        # Cập nhật lại tin nhắn để hiển thị nút đã bị vô hiệu hóa
        # Giả sử bạn có lưu trữ interaction hoặc message để cập nhật lại
        # await self.message.edit(view=self)  # Cập nhật lại tin nhắn với view đã bị vô hiệu hóa


class Quest(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.voice_times = {}
        self.update_voice_time.start() 
        self.quest_reset.start()

    async def check_command_disabled(self, ctx):  
        guild_id = str(ctx.guild.id)  
        command_name = ctx.command.name.lower()  
        if guild_id in self.client.get_cog('Toggle').toggles:  
            if command_name in self.client.get_cog('Toggle').toggles[guild_id]:  
                if ctx.channel.id in self.client.get_cog('Toggle').toggles[guild_id][command_name]:  
                    await ctx.send(f"Lệnh `{command_name}` đã bị tắt ở kênh này.")  
                    return True  
        return False 

    @commands.Cog.listener()
    async def on_message(self, message):
        user_id = message.author.id
        # logger.info(f"Processing message from user {user_id} in channel {message.channel.id}")
        if not is_registered(user_id):
            # logger.info(f"User {user_id} not registered, skipping quest processing")
            return
        ensure_data_consistency()
        cursor.execute("SELECT quest, quest_mess, quest_image, quest_CASINO, quest_GIAITRI, quest_PRAY FROM users WHERE user_id = ?", (user_id,))
        quest_data = cursor.fetchone()
        if quest_data:
            quest, quest_mess, quest_image, quest_CASINO, quest_GIAITRI, quest_PRAY = quest_data
            if quest:
                try:
                    quest_dict = json.loads(quest)
                except (json.JSONDecodeError, ValueError) as e:
                    # logger.error(f"Invalid quest data for user {user_id} in on_message: {e}")
                    logger.error(f"Raw quest data: {repr(quest)}")
                    # Reset quest data nếu bị lỗi
                    cursor.execute("UPDATE users SET quest = '' WHERE user_id = ?", (user_id,))
                    conn.execute('PRAGMA wal_checkpoint;')
                    logger.info(f"Reset corrupted quest data for user {user_id}")
                    return
                if message.channel.id in {quest_dict.get('message_image', 0)}: 
                    if message.attachments: 
                        if all(att.content_type and att.content_type.startswith("image/") for att in message.attachments):
                            # Kiểm tra xem đã hoàn thành chưa (tránh spam thông báo)  
                            cursor.execute("SELECT quest_image FROM users WHERE user_id = ?", (user_id,))
                            current_image = cursor.fetchone()
                            if current_image and current_image[0] == 0:  # Chỉ cập nhật nếu chưa hoàn thành
                                cursor.execute("UPDATE users SET quest_image = 1 WHERE user_id = ?", (user_id,))
                                conn.execute('PRAGMA wal_checkpoint;')
                                logger.info(f"User {user_id} completed image quest")
                                # Thông báo real-time cho nhiệm vụ image
                                await self.notify_completion(user_id, 0, "image", "1 ảnh", quest_dict.get('img_xu', 0))
                                # Kiểm tra xem có hoàn thành đủ 3 nhiệm vụ chính không
                                await self.check_combo_completion(user_id, quest_dict)
                                # Gọi check_quests để xử lý thưởng
                                await self.check_quests()
                        else:
                            return  
                    else:
                        return 
                elif message.channel.id in {quest_dict.get('message_channel', 0)}:
                    if quest_data and quest_data[0]:
                        cursor.execute("UPDATE users SET quest_mess = quest_mess + 1 WHERE user_id = ?", (user_id,))
                        conn.execute('PRAGMA wal_checkpoint;')
                        # Kiểm tra sau khi update để đảm bảo thông báo chỉ gửi 1 lần khi đạt mục tiêu
                        cursor.execute("SELECT quest_mess FROM users WHERE user_id = ?", (user_id,))
                        updated_mess = cursor.fetchone()[0]
                        if updated_mess == quest_dict.get('messages', 0):  # Chỉ thông báo khi vừa đạt mục tiêu
                            logger.info(f"User {user_id} completed message quest: {updated_mess}/{quest_dict.get('messages', 0)}")
                            # Thông báo real-time cho nhiệm vụ message
                            await self.notify_completion(user_id, quest_dict.get('balance_mess', 0), "messages", quest_dict.get('messages', 0), quest_dict.get('mess_noel', 0))
                            # Kiểm tra xem có hoàn thành đủ 3 nhiệm vụ chính không
                            await self.check_combo_completion(user_id, quest_dict)
                            # Gọi check_quests để xử lý thưởng
                            await self.check_quests()

                # Kiểm tra nếu người chơi sử dụng lệnh zpray hoặc zlove
                elif message.content.lower() in ["zpray", "zpray"]:
                    # Lấy thời gian hiện tại
                    timezone = pytz.timezone('Asia/Ho_Chi_Minh')
                    now = datetime.now(timezone)

                    # Kiểm tra thời gian lần cuối cùng sử dụng lệnh
                    cursor.execute("SELECT last_pray_time FROM users WHERE user_id = ?", (user_id,))
                    last_pray_time = cursor.fetchone()
                    if last_pray_time and last_pray_time[0]:
                        last_pray_time = datetime.strptime(last_pray_time[0], "%Y-%m-%d %H:%M:%S")
                        # Chuyển đổi sang timezone aware
                        last_pray_time = timezone.localize(last_pray_time)
                        time_diff = (now - last_pray_time).total_seconds() / 60  # Tính thời gian cách nhau (phút)
                        if time_diff < 15:  # Nếu dưới 15 phút, không tăng
                            return

                    # Cập nhật số lượng quest_PRAY và thời gian sử dụng lệnh
                    cursor.execute("UPDATE users SET quest_PRAY = quest_PRAY + 1, last_pray_time = ? WHERE user_id = ?", (now.strftime("%Y-%m-%d %H:%M:%S"), user_id))
                    conn.execute('PRAGMA wal_checkpoint;')
                    # Kiểm tra sau khi update để đảm bảo thông báo chỉ gửi 1 lần
                    cursor.execute("SELECT quest_PRAY FROM users WHERE user_id = ?", (user_id,))
                    updated_pray = cursor.fetchone()[0]
                    if updated_pray == quest_dict.get('pray_times', 0):  # Chỉ thông báo khi vừa đạt mục tiêu
                        # Thông báo real-time cho nhiệm vụ pray
                        await self.notify_completion(user_id, quest_dict.get('pray_xu', 0), "pray", quest_dict.get('pray_times', 0), 0)
                        # Kiểm tra xem có hoàn thành đủ 3 nhiệm vụ phụ không
                        await self.check_combo_completion_secondary(user_id, quest_dict)
                        # Gọi check_quests để xử lý thưởng
                        await self.check_quests()

                elif message.channel.id == 1273768834830041301:
                    economy_gamble_commands = ["coinflip", "zcoinflip", "cf", "zcf", "blackjack", "zblackjack", "bj", "zbj", "taixiu", "ztaixiu", "tx", "ztx", "baucua", "zbaucua", "bc", "zbc"]
                    # logger.info(f"User {user_id} sent message in casino channel: '{message.content}'")
                    if any(message.content.lower().startswith(cmd) for cmd in economy_gamble_commands):
                        logger.info(f"User {user_id} used casino command: '{message.content}' - matched commands: {[cmd for cmd in economy_gamble_commands if message.content.lower().startswith(cmd)]}")
                        timezone = pytz.timezone('Asia/Ho_Chi_Minh')
                        now = datetime.now(timezone)
                        cursor.execute("SELECT last_casino_time FROM users WHERE user_id = ?", (user_id,))
                        last_casino_time = cursor.fetchone()
                        if last_casino_time and last_casino_time[0]:
                            last_casino_time = datetime.strptime(last_casino_time[0], "%Y-%m-%d %H:%M:%S")
                            # Chuyển đổi sang timezone aware
                            last_casino_time = timezone.localize(last_casino_time)
                            time_diff = (now - last_casino_time).total_seconds()  # Tính thời gian cách nhau (giây)
                            logger.info(f"User {user_id} casino cooldown check: last_time={last_casino_time}, now={now}, diff={time_diff}s")
                            if time_diff < 30:  # Nếu dưới 30 giây, không tăng
                                logger.info(f"User {user_id} casino command blocked due to cooldown ({time_diff}s < 30s)")
                                return
                        cursor.execute("UPDATE users SET quest_CASINO = quest_CASINO + 1, last_casino_time = ? WHERE user_id = ?", (now.strftime("%Y-%m-%d %H:%M:%S"), user_id))
                        conn.execute('PRAGMA wal_checkpoint;')
                        logger.info(f"User {user_id} quest_CASINO incremented")
                        # Kiểm tra sau khi update để đảm bảo thông báo chỉ gửi 1 lần
                        cursor.execute("SELECT quest_CASINO FROM users WHERE user_id = ?", (user_id,))
                        updated_casino = cursor.fetchone()[0]
                        logger.info(f"User {user_id} quest_CASINO updated to: {updated_casino}/{quest_dict.get('casino_times', 0)}")
                        if updated_casino == quest_dict.get('casino_times', 0):  # Chỉ thông báo khi vừa đạt mục tiêu
                            # Thông báo real-time cho nhiệm vụ casino
                            await self.notify_completion(user_id, quest_dict.get('casino_xu', 0), "casino", quest_dict.get('casino_times', 0), 0)
                            # Kiểm tra xem có hoàn thành đủ 3 nhiệm vụ phụ không
                            await self.check_combo_completion_secondary(user_id, quest_dict)
                            # Gọi check_quests để xử lý thưởng
                            await self.check_quests()

                elif message.channel.id == 1273769137985818624:
                    giaitri_commands = ["keobuabao", "zkeobuabao", "kbb", "zkbb", "vuatiengviet", "zvuatiengviet", "vtv", "zvtv", "vuatv", "zvuatv", "mathquiz", "zmathquiz", "toan", "ztoan", "duoihinhbatchu", "zduoihinhbatchu", "dhbc", "zdhbc"]
                    if any(message.content.lower().startswith(cmd) for cmd in giaitri_commands):
                        timezone = pytz.timezone('Asia/Ho_Chi_Minh')
                        now = datetime.now(timezone)
                        cursor.execute("SELECT last_giaitri_time FROM users WHERE user_id = ?", (user_id,))
                        last_giaitri_time = cursor.fetchone()
                        if last_giaitri_time and last_giaitri_time[0]:
                            last_giaitri_time = datetime.strptime(last_giaitri_time[0], "%Y-%m-%d %H:%M:%S")
                            # Chuyển đổi sang timezone aware
                            last_giaitri_time = timezone.localize(last_giaitri_time)
                            time_diff = (now - last_giaitri_time).total_seconds()  # Tính thời gian cách nhau (giây)
                            if time_diff < 30:  # Nếu dưới 30 giây, không tăng
                                return
                        cursor.execute("UPDATE users SET quest_GIAITRI = quest_GIAITRI + 1, last_giaitri_time = ? WHERE user_id = ?", (now.strftime("%Y-%m-%d %H:%M:%S"), user_id))
                        conn.execute('PRAGMA wal_checkpoint;')
                        # Kiểm tra sau khi update để đảm bảo thông báo chỉ gửi 1 lần
                        cursor.execute("SELECT quest_GIAITRI FROM users WHERE user_id = ?", (user_id,))
                        updated_giaitri = cursor.fetchone()[0]
                        if updated_giaitri == quest_dict.get('giaitri_times', 0):  # Chỉ thông báo khi vừa đạt mục tiêu
                            # Thông báo real-time cho nhiệm vụ giải trí
                            await self.notify_completion(user_id, quest_dict.get('giaitri_xu', 0), "giaitri", quest_dict.get('giaitri_times', 0), 0)
                            # Kiểm tra xem có hoàn thành đủ 3 nhiệm vụ phụ không
                            await self.check_combo_completion_secondary(user_id, quest_dict)
                            # Gọi check_quests để xử lý thưởng
                            await self.check_quests()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        user_id = member.id
        if not is_registered(user_id):
            return

        timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        now = datetime.now(timezone)

        # Nếu người dùng tham gia kênh voice
        if before.channel is None and after.channel is not None:
            self.voice_times[user_id] = now  # Lưu thời gian bắt đầu treo voice

        # Nếu người dùng rời kênh voice
        elif before.channel is not None and after.channel is None:
            if user_id in self.voice_times:
                self.voice_times.pop(user_id)

    @tasks.loop(seconds=60)  # Chạy mỗi phút
    async def update_voice_time(self):
        timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        now = datetime.now(timezone)

        for user_id, join_time in list(self.voice_times.items()):
            time_spent = round((now - join_time).total_seconds() / 3600, 2)  # Tính thời gian treo voice (giờ)
            
            # Cập nhật thời gian treo voice vào cơ sở dữ liệu
            cursor.execute("SELECT quest, quest_time FROM users WHERE user_id = ?", (user_id,))
            quest_data = cursor.fetchone()
            if quest_data:
                quest, quest_time = quest_data
                if quest:
                    try:
                        quest_dict = json.loads(quest)
                    except (json.JSONDecodeError, ValueError) as e:
                        # logger.error(f"Invalid quest data for user {user_id} in update_voice_time: {e}")
                        logger.error(f"Raw quest data: {repr(quest)}")
                        # Reset quest data nếu bị lỗi
                        cursor.execute("UPDATE users SET quest = '' WHERE user_id = ?", (user_id,))
                        conn.execute('PRAGMA wal_checkpoint;')
                        logger.info(f"Reset corrupted quest data for user {user_id}")
                        continue
                else:
                    quest_dict = {}

                # Cập nhật thời gian treo voice
                new_time = quest_time + time_spent
                cursor.execute("UPDATE users SET quest_time = ? WHERE user_id = ?", (new_time, user_id))
                conn.execute('PRAGMA wal_checkpoint;')

                # Debug log
                # logger.info(f"User {user_id}: voice_time {quest_time} -> {new_time}, target: {quest_dict.get('voice_time', 0)}")

                # Kiểm tra nếu nhiệm vụ voice vừa hoàn thành (chỉ thông báo 1 lần)
                if quest_time < quest_dict.get('voice_time', 0) and new_time >= quest_dict.get('voice_time', 0):
                    logger.info(f"User {user_id} completed voice quest!")
                    # Thông báo real-time cho nhiệm vụ voice
                    await self.notify_completion(user_id, quest_dict.get('balance_voice', 0), "voice", quest_dict.get('voice_time', 0), quest_dict.get('voice_noel', 0))
                    # Kiểm tra xem có hoàn thành đủ 3 nhiệm vụ chính không
                    await self.check_combo_completion(user_id, quest_dict)
                    # Gọi check_quests để xử lý thưởng
                    await self.check_quests()
                    # Không xóa khỏi voice_times ngay để tiếp tục tracking, sẽ xóa khi rời voice
                elif new_time >= quest_dict.get('voice_time', 0):
                    # Nếu đã hoàn thành từ trước, vẫn tiếp tục tracking để cập nhật thời gian
                    self.voice_times[user_id] = now
                else:
                    # Cập nhật lại thời gian bắt đầu để tránh tính trùng lặp
                    self.voice_times[user_id] = now

    @update_voice_time.before_loop
    async def before_update_voice_time(self):
        await self.client.wait_until_ready()

    @commands.command(aliases=["q"], description="daily quest")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @is_daily_channel()
    async def quest(self, ctx):
        if await self.check_command_disabled(ctx):
            return
        guild = ctx.guild  
        user_id = ctx.author.id
        cursor.execute("SELECT quest, quest_time, quest_mess, quest_image, quest_time_start, quest_CASINO, quest_GIAITRI, quest_PRAY FROM users WHERE user_id = ?", (user_id,))
        quest_data = cursor.fetchone()
        timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        now = datetime.now(timezone)
        reset_time = datetime(now.year, now.month, now.day, 14, 0) + timedelta(days=1)
        if not quest_data or not quest_data[0]:  # Nếu người dùng chưa có nhiệm vụ, tạo nhiệm vụ mới
            self.create_new_quest(user_id, ctx)
            cursor.execute("SELECT quest, quest_time, quest_mess, quest_image, quest_time_start, quest_CASINO, quest_GIAITRI, quest_PRAY FROM users WHERE user_id = ?", (user_id,))
            quest_data = cursor.fetchone()

        quest, quest_time, quest_mess, quest_image, quest_time_start, quest_CASINO, quest_GIAITRI, quest_PRAY = quest_data
        if quest_time_start:
            quest_time_start = datetime.strptime(quest_time_start, "%Y-%m-%d %H:%M:%S")

        if quest:
            try:
                quest_dict = json.loads(quest)
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Invalid quest data for user {user_id} in quest command: {e}")
                logger.error(f"Raw quest data: {repr(quest)}")
                # Reset quest data và tạo mới
                self.create_new_quest(user_id, ctx)
                cursor.execute("SELECT quest FROM users WHERE user_id = ?", (user_id,))
                quest = cursor.fetchone()[0]
                quest_dict = json.loads(quest)
                await ctx.send("⚠️ Dữ liệu nhiệm vụ của bạn đã được reset và tạo mới!")
            is_time_completed = quest_time >= quest_dict.get('voice_time', 0)
            is_mess_completed = quest_mess >= quest_dict.get('messages', 0)
            is_image_completed = quest_image >= quest_dict.get('image', 0)
            is_casino_completed = quest_CASINO >= quest_dict.get('casino_times', 0)
            is_giaitri_completed = quest_GIAITRI >= quest_dict.get('giaitri_times', 0)
            is_pray_completed = quest_PRAY >= quest_dict.get('pray_times', 0)
            
            embed = discord.Embed(title="", color=discord.Color.from_rgb(255, 255, 255))
            if ctx.author.avatar:
                avatar_url = ctx.author.avatar.url
            else:
                avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
            embed.set_author(name=f"{ctx.author.display_name}'s daily quest", icon_url=avatar_url)
            embed.add_field(
                name="", 
                value=f"{questso1} **Chat** __**{quest_dict.get('messages', 0)} tin**__ tại [__**sảnh chat**__](<https://discord.com/channels/832579380634451969/{quest_dict.get('message_channel', 0)}>)\n-# {list_emoji.trong}`‣ Tiến độ:` **{quest_mess}/{quest_dict.get('messages', 0)}**\n-# {list_emoji.trong}`‣ Thưởng :` **{format_number(quest_dict.get('balance_mess', 0))} {list_emoji.pinkcoin} + {quest_dict.get('mess_noel', 0)} {list_emoji.xu_event}**" if not is_mess_completed else f"{questso1} **Chat** __**{quest_dict.get('messages', 0)} tin**__ tại [__**sảnh chat**__](<https://discord.com/channels/832579380634451969/{quest_dict.get('message_channel', 0)}>)\n-# {list_emoji.trong}`‣ Tiến độ:` {tickxanh}\n-# {list_emoji.trong}`‣ Thưởng :` **{format_number(quest_dict.get('balance_mess', 0))} {list_emoji.pinkcoin} + {quest_dict.get('mess_noel', 0)} {list_emoji.xu_event}**",
                inline=False
            )
            embed.add_field(
                name="",
                value=f"{questso2} **Treo voice** __**{quest_dict.get('voice_time', 0)}h**__\n-# {list_emoji.trong}`‣ Tiến độ:` **{quest_time}/{quest_dict.get('voice_time', 0)}**\n-# {list_emoji.trong}`‣ Thưởng :` **{format_number(quest_dict.get('balance_voice', 0))} {list_emoji.pinkcoin} + {quest_dict.get('voice_noel', 0)} {list_emoji.xu_event}**" if not is_time_completed else f"{questso2} **Treo voice** __**{quest_dict.get('voice_time', 0)}h**__\n-# {list_emoji.trong}`‣ Tiến độ:` {tickxanh} \n-# {list_emoji.trong}`‣ Thưởng :` **{format_number(quest_dict.get('balance_voice', 0))} {list_emoji.pinkcoin} + {quest_dict.get('voice_noel', 0)} {list_emoji.xu_event}**",
                inline=False
            )
            if quest_dict.get('message_image', 0) == 1052625475769471127:
                embed.add_field(
                    name="",
                    value=f"{questso3} **Gửi một ảnh meme vào** [__**đây**__](<https://discord.com/channels/832579380634451969/1052625475769471127>)"if not is_image_completed else f"{questso3} **Gửi một ảnh meme vào** [__**đây**__](<https://discord.com/channels/832579380634451969/1052625475769471127>) {tickxanh}",
                    inline=False
                )
            elif quest_dict.get('message_image', 0) == 1021646306567016498:
                embed.add_field(
                    name="",
                    value=f"{questso3} **Gửi một ảnh đồ ăn vào** [__**đây**__](<https://discord.com/channels/832579380634451969/1021646306567016498>)"if not is_image_completed else f"{questso3} **Gửi một ảnh đồ ăn vào** [__**đây**__](<https://discord.com/channels/832579380634451969/1021646306567016498>) {tickxanh}",
                    inline=False)
            # embed.add_field(
            #     name="",
            #     value=f"{questso1} **Chơi** [__**casino**__](<https://discord.com/channels/832579380634451969/1273768834830041301>) __**{quest_dict.get('casino_times', 0)} lần**__\n-# {list_emoji.trong}`‣ Tiến độ:` **{quest_CASINO}/{quest_dict.get('casino_times', 0)}**\n-# {list_emoji.trong}`‣ Thưởng :` **{format_number(quest_dict.get('casino_xu', 0))} {list_emoji.pinkcoin}**" if not is_casino_completed else f"{questso1} **Chơi** [__**casino**__](<https://discord.com/channels/832579380634451969/1273768834830041301>) __**{quest_dict.get('casino_times', 0)} lần**__\n-# {list_emoji.trong}`‣ Tiến độ:` {tickxanh} \n-# {list_emoji.trong}`‣ Thưởng :` **{format_number(quest_dict.get('casino_xu', 0))} {list_emoji.pinkcoin}**",
            #     inline=False
            # )
            # embed.add_field(
            #     name="",
            #     value=f"{questso1} **Chơi** [__**giải trí**__](<https://discord.com/channels/832579380634451969/1273769137985818624>) __**{quest_dict.get('giaitri_times', 0)} lần**__\n-# {list_emoji.trong}`‣ Tiến độ:` **{quest_CASINO}/{quest_dict.get('casino_times', 0)}**\n-# {list_emoji.trong}`‣ Thưởng :` **{format_number(quest_dict.get('giaitri_xu', 0))} {list_emoji.pinkcoin}**" if not is_giaitri_completed else f"{questso1} **Chơi** [__**giải trí**__](<https://discord.com/channels/832579380634451969/1273769137985818624>) __**{quest_dict.get('giaitri_times', 0)} lần**__\n-# {list_emoji.trong}`‣ Tiến độ:` {tickxanh} \n-# {list_emoji.trong}`‣ Thưởng :` **{format_number(quest_dict.get('giaitri_xu', 0))} {list_emoji.pinkcoin}**",
            #     inline=False
            # )

            # if quest_dict.get('pray_choice', 0) == 'zpray':
            #     embed.add_field(
            #         name="",
            #         value=f"{questso2} [__**zpray**__](<https://discord.com/channels/832579380634451969/1273768834830041301>) __**{quest_dict.get('pray_times', 0)} lần**__\n-# {list_emoji.trong}`‣ Tiến độ:` **{quest_CASINO}/{quest_dict.get('pray_times', 0)}**\n-# {list_emoji.trong}`‣ Thưởng :` **{format_number(quest_dict.get('pray_xu', 0))} {list_emoji.pinkcoin}**" if not is_pray_completed else f"{questso1} [__**zpray**__](<https://discord.com/channels/832579380634451969/1273768834830041301>) __**{quest_dict.get('pray_times', 0)} lần**__\n-# {list_emoji.trong}`‣ Tiến độ:` {tickxanh} \n-# {list_emoji.trong}`‣ Thưởng :` **{format_number(quest_dict.get('pray_xu', 0))} {list_emoji.pinkcoin}**",
            #         inline=False
            #     )
            # if quest_dict.get('pray_choice', 0) == 'zlove':
            #     embed.add_field(
            #         name="",
            #         value=f"{questso3} [__**zlove**__](<https://discord.com/channels/832579380634451969/1273768834830041301>) __**{quest_dict.get('pray_times', 0)} lần**__\n-# {list_emoji.trong}`‣ Tiến độ:` **{quest_CASINO}/{quest_dict.get('pray_times', 0)}**\n-# {list_emoji.trong}`‣ Thưởng :` **{format_number(quest_dict.get('pray_xu', 0))} {list_emoji.pinkcoin}**" if not is_pray_completed else f"{questso1} [__**zlove**__](<https://discord.com/channels/832579380634451969/1273768834830041301>) __**{quest_dict.get('pray_times', 0)} lần**__\n-# {list_emoji.trong}`‣ Tiến độ:` {tickxanh} \n-# {list_emoji.trong}`‣ Thưởng :` **{format_number(quest_dict.get('pray_xu', 0))} {list_emoji.pinkcoin}**",
            #         inline=False
            #     )
                
            embed.add_field(name="", value=f"-# {benphai} Hoàn thành cả ba + **1 {list_emoji.xu_event} & 1 combo x10**\n-# {benphai} Voice nhớ out ra vào lại, kh tắt loa", inline=False)
            icon_url = guild.icon.url if guild.icon else None
            embed.set_footer(text="Quests reset at 14:00 every day.", icon_url=icon_url)
            await self.check_quests()
            view = QuestView(ctx.author.id, quest_dict)
            await ctx.send(embed=embed, view=view)
            

    @quest.error
    async def quest_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = divmod(int(error.retry_after), 60)  # Chia cho 60 để có phút và giây
            formatted_time = f"{remaining_time[0]}m{remaining_time[1]}s"
            message = await ctx.send(f"{list_emoji.tick_check} | Vui lòng đợi thêm `{formatted_time}` để có thể sử dụng lệnh này!!")
            await asyncio.sleep(2)
            await message.delete()
            await ctx.message.delete()
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error


    async def check_combo_completion(self, user_id, quest_dict):
        """Kiểm tra và thông báo nếu vừa hoàn thành đủ 3 nhiệm vụ chính"""
        cursor.execute("SELECT quest_time, quest_mess, quest_image, quest_done FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            quest_time, quest_mess, quest_image, quest_done = result
            
            # Kiểm tra điều kiện hoàn thành từng nhiệm vụ
            is_time_completed = quest_time >= quest_dict.get('voice_time', 0)
            is_mess_completed = quest_mess >= quest_dict.get('messages', 0)
            is_image_completed = quest_image >= quest_dict.get('image', 0)
            
            # Debug log
            logger.info(f"User {user_id} combo check: voice={is_time_completed} ({quest_time}/{quest_dict.get('voice_time', 0)}), mess={is_mess_completed} ({quest_mess}/{quest_dict.get('messages', 0)}), image={is_image_completed} ({quest_image}/{quest_dict.get('image', 0)}), quest_done={quest_done}")
            
            # Nếu tất cả 3 nhiệm vụ đều hoàn thành và chưa thông báo combo
            if is_time_completed and is_mess_completed and is_image_completed and quest_done < 8:
                logger.info(f"User {user_id} completed all 3 main quests! Sending combo notification.")
                # Thông báo combo ngay lập tức - truyền thông tin random rewards
                rewards = generate_random_combo_rewards()
                combo_text = f"{bot}{number_to_superscript(rewards['bột']['so_luong'])} + {dauxanh}{number_to_superscript(rewards['đậu xanh']['so_luong'])} + {trungmuoi}{number_to_superscript(rewards['trứng muối']['so_luong'])}"
                
                # Lưu combo rewards vào quest data
                quest_dict['combo_rewards'] = rewards
                cursor.execute("UPDATE users SET quest = ? WHERE user_id = ?", (json.dumps(quest_dict), user_id))
                conn.execute('PRAGMA wal_checkpoint;')
                
                await self.notify_completion(user_id, combo_text, "combo", "3 nhiệm vụ", quest_dict.get('img_xu', 0))

    async def check_combo_completion_secondary(self, user_id, quest_dict):
        """Kiểm tra và thông báo nếu vừa hoàn thành đủ 3 nhiệm vụ phụ (pray, casino, giải trí)"""
        cursor.execute("SELECT quest_CASINO, quest_GIAITRI, quest_PRAY, quest_done2 FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            quest_CASINO, quest_GIAITRI, quest_PRAY, quest_done2 = result
            
            # Kiểm tra điều kiện hoàn thành từng nhiệm vụ phụ
            is_casino_completed = quest_CASINO >= quest_dict.get('casino_times', 0)
            is_giaitri_completed = quest_GIAITRI >= quest_dict.get('giaitri_times', 0)
            is_pray_completed = quest_PRAY >= quest_dict.get('pray_times', 0)
            
            # Debug log
            logger.info(f"User {user_id} secondary combo check: casino={is_casino_completed} ({quest_CASINO}/{quest_dict.get('casino_times', 0)}), giaitri={is_giaitri_completed} ({quest_GIAITRI}/{quest_dict.get('giaitri_times', 0)}), pray={is_pray_completed} ({quest_PRAY}/{quest_dict.get('pray_times', 0)}), quest_done2={quest_done2}")
            
            # Nếu tất cả 3 nhiệm vụ phụ đều hoàn thành và chưa thông báo combo
            if is_casino_completed and is_giaitri_completed and is_pray_completed and quest_done2 < 8:
                logger.info(f"User {user_id} completed all 3 secondary quests! Sending secondary combo notification.")
                # Thông báo combo cho nhiệm vụ phụ ngay lập tức
                total_xu_reward = quest_dict.get('casino_xu', 0) + quest_dict.get('giaitri_xu', 0) + quest_dict.get('pray_xu', 0)
                await self.notify_completion(user_id, total_xu_reward, "combo_secondary", "3 nhiệm vụ phụ", 1)

    async def check_quests(self): 
        ensure_data_consistency() 
        # Lấy danh sách người dùng và nhiệm vụ
        cursor.execute("SELECT user_id, quest, quest_time, quest_mess, quest_image, quest_done, quest_CASINO, quest_GIAITRI, quest_PRAY, quest_done2, balance FROM users")  
        users = cursor.fetchall()  

        for user in users:  
            user_id, quest_data, quest_time, quest_mess, quest_image, quest_done, quest_CASINO, quest_GIAITRI, quest_PRAY, quest_done2, balance = user  

            if quest_data:  
                try:
                    # Chuyển đổi dữ liệu nhiệm vụ từ chuỗi sang dictionary
                    quest_dict = json.loads(quest_data)  
                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"Invalid quest data for user {user_id}: {e}")
                    logger.error(f"Raw quest data: {repr(quest_data)}")
                    # Reset quest data nếu bị lỗi
                    cursor.execute("UPDATE users SET quest = '' WHERE user_id = ?", (user_id,))
                    conn.execute('PRAGMA wal_checkpoint;')
                    logger.info(f"Reset corrupted quest data for user {user_id}")
                    continue
                
                # Kiểm tra điều kiện hoàn thành từng nhiệm vụ
                is_time_completed = quest_time >= quest_dict.get('voice_time', 0)  
                is_mess_completed = quest_mess >= quest_dict.get('messages', 0)  
                is_image_completed = quest_image >= quest_dict.get('image', 0)  
                is_casino_completed = quest_CASINO >= quest_dict.get('casino_times', 0)
                is_giaitri_completed = quest_GIAITRI >= quest_dict.get('giaitri_times', 0)
                is_pray_completed = quest_PRAY >= quest_dict.get('pray_times', 0)
                
                balance_reward = quest_dict.get('balance_voice', 0) + quest_dict.get('balance_mess', 0)
                event_reward = quest_dict.get('voice_noel', 0) + quest_dict.get('mess_noel', 0) + quest_dict.get('img_xu', 0)
                balance_reward2 = quest_dict.get('casino_xu', 0) + quest_dict.get('giaitri_xu', 0) + quest_dict.get('pray_xu', 0)
                
                # Kiểm tra nếu quest_done == 0 (chưa hoàn thành nhiệm vụ nào)
                if quest_done == 0:
                    if is_time_completed and is_mess_completed and is_image_completed:
                        # Cộng thêm combo items vào kho (sử dụng rewards đã lưu)
                        cursor.execute("SELECT open_items FROM users WHERE user_id = ?", (user_id,))
                        open_items_data = cursor.fetchone()[0]
                        open_items_dict = json.loads(open_items_data) if open_items_data else {}

                        # Sử dụng combo rewards đã lưu trong quest data
                        rewards = quest_dict.get('combo_rewards', generate_random_combo_rewards())

                        for item_name, item_data in rewards.items():
                            if item_name in open_items_dict:
                                open_items_dict[item_name]["so_luong"] += item_data["so_luong"]
                            else:
                                open_items_dict[item_name] = {
                                    "emoji": item_data["emoji"],
                                    "name_phanthuong": item_name,
                                    "so_luong": item_data["so_luong"],
                                }

                        # Sắp xếp lại kho theo emoji
                        sorted_open_items = dict(
                            sorted(open_items_dict.items(), key=lambda item: item[1]["emoji"])
                        )
                        updated_open_items = json.dumps(sorted_open_items)
                        cursor.execute("UPDATE users SET open_items = ? WHERE user_id = ?", (updated_open_items, user_id))

                        # Cập nhật trạng thái nhiệm vụ
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ?, quest_done = 8 WHERE user_id = ?", 
                                    (balance_reward, event_reward + 1, user_id))
                        conn.execute('PRAGMA wal_checkpoint;')
                    elif is_time_completed and is_mess_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ?, quest_done = 5 WHERE user_id = ?",   
                                        (quest_dict.get('balance_voice', 0) + quest_dict.get('balance_mess', 0), 
                                        quest_dict.get('voice_noel', 0) + quest_dict.get('mess_noel', 0), user_id))  
                        conn.execute('PRAGMA wal_checkpoint;')
                    elif is_time_completed and is_image_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ?, quest_done = 6 WHERE user_id = ?",   
                                        (quest_dict.get('balance_voice', 0), 
                                        quest_dict.get('voice_noel', 0) + quest_dict.get('img_xu', 0), user_id))  
                        conn.execute('PRAGMA wal_checkpoint;')
                    elif is_mess_completed and is_image_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ?, quest_done = 7 WHERE user_id = ?",   
                                        (quest_dict.get('balance_mess', 0), 
                                        quest_dict.get('mess_noel', 0) + quest_dict.get('img_xu', 0), user_id))  
                        conn.execute('PRAGMA wal_checkpoint;')
                    elif is_time_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ?, quest_done = 1 WHERE user_id = ?",   
                                        (quest_dict.get('balance_voice', 0), quest_dict.get('voice_noel', 0), user_id))  
                        conn.execute('PRAGMA wal_checkpoint;')
                    elif is_mess_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ?, quest_done = 2 WHERE user_id = ?",   
                                        (quest_dict.get('balance_mess', 0), quest_dict.get('mess_noel', 0), user_id))  
                        conn.execute('PRAGMA wal_checkpoint;')
                    elif is_image_completed:
                        cursor.execute("UPDATE users SET xu_hlw = xu_hlw + ?, quest_done = 3 WHERE user_id = ?",   
                                        (quest_dict.get('img_xu', 0), user_id))  
                        conn.execute('PRAGMA wal_checkpoint;')

                # Kiểm tra nếu quest_done == 1 (đã hoàn thành nhiệm vụ time)
                elif quest_done == 1:
                    if is_mess_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ?, quest_done = 5 WHERE user_id = ?",   
                                        (quest_dict.get('balance_mess', 0), quest_dict.get('mess_noel', 0), user_id))  
                        conn.execute('PRAGMA wal_checkpoint;')
                    elif is_image_completed:
                        cursor.execute("UPDATE users SET xu_hlw = xu_hlw + ?, quest_done = 6 WHERE user_id = ?",   
                                        (quest_dict.get('img_xu', 0), user_id))  
                        conn.execute('PRAGMA wal_checkpoint;')

                # Kiểm tra nếu quest_done == 2 (đã hoàn thành nhiệm vụ message)
                elif quest_done == 2:
                    if is_image_completed:
                        cursor.execute("UPDATE users SET xu_hlw = xu_hlw + ?, quest_done = 7 WHERE user_id = ?",   
                                        (quest_dict.get('img_xu', 0), user_id))  
                        conn.execute('PRAGMA wal_checkpoint;')
                    elif is_time_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ?, quest_done = 5 WHERE user_id = ?",   
                                        (quest_dict.get('balance_voice', 0), quest_dict.get('voice_noel', 0), user_id))  
                        conn.execute('PRAGMA wal_checkpoint;')

                # Kiểm tra nếu quest_done == 3 (đã hoàn thành nhiệm vụ image)
                elif quest_done == 3:
                    if is_time_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ?, quest_done = 6 WHERE user_id = ?",   
                                        (quest_dict.get('balance_voice', 0), quest_dict.get('voice_noel', 0), user_id))  
                        conn.execute('PRAGMA wal_checkpoint;')
                    elif is_mess_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ?, quest_done = 7 WHERE user_id = ?",   
                                        (quest_dict.get('balance_mess', 0), quest_dict.get('mess_noel', 0), user_id))  
                        conn.execute('PRAGMA wal_checkpoint;')

                # Kiểm tra nếu tất cả các điều kiện hoàn thành và quest_done < 7 - THÔNG BÁO COMBO
                if is_time_completed and is_mess_completed and is_image_completed and quest_done < 8:
                    # Cộng thêm combo items vào kho (sử dụng rewards đã lưu)
                    cursor.execute("SELECT open_items FROM users WHERE user_id = ?", (user_id,))
                    open_items_data = cursor.fetchone()[0]
                    open_items_dict = json.loads(open_items_data) if open_items_data else {}

                    # Sử dụng combo rewards đã lưu trong quest data
                    rewards = quest_dict.get('combo_rewards', generate_random_combo_rewards())

                    for item_name, item_data in rewards.items():
                        if item_name in open_items_dict:
                            open_items_dict[item_name]["so_luong"] += item_data["so_luong"]
                        else:
                            open_items_dict[item_name] = {
                                "emoji": item_data["emoji"],
                                "name_phanthuong": item_name,
                                "so_luong": item_data["so_luong"],
                            }

                    # Sắp xếp lại kho theo emoji
                    sorted_open_items = dict(
                        sorted(open_items_dict.items(), key=lambda item: item[1]["emoji"])
                    )
                    updated_open_items = json.dumps(sorted_open_items)
                    cursor.execute("UPDATE users SET open_items = ? WHERE user_id = ?", (updated_open_items, user_id))
                    # Không cần thông báo combo ở đây nữa vì đã có trong check_combo_completion
                    if quest_done == 5:
                        cursor.execute("UPDATE users SET xu_hlw = xu_hlw + ?, quest_done = 8 WHERE user_id = ?", (quest_dict.get('img_xu', 0) + 1, user_id))
                        conn.execute('PRAGMA wal_checkpoint;')
                    elif quest_done == 6:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ?, quest_done = 8 WHERE user_id = ?", (quest_dict.get('balance_mess', 0), quest_dict.get('mess_noel', 0) + 1, user_id))
                        conn.execute('PRAGMA wal_checkpoint;')
                    elif quest_done == 7:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ?, quest_done = 8 WHERE user_id = ?", (quest_dict.get('balance_voice', 0), quest_dict.get('voice_noel', 0) + 1, user_id))
                        conn.execute('PRAGMA wal_checkpoint;')

                # Kiểm tra nếu quest_done2 == 0 (chưa hoàn thành nhiệm vụ nào)
                if quest_done2 == 0:
                    if is_casino_completed and is_giaitri_completed and is_pray_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ?, quest_done2 = 8 WHERE user_id = ?",   
                                        (balance_reward2, event_reward + 1, user_id))  
                        conn.execute('PRAGMA wal_checkpoint;')
                    elif is_casino_completed and is_giaitri_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, quest_done2 = 5 WHERE user_id = ?",   
                                        (quest_dict.get('casino_xu', 0) + quest_dict.get('giaitri_xu', 0), user_id))  
                        conn.execute('PRAGMA wal_checkpoint;')
                    elif is_casino_completed and is_pray_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, quest_done2 = 6 WHERE user_id = ?",   
                                        (quest_dict.get('casino_xu', 0) + quest_dict.get('pray_xu', 0),  user_id))  
                        conn.execute('PRAGMA wal_checkpoint;')
                    elif is_giaitri_completed and is_pray_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, quest_done2 = 7 WHERE user_id = ?",   
                                        (quest_dict.get('giaitri_xu', 0) + quest_dict.get('pray_xu', 0), user_id))  
                        conn.execute('PRAGMA wal_checkpoint;')
                    elif is_casino_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, quest_done2 = 1 WHERE user_id = ?",   
                                        (quest_dict.get('casino_xu', 0), user_id))  
                        conn.execute('PRAGMA wal_checkpoint;')
                    elif is_giaitri_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, quest_done2 = 2 WHERE user_id = ?",   
                                        (quest_dict.get('giaitri_xu', 0), user_id))  
                        conn.execute('PRAGMA wal_checkpoint;')
                    elif is_pray_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, quest_done2 = 3 WHERE user_id = ?",   
                                        (quest_dict.get('pray_xu', 0), user_id))  
                        conn.execute('PRAGMA wal_checkpoint;')

                # Kiểm tra nếu quest_done2 == 1 (đã hoàn thành nhiệm vụ time)
                elif quest_done2 == 1:
                    if is_giaitri_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, quest_done2 = 5 WHERE user_id = ?",   
                                        (quest_dict.get('giaitri_xu', 0), user_id))  
                        conn.execute('PRAGMA wal_checkpoint;')
                    elif is_pray_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, quest_done2 = 6 WHERE user_id = ?",   
                                        (quest_dict.get('pray_xu', 0), user_id))  
                        conn.execute('PRAGMA wal_checkpoint;')

                # Kiểm tra nếu quest_done2 == 2 (đã hoàn thành nhiệm vụ message)
                elif quest_done2 == 2:
                    if is_pray_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, quest_done2 = 7 WHERE user_id = ?",   
                                        (quest_dict.get('pray_xu', 0), user_id))  
                        conn.execute('PRAGMA wal_checkpoint;')
                    elif is_casino_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, quest_done2 = 5 WHERE user_id = ?",   
                                        (quest_dict.get('casino_xu', 0), user_id))  
                        conn.execute('PRAGMA wal_checkpoint;')

                # Kiểm tra nếu quest_done2 == 3 (đã hoàn thành nhiệm vụ image)
                elif quest_done2 == 3:
                    if is_casino_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, quest_done2 = 6 WHERE user_id = ?",   
                                        (quest_dict.get('casino_xu', 0), user_id))  
                        conn.execute('PRAGMA wal_checkpoint;')
                    elif is_giaitri_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, quest_done2 = 7 WHERE user_id = ?",   
                                        (quest_dict.get('giaitri_xu', 0), user_id))  
                        conn.execute('PRAGMA wal_checkpoint;')

                # Kiểm tra nếu tất cả các điều kiện hoàn thành và quest_done2 < 7
                if is_casino_completed and is_giaitri_completed and is_pray_completed and quest_done2 < 8:
                    if quest_done2 == 5:
                        cursor.execute("UPDATE users SET xu_hlw = xu_hlw + 1, quest_done2 = 8 WHERE user_id = ?", (user_id,))  
                        conn.execute('PRAGMA wal_checkpoint;')
                    elif quest_done2 == 6:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + 1, quest_done2 = 8 WHERE user_id = ?", (quest_dict.get('giaitri_xu', 0), user_id))  
                        conn.execute('PRAGMA wal_checkpoint;')
                    elif quest_done2 == 7:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + 1, quest_done2 = 8 WHERE user_id = ?", (quest_dict.get('casino_xu', 0), user_id))  
                        conn.execute('PRAGMA wal_checkpoint;')

    # @check_quests.before_loop
    # async def before_check_quests(self):
    #     await self.client.wait_until_ready()

    def create_new_quest(self, user_id, ctx):
        guild = ctx.guild  
        voice_time = random.choice([1, 2, 3])  
        if voice_time == 1:  
            voice_xu = 5000
            voice_noel = 1 
        elif voice_time == 2:  
            voice_xu = 10000  
            voice_noel = 2
        elif voice_time == 3:   
            voice_xu = 15000  
            voice_noel = 3

        message_channel = 993153068378116127    
        if message_channel == 993153068378116127:  
            messages = random.choice([50, 80, 120])
            if messages == 50:
                message_xu = 5000
                mess_xu = 1  
            elif messages == 80:
                message_xu = 10000
                mess_xu = 2  
            elif messages == 120:
                message_xu = 15000
                mess_xu = 3
        else: 
            return  

        casino_times = 0
        casino_xu = 0
        giaitri_times = 0
        giaitri_xu = 0

        channel_casino = 1273768834830041301
        if channel_casino == 1273768834830041301:
            casino_times = random.choice([10, 20])
            if casino_times == 10:
                casino_xu = 5000
            elif casino_times == 20:
                casino_xu = 10000
        else:
            return

        channel_giaitri = 1273769137985818624
        if channel_giaitri == 1273769137985818624:
            giaitri_times = random.choice([10, 20])
            if giaitri_times == 10:
                giaitri_xu = 5000
            elif giaitri_times == 20:
                giaitri_xu = 10000
        else:
            return

        pray_choice = random.choice(["zpray", "zpray"])
        pray_times = 5
        pray_xu = 10000

        # Khởi tạo giá trị mặc định cho image
        image = 0  
        img_xu = 0 
        message_channel_image = [1052625475769471127, 1021646306567016498]
        message_image = random.choice(message_channel_image) 

        if message_image == 1052625475769471127:
            image = 1 
            img_xu = 1 
        elif message_image == 1021646306567016498:
            image = 1 
            img_xu = 1

        balance_voice = voice_xu  
        balance_mess = message_xu

        quest_data = {
            'voice_time': voice_time,
            'balance_voice': balance_voice,
            'voice_noel': voice_noel,
            'messages': messages,
            'message_channel': message_channel,
            'balance_mess': balance_mess,
            'mess_noel': mess_xu,
            'image': image,
            'message_image': message_image,
            'img_xu': img_xu,
            'casino_times': casino_times,
            'casino_xu': casino_xu,
            'giaitri_times': giaitri_times,
            'giaitri_xu': giaitri_xu,
            'pray_choice': pray_choice,
            'pray_times': pray_times,
            'pray_xu': pray_xu,
        }




        cursor.execute("UPDATE users SET quest = ? WHERE user_id = ?", (json.dumps(quest_data), user_id))
        conn.execute('PRAGMA wal_checkpoint;')
        logger.info(f"Created new quest for user {user_id}: voice={voice_time}h, messages={messages}, casino={casino_times}, giaitri={giaitri_times}")

        # embed = discord.Embed(title="", color=discord.Color.from_rgb(255, 255, 255))
        # avatar_url = ctx.author.avatar.url if ctx.author.avatar else "https://cdn.discordapp.com/embed/avatars/0.png"
        # embed.set_author(name=f"{ctx.author.display_name}'s daily quest", icon_url=avatar_url)

        # embed.add_field(
        #     name="",
        #     value=f"{questso1} **Chat** __**{messages} tin**__ tại [__**sảnh chat**__](<https://discord.com/channels/832579380634451969/993153068378116127>)\n-# {list_emoji.trong}`‣ Tiến độ:` **0/{messages}**\n-# {list_emoji.trong}`‣ Thưởng :` **{format_number(balance_mess)} {list_emoji.pinkcoin} + {mess_xu} {list_emoji.xu_event}**",
        #     inline=False
        # )
        # embed.add_field(
        #     name="",
        #     value=f"{questso1} **Treo voice** __**{voice_time}h**__\n-# {list_emoji.trong}`‣ Tiến độ:` **0/{voice_time}**\n-# {list_emoji.trong}`‣ Thưởng :` **{format_number(balance_voice)} {list_emoji.pinkcoin} + {voice_noel} {list_emoji.xu_event}**",
        #     inline=False
        # )
        # if message_image == 1052625475769471127:
        #     embed.add_field(
        #         name="",
        #         value=f"{questso1} **Gửi một ảnh meme vào** [__**đây**__](<https://discord.com/channels/832579380634451969/1052625475769471127>)",
        #         inline=False
        #     )
        # elif message_image == 1021646306567016498:
        #     embed.add_field(
        #         name="",
        #         value=f"{questso1} **Gửi một ảnh đồ ăn vào** [__**đây**__](<https://discord.com/channels/832579380634451969/1021646306567016498>)",
        #         inline=False
        #     )
        # embed.add_field(name="", value=f"-# {benphai}Voice nhớ out ra vào lại, kh tắt loa\n-# {benphai}Hoàn thành cả ba + 1 {list_emoji.xu_event}", inline=False)
        # icon_url = guild.icon.url if guild.icon else None
        # embed.set_footer(text="Quests reset at 14:00 every day.", icon_url=icon_url)

        # asyncio.run_coroutine_threadsafe(self.quest(), self.client.loop)


    def cog_unload(self):
        self.update_voice_time.cancel()
        self.quest_reset.cancel()

    @tasks.loop(minutes=1)
    async def quest_reset(self):
        timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        now = datetime.now(timezone)
        if now.hour == 14 and now.minute == 0: 
            cursor.execute("UPDATE users SET quest = '', quest_time = 0, quest_mess = 0, quest_image = 0, quest_time_start = '', quest_done = 0")
            conn.execute('PRAGMA wal_checkpoint;')

    @quest_reset.before_loop
    async def before_quest_reset(self):
        await self.client.wait_until_ready()

    @commands.command( description="reset quest")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @is_bot_owner()
    async def rsquest(self, ctx):
        cursor.execute("UPDATE users SET quest = '', quest_time = 0, quest_mess = 0, quest_image = 0, quest_time_start = '', quest_done = 0, quest_CASINO = 0, quest_GIAITRI = 0, quest_PRAY = 0, quest_done2 = 0, last_pray_time = '', last_casino_time = '', last_giaitri_time = ''")
        conn.execute('PRAGMA wal_checkpoint;')
        await ctx.send("Đã reset quest của tất cả người dùng")

    async def notify_completion(self, user_id, reward, quest_type, goal, xu_reward):
        ensure_data_consistency()
        logger.info(f"notify_completion called: user_id={user_id}, reward={reward}, quest_type={quest_type}, goal={goal}, xu_reward={xu_reward}")
        channel = self.client.get_channel(NOTIFY_CHANNEL_ID)
        if channel:
            user_obj = await self.client.fetch_user(user_id)
            if user_obj:
                user_name = user_obj.mention
                if quest_type == "voice":
                    await channel.send(f"{list_emoji.tickdung} **{user_name}** đã hoàn thành nhiệm vụ voice __**{goal} giờ**__ , bạn được cộng **{reward}** {list_emoji.pinkcoin} + **{xu_reward}** {list_emoji.xu_event}!")
                elif quest_type == "messages":
                    await channel.send(f"{list_emoji.tickdung} **{user_name}**  đã hoàn thành nhiệm vụ chat __**{goal} tin nhắn**__ , bạn được cộng **{reward}** {list_emoji.pinkcoin} + **{xu_reward}** {list_emoji.xu_event}!")
                elif quest_type == "image":
                    await channel.send(f"{list_emoji.tickdung} **{user_name}** đã hoàn thành nhiệm vụ gửi ảnh và nhận được **{xu_reward}** {list_emoji.xu_event}!")
                elif quest_type == "pray":
                    await channel.send(f"{list_emoji.tickdung} **{user_name}** đã hoàn thành nhiệm vụ __**{goal} lần zpray**__ và nhận được **{reward}** {list_emoji.pinkcoin}!")
                elif quest_type == "casino":
                    await channel.send(f"{list_emoji.tickdung} **{user_name}** đã hoàn thành nhiệm vụ __**{goal} lần chơi casino**__ và nhận được **{reward}** {list_emoji.pinkcoin}!")
                elif quest_type == "giaitri":
                    await channel.send(f"{list_emoji.tickdung} **{user_name}** đã hoàn thành nhiệm vụ __**{goal} lần chơi giải trí**__ và nhận được **{reward}** {list_emoji.pinkcoin}!")
                elif quest_type == "combo":
                    logger.info(f"Sending combo notification for user {user_id}")
                    await channel.send(f"{list_emoji.tickdung} **{user_name}** đã hoàn thành 3 nhiệm vụ hôm nay, bạn được cộng **{xu_reward}** {list_emoji.xu_event} & combo x10 {reward}")
                elif quest_type == "combo_secondary":
                    logger.info(f"Sending secondary combo notification for user {user_id}")
                    await channel.send(f"{list_emoji.tickdung} **{user_name}** đã hoàn thành cả 3 nhiệm vụ phụ (casino + giải trí + pray), bạn được cộng **{xu_reward}** {list_emoji.xu_event} thêm!")
                else:
                    logger.warning(f"Unknown quest_type: {quest_type}")
            else:
                logger.error(f"Could not fetch user {user_id}")
        else:
            logger.error(f"Could not get notification channel {NOTIFY_CHANNEL_ID}")


async def setup(client):    
    await client.add_cog(Quest(client))
