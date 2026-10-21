# -*- coding: utf-8 -*-
"""Put the unemployment-rate cells collected by 90_collect_unemployment.py into the panel and the
per-country tables (run after 88_add_census_non_citizens.py, before 81).

  data/panel_final.csv                       ten columns unemployment_rate[_*], appended
  evidence/countries/*/data_from_source.csv  one row per value
  data/source_register.csv                   one row per source and country (from_workbook UNEMPLOYMENT)
  evidence/countries/*/README.md             a dated "Unemployment rate" section

Nothing else in the panel is touched: the step asserts that every other column is unchanged.
74_assemble_panel.py writes only the columns it knows, so after a rebuild from 74 this step has to
run again (after 85 and 88, which keeps the column order); it rebuilds its columns from the staging
file each time (idempotent).
"""
import os
import re
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
D = os.path.join(SITE, 'data')
EVC = os.path.join(SITE, 'evidence', 'countries')
STAGE = os.path.join(D, 'extension_staging', 'unemployment_cells.csv')
VAR = 'unemployment_rate'
WHEN = '2026-10-21'
TAG = 'UNEMPLOYMENT'
SUFFIX = ['', '_source', '_url', '_ref_date', '_note', '_grade', '_verification', '_source_type',
          '_flag', '_collected_on']
UCOLS = [VAR + s for s in SUFFIX]

cells = pd.read_csv(STAGE).fillna('')
panel = pd.read_csv(os.path.join(D, 'panel_final.csv'), float_precision='round_trip')
before = panel.drop(columns=[c for c in UCOLS if c in panel.columns]).copy()
panel = before.copy()
for c in UCOLS:
    panel[c] = np.nan if c == VAR else ''
    if c != VAR:
        panel[c] = panel[c].astype(object)
key = {(r.iso3, int(r.year)): i for i, r in enumerate(panel.itertuples())}
assert len(cells) == len(panel), (len(cells), len(panel))
for r in cells.itertuples():
    i = key[(r.iso3, int(r.year))]
    panel.at[i, VAR] = float(r.value)
    for s, v in (('_source', r.source_name), ('_url', r.source_url), ('_ref_date', r.ref_date),
                 ('_note', r.note), ('_grade', r.grade), ('_verification', r.verification),
                 ('_source_type', r.source_type), ('_flag', r.flag), ('_collected_on', r.collected_on)):
        panel.at[i, VAR + s] = v
for c in UCOLS[1:]:
    panel[c] = panel[c].replace('', np.nan)
assert panel[VAR].notna().all()
# every column that was there before is untouched
pd.testing.assert_frame_equal(panel[before.columns], before)
panel.to_csv(os.path.join(D, 'panel_final.csv'), index=False, encoding='utf-8-sig')
print('panel_final.csv: %d rows x %d columns; %s filled in every row (%d countries x %d years)'
      % (len(panel), len(panel.columns), VAR, panel.iso3.nunique(), panel.year.nunique()))


# ------------------------------------------------------------------ per-country data_from_source.csv
def live_check(ver):
    if ver.startswith('Read directly from the archived ILO SDMX'):
        return 'READ FROM ARCHIVED PAYLOAD'
    if ver.startswith('Read directly from the official'):
        return 'READ FROM OFFICIAL WORKBOOK'
    return 'CONFIRMED IN ARCHIVED DOCUMENT'


n = 0
for iso, g in cells.groupby('iso3'):
    f = os.path.join(EVC, iso, 'data_from_source.csv')
    # values are kept as text: the column holds whole-number counts, and reading it as float
    # would rewrite every one of them as 843000.0
    d = pd.read_csv(f, dtype={'value': str})
    d = d[d.variable != VAR]
    add = pd.DataFrame([dict(iso3=iso, year=int(r.year), variable=VAR, value=repr(float(r.value)),
                             source_name=r.source_name, source_url=r.source_url,
                             notes=(r.note or 'Unemployment rate, % of the labour force aged 15+.')
                             + (' Flag: %s.' % r.flag if r.flag else ''),
                             used_in_panel='yes', live_source_check=live_check(r.verification),
                             historical_status='current') for r in g.itertuples()])
    d = pd.concat([d, add], ignore_index=True)
    d = d.sort_values(['variable', 'year', 'used_in_panel'], ascending=[True, True, False], kind='stable')
    d.to_csv(f, index=False, encoding='utf-8-sig')
    n += len(add)
print('data_from_source.csv: %d unemployment rows across %d countries' % (n, cells.iso3.nunique()))

