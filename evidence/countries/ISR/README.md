# Israel — source verification

ISO3: **ISR**   First verified: 2026-08-17 (first release; the counts below are that check). Audit of 2026-10-07: see verification/AUDIT_RESPONSE_2026-10-07.md

## Machine-readable sources

- Values re-queried live and compared: **42**
- Exact match: **42**
- Discrepancies: **0**

## Document sources

- Cited document sources: **1**
- Retrieved into this folder: **1**

| variable | years | status | file | source |
|---|---|---|---|---|
| irregular_stock | 2020-2022 | RECOVERED | `irregular_stock__PIBA_zarim_2022_q1.pdf` | Israel Population and Immigration Authority (רשות האוכלוסין וההגירה), Foreigners |

### Notes

- **RECOVERED** — Retrieved with full browser headers.

## Files in this folder

- `data_from_source.csv` — the observations extracted from the sources for this country: the 2010-2022 records of the first release plus, since 2026-10-07, every current panel value that had no row. `used_in_panel` is recomputed from the current panel and `historical_status` says why a record is no longer used (superseded, rejected, reclassified, deleted)
- `value_check.csv` — workbook value vs live source value, where machine-checkable
- `source_manifest.csv` — every cited source and how it was retrieved
- the downloaded source documents sit directly in this folder (there is no `sources/` subfolder); each has a viewable `MIRROR__` PDF/PNG, and a `SNAPSHOT__` page extract where one was cut out

<!-- health-expenditure:begin -->

## Health expenditure (collected 2026-10-17)

`health_expenditure_pct_gdp`: current health expenditure as a percentage of GDP, 2001-2022 (22 values). A new variable; no other value in this folder or in the panel changed.

| years | source | file |
|---|---|---|
| 2001-2022 | World Bank, World Development Indicators (SH.XPD.CHEX.GD.ZS, current health expenditure % of GDP), sourced fro | `wb_SH_XPD_CHEX_GD_ZS_2001-2022_retrieved_2026-10-17.json` |

Each value carries its source, reference period, grade, verification text and any flag in `data/panel_final.csv`; the revision history on the Verification page dates the addition.

<!-- health-expenditure:end -->

<!-- unemployment:begin -->

## Unemployment rate (collected 2026-10-21)

`unemployment_rate`: unemployed persons as a percentage of the labour force aged 15 and over, 2001-2022 (22 values). A new variable; no other value in this folder or in the panel changed.

| years | source | file |
|---|---|---|
| 2001-2022 | International Labour Organization, ILO modelled estimates (ILOEST), November 2025: unemployment rate, total, a | `ilo_UNE_2EAP_SEX_AGE_RT_2001-2022_retrieved_2026-10-21.csv` |

Each value carries its source, reference period, grade, verification text and any flag in `data/panel_final.csv`; the revision history on the Verification page dates the addition.

<!-- unemployment:end -->

<!-- vdem:begin -->

## V-Dem liberal democracy index (collected 2026-10-26)

`vdem_libdem`: the V-Dem liberal democracy index (v2x_libdem, 0-1), 2001-2022 (22 values), from the V-Dem Country-Year Dataset v16. A new variable; no other value in this folder or in the panel changed.

| years | source | file |
|---|---|---|
| 2001-2022 | V-Dem Institute, V-Dem Country-Year Dataset v16 (Coppedge et al. 2026, https://doi.org/10.23696/vdemds26): lib | `vdem_v16_vdemdata_vdem_retrieved_2026-10-26.RData` |
| 2001-2022 | V-Dem Institute, V-Dem Country-Year Dataset v16 (Coppedge et al. 2026, https://doi.org/10.23696/vdemds26): lib | `vdem_codebook_v16_retrieved_2026-10-26.pdf` |

Each value carries its source, reference period, grade and verification text in `data/panel_final.csv`; V-Dem's 68% interval for it is in `data/vdem_source_comparison.csv`; the revision history on the Verification page dates the addition.

<!-- vdem:end -->

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
