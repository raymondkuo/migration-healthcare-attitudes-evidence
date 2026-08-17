# -*- coding: utf-8 -*-
"""Generate the sources, data-files, verification and methods pages."""
import os, sys, json
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _sitelib import (SITE, EV, D, ACCESS, panel, qual, corr, issues, vlog, reg, codeb,
                      apis, snaps, irrall, VARS, VLAB, E, num, pill, filelink, page, table)

snap_by = {}
for _, s in snaps.iterrows():
    snap_by.setdefault((s['iso3'], s['source_url']), []).append(s)

# =====================================================================  SOURCES
api_rows = []
for _, a in apis.iterrows():
    api_rows.append(
        '<tr><td>%s</td><td class="wrap-any">%s</td>'
        '<td class="wrap-any"><a href="%s" rel="nofollow noopener" '
        'style="font-size:11.5px;word-break:break-all;color:var(--muted)">%s</a></td>'
        '<td class="num">%s</td><td>%s</td></tr>'
        % (E(a['publisher']), E(a['description']), E(a['query_url']),
           E(str(a['query_url'])[:95]), num(a['bytes']),
           filelink(a['path'], os.path.basename(str(a['path'])))))
api_table = ('<div class="tablewrap"><table><thead><tr><th>Publisher</th><th>Dataset</th>'
             '<th>Query URL used</th><th class="num">Bytes</th><th>Raw snapshot</th>'
             '</tr></thead><tbody>' + ''.join(api_rows) + '</tbody></table></div>')

# ---- publisher-page mirrors for the bulk sources ----
pubs = pd.read_csv(os.path.join(D, 'api_publisher_snapshots.csv'))
prows = []
for _, r in pubs.iterrows():
    links = ''
    if isinstance(r['pdf'], str) and r['pdf']:
        links += filelink(r['pdf'], 'PDF mirror')
    if isinstance(r['png'], str) and r['png']:
        links += filelink(r['png'], 'screenshot')
    note = str(r.get('note') or '')
    extra = ('<br><span style="color:var(--muted);font-size:11.5px">%s</span>' % E(note[:230])) \
        if note and note != 'nan' else ''
    prows.append('<tr><td>%s</td><td class="wrap-any">%s%s</td>'
                 '<td class="wrap-any"><a href="%s" rel="nofollow noopener" '
                 'style="font-size:11.5px;word-break:break-all;color:var(--muted)">%s</a></td>'
                 '<td>%s</td></tr>'
                 % (E(r['publisher']), E(r['dataset']), extra, E(r['page_url']),
                    E(str(r['page_url'])[:95]), links or '<span class="tag bad">not captured</span>'))
pub_table = ('<div class="tablewrap"><table><thead><tr><th>Publisher</th><th>Dataset page</th>'
             '<th>URL</th><th>Archived mirror</th></tr></thead><tbody>'
             + ''.join(prows) + '</tbody></table></div>')

nonapi = reg[reg.retrieval != 'VERIFIED_API']
docs = nonapi.drop_duplicates(subset=['iso3', 'source_url'])
TAG = {'DOWNLOADED': ('ok', 'archived'), 'RECOVERED': ('ok', 'recovered'),
       'RECOVERED_SCREENSHOT': ('ok', 'screenshot'), 'SUBSTITUTED': ('warn', 'substituted'),
       'NOT_RETRIEVED': ('bad', 'not retrievable'),
       'NOT_RETRIEVED_REDUNDANT': ('bad', 'not retrievable')}
