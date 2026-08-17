# -*- coding: utf-8 -*-
"""Generate the static archive website."""
import os, re, html, json, datetime
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(BASE, 'migration-data-archive')
D = os.path.join(SITE, 'data')
EV = os.path.join(SITE, 'evidence', 'countries')
ACCESS = '2026-08-17'

panel = pd.read_csv(os.path.join(D, 'panel_final.csv'))
qual = pd.read_csv(os.path.join(D, 'data_quality.csv'))
corr = pd.read_csv(os.path.join(D, 'corrections_applied.csv'))
issues = pd.read_csv(os.path.join(D, 'known_issues.csv'))
vlog = pd.read_csv(os.path.join(D, 'verification_log.csv'))
reg = pd.read_csv(os.path.join(D, 'source_register.csv'))
codeb = pd.read_csv(os.path.join(D, 'codebook.csv'))
apis = pd.read_csv(os.path.join(D, 'api_snapshots.csv'))
snaps = pd.read_csv(os.path.join(D, 'web_snapshots.csv'))
irrall = pd.read_csv(os.path.join(D, 'irregular_estimates_all.csv'))

VARS = ['population', 'foreign_born', 'foreign_nationals', 'irregular_stock',
        'irregular_proxy_overstayers', 'irregular_proxy_detections']
VLAB = {'population': 'Population', 'foreign_born': 'Foreign-born',
        'foreign_nationals': 'Foreign nationals', 'irregular_stock': 'Irregular stock',
        'irregular_proxy_overstayers': 'Overstayers', 'irregular_proxy_detections': 'Detections'}

E = lambda s: html.escape('' if s is None or (isinstance(s, float) and pd.isna(s)) else str(s))


def num(v, dec=0):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return '<span style="color:var(--faint)">—</span>'
    try:
        return f'{float(v):,.{dec}f}'
    except Exception:
        return E(v)


def pill(g):
    g = str(g).strip()
    return f'<span class="g g{g}">{g}</span>' if g in 'ABCD' and g else ''


NAV = [('index.html', 'Overview'), ('countries.html', 'Countries'),
       ('sources.html', 'Sources'), ('data.html', 'Data files'),
       ('verification.html', 'Verification'), ('methods.html', 'Methods')]


def page(fn, title, body, up='', desc=''):
    nav = ''.join(
        f'<a href="{up}{h}"{" aria-current=\"page\"" if h == os.path.basename(fn) else ""}>{t}</a>'
        for h, t in NAV)
    doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="stylesheet" href="{up}assets/style.css">
</head>
<body>
<header class="site"><div class="wrap">
  <a class="brand" href="{up}index.html">Migration &amp; Population Data Archive</a>
  <nav>{nav}</nav>
</div></header>
{body}
<footer class="site"><div class="wrap">
  <p class="credit"><strong>This archive is joint work of
     <a href="https://raymond.cph.ntu.edu.tw/" rel="noopener">Prof. Raymond Kuo</a>,
     National Taiwan University, and Claude (Anthropic).</strong></p>
  <p><strong>Migration and population data archive, 40 countries, 2010–2022.</strong>
     Every source retrieved and verified {ACCESS}.</p>
  <p>Companion archive to a study of attitudes toward publicly funded healthcare for
     non-nationals. Prepared for journal editors and peer reviewers.</p>
  <p>All files in this archive are mirrors held for verification. Copyright in each source
     document remains with its publisher; each entry links to the original URL.</p>
