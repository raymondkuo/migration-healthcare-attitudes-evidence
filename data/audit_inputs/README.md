# Audit inputs of the build

Result tables written by two independent audits. They are inputs of `scripts/82_audit_documents.py`, which uses them
to fill the check method (`how_checked`) and the audit columns of `data/current_panel_verification.csv`, one row per
current observation.

**The re-audit of 7 October 2026** (audited commit `30d6cb1`) fills the column `audit_2026_10_07`:

| File | Rows | What it records |
|---|---:|---|
| `source_value_checks.csv` | 3,213 | Observations the audit decoded itself from an archived machine-readable source (`family`: Eurostat, World Bank, UN WPP, OECD, Taiwan MOI, Korea MOJ, ISMU), with the source file, the decoded value, the publisher's flag and the difference from the panel. All are `EXACT`. |
| `document_value_review.csv` | 152 | Observations that rest on an archived document or a derivation: the review status, the basis (page, table, series read), and the hashes of the source files read. |

Together they cover the **3,365** observations of that release (880 population, 880 UN WPP population and 1,605
migration values, counting the seven Taiwan absconded-worker values).

**The health-expenditure audit of 17 October 2026** (audited commit `be71262`) fills the column
`health_audit_2026_10_17`; for these rows `audit_2026_10_07` says that the variable was added after that audit:

| File | Rows | What it records |
|---|---:|---|
| `health_wb_who_checks_2026-10-17.csv` | 858 | `health_expenditure_pct_gdp` for the 39 countries the World Bank covers: the panel value, the staged value, the World Bank value and the WHO GHO value, compared digit for digit (all `True`). |
| `health_taiwan_checks_2026-10-17.csv` | 22 | Taiwan: the panel value, the official MOHW workbook value with its cell (sheet 表1), the published report's Table 1 value, CHE and GDP, and the percentage recomputed from them (all `True`). |

With them the audits cover 4,245 current observations; with the census value (2026-10-18) and the 880 unemployment
rates (2026-10-21) added after them the ledger has 5,126 rows. Every source path is relative to the archive root.

**These files are not produced by this archive's pipeline.** They are the audits' own record and are committed so
that a clean clone reproduces the ledger. Keep them as they are: if an observation is added to the panel, an audit has
to be extended, and `82_audit_documents.py` stops with a message naming the first uncovered observation rather than
writing "not in the audited revision". It also stops if a health-expenditure value in the panel differs, digit for
digit, from the value the health audit recorded. The exceptions are observations added after both audits and named
in the script (`POST_AUDIT`): Australia's 2021 census count of non-citizens (`non_citizens_census`, added 2026-10-18)
and the unemployment rate of every country and year (`unemployment_rate`, added 2026-10-21), whose ledger rows say
that no independent audit covered them and how the archive itself checked them. Where a later correction changed a cell
(`data/audit_changes_2026-10-07.csv`), the ledger shows that change first and the audit result after it; the audit's
own status in these files is left as it was written.
