# Portugal — source verification

ISO3: **PRT**   Verified: 2026-08-17

## Machine-readable sources

- Values re-queried live and compared: **81**
- Exact match: **68**
- Discrepancies: **13**

### Discrepancies found

| year | variable | workbook | live source | diff |
|---|---|---|---|---|
| 2010 | irregular_detections | 9,230 | 10,085 | -855 |
| 2011 | irregular_detections | 9,110 | 9,230 | -120 |
| 2012 | irregular_detections | 5,155 | 9,110 | -3,955 |
| 2013 | irregular_detections | 4,530 | 5,155 | -625 |
| 2014 | irregular_detections | 5,145 | 4,530 | 615 |
| 2015 | irregular_detections | 6,500 | 5,145 | 1,355 |
| 2016 | irregular_detections | 6,005 | 6,500 | -495 |
| 2017 | irregular_detections | 4,760 | 6,005 | -1,245 |
| 2018 | irregular_detections | 5,890 | 4,760 | 1,130 |
| 2019 | irregular_detections | 3,145 | 5,890 | -2,745 |
| 2020 | irregular_detections | 1,855 | 3,145 | -1,290 |
| 2021 | irregular_detections | 2,170 | 1,855 | 315 |
| 2022 | irregular_detections | 1,615 | 2,170 | -555 |

## Document sources

- Cited document sources: **0**
- Retrieved into `sources/`: **0**

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
| foreign_born | 2009-2009 (1) | Eurostat [migr_pop3ctb] | `eurostat_migr_pop3ctb_2001-2022_retrieved_2026-10-07.json` |
| foreign_born | 2002-2002 (1) | OECD International Migration Database (stocks of foreign-born population, measure B14) | `OECD_B14_foreign-born_2001-2022_retrieved_2026-10-07.json` |
| foreign_nationals | 2001-2009 (7) | Eurostat [migr_pop1ctz] | `eurostat_migr_pop1ctz_2001-2022_retrieved_2026-10-07.json` |
| foreign_nationals | 2004-2005 (2) | OECD International Migration Database (stocks of foreign population, measure B15) | `OECD_B15_foreign-population_2001-2022_retrieved_2026-10-07.json` |
| population | 2001-2009 (9) | World Bank, World Development Indicators (SP.POP.TOTL), sourced from UN World Population Prospects and nationa | `wb_SP_POP_TOTL_2001-2022_retrieved_2026-10-07.json` |
| population_un_wpp2024 | 2001-2009 (9) | UN DESA Population Division, World Population Prospects 2024 (compact demographic indicators) | `UN_WPP2024_demographic_indicators_compact.xlsx` |

Each cell carries its own note, source type and flag in `data/panel_final.csv`; the revision history on the Verification page dates the change.

<!-- extension-2001:end -->
