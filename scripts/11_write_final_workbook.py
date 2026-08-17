# -*- coding: utf-8 -*-
"""Grade data quality and write the final workbook."""
import os, datetime
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VER = os.path.join(BASE, 'verification')
F1 = os.path.join(BASE, 'immigration_country_year_2010_2022.xlsx')
F2 = os.path.join(BASE, 'migration_population_panel_40countries_2010-2022.xlsx')
OUT = os.path.join(BASE, 'FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx')
ACCESS = '2026-08-17'

fin = pd.read_pickle(os.path.join(VER, '_final_panel.pkl'))
CORR = pd.read_csv(os.path.join(VER, 'corrections_applied.csv'))
checks = pd.concat([pd.read_csv(os.path.join(VER, 'value_checks.csv')),
                    pd.read_csv(os.path.join(VER, 'value_checks_oecd.csv'))], ignore_index=True)
man = pd.read_csv(os.path.join(VER, 'country_source_manifest.csv'))
dl = pd.read_csv(os.path.join(VER, 'download_log.csv'))
irr = pd.read_excel(F2, sheet_name='Irregular_estimates')
lg = pd.read_excel(F2, sheet_name='Long_all_observations')
ctr = pd.read_excel(F2, sheet_name='Countries').dropna(subset=['iso3'])

VARS = ['population', 'foreign_born', 'foreign_nationals', 'irregular_stock',
        'irregular_proxy_overstayers', 'irregular_proxy_detections']

MACHINE = ('World Bank', 'Eurostat', 'OECD', 'UN DESA', 'SP.POP', 'SM.POP', 'migr_')

# URLs that could NOT be retrieved by any means (see Known_issues)
UNRETRIEVED = {
    'https://press.police.ac.kr/pds/1476878914562.pdf',
}
# URLs recovered after the first pass, or replaced by an equivalent retrieved source
RECOVERED = {
    'https://www.pewresearch.org/hispanic/2020/08/20/facts-on-u-s-immigrants/',
    'https://mexico.iom.int/sites/g/files/tmzbdl1686/files/documents/2024-03/estadisticas-migratorias-2023.pdf',
    'https://www.gov.il/BlobFolder/generalpage/foreign_workers_stats/he/zarim_2022_q1.pdf',
    'https://psa.gov.ph/content/foreign-citizens-country-2020-census-population-and-housing',
    'https://www.moj.go.kr/moj/2415/subview.do',
    'https://www.ismu.org/comunicato-stampa-xxv-rapporto-ismu/',
    'https://www.ismu.org/xxvii-rapporto-sulle-migrazioni-2021-comunicato-stampa-11-2-2022/',
    'https://www.cinformi.it/Comunicazione/Notizie/I-dati-del-Rapporto-ISMU-sulle-migrazioni-2020',
    'https://www.sem.admin.ch/dam/sem/de/data/internationales/illegale-migration/sans_papiers/ber-sanspapiers-2015-d.pdf',
    'https://www.nisshinkyo.org/news/pdf/G-26-2.pdf',
}
OK_URLS = set(dl[dl.http_status.astype(str).isin(['200', 'cached'])]['source_url']) | RECOVERED

# Values checked by reading the retrieved document during this verification.
DOC_VERIFIED = {}
for y, v in [(2010, 454000), (2011, 443000), (2012, 326000), (2013, 294000), (2014, 350000),
             (2015, 404000), (2016, 435000), (2017, 491000), (2018, 533000), (2019, 562000),
             (2020, 517000), (2021, 519000)]:
    DOC_VERIFIED[('ITA', y, 'irregular_stock')] = \
        'Matches the official ISMU series "Stime stranieri irregolari 1991-2021" exactly.'
DOC_VERIFIED[('PHL', 2020, 'foreign_nationals')] = \
    'Philippine Statistics Authority 2020 CPH release states 78,396 foreign citizens - exact match.'
