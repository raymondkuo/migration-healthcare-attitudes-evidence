# -*- coding: utf-8 -*-
"""Build the final, quality-judged panel from the two input workbooks plus the
verification evidence collected in verification/ and countries/."""
import os, json, datetime
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VER = os.path.join(BASE, 'verification')
RAW = os.path.join(BASE, 'data_raw')
F1 = os.path.join(BASE, 'immigration_country_year_2010_2022.xlsx')
F2 = os.path.join(BASE, 'migration_population_panel_40countries_2010-2022.xlsx')
ACCESS = '2026-08-17'

pn = pd.read_excel(F2, sheet_name='Panel')
cy = pd.read_excel(F1, sheet_name='Country-Year Data')
lg = pd.read_excel(F2, sheet_name='Long_all_observations')
irr = pd.read_excel(F2, sheet_name='Irregular_estimates')
ctr = pd.read_excel(F2, sheet_name='Countries').dropna(subset=['iso3'])
checks = pd.concat([pd.read_csv(os.path.join(VER, 'value_checks.csv')),
                    pd.read_csv(os.path.join(VER, 'value_checks_oecd.csv'))], ignore_index=True)

corrections = []


def corr(iso3, year, variable, old, new, reason, evidence):
    corrections.append(dict(iso3=iso3, year=year, variable=variable, old_value=old,
                            new_value=new, reason=reason, evidence=evidence))


# =====================================================================
# Start from FILE2's Panel: it separates the three irregular measures,
# carries an audit trail, and verified exactly on 2,415 of 2,454 values.
# =====================================================================
fin = pn.copy()

# ---------------------------------------------------------------------
# CORRECTION 1 - Eurostat detections were shifted one year for CHE/PRT/SWE
# ---------------------------------------------------------------------
def load_jsonstat(fn, fixed=None):
    d = json.load(open(os.path.join(RAW, fn), encoding='utf-8'))
    ids, size = d['id'], d['size']
    idx = {k: d['dimension'][k]['category']['index'] for k in ids}
    strides = [1] * len(size)
    for i in range(len(size) - 2, -1, -1):
        strides[i] = strides[i + 1] * size[i + 1]
    gi, ti = ids.index('geo'), ids.index('time')
    base = sum(idx[k][v] * strides[ids.index(k)] for k, v in (fixed or {}).items())
    ig = {v: k for k, v in idx['geo'].items()}
    it = {v: k for k, v in idx['time'].items()}
    out = {}
    for g in range(size[gi]):
        for t in range(size[ti]):
            v = d['value'].get(str(base + g * strides[gi] + t * strides[ti]))
            if v is not None:
                out[(ig[g], int(it[t]))] = v
    return out


det = load_jsonstat('eurostat_migr_eipre.json', fixed={'reason': 'TOTAL', 'apprehen': 'TOTAL'})
iso2 = ctr.set_index('iso3')['iso2'].to_dict()
iso2['GBR'] = 'UK'

EV_EUROSTAT = ('Eurostat migr_eipre re-queried 2026-08-17 (reason=TOTAL, apprehen=TOTAL, '
               'citizen=TOTAL); see data_raw/eurostat_migr_eipre.json')
for iso3 in ['CHE', 'PRT', 'SWE']:
    for y in range(2010, 2023):
        live = det.get((iso2[iso3], y))
        m = (fin.iso3 == iso3) & (fin.year == y)
        old = fin.loc[m, 'irregular_proxy_detections'].iloc[0]
        if live is not None and (pd.isna(old) or abs(float(old) - float(live)) > 0.5):
            fin.loc[m, 'irregular_proxy_detections'] = live
            corr(iso3, y, 'irregular_proxy_detections', old, live,
                 'Series was offset by one year: the input workbook carried the Eurostat value '
                 'for year Y+1 under year Y. Replaced with the correct year-aligned value.',
                 EV_EUROSTAT)

# ---------------------------------------------------------------------
# CORRECTION 2 - Italy: use the official ISMU series for the whole period
# ---------------------------------------------------------------------
ITA_ISMU = {2010: 454000, 2011: 443000, 2012: 326000, 2013: 294000, 2014: 350000,
            2015: 404000, 2016: 435000, 2017: 491000, 2018: 533000, 2019: 562000,
            2020: 517000, 2021: 519000}
EV_ISMU = ('Fondazione ISMU, "Stime stranieri irregolari ISMU 1991-2021" (agg. maggio 2022); '
           'countries/ITA_Italy/sources/irregular_stock__ISMU_Stime_irregolari_1991_2021_agg_maggio2022.xls')
