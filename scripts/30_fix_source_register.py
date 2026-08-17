# -*- coding: utf-8 -*-
"""The source register's local_file column was carried from the first download pass,
so it is empty for sources that were recovered or substituted later. Repair it and
record the retrieval outcome explicitly."""
import os
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(BASE, 'migration-data-archive')
EV = os.path.join(SITE, 'evidence', 'countries')

# url -> (iso3, filename actually archived, outcome, explanation)
FIX = {
 'https://www.pewresearch.org/hispanic/2020/08/20/facts-on-u-s-immigrants/':
   ('USA', 'irregular__PewResearch_2020_facts-on-us-immigrants.html', 'RECOVERED',
    'Refused the first request; retrieved with a full browser header set.'),
 'https://mexico.iom.int/sites/g/files/tmzbdl1686/files/documents/2024-03/estadisticas-migratorias-2023.pdf':
   ('MEX', 'irregular_proxy_detections__UPMRIP_SEGOB_boletin_2023.pdf', 'RECOVERED',
    'Refused the first request; retrieved with a full browser header set.'),
 'https://www.gov.il/BlobFolder/generalpage/foreign_workers_stats/he/zarim_2022_q1.pdf':
   ('ISR', 'irregular_stock__PIBA_zarim_2022_q1.pdf', 'RECOVERED',
    'Refused the first request; retrieved with a full browser header set.'),
 'https://psa.gov.ph/content/foreign-citizens-country-2020-census-population-and-housing':
   ('PHL', 'foreign_nationals__PSA_2020CPH_foreign_citizens_SCREENSHOT.jpg', 'RECOVERED_SCREENSHOT',
    'A bot check blocks scripted clients. Captured in an interactive browser: the page states '
    '78,396 foreign citizens in 2020, matching the workbook exactly.'),
 'https://www.moj.go.kr/moj/2415/subview.do':
   ('KOR', 'irregular__MOJ_illegal_stay_table_2021_2025_SCREENSHOT.jpg', 'RECOVERED_SCREENSHOT',
    'The table is rendered by JavaScript. Captured in an interactive browser: '
    '2021 = 125,022 + 262,251 + 1,427 = 388,700 and 2022 = 138,013 + 269,532 + 3,725 = 411,270, '
    'both matching the workbook exactly.'),
 'https://www.ismu.org/comunicato-stampa-xxv-rapporto-ismu/':
   ('ITA', 'irregular_stock__ISMU_Stime_irregolari_1991_2021_agg_maggio2022.xls', 'SUBSTITUTED',
    'ismu.org returns HTTP 403 to every client, including a real browser. Replaced by ISMU\'s own '
    'published series, which confirms the 2019 value of 562,000.'),
 'https://www.ismu.org/xxvii-rapporto-sulle-migrazioni-2021-comunicato-stampa-11-2-2022/':
   ('ITA', 'irregular_stock__ISMU_Stime_irregolari_1991_2021_agg_maggio2022.xls', 'SUBSTITUTED',
    'ismu.org returns HTTP 403 to every client. Replaced by ISMU\'s own published series, which '
    'confirms the 2021 value of 519,000.'),
 'https://www.cinformi.it/Comunicazione/Notizie/I-dati-del-Rapporto-ISMU-sulle-migrazioni-2020':
   ('ITA', 'irregular_stock__ISMU_Stime_irregolari_1991_2021_agg_maggio2022.xls', 'SUBSTITUTED',
    'Host unreachable. Replaced by ISMU\'s own published series, which confirms the 2020 value '
    'of 517,000.'),
 'https://www.sem.admin.ch/dam/sem/de/data/internationales/illegale-migration/sans_papiers/ber-sanspapiers-2015-d.pdf':
   ('CHE', 'irregular_stock__SRF_SEM_76000_sanspapiers_CORROBORATION.html', 'SUBSTITUTED',
    'Link rot: the SEM PDF now returns 404. The 76,000 estimate is corroborated by SRF reporting '
    'on the SEM study release of 25 April 2016. The study\'s own range was 58,000-105,000.'),
 'https://press.police.ac.kr/pds/1476878914562.pdf':
   ('KOR', '', 'NOT_RETRIEVED',
    'The host does not respond and no web-archive copy was available. This is the only source for '
    'Korea 2010-2015 overstayers, so those six values are graded D.'),
 'https://www.nisshinkyo.org/news/pdf/G-26-2.pdf':
   ('JPN', '', 'NOT_RETRIEVED_REDUNDANT',
    'HTTP 404. No impact: it duplicated an Immigration Services Agency figure for 2014 whose '
    'primary ISA source was retrieved successfully.'),
}

p = os.path.join(SITE, 'data', 'source_register.csv')
reg = pd.read_csv(p)
if 'outcome' not in reg.columns:
    reg['outcome'] = ''
reg['note'] = reg.get('note', '').fillna('') if 'note' in reg.columns else ''

fixed = 0
for i, r in reg.iterrows():
    url = str(r['source_url'])
    if r['retrieval'] == 'VERIFIED_API':
        reg.at[i, 'outcome'] = 'VERIFIED_API'
        continue
    if url in FIX:
        iso, fn, outcome, note = FIX[url]
        if fn and os.path.exists(os.path.join(EV, r['iso3'], fn)):
            reg.at[i, 'local_file'] = fn
            fixed += 1
        reg.at[i, 'outcome'] = outcome
        reg.at[i, 'note'] = note
        reg.at[i, 'retrieval'] = 'ARCHIVED' if fn else 'NOT_RETRIEVED'
    else:
        lf = str(r.get('local_file') or '')
        ok = lf and lf != 'nan' and os.path.exists(os.path.join(EV, r['iso3'], lf))
        reg.at[i, 'outcome'] = 'DOWNLOADED' if ok else 'CHECK'
        reg.at[i, 'retrieval'] = 'ARCHIVED' if ok else r['retrieval']

reg.to_csv(p, index=False, encoding='utf-8-sig')

d = reg[reg.retrieval != 'VERIFIED_API'].drop_duplicates(['iso3', 'source_url'])
n_ok = int((d.outcome != 'NOT_RETRIEVED').sum() - (d.outcome == 'NOT_RETRIEVED_REDUNDANT').sum())
print('repaired local_file on %d rows' % fixed)
print('distinct country x document source: %d' % len(d))
print('  archived                        : %d' % (d.local_file.astype(str).ne('nan') &
                                                  d.local_file.astype(str).ne('')).sum())
print('  not retrievable                 : %d' % d.outcome.astype(str).str.startswith('NOT_RETRIEVED').sum())
print()
print(d.outcome.value_counts().to_string())
