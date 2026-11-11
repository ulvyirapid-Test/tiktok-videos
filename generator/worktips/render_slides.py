"""Render a Work-Tips photo carousel (JPG slides) with the same engine as the videos.

Usage: python3 generator/worktips/render_slides.py content/worktips/SPEC.json carousels/OUT_DIR
Spec: same as render.py but with "slides" instead of "scenes" (each slide is a scene; it is captured fully drawn).
"""
import asyncio, json, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import frames

spec = json.load(open(sys.argv[1])); out = os.path.abspath(sys.argv[2]); os.makedirs(out, exist_ok=True)
spec["scenes"] = spec.pop("slides")
times, t = [], 0.0
for s in spec["scenes"]:
    times.append(t + s["dur"] * 0.7); t += s["dur"]
_, paths = asyncio.run(frames(spec, times, out))
for i, p in enumerate(paths):
    shutil.move(p, os.path.join(out, f"{i+1:02d}.jpg"))
print("\n".join(sorted(os.listdir(out))))
