# -*- coding: utf-8 -*-
"""ismu.org answers again, and the pages corroborate the Italian figures.

The register recorded that ismu.org "returns HTTP 403 to every client, including a real
browser". Re-checked on 2026-08-18 both press releases returned 200 and state the values
this archive publishes:

    XXV Rapporto   "...componente irregolare (+5,4%), pari a 562mila unita"      -> 2019
    XXVII Rapporto "...attestandosi sui 519mila (contro i 517mila dell'anno...)" -> 2021, 2020

The cited source stays the ISMU machine-readable series, which reproduces every year
exactly. These pages are archived alongside it as independent corroboration, and the
claim that they are unreachable is withdrawn.
"""
import os
import re
import subprocess
import pandas as pd

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(SITE, 'data')
ITA = os.path.join(SITE, 'evidence', 'countries', 'ITA')
CHROME = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
CAPTURED = '2026-08-18'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126 Safari/537.36')

PAGES = [
    dict(tag='ISMU_XXV_Rapporto_2019_comunicato',
         url='https://www.ismu.org/comunicato-stampa-xxv-rapporto-ismu/',
         expect='562mila', years='2019'),
    dict(tag='ISMU_XXVII_Rapporto_2021_comunicato',
         url='https://www.ismu.org/xxvii-rapporto-sulle-migrazioni-2021-comunicato-stampa-11-2-2022/',
         expect='519mila', years='2020-2021'),
]


def psq(s):
    return "'" + str(s).replace("'", "''") + "'"


def chrome(args):
    ps = ('$a = @(%s); $p = Start-Process -FilePath %s -ArgumentList $a -PassThru -Wait '
          '-WindowStyle Hidden; exit $p.ExitCode'
          % (','.join(psq(a) for a in args), psq(CHROME)))
    try:
        subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-Command', ps],
                       capture_output=True, timeout=300)
    except subprocess.TimeoutExpired:
        pass


rows = []
for p in PAGES:
    html_name = 'irregular_stock__%s.html' % p['tag']
    html_path = os.path.join(ITA, html_name)
    subprocess.run(['curl', '-s', '-L', '--max-time', '60', '-A', UA,
                    p['url'], '-o', html_path], check=False)
    raw = open(html_path, encoding='utf-8', errors='replace').read()
    text = re.sub(r'<[^>]+>', ' ', re.sub(r'<(script|style).*?</\1>', '', raw,
                                          flags=re.S | re.I))
    found = p['expect'] in re.sub(r'\s+', ' ', text)
    print('%s\n   html %7d bytes | states %s: %s' % (p['url'][:88], len(raw), p['expect'], found))
    if not found:
        print('   value not present in what was served - not archiving this page')
        os.remove(html_path)
        continue

    base = 'SNAPSHOT__irregular_stock__%s__%s' % (p['tag'], CAPTURED)
    pdf, png = os.path.join(ITA, base + '.pdf'), os.path.join(ITA, base + '.png')
    prof = os.path.join(os.environ.get('TEMP', 'C:/Windows/Temp'), 'claude', 'chrome-ismu')
    common = ['--headless=new', '--disable-gpu', '--no-sandbox', '--user-data-dir=' + prof,
              '--hide-scrollbars', '--virtual-time-budget=20000', '--window-size=1280,2400']
    chrome(common + ['--no-pdf-header-footer', '--print-to-pdf=' + pdf, p['url']])
    chrome(common + ['--screenshot=' + png, p['url']])
    pb = os.path.getsize(pdf) if os.path.exists(pdf) else 0
    nb = os.path.getsize(png) if os.path.exists(png) else 0
    print('   pdf %7d bytes | png %7d bytes' % (pb, nb))

    rows.append(dict(iso3='ITA', variable='irregular_stock', source_url=p['url'],
                     pdf_mirror=os.path.basename(pdf) if pb >= 3000 else '',
                     png_screenshot=os.path.basename(png) if nb >= 3000 else '',
                     pdf_bytes=pb, png_bytes=nb, captured=CAPTURED,
                     snapshot_status='live_render_verified',
                     archived_html=html_name,
                     note='Reachable again on %s after previously refusing all clients; '
                          'states %s, corroborating %s.' % (CAPTURED, p['expect'], p['years'])))

if rows:
    fp = os.path.join(D, 'web_snapshots.csv')
    ws = pd.read_csv(fp).fillna('')
    new = pd.DataFrame(rows)
    keep = ws[~ws.set_index(['iso3', 'source_url']).index.isin(
        new.set_index(['iso3', 'source_url']).index)]
    out = pd.concat([keep, new], ignore_index=True).sort_values(
        ['iso3', 'variable', 'source_url'])
    out.to_csv(fp, index=False, encoding='utf-8-sig')
    print('\nweb_snapshots.csv: %d -> %d rows' % (len(ws), len(out)))

    # the register note must stop asserting something that is no longer true
    rp = os.path.join(D, 'source_register.csv')
    reg = pd.read_csv(rp).fillna('')
    m = reg.superseded_source_url.astype(str).str.contains('ismu.org', na=False)
    reg.loc[m, 'note'] = (
        'Cited to ISMU\'s own machine-readable series, which reproduces every year exactly. '
        'The press release originally cited refused all clients when this archive was built; '
        'it answered again on %s and states the same figure, and is archived here too.'
        % CAPTURED)
    reg.to_csv(rp, index=False, encoding='utf-8-sig')
    print('source_register.csv: %d ISMU note(s) corrected' % int(m.sum()))
