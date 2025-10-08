import asyncio
import json
import typing
import discord
import random
import sqlite3
import datetime
from discord.ext import commands
from Commands.Mod.list_emoji import list_emoji, lambanh_emoji, profile_emoji, sinhnhat_emoji
from utils.checks import is_bot_owner, is_admin, is_mod

# Kết nối và tạo bảng trong SQLite
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

tienhatgiong = "<:timcoin:1192458078294122526>"
dk = "<:profile:1181400074127945799>"
dung = "<:hgtt_dung:1186838952544575538>"
sai = "<:hgtt_sai:1186839020974657657>"
chamhoi = "<:hoi:1186839345878007810>"
so2 = '<:so2:1193863285263573063>'
so3 = '<:so3:1193863283195793540>'
so4 = '<:so4:1193863279391555595>'
so5 = '<:so5:1193878218445426708>'
so6 = '<:so6:1193863275885113364>'
so7 = '<:so7:1193863273473392742>'
so8 = '<:so8:1193863269786599464>'
so9 = '<:so9:1193863267773329408>'
so10 = '<:so10:1193863263901990912>'
soJ = '<:soJ:1193863260110327898>'
soQ = '<:soQ:1193863256436129883>'
soK = '<:soK:1193863254338961428>'
soA = '<:soA:1193863250320838726>'
so0 = '<:so0:1193865318922207232>'

def is_allowed_channel_check():
    async def predicate(ctx):
        allowed_channel_ids = [993153068378116127, 1147355133622108262, 1152710848284991549, 1079170812709458031, 1207593935359320084, 1215331218124574740,1215331281878130738, 1051454917702848562, 1210296290026455140, 1210417888272318525, 1256198177246285825, 1050649044160094218, 1091208904920281098, 1238177759289806878, 1243264114483138600, 1251418765665505310, 1243440233685712906, 1237810926913323110, 1247072223861280768, 1270031327999164548, 1022533822031601766, 1065348266193063979, 1027622168181350400, 1072536912562241546, 1045395054954565652, 1273769137985818624,1273769188988682360, 1273769291099144222, 1026627301573677147, 1035183712582766673, 1090897131486842990, 1213122881802997770, 1104362707580375120]
        if ctx.channel.id in allowed_channel_ids:
            return False
        return True
    return commands.check(predicate)

