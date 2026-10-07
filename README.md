# Migration and Population Data Archive<br>移民與人口資料存檔

**40 countries, 2001–2022 · 40 國，2001–2022 年**

Joint work of [Prof. Raymond Kuo](https://raymond.cph.ntu.edu.tw/), National Taiwan University,
and Claude (Anthropic).<br>
本存檔為國立臺灣大學[郭年真教授](https://raymond.cph.ntu.edu.tw/)與 Claude（Anthropic）之共同成果。

**Browse: <https://raymondkuo.github.io/migration-healthcare-attitudes-evidence/>**

Source archive and verification record for the migration and population panel used in a study of
**attitudes toward publicly funded healthcare for non-nationals**. It exists so that a journal
editor or peer reviewer can check every number in the dataset against the source it came from,
without depending on any external server still being available. All sources were retrieved and
verified on **2026-08-17**. The panel was extended back from 2010 to 2001 on **2026-10-07** (see *Extension* below).

本存檔為「民眾對非本國籍人士使用公費醫療之態度」研究之來源存檔與查證紀錄，
目的在於讓期刊編輯與審查委員能將資料集中的每一個數字追溯至其來源，
且不需依賴任何外部伺服器仍然運作。所有來源均於 **2026-08-17** 取得並完成查證。面板已於 **2026-10-07** 向前延伸至 2001 年（見下方「延伸」）。

---

## Bilingual · 雙語

**Every page exists in English and 繁體中文.** The language button in the top-right corner of each
page switches between them and keeps you on the same content.<br>
**每一頁都有英文與繁體中文版本。**點選每頁右上角的語言按鈕即可切換，並停留在相同內容的頁面。

| | English | 繁體中文 |
|---|---|---|
| Overview 總覽 | `index.html` | `index.zh.html` |
| Countries 各國 | `countries.html` | `countries.zh.html` |
| A country 單一國家 | `countries/CHE.html` | `countries/CHE.zh.html` |
| An evidence page 佐證頁 | `evidence-pages/CHE__irregular_stock.html` | `…__irregular_stock.zh.html` |
| Sources 資料來源 | `sources.html` | `sources.zh.html` |
| Data files 資料檔案 | `data.html` | `data.zh.html` |
| Verification 查證紀錄 | `verification.html` | `verification.zh.html` |
| Methods 研究方法 | `methods.html` | `methods.zh.html` |

**406 pages** — 203 per language. Validated: 26,830 internal links, 0 broken.

### What is translated, and what is deliberately not · 翻譯範圍

Translated: navigation, headings, prose, table headers, variable and country names, quality grades,
verification statuses, correction reasons, the codebook, the known-issues register and the
data-quality assessments.

Not translated, by design: **source names and citations** (a source is cited as its publisher
titled it), **URLs, file names, column names and variable codes** (`foreign_nationals_pct_pop` is
identical in both languages so code, CSVs and text agree), **the data itself**, and **workbook
sheet names**. Taiwan terminology is used throughout: 臺灣、資料、外國籍人口、外國出生人口、
逾期停留・居留、查獲人數、失聯移工、內政部移民署、勞動部。

---

## What is here

| Path | Contents |
|---|---|
| `index.html` / `index.zh.html` | Overview, headline verification results |
| `countries.html`, `countries/<ISO3>.html` | One page per country: data, verification result, sources |
| `evidence-pages/` | 157 per-country, per-variable evidence pages (×2 languages) — every value with its source, verification result and archived files |
| `sources.html` | Complete source register — original URL plus archived copy for each |
| `data.html` | Download the dataset and every supporting table |
| `verification.html` | All 2,737 value comparisons, the 1,777 re-comparisons of 2026-10-07, corrections, the extension and the issues |
| `methods.html` | Procedure, grading scheme, and guidance on variable reliability |
| `data/` | The verified panel (Excel + CSV), codebook, logs, the two original inputs, and a second independently produced summary workbook — see `data/ABOUT_THE_TWO_WORKBOOKS.md` |
| `evidence/api/` | Raw API response payloads exactly as returned by the publisher |
| `evidence/api/publisher_pages/` | PDF and screenshot mirrors of the publishers' own dataset pages |
| `evidence/countries/<ISO3>/` | Every source document, PDF mirror and screenshot for that country |
| `evidence/extracts/` | 157 bilingual PDF extracts, one per country × variable |
| `manifest/checksums.csv` | SHA-256 hash of every file in the archive, of the bytes the website serves (text files with LF line endings, so a Windows checkout with CRLF will not match; `scripts/78_verify_checksums.py` checks the manifest against git) |
| `verification/` | Machine-readable verification output, the live link sweep, and the audit response |
| `scripts/` | Every script used. Only the pipeline in `REBUILD.md` can be re-run safely; the first-release builders (numbered below 67) would undo later corrections |
| `VERIFICATION_REPORT.md` | The written verification report (first release; kept as written) |
| `REBUILD.md` | The supported order for rebuilding this release, and what must not be re-run |
| `verification/AUDIT_RESPONSE_2026-10-07.md` | The response to the audit of 2026-10-07, finding by finding |
| `data/ANALYSIS_NOTES.md` | The construct, timing, universe and sensitivity choices that are the authors' to make |
| `verification/AUDIT_response.md` | Point-by-point response to that audit, and what was fixed |

<!-- headline:begin -->
## Headline results

**At first release (2026-08-17 / 08-18; the figures in this block are frozen as published in commit `0d64a1c`)**

- **2,454** values re-derived from live sources; **2,415 (98.4%)** matched exactly.
- **39** discrepancies found — all one error: the Eurostat irregular-migration detections
  series for **Switzerland, Portugal and Sweden** was offset by one year in one input workbook.
- **49** corrections across 5 countries, each itemised with its evidence
  (`data/corrections_applied.csv`).
- **76 of 78** distinct country-source document citations archived, across 72 URLs; the 2 that could not be retrieved are named.
- **Every retained number cites an archived source.** Whether a source was read under the right year and
  concept is a separate question, and the audit of 2026-10-07 found it was not always (below). At first
  release each of the 116 values that were not machine-verified was checked against the archived source
  document: 102 were found in it and regraded B, 13 are derived from a published range and are flagged ≈, and 1
  (Russia 2020 irregular stock) could not be traced to anything and was **deleted** — see
  `data/deleted_values.csv`.
- **Every archived source file has a viewable mirror.** Every PDF, HTML page, raw JSON/CSV API
  payload and spreadsheet carries a rendered PNG or PDF companion, so a reader can see the content
  without trusting an opaque binary.
- Korea's 2010–2015 overstayer figures, which were grade D because their only cited source was
  offline, were re-sourced to the Ministry of Justice series, and one error was found and corrected.
- **Every number in every country's Panel data table is a link.** Click a value, or the grade pill
  beside it, and you reach the evidence for that exact figure.

**Now (revised 2026-10-07)**

- **Audit of 2026-10-07** (issues #1–#25): all 24 findings were re-checked against the archived sources and
  confirmed; **45 cell changes** followed, counting the audit and the re-audit below (15 corrected, 7 regraded, 6 relabelled, 6 added, 4 source corrected, 4 flag added, 2 metadata cleared, 1 deleted). The response is in
  `verification/AUDIT_RESPONSE_2026-10-07.md`; the dispositions of all **3,365** current observations are in
  `data/current_panel_verification.csv`. The 2,454 / 2,737 figures above are comparison *records* of the first-release
  check, not a count of unique current observations.
- **Re-audit of 2026-10-07**, an independent re-check of commit `30d6cb1` (issues #5, #11, #12, #13, #17, #20 and #21
  reopened, #27–#30 opened): all **11** findings were confirmed and are answered in the same response file. 5 of the
  cell changes above belong to it (a detection break flag, a derived flag; no value changed).
- **67** value corrections across 10 countries are itemised in `data/corrections_applied.csv`
  (the 49 of the first release, later amendments, and 15 from the audit of 2026-10-07), and 2 deletions in
  `data/deleted_values.csv`.
- Quality grades on the 2,478 displayed values of the six headline variables (2001–2022): **A** 2,323 · **B** 142 · **C** 13 · **D** 0.
  With the 7 Taiwan absconded-worker values (all grade B) the displayed total is 2,485: **A** 2,323 · **B** 149 · **C** 13.
  A grade says where a value was read from (A decoded from a machine-readable source, B read from an archived document,
  C the midpoint of a published range computed by the archive; a single-number estimate a source publishes is A or B);
  it does not say how precise or comparable the value is.
- Link sweep of 2026-10-07 over **195** external URLs: 184 reachable (0 only on a curl retry,
  after a failed first attempt), 11 blocked, moved or lost and documented with their archived copies,
  **0 undocumented failures** (`verification/link_sweep.csv`, with the date and method of each check).

## Extension to 2001 · 延伸至 2001 年

On **2026-10-07** the panel was extended from 2010–2022 back to **2001**, following the plan in
the project notes (foreign-born and foreign-national stocks wherever a verifiable source exists).

- **880 rows** now (was 520); 194 foreign-born and 228 foreign-national values and
  720 population values were added. **No value published before the extension changed**: this
  is asserted cell by cell against the 2026-08-17 panel, and 1,777 published values were
  re-compared with fresh responses from Eurostat, OECD, the World Bank and UN WPP (1,777 identical).
- Each foreign-born / foreign-national value now states its **source type** (annual, census,
  survey, UN estimate) and carries a **flag**. Where an earlier year had to come from a different
  source than the 2010–2022 series (**28 series**), the gap between the two sources over the
  overlapping years was measured; **8 series differ by 5% or more** and are flagged as a
  break in the series (largest: Slovakia and Denmark foreign-born).
- Not everything could be found. Australia's foreign nationals and Chile's 2002 foreign-born count were
  searched for and not obtained; several countries have only census years; nothing was
  approximated. See `data/known_issues.csv` and the *Verification* page.
- The file names that carry "2010-2022" are unchanged so that existing links keep working; the
  data inside run 2001–2022.
- Unresolved, for the authors: UN DESA labels the migrant stock of China, India, the Philippines,
  Suriname and Thailand as based on citizenship although the panel carries it as foreign-born
  (`data/known_issues.csv`).
<!-- headline:end -->

## How sources were preserved

**Statistical APIs** (World Bank, Eurostat, OECD, UN DESA) — the raw response payload was saved
byte-for-byte in `evidence/api/`, together with the exact query URL that produced it. Because a
JSON payload is precise but not readable, the publishers' own dataset pages were **also mirrored as
PDF and screenshot** in `evidence/api/publisher_pages/`. Two publishers refuse automated clients:
the UN DESA page was fetched with a normal HTTP client and that retrieved copy rendered, and
`oecd.org` was replaced by the OECD SDMX registry's authoritative dataflow definition — the service
the data was actually queried from.

**Documents** (PDF reports, statistical yearbooks) — downloaded to the country folder.

**Web pages** — archived three ways where possible: the original HTML, a PDF mirror, and a
full-page PNG screenshot, all captured on the access date. Each render was validated by dumping the
rendered DOM and testing it against a list of bot-wall and block-page markers; any page that
answered with an interstitial was re-rendered from the HTML copy archived earlier the same day and
is labelled `rendered_from_archived_html` in `data/web_snapshots.csv`.

## Publishing

`.github/workflows/pages.yml` deploys to GitHub Pages on every push to `main`. The site is plain
static HTML and CSS with no external requests and no build step; `.nojekyll` stops Jekyll rewriting
the paths.

Notes:
- About 386 MB across 1,358 files. No single file exceeds 27 MB; the largest is UN_WPP2024_demographic_indicators_compact.xlsx at 26 MB.
- `robots.txt` asks search engines not to index the archive while the manuscript is under review.
  Relax it once the paper is published.
- The archive is public and readable by anyone with the link, and it names the authors. If the
  journal uses double-blind review, send reviewers a ZIP instead, or publish an anonymised copy for
  the review period.

## Reusing and citing

Files under `evidence/` are **mirrors held for verification**. Copyright in each source document
remains with its publisher, and every entry links to the original URL. The compiled dataset,
verification log and code may be reused with attribution to the study.

## Re-running

The supported rebuild is in **[`REBUILD.md`](REBUILD.md)**: the order, what is pinned (commit `0d64a1c` and the archived payloads), and which first-release scripts must not be re-run because they would undo later corrections. Needs `pip install pandas openpyxl pymupdf pdfplumber pypdf`. After committing, `python scripts/78_verify_checksums.py` compares `manifest/checksums.csv` with what git stored.

Translations live in `scripts/i18n.py` (UI, countries, variables) and `scripts/i18n_content.py`
(long-form prose, codebook, known issues).<br>
翻譯內容分別位於 `scripts/i18n.py`（介面、國名、變項）與 `scripts/i18n_content.py`
（長篇說明、變項說明書、已知問題）。