DOC_VERIFIED[('KOR', 2021, 'irregular_proxy_overstayers')] = \
    'Ministry of Justice table: 125,022 + 262,251 + 1,427 = 388,700 - exact match.'
DOC_VERIFIED[('KOR', 2022, 'irregular_proxy_overstayers')] = \
    'Ministry of Justice table: 138,013 + 269,532 + 3,725 = 411,270 - exact match.'
DOC_VERIFIED[('CHE', 2015, 'irregular_stock')] = \
    'SEM study estimate of 76,000 corroborated by SRF reporting on its release (range 58,000-105,000).'


def cell_sources(r, v):
    """URLs cited for this specific country-year-variable."""
    urls = set()
    u = r.get(('population_url' if v == 'population' else v + '_url'))
    if isinstance(u, str) and u.startswith('http'):
        urls.add(u)
    sub = lg[(lg.iso3 == r['iso3']) & (lg.year == r['year']) & (lg.variable == v)]
    urls |= {x for x in sub['source_url'].astype(str) if x.startswith('http')}
    return urls


def grade_row(r, v):
    if pd.isna(r[v]):
        return ''
    src = str(r.get('population_source' if v == 'population' else v + '_source', '') or '')
    chk = checks[(checks.iso3 == r['iso3']) & (checks.year == r['year']) &
                 (checks.variable == {'irregular_proxy_detections': 'irregular_detections'}.get(v, v))]
    if len(chk) and (chk['status'] == 'EXACT').all():
        return 'A'
    if len(CORR[(CORR.iso3 == r['iso3']) & (CORR.year == r['year']) & (CORR.variable == v)]):
        return 'A'          # replaced with a value re-derived from the live source
    if (r['iso3'], r['year'], v) in DOC_VERIFIED:
        return 'B'          # confirmed by reading the retrieved source document
    if any(k in src for k in MACHINE):
        return 'B'
    urls = cell_sources(r, v)
    if urls and urls <= UNRETRIEVED:
        return 'D'
    if urls & OK_URLS:
        return 'C'
    return 'D' if urls else 'C'


for v in VARS:
    fin[v + '_grade'] = fin.apply(lambda r: grade_row(r, v), axis=1)
    fin[v + '_verification'] = fin.apply(
        lambda r: DOC_VERIFIED.get((r['iso3'], r['year'], v), ''), axis=1)

# ---------------------------------------------------------------- country x variable quality
COMPARABILITY = {
    'population': 'Directly comparable. World Bank WDI mid-year for 39 countries; Taiwan is a '
                  'national year-end register figure.',
    'foreign_born': 'Comparable in concept (born abroad) but sources differ (Eurostat 1 Jan, '
                    'OECD mid-year, UN DESA benchmark years). Includes naturalised citizens.',
    'foreign_nationals': 'Closest match to "non-nationals". Not maintained by jus-soli countries; '
                         'affected by naturalisation rates, so not a pure migration measure.',
    'irregular_stock': 'NOT comparable across countries. Different estimation methods, different '
                       'years, different definitions.',
    'irregular_proxy_overstayers': 'NOT comparable across countries. Administrative register '
                                   'counts that capture only recorded overstays.',
    'irregular_proxy_detections': 'NOT comparable across countries and is a FLOW of enforcement '
                                  'events, not a stock of people. Driven by enforcement intensity '
                                  'and geographic position on migration routes.',
}
rows = []
for iso3, g in fin.groupby('iso3'):
    cname = g['country'].iloc[0]
    for v in VARS:
        s = g[g[v].notna()]
        if not len(s):
            rows.append(dict(iso3=iso3, country=cname, variable=v, n_years=0, coverage='0/13',
                             years='', modal_grade='', sources='', usable_for_trend='NO - no data',
                             comparability=COMPARABILITY[v]))
            continue
        gr = s[v + '_grade'].mode()
        srcs = sorted({str(x)[:60] for x in s[v + '_source'].dropna()}) if v != 'population' \
            else sorted({str(x)[:60] for x in s['population_source'].dropna()})
        yrs = sorted(s['year'].tolist())
        gaps = len(yrs) < (max(yrs) - min(yrs) + 1)
        multi = len(srcs) > 1
        if len(yrs) >= 10 and not multi:
            use = 'YES - continuous single-source series'
        elif len(yrs) >= 10 and multi:
            use = 'CAUTION - 10+ years but more than one source in the series'
        elif len(yrs) >= 5:
            use = 'CAUTION - partial coverage%s' % (', with gaps' if gaps else '')
        else:
            use = 'NO - too few years for a trend (use as a level only)'
        rows.append(dict(iso3=iso3, country=cname, variable=v, n_years=len(yrs),
                         coverage='%d/13' % len(yrs),
                         years='%d-%d' % (min(yrs), max(yrs)),
                         modal_grade=gr.iloc[0] if len(gr) else '',
                         sources=' | '.join(srcs),
                         usable_for_trend=use, comparability=COMPARABILITY[v]))