# ------------------------------------------------------------------ source register
reg = pd.read_csv(os.path.join(D, 'source_register.csv')).fillna('')
reg = reg[reg.from_workbook != TAG]
TW = cells[cells.iso3 == 'TWN'].iloc[0]
TW_FILES = re.findall(r'(unemployment_rate__\S+?\.(?:xlsx|pdf))', TW.verification)
out = []
for iso, g in cells.groupby('iso3'):
    r0 = g.iloc[0]
    base = dict(iso3=iso, variable=VAR, years='%d-%d' % (g.year.min(), g.year.max()), n_obs=len(g),
                from_workbook=TAG, source_name=r0.source_name, source_url=r0.source_url,
                superseded_source_name='', superseded_source_url='')
    if iso != 'TWN':
        imp = g[g.flag != '']
        out.append(dict(base, retrieval='VERIFIED_API', local_file=r0.local_file, outcome='VERIFIED_API',
                        note='Read directly from the live source on %s; the raw response is archived at %s. Every '
                             'value agrees at the ILO\'s three decimals with the World Bank\'s copy, WDI SL.UEM.TOTL.ZS '
                             '(data/unemployment_source_comparison.csv). %s'
                             % (WHEN, r0.local_file,
                                ('%d value(s) (%s) are ILO imputations, not based on national data, and are flagged.'
                                 % (len(imp), ', '.join(str(int(y)) for y in imp.year))) if len(imp) else
                                'Every value carries the ILO observation status R (Real value).')))
    else:
        files = [r0.local_file] + [f for f in dict.fromkeys(TW_FILES) if f != r0.local_file]
        files.append('unemployment_rate__DGBAS_Manpower_Yearbook2025_page__retrieved_%s.html' % WHEN)
        what = {'xlsx': 'Official workbook table2.xlsx (表2 歷年人力資源調查重要指標): the values used',
                'pdf': 'Published Yearbook of Manpower Survey Statistics 2025 (March 2026), Table 2 on PDF pages '
                       '20-21 (the same figures) and the definitions on PDF page 322',
                'html': 'The DGBAS statistics page 114年人力資源調查統計 that links both files'}
        for f in files:
            ext = f.rsplit('.', 1)[1]
            out.append(dict(base, retrieval='ARCHIVED', local_file=f, outcome='DOWNLOADED',
                            note='%s. Retrieved %s.' % (what[ext], WHEN)))
reg = pd.concat([reg, pd.DataFrame(out)[reg.columns]], ignore_index=True)
reg = reg.sort_values(['iso3', 'variable', 'years'], kind='stable').reset_index(drop=True)
for _, r in reg[reg.from_workbook == TAG].iterrows():
    p = r.local_file if r.local_file.startswith('evidence/') else 'evidence/countries/%s/%s' % (r.iso3, r.local_file)
    assert os.path.exists(os.path.join(SITE, p)), p
reg.to_csv(os.path.join(D, 'source_register.csv'), index=False, encoding='utf-8-sig')
print('source_register.csv: %d rows (%d for the unemployment rate)' % (len(reg), len(out)))

# ------------------------------------------------------------------ country READMEs
BEGIN, END = '<!-- unemployment:begin -->', '<!-- unemployment:end -->'
for iso, g in cells.groupby('iso3'):
    rd = os.path.join(EVC, iso, 'README.md')
    if not os.path.exists(rd):
        continue
    txt = open(rd, encoding='utf-8').read()
    txt = re.sub(re.escape(BEGIN) + r'.*?' + re.escape(END) + r'\s*', '', txt, flags=re.S)
    r0 = g.iloc[0]
    files = [o['local_file'] for o in out if o['iso3'] == iso]
    imp = g[g.flag != '']
    lines = [BEGIN, '', '## Unemployment rate (collected %s)' % WHEN, '',
             '`%s`: unemployed persons as a percentage of the labour force aged 15 and over, %d-%d (%d values). '
             'A new variable; no other value in this folder or in the panel changed.'
             % (VAR, g.year.min(), g.year.max(), len(g)), '']
    if len(imp):
        lines += ['%d of the values (%s) are ILO imputations, which the ILO describes as not based on national data; '
                  'they carry the flag "%s".' % (len(imp), ', '.join(str(int(y)) for y in imp.year), imp.flag.iloc[0]),
                  '']
    lines += ['| years | source | file |', '|---|---|---|']
    for f in files:
        lines.append('| %d-%d | %s | `%s` |' % (g.year.min(), g.year.max(),
                                                 str(r0.source_name).replace('|', '/')[:110],
                                                 os.path.basename(f)))
    lines += ['', 'Each value carries its source, reference period, grade, verification text and any '
              'flag in `data/panel_final.csv`; the revision history on the Verification page dates the '
              'addition.', '', END, '']
    open(rd, 'w', encoding='utf-8', newline='\n').write(txt.rstrip('\n') + '\n\n' + '\n'.join(lines))
print('country READMEs: unemployment section written for %d countries' % cells.iso3.nunique())
