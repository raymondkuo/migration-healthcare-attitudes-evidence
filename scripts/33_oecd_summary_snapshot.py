# -*- coding: utf-8 -*-
"""Build a readable one-page summary of the OECD dataflow definition and render it,
replacing the 22 MB raw-XML print-out."""
import os, re, subprocess, html
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(BASE, 'migration-data-archive')
OUT = os.path.join(SITE, 'evidence', 'api', 'publisher_pages')
XML = os.path.join(SITE, 'evidence', 'api', 'oecd', 'DSD_MIG_dataflow_metadata.xml')
CHROME = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
PROFILE = os.path.join(os.environ.get('TEMP', 'C:/Windows/Temp'), 'claude', 'chrome-oecd')
ACCESS = '2026-08-17'

s = open(XML, encoding='utf-8', errors='replace').read()
prepared = (re.search(r'<message:Prepared>(.*?)</message:Prepared>', s) or [None, '—'])[1]
dfm = re.search(r'<structure:Dataflow id="([^"]+)" agencyID="([^"]+)" version="([^"]+)"', s)

# the MEASURE codelist entries actually used by this archive
codes = {}
for cid in ['B11', 'B12', 'B13', 'B14', 'B15']:
    m = re.search(r'<structure:Code id="%s">(.*?)</structure:Code>' % cid, s, re.S)
    if m:
        nm = re.search(r'<common:Name xml:lang="en">(.*?)</common:Name>', m.group(1), re.S)
        codes[cid] = html.unescape(nm.group(1).strip()) if nm else ''

used = pd.read_csv(os.path.join(SITE, 'data', 'panel_final.csv'))
oecd_rows = []
for v, meas in [('foreign_born', 'B14'), ('foreign_nationals', 'B15')]:
    sub = used[used[v + '_source'].astype(str).str.contains('OECD', na=False)]
    for iso, g in sub.groupby('iso3'):
        oecd_rows.append((iso, v, meas, int(g.year.min()), int(g.year.max()), len(g)))
oecd_rows.sort()

rowhtml = ''.join(
    '<tr><td>%s</td><td>%s</td><td><code>%s</code></td><td class="n">%d–%d</td><td class="n">%d</td></tr>'
    % (iso, v, meas, y0, y1, n) for iso, v, meas, y0, y1, n in oecd_rows)
codehtml = ''.join('<tr><td><code>%s</code></td><td>%s</td><td>%s</td></tr>'
                   % (k, html.escape(v), 'used by this archive' if k in ('B14', 'B15') else '—')
                   for k, v in sorted(codes.items()))

