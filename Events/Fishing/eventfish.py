import asyncio
import json
import typing
import discord
import sqlite3
import random
from discord.ext import commands
from discord.ui import Button, View
import unicodedata

conn = sqlite3.connect('economy.db')
cursor = conn.cursor()

dk = "<:profile:1181400074127945799>"
fishcoin = "<:fishcoin:1213027788672737300>"
moicau = "<:moicauca:1213073602996477972>"
cancau50 = "<:can50:1213177065931804752>"
cancau80 = "<:can80:1213179176291536926>"
cancau100 = "<:can100:1213182598990274651>"
line = "<a:hgtt_ogach:1024039534452813824>"
checkcauca = "<:checkcauca:1213359415080517714>"
khongdutien = "<:khongdutien:1211921509514477568>"
canhbao = "<:chamthan:1213200604495749201> "
suacan = "<:suacan:1213359207705743400>"
suacan1 = "<:suacan:1213200488292687912>"
taiche = "<:taiche:1211435320709480468>"
rac = "<:rac:1211435291391299654>"
cash = "<:timcoin:1192458078294122526>"
mamcay = "<a:diemtaiche:1211410013868789850>"
cauca = "<:cauca:1213251373949390979>"
cauca1 = "<:cauca:1213251402097496175>"
cauca2 = "<:cauca:1213249056311083148>"
cauca3 = "<a:botbien:1214118203995717653>"
oc = "<a:ocean:1211920499115032636>"
saocasong = "<a:star_casong:1213790734059175936>"
saocabien = "<a:star_cabien:1213790799439863829>"
saocatrendy = "<a:star_catrendy:1213790869337940018>"
saocavip = "<a:star_cavip:1213791095033569310>"
exp = "<a:exp:1214433497528401920>"

def is_guild_owner_or_bot_owner():
    async def predicate(ctx):
        return ctx.author == ctx.guild.owner or ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222
    return commands.check(predicate)

def is_staff():
    async def predicate(ctx):
        guild_owner = ctx.author == ctx.guild.owner
        bot_owner = ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222 
        specific_role = any(role.id == 1113463122515214427 for role in ctx.author.roles)
        return guild_owner or bot_owner or specific_role
    return commands.check(predicate)

def is_registered(user_id):  # Hàm kiểm tra xem người dùng đã được đăng ký hay chưa
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None

def get_superscript(n):
    superscripts = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    return str(n).translate(superscripts)

