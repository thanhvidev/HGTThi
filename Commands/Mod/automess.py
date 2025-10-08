import datetime
import discord
from discord.ext import commands, tasks
import asyncio
import config

ROLE_HOST = 'host'
channel_ids = config.AUTOMESS_CHANNEL_ID

class AutoMessage(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.channel_ids = channel_ids  # ID của kênh để gửi tin nhắn
        self.message_content = "xxx" # Nội dung của tin nhắn được gửi tự động
        self.interval = 1200 # Khoảng thời gian giữa hai lần gửi tin nhắn (đơn vị: giây)
        self.delete_after = 10 # Khoảng thời gian để xoá tin nhắn sau khi gửi (đơn vị: giây)
        self.send_message.start() # Bắt đầu lập lịch gửi tin nhắn

    def cog_unload(self):
        self.send_message.cancel() # Hủy lịch gửi tin nhắn khi tắt bot

    @tasks.loop(seconds=1200)
    async def send_message(self):
        for channel_id in self.channel_ids:
            channel = self.client.get_channel(channel_id)
            await channel.send(self.message_content, delete_after=self.delete_after)

    @tasks.loop(hours=24)
    async def send_daily_message(self):
        current_time = datetime.datetime.utcnow() + datetime.timedelta(hours=7)  # Múi giờ +7
        if current_time.hour == 15 and current_time.minute == 0:
            channel_id = 1053799649938505889
            channel = self.client.get_channel(channel_id)
            await channel.send("zdaily")

    @send_message.before_loop
    async def before_send_message(self):
        await self.client.wait_until_ready() # Đợi cho bot sẵn sàng trước khi bắt đầu lập lịch gửi tin nhắn
        await asyncio.sleep(5) # Đợi 5 giây để đảm bảo bot đã sẵn sàng

    @commands.command()
    @commands.is_owner()
    async def stop_auto_message(self, ctx):
        self.send_message.stop() # Dừng lập lịch gửi tin nhắn
        await ctx.send("Đã dừng lập lịch gửi tin nhắn tự động.")

    @commands.command()
    @commands.is_owner()
    async def set_auto_message(self, ctx, channel_ids: commands.Greedy[int], message_content: str, interval: int, delete_after: int):
        self.channel_ids = channel_ids
        self.message_content = message_content
        self.interval = interval
        self.delete_after = delete_after
        self.send_message.change_interval(seconds=interval) # Thay đổi khoảng thời gian giữa hai lần gửi tin nhắn
        await ctx.send("Đã cập nhật lập lịch gửi tin nhắn tự động.") 

async def setup(client):
    await client.add_cog(AutoMessage(client))