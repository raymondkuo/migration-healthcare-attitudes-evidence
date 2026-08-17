# -*- coding: utf-8 -*-
"""For every country folder write:
   - data_from_source.csv   the country's observations with the live-source check result
   - source_manifest.csv    every cited source, its retrieval status and local file
   - README.md              a short human-readable verification note
"""
import os, re, json
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VER = os.path.join(BASE, 'verification')
CDIR = os.path.join(BASE, 'countries')
F1 = os.path.join(BASE, 'immigration_country_year_2010_2022.xlsx')
F2 = os.path.join(BASE, 'migration_population_panel_40countries_2010-2022.xlsx')

checks = pd.concat([pd.read_csv(os.path.join(VER, 'value_checks.csv')),
                    pd.read_csv(os.path.join(VER, 'value_checks_oecd.csv'))], ignore_index=True)
man = pd.read_csv(os.path.join(VER, 'country_source_manifest.csv'))
dl = pd.read_csv(os.path.join(VER, 'download_log.csv'))
lg = pd.read_excel(F2, sheet_name='Long_all_observations')
cy = pd.read_excel(F1, sheet_name='Country-Year Data')

# --- manual recovery record for sources the plain downloader could not fetch ---
RECOVERY = {
    'https://www.pewresearch.org/hispanic/2020/08/20/facts-on-u-s-immigrants/':
        ('RECOVERED', 'irregular__PewResearch_2020_facts-on-us-immigrants.html',
         'Retrieved with full browser headers.'),
    'https://mexico.iom.int/sites/g/files/tmzbdl1686/files/documents/2024-03/estadisticas-migratorias-2023.pdf':
        ('RECOVERED', 'irregular_proxy_detections__UPMRIP_SEGOB_boletin_2023.pdf',
         'Retrieved with full browser headers.'),
    'https://www.gov.il/BlobFolder/generalpage/foreign_workers_stats/he/zarim_2022_q1.pdf':
        ('RECOVERED', 'irregular_stock__PIBA_zarim_2022_q1.pdf',
         'Retrieved with full browser headers.'),
    'https://psa.gov.ph/content/foreign-citizens-country-2020-census-population-and-housing':
        ('RECOVERED_SCREENSHOT', 'foreign_nationals__PSA_2020CPH_foreign_citizens_SCREENSHOT.jpg',
         'Bot-check blocks scripted clients; captured in browser. Page states 78,396 foreign '
         'citizens in 2020, matching the workbook exactly.'),
    'https://www.moj.go.kr/moj/2415/subview.do':
        ('RECOVERED_SCREENSHOT', 'irregular__MOJ_illegal_stay_table_2021_2025_SCREENSHOT.jpg',
         'Table is rendered by JavaScript. Captured in browser: 2021 = 125,022+262,251+1,427 = '
         '388,700 and 2022 = 138,013+269,532+3,725 = 411,270, matching the workbook exactly.'),
    'https://www.ismu.org/comunicato-stampa-xxv-rapporto-ismu/':
        ('SUBSTITUTED', 'irregular_stock__ISMU_Stime_irregolari_1991_2021_agg_maggio2022.xls',
         'ismu.org blocks all clients (HTTP 403). Replaced by ISMU\'s own published series '
         '"Stime stranieri irregolari ISMU 1991-2021", which confirms 2019 = 562,000.'),
    'https://www.ismu.org/xxvii-rapporto-sulle-migrazioni-2021-comunicato-stampa-11-2-2022/':
        ('SUBSTITUTED', 'irregular_stock__ISMU_Stime_irregolari_1991_2021_agg_maggio2022.xls',
         'ismu.org blocks all clients (HTTP 403). ISMU series confirms 2021 = 519,000; the 2022 '
         'value of 506,000 is corroborated by the XXVIII Rapporto coverage.'),
    'https://www.cinformi.it/Comunicazione/Notizie/I-dati-del-Rapporto-ISMU-sulle-migrazioni-2020':
        ('SUBSTITUTED', 'irregular_stock__ISMU_Stime_irregolari_1991_2021_agg_maggio2022.xls',
         'Host unreachable. ISMU series confirms 2020 = 517,000.'),
    'https://www.sem.admin.ch/dam/sem/de/data/internationales/illegale-migration/sans_papiers/ber-sanspapiers-2015-d.pdf':
        ('SUBSTITUTED', 'irregular_stock__SRF_SEM_76000_sanspapiers_CORROBORATION.html',
         'LINK ROT: the SEM PDF now returns 404 (site restructured). The 76,000 estimate is '
         'corroborated by SRF reporting on the SEM study release of 25 April 2016.'),
    'https://press.police.ac.kr/pds/1476878914562.pdf':
        ('NOT_RETRIEVED', '',
         'Host does not respond. This secondary source is the sole basis for Korea 2010-2015 '
         'overstayers; those six values could not be checked against any source.'),
    'https://www.nisshinkyo.org/news/pdf/G-26-2.pdf':
        ('NOT_RETRIEVED_REDUNDANT', '',
         'HTTP 404. Redundant: it duplicates the Immigration Services Agency figure for 2014, '
         'and the primary ISA source was retrieved successfully.'),
}

dl_by_url = {r['source_url']: r for _, r in dl.iterrows()}
summary_rows = []

