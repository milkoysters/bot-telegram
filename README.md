# Telegram X Photo Bot

Bot này tự động lấy ảnh mới nhất từ các người dùng X (Twitter) và đăng lên channel Telegram.

## Triển khai trên Render

1. Tạo tài khoản trên [Render](https://render.com).
2. Tạo repository trên GitHub và đẩy các file này lên.
3. Kết nối repository với Render:
   - Chọn **New** > **Web Service**.
   - Chọn repository của bạn.
   - Cấu hình:
     - **Name**: `x-photo-bot`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python app.py`
4. Thêm biến môi trường:
   - `BOT_TOKEN`: Token từ `@BotFather`.
   - `CHAT_ID`: Chat ID của channel Telegram.
5. Nhấp **Create Web Service** để triển khai.

## Lưu ý
- Bot kiểm tra ảnh mới mỗi 5 phút.
- File `processed_images.txt` sẽ bị xóa khi Render khởi động lại ứng dụng. Nếu cần lưu lâu dài, hãy liên hệ lập trình viên để tích hợp cơ sở dữ liệu.
