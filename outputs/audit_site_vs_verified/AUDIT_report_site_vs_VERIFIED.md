# Website vs. VERIFIED workbook audit report

Audit date: 2026-08-17 (Asia/Taipei; report generated 19:04 +08:00)

This report records the reproducible audit of the published website in this repository against the authoritative workbook `FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx`. It is intended to be read together with the complete Excel checklist, especially its `WORKBOOK_AUDIT` and `LINK_AUDIT` sheets.

## Deliverables and fixed inputs

Repository root:

`D:\研究計畫\其他投稿\2026_移民對非本國籍使用公共醫療態度（葉明叡）\claude-work\migration-data-archive`

| Artifact | Location | Purpose |
|---|---|---|
| Audit report | `outputs/audit_site_vs_verified/AUDIT_report_site_vs_VERIFIED.md` | This narrative and reproducibility record |
| Excel checklist | [`AUDIT_checklist_site_vs_VERIFIED.xlsx`](AUDIT_checklist_site_vs_VERIFIED.xlsx) | Detailed per-country/per-worksheet checklist, workbook audit, and 189-row URL appendix |
| Audit implementation | [`scripts/audit_site_against_verified.py`](../../scripts/audit_site_against_verified.py) | Static HTML, workbook, URL, archive, and manifest audit |
| Regression tests | [`scripts/test_audit_site_against_verified.py`](../../scripts/test_audit_site_against_verified.py) | Parser, comparison, archive, and checklist-structure tests |
| Reference workbook | [`FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx`](../../../FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx) | External truth source requested for comparison |
| Site data tables | [`data/`](../../data) | CSV representations used by the website |
| Archive manifest | [`manifest/checksums.csv`](../../manifest/checksums.csv) | Expected bytes and SHA-256 digests for packaged files |

The audit covered 40 countries, 40 country pages, 156 evidence pages, six top-level HTML pages, and all nine worksheets in the reference workbook:

`README`, `Panel_final`, `Data_quality`, `Corrections_applied`, `Known_issues`, `Verification_log`, `Source_register`, `Irregular_estimates_all`, and `Codebook`.

Country ISO3 list: `AUS`, `AUT`, `BEL`, `BGR`, `CHE`, `CHL`, `CHN`, `CZE`, `DEU`, `DNK`, `ESP`, `FIN`, `FRA`, `GBR`, `HRV`, `HUN`, `IND`, `ISL`, `ISR`, `ITA`, `JPN`, `KOR`, `LTU`, `MEX`, `NLD`, `NOR`, `NZL`, `PHL`, `POL`, `PRT`, `RUS`, `SUR`, `SVK`, `SVN`, `SWE`, `THA`, `TUR`, `TWN`, `USA`, `ZAF`.

## Executive result

The website’s displayed statistical values match the requested reference workbook exactly. The audit found no numeric mismatch in any country-page or evidence-page value cell.

The separate requirement that every current external URL remain downloadable is not fully satisfied at audit time. The local archive is complete and checksum-valid, but 38 of 189 unique external URLs were blocked, rate-limited, missing, malformed, or unreachable during the live test. Those URLs are listed below and in the `LINK_AUDIT` sheet.

The site also contains an enriched Taiwan-specific copy of `Panel_final` and refreshed source-register metadata. These differences are explicitly flagged; they do not change the compared core values.

### Value comparison totals

| Compared website content | Cells | Exact matches | Mismatches |
|---|---:|---:|---:|
| Country-page panel values | 3,133 | 3,133 | 0 |
| Evidence-page values | 1,699 | 1,699 | 0 |
| Combined displayed values | 4,832 | 4,832 | 0 |

The full row-level checklist contains 12,147 audit rows: 10,349 `MATCH`, 2 `FAIL`, and 1,796 `N/A`. The two `FAIL` rows are website-wide presentation/headline differences, not displayed statistic value differences. `N/A` rows cover items that are not directly displayed on the website, competing irregular-migration estimates, or site-only fields without a corresponding reference column.

## Exact file identities

SHA-256 values are lowercase hexadecimal.

