# -*- coding: utf-8 -*-
"""Population for 2001-2009, and the UN DESA 2005 migrant-stock benchmark.

Population is collected only because the share columns (foreign_born as a % of population,
and so on) need a denominator; it is not itself the subject of the extension. Two series, as
in the published panel:
  population             World Bank SP.POP.TOTL (39 countries; Taiwan has its own collector)
  population_un_wpp2024  UN WPP 2024, read from the workbook already archived

The UN DESA 2005 benchmark comes from the World Bank SM.POP.TOTL mirror, because that is the
mirror the published 2010/2015/2020 cells were read from; all 27 of those cells reproduce
exactly from it, so 2005 is on the same UN revision. It is added only where
  (a) the country's published foreign_born series already relies on UN DESA, so the new year
      extends a series that exists; or
  (b) no annual source reaches before 2009 at all (Bulgaria, Croatia), so the benchmark is the
      only early information there is.
It is NOT added for countries with annual Eurostat/OECD series: UN DESA diverges sharply from
those (Turkey +144%, Czechia +55%, Slovakia +42%), and putting an estimate that far off into an
otherwise annual series would mislead anyone who does not filter by source type.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ext_lib as L                                    # noqa: E402

SITE = os.path.dirname(HERE)
D = os.path.join(SITE, 'data')
STAGE = os.path.join(D, 'extension_staging')
COLLECTED = L.COLLECTED
P = L.baseline_panel()   # the panel as it stood before the extension
SNAP = pd.read_csv(os.path.join(D, 'api_snapshots.csv')).set_index('file')
ISO = sorted(P.iso3.unique())


def r0(v):
    return int(np.floor(float(v) + 0.5))


rows = []

# ------------------------------------------------------------------ World Bank population
wb = L.parse_worldbank(L.WB_POP)
ex = P[(P.iso3 == 'AUT') & (P.year == 2012)].iloc[0]
same = diff = 0
for r in P.itertuples():
    if r.iso3 == 'TWN':
        continue
    v = wb.get((r.iso3, int(r.year)))
    if v is not None:
        same += (r.population == r0(v[0]))
        diff += (r.population != r0(v[0]))
print('World Bank population, published 2010-2022 cells re-checked: %d identical, %d different'
      % (same, diff))
wb_same, wb_diff = same, diff
for iso in ISO:
    if iso == 'TWN':
        continue
    for y in range(2001, 2010):
        v = wb.get((iso, y))
        if v is None:
            print('   no World Bank population for %s %d' % (iso, y))
            continue
        rows.append(dict(
            iso3=iso, year=y, variable='population', value=r0(v[0]), source_id='WB_SP_POP_TOTL',
            source_name=ex.population_source, source_url=ex.population_url,
            local_file='evidence/api/' + L.WB_POP, ref_date='Mid-year', grade='A',
            source_type='annual', flag='', note='',
            verification='Read directly from the archived API response (evidence/api/%s); '
                         'retrieved %s.' % (L.WB_POP, COLLECTED), collected_on=COLLECTED))

# ------------------------------------------------------------------ UN WPP 2024 population
f = os.path.join(SITE, 'evidence', 'api', 'UN_WPP2024_demographic_indicators_compact.xlsx')
w = pd.read_excel(f, 'Estimates', header=16)
w = w[w['ISO3 Alpha-code'].notna()]
col = [c for c in w.columns if str(c).startswith('Total Population, as of 1 July')][0]
wpp = {(r['ISO3 Alpha-code'], int(r['Year'])): float(r[col]) * 1000 for _, r in w.iterrows()}
same = diff = 0
for r in P.itertuples():
    v = wpp.get((r.iso3, int(r.year)))
    if v is not None:
        same += (r.population_un_wpp2024 == r0(v))
        diff += (r.population_un_wpp2024 != r0(v))
print('UN WPP population, published 2010-2022 cells re-checked: %d identical, %d different'
      % (same, diff))
wpp_same, wpp_diff = same, diff
for iso in ISO:
    for y in range(2001, 2010):
        v = wpp.get((iso, y))
        if v is None:
            print('   no UN WPP population for %s %d' % (iso, y))
            continue
        rows.append(dict(
            iso3=iso, year=y, variable='population_un_wpp2024', value=r0(v),
            source_id='UN_WPP2024', source_name='UN DESA Population Division, World Population '
            'Prospects 2024 (compact demographic indicators)',
            source_url=SNAP.loc['UN_WPP2024_demographic_indicators_compact.xlsx', 'query_url'],
            local_file='evidence/api/UN_WPP2024_demographic_indicators_compact.xlsx',
            ref_date='1 July', grade='A', source_type='un_estimate', flag='', note='',
            verification='Read directly from the archived workbook; the 2010-2022 values '
                         'already published reproduce exactly from the same file.',
            collected_on=COLLECTED))

# ------------------------------------------------------------------ UN DESA 2005 benchmark
mig = L.parse_worldbank(L.WB_MIG)
un_ex = P[P.foreign_born_source.astype(str).str.contains('UN DESA', na=False)].iloc[0]
declared_c = {'CHN', 'IND', 'PHL', 'SUR', 'THA'}      # UN DESA data type C for these countries
api = pd.read_csv(os.path.join(STAGE, 'api_migrant_cells.csv'))
have_early = set(api[(api.variable == 'foreign_born') & (api.year < 2009)].iso3)
relies = set(P[P.foreign_born_source.astype(str).str.contains('UN DESA', na=False)].iso3)
targets = sorted(relies | {'BGR', 'HRV'})
print('\nUN DESA 2005 benchmark for foreign_born: %s' % ', '.join(targets))
for iso in targets:
    v = mig.get((iso, 2005))
    if v is None:
        print('   no UN DESA 2005 value for', iso)
        continue
    if iso in ('BGR', 'HRV'):
        assert iso not in have_early, '%s already has early annual data' % iso
    note = ('UN estimate (not annual); mid-year benchmark year only; retrieved from World Bank '
            'mirror of UN DESA International Migrant Stock, retrieved %s.' % COLLECTED)
    if iso in declared_c:
        note += (' UN DESA declares this country\'s stock as based on citizenship (data type C), '
                 'not place of birth; see the known issue on UN DESA data types.')
    if iso in ('BGR', 'HRV'):
        v10 = mig.get((iso, 2010))
        pub = P[(P.iso3 == iso) & P.foreign_born.notna()].sort_values('year').iloc[0]
        if v10:
            note += (' The only early value for this country. UN DESA\'s own 2010 estimate '
                     '(%s) is %+.0f%% against the %d value in this panel (%s), so treat the '
                     'level with caution.'
                     % (format(r0(v10[0]), ','), (v10[0] - pub.foreign_born) / pub.foreign_born * 100,
                        int(pub.year), format(int(pub.foreign_born), ',')))
    rows.append(dict(
        iso3=iso, year=2005, variable='foreign_born', value=r0(v[0]), source_id='UNDESA_fb',
        source_name=un_ex.foreign_born_source, source_url=SNAP.loc[L.WB_MIG, 'query_url'],
        local_file='evidence/api/' + L.WB_MIG, ref_date=str(un_ex.foreign_born_ref_date),
        grade='A', source_type='un_estimate',
        flag='un_estimate' + ('; declared citizenship basis' if iso in declared_c else ''),
        note=note, verification='Read directly from the archived API response '
        '(evidence/api/%s); retrieved %s.' % (L.WB_MIG, COLLECTED), collected_on=COLLECTED))

# ---- the re-verification of published cells against today's responses, for the record
un_same = un_diff = 0
for r in P.itertuples():
    if 'UN DESA' in str(r.foreign_born_source):
        v = mig.get((r.iso3, int(r.year)))
        if v is not None:
            un_same += (r.foreign_born == r0(v[0]))
            un_diff += (r.foreign_born != r0(v[0]))
print('UN DESA (World Bank mirror), published cells re-checked: %d identical, %d different'
      % (un_same, un_diff))
ovp = os.path.join(D, 'extension_overlap_check.csv')
ov = pd.read_csv(ovp)
NAMES = ['World Bank SP.POP.TOTL', 'UN WPP 2024 (compact demographic indicators)',
         'World Bank SM.POP.TOTL (mirror of UN DESA migrant stock)']
ov = ov[~ov.source.isin(NAMES)]
add = pd.DataFrame([
    dict(variable='population', source=NAMES[0], iso3='(all)', cells_compared=wb_same + wb_diff,
         identical=wb_same, different=wb_diff, retrieved=COLLECTED),
    dict(variable='population_un_wpp2024', source=NAMES[1], iso3='(all)',
         cells_compared=wpp_same + wpp_diff, identical=wpp_same, different=wpp_diff,
         retrieved=COLLECTED),
    dict(variable='foreign_born', source=NAMES[2], iso3='(all)', cells_compared=un_same + un_diff,
         identical=un_same, different=un_diff, retrieved=COLLECTED)])
pd.concat([ov, add], ignore_index=True).to_csv(ovp, index=False, encoding='utf-8-sig')

out = pd.DataFrame(rows)
out.to_csv(os.path.join(STAGE, 'api_population_un_cells.csv'), index=False, encoding='utf-8-sig')
print('\ncells written: %d' % len(out))
print(out.groupby(['variable', 'source_id']).size().to_string())
