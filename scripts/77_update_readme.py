# -*- coding: utf-8 -*-
"""Refresh the numbers quoted in README.md, CITATION.cff and the VERIFICATION_REPORT notice.

The README had counts typed into it by hand (156 evidence pages, 2,454 comparisons, 1,698
graded values ...) and they went stale when the archive grew. Every count here is computed
from the data files, and the headline block is rewritten between markers so that running this
again changes nothing unless the data changed.

Run after the site has been built and validated (it reads manifest/validation_summary.json
and manifest/checksums.csv)."""
import json
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SITE = os.path.dirname(HERE)
D = os.path.join(SITE, 'data')
import counts as K                                                        # noqa: E402


def read(name):
    return pd.read_csv(os.path.join(D, name))


def n(x):
    return format(int(x), ',')


panel = read('panel_final.csv')
vlog = read('verification_log.csv')
corr = read('corrections_applied.csv')
hist = read('revision_history.csv').fillna('')
ovl = read('extension_overlap_check.csv')
spl = read('extension_splice_summary.csv')
dele = read('deleted_values.csv')
ck = pd.read_csv(os.path.join(SITE, 'manifest', 'checksums.csv'))
val = json.load(open(os.path.join(SITE, 'manifest', 'validation_summary.json'), encoding='utf-8'))
sweep = pd.read_csv(os.path.join(SITE, 'verification', 'link_sweep.csv'))

LAST = str(hist[hist.amends_data == 'yes'].date.max())
VARS = ['population', 'foreign_born', 'foreign_nationals', 'irregular_stock',
        'irregular_proxy_overstayers', 'irregular_proxy_detections']
grades = pd.Series([g for v in VARS for g in panel[v + '_grade'].dropna() if str(g).strip()]
                   ).value_counts()
gtot = int(grades.sum())
as_rec = vlog[vlog.stage == 'as_received']
n_as, n_bad = len(as_rec), int((as_rec.status != 'EXACT').sum())
n_exact = n_as - n_bad
ys = panel.year
Y0, Y1 = int(ys.min()), int(ys.max())
new = {v: int(panel[v + '_collected_on'].notna().sum())
       for v in ('population', 'population_un_wpp2024', 'foreign_born', 'foreign_nationals')}
n_large = int((spl.mean_abs_gap_pct >= 5).sum())          # the declared rule: mean ABSOLUTE gap (re-audit R03)
grades7 = pd.Series([g for v in VARS + ['irregular_proxy_absconded_workers', 'health_expenditure_pct_gdp', 'non_citizens_census',
                                         'unemployment_rate', 'vdem_libdem', 'gini_index']
                     for g in panel[v + '_grade'].dropna()
                     if str(g).strip()]).value_counts()
n_abs = int(panel.irregular_proxy_absconded_workers.notna().sum())
n_he = int(panel.health_expenditure_pct_gdp.notna().sum())
import health_texts as HT                                          # noqa: E402
_hk = HT.counts()
import unemployment_texts as UT                                    # noqa: E402
_uk = UT.counts()
import vdem_texts as VT                                            # noqa: E402
_vk = VT.counts()
import gini_texts as GT                                            # noqa: E402
_gk = GT.counts()
n_corr_aud = int((corr.corrected_on.astype(str) == '2026-10-07').sum())
pages_each = val['pages_en']
total_pages = val['pages_en'] + val['pages_zh']
n_ext = int((sweep.status != 'OK').sum())
n_bad_links = int((~sweep.status.isin(['OK', 'KNOWN'])).sum())
n_retry_ok = int(((sweep.status == 'OK') & sweep.method.astype(str).str.startswith('curl')).sum())
aud = pd.read_csv(os.path.join(D, 'audit_changes_2026-10-07.csv'))
n_re = int(aud.finding.astype(str).str.startswith('R').sum())
aud_kinds = ', '.join('%d %s' % (v, k) for k, v in aud.kind.value_counts().items())
n_cur = len(pd.read_csv(os.path.join(D, 'current_panel_verification.csv')))

