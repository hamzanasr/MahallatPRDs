# -*- coding: utf-8 -*-
"""رسومات شاشات Taxi (نماذج توضيحية بنفس نظام رسومات بقية الوثيقة). كل الأسماء والأرقام في الرسومات تجريبية."""

ICONS = {
    'pin': '<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    'car': '<path d="M5 16l1.5-5h11L19 16"/><rect x="3" y="16" width="18" height="4" rx="1.5"/><circle cx="7.5" cy="20" r="1"/><circle cx="16.5" cy="20" r="1"/>',
    'star': '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>',
    'phone': '<path d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A17 17 0 0 1 3 5a2 2 0 0 1 2-2z"/>',
    'chat': '<path d="M4 5h16v11H9l-5 4z"/>',
    'shield': '<path d="M12 2l8 3v6c0 5-3.4 9-8 11-4.6-2-8-6-8-11V5z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    'share': '<circle cx="6" cy="12" r="2.3"/><circle cx="18" cy="6" r="2.3"/><circle cx="18" cy="18" r="2.3"/><path d="M8 11l8-4M8 13l8 4"/>',
    'search': '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/>',
    'home': '<path d="M3 11l9-7 9 7v9a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/>',
    'work': '<rect x="3" y="7" width="18" height="12" rx="2"/><path d="M9 7V5h6v2"/>',
    'clock': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    'user': '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    'card': '<rect x="3" y="6" width="18" height="12" rx="2"/><path d="M3 10h18M7 15h3"/>',
    'check': '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    'x': '<path d="M6 6l12 12M18 6L6 18"/>',
    'alert': '<path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18v.01"/>',
    'map': '<path d="M9 4l-6 2v14l6-2 6 2 6-2V4l-6 2z"/><path d="M9 4v14M15 6v14"/>',
    'chart': '<path d="M5 20V10M12 20V4M19 20v-7"/>',
    'wallet': '<rect x="3" y="6" width="18" height="13" rx="2"/><path d="M16 12.5h2"/><path d="M3 9h18"/>',
    'bag': '<path d="M5 8h14l-1 12H6z"/><path d="M9 8a3 3 0 0 1 6 0"/>',
    'nav': '<path d="M12 3l7 17-7-4-7 4z"/>',
    'edit': '<path d="M4 20h4L19 9l-4-4L4 16z"/>',
    'doc': '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 13h6M9 17h6"/>',
    'sos': '<circle cx="12" cy="12" r="9"/><path d="M12 7v6M12 16.5v.01"/>',
    'lock': '<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
    'plus': '<path d="M12 5v14M5 12h14"/>',
    'back': '<path d="M9 6l6 6-6 6"/>',
    'cam': '<path d="M4 7h4l2-3h4l2 3h4v12H4z"/><circle cx="12" cy="13" r="3.5"/>',
    'list': '<path d="M4 6h16M7 12h10M10 18h4"/>',
    'gear': '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"/>',
}


def I(name, cls='ic', extra=''):
    return '<svg class="%s" viewBox="0 0 24 24" aria-hidden="true"%s>%s</svg>' % (cls, extra, ICONS[name])


def an(n):
    return '<i class="an">%d</i>' % n


def blk(n, inner, style=''):
    return '<div style="position:relative;%s">%s%s</div>' % (style, an(n), inner)


# ---------------------------------------------------------------- خريطة
def map_svg(route=None, pins=(), cars=(), radar=None, w=300, h=300):
    """route: قائمة نقاط (x,y). pins: [(x,y,لون,نوع)] نوع: 'a' انطلاق أو 'b' وجهة أو 'me'. cars: [(x,y,زاوية)]"""
    roads = ('<path d="M-10 70 L320 40" stroke="#fff" stroke-width="13"/><path d="M-10 170 L320 150" stroke="#fff" stroke-width="16"/>'
             '<path d="M-10 250 L320 265" stroke="#fff" stroke-width="12"/><path d="M60 -10 L85 320" stroke="#fff" stroke-width="12"/>'
             '<path d="M170 -10 L150 320" stroke="#fff" stroke-width="16"/><path d="M255 -10 L275 320" stroke="#fff" stroke-width="11"/>')
    blocks = ('<rect x="95" y="80" width="45" height="55" rx="5" fill="#DCE6DD"/><rect x="185" y="185" width="55" height="45" rx="5" fill="#DCE6DD"/>'
              '<rect x="15" y="185" width="35" height="50" rx="5" fill="#DCE6DD"/><rect x="190" y="70" width="50" height="55" rx="5" fill="#D6E4EA"/>')
    out = ['<svg viewBox="0 0 %d %d" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><rect width="%d" height="%d" fill="#E9EEE9"/>' % (w, h, w, h), blocks, roads]
    if radar:
        x, y = radar
        out.append('<circle cx="%d" cy="%d" r="88" fill="#0B7A6F" opacity=".07"/><circle cx="%d" cy="%d" r="56" fill="#0B7A6F" opacity=".1"/><circle cx="%d" cy="%d" r="26" fill="#0B7A6F" opacity=".14"/>' % (x, y, x, y, x, y))
    if route:
        pts = ' '.join('%d,%d' % p for p in route)
        out.append('<polyline points="%s" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>'
                   '<polyline points="%s" fill="none" stroke="#0B7A6F" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>' % (pts, pts))
    for x, y, ang in cars:
        out.append('<g transform="translate(%d %d) rotate(%d)"><rect x="-6" y="-11" width="12" height="22" rx="4" fill="#16202B"/><rect x="-4" y="-6" width="8" height="5" rx="1.5" fill="#9AA6B2"/></g>' % (x, y, ang))
    for x, y, kind in pins:
        if kind == 'me':
            out.append('<circle cx="%d" cy="%d" r="11" fill="#2B59C3" opacity=".2"/><circle cx="%d" cy="%d" r="6" fill="#2B59C3" stroke="#fff" stroke-width="2.5"/>' % (x, y, x, y))
        elif kind == 'a':
            out.append('<circle cx="%d" cy="%d" r="8" fill="#fff" stroke="#0B7A6F" stroke-width="4"/>' % (x, y))
        else:
            out.append('<rect x="%d" y="%d" width="15" height="15" rx="3" fill="#16202B" stroke="#fff" stroke-width="2.5"/>' % (x - 7, y - 7))
    out.append('</svg>')
    return ''.join(out)