drows = []
for _, r in docs.sort_values(['iso3', 'variable']).iterrows():
    iso, url = r['iso3'], str(r['source_url'])
    links = []
    lf = str(r.get('local_file') or '')
    if lf and lf != 'nan':
        links.append(filelink('evidence/countries/%s/%s' % (iso, lf), 'file'))
    for s in snap_by.get((iso, url), []):
        if isinstance(s['pdf_mirror'], str) and s['pdf_mirror']:
            links.append(filelink('evidence/countries/%s/%s' % (iso, s['pdf_mirror']), 'PDF'))
        if isinstance(s['png_screenshot'], str) and s['png_screenshot']:
            links.append(filelink('evidence/countries/%s/%s' % (iso, s['png_screenshot']), 'PNG'))
    cls, lab = TAG.get(str(r.get('outcome', '')), ('', 'archived' if links else 'check'))
    note = str(r.get('note') or '')
    status = '<span class="tag %s">%s</span>' % (cls, lab)
    if note and note != 'nan':
        status += ('<br><span style="color:var(--muted);font-size:11.5px">%s</span>'
                   % E(note[:190]))
    drows.append(
        '<tr data-t="%s"><td><a href="countries/%s.html">%s</a></td>'
        '<td>%s</td><td class="wrap-any">%s<br>'
        '<a href="%s" rel="nofollow noopener" style="font-size:11.5px;word-break:break-all;'
        'color:var(--muted)">%s</a></td><td class="wrap-any">%s</td><td>%s</td></tr>'
        % (E((str(iso) + ' ' + str(r['source_name']) + ' ' + url + ' ' + str(r['variable'])).lower()),
           iso, iso, E(VLAB.get(r['variable'], r['variable'])),
           E(str(r['source_name'])[:130]), E(url), E(url[:95]), status,
           ''.join(links) or '<span style="color:var(--faint)">&mdash;</span>'))

n_arch = int((~docs.outcome.astype(str).str.startswith('NOT_RETRIEVED')).sum())
n_urls = int(nonapi.source_url.nunique())
n_pairs = int(len(nonapi))

