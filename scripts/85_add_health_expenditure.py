# -*- coding: utf-8 -*-
"""Put the health-expenditure cells collected by 84_collect_health_expenditure.py into the panel
and the per-country tables (run after 79_apply_audit_corrections.py, before 81).

  data/panel_final.csv                       ten columns health_expenditure_pct_gdp[_*], appended
  evidence/countries/*/data_from_source.csv  one row per value
  data/source_register.csv                   one row per source and country (from_workbook HEALTH)
  evidence/countries/*/README.md             a dated "Health expenditure" section

Nothing else in the panel is touched: the step asserts that every other column is unchanged.
74_assemble_panel.py writes only the columns it knows, so after a rebuild from 74 this step has to
run again; it rebuilds its columns from the staging file each time (idempotent).
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
STAGE = os.path.join(D, 'extension_staging', 'health_expenditure_cells.csv')
VAR = 'health_expenditure_pct_gdp'
WHEN = '2026-10-17'
TAG = 'HEALTH'
SUFFIX = ['', '_source', '_url', '_ref_date', '_note', '_grade', '_verification', '_source_type',
          '_flag', '_collected_on']
HCOLS = [VAR + s for s in SUFFIX]

cells = pd.read_csv(STAGE).fillna('')
panel = pd.read_csv(os.path.join(D, 'panel_final.csv'), float_precision='round_trip')
before = panel.drop(columns=[c for c in HCOLS if c in panel.columns]).copy()
panel = before.copy()
for c in HCOLS:
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
for c in HCOLS[1:]:
    panel[c] = panel[c].replace('', np.nan)
assert panel[VAR].notna().all()
# every column that was there before is untouched
pd.testing.assert_frame_equal(panel[before.columns], before)
panel.to_csv(os.path.join(D, 'panel_final.csv'), index=False, encoding='utf-8-sig')
print('panel_final.csv: %d rows x %d columns; %s filled in every row (%d countries x %d years)'
      % (len(panel), len(panel.columns), VAR, panel.iso3.nunique(), panel.year.nunique()))

# ------------------------------------------------------------------ per-country data_from_source.csv
def live_check(ver):
    if ver.startswith('Read directly from the archived API'):
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
                             notes=r.note or 'Current health expenditure as % of GDP (WHO GHED via the World Bank).',
                             used_in_panel='yes', live_source_check=live_check(r.verification),
                             historical_status='current') for r in g.itertuples()])
    d = pd.concat([d, add], ignore_index=True)
    d = d.sort_values(['variable', 'year', 'used_in_panel'], ascending=[True, True, False], kind='stable')
    d.to_csv(f, index=False, encoding='utf-8-sig')
    n += len(add)
print('data_from_source.csv: %d health-expenditure rows across %d countries' % (n, cells.iso3.nunique()))

# ------------------------------------------------------------------ source register
reg = pd.read_csv(os.path.join(D, 'source_register.csv')).fillna('')
reg = reg[reg.from_workbook != TAG]
TW = cells[cells.iso3 == 'TWN'].iloc[0]
TW_FILES = re.findall(r'(health_expenditure__\S+?\.(?:xlsx|pdf))', TW.verification)
out = []
for iso, g in cells.groupby('iso3'):
    r0 = g.iloc[0]
    base = dict(iso3=iso, variable=VAR, years='%d-%d' % (g.year.min(), g.year.max()), n_obs=len(g),
                from_workbook=TAG, source_name=r0.source_name, source_url=r0.source_url,
                superseded_source_name='', superseded_source_url='')
    if iso != 'TWN':
        out.append(dict(base, retrieval='VERIFIED_API', local_file=r0.local_file, outcome='VERIFIED_API',
                        note='Read directly from the live source on %s; the raw response is archived at %s. '
                             'Every value is identical to WHO\'s own Global Health Observatory API '
                             '(data/health_expenditure_wb_vs_who.csv).' % (WHEN, r0.local_file)))
    else:
        files = [r0.local_file] + [f for f in dict.fromkeys(TW_FILES) if f != r0.local_file]
        files.append('health_expenditure__MOHW_DOS_NHE_page__retrieved_%s.html' % WHEN)
        what = {'xlsx': 'Official workbook 113年NHE統計表.xlsx, sheet 表1: the values used',
                'pdf': 'Published report 113年國民醫療保健支出 (February 2026), Table 1 on PDF page 18: the same figures',
                'html': 'The MOHW Department of Statistics page 國民醫療保健支出(NHE) that links both files'}
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
print('source_register.csv: %d rows (%d for health expenditure)' % (len(reg), len(out)))

# ------------------------------------------------------------------ country READMEs
BEGIN, END = '<!-- health-expenditure:begin -->', '<!-- health-expenditure:end -->'
for iso, g in cells.groupby('iso3'):
    rd = os.path.join(EVC, iso, 'README.md')
    if not os.path.exists(rd):
        continue
    txt = open(rd, encoding='utf-8').read()
    txt = re.sub(re.escape(BEGIN) + r'.*?' + re.escape(END) + r'\s*', '', txt, flags=re.S)
    r0 = g.iloc[0]
    files = [o['local_file'] for o in out if o['iso3'] == iso]
    lines = [BEGIN, '', '## Health expenditure (collected %s)' % WHEN, '',
             '`%s`: current health expenditure as a percentage of GDP, %d-%d (%d values). '
             'A new variable; no other value in this folder or in the panel changed.'
             % (VAR, g.year.min(), g.year.max(), len(g)), '',
             '| years | source | file |', '|---|---|---|']
    for f in files:
        lines.append('| %d-%d | %s | `%s` |' % (g.year.min(), g.year.max(),
                                                 str(r0.source_name).replace('|', '/')[:110],
                                                 os.path.basename(f)))
    lines += ['', 'Each value carries its source, reference period, grade, verification text and any '
              'flag in `data/panel_final.csv`; the revision history on the Verification page dates the '
              'addition.', '', END, '']
    open(rd, 'w', encoding='utf-8', newline='\n').write(txt.rstrip('\n') + '\n\n' + '\n'.join(lines))
print('country READMEs: health-expenditure section written for %d countries' % cells.iso3.nunique())