| File | Bytes | SHA-256 |
|---|---:|---|
| External reference workbook | 334,455 | `3376385ee1ca23658dfe3741c83930fdaa03e1e2ac7e762890646223fcd0f0bc` |
| Website-bundled workbook (`data/FINAL_...xlsx`) | 334,276 | `875e5a45173bab0ac04f09559e17dc15e149f7d0430fee51060e07d5bca568a4` |
| Final Excel checklist | 1,236,494 | `52bb7d454e6ebbf005b06d68cebc2977ec1b2ff1f7c0cc1bd3ed4cdefedf765c` |
| Audit implementation | 123,938 | `b60ba490b5dd9e938d2e26940d55ddb3570cc0c015e2557d760a7aa656d11c24` |
| Regression tests | 10,953 | `a2a390c4435126bf9c46d0359b0c5eb13677ed57bfc71c78d09394b146cbde80` |
| Archive manifest | 94,060 | `e8fccd324e4754dd88ccee220b0c735f69502ff58b3e50447523fc7931530395` |
| Site source register | 110,184 | `57df608a9c6a4a8bb3ccfc28a863a57f8cbabb52edf82a106eff57e8b8e8257a` |

The two workbooks are not byte-identical. The site copy has five additional Taiwan absconded-worker columns, while all 56 reference columns match the site CSV representation cell-for-cell after normalized comparison.

## Audit method

1. Load the external workbook with `pandas`/`openpyxl` and identify its 40 ISO3 countries and nine worksheets.
2. Parse the shipped static HTML with BeautifulSoup. Country-page panel tables and evidence-page value tables were parsed independently.
3. Normalize displayed numbers including commas, percentages, fractions, blank markers, and integer-valued floats. Numeric equality uses exact equality after normalization, with a `1e-9` tolerance for floating-point representations.
4. Compare website panel/evidence values to `Panel_final`. Website primary irregular estimates are compared to the authoritative `Panel_final` value; non-primary rows in `Irregular_estimates_all` are recorded as `N/A` because they are competing estimates rather than displayed panel cells.
5. Compare the site CSV representation of every reference worksheet against the common reference columns. Empty trailing rows are removed before comparison. Numeric cells use the same normalized numeric comparison; text is compared after trimming.
6. Compare grades where a corresponding reference grade column exists. Taiwan’s site-only absconded-worker grade is recorded as site-only metadata, not as a false numerical failure.
7. Collect statistic-associated external URLs from country pages, evidence pages, source pages, the site source register, and the competing-estimate worksheet. Deduplicate by exact URL; 189 unique URLs were tested.
8. Reuse the saved response cache for the final checklist. Each cached response records HTTP status, content type, byte count, SHA-256, local capture path, and (for downloadable HTML) a second-fetch consistency check.
9. Pair live URLs with local PDF/HTML/PNG/CSV/JSON mirrors where the website presents them. Live-byte equality is reported separately from archive integrity because a current dynamic page, PDF mirror, or historical snapshot can legitimately have different bytes.
10. Resolve every local `href`/`src` in generated HTML and recalculate every SHA-256 digest listed in `manifest/checksums.csv`.

The fetch script had to use `requests` with certificate verification disabled because the workstation’s conda activation hook removes `SSL_CERT_FILE`. The saved live status is still the HTTP response status and captured response body; re-running in a different network environment may produce different live statuses.

## Worksheet-by-worksheet comparison

The counts below exclude all-empty trailing rows. Raw workbook/CSV files contain one trailing blank row in the usual exported tables.

| Worksheet | Reference rows × columns | Site CSV rows × columns | Common cells compared | Matching cells | Differing cells | Status |
|---|---:|---:|---:|---:|---:|---|
| `README` | 38 × 2 | 38 × 2 | 76 | 76 | 0 | `MATCH` |
| `Panel_final` | 520 × 56 | 520 × 61 | 29,120 | 29,120 | 0 | `MATCH_CORE_PLUS_SITE_COLUMNS` |
| `Data_quality` | 240 × 10 | 240 × 10 | 2,400 | 2,400 | 0 | `MATCH` |
| `Corrections_applied` | 49 × 7 | 49 × 7 | 343 | 343 | 0 | `MATCH` |
| `Known_issues` | 14 × 6 | 14 × 6 | 84 | 84 | 0 | `MATCH` |
| `Verification_log` | 2,454 × 12 | 2,454 × 12 | 29,448 | 29,448 | 0 | `MATCH` |
| `Source_register` | 314 × 10 | 314 × 11 | 3,140 | 3,038 | 102 | `UPDATED_SITE_REGISTER` |
| `Irregular_estimates_all` | 433 × 10 | 433 × 10 | 4,330 | 4,330 | 0 | `MATCH` |
| `Codebook` | 17 × 3 | 17 × 3 | 51 | 51 | 0 | `MATCH` |

