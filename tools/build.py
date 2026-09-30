# -*- coding: utf-8 -*-
"""يبني موقع مواصفات منصة التوصيل من الملف الأصلي (source.html) بعد حذف المكرر وما لا داعي له."""
import re, html, json, os, sys
from bs4 import BeautifulSoup, NavigableString, Tag

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'delivery-spec.html')
OUT = os.path.dirname(HERE)

soup = BeautifulSoup(open(SRC, encoding='utf8').read(), 'lxml')
for t in soup(['style', 'script']):
    t.decompose()
main = soup.find('main')
S = {x['id']: x for x in main.find_all('section', recursive=False)}
import patches
import lang
patches.patch_sections(S, soup)
import review
review.fix_sections(S, soup)
import review_front, review_more
review_more.extract_shared(S, soup)
review_more.finance_and_wording(S, soup)
review_more.taxi_launch(S, soup)


# ------------------------------------------------------------------ helpers
def norm(t):
    return re.sub(r'\s+', ' ', t or '').strip()


def esc(t):
    return html.escape(t, quote=False)


def inner(el):
    return ''.join(str(c) for c in el.children)


def clone(el):
    return BeautifulSoup(str(el), 'lxml').find(el.name)


def drop(el):
    if el is not None:
        el.decompose()


def drop_starting(root, prefix, tags='li,p,div', expect=1):
    """يحذف عناصر يبدأ نصها بـ prefix. يتأكد من عدد المطابقات حتى لا يُحذف شيء بالخطأ."""
    hits = [e for e in root.select(tags) if norm(e.get_text(' ')).startswith(prefix)]
    hits = [e for e in hits if not any(o is not e and any(a is e for a in o.parents) for o in hits)]
    assert len(hits) == expect, (prefix, len(hits))
    for e in hits:
        e.decompose()


def h3_block_remove(root, title):
    """يحذف h3 وما يليه حتى h3 التالي."""
    h = [x for x in root.find_all('h3') if norm(x.get_text()) == title]
    assert len(h) == 1, title
    h = h[0]
    nxt = h.next_sibling
    while nxt is not None and not (isinstance(nxt, Tag) and nxt.name in ('h3', 'h2', 'figure')):
        n2 = nxt.next_sibling
        if isinstance(nxt, Tag):
            nxt.decompose()
        nxt = n2
    h.decompose()


def html_to_tag(s):
    return BeautifulSoup(s, 'lxml').body.find(True)


# ------------------------------------------------------------------ الفهرس (المتطلبات)
cat = S['catalog']
MODS = []          # [{code,name,reqs:[...]}]
REQ_IDS = set()
for mod in cat.select('#mods > div.mod'):
    h = mod.find('h3')
    code = h.find(class_='rid').get_text(strip=True)
    name = norm(h.get_text(' ').replace(code, ''))
    m = {'code': code, 'name': name, 'reqs': []}
    for d in mod.select('details.req'):
        sm = d.find('summary')
        rid = sm.find(class_='rid').get_text(strip=True)
        st = sm.find(class_='st')
        tags = [norm(t.get_text()) for t in st.select('.tag')]
        for t in st.select('.tag'):
            t.extract()
        title = norm(st.get_text(' '))
        sections = {}
        for div in d.select('.body > div'):
            hd = norm(div.find('h5').get_text())
            sections[hd] = ''.join(str(li) for li in div.select('ul > li'))
        m['reqs'].append({'id': rid, 'title': title, 'tags': tags,
                          'rules': sections.get('القواعد', ''), 'accept': sections.get('معيار القبول', '')})
        REQ_IDS.add(rid)
    MODS.append(m)
MODS = patches.patch_catalog(MODS)
MODS = review.fix_catalog(MODS)
MODS = review_more.catalog_wording(MODS)
MODS = review_more.taxi_catalog(MODS)
REQ_IDS = {r['id'] for m in MODS for r in m['reqs']}
N_REQ = sum(len(m['reqs']) for m in MODS)
assert N_REQ == 267 - 15 + 3, N_REQ