def map_box(height, fixed=False, **kw):
    if fixed:
        return '<div class="map" style="height:%dpx;border-radius:12px">%s</div>' % (height, map_svg(**kw))
    return '<div class="map" style="position:absolute;inset:0">%s</div>' % map_svg(**kw)


# ---------------------------------------------------------------- إطار الجوال
def status_bar():
    return '<div class="sb"><span>9:41</span><span class="isl"></span><span>5G ▮▮</span></div>'


def cust_nav(active='taxi'):
    items = [('home', 'الرئيسية'), ('bag', 'الطلبات'), ('car', 'Taxi'), ('user', 'حسابي')]
    key = {'home': 'home', 'bag': 'orders', 'car': 'taxi', 'user': 'me'}
    return '<div class="nav">%s</div>' % ''.join('<span%s>%s%s</span>' % (' class="on"' if key[i] == active else '', I(i, 'ic l'), t) for i, t in items)


def drv_nav(active='map'):
    items = [('map', 'الخريطة', 'map'), ('wallet', 'الأرباح', 'earn'), ('chat', 'الرسائل', 'msg'), ('user', 'حسابي', 'me')]
    return '<div class="nav">%s</div>' % ''.join('<span%s>%s%s</span>' % (' class="on"' if k == active else '', I(i, 'ic l'), t) for i, t, k in items)


def phone(body, nav='', label=''):
    return ('<div class="ph" aria-label="%s"><div class="sc">%s%s%s</div></div>' % (label, status_bar(), body, nav))


def stars(n=5):
    return '<span class="stars">%s</span>' % ('★' * n)


def avatar():
    return '<div class="av"></div>'


# ---------------------------------------------------------------- شاشات العميل
def c_home():
    body = ('<div style="flex:1;position:relative">' +
            map_box(258, pins=[(150, 150, 'me')], cars=[(90, 120, 20), (215, 105, -30), (120, 215, 70), (235, 195, 10)]) +
            '<div class="notif" style="top:10px"><i>%s</i><div><b>Taxi</b><div class="mut">سيارات متاحة بالقرب منك</div></div></div></div>' % I('car') +
            '<div class="sheet" style="gap:10px">' +
            blk(1, '<div class="srch" style="padding:11px 12px">%s<b class="t14" style="color:var(--k)">إلى أين؟</b></div>' % I('search')) +
            blk(2, '<div class="row" style="gap:8px"><span class="chip2">%s المنزل</span><span class="chip2">%s العمل</span><span class="chip2">%s إضافة</span></div>' % (I('home', 'ic s'), I('work', 'ic s'), I('plus', 'ic s'))) +
            blk(3, '<div class="ls"><div class="li row" style="padding:8px 2px;border-bottom:1px solid var(--l)">%s<span>الواجهة الشمالية · المدخل الرئيسي</span></div>'
                   '<div class="li row" style="padding:8px 2px">%s<span>حي النخيل · شارع الأمير</span></div></div>' % (I('clock', 'ic s'), I('clock', 'ic s'))) +
            '</div>')
    return phone(body, cust_nav('taxi'), 'رسم تخيلي: الصفحة الرئيسية لـTaxi')


def c_destination():
    body = ('<div class="bd" style="gap:10px;padding-top:10px">'
            '<div class="row sp"><b class="t16">وجهة المشوار</b><span class="cbtn">%s</span></div>' % I('x') +
            blk(1, '<div class="crd" style="padding:6px 10px"><div class="row" style="padding:7px 0;border-bottom:1px solid var(--l)"><span class="dot" style="margin:0"></span><div style="flex:1"><div class="mut t10">الانطلاق</div><b class="t13">موقعك الحالي · حي الياسمين</b></div></div>'
                   '<div class="row" style="padding:7px 0"><span class="dot" style="margin:0;background:#16202B"></span><div style="flex:1"><div class="mut t10">الوجهة</div><b class="t13">الواجهة الشمالية</b></div></div></div>') +
            blk(2, '<div class="row" style="gap:8px"><span class="chip2">%s تحديد على الخريطة</span><span class="chip2">%s المنزل</span><span class="chip2">%s العمل</span></div>' % (I('pin', 'ic s'), I('home', 'ic s'), I('work', 'ic s'))) +
            blk(3, '<div class="ls" style="background:var(--c);border:1px solid var(--l);border-radius:12px;padding:2px 10px">'
                   '<div class="li row" style="padding:9px 0;border-bottom:1px solid var(--l)">%s<div style="flex:1"><b class="t13">الواجهة الشمالية</b><div class="mut t10">الرياض · 17 كم</div></div></div>'
                   '<div class="li row" style="padding:9px 0;border-bottom:1px solid var(--l)">%s<div style="flex:1"><b class="t13">الواجهة الشمالية · المدخل الرئيسي</b><div class="mut t10">الرياض · 17 كم</div></div></div>'
                   '<div class="li row" style="padding:9px 0">%s<div style="flex:1"><b class="t13">محطة قطار الرياض</b><div class="mut t10">الرياض · 12 كم</div></div></div></div>' % (I('pin', 'ic s'), I('pin', 'ic s'), I('pin', 'ic s'))) +
            '<div class="mut t10" style="text-align:center">الوجهة تحتاج إلى مدينة مفعّلة لـTaxi</div></div>')
    return phone(body, '', 'رسم تخيلي: اختيار الوجهة')


