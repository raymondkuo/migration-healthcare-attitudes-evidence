# United States — source verification

ISO3: **USA**   First verified: 2026-08-17 (first release; the counts below are that check). Audit of 2026-10-07: see verification/AUDIT_RESPONSE_2026-10-07.md

## Machine-readable sources

- Values re-queried live and compared: **55**
- Exact match: **55**
- Discrepancies: **0**

## Document sources

- Cited document sources: **14**
- Retrieved into this folder: **14**

| variable | years | status | file | source |
|---|---|---|---|---|
| irregular | 2010-2017 | RECOVERED | `irregular__PewResearch_2020_facts-on-us-immigrants.html` | Pew Research Center, Immigrants in America: Key Charts and Facts (2020) |
| irregular | 2021-2022 | DOWNLOADED | `irregular_stock__4b5c514e18__www.pewresearch.org.html` | Pew Research Center, What we know about unauthorized immigrants living in the U. |
| irregular_stock | 2019-2022 | DOWNLOADED | `irregular_stock__acbbe0d526__journals.sagepub.com.html` | Center for Migration Studies of New York (Robert Warren), After a Decade of Decl |
| irregular_stock | 2020-2020 | DOWNLOADED | `irregular_stock__693e3d8133__cmsny.org.html` | Center for Migration Studies of New York (Robert Warren), US Undocumented Popula |
| irregular_stock | 2019-2022 | DOWNLOADED | `irregular_stock__f07e822120__www.choicesmagazine.org.pdf` | DHS Office of Homeland Security Statistics (Baker & Warren 2024), Estimates of t |
| irregular_stock | 2010-2018 | DOWNLOADED | `irregular_stock__61d67a1914__ohss.dhs.gov.pdf` | DHS Office of Homeland Security Statistics, Estimates of the Unauthorized Immigr |
| irregular_stock | 2010-2010 | DOWNLOADED | `irregular_stock__61d67a1914__ohss.dhs.gov.pdf` | DHS Office of Homeland Security Statistics, Estimates of the Unauthorized Immigr |
| irregular_stock | 2015-2015 | DOWNLOADED | `irregular_stock__61d67a1914__ohss.dhs.gov.pdf` | DHS Office of Homeland Security Statistics, Estimates of the Unauthorized Immigr |
| irregular_stock | 2019-2022 | DOWNLOADED | `irregular_stock__a21b7d97cf__www.migrationpolicy.org.html` | Migration Policy Institute (with Jennifer Van Hook, Penn State), Diverse Flows D |
| irregular_stock | 2011-2018 | DOWNLOADED | `irregular_stock__66eb6dec29__www.migrationpolicy.org.pdf` | Migration Policy Institute, Unauthorized Immigrants in the United States: Stable |
| irregular_stock | 2010-2010 | DOWNLOADED | `irregular_stock__1db68f77f4__www.pewresearch.org.html` | Pew Hispanic Center, Unauthorized Immigrant Population: National and State Trend |
| irregular_stock | 2021-2022 | DOWNLOADED | `irregular_stock__5f9277ca27__www.pewresearch.org.html` | Pew Research Center, Q&A: How Pew Research Center estimates the number of unauth |
| irregular_stock | 2017-2017 | DOWNLOADED | `irregular_stock__6832664b64__www.pewresearch.org.html` | Pew Research Center, Unauthorized immigrant population trends |
| irregular_stock | 2021-2022 | DOWNLOADED | `irregular_stock__4b5c514e18__www.pewresearch.org.html` | Pew Research Center, What we know about unauthorized immigrants living in the U. |

### Notes

- **RECOVERED** — Retrieved with full browser headers.

## Files in this folder

- `data_from_source.csv` — the observations extracted from the sources for this country: the 2010-2022 records of the first release plus, since 2026-10-07, every current panel value that had no row. `used_in_panel` is recomputed from the current panel and `historical_status` says why a record is no longer used (superseded, rejected, reclassified, deleted)
- `value_check.csv` — workbook value vs live source value, where machine-checkable
- `source_manifest.csv` — every cited source and how it was retrieved
- the downloaded source documents sit directly in this folder (there is no `sources/` subfolder); each has a viewable `MIRROR__` PDF/PNG, and a `SNAPSHOT__` page extract where one was cut out

<!-- extension-2001:begin -->

## Extension to 2001 (collected 2026-10-07)

Values for 2001-2009 (and any blank cell inside 2010-2022 that the new sources filled) were collected on 2026-10-07. No value published earlier was changed.

| variable | years | source | file |
|---|---|---|---|
| foreign_born | 2001-2009 (9) | OECD International Migration Database (stocks of foreign-born population, measure B14) | `OECD_B14_foreign-born_2001-2022_retrieved_2026-10-07.json` |
| foreign_nationals | 2001-2009 (9) | OECD International Migration Database (stocks of foreign population, measure B15) | `OECD_B15_foreign-population_2001-2022_retrieved_2026-10-07.json` |
| population | 2001-2009 (9) | World Bank, World Development Indicators (SP.POP.TOTL), sourced from UN World Population Prospects and nationa | `wb_SP_POP_TOTL_2001-2022_retrieved_2026-10-07.json` |
| population_un_wpp2024 | 2001-2009 (9) | UN DESA Population Division, World Population Prospects 2024 (compact demographic indicators) | `UN_WPP2024_demographic_indicators_compact.xlsx` |

Each cell carries its own note, source type and flag in `data/panel_final.csv`; the revision history on the Verification page dates the change.

<!-- extension-2001:end -->
