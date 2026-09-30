# -*- coding: utf-8 -*-
"""تحرير الصياغة: يستخرج كتل النص من الصفحة، ويطبّق النسخ المحررة (tools/edits/*.json) بعد التحقق الآلي من سلامتها."""
import os, re, json, glob, hashlib, sys
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
EDIT_DIR = os.path.join(HERE, 'edits')
SKIP_SECTIONS = {'start', 'scope', 'decisions', 'glossary', 'changelog', 'shared-rules', 'taxi'}
DUMP = os.environ.get('LANG_DUMP') == '1'
BLOCKS = {}
APPLIED = {'n': 0}
_edits = None


def _load():
    global _edits
    if _edits is None:
        _edits = {}
        for f in sorted(glob.glob(os.path.join(EDIT_DIR, '*.json'))):
            _edits.update(json.load(open(f, encoding='utf8')))
    return _edits


def key(inner):
    return hashlib.sha1(inner.encode('utf8')).hexdigest()[:12]


def candidates(frag):
    for e in frag.find_all(['li', 'p', 'td', 'h3', 'h4', 'h5']):
        if e.find_parent(class_='mock') or e.find_parent('thead'):
            continue
        if e.name == 'td' and e.find(['ul', 'ol', 'table', 'div']):
            continue
        if e.name == 'li' and e.find(['li', 'ul', 'ol']):
            continue
        inner = e.decode_contents().strip()
        if len(e.get_text(' ', strip=True)) < 28:
            continue
        yield e, inner


# ---------------------------------------------------------------- التحقق
def _nums(s):
    t = re.sub(r'<[^>]+>', ' ', s)
    return sorted(re.findall(r'\d+(?:[.,]\d+)?', t))


def _ids(s):
    return sorted(re.findall(r'\b[A-Z]{2,4}-\d{2,3}\b', re.sub(r'<[^>]+>', ' ', s)))


def _quotes(s):
    return re.findall(r'«[^»]+»', re.sub(r'<[^>]+>', '', s))


def _latin(s):
    return sorted(w.lower() for w in re.findall(r'[A-Za-z][A-Za-z0-9+]*', re.sub(r'<[^>]+>', ' ', s)) if len(w) > 1)


def _tags(s):
    return sorted(re.findall(r'<\s*/?\s*(?:b|bdi|a|span|i|em|small|strong|br)\b', s))


def valid(old, new):
    """يرفض أي تحرير يُسقط رقماً أو معرّفاً أو نصاً بين «» أو كلمة لاتينية، أو يغيّر الوسوم، أو يبالغ في التقصير."""
    if _nums(old) != _nums(new):
        return 'أرقام'
    if _ids(old) != _ids(new):
        return 'معرّفات'
    if _latin(old) != _latin(new):
        return 'لاتيني'
    if any(q not in _quotes(new) for q in _quotes(old)):
        return 'اقتباس'
    if _tags(old) != _tags(new):
        return 'وسوم'
    a, b = len(re.sub(r'<[^>]+>', '', old)), len(re.sub(r'<[^>]+>', '', new))
    if b < 0.55 * a or b > 1.7 * a:
        return 'طول'
    return None


def process(frag, sid):
    if sid in SKIP_SECTIONS:
        return
    ed = None if DUMP else _load()
    for e, inner in list(candidates(frag)):
        k = key(inner)
        if DUMP:
            BLOCKS[k] = {'s': sid, 'h': inner}
            continue
        new = ed.get(k)
        if new and new.strip() != inner and valid(inner, new) is None:
            e.clear()
            piece = BeautifulSoup('<x>' + new + '</x>', 'lxml').find('x')
            for c in list(piece.children):
                e.append(c)
            APPLIED['n'] += 1


def dump():
    if DUMP:
        json.dump(BLOCKS, open(os.path.join(HERE, 'lang_blocks.json'), 'w', encoding='utf8'), ensure_ascii=False)
        print('dumped', len(BLOCKS), 'blocks')
