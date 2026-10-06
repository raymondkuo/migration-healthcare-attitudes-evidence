# New Zealand — source verification

ISO3: **NZL**   Verified: 2026-08-17

## Machine-readable sources

- Values re-queried live and compared: **34**
- Exact match: **34**
- Discrepancies: **0**

## Document sources

- Cited document sources: **2**
- Retrieved into `sources/`: **2**

| variable | years | status | file | source |
|---|---|---|---|---|
| irregular_proxy_overstayers | 2010-2016 | DOWNLOADED | `irregular_proxy_overstayers__c9a01f8746__fyi.org.nz.pdf` | Immigration New Zealand (MBIE), 'OVERSTAYERS' factsheet, October 2018, released  |
| irregular_proxy_overstayers | 2017-2017 | DOWNLOADED | `irregular_proxy_overstayers__4f53adc2ee__immigration.govt.nz.pdf` | Immigration New Zealand, New estimate of people who have overstayed their visa ( |

## Files in this folder

- `data_from_source.csv` — every observation for this country with its live-source check
- `value_check.csv` — workbook value vs live source value, where machine-checkable
- `source_manifest.csv` — every cited source and how it was retrieved
- `sources/` — the downloaded source documents and screenshots

<!-- extension-2001:begin -->

## Extension to 2001 (collected 2026-10-07)

Values for 2001-2009 (and any blank cell inside 2010-2022 that the new sources filled) were collected on 2026-10-07. No value published earlier was changed.

| variable | years | source | file |
|---|---|---|---|
| foreign_born | 2001-2006 (2) | OECD International Migration Database (stocks of foreign-born population, measure B14) | `OECD_B14_foreign-born_2001-2022_retrieved_2026-10-07.json` |
| foreign_born | 2005-2005 (1) | UN DESA International Migrant Stock (World Bank indicator SM.POP.TOTL) | `wb_SM_POP_TOTL_2001-2022_retrieved_2026-10-07.json` |
| population | 2001-2009 (9) | World Bank, World Development Indicators (SP.POP.TOTL), sourced from UN World Population Prospects and nationa | `wb_SP_POP_TOTL_2001-2022_retrieved_2026-10-07.json` |
| population_un_wpp2024 | 2001-2009 (9) | UN DESA Population Division, World Population Prospects 2024 (compact demographic indicators) | `UN_WPP2024_demographic_indicators_compact.xlsx` |

Each cell carries its own note, source type and flag in `data/panel_final.csv`; the revision history on the Verification page dates the change.

<!-- extension-2001:end -->
