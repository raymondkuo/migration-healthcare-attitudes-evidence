# -*- coding: utf-8 -*-
"""Download the bulk / machine-readable reference datasets used by both workbooks."""
import os, sys, json, time, urllib.request, urllib.error, ssl

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, 'data_raw')
os.makedirs(RAW, exist_ok=True)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'


def get(url, dest, timeout=180):
    if os.path.exists(dest) and os.path.getsize(dest) > 500:
        return 'cached', os.path.getsize(dest)
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*'})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            data = r.read()
        with open(dest, 'wb') as f:
            f.write(data)
        return 'ok', len(data)
    except Exception as e:
        return 'FAIL: %s' % e, 0


TARGETS = [
    # --- World Bank ---
    ('wb_SP_POP_TOTL.json',
     'https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json&date=2010:2022&per_page=20000'),
    ('wb_SM_POP_TOTL.json',
     'https://api.worldbank.org/v2/country/all/indicator/SM.POP.TOTL?format=json&date=2010:2022&per_page=20000'),
    # --- Eurostat full datasets (all geos at once) ---
    ('eurostat_migr_pop3ctb.json',
     'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/migr_pop3ctb?format=JSON&lang=EN&age=TOTAL&sex=T&unit=NR&c_birth=FOR&sinceTimePeriod=2010&untilTimePeriod=2022'),
    ('eurostat_migr_pop1ctz.json',
     'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/migr_pop1ctz?format=JSON&lang=EN&age=TOTAL&sex=T&unit=NR&citizen=FOR_STLS&sinceTimePeriod=2010&untilTimePeriod=2022'),
    ('eurostat_migr_eipre.json',
     'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/migr_eipre?format=JSON&lang=EN&age=TOTAL&sex=T&unit=PER&citizen=TOTAL&sinceTimePeriod=2010&untilTimePeriod=2022'),
    # --- UN DESA ---
    ('UN_WPP2024_demographic_indicators_compact.xlsx',
     'https://population.un.org/wpp/assets/Excel%20Files/1_Indicator%20(Standard)/EXCEL_FILES/1_General/WPP2024_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT.xlsx'),
    ('UN_DESA_IMS2024_stock_by_sex_and_destination.xlsx',
     'https://www.un.org/development/desa/pd/sites/www.un.org.development.desa.pd/files/undesa_pd_2024_ims_stock_by_sex_and_destination.xlsx'),
]

for name, url in TARGETS:
    dest = os.path.join(RAW, name)
    t0 = time.time()
    status, n = get(url, dest)
    print('%-52s %-10s %10s bytes  %5.1fs' % (name, status[:10], f'{n:,}', time.time() - t0))
    sys.stdout.flush()
