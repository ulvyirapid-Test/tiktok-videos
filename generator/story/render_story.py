#!/usr/bin/env python3
"""Render a Khmer AI-story video (1080x1920) from a JSON spec.

    python3 generator/story/render_story.py content/stories/ID.json [--out videos/stories] [--no-images] [--preview]

Pipeline (all free):
  * narration  : Microsoft Edge neural TTS (km-KH voices) via `edge-tts`
  * images     : Pollinations.ai (FLUX) — one image per scene; set POLLINATIONS_TOKEN for higher limits
  * motion     : FFmpeg zoompan (Ken Burns) + crossfades
  * subtitles  : ASS burned with libass (correct Khmer shaping), Kantumruy Pro font
  * music      : original generator in generator/music.py (no copyright issues)
Outputs: OUT/ID.mp4, OUT/ID_cover.jpg, OUT/ID.json (meta: duration, caption, images_ok)
"""
import argparse, asyncio, json, os, subprocess, sys, time, urllib.parse, urllib.request, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "generator"))
from music import make_music  # noqa: E402

W, H, FPS = 1080, 1920, 30
XF = 0.45          # crossfade seconds
LEAD, TAIL = 0.25, 0.55   # silence before / after each narration clip
SR = 44100
FONTS = os.path.join(ROOT, "fonts")
# Distro FFmpeg is built with HarfBuzz; static builds often are not -> broken Khmer shaping.
FF = "/usr/bin/ffmpeg" if os.path.exists("/usr/bin/ffmpeg") else "ffmpeg"

# Inside Claude's sandbox the network goes through a proxy with its own CA.
_CA = os.path.expanduser("~/.ccr/ca-bundle.crt")
if os.path.exists(_CA):
    import certifi
    certifi.where = lambda: _CA


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit("FFMPEG FAILED:\n" + " ".join(cmd) + "\n" + r.stderr[-3000:])
    return r


def duration(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", path]).strip())


# ---------------------------------------------------------------- narration
def tts(text, voice, rate, path):
    import edge_tts
    for attempt in range(5):
        try:
            asyncio.run(edge_tts.Communicate(text, voice, rate=rate).save(path))
            if os.path.getsize(path) > 1000:
                return
        except Exception as e:  # network hiccup
            print(f"  tts retry {attempt + 1}: {e}")
        time.sleep(3 + attempt * 3)
    sys.exit("TTS failed: " + text[:40])


def load_wav_mono(mp3, tmp):
    wav = tmp + ".wav"
    run([FF, "-y", "-v", "error", "-i", mp3, "-ac", "1", "-ar", str(SR), wav])
    with wave.open(wav) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return a


# ---------------------------------------------------------------- images
def build_prompt(spec, scene):
    p = scene["prompt"]
    for k, v in spec.get("characters", {}).items():
        p = p.replace(k, v)
    return p + ", " + scene.get("style", spec.get("style", ""))


UNSAFE = {"FEMALE_BREAST_EXPOSED": .25, "FEMALE_GENITALIA_EXPOSED": .2, "MALE_GENITALIA_EXPOSED": .2,
          "BUTTOCKS_EXPOSED": .3, "ANUS_EXPOSED": .2}
_detector = None


def is_safe(path):
    """Family-friendly check with NudeNet; also rejects bikini-like shots (exposed belly next to a female face)."""
    global _detector
    try:
        from nudenet import NudeDetector
    except ImportError:
        print("  WARNING: nudenet not installed — safety check skipped")
        return True
    _detector = _detector or NudeDetector()
    found = {d["class"]: d["score"] for d in _detector.detect(path)}
    bad = [k for k, th in UNSAFE.items() if found.get(k, 0) >= th]
    if found.get("BELLY_EXPOSED", 0) >= .5 and found.get("FACE_FEMALE", 0) >= .3:
        bad.append("BELLY_EXPOSED")
    if bad:
        print(f"  rejected (unsafe): {bad}")
    return not bad


def fetch_image(prompt, seed, path):
    """Try up to 3 seeds; each candidate must pass the safety check. Returns False -> placeholder."""
    if os.path.exists(path) and os.path.getsize(path) > 20000:
        return True
    from PIL import Image
    import io
    headers = {"User-Agent": "tiktok-story-generator/1.0"}
    tok = os.environ.get("POLLINATIONS_TOKEN")
    if tok:
        headers["Authorization"] = "Bearer " + tok
    for k in range(3):
        q = urllib.parse.quote(prompt[:1800], safe="")
        url = (f"https://image.pollinations.ai/prompt/{q}?width={W}&height={H}&seed={seed + 1000 * k}"
               f"&model=flux&nologo=true&enhance=false&safe=true")
        for attempt in range(6):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=180) as r:
                    data = r.read()
                im = Image.open(io.BytesIO(data)).convert("RGB")
                if im.width < 500:
                    raise ValueError(f"tiny image {im.size}")
                break
            except Exception as e:
                print(f"  image retry {attempt + 1}: {e}")
                time.sleep(16 + attempt * 10)   # anonymous limit ≈ 1 request / 15 s
        else:
            return False
        # cut the bottom strip (free-tier logo sits there), then fill the frame
        im = im.crop((0, 0, im.width, int(im.height * 0.93)))
        cover_resize(im, W, H).save(path, quality=94)
        if is_safe(path):
            return True
        os.remove(path)
        time.sleep(15)
    return False


