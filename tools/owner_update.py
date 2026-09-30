# -*- coding: utf-8 -*-
"""قرارات المالك بعد مراجعة 30 سبتمبر؛ تحفظها إعادة البناء أيضاً.

يعالج الأقسام المعدلة فقط، ويتحقق من وجود النص القديم قبل تغييره.
"""
from pathlib import Path
import re
from collections import Counter
from bs4 import BeautifulSoup, NavigableString

MARKER = 'id="owner-decisions-20260930"'


def apply(page):
    if MARKER in page or 'data-document="developer-brief-v1"' in page:
        return page
    soup = BeautifulSoup(page, 'html.parser')
    changed = set()

    def section(id):
        changed.add(id)
        node = soup.find('section', id=id)
        assert node is not None, id
        return node

    def text(node, old, new, minimum=1):
        count = 0
        for item in list(node.find_all(string=True)):
            if old in item:
                count += str(item).count(old)
                item.replace_with(NavigableString(str(item).replace(old, new)))
        if count < minimum:
            # بعض الجمل موزعة على نص وعناصر إبراز؛ يُغيّر أصغر عنصر كامل فقط.
            for item in reversed(node.find_all(['li', 'p', 'td', 'div'])):
                value = item.get_text(' ', strip=True)
                if old in value:
                    count += value.count(old)
                    item.clear()
                    item.append(NavigableString(value.replace(old, new)))
        assert count >= minimum, (old, count)

    def fragment(html):
        return BeautifulSoup(html, 'html.parser').find(True)

    def add_rule(req, value, acceptance=False):
        body = req.select_one('.rbody')
        target = body.find_all('div', recursive=False)[1 if acceptance else 0].find('ul')
        li = soup.new_tag('li')
        li.string = value
        target.append(li)

    cat = section('catalog')
    req = lambda id: cat.find('details', id=id)

    # المارت علامة وكتالوج موحد؛ قبول البقالة يسبق عرض الطلب على المناديب.
    ord3 = req('ORD-003')
    text(ord3, 'بعد أن يقبل المندوب الطلب يصل الطلب إلى التاجر بحالة «جاري التجهيز».',
         'في المطاعم والمحلات المتنوعة وطلبات الكتابة، يصل الطلب إلى التاجر بحالة «جاري التجهيز» بعد قبول المندوب. أما المارت فيصل إلى البقالات بالتتابع أولاً، وبعد قبول بقالة يبدأ التجهيز ويُعرض الطلب على المناديب (DSP-005).')
    ord6 = req('ORD-006')
    text(ord6, 'المندوب قبل التاجر', 'ترتيب قبول المندوب والتاجر حسب الخدمة')
    text(ord6, 'في طلبات التوصيل بالمنيو لا يصل الطلب إلى التاجر إلا بعد أن يقبله مندوب واحد.',
         'في طلبات المطاعم والمحلات المتنوعة بالمنيو لا يصل الطلب إلى التاجر إلا بعد أن يقبله مندوب واحد. المارت مستثنى: تقبل البقالة أولاً ثم يبدأ إسناد الطلب إلى مندوب (DSP-005).')
    add_rule(ord6, 'في المارت لا يُعرض الطلب على أي مندوب ما دام قبول البقالة معلقاً؛ الاعتذار أو انتهاء مهلة البقالة ينقله إلى التالية.', True)
    dsp = req('DSP-005')
    text(dsp, 'البقالة تجهز الطلب فيُعتمد', 'البقالة تقبل الطلب كاملاً فيُعتمد وتبدأ تجهيزه')
    add_rule(dsp, 'يظهر المارت للعميل باسم وهوية وكتالوج موحد، وتُنشأ السلة والطلب للمارت نفسه. لا تظهر البقالات كبطاقات متاجر ولا يختار العميل بقالة بعينها.')
    add_rule(dsp, 'يبقى قبول بقالة واحدة فقط صالحاً للطلب؛ لا يسند النظام الطلب لبقالتين عند تزامن القبول مع انتهاء المهلة.', True)
    add_rule(dsp, 'لا توجد بطاقات بقالات في قسم المارت أو نتائج بحثه، ويظهر اسم المارت في تفاصيل الطلب والإشعارات والفاتورة والتقييم.', True)
    stores = section('stores')
    text(stores, 'طلب واحد لكل الكتالوج', 'مارت واحد وطلب واحد لكل الكتالوج')
    text(stores, 'لا يرى العميل اسم أي بقالة في أي شاشة أو إشعار أو فاتورة، ولا يقيّم البقالة باسمها.',
         'يرى العميل مارتاً واحداً بكتالوج موحد، ويصل الطلب للمارت نفسه. لا تظهر البقالات كبطاقات متاجر ولا يختار العميل بقالة. لا يرى اسم أي بقالة في أي شاشة أو إشعار أو فاتورة أو تقييم.')
    for id in ['app-customer', 'app-driver']:
        node = section(id)
        text(node, 'مارت الحي', 'المارت', minimum=0)
    section('app-customer').find('h2').insert_after(fragment('<p class="sub">قسم المارت يفتح كتالوجاً موحداً باسم المارت؛ لا يعرض بطاقات البقالات. السلة وتفاصيل الطلب والتقييم تخص المارت، والتوزيع الداخلي على البقالات لا يظهر للعميل.</p>'))

    journey = section('journey')
    text(journey, 'للمنصة ثلاثة أنواع من الطلبات، ولكل نوع دورة كاملة',
         'تعرض الوثيقة مسارات المنيو والمارت والكتابة وTaxi، ولكل مسار دورة كاملة')
    rest = journey.find(id='jr-rest')
    text(rest, 'المسار الأساسي: لا يصل الطلب إلى التاجر قبل أن يقبله مندوب.',
         'في المطاعم والمحلات المتنوعة: لا يصل الطلب إلى التاجر قبل أن يقبله مندوب. للمارت مسار مستقل أدناه؛ تقبل البقالة أولاً.')
    mart = fragment('''<div class="jtype" id="jr-mart"><h3>طلب المارت (كتالوج موحد)</h3>
<p>يختار العميل من المارت نفسه؛ لا تظهر له البقالات. قبول البقالة يسبق إسناد المندوب، وفق <a class="rid" href="#DSP-005">DSP-005</a>.</p>
<h4>الحالات بالترتيب</h4><div class="tbl"><table><thead><tr><th>الحالة</th><th>ما يراه العميل</th><th>ما يحدث</th><th>من ينقلها</th><th>المهلة والقاعدة</th></tr></thead><tbody>
<tr><td>السلة والدفع</td><td>المارت · السلة</td><td>سلة واحدة من الكتالوج الموحد بأسعار المارت، ثم الدفع وفق القواعد الحالية.</td><td>العميل والنظام</td><td>فشل الدفع لا ينشئ طلباً.</td></tr>
<tr><td>مهلة التراجع</td><td>تم الطلب · يمكنك الإلغاء</td><td>لا يُعرض الطلب على بقالة أو مندوب خلال المهلة.</td><td>النظام</td><td>60 ثانية؛ بعدها لا يلغي العميل.</td></tr>
<tr><td>بانتظار قبول بقالة</td><td>جاري التجهيز</td><td>عرض على بقالة واحدة في كل مرة. عند الاعتذار أو انتهاء المهلة ينتقل إلى التالية، حتى تقبل بقالة.</td><td>نظام التوزيع والبقالة</td><td>60 ثانية لكل بقالة افتراضياً، مرنة. لا عرض على المناديب في هذه الحالة.</td></tr>
<tr><td>قبول البقالة وبدء التجهيز</td><td>جاري التجهيز</td><td>تُثبت البقالة المقبولة داخلياً ويبدأ تجهيز الطلب، ثم يُعرض على المناديب.</td><td>البقالة ثم نظام التوزيع</td><td>مدة التحضير مرنة حتى 40 دقيقة؛ تعديل واحد خلال 3 دقائق.</td></tr>
<tr><td>بانتظار مندوب</td><td>جاري التجهيز</td><td>توزيع متتابع على المناديب بعد قبول البقالة فقط. يستمر التجهيز.</td><td>نظام التوزيع</td><td>تنبيه 3 دقائق وإنذار 5 دقائق؛ بعد 15 دقيقة بلا مندوب يُلغى ويُرد المبلغ كاملاً. لا استلام ذاتي في المارت.</td></tr>
<tr><td>جاهز والاستلام</td><td>جاري التجهيز ثم جاري التوصيل</td><td>البقالة ترفق الفاتورة وتضغط «جاهز». الاستلام بكود المندوب والصورة داخل نطاق 100 متر.</td><td>البقالة والمندوب</td><td>لا ينتقل إلى جاهز تلقائياً. يصبح «جاري التوصيل» عند الاستلام.</td></tr>
<tr><td>التسليم والإكمال</td><td>تم التسليم · قيّم المارت</td><td>كود العميل وصورة التسليم والتسوية وفق قواعد طلب المنيو؛ يبقى اسم البقالة مخفياً.</td><td>المندوب والنظام</td><td>قواعد عدم التجاوب والشكوى نفسها، والتقييم والمشكلات للإدارة.</td></tr>
</tbody></table></div><h4>ما يخرج عن المسار</h4><ul class="rules">
<li>إذا لم تقبل أي بقالة الطلب، يُلغى ويُرد المبلغ كاملاً.</li>
<li>النقص بعد قبول البقالة يُعالج بالحذف أو البديل بموافقة العميل وفق <a class="rid" href="#MER-032">MER-032</a>؛ لا يعاد عرضه على بقالة أخرى تلقائياً بعد اعتماد القبول.</li>
<li>اعتذار المندوب بعد قبوله يعيد توزيع المندوب بأعلى أولوية مع بقاء البقالة المقبولة وفق قواعد الاعتذار الحالية.</li>
</ul></div>''')
    rest.insert_after(mart)

    # حد التحضير 40 دقيقة؛ تبقى قواعد المرونة والتعديل والمدد الأصلية.
    prep = section('merchant-time')
    text(prep, 'بعد أن يقبل المندوب الطلب يصل الطلب إلى التاجر، و تكون حالته «جاري التجهيز» مباشرة.',
         'في المطاعم والمحلات المتنوعة وطلبات الكتابة يصل الطلب للتاجر بعد قبول المندوب، بحالة «جاري التجهيز». المارت مستثنى: يبدأ تجهيز البقالة عند قبولها، ثم يبدأ إسناد المندوب (DSP-005).')
    text(prep, 'المدير يحدد لكل متجر إن كان مسموحاً له بتجاوز 40 دقيقة أم لا.',
         'تظل مدة التحضير مرنة من الإعدادات، وحدها الأقصى 40 دقيقة لكل متجر؛ لا توجد صلاحية لتجاوز هذا الحد.')
    text(prep, 'ويستمر ساعة كحد أقصى.', 'ويستمر ساعة كحد أقصى، ولا يرفع مدة التحضير النهائية فوق 40 دقيقة.')
    text(stores, 'مدة التحضير الافتراضية، وهل يملك المتجر صلاحية تجاوز 40 دقيقة',
         'مدة التحضير الافتراضية المرنة، بحد أقصى 40 دقيقة')
    text(ord3, 'لا تتجاوز المدة 40 دقيقة إلا بصلاحية من المدير.', 'مدة التحضير مرنة ولا تتجاوز 40 دقيقة.')
    add_rule(ord3, 'لا يقبل النظام مدة تحضير أعلى من 40 دقيقة، سواء من المدة الافتراضية أو تعديل التاجر أو وضع الانشغال.', True)
    settings = section('settings')
    text(settings, '40 دقيقة · صلاحية تجاوزه وحدها الأعلى لكل متجر', 'مرن لكل متجر حتى 40 دقيقة')
    text(settings, '40 دقيقة. يمكن تجاوزها لمتجر بعينه بصلاحية من المدير.', '40 دقيقة كحد أقصى؛ لا يتجاوزها أي متجر أو دور إداري.')
    admin = section('admin-pages')
    text(admin, 'صلاحية تجاوز 40 دقيقة', 'حد التحضير المرن حتى 40 دقيقة')
    text(admin, 'الحد الأعلى: —', 'الحد الأقصى: 40 دقيقة')
    text(admin, 'صلاحية تجاوز 40 د · بيت الكبسة', 'مدة التحضير الافتراضية · بيت الكبسة')
    text(admin, 'بلا صلاحية', '20 د')
    text(admin, 'حتى 50 د', '30 د')
    prep_field = next(x for x in admin.select('.fl') if x.find('label') and x.find('label').get_text(strip=True) == 'حد التحضير المرن حتى 40 دقيقة')
    prep_field.find('label').string = 'الحد الأقصى للتحضير'
    prep_field.select_one('.in').clear()
    prep_field.select_one('.in').append(NavigableString('40 دقيقة · لا يُتجاوز'))

    # موظف الدعم يراجع ويرفع؛ المشرف صاحب الإنهاء والتنفيذ المالي.
    replacements = [
        ('الدعم وحده ينهي الطلب بعد مراجعته', 'يراجع الدعم الحالة ويرفعها إلى مشرف العمليات، والمشرف وحده ينهي الطلب بعد المراجعة'),
        ('ينهي الدعم الطلب', 'ينهي مشرف العمليات الطلب بعد مراجعة الدعم'),
        ('يقرر الدعم: إعادة المحاولة، أو كود العمليات، أو إنهاء الطلب مع استرداد', 'يرفع الدعم توصيته إلى مشرف العمليات: إعادة المحاولة، أو كود العمليات، أو إنهاء الطلب مع استرداد ضمن صلاحية المشرف'),
        ('حتى يصدر قرار الدعم أو يسمح له الدعم بالمغادرة', 'حتى يصدر قرار مشرف العمليات أو يسمح له بالمغادرة بعد مراجعة الدعم'),
        ('الدعم ينهي الطلب بعد مراجعته', 'الدعم يراجع الحالة، ومشرف العمليات ينهي الطلب بعد المراجعة'),
        ('الدعم ينهي الطلب', 'مشرف العمليات ينهي الطلب بعد مراجعة الدعم'),
        ('الدعم ينهي بعد المراجعة', 'الدعم يراجع؛ المشرف ينهي'),
        ('الدعم ينهي', 'المشرف ينهي بعد مراجعة الدعم'),
        ('يصدر الدعم قراراً نهائياً بعد مراجعة الشروط الثلاثة.', 'يصدر مشرف العمليات قراراً نهائياً بعد مراجعة الدعم للشروط الثلاثة.'),
        ('يراجع الدعم الطلب وينهيه بلا استرداد', 'يراجع الدعم الطلب، وينهيه مشرف العمليات بلا استرداد'),
        ('الإنهاء قرار بشري يتخذه موظف الدعم بعد المراجعة.', 'الإنهاء قرار بشري يتخذه مشرف العمليات بعد مراجعة الدعم؛ الدعم لا ينهي الطلب ولا ينفذ استرداداً أو تعويضاً.'),
        ('وإذا نقص شرط، يقرر الموظف:', 'وإذا نقص شرط، يقرر المشرف:'),
        ('ينهي الدعم الطلب بعد المراجعة', 'ينهي مشرف العمليات الطلب بعد مراجعة الدعم'),
    ]
    for id in ['journey', 'arrival', 'cancel', 'notifications', 'app-driver', 'settings', 'catalog', 'admin-pages']:
        node = section(id)
        for old, new in replacements:
            text(node, old, new, minimum=0)
    text(settings, 'بعد مراجعة الدعم بعد المراجعة', 'بعد مراجعة الدعم', minimum=0)
    # هذه مهلة وصول التنبيه، وليست إنهاء تلقائياً.
    for row in admin.find_all('tr'):
        cells = row.find_all('td', recursive=False)
        if cells and cells[0].get_text(strip=True) == 'إنهاء عدم التجاوب':
            if len(cells) in (2,3) and cells[1].get_text(strip=True) == '30 د':
                cells[0].string = 'تنبيه الدعم لعدم التجاوب'
    ord8 = req('ORD-008')
    text(ord8, 'إلا بقرار من موظف.', 'إلا بقرار من مشرف العمليات بعد مراجعة الدعم.')
    add_rule(ord8, 'لا يظهر زر إنهاء عدم التجاوب لموظف العمليات أو الدعم، ويظهر للمشرف فقط مع تسجيل القرار وسببه.', True)
    adm43 = req('ADM-043')
    add_rule(adm43, 'الإلغاء اليدوي بسبب، والاسترداد والتعويض، وإنهاء عدم التجاوب إجراءات للمشرف أو المدير فقط. موظف العمليات يصعّد الحالة، وموظف الدعم يراجع ويطلب الإجراء.')
    add_rule(adm43, 'يرفض الخادم طلب التنفيذ المالي أو الإلغاء أو الإنهاء من دور العمليات أو الدعم، حتى إذا حاول استدعاءه مباشرةً.', True)
    text(req('SUP-002'), 'حدود مالية لكل موظف وتصعيد', 'يراجع الدعم الأدلة ويرفع طلب التسوية؛ ينفذ المشرف الاسترداد أو التعويض ضمن حده، ويصعّد ما يتجاوزه.')
    text(admin, 'الإسناد اليدوي والإلغاء', 'الإسناد اليدوي وتصعيد طلب الإلغاء')
    text(admin, 'الاسترداد حتى 100 ر.س', 'تصعيد طلب الاسترداد للمشرف')
    text(admin, 'حدّك في الاسترداد: 100 ر.س', 'الدعم يرفع الطلب؛ ينفذ المشرف الاسترداد أو التعويض ضمن حده المالي.')
    text(admin, 'استرداد 1.50 للبطاقة', 'طلب استرداد 1.50 للبطاقة')
    text(admin, 'نعتذر لك. راجعنا الطلب ونعيد لك قيمة الثومية الآن.', 'نعتذر لك. راجعنا الطلب ورفعنا للمشرف طلب استرداد قيمة الصنف وإعادة حساب الرسوم.')
    text(admin, 'لكل دور حد، وما فوقه يُحال إلى المشرف أو المالية.', 'الدعم يراجع ويطلب فقط؛ ينفذ المشرف ضمن حده المالي، وما فوقه يحتاج الاعتماد المحدد في ADM-043.')
    for table in admin.find_all('table'):
        if 'وافق عليه' in table.get_text():
            text(table, 'سارة · الدعم', 'سارة · مشرفة العمليات')
            text(table, 'خالد · الدعم', 'خالد · مشرف العمليات')
        if 'المستخدم' in table.get_text() and 'استرداد #1031' in table.get_text():
            text(table, 'استرداد #1031', 'طلب استرداد #1031')
    # الأزرار في واجهة الدعم ترفع طلباً، بما فيها الاعتراضات.
    for page_node in admin.select('details.page'):
        if page_node.select_one('.pn').get_text(strip=True) == 'الدعم والشكاوى':
            for old, new in [('رصيد استرداد', 'طلب رصيد استرداد'), ('مكافأة تعويض', 'طلب مكافأة تعويض'),
                             ('قبول وإعادة المبلغ', 'طلب قبول وإعادة المبلغ'), ('قبول جزئي', 'طلب قبول جزئي')]:
                text(page_node, old, new, minimum=0)
            text(page_node, 'القرار يصل لصاحب الاعتراض بإشعار، ويُسجَّل في سجل التدقيق',
                 'يرفع الدعم التوصية للمشرف؛ بعد اعتماده وتنفيذ التسوية يصل القرار لصاحب الاعتراض بإشعار ويُسجَّل في سجل التدقيق')
            for button in page_node.select('.sbt'):
                if button.get_text(strip=True) == 'استرداد للعميل':
                    button.string = 'طلب استرداد للعميل'
            for heading in page_node.find_all('h6', string='القرار'):
                heading.string = 'التوصية للمشرف'
            for li in page_node.find_all('li', string='تعويض'):
                li.string = 'طلب تعويض'
            text(page_node, 'ملف أدلة تلقائي · القرار: استرداد أو رفض بسبب أو تحويل لمشرف',
                 'ملف أدلة تلقائي · يراجع الدعم ويوصي باسترداد أو رفض بسبب؛ يعتمد المشرف الإجراء المالي وينفذه.')
    # المصفوفة تميز المشرف عن موظف العمليات والدعم.
    matrix = next(t for t in admin.find_all('table') if 'الصلاحية' in t.get_text() and 'اعتماد دفعة تحويل' in t.get_text())
    headers = matrix.find('tr').find_all('th')
    headers[4].string = 'موظف عمليات'
    th = soup.new_tag('th'); th.string = 'مشرف عمليات'; headers[4].insert_after(th)
    for row in matrix.find_all('tr')[1:]:
        cells = row.find_all('td')
        name = cells[0].get_text(strip=True)
        supervisor = fragment('<td><span class="no2">—</span></td>')
        if name == 'استرداد حتى 100 ر.س':
            cells[0].string = 'استرداد ضمن حد المشرف'
            supervisor = fragment('<td>ضمن الحد المعتمد</td>')
            cells[4].clear(); cells[4].append(fragment('<span class="no2">—</span>'))
            cells[5].clear(); cells[5].append(fragment('<span class="no2">طلب فقط</span>'))
        elif name == 'استرداد أكثر من 100':
            cells[0].string = 'استرداد فوق حد المشرف'
            supervisor = fragment('<td>اعتماد ثانٍ</td>')
            cells[5].string = 'طلب فقط'
        cells[4].insert_after(supervisor)
    # بنود الكشف تستخدم الضريبة الموجودة في القواعد، بلا تغيير للسياسة.
    merchant = section('merchant-dash')
    fee = merchant.find(string='رسم البوابة')
    assert fee is not None
    fee.parent.parent.insert_after(fragment('<div><span>ضريبة رسم الدفع 15%</span><span style="color:var(--r)">−0.37</span></div>'))
    fee_row = next(r for r in merchant.find_all('tr') if 'رسم بوابة الدفع (2.5% + 1 لكل طلب)' in r.get_text())
    fee_row.insert_after(fragment('<tr><td>ضريبة رسم الدفع 15%</td><td style="text-align:left;direction:ltr;color:var(--r)">−394.03</td></tr>'))
    text(merchant, 'رسم البوابة، وحصتك', 'رسم البوابة وضريبته، وحصتك')
    text(req('MER-008'), 'ورسم البوابة والتعويضات', 'ورسم البوابة وضريبته والتعويضات')
    detail_table = next(t for t in merchant.find_all('table') if '#1045' in t.get_text() and '60.92' in t.get_text())
    th = soup.new_tag('th'); th.string = 'ضريبة البوابة'
    detail_table.find_all('th')[4].insert_after(th)
    for row, vat, net in zip(detail_table.find_all('tr')[1:], ['−0.42', '−0.37', '−0.23'], ['60.50', '43.51', '17.69']):
        cells = row.find_all('td'); td = soup.new_tag('td'); td.string = vat; cells[4].insert_after(td); cells[-1].string = net
    text(merchant, '43.88', '43.51')
    fee = admin.find(string='رسم الدفع')
    # نختار سطر كشف التاجر المحدد، لا بقية أمثلة الرسوم في اللوحة.
    fee = next(x for x in admin.find_all(string='رسم الدفع') if '−2,626.85' in x.parent.parent.get_text())
    fee.parent.parent.insert_after(fragment('<div><span>ضريبة رسم الدفع 15%</span><span>−394.03</span></div>'))
    for id in ['app-merchant', 'merchant-dash', 'admin-pages']:
        text(section(id), '36,660.25', '36,266.22')
    # تبقى ضريبة إجمالي الفترة مثالاً حسابياً، والفعلية مجموع ضرائب الطلبات.
    fee_row.find_parent('table').insert_after(fragment('<p class="t11 mut">أرقام توضيحية؛ ضريبة رسم الدفع في هذا المثال 394.03 ر.س. في الكشف الفعلي تُجمع الضريبة المحسوبة والمقرّبة لكل طلب.</p>'))

    # مطلوبان مع الإطلاق؛ يتحدث ملخص النطاق من الفهرس الفعلي.
    for id in ['MER-005', 'DRV-013']:
        node = req(id); node['data-p'] = 'p1'
        tag = node.select_one('.tag.p2'); tag['class'] = ['tag', 'p1']; tag.string = 'أساسي للإطلاق'
    add_rule(req('MER-005'), 'منيوهات المناوبات تخص متاجر المنيو. البقالات في المارت لها مناوبات عمل لتحديد إتاحتها في التوزيع، لكن كتالوج العميل موحد ولا تُنشئ البقالة منيو مستقلاً. الصيدليات تستقبل طلبات كتابة بلا منيو.')
    scope = section('scope')
    text(scope, '(192 متطلباً)', '(194 متطلباً)')
    text(scope, '«مهم» (56)', '«مهم» (54)')
    for id in ['MER-005', 'DRV-013']:
        scope.find('a', href='#'+id).find_parent('li').decompose()
    first_scope_row = scope.find('tbody').find('tr').find_all('td')[1]
    first_scope_row.append(NavigableString(' وتشمل إدارة المناوبات والمنيو (MER-005) وسجل المعدات وحقيبة التبريد (DRV-013).'))
    count_table = next(t for t in scope.find_all('table') if t.find('th', string='الوحدة'))
    counts = Counter(d['data-p'] for d in cat.select('details.req[id]'))
    for row in count_table.select('tbody tr'):
        cells = row.find_all('td'); code = cells[0].find('bdi')
        subtotal = Counter(d['data-p'] for d in cat.select('details.req[id]') if code and d['id'].startswith(code.get_text()+'-')) if code else counts
        for i, priority in enumerate(['p1','p2','p3'], 1): cells[i].string = str(subtotal[priority])
    assert counts == {'p1':194, 'p2':54, 'p3':28}, counts
    decisions = section('decisions')
    text(decisions, 'والتقريب، وهل يبقى سقف 40 دقيقة على الناتج.', 'والتقريب. سقف الناتج 40 دقيقة معتمد، ولا يتغير.')
    d3 = next(r for r in decisions.find_all('tr') if r.find('td') and r.find('td').get_text(strip=True) == 'D-03')
    d3.find_all('td')[1].append(NavigableString(' وبقرار المالك في الإصدار 3.4 رُفعت MER-005 وDRV-013 إلى «أساسي للإطلاق».'))

    # الأشهر الثلاثة حد الكمية المصروفة، لا صلاحية موحدة للوصفة.
    pharmacy = section('pharmacy')
    text(pharmacy, 'تظل الوصفة صالحة للصرف حتى 3 أشهر.',
         'لا يعتمد الصيدلي كمية من دواء وصفي تتجاوز احتياج 3 أشهر بحسب الوصفة (PHR-001). هذا حد للكمية المصروفة، وليس مدة صلاحية موحدة للوصفة؛ يتحقق الصيدلي من صلاحيتها أثناء المراجعة.')
    text(req('PHR-001'), 'حد الأشهر الثلاثة', 'حد كمية الدواء لاحتياج ثلاثة أشهر')
    add_rule(req('PHR-001'), 'لا يحوّل النظام حد احتياج الثلاثة أشهر إلى مدة صلاحية تلقائية للوصفة؛ صلاحيتها جزء من مراجعة الصيدلي.')
    add_rule(req('PHR-001'), 'لا تُقبل وصفة لمجرد أن عمرها أقل من ثلاثة أشهر؛ يراجع الصيدلي صلاحيتها وعناصرها قبل اعتماد كمية الدواء.', True)

    for id in ['taxi','catalog']:
        node = section(id)
        for old, new in [('عند تجاوز 5 شكاوى صحيحة', 'عند بلوغ 5 شكاوى صحيحة'),
                         ('عند تجاوز عدد شكاواه الصحيحة 5', 'عند بلوغ عدد شكاواه الصحيحة 5'),
                         ('إذا تجاوزت شكاواه الصحيحة 5 شكاوى', 'عند بلوغ شكاواه الصحيحة 5 شكاوى'),
                         ('بعد 5 شكاوى صحيحة', 'عند بلوغ 5 شكاوى صحيحة')]:
            text(node, old, new, minimum=0)
    add_rule(req('TAX-016'), 'أربع شكاوى صحيحة لا تُفعّل هذا الإيقاف؛ تأكيد الشكوى الخامسة يفعّل إيقاف 30 يوماً مرة واحدة ويسجل سببه.', True)

    # الإصدار وسجل القرارات المعتمدة؛ سجل 3.3 يبقى تاريخياً.
    log = section('changelog')
    log.find('h2').insert_after(fragment('''<div id="owner-decisions-20260930"><h3>الإصدار 3.4 · 30 سبتمبر 2026</h3><ul class="rules">
<li>المارت موحد للعميل: كتالوج وطلب وهوية واحدة، والبقالات مخفية. تقبل بقالة أولاً بعد العرض المتتابع؛ ثم يبدأ إسناد المندوب. توحيد رحلة الطلب وقواعد ORD-003 وORD-006 مع DSP-005.</li>
<li>مدة التحضير مرنة بقواعدها الحالية، وتعديل واحد خلال 3 دقائق، بحد أقصى 40 دقيقة يشمل وضع الانشغال؛ أُزيلت صلاحية تجاوز الحد.</li>
<li>الصلاحيات: موظف العمليات يسند ويصعّد، والدعم يراجع ويرفع الطلب، والمشرف ينفذ الإلغاء والاسترداد والتعويض وإنهاء عدم التجاوب ضمن صلاحياته. تصحيح القواعد ومعايير القبول وأزرار الشاشات والمصفوفة.</li>
<li>MER-005 إدارة المناوبات والمنيو، وDRV-013 سجل المعدات وحقيبة التبريد، صارا أساسيين للإطلاق. الإجمالي 276: منها 194 أساسياً و54 مهماً و28 لاحقاً.</li>
<li>تصحيح رسومات كشف التاجر بإظهار ضريبة رسم الدفع وإعادة حساب الصافي والتحويلات؛ بقيت قواعد الدفع والضريبة الموجودة كما هي.</li>
<li>الصيدليات: الثلاثة أشهر حد كمية الدواء بحسب الوصفة، وليست صلاحية موحدة لها. Taxi: الإيقاف 30 يوماً عند بلوغ خمس شكاوى صحيحة، مع اختبار الحد بين الرابعة والخامسة.</li>
<li>إصلاح عداد فهرس المتطلبات والفلترة، وفتح الروابط المباشرة إلى المتطلبات عند تحميل الصفحة.</li>
</ul></div>'''))
    text(section('start'), 'الإصدار 3.3', 'الإصدار 3.4')
    # الروابط المضافة بعد تحريرات الصياغة تفتح المتطلبات مثل بقية الوثيقة.
    for id in changed - {'catalog'}:
        for item in list(soup.find('section', id=id).find_all(string=True)):
            if item.parent.name in {'a', 'bdi', 'script', 'style'} or item.find_parent('a'):
                continue
            value = str(item)
            matches = [m for m in re.finditer(r'\b[A-Z]{3}-\d{3}\b', value) if req(m.group())]
            if not matches:
                continue
            parts = []; previous = 0
            for match in matches:
                parts.append(NavigableString(value[previous:match.start()]))
                a = soup.new_tag('a', href='#'+match.group()); a['class'] = ['rid']; a.string = match.group(); parts.append(a)
                previous = match.end()
            parts.append(NavigableString(value[previous:]))
            item.replace_with(*parts)
    # الاحتفاظ بكل باقي الصفحة والرسومات خارج الأقسام المعدلة حرفياً.
    for id in changed:
        pattern = r'<section\b[^>]*\bid="'+re.escape(id)+r'"[^>]*>.*?</section>'
        page, count = re.subn(pattern, lambda m: str(soup.find('section', id=id)), page, count=1, flags=re.S)
        assert count == 1, id
    page = page.replace('الإصدار 3.3.</footer>', 'الإصدار 3.4.</footer>')
    # شارة الإصدار في الغلاف تقع خارج الأقسام.
    page = page.replace('مرجع التنفيذ · الإصدار 3.3', 'مرجع التنفيذ · الإصدار 3.4')
    return page


if __name__ == '__main__':
    target = Path(__file__).resolve().parents[1] / 'index.html'
    before = target.read_text(encoding='utf-8')
    after = apply(before)
    target.write_text(after, encoding='utf-8')
    print('Owner decisions applied' if before != after else 'Owner decisions already applied')