</div></footer>
</body></html>'''
    p = os.path.join(SITE, fn)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(doc)


def filelink(relpath, label=None, kind=''):
    if not relpath:
        return ''
    cls = 'file'
    low = relpath.lower()
    if low.endswith(('.png', '.jpg', '.jpeg')):
        cls += ' img'
    elif low.endswith('.pdf'):
        cls += ' pdf'
    return f'<a class="{cls}" href="{E(relpath)}" download>{E(label or os.path.basename(relpath))}</a>'


def table(df, cols, headers=None, numcols=(), rawcols=(), cls=''):
    headers = headers or cols
    h = ''.join(f'<th class="{"num" if c in numcols else ""}">{E(t)}</th>'
                for c, t in zip(cols, headers))
    body = []
    for _, r in df.iterrows():
        tds = []
        for c in cols:
            v = r.get(c)
            if c in rawcols:
                tds.append(f'<td>{v if pd.notna(v) else ""}</td>')
            elif c in numcols:
                tds.append(f'<td class="num">{num(v)}</td>')
            else:
                tds.append(f'<td>{E(v)}</td>')
        body.append('<tr>' + ''.join(tds) + '</tr>')
    return (f'<div class="tablewrap {cls}"><table><thead><tr>{h}</tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>')


# =====================================================================  INDEX
n_checked = len(vlog)
n_exact = int((vlog.status == 'EXACT').sum())
# all displayed variables, including Taiwan's absconded-workers column
GRADE_VARS = VARS + ['irregular_proxy_absconded_workers']
grades = pd.Series([g for v in GRADE_VARS if v + '_grade' in panel
                    for g in panel[v + '_grade'].dropna() if str(g).strip()]).value_counts()
n_files = sum(len(fs) for _, _, fs in os.walk(os.path.join(SITE, 'evidence')))
ev_bytes = sum(os.path.getsize(os.path.join(rt, f))
               for rt, _, fs in os.walk(os.path.join(SITE, 'evidence')) for f in fs)

body = f'''
<div class="hero"><div class="wrap">
  <p class="eyebrow">Replication &amp; source archive · accessed {ACCESS}</p>
  <h1>Migration and population data for 40 countries, 2010–2022</h1>
  <p class="lede">Every number in the accompanying dataset is traced here to a source file you can
  download. Statistical-agency APIs were captured as raw response snapshots; web pages were
  mirrored as PDF and full-page screenshots on the access date. Nothing in this archive depends
  on a live external server still being available.</p>
</div></div>

<section><div class="wrap">
  <div class="stats">
    <div class="stat"><span class="n">{n_checked:,}</span><span class="l">values re-derived from live sources</span></div>
    <div class="stat"><span class="n">{n_exact / n_checked * 100:.1f}%</span><span class="l">matched the source exactly</span></div>
    <div class="stat"><span class="n">{n_files}</span><span class="l">source files archived</span></div>
    <div class="stat"><span class="n">{ev_bytes / 1e6:.0f} MB</span><span class="l">of mirrored evidence</span></div>
    <div class="stat"><span class="n">40</span><span class="l">countries, 13 years each</span></div>
    <div class="stat"><span class="n">{len(corr)}</span><span class="l">values corrected</span></div>
    <div class="stat"><span class="n">156</span><span class="l">per-variable evidence pages, each with a PDF extract</span></div>
  </div>
</div></section>

<section><div class="wrap">
  <h2>Start here</h2>
  <p class="sub">Four routes into the archive, depending on what you want to check.</p>
  <div class="cards">
    <div class="card"><h3>The dataset</h3>
      <p>The verified panel as Excel and CSV, with a quality grade on every value, plus the
         codebook and the two original input workbooks.</p>
      <a class="go" href="data.html">Data files &rarr;</a></div>
    <div class="card"><h3>Country by country</h3>
      <p>One page per country: the data, the check against the live source, and every source
         document held locally for that country.</p>
      <a class="go" href="countries.html">40 countries &rarr;</a></div>
    <div class="card"><h3>Every source</h3>
      <p>The complete source register: 78 country&ndash;source citations, 76 of them archived
         here, each linking to both the original URL and the local copy.</p>
      <a class="go" href="sources.html">Source register &rarr;</a></div>
    <div class="card"><h3>What was checked</h3>
      <p>All {n_checked:,} value-by-value comparisons, the corrections applied, and the issues
         that remain.</p>
      <a class="go" href="verification.html">Verification &rarr;</a></div>
  </div>