def prio(tags):
    if 'أساسي للإطلاق' in tags: return 'p1'
    if 'مهم' in tags: return 'p2'
    return 'p3'


def linkify(root):
    """يحوّل معرّفات المتطلبات (مثل ORD-003) إلى روابط تفتح المتطلب في الفهرس."""
    pat = re.compile(r'\b([A-Z]{3}-\d{3})\b')
    for txt in list(root.find_all(string=True)):
        if txt.parent.name in ('a', 'script', 'style') or txt.find_parent(class_='mock'):
            continue
        if not pat.search(txt):
            continue
        parts = pat.split(txt)
        frag = []
        for i, p in enumerate(parts):
            if i % 2 == 0:
                if p: frag.append(NavigableString(p))
            elif p in REQ_IDS:
                a = soup.new_tag('a', href='#' + p)
                a['class'] = 'rid'
                a.string = p
                frag.append(a)
            else:
                frag.append(NavigableString(p))
        for f in frag:
            txt.insert_before(f)
        txt.extract()
    for b in root.select('bdi.rid'):
        if b.parent.name == 'a' or b.find_parent(class_='mock'):
            continue
        t = b.get_text(strip=True)
        if t in REQ_IDS:
            a = soup.new_tag('a', href='#' + t)
            a['class'] = 'rid'
            a.string = t
            b.replace_with(a)


# ------------------------------------------------------------------ تنظيف أقسام القواعد
def base_clean(sec):
    """حذف الرسوم التوضيحية (تكرار للجداول) والفواصل الشكلية."""
    for f in sec.select('figure'):
        f.decompose()
    for e in sec.select('.pnext,.flist,.jleg'):
        e.decompose()
    h2 = sec.find('h2')
    if h2:
        h2.decompose()
    return sec


def get(sid):
    return base_clean(S[sid])


SECTIONS = []   # (id, title, part, html)


def add(sid, title, part, body_html):
    SECTIONS.append({'id': sid, 'title': title, 'part': part, 'html': body_html})


def sec_html(sec):
    return inner(sec)


# ---------------- 1. أقسام البداية (ابدأ من هنا، النطاق، القرارات المفتوحة، المصطلحات)
for _d in review_front.front_sections(MODS):
    add(_d['id'], _d['title'], _d['part'], _d['html'])

# ---------------- 2. المنصة في صفحة
sec = get('overview')
sec.find('p', class_='sub')
add('overview', 'المنصة في صفحة', 'البداية', sec_html(sec))

# ---------------- 3. رحلة الطلب
sec = get('journey')
sub = sec.find('p', class_='sub')
sub.string = 'ثلاثة أنواع طلبات، ولكل نوع دورة كاملة: كل حالة، ومن ينقلها، ومهلتها، وما يخرج عن المسار. عمود «ما يراه العميل» هو النص الظاهر له.'
tabs = sec.select_one('.ptabs')
pieces = []
for p in tabs.select('.ppanel'):
    for h4 in p.find_all('h4'):
        if norm(h4.get_text()) == 'من يفعل ماذا':
            h4.decompose()
    for f in p.select('figure'):
        f.decompose()
    # ندمج «المسار الأساسي» بلا الإشارة للرسم: الفقرة الأولى تبقى كما هي
    h3 = p.find('h3')
    pieces.append('<div class="jtype" id="%s"><h3>%s</h3>%s</div>' % (
        p['id'], inner(h3), ''.join(str(c) for c in p.find_all(recursive=False) if c is not h3)))
tabs.replace_with(html_to_tag('<div class="jflow">' + ''.join(pieces) + '</div>'))
add('journey', 'رحلة الطلب بكل أنواعه', 'قواعد العمل', sec_html(sec))

# ---------------- 4. مدة التحضير والأوقات والغرامات
add('merchant-time', 'مدة التحضير والأوقات والغرامات', 'قواعد العمل', sec_html(get('merchant-time')))

# ---------------- 5. الاستلام والتوصيل والتسليم
add('arrival', 'الاستلام والتوصيل والتسليم', 'قواعد العمل', sec_html(get('arrival')))

