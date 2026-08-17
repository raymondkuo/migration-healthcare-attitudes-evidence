# -*- coding: utf-8 -*-
"""Create the GitHub Pages archive folder, export every dataset as a downloadable
file, mirror all evidence, and checksum everything."""
import os, re, shutil, hashlib, json
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(BASE, 'migration-data-archive')
XLSX = os.path.join(BASE, 'FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx')
VER = os.path.join(BASE, 'verification')
RAW = os.path.join(BASE, 'data_raw')
CDIR = os.path.join(BASE, 'countries')

for d in ['', 'assets', 'data', 'evidence', 'evidence/api', 'evidence/countries',
          'countries', 'manifest', 'verification']:
    os.makedirs(os.path.join(SITE, d), exist_ok=True)

# ---------------------------------------------------------------- 1. datasets
print('== exporting workbook sheets ==')
xl = pd.ExcelFile(XLSX)
SHEET_FILE = {}
for sh in xl.sheet_names:
    df = pd.read_excel(XLSX, sheet_name=sh)
    fn = re.sub(r'[^a-z0-9]+', '_', sh.lower()).strip('_') + '.csv'
    df.to_csv(os.path.join(SITE, 'data', fn), index=False, encoding='utf-8-sig')
    SHEET_FILE[sh] = fn
    print('   %-26s -> data/%-28s %5d rows' % (sh, fn, len(df)))

shutil.copy2(XLSX, os.path.join(SITE, 'data', os.path.basename(XLSX)))
for f in ['sources_catalog.csv', 'value_checks.csv', 'value_checks_oecd.csv',
          'country_source_manifest.csv', 'download_log.csv', 'audit_issues.csv',
          'corrections_applied.csv', 'country_package_summary.csv']:
    p = os.path.join(VER, f)
    if os.path.exists(p):
        shutil.copy2(p, os.path.join(SITE, 'verification', f))
for f in ['VERIFICATION_REPORT.md']:
    p = os.path.join(BASE, f)
    if os.path.exists(p):
        shutil.copy2(p, os.path.join(SITE, f))

# the two original input workbooks, for provenance
os.makedirs(os.path.join(SITE, 'data', 'original_inputs'), exist_ok=True)
for f in ['immigration_country_year_2010_2022.xlsx',
          'migration_population_panel_40countries_2010-2022.xlsx']:
    shutil.copy2(os.path.join(BASE, f), os.path.join(SITE, 'data', 'original_inputs', f))

