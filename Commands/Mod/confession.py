import discord
from discord.ext import commands
import datetime
import pytz
import sqlite3
import os

# Kết nối đến cơ sở dữ liệu SQLite3
conn = sqlite3.connect('confessions.db')
c = conn.cursor()

# Tạo bảng confession nếu chưa tồn tại
c.execute('''CREATE TABLE IF NOT EXISTS confession
             (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, image_path TEXT, userid INTEGER)''')

def is_allowed_channel():
    async def predicate(ctx):
        allowed_channel_id = 1171755751295959052  # ID của kênh văn bản cho phép
        if ctx.channel.id != allowed_channel_id:
            return False
        return True
    return commands.check(predicate)

class Confession(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.hybrid_command(name="confess", description="Viết confession ẩn danh")
    @is_allowed_channel()
    async def confess(self, ctx, content, attachment: discord.Attachment = None):
        # Kiểm tra nội dung confession
        if len(content) > 1000:
            await ctx.send("Confession của bạn quá dài, vui lòng nhập lại.", ephemeral=True)
            return
        if len(content) < 10:
            await ctx.send("Confession phải trên 10 ký tự", ephemeral=True)
            return
        # Lấy múi giờ hiện tại của Việt Nam
        timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        current_time = datetime.datetime.now(timezone)
        
        if attachment:
            # Nếu có ảnh đính kèm, lưu ảnh vào thư mục cục bộ
            image_path = os.path.join("images", attachment.filename)
            await attachment.save(image_path)
        else:
            image_path = None

        # Thêm confession vào cơ sở dữ liệu
        c.execute("INSERT INTO confession (content, image_path, userid) VALUES (?, ?, ?)",
                  (content, image_path, ctx.author.id))
        conn.commit()
        c.execute("SELECT last_insert_rowid()")
        data = c.fetchone()
        confession_id = data[0]
        
        # Lấy avatar của bot
        bot_avatar = self.client.user.avatar.url
        
        # Xoá tin nhắn của người dùng
        try:
            await ctx.message.delete()
        except discord.NotFound:
            pass
        
        # Gửi confession như một tin nhắn embed
        embed = discord.Embed(
            title=f"Tâm thư (#{confession_id})", description=f"{content}", color=discord.Color.from_rgb(242, 205, 255), timestamp=current_time)
        embed.set_footer(icon_url=bot_avatar, text=f"Dùng /confess để gửi tâm thư")
        
        if image_path:
            file = discord.File(image_path, filename=attachment.filename)
            embed.set_image(url=f"attachment://{attachment.filename}")
            await ctx.channel.send(embed=embed, file=file)
        else:
            await ctx.channel.send(embed=embed)

# Tạo thư mục images nếu nó chưa tồn tại
if not os.path.exists("images"):
    os.makedirs("images")

async def setup(client):
    await client.add_cog(Confession(client))