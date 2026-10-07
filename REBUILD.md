# Rebuilding this release

*Written 2026-10-07 after audit finding F21. The procedure below is the supported one: it was run in an
isolated clone of the repository and reproduced the committed data files (see "Tested" at the end).*

## 1. What must not be re-run

`scripts/` holds two generations of code.

**The first release (2026-08-17 to 2026-10-02), scripts numbered below 67.** They built the 2010-2022 panel from
the two input workbooks and the first-release payloads (`01`-`11`), then corrected it step by step (`40`-`66`).
Several expect a `data_raw/` folder and the input workbooks in the archive root, which no longer exist there
(the payloads are under `evidence/api/`, the inputs under `data/original_inputs/`). **Re-running them
regenerates the first-release panel and undoes every later correction.** They are kept as the record of how the
first release was made, not as a build. The only scripts below 67 that belong to the supported build are the
page and check scripts listed in section 3 (`build_core.py`, `build_pages.py`, `build_evidence.py`,
`build_pdf_extracts.py`, `27_validate_site.py`, `28_checksums.py`, `29_website_manifest.py`,
`validate_bilingual.py`, `41_link_sweep.py`, `45_build_source_mirrors.py`, `57_sync_workbook_sheets.py`,
`63_export_clean_panel.py`, `66_revision_history.py`).

There is no `build-site.mjs` in this archive; older reports that name one describe the first-release tooling.

## 2. What is pinned

- **The pre-extension panel is commit `0d64a1c`.** The assembler (`74`) and the collectors read it from git, so
  clone the full history (`git clone`, not a shallow clone). Every value of that panel is asserted unchanged
  afterwards, except the cells listed one by one in `data/audit_changes_2026-10-07.csv`.
- **The source payloads and documents are the archived files** under `evidence/api/` and `evidence/countries/`,
  each with its retrieval date in its name or in `data/api_snapshots.csv` / `data/source_register.csv`.
  The 2001-2022 payloads are dated 2026-10-07.
- **The collector outputs** (`data/extension_staging/*.csv`) are committed, so the build does not need the
  network.

## 3. The supported order

Run from the archive root. Python 3.11+ with pandas, openpyxl, PyMuPDF (`fitz`), pdfplumber, pypdf.

| Step | Command | What it does |
|---|---|---|
| 1 | `python scripts/74_assemble_panel.py` | Merges the staged 2001-2009 cells into `panel_final.csv`; marks the concept of each foreign-born cell; fails if a first-release value changed outside the audit list |
| 2 | `python scripts/79_apply_audit_corrections.py` | Applies the corrections, additions, deletion and regrades of the audit of 2026-10-07; writes `audit_changes_2026-10-07.csv`, `corrections_applied.csv`, `deleted_values.csv` |
| 3 | `python scripts/81_audit_reference_tables.py` | Status of every irregular-estimate record; `data_from_source.csv` for every country; source-register routing; country READMEs |
| 4 | `python scripts/75_build_derived_tables.py` | Source register rows for the extension, per-country manifests, data quality, evidence index, known issues, codebook |
| 5 | `python scripts/66_revision_history.py` | The dated revision history (reads the commit stamp files for the commit and time) |
| 6 | `python scripts/63_export_clean_panel.py` | The analysis extract (xlsx and csv) and `foreign_born_below_foreign_nationals.csv`, which the next two steps read |
| 7 | `python scripts/82_audit_documents.py` | `current_panel_verification.csv`, `secondary_workbook_differences.csv`, `ABOUT_THE_TWO_WORKBOOKS.md`, `ANALYSIS_NOTES.md` |
| 8 | `python scripts/83_audit_response.py` | The response to the audit |
| 9 | `python scripts/57_sync_workbook_sheets.py` | Rewrites the main workbook's sheets from the CSVs |
| 10 | `python scripts/80_check_source_charts.py` | Source-label check: the Chile chart is read from the PDF's coordinates and compared with the panel |
| 11 | `python scripts/build_core.py`, `build_pages.py`, `build_evidence.py` | The 406 pages, both languages |
| 12 | `python scripts/build_pdf_extracts.py` | The PDF extracts (needs Windows and Chrome; about 8 minutes) |
| 13 | `python scripts/28_checksums.py`, `29_website_manifest.py`, `27_validate_site.py`, `validate_bilingual.py`, `77_update_readme.py`, then `28_checksums.py` again | Checksums, manifest, validators, README and CITATION numbers |
| 14 | after committing: `python scripts/78_verify_checksums.py` | Compares the manifest with what git stored |

Every step is idempotent. `45_build_source_mirrors.py` creates the `MIRROR__` renderings of newly archived files;
`41_link_sweep.py` re-tests every external URL (`--retry-only` re-tests just the failures with curl).

## 4. Re-collecting the sources (needs the network)

`67` (bulk payloads) and `68`-`73` (Eurostat/OECD cells, population and UN DESA, Taiwan, census documents, Russia, UK)
re-collect the 2001-2009 extension and rewrite `data/extension_staging/`. Run `68` and `69` together: `69` appends its
comparison rows to the file `68` writes. A re-collection will overwrite archived payloads with newer responses, so the
extension's retrieval dates and the overlap check (1,777 of 1,777 identical on 2026-10-07) must be re-established
before anything is committed.

## 5. Checks that are not about links or hashes

The validators confirm that pages link, translate, display the panel's numbers and match their checksums. They cannot
tell whether a source was read under the right year or concept. For that:

- `scripts/80_check_source_charts.py` ties each Chile value to a year and a series by the chart's own geometry;
- `data/current_panel_verification.csv` records, per observation, the source, unit, concept and how it was checked;
- `verification/AUDIT_RESPONSE_2026-10-07.md` records how each audit finding was re-checked.

## Tested

The order in section 3 was run (steps 1-10 and the page build) in a fresh clone of the repository on 2026-10-07 and the
committed data files were reproduced byte for byte (see `verification/AUDIT_RESPONSE_2026-10-07.md`, finding F21).
