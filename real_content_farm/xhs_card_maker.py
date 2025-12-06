import os
import re
import random
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = "real_content_farm/output"
IMAGES_DIR = "real_content_farm/images"

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- 极简配色方案 ---
MINIMALIST_COLORS = [
    "#1A1A1A", # 极简黑
    "#2C3E50", # 深蓝灰
    "#192a56", # 深邃蓝
    "#2d3436", # 德式灰
    "#000000", # 纯黑
]

class XhsCardMaker:
    def __init__(self):
        self.width = 1242
        self.height = 1660
        self.padding = 100 # 左右边距

    def remove_emoji(self, text):
        return re.sub(r'[^\u0000-\uFFFF]', '', text)

    def get_font(self, size):
        """获取字体"""
        font_file = os.path.join(os.path.dirname(__file__), "SimHei.ttf")
        if os.path.exists(font_file):
            return ImageFont.truetype(font_file, size)
        return ImageFont.load_default()

    def wrap_text(self, text, font, max_width):
        """智能按单词换行算法"""
        lines = []
        words = text.split()
        current_line = []
        
        for word in words:
            # 测试加入这个单词后的宽度
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            w = bbox[2] - bbox[0]
            
            if w <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        return lines

    def create_card(self, title, summary, filename_base):
        # 1. 准备素材
        title = self.remove_emoji(title).strip()
        summary = self.remove_emoji(summary).strip()
        
        bg_color = random.choice(MINIMALIST_COLORS)
        text_color = "#FFFFFF" 

        # 2. 创建画布
        img = Image.new('RGB', (self.width, self.height), color=bg_color)
        draw = ImageDraw.Draw(img)

        # --- 3. 绘制主标题 (左对齐, 智能换行) ---
        title_size = 100 # 字号调小
        title_font = self.get_font(title_size)
        
        # 计算最大允许宽度
        max_text_width = self.width - (self.padding * 2)
        
        title_lines = self.wrap_text(title, title_font, max_text_width)
        
        # 计算标题起始位置 (稍微靠上一点)
        y_text = 350
        
        for line in title_lines:
            draw.text((self.padding, y_text), line, font=title_font, fill=text_color)
            y_text += (title_size + 30) # 行间距

        # --- 4. 绘制装饰线 ---
        # 稍微留白
        y_text += 60
        draw.line((self.padding, y_text, self.padding + 150, y_text), fill="#FFD700", width=8)
        y_text += 80

        # --- 5. 绘制摘要 (左对齐) ---
        body_size = 50 # 字号调小
        body_font = self.get_font(body_size)
        
        # 限制摘要长度，防止占满屏幕
        summary_lines = self.wrap_text(summary[:200], body_font, max_text_width)
            
        for line in summary_lines:
            draw.text((self.padding, y_text), line, font=body_font, fill="#DDDDDD") # 稍微灰一点，区分层级
            y_text += (body_size + 25)

        # --- 6. 底部版权标 ---
        footer_font = self.get_font(35)
        draw.text((self.padding, self.height - 100), "AI Insider Daily", font=footer_font, fill="#888888")
        draw.text((self.width - self.padding - 300, self.height - 100), "Powered by Gemini", font=footer_font, fill="#888888")

        # 7. 保存
        save_path = os.path.join(IMAGES_DIR, f"{filename_base}.png")
        img.save(save_path)
        print(f"✅ [v3.1 英文适配版] 海报已生成: {save_path}")
        return save_path

if __name__ == "__main__":
    maker = XhsCardMaker()
    maker.create_card("Test Title", "Test Summary", "test_card")
