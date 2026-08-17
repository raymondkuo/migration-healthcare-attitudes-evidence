# -*- coding: utf-8 -*-
"""Download every document source into its country folder and record the HTTP result."""
import os, re, ssl, time, sys, urllib.request, urllib.error, urllib.parse
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VER = os.path.join(BASE, 'verification')
man = pd.read_csv(os.path.join(VER, 'country_source_manifest.csv'))
docs = man[man.kind == 'document'].copy()

ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/126.0.0.0 Safari/537.36')
HDRS = {'User-Agent': UA,
        'Accept': 'text/html,application/xhtml+xml,application/pdf,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,ja;q=0.7,ko;q=0.7,es;q=0.6',
        'Accept-Encoding': 'identity'}

EXT = {'application/pdf': '.pdf', 'text/html': '.html', 'application/xhtml+xml': '.html',
       'text/plain': '.txt', 'application/json': '.json',
       'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
       'application/vnd.ms-excel': '.xls', 'text/csv': '.csv'}


def safe(s, n=70):
    s = re.sub(r'[^A-Za-z0-9._-]+', '_', str(s)).strip('_')
    return s[:n]


results = []
for i, (_, r) in enumerate(docs.iterrows(), 1):
    url = r['source_url']
    folder = os.path.join(r['folder'], 'sources')
    os.makedirs(folder, exist_ok=True)
    stem = '%s__%s__%s' % (safe(r['variable'], 28), safe(r['url_id'], 10),
                           safe(urllib.parse.urlparse(url).netloc, 28))
    existing = [f for f in os.listdir(folder) if f.startswith(stem)]
    if existing and os.path.getsize(os.path.join(folder, existing[0])) > 800:
        results.append(dict(iso3=r['iso3'], variable=r['variable'], source_url=url,
                            http_status='cached', content_type='', bytes=os.path.getsize(
                                os.path.join(folder, existing[0])), local_file=existing[0],
                            source_name=r['source_name']))
        continue
    status, ctype, data, err = None, '', b'', ''
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers=HDRS)
            with urllib.request.urlopen(req, timeout=90, context=ctx) as resp:
                status = resp.status
                ctype = (resp.headers.get('Content-Type') or '').split(';')[0].strip().lower()
                data = resp.read()
            break
        except urllib.error.HTTPError as e:
            status, err = e.code, 'HTTP %s' % e.code
            try:
                ctype = (e.headers.get('Content-Type') or '').split(';')[0].strip().lower()
                data = e.read()
            except Exception:
                pass
            if e.code in (403, 404, 410):
                break
        except Exception as e:
            status, err = 'ERR', str(e)[:120]
        time.sleep(2)

    fname = ''
    if data and len(data) > 800 and str(status).startswith('2'):
        ext = EXT.get(ctype, '')
        if not ext:
            tail = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
            ext = tail if tail in ('.pdf', '.xlsx', '.xls', '.csv', '.json', '.html') else '.bin'
        if data[:4] == b'%PDF':
            ext = '.pdf'
        elif data[:2] == b'PK' and ext == '.bin':
            ext = '.xlsx'
        fname = stem + ext
        with open(os.path.join(folder, fname), 'wb') as f:
            f.write(data)
    results.append(dict(iso3=r['iso3'], variable=r['variable'], source_url=url,
                        http_status=status, content_type=ctype, bytes=len(data),
                        local_file=fname, source_name=r['source_name'], error=err))
    print('%3d/%d %-4s %-28s %-6s %-10s %9s  %s' % (
        i, len(docs), r['iso3'], str(r['variable'])[:28], str(status), ctype[:10],
        f'{len(data):,}', fname[:40] or err[:40]))
    sys.stdout.flush()
    time.sleep(0.7)

res = pd.DataFrame(results)
res.to_csv(os.path.join(VER, 'download_log.csv'), index=False, encoding='utf-8-sig')
print('\n--- summary ---')
print(res['http_status'].astype(str).value_counts().to_string())
print('\nfiles saved:', (res['local_file'].astype(str) != '').sum(), 'of', len(res))
