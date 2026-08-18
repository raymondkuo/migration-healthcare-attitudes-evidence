# -*- coding: utf-8 -*-
"""Three of the 2026-08-18 live captures came back as bot-protection pages, not content:
Cloudflare for fondazionecariplo.it and an HTTP 403 "Access Blocked" wall for both
ismu.org press releases. curl reaches all three; headless Chrome does not.

Publishing a challenge page as evidence would be worse than publishing nothing, so
those captures are deleted. The page CONTENT was retrieved and checked (each archived
HTML contains the figure it supports), so the visual is rendered from the archived HTML
instead - the same fallback this archive already uses for five other sources, recorded
honestly as rendered_from_archived_html rather than as a live capture.
"""
import os
import subprocess
import glob
import pandas as pd

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(SITE, 'data')
ITA = os.path.join(SITE, 'evidence', 'countries', 'ITA')
CHROME = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
CAPTURED = '2026-08-18'

BLOCKED = [
    dict(url='https://www.fondazionecariplo.it/xxviii-rapporto-ismu-sulle-migrazioni-2022/',
         pattern='SNAPSHOT__*Cariplo_XXVIII_Rapporto_2022__2026-08-18.*',
         archived=None),        # already has MIRROR__ files from its archived HTML
    dict(url='https://www.ismu.org/comunicato-stampa-xxv-rapporto-ismu/',
         pattern='SNAPSHOT__*ISMU_XXV_Rapporto_2019_comunicato__2026-08-18.*',
         archived='irregular_stock__ISMU_XXV_Rapporto_2019_comunicato.html',
         tag='ISMU_XXV_Rapporto_2019_comunicato', expect='562mila'),
    dict(url='https://www.ismu.org/xxvii-rapporto-sulle-migrazioni-2021-comunicato-stampa-11-2-2022/',
         pattern='SNAPSHOT__*ISMU_XXVII_Rapporto_2021_comunicato__2026-08-18.*',
         archived='irregular_stock__ISMU_XXVII_Rapporto_2021_comunicato.html',
         tag='ISMU_XXVII_Rapporto_2021_comunicato', expect='519mila'),
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


ws = pd.read_csv(os.path.join(D, 'web_snapshots.csv')).fillna('')
new_rows, drop_urls = [], []

for b in BLOCKED:
    for f in glob.glob(os.path.join(ITA, b['pattern'])):
        os.remove(f)
        print('removed blocked capture: %s' % os.path.basename(f)[:74])
    if not b.get('archived'):
        drop_urls.append(b['url'])
        continue

    src = os.path.join(ITA, b['archived'])
    if not os.path.exists(src):
        print('   archived HTML missing for %s - dropping the row' % b['tag'])
        drop_urls.append(b['url'])
        continue

    base = 'MIRROR__irregular_stock__%s' % b['tag']
    pdf, png = os.path.join(ITA, base + '.pdf'), os.path.join(ITA, base + '.png')
    prof = os.path.join(os.environ.get('TEMP', 'C:/Windows/Temp'), 'claude', 'chrome-arch')
    url = 'file:///' + src.replace('\\', '/')
    common = ['--headless=new', '--disable-gpu', '--no-sandbox', '--user-data-dir=' + prof,
              '--hide-scrollbars', '--virtual-time-budget=15000', '--window-size=1280,2400']
    chrome(common + ['--no-pdf-header-footer', '--print-to-pdf=' + pdf, url])
    chrome(common + ['--screenshot=' + png, url])
    pb = os.path.getsize(pdf) if os.path.exists(pdf) else 0
    nb = os.path.getsize(png) if os.path.exists(png) else 0
    print('   rendered from archived HTML: pdf %d bytes, png %d bytes' % (pb, nb))
    if pb < 3000 and nb < 3000:
        drop_urls.append(b['url'])
        continue
    new_rows.append(dict(iso3='ITA', variable='irregular_stock', source_url=b['url'],
                         pdf_mirror=os.path.basename(pdf) if pb >= 3000 else '',
                         png_screenshot=os.path.basename(png) if nb >= 3000 else '',
                         pdf_bytes=pb, png_bytes=nb, captured=CAPTURED,
                         snapshot_status='rendered_from_archived_html',
                         archived_html=b['archived'],
                         note='The publisher answers a direct request but serves an HTTP 403 '
                              'bot wall to a browser, so this is rendered from the archived '
                              'copy retrieved on %s, which states %s.' % (CAPTURED, b['expect'])))

keep = ws[~ws.source_url.isin(drop_urls + [r['source_url'] for r in new_rows])]
out = (pd.concat([keep, pd.DataFrame(new_rows)], ignore_index=True) if new_rows else keep)
out = out.sort_values(['iso3', 'variable', 'source_url'])
out.to_csv(os.path.join(D, 'web_snapshots.csv'), index=False, encoding='utf-8-sig')
print('\nweb_snapshots.csv: %d -> %d rows' % (len(ws), len(out)))
print('dropped live-capture rows: %d | rendered-from-archive rows: %d'
      % (len(drop_urls), len(new_rows)))
