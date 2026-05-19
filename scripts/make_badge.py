from PIL import Image, ImageDraw, ImageFont
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(BASE, ".knowledge", "templates", "assets")

SCALE = 4

class C:
    gold = (219, 197, 133)
    gold_rich = (200, 165, 60)
    gold_bright = (240, 200, 80)
    navy = (35, 45, 75)
    navy_mid = (55, 70, 110)
    charcoal = (59, 52, 71)
    red_warm = (200, 50, 50)
    red_soft = (180, 70, 70)
    cream = (255, 248, 235)
    green_mgo = (60, 120, 80)
    white = (255, 255, 255)


def draw_sparkle(draw, cx, cy, size, color, width=3):
    draw.line([(cx, cy - size), (cx, cy + size)], fill=color, width=width)
    draw.line([(cx - size, cy), (cx + size, cy)], fill=color, width=width)
    s2 = int(size * 0.5)
    w2 = max(1, width - 1)
    draw.line([(cx - s2, cy - s2), (cx + s2, cy + s2)], fill=color, width=w2)
    draw.line([(cx + s2, cy - s2), (cx - s2, cy + s2)], fill=color, width=w2)
    r = width + 1
    draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=color)


def draw_analytics_small(draw, ox, oy, s=1):
    """Compact: 4 ascending bars + connected dot line (no arrow) + small magnifying glass"""
    S = s

    bar_w = 16 * S
    bar_gap = 5 * S
    bar_bottom = oy + 55 * S
    num_bars = 4

    bar_heights = [28, 38, 34, 50]
    bar_colors = [
        (C.navy_mid, C.navy),
        (C.red_soft, C.red_warm),
        (C.red_soft, C.red_warm),
        (C.gold_rich, C.gold),
    ]

    bar_centers_x = []
    for i in range(num_bars):
        col_top, col_bot = bar_colors[i]
        height = bar_heights[i]
        bx = ox + i * (bar_w + bar_gap)
        btop = bar_bottom - height * S
        h = bar_bottom - btop
        for row in range(h):
            t = row / max(1, h - 1)
            r = int(col_top[0] + (col_bot[0] - col_top[0]) * t)
            g = int(col_top[1] + (col_bot[1] - col_top[1]) * t)
            b = int(col_top[2] + (col_bot[2] - col_top[2]) * t)
            draw.rectangle([(bx, btop + row), (bx + bar_w, btop + row)], fill=(r, g, b))
        draw.rounded_rectangle(
            [(bx, btop), (bx + bar_w, bar_bottom)],
            radius=3 * S, fill=None, outline=col_bot, width=1 * S
        )
        bar_centers_x.append(bx + bar_w // 2)

    chart_right = ox + (num_bars - 1) * (bar_w + bar_gap) + bar_w

    # Connected dot line on top (no arrow, just dots and lines)
    line_y_values = [25, 35, 30, 48]
    line_points = []
    for i in range(num_bars):
        px = bar_centers_x[i]
        py = bar_bottom - line_y_values[i] * S - 10 * S
        line_points.append((px, py))

    for i in range(len(line_points) - 1):
        draw.line([line_points[i], line_points[i + 1]], fill=C.charcoal, width=3 * S)

    dot_r = 5 * S
    for px, py in line_points:
        draw.ellipse(
            [(px - dot_r, py - dot_r), (px + dot_r, py + dot_r)],
            fill=C.charcoal, outline=C.white, width=2 * S
        )

    # Small magnifying glass
    mag_cx = chart_right + 28 * S
    mag_cy = oy + 15 * S
    mag_r = 20 * S

    draw.ellipse(
        [(mag_cx - mag_r, mag_cy - mag_r), (mag_cx + mag_r, mag_cy + mag_r)],
        fill=C.cream, outline=C.charcoal, width=4 * S
    )

    hx1 = int(mag_cx + mag_r * 0.65)
    hy1 = int(mag_cy + mag_r * 0.65)
    hx2 = int(hx1 + 14 * S)
    hy2 = int(hy1 + 14 * S)
    draw.line([(hx1, hy1), (hx2, hy2)], fill=C.charcoal, width=5 * S)
    draw.line([(hx1 + 2 * S, hy1 + 2 * S), (hx2, hy2)], fill=C.gold_rich, width=3 * S)

    # Tiny line inside glass
    mini_pts = [
        (mag_cx - 8 * S, mag_cy + 4 * S),
        (mag_cx - 2 * S, mag_cy - 2 * S),
        (mag_cx + 4 * S, mag_cy + 1 * S),
        (mag_cx + 10 * S, mag_cy - 6 * S),
    ]
    draw.line(mini_pts, fill=C.red_warm, width=2 * S)

    # Subtle sparkles
    draw_sparkle(draw, ox - 3 * S, oy, 7 * S, C.gold, width=2 * S)
    draw_sparkle(draw, chart_right + 5 * S, oy - 18 * S, 8 * S, C.gold_bright, width=2 * S)

    return hx2 + 5 * S


# VERSION A: MGO LOGO with analytics underneath, text tight
final_w, final_h = 440, 260
canvas_w, canvas_h = final_w * SCALE, final_h * SCALE
canvas_a = Image.new("RGBA", (canvas_w, canvas_h), (255, 255, 255, 0))

logo = Image.open(os.path.join(ASSETS, "mgo_logo.png")).convert("RGBA")
logo_h_target = 120 * SCALE
ratio = logo_h_target / logo.height
logo_resized = logo.resize((int(logo.width * ratio), logo_h_target), Image.LANCZOS)

# Center logo at top
logo_x = (canvas_w - logo_resized.width) // 2
logo_y = 10 * SCALE
canvas_a.paste(logo_resized, (logo_x, logo_y), logo_resized)

draw_a = ImageDraw.Draw(canvas_a)

# Analytics icon below logo, centered (shifted right, scaled down)
icon_scale = 0.75
icon_total_w = int((4 * 16 + 3 * 5 + 28 + 20 + 14 + 5) * SCALE * icon_scale)
icon_x = (canvas_w - icon_total_w) // 2 + 20 * SCALE
icon_y = logo_y + logo_resized.height + 18 * SCALE
draw_analytics_small(draw_a, icon_x, icon_y, s=int(SCALE * icon_scale))

# "AI POWERED" text - thin modern, letter-spaced
try:
    font_display = ImageFont.truetype("C:/Windows/Fonts/segoeuil.ttf", 20 * SCALE)
except Exception:
    font_display = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 20 * SCALE)