def c_choose():
    def row_(sel, name, seats, eta, price, sub):
        st = ' style="border-color:var(--p);background:var(--p2)"' if sel else ''
        return ('<div class="opt%s"%s><span class="cbtn" style="width:40px;height:40px;border-radius:12px">%s</span>'
                '<div style="flex:1"><b class="t13">%s</b> <span class="mut t10">%s</span><div class="mut t10">%s · %s</div></div><b class="t14">%s</b></div>'
                % (' on' if sel else '', st, I('car'), name, seats, eta, sub, price))
    body = ('<div style="flex:1;position:relative">' +
            map_box(190, route=[(78, 240), (78, 170), (150, 165), (215, 120), (240, 60)], pins=[(78, 240, 'a'), (240, 60, 'b')]) +
            '<div class="notif" style="top:8px"><i>%s</i><div><b>17 كم · 22 د</b><div class="mut">الواجهة الشمالية</div></div></div></div>' % I('nav') +
            '<div class="sheet" style="gap:8px">' +
            blk(1, row_(True, 'اقتصادي', '4 ركاب', 'يصل خلال 4 د', '38.80 ر.س', 'سيارة اقتصادية') +
                row_(False, 'مريح', '4 ركاب', 'يصل خلال 6 د', '51.50 ر.س', 'سيارة أوسع') +
                row_(False, 'عائلي', '6 ركاب', 'يصل خلال 9 د', '64.20 ر.س', 'للعائلات') +
                row_(False, 'بزنس', '4 ركاب', 'يصل خلال 8 د', '90.60 ر.س', 'سيارة فاخرة'), 'display:flex;flex-direction:column;gap:6px') +
            blk(2, '<div class="row sp crd" style="padding:8px 10px"><span class="row t12">%s بطاقة •••• 4242</span><span class="t12 mut">رصيد 12.50 ر.س</span></div>' % I('card')) +
            blk(3, '<div class="btn">اطلب اقتصادي · 38.80 ر.س</div>') +
            '</div>')
    return phone(body, '', 'رسم تخيلي: اختيار الفئة والسعر')


def c_search():
    body = ('<div style="flex:1;position:relative">' +
            map_box(300, radar=(150, 150), pins=[(150, 150, 'me')], cars=[(80, 95, 20), (225, 105, -35), (105, 220, 80)]) + '</div>'
            '<div class="sheet" style="gap:9px">' +
            blk(1, '<div class="row sp"><b class="t16">نبحث عن سائق قريب…</b><span class="pill">اقتصادي</span></div>') +
            '<div class="prog"><i style="width:35%"></i></div>' +
            blk(2, '<div class="near" style="background:var(--p2);color:var(--p)">%s إلغاء مجاني خلال 1:32</div>' % I('clock', 'ic s')) +
            '<div class="row sp crd" style="padding:8px 10px"><span class="t12">%s موقعك الحالي</span><span class="t12">← الواجهة الشمالية</span></div>' % I('pin', 'ic s') +
            blk(3, '<div class="btn gh">إلغاء الطلب</div>') + '</div>')
    return phone(body, '', 'رسم تخيلي: البحث عن سائق')


def c_ontheway():
    body = ('<div style="flex:1;position:relative">' +
            map_box(215, route=[(215, 60), (215, 110), (150, 118), (95, 165), (95, 205)], pins=[(95, 205, 'me')], cars=[(215, 60, 180)]) + '</div>'
            '<div class="sheet" style="gap:8px">' +
            '<div class="row sp"><b class="t16">السائق في الطريق</b><span class="pill g">يصل خلال 4 د</span></div>' +
            blk(1, '<div class="row crd" style="padding:8px 10px">%s<div style="flex:1"><b class="t13">خالد · 4.9 %s</b><div class="mut t10">2,340 مشوار · تويوتا كامري بيضاء</div></div>'
                   '<span class="crd" style="padding:2px 10px;font-weight:700;direction:ltr;letter-spacing:1px">ABC 1234</span></div>' % (avatar(), stars(1))) +
            blk(2, '<div class="row sp crd" style="padding:8px 12px"><div><div class="mut t10">كود بدء المشوار</div><b class="t22" style="letter-spacing:5px;direction:ltr">4729</b></div><div class="mut t10" style="max-width:120px;text-align:start">أعطِ الكود للسائق قبل الركوب</div></div>') +
            blk(3, '<div class="row" style="gap:8px"><span class="btn gh" style="flex:1">%s اتصال</span><span class="btn gh" style="flex:1">%s رسالة</span><span class="btn gh" style="flex:1">%s مشاركة</span><span class="btn gh" style="flex:0 0 40px">%s</span></div>' % (I('phone', 'ic s'), I('chat', 'ic s'), I('share', 'ic s'), I('shield', 'ic s'))) +
            blk(4, '<div class="row sp t11 mut"><span style="color:var(--r);font-weight:700">إلغاء</span><span>إلغاء مجاني خلال 0:58</span></div>') +
            '</div>')
    return phone(body, '', 'رسم تخيلي: السائق في الطريق')


