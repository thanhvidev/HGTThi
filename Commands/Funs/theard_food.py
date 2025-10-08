import asyncio
import discord
from discord.ext import commands

chamthan = "<a:hgtt_chamthan:1285232578525397002>"
dung1 = "<a:meo_an:1363304203849695353>"
sai1 = "<:tho_an:1363304211453841498>"
dung2 = "<a:ech_cuoi:1363304223063933059>"
sai2 = "<a:chamhoicam:1363304289899905175>"
dung3 = "<a:choliem:1304721320067731497>"
dung4 = "<a:tivi:1309796590663372831>" 
sai3 = "<:hgtt_chotim:1064307126547263510>"
sai4 = "<:chat1:1309796581876170752>"
mu1 = "<a:likenhay:1363304169527705610>"
mu2 = "<a:tim_like:1363304176821735586>"
mu3 = "<a:wow_ngoisao:1363304186715963472>"
davao = "<:tim_chat:1363304195641446560>"
tisua = "<a:tisua:1378276582627479633>"



class Theard_food(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        # Kiểm tra nếu tin nhắn là của bot thì bỏ qua
        if message.author.bot:
            return
        

        if message.channel.id == 1019375192612548608:
            if message.attachments and any(attachment.content_type.startswith('image') for attachment in message.attachments):
                await message.add_reaction(mu1)
                await message.add_reaction(mu2)
                await message.add_reaction(mu3)
        elif message.channel.id == 1019341181743812690:
                await message.add_reaction(davao)

        # ID kênh và ID role đặc biệt
        target_channel_id = 1246341829847289876
        special_role_id = 1113463122515214427 # THAY THẾ BẰNG ID ROLE CỤ THỂ CỦA BẠN

        # Kiểm tra nếu tin nhắn nằm trong kênh chỉ định
        if message.channel.id == target_channel_id:
            # Lấy đối tượng member từ message.author
            member = message.author
            has_special_role = False
            
            # Kiểm tra xem member có role đặc biệt không
            # Đảm bảo member là một đối tượng discord.Member (thường là vậy nếu message.guild tồn tại)
            if isinstance(member, discord.Member):
                for role in member.roles:
                    if role.id == special_role_id:
                        has_special_role = True
                        break
            
            if has_special_role:
                try:
                    # Sử dụng self.tisua_emoji nếu bạn đã định nghĩa nó trong __init__
                    # await message.add_reaction(self.tisua_emoji)
                    thread = await message.create_thread(name=f"Comment của {message.author.display_name}")
                    await message.add_reaction(tisua) 
                except discord.HTTPException as e:
                    print(f"Không thể reaction tin nhắn của người dùng có role đặc biệt: {e}")
            else:
                # Xử lý cho những người dùng khác (không có role đặc biệt)
                has_media = False
                if message.attachments:
                    for attachment in message.attachments:
                        # Kiểm tra xem content_type có tồn tại không
                        if attachment.content_type:
                            if attachment.content_type.startswith('image') or \
                               attachment.content_type.startswith('video'):
                                has_media = True
                                break
                
                if has_media:
                    try:
                        # await message.add_reaction(self.tisua_emoji)
                        thread = await message.create_thread(name=f"Comment của {message.author.display_name}")
                        await message.add_reaction(tisua)
                    except discord.HTTPException as e:
                        print(f"Không thể reaction tin nhắn có media: {e}")
                else:
                    try:
                        await message.delete()
                        # Gửi thông báo (có thể tùy chỉnh thời gian tự xóa thông báo)
                        await message.channel.send(
                            f"{message.author.mention}, tin nhắn của bạn đã bị xoá vì không có hình ảnh hoặc video đính kèm. Vui lòng chỉ gửi tin nhắn có chứa hình ảnh/video vào kênh này.",
                            delete_after=10 # Tùy chọn: tự xóa thông báo sau 10 giây
                        )
                    except discord.Forbidden:
                        print(f"Bot không có quyền xóa tin nhắn hoặc gửi tin nhắn trong kênh {message.channel.name}.")
                    except discord.HTTPException as e:
                        print(f"Lỗi khi xóa hoặc gửi thông báo: {e}")

        # Chỉ thực hiện ở các kênh có id được chỉ định
        allowed_channels = [1021646306567016498, 1052625475769471127, 993153209638064179, 1309783710064705556]

        if message.channel.id not in allowed_channels:
            return

        if message.attachments and any(attachment.content_type.startswith('image') for attachment in message.attachments):
            try:
                # Phân loại theo từng kênh để đặt tên chủ đề và thêm reaction khác nhau
                if message.channel.id == 1021646306567016498: #doan
                    thread = await message.create_thread(name=f"Comment món ăn của {message.author.display_name}")
                    await message.add_reaction(dung1)
                    await message.add_reaction(sai1)
                elif message.channel.id == 1052625475769471127: # meme
                    thread = await message.create_thread(name=f"Comment meme của {message.author.display_name}")
                    await message.add_reaction(dung2)
                    await message.add_reaction(sai2)
                elif message.channel.id == 993153209638064179: #vitamin
                    thread = await message.create_thread(name=f"Vitamin comment ảnh {message.author.display_name}")
                    await message.add_reaction(dung3)
                    await message.add_reaction(sai3)
                elif message.channel.id == 1309783710064705556: #xemphim
                    thread = await message.create_thread(name=f"Comment phim của {message.author.display_name}")
                    await message.add_reaction(dung4)
                    await message.add_reaction(sai4)
                    
            except discord.Forbidden:
                print("Bot không có quyền tạo chủ đề.")
            except discord.HTTPException as e:
                print(f"Lỗi HTTP khi tạo chủ đề: {e}")

        else:
            await message.delete()
            msg = await message.channel.send('Kênh này chỉ gửi hình ảnh.')
            await asyncio.sleep(5)
            await msg.delete()
        
        await self.client.process_commands(message)

async def setup(client):
    await client.add_cog(Theard_food(client))

