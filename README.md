# Telegram X Photo Bot (Web Service)

Bot này tự động lấy ảnh mới nhất từ các người dùng X (Twitter) và đăng lên channel Telegram.

## Triển khai trên Render

1. Tạo repository trên GitHub và đẩy các file này lên.
2. Truy cập [Render](https://render.com):
   - Nhấp **New** > **Web Service**.
   - Kết nối repository GitHub.
   - Cấu hình:
     - **Name**: `x-photo-bot`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python app.py`
3. Thêm biến môi trường:
   - `BOT_TOKEN`: Token từ `@BotFather`.
   - `CHAT_ID`: Chat ID của channel Telegram.
4. Nhấp **Create Web Service** để triển khai.

## Lưu ý
- Bot dùng Selenium để lấy ảnh từ X, kiểm tra mỗi 5 phút.
- Web Service miễn phí sẽ ngủ sau 15 phút không hoạt động. Dùng UptimeRobot để giữ bot chạy.
