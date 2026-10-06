# -*- coding: utf-8 -*-
"""Merge the collected 2001-2009 cells into panel_final.csv.

What this guarantees:
  * No value that was published before the extension changes. The pre-extension panel is read
    from git (BASELINE) and every non-blank cell in it is asserted identical afterwards.
  * Only blank cells are filled. Where two collectors supplied the same cell, the more
    comparable source wins (annual register/API > census > survey > UN estimate) and the loser
    is kept in migrant_stock_alternatives.csv, so the choice is visible.
  * Re-running is safe. Cells this script added are marked by <variable>_collected_on; they are
    cleared first and rebuilt, so a corrected collector does not leave stale cells behind.

New rows (2001-2009 for all 40 countries) carry the same identifier columns as the country's
existing rows. Eight columns are added to the panel:
    <var>_collected_on  for population, population_un_wpp2024, foreign_born, foreign_nationals
    <var>_source_type   for foreign_born, foreign_nationals (annual / census / survey / ...)
    <var>_flag          for foreign_born, foreign_nationals (splice, break, caution ...)
"""
import glob
import io
import os
import subprocess
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ext_lib as L                                    # noqa: E402

SITE = os.path.dirname(HERE)
D = os.path.join(SITE, 'data')
STAGE = os.path.join(D, 'extension_staging')
C = L.COLLECTED
BASELINE = L.BASELINE                  # last commit before the extension
RANK = {'annual': 0, 'census': 1, 'survey': 2, 'un_estimate': 3}

# ------------------------------------------------------------------ baseline and current panel
base = L.baseline_panel()
panel = pd.read_csv(os.path.join(D, 'panel_final.csv'))

MIG = ('foreign_born', 'foreign_nationals')
FAMILY = {'population': ['population', 'population_grade', 'population_source', 'population_url',
                         'population_verification', 'population_wb_vs_unwpp_pct',
                         'population_collected_on'],
          'population_un_wpp2024': ['population_un_wpp2024', 'population_un_wpp2024_collected_on']}
for v in MIG:
    FAMILY[v] = [c for c in panel.columns if c == v or c.startswith(v + '_')] + \
                [v + '_source_type', v + '_flag', v + '_collected_on']
    FAMILY[v] = list(dict.fromkeys(FAMILY[v]))
NEWCOLS = ['population_collected_on', 'population_un_wpp2024_collected_on'] + \
          [v + s for v in MIG for s in ('_source_type', '_flag', '_collected_on')]
for c in NEWCOLS:
    if c not in panel.columns:
        panel[c] = np.nan
for c in NEWCOLS:
    base[c] = np.nan

# text columns must be able to hold text even where the baseline has only blanks
TEXT_SUFFIX = ('_source', '_url', '_note', '_grade', '_verification', '_derived', '_derivation',
               '_published_range', '_ref_date', '_flag', '_source_type', '_collected_on')
for c in panel.columns:
    if c.endswith(TEXT_SUFFIX) or c in ('country', 'iso3', 'iso2'):
        panel[c] = panel[c].astype(object)

# 1. strip anything an earlier run added, so this run rebuilds from a clean state
panel = panel[panel.year >= 2010].copy()
for var, cols in FAMILY.items():
    marker = var + '_collected_on'
    m = panel[marker].notna() & (panel[marker].astype(str) != '')
    for c in cols:
        if c in panel.columns:
            panel.loc[m, c] = np.nan
panel = panel.reset_index(drop=True)

# 2. new rows, 2001-2009, for every country
order = list(dict.fromkeys(panel.iso3))
ID = ['country', 'iso3', 'iso2', 'm49_code', 'in_wave1', 'in_wave2']
first = panel.drop_duplicates('iso3').set_index('iso3')
new_rows = []
for iso in order:
    for y in range(2001, 2010):
        r = {c: np.nan for c in panel.columns}
        for c in ID:
            r[c] = iso if c == 'iso3' else first.loc[iso, c]
        r['year'] = y
        new_rows.append(r)
panel = pd.concat([pd.DataFrame(new_rows), panel], ignore_index=True)
panel['_o'] = panel.iso3.map({k: i for i, k in enumerate(order)})
panel = panel.sort_values(['_o', 'year']).drop(columns='_o').reset_index(drop=True)
key = {(r.iso3, int(r.year)): i for i, r in enumerate(panel.itertuples())}

# 3. the collected cells
COLLECTOR_FILES = sorted(glob.glob(os.path.join(STAGE, 'api_*_cells.csv')) +
                         glob.glob(os.path.join(STAGE, 'national_*_cells.csv')))
