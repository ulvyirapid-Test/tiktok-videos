"""Build the Claude video-editing carousel (10 JPG slides, 1080x1350) — python3 build.py OUT_DIR"""
import asyncio, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
N = 10
km = lambda n: f'{n:02d}'.translate(str.maketrans('0123456789','០១២៣៤៥៦៧៨៩'))
def head(i, foot):
    bars = ''.join(f'<i class="{"on" if k <= i else ""}"></i>' for k in range(N))
    return (f'<div class=top><img src="{ROOT}/generator/worktips/logo.png"><div><b>@ulvyi</b><span>AI សម្រាប់ការងារ</span></div><em>{km(i+1)}/{km(N)}</em></div>',
            f'<div class=bot><div class=bars>{bars}</div><div class=ft><span>{foot}</span><span class=sw>{"អូសបន្ត →" if i < N-1 else "@ulvyi"}</span></div></div>')
def step(n, title, body):
    return f'<div class=num>{n}</div><h2>{title}</h2>{body}'
S = []
S.append(('ចាប់ផ្តើមនៅទីនេះ', '''<div class=tag>AI ធ្វើវីដេអូ · សម្រាប់អ្នកចាប់ផ្តើម</div>
<h1 class=h1c>ប្រាប់ Claude<br>→ បាន <span class=or>Reel</span> MP4</h1>
<p class=lead>ធ្វើវីដេអូជាមួយ <b>Claude</b> · <b>៨ ជំហាន</b>ច្បាស់ៗ</p>
<div class=bar><span class=ic>✍️</span><span>«ធ្វើ Reel ៣០ វិនាទី ពីវីដេអូដើមរបស់ខ្ញុំ»</span><span class=cur></span></div>
<div class=strip><span>✍️ Prompt</span><em>→</em><span>🧠 Claude</span><em>→</em><span class=vid>▶ reel.mp4 · 0:30</span></div>
<div class=note>👑 ផ្ទាំង <b>Code</b> ត្រូវការគម្រោង <b>Claude Pro</b> ឡើងទៅ</div>'''))
S.append(('ជំហាន ០១ / ០៨', step('០១','ដំឡើង Claude Desktop','''<p>ទាញយកពី <b class=mono>claude.com/download</b> ហើយ <b>Sign in</b>។ App <b>ឥតគិតថ្លៃ</b> · ផ្ទាំង Code ត្រូវការ Pro។</p>
<div class=app><div class=ai>💻</div><div><b>Claude Desktop</b><span>Mac · Windows · Linux (beta)</span></div><div class=btn>ទាញយក</div></div>
<div class=note>⚙️ ដំឡើង <b>Node.js</b> (<span class=mono>nodejs.org</span> · LTS) ផងដែរ — Remotion ត្រូវការវា</div>
<p class=small>🐧 Linux (beta)៖ សម្រាប់ Ubuntu / Debian</p>''')))
S.append(('ជំហាន ០២ / ០៨', step('០២','រៀបចំ Folder គម្រោង','''<div class=tree><div class=root>📂 AI Video Editing</div>
<div class=br>📁 <b>Assets</b> — Logo · តន្ត្រី · Font</div>
<div class=br>📁 <b>Raw</b> — វីដេអូដើម (បើមាន)</div>
<div class=br>📁 <b>Reference</b> — Screenshot ពីវីដេអូគំរូ</div></div>
<div class=note>💡 Folder ច្បាស់ → Claude ដឹងថា<b>ឯកសារណាប្រើធ្វើអ្វី</b></div>''')))
S.append(('ជំហាន ០៣ / ០៨', step('០៣','បើកផ្ទាំង Code','''<div class=tabs><span>💬 Chat</span><span>📁 Cowork</span><span class=sel>‹› Code</span></div>
<ol><li>ចុចផ្ទាំង <b>Code</b> (ខាងលើ)</li><li>ក្រោមប្រអប់ Prompt ជ្រើស <b>Local</b></li><li>ចុច <b>Open folder…</b> → រើស Folder&nbsp;ជំហាន&nbsp;០២</li></ol>
<div class=note>👑 Code ត្រូវការ <b>Pro · Max · Team · Enterprise</b></div>''')))
S.append(('ជំហាន ០៤ / ០៨', step('០៤','ដំឡើង Remotion Skills','''<p class=small><b>Skills</b> បង្រៀន Claude ពីរបៀបធ្វើវីដេអូដោយកូដ (Remotion)</p>
<div class=prm><span class=ic2>✍️</span><span>វិធីងាយបំផុត៖ ប្រាប់ Claude<br><b>«ដំឡើង Remotion skills ឱ្យខ្ញុំ»</b></span></div>
<div class=term><span class=mut2>ជម្រើសសម្រាប់អ្នកចេះ៖ វាយក្នុង Terminal (Ctrl+`)</span><br>&gt; npx skills add remotion-dev/skills<br><span class=mut2>ចុច Space ជ្រើស Claude Code → Enter → Enter</span><br><span class=ok>✔ remotion-best-practices</span></div>
<p class=small>⚙️ Node.js បានដំឡើងនៅជំហាន ០១</p>''')))
S.append(('ជំហាន ០៥ / ០៨', step('០៥','សរសេរ Prompt','''<div class=dark><span class=chip>/&gt;</span><p>ធ្វើ Reel ៣០ វិនាទី ពីវីដេអូក្នុង <b>Raw</b> · Style ដូចរូបក្នុង <b>Reference</b> · ប្រើ Logo ក្នុង <b>Assets</b> · <span class=yl>បង្ហាញ Storyboard ឱ្យខ្ញុំមើលមុនសិន។</span></p></div>
<div class=note>💡 លើកដំបូង Claude ត្រូវបង្កើតគម្រោង Remotion — រង់ចាំពីរបីនាទី</div>''')))
S.append(('ជំហាន ០៦ / ០៨', step('០៦','ពិនិត្យ Storyboard មុន','''<div class=sb><div><i>🙋</i><b>S1 · Hook</b><span>0:00</span></div><div><i>🎞️</i><b>S2 · រូប/វីដេអូ</b><span>0:06</span></div><div><i>💻</i><b>S3 · Logo + អក្សរ</b><span>0:14</span></div><div><i>▶️</i><b>S4 · CTA</b><span>0:22</span></div></div>
<div class=row>✅ <b>ពេញចិត្ត?</b> ប្រាប់ Claude «ចាប់ផ្តើមធ្វើ»</div><div class=row>✏️ <b>មិនទាន់?</b> កែ Storyboard សិន</div>''')))
S.append(('ជំហាន ០៧ / ០៨', step('០៧','មើលសាក → Render','''<p class=small>Render = បម្លែងជាឯកសារវីដេអូ MP4</p><ol><li>Claude បើក <b>Remotion Studio</b> ឱ្យមើលក្នុង Browser 👀</li><li>ពេញចិត្ត → ប្រាប់ «<b>Render ជា&nbsp;MP4</b>»</li><li>ឯកសារ <b>MP4</b> ចេញក្នុង Folder <b class=mono>out</b> 📦</li></ol>
<div class=note>🔐 បើ Claude សួរសុំអនុញ្ញាតរត់ពាក្យបញ្ជា → ចុចយល់ព្រម (<b>Allow</b>)</div>''')))
S.append(('ជំហាន ០៨ / ០៨', step('០៨','កែរហូតត្រូវចិត្ត','''<div class=loop><div><i>💬</i><b>Prompt</b></div><em>→</em><div><i>▶️</i><b>Preview</b></div><em>→</em><div><i>✏️</i><b>Feedback</b></div></div>
<div class=pill>🔁 ធ្វើម្តងទៀត រហូតត្រូវចិត្ត</div>
<div class=note>✨ Feedback ច្បាស់ ដូចជា «អក្សរធំជាងនេះ» · «ប្តូរតន្ត្រី» → លទ្ធផលល្អជាង</div>''')))
S.append(('AI សម្រាប់ការងារ', '''<h1 class=h1s>នេះទើបតែ<br><span class=yl2>ការចាប់ផ្តើម។</span></h1>
<p class=sub2>ជំហានបន្ទាប់ (ស្រេចចិត្ត)៖</p><div class=chips><span><b>ElevenLabs</b> — បន្ថែមសំឡេងអាន · ត្រូវការ API key</span><span><b>Whisper</b> — បន្ថែម Subtitle · Claude ដំឡើងឱ្យបាន</span></div>
<div class=warn><div>⚠️ <b>AI អាចខុស</b> — កុំរំពឹងល្អឥតខ្ចោះលើកដំបូង</div><div>📜 <b>Remotion</b>៖ ឥតគិតថ្លៃ បុគ្គល/ក្រុមហ៊ុន ≤៣ នាក់<br>ក្រុមហ៊ុនធំជាងនេះ ត្រូវទិញ License</div><div>🧭 <b>សាកធ្វើផ្ទាល់</b> ទើបពូកែ</div></div>
<p class=ask>អ្នកចង់ឱ្យ Claude ធ្វើវីដេអូអ្វី? Comment ប្រាប់ខ្ញុំ 👇</p>
<div class=cta><span class=fol>🔔 Follow @ulvyi</span><span class=sav>🔖 Save ទុក</span></div>'''))
CSS = open(os.path.join(HERE, 'style.css')).read().replace('FONT', ROOT + '/fonts/KantumruyPro.ttf')
html = '<html><head><meta charset=utf-8><style>' + CSS + '</style></head><body>'
for i, (foot, body) in enumerate(S):
    t, b = head(i, foot); html += f'<section class="s{" cover" if i == 0 else ""}" id=s{i}>{t}<div class=blob></div><div class=body>{body}</div>{b}</section>'
html += '</body></html>'
open(os.path.join(HERE, 'claude_video.html'), 'w').write(html)
async def go(out):
    from playwright.async_api import async_playwright
    os.makedirs(out, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--allow-file-access-from-files"])
        pg = await b.new_page(viewport={"width":1080,"height":1350}); await pg.goto("file://" + HERE + "/claude_video.html"); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(500)
        for i in range(N): await pg.locator(f"#s{i}").screenshot(path=f"{out}/{i+1:02d}.jpg", type="jpeg", quality=92)
        await b.close()
asyncio.run(go(sys.argv[1]))
