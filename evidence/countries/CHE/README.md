# Switzerland — source verification

ISO3: **CHE**   First verified: 2026-08-17 (first release; the counts below are that check). Audit of 2026-10-07: see verification/AUDIT_RESPONSE_2026-10-07.md

## Machine-readable sources

- Values re-queried live and compared: **80**
- Exact match: **67**
- Discrepancies: **13**

### Discrepancies found

| year | variable | workbook | live source | diff |
|---|---|---|---|---|
| 2010 | irregular_detections | 12,630 | 12,020 | 610 |
| 2011 | irregular_detections | 14,170 | 12,630 | 1,540 |
| 2012 | irregular_detections | 15,045 | 14,170 | 875 |
| 2013 | irregular_detections | 13,800 | 15,045 | -1,245 |
| 2014 | irregular_detections | 15,555 | 13,800 | 1,755 |
| 2015 | irregular_detections | 15,765 | 15,555 | 210 |
| 2016 | irregular_detections | 13,940 | 15,765 | -1,825 |
| 2017 | irregular_detections | 14,420 | 13,940 | 480 |
| 2018 | irregular_detections | 13,885 | 14,420 | -535 |
| 2019 | irregular_detections | 11,020 | 13,885 | -2,865 |
| 2020 | irregular_detections | 12,175 | 11,020 | 1,155 |
| 2021 | irregular_detections | 15,130 | 12,175 | 2,955 |
| 2022 | irregular_detections | 19,280 | 15,130 | 4,150 |

## Document sources

- Cited document sources: **2**
- Retrieved into this folder: **2**

| variable | years | status | file | source |
|---|---|---|---|---|
| irregular_stock | 2015-2015 | SUBSTITUTED | `irregular_stock__SRF_SEM_76000_sanspapiers_CORROBORATION.html` | Morlok, Oswald, Meier, Efionayi-Mader, Ruedin, Bader, Wanner (2015), Sans-Papier |
| irregular_stock | 2017-2017 | DOWNLOADED | `irregular_stock__dccd321871__www.pewresearch.org.html` | Pew Research Center (2019), Europe's Unauthorized Immigrant Population Peaks in  |

### Notes

- **SUBSTITUTED** — LINK ROT: the SEM PDF now returns 404 (site restructured). The 76,000 estimate is corroborated by SRF reporting on the SEM study release of 25 April 2016.

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
| foreign_born | 2001-2001 (1) | OECD International Migration Database (stocks of foreign-born population, measure B14) | `OECD_B14_foreign-born_2001-2022_retrieved_2026-10-07.json` |
| foreign_nationals | 2001-2009 (9) | Eurostat [migr_pop1ctz] | `eurostat_migr_pop1ctz_2001-2022_retrieved_2026-10-07.json` |
| population | 2001-2009 (9) | World Bank, World Development Indicators (SP.POP.TOTL), sourced from UN World Population Prospects and nationa | `wb_SP_POP_TOTL_2001-2022_retrieved_2026-10-07.json` |
| population_un_wpp2024 | 2001-2009 (9) | UN DESA Population Division, World Population Prospects 2024 (compact demographic indicators) | `UN_WPP2024_demographic_indicators_compact.xlsx` |

Each cell carries its own note, source type and flag in `data/panel_final.csv`; the revision history on the Verification page dates the change.

<!-- extension-2001:end -->
