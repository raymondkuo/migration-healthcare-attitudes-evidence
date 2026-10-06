# Sweden — source verification

ISO3: **SWE**   Verified: 2026-08-17

## Machine-readable sources

- Values re-queried live and compared: **81**
- Exact match: **68**
- Discrepancies: **13**

### Discrepancies found

| year | variable | workbook | live source | diff |
|---|---|---|---|---|
| 2010 | irregular_detections | 20,765 | 27,460 | -6,695 |
| 2011 | irregular_detections | 23,205 | 20,765 | 2,440 |
| 2012 | irregular_detections | 24,400 | 23,205 | 1,195 |
| 2013 | irregular_detections | 72,835 | 24,400 | 48,435 |
| 2014 | irregular_detections | 1,445 | 72,835 | -71,390 |
| 2015 | irregular_detections | 1,210 | 1,445 | -235 |
| 2016 | irregular_detections | 2,145 | 1,210 | 935 |
| 2017 | irregular_detections | 1,720 | 2,145 | -425 |
| 2018 | irregular_detections | 2,170 | 1,720 | 450 |
| 2019 | irregular_detections | 2,615 | 2,170 | 445 |
| 2020 | irregular_detections | 2,635 | 2,615 | 20 |
| 2021 | irregular_detections | 2,455 | 2,635 | -180 |
| 2022 | irregular_detections | 2,510 | 2,455 | 55 |

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
| foreign_born | 2001-2008 (8) | OECD International Migration Database (stocks of foreign-born population, measure B14) | `OECD_B14_foreign-born_2001-2022_retrieved_2026-10-07.json` |
| foreign_nationals | 2001-2009 (9) | Eurostat [migr_pop1ctz] | `eurostat_migr_pop1ctz_2001-2022_retrieved_2026-10-07.json` |
| population | 2001-2009 (9) | World Bank, World Development Indicators (SP.POP.TOTL), sourced from UN World Population Prospects and nationa | `wb_SP_POP_TOTL_2001-2022_retrieved_2026-10-07.json` |
| population_un_wpp2024 | 2001-2009 (9) | UN DESA Population Division, World Population Prospects 2024 (compact demographic indicators) | `UN_WPP2024_demographic_indicators_compact.xlsx` |

Each cell carries its own note, source type and flag in `data/panel_final.csv`; the revision history on the Verification page dates the change.

<!-- extension-2001:end -->
