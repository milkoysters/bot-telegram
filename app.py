import time
import os
from flask import Flask
import logging
from threading import Thread
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
import requests

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Khởi tạo Flask app
app = Flask(__name__)

# Lấy thông tin từ biến môi trường
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Danh sách người dùng X và caption riêng
X_USERS = {
    "littlekycap": "Ảnh mới từ Milk Oysters",
    "milkoysters": "Hình ảnh độc quyền từ User2",
    "nyanchan2k3": "Cập nhật ảnh từ User3"
}

PROCESSED_FILE = "processed_images.txt"

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
    
    # Cấu hình Selenium
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = None
    try:
        logger.info("Khởi tạo Chrome driver...")
        driver = webdriver.Chrome(options=chrome_options)
        logger.info("Chrome driver khởi tạo thành công")
    except WebDriverException as e:
        logger.error(f"Lỗi khởi tạo Chrome driver: {e}")
        return
    
    for user, caption in X_USERS.items():
        try:
            url = f"https://twitter.com/{user}"
            logger.info(f"Đang truy cập {url}")
            driver.get(url)
            
            # Chờ tweet xuất hiện (tối đa 20 giây)
            logger.info(f"Đang chờ tweet từ {user}...")
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='tweet']"))
            )
            
            # Tìm các bài viết
            tweets = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='tweet']")
            if not tweets:
                logger.info(f"Không tìm thấy bài viết từ {user}")
                continue

            for tweet in tweets:
                # Kiểm tra retweet
                is_retweet = len(tweet.find_elements(By.XPATH, ".//*[contains(text(), 'Retweeted')]")) > 0 or "RT @" in tweet.text
                if is_retweet:
                    continue

                # Tìm ảnh
                images = tweet.find_elements(By.CSS_SELECTOR, "img[src*='media']")
                if images:
                    latest_image = images[0].get_attribute("src")
                    if not latest_image.startswith("http"):
                        latest_image = "https:" + latest_image

                    if latest_image not in processed_images:
                        if send_photo_to_telegram(latest_image, caption):
                            save_processed_image(latest_image)
                            processed_images.add(latest_image)
                        break
                    else:
                        logger.info(f"Ảnh mới nhất từ {user} đã được xử lý: {latest_image}")
                        break
                else:
                    logger.info(f"Không tìm thấy ảnh trong bài viết từ {user}")

        except Exception as e:
            logger.error(f"Lỗi khi lấy ảnh từ {user}: {e}")
    
    if driver:
        driver.quit()

def run_bot():
    logger.info("Bắt đầu vòng lặp bot...")
    while True:
        fetch_latest_photos_from_x()
        time.sleep(300)

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
