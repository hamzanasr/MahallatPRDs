import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import re
raw=open(__import__('sys').argv[1] if len(__import__('sys').argv)>1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),'delivery-spec.html'),encoding='utf8').read()
raw=raw[raw.index('/* ---- product palette (fixed) ---- */'):]
raw=raw[:raw.index('</style>')]
def cut(txt,start,end):
    i=txt.index(start); j=txt.index(end,i)
    return txt[:i]+txt[j:]
# مقاطع خاصة بالصفحة لا بالنماذج
css=cut(raw,'.new.upd{','/* ---- v3.2 dashboard mockups ---- */')
css=cut(css,'/* ---- page tabs + spec cards (page theme) ---- */','.mhd{')
css=re.sub(r'/\*.*?\*/','',css,flags=re.S)
# rule splitter
rules=[];depth=0;buf='';
for ch in css:
    buf+=ch
    if ch=='{': depth+=1
    elif ch=='}':
        depth-=1
        if depth==0:
            rules.append(buf.strip()); buf=''
page=re.compile(r'^(tr\.grp|\.money|\.opts|\.pmap|\.ppanel|\.pframe|\.pnext|\.modmap|\.jleg|\.mk-|\.new(?![\w-])|\.dst|\.dnote|details\.|tr\.wait|\.fil(?![\w-])|\.ptl|\.pspec|\.gloss|\.rep-g|\.kpis|\.comp(?![\w-])|\.srcl|#sources|\.cat-tools|\.mod\b|\.src(?![\w-])|\.vh(?![\w-])|\.ptabs)')
def scope(sel):
    out=[]
    for part in sel.split(','):
        p=part.strip()
        if not p: continue
        out.append('.mock '+p)
    return ','.join(out)
res=[]
dropped=[]
for r in rules:
    m=re.match(r'([^{]+)\{(.*)\}$',r,flags=re.S)
    if not m: continue
    sel,body=m.group(1).strip(),m.group(2)
    if sel.startswith('@media'):
        inner=[x for x in re.findall(r'([^{}]+)\{([^{}]*)\}',body)]
        ins=''.join(scope(a.strip())+'{'+b+'}' for a,b in inner if not page.match(a.strip()))
        if ins and 'min-width:981px' in sel: res.append(sel+'{'+ins+'}')
        continue
    parts=[p.strip() for p in sel.split(',')]
    if all(page.match(p) for p in parts): dropped.append(sel); continue
    parts=[p for p in parts if not page.match(p)]
    # :root-type or body rules not expected
    res.append(scope(','.join(parts))+'{'+body.strip()+'}')
out='\n'.join(res)
# the .mk-shot zoom media
out=out.replace('.mock .mk-shot .wb.wx','.mock .wb.wx')
open(os.path.join(ROOT,'assets','mock.css'),'w',encoding='utf8').write('/* نماذج الشاشات المرسومة: كل القواعد مقيّدة بـ .mock حتى لا تتأثر بقية الصفحة */\n'+out+'\n')
print(len(res),'rules',len(out),'bytes; dropped',len(dropped)); print(dropped[:40])
