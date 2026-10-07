# Russia — source verification

ISO3: **RUS**   First verified: 2026-08-17 (first release; the counts below are that check). Audit of 2026-10-07: see verification/AUDIT_RESPONSE_2026-10-07.md

## Machine-readable sources

- Values re-queried live and compared: **32**
- Exact match: **32**
- Discrepancies: **0**

## Document sources

- Cited document sources: **1**
- Retrieved into this folder: **1**

| variable | years | status | file | source |
|---|---|---|---|---|
| irregular_stock | 2020-2020 | DOWNLOADED | `irregular_stock__dcc58afd38__www.themoscowtimes.com.html` | Russian Ministry of Internal Affairs (MVD) data, reported by The Moscow Times, 1 |

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
| foreign_born | 2002-2002 (1) | Rosstat (State Committee of the Russian Federation on Statistics), All-Russia Census 2002, as reported in UN E | `foreign_born__UN_EGM2006_Antonova_Russia_ESA-STAT-AC119-17.pdf` |
| foreign_born | 2005-2005 (1) | UN DESA International Migrant Stock (World Bank indicator SM.POP.TOTL) | `wb_SM_POP_TOTL_2001-2022_retrieved_2026-10-07.json` |
| foreign_nationals | 2002-2002 (1) | Rosstat (State Committee of the Russian Federation on Statistics), All-Russia Census 2002, as reported in UN E | `foreign_born__UN_EGM2006_Antonova_Russia_ESA-STAT-AC119-17.pdf` |
| population | 2001-2009 (9) | World Bank, World Development Indicators (SP.POP.TOTL), sourced from UN World Population Prospects and nationa | `wb_SP_POP_TOTL_2001-2022_retrieved_2026-10-07.json` |
| population_un_wpp2024 | 2001-2009 (9) | UN DESA Population Division, World Population Prospects 2024 (compact demographic indicators) | `UN_WPP2024_demographic_indicators_compact.xlsx` |

Each cell carries its own note, source type and flag in `data/panel_final.csv`; the revision history on the Verification page dates the change.

<!-- extension-2001:end -->
