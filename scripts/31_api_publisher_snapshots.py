# -*- coding: utf-8 -*-
"""Render PDF + PNG snapshots of the human-facing publisher page for every bulk
statistical source, so the API sources have viewable mirrors too."""
import os, re, subprocess, sys, html
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(BASE, 'migration-data-archive')
OUT = os.path.join(SITE, 'evidence', 'api', 'publisher_pages')
CHROME = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
PROFILE = os.path.join(os.environ.get('TEMP', 'C:/Windows/Temp'), 'claude', 'chrome-api')
ACCESS = '2026-08-17'
os.makedirs(OUT, exist_ok=True)

# key -> (publisher, dataset, human-facing page, which archive files it backs)
PAGES = [
 ('worldbank_SP_POP_TOTL', 'World Bank', 'World Development Indicators — Population, total (SP.POP.TOTL)',
  'https://data.worldbank.org/indicator/SP.POP.TOTL', 'wb_SP_POP_TOTL.json'),
 ('worldbank_SM_POP_TOTL', 'World Bank', 'World Development Indicators — International migrant stock (SM.POP.TOTL)',
  'https://data.worldbank.org/indicator/SM.POP.TOTL', 'wb_SM_POP_TOTL.json'),
 ('eurostat_migr_pop3ctb', 'Eurostat', 'Population on 1 January by age group, sex and country of birth (migr_pop3ctb)',
  'https://ec.europa.eu/eurostat/databrowser/view/migr_pop3ctb/default/table?lang=en',
  'eurostat_migr_pop3ctb.json'),
 ('eurostat_migr_pop1ctz', 'Eurostat', 'Population on 1 January by age group, sex and citizenship (migr_pop1ctz)',
  'https://ec.europa.eu/eurostat/databrowser/view/migr_pop1ctz/default/table?lang=en',
  'eurostat_migr_pop1ctz.json'),
 ('eurostat_migr_eipre', 'Eurostat', 'Third country nationals found to be illegally present — annual data (migr_eipre)',
  'https://ec.europa.eu/eurostat/databrowser/view/migr_eipre/default/table?lang=en',
  'eurostat_migr_eipre.json'),
 ('eurostat_migr_eipre_metadata', 'Eurostat', 'migr_eipre — explanatory metadata (definitions and caveats)',
  'https://ec.europa.eu/eurostat/cache/metadata/en/migr_eil_esms.htm', 'eurostat_migr_eipre.json'),
 ('oecd_international_migration_database', 'OECD', 'International Migration Database (stocks of foreign-born and foreign population)',
  'https://www.oecd.org/en/data/datasets/oecd-international-migration-database.html',
  'oecd/*.json'),
 ('un_wpp_2024', 'UN DESA', 'World Population Prospects 2024 — download portal',
  'https://population.un.org/wpp/downloads', 'UN_WPP2024_demographic_indicators_compact.xlsx'),
 ('un_desa_international_migrant_stock_2024', 'UN DESA', 'International Migrant Stock 2024',
  'https://www.un.org/development/desa/pd/content/international-migrant-stock',
  'UN_DESA_IMS2024_stock_by_sex_and_destination.xlsx'),
]

BLOCK = ['sorry, you have been blocked', 'just a moment', 'checking your browser',
         'verifying you are human', 'access blocked', 'attention required',
         '正在執行安全驗證', 'enable javascript and cookies']


def dom(url):
    try:
        p = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
                            '--user-data-dir=' + PROFILE, '--virtual-time-budget=22000',
                            '--dump-dom', url], capture_output=True, timeout=150)
        t = p.stdout.decode('utf8', 'replace')
        t = re.sub(r'<(script|style|noscript).*?</\1>', ' ', t, flags=re.S | re.I)
        t = re.sub(r'<[^>]+>', ' ', t)
        return re.sub(r'\s+', ' ', html.unescape(t))
    except Exception:
        return ''


rows = []
for key, pub, dataset, url, backs in PAGES:
    pdf = os.path.join(OUT, key + '.pdf')
    png = os.path.join(OUT, key + '.png')
    for flags in ([('--no-pdf-header-footer', '--print-to-pdf=' + pdf)],
                  [('--window-size=1500,2600', '--screenshot=' + png)]):
        flat = [x for t in flags for x in t]
        try:
            subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
                            '--user-data-dir=' + PROFILE, '--hide-scrollbars',
                            '--virtual-time-budget=25000',
                            '--run-all-compositor-stages-before-draw'] + flat + [url],
                           capture_output=True, timeout=180)
        except Exception:
            pass
    body = dom(url)[:5000].lower()
    blocked = any(m in body for m in BLOCK) or len(body) < 300
    ok_pdf = os.path.exists(pdf) and os.path.getsize(pdf) > 5000
    ok_png = os.path.exists(png) and os.path.getsize(png) > 5000
    status = 'blocked_or_empty' if blocked else 'captured'
    rows.append(dict(key=key, publisher=pub, dataset=dataset, page_url=url,
                     backs_payload=backs, status=status,
                     pdf='evidence/api/publisher_pages/%s.pdf' % key if ok_pdf else '',
                     png='evidence/api/publisher_pages/%s.png' % key if ok_png else '',
                     pdf_bytes=os.path.getsize(pdf) if ok_pdf else 0,
                     png_bytes=os.path.getsize(png) if ok_png else 0,
                     captured=ACCESS))
    print('%-42s %-16s pdf:%-7s png:%-7s' % (
        key, status, '%dK' % (os.path.getsize(pdf) // 1024) if ok_pdf else 'FAIL',
        '%dK' % (os.path.getsize(png) // 1024) if ok_png else 'FAIL'))
    sys.stdout.flush()

df = pd.DataFrame(rows)
df.to_csv(os.path.join(SITE, 'data', 'api_publisher_snapshots.csv'), index=False, encoding='utf-8-sig')
print('\ncaptured %d of %d publisher pages' % ((df.status == 'captured').sum(), len(df)))