# ---------------------------------------------------------------- 2. API snapshots
print('\n== mirroring API / bulk snapshots ==')
API_DESC = {
    'wb_SP_POP_TOTL.json': ('World Bank WDI', 'Total population (SP.POP.TOTL), all countries 2010-2022',
                            'https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json&date=2010:2022&per_page=20000'),
    'wb_SM_POP_TOTL.json': ('World Bank WDI', 'International migrant stock (SM.POP.TOTL), all countries 2010-2022',
                            'https://api.worldbank.org/v2/country/all/indicator/SM.POP.TOTL?format=json&date=2010:2022&per_page=20000'),
    'eurostat_migr_pop3ctb.json': ('Eurostat', 'Population by country of birth, foreign-born (migr_pop3ctb), 1 Jan, 2010-2022',
                                   'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/migr_pop3ctb?format=JSON&lang=EN&age=TOTAL&sex=T&unit=NR&c_birth=FOR&sinceTimePeriod=2010&untilTimePeriod=2022'),
    'eurostat_migr_pop1ctz.json': ('Eurostat', 'Population by citizenship, foreign + stateless (migr_pop1ctz), 1 Jan, 2010-2022',
                                   'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/migr_pop1ctz?format=JSON&lang=EN&age=TOTAL&sex=T&unit=NR&citizen=FOR_STLS&sinceTimePeriod=2010&untilTimePeriod=2022'),
    'eurostat_migr_eipre.json': ('Eurostat', 'Third-country nationals found illegally present (migr_eipre), annual, 2010-2022',
                                 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/migr_eipre?format=JSON&lang=EN&age=TOTAL&sex=T&unit=PER&citizen=TOTAL&sinceTimePeriod=2010&untilTimePeriod=2022'),
    'eurostat_migr_eipre_CH_PT_SE_2010_2023.json': ('Eurostat', 'migr_eipre for CH/PT/SE extended to 2023 - the evidence for the one-year offset correction',
                                                    'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/migr_eipre?format=JSON&lang=EN&age=TOTAL&sex=T&unit=PER&citizen=TOTAL&reason=TOTAL&apprehen=TOTAL&geo=CH&geo=PT&geo=SE&sinceTimePeriod=2010&untilTimePeriod=2023'),
    'UN_WPP2024_demographic_indicators_compact.xlsx': ('UN DESA', 'World Population Prospects 2024, compact demographic indicators',
                                                       'https://population.un.org/wpp/assets/Excel%20Files/1_Indicator%20(Standard)/EXCEL_FILES/1_General/WPP2024_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT.xlsx'),
    'UN_DESA_IMS2024_stock_by_sex_and_destination.xlsx': ('UN DESA', 'International Migrant Stock 2024, stock by sex and destination',
                                                          'https://www.un.org/development/desa/pd/sites/www.un.org.development.desa.pd/files/undesa_pd_2024_ims_stock_by_sex_and_destination.xlsx'),
}
api_rows = []
for f in sorted(os.listdir(RAW)):
    src = os.path.join(RAW, f)
    if os.path.isdir(src):
        continue
    shutil.copy2(src, os.path.join(SITE, 'evidence', 'api', f))
    pub, desc, url = API_DESC.get(f, ('', '', ''))
    api_rows.append(dict(file=f, publisher=pub, description=desc, query_url=url,
                         bytes=os.path.getsize(src), path='evidence/api/' + f))
    print('   %-52s %10s bytes' % (f, f'{os.path.getsize(src):,}'))

# OECD SDMX responses.
# The exact query URL for each series is recovered from the source workbook's audit
# trail rather than reconstructed, so no placeholder or wildcard can be published.
OECD_REAL_URL = {}
_lg = pd.read_excel(os.path.join(BASE, 'migration_population_panel_40countries_2010-2022.xlsx'),
                    sheet_name='Long_all_observations')
for _u in sorted({str(x) for x in _lg.source_url if 'sdmx.oecd.org' in str(x)}):
    _m = re.search(r'/([A-Z]{3})\.W\.A\.(B1[45])\.', _u)
    if _m:
        OECD_REAL_URL['oecd/%s_%s.json' % (_m.group(1), _m.group(2))] = _u

oecd_dir = os.path.join(RAW, 'oecd')
if os.path.isdir(oecd_dir):
    os.makedirs(os.path.join(SITE, 'evidence', 'api', 'oecd'), exist_ok=True)
    for f in sorted(os.listdir(oecd_dir)):
        shutil.copy2(os.path.join(oecd_dir, f), os.path.join(SITE, 'evidence', 'api', 'oecd', f))
        iso, meas = f.replace('.json', '').split('_')
        api_rows.append(dict(
            file='oecd/' + f, publisher='OECD',
            description='International Migration Database, %s, measure %s (%s)'
                        % (iso, meas, 'foreign-born stock' if meas == 'B14' else 'foreign-national stock'),
            query_url=OECD_REAL_URL.get('oecd/%s' % f, ''),
            bytes=os.path.getsize(os.path.join(oecd_dir, f)), path='evidence/api/oecd/' + f))
    print('   oecd/  %d SDMX responses' % len(os.listdir(oecd_dir)))

pd.DataFrame(api_rows).to_csv(os.path.join(SITE, 'data', 'api_snapshots.csv'),
                              index=False, encoding='utf-8-sig')

# ---------------------------------------------------------------- 3. country evidence
print('\n== mirroring country source files ==')
n_files = 0
for d in sorted(os.listdir(CDIR)):
    p = os.path.join(CDIR, d)
    if not os.path.isdir(p):
        continue
    iso3 = d.split('_')[0]
    dst = os.path.join(SITE, 'evidence', 'countries', iso3)
    os.makedirs(dst, exist_ok=True)
    sdir = os.path.join(p, 'sources')
    if os.path.isdir(sdir):
        for f in os.listdir(sdir):
            shutil.copy2(os.path.join(sdir, f), os.path.join(dst, f))
            n_files += 1
    for f in ['README.md', 'data_from_source.csv', 'value_check.csv', 'source_manifest.csv']:
        s = os.path.join(p, f)
        if os.path.exists(s):
            shutil.copy2(s, os.path.join(dst, f))
print('   %d source files mirrored across 40 countries' % n_files)

# ---------------------------------------------------------------- 4. checksums
print('\n== checksums ==')
rows = []
for root, _, files in os.walk(SITE):
    if 'manifest' in os.path.relpath(root, SITE).split(os.sep):
        continue
    for f in files:
        fp = os.path.join(root, f)
        rel = os.path.relpath(fp, SITE).replace('\\', '/')
        h = hashlib.sha256()
        with open(fp, 'rb') as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b''):
                h.update(chunk)
        rows.append(dict(path=rel, bytes=os.path.getsize(fp), sha256=h.hexdigest()))
ck = pd.DataFrame(rows).sort_values('path')
ck.to_csv(os.path.join(SITE, 'manifest', 'checksums.csv'), index=False, encoding='utf-8-sig')
print('   %d files, %.1f MB total' % (len(ck), ck.bytes.sum() / 1e6))

open(os.path.join(SITE, '.nojekyll'), 'w').close()
json.dump({'sheet_files': SHEET_FILE}, open(os.path.join(SITE, 'manifest', 'sheets.json'), 'w'), indent=1)
print('\nsite folder:', SITE)