def c_arrived():
    body = ('<div style="flex:1;position:relative">' + map_box(215, pins=[(150, 150, 'me')], cars=[(150, 150, 0)]) + '</div>'
            '<div class="sheet" style="gap:8px">' +
            '<div class="row sp"><b class="t16">السائق وصل</b><span class="pill o">أنت أمام السائق؟</span></div>' +
            blk(1, '<div class="row sp crd" style="padding:9px 12px"><div><div class="mut t10">الانتظار المجاني</div><b class="t22" style="direction:ltr">03:40</b></div><div class="mut t10" style="max-width:150px">بعد 5 دقائق يُحتسب رسم انتظار 0.40 ر.س للدقيقة (مثال)</div></div>') +
            '<div class="row crd" style="padding:8px 10px">%s<div style="flex:1"><b class="t13">خالد · 4.9</b><div class="mut t10">تويوتا كامري بيضاء</div></div><span class="crd" style="padding:2px 10px;font-weight:700;direction:ltr">ABC 1234</span></div>' % avatar() +
            blk(2, '<div class="row sp crd" style="padding:8px 12px"><span class="t12">كود البدء</span><b class="t18" style="letter-spacing:5px;direction:ltr">4729</b></div>') +
            blk(3, '<div class="row" style="gap:6px;flex-wrap:wrap"><span class="chip2">أنا قادم</span><span class="chip2">أنتظرني دقيقة</span><span class="chip2">أنا عند البوابة</span></div>') +
            '</div>')
    return phone(body, '', 'رسم تخيلي: وصل السائق')


def c_trip():
    body = ('<div style="flex:1;position:relative">' +
            map_box(255, route=[(95, 235), (95, 170), (150, 160), (215, 110), (240, 60)], pins=[(240, 60, 'b')], cars=[(150, 160, 300)]) +
            '<div class="notif" style="top:8px"><i>%s</i><div><b>الواجهة الشمالية</b><div class="mut">وصول 8:52 م · 12 كم متبقية</div></div></div></div>' % I('nav') +
            '<div class="sheet" style="gap:8px">' +
            '<div class="row sp"><b class="t16">في المشوار</b><span class="pill g">في الوقت</span></div>' +
            '<div class="row crd" style="padding:8px 10px">%s<div style="flex:1"><b class="t13">خالد · تويوتا كامري</b><div class="mut t10">ABC 1234</div></div><b class="t14">38.80 ر.س</b></div>' % avatar() +
            blk(1, '<div class="row" style="gap:8px"><span class="btn gh" style="flex:1">%s مشاركة المشوار</span><span class="btn gh" style="flex:1">%s تغيير الوجهة</span></div>' % (I('share', 'ic s'), I('edit', 'ic s'))) +
            blk(2, '<div class="row sp crd" style="padding:8px 10px;border-color:#F4C2BD;background:#FFF8F7"><span class="row t12" style="color:var(--r)">%s السلامة والطوارئ</span><span class="t10 mut">اضغط عند الحاجة</span></div>' % I('sos', 'ic s')) +
            '</div>')
    return phone(body, '', 'رسم تخيلي: أثناء المشوار')


def c_done():
    body = ('<div class="bd" style="gap:8px;padding-top:12px">'
            '<div style="text-align:center"><span class="cbtn" style="width:46px;height:46px;background:var(--g2);color:#0B7A43;display:inline-grid">%s</span><div class="b7 t16" style="margin-top:4px">وصلت بالسلامة</div><div class="mut t11">الواجهة الشمالية · 22 د · 17 كم</div></div>' % I('check', 'ic l') +
            blk(1, '<div class="crd sum t12"><div><span>السعر المسبق</span><span>38.80</span></div><div><span>رسم الانتظار</span><span>0.00</span></div><div><span>الإكرامية</span><span>+ 5.00</span></div><div class="b7"><span>المدفوع</span><span>43.80 ر.س</span></div></div>') +
            blk(2, '<div style="text-align:center"><div class="mut t11">قيّم مشوارك مع خالد</div>%s</div><div class="row" style="gap:5px;flex-wrap:wrap;justify-content:center"><span class="chip2">سياقة ممتازة</span><span class="chip2">سيارة نظيفة</span><span class="chip2">التزام بالمسار</span></div>' % stars(5)) +
            blk(3, '<div class="tipc"><span>2</span><span class="on">5</span><span>10</span><span>مبلغ آخر</span></div><div class="mut t10" style="text-align:center">الإكرامية كاملة للسائق</div>') +
            '<div class="btn sticky" style="position:static">إرسال</div></div>')
    return phone(body, '', 'رسم تخيلي: نهاية المشوار والتقييم')


def c_cancel():
    body = ('<div style="flex:1;position:relative;background:#cdd5d3">' + '<div style="position:absolute;inset:0;background:rgba(16,24,32,.45)"></div></div>'
            '<div class="sheet" style="gap:9px">' +
            '<div class="row sp"><b class="t16">إلغاء المشوار</b><span class="cbtn">%s</span></div>' % I('x') +
            blk(1, '<div class="crd" style="padding:8px 10px;background:#FFF8F0;border-color:#F3D08A"><b class="t12">رسم الإلغاء 10.00 ر.س (مثال)</b><div class="mut t11">أُلغي بعد دقيقتين من الطلب وقبل وصول السائق. الرسم يساوي الحد الأدنى للأجرة.</div></div>') +
            blk(2, '<div style="display:flex;flex-direction:column;gap:6px"><div class="opt on"><i></i>غيّرت رأيي</div><div class="opt"><i></i>وقت الانتظار طويل</div><div class="opt"><i></i>طلبت بالخطأ</div><div class="opt"><i></i>السائق طلب الإلغاء</div></div>') +
            '<div class="btn gh">إبقاء المشوار</div><div class="btn r">تأكيد الإلغاء</div>'
            '<div class="mut t10" style="text-align:center">لا رسم إذا تأخر السائق كثيراً عن الوقت المعلن أو لم يتحرك نحوك</div></div>')
    return phone(body, '', 'رسم تخيلي: إلغاء المشوار')


