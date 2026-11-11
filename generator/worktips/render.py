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

def main():
    spec = json.load(open(sys.argv[1]))
    if sys.argv[2] == "--preview":
        out = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), "_preview"); os.makedirs(out, exist_ok=True)
        _, paths = asyncio.run(frames(spec, [float(x) for x in sys.argv[3:]], out))
        print("\n".join(paths)); return
    out_mp4, seed = sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 0
    tmp = tempfile.mkdtemp()
    total, _ = asyncio.run(frames(spec, None, tmp))
    from music import make_music
    make_music(os.path.join(tmp, "m.wav"), total, seed=seed)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i", os.path.join(tmp, "f%05d.jpg"), "-i", os.path.join(tmp, "m.wav"),
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS),
                    "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out_mp4], check=True)
    shutil.rmtree(tmp); print(out_mp4, f"{total:.1f}s")

if __name__ == "__main__":
    main()