# ---------------- 6. الاستلام الذاتي
add('pickup', 'الاستلام الذاتي', 'قواعد العمل', sec_html(get('pickup')))

# ---------------- 7. الإلغاء والاسترداد
add('cancel', 'الإلغاء والاسترداد', 'قواعد العمل', sec_html(get('cancel')))

# ---------------- 8. المتاجر والمنيو
sec = get('stores')
types_table = '''
<div class="tbl"><table><thead><tr><th>نوع التشغيل</th><th>نموذج الرسوم</th><th>القسم في تطبيق العميل</th></tr></thead><tbody>
<tr><td><b>مطاعم</b></td><td rowspan="2">عقد واحد: رسوم لكل عميل (2 أو 5 حتى 30 في السنة) أو نسبة أو بدون خصم · الزيادة على المنيو مستقلة · رسم الدفع 2.5% + 1</td><td>كافيه · مطعم · شعبي · بوفية</td></tr>
<tr><td><b>محلات متنوعة</b></td><td>قسم مستقل</td></tr>
<tr><td><b>مارت</b></td><td rowspan="2">مارت وصيدليات: 5% على العميل و5% من التاجر · طلبات الكتابة: نسبة المنصة على العميل وعقد المتجر</td><td>بقالة وغيرها</td></tr>
<tr><td><b>صيدليات</b></td><td>طلب كتابة ومراجعة صيدلي</td></tr>
</tbody></table></div>'''
sec.find('p', class_='sub').insert_after(html_to_tag(types_table))
add('stores', 'المتاجر والمنيو', 'قواعد العمل', sec_html(sec))

# ---------------- 9. طلبات الكتابة
add('text-orders', 'طلبات الكتابة', 'قواعد العمل', sec_html(get('text-orders')))

# ---------------- 10. الرسوم والأسعار
sec = get('fees')
h3_block_remove(sec, 'كل القيم مرنة')
h3_block_remove(sec, 'مسار الأموال')
# جملة «كل الأرقام مرنة» تبقى مرة واحدة بدل قائمة الأرقام المكررة في «القيم المرنة»
tbl = [t for t in sec.select('div.tbl')][-1]
note = html_to_tag('<div class="note">كل الأرقام في هذا القسم قيم افتراضية في الإعدادات، والمدير يعدّلها ويكتب لكل متجر قيمه الخاصة في عقده. القائمة الكاملة في «القيم المرنة»، والأمثلة الكاملة في «أمثلة العمليات المالية».</div>')
last_rule = tbl.find_next_sibling('ul')
last_rule.insert_after(note)
calc = html_to_tag('''<div><h3>ترتيب احتساب الطلب</h3><ol class="steps">
<li><div><b>هل الطلب من رابط منيو التاجر؟</b>نعم: بلا نسبة العقد لهذا الطلب فقط، ورسوم الخدمة ورسم الدفع يبقيان. الاستلام الذاتي: رسوم العقد نفسها، وخصم يحدد المدير من يتحمله.</div></li>
<li><div><b>سعر المنتجات حسب نوع التشغيل</b>مطاعم ومحلات متنوعة: سعر المحل + الزيادة على المنيو إن وُجدت. مارت وطلبات الكتابة: 5% داخل سعر المنتج، أو نسبة على الفاتورة.</div></li>
<li><div><b>رسوم الخدمة</b>على العميل من الإعدادات: مبلغ أو نسبة (الافتراضي 2.5%).</div></li>
<li><div><b>رسوم التوصيل</b>حسب المدينة والمحافظة + الكيلو الإضافي.</div></li>
<li><div><b>الإكرامية</b>اختيارية: نسب جاهزة أو مبلغ حر.</div></li>
<li><div><b>ما يُخصم من التاجر</b>رسوم لكل عميل أو النسبة (حسب العقد)، و5% للمارت والصيدليات، ورسم البوابة للمطاعم والمحلات المتنوعة. وتُحفظ نسخة الإعدادات على الطلب عند تأكيده.</div></li>
</ol></div>''')
note.insert_after(calc)
money_flow = html_to_tag('''<div><h3>مسار الأموال</h3>
<p>العميل يدفع إلكترونياً ← ميسر يحجز المبلغ ثم يحصّله عند اكتمال الطلب ← حساب المنصة يوزّع أسبوعياً حسب السجل المالي. المحفظة استردادات وتعويضات فقط، وتُستخدم في الدفع.</p>
<div class="tbl"><table><thead><tr><th>المستفيد</th><th>ما يصله</th></tr></thead><tbody>
<tr><td><b>التاجر</b></td><td>السلع − رسوم العميل أو النسبة − 5% مارت − رسم البوابة − حصته من العروض والتعويض</td></tr>
<tr><td><b>إيراد المنصة</b></td><td>رسوم الخدمة 2.5% · رسوم لكل عميل · النسبة · الزيادة · نسبة المناديب</td></tr>
<tr><td><b>المندوب الحر</b></td><td>التوصيل والإكرامية بعد الضريبة − نسبة المنصة</td></tr>
<tr><td><b>شركة التوصيل</b></td><td>مستحقات مناديبها، وهي تدفع لهم</td></tr>
<tr><td><b>هيئة الزكاة</b></td><td>ضريبة 15%</td></tr>
<tr><td><b>الغرامات المعلقة</b></td><td>تنتظر القرار: للعميل أو للمنصة أو تُعاد</td></tr>
</tbody></table></div></div>''')
sec.append(money_flow)
add('fees', 'الرسوم والأسعار', 'قواعد العمل', sec_html(sec))

