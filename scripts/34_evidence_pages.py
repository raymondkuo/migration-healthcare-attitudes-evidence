# -*- coding: utf-8 -*-
"""For every country x variable, build an evidence page: each year's value, the source,
the exact query URL, the reference date, the quality grade and the verification result,
with links to every archived artifact behind it. Also emit a print-ready HTML that is
rendered to PDF by 35_render_extract_pdfs.py, so every number has a PDF mirror."""
import os, sys, html, json
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _sitelib import (SITE, EV, D, ACCESS, panel, vlog, reg, corr, snaps, apis,
                      VLAB, E, num, pill, filelink, page)

EVP = os.path.join(SITE, 'evidence-pages')
PRINT = os.path.join(SITE, 'evidence', 'extracts')
os.makedirs(EVP, exist_ok=True)
os.makedirs(PRINT, exist_ok=True)

pub = pd.read_csv(os.path.join(D, 'api_publisher_snapshots.csv'))
VARS = ['population', 'foreign_born', 'foreign_nationals', 'irregular_stock',
        'irregular_proxy_overstayers', 'irregular_proxy_detections',
        'irregular_proxy_absconded_workers']
CHK = {'irregular_proxy_detections': 'irregular_detections'}

snap_by = {}
for _, s in snaps.iterrows():
    snap_by.setdefault((s['iso3'], s['source_url']), []).append(s)
reg_by = {}
for _, r in reg.iterrows():
    reg_by.setdefault((r['iso3'], str(r['source_url'])), []).append(r)

# which publisher snapshot backs which source URL
def publisher_for(url):
    u = str(url)
    if 'api.worldbank.org' in u and 'SP.POP.TOTL' in u:
        return 'worldbank_SP_POP_TOTL'
    if 'api.worldbank.org' in u and 'SM.POP.TOTL' in u:
        return 'worldbank_SM_POP_TOTL'
    if 'migr_pop3ctb' in u:
        return 'eurostat_migr_pop3ctb'
    if 'migr_pop1ctz' in u:
        return 'eurostat_migr_pop1ctz'
    if 'migr_eipre' in u:
        return 'eurostat_migr_eipre'
    if 'sdmx.oecd.org' in u:
        return 'oecd_international_migration_database'
    if 'population.un.org' in u:
        return 'un_wpp_2024'
    if 'un.org/development/desa' in u:
        return 'un_desa_international_migrant_stock_2024'
    return None


RAWFILE = {
 'worldbank_SP_POP_TOTL': 'evidence/api/wb_SP_POP_TOTL.json',
 'worldbank_SM_POP_TOTL': 'evidence/api/wb_SM_POP_TOTL.json',
 'eurostat_migr_pop3ctb': 'evidence/api/eurostat_migr_pop3ctb.json',
 'eurostat_migr_pop1ctz': 'evidence/api/eurostat_migr_pop1ctz.json',
 'eurostat_migr_eipre': 'evidence/api/eurostat_migr_eipre.json',
 'un_wpp_2024': 'evidence/api/UN_WPP2024_demographic_indicators_compact.xlsx',
 'un_desa_international_migrant_stock_2024':
     'evidence/api/UN_DESA_IMS2024_stock_by_sex_and_destination.xlsx',
}
pub_by_key = {r['key']: r for _, r in pub.iterrows()}

index_rows = []

