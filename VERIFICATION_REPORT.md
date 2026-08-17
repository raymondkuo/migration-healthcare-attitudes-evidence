# Source verification report

**Scope** — the two supplied workbooks, `immigration_country_year_2010_2022.xlsx` (FILE 1) and
`migration_population_panel_40countries_2010-2022.xlsx` (FILE 2).
**Verified** 2026-08-17. Every source was re-retrieved on that date; nothing below relies on the
workbooks' own claims about their sources.

---

## 1. What was done

| Step | Result |
|---|---|
| Sources catalogued from both workbooks | 171 source references, **160 distinct URLs**, 51 hosts |
| Machine-readable sources re-queried and compared value by value | **2,454 values** |
| — matched the live source exactly | **2,415 (98.4%)** |
| — discrepancies | **39** |
| Document / web-page source citations | **78 distinct country-source citations** across 72 URLs |
| — archived in the country folders | **76 of 78** |
| — not retrievable by any means | **2** |
| Country folders created, each with evidence and a README | **40** |
| Source files downloaded | 82 files, 91 MB |
| Corrections applied in the final panel | **49 values across 5 countries** |

Sources re-queried live: World Bank WDI (`SP.POP.TOTL`, `SM.POP.TOTL`), Eurostat `migr_pop3ctb`,
`migr_pop1ctz` and `migr_eipre`, the OECD International Migration Database (13 SDMX series),
UN WPP 2024, and UN DESA International Migrant Stock 2024.

---

## 2. The main finding: a one-year offset in FILE 2

For **Switzerland, Portugal and Sweden**, FILE 2's `irregular_proxy_detections` series is shifted
by one year. The value published by Eurostat for year *Y+1* is recorded under year *Y*, the genuine
2010 figures are absent, and the 2022 cell actually holds the 2023 figure.

| Year | Eurostat (live) SE | FILE 2 SE | Eurostat CH | FILE 2 CH | Eurostat PT | FILE 2 PT |
|---|---|---|---|---|---|---|
| 2010 | 27,460 | 20,765 | 12,020 | 12,630 | 10,085 | 9,230 |
| 2013 | 24,400 | 72,835 | 15,045 | 13,800 | 5,155 | 4,530 |
| 2014 | 72,835 | 1,445 | 13,800 | 15,555 | 4,530 | 5,145 |
| 2022 | 15,130 | 19,280 | 15,130 | 19,280 | 2,170 | 1,615 |

This is not a definitional difference. FILE 1 carries the same Eurostat series for the same three
countries **correctly**, which confirms FILE 2 is the file in error. All 39 values were replaced.

A consequence: FILE 2's codebook warns that "Sweden has a break in the detections series
(2013: 72,835 → 2014: 1,445)". That break is an artefact of the offset. In the real Eurostat data
the break falls between **2014 (72,835) and 2015 (1,445)**.

---

## 3. Other substantive findings

**Taiwan's overstayer series mixed two incompatible measures.** FILE 2 used Ministry of Labor
*absconded migrant workers* (失聯移工 — a subset) for 2011–2013 and 2019–2022, but National
Immigration Agency *overstayers* (逾期停留/居留) for 2014–2018, in one column. Read as a time
series that produces a false +65% jump in 2014 and a false −47% fall in 2019. The workbook's own
notes document the difference honestly, but the values still sit in a single column. Fixed by
splitting them; the NIA measure — which FILE 1 carries consistently for 2012–2021 — is now the
overstayer series.

**FILE 1 pools five different measures in one column.** `Illegal_immigrants_number` combines 274
Eurostat annual enforcement *detections* (a flow, and not even a count of persons — one person can
be detected repeatedly) with overstayer register counts and modelled unauthorised-population
*stocks* for eight countries. These cannot be pooled. This is the main reason the final panel is
built on FILE 2 rather than FILE 1.

**Italy's irregular series was incomplete and method-mixed.** 2010–2013 were missing although ISMU
publishes them, and 2014 used a Pew estimate while every other year used ISMU. ISMU's own
machine-readable series was located and downloaded; it confirmed **every** existing Italian value
exactly (2015: 404,000 … 2021: 519,000) and supplied the four missing years.

**The two workbooks disagree on population.** FILE 1 uses UN WPP 2024, FILE 2 uses World Bank WDI.
427 of 520 country-years differ; 26 by more than 3% (Israel −4.1%, Bulgaria +3.2%, France −2.5%).
Both are internally correct — they are simply different sources. The final panel carries both,
side by side, with the gap computed.

**The two workbooks disagree on foreign-born stock even more.** On the 110 overlapping
country-years, UN DESA migrant stock and the OECD/Eurostat foreign-born series diverge by +144% for
Turkey, +55% Czechia, +42% Slovakia, −18% Portugal. Turkey is the clearest case: UN DESA includes
Syrians under temporary protection, the OECD series does not.