# ---------------------------------------------------------------- README
fp = os.path.join(SITE, 'README.md')
s = open(fp, encoding='utf-8').read()


def sub(pattern, repl, count=1, flags=0, required=True):
    global s
    s, k = re.subn(pattern, lambda m: repl, s, count=count, flags=flags)
    assert k >= 1 or not required, 'README pattern not found: %s' % pattern[:60]


sub(r'\*\*40 countries, [0-9–-]+ · 40 國，[0-9–-]+ 年\*\*',
    '**40 countries, %d–%d · 40 國，%d–%d 年**' % (Y0, Y1, Y0, Y1))
sub(r'verified on \*\*2026-08-17\*\*\.[^\n]*\n(?:[^\n]+\n)*?\n',
    'verified on **2026-08-17**. The panel was extended back from 2010 to %d on **2026-10-07** '
    '(see *Extension* below).\n\n' % Y0)
sub(r'所有來源均於 \*\*2026-08-17\*\* 取得並完成查證。(?:面板已於[^\n]*)?',
    '所有來源均於 **2026-08-17** 取得並完成查證。面板已於 **2026-10-07** 向前延伸至 %d 年（見下方「延伸」）。' % Y0)
sub(r'\*\*[\d,]+ pages\*\* — [^\n]*',
    '**%s pages** — %d per language. Validated: %s internal links, %d broken.'
    % (n(total_pages), pages_each, n(val['internal_links_checked']), val['errors']))
sub(r'\| `evidence-pages/` \| \d+ per-country',
    '| `evidence-pages/` | %d per-country' % K.N_EVIDENCE)
sub(r'\| `verification.html` \| All [\d,]+ value comparisons[^|]*\|',
    '| `verification.html` | All %s value comparisons, the %s re-comparisons of 2026-10-07, '
    'corrections, the extension and the issues |' % (n(len(vlog)), n(ovl.cells_compared.sum())))
sub(r'\| `evidence/extracts/` \| \d+ bilingual',
    '| `evidence/extracts/` | %d bilingual' % K.N_EVIDENCE)
# the code block that held these two lines is replaced by a pointer to REBUILD.md (below), so a
# second run no longer finds them
sub(r'build_evidence\.py         # \d+ evidence', 'build_evidence.py         # %d evidence' % K.N_EVIDENCE, required=False)
sub(r'build_pdf_extracts\.py     # \d+ bilingual', 'build_pdf_extracts.py     # %d bilingual' % K.N_EVIDENCE, required=False)
sub(r'About [\d,]+ MB across ~?[\d,]+ files\. No single file exceeds \d+ MB; the largest is [^\n]*\n(?:  workbook at \d+ MB\.\n)?',
    'About %d MB across %s files. No single file exceeds %d MB; the largest is %s at %d MB.\n'
    % (round(ck.bytes.sum() / 1e6), n(len(ck)), int(ck.bytes.max() / 1e6) + 1,
       os.path.basename(ck.loc[ck.bytes.idxmax(), 'path']), round(ck.bytes.max() / 1e6)))

# rows of the file table and the re-running section
if '| `REBUILD.md`' not in s:
    s = s.replace('| `VERIFICATION_REPORT.md` | The written verification report |\n',
                  '| `VERIFICATION_REPORT.md` | The written verification report (first release; kept as written) |\n'
                  '| `REBUILD.md` | The supported order for rebuilding this release, and what must not be re-run |\n'
                  '| `verification/AUDIT_RESPONSE_2026-10-07.md` | The response to the audit of 2026-10-07, finding by finding |\n'
                  '| `data/ANALYSIS_NOTES.md` | The construct, timing, universe and sensitivity choices that are the authors\' to make |\n', 1)
s = re.sub(r'\| `AUDIT_report_site_vs_VERIFIED.md` \|[^\n]*\n', '', s)
s = re.sub(r'\| `scripts/` \|[^\n]*\n',
           '| `scripts/` | Every script used. Only the pipeline in `REBUILD.md` can be re-run safely; the first-release '
           'builders (numbered below 67) would undo later corrections |\n', s)
