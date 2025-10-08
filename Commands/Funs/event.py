import asyncio
import discord
import random
from discord.ext import commands, tasks
from datetime import datetime, timedelta


class Event(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.questions_channel_id = 993153068378116127
        self.original_questions_list = [
            {"question": "Ông già Noel thường vào nhà để tặng quà cho trẻ em bằng cách nào?",
                "answer": "Chui qua ống khói"},
            {"question": "Ông già Noel tên thật là gì?", "answer": "Santa Claus"},
            {"question": "Mũi người tuyết thường được làm từ gì?",
                "answer": "Củ cà rốt"},
            {"question": "Loại thịt nào là món thịt phổ biến nhất trong dịp lễ Giáng Sinh ở Anh?",
                "answer": "Gà tây"},
            {"question": "Thắt lưng của ông già Noel màu nào?", "answer": "Màu đen"},
            {"question": "Trên đỉnh cây Noel, người ta thường hay treo thứ gì nhiều nhất ?",
                "answer": "Ngôi sao"},
            {"question": "Đại dương lớn nhất trên Trái đất là gì?",
                "answer": "Thái Bình Dương"},
            {"question": "Có bao nhiêu nguyên tố được liệt kê trong bảng tuần hoàn?", "answer": "118"},
            {"question": "Hành tinh lớn nhất trong hệ mặt trời là gì?",
                "answer": "Sao Mộc"},
            {"question": "Ai là quán quân the masked singer Việt Nam mùa 2 ?",
                "answer": "Anh Tú"},
            {"question": " 'giờ thì anh chịu thua em rồi...' là lời trong bài hát nào? ",
                "answer": "Chịu cách mình nói thua"},
            {"question": "Bài thơ 'Đồng Chí' của tác giả nào?", "answer": "Chính Hữu"},
            {"question": "Điểm cực tây của Việt Nam nằm ở tỉnh nào?",
                "answer": "Điện Biên"},
            {"question": "Con sông nào dài nhất thế giới?", "answer": "Sông nile"},
            {"question": "Trong MV bài hát 'Thương em là điều anh không thể ngờ' Noo Phước Thịnh ăn gì?", "answer": "ăn tát"},
            {"question": "Một trận thi đấu bóng đa có bao nhiêu người chạy trong sân?", "answer": "23"},
            {"question": "Sông gì có nước mắt?", "answer": "Sông Nhật Lệ"},
            {"question": "Vòng xoay Hồ con Rùa ở thành phố Hồ Chí Minh còn có tên gọi khác là gì?",
                "answer": "Công trường quốc tế"},
            {"question": "Điệu nhảy tango xuất xứ từ nước nào?", "answer": "Argentina"},
            {"question": "Huyện đảo Phú Quốc thuộc tỉnh nào?", "answer": "Kiên Giang"},
            {"question": "Ở người có bao nhiêu cặp nhiễm sắc thể?", "answer": "23"},
            {"question": "550/2 = ?", "answer": "275"},
            {"question": "Tỉnh nào có diện tích nhỏ nhất Việt Nam? ",
                "answer": "Bắc Ninh"},
            {"question": "Trong bài hát 'Úp lá khoai', có bao nhiêu cái chong chóng?", "answer": "12"},
            {"question": "Môn thể thao nào được coi là môn thể thao nữ hoàng?",
                "answer": "Điền kinh"},
            {"question": "Bài thơ Tây Tiến còn có tên gọi là gì?",
                "answer": "Nhớ Tây Tiến"},
            {"question": "Tỉnh nào tên không bao giờ có chiến tranh?",
                "answer": "Hòa Bình"},
            {"question": "Vĩ tuyến 17 chạy qua địa phận tỉnh nào của nước ta?",
                "answer": "Quảng Trị"},
            {"question": "Sông Mê Kông chảy qua bao nhiêu quốc gia?", "answer": "6"},
            {"question": " 'Nhiều khi muốn 1 mình nhưng sợ cô đơn...' là lời trong bài hát nào?",
                "answer": "Đâu ai chung tình được mãi"},
            {"question": "Quả gì lúc nào cũng ngủ?", "answer": "Quả mơ"},
            {"question": "Loài rắn ngửi bằng mồm hay bằng mũi?", "answer": "Lưỡi"},
            {"question": "Cây gì mang tên một loài chim?", "answer": "Cây sáo"},
            {"question": "Quảng trường đỏ ở nước nào?", "answer": "Nga"},
            {"question": "San hô là động vật hay thực vật?", "answer": "Động vật"},
            {"question": "Con vật nào là biểu tượng của quỹ bảo tồn thiên nhiên thế giới",
                "answer": "Gấu trúc"},
            {"question": "Động vật nào trên cạn lớn nhất thế giới?",
                "answer": "Voi Châu Phi"},
            {"question": "Dạ dày của động vật nhai lại có mấy ngăn?", "answer": "4"},
            {"question": "Loài cá nào có thể bay?", "answer": "Cá chuồn"},
            {"question": "Loài chim nào có tốc độ bay nhanh nhất thế giới?",
                "answer": "Chim cắt"},
            {"question": "Quảng trường Lâm Viên ở đâu?", "answer": "Lâm Đồng"},
            {"question": "Ai là người quyết định dời đô từ Hoa Lư về Đại La?",
                "answer": "Lý Công Uẩn"},
            {"question": "Bác Hồ ra đi tìm đường cứu nước năm bao nhiêu tuổi?",
                "answer": "21"},
            {"question": "Ai là vị vua cuối cùng của Việt Nam?",
                "answer": "Vua Bảo Đại"},
            {"question": "Bạn sẽ tìm thấy thủ đô nào ở đồng bằng sông Hồng?",
                "answer": "Hà Nội"},
            {"question": "Bộ môn đấu bò tót đã trở thành biểu tượng truyền thống của nước nào?",
                "answer": "Tây Ban Nha"},
            {"question": "Quốc gia nào có nhiều Di sản Thế giới được UNESCO công nhận nhất?",
                "answer": "Italia"},
            {"question": "Quốc gia sử dụng tiền giấy đầu tiên?", "answer": "Trung Quốc"},
            {"question": "Con gì nay mưa mai ướt?", "answer": "Con rùa"},
            {"question": "Thủ đô của Ấn độ là thành phố nào?", "answer": "New Delhi"},
            {"question": "Chùa một cột xây dựng dựa trên hình tượng loại hoa nào?",
                "answer": "Hoa sen"},
            {"question": "Bia gì mà không ai dám uống?", "answer": "Bia mộ"},
            {"question": "Trong bài hát em là bông hồng nhỏ, cái gì nằm mơ màng ngủ?",
                "answer": "Trang sách hồng"},
            {"question": "Cầu nào để cho xe cộ qua lại nhưng không bắc qua sông?",
                "answer": "Cầu vượt"},
            {"question": "Ca sĩ Việt Nam nào có biệt danh là “Thánh mưa”?",
                "answer": "Trung Quân idol"},
            {"question": "Muốn đổ xăng vào cây xăng, vậy muốn đổ dầu vào đâu?",
                "answer": "Cây xăng"},
            {"question": "Sắp xếp từ : C/o/m/a/n/đ/a", "answer": "Cam đoan"},
            {"question": "Sắp xếp từ : h/ả/n/d/ẻ/M", "answer": "Mảnh dẻ"},
            {"question": "Sắp xếp từ : b/ê/m/h/o/a/i/C", "answer": "Chiêm bao"},
            {"question": "Sắp xếp từ : K/h/ị/n/h/i/t/h", "answer": "Khinh thị"},
            {"question": "Bánh cáy là đặc sản ở đâu?", "answer": "Thái Bình"},
            {"question": "Ăn thắng cố, uống rượu ngô là đặc trưng của vùng nào?",
                "answer": "Hà Giang"},
            {"question": "Chuột đồng là đặc sản phổ biến ở tỉnh thành nào?",
                "answer": "Đồng Tháp"},
            {"question": "Lạng Sơn có món đặc sản trứ danh nào? ", "answer": "Phở chua"},
        ]
        self.guild = None
        self.question = None
        self.answer = None
        self.dung = None
        self.sai = None
        self.tien = None
        self.questions_list = []
        self.daily_questions = {}
        self.send_questions_loop.start()
        self.client.loop.create_task(self.setup())

    async def setup(self):
        await self.init_emojis()
        print("Emoji event")

    async def init_emojis(self):
        self.guild = self.client.get_guild(1090136467541590066)
        self.question = await self.guild.fetch_emoji(1186839345878007810)
        self.answer = await self.guild.fetch_emoji(1186838813205614592)
        self.dung = await self.guild.fetch_emoji(1186838952544575538)
        self.sai = await self.guild.fetch_emoji(1186839020974657657)
        self.tien = await self.guild.fetch_emoji(1170702509971607606)

    def cog_unload(self):
        self.send_questions_loop.cancel()

    async def send_question(self):
        if not self.questions_list:
            self.questions_list = self.original_questions_list.copy()

        for question_id, question_data in self.daily_questions.items():
            question_data["answers"] = {}

        question_id = len(self.daily_questions) + 1
        question = random.choice(self.questions_list)
        self.questions_list.remove(question)  # Loại bỏ câu hỏi đã chọn
        self.daily_questions[question_id] = {
            "question": question, "answers": {}}

        channel = self.client.get_channel(self.questions_channel_id)
        embed = discord.Embed(title=f"{self.question} **Câu hỏi {question_id}: {question['question']}**", description=f"- Phần thưởng là 100k {self.tien} \n- Dùng lệnh `ztraloi` để trả lời câu hỏi",
                              color=discord.Color.from_rgb(255, 158, 242))
        await channel.send(embed=embed)

    def get_random_minutes(self):
        return random.randint(73, 75) * 60

    async def random_delayed_send(self):
        current_time = datetime.utcnow() + timedelta(hours=7)  # Lấy múi giờ +7
        if current_time.hour < 3 or current_time.hour >= 8:
            await self.send_question()
        await asyncio.sleep(self.get_random_minutes())

    @tasks.loop(seconds=1)
    async def send_questions_loop(self):
        await self.random_delayed_send()

    @send_questions_loop.before_loop
    async def before_send_message(self):
        await self.client.wait_until_ready()
        await asyncio.sleep(5)

    @commands.command()
    async def traloi(self, ctx, *, user_answer):
        if not self.daily_questions:
            await ctx.send("Hiện không có câu hỏi nào để trả lời.")
            return

        question_id = list(self.daily_questions.keys())[-1]
        question_data = self.daily_questions[question_id]
        correct_answer = question_data["question"]["answer"]

        if question_id in question_data["answers"]:
            embed = discord.Embed(title="", description=f"{ctx.author.mention}, đã có người trả lời đúng rồi!",
                                  color=discord.Color.from_rgb(36, 255, 215))
            await ctx.reply(embed=embed)
        else:
            if user_answer.lower() == correct_answer.lower():
                question_data["answers"][question_id] = {
                    "user": ctx.author, "answer": user_answer}
                await ctx.message.add_reaction(self.dung)
                embed = discord.Embed(title="", description=f"{self.answer} {ctx.author.mention} bạn đã trả lời đúng và nhanh nhất",
                                      color=discord.Color.from_rgb(255, 158, 242))
                await ctx.reply(embed=embed)
            else:
                await ctx.message.add_reaction(self.sai)
