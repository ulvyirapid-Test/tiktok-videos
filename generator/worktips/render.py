"""Render a Work-Tips animated short (1080x1920 MP4) from a JSON spec with engine.html.

Usage:
  python3 generator/worktips/render.py content/worktips/SPEC.json videos/OUT.mp4 [music_seed]
  python3 generator/worktips/render.py content/worktips/SPEC.json --preview t1 t2 ...   (writes PNGs next to OUT dir)
"""
import asyncio, base64, json, os, shutil, subprocess, sys, tempfile
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
FPS = 30

async def frames(spec, times, out_dir):
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--allow-file-access-from-files"])
        pg = await b.new_page(viewport={"width": 1080, "height": 1920})
        await pg.goto("file://" + os.path.join(HERE, "engine.html"))
        await pg.evaluate("document.fonts.ready")
        total = await pg.evaluate("s => setup(s)", spec)
        await pg.evaluate("document.fonts.ready")
        if times is None: times = [i / FPS for i in range(int(total * FPS))]
        paths = []
        for i, t in enumerate(times):
            await pg.evaluate(f"draw({t})")
            path = os.path.join(out_dir, f"f{i:05d}.jpg")
            await pg.screenshot(path=path, type="jpeg", quality=88)
            paths.append(path)
        await b.close()
        return total, paths

VOFF = 0.15  # voice starts this many seconds into each scene (matches engine.html)
TAIL = 0.55  # pause after each narration line before the next scene

# English words the Khmer neural voice mispronounces -> Khmer spelling (screen text keeps English)
PRON = [("Caps Lock", "ខេបស៍ ឡុក"), ("GHz", "ជីហ្គាហឺត"), ("UEFI", "យូ អ៊ី អេហ្វ អាយ"), ("BIOS", "បាយអូស"), ("POST", "ផូស"),
        ("PSU", "ភី អេស យូ"), ("SSD", "អេស អេស ឌី"), ("HDD", "អេច ឌី ឌី"), ("ROM", "រ៉ូម"), ("Cores", "ខរ"), ("Core", "ខរ"),
        ("Flash", "ហ្វ្លាស"), ("Save", "សេវ"), ("Icon", "អាយខុន"), ("Taskbar", "ថាសបា"), ("Desktop", "ដេសថប"), ("Motherboard", "ម៉ាទ័របត"), ("Controller", "ខុនត្រូលល័រ"), ("Keyboard", "ឃីបត"),
        ("Layout", "ឡេអៅ"), ("Unicode", "យូនីកូដ"), ("Windows", "វីនដូ"), ("Monitor", "ម៉ូនីទ័រ"), ("Binary", "បាយណារី"),
        ("Driver", "ដ្រាយវ័រ"), ("Switch", "ស្វីច"), ("Chrome", "ក្រូម"), ("Shift", "ស៊ីហ្វ"), ("Chip", "ឈីប"), ("Byte", "បៃ"),
        ("Font", "ហ្វុន"), ("Word", "វើដ"), ("HDMI", "អេចឌីអេមអាយ"), ("USB", "យូអេសប៊ី"), ("CPU", "ស៊ីភីយូ"),
        ("GPU", "ជីភីយូ"), ("RAM", "រ៉េម"), ("Google Sheet", "ហ្គូហ្គល ស៊ីត"), ("Apps Script", "អែប ស្គ្រីប"), ("BotFather", "បត ហ្វាដឺ"),
        ("Telegram", "តេឡេក្រាម"), ("Excel", "អ៊ិចសែល"), ("Prompt", "ផ្រមត៍"), ("Caption", "ខេបសិន"),
        ("Comment", "ខមមិន"), ("Follow", "ហ្វលឡូ"), ("Email", "អ៊ីមែល"), ("email", "អ៊ីមែល"), ("Copy", "ខូពី"),
        ("Paste", "ផេស"), ("Enter", "អិនទ័រ"), ("Token", "តូខិន"), ("Trigger", "ទ្រីហ្គ័រ"), ("Part 2", "ភាគទីពីរ"),
        ("Control", "ខុនត្រូល"), ("SUMIF", "សាំ អ៊ីហ្វ"), ("VLOOKUP", "វី លុកអាប់"), ("COUNTIF", "ខោន អ៊ីហ្វ"),
        ("Bot", "បត"), ("Sheet", "ស៊ីត"), ("AI", "អេអាយ"), ("IF", "អ៊ីហ្វ")]