def cover_resize(im, w, h):
    from PIL import Image
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    l, t = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((l, t, l + w, t + h))


def placeholder(path, i):
    """Used only when image generation fails or --no-images: a soft night-sky gradient."""
    from PIL import Image
    y = np.linspace(0, 1, H)[:, None, None]
    top = np.array([[[18, 24, 58]]]) if i % 2 else np.array([[[60, 30, 70]]])
    bot = np.array([[[200, 120, 60]]])
    arr = (top * (1 - y) + bot * y) * np.ones((1, W, 1))
    Image.fromarray(arr.astype(np.uint8)).save(path, quality=90)


# ---------------------------------------------------------------- motion
def kenburns(img, dur, motion, out):
    n = max(2, round(dur * FPS))
    z0, z1 = 1.0, 1.13
    pan = 1.12
    cx, cy = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    t = f"(on/{n - 1})"
    ease = f"(0.5-0.5*cos(PI*{t}))"
    if motion == "out":
        z, x, y = f"{z1}-{z1 - z0}*{ease}", cx, cy
    elif motion == "left":
        z, x, y = str(pan), f"(iw-iw/zoom)*(1-{ease})", cy
    elif motion == "right":
        z, x, y = str(pan), f"(iw-iw/zoom)*{ease}", cy
    elif motion == "up":
        z, x, y = str(pan), cx, f"(ih-ih/zoom)*(1-{ease})"
    else:  # in
        z, x, y = f"{z0}+{z1 - z0}*{ease}", cx, cy
    vf = (f"scale={W * 2}:{H * 2}:flags=lanczos,zoompan=z='{z}':x='{x}':y='{y}':d={n}:s={W}x{H}:fps={FPS},"
          f"eq=contrast=1.04:saturation=1.08,vignette=PI/5,format=yuv420p")
    run([FF, "-y", "-v", "error", "-i", img, "-vf", vf, "-frames:v", str(n),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", out])


# ---------------------------------------------------------------- subtitles
def ass_time(t):
    t = max(0, t)
    h, m = int(t // 3600), int(t % 3600 // 60)
    return f"{h}:{m:02d}:{t % 60:05.2f}"


def write_ass(path, label, events, total, title=None):
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Kantumruy Pro,76,&H00FFFFFF,&H00FFFFFF,&H00101010,&H96000000,1,0,0,0,100,100,0,0,1,5,3,2,70,170,560,1
Style: Label,Kantumruy Pro,50,&H0040D8FF,&H00FFFFFF,&H00101010,&H80000000,1,0,0,0,100,100,0,0,1,3,2,8,70,170,150,1
Style: Title,Kantumruy Pro,112,&H0040D8FF,&H00FFFFFF,&H00101010,&H80000000,1,0,0,0,100,100,0,0,1,7,4,5,70,170,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [f"Dialogue: 0,{ass_time(0)},{ass_time(total)},Label,,0,0,0,,{label}"]
    if title:
        lines.append(f"Dialogue: 1,{ass_time(0)},{ass_time(total)},Title,,0,0,0,,{title}")
    for s, e, text in events:
        lines.append(f"Dialogue: 2,{ass_time(s)},{ass_time(e)},Sub,,0,0,0,,{{\\fad(120,120)}}{text}")
    open(path, "w", encoding="utf-8").write(head + "\n".join(lines) + "\n")


def sub_events(lines, start, length):
    """Spread subtitle lines over the narration window, proportional to their length."""
    weights = [max(4, len(l.replace(" ", ""))) for l in lines]
    tot, t, ev = sum(weights), start, []
    for l, w in zip(lines, weights):
        d = length * w / tot
        ev.append((t, t + d - 0.02, l))
        t += d
    return ev


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--out", default=os.path.join(ROOT, "videos", "stories"))
    ap.add_argument("--work", default=os.path.join(ROOT, ".work"))
    ap.add_argument("--no-images", action="store_true", help="use placeholder backgrounds (offline test)")
    ap.add_argument("--preview", action="store_true", help="also write a contact sheet of frames")
    a = ap.parse_args()

    spec = json.load(open(a.spec, encoding="utf-8"))
    sid = spec["id"]
    work = os.path.join(a.work, sid)
    os.makedirs(work, exist_ok=True)
    os.makedirs(a.out, exist_ok=True)
    scenes = spec["scenes"]

    # 1) narration -> scene durations
    voices, durs = [], []
    for i, s in enumerate(scenes):
        mp3 = os.path.join(work, f"v{i:02d}.mp3")
        if not (os.path.exists(mp3) and os.path.getsize(mp3) > 1000):
            tts(s["speak"], spec.get("voice", "km-KH-SreymomNeural"), spec.get("rate", "-5%"), mp3)
        v = load_wav_mono(mp3, os.path.join(work, f"v{i:02d}"))
        voices.append(v)
        durs.append(LEAD + len(v) / SR + TAIL + (XF if i < len(scenes) - 1 else 1.2))
        print(f"scene {i:2d}: voice {len(v) / SR:5.1f}s")

    # 2) images
    images_ok = 0
    for i, s in enumerate(scenes):
        img = os.path.join(work, f"img{i:02d}.jpg")
        ok = False
        if not a.no_images:
            print(f"image {i}…", flush=True)
            ok = fetch_image(build_prompt(spec, s), spec.get("image_seed", 1000) + i, img)
            if i < len(scenes) - 1:
                time.sleep(2 if os.environ.get("POLLINATIONS_TOKEN") else 15)
        if not ok:
            placeholder(img, i)
        images_ok += ok

    # 3) Ken Burns clips
    clips = []
    for i, s in enumerate(scenes):
        c = os.path.join(work, f"c{i:02d}.mp4")
        kenburns(os.path.join(work, f"img{i:02d}.jpg"), durs[i], s.get("motion", "in"), c)
        clips.append(c)

    # 4) timeline: scene k starts at offset_k (crossfades overlap by XF)
    offsets, t = [], 0.0
    for d in durs:
        offsets.append(t)
        t += d - XF
    total = offsets[-1] + durs[-1]

    # 5) audio: voice + ducked original music
    n = int(total * SR) + SR
    voice = np.zeros(n, np.float32)
    events = []
    for i, v in enumerate(voices):
        st = offsets[i] + (XF if i else 0) * 0.5 + LEAD
        k = int(st * SR)
        voice[k:k + len(v)] += v[: n - k]
        events += sub_events(scenes[i].get("subs") or [scenes[i]["speak"]], st, len(v) / SR)
    mus_path = os.path.join(work, "music.wav")
    make_music(mus_path, total + 1, seed=spec.get("music_seed", 0))
    with wave.open(mus_path) as w:
        raw = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        if w.getnchannels() == 2:
            raw = raw.reshape(-1, 2).mean(1)
    mus = np.zeros(n, np.float32)
    mus[: min(n, len(raw))] = raw[:n]
    env = np.convolve(np.abs(voice), np.ones(SR // 5) / (SR // 5), mode="same")
    duck = np.where(env > 0.01, 0.10, 0.22).astype(np.float32)
    duck = np.convolve(duck, np.ones(SR // 4) / (SR // 4), mode="same")
    mix = voice * 1.0 + mus / (np.abs(mus).max() + 1e-6) * duck
    fade = int(1.5 * SR)
    end = int(total * SR)
    mix = mix[:end]
    mix[-fade:] *= np.linspace(1, 0, fade)
    mix = np.clip(mix / max(1.0, np.abs(mix).max() / 0.95), -1, 1)
    wav_path = os.path.join(work, "mix.wav")
    with wave.open(wav_path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())

    # 6) subtitles + crossfade graph
    ass = os.path.join(work, "subs.ass")
    write_ass(ass, spec.get("label", spec.get("series", "")), events, total)
    inputs, graph, last = [], [], "[0:v]"
    for c in clips:
        inputs += ["-i", c]
    for i in range(1, len(clips)):
        out = f"[x{i}]"
        graph.append(f"{last}[{i}:v]xfade=transition=fade:duration={XF}:offset={offsets[i]:.3f}{out}")
        last = out
    esc = ass.replace("\\", "/").replace(":", "\\:")
    graph.append(f"{last}ass='{esc}':fontsdir='{FONTS}':shaping=complex,fade=t=out:st={total - 0.8:.2f}:d=0.8[v]")
    mp4 = os.path.join(a.out, f"{sid}.mp4")
    run([FF, "-y", "-v", "error", *inputs, "-i", wav_path, "-filter_complex", ";".join(graph),
         "-map", "[v]", "-map", f"{len(clips)}:a", "-c:v", "libx264", "-preset", "medium", "-crf", "21",
         "-maxrate", "6M", "-bufsize", "12M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
         "-t", f"{total:.2f}", "-movflags", "+faststart", mp4])

    # 7) cover
    ci = spec.get("cover_scene", 0)
    cass = os.path.join(work, "cover.ass")
    write_ass(cass, spec.get("label", ""), [], 1, title=spec.get("cover_title"))
    cesc = cass.replace("\\", "/").replace(":", "\\:")
    cover = os.path.join(a.out, f"{sid}_cover.jpg")
    run([FF, "-y", "-v", "error", "-i", os.path.join(work, f"img{ci:02d}.jpg"), "-vf",
         f"ass='{cesc}':fontsdir='{FONTS}':shaping=complex", "-frames:v", "1", "-q:v", "2", cover])

    if a.preview:
        times = [offsets[i] + durs[i] / 2 for i in range(len(scenes))]
        sel = "+".join(f"between(t\\,{x:.2f}\\,{x + 0.04:.2f})" for x in times)
        run([FF, "-y", "-v", "error", "-i", mp4, "-vf",
             f"select='{sel}',scale=270:480,tile=7x{(len(times) + 6) // 7}", "-frames:v", "1",
             os.path.join(a.work, f"{sid}_preview.jpg")])

    meta = {"id": sid, "duration": round(total, 1), "scenes": len(scenes), "images_ok": images_ok,
            "caption": spec.get("caption", ""), "video": f"videos/stories/{sid}.mp4",
            "cover": f"videos/stories/{sid}_cover.jpg"}
    json.dump(meta, open(os.path.join(a.out, f"{sid}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps(meta, ensure_ascii=False))


if __name__ == "__main__":
    main()