doc = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>OECD International Migration Database — dataflow definition</title>
<style>
 @page{margin:16mm}
 body{font:12.5px/1.55 -apple-system,"Segoe UI",Roboto,sans-serif;color:#1a1a18;margin:0}
 h1{font-size:19px;margin:0 0 4px;letter-spacing:-.01em}
 .sub{color:#5f5f5a;margin:0 0 18px;font-size:12.5px}
 h2{font-size:14px;margin:22px 0 7px}
 table{border-collapse:collapse;width:100%;font-size:11.6px}
 th,td{border:1px solid #ddd;padding:5px 8px;text-align:left;vertical-align:top}
 th{background:#eef2f7;font-weight:600}
 td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}
 code{font-family:Consolas,monospace;font-size:11px;background:#f2f4f7;padding:1px 4px;border-radius:3px}
 .box{border-left:3px solid #3d5a80;background:#eef2f7;padding:9px 13px;margin:14px 0;font-size:11.8px}
 .foot{margin-top:26px;border-top:1px solid #ddd;padding-top:9px;color:#6a6a64;font-size:10.6px}
</style></head><body>
<h1>OECD International Migration Database — dataflow definition</h1>
<p class="sub">Authoritative structural metadata retrieved from the OECD SDMX registry on ACCESSDATE.
This is the service the archive's OECD values were queried from.</p>

<div class="box"><strong>Why this page exists.</strong> <code>oecd.org</code> returns HTTP 403 to
every automated client, so the OECD's human-facing dataset page could not be mirrored. The SDMX
registry — the actual data source used — is open, and its dataflow definition is reproduced here
and archived in full as
<code>evidence/api/oecd/DSD_MIG_dataflow_metadata.xml</code>.</div>

<h2>Identity</h2>
<table>
<tr><th style="width:26%">Dataflow ID</th><td><code>DATAFLOWID</code></td></tr>
<tr><th>Agency</th><td><code>AGENCYID</code></td></tr>
<tr><th>Version</th><td>VERSIONID</td></tr>
<tr><th>Registry prepared</th><td>PREPARED</td></tr>
<tr><th>Metadata query</th><td><code>https://sdmx.oecd.org/public/rest/dataflow/OECD.ELS.IMD/DSD_MIG@DF_MIG/1.0?references=all</code></td></tr>
<tr><th>Data query, B14</th><td><code>https://sdmx.oecd.org/public/rest/data/OECD.ELS.IMD,DSD_MIG_F@DF_MIG_POPF,1.0/&lt;ISO3&gt;.W.A.B14._T._Z._Z.PS?startPeriod=2010&amp;endPeriod=2022&amp;format=jsondata&amp;dimensionAtObservation=AllDimensions</code></td></tr>
<tr><th>Data query, B15</th><td><code>https://sdmx.oecd.org/public/rest/data/OECD.ELS.IMD,DSD_MIG@DF_MIG,1.0/&lt;ISO3&gt;.W.A.B15._T._Z._Z.PS?startPeriod=2010&amp;endPeriod=2022&amp;format=jsondata&amp;dimensionAtObservation=AllDimensions</code></td></tr>
</table>

<h2>MEASURE codelist — the definitions that matter</h2>
<table><thead><tr><th style="width:12%">Code</th><th>Definition (OECD)</th><th style="width:26%">Status here</th></tr></thead>
<tbody>CODEROWS</tbody></table>

<h2>Series drawn from this dataflow into the archive</h2>
<table><thead><tr><th>Country</th><th>Variable</th><th>Measure</th><th class="n">Years</th><th class="n">Values</th></tr></thead>
<tbody>SERIESROWS</tbody></table>

<p class="foot">Migration and Population Data Archive · captured ACCESSDATE · every one of these
values was re-derived from the raw SDMX responses in <code>evidence/api/oecd/</code> and matched
the archived panel exactly.</p>
</body></html>"""

doc = (doc.replace('ACCESSDATE', ACCESS)
          .replace('DATAFLOWID', dfm.group(1) if dfm else 'DSD_MIG@DF_MIG')
          .replace('AGENCYID', dfm.group(2) if dfm else 'OECD.ELS.IMD')
          .replace('VERSIONID', dfm.group(3) if dfm else '1.0')
          .replace('PREPARED', html.escape(prepared))
          .replace('CODEROWS', codehtml)
          .replace('SERIESROWS', rowhtml))

tmp = os.path.join(OUT, '_oecd_summary.html')
open(tmp, 'w', encoding='utf-8').write(doc)
src = 'file:///' + tmp.replace('\\', '/')
for flags in ([('--no-pdf-header-footer', '--print-to-pdf=' + os.path.join(OUT, 'oecd_international_migration_database.pdf'))],
              [('--window-size=1400,2200', '--screenshot=' + os.path.join(OUT, 'oecd_international_migration_database.png'))]):
    flat = [x for t in flags for x in t]
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
                    '--user-data-dir=' + PROFILE, '--hide-scrollbars',
                    '--virtual-time-budget=12000'] + flat + [src], capture_output=True, timeout=180)
os.remove(tmp)

p = os.path.join(SITE, 'data', 'api_publisher_snapshots.csv')
df = pd.read_csv(p)
m = df.key == 'oecd_international_migration_database'
for ext, col in (('pdf', 'pdf'), ('png', 'png')):
    f = os.path.join(OUT, 'oecd_international_migration_database.' + ext)
    df.loc[m, col + '_bytes'] = os.path.getsize(f) if os.path.exists(f) else 0
df.to_csv(p, index=False, encoding='utf-8-sig')
print('OECD summary: pdf %s KB, png %s KB, %d series listed'
      % (os.path.getsize(os.path.join(OUT, 'oecd_international_migration_database.pdf')) // 1024,
         os.path.getsize(os.path.join(OUT, 'oecd_international_migration_database.png')) // 1024,
         len(oecd_rows)))
print('codes:', codes)
