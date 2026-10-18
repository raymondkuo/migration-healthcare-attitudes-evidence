# -*- coding: utf-8 -*-
"""Put the census non-citizen count collected by 87_collect_census_non_citizens.py into the panel (run after
85_add_health_expenditure.py, before 81).

  data/panel_final.csv           eleven columns non_citizens_census[_*], appended; one value (Australia 2021)
  data/source_register.csv       one row per archived file (from_workbook CENSUS)
  evidence/countries/AUS/README.md   a dated section

The value is kept out of foreign_nationals on purpose (issue #9, the authors' decision of 2026-10-18): that column is
an annual register series wherever it exists, and one census value would read as part of it. Every other column of the
panel is asserted unchanged. 81_audit_reference_tables.py adds the row to the country's data_from_source.csv.
Idempotent: the columns are rebuilt from the staging file each time.
"""
import os
import re

import numpy as np
import pandas as pd

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(SITE, 'data')
EVC = os.path.join(SITE, 'evidence', 'countries')
VAR = 'non_citizens_census'
WHEN = '2026-10-18'
TAG = 'CENSUS'
SUFFIX = ['', '_pct_pop', '_source', '_url', '_ref_date', '_note', '_grade', '_verification', '_source_type', '_flag',
          '_collected_on']
COLS = [VAR + s for s in SUFFIX]
FILES = {'xlsx': 'Official ABS workbook "Cultural diversity data summary, 2021", Table 2: the value used',
         'cultural_diversity_page': 'The ABS release page that links the workbook',
         'about_census': 'The ABS page stating the census date (Tuesday 10 August 2021)'}

cells = pd.read_csv(os.path.join(D, 'extension_staging', 'census_non_citizens_cells.csv')).fillna('')
panel = pd.read_csv(os.path.join(D, 'panel_final.csv'), float_precision='round_trip')
before = panel.drop(columns=[c for c in COLS if c in panel.columns]).copy()
panel = before.copy()
for c in COLS:
    panel[c] = np.nan
    if c not in (VAR, VAR + '_pct_pop'):
        panel[c] = panel[c].astype(object)
key = {(r.iso3, int(r.year)): i for i, r in enumerate(panel.itertuples())}
for r in cells.itertuples():
    i = key[(r.iso3, int(r.year))]
    panel.at[i, VAR] = float(r.value)
    panel.at[i, VAR + '_pct_pop'] = float(r.value) / panel.at[i, 'population']
    for s, v in (('_source', r.source_name), ('_url', r.source_url), ('_ref_date', r.ref_date), ('_note', r.note),
                 ('_grade', r.grade), ('_verification', r.verification), ('_source_type', r.source_type),
                 ('_flag', r.flag), ('_collected_on', r.collected_on)):
        panel.at[i, VAR + s] = v if v != '' else np.nan
pd.testing.assert_frame_equal(panel[before.columns], before)
panel.to_csv(os.path.join(D, 'panel_final.csv'), index=False, encoding='utf-8-sig')
print('panel_final.csv: %d rows x %d columns; %s: %d value(s) %s'
      % (len(panel), len(panel.columns), VAR, panel[VAR].notna().sum(),
         [(r.iso3, int(r.year), int(getattr(r, VAR))) for r in panel[panel[VAR].notna()].itertuples()]))

# ------------------------------------------------------------------ source register
reg = pd.read_csv(os.path.join(D, 'source_register.csv')).fillna('')
reg = reg[reg.from_workbook != TAG]
out = []
for r in cells.itertuples():
    folder = os.path.join(EVC, r.iso3)
    files = sorted(f for f in os.listdir(folder) if f.startswith(VAR + '__') and not f.startswith('MIRROR__'))
    for f in files:
        what = next(v for k, v in FILES.items() if k in f)
        out.append(dict(iso3=r.iso3, variable=VAR, years='%d-%d' % (r.year, r.year), n_obs=1, from_workbook=TAG,
                        source_name=r.source_name, source_url=r.source_url, retrieval='ARCHIVED', local_file=f,
                        note='%s. Retrieved %s.' % (what, r.collected_on), outcome='DOWNLOADED',
                        superseded_source_name='', superseded_source_url=''))
reg = pd.concat([reg, pd.DataFrame(out)[reg.columns]], ignore_index=True)
reg = reg.sort_values(['iso3', 'variable', 'years'], kind='stable').reset_index(drop=True)
reg.to_csv(os.path.join(D, 'source_register.csv'), index=False, encoding='utf-8-sig')
print('source_register.csv: %d rows (%d for %s)' % (len(reg), len(out), VAR))

# ------------------------------------------------------------------ country README
BEGIN, END = '<!-- census-non-citizens:begin -->', '<!-- census-non-citizens:end -->'
for iso, g in cells.groupby('iso3'):
    rd = os.path.join(EVC, iso, 'README.md')
    txt = open(rd, encoding='utf-8').read()
    txt = re.sub(re.escape(BEGIN) + r'.*?' + re.escape(END) + r'\s*', '', txt, flags=re.S)
    r0 = g.iloc[0]
    lines = [BEGIN, '', '## Census count of non-citizens (added %s)' % WHEN, '',
             '`%s`: %s persons who are not Australian citizens, %d census (%s). A separate column, not part of '
             '`foreign_nationals`; no other value changed.' % (VAR, format(int(r0.value), ','), int(r0.year), r0.ref_date),
             '', '| file | what it is |', '|---|---|']
    lines += ['| `%s` | %s |' % (o['local_file'], o['note']) for o in out if o['iso3'] == iso]
    lines += ['', END, '']
    open(rd, 'w', encoding='utf-8', newline='\n').write(txt.rstrip('\n') + '\n\n' + '\n'.join(lines))
print('country README: census section written for %s' % ', '.join(sorted(cells.iso3.unique())))
