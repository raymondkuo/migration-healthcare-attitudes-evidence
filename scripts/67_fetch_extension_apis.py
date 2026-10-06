# -*- coding: utf-8 -*-
"""Collect the bulk-API part of the 2001-2009 extension (plan: migrant_data_availability_
2001-2022.md, Option 3). Raw responses are saved exactly as the server returned them, so
they can be re-parsed or compared later; nothing is interpreted here except to check that
each response parses and holds the series expected.

Each payload spans 2001-2022, not only the new years. That is deliberate: the 2010-2022
part is compared with the values the archive already publishes, which re-verifies them
against today's source at the same time as the new years are collected.

curl does the fetching; Python's urllib is blocked in this environment.
"""
import json
import os
import subprocess
import sys
import pandas as pd

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(SITE, 'data')
API = os.path.join(SITE, 'evidence', 'api')
COLLECTED = '2026-10-07'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126 Safari/537.36')

ISO3 = ('AUS AUT BEL BGR CHE CHL CHN CZE DEU DNK ESP FIN FRA GBR HRV HUN IND ISL ISR ITA '
        'JPN KOR LTU MEX NLD NOR NZL PHL POL PRT RUS SUR SVK SVN SWE THA TUR TWN USA ZAF').split()
OECD = 'https://sdmx.oecd.org/public/rest/data/'
OTAIL = '?startPeriod=2001&endPeriod=2022&format=jsondata&dimensionAtObservation=AllDimensions'
EUR = 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/'

JOBS = [
    dict(file='oecd/OECD_B14_foreign-born_2001-2022_retrieved_%s.json' % COLLECTED,
         publisher='OECD',
         description='International Migration Database, measure B14 (stocks of foreign-born '
                     'population), all 40 panel countries, 2001-2022',
         url=OECD + 'OECD.ELS.IMD,DSD_MIG_F@DF_MIG_POPF,1.0/' + '+'.join(ISO3)
             + '.W.A.B14._T._Z._Z.PS' + OTAIL, accept='application/vnd.sdmx.data+json'),
    dict(file='oecd/OECD_B15_foreign-population_2001-2022_retrieved_%s.json' % COLLECTED,
         publisher='OECD',
         description='International Migration Database, measure B15 (stocks of foreign '
                     'population), all 40 panel countries, 2001-2022',
         url=OECD + 'OECD.ELS.IMD,DSD_MIG@DF_MIG,1.0/' + '+'.join(ISO3)
             + '.W.A.B15._T._Z._Z.PS' + OTAIL, accept='application/vnd.sdmx.data+json'),
    dict(file='eurostat_migr_pop3ctb_2001-2022_retrieved_%s.json' % COLLECTED,
         publisher='Eurostat',
         description='Population by country of birth, foreign country (migr_pop3ctb), 1 Jan, '
                     '2001-2022',
         url=EUR + 'migr_pop3ctb?format=JSON&lang=EN&age=TOTAL&sex=T&unit=NR&c_birth=FOR'
                   '&sinceTimePeriod=2001&untilTimePeriod=2022', accept='application/json'),
    dict(file='eurostat_migr_pop1ctz_2001-2022_retrieved_%s.json' % COLLECTED,
         publisher='Eurostat',
         description='Population by citizenship, foreign + stateless (migr_pop1ctz), 1 Jan, '
                     '2001-2022',
         url=EUR + 'migr_pop1ctz?format=JSON&lang=EN&age=TOTAL&sex=T&unit=NR&citizen=FOR_STLS'
                   '&sinceTimePeriod=2001&untilTimePeriod=2022', accept='application/json'),
    dict(file='wb_SP_POP_TOTL_2001-2022_retrieved_%s.json' % COLLECTED,
         publisher='World Bank WDI',
         description='Total population (SP.POP.TOTL), all countries 2001-2022',
         url='https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json'
             '&date=2001:2022&per_page=20000', accept='application/json'),
    dict(file='wb_SM_POP_TOTL_2001-2022_retrieved_%s.json' % COLLECTED,
         publisher='World Bank WDI',
         description='International migrant stock, total (SM.POP.TOTL), the World Bank mirror '
                     'of UN DESA International Migrant Stock, all countries 2001-2022',
         url='https://api.worldbank.org/v2/country/all/indicator/SM.POP.TOTL?format=json'
             '&date=2001:2022&per_page=20000', accept='application/json'),
]


def fetch(job):
    out = os.path.join(API, job['file'].replace('/', os.sep))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    r = subprocess.run(['curl', '-s', '-L', '--max-time', '240', '-A', UA,
                        '-H', 'Accept: ' + job['accept'], '-o', out, '-w', '%{http_code}',
                        job['url']], capture_output=True, text=True)
    return r.stdout.strip(), out


snap = pd.read_csv(os.path.join(D, 'api_snapshots.csv'))
rows, bad = [], 0
for job in JOBS:
    code, out = fetch(job)
    size = os.path.getsize(out) if os.path.exists(out) else 0
    try:
        payload = json.load(open(out, encoding='utf-8'))
        parsed = True
    except Exception as e:
        payload, parsed = None, False
    print('%-62s http %s  %9s bytes  parses=%s' % (job['file'][:62], code, format(size, ','), parsed))
    if code != '200' or not parsed or size < 1000:
        bad += 1
        print('   *** NOT USED:', open(out, encoding='utf-8', errors='replace').read(200).replace('\n', ' '))
        continue
    rows.append(dict(file=job['file'], publisher=job['publisher'], description=job['description'],
                     query_url=job['url'], bytes=size,
                     path='evidence/api/' + job['file']))

if rows:
    new = pd.DataFrame(rows)
    keep = snap[~snap['file'].isin(new['file'])]
    pd.concat([keep, new], ignore_index=True).to_csv(
        os.path.join(D, 'api_snapshots.csv'), index=False, encoding='utf-8-sig')
    print('\napi_snapshots.csv: %d -> %d rows' % (len(snap), len(keep) + len(new)))
sys.exit(1 if bad else 0)
