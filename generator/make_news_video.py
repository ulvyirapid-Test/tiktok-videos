"""Render a 9:16 Khmer tech-news TikTok video from a JSON spec.

Usage: python3 make_news_video.py content/2026-11-09.json videos/2026-11-09.mp4 [seed]

JSON fields: hook, tag, headline, facts (list of 3), why, source
"""
import sys, json, math, os, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from music import make_music

W, H, FPS = 1080, 1920, 30
FONT = os.path.join(HERE, "..", "fonts", "KantumruyPro.ttf")
BG1, BG2 = (10, 14, 32), (26, 16, 60)
ACCENTS = [(0, 229, 255), (124, 255, 178), (255, 196, 0), (180, 140, 255), (255, 120, 90)]
PINK = (255, 64, 129)
WHITE = (245, 247, 255)
MUTED = (175, 183, 215)
KH_NUM = "០១២៣៤៥៦៧៨៩"
SAFE_W = 860  # keep text clear of TikTok's right-side buttons

_cache = {}
def font(size, weight="Bold"):
    k = (size, weight)
    if k not in _cache:
        f = ImageFont.truetype(FONT, size, layout_engine=ImageFont.Layout.RAQM)
        try: f.set_variation_by_name(weight)
        except Exception: pass
        _cache[k] = f
    return _cache[k]

_measure = ImageDraw.Draw(Image.new("RGB", (10, 10)))
def fit(s, size, weight, maxw, spacing=20):
    while size > 28:
        b = _measure.multiline_textbbox((0, 0), s, font=font(size, weight), spacing=spacing)
        if b[2] - b[0] <= maxw: break
        size -= 2
    return size

def ease(t): t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3
def kh(n): return "".join(KH_NUM[int(d)] for d in str(n))

def text(layer, xy, s, size, fill, alpha=1.0, anchor="la", weight="Bold", spacing=20, maxw=SAFE_W):
    if alpha <= 0: return
    size = fit(s, size, weight, maxw, spacing)
    ImageDraw.Draw(layer).multiline_text(xy, s, font=font(size, weight), fill=fill + (int(255 * alpha),),
                                         anchor=anchor, spacing=spacing, align="center" if anchor[0] == "m" else "left")

def make_bg(seed):
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(BG1[i] + (BG2[i] - BG1[i]) * t) for i in range(3)))
    glow = Image.new("RGB", (W, H)); g = ImageDraw.Draw(glow)
    a = ACCENTS[seed % len(ACCENTS)]
    g.ellipse([-300, -200, 700, 800], fill=tuple(int(c * 0.45) for c in a))
    g.ellipse([500, 1200, 1400, 2200], fill=(110, 20, 80))
    img = ImageChops.add(img, glow.filter(ImageFilter.GaussianBlur(220))).convert("RGBA")
    over = Image.new("RGBA", (W, H)); od = ImageDraw.Draw(over)
    for x in range(0, W, 90): od.line([(x, 0), (x, H)], fill=(255, 255, 255, 10))
    for y in range(0, H, 90): od.line([(0, y), (W, y)], fill=(255, 255, 255, 10))
    img.alpha_composite(over)
    return img.convert("RGB")

