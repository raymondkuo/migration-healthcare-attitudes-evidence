# -*- coding: utf-8 -*-
"""Verify every workbook value that comes from a machine-readable source against a
fresh download of that source. Produces verification/value_checks.csv."""
import os, json, math
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, 'data_raw')
OUT = os.path.join(BASE, 'verification')
F1 = os.path.join(BASE, 'immigration_country_year_2010_2022.xlsx')
F2 = os.path.join(BASE, 'migration_population_panel_40countries_2010-2022.xlsx')

checks = []


def add(wb, country, iso3, year, variable, source_tag, wb_value, src_value, note=''):
    if src_value is None or (isinstance(src_value, float) and math.isnan(src_value)):
        status, diff, pct = 'SOURCE_MISSING', None, None
    else:
        diff = float(wb_value) - float(src_value)
        pct = diff / float(src_value) * 100 if src_value else None
        if abs(diff) < 0.5:
            status = 'EXACT'
        elif pct is not None and abs(pct) < 0.05:
            status = 'ROUNDING'
        elif pct is not None and abs(pct) < 1.0:
            status = 'MINOR_DIFF'
        else:
            status = 'MISMATCH'
    checks.append(dict(workbook=wb, country=country, iso3=iso3, year=year, variable=variable,
                       source=source_tag, workbook_value=wb_value, live_source_value=src_value,
                       diff=diff, pct_diff=pct, status=status, note=note))


# ---------------------------------------------------------------- World Bank
def load_wb(fn):
    d = json.load(open(os.path.join(RAW, fn), encoding='utf-8'))
    out = {}
    for rec in d[1]:
        if rec['value'] is not None:
            out[(rec['countryiso3code'], int(rec['date']))] = rec['value']
    return out


wb_pop = load_wb('wb_SP_POP_TOTL.json')
wb_mig = load_wb('wb_SM_POP_TOTL.json')

# ---------------------------------------------------------------- Eurostat
def load_jsonstat(fn, fixed=None):
    """Return {(geo, year): value}; `fixed` pins extra dimensions to a category id."""
    d = json.load(open(os.path.join(RAW, fn), encoding='utf-8'))
    ids, size = d['id'], d['size']
    idx = {k: d['dimension'][k]['category']['index'] for k in ids}
    # position of each fixed dim
    strides = [1] * len(size)
    for i in range(len(size) - 2, -1, -1):
        strides[i] = strides[i + 1] * size[i + 1]
    geo_i, time_i = ids.index('geo'), ids.index('time')
    fixed = fixed or {}
    base = 0
    for k, v in fixed.items():
        base += idx[k][v] * strides[ids.index(k)]
    out = {}
    inv_geo = {v: k for k, v in idx['geo'].items()}
    inv_time = {v: k for k, v in idx['time'].items()}
    for g in range(size[geo_i]):
        for t in range(size[time_i]):
            pos = base + g * strides[geo_i] + t * strides[time_i]
            v = d['value'].get(str(pos))
            if v is not None:
                out[(inv_geo[g], int(inv_time[t]))] = v
    return out


es_fb = load_jsonstat('eurostat_migr_pop3ctb.json')
es_fn = load_jsonstat('eurostat_migr_pop1ctz.json')
es_det = load_jsonstat('eurostat_migr_eipre.json', fixed={'reason': 'TOTAL', 'apprehen': 'TOTAL'})

# ---------------------------------------------------------------- UN WPP 2024
wpp = pd.read_excel(os.path.join(RAW, 'UN_WPP2024_demographic_indicators_compact.xlsx'),
                    sheet_name='Estimates', skiprows=16)
wpp.columns = [str(c).strip() for c in wpp.columns]
popcol = [c for c in wpp.columns if c.startswith('Total Population, as of 1 July')][0]
isocol = [c for c in wpp.columns if 'ISO3' in c][0]
yrcol = [c for c in wpp.columns if c == 'Year'][0]
wpp = wpp[wpp[isocol].notna()]
wpp_map = {}
for _, r in wpp.iterrows():
    try:
        wpp_map[(r[isocol], int(r[yrcol]))] = float(r[popcol]) * 1000.0
    except Exception:
        pass