for folder in sorted(os.listdir(CDIR)):
    p = os.path.join(CDIR, folder)
    if not os.path.isdir(p):
        continue
    iso3 = folder.split('_')[0]
    files = os.listdir(os.path.join(p, 'sources')) if os.path.isdir(os.path.join(p, 'sources')) else []

    # ---------- data + check ----------
    c = checks[checks.iso3 == iso3].copy()
    obs = lg[lg.iso3 == iso3][['year', 'variable', 'value', 'source_name', 'source_url', 'notes',
                               'used_in_panel']].copy()
    obs.insert(0, 'iso3', iso3)
    key = c.set_index(['year', 'variable'])['status'].to_dict() if len(c) else {}

    def vstat(r):
        v = r['variable']
        v = {'foreign_born': 'foreign_born', 'population': 'population',
             'foreign_nationals': 'foreign_nationals',
             'irregular_proxy_detections': 'irregular_detections'}.get(v, v)
        return key.get((r['year'], v), 'not_machine_checkable')

    if len(obs):
        obs['live_source_check'] = obs.apply(vstat, axis=1)
        obs.sort_values(['variable', 'year']).to_csv(
            os.path.join(p, 'data_from_source.csv'), index=False, encoding='utf-8-sig')
    if len(c):
        c.sort_values(['variable', 'year']).to_csv(
            os.path.join(p, 'value_check.csv'), index=False, encoding='utf-8-sig')

    # ---------- manifest ----------
    rows = []
    for _, r in man[man.iso3 == iso3].iterrows():
        url = str(r['source_url'])
        if r['kind'] == 'bulk_api':
            st, lf, note = 'VERIFIED_API', '(see ../../data_raw/)', \
                'Bulk machine-readable source; re-queried live and compared value by value.'
        elif url in RECOVERY:
            st, lf, note = RECOVERY[url]
        else:
            d = dl_by_url.get(url)
            if d is not None and str(d['http_status']) in ('200', 'cached') and str(d.get('local_file', '')):
                st, lf, note = 'DOWNLOADED', d['local_file'], ''
            else:
                st, lf, note = 'FAILED', '', 'HTTP %s' % (d['http_status'] if d is not None else '?')
        rows.append(dict(iso3=iso3, variable=r['variable'], years=r['years'], n_obs=r['n_obs'],
                         workbook=r['workbook'], source_name=r['source_name'], source_url=url,
                         retrieval_status=st, local_file=lf, note=note))
    mf = pd.DataFrame(rows)
    if len(mf):
        mf.to_csv(os.path.join(p, 'source_manifest.csv'), index=False, encoding='utf-8-sig')

    # ---------- README ----------
    nchk = len(c)
    nexact = int((c['status'] == 'EXACT').sum()) if nchk else 0
    nbad = int((~c['status'].isin(['EXACT'])).sum()) if nchk else 0
    docs = mf[mf.retrieval_status != 'VERIFIED_API'] if len(mf) else pd.DataFrame()
    got = int(docs['retrieval_status'].isin(
        ['DOWNLOADED', 'RECOVERED', 'RECOVERED_SCREENSHOT', 'SUBSTITUTED']).sum()) if len(docs) else 0

    L = ['# %s — source verification' % folder.split('_', 1)[1].replace('_', ' '),
         '', 'ISO3: **%s**   Verified: 2026-08-17' % iso3, '',
         '## Machine-readable sources', '',
         '- Values re-queried live and compared: **%d**' % nchk,
         '- Exact match: **%d**' % nexact,
         '- Discrepancies: **%d**' % nbad, '']
    if nbad:
        L.append('### Discrepancies found')
        L.append('')
        L.append('| year | variable | workbook | live source | diff |')
        L.append('|---|---|---|---|---|')
        for _, r in c[~c['status'].isin(['EXACT'])].sort_values('year').iterrows():
            L.append('| %d | %s | %s | %s | %s |' % (
                r['year'], r['variable'], f"{r['workbook_value']:,.0f}",
                f"{r['live_source_value']:,.0f}" if pd.notna(r['live_source_value']) else 'n/a',
                f"{r['diff']:,.0f}" if pd.notna(r['diff']) else 'n/a'))
        L.append('')
    L += ['## Document sources', '',
          '- Cited document sources: **%d**' % len(docs),
          '- Retrieved into `sources/`: **%d**' % got, '']
    if len(docs):
        L.append('| variable | years | status | file | source |')
        L.append('|---|---|---|---|---|')
        for _, r in docs.iterrows():
            L.append('| %s | %s | %s | %s | %s |' % (
                r['variable'], r['years'], r['retrieval_status'],
                ('`%s`' % r['local_file']) if r['local_file'] else '—',
                str(r['source_name'])[:80]))
        L.append('')
        notes = docs[docs['note'].astype(str).str.len() > 3]
        if len(notes):
            L.append('### Notes')
            L.append('')
            for _, r in notes.iterrows():
                L.append('- **%s** — %s' % (r['retrieval_status'], r['note']))
            L.append('')
    L += ['## Files in this folder', '',
          '- `data_from_source.csv` — every observation for this country with its live-source check',
          '- `value_check.csv` — workbook value vs live source value, where machine-checkable',
          '- `source_manifest.csv` — every cited source and how it was retrieved',
          '- `sources/` — the downloaded source documents and screenshots', '']
    open(os.path.join(p, 'README.md'), 'w', encoding='utf-8').write('\n'.join(L))

    summary_rows.append(dict(iso3=iso3, folder=folder, values_checked=nchk, exact=nexact,
                             discrepancies=nbad, doc_sources=len(docs), doc_retrieved=got,
                             files_in_sources=len(files)))

s = pd.DataFrame(summary_rows)
s.to_csv(os.path.join(VER, 'country_package_summary.csv'), index=False, encoding='utf-8-sig')
print(s.to_string(index=False))
print()
print('TOTAL values checked %d | exact %d | discrepancies %d' %
      (s.values_checked.sum(), s.exact.sum(), s.discrepancies.sum()))
print('TOTAL document sources %d | retrieved %d' % (s.doc_sources.sum(), s.doc_retrieved.sum()))
