import sqlite3
import discord
from discord.ext import commands

# Kết nối tới cơ sở dữ liệu SQLite
conn = sqlite3.connect('economy.db')
cursor = conn.cursor()

# Tạo bảng mới nếu chưa tồn tại
cursor.execute('''
CREATE TABLE IF NOT EXISTS servers (
    server_id INTEGER PRIMARY KEY,
    server_name TEXT,
    channel_simsimi INTEGER
)
''')
conn.commit()

# Định nghĩa class Server để quản lý các sự kiện liên quan đến server
class Server(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        cursor.execute('INSERT OR IGNORE INTO servers (server_id, server_name, channel_simsimi) VALUES (?, ?, ?)', (guild.id, guild.name, None))
        conn.commit()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        cursor.execute('DELETE FROM servers WHERE server_id = ?', (guild.id,))
        conn.commit()

    @commands.command()
    async def server(self, ctx):
        servers = cursor.execute('SELECT server_id, server_name FROM servers').fetchall()
        server_list = '\n'.join([f'{server[1]} (ID: {server[0]})' for server in servers])
        await ctx.send(f'Bot hiện đang ở các server:\n{server_list}')

async def setup(client):
    await client.add_cog(Server(client))