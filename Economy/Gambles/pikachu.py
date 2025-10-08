import asyncio
import discord
import random
import re
import aiosqlite
from discord.ext import commands
from Commands.Mod.list_emoji import list_emoji, lambanh_emoji, profile_emoji, sinhnhat_emoji
from utils.checks import is_bot_owner, is_admin, is_mod

# --- Biến toàn cục để lưu các người dùng đang chơi game ---
active_games = set()

# --- Phần kết nối SQLite với aiosqlite ---
async def get_database_connection():
    conn = await aiosqlite.connect('economy.db')
    await conn.execute('PRAGMA journal_mode=WAL;')
    return conn

async def is_registered(user_id):
    conn = await get_database_connection()
    async with conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
        result = await cursor.fetchone()
    await conn.close()
    return result is not None

async def add_balance(user_id, amount):
    """Cộng tiền thưởng vào balance của người chơi."""
    conn = await get_database_connection()
    await conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    await conn.commit()
    await conn.close()

def parse_emoji(emoji_str):
    m = re.match(r'<(a?):(\w+):(\d+)>', emoji_str)
    if m:
        animated, name, id_ = m.groups()
        return discord.PartialEmoji(name=name, id=int(id_), animated=bool(animated))
    return emoji_str

def is_allowed_channel_check():
    async def predicate(ctx):
        allowed_channel_ids = [1147355133622108262, 1152710848284991549, 1079170812709458031, 1207593935359320084, 1215331218124574740,1215331281878130738, 1051454917702848562, 1210296290026455140, 1210417888272318525, 1256198177246285825, 1050649044160094218, 1091208904920281098, 1238177759289806878, 1243264114483138600, 1251418765665505310, 1243440233685712906, 1237810926913323110, 1247072223861280768, 1270031327999164548, 1022533822031601766, 1065348266193063979, 1027622168181350400, 1072536912562241546, 1045395054954565652, 1273768834830041301, 1273768884885000326, 1273769291099144222, 1026627301573677147, 1035183712582766673, 1090897131486842990, 1213122881802997770, 1104362707580375120, 993153068378116127]
        if ctx.channel.id in allowed_channel_ids:
            return False
        return True
    return commands.check(predicate)

# --- Định nghĩa 10 emoji ---
emoji1 = '<:pkc1:1364074099701317632>'
emoji2 = '<:pkc2:1364074114138112091>'
emoji3 = '<:pkc3:1364074119166951444>'
emoji4 = '<:pkc4:1364074131972165752>'
emoji5 = '<:pkc5:1364074139794804821>'
emoji6 = '<:pkc6:1364074148439134268>'
emoji7 = '<:pkc7:1364074156089413732>'
emoji8 = '<:pkc8:1364074166176714762>'
emoji9 = '<:pkc9:1364074174296887349>'
emoji10 = '<:pkc10:1364074182983553145>'
emoji11 = '<:pkc11:1364074215401328760>'
emoji12 = '<:pkc12:1364074222166474854>'
emoji13 = '<:pkc13:1364074230462943233>'
emoji14 = '<:pkc14:1364074239115788349>'
emoji15 = '<:pkc15:1364074246627791008>'
emoji16 = '<:pkc16:1364074256018964590>'
emoji17 = '<:pkc17:1364074265418141766>'
emoji18 = '<:pkc18:1364074272309641267>'
emoji19 = '<:pkc19:1364074280098336778>'

start_pikachu = '<:hgtt_concu:1346055175076446239>'
pinkcoin = '<:timcoin:1192458078294122526>'