for y, v in ITA_ISMU.items():
    m = (fin.iso3 == 'ITA') & (fin.year == y)
    old = fin.loc[m, 'irregular_stock'].iloc[0]
    if pd.isna(old) or abs(float(old) - v) > 0.5:
        why = ('Value absent from the input workbook; added from the official ISMU series.'
               if pd.isna(old) else
               'Input used the Pew Research estimate for this year while every other year in the '
               'series used ISMU. Replaced with ISMU so the Italian series has one consistent method.')
        fin.loc[m, 'irregular_stock'] = v
        fin.loc[m, 'irregular_stock_source'] = 'Fondazione ISMU, Stime stranieri irregolari 1991-2021 (agg. maggio 2022)'
        fin.loc[m, 'irregular_stock_url'] = 'https://test.ismu.org/wp-content/uploads/2022/11/Stime-irregolari-ISMU_1991_2021_agg_maggio-2022.xls'
        fin.loc[m, 'irregular_stock_ref_date'] = '1 January'
        fin.loc[m, 'irregular_stock_note'] = 'ISMU estimate of irregularly present foreigners, stock at 1 January.'
        corr('ITA', y, 'irregular_stock', old, v, why, EV_ISMU)

# ---------------------------------------------------------------------
# CORRECTION 3 - Taiwan: the overstayer column mixed two different measures.
#   Split them: NIA overstayers (逾期停留/居留) vs MOL absconded workers (失聯移工).
# ---------------------------------------------------------------------
fin['tw_note'] = ''
TWN_NIA = {2012: 66696, 2013: 69929, 2014: 68998, 2015: 77422, 2016: 79392,
           2017: 79909, 2018: 89965, 2019: 83465, 2020: 86061, 2021: 81538}
EV_TWN = ('Legislative Yuan Budget Center reports citing National Immigration Agency data; '
          'countries/TWN_Taiwan/sources/ (S11 2019 report, S12 2021 report). '
          'Cross-checked against immigration_country_year_2010_2022.xlsx, which carries the '
          'same NIA series consistently for 2012-2021.')
fin['irregular_proxy_absconded_workers'] = np.nan
for y in range(2010, 2023):
    m = (fin.iso3 == 'TWN') & (fin.year == y)
    old = fin.loc[m, 'irregular_proxy_overstayers'].iloc[0]
    src = str(fin.loc[m, 'irregular_proxy_overstayers_source'].iloc[0])
    if pd.notna(old) and ('Ministry of Labor' in src or '失聯' in src):
        fin.loc[m, 'irregular_proxy_absconded_workers'] = old   # move MOL figure aside
        fin.loc[m, 'irregular_proxy_overstayers'] = np.nan
    new = TWN_NIA.get(y)
    if new is not None:
        prev = fin.loc[m, 'irregular_proxy_overstayers'].iloc[0]
        if pd.isna(prev) or abs(float(prev) - new) > 0.5:
            fin.loc[m, 'irregular_proxy_overstayers'] = new
            fin.loc[m, 'irregular_proxy_overstayers_source'] = \
                'National Immigration Agency (內政部移民署), via Legislative Yuan Budget Center reports'
            fin.loc[m, 'irregular_proxy_overstayers_ref_date'] = '31 December'
            fin.loc[m, 'irregular_proxy_overstayers_note'] = \
                'Overstaying foreign nationals (逾期停留 + 逾期居留), administrative register count.'
            corr('TWN', y, 'irregular_proxy_overstayers', old if pd.notna(old) else np.nan, new,
                 'The input column mixed two incompatible Taiwanese measures across years: MOL '
                 'absconded migrant workers (失聯移工, a subset) for 2011-2013 and 2019-2022, and '
                 'NIA overstayers (逾期停留/居留) for 2014-2018, producing spurious jumps in 2014 '
                 'and 2019. The column now holds only the NIA overstayer measure; the MOL figures '
                 'were moved to irregular_proxy_absconded_workers.', EV_TWN)
fin.drop(columns=['tw_note'], inplace=True)

# ---------------------------------------------------------------------
# ADDITION - UN WPP 2024 population as a second, fully comparable series
# ---------------------------------------------------------------------
wpp = cy[['ISO3', 'Year', 'Population_total_persons']].rename(
    columns={'ISO3': 'iso3', 'Year': 'year', 'Population_total_persons': 'population_un_wpp2024'})
fin = fin.merge(wpp, on=['iso3', 'year'], how='left')
fin['population_wb_vs_unwpp_pct'] = (fin['population'] - fin['population_un_wpp2024']) / \
                                    fin['population_un_wpp2024'] * 100

# ---------------------------------------------------------------------
# recompute derived shares after the corrections
# ---------------------------------------------------------------------
for v in ['foreign_born', 'foreign_nationals', 'irregular_stock']:
    fin[v + '_pct_pop'] = fin[v] / fin['population']
fin['irregular_proxy_overstayers_pct_pop'] = fin['irregular_proxy_overstayers'] / fin['population']
fin['irregular_proxy_detections_per_1000_pop'] = fin['irregular_proxy_detections'] / fin['population'] * 1000

CORR = pd.DataFrame(corrections)
CORR.to_csv(os.path.join(VER, 'corrections_applied.csv'), index=False, encoding='utf-8-sig')
print('corrections applied: %d' % len(CORR))
print(CORR.groupby(['iso3', 'variable']).size().to_string())
fin.to_pickle(os.path.join(VER, '_final_panel.pkl'))
print('\nfinal panel: %d rows x %d cols' % fin.shape)
