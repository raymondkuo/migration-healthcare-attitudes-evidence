# -*- coding: utf-8 -*-
"""Internal-consistency and cross-file audit of the two workbooks."""
import os
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VER = os.path.join(BASE, 'verification')
F1 = os.path.join(BASE, 'immigration_country_year_2010_2022.xlsx')
F2 = os.path.join(BASE, 'migration_population_panel_40countries_2010-2022.xlsx')

cy = pd.read_excel(F1, sheet_name='Country-Year Data')
pn = pd.read_excel(F2, sheet_name='Panel')
lg = pd.read_excel(F2, sheet_name='Long_all_observations')
ir = pd.read_excel(F2, sheet_name='Irregular_estimates')

issues = []


def add(sev, area, country, detail):
    issues.append(dict(severity=sev, area=area, country=country, detail=detail))


print('=' * 78)
print('1. CROSS-FILE POPULATION: FILE1 (UN WPP 2024) vs FILE2 (World Bank WDI)')
print('=' * 78)
m = cy[['ISO3', 'Year', 'Population_total_persons']].merge(
    pn[['iso3', 'year', 'population']], left_on=['ISO3', 'Year'], right_on=['iso3', 'year'])
m['pct'] = (m['Population_total_persons'] - m['population']) / m['population'] * 100
g = m.groupby('ISO3')['pct'].agg(['mean', 'min', 'max']).sort_values('mean', key=abs, ascending=False)
print(g.head(12).round(3).to_string())
print('\nrows compared: %d | identical: %d | |diff|>1%%: %d | |diff|>3%%: %d'
      % (len(m), (m['pct'].abs() < 1e-9).sum(), (m['pct'].abs() > 1).sum(), (m['pct'].abs() > 3).sum()))
for iso, r in g.iterrows():
    if abs(r['mean']) > 1:
        add('MEDIUM', 'cross-file population', iso,
            'FILE1 (UN WPP 2024) differs from FILE2 (World Bank WDI) by %.2f%% on average '
            '(range %.2f%% to %.2f%%). The two files are not interchangeable for this country.'
            % (r['mean'], r['min'], r['max']))

print()
print('=' * 78)
print('2. CROSS-FILE IMMIGRANT STOCK: FILE1 (UN DESA IMS) vs FILE2 (foreign_born)')
print('=' * 78)
m2 = cy[cy.Immigrant_stock_total_persons.notna()][['ISO3', 'Year', 'Immigrant_stock_total_persons']].merge(
    pn[['iso3', 'year', 'foreign_born', 'foreign_born_source']],
    left_on=['ISO3', 'Year'], right_on=['iso3', 'year'])
m2 = m2[m2.foreign_born.notna()]
m2['pct'] = (m2['Immigrant_stock_total_persons'] - m2['foreign_born']) / m2['foreign_born'] * 100
g2 = m2.groupby('ISO3')['pct'].agg(['mean', 'min', 'max', 'size']).sort_values('mean', key=abs, ascending=False)
print(g2.head(15).round(2).to_string())
print('\nrows compared: %d | median |diff| = %.2f%%' % (len(m2), m2['pct'].abs().median()))
for iso, r in g2.iterrows():
    if abs(r['mean']) > 5:
        add('MEDIUM', 'cross-file foreign-born', iso,
            'UN DESA migrant stock (FILE1) differs from the FILE2 foreign-born series by %.1f%% '
            'on average. Different concepts/sources; do not mix.' % r['mean'])

print()
print('=' * 78)
print('3. FILE1 "Illegal_immigrants_number": measures mixed in one column')
print('=' * 78)
mm = cy[cy.Illegal_immigrants_number.notna()].groupby(
    ['Illegal_immigrants_measure', 'Illegal_source_id']).agg(
    n=('ISO3', 'size'), countries=('ISO3', 'nunique')).reset_index()
for _, r in mm.iterrows():
    print('  %-4s %3d obs %2dc  %s' % (r['Illegal_source_id'], r['n'], r['countries'],
                                       str(r['Illegal_immigrants_measure'])[:88]))
add('HIGH', 'concept', 'ALL',
    'FILE1 places %d values from %d conceptually different measures (annual enforcement '
    'detections, overstayer register counts, and modelled unauthorised-population stocks) in the '
    'single column Illegal_immigrants_number. These are not comparable across countries and must '
    'not be pooled.' % (len(cy[cy.Illegal_immigrants_number.notna()]), len(mm)))

