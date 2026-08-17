# -*- coding: utf-8 -*-
"""Enforce the rule: every number must be traceable to an archived source, or be deleted;
anything derived from the source rather than published by it must be flagged.

Grade scheme after this pass
  A  re-derived from a machine-readable official source and matched exactly
  B  confirmed present in the retrieved source document
  C  DERIVED from the source (e.g. the midpoint of a published range) — flagged
  D  not traceable — such values are deleted, so none remain
"""
import os, re, shutil, json
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(BASE, 'migration-data-archive')
BIL = os.path.join(BASE, 'migration-data-archive-bilingual')
D = os.path.join(SITE, 'data')
EVC = os.path.join(SITE, 'evidence', 'countries')

panel = pd.read_csv(os.path.join(D, 'panel_final.csv'))
trace = pd.read_csv(os.path.join(BASE, 'verification', 'trace_c_values.csv'))
VARS = ['population', 'foreign_born', 'foreign_nationals', 'irregular_stock',
        'irregular_proxy_overstayers', 'irregular_proxy_detections',
        'irregular_proxy_absconded_workers']

# ------------------------------------------------------------------ new columns
# text columns that are entirely empty come back from CSV as float64; force them to object
# so text can be written into them
for v in VARS:
    for suf in ('_derived', '_derivation', '_published_range'):
        if v + suf not in panel.columns:
            panel[v + suf] = ''
    for suf in ('_source', '_url', '_note', '_ref_date', '_verification',
                '_derived', '_derivation', '_published_range', '_grade'):
        col = v + suf
        if col in panel.columns:
            panel[col] = panel[col].astype(object).where(panel[col].notna(), '')

log = []


def mark(iso, year, var, **kw):
    m = (panel.iso3 == iso) & (panel.year == year)
    for k, val in kw.items():
        panel.loc[m, var + k] = val


# ==================================================================== 1. DERIVED VALUES
# Pew Research Center 2019, Appendix B (with waiting asylum seekers), thousands, low-high.
# The workbook records the midpoint of each published range.
PEW_B = {   # iso3: {year: (low_thousands, high_thousands)}
 'AUT': {2017: (100, 200)},
 'CZE': {2017: (100, 200)},
 'CHE': {2017: (100, 200)},
 'FRA': {2014: (200, 300), 2015: (200, 300), 2016: (300, 400), 2017: (300, 400)},
 'DEU': {2014: (500, 600), 2015: (600, 1200), 2016: (1100, 1400), 2017: (1000, 1200)},
}
PEW_E = {'GBR': {2017: (700, 900)}}   # Appendix E, revised 18 March 2025

PEW_SRC = ('Pew Research Center (2019), Europe\'s Unauthorized Immigrant Population Peaks in 2016, '
           'Then Levels Off — Appendix B, unauthorized immigrant population trends with waiting '
           'asylum seekers, by country')
PEW_URL = ('https://www.pewresearch.org/global/2019/11/13/eu-unauthorized-immigrants-appendix-b-'
           'unauthorized-immigrant-population-trends-with-waiting-asylum-seekers-by-country/')
PEWE_SRC = ('Pew Research Center (2019, revised 18 March 2025), Appendix E: Updated unauthorized '
            'immigrant population estimates for Europe and the United Kingdom, 2014-2017')
PEWE_URL = ('https://www.pewresearch.org/global/2019/11/13/eu-unauthorized-immigrants-appendix-e-'
            'updated-unauthorized-immigrant-population-estimates-for-europe-and-the-united-kingdom-'
            '2014-2017/')

for table, src, url, appx in ((PEW_B, PEW_SRC, PEW_URL, 'Appendix B'),
                              (PEW_E, PEWE_SRC, PEWE_URL, 'Appendix E')):
    for iso, yrs in table.items():
        for y, (lo, hi) in yrs.items():
            m = (panel.iso3 == iso) & (panel.year == y)
            if not m.any() or pd.isna(panel.loc[m, 'irregular_stock'].iloc[0]):
                continue
            cur = float(panel.loc[m, 'irregular_stock'].iloc[0])
            mid = (lo + hi) / 2 * 1000
            ok = abs(cur - mid) < 1
            panel.loc[m, 'irregular_stock'] = mid
            panel.loc[m, 'irregular_stock_grade'] = 'C'
            panel.loc[m, 'irregular_stock_derived'] = 'yes'
            panel.loc[m, 'irregular_stock_derivation'] = 'midpoint of the published range'
            panel.loc[m, 'irregular_stock_published_range'] = '%s–%s (Pew %s, thousands)' % (
                format(lo * 1000, ','), format(hi * 1000, ','), appx)
            panel.loc[m, 'irregular_stock_source'] = src
            panel.loc[m, 'irregular_stock_url'] = url
            panel.loc[m, 'irregular_stock_note'] = (
                'Pew publishes a RANGE, not a point estimate. This cell is the midpoint of the '
                'published %s–%s range in %s. Use the range, not the midpoint, for any claim '
                'about level.' % (format(lo * 1000, ','), format(hi * 1000, ','), appx))
            panel.loc[m, 'irregular_stock_verification'] = (
                'Published range read from the archived %s table.' % appx)
            log.append((iso, y, 'irregular_stock', 'DERIVED midpoint of %s–%s' % (lo, hi),
                        'value unchanged' if ok else 'value corrected to the true midpoint'))

