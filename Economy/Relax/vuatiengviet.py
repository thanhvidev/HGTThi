import asyncio
import sqlite3
import discord
from discord.ext import commands
import json
import random
import easy_pil
import requests
from Economy.Relax.cache.list_color import list_color
import os
import time as pyTime
from Commands.Mod.list_emoji import list_emoji, lambanh_emoji, profile_emoji, sinhnhat_emoji

maytinh = "<:maytinh:1271305161989427250>"
dongho = "<:emoji_54:1273740687359344720>"
hopqua = "<:emoji_54:1273745122915516592> "
pinkcoin = "<:timcoin:1192458078294122526>"
dung = "<a:dung:1271305150492835924>"
sai = "<:sai:1271305088350027853>"
dk = "<:profile:1181400074127945799>"
maychoigame = "<a:chamhoi:1215618463318413342>"
votay = "<a:votay:1271305102011138048>"
xulove = '<a:xu_love_2025:1339490786840150087>'

def get_database_connection():
    conn = sqlite3.connect('economy.db', isolation_level=None)
    conn.execute('PRAGMA journal_mode=WAL;')
    return conn

def is_registered(user_id):
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def get_balance(user_id):  
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    balance = cursor.fetchone()
    conn.close()
    if balance:
        return balance[0]
    return None

def is_allowed_channel_check():
    async def predicate(ctx):
        allowed_channel_ids = [993153068378116127, 1147355133622108262, 1152710848284991549, 1079170812709458031, 
                                1207593935359320084, 1215331218124574740, 1215331281878130738, 1051454917702848562, 
                                1210296290026455140, 1210417888272318525, 1256198177246285825, 1050649044160094218, 
                                1091208904920281098, 1238177759289806878, 1243264114483138600, 1251418765665505310, 
                                1243440233685712906, 1237810926913323110, 1247072223861280768, 1270031327999164548, 
                                1022533822031601766, 1065348266193063979, 1027622168181350400, 1072536912562241546, 
                                1045395054954565652, 1273768834830041301, 1273768884885000326, 1273769291099144222, 
                                1026627301573677147, 1035183712582766673, 1090897131486842990, 1213122881802997770, 
                                1104362707580375120]
        if ctx.channel.id in allowed_channel_ids:
            return False
        return True
    return commands.check(predicate)

def is_allowed_channel():
    async def predicate(ctx):
        allowed_channel_id = 1273769137985818624
        if ctx.channel.id != allowed_channel_id:
            message = await ctx.reply(f"**Dùng lệnh** [__**ở đây**__](<https://discord.com/channels/832579380634451969/1273769137985818624>)")
            await asyncio.sleep(10)
            await message.delete()
            await ctx.message.delete()
            return False
        return True
    return commands.check(predicate)

class Vtv(commands.Cog):
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

    @commands.hybrid_command(aliases=["vtv", "vuatv"], description="Trò chơi vua tiếng việt")
    @commands.cooldown(1, 45, commands.BucketType.user)
    @is_allowed_channel_check()
    async def vuatiengviet(self, ctx):
        if await self.check_command_disabled(ctx):
            return
        if not is_registered(ctx.author.id):
            await ctx.send(f"{dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
            return
        
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (ctx.author.id,))
        result = cursor.fetchone()
        balance = result[2]
        await ctx.defer()
        try:
            response = requests.get('https://raw.githubusercontent.com/undertheseanlp/dictionary/master/dictionary/words.txt')
            word_list = response.text.split('\n')
            list_word = []
            for i in word_list:
                try:
                    text = json.loads(i)['text']
                    if len(text.split(' ')) == 2:
                        list_word.append(text)
                except:
                    continue
            word = random.choice(list_word).strip('-')
            # Tạo dạng xáo trộn của từ cần đoán
            scrambled_chars = list(word.replace(" ", ""))
            random.shuffle(scrambled_chars)
            scrambled_text = " /".join(scrambled_chars) + " /"
            # Tạo ảnh sử dụng easy_pil
            img = easy_pil.Editor(os.path.join(os.path.dirname(__file__), 'cache', "vuatiengviet_background.jpg"))
            img.resize((1080, 832))
            img.text(position=(540, 680), text=scrambled_text, font=easy_pil.font.Font.montserrat(variant='bold', size=30), align="center")
            time_duration = 45
            end_time = pyTime.time() + time_duration
            msg_content = (f'# {maychoigame} VUA TIẾNG VIỆT {maychoigame}\nㅤ\n'
                           f'{dongho} **{ctx.author.mention}, reply tin nhắn này để trả lời câu hỏi, '
                           f'đếm ngược: <t:{int(end_time)}:R> | {hopqua}: 5k {list_emoji.pinkcoin}**')
            msg1 = await ctx.send(msg_content, file=discord.File(img.image_bytes, filename='vuatiengviet.png'))

            def check(m):
                return (m.author.id == ctx.author.id and m.channel == ctx.channel and 
                        m.reference is not None and m.reference.message_id == msg1.id)

            try:
                message = await self.client.wait_for("message", timeout=time_duration, check=check)
                if message:
                    if message.content.lower() == word.lower():
                        if discord.utils.get(ctx.author.roles, id=1339482195907186770):
                            cursor.execute("UPDATE users SET balance = balance + 5000 WHERE user_id = ?", (ctx.author.id,))
                            conn.commit()
                            await ctx.send(f"{votay} **Chính xác, đáp án là :** __**{word}**__. **Bạn được thưởng 5k** {list_emoji.pinkcoin}")
                        else:
                            cursor.execute("UPDATE users SET balance = balance + 5000 WHERE user_id = ?", (ctx.author.id,))
                            conn.commit()
                            await ctx.send(f"{votay} **Chính xác, đáp án là :** __**{word}**__. **Bạn được thưởng 5k** {list_emoji.pinkcoin}")
                    else:
                        await ctx.send(f'{sai} **Sai rồi má, đáp án là** : "**{word}**"')
                    # Cập nhật tin nhắn gốc để hiển thị đồng hồ hết giờ
                    try:
                        await msg1.edit(content=(f'# {maychoigame} VUA TIẾNG VIỆT {maychoigame}\nㅤ\n'
                                                 f'{dongho} **{ctx.author.mention}, reply tin nhắn này để trả lời câu hỏi, '
                                                 f'đếm ngược: 0 giây | {hopqua}: 5k {list_emoji.pinkcoin}**'))
                    except discord.HTTPException as e:
                        print("Error editing message:", e)
            except asyncio.TimeoutError:
                await ctx.send(f"{dongho} **Hết giờ rồi {ctx.author.mention} ơi, làm lại ván mới đi**")
                try:
                    await msg1.edit(content=(f'# {maychoigame} VUA TIẾNG VIỆT {maychoigame}\nㅤ\n'
                                             f'{dongho} **{ctx.author.mention}, reply tin nhắn này để trả lời câu hỏi, '
                                             f'đếm ngược: 0 giây | {hopqua}: 5k {list_emoji.pinkcoin}**'))
                except discord.HTTPException as e:
                    print("Error editing message on timeout:", e)
            conn.close()
        except Exception as e:
            print(e)
            await ctx.send('Hiện tại lệnh bạn đang sử dụng đã gặp lỗi, hãy thử lại sau. Xin lỗi vì sự cố này')

    @vuatiengviet.error
    async def vuatiengviet_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            message = await ctx.send(f"Vui lòng đợi `{error.retry_after:.0f}s` trước khi sử dụng lệnh này!")
            await asyncio.sleep(2)
            await message.delete()
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error

async def setup(client):
    await client.add_cog(Vtv(client))