# China — source verification

ISO3: **CHN**   First verified: 2026-08-17 (first release; the counts below are that check). Audit of 2026-10-07: see verification/AUDIT_RESPONSE_2026-10-07.md

## Machine-readable sources

- Values re-queried live and compared: **32**
- Exact match: **32**
- Discrepancies: **0**

## Document sources

- Cited document sources: **2**
- Retrieved into this folder: **2**

| variable | years | status | file | source |
|---|---|---|---|---|
| foreign_nationals | 2010-2010 | DOWNLOADED | `foreign_nationals__06858e32fc__www.stats.gov.cn.html` | National Bureau of Statistics of China - 2010 Population Census (Sixth National  |
| foreign_nationals | 2020-2020 | DOWNLOADED | `foreign_nationals__0bdd1c303b__www.stats.gov.cn.html` | National Bureau of Statistics of China - Communique of the Seventh National Popu |

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

22 of the values (2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022) are ILO imputations, which the ILO describes as not based on national data; they carry the flag "ILO imputed: not based on national data".

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

`gini_index`: 100 x the Gini coefficient of income or consumption, 16 value(s) for the survey years 2002, 2005, 2008, 2010-2022. A new variable; no other value in this folder or in the panel changed.

- Flag "consumption-based (not income)": 2002, 2005, 2008, 2010-2012, 2014-2022.
- Flag "consumption-based (not income); break in time series: new PIP survey-comparability spell": 2013.

| years | source | file |
|---|---|---|
| 2002-2022 | World Bank, World Development Indicators: Gini index (SI.POV.GINI), from the Poverty and Inequality Platform ( | `wb_SI_POV_GINI_2001-2022_retrieved_2026-10-29.json` |

Each value carries its source, reference period, grade, verification text and any flag in `data/panel_final.csv`; `data/gini_source_comparison.csv` sets the World Bank, PIP and OECD values side by side; the revision history on the Verification page dates the addition.

<!-- gini:end -->

<!-- covid:begin -->

## COVID-19 (collected 2026-11-06)

Four new variables for the years 2020, 2021, 2022: `covid_cases` and `covid_deaths` (reported in the calendar year) and `covid_cases_pct_pop` and `covid_deaths_pct_pop` (the same over the panel's population, x 100, computed by the archive). No other value in this folder or in the panel changed.

| year | cases | deaths | source | file |
|---|---:|---:|---|---|
| 2020 | 87,071 | 4,634 | National Health Commission of China, daily briefing on COVID-19 for 24:00 on 31 December 2 | `covid__NHC_briefing_2020-12-31__chinadaily__retrieved_2026-11-06.html` |
| 2021 | 15,243 | 2 | National Health Commission of China, daily briefing on COVID-19 for 24:00 on 31 December 2 | `covid__NHC_briefing_2021-12-31__chinadaily__retrieved_2026-11-06.html` |
| 2022 | 294,881 | 605 | National Health Commission of China, last daily briefing on COVID-19 (24 December 2022, da | `covid__NHC_briefing_2022-12-23__en.nhc.gov.cn__retrieved_2026-11-06.html` |

Flag "incomplete year: national daily reporting ended 23 Dec 2022; confirmed cases only": 2022.

WHO's "China" includes Hong Kong, Macao and Taiwan, so the mainland figures come from the National Health Commission.

`data/covid_source_comparison.csv` sets the values beside WHO's and the Johns Hopkins archive's; the revision history on the Verification page dates the addition.

<!-- covid:end -->

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
