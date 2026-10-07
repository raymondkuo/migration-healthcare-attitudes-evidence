# Australia — source verification

ISO3: **AUS**   First verified: 2026-08-17 (first release; the counts below are that check). Audit of 2026-10-07: see verification/AUDIT_RESPONSE_2026-10-07.md

## Machine-readable sources

- Values re-queried live and compared: **42**
- Exact match: **42**
- Discrepancies: **0**

## Document sources

- Cited document sources: **4**
- Retrieved into this folder: **4**

| variable | years | status | file | source |
|---|---|---|---|---|
| irregular | 2011-2011 | DOWNLOADED | `irregular__4ff1da10a5__www.homeaffairs.gov.au.pdf` | Australian Department of Immigration and Citizenship, Trends in Migration: Austr |
| irregular | 2015-2016 | DOWNLOADED | `irregular__9fcb57f01c__www.homeaffairs.gov.au.pdf` | Australian Department of Immigration and Border Protection, Annual Report 2015–1 |
| irregular_proxy_overstayers | 2010-2011 | DOWNLOADED | `irregular_proxy_overstayers__6b569b4ed3__press-files.anu.edu.au.html` | ANU Press, A Long Way to Go, Chapter 2, Table 2.3 Estimated size of irregular mi |
| irregular_proxy_overstayers | 2016-2016 | DOWNLOADED | `irregular_proxy_overstayers__f49a534fbe__www.aph.gov.au.pdf` | Australian Department of Immigration and Border Protection, Senate Legal and Con |

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
| population | 2001-2009 (9) | World Bank, World Development Indicators (SP.POP.TOTL), sourced from UN World Population Prospects and nationa | `wb_SP_POP_TOTL_2001-2022_retrieved_2026-10-07.json` |
| population_un_wpp2024 | 2001-2009 (9) | UN DESA Population Division, World Population Prospects 2024 (compact demographic indicators) | `UN_WPP2024_demographic_indicators_compact.xlsx` |

Each cell carries its own note, source type and flag in `data/panel_final.csv`; the revision history on the Verification page dates the change.

<!-- extension-2001:end -->