RERUN = ('## Re-running\n\nThe supported rebuild is in **[`REBUILD.md`](REBUILD.md)**: the order, what is pinned (commit '
         '`0d64a1c` and the archived payloads), and which first-release scripts must not be re-run because they would '
         'undo later corrections. Needs `pip install pandas openpyxl pymupdf pdfplumber pypdf`. After committing, '
         '`python scripts/78_verify_checksums.py` compares `manifest/checksums.csv` with what git stored.\n\n')
s = re.sub(r'## Re-running\n.*?(?=Translations live in)', lambda m: RERUN, s, flags=re.S)

miss = K.N_CITES - K.N_CITES_HELD
HEAD = '''<!-- headline:begin -->
## Headline results

**At first release (2026-08-17 / 08-18; the figures in this block are frozen as published in commit `0d64a1c`)**

- **%(n_as)s** values re-derived from live sources; **%(n_exact)s (%(pct).1f%%)** matched exactly.
- **%(n_bad)d** discrepancies found — all one error: the Eurostat irregular-migration detections
  series for **Switzerland, Portugal and Sweden** was offset by one year in one input workbook.
- **%(n_corr)d** corrections across %(n_ctry)d countries, each itemised with its evidence
  (`data/corrections_applied.csv`).
- **%(held)d of %(cites)d** distinct country-source document citations archived, across %(urls)d URLs%(missing)s.
- **Every retained number cites an archived source.** Whether a source was read under the right year and
  concept is a separate question, and the audit of 2026-10-07 found it was not always (below). At first
  release each of the 116 values that were not machine-verified was checked against the archived source
  document: 102 were found in it and regraded B, 13 are derived from a published range and are flagged ≈, and 1
  (Russia 2020 irregular stock) could not be traced to anything and was **deleted** — see
  `data/deleted_values.csv`.
- **Every archived source file has a viewable mirror.** Every PDF, HTML page, raw JSON/CSV API
  payload and spreadsheet carries a rendered PNG or PDF companion, so a reader can see the content
  without trusting an opaque binary.
- Korea's 2010–2015 overstayer figures, which were grade D because their only cited source was
  offline, were re-sourced to the Ministry of Justice series, and one error was found and corrected.
- **Every number in every country's Panel data table is a link.** Click a value, or the grade pill
  beside it, and you reach the evidence for that exact figure.

**Now (revised %(last)s)**

- **Audit of 2026-10-07** (issues #1–#25): all 24 findings were re-checked against the archived sources and
  confirmed; **%(n_aud)d cell changes** followed, counting the audit and the re-audit below (%(aud_kinds)s). The response is in
  `verification/AUDIT_RESPONSE_2026-10-07.md`; the dispositions of all **%(n_cur)s** current observations are in
  `data/current_panel_verification.csv`. The 2,454 / 2,737 figures above are comparison *records* of the first-release
  check, not a count of unique current observations.
- **Re-audit of 2026-10-07**, an independent re-check of commit `30d6cb1` (issues #5, #11, #12, #13, #17, #20 and #21
  reopened, #27–#30 opened): all **11** findings were confirmed and are answered in the same response file. %(n_re)d of the
  cell changes above belong to it (a detection break flag, a derived flag; no value changed).
- **%(n_corr_now)d** value corrections across %(n_ctry_now)d countries are itemised in `data/corrections_applied.csv`
  (the 49 of the first release, later amendments, and %(n_corr_aud)d from the audit of 2026-10-07), and %(n_del)d deletion%(s_del)s in
  `data/deleted_values.csv`.
- Quality grades on the %(gtot)s displayed values of the six headline variables (%(y0)d–%(y1)d): **A** %(ga)s · **B** %(gb)s · **C** %(gc)s · **D** 0.
  With the %(n_abs)d Taiwan absconded-worker values (all grade B), the %(n_he)s health-expenditure values (all grade A,
  added 2026-10-17) and Australia's 2021 census count of non-citizens (grade A, added 2026-10-18) the displayed total
  is %(gtot7)s: **A** %(ga7)s · **B** %(gb7)s · **C** %(gc)s.
  A grade says where a value was read from (A decoded from a machine-readable source, B read from an archived document,
  C the midpoint of a published range computed by the archive; a single-number estimate a source publishes is A or B);
  it does not say how precise or comparable the value is.
- Link sweep of %(sweep_date)s over **%(n_sweep)d** external URLs: %(n_ok)d reachable (%(n_retry_ok)d only on a curl retry,
  after a failed first attempt), %(n_known)d blocked, moved or lost and documented with their archived copies,
  **%(n_bad_links)d undocumented failures** (`verification/link_sweep.csv`, with the date and method of each check).

## Extension to %(y0)d · 延伸至 %(y0)d 年

On **2026-10-07** the panel was extended from 2010–2022 back to **%(y0)d**, following the plan in
the project notes (foreign-born and foreign-national stocks wherever a verifiable source exists).

- **%(rows)s rows** now (was 520); %(n_fb)s foreign-born and %(n_fn)s foreign-national values and
  %(n_pop)s population values were added. **No value published before the extension changed**: this
  is asserted cell by cell against the 2026-08-17 panel, and %(rechecked)s published values were
  re-compared with fresh responses from Eurostat, OECD, the World Bank and UN WPP (%(same)s identical).
- Each foreign-born / foreign-national value now states its **source type** (annual, census,
  survey, UN estimate) and carries a **flag**. Where an earlier year had to come from a different
  source than the 2010–2022 series (**%(n_spl)d series**), the gap between the two sources over the
  overlapping years was measured; **%(n_large)d series differ by 5%% or more** and are flagged as a
  break in the series (largest: Slovakia and Denmark foreign-born).
- Not everything could be found. Australia's foreign nationals and Chile's 2002 foreign-born count were
  searched for and not obtained; several countries have only census years; nothing was
  approximated. See `data/known_issues.csv` and the *Verification* page.
- The file names that carry "2010-2022" are unchanged so that existing links keep working; the
  data inside run %(y0)d–%(y1)d.
- Unresolved, for the authors: UN DESA labels the migrant stock of China, India, the Philippines,
  Suriname and Thailand as based on citizenship although the panel carries it as foreign-born
  (`data/known_issues.csv`).

## Health expenditure · 醫療保健支出 (added %(he_when)s)

- New variable **`health_expenditure_pct_gdp`**: current health expenditure as a percentage of GDP for **all %(he_nc)d
  countries and all years %(y0)d–%(y1)d** (%(n_he)s values), the years of the population and migrant series, with source,
  reference period, grade, verification text and flag on every value. No other value changed.
- %(he_nwb)d countries: the WHO Global Health Expenditure Database as published by the World Bank (WDI
  `SH.XPD.CHEX.GD.ZS`); all %(he_ncmp)s values are identical to full precision to WHO's own API
  (`data/health_expenditure_wb_vs_who.csv`). Taiwan, which neither covers: the Ministry of Health and Welfare's
  National Health Expenditure 2024, Table 1, read from the official workbook and identical to the published report;
  long-term care is included only from 2007 and the earlier years are flagged.
- Raw API responses, the workbook, the report and the publishers' own pages are archived with PDF/PNG mirrors in
  `evidence/api/` and `evidence/countries/TWN/`.

## Unemployment rate · 失業率 (added %(ue_when)s)

- New variable **`unemployment_rate`**: unemployed persons as a percentage of the labour force aged 15 and over for
  **all %(ue_nc)d countries and all years %(y0)d–%(y1)d** (%(n_ue)s values), with source, reference period, grade,
  verification text and flag on every value. No other value changed.
- %(ue_nilo)d countries: the ILO modelled estimates (November 2025 edition), read from the ILO's own SDMX API; all
  %(ue_ncmp)s values agree at three decimals with the World Bank's copy (WDI `SL.UEM.TOTL.ZS`,
  `data/unemployment_source_comparison.csv`). **%(ue_nimp)s values are ILO imputations, not based on national data**,
  which the ILO says should not be used for country comparisons; they are flagged (China in every year).
- Taiwan: the DGBAS Manpower Survey (Yearbook of Manpower Survey Statistics 2025, Table 2), read from the official
  workbook and identical to the printed yearbook; the ILO imputes Taiwan's 2021 and 2022 although DGBAS published them.
- Raw responses, the ILO's own dataset description and status codes, the workbook, the yearbook and the World Bank's
  indicator page are archived with PDF/PNG mirrors in `evidence/api/` and `evidence/countries/TWN/`.

## V-Dem liberal democracy index · V-Dem 自由民主指數 (added %(vd_when)s)

- New variable **`vdem_libdem`**: the V-Dem liberal democracy index (`v2x_libdem`, 0 to 1) for **all %(vd_nc)d countries
  and all years %(y0)d–%(y1)d** (%(n_vd)s values), with source, reference period, grade and verification text on every
  value. No other value changed.
- Source: the V-Dem Country-Year Dataset v16 (%(vd_doi)s), read from the V-Dem Institute's own data file (R package
  `vdemdata` 16.0, release commit `%(vd_commit)s`; the archived file's git hash is the one GitHub records). All
  %(vd_ncmp)s values are identical at three decimals to Our World in Data's copy (`data/vdem_source_comparison.csv`,
  which also gives V-Dem's 68%% interval for each value). V-Dem re-estimates past years with every release: cite v16.
- The data file, its codebook entry, the V-Dem Codebook v16 (pages on the index, the interval and the annual
  aggregation), Our World in Data's copy and the publishers' pages are archived with PDF/PNG mirrors in `evidence/api/`.

## Gini index · 吉尼指數 (added %(gi_when)s)

- New variable **`gini_index`**: 100 x the Gini coefficient of income (or consumption) per person for **all %(gi_nc)d
  countries**, in the years a household survey exists (%(n_gi)s of %(gi_ncy)s country-years; the gaps are not filled),
  with source, reference period, grade, verification text and flag on every value. No other value changed.
- %(gi_nwdi)d countries: World Bank WDI `SI.POV.GINI` (Poverty and Inequality Platform, version `%(gi_pv)s`); all
  %(gi_ncmp)s values equal the platform's own survey estimates (`data/gini_source_comparison.csv`). Taiwan, which WDI
  does not publish: the same platform (%(gi_ntwn)d survey years). New Zealand, which the World Bank does not cover: the
  OECD Income Distribution Database (%(gi_nnzl)d years, equivalised disposable income, flagged).
- Flagged: **%(gi_ncons)s consumption-based values** (lower than income-based ones) and **%(gi_nbreak)s survey breaks**
  the World Bank marks as not comparable with earlier surveys.
- Raw responses, the PIP survey table and citation, the OECD dataset description and the publishers' pages are archived
  with PDF/PNG mirrors in `evidence/api/`.

## Decisions of 2026-10-18 · 2026-10-18 之決定

- **Construct and timing (issue #24).** From the ISSP 2021 item the study analyses (Q6a: access to publicly funded
  health care "even if they do not hold citizenship of [country]"), the main regressor is `foreign_nationals_pct_pop`,
  with `foreign_born_pct_pop` as a robustness check; the primary timing rule is the latest stock dated on or before the
  first interview. `data/ANALYSIS_NOTES.md`, sections 1-2; the ISSP documentation quoted is in `evidence/survey/`.
- **Australia (issue #9).** The 2021 Census count of non-citizens (%(aus_v)s) is in a separate column,
  `non_citizens_census`, read from the official ABS workbook; `foreign_nationals` stays an annual series.
- **South Africa (issue #10).** The 2011 Census count was assessed and not added: ten years before the 2021 interviews.
- The independent audit of the health-expenditure variable (issues #31 and #32) found every value correct; the
  verification ledger now covers it, and the evidence labels and retrieval dates follow each value's check method and
  collection date.
<!-- headline:end -->

''' % dict(n_as=n(n_as), n_exact=n(n_exact), pct=100 * n_exact / n_as, n_bad=n_bad,
           # frozen first-release figures (README of commit 0d64a1c); the current ones are in the next block
           n_corr=49, n_ctry=5, held=76, cites=78, urls=72,
           missing='; the 2 that could not be retrieved are named',
           n_re=n_re, n_corr_now=len(corr), n_ctry_now=corr.iso3.nunique(), n_corr_aud=n_corr_aud,
           n_del=len(dele), s_del='' if len(dele) == 1 else 's',
           gtot7=n(grades7.sum()), gb7=n(grades7.get('B', 0)), n_abs=n_abs,
           ga7=n(grades7.get('A', 0)), n_he=n(n_he), he_when=HT.WHEN, he_nc=_hk['n_countries'],
           he_nwb=_hk['n_countries'] - 1, he_ncmp=n(_hk['n_cmp']),
           ue_when=UT.WHEN, ue_nc=_uk['n_countries'], n_ue=n(_uk['n']), ue_nilo=_uk['n_countries'] - 1,
           ue_ncmp=n(_uk['n_cmp']), ue_nimp=n(_uk['n_imp']),
           vd_when=VT.WHEN, vd_nc=_vk['n_countries'], n_vd=n(_vk['n']), vd_doi=VT.DOI, vd_commit=VT.COMMIT[:7],
           vd_ncmp=n(_vk['n_cmp']),
           gi_when=GT.WHEN, gi_nc=_gk['n_countries'], n_gi=n(_gk['n']), gi_ncy=n(40 * (_gk['y1'] - _gk['y0'] + 1)),
           gi_nwdi=_gk['n_wdi_countries'], gi_pv=GT.PIP_VERSION, gi_ncmp=n(_gk['n_wdi']), gi_ntwn=_gk['n_twn'],
           gi_nnzl=_gk['n_nzl'], gi_ncons=n(_gk['n_cons']), gi_nbreak=n(_gk['n_break']),
           aus_v=n(panel.non_citizens_census.dropna().iloc[0]),
           last=LAST, gtot=n(gtot), y0=Y0, y1=Y1, ga=n(grades.get('A', 0)),
           gb=n(grades.get('B', 0)), gc=n(grades.get('C', 0)), n_sweep=len(sweep),
           sweep_date='2026-10-07', n_bad_links=n_bad_links, n_aud=len(aud), aud_kinds=aud_kinds, n_cur=n(n_cur),
           n_ok=int((sweep.status == 'OK').sum()), n_retry_ok=n_retry_ok, n_known=int((sweep.status == 'KNOWN').sum()),
           rows=n(len(panel)), n_fb=n(new['foreign_born']), n_fn=n(new['foreign_nationals']),
           n_pop=n(new['population'] + new['population_un_wpp2024']),
           rechecked=n(ovl.cells_compared.sum()), same=n(ovl.identical.sum()), n_spl=len(spl),
           n_large=n_large)

