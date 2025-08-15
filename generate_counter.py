#!/usr/bin/env python3
# generate_counter.py
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timezone
import os, textwrap

# ========== Настройки ==========
QUIT_DATE = os.environ.get("QUIT_DATE", "2025-08-16")  # формат YYYY-MM-DD
TITLE = os.environ.get("TITLE", "🚭 Свободен от дыма с 15.08.2025")
TAGLINE = os.environ.get("TAGLINE", "💻 IT, семья, здоровье — мой новый стек жизни")
OUT_DIR = "public"
OUT_FILE = "counter.png"

# Размеры картинки — можно менять
WIDTH = int(os.environ.get("IMG_WIDTH", 700))
PADDING_LEFT = int(os.environ.get("PAD_LEFT", 28))
PADDING_TOP = int(os.environ.get("PAD_TOP", 18))
LINE_SPACING = 8  # пространство между строками

# Цвета
BG_COLOR = (245, 251, 255)
CARD_COLOR = (255, 255, 255)
TEXT_COLOR = (24, 30, 36)
ACCENT_COLOR = (0, 100, 80)

# Шрифты: сначала локальные в repo/fonts, затем системные
FONT_PATHS = [
    "./fonts/Roboto-Regular.ttf",
    "./fonts/FiraSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
]
# ================================

def find_font():
    for p in FONT_PATHS:
        if os.path.exists(p):
            return p
    return None

# parse quit date
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
    font_title = ImageFont.truetype(font_path, size=20)
    font_counter = ImageFont.truetype(font_path, size=56)
    font_sub = ImageFont.truetype(font_path, size=14)
    font_tag = ImageFont.truetype(font_path, size=18)
else:
    font_title = ImageFont.load_default()
    font_counter = ImageFont.load_default()
    font_sub = ImageFont.load_default()
    font_tag = ImageFont.load_default()

# Prepare lines (all will be drawn left-aligned)
line_title = TITLE
line_counter = f"{days} дн {hours} ч"
line_sub = f"С {d0.date().isoformat()} · {minutes} мин"
# tagline may be long — we'll wrap it
max_text_width = WIDTH - PADDING_LEFT - 28

# create temporary image to measure text height
tmp_img = Image.new("RGBA", (WIDTH, 400), BG_COLOR)
draw_tmp = ImageDraw.Draw(tmp_img)

# wrap tagline into lines that fit
words = TAGLINE
wrapped = []
# naive wrap: try different wrap widths until fits
for wrap_chars in range(40, 120):
    cand = textwrap.fill(words, width=wrap_chars)
    # measure widest line
    ok = True
    for l in cand.splitlines():
        w, h = draw_tmp.textsize(l, font=font_tag)
        if w > max_text_width:
            ok = False
            break
    if ok:
        wrapped = cand.splitlines()
        break
if not wrapped:
    # fallback: simple splitting by words into ~2 lines
    wrapped = textwrap.wrap(words, width=60)

# measure total height
y = PADDING_TOP
w, h = draw_tmp.textsize(line_title, font=font_title); y += h + LINE_SPACING
w, h_counter = draw_tmp.textsize(line_counter, font=font_counter); y += h_counter + LINE_SPACING
w, h = draw_tmp.textsize(line_sub, font=font_sub); y += h + LINE_SPACING
for l in wrapped:
    w, h = draw_tmp.textsize(l, font=font_tag); y += h + LINE_SPACING
total_height = y + 16

# create final image with enough height
img = Image.new("RGBA", (WIDTH, total_height), BG_COLOR)
draw = ImageDraw.Draw(img)

# draw white card background (optional)
card_pad = 10
draw.rounded_rectangle(
    (card_pad, card_pad, WIDTH - card_pad, total_height - card_pad),
    radius=12,
    fill=CARD_COLOR
)

# start drawing left-aligned
cur_y = PADDING_TOP + 4
x = PADDING_LEFT

# title
draw.text((x, cur_y), line_title, font=font_title, fill=TEXT_COLOR)
w, h = draw.textsize(line_title, font=font_title)
cur_y += h + LINE_SPACING

# counter (большой)
draw.text((x, cur_y), line_counter, font=font_counter, fill=ACCENT_COLOR)
w, h = draw.textsize(line_counter, font=font_counter)
cur_y += h + LINE_SPACING

# subtitle (date + minutes)
draw.text((x, cur_y), line_sub, font=font_sub, fill=TEXT_COLOR)
w, h = draw.textsize(line_sub, font=font_sub)
cur_y += h + LINE_SPACING

# tagline (wrapped)
for ln in wrapped:
    draw.text((x, cur_y), ln, font=font_tag, fill=TEXT_COLOR)
    w, h = draw.textsize(ln, font=font_tag)
    cur_y += h + LINE_SPACING

# save
img.save(out_path)
print("Saved:", out_path)