### Worksheet differences requiring interpretation

- `Panel_final`: the site adds `irregular_proxy_absconded_workers_source`, `_url`, `_note`, `_ref_date`, and `_grade`. The 56 shared columns match exactly.
- `Source_register`: the site has an additional `outcome` column and refreshed metadata. The 102 common-column differences are confined to `retrieval`, `local_file`, and `note`; the site records current archive/substitution/recovery work that is not present in the external workbook’s older register.
- Workbook byte identity: the external workbook and site-bundled workbook have different byte hashes and sizes. This is flagged as `DIFF` even though common worksheet data matches.

### Website-wide headline differences

| Item | Website | Reference/workbook basis | Interpretation |
|---|---:|---:|---|
| Values with a quality grade | 1,699 | 1,692 | The site counts seven Taiwan absconded-worker grade cells stored in site-only columns. |
| Country-source citations archived/total | 76/78 | 87/89 | The website headline uses a narrower country-source citation/archive scope than the workbook README document-source totals. |

These are the two `PRESENTATION_MISMATCH` rows shown in `WORKBOOK_AUDIT` and `ALL_HEADLINES`.

## Local links, archive files, and snapshots

| Check | Result |
|---|---:|
| Local HTML `href`/`src` references scanned | 7,351 |
| Unique local paths referenced | 734 |
| Missing local paths | 0 |
| Manifest entries checked | 778 |
| Manifest entries with exact bytes and SHA-256 | 778 |
| Manifest entries not linked from generated HTML | 1 (`manifest/checksums.csv` itself) |
| Unique external URLs | 189 |
| URLs with an existing local archive association | 188 |
| Associated archives whose files exist | 188/188 |
| Associated archives whose manifest status is `all_exact` | 188/188 |

For the 189 unique URLs, the live/archive relationship was:

| Relationship | Count | Meaning |
|---|---:|---|
| `same_bytes` | 45 | Current captured response hash equals at least one presented local archive. |
| `different_snapshot_or_mirror` | 105 | Both live and local archive exist, but bytes differ; this is recorded as a snapshot/format/current-version difference, not automatically as a value error. |
| `not_compared_live_failed` | 38 | Local archive exists, but the current URL could not be downloaded successfully. |
| `no_archive` | 1 | URL is a landing/publisher link with no paired local archive. |

The website’s own source and snapshot records provide additional provenance:

- `data/source_register.csv`: 314 rows; retrieval labels are `VERIFIED_API` 232, `ARCHIVED` 80, and `NOT_RETRIEVED` 2. Outcomes are `VERIFIED_API` 232, `DOWNLOADED` 71, `SUBSTITUTED` 4, `RECOVERED` 3, `RECOVERED_SCREENSHOT` 2, `NOT_RETRIEVED_REDUNDANT` 1, and `NOT_RETRIEVED` 1.
- `data/web_snapshots.csv`: 41 records; `live_render_verified` 33, `rendered_from_archived_html` 5, and `interactive_browser_capture` 3.
- `data/api_snapshots.csv`: 21 captured API records: OECD 13, Eurostat 4, UN DESA 2, and World Bank WDI 2.
- `verification/download_log.csv`: 89 original document retrieval records: HTTP 200 72, cached 7, HTTP 403 6, HTTP 404 2, and errors 2.

## Current external URL results

The complete 189-row URL appendix is the `LINK_AUDIT` worksheet. Its unique-URL status counts are:

| Current status | Count |
|---|---:|
| `downloadable_200` | 151 |
| `rate_limited_429` | 15 |
| `not_found_404` | 14 |
| `blocked_403` | 6 |
| `unreachable` | 2 |
| `bad_request_400` | 1 |

