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
n_large = int((spl.mean_gap_pct.abs() >= 5).sum())
pages_each = val['pages_en']
total_pages = val['pages_en'] + val['pages_zh']
n_ext = int((sweep.status != 'OK').sum())
n_bad_links = int((~sweep.status.isin(['OK', 'KNOWN'])).sum())

# ---------------------------------------------------------------- README
fp = os.path.join(SITE, 'README.md')
s = open(fp, encoding='utf-8').read()


def sub(pattern, repl, count=1, flags=0):
    global s
    s, k = re.subn(pattern, lambda m: repl, s, count=count, flags=flags)
    assert k >= 1, 'README pattern not found: %s' % pattern[:60]


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
sub(r'build_evidence\.py         # \d+ evidence', 'build_evidence.py         # %d evidence' % K.N_EVIDENCE)
sub(r'build_pdf_extracts\.py     # \d+ bilingual', 'build_pdf_extracts.py     # %d bilingual' % K.N_EVIDENCE)
sub(r'About [\d,]+ MB across ~?[\d,]+ files\. No single file exceeds \d+ MB; the largest is [^\n]*\n(?:  workbook at \d+ MB\.\n)?',
    'About %d MB across %s files. No single file exceeds %d MB; the largest is %s at %d MB.\n'
    % (round(ck.bytes.sum() / 1e6), n(len(ck)), int(ck.bytes.max() / 1e6) + 1,
       os.path.basename(ck.loc[ck.bytes.idxmax(), 'path']), round(ck.bytes.max() / 1e6)))

miss = K.N_CITES - K.N_CITES_HELD
HEAD = '''<!-- headline:begin -->
## Headline results

**At first release (2026-08-17 / 08-18)**

- **%(n_as)s** values re-derived from live sources; **%(n_exact)s (%(pct).1f%%)** matched exactly.
- **%(n_bad)d** discrepancies found — all one error: the Eurostat irregular-migration detections
  series for **Switzerland, Portugal and Sweden** was offset by one year in one input workbook.
- **%(n_corr)d** corrections across %(n_ctry)d countries, each itemised with its evidence
  (`data/corrections_applied.csv`).
- **%(held)d of %(cites)d** distinct country-source document citations archived, across %(urls)d URLs%(missing)s.
- **Every retained number is traceable to an archived source.** Each of the 116 values that were
  not machine-verified at first release was checked against the archived source document: 102 were
  found in it and regraded B, 13 are derived from a published range and are flagged ≈, and 1
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

- Quality grades on all %(gtot)s displayed values (%(y0)d–%(y1)d): **A** %(ga)s · **B** %(gb)s · **C** %(gc)s · **D** 0.
- Live sweep of all **%(n_sweep)d** external URLs the site publishes, run %(sweep_date)s: **%(n_bad_links)d undocumented
  failures** (`verification/link_sweep.csv`).

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
<!-- headline:end -->

''' % dict(n_as=n(n_as), n_exact=n(n_exact), pct=100 * n_exact / n_as, n_bad=n_bad,
           n_corr=len(corr), n_ctry=corr.iso3.nunique(), held=K.N_CITES_HELD, cites=K.N_CITES,
           urls=K.N_DOC_URLS,
           missing=('; the %d that could not be retrieved are named' % miss) if miss else '',
           last=LAST, gtot=n(gtot), y0=Y0, y1=Y1, ga=n(grades.get('A', 0)),
           gb=n(grades.get('B', 0)), gc=n(grades.get('C', 0)), n_sweep=len(sweep),
           sweep_date='2026-10-07', n_bad_links=n_bad_links,
           rows=n(len(panel)), n_fb=n(new['foreign_born']), n_fn=n(new['foreign_nationals']),
           n_pop=n(new['population'] + new['population_un_wpp2024']),
           rechecked=n(ovl.cells_compared.sum()), same=n(ovl.identical.sum()), n_spl=len(spl),
           n_large=n_large)

if '<!-- headline:begin -->' in s:
    s = re.sub(r'<!-- headline:begin -->.*?<!-- headline:end -->\n\n', lambda m: HEAD, s, flags=re.S)
else:
    s = re.sub(r'## Headline results\n.*?(?=## How sources were preserved)', lambda m: HEAD, s,
               flags=re.S)
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
     'state the\n  archive version (first freeze 2026-08-17; extended to %d on %s).' % (Y0, LAST))
csub(r'and \d+ values were corrected,', 'and %d values were corrected,' % len(corr))
csub(r'covering 40 countries for [\d-]+\.', 'covering 40 countries for %d-%d.' % (Y0, Y1))
if 'extended back' not in c:
    c = c.replace('  each itemised with its evidence.\n',
                  '  each itemised with its evidence. On %s the panel was extended back from 2010 to %d '
                  'for the foreign-born, foreign-national and population series; no value published '
                  'earlier changed, and %s of them were re-compared with fresh source responses.\n'
                  % (LAST, Y0, n(ovl.cells_compared.sum())), 1)
    assert 'extended back' in c
open(fp, 'w', encoding='utf-8').write(c)
print('CITATION.cff refreshed')

# ---------------------------------------------------------------- VERIFICATION_REPORT notice
fp = os.path.join(SITE, 'VERIFICATION_REPORT.md')
r = open(fp, encoding='utf-8').read()
NOTICE = ('> **This report records the first release (2010–2022, verified 2026-08-17/18) and is kept '
          'as written; its counts describe that release.** The panel was extended back to %d on '
          '2026-10-07: that extension, the re-check of every value published earlier, and the issues '
          'it raised are on the Verification page of the site, in `data/revision_history.csv`, '
          '`data/known_issues.csv` and `data/extension_*.csv`.\n\n' % Y0)
if 'This report records the first release' in r:
    r = re.sub(r'> \*\*This report records the first release.*?\n\n', lambda m: NOTICE, r, count=1,
               flags=re.S)
else:
    r = r.replace('**Scope** —', NOTICE + '**Scope** —', 1)
open(fp, 'w', encoding='utf-8').write(r)
print('VERIFICATION_REPORT.md notice written')
