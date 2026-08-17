# Migration and Population Data Archive, 40 countries, 2010–2022

Source archive and verification record for the migration and population panel used in a study of
**attitudes toward publicly funded healthcare for non-nationals**.

This archive is joint work of **[Prof. Raymond Kuo](https://raymond.cph.ntu.edu.tw/), National
Taiwan University**, and **Claude** (Anthropic).

This repository exists so that a journal editor or peer reviewer can check every number in the
dataset against the source it came from, without depending on any external server still being
available. All sources were retrieved and verified on **2026-08-17**.

**Browse the archive: `https://raymondkuo.github.io/migration-healthcare-attitudes-evidence/`**

---

## What is here

| Path | Contents |
|---|---|
| `index.html` | Overview, headline verification results |
| `countries.html`, `countries/<ISO3>.html` | One page per country: data, verification result, sources |
| `sources.html` | Complete source register — original URL plus archived copy for each |
| `data.html` | Download the dataset and every supporting table |
| `verification.html` | All 2,454 value comparisons, corrections and issues |
| `methods.html` | Procedure, grading scheme, and guidance on variable reliability |
| `data/` | The verified panel (Excel + CSV), codebook, logs, the two original inputs, and a second independently produced summary workbook — see `data/ABOUT_THE_TWO_WORKBOOKS.md` |
| `evidence-pages/` | 156 per-country, per-variable evidence pages — every value with its source, verification result and archived files |
| `evidence/extracts/` | 156 PDF extracts, one per country x variable, so every number exists in a fixed citable document |
| `evidence/api/` | Raw API response payloads exactly as returned by the publisher |
| `evidence/api/publisher_pages/` | PDF and screenshot mirrors of the publishers' own dataset pages |
| `evidence/countries/<ISO3>/` | Every source document, PDF mirror and screenshot for that country |
| `manifest/checksums.csv` | SHA-256 hash of every file in the archive |
| `scripts/` | Every script used, so the verification can be re-run |
| `VERIFICATION_REPORT.md` | The written verification report |
| `manifest/website_manifest.json` | SHA-256 and page-count manifest for the website packaging |

## Headline results

- **2,454** values re-derived from live sources; **2,415 (98.4%)** matched exactly.
- **39** discrepancies found — all one error: the Eurostat irregular-migration detections series
  for **Switzerland, Portugal and Sweden** was offset by one year in one input workbook.
- **49** values corrected across 5 countries, each itemised with its evidence.
- **76 of 78** distinct country-source document citations archived, across 72 URLs; the 2
  that could not be retrieved are named.
- Quality grades on all 1,699 values: **A** 1,564 · **B** 11 · **C** 111 · **D** 6.
- **Every number in every country's Panel data table is a link.** Click a value, or the grade pill
  beside it, and you reach the evidence for that exact figure.

## How sources were preserved

**Statistical APIs** (World Bank, Eurostat, OECD, UN DESA) — the raw response payload was saved
byte-for-byte in `evidence/api/`, together with the query URL that produced it, so the request can
be repeated and compared. Because a JSON payload is precise but not readable, the publishers' own
dataset pages were **also mirrored as PDF and screenshot** in `evidence/api/publisher_pages/`, so
the bulk sources carry the same visual evidence the document sources do. Two publishers refuse
automated clients: the UN DESA page was fetched with a normal HTTP client and that retrieved copy
rendered, and `oecd.org` was replaced by the OECD SDMX registry's authoritative dataflow
definition — the service the data was actually queried from.

**Documents** (PDF reports, statistical yearbooks) — downloaded to the country folder.

**Web pages** — archived three ways where possible: the original HTML, a PDF mirror, and a
full-page PNG screenshot, all captured on the access date. Each render was validated by dumping
the rendered DOM and testing it against a list of bot-wall and block-page markers; any page that
had answered with an interstitial was re-rendered from the HTML copy archived earlier the same
day and is labelled `rendered_from_archived_html` in `data/web_snapshots.csv`.

## Publishing this to GitHub Pages

```bash
cd migration-data-archive
git add -A
git commit -m "Publish migration evidence archive"
git push -u origin main
```

The repository includes `.github/workflows/pages.yml`. On GitHub, open **Settings → Pages** and select
**GitHub Actions** if Pages has not selected the workflow automatically. The public site is
`https://raymondkuo.github.io/migration-healthcare-attitudes-evidence/`.

Notes:
- The site is plain static HTML and CSS with no external requests, so it works on GitHub Pages
  with no build step. A `.nojekyll` file is included to stop Jekyll rewriting the paths.
- The archive is about 203 MB across 437 files, well inside GitHub's limits. No single file
  exceeds 50 MB; the largest is the UN WPP 2024 workbook at 26 MB.
- `robots.txt` currently asks search engines not to index the archive, since the manuscript is
  under review. Relax it once the paper is published.
- If the repository must stay private until the paper is accepted, GitHub Pages for private
  repositories requires a paid plan. A simple alternative is to keep the repository private and
  send reviewers a ZIP of this folder, or make it public only at submission.

## Reusing and citing

Files under `evidence/` are **mirrors held for verification**. Copyright in each source document
remains with its publisher, and every entry links to the original URL. The compiled dataset,
verification log and code in this repository may be reused with attribution to the study.

## Re-running the verification

```bash
pip install pandas openpyxl
python scripts/02_fetch_bulk.py          # re-download the bulk sources
python scripts/03_verify_api.py          # compare every value
python scripts/04_verify_oecd.py
python scripts/09_audit.py               # internal-consistency audit
```

Scripts `20`–`26` rebuild this website from the verification output.
