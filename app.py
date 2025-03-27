import requests
from bs4 import BeautifulSoup
import time
import os
from threading import Thread

# Lấy thông tin từ biến môi trường
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Danh sách người dùng X và caption riêng (bạn có thể thay đổi tại đây)
X_USERS = {
    "CRYBABY0430": "Connect w/ her: https://linktr.ee/CRYBABY_0430",
    "kyoncy_ex": "Connect w/ her:  https://linktr.ee/CRYBABY_0430",
    "salvatore90822": "Connect w/ her: https://getallmylinks.com/qiqi"
}

# File để lưu danh sách ảnh đã xử lý
PROCESSED_FILE = "processed_images.txt"

# Headers để giả lập trình duyệt
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Hàm gửi ảnh lên Telegram
def send_photo_to_telegram(photo_url, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    params = {
        "chat_id": CHAT_ID,
        "photo": photo_url,
        "caption": f"{caption} (ngày {time.strftime('%Y-%m-%d %H:%M:%S')})"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print(f"Đã gửi ảnh: {photo_url}")
        return True
    else:
        print(f"Lỗi khi gửi ảnh: {response.text}")
        return False

# Hàm đọc danh sách ảnh đã xử lý
def load_processed_images():
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, "r") as file:
            return set(line.strip() for line in file)
    return set()

# Hàm lưu ảnh đã xử lý
def save_processed_image(photo_url):
    with open(PROCESSED_FILE, "a") as file:
        file.write(f"{photo_url}\n")

# Hàm lấy ảnh mới nhất từ X, tránh repost
def fetch_latest_photos_from_x():
    processed_images = load_processed_images()
    
    for user, caption in X_USERS.items():
        try:
            url = f"https://twitter.com/{user}"
            response = requests.get(url, headers=HEADERS)
            
            if response.status_code != 200:
                print(f"Không thể truy cập {user}: {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            tweets = soup.find_all("article", {"role": "article"})
            if not tweets:
                print(f"Không tìm thấy bài viết từ {user}")
                continue

            for tweet in tweets:
                is_retweet = tweet.find("span", string=lambda x: x and "Retweet" in x) or "RT @" in tweet.text
                if is_retweet:
                    continue

                images = tweet.find_all("img", {"src": lambda x: x and "media" in x})
                if images:
                    latest_image = images[0]["src"]
                    if not latest_image.startswith("http"):
                        latest_image = "https:" + latest_image

                    if latest_image not in processed_images:
                        if send_photo_to_telegram(latest_image, caption):
                            save_processed_image(latest_image)
                            processed_images.add(latest_image)
                        break
                    else:
                        print(f"Ảnh mới nhất từ {user} đã được xử lý: {latest_image}")
                        break

        except Exception as e:
            print(f"Lỗi khi lấy ảnh từ {user}: {e}")

# Chạy bot trong luồng riêng
def run_bot():
    while True:
        fetch_latest_photos_from_x()
        time.sleep(300)  # Kiểm tra mỗi 5 phút

if __name__ == "__main__":
    print("Bot đang khởi động trên Render...")
    bot_thread = Thread(target=run_bot)
    bot_thread.start()