if '<!-- headline:begin -->' in s:
    s = re.sub(r'<!-- headline:begin -->.*?<!-- headline:end -->\n\n', lambda m: HEAD, s, flags=re.S)
else:
    s = re.sub(r'## Headline results\n.*?(?=## How sources were preserved)', lambda m: HEAD, s,
               flags=re.S)
s = s.replace('查獲人次', '查獲人數')            # Eurostat counts persons; Mexico's events are named in the codebook
open(fp, 'w', encoding='utf-8').write(s)
print('README.md refreshed')

# ---------------------------------------------------------------- CITATION.cff
fp = os.path.join(SITE, 'CITATION.cff')
c = open(fp, encoding='utf-8').read()


def csub(pattern, repl):
    global c
    c, k = re.subn(pattern, lambda m: repl, c, count=1)
    assert k == 1, 'CITATION pattern not found: %s' % pattern[:60]


csub(r'title: "[^"]*"', 'title: "Migration and population data archive, 40 countries, %d-%d"' % (Y0, Y1))
csub(r'version: "[^"]*"', 'version: "%s"' % LAST)
csub(r'date-released: [\d-]+', 'date-released: %s' % LAST)
csub(r'state the\n  archive (?:freeze date, 2026-08-17\.|version \([^)]*\)\.)',
     'state the\n  archive version (first freeze 2026-08-17; extended to %d on 2026-10-07; health expenditure added '
     'on %s; unemployment rate added on %s; V-Dem liberal democracy index added on %s; Gini index added on %s).'
     % (Y0, HT.WHEN, UT.WHEN, VT.WHEN, GT.WHEN))       # the extension date is fixed; LAST moves with every later amendment
