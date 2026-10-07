# -*- coding: utf-8 -*-
"""Independent live sweep of every external URL the site publishes, run sequentially
with polite spacing so publisher rate limits are not mistaken for broken links."""
import os, re, ssl, sys, time, json, subprocess, datetime, urllib.request, urllib.error
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
 'https://press.police.ac.kr/pds/1476878914562.pdf': 'host down; the values it supported were re-sourced to the Ministry of Justice open-data series (no value is graded D)',
 'https://www.nisshinkyo.org/news/pdf/G-26-2.pdf': 'link rot; redundant mirror, primary ISA source archived',
 'https://www.sem.admin.ch/dam/sem/de/data/internationales/illegale-migration/sans_papiers/ber-sanspapiers-2015-d.pdf': 'link rot; corroborated by SRF report, archived',
 'https://www.migrationpolicy.org/commentary/diverse-flows-drive-increase-us-unauthorized-immigrant-population': 'blocked; rendered from archived HTML',
 'https://cmsny.org/us-undocumented-population-increased-in-july-2023-warren-090624/': 'blocked; rendered from archived HTML',
 # answered on 2026-08-18, failing on 2026-10-07; the copy archived on 2026-08-17 is the evidence
 'https://porcausa.org/wp-content/uploads/2020/07/RetratodelairregularidadporCausa.pdf': 'link rot since 2026-08-18 (HTTP 404); PDF archived 2026-08-17',
 'https://www.ine.gob.cl/docs/default-source/demografia-y-migracion/publicaciones-y-anuarios/migraci%C3%B3n-internacional/estimaci%C3%B3n-poblaci%C3%B3n-extranjera-en-chile-2018/sintesis-epe2023.pdf?sfvrsn=cc51129c_10': 'did not answer the first attempt from the sweep machine (transport, not a dead link); PDF and rendered mirror archived 2026-08-17',
 'https://www.ine.gob.cl/sala-de-prensa/prensa/general/noticia/2023/12/29/poblaci%C3%B3n-extranjera-residente-en-chile-super%C3%B3-los-1-6-millones-de-personas-en-2022-con-un-6-6-de-ellas-en-situaci%C3%B3n-irregular': 'did not answer the first attempt from the sweep machine (transport, not a dead link); HTML and rendered mirror archived 2026-08-17',
}

TODAY = datetime.date.today().isoformat()
M_PY = 'python urllib, TLS verification off'
M_CURL = 'curl, TLS verification on, after a failed first attempt'


def curl_retry(u):
    """A failed first attempt is not a dead link: Python's TLS stack and some hosts' bot checks fail where a
    plain curl with certificate verification succeeds (the audit of 2026-10-07 found 11 such cases)."""
    try:
        p = subprocess.run(['curl', '-s', '-L', '-m', '60', '-A', UA, '-o', os.devnull, '-w', '%{http_code} %{size_download}', u],
                           capture_output=True, timeout=90)
        code, size = p.stdout.decode().split()[:2]
        return int(code), int(size)
    except Exception:
        return 0, 0


def judged(u, code):
    return 'OK' if str(code).startswith('2') else ('KNOWN' if u in KNOWN else 'PROBLEM')


if '--retry-only' in sys.argv:
    # re-test only the rows that did not answer, with curl, and stamp every row with its date and method
    old = pd.read_csv(os.path.join(BASE, 'verification', 'link_sweep.csv'), encoding='utf-8-sig').fillna('').astype(object)
    for c, dflt in (('checked_on', TODAY), ('method', M_PY), ('first_result', '')):
        if c not in old.columns:
            old[c] = dflt
    old['first_result'] = [r.first_result or str(r.http) for r in old.itertuples()]
    for i, r in old[old.status != 'OK'].iterrows():
        if r.method == M_CURL:
            continue
        code, size = curl_retry(r.url)
        old.at[i, 'http'], old.at[i, 'bytes'] = code, size
        old.at[i, 'method'] = M_CURL
        old.at[i, 'status'] = judged(r.url, code)
        old.at[i, 'checked_on'] = TODAY
        old.at[i, 'error'] = '' if str(code).startswith('2') else 'curl: HTTP %s' % code
        if str(code).startswith('2'):
            old.at[i, 'disposition'] = ('reachable on retry; the first attempt (%s) was a transport or bot-check failure, '
                                        'not missing content' % r.first_result)
        elif r.url in KNOWN:
            old.at[i, 'disposition'] = KNOWN[r.url]
    old.to_csv(os.path.join(BASE, 'verification', 'link_sweep.csv'), index=False, encoding='utf-8-sig')
    print(old.status.value_counts().to_string())
    sys.exit(0)

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
    first, method = (str(code) if not err else err), M_PY
    if not str(code).startswith('2'):
        c2, s2 = curl_retry(u)
        if str(c2).startswith('2'):
            code, size, err, method = c2, s2, '', M_CURL
    status = judged(u, code)
    disp = KNOWN.get(u, '') if status != 'OK' else ('reachable on retry; the first attempt (%s) was a transport or '
                                                    'bot-check failure, not missing content' % first
                                                    if method == M_CURL else '')
    rows.append(dict(url=u, http=code, bytes=size, status=status, disposition=disp, error=err,
                     checked_on=TODAY, method=method, first_result=first))
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