# ---------------------------------------------------------------- UN DESA IMS 2024
# Table 1 is keyed on M49 "Location code"; the year columns repeat for both sexes /
# male / female, so only the first block (both sexes) is kept.
ims_path = os.path.join(RAW, 'UN_DESA_IMS2024_stock_by_sex_and_destination.xlsx')
t = pd.read_excel(ims_path, sheet_name='Table 1', header=None, skiprows=10)
hdr = [str(x).strip().replace('.0', '') for x in t.iloc[0]]
t = t.iloc[1:]
t.columns = hdr
loc_c = hdr[hdr.index('Location code')]
yearcols, seen = {}, set()
for i, c in enumerate(hdr):
    if c.isdigit() and 1990 <= int(c) <= 2024 and int(c) not in seen:
        seen.add(int(c))
        yearcols[int(c)] = i
ims_map = {}
for _, r in t.iterrows():
    try:
        m49 = int(r[hdr.index('Location code')] if False else r[loc_c])
    except Exception:
        continue
    for y, i in yearcols.items():
        try:
            ims_map[(m49, y)] = float(r.iloc[i])
        except Exception:
            pass
# ISO3 -> M49 from the workbooks themselves
m49_by_iso3 = pd.read_excel(F2, sheet_name='Countries').dropna(subset=['m49_code']) \
    .set_index('iso3')['m49_code'].astype(int).to_dict()
print('loaded refs: WB pop %d, WB mig %d, ES fb %d, ES fn %d, ES det %d, WPP %d, IMS %d'
      % (len(wb_pop), len(wb_mig), len(es_fb), len(es_fn), len(es_det), len(wpp_map), len(ims_map)))

# ================================================================ FILE 1
cy = pd.read_excel(F1, sheet_name='Country-Year Data')
for _, r in cy.iterrows():
    iso3, y = r['ISO3'], int(r['Year'])
    if pd.notna(r['Population_total_persons']):
        add('FILE1', r['Country'], iso3, y, 'population', 'S1 UN WPP2024',
            r['Population_total_persons'], wpp_map.get((iso3, y)))
    if pd.notna(r['Immigrant_stock_total_persons']):
        add('FILE1', r['Country'], iso3, y, 'foreign_born', 'S2 UN DESA IMS2024',
            r['Immigrant_stock_total_persons'], ims_map.get((m49_by_iso3.get(iso3), y)))
    if pd.notna(r['Illegal_immigrants_number']) and r['Illegal_source_id'] == 'S3':
        add('FILE1', r['Country'], iso3, y, 'irregular_detections', 'S3 Eurostat migr_eipre',
            r['Illegal_immigrants_number'], es_det.get((r['ISO2'], y)))

# ================================================================ FILE 2
lg = pd.read_excel(F2, sheet_name='Long_all_observations')
iso2map = pd.read_excel(F2, sheet_name='Countries').set_index('iso3')['iso2'].to_dict()
iso2map['GBR'] = 'UK'   # Eurostat uses UK
iso2map['GRC'] = 'EL'

for _, r in lg.iterrows():
    iso3, y, var, val = r['iso3'], int(r['year']), r['variable'], r['value']
    src = str(r['source_name'])
    url = str(r['source_url'])
    g2 = iso2map.get(iso3, '')
    if pd.isna(val):
        continue
    if 'SP.POP.TOTL' in url or 'SP.POP.TOTL' in src:
        add('FILE2', r['country'], iso3, y, 'population', 'World Bank SP.POP.TOTL',
            val, wb_pop.get((iso3, y)))
    elif 'SM.POP.TOTL' in url or 'SM.POP.TOTL' in src:
        add('FILE2', r['country'], iso3, y, 'foreign_born', 'World Bank SM.POP.TOTL',
            val, wb_mig.get((iso3, y)))
    elif 'migr_pop3ctb' in url:
        add('FILE2', r['country'], iso3, y, 'foreign_born', 'Eurostat migr_pop3ctb',
            val, es_fb.get((g2, y)))
    elif 'migr_pop1ctz' in url:
        add('FILE2', r['country'], iso3, y, 'foreign_nationals', 'Eurostat migr_pop1ctz',
            val, es_fn.get((g2, y)))
    elif 'migr_eipre' in url:
        add('FILE2', r['country'], iso3, y, 'irregular_detections', 'Eurostat migr_eipre',
            val, es_det.get((g2, y)))

df = pd.DataFrame(checks)
df.to_csv(os.path.join(OUT, 'value_checks.csv'), index=False, encoding='utf-8-sig')
print('\nchecked %d values' % len(df))
print(df.groupby(['workbook', 'source', 'status']).size().to_string())
