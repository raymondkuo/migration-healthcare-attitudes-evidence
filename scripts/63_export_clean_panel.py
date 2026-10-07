# -*- coding: utf-8 -*-
"""Analysis-ready country-year extract.

panel_final.csv carries the evidence apparatus - source, URL, grade, reference date,
verification note and derivation for every value, over 90 columns. That is what a reviewer
needs and what an analyst has to wade through. This writes the same verified numbers as
a clean rectangle: one row per country-year, values and shares, with a compact quality
grade, source type and flag beside each variable and the caveats stated on the first sheet.

Every count quoted in the README and codebook is computed from the data files here, never
typed in: the first version of this text carried numbers that went stale after later edits.

Two naming decisions, both deliberate:

  *_pct_of_pop here is a PERCENTAGE (0-100). The archive's own *_pct_pop columns hold
  the same quantity as a proportion (0-1) despite the name - Australia 2010 reads
  0.2669 for a country that is 26.7% foreign-born. Renamed and rescaled so the number
  cannot be read 100x wrong.

  The three irregular-migration measures stay in three columns and are never summed
  into one. They count different things and cover different countries.

The file names still say 2010-2022 although the panel now starts in 2001: they were
published under that name and links to them must keep working.
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
vlog = pd.read_csv(os.path.join(D, 'verification_log.csv'))
ovl = pd.read_csv(os.path.join(D, 'extension_overlap_check.csv'))
spl = pd.read_csv(os.path.join(D, 'extension_splice_summary.csv'))
dele = pd.read_csv(os.path.join(D, 'deleted_values.csv'))
lchg = pd.read_csv(os.path.join(D, 'extension_large_changes.csv'))
dq = pd.read_csv(os.path.join(D, 'data_quality.csv'))
LAST = str(hist[hist.amends_data == 'yes'].date.max())
out = pd.DataFrame()


def n(x):
    return format(int(x), ',')


def codes(s):
    return ', '.join(sorted(s)) if len(s) else '(none)'


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
# UN DESA declares citizenship (data type C), not birthplace, for some countries. Those cells are
# not birthplace counts, so they sit in their own columns and foreign_born stays birthplace only
# (audit finding F04); panel_final.csv keeps them in foreign_born with foreign_born_concept saying so.
typec = p['foreign_born_concept'].fillna('').str.contains('citizenship basis')
out['foreign_born'] = p['foreign_born'].where(~typec)
out['foreign_born_pct_of_pop'] = (p['foreign_born_pct_pop'] * 100).round(3).where(~typec)
out['foreign_born_source_type'] = p['foreign_born_source_type'].fillna('').where(~typec, '')
out['foreign_born_flag'] = p['foreign_born_flag'].fillna('').where(~typec, '')
out['un_stock_citizenship_basis'] = p['foreign_born'].where(typec)
out['un_stock_citizenship_basis_pct_of_pop'] = (p['foreign_born_pct_pop'] * 100).round(3).where(typec)
out['foreign_nationals'] = p['foreign_nationals']
out['foreign_nationals_pct_of_pop'] = (p['foreign_nationals_pct_pop'] * 100).round(3)
out['foreign_nationals_source_type'] = p['foreign_nationals_source_type'].fillna('')
out['foreign_nationals_flag'] = p['foreign_nationals_flag'].fillna('')

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
out['grade_un_stock_citizenship_basis'] = out['grade_foreign_born'].where(typec, '')
out['grade_foreign_born'] = out['grade_foreign_born'].where(~typec, '')

out = out.sort_values(['country', 'year']).reset_index(drop=True)

# ---------------------------------------------------------------- numbers quoted in the text
NR, NC = len(out), out.iso3.nunique()
Y0, Y1 = int(out.year.min()), int(out.year.max())
NY = Y1 - Y0 + 1
name_of = dict(zip(out.iso3, out.country))

gap = p['population_wb_vs_unwpp_pct'].dropna()
n_gap_any = int((gap.abs() > 1e-9).sum())
n_gap_3 = int((gap.abs() > 3).sum())
worst_neg = p.loc[gap.idxmin()]
worst_pos = p.loc[gap.idxmax()]
n_wb = int((out.population.notna() & (out.iso3 != 'TWN')).sum())
n_wb_post = int((out.population.notna() & (out.iso3 != 'TWN') & (out.year >= 2010)).sum())

gcount = pd.Series([g for c in [c for c, _ in GRADES] + ['grade_un_stock_citizenship_basis']
                    for g in out[c] if str(g).strip()]).value_counts()
gtot = int(gcount.sum())


def gline(k):
    return '%s values (%.1f%%)' % (n(gcount.get(k, 0)), 100 * gcount.get(k, 0) / gtot)


fb_none = set(out.iso3) - set(out[out.foreign_born.notna()].iso3)
fn_none = set(out.iso3) - set(out[out.foreign_nationals.notna()].iso3)
fn_only_census = {i for i, g in out[out.foreign_nationals.notna()].groupby('iso3')
                  if set(g.foreign_nationals_source_type) <= {'census', 'survey'}}
irr_c = out[out.irregular_stock.notna()].iso3.nunique()
ovs_c = out[out.overstayers.notna()].iso3.nunique()
mid_n = int((out.irregular_stock_is_midpoint == 'yes').sum())
irr_first = int(out[out.irregular_stock.notna() | out.overstayers.notna()
                    | out.detections.notna()].year.min())
brk = int(dq.usable_for_trend.astype(str).str.startswith('CAUTION - 10+').sum())

as_rec = vlog[vlog.stage == 'as_received']
after = vlog[vlog.stage == 'after_correction']
n_src = vlog.source.nunique()
bad_rec = int((as_rec.status != 'EXACT').sum())
ok_after = int((after.status == 'EXACT').sum())

ovl_n, ovl_same = int(ovl.cells_compared.sum()), int(ovl.identical.sum())
NSPL = len(spl)
LARGE = spl[spl.mean_gap_pct.abs() >= 5]
worst_spl = spl.loc[spl.mean_gap_pct.abs().idxmax()]

type_c = set(p[typec].iso3)
n_type_c = int(typec.sum())
_both = p[p.foreign_born.notna() & p.foreign_nationals.notna() & (p.foreign_born < p.foreign_nationals)]
n_below = len(_both)
below_out = _both[['iso3', 'country', 'year', 'foreign_born', 'foreign_nationals', 'foreign_born_source_type',
                   'foreign_nationals_source_type', 'foreign_born_concept', 'foreign_born_flag',
                   'foreign_nationals_flag']].copy()
below_out['foreign_born_to_foreign_nationals'] = (below_out.foreign_born / below_out.foreign_nationals).round(3)
st_fb = out[out.foreign_born.notna()].foreign_born_source_type.value_counts()
st_fn = out[out.foreign_nationals.notna()].foreign_nationals_source_type.value_counts()


def st_text(s):
    return ', '.join('%s %s' % (k, n(v)) for k, v in s.items())


new_cells = {v: int(p[v + '_collected_on'].notna().sum()) for v in
             ('population', 'population_un_wpp2024', 'foreign_born', 'foreign_nationals')}

# ---------------------------------------------------------------- codebook
FLAGS = {
 'splice': "Filled from a different source family than the country's 2010-2022 series; the "
           'mean gap on the overlapping years is under 5% (extension_splice_summary.csv).',
 'splice (large gap)': 'Same, but the mean gap on the overlapping years is 5% or more: treat '
                       'the join as a break in the series.',
 'splice; derived by subtraction': 'United Kingdom only: total population minus UK-born (ONS '
                                   'Annual Population Survey), not a published foreign-born '
                                   'count; also a splice.',
 'un_estimate': 'UN DESA International Migrant Stock 2024: a modelled estimate for the '
                'benchmark year (2005, 2010, 2015, 2020), not a national statistic.',
 'un_estimate; declared citizenship basis': "UN DESA declares this country's stock on a "
                                            'citizenship basis (data type C), although the '
                                            'column is foreign-born; see the known issues.',
 'comparability caution': 'Taiwan 2001-2011: the input workbook stated that this series begins '
                          'in 2012 and that earlier years are not comparable; the table read '
                          'shows no break, but one cannot be ruled out.',
 'includes former-USSR births': 'Russia, 2002 census: the count includes people born in other '
                                'former Soviet republics.',
 'Eurostat flag: ...': 'The flag Eurostat attached to the observation, for example break '
                       'in time series, estimated or provisional. Recorded for every Eurostat '
                       'cell, including those published before the extension.',
}
used = set(out.foreign_born_flag) | set(out.foreign_nationals_flag)
unknown = {f for f in used if f and f not in FLAGS and not f.startswith('Eurostat flag: ')}
assert not unknown, 'flag values with no codebook text: %s' % sorted(unknown)
flag_text = ' | '.join('%s: %s' % (k, v) for k, v in FLAGS.items())

CODE = [
 ('iso3', 'ISO 3166-1 alpha-3 country code.', ''),
 ('iso2', 'ISO 3166-1 alpha-2 country code.', ''),
 ('country', 'Country name, English.', ''),
 ('country_zh', 'Country name, Traditional Chinese (Taiwan usage).', ''),
 ('year', 'Calendar year, %d-%d.' % (Y0, Y1),
  'See the reference-date caution on the README sheet. The irregular-migration columns start '
  'in %d: nothing earlier was collected for them.' % irr_first),
 ('in_issp_wave1', '1 if the country is in the first ISSP wave used by the study.', ''),
 ('in_issp_wave2', '1 if the country is in the second ISSP wave.', ''),
 ('population', 'Total resident population. World Bank WDI SP.POP.TOTL, mid-year, for 39 '
                'countries; Taiwan is year-end registered population (Ministry of the Interior; '
                '2001-2009 read from the National Development Council Statistical Data Book).',
  'All %s World Bank values come from the archived live API response; the %s for 2010-2022 '
  'were also re-compared on 2026-10-07 and reproduced exactly. Taiwan is the registered '
  '(household-registration) population, which excludes foreign residents, so its shares have a '
  'different denominator from every other country; 2001-2009 is rounded to thousands, 2010-2022 '
  'is exact.' % (n(n_wb), n(n_wb_post))),
 ('population_unwpp', 'Alternative total population, UN WPP 2024, 1 July, all %d countries.' % NC,
  'All %s values come from the archived UN WPP file. Pick ONE denominator and use it '
  'throughout.' % n(out.population_unwpp.notna().sum())),
 ('population_gap_pct', 'Percentage gap between the two population series, '
                        '(World Bank - UN WPP) / UN WPP x 100.',
  '%s of %s country-years differ; %s differ by more than 3%%.'
  % (n(n_gap_any), n(len(gap)), n(n_gap_3))),
 ('foreign_born', 'Residents born outside the reporting country.',
  'Includes people who have since naturalised, so it exceeds foreign_nationals almost '
  'everywhere. BIRTHPLACE counts only: the %d UN DESA stocks that UN declares on a citizenship '
  'basis are in un_stock_citizenship_basis. Missing entirely for %s. Before 2010 some values come '
  'from a census, a survey or a UN estimate or were joined from a second source: read '
  'foreign_born_source_type and foreign_born_flag before using them as a trend.'
  % (n_type_c, codes(fb_none))),
 ('un_stock_citizenship_basis', 'UN DESA international migrant stock for countries whose stock UN '
                                  'declares on a CITIZENSHIP basis (data type C): China, India, '
                                  'Philippines, Suriname, Thailand; 2005, 2010, 2015, 2020.',
  'Not a birthplace count and not interchangeable with foreign_born. Not moved into '
  'foreign_nationals either: its population universe and estimate status have not been checked '
  'against national citizenship counts. A modelled UN benchmark, not a national statistic.'),
 ('un_stock_citizenship_basis_pct_of_pop', 'un_stock_citizenship_basis as a PERCENTAGE of '
                                          'population (0-100).', ''),
 ('foreign_born_pct_of_pop', 'foreign_born as a PERCENTAGE of population (0-100).',
  'Computed on the World Bank population column.'),
 ('foreign_born_source_type', 'Kind of source behind the foreign_born value: annual (register '
                              'or annual statistical release), census, survey, un_estimate '
                              '(UN DESA modelled stock) or other.',
  'Blank where there is no value. Census, survey and un_estimate cells are measured at one '
  'date; do not treat them as a continuous series with the annual cells.'),
 ('foreign_born_flag', 'Why the value needs a caution, blank where nothing does. ' + flag_text, ''),
 ('foreign_nationals', 'Residents holding a foreign nationality, including reported stateless '
                       'persons.',
  'Closest to "non-nationals" for healthcare entitlement. Recommended main regressor. Not '
  'compiled by jus soli countries: absent entirely for %s; census or survey values only for %s.'
  % (codes(fn_none), codes(fn_only_census))),
 ('foreign_nationals_pct_of_pop', 'foreign_nationals as a PERCENTAGE of population (0-100).', ''),
 ('foreign_nationals_source_type', 'Kind of source behind the foreign_nationals value; same '
                                    'categories as foreign_born_source_type.', ''),
 ('foreign_nationals_flag', 'Why the value needs a caution, blank where nothing does; same '
                            'vocabulary as foreign_born_flag.', ''),
 ('irregular_stock', 'Estimated number of foreign residents without authorisation.',
  'STOCK. %d of %d countries. Estimation methods differ by country and are not comparable.'
  % (irr_c, NC)),
 ('irregular_stock_pct_of_pop', 'irregular_stock as a PERCENTAGE of population (0-100).', ''),
 ('irregular_stock_is_midpoint', '"yes" where the source publishes a RANGE and this cell is its '
                                 'midpoint.',
  '%d values, all Pew Research ranges. Use irregular_stock_published_range for any claim '
  'about level.' % mid_n),
 ('irregular_stock_published_range', 'The range the source actually published, where it '
                                     'published a range rather than a point estimate.', ''),
 ('overstayers', 'Administrative count of people recorded as overstaying a permit.',
  'STOCK, register-based. Only %d countries. Counts those already recorded, not the whole '
  'unauthorised population.' % ovs_c),
 ('overstayers_pct_of_pop', 'overstayers as a PERCENTAGE of population (0-100).', ''),
 ('detections', 'Persons found or apprehended as illegally present during the calendar year, as the '
                'source counts them. Eurostat (migr_eipre): third-country nationals found to be illegally '
                'present.',
  'An annual FLOW of enforcement detections, NOT a stock and not an estimate of the unauthorised '
  'population. The unit differs by source: Eurostat counts persons, each once within the reference '
  'year, rounded to the nearest 5; Mexico counts EVENTS (a person can be recorded more than once); '
  'Turkey counts irregular migrants apprehended, Syrians under temporary protection excluded. The '
  'same person can appear in different years. Driven by enforcement intensity and position on a '
  'migration route.'),
 ('detections_per_1000_pop', 'detections per 1,000 residents.',
  'Provided because a flow count cannot be compared with a stock share; the unit differs by '
  'source (see detections).'),
 ('absconded_workers_tw', 'Taiwan only: migrant workers recorded as having absconded '
                          '(失聯移工), Ministry of Labor.',
  'A SUBSET of overstayers. Kept in its own column so it is never read as the same series.'),
 ('grade_population', 'Evidence grade for the population value. A: decoded from a machine-readable '
                       'official source; B: read from an archived document; C: published estimate or '
                       'range; D: none published.',
  'A grade says where a value was read from, not how precise it is (Taiwan 2001-2009 population is '
  'rounded to thousands) or whether it is comparable across countries.'),
 ('grade_foreign_born', 'Evidence grade for foreign_born.', ''),
 ('grade_foreign_nationals', 'Evidence grade for foreign_nationals.', ''),
 ('grade_un_stock_citizenship_basis', 'Evidence grade for un_stock_citizenship_basis.', ''),
 ('grade_irregular_stock', 'Evidence grade for irregular_stock.', ''),
 ('grade_overstayers', 'Evidence grade for overstayers.', ''),
 ('grade_detections', 'Evidence grade for detections.', ''),
]
codebook = pd.DataFrame(CODE, columns=['column', 'definition', 'caution'])
missing = [c for c in out.columns if c not in set(codebook.column)]
assert not missing, 'columns with no codebook entry: %s' % missing
extra = [c for c in codebook.column if c not in set(out.columns)]
assert not extra, 'codebook entries for columns that do not exist: %s' % extra

# ---------------------------------------------------------------- coverage
cov = []
for c in ['population', 'population_unwpp', 'foreign_born', 'un_stock_citizenship_basis', 'foreign_nationals',
          'irregular_stock', 'overstayers', 'detections', 'absconded_workers_tw']:
    s = out[out[c].notna()]
    yrs = sorted(s.year.unique())
    cov.append(dict(variable=c, observations=len(s), pct_of_rows=round(100 * len(s) / NR, 1),
                    countries=s.iso3.nunique(),
                    years='%d-%d' % (yrs[0], yrs[-1]) if yrs else '',
                    countries_missing_entirely=', '.join(
                        sorted(set(out.iso3) - set(s.iso3))) or '(none)'))
coverage = pd.DataFrame(cov)

README = [
 ('Migration and population panel, %d countries, %d-%d - analysis extract' % (NC, Y0, Y1), ''),
 ('', ''),
 ('What this is', 'One row per country-year: %s rows, %d countries, %d years. The same verified '
                  'numbers as the evidence archive, without the per-value source apparatus.'
                  % (n(NR), NC, NY)),
 ('File name', 'The file names still say 2010-2022 because they were published under that name '
               'and existing links must keep working. The data now run %d-%d.' % (Y0, Y1)),
 ('Companion archive', 'https://raymondkuo.github.io/migration-healthcare-attitudes-evidence'),
 ('Full evidence version', 'data/panel_final.csv in that archive carries source, URL, grade, '
                           'reference date and verification note on EVERY value, and each number '
                           'on the website links to its archived source document.'),
 ('Built', 'Sources first retrieved and verified 2026-08-17. Data last revised %s. Every '
           'amendment since is dated on the Revision_history sheet.' % LAST),
 ('', ''),
 ('WHAT THE 2026-10-07 EXTENSION ADDED', ''),
 ('Years added', 'Collected on 2026-10-07 for 2001-2009 (Taiwan foreign nationals also 2010-2011): %s population values, %s UN WPP population '
                     'values, %s foreign_born values and %s foreign_nationals values, where '
                     'the first release (2010-2022) had none. Blank cells only were filled: no '
                     'value published earlier was changed.'
                     % (n(new_cells['population']), n(new_cells['population_un_wpp2024']),
                        n(new_cells['foreign_born']), n(new_cells['foreign_nationals']))),
 ('Source type and flag columns', 'foreign_born and foreign_nationals each carry a '
                                  '*_source_type (annual / census / survey / un_estimate / other) '
                                  'and a *_flag. foreign_born cells: %s. foreign_nationals cells: '
                                  '%s. Flags were also attached to cells published earlier '
                                  '(UN DESA estimates, the flags Eurostat itself attached): '
                                  'metadata only, no value changed.'
                                  % (st_text(st_fb), st_text(st_fn))),
 ('Joins between sources', '%d country-series needed a different source from the one behind '
                           'their 2010-2022 values; every such cell carries the flag "splice". '
                           'The gap between the two sources on the overlapping years was '
                           'measured: %d series have a mean gap of 5%% or more (largest: %s %s, '
                           '%+.1f%%) and those cells carry "splice (large gap)". Treat each '
                           'as a break in the series, not as a continuation.'
                           % (NSPL, len(LARGE), name_of[worst_spl.iso3],
                              worst_spl.variable.replace('_', ' '), worst_spl.mean_gap_pct)),
 ('Large year-on-year changes', '%d changes of 25%% or more between consecutive years involve '
                                 'a year added in the extension. Some may be real, others breaks '
                                 'inside a source; nothing was adjusted. They are listed in '
                                 'data/extension_large_changes.csv of the archive.' % len(lchg)),
 ('Not collected', 'No value was found for some cells and none was invented; blank means no '
                   'verifiable source. Coverage by variable is on the Coverage sheet.'),
 ('', ''),
 ('HOW THE NUMBERS WERE CHECKED', ''),
 ('Value-by-value comparisons', 'These are the RECORDS of the first-release check, not a count of unique '
                                 'current observations: %s comparisons against live sources on 2026-08-17/18, across %d '
                                'sources. As received, %s matched exactly and %d did not; those '
                                'were corrected, and %s corrected values were queried again and '
                                'matched exactly. A per-observation table of the current panel is '
                                'data/current_panel_verification.csv in the archive.'
                                % (n(len(vlog)), n_src, n(len(as_rec) - bad_rec), bad_rec,
                                   n(ok_after))),
 ('Re-check on 2026-10-07', '%s of the values published before the extension were compared '
                            'with fresh responses from Eurostat, OECD, the World Bank and UN '
                            'WPP: %s reproduced exactly.' % (n(ovl_n), n(ovl_same))),
 ('What a grade means', 'A grade says where a value was read from. It does not say how precise '
                         'the value is (rounding is in the cell note), whether the quantity is '
                         'comparable across countries or years (see the flags), or whether the '
                         "source's own estimate is accurate. Grades of first-release values were "
                         'assigned under an earlier wording; the audit of 2026-10-07 re-read the '
                         '19 grade-A values that rest on documents: 18 were regraded B and one '
                         '(Taiwan overstayers 2021) was deleted.'),
 ('Grade A', 'Decoded from a machine-readable official source (API response, open-data file or '
             'official workbook) and matched exactly. %s.' % gline('A')),
 ('Grade B', 'Read from an archived source document (PDF, web page, printed table or chart) in '
             'which the value appears, or summed from figures printed there. %s.' % gline('B')),
 ('Grade C', 'A published estimate or range: the value is the point estimate or the midpoint of the '
             'range. %s.' % gline('C')),
 ('Grade D', 'None. Values that could not be traced to an archived source were deleted, not '
             'published: %d value%s removed (%s).'
             % (len(dele), '' if len(dele) == 1 else 's',
                '; '.join('%s %d %s' % (name_of.get(r.iso3, r.iso3), r.year,
                                        r.variable.replace('_', ' '))
                          for r in dele.itertuples()))),
 ('', ''),
 ('READ BEFORE USING', ''),
 ('Percentages', 'Every *_pct_of_pop column is a PERCENTAGE, 0-100. The archive workbook '
                 'stores the same quantity as a proportion, 0-1, under the name *_pct_pop.'),
 ('Two population series', 'population (World Bank, mid-year) and population_unwpp (UN WPP, '
                           '1 July) both defensible. %s of %s country-years differ, %s by more '
                           'than 3%% (worst: %s %+.1f%% in %d, %s %+.1f%% in %d). Choose one and '
                           'hold it across all countries.'
                           % (n(n_gap_any), n(len(gap)), n(n_gap_3),
                              worst_neg.country, worst_neg.population_wb_vs_unwpp_pct,
                              worst_neg.year, worst_pos.country,
                              worst_pos.population_wb_vs_unwpp_pct, worst_pos.year)),
 ('Recommended regressor', 'foreign_nationals_pct_of_pop - the share of residents who are '
                           'non-nationals, closest to the entitlement question. Second choice '
                           'foreign_born_pct_of_pop: wider coverage but it counts naturalised '
                           'citizens as migrants.'),
 ('Do NOT pool the irregular columns', 'irregular_stock, overstayers and detections measure '
                                       'different things over different countries. detections is '
                                       'an annual FLOW of enforcement detections - Eurostat counts '
                                       'persons once per year, Mexico counts events - and is not a '
                                       'population. Adding or substituting them produces a '
                                       'meaningless series.'),
 ('Irregular migration as a regressor', 'Not internationally comparable. Use as an ordinal '
                                        'salience signal at most; prefer '
                                        'foreign_nationals_pct_of_pop for a continuous '
                                        'cross-national term. These columns start in %d.'
                                        % irr_first),
 ('Reference dates', 'Dates differ by source and are recorded per value in the archive workbook '
                     '(*_ref_date). Eurostat stocks are 1 January, so a row labelled year Y describes '
                     '31 December of Y-1. OECD dates follow the national source: 30 June for '
                     "Australia's foreign-born, 1 January for the foreign population of Japan, Turkey, "
                     'the United Kingdom and Germany, no stated date for several survey- or '
                     'census-based series. Census and survey values describe the census or survey '
                     'date. Years are as the publisher labels them; nothing was shifted. Consider '
                     'lagging when matching to mid-year survey fieldwork.'),
 ('foreign_born vs foreign_nationals', 'Different concepts, never mix them in one series. UN '
                                       'DESA and OECD/Eurostat foreign-born also diverge sharply '
                                       'for Turkey (+144%), Czechia (+55%), Slovakia (+42%) and '
                                       'Portugal (-18%) in 2010-2022.'),
 ('UN DESA type C', 'UN DESA labels the stock of China, India, Japan, the Philippines, '
                    'Suriname, Thailand and Taiwan as based on CITIZENSHIP, yet the first '
                    'release put %s of them in foreign_born. Their %d cells (benchmark years '
                    '2005 to 2020) are therefore in the separate column un_stock_citizenship_basis here, '
                    'and foreign_born holds birthplace counts only; panel_final.csv keeps them '
                    'in foreign_born with foreign_born_concept saying so. They are not moved to '
                    'foreign_nationals: their population universe has not been checked. See the known '
                    'issues.' % (', '.join(sorted(type_c)), n_type_c)),
 ('foreign_born below foreign_nationals', '%d country-years have foreign_born below foreign_nationals '
                                          '(data/foreign_born_below_foreign_nationals.csv). That is not an error '
                                          'rule: the two come from different sources, concepts, dates or '
                                          'universes, and no ordering was forced.' % n_below),
 ('Series breaks', '%d country-series of more than ten years draw on more than one source. The '
                   'Data_quality sheet of the archive workbook flags which.' % brk),
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

below_out.to_csv(os.path.join(D, 'foreign_born_below_foreign_nationals.csv'), index=False, encoding='utf-8-sig')
csv = os.path.join(D, 'clean_country_year_panel_2010-2022.csv')
out.to_csv(csv, index=False, encoding='utf-8-sig')

print('wrote %s' % os.path.relpath(xlsx, SITE))
print('      %s' % os.path.relpath(csv, SITE))
print()
print('rows %d | countries %d | years %d-%d | columns %d'
      % (len(out), out.iso3.nunique(), out.year.min(), out.year.max(), len(out.columns)))
print()
print(coverage.to_string(index=False, max_colwidth=44))
