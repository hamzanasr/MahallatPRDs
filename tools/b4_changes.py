# -*- coding: utf-8 -*-
"""ما تغيّر عن الإصدار 3.3 + مسائل للمالك."""
import json, re, os, collections
from b4_common import *
import b4_decisions as DEC

OLD = {r['k']: r for r in json.load(open(os.path.join(HERE, 'lite', 'req_all.json'), encoding='utf8'))}


def plain(h):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', h)).strip()


def norm(s):
    s = plain(s)
    s = re.sub(r'\(\s+', '(', s)
    s = re.sub(r'\s+\)', ')', s)
    return re.sub(r'[\s؛،,.:]+', ' ', s).strip()


GROUPS = [
    ('Taxi', [i for i in OLD if i.startswith('TAX-')] + ['REG-009']),
    ('الامتثال والتراخيص', ['REG-001', 'REG-003', 'REG-004', 'REG-007', 'REG-008', 'FLT-005', 'INT-006', 'PHR-001', 'PHR-002', 'PHR-006', 'CUS-012']),
    ('البيانات الغذائية والحساسية', ['REG-002', 'CUS-014', 'CUS-019', 'MER-025']),
    ('ميزات أخرى', ['CUS-017', 'CUS-018', 'CUS-022', 'DRV-010']),
]

KEY_CHANGES = [  # كل بند تحققت منه بمقارنة النصين
    ('المارت', 'كان الطلب يمر على بقالات متتابعة باسم مخفي. صار العميل يختار بقالة محددة ولا ينتقل الطلب لغيرها ولا يُخفى اسمها.', ['DSP-005', 'ORD-006', 'MER-031', 'MER-010', 'CAT-001']),
    ('الغرامات', 'كانت الغرامات تُخصم آلياً بالتأخر أو الإلغاء. صارت يدوية فقط: يقررها موظف الدعم بسبب مكتوب ودليل ويحدد من يتحملها، ولا خصم آلي.', ['PAY-025', 'ORD-004', 'ORD-007', 'ORD-012', 'PAY-026', 'DRV-023']),
    ('أكواد التسليم والعمليات', 'كان للعميل كود تسليم يظهر ويُحفظ، وكان في عدم التجاوب «كود عمليات». لا كود للعميل الآن ولا كود عمليات؛ يؤكد المندوب التسليم داخل 100 متر بدليل، ويراجع الدعم الأدلة ثم يصعّد للمخول.', ['CUS-007', 'ORD-005', 'ORD-008', 'ADM-043']),
    ('وقت الوصول', 'كان وقتان: تحضير قبل الاستلام وتوصيل بعده. صار مدة واحدة = أطول تحضير + طريق المتجر إلى العميل + 5 دقائق.', ['ORD-011', 'CUS-007']),
    ('تجميع الطلبات', 'تغيرت الشروط الافتراضية (3 طلبات و3 كم و3 كم و10 دقائق) وأُضيف جواز إضافة طلب في أي مرحلة.', ['DSP-003']),
    ('المنيو والمناوبات', 'تُدار المناوبات من صفحة التاجر في الإدارة، ولكل منتج وقت توفر، ويمكن تشغيل منيو واحد بلا تقسيم.', ['MER-005', 'MER-053', 'MER-046']),
    ('Taxi', 'من قسم كامل (26 متطلباً) إلى بنية مؤجلة بلا تشغيل.', ['TAX-FND']),
    ('الأدوار والصلاحيات', 'أدوار جاهزة يعدّلها الأدمن أو ينشئ غيرها. بعد مهلة 60 ثانية لا يُلغى الطلب إلا عبر الدعم، وموظف الدعم يرد المبلغ ويحدد الغرامة ومن يتحملها. لا كود عمليات.', ['ADM-001', 'ADM-043', 'ORD-004']),
]


def diff_html(rid):
    o = OLD[rid]
    n = REQ[rid]
    o_all = [plain(x) for x in o['rules'] + o['acc']]
    n_all = n['rules'] + n['acceptance']
    on = {norm(x) for x in o_all}
    nn = {norm(x) for x in n_all}
    gone = [x for x in o_all if norm(x) not in nn]
    came = [x for x in n_all if norm(x) not in on]
    if not gone and not came:
        return None
    return ('<details class="chg" id="chg-%s"><summary><a class="rid" href="#%s">%s</a> %s</summary><div class="cmp">'
            '<div><h5>في 3.3 وغاب أو تغيّر</h5><ul>%s</ul></div><div><h5>في الجديد</h5><ul>%s</ul></div></div></details>') % (
        rid, rid, rid, esc(n['title']), ''.join('<li>%s</li>' % esc(x) for x in gone) or '<li>—</li>', ''.join('<li>%s</li>' % fmt(x) for x in came) or '<li>—</li>')


