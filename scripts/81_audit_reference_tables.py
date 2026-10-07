# -*- coding: utf-8 -*-
"""Reference tables that follow from the audit of 2026-10-07 (run after 79_apply_audit_corrections.py).

  F14  irregular_estimates_all.csv gets a status for every record (current, valid alternative,
       rejected, superseded, reclassified, deleted, component). The Chile alternatives are
       rebuilt with the right years and methodologies; Taiwan's foreign-national component of the
       overstay total and the 31 July 2019 absconded-worker figure are added as alternatives.
  F15  every country's data_from_source.csv: used_in_panel is recomputed from the current panel,
       historical_status says why a record is no longer used, and every current panel value that
       had no row (the extension, the corrected and the added values) gets one.
  F21  the source register's data_raw/ placeholders become the exact archived files; rows for the
       corrected and added cells are written; the country READMEs stop describing a sources/
       subfolder that never existed here and say what data_from_source.csv now holds.

Idempotent.
"""
import os
import re
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SITE = os.path.dirname(HERE)
D = os.path.join(SITE, 'data')
EV = os.path.join(SITE, 'evidence', 'countries')
WHEN = '2026-10-07'
panel = pd.read_csv(os.path.join(D, 'panel_final.csv'))
pi = panel.set_index(['iso3', 'year'])
audit = pd.read_csv(os.path.join(D, 'audit_changes_%s.csv' % WHEN))
name_of = dict(zip(panel.iso3, panel.country))
VARS = ['population', 'foreign_born', 'foreign_nationals', 'irregular_stock', 'irregular_proxy_overstayers',
        'irregular_proxy_detections', 'irregular_proxy_absconded_workers']

# ================================================================== F14  irregular_estimates_all.csv
alt = pd.read_csv(os.path.join(D, 'irregular_estimates_all.csv'))
for c in ('status', 'status_reason'):
    if c in alt.columns:
        alt = alt.drop(columns=c)
old_chl = alt[(alt.iso3 == 'CHL') & (alt.year == 2022) & alt.source_name.str.contains('press release')].copy()
alt = alt[~(alt.iso3 == 'CHL')]
alt = alt[alt.estimate_rank_in_cell != 'ALTERNATIVE - COMPONENT (foreign nationals only)']
alt = alt[~alt.estimate_rank_in_cell.astype(str).str.startswith('ALTERNATIVE - 31 July')]
CHL_URL = pi.loc[('CHL', 2018), 'irregular_stock_url']
M2023 = {2018: 10375, 2019: 21833, 2020: 53356, 2021: 109846, 2022: 291149}
M2022 = {2018: 5975, 2019: 14818, 2020: 27162, 2021: 59682, 2022: 115059}
pop = lambda iso, y: float(pi.loc[(iso, y), 'population'])
rows = []
for y in range(2018, 2023):
    base = dict(country='Chile', iso3='CHL', year=y, variable='irregular_stock', source_url=CHL_URL)
    rows.append(dict(base, value=M2023[y], value_pct_pop=M2023[y] / pop('CHL', y), estimate_rank_in_cell='PANEL PRIMARY',
                     source_name=pi.loc[('CHL', y), 'irregular_stock_source'],
                     notes='Revised 2023 methodology (adds Mineduc school-enrolment and SERMIG biometric '
                           'registration records). Chart on page 12 of the Sintesis 2023, year axis checked.'))
    rows.append(dict(base, value=M2022[y], value_pct_pop=M2022[y] / pop('CHL', y), estimate_rank_in_cell='alternative 1',
                     source_name='Instituto Nacional de Estadisticas (INE) and Servicio Nacional de Migraciones '
                                 '(SERMIG), Estimacion de Personas Extranjeras Residentes Habituales en Chile 2023 - '
                                 'Sintesis, page 12 (2022 methodology series)',
                     notes='Same chart, 2022 methodology (blue series). The first release had these chart values '
                           'under other years.'))
if len(old_chl):
    r = old_chl.iloc[0].to_dict()
    r.update(estimate_rank_in_cell='alternative 2')
    rows.append(r)
