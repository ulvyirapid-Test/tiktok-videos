from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, random, os

FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "fonts", "KantumruyPro.ttf")
NAVY1 = (8, 15, 34); NAVY2 = (17, 32, 66)
CYAN = (34, 211, 238); YELLOW = (250, 204, 21); WHITE = (241, 245, 249); MUTED = (148, 163, 184)
W, H = 1080, 1920
SAFE_R = int(W * 0.85)  # keep text left of TikTok right-side UI

def font(size, weight="Bold"):
    f = ImageFont.truetype(FONT, size, layout_engine=ImageFont.Layout.RAQM)
    f.set_variation_by_name(weight)
    return f

def base(seed):
    img = Image.new("RGB", (W, H), NAVY1)
    px = img.load()
    for y in range(H):
        t = y / H
        c = tuple(int(NAVY1[i] + (NAVY2[i] - NAVY1[i]) * t) for i in range(3))
        for x in range(W):
            px[x, y] = c
    img = img.convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    rnd = random.Random(seed)
    for _ in range(22):
        x, y = rnd.randint(0, W), rnd.randint(0, H)
        pts = [(x, y)]
        for _ in range(rnd.randint(2, 4)):
            if rnd.random() < 0.5: x += rnd.choice([-1, 1]) * rnd.randint(60, 200)
            else: y += rnd.choice([-1, 1]) * rnd.randint(60, 200)
            pts.append((x, y))
        d.line(pts, fill=CYAN + (30,), width=3)
        d.ellipse([x-8, y-8, x+8, y+8], outline=CYAN + (30,), width=3)
    img.alpha_composite(ov)
    return img

def glow(img, cx, cy, r, color, strength=90):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse([cx-r, cy-r, cx+r, cy+r], fill=color + (strength,))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(r * 0.45)))

def header(d, topic="AI ជាអ្វី?"):
    # brand chip top-left, topic chip
    f = font(40, "Bold")
    d.rounded_rectangle([70, 150, 70 + d.textlength("Smart Tips KH", font=f) + 60, 226], radius=38, fill=(32, 48, 86))
    d.text((100, 158), "Smart Tips", font=f, fill=WHITE)
    d.text((100 + d.textlength("Smart Tips ", font=f), 158), "KH", font=f, fill=YELLOW)
    ft = font(40, "SemiBold")
    tw = d.textlength(topic, font=ft)
    x1 = SAFE_R
    d.rounded_rectangle([x1 - tw - 60, 150, x1, 226], radius=38, outline=CYAN, width=3)
    d.text((x1 - tw - 30, 160), topic, font=ft, fill=CYAN)

def center_text(d, y, text, f, fill, max_w=SAFE_R - 70):
    lines = text.split("\n")
    for ln in lines:
        tw = d.textlength(ln, font=f)
        x = 70 + (max_w - tw) / 2
        d.text((x, y), ln, font=f, fill=fill)
        y += int(f.size * 1.45)
    return y

def badge(d, cx, cy, n):
    d.ellipse([cx-70, cy-70, cx+70, cy+70], fill=YELLOW)
    f = font(90, "Bold")
    tw = d.textlength(str(n), font=f)
    d.text((cx - tw/2, cy - 62), str(n), font=f, fill=NAVY1)

CX = (70 + SAFE_R) // 2  # visual centre of the safe area

# ---------- icons (generic, no brand logos) ----------
def icon_phone(d, cx, cy):
    d.rounded_rectangle([cx-140, cy-250, cx+140, cy+250], radius=40, outline=WHITE, width=12)
    d.rounded_rectangle([cx-40, cy-225, cx+40, cy-210], radius=7, fill=WHITE)
    # sparkle "AI" inside
    f = font(110, "Bold")
    tw = d.textlength("AI", font=f)
    d.text((cx - tw/2, cy - 90), "AI", font=f, fill=YELLOW)
    for (dx, dy, s) in [(-80, -130, 22), (85, 70, 16), (70, -150, 12)]:
        x, y = cx+dx, cy+dy
        d.polygon([(x, y-s), (x+s*0.3, y-s*0.3), (x+s, y), (x+s*0.3, y+s*0.3), (x, y+s), (x-s*0.3, y+s*0.3), (x-s, y), (x-s*0.3, y-s*0.3)], fill=CYAN)

