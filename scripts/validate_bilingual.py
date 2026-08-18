# -*- coding: utf-8 -*-
"""Validate the bilingual archive: links, language pairing, cell linking, translation coverage."""
import os, re, sys, urllib.parse
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_here = os.path.dirname(os.path.abspath(__file__))
_parent = os.path.dirname(_here)
if os.path.isdir(os.path.join(_parent, 'data')) and os.path.isdir(os.path.join(_parent, 'evidence')):
    SITE = _parent
else:
    SITE = os.path.join(BASE, 'migration-data-archive-bilingual')
errors, warns, checked = [], [], 0

pages = [os.path.join(SITE, f) for f in sorted(os.listdir(SITE)) if f.endswith('.html')]
for sub in ('countries', 'evidence-pages'):
    d = os.path.join(SITE, sub)
    pages += [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith('.html')]
en = [p for p in pages if not p.endswith('.zh.html')]
zh = [p for p in pages if p.endswith('.zh.html')]
print('pages: %d total (%d EN, %d ZH)' % (len(pages), len(en), len(zh)))

CJK = re.compile(r'[一-鿿]')

for p in pages:
    h = open(p, encoding='utf-8', errors='replace').read()
    rel = os.path.relpath(p, SITE).replace('\\', '/')
    is_zh = p.endswith('.zh.html')
    # lang attribute
    want = 'zh-Hant-TW' if is_zh else 'en'
    if '<html lang="%s">' % want not in h:
        errors.append('%s: wrong or missing lang attribute (want %s)' % (rel, want))
    if '<title>' not in h:
        errors.append('%s: missing title' % rel)
    # every ZH page must actually contain Chinese
    if is_zh and len(CJK.findall(h)) < 40:
        errors.append('%s: looks untranslated (only %d CJK chars)' % (rel, len(CJK.findall(h))))
    # every EN page must have a switcher to its ZH twin and vice versa
    if 'class="langsw"' not in h:
        errors.append('%s: no language switcher' % rel)
    # links
    for m in re.finditer(r'(?:href|src)="([^"]+)"', h):
        href = m.group(1)
        if re.match(r'^(https?:|mailto:|#|data:|javascript:)', href, re.I):
            continue
        clean = urllib.parse.unquote(href.split('#')[0].split('?')[0])
        if not clean:
            continue
        checked += 1
        tgt = os.path.normpath(os.path.join(os.path.dirname(p), clean))
        if not os.path.exists(tgt):
            errors.append('%s -> broken link: %s' % (rel, href))
print('internal links checked: %d' % checked)

# ---- language pairing: each EN page has a ZH twin and the switcher resolves
for p in en:
    twin = p[:-5] + '.zh.html'
    if not os.path.exists(twin):
        errors.append('missing ZH twin: %s' % os.path.relpath(p, SITE))
for p in zh:
    twin = p[:-8] + '.html'
    if not os.path.exists(twin):
        errors.append('missing EN twin: %s' % os.path.relpath(p, SITE))

# ---- every panel value links to its evidence page, in both languages
panel = pd.read_csv(os.path.join(SITE, 'data', 'panel_final.csv'))
VARS = ['population', 'foreign_born', 'foreign_nationals', 'irregular_stock',
        'irregular_proxy_overstayers', 'irregular_proxy_detections',
        'irregular_proxy_absconded_workers']
cells = unlinked = 0
for lang, sfx in (('en', ''), ('zh', '.zh')):
    for iso in sorted(panel.iso3.unique()):
        fp = os.path.join(SITE, 'countries', '%s%s.html' % (iso, sfx))
        if not os.path.exists(fp):
            errors.append('missing country page %s %s' % (iso, lang)); continue
        h = open(fp, encoding='utf-8', errors='replace').read()
        g = panel[panel.iso3 == iso]
        for v in VARS:
            if v not in g:
                continue
            sub = g[g[v].notna()]
            if not len(sub):
                continue
            ev = os.path.join(SITE, 'evidence-pages', '%s__%s%s.html' % (iso, v, sfx))
            if not os.path.exists(ev):
                errors.append('missing evidence page %s %s %s' % (iso, v, lang))
            pdf = os.path.join(SITE, 'evidence', 'extracts', iso, '%s.pdf' % v)
            if not os.path.exists(pdf):
                errors.append('missing PDF extract %s %s' % (iso, v))
            for _, r in sub.iterrows():
                cells += 1
                if '../evidence-pages/%s__%s%s.html#y%d' % (iso, v, sfx, int(r['year'])) not in h:
                    unlinked += 1
                    if unlinked <= 5:
                        errors.append('%s%s.html: %s %d not linked' % (iso, sfx, v, int(r['year'])))
print('panel cells (both languages): %d | unlinked: %d' % (cells, unlinked))

# ---- row-level translations live beside the English, and must actually be filled in
for csvname, pairs in (('known_issues.csv', [('issue', 'issue_zh'), ('evidence', 'evidence_zh'),
                                             ('action', 'action_zh')]),
                       ('codebook.csv', [(1, 'definition_zh'), (2, 'caution_zh')])):
    fp = os.path.join(SITE, 'data', csvname)
    if not os.path.exists(fp):
        continue
    df = pd.read_csv(fp).fillna('')
    for en_col, zh_col in pairs:
        if zh_col not in df.columns:
            errors.append('%s: missing translation column %s' % (csvname, zh_col))
            continue
        en_s = df.iloc[:, en_col] if isinstance(en_col, int) else df[en_col]
        for i in range(len(df)):
            if str(en_s.iloc[i]).strip() and not str(df[zh_col].iloc[i]).strip():
                errors.append('%s row %d: %s is filled but %s is empty'
                              % (csvname, i,
                                 en_col if isinstance(en_col, str) else 'col%d' % en_col, zh_col))

# ---- translation spot-checks: ZH pages must not leak key English UI strings
LEAK = ['Panel data', 'Verification', 'Data quality by variable', 'All archived files',
        'Sources</h2>', 'Every number below is a link']
for p in zh:
    h = open(p, encoding='utf-8', errors='replace').read()
    body = h.split('</header>', 1)[-1].split('<footer', 1)[0]
    for s in LEAK:
        if s in body:
            warns.append('%s: untranslated string "%s"' % (os.path.relpath(p, SITE), s))

print('\n%d errors, %d warnings' % (len(errors), len(warns)))
for e in errors[:30]:
    print('  ERROR  ' + e)
for w in warns[:12]:
    print('  warn   ' + w)
sys.exit(1 if errors else 0)