class EventFishView(discord.ui.View):
    def __init__(self, enable_buttons, timeout: float = 180.0):
        super().__init__(timeout=timeout)
        self.enable_buttons = enable_buttons
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.enable_buttons:
            return True
        else:
            await interaction.response.send_message("Bảng câu cá này của người khác", ephemeral=True)
            return False
    
    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)
    
    async def enable_all_items(self):
        for item in self.children:
            item.disabled = False
        await self.message.edit(view=self)
    
    async def disable_button_for(self, button_name: str, duration: int):
        button = getattr(self, button_name)
        button.disabled = True
        await self.message.edit(view=self)
        await asyncio.sleep(duration)
        button.disabled = False
        await self.message.edit(view=self)
    
    async def on_timeout(self) -> None:
        await self.disable_all_items()
        return await super().on_timeout()
    
    @discord.ui.button(label="Câu Cá", style=discord.ButtonStyle.blurple, emoji="🎣", row=1, disabled = True)
    async def cau(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        cursor.execute("SELECT kho_can, kho_moi, kho_ca FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            kho_can_json, kho_moi_json, kho_ca_json = result
            kho_can = json.loads(kho_can_json) if kho_can_json else []
            kho_moi = json.loads(kho_moi_json) if kho_moi_json else []
            kho_ca = json.loads(kho_ca_json) if kho_ca_json else []
        else:
            await interaction.response.send_message("Không thể tìm thấy thông tin người dùng", ephemeral=True)
            return
        # Kiểm tra cần câu
        if not kho_can:
            await interaction.response.send_message(f"{canhbao} **{interaction.user.mention}, bạn không có cần câu nào trong kho**", ephemeral=True)
            return
        
        for item in kho_can:
            if item.get("used") == 0: 
                await interaction.response.send_message(f"{canhbao} **{interaction.user.mention}, cần câu của bạn đã bị hỏng, hãy sửa cần để câu tiếp!**", ephemeral=True)
                return
        # Kiểm tra mồi
        if not kho_moi or kho_moi[0].get("quantity", 0) <= 0:  
            await interaction.response.send_message(f"**Bạn đã hết mồi {moicau}**", ephemeral=True)
            return
        # Trừ mồi
        kho_moi[0]["quantity"] -= 1
        cursor.execute("UPDATE users SET kho_moi = ? WHERE user_id = ?", (json.dumps(kho_moi), user_id))
        # Trừ cần câu đã sử dụng
        for item in kho_can:
            if item.get("used") > 0:
                item["used"] -= 1
                cursor.execute("UPDATE users SET kho_can = ? WHERE user_id = ?", (json.dumps(kho_can), user_id))
                break
        # Random cá
        fish_list_A = [
            {"name": "caheo_vip", "emoji": "<:caheo_vip:1213805282799652884>", "rank": "A"},
            {"name": "camap_vip", "emoji": "<:camap_vip:1215242654867132516>", "rank": "A"},
            {"name": "canhamvoi_vip", "emoji": "<:canhamvoi_vip:1213805195994202182>", "rank": "A"},
            {"name": "caduoi_vip", "emoji": "<:caduoi_vip:1213698475041234984>", "rank": "A"},
            {"name": "cavoisatthu_vip", "emoji": "<:camap_vip:1213776381046034452>", "rank": "A"},
            {"name": "camapdaubua_vip", "emoji": "<:camapdaubua_vip:1215242286418366514>", "rank": "A"},
        ]
        fish_list_B = [
            {"name": "cabuom_trendy", "emoji": "<:cabuom_trendy:1213374797317410846>", "rank": "B"},
            {"name": "cadiacam_trendy", "emoji": "<:cadiacam_trendy:1213734295378862080>", "rank": "B"},
            {"name": "cahe_trendy", "emoji": "<:cahe_trendy:1213432434377629727>", "rank": "B"},
            {"name": "cabluetang_trendy", "emoji": "<:cabluetang_trendy:1213537800289263696>", "rank": "B"},
            {"name": "calongden_trendy", "emoji": "<:calongden_trendy:1213432395890688000>", "rank": "B"},
            {"name": "cathantien_trendy", "emoji": "<:cathantien_trendy:1213733169724002354>", "rank": "B"},
            {"name": "cavet_trendy", "emoji": "<:cavet_trendy:1213736162762424380>", "rank": "B"},
            {"name": "caneon_trendy", "emoji": "<:caneon_trendy:1214823844087599125>", "rank": "B"},
            {"name": "casutu_trendy", "emoji": "<:casutu_trendy:1214826508481208330>", "rank": "B"},
            {"name": "cachimco_trendy", "emoji": "<:cachimco_trendy:1214823631377661992>", "rank": "B"},
            {"name": "casacgam_trendy", "emoji": "<:casacgam_trendy:1214817462395342898>", "rank": "B"},
            {"name": "cabonuhoang_trendy", "emoji": "<:cabonuhoang_trendy:1214817413342957649>", "rank": "B"},
            {"name": "cadolabac_trendy", "emoji": "<:cadolabac_trendy:1214821326469074954>", "rank": "B"},
            {"name": "cakhetrang_trendy", "emoji": "<:cakhetrang_bien:1214810113848639508>", "rank": "B"},
        ]
        fish_list_C = [
            {"name": "cachim_bien", "emoji": "<:cachim_bien:1213763161908314173>", "rank": "C"},
            {"name": "cadua", "emoji": "<:cadua:1213374821866672178>", "rank": "C"},
            {"name": "cahong_bien", "emoji": "<:cahong_bien:1213374853193670657> ", "rank": "C"},
            {"name": "cangu_bien", "emoji": "<:cangu_bien:1214053596480409610>", "rank": "C"},
            {"name": "cathu_bien", "emoji": "<:cathu_bien:1214824118952656896>", "rank": "C"},
            {"name": "canoc_bien", "emoji": "<:canoc_bien:1213374875922599937>", "rank": "C"},
            {"name": "catuyet_bien", "emoji": "<:catuyet_bien:1214824043203530782>", "rank": "C"},
            {"name": "cakiem_bien", "emoji": "<:cakiem_bien:1213795318316015676>", "rank": "C"},
            {"name": "cachuon_bien", "emoji": "<:cachuon_bien:1214821078166413342>", "rank": "C"},
            {"name": "cabongtuongvayxanh_bien", "emoji": "<:cabongtuongvayxanh_bien:1214817434721325086>", "rank": "C"},
        ]
        fish_list_D = [
            {"name": "cachep_song", "emoji": "<:cachep_song:1214823778991738930>", "rank": "D"},
            {"name": "cabong_song", "emoji": "<:cabong_song:1213771758922895380>", "rank": "D"},
            {"name": "cadieuhong_song", "emoji": "<:cadieuhong_song:1213763282280783913>", "rank": "D"},
            {"name": "camu_song", "emoji": "<:camu_song:1213754239147442216>", "rank": "D"},
            {"name": "catre_song", "emoji": "<:catre_song:1215330238804918323>", "rank": "D"},
            {"name": "cahoicauvong_song", "emoji": "<:cahoicauvong_song:1214824502974742590>", "rank": "D"},
            {"name": "cataituong_song", "emoji": "<:cataituong_song:1213767502694322218>", "rank": "D"},
            {"name": "cabon_song", "emoji": "<:cabon_song:1213771586029621308>", "rank": "D"},
            {"name": "cathaclac_song", "emoji": "<:cathatlat_song:1214821126056976395>", "rank": "D"},
            {"name": "carovang_song", "emoji": "<:carovang_song:1214809953865437204>", "rank": "D"},
            {"name": "cavuocda_song", "emoji": "<:cavuocda_song:1214809912207478794>", "rank": "D"},
            {"name": "caliet_song", "emoji": "<:caliet_song:1214809882457280562>", "rank": "D"},
        ]
        fish_list_E = [
            {"name": "rac", "emoji": "<:rac:1211435291391299654>", "rank": "E"},
        ]
        fish_list_F = [
            {"name": "dutday", "emoji": "<:dutday:1211435291391299654>", "rank": "F"},
        ]

        fish_list = fish_list_A + fish_list_B + fish_list_C + fish_list_D + fish_list_E + fish_list_F

        can_name = ""
        for item in kho_can:
            if item.get("used") > 0:
                can_name = item.get("name", "")
                break
        # Chọn loại cá dựa trên loại của "cần câu"
        if can_name == "Can 100":
            random_number = random.random()  # Số ngẫu nhiên từ 0 đến 1
            if random_number < 0.1:  # 10% fish_list_E
                fish_list = fish_list_E
            else:  # 90%
                random_number = random.random()  # Số ngẫu nhiên mới
                if random_number < 0.03:  # 3% fish_list_A
                    fish_list = fish_list_A
                elif random_number < 0.25:  # 22% fish_list_B
                    fish_list = fish_list_B
                elif random_number < 0.6:  # 35% fish_list_C
                    fish_list = fish_list_C
                else:  # 40% fish_list_D
                    fish_list = fish_list_D

        elif can_name == "Can 80":
            random_number = random.random()  # Số ngẫu nhiên từ 0 đến 1
            if random_number < 0.1:  # 10% fish_list_E
                fish_list = fish_list_E
            elif random_number < 0.2:  # 10% fish_list_F
                fish_list = fish_list_F
            else:  # 80%
                random_number = random.random()  # Số ngẫu nhiên mới
                if random_number < 0.02:  # 2% fish_list_A
                    fish_list = fish_list_A
                elif random_number < 0.15:  # 13% fish_list_B
                    fish_list = fish_list_B
                elif random_number < 0.55:  # 40% fish_list_C
                    fish_list = fish_list_C
                else:  # 45% fish_list_D
                    fish_list = fish_list_D

        elif can_name == "Can 50":
            random_number = random.random()  # Số ngẫu nhiên từ 0 đến 1
            if random_number < 0.2:  # 20% fish_list_F
                fish_list = fish_list_F
            elif random_number < 0.4:  # 20% fish_list_E
                fish_list = fish_list_E
            else:  # 60%
                random_number = random.random()  # Số ngẫu nhiên mới
                if random_number < 0.05:  # 5% fish_list_B
                    fish_list = fish_list_B
                elif random_number < 0.35:  # 35% fish_list_C
                    fish_list = fish_list_C
                else:  # 60% fish_list_D
                    fish_list = fish_list_D

        fish = random.choice(fish_list)

        # Cộng kinh nghiệm tùy theo rank của cá đã câu được
        exp_increase = 0
        fish_rank = fish.get("rank")
        if fish_rank == "A":
            exp_increase = 500
        elif fish_rank == "B":
            exp_increase = 300
        elif fish_rank == "C":
            exp_increase = 200
        elif fish_rank == "D":
            exp_increase = 100
        # Cập nhật thông tin cá đã câu
        fish_name = fish.get("name")
        fish_emoji = fish.get("emoji")
        fish_rank = fish.get("rank")
        for item in kho_ca:
            if item.get("name") == fish_name:
                item["quantity"] += 1
                break
        else:
            kho_ca.append({"name": fish_name, "emoji": fish_emoji, "quantity": 1, "rank": fish_rank})
        cursor.execute("UPDATE users SET kho_ca = ?, exp_fish = exp_fish + ? WHERE user_id = ?", (json.dumps(kho_ca), exp_increase, user_id))
        conn.commit()        
        # Gửi tin nhắn
        if fish_name == "rac":
            fish_name_display = "rác"
            thumbnail = "https://cdn.discordapp.com/attachments/1213787485046444072/1214757898639515699/1211435291391299654.png"
        elif fish_name == "dutday":
            fish_name_display = "Dây câu"
        elif fish_name == "caheo_vip":
            fish_name_display = "Cá Heo"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1213805597611266078/gift_160_x_160_px_-_2024-03-03T180800.761.png"
        elif fish_name == "camap_vip":
            fish_name_display = "Cá Mập"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1215216751739142145/gift_160_x_160_px_-_2024-03-07T134340.639.png"
        elif fish_name == "canhamvoi_vip":
            fish_name_display = "Cá Nhám Voi"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1213805598676615218/gift_160_x_160_px_-_2024-03-03T180418.009.png"
        elif fish_name == "caduoi_vip":
            fish_name_display = "Cá Đuối"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1213805600064938025/gift_160_x_160_px_-_2024-03-02T225307.768.png"
        elif fish_name == "cavoisatthu_vip":
            fish_name_display = "Cá Voi Sát Thủ"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1213805599184388106/gift_160_x_160_px_-_2024-03-03T155904.643.png"

        elif fish_name == "cabuom_trendy":
            fish_name_display = "Cá Bướm"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1213799433003601951/gift_160_x_160_px_-_2024-03-02T060449.964.png"
        elif fish_name == "cadiacam_trendy":
            fish_name_display = "Cá Dĩa Cam"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1213799107542515722/gift_160_x_160_px_-_2024-03-02T135146.396.png"
        elif fish_name == "cahe_trendy":
            fish_name_display = "Cá Hề"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1213799107064369172/gift_160_x_160_px_-_2024-03-02T142452.982.png"
        elif fish_name == "cabluetang_trendy":
            fish_name_display = "Cá Blue Tang"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1213799106816909312/gift_160_x_160_px_-_2024-03-02T224220.130.png"
        elif fish_name == "calongden_trendy":
            fish_name_display = "Cá Lồng Đèn"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1213799106552537188/gift_160_x_160_px_-_2024-03-02T145451.159.png"
        elif fish_name == "cathantien_trendy":
            fish_name_display = "Cá Thần Tiên"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1213799107316158515/gift_160_x_160_px_-_2024-03-03T131742.829.png"
        elif fish_name == "cavet_trendy":
            fish_name_display = "Cá Vẹt"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1213799106305327164/gift_160_x_160_px_-_2024-03-03T133309.577.png"
        elif fish_name == "caneon_trendy":
            fish_name_display = "Cá Neon"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1214826750824161300/gift_160_x_160_px_-_2024-03-06T133247.556.png"
        elif fish_name == "casutu_trendy":
            fish_name_display = "Cá Sư Tử"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1214826750601732128/gift_160_x_160_px_-_2024-03-06T134604.219.png"
        elif fish_name == "cachimco_trendy":
            fish_name_display = "Cá Chim Cỏ"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1214827439524417578/gift_160_x_160_px_-_2024-03-06T133446.001.png"
        elif fish_name == "casacgam_trendy":
            fish_name_display = "Cá Sặc Gấm"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1214827441592467506/gift_160_x_160_px_-_2024-03-06T124950.703.png"
        elif fish_name == "cabonuhoang_trendy":
            fish_name_display = "Cá Bò Nữ Hoàng"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1214827441348943932/gift_160_x_160_px_-_2024-03-06T125905.513.png"
        elif fish_name == "cadolabac_trendy":
            fish_name_display = "Cá Đô La Bạc"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1214827440480985088/gift_160_x_160_px_-_2024-03-06T131630.590.png"
        elif fish_name == "cakhetrang_trendy":
            fish_name_display = "Cá Khế Trăng"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1214903204781756477/gift_160_x_160_px_-_2024-03-03T123218.223.png"

        elif fish_name == "cachim_bien":
            fish_name_display = "Cá Chim"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1213795204302372884/gift_160_x_160_px_-_2024-03-03T152106.339.png"
        elif fish_name == "cadua":
            fish_name_display = "Cá Dũa"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1213795204633596014/gift_160_x_160_px_-_2024-03-02T060335.041.png"
        elif fish_name == "cahong_bien":
            fish_name_display = "Cá Hồng"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1213795204906221608/gift_160_x_160_px_-_2024-03-02T060053.284.png"
        elif fish_name == "cangu_bien":
            fish_name_display = "Cá Ngừ"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1214054371923337256/gift_160_x_160_px_-_2024-03-04T103518.373.png"
        elif fish_name == "cathu_bien":
            fish_name_display = "Cá Thu"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1214826750379298826/gift_160_x_160_px_-_2024-03-06T120634.495.png"
        elif fish_name == "canoc_bien":
            fish_name_display = "Cá Nóc"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1213795205463941190/gift_160_x_160_px_-_2024-03-02T055930.170.png"
        elif fish_name == "catuyet_bien":
            fish_name_display = "Cá Tuyết"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1214826750144679956/gift_160_x_160_px_-_2024-03-06T120846.811.png"
        elif fish_name == "cakiem_bien":
            fish_name_display = "Cá Kiếm"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1213795205828837376/gift_160_x_160_px_-_2024-03-02T173249.798.png"
        elif fish_name == "cachuon_bien":
            fish_name_display = "Cá Chuồn"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1214827439838986280/gift_160_x_160_px_-_2024-03-06T132502.536.png"
        elif fish_name == "cabongtuongvayxanh_bien":
            fish_name_display = "Cá Bống Tượng Vây Xanh"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1214827440791359568/gift_160_x_160_px_-_2024-03-06T131020.504.png"

        elif fish_name == "cachep_song":
            fish_name_display = "Cá Chép"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1214826749498626048/gift_160_x_160_px_-_2024-03-06T123400.705.png"
        elif fish_name == "cabong_song":
            fish_name_display = "Cá Bống"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1213789446722293801/gift_160_x_160_px_-_2024-03-03T155124.615.png"
        elif fish_name == "cadieuhong_song":
            fish_name_display = "Cá Diêu Hồng"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1213789444524613672/gift_160_x_160_px_-_2024-03-03T145943.773.png"
        elif fish_name == "camu_song":
            fish_name_display = "Cá Mú"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1213789445405286521/gift_160_x_160_px_-_2024-03-03T144133.899.png"
        elif fish_name == "catre_song":
            fish_name_display = "Cá Trê"
            thumbnail = "https://cdn.discordapp.com/attachments/1213787485046444072/1215330033699266560/gift_160_x_160_px_-_2024-03-07T204253.png"
        elif fish_name == "cahoicauvong_song":
            fish_name_display = "Cá Hồi Cầu Vồng"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1214826749809000470/gift_160_x_160_px_-_2024-03-06T121657.935.png"
        elif fish_name == "cataituong_song":
            fish_name_display = "Cá Tai Tượng"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1213789446349127720/gift_160_x_160_px_-_2024-03-03T145729.809.png"
        elif fish_name == "cabon_song":
            fish_name_display = "Cá Bơn"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1213806182347837481/gift_160_x_160_px_-_2024-03-03T135545.313.png"
        elif fish_name == "cathaclac_song":
            fish_name_display = "Cá Thác Lác"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1214827440187252766/gift_160_x_160_px_-_2024-03-06T132001.739.png"
        elif fish_name == "carovang_song":
            fish_name_display = "Cá Rô Vàng"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1214827442074550272/gift_160_x_160_px_-_2024-03-06T121110.978.png"
        elif fish_name == "cavuocda_song":
            fish_name_display = "Cá Vuợc Đá"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1214827442322145290/gift_160_x_160_px_-_2024-03-06T121325.108.png"
        elif fish_name == "caliet_song":
            fish_name_display = "Cá Liệt"
            thumbnail = "https://media.discordapp.net/attachments/1213787485046444072/1214827441835479050/gift_160_x_160_px_-_2024-03-06T123045.169.png"
        else:
            fish_name_display = fish_name
        embed = discord.Embed(title=f"", color=discord.Color.from_rgb(255,255,255), description="")
        embed.add_field(name="", value=f"{cauca} **{interaction.user.mention} đã thả câu, đang đợi cá đớp mồi {cauca1}**", inline=False)
        await interaction.response.send_message(embed=embed)
        # disabled nút 10s
        await self.disable_button_for("cau", 10)
        if fish_name == "rac":
            embed = discord.Embed(title=f"{cauca2} Chúc mừng __{interaction.user.display_name}__, bạn câu được 1 túi {fish_name_display} {fish_emoji}. Vì môi trường, bạn hãy tái chế nó!", color=discord.Color.from_rgb(255,255,255), description="")
            embed.set_thumbnail(url=thumbnail)
            await interaction.edit_original_response(embed=embed)
        elif fish_name == "dutday":
            embed = discord.Embed(title=f"{khongdutien} **Ôi không! {fish_name_display} của bạn đã bị đứt, bấm câu lại nhé!**", color=discord.Color.from_rgb(255,255,255), description="")
            await interaction.edit_original_response(embed=embed)
        elif fish_name in [fish["name"] for fish in fish_list_A]:
            embed1 = discord.Embed(title=f"{saocavip} Chúc mừng __{interaction.user.display_name}__, bạn câu được 1 con {fish_name_display} {cauca3}", color=discord.Color.from_rgb(238,238,0), description="")
            embed1.add_field(name=f"**Điểm kinh nghiệm + 500 {exp}**", value=f"", inline=False)
            embed1.set_thumbnail(url=thumbnail)
            await interaction.edit_original_response(embed=embed1)
        elif fish_name in [fish["name"] for fish in fish_list_B]:
            embed2 = discord.Embed(title=f"{saocatrendy} Chúc mừng __{interaction.user.display_name}__, bạn câu được 1 con {fish_name_display} {cauca3}", color=discord.Color.from_rgb(255, 105, 180), description="")
            embed2.add_field(name=f"**Điểm kinh nghiệm + 300 {exp}**", value=f"", inline=False)
            embed2.set_thumbnail(url=thumbnail)
            await interaction.edit_original_response(embed=embed2)
        elif fish_name in [fish["name"] for fish in fish_list_C]:
            embed3 = discord.Embed(title=f"{saocabien} Chúc mừng __{interaction.user.display_name}__, bạn câu được 1 con {fish_name_display} {cauca3}", color=discord.Color.from_rgb(163, 221, 255), description="")
            embed3.add_field(name=f"**Điểm kinh nghiệm + 200 {exp}**", value=f"", inline=False)
            embed3.set_thumbnail(url=thumbnail)
            await interaction.edit_original_response(embed=embed3)
        elif fish_name in [fish["name"] for fish in fish_list_D]:
            embed4 = discord.Embed(title=f"{saocasong} Chúc mừng __{interaction.user.display_name}__, bạn câu được 1 con {fish_name_display} {cauca3}", color=discord.Color.from_rgb(165, 255, 174), description="")
            embed4.add_field(name=f"**Điểm kinh nghiệm + 100 {exp}**", value=f"", inline=False)
            embed4.set_thumbnail(url=thumbnail)
            await interaction.edit_original_response(embed=embed4)

    @discord.ui.button(label="Sửa Cần", style=discord.ButtonStyle.blurple, emoji="<:suacan:1213359207705743400>", row=1, disabled = True)
    async def suacan(self, interaction: discord.Interaction, button: discord.ui.Button):
        cursor.execute("SELECT balance, kho_can FROM users WHERE user_id = ?", (interaction.user.id,))
        result = cursor.fetchone()
        if result:
            balance, existing_items_json = result
            if existing_items_json:
                existing_items = json.loads(existing_items_json)
            else:
                existing_items = []
            can_cost = {
                "Can 50": 50000,
                "Can 80": 80000,
                "Can 100": 100000
            }
            for item in existing_items:
                if item["name"] in can_cost and item["used"] == 0:
                    if balance >= can_cost.get(item["name"], 0):
                        # Thực hiện sửa cần câu
                        item["used"] = 10
                        cursor.execute("UPDATE users SET kho_can = ? WHERE user_id = ?", (json.dumps(existing_items), interaction.user.id))
                        new_balance = balance - can_cost[item["name"]]
                        cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, interaction.user.id))
                        conn.commit()
                        await interaction.response.send_message(f"{suacan1} **{interaction.user.mention} sửa cần thành công với số tiền {can_cost[item['name']]:,} {cash}**")
                        await self.disable_button_for("suacan", 10)
                        return
                    else:
                        await interaction.response.send_message(f"**{interaction.user.mention}, bạn không đủ tiền để sửa cần**", ephemeral=True)
                        return
            await interaction.response.send_message(f"**{interaction.user.mention}, cần câu của bạn chưa bị hỏng**", ephemeral=True)
        else:
            await interaction.response.send_message("Không thể tìm thấy thông tin người dùng", ephemeral=True)

    @discord.ui.button(label="Tái Chế", style=discord.ButtonStyle.blurple, emoji="<:taiche:1211435320709480468>", row=1)
    async def taiche(self, interaction: discord.Interaction, button: discord.ui.Button):
        cursor.execute("SELECT kho_ca FROM users WHERE user_id = ?", (interaction.user.id,))
        result = cursor.fetchone()
        if result:
            kho_ca_json = result[0]
            if kho_ca_json:
                kho_ca = json.loads(kho_ca_json)
                rac_found = False
                for item in kho_ca:
                    if item.get("name") == "rac":
                        rac_quantity = item.get("quantity", 0)
                        if rac_quantity > 0:  # Kiểm tra nếu quantity của rac lớn hơn 0 mới tiến hành tái chế
                            item["quantity"] = 0
                            mamcay_found = False
                            for existing_item in kho_ca:
                                if existing_item.get("name") == "mamcay":
                                    existing_item["quantity"] += rac_quantity
                                    mamcay_found = True
                                    break
                            if not mamcay_found:
                                mamcay_item = {
                                    "name": "mamcay",
                                    "emoji": "<a:diemtaiche:1211410013868789850>",
                                    "quantity": rac_quantity,
                                    "rank": "F"
                                }
                                kho_ca.append(mamcay_item)
                            cursor.execute("UPDATE users SET kho_ca = ? WHERE user_id = ?", (json.dumps(kho_ca), interaction.user.id))
                            conn.commit()
                            await interaction.response.send_message(f"**{taiche} {interaction.user.mention} tái chế thành công {rac_quantity} {rac}, bạn có {rac_quantity} {mamcay} điểm tái chế**",)
                            rac_found = True
                            break
                if not rac_found:
                    await interaction.response.send_message(f"**Không có {rac} để tái chế**", ephemeral=True)
            else:
                await interaction.response.send_message(f"**Không có {rac} để tái chế**", ephemeral=True)
        else:
            await interaction.response.send_message("Không thể tìm thấy thông tin của bạn", ephemeral=True)


    async def on_click(self, interaction: discord.Interaction):
        if interaction.user.id == self.enable_buttons:
            await self.process_components(interaction)