# Taiwan: the foreign-national component of the overstay total (2012-2018) and the 31 July 2019 stock
LY1 = 'https://www.ly.gov.tw/Pages/Detail.aspx?nodeid=33342&pid=184411'
FN = {2012: 63181, 2013: 64728, 2014: 65711, 2015: 74088, 2016: 76027, 2017: 76493, 2018: 86585}
for y, v in FN.items():
    rows.append(dict(country='Taiwan', iso3='TWN', year=y, variable='irregular_proxy_overstayers', value=v,
                     value_pct_pop=v / pop('TWN', y), estimate_rank_in_cell='ALTERNATIVE - COMPONENT (foreign nationals only)',
                     source_name='National Immigration Agency, as tabulated in the Legislative Yuan Budget Center report of '
                                 'July 2019 (附表11, 外國人 column)',
                     source_url=LY1,
                     notes='The foreign-national component of the overstay total in the panel (which covers all '
                           'categories). Use it if the intended universe is foreign nationals only.'))
rows.append(dict(country='Taiwan', iso3='TWN', year=2019, variable='irregular_proxy_absconded_workers', value=47632,
                 value_pct_pop=47632 / pop('TWN', 2019),
                 estimate_rank_in_cell='ALTERNATIVE - 31 July stock (not year-end)',
                 source_name='National Immigration Agency / Ministry of Labor (失聯移工), reported by the Legislative Yuan '
                             'Budget Center, October 2019',
                 source_url='https://www.ly.gov.tw/Pages/Detail.aspx?nodeid=33580&pid=188916',
                 notes='Stock at 31 July 2019. Held in the panel until %s; replaced by the Ministry of Labor year-end '
                       'stock (48,491) so the column is year-end throughout.' % WHEN))
alt = pd.concat([alt, pd.DataFrame(rows)], ignore_index=True)
alt['value_pct_pop'] = alt.value_pct_pop.astype(float)

colmap = {'irregular_stock': 'irregular_stock', 'irregular_proxy_overstayers': 'irregular_proxy_overstayers',
          'irregular_proxy_detections': 'irregular_proxy_detections', 'foreign_nationals': 'foreign_nationals',
          'irregular_proxy_absconded_workers': 'irregular_proxy_absconded_workers'}
audit_idx = {(r.iso3, int(r.year), r.variable): r for r in audit.itertuples()}