# ---------------- 11. أمثلة العمليات المالية
add('money', 'أمثلة العمليات المالية', 'قواعد العمل', sec_html(get('money')))

# ---------------- 12. المناديب وشركات التوصيل
sec = get('drivers')
drop_starting(sec, 'يقبل المندوب حتى 3 طلبات في الوقت نفسه', 'li')          # مذكور في «الاستلام والتوصيل» و«التوزيع»
drop_starting(sec, 'الطلب بلا مندوب: تنبيه لغرفة العمليات', 'li')            # مذكور في «رحلة الطلب» و«الاستلام الذاتي»
drop_starting(sec, 'اعتذار المندوب بعد القبول يعيد الطلب للتوزيع', 'li')     # مذكور في «الاستلام والتوصيل»
add('drivers', 'المناديب وشركات التوصيل', 'قواعد العمل', sec_html(sec))

# ---------------- 13. أداء المناديب والحوافز
sec = get('performance')
drop_starting(sec, 'الصفحات في لوحة الإدارة', 'p,div')
add('performance', 'أداء المناديب والحوافز', 'قواعد العمل', sec_html(sec))

# ---------------- 14. الفواتير
add('invoices', 'الفواتير', 'قواعد العمل', sec_html(get('invoices')))

# ---------------- 15. العروض والحملات
sec = get('offers')
drop_starting(sec, 'برنامج الولاء ودعوة صديق والرصيد الترويجي', 'p,div')
drop_starting(sec, 'عرض التوصيل لا ينقص أجر المندوب', 'li')                    # القاعدة في «الرسوم والأسعار» و«المناديب»
add('offers', 'العروض والحملات', 'قواعد العمل', sec_html(sec))

# ---------------- 16. الولاء ودعوة صديق
add('loyalty', 'الولاء ودعوة صديق', 'قواعد العمل', sec_html(get('loyalty')))

# ---------------- 17. المدن
add('zones', 'المدن', 'قواعد العمل', sec_html(get('zones')))

# ---------------- 18. Taxi
add('taxi', 'Taxi', 'قواعد العمل', sec_html(get('taxi')))

# ---------------- 19. الصيدليات
sec = get('pharmacy')
add('pharmacy', 'الصيدليات', 'قواعد العمل', sec_html(sec))

# ---------------- 20. التواصل والإكرامية والشكاوى
add('comms', 'التواصل والإكرامية والشكاوى', 'قواعد العمل', sec_html(get('comms')))

# ---------------- 21. الإشعارات
add('notifications', 'الإشعارات', 'قواعد العمل', sec_html(get('notifications')))