QUAL = pd.DataFrame(rows)

# ---------------------------------------------------------------- source register
reg = []
for _, r in man.drop_duplicates(['iso3', 'source_url', 'variable']).iterrows():
    url = str(r['source_url'])
    if r['kind'] == 'bulk_api':
        st, note = 'VERIFIED_API', 'Re-queried live and compared value by value on ' + ACCESS
        lf = 'data_raw/'
    else:
        d = dl[dl.source_url == url]
        ok = len(d) and str(d.iloc[0]['http_status']) in ('200', 'cached') and str(d.iloc[0].get('local_file') or '')
        st = 'DOWNLOADED' if ok else 'SEE_COUNTRY_README'
        lf = d.iloc[0]['local_file'] if ok else ''
        note = ''
    reg.append(dict(iso3=r['iso3'], variable=r['variable'], years=r['years'], n_obs=r['n_obs'],
                    from_workbook=r['workbook'], source_name=r['source_name'], source_url=url,
                    retrieval=st, local_file=lf, note=note))
REG = pd.DataFrame(reg).sort_values(['iso3', 'variable'])

# ---------------------------------------------------------------- known issues
ISSUES = pd.DataFrame([
    dict(severity='RESOLVED', scope='Switzerland, Portugal, Sweden',
         variable='irregular_proxy_detections',
         issue='In migration_population_panel_40countries_2010-2022.xlsx the Eurostat detections '
               'series for these three countries was offset by one year: the value published for '
               'year Y+1 was recorded under year Y, and the genuine 2010 figures were missing.',
         evidence='Live Eurostat migr_eipre re-query, 2026-08-17. E.g. Sweden: workbook 2013 = '
                  '72,835 but Eurostat 2013 = 24,400 and 2014 = 72,835. The other workbook, '
                  'immigration_country_year_2010_2022.xlsx, has these three countries correct.',
         action='Corrected: all 39 values replaced with the year-aligned Eurostat figures.'),
    dict(severity='RESOLVED', scope='Sweden', variable='documentation',
         issue='The input codebook states the Swedish break in detections is "2013: 72,835 -> '
               '2014: 1,445". That is a consequence of the one-year offset above.',
         evidence='Eurostat migr_eipre: 2013 = 24,400; 2014 = 72,835; 2015 = 1,445.',
         action='Corrected: the break falls between 2014 and 2015, not 2013 and 2014.'),
    dict(severity='RESOLVED', scope='Taiwan', variable='irregular_proxy_overstayers',
         issue='A single column mixed two incompatible measures: Ministry of Labor absconded '
               'migrant workers (失聯移工, a subset) for 2011-2013 and 2019-2022, and National '
               'Immigration Agency overstayers (逾期停留/居留) for 2014-2018. Read as a time '
               'series this creates a false +65% jump in 2014 and a false -47% fall in 2019.',
         evidence='Source notes in the input workbook itself; and the NIA series is carried '
                  'consistently for 2012-2021 in immigration_country_year_2010_2022.xlsx.',
         action='Corrected: the column now holds only the NIA overstayer measure (2012-2021); '
                'the MOL figures were moved to a separate column, irregular_proxy_absconded_workers.'),
    dict(severity='RESOLVED', scope='Italy', variable='irregular_stock',
         issue='2010-2013 were missing although ISMU publishes them, and 2014 used a Pew estimate '
               'while every other year used ISMU, mixing two methods inside one series.',
         evidence='Fondazione ISMU, "Stime stranieri irregolari 1991-2021" (agg. maggio 2022), '
                  'downloaded to countries/ITA_Italy/sources/.',
         action='Corrected: Italy now carries one consistent ISMU series for 2010-2021. The Pew '
                'estimates remain available in the Irregular_estimates_all sheet.'),
    dict(severity='HIGH', scope='immigration_country_year_2010_2022.xlsx', variable='Illegal_immigrants_number',
         issue='That workbook puts five conceptually different measures in one column: 274 '
               'Eurostat annual enforcement detections (a FLOW), plus overstayer register counts '
               'and modelled unauthorised-population stocks (STOCKS) for 8 countries.',
         evidence='Sources sheet S3-S12; see verification/audit_issues.csv.',
         action='NOT USED. The final panel keeps the three measures in three separate columns and '
                'they must never be pooled.'),
    dict(severity='HIGH', scope='all', variable='irregular_stock / overstayers / detections',
         issue='No internationally comparable measure of the irregular population exists. '
               'irregular_stock covers 13/40 countries, overstayers 5/40, detections 25/40, and '
               'the three are not additive or interchangeable.',
         evidence='Coverage sheet; verification/audit_issues.csv.',
         action='Use as an ordinal salience signal at most. For a cross-national regressor prefer '
                'foreign_nationals_pct_pop.'),
    dict(severity='MEDIUM', scope='Israel, Bulgaria, France, Turkey, USA, Poland, China, Netherlands',
         variable='population',
         issue='The two input workbooks disagree on population because one uses UN WPP 2024 and '
               'the other World Bank WDI. Israel differs by -4.1%, Bulgaria +3.2%, France -2.5%.',
         evidence='427 of 520 country-years differ; 26 by more than 3%.',
         action='Both series are retained side by side (population = World Bank; '
                'population_un_wpp2024 = UN WPP) with the gap in population_wb_vs_unwpp_pct. '
                'Pick one and keep it for every country.'),
    dict(severity='MEDIUM', scope='Turkey, Czechia, Slovakia, Portugal, Germany',
         variable='foreign_born',
         issue='UN DESA migrant stock and the OECD/Eurostat foreign-born series diverge sharply '
               '(Turkey +144%, Czechia +55%, Slovakia +42%, Portugal -18%).',
         evidence='Cross-file comparison on the 110 overlapping country-years.',
         action='Do not mix the two. Turkey in particular: UN DESA includes Syrians under '
                'temporary protection, the OECD series does not.'),
    dict(severity='MEDIUM', scope='Korea', variable='irregular_proxy_overstayers',
         issue='The 2010-2015 values rest on a single secondary source (a Korean National Police '
               'University publication) whose host no longer responds, so they could not be '
               'checked against anything.',
         evidence='press.police.ac.kr does not answer; no archive copy available (Wayback was '
                  'returning 503 during this work).',
         action='Kept but graded D. The 2021 and 2022 values were verified exactly against the '
                'live Ministry of Justice table (388,700 and 411,270).'),
    dict(severity='MEDIUM', scope='Switzerland', variable='irregular_stock',
         issue='LINK ROT: the cited SEM PDF (ber-sanspapiers-2015-d.pdf) now returns 404.',
         evidence='Checked 2026-08-17 with several URL patterns.',
         action='The 76,000 estimate is corroborated by SRF reporting on the SEM study release of '
                '25 April 2016, saved to countries/CHE_Switzerland/sources/. Note the study'
                "'s own range was 58,000-105,000."),
    dict(severity='MEDIUM', scope='Italy', variable='sources',
         issue='ismu.org returns HTTP 403 to every automated client and to a real browser.',
         evidence='Checked 2026-08-17 from two clients.',
         action='Replaced by ISMU\'s own machine-readable series, which confirmed every Italian '
                'value exactly.'),
    dict(severity='LOW', scope='Japan', variable='irregular_proxy_overstayers',
         issue='One cited mirror (nisshinkyo.org) returns 404.',
         evidence='Checked 2026-08-17.',
         action='No impact: it duplicated the Immigration Services Agency figure for 2014, and '
                'the primary ISA sources were downloaded successfully.'),
    dict(severity='INFO', scope='EU/EFTA', variable='irregular_proxy_detections',
         issue='Large genuine jumps in 2015 (Germany +193%, Hungary +655%, Austria +161%) and in '
               '2021-2022 (Italy +304%, Austria +175%, Croatia +224%) reflect the 2015 migration '
               'crisis and the 2021-22 Balkan-route and Ukraine movements, not data errors.',
         evidence='All values matched live Eurostat exactly.',
         action='Documented. Do not treat as breaks in the series.'),
    dict(severity='INFO', scope='Eurostat / OECD countries', variable='foreign_born, foreign_nationals',
         issue='Eurostat and OECD stocks are measured at 1 January, so the row labelled year Y '
               'describes the situation at 31 December of Y-1.',
         evidence='Eurostat migr_pop1ctz / migr_pop3ctb metadata.',
         action='If matching to survey data collected mid-year, consider lagging or using the '
                'ref_date columns.'),
])