def c_safety():
    body = ('<div style="flex:1;position:relative;background:#cdd5d3"><div style="position:absolute;inset:0;background:rgba(16,24,32,.45)"></div></div>'
            '<div class="sheet" style="gap:8px">' +
            '<div class="row sp"><b class="t16">السلامة</b><span class="cbtn">%s</span></div>' % I('x') +
            blk(1, '<div class="crd" style="padding:9px 11px"><div class="row sp"><b class="t13">مشاركة المشوار</b><span class="tgl on"></span></div><div class="mut t11">يصل جهات الاتصال رابط تتبع مؤقت ينتهي بانتهاء المشوار، بلا رقم أي طرف.</div>'
                   '<div class="row" style="gap:6px;margin-top:6px"><span class="chip2">%s أمي</span><span class="chip2">%s سلطان</span><span class="chip2">%s إضافة</span></div></div>' % (I('user', 'ic s'), I('user', 'ic s'), I('plus', 'ic s'))) +
            blk(2, '<div class="btn r">%s اتصال بالطوارئ</div><div class="mut t10" style="text-align:center">يُرسل موقعك وتفاصيل المشوار إلى غرفة العمليات</div>' % I('sos', 'ic s')) +
            blk(3, '<div class="row sp crd" style="padding:9px 11px"><span class="t13">الإبلاغ عن مشكلة سلامة</span>%s</div>' % I('back', 'ic s')) +
            '<div class="row sp crd" style="padding:9px 11px"><span class="t13">تفاصيل السائق والمركبة</span>%s</div>' % I('back', 'ic s') +
            '</div>')
    return phone(body, '', 'رسم تخيلي: أدوات السلامة')


def c_history():
    body = ('<div class="bd" style="gap:8px;padding-top:10px">'
            '<div class="row sp"><b class="t16">تفاصيل المشوار</b><span class="cbtn">%s</span></div>' % I('x') +
            map_box(110, fixed=True, route=[(60, 210), (100, 150), (170, 130), (240, 60)], pins=[(60, 210, 'a'), (240, 60, 'b')]) +
            '<div class="row sp"><div><b class="t13">27 سبتمبر · 8:20 م</b><div class="mut t10">اقتصادي · خالد · ABC 1234</div></div><b class="t16">43.80 ر.س</b></div>' +
            blk(1, '<div class="crd sum t12"><div><span>السعر المسبق</span><span>38.80</span></div><div><span>الإكرامية</span><span>5.00</span></div><div><span>ضريبة القيمة المضافة المضمّنة في السعر</span><span>5.06</span></div></div>') +
            blk(2, '<div class="row" style="gap:8px"><span class="btn gh" style="flex:1">%s الإيصال</span><span class="btn gh" style="flex:1">%s إعادة الطلب</span></div>' % (I('doc', 'ic s'), I('nav', 'ic s'))) +
            blk(3, '<div class="ls"><div class="li row" style="padding:9px 2px;border-bottom:1px solid var(--l)">%s<span>الإبلاغ عن غرض مفقود</span>%s</div><div class="li row" style="padding:9px 2px;border-bottom:1px solid var(--l)">%s<span>مراجعة الأجرة</span>%s</div><div class="li row" style="padding:9px 2px">%s<span>الإبلاغ عن مشكلة</span>%s</div></div>' % (I('bag', 'ic s'), I('back', 'ic s'), I('card', 'ic s'), I('back', 'ic s'), I('alert', 'ic s'), I('back', 'ic s'))) +
            '</div>')
    return phone(body, '', 'رسم تخيلي: سجل المشوار')


# ---------------------------------------------------------------- شاشات السائق
def d_home():
    body = ('<div style="flex:1;position:relative">' + map_box(275, pins=[(150, 150, 'me')], cars=[(90, 100, 30), (220, 200, -40)]) +
            blk(1, '<div class="seg" style="margin:0"><span>توصيل</span><span class="on">Taxi</span></div>', 'position:absolute;top:10px;inset-inline:14px;background:none') + '</div>'
            '<div class="sheet" style="gap:9px">' +
            blk(2, '<div class="row sp"><div><span class="mst">%s متصل · بانتظار الطلبات</span></div><span class="tgl on"></span></div>' % '<i></i>') +
            blk(3, '<div class="kp k4" style="grid-template-columns:repeat(3,1fr);display:grid;gap:6px"><div style="background:var(--bg);border-radius:10px;padding:7px"><small class="mut t10">أرباح اليوم</small><b class="t14" style="display:block">186.40</b></div><div style="background:var(--bg);border-radius:10px;padding:7px"><small class="mut t10">مشاوير</small><b class="t14" style="display:block">9</b></div><div style="background:var(--bg);border-radius:10px;padding:7px"><small class="mut t10">القبول</small><b class="t14" style="display:block">92%</b></div></div>') +
            blk(4, '<div class="row sp crd" style="padding:8px 10px"><span class="t12 row">%s وجه تحققت منه اليوم 6:10 ص</span><span class="pill g">ساري</span></div>' % I('shield', 'ic s')) +
            '<div class="mut t10" style="text-align:center">في وضع Taxi لا تصلك طلبات التوصيل</div></div>')
    return phone(body, drv_nav('map'), 'رسم تخيلي: الرئيسية بوضع Taxi')