def status(r):
    iso, y, var, val, rank = r.iso3, int(r.year), r.variable, float(r.value), str(r.estimate_rank_in_cell)
    cur = pi.loc[(iso, y), colmap.get(var, var)] if (iso, y) in pi.index else np.nan
    absc = pi.loc[(iso, y), 'irregular_proxy_absconded_workers'] if (iso, y) in pi.index else np.nan
    if rank.startswith('ALTERNATIVE - COMPONENT'):
        return 'component', 'The foreign-national part of a total that is held in the panel; a different universe, not a rival estimate.'
    if rank.startswith('ALTERNATIVE - 31 July'):
        return 'superseded', 'Replaced in the panel by the Ministry of Labor year-end stock.'
    if rank == 'NOT USED - PARTIAL COMPONENT' or rank == 'ALTERNATIVE - EXCLUDED COMPONENT':
        return 'component', 'A partial component, not an estimate of the whole; kept as provenance.'
    if rank == 'PANEL PRIMARY' and pd.notna(cur) and abs(float(cur) - val) <= 1:
        return 'current', 'This is the value held in panel_final.csv.'
    if iso == 'TWN' and var == 'irregular_proxy_overstayers' and pd.notna(absc) and abs(float(absc) - val) <= 1:
        return 'reclassified', ('This is the Ministry of Labor missing-worker count (Table 12-7); it now sits in '
                                'irregular_proxy_absconded_workers, not in the overstay column.')
    if rank.startswith('alternative'):
        return 'valid alternative', 'A competing published estimate for the same quantity, not used in the panel.'
    # a PANEL PRIMARY record that is no longer the panel value
    if var == 'irregular_proxy_detections' and iso in ('CHE', 'PRT', 'SWE'):
        return 'rejected', ('Input error: the Eurostat value for the next year was recorded under this year '
                            '(corrected 2026-08-17; the panel holds the correctly aligned value). Not a valid estimate.')
    if iso == 'ISR' and y == 2020 and var == 'irregular_stock':
        return 'reclassified', 'Tourist overstayers, not a stock of irregular residents; now irregular_proxy_overstayers.'
    if iso == 'ITA' and y == 2014:
        return 'superseded', 'Replaced by 350,000 after the source series was re-read (corrections_applied.csv).'
    if iso == 'KOR' and y == 2015:
        return 'superseded', 'Replaced by 214,168 from the Ministry of Justice open-data series (corrections_applied.csv).'
    if iso == 'RUS' and y == 2020:
        return 'deleted', 'No numeric estimate exists in the archived source; deleted as untraceable (deleted_values.csv).'
    if iso == 'TWN' and var == 'irregular_proxy_overstayers' and pd.notna(absc) and abs(float(absc) - val) <= 1:
        return 'reclassified', ('This is the Ministry of Labor missing-worker count (Table 12-7); it now sits in '
                                'irregular_proxy_absconded_workers, not in the overstay column.')
    if iso == 'TWN' and var == 'irregular_proxy_overstayers' and y in (2011, 2022):
        return 'reclassified', 'Ministry of Labor missing-worker count; it now sits in irregular_proxy_absconded_workers.'
    if iso == 'TWN' and var == 'irregular_proxy_overstayers' and y == 2019 and abs(val - 47632) <= 1:
        return 'reclassified', 'Missing-worker count at 31 July 2019; see the absconded-worker alternatives.'
    return 'unexplained', 'No longer the panel value; reason not recorded.'


st = alt.apply(status, axis=1, result_type='expand')
alt['status'], alt['status_reason'] = st[0], st[1]
assert (alt.status != 'unexplained').all(), alt[alt.status == 'unexplained'][['iso3', 'year', 'variable', 'value']]
alt = alt.sort_values(['iso3', 'variable', 'year', 'status'], kind='stable').reset_index(drop=True)
alt.to_csv(os.path.join(D, 'irregular_estimates_all.csv'), index=False, encoding='utf-8-sig')
print('irregular_estimates_all.csv: %d rows | %s' % (len(alt), alt.status.value_counts().to_dict()))
# the number of estimates per cell counts the usable ones
usable = alt[alt.status.isin(['current', 'valid alternative'])]
n_est = usable[usable.variable == 'irregular_stock'].groupby(['iso3', 'year']).size()
panel2 = pd.read_csv(os.path.join(D, 'panel_final.csv'))
changed = 0
for (iso, y), n in n_est.items():
    m = panel2.index[(panel2.iso3 == iso) & (panel2.year == y)]
    if len(m) and pd.notna(panel2.at[m[0], 'irregular_stock']) and panel2.at[m[0], 'irregular_stock_n_estimates'] != n \
            and iso == 'CHL':
        panel2.at[m[0], 'irregular_stock_n_estimates'] = n
        changed += 1
if changed:
    panel2.to_csv(os.path.join(D, 'panel_final.csv'), index=False, encoding='utf-8-sig')
    print('irregular_stock_n_estimates updated for %d Chile cells' % changed)
    panel = panel2
    pi = panel.set_index(['iso3', 'year'])

