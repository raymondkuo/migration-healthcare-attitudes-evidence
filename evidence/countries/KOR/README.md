# Korea South — source verification

ISO3: **KOR**   Verified: 2026-08-17

## Machine-readable sources

- Values re-queried live and compared: **45**
- Exact match: **45**
- Discrepancies: **0**

## Document sources

- Cited document sources: **3**
- Retrieved into `sources/`: **2**

| variable | years | status | file | source |
|---|---|---|---|---|
| irregular | 2021-2022 | RECOVERED_SCREENSHOT | `irregular__MOJ_illegal_stay_table_2021_2025_SCREENSHOT.jpg` | Korea Ministry of Justice, annual illegal-stay foreigner statistics |
| irregular_proxy_overstayers | 2010-2015 | NOT_RETRIEVED | — | Korean National Police University press, Cheryu oegugin beomjoe-e gwanhan gyeong |
| irregular_proxy_overstayers | 2018-2022 | DOWNLOADED | `irregular_proxy_overstayers__f55526aebb__www.ekw.co.kr.html` | Ministry of Justice of Korea, Immigration and Foreign Policy Statistics (불법체류외국인 |

### Notes

- **RECOVERED_SCREENSHOT** — Table is rendered by JavaScript. Captured in browser: 2021 = 125,022+262,251+1,427 = 388,700 and 2022 = 138,013+269,532+3,725 = 411,270, matching the workbook exactly.
- **NOT_RETRIEVED** — Host does not respond. This secondary source is the sole basis for Korea 2010-2015 overstayers; those six values could not be checked against any source.

## Files in this folder

- `data_from_source.csv` — every observation for this country with its live-source check
- `value_check.csv` — workbook value vs live source value, where machine-checkable
- `source_manifest.csv` — every cited source and how it was retrieved
- `sources/` — the downloaded source documents and screenshots