def d_request():
    body = ('<div style="flex:1;position:relative">' +
            map_box(190, route=[(95, 230), (150, 170), (215, 110), (240, 60)], pins=[(95, 230, 'a'), (240, 60, 'b')], cars=[(150, 250, 0)]) + '</div>'
            '<div class="sheet" style="gap:8px">' +
            blk(1, '<div class="row sp"><div><span class="pill b">مشوار Taxi · اقتصادي</span><div class="t22 b7" style="margin-top:4px">38.80 ر.س</div><div class="mut t11">أجرة العميل شاملة الضريبة</div></div><div class="ring"><b>12</b></div></div>') +
            blk(2, '<div class="row sp crd" style="padding:7px 10px"><span class="row t12">%s سارة · 4.8</span><span class="t11 mut">عميلة منذ 8 أشهر</span></div>' % I('user', 'ic s')) +
            blk(3, '<div class="vl"><div><span class="dot"></span><b class="t13">حي الياسمين</b><div class="mut t11">الاستلام · 1.1 كم · 3 د</div></div><div><span class="dot" style="background:#16202B"></span><b class="t13">الواجهة الشمالية</b><div class="mut t11">التوصيل · 17 كم · 22 د</div></div></div>') +
            '<div class="row" style="gap:8px"><div class="btn gh" style="flex:1">رفض</div><div class="btn" style="flex:2">قبول</div></div></div>')
    return phone(body, '', 'رسم تخيلي: طلب مشوار')


def d_pickup():
    body = ('<div style="flex:1;position:relative">' +
            map_box(230, route=[(215, 245), (150, 195), (95, 160), (95, 110)], pins=[(95, 110, 'a')], cars=[(215, 245, 320)]) +
            '<div class="notif" style="top:8px"><i>%s</i><div><b>ادخل شارع الياسمين</b><div class="mut">في 300 م · الوصول خلال 3 د</div></div></div></div>' % I('nav') +
            '<div class="sheet" style="gap:8px">' +
            blk(1, '<div class="row crd" style="padding:8px 10px">%s<div style="flex:1"><b class="t13">سارة · 4.8</b><div class="mut t10">حي الياسمين · شارع الأمير</div></div><span class="cbtn">%s</span><span class="cbtn">%s</span></div>' % (avatar(), I('phone'), I('chat'))) +
            blk(2, '<div class="btn">وصلت لنقطة الانطلاق</div>') +
            blk(3, '<div class="row sp t11 mut"><span style="color:var(--r);font-weight:700">إلغاء</span><span>الاتصال مقنّع</span></div>') +
            '</div>')
    return phone(body, '', 'رسم تخيلي: التوجه إلى العميل')


def d_wait():
    body = ('<div class="bd" style="gap:9px;padding-top:12px">'
            '<div class="row sp"><b class="t16">بانتظار العميل</b><span class="pill o">وصلت 8:41</span></div>' +
            blk(1, '<div class="crd" style="text-align:center;padding:10px"><div class="mut t11">الانتظار المجاني</div><div class="big" style="font-size:30px">03:20</div><div class="mut t10">بعد 5 دقائق يبدأ رسم الانتظار لصالحك</div><div class="prog" style="margin-top:6px"><i style="width:66%"></i></div></div>') +
            blk(2, '<div class="mut t11" style="text-align:center">اطلب من العميل كود البدء</div><div class="code"><span class="on">4</span><span class="on">7</span><span>·</span><span>·</span></div><div class="kb"><span>1</span><span>2</span><span>3</span><span>4</span><span>5</span><span>6</span><span>7</span><span>8</span><span>9</span><span></span><span>0</span><span>⌫</span></div>') +
            blk(3, '<div class="row" style="gap:8px"><span class="btn gh" style="flex:1">%s اتصال</span><span class="btn gh" style="flex:1">%s رسالة</span></div><div class="btn dis">العميل لم يحضر · بعد 5:00 واتصال ورسالة</div>' % (I('phone', 'ic s'), I('chat', 'ic s'))) +
            '</div>')
    return phone(body, '', 'رسم تخيلي: بانتظار العميل وإدخال الكود')


def d_trip():
    body = ('<div style="flex:1;position:relative">' +
            map_box(255, route=[(95, 235), (95, 170), (150, 160), (215, 110), (240, 60)], pins=[(240, 60, 'b')], cars=[(150, 160, 300)]) +
            '<div class="notif" style="top:8px"><i>%s</i><div><b>اتجه يميناً على طريق الأمير</b><div class="mut">بعد 2.4 كم</div></div></div></div>' % I('nav') +
            '<div class="sheet" style="gap:8px">' +
            blk(1, '<div class="row sp"><div><b class="t16">الواجهة الشمالية</b><div class="mut t11">وصول 8:52 م · 12 كم متبقية</div></div><span class="pill g">في الوقت</span></div>') +
            blk(2, '<div class="row" style="gap:8px"><span class="btn gh" style="flex:1">%s السلامة</span><span class="btn k" style="flex:2">إنهاء المشوار</span></div>' % I('sos', 'ic s')) +
            '<div class="mut t10" style="text-align:center">إنهاء المشوار بعيداً عن الوجهة يعيد حساب الأجرة على المسار الفعلي</div></div>')
    return phone(body, '', 'رسم تخيلي: أثناء المشوار')


def d_summary():
    body = ('<div class="bd" style="gap:8px;padding-top:12px">'
            '<div style="text-align:center"><div class="mut t11">أرباح المشوار</div><div class="big">31.34 ر.س</div></div>' +
            blk(1, '<div class="crd sum t12"><div><span>أجرة المشوار</span><span>38.80</span></div><div><span>ضريبة القيمة المضافة المضمّنة</span><span>− 5.06</span></div><div><span>نسبة المنصة 20% (مثال)</span><span>− 6.75</span></div><div><span>الإكرامية بعد الضريبة</span><span>+ 4.35</span></div><div class="b7"><span>صافي المشوار</span><span>31.34</span></div></div>') +
            blk(2, '<div style="text-align:center"><div class="mut t11">قيّم العميل</div>%s</div>' % stars(5)) +
            '<div class="btn">متابعة استقبال الطلبات</div></div>')
    return phone(body, drv_nav('map'), 'رسم تخيلي: ملخص المشوار للسائق')


