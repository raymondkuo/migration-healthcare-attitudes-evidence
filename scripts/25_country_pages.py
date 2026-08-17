# -*- coding: utf-8 -*-
"""Generate one archive page per country."""
import os, sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _sitelib import (SITE, EV, ACCESS, panel, qual, corr, vlog, reg, apis, snaps,
                      VARS, VLAB, E, num, pill, filelink, page, table)

snap_by = {}
for _, s in snaps.iterrows():
    snap_by.setdefault((s['iso3'], s['source_url']), []).append(s)

cinfo = panel.groupby(['iso3', 'country']).size().reset_index()[['iso3', 'country']]

for _, ci in cinfo.iterrows():
    iso, cname = ci['iso3'], ci['country']
    g = panel[panel.iso3 == iso].sort_values('year')
    cq = qual[qual.iso3 == iso]
    cv = vlog[vlog.iso3 == iso]
    cr = reg[reg.iso3 == iso]
    cc = corr[corr.iso3 == iso]
    evdir = os.path.join(EV, iso)
    evfiles = sorted(os.listdir(evdir)) if os.path.isdir(evdir) else []

    # ---------------- data table (every value links to its evidence page)
    extra = ['irregular_proxy_absconded_workers'] if g['irregular_proxy_absconded_workers'].notna().any() else []
    show = VARS + extra
    head = '<th class="num">Year</th>' + ''.join('<th class="num">%s</th>' % VLAB.get(v, v) for v in show)
    rows = []
    for _, r in g.iterrows():
        cells = ['<td class="num">%d</td>' % int(r['year'])]
        for v in show:
            val = r[v]
            if pd.isna(val):
                cells.append('<td class="num">%s</td>' % num(val))
                continue
            href = '../evidence-pages/%s__%s.html#y%d' % (iso, v, int(r['year']))
            tip = 'Evidence for %s %s %d — sources, snapshots and PDF mirrors' % (
                cname, VLAB.get(v, v), int(r['year']))
            cells.append(
                '<td class="num"><a class="cell" href="%s" title="%s">%s</a>'
                '<a class="cellg" href="%s" title="%s">%s</a></td>'
                % (href, E(tip), num(val), href, E(tip), pill(r.get(v + '_grade', ''))))
        rows.append('<tr>' + ''.join(cells) + '</tr>')
    dtable = ('<div class="tablewrap"><table><thead><tr>' + head + '</tr></thead><tbody>'
              + ''.join(rows) + '</tbody></table></div>')

    # ---------------- verification
    nchk, nex = len(cv), int((cv.status == 'EXACT').sum())
    if nchk:
        vsum = ('<p class="sub"><strong>%d of %d</strong> machine-checkable values for %s '
                'reproduced the live source exactly.</p>' % (nex, nchk, E(cname)))
    else:
        vsum = '<p class="sub">No machine-readable bulk source applies to this country.</p>'
    disc = cv[cv.status != 'EXACT']
    if len(disc):
        vsum += ('<div class="note bad"><strong>%d discrepancies were found in the input '
                 'workbook and corrected.</strong> Input value against the live source:</div>'
                 % len(disc))
        dv = disc.sort_values(['variable', 'year']).copy()
        dv['year'] = dv['year'].astype(int).astype(str)
        dv['variable'] = dv['variable'].map(lambda v: VLAB.get(v, v))
        vsum += table(dv,
                      ['year', 'variable', 'workbook_value', 'live_source_value', 'diff', 'source'],
                      ['Year', 'Variable', 'Input workbook', 'Live source', 'Difference', 'Source'],
                      numcols=('workbook_value', 'live_source_value', 'diff'))

    csec = ''
    if len(cc):
        cc2 = cc.copy()
        cc2['what'] = [('%s %d' % (VLAB.get(v, v), int(y))) for v, y in zip(cc2['variable'], cc2['year'])]
        csec = ('<h3>Corrections applied</h3>'
                + table(cc2, ['what', 'old_value', 'new_value', 'reason'],
                        ['Value', 'Was', 'Now', 'Why'], numcols=('old_value', 'new_value')))

    # ---------------- sources
    srows = []
    for _, r in cr.drop_duplicates(subset=['source_url', 'variable']).iterrows():
        url = str(r['source_url'])
        links = []
        lf = str(r.get('local_file') or '')
        if r['retrieval'] == 'VERIFIED_API':
            base = url.split('?')[0]
            hit = apis[apis.query_url.astype(str).str.split('?').str[0] == base]
            for _, a in hit.iterrows():
                links.append(filelink('../' + a['path'], 'raw API response'))
            if not links:
                links.append('<span class="tag ok">bulk API snapshot &mdash; see Sources page</span>')
        else:
            if lf and lf != 'nan':
                links.append(filelink('../evidence/countries/%s/%s' % (iso, lf), 'archived copy'))
            for s in snap_by.get((iso, url), []):
                if isinstance(s['pdf_mirror'], str) and s['pdf_mirror']:
                    links.append(filelink('../evidence/countries/%s/%s' % (iso, s['pdf_mirror']), 'PDF mirror'))
                if isinstance(s['png_screenshot'], str) and s['png_screenshot']:
                    links.append(filelink('../evidence/countries/%s/%s' % (iso, s['png_screenshot']), 'screenshot'))
        if not links:
            links.append('<span class="tag bad">source not retrievable</span>')
        srows.append(
            '<tr><td>%s</td><td class="num">%s</td>'
            '<td class="wrap-any">%s<br><a href="%s" rel="nofollow noopener" '
            'style="font-size:11.5px;word-break:break-all;color:var(--muted)">%s</a></td>'
            '<td>%s</td></tr>'
            % (E(VLAB.get(r['variable'], r['variable'])), E(r['years']),
               E(str(r['source_name'])[:150]), E(url), E(url[:100]), ''.join(links)))
    stable = ('<div class="tablewrap"><table><thead><tr><th>Variable</th><th class="num">Years</th>'
              '<th>Source</th><th>Archived here</th></tr></thead><tbody>'
              + ''.join(srows) + '</tbody></table></div>')

    # ---------------- quality
    qrows = []
    for _, r in cq.iterrows():
        if r['n_years'] == 0:
            continue
        qrows.append('<tr><td>%s</td><td class="num">%s</td><td class="num">%s</td>'
                     '<td>%s</td><td>%s</td></tr>'
                     % (E(VLAB.get(r['variable'], r['variable'])), E(r['coverage']),
                        E(r['years']), pill(r['modal_grade']), E(r['usable_for_trend'])))
    qtable = ('<div class="tablewrap"><table><thead><tr><th>Variable</th>'
              '<th class="num">Coverage</th><th class="num">Years</th><th>Grade</th>'
              '<th>Usable as a trend?</th></tr></thead><tbody>'
              + ''.join(qrows) + '</tbody></table></div>')

    flinks = ''.join(filelink('../evidence/countries/%s/%s' % (iso, f), f) for f in evfiles)

    body = (
        '<div class="hero"><div class="wrap">\n'
        '  <p class="eyebrow">' + iso + ' &middot; country archive</p>\n'
        '  <h1>' + E(cname) + '</h1>\n'
        '  <p class="lede">Data, verification result and every archived source document for '
        + E(cname) + ', 2010&ndash;2022. All sources retrieved ' + ACCESS + '.</p>\n'
        '</div></div>\n\n'
        '<section><div class="wrap">\n  <h2>Panel data</h2>\n'
        '  <p class="sub"><strong>Every number below is a link.</strong> Click a value, or the '
        'grade pill beside it, to open the evidence for that exact figure &mdash; the source, the '
        'query URL, what it was checked against, and the snapshots, PDF mirrors and files held in '
        'this archive that support it. Grades: ' + pill('A') + ' verified against a '
        'machine-readable official source, ' + pill('B') + ' confirmed in the source document, '
        + pill('C') + ' modelled estimate, ' + pill('D') + ' source unretrievable.</p>\n  '
        + dtable + '\n'
        '  <p style="margin-top:12px">'
        + filelink('../evidence/countries/%s/data_from_source.csv' % iso, 'this country as CSV')
        + filelink('../evidence/countries/%s/value_check.csv' % iso, 'value-by-value check')
        + filelink('../evidence/countries/%s/source_manifest.csv' % iso, 'source manifest')
        + filelink('../evidence/countries/%s/README.md' % iso, 'country README')
        + '</p>\n</div></section>\n\n'
        '<section><div class="wrap">\n  <h2>Verification</h2>\n  ' + vsum + csec + '\n</div></section>\n\n'
        '<section><div class="wrap">\n  <h2>Data quality by variable</h2>\n'
        '  <p class="sub">Coverage, and whether this series can carry a trend for this country.</p>\n  '
        + qtable + '\n</div></section>\n\n'
        '<section><div class="wrap">\n  <h2>Sources</h2>\n'
        '  <p class="sub">Each row links to the original URL and to the copy held in this archive. '
        'API sources link to the raw response captured on ' + ACCESS + '.</p>\n  '
        + stable + '\n</div></section>\n\n'
        '<section><div class="wrap">\n  <h2>All archived files</h2>\n'
        '  <p class="sub">' + str(len(evfiles)) + ' files in '
        '<code>evidence/countries/' + iso + '/</code>.</p>\n  <p>'
        + (flinks or '<span class="tag">No country-specific documents &mdash; every source for '
                     'this country is a bulk statistical API, archived under evidence/api/.</span>')
        + '</p>\n</div></section>\n')

    page('countries/%s.html' % iso, '%s — Migration Data Archive' % cname, body, up='../',
         desc='Data, verification and archived sources for %s, 2010-2022.' % cname)

print('wrote %d country pages' % len(cinfo))