# ================================================================== F15  country source tables
def hist_reason(iso, y, var, val, panel_val):
    if var == 'irregular_proxy_detections' and iso in ('CHE', 'PRT', 'SWE'):
        return 'Rejected input error: Eurostat value of the next year recorded under this year; the panel holds the aligned value'
    if iso == 'ITA' and var == 'irregular_stock' and y == 2014:
        return 'Superseded: corrected to 350,000'
    if iso == 'KOR' and var == 'irregular_proxy_overstayers' and y == 2015:
        return 'Superseded: corrected to 214,168'
    if iso == 'ISR' and var == 'irregular_stock' and y == 2020:
        return 'Reclassified: tourist overstayers, now irregular_proxy_overstayers'
    if iso == 'RUS' and var == 'irregular_stock' and y == 2020:
        return 'Deleted: untraceable'
    if iso == 'TWN' and var == 'irregular_proxy_overstayers':
        return ('Reclassified: Ministry of Labor missing-worker count, now irregular_proxy_absconded_workers'
                if y != 2021 else 'Reclassified: Ministry of Labor missing-worker count (55,805); the 81,538 held in the panel until %s was deleted' % WHEN)
    if iso == 'TWN' and var == 'foreign_workers':
        return 'Never a panel variable: Ministry of Labor foreign workers with permits'
    if iso == 'CHL' and var == 'irregular_stock':
        return 'Superseded %s: chart year and methodology assignment corrected (audit F01)' % WHEN
    if iso == 'IND' and var == 'foreign_born' and y == 2011:
        return 'Superseded %s: previous-residence figure replaced by the official birthplace total (audit F02)' % WHEN
    if iso == 'SUR' and var == 'foreign_nationals' and y == 2012:
        return 'Superseded %s: residual with unknown nationality replaced by the known foreign nationalities (audit F03)' % WHEN
    if iso == 'TWN' and var == 'population':
        return 'Superseded %s: rounded NDC figure replaced by the exact MOI total (audit F08)' % WHEN
    return 'Not used in the current panel'


def live_check(ver):
    ver = '' if pd.isna(ver) else str(ver)
    if ver.startswith('Read directly from the archived API'):
        return 'READ FROM ARCHIVED PAYLOAD'
    if ver.startswith('Read directly from the archived CSV'):
        return 'READ FROM ARCHIVED CSV'
    if ver.startswith('Read directly from the official'):
        return 'READ FROM OFFICIAL WORKBOOK'
    if ver:
        return 'CONFIRMED IN ARCHIVED DOCUMENT'
    return ''


total_added = total_off = 0
for f in sorted(os.path.join(EV, i, 'data_from_source.csv') for i in sorted(os.listdir(EV))
                if os.path.exists(os.path.join(EV, i, 'data_from_source.csv'))):
    iso = os.path.basename(os.path.dirname(f))
    d = pd.read_csv(f)
    if 'historical_status' in d.columns:
        d = d.drop(columns='historical_status')
    d = d[d.get('source_name', '').astype(str) != '__current_panel_row__']
    # rows this script added earlier are rebuilt: they carry the marker in the status column
    d['_added'] = False
    was_yes = d.used_in_panel.astype(str).str.lower().eq('yes')
    cur = []
    st_ = []
    for r in d.itertuples():
        pv = pi.loc[(iso, int(r.year)), r.variable] if ((iso, int(r.year)) in pi.index and r.variable in pi.columns) else np.nan
        ok = pd.notna(pv) and abs(float(pv) - float(r.value)) <= 1
        cur.append('yes' if ok else 'no')
        st_.append('current' if ok else (hist_reason(iso, int(r.year), r.variable, r.value, pv) if True else ''))
    d['used_in_panel'] = cur
    d['historical_status'] = st_
    off = int((was_yes & (d.used_in_panel == 'no')).sum())
    # current panel values that have no row
    have = {(int(r.year), r.variable, round(float(r.value))) for r in d.itertuples() if r.used_in_panel == 'yes'}
    add = []
    sub = panel[panel.iso3 == iso]
    for r in sub.itertuples():
        for v in VARS:
            val = getattr(r, v)
            if pd.isna(val):
                continue
            if (int(r.year), v, round(float(val))) in have:
                continue
            add.append(dict(iso3=iso, year=int(r.year), variable=v, value=int(round(float(val))),
                            source_name=getattr(r, v + '_source') if hasattr(r, v + '_source') else '',
                            source_url=getattr(r, v + '_url') if hasattr(r, v + '_url') else '',
                            notes=(getattr(r, v + '_note') if hasattr(r, v + '_note') else '') if v != 'population' else
                                  'Total population; see the source and verification text in panel_final.csv.',
                            used_in_panel='yes',
                            live_source_check=live_check(getattr(r, v + '_verification') if hasattr(r, v + '_verification') else ''),
                            historical_status='current'))
    d = d.drop(columns='_added')
    if add:
        d = pd.concat([d, pd.DataFrame(add)], ignore_index=True)
    d = d.sort_values(['variable', 'year', 'used_in_panel'], ascending=[True, True, False], kind='stable')
    d.to_csv(f, index=False, encoding='utf-8-sig')
    total_added += len(add)
    total_off += off