stage = pd.concat([pd.read_csv(f) for f in COLLECTOR_FILES], ignore_index=True)
stage['_rank'] = stage.source_type.map(RANK).fillna(9)
stage = stage.sort_values(['iso3', 'year', 'variable', '_rank'])
won = stage.drop_duplicates(['iso3', 'year', 'variable'], keep='first')
lost = stage[~stage.index.isin(won.index)]
print('collected cells: %d | kept: %d | superseded by a more comparable source: %d'
      % (len(stage), len(won), len(lost)))
for _, r in lost.iterrows():
    w = won[(won.iso3 == r.iso3) & (won.year == r.year) & (won.variable == r.variable)].iloc[0]
    print('   %s %d %s: kept %s (%s), set aside %s (%s)'
          % (r.iso3, r.year, r.variable, w.source_id, format(int(w.value), ','), r.source_id,
             format(int(r.value), ',')))

filled = {v: 0 for v in FAMILY}
for r in won.itertuples():
    i = key[(r.iso3, int(r.year))]
    v = r.variable
    assert pd.isna(panel.at[i, v]), 'would overwrite %s %d %s' % (r.iso3, r.year, v)
    panel.at[i, v] = float(r.value)
    panel.at[i, v + '_collected_on'] = r.collected_on
    if v == 'population':
        panel.at[i, 'population_grade'] = r.grade
        panel.at[i, 'population_source'] = r.source_name
        panel.at[i, 'population_url'] = r.source_url
        panel.at[i, 'population_verification'] = r.verification
    elif v in MIG:
        panel.at[i, v + '_ref_date'] = r.ref_date
        panel.at[i, v + '_source'] = r.source_name
        panel.at[i, v + '_url'] = r.source_url
        panel.at[i, v + '_note'] = r.note if isinstance(r.note, str) else ''
        panel.at[i, v + '_grade'] = r.grade
        panel.at[i, v + '_verification'] = r.verification
        panel.at[i, v + '_source_type'] = r.source_type
        panel.at[i, v + '_flag'] = r.flag if isinstance(r.flag, str) else ''
        # a value worked out from two published rows is derived, and is marked as such like the
        # midpoints of published ranges are
        if isinstance(r.flag, str) and 'derived by subtraction' in r.flag:
            panel.at[i, v + '_derived'] = 'yes'
            how = (r.note if isinstance(r.note, str) else '').replace('DERIVED BY SUBTRACTION: ', '')
            panel.at[i, v + '_derivation'] = how.split('. ONS warns')[0].split('. Survey estimate')[0].strip()
    filled[v] += 1

# 4. derived columns for the new cells
den = panel.population
for v in MIG:
    m = panel[v + '_collected_on'].notna() & panel[v].notna() & den.notna()
    panel.loc[m, v + '_pct_pop'] = panel.loc[m, v] / den[m]
m = panel.population_collected_on.notna() & panel.population_un_wpp2024.notna()
panel.loc[m, 'population_wb_vs_unwpp_pct'] = ((panel.loc[m, 'population']
                                               - panel.loc[m, 'population_un_wpp2024'])
                                              / panel.loc[m, 'population_un_wpp2024'] * 100)


# 5. a source type for the cells that were already published, so every cell can be filtered
def stype(src):
    s = str(src)
    if 'UN DESA' in s:
        return 'un_estimate'
    if 'migr_pop' in s or 'OECD' in s or 'Ministry of the Interior' in s:
        return 'annual'
    if s.startswith('ONS') or 'Community Survey' in s:
        return 'survey'
    if any(k in s.lower() for k in ('census', 'chandrasekhar', 'national bureau of statistics',
                                    'national statistics office', 'philippine statistics',
                                    'general bureau of statistics', 'statistics south africa')):
        return 'census'
    return 'other'


for v in MIG:
    m = panel[v].notna() & panel[v + '_source_type'].isna()
    panel.loc[m, v + '_source_type'] = panel.loc[m, v + '_source'].map(stype)

# 5b. flags for the cells that were already published. A flag is metadata about a value, not a
#     change to it, and a column that flagged only the new cells would imply the old ones had
#     nothing to flag: UN DESA estimates, the citizenship basis UN DESA declares for some
#     countries, and whatever Eurostat attached to each observation.
DECLARED_C = set(won[(won.variable == 'foreign_born')
                     & won.flag.astype(str).str.contains('declared citizenship', regex=False)].iso3)
EUR_FLAGS = {'foreign_born': L.parse_eurostat(L.EUR_CTB),
             'foreign_nationals': L.parse_eurostat(L.EUR_CTZ)}