def d_earn():
    bars = ''.join('<i%s style="height:%d%%"></i>' % (' class="on"' if k == 4 else '', v) for k, v in enumerate([35, 55, 40, 90, 60, 75, 20]))
    body = ('<div class="bd" style="gap:8px;padding-top:10px">'
            '<div class="row sp"><b class="t16">أرباح Taxi</b><div class="seg" style="width:120px;margin:0"><span class="on">الأسبوع</span><span>اليوم</span></div></div>' +
            blk(1, '<div class="crd"><div class="mut t11">صافي هذا الأسبوع</div><div class="big" style="text-align:start;font-size:24px">937.92 ر.س</div><div class="bars">%s</div></div>' % bars) +
            blk(2, '<div class="crd sum t12"><div><span>أجرة المشاوير بعد الضريبة</span><span>1,051.02</span></div><div><span>نسبة المنصة</span><span>− 210.20</span></div><div><span>الإكراميات بعد الضريبة</span><span>+ 74.70</span></div><div><span>رسوم إلغاء وانتظار</span><span>+ 22.40</span></div><div class="b7"><span>الصافي</span><span>937.92</span></div></div>') +
            blk(3, '<div class="row sp crd" style="padding:8px 10px"><span class="t12">التحويل القادم</span><b class="t13">الأحد</b></div>') +
            '</div>')
    return phone(body, drv_nav('earn'), 'رسم تخيلي: أرباح Taxi')


# ---------------------------------------------------------------- شاشات لوحة الإدارة
def admin_shell(side_html, title, body, sub=''):
    return ('<div class="wb tl" aria-label="رسم تخيلي: لوحة الإدارة · %s"><div class="wtop"><i></i><i></i><i></i><span class="u">لوحة الإدارة · %s</span></div>'
            '<div class="wmain">%s<div class="wc">%s</div></div></div>' % (title, title, side_html, body))


def a_pricing(side):
    hdr = '<div class="row sp"><b class="t18">Taxi · الفئات والتسعيرة</b><div class="row"><span class="pill k">الرياض</span><span class="sbt p">حفظ بتاريخ سريان</span></div></div>'
    tbl = ('<div class="pan"><h6>تسعيرة الفئات في المدينة (أرقام تجريبية)</h6><table class="tbl2 sm"><tr><th>الفئة</th><th>المقاعد</th><th>أساسي</th><th>للكيلو</th><th>للدقيقة</th><th>الحد الأدنى</th><th>نسبة المنصة</th><th>الحالة</th></tr>'
           '<tr><td>اقتصادي</td><td>4</td><td class="n">5.00</td><td class="n">1.60</td><td class="n">0.30</td><td class="n">10.00</td><td class="n">20%</td><td><span class="pill g">مفعّلة</span></td></tr>'
           '<tr><td>مريح</td><td>4</td><td class="n">7.00</td><td class="n">2.10</td><td class="n">0.40</td><td class="n">14.00</td><td class="n">20%</td><td><span class="pill g">مفعّلة</span></td></tr>'
           '<tr><td>عائلي</td><td>6</td><td class="n">9.00</td><td class="n">2.60</td><td class="n">0.50</td><td class="n">18.00</td><td class="n">20%</td><td><span class="pill g">مفعّلة</span></td></tr>'
           '<tr><td>بزنس</td><td>4</td><td class="n">14.00</td><td class="n">3.60</td><td class="n">0.70</td><td class="n">25.00</td><td class="n">20%</td><td><span class="pill a">موقوفة</span></td></tr></table></div>')
    pol = ('<div class="g2b"><div class="pan"><h6>الإلغاء والانتظار</h6><div class="sum t12"><div><span>إلغاء مجاني بعد الطلب</span><span>2 د</span></div><div><span>رسم الإلغاء بعدها</span><span>الحد الأدنى للأجرة</span></div>'
           '<div><span>انتظار مجاني عند الوصول</span><span>5 د</span></div><div><span>رسم الانتظار بعدها</span><span>سعر دقيقة الفئة</span></div><div><span>إعفاء رسم الإلغاء عند تأخر السائق أكثر من</span><span>5 د</span></div></div></div>'
           '<div class="pan"><h6>المطابقة</h6><div class="sum t12"><div><span>مهلة قبول السائق</span><span>15 ث</span></div><div><span>مهلة البحث عن سائق</span><span>3 د</span></div><div><span>كود البدء</span><span>4 أرقام</span></div><div><span>تنبيه العمليات بعد كود خاطئ</span><span>3 محاولات</span></div></div></div></div>')
    return admin_shell(side, 'Taxi', hdr + '<div class="al"><i style="background:var(--a)"></i><div class="t12" style="flex:1">تغيير التسعيرة يسري على المشاوير الجديدة فقط، ولا يغيّر مشواراً مؤكداً. لا تسعير ديناميكي في الإصدار الأول.</div></div>' + tbl + pol)


