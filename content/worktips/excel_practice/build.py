from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment
F="Arial"; H=Font(name=F,bold=True,color="FFFFFF"); N=Font(name=F); B=Font(name=F,bold=True)
HF=PatternFill("solid",fgColor="1F7A4D"); YF=PatternFill("solid",fgColor="FFF2CC")
thin=Side(style="thin",color="BBBBBB"); BD=Border(left=thin,right=thin,top=thin,bottom=thin)
wb=Workbook()
s=wb.active; s.title="Sales"
hdr=["ថ្ងៃ (Date)","មុខទំនិញ (Product)","អ្នកលក់ (Seller)","ចំនួន (Qty)","ទឹកប្រាក់ ($)","វាយតម្លៃ (IF)","តម្លៃ/ឯកតា (VLOOKUP)"]
import datetime as dt
rows=[("01/11","កាហ្វេ","សុខា",3,7.5),("01/11","តែ","ដារ៉ា",2,4),("02/11","កាហ្វេ","ដារ៉ា",5,12.5),
      ("02/11","នំ","សុខា",4,6),("03/11","កាហ្វេ","សុខា",2,5),("03/11","តែ","សុខា",1,2)]
s.append(hdr)
for r in rows:
    d,m=map(int,r[0].split("/")); s.append([dt.date(2026,m,d)]+list(r[1:]))
for i in range(2,8): s[f"A{i}"].number_format="d-mmm"
for i in range(2,8):
    s[f"F{i}"]=f'=IF(E{i}>=5,"ល្អ","ធម្មតា")'
    s[f"G{i}"]=f'=IFERROR(VLOOKUP(B{i},Price!$A:$C,2,FALSE),"រកមិនឃើញ")'
    s[f"E{i}"].number_format='$#,##0.00'; s[f"G{i}"].number_format='$#,##0.00'
p=wb.create_sheet("Price")
p.append(["មុខទំនិញ (Product)","តម្លៃ ($)","កូដ (Code)"])
for r in [("កាហ្វេ",2.5,"K01"),("តែ",2,"T01"),("នំ",1.5,"N01")]: p.append(list(r))
for i in range(2,5): p[f"B{i}"].number_format='$#,##0.00'
x=wb.create_sheet("Practice")
x.append(["#","សំណួរ","រូបមន្ត (សាកវាយនៅទីនេះ)","ចម្លើយត្រឹមត្រូវ","✔ ពិនិត្យ"])
Q=[("COUNTIF","លក់កាហ្វេប៉ុន្មានដង?",'=COUNTIF(Sales!B2:B7,"កាហ្វេ")'),
   ("SUMIF","លុយសរុបពីកាហ្វេ ($)?",'=SUMIF(Sales!B2:B7,"កាហ្វេ",Sales!E2:E7)'),
   ("SUMIFS","លុយកាហ្វេ ដែលសុខាលក់ ($)?",'=SUMIFS(Sales!E2:E7,Sales!B2:B7,"កាហ្វេ",Sales!C2:C7,"សុខា")'),
   ("COUNTIFS","ដារ៉ាលក់កាហ្វេប៉ុន្មានដង?",'=COUNTIFS(Sales!B2:B7,"កាហ្វេ",Sales!C2:C7,"ដារ៉ា")'),
   ("IF","ជួរដេក 4 (12.5$) ល្អ ឬធម្មតា?",'=IF(Sales!E4>=5,"ល្អ","ធម្មតា")'),
   ("IFS","ជួរដេក 4: ≥10 ខ្ពស់ / ≥5 មធ្យម / ផ្សេង ទាប",'=_xlfn.IFS(Sales!E4>=10,"ខ្ពស់",Sales!E4>=5,"មធ្យម",TRUE,"ទាប")'),
   ("AND","ជួរដេក 2: កាហ្វេ និង ≥3 កែវ?",'=AND(Sales!B2="កាហ្វេ",Sales!D2>=3)'),
   ("OR","ជួរដេក 3: តែ ឬ នំ?",'=OR(Sales!B3="តែ",Sales!B3="នំ")'),
   ("COUNTIF >=","ការលក់ចាប់ពី 5 កែវ មានប៉ុន្មានដង?",'=COUNTIF(Sales!D2:D7,">=5")'),
   ("IFNA","រកតម្លៃ \"ទឹកក្រូច\" ដោយ IFNA",'=_xlfn.IFNA(VLOOKUP("ទឹកក្រូច",Price!A:C,2,FALSE),"រកមិនឃើញ")'),
   ("VLOOKUP","តម្លៃកាហ្វេ ($)?",'=VLOOKUP("កាហ្វេ",Price!A:C,2,FALSE)'),
   ("IFERROR","រកតម្លៃ \"ទឹកក្រូច\" (គ្មានក្នុងតារាង)",'=IFERROR(VLOOKUP("ទឹកក្រូច",Price!A:C,2,FALSE),"រកមិនឃើញ")'),
   ("XLOOKUP","កូដ T01 ជាមុខទំនិញអ្វី? (Excel 365/2021+)",'=_xlfn.XLOOKUP("T01",Price!C:C,Price!A:A,"រកមិនឃើញ")')]
for n,(fn,q,f) in enumerate(Q,2):
    x.cell(n,1,n-1); x.cell(n,2,f"{fn}: {q}"); x.cell(n,4,f)
    x.cell(n,5,f'=IF(C{n}="","",IF(C{n}=D{n},"✅ ត្រូវ","❌ សាកម្តងទៀត"))')
    x.cell(n,3).fill=YF
for n in (3,4,12): x.cell(n,4).number_format='$#,##0.00'
x.cell(16,2,"របៀបប្រើ: វាយរូបមន្តក្នុងប្រអប់ពណ៌លឿង (ជួរឈរ C) រួចមើលជួរឈរ E។ ជួរឈរ D ជាចម្លើយគំរូ។").font=B
x.cell(17,2,"ចំណាំ: XLOOKUP / IFS ដំណើរការលើ Excel 365 / 2021 ឡើងទៅ (IFS ក៏មានក្នុង 2019)។")
x["C2"].comment=Comment("ឧទាហរណ៍: វាយ =COUNTIF(Sales!B2:B7,\"កាហ្វេ\")","ulvyi")
for ws,w in ((s,[12,18,16,12,14,16,20]),(p,[18,12,12]),(x,[5,48,46,22,16])):
    for i,wd in enumerate(w): ws.column_dimensions[chr(65+i)].width=wd
    for row in ws.iter_rows():
        for c in row:
            if c.font==Font() or not c.font.bold: c.font=N
            if c.value is not None and c.row<=15: c.border=BD
            c.alignment=Alignment(vertical="center",wrap_text=True)
    for c in ws[1]: c.font=H; c.fill=HF
    ws.freeze_panes="A2"
x["B16"].font=B
wb.save("Excel_Practice_ulvyi.xlsx")