# ==============================================
# MODE A: Lệnh pikachu – Board 12 ô (6 emoji từ 10)
# ==============================================
class PikachuButton(discord.ui.Button):
    def __init__(self, index, emoji, row: int):
        self.custom_emoji = parse_emoji(emoji)
        super().__init__(style=discord.ButtonStyle.gray, label="\u200b", custom_id=str(index), row=row)
        self.index = index
        self.emoji_value = emoji  # giữ chuỗi gốc để so sánh
        self.is_revealed = False
        self.is_matched = False

    async def callback(self, interaction: discord.Interaction):
        view: PikachuView = self.view

        # Kiểm tra quyền bấm nút
        if interaction.user.id != view.author_id:
            try:
                await interaction.response.send_message("Bạn không được phép bấm nút này!", ephemeral=True)
            except discord.errors.NotFound:
                pass
            return

        if not interaction.response.is_done():
            try:
                await interaction.response.defer()
            except discord.errors.NotFound:
                pass

        async with view.lock:
            # Nếu đã có 2 nút được chọn và chúng không khớp,
            # thì khi nhấn nút mới (nút thứ 3) sẽ hiển thị emoji của nút mới,
            # sau đó reset 2 nút cũ và trừ lượt thử đi 1.
            if len(view.selected_buttons) == 2:
                btn1, btn2 = view.selected_buttons
                if btn1.emoji_value != btn2.emoji_value:
                    need_reset = True
                else:
                    need_reset = False
            else:
                need_reset = False

            # Nếu nút đã được bật hoặc đã khớp thì bỏ qua
            if self.is_revealed or self.is_matched:
                return

            # Bật nút hiện tại: hiển thị emoji của nút này
            self.is_revealed = True
            self.emoji = self.custom_emoji
            view.selected_buttons.append(self)
            try:
                await interaction.message.edit(view=view)
            except Exception:
                pass

            # Chờ 0.5 giây để hiển thị emoji
            await asyncio.sleep(0.5)
            if need_reset:
                # Reset 2 nút đầu tiên trong danh sách
                btn1, btn2 = view.selected_buttons[:2]
                btn1.is_revealed = False
                btn2.is_revealed = False
                btn1.style = discord.ButtonStyle.gray
                btn2.style = discord.ButtonStyle.gray
                btn1.emoji = None
                btn2.emoji = None
                btn1.label = "\u200b"
                btn2.label = "\u200b"
                view.attempts -= 1
                try:
                    await interaction.message.edit(
                        content=f"**{start_pikachu} Pikachu game - {interaction.user.mention}**\n**Bạn có `{view.attempts}` lượt thử và `1` phút để chơi.**",
                        view=view
                    )
                except Exception:
                    pass
                # Giữ lại nút hiện tại (nút thứ 3) trong danh sách
                view.selected_buttons = [self]
            else:
                # Nếu sau khi chọn nút hiện tại danh sách chứa 2 nút, kiểm tra ngay nếu khớp
                if len(view.selected_buttons) == 2:
                    btn1, btn2 = view.selected_buttons
                    if btn1.emoji_value == btn2.emoji_value:
                        btn1.style = discord.ButtonStyle.success
                        btn2.style = discord.ButtonStyle.success
                        btn1.is_matched = True
                        btn2.is_matched = True
                        view.selected_buttons.clear()
                        try:
                            await interaction.message.edit(view=view)
                        except Exception:
                            pass

            # Kiểm tra nếu trò chơi đã hoàn thành
            if all(button.is_matched for button in view.children):
                view.disable_all_buttons()
                view.stop_game(win=True)
                await add_balance(view.author_id, 5000)
                try:
                    await interaction.message.edit(
                        content=f"**{start_pikachu} Pikachu game - {interaction.user.mention}**\n**Xuất sắc! {interaction.user.mention} đã hoàn thành game và được thưởng 5K {list_emoji.pinkcoin}**",
                        view=view
                    )
                except Exception:
                    pass
                return

            # Nếu lượt thử hết, kết thúc game
            if view.attempts <= 0:
                view.disable_all_buttons()
                view.stop_game(win=False)
                try:
                    await interaction.message.edit(
                        content=f"**{start_pikachu} Pikachu game - {interaction.user.mention}**\n**Hết lượt, Bạn đã thua!**",
                        view=view
                    )
                except Exception:
                    pass
                return

# Board 12 ô, chọn 6 emoji ngẫu nhiên từ 10
class PikachuView(discord.ui.View):
    def __init__(self, author_id, *, timeout=60):  # 3 phút timeout
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.attempts = 6  # Số lượt thử (có thể thay đổi)
        self.selected_buttons = []  # Danh sách các nút đã mở (chưa xử lý cặp)
        self.lock = asyncio.Lock()

        # Chọn ngẫu nhiên 6 emoji từ 10, sau đó nhân đôi để tạo 12 ô
        all_emojis = [emoji1, emoji2, emoji3, emoji4, emoji5, emoji6, emoji7, emoji8, emoji9, emoji10, emoji11, emoji12, emoji13, emoji14, emoji15, emoji16, emoji17, emoji18, emoji19]
        chosen = random.sample(all_emojis, 6)
        emoji_list = chosen * 2
        random.shuffle(emoji_list)

        # Tạo 12 nút, 4 nút mỗi hàng
        for index, emoji in enumerate(emoji_list):
            row = index // 4
            self.add_item(PikachuButton(index, emoji, row))

    def disable_all_buttons(self):
        for child in self.children:
            child.disabled = True

    def stop_game(self, win: bool):
        self.disable_all_buttons()
        # Xóa người dùng khỏi active_games nếu có
        if self.author_id in active_games:
            active_games.remove(self.author_id)
        self.stop()

    async def on_timeout(self):
        self.disable_all_buttons()
        self.stop_game(win=False)

