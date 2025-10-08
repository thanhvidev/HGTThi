import asyncio
import json
import random
import sqlite3
import datetime
import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
from Commands.Mod.list_emoji import list_emoji
from datetime import datetime, date, time, timedelta, timezone

# --------------------------------------------
# Configuration & Database Setup
# --------------------------------------------
DB_PATH = 'economy.db'
QUESTIONS_PATH = 'questions.json'
DAILY_LIMIT = 20
# START_DATE = datetime.date(2025, 4, 21)
# END_DATE = datetime.date(2025, 4, 30)
TOTAL_PIECES = 44

conn = sqlite3.connect(DB_PATH, isolation_level=None)
conn.execute('PRAGMA journal_mode = WAL')
cursor = conn.cursor()

# Create necessary tables
cursor.executescript('''
CREATE TABLE IF NOT EXISTS answered (
    user_id INTEGER,
    question_id INTEGER,
    answered_at TEXT,
    PRIMARY KEY (user_id, question_id)
);

CREATE TABLE IF NOT EXISTS pieces (
    user_id INTEGER,
    piece_index INTEGER,
    awarded_at TEXT,
    PRIMARY KEY (user_id, piece_index)
);

CREATE TABLE IF NOT EXISTS flag_pieces (
    user_id INTEGER PRIMARY KEY,
    flags_completed INTEGER NOT NULL DEFAULT 0
);            
''')

# Load questions from JSON
with open(QUESTIONS_PATH, 'r', encoding='utf-8') as f:
    QUESTIONS = json.load(f)

# múi giờ UTC+7
TZ = timezone(timedelta(hours=7))

def get_now() -> datetime:
    """Trả về datetime hiện tại (có timezone UTC+7)."""
    return datetime.now(TZ)

def get_cutoff() -> datetime:
    now = get_now()
    today = now.date()
    today_cutoff = datetime.combine(today, time(14, 0, 0), tzinfo=TZ)
    if now < today_cutoff:
        # chưa tới 14h hôm nay → lấy 14h ngày hôm trước
        return today_cutoff - timedelta(days=1)
    else:
        # đã hoặc bằng 14h hôm nay
        return today_cutoff

def has_reached_daily_limit(user_id: int) -> bool:
    start = get_cutoff()
    end = get_now()
    cursor.execute(
        """
        SELECT COUNT(*) 
          FROM answered 
         WHERE user_id = ?
           AND answered_at >= ?
           AND answered_at <= ?
        """,
        (user_id, start.isoformat(), end.isoformat())
    )
    count = cursor.fetchone()[0]
    return count >= DAILY_LIMIT

def mark_answered(user_id: int, qid: int):
    today = get_now().isoformat()
    cursor.execute(
        "INSERT OR IGNORE INTO answered (user_id, question_id, answered_at) VALUES (?, ?, ?)",
        (user_id, qid, today)
    )

def get_today_count(user_id: int) -> int:
    cursor.execute(
        "SELECT COUNT(*) FROM answered WHERE user_id = ?",
        (user_id,)
    )
    return cursor.fetchone()[0]


def assign_piece(user_id: int) -> int:
    # 1. Đếm xem user đã có bao nhiêu mảnh
    cursor.execute("SELECT COUNT(*) FROM pieces WHERE user_id = ?", (user_id,))
    total_awarded = cursor.fetchone()[0]

    # 2. Tính chỉ số của mảnh sẽ trao
    next_idx = (total_awarded % TOTAL_PIECES) + 1

    # 3. Nếu chuẩn bị gán mảnh thứ 44 → tăng cờ hoàn thành
    if next_idx == TOTAL_PIECES:
        cursor.execute(
            """
            INSERT INTO flag_pieces (user_id, flags_completed)
            VALUES (?, 1)
            ON CONFLICT(user_id) DO UPDATE
              SET flags_completed = flags_completed + 1
            """,
            (user_id,)
        )

    # 4. Nếu chuẩn bị gán mảnh thứ 1 mà đã có mảnh cũ (tức đang qua chu kỳ) → xóa mảnh cũ
    if next_idx == 1 and total_awarded != 0:
        cursor.execute("DELETE FROM pieces WHERE user_id = ?", (user_id,))

    # 5. Chèn mảnh mới
    cursor.execute(
        "INSERT INTO pieces (user_id, piece_index, awarded_at) VALUES (?, ?, ?)",
        (user_id, next_idx, datetime.utcnow().isoformat())
    )
    return next_idx


def get_completed_flags(user_id: int) -> int:
    cursor.execute(
        "SELECT flags_completed FROM flag_pieces WHERE user_id = ?", (user_id,)
    )
    row = cursor.fetchone()
    return row[0] if row else 0

