# Response to `AUDIT_report_site_vs_VERIFIED.md`

Every issue the audit raised was re-tested independently on 2026-08-17. This records what was
confirmed, what was not, and what was done about it.

## Verdict summary

| Audit claim | Verified? | Verdict |
|---|---|---|
| 4,832 displayed values match the workbook exactly, 0 mismatches | yes | **Confirmed.** No action needed. |
| 1 × HTTP 400 — Eurostat URL contains a literal `...` | yes | **Real defect, mine.** Fixed. |
| 12 × HTTP 404 — OECD `DSD_MIG*` wildcard endpoints | yes | **Real defect, mine.** Fixed. |
| 1 × HTTP 404 — `population.un.org/wpp/downloads` | yes | **Real defect, mine.** Fixed. |
| 15 × HTTP 429 — OECD SDMX JSON | no | **Transient rate-limiting, not a defect.** On retest with 2 s spacing, 13/13 real endpoints returned HTTP 200 with byte counts matching the archives exactly. |
| 6 × HTTP 403 | yes | **Publisher-side blocking, already disclosed.** Not a defect. |
| 2 × unreachable | yes | **Host down / link rot, already disclosed.** Not a defect. |
| 2 × HTTP 404 (nisshinkyo, sem.admin.ch) | yes | **Link rot, already disclosed.** Not a defect. |
| Grade headline 1,699 vs 1,692 | yes | **Real defect, mine.** Fixed. |
| Headline 76/78 vs workbook 87/89 | yes | **Real inconsistency, mine.** Fixed. |
| `Source_register` 102 differing cells | yes | **Workbook sheet was stale.** Fixed. |
| Root and site workbooks not byte-identical | yes | **Root copy was stale.** Fixed. |

## Detail on the three URL defects

These were defects in the *published URL strings*, not in the data. In every case the archived
payload was already correct — proven by byte-for-byte agreement with the corrected live query:

| Item | Broken URL published | Live result | Corrected URL | Live result | Archive size |
|---|---|---|---|---|---|
| Eurostat CH/PT/SE 2010–2023 | `…/migr_eipre?...&geo=CH&geo=PT&geo=SE&…` | 400 | full query with all filter parameters | 200, 3,861 B | 3,861 B ✔ |
| OECD (13 series) | `…,DSD_MIG*/AUS.W.A.B14…` | 404 | `…,DSD_MIG_F@DF_MIG_POPF,1.0/AUS.W.A.B14…` | 200, 7,107 B | 7,107 B ✔ |
| UN WPP publisher page | `population.un.org/wpp/downloads` | 404 | `population.un.org/wpp/` | 200 | n/a |

The `...` and the `DSD_MIG*` wildcard were shorthand written into the snapshot index by hand. They
were never the strings actually used to fetch the data — the real queries are recorded in the
source workbook's audit trail, and it is those that the corrected index now publishes.

## The 429 claim

The audit tested the OECD endpoints in parallel with 6 workers and recorded HTTP 429. Re-tested
sequentially with a 2-second gap, all 13 returned HTTP 200:

```
AUS_B14 200 7107 B    CHL_B14 200 6796 B    CHL_B15 200 6614 B    ISR_B14 200 7104 B
JPN_B15 200 7218 B    KOR_B15 200 7218 B    MEX_B14 200 6361 B    MEX_B15 200 7205 B
NZL_B14 200 5926 B    TUR_B14 200 6517 B    TUR_B15 200 7215 B    USA_B14 200 7131 B
USA_B15 200 7258 B
```

Each byte count equals the corresponding archived file. This is a rate limit on the auditor's
request pattern, not a broken link.

## The blocked and dead URLs

Re-tested and confirmed exactly as the audit found — and exactly as the site already documents:

- 403: sagepub, mexico.iom.int, psa.gov.ph, gov.il, ismu.org ×2
- unreachable: press.police.ac.kr, cinformi.it
- 404: nisshinkyo.org, sem.admin.ch

All ten already appear in `Known_issues`, on the Sources page under "Sources that could not be
archived", and in the per-source `outcome`/`note` fields as `RECOVERED`, `RECOVERED_SCREENSHOT`,
`SUBSTITUTED` or `NOT_RETRIEVED`. Each has a local mirror or a documented substitute, except the
two named as unretrievable, whose six dependent values carry grade D. No change was warranted.

## Where the audit's own numbers need care

The audit counted 189 unique URLs including both the broken wildcard form *and* the real form of
the same 13 OECD endpoints, so those series are represented twice in its failure totals — once
under 404 and once under 429. After the fix there is one correct URL per series.

Its "87/89 document sources" figure comes from the workbook's older README sheet. The site's
"76 of 78" counts distinct country–source citations, which is the definition the site states
explicitly. Both described the same 2 unretrievable sources. The workbook sheet has now been
brought into line with the site so only one definition appears anywhere.

---

## Post-fix verification (re-run after all corrections)

A fresh, independent live sweep was run over **every** external URL the site publishes — harvested
from the six data tables *and* from the `href` of all 202 generated HTML pages, tested sequentially
with 1.2 s spacing and one retry on HTTP 429:

| Result | Count |
|---|---:|
| HTTP 200 | 166 |
| Non-200, and already documented on the site as a publisher block or link rot | 10 |
| **Undocumented broken URLs** | **0** |

176 distinct URLs. The audit reported 189; the difference is exactly the 13 OECD series that
appeared twice in its list — once as the broken wildcard form and once as the working form.
189 − 13 = 176. After the fix there is one correct URL per series.

Full results: `verification/link_sweep.csv`.

### Fixes applied

| # | Defect | Fix |
|---|---|---|
| 1 | Eurostat CH/PT/SE query URL contained a literal `...` | Replaced with the full parameterised query; verified HTTP 200, 3,861 B, byte-identical to the archive |
| 2 | 13 OECD query URLs used a `DSD_MIG*` wildcard | Replaced with the real dataflow IDs recovered from the source workbook's audit trail; all 13 verified HTTP 200 with byte counts matching their archives |
| 3 | UN WPP publisher page pointed at a 404 path | Repointed to `https://population.un.org/wpp/` (HTTP 200) |
| 4 | README grade headline said 1,699 but its breakdown summed to 1,692 | Breakdown corrected to A 1,564 · B 11 · **C 118** · D 6 = 1,699, and the site's grade table now counts all seven displayed variables so page and README agree |
| 5 | Workbook README sheet said 89/87 document sources; site said 78/76 | Workbook sheet reworded to the site's definition: 78 distinct country–source citations across 72 URLs, 76 archived, 2 not retrievable |
| 6 | Workbook `Source_register` sheet was stale by 102 cells | Sheet refreshed from the live register; the CSV is now re-exported from the workbook so the two cannot drift apart again |
| 7 | Root and site workbooks were not byte-identical | Root copy replaced with the corrected workbook; both now hash identically |

The generators were fixed too, not just their output, so a future rebuild cannot reintroduce the
placeholders: `20_site_scaffold.py` now recovers each OECD query URL from the workbook audit trail
instead of reconstructing it, and `33_oecd_summary_snapshot.py` prints the two real dataflow IDs
rather than a wildcard pattern.

### Final state

| Check | English archive | Bilingual archive |
|---|---:|---:|
| Site pages | 202 | 404 |
| Internal links, broken | 7,364 / 0 | 15,540 / 0 |
| Panel cells linked to evidence | 1,699 / 0 unlinked | 3,398 / 0 unlinked |
| External URLs, undocumented failures | 176 / 0 | same data tables |
| Files, size | 784, 227.0 MB | 957, 231.2 MB |

Nothing was committed or pushed.