body = (
 '<div class="hero"><div class="wrap">\n'
 '  <p class="eyebrow">Source register</p>\n  <h1>Every source, and its archived copy</h1>\n'
 '  <p class="lede">Two kinds of source feed this dataset. Bulk statistical APIs were captured as '
 'raw response payloads. Individual documents and web pages were downloaded, and where the source '
 'is a web page it was additionally rendered to PDF and to a full-page screenshot. Everything was '
 'captured on ' + ACCESS + '.</p>\n</div></div>\n\n'
 '<section><div class="wrap">\n  <h2>Bulk statistical sources (API snapshots)</h2>\n'
 '  <p class="sub">These ' + str(len(apis)) + ' payloads are the evidence behind '
 + format(int((vlog.status == 'EXACT').sum()), ',') + ' of the ' + format(len(vlog), ',')
 + ' verified values. Each file is exactly what the publisher’s server returned; the query '
 'URL that produced it is given so the request can be repeated.</p>\n  ' + api_table + '\n'
 '  <p style="margin-top:12px">' + filelink('data/api_snapshots.csv', 'api_snapshots.csv')
 + '</p>\n</div></section>\n\n'
 '<section><div class="wrap">\n  <h2>Publisher pages for the bulk sources</h2>\n'
 '  <p class="sub">A raw JSON payload is precise but not readable. So the publishers’ own dataset '
 'pages &mdash; the human-facing definition of each series &mdash; were also mirrored as PDF and '
 'screenshot on ' + ACCESS + ', giving the bulk API sources the same kind of visual evidence the '
 'document sources have.</p>\n  ' + pub_table + '\n'
 '  <p style="margin-top:12px">'
 + filelink('data/api_publisher_snapshots.csv', 'api_publisher_snapshots.csv') + '</p>\n'
 '</div></section>\n\n'
 '<section><div class="wrap">\n  <h2>Per-variable evidence pages</h2>\n'
 '  <p class="sub">Beyond the source-level mirrors, every country&times;variable series has its own '
 'evidence page and a PDF extract listing each year’s value, its grade, what it was checked '
 'against and every archived file behind it. These are reached by clicking any number in a '
 'country’s Panel data table.</p>\n'
 '  <p>' + filelink('data/evidence_index.csv', 'evidence_index.csv')
 + ' &nbsp;<span class="count">156 evidence pages · 156 PDF extracts</span></p>\n'
 '</div></section>\n\n'
 '<section><div class="wrap">\n  <h2>Document and web-page sources</h2>\n'
 '  <p class="sub">Beyond the bulk APIs, the two workbooks cite <strong>' + str(len(docs))
 + ' distinct country–source citations</strong> across ' + str(n_urls) + ' URLs. <strong>'
 + str(n_arch) + ' of ' + str(len(docs)) + '</strong> are held in this archive; the 2 that are '
 'not are named below. Use the filter to find a country, a publisher or a URL.</p>\n'
 '  <div class="toolbar">\n'
 '    <input type="search" id="q" placeholder="Filter by country, source or URL…" '
 'aria-label="Filter sources">\n    <span class="count" id="n"></span>\n  </div>\n'
 '  <div class="tablewrap"><table id="tbl"><thead><tr><th>Country</th><th>Variable</th>'
 '<th>Source</th><th>Status</th><th>Archived copies</th></tr></thead><tbody>'
 + ''.join(drows) + '</tbody></table></div>\n'
 '  <p style="margin-top:12px">' + filelink('data/source_register.csv', 'source_register.csv')
 + filelink('data/web_snapshots.csv', 'web_snapshots.csv')
 + filelink('verification/download_log.csv', 'download_log.csv') + '</p>\n</div></section>\n\n'
 '<section><div class="wrap">\n  <h2>Sources that could not be archived</h2>\n'
 '  <div class="note warn"><strong>Two of the ' + str(len(docs)) + ' country–source citations '
 'could not be retrieved by any means.</strong><br>\n'
 '  <em>press.police.ac.kr</em> — the Korean National Police University publication behind '
 'Korea’s 2010–2015 overstayer figures. The host does not respond and no web archive '
 'copy was available. Those six values are graded D.<br>\n'
 '  <em>nisshinkyo.org</em> — a mirror of a Japanese Immigration Services Agency table, now '
 '404. No impact: it duplicated a figure whose primary ISA source was retrieved successfully.</div>\n'
 '  <p>Three further sources block automated and browser access entirely (<em>ismu.org</em>) or '
 'have moved (<em>sem.admin.ch</em>). In each case an equivalent or better source was located and '
 'archived instead, and it confirmed the values. See '
 '<a href="verification.html">Verification</a>.</p>\n</div></section>\n\n'
 '<script>\n(function(){\n'
 "  var q=document.getElementById('q'),n=document.getElementById('n'),\n"
 "      rows=[].slice.call(document.querySelectorAll('#tbl tbody tr'));\n"
 "  function upd(){var t=q.value.trim().toLowerCase(),c=0;\n"
 "    rows.forEach(function(r){var m=!t||r.getAttribute('data-t').indexOf(t)>=0;\n"
 "      r.style.display=m?'':'none'; if(m)c++;});\n"
 "    n.textContent=c+' of '+rows.length+' sources';}\n"
 "  q.addEventListener('input',upd); upd();\n})();\n</script>\n")
page('sources.html', 'Source register — Migration Data Archive', body,
     desc='Every data source with its archived copy: API snapshots, PDF mirrors and screenshots.')
print('sources.html')

# =====================================================================  DATA FILES
def sizeof(rel):
    p = os.path.join(SITE, rel)
    return os.path.getsize(p) if os.path.exists(p) else 0


