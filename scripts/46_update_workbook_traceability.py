# -*- coding: utf-8 -*-
"""Bring the workbook into line with the traceability pass: refreshed Panel_final,
new codebook entries for the derived-value columns, revised grade definitions, a
Deleted_values sheet, and updated README counts."""
import os, shutil
import pandas as pd
import openpyxl

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(BASE, 'migration-data-archive')
BIL = os.path.join(BASE, 'migration-data-archive-bilingual')
D = os.path.join(SITE, 'data')
WB = os.path.join(D, 'FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx')

book = pd.read_excel(WB, sheet_name=None)
panel = pd.read_csv(os.path.join(D, 'panel_final.csv'))
book['Panel_final'] = panel

# ---------------------------------------------------------------- codebook
cb = book['Codebook']
c0, c1, c2 = cb.columns[:3]
new_rows = [
    {c0: '*_derived',
     c1: 'Flag: "yes" when the cell is derived from the source rather than published by it.',
     c2: 'Marked with ≈ on the website. 13 such values, all midpoints of published ranges.'},
    {c0: '*_derivation', c1: 'How the value was derived, e.g. "midpoint of the published range".',
     c2: 'Empty when the value is published directly by the source.'},
    {c0: '*_published_range', c1: 'The range the source actually publishes, where it publishes a '
                                  'range rather than a point estimate.',
     c2: 'Use the range, not the derived midpoint, for any claim about level.'},
]
cb = pd.concat([cb, pd.DataFrame(new_rows)], ignore_index=True)
# revised grade definition row
m = cb[c0].astype(str).str.startswith('*_grade')
if m.any():
    cb.loc[m, c1] = ('Data-quality grade for that cell. A = re-derived from a machine-readable '
                     'official source and matched exactly, or corrected against one during this '
                     'verification. B = the published figure appears in the retrieved source '
                     'document. C = derived from the source rather than published by it (see '
                     '*_derived and *_published_range). Values that could not be traced to an '
                     'archived source were deleted, so no grade D remains.')
    cb.loc[m, c2] = 'Every retained value is traceable to an archived source file.'
book['Codebook'] = cb

# ---------------------------------------------------------------- deleted values sheet
dv = os.path.join(BASE, 'verification', 'deleted_values.csv')
if os.path.exists(dv):
    book['Deleted_values'] = pd.read_csv(dv)

# ---------------------------------------------------------------- README counts
VARS = ['population', 'foreign_born', 'foreign_nationals', 'irregular_stock',
        'irregular_proxy_overstayers', 'irregular_proxy_detections',
        'irregular_proxy_absconded_workers']
g = pd.Series([x for v in VARS if v + '_grade' in panel
               for x in panel[v + '_grade'].dropna() if str(x).strip()]).value_counts()
nd = int(sum((panel[v + '_derived'] == 'yes').sum() for v in VARS if v + '_derived' in panel))
rd = book['README']
r0, r1 = rd.columns[:2]
for i, r in rd.iterrows():
    k = str(r[r0]).strip()
    if k.startswith('A - '):
        rd.at[i, r0] = 'A - re-derived from a machine-readable official source, exact match'
        rd.at[i, r1] = str(int(g.get('A', 0)))
    elif k.startswith('B - '):
        rd.at[i, r0] = 'B - the published figure appears in the retrieved source document'
        rd.at[i, r1] = str(int(g.get('B', 0)))
    elif k.startswith('C - '):
        rd.at[i, r0] = 'C - derived from the source (midpoint of a published range), flagged'
        rd.at[i, r1] = str(int(g.get('C', 0)))
    elif k.startswith('D - '):
        rd.at[i, r0] = 'D - not traceable to an archived source; such values were deleted'
        rd.at[i, r1] = str(int(g.get('D', 0)))
extra = pd.DataFrame([
    {r0: 'Values flagged as derived', r1: str(nd)},
    {r0: 'Values deleted as untraceable', r1: '1 (Russia 2020 irregular stock; see Deleted_values)'},
])
book['README'] = pd.concat([rd, extra], ignore_index=True)

with pd.ExcelWriter(WB, engine='openpyxl') as xw:
    for nm, df in book.items():
        df.to_excel(xw, sheet_name=nm, index=False)
wb = openpyxl.load_workbook(WB)
for ws in wb.worksheets:
    ws.freeze_panes = 'A2'
    for col in ws.columns:
        w = max((len(str(c.value)) for c in col[:200] if c.value is not None), default=10)
        ws.column_dimensions[col[0].column_letter].width = min(max(w + 2, 10), 62)
wb.save(WB)

for sh, fn in [('README', 'readme.csv'), ('Codebook', 'codebook.csv'),
               ('Panel_final', 'panel_final.csv')]:
    pd.read_excel(WB, sheet_name=sh).to_csv(os.path.join(D, fn), index=False, encoding='utf-8-sig')
if 'Deleted_values' in book:
    book['Deleted_values'].to_csv(os.path.join(D, 'deleted_values.csv'),
                                  index=False, encoding='utf-8-sig')

shutil.copy2(WB, os.path.join(BASE, 'FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx'))
for f in ['FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx', 'panel_final.csv',
          'readme.csv', 'codebook.csv', 'deleted_values.csv']:
    src = os.path.join(D, f)
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(BIL, 'data', f))

print('workbook sheets: %s' % ', '.join(book.keys()))
print('grades: %s   derived: %d' % (dict(sorted(g.items())), nd))
print('Panel_final columns: %d' % panel.shape[1])