**Link rot and access blocking.** The Swiss SEM `sans-papiers` PDF now 404s; `ismu.org` returns 403
to every client including a real browser; `press.police.ac.kr` does not respond at all. In eight of
ten cases an equivalent or better source was retrieved instead. The two genuine losses are the
Korean police-university PDF (the sole basis for Korea 2010–2015) and a redundant Japanese mirror.

---

## 4. What checked out

These deserve stating as plainly as the problems:

- **All 520** FILE 1 population values reproduce the UN WPP 2024 file exactly.
- **All 507** FILE 2 population values reproduce the World Bank API exactly.
- **All 584** Eurostat foreign-born and foreign-national values reproduce exactly.
- **All 139** OECD International Migration Database values reproduce exactly.
- **All 274** FILE 1 Eurostat detections reproduce exactly, including the three countries FILE 2
  got wrong.
- FILE 2's `Panel` sheet is **perfectly consistent** with its own `Long_all_observations` audit
  trail — 1,690 values, zero mismatches — and every `*_pct_pop` column recomputes to floating-point
  precision.
- Korea 2021 and 2022 verified against the live Ministry of Justice table: 125,022 + 262,251 +
  1,427 = **388,700** and 138,013 + 269,532 + 3,725 = **411,270**, confirming both the values and
  the stated summing method.
- Philippines 2020 verified against the PSA census release: **78,396**.

FILE 2 is a careful piece of work. Its documentation is unusually honest about its own weaknesses,
and outside the three shifted countries and the Taiwan column, it held up.

---

## 5. Judgement on data quality

Grades assigned to each of the 1,692 values in the final panel:

| Grade | Meaning | Count |
|---|---|---|
| **A** | Re-derived from a machine-readable official source and matched exactly, or corrected against one during this verification | 1,564 |
| **B** | Confirmed by reading the retrieved source document | 11 |
| **C** | Source document retrieved, but the value is a modelled estimate that cannot be mechanically re-derived | 111 |
| **D** | Cited source could not be retrieved | 6 |

The six D cells are Korea's 2010–2015 overstayer figures.

**By variable:**

| Variable | Coverage | Verdict |
|---|---|---|
| `population` | 520/520 country-years, 40/40 countries | **Strong.** Use freely. |
| `foreign_born` | 395/520, 38/40 | **Strong**, but includes naturalised citizens. |
| `foreign_nationals` | 383/520, 34/40 | **Strong**, and conceptually the right variable here. |
| `irregular_stock` | 59/520, 13/40 | **Weak.** Not comparable across countries. |
| `irregular_proxy_overstayers` | 38/520, 5/40 | **Weak.** Register counts, understate the true figure. |
| `irregular_proxy_detections` | 297/520, 25/40 | **Weakest.** A flow of enforcement events, driven by enforcement intensity and position on migration routes. |

**Recommendation for the healthcare-attitudes study.** Use `foreign_nationals_pct_pop` as the main
cross-national regressor: it is the population the survey question is actually about, it covers 34
of 40 countries, and every value is graded A or B. Use `foreign_born_pct_pop` as a robustness
check, noting it includes naturalised citizens who *are* nationals. Do **not** use any irregular-
migration variable as a continuous cross-national regressor — with 10.6% coverage for stocks and no
comparable method, it will not support one. If irregular migration matters to the argument, treat
it as an ordinal salience indicator or exploit within-country variation only.

Two practical cautions: Eurostat and OECD stocks are measured at **1 January**, so the row labelled
year *Y* describes 31 December of *Y−1* — lag accordingly if the survey is fielded mid-year. And
pick one population denominator and keep it for every country.

---

## 6. Deliverables

This report was written before the GitHub Pages wrapper was added. In this frozen
repository, the same deliverables are exposed at the paths below. The web index
at `index.html` provides stable links for editors and reviewers.

```
data/FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx
    README, Panel_final, Data_quality, Corrections_applied, Known_issues,
    Verification_log, Source_register, Irregular_estimates_all, Codebook

evidence/countries/<ISO3>/        one folder per country, 40 in total
    README.md                     what was verified, and any discrepancy found
    data_from_source.csv          every observation with its live-source check
    value_check.csv               workbook value vs live source value
    source_manifest.csv           every cited source and how it was retrieved
    *.pdf, *.html, *.png, *.jpg    downloaded documents, web snapshots and screenshots

verification/                     full machine-readable output
    sources_catalog.csv, value_checks.csv, value_checks_oecd.csv,
    country_source_manifest.csv, download_log.csv, audit_issues.csv,
    corrections_applied.csv, country_package_summary.csv

evidence/api/                     bulk source downloads and API snapshots
data/                              panel CSVs, definitions, audit tables and input workbooks
scripts/build-site.mjs             generator for index.html and 40 country pages
```
