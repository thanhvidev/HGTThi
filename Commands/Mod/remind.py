import datetime
import discord
from discord.ext import commands, tasks
import asyncio
import json
import os

def is_guild_owner_or_bot_owner():
    async def predicate(ctx):
        return ctx.author == ctx.guild.owner or ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222
    return commands.check(predicate)

class Remind(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.remind_tasks = {}
        self.remind_messages = {}  # Lưu lại message nhắc nhở đã gửi
        self.active_reminders = {}
        self.load_reminders()

    async def monitor_channel(self, channel, message):
        try:
            while self.active_reminders.get(channel.id, False):  # Chỉ tiếp tục nếu cờ vẫn bật
                def check(m):
                    return m.channel.id == channel.id

                try:
                    await self.client.wait_for("message", timeout=300, check=check)
                except asyncio.TimeoutError:
                    if channel.id in self.remind_messages:
                        try:
                            old_message = await channel.fetch_message(self.remind_messages[channel.id])
                            await old_message.delete()
                        except discord.NotFound:
                            pass
                    sent_message = await channel.send(message)
                    self.remind_messages[channel.id] = sent_message.id
        except asyncio.CancelledError:
            pass  # Thoát khi task bị huỷ
        finally:
            self.active_reminders[channel.id] = False

    @commands.command()
    @is_guild_owner_or_bot_owner()
    async def remind(self, ctx, channel_id: int, *, message):
        channel = self.client.get_channel(channel_id)
        if channel is None:
            await ctx.send("Không tìm thấy kênh với ID đã cho.")
            return

        reminder = {"message": message, "channel_id": channel_id}
        self.save_reminder(reminder)

        # Nếu đã có task đang chạy, huỷ trước khi khởi tạo mới
        if channel_id in self.remind_tasks:
            self.remind_tasks[channel_id].cancel()

        # Cài đặt cờ kiểm soát và khởi động task mới
        self.active_reminders[channel_id] = True
        self.remind_tasks[channel_id] = asyncio.create_task(self.monitor_channel(channel, message))

        await ctx.send(f"Đã thiết lập nhắc nhở cho kênh <#{channel_id}> với tin nhắn: {message}.")
        
    @commands.command()
    @is_guild_owner_or_bot_owner()
    async def xoaremind(self, ctx, channel_id: int):
        if channel_id in self.remind_tasks:
            # Hủy task và tắt cờ kiểm soát
            self.remind_tasks[channel_id].cancel()
            del self.remind_tasks[channel_id]
            self.active_reminders[channel_id] = False

            # Xóa tin nhắn nhắc nhở đã gửi
            if channel_id in self.remind_messages:
                try:
                    channel = self.client.get_channel(channel_id)
                    if channel:
                        old_message = await channel.fetch_message(self.remind_messages[channel_id])
                        await old_message.delete()
                except discord.NotFound:
                    pass
                del self.remind_messages[channel_id]

            # Cập nhật file JSON
            if os.path.exists("remind.json"):
                with open("remind.json", "r") as f:
                    data = json.load(f)
                data = [r for r in data if r["channel_id"] != channel_id]
                with open("remind.json", "w") as f:
                    json.dump(data, f, indent=4)

            await ctx.send(f"Đã dừng nhắc nhở cho kênh <#{channel_id}>.")
        else:
            await ctx.send("Không tìm thấy nhắc nhở cho kênh này.")

    def save_reminder(self, reminder):
        if not os.path.exists("remind.json"):
            with open("remind.json", "w") as f:
                json.dump([], f)

        with open("remind.json", "r") as f:
            data = json.load(f)

        # Loại bỏ nhắc nhở cũ của cùng kênh
        data = [r for r in data if r["channel_id"] != reminder["channel_id"]]
        data.append(reminder)

        with open("remind.json", "w") as f:
            json.dump(data, f, indent=4)

    def load_reminders(self):
        if not os.path.exists("remind.json"):
            return

        with open("remind.json", "r") as f:
            data = json.load(f)

        for reminder in data:
            channel = self.client.get_channel(reminder["channel_id"])
            if channel:
                self.active_reminders[reminder["channel_id"]] = True
                self.remind_tasks[reminder["channel_id"]] = asyncio.create_task(
                    self.monitor_channel(channel, reminder["message"])
                )

async def setup(client):
    await client.add_cog(Remind(client))