print('data_from_source.csv: %d rows added across %d countries; %d records that said used_in_panel=yes now say no'
      % (total_added, len(os.listdir(EV)), total_off))

# ================================================================== F21  the source register
reg = pd.read_csv(os.path.join(D, 'source_register.csv')).fillna('')
reg = reg[reg.from_workbook != 'AUDIT']


def route(r):
    s, iso = r.source_name, r.iso3
    if 'World Population Prospects' in s:
        return 'evidence/api/UN_WPP2024_demographic_indicators_compact.xlsx'
    if 'SM.POP.TOTL' in s:
        return 'evidence/api/wb_SM_POP_TOTL.json'
    if 'International Migrant Stock 2024' in s:
        return 'evidence/api/UN_DESA_IMS2024_stock_by_sex_and_destination.xlsx'
    if 'SP.POP.TOTL' in s:
        return 'evidence/api/wb_SP_POP_TOTL.json'
    if 'migr_pop1ctz' in s:
        return 'evidence/api/eurostat_migr_pop1ctz.json'
    if 'migr_pop3ctb' in s:
        return 'evidence/api/eurostat_migr_pop3ctb.json'
    if 'migr_eipre' in s.lower() or 'MIGR_EIPRE' in s:
        return ('evidence/api/eurostat_migr_eipre_CH_PT_SE_2010_2023.json' if iso in ('CHE', 'PRT', 'SWE')
                else 'evidence/api/eurostat_migr_eipre.json')
    m = re.search(r'measure (B14|B15)', s)
    if m:
        return 'evidence/api/oecd/%s_%s.json' % (iso, m.group(1))
    return r.local_file


ph = reg.local_file == 'data_raw/'
reg.loc[ph, 'local_file'] = reg[ph].apply(route, axis=1)
missing = [p_ for p_ in reg[ph].local_file.unique() if not os.path.exists(os.path.join(SITE, p_))]
assert not missing, 'routed to files that do not exist: %s' % missing
print('source_register: %d data_raw/ placeholders routed to %d exact files' % (int(ph.sum()), reg[ph].local_file.nunique()))


def drop(mask):
    global reg
    reg = reg[~mask]


# Chile: one row for the corrected series
drop((reg.iso3 == 'CHL') & (reg.variable == 'irregular_stock') & (reg.from_workbook == 'FILE2') &
     reg.source_name.str.contains('2022 methodology series'))
# India 2011: the official birthplace table replaces the journal article
drop((reg.iso3 == 'IND') & (reg.variable == 'foreign_born') & (reg.years == '2011-2011') & (reg.from_workbook == 'FILE2'))
# Taiwan: missing-worker rows are not overstayers; the 2019-2021 row ends at 2020
t_ = (reg.iso3 == 'TWN') & (reg.variable == 'irregular_proxy_overstayers') & reg.source_name.str.contains('Missing Foreign Workers|失聯移工')
reg.loc[t_, 'variable'] = 'irregular_proxy_absconded_workers'
t2 = (reg.iso3 == 'TWN') & (reg.variable == 'irregular') & (reg.years == '2019-2021')
reg.loc[t2, ['years', 'n_obs']] = ['2019-2020', 2]
reg.loc[t2, 'note'] = ('Legislative Yuan Budget Center report of September 2021, Table 1: totals for 2019 and 2020. '
                       'The 2021 total (81,538) held until %s had no source and was deleted.' % WHEN)
