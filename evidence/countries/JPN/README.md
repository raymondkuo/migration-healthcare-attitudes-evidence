# Japan — source verification

ISO3: **JPN**   First verified: 2026-08-17 (first release; the counts below are that check). Audit of 2026-10-07: see verification/AUDIT_RESPONSE_2026-10-07.md

## Machine-readable sources

- Values re-queried live and compared: **42**
- Exact match: **42**
- Discrepancies: **0**

## Document sources

- Cited document sources: **10**
- Retrieved into this folder: **9**

| variable | years | status | file | source |
|---|---|---|---|---|
| irregular | 2010-2015 | DOWNLOADED | `irregular__ccfa80d7df__www.moj.go.jp.pdf` | Japan Immigration Services Agency, Immigration Control in Recent Years (historic |
| irregular | 2021-2022 | DOWNLOADED | `irregular__cccd1ea084__www.moj.go.jp.pdf` | Japan Immigration Services Agency, Immigration Control and Residency Management  |
| irregular_proxy_overstayers | 2011-2011 | DOWNLOADED | `irregular_proxy_overstayers__d9d919a65a__www.globaldetentionproject.o.html` | Global Detention Project, Japan Immigration Detention Profile (reproducing Minis |
| irregular_proxy_overstayers | 2017-2019 | DOWNLOADED | `irregular_proxy_overstayers__3c80fc7397__www.moj.go.jp.pdf` | Immigration Services Agency of Japan, Honpo ni okeru fuho zanryusha su ni tsuite |
| irregular_proxy_overstayers | 2022-2022 | DOWNLOADED | `irregular_proxy_overstayers__9ff4b8949e__www.moj.go.jp.html` | Immigration Services Agency of Japan, Overstayers as of 1 January (本邦における不法残留者数に |
| irregular_proxy_overstayers | 2020-2021 | DOWNLOADED | `irregular_proxy_overstayers__b84a36a0c9__www.moj.go.jp.html` | Immigration Services Agency of Japan, Overstayers as of 1 January (本邦における不法残留者数に |
| irregular_proxy_overstayers | 2014-2014 | NOT_RETRIEVED_REDUNDANT | — | Ministry of Justice Immigration Bureau, Honpo ni okeru fuho zanryusha su ni tsui |
| irregular_proxy_overstayers | 2017-2017 | DOWNLOADED | `irregular_proxy_overstayers__3c80fc7397__www.moj.go.jp.pdf` | 出入国在留管理庁 本邦における不法残留者数について (Immigration Services Agency of Japan, Number of Overs |
| irregular_proxy_overstayers | 2018-2022 | DOWNLOADED | `irregular_proxy_overstayers__079fcae015__www.moj.go.jp.pdf` | 出入国在留管理庁 本邦における不法残留者数について (Immigration Services Agency of Japan, Number of Overs |
| irregular_proxy_overstayers | 2014-2014 | DOWNLOADED | `irregular_proxy_overstayers__a54f439438__www.moj.go.jp.pdf` | 出入国在留管理庁 本邦における不法残留者数について (Immigration Services Agency of Japan, Number of Overs |

### Notes

- **NOT_RETRIEVED_REDUNDANT** — HTTP 404. Redundant: it duplicates the Immigration Services Agency figure for 2014, and the primary ISA source was retrieved successfully.

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
| foreign_nationals | 2001-2009 (9) | OECD International Migration Database (stocks of foreign population, measure B15) | `OECD_B15_foreign-population_2001-2022_retrieved_2026-10-07.json` |
| population | 2001-2009 (9) | World Bank, World Development Indicators (SP.POP.TOTL), sourced from UN World Population Prospects and nationa | `wb_SP_POP_TOTL_2001-2022_retrieved_2026-10-07.json` |
| population_un_wpp2024 | 2001-2009 (9) | UN DESA Population Division, World Population Prospects 2024 (compact demographic indicators) | `UN_WPP2024_demographic_indicators_compact.xlsx` |

Each cell carries its own note, source type and flag in `data/panel_final.csv`; the revision history on the Verification page dates the change.

<!-- extension-2001:end -->