def icon_brain_chip(d, cx, cy):
    s = 170
    d.rounded_rectangle([cx-s, cy-s, cx+s, cy+s], radius=40, outline=CYAN, width=12)
    for i in range(-2, 3):
        o = i * 60
        for (a, b, c, e) in [(cx+o, cy-s, cx+o, cy-s-55), (cx+o, cy+s, cx+o, cy+s+55), (cx-s, cy+o, cx-s-55, cy+o), (cx+s, cy+o, cx+s+55, cy+o)]:
            d.line([(a, b), (c, e)], fill=CYAN, width=10)
            d.ellipse([c-10, e-10, c+10, e+10], fill=CYAN)
    # data dots -> brain
    f = font(130, "Bold")
    tw = d.textlength("AI", font=f)
    d.text((cx - tw/2, cy - 105), "AI", font=f, fill=YELLOW)

def icon_feed(d, cx, cy):
    d.rounded_rectangle([cx-170, cy-260, cx+170, cy+260], radius=40, outline=WHITE, width=10)
    for i, col in enumerate([CYAN, YELLOW, CYAN]):
        y0 = cy - 220 + i * 150
        d.rounded_rectangle([cx-130, y0, cx+130, y0+120], radius=18, fill=col + (255,))
        d.polygon([(cx-20, y0+35), (cx-20, y0+85), (cx+25, y0+60)], fill=NAVY1)
    # heart
    hx, hy = cx + 175, cy + 170
    d.ellipse([hx-60, hy-50, hx, hy+10], fill=(244, 63, 94))
    d.ellipse([hx-10, hy-50, hx+50, hy+10], fill=(244, 63, 94))
    d.polygon([(hx-58, hy-8), (hx+48, hy-8), (hx-5, hy+60)], fill=(244, 63, 94))

def icon_map(d, cx, cy):
    d.rounded_rectangle([cx-220, cy-220, cx+220, cy+220], radius=40, fill=(30, 48, 90), outline=WHITE, width=8)
    # roads
    d.line([(cx-220, cy+80), (cx+220, cy-40)], fill=(71, 85, 105), width=34)
    d.line([(cx-60, cy-220), (cx+40, cy+220)], fill=(71, 85, 105), width=34)
    # route
    d.line([(cx-170, cy+150), (cx-60, cy+50), (cx+20, cy+20), (cx+120, cy-110)], fill=CYAN, width=18, joint="curve")
    # red jam segment on other road
    d.line([(cx-40, cy-150), (cx-10, cy-60)], fill=(244, 63, 94), width=22)
    # pin
    px, py = cx + 120, cy - 150
    d.ellipse([px-55, py-55, px+55, py+55], fill=YELLOW)
    d.polygon([(px-45, py+25), (px+45, py+25), (px, py+105)], fill=YELLOW)
    d.ellipse([px-20, py-20, px+20, py+20], fill=NAVY1)

def icon_chat(d, cx, cy):
    d.rounded_rectangle([cx-230, cy-230, cx+90, cy-60], radius=40, fill=WHITE)
    d.polygon([(cx-170, cy-62), (cx-120, cy-62), (cx-190, cy-10)], fill=WHITE)
    f = font(56, "SemiBold")
    d.text((cx-195, cy-190), "សួស្តី AI!", font=f, fill=NAVY1)
    d.rounded_rectangle([cx-90, cy+10, cx+230, cy+230], radius=40, fill=CYAN)
    d.polygon([(cx+130, cy+228), (cx+180, cy+228), (cx+200, cy+280)], fill=CYAN)
    for i in range(3):
        y = cy + 60 + i * 50
        d.rounded_rectangle([cx-50, y, cx + 190 - i * 60, y + 22], radius=11, fill=NAVY1)