csub(r'and \d+ values were corrected,', 'and %d values were corrected,' % len(corr))
csub(r'covering 40 countries for [\d-]+\.', 'covering 40 countries for %d-%d.' % (Y0, Y1))
if 'extended back' not in c:
    c = c.replace('  each itemised with its evidence.\n',
                  '  each itemised with its evidence. On %s the panel was extended back from 2010 to %d '
                  'for the foreign-born, foreign-national and population series; no value published '
                  'earlier changed, and %s of them were re-compared with fresh source responses.\n'
                  % ('2026-10-07', Y0, n(ovl.cells_compared.sum())), 1)
    assert 'extended back' in c
csub(r'(?:no value published earlier changed|the extension itself changed no value published earlier), and [\d,]+ of them were re-compared with fresh source responses\.[^\n]*',
     'the extension itself changed no value published earlier, and %s of them were re-compared with fresh source '
     'responses. An audit on 2026-10-07 re-checked 24 findings against the archived sources and confirmed all of '
     'them; %d cells were corrected, added, regraded or deleted as a result (verification/AUDIT_RESPONSE_2026-10-07.md). '
     'On %s a health-expenditure variable (current health expenditure as a percentage of GDP) was added for all %d '
     "countries and years, from the WHO Global Health Expenditure Database via the World Bank, checked against WHO's "
     'own API, and for Taiwan from the Ministry of Health and Welfare; on %s an unemployment-rate variable for all '
     '%d countries and years, from the ILO modelled estimates (imputed values flagged) and for Taiwan from DGBAS; on %s '
     'the V-Dem liberal democracy index for all %d countries and years (V-Dem v16); on %s the Gini index for all %d '
     'countries in their survey years (World Bank Poverty and Inequality Platform; New Zealand from the OECD); no other '
     'value changed.'
     % (n(ovl.cells_compared.sum()), len(aud), HT.WHEN, _hk['n_countries'], UT.WHEN, _uk['n_countries'],
        VT.WHEN, _vk['n_countries'], GT.WHEN, _gk['n_countries']))
