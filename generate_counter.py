#!/usr/bin/env python3
# generate_counter.py
"""
Генератор counter.png:
- прозрачный фон (по умолчанию)
- левостороннее выравнивание
- векторные иконки вместо эмодзи (чтобы не было "черных квадратов")
- аккуратный перенос TAGLINE по ширине
Настраивается через переменные окружения (см. README)
"""

from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timezone
import os

# ========= Настройки (можно задавать через env в workflow) ==========
QUIT_DATE = os.environ.get("QUIT_DATE", "2025-08-15")  # YYYY-MM-DD
TITLE = os.environ.get("TITLE", "Свободен от дыма")   # эмодзи убраны, иконка рисуется отдельно
TAGLINE = os.environ.get("TAGLINE", "💻 IT, семья, здоровье — мой новый стек жизни")
OUT_DIR = "public"
OUT_FILE = "counter.png"

WIDTH = int(os.environ.get("IMG_WIDTH", 700))
PADDING_LEFT = int(os.environ.get("PAD_LEFT", 28))
PADDING_TOP = int(os.environ.get("PAD_TOP", 18))
LINE_SPACING = int(os.environ.get("LINE_SPACING", 6))

# визуальные настройки
USE_SEMI_TRANSPARENT_CARD = os.environ.get("SEMI_CARD", "true").lower() in ("1","true","yes")
CARD_ALPHA = int(os.environ.get("CARD_ALPHA", 200))  # 0..255, 0=fully transparent
CARD_ROUND_RADIUS = int(os.environ.get("CARD_RADIUS", 12))

# цвета
TEXT_COLOR = (24, 30, 36, 255)
ACCENT_COLOR = (0, 110, 78, 255)
CARD_COLOR_RGBA = (255, 255, 255, CARD_ALPHA)  # белая полупрозрачная карточка
TRANSPARENT = (255, 255, 255, 0)

# Шрифты — кладём TTF в ./fonts/Roboto-Regular.ttf для точного совпадения
FONT_PATHS = [
    "./fonts/Roboto-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
]

# ====================================================================

def find_font():
    for p in FONT_PATHS:
        if os.path.exists(p):
            return p
    return None

def get_text_size(draw, text, font):
    # Возвращает (w,h) используя textbbox (работает в современных Pillow)
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    return w, h

def wrap_text_by_width(draw, text, font, max_width):
    # Безразрывный перенос по словам, измеряем ширину каждой строки
    words = text.split()
    if not words:
        return []
    lines = []
    cur = words[0]
    for w in words[1:]:
        test = cur + " " + w
        tw, _ = get_text_size(draw, test, font)
        if tw <= max_width:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines

# Простые векторные иконки (рисуем вручную) — размеры в px
def draw_no_smoke_icon(draw, x, y, size):
    # круг с диагональю + маленький "сигаретный прямоугольник"
    cx = x + size//2
    cy = y + size//2
    r = int(size*0.45)
    # circle outline
    draw.ellipse((cx-r, cy-r, cx+r, cy+r), outline=ACCENT_COLOR, width=max(2, size//12))
    # diagonal line
    draw.line((cx-r+4, cy+r-4, cx+r-4, cy-r+4), fill=ACCENT_COLOR, width=max(2, size//12))
    # cigarette (small rounded rect)
    cig_w = int(size*0.5)
    cig_h = int(size*0.16)
    cig_x = x + (size - cig_w) // 2
    cig_y = cy - cig_h//2 + int(size*0.2)
    draw.rectangle((cig_x, cig_y, cig_x + cig_w, cig_y + cig_h), fill=(200,200,200,255))
    # tip (burn) at right
    draw.rectangle((cig_x+cig_w-4, cig_y, cig_x+cig_w, cig_y+cig_h), fill=(255,120,0,255))

def draw_laptop_icon(draw, x, y, size):
    # rectangle screen + base
    w = size
    h = int(size*0.64)
    draw.rounded_rectangle((x, y, x+w, y+h), radius=max(2, size//12), outline=None, fill=(230,230,230,255))
    # base
    base_h = max(2, size//12)
    draw.rectangle((x + size*0.08, y+h, x + w - size*0.08, y+h+base_h), fill=(200,200,200,255))

def draw_heart_icon(draw, x, y, size):
    # simple heart via two circles and a triangle
    s = size
    left = (x + s*0.25, y + s*0.35)
    right = (x + s*0.75, y + s*0.35)
    top = (x + s*0.5, y + s*0.65)
    # two circles
    r = int(s*0.2)
    draw.ellipse((left[0]-r, left[1]-r, left[0]+r, left[1]+r), fill=(220,30,60,255))
    draw.ellipse((right[0]-r, right[1]-r, right[0]+r, right[1]+r), fill=(220,30,60,255))
    # bottom triangle-ish (rounded)
    draw.polygon([(x + s*0.15, y + s*0.45), (x + s*0.85, y + s*0.45), top], fill=(220,30,60,255))

# ---------- main ----------
def main():
    # parse date
    try:
        d0 = datetime.fromisoformat(QUIT_DATE)
    except Exception:
        d0 = datetime.strptime(QUIT_DATE, "%Y-%m-%d")
    if d0.tzinfo is None:
        d0 = d0.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    delta = now - d0
    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, OUT_FILE)

    font_path = find_font()
    if font_path:
        font_title = ImageFont.truetype(font_path, size=18)
        font_counter = ImageFont.truetype(font_path, size=48)  # меньше, чем раньше
        font_sub = ImageFont.truetype(font_path, size=12)
        font_tag = ImageFont.truetype(font_path, size=16)
    else:
        font_title = ImageFont.load_default()
        font_counter = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_tag = ImageFont.load_default()

    # Prepare layout text
    line_title = TITLE
    line_counter = f"{days} дн {hours} ч"
    line_sub = f"С {d0.date().isoformat()} · {minutes} мин"

    max_text_width = WIDTH - PADDING_LEFT - 28

    # temporary image for measurement
    tmp = Image.new("RGBA", (WIDTH, 600), TRANSPARENT)
    dt = ImageDraw.Draw(tmp)

    # wrap tagline by measured width (no word breaks)
    tagline_lines = wrap_text_by_width(dt, TAGLINE, font_tag, max_text_width)

    # measure heights
    y = PADDING_TOP
    _, h_title = get_text_size(dt, line_title, font_title); y += h_title + LINE_SPACING
    _, h_counter = get_text_size(dt, line_counter, font_counter); y += h_counter + LINE_SPACING
    _, h_sub = get_text_size(dt, line_sub, font_sub); y += h_sub + LINE_SPACING
    for ln in tagline_lines:
        _, h_ln = get_text_size(dt, ln, font_tag)
        y += h_ln + LINE_SPACING

    total_height = int(y + 16)

    # final image: transparent background
    img = Image.new("RGBA", (WIDTH, total_height), TRANSPARENT)
    draw = ImageDraw.Draw(img)

    # optional semi-transparent card for readability
    if USE_SEMI_TRANSPARENT_CARD:
        pad = 8
        draw.rounded_rectangle(
            (pad, pad, WIDTH - pad, total_height - pad),
            radius=CARD_ROUND_RADIUS, fill=CARD_COLOR_RGBA
        )

    # start drawing
    cur_y = PADDING_TOP + 4
    x = PADDING_LEFT

    # draw small no-smoking icon to the left of title
    icon_size = 22
    draw_no_smoke_icon(draw, x - icon_size - 10, cur_y - 2, icon_size)

    # title (left-aligned)
    draw.text((x, cur_y), line_title, font=font_title, fill=TEXT_COLOR)
    _, h_title = get_text_size(draw, line_title, font_title)
    cur_y += h_title + LINE_SPACING

    # counter (big) — ensure extra spacing below
    draw.text((x, cur_y), line_counter, font=font_counter, fill=ACCENT_COLOR)
    _, h_counter = get_text_size(draw, line_counter, font_counter)
    cur_y += h_counter + LINE_SPACING + 6  # extra gap to avoid overlap

    # subtitle (date/minutes)
    draw.text((x, cur_y), line_sub, font=font_sub, fill=TEXT_COLOR)
    _, h_sub = get_text_size(draw, line_sub, font_sub)
    cur_y += h_sub + LINE_SPACING

    # small icons before tagline: laptop + heart (draw inline with text)
    icon_margin = 2
    icon_x = x
    icon_y = cur_y
    # laptop icon
    draw_laptop_icon(draw, icon_x, icon_y, 18)
    icon_x += 18 + icon_margin
    # heart icon
    draw_heart_icon(draw, icon_x, icon_y, 18)
    icon_x += 18 + 8

    # draw tagline lines after a small left padding to leave space after icons
    tagline_x = x
    # if icons drawn, shift first line a bit to avoid overlap (we keep icons to the left of first line)
    # we'll draw tagline starting at same x (icons are before it visually)
    for ln in tagline_lines:
        draw.text((tagline_x, cur_y), ln, font=font_tag, fill=TEXT_COLOR)
        _, h_ln = get_text_size(draw, ln, font_tag)
        cur_y += h_ln + LINE_SPACING

    # save with RGBA — transparent background
    img.save(out_path, format="PNG")
    print("Saved:", out_path)

if __name__ == "__main__":
    main()
