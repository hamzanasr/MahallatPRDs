# -*- coding: utf-8 -*-
"""إخراج مواصفات مختصرة للمبرمج مع إبقاء قواعد المتطلبات دون تعديل."""
from copy import deepcopy
from pathlib import Path
import re
from bs4 import BeautifulSoup, NavigableString

MARKER = 'data-document="developer-brief-v1"'


def apply(page):
    if MARKER in page:
        return page
    soup = BeautifulSoup(page, 'html.parser')
    attributions = [', على نمط Uber Reserve وCareem', '، على نمط Uber Reserve وCareem', '، على نمط Uber،']
    def without_attributions(value):
        for attribution in attributions:
            value = value.replace(attribution, '،' if attribution.endswith('،') else '')
        return value
    original_requirements = [without_attributions(str(e)) for e in soup.select('#catalog details.req[id]')]
    original_pages = [e['id'] for e in soup.select('details.page[id]')]
    original_frames = len(soup.select('.frame'))

    def section(id):
        node = soup.find('section', id=id)
        assert node is not None, id
        return node

    def fragment(html):
        return BeautifulSoup(html, 'html.parser').find(True)

    def heading_block(node, title):
        heading = next(h for h in node.find_all('h3', recursive=False) if h.get_text(strip=True) == title)
        following = []
        for sibling in heading.next_siblings:
            if getattr(sibling, 'name', None) in {'h2', 'h3'}:
                break
            following.append(sibling)
        heading.decompose()
        for sibling in following:
            if hasattr(sibling, 'decompose'):
                sibling.decompose()
            else:
                sibling.extract()

    # مقدمة تنفيذية واحدة بدلاً من المقدمة ومصفوفة المصادر والملخص الثاني.
    start = section('start')
    heading = start.find('h2').extract()
    start.clear(); start.append(heading)
    intro = fragment('''<div><p class="sub">مواصفات التنفيذ: نطاق الإطلاق، دورة الطلب، الواجهات، والقواعد ومعايير القبول. لكل متطلب معرّف ثابت يُستخدم في مهام التطوير والاختبار.</p>
<p>منصة توصيل سعودية للمطاعم والمحلات والمارت والصيدليات والاستلام الذاتي وTaxi، تبدأ مدينة بعد مدينة. الدفع إلكتروني عبر ميسر.</p>
<h3>الواجهات والمسؤوليات</h3><div class="tbl"><table><thead><tr><th>الواجهة</th><th>المسؤولية</th></tr></thead><tbody>
<tr><td>تطبيق العميل</td><td>الطلب والدفع والتتبع والتواصل والتقييم والدعم والمحفظة.</td></tr>
<tr><td>تطبيق التاجر</td><td>تشغيل الفرع والمناوبات والطلبات والتحضير والفواتير والكشف. بقالة المارت تقبل أو تعتذر؛ كتالوج المارت تديره الإدارة.</td></tr>
<tr><td>تطبيق المندوب</td><td>التوفر وقبول المهام وأكواد الاستلام والتسليم والأرباح. وضع Taxi للموافق عليهم فقط.</td></tr>
<tr><td>لوحة الإدارة</td><td>التشغيل والإسناد والدعم والمالية والمتاجر والمدن والتسويق والإعدادات والصلاحيات.</td></tr>
<tr><td>بوابة شركة التوصيل</td><td>مناديب الشركة ومركباتها ومدنها المسموحة والأداء والمستحقات والتحويلات.</td></tr>
</tbody></table></div>
<h3>قراءة الملف وتنفيذه</h3><ol class="rules">
<li>ابدأ بـ<a href="#scope">نطاق الإصدار الأول</a> و<a href="#decisions">القرارات المفتوحة</a>، ثم <a href="#journey">رحلة الطلب</a> والواجهات.</li>
<li>نفّذ كل بند من <a href="#catalog">فهرس المتطلبات</a> واختبر معيار قبوله. وسومه تحدد ما يُبنى الآن وما يؤجّل.</li>
<li>الأرقام المرنة تُحفظ في <a href="#settings">إعدادات الإدارة</a>. أرقام الرسومات والأمثلة للتوضيح؛ الرسومات تحدد المحتوى، والتصميم البصري والهوية خارج مسؤولية المبرمج.</li>
<li>الهيكل التقني وترتيب العمل في <a href="#build">البناء</a>، والربط في <a href="#services">الخدمات</a>، والنقل من التطبيق الحالي في <a href="#launch">الإطلاق</a>.</li>
</ol></div>''')
    for child in list(intro.contents):
        start.append(child.extract())

    # الربط في جدول واحد: تفاصيل مزود الخدمة والغرض والدفعة والمفاتيح والفشل.
    scope = section('scope')
    services = section('services')
    integration_table = next(t for t in scope.find_all('table') if 'ما يلزم توفيره من المالك أو المزود' in t.get_text())
    old_service_table = services.find('table')
    purposes = {r.find_all('td')[0].get_text(' ',strip=True): r.find_all('td')[1] for r in old_service_table.select('tbody tr')}
    mapping = {
        'ميسر (الدفع)': ['ميسر'], 'خرائط جوجل': ['الخرائط'],
        'الرسائل ورمز الدخول': ['مزود الرسائل والاتصال المقنع'], 'OneSignal': ['OneSignal'],
        'الفوترة الإلكترونية (هيئة الزكاة)': ['الفوترة الإلكترونية (هيئة الزكاة)'],
        'Odoo (المحاسبة)': ['Odoo'], 'Adjust وMixpanel': ['Adjust','Mixpanel'],
        'المساعدات الذكية (MCP)': ['المساعدات الذكية عبر خادم MCP (مثل Claude وChatGPT وGemini)'],
        'أنظمة الكاشير': ['أنظمة الكاشير'], 'الكول سنتر': ['الكول سنتر'],
        'التحقق من الوجه': ['التحقق من الوجه'], 'قراءة الفواتير آلياً': ['قراءة الفواتير آلياً'],
        'نوبكو': ['نوبكو (مستقبلاً)'],
    }
    assert set(purposes) == {key for values in mapping.values() for key in values}
    th = soup.new_tag('th'); th.string = 'الغرض'; integration_table.find('tr').find('th').insert_after(th)
    for row in integration_table.select('tbody tr'):
        name = row.find('td').get_text(' ',strip=True)
        td = soup.new_tag('td')
        for i,key in enumerate(mapping[name]):
            if i: td.append(NavigableString(' · '))
            for content in purposes[key].contents:
                td.append(deepcopy(content))
        row.find('td').insert_after(td)
    table_wrapper = integration_table.find_parent(class_='tbl').extract()
    service_h2 = services.find('h2').extract(); services.clear(); services.append(service_h2)
    services.append(fragment('<p class="sub">كل خدمة خلف واجهة ومحوّل مستقل (SYS-009)، وتُجرَّب بمحوّل وهمي قبل استخدام المفاتيح الحقيقية. يحدد الجدول الغرض وما يلزم للربط وسلوك التعطل.</p>'))
    services.append(table_wrapper)
    heading_block(scope, 'الربط المطلوب في الدفعة الأولى')
    # قوائم الأولويات تعرض مرة واحدة في الفهرس بفلاتره.
    heading_block(scope, 'عدد المتطلبات حسب الوحدة والأولوية')
    # heading_block أزال قوائم details التابعة للعنوان نفسه أيضاً.
    assert not scope.find('details')
    scope.select_one('.sub').string = 'نطاق الإطلاق والتهيئة والتأجيل. القائمة التفصيلية لكل أولوية في فهرس المتطلبات، والربط في قسم الخدمات.'
    table = scope.find('table')
    for row in table.find_all('tr'):
        row.find_all(['th','td'],recursive=False)[-1].decompose()
    for item in table.find_all(string=True):
        value = str(item).replace('القائمتان أدناه.', 'استخدم فلتر الأولوية في فهرس المتطلبات.')
        if value != str(item): item.replace_with(NavigableString(value))
    heading_block(section('decisions'), 'قرارات حُسمت')
    for item in list(section('decisions').find_all(string=True)):
        value = str(item).replace('اللائحة تشترط تسعيرة معتمدة مسبقاً من الهيئة، بينما Uber وCareem يستخدمان تسعيراً ديناميكياً وقت الذروة.', 'اللائحة تشترط تسعيرة معتمدة مسبقاً من الهيئة؛ يلزم حسم إمكان استخدام تسعير ديناميكي وقت الذروة.')
        if value != str(item): item.replace_with(NavigableString(value))

    # حذف المصادر والمقارنة مع المنافسين، والإبقاء على سياسة Taxi التنفيذية.
    taxi = section('taxi')
    heading_block(taxi, 'ما اعتُمد من Uber وCareem')
    heading_block(taxi, 'المصادر')
    taxi.select_one('.note').clear()
    taxi.select_one('.note').append(NavigableString('Taxi ضمن الإطلاق. القيم الافتراضية مرنة من الإعدادات، وأرقام الأسعار في الرسومات أمثلة.'))
    classes_table = taxi.find('table')
    for row in classes_table.find_all('tr'):
        row.find_all(['th','td'],recursive=False)[-1].decompose()
    for p in taxi.find_all('p'):
        if 'ملخص اللائحة التنفيذية' in p.get_text():
            p.clear()
            p.append(fragment('<span>يراجع المستشار النظامي الترخيص والربط بمنصة الهيئة والمواصفات قبل تفعيل Taxi (<a class="rid" href="#REG-009">REG-009</a>، D-17).</span>'))
    for item in list(section('journey').find_all(string=True)):
        value = str(item).replace('الأرقام قيم افتراضية مستوحاة من سياسات Uber وCareem، ومعتمدة بتوجيه من المالك', 'الأرقام قيم افتراضية معتمدة ومرنة من الإعدادات')
        if value != str(item): item.replace_with(NavigableString(value))
    for item in list(section('catalog').find_all(string=True)):
        value = without_attributions(str(item))
        if value != str(item): item.replace_with(NavigableString(value))

    # هذه أقسام ثانية تعرض المحتوى نفسه أو تاريخه؛ الفهرس يحفظ جميع تفاصيله.
    for id in ['changelog','overview','improvements']:
        section(id).decompose()
        for a in soup.select('a[data-sec="'+id+'"]'): a.decompose()
    # مثال القائمة الجانبية مرة واحدة لكل لوحة، والباقي يركز على محتوى الصفحة.
    sidebar_count = 0
    for id in ['merchant-dash','admin-pages']:
        boards = section(id).select('.mock .wb')
        for board in boards[1:]:
            side = board.select_one('.wmain > .side')
            if side:
                side.decompose(); sidebar_count += 1
                board['class'] = list(board.get('class',[])) + ['compact']
    # حذف وصف المؤشرات والقوائم إذا كانت تسمياتها ظاهرة في رسم الصفحة نفسه.
    def norm(value):
        return re.sub(r'[\W_]+', ' ', value, flags=re.U).strip()
    redundant_items = 0
    for page_node in soup.select('details.page'):
        visual_text = norm(' '.join(e.get_text(' ',strip=True) for e in page_node.select('.mock')))
        seen = set()
        for li in list(page_node.select('.pspec li')):
            value = norm(li.get_text(' ',strip=True))
            if len(value)>=10 and (value in visual_text or value in seen):
                li.decompose(); redundant_items += 1
            else:
                seen.add(value)
        for card in list(page_node.select('.pspec .sc2')):
            if not card.find('li'): card.decompose()
        for spec in list(page_node.select('.pspec')):
            if not spec.select('.sc2'):
                preceding = spec.find_previous_sibling('h5')
                if preceding and preceding.get_text(strip=True)=='ما في الصفحة': preceding.decompose()
                spec.decompose()
    # أسماء الأقسام وأرقامها والروابط تتبع بنية الملف المختصر.
    for i,sec in enumerate(soup.select('main > section'),1):
        sec.find('h2').select_one('.num').string = str(i)
        link = soup.select_one('.sidebar a[data-sec="'+sec['id']+'"]')
        assert link is not None, sec['id']
        link.find('i').string = str(i)
    footer = soup.find('footer')
    if footer: footer.decompose()
    for p in soup.find_all(['p','li']):
        if not p.find_parent(class_='mock') and not p.find_parent(id='catalog'):
            for item in list(p.find_all(string=True)):
                value = str(item).replace('«التحسينات»','«فهرس المتطلبات»').replace('جدول التحسينات','فهرس المتطلبات')
                if value != str(item): item.replace_with(NavigableString(value))
    assert original_requirements == [without_attributions(str(e)) for e in soup.select('#catalog details.req[id]')]
    assert original_pages == [e['id'] for e in soup.select('details.page[id]')]
    assert original_frames == len(soup.select('.frame'))
    assert not soup.select('main a[href^="http"]')
    soup.html['data-document'] = 'developer-brief-v1'
    print('Cleaned document: repeated sidebars',sidebar_count,'repeated page labels',redundant_items)
    return str(soup)


if __name__ == '__main__':
    target = Path(__file__).resolve().parents[1] / 'index.html'
    target.write_text(apply(target.read_text(encoding='utf-8')), encoding='utf-8')
