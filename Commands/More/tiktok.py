import re
import discord
from discord.ext import commands
from discord import *
from discord import File
import aiohttp
import io
import os
import json

class Tiktok(commands.Cog):
    def __init__(self, client):
        self.client = client
        
        # Backup APIs cho TikTok
        self.tiktok_apis = [
            "https://nguyenmanh.name.vn/api/tikDL?url={}&apikey=T3OiUYEB",
            "https://api.tiklydown.eu.org/api/download?url={}",
            "https://tikdown.org/wp-json/aio-dl/video-data/"
        ]

    async def get_tiktok_data(self, url):
        """Thử các API TikTok khác nhau"""
        async with aiohttp.ClientSession() as session:
            # API 1: nguyenmanh.name.vn
            try:
                api_url = f'https://nguyenmanh.name.vn/api/tikDL?url={url}&apikey=T3OiUYEB'
                async with session.get(api_url, timeout=10) as response:
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '')
                        if 'application/json' in content_type:
                            data = await response.json()
                            if data.get('result', {}).get('aweme_list'):
                                return data, 'nguyen_manh'
            except Exception as e:
                print(f"API 1 failed: {e}")
            
            # API 2: tiklydown.eu.org
            try:
                api_url = f'https://api.tiklydown.eu.org/api/download?url={url}'
                async with session.get(api_url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('video', {}).get('noWatermark'):
                            return data, 'tiklydown'
            except Exception as e:
                print(f"API 2 failed: {e}")
            
            # API 3: tikdown.org (POST request)
            try:
                api_url = 'https://tikdown.org/wp-json/aio-dl/video-data/'
                payload = {'url': url}
                async with session.post(api_url, json=payload, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('medias'):
                            return data, 'tikdown'
            except Exception as e:
                print(f"API 3 failed: {e}")
        
        return None, None

    def extract_video_url(self, data, api_type):
        """Trích xuất URL video từ response khác nhau"""
        try:
            if api_type == 'nguyen_manh':
                return data['result']['aweme_list'][0]["video"]["play_addr"]["url_list"][0]
            elif api_type == 'tiklydown':
                return data['video']['noWatermark']
            elif api_type == 'tikdown':
                for media in data['medias']:
                    if media.get('type') == 'video':
                        return media['url']
        except (KeyError, IndexError, TypeError):
            pass
        return None

    def extract_music_url(self, data, api_type):
        """Trích xuất URL music từ response khác nhau"""
        try:
            if api_type == 'nguyen_manh':
                return data['result']['aweme_list'][0]["music"]["play_url"]["url_list"][0]
            elif api_type == 'tiklydown':
                return data.get('music', {}).get('play_url')
            elif api_type == 'tikdown':
                for media in data['medias']:
                    if media.get('type') == 'audio':
                        return media['url']
        except (KeyError, IndexError, TypeError):
            pass
        return None



    
    @commands.hybrid_command(name="videotiktok", aliases=["tt","tiktok"], description="Gửi link tiktok để lấy video")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def videotiktok(self, ctx, link_video_tiktok: str):
        if link_video_tiktok is None:
            await ctx.send("Vui lòng nhập link Tiktok")
            return
        
        await ctx.defer()
        load_msg = await ctx.reply("> Đang tải video", ephemeral=False)
        
        try:
            # Thử các API khác nhau
            data, api_type = await self.get_tiktok_data(link_video_tiktok)
            
            if not data:
                await load_msg.edit(content="❌ Không thể lấy dữ liệu từ TikTok. Vui lòng thử lại sau.")
                return
            
            video_url = self.extract_video_url(data, api_type)
            if not video_url:
                await load_msg.edit(content="❌ Không tìm thấy URL video.")
                return
            
            # Tải video
            async with aiohttp.ClientSession() as session:
                async with session.get(video_url, timeout=30) as response:
                    if response.status != 200:
                        await load_msg.edit(content="❌ Không thể tải video từ URL.")
                        return
                    
                    video = await response.read()
            
            await load_msg.delete()
            
            # Kiểm tra kích thước (Discord limit 8MB)
            if len(video) > 8 * 1024 * 1024:
                await ctx.send(content='❌ Video quá lớn (>8MB) không thể gửi qua Discord.', ephemeral=True)
                return
            
            if len(video) == 0:
                await ctx.send(content='❌ Video không có nội dung.', ephemeral=True)
                return
            
            file = File(io.BytesIO(video), filename='tiktok_video.mp4')
            await ctx.send(file=file)
            await ctx.message.delete()
            
        except Exception as e:
            print(f"TikTok video error: {e}")
            await load_msg.edit(content='❌ Không thể tải video! Vui lòng thử lại.')
        
    @commands.hybrid_command(name="tiktokmusic", aliases=["ttmusic","ttnhac"], description="Tải xuống nhạc từ TikTok")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def tiktokmusic(self, ctx, link_music_tiktok: str):
        if link_music_tiktok is None:
            await ctx.send("Vui lòng nhập link Tiktok")
            return
        
        await ctx.defer()
        load_msg = await ctx.reply("> Đang tải nhạc")
        
        try:
            # Thử các API khác nhau
            data, api_type = await self.get_tiktok_data(link_music_tiktok)
            
            if not data:
                await load_msg.edit(content="❌ Không thể lấy dữ liệu từ TikTok. Vui lòng thử lại sau.")
                return
            
            music_url = self.extract_music_url(data, api_type)
            if not music_url:
                await load_msg.edit(content="❌ Không tìm thấy URL nhạc.")
                return
            
            # Tải nhạc
            async with aiohttp.ClientSession() as session:
                async with session.get(music_url, timeout=30) as response:
                    if response.status != 200:
                        await load_msg.edit(content="❌ Không thể tải nhạc từ URL.")
                        return
                    
                    music = await response.read()
            
            await load_msg.delete()
            
            if len(music) == 0:
                await ctx.send(content='❌ Không thể tải nhạc từ TikTok!', ephemeral=True)
                return
            
            # Kiểm tra kích thước
            if len(music) > 8 * 1024 * 1024:
                await ctx.send(content='❌ File nhạc quá lớn (>8MB) không thể gửi qua Discord.', ephemeral=True)
                return
            
            file = File(io.BytesIO(music), filename='tiktok_music.mp3')
            await ctx.send(file=file)
            await ctx.message.delete()
            
        except Exception as e:
            print(f"TikTok music error: {e}")
            await load_msg.edit(content='❌ Không thể tải nhạc từ TikTok!')
    
    @commands.hybrid_command(name="tiktokinfo", aliases=["ttinfo","infott"], description="Xem thông tin người dùng TikTok")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def tiktokinfo(self, ctx, username_tiktok: str):
        if username_tiktok is None:
            await ctx.send("Vui lòng nhập tên người dùng TikTok")
            return
        
        await ctx.defer()
        load_msg = await ctx.reply("> Đang lấy thông tin")
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f'https://nguyenmanh.name.vn/api/tikInfo?query={username_tiktok}&apikey=T3OiUYEB'
                async with session.get(url, timeout=10) as response:
                    if response.status != 200:
                        await load_msg.edit(content="❌ Không thể kết nối tới API.")
                        return
                    
                    content_type = response.headers.get('content-type', '')
                    if 'application/json' not in content_type:
                        await load_msg.edit(content="❌ API trả về dữ liệu không hợp lệ.")
                        return
                    
                    response_data = await response.json()
                    info = response_data.get('result')
            
            await load_msg.delete()
            
            if not info:
                await ctx.reply(content='❌ Không tìm thấy người dùng TikTok!', ephemeral=True)
                return
            
            embed = discord.Embed(
                title=f"{info.get('nickname', 'N/A')}", 
                url=f"https://www.tiktok.com/@{username_tiktok}/", 
                color=discord.Color.from_rgb(242, 205, 255)
            )
            embed.set_thumbnail(url=info.get('avatar'))
            embed.add_field(name="Tên người dùng", value=info.get('uniqueId', 'N/A'), inline=True)
            embed.add_field(name="Số video", value=f"{info.get('videoCount', 0):,}", inline=True)
            embed.add_field(name="Người theo dõi", value=f"{info.get('followerCount', 0):,}", inline=True)
            embed.add_field(name="Đang theo dõi", value=f"{info.get('followingCount', 0):,}", inline=True)
            embed.add_field(name="Lượt thích", value=f"{info.get('heartCount', 0):,}", inline=True)
            
            signature = info.get('signature', 'Không có mô tả')
            if len(signature) > 100:
                signature = signature[:97] + "..."
            embed.add_field(name="Mô tả", value=signature, inline=False)
            
            await ctx.send(embed=embed, ephemeral=False)
            await ctx.message.delete()
            
        except Exception as e:
            print(f"TikTok info error: {e}")
            await load_msg.edit(content='❌ Không thể tải thông tin người dùng TikTok!')

async def setup(client):
    await client.add_cog(Tiktok(client))