def get_user_pieces(user_id: int):
    cursor.execute(
        "SELECT piece_index FROM pieces WHERE user_id = ? ORDER BY awarded_at",
        (user_id,)
    )
    all_pieces = [r[0] for r in cursor.fetchall()]

    if not all_pieces:
        return []

    # cycle hiện tại = floor((total-1)/TOTAL_PIECES)
    cycle = (len(all_pieces) - 1) // TOTAL_PIECES
    start = cycle * TOTAL_PIECES
    return all_pieces[start:]

# Format flag embed with reset logic when full

def format_flag_embed(
    pieces: list[int],
    *,
    last_idx: int | None = None,
    author: discord.User
) -> discord.Embed:
    rows, cols = 5, 9
    center_slot = (rows * cols) // 2 + 1

    remainder_pieces = len(pieces)
    completed_flags = get_completed_flags(author.id)

    grid = []
    current = 1
    for r in range(rows):
        row = []
        for c in range(cols):
            slot = r * cols + c + 1
            if slot == center_slot:
                emoji = ngoisao
            else:
                if current in pieces or (last_idx is not None and current == last_idx):
                    emoji = codo
                else:
                    emoji = trong
                current += 1
            row.append(emoji)
        grid.append(''.join(row))

    embed = discord.Embed(
        description='\n'.join(grid),
        color=discord.Color.from_rgb(255, 236, 25)
    )
    avatar = author.avatar.url if author.avatar else "https://cdn.discordapp.com/embed/avatars/0.png"
    embed.set_author(name=f"{author.display_name} chơi ghép cờ", icon_url=avatar)
    embed.set_footer(
        text=f"Mảnh hiện tại: {remainder_pieces}  |  Cờ hoàn chỉnh: {completed_flags}"
    )
    return embed


def is_registered(user_id):
    cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None

def is_allowed_channel_check():
    async def predicate(ctx):
        # Nếu ctx.channel.id khác với ID được phép thì trả về False
        if ctx.channel.id != 1295144686536888340:
            # dauxdo phải là một biến/string đã được định nghĩa từ trước
            await ctx.send(f"{dauxdo} **Dùng lệnh** **`zcauhoi`** [__**ở đây**__]"
                           f"(https://discord.com/channels/832579380634451969/1295144686536888340)")
            return False
        return True
    return commands.check(predicate)

def is_allowed_channel():
    async def predicate(ctx):
        allowed_channel_ids = [1273768834830041301, 1273769137985818624, 993153068378116127, 1026627301573677147, 1035183712582766673, 1090897131486842990, 1213122881802997770, 1147355133622108262, 1295144686536888340, 1207593935359320084]
        if ctx.channel.id not in allowed_channel_ids:
            await ctx.send(f"{dauxdo} **Dùng lệnh** **`zco`** [__**ở đây**__](<https://discord.com/channels/832579380634451969/1147355133622108262>)")
            return False
        return True
    return commands.check(predicate)

codo = '<:maudo:1364056933538988202>'
ngoisao = '<:sao_covn:1364056926014668821>'
trong = '<:trong:1314626864639115275>'
tickdo = '<:tick_do:1362461014238560477>'
tickxanh = '<a:tick_xanhla:1362461009373040872>'
phaohoa = '<a:phaohoahong:1358024352318357574>'
chu_a = '<:chu_A:1362985409843298365>'
chu_b = '<:chu_B:1362985417586114644>'
chu_c = '<:chu_C:1362985427535134720>'
chu_d = '<:chu_D:1362985433834852412>'
dongho = '<a:time:1362955677907288296>'
traitim = '<a:qua_nonla:1362785090198831156>'
ngoisaochay = '<a:ngoisaochay:1362990241430110309>'
dauxdo = "<a:hgtt_check:1246910030444495008>"


