# 🎯 Hệ Thống Leveling - Discord Bot

Hệ thống cấp độ hoàn chỉnh cho Discord bot với đầy đủ tính năng theo yêu cầu.

## 📋 Tính Năng

### 🔥 Core Features
- ✅ **Theo dõi kinh nghiệm (XP)** từ tin nhắn và voice chat
- ✅ **Hệ thống cấp độ** với công thức tăng dần
- ✅ **Profile cards** với hình ảnh đẹp mắt
- ✅ **Rank cards** hiển thị nhanh
- ✅ **Thành tựu (Achievements)** đa dạng
- ✅ **Bảng xếp hạng (Leaderboard)** theo nhiều tiêu chí
- ✅ **Thông báo level up** tự động
- ✅ **Multiplier XP** cho VIP và Boost members
- ✅ **Cấu hình server** linh hoạt

### 🎨 Visual Features
- 🖼️ **Profile cards** với avatar, thanh tiến độ, thống kê
- 🏆 **Achievement showcase** với hình ảnh đẹp
- 📊 **Rank cards** nhỏ gọn
- 🎨 **Custom backgrounds** và colors
- 📈 **Progress bars** trực quan

### ⚙️ Admin Features
- 🔧 **Cấu hình server** đầy đủ
- 👑 **Chỉnh sửa level** người dùng
- ➕ **Thêm XP** thủ công
- 📢 **Thiết lập kênh thông báo**
- 🚫 **Tắt/bật XP** cho kênh cụ thể

## 🛠️ Cài Đặt

Hệ thống đã được tích hợp sẵn vào bot. Chỉ cần:

1. **Cơ sở dữ liệu** sẽ tự động tạo các bảng cần thiết
2. **Module leveling** đã được thêm vào `main.py`
3. **Dependencies** đã được cài đặt

## 📝 Lệnh Sử Dụng

### 👥 User Commands

#### `zprofile [@user]`
Xem profile level đầy đủ với hình ảnh đẹp
```
zprofile
zprofile @username
```

#### `zrank [@user]`
Xem rank card nhỏ gọn
```
zrank
zrank @username
```

#### `zleaderboard [sort]`
Xem bảng xếp hạng server
```
zlb
zlb level
zlb xp
zlb messages
zlb voice
```

#### `zachievements [@user]`
Xem thành tựu đã mở khóa
```
zachievements
zachievements @username
```

### 👑 Admin Commands

#### `zlevelconfig`
Xem cấu hình hiện tại
```
zlevelconfig
```

#### `zlevelconfig channel <#channel>`
Thiết lập kênh thông báo level up
```
zlevelconfig channel #general
```

#### `zlevelconfig announcements <on/off>`
Bật/tắt thông báo level up
```
zlevelconfig announcements on
zlevelconfig announcements off
```

#### `zlevelconfig xpchannels <action>`
Quản lý kênh nhận XP
```
zlevelconfig xpchannels add #chat
zlevelconfig xpchannels remove #chat
zlevelconfig xpchannels clear
```

#### `zsetlevel <@user> <level>`
Chỉnh sửa level người dùng
```
zsetlevel @username 10
```

#### `zaddxp <@user> <xp>`
Thêm XP cho người dùng
```
zaddxp @username 500
```

## 🏆 Hệ Thống Thành Tựu

### 📝 Message Achievements
- **Tin Nhắn Đầu Tiên** - Gửi tin nhắn đầu tiên (50 XP)
- **Người Nói Nhiều** - Gửi 100 tin nhắn (200 XP)
- **Bướm Xã Hội** - Gửi 1000 tin nhắn (1000 XP)
- **Hoạt Động Hàng Ngày** - Gửi 10+ tin nhắn/ngày (100 XP)

### 🎤 Voice Achievements
- **Người Mới Tham Gia Voice** - 30 phút voice (100 XP)
- **Người Đam Mê Voice** - 5 giờ voice (500 XP)
- **Huyền Thoại Voice** - 24 giờ voice (2000 XP)

### ⭐ Level Achievements
- **Cấp Độ 5** - Đạt level 5 (250 XP)
- **Cấp Độ 10** - Đạt level 10 (500 XP)
- **Cấp Độ 25** - Đạt level 25 (1250 XP)
- **Cấp Độ 50** - Đạt level 50 (2500 XP)

## ⚡ Hệ Thống XP

### 💬 Message XP
- **Base XP**: 10-25 XP/tin nhắn (random)
- **Cooldown**: 60 giây giữa các tin nhắn
- **Daily tracking**: Theo dõi tin nhắn hàng ngày

### 🎤 Voice XP
- **Base XP**: 10 XP/phút
- **Real-time tracking**: Cập nhật mỗi phút
- **AFK detection**: Không tính XP khi AFK

