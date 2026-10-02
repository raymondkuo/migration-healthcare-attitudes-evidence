# -*- coding: utf-8 -*-
"""Analysis-ready country-year extract.

panel_final.csv carries the evidence apparatus - source, URL, grade, reference date,
verification note and derivation for every value, 83 columns. That is what a reviewer
needs and what an analyst has to wade through. This writes the same verified numbers as
a clean rectangle: one row per country-year, values and shares, with a compact quality
grade beside each variable and the caveats stated on the first sheet.

Two naming decisions, both deliberate:

  *_pct_of_pop here is a PERCENTAGE (0-100). The archive's own *_pct_pop columns hold
  the same quantity as a proportion (0-1) despite the name - Australia 2010 reads
  0.2669 for a country that is 26.7% foreign-born. Renamed and rescaled so the number
  cannot be read 100x wrong.

  The three irregular-migration measures stay in three columns and are never summed
  into one. They count different things and cover different countries.
"""
import os
import sys
import pandas as pd

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SITE, 'scripts'))
D = os.path.join(SITE, 'data')
from i18n import COUNTRY                                            # noqa: E402

p = pd.read_csv(os.path.join(D, 'panel_final.csv'))
hist = pd.read_csv(os.path.join(D, 'revision_history.csv')).fillna('')
LAST = str(hist[hist.amends_data == 'yes'].date.max())
out = pd.DataFrame()

# ---------------------------------------------------------------- identifiers
out['iso3'] = p['iso3']
out['iso2'] = p['iso2']
out['country'] = p['country']
out['country_zh'] = p['country'].map(lambda c: COUNTRY.get(c, ''))
out['year'] = p['year'].astype(int)
out['in_issp_wave1'] = p['in_wave1'].astype(int)
out['in_issp_wave2'] = p['in_wave2'].astype(int)

# ---------------------------------------------------------------- population
out['population'] = p['population']
out['population_unwpp'] = p['population_un_wpp2024']
out['population_gap_pct'] = p['population_wb_vs_unwpp_pct'].round(3)

# ---------------------------------------------------------------- migrant stock
out['foreign_born'] = p['foreign_born']
out['foreign_born_pct_of_pop'] = (p['foreign_born_pct_pop'] * 100).round(3)
out['foreign_nationals'] = p['foreign_nationals']
out['foreign_nationals_pct_of_pop'] = (p['foreign_nationals_pct_pop'] * 100).round(3)

# ---------------------------------------------------------------- irregular migration
out['irregular_stock'] = p['irregular_stock']
out['irregular_stock_pct_of_pop'] = (p['irregular_stock_pct_pop'] * 100).round(3)
out['irregular_stock_is_midpoint'] = (
    p['irregular_stock_derived'].astype(str).str.strip().eq('yes').map({True: 'yes', False: ''}))
out['irregular_stock_published_range'] = p['irregular_stock_published_range'].fillna('')
out['overstayers'] = p['irregular_proxy_overstayers']
out['overstayers_pct_of_pop'] = (p['irregular_proxy_overstayers_pct_pop'] * 100).round(3)
out['detections'] = p['irregular_proxy_detections']
out['detections_per_1000_pop'] = p['irregular_proxy_detections_per_1000_pop'].round(4)
out['absconded_workers_tw'] = p['irregular_proxy_absconded_workers']

# ---------------------------------------------------------------- quality grades
GRADES = [('grade_population', 'population'),
          ('grade_foreign_born', 'foreign_born'),
          ('grade_foreign_nationals', 'foreign_nationals'),
          ('grade_irregular_stock', 'irregular_stock'),
          ('grade_overstayers', 'irregular_proxy_overstayers'),
          ('grade_detections', 'irregular_proxy_detections')]
for new, src in GRADES:
    col = src + '_grade'
    out[new] = p[col].fillna('') if col in p.columns else ''

out = out.sort_values(['country', 'year']).reset_index(drop=True)

