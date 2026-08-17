# -*- coding: utf-8 -*-
"""Independent live sweep of every external URL the site publishes, run sequentially
with polite spacing so publisher rate limits are not mistaken for broken links."""
import os, re, ssl, sys, time, json, urllib.request, urllib.error
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_here = os.path.dirname(os.path.abspath(__file__))
_parent = os.path.dirname(_here)
if os.path.isdir(os.path.join(_parent, 'data')) and os.path.isdir(os.path.join(_parent, 'evidence')):
    SITE = _parent          # scripts/ lives inside the published archive
else:
    SITE = os.path.join(BASE, 'migration-data-archive')

D = os.path.join(SITE, 'data')
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/126.0.0.0 Safari/537.36')

# every external URL the site publishes: data tables AND every generated HTML page
urls = set()
for f, col in [('api_snapshots.csv', 'query_url'),
               ('api_publisher_snapshots.csv', 'page_url'),
               ('source_register.csv', 'source_url'),
               ('web_snapshots.csv', 'source_url'),
               ('irregular_estimates_all.csv', 'source_url'),
               ('panel_final.csv', None)]:
    p = os.path.join(D, f)
    if not os.path.exists(p):
        continue
    df0 = pd.read_csv(p, low_memory=False)
    cols = [col] if col else [c for c in df0.columns if c.endswith('_url')]
    for c in cols:
        if c in df0.columns:
            for u in df0[c].dropna().astype(str):
                if u.startswith('http'):
                    urls.add(u.strip())

HTML_DIRS = [SITE, os.path.join(SITE, 'countries'), os.path.join(SITE, 'evidence-pages')]
n_html = 0
for d in HTML_DIRS:
    if not os.path.isdir(d):
        continue
    for f in os.listdir(d):
        if not f.endswith('.html'):
            continue
        n_html += 1
        h = open(os.path.join(d, f), encoding='utf-8', errors='replace').read()
        for m in re.finditer(r'href="(https?://[^"]+)"', h):
            u = m.group(1).replace('&amp;', '&').strip()
            if 'raymond.cph.ntu.edu.tw' not in u:      # author page, not a data source
                urls.add(u)
urls = sorted(urls)
print('scanned %d HTML pages' % n_html)
print('external URLs published by the site: %d' % len(urls))

# URLs already documented as blocked / dead, with the site's disposition
KNOWN = {
 'https://journals.sagepub.com/doi/10.1177/23315024241226624': 'blocked; archived HTML mirror held',
 'https://mexico.iom.int/sites/g/files/tmzbdl1686/files/documents/2024-03/estadisticas-migratorias-2023.pdf': 'blocked; PDF recovered and archived',
 'https://psa.gov.ph/content/foreign-citizens-country-2020-census-population-and-housing': 'bot check; interactive screenshot archived',
 'https://www.gov.il/BlobFolder/generalpage/foreign_workers_stats/he/zarim_2022_q1.pdf': 'blocked; PDF recovered and archived',
 'https://www.ismu.org/comunicato-stampa-xxv-rapporto-ismu/': 'blocked; substituted by ISMU official series',
 'https://www.ismu.org/xxvii-rapporto-sulle-migrazioni-2021-comunicato-stampa-11-2-2022/': 'blocked; substituted by ISMU official series',
 'https://www.cinformi.it/Comunicazione/Notizie/I-dati-del-Rapporto-ISMU-sulle-migrazioni-2020': 'host down; substituted by ISMU official series',
 'https://press.police.ac.kr/pds/1476878914562.pdf': 'host down; no copy exists, dependent values graded D',
 'https://www.nisshinkyo.org/news/pdf/G-26-2.pdf': 'link rot; redundant mirror, primary ISA source archived',
 'https://www.sem.admin.ch/dam/sem/de/data/internationales/illegale-migration/sans_papiers/ber-sanspapiers-2015-d.pdf': 'link rot; corroborated by SRF report, archived',
 'https://www.migrationpolicy.org/commentary/diverse-flows-drive-increase-us-unauthorized-immigrant-population': 'blocked; rendered from archived HTML',
 'https://cmsny.org/us-undocumented-population-increased-in-july-2023-warren-090624/': 'blocked; rendered from archived HTML',
}

rows = []
for i, u in enumerate(urls, 1):
    code, size, err = None, 0, ''
    for attempt in (1, 2):
        try:
            req = urllib.request.Request(u, headers={
                'User-Agent': UA,
                'Accept': 'text/html,application/xhtml+xml,application/pdf,application/json;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9'})
            with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
                code = r.status
                size = len(r.read(400000))
            break
        except urllib.error.HTTPError as e:
            code, err = e.code, 'HTTP %s' % e.code
            if e.code == 429 and attempt == 1:
                time.sleep(8)
                continue
            break
        except Exception as e:
            code, err = 'ERR', str(e)[:70]
            break
    status = ('OK' if str(code).startswith('2')
              else ('KNOWN' if u in KNOWN else 'PROBLEM'))
    rows.append(dict(url=u, http=code, bytes=size, status=status,
                     disposition=KNOWN.get(u, ''), error=err))
    if status == 'PROBLEM':
        print('  PROBLEM %-6s %s' % (code, u[:105]))
    if i % 25 == 0:
        print('  ... %d/%d' % (i, len(urls))); sys.stdout.flush()
    time.sleep(1.2)

df = pd.DataFrame(rows)
df.to_csv(os.path.join(BASE, 'verification', 'link_sweep.csv'), index=False, encoding='utf-8-sig')
print()
print(df.status.value_counts().to_string())
print()
prob = df[df.status == 'PROBLEM']
if len(prob):
    print('UNDOCUMENTED PROBLEMS (%d):' % len(prob))
    for _, r in prob.iterrows():
        print('  %-6s %s' % (r['http'], r['url']))
else:
    print('No undocumented broken URLs. Every non-200 is a disclosed publisher block or link rot.')