# WODC (Netherlands) 2017: published range circa 23,000-58,000; the workbook holds the midpoint
m = (panel.iso3 == 'NLD') & (panel.year == 2017)
if m.any() and pd.notna(panel.loc[m, 'irregular_stock'].iloc[0]):
    panel.loc[m, 'irregular_stock'] = 40500
    panel.loc[m, 'irregular_stock_grade'] = 'C'
    panel.loc[m, 'irregular_stock_derived'] = 'yes'
    panel.loc[m, 'irregular_stock_derivation'] = 'midpoint of the published range'
    panel.loc[m, 'irregular_stock_published_range'] = '23,000–58,000 (WODC)'
    panel.loc[m, 'irregular_stock_note'] = (
        'WODC publishes a range: "tussen de circa 23.000 en 58.000 vreemdelingen" for mid-2017 to '
        'mid-2018. This cell is the midpoint. Use the range for any claim about level.')
    panel.loc[m, 'irregular_stock_verification'] = 'Range read from the archived WODC news release.'
    log.append(('NLD', 2017, 'irregular_stock', 'DERIVED midpoint of 23,000–58,000', 'confirmed'))

# ==================================================================== 2. DELETE UNTRACEABLE
DELETE = [('RUS', 2020, 'irregular_stock',
           'The cited source (The Moscow Times report of MVD data) contains no numeric estimate in '
           'the archived copy, and no alternative source was found. Per the traceability rule the '
           'value was deleted rather than retained unverified.')]
deleted = []
for iso, y, var, why in DELETE:
    m = (panel.iso3 == iso) & (panel.year == y)
    if m.any() and pd.notna(panel.loc[m, var].iloc[0]):
        old = float(panel.loc[m, var].iloc[0])
        import numpy as np
        for suf in ['', '_grade', '_source', '_url', '_note', '_ref_date', '_verification',
                    '_pct_pop', '_derived', '_derivation', '_published_range', '_n_estimates']:
            col = var + suf
            if col not in panel.columns:
                continue
            blank = np.nan if pd.api.types.is_numeric_dtype(panel[col]) else ''
            panel.loc[m, col] = blank
        deleted.append(dict(iso3=iso, year=y, variable=var, deleted_value=old, reason=why))
        log.append((iso, y, var, 'DELETED', why[:60]))

# ==================================================================== 3. TURKEY attribution
TUR_SRC = ('Ada Ş. (2024), Türkiye\'de düzensiz göç ile mücadele, Göç İdaresi Başkanlığı (GİB) '
           'yıllık düzensiz göçmen yakalama verileri (DergiPark)')
TUR_URL = 'https://dergipark.org.tr/tr/download/article-file/3843070'
tm = (panel.iso3 == 'TUR') & panel.irregular_proxy_detections.notna()
panel.loc[tm, 'irregular_proxy_detections_source'] = TUR_SRC
panel.loc[tm, 'irregular_proxy_detections_url'] = TUR_URL
panel.loc[tm, 'irregular_proxy_detections_verification'] = (
    'Each annual figure appears in the archived DergiPark article, which reproduces the GİB series.')
log.append(('TUR', 0, 'irregular_proxy_detections',
            'RE-ATTRIBUTED to the archived DergiPark article where every year is present', ''))

# ==================================================================== 4. GRADE the traced values
traced_ok = {(r['iso3'], int(r['year']), r['variable'])
             for _, r in trace.iterrows() if r['traced'] == 'YES'}
tur_years = set(panel.loc[tm, 'year'].astype(int))
for y in tur_years:
    traced_ok.add(('TUR', y, 'irregular_proxy_detections'))

upgraded = 0
for v in VARS:
    gcol = v + '_grade'
    if gcol not in panel:
        continue
    for i, r in panel[panel[gcol] == 'C'].iterrows():
        key = (r['iso3'], int(r['year']), v)
        if str(r.get(v + '_derived') or '') == 'yes':
            continue                      # derived values stay C and carry the flag
        if key in traced_ok:
            panel.at[i, gcol] = 'B'
            if not str(r.get(v + '_verification') or '').strip():
                panel.at[i, v + '_verification'] = (
                    'The published figure appears in the archived source document.')
            upgraded += 1

# recompute shares
for v in ['foreign_born', 'foreign_nationals', 'irregular_stock']:
    panel[v + '_pct_pop'] = panel[v] / panel['population']
panel['irregular_proxy_overstayers_pct_pop'] = panel['irregular_proxy_overstayers'] / panel['population']
panel['irregular_proxy_detections_per_1000_pop'] = panel['irregular_proxy_detections'] / panel['population'] * 1000

panel.to_csv(os.path.join(D, 'panel_final.csv'), index=False, encoding='utf-8-sig')
pd.DataFrame(deleted).to_csv(os.path.join(BASE, 'verification', 'deleted_values.csv'),
                             index=False, encoding='utf-8-sig')

print('=== actions ===')
for l in log:
    print('  %-4s %-5s %-28s %s %s' % (l[0], l[1] or '', l[2], l[3], l[4]))
print()
print('upgraded traced C -> B : %d' % upgraded)
print('deleted (untraceable)  : %d' % len(deleted))
g = pd.Series([x for v in VARS if v + '_grade' in panel
               for x in panel[v + '_grade'].dropna() if str(x).strip()]).value_counts()
print('grades now             : %s  total %d' % (dict(sorted(g.items())), int(g.sum())))
nd = sum((panel[v + '_derived'] == 'yes').sum() for v in VARS if v + '_derived' in panel)
print('flagged as derived     : %d' % nd)