# ---------------- 22. التحسينات
add('improvements', 'التحسينات', 'قواعد العمل', sec_html(get('improvements')))


# ------------------------------------------------------------------ الواجهات
def mock_of(fig):
    m = fig.find(class_=re.compile(r'^(ph|tb|wb)$'))
    return '<div class="mock" aria-hidden="true">%s</div>' % str(m) if m else ''


def render_screen(fig):
    cap = fig.find('figcaption')
    title = norm(cap.find('b').get_text()).replace(' (بطولها)', '')
    desc = ' '.join(norm(str(c)) for c in cap.children if isinstance(c, NavigableString)).strip()
    desc = desc.replace('الأرقام البرتقالية على الرسم تشرح كل جزء:', 'مكونات الشاشة (الأرقام البرتقالية على الرسم):').strip()
    leg = cap.find('ol', class_='mk-leg')
    frm = cap.find(class_='from')
    ids = cap.find(class_='ids')
    out = ['<figure class="shot">', mock_of(fig), '<figcaption class="cap">', '<h4>%s</h4>' % esc(title)]
    if desc:
        out.append('<p>%s</p>' % esc(desc))
    if frm:
        out.append('<p class="from">%s</p>' % esc(norm(frm.get_text())))
    if leg:
        out.append('<ol class="leg">%s</ol>' % ''.join('<li>%s</li>' % inner(li) for li in leg.find_all('li')))
    if ids:
        out.append('<p class="ids">%s</p>' % esc(norm(ids.get_text())))
    out.append('</figcaption></figure>')
    return ''.join(out)


def render_screens(sid, note=None):
    sec = S[sid]
    out = []
    for g in sec.select('.mk-group'):
        h3 = g.find('h3')
        sub = g.find('p', class_='sub')
        if h3:
            out.append('<h3>%s</h3>' % inner(h3))
        if sub:
            out.append('<p class="sub">%s</p>' % inner(sub))
        out.append('<div class="shots">%s</div>' % ''.join(render_screen(f) for f in g.select('figure.mk-shot')))
    return ''.join(out)


add('app-customer', 'تطبيق العميل', 'الواجهات', render_screens('app-customer'))
add('app-driver', 'تطبيق المندوب', 'الواجهات', render_screens('app-driver'))
add('app-merchant', 'تطبيق التاجر', 'الواجهات', render_screens('app-merchant'))


def render_pages(sec, group_order=None):
    """صفحات اللوحات: نأخذ المواصفات (ما في الصفحة، الخيارات، الشاشات) ونتجاهل نماذج الشاشات المرسومة."""
    groups = []
    for p in sec.select('section.ppanel'):
        crumb = norm(p.find(class_='crumb').get_text())
        title = norm(p.find('h3').get_text())
        sub = p.find('p', class_='sub')
        frames = []
        for fr in p.select('.pframe'):
            h4 = fr.find('h4')
            pp = fr.find('p')
            frames.append((norm(h4.get_text()), norm(pp.get_text()) if pp else ''))
        spec = p.select_one('.pspec')
        opts = p.select_one('.opts .tbl')
        body = []
        short = sub is not None and len(norm(sub.get_text())) <= 110
        if sub and not short:
            body.append('<p class="sub">%s</p>' % inner(sub))
        if frames:
            fr_html = []
            for fr in p.select('.pframe'):
                h4 = fr.find('h4'); pp = fr.find('p')
                t = re.sub(r'^\d+\s*·\s*', '', norm(h4.get_text()))
                d = norm(pp.get_text()) if pp else ''
                d = d.replace('القائمة الكاملة في القسم التالي', 'القائمة الكاملة في قسم «تقارير التاجر» أدناه')
                fig = fr.find('figure')
                fr_html.append('<div class="frame"><h5>%s%s</h5><div class="shots"><figure class="shot">%s</figure></div></div>' % (
                    esc(t), (' <span>— %s</span>' % esc(d)) if d and not norm(d).startswith(t.rstrip('.،')) else '', mock_of(fig) if fig else ''))
            body.append('<h5 class="grp-h">الشاشات</h5>' + ''.join(fr_html))
        if spec:
            body.append('<h5>ما في الصفحة</h5>' + str(spec))
        if opts:
            body.append('<h5>خيارات الصفحة وإعداداتها</h5>' + str(opts))
        html_ = '<details class="page" id="%s"><summary><span class="pn">%s</span>%s</summary><div class="pbody">%s</div></details>' % (
            p['id'], esc(title), ('<span class="ps">%s</span>' % esc(norm(sub.get_text()))) if short else '', ''.join(body))
        for g in groups:
            if g[0] == crumb:
                g[1].append(html_)
                break
        else:
            groups.append((crumb, [html_]))
    return ''.join('<h3>%s</h3><div class="pages">%s</div>' % (esc(c), ''.join(items)) for c, items in groups)