def a_drivers(side):
    hdr = '<div class="row sp"><b class="t18">Taxi · السائقون</b><div class="fb"><span class="fc on">بانتظار الموافقة 6</span><span class="fc">موافق عليهم 38</span><span class="fc">موقوفون 2</span><span class="fc">تحت المتابعة 5</span></div></div>'
    kp = '<div class="kp k4"><div><small>موافق عليهم</small><b>38</b></div><div><small>بانتظار الموافقة</small><b>6</b></div><div><small>تحقق الوجه اليوم</small><b>31</b></div><div><small>موقوفون</small><b>2</b></div></div>'
    q = ('<div class="pan"><h6>طلبات الانضمام</h6><table class="tbl2 sm"><tr><th>السائق</th><th>الهوية والرخصة</th><th>الصحيفة الجنائية</th><th>المركبة</th><th>التأمين والفحص</th><th>الوجه</th><th></th></tr>'
         '<tr><td>D-3107</td><td><span class="pill g">✓</span></td><td><span class="pill g">✓ محدثة</span></td><td>سيدان 2023 · اقتصادي</td><td><span class="pill g">ساريان</span></td><td><span class="pill g">صورة مرجعية ✓</span></td><td><span class="sbt p">موافقة</span></td></tr>'
         '<tr><td>D-0551</td><td><span class="pill g">✓</span></td><td><span class="pill a">تنتهي بعد 20 يوماً</span></td><td>سيدان 2021 · مريح</td><td><span class="pill r">التأمين منتهٍ</span></td><td><span class="pill a">بلا صورة</span></td><td><span class="sbt">طلب استكمال</span></td></tr>'
         '<tr><td>D-2288</td><td><span class="pill g">✓</span></td><td><span class="pill g">✓</span></td><td>فان 7 مقاعد · عائلي</td><td><span class="pill g">ساريان</span></td><td><span class="pill g">✓</span></td><td><span class="sbt p">موافقة</span></td></tr></table></div>')
    qual = ('<div class="g2b"><div class="pan"><h6>سائقون تحت المتابعة (آخر 7 أيام)</h6><table class="tbl2 sm"><tr><th>السائق</th><th>القبول</th><th>الإلغاء</th><th>التقييم</th><th>الإجراء</th></tr>'
            '<tr><td>D-1420</td><td class="n">55%</td><td class="n">3%</td><td class="n">4.8</td><td><span class="pill a">إيقاف 24 ساعة</span></td></tr>'
            '<tr><td>D-0913</td><td class="n">88%</td><td class="n">11%</td><td class="n">4.7</td><td><span class="pill a">إيقاف مؤقت</span></td></tr>'
            '<tr><td>D-2001</td><td class="n">91%</td><td class="n">2%</td><td class="n">4.5</td><td><span class="pill r">مراجعة وإيقاف</span></td></tr></table></div>'
            '<div class="pan"><h6>الشكاوى الصحيحة</h6><table class="tbl2 sm"><tr><th>السائق</th><th>الشكاوى</th><th>الحالة</th></tr>'
            '<tr><td>D-0913</td><td class="n">5 من 5</td><td><span class="pill r">إيقاف 30 يوماً</span></td></tr>'
            '<tr><td>D-2001</td><td class="n">2 من 5</td><td><span class="pill k">تحت المراجعة</span></td></tr></table></div></div>')
    return admin_shell(side, 'Taxi', hdr + kp + q + qual)


def set_active(side, label):
    import re
    side = side.replace(' class="on"', ' class=""').replace('<span class="on">', '<span class="">')
    pat = re.compile(r'<span class="">(<svg[^>]*>.*?</svg>) ' + re.escape(label) + '</span>', re.S)
    return pat.sub(lambda m: '<span class="on">' + m.group(1) + ' ' + label + '</span>', side, count=1)


def a_ride(side):
    side = set_active(side, 'غرفة العمليات')
    hdr = '<div class="row sp"><b class="t18">مشوار T-5521 · Taxi</b><div class="row"><span class="pill b">Taxi</span><span class="pill o">في الطريق للعميل</span></div></div>'
    mp = ('<div class="pan" style="padding:0;overflow:hidden"><div class="map" style="height:230px">%s</div></div>'
          % map_svg(route=[(215, 245), (150, 195), (95, 160), (95, 110)], pins=[(95, 110, 'a'), (240, 60, 'b')], cars=[(215, 245, 320)]))
    tl = ('<div class="pan"><h6>الخط الزمني</h6><div class="tl2"><div><small>8:31</small><i></i><span>طلب المشوار · اقتصادي · 38.80 ر.س</span></div>'
          '<div><small>8:31</small><i></i><span>حجز المبلغ</span></div><div><small>8:32</small><i></i><span>قبل السائق D-2144 بعد رفض سائقين</span></div>'
          '<div><small>8:37</small><i style="background:var(--a)"></i><span>السائق متأخر 6 د عن الوقت المعلن · إعفاء رسم الإلغاء</span></div>'
          '<div><small>—</small><i style="background:#CBD3DA"></i><span>وصول السائق · كود البدء · المشوار</span></div></div></div>')
    info = ('<div class="pan"><h6>الأطراف والمبالغ</h6><div class="sum t12"><div><span>العميلة</span><span>C-40233 · 4.8</span></div><div><span>السائق</span><span>D-2144 · 4.9 · ABC 1234</span></div>'
            '<div><span>السعر المسبق</span><span>38.80</span></div><div><span>الحجز</span><span>38.80 محجوز</span></div></div></div>')
    act = ('<div class="pan"><h6>الإجراءات</h6><div class="acts"><span class="sbt p">%s اتصال بالعميلة</span><span class="sbt">%s اتصال بالسائق</span><span class="sbt">إسناد لسائق آخر</span><span class="sbt r">إلغاء مع الاسترداد (مشرف)</span></div></div>' % (I('phone', 'ic s'), I('phone', 'ic s')))
    return admin_shell(side, 'غرفة العمليات', hdr + '<div class="g2">' + mp + '<div style="display:flex;flex-direction:column;gap:12px">' + info + act + '</div></div>' + tl)
