import os
import re
import time
import json
import random
import sqlite3
import asyncio
import contextlib
from typing import List, Tuple, Optional, Dict

import discord
from discord.ext import commands, tasks

# ===================== CONFIG =====================
DB_FILE = "economy.db"                  # file DB SQLite
VIETNAMESE_WORDS_FILE = "vietnamese-wordlist.txt"   # mỗi dòng: "từ1 từ2"
ALLOWED_CHANNEL_ID = 1247072223861280768            # kênh chơi
SUGGEST_AFTER_WRONG = 5                              # số lần sai liên tiếp để gợi ý
SUGGEST_AFTER_IDLE = 15                              # số giây im lặng để gợi ý
IDLE_CHECK_INTERVAL = 360                              # chu kỳ kiểm tra im lặng
REPEAT_BLOCK = 40                                    # không cho lặp lại cụm từ trong N bước gần nhất
BOT_THINKING_EMOJIS = ["🤔", "😵‍💫", "🧠", "🫠", "🌀"]
WRONG_REMIND_AFTER = 600
# ==================================================

# ============ UTIL CHUẨN HÓA VĂN BẢN ==============
PUNCT = r"""`~!@#$%^&*()_+\-=\[\]{};':",./<>?…“”’–—«»|"""

def normalize(text: str) -> str:
    text = text.strip()
    text = re.sub(rf"[{re.escape(PUNCT)}]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.lower().strip()

def tokens(text: str) -> List[str]:
    return normalize(text).split()

def first_tok(phrase: str) -> Optional[str]:
    t = tokens(phrase)
    return t[0] if t else None

def last_tok(phrase: str) -> Optional[str]:
    t = tokens(phrase)
    return t[-1] if t else None

def two_wordish(phrase: str) -> bool:
    # cho phép >=2 từ, nhưng khuyến khích 2
    return len(tokens(phrase)) >= 2

# =============== DỮ LIỆU CỤM TỪ ===================
def load_pairs_from_file(path: str) -> List[Tuple[str, str]]:
    pairs = []
    if not os.path.exists(path):
        return pairs
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = normalize(line)
            if not line:
                continue
            ts = line.split()
            if len(ts) >= 2:
                pairs.append((" ".join(ts[:-1]), ts[-1]))  # linh hoạt n từ, lấy từ cuối
    # quy về dạng (first, last) theo 2 token đầu/cuối
    cleaned = []
    for a, b in pairs:
        a_t = tokens(a)
        if not a_t:
            continue
        cleaned.append((" ".join(a_t), b))
    return cleaned

FALLBACK_PAIRS = [
    "xe máy", "máy nổ", "nổ súng", "súng ống", "ống hút", "hút bụi", "bụi cây",
    "cây bút", "bút mực", "mực nước", "nước ngọt", "ngọt ngào", "ngào ngạt",
    "ngạt khí", "khí hậu", "hậu vệ", "vệ sinh", "sinh viên", "viên thuốc",
    "thuốc bổ", "bổ sung", "sung túc", "túc cầu", "cầu thủ", "thủ môn",
    "môn học", "học phí", "phí ship", "ship nhanh", "nhanh nhẹn", "nhẹn bén",
    "bén rễ", "rễ cây", "cây cối", "cối xay", "xay gạo", "gạo lứt", "lứt khứt",
    "khứ hồi", "hồi hộp", "hộp sữa", "sữa tươi", "tươi rói", "rói rắm",
    "rắm bắp", "bắp rang", "rang muối", "muối tiêu", "tiêu chuẩn", "chuẩn mực",
    "mực in", "in ấn", "ấn tượng", "tượng đài", "đài phun", "phun sương",
    "sương mù", "mù đường", "đường sắt", "sắt thép", "thép hộp", "hộp quà",
]

def build_graph(entries: List[str]) -> Dict[str, List[str]]:
    # nhận list các cụm từ (mỗi cụm >=2 từ). Mô hình: "A B" => B -> (B C) bằng cách nhóm theo first token
    graph: Dict[str, List[str]] = {}
    for phrase in entries:
        ts = tokens(phrase)
        if len(ts) < 2:
            continue
        f = ts[0]
        graph.setdefault(f, []).append(" ".join(ts))
    return graph

def is_staff():
    async def predicate(ctx):
        guild_owner = ctx.author == ctx.guild.owner
        bot_owner = ctx.author.id == 962627128204075039 or ctx.author.id == 928879945000833095
        specific_role = any(
            role.id == 1113463122515214427 for role in ctx.author.roles)
        return guild_owner or bot_owner or specific_role
    return commands.check(predicate)

# =============== LỚP TRẠNG THÁI VÁN ===============
# Thêm vào sau phần config
  # 10 phút = 600 giây

# Trong GameState, thêm biến để lưu thời điểm sai gần nhất & người sai
class GameState:
    def __init__(self):
        self.current_phrase: Optional[str] = None
        self.last_active_ts: float = time.time()
        self.wrong_streak: int = 0
        self.history: List[str] = []
        self.last_wrong_ts: Optional[float] = None
        self.last_wrong_user: Optional[int] = None

    def push_phrase(self, phrase: str):
        self.current_phrase = phrase
        self.last_active_ts = time.time()
        self.wrong_streak = 0
        self.history.append(normalize(phrase))
        if len(self.history) > REPEAT_BLOCK:
            self.history = self.history[-REPEAT_BLOCK:]

# ================== DB (SQLite) ====================
class Storage:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self._migrate()

    def _migrate(self):
        cur = self.conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS scores(
            user_id INTEGER PRIMARY KEY,
            score INTEGER NOT NULL DEFAULT 0
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS games(
            channel_id INTEGER PRIMARY KEY,
            started INTEGER NOT NULL DEFAULT 0,
            current_phrase TEXT,
            last_active_ts REAL NOT NULL DEFAULT 0,
            wrong_streak INTEGER NOT NULL DEFAULT 0,
            history TEXT NOT NULL DEFAULT '[]'
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS used(
            channel_id INTEGER,
            phrase TEXT,
            used_at REAL,
            PRIMARY KEY(channel_id, phrase)
        )""")
        self.conn.commit()

    # điểm
    def add_score(self, user_id: int, delta: int = 1):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO scores(user_id, score) VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE SET score = score + ?",
                    (user_id, delta, delta))
        self.conn.commit()

    def top_scores(self, limit=10) -> List[Tuple[int, int]]:
        cur = self.conn.cursor()
        cur.execute("SELECT user_id, score FROM scores ORDER BY score DESC, user_id ASC LIMIT ?", (limit,))
        return cur.fetchall()

    # game per channel
    def load_game(self, channel_id: int) -> GameState:
        cur = self.conn.cursor()
        cur.execute("SELECT started, current_phrase, last_active_ts, wrong_streak, history FROM games WHERE channel_id=?",
                    (channel_id,))
        row = cur.fetchone()
        st = GameState()
        if row:
            started, cp, ts, ws, hist = row
            st.current_phrase = cp
            st.last_active_ts = ts or time.time()
            st.wrong_streak = ws or 0
            try:
                st.history = json.loads(hist) if hist else []
            except Exception:
                st.history = []
        return st

    def save_game(self, channel_id: int, started: bool, st: GameState):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO games(channel_id, started, current_phrase, last_active_ts, wrong_streak, history)
            VALUES(?,?,?,?,?,?)
            ON CONFLICT(channel_id) DO UPDATE SET
              started=excluded.started,
              current_phrase=excluded.current_phrase,
              last_active_ts=excluded.last_active_ts,
              wrong_streak=excluded.wrong_streak,
              history=excluded.history
        """, (channel_id, 1 if started else 0, st.current_phrase, st.last_active_ts, st.wrong_streak, json.dumps(st.history)))
        self.conn.commit()

# ============== CHECK KÊNH CHƠI ====================
def is_noitutv():
    async def predicate(ctx):
        if isinstance(ctx, discord.Message):
            channel_id = ctx.channel.id
            author = ctx.author
        else:
            channel_id = ctx.channel.id
            author = ctx.author

        if channel_id != ALLOWED_CHANNEL_ID:
            # mềm mại: không raise, chỉ thông báo khi dùng command
            if isinstance(ctx, commands.Context):
                await ctx.reply(f"⛔ Lệnh chỉ dùng trong kênh <#{ALLOWED_CHANNEL_ID}>.", mention_author=False)
            return False
        if author.bot:
            return False
        return True
    return commands.check(predicate)

def has_continuation(self, phrase: str) -> bool:
    key = last_tok(phrase or "")
    return bool(key and self.graph.get(key))

# ===================== COG GAME ====================
class Noitutv(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.db = Storage(DB_FILE)
        self.channel_locks: Dict[int, asyncio.Lock] = {} # để kiểm tra nhanh cụm đã dùng

        # nguồn dữ liệu cụm từ
        entries = []
        # từ file mỗi dòng là cụm: "a b", "b c", hoặc "a b c" (lấy từ đầu & cuối để nối)
        raw = load_pairs_from_file(VIETNAMESE_WORDS_FILE)
        if raw:
            # chuyển về danh sách cụm đầy đủ để bot tự gợi ý/đáp
            for left, last in raw:
                entries.append(f"{left} {last}")
        else:
            entries = FALLBACK_PAIRS[:]

        self.entries = sorted(set([normalize(x) for x in entries if two_wordish(x)]))
        self.graph = build_graph(self.entries)  # key = từ đầu, value = list các cụm bắt đầu bằng từ đó
        self.entry_set = set(self.entries)  # For fast lookup of normalized entries

        # quản lý state theo kênh trong RAM
        self.states: Dict[int, GameState] = {}

        # background check gợi ý khi im lặng
        self.idle_checker.start()
        self.wrong_checker.start()

    # ---------- trợ giúp chọn nước đi ----------
    def candidates_starting_with(self, first_word: str, exclude: List[str]) -> List[str]:
        first_word = normalize(first_word)
        cands = self.graph.get(first_word, [])
        if not cands:
            return []
        # loại cụm đã dùng trong history gần đây
        ex = set(exclude)
        return [p for p in cands if normalize(p) not in ex]

    def bot_reply_after(self, user_phrase: str, used_recent: List[str]) -> Optional[str]:
        # từ cuối của user_phrase
        nxt_first = last_tok(user_phrase)
        if not nxt_first:
            return None
        cands = self.candidates_starting_with(nxt_first, used_recent)
        if not cands:
            return None
        # chọn ngẫu nhiên nhưng ưu tiên cụm 2 từ
        two_word = [p for p in cands if len(tokens(p)) == 2]
        pool = two_word or cands
        return random.choice(pool)

    def random_hint_from_state(self, st: GameState) -> Optional[str]:
        if not st.current_phrase:
            return None
        key = last_tok(st.current_phrase)
        if key is None:
            return None
        cands = self.candidates_starting_with(key, st.history)
        return random.choice(cands) if cands else None

    # ---------------- commands ----------------
    @commands.command(name="starttv")
    @is_noitutv()
    @is_staff()
    async def starttv(self, ctx):
        cid = ctx.channel.id
        st = self.states.get(cid) or self.db.load_game(cid)
        if st.current_phrase is None:
            # khởi tạo ngẫu nhiên
            first = random.choice(self.entries)
            st.push_phrase(first)
            self.states[cid] = st
            self.db.save_game(cid, True, st)
            await ctx.send(f"🎮 Bắt đầu nhé! Cụm đầu: **{first}**\nBạn nối tiếp bằng cụm bắt đầu bằng **{last_tok(first)}**.")
        else:
            await ctx.send(f"⏳ Ván đang chạy. Cụm hiện tại: **{st.current_phrase}** → bắt đầu bằng **{last_tok(st.current_phrase)}**.")

    @commands.command(name="stoptv")
    @is_noitutv()
    @is_staff()
    async def stoptv(self, ctx):
        cid = ctx.channel.id
        st = self.states.get(cid) or self.db.load_game(cid)
        st.current_phrase = None
        st.history = []
        st.wrong_streak = 0
        self.states[cid] = st
        self.db.save_game(cid, False, st)
        await ctx.send("🛑 Đã dừng ván nối từ.")

    @commands.command(name="resettv")
    @is_noitutv()
    @is_staff()
    async def resettv(self, ctx):
        cid = ctx.channel.id
        st = GameState()
        first = random.choice(self.entries)
        st.push_phrase(first)
        self.states[cid] = st
        self.db.save_game(cid, True, st)
        await ctx.send(f"🔄 Reset ván. Cụm mới: **{first}** → bắt đầu bằng **{last_tok(first)}**.")

    @commands.command(name="lbtv")
    @is_noitutv()
    @is_staff()
    async def lbtv(self, ctx):
        rows = self.db.top_scores(10)
        if not rows:
            await ctx.send("📉 Chưa có điểm.")
            return
        lines = []
        for i, (uid, score) in enumerate(rows, start=1):
            user = self.client.get_user(uid)
            name = user.mention if user else f"<@{uid}>"
            lines.append(f"`#{i:02}` {name} — **{score}** điểm")
        await ctx.send("🏆 **Bảng xếp hạng**\n" + "\n".join(lines))

    @commands.command(name="hinttv")
    @is_noitutv()
    @is_staff()
    async def hinttv(self, ctx):
        cid = ctx.channel.id
        st = self.states.get(cid) or self.db.load_game(cid)
        if not st.current_phrase:
            await ctx.reply("Chưa bắt đầu ván. Dùng `zstart` nhé.", mention_author=False)
            return
        h = self.random_hint_from_state(st)
        if h:
            await ctx.reply(f"💡 Gợi ý nè: **{h}**", mention_author=False)
        else:
            await ctx.reply("😵 Không còn gợi ý hợp lệ. Dùng `zreset` để bắt đầu lại?", mention_author=False)

    @commands.command(name="skiptv")
    @is_noitutv()
    async def skip(self, ctx):
        cid = ctx.channel.id
        st = self.states.get(cid) or self.db.load_game(cid)
        if not st.current_phrase:
            await ctx.reply("Chưa có ván nào.", mention_author=False)
            return
        nxt = self.random_hint_from_state(st)
        if not nxt:
            await ctx.send("🤷 Bot bí quá rồi. `zreset` thôi.")
            return
        st.push_phrase(nxt)
        self.states[cid] = st
        self.db.save_game(cid, True, st)
        await ctx.send(f"⏭️ Bỏ qua. Cụm mới: **{nxt}** → bắt đầu bằng **{last_tok(nxt)}**.")

    # ------------- message listener -------------
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        if message.channel.id != ALLOWED_CHANNEL_ID:
            return

        # Ưu tiên xử lý command
        ctx = await self.client.get_context(message)
        if ctx.valid:
            return

        content = message.content.strip()
        if not two_wordish(content):
            return

        # Lấy lock cho channel này
        lock = self.channel_locks.setdefault(message.channel.id, asyncio.Lock())
        async with lock:
            cid = message.channel.id
            st = self.states.get(cid) or self.db.load_game(cid)
            started = st.current_phrase is not None
            if not started:
                return

            want = last_tok(st.current_phrase) if st.current_phrase else None
            user_first = first_tok(content)
            user_norm = normalize(content)
            unknown = user_norm not in self.entry_set

            repeated = user_norm in st.history

            # Nếu sai hoặc trùng
            if user_first != want or repeated or unknown:
                st.wrong_streak += 1
                st.last_active_ts = time.time()
                st.last_wrong_ts = time.time()
                st.last_wrong_user = message.author.id
                self.states[cid] = st
                self.db.save_game(cid, True, st)

                with contextlib.suppress(discord.HTTPException):
                    await message.add_reaction("❌")
                    await message.add_reaction("🤨" if repeated else ("🧠" if unknown else "🤔"))
                if st.wrong_streak >= SUGGEST_AFTER_WRONG:
                    st.wrong_streak = 0
                    hint = self.random_hint_from_state(st)
                    self.states[cid] = st
                    self.db.save_game(cid, True, st)
                    if hint:
                        await message.channel.send(f"💡 Gợi ý đi kìa: **{hint}**")
                return

            # === Kiểm tra lại để tránh double reply ===
            if st.current_phrase is None:
                return

            # Đúng: cộng điểm, reset wrong_streak, đẩy lịch sử
            with contextlib.suppress(discord.HTTPException):
                await message.add_reaction("✅")
                await message.add_reaction("🙂")

            self.db.add_score(message.author.id, 1)
            st.push_phrase(content)
            self.states[cid] = st
            self.db.save_game(cid, True, st)

            # Bot nối tiếp
            reply = self.bot_reply_after(content, st.history)
            if not reply:
                # Bot bí → bắt đầu từ mới
                new_start = random.choice(self.entries)
                st.push_phrase(new_start)
                self.states[cid] = st
                self.db.save_game(cid, True, st)
                await message.reply(f"🤖 mày thắng rồi đó.. bắt đầu từ mới nhé: **{new_start}** → bắt đầu bằng **{last_tok(new_start)}**")
                return

            if normalize(reply) == user_norm:
                alt = self.bot_reply_after(content, st.history + [user_norm])
                if alt:
                    reply = alt

            bot_msg = await message.reply(f"**{reply}**")
            st.push_phrase(reply)
            self.states[cid] = st
            self.db.save_game(cid, True, st)
            with contextlib.suppress(discord.HTTPException):
                await bot_msg.add_reaction("🆗")


    # ------------- idle hint background -------------
    @tasks.loop(seconds=IDLE_CHECK_INTERVAL)
    async def idle_checker(self):
        # mỗi chu kỳ quét các kênh đang chơi để gợi ý khi im lặng
        for guild in self.client.guilds:
            ch = guild.get_channel(ALLOWED_CHANNEL_ID)
            if not ch or not isinstance(ch, (discord.TextChannel, discord.Thread)):
                continue
            st = self.states.get(ch.id) or self.db.load_game(ch.id)
            if not st.current_phrase:
                continue
            # nếu im lặng quá lâu
            if time.time() - st.last_active_ts >= SUGGEST_AFTER_IDLE:
                hint = self.random_hint_from_state(st)
                st.last_active_ts = time.time()
                st.wrong_streak = 0
                self.states[ch.id] = st
                self.db.save_game(ch.id, True, st)
                if hint:
                    with contextlib.suppress(discord.HTTPException):
                        await ch.send(f"⏰ Gà vậy trời!!! Gợi ý nè: **{hint}**")

    @idle_checker.before_loop
    async def before_idle(self):
        await self.client.wait_until_ready()

    @tasks.loop(seconds=WRONG_REMIND_AFTER)
    async def wrong_checker(self):
        now = time.time()
        for guild in self.client.guilds:
            ch = guild.get_channel(ALLOWED_CHANNEL_ID)
            if not ch or not isinstance(ch, (discord.TextChannel, discord.Thread)):
                continue
            st = self.states.get(ch.id) or self.db.load_game(ch.id)
            if st.last_wrong_ts and (now - st.last_wrong_ts >= WRONG_REMIND_AFTER):
                if st.last_wrong_user:
                    user = self.client.get_user(st.last_wrong_user)
                    if user:
                        with contextlib.suppress(discord.HTTPException):
                            await ch.send(f"⏰ {user.mention} Có thực sự là biết nối từ không ? Gà vờ lờ")
                st.last_wrong_ts = None  # reset để không nhắc lại liên tục
                self.states[ch.id] = st
                self.db.save_game(ch.id, True, st)

    @wrong_checker.before_loop
    async def before_wrong_checker(self):
        await self.client.wait_until_ready()


async def setup(client):
    await client.add_cog(Noitutv(client))