"""Render a Work-Tips animated short (1080x1920 MP4) from a JSON spec with engine.html.

Usage:
  python3 generator/worktips/render.py content/worktips/SPEC.json videos/OUT.mp4 [music_seed]
  python3 generator/worktips/render.py content/worktips/SPEC.json --preview t1 t2 ...   (writes PNGs next to OUT dir)
"""
import asyncio, base64, json, re, os, shutil, subprocess, sys, tempfile
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
PRON = [("COUNTIFS", "ខោនធ៍ អ៊ីហ្វ អេស"), ("SUMIFS", "សាំ អ៊ីហ្វ អេស"), ("IFERROR", "អ៊ីហ្វ អ៊ែរើ"), ("IFNA", "អ៊ីហ្វ អិនអេ"), ("XLOOKUP", "អ៊ិចស៍ លុកអាប់"), ("IFS", "អ៊ីហ្វ អេស"), ("FALSE", "ហ្វលស៍"), ("TRUE", "ទ្រូ"), ("AND", "អែន"), ("OR", "អ័រ"), ("Google Sheets", "ហ្គូហ្គល ស៊ីត"), ("Microsoft 365", "ម៉ាយក្រូសូហ្វ ស្រី ស៊ិច ហ្វាយ"), ("Microsoft", "ម៉ាយក្រូសូហ្វ"), ("Playlist", "ផ្លេលីស"), ("Price", "ប្រាយស៍"), ("Sales", "សេលស៍"), ("Channel", "ឆានែល"), ("TikTok", "ធិកតុក"), ("PDF", "ភីឌីអែហ្វ"), ("John McCarthy", "ចន ម៉ាកខាធី"), ("Google Translate", "ហ្គូហ្គល ត្រេនស្លេត"), ("Google Drive", "ហ្គូហ្គល ដ្រាយ"), ("Artificial", "អាធីហ្វីសៀល"),
        ("Intelligence", "អ៊ីនថេលីជិន"), ("Dartmouth", "ដាតម៉ោត"), ("ELIZA", "អេលីហ្សា"), ("Chatbot", "ឆាតបូត"), ("Chat", "ឆាត"), ("Robot", "រ៉ូបូត"),
        ("Hallucination", "ហាលូស៊ីណេសិន"), ("Facebook", "ហ្វេសប៊ុក"), ("Post", "ផូស្ត៍"), ("Emoji", "អ៊ីម៉ូជី"), ("Hashtag", "ហាសថេក"),
        ("Skills", "ស្គីល"), ("Skill", "ស្គីល"), ("Projects", "ប្រូជេក"), ("Project", "ប្រូជេក"), ("Connectors", "ខនណិចទ័រ"), ("Connect", "ខនណិច"),
        ("Artifacts", "អាធីហ្វេក"), ("Artifact", "អាធីហ្វេក"), ("Design", "ឌីហ្សាញ"), ("Anthropic", "អេនត្រូពិក"), ("Sign in", "សាញ អ៊ីន"),
        ("Notion", "ណូសិន"), ("Canva", "ខេនវ៉ា"), ("PowerPoint", "ផៅវ័រផញ"), ("Export", "អិចស្ពត"), ("Share", "ស្ហែរ"), ("Save", "សេវ"), ("Gemini", "ជេមីណៃ"), ("IMF", "អាយ អឹម អេហ្វ"), ("ILO", "អាយ អិល អូ"), ("WEF", "ដាប់ប៊លយូ អ៊ី អេហ្វ"), ("integrations", "អ៊ីនធីហ្គ្រេសិន"), ("Server", "សឺវើ"), ("Starter", "ស្តាតទ័រ"), ("tab", "ថេប"), ("telegram", "តេឡេក្រាម"), ("bot", "បូត"), ("api", "អេភីអាយ"), ("org", "អ័រ"), ("Chat Model", "ឆាត ម៉ូដែល"), ("Activate", "អាក់ធីវេត"), ("Gmail", "ជីមែល"), ("API", "អេភីអាយ"), ("MCP", "អឹម ស៊ី ភី"), ("Execute workflow", "អិចសេគ្យូត វើកហ្វ្លូ"), ("HTTP Request", "អេចធីធីភី រីក្វេស"), ("Select all", "ស៊ីឡិច អល"), ("Continue", "ខនធីនីវ"), ("Day timer", "ដេ ថាយម័រ"), ("Run once", "រ៉ាន់ វ៉ាន់ស៍"), ("Run an agent", "រ៉ាន់ អាន អេជិន"),
        ("Self-host", "សែលហូស្ត៍"), ("executions", "អិចសេគ្យូសិន"), ("Router", "រ៉ោទ័រ"), ("Filter", "ហ្វីលទ័រ"), ("Publish", "ផាប់ប្លីស"),
        ("Schedule", "ស្កេជូល"), ("Webhook", "វេបហុក"), ("JavaScript", "ចាវ៉ាស្គ្រីប"), ("Python", "ផៃថុន"), ("Create", "ក្រៀត"), ("ON", "អន"),
        ("Community Edition", "ខមមុយនីធី អេឌីសិន"), ("AI Automation", "អេអាយ អូតូមេសិន"), ("AI Agents", "អេអាយ អេជិន"), ("AI Agent", "អេអាយ អេជិន"),
        ("Automation", "អូតូមេសិន"), ("Agents", "អេជិន"), ("Agent", "អេជិន"), ("n8n", "អិន អេត អិន"), ("Make", "មេក"), ("Module", "ម៉ូឌុល"),
        ("Scenario", "ស៊ីណារីយ៉ូ"), ("Workflow", "វើកហ្វ្លូ"), ("Node", "ណូដ"), ("node", "ណូដ"), ("Memory", "មេម៉ូរី"), ("Instructions", "អ៊ិនស្ត្រាក់សិន"),
        ("Tools", "ធូល"), ("Model", "ម៉ូដែល"), ("credits", "ក្រេឌីត"), ("credit", "ក្រេឌីត"), ("Cloud", "ក្លោដ"), ("Website", "វេបសាយ"), ("Code", "ខូដ"),
        ("Google Sheet", "ហ្គូហ្គល ស៊ីត"), ("Apps Script", "អែប ស្គ្រីប"), ("installable trigger", "ឥនស្តលអេបិល ទ្រីហ្គ័រ"), ("From spreadsheet", "ហ្វ្រំ ស្ព្រេតស៊ីត"), ("Go to project", "ហ្គោ ធូ ប្រូជេក"),
        ("Review permissions", "រីវីវ ភើមីសិន"), ("Time-driven", "ថាយម៍ ដ្រីវិន"), ("Add Trigger", "អែត ទ្រីហ្គ័រ"), ("On edit", "អន អេឌីត"),
        ("notifyOnEdit", "ណូទីហ្វាយ អន អេឌីត"), ("onEdit", "អន អេឌីត"), ("testSend", "តេស សេន"), ("send", "សេន"), ("getUpdates", "ហ្គេត អាប់ដេត"),
        ("Chat ID", "ឆាត អាយឌី"), ("SHD Alert", "អេស អេច ឌី អាឡឺត"), ("SHD", "អេស អេច ឌី"), ("ChatGPT", "ឆាត ជីភីធី"), ("Claude", "ក្លូដ"),
        ("Extensions", "អ៊ិចស្ទេនសិន"), ("Triggers", "ទ្រីហ្គ័រ"), ("Advanced", "អាតវ៉ាន់"), ("Allow", "អាឡៅ"), ("Run", "រ៉ាន់"),
        ("Start", "ស្តាត"), ("start", "ស្តាត"), ("newbot", "ញូបូត"), ("revoke", "រីវូក"), ("username", "យូសឺណេម"), ("Browser", "ប្រោស័រ"),
        ("function", "ហ្វាំងសិន"), ("Delivery", "ដេលីវើរី"), ("Refresh", "រីហ្វ្រេស"), ("Google", "ហ្គូហ្គល"), ("chat", "ឆាត"), ("id", "អាយឌី"),
        ("Caps Lock", "ខេបស៍ ឡុក"), ("GHz", "ជីហ្គាហឺត"), ("UEFI", "យូ អ៊ី អេហ្វ អាយ"), ("BIOS", "បាយអូស"), ("POST", "ផូស"),
        ("PSU", "ភី អេស យូ"), ("SSD", "អេស អេស ឌី"), ("HDD", "អេច ឌី ឌី"), ("ROM", "រ៉ូម"), ("Cores", "ខរ"), ("Core", "ខរ"),
        ("Flash", "ហ្វ្លាស"), ("Save", "សេវ"), ("Icon", "អាយខុន"), ("Taskbar", "ថាសបា"), ("Desktop", "ដេសថប"), ("Motherboard", "ម៉ាទ័របត"), ("Controller", "ខុនត្រូលល័រ"), ("Keyboard", "ឃីបត"),
        ("Layout", "ឡេអៅ"), ("Unicode", "យូនីកូដ"), ("Windows", "វីនដូ"), ("Monitor", "ម៉ូនីទ័រ"), ("Binary", "បាយណារី"),
        ("Driver", "ដ្រាយវ័រ"), ("Switch", "ស្វីច"), ("Chrome", "ក្រូម"), ("Shift", "ស៊ីហ្វ"), ("Chip", "ឈីប"), ("Byte", "បៃ"),
        ("Font", "ហ្វុន"), ("Word", "វើដ"), ("HDMI", "អេចឌីអេមអាយ"), ("USB", "យូអេសប៊ី"), ("CPU", "ស៊ីភីយូ"),
        ("GPU", "ជីភីយូ"), ("RAM", "រ៉េម"), ("Google Sheet", "ហ្គូហ្គល ស៊ីត"), ("Apps Script", "អែប ស្គ្រីប"), ("BotFather", "បូត ហ្វាដឺ"),
        ("Telegram", "តេឡេក្រាម"), ("Excel", "អ៊ិចសែល"), ("Prompt", "ផ្រមត៍"), ("Caption", "ខេបសិន"),
        ("Comment", "ខមមិន"), ("Follow", "ហ្វលឡូ"), ("Email", "អ៊ីមែល"), ("email", "អ៊ីមែល"), ("Copy", "ខូពី"),
        ("Paste", "ផេស"), ("Enter", "អិនទ័រ"), ("Token", "តូខិន"), ("Trigger", "ទ្រីហ្គ័រ"), ("Part 2", "ភាគទីពីរ"),
        ("Control", "ខុនត្រូល"), ("SUMIF", "សាំ អ៊ីហ្វ"), ("VLOOKUP", "វី លុកអាប់"), ("COUNTIF", "ខោនធ៍ អ៊ីហ្វ"),
        ("Bot", "បូត"), ("Sheet", "ស៊ីត"), ("AI", "អេអាយ"), ("IF", "អ៊ីហ្វ")]

