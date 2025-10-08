import asyncio
import json
import discord
import random
import sqlite3
import datetime
from discord.ext import commands
import datetime
import pytz
from utils.checks import is_bot_owner, is_admin, is_mod

# Kết nối và tạo bảng trong SQLite
# conn = sqlite3.connect('economy.db', isolation_level=None)
# conn.execute('pragma journal_mode=wal')
# cursor = conn.cursor()

def load_random_chance():
    with open('ve.json', 'r') as f:
        data = json.load(f)
        return data.get('random_chance', 0.3)  # Default to 0.3 if not found

random_chance = load_random_chance()

conn = sqlite3.connect('economy.db')
cursor = conn.cursor()

# Tạo bảng ve_database nếu chưa tồn tại
cursor.execute('''CREATE TABLE IF NOT EXISTS ve_database (
                  id INTEGER PRIMARY KEY,
                  num_gold_tickets_available INTEGER DEFAULT 8890,
                  num_diamond_tickets_available INTEGER DEFAULT 70,
                  quantity_tickets INTEGER DEFAULT 0,
                  tong_tickets INTEGER DEFAULT 0,
                  daily_keo INTEGER DEFAULT 0,
                  daily_bonus1 INTEGER DEFAULT 0,
                  daily_bonus2 INTEGER DEFAULT 0,
                  daily_bonus3 INTEGER DEFAULT 0,
                  daily_bonus4 INTEGER DEFAULT 0,
                  daily_nglieu1 INTEGER DEFAULT 0,
                  daily_nglieu2 INTEGER DEFAULT 0,
                  daily_nglieu3 INTEGER DEFAULT 0,
                  daily_nglieu4 INTEGER DEFAULT 0
               )''')
conn.commit()

# Cập nhật bảng ve_database chỉ khi chưa có dữ liệu
cursor.execute('INSERT OR IGNORE INTO ve_database (id, num_gold_tickets_available, num_diamond_tickets_available) VALUES (?, ?, ?)',
               (1, 8890, 70))
conn.commit()

def is_registered(user_id):  # Hàm kiểm tra xem người dùng đã được đăng ký hay chưa
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None

vevang = "<:vevang:1192461054131847260>"
vekc = "<:vekc:1146756758665175040>"

# 128 vé/ngày, 10 vé kc/ngày => vé kc rơi tại các vị trí cố định mỗi ngày  
# Mở rộng để có đủ vé kim cương cho nhiều ngày hơn
trungvekc = []
for day in range(100):  # Mở rộng lên 100 ngày để đủ vé KC
    base = day * 128
    trungvekc.extend([base + 10, base + 20, base + 30, base + 40, base + 50, base + 60, base + 70, base + 80, base + 90, base + 100])

# Không giới hạn 70 vé nữa, để có đủ vé KC cho dài hạn
# trungvekc = trungvekc[:70]  # Bỏ giới hạn này

