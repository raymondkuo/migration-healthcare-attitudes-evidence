# Audit inputs of the build

Two tables written by the **independent re-audit of 7 October 2026** (audited commit `30d6cb1`). They are inputs of
`scripts/82_audit_documents.py`, which uses them to fill two columns of `data/current_panel_verification.csv`: the
check method (`how_checked`) and the audit result (`audit_2026_10_07`) of every current observation.

| File | Rows | What it records |
|---|---:|---|
| `source_value_checks.csv` | 3,213 | Observations the audit decoded itself from an archived machine-readable source (`family`: Eurostat, World Bank, UN WPP, OECD, Taiwan MOI, Korea MOJ, ISMU), with the source file, the decoded value, the publisher's flag and the difference from the panel. All are `EXACT`. |
| `document_value_review.csv` | 152 | Observations that rest on an archived document or a derivation: the review status, the basis (page, table, series read), and the hashes of the source files read. |

Together they cover all **3,365** current observations (880 population, 880 UN WPP population and 1,605 migration
values, counting the seven Taiwan absconded-worker values). Every source path is relative to the archive root.

**These files are not produced by this archive's pipeline.** They are the audit's own record and are committed so that
a clean clone reproduces the ledger. Keep them as they are: if an observation is added to the panel, the audit has to
be extended, and `82_audit_documents.py` stops with a message naming the first uncovered observation rather than
writing "not in the audited revision". Where a later correction changed a cell (`data/audit_changes_2026-10-07.csv`),
the ledger shows that change first and the audit result after it; the audit's own status in these files is left as
it was written.
