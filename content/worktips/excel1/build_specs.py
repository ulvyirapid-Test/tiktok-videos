import json, os, re
D = os.path.dirname(os.path.abspath(__file__))
MD = open(os.path.join(D, "..", "excel_one_formula_script.md")).read()
KH = "០១២៣៤៥៦៧៨៩"
def kh(n): return "".join(KH[int(c)] for c in str(n))

# ---- parse approved script: topic, 7 narrations, caption per part
parts = re.split(r"\n## ភាគ ", MD)[1:]
P = []
for sec in parts:
    sec = sec.split("\n## ✅")[0]
    name = sec.split("\n")[0].split(":", 1)[1].strip()
    topic = re.search(r"\*\*topic៖\*\* «(.+?)»", sec).group(1)
    speaks = [ln.rstrip().rstrip("|").rstrip().rsplit(" | ", 1)[-1].strip().lstrip("«").rstrip("»") for ln in sec.split("\n") if re.match(r"\| [1-7] \|", ln)]
    cap = re.search(r"\*\*Caption:\*\* `(.+?)` / `(.+?)` / `(.+?)`", sec)
    assert len(speaks) == 7, (name, len(speaks))
    P.append(dict(name=name, topic=topic, speak=speaks, caption="\n".join(cap.groups())))
assert len(P) == 12

R = [["កាហ្វេ","សុខា",3,7.5],["តែ","ដារ៉ា",2,4],["កាហ្វេ","ដារ៉ា",5,12.5],["នំ","សុខា",4,6],["កាហ្វេ","សុខា",2,5],["តែ","សុខា",1,2]]
C = ["B ទំនិញ","C អ្នកលក់","D ចំនួន","E $"]
def sub(idx, extra=None):
    return [C[i] for i in idx] + ([extra] if extra else []), [[r[i] for i in idx] + ([""] if extra else []) for r in R]
PR = (["A ទំនិញ","B តម្លៃ $","C កូដ"], [["កាហ្វេ",2.5,"K01"],["តែ",2,"T01"],["នំ",1.5,"N01"]])
def sheet(bg, title, formula, cr, **kw):
    c, r = cr
    if "result" in kw and not c[-1][0] in "FGH": c, r = c + ["F លទ្ធផល"], [x + [""] for x in r]
    d = {"type":"sheet","bg":bg,"rel":True,"title":title,"file":kw.pop("file","Sales"),"cols":c,"rows":r,"formula":formula,
         "fAt":0.04,"fDur":0.22,"hlAt":0.35,"rAt":0.7,"fs":kw.pop("fs",42),"noteSize":44}
    d.update(kw); return d
def hook(lines, notify, **kw):
    return dict(type="hook", bg="excel", pulse=True, cycle=True, ntfSize=44, notify=[dict(bot=b, time="", icon=i, t=t) for b,i,t in notify],
                ntfAt=[0.03] + [0.3 + 0.25*k for k in range(len(notify) - 1)], lines=[{"t":lines[0],"cls":"h1"}] + ([{"t":lines[1],"cls":"h2"}] if len(lines) > 1 else []), **kw)
def what(syntax, sub, label="📐 ជាអ្វី?"): return dict(type="tip", bg="google", label=label, text=syntax.replace(", ", ",`\n`"), sub=sub, subSize=44)
def steps(bg, title, items): return dict(type="steps", bg=bg, fs=46, fixed=True, stagger=0.4, title=title, items=items)
def tip(bg, label, text, sub=""): return dict(type="tip", bg=bg, label=label, text=text, sub=sub, subSize=44)
def cta(pre, text, ask): return dict(type="cta", bg="navy", avatarSize=150, gap=24, preSize=62, pre=pre, text=text, ask=ask)
E = sub([0,1,2,3]); BE = sub([0,3]); BCE = sub([0,1,3])
F = "F លទ្ធផល"; G = "G តម្លៃ"
GV = [2.5,2,2.5,1.5,2.5,2]

