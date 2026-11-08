"""Build a Smart Tips KH short video (1080x1920) from a JSON spec.

Usage: python3 generator/smarttips/build_short.py content/smarttips/SPEC.json videos/OUT.mp4 [SEED]

Spec format:
{
  "topic": "chip text top-right",
  "scenes": [
    {"icon": "battery", "icon_args": {"label": "5%"}, "main": "line1\\nline2", "sub": "...",
     "number": 1, "accent": "yellow|white", "glow": "cyan|yellow|red", "note": "small note", "pill": "+ Follow",
     "seconds": 7}
  ]
}
Icons: see ICONS below. Keep each "main" to <= ~22 Khmer chars per line, max 2 lines.
"""
import sys, os, json, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, ".."))
from stk import *
from music import make_music


def icon_shield(d, cx, cy):
    d.polygon([(cx, cy - 250), (cx + 210, cy - 170), (cx + 190, cy + 60), (cx, cy + 250), (cx - 190, cy + 60), (cx - 210, cy - 170)], fill=CYAN)
    d.polygon([(cx, cy - 200), (cx + 160, cy - 140), (cx + 145, cy + 45), (cx, cy + 195), (cx - 145, cy + 45), (cx - 160, cy - 140)], fill=PANEL)
    d.line([(cx - 80, cy), (cx - 15, cy + 70), (cx + 95, cy - 70)], fill=YELLOW, width=30)

def icon_warning(d, cx, cy):
    d.polygon([(cx, cy - 240), (cx + 250, cy + 200), (cx - 250, cy + 200)], fill=YELLOW)
    d.rounded_rectangle([cx - 22, cy - 100, cx + 22, cy + 70], radius=12, fill=NAVY1)
    d.ellipse([cx - 26, cy + 110, cx + 26, cy + 162], fill=NAVY1)

def icon_news(d, cx, cy):
    d.rounded_rectangle([cx - 250, cy - 210, cx + 250, cy + 210], radius=30, fill=WHITE)
    d.rounded_rectangle([cx - 210, cy - 170, cx + 210, cy - 100], radius=12, fill=NAVY1)
    d.rounded_rectangle([cx - 210, cy - 70, cx - 10, cy + 160], radius=12, fill=CYAN)
    for i in range(5):
        y = cy - 60 + i * 50
        d.rounded_rectangle([cx + 20, y, cx + 210, y + 20], radius=10, fill=MUTED)

def icon_big_text(d, cx, cy, text="AI", color=None):
    f = font(260, "Bold"); tw = d.textlength(text, font=f)
    d.text((cx - tw / 2, cy - 200), text, font=f, fill=color or YELLOW)

ICONS = {
    "phone": icon_phone, "chip": icon_brain_chip, "feed": icon_feed, "map": icon_map, "chat": icon_chat,
    "battery": icon_battery, "timer": icon_timer, "moon": icon_moon, "apps": icon_apps,
    "doc_before_after": icon_before_after_doc, "phone_over_paper": icon_phone_over_paper, "plus_scan": icon_plus_scan,
    "camera_scan": icon_camera_scan, "send_pdf": icon_send_pdf, "bad_chat": icon_bad_chat, "short_prompt": icon_short_prompt,
    "four_chips": icon_four_chips, "highlight_line": icon_highlight_line, "chat_before_after": icon_before_after_chat,
    "logo": icon_logo, "shield": icon_shield, "warning": icon_warning, "news": icon_news, "big_text": icon_big_text,
}
COLORS = {"yellow": YELLOW, "white": WHITE, "cyan": CYAN, "red": RED}
ICON_Y = 700


def render_scene(path, topic, sc, seed):
    img = base(seed)
    glow(img, CX, ICON_Y, 300, COLORS.get(sc.get("glow", "cyan"), CYAN), 60)
    d = ImageDraw.Draw(img)
    header(d, topic)
    if sc.get("number"): badge(d, 150, 380, sc["number"])
    fn = ICONS[sc["icon"]]
    fn(d, CX, ICON_Y, **sc.get("icon_args", {}))
    y = center_text(d, 1060, sc["main"], font(84, "Bold"), COLORS.get(sc.get("accent", "white"), WHITE))
    y = center_text(d, y + 30, sc.get("sub", ""), font(54, "Regular"), MUTED)
    pill = sc.get("pill")
    if pill:
        f = font(58, "Bold"); tw = d.textlength(pill, font=f)
        py = max(y + 40, 1400)
        d.rounded_rectangle([CX - tw / 2 - 60, py, CX + tw / 2 + 60, py + 115], radius=58, fill=RED)
        d.text((CX - tw / 2, py + 18), pill, font=f, fill=WHITE)
    if sc.get("note"):
        center_text(d, 1530 if pill else 1470, sc["note"], font(40, "Regular"), (100, 116, 139))
    img.convert("RGB").save(path)


def build(spec, outp, seed=0, music=True):
    tmp = tempfile.mkdtemp()
    scenes = spec["scenes"]; durs = [float(s["seconds"]) for s in scenes]; X = 0.5
    clips = []
    for i, sc in enumerate(scenes):
        png = f"{tmp}/s{i}.png"; render_scene(png, spec["topic"], sc, seed * 10 + i)
        n = int(round((durs[i] + (X if i < len(scenes) - 1 else 0)) * 30))
        c = f"{tmp}/c{i}.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", png, "-filter_complex",
            f"[0]scale=2160:3840,zoompan=z='min(1+0.0006*on,1.05)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s=1080x1920:fps=30,format=yuv420p",
            "-frames:v", str(n), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", c], check=True)
        clips.append(c)
    total = sum(durs)
    if music:
        wav = f"{tmp}/m.wav"; make_music(wav, total, seed); audio = ["-i", wav]
    else:
        audio = ["-f", "lavfi", "-t", str(total), "-i", "anullsrc=r=44100:cl=stereo"]
    fc, prev, off = [], "0", 0.0
    for i in range(1, len(clips)):
        off += durs[i - 1]
        tr = "fade" if i == len(clips) - 1 else "slideleft"
        fc.append(f"[{prev}][{i}]xfade=transition={tr}:duration={X}:offset={off:.2f}[v{i}]"); prev = f"v{i}"
    fc[-1] = fc[-1][: -len(f"[{prev}]")] + ",format=yuv420p[v]"
    os.makedirs(os.path.dirname(os.path.abspath(outp)), exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *sum([["-i", c] for c in clips], []), *audio,
        "-filter_complex", ";".join(fc), "-map", "[v]", "-map", f"{len(clips)}:a", "-t", f"{total:.2f}",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-r", "30", "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart", outp], check=True)
    # one preview frame per scene for checking Khmer text
    prev_png = os.path.splitext(outp)[0] + "_preview.png"
    ims = [Image.open(f"{tmp}/s{i}.png").resize((216, 384)) for i in range(len(scenes))]
    sheet = Image.new("RGB", (216 * len(ims), 384)); [sheet.paste(im, (i * 216, 0)) for i, im in enumerate(ims)]
    sheet.save(prev_png)
    return outp, prev_png


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    print(*build(spec, sys.argv[2], seed))
