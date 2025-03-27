import time
import os
import requests
from bs4 import BeautifulSoup
import logging
from threading import Thread
from flask import Flask

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Khởi tạo Flask app
app = Flask(__name__)

# Lấy thông tin từ biến môi trường
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Danh sách người dùng X và caption
X_USERS = {
    "littlekycap": "Ảnh mới từ Milk Oysters",
    "milkoysters": "Hình ảnh độc quyền từ User2",
    "nyanchan2k3": "Cập nhật ảnh từ User3"
}

PROCESSED_FILE = "processed_images.txt"

# Headers giả lập trình duyệt
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

# Danh sách nguồn dữ liệu thay thế
SOURCES = [
    {"base_url": "https://nitter.net", "tweet_selector": ".timeline-item", "retweet_check": "span.retweet-header", "img_selector": "img[src*='media']"},
    {"base_url": "https://nitter.lacontrevoie.fr", "tweet_selector": ".timeline-item", "retweet_check": "span.retweet-header", "img_selector": "img[src*='media']"},
    {"base_url": "https://nitter.cz", "tweet_selector": ".timeline-item", "retweet_check": "span.retweet-header", "img_selector": "img[src*='media']"},
    # Bạn có thể thêm nguồn khác nếu tìm thấy (ví dụ: twstalker.com, nhưng cần kiểm tra)
]

def send_photo_to_telegram(photo_url, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    params = {
        "chat_id": CHAT_ID,
        "photo": photo_url,
        "caption": f"{caption} (ngày {time.strftime('%Y-%m-%d %H:%M:%S')})"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            logger.info(f"Đã gửi ảnh: {photo_url}")
            return True
        else:
            logger.error(f"Lỗi khi gửi ảnh: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Lỗi gửi ảnh lên Telegram: {e}")
        return False

def load_processed_images():
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, "r") as file:
            return set(line.strip() for line in file)
    return set()

def save_processed_image(photo_url):
    with open(PROCESSED_FILE, "a") as file:
        file.write(f"{photo_url}\n")

def fetch_latest_photos_from_x():
    processed_images = load_processed_images()
    
    for user, caption in X_USERS.items():
        for source in SOURCES:
            base_url = source["base_url"]
            tweet_selector = source["tweet_selector"]
            retweet_check = source["retweet_check"]
            img_selector = source["img_selector"]
            
            try:
                url = f"{base_url}/{user}"
                logger.info(f"Đang truy cập {url}")
                response = requests.get(url, headers=HEADERS, timeout=15)
                
                if response.status_code != 200:
                    logger.warning(f"Không thể truy cập {user} trên {base_url}: {response.status_code}")
                    continue

                soup = BeautifulSoup(response.text, "html.parser")
                tweets = soup.select(tweet_selector)
                if not tweets:
                    logger.info(f"Không tìm thấy bài viết từ {user} trên {base_url}")
                    continue

                for tweet in tweets:
                    if tweet.find("span", class_=retweet_check):
                        continue  # Bỏ qua retweet
                    
                    images = tweet.select(img_selector)
                    if images:
                        latest_image = images[0]["src"]
                        if not latest_image.startswith("http"):
                            latest_image = base_url + latest_image
                        
                        if latest_image not in processed_images:
                            if send_photo_to_telegram(latest_image, caption):
                                save_processed_image(latest_image)
                            break
                        else:
                            logger.info(f"Ảnh mới nhất từ {user} đã được xử lý: {latest_image}")
                            break
                    else:
                        logger.info(f"Không tìm thấy ảnh trong bài viết từ {user} trên {base_url}")
                break  # Thoát vòng lặp nguồn nếu thành công

            except Exception as e:
                logger.error(f"Lỗi khi lấy ảnh từ {user} trên {base_url}: {e}")
                time.sleep(5)  # Chờ trước khi thử nguồn khác

def run_bot():
    logger.info("Bắt đầu vòng lặp bot...")
    while True:
        fetch_latest_photos_from_x()
        time.sleep(300)  # Kiểm tra mỗi 5 phút

@app.route('/')
def health_check():
    return "Bot is running", 200

if __name__ == "__main__":
    logger.info("Bot đang khởi động trên Render (Web Service)...")
    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
