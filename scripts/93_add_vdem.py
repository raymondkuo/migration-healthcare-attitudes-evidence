# -*- coding: utf-8 -*-
"""Put the V-Dem liberal democracy index cells collected by 92_collect_vdem.py into the panel and the
per-country tables (run after 91_add_unemployment.py, before 81).

  data/panel_final.csv                       ten columns vdem_libdem[_*], appended
  evidence/countries/*/data_from_source.csv  one row per value
  data/source_register.csv                   two rows per country (from_workbook VDEM): the data file and the codebook
  evidence/countries/*/README.md             a dated "V-Dem liberal democracy index" section

Nothing else in the panel is touched: the step asserts that every other column is unchanged.
74_assemble_panel.py writes only the columns it knows, so after a rebuild from 74 this step has to
run again (after 85, 88 and 91, which keeps the column order); it rebuilds its columns from the staging
file each time (idempotent).
"""
import os
import re
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vdem_texts as VT                                # noqa: E402

SITE = os.path.dirname(HERE)
D = os.path.join(SITE, 'data')
EVC = os.path.join(SITE, 'evidence', 'countries')
STAGE = os.path.join(D, 'extension_staging', 'vdem_cells.csv')
VAR = VT.VAR
WHEN = VT.WHEN
TAG = 'VDEM'
SUFFIX = ['', '_source', '_url', '_ref_date', '_note', '_grade', '_verification', '_source_type',
          '_flag', '_collected_on']
VCOLS = [VAR + s for s in SUFFIX]
CB_PDF = 'evidence/api/vdem_codebook_v16_retrieved_%s.pdf' % WHEN

cells = pd.read_csv(STAGE).fillna('')
panel = pd.read_csv(os.path.join(D, 'panel_final.csv'), float_precision='round_trip')
before = panel.drop(columns=[c for c in VCOLS if c in panel.columns]).copy()
panel = before.copy()
for c in VCOLS:
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
for c in VCOLS[1:]:
    panel[c] = panel[c].replace('', np.nan)
assert panel[VAR].notna().all()
# every column that was there before is untouched
pd.testing.assert_frame_equal(panel[before.columns], before)
panel.to_csv(os.path.join(D, 'panel_final.csv'), index=False, encoding='utf-8-sig')
print('panel_final.csv: %d rows x %d columns; %s filled in every row (%d countries x %d years)'
      % (len(panel), len(panel.columns), VAR, panel.iso3.nunique(), panel.year.nunique()))

# ------------------------------------------------------------------ per-country data_from_source.csv
n = 0
for iso, g in cells.groupby('iso3'):
    f = os.path.join(EVC, iso, 'data_from_source.csv')
    # values are kept as text: the column holds whole-number counts, and reading it as float
    # would rewrite every one of them as 843000.0
    d = pd.read_csv(f, dtype={'value': str})
    d = d[d.variable != VAR]
    add = pd.DataFrame([dict(iso3=iso, year=int(r.year), variable=VAR, value=repr(float(r.value)),
                             source_name=r.source_name, source_url=r.source_url,
                             notes=r.note or 'V-Dem liberal democracy index, 0-1.',
                             used_in_panel='yes', live_source_check='READ FROM ARCHIVED PAYLOAD',
                             historical_status='current') for r in g.itertuples()])
    d = pd.concat([d, add], ignore_index=True)
    d = d.sort_values(['variable', 'year', 'used_in_panel'], ascending=[True, True, False], kind='stable')
    d.to_csv(f, index=False, encoding='utf-8-sig')
    n += len(add)
print('data_from_source.csv: %d V-Dem rows across %d countries' % (n, cells.iso3.nunique()))

# ------------------------------------------------------------------ source register
reg = pd.read_csv(os.path.join(D, 'source_register.csv')).fillna('')
reg = reg[reg.from_workbook != TAG]
out = []
for iso, g in cells.groupby('iso3'):
    r0 = g.iloc[0]
    base = dict(iso3=iso, variable=VAR, years='%d-%d' % (g.year.min(), g.year.max()), n_obs=len(g),
                from_workbook=TAG, source_name=r0.source_name, source_url=r0.source_url,
                superseded_source_name='', superseded_source_url='')
    out.append(dict(base, retrieval='VERIFIED_API', local_file=r0.local_file, outcome='VERIFIED_API',
                    note='Read on %s from the V-Dem Institute\'s own data file (vdemdata 16.0, release commit %s), archived '
                         'at %s and decoded with R; its git blob hash is the one GitHub records for the release. Every '
                         'value is identical at three decimals to Our World in Data\'s copy of V-Dem v16 '
                         '(data/vdem_source_comparison.csv).' % (WHEN, VT.COMMIT[:7], r0.local_file)))
    out.append(dict(base, retrieval='ARCHIVED', local_file=CB_PDF, outcome='DOWNLOADED',
                    note='V-Dem Codebook v16: the definition of the index (PDF page 48), its 68%% interval (page 32), the '
                         'annual aggregation (page 42) and the dataset citation (page 29). Retrieved %s.' % WHEN))
reg = pd.concat([reg, pd.DataFrame(out)[reg.columns]], ignore_index=True)
reg = reg.sort_values(['iso3', 'variable', 'years'], kind='stable').reset_index(drop=True)
for _, r in reg[reg.from_workbook == TAG].iterrows():
    p = r.local_file if r.local_file.startswith('evidence/') else 'evidence/countries/%s/%s' % (r.iso3, r.local_file)
    assert os.path.exists(os.path.join(SITE, p)), p
reg.to_csv(os.path.join(D, 'source_register.csv'), index=False, encoding='utf-8-sig')
print('source_register.csv: %d rows (%d for the V-Dem index)' % (len(reg), len(out)))

# ------------------------------------------------------------------ country READMEs
BEGIN, END = '<!-- vdem:begin -->', '<!-- vdem:end -->'
for iso, g in cells.groupby('iso3'):
    rd = os.path.join(EVC, iso, 'README.md')
    if not os.path.exists(rd):
        continue
    txt = open(rd, encoding='utf-8').read()
    txt = re.sub(re.escape(BEGIN) + r'.*?' + re.escape(END) + r'\s*', '', txt, flags=re.S)
    r0 = g.iloc[0]
    files = [o['local_file'] for o in out if o['iso3'] == iso]
    lines = [BEGIN, '', '## V-Dem liberal democracy index (collected %s)' % WHEN, '',
             '`%s`: the V-Dem liberal democracy index (v2x_libdem, 0-1), %d-%d (%d values), from the V-Dem Country-Year '
             'Dataset v16. A new variable; no other value in this folder or in the panel changed.'
             % (VAR, g.year.min(), g.year.max(), len(g)), '',
             '| years | source | file |', '|---|---|---|']
    for f in files:
        lines.append('| %d-%d | %s | `%s` |' % (g.year.min(), g.year.max(),
                                                 str(r0.source_name).replace('|', '/')[:110],
                                                 os.path.basename(f)))
    lines += ['', 'Each value carries its source, reference period, grade and verification text in '
              '`data/panel_final.csv`; V-Dem\'s 68% interval for it is in `data/vdem_source_comparison.csv`; the '
              'revision history on the Verification page dates the addition.', '', END, '']
    open(rd, 'w', encoding='utf-8', newline='\n').write(txt.rstrip('\n') + '\n\n' + '\n'.join(lines))
print('country READMEs: V-Dem section written for %d countries' % cells.iso3.nunique())
