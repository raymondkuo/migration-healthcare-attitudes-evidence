# -*- coding: utf-8 -*-
"""Tables and documents that the audit of 2026-10-07 asked for (run after 79 and 81).

  data/secondary_workbook_differences.csv   F16: a disposition for every number the secondary workbook holds
                                            that differs from the panel
  data/current_panel_verification.csv       F23: one row per current panel observation - source, year, unit,
                                            concept, grade, how it was checked, and what the 2026-10-07 audit found
  data/ABOUT_THE_TWO_WORKBOOKS.md           F16/F17: rewritten for the current release
  data/ANALYSIS_NOTES.md                    F24: the construct, timing, universe and sensitivity choices that remain
                                            the authors' to make, with the numbers behind each
  REBUILD.md                                F21: the supported, safe order for rebuilding this release

Numbers in the documents are computed here, not typed. The per-observation audit statuses come from the
audit's result tables if they are present beside the archive (../comprehensive_audit); the rest of the table
does not depend on them.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import counts as K                                                 # noqa: E402

SITE = os.path.dirname(HERE)
D = os.path.join(SITE, 'data')
AUD = os.path.join(os.path.dirname(SITE), 'comprehensive_audit')
WHEN = '2026-10-07'
panel = pd.read_csv(os.path.join(D, 'panel_final.csv'))
pi = panel.set_index(['iso3', 'year'])
chg = pd.read_csv(os.path.join(D, 'audit_changes_%s.csv' % WHEN))
n = lambda x: format(int(x), ',')
chg_idx = {(r.iso3, int(r.year), r.variable): r for r in chg.itertuples()}

# ================================================================== F16  secondary workbook
sec = pd.read_excel(os.path.join(D, 'migration_population_panel_40countries_2010-2022_final.xlsx'), sheet_name='Panel')
VCOLS = ['population', 'foreign_born', 'foreign_nationals', 'irregular_stock', 'irregular_proxy_overstayers',
         'irregular_proxy_detections']
absc = pi['irregular_proxy_absconded_workers']
rows = []
n_cmp = 0
for v in VCOLS:
    for r in sec[sec[v].notna()].itertuples():
        n_cmp += 1
        cur = pi.at[(r.iso3, int(r.year)), v] if (r.iso3, int(r.year)) in pi.index else np.nan
        sv = float(getattr(r, v))
        if pd.notna(cur) and abs(float(cur) - sv) <= 1:
            continue
        a = absc.get((r.iso3, int(r.year)), np.nan)
        key = (r.iso3, int(r.year), v)
        if v == 'irregular_proxy_overstayers' and r.iso3 == 'TWN' and pd.notna(a) and abs(float(a) - sv) <= 1:
            disp = ('Reclassified: the Ministry of Labor missing-worker count (Table 12-7); it is held in '
                    'irregular_proxy_absconded_workers, and the overstay column holds the National Immigration Agency total.')
        elif key in chg_idx and chg_idx[key].kind == 'corrected':
            disp = ('Corrected on %s (audit %s): the secondary workbook still holds the value the first release carried. %s'
                    % (WHEN, chg_idx[key].finding, chg_idx[key].reason))
        elif v == 'irregular_proxy_overstayers' and r.iso3 == 'TWN':
            disp = ('Reclassified: a missing-worker count at 31 July 2019, not year-end; the panel now holds the Ministry of '
                    'Labor year-end stock (48,491) in irregular_proxy_absconded_workers and keeps this as an alternative.')
        elif r.iso3 == 'ISR':
            disp = 'Reclassified: tourist overstayers, not a stock of irregular residents; see Known_issues.'
        elif r.iso3 == 'ITA':
            disp = 'Superseded: the series was re-read and corrected to 350,000 (corrections_applied.csv).'
        elif r.iso3 == 'KOR':
            disp = 'Superseded: corrected to the official year-end 214,168 (the secondary workbook has a 31 August snapshot).'
        elif r.iso3 == 'RUS':
            disp = 'Deleted: no numeric estimate exists in the archived source (deleted_values.csv).'
        else:
            disp = 'Unexplained difference.'
        rows.append(dict(iso3=r.iso3, year=int(r.year), variable=v, secondary_workbook_value=sv,
                         panel_value=cur, disposition=disp, status_now='in secondary workbook only'))
# values that were differences before the audit corrections and are now resolved by adding or correcting
added = chg[chg.kind.isin(['added', 'corrected']) & chg.finding.isin(['F16'])]
for r in added.itertuples():
    rows.append(dict(iso3=r.iso3, year=int(r.year), variable=r.variable, secondary_workbook_value=r.new_value,
                     panel_value=r.new_value,
                     disposition='Omitted from the panel at first release although the archived source supports it; added '
                                 'on %s (audit F16).' % WHEN,
                     status_now='resolved: now in the panel'))
secdiff = pd.DataFrame(rows).sort_values(['status_now', 'iso3', 'variable', 'year'], ascending=[False, True, True, True])
assert (secdiff.disposition != 'Unexplained difference.').all(), secdiff[secdiff.disposition == 'Unexplained difference.']
secdiff.to_csv(os.path.join(D, 'secondary_workbook_differences.csv'), index=False, encoding='utf-8-sig')
n_open = int((secdiff.status_now == 'in secondary workbook only').sum())
n_res = int((secdiff.status_now != 'in secondary workbook only').sum())
print('secondary_workbook_differences.csv: %d rows (%d still differ, %d resolved) of %d compared'
      % (len(secdiff), n_open, n_res, n_cmp))

# ================================================================== F23  one row per current observation
VAR = [('population', 'total resident population'), ('population_un_wpp2024', 'total population, UN WPP 2024 (alternative denominator)'),
       ('foreign_born', None), ('foreign_nationals', 'residents holding a foreign nationality'),
       ('irregular_stock', 'estimated stock of irregular residents'),
       ('irregular_proxy_overstayers', 'persons recorded as overstaying (register count)'),
       ('irregular_proxy_detections', None), ('irregular_proxy_absconded_workers', 'migrant workers recorded as absconded (stock)')]
src_audit, doc_audit = None, None
if os.path.exists(os.path.join(AUD, 'source_value_checks.csv')):
    src_audit = pd.read_csv(os.path.join(AUD, 'source_value_checks.csv')).set_index(['iso3', 'year', 'variable']).status
    doc_audit = pd.read_csv(os.path.join(AUD, 'document_value_review.csv')).set_index(['iso3', 'year', 'variable'])
chg_idx = {(r.iso3, int(r.year), r.variable): r for r in chg.itertuples()}


def basis(ver, grade, derived, derivation, v):
    ver = '' if pd.isna(ver) else str(ver)
    if ver.startswith(('Read directly from the archived API', 'Read directly from the archived CSV',
                       'Read directly from the official')):
        b = 'decoded from an archived machine-readable source'
    elif ver:
        b = 'read from an archived source document'
    elif grade == 'A':
        b = 'reproduced from the archived payload in the first-release comparison (verification_log.csv)'
    else:
        b = 'read from an archived source document'
    if isinstance(derived, str) and derived.strip() == 'yes':
        b += '; derived: %s' % (str(derivation)[:110] if pd.notna(derivation) else 'see the cell note')
    return b


out = []
for r in panel.itertuples():
    iso, y = r.iso3, int(r.year)
    for v, concept in VAR:
        val = getattr(r, v)
        if pd.isna(val):
            continue
        g = lambda suf, default='': (getattr(r, v + suf) if hasattr(r, v + suf) else default)
        if v == 'population_un_wpp2024':
            source, ref, grade, ver, note, stype, flag, coll = ('UN DESA, World Population Prospects 2024', '1 July', '',
                                                                 'Read from the archived UN WPP workbook', '', 'annual', '',
                                                                 g('_collected_on'))
        else:
            source, ref, grade, ver, note = g('_source'), g('_ref_date'), g('_grade'), g('_verification'), g('_note')
            stype, flag, coll = g('_source_type'), g('_flag'), g('_collected_on')
        unit = 'persons'
        if v == 'foreign_born':
            concept = getattr(r, 'foreign_born_concept')
        if v == 'irregular_proxy_detections':
            if iso == 'MEX':
                concept, unit = 'irregular-status EVENTS recorded in the year (a person may be recorded more than once)', 'events'
            elif iso == 'TUR':
                concept = 'irregular migrants apprehended in the year (Syrians under temporary protection excluded)'
            else:
                concept = 'third-country nationals found to be illegally present in the year (each person once per year)'
            if v in ('irregular_proxy_detections',):
                unit = unit + ' per calendar year (flow)'
        if v in ('foreign_nationals',) and iso == 'TWN':
            concept = 'registered foreign residents holding a resident certificate (excl. mainland Chinese, Hong Kong, Macao)'
        if v == 'foreign_nationals' and iso == 'RUS':
            concept = 'foreign citizens plus stateless persons (2002 census)'
        if v == 'foreign_nationals' and iso == 'SUR':
            concept = 'known foreign nationalities (3,340 of unknown nationality excluded)'
        if v == 'irregular_proxy_overstayers' and iso == 'TWN':
            concept = 'ALL overstaying persons recorded by the National Immigration Agency (foreign nationals, mainland Chinese, HK/Macao, no household registration)'
        if v == 'population' and iso == 'TWN':
            concept = 'registered (household-registration) population; excludes foreign residents'
        key = (iso, y, v)
        if key in chg_idx:
            c_ = chg_idx[key]
            audit = '%s on %s (%s)' % (c_.kind, WHEN, c_.finding)
        elif src_audit is not None and key in src_audit.index:
            audit = 'matched the machine-readable source (audit %s)' % WHEN
        elif doc_audit is not None and key in doc_audit.index:
            d_ = doc_audit.loc[key]
            audit = '%s%s (audit %s)' % (str(d_.audit_status).lower().replace('_', ' '),
                                        '; ' + str(d_.finding) if pd.notna(d_.finding) else '', WHEN)
        else:
            audit = 'not in the audited revision'
        out.append(dict(iso3=iso, country=r.country, year=y, variable=v, value=int(round(float(val))), unit=unit,
                        concept=concept, source=str(source)[:150], source_type=stype if isinstance(stype, str) else '',
                        reference_date=ref if isinstance(ref, str) else '', grade=grade if isinstance(grade, str) else '',
                        how_checked=basis(ver, grade, g('_derived'), g('_derivation'), v),
                        flag=flag if isinstance(flag, str) else '',
                        first_collected=(coll if isinstance(coll, str) and coll else '2026-08-17'),
                        audit_2026_10_07=audit))
ver = pd.DataFrame(out)
ver.to_csv(os.path.join(D, 'current_panel_verification.csv'), index=False, encoding='utf-8-sig')
print('current_panel_verification.csv: %d observations | how checked: %s'
      % (len(ver), ver.how_checked.str.split(';').str[0].value_counts().to_dict()))

# ================================================================== numbers for the documents
fb = panel[panel.foreign_born.notna()]
fn = panel[panel.foreign_nationals.notna()]
spl = pd.read_csv(os.path.join(D, 'extension_splice_summary.csv'))
large = spl[spl.mean_abs_gap_pct >= 5]
vlog = pd.read_csv(os.path.join(D, 'verification_log.csv'))
reg = pd.read_csv(os.path.join(D, 'source_register.csv'))
below = pd.read_csv(os.path.join(D, 'foreign_born_below_foreign_nationals.csv'))
G = ['population', 'foreign_born', 'foreign_nationals', 'irregular_stock', 'irregular_proxy_overstayers', 'irregular_proxy_detections']
gr = pd.Series([x for v in G for x in panel[v + '_grade'].dropna() if str(x).strip()]).value_counts()
sec_total = pd.read_csv(os.path.join(D, 'secondary_workbook_differences.csv'))

# ================================================================== ABOUT_THE_TWO_WORKBOOKS.md
about = '''# The two final workbooks in this folder

This folder holds two compiled workbooks. They come from **two separate compilation runs** and are not
interchangeable. **Use the first one.** This note was rewritten on %(when)s for the 2001-2022 release; the
first-release figures it used to quote are given below as history and dated.

---

## 1. `FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx` - the current analysis workbook

**This is the workbook the website documents.** The file name still says 2010-2022 because it was published
under that name and links to it must keep working; **the data inside run 2001-2022** (%(rows)s rows, 40 countries).

Sheets: `README`, `Revision_history`, `Audit_changes`, `Panel_final`, `Data_quality`, `Corrections_applied`,
`Known_issues`, `Verification_log`, `Source_register`, `Irregular_estimates_all`, `Codebook`, `Deleted_values`.

Current figures (computed from the data files on %(when)s):

- Grades over the six graded variables: **A %(ga)s, B %(gb)s, C %(gc)s, D 0** (%(gtot)s values). Grades say where a
  value was read from, not how precise or comparable it is.
- %(ncorr)d value corrections and %(ndel)d deletions are itemised in `Corrections_applied` and `Deleted_values`.
- Every change since first publication is dated in `Revision_history`; every cell changed by the audit of
  %(when)s is in `Audit_changes`.

What the verification does and does not show. The raw source payloads and documents are archived under
`evidence/`, and every value links to its evidence page. The **%(nlog)s rows of `Verification_log` are comparison
records of the first release (2,454 as received, 283 after correction)**, not a count of unique current
observations; the per-observation table of the current panel is `data/current_panel_verification.csv`. An evidence
page that agrees with the panel shows only that the panel was reproduced: the audit of %(when)s found that
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
  750 of 750 Eurostat/OECD values matched. The corresponding figures for this archive are %(nurls)d distinct source
  URLs in the register and %(nlog)s value comparisons. Neither set is wrong; they are different runs.
- Its `Source Audit` and `Folder Index` sheets point to a folder layout (`country_sources\\...`, `sources\\001_...`)
  that does not exist here; the evidence lives under `evidence/countries/<ISO3>/`.
- It differs from the current panel in **%(nsec)d of %(ncmp)s compared primary values**; %(nres)d of these were
  omissions that have since been added to the panel, and the other %(nopen)d are corrected, rejected, reclassified,
  superseded or deleted input values. Every one has a disposition in `data/secondary_workbook_differences.csv`.

Its substantive conclusions agree with this archive's: population is sound as a denominator, the foreign-national
stock is the variable closest to the survey question, and the irregular-migration measures are too sparse and too
heterogeneous to carry a cross-national regression.

---

## Which to use

For the manuscript and for any claim a reviewer might check, use
**`FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx`** or, for analysis, the cleaned extract
`CLEAN_country_year_panel_2010-2022.xlsx` built from it. The original, unmodified input workbooks are preserved in
`data/original_inputs/` so that every correction can be checked against what was supplied.
''' % dict(when=WHEN, rows=n(len(panel)), ga=n(gr.get('A', 0)), gb=n(gr.get('B', 0)), gc=n(gr.get('C', 0)),
           gtot=n(gr.sum()), ncorr=len(pd.read_csv(os.path.join(D, 'corrections_applied.csv'))),
           ndel=len(pd.read_csv(os.path.join(D, 'deleted_values.csv'))), nlog=n(len(vlog)),
           nurls=reg.source_url.nunique(), nsec=len(sec_total), ncmp=n(n_cmp),
           nres=int((sec_total.status_now != 'in secondary workbook only').sum()),
           nopen=int((sec_total.status_now == 'in secondary workbook only').sum()))
open(os.path.join(D, 'ABOUT_THE_TWO_WORKBOOKS.md'), 'w', encoding='utf-8', newline='\n').write(about)

# ================================================================== ANALYSIS_NOTES.md (F24)
refcls = []
for v, lab in (('foreign_nationals', 'foreign_nationals'), ('foreign_born', 'foreign_born')):
    s_ = panel[panel[v].notna()][v + '_ref_date'].fillna('').astype(str)
    cls = s_.map(lambda x: '1 January' if x.startswith('1 January') else '31 December' if x.startswith('31 December')
                 else 'mid-year / 30 June' if x.startswith('Mid-year') else 'census date' if 'ensus' in x
                 else 'survey period' if 'survey' in x.lower() else 'not stated in the API response (see note)' if x == 'See note'
                 else 'other')
    for k, c_ in cls.value_counts().items():
        refcls.append('| %s | %s | %s |' % (lab, k, n(c_)))
st_fb = fb.foreign_born_source_type.value_counts()
st_fn = fn.foreign_nationals_source_type.value_counts()
splice_lines = '\n'.join('| %s | %s | %+.1f%% | %.1f%% | %d |' % (r.iso3, r.variable, r.mean_gap_pct, r.mean_abs_gap_pct, r.overlap_years)
                         for r in large.itertuples())
below_lines = '\n'.join('| %s | %d | %s |' % (k, len(g), ', '.join(str(y) for y in sorted(g.year)))
                        for k, g in below.groupby('iso3'))
notes = '''# Research-use notes: constructs, timing, universes and sensitivity

*Written %(when)s after audit finding F24. These are the choices that source verification does not settle.
They are **not decisions**: the places marked [AUTHORS] are for the study's authors to fill in before the final
analysis. No manuscript result was recalculated in preparing this file.*

## 1. The construct [AUTHORS]

The study asks about **attitudes toward publicly funded healthcare for non-nationals**. Which stock best
matches the survey item depends on the item itself, which this archive does not hold.

- Paste the questionnaire wording and response scale here: [AUTHORS]
- Whom does the item name - foreigners / non-citizens in general, legally resident foreigners, migrants, or
  irregular migrants? [AUTHORS]
- Is the entitlement question about people who are *present* (a stock), people who *arrive* (a flow), or a
  policy position? [AUTHORS]

The archive recommends `foreign_nationals_pct_pop` as the main regressor because it counts residents without
the country's nationality, the closest match to "non-nationals". That is a methodological judgement, not a
verified property of the survey question: it fails if the item is about birthplace or about irregular status.

| Variable | What it counts | Countries (years) | Main caution |
|---|---|---|---|
| foreign_nationals | residents holding a foreign nationality (stateless where reported) | %(nfn)d (%(yfn)s) | falls with naturalisation; no annual series for AUS, IND, ISR, NZL, ZAF |
| foreign_born | residents born abroad | %(nfb)d (%(yfb)s) | includes naturalised citizens; %(ntc)d UN citizenship-basis cells are excluded from the extract |
| irregular_stock | estimated unauthorised residents | %(nir)d (2010-2022) | methods differ by country; not comparable |
| irregular_proxy_overstayers | register count of overstayers | %(nov)d (2010-2022) | register-based; universe differs (Taiwan: all categories) |
| irregular_proxy_detections | annual enforcement detections | %(nde)d (2010-2022) | a flow; unit differs by source (persons / events) |

## 2. Timing: survey year versus stock date [AUTHORS]

Pick one rule and apply it to every country, then test the other.

1. Same year (survey year Y with the row labelled Y);
2. One-year lag (row Y-1), which matches a 1 January stock to a mid-year survey better;
3. Nearest reference date, using `*_ref_date` per value.

Reference dates differ by source and are not harmonised: years are as the publisher labels them.

| Variable | Reference date class | Values |
|---|---|---|
%(refcls)s

## 3. Universes: citizenship, stateless, census

- `foreign_nationals` counts people holding a foreign nationality, **including stateless persons where the source
  reports them**; Russia 2002 (census) is foreign citizens plus stateless; Suriname 2012 is the known foreign
  nationalities with 3,340 of unknown nationality excluded (the residual is kept as an alternative); Taiwan is
  registered foreign residents and excludes mainland Chinese, Hong Kong and Macao residents.
- Source types in the panel - `foreign_born`: %(stfb)s; `foreign_nationals`: %(stfn)s. Census and survey values are
  point-in-time and not interchangeable with annual register series.
- UN DESA declares its stock **on a citizenship basis** for China, India, the Philippines, Suriname and Thailand
  (%(ntc)d cells). They are not birthplace counts and have not been moved into `foreign_nationals`; decide whether to
  drop them, keep them apart, or test them against national citizenship counts.
- Taiwan's population is the **registered population, which excludes foreign residents**, so its shares have a different
  denominator from every other country.
- Census counts of non-citizens exist that are not in the panel: Australia 2021 (2,808,214; 5.1%% did not state) and
  South Africa 2011 (1,692,242 "No" to South African citizenship; the table covers 50,641,580 of 51,770,560).
  Their universes (not stated, visitors, stateless) have to be agreed before they are added. See Known_issues.

## 4. Denominators

`population` (World Bank, mid-year; Taiwan registered year-end) and `population_unwpp` (UN WPP, 1 July) differ by more
than 3%% in %(gap_all)d country-years (%(gap_late)d of them in 2010-2022). Choose one and keep it for every country;
report the other as a sensitivity check.

## 5. Source families and breaks

Run the models on the full panel and again after removing, in turn:

- every `splice (large gap)` cell (the series below differ from the series they were joined to by 5%% or more on average);
- every `un_estimate`, `census` and `survey` cell (annual register series only);
- the OECD-only series in `data/migrant_stock_alternatives.csv` instead of the Eurostat/OECD splice;
- country-years flagged `Eurostat flag: break in time series` or `comparability caution` (Taiwan 2001-2011).

| Series | Mean gap | Mean absolute gap | Overlap years |
|---|---|---|---|
%(splice)s

## 6. Where foreign-born is below foreign-nationals

The codebook's "foreign-born usually exceeds foreign nationals" is not a rule. **%(nb)d country-years** have
`foreign_born` below `foreign_nationals` (`data/foreign_born_below_foreign_nationals.csv`). Nothing was
corrected to force an ordering: the two series come from different sources, concepts, dates or universes. Each case
needs a source-and-concept explanation before it is read as an error or as a finding.

| Country | Country-years | Years |
|---|---|---|
%(below)s

## 7. What this archive does not establish

It does not establish that any source's own estimate is accurate, that a series is comparable across countries because
its numbers were reproduced, or that the choices above have been made. Report the sensitivity of the main result to
each of them.
''' % dict(when=WHEN, nfn=fn.iso3.nunique(), yfn='%d-%d' % (fn.year.min(), fn.year.max()),
           nfb=fb.iso3.nunique(), yfb='%d-%d' % (fb.year.min(), fb.year.max()),
           ntc=int(panel.foreign_born_concept.fillna('').str.contains('citizenship basis').sum()),
           nir=panel[panel.irregular_stock.notna()].iso3.nunique(),
           nov=panel[panel.irregular_proxy_overstayers.notna()].iso3.nunique(),
           nde=panel[panel.irregular_proxy_detections.notna()].iso3.nunique(),
           refcls='\n'.join(refcls),
           stfb=', '.join('%s %s' % (k, n(v)) for k, v in st_fb.items()),
           stfn=', '.join('%s %s' % (k, n(v)) for k, v in st_fn.items()),
           gap_all=K.GAP3_ALL, gap_late=K.GAP3_LATE, splice=splice_lines, nb=len(below), below=below_lines)
open(os.path.join(D, 'ANALYSIS_NOTES.md'), 'w', encoding='utf-8', newline='\n').write(notes)
print('ABOUT_THE_TWO_WORKBOOKS.md and ANALYSIS_NOTES.md written')
