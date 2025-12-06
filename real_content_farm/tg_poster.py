import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv("real_content_farm/.env")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

def send_photo_to_channel(image_path, caption):
    """发送带图片的图文消息"""
    if not BOT_TOKEN or not CHANNEL_ID:
        logging.error("❌ 无法发送：缺少 TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHANNEL_ID")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    
    try:
        with open(image_path, 'rb') as img_file:
            files = {'photo': img_file}
            data = {
                'chat_id': CHANNEL_ID,
                'caption': caption,
                'parse_mode': 'Markdown'
            }
            response = requests.post(url, files=files, data=data)
            
            if response.status_code == 200:
                logging.info(f"✅ Telegram 发布成功！")
                return True
            else:
                logging.error(f"❌ Telegram 发布失败: {response.text}")
                return False
    except Exception as e:
        logging.error(f"❌ 网络错误: {e}")
        return False
