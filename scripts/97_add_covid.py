# -*- coding: utf-8 -*-
"""Put the COVID-19 cells collected by 96_collect_covid.py into the panel and the per-country tables (run after
95_add_gini.py, before 81).

  data/panel_final.csv                       four variable families, 44 columns, appended (2020-2022 only):
                                             covid_cases, covid_cases_pct_pop, covid_deaths, covid_deaths_pct_pop,
                                             each with _source, _url, _ref_date, _note, _grade, _verification,
                                             _source_type, _flag, _collected_on; the two percentages also with
                                             _derived and _derivation (computed by the archive)
  evidence/countries/*/data_from_source.csv  one row per value
  data/source_register.csv                   one row per source document and country (from_workbook COVID)
  evidence/countries/*/README.md             a dated "COVID-19" section

Nothing else in the panel is touched: the step asserts that every other column is unchanged. 74 writes only the
columns it knows, so after a rebuild from 74 this step has to run again (after 95); it rebuilds its columns from
the staging file each time (idempotent).
"""
import os
import re
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import covid_texts as CT                               # noqa: E402

SITE = os.path.dirname(HERE)
D = os.path.join(SITE, 'data')
EVC = os.path.join(SITE, 'evidence', 'countries')
STAGE = os.path.join(D, 'extension_staging', 'covid_cells.csv')
WHEN = CT.WHEN
TAG = 'COVID'
SUFFIX = ['', '_source', '_url', '_ref_date', '_note', '_grade', '_verification', '_source_type', '_flag', '_collected_on']


def cols(v):
    return [v + s for s in SUFFIX] + ([v + '_derived', v + '_derivation'] if v in CT.PCT else [])


ALL = [c for v in CT.VARS for c in cols(v)]
cells = pd.read_csv(STAGE, float_precision='round_trip').fillna('')
panel = pd.read_csv(os.path.join(D, 'panel_final.csv'), float_precision='round_trip')
before = panel.drop(columns=[c for c in ALL if c in panel.columns]).copy()
panel = before.copy()
for c in ALL:
    panel[c] = np.nan if c in CT.VARS else ''
    if c not in CT.VARS:
        panel[c] = panel[c].astype(object)
key = {(r.iso3, int(r.year)): i for i, r in enumerate(panel.itertuples())}
assert not cells.duplicated(['iso3', 'year', 'variable']).any()
for r in cells.itertuples():
    i, v = key[(r.iso3, int(r.year))], r.variable
    panel.at[i, v] = float(r.value)
    for s, val in (('_source', r.source_name), ('_url', r.source_url), ('_ref_date', r.ref_date), ('_note', r.note),
                   ('_grade', r.grade), ('_verification', r.verification), ('_source_type', r.source_type),
                   ('_flag', r.flag), ('_collected_on', r.collected_on)):
        panel.at[i, v + s] = val
    if v in CT.PCT:
        base = CT.CASES if v == CT.CASES_PCT else CT.DEATHS
        panel.at[i, v + '_derived'] = 'yes'
        panel.at[i, v + '_derivation'] = '%s / population x 100 (the panel\'s population of the same country and year)' % base
for c in ALL:
    if c not in CT.VARS:
        panel[c] = panel[c].replace('', np.nan)
for v in CT.VARS:
    assert int(panel[v].notna().sum()) == int((cells.variable == v).sum())
    assert panel[panel[v].notna()].year.isin(CT.YEARS).all()
    assert panel[panel[v].notna()].iso3.nunique() == panel.iso3.nunique(), (v, 'a country without any value')
# the percentages are the counts over the panel's population
for v, base in ((CT.CASES_PCT, CT.CASES), (CT.DEATHS_PCT, CT.DEATHS)):
    s = panel[panel[v].notna()]
    assert np.allclose(s[v], 100.0 * s[base] / s['population'], rtol=1e-12), v
pd.testing.assert_frame_equal(panel[before.columns], before)
panel.to_csv(os.path.join(D, 'panel_final.csv'), index=False, encoding='utf-8-sig')
print('panel_final.csv: %d rows x %d columns; COVID-19 values in %d country-years per variable (all %d countries, %s)'
      % (len(panel), len(panel.columns), panel[CT.CASES].notna().sum(), panel.iso3.nunique(),
         '-'.join(map(str, (CT.YEARS[0], CT.YEARS[-1])))))