def changes_section(num):
    common = sorted(set(OLD) & set(REQ))
    removed = sorted(set(OLD) - set(REQ))
    added = sorted(set(REQ) - set(OLD))
    grouped = set(i for _, ids in GROUPS for i in ids)
    assert grouped == set(removed), (grouped ^ set(removed))
    diffs = [(i, diff_html(i)) for i in common]
    rewritten = [h for i, h in diffs if h]
    same = len(common) - len(rewritten)
    summary = tbl(['', 'العدد'], [
        ['متطلبات الإصدار 3.3', str(len(OLD))], ['متطلبات هذا الإصدار', str(len(REQ))],
        ['غير موجودة في الجديد', str(len(removed))], ['جديدة', str(len(added))],
        ['بقيت دون تغيير في النص', str(same)], ['تغيّر نصها (قواعد أو معايير)', str(len(rewritten))],
        ['صفحات الواجهات', '%d (لم تكن الصفحات مفصّلة بهذا الشكل في 3.3)' % len(D['pages'])],
    ])
    key = tbl(['الموضوع', 'ما تغيّر', 'المتطلبات'], [['<b>%s</b>' % esc(a), esc(b), refs_html(c)] for a, b, c in KEY_CHANGES])
    rem = ''
    for name, ids in GROUPS:
        ids = sorted(ids)
        rem += '<details class="chg-grp"><summary><b>%s</b> <span class="cnt">%d</span></summary><ul>%s</ul></details>' % (
            esc(name), len(ids), ''.join('<li><bdi class="rid">%s</bdi> %s</li>' % (i, esc(OLD[i]['t'])) for i in ids))
    add = ''.join('<li>%s</li>' % req_link(i) for i in added)
    return ('<section id="changes"><h2><span class="num">%d</span>ما تغيّر عن 3.3</h2>'
            '<p class="sub">مقارنة بين الإصدار 3.3 وملف المتطلبات الجديد، لتتأكد أن كل تغيير مقصود، ولترى ما كان في 3.3 وغاب. المقارنة نصية: قد يكون التغيير في الصياغة فقط، والفيصل المتطلب في الفهرس.</p>'
            '<h3>الخلاصة</h3>%s<h3>أهم التغييرات</h3>%s<h3>متطلبات غير موجودة في الجديد</h3>'
            '<p>لم يعد لها متطلب مستقل. إن كان أحدها قد دُمج في متطلب آخر فلا يظهر ذلك في هذه المقارنة.</p>%s'
            '<h3>متطلبات جديدة</h3><ul class="reqlist">%s</ul>'
            '<h3>متطلبات تغيّر نصها</h3><p>اضغط المتطلب لترى ما في 3.3 ولم يعد بنصه، وما يقابله في الجديد (التطابق حرفي بعد تسوية الفواصل، فقد تظهر صياغة جديدة لمعنى واحد).</p>%s</section>') % (
        num, summary, key, rem, add, ''.join(rewritten))


# ---------------------------------------------------------------- مسائل للمالك
KIND_LABEL = {'conflict': 'تعارض', 'ambiguity': 'غموض', 'fragment': 'بند ناقص', 'acceptance': 'معيار قبول', 'duplicate': 'تكرار', 'editorial': 'بقايا تحرير', 'typo': 'خطأ كتابة'}


def notes_section(num, notes, log):
    # المسائل المهمة حُسمت كلها أو استُبدلت بما بقي بعد قرارات 5 أكتوبر
    n_res = len(DEC.RESOLVED_KEY) + len(DEC.RESOLVED_NOTES)
    notes = [n for i, n in enumerate(notes) if not n['key'] and i not in DEC.RESOLVED_NOTES]
    krows = [[str(i + 1), refs_html([rid]), fmt(t)] for i, (rid, t) in enumerate(DEC.PENDING)]
    top = tbl(['#', 'المتطلب', 'السؤال'], krows, 'tbl-notes')
    key = DEC.PENDING
    by = collections.OrderedDict()
    for m, name in MODULES:
        items = [n for n in notes if n['ids'][0].startswith(m + '-') and not n['key']]
        if items:
            by[m] = items
    rest = ''
    for m, items in by.items():
        rows = [[refs_html(n['ids']), '<b>%s</b> %s' % (KIND_LABEL[n['kind']], fmt(n['text'])), fmt(n['ask'])] for n in items]
        rest += '<details class="rep"><summary><b>%s</b> <span class="cnt">%d</span></summary>%s</details>' % (esc(MOD_NAME[m]), len(items), tbl(['المتطلبات', 'المسألة', 'السؤال أو الاقتراح'], rows, 'tbl-notes'))
    lrows = [['<a class="rid" href="#%s">%s</a>' % (e['id'], e['id']), esc(e['old']), esc(e['new']) if e['new'] else '<i>حُذف</i>', esc(e['why'])] for e in log]
    edits = tbl(['المتطلب', 'قبل', 'بعد', 'السبب'], lrows, 'tbl-notes')
    return ('<section id="notes"><h2><span class="num">%d</span>مسائل للمالك</h2>'
            '<p class="sub">راجعتُ نص المتطلبات بحثاً عمّا يترك المبرمج يخمّن: تعارض بين متطلبين، وغموض، وبند ناقص، وتكرار قد يتباعد. حسمت قرارات 5 أكتوبر ' + str(n_res) + ' مسألة وكُتبت في المتطلبات. ما بقي هنا، وما كان تصحيحاً لغوياً خالصاً طبّقته وسجّلته في الجدول الأخير.</p>'
            '<h3>بقي مفتوحاً بعد قرارات 5 أكتوبر (%d)</h3><p>أسئلة لم تُحسم، وافتراضات كتبتها في المتطلبات وتحتاج تأكيدك. يُفضَّل حسمها قبل برمجة المتطلب.</p>%s'
            '<h3>بقية المسائل حسب الوحدة (%d)</h3>%s'
            '<h3>تصحيحات لغوية طبّقتها (%d)</h3><p>لا تغيّر قراراً: إكمال بنود ناقصة، وإزالة بقايا تحرير وتكرار صريح، وتصحيح فاعل أو ضمير. النص الأصلي في عمود «قبل».</p>%s</section>') % (
        num, len(key), top, len(notes), rest, len(log), edits)