LETTER = {"A": "អេ", "B": "ប៊ី", "C": "ស៊ី", "D": "ឌី", "E": "អ៊ី", "F": "អែហ្វ", "G": "ជី"}
NUM = {"2": "ពីរ", "3": "បី", "4": "បួន", "5": "ប្រាំ", "6": "ប្រាំមួយ", "7": "ប្រាំពីរ"}
def cellrefs(text):
    import re
    return re.sub(r"(?<![A-Za-z0-9])([A-G])([2-7])?(?![A-Za-z0-9])", lambda m: LETTER[m.group(1)] + (" " + NUM[m.group(2)] if m.group(2) else ""), text)

def khmerize(text, cells=False):
    import re
    if cells: text = cellrefs(text)
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
            asyncio.run(edge_tts.Communicate(khmerize(s["speak"], spec.get("cellrefs", False)), voice, rate=rate, proxy=proxy).save(path))
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

# Ravy's standing rules for every video (14 Nov 2026):
#  1) open with a greeting + welcome + what this video covers:
#     standalone / part 1 : "...ស្វាគមន៍មកកាន់ Channel របស់ខ្ញុំ។ វីដេអូនេះ យើងនឹងសិក្សាស្វែងយល់អំពី {topic}។"
#     later parts (part>=2): "...វីដេអូនេះ យើងនឹងសិក្សាបន្តពីភាគមុន អំពី {topic}។"
#  2) say "វីដេអូនេះ" (this video), never "ស៊េរីនេះ" (this series).
GREETING = "សួស្តីបងប្អូនទាំងអស់គ្នា! ស្វាគមន៍មកកាន់ Channel របស់ខ្ញុំ។"
KH_DIG = str.maketrans("០១២៣៤៥៦៧៨៩", "0123456789")

def part_no(spec):
    if spec.get("part"): return int(spec["part"])
    m = re.search(r"ភាគ\s*([០-៩0-9]+)", spec.get("series", ""))
    return int(m.group(1).translate(KH_DIG)) if m else 1

def apply_house_rules(spec):
    spec = json.loads(json.dumps(spec, ensure_ascii=False).replace("ស៊េរីនេះ", "វីដេអូនេះ"))
    first = spec["scenes"][0]
    if spec.get("greet", True) and first.get("speak") and not first["speak"].startswith("សួស្តី"):
        topic = spec.get("topic")
        if not topic: raise SystemExit("spec needs a 'topic' (what this video covers) for the opening line")
        intro = (f"វីដេអូនេះ យើងនឹងសិក្សាបន្តពីភាគមុន អំពី{topic}។" if part_no(spec) >= 2
                 else f"វីដេអូនេះ យើងនឹងសិក្សាស្វែងយល់អំពី{topic}។")
        intro = re.sub(r"អំពី(?=[A-Za-z])", "អំពី ", intro)
        first["speak"] = f"{GREETING} {intro} {first['speak']}"
    return spec

def main():
    spec = apply_house_rules(json.load(open(sys.argv[1])))
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
