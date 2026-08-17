# Switzerland — source verification

ISO3: **CHE**   Verified: 2026-08-17

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
- Retrieved into `sources/`: **2**

| variable | years | status | file | source |
|---|---|---|---|---|
| irregular_stock | 2015-2015 | SUBSTITUTED | `irregular_stock__SRF_SEM_76000_sanspapiers_CORROBORATION.html` | Morlok, Oswald, Meier, Efionayi-Mader, Ruedin, Bader, Wanner (2015), Sans-Papier |
| irregular_stock | 2017-2017 | DOWNLOADED | `irregular_stock__dccd321871__www.pewresearch.org.html` | Pew Research Center (2019), Europe's Unauthorized Immigrant Population Peaks in  |

### Notes

- **SUBSTITUTED** — LINK ROT: the SEM PDF now returns 404 (site restructured). The 76,000 estimate is corroborated by SRF reporting on the SEM study release of 25 April 2016.

## Files in this folder

- `data_from_source.csv` — every observation for this country with its live-source check
- `value_check.csv` — workbook value vs live source value, where machine-checkable
- `source_manifest.csv` — every cited source and how it was retrieved
- `sources/` — the downloaded source documents and screenshots
