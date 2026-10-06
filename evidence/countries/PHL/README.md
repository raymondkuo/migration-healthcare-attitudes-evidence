# Philippines — source verification

ISO3: **PHL**   Verified: 2026-08-17

## Machine-readable sources

- Values re-queried live and compared: **32**
- Exact match: **32**
- Discrepancies: **0**

## Document sources

- Cited document sources: **2**
- Retrieved into `sources/`: **2**

| variable | years | status | file | source |
|---|---|---|---|---|
| foreign_nationals | 2010-2010 | DOWNLOADED | `foreign_nationals__8847422287__www.sunstar.com.ph.html` | National Statistics Office (Philippines) - 2010 Census of Population and Housing |
| foreign_nationals | 2020-2020 | RECOVERED_SCREENSHOT | `foreign_nationals__PSA_2020CPH_foreign_citizens_SCREENSHOT.jpg` | Philippine Statistics Authority - Foreign Citizens in the Country (2020 Census o |

### Notes

- **RECOVERED_SCREENSHOT** — Bot-check blocks scripted clients; captured in browser. Page states 78,396 foreign citizens in 2020, matching the workbook exactly.

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
| foreign_born | 2005-2005 (1) | UN DESA International Migrant Stock (World Bank indicator SM.POP.TOTL) | `wb_SM_POP_TOTL_2001-2022_retrieved_2026-10-07.json` |
| population | 2001-2009 (9) | World Bank, World Development Indicators (SP.POP.TOTL), sourced from UN World Population Prospects and nationa | `wb_SP_POP_TOTL_2001-2022_retrieved_2026-10-07.json` |
| population_un_wpp2024 | 2001-2009 (9) | UN DESA Population Division, World Population Prospects 2024 (compact demographic indicators) | `UN_WPP2024_demographic_indicators_compact.xlsx` |

Each cell carries its own note, source type and flag in `data/panel_final.csv`; the revision history on the Verification page dates the change.

<!-- extension-2001:end -->
