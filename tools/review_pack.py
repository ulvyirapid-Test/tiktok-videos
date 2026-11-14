"""Build an evidence pack for an independent reviewer: script (narration, on-screen text, TTS text, caption, audio stats) + contact sheets every 3 s.
Usage: python3 tools/review_pack.py OUT_DIR name1 [name2 ...]   (names = spec basenames in content/worktips and videos/)"""
import json, os, subprocess, sys
sys.path.insert(0, 'generator/worktips'); from render import khmerize
SKIP = {'type','bg','dur','speak','talk','stagger','uAt','uDur','aDur','fAt','fDur','rAt','tDur','tAt','toastAt','size','fs','h','c','style','neutral','small'}
def txt(v):
    if isinstance(v, dict): return '; '.join(f"{k}={txt(x)}" for k, x in v.items() if k not in SKIP)
    if isinstance(v, list): return ' | '.join(txt(x) for x in v)
    return str(v).replace('\n', ' / ')
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
for n in sys.argv[2:]:
    sp = json.load(open(f'content/worktips/{n}.json')); V = f'videos/{n}.mp4'
    dur = float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',V]).decode())
    a = subprocess.run(['ffmpeg','-i',V,'-af','silencedetect=noise=-35dB:d=1.2,volumedetect','-vn','-f','null','-'], capture_output=True, text=True).stderr
    mv = [l.split('] ')[1] for l in a.splitlines() if 'mean_volume' in l or 'max_volume' in l]
    L = [f"# {n} — series: {sp['series']}", f"AUDIO: duration {dur:.1f}s · silent gaps >1.2s: {a.count('silence_start')} · {' · '.join(mv)} · AI voice km-KH-PisethNeural · music ducked (0.22 vs voice 1.6)", "", f"## Caption\n{sp['caption']}", ""]
    for i, s in enumerate(sp['scenes'], 1):
        L += [f"## Scene {i} [{s['type']}, background={s.get('bg','navy')}]", "ON-SCREEN: " + txt({k: v for k, v in s.items() if k not in SKIP}),
              "NARRATION: " + s['speak'], "TTS TEXT (English terms respelled in Khmer): " + khmerize(s['speak']), ""]
    open(f'{out}/{n}_script.md', 'w').write('\n'.join(L))
    fd = f'{out}/_{n}'; os.makedirs(fd, exist_ok=True)
    subprocess.run(['ffmpeg','-v','error','-y','-i',V,'-vf','fps=1/3,scale=360:-1',f'{fd}/f%03d.jpg'], check=True)
    fr = sorted(os.listdir(fd))
    for k in range(0, len(fr), 8):
        ch = fr[k:k+8]; ins = sum([['-i', f'{fd}/{x}'] for x in ch], [])
        flt = ''.join(f'[{j}]' for j in range(len(ch))) + f'hstack={len(ch)}' if len(ch) > 1 else '[0]copy'
        subprocess.run(['ffmpeg','-v','error','-y',*ins,'-filter_complex',flt,f'{out}/{n}_sheet{k//8+1:02d}_t{k*3}-{(k+len(ch)-1)*3}s.jpg'], check=True)
    subprocess.run(['rm','-rf',fd])
print('ok')
