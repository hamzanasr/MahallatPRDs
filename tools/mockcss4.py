# -*- coding: utf-8 -*-
"""يستخرج css المعاينات والمخططات من ملف المالك ويحصر كل قاعدة تحت .mock لتتجنب التعارض."""
import re
css = open('newcss.css', encoding='utf8').read()
a = css.find('MOCKUPS'); a = css.rfind('/*', 0, a)
b = css.find('Responsive'); b = css.rfind('/*', 0, b)
mock = css[a:b]
resp = css[b:]
dg_a = css.find('diagrams'); dg_a = css.rfind('/*', 0, dg_a)
dg_b = css.find('phone', dg_a + 20); dg_b = css.rfind('/*', 0, dg_b)
diag = css[dg_a:dg_b]

def split_rules(s):
    """يقسم النص إلى قواعد على المستوى الأعلى مع دعم @media المتداخلة."""
    out, depth, cur = [], 0, ''
    for ch in s:
        cur += ch
        if ch == '{': depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                out.append(cur.strip()); cur = ''
    return out

def scope_sel(sel, prefix):
    parts = [p.strip() for p in sel.split(',') if p.strip()]
    res = []
    for p in parts:
        if p.startswith(('@', 'from', 'to')) or re.match(r'^\d+%$', p): res.append(p); continue
        if p in (':root', 'html', 'body'): res.append(prefix); continue
        res.append(prefix + ' ' + p)
    return ','.join(res)

def scope(rules, prefix, in_media=False):
    out = []
    for r in rules:
        r = re.sub(r'/\*.*?\*/', '', r, flags=re.S).strip()
        if not r: continue
        head, body = r.split('{', 1)
        head = head.strip()
        if head.startswith('@media') or head.startswith('@supports'):
            inner = body.rsplit('}', 1)[0]
            out.append(head + '{' + scope(split_rules(inner), prefix, True) + '}')
        elif head.startswith('@keyframes') or head.startswith('@font-face'):
            out.append(r)
        else:
            out.append(scope_sel(head, prefix) + '{' + body)
    return '\n'.join(out)

# قواعد @media في جزء الاستجابة التي تخص المعاينات فقط
resp_rules = [r for r in split_rules(resp) if re.search(r'\.(mk|phone|desk|m-|d-)', r)]
final = '/* معاينات الواجهات — مستخرجة من ملف المالك ومحصورة تحت .mock */\n.mock{--f-body:"IBM Plex Sans Arabic","Segoe UI",Tahoma,Arial,sans-serif;--f-display:"Readex Pro","IBM Plex Sans Arabic","Segoe UI",Tahoma,sans-serif;--paper:#F3F6F5;--surface:#fff;--ink:#10282A;--line:#DCE4E1;--line-2:#C9D4D0;--brand:#0A6B5C}\n'
final += scope(split_rules(mock), '.mock') + '\n' + scope(resp_rules, '.mock')
open('mock4.css', 'w', encoding='utf8').write(final)
open('diagram4.css', 'w', encoding='utf8').write(diag)
print('mock4.css', len(final), 'diag chars', len(diag), 'resp rules kept', len(resp_rules))
