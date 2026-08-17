# Migration and Population Data Archive<br>移民與人口資料存檔

**40 countries, 2010–2022 · 40 國，2010–2022 年**

Joint work of [Prof. Raymond Kuo](https://raymond.cph.ntu.edu.tw/), National Taiwan University,
and Claude (Anthropic).<br>
本存檔為國立臺灣大學[郭柏秀教授](https://raymond.cph.ntu.edu.tw/)與 Claude（Anthropic）之共同成果。

**Browse: <https://raymondkuo.github.io/migration-healthcare-attitudes-evidence/>**

Source archive and verification record for the migration and population panel used in a study of
**attitudes toward publicly funded healthcare for non-nationals**. It exists so that a journal
editor or peer reviewer can check every number in the dataset against the source it came from,
without depending on any external server still being available. All sources were retrieved and
verified on **2026-08-17**.

本存檔為「民眾對非本國籍人士使用公費醫療之態度」研究之來源存檔與查證紀錄，
目的在於讓期刊編輯與審查委員能將資料集中的每一個數字追溯至其來源，
且不需依賴任何外部伺服器仍然運作。所有來源均於 **2026-08-17** 取得並完成查證。

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

**404 pages** — 202 per language. Validated: 15,540 internal links, 0 broken.

### What is translated, and what is deliberately not · 翻譯範圍

Translated: navigation, headings, prose, table headers, variable and country names, quality grades,
verification statuses, correction reasons, the codebook, the known-issues register and the
data-quality assessments.

Not translated, by design: **source names and citations** (a source is cited as its publisher
titled it), **URLs, file names, column names and variable codes** (`foreign_nationals_pct_pop` is
identical in both languages so code, CSVs and text agree), **the data itself**, and **workbook
sheet names**. Taiwan terminology is used throughout: 臺灣、資料、外國籍人口、外國出生人口、
逾期停留・居留、查獲人次、失聯移工、內政部移民署、勞動部。

---

## What is here

| Path | Contents |
|---|---|
| `index.html` / `index.zh.html` | Overview, headline verification results |
| `countries.html`, `countries/<ISO3>.html` | One page per country: data, verification result, sources |
| `evidence-pages/` | 156 per-country, per-variable evidence pages (×2 languages) — every value with its source, verification result and archived files |
| `sources.html` | Complete source register — original URL plus archived copy for each |
| `data.html` | Download the dataset and every supporting table |
| `verification.html` | All 2,454 value comparisons, corrections and issues |
| `methods.html` | Procedure, grading scheme, and guidance on variable reliability |
| `data/` | The verified panel (Excel + CSV), codebook, logs, the two original inputs, and a second independently produced summary workbook — see `data/ABOUT_THE_TWO_WORKBOOKS.md` |
| `evidence/api/` | Raw API response payloads exactly as returned by the publisher |
| `evidence/api/publisher_pages/` | PDF and screenshot mirrors of the publishers' own dataset pages |
| `evidence/countries/<ISO3>/` | Every source document, PDF mirror and screenshot for that country |
| `evidence/extracts/` | 156 bilingual PDF extracts, one per country × variable |
| `manifest/checksums.csv` | SHA-256 hash of every file in the archive |
| `verification/` | Machine-readable verification output, the live link sweep, and the audit response |
| `scripts/` | Every script used, so the verification and the site build can be re-run |
| `VERIFICATION_REPORT.md` | The written verification report |
| `AUDIT_report_site_vs_VERIFIED.md` | Independent site-vs-workbook audit |
| `verification/AUDIT_response.md` | Point-by-point response to that audit, and what was fixed |

## Headline results

- **2,454** values re-derived from live sources; **2,415 (98.4%)** matched exactly.
- **39** discrepancies found — all one error: the Eurostat irregular-migration detections series
  for **Switzerland, Portugal and Sweden** was offset by one year in one input workbook.
- **49** values corrected across 5 countries, each itemised with its evidence.
- **76 of 78** distinct country-source document citations archived, across 72 URLs; the 2 that
  could not be retrieved are named.
- Quality grades on all 1,699 displayed values: **A** 1,564 · **B** 11 · **C** 118 · **D** 6.
- **Every number in every country's Panel data table is a link.** Click a value, or the grade pill
  beside it, and you reach the evidence for that exact figure.
- Live sweep of all **176** external URLs the site publishes: **0 undocumented failures**
  (`verification/link_sweep.csv`).

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
- About 232 MB across ~990 files. No single file exceeds 50 MB; the largest is the UN WPP 2024
  workbook at 26 MB.
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

```bash
pip install pandas openpyxl

# verification chain
python scripts/02_fetch_bulk.py          # re-download the bulk sources
python scripts/03_verify_api.py          # compare every value
python scripts/04_verify_oecd.py
python scripts/09_audit.py               # internal-consistency audit
python scripts/41_link_sweep.py          # live sweep of every published URL

# bilingual site build
python scripts/build_core.py             # index, countries index, 40 country pages ×2
python scripts/build_evidence.py         # 156 evidence pages ×2
python scripts/build_pages.py            # sources, data, verification, methods ×2
python scripts/build_pdf_extracts.py     # 156 bilingual PDF extracts
python scripts/validate_bilingual.py     # link, language-pairing and cell-link validation
python scripts/28_checksums.py           # refresh manifest/checksums.csv
```

Translations live in `scripts/i18n.py` (UI, countries, variables) and `scripts/i18n_content.py`
(long-form prose, codebook, known issues).<br>
翻譯內容分別位於 `scripts/i18n.py`（介面、國名、變項）與 `scripts/i18n_content.py`
（長篇說明、變項說明書、已知問題）。
