# The two final workbooks in this folder

This folder holds two compiled workbooks. They come from **two separate compilation runs** and are not
interchangeable. **Use the first one.** This note was rewritten on 2026-10-07 for the 2001-2022 release; the
first-release figures it used to quote are given below as history and dated.

---

## 1. `FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx` - the current analysis workbook

**This is the workbook the website documents.** The file name still says 2010-2022 because it was published
under that name and links to it must keep working; **the data inside run 2001-2022** (880 rows, 40 countries).

Sheets: `README`, `Revision_history`, `Audit_changes`, `Panel_final`, `Data_quality`, `Corrections_applied`,
`Known_issues`, `Verification_log`, `Source_register`, `Irregular_estimates_all`, `Codebook`, `Deleted_values`.

Current figures (computed from the data files on 2026-10-07):

- Grades over the six headline variables: **A 2,323, B 142, C 13, D 0** (2,478 values). The seven
  Taiwan absconded-worker values are also displayed and are all grade B: with them, 2,485 values, A 2,323,
  B 149, C 13. Grades say where a value was read from, not how precise or comparable it is.
- 67 value corrections and 2 deletions are itemised in `Corrections_applied` and `Deleted_values`.
- Every change since first publication is dated in `Revision_history`; every cell changed by the audit of
  2026-10-07 is in `Audit_changes`.

What the verification does and does not show. The raw source payloads and documents are archived under
`evidence/`, and every value links to its evidence page. The **2,737 rows of `Verification_log` are comparison
records of the first release (2,454 as received, 283 after correction)**, not a count of unique current
observations; the per-observation table of the current panel is `data/current_panel_verification.csv`. An evidence
page that agrees with the panel shows only that the panel was reproduced: the audit of 2026-10-07 found that
agreement of this kind did not detect a chart read under the wrong years (Chile) or a previous-residence figure used as
a birthplace count (India), both now corrected. See `verification/AUDIT_RESPONSE_2026-10-07.md`.

Reproducibility: the supported way to rebuild this release is `REBUILD.md`. The early first-release builders
cannot be re-run safely; they would undo later corrections.

### First-release figures, kept as history (2026-08-17 / 08-18)

2,454 values checked as received, 2,415 exact, 39 discrepancies, 49 corrections, grades A 1,564 / B 11 / C 111 / D 6
as first compiled, and a sheet list without `Revision_history`, `Audit_changes` and `Deleted_values`. None of these
describes the current release.

---

## 2. `migration_population_panel_40countries_2010-2022_final.xlsx` - a historical compilation, not a current file

**A separately produced summary workbook, kept for provenance only. Do not use it as an analysis file.** It was
compiled from the first-release inputs, covers 2010-2022 only, and has not been updated.

- Its numbers describe its own run: its `Verification` sheet reports 203 source-URL rows, 192 of 203 snapshots and
  750 of 750 Eurostat/OECD values matched. The corresponding figures for this archive are 171 distinct source
  URLs in the register and 2,737 value comparisons. Neither set is wrong; they are different runs.
- Its `Source Audit` and `Folder Index` sheets point to a folder layout (`country_sources\...`, `sources\001_...`)
  that does not exist here; the evidence lives under `evidence/countries/<ISO3>/`.
- It differs from the current panel in **25 of 1,696 compared primary values** (corrected, rejected,
  reclassified, superseded or deleted input values). `data/secondary_workbook_differences.csv` holds **31
  disposition records**: those 25 present differences plus 6 first-release omissions that have since
  been added to the panel and now agree. The two numbers answer different questions and are not interchangeable.

Its substantive conclusions agree with this archive's: population is sound as a denominator, the foreign-national
stock is the variable closest to the survey question, and the irregular-migration measures are too sparse and too
heterogeneous to carry a cross-national regression.

---

## Which to use

For the manuscript and for any claim a reviewer might check, use
**`FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx`** or, for analysis, the cleaned extract
`CLEAN_country_year_panel_2010-2022.xlsx` built from it. The original, unmodified input workbooks are preserved in
`data/original_inputs/` so that every correction can be checked against what was supplied.
