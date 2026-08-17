# -*- coding: utf-8 -*-
"""Create one folder per country and write the per-country source manifest
(the download plan). Downloading itself is done by 06_download_sources.py."""
import os, re, hashlib
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F1 = os.path.join(BASE, 'immigration_country_year_2010_2022.xlsx')
F2 = os.path.join(BASE, 'migration_population_panel_40countries_2010-2022.xlsx')
CDIR = os.path.join(BASE, 'countries')
os.makedirs(CDIR, exist_ok=True)

countries = pd.read_excel(F2, sheet_name='Countries').dropna(subset=['iso3'])
countries = countries[['country', 'iso3', 'iso2', 'm49_code']].drop_duplicates('iso3')


def slug(s):
    return re.sub(r'[^A-Za-z0-9]+', '_', str(s)).strip('_')


folders = {}
for _, r in countries.iterrows():
    name = '%s_%s' % (r['iso3'], slug(r['country']))
    p = os.path.join(CDIR, name)
    os.makedirs(os.path.join(p, 'sources'), exist_ok=True)
    folders[r['iso3']] = p
print('created %d country folders' % len(folders))

# ---- gather every (country, variable, source, url) pair from both workbooks ----
rows = []

cy = pd.read_excel(F1, sheet_name='Country-Year Data')
s1 = pd.read_excel(F1, sheet_name='Sources')
smap = {r['Source_ID']: r for _, r in s1.iterrows()}
for var, idc, urlc in [('population', 'Population_source_id', 'Population_source_url'),
                       ('foreign_born', 'Immigrant_source_id', 'Immigrant_source_url'),
                       ('irregular', 'Illegal_source_id', 'Illegal_source_url')]:
    sub = cy[cy[idc].notna()]
    for (iso3, sid, url), g in sub.groupby(['ISO3', idc, urlc]):
        s = smap.get(sid, {})
        rows.append(dict(iso3=iso3, workbook='FILE1', variable=var, source_id=sid,
                         source_name=s.get('Title', ''), source_url=url,
                         landing_url=s.get('Landing_URL', ''),
                         years='%d-%d' % (g['Year'].min(), g['Year'].max()), n_obs=len(g)))

lg = pd.read_excel(F2, sheet_name='Long_all_observations')
for (iso3, var, name, url), g in lg.groupby(['iso3', 'variable', 'source_name', 'source_url'], dropna=False):
    rows.append(dict(iso3=iso3, workbook='FILE2', variable=var, source_id='',
                     source_name=name, source_url=url, landing_url='',
                     years='%d-%d' % (g['year'].min(), g['year'].max()), n_obs=len(g)))

ir = pd.read_excel(F2, sheet_name='Irregular_estimates')
seen = {(r['iso3'], r['source_url']) for r in rows}
for (iso3, var, name, url), g in ir.groupby(['iso3', 'variable', 'source_name', 'source_url'], dropna=False):
    if (iso3, url) in seen:
        continue
    rows.append(dict(iso3=iso3, workbook='FILE2-IRR', variable=var, source_id='',
                     source_name=name, source_url=url, landing_url='',
                     years='%d-%d' % (g['year'].min(), g['year'].max()), n_obs=len(g)))

man = pd.DataFrame(rows)
man['source_url'] = man['source_url'].astype(str)

# classify: bulk API sources are stored once in data_raw/ and extracted per country;
# document sources get downloaded into the country folder.
BULK = ('api.worldbank.org', 'population.un.org', 'ec.europa.eu/eurostat/api',
        'ec.europa.eu/eurostat/databrowser', 'sdmx.oecd.org',
        'un.org/development/desa/pd/sites')
man['kind'] = man['source_url'].map(lambda u: 'bulk_api' if any(b in u for b in BULK) else 'document')
man['url_id'] = man['source_url'].map(lambda u: hashlib.md5(u.encode('utf-8')).hexdigest()[:10])
man['folder'] = man['iso3'].map(folders)

man.to_csv(os.path.join(BASE, 'verification', 'country_source_manifest.csv'),
           index=False, encoding='utf-8-sig')

print('\nmanifest rows: %d' % len(man))
print(man.groupby('kind').agg(rows=('iso3', 'size'), urls=('source_url', 'nunique')).to_string())
print('\ndocument URLs to download: %d (distinct)' % man[man.kind == 'document']['source_url'].nunique())
print('\ncountries with no document source:',
      sorted(set(folders) - set(man[man.kind == 'document']['iso3'])))