_d = review_more.shared_section()
add(_d['id'], _d['title'], _d['part'], _d['html'])

# لوحة التاجر + تقاريرها
sec = S['merchant-dash']
mer_html = str(sec.find('p', class_='sub')) + render_pages(sec)
rep = get('merchant-reports')
mer_html += '<h3>تقارير التاجر</h3>' + inner(rep)
add('merchant-dash', 'لوحة التاجر', 'الواجهات', mer_html)

# لوحة الإدارة + قواعدها + تقاريرها
sec = S['admin-pages']
adm_html = str(sec.find('p', class_='sub')) + render_pages(sec)
rep = get('admin-reports')
adm_html += '<h3>تقارير الإدارة</h3>' + inner(rep)
add('admin-pages', 'لوحة الإدارة', 'الواجهات', adm_html)

# ------------------------------------------------------------------ للتنفيذ
add('build', 'البناء وقابلية التطوير', 'للتنفيذ', sec_html(get('build')))
add('launch', 'الإطلاق والتشغيل', 'للتنفيذ', sec_html(get('launch')))
add('services', 'الربط مع الخدمات الأخرى', 'للتنفيذ', sec_html(get('services')))
_d = review_more.settings_section(S)
add(_d['id'], _d['title'], _d['part'], _d['html'])


# ---- فهرس المتطلبات
def req_html(r):
    tags = ''.join('<span class="tag %s">%s</span>' % ({'أساسي للإطلاق': 'p1', 'مهم': 'p2', 'لاحقاً': 'p3', 'نظامي': 'reg'}.get(t, ''), esc(t)) for t in r['tags'])
    return ('<details class="req" id="{id}" data-p="{p}" data-reg="{reg}"><summary><bdi class="rid">{id}</bdi> '
            '<span class="rt">{title}</span> {tags}</summary><div class="rbody"><div><h5>القواعد</h5><ul>{rules}</ul></div>'
            '<div><h5>معيار القبول</h5><ul>{accept}</ul></div></div></details>').format(
        id=r['id'], p=prio(r['tags']), reg='1' if 'نظامي' in r['tags'] else '0', title=esc(r['title']), tags=tags,
        rules=r['rules'], accept=r['accept'])


cat_html = ['<p class="sub">%d متطلباً. لكل متطلب معرّف ثابت، وقواعد، ومعيار قبول يُختبر عليه. «أساسي للإطلاق» يُبنى قبل التشغيل، و«مهم» بعده مباشرة، ثم «لاحقاً». المتطلبات الموسومة «نظامي» يلزم بها النظام السعودي.</p>' % N_REQ]
cat_html.append('''<div class="cat-tools" id="cat-tools">
<input type="search" id="cat-q" placeholder="ابحث في المتطلبات: المعرّف أو النص" aria-label="بحث في المتطلبات" autocomplete="off">
<select id="cat-mod" aria-label="الوحدة"><option value="">كل الوحدات</option>%s</select>
<div class="chips-f" id="cat-pri" role="group" aria-label="الأولوية">
<button type="button" data-v="" aria-pressed="true">الكل</button>
<button type="button" data-v="p1" aria-pressed="false">أساسي للإطلاق</button>
<button type="button" data-v="p2" aria-pressed="false">مهم</button>
<button type="button" data-v="p3" aria-pressed="false">لاحقاً</button>
<button type="button" data-v="reg" aria-pressed="false">نظامي</button>
</div>
<span class="cat-count" id="cat-count" aria-live="polite"></span>
<button type="button" id="cat-open">فتح الكل</button><button type="button" id="cat-close">إغلاق الكل</button>
</div>''' % ''.join('<option value="%s">%s · %s</option>' % (m['code'], esc(m['name']), m['code']) for m in MODS))
for m in MODS:
    cat_html.append('<div class="mod" data-mod="%s"><h3>%s <bdi class="rid">%s</bdi><small>%d</small></h3>%s</div>' % (
        m['code'], esc(m['name']), m['code'], len(m['reqs']), ''.join(req_html(r) for r in m['reqs'])))