### HTTP 400

The Eurostat URL contains a literal placeholder/ellipsis in the query and returned HTTP 400:

`https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/migr_eipre?...&geo=CH&geo=PT&geo=SE&sinceTimePeriod=2010&untilTimePeriod=2023`

### HTTP 403

- `https://journals.sagepub.com/doi/10.1177/23315024241226624`
- `https://mexico.iom.int/sites/g/files/tmzbdl1686/files/documents/2024-03/estadisticas-migratorias-2023.pdf`
- `https://psa.gov.ph/content/foreign-citizens-country-2020-census-population-and-housing`
- `https://www.gov.il/BlobFolder/generalpage/foreign_workers_stats/he/zarim_2022_q1.pdf`
- `https://www.ismu.org/comunicato-stampa-xxv-rapporto-ismu/`
- `https://www.ismu.org/xxvii-rapporto-sulle-migrazioni-2021-comunicato-stampa-11-2-2022/`

The site’s notes record browser/header captures or substituted official series where available. For example, the PSA page was captured interactively and its 78,396 foreign-citizen value matched the workbook; the IOM, gov.il, and ISMU records have local substitutions or browser captures as described in `LINK_AUDIT`.

### HTTP 404

- `https://population.un.org/wpp/downloads`
- `https://sdmx.oecd.org/public/rest/data/OECD.ELS.IMD,DSD_MIG*/AUS.W.A.B14._T._Z._Z.PS?startPeriod=2010&endPeriod=2022`
- `https://sdmx.oecd.org/public/rest/data/OECD.ELS.IMD,DSD_MIG*/CHL.W.A.B14._T._Z._Z.PS?startPeriod=2010&endPeriod=2022`
- `https://sdmx.oecd.org/public/rest/data/OECD.ELS.IMD,DSD_MIG*/CHL.W.A.B15._T._Z._Z.PS?startPeriod=2010&endPeriod=2022`
- `https://sdmx.oecd.org/public/rest/data/OECD.ELS.IMD,DSD_MIG*/ISR.W.A.B14._T._Z._Z.PS?startPeriod=2010&endPeriod=2022`
- `https://sdmx.oecd.org/public/rest/data/OECD.ELS.IMD,DSD_MIG*/JPN.W.A.B15._T._Z._Z.PS?startPeriod=2010&endPeriod=2022`
- `https://sdmx.oecd.org/public/rest/data/OECD.ELS.IMD,DSD_MIG*/KOR.W.A.B15._T._Z._Z.PS?startPeriod=2010&endPeriod=2022`
- `https://sdmx.oecd.org/public/rest/data/OECD.ELS.IMD,DSD_MIG*/MEX.W.A.B14._T._Z._Z.PS?startPeriod=2010&endPeriod=2022`
- `https://sdmx.oecd.org/public/rest/data/OECD.ELS.IMD,DSD_MIG*/MEX.W.A.B15._T._Z._Z.PS?startPeriod=2010&endPeriod=2022`
- `https://sdmx.oecd.org/public/rest/data/OECD.ELS.IMD,DSD_MIG*/NZL.W.A.B14._T._Z._Z.PS?startPeriod=2010&endPeriod=2022`
- `https://sdmx.oecd.org/public/rest/data/OECD.ELS.IMD,DSD_MIG*/TUR.W.A.B14._T._Z._Z.PS?startPeriod=2010&endPeriod=2022`
- `https://sdmx.oecd.org/public/rest/data/OECD.ELS.IMD,DSD_MIG*/TUR.W.A.B15._T._Z._Z.PS?startPeriod=2010&endPeriod=2022`
- `https://www.nisshinkyo.org/news/pdf/G-26-2.pdf`
- `https://www.sem.admin.ch/dam/sem/de/data/internationales/illegale-migration/sans_papiers/ber-sanspapiers-2015-d.pdf`

The OECD wildcard endpoints are separate from the exact current JSON queries. The website’s API snapshot files retain the previously captured data used for value verification.

### HTTP 429

All 15 rate-limited URLs are OECD SDMX JSON endpoints. They were not treated as numeric mismatches because the source register records successful API re-query/value comparison on 2026-08-17 and the website retains API snapshots. The exact rate-limited endpoints were:

- `https://sdmx.oecd.org/public/rest/data/OECD.ELS.IMD,DSD_MIG*/USA.W.A.B14._T._Z._Z.PS?startPeriod=2010&endPeriod=2022`
- `https://sdmx.oecd.org/public/rest/data/OECD.ELS.IMD,DSD_MIG*/USA.W.A.B15._T._Z._Z.PS?startPeriod=2010&endPeriod=2022`
- `https://sdmx.oecd.org/public/rest/data/OECD.ELS.IMD,DSD_MIG@DF_MIG,1.0/CHL.W.A.B15._T._Z._Z.PS?startPeriod=2010&endPeriod=2022&format=jsondata&dimensionAtObservation=AllDimensions`
- `https://sdmx.oecd.org/public/rest/data/OECD.ELS.IMD,DSD_MIG@DF_MIG,1.0/JPN.W.A.B15._T._Z._Z.PS?startPeriod=2010&endPeriod=2022&format=jsondata&dimensionAtObservation=AllDimensions`
- `https://sdmx.oecd.org/public/rest/data/OECD.ELS.IMD,DSD_MIG@DF_MIG,1.0/KOR.W.A.B15._T._Z._Z.PS?startPeriod=2010&endPeriod=2022&format=jsondata&dimensionAtObservation=AllDimensions`
- `https://sdmx.oecd.org/public/rest/data/OECD.ELS.IMD,DSD_MIG@DF_MIG,1.0/MEX.W.A.B15._T._Z._Z.PS?startPeriod=2010&endPeriod=2022&format=jsondata&dimensionAtObservation=AllDimensions`
- `https://sdmx.oecd.org/public/rest/data/OECD.ELS.IMD,DSD_MIG@DF_MIG,1.0/TUR.W.A.B15._T._Z._Z.PS?startPeriod=2010&endPeriod=2022&format=jsondata&dimensionAtObservation=AllDimensions`
- `https://sdmx.oecd.org/public/rest/data/OECD.ELS.IMD,DSD_MIG@DF_MIG,1.0/USA.W.A.B15._T._Z._Z.PS?startPeriod=2010&endPeriod=2022&format=jsondata&dimensionAtObservation=AllDimensions`
- `https://sdmx.oecd.org/public/rest/data/OECD.ELS.IMD,DSD_MIG_F@DF_MIG_POPF,1.0/AUS.W.A.B14._T._Z._Z.PS?startPeriod=2010&endPeriod=2022&format=jsondata&dimensionAtObservation=AllDimensions`
- `https://sdmx.oecd.org/public/rest/data/OECD.ELS.IMD,DSD_MIG_F@DF_MIG_POPF,1.0/CHL.W.A.B14._T._Z._Z.PS?startPeriod=2010&endPeriod=2022&format=jsondata&dimensionAtObservation=AllDimensions`
- `https://sdmx.oecd.org/public/rest/data/OECD.ELS.IMD,DSD_MIG_F@DF_MIG_POPF,1.0/ISR.W.A.B14._T._Z._Z.PS?startPeriod=2010&endPeriod=2022&format=jsondata&dimensionAtObservation=AllDimensions`
- `https://sdmx.oecd.org/public/rest/data/OECD.ELS.IMD,DSD_MIG_F@DF_MIG_POPF,1.0/MEX.W.A.B14._T._Z._Z.PS?startPeriod=2010&endPeriod=2022&format=jsondata&dimensionAtObservation=AllDimensions`
- `https://sdmx.oecd.org/public/rest/data/OECD.ELS.IMD,DSD_MIG_F@DF_MIG_POPF,1.0/NZL.W.A.B14._T._Z._Z.PS?startPeriod=2010&endPeriod=2022&format=jsondata&dimensionAtObservation=AllDimensions`
- `https://sdmx.oecd.org/public/rest/data/OECD.ELS.IMD,DSD_MIG_F@DF_MIG_POPF,1.0/TUR.W.A.B14._T._Z._Z.PS?startPeriod=2010&endPeriod=2022&format=jsondata&dimensionAtObservation=AllDimensions`
- `https://sdmx.oecd.org/public/rest/data/OECD.ELS.IMD,DSD_MIG_F@DF_MIG_POPF,1.0/USA.W.A.B14._T._Z._Z.PS?startPeriod=2010&endPeriod=2022&format=jsondata&dimensionAtObservation=AllDimensions`