MAIN = [
    ('data/FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx',
     'The verified panel, all sheets', 'Excel workbook. README, Panel_final, Data_quality, '
     'Corrections_applied, Known_issues, Verification_log, Source_register, '
     'Irregular_estimates_all, Codebook.'),
    ('data/panel_final.csv', 'Panel_final as CSV',
     '520 rows, one per country-year, with source, URL, reference date and quality grade on '
     'every value.'),
    ('data/codebook.csv', 'Codebook', 'Variable definitions and cautions.'),
    ('data/data_quality.csv', 'Data quality by country and variable',
     'Coverage, modal grade, sources and whether each series can carry a trend.'),
    ('data/corrections_applied.csv', 'Corrections applied',
     'Every value changed from the input workbooks, with reason and evidence.'),
    ('data/known_issues.csv', 'Known issues', 'Resolved and unresolved, with severity.'),
    ('data/verification_log.csv', 'Verification log',
     'All %s value-by-value comparisons against live sources.' % format(len(vlog), ',')),
    ('data/source_register.csv', 'Source register', 'Every cited source and how it was retrieved.'),
    ('data/irregular_estimates_all.csv', 'All competing irregular-migration estimates',
     'Every published estimate side by side, so alternatives are visible rather than hidden.'),
    ('data/api_snapshots.csv', 'API snapshot index', 'Each raw payload with the query URL that produced it.'),
    ('data/web_snapshots.csv', 'Web snapshot index', 'Each page with its PDF mirror and screenshot.'),
    ('manifest/checksums.csv', 'SHA-256 checksums', 'Integrity hash for every file in this archive.'),
]
ORIG = [
    ('data/original_inputs/immigration_country_year_2010_2022.xlsx',
     'Input workbook 1 (unmodified)', 'Kept for provenance. Not used as the base for the final panel.'),
    ('data/original_inputs/migration_population_panel_40countries_2010-2022.xlsx',
     'Input workbook 2 (unmodified)', 'Kept for provenance. The final panel is built from this file.'),
]