cat_html.append('<p class="empty" id="cat-empty" hidden>لا توجد نتائج. جرّب كلمة أخرى.</p>')
add('catalog', 'فهرس المتطلبات', 'للتنفيذ', ''.join(cat_html))

add('delivery', 'التسليم والقبول', 'للتنفيذ', sec_html(get('delivery')))
_d = review_more.changelog_section(N_REQ)
add(_d['id'], _d['title'], _d['part'], _d['html'])

# ------------------------------------------------------------------ تجميع الصفحة
PARTS = []
for s in SECTIONS:
    if not PARTS or PARTS[-1][0] != s['part']:
        PARTS.append((s['part'], []))
    PARTS[-1][1].append(s)

n = 0
nav = []
body = []
for pname, secs in PARTS:
    nav.append('<div class="nav-part">%s</div>' % esc(pname))
    body.append('<div class="part-h" id="part-%d"><span>%s</span></div>' % (len(nav), esc(pname)))
    for s in secs:
        n += 1
        s['n'] = n
        nav.append('<a href="#%s" data-sec="%s"><i>%d</i>%s</a>' % (s['id'], s['id'], n, esc(s['title'])))
        frag = BeautifulSoup('<div>' + s['html'] + '</div>', 'lxml').find('div')
        lang.process(frag, s['id'])
        if s['id'] != 'catalog':
            linkify(frag)
        # جداول: لفّها للتمرير الأفقي (موجودة أصلاً داخل .tbl) وتأكد من عدم وجود جداول عارية
        for t in frag.find_all('table'):
            if not t.find_parent(class_='tbl') and not t.find_parent(class_='mock'):
                w = soup.new_tag('div'); w['class'] = 'tbl'
                t.wrap(w)
        # نزيل السمات المتبقية من العرض القديم
        for e in frag.find_all(attrs={'role': True}):
            del e['role']
        body.append('<section id="{id}"><h2><span class="num">{n}</span>{title}</h2>{html}</section>'.format(
            id=s['id'], n=n, title=esc(s['title']), html=inner(frag)))

# تقدير عدد الشاشات والصفحات لعرضه في الغلاف
n_screens = sum(len(S[k].select('figure.mk-shot')) for k in ('app-customer', 'app-driver', 'app-merchant'))
n_pages = len(S['merchant-dash'].select('section.ppanel')) + len(S['admin-pages'].select('section.ppanel'))

page = open(os.path.join(HERE, 'template.html'), encoding='utf8').read()
page = (page.replace('{{NAV}}', '\n'.join(nav)).replace('{{BODY}}', '\n'.join(body))
        .replace('{{N_REQ}}', str(N_REQ)).replace('{{VERSION}}', review.VERSION).replace('{{DATE}}', review.DATE).replace('{{N_SECTIONS}}', str(n))
        .replace('{{N_SCREENS}}', str(n_screens)).replace('{{N_PAGES}}', str(n_pages)))
os.makedirs(os.path.join(OUT, 'assets'), exist_ok=True)
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf8').write(page)
lang.dump()
print('تحريرات صياغة مطبّقة:', lang.APPLIED['n'])
print('sections', n, 'requirements', N_REQ, 'screens', n_screens, 'dashboard pages', n_pages, 'bytes', len(page.encode('utf8')))