# Iceland detections now include 2021
reg.loc[(reg.iso3 == 'ISL') & (reg.variable == 'irregular_proxy_detections') & (reg.years == '2016-2019'),
        ['years', 'n_obs']] = ['2016-2021', 4]
# Suriname: say what the value is
reg.loc[(reg.iso3 == 'SUR') & (reg.variable == 'foreign_nationals') & (reg.years == '2012-2012'), 'note'] = (
    'Census count; the six foreign nationality categories of Table H2 (page 24) summed, 33,053. The 3,340 persons '
    'of unknown nationality are excluded (audit F03, %s).' % WHEN)
CHL_PDF = 'irregular_stock__f8f04e39ba__www.ine.gob.cl.pdf'
new = [
    dict(iso3='CHL', variable='irregular_stock', years='2018-2022', n_obs=5, source_name=pi.loc[('CHL', 2018), 'irregular_stock_source'],
         source_url=CHL_URL, retrieval='ARCHIVED', local_file=CHL_PDF, outcome='DOWNLOADED',
         note='Chart on page 12, revised 2023 methodology series; the 2022-methodology series is the alternative '
              '(irregular_estimates_all.csv). Years and values corrected %s (audit F01).' % WHEN),
    dict(iso3='IND', variable='foreign_born', years='2011-2011', n_obs=1,
         source_name=pi.loc[('IND', 2011), 'foreign_born_source'], source_url=pi.loc[('IND', 2011), 'foreign_born_url'],
         retrieval='ARCHIVED', local_file='foreign_born__ORGI_Census2011_D01_India__DS-0000-D01-MDDS.xlsx',
         outcome='DOWNLOADED',
         note='Official national row "Born Outside India" of Census 2011 Table D-01 (audit F02, %s).' % WHEN,
         superseded_source_name='Singh D.P. and Biradar R., Migration in India: trends and characteristics, Demography '
                                'India 51(1) 2022 (cited in the first release as Chandrasekhar and Sharma); its Table 2a '
                                'is built on Table D-2, place of last residence',
         superseded_source_url='https://iasp.ac.in/uploads/journal/10.%20Migration%20in%20India%20trends%20and%20characteristics-1669206793.pdf'),
    dict(iso3='AUS', variable='irregular_proxy_overstayers', years='2015-2015', n_obs=1,
         source_name=pi.loc[('AUS', 2015), 'irregular_proxy_overstayers_source'], source_url=pi.loc[('AUS', 2015), 'irregular_proxy_overstayers_url'],
         retrieval='ARCHIVED', local_file='irregular__9fcb57f01c__www.homeaffairs.gov.au.pdf', outcome='DOWNLOADED',
         note='Annual Report 2015-16 page 63: unlawful non-citizens in the community, 62,000 at 30 June 2015 (audit F16, %s).' % WHEN),
    dict(iso3='JPN', variable='irregular_proxy_overstayers', years='2010-2015', n_obs=4,
         source_name=pi.loc[('JPN', 2010), 'irregular_proxy_overstayers_source'], source_url=pi.loc[('JPN', 2010), 'irregular_proxy_overstayers_url'],
         retrieval='ARCHIVED', local_file='irregular__ccfa80d7df__www.moj.go.jp.pdf', outcome='DOWNLOADED',
         note='Table 21 (page 46), 1 January 2010, 2012, 2013 and 2015; the 2011 and 2014 values of the same table were '
              'already in the panel (audit F16, %s).' % WHEN),
    dict(iso3='TWN', variable='irregular_proxy_overstayers', years='2012-2013', n_obs=2,
         source_name=pi.loc[('TWN', 2012), 'irregular_proxy_overstayers_source'], source_url=pi.loc[('TWN', 2012), 'irregular_proxy_overstayers_url'],
         retrieval='ARCHIVED', local_file='irregular__539a03cf36__www.ly.gov.tw.html', outcome='DOWNLOADED',
         note='Legislative Yuan Budget Center report of July 2019, 附表11 (end of 2012 and 2013): totals of all external-population '
              'categories (audit F06/F07, %s).' % WHEN),
    dict(iso3='TWN', variable='irregular_proxy_overstayers', years='2019-2020', n_obs=2,
         source_name=pi.loc[('TWN', 2019), 'irregular_proxy_overstayers_source'], source_url=pi.loc[('TWN', 2019), 'irregular_proxy_overstayers_url'],
         retrieval='ARCHIVED', local_file='irregular__40806cb930__www.ly.gov.tw.html', outcome='DOWNLOADED',
         note='Legislative Yuan Budget Center report of September 2021, Table 1, totals for 2019 and 2020 (audit F06, %s).' % WHEN),
]
for r in new:
    r.update(from_workbook='AUDIT')
    for c in ('superseded_source_name', 'superseded_source_url'):
        r.setdefault(c, '')