class Cauhoi30_4(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    @is_allowed_channel_check()
    async def cauhoi(self, ctx):
        user_id = ctx.author.id
        # Kiểm tra đăng ký
        if not is_registered(user_id):
            return await ctx.reply(
                f"{list_emoji.dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí",
                ephemeral=True
            )
        # Giới hạn số câu hỏi/ngày
        if has_reached_daily_limit(user_id):
            return await ctx.reply(
                f"{ngoisaochay} **đã xuất sắc hoàn thành** **`20`** **câu hỏi của ngày hôm nay, hẹn bạn vào** **`14H`** **ngày mai nhé!**",
            )
        # Gửi nút nhận câu hỏi
        view = NhanCauHoiView(user_id)
        msg = await ctx.reply(
            f"__**Minigame:**__\n# {list_emoji.xu_event} Người con đất Việt {list_emoji.xu_event}",
            view=view,
            ephemeral=True
        )
        view.message = msg

    @cauhoi.error
    async def cauhoi_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            m, s = divmod(int(error.retry_after), 60)
            tmp = f"{m}m{s}s"
            notif = await ctx.reply(
                f"| Vui lòng đợi thêm `{tmp}` để sử dụng lệnh!",
                ephemeral=True
            )
            await asyncio.sleep(2)
            await notif.delete()
            await ctx.message.delete()
        else:
            raise error

    @commands.command(name='co')
    @commands.cooldown(1, 15, commands.BucketType.user)
    # @is_allowed_channel()
    async def co(self, ctx):
        if ctx.channel.id == 1147355133622108262:
            return 
        user_id = ctx.author.id
        if not is_registered(user_id):
            return await ctx.reply(
                f"{list_emoji.dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí",
                ephemeral=True
            )
        pieces = get_user_pieces(user_id)
        await ctx.reply(embed=format_flag_embed(pieces, author=ctx.author), ephemeral=True)

    @co.error
    async def co_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            m, s = divmod(int(error.retry_after), 60)
            tmp = f"{m}m{s}s"
            notif = await ctx.reply(
                f"| Vui lòng đợi thêm `{tmp}` để sử dụng lệnh!",
                ephemeral=True
            )
            await asyncio.sleep(2)
            await notif.delete()
            await ctx.message.delete()
        else:
            raise error

class NhanCauHoiView(View):
    def __init__(self, author_id: int):
        super().__init__(timeout=60)
        self.author_id = author_id
        self.add_item(NhanCauHoiButton(author_id))

    async def on_timeout(self):
        for btn in self.children:
            btn.disabled = True
        if hasattr(self, 'message'):
            await self.message.edit(view=self)

class NhanCauHoiButton(Button):
    def __init__(self, author_id: int):
        super().__init__(label="Nhận câu hỏi", style=discord.ButtonStyle.success)
        self.author_id = author_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message(
                "Bạn không thể nhận câu hỏi của người khác!",
                ephemeral=True
            )
        user_id = self.author_id
        answered_qids = {r[0] for r in cursor.execute(
            "SELECT question_id FROM answered WHERE user_id = ?", (user_id,)
        )}
        remaining = [q for q in QUESTIONS if q['id'] not in answered_qids]
        if not remaining:
            return await interaction.response.send_message(
                f"Chúc mừng bạn đã hoàn thành tất cả câu hỏi, hẹn bạn ở sự kiện tiếp theo {phaohoa}"
            )
        question = random.choice(remaining)
        mark_answered(user_id, question['id'])
        # Ghi nhận câu hỏi đã được trả lời
        num_asked = get_today_count(user_id)
        # Disable nút nhận câu hỏi
        for btn in self.view.children:
            btn.disabled = True
        # Cập nhật view câu hỏi ban đầu
        await interaction.response.edit_message(view=self.view)

        # Hiển thị câu hỏi
        if question['type'] == 1:
            embed = discord.Embed(
                title=f'{traitim} Câu hỏi trắc nghiệm `{num_asked}/200` | {dongho} `15s`',
                description="", 
                color=discord.Color.from_rgb(255, 0, 0))
            if interaction.user.avatar:
                avatar_url = interaction.user.avatar.url
            else:
                avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
            embed.set_author(name=f"{interaction.user.display_name}", icon_url=avatar_url)
            embed.add_field(
                name=f"**{question['question']}**\n",
                value=f"" +
                            '\n'.join(f"**{k}.** {v}" for k, v in question['options'].items()),
                inline=False
            )
            guild_icon_url = interaction.guild.icon.url if interaction.guild.icon else "https://cdn.discordapp.com/embed/avatars/0.png"

            embed.set_footer(text=f"Phần thưởng 1 🟥 bấm zco để xem nhé", icon_url=guild_icon_url)
            view = Cauhoi30_4View(question, user_id)
        else:
            embed = discord.Embed(
                title=f'{traitim} Câu hỏi điền đáp án `{num_asked}/200` | {dongho} `20s`',
                description=f"",
                color=discord.Color.from_rgb(255, 0, 0)
            )
            if interaction.user.avatar:
                avatar_url = interaction.user.avatar.url
            else:
                avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
            embed.set_author(name=f"{interaction.user.display_name}", icon_url=avatar_url)
            embed.add_field(
                name=f"**{question['question']}**",
                value="",
                inline=False
            )
            guild_icon_url = interaction.guild.icon.url if interaction.guild.icon else "https://cdn.discordapp.com/embed/avatars/0.png"
            embed.set_footer(text=f"Phần thưởng 1 🟥 bấm zco để xem nhé", icon_url=guild_icon_url)
            view = FillInView(question, user_id)
        # Gửi câu hỏi với view mới
        msg = await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        view.message = msg
        view.interaction = interaction

        # --- thêm countdown ---
        async def countdown(total: int):
            for remaining in range(total, -1, -1):
                # If the question has already been answered, stop the countdown immediately
                if view.answered:
                    return

                # Update the embed’s title with the remaining time
                new = embed.copy()
                suffix = 'trắc nghiệm' if question['type']==1 else 'điền đáp án'
                new.title = f"{traitim} Câu hỏi {suffix} `{num_asked}/200` | {dongho} `{remaining}s`"
                await msg.edit(embed=new, view=view)

                # Sleep only if there’s still time left
                if remaining:
                    await asyncio.sleep(1)

            # Time’s up: disable buttons and (only if not answered) send the timeout notice
            for btn in view.children:
                btn.disabled = True
            await msg.edit(view=view)

            if not view.answered:
                await interaction.followup.send(
                    f"{tickdo} {interaction.user.mention} **đã hết thời gian trả lời, sai câu hỏi này!**"
                )


        limit = 15 if question['type']==1 else 20
        asyncio.create_task(countdown(limit))

class Cauhoi30_4View(View):
    def __init__(self, question: dict, author_id: int, timeout: int = 60):
        super().__init__(timeout=timeout)
        self.question = question
        self.answered = False
        self.author_id = author_id
        for opt in ['A', 'B', 'C', 'D']:
            self.add_item(Cauhoi30_4Button(opt, question, author_id))

    async def on_timeout(self):
        pass


class Cauhoi30_4Button(Button):
    def __init__(self, label: str, question: dict, author_id: int):
        emoji_map = {'A': chu_a, 'B': chu_b, 'C': chu_c, 'D': chu_d}
        super().__init__(label=None, emoji=emoji_map[label], style=discord.ButtonStyle.gray)
        self.option = label
        self.question = question
        self.author_id = author_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message(
                "Bạn không thể trả lời câu hỏi của người khác!",
                ephemeral=True
            )
        if self.view.answered:
            return
        # đánh dấu đã trả lời
        self.view.answered = True
        # Disable buttons
        for btn in self.view.children:
            btn.disabled = True
        # Cập nhật view chính
        await interaction.response.edit_message(view=self.view)

        # Tính kết quả
        if self.option == self.question['answer']:
            idx = assign_piece(self.author_id)
            reply = f"{tickxanh} {interaction.user.mention} **trả lời chính xác! Bạn được tặng 1 mảnh ghép {codo}**"
        else:
            reply = f"{tickdo} {interaction.user.mention} **đã trả lời sai câu hỏi này!**"
        # Gửi kết quả
        await interaction.followup.send(reply)

class FillInView(View):
    def __init__(self, question: dict, author_id: int, timeout: int = 60):
        super().__init__(timeout=timeout)
        self.question = question
        self.author_id = author_id
        self.answered=False
        self.add_item(FillInButton(question, author_id))

    async def on_timeout(self):
        pass

class FillInButton(Button):
    def __init__(self, question: dict, author_id: int):
        super().__init__(label="Trả lời", style=discord.ButtonStyle.secondary)
        self.question = question
        self.author_id = author_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message(
                "Bạn không thể trả lời câu hỏi của người khác!",
                ephemeral=True
            )
        modal = FillInModal(self.question, self.view)
        modal.view = self.view
        await interaction.response.send_modal(modal)

class FillInModal(Modal):
    def __init__(self, question: dict, view: View):
        super().__init__(title="Trả lời câu hỏi")
        self.question = question
        self.view = view
        self.answer_input = TextInput(
            label="Đáp án của bạn",
            placeholder="Nhập đáp án tại đây...",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.answer_input)

    async def on_submit(self, interaction: discord.Interaction):
        self.view.answered = True
        # Disable buttons
        for btn in self.view.children:
            btn.disabled = True
        # Cập nhật view chính
        await interaction.response.edit_message(view=self.view)
        # Ghi nhận
        mark_answered(interaction.user.id, self.question['id'])
        # Tính kết quả
        if self.answer_input.value.strip().lower() == self.question['answer'].lower():
            idx = assign_piece(interaction.user.id)
            reply = f"{tickxanh} {interaction.user.mention} **trả lời chính xác! Bạn được tặng 1 mảnh ghép {codo}**"
        else:
            reply = f"{tickdo} {interaction.user.mention} **đã trả lời sai câu hỏi này!**"
        # Gửi kết quả
        await interaction.followup.send(reply)

async def setup(client):
    await client.add_cog(Cauhoi30_4(client))