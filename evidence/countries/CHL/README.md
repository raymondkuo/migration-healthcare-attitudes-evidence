# Chile — source verification

ISO3: **CHL**   Verified: 2026-08-17

## Machine-readable sources

- Values re-queried live and compared: **46**
- Exact match: **46**
- Discrepancies: **0**

## Document sources

- Cited document sources: **3**
- Retrieved into `sources/`: **3**

| variable | years | status | file | source |
|---|---|---|---|---|
| irregular_stock | 2018-2022 | DOWNLOADED | `irregular_stock__f8f04e39ba__www.ine.gob.cl.pdf` | Instituto Nacional de Estadisticas (INE) and Servicio Nacional de Migraciones (S |
| irregular_stock | 2018-2020 | DOWNLOADED | `irregular_stock__f8f04e39ba__www.ine.gob.cl.pdf` | Instituto Nacional de Estadisticas (INE) and Servicio Nacional de Migraciones (S |
| irregular_stock | 2022-2022 | DOWNLOADED | `irregular_stock__84522ec4c7__www.ine.gob.cl.html` | Instituto Nacional de Estadisticas (INE) de Chile, press release 29 December 202 |

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
| foreign_born | 2003-2009 (7) | OECD International Migration Database (stocks of foreign-born population, measure B14) | `OECD_B14_foreign-born_2001-2022_retrieved_2026-10-07.json` |
| population | 2001-2009 (9) | World Bank, World Development Indicators (SP.POP.TOTL), sourced from UN World Population Prospects and nationa | `wb_SP_POP_TOTL_2001-2022_retrieved_2026-10-07.json` |
| population_un_wpp2024 | 2001-2009 (9) | UN DESA Population Division, World Population Prospects 2024 (compact demographic indicators) | `UN_WPP2024_demographic_indicators_compact.xlsx` |

Each cell carries its own note, source type and flag in `data/panel_final.csv`; the revision history on the Verification page dates the change.

<!-- extension-2001:end -->
