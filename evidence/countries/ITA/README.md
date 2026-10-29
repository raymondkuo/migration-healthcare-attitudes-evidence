# Italy — source verification

ISO3: **ITA**   First verified: 2026-08-17 (first release; the counts below are that check). Audit of 2026-10-07: see verification/AUDIT_RESPONSE_2026-10-07.md

## Machine-readable sources

- Values re-queried live and compared: **81**
- Exact match: **81**
- Discrepancies: **0**

## Document sources

- Cited document sources: **7**
- Retrieved into this folder: **7**

| variable | years | status | file | source |
|---|---|---|---|---|
| irregular_stock | 2017-2017 | DOWNLOADED | `irregular_stock__eeb1002910__www.neodemos.info.html` | Fondazione ISMU estimate, reported in Neodemos |
| irregular_stock | 2015-2016 | DOWNLOADED | `irregular_stock__a0f7dc3c81__www.antoniocasella.eu.pdf` | Fondazione ISMU, XXII Rapporto sulle migrazioni 2016 |
| irregular_stock | 2018-2018 | DOWNLOADED | `irregular_stock__77693a7efa__www.vita.it.html` | Fondazione ISMU, XXIV Rapporto sulle migrazioni 2018 |
| irregular_stock | 2019-2019 | SUBSTITUTED | `irregular_stock__ISMU_Stime_irregolari_1991_2021_agg_maggio2022.xls` | Fondazione ISMU, XXV Rapporto sulle migrazioni 2019 |
| irregular_stock | 2020-2020 | SUBSTITUTED | `irregular_stock__ISMU_Stime_irregolari_1991_2021_agg_maggio2022.xls` | Fondazione ISMU, XXVI Rapporto sulle migrazioni 2020 |
| irregular_stock | 2021-2022 | SUBSTITUTED | `irregular_stock__ISMU_Stime_irregolari_1991_2021_agg_maggio2022.xls` | Fondazione ISMU, XXVII Rapporto sulle migrazioni 2021 |
| irregular_stock | 2014-2017 | DOWNLOADED | `irregular_stock__dccd321871__www.pewresearch.org.html` | Pew Research Center (2019), Europe's Unauthorized Immigrant Population Peaks in  |

### Notes

- **SUBSTITUTED** — ismu.org blocks all clients (HTTP 403). Replaced by ISMU's own published series "Stime stranieri irregolari ISMU 1991-2021", which confirms 2019 = 562,000.
- **SUBSTITUTED** — Host unreachable. ISMU series confirms 2020 = 517,000.
- **SUBSTITUTED** — ismu.org blocks all clients (HTTP 403). ISMU series confirms 2021 = 519,000; the 2022 value of 506,000 is corroborated by the XXVIII Rapporto coverage.

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

<!-- gini:begin -->

## Gini index (collected 2026-10-29)

`gini_index`: 100 x the Gini coefficient of income or consumption, 21 value(s) for the survey years 2002-2022. A new variable; no other value in this folder or in the panel changed.

- Flag "break in time series: new PIP survey-comparability spell": 2003.

| years | source | file |
|---|---|---|
| 2002-2022 | World Bank, World Development Indicators: Gini index (SI.POV.GINI), from the Poverty and Inequality Platform ( | `wb_SI_POV_GINI_2001-2022_retrieved_2026-10-29.json` |

Each value carries its source, reference period, grade, verification text and any flag in `data/panel_final.csv`; `data/gini_source_comparison.csv` sets the World Bank, PIP and OECD values side by side; the revision history on the Verification page dates the addition.

<!-- gini:end -->

<!-- extension-2001:begin -->

## Extension to 2001 (collected 2026-10-07)

Values for 2001-2009 (and any blank cell inside 2010-2022 that the new sources filled) were collected on 2026-10-07. No value published earlier was changed.

| variable | years | source | file |
|---|---|---|---|
| foreign_born | 2002-2009 (8) | Eurostat [migr_pop3ctb] | `eurostat_migr_pop3ctb_2001-2022_retrieved_2026-10-07.json` |
| foreign_nationals | 2002-2009 (8) | Eurostat [migr_pop1ctz] | `eurostat_migr_pop1ctz_2001-2022_retrieved_2026-10-07.json` |
| foreign_nationals | 2001-2001 (1) | OECD International Migration Database (stocks of foreign population, measure B15) | `OECD_B15_foreign-population_2001-2022_retrieved_2026-10-07.json` |
| population | 2001-2009 (9) | World Bank, World Development Indicators (SP.POP.TOTL), sourced from UN World Population Prospects and nationa | `wb_SP_POP_TOTL_2001-2022_retrieved_2026-10-07.json` |
| population_un_wpp2024 | 2001-2009 (9) | UN DESA Population Division, World Population Prospects 2024 (compact demographic indicators) | `UN_WPP2024_demographic_indicators_compact.xlsx` |

Each cell carries its own note, source type and flag in `data/panel_final.csv`; the revision history on the Verification page dates the change.

<!-- extension-2001:end -->