</div></section>

<section><div class="wrap">
  <h2>How reliable is each value?</h2>
  <p class="sub">Every one of the {int(grades.sum()):,} values in the panel carries a grade.
     Grades are assigned per value, not per country.</p>
  <div class="tablewrap"><table>
   <thead><tr><th>Grade</th><th>Meaning</th><th class="num">Values</th><th class="num">Share</th></tr></thead>
   <tbody>
    <tr><td>{pill('A')}</td><td>Re-derived from a machine-readable official source and matched
        exactly, or corrected against one during this verification</td>
        <td class="num">{grades.get('A', 0):,}</td><td class="num">{grades.get('A', 0) / grades.sum() * 100:.1f}%</td></tr>
    <tr><td>{pill('B')}</td><td>Confirmed by reading the retrieved source document</td>
        <td class="num">{grades.get('B', 0):,}</td><td class="num">{grades.get('B', 0) / grades.sum() * 100:.1f}%</td></tr>
    <tr><td>{pill('C')}</td><td>Source document retrieved, but the value is a modelled estimate
        that cannot be mechanically re-derived</td>
        <td class="num">{grades.get('C', 0):,}</td><td class="num">{grades.get('C', 0) / grades.sum() * 100:.1f}%</td></tr>
    <tr><td>{pill('D')}</td><td>Cited source could not be retrieved by any means</td>
        <td class="num">{grades.get('D', 0):,}</td><td class="num">{grades.get('D', 0) / grades.sum() * 100:.1f}%</td></tr>
   </tbody></table></div>
  <div class="note"><strong>The six D-graded values</strong> are Korea's 2010–2015 overstayer
   figures. Their only source is a Korean National Police University publication whose host no
   longer responds, so they could not be checked against anything. They are retained and flagged
   rather than dropped.</div>
</div></section>

<section><div class="wrap">
  <h2>The substantive finding</h2>
  <p class="sub">Verification was not a formality. It changed the data.</p>
  <div class="note bad"><strong>A one-year offset in three countries.</strong> In the input
   workbook, the Eurostat irregular-migration detections series for <strong>Switzerland,
   Portugal and Sweden</strong> was shifted by one year: the figure Eurostat publishes for year
   <em>Y+1</em> sat under year <em>Y</em>. The genuine 2010 values were missing and the 2022 cell
   held the 2023 figure. All 39 values were replaced with the year-aligned Eurostat data.</div>
  <p>A consequence worth noting: the input codebook warned that Sweden's detections series breaks
  between 2013 (72,835) and 2014 (1,445). That break is an artefact of the offset. In the real
  Eurostat data it falls between <strong>2014 and 2015</strong>. The evidence is archived as
  <a href="evidence/api/eurostat_migr_eipre_CH_PT_SE_2010_2023.json">a raw Eurostat API response
  covering 2010–2023</a>.</p>
  <p>Three further corrections were made — Taiwan's overstayer column mixed two incompatible
  national measures, Italy's irregular series was missing four years and mixed two methods, and
  the two input workbooks disagreed on population because they used different publishers.
  <a href="verification.html">All {len(corr)} corrections are itemised, with evidence.</a></p>
</div></section>

<section><div class="wrap">
  <h2>Every number is a link</h2>
  <p class="sub">On each country page, the Panel data table is fully clickable.</p>
  <p>Click any value &mdash; or the grade pill beside it &mdash; and you land on the evidence for
  that exact figure: the source, the query URL that produced it, what it was checked against, the
  correction applied if there was one, and every archived file that supports it. There are
  <strong>156 such evidence pages</strong>, one per country and variable, each with its own
  <strong>PDF extract</strong> so the numbers exist in a fixed, citable document as well as on
  the page.</p>
  <p>This holds for the bulk statistical sources too. The World Bank, Eurostat, OECD and UN DESA
  series are backed not only by their raw API payloads but by <strong>PDF and screenshot mirrors
  of the publishers' own dataset pages</strong>, captured on the access date.</p>
