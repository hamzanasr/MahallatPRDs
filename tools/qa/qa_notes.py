# -*- coding: utf-8 -*-
import json, re
D = json.load(open('newprd.json', encoding='utf8'))
ids = {r['id'] for r in D['requirements']}
allf = json.load(open('qa/all_findings.json', encoding='utf8'))
own = [x for x in allf if x.get('owner')]
KEY = [20, 21, 22, 4, 1, 7, 12, 82, 23, 24, 30, 27, 39, 59, 64, 60, 65, 121, 122, 123, 140, 141, 98, 156]
IDRE = re.compile(r'\b[A-Z]{3}-\d{2,3}\b|TAX-FND')

def clean(s):
    s = re.sub(r'\s+', ' ', s).strip()
    s = re.sub(r'\(\s+', '(', s); s = re.sub(r'\s+\)', ')', s)
    return s

def cut(s, n):
    s = clean(s)
    if len(s) <= n: return s
    t = s[:n]
    k = max(t.rfind('. '), t.rfind('؟ '), t.rfind('؛ '))
    return (t[:k + 1] if k > n * 0.5 else t.rstrip()) + ' …'

out = []
for k, x in enumerate(own):
    refs = [x['id']] + [i for i in dict.fromkeys(IDRE.findall(x['problem'] + ' ' + x['fix'])) if i in ids and i != x['id']][:4]
    out.append({'kind': x['kind'], 'ids': refs, 'text': cut(x['problem'], 520), 'ask': cut(x['fix'], 460), 'key': k in KEY, 'order': KEY.index(k) if k in KEY else 999})
json.dump(out, open('qa/notes.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print(len(out), sum(1 for o in out if o['key']))
