# -*- coding: utf-8 -*-
"""Capture a dated live snapshot of every source that was re-cited on 2026-08-18.

Those five rows already carried an archived copy and a rendered mirror of it, but a
mirror and a snapshot prove different things: a mirror shows what this archive holds,
a snapshot shows what the publisher served, on a stated date. The re-cited sources are
now the authority printed on the page, so they should have both.

Chrome will not render when spawned from this process — it exits 0, writes nothing,
and reports "opening in an existing browser session" whenever a browser is open. Driven
through PowerShell Start-Process it renders normally, so that is how it is called here.
"""
import os
import subprocess
import sys
import pandas as pd

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(SITE, 'data')
CHROME = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
CAPTURED = '2026-08-18'

# Only pages are snapshotted. The Japanese ISA source and the ISMU workbook are files,
# not pages: for those the archived file itself is the evidence and Chrome would only
# capture a download shell.
TARGETS = [
    dict(iso3='CHE', variable='irregular_stock', tag='SRF_SEM_sanspapiers',
         url='https://www.srf.ch/news/schweiz/'
             'schweiz-sem-schaetzt-zahl-der-sans-papiers-in-der-schweiz-auf-76-000',
         archived='irregular_stock__SRF_SEM_76000_sanspapiers_CORROBORATION.html'),
    dict(iso3='ITA', variable='irregular_stock', tag='Cariplo_XXVIII_Rapporto_2022',
         url='https://www.fondazionecariplo.it/xxviii-rapporto-ismu-sulle-migrazioni-2022/',
         archived='irregular_stock__Cariplo_XXVIII_Rapporto_ISMU_2022_CORROBORATION.html'),
    dict(iso3='ITA', variable='irregular_stock', tag='ISMU_data_on_migration',
         url='https://test.ismu.org/en/data-on-migration/',
         archived='irregular_stock__ISMU_data_on_migration_CORROBORATION.html'),
    dict(iso3='KOR', variable='irregular_proxy_overstayers', tag='MOJ_yearbook2015_korea_kr',
         url='https://www.korea.kr/archive/expDocView.do?docId=38074',
         archived='irregular_proxy_overstayers__MOJ_yearbook2015_ch6_pp74-75.pdf'),
]


def psq(s):
    return "'" + str(s).replace("'", "''") + "'"


def chrome(args, label):
    """Render through Start-Process, the only spawn that produces output here."""
    ps = ('$a = @(%s); $p = Start-Process -FilePath %s -ArgumentList $a -PassThru -Wait '
          '-WindowStyle Hidden; exit $p.ExitCode'
          % (','.join(psq(a) for a in args), psq(CHROME)))
    try:
        subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-Command', ps],
                       capture_output=True, timeout=300)
    except subprocess.TimeoutExpired:
        print('   %s TIMEOUT' % label)


rows = []
for t in TARGETS:
    folder = os.path.join(SITE, 'evidence', 'countries', t['iso3'])
    os.makedirs(folder, exist_ok=True)
    base = 'SNAPSHOT__%s__%s__%s' % (t['variable'], t['tag'], CAPTURED)
    pdf = os.path.join(folder, base + '.pdf')
    png = os.path.join(folder, base + '.png')
    prof = os.path.join(os.environ.get('TEMP', 'C:/Windows/Temp'), 'claude', 'chrome-snap')

    common = ['--headless=new', '--disable-gpu', '--no-sandbox',
              '--user-data-dir=' + prof, '--hide-scrollbars',
              '--virtual-time-budget=20000', '--window-size=1280,2400']
    print('%s  %s' % (t['iso3'], t['url'][:78]))
    for out in (pdf, png):
        if os.path.exists(out):
            os.remove(out)
    chrome(common + ['--no-pdf-header-footer', '--print-to-pdf=' + pdf, t['url']], 'pdf')
    chrome(common + ['--screenshot=' + png, t['url']], 'png')

    pb = os.path.getsize(pdf) if os.path.exists(pdf) else 0
    nb = os.path.getsize(png) if os.path.exists(png) else 0
    print('   pdf %7d bytes | png %7d bytes' % (pb, nb))
    if pb < 3000 and nb < 3000:
        print('   NOT CAPTURED - leaving the register untouched for this source')
        continue
    rows.append(dict(iso3=t['iso3'], variable=t['variable'], source_url=t['url'],
                     pdf_mirror=os.path.basename(pdf) if pb >= 3000 else '',
                     png_screenshot=os.path.basename(png) if nb >= 3000 else '',
                     pdf_bytes=pb, png_bytes=nb, captured=CAPTURED,
                     snapshot_status='live_render_verified',
                     archived_html=t['archived'],
                     note='Captured after this source became the cited authority on %s.'
                          % CAPTURED))

if not rows:
    print('\nnothing captured; web_snapshots.csv unchanged')
    sys.exit(1)

p = os.path.join(D, 'web_snapshots.csv')
ws = pd.read_csv(p).fillna('')
new = pd.DataFrame(rows)
keep = ws[~ws.set_index(['iso3', 'source_url']).index.isin(
    new.set_index(['iso3', 'source_url']).index)]
out = pd.concat([keep, new], ignore_index=True).sort_values(['iso3', 'variable', 'source_url'])
out.to_csv(p, index=False, encoding='utf-8-sig')
print('\nweb_snapshots.csv: %d -> %d rows (%d captured)' % (len(ws), len(out), len(new)))