V = [
# 1 COUNTIF
[hook(["*3 ដង* ⚡","រាប់ _មិនបាច់ប្រើដៃ_"], [("😩 រាប់ដោយដៃ","✋","កាហ្វេ… ១, ២, ៣… !យឺត!"),("COUNTIF","🔢","កាហ្វេ → *3 ដង* ⚡")]),
 what("`=COUNTIF(កន្លែងរក, លក្ខខណ្ឌ)`", "① *កន្លែងរក* = ជួរឈរដែលចង់រាប់\n② *លក្ខខណ្ឌ* = អ្វីដែលចង់រាប់\n[[:]] = ដល់"),
 sheet("cpu","🔢 ឧទាហរណ៍ ១", '=COUNTIF(B2:B7,"កាហ្វេ")', BE, hlRows=[2,4,6], result={"label":"កាហ្វេ (ដង)","value":"3"}, note="ជួរដេក *2 · 4 · 6*"),
 sheet("code","🔢 ឧទាហរណ៍ ២ · លេខ", '=COUNTIF(E2:E7,">=5")', BE, hlRows=[2,4,5,6], result={"label":"≥ $5 (ដង)","value":"4"}, note="សញ្ញា + លេខ → [[\">=5\"]]"),
 steps("alert","⚠️ កំហុសញឹកញាប់",["`=COUNTIF(B2:B7,កាហ្វេ)` ភ្លេច [[\" \"]] → !#NAME?!","B4 = «កាហ្វេ + ដកឃ្លា» មើលមិនឃើញ → *2* ជំនួស 3\n✅ *TRIM* ក្នុងជួរឈរជំនួយ / Find & Replace"]),
 tip("tg","💡 គន្លឹះ","វាយលក្ខខណ្ឌក្នុងក្រឡា *G1*","`=COUNTIF(B2:B7,G1)`\nG1 = កាហ្វេ → *3* · G1 = តែ → *2*\nប្តូរ G1 = មិនបាច់កែរូបមន្ត ✅"),
 cta("ភាគ ១/១២ ✅\nបន្ទាប់៖ SUMIF 👀","COUNTIF = *រាប់ ១ លក្ខខណ្ឌ*","អ្នកនឹងប្រើ COUNTIF\n_រាប់អ្វី_? 👇")],
# 2 SUMIF
[hook(["*$25* ⚡","_បូកលុយ_ តាមលក្ខខណ្ឌ"], [("💵 លុយកាហ្វេ?","☕","7.5 + 12.5 + 5"),("SUMIF","⚡","→ *$25*")]),
 what("`=SUMIF(កន្លែងរក, លក្ខខណ្ឌ, កន្លែងបូក)`", "① *កន្លែងរក* ② *លក្ខខណ្ឌ* ③ *កន្លែងបូក*\n📏 ទំហំស្មើ · ចាប់ផ្តើមជួរដេកដូចគ្នា"),
 sheet("cpu","💵 ឧទាហរណ៍ ១", '=SUMIF(B2:B7,"កាហ្វេ",E2:E7)', BE, hlRows=[2,4,6], result={"label":"កាហ្វេ ($)","value":"25"}, note="7.5 + 12.5 + 5 = *25*"),
 sheet("code","💵 ឧទាហរណ៍ ២", '=SUMIF(C2:C7,"សុខា",E2:E7)', sub([1,3]), hlRows=[2,5,6,7], result={"label":"សុខា ($)","value":"20.5"}, note="7.5 + 6 + 5 + 2 = *20.5*"),
 steps("alert","⚠️ កំហុសញឹកញាប់",["`=SUMIF(B2:B7,\"កាហ្វេ\",E3:E8)` ចាប់ផ្តើមខុសជួរដេក\n→ *12* !ខុស! (4 + 6 + 2)","`=SUMIF(E2:E7,\"កាហ្វេ\",B2:B7)` ច្រឡំលំដាប់ → *0*\n✅ កន្លែងបូក *នៅចុង*"]),
 sheet("tg","💡 គន្លឹះ · បូកជួរឈរខ្លួនឯង", '=SUMIF(E2:E7,">=5")', BE, hlRows=[2,4,5,6], result={"label":"≥ $5 ($)","value":"31"}, note="មិនបាច់ផ្នែកទី ៣ ✅"),
 cta("ភាគ ២/១២ ✅\nបន្ទាប់៖ COUNTIFS 👀","SUMIF = *បូក ១ លក្ខខណ្ឌ*\nកន្លែងបូក *នៅចុង*","អ្នកនឹងប្រើ SUMIF\n_បូកអ្វី_? 👇")],
# 3 COUNTIFS
[hook(["*1 ដង* ⚡","កាហ្វេ _និង_ ដារ៉ា"], [("COUNTIF","❌","បានតែ ១ លក្ខខណ្ឌ"),("COUNTIFS","✅","កាហ្វេ + ដារ៉ា → *1*")]),
 what("`=COUNTIFS(រក១, លក្ខខណ្ឌ១, រក២, លក្ខខណ្ឌ២)`", "សរសេរជា *គូៗ* ① ②\nS = *ច្រើន* · រាប់តែជួរដេក ពិត*គ្រប់*លក្ខខណ្ឌ"),
 sheet("cpu","🎯 ឧទាហរណ៍ ១", '=COUNTIFS(B2:B7,"កាហ្វេ",\nC2:C7,"ដារ៉ា")', sub([0,1]), hlRows=[4], result={"label":"កាហ្វេ + ដារ៉ា","value":"1"}, note="គូ ① *B* + កាហ្វេ · គូ ② *C* + ដារ៉ា"),
 sheet("code","🎯 ឧទាហរណ៍ ២ · លេខ", '=COUNTIFS(C2:C7,"សុខា",\nD2:D7,">=3")', sub([1,2]), hlRows=[2,5], result={"label":"សុខា + ≥3","value":"2"}, note="សុខា 4 ដង · មានតែ *2* ដង ≥ 3 → ជួរដេក *2 · 5*"),
 steps("alert","⚠️ កំហុសញឹកញាប់",["`B2:B7` + `C2:C6` ទំហំមិនស្មើ → !#VALUE\\!!","COUNTIFS = *និង* · មិនមែន *ឬ* ទេ"]),
 tip("tg","💡 គន្លឹះ · រាប់ «ឬ»","តែ *ឬ* នំ = COUNTIF *២* បូកគ្នា","`=COUNTIF(B2:B7,\"តែ\")`\n`+COUNTIF(B2:B7,\"នំ\")`\nតែ *2* + នំ *1* = *3* · ថែម COUNTIF ទី ៣ ក៏បាន"),
 cta("ភាគ ៣/១២ ✅\nបន្ទាប់៖ SUMIFS 👀","COUNTIFS = *រាប់ «និង»*","អ្នកនឹងរាប់អ្វី\n_ជាមួយ ២ លក្ខខណ្ឌ_? 👇")],
# 4 SUMIFS
[hook(["*$12.5* ⚡","កាហ្វេ _ដែលសុខាលក់_"], [("💰 លុយ?","☕","កាហ្វេ + សុខា"),("SUMIFS","⚡","→ *$12.5*")]),
 what("`=SUMIFS(កន្លែងបូក, រក១, លក្ខខណ្ឌ១, រក២, លក្ខខណ្ឌ២)`", "⚠️ !កន្លែងបូក នៅមុខគេ!\nខុសពី SUMIF (នៅចុង)"),
 sheet("cpu","💰 ឧទាហរណ៍ ១", '=SUMIFS(E2:E7,\nB2:B7,"កាហ្វេ",\nC2:C7,"សុខា")', BCE, hlRows=[2,6], result={"label":"កាហ្វេ + សុខា","value":"12.5"}, fs=38, note="7.5 + 5 = *12.5*"),
 sheet("code","💰 ឧទាហរណ៍ ២ · លេខ", '=SUMIFS(E2:E7,\nC2:C7,"សុខា",\nD2:D7,">=2")', sub([1,2,3]), hlRows=[2,5,6,7], bad=[7], result={"label":"សុខា + ≥2","value":"18.5"}, fs=38, note="ជួរដេក 7 = ចំនួន 1 !មិនរាប់!"),
 steps("alert","⚠️ កំហុសញឹកញាប់",["`=SUMIFS(B2:B7,\"កាហ្វេ\",E2:E7)` លំដាប់ SUMIF\n→ ⚠️ Excel៖ «There's a problem with this formula»","ទំហំមិនស្មើ → !#VALUE\\!!"]),
 sheet("tg","💡 គន្លឹះ · ១ លក្ខខណ្ឌក៏បាន", '=SUMIFS(E2:E7,B2:B7,"កាហ្វេ")', BE, hlRows=[2,4,6], result={"label":"កាហ្វេ ($)","value":"25"}, fxSize=38, note="ប្រើ SUMIFS ជានិច្ច = *មិនច្រឡំលំដាប់*"),
 cta("ភាគ ៤/១២ ✅\nបន្ទាប់៖ IF 👀","SUMIFS = *បូក «និង»*\nកន្លែងបូក *មុនគេ*","អ្នកនឹងបូកលុយ\n_តាមលក្ខខណ្ឌអ្វី_? 👇")],
# 5 IF
[hook(["*ល្អ* · _ធម្មតា_ ⚡","ឱ្យ Excel _សម្រេចចិត្ត_"], [("កាហ្វេ $7.5","🟢","→ *ល្អ*"),("តែ $4","⚪","→ ធម្មតា")]),
 what("`=IF(លក្ខខណ្ឌ, បើពិត, បើមិនពិត)`", "❓ លក្ខខណ្ឌ\n✅ ពិត → … · ❌ មិនពិត → …"),
 sheet("cpu","❓ ឧទាហរណ៍ ១ · ពាក្យ", '=IF(E2>=5,"ល្អ","ធម្មតា")', sub([0,3],F), fill=["ល្អ","ធម្មតា","ល្អ","ល្អ","ល្អ","ធម្មតា"], fillCol=2, fillBlank=True, fillAt=0.6, hlRows=[3,7], bad=[3,7], hlAt=0.85, fs=44, note="ចាប់ការ៉េតូចជ្រុង *F2* ទាញចុះ ⬇"),
 sheet("code","❓ ឧទាហរណ៍ ២ · គណនា", '=IF(D2>=4,E2*0.9,E2)', sub([2,3],"G ក្រោយបញ្ចុះ"), fill=[7.5,4,11.25,5.4,5,2], fillCol=2, fillBlank=True, fillAt=0.55, hlRows=[4,5], hlAt=0.7, fs=44, note="≥ 4 → *×0.9* (បញ្ចុះ 10%)"),
 steps("alert","⚠️ កំហុសញឹកញាប់",["`\"ល្អ` ភ្លេចបិទ [[\"]] → ⚠️ Excel មិនព្រមទទួល","`E2>=\"5\"` លេខក្នុង [[\" \"]] → «ធម្មតា» គ្រប់ជួរដេក !ខុស!"]),
 sheet("tg","💡 គន្លឹះ · [[\"\"]] = ក្រឡាទទេ", '=IF(E2>=5,"ល្អ","")', sub([0,3],F), fill=["ល្អ","","ល្អ","ល្អ","ល្អ",""], fillCol=2, fillBlank=True, fillAt=0.45, fs=44, note="«ធម្មតា» → *ទទេ* · តារាង*ស្អាតជាង* ✨"),
 cta("ភាគ ៥/១២ ✅\nបន្ទាប់៖ IFS 👀","IF = ពិត ➜ … / មិនពិត ➜ …","អ្នកនឹងឱ្យ IF\n_សម្រេចអ្វី_? 👇")],
# 6 IFS
[hook(["*ខ្ពស់* · _មធ្យម_ · !ទាប!","មិនបាច់ IF ក្នុង IF ⚡"], [("😵 IF(…,IF(…))","🌀","វែង · ច្រឡំវង់ក្រចក"),("IFS","✅","ខ្លី · ងាយអាន")]),
 what("`=IFS(លក្ខខណ្ឌ១, លទ្ធផល១, …, TRUE, ករណីផ្សេង)`", "ពិនិត្យ *ពីលើចុះក្រោម* ⬇\n*TRUE* = ករណីផ្សេងៗ\n[[Excel 2019+]] [[365]] [[Google Sheets]]"),
 sheet("cpu","🪜 ឧទាហរណ៍ ១ · លុយ", '=IFS(E2>=10,"ខ្ពស់",\nE2>=5,"មធ្យម",\nTRUE,"ទាប")', sub([0,3],F), fill=["មធ្យម","ទាប","ខ្ពស់","មធ្យម","មធ្យម","ទាប"], fillCol=2, fillBlank=True, fillAt=0.5, fxSize=38, fs=42),
 sheet("code","🪜 ឧទាហរណ៍ ២ · ចំនួន", '=IFS(D2>=5,"ច្រើន",\nD2>=3,"មធ្យម",\nTRUE,"តិច")', sub([0,2],F), fill=["មធ្យម","តិច","ច្រើន","មធ្យម","តិច","តិច"], fillCol=2, fillBlank=True, fillAt=0.5, fxSize=38, fs=42),
 steps("alert","⚠️ កំហុសញឹកញាប់",["`=IFS(E2>=5,\"មធ្យម\",`\n`E2>=10,\"ខ្ពស់\",…)`\n→ $12.5 ចេញ «មធ្យម» !ខុស! ✅ *ធំមុន*","`=IFS(E2>=10,\"ខ្ពស់\",`\n`E2>=5,\"មធ្យម\")` គ្មាន TRUE\n→ ជួរដេក 3 ($4) !#N/A!"]),
 tip("tg","💡 Excel 2016 គ្មាន IFS?","ប្រើ IF ក្នុង IF","`=IF(E2>=10,\"ខ្ពស់\",`\n`IF(E2>=5,\"មធ្យម\",\"ទាប\"))`\nរាប់វង់ក្រចកបិទ*ឱ្យគ្រប់* ✅"),
 cta("ភាគ ៦/១២ ✅\nបន្ទាប់៖ AND 👀","IFS = *ច្រើនកាំ* · ធំមុន\n*TRUE* នៅចុង","អ្នកនឹងចាត់ថ្នាក់អ្វី\n_ជា ៣ កម្រិត_? 👇")],
# 7 AND
[hook(["✅ + ✅ = *បញ្ចុះ* ⚡","កាហ្វេ _និង_ ≥ ៣"], [("កាហ្វេ?","☕","✅"),("≥ ៣ កែវ?","🔢","✅ → *បញ្ចុះ*")]),
 what("`=AND(លក្ខខណ្ឌ១, លក្ខខណ្ឌ២, …)`", "✅✅ → *TRUE*\n✅❌ → !FALSE!\nពិត*ទាំងអស់* ទើប TRUE"),
 sheet("cpu","✅ ឧទាហរណ៍ ១", '=AND(B2="កាហ្វេ",D2>=3)', sub([0,2],F), fill=["TRUE","FALSE","TRUE","FALSE","FALSE","FALSE"], fillCol=2, fillBlank=True, fillAt=0.5, hlRows=[2,4,6], bad=[6], hlAt=0.65, fs=44, note="ជួរដេក 6 = កាហ្វេ ប៉ុន្តែ *2* → FALSE"),
 sheet("code","✅ ឧទាហរណ៍ ២ · ក្នុង IF", '=IF(AND(C2="សុខា",E2>=5),\n"Bonus","")', sub([1,3],F), fill=["Bonus","","","Bonus","Bonus",""], fillCol=2, fillBlank=True, fillAt=0.6, hlRows=[2,5,6], hlAt=0.5, fs=44),
 steps("alert","⚠️ កំហុសញឹកញាប់",["`=AND(B2=កាហ្វេ,…)` ភ្លេច [[\" \"]] → !#NAME?!","(Excel) `=5<=E2<=10` → FALSE *គ្រប់ជួរដេក*\n✅ `=AND(E2>=5,E2<=10)`"]),
 sheet("tg","💡 គន្លឹះ · ពិនិត្យចន្លោះ", '=AND(E2>=5,E2<=10)', sub([0,3],F), fill=["TRUE","FALSE","FALSE","TRUE","TRUE","FALSE"], fillCol=2, fillBlank=True, fillAt=0.55, hlRows=[2,5,6], hlAt=0.45, fs=44, note="$5 ដល់ $10"),
 cta("ភាគ ៧/១២ ✅\nបន្ទាប់៖ OR 👀","AND = ពិត*ទាំងអស់*","អ្នកនឹងពិនិត្យ\n_លក្ខខណ្ឌពីរណា_? 👇")],
# 8 OR
[hook(["តែ _ឬ_ នំ ⚡","ពិត *មួយក៏បាន*"], [("កាហ្វេ","❌","FALSE"),("តែ / នំ","✅","*TRUE*"),("OR","🔀","ជួរដេក *3 · 5 · 7*")]),
 what("`=OR(លក្ខខណ្ឌ១, លក្ខខណ្ឌ២, …)`", "✅❌ → *TRUE*\n❌❌ → !FALSE!\nពិត*មួយ*ក៏គ្រប់គ្រាន់"),
 sheet("cpu","🔀 ឧទាហរណ៍ ១", '=OR(B2="តែ",B2="នំ")', sub([0],F), fill=["FALSE","TRUE","FALSE","TRUE","FALSE","TRUE"], fillCol=1, fillBlank=True, fillAt=0.55, hlRows=[3,5,7], hlAt=0.45, fs=46),
 sheet("code","🔀 ឧទាហរណ៍ ២ · ក្នុង IF", '=IF(OR(D2>=5,E2>=10),\n"ពិសេស","")', sub([2,3],F), fill=["","","ពិសេស","","",""], fillCol=2, fillBlank=True, fillAt=0.6, hlRows=[4], hlAt=0.5, fs=44, note="ជួរដេក 4 = *5* និង *$12.5*"),
 steps("alert","⚠️ កំហុសញឹកញាប់",["`=OR(B2=\"តែ\",\"នំ\")` → !#VALUE\\!!","✅ `=OR(B2=\"តែ\",B2=\"នំ\")`\nសរសេរ *B2=* ម្តងទៀត គ្រប់លក្ខខណ្ឌ"]),
 sheet("tg","💡 គន្លឹះ · AND + OR", '=AND(C2="សុខា",\nOR(B2="តែ",B2="នំ"))', sub([0,1],F), fill=["FALSE","FALSE","FALSE","TRUE","FALSE","TRUE"], fillCol=2, fillBlank=True, fillAt=0.5, hlRows=[5,7,3], bad=[3], hlAt=0.65, fs=44, note="ជួរដេក 3 = តែ ប៉ុន្តែ *ដារ៉ា*លក់ → FALSE"),
 cta("ភាគ ៨/១២ ✅\nបន្ទាប់៖ VLOOKUP 👀","OR = ពិត*មួយក៏បាន*","អ្នកនឹងប្រើ OR\n_ពិនិត្យអ្វី_? 👇")],
# 9 VLOOKUP
[hook(["*តម្លៃចេញឯង* ⚡","_ទាញ_ពីតារាងមួយទៀត 🔎"], [("😩 Copy ម្តងមួយៗ","✋","!យឺត · ងាយខុស!"),("VLOOKUP","⚡","2.5 · 2 · 1.5 …")]),
 what("`=VLOOKUP(រកអ្វី, តារាង, ជួរឈរទី, FALSE)`", "① *រកអ្វី* ② *តារាង* ③ *ជួរឈរទីប៉ុន្មាន* ④ *FALSE*\nរកក្នុងជួរឈរ*ទីមួយ* → យកពី*ស្តាំ* ➡️"),
 sheet("cpu","🔎 ឧទាហរណ៍ ១ · តម្លៃ", '=VLOOKUP(B2,Price!A:C,2,FALSE)', sub([0,3],G), fill=GV, fillCol=2, fillBlank=True, fillAt=0.85, hlRows=[2], hlAt=0.3, fs=44, note="Price៖ កាហ្វេ *2.5* · តែ *2* · នំ *1.5*\nទាញ *G2* ចុះក្រោម ⬇"),
 sheet("code","🔎 ឧទាហរណ៍ ២ · កូដ", '=VLOOKUP(B2,Price!A:C,3,FALSE)', sub([0,3],"H កូដ"), fill=["K01","T01","K01","N01","K01","T01"], fillCol=2, fillBlank=True, fillAt=0.75, hlRows=[2], hlAt=0.4, fs=44, note="ប្តូរតែ *2 → 3* (ជួរឈរទី ៣ នៃ Price = កូដ)"),
 steps("alert","⚠️ កំហុសញឹកញាប់",["ភ្លេច *FALSE* → រកប្រហាក់ប្រហែល\nតារាងមិនតម្រៀប → !លេខខុស!","`=VLOOKUP(\"T01\",`\n`Price!A:C,1,FALSE)` ⬅️ → !#N/A!\nជួរឈររក ត្រូវនៅ*ឆ្វេងបំផុត*"]),
 tip("tg","💡 គន្លឹះ · $ ចាក់សោ 🔒","`Price!$A$2:$C$4`","ចុច [[F4]] (Laptop៖ [[Fn]] + [[F4]])\nទាញចុះ → តារាង*មិនរំកិល* ✅\n`A:C` ទាំងជួរឈរ → មិនបាច់ $"),
 cta("ភាគ ៩/១២ ✅\nបន្ទាប់៖ XLOOKUP 👀","VLOOKUP = *ទាញ* · កុំភ្លេច *FALSE*","អ្នកនឹងទាញ\n_ទិន្នន័យអ្វី_? 👇")],
# 10 XLOOKUP
[hook(["*ខ្លីជាង* · រកបាន*សងខាង* ⚡"], [("🐢 VLOOKUP · ៤ ផ្នែក","📏","→ 2.5"),("⚡ XLOOKUP · ៣ ផ្នែក","✂️","→ *2.5* · ⬅️ *តែ*")]),
 what("`=XLOOKUP(រកអ្វី, ជួរឈររក, ជួរឈរលទ្ធផល, [បើរកមិនឃើញ])`", "ត្រូវគ្នាពិត *ស្វ័យប្រវត្តិ* (មិនបាច់ FALSE)\n[[365]] [[Excel 2021+]] [[Google Sheets]]"),
 sheet("cpu","⚡ ឧទាហរណ៍ ១ · តម្លៃ", '=XLOOKUP(B2,Price!A:A,\nPrice!B:B)', sub([0,3],G), fill=GV, fillCol=2, fillBlank=True, fillAt=0.8, hlRows=[2], hlAt=0.3, fs=44, fxSize=40, note="Price៖ កាហ្វេ *2.5* · តែ *2* · នំ *1.5*\nមិនបាច់*រាប់លេខជួរឈរ* ✅"),
 sheet("code","⬅️ ឧទាហរណ៍ ២ · Sheet Price", '=XLOOKUP(E2,C2:C4,A2:A4)', (["A ទំនិញ","B $","C កូដ","E កូដរក","F ឈ្មោះ"], [["កាហ្វេ",2.5,"K01","T01",""],["តែ",2,"T01","",""],["នំ",1.5,"N01","",""]]), file="Price · F2", fill=["តែ","",""], fillCol=4, fillBlank=True, fillAt=0.8, hlRows=[3], hlAt=0.5, fs=40, fxSize=42, note="រកក្នុង *C* (ស្តាំ) → យកពី *A* (ឆ្វេង)\nVLOOKUP !❌ ធ្វើមិនបាន!"),
 steps("alert","⚠️ កំហុសញឹកញាប់",["`A2:A4` + `B2:B5` ទំហំមិនស្មើ → !#VALUE\\!!","Excel 2016 / 2019 → !#NAME?! (គ្មាន XLOOKUP)"]),
 tip("tg","💡 គន្លឹះ · ផ្នែកទី ៤","ពាក្យពេល*រកមិនឃើញ*","`=XLOOKUP(\"ទឹកក្រូច\",`\n`Price!A:A,Price!B:B,`\n`\"រកមិនឃើញ\")`\n→ *រកមិនឃើញ* ✅ មិនបាច់ IFERROR"),
 cta("ភាគ ១០/១២ ✅\nបន្ទាប់៖ IFERROR 👀","XLOOKUP = *ទាញសងខាង*","អ្នកប្រើ Excel\n_កំណែណា_? 👇")],
# 11 IFERROR
[hook(["កំហុស → *ពាក្យស្អាត* ✅"], [("😱 កំហុស","🔴","!#N/A! · !#DIV/0\\!!"),("IFERROR","🛡️","→ *រកមិនឃើញ* · *-*")]),
 what("`=IFERROR(រូបមន្តដើម, បង្ហាញពេលមានកំហុស)`", "គ្មានកំហុស → លទ្ធផល*ធម្មតា*\nមានកំហុស → *ពាក្យដែលអ្នកចង់បាន*"),
 steps("cpu","🛡️ ឧទាហរណ៍ ១ · រកមិនឃើញ",["`=VLOOKUP(\"ទឹកក្រូច\",`\n`Price!A:C,2,FALSE)` → !#N/A! 😱","`=IFERROR(VLOOKUP(\"ទឹកក្រូច\",`\n`Price!A:C,2,FALSE),\"រកមិនឃើញ\")`\n→ *រកមិនឃើញ* ✅"]),
 dict(sheet("code","➗ ឧទាហរណ៍ ២ · ចែកនឹងសូន្យ", '=IFERROR(E2/D2,"-")', (["B ទំនិញ","D ចំនួន","E $","F តម្លៃ/មួយ"], [["កាហ្វេ",3,7.5,""],["តែ",2,4,""],["កាហ្វេ",5,12.5,""],["នំ",4,6,""],["កាហ្វេ",2,5,""],["តែ",1,2,""],["ទឹកក្រូច",0,0,""]]), fill=[2.5,2,2.5,1.5,2.5,2,"-"], fillCol=3, fillBlank=True, fillAt=0.55, hlRows=[8], bad=[8], hlAt=0.75, fs=38, note="ទាញ *F2* ដល់ *F8* · ជួរដេក 8 !#DIV/0\\!! → *-* ✅")),
 steps("alert","⚠️ ប្រយ័ត្ន",["`=IFERROR(VLOOKP(B2,…),`\n`\"រកមិនឃើញ\")` វាយខុស","→ «រកមិនឃើញ» *គ្រប់ជួរដេក*\n!លាក់កំហុសពិត! 🙈"]),
 tip("tg","💡 គន្លឹះ","សរសេររូបមន្ត*ឱ្យត្រូវ*សិន","① សាកល្បង ✅\n② ទើបរុំ *IFERROR* នៅ*ចុងក្រោយ*"),
 cta("ភាគ ១១/១២ ✅\nបន្ទាប់៖ IFNA 👀","IFERROR = កំហុស → *ពាក្យ*","អ្នកជួបកំហុសអ្វី\n_ញឹកញាប់ជាងគេ_? 👇")],
# 12 IFNA
[hook(["លាក់*តែ* #N/A 🎯"], [("🙈 IFERROR","🛡️","លាក់*គ្រប់*កំហុស"),("🎯 IFNA","👀","លាក់តែ *#N/A* · ឃើញរូបមន្តខុស")]),
 what("`=IFNA(រូបមន្តដើម, បង្ហាញពេល #N/A)`", "សរសេរ*ដូច* IFERROR\nធ្វើការតែពេល *#N/A*\n[[Excel 2013+]] [[Google Sheets]]"),
 sheet("cpu","🎯 ឧទាហរណ៍ ១", '=IFNA(VLOOKUP(B8,Price!A:C,2,FALSE),\n"រកមិនឃើញ")', (["B ទំនិញ","G តម្លៃ"], [[r[0],""] for r in R] + [["ទឹកក្រូច",""]]), fill=GV + ["រកមិនឃើញ"], fillCol=1, fillBlank=True, fillAt=0.55, hlRows=[8], bad=[8], hlAt=0.4, fs=40, fxSize=38, note="ទឹកក្រូច → *រកមិនឃើញ* ✅ (ដូច IFERROR)"),
 dict(type="compare", bg="code", neutral=True, title="វាយខុស *VLOOKP*\n`=IFNA(VLOOKP(B2,…),…)`", left={"title":"🙈 IFERROR","items":["«រកមិនឃើញ»","លាក់កំហុស","មិនដឹងថាខុស"]}, right={"title":"👀 IFNA","items":["!#NAME?!","បង្ហាញកំហុស","*ដឹងភ្លាម* → កែ"]}),
 sheet("alert","⚠️ កំហុសញឹកញាប់", '=IFNA(E2/D2,"-")', (["B ទំនិញ","D ចំនួន","E $","F តម្លៃ/មួយ"], [[r[0],r[2],r[3],""] for r in R] + [["ទឹកក្រូច",0,0,""]]), fill=[2.5,2,2.5,1.5,2.5,2,"#DIV/0!"], fillCol=3, fillBlank=True, fillAt=0.5, hlRows=[8], bad=[8], hlAt=0.35, fs=38, note="IFNA *មិនលាក់* !#DIV/0\\!! → ✅ ប្រើ *IFERROR*"),
 tip("tg","💡 ជ្រើសមួយណា?","🔎 VLOOKUP → *IFNA*","⚡ XLOOKUP → *ផ្នែកទី ៤*\n➗ គណនា → *IFERROR*"),
 cta("ភាគ ១២/១២ · ចប់ ✅\nSave ទុក 📌","▶️ Playlist៖ *រូបមន្ត Excel*","រូបមន្តណាទៀត\n_ចង់ឱ្យខ្ញុំបង្រៀន_? 👇")],
]
assert len(V) == 12
QUIZ = [("រាប់ការលក់ របស់ដារ៉ា?", '=COUNTIF(C2:C7,"ដារ៉ា")', "2", "សាកល្បងខ្លួនឯង៖ រាប់ថា ដារ៉ាលក់បានប៉ុន្មានដង? ផ្អាកវីដេអូ ហើយសាកវាយ។ ចម្លើយ គឺពីរដង នៅជួរដេកលេខ ៣ និងលេខ ៤។"),
 ("បូកលុយពី តែ?", '=SUMIF(B2:B7,"តែ",E2:E7)', "6", "សាកល្បងខ្លួនឯង៖ បូកលុយពីការលក់តែ។ ផ្អាកវីដេអូ ហើយសាកវាយ។ ចម្លើយ គឺបួន បូកពីរ ស្មើប្រាំមួយដុល្លារ។"),
 ("កាហ្វេ ដែលសុខាលក់ ប៉ុន្មានដង?", '=COUNTIFS(B2:B7,"កាហ្វេ",\nC2:C7,"សុខា")', "2", "សាកល្បងខ្លួនឯង៖ រាប់កាហ្វេ ដែលសុខាលក់។ ផ្អាកវីដេអូ ហើយសាកវាយ។ ចម្លើយ គឺពីរដង នៅជួរដេកលេខ ២ និងលេខ ៦។"),
 ("លុយពី តែ ដែលសុខាលក់?", '=SUMIFS(E2:E7,B2:B7,"តែ",\nC2:C7,"សុខា")', "2", "សាកល្បងខ្លួនឯង៖ បូកលុយពីតែ ដែលសុខាលក់។ ផ្អាកវីដេអូ ហើយសាកវាយ។ ចម្លើយ គឺពីរដុល្លារ មានតែជួរដេកលេខ ៧។"),
 ("ជួរដេក 3 ចេញអ្វី?", '=IF(D3>=3,"ច្រើន","តិច")', "តិច", "សាកល្បងខ្លួនឯង៖ បើចំនួនចាប់ពីបី ដាក់ថា ច្រើន បើមិនដល់ ដាក់ថា តិច។ ជួរដេកលេខ ៣ ចេញអ្វី? ចម្លើយ គឺ តិច ព្រោះលក់បានតែពីរ។"),
 ("ជួរដេក 5 ($6) ចេញអ្វី?", '=IFS(E5>=10,"ខ្ពស់",\nE5>=5,"មធ្យម",TRUE,"ទាប")', "មធ្យម", "សាកល្បងខ្លួនឯង៖ ជួរដេកលេខ ៥ លក់ប្រាំមួយដុល្លារ ចេញអ្វី? ផ្អាកវីដេអូ ហើយគិត។ ចម្លើយ គឺ មធ្យម ព្រោះមិនដល់ដប់ តែចាប់ពីប្រាំ។"),
 ("ជួរដេក 3 ចេញអ្វី?", '=AND(B3="តែ",C3="ដារ៉ា")', "TRUE", "សាកល្បងខ្លួនឯង៖ ជួរដេកលេខ ៣ ជាតែ និងដារ៉ាលក់ឬទេ? ផ្អាកវីដេអូ ហើយគិត។ ចម្លើយ គឺ TRUE ព្រោះពិតទាំងពីរ។"),
 ("ជួរដេក 7 ចេញអ្វី?", '=OR(D7>=3,E7>=5)', "FALSE", "សាកល្បងខ្លួនឯង៖ ជួរដេកលេខ ៧ លក់មួយ និងពីរដុល្លារ។ OR ចេញអ្វី? ផ្អាកវីដេអូ ហើយគិត។ ចម្លើយ គឺ FALSE ព្រោះមិនពិតទាំងពីរ។"),
 ("តម្លៃ នំ ប៉ុន្មាន?", '=VLOOKUP("នំ",Price!A:C,2,FALSE)', "1.5", "សាកល្បងខ្លួនឯង៖ ទាញតម្លៃនំ ពី Sheet Price។ ផ្អាកវីដេអូ ហើយសាកវាយ។ ចម្លើយ គឺមួយដុល្លារកន្លះ។"),
 ("កូដ N01 ជាអ្វី?", '=XLOOKUP("N01",Price!C:C,\nPrice!A:A)', "នំ", "សាកល្បងខ្លួនឯង៖ កូដ អិន សូន្យ មួយ ជាទំនិញអ្វី? ផ្អាកវីដេអូ ហើយសាកវាយ។ ចម្លើយ គឺ នំ។"),
 ("ចេញអ្វី?", '=IFERROR(10/0,"-")', "-", "សាកល្បងខ្លួនឯង៖ ដប់ចែកនឹងសូន្យ រុំដោយ IFERROR ចេញអ្វី? ផ្អាកវីដេអូ ហើយគិត។ ចម្លើយ គឺសញ្ញាដក ព្រោះចែកនឹងសូន្យ ជាកំហុស។"),
 ("ចេញអ្វី?", '=IFNA(VLOOKUP("តែ",Price!A:C,2,FALSE),\n"រកមិនឃើញ")', "2", "សាកល្បងខ្លួនឯង៖ IFNA ជាមួយ VLOOKUP រកតែ ចេញអ្វី? ផ្អាកវីដេអូ ហើយគិត។ ចម្លើយ គឺពីរដុល្លារ ព្រោះរកឃើញ ដូច្នេះគ្មានអ្វីត្រូវលាក់។")]
