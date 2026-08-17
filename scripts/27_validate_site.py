# -*- coding: utf-8 -*-
"""Validate the archive site: every internal link resolves, every panel value is
represented, and the checksum manifest is complete and correct."""
import os, re, sys, hashlib, urllib.parse
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(BASE, 'migration-data-archive')
errors, warns, checked = [], [], 0

# ---------------------------------------------------------------- 1. links
# only the generated site pages; evidence/ holds archived source HTML, not site pages
pages = [os.path.join(SITE, f) for f in sorted(os.listdir(SITE)) if f.endswith('.html')]
for sub in ('countries', 'evidence-pages'):
    d = os.path.join(SITE, sub)
    if os.path.isdir(d):
        pages += [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith('.html')]
print('site pages: %d' % len(pages))

for p in pages:
    h = open(p, encoding='utf-8', errors='replace').read()
    rel = os.path.relpath(p, SITE).replace('\\', '/')
    if '<!doctype html>' not in h.lower():
        errors.append('%s: missing doctype' % rel)
    if '<title>' not in h:
        errors.append('%s: missing title' % rel)
    if 'assets/style.css' not in h:
        errors.append('%s: stylesheet not linked' % rel)
    for m in re.finditer(r'(?:href|src)="([^"]+)"', h):
        href = m.group(1)
        if re.match(r'^(https?:|mailto:|#|data:|javascript:)', href, re.I):
            continue
        clean = urllib.parse.unquote(href.split('#')[0].split('?')[0])
        if not clean:
            continue
        checked += 1
        target = os.path.normpath(os.path.join(os.path.dirname(p), clean))
        if not os.path.exists(target):
            errors.append('%s -> broken link: %s' % (rel, href))

print('internal links checked: %d' % checked)

# ---------------------------------------------------------------- 2. coverage
panel = pd.read_csv(os.path.join(SITE, 'data', 'panel_final.csv'))
isos = sorted(panel.iso3.unique())
for iso in isos:
    p = os.path.join(SITE, 'countries', '%s.html' % iso)
    if not os.path.exists(p):
        errors.append('missing country page: %s' % iso)
        continue
    h = open(p, encoding='utf-8', errors='replace').read()
    g = panel[panel.iso3 == iso]
    # spot-check: the largest population value must appear formatted in the page
    v = g['population'].max()
    if pd.notna(v) and format(float(v), ',.0f') not in h:
        errors.append('%s.html: population value %s not rendered' % (iso, format(v, ',.0f')))
if len(isos) != 40:
    errors.append('expected 40 countries, found %d' % len(isos))

# every country referenced from the index
ch = open(os.path.join(SITE, 'countries.html'), encoding='utf-8').read()
for iso in isos:
    if 'countries/%s.html' % iso not in ch:
        errors.append('countries.html does not link %s' % iso)

# ---- every non-null panel value must link to an existing evidence page and PDF extract
VARS = ['population', 'foreign_born', 'foreign_nationals', 'irregular_stock',
        'irregular_proxy_overstayers', 'irregular_proxy_detections',
        'irregular_proxy_absconded_workers']
cells = missing_ev = missing_pdf = unlinked = 0
for iso in isos:
    h = open(os.path.join(SITE, 'countries', '%s.html' % iso), encoding='utf-8', errors='replace').read()
    g = panel[panel.iso3 == iso]
    for v in VARS:
        if v not in g:
            continue
        sub = g[g[v].notna()]
        if not len(sub):
            continue
        ev = os.path.join(SITE, 'evidence-pages', '%s__%s.html' % (iso, v))
        pdf = os.path.join(SITE, 'evidence', 'extracts', iso, '%s.pdf' % v)
        if not os.path.exists(ev):
            errors.append('missing evidence page: %s %s' % (iso, v)); missing_ev += 1
        if not os.path.exists(pdf):
            errors.append('missing PDF extract: %s %s' % (iso, v)); missing_pdf += 1
        for _, r in sub.iterrows():
            cells += 1
            if '../evidence-pages/%s__%s.html#y%d' % (iso, v, int(r['year'])) not in h:
                unlinked += 1
                if unlinked <= 5:
                    errors.append('%s.html: %s %d value not linked to its evidence'
                                  % (iso, v, int(r['year'])))
print('panel cells: %d | unlinked: %d | missing evidence pages: %d | missing PDF extracts: %d'
      % (cells, unlinked, missing_ev, missing_pdf))

# ---------------------------------------------------------------- 3. evidence present
reg = pd.read_csv(os.path.join(SITE, 'data', 'source_register.csv'))
snaps = pd.read_csv(os.path.join(SITE, 'data', 'web_snapshots.csv'))
miss = 0
for _, r in snaps.iterrows():
    for c in ('pdf_mirror', 'png_screenshot'):
        f = r[c]
        if isinstance(f, str) and f:
            if not os.path.exists(os.path.join(SITE, 'evidence', 'countries', r['iso3'], f)):
                errors.append('snapshot missing on disk: %s/%s' % (r['iso3'], f))
                miss += 1
apis = pd.read_csv(os.path.join(SITE, 'data', 'api_snapshots.csv'))
for _, a in apis.iterrows():
    if not os.path.exists(os.path.join(SITE, a['path'].replace('/', os.sep))):
        errors.append('API snapshot missing: %s' % a['path'])

# ---------------------------------------------------------------- 4. checksums
ck = pd.read_csv(os.path.join(SITE, 'manifest', 'checksums.csv'))
have = set(ck.path)
on_disk = set()
SKIP = {'__pycache__', '.git'}
for root, dirs, files in os.walk(SITE):
    dirs[:] = [d for d in dirs if d not in SKIP]
    if 'manifest' in os.path.relpath(root, SITE).split(os.sep):
        continue
    for f in files:
        on_disk.add(os.path.relpath(os.path.join(root, f), SITE).replace('\\', '/'))
missing = on_disk - have
extra = have - on_disk
if missing:
    warns.append('%d files on disk not in checksums.csv (regenerate)' % len(missing))
if extra:
    warns.append('%d checksum entries no longer on disk (regenerate)' % len(extra))

# verify a sample of hashes
import random
random.seed(0)
sample = random.sample(sorted(have & on_disk), min(25, len(have & on_disk)))
bad = 0
for rel in sample:
    h = hashlib.sha256()
    with open(os.path.join(SITE, rel.replace('/', os.sep)), 'rb') as fh:
        for c in iter(lambda: fh.read(1 << 20), b''):
            h.update(c)
    exp = ck[ck.path == rel]['sha256'].iloc[0]
    if h.hexdigest() != exp:
        bad += 1
        warns.append('checksum mismatch (stale manifest): %s' % rel)

# ---------------------------------------------------------------- report
print('\n%d errors, %d warnings' % (len(errors), len(warns)))
for e in errors[:40]:
    print('  ERROR  ' + e)
for w in warns[:15]:
    print('  warn   ' + w)
sys.exit(1 if errors else 0)
