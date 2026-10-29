# Taiwan — source verification

ISO3: **TWN**   First verified: 2026-08-17 (first release; the counts below are that check). Audit of 2026-10-07: see verification/AUDIT_RESPONSE_2026-10-07.md

## Machine-readable sources

- Values re-queried live and compared: **16**
- Exact match: **16**
- Discrepancies: **0**

## Document sources

- Cited document sources: **10**
- Retrieved into this folder: **10**

| variable | years | status | file | source |
|---|---|---|---|---|
| irregular | 2012-2018 | DOWNLOADED | `irregular__539a03cf36__www.ly.gov.tw.html` | Taiwan Legislative Yuan report citing National Immigration Agency data (2019) |
| irregular | 2019-2021 | DOWNLOADED | `irregular__40806cb930__www.ly.gov.tw.html` | Taiwan Legislative Yuan report citing National Immigration Agency data (2021) |
| foreign_nationals | 2012-2021 | DOWNLOADED | `foreign_nationals__5669f2f014__ws.moi.gov.tw.pdf` | Taiwan Ministry of the Interior, Department of Statistics (內政統計通報), foreign resi |
| foreign_nationals | 2022-2022 | DOWNLOADED | `foreign_nationals__8280cc6d01__ws.moi.gov.tw.pdf` | Taiwan Ministry of the Interior, Department of Statistics (內政統計通報), foreign resi |
| foreign_workers | 2011-2011 | DOWNLOADED | `foreign_workers__d0a0269c40__statdb.mol.gov.tw.pdf` | Ministry of Labor (勞動部) Labour Statistics Database, monthly statistics Table 12- |
| irregular_proxy_overstayers | 2011-2022 | DOWNLOADED | `irregular_proxy_overstayers__0756fa9f58__statdb.mol.gov.tw.pdf` | Ministry of Labor, Republic of China (Taiwan), Monthly Bulletin of Labour Statis |
| irregular_proxy_overstayers | 2014-2018 | DOWNLOADED | `irregular_proxy_overstayers__5d0d32cf1c__www.ly.gov.tw.html` | National Immigration Agency (內政部移民署), reported by the Legislative Yuan Budget Ce |
| irregular_proxy_overstayers | 2019-2019 | DOWNLOADED | `irregular_proxy_overstayers__5d0d32cf1c__www.ly.gov.tw.html` | National Immigration Agency / Ministry of Labor (失聯移工), reported by the Legislat |
| population | 2010-2016 | DOWNLOADED | `population__19060caafa__ws.moi.gov.tw.pdf` | 內政部統計處 內政統計年報 108年版 (MOI Dept. of Statistics, Statistical Yearbook of Interior,  |
| population | 2017-2022 | DOWNLOADED | `population__0c3445011b__ws.moi.gov.tw.pdf` | 內政部統計處 內政統計月報 115年5月 (MOI Dept. of Statistics, Monthly Bulletin of Interior Stat |

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
| 2001-2022 | Taiwan Ministry of Health and Welfare, Department of Statistics, National Health Expenditure 2024 (中華民國113年國民醫 | `health_expenditure__MOHW_NHE2024_tables__retrieved_2026-10-17.xlsx` |
| 2001-2022 | Taiwan Ministry of Health and Welfare, Department of Statistics, National Health Expenditure 2024 (中華民國113年國民醫 | `health_expenditure__MOHW_NHE2024_report__retrieved_2026-10-17.pdf` |
| 2001-2022 | Taiwan Ministry of Health and Welfare, Department of Statistics, National Health Expenditure 2024 (中華民國113年國民醫 | `health_expenditure__MOHW_DOS_NHE_page__retrieved_2026-10-17.html` |

Each value carries its source, reference period, grade, verification text and any flag in `data/panel_final.csv`; the revision history on the Verification page dates the addition.

<!-- health-expenditure:end -->

<!-- unemployment:begin -->

## Unemployment rate (collected 2026-10-21)

`unemployment_rate`: unemployed persons as a percentage of the labour force aged 15 and over, 2001-2022 (22 values). A new variable; no other value in this folder or in the panel changed.

| years | source | file |
|---|---|---|
| 2001-2022 | Taiwan Directorate-General of Budget, Accounting and Statistics, Yearbook of Manpower Survey Statistics 2025 ( | `unemployment_rate__DGBAS_Manpower_Yearbook2025_table2__retrieved_2026-10-21.xlsx` |
| 2001-2022 | Taiwan Directorate-General of Budget, Accounting and Statistics, Yearbook of Manpower Survey Statistics 2025 ( | `unemployment_rate__DGBAS_Manpower_Yearbook2025__retrieved_2026-10-21.pdf` |
| 2001-2022 | Taiwan Directorate-General of Budget, Accounting and Statistics, Yearbook of Manpower Survey Statistics 2025 ( | `unemployment_rate__DGBAS_Manpower_Yearbook2025_page__retrieved_2026-10-21.html` |

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

`gini_index`: 100 x the Gini coefficient of income or consumption, 10 value(s) for the survey years 2005, 2007, 2010, 2013, 2016-2021. A new variable; no other value in this folder or in the panel changed.

| years | source | file |
|---|---|---|
| 2005-2021 | World Bank, Poverty and Inequality Platform (PIP version 20260922_2021_01_02_PROD): survey estimate for Taiwan | `pip_survey_estimates_20260922_2021_01_02_PROD_retrieved_2026-10-29.csv` |

Each value carries its source, reference period, grade, verification text and any flag in `data/panel_final.csv`; `data/gini_source_comparison.csv` sets the World Bank, PIP and OECD values side by side; the revision history on the Verification page dates the addition.

<!-- gini:end -->

<!-- extension-2001:begin -->

## Extension to 2001 (collected 2026-10-07)

Values for 2001-2009 (and any blank cell inside 2010-2022 that the new sources filled) were collected on 2026-10-07. No value published earlier was changed.

| variable | years | source | file |
|---|---|---|---|
| foreign_nationals | 2001-2011 (11) | Taiwan Ministry of the Interior, Department of Statistics, statistical query system (內政統計查詢網), 外僑居留人數─按國籍別職業別分 | `foreign_nationals__MOI_statis_c0930103_ROC85-111__retrieved_2026-10-07.csv` |
| population | 2001-2009 (9) | National Development Council, Taiwan Statistical Data Book 2019, Table 2-2 Population (End of Year; source cit | `population__NDC_TaiwanStatisticalDataBook2019.pdf` |
| population_un_wpp2024 | 2001-2009 (9) | UN DESA Population Division, World Population Prospects 2024 (compact demographic indicators) | `UN_WPP2024_demographic_indicators_compact.xlsx` |

Each cell carries its own note, source type and flag in `data/panel_final.csv`; the revision history on the Verification page dates the change.

<!-- extension-2001:end -->