# ------------------------------------------------------------------ per-country data_from_source.csv
n = 0
for iso, g in cells.groupby('iso3'):
    f = os.path.join(EVC, iso, 'data_from_source.csv')
    d = pd.read_csv(f, dtype={'value': str})
    d = d[~d.variable.isin(CT.VARS)]
    add = pd.DataFrame([dict(iso3=iso, year=int(r.year), variable=r.variable,
                             value=str(int(r.value)) if r.variable in (CT.CASES, CT.DEATHS) else repr(float(r.value)),
                             source_name=r.source_name, source_url=r.source_url, notes=r.note,
                             used_in_panel='yes',
                             live_source_check='READ FROM ARCHIVED PAYLOAD' if r.grade == 'A'
                             else 'CONFIRMED IN ARCHIVED DOCUMENT',
                             historical_status='current') for r in g.itertuples()])
    d = pd.concat([d, add], ignore_index=True)
    d = d.sort_values(['variable', 'year', 'used_in_panel'], ascending=[True, True, False], kind='stable')
    d.to_csv(f, index=False, encoding='utf-8-sig')
    n += len(add)
print('data_from_source.csv: %d COVID-19 rows across %d countries' % (n, cells.iso3.nunique()))

# ------------------------------------------------------------------ source register (one row per source and country)
reg = pd.read_csv(os.path.join(D, 'source_register.csv')).fillna('')
reg = reg[reg.from_workbook != TAG]
out = []
for (iso, url, lf), g in cells[cells.variable == CT.CASES].groupby(['iso3', 'source_url', 'local_file'], sort=True):
    r0 = g.iloc[0]
    yrs = ', '.join(str(int(y)) for y in g.year)
    api = lf.startswith('evidence/api/')
    out.append(dict(iso3=iso, variable=CT.CASES, years='%d-%d' % (g.year.min(), g.year.max()), n_obs=len(g),
                    from_workbook=TAG, source_name=r0.source_name, source_url=url,
                    retrieval='VERIFIED_API' if api else 'ARCHIVED', local_file=lf,
                    outcome='VERIFIED_API' if api else 'DOWNLOADED',
                    note=('Read on %s from the archived %s (years %s); also the source of covid_deaths and of the two '
                          'percentages, which the archive computes with the panel\'s population.'
                          % (WHEN, 'WHO daily file' if api else 'document', yrs)),
                    superseded_source_name='', superseded_source_url=''))
reg = pd.concat([reg, pd.DataFrame(out)[reg.columns]], ignore_index=True)
reg = reg.sort_values(['iso3', 'variable', 'years'], kind='stable').reset_index(drop=True)
for _, r in reg[reg.from_workbook == TAG].iterrows():
    p = r.local_file if r.local_file.startswith('evidence/') else 'evidence/countries/%s/%s' % (r.iso3, r.local_file)
    assert os.path.exists(os.path.join(SITE, p)), p
reg.to_csv(os.path.join(D, 'source_register.csv'), index=False, encoding='utf-8-sig')
print('source_register.csv: %d rows (%d for COVID-19)' % (len(reg), len(out)))

# ------------------------------------------------------------------ country READMEs
BEGIN, END = '<!-- covid:begin -->', '<!-- covid:end -->'
for iso, g in cells.groupby('iso3'):
    rd = os.path.join(EVC, iso, 'README.md')
    if not os.path.exists(rd):
        continue
    txt = open(rd, encoding='utf-8').read()
    txt = re.sub(re.escape(BEGIN) + r'.*?' + re.escape(END) + r'\s*', '', txt, flags=re.S)
    c = g[g.variable == CT.CASES].set_index('year')
    dd = g[g.variable == CT.DEATHS].set_index('year')
    lines = [BEGIN, '', '## COVID-19 (collected %s)' % WHEN, '',
             'Four new variables for the years %s: `covid_cases` and `covid_deaths` (reported in the calendar year) and '
             '`covid_cases_pct_pop` and `covid_deaths_pct_pop` (the same over the panel\'s population, x 100, computed by '
             'the archive). No other value in this folder or in the panel changed.'
             % ', '.join(str(int(y)) for y in c.index), '',
             '| year | cases | deaths | source | file |', '|---|---:|---:|---|---|']
    for y in c.index:
        lines.append('| %d | %s | %s | %s | `%s` |' % (y, format(int(c.loc[y, 'value']), ','), format(int(dd.loc[y, 'value']), ','),
                                                        str(c.loc[y, 'source_name']).replace('|', '/')[:90],
                                                        os.path.basename(c.loc[y, 'local_file'])))
    for fl, gg in g[(g.variable == CT.CASES) & (g.flag != '')].groupby('flag'):
        lines += ['', 'Flag "%s": %s.' % (fl, ', '.join(str(int(y)) for y in gg.year))]
    if iso == 'CHN':
        lines += ['', 'WHO\'s "China" includes Hong Kong, Macao and Taiwan, so the mainland figures come from the National '
                      'Health Commission.']
    lines += ['', '`data/covid_source_comparison.csv` sets the values beside WHO\'s and the Johns Hopkins archive\'s; the '
              'revision history on the Verification page dates the addition.', '', END, '']
    open(rd, 'w', encoding='utf-8', newline='\n').write(txt.rstrip('\n') + '\n\n' + '\n'.join(lines))
print('country READMEs: COVID-19 section written for %d countries' % cells.iso3.nunique())
