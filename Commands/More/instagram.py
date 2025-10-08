import json
import discord
import asyncio
import config
from discord.ext import commands
from instagram_private_api import (
    Client, ClientCompatPatch, ClientError, ClientLoginRequiredError
)

usernames = config.USERNAME
passwords = config.PASSWORD

class Instagram(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.api = None

    async def login(self):
        if self.api is not None:
            return
        # Thông tin đăng nhập của tài khoản Instagram
        username = usernames
        password = passwords
        # Khởi tạo API client
        self.api = Client(username, password)
        try:
            # Thử truy cập vào một trang nào đó để kiểm tra cookie đã có hay chưa
            self.api.feed_timeline()
        except ClientLoginRequiredError:
            # Nếu chưa có cookie thì đăng nhập và lưu lại cookie
            self.api.login()
            cookiejar = self.api.cookie_jar.dump()
            with open("cookies.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(cookiejar))
        except ClientError as e:
            raise e

    async def search_user(self, username):
        if self.api is None:
            await self.login()
        # Tìm kiếm thông tin người dùng
        user_info = None
        try:
            user_info = self.api.username_info(username)
        except ClientError as e:
            if e.code == 404:
                #await ctx.send("Không tìm thấy thông tin người dùng này trên Instagram.")
                return
            else:
                raise e
        return user_info

    @commands.hybrid_command(aliases=["ig","insta"], description="Tìm kiếm thông tin Instagram của người dùng")
    async def instagram(self, ctx, username: str = None):
        if username is None:
            await ctx.send("Vui lòng nhập tên người dùng Instagram.")
            return
        user_info = await self.search_user(username)
        if not user_info:
            await ctx.send("Không tìm thấy thông tin người dùng này trên Instagram.")
            return
        embed = discord.Embed(title=f"{username}",url=f"https://www.instagram.com/{username}/", color=discord.Color.from_rgb(242, 205, 255))
        embed.set_thumbnail(url=user_info["user"]["profile_pic_url"])
        embed.add_field(name="Tên đầy đủ", value=user_info["user"]["full_name"], inline=True)
        embed.add_field(name="Số bài đăng", value=user_info["user"]["media_count"], inline=True)
        embed.add_field(name="Số người theo dõi", value=user_info["user"]["follower_count"], inline=False)
        embed.add_field(name="Số người đang theo dõi", value=user_info["user"]["following_count"], inline=True)
        embed.add_field(name="Tiểu sử", value=user_info["user"]["biography"], inline=False)
        await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(Instagram(client))