def flist(items):
    out = []
    for rel, name, desc in items:
        out.append('<tr><td><strong>%s</strong><br><span style="color:var(--muted);'
                   'font-size:13px">%s</span></td><td class="num">%s KB</td><td>%s</td></tr>'
                   % (E(name), E(desc), format(sizeof(rel) // 1024, ','),
                      filelink(rel, os.path.basename(rel))))
    return ('<div class="tablewrap"><table><thead><tr><th>File</th><th class="num">Size</th>'
            '<th>Download</th></tr></thead><tbody>' + ''.join(out) + '</tbody></table></div>')


cb = table(codeb, list(codeb.columns), list(codeb.columns))
ALT = [
    ('data/migration_population_panel_40countries_2010-2022_final.xlsx',
     'Independently produced summary workbook',
     'Extends the original input workbook with Final Summary, Verification, Source Audit and '
     'Folder Index sheets. Produced by a separate compilation run: its internal counts and file '
     'paths describe that run, not this archive. Read the note below before citing it.'),
    ('data/ABOUT_THE_TWO_WORKBOOKS.md', 'Note: how the two workbooks differ',
     'Which workbook this website documents, and where the other one diverges.'),
]

body = (
 '<div class="hero"><div class="wrap">\n  <p class="eyebrow">Downloads</p>\n'
 '  <h1>Data files</h1>\n'
 '  <p class="lede">The dataset and every supporting table, as Excel and CSV. All files are UTF-8 '
 'with a BOM so they open cleanly in Excel, including the Chinese, Japanese, Korean and Hebrew '
 'source names.</p>\n</div></div>\n\n'
 '<section><div class="wrap">\n  <h2>The dataset</h2>\n'
 '  <p class="sub">Everything on this website — every count, grade and correction — refers to '
 '<strong>FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx</strong>. It is the only '
 'workbook whose every value can be traced to a source file held in this archive.</p>\n'
 + flist(MAIN) + '\n</div></section>\n\n'
 '<section><div class="wrap">\n  <h2>A second workbook, included for completeness</h2>\n'
 '  <div class="note warn"><strong>This file is not the one the website documents.</strong> It '
 'was produced by a separate compilation run. Its <em>Verification</em> sheet reports 203 source '
 'rows, 192 of 203 snapshots and 750 of 750 values matched; the figures for this archive are 72 '
 'distinct document-source URLs, 76 of 78 country-source citations archived and 2,454 '
 'values checked. Its '
 '<em>Source Audit</em> and <em>Folder Index</em> sheets also point at a folder layout '
 '(<code>country_sources\\…</code>) that does not exist in this repository. Its substantive '
 'conclusions agree with this archive’s; its counts are not interchangeable with them.</div>\n'
 + flist(ALT) + '\n</div></section>\n\n'
 '<section><div class="wrap">\n  <h2>Original inputs, unmodified</h2>\n'
 '  <p class="sub">The two workbooks this archive started from, kept exactly as supplied so that '
 'every correction can be checked against the original.</p>\n' + flist(ORIG) + '\n</div></section>\n\n'
 '<section><div class="wrap">\n  <h2>Per-country files</h2>\n'
 '  <p class="sub">Each country folder carries the same four files. Browse them from any '
 '<a href="countries.html">country page</a>, or reach them directly at '
 '<code>evidence/countries/&lt;ISO3&gt;/</code>.</p>\n'
 '  <ul class="clean">\n'
 '   <li><code>data_from_source.csv</code> &mdash; every observation for that country with its '
 'live-source check result</li>\n'
 '   <li><code>value_check.csv</code> &mdash; input workbook value against the live source value</li>\n'
 '   <li><code>source_manifest.csv</code> &mdash; every cited source and how it was retrieved</li>\n'
 '   <li><code>README.md</code> &mdash; what was verified, and any discrepancy found</li>\n'
 '  </ul>\n</div></section>\n\n'
 '<section><div class="wrap">\n  <h2>Codebook</h2>\n  ' + cb + '\n</div></section>\n')
page('data.html', 'Data files — Migration Data Archive', body,
     desc='Download the verified panel, codebook, verification log and all supporting tables.')
print('data.html')

# =====================================================================  VERIFICATION
by_src = vlog.groupby('source').agg(n=('status', 'size'),
                                    exact=('status', lambda s: int((s == 'EXACT').sum()))).reset_index()
by_src['rate'] = (by_src.exact / by_src.n * 100).round(1)
by_src = by_src.sort_values('n', ascending=False)
srows = ''.join(
    '<tr><td>%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s%%</td></tr>'
    % (E(r['source']), num(r['n']), num(r['exact']), format(r['rate'], '.1f'))
    for _, r in by_src.iterrows())
srctab = ('<div class="tablewrap"><table><thead><tr><th>Source</th><th class="num">Values checked</th>'
          '<th class="num">Exact</th><th class="num">Rate</th></tr></thead><tbody>'
          + srows + '</tbody></table></div>')

sev_order = {'RESOLVED': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'INFO': 4}
iss = issues.copy()
iss['o'] = iss.severity.map(lambda s: sev_order.get(s, 9))
iss = iss.sort_values('o')
irows = []
for _, r in iss.iterrows():
    cls = {'RESOLVED': 'ok', 'HIGH': 'bad', 'MEDIUM': 'warn'}.get(r['severity'], '')
    irows.append('<tr><td><span class="tag %s">%s</span></td><td>%s<br>'
                 '<span style="color:var(--muted);font-size:12.5px">%s</span></td>'
                 '<td class="wrap-any">%s</td><td class="wrap-any" style="color:var(--muted)">%s</td>'
                 '<td class="wrap-any">%s</td></tr>'
                 % (cls, E(r['severity']), E(r['scope']), E(r['variable']),
                    E(r['issue']), E(r['evidence']), E(r['action'])))
isstab = ('<div class="tablewrap"><table><thead><tr><th>Severity</th><th>Scope</th><th>Issue</th>'
          '<th>Evidence</th><th>Action taken</th></tr></thead><tbody>'
          + ''.join(irows) + '</tbody></table></div>')

cr = corr.copy()
cr['what'] = [('%s %d' % (VLAB.get(v, v), int(y))) for v, y in zip(cr['variable'], cr['year'])]
ctab = table(cr, ['iso3', 'what', 'old_value', 'new_value', 'reason'],
             ['Country', 'Value', 'Was', 'Now', 'Why'],
             numcols=('old_value', 'new_value'))

body = (
 '<div class="hero"><div class="wrap">\n  <p class="eyebrow">Verification record</p>\n'
 '  <h1>What was checked, and what changed</h1>\n'
 '  <p class="lede">Every source was retrieved again on ' + ACCESS + ' and each value in the input '
 'workbooks was compared against it. This page reports the result in full, including the values '
 'that did not match.</p>\n</div></div>\n\n'
 '<section><div class="wrap">\n  <div class="stats">\n'
 '    <div class="stat"><span class="n">' + format(len(vlog), ',') + '</span>'
 '<span class="l">values re-derived from live sources</span></div>\n'
 '    <div class="stat"><span class="n">' + format(int((vlog.status == 'EXACT').sum()), ',')
 + '</span><span class="l">matched exactly</span></div>\n'
 '    <div class="stat"><span class="n">' + str(int((vlog.status != 'EXACT').sum()))
 + '</span><span class="l">discrepancies</span></div>\n'
 '    <div class="stat"><span class="n">' + str(len(corr)) + '</span>'
 '<span class="l">values corrected</span></div>\n  </div>\n</div></section>\n\n'
 '<section><div class="wrap">\n  <h2>Reproduction rate by source</h2>\n'
 '  <p class="sub">Every discrepancy fell in one place: the Eurostat detections series for three '
 'countries in one of the two input workbooks.</p>\n  ' + srctab + '\n'
 '  <p style="margin-top:12px">' + filelink('data/verification_log.csv', 'full verification log (CSV)')
 + '</p>\n</div></section>\n\n'
 '<section><div class="wrap">\n  <h2>Corrections applied</h2>\n'
 '  <p class="sub">' + str(len(corr)) + ' values across ' + str(corr.iso3.nunique())
 + ' countries. The original workbooks are kept unmodified on the '
 '<a href="data.html">Data files</a> page so every change can be checked.</p>\n  ' + ctab + '\n'
 '</div></section>\n\n'
 '<section><div class="wrap">\n  <h2>Issues found</h2>\n'
 '  <p class="sub">Resolved issues first, then those that remain and must be carried into any '
 'analysis.</p>\n  ' + isstab + '\n</div></section>\n\n'
 '<section><div class="wrap">\n  <h2>What held up</h2>\n'
 '  <p class="sub">Worth stating as plainly as the problems.</p>\n'
 '  <ul class="clean">\n'
 '   <li>All 520 UN WPP 2024 population values reproduced exactly.</li>\n'
 '   <li>All 507 World Bank population values reproduced exactly.</li>\n'
 '   <li>All 584 Eurostat foreign-born and foreign-national values reproduced exactly.</li>\n'
 '   <li>All 139 OECD International Migration Database values reproduced exactly.</li>\n'
 '   <li>All 274 Eurostat detections in input workbook 1 reproduced exactly &mdash; including the '
 'three countries workbook 2 had wrong.</li>\n'
 '   <li>Workbook 2’s Panel sheet is perfectly consistent with its own audit trail: 1,690 '
 'values, zero mismatches, and every percentage column recomputes to floating-point precision.</li>\n'
 '   <li>Korea 2021 and 2022 verified against the live Ministry of Justice table: '
 '125,022 + 262,251 + 1,427 = <strong>388,700</strong> and 138,013 + 269,532 + 3,725 = '
 '<strong>411,270</strong>.</li>\n'
 '   <li>The Philippines 2020 figure verified against the PSA census release: <strong>78,396</strong>.</li>\n'
 '   <li>Every Italian irregular-migration value verified against ISMU’s own published series.</li>\n'
 '  </ul>\n</div></section>\n')
page('verification.html', 'Verification — Migration Data Archive', body,
     desc='Full verification record: 2,454 values re-derived from live sources, corrections and issues.')
print('verification.html')

# =====================================================================  METHODS
qsum = qual[qual.n_years > 0].groupby('variable').agg(
    countries=('iso3', 'nunique'), obs=('n_years', 'sum')).reset_index()
qrows = ''
COV = {'population': 'Strong. Use freely.',
       'foreign_born': 'Strong, but includes naturalised citizens.',
       'foreign_nationals': 'Strong, and conceptually the right variable for this study.',
       'irregular_stock': 'Weak. Not comparable across countries.',
       'irregular_proxy_overstayers': 'Weak. Register counts; they understate the true figure.',
       'irregular_proxy_detections': 'Weakest. A flow of enforcement events, not a stock.'}
for v in VARS:
    row = qsum[qsum.variable == v]
    obs = int(row.obs.iloc[0]) if len(row) else 0
    nc = int(row.countries.iloc[0]) if len(row) else 0
    qrows += ('<tr><td>%s</td><td class="num">%d / 520</td><td class="num">%d / 40</td>'
              '<td>%s</td></tr>' % (E(VLAB[v]), obs, nc, E(COV[v])))
qtab = ('<div class="tablewrap"><table><thead><tr><th>Variable</th>'
        '<th class="num">Country-years</th><th class="num">Countries</th><th>Verdict</th>'
        '</tr></thead><tbody>' + qrows + '</tbody></table></div>')

body = (
 '<div class="hero"><div class="wrap">\n  <p class="eyebrow">Methods</p>\n'
 '  <h1>How this archive was built</h1>\n'
 '  <p class="lede">The procedure, the grading scheme, and the judgements a reader needs in order '
 'to decide how much weight each variable can carry.</p>\n</div></div>\n\n'
 '<section><div class="wrap">\n  <h2>Procedure</h2>\n'
 '  <ol style="max-width:78ch;line-height:1.75">\n'
 '   <li><strong>Catalogue.</strong> Every source reference was extracted from both input '
 'workbooks: 171 references, 160 distinct URLs across 51 hosts.</li>\n'
 '   <li><strong>Re-query.</strong> Each bulk statistical source was requested again and the raw '
 'response saved unaltered. Each value in the workbooks was then recomputed from that response '
 'and compared.</li>\n'
 '   <li><strong>Retrieve.</strong> Every document source was downloaded into a per-country '
 'folder. Where the first attempt was refused, a full browser header set, then an interactive '
 'browser, then an equivalent official source were tried in turn.</li>\n'
 '   <li><strong>Snapshot.</strong> Every web-page source was rendered to PDF and to a full-page '
 'screenshot. Each render was then validated by dumping the rendered DOM and checking it against '
 'a list of bot-wall and block-page markers; any page that had answered with an interstitial was '
 're-rendered from the HTML copy archived earlier the same day, and is labelled as such.</li>\n'
 '   <li><strong>Audit.</strong> Internal consistency, derived columns, cross-file agreement and '
 'year-on-year breaks were tested independently of the source check.</li>\n'
 '   <li><strong>Correct and grade.</strong> Discrepancies traced to a demonstrable error were '
 'corrected against the live source and itemised; every value was graded.</li>\n'
 '   <li><strong>Make it traceable.</strong> One evidence page was generated for every '
 'country&times;variable series &mdash; 156 in all &mdash; listing each year&rsquo;s value, its '
 'grade, what it was checked against, and every archived file supporting it. Each was also '
 'rendered to a PDF extract, so every number exists in a fixed citable document as well as on a '
 'web page. Every value in every country&rsquo;s Panel data table links to its own evidence.</li>\n'
 '   <li><strong>Checksum.</strong> A SHA-256 hash was recorded for every file.</li>\n'
 '  </ol>\n</div></section>\n\n'
 '<section><div class="wrap">\n  <h2>Authorship</h2>\n'
 '  <p>This archive is joint work of <a href="https://raymond.cph.ntu.edu.tw/" rel="noopener">'
 '<strong>Prof. Raymond Kuo</strong></a>, National Taiwan University, and <strong>Claude</strong> '
 '(Anthropic).</p>\n</div></section>\n\n'
 '<section><div class="wrap">\n  <h2>Grading scheme</h2>\n'
 '  <p class="sub">Grades describe how a value was checked, not how plausible it looks.</p>\n'
 '  <div class="tablewrap"><table><thead><tr><th>Grade</th><th>Criterion</th></tr></thead><tbody>\n'
 '   <tr><td>' + pill('A') + '</td><td>Recomputed from a machine-readable official source and '
 'matched exactly, or replaced during this verification with a value taken from one.</td></tr>\n'
 '   <tr><td>' + pill('B') + '</td><td>Confirmed by reading the retrieved source document, '
 'including cases where the published components had to be summed.</td></tr>\n'
 '   <tr><td>' + pill('C') + '</td><td>Source document retrieved and archived, but the value is a '
 'modelled or survey-based estimate that cannot be mechanically re-derived from it.</td></tr>\n'
 '   <tr><td>' + pill('D') + '</td><td>The cited source could not be retrieved by any means, so '
 'the value rests on the original compiler’s transcription alone.</td></tr>\n'
 '  </tbody></table></div>\n</div></section>\n\n'
 '<section><div class="wrap">\n  <h2>How much weight each variable can carry</h2>\n  ' + qtab + '\n'
 '  <div class="note"><strong>Recommendation.</strong> Use <code>foreign_nationals_pct_pop</code> '
 'as the main cross-national regressor. It is the population the survey question is actually '
 'about, it covers 34 of 40 countries, and every value is graded A or B. Use '
 '<code>foreign_born_pct_pop</code> as a robustness check, noting that it includes naturalised '
 'citizens, who <em>are</em> nationals.</div>\n'
 '  <div class="note warn"><strong>Do not use any irregular-migration variable as a continuous '
 'cross-national regressor.</strong> Stocks cover 10.6% of country-years, the estimation methods '
 'are not comparable between countries, and detections are a flow driven by enforcement intensity '
 'and by a country’s position on migration routes. If irregular migration matters to the '
 'argument, treat it as an ordinal salience indicator or exploit within-country variation only.</div>\n'
 '</div></section>\n\n'
 '<section><div class="wrap">\n  <h2>Two cautions to carry into the analysis</h2>\n'
 '  <ul class="clean">\n'
 '   <li><strong>Reference dates differ.</strong> Eurostat and OECD stocks are measured at '
 '1 January, so the row labelled year <em>Y</em> describes 31 December of <em>Y&minus;1</em>. '
 'Taiwan and Korea are year-end; Japan is 1 January. The <code>*_ref_date</code> columns carry '
 'this per value.</li>\n'
 '   <li><strong>Choose one population denominator.</strong> Both World Bank '
 '(<code>population</code>) and UN WPP 2024 (<code>population_un_wpp2024</code>) are supplied '
 'because the two input workbooks disagreed. They differ by more than 3% for 26 country-years '
 '&mdash; Israel by 4.1%. Pick one and keep it for every country.</li>\n'
 '  </ul>\n</div></section>\n\n'
 '<section><div class="wrap">\n  <h2>Limits of this archive</h2>\n'
 '  <p>The archive fixes what could be demonstrated wrong and documents what could not be fixed. '
 'It does not make the irregular-migration variables comparable across countries, because no '
 'source does. Six values rest on a source that no longer exists anywhere reachable; they are '
 'graded D and named rather than quietly dropped. Five sources block or have moved, and were '
 'replaced by equivalents that confirmed the values &mdash; the substitutions are itemised on the '
 '<a href="verification.html">Verification</a> page.</p>\n'
 '  <p>Mirrors are held for verification only. Copyright in each source document remains with its '
 'publisher, and every entry links to the original URL.</p>\n</div></section>\n')
page('methods.html', 'Methods — Migration Data Archive', body,
     desc='Verification procedure, grading scheme and guidance on how much weight each variable carries.')
print('methods.html')
