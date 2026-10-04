# -*- coding: utf-8 -*-
"""تحقق: كل ما في ملف المالك موجود في الموقع الجديد."""
import json, re, sys
from bs4 import BeautifulSoup
D = json.load(open('newprd.json', encoding='utf8'))
site = sys.argv[1] if len(sys.argv) > 1 else '../index.html'
h = open(site, encoding='utf8').read()
s = BeautifulSoup(h, 'lxml')
for m in s.select('.mock'): m.decompose()
bad = 0
def nums(t): return sorted(re.findall(r'\d+(?:[.,]\d+)?', re.sub(r'\b[A-Z]{3}-\d{2,3}\b', ' ', t)))
def norm(t): return re.sub(r'[\s]+', ' ', t).strip()

# المتطلبات
req = {d['id']: d for d in s.select('#catalog details.req')}
print('requirements', len(req), 'of', len(D['requirements']))
fixes = json.load(open('qa/fixes.json', encoding='utf8'))
for r in D['requirements']:
    d = req.get(r['id'])
    if not d: print('MISSING', r['id']); bad += 1; continue
    got = [norm(x.get_text(' ')) for x in d.select('.rbody li')]
    src = fixes.get(r['id'], {}).get('rules', r['rules']) + fixes.get(r['id'], {}).get('acceptance', r['acceptance'])
    if len(got) != len(src): print('COUNT', r['id'], len(got), len(src)); bad += 1
    orig_nums = nums(' '.join(r['rules'] + r['acceptance']))
    if r['id'] not in fixes and nums(' '.join(got)) != orig_nums: print('NUMS', r['id']); bad += 1
    if d['data-p'] != {'launch': 'p1', 'important': 'p2', 'later': 'p3', 'foundation': 'p4'}[r['priority']]: print('PRI', r['id']); bad += 1
# الأرقام في المتطلبات المحرَّرة: أي رقم ضاع من المتطلب بعد التحرير؟
for rid, f in fixes.items():
    r = next(x for x in D['requirements'] if x['id'] == rid)
    a = nums(' '.join(r['rules'] + r['acceptance'])); b = nums(' '.join(f['rules'] + f['acceptance']))
    import collections
    lost = collections.Counter(a) - collections.Counter(b)
    if lost: print('EDIT-LOST-NUMBERS', rid, dict(lost))
# الصفحات
pages = {d['id']: d for d in s.select('details.page')}
print('pages', len(pages), 'of', len(D['pages']))
for p in D['pages']:
    d = pages.get('p-' + p['id'])
    if not d: print('PAGE MISSING', p['id']); bad += 1; continue
    t = d.get_text(' ')
    for x in p['fields'] + p['actions']:
        if norm(x) not in norm(t): print('PAGE FIELD', p['id'], x); bad += 1
    for r in p['refs']:
        if not d.select('a[href="#%s"]' % r): print('PAGE REF', p['id'], r); bad += 1
    for l in p['links']:
        if not d.select('a[href="#p-%s"]' % l): print('PAGE LINK', p['id'], l); bad += 1
# الإعدادات
txt = norm(s.find(id='settings').get_text(' '))
for a, b, c in D['settings']:
    if norm(a) not in txt or norm(b).replace('؛', ' ')[:20] == '' : print('SETTING', a); bad += 1
print('settings rows', len(s.find(id='settings').select('tbody tr')), 'of', len(D['settings']))
print('integrations rows', len(s.find(id='integrations').select('tbody tr')), 'of', len(D['integrations']))
print('quality rows', len(s.find(id='quality').select('tbody tr')), 'of', len(D['quality']))
print('reports', sum(len(sec.select('tbody tr')) for sec in s.select('details.rep#rep-merchant, details.rep#rep-admin')), 'of', sum(len(v) for v in D['reports'].values()))
print('examples rows', len(s.find(id='money').select('table.tbl-ex tbody tr, .tbl-ex tbody tr')), 'of', len(D['financialExamples']))
print('flows', len(s.select('.flow-svg')), 'of', len(D['diagrams']))
ids = {e['id'] for e in s.find_all(id=True)}
print('broken links', sorted({a['href'] for a in s.select('a[href^="#"]') if a['href'][1:] and a['href'][1:] not in ids})[:10])
import collections
c = collections.Counter(e['id'] for e in s.find_all(id=True)); print('dup ids', [k for k, v in c.items() if v > 1][:5])
print('PROBLEMS', bad)