n_flagged = 0
for v in MIG:
    for i in panel.index[panel[v].notna() & panel[v + '_collected_on'].isna()]:
        iso, yr, src = panel.at[i, 'iso3'], int(panel.at[i, 'year']), str(panel.at[i, v + '_source'])
        text = ''
        if 'UN DESA' in src:
            text = 'un_estimate'
            if v == 'foreign_born' and iso in DECLARED_C:
                text += '; declared citizenship basis'
        elif 'migr_pop' in src:
            text = L.eurostat_flag_text(EUR_FLAGS[v].get((iso, yr), (0, ''))[1])
        panel.at[i, v + '_flag'] = text
        n_flagged += bool(text)
print('flags attached to cells published earlier: %d (declared citizenship basis: %s)'
      % (n_flagged, sorted(DECLARED_C)))

# 6. the Taiwan note that said the series could not be extended
OLD = 'Series on this basis begins in 2012; 2010 and 2011 are not available on a comparable basis.'
NEW = ('The input workbook stated: "Series on this basis begins in 2012; 2010 and 2011 are not '
       'available on a comparable basis." On %s the Ministry of the Interior\'s consolidated table '
       '1996-2022 was found to give 2001-2011 as well, with these 2012-2022 values reproducing '
       'exactly; those years are included with a comparability caution.' % C)
#    The amended wording quotes the old sentence, so it is applied only to notes that have not
#    been amended yet; otherwise every re-run would nest another copy inside the last.
mt = ((panel.iso3 == 'TWN')
      & panel.foreign_nationals_note.astype(str).str.contains(OLD, regex=False)
      & ~panel.foreign_nationals_note.astype(str).str.contains('The input workbook stated:',
                                                               regex=False))
panel.loc[mt, 'foreign_nationals_note'] = panel.loc[mt, 'foreign_nationals_note'].str.replace(
    OLD, NEW, regex=False)
print('Taiwan notes amended: %d cells' % int(mt.sum()))

# ------------------------------------------------------------------ the guarantee
a = base.set_index(['iso3', 'year'])
b = panel.set_index(['iso3', 'year'])
changed = []
for c in base.columns:
    if c in NEWCOLS or c not in b.columns:
        continue
    x, y = a[c], b[c].reindex(a.index)
    nb = x.notna()
    same = (x[nb].astype(str) == y[nb].astype(str)) | (pd.to_numeric(x[nb], errors='coerce')
                                                       == pd.to_numeric(y[nb], errors='coerce'))
    bad = same[~same].index.tolist()
    if c.endswith('_note') and c.startswith('foreign_nationals') and all(k[0] == 'TWN' for k in bad):
        continue                                        # the deliberate Taiwan note amendment
    changed += [(c, k) for k in bad]
assert not changed, 'published values changed: %s' % changed[:8]
print('published cells compared with the pre-extension panel: no value changed')

# ------------------------------------------------------------------ write
cols = list(base.columns[:len(base.columns) - len(NEWCOLS)]) + NEWCOLS
cols = [c for c in cols if c in panel.columns]
for c in ('year', 'm49_code', 'in_wave1', 'in_wave2'):
    panel[c] = panel[c].astype(int)
panel[cols].to_csv(os.path.join(D, 'panel_final.csv'), index=False, encoding='utf-8-sig')
print('\npanel_final.csv: %d rows x %d columns (was %d x %d)'
      % (len(panel), len(cols), len(base), len(base.columns) - len(NEWCOLS)))
print('cells filled: %s' % {k: v for k, v in filled.items()})

# the alternatives table: every competing value, so the choice of source is visible
alt = pd.read_csv(os.path.join(STAGE, 'api_alternatives.csv'))
extra = []
for r in lost.itertuples():
    w = won[(won.iso3 == r.iso3) & (won.year == r.year) & (won.variable == r.variable)].iloc[0]
    extra.append(dict(country=first.loc[r.iso3, 'country'], iso3=r.iso3, year=int(r.year),
                      variable=r.variable, source=r.source_name, value=int(r.value),
                      used_in_panel='no',
                      diff_vs_used_pct=round((r.value - w.value) / w.value * 100, 3)))
alt = pd.concat([alt, pd.DataFrame(extra)], ignore_index=True)
alt = alt.sort_values(['iso3', 'variable', 'year', 'used_in_panel'],
                      ascending=[True, True, True, False])
alt.to_csv(os.path.join(D, 'migrant_stock_alternatives.csv'), index=False, encoding='utf-8-sig')
print('migrant_stock_alternatives.csv: %d rows' % len(alt))
stage.drop(columns='_rank').to_csv(os.path.join(STAGE, 'assembled_cells.txt'), index=False,
                                   encoding='utf-8-sig')
won.drop(columns='_rank').to_csv(os.path.join(STAGE, 'assembled_winners.txt'), index=False,
                                 encoding='utf-8-sig')