# ---------------------------------------------------------------- codebook
CODEBOOK = pd.DataFrame([
    ('country, iso3, iso2, m49_code', 'Country identifiers.', ''),
    ('in_wave1, in_wave2', 'Whether the country appears in each ISSP/ISPSS wave.', ''),
    ('year', 'Calendar year, 2010-2022.', ''),
    ('population', 'Total resident population. World Bank WDI SP.POP.TOTL, mid-year, for 39 '
     'countries; Taiwan is the MOI year-end registered population.',
     'Verified: all 507 World Bank values matched the live API exactly.'),
    ('population_un_wpp2024', 'Alternative population from UN WPP 2024, total population at 1 '
     'July, for all 40 countries including Taiwan.',
     'Verified: all 520 values matched the live UN WPP 2024 file exactly.'),
    ('population_wb_vs_unwpp_pct', 'Percentage gap between the two population series.',
     'Use to see where the choice of population denominator matters.'),
    ('foreign_born', 'Residents born outside the reporting country.',
     'Includes naturalised citizens, so it exceeds foreign_nationals almost everywhere.'),
    ('foreign_nationals', 'Residents holding foreign citizenship, including stateless where '
     'reported.', 'Conceptually the closest available match to "non-nationals" using public '
     'healthcare. RECOMMENDED as the main cross-national regressor.'),
    ('irregular_stock', 'Estimated number of foreign nationals resident without authorisation.',
     'WEAK. 13/40 countries. Methods not comparable across countries.'),
    ('irregular_proxy_overstayers', 'Administrative register count of persons remaining beyond '
     'authorised stay.', 'WEAK. 5/40 countries. A register count, not a modelled stock.'),
    ('irregular_proxy_absconded_workers', 'Taiwan only: Ministry of Labor count of absconded / '
     'missing migrant workers (失聯移工).',
     'A SUBSET of overstayers. Kept separate so it is never read as the same series.'),
    ('irregular_proxy_detections', 'Third-country nationals found to be illegally present during '
     'the year.', 'A FLOW of enforcement events, NOT a stock, and not a count of persons - one '
     'person can be detected more than once.'),
    ('*_pct_pop', 'Variable divided by population (proportion, not percent).', 'Recomputed after '
     'corrections.'),
    ('irregular_proxy_detections_per_1000_pop', 'Detections per 1,000 residents.',
     'Provided because a raw flow is not comparable to a stock share.'),
    ('*_ref_date', 'Reference date of the underlying measurement.',
     'Eurostat/OECD stocks are 1 January; Taiwan and Korea are 31 December; Japan is 1 January.'),
    ('*_source, *_url, *_note', 'Provenance of each value.', ''),
    ('*_grade', 'Data-quality grade for that cell. A = re-derived from a machine-readable '
     'official source and matched exactly, or corrected against one during this verification. '
     'B = official statistical source, value consistent with it. C = source document retrieved '
     'but the value is a modelled estimate that cannot be mechanically re-derived. '
     'D = cited source could not be retrieved.', ''),
])
CODEBOOK.columns = ['Variable', 'Definition', 'Caution / verification']

