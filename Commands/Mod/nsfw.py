import io,aiohttp
from discord.ext import commands
import random
import json
import discord
from discord import *


class Nsfw(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.hybrid_command(name="nsfw", description="NSFW")
    @commands.is_nsfw()
    @commands.cooldown(3, 9, commands.BucketType.user)
    async def nsfw(self, ctx: commands.Context) -> None:
        await ctx.defer()
        try:
            result = []
            async with aiohttp.ClientSession() as session:
                get = await session.get("https://www.reddit.com/r/nsfw/new.json?sort=hot")
                data = await get.json()
                result = random.choice(data["data"]["children"])[
                    "data"]["url_overridden_by_dest"]
                image = await session.get(result)
                image = await image.read()
                if "redgifs" in result:
                    await ctx.send(f"{result.replace('watch', 'ifr')}")
                    return
            await ctx.send(result)
        except Exception as e:
            print(e)
            await ctx.send("Không thể tải ảnh NSFW")

    @commands.hybrid_command(name="nsfw18", description="Tải xuống video từ Chim Xanh")
    @commands.is_nsfw()
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def nsfw18(self, ctx, link_twitter: str):
        if link_twitter is None:
            await ctx.send("Vui lòng nhập link Chim xanh")
            return
        await ctx.defer()
        load_msg = await ctx.reply("> Đang tải video")
        try:
            async with aiohttp.ClientSession() as session:
                url = f'https://www.nguyenmanh.name.vn/api/twitterDL?url={link_twitter}&apikey=T3OiUYEB'
                async with session.get(url) as get:
                    data = await get.json()
                    video_url_hd = data["result"].get("HD")
                    video_url_sd = data["result"].get("SD")
                    
                if video_url_hd:
                    async with session.get(video_url_hd) as response:
                        video = await response.read()
                elif video_url_sd:
                    async with session.get(video_url_sd) as response:
                        video = await response.read()
                else:
                    await ctx.reply(content='Không có video nào khả dụng', ephemeral=False)
                    return
                    
                await load_msg.delete()
                if len(video) > 1e9: 
                    await ctx.reply(content='Video quá dài', ephemeral=False)
                    return
                file = discord.File(io.BytesIO(video), filename='video.mp4')
                await ctx.reply(file=file)
        except Exception as e:
            print(e)
            await ctx.reply(content='Không thể tải video!', ephemeral=False)

async def setup(client):
    await client.add_cog(Nsfw(client))