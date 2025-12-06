import os
import time
import json
import logging
import feedparser
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime
from xhs_card_maker import XhsCardMaker
from tg_poster import send_photo_to_channel

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    logging.warning("⚠️ 未配置 GEMINI_API_KEY")
else:
    genai.configure(api_key=API_KEY)

HISTORY_FILE = "real_content_farm/history.json"

class AutoContentFarm:
    def __init__(self):
        self.processed_links = self.load_history()
        self.rss_url = os.getenv("RSS_SOURCE", "https://news.ycombinator.com/rss")
        self.card_maker = XhsCardMaker()
        try:
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        except:
            self.model = genai.GenerativeModel('gemini-pro')

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r') as f:
                    return set(json.load(f))
            except:
                return set()
        return set()

    def save_history(self):
        with open(HISTORY_FILE, 'w') as f:
            json.dump(list(self.processed_links), f)

    def fetch_feed(self):
        logging.info(f"正在扫描 RSS: {self.rss_url}")
        try:
            feed = feedparser.parse(self.rss_url)
            return feed.entries
        except Exception as e:
            logging.error(f"RSS 抓取失败: {e}")
            return []

    def generate_article(self, entry):
        if entry.link in self.processed_links:
            return False

        logging.info(f"发现新热点: {entry.title}")
        
        if not API_KEY:
            return False

        try:
            prompt = f"Rewrite this tech news into an engaging English blog post. Also, provide a one-line summary at the very top (for the cover image).\nNews Title: {entry.title}\nLink: {entry.link}"
            response = self.model.generate_content(prompt)
            content = response.text
            lines = content.split('\n')
            summary = lines[0].replace('#', '').strip() if lines else entry.title
        except Exception as e:
            logging.error(f"AI 生成失败: {e}")
            return False

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 生成海报
        image_path = None
        try:
            image_path = self.card_maker.create_card(entry.title, summary, timestamp)
            logging.info(f"✅ 海报已生成至: {image_path}")
        except Exception as e:
            logging.error(f"❌ 海报生成失败: {e}")

        # 发布到 Telegram
        if image_path and os.getenv("TELEGRAM_CHANNEL_ID"):
            tg_caption = f"*{entry.title}*\n\n{summary}\n\n[🔗 Read More]({entry.link})\n\n#AI #TechNews #Innovation"
            send_photo_to_channel(image_path, tg_caption)
        
        self.processed_links.add(entry.link)
        self.save_history()
        return True

    def run_once(self):
        logging.info("=== Serverless Task Start ===")
        entries = self.fetch_feed()
        processed_count = 0
        for entry in entries:
            if entry.link not in self.processed_links:
                if self.generate_article(entry):
                    processed_count += 1
                    break # 每小时只发一条
        
        if processed_count == 0:
            logging.info("暂无新内容。")

if __name__ == "__main__":
    agent = AutoContentFarm()
    agent.run_once()
