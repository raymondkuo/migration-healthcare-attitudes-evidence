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
  The 2001-2022 payloads are dated 2026-10-07; the health-expenditure files (World Bank, WHO and the Taiwan
  Ministry of Health and Welfare workbook and report) are dated 2026-10-17, the unemployment files 2026-10-21 and the
  V-Dem files (the V-Dem Institute's R data file and codebook, the V-Dem Codebook, Our World in Data's copy) 2026-10-26
  and the Gini files (World Bank WDI and PIP, OECD IDD) 2026-10-29.
- **The collector outputs** (`data/extension_staging/*.csv`) are committed, so the build does not need the
  network.
- **The audits' result tables are committed** in `data/audit_inputs/` (README there): the re-audit of 2026-10-07 and
  the health-expenditure audit of 2026-10-17. Step 7 reads them to fill the check method and the audit result of every
  observation in `data/current_panel_verification.csv`. They are inputs,
  not products: step 7 stops with a message if they are missing or do not cover an observation, rather than writing
  "not in the audited revision" over a completed audit.

## 3. The supported order

Run from the archive root. Python 3.11+ with pandas, openpyxl, PyMuPDF (`fitz`), pdfplumber, pypdf.

| Step | Command | What it does |
|---|---|---|
| 1 | `python scripts/74_assemble_panel.py` | Merges the staged 2001-2009 cells into `panel_final.csv`; marks the concept of each foreign-born cell; fails if a first-release value changed outside the audit list |
| 2 | `python scripts/79_apply_audit_corrections.py` | Applies the corrections, additions, deletion and regrades of the audit of 2026-10-07; writes `audit_changes_2026-10-07.csv`, `corrections_applied.csv`, `deleted_values.csv` |
| 2a | `python scripts/85_add_health_expenditure.py` | Appends the ten `health_expenditure_pct_gdp*` columns from `data/extension_staging/health_expenditure_cells.csv` (step 1 writes only the columns it knows, so this must follow it); asserts every other column unchanged; adds the rows of the new variable to each country's `data_from_source.csv`, the source register and the country READMEs |
| 2b | `python scripts/88_add_census_non_citizens.py` | Appends the eleven `non_citizens_census*` columns (Australia's 2021 census count of non-citizens, kept out of `foreign_nationals`) from `data/extension_staging/census_non_citizens_cells.csv`; must follow 2a; asserts every other column unchanged; source register and the Australian README |
| 2c | `python scripts/91_add_unemployment.py` | Appends the ten `unemployment_rate*` columns from `data/extension_staging/unemployment_cells.csv`; must follow 2b (which keeps the column order); asserts every other column unchanged; adds the rows of the new variable to each country's `data_from_source.csv`, the source register and the country READMEs |
| 2d | `python scripts/93_add_vdem.py` | Appends the ten `vdem_libdem*` columns (V-Dem liberal democracy index) from `data/extension_staging/vdem_cells.csv`; must follow 2c (which keeps the column order); asserts every other column unchanged; adds the rows of the new variable to each country's `data_from_source.csv`, the source register and the country READMEs |
| 2e | `python scripts/95_add_gini.py` | Appends the ten `gini_index*` columns (Gini index, survey years only) from `data/extension_staging/gini_cells.csv`; must follow 2d (which keeps the column order); asserts every other column unchanged and that every country has a value; adds the rows of the new variable to each country's `data_from_source.csv`, the source register and the country READMEs |
| 3 | `python scripts/81_audit_reference_tables.py` | Status of every irregular-estimate record; `data_from_source.csv` for every country; source-register routing; country READMEs |
| 4 | `python scripts/75_build_derived_tables.py` | Source register rows for the extension, per-country manifests, data quality, evidence index, known issues, codebook |
| 5 | `python scripts/66_revision_history.py` | The dated revision history (reads the commit stamp files for the commit and time) |
| 6 | `python scripts/63_export_clean_panel.py` | The analysis extract (xlsx and csv) and `foreign_born_below_foreign_nationals.csv`, which the next two steps read |
| 7 | `python scripts/82_audit_documents.py` | `current_panel_verification.csv` (reads `data/audit_inputs/`), `secondary_workbook_differences.csv`, `ABOUT_THE_TWO_WORKBOOKS.md`, `ANALYSIS_NOTES.md` |
| 8 | `python scripts/83_audit_response.py` | The response to the audit and to the re-audit (`audit_response_*.csv`, `reaudit_response_*.csv`, `verification/AUDIT_RESPONSE_*.md`) |
| 9 | `python scripts/57_sync_workbook_sheets.py` | Rewrites the main workbook's sheets from the CSVs |
| 10 | `python scripts/80_check_source_charts.py` | Source-label check: the Chile chart is read from the PDF's coordinates and compared with the panel |
| 11 | `python scripts/build_core.py`, `build_pages.py`, `build_evidence.py` | The 728 pages, both languages (364 each) |
| 12 | `python scripts/build_pdf_extracts.py` | The PDF extracts (needs Windows and Chrome; about 8 minutes) |
| 13 | `python scripts/28_checksums.py`, `29_website_manifest.py`, `27_validate_site.py`, `validate_bilingual.py`, `77_update_readme.py`, then `28_checksums.py` again | Checksums, manifest, validators, README and CITATION numbers |
| 14 | after committing: `python scripts/78_verify_checksums.py` | Compares the manifest with what git stored |

Every step is idempotent. `45_build_source_mirrors.py` creates the `MIRROR__` renderings of newly archived files
(it, like every render through `ext_lib.chrome_render`, deletes link targets that point at the local disk, and
`86_scrub_pdf_local_links.py` checks every PDF of the archive for them, raw and inside compressed streams);
`41_link_sweep.py` re-tests every external URL (`--retry-only` re-tests just the failures with curl).

## 4. Re-collecting the sources (needs the network)

`87_collect_census_non_citizens.py` re-reads the archived ABS workbook and pages (with `--fetch` it downloads them).
`89_archive_survey_documents.py <folder>` copies the ISSP 2021 documentation quoted in `data/ANALYSIS_NOTES.md` into
`evidence/survey/` and renders the pages quoted; GESIS refuses automated downloads, so it takes the authors' copies.

`90_collect_unemployment.py` re-reads the archived unemployment files (ILO SDMX response and metadata, World Bank
response and metadata, the DGBAS workbook and yearbook) and rewrites its staging file and
`data/unemployment_source_comparison.csv` without the network; with `--fetch` it downloads them again (change the date
constant first, as for 84) and renders the mirrors and the World Bank's indicator page. The ILOSTAT web pages answer
automated requests with a bot check and the DGBAS site blocks headless browsers, so neither is captured live: the ILO's
dataset description and status codes come from its SDMX API, and the DGBAS page is rendered from the copy retrieved.

`92_collect_vdem.py` re-reads the archived V-Dem files (the V-Dem Institute's R data file and codebook entry at the
v16 release commit of its `vdemdata` package, the commit record and GitHub's size and hash of the files, the V-Dem
Codebook v16, Our World in Data's copy) and rewrites its staging file and `data/vdem_source_comparison.csv` without the
network; with `--fetch` it downloads them again (change the date constant in `scripts/vdem_texts.py` first) and renders
the mirrors, codebook pages and publisher pages. It needs R (`Rscript`, base R only) to read the R data file, through
`scripts/92_decode_vdem.R`; the rebuild in section 3 does not, because the staging file is committed. The download on
v-dem.net asks for an e-mail address and consent to a privacy policy, so the same dataset is taken from the institute's
GitHub package, pinned to the release commit.

`94_collect_gini.py` re-reads the archived Gini files (the World Bank WDI response and indicator metadata, the PIP
survey table and citation of the pinned PIP version, the OECD IDD response for New Zealand, the OECD dataflow and the
World Bank's PIP methodology chapter on income and consumption) and rewrites its staging file,
`data/gini_source_comparison.csv` and `data/gini_income_consumption_pairs.csv` without the network
(`--fetch-methodology` downloads only the methodology chapter); with `--fetch` it downloads them
again (change the date constant in `scripts/gini_texts.py` first, and the PIP version if a newer one is wanted) and
renders the mirrors and publisher pages. The OECD's own site answers a headless browser with a bot check, so its page
is captured from the OECD Data Explorer instead.

`84_collect_health_expenditure.py` re-reads the archived health-expenditure files and rewrites its staging file and
`data/health_expenditure_wb_vs_who.csv` without the network; with `--fetch` it downloads them again under new dated names
only if the date constant in the script is changed first (otherwise it overwrites the 2026-10-17 files), and renders the
mirrors and publisher pages.

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

On 2026-10-07 steps 1-11 of section 3 (everything except the Chrome render of the PDF extracts) were run in a fresh
`git clone` of the commit that contains this file, placed in an otherwise empty folder: no sibling folder, no audit folder,
no local inputs. Every tracked file came out identical, including `data/current_panel_verification.csv` with all 3,365 audit
results. The two `.xlsx` files differ in their zip container (it embeds a timestamp) but not in a single cell: they were
compared sheet by sheet. Not repeated in that test: the PDF extract render (step 12), the link sweep, and the network
collectors of section 4.

On 2026-10-17, when step 2a was added for the health-expenditure variable, steps 1-14 were run in order in a working
clone of the previous commit (a full clone, not the empty-folder test above). Steps 1 and 2 reproduced the committed panel
exactly; step 2a appended its ten columns with every other cell byte-identical; every derived table, workbook sheet and
country file changed only by the new variable's rows; the validators reported 0 errors. The PDF extracts were re-rendered,
because every country's "last amended" date changed.

On 2026-10-21, when step 2c was added for the unemployment rate, steps 1-2c were run in order in the working clone:
the panel they produced was byte-identical to the one step 2c had written, step 2c appended its ten columns with every
other column identical as text, and the analysis extract kept every earlier column unchanged. Steps 3-13 followed; the
validators reported 0 errors on 568 pages. The PDF extracts were re-rendered (every country's "last amended" date
changed, and the extracts now list the raw API files they rest on).

On 2026-10-26, when step 2d was added for the V-Dem liberal democracy index, steps 1-2d were run in order in the
working clone: the panel they produced was byte-identical to the one step 2d had written, and after steps 3 and 4 every
tracked file was identical to its state before the test. Steps 3-13 had been run before it; the validators reported 0
errors on 648 pages (324 per language). The PDF extracts were re-rendered (every country's "last amended" date changed).

On 2026-10-29, when step 2e was added for the Gini index, steps 1-2e were run in order in the working clone: the panel
they produced was byte-identical to the one step 2e had written, and after steps 3 and 4 every file of the working tree
was identical to its state before the test. The validators reported 0 errors on 728 pages (364 per language). The PDF
extracts were re-rendered.

An earlier test of this kind, run in a folder next to the audit's working folders, passed without showing that step 7 depended
on them: in an isolated clone it lost 3,328 of the 3,365 audit results (re-audit finding R01). Those result tables are now
committed in `data/audit_inputs/`. See `verification/AUDIT_RESPONSE_2026-10-07.md`, findings F21 and R01.
