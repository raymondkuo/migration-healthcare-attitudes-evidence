# Research-use notes: constructs, timing, universes and sensitivity

*Written 2026-10-07 after audit finding F24. Sections 1 and 2 record the authors' decisions of 2026-10-18 (issue #24).
The rest sets out choices that source verification does not settle; the places still marked [AUTHORS] are for the
study's authors. No manuscript result was recalculated in preparing this file.*

## 1. The construct (decided 2026-10-18)

The study analyses the ISSP 2021 item **Q6a** (variable v8), quoted from the ZA8000 Variable Report, PDF page 51
(archived in `evidence/survey/`, with an image of the page):

> How much do you agree or disagree with the following statements? [...] People should have access to publicly
> funded health care even if they do not hold citizenship of [country].

Answers run from 1 strongly agree to 5 strongly disagree (-8 can't choose, -9 no answer). The Taiwan questionnaire
(D2a, page 6) asks: 住在台灣的每個人，就算沒有台灣的身分證，都應該可以使用公共醫療保健服務（例如：健保）. The companion item
**Q7d** (v13, page 61) asks whether access to health care is easier or harder "for citizens of [country] than for
people who do not hold [country's] citizenship".

- **Whom the item names:** people who do not hold the country's citizenship - non-citizens, whatever their legal
  status. Naturalised citizens hold the citizenship and are not named; irregular migrants are not named as a group.
- **Stock, flow or position:** a position on an entitlement. The context that matches it is the size of the group
  named, a stock, never a flow.
- **Main regressor: `foreign_nationals_pct_pop`.** Robustness: `foreign_born_pct_pop`, which also counts naturalised
  citizens. The irregular-migration series are not regressors for this item.
- **Australia** has no annual foreign-national series; its 2021 Census count is in `non_citizens_census` (issue #9),
  for a single-year level or a sensitivity run. **South Africa**'s 2011 census count was not added (issue #10): its
  interviews were in 2021.
- **Taiwan:** "沒有台灣的身分證" (without a Taiwan identity card) may be wider than the register series, which excludes
  people from Mainland China, Hong Kong and Macau; whether to add them in a sensitivity run is open. [AUTHORS]

| Variable | What it counts | Countries (years) | Main caution |
|---|---|---|---|
| foreign_nationals | residents holding a foreign nationality (stateless where reported) | 35 (2001-2022) | falls with naturalisation; no annual series for AUS, IND, ISR, NZL, ZAF |
| foreign_born | residents born abroad | 38 (2001-2022) | includes naturalised citizens; 20 UN citizenship-basis cells are excluded from the extract |
| non_citizens_census | persons who are not citizens, census count, where no annual series exists | 1 (Australia 2021) | a single year, not a series; 5.1% did not state their citizenship |
| irregular_stock | estimated unauthorised residents | 12 (2010-2022) | methods differ by country; not comparable |
| irregular_proxy_overstayers | stock proxy for persons staying beyond authorised stay: register counts (Korea; Taiwan, all categories), official estimates (Japan, New Zealand; Australia's unlawful non-citizens, a broader group) and one component (Israel) | 6 (2010-2022) | heterogeneous; neither a modelled stock of all irregular residents nor an exact count |
| irregular_proxy_detections | annual enforcement detections | 25 (2010-2022) | a flow; unit differs by source (persons / events) |

`health_expenditure_pct_gdp`, added on 2026-10-17, is a context variable, not a measure of the group the item
names: current health expenditure as a percentage of GDP for all 40 countries, 2001-2022 (WHO Global Health
Expenditure Database via the World Bank, checked against WHO's own API; Taiwan from the Ministry of Health and
Welfare, long-term care included only from 2007). It is a spending flow over the year as published, so the stock
date rules in section 2 do not apply to it: use the fieldwork year, or the year before if spending should precede
the attitude, and state which. [AUTHORS]

`unemployment_rate`, added on 2026-10-21, is the same kind of context variable: unemployed persons as a percentage of
the labour force aged 15 and over for all 40 countries, 2001-2022 (ILO modelled estimates, November 2025 edition,
checked against the World Bank's copy; Taiwan from DGBAS). 61 of the values are ILO imputations, not based on
national data, which the ILO says should not be used for country comparisons: China 2001-2022; India 2001-2017; Suriname 2001-2003, 2005-2008, 2017-2022; South Africa 2001-2007; Philippines 2002; Thailand 2002. Run a cross-country model with
and without them (`unemployment_flag` in the extract); China has no value of the other kind. It is an annual average,
so the same timing choice applies as for health expenditure. [AUTHORS]

`vdem_libdem`, added on 2026-10-26, is a third context variable: the V-Dem liberal democracy index (v2x_libdem, 0 to
1) for all 40 countries, 2001-2022, from the V-Dem Country-Year Dataset v16, read from the V-Dem Institute's own data
file and identical to Our World in Data's copy. Each annual value is a day-weighted mean over the calendar year, so the
same timing choice applies again. It is an estimate from expert ratings: V-Dem's 68% interval for every value is in
`data/vdem_source_comparison.csv` (mean width 0.091), and V-Dem re-estimates all past years with each release,
so a model should name the version (v16). Whether to use this index, another democracy measure, or both as a
robustness check is a choice of the study. [AUTHORS]

`gini_index`, added on 2026-10-29, is a fourth context variable: 100 x the Gini coefficient of income or consumption per
person for all 40 countries, but only in the years a household survey exists (679 of 880 country-years); the
gaps are real and are not filled. The World Bank's indicator (Poverty and Inequality Platform) gives 38 countries,
the same platform Taiwan, and the OECD New Zealand, on a different income concept (flagged). Consumption-based values
(flagged, 89) are lower than income-based ones, and flagged breaks mark a change of survey. For a model that needs
one value per country and wave, take the survey nearest to (and not after) the fieldwork, state the distance, and check
the result without the flagged values. [AUTHORS]

## 2. Timing: survey year versus stock date (decided 2026-10-18)

**The primary rule is rule 2 below: the latest stock dated on or before the first interview in the country.** Rules 1
and 3 are the sensitivity checks. The year and month of every interview are in the ISSP data (DATEYR, DATEMO), and
the Variable Report tabulates the year of interview by country (PDF page 778; the month on page 779). The panel ends
in 2022, so for a country interviewed in 2023 or 2024 the rule takes the latest row that exists, and the lag is stated
with the result.

1. Same row year (survey year Y with the row labelled Y);
2. The latest stock dated on or before the start of fieldwork: row Y for a 1 January stock, row Y-1 for a
   31 December stock, and for a 30 June stock row Y-1 if fieldwork starts before 30 June, row Y if after;
3. The nearest stock to the fieldwork date, using `*_ref_date` per value.

A one-year lag (row Y-1 for every source) is not a rule that suits a 1 January stock: labelled Y it is six months
before a mid-year survey in Y, labelled Y-1 eighteen months before. A lag is the nearest row only for 31 December
stocks (and only when fieldwork is in the first half of the year). This corrects the earlier wording of this note.

Reference dates differ by source and are not harmonised: years are as the publisher labels them.

| Variable | Reference date class | Values |
|---|---|---|
| foreign_nationals | 1 January | 469 |
| foreign_nationals | 31 December | 66 |
| foreign_nationals | census date | 40 |
| foreign_nationals | not stated in the API response (see note) | 33 |
| foreign_nationals | other | 3 |
| foreign_born | 1 January | 335 |
| foreign_born | not stated in the API response (see note) | 133 |
| foreign_born | mid-year / 30 June | 60 |
| foreign_born | census date | 34 |
| foreign_born | 31 December | 22 |
| foreign_born | other | 3 |
| foreign_born | survey period | 2 |

## 3. Universes: citizenship, stateless, census

- `foreign_nationals` counts people holding a foreign nationality, **including stateless persons where the source
  reports them**; Russia 2002 (census) is foreign citizens plus stateless; Suriname 2012 is the known foreign
  nationalities with 3,340 of unknown nationality excluded (the residual is kept as an alternative); Taiwan is
  registered foreign residents and excludes mainland Chinese, Hong Kong and Macao residents.
- Source types in the panel - `foreign_born`: annual 538, un_estimate 38, census 8, survey 5; `foreign_nationals`: annual 601, census 7, survey 2, other 1. Census and survey values are
  point-in-time and not interchangeable with annual register series.
- UN DESA declares its stock **on a citizenship basis** for China, India, the Philippines, Suriname and Thailand
  (20 cells). They are not birthplace counts and have not been moved into `foreign_nationals`; decide whether to
  drop them, keep them apart, or test them against national citizenship counts.
- Taiwan's population is the **registered population, which excludes foreign residents**, so its shares have a different
  denominator from every other country.
- Census counts of non-citizens exist that are not in the panel: Australia 2021 (2,808,214; 5.1% did not state) and
  South Africa 2011 (1,692,242 "No" to South African citizenship; the table covers 50,641,580 of 51,770,560).
  Their universes (not stated, visitors, stateless) have to be agreed before they are added. See Known_issues.

## 4. Denominators

`population` (World Bank, mid-year; Taiwan registered year-end) and `population_unwpp` (UN WPP, 1 July) differ by more
than 3% in 30 country-years (25 of them in 2010-2022). Choose one and keep it for every country;
report the other as a sensitivity check.

## 5. Source families and breaks

Run the models on the full panel and again after removing, in turn:

- every `splice (large gap)` cell (the series below differ from the series they were joined to by 5% or more on average);
- every `un_estimate`, `census` and `survey` cell (annual register series only);
- the OECD-only series in `data/migrant_stock_alternatives.csv` instead of the Eurostat/OECD splice;
- country-years flagged `Eurostat flag: break in time series` or `comparability caution` (Taiwan 2001-2011).

| Country (ISO3) | Variable | Signed mean gap | Mean absolute gap | Overlap years |
|---|---|---|---|---|
| CZE | foreign_born | +10.9% | 10.9% | 12 |
| DEU | foreign_born | +1.6% | 7.4% | 13 |
| DNK | foreign_born | -15.5% | 15.5% | 13 |
| LTU | foreign_born | +9.7% | 11.0% | 13 |
| POL | foreign_born | +5.9% | 5.9% | 1 |
| PRT | foreign_born | -5.9% | 21.3% | 2 |
| SVK | foreign_born | +19.7% | 19.7% | 13 |
| PRT | foreign_nationals | +7.0% | 7.0% | 13 |

## 6. Where foreign-born is below foreign-nationals

The codebook's "foreign-born usually exceeds foreign nationals" is not a rule. **24 country-years** have
`foreign_born` below `foreign_nationals` (`data/foreign_born_below_foreign_nationals.csv`). Nothing was
corrected to force an ordering: the two series come from different sources, concepts, dates or universes. Each case
needs a source-and-concept explanation before it is read as an error or as a finding.

| Country | Country-years | Years |
|---|---|---|
| CHL | 5 | 2017, 2019, 2020, 2021, 2022 |
| CZE | 13 | 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021 |
| KOR | 4 | 2005, 2010, 2015, 2020 |
| SVK | 2 | 2010, 2011 |

## 7. What this archive does not establish

It does not establish that any source's own estimate is accurate, that a series is comparable across countries because
its numbers were reproduced, or that the choices above have been made. Report the sensitivity of the main result to
each of them.
