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


# =====================================================================================
# Archived artifacts for one source.
# Every source row anywhere on the site resolves through this, so the country pages,
# the evidence pages and the site-wide Sources page all offer the same set of files:
# the archived original, its rendered mirror, the publisher page mirror, and any
# page snapshot.
# =====================================================================================
_mirror_idx = {}
_mp = os.path.join(D, 'source_mirrors.csv')
if os.path.exists(_mp):
    for _, _r in pd.read_csv(_mp).iterrows():
        _ms = [x for x in str(_r.get('mirrors') or '').split(';') if x]
        if _ms:
            _mirror_idx[(str(_r['folder']), str(_r['source_file']))] = _ms

_pub_by_key = {}
_pp = os.path.join(D, 'api_publisher_snapshots.csv')
if os.path.exists(_pp):
    for _, _r in pd.read_csv(_pp).iterrows():
        _pub_by_key[_r['key']] = _r

_apis = pd.read_csv(os.path.join(D, 'api_snapshots.csv')) if \
    os.path.exists(os.path.join(D, 'api_snapshots.csv')) else pd.DataFrame()

_snap_by = {}
_sp = os.path.join(D, 'web_snapshots.csv')
if os.path.exists(_sp):
    for _, _r in pd.read_csv(_sp).iterrows():
        _snap_by.setdefault((_r['iso3'], str(_r['source_url'])), []).append(_r)


def publisher_key(url):
    u = str(url)
    if 'api.worldbank.org' in u and 'SP.POP.TOTL' in u:
        return 'worldbank_SP_POP_TOTL'
    if 'api.worldbank.org' in u and 'SM.POP.TOTL' in u:
        return 'worldbank_SM_POP_TOTL'
    for k in ('migr_pop3ctb', 'migr_pop1ctz', 'migr_eipre'):
        if k in u:
            return 'eurostat_' + k
    if 'sdmx.oecd.org' in u:
        return 'oecd_international_migration_database'
    if 'population.un.org' in u:
        return 'un_wpp_2024'
    if 'un.org/development/desa' in u:
        return 'un_desa_international_migrant_stock_2024'
    return None


def _mirrors_of(folder, filename, lang):
    out = []
    for m in _mirror_idx.get((folder, filename), []):
        is_pdf = m.lower().endswith('.pdf')
        lab = ({'en': 'PDF mirror', 'zh': 'PDF 鏡像'} if is_pdf
               else {'en': 'screenshot', 'zh': '截圖'})[lang]
        out.append((lab, folder + '/' + m))
    return out


def artifacts(iso3, url, local_file, lang, is_api=False):
    """All archived files for one source, as (label, path-from-site-root)."""
    out, seen = [], set()

    def add(label, rel):
        if rel and rel not in seen and os.path.isfile(
                os.path.join(SITE, rel.replace('/', os.sep))):
            seen.add(rel)
            out.append((label, rel))

    url = str(url or '')
    lf = str(local_file or '')

    # 1. the archived original document, and its rendered mirror
    if lf and lf != 'nan':
        folder = 'evidence/countries/%s' % iso3
        add({'en': 'archived copy', 'zh': '存檔備份'}[lang], folder + '/' + lf)
        for lab, rel in _mirrors_of(folder, lf, lang):
            add(lab, rel)

    # 2. raw API payloads for this query, and their rendered mirrors
    if len(_apis):
        base = url.split('?')[0]
        for _, a in _apis.iterrows():
            ap = str(a['path'])
            if str(a['query_url']).split('?')[0] != base:
                continue
            add(t('art_raw', lang), ap)
            for lab, rel in _mirrors_of(os.path.dirname(ap), os.path.basename(ap), lang):
                add(lab, rel)

    # 3. the publisher's own dataset page, mirrored
    k = publisher_key(url)
    if k and k in _pub_by_key:
        pr = _pub_by_key[k]
        if isinstance(pr.get('pdf'), str) and pr['pdf']:
            add(t('art_pubpdf', lang), pr['pdf'])
        if isinstance(pr.get('png'), str) and pr['png']:
            add(t('art_pubpng', lang), pr['png'])
        if k == 'oecd_international_migration_database':
            add(t('art_oecdxml', lang), 'evidence/api/oecd/DSD_MIG_dataflow_metadata.xml')
            for _, a in _apis[_apis.path.astype(str).str.contains('oecd/%s_' % iso3, na=False)].iterrows():
                ap = str(a['path'])
                add(t('art_sdmx', lang) % os.path.basename(ap), ap)
                for lab, rel in _mirrors_of(os.path.dirname(ap), os.path.basename(ap), lang):
                    add(lab, rel)

    # 4. snapshots of the source web page
    for s in _snap_by.get((iso3, url), []):
        if isinstance(s['pdf_mirror'], str) and s['pdf_mirror']:
            add(t('art_pdfmirror', lang), 'evidence/countries/%s/%s' % (iso3, s['pdf_mirror']))
        if isinstance(s['png_screenshot'], str) and s['png_screenshot']:
            add(t('art_screenshot', lang), 'evidence/countries/%s/%s' % (iso3, s['png_screenshot']))
    return out


def artifact_links(iso3, url, local_file, lang, up=''):
    arts = artifacts(iso3, url, local_file, lang)
    return ''.join(filelink(up + rel, lab) for lab, rel in arts)
