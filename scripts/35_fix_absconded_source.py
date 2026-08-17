# -*- coding: utf-8 -*-
"""When Taiwan's overstayer column was split, the Ministry of Labor values moved to
irregular_proxy_absconded_workers but their source columns did not follow. Restore them
from the original workbook's audit trail."""
import os
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(BASE, 'migration-data-archive')
F2 = os.path.join(BASE, 'migration_population_panel_40countries_2010-2022.xlsx')

lg = pd.read_excel(F2, sheet_name='Long_all_observations')
mol = lg[(lg.iso3 == 'TWN') & (lg.variable == 'irregular_proxy_overstayers')
         & (lg.source_name.astype(str).str.contains('Ministry of Labor', na=False))]
by_year = {int(r['year']): r for _, r in mol.iterrows()}
print('Ministry of Labor rows found:', sorted(by_year))

V = 'irregular_proxy_absconded_workers'
for target, xlsx in [(os.path.join(SITE, 'data', 'panel_final.csv'), None)]:
    p = pd.read_csv(target)
    for c in ['_source', '_url', '_note', '_ref_date', '_grade']:
        if V + c not in p.columns:
            p[V + c] = ''
    n = 0
    for i, r in p.iterrows():
        if r['iso3'] != 'TWN' or pd.isna(r.get(V)):
            continue
        src = by_year.get(int(r['year']))
        if src is None:
            continue
        p.at[i, V + '_source'] = src['source_name']
        p.at[i, V + '_url'] = src['source_url']
        p.at[i, V + '_note'] = src['notes']
        p.at[i, V + '_ref_date'] = '31 December'
        p.at[i, V + '_grade'] = 'C'
        n += 1
    p.to_csv(target, index=False, encoding='utf-8-sig')
    print('rows repaired in %s: %d' % (os.path.basename(target), n))

# keep the workbook consistent too
import openpyxl
wb_path = os.path.join(SITE, 'data', 'FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx')
pf = pd.read_csv(os.path.join(SITE, 'data', 'panel_final.csv'))
book = pd.read_excel(wb_path, sheet_name=None)
book['Panel_final'] = pf
with pd.ExcelWriter(wb_path, engine='openpyxl') as xw:
    for name, df in book.items():
        df.to_excel(xw, sheet_name=name, index=False)
wbk = openpyxl.load_workbook(wb_path)
for ws in wbk.worksheets:
    ws.freeze_panes = 'A2'
    for col in ws.columns:
        w = max((len(str(c.value)) for c in col[:200] if c.value is not None), default=10)
        ws.column_dimensions[col[0].column_letter].width = min(max(w + 2, 10), 62)
wbk.save(wb_path)
print('workbook Panel_final sheet refreshed')
