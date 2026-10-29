# -*- coding: utf-8 -*-
"""Put the Gini-index cells collected by 94_collect_gini.py into the panel and the per-country tables
(run after 93_add_vdem.py, before 81).

  data/panel_final.csv                       ten columns gini_index[_*], appended (empty where no survey exists)
  evidence/countries/*/data_from_source.csv  one row per value
  data/source_register.csv                   one row per source and country (from_workbook GINI)
  evidence/countries/*/README.md             a dated "Gini index" section

Nothing else in the panel is touched: the step asserts that every other column is unchanged.
74_assemble_panel.py writes only the columns it knows, so after a rebuild from 74 this step has to
run again (after 85, 88, 91 and 93, which keeps the column order); it rebuilds its columns from the
staging file each time (idempotent).
"""
import os
import re
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gini_texts as GT                                # noqa: E402

SITE = os.path.dirname(HERE)
D = os.path.join(SITE, 'data')
EVC = os.path.join(SITE, 'evidence', 'countries')
STAGE = os.path.join(D, 'extension_staging', 'gini_cells.csv')
VAR = GT.VAR
WHEN = GT.WHEN
TAG = 'GINI'
SUFFIX = ['', '_source', '_url', '_ref_date', '_note', '_grade', '_verification', '_source_type',
          '_flag', '_collected_on']
GCOLS = [VAR + s for s in SUFFIX]

cells = pd.read_csv(STAGE).fillna('')
panel = pd.read_csv(os.path.join(D, 'panel_final.csv'), float_precision='round_trip')
before = panel.drop(columns=[c for c in GCOLS if c in panel.columns]).copy()
panel = before.copy()
for c in GCOLS:
    panel[c] = np.nan if c == VAR else ''
    if c != VAR:
        panel[c] = panel[c].astype(object)
key = {(r.iso3, int(r.year)): i for i, r in enumerate(panel.itertuples())}
assert not cells.duplicated(['iso3', 'year']).any()
for r in cells.itertuples():
    i = key[(r.iso3, int(r.year))]
    panel.at[i, VAR] = float(r.value)
    for s, v in (('_source', r.source_name), ('_url', r.source_url), ('_ref_date', r.ref_date),
                 ('_note', r.note), ('_grade', r.grade), ('_verification', r.verification),
                 ('_source_type', r.source_type), ('_flag', r.flag), ('_collected_on', r.collected_on)):
        panel.at[i, VAR + s] = v
for c in GCOLS[1:]:
    panel[c] = panel[c].replace('', np.nan)
assert int(panel[VAR].notna().sum()) == len(cells)
assert panel[panel[VAR].notna()].iso3.nunique() == panel.iso3.nunique(), 'a country without any Gini value'
# every column that was there before is untouched
pd.testing.assert_frame_equal(panel[before.columns], before)
panel.to_csv(os.path.join(D, 'panel_final.csv'), index=False, encoding='utf-8-sig')
print('panel_final.csv: %d rows x %d columns; %s filled in %d rows (all %d countries; survey years only)'
      % (len(panel), len(panel.columns), VAR, panel[VAR].notna().sum(), panel.iso3.nunique()))

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
                             notes=(r.note or 'Gini index, 0-100.') + (' Flag: %s.' % r.flag if r.flag else ''),
                             used_in_panel='yes', live_source_check='READ FROM ARCHIVED PAYLOAD',
                             historical_status='current') for r in g.itertuples()])
    d = pd.concat([d, add], ignore_index=True)
    d = d.sort_values(['variable', 'year', 'used_in_panel'], ascending=[True, True, False], kind='stable')
    d.to_csv(f, index=False, encoding='utf-8-sig')
    n += len(add)
print('data_from_source.csv: %d Gini rows across %d countries' % (n, cells.iso3.nunique()))

# ------------------------------------------------------------------ source register
reg = pd.read_csv(os.path.join(D, 'source_register.csv')).fillna('')
reg = reg[reg.from_workbook != TAG]
out = []
for (iso, sid), g in cells.groupby(['iso3', 'source_id']):
    r0 = g.iloc[0]
    yrs = ', '.join(str(int(y)) for y in g.year)
    check = {'WB_SI_POV_GINI': 'Every value equals 100 x the Gini of the matching World Bank PIP survey row, rounded to '
                               'one decimal (data/gini_source_comparison.csv).',
             'WB_PIP': 'WDI does not publish Taiwan; the values are PIP\'s survey Gini x 100, rounded to one decimal as '
                       'WDI does.',
             'OECD_IDD': 'The World Bank has no New Zealand data; OECD IDD Gini of equivalised disposable income x 100, '
                         'flagged as a different concept.'}[sid]
    out.append(dict(iso3=iso, variable=VAR, years='%d-%d' % (g.year.min(), g.year.max()), n_obs=len(g),
                    from_workbook=TAG, source_name=r0.source_name, source_url=r0.source_url,
                    retrieval='VERIFIED_API', local_file=r0.local_file, outcome='VERIFIED_API',
                    note='Read directly from the live source on %s; the raw response is archived at %s. Years with a '
                         'value: %s. %s' % (WHEN, r0.local_file, yrs, check),
                    superseded_source_name='', superseded_source_url=''))
reg = pd.concat([reg, pd.DataFrame(out)[reg.columns]], ignore_index=True)
reg = reg.sort_values(['iso3', 'variable', 'years'], kind='stable').reset_index(drop=True)
for _, r in reg[reg.from_workbook == TAG].iterrows():
    assert os.path.exists(os.path.join(SITE, r.local_file)), r.local_file
reg.to_csv(os.path.join(D, 'source_register.csv'), index=False, encoding='utf-8-sig')
print('source_register.csv: %d rows (%d for the Gini index)' % (len(reg), len(out)))

# ------------------------------------------------------------------ country READMEs
BEGIN, END = '<!-- gini:begin -->', '<!-- gini:end -->'
for iso, g in cells.groupby('iso3'):
    rd = os.path.join(EVC, iso, 'README.md')
    if not os.path.exists(rd):
        continue
    txt = open(rd, encoding='utf-8').read()
    txt = re.sub(re.escape(BEGIN) + r'.*?' + re.escape(END) + r'\s*', '', txt, flags=re.S)
    r0 = g.iloc[0]
    flagged = g[g.flag != '']
    lines = [BEGIN, '', '## Gini index (collected %s)' % WHEN, '',
             '`%s`: 100 x the Gini coefficient of income or consumption, %d value(s) for the survey years %s. A new '
             'variable; no other value in this folder or in the panel changed.'
             % (VAR, len(g), GT._years(g.year)), '']
    if len(flagged):
        for fl, gg in flagged.groupby('flag'):
            lines += ['- Flag "%s": %s.' % (fl, GT._years(gg.year))]
        lines += ['']
    lines += ['| years | source | file |', '|---|---|---|']
    for o in [o for o in out if o['iso3'] == iso]:
        lines.append('| %s | %s | `%s` |' % (o['years'], str(o['source_name']).replace('|', '/')[:110],
                                            os.path.basename(o['local_file'])))
    lines += ['', 'Each value carries its source, reference period, grade, verification text and any flag in '
              '`data/panel_final.csv`; `data/gini_source_comparison.csv` sets the World Bank, PIP and OECD values side '
              'by side; the revision history on the Verification page dates the addition.', '', END, '']
    open(rd, 'w', encoding='utf-8', newline='\n').write(txt.rstrip('\n') + '\n\n' + '\n'.join(lines))
print('country READMEs: Gini section written for %d countries' % cells.iso3.nunique())