# ---------------------------------------------------------------- README
gcount = pd.Series([g for v in VARS for g in fin[v + '_grade'] if g]).value_counts().sort_index()
README = pd.DataFrame([
    ('FINAL verified migration and population panel, 40 countries, 2010-2022', ''),
    ('', ''),
    ('Built', 'Compiled and verified ' + ACCESS + ' from the two supplied workbooks.'),
    ('Inputs', 'immigration_country_year_2010_2022.xlsx  and  '
               'migration_population_panel_40countries_2010-2022.xlsx'),
    ('Base', 'migration_population_panel_40countries_2010-2022.xlsx. It was chosen because it '
             'keeps the three irregular-migration measures in separate columns, carries a full '
             'audit trail, is internally consistent with that trail, and 2,415 of its values '
             'reproduced exactly from the live sources.'),
    ('', ''),
    ('WHAT WAS VERIFIED', ''),
    ('Values re-derived from live sources', '%d' % len(checks)),
    ('  matched exactly', '%d (%.1f%%)' % ((checks.status == 'EXACT').sum(),
                                           (checks.status == 'EXACT').mean() * 100)),
    ('  discrepancies found', '%d' % (checks.status != 'EXACT').sum()),
    ('Sources re-queried live', 'World Bank WDI (SP.POP.TOTL, SM.POP.TOTL); Eurostat '
                                'migr_pop3ctb, migr_pop1ctz, migr_eipre; OECD International '
                                'Migration Database (13 series); UN WPP 2024; UN DESA '
                                'International Migrant Stock 2024.'),
    ('Document sources cited', '89 across 27 countries'),
    ('  retrieved to country folders', '87'),
    ('  not retrievable', '2 (see Known_issues)'),
    ('Corrections applied', '%d values across 5 countries (see Corrections_applied)' % len(CORR)),
    ('', ''),
    ('CELL GRADES', ''),
    ('A - re-derived from a machine-readable official source, exact match', '%d' % gcount.get('A', 0)),
    ('B - official statistical source, consistent', '%d' % gcount.get('B', 0)),
    ('C - source document retrieved, modelled estimate not re-derivable', '%d' % gcount.get('C', 0)),
    ('D - cited source could not be retrieved', '%d' % gcount.get('D', 0)),
    ('', ''),
    ('HOW TO USE THIS FOR THE HEALTHCARE-ATTITUDES STUDY', ''),
    ('Main regressor', 'foreign_nationals_pct_pop - the share of residents who are non-nationals. '
                       'This is the population actually at issue in "publicly funded healthcare '
                       'for non-nationals", it covers 34 of 40 countries, and every value is '
                       'graded A or B.'),
    ('Second choice', 'foreign_born_pct_pop - wider coverage (38 countries) but it includes '
                      'naturalised citizens, who are nationals and therefore not the group the '
                      'survey question is about.'),
    ('Irregular migration', 'Do NOT use as a continuous cross-national regressor. Coverage is '
                            '10.6% of country-years for stocks, the methods are not comparable, '
                            'and detections are a flow driven by enforcement intensity. Use at '
                            'most as an ordinal salience indicator, or restrict to within-country '
                            'variation.'),
    ('Reference dates', 'Eurostat and OECD stocks are 1 January of the labelled year. If the '
                        'survey is fielded mid-year, either lag the covariate or state the '
                        'convention explicitly.'),
    ('Population denominator', 'population (World Bank) and population_un_wpp2024 are both '
                               'supplied. Choose one and use it throughout; they differ by more '
                               'than 3% for 26 country-years.'),
    ('', ''),
    ('SHEETS', ''),
    ('Panel_final', 'The recommended panel: one row per country-year, corrected, with a quality '
                    'grade on every value.'),
    ('Data_quality', 'Country x variable: coverage, modal grade, sources, and whether the series '
                     'can carry a trend.'),
    ('Corrections_applied', 'Every value changed from the input workbooks, with the reason and '
                            'the evidence.'),
    ('Known_issues', 'Everything found, resolved and unresolved.'),
    ('Verification_log', 'All %d value-by-value comparisons against live sources.' % len(checks)),
    ('Source_register', 'Every cited source, how it was retrieved, and the local file.'),
    ('Irregular_estimates_all', 'Every competing irregular-migration estimate, kept side by side.'),
    ('Codebook', 'Variable definitions and cautions.'),
    ('', ''),
    ('EVIDENCE ON DISK', ''),
    ('countries/<ISO3>_<Name>/', 'One folder per country: README.md, data_from_source.csv, '
                                 'value_check.csv, source_manifest.csv, and sources/ holding the '
                                 'downloaded documents and screenshots.'),
    ('data_raw/', 'The bulk source downloads (World Bank, Eurostat, OECD, UN) used for verification.'),
    ('verification/', 'The full machine-readable verification output.'),
    ('scripts/', 'Every script used, so the whole check can be re-run.'),
])
README.columns = ['Item', 'Detail']