def logo_bulb(d, cx, cy, s):
    d.ellipse([cx-s, cy-s*1.05, cx+s, cy+s*0.95], fill=YELLOW)
    nw = s*0.55
    d.polygon([(cx-s*0.62, cy+s*0.62), (cx+s*0.62, cy+s*0.62), (cx+nw, cy+s*1.15), (cx-nw, cy+s*1.15)], fill=YELLOW)
    for i in range(3):
        y0 = cy + s*1.22 + i*s*0.2
        d.rounded_rectangle([cx-nw, y0, cx+nw, y0+s*0.13], radius=s*0.06, fill=CYAN)
    lw = max(3, int(s*0.07))
    d.line([(cx, cy+s*0.95), (cx, cy-s*0.05)], fill=NAVY1, width=lw)
    d.line([(cx, cy+s*0.25), (cx-s*0.42, cy-s*0.17), (cx-s*0.42, cy-s*0.45)], fill=NAVY1, width=lw)
    d.line([(cx, cy+s*0.05), (cx+s*0.42, cy-s*0.37), (cx+s*0.42, cy-s*0.6)], fill=NAVY1, width=lw)
    r = s*0.11
    for (a, b) in [(cx, cy-s*0.05), (cx-s*0.42, cy-s*0.45), (cx+s*0.42, cy-s*0.6)]:
        d.ellipse([a-r, b-r, a+r, b+r], fill=NAVY1)
    for ang in [-150, -120, -90, -60, -30]:
        a = math.radians(ang); r1, r2 = s*1.3, s*1.62
        d.line([(cx+math.cos(a)*r1, cy-s*0.05+math.sin(a)*r1), (cx+math.cos(a)*r2, cy-s*0.05+math.sin(a)*r2)], fill=CYAN, width=max(4, int(s*0.1)))



RED = (244, 63, 94); GREEN = (34, 197, 94); PANEL = (30, 48, 90)
ICON_Y = 700

# ---------------- extra generic icons ----------------
def icon_battery(d, cx, cy, pct=0.08, col=RED, label="5%"):
    d.rounded_rectangle([cx-230, cy-120, cx+190, cy+120], radius=30, outline=WHITE, width=14)
    d.rounded_rectangle([cx+190, cy-45, cx+230, cy+45], radius=10, fill=WHITE)
    w = int(380 * pct)
    d.rounded_rectangle([cx-205, cy-95, cx-205+max(w, 30), cy+95], radius=16, fill=col)
    f = font(110, "Bold"); tw = d.textlength(label, font=f)
    d.text((cx - 20 - tw/2, cy - 80), label, font=f, fill=WHITE)

def icon_timer(d, cx, cy, label="30s"):
    d.ellipse([cx-200, cy-200, cx+200, cy+200], outline=CYAN, width=16)
    d.rounded_rectangle([cx-40, cy-260, cx+40, cy-215], radius=10, fill=CYAN)
    d.pieslice([cx-170, cy-170, cx+170, cy+170], -90, 90, fill=CYAN + (255,))
    d.ellipse([cx-120, cy-120, cx+120, cy+120], fill=PANEL)
    f = font(100, "Bold"); tw = d.textlength(label, font=f)
    d.text((cx - tw/2, cy - 75), label, font=f, fill=YELLOW)

def icon_moon(d, cx, cy):
    d.rounded_rectangle([cx-150, cy-260, cx+150, cy+260], radius=40, fill=(2, 6, 23), outline=WHITE, width=10)
    d.ellipse([cx-110, cy-110, cx+110, cy+110], fill=YELLOW)
    d.ellipse([cx-45, cy-140, cx+135, cy+50], fill=(2, 6, 23))
    for (x, y, s) in [(cx+70, cy+120, 14), (cx-80, cy-170, 10), (cx+90, cy-190, 8)]:
        d.ellipse([x-s, y-s, x+s, y+s], fill=WHITE)

def icon_apps(d, cx, cy):
    cols = [CYAN, YELLOW, RED, GREEN, CYAN, YELLOW, GREEN, RED, CYAN]
    for i in range(9):
        r, c = divmod(i, 3)
        x0 = cx - 230 + c * 160; y0 = cy - 230 + r * 160
        d.rounded_rectangle([x0, y0, x0 + 130, y0 + 130], radius=30, fill=cols[i])
    for i in (2, 5, 7):  # crossed-out background apps
        r, c = divmod(i, 3)
        x0 = cx - 230 + c * 160; y0 = cy - 230 + r * 160
        d.rounded_rectangle([x0, y0, x0 + 130, y0 + 130], radius=30, fill=(51, 65, 85))
        d.line([(x0 + 25, y0 + 25), (x0 + 105, y0 + 105)], fill=RED, width=14)
        d.line([(x0 + 105, y0 + 25), (x0 + 25, y0 + 105)], fill=RED, width=14)

