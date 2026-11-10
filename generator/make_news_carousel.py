"""Render a Khmer tech-news TikTok photo carousel (1080x1920 JPGs) from a content JSON.

Usage: python3 make_news_carousel.py content/2026-11-11.json carousels/2026-11-11 [accent_index]
Slides: cover (hook) -> headline -> 3 facts -> why it matters -> follow CTA
"""
import asyncio, html, json, os, sys
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.abspath(os.path.join(HERE, "..", "fonts", "KantumruyPro.ttf"))
ACCENTS = ["#00E5FF", "#7CFFB2", "#FFC400", "#B48CFF", "#FF785A"]
KH = "០១២៣៤៥៦៧៨៩"

def esc(s): return html.escape(s).replace("\n", "<br>")

CSS = """
@font-face { font-family:K; src:url('file://%(font)s'); font-weight:100 900; }
* { margin:0; padding:0; box-sizing:border-box; }
body { width:1080px; height:1920px; overflow:hidden; font-family:K, sans-serif; color:#F5F7FF;
       background:linear-gradient(180deg,#0A0E20 0%%,#1A103C 100%%); position:relative; }
.g1 { position:absolute; width:1000px; height:1000px; border-radius:50%%; left:-300px; top:-200px;
      background:%(acc)s; opacity:.28; filter:blur(200px); }
.g2 { position:absolute; width:900px; height:900px; border-radius:50%%; right:-350px; bottom:-250px;
      background:#6E1450; opacity:.55; filter:blur(200px); }
.top { position:absolute; top:110px; left:80px; right:80px; display:flex; justify-content:space-between; align-items:center; }
.handle { font-size:34px; font-weight:700; color:#AFB7D7; }
.count { font-size:32px; font-weight:700; color:#AFB7D7; background:rgba(255,255,255,.08); padding:8px 24px; border-radius:999px; }
.safe { position:absolute; left:80px; top:260px; width:860px; height:1240px; display:flex; flex-direction:column; justify-content:center; gap:48px; }
.tag { align-self:flex-start; font-size:38px; font-weight:700; color:#0A0E20; background:%(acc)s; padding:10px 34px; border-radius:999px; }
.hook { font-size:104px; line-height:1.42; font-weight:800; }
.head { font-size:88px; line-height:1.45; font-weight:800; }
.num { width:150px; height:150px; border-radius:40px; background:%(acc)s; color:#0A0E20; font-size:96px; font-weight:800;
       display:flex; align-items:center; justify-content:center; }
.fact { font-size:76px; line-height:1.5; font-weight:700; }
.label { font-size:44px; font-weight:700; color:%(acc)s; }
.why { font-size:66px; line-height:1.55; font-weight:700; }
.card { background:rgba(255,255,255,.07); border:3px solid rgba(255,255,255,.12); border-radius:44px; padding:56px 56px; }
.muted { font-size:42px; color:#AFB7D7; line-height:1.5; }
.swipe { margin-top:40px; font-size:44px; font-weight:700; color:%(acc)s; }
.bar { position:absolute; left:80px; width:860px; top:200px; height:8px; border-radius:4px; background:rgba(255,255,255,.12); }
.bar i { display:block; height:100%%; border-radius:4px; background:%(acc)s; }
.acc { color:%(acc)s; }
"""

def slides(d):
    s = [f"<div class=tag>{esc(d['tag'])}</div><div class=hook>{esc(d['hook'])}</div><div class=swipe>អូសមើលបន្ត →</div>",
         f"<div class=label>ព័ត៌មាន Tech ថ្ងៃនេះ</div><div class=head>{esc(d['headline'])}</div>"]
    for i, f in enumerate(d["facts"], 1):
        s.append(f"<div class=num>{KH[i]}</div><div class=fact>{esc(f)}</div>")
    s.append(f"<div class=label>ហេតុអ្វីសំខាន់?</div><div class='card why'>{esc(d['why'])}</div>")
    s.append(f"<div class=head>Follow<br><span class=acc>@ulvyi</span></div>"
             f"<div class=muted>ដើម្បីដឹងព័ត៌មាន Tech និង AI<br>ថ្មីៗរៀងរាល់ថ្ងៃ 🚀</div>"
             f"<div class=muted style='font-size:34px'>ប្រភព៖ {esc(d['source'])}</div>")
    return s

async def render(pages, out_dir, acc):
    out_dir = os.path.abspath(out_dir); os.makedirs(out_dir, exist_ok=True)
    css = CSS % {"font": FONT, "acc": acc}
    n = len(pages); paths = []
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--allow-file-access-from-files"])
        pg = await b.new_page(viewport={"width": 1080, "height": 1920})
        for i, body in enumerate(pages):
            doc = (f"<html><head><meta charset=utf-8><style>{css}</style></head><body><div class=g1></div><div class=g2></div>"
                   f"<div class=top><div class=handle>@ulvyi</div><div class=count>{i+1}/{n}</div></div>"
                   f"<div class=bar><i style='width:{int(860*(i+1)/n)}px'></i></div><div class=safe>{body}</div></body></html>")
            tmp = os.path.join(out_dir, "_tmp.html"); open(tmp, "w").write(doc)
            await pg.goto("file://" + tmp); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(150)
            path = os.path.join(out_dir, f"{i+1:02d}.jpg")
            await pg.screenshot(path=path, type="jpeg", quality=90); paths.append(path)
        await b.close()
    os.remove(os.path.join(out_dir, "_tmp.html"))
    return paths

if __name__ == "__main__":
    d = json.load(open(sys.argv[1]))
    acc = ACCENTS[int(sys.argv[3]) % len(ACCENTS)] if len(sys.argv) > 3 else ACCENTS[0]
    for p in asyncio.run(render(slides(d), sys.argv[2], acc)): print(p)
