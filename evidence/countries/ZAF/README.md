# South Africa — source verification

ISO3: **ZAF**   First verified: 2026-08-17 (first release; the counts below are that check). Audit of 2026-10-07: see verification/AUDIT_RESPONSE_2026-10-07.md

## Machine-readable sources

- Values re-queried live and compared: **32**
- Exact match: **32**
- Discrepancies: **0**

## Document sources

- Cited document sources: **3**
- Retrieved into this folder: **3**

| variable | years | status | file | source |
|---|---|---|---|---|
| foreign_born | 2011-2011 | DOWNLOADED | `foreign_born__c204ed0e2a__census.statssa.gov.za.pdf` | Statistics South Africa - Census 2011 (as tabulated in the Census 2022 Statistic |
| foreign_born | 2022-2022 | DOWNLOADED | `foreign_born__c204ed0e2a__census.statssa.gov.za.pdf` | Statistics South Africa - Census 2022 Statistical Release P0301.4 |
| foreign_born | 2016-2016 | DOWNLOADED | `foreign_born__a8ebe1b51a__unstats.un.org.pdf` | Statistics South Africa - Community Survey 2016 (presented to the UN Expert Foru |

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
| foreign_born | 2001-2001 (1) | Statistics South Africa - Census 2011 (as tabulated in the Census 2022 Statistical Release P0301.4) | `foreign_born__c204ed0e2a__census.statssa.gov.za.pdf` |
| foreign_born | 2005-2005 (1) | UN DESA International Migrant Stock (World Bank indicator SM.POP.TOTL) | `wb_SM_POP_TOTL_2001-2022_retrieved_2026-10-07.json` |
| population | 2001-2009 (9) | World Bank, World Development Indicators (SP.POP.TOTL), sourced from UN World Population Prospects and nationa | `wb_SP_POP_TOTL_2001-2022_retrieved_2026-10-07.json` |
| population_un_wpp2024 | 2001-2009 (9) | UN DESA Population Division, World Population Prospects 2024 (compact demographic indicators) | `UN_WPP2024_demographic_indicators_compact.xlsx` |

Each cell carries its own note, source type and flag in `data/panel_final.csv`; the revision history on the Verification page dates the change.

<!-- extension-2001:end -->
