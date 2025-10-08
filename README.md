# Discord Bot - Multi-Guild Support

## 🚀 Tính năng mới

Bot đã được nâng cấp để hỗ trợ nhiều máy chủ Discord với các tính năng sau:

### ✨ Các cải tiến chính

1. **Database riêng cho mỗi server** 
   - Mỗi server có database SQLite riêng biệt
   - Dữ liệu giữa các server không ảnh hưởng lẫn nhau
   - Tự động tạo database khi bot join server mới

2. **Connection Pooling**
   - Quản lý kết nối database hiệu quả
   - Tối đa 20 connections đồng thời cho mỗi server
   - Tự động cleanup connections không sử dụng

3. **Caching System**
   - Cache thông tin người dùng để tăng tốc độ
   - Cache leaderboard với TTL 5 phút
   - Tự động clear cache khi có thay đổi

4. **Async Operations**
   - Tất cả database operations đều async
   - Không block main thread
   - Xử lý nhiều commands đồng thời

5. **Transaction Logging**
   - Ghi log tất cả giao dịch tiền
   - Theo dõi lịch sử chuyển tiền
   - Hỗ trợ audit và rollback

## 📦 Cài đặt

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Cấu hình bot

Sửa file `config.py`:

```python
TOKEN = "YOUR_BOT_TOKEN_HERE"  # Thay bằng token bot của bạn
BOT_OWNER_IDS = [YOUR_ID]  # Thay bằng Discord ID của bạn
```

### 3. Migration dữ liệu cũ (nếu có)

Nếu bạn đang sử dụng phiên bản cũ với database đơn:

```bash
python migrate_data.py
```

Script này sẽ:
- Chuyển dữ liệu từ `economy.db` sang database mới
- Backup database cũ thành `economy_backup.db`
- Tạo database riêng cho mỗi server

### 4. Chạy bot

```bash
python main.py
```

## 🏗️ Cấu trúc Database

```
databases/
├── guild_123456789.db  # Database cho server ID 123456789
├── guild_987654321.db  # Database cho server ID 987654321
└── ...
```

Mỗi database chứa các bảng:
- `users` - Thông tin người dùng
- `guild_settings` - Cài đặt server
- `transactions` - Lịch sử giao dịch
- `giveaways` - Thông tin giveaway

## 🔧 API Helper Functions

### UserDatabase

```python
from utils.db_helpers import UserDatabase

# Kiểm tra đăng ký
is_registered = await UserDatabase.is_registered(guild_id, user_id)

# Đăng ký user mới
success = await UserDatabase.register_user(guild_id, user_id, initial_balance=200000)

# Lấy balance
balance = await UserDatabase.get_balance(guild_id, user_id)

# Thêm/trừ tiền
await UserDatabase.add_balance(guild_id, user_id, amount)
await UserDatabase.subtract_balance(guild_id, user_id, amount)

# Chuyển tiền
success = await UserDatabase.transfer_money(guild_id, from_user_id, to_user_id, amount)
```

### GuildDatabase

```python
from utils.db_helpers import GuildDatabase

# Lấy/set setting
value = await GuildDatabase.get_setting(guild_id, "prefix", default="z")
await GuildDatabase.set_setting(guild_id, "prefix", "!")

# Lấy top users
top_users = await GuildDatabase.get_top_users(guild_id, limit=10, field="balance")

# Reset tất cả balance
await GuildDatabase.reset_all_balances(guild_id)
```

### LeaderboardDatabase

```python
from utils.db_helpers import LeaderboardDatabase

# Lấy leaderboard
leaderboard = await LeaderboardDatabase.get_balance_leaderboard(guild_id, limit=10)

# Lấy rank của user
rank = await LeaderboardDatabase.get_user_rank(guild_id, user_id, field="balance")
```

## 📊 Performance Optimizations

1. **WAL Mode** - Write-Ahead Logging cho better concurrency
2. **Connection Pooling** - Reuse connections thay vì tạo mới
3. **Async I/O** - Non-blocking database operations
4. **Caching** - In-memory cache cho frequently accessed data
5. **Indexes** - Database indexes cho faster queries

## 🛡️ Security Features

1. **SQL Injection Protection** - Sử dụng parameterized queries
2. **Rate Limiting** - Giới hạn số commands per user
3. **Permission Checks** - Kiểm tra quyền cho admin commands
4. **Transaction Atomicity** - Đảm bảo tính toàn vẹn của giao dịch

## 🐛 Troubleshooting

### Bot không lưu dữ liệu
- Kiểm tra folder `databases/` có quyền write
- Xem logs để check database errors

### Commands chạy chậm
- Clear cache: Restart bot
- Check database size: Large databases có thể cần optimize
- Enable DEBUG mode trong config.py

### Migration thất bại
- Backup database cũ trước khi migrate
- Check logs trong `migrate_data.py`
- Manual recovery từ backup nếu cần

## 📝 Changelog

### Version 2.0.0 - Multi-Guild Support
- ✅ Separate database per guild
- ✅ Connection pooling
- ✅ Async database operations
- ✅ Transaction logging
- ✅ Caching system
- ✅ Migration tool
- ✅ Performance optimizations

## 🤝 Contributing

Nếu bạn muốn đóng góp:

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

MIT License - See LICENSE file for details

## 👨‍💻 Author

Developed by ThanhViDev with multi-guild support enhancements

---

**Note**: Nhớ backup database trước khi update lên version mới!
