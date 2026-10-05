# -*- coding: utf-8 -*-
"""يجهّز ملف سياق لكل مجموعة صفحات: الصفحات، والمتطلبات التي تحكمها، والمتطلبات غير المغطاة المسندة لها."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from b4_common import D, REQ, PAGES, USED, PRI
import b4_annex as X
import b4_decisions as DEC

GROUPS = {
    'cust-a': dict(pages=['C%02d' % i for i in range(1, 13)], new=['C25', 'C26', 'C27'],
                   extra=['CUS-008', 'CRT-002', 'CRT-003', 'CRT-004', 'ORD-011', 'PAY-001', 'PAY-015', 'MKT-014', 'EXT-004', 'PHR-008', 'MER-024']),
    'cust-b': dict(pages=['C%02d' % i for i in range(13, 25)], new=['C28', 'C29', 'C30'],
                   extra=['MKT-002', 'SUP-003', 'SUP-007', 'SUP-009', 'PAY-026', 'CUS-008']),
    'driver': dict(pages=['D%02d' % i for i in range(1, 14)], new=['D14', 'D15', 'D16'],
                   extra=['DRV-004', 'DRV-005', 'DRV-007', 'DRV-011', 'DRV-018', 'DRV-019', 'DRV-021', 'DRV-024', 'DRV-027', 'DRV-028',
                          'DRV-029', 'DRV-030', 'PAY-026', 'ORD-012', 'MER-020', 'DSP-001']),
    'merchant': dict(pages=['M%02d' % i for i in range(1, 13)], new=['M13', 'M14', 'M15'],
                     extra=['MER-020', 'MER-022', 'MER-024', 'MER-026', 'MER-028', 'MER-030', 'MER-038', 'MER-040', 'MER-042', 'ORD-007', 'MER-032']),
    'merchant-dash': dict(pages=['MD%02d' % i for i in range(1, 14)], new=['MD14', 'MD15', 'MD16'],
                          extra=['PAY-010', 'PAY-011', 'PAY-022', 'MER-009', 'MER-013', 'MER-026', 'MER-029', 'MER-034', 'MER-041', 'MER-043',
                                 'MER-045', 'MER-047', 'MKT-005', 'INT-009', 'INT-012', 'MKT-014']),
    'admin-a': dict(pages=['A%02d' % i for i in range(1, 12)], new=['A23', 'A24', 'A25'],
                    extra=['ADM-004', 'ADM-005', 'ADM-009', 'ADM-010', 'ADM-012', 'ADM-014', 'ADM-015', 'ADM-032', 'ADM-035', 'ADM-044',
                           'DSP-001', 'DSP-004', 'ORD-004', 'ORD-006', 'ORD-007', 'ORD-012', 'MER-038', 'SUP-003', 'DRV-027', 'PAY-026', 'ORD-008', 'PHR-012', 'EXT-006', 'ORD-013']),
    'admin-b': dict(pages=['A%02d' % i for i in range(12, 23)], new=['A26', 'A27', 'A28', 'A29'],
                    extra=['ADM-001', 'ADM-002', 'ADM-034', 'ADM-036', 'ADM-040', 'MKT-002', 'MKT-005', 'MKT-014', 'SUP-003', 'SUP-007', 'SUP-009',
                           'INT-001', 'INT-010', 'INT-013', 'PAY-022', 'PAY-027', 'PAY-029', 'SYS-006', 'SYS-012', 'SYS-013', 'SYS-019', 'SYS-021', 'REP-001', 'PAY-006', 'PAY-024']),
}


def req_txt(rid):
    r = REQ[rid]
    s = ['### %s — %s [%s]' % (rid, r['title'], PRI[r['priority']][1])]
    s += ['- ' + x for x in r['rules']]
    s += ['- ✓ ' + x for x in r['acceptance']]
    return '\n'.join(s)


def main():
    for g, c in GROUPS.items():
        L = ['# سياق المجموعة %s' % g, '']
        L += ['## الصفحات الحالية', '']
        refs = set()
        for pid in c['pages']:
            p = PAGES[pid]
            refs |= set(p['refs'])
            L += ['### %s — %s' % (pid, p['title']),
                  '- الغرض: ' + p['purpose'],
                  '- النوع: ' + p['kind'],
                  '- العناصر (fields): ' + ' | '.join(p['fields']),
                  '- الإجراءات (actions): ' + ' | '.join(p['actions']),
                  '- حالات خاصة: ' + ' | '.join(s for s in p['states'] if s not in D['pages'][0]['states']),
                  '- المتطلبات: ' + ' '.join(p['refs']),
                  '- تنتقل إلى: ' + ' '.join(p['links']),
                  '- المعاينة الحالية: previews_raw.json["%s"] (صوّرها: python ux/shot.py %s)' % (pid, pid), '']
        L += ['## معرّفات الصفحات الجديدة المسموحة لك', '', ', '.join(c['new']), '']
        L += ['## متطلبات غير مغطاة بأي صفحة، مسندة لهذه المجموعة (يجب أن تظهر في صفحة)', '']
        L += [req_txt(r) for r in c['extra'] if r in REQ]
        L += ['', '## نص المتطلبات التي تحكم صفحاتك', '']
        L += [req_txt(r) for r in sorted(refs) if r not in c['extra']]
        L += ['', '## الحالات المشتركة الخمس (لا تكررها في الصفحات)', ''] + ['- ' + s for s in D['pages'][0]['states']]
        open(os.path.join(HERE, 'ctx', g + '.md'), 'w', encoding='utf8').write('\n'.join(L))

    # ملف مشترك: القرارات والملاحق
    L = ['# قرارات المالك والملاحق (مرجع مشترك)', '', '## القرارات']
    L += ['%d. %s: %s (%s)' % (n, t, d, ' '.join(ids)) for n, t, d, ids in DEC.DECISIONS]
    for sid, title, sub, blocks in X.ANNEX:
        L += ['', '## ' + title, sub, ''] + X.blocks_md(blocks)
    L += ['', '## كل صفحات النظام (للروابط)', ''] + ['- %s %s (%s)' % (p['id'], p['title'], p['surface']) for p in D['pages']]
    open(os.path.join(HERE, 'ctx', 'common.md'), 'w', encoding='utf8').write('\n'.join(L))
    print('ok', {g: len(open(os.path.join(HERE, 'ctx', g + '.md'), encoding='utf8').read()) for g in GROUPS})


main()
