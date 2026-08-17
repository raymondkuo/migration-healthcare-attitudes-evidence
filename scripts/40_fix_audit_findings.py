# -*- coding: utf-8 -*-
"""Fix the genuine defects confirmed from AUDIT_report_site_vs_VERIFIED.md:

  1. api_snapshots.csv published a Eurostat URL containing a literal "..."      -> HTTP 400
  2. api_snapshots.csv published OECD URLs with a "DSD_MIG*" wildcard           -> HTTP 404
  3. api_publisher_snapshots.csv published population.un.org/wpp/downloads      -> HTTP 404
  4. README.md grade headline said 1,699 but its breakdown summed to 1,692
  5. Workbook README sheet said 89/87 document sources while the site says 78/76
  6. Workbook Source_register sheet was stale (102 cells) vs the site register
  7. Root workbook was not byte-identical to the site workbook
"""
import os, re, json, shutil, hashlib
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(BASE, 'migration-data-archive')
D = os.path.join(SITE, 'data')
WB_SITE = os.path.join(D, 'FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx')
WB_ROOT = os.path.join(BASE, 'FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx')
F2 = os.path.join(BASE, 'migration_population_panel_40countries_2010-2022.xlsx')

EUROSTAT_REAL = ('https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/migr_eipre'
                 '?format=JSON&lang=EN&age=TOTAL&sex=T&unit=PER&citizen=TOTAL&reason=TOTAL'
                 '&apprehen=TOTAL&geo=CH&geo=PT&geo=SE&sinceTimePeriod=2010&untilTimePeriod=2023')
UN_WPP_PAGE = 'https://population.un.org/wpp/'

# ---------------------------------------------------------------- 1 & 2: API query URLs
lg = pd.read_excel(F2, sheet_name='Long_all_observations')
oecd_real = {}
for u in sorted({str(x) for x in lg.source_url if 'sdmx.oecd.org' in str(x)}):
    m = re.search(r'/([A-Z]{3})\.W\.A\.(B1[45])\.', u)
    if m:
        oecd_real['oecd/%s_%s.json' % (m.group(1), m.group(2))] = u
print('real OECD URLs recovered: %d' % len(oecd_real))

p = os.path.join(D, 'api_snapshots.csv')
api = pd.read_csv(p)
fixed = 0
for i, r in api.iterrows():
    f = str(r['file'])
    if f in oecd_real:
        api.at[i, 'query_url'] = oecd_real[f]
        fixed += 1
    elif f == 'eurostat_migr_eipre_CH_PT_SE_2010_2023.json':
        api.at[i, 'query_url'] = EUROSTAT_REAL
        fixed += 1
assert not api.query_url.astype(str).str.contains(r'\.\.\.|DSD_MIG\*', regex=True).any()
api.to_csv(p, index=False, encoding='utf-8-sig')
print('api_snapshots.csv: %d query URLs corrected; 0 placeholders remain' % fixed)

# ---------------------------------------------------------------- 3: UN WPP publisher page
p = os.path.join(D, 'api_publisher_snapshots.csv')
pub = pd.read_csv(p)
m = pub.key == 'un_wpp_2024'
old = pub.loc[m, 'page_url'].iloc[0]
pub.loc[m, 'page_url'] = UN_WPP_PAGE
if 'note' not in pub.columns:
    pub['note'] = ''
pub.loc[m, 'note'] = ('The WPP download portal path used at capture time now returns 404; the '
                      'dataset home page is the stable address. The archived mirror is the page '
                      'as captured on 2026-08-17.')
pub.to_csv(p, index=False, encoding='utf-8-sig')
print('api_publisher_snapshots.csv: UN WPP page URL\n   %s\n-> %s' % (old, UN_WPP_PAGE))

# ---------------------------------------------------------------- 5 & 6: workbook sheets
book = pd.read_excel(WB_SITE, sheet_name=None)

# 6. refresh Source_register from the site's current register
site_reg = pd.read_csv(os.path.join(D, 'source_register.csv'))
before = book['Source_register'].shape
book['Source_register'] = site_reg
print('Source_register sheet refreshed: %s -> %s' % (before, site_reg.shape))

# 5. reconcile the README sheet's document-source wording and grade counts
panel = pd.read_csv(os.path.join(D, 'panel_final.csv'))
V7 = ['population', 'foreign_born', 'foreign_nationals', 'irregular_stock',
      'irregular_proxy_overstayers', 'irregular_proxy_detections',
      'irregular_proxy_absconded_workers']
g = pd.Series([x for v in V7 for x in panel[v + '_grade'].dropna()
               if str(x).strip()]).value_counts()
GA, GB, GC, GD = (int(g.get(k, 0)) for k in 'ABCD')
TOT = GA + GB + GC + GD
print('grade counts (all %d displayed values): A %d B %d C %d D %d' % (TOT, GA, GB, GC, GD))

rd = book['README']
c0, c1 = rd.columns[0], rd.columns[1]
REPL = {
 'Document sources cited': ('Document source citations',
                            '78 distinct country-source citations across 72 URLs'),
 '  retrieved to country folders': ('  archived in the country folders', '76 of 78'),
 '  not retrievable': ('  not retrievable by any means', '2'),
 'A - re-derived from a machine-readable official source, exact match': (None, str(GA)),
 'B - official statistical source, consistent': (
     'B - confirmed by reading the retrieved source document', str(GB)),
 'C - source document retrieved, modelled estimate not re-derivable': (None, str(GC)),
 'D - cited source could not be retrieved': (None, str(GD)),
}
n = 0
for i, r in rd.iterrows():
    k = str(r[c0]).strip()
    if k in REPL:
        newk, newv = REPL[k]
        if newk:
            rd.at[i, c0] = newk
        rd.at[i, c1] = newv
        n += 1
book['README'] = rd
print('README sheet: %d rows reconciled' % n)

with pd.ExcelWriter(WB_SITE, engine='openpyxl') as xw:
    for name, df in book.items():
        df.to_excel(xw, sheet_name=name, index=False)
import openpyxl
wb = openpyxl.load_workbook(WB_SITE)
for ws in wb.worksheets:
    ws.freeze_panes = 'A2'
    for col in ws.columns:
        w = max((len(str(c.value)) for c in col[:200] if c.value is not None), default=10)
        ws.column_dimensions[col[0].column_letter].width = min(max(w + 2, 10), 62)
wb.save(WB_SITE)

# re-export the CSVs so site tables and workbook cannot drift apart again
for sheet, fn in [('README', 'readme.csv'), ('Source_register', 'source_register.csv')]:
    pd.read_excel(WB_SITE, sheet_name=sheet).to_csv(
        os.path.join(D, fn), index=False, encoding='utf-8-sig')
print('re-exported readme.csv and source_register.csv from the workbook')

# ---------------------------------------------------------------- 7: sync the root copy
shutil.copy2(WB_SITE, WB_ROOT)
h = lambda f: hashlib.sha256(open(f, 'rb').read()).hexdigest()
print('\nworkbook identity now:')
for f in (WB_ROOT, WB_SITE):
    print('  %8d  %s  %s' % (os.path.getsize(f), h(f)[:16], os.path.relpath(f, BASE)))
assert h(WB_ROOT) == h(WB_SITE), 'root and site workbook still differ'

json.dump({'grades': {'A': GA, 'B': GB, 'C': GC, 'D': GD, 'total': TOT}},
          open(os.path.join(BASE, 'verification', '_grade_counts.json'), 'w'), indent=1)
print('\nall workbook fixes applied')