for iso3, g in panel.groupby('iso3'):
    cname = g['country'].iloc[0]
    g = g.sort_values('year')
    for v in VARS:
        if v not in g or g[v].notna().sum() == 0:
            continue
        sub = g[g[v].notna()]
        scol, ucol = v + '_source', v + '_url'
        has_src = scol in g.columns

        # ---------- gather artifacts for this country x variable ----------
        arts = []          # (label, relpath from site root)
        seen = set()

        def add(label, rel):
            """Only link an artifact that actually exists on disk."""
            if not rel or rel in seen:
                return
            if not os.path.isfile(os.path.join(SITE, rel.replace('/', os.sep))):
                return
            seen.add(rel)
            arts.append((label, rel))

        urls = sorted({str(u) for u in sub[ucol].dropna()}) if has_src and ucol in sub else []
        for u in urls:
            k = publisher_for(u)
            if k:
                pr = pub_by_key.get(k)
                if pr is not None:
                    if isinstance(pr['pdf'], str) and pr['pdf']:
                        add('Publisher page (PDF)', pr['pdf'])
                    if isinstance(pr['png'], str) and pr['png']:
                        add('Publisher page (screenshot)', pr['png'])
                if k in RAWFILE:
                    add('Raw API response', RAWFILE[k])
                if k == 'oecd_international_migration_database':
                    add('OECD dataflow definition (XML)',
                        'evidence/api/oecd/DSD_MIG_dataflow_metadata.xml')
                    for _, a in apis[apis.path.str.contains('oecd/%s_' % iso3, na=False)].iterrows():
                        add('Raw SDMX response (%s)' % os.path.basename(a['path']), a['path'])
            for r in reg_by.get((iso3, u), []):
                lf = str(r.get('local_file') or '')
                if lf and lf != 'nan':
                    ext = os.path.splitext(lf)[1].lstrip('.').upper() or 'file'
                    host = u.split('/')[2] if '://' in u else ''
                    add('Archived source document (%s, %s)' % (host, ext),
                        'evidence/countries/%s/%s' % (iso3, lf))
            for s in snap_by.get((iso3, u), []):
                if isinstance(s['pdf_mirror'], str) and s['pdf_mirror']:
                    add('PDF mirror of source page', 'evidence/countries/%s/%s' % (iso3, s['pdf_mirror']))
                if isinstance(s['png_screenshot'], str) and s['png_screenshot']:
                    add('Screenshot of source page', 'evidence/countries/%s/%s' % (iso3, s['png_screenshot']))

        # ---------- value table ----------
        cv = vlog[(vlog.iso3 == iso3) & (vlog.variable == CHK.get(v, v))]
        chk = {int(r['year']): r for _, r in cv.iterrows()}
        cc = corr[(corr.iso3 == iso3) & (corr.variable == v)]
        corrected = {int(r['year']): r for _, r in cc.iterrows()}

        rows_html, print_rows = [], []
        for _, r in sub.iterrows():
            y = int(r['year'])
            c = chk.get(y)
            if y in corrected:
                ver = ('<span class="tag ok">corrected &amp; re-derived</span>')
                verp = 'corrected from the live source'
            elif c is not None and c['status'] == 'EXACT':
                ver = '<span class="tag ok">reproduced exactly</span>'
                verp = 'reproduced exactly from the live source'
            elif str(r.get(v + '_verification') or '') not in ('', 'nan'):
                ver = '<span class="tag ok">confirmed in document</span>'
                verp = 'confirmed by reading the source document'
            else:
                ver = '<span class="tag">not machine-checkable</span>'
                verp = 'modelled estimate; not mechanically re-derivable'
            src = str(r.get(scol) or '') if has_src else 'World Bank / national source'
            ref = str(r.get(v + '_ref_date') or '') if v + '_ref_date' in r else ''
            rows_html.append(
                '<tr id="y%d"><td class="num">%d</td><td class="num"><strong>%s</strong></td>'
                '<td>%s</td><td>%s</td><td class="wrap-any">%s</td><td>%s</td></tr>'
                % (y, y, num(r[v]), pill(r.get(v + '_grade', '')), ver, E(src[:110]),
                   E(ref)))
            print_rows.append((y, r[v], str(r.get(v + '_grade') or ''), verp, src[:90], ref))

        note = ''
        for cand in sub[v + '_note'] if (v + '_note') in sub else []:
            if isinstance(cand, str) and cand.strip():
                note = cand
                break
        vnote = ''
        for cand in (sub[v + '_verification'] if (v + '_verification') in sub else []):
            if isinstance(cand, str) and cand.strip():
                vnote = cand
                break

        pdfrel = 'evidence/extracts/%s/%s.pdf' % (iso3, v)
        artlinks = ''.join(filelink('../' + rel, lab) for lab, rel in arts)

        corrhtml = ''
        if len(cc):
            rr = ''.join('<tr><td class="num">%d</td><td class="num">%s</td>'
                         '<td class="num">%s</td><td>%s</td></tr>'
                         % (int(x['year']), num(x['old_value']), num(x['new_value']), E(x['reason']))
                         for _, x in cc.iterrows())
            corrhtml = ('<h2>Corrections applied</h2><div class="tablewrap"><table><thead><tr>'
                        '<th class="num">Year</th><th class="num">Was</th><th class="num">Now</th>'
                        '<th>Why</th></tr></thead><tbody>' + rr + '</tbody></table></div>')

        body = (
         '<div class="hero"><div class="wrap">\n'
         '  <p class="eyebrow">' + iso3 + ' &middot; evidence for one variable</p>\n'
         '  <h1>' + E(cname) + ' &mdash; ' + E(VLAB.get(v, v)) + '</h1>\n'
         '  <p class="lede">Every value behind this series, what it was checked against, and every '
         'file held in this archive that supports it. Retrieved ' + ACCESS + '.</p>\n'
         '</div></div>\n\n'
         '<section><div class="wrap">\n  <h2>Values</h2>\n'
         '  <div class="tablewrap"><table><thead><tr><th class="num">Year</th>'
         '<th class="num">Value</th><th>Grade</th><th>Verification</th><th>Source</th>'
         '<th>Reference date</th></tr></thead><tbody>' + ''.join(rows_html) + '</tbody></table></div>\n'
         + ('  <div class="note"><strong>Definition note.</strong> ' + E(note) + '</div>\n' if note else '')
         + ('  <div class="note"><strong>How this was confirmed.</strong> ' + E(vnote) + '</div>\n' if vnote else '')
         + '</div></section>\n\n'
         '<section><div class="wrap">\n  <h2>Source</h2>\n'
         '  <p class="sub">The query or document URL this series was taken from.</p>\n'
         '  <ul class="clean">' +
         ''.join('<li><a href="%s" rel="nofollow noopener" style="word-break:break-all">%s</a></li>'
                 % (E(u), E(u)) for u in urls) +
         '</ul>\n</div></section>\n\n'
         + ('<section><div class="wrap">' + corrhtml + '</div></section>\n\n' if corrhtml else '')
         + '<section><div class="wrap">\n  <h2>Archived evidence for these numbers</h2>\n'
         '  <p class="sub">Every file below is stored in this archive and downloads from this '
         'site &mdash; no external server is involved.</p>\n  <p>'
         + filelink('../' + pdfrel, 'PDF extract of this table')
         + artlinks + '</p>\n'
         '  <p style="margin-top:10px">'
         + filelink('../evidence/countries/%s/data_from_source.csv' % iso3, 'country data (CSV)')
         + filelink('../evidence/countries/%s/value_check.csv' % iso3, 'value check (CSV)')
         + '</p>\n</div></section>\n\n'
         '<section><div class="wrap">\n  <p><a href="../countries/' + iso3 + '.html">&larr; back to '
         + E(cname) + '</a></p>\n</div></section>\n')

        page('evidence-pages/%s__%s.html' % (iso3, v),
             '%s — %s — evidence' % (cname, VLAB.get(v, v)), body, up='../',
             desc='Every value, source and archived file for %s %s, 2010-2022.'
                  % (cname, VLAB.get(v, v)))

        # ---------- print-ready HTML for the PDF extract ----------
        os.makedirs(os.path.join(PRINT, iso3), exist_ok=True)
        trs = ''.join(
            '<tr><td class="n">%d</td><td class="n"><b>%s</b></td><td>%s</td><td>%s</td>'
            '<td>%s</td><td>%s</td></tr>'
            % (y, ('{:,.0f}'.format(val) if pd.notna(val) else '—'), gr or '—',
               html.escape(vp), html.escape(str(sr)), html.escape(str(rf)))
            for y, val, gr, vp, sr, rf in print_rows)
        arts_p = ''.join('<li><code>%s</code></li>' % html.escape(rel) for _, rel in arts)
        pdoc = ("""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>EXTRACT</title><style>
 @page{margin:15mm}
 body{font:11.8px/1.5 -apple-system,"Segoe UI",Roboto,"Noto Sans TC",sans-serif;color:#1a1a18;margin:0}
 h1{font-size:17px;margin:0 0 3px;letter-spacing:-.01em}
 .sub{color:#5f5f5a;margin:0 0 14px;font-size:11.6px}
 h2{font-size:12.8px;margin:18px 0 6px}
 table{border-collapse:collapse;width:100%;font-size:11px}
 th,td{border:1px solid #dcdcd6;padding:4px 7px;text-align:left;vertical-align:top}
 th{background:#eef2f7;font-weight:600}
 td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}
 code{font-family:Consolas,monospace;font-size:10.2px}
 .box{border-left:3px solid #3d5a80;background:#eef2f7;padding:8px 12px;margin:12px 0;font-size:11px}
 ul{margin:6px 0;padding-left:18px} li{margin:2px 0}
 .foot{margin-top:22px;border-top:1px solid #dcdcd6;padding-top:8px;color:#6a6a64;font-size:10px}
</style></head><body>
<h1>TITLE</h1>
<p class="sub">Data extract and provenance sheet &middot; retrieved ACCESSDATE &middot;
Migration and Population Data Archive</p>
<h2>Values</h2>
<table><thead><tr><th class="n">Year</th><th class="n">Value</th><th>Grade</th>
<th>Verification</th><th>Source</th><th>Reference date</th></tr></thead><tbody>TRS</tbody></table>
NOTEBOX
<h2>Source URL(s)</h2><ul>URLS</ul>
<h2>Archived evidence files</h2><ul>ARTS</ul>
<p class="foot">Grades: A re-derived from a machine-readable official source and matched exactly, or
corrected against one during verification &middot; B confirmed by reading the retrieved source
document &middot; C source document retrieved but the value is a modelled estimate &middot;
D cited source could not be retrieved.<br>
Joint work of Prof. Raymond Kuo, National Taiwan University, and Claude (Anthropic).</p>
</body></html>""")
        notebox = ''
        if note:
            notebox += '<div class="box"><b>Definition note.</b> %s</div>' % html.escape(note)
        if vnote:
            notebox += '<div class="box"><b>How this was confirmed.</b> %s</div>' % html.escape(vnote)
        pdoc = (pdoc.replace('EXTRACT', '%s %s extract' % (iso3, v))
                    .replace('TITLE', html.escape('%s — %s' % (cname, VLAB.get(v, v))))
                    .replace('ACCESSDATE', ACCESS).replace('TRS', trs)
                    .replace('NOTEBOX', notebox)
                    .replace('URLS', ''.join('<li><code>%s</code></li>' % html.escape(u) for u in urls) or '<li>—</li>')
                    .replace('ARTS', arts_p or '<li>—</li>'))
        open(os.path.join(PRINT, iso3, v + '.src.html'), 'w', encoding='utf-8').write(pdoc)

        index_rows.append(dict(iso3=iso3, country=cname, variable=v, n_values=int(len(sub)),
                               years='%d-%d' % (sub.year.min(), sub.year.max()),
                               evidence_page='evidence-pages/%s__%s.html' % (iso3, v),
                               pdf_extract=pdfrel, artifacts=len(arts)))

idx = pd.DataFrame(index_rows)
idx.to_csv(os.path.join(D, 'evidence_index.csv'), index=False, encoding='utf-8-sig')
print('evidence pages: %d' % len(idx))
print('print-ready extracts queued: %d' % len(idx))
print(idx.groupby('variable').agg(pages=('iso3', 'size'), artifacts=('artifacts', 'mean')).round(1).to_string())