line1 = "A I   P O W E R E D"
line2 = "A N A L Y S I S"

bbox1 = draw_a.textbbox((0, 0), line1, font=font_display)
w1 = bbox1[2] - bbox1[0]
h1 = bbox1[3] - bbox1[1]

bbox2 = draw_a.textbbox((0, 0), line2, font=font_display)
w2 = bbox2[2] - bbox2[0]

text_y = icon_y + int(62 * SCALE * icon_scale) + 10 * SCALE
line_gap = 4 * SCALE

draw_a.text(((canvas_w - w1) // 2, text_y), line1, fill=C.charcoal, font=font_display)
draw_a.text(((canvas_w - w2) // 2, text_y + h1 + line_gap), line2, fill=C.charcoal, font=font_display)

canvas_a_final = canvas_a.resize((final_w, final_h), Image.LANCZOS)
canvas_a_final.save(os.path.join(ASSETS, "ai_powered_badge.png"), "PNG")
print(f"Version A (logo) saved: {final_w}x{final_h}")


# VERSION B: MR. MONOPOLY with analytics + text to the right
final_w_b, final_h_b = 440, 220
canvas_w_b, canvas_h_b = final_w_b * SCALE, final_h_b * SCALE
canvas_b = Image.new("RGBA", (canvas_w_b, canvas_h_b), (255, 255, 255, 0))

artwork = Image.open(os.path.join(ASSETS, "mgo_artwork.png")).convert("RGBA")
art_h_target = 190 * SCALE
ratio_b = art_h_target / artwork.height
art_resized = artwork.resize((int(artwork.width * ratio_b), art_h_target), Image.LANCZOS)

art_x = 5 * SCALE
art_y = (canvas_h_b - art_resized.height) // 2
canvas_b.paste(art_resized, (art_x, art_y), art_resized)

draw_b = ImageDraw.Draw(canvas_b)

# Analytics to the right of Mr. Monopoly, vertically centered
icon_x_b = art_x + art_resized.width + 10 * SCALE
icon_y_b = canvas_h_b // 2 - 20 * SCALE
draw_analytics_small(draw_b, icon_x_b, icon_y_b, s=SCALE)

# "AI POWERED" text - thin modern, letter-spaced
try:
    font_display_b = ImageFont.truetype("C:/Windows/Fonts/segoeuil.ttf", 18 * SCALE)
except Exception:
    font_display_b = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 18 * SCALE)

line1_b = "A I   P O W E R E D"
line2_b = "A N A L Y S I S"

bbox1_b = draw_b.textbbox((0, 0), line1_b, font=font_display_b)
w1_b = bbox1_b[2] - bbox1_b[0]
h1_b = bbox1_b[3] - bbox1_b[1]

bbox2_b = draw_b.textbbox((0, 0), line2_b, font=font_display_b)
w2_b = bbox2_b[2] - bbox2_b[0]

icon_area_center = icon_x_b + 50 * SCALE
text_y_b = icon_y_b + 60 * SCALE + 5 * SCALE
line_gap_b = 3 * SCALE

draw_b.text((icon_area_center - w1_b // 2, text_y_b), line1_b, fill=C.charcoal, font=font_display_b)
draw_b.text((icon_area_center - w2_b // 2, text_y_b + h1_b + line_gap_b), line2_b, fill=C.charcoal, font=font_display_b)

canvas_b_final = canvas_b.resize((final_w_b, final_h_b), Image.LANCZOS)
canvas_b_final.save(os.path.join(ASSETS, "ai_powered_badge_v2.png"), "PNG")
print(f"Version B (artwork) saved: {final_w_b}x{final_h_b}")
