# -*- coding: utf-8 -*-
"""Shared helpers and loaded data for the archive site generator."""
import os, html
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
        'irregular_proxy_overstayers': 'Overstayers', 'irregular_proxy_detections': 'Detections',
        'irregular_proxy_absconded_workers': 'Absconded workers (TW)',
        'irregular_detections': 'Detections', 'irregular': 'Irregular migration',
        'foreign_workers': 'Foreign workers'}

NAV = [('index.html', 'Overview'), ('countries.html', 'Countries'),
       ('sources.html', 'Sources'), ('data.html', 'Data files'),
       ('verification.html', 'Verification'), ('methods.html', 'Methods')]


def E(s):
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return ''
    return html.escape(str(s))


def num(v, dec=0):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return '<span style="color:var(--faint)">&mdash;</span>'
    try:
        return format(float(v), ',.%df' % dec)
    except Exception:
        return E(v)


def pill(g):
    g = str(g).strip()
    if g in ('A', 'B', 'C', 'D'):
        return '<span class="g g%s">%s</span>' % (g, g)
    return ''


def filelink(relpath, label=None):
    if not relpath:
        return ''
    cls = 'file'
    low = str(relpath).lower()
    if low.endswith(('.png', '.jpg', '.jpeg')):
        cls += ' img'
    elif low.endswith('.pdf'):
        cls += ' pdf'
    return '<a class="%s" href="%s" download>%s</a>' % (
        cls, E(relpath), E(label or os.path.basename(str(relpath))))


def page(fn, title, body, up='', desc=''):
    cur = os.path.basename(fn)
    nav = ''.join(
        '<a href="%s%s"%s>%s</a>' % (up, h, ' aria-current="page"' if h == cur else '', t)
        for h, t in NAV)
    doc = (
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        '<title>' + E(title) + '</title>\n'
        '<meta name="description" content="' + E(desc) + '">\n'
        '<link rel="stylesheet" href="' + up + 'assets/style.css">\n</head>\n<body>\n'
        '<header class="site"><div class="wrap">\n'
        '  <a class="brand" href="' + up + 'index.html">Migration &amp; Population Data Archive</a>\n'
        '  <nav>' + nav + '</nav>\n</div></header>\n'
        + body +
        '\n<footer class="site"><div class="wrap">\n'
        '  <p class="credit"><strong>This archive is joint work of '
        '<a href="https://raymond.cph.ntu.edu.tw/" rel="noopener">Prof. Raymond Kuo</a>, '
        'National Taiwan University, and Claude (Anthropic).</strong></p>\n'
        '  <p><strong>Migration and population data archive, 40 countries, 2010&ndash;2022.</strong> '
        'Every source retrieved and verified ' + ACCESS + '.</p>\n'
        '  <p>Companion archive to a study of attitudes toward publicly funded healthcare for '
        'non-nationals. Prepared for journal editors and peer reviewers.</p>\n'
        '  <p>All files here are mirrors held for verification. Copyright in each source document '
        'remains with its publisher; every entry links to the original URL.</p>\n'
        '</div></footer>\n</body></html>')
    p = os.path.join(SITE, fn)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(doc)


def table(df, cols, headers=None, numcols=(), rawcols=(), maxlen=None):
    headers = headers or cols
    h = ''.join('<th class="%s">%s</th>' % ('num' if c in numcols else '', E(t))
                for c, t in zip(cols, headers))
    body = []
    for _, r in df.iterrows():
        tds = []
        for c in cols:
            v = r.get(c)
            if c in rawcols:
                tds.append('<td>%s</td>' % ('' if pd.isna(v) else v))
            elif c in numcols:
                tds.append('<td class="num">%s</td>' % num(v))
            else:
                s = E(v)
                if maxlen and len(s) > maxlen:
                    s = s[:maxlen] + '&hellip;'
                tds.append('<td>%s</td>' % s)
        body.append('<tr>' + ''.join(tds) + '</tr>')
    return ('<div class="tablewrap"><table><thead><tr>' + h + '</tr></thead><tbody>'
            + ''.join(body) + '</tbody></table></div>')
