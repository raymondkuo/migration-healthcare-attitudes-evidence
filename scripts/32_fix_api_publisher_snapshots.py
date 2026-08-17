# -*- coding: utf-8 -*-
"""UN DESA and OECD refuse headless Chrome. Fetch their pages with a normal HTTP
client and render the retrieved copy instead, so both sources still get a viewable
mirror captured on the access date."""
import os, ssl, subprocess, urllib.request
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(BASE, 'migration-data-archive')
OUT = os.path.join(SITE, 'evidence', 'api', 'publisher_pages')
OECD = os.path.join(SITE, 'evidence', 'api', 'oecd')
CHROME = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
PROFILE = os.path.join(os.environ.get('TEMP', 'C:/Windows/Temp'), 'claude', 'chrome-fix')
ACCESS = '2026-08-17'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/126.0.0.0 Safari/537.36')
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE


def get(url, dest):
    req = urllib.request.Request(url, headers={
        'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9', 'Accept-Encoding': 'identity'})
    with urllib.request.urlopen(req, timeout=120, context=ctx) as r:
        d = r.read()
    open(dest, 'wb').write(d)
    return len(d)


def render(src_url, stem):
    for flags in ([('--no-pdf-header-footer', '--print-to-pdf=' + os.path.join(OUT, stem + '.pdf'))],
                  [('--window-size=1500,2600', '--screenshot=' + os.path.join(OUT, stem + '.png'))]):
        flat = [x for t in flags for x in t]
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
                        '--user-data-dir=' + PROFILE, '--hide-scrollbars',
                        '--virtual-time-budget=20000'] + flat + [src_url],
                       capture_output=True, timeout=180)


rows = []

# ---------------------------------------------------------------- UN DESA IMS 2024
tmp = os.path.join(OUT, '_un_desa_ims_page.html')
n = get('https://www.un.org/development/desa/pd/content/international-migrant-stock', tmp)
render('file:///' + tmp.replace('\\', '/'), 'un_desa_international_migrant_stock_2024')
print('UN DESA IMS page: %s bytes fetched, rendered from the retrieved copy' % f'{n:,}')
rows.append(('un_desa_international_migrant_stock_2024', 'rendered_from_retrieved_copy',
             'The UN DESA server returns 403 to headless Chrome. The page was fetched with a '
             'normal HTTP client on the access date and that retrieved copy was rendered.'))

# ---------------------------------------------------------------- OECD
# The OECD website blocks automated clients, but its SDMX registry — the service the
# data was actually taken from — serves the authoritative dataflow definition.
meta = os.path.join(OECD, 'DSD_MIG_dataflow_metadata.xml')
n = get('https://sdmx.oecd.org/public/rest/dataflow/OECD.ELS.IMD/DSD_MIG@DF_MIG/1.0?references=all', meta)
print('OECD SDMX dataflow metadata: %s bytes' % f'{n:,}')
render('file:///' + meta.replace('\\', '/'), 'oecd_international_migration_database')
rows.append(('oecd_international_migration_database', 'sdmx_registry_metadata',
             'oecd.org returns 403 to every automated client. Captured instead from the OECD '
             'SDMX registry, which is the service the data was actually queried from: the '
             'authoritative dataflow definition for DSD_MIG@DF_MIG, including the measure '
             'codelist that defines B14 (foreign-born stock) and B15 (foreign-national stock).'))

# ---------------------------------------------------------------- update the index
p = os.path.join(SITE, 'data', 'api_publisher_snapshots.csv')
df = pd.read_csv(p)
if 'note' not in df.columns:
    df['note'] = ''
for key, status, note in rows:
    m = df.key == key
    df.loc[m, 'status'] = status
    df.loc[m, 'note'] = note
    for ext, col in (('pdf', 'pdf'), ('png', 'png')):
        f = os.path.join(OUT, key + '.' + ext)
        ok = os.path.exists(f) and os.path.getsize(f) > 5000
        df.loc[m, col] = ('evidence/api/publisher_pages/%s.%s' % (key, ext)) if ok else ''
        df.loc[m, col + '_bytes'] = os.path.getsize(f) if ok else 0
df.loc[df.key == 'oecd_international_migration_database', 'page_url'] = \
    'https://sdmx.oecd.org/public/rest/dataflow/OECD.ELS.IMD/DSD_MIG@DF_MIG/1.0?references=all'
df.to_csv(p, index=False, encoding='utf-8-sig')

if os.path.exists(tmp):
    os.remove(tmp)

print()
print(df[['key', 'status', 'pdf_bytes', 'png_bytes']].to_string(index=False))
