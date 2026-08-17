# -*- coding: utf-8 -*-
"""Shared helpers for the bilingual build."""
import os, sys, html
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import i18n
from i18n import T, t, COUNTRY, VLAB, NAV, BRAND, FOOTER, GRADE_DESC, GRADE_SHORT, VERTAG
from i18n import HTML_LANG, OTHER, SWITCH_LABEL, SWITCH_TITLE, USABLE, COMPARABILITY, reason_zh
import i18n_content as C

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Resolve the site directory relative to this file so the build works both from the
# standalone bilingual folder and from inside the published archive (scripts/ lives in it).
_here = os.path.dirname(os.path.abspath(__file__))
_parent = os.path.dirname(_here)
if os.path.isdir(os.path.join(_parent, 'data')) and os.path.isdir(os.path.join(_parent, 'evidence')):
    SITE = _parent                      # scripts/ sits inside the site
else:
    SITE = os.path.join(BASE, 'migration-data-archive-bilingual')
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
pubs = pd.read_csv(os.path.join(D, 'api_publisher_snapshots.csv'))

VARS = ['population', 'foreign_born', 'foreign_nationals', 'irregular_stock',
        'irregular_proxy_overstayers', 'irregular_proxy_detections']
ALLVARS = VARS + ['irregular_proxy_absconded_workers']


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
    return '<span class="g g%s">%s</span>' % (g, g) if g in ('A', 'B', 'C', 'D') else ''


def cname(en, lang):
    return COUNTRY.get(en, en) if lang == 'zh' else en


def vlab(v, lang):
    return VLAB[lang].get(v, VLAB['en'].get(v, v))


def suffix(lang):
    return '' if lang == 'en' else '.zh'


def fname(stem, lang):
    """countries/CHE + zh -> countries/CHE.zh.html"""
    return '%s%s.html' % (stem, suffix(lang))


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


def page(stem, title, body, lang, up='', desc=''):
    """stem is the path without language suffix or extension, e.g. 'countries/CHE'."""
    fn = fname(stem, lang)
    cur = os.path.basename(fn)
    nav = ''.join(
        '<a href="%s%s"%s>%s</a>' % (up, fname(h[:-5], lang),
                                     ' aria-current="page"' if fname(h[:-5], lang) == cur else '', lbl)
        for h, lbl in NAV[lang])
    o = OTHER[lang]
    switch = ('<a class="langsw" href="%s%s" title="%s" hreflang="%s" rel="alternate">%s</a>'
              % (up, os.path.basename(fname(stem, o)) if '/' not in stem else fname(stem, o),
                 SWITCH_TITLE[lang], HTML_LANG[o], SWITCH_LABEL[lang]))
    # for nested pages the alternate must keep the same directory
    alt_href = fname(stem, o)
    if '/' in stem:
        switch = ('<a class="langsw" href="%s%s" title="%s" hreflang="%s" rel="alternate">%s</a>'
                  % (up, alt_href, SWITCH_TITLE[lang], HTML_LANG[o], SWITCH_LABEL[lang]))
    else:
        switch = ('<a class="langsw" href="%s%s" title="%s" hreflang="%s" rel="alternate">%s</a>'
                  % (up, alt_href, SWITCH_TITLE[lang], HTML_LANG[o], SWITCH_LABEL[lang]))

    foot = ''.join(x.replace('ACCESS', ACCESS) for x in FOOTER[lang])
    doc = (
        '<!doctype html>\n<html lang="%s">\n<head>\n<meta charset="utf-8">\n' % HTML_LANG[lang]
        + '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        '<title>' + E(title) + '</title>\n'
        '<meta name="description" content="' + E(desc) + '">\n'
        '<link rel="alternate" hreflang="%s" href="%s%s">\n' % (HTML_LANG[o], up, alt_href)
        + '<link rel="stylesheet" href="' + up + 'assets/style.css">\n</head>\n<body>\n'
        '<header class="site"><div class="wrap">\n'
        '  <a class="brand" href="' + up + fname('index', lang) + '">' + BRAND[lang] + '</a>\n'
        '  <nav>' + nav + switch + '</nav>\n</div></header>\n'
        + body +
        '\n<footer class="site"><div class="wrap">\n' + foot + '\n</div></footer>\n</body></html>')
    p = os.path.join(SITE, fn)
    os.makedirs(os.path.dirname(p) if os.path.dirname(p) else SITE, exist_ok=True)
    open(p, 'w', encoding='utf-8').write(doc)


def table(df, cols, headers, numcols=(), rawcols=(), maxlen=None):
    h = ''.join('<th class="%s">%s</th>' % ('num' if c in numcols else '', E(x))
                for c, x in zip(cols, headers))
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


def usable_zh(x):
    return USABLE.get(str(x), str(x))