# ==============================================
# MODE B: Lệnh pikachu2 – Board 20 ô (sử dụng 10 emoji)
# ==============================================
# class PikachuButton1(discord.ui.Button):
#     def __init__(self, index, emoji, row: int):
#         self.custom_emoji = parse_emoji(emoji)
#         super().__init__(style=discord.ButtonStyle.gray, label="\u200b", custom_id=str(index), row=row)
#         self.index = index
#         self.emoji_value = emoji
#         self.is_revealed = False
#         self.is_matched = False

#     async def callback(self, interaction: discord.Interaction):
#         view: PikachuView2 = self.view

#         if interaction.user.id != view.author_id:
#             try:
#                 await interaction.response.send_message("Bạn không được phép bấm nút này!", ephemeral=True)
#             except discord.errors.NotFound:
#                 pass
#             return

#         if not interaction.response.is_done():
#             try:
#                 await interaction.response.defer()
#             except discord.errors.NotFound:
#                 pass

#         async with view.lock:
#             # Nếu nút đã được bật hoặc đã khớp thì bỏ qua
#             if self.is_revealed or self.is_matched:
#                 return

#             # Nếu đã có 1 nút được chọn trước đó, tiến hành xử lý nút thứ 2
#             if len(view.selected_buttons) == 1:
#                 first_btn = view.selected_buttons[0]
#                 self.is_revealed = True
#                 self.emoji = self.custom_emoji
#                 view.selected_buttons.append(self)
#                 try:
#                     await interaction.message.edit(view=view)
#                 except Exception:
#                     pass
#                 # Cho nút thứ 2 hiển thị emoji rồi chờ 0.1 giây trước khi so sánh
#                 await asyncio.sleep(0.1)
#                 if first_btn.emoji_value == self.emoji_value:
#                     first_btn.style = discord.ButtonStyle.success
#                     self.style = discord.ButtonStyle.success
#                     first_btn.is_matched = True
#                     self.is_matched = True
#                 else:
#                     # Reset 2 nút và trừ lượt thử 1
#                     first_btn.is_revealed = False
#                     self.is_revealed = False
#                     first_btn.style = discord.ButtonStyle.gray
#                     self.style = discord.ButtonStyle.gray
#                     first_btn.emoji = None
#                     self.emoji = None
#                     first_btn.label = "\u200b"
#                     self.label = "\u200b"
#                     view.attempts -= 1
#                     try:
#                         await interaction.message.edit(
#                             content=f"**{start_pikachu} Pikachu game khó - {interaction.user.mention}**\n**Bạn có `{view.attempts}` lượt thử và `3` phút để chơi.**",
#                             view=view
#                         )
#                     except Exception:
#                         pass
#                 view.selected_buttons.clear()
#             else:
#                 # Chưa có nút nào được chọn, bật nút hiện tại và lưu lại
#                 self.is_revealed = True
#                 self.emoji = self.custom_emoji
#                 view.selected_buttons.append(self)
#                 try:
#                     await interaction.message.edit(view=view)
#                 except Exception:
#                     pass

#             # Kiểm tra nếu trò chơi đã hoàn thành
#             if all(button.is_matched for button in view.children):
#                 view.disable_all_buttons()
#                 view.stop_game(win=True)
#                 await add_balance(view.author_id, 20000)
#                 try:
#                     await interaction.message.edit(
#                         content=f"**{start_pikachu} Pikachu game khó - {interaction.user.mention}**\n**Xuất sắc! {interaction.user.mention} đã hoàn thành game và được thưởng 30K {list_emoji.pinkcoin}**",
#                         view=view
#                     )
#                 except Exception:
#                     pass
#                 return

#             if view.attempts <= 0:
#                 view.disable_all_buttons()
#                 view.stop_game(win=False)
#                 try:
#                     await interaction.message.edit(
#                         content=f"**{start_pikachu} Pikachu game khó - {interaction.user.mention}**\n**Hết lượt, Bạn đã thua!**",
#                         view=view
#                     )
#                 except Exception:
#                     pass
#                 return