# ---------------------------------------------------------------- codebook
CODE = [
 ('iso3', 'ISO 3166-1 alpha-3 country code.', ''),
 ('iso2', 'ISO 3166-1 alpha-2 country code.', ''),
 ('country', 'Country name, English.', ''),
 ('country_zh', 'Country name, Traditional Chinese (Taiwan usage).', ''),
 ('year', 'Calendar year, 2010-2022.', 'See the reference-date caution on the README sheet.'),
 ('in_issp_wave1', '1 if the country is in the first ISSP wave used by the study.', ''),
 ('in_issp_wave2', '1 if the country is in the second ISSP wave.', ''),
 ('population', 'Total resident population. World Bank WDI SP.POP.TOTL, mid-year, for 39 '
                'countries; Taiwan is Ministry of the Interior year-end registered population.',
  'All 507 World Bank values reproduced exactly from the live API.'),
 ('population_unwpp', 'Alternative total population, UN WPP 2024, 1 July, all 40 countries.',
  'All 520 values reproduced exactly. Pick ONE denominator and use it throughout.'),
 ('population_gap_pct', 'Percentage gap between the two population series, '
                        '(World Bank - UN WPP) / UN WPP x 100.',
  '426 of 520 country-years differ; 25 differ by more than 3%.'),
 ('foreign_born', 'Residents born outside the reporting country.',
  'Includes people who have since naturalised, so it exceeds foreign_nationals almost '
  'everywhere. Missing for Japan and Taiwan.'),
 ('foreign_born_pct_of_pop', 'foreign_born as a PERCENTAGE of population (0-100).',
  'Computed on the World Bank population column.'),
 ('foreign_nationals', 'Residents holding a foreign nationality, including reported stateless '
                       'persons.',
  'Closest to "non-nationals" for healthcare entitlement. Recommended main regressor. Not '
  'compiled by jus soli countries: absent for AUS, IND, ISR, NZL, RUS, ZAF.'),
 ('foreign_nationals_pct_of_pop', 'foreign_nationals as a PERCENTAGE of population (0-100).', ''),
 ('irregular_stock', 'Estimated number of foreign residents without authorisation.',
  'STOCK. 12 of 40 countries. Estimation methods differ by country and are not comparable.'),
 ('irregular_stock_pct_of_pop', 'irregular_stock as a PERCENTAGE of population (0-100).', ''),
 ('irregular_stock_is_midpoint', '"yes" where the source publishes a RANGE and this cell is its '
                                 'midpoint.',
  '13 values, all Pew Research ranges. Use irregular_stock_published_range for any claim '
  'about level.'),
 ('irregular_stock_published_range', 'The range the source actually published, where it '
                                     'published a range rather than a point estimate.', ''),
 ('overstayers', 'Administrative count of people recorded as overstaying a permit.',
  'STOCK, register-based. Only 5 countries. Counts those already recorded, not the whole '
  'unauthorised population.'),
 ('overstayers_pct_of_pop', 'overstayers as a PERCENTAGE of population (0-100).', ''),
 ('detections', 'Third-country nationals found to be illegally present during the year '
                '(Eurostat migr_eipre).',
  'FLOW of enforcement events, NOT people and NOT a stock: one person can be detected more '
  'than once. Driven by enforcement intensity and position on a migration route.'),
 ('detections_per_1000_pop', 'detections per 1,000 residents.',
  'Provided because a flow count cannot be compared with a stock share.'),
 ('absconded_workers_tw', 'Taiwan only: migrant workers recorded as having absconded '
                          '(失聯移工), Ministry of Labor.',
  'A SUBSET of overstayers. Kept in its own column so it is never read as the same series.'),
 ('grade_population', 'Evidence grade for the population value.', 'A / B / C - see README.'),
 ('grade_foreign_born', 'Evidence grade for foreign_born.', ''),
 ('grade_foreign_nationals', 'Evidence grade for foreign_nationals.', ''),
 ('grade_irregular_stock', 'Evidence grade for irregular_stock.', ''),
 ('grade_overstayers', 'Evidence grade for overstayers.', ''),
 ('grade_detections', 'Evidence grade for detections.', ''),
]
codebook = pd.DataFrame(CODE, columns=['column', 'definition', 'caution'])
missing = [c for c in out.columns if c not in set(codebook.column)]
assert not missing, 'columns with no codebook entry: %s' % missing

# ---------------------------------------------------------------- coverage
cov = []
for c in ['population', 'population_unwpp', 'foreign_born', 'foreign_nationals',
          'irregular_stock', 'overstayers', 'detections', 'absconded_workers_tw']:
    s = out[out[c].notna()]
    yrs = sorted(s.year.unique())
    cov.append(dict(variable=c, observations=len(s), pct_of_520=round(100 * len(s) / 520, 1),
                    countries=s.iso3.nunique(),
                    years='%d-%d' % (yrs[0], yrs[-1]) if yrs else '',
                    countries_missing_entirely=', '.join(
                        sorted(set(out.iso3) - set(s.iso3))) or '(none)'))
coverage = pd.DataFrame(cov)

