# -*- coding: utf-8 -*-
"""أدوات مشتركة لبناء موقع المتطلبات (الإصدار 4) من ملف المالك."""
import json, re, os, html
HERE = os.path.dirname(os.path.abspath(__file__))

import copy
import b4_decisions as DEC

D = json.load(open(os.path.join(HERE, 'newprd.json'), encoding='utf8'))
D_ORIG = copy.deepcopy(D)  # ملف المالك كما وصل، للمقارنة والتحقق

# 1) التصحيحات اللغوية المعتمدة  2) قرارات المالك. كلاهما يُكتب في نص المتطلب نفسه.
_fx = os.path.join(HERE, 'qa', 'fixes.json')
FIXES = json.load(open(_fx, encoding='utf8')) if os.path.exists(_fx) else {}
DEC_LOG = []  # (المعرّف, قرارات, القواعد قبل, القبول قبل, الأولوية قبل)
for _r in D['requirements']:
    _f = FIXES.get(_r['id'])
    if _f:
        _r['rules'], _r['acceptance'] = list(_f['rules']), list(_f['acceptance'])
    _d = DEC.REQ.get(_r['id'])
    if _d:
        DEC_LOG.append((_r['id'], _d['dec'], list(_r['rules']), list(_r['acceptance']), _r['priority']))
        if _d.get('rules') is not None:
            _r['rules'], _r['acceptance'] = list(_d['rules']), list(_d['acceptance'])
        if _d.get('priority'):
            _r['priority'] = _d['priority']
assert {x[0] for x in DEC_LOG} == set(DEC.REQ), set(DEC.REQ) - {x[0] for x in DEC_LOG}
SETTING_REFS_ADD = []
for _i, _row in DEC.SETTING_EDITS.items():
    D['settings'][_i] = list(_row)
for _a, _b, _c, _g, _refs in DEC.SETTING_ADD:
    D['settings'].append([_a, _b, _c])
    SETTING_REFS_ADD.append((len(D['settings']) - 1, _g, _refs))
for _pid, _k, _old, _new in DEC.PAGE_EDITS:
    _p = next(p for p in D['pages'] if p['id'] == _pid)
    _p[_k] = [_new if x == _old else x for x in _p[_k]]
    assert _new in _p[_k]

# 3) مراجعة الصفحات: عناصر ناقصة، وسلوك الإجراءات، وصفحات جديدة، ومعاينات محسّنة
import b4_ux as UXM
UX_MOCKS, UX_MOCKS2 = UXM.apply(D, {r['id'] for r in D['requirements']}, HERE)

PRI = {'launch': ('p1', 'أساسي للإطلاق'), 'important': ('p2', 'مهم'), 'later': ('p3', 'لاحقاً'), 'foundation': ('p4', 'بنية مؤجلة')}
PRI_ORDER = ['launch', 'important', 'later', 'foundation']

MODULES = [  # (البادئة, الاسم, المجموعة في الملف)
    ('REG', 'الامتثال: برنامج «هدف»'), ('CUS', 'تطبيق العميل'), ('CRT', 'السلة والدفع'), ('ORD', 'دورة الطلب'),
    ('PAY', 'الدفع والرسوم والتسويات'), ('CAT', 'كتالوج المارت'), ('MER', 'التاجر والفروع'), ('DRV', 'المندوب'),
    ('DSP', 'التوزيع والمدن'), ('FLT', 'شركات التوصيل'), ('ADM', 'الإدارة'), ('SUP', 'الدعم'),
    ('MKT', 'العروض والإعلانات والولاء'), ('EXT', 'الخدمات'), ('INT', 'الربط مع الخدمات'), ('PHR', 'الصيدليات'),
    ('REP', 'التقارير'), ('SYS', 'البناء والتشغيل'), ('TAX', 'Taxi'),
]
MOD_NAME = dict(MODULES)

SURF = [  # (المعرّف في الملف, الاسم, الوصف, رمز الصفحات)
    ('customer', 'تطبيق العميل', 'المتاجر والسلة والطلب والتتبع والرصيد.', 'C'),
    ('merchant', 'تطبيق التاجر', 'التجهيز والتسليم والمنيو والفريق.', 'M'),
    ('merchant-dash', 'لوحة التاجر', 'التقارير والمستحقات والفروع والصلاحيات (موقع ويب).', 'MD'),
    ('driver', 'تطبيق المندوب', 'المهام والاستلام والتسليم والأداء والأرباح.', 'D'),
    ('admin', 'لوحة الإدارة', 'التشغيل وملف التاجر والحسابات والدعم والإعدادات.', 'A'),
]
SURF_NAME = {s[0]: s[1] for s in SURF}

REQ = {r['id']: r for r in D['requirements']}
PAGES = {p['id']: p for p in D['pages']}
USED = {}
for p in D['pages']:
    for r in p['refs']:
        USED.setdefault(r, []).append(p['id'])


def esc(s):
    return html.escape(str(s), quote=False)


def attr(s):
    return html.escape(str(s), quote=True)


ID_RE = re.compile(r'(?<![\w-])((?:[A-Z]{3}-\d{2,3})|TAX-FND|CFG-01|DATA-01|INT-SEL|D-\d{2})(?![\w-])')


def link_ids(text):
    """يحوّل معرّفات المتطلبات داخل نص (بعد الهروب) إلى روابط."""
    def rep(m):
        i = m.group(1)
        if i in REQ:
            return '<a class="rid" href="#%s">%s</a>' % (i, i)
        if i in ('CFG-01', 'INT-SEL', 'DATA-01'):
            return '<a class="rid" href="#prelaunch">%s</a>' % i
        return '<bdi class="rid">%s</bdi>' % i
    return ID_RE.sub(rep, text)


def fmt(text):
    """نص عادي → HTML آمن مع روابط المعرّفات ونظافة الفراغات حول الأقواس."""
    t = esc(text)
    t = re.sub(r'\(\s+', '(', t)
    t = re.sub(r'\s+\)', ')', t)
    t = re.sub(r'\s{2,}', ' ', t).strip()
    return link_ids(t)


def tag(pri):
    k, label = PRI[pri]
    return '<span class="tag %s">%s</span>' % (k, label)


def req_link(i, title=True):
    r = REQ.get(i)
    if not r:
        return '<bdi class="rid">%s</bdi>' % esc(i)
    return '<a class="rid" href="#%s">%s</a>%s' % (i, i, (' ' + esc(r['title'])) if title else '')


def tbl(head, rows, cls=''):
    h = ''.join('<th>%s</th>' % c for c in head)
    b = ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % c for c in r) for r in rows)
    return '<div class="tbl %s"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (cls, h, b)


def refs_html(ids):
    return ' · '.join('<a class="rid" href="#%s">%s</a>' % (i, i) if i in REQ else '<bdi class="rid">%s</bdi>' % i for i in ids)


def lines(text):
    """يفصل المقاطع المفصولة بـ«؛» إلى أسطر ليسهل مسح القيم المضغوطة."""
    parts = [p.strip() for p in re.split(r'[؛;]', str(text)) if p.strip()]
    return '<br>'.join(fmt(p) for p in parts)
