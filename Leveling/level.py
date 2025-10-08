import discord
from discord.ext import commands
from typing import Optional, Union
import config
from .database import LevelingDatabase
from .image_generator import ProfileImageGenerator, AchievementImageGenerator
from .utils import format_time, format_number, get_achievement_emoji

class LevelingCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = LevelingDatabase()
        self.profile_generator = ProfileImageGenerator()
        self.achievement_generator = AchievementImageGenerator()

    @commands.hybrid_command(name="profile", aliases=["lv"], description="Xem profile level của bạn hoặc người khác")
    async def profile_command(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        """Display user's leveling profile"""
        target_member = member or ctx.author
        
        if target_member.bot:
            embed = discord.Embed(
                title="❌ Lỗi",
                description="Bot không có hệ thống cấp độ!",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # Get user stats
        stats = self.db.get_user_stats(target_member.id, ctx.guild.id)
        
        # Get user rank
        leaderboard = self.db.get_leaderboard(ctx.guild.id, limit=1000)
        user_rank = None
        for entry in leaderboard:
            if entry['user_id'] == target_member.id:
                user_rank = entry['rank']
                break
        
        if user_rank is None:
            user_rank = len(leaderboard) + 1
        
        total_members = len([m for m in ctx.guild.members if not m.bot])
        
        try:
            # Generate profile image
            profile_image = await self.profile_generator.create_profile_card(
                target_member, stats, user_rank, total_members
            )
            
            # Create embed
            embed = discord.Embed(
                title=f"🎯 Profile của {target_member.display_name}",
                color=discord.Color.from_rgb(*self.profile_generator.get_background_color(stats))
            )
            
            # Add detailed stats in embed
            xp_needed = self.profile_generator.calculate_xp_for_next_level(stats['level'])
            progress_percent = (stats['xp'] / xp_needed * 100) if xp_needed > 0 else 0
            
            embed.add_field(
                name="📊 Thống Kê Chi Tiết",
                value=f"""**Cấp Độ:** {stats['level']} (Hạng #{user_rank}/{total_members})
**Kinh Nghiệm:** {stats['xp']:,} / {xp_needed:,} ({progress_percent:.1f}%)
**Tổng XP:** {format_number(stats['total_xp'])}
**Tin Nhắn:** {format_number(stats['messages'])}
**Thời Gian Voice:** {format_time(stats['voice_minutes'])}
**Thành Tựu:** {len(stats['achievements'])}/{ len(config.ACHIEVEMENTS)}""",
                inline=False
            )
            
            # Add recent achievements
            if stats['achievements']:
                recent_achievements = stats['achievements'][-3:]  # Show last 3
                achievement_text = ""
                
                for achievement_id in recent_achievements:
                    achievement = config.ACHIEVEMENTS.get(achievement_id, {})
                    if achievement:
                        emoji = get_achievement_emoji(achievement_id)
                        achievement_text += f"{emoji} {achievement['name']}\n"
                
                embed.add_field(
                    name="🏆 Thành Tựu Gần Đây",
                    value=achievement_text or "Chưa có thành tựu nào",
                    inline=True
                )
            
            # Send image with embed
            file = discord.File(profile_image, filename="profile.png")
            embed.set_image(url="attachment://profile.png")
            
            await ctx.send(file=file, embed=embed)
        
        except Exception as e:
            # Fallback to text-only embed if image generation fails
            embed = discord.Embed(
                title=f"🎯 Profile của {target_member.display_name}",
                color=discord.Color.blue()
            )
            
            xp_needed = self.db.xp_for_next_level(stats['level'])
            progress_percent = (stats['xp'] / xp_needed * 100) if xp_needed > 0 else 0
            
            embed.add_field(
                name="📊 Thống Kê",
                value=f"""**Cấp Độ:** {stats['level']} (#{user_rank})
**XP:** {stats['xp']:,} / {xp_needed:,} ({progress_percent:.1f}%)
**Tổng XP:** {format_number(stats['total_xp'])}
**Tin Nhắn:** {format_number(stats['messages'])}
**Voice:** {format_time(stats['voice_minutes'])}
**Thành Tựu:** {len(stats['achievements'])}/{ len(config.ACHIEVEMENTS)}""",
                inline=False
            )
            
            embed.set_thumbnail(url=target_member.display_avatar.url)
            await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="rank", description="Xem rank ngắn gọn")
    async def rank_command(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        """Display compact rank card"""
        target_member = member or ctx.author
        
        if target_member.bot:
            embed = discord.Embed(
                title="❌ Lỗi",
                description="Bot không có hệ thống cấp độ!",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # Get user stats and rank
        stats = self.db.get_user_stats(target_member.id, ctx.guild.id)
        leaderboard = self.db.get_leaderboard(ctx.guild.id, limit=1000)
        
        user_rank = None
        for entry in leaderboard:
            if entry['user_id'] == target_member.id:
                user_rank = entry['rank']
                break
        
        if user_rank is None:
            user_rank = len(leaderboard) + 1
        
        try:
            # Generate rank card
            rank_image = await self.profile_generator.create_rank_card(target_member, stats, user_rank)
            
            file = discord.File(rank_image, filename="rank.png")
            await ctx.send(file=file)
        
        except Exception as e:
            # Fallback to embed
            xp_needed = self.db.xp_for_next_level(stats['level'])
            progress_percent = (stats['xp'] / xp_needed * 100) if xp_needed > 0 else 0
            
            embed = discord.Embed(
                title=f"📈 Rank của {target_member.display_name}",
                description=f"**Cấp độ:** {stats['level']} | **Hạng:** #{user_rank}\n**XP:** {stats['xp']:,}/{xp_needed:,} ({progress_percent:.1f}%)",
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=target_member.display_avatar.url)
            await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="leaderboard", aliases=["lb"], description="Xem bảng xếp hạng")
    async def leaderboard_command(self, ctx: commands.Context, sort_by: str = "level"):
        """Display guild leaderboard"""
        valid_sorts = ["level", "xp", "messages", "voice"]
        if sort_by.lower() not in valid_sorts:
            sort_by = "level"
        else:
            sort_by = sort_by.lower()
        
        leaderboard = self.db.get_leaderboard(ctx.guild.id, limit=15, sort_by=sort_by)
        
        if not leaderboard:
            embed = discord.Embed(
                title="📊 Bảng Xếp Hạng",
                description="Chưa có dữ liệu xếp hạng!",
                color=discord.Color.blue()
            )
            return await ctx.send(embed=embed)
        
        # Create leaderboard embed
        sort_names = {
            "level": "Cấp Độ",
            "xp": "Tổng XP", 
            "messages": "Tin Nhắn",
            "voice": "Thời Gian Voice"
        }
        
        embed = discord.Embed(
            title=f"🏆 Bảng Xếp Hạng - {sort_names[sort_by]}",
            color=discord.Color.gold()
        )
        
        leaderboard_text = ""
        medals = ["🥇", "🥈", "🥉"]
        
        for entry in leaderboard:
            user = ctx.guild.get_member(entry['user_id'])
            if not user:
                continue
            
            rank = entry['rank']
            medal = medals[rank - 1] if rank <= 3 else f"**{rank}.**"
            
            if sort_by == "level":
                value = f"Cấp {entry['level']} ({format_number(entry['total_xp'])} XP)"
            elif sort_by == "xp":
                value = f"{format_number(entry['total_xp'])} XP"
            elif sort_by == "messages":
                value = f"{format_number(entry['messages'])} tin nhắn"
            elif sort_by == "voice":
                value = f"{format_time(entry['voice_minutes'])}"
            
            leaderboard_text += f"{medal} {user.display_name} - {value}\n"
        
        embed.description = leaderboard_text
        embed.set_footer(text=f"Sắp xếp theo: {sort_names[sort_by]} | Sử dụng zlb <level/xp/messages/voice> để đổi")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="achievements", aliases=["thanhtuu"], description="Xem thành tựu của bạn")
    async def achievements_command(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        """Display user achievements"""
        target_member = member or ctx.author
        
        if target_member.bot:
            embed = discord.Embed(
                title="❌ Lỗi", 
                description="Bot không có thành tựu!",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # Get user achievements
        stats = self.db.get_user_stats(target_member.id, ctx.guild.id)
        user_achievements = stats['achievements']
        
        # Create achievements embed
        embed = discord.Embed(
            title=f"🏆 Thành Tựu của {target_member.display_name}",
            description=f"Đã mở khóa: {len(user_achievements)}/{len(config.ACHIEVEMENTS)} thành tựu",
            color=discord.Color.gold()
        )
        
        # Unlocked achievements
        if user_achievements:
            unlocked_text = ""
            for achievement_id in user_achievements:
                achievement = config.ACHIEVEMENTS.get(achievement_id, {})
                if achievement:
                    emoji = get_achievement_emoji(achievement_id)
                    unlocked_text += f"{emoji} **{achievement['name']}**\n{achievement['description']}\n\n"
            
            embed.add_field(
                name="✅ Đã Mở Khóa",
                value=unlocked_text[:1024],  # Discord embed field limit
                inline=False
            )
        
        # Locked achievements (next few to unlock)
        locked_achievements = []
        for achievement_id, achievement in config.ACHIEVEMENTS.items():
            if achievement_id not in user_achievements:
                locked_achievements.append((achievement_id, achievement))
        
        if locked_achievements:
            locked_text = ""
            for achievement_id, achievement in locked_achievements[:5]:  # Show next 5
                emoji = get_achievement_emoji(achievement_id)
                locked_text += f"{emoji} **{achievement['name']}**\n{achievement['description']}\n\n"
            
            embed.add_field(
                name="🔒 Chưa Mở Khóa",
                value=locked_text[:1024],
                inline=False
            )
        
        # Try to create achievement showcase image
        try:
            if user_achievements:
                achievement_image = await self.achievement_generator.create_achievement_showcase(
                    target_member, user_achievements, config.ACHIEVEMENTS
                )
                
                file = discord.File(achievement_image, filename="achievements.png")
                embed.set_image(url="attachment://achievements.png")
                await ctx.send(file=file, embed=embed)
            else:
                await ctx.send(embed=embed)
                
        except Exception as e:
            # Fallback to embed only
            await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="setlevel", description="Chỉnh sửa level của người dùng")
    @commands.has_permissions(administrator=True)
    async def set_level_command(self, ctx: commands.Context, member: discord.Member, level: int):
        """Set user's level (Admin only)"""
        if level < 1 or level > 1000:
            embed = discord.Embed(
                title="❌ Lỗi",
                description="Level phải từ 1 đến 1000!",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        if member.bot:
            embed = discord.Embed(
                title="❌ Lỗi",
                description="Không thể chỉnh sửa level của bot!",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # Calculate total XP for the level
        target_total_xp = self.db.xp_for_level(level)
        current_stats = self.db.get_user_stats(member.id, ctx.guild.id)
        
        # Update database directly
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE leveling_stats 
                SET level = ?, total_xp = ?, xp = 0
                WHERE user_id = ? AND guild_id = ?
            ''', (level, target_total_xp, member.id, ctx.guild.id))
            conn.commit()
        
        embed = discord.Embed(
            title="✅ Thành Công",
            description=f"Đã chỉnh sửa level của {member.mention} thành **{level}**!",
            color=discord.Color.green()
        )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="addxp", description="Thêm XP cho người dùng")
    @commands.has_permissions(administrator=True) 
    async def add_xp_command(self, ctx: commands.Context, member: discord.Member, xp: int):
        """Add XP to user (Admin only)"""
        if xp <= 0 or xp > 1000000:
            embed = discord.Embed(
                title="❌ Lỗi",
                description="XP phải từ 1 đến 1,000,000!",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        if member.bot:
            embed = discord.Embed(
                title="❌ Lỗi", 
                description="Không thể thêm XP cho bot!",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # Add XP
        result = self.db.add_xp(member.id, ctx.guild.id, xp, 'admin')
        
        embed = discord.Embed(
            title="✅ Thành Công",
            description=f"Đã thêm **{xp:,} XP** cho {member.mention}!",
            color=discord.Color.green()
        )
        
        if result['leveled_up']:
            embed.add_field(
                name="🎉 Level Up!",
                value=f"Cấp độ: {result['old_level']} → **{result['new_level']}**",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="levelconfig", description="Cấu hình hệ thống level")
    @commands.has_permissions(administrator=True)
    async def level_config_command(self, ctx: commands.Context, setting: str = None, *, value: str = None):
        """Configure leveling system (Admin only)"""
        if not setting:
            # Show current config
            config_data = self.db.get_guild_config(ctx.guild.id)
            
            embed = discord.Embed(
                title="⚙️ Cấu Hình Hệ Thống Level",
                color=discord.Color.blue()
            )
            
            # Level up channel
            channel_id = config_data.get('level_up_channel')
            channel = ctx.guild.get_channel(channel_id) if channel_id else None
            embed.add_field(
                name="📢 Kênh Thông Báo Level Up",
                value=channel.mention if channel else "Không thiết lập",
                inline=False
            )
            
            # Announcements enabled
            enabled = config_data.get('announcement_enabled', True)
            embed.add_field(
                name="🔔 Thông Báo Level Up",
                value="Bật" if enabled else "Tắt",
                inline=True
            )
            
            # XP channels
            xp_channels = config_data.get('xp_channels', [])
            if xp_channels:
                channels = [ctx.guild.get_channel(ch_id) for ch_id in xp_channels]
                channels = [ch.mention for ch in channels if ch]
                embed.add_field(
                    name="💬 Kênh Nhận XP",
                    value=", ".join(channels) if channels else "Không có",
                    inline=False
                )
            
            # Commands
            embed.add_field(
                name="📝 Lệnh Cấu Hình",
                value="""
`levelconfig channel <#channel>` - Thiết lập kênh thông báo
`levelconfig announcements <on/off>` - Bật/tắt thông báo
`levelconfig xpchannels add <#channel>` - Thêm kênh nhận XP
`levelconfig xpchannels remove <#channel>` - Xóa kênh nhận XP
`levelconfig xpchannels clear` - Xóa tất cả (tất cả kênh nhận XP)
                """,
                inline=False
            )
            
            return await ctx.send(embed=embed)
        
        # Handle specific settings
        setting = setting.lower()
        
        if setting == "channel":
            if not value:
                return await ctx.send("❌ Vui lòng mention một kênh!")
            
            try:
                channel_id = int(value.strip("<>#"))
                channel = ctx.guild.get_channel(channel_id)
                
                if not channel or not isinstance(channel, discord.TextChannel):
                    return await ctx.send("❌ Kênh không hợp lệ!")
                
                config_data = self.db.get_guild_config(ctx.guild.id)
                config_data['level_up_channel'] = channel.id
                self.db.update_guild_config(ctx.guild.id, config_data)
                
                embed = discord.Embed(
                    title="✅ Thành Công",
                    description=f"Đã thiết lập kênh thông báo level up: {channel.mention}",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)
                
            except ValueError:
                await ctx.send("❌ ID kênh không hợp lệ!")
        
        elif setting == "announcements":
            if not value or value.lower() not in ["on", "off", "bật", "tắt"]:
                return await ctx.send("❌ Sử dụng: `on/off` hoặc `bật/tắt`")
            
            enabled = value.lower() in ["on", "bật"]
            
            config_data = self.db.get_guild_config(ctx.guild.id)
            config_data['announcement_enabled'] = enabled
            self.db.update_guild_config(ctx.guild.id, config_data)
            
            status = "bật" if enabled else "tắt"
            embed = discord.Embed(
                title="✅ Thành Công",
                description=f"Đã {status} thông báo level up!",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        
        elif setting == "xpchannels":
            if not value:
                return await ctx.send("❌ Sử dụng: `add <#channel>`, `remove <#channel>`, hoặc `clear`")
            
            parts = value.split()
            action = parts[0].lower()
            
            config_data = self.db.get_guild_config(ctx.guild.id)
            xp_channels = config_data.get('xp_channels', [])
            
            if action == "add" and len(parts) > 1:
                try:
                    channel_id = int(parts[1].strip("<>#"))
                    channel = ctx.guild.get_channel(channel_id)
                    
                    if not channel:
                        return await ctx.send("❌ Kênh không tồn tại!")
                    
                    if channel_id not in xp_channels:
                        xp_channels.append(channel_id)
                        config_data['xp_channels'] = xp_channels
                        self.db.update_guild_config(ctx.guild.id, config_data)
                        
                        embed = discord.Embed(
                            title="✅ Thành Công",
                            description=f"Đã thêm {channel.mention} vào danh sách kênh nhận XP!",
                            color=discord.Color.green()
                        )
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send("❌ Kênh đã có trong danh sách!")
                        
                except ValueError:
                    await ctx.send("❌ ID kênh không hợp lệ!")
            
            elif action == "remove" and len(parts) > 1:
                try:
                    channel_id = int(parts[1].strip("<>#"))
                    
                    if channel_id in xp_channels:
                        xp_channels.remove(channel_id)
                        config_data['xp_channels'] = xp_channels
                        self.db.update_guild_config(ctx.guild.id, config_data)
                        
                        channel = ctx.guild.get_channel(channel_id)
                        channel_name = channel.mention if channel else f"<#{channel_id}>"
                        
                        embed = discord.Embed(
                            title="✅ Thành Công", 
                            description=f"Đã xóa {channel_name} khỏi danh sách kênh nhận XP!",
                            color=discord.Color.green()
                        )
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send("❌ Kênh không có trong danh sách!")
                        
                except ValueError:
                    await ctx.send("❌ ID kênh không hợp lệ!")
            
            elif action == "clear":
                config_data['xp_channels'] = []
                self.db.update_guild_config(ctx.guild.id, config_data)
                
                embed = discord.Embed(
                    title="✅ Thành Công",
                    description="Đã xóa tất cả kênh nhận XP! (Bây giờ tất cả kênh đều nhận XP)",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)
            
            else:
                await ctx.send("❌ Sử dụng: `add <#channel>`, `remove <#channel>`, hoặc `clear`")
        
        else:
            await ctx.send(f"❌ Cài đặt không hợp lệ: `{setting}`")
    
    # Error handlers
    @set_level_command.error
    @add_xp_command.error
    @level_config_command.error
    async def admin_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="❌ Không Có Quyền",
                description="Bạn cần quyền Administrator để sử dụng lệnh này!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.hybrid_command(name="profileconfig", description="Tùy chỉnh profile của bạn")
    async def profile_config_command(self, ctx: commands.Context, setting: str = None, *, value: str = None):
        """Customize user profile"""
        if not setting:
            embed = discord.Embed(
                title="🎨 Tùy Chỉnh Profile",
                description="Các lệnh tùy chỉnh profile có sẵn:",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📝 Lệnh Tùy Chỉnh",
                value="""
`profileconfig background <url>` - Đặt ảnh nền tùy chỉnh (URL)
`profileconfig color <#hex>` - Đặt màu tùy chỉnh (mã hex)
`profileconfig reset` - Reset về mặc định
`profileconfig view` - Xem cấu hình hiện tại
                """,
                inline=False
            )
            
            embed.add_field(
                name="📌 Lưu Ý",
                value="""
• URL ảnh nền phải bắt đầu bằng http/https
• Mã màu hex phải có format #RRGGBB (ví dụ: #FF5733)
• Ảnh nền sẽ được làm mờ và tối để văn bản dễ đọc
                """,
                inline=False
            )
            
            return await ctx.send(embed=embed)
        
        setting = setting.lower()
        
        if setting == "background" or setting == "bg":
            if not value:
                return await ctx.send("❌ Vui lòng cung cấp URL ảnh nền!")
            
            # Validate URL
            if not (value.startswith('http://') or value.startswith('https://')):
                return await ctx.send("❌ URL phải bắt đầu bằng http:// hoặc https://")
            
            # Check if URL is valid image
            try:
                from .utils import download_image
                test_img = await download_image(value)
                if not test_img:
                    return await ctx.send("❌ Không thể tải ảnh từ URL này!")
            except Exception:
                return await ctx.send("❌ URL ảnh không hợp lệ!")
            
            # Update background
            self.db.update_user_customization(ctx.author.id, ctx.guild.id, custom_bg=value)
            
            embed = discord.Embed(
                title="✅ Thành Công",
                description=f"Đã đặt ảnh nền profile: [Xem ảnh]({value})",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=value)
            await ctx.send(embed=embed)
        
        elif setting == "color" or setting == "colour":
            if not value:
                return await ctx.send("❌ Vui lòng cung cấp mã màu hex! (ví dụ: #FF5733)")
            
            # Validate hex color
            if not value.startswith('#') or len(value) != 7:
                return await ctx.send("❌ Mã màu phải có định dạng #RRGGBB (ví dụ: #FF5733)")
            
            try:
                # Test if valid hex
                int(value[1:], 16)
            except ValueError:
                return await ctx.send("❌ Mã màu hex không hợp lệ!")
            
            # Update color
            self.db.update_user_customization(ctx.author.id, ctx.guild.id, custom_color=value)
            
            # Convert hex to RGB for embed color
            rgb = tuple(int(value[1:][i:i+2], 16) for i in (0, 2, 4))
            
            embed = discord.Embed(
                title="✅ Thành Công",
                description=f"Đã đặt màu profile: `{value.upper()}`",
                color=discord.Color.from_rgb(*rgb)
            )
            await ctx.send(embed=embed)
        
        elif setting == "reset":
            # Reset customization
            self.db.update_user_customization(ctx.author.id, ctx.guild.id, custom_bg=None, custom_color=None)
            
            embed = discord.Embed(
                title="✅ Reset Thành Công",
                description="Đã reset tùy chỉnh profile về mặc định!",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        
        elif setting == "view":
            # Show current customization
            stats = self.db.get_user_stats(ctx.author.id, ctx.guild.id)
            
            embed = discord.Embed(
                title=f"🎨 Tùy Chỉnh Profile - {ctx.author.display_name}",
                color=discord.Color.blue()
            )
            
            bg_text = stats.get('custom_bg', 'Mặc định (dựa theo level)')
            if stats.get('custom_bg'):
                embed.set_thumbnail(url=stats['custom_bg'])
                bg_text = f"[Ảnh tùy chỉnh]({stats['custom_bg']})"
            
            color_text = stats.get('custom_color', 'Mặc định (dựa theo level)')
            if stats.get('custom_color'):
                # Convert hex to RGB for embed color
                rgb = tuple(int(stats['custom_color'][1:][i:i+2], 16) for i in (0, 2, 4))
                embed.color = discord.Color.from_rgb(*rgb)
                color_text = f"`{stats['custom_color'].upper()}`"
            
            embed.add_field(name="🖼️ Ảnh Nền", value=bg_text, inline=True)
            embed.add_field(name="🎨 Màu Sắc", value=color_text, inline=True)
            
            await ctx.send(embed=embed)
        
        else:
            await ctx.send("❌ Cài đặt không hợp lệ! Sử dụng `profileconfig` để xem hướng dẫn.")

async def setup(bot: commands.Bot):
    """Setup function for the cog"""
    await bot.add_cog(LevelingCommands(bot))