class EventFish(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def cauca(self, ctx):
        if ctx.channel.id not in [1215331218124574740, 1215331281878130738]:
            return None
        if not is_registered(ctx.author.id):
            await ctx.send(f"{dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
        else:
            cursor.execute("SELECT kho_ca, kho_moi, kho_can FROM users WHERE user_id = ?", (ctx.author.id,))
            result = cursor.fetchone()
            kho_ca, kho_moi, kho_can = result

            embed = discord.Embed(title="", color=discord.Color.from_rgb(255,255,255), description="")
            if ctx.author.avatar:
                avatar_url = ctx.author.avatar.url
            else:
                avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
            embed.set_author(name=f"{ctx.author.display_name} đi câu cá", icon_url=avatar_url)
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1213787485046444072/1215992870721290352/OIG2.hKyhEX1I.jpg")
            moi_quantity = 0
            can_name = "Chưa có cần câu"
            can_emoji = ""
            can_used = 0
            rac_quantity = 0
            try:
                if kho_moi:
                    moi_info = json.loads(kho_moi)[0]
                    moi_quantity = moi_info.get("quantity", 0)
                if kho_can:
                    can_info = json.loads(kho_can)[0]
                    can_name = can_info.get("name", "")
                    if can_name == "Can 100":
                        can_name = "Cần câu 100%"
                    elif can_name == "Can 50":
                        can_name = "Cần câu 50%"
                    elif can_name == "Can 80":
                        can_name = "Cần câu 80%"
                    can_emoji = can_info.get("emoji", "")
                    can_used = can_info.get("used", 0)
                if kho_ca:
                    rac_info = json.loads(kho_ca)
                    if isinstance(rac_info, list):
                        for item in rac_info:
                            if item.get("name") == "rac":
                                rac_quantity = item.get("quantity", 0)
                                break
            except json.JSONDecodeError:
                # Xử lý trường hợp cột kho_ca, kho_moi, kho_can chứa giá trị NULL hoặc rỗng
                pass
            embed.add_field(name="", value=f"**Mồi câu: {moi_quantity} {moicau}\n {can_name} {can_emoji}: {can_used}\n Rác: {rac_quantity} {rac}\n ---------------------**", inline=False)
            enable_buttons = ctx.author.id
            view = EventFishView(enable_buttons)
            message = await ctx.send(embed=embed, view=view)
            view.message = message
            await view.wait()
    
    @cauca.error
    async def cauca_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = divmod(int(error.retry_after), 60)  # Chia cho 60 để có phút và giây
            formatted_time = f"{remaining_time[1]}s"
            message = await ctx.send(f"{canhbao} | Vui lòng đợi thêm `{formatted_time}` để có thể sử dụng lệnh này!!")
            await asyncio.sleep(3)
            await message.delete()
            await ctx.message.delete()

    @commands.command()
    async def khoca(self, ctx):
        if ctx.channel.id not in [1193936442045505546, 1026627301573677147, 1035183712582766673, 1090897131486842990, 1213122881802997770, 1107957984266563656, 1215331218124574740, 1215331281878130738]:
            return None
        cursor.execute("SELECT kho_ca, exp_fish FROM users WHERE user_id = ?", (ctx.author.id,))
        result = cursor.fetchone()
        if result:
            kho_ca_json, exp_fish = result
            embed = discord.Embed(title="", color=discord.Color.from_rgb(255,255,255))
            if ctx.author.avatar:
                avatar_url = ctx.author.avatar.url
            else:
                avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
            embed.set_author(name=f"Kho Cá Của {ctx.author.display_name}", icon_url=avatar_url)
            kho_ca = json.loads(kho_ca_json) if kho_ca_json else []

            # Lấy điểm kinh nghiệm và điểm tái chế
            exp_ca = exp_fish if exp_fish else 0
            taiche = next((item.get('quantity', 0) for item in kho_ca if item.get('name') == 'mamcay'), 0)

            ranks = ["D", "C", "B", "A"]
            total_species = 0  # Biến đếm số loài cá
            for rank in ranks:
                # Đổi tên của rank tương ứng
                if rank == "D":
                    rank_name = f"{saocasong} Cá Nước Ngọt"
                elif rank == "C":
                    rank_name = f"{saocabien} Cá Biển"
                elif rank == "B":
                    rank_name = f"{saocatrendy} Cá Trendy"
                elif rank == "A":
                    rank_name = f"{saocavip} Cá Vip"
                items_of_rank = [item for item in kho_ca if item.get("rank") == rank]
                if items_of_rank:
                    emojis = " ".join([f"{item.get('emoji')} {get_superscript(item.get('quantity'))}" for item in items_of_rank])
                    embed.add_field(name=f"**{rank_name}**", value=f"**{emojis}**", inline=False)
                    # Đếm số loài cá
                    total_species += len(items_of_rank)
                else:
                    embed.add_field(name=f"**{rank_name}**", value="", inline=False)
            embed.add_field(name=f"-----------------------\n**Điểm kinh nghiệm: {exp_ca} {exp}\nĐiểm tái chế: {taiche} {mamcay}\nBộ sưu tập cá: {total_species}/42**", value=f"", inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Không thể tìm thấy thông tin của bạn.")

    @commands.command( description="set coin kim cương cho người khác")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @is_guild_owner_or_bot_owner()
    async def setkc(self, ctx, amount: int, member: typing.Optional[discord.Member] = None):
        if member is None:  # Nếu không nhập người dùng, set cho tất cả người dùng trong bảng users
            cursor.execute("UPDATE users SET coin_kc = coin_kc + ?", (amount,))
            conn.commit()
            formatted_amount = "{:,}".format(amount)
            await ctx.send(f"**HGTT đã trao tặng** __**{formatted_amount}**__ {fishcoin} **cho tất cả thành viên**")
        elif is_registered(member.id):
            cursor.execute(
                "UPDATE users SET coin_kc = coin_kc + ? WHERE user_id = ?", (amount, member.id))
            conn.commit()
            formatted_amount = "{:,}".format(amount)
            await ctx.send(f"**HGTT đã trao tặng** __**{formatted_amount}**__ {fishcoin} **cho {member.display_name}**")
        else:
            await ctx.send("Bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")

    @commands.command()
    @is_guild_owner_or_bot_owner()
    async def rskhoca(self, ctx, user: discord.User = None):
        if user:
            # Cập nhật của người dùng được chỉ định
            cursor.execute("UPDATE users SET kho_ca = ?, exp_fish = ? WHERE user_id = ?", ('', 0, user.id))
            conn.commit()
            await ctx.send(f"Đã reset kho của người dùng {user.mention}")
        else:
            # Cập nhật tất cả người dùng
            cursor.execute("UPDATE users SET kho_ca = '', exp_fish = 0")
            conn.commit()
            await ctx.send("Đã reset kho của tất cả người dùng")

    @commands.command()
    @is_guild_owner_or_bot_owner()
    async def rskhocan(self, ctx, user: discord.User = None):
        if user:
            # Cập nhật của người dùng được chỉ định
            cursor.execute("UPDATE users SET kho_can = ? WHERE user_id = ?", ('', user.id))
            conn.commit()
            await ctx.send(f"Đã reset kho của người dùng {user.mention}")
        else:
            # Cập nhật tất cả người dùng
            cursor.execute("UPDATE users SET kho_can = ''")
            conn.commit()
            await ctx.send("Đã reset kho của tất cả người dùng")

    @commands.command()
    @is_guild_owner_or_bot_owner()
    async def rskhomoi(self, ctx, user: discord.User = None):
        if user:
            # Cập nhật của người dùng được chỉ định
            cursor.execute("UPDATE users SET kho_moi = ? WHERE user_id = ?", ('', user.id))
            conn.commit()
            await ctx.send(f"Đã reset kho của người dùng {user.mention}")
        else:
            # Cập nhật tất cả người dùng
            cursor.execute("UPDATE users SET kho_moi = ''")
            conn.commit()
            await ctx.send("Đã reset kho của tất cả người dùng")
    
    @commands.command()
    @is_guild_owner_or_bot_owner()
    async def rskc(self, ctx, user: discord.User = None):
        if user:
            # Cập nhật của người dùng được chỉ định
            cursor.execute("UPDATE users SET coin_kc = ? WHERE user_id = ?", (0, user.id))
            conn.commit()
            await ctx.send(f"Đã reset coin kim cương của người dùng {user.mention}")
        else:
            # Cập nhật tất cả người dùng
            cursor.execute("UPDATE users SET coin_kc = 0")
            conn.commit()
            await ctx.send("Đã reset xu cá của tất cả người dùng")

async def setup(client):
    await client.add_cog(EventFish(client))