def khmerize(text):
    import re
    for en, km in PRON:
        text = re.sub(r"(?<![A-Za-z])" + re.escape(en) + r"(?![A-Za-z])", km, text)
    return text

def anim_floor(s):
    """Minimum scene length so on-screen animations finish."""
    if s["type"] == "chat":
        ua, ud, ad = s.get("uAt", 0.5), s.get("uDur", 2.2), s.get("aDur", 3.2)
        return ua + ud + 0.5 + ad + 1.0
    if s["type"] in ("steps", "flow"):
        n = len(s.get("items", s.get("nodes", [])))
        return 1.0 + n * s.get("stagger", 0.3) * (2 if s["type"] == "flow" else 1) + 1.0
    if s["type"] == "phone": return 1.5 + len(s["msgs"]) * s.get("gap", 1.0)
    if s["type"] == "bits": return 4.5
    return 3.5

def synth_voices(spec, tmp):
    """Generate one Khmer TTS clip per scene that has `speak`; stretch scene durations to fit the voice."""
    import edge_tts
    os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    voice, rate = spec.get("voice", "km-KH-PisethNeural"), spec.get("rate", "-5%")
    clips, t0 = [], 0.0
    for i, s in enumerate(spec["scenes"]):
        if s.get("speak"):
            path = os.path.join(tmp, f"v{i:02d}.mp3")
            asyncio.run(edge_tts.Communicate(khmerize(s["speak"]), voice, rate=rate, proxy=proxy).save(path))
            d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).decode())
            s["talk"] = round(d, 2)
            s["dur"] = round(max(anim_floor(s), VOFF + d + TAIL), 2)
            clips.append((t0 + VOFF, path))
        t0 += s["dur"]
    return clips

def mix_audio(clips, music, total, out):
    """Voice clips at full volume, music ducked underneath."""
    args, parts = ["ffmpeg", "-y", "-v", "error", "-i", music], []
    for k, (start, path) in enumerate(clips, 1):
        args += ["-i", path]; ms = int(start * 1000)
        parts.append(f"[{k}:a]aresample=44100,adelay={ms}|{ms},volume=1.6[v{k}]")
    vl = "".join(f"[v{k}]" for k in range(1, len(clips) + 1))
    fc = ";".join(parts + [f"[0:a]volume=0.22[m]", f"[m]{vl}amix=inputs={len(clips)+1}:normalize=0:duration=first,atrim=0:{total:.2f}[a]"])
    subprocess.run(args + ["-filter_complex", fc, "-map", "[a]", "-ac", "2", out], check=True)

def main():
    spec = json.load(open(sys.argv[1]))
    if sys.argv[2] == "--preview":
        out = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), "_preview"); os.makedirs(out, exist_ok=True)
        _, paths = asyncio.run(frames(spec, [float(x) for x in sys.argv[3:]], out))
        print("\n".join(paths)); return
    out_mp4, seed = sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 0
    tmp = tempfile.mkdtemp()
    clips = synth_voices(spec, tmp) if any(s.get("speak") for s in spec["scenes"]) else []
    total, _ = asyncio.run(frames(spec, None, tmp))
    from music import make_music
    make_music(os.path.join(tmp, "music.wav"), total, seed=seed)
    if clips: mix_audio(clips, os.path.join(tmp, "music.wav"), total, os.path.join(tmp, "m.wav"))
    else: shutil.move(os.path.join(tmp, "music.wav"), os.path.join(tmp, "m.wav"))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i", os.path.join(tmp, "f%05d.jpg"), "-i", os.path.join(tmp, "m.wav"),
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS),
                    "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out_mp4], check=True)
    shutil.rmtree(tmp); print(out_mp4, f"{total:.1f}s")

if __name__ == "__main__":
    main()