README = [
 ('Migration and population panel, 40 countries, 2010-2022 - analysis extract', ''),
 ('', ''),
 ('What this is', 'One row per country-year: 520 rows, 40 countries, 13 years. The same '
                  'verified numbers as the evidence archive, without the per-value source '
                  'apparatus.'),
 ('Companion archive', 'https://raymondkuo.github.io/migration-healthcare-attitudes-evidence'),
 ('Full evidence version', 'data/panel_final.csv in that archive carries source, URL, grade, '
                           'reference date and verification note on EVERY value, and each number '
                           'on the website links to its archived source document.'),
 ('Built', 'Sources first retrieved and verified 2026-08-17. Data last revised %s. Every '
           'amendment since is dated on the Revision_history sheet.' % LAST),
 ('', ''),
 ('HOW THE NUMBERS WERE CHECKED', ''),
 ('Value-by-value comparisons', '2,737 against live sources, across 21 sources at 100%.'),
 ('Grade A', 'Re-derived from a machine-readable official source and matched exactly, or '
             'corrected against one. 1,573 values (92.6%).'),
 ('Grade B', 'Confirmed by reading the retrieved source document. 112 values (6.6%).'),
 ('Grade C', 'Source retrieved, but the value is a modelled or range-based estimate that '
             'cannot be mechanically re-derived. 13 values (0.8%).'),
 ('Grade D', 'None. Values that could not be traced to an archived source were deleted, not '
             'published: 1 value removed (Russia 2020 irregular stock).'),
 ('', ''),
 ('READ BEFORE USING', ''),
 ('Percentages', 'Every *_pct_of_pop column is a PERCENTAGE, 0-100. The archive workbook '
                 'stores the same quantity as a proportion, 0-1, under the name *_pct_pop.'),
 ('Two population series', 'population (World Bank, mid-year) and population_unwpp (UN WPP, '
                           '1 July) both defensible. 426 of 520 country-years differ, 25 by more '
                           'than 3% (worst: Bulgaria -5.5%, Israel +5.0%). Choose one and hold '
                           'it across all countries.'),
 ('Recommended regressor', 'foreign_nationals_pct_of_pop - the share of residents who are '
                           'non-nationals, closest to the entitlement question. Second choice '
                           'foreign_born_pct_of_pop: wider coverage but it counts naturalised '
                           'citizens as migrants.'),
 ('Do NOT pool the irregular columns', 'irregular_stock, overstayers and detections measure '
                                       'different things over different countries. detections is '
                                       'a FLOW of enforcement events - one person can be counted '
                                       'more than once - and is not a population. Adding or '
                                       'substituting them produces a meaningless series.'),
 ('Irregular migration as a regressor', 'Not internationally comparable. Use as an ordinal '
                                        'salience signal at most; prefer '
                                        'foreign_nationals_pct_of_pop for a continuous '
                                        'cross-national term.'),
 ('Reference dates', 'Eurostat and OECD stocks are measured at 1 January, so a row labelled '
                     'year Y describes 31 December of Y-1. Consider lagging when matching to '
                     'mid-year survey fieldwork.'),
 ('foreign_born vs foreign_nationals', 'Different concepts, never mix them in one series. UN '
                                       'DESA and OECD/Eurostat foreign-born also diverge sharply '
                                       'for Turkey (+144%), Czechia (+55%), Slovakia (+42%) and '
                                       'Portugal (-18%).'),
 ('Series breaks', '20 country-series draw on more than one source across the period. The '
                   'Data_quality sheet of the archive workbook flags which.'),
 ('Genuine jumps', 'Large 2015 and 2021-22 movements in detections are real (migration crisis, '
                   'Balkan route, Ukraine), not data errors.'),
]
readme = pd.DataFrame(README, columns=['Item', 'Detail'])

# ---------------------------------------------------------------- write
xlsx = os.path.join(D, 'CLEAN_country_year_panel_2010-2022.xlsx')
with pd.ExcelWriter(xlsx, engine='openpyxl') as xw:
    readme.to_excel(xw, sheet_name='README', index=False)
    out.to_excel(xw, sheet_name='Country_year', index=False)
    codebook.to_excel(xw, sheet_name='Codebook', index=False)
    coverage.to_excel(xw, sheet_name='Coverage', index=False)
    hist.to_excel(xw, sheet_name='Revision_history', index=False)

import openpyxl
from openpyxl.styles import Alignment, Font
wb = openpyxl.load_workbook(xlsx)
for ws in wb.worksheets:
    ws.freeze_panes = 'B2' if ws.title == 'Country_year' else 'A2'
    for cell in ws[1]:
        cell.font = Font(bold=True)
    for col in ws.columns:
        w = max((len(str(c.value)) for c in col[:400] if c.value is not None), default=10)
        ws.column_dimensions[col[0].column_letter].width = min(max(w + 2, 11), 72)
for ws in (wb['README'], wb['Codebook']):
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical='top')
    ws.column_dimensions['B'].width = 86
    if ws.title == 'Codebook':
        ws.column_dimensions['C'].width = 62
wb.save(xlsx)

csv = os.path.join(D, 'clean_country_year_panel_2010-2022.csv')
out.to_csv(csv, index=False, encoding='utf-8-sig')

print('wrote %s' % os.path.relpath(xlsx, SITE))
print('      %s' % os.path.relpath(csv, SITE))
print()
print('rows %d | countries %d | years %d-%d | columns %d'
      % (len(out), out.iso3.nunique(), out.year.min(), out.year.max(), len(out.columns)))
print()
print(coverage.to_string(index=False, max_colwidth=44))