import copy
for n, scenes in enumerate(V, 1):
    h0 = scenes[0]
    if n == 9:
        hs = sheet("excel", h0["lines"][0]["t"], "", PR, file="Price", hlRows=[2,3,4], hlAt=0.35, hlGap=1.2, fs=46, note="ជួរឈរ *① A ទំនិញ* · *② B តម្លៃ* · *③ C កូដ*")
    else:
        src = scenes[3] if n == 11 else scenes[2]
        hs = copy.deepcopy(src); hs["bg"] = "excel"; hs["title"] = h0["lines"][0]["t"]
        hs["note"] = h0["lines"][1]["t"] if len(h0["lines"]) > 1 else ""
        hs.update(fAt=0.3, fDur=0.25, hlAt=0.6, rAt=0.85, fillAt=0.7); hs.pop("say", None)
    scenes[0] = hs
    q, f, a, sp = QUIZ[n-1]
    scenes.insert(6, dict(type="tip", bg="ram", label="🧠 សាកល្បងខ្លួនឯង", text=q, sub="`" + f.replace("\n", "`\n`") + "`\n⏸️ ផ្អាក សាកវាយ…\n✅ ចម្លើយ៖ *" + a + "*", subSize=44, quiz_speak=sp))
    if n < 12: scenes[-1]["text"] += "\n🔔 Follow ដើម្បីមិនខកភាគបន្ទាប់"
for n, (p, scenes) in enumerate(zip(P, V), 1):
    assert len(scenes) == 8, n
    roles = [None, "ផ្នែកនីមួយៗ", "ឧទាហរណ៍ ១", "ឧទាហរណ៍ ២", "កំហុសញឹកញាប់", "គន្លឹះ", "សាកល្បង", None]
    sps = p["speak"][:6] + [scenes[6].pop("quiz_speak")] + p["speak"][6:]
    for s, sp, ro in zip(scenes, sps, roles):
        s["speak"] = sp
        if ro and "say" not in s: s["say"] = f"*{p['name']}* · {ro}"
    spec = {"avatar":True,"voice":"km-KH-PisethNeural","acc":"#4ADE80","series":f"រូបមន្ត Excel · ភាគ {kh(n)}","part":n,"cellrefs":True,
            "title":p["name"],"topic":p["topic"].replace("#N/A","អិនអេ"),"caption":p["caption"],"scenes":scenes}
    json.dump(spec, open(os.path.join(D, f"f{n:02d}.json"), "w"), ensure_ascii=False, indent=1)
print("ok", [p["name"] for p in P])