def doc(d, x0, y0, w, h, col=WHITE, lines=5, line_col=MUTED):
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=18, fill=col)
    for i in range(lines):
        y = y0 + 50 + i * (h - 90) / max(lines - 1, 1)
        d.rounded_rectangle([x0 + 35, y, x0 + w - 35 - (i % 2) * 60, y + 18], radius=9, fill=line_col)

def icon_before_after_doc(d, cx, cy):
    # crooked dark photo -> clean PDF
    tmp = Image.new("RGBA", (330, 420), (0, 0, 0, 0)); td = ImageDraw.Draw(tmp)
    doc(td, 15, 15, 300, 390, col=(100, 100, 90), line_col=(60, 60, 55))
    tmp = tmp.rotate(14, expand=True)
    d._image.alpha_composite(tmp, (cx - 470, cy - 260))
    d.line([(cx - 70, cy), (cx + 30, cy)], fill=YELLOW, width=18)
    d.polygon([(cx + 30, cy - 40), (cx + 90, cy), (cx + 30, cy + 40)], fill=YELLOW)
    doc(d, cx + 110, cy - 210, 300, 400)
    d.rounded_rectangle([cx + 280, cy + 120, cx + 400, cy + 180], radius=12, fill=RED)
    d.text((cx + 293, cy + 120), "PDF", font=font(44, "Bold"), fill=WHITE)

def icon_phone_over_paper(d, cx, cy):
    doc(d, cx - 230, cy - 120, 460, 330, col=WHITE)
    d.rounded_rectangle([cx - 130, cy - 300, cx + 130, cy + 160], radius=36, fill=NAVY1, outline=CYAN, width=12)
    for (a, b) in [((cx-90, cy-200), (cx-90, cy-240)), ((cx-90, cy-240), (cx-50, cy-240)),
                   ((cx+90, cy-200), (cx+90, cy-240)), ((cx+90, cy-240), (cx+50, cy-240)),
                   ((cx-90, cy+60), (cx-90, cy+100)), ((cx-90, cy+100), (cx-50, cy+100)),
                   ((cx+90, cy+60), (cx+90, cy+100)), ((cx+90, cy+100), (cx+50, cy+100))]:
        d.line([a, b], fill=YELLOW, width=10)

def icon_plus_scan(d, cx, cy):
    d.rounded_rectangle([cx - 170, cy - 260, cx + 170, cy + 260], radius=40, outline=WHITE, width=10)
    for i in range(3):
        y = cy - 200 + i * 110
        d.rounded_rectangle([cx - 120, y, cx + 120, y + 80], radius=14, fill=PANEL)
    d.ellipse([cx + 40, cy + 120, cx + 160, cy + 240], fill=YELLOW)
    d.line([(cx + 100, cy + 145), (cx + 100, cy + 215)], fill=NAVY1, width=14)
    d.line([(cx + 65, cy + 180), (cx + 135, cy + 180)], fill=NAVY1, width=14)

def icon_camera_scan(d, cx, cy):
    d.rounded_rectangle([cx - 220, cy - 140, cx + 220, cy + 170], radius=40, fill=CYAN)
    d.rounded_rectangle([cx - 80, cy - 190, cx + 80, cy - 120], radius=20, fill=CYAN)
    d.ellipse([cx - 105, cy - 90, cx + 105, cy + 120], fill=NAVY1)
    d.ellipse([cx - 65, cy - 50, cx + 65, cy + 80], fill=YELLOW)
    doc(d, cx + 120, cy + 60, 160, 200, lines=3)

def icon_send_pdf(d, cx, cy):
    doc(d, cx - 260, cy - 180, 240, 320)
    d.rounded_rectangle([cx - 160, cy + 80, cx - 40, cy + 140], radius=12, fill=RED)
    d.text((cx - 147, cy + 80), "PDF", font=font(44, "Bold"), fill=WHITE)
    # paper plane (generic)
    p = [(cx + 20, cy + 20), (cx + 280, cy - 150), (cx + 190, cy + 170), (cx + 130, cy + 70)]
    d.polygon([p[0], p[1], p[3]], fill=CYAN)
    d.polygon([p[3], p[1], p[2]], fill=(14, 165, 233))