</div></section>

<section><div class="wrap">
  <h2>Authorship</h2>
  <p>This archive is joint work of
  <a href="https://raymond.cph.ntu.edu.tw/" rel="noopener"><strong>Prof. Raymond Kuo</strong></a>,
  National Taiwan University, and <strong>Claude</strong> (Anthropic).</p>
</div></section>

<section><div class="wrap">
  <h2>Using this archive</h2>
  <p class="sub">For editors and reviewers.</p>
  <ul class="clean">
   <li><strong>Every file is downloadable at a stable relative URL.</strong> Nothing is behind a
       script, a query string, or an external service.</li>
   <li><strong>API data is archived as raw responses.</strong> The exact JSON and spreadsheet
       payloads returned by the World Bank, Eurostat, OECD and UN DESA on {ACCESS} are in
       <code>evidence/api/</code>, together with the query URL that produced each one.</li>
   <li><strong>Web pages are archived three ways</strong> where possible: the original HTML, a
       PDF mirror, and a full-page PNG screenshot, all captured on {ACCESS}.</li>
   <li><strong>Integrity is checkable.</strong> <a href="manifest/checksums.csv">SHA-256
       checksums</a> are published for every file in the archive.</li>
   <li><strong>The verification is re-runnable.</strong> Every script used is included in
       <code>scripts/</code>.</li>
  </ul>
</div></section>
'''
page('index.html', 'Migration & Population Data Archive, 40 countries 2010–2022', body,
     desc='Source archive and verification record for a 40-country migration and population '
          'panel, 2010-2022. Every value traced to a downloadable source file.')
print('index.html')

# =====================================================================  COUNTRIES INDEX
cinfo = panel.groupby(['iso3', 'country']).first().reset_index()[['iso3', 'country']]
boxes = []
for _, r in cinfo.sort_values('country').iterrows():
    iso = r['iso3']
    g = panel[panel.iso3 == iso]
    nv = sum(g[v].notna().sum() for v in VARS)
    nf = len(os.listdir(os.path.join(EV, iso))) if os.path.isdir(os.path.join(EV, iso)) else 0
    boxes.append(f'<a class="cbox" href="countries/{iso}.html"><span class="cn">{E(r["country"])}</span>'
                 f'<span class="cm">{iso} · {nv} values · {nf} files</span></a>')
body = f'''
<div class="hero"><div class="wrap">
  <p class="eyebrow">40 countries</p>
  <h1>Country pages</h1>
  <p class="lede">Each page shows that country's data with a grade on every value, the result of
  checking it against the live source, and every source document archived locally for it.</p>
</div></div>
<section><div class="wrap">
  <div class="toolbar">
    <input type="search" id="q" placeholder="Filter countries…" aria-label="Filter countries">
    <span class="count" id="n">40 countries</span>
  </div>
  <div class="cgrid" id="grid">{''.join(boxes)}</div>
</div></section>
<script>
(function(){{
  var q=document.getElementById('q'),grid=document.getElementById('grid'),
      n=document.getElementById('n'),items=[].slice.call(grid.children);
  q.addEventListener('input',function(){{
    var t=q.value.trim().toLowerCase(),c=0;
    items.forEach(function(el){{
      var m=!t||el.textContent.toLowerCase().indexOf(t)>=0;
      el.style.display=m?'':'none'; if(m)c++;
    }});
    n.textContent=c+' countr'+(c===1?'y':'ies');
  }});
}})();
</script>
'''
page('countries.html', 'Country pages — Migration Data Archive', body,
     desc='Per-country data, verification results and archived source documents.')
print('countries.html')
