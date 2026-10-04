# -*- coding: utf-8 -*-
"""يبني موقع المتطلبات (الإصدار 4) من ملف المالك الجديد."""
import os, sys, json, shutil, re
from b4_common import *
import b4_pages as P
import b4_rules as R
import b4_front as F
import b4_changes as C
import b4_md as M

OUT = sys.argv[1] if len(sys.argv) > 1 else (os.path.dirname(HERE) if os.path.basename(HERE) == 'tools' else os.path.join(HERE, 'site4'))

# إصلاحات لغوية معتمدة وملاحظات المالك
FIXES = json.load(open(os.path.join(HERE, 'qa', 'fixes.json'), encoding='utf8')) if os.path.exists(os.path.join(HERE, 'qa', 'fixes.json')) else {}
NOTES = json.load(open(os.path.join(HERE, 'qa', 'notes.json'), encoding='utf8')) if os.path.exists(os.path.join(HERE, 'qa', 'notes.json')) else []
EDITLOG = json.load(open(os.path.join(HERE, 'qa', 'edit_log.json'), encoding='utf8')) if os.path.exists(os.path.join(HERE, 'qa', 'edit_log.json')) else []

# ترتيب الأقسام: (المعرّف في القائمة, العنوان, الجزء)
n = 0


def nxt():
    global n
    n += 1
    return n


body = []
nav = []


def add(sid, title, part, html):
    body.append(html)
    nav.append((part, sid, title))


add('start', 'ابدأ من هنا', 'البداية', F.start_section(nxt()))
add('scope', 'نطاق الإصدار الأول', 'البداية', F.scope_section(nxt()))
add('prelaunch', 'قبل التشغيل', 'البداية', F.prelaunch_section(nxt()))
add('glossary', 'المصطلحات', 'البداية', F.glossary_section(nxt()))
add('flows', 'رحلة الطلب', 'قواعد العمل', P.flows_section(nxt()))
add('money', 'الحسابات والرسوم', 'قواعد العمل', R.money_section(nxt()))
add('settings', 'القيم المرنة', 'قواعد العمل', R.settings_section(nxt()))
add('integrations', 'الربط مع الخدمات', 'قواعد العمل', R.integrations_section(nxt()))
add('quality', 'الجودة والتشغيل', 'قواعد العمل', R.quality_section(nxt()))
add('states', 'حالات الصفحات المشتركة', 'الواجهات', F.states_section(nxt()))
for sid, name, desc, _ in SURF:
    add('s-' + sid, name, 'الواجهات', P.surface_section(nxt(), sid, name, desc))
add('reports', 'التقارير', 'الواجهات', R.reports_section(nxt()))
add('catalog', 'فهرس المتطلبات', 'للتنفيذ', F.catalog_section(nxt(), FIXES))
add('changes', 'ما تغيّر عن 3.3', 'للتنفيذ', C.changes_section(nxt()))
add('notes', 'مسائل للمالك', 'للتنفيذ', C.notes_section(nxt(), NOTES, EDITLOG))

nav_html = ''
cur = None
for i, (part, sid, title) in enumerate(nav, 1):
    if part != cur:
        nav_html += '<div class="nav-part">%s</div>\n' % part
        cur = part
    nav_html += '<a href="#%s" data-sec="%s"><i>%d</i>%s</a>\n' % (sid, sid, i, esc(title))

tpl = open(os.path.join(HERE, 'template4.html'), encoding='utf8').read()
html_out = (tpl.replace('{{NAV}}', nav_html).replace('{{BODY}}', '\n'.join(body))
            .replace('{{VERSION}}', F.VERSION).replace('{{DATE}}', F.DATE).replace('{{N_REQ}}', str(F.N_REQ))
            .replace('{{N_PAGES}}', str(F.N_PAGES)).replace('{{N_FLOWS}}', str(len(P.FLOWS)))
            .replace('{{SPRITE}}', P.sprite_defs()))

os.makedirs(os.path.join(OUT, 'assets'), exist_ok=True)
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf8').write(html_out)
shutil.copy(os.path.join(HERE, 'style4.css'), os.path.join(OUT, 'assets', 'style.css'))
shutil.copy(os.path.join(HERE, 'mock4.css'), os.path.join(OUT, 'assets', 'mock.css'))
shutil.copy(os.path.join(HERE, 'app4.js'), os.path.join(OUT, 'assets', 'app.js'))
open(os.path.join(OUT, 'prd.md'), 'w', encoding='utf8').write(M.markdown(FIXES))
print('written', OUT, len(html_out), 'sections', len(nav), 'reqs', F.N_REQ, 'pages', F.N_PAGES, 'icons', len(P.SPRITE))