class Blackjack(commands.Cog):
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

    @commands.command(aliases=['bj'])
    @commands.cooldown(1, 20, commands.BucketType.user)
    @is_allowed_channel_check()
    async def blackjack(self, ctx, bet_amount: typing.Union[int, str] = 1):
        if await self.check_command_disabled(ctx):
            return
        if not is_registered(ctx.author.id):
            await ctx.send(f"{dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
            return
        conn = get_database_connection()
        cursor = conn.cursor()        
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (ctx.author.id,))
        result = cursor.fetchone()
        balance = result[2] if result[2] is not None else 0

        if balance == 0:
            await ctx.send("Còn ngàn bạc đâu mà chơi")
            return

        if bet_amount == "all":
            if balance >= 100000:
                bet_amount = 100000
            elif 0 < balance < 100000:
                bet_amount = balance
        else:
            try:
                bet_amount = int(bet_amount)
                if bet_amount > 100000:
                    await ctx.send("Bạn chỉ có thể đặt cược tối đa 100.000!")
                    return
            except ValueError:
                await ctx.send("Số tiền đặt cược không hợp lệ!")
                return
            
        if bet_amount < 0:
            await ctx.send("Số tiền đặt cược không hợp lệ!")
            return
        elif bet_amount > balance:
            await ctx.send("Bạn không đủ tiền cược!")
            return

        cursor.execute("SELECT * FROM users WHERE user_id = ?", (ctx.author.id,))
        result = cursor.fetchone()
        user_money = result[2]
        formatted_balance = "{:,}".format(bet_amount)
        if bet_amount > user_money:
            await ctx.send("Còn ngàn bạc nào đâu mà đặt cược!")
            return
        # Ánh xạ giữa lá bài và emoji
        card_emojis = {
            2: f'{so2}', 3: f'{so3}', 4: f'{so4}', 5: f'{so5}', 6: f'{so6}', 7: f'{so7}', 8: f'{so8}', 9: f'{so9}', 10: f'{so10}',
            'J': f'{soJ}', 'Q': f'{soQ}', 'K': f'{soK}', 'A': f'{soA}'
        }
        # Tạo bộ bài
        cards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'K', 'Q', 'A'] * 4
        # Tạo bộ bài của người chơi
        player_cards = []
        player_cards.append(random.choice(cards))
        player_cards.append(random.choice(cards))
        # Tạo bộ bài của máy
        dealer_cards = []
        dealer_cards.append(random.choice(cards))
        dealer_cards.append(random.choice(cards))
        # Tính điểm của người chơi
        player_score = 0
        for card in player_cards:
            if card == 'J' or card == 'K' or card == 'Q':
                player_score += 10
            elif card == 'A':
                if player_score >= 11:
                    player_score += 1
                else:
                    player_score += 11
            else:
                player_score += card

        # Tính điểm của máy
        dealer_score = 0
        for card in dealer_cards:
            if card == 'J' or card == 'K' or card == 'Q':
                dealer_score += 10
            elif card == 'A':
                if dealer_score >= 11:
                    dealer_score += 1
                else:
                    dealer_score += 11
            else:
                dealer_score += card
        
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (bet_amount, ctx.author.id))
        conn.commit()
        winnings = bet_amount + bet_amount       
        # Gửi tin nhắn cho người chơi
        embed = discord.Embed(
            color=discord.Color.from_rgb(255, 192, 203), description=f"")
        if ctx.author.avatar:
            avatar_url = ctx.author.avatar.url
        else:
            avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
        embed.set_author(name=f"{ctx.author.display_name}, bạn đã đặt cược {formatted_balance} ", icon_url=avatar_url)
        embed.add_field(name=f"Bài của bạn: **`[{player_score}]`**", value=f"{card_emojis[player_cards[0]]} {card_emojis[player_cards[1]]}", inline=False)
        embed.add_field(name=f"Bài của HGTT: **`[?]`**", value=f"{card_emojis[dealer_cards[0]]} {so0}", inline=False)
        message = await ctx.send(embed=embed)
        # Thêm các emoji vào tin nhắn
        await message.add_reaction(dung)
        await message.add_reaction(sai)
        # Hàm kiểm tra xem người chơi có phải là người gửi tin nhắn hay không
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in [dung, sai]
        # Chờ người chơi phản hồi
        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=15.0, check=check)
        except asyncio.TimeoutError:
            await message.delete()
            message1 = await ctx.send(f"bạn bị trừ {bet_amount} {list_emoji.pinkcoin} vì hết thời gian phản hồi!")
            await asyncio.sleep(2)
            await message1.delete()
            return
        else:
            if str(reaction.emoji) == dung:
                # Nếu người chơi chọn rút thêm bài
                while True:
                    # Rút thêm bài
                    player_cards.append(random.choice(cards))
                    # Tính điểm của người chơi
                    player_score = 0
                    for card in player_cards:
                        if card == 'J' or card == 'K' or card == 'Q':
                            player_score += 10
                        elif card == 'A':
                            if player_score >= 11:
                                player_score += 1
                            else:
                                player_score += 11
                        else:
                            player_score += card
                    # Nếu người chơi có 21 điểm hoặc hơn thì dừng rút bài
                    if player_score >= 21:
                        break
                    # Tạo embed
                    embed = discord.Embed(
                        color=discord.Color.from_rgb(255, 192, 203), description=f"")
                    if ctx.author.avatar:
                        avatar_url = ctx.author.avatar.url
                    else:
                        avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
                    embed.set_author(name=f"{ctx.author.display_name}, bạn đã đặt cược {formatted_balance} ", icon_url=avatar_url)
                    embed.add_field(name=f"Bài của bạn: **`[{player_score}]`**", value=' '.join(card_emojis[card] for card in player_cards), inline=False)
                    embed.add_field(name=f"Bài của HGTT: **`[?]`**", value=f"{card_emojis[dealer_cards[0]]} {so0}", inline=False)
                    await message.edit(embed=embed)
                    # Chờ người chơi phản hồi
                    try:
                        reaction, user = await self.client.wait_for('reaction_add', timeout=30.0, check=check)
                    except asyncio.TimeoutError:
                        await message.delete()
                        message1 = await ctx.send(f"bạn bị trừ {bet_amount} {list_emoji.pinkcoin} vì hết thời gian phản hồi!")
                        await asyncio.sleep(2)
                        await message1.delete()
                    else:
                        if str(reaction.emoji) == sai:
                            break
                # Tính điểm của máy
                dealer_score = 0
                for card in dealer_cards:
                    if card == 'J' or card == 'K' or card == 'Q':
                        dealer_score += 10
                    elif card == 'A':
                        if dealer_score >= 11:
                            dealer_score += 1
                        else:
                            dealer_score += 11
                    else:
                        dealer_score += card
                # Rút thêm bài cho máy
                while dealer_score < 17:
                    dealer_cards.append(random.choice(cards))
                    dealer_score = 0
                    for card in dealer_cards:
                        if card == 'J' or card == 'K' or card == 'Q':
                            dealer_score += 10
                        elif card == 'A':
                            if dealer_score >= 11:
                                dealer_score += 1
                            else:
                                dealer_score += 11
                        else:
                            dealer_score += card
                # Tạo embed
                embed = discord.Embed(
                    color=discord.Color.from_rgb(255, 192, 203), description=f"")
                if ctx.author.avatar:
                    avatar_url = ctx.author.avatar.url
                else:
                    avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
                embed.set_author(name=f"{ctx.author.display_name}, bạn đã đặt cược {formatted_balance} ", icon_url=avatar_url)
                embed.add_field(name=f"Bài của bạn: **`[{player_score}]`**", value=' '.join(card_emojis[card] for card in player_cards), inline=False)
                embed.add_field(name=f"Bài của HGTT: **`[{dealer_score}]`**", value=' '.join(card_emojis[card] for card in dealer_cards))
                await message.edit(embed=embed)
                # Kiểm tra kết quả
                if player_score > 21 and dealer_score > 21:
                    embed = discord.Embed(
                        color=discord.Color.from_rgb(255,255,0), description=f"")
                    if ctx.author.avatar:
                        avatar_url = ctx.author.avatar.url
                    else:
                        avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
                    embed.set_author(name=f"{ctx.author.display_name}, bạn đã đặt cược {formatted_balance} ", icon_url=avatar_url)
                    embed.add_field(name=f"Bài của bạn: **`[{player_score}]`**", value=' '.join(card_emojis[card] for card in player_cards), inline=False)
                    embed.add_field(name=f"Bài của HGTT: **`[{dealer_score}]`**", value=' '.join(card_emojis[card] for card in dealer_cards))
                    embed.set_footer(text=f"Kết quả: Hoà")
                    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (bet_amount, ctx.author.id))
                    conn.commit()
                    await message.edit(embed=embed)
                elif player_score == dealer_score:
                    embed = discord.Embed(
                        color=discord.Color.from_rgb(255,255,0), description=f"")
                    if ctx.author.avatar:
                        avatar_url = ctx.author.avatar.url
                    else:
                        avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
                    embed.set_author(name=f"{ctx.author.display_name}, bạn đã đặt cược {formatted_balance} ", icon_url=avatar_url)
                    embed.add_field(name=f"Bài của bạn: **`[{player_score}]`**", value=' '.join(card_emojis[card] for card in player_cards), inline=False)
                    embed.add_field(name=f"Bài của HGTT: **`[{dealer_score}]`**", value=' '.join(card_emojis[card] for card in dealer_cards))
                    embed.set_footer(text=f"Kết quả: Hoà")
                    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (bet_amount, ctx.author.id))
                    conn.commit()
                    await message.edit(embed=embed)
                elif player_score > 21:
                    embed = discord.Embed(
                        color=discord.Color.from_rgb(255,0,0), description=f"")
                    if ctx.author.avatar:
                        avatar_url = ctx.author.avatar.url
                    else:
                        avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
                    embed.set_author(name=f"{ctx.author.display_name}, bạn đã đặt cược {formatted_balance} ", icon_url=avatar_url)
                    embed.add_field(name=f"Bài của bạn: **`[{player_score}]`**", value=' '.join(card_emojis[card] for card in player_cards), inline=False)
                    embed.add_field(name=f"Bài của HGTT: **`[{dealer_score}]`**", value=' '.join(card_emojis[card] for card in dealer_cards))
                    embed.set_footer(text=f"Bạn đã thua {formatted_balance}")
                    await message.edit(embed=embed)
                elif dealer_score > 21:
                    embed = discord.Embed(
                        color=discord.Color.from_rgb(0, 255, 0), description=f"")
                    if ctx.author.avatar:
                        avatar_url = ctx.author.avatar.url
                    else:
                        avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
                    embed.set_author(name=f"{ctx.author.display_name}, bạn đã đặt cược {formatted_balance} ", icon_url=avatar_url)
                    embed.add_field(name=f"Bài của bạn: **`[{player_score}]`**", value=' '.join(card_emojis[card] for card in player_cards), inline=False)
                    embed.add_field(name=f"Bài của HGTT: **`[{dealer_score}]`**", value=' '.join(card_emojis[card] for card in dealer_cards))
                    embed.set_footer(text=f"Bạn đã thắng {formatted_balance}")
                    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (winnings, ctx.author.id))
                    conn.commit()
                    await message.edit(embed=embed)
                elif player_score > dealer_score:
                    embed = discord.Embed(
                        color=discord.Color.from_rgb(0, 255, 0), description=f"")
                    if ctx.author.avatar:
                        avatar_url = ctx.author.avatar.url
                    else:
                        avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
                    embed.set_author(name=f"{ctx.author.display_name}, bạn đã đặt cược {formatted_balance} ", icon_url=avatar_url)
                    embed.add_field(name=f"Bài của bạn: **`[{player_score}]`**", value=' '.join(card_emojis[card] for card in player_cards), inline=False)
                    embed.add_field(name=f"Bài của HGTT: **`[{dealer_score}]`**", value=' '.join(card_emojis[card] for card in dealer_cards))
                    embed.set_footer(text=f"Bạn đã thắng {formatted_balance}")
                    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (winnings, ctx.author.id))
                    conn.commit()
                    await message.edit(embed=embed)
                else:
                    embed = discord.Embed(
                        color=discord.Color.from_rgb(255,0,0), description=f"")
                    if ctx.author.avatar:
                        avatar_url = ctx.author.avatar.url
                    else:
                        avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
                    embed.set_author(name=f"{ctx.author.display_name}, bạn đã đặt cược {formatted_balance} ", icon_url=avatar_url)
                    embed.add_field(name=f"Bài của bạn: **`[{player_score}]`**", value=' '.join(card_emojis[card] for card in player_cards), inline=False)
                    embed.add_field(name=f"Bài của HGTT: **`[{dealer_score}]`**", value=' '.join(card_emojis[card] for card in dealer_cards))
                    embed.set_footer(text=f"Bạn đã thua {formatted_balance}")
                    await message.edit(embed=embed)
            else:
                # Nếu người chơi không rút thêm bài
                # Tính điểm của máy
                dealer_score = 0
                for card in dealer_cards:
                    if card == 'J' or card == 'K' or card == 'Q':
                        dealer_score += 10
                    elif card == 'A':
                        if dealer_score >= 11:
                            dealer_score += 1
                        else:
                            dealer_score += 11
                    else:
                        dealer_score += card
                # Rút thêm bài cho máy
                while dealer_score < 17:
                    dealer_cards.append(random.choice(cards))
                    dealer_score = 0
                    for card in dealer_cards:
                        if card == 'J' or card == 'K' or card == 'Q':
                            dealer_score += 10
                        elif card == 'A':
                            if dealer_score >= 11:
                                dealer_score += 1
                            else:
                                dealer_score += 11
                        else:
                            dealer_score += card
                # Tạo embed
                embed = discord.Embed(
                    color=discord.Color.from_rgb(255, 192, 203), description=f"")
                if ctx.author.avatar:
                    avatar_url = ctx.author.avatar.url
                else:
                    avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
                embed.set_author(name=f"{ctx.author.display_name}, bạn đã đặt cược {formatted_balance} ", icon_url=avatar_url)
                embed.add_field(name=f"Bài của bạn: **`[{player_score}]`**", value=f"{card_emojis[player_cards[0]]} {card_emojis[player_cards[1]]}", inline=False)
                embed.add_field(name=f"Bài của HGTT: **`[{dealer_score}]`**", value=' '.join(card_emojis[card] for card in dealer_cards))
                await message.edit(embed=embed)
                # Kiểm tra kết quả
                if player_score > 21 and dealer_score > 21:
                    embed = discord.Embed(
                        color=discord.Color.from_rgb(255,255,0), description=f"")
                    if ctx.author.avatar:
                        avatar_url = ctx.author.avatar.url
                    else:
                        avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
                    embed.set_author(name=f"{ctx.author.display_name}, bạn đã đặt cược {formatted_balance} ", icon_url=avatar_url)
                    embed.add_field(name=f"Bài của bạn: **`[{player_score}]`**", value=f"{card_emojis[player_cards[0]]} {card_emojis[player_cards[1]]}", inline=False)
                    embed.add_field(name=f"Bài của HGTT: **`[{dealer_score}]`**", value=' '.join(card_emojis[card] for card in dealer_cards))
                    embed.set_footer(text=f"Kết quả: Hoà")
                    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (bet_amount, ctx.author.id))
                    conn.commit()
                    await message.edit(embed=embed)
                elif player_score == dealer_score:
                    embed = discord.Embed(
                        color=discord.Color.from_rgb(255,255,0), description=f"")
                    if ctx.author.avatar:
                        avatar_url = ctx.author.avatar.url
                    else:
                        avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
                    embed.set_author(name=f"{ctx.author.display_name}, bạn đã đặt cược {formatted_balance} ", icon_url=avatar_url)
                    embed.add_field(name=f"Bài của bạn: **`[{player_score}]`**", value=f"{card_emojis[player_cards[0]]} {card_emojis[player_cards[1]]}", inline=False)
                    embed.add_field(name=f"Bài của HGTT: **`[{dealer_score}]`**", value=' '.join(card_emojis[card] for card in dealer_cards))
                    embed.set_footer(text=f"Kết quả: Hoà")
                    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (bet_amount, ctx.author.id))
                    conn.commit()
                    await message.edit(embed=embed)
                elif player_score > 21:
                    embed = discord.Embed(
                        color=discord.Color.from_rgb(255,0,0), description=f"")
                    if ctx.author.avatar:
                        avatar_url = ctx.author.avatar.url
                    else:
                        avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
                    embed.set_author(name=f"{ctx.author.display_name}, bạn đã đặt cược {formatted_balance} ", icon_url=avatar_url)
                    embed.add_field(name=f"Bài của bạn: **`[{player_score}]`**", value=f"{card_emojis[player_cards[0]]} {card_emojis[player_cards[1]]}", inline=False)
                    embed.add_field(name=f"Bài của HGTT: **`[{dealer_score}]`**", value=' '.join(card_emojis[card] for card in dealer_cards))
                    embed.set_footer(text=f"Bạn đã thua: {formatted_balance}")
                    await message.edit(embed=embed)
                elif dealer_score > 21:
                    embed = discord.Embed(
                        color=discord.Color.from_rgb(0, 255, 0), description=f"")
                    if ctx.author.avatar:
                        avatar_url = ctx.author.avatar.url
                    else:
                        avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
                    embed.set_author(name=f"{ctx.author.display_name}, bạn đã đặt cược {formatted_balance} ", icon_url=avatar_url)
                    embed.add_field(name=f"Bài của bạn: **`[{player_score}]`**", value=f"{card_emojis[player_cards[0]]} {card_emojis[player_cards[1]]}", inline=False)
                    embed.add_field(name=f"Bài của HGTT: **`[{dealer_score}]`**", value=' '.join(card_emojis[card] for card in dealer_cards))
                    embed.set_footer(text=f"Bạn đã thắng: {formatted_balance}")
                    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (winnings, ctx.author.id))
                    conn.commit()
                    await message.edit(embed=embed)
                elif player_score > dealer_score:
                    embed = discord.Embed(
                        color=discord.Color.from_rgb(0, 255, 0), description=f"")
                    if ctx.author.avatar:
                        avatar_url = ctx.author.avatar.url
                    else:
                        avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
                    embed.set_author(name=f"{ctx.author.display_name}, bạn đã đặt cược {formatted_balance} ", icon_url=avatar_url)
                    embed.add_field(name=f"Bài của bạn: **`[{player_score}]`**", value=f"{card_emojis[player_cards[0]]} {card_emojis[player_cards[1]]}", inline=False)
                    embed.add_field(name=f"Bài của HGTT: **`[{dealer_score}]`**", value=' '.join(card_emojis[card] for card in dealer_cards))
                    embed.set_footer(text=f"Bạn đã thắng: {formatted_balance}")
                    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (winnings, ctx.author.id))
                    conn.commit()
                    await message.edit(embed=embed)
                else:
                    embed = discord.Embed(
                        color=discord.Color.from_rgb(255,0,0), description=f"")
                    if ctx.author.avatar:
                        avatar_url = ctx.author.avatar.url
                    else:
                        avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
                    embed.set_author(name=f"{ctx.author.display_name}, bạn đã đặt cược {formatted_balance} ", icon_url=avatar_url)
                    embed.add_field(name=f"Bài của bạn: **`[{player_score}]`**", value=f"{card_emojis[player_cards[0]]} {card_emojis[player_cards[1]]}", inline=False)
                    embed.add_field(name=f"Bài của HGTT: **`[{dealer_score}]`**", value=' '.join(card_emojis[card] for card in dealer_cards))
                    embed.set_footer(text=f"Bạn đã thua: {formatted_balance}")
                    await message.edit(embed=embed)

    @blackjack.error
    async def blackjack_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            message = await ctx.send("Vui lòng nhập số tiền cược!")
            await asyncio.sleep(2)
            await message.delete()
        elif isinstance(error, commands.BadArgument):
            message = await ctx.send("Số tiền cược không hợp lệ!")
            await asyncio.sleep(2)
            await message.delete()
        elif isinstance(error, commands.CommandOnCooldown):
            message = await ctx.send(f"Vui lòng đợi `{error.retry_after:.0f}s` trước khi sử dụng lệnh này!")
            await asyncio.sleep(2)
            await message.delete()
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error
        
 #--------------------------------end---------------------------------#

async def setup(client):
    await client.add_cog(Blackjack(client))