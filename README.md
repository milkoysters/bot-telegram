# Telegram X Photo Bot (Background Worker)

Bot này tự động lấy ảnh mới nhất từ các người dùng X (Twitter) và đăng lên channel Telegram.

## Triển khai trên Render

1. Tạo repository trên GitHub và đẩy các file này lên.
2. Truy cập [Render](https://render.com):
   - Nhấp **New** > **Background Worker**.
   - Kết nối repository GitHub.
   - Cấu hình:
     - **Name**: `x-photo-bot`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python app.py`
3. Thêm biến môi trường:
   - `BOT_TOKEN`: Token từ `@BotFather`.
   - `CHAT_ID`: Chat ID của channel Telegram.
4. Nhấp **Create Background Worker** để triển khai.

## Lưu ý
- Bot kiểm tra ảnh mới mỗi 5 phút.
- File `processed_images.txt` sẽ bị xóa khi Render khởi động lại.