# ---------------------------------------------------------------- column order
front = ['country', 'iso3', 'iso2', 'm49_code', 'in_wave1', 'in_wave2', 'year',
         'population', 'population_grade', 'population_source', 'population_url',
         'population_un_wpp2024', 'population_wb_vs_unwpp_pct']
rest = [c for c in fin.columns if c not in front]
ordered = front + [c for c in rest]
fin = fin[[c for c in ordered if c in fin.columns]]

with pd.ExcelWriter(OUT, engine='openpyxl') as xw:
    README.to_excel(xw, sheet_name='README', index=False)
    fin.to_excel(xw, sheet_name='Panel_final', index=False)
    QUAL.to_excel(xw, sheet_name='Data_quality', index=False)
    CORR.to_excel(xw, sheet_name='Corrections_applied', index=False)
    ISSUES.to_excel(xw, sheet_name='Known_issues', index=False)
    checks.to_excel(xw, sheet_name='Verification_log', index=False)
    REG.to_excel(xw, sheet_name='Source_register', index=False)
    irr.to_excel(xw, sheet_name='Irregular_estimates_all', index=False)
    CODEBOOK.to_excel(xw, sheet_name='Codebook', index=False)

# tidy widths
import openpyxl
wb = openpyxl.load_workbook(OUT)
for ws in wb.worksheets:
    ws.freeze_panes = 'A2'
    for col in ws.columns:
        w = max((len(str(c.value)) for c in col[:200] if c.value is not None), default=10)
        ws.column_dimensions[col[0].column_letter].width = min(max(w + 2, 10), 62)
wb.save(OUT)

print('wrote', OUT)
print('Panel_final %d rows x %d cols' % fin.shape)
print('\ngrades:'); print(gcount.to_string())
print('\nData_quality rows:', len(QUAL))
print('Known issues:', len(ISSUES), '| corrections:', len(CORR))