open(fp, 'w', encoding='utf-8').write(c)
print('CITATION.cff refreshed')

# ---------------------------------------------------------------- VERIFICATION_REPORT notice
fp = os.path.join(SITE, 'VERIFICATION_REPORT.md')
r = open(fp, encoding='utf-8').read()
NOTICE = ('> **This report records the first release (2010–2022, verified 2026-08-17/18) and is kept '
          'as written; its counts describe that release.** The panel was extended back to %d on '
          '2026-10-07: that extension, the re-check of every value published earlier, and the issues '
          'it raised are on the Verification page of the site, in `data/revision_history.csv`, '
          '`data/known_issues.csv` and `data/extension_*.csv`. The audit of 2026-10-07 (24 findings, several of them about '
          'this report\'s own statements, for example the detections unit, the source-reachability claims and the '
          'first-release grade counts) is answered finding by finding in `verification/AUDIT_RESPONSE_2026-10-07.md`.\n\n'
          % Y0)
if 'This report records the first release' in r:
    r = re.sub(r'> \*\*This report records the first release.*?\n\n', lambda m: NOTICE, r, count=1,
               flags=re.S)
else:
    r = r.replace('**Scope** —', NOTICE + '**Scope** —', 1)
open(fp, 'w', encoding='utf-8').write(r)
print('VERIFICATION_REPORT.md notice written')
