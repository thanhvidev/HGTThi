import asyncio
import datetime
import re
import discord
import sqlite3
import random
from discord.ext import commands, tasks

conn = sqlite3.connect('economy.db', check_same_thread=False)
cursor = conn.cursor()

diemlove = "<a:emoji_50:1273622387358957618>"
emoji_voice = '<:voice:1213059894828335115>'
emoji_chat = '<:chat:1213059748178559047>'

def is_guild_owner_or_bot_owner():
    async def predicate(ctx):
        return ctx.author == ctx.guild.owner or ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222
    return commands.check(predicate)

class Level(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.level_up_log_channel_id = 1211199649667616768
        self.user_experiences = {}
        self.active_check_time = {}

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        cursor.execute("SELECT user_id, last_voice FROM users WHERE user_id = ?", (member.id,))
        result = cursor.fetchone()
        if result is None:
            return
        user_id, last_voice = result

        if before.channel is None and after.channel is not None:
            cursor.execute("UPDATE users SET last_voice = ? WHERE user_id = ?", (datetime.datetime.now(), user_id))
            conn.commit()
            cursor.execute("SELECT last_voice FROM users WHERE user_id = ?", (user_id,))
            last_voice = cursor.fetchone()[0]
            if last_voice != '0':
                await self.start_check_time(user_id, member, last_voice)

        elif before.channel is not None and after.channel is None:
            cursor.execute("UPDATE users SET last_voice = ? WHERE user_id = ?", ('0', user_id))
            conn.commit()
            await self.stop_check_time(user_id)

        elif before.channel is not None and after.channel is not None:
            if last_voice != '0':
                await self.start_check_time(user_id, member, last_voice)

    async def start_check_time(self, user_id, member, last_voice):
        if user_id not in self.active_check_time:
            self.active_check_time[user_id] = asyncio.create_task(self.check_time(user_id, member, last_voice))

    async def stop_check_time(self, user_id):
        if user_id in self.active_check_time:
            self.active_check_time[user_id].cancel()
            del self.active_check_time[user_id]

    async def check_time(self, user_id, member, last_voice):
        last_voice = str(last_voice)  # Chuyển đổi sang chuỗi
        last_voice = datetime.datetime.strptime(last_voice, '%Y-%m-%d %H:%M:%S.%f')
        while True:
            await asyncio.sleep(600)  # Đợi 10 phút
            now = datetime.datetime.now()
            difference = now - last_voice
            minutes = difference.total_seconds() / 60
            if minutes >= 10 and not member.voice.self_deaf:
                experience = random.randint(5, 10)
                new_experience = experience
                cursor.execute("SELECT marry, love_marry FROM users WHERE user_id = ?", (user_id,))
                result = cursor.fetchone()
                if result is None:  
                    return
                marry_status = result[0]
                marry_love = result[1]
                matches = re.findall(r'<@(\d+)>', marry_status)
                if marry_status == '':
                    return
                if result:
                    if len(matches) == 2:  
                        user1_id = int(matches[0])
                        user2_id = int(matches[1])
                        new_experience = marry_love + experience
                        cursor.execute("UPDATE users SET love_marry = ? WHERE user_id = ? OR user_id = ?", (new_experience, user1_id, user2_id))
                        conn.commit()
                        await self.log_experience(member, experience, "voice")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.channel.id == 993153068378116127:  # ID của kênh tin nhắn
            cursor.execute("SELECT marry, love_marry FROM users WHERE user_id = ?", (message.author.id,))
            result = cursor.fetchone()
            if result is None:  
                return
            marry_status = result[0]
            marry_love = result[1]
            matches = re.findall(r'<@(\d+)>', marry_status)
            if marry_status == '':
                return
            if result:
                if len(matches) == 2:
                    user1_id = int(matches[0])
                    user2_id = int(matches[1])
                    self.user_experiences[message.author.id] = self.user_experiences.get(message.author.id, 0) + 1
                    if self.user_experiences[message.author.id] % 10 == 0:  # Kiểm tra sau mỗi 5 tin nhắn
                        experience = random.randint(5, 10)
                        new_experience = marry_love + experience
                        cursor.execute("UPDATE users SET love_marry = ? WHERE user_id = ? OR user_id = ?", (new_experience, user1_id, user2_id))
                        conn.commit()
                        await self.log_experience(message.author, experience, "chat")
        else:
            return

    # async def check_time(self, user_id, member, last_voice):
    #     last_voice = str(last_voice)  # Chuyển đổi sang chuỗi
    #     last_voice = datetime.datetime.strptime(last_voice, '%Y-%m-%d %H:%M:%S.%f')
    #     while True:
    #         await asyncio.sleep(600)  # Đợi 10 phút
    #         now = datetime.datetime.now()
    #         difference = now - last_voice
    #         minutes = difference.total_seconds() / 60
    #         if minutes >= 10 and not member.voice.self_deaf:
    #             experience = random.randint(5, 10)
    #             new_experience = experience
    #             cursor.execute("SELECT coin_kc FROM users WHERE user_id = ?", (user_id,))
    #             result = cursor.fetchone()
    #             if result:
    #                 new_experience = result[0] + experience
    #                 cursor.execute("UPDATE users SET coin_kc = ? WHERE user_id = ?", (new_experience, user_id))
    #                 conn.commit()
    #                 await self.log_experience(member, experience, "voice")

    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     if message.author.bot:
    #         return
    #     if message.channel.id == 993153068378116127:  # ID của kênh tin nhắn
    #         cursor.execute("SELECT coin_kc FROM users WHERE user_id = ?", (message.author.id,))
    #         result = cursor.fetchone()
    #         if result:
    #             self.user_experiences[message.author.id] = self.user_experiences.get(message.author.id, 0) + 1
    #             if self.user_experiences[message.author.id] % 10 == 0:  # Kiểm tra sau mỗi 5 tin nhắn
    #                 experience = random.randint(5, 10)
    #                 new_experience = result[0] + experience
    #                 cursor.execute("UPDATE users SET coin_kc = ? WHERE user_id = ?", (new_experience, message.author.id))
    #                 conn.commit()
    #                 await self.log_experience(message.author, experience, "chat")
    #     else:
    #         return
    
    async def log_experience(self, member, experience, source):
        log_channel = self.client.get_channel(self.level_up_log_channel_id)
        embed = discord.Embed(color=discord.Color.from_rgb(255,255,255))
        if log_channel:
            if source == "voice":
                embed.add_field(name=f"",value=f"{emoji_voice} **{member.mention} nhận được** **{experience}** {diemlove} **từ việc tham gia thoại**", inline=False)
                await log_channel.send(embed=embed)
            elif source == "chat":
                embed.add_field(name=f"",value=f"{emoji_chat} **{member.mention} nhận được** **{experience}** {diemlove} **từ việc chat trên sảnh**", inline=False)
                await log_channel.send(embed=embed)

    @commands.command()
    @is_guild_owner_or_bot_owner()
    async def rslevel(self, ctx, member: discord.Member = None):
        if member:
            cursor.execute("UPDATE users SET last_voice = NULL WHERE user_id = ?", (member.id,))
            conn.commit()
            await ctx.send(f"Đã cập nhật cột last_voice của thành viên {member.display_name} về NULL.")
        else:
            cursor.execute("UPDATE users SET last_voice = NULL")
            conn.commit()
            await ctx.send("Đã cập nhật cột last_voice của tất cả thành viên về NULL.")

async def setup(client):
    await client.add_cog(Level(client))