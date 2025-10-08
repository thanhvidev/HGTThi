import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import datetime, timezone
import psutil
import os
import csv

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="stats", description="Hiển thị thống kê chi tiết của bot")
    async def stats_command(self, ctx):
        """Hiển thị thống kê bot kết hợp cả hai giao diện"""
        
        # Tính toán thống kê cơ bản
        total_guilds = len(self.bot.guilds)
        total_users = len(set(self.bot.get_all_members()))
        total_members = sum(guild.member_count for guild in self.bot.guilds if guild.member_count)
        
        # Đếm channels và emojis
        total_text_channels = 0
        total_voice_channels = 0
        total_stage_channels = 0
        total_categories = 0
        total_threads = 0
        total_emojis = 0
        
        for guild in self.bot.guilds:
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    total_text_channels += 1
                    total_threads += len(channel.threads)
                elif isinstance(channel, discord.VoiceChannel):
                    total_voice_channels += 1
                elif isinstance(channel, discord.StageChannel):
                    total_stage_channels += 1
                elif isinstance(channel, discord.CategoryChannel):
                    total_categories += 1
            
            total_emojis += len(guild.emojis)
        
        total_channels = total_text_channels + total_voice_channels + total_stage_channels
        
        # Lấy thông tin hệ thống
        process = psutil.Process()
        memory = process.memory_info()
        cpu_percent = process.cpu_percent()
        
        # Uptime
        uptime_seconds = (datetime.now(timezone.utc) - self.bot.start_time if hasattr(self.bot, 'start_time') else datetime.now(timezone.utc)).total_seconds()
        uptime_str = f"{int(uptime_seconds // 86400)} ngày {int((uptime_seconds % 86400) // 3600)} giờ"
        
        # Database info
        db_files = []
        if os.path.exists('databases'):
            for file in os.listdir('databases'):
                if file.endswith('.db'):
                    db_files.append(file)
        
        # Tạo embed với style kết hợp
        embed = discord.Embed(
            title="🔶 Core | Bot Statistics",
            description="Emoji Credits • Icons Server",
            color=0xFF6B35,  # Màu cam
            timestamp=datetime.now(timezone.utc)
        )
        
        # Hàng 1: Server Count, Total Users, Total Members  
        embed.add_field(
            name="� **Server Count**",
            value=f"```\n{total_guilds:,}\n```",
            inline=True
        )
        embed.add_field(
            name="� **Total Users**", 
            value=f"```\n{total_users:,}\n```",
            inline=True
        )
        embed.add_field(
            name="� **Total Members**",
            value=f"```\n{total_members:,}\n```",
            inline=True
        )
        
        # Hàng 2: Ping, Uptime, CPU
        embed.add_field(
            name="� **Ping**",
            value=f"```\n{round(self.bot.latency * 1000)}ms\n```",
            inline=True
        )
        embed.add_field(
            name="⏱️ **Uptime**", 
            value=f"```\n{uptime_str}\n```",
            inline=True
        )
        embed.add_field(
            name="� **CPU**",
            value=f"```\n{cpu_percent:.1f}%\n```",
            inline=True
        )
        
        # Hàng 3: Total Emojis, Memory, Database
        embed.add_field(
            name="� **Total Emojis**",
            value=f"```\n{total_emojis:,}\n```",
            inline=True
        )
        embed.add_field(
            name="� **Memory**",
            value=f"```\n{memory.rss / 1024 / 1024:.1f} MB\n```", 
            inline=True
        )
        embed.add_field(
            name="� **Database**",
            value=f"```\n{len(db_files)} databases\n```",
            inline=True
        )
        
        # Hàng 4: Total Channels, Categories, Thread Channels  
        embed.add_field(
            name="🟠 **Total Channels**",
            value=f"```\n{total_channels:,}\n```",
            inline=True
        )
        embed.add_field(
            name="🟡 **Total Categories**", 
            value=f"```\n{total_categories:,}\n```",
            inline=True
        )
        embed.add_field(
            name="� **Thread Channels**",
            value=f"```\n{total_threads:,}\n```",
            inline=True
        )
        
        # Hàng 5: Text Channels, Voice Channels, Stage Channels
        embed.add_field(
            name="� **Text Channels**",
            value=f"```\n{total_text_channels:,}\n```", 
            inline=True
        )
        embed.add_field(
            name="� **Voice Channels**",
            value=f"```\n{total_voice_channels:,}\n```",
            inline=True
        )
        embed.add_field(
            name="� **Stage Channels**", 
            value=f"```\n{total_stage_channels:,}\n```",
            inline=True
        )
        
        # Thông tin bổ sung
        embed.add_field(
            name="� **Owner**",
            value=f"```\n14_HGTT\n```",
            inline=True
        )
        embed.add_field(
            name="� **Events/Cogs**",
            value=f"```\n{len(self.bot.cogs):,}\n```",
            inline=True
        )
        embed.add_field(
            name="� **Stickers**",
            value=f"```\n{len(self.bot.stickers) if hasattr(self.bot, 'stickers') else 0:,}\n```",
            inline=True
        )
        
        # Footer với thông tin cluster
        embed.add_field(
            name="",
            value="Cluster • 2 | Shard • 32",
            inline=False
        )
        
        # Footer và thumbnail
        embed.set_footer(text="HGTT Bot Statistics • Choose a cluster to view more stats")
        
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        await ctx.send(embed=embed)


    @commands.hybrid_command(name="demtn", description="Đếm số tin nhắn tất cả kênh")
    @commands.has_permissions(administrator=True)
    async def demtntong(self, ctx):
        """Đếm tổng số tin nhắn của tất cả kênh văn bản và xuất CSV."""
        await ctx.send("⏳ Đang đếm tin nhắn của toàn bộ kênh... (có thể mất vài phút)")

        guild = ctx.guild
        total_msgs = 0
        channel_counts = []

        for channel in guild.text_channels:
            count = 0
            try:
                async for _ in channel.history(limit=None, oldest_first=True):
                    count += 1
                channel_counts.append((channel.name, count))
                total_msgs += count
                print(f"✅ Đã đếm xong #{channel.name}: {count}")
            except Exception as e:
                print(f"⚠️ Lỗi khi đọc kênh {channel.name}: {e}")
                channel_counts.append((channel.name, "Lỗi quyền / quá lớn"))

        # Sắp xếp giảm dần theo số tin nhắn
        channel_counts.sort(key=lambda x: x[1] if isinstance(x[1], int) else 0, reverse=True)

        # --- Ghi file CSV ---
        filename = f"messages_count_{guild.name}.csv".replace(" ", "_")
        with open(filename, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Tên kênh", "Số tin nhắn"])
            for name, count in channel_counts:
                writer.writerow([name, count])
            writer.writerow(["Tổng cộng", total_msgs])

        # --- Gửi kết quả lên Discord ---
        result_lines = ["📊 **Tổng hợp tin nhắn theo kênh:**\n"]
        for name, count in channel_counts:
            if isinstance(count, int):
                result_lines.append(f"- **#{name}** → {count:,}")
            else:
                result_lines.append(f"- **#{name}** → ❌ {count}")
        result_lines.append(f"\n💬 **Tổng cộng toàn server:** {total_msgs:,} tin nhắn")

        result_text = "\n".join(result_lines)
        for chunk in [result_text[i:i+1900] for i in range(0, len(result_text), 1900)]:
            await ctx.send(chunk)

        # Gửi file CSV
        try:
            await ctx.send(file=discord.File(filename))
        except Exception as e:
            await ctx.send(f"⚠️ Không gửi được file CSV: {e}")

        print(f"\n📁 File CSV đã lưu: {filename}")
        print(f"💬 Tổng số tin nhắn toàn server: {total_msgs:,}")


    # ===== LỆNH 2: Đếm 1 kênh cụ thể bằng ID =====
    @commands.hybrid_command(name="demtnkenh", description="Đếm số tin nhắn trong kênh hiện tại")
    @commands.has_permissions(administrator=True)
    async def demtnkenh(self, ctx, channel_id: int):
        """Đếm tổng số tin nhắn của 1 kênh chỉ định bằng ID."""
        channel = self.bot.get_channel(channel_id)

        if not channel:
            await ctx.send(f"⚠️ Không tìm thấy kênh với ID `{channel_id}`.")
            return

        if not isinstance(channel, discord.TextChannel):
            await ctx.send("⚠️ Kênh này không phải là kênh văn bản.")
            return

        await ctx.send(f"⏳ Đang đếm tin nhắn trong kênh **#{channel.name}**...")

        count = 0
        try:
            async for _ in channel.history(limit=None, oldest_first=True):
                count += 1
            await ctx.send(f"📈 Tổng số tin nhắn trong **#{channel.name}** là: **{count:,}**")
            print(f"✅ Kênh {channel.name}: {count} tin nhắn")
        except Exception as e:
            await ctx.send(f"⚠️ Lỗi khi đọc kênh {channel.mention}: {e}")
            print(f"⚠️ Lỗi khi đọc kênh {channel.name}: {e}")


async def setup(bot):
    await bot.add_cog(Stats(bot))