### 🔥 Multipliers
- **VIP roles**: 1.5x XP (role chứa: vip, premium, supporter, donator)
- **Server boost**: 2.0x XP
- **Stack**: Multipliers có thể cộng dồn

### 📊 Level Formula
```
Level 1 -> 2: 100 XP
Level 2 -> 3: 120 XP (100 * 1.2^1)
Level 3 -> 4: 144 XP (100 * 1.2^2)
...
Level n -> n+1: 100 * 1.2^(n-1) XP
```

## 🗃️ Database Schema

### `leveling_stats`
Thống kê người dùng:
- `user_id`, `guild_id` - Khóa chính
- `level`, `xp`, `total_xp` - Cấp độ và kinh nghiệm
- `messages`, `voice_minutes` - Hoạt động
- `achievements` - Thành tựu (JSON array)
- `custom_bg`, `custom_color` - Tùy chỉnh profile
- `daily_messages`, `last_daily_reset` - Theo dõi hàng ngày

### `user_achievements`
Chi tiết thành tựu:
- `user_id`, `guild_id`, `achievement_id` - Khóa chính
- `unlocked_at` - Thời gian mở khóa

### `leveling_config`
Cấu hình server:
- `guild_id` - Khóa chính
- `level_up_channel` - Kênh thông báo
- `xp_channels` - Kênh nhận XP (JSON array)
- `disabled_channels` - Kênh bị tắt XP (JSON array)
- `level_roles` - Role theo level (JSON object)
- `announcement_enabled` - Bật/tắt thông báo
- `custom_message` - Tin nhắn tùy chỉnh

## 🎨 Customization

### Profile Backgrounds
- Upload URL hình ảnh làm background
- Tự động blur và overlay để đảm bảo text hiển thị tốt
- Fallback về gradient mặc định

### Colors
- Hex color codes (#FF0000)
- Màu mặc định dựa theo level:
  - Level 1-4: Cornflower blue
  - Level 5-9: Lime green
  - Level 10-24: Bronze
  - Level 25-49: Silver
  - Level 50+: Gold

## 🔧 Configuration

### Environment Variables
```env
# Trong file .env hoặc environment
BOT_TOKEN=your_bot_token
BOT_PREFIX=z
BOT_OWNER_IDS=123456789,987654321
```

### Leveling Config (config.py)
```python
LEVELING_CONFIG = {
    'exp_per_message': 15,
    'exp_per_message_range': [10, 25],
    'exp_per_minute_voice': 10,
    'vip_multiplier': 1.5,
    'boost_multiplier': 2.0,
    'message_cooldown': 60,
    'voice_update_interval': 60,
}
```

## 🚀 Advanced Features

### Voice Tracking
- Real-time tracking khi user join/leave voice
- Background task update XP mỗi phút
- AFK channel detection
- Persistent tracking qua reconnect

### Achievement System
- Dynamic requirement checking
- XP rewards for achievements
- Visual showcase với images
- Extensible configuration

### Image Generation
- PIL-based card generation
- Circular avatar cropping
- Progress bars và gradients
- Custom fonts và colors
- Error fallback to text embeds

### Performance
- Connection pooling
- Efficient database queries
- Background task optimization
- Memory management cho voice tracking
- Cooldown system để tránh spam

## 📊 Monitoring

### Owner Commands
```
zlevelstatus - Xem trạng thái hệ thống (owner only)
```

### Logs
Hệ thống tự động log:
- Extension loading/unloading
- Database operations
- Error handling
- Performance metrics

## 🛠️ Troubleshooting

### Common Issues

1. **Database errors**
   ```python
   # Recreate tables nếu bị lỗi
   from Leveling.database import LevelingDatabase
   db = LevelingDatabase()
   ```

2. **Image generation fails**
   - Fallback tự động về text embed
   - Check PIL và font dependencies
   - Verify internet connection cho avatar

3. **Voice tracking không hoạt động**
   - Check voice_states intent
   - Verify bot permissions trong voice channels
   - Check background task status

4. **XP không được tính**
   - Check channel permissions
   - Verify XP channel configuration
   - Check user cooldowns

## 📈 Future Enhancements

- [ ] Level roles tự động
- [ ] Weekly/monthly leaderboards
- [ ] More achievement types
- [ ] Export/import user data
- [ ] Advanced statistics
- [ ] Seasonal events
- [ ] Custom XP formulas per server
- [ ] Integration with economy system

## 📞 Support

Hệ thống đã được tối ưu và test kỹ lưỡng. Nếu có vấn đề:

1. Check logs trong console
2. Verify database tables tồn tại
3. Check bot permissions
4. Test với `zlevelstatus` command

---

**Phiên bản**: 1.0.0  
**Tác giả**: AI Assistant  
**Tương thích**: Discord.py 2.3.0+, Python 3.8+