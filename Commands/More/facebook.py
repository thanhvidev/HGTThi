import discord
from discord.ext import commands
from discord import File
import aiohttp
import io
import re

class Facebook(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def extract_facebook_video_url(self, page_url: str) -> str:
        """Tự động theo dõi redirect và lấy link video từ HTML Facebook"""
        async with aiohttp.ClientSession() as session:
            async with session.get(page_url, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True) as response:
                if response.status != 200:
                    return None
                final_url = str(response.url)
                html = await response.text()

        print(f"[DEBUG] Redirected to: {final_url}")

        # Tìm link video SD và HD từ HTML
        hd_match = re.search(r'"playable_url_quality_hd":"(https:\\/\\/video.*?)"', html)
        sd_match = re.search(r'"playable_url":"(https:\\/\\/video.*?)"', html)

        def clean_url(raw):
            return raw.replace('\\u0025', '%').replace('\\', '')

        if hd_match:
            return clean_url(hd_match.group(1))
        elif sd_match:
            return clean_url(sd_match.group(1))
        return None

    async def download_video(self, url):
        """Tải dữ liệu video từ URL"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as response:
                if response.status != 200:
                    return None
                return await response.read()

    @commands.hybrid_command(name="fbauto", description="Tải bất kỳ video Facebook nào: post, story, reel, comment, hoặc link chia sẻ")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def fbauto(self, ctx, fb_link: str):
        await ctx.defer()
        loading = await ctx.reply("> 🔄 Đang xử lý link Facebook...")

        try:
            video_url = await self.extract_facebook_video_url(fb_link)
            if not video_url:
                await loading.edit(content="❌ Không tìm thấy video trong liên kết này.")
                return

            # Tải video từ link đã trích xuất
            video_data = await self.download_video(video_url)
            if not video_data:
                await loading.edit(content="❌ Không thể tải video từ link đã tìm được.")
                return

            await loading.delete()

            # Nếu quá giới hạn Discord, gửi link thay vì file
            if len(video_data) > 8 * 1024 * 1024:
                await ctx.send(f"⚠️ Video vượt quá giới hạn gửi file của Discord (>8MB).\n🔗 Bạn có thể tải video tại: {video_url}")
                return

            file = File(io.BytesIO(video_data), filename="facebook_video.mp4")
            await ctx.send(file=file)
            await ctx.message.delete()

        except Exception as e:
            print(f"[fbauto] Error: {e}")
            await loading.edit(content="❌ Có lỗi xảy ra khi xử lý video Facebook.")

async def setup(client):
    await client.add_cog(Facebook(client))
