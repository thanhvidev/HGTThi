import discord
from discord.ext import commands
import openai
import sqlite3
import config
import random
import requests

# Kết nối tới cơ sở dữ liệu SQLite
conn = sqlite3.connect('economy.db')
cursor = conn.cursor()

coze_key = config.YOUR_PERSONAL_ACCESS_TOKEN
id_botcici = config.ID_BOTCICI
API_URL = 'https://nguyenmanh.name.vn/api/sim'
API_KEY = 'T3OiUYEB'

def is_guild_owner_or_bot_owner():
    async def predicate(ctx):
        return ctx.author == ctx.guild.owner or ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222
    return commands.check(predicate)

# def call_coze_api(user_query):
#     try:
#         response = requests.post('https://api.coze.com/open_api/v2/chat',
#         headers={
#             'Authorization': f'Bearer {coze_key}',
#             'Content-Type': 'application/json',
#             'Accept': '*/*',
#             'Host': 'api.coze.com',
#             'Connection': 'keep-alive'
#         },
#         json={
#             "conversation_id": "123",
#             "bot_id": f"{id_botcici}",
#             "user": "29032201862555",
#             "query": user_query,
#             "stream": False
#         })
#         response.raise_for_status()  # Raise an exception for HTTP errors

#         if response.status_code == 200:
#             data = response.json()
#             return [msg['content'] for msg in data['messages'] if msg['type'] == 'answer']
#     except requests.exceptions.RequestException as e:
#         print(f"An error occurred: {e}")

#     return None

def simsimi_api(content):
    try:
        response = requests.get(API_URL,
        params = {
            "type": "ask",
            "apikey": API_KEY,
            "ask": content
        })
        response.raise_for_status()  # Ném ra một exception cho lỗi HTTP

        if response.status_code == 200:
            data = response.json()
            if 'answer' in data:
                return [data['answer']]  # Trả về một list chứa câu trả lời
            else:
                return ["Không có câu trả lời phù hợp"]
    except requests.exceptions.RequestException as e:
        print(f"Đã xảy ra lỗi: {e}")

    return None


class Trainbot(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='sim')
    @is_guild_owner_or_bot_owner()
    async def sim(self, ctx, channel: discord.TextChannel):
        server_id = ctx.guild.id
        channel_id = channel.id

        cursor.execute('SELECT * FROM servers WHERE server_id = ?', (server_id,))
        result = cursor.fetchone()

        cursor.execute('UPDATE servers SET channel_simsimi = ? WHERE server_id = ?', (channel_id, server_id))

        conn.commit()
        await ctx.send(f'Kênh đã được đặt thành: {channel.mention}')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return
        cursor.execute('SELECT channel_simsimi FROM servers WHERE server_id = ?', (message.guild.id,))
        result = cursor.fetchone()
        if result is None:
            return
        self.channel_id = result[0]
        if message.channel.id != self.channel_id:
            return
        if message.author.bot:
            return
        content = message.content
        response = simsimi_api(content)
        if response:
            for resp in response:
                await message.reply(resp)

    @commands.command(name='daysim')
    @is_guild_owner_or_bot_owner()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def daysim(self, ctx, ask, ans):
        params = {
            "type": "teach",
            "ask": ask,
            "ans": ans,
            "by": ctx.author.name,
            "apikey": API_KEY
        }

        try:
            response = requests.get(API_URL, params=params)
            response.raise_for_status()

            if response.status_code == 200:
                data = response.json()
                if 'msg' in data and data['msg'] == "Dạy sim thành công":
                    teach_data = data.get('data', {})
                    ask = teach_data.get('ask', '')
                    ans = teach_data.get('ans', '')
                    by = teach_data.get('by', '')
                    time = teach_data.get('time', '')

                    if ask == teach_data.get('original_ask', ''):
                        await ctx.send(f"Từ '{ask}' đã được dạy trước đó.")
                    else:
                        await ctx.send(f"Dạy sim cho từ '{ask}' với câu trả lời '{ans}' được thêm bởi {by} vào lúc {time}")
                else:
                    await ctx.send("Đã xảy ra lỗi khi dạy sim.")
        except requests.exceptions.RequestException as e:
            print(f"Đã xảy ra lỗi: {e}")
            await ctx.send("Đã xảy ra lỗi khi gửi yêu cầu dạy tới API.")

    @daysim.error
    async def daysim_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Vui lòng nhập đủ thông tin cần thiết để dạy sim.")
        elif isinstance(error, commands.CheckFailure):
            await ctx.send("Bạn không có quyền thực hiện lệnh này.")
        else:
            await ctx.send("Đã xảy ra lỗi khi thực hiện lệnh.")