A PowerShell spot check showed that an OECD `format=csvfile` representation of a short query returned HTTP 200, but that alternate representation is not the same URL as the rate-limited JSON endpoint and is therefore not counted as a successful fetch of the exact URL.

### Unreachable

- `https://press.police.ac.kr/pds/1476878914562.pdf` — connection timeout; the site notes that no web-archive copy was available and that the affected Korea 2010–2015 overstayer values are graded D.
- `https://www.cinformi.it/Comunicazione/Notizie/I-dati-del-Rapporto-ISMU-sulle-migrazioni-2020` — connection timeout; the site notes a replacement by ISMU’s own published series confirming the 2020 value.

## Regression and file-integrity verification

The final checklist was reopened with `openpyxl` and checked as follows:

- 44 sheets present: `SUMMARY`, `WORKBOOK_AUDIT`, `LINK_AUDIT`, 40 ISO3 sheets, and `ALL_HEADLINES`.
- Every country sheet contains all nine worksheet groups, including `Codebook`.
- ZIP container test passed.
- Zero formula cells and zero `#REF!`, `#DIV/0!`, `#VALUE!`, or `#NAME?` strings.
- All nine regression tests passed (`python -m unittest scripts/test_audit_site_against_verified.py -q`).

The spreadsheet-specific `@oai/artifact-tool` runtime was unavailable in this Windows workspace. The checklist was generated with the repository-compatible `openpyxl` writer and then reopened, structurally inspected, ZIP-tested, and formula/error-scanned.

## Exact re-verification procedure

From the repository root, first verify the reference path and the listed hashes. Then run the cached audit:

```powershell
Set-Location 'D:\研究計畫\其他投稿\2026_移民對非本國籍使用公共醫療態度（葉明叡）\claude-work\migration-data-archive'

python scripts/audit_site_against_verified.py `
  --truth ..\FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx `
  --site . `
  --scratch C:\Users\Raymond\AppData\Local\Temp\migration-site-audit `
  --no-fetch `
  --out outputs\audit_site_vs_verified\AUDIT_checklist_site_vs_VERIFIED.xlsx

python -m unittest scripts/test_audit_site_against_verified.py -q
```

`--no-fetch` reuses `C:\Users\Raymond\AppData\Local\Temp\migration-site-audit\downloads\fetch_cache.json`, whose audit-run SHA-256 was:

`33d2ba42d954daf208cae9df27c2628162b3f0ac89055be0e6cfd3a3bab4a65c` (153,129 bytes).

The cached summary files were:

- `C:\Users\Raymond\AppData\Local\Temp\migration-site-audit\audit_summary.json` — SHA-256 `727814c7318e4b27e2764273023f2f476e9bd86fc3a55534476980f848e55550`.
- `C:\Users\Raymond\AppData\Local\Temp\migration-site-audit\audit_summary.csv` — SHA-256 `547d8c07ad8e937d5c3af72d20368c0eb55bb8c6117e5caec321aeb8555ac856`.

To refresh live statuses instead of reproducing the saved 2026-08-17 capture, omit `--no-fetch`. Expect current HTTP results to change as publishers rate-limit, move, or repair their URLs:

```powershell
python scripts/audit_site_against_verified.py `
  --truth ..\FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx `
  --site . `
  --scratch C:\Users\Raymond\AppData\Local\Temp\migration-site-audit `
  --workers 6 `
  --out outputs\audit_site_vs_verified\AUDIT_checklist_site_vs_VERIFIED.xlsx
```

For a later review, inspect `SUMMARY` first, then `WORKBOOK_AUDIT` for worksheet/package differences, `LINK_AUDIT` for the complete URL-level evidence, and each ISO3 sheet for the per-country/per-worksheet rows. The `content_compare` counts in the summary are row-level page/archive associations; the unique-URL conclusion must be taken from `LINK_AUDIT`.