# Board 20 ô, sử dụng 10 emoji (mỗi emoji xuất hiện 2 lần)
# class PikachuView2(discord.ui.View):
#     def __init__(self, author_id, *, timeout=180):
#         super().__init__(timeout=timeout)
#         self.author_id = author_id
#         self.attempts = 10  # Số lượt thử
#         self.selected_buttons = []
#         self.lock = asyncio.Lock()

#         # Dùng tất cả 10 emoji, nhân đôi để tạo 20 ô
#         all_emojis = [emoji1, emoji2, emoji3, emoji4, emoji5, emoji6, emoji7, emoji8, emoji9, emoji10, emoji11, emoji12, emoji13, emoji14, emoji15, emoji16, emoji17, emoji18, emoji19]
#         chosen = random.sample(all_emojis, 10)
#         emoji_list = chosen * 2
#         random.shuffle(emoji_list)

#         # Tạo 20 nút, giả sử 5 nút mỗi hàng (tùy chỉnh row nếu cần)
#         for index, emoji in enumerate(emoji_list):
#             row = index // 5
#             self.add_item(PikachuButton1(index, emoji, row))

#     def disable_all_buttons(self):
#         for child in self.children:
#             child.disabled = True

#     def stop_game(self, win: bool):
#         self.disable_all_buttons()
#         if self.author_id in active_games:
#             active_games.remove(self.author_id)
#         self.stop()

#     async def on_timeout(self):
#         self.disable_all_buttons()
#         self.stop_game(win=False)

# ==============================================
# Cog tích hợp trò chơi vào bot với 2 lệnh: pikachu và pikachu2
# ==============================================
class Pikachu(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["pkc", "pkc1", "pikachu1"], description="Trò chơi tìm cặp (12 ô)")
    @commands.cooldown(1, 180, commands.BucketType.user)
    @is_allowed_channel_check()
    async def pikachu(self, ctx):
        if not await is_registered(ctx.author.id):
            await ctx.send("Bạn chưa đăng ký tài khoản! Bấm `zdk` để đăng kí")
            return

        # Kiểm tra xem người dùng đã có game đang chạy hay chưa
        if ctx.author.id in active_games:
            await ctx.send("Bạn đang có một game đang chạy, vui lòng chờ game kết thúc trước khi bắt đầu game mới!")
            return

        active_games.add(ctx.author.id)
        view = PikachuView(ctx.author.id)
        await ctx.send(
            f"**{start_pikachu} Pikachu game - {ctx.author.mention}**\n**Bạn có `{view.attempts}` lượt thử và `1` phút để chơi.**",
            view=view
        )

    @pikachu.error
    async def pikachu_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = await ctx.send(f"Vui lòng đợi `{error.retry_after:.0f}s` trước khi sử dụng lệnh này!")
            await asyncio.sleep(2)
            await msg.delete()
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error

    # @commands.command(aliases=["PIKACHU2", "pkc2"], description="Trò chơi tìm cặp khó")
    # @commands.cooldown(1, 180, commands.BucketType.user)
    # @is_allowed_channel_check()
    # async def pikachu2(self, ctx):
    #     if not await is_registered(ctx.author.id):
    #         await ctx.send("Bạn chưa đăng ký tài khoản! Bấm `zdk` để đăng kí")
    #         return

    #     # Kiểm tra xem người dùng đã có game đang chạy hay chưa
    #     if ctx.author.id in active_games:
    #         await ctx.send("Bạn đang có một game đang chạy, vui lòng chờ game kết thúc trước khi bắt đầu game mới!")
    #         return

    #     active_games.add(ctx.author.id)
    #     view = PikachuView2(ctx.author.id)
    #     await ctx.send(
    #         f"**{start_pikachu} Pikachu game khó - {ctx.author.mention}**\n**Bạn có `{view.attempts}` lượt thử và `3` phút để chơi.**",
    #         view=view
    #     )

    # @pikachu2.error
    # async def pikachu1_error(self, ctx, error):
    #     if isinstance(error, commands.CommandOnCooldown):
    #         msg = await ctx.send(f"Vui lòng đợi `{error.retry_after:.0f}s` trước khi sử dụng lệnh này!")
    #         await asyncio.sleep(2)
    #         await msg.delete()
    #     elif isinstance(error, commands.CheckFailure):
    #         pass
    #     else:
    #         raise error

async def setup(client):
    await client.add_cog(Pikachu(client))