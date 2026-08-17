# Italy — source verification

ISO3: **ITA**   Verified: 2026-08-17

## Machine-readable sources

- Values re-queried live and compared: **81**
- Exact match: **81**
- Discrepancies: **0**

## Document sources

- Cited document sources: **7**
- Retrieved into `sources/`: **7**

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

- `data_from_source.csv` — every observation for this country with its live-source check
- `value_check.csv` — workbook value vs live source value, where machine-checkable
- `source_manifest.csv` — every cited source and how it was retrieved
- `sources/` — the downloaded source documents and screenshots