print()
print('=' * 78)
print('4. Panel vs Long_all_observations consistency (FILE2)')
print('=' * 78)
used = lg[lg.used_in_panel.astype(str).str.lower() == 'yes']
bad = 0
for var, col in [('population', 'population'), ('foreign_born', 'foreign_born'),
                 ('foreign_nationals', 'foreign_nationals'), ('irregular_stock', 'irregular_stock'),
                 ('irregular_proxy_overstayers', 'irregular_proxy_overstayers'),
                 ('irregular_proxy_detections', 'irregular_proxy_detections')]:
    s = used[used.variable == var][['iso3', 'year', 'value']]
    j = s.merge(pn[['iso3', 'year', col]], on=['iso3', 'year'], how='left')
    d = j[(j[col].notna()) & (np.abs(j['value'] - j[col]) > 0.5)]
    miss = j[j[col].isna()]
    print('  %-28s used=%4d  mismatched=%3d  absent_from_panel=%3d' % (var, len(s), len(d), len(miss)))
    bad += len(d)
    for _, r in d.head(5).iterrows():
        add('MEDIUM', 'internal consistency', r['iso3'],
            '%s %d: Long_all_observations says %s but Panel says %s.'
            % (var, r['year'], f"{r['value']:,.0f}", f"{r[col]:,.0f}"))
if bad == 0:
    print('  -> Panel is consistent with its own audit trail.')

print()
print('=' * 78)
print('5. Percent-of-population columns recomputed (FILE2)')
print('=' * 78)
for v in ['foreign_born', 'foreign_nationals', 'irregular_stock']:
    c = v + '_pct_pop'
    s = pn[pn[c].notna() & pn[v].notna() & pn['population'].notna()].copy()
    s['recalc'] = s[v] / s['population']
    s['absdiff'] = (s[c] - s['recalc']).abs()
    n = (s['absdiff'] > 1e-6).sum()
    print('  %-22s n=%4d  disagreeing=%3d  max abs diff=%.2e' % (c, len(s), n, s['absdiff'].max()))
    if n:
        for _, r in s[s['absdiff'] > 1e-6].head(5).iterrows():
            add('LOW', 'derived column', r['iso3'],
                '%s %d: stored %.6f but %s/population = %.6f.' % (c, r['year'], r[c], v, r['recalc']))

print()
print('=' * 78)
print('6. Coverage of each variable (FILE2 Panel)')
print('=' * 78)
tot = len(pn)
for v in ['population', 'foreign_born', 'foreign_nationals', 'irregular_stock',
          'irregular_proxy_overstayers', 'irregular_proxy_detections']:
    n = pn[v].notna().sum()
    nc = pn[pn[v].notna()]['iso3'].nunique()
    print('  %-30s %4d/%d country-years (%4.1f%%)  %2d/40 countries' % (v, n, tot, n / tot * 100, nc))

print()
print('=' * 78)
print('7. Year-on-year jumps > 25% (possible breaks in series)')
print('=' * 78)
brk = []
for v in ['population', 'foreign_born', 'foreign_nationals', 'irregular_proxy_detections']:
    s = pn[['iso3', 'year', v]].dropna().sort_values(['iso3', 'year'])
    s['prev'] = s.groupby('iso3')[v].shift(1)
    s['chg'] = (s[v] / s['prev'] - 1) * 100
    d = s[(s['prev'].notna()) & (s['chg'].abs() > 25)]
    for _, r in d.iterrows():
        brk.append((v, r['iso3'], int(r['year']), r['prev'], r[v], r['chg']))
brk.sort(key=lambda x: -abs(x[5]))
for v, iso, y, a, b, c in brk[:20]:
    print('  %-28s %-4s %d  %12s -> %12s  %+8.1f%%' % (v, iso, y, f'{a:,.0f}', f'{b:,.0f}', c))
    add('INFO' if v == 'irregular_proxy_detections' else 'MEDIUM', 'series break', iso,
        '%s jumps %+.0f%% in %d (%s -> %s). Check for a definition or census re-basing break.'
        % (v, c, y, f'{a:,.0f}', f'{b:,.0f}'))

pd.DataFrame(issues).to_csv(os.path.join(VER, 'audit_issues.csv'), index=False, encoding='utf-8-sig')
print('\nwrote %d audit issues' % len(issues))