def icon_bad_chat(d, cx, cy):
    d.rounded_rectangle([cx - 240, cy - 200, cx + 240, cy + 140], radius=40, fill=WHITE)
    d.polygon([(cx - 150, cy + 138), (cx - 90, cy + 138), (cx - 170, cy + 200)], fill=WHITE)
    for i in range(4):
        y = cy - 140 + i * 65
        d.rounded_rectangle([cx - 190, y, cx + 190 - (i % 2) * 70, y + 26], radius=13, fill=(148, 163, 184))
    d.ellipse([cx + 130, cy - 290, cx + 290, cy - 130], fill=RED)
    d.line([(cx + 170, cy - 250), (cx + 250, cy - 170)], fill=WHITE, width=18)
    d.line([(cx + 250, cy - 250), (cx + 170, cy - 170)], fill=WHITE, width=18)

def icon_short_prompt(d, cx, cy):
    d.rounded_rectangle([cx - 330, cy - 70, cx + 330, cy + 70], radius=70, fill=WHITE)
    d.text((cx - 285, cy - 38), "សរសេរសារសុំច្បាប់", font=font(50, "SemiBold"), fill=NAVY1)
    d.ellipse([cx + 215, cy - 50, cx + 315, cy + 50], fill=CYAN)
    d.polygon([(cx + 245, cy - 25), (cx + 245, cy + 25), (cx + 290, cy)], fill=NAVY1)
    f = font(140, "Bold"); d.text((cx - 40, cy - 290), "?", font=f, fill=YELLOW)

def icon_four_chips(d, cx, cy):
    items = [("អ្នកណា", CYAN), ("រឿងអ្វី", YELLOW), ("Tone", GREEN), ("ប្រវែង", RED)]
    f = font(58, "Bold")
    for i, (t, c) in enumerate(items):
        r, k = divmod(i, 2)
        x0 = cx - 280 + k * 300; y0 = cy - 190 + r * 210
        d.rounded_rectangle([x0, y0, x0 + 260, y0 + 160], radius=36, fill=c)
        tw = d.textlength(t, font=f)
        d.text((x0 + 130 - tw/2, y0 + 40), t, font=f, fill=NAVY1)

def icon_highlight_line(d, cx, cy):
    d.rounded_rectangle([cx - 280, cy - 230, cx + 280, cy + 230], radius=30, fill=PANEL)
    for i in range(5):
        y = cy - 180 + i * 80
        if i == 3:
            d.rounded_rectangle([cx - 250, y - 14, cx + 250, y + 44], radius=12, fill=YELLOW)
            d.rounded_rectangle([cx - 220, y + 4, cx + 200, y + 26], radius=11, fill=NAVY1)
        else:
            d.rounded_rectangle([cx - 220, y + 4, cx + 220 - (i % 2) * 90, y + 26], radius=11, fill=(100, 116, 139))

def icon_before_after_chat(d, cx, cy):
    for k, (col, mark) in enumerate([(RED, "x"), (GREEN, "v")]):
        x0 = cx - 290 + k * 300
        d.rounded_rectangle([x0, cy - 200, x0 + 270, cy + 200], radius=30, fill=PANEL, outline=col, width=8)
        for i in range(4):
            y = cy - 140 + i * 70
            lc = (100, 116, 139) if k == 0 else WHITE
            d.rounded_rectangle([x0 + 30, y, x0 + 240 - (i % 2) * 60, y + 24], radius=12, fill=lc)
        bx, by = x0 + 135, cy - 230
        d.ellipse([bx - 50, by - 50, bx + 50, by + 50], fill=col)
        if mark == "x":
            d.line([(bx - 22, by - 22), (bx + 22, by + 22)], fill=WHITE, width=12)
            d.line([(bx + 22, by - 22), (bx - 22, by + 22)], fill=WHITE, width=12)
        else:
            d.line([(bx - 25, by), (bx - 6, by + 22), (bx + 26, by - 20)], fill=WHITE, width=12)

def icon_logo(d, cx, cy):
    d.ellipse([cx - 260, cy - 260, cx + 260, cy + 260], outline=CYAN, width=14)
    logo_bulb(d, cx, cy - 40, 120)

