# United Kingdom — source verification

ISO3: **GBR**   First verified: 2026-08-17 (first release; the counts below are that check). Audit of 2026-10-07: see verification/AUDIT_RESPONSE_2026-10-07.md

## Machine-readable sources

- Values re-queried live and compared: **59**
- Exact match: **59**
- Discrepancies: **0**

## Document sources

- Cited document sources: **5**
- Retrieved into this folder: **5**

| variable | years | status | file | source |
|---|---|---|---|---|
| foreign_born | 2020-2020 | DOWNLOADED | `foreign_nationals__e1040217f2__www.ons.gov.uk.html` | ONS, Population of the UK by country of birth and nationality |
| foreign_born | 2021-2021 | DOWNLOADED | `foreign_nationals__f269f649a7__www.ons.gov.uk.html` | ONS, Population of the UK by country of birth and nationality |
| foreign_nationals | 2020-2020 | DOWNLOADED | `foreign_nationals__e1040217f2__www.ons.gov.uk.html` | ONS, Population of the UK by country of birth and nationality |
| foreign_nationals | 2021-2021 | DOWNLOADED | `foreign_nationals__f269f649a7__www.ons.gov.uk.html` | ONS, Population of the UK by country of birth and nationality |
| irregular_stock | 2017-2017 | DOWNLOADED | `irregular_stock__dc9847ae35__www.pewresearch.org.html` | Pew Research Center (2019), Europe's Unauthorized Immigrant Population Peaks in  |

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
| foreign_born | 2009-2009 (1) | Eurostat [migr_pop3ctb] | `eurostat_migr_pop3ctb_2001-2022_retrieved_2026-10-07.json` |
| foreign_born | 2006-2008 (3) | OECD International Migration Database (stocks of foreign-born population, measure B14) | `OECD_B14_foreign-born_2001-2022_retrieved_2026-10-07.json` |
| foreign_born | 2004-2004 (1) | Office for National Statistics, Population by country of birth and nationality, Annual Population Survey, Janu | `foreign_born__ONS_APS_jan04-dec04_historical-edition.xls` |
| foreign_born | 2005-2005 (1) | Office for National Statistics, Population by country of birth and nationality, Annual Population Survey, Janu | `foreign_born__ONS_APS_jan05-dec05_historical-edition.xls` |
| foreign_nationals | 2001-2009 (8) | Eurostat [migr_pop1ctz] | `eurostat_migr_pop1ctz_2001-2022_retrieved_2026-10-07.json` |
| foreign_nationals | 2002-2002 (1) | OECD International Migration Database (stocks of foreign population, measure B15) | `OECD_B15_foreign-population_2001-2022_retrieved_2026-10-07.json` |
| population | 2001-2009 (9) | World Bank, World Development Indicators (SP.POP.TOTL), sourced from UN World Population Prospects and nationa | `wb_SP_POP_TOTL_2001-2022_retrieved_2026-10-07.json` |
| population_un_wpp2024 | 2001-2009 (9) | UN DESA Population Division, World Population Prospects 2024 (compact demographic indicators) | `UN_WPP2024_demographic_indicators_compact.xlsx` |

Each cell carries its own note, source type and flag in `data/panel_final.csv`; the revision history on the Verification page dates the change.

<!-- extension-2001:end -->