class Ve(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.allowed_channel_id = 993153068378116127
        self.last_winner_user_id = None  # Lưu ID của người vừa trúng vé gần nhất
        self.user_cooldowns = {}  # Dict để track thời gian nhận vé cuối cùng {user_id: timestamp}
        self.cooldown_minutes = 10  # Cooldown 10 phút giữa các lần nhận vé

    @commands.Cog.listener()
    async def on_message(self, message):
        global user_last_ticket_received
        
        if message.author.bot or message.channel.id != self.allowed_channel_id:
            return
        if not is_registered(message.author.id):
            return
        timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        now_vietnam = datetime.datetime.now(timezone)

        # Kiểm tra reset hàng ngày - sử dụng logic tốt hơn
        cursor.execute('SELECT quantity_tickets FROM ve_database')
        result = cursor.fetchone()
        current_quantity = result[0] if result else 0
        
        # Reset nếu đã qua 14:00 và chưa reset hôm nay
        if now_vietnam.hour >= 14 and current_quantity >= 128:
            cursor.execute('UPDATE ve_database SET quantity_tickets = 0')
            conn.commit()
            cursor.execute('UPDATE users SET daily_tickets = 0')
            conn.commit()
            # Xóa tất cả cooldowns khi reset daily
            self.user_cooldowns.clear()
            print(f"[VE] Reset daily tickets and cooldowns at {now_vietnam.strftime('%H:%M:%S')}")

        if random.random() < random_chance:
            user_id = message.author.id
            
            # Kiểm tra cooldown - người dùng phải đợi ít nhất 10 phút giữa các lần nhận vé
            current_time = now_vietnam.timestamp()
            if user_id in self.user_cooldowns:
                time_since_last = current_time - self.user_cooldowns[user_id]
                if time_since_last < (self.cooldown_minutes * 60):  # Chưa đủ cooldown
                    return
            
            # Kiểm tra nếu người này vừa trúng vé lần trước thì bỏ qua
            if user_id == self.last_winner_user_id:
                return
            
            trung_ve = tao_lenh_tang_ve(user_id)
            if trung_ve == "Vé vàng":
                self.last_winner_user_id = user_id  # Lưu ID người vừa trúng
                self.user_cooldowns[user_id] = current_time  # Cập nhật cooldown
                await message.add_reaction(vevang)
            elif trung_ve == "Vé kim cương":
                self.last_winner_user_id = user_id  # Lưu ID người vừa trúng
                self.user_cooldowns[user_id] = current_time  # Cập nhật cooldown
                await message.add_reaction(vekc)
                
    @commands.command()
    @is_bot_owner()
    async def tile(self, ctx, chance: float):
        if 0 <= chance <= 1:
            global random_chance
            random_chance = chance
            with open('ve.json', 'r') as f:
                data = json.load(f)
            data['random_chance'] = chance
            with open('ve.json', 'w') as f:
                json.dump(data, f, indent=4)
            await ctx.send(f"Đã cập nhật random_chance thành {chance}")
        else:
            await ctx.send("Giá trị chance phải từ 0 đến 1")
    
    @commands.command()
    @is_bot_owner()
    async def fixve(self, ctx):
        """Sửa chữa dữ liệu vé nếu có vấn đề"""
        cursor.execute('SELECT num_gold_tickets_available, num_diamond_tickets_available, quantity_tickets, tong_tickets FROM ve_database')
        ve_data = cursor.fetchone()
        
        if not ve_data:
            await ctx.send("❌ Không tìm thấy dữ liệu ve_database!")
            return
            
        num_gold_tickets_available, num_diamond_tickets_available, quantity_tickets, tong_tickets = ve_data
        
        # Tạo embed báo cáo
        embed = discord.Embed(title="📊 Báo cáo trạng thái vé", color=0x00ff00)
        embed.add_field(name="Vé vàng còn lại", value=f"{num_gold_tickets_available:,}", inline=True)
        embed.add_field(name="Vé KC còn lại", value=f"{num_diamond_tickets_available:,}", inline=True)
        embed.add_field(name="Vé đã phát hôm nay", value=f"{quantity_tickets}/128", inline=True)
        embed.add_field(name="Tổng vé đã phát", value=f"{tong_tickets:,}", inline=True)
        
        # Kiểm tra và sửa lỗi
        fixes_made = []
        
        # Fix 1: Đảm bảo quantity_tickets không vượt quá 128
        if quantity_tickets > 128:
            cursor.execute('UPDATE ve_database SET quantity_tickets = 128')
            fixes_made.append(f"Đã giảm quantity_tickets từ {quantity_tickets} xuống 128")
            quantity_tickets = 128
            
        # Fix 2: Đảm bảo số vé không âm
        if num_gold_tickets_available < 0:
            cursor.execute('UPDATE ve_database SET num_gold_tickets_available = 0')
            fixes_made.append(f"Đã tăng num_gold_tickets_available từ {num_gold_tickets_available} lên 0")
            
        if num_diamond_tickets_available < 0:
            cursor.execute('UPDATE ve_database SET num_diamond_tickets_available = 0')
            fixes_made.append(f"Đã tăng num_diamond_tickets_available từ {num_diamond_tickets_available} lên 0")
            
        if fixes_made:
            conn.commit()
            embed.add_field(name="🔧 Sửa chữa đã thực hiện", 
                          value="\n".join(fixes_made), inline=False)
            embed.color = 0xff9900
        else:
            embed.add_field(name="✅ Status", value="Dữ liệu vé đang ổn định", inline=False)
            
        await ctx.send(embed=embed)
    
    @commands.command()
    @is_bot_owner()
    async def resetdaily(self, ctx):
        """Reset thủ công số vé hàng ngày"""
        cursor.execute('UPDATE ve_database SET quantity_tickets = 0')
        cursor.execute('UPDATE users SET daily_tickets = 0')
        conn.commit()
        
        # Xóa tất cả cooldowns
        cooldown_count = len(self.user_cooldowns)
        self.user_cooldowns.clear()
        
        embed = discord.Embed(
            title="🔄 Reset Daily Tickets", 
            description=f"Đã reset số vé hàng ngày về 0 cho tất cả người dùng\nĐã xóa {cooldown_count} cooldowns",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @commands.command()
    @is_bot_owner()
    async def setcooldown(self, ctx, minutes: int):
        """Thiết lập thời gian cooldown giữa các lần nhận vé (phút)"""
        if minutes < 0 or minutes > 60:
            await ctx.send("❌ Cooldown phải từ 0-60 phút")
            return
            
        self.cooldown_minutes = minutes
        embed = discord.Embed(
            title="⏰ Cập nhật Cooldown", 
            description=f"Đã thiết lập cooldown thành **{minutes} phút** giữa các lần nhận vé",
            color=0x00ff00
        )
        if minutes == 0:
            embed.description = "🚫 **Đã TẮT cooldown** - User có thể nhận vé liên tục"
            embed.color = 0xff0000
        await ctx.send(embed=embed)
    
    @commands.command()
    @is_bot_owner()  
    async def cooldownstatus(self, ctx):
        """Xem trạng thái cooldown của các user"""
        if not self.user_cooldowns:
            await ctx.send("📝 Chưa có user nào trong cooldown")
            return
            
        timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        current_time = datetime.datetime.now(timezone).timestamp()
        
        embed = discord.Embed(title="⏰ Trạng thái Cooldown", color=0x00ff00)
        embed.add_field(name="⚙️ Settings", value=f"Cooldown: **{self.cooldown_minutes} phút**", inline=False)
        
        active_cooldowns = []
        expired_cooldowns = []
        
        for user_id, last_time in list(self.user_cooldowns.items()):
            time_since = current_time - last_time
            remaining = (self.cooldown_minutes * 60) - time_since
            
            try:
                user = self.client.get_user(user_id) or await self.client.fetch_user(user_id)
                username = user.display_name if user else f"User {user_id}"
            except:
                username = f"User {user_id}"
            
            if remaining > 0:
                mins, secs = divmod(int(remaining), 60)
                active_cooldowns.append(f"• {username}: {mins}m{secs}s")
            else:
                expired_cooldowns.append(user_id)
        
        # Xóa cooldowns đã hết hạn
        for user_id in expired_cooldowns:
            del self.user_cooldowns[user_id]
        
        if active_cooldowns:
            cooldown_text = "\n".join(active_cooldowns[:10])  # Giới hạn 10 người
            if len(active_cooldowns) > 10:
                cooldown_text += f"\n... và {len(active_cooldowns) - 10} người khác"
            embed.add_field(name="🔒 Đang trong cooldown", value=cooldown_text, inline=False)
        else:
            embed.add_field(name="✅ Status", value="Không có user nào trong cooldown", inline=False)
            
        await ctx.send(embed=embed)
    

def tao_lenh_tang_ve(user_id):
    # Sử dụng transaction để tránh race condition
    conn.execute('BEGIN TRANSACTION')
    try:
        cursor.execute(
            'SELECT num_gold_tickets_available, num_diamond_tickets_available, quantity_tickets, tong_tickets FROM ve_database')
        ve_data = cursor.fetchone()

        if not ve_data:
            conn.rollback()
            return None

        num_gold_tickets_available, num_diamond_tickets_available, quantity_tickets, tong_tickets = ve_data
        
        # Kiểm tra hard limit - không được vượt quá 128 vé/ngày
        if quantity_tickets >= 128:
            conn.rollback()
            return None
            
        # Kiểm tra daily_tickets của người dùng
        cursor.execute(
            'SELECT daily_tickets, kimcuong FROM users WHERE user_id = ?', (user_id,))
        user_data = cursor.fetchone()
        danh_sach_3_ve_ngay = [1021383533178134620, 1110815562910670890]
        danh_sach_cam_user_id = [1043086185557393429, 758208203019517972, 893690187501166613, 1173834427667861616, 988714712961286144, 1019284062294253659, 840058737191288832, 852692490468458566]
        
        if user_data and (user_id in danh_sach_3_ve_ngay) and user_data[0] >= 12:
            conn.rollback()
            return None
        elif user_id in danh_sach_cam_user_id:
            conn.rollback()
            return None
        elif user_data and user_data[0] >= 10:
            conn.rollback()
            return None

        # Kiểm tra vé kim cương TRƯỚC - kiểm tra vị trí vé tiếp theo  
        next_ticket_position = tong_tickets + 1
        if (next_ticket_position in trungvekc and 
            num_diamond_tickets_available > 0 and 
            quantity_tickets < 128):
              
            new_num_diamond_tickets = num_diamond_tickets_available - 1
            new_quantity_tickets = quantity_tickets + 1
            new_tong_tickets = tong_tickets + 1
            
            # Kiểm tra lần cuối trước khi commit
            if new_num_diamond_tickets >= 0 and new_quantity_tickets <= 128:
                cursor.execute('UPDATE ve_database SET num_diamond_tickets_available = ?, quantity_tickets = ?, tong_tickets = ?',
                               (new_num_diamond_tickets, new_quantity_tickets, new_tong_tickets))
                cursor.execute(
                    'UPDATE users SET num_diamond_tickets = num_diamond_tickets + 1, daily_tickets = daily_tickets + 1, kimcuong = kimcuong + 1 WHERE user_id = ?', (user_id,))
                conn.commit()
                return "Vé kim cương"
            else:
                conn.rollback()
                return None
                
        # Kiểm tra vé vàng SAU - thêm điều kiện kiểm tra chặt chẽ hơn
        elif (random.random() < 0.1 and 
            num_gold_tickets_available > 0 and 
            quantity_tickets < 128):
            
            new_num_gold_tickets = num_gold_tickets_available - 1
            new_quantity_tickets = quantity_tickets + 1
            new_tong_tickets = tong_tickets + 1
            
            # Kiểm tra lần cuối trước khi commit
            if new_num_gold_tickets >= 0 and new_quantity_tickets <= 128:
                cursor.execute('UPDATE ve_database SET num_gold_tickets_available = ?, quantity_tickets = ?, tong_tickets = ?',
                               (new_num_gold_tickets, new_quantity_tickets, new_tong_tickets))
                cursor.execute(
                    'UPDATE users SET num_gold_tickets = num_gold_tickets + 1, daily_tickets = daily_tickets + 1, kimcuong = kimcuong + 1 WHERE user_id = ?', (user_id,))
                conn.commit()
                return "Vé vàng"
            else:
                conn.rollback()
                return None
        else:
            conn.rollback()
            return None
            
    except Exception as e:
        conn.rollback()
        print(f"Lỗi trong tao_lenh_tang_ve: {e}")
        return None

async def setup(client):
    await client.add_cog(Ve(client))