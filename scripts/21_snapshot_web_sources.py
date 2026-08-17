# -*- coding: utf-8 -*-
"""Render every web-page source to a PDF mirror and a full-page PNG screenshot,
so a reviewer can see the page as it stood on the access date."""
import os, re, subprocess, sys, time, shutil
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(BASE, 'migration-data-archive')
EV = os.path.join(SITE, 'evidence', 'countries')
CHROME = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
PROFILE = os.path.join(os.environ.get('TEMP', 'C:/Windows/Temp'), 'claude', 'chrome-snap-profile')
ACCESS = '2026-08-17'

reg = pd.read_csv(os.path.join(SITE, 'data', 'source_register.csv'))
docs = reg[reg.retrieval != 'VERIFIED_API'].drop_duplicates(subset=['iso3', 'source_url'])
targets = docs[docs.local_file.astype(str).str.endswith('.html')]

# pages that are JS-rendered or blocked and were already captured interactively
ALREADY = {
    'https://www.moj.go.kr/moj/2415/subview.do',
    'https://psa.gov.ph/content/foreign-citizens-country-2020-census-population-and-housing',
}


def safe(s, n=60):
    return re.sub(r'[^A-Za-z0-9._-]+', '_', str(s)).strip('_')[:n]


def run(args, timeout=150):
    try:
        p = subprocess.run(args, capture_output=True, timeout=timeout)
        return p.returncode, (p.stderr or b'').decode('utf8', 'replace')[-200:]
    except subprocess.TimeoutExpired:
        return 'TIMEOUT', ''
    except Exception as e:
        return 'ERR', str(e)[:200]


rows = []
todo = [r for _, r in targets.iterrows() if r['source_url'] not in ALREADY]
print('rendering %d web pages to PDF + PNG\n' % len(todo))

for i, r in enumerate(todo, 1):
    iso, url = r['iso3'], r['source_url']
    dst = os.path.join(EV, iso)
    os.makedirs(dst, exist_ok=True)
    stem = 'SNAPSHOT__%s__%s' % (safe(r['variable'], 26), safe(re.sub(r'^https?://', '', url), 46))
    pdf = os.path.join(dst, stem + '.pdf')
    png = os.path.join(dst, stem + '.png')

    got_pdf = got_png = False
    if not (os.path.exists(pdf) and os.path.getsize(pdf) > 5000):
        rc, err = run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
                       '--user-data-dir=' + PROFILE, '--hide-scrollbars',
                       '--no-pdf-header-footer', '--virtual-time-budget=25000',
                       '--run-all-compositor-stages-before-draw',
                       '--print-to-pdf=' + pdf, url])
    got_pdf = os.path.exists(pdf) and os.path.getsize(pdf) > 5000

    if not (os.path.exists(png) and os.path.getsize(png) > 5000):
        rc, err = run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
                       '--user-data-dir=' + PROFILE, '--hide-scrollbars',
                       '--window-size=1400,3200', '--virtual-time-budget=25000',
                       '--run-all-compositor-stages-before-draw',
                       '--screenshot=' + png, url])
    got_png = os.path.exists(png) and os.path.getsize(png) > 5000

    for f, ok in ((pdf, got_pdf), (png, got_png)):
        if os.path.exists(f) and not ok:
            os.remove(f)

    rows.append(dict(iso3=iso, variable=r['variable'], source_url=url,
                     pdf_mirror=os.path.basename(pdf) if got_pdf else '',
                     png_screenshot=os.path.basename(png) if got_png else '',
                     pdf_bytes=os.path.getsize(pdf) if got_pdf else 0,
                     png_bytes=os.path.getsize(png) if got_png else 0,
                     captured=ACCESS))
    print('%2d/%d %-4s pdf:%-7s png:%-9s %s' % (
        i, len(todo), iso,
        f'{os.path.getsize(pdf)//1024}K' if got_pdf else 'FAIL',
        f'{os.path.getsize(png)//1024}K' if got_png else 'FAIL',
        url[:74]))
    sys.stdout.flush()

# record the two captured interactively
for iso, url, f in [('KOR', 'https://www.moj.go.kr/moj/2415/subview.do',
                     'irregular__MOJ_illegal_stay_table_2021_2025_SCREENSHOT.jpg'),
                    ('PHL', 'https://psa.gov.ph/content/foreign-citizens-country-2020-census-population-and-housing',
                     'foreign_nationals__PSA_2020CPH_foreign_citizens_SCREENSHOT.jpg')]:
    p = os.path.join(EV, iso, f)
    rows.append(dict(iso3=iso, variable='irregular / foreign_nationals', source_url=url,
                     pdf_mirror='', png_screenshot=f if os.path.exists(p) else '',
                     pdf_bytes=0, png_bytes=os.path.getsize(p) if os.path.exists(p) else 0,
                     captured=ACCESS))

df = pd.DataFrame(rows)
df.to_csv(os.path.join(SITE, 'data', 'web_snapshots.csv'), index=False, encoding='utf-8-sig')
print('\npdf mirrors: %d | png screenshots: %d | of %d pages'
      % ((df.pdf_mirror != '').sum(), (df.png_screenshot != '').sum(), len(df)))
