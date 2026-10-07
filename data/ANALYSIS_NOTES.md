# Research-use notes: constructs, timing, universes and sensitivity

*Written 2026-10-07 after audit finding F24. These are the choices that source verification does not settle.
They are **not decisions**: the places marked [AUTHORS] are for the study's authors to fill in before the final
analysis. No manuscript result was recalculated in preparing this file.*

## 1. The construct [AUTHORS]

The study asks about **attitudes toward publicly funded healthcare for non-nationals**. Which stock best
matches the survey item depends on the item itself, which this archive does not hold.

- Paste the questionnaire wording and response scale here: [AUTHORS]
- Whom does the item name - foreigners / non-citizens in general, legally resident foreigners, migrants, or
  irregular migrants? [AUTHORS]
- Is the entitlement question about people who are *present* (a stock), people who *arrive* (a flow), or a
  policy position? [AUTHORS]

The archive recommends `foreign_nationals_pct_pop` as the main regressor because it counts residents without
the country's nationality, the closest match to "non-nationals". That is a methodological judgement, not a
verified property of the survey question: it fails if the item is about birthplace or about irregular status.

| Variable | What it counts | Countries (years) | Main caution |
|---|---|---|---|
| foreign_nationals | residents holding a foreign nationality (stateless where reported) | 35 (2001-2022) | falls with naturalisation; no annual series for AUS, IND, ISR, NZL, ZAF |
| foreign_born | residents born abroad | 38 (2001-2022) | includes naturalised citizens; 20 UN citizenship-basis cells are excluded from the extract |
| irregular_stock | estimated unauthorised residents | 12 (2010-2022) | methods differ by country; not comparable |
| irregular_proxy_overstayers | register count of overstayers | 6 (2010-2022) | register-based; universe differs (Taiwan: all categories) |
| irregular_proxy_detections | annual enforcement detections | 25 (2010-2022) | a flow; unit differs by source (persons / events) |

## 2. Timing: survey year versus stock date [AUTHORS]

Pick one rule and apply it to every country, then test the other.

1. Same year (survey year Y with the row labelled Y);
2. One-year lag (row Y-1), which matches a 1 January stock to a mid-year survey better;
3. Nearest reference date, using `*_ref_date` per value.

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

| Series | Mean gap | Mean absolute gap | Overlap years |
|---|---|---|---|
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