def render(spec, out_path, seed=0):
    A = ACCENTS[seed % len(ACCENTS)]
    S_HOOK, S_HEAD, S_FACT, S_WHY, S_CTA = 3.5, 4.0, 4.3, 5.0, 3.5
    t_head = S_HOOK; t_facts = t_head + S_HEAD
    t_why = t_facts + S_FACT * 3; t_cta = t_why + S_WHY
    TOTAL = t_cta + S_CTA
    bg = make_bg(seed)

    def chrome(layer, t):
        d = ImageDraw.Draw(layer)
        d.rounded_rectangle([80, 150, W - 80, 160], radius=5, fill=(255, 255, 255, 40))
        d.rounded_rectangle([80, 150, 80 + int((W - 160) * t / TOTAL), 160], radius=5, fill=A + (255,))
        text(layer, (80, 190), "TECH NEWS", 34, A)
        text(layer, (W - 80, 190), "#ព័ត៌មានTech", 34, MUTED, anchor="ra", weight="Medium")

    def chip(layer, label, y, alpha):
        if alpha <= 0: return
        f = font(40, "SemiBold")
        w = _measure.textlength(label, font=f) + 70
        x0 = (W - w) / 2
        ImageDraw.Draw(layer).rounded_rectangle([x0, y, x0 + w, y + 74], radius=37, fill=A + (int(60 * alpha),), outline=A + (int(255 * alpha),), width=3)
        text(layer, (W // 2, y + 37), label, 40, A, alpha, anchor="mm", weight="SemiBold")

    def scene(layer, t):
        d = ImageDraw.Draw(layer)
        if t < t_head:  # hook
            a = ease(t / 0.5)
            text(layer, (W // 2, 820 - int(60 * (1 - a))), spec["hook"], 104, WHITE, a, anchor="mm", spacing=36)
            b = ease((t - 1.0) / 0.5)
            if b > 0:
                off = int(16 * math.sin(t * 6)); y = 1130 + off
                d.polygon([(W//2 - 40, y), (W//2 + 40, y), (W//2, y + 50)], fill=PINK + (int(255 * b),))
        elif t < t_facts:  # headline
            st = t - t_head
            chip(layer, spec["tag"], 560, ease(st / 0.4))
            b = ease((st - 0.3) / 0.5)
            text(layer, (W // 2 + int(80 * (1 - b)), 880), spec["headline"], 96, WHITE, b, anchor="mm", spacing=34)
            c = ease((st - 1.0) / 0.5)
            if c > 0:
                d.rounded_rectangle([W//2 - 120, 1080, W//2 + 120, 1090], radius=5, fill=PINK + (int(255 * c),))
        elif t < t_why:  # facts accumulate
            st = t - t_facts
            text(layer, (W // 2, 330), spec["headline"].replace("\n", " "), 52, WHITE, 1.0, anchor="ma")
            for i, fact in enumerate(spec["facts"]):
                a = ease((st - i * S_FACT) / 0.5)
                if a <= 0: continue
                y0 = 480 + i * 330 + int(50 * (1 - a))
                active = i == min(2, int(st // S_FACT))
                d.rounded_rectangle([90, y0, W - 90, y0 + 290], radius=36,
                                    fill=(255, 255, 255, int((26 if active else 14) * a)),
                                    outline=(A if active else (120, 130, 170)) + (int(220 * a),), width=4)
                cx, cy = 175, y0 + 145
                d.ellipse([cx - 48, cy - 48, cx + 48, cy + 48], fill=A + (int(255 * a),))
                text(layer, (cx, cy + 2), kh(i + 1), 58, BG1, a, anchor="mm")
                text(layer, (260, cy), fact, 50, WHITE if active else MUTED, a, anchor="lm",
                     weight="SemiBold" if active else "Medium", spacing=18, maxw=W - 90 - 260 - 40)
        elif t < t_cta:  # why it matters
            st = t - t_why
            a = ease(st / 0.5)
            chip(layer, "ហេតុអ្វីសំខាន់?", 560, a)
            b = ease((st - 0.4) / 0.6)
            text(layer, (W // 2, 720 + int(40 * (1 - b))), spec["why"], 62, WHITE, b, anchor="ma", spacing=26)
        else:  # CTA
            st = t - t_cta
            a = ease(st / 0.5)
            cx, cy = W // 2, 640
            s = 1.0 + 0.05 * math.sin(st * 5); w, h = int(110 * s), int(146 * s)
            d.polygon([(cx - w//2, cy - h//2), (cx + w//2, cy - h//2), (cx + w//2, cy + h//2), (cx, cy + h//4), (cx - w//2, cy + h//2)], fill=PINK + (int(255 * a),))
            text(layer, (W // 2, 860), "Follow ដើម្បីតាមដាន\nព័ត៌មាន Tech រាល់ថ្ងៃ", 76, WHITE, a, anchor="ma", spacing=28)
        # source line (not on hook/CTA)
        if t_head <= t < t_cta and spec.get("source"):
            text(layer, (W // 2, 1500), "ប្រភព៖ " + spec["source"], 32, MUTED, 0.9, anchor="mm", weight="Regular")

    tmp = tempfile.mkdtemp()
    silent = os.path.join(tmp, "v.mp4"); wav = os.path.join(tmp, "m.wav")
    nframes = int(TOTAL * FPS)
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                             "-pix_fmt", "yuv420p", silent], stdin=subprocess.PIPE)
    previews = {int(x * FPS) for x in (1.5, t_head + 2, t_facts + S_FACT * 2.5, t_why + 3, TOTAL - 1)}
    for f in range(nframes):
        t = f / FPS
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        scene(layer, t)
        for boundary in (t_head, t_facts, t_why, t_cta):  # fade out before scene change
            if 0 < boundary - t < 0.25:
                k = (boundary - t) / 0.25
                layer.putalpha(layer.getchannel("A").point(lambda v, k=k: int(v * k)))
        chrome(layer, t)
        frame = bg.copy().convert("RGBA"); frame.alpha_composite(layer)
        rgb = frame.convert("RGB")
        proc.stdin.write(rgb.tobytes())
        if f in previews:
            rgb.save(out_path.replace(".mp4", f"_p{f}.png"))
    proc.stdin.close(); proc.wait()
    make_music(wav, TOTAL, seed)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", wav, "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "160k", "-shortest", "-movflags", "+faststart", out_path], check=True)
    return TOTAL

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    print("rendered", render(spec, sys.argv[2], seed), "s")