reg = pd.concat([reg, pd.DataFrame(new)[reg.columns]], ignore_index=True)
reg = reg.sort_values(['iso3', 'variable', 'years']).reset_index(drop=True)
reg.to_csv(os.path.join(D, 'source_register.csv'), index=False, encoding='utf-8-sig')
print('source_register.csv: %d rows (%d from the audit corrections)' % (len(reg), len(new)))

# ================================================================== country READMEs
for iso in sorted(os.listdir(EV)):
    f = os.path.join(EV, iso, 'README.md')
    if not os.path.exists(f):
        continue
    t = open(f, encoding='utf-8').read()
    t = re.sub(r'- Retrieved into `sources/`: \*\*(\d+)\*\*', r'- Retrieved into this folder: **\1**', t)
    t = re.sub(r'- `sources/` .*?\n',
               '- the downloaded source documents sit directly in this folder (there is no `sources/` subfolder); '
               'each has a viewable `MIRROR__` PDF/PNG, and a `SNAPSHOT__` page extract where one was cut out\n', t)
    t = re.sub(r'- `data_from_source.csv` .*?\n',
               '- `data_from_source.csv` — the observations extracted from the sources for this country: the 2010-2022 records '
               'of the first release plus, since %s, every current panel value that had no row. `used_in_panel` is recomputed '
               'from the current panel and `historical_status` says why a record is no longer used '
               '(superseded, rejected, reclassified, deleted)\n' % WHEN, t)
    t = re.sub(r'(ISO3: \*\*[A-Z]{3}\*\*)\s+Verified: 2026-08-17(?: \(first release;[^\n]*\))?',
               r'\1   First verified: 2026-08-17 (first release; the counts below are that check). Audit of '
               + WHEN + ': see verification/AUDIT_RESPONSE_2026-10-07.md', t)
    open(f, 'w', encoding='utf-8', newline='\n').write(t)
print('country READMEs updated')

# ================================================================== F02  the article's authors
# The Demography India article was cited as "Chandrasekhar S. and Sharma A."; its first page names Dharmendra
# Pratap Singh and Rejeshwari Biradar. Citation text only; no value depends on it.
import fitz
first = fitz.open(os.path.join(EV, 'IND', 'foreign_born__e47d30324c__iasp.ac.in.pdf'))[0].get_text()
assert 'Dharmendra Pratap Singh' in first and 'Rejeshwari Biradar' in first
changed_files = []
for rel in ('evidence/countries/IND/data_from_source.csv', 'evidence/countries/IND/README.md',
            'evidence/countries/IND/source_manifest.csv', 'evidence/countries/IND/value_check.csv',
            'verification/country_source_manifest.csv', 'verification/download_log.csv',
            'verification/sources_catalog.csv', 'data/source_register.csv'):
    fp_ = os.path.join(SITE, rel)
    if not os.path.exists(fp_):
        continue
    raw = open(fp_, 'rb').read()
    txt = raw.decode('utf-8')
    new_ = txt.replace('Chandrasekhar S. and Sharma A.', 'Singh D.P. and Biradar R.')
    if new_ != txt:
        open(fp_, 'wb').write(new_.encode('utf-8'))
        changed_files.append(rel)
print('article authors corrected in: %s' % changed_files)
