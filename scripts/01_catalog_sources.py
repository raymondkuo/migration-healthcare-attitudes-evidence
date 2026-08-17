# -*- coding: utf-8 -*-
"""Extract every distinct source referenced by the two workbooks into one catalog."""
import pandas as pd, os, sys, re, hashlib

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F1 = os.path.join(BASE, 'immigration_country_year_2010_2022.xlsx')
F2 = os.path.join(BASE, 'migration_population_panel_40countries_2010-2022.xlsx')
OUT = os.path.join(BASE, 'verification')
os.makedirs(OUT, exist_ok=True)

rows = []

# ---------- File 1 ----------
cy = pd.read_excel(F1, sheet_name='Country-Year Data')
src1 = pd.read_excel(F1, sheet_name='Sources')
if 'Source_ID' not in src1.columns:
    src1.columns = src1.iloc[0]
    src1 = src1[1:].reset_index(drop=True)
src_map = {r['Source_ID']: r for _, r in src1.iterrows()}

for var, idcol, urlcol in [('population', 'Population_source_id', 'Population_source_url'),
                           ('foreign_born', 'Immigrant_source_id', 'Immigrant_source_url'),
                           ('irregular', 'Illegal_source_id', 'Illegal_source_url')]:
    sub = cy[cy[idcol].notna()]
    for (sid, url), g in sub.groupby([idcol, urlcol]):
        s = src_map.get(sid, {})
        rows.append(dict(workbook='FILE1', source_key=sid, variable=var,
                         source_name=s.get('Title', ''), source_url=url,
                         landing_url=s.get('Landing_URL', ''),
                         citation=s.get('Citation', ''),
                         n_obs=len(g), n_countries=g['ISO3'].nunique(),
                         iso3_list=';'.join(sorted(g['ISO3'].unique())),
                         year_min=int(g['Year'].min()), year_max=int(g['Year'].max())))

# ---------- File 2 ----------
lg = pd.read_excel(F2, sheet_name='Long_all_observations')
for (name, url, var), g in lg.groupby(['source_name', 'source_url', 'variable'], dropna=False):
    rows.append(dict(workbook='FILE2', source_key='', variable=var,
                     source_name=name, source_url=url, landing_url='', citation='',
                     n_obs=len(g), n_countries=g['iso3'].nunique(),
                     iso3_list=';'.join(sorted(g['iso3'].astype(str).unique())),
                     year_min=int(g['year'].min()), year_max=int(g['year'].max())))

# Irregular_estimates may carry sources not in Long_all_observations
ir = pd.read_excel(F2, sheet_name='Irregular_estimates')
known = {(r['source_name'], r['source_url']) for r in rows if r['workbook'] == 'FILE2'}
for (name, url, var), g in ir.groupby(['source_name', 'source_url', 'variable'], dropna=False):
    if (name, url) in known:
        continue
    rows.append(dict(workbook='FILE2-IRR', source_key='', variable=var,
                     source_name=name, source_url=url, landing_url='', citation='',
                     n_obs=len(g), n_countries=g['iso3'].nunique(),
                     iso3_list=';'.join(sorted(g['iso3'].astype(str).unique())),
                     year_min=int(g['year'].min()), year_max=int(g['year'].max())))

cat = pd.DataFrame(rows)
cat['url_id'] = cat['source_url'].fillna('').map(lambda u: hashlib.md5(u.encode('utf-8')).hexdigest()[:8])


def host(u):
    m = re.match(r'https?://([^/]+)', str(u))
    return m.group(1).lower() if m else ''


cat['host'] = cat['source_url'].map(host)
cat = cat.sort_values(['workbook', 'variable', 'n_obs'], ascending=[True, True, False])
cat.to_csv(os.path.join(OUT, 'sources_catalog.csv'), index=False, encoding='utf-8-sig')

print('total source rows:', len(cat))
print('distinct URLs     :', cat['source_url'].nunique())
print('distinct hosts    :', cat['host'].nunique())
print()
print(cat.groupby('host').agg(urls=('source_url', 'nunique'), obs=('n_obs', 'sum')).sort_values('obs', ascending=False).to_string())
