# The two final workbooks in this folder

This folder contains two compiled workbooks. They were produced by **two separate compilation
runs** and they do not have the same contents. Please read this note before citing either.

---

## 1. `FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx`

**This is the workbook the website documents.** Every figure quoted anywhere on this site —
2,454 values checked, 2,415 exact, 39 discrepancies, 49 corrections, grades A 1,564 / B 11 /
C 111 / D 6 — refers to this file and to the evidence held in `evidence/`.

Sheets: `README`, `Panel_final`, `Data_quality`, `Corrections_applied`, `Known_issues`,
`Verification_log`, `Source_register`, `Irregular_estimates_all`, `Codebook`.

Its verification chain is fully reproducible from this repository: the raw source payloads are in
`evidence/api/` and `evidence/countries/`, the value-by-value comparison is in
`data/verification_log.csv`, and the scripts that produced all of it are in `scripts/`.

---

## 2. `migration_population_panel_40countries_2010-2022_final.xlsx`

**An independently produced summary workbook, included for completeness.** It extends the
original input workbook with four additional sheets: `Final Summary`, `Verification`,
`Source Audit` and `Folder Index`.

Two things to be aware of:

- **Its counts describe its own run, not this archive.** Its `Verification` sheet reports 203
  source-URL rows, 192 of 203 snapshots downloaded, and 750 of 750 Eurostat/OECD values matched.
  The corresponding figures for this archive are 160 distinct source URLs, 87 of 89 document
  sources retrieved, and 2,454 values checked. Neither set is wrong; they are different runs with
  different scopes and different de-duplication rules.
- **Its file paths refer to a different folder layout.** The `Source Audit` and `Folder Index`
  sheets point to `country_sources\...` and `sources\001_...`. Those paths do not exist in this
  repository, where the equivalent evidence lives under `evidence/countries/<ISO3>/`.

Its substantive conclusions agree with this archive's: population is sound as a denominator,
foreign-national stock is the variable closest to the survey question, and the irregular-migration
measures are too sparse and too method-heterogeneous to carry a cross-national regression.

---

## Which to use

For the manuscript and for any claim a reviewer might check, use
**`FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx`**. It is the file this website is
built from and the only one whose every value can be traced to a source file held here.

The original, unmodified input workbooks are preserved in `data/original_inputs/` so that every
correction can be checked against what was supplied.
