# -*- coding: utf-8 -*-
"""V-Dem liberal democracy index for every panel country, 2001-2022 (the years of the population and
migrant series).

Source
  V-Dem Country-Year Dataset v16 (Coppedge et al. 2026, https://doi.org/10.23696/vdemds26), variable
  v2x_libdem, read from the V-Dem Institute's own data file: data/vdem.RData of its R package vdemdata
  16.0 ("v16 release", commit f4dd269 of github.com/vdeminstitute/vdemdata, 2026-03-17). The download
  on v-dem.net asks for an e-mail address and consent to a privacy policy, so the archive takes the
  same dataset from the institute's GitHub package, pinned to the release commit; the file's git blob
  hash is checked against the one GitHub records for that commit. Definitions, the 68% interval
  (codelow/codehigh) and the annual aggregation (day-weighted mean) are quoted from the V-Dem
  Codebook v16 and from the package's own codebook entry.
  Checked cell by cell against Our World in Data's copy of V-Dem v16 (grapher liberal-democracy-index):
  a value is used only if the two agree at V-Dem's three decimals.

Usage
  python scripts/92_collect_vdem.py           parse the archived files only
  python scripts/92_collect_vdem.py --fetch   download them first, and render the mirrors, page
                                              extracts and publisher pages

Needs R (Rscript) to read the R data file: scripts/92_decode_vdem.R does the decoding, base R only.
Writes data/extension_staging/vdem_cells.csv in the collectors' cell format (not read by
74_assemble_panel.py; 93_add_vdem.py puts the cells into the panel) and
data/vdem_source_comparison.csv (V-Dem value, interval and standard deviation, and Our World in Data's
value, side by side).
"""
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ext_lib as L                                    # noqa: E402
import vdem_texts as VT                                # noqa: E402

SITE = os.path.dirname(HERE)
D = os.path.join(SITE, 'data')
API = os.path.join(SITE, 'evidence', 'api')
PUB = os.path.join(API, 'publisher_pages')
COLLECTED = VT.WHEN
YEARS = list(range(2001, 2023))
VAR = VT.VAR
COMMIT = VT.COMMIT

GH = 'https://raw.githubusercontent.com/vdeminstitute/vdemdata/%s/' % COMMIT
VD_URL = GH + 'data/vdem.RData'
VD_FILE = 'vdem_v16_vdemdata_vdem_retrieved_%s.RData' % COLLECTED
VD_CB_URL = GH + 'data/codebook.RData'
VD_CB = 'vdem_v16_vdemdata_codebook_retrieved_%s.RData' % COLLECTED
VD_DESC_URL = GH + 'DESCRIPTION'
VD_DESC = 'vdem_v16_vdemdata_DESCRIPTION_retrieved_%s.txt' % COLLECTED
VD_COMMIT_URL = 'https://api.github.com/repos/vdeminstitute/vdemdata/commits/%s' % COMMIT
VD_COMMIT = 'vdem_v16_vdemdata_commit_%s_retrieved_%s.json' % (COMMIT[:7], COLLECTED)
VD_TREE_URL = 'https://api.github.com/repos/vdeminstitute/vdemdata/contents/data?ref=%s' % COMMIT
VD_TREE = 'vdem_v16_vdemdata_data_folder_%s_retrieved_%s.json' % (COMMIT[:7], COLLECTED)
CB_PDF_URL = 'https://v-dem.net/documents/70/codebook_v16.pdf'
CB_PDF = 'vdem_codebook_v16_retrieved_%s.pdf' % COLLECTED
CB_PAGES = {29: 'suggested citation (dataset DOI)', 32: 'codelow/codehigh: the 68 percent interval',
            42: 'country-year aggregation: day-weighted mean', 48: 'liberal democracy index (v2x_libdem)'}
OWID_URL = ('https://ourworldindata.org/grapher/liberal-democracy-index.csv?v=1&csvType=full'
            '&useColumnShortNames=true')
OWID_FILE = 'owid_liberal-democracy-index_retrieved_%s.csv' % COLLECTED
OWID_META_URL = ('https://ourworldindata.org/grapher/liberal-democracy-index.metadata.json?v=1&csvType=full'
                 '&useColumnShortNames=true')
OWID_META = 'owid_liberal-democracy-index_metadata_retrieved_%s.json' % COLLECTED
OWID_COL = 'libdem_vdem__estimate_best'

VD_NAME = ('V-Dem Institute, V-Dem Country-Year Dataset v16 (Coppedge et al. 2026, %s): liberal democracy index '
           '(v2x_libdem), from the institute\'s R data package vdemdata 16.0 (data/vdem.RData)' % VT.DOI)
REF = 'Calendar year (day-weighted mean of V-Dem\'s country-date scores)'
NOTE = ('V-Dem liberal democracy index (v2x_libdem): "To what extent is the ideal of liberal democracy achieved?", '
        'interval scale from 0 (low) to 1 (high); it combines the electoral democracy index (v2x_polyarchy) with the '
        'liberal component index (v2x_liberal) as .25*polyarchy^1.585 + .25*liberal + .5*polyarchy^1.585*liberal. An '
        'estimate from V-Dem\'s Bayesian measurement model of expert ratings, published to three decimals with a 68%% '
        'interval (v2x_libdem_codelow/codehigh, in data/vdem_source_comparison.csv). Definition, interval and annual '
        'aggregation: V-Dem Codebook v16, PDF pages 48, 32 and 42 (evidence/api/%s).' % CB_PDF)
PUBLISHER_PAGES = [
    dict(key='vdem_dataset_v16', publisher='V-Dem Institute',
         dataset='The V-Dem Dataset: Country-Year V-Dem Core and Full+Others v16, with the codebook v16',
         page_url='https://v-dem.net/data/the-v-dem-dataset/', backs_payload=VD_FILE),
    dict(key='vdemdata_github_v16', publisher='V-Dem Institute',
         dataset='vdemdata R package (github.com/vdeminstitute/vdemdata) at the v16 release commit %s' % COMMIT[:7],
         page_url='https://github.com/vdeminstitute/vdemdata/tree/%s' % COMMIT, backs_payload=VD_FILE),
    dict(key='owid_liberal_democracy_index', publisher='Our World in Data',
         dataset='Liberal Democracy Index (V-Dem v16, processed by Our World in Data)',
         page_url='https://ourworldindata.org/grapher/liberal-democracy-index', backs_payload=OWID_FILE),
]

P = pd.read_csv(os.path.join(D, 'panel_final.csv'), usecols=['iso3', 'year'])
ISO = sorted(P.iso3.unique())
FETCH = '--fetch' in sys.argv


def fetch(url, dest, accept=None, minimum=500):
    code, size = L.download(url, dest, accept=accept)
    print('%-72s http %s %12s bytes' % (os.path.basename(dest)[:72], code, format(size, ',')))
    if code != '200' or size < minimum:
        sys.exit('download failed: ' + url)
    return size


def upsert(path, rows, key):
    df = pd.read_csv(path)
    new = pd.DataFrame(rows)
    keep = df[~df[key].isin(new[key])]
    pd.concat([keep, new], ignore_index=True)[list(df.columns)].to_csv(path, index=False,
                                                                        encoding='utf-8-sig')


def git_blob_sha(path):
    """The hash git (and GitHub) gives a file: sha1 of 'blob <size>\\0' + content."""
    h = hashlib.sha1()
    h.update(b'blob %d\0' % os.path.getsize(path))
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def rscript():
    found = shutil.which('Rscript') or shutil.which('Rscript.exe')
    if not found:
        cands = sorted(glob.glob(r'C:\Program Files\R\R-*\bin\Rscript.exe'))
        found = cands[-1] if cands else None
    if not found:
        sys.exit('Rscript not found: R is needed to read the V-Dem data file (scripts/92_decode_vdem.R)')
    return found


if FETCH:
    new = []
    for f, url, desc, pub, acc in (
            (VD_FILE, VD_URL, 'V-Dem Country-Year Dataset v16 (all variables, all countries and years) as published in '
                              'the V-Dem Institute\'s R package vdemdata 16.0, file data/vdem.RData at the v16 release '
                              'commit %s; read with R (scripts/92_decode_vdem.R)' % COMMIT[:7], 'V-Dem Institute', None),
            (VD_CB, VD_CB_URL, 'The package\'s machine-readable codebook (data/codebook.RData): name, question, '
                               'clarification, scale and country-year aggregation of every V-Dem variable',
             'V-Dem Institute', None),
            (VD_DESC, VD_DESC_URL, 'The package\'s DESCRIPTION file at the release commit: package name, version 16.0 '
                                   'and what it contains', 'V-Dem Institute', None),
            (VD_COMMIT, VD_COMMIT_URL, 'GitHub API record of the release commit %s ("v16 release"): its date and '
                                       'message' % COMMIT[:7], 'GitHub (V-Dem Institute repository)',
             'application/vnd.github+json'),
            (VD_TREE, VD_TREE_URL, 'GitHub API listing of the package\'s data folder at the release commit: the size '
                                   'and git blob hash of vdem.RData and codebook.RData, against which the archived files '
                                   'are checked', 'GitHub (V-Dem Institute repository)', 'application/vnd.github+json'),
            (OWID_FILE, OWID_URL, 'Our World in Data, Liberal Democracy Index (V-Dem v16), all countries and years, '
                                  'CSV; a copy of V-Dem v16, the check of the V-Dem values', 'Our World in Data', 'text/csv'),
            (OWID_META, OWID_META_URL, 'Our World in Data metadata of the chart: title, source (V-Dem v16), citation '
                                       'and last update', 'Our World in Data', 'application/json')):
        dest = os.path.join(API, f)
        size = fetch(url, dest, acc)
        if f.endswith('.json'):
            json.load(open(dest, encoding='utf-8-sig'))                 # must parse
        new.append(dict(file=f, publisher=pub, description=desc, query_url=url, bytes=size,
                        path='evidence/api/' + f))
    upsert(os.path.join(D, 'api_snapshots.csv'), new, 'file')
    fetch(CB_PDF_URL, os.path.join(API, CB_PDF), 'application/pdf', minimum=100000)

# ------------------------------------------------------------------ provenance of the data file
commit = json.load(open(os.path.join(API, VD_COMMIT), encoding='utf-8-sig'))
assert commit['sha'] == COMMIT, commit['sha']
assert commit['commit']['message'].strip().startswith('v16 release'), commit['commit']['message']
released = commit['commit']['committer']['date'][:10]
assert released == VT.RELEASED, released
tree = {x['name']: x for x in json.load(open(os.path.join(API, VD_TREE), encoding='utf-8-sig'))}
for f, name in ((VD_FILE, 'vdem.RData'), (VD_CB, 'codebook.RData')):
    p = os.path.join(API, f)
    assert os.path.getsize(p) == tree[name]['size'], (f, os.path.getsize(p), tree[name]['size'])
    assert git_blob_sha(p) == tree[name]['sha'], (f, 'git blob hash differs from GitHub\'s')
desc = open(os.path.join(API, VD_DESC), encoding='utf-8').read()
assert re.search(r'^Package: vdemdata$', desc, re.M) and re.search(r'^Version: 16\.0$', desc, re.M), desc[:200]
print('vdemdata %s: release commit %s of %s; vdem.RData and codebook.RData match GitHub\'s size and git blob hash'
      % ('16.0', COMMIT[:7], released))

# ------------------------------------------------------------------ the codebook (PDF and the package's own entry)
import fitz                                              # noqa: E402

doc = fitz.open(os.path.join(API, CB_PDF))
pg = {n: re.sub(r'\s+', ' ', doc[n - 1].get_text()) for n in CB_PAGES}
doc.close()
assert 'Liberal democracy index (D) (v2x_libdem)' in pg[48] and 'Day-weighted mean' in pg[48], 'p48'
assert 'Interval, from low to high (0-1)' in pg[48], 'p48 scale'
assert 'doi.org/10.23696/vdemds26' in pg[29] and 'Dataset v16' in pg[29], 'p29'
assert '68 percent of the probability mass' in pg[32], 'p32'
assert 'High-Level/Mid-Level Democracy indices are aggregated' in pg[42] and 'day-weighted mean' in pg[42], 'p42'

# ------------------------------------------------------------------ decode the data file with R
tmp = tempfile.mkdtemp(prefix='vdem_')
out_csv, cb_csv = os.path.join(tmp, 'v2x_libdem.csv'), os.path.join(tmp, 'codebook_entry.csv')
r = subprocess.run([rscript(), '--vanilla', os.path.join(HERE, '92_decode_vdem.R'), os.path.join(API, VD_FILE),
                    os.path.join(API, VD_CB), ','.join(ISO), str(YEARS[0]), str(YEARS[-1]), out_csv, cb_csv],
                   capture_output=True, text=True)
print(r.stdout.strip())
if r.returncode != 0:
    sys.exit('R failed: ' + r.stderr[-2000:])
vd = pd.read_csv(out_csv, dtype=str, keep_default_na=False)
cbe = dict(pd.read_csv(cb_csv, dtype=str, keep_default_na=False).values)
shutil.rmtree(tmp)
assert cbe['name'] == 'Liberal democracy index' and cbe['tag'] == 'v2x_libdem', cbe
assert cbe['cy_aggregation'] == 'Day-weighted mean' and cbe['scale'] == 'Interval, from low to high (0-1).', cbe
assert '16' in cbe['datarelease'], cbe['datarelease']
vdem = {(x.country_text_id, int(x.year)): x for x in vd.itertuples()}

# ------------------------------------------------------------------ Our World in Data's copy
meta = json.load(open(os.path.join(API, OWID_META), encoding='utf-8-sig'))
ocol = meta['columns'][OWID_COL]
assert 'Democracy report v16' in ocol['citationLong'] or 'v16' in ocol['citationLong'], ocol['citationLong']
owid_df = pd.read_csv(os.path.join(API, OWID_FILE))
owid = {(x.code, int(x.year)): float(getattr(x, OWID_COL)) for x in owid_df.itertuples()
        if isinstance(x.code, str) and 2001 <= x.year <= 2022}

rows, compared, agree, mismatch = [], 0, 0, []
for iso in ISO:
    for y in YEARS:
        x = vdem.get((iso, y))
        if x is None or x.v2x_libdem == '':
            sys.exit('no V-Dem value for %s %d' % (iso, y))
        v = float(x.v2x_libdem)
        assert round(v, 3) == v, (iso, y, x.v2x_libdem)                # published to three decimals
        assert float(x.v2x_libdem_codelow) <= v <= float(x.v2x_libdem_codehigh), (iso, y)
        o = owid.get((iso, y))
        compared += 1
        if o is not None and round(o, 3) == round(v, 3):
            agree += 1
        else:
            mismatch.append((iso, y, v, o))
            continue                          # used only where the two agree
        rows.append(L.cell(
            iso, y, VAR, v, 'VDEM_V16_V2X_LIBDEM', VD_NAME, VD_URL, 'evidence/api/' + VD_FILE, REF, 'A',
            VT.SOURCE_TYPE, note=NOTE, flag='',
            verification=('Read directly from the archived V-Dem v16 data file (evidence/api/%s: data/vdem.RData of the '
                          'V-Dem Institute\'s R package vdemdata 16.0, release commit %s of %s, git blob hash as GitHub '
                          'records it), decoded with R (scripts/92_decode_vdem.R); Our World in Data\'s copy of V-Dem '
                          'v16 (evidence/api/%s) gives the same value at V-Dem\'s three decimals. Retrieved %s.'
                          % (VD_FILE, COMMIT[:7], released, OWID_FILE, COLLECTED)),
            collected_on=COLLECTED))
print('V-Dem vs Our World in Data: %d cells compared, %d agree at three decimals, %d differ'
      % (compared, agree, len(mismatch)))
assert not mismatch, mismatch[:5]
assert compared == len(ISO) * len(YEARS)

out = L.write_stage('vdem_cells.csv', rows)
print('cells written: %d (%d countries x %d years)' % (len(out), len(ISO), len(YEARS)))

cmp_rows = []
for iso in ISO:
    for y in YEARS:
        x = vdem[(iso, y)]
        o = owid.get((iso, y))
        cmp_rows.append(dict(
            iso3=iso, year=y, vdem_country_name=x.country_name, v2x_libdem=repr(float(x.v2x_libdem)),
            v2x_libdem_codelow=repr(float(x.v2x_libdem_codelow)), v2x_libdem_codehigh=repr(float(x.v2x_libdem_codehigh)),
            v2x_libdem_sd=repr(float(x.v2x_libdem_sd)), owid_value='' if o is None else repr(o),
            owid_same='' if o is None else ('yes' if round(o, 3) == round(float(x.v2x_libdem), 3) else 'no'),
            used_value=repr(float(x.v2x_libdem))))
pd.DataFrame(cmp_rows).to_csv(VT.CMP, index=False, encoding='utf-8-sig')

# ------------------------------------------------------------------ mirrors, extracts, publisher pages
if FETCH:
    mirrors = []
    g_vd = {iso: {y: float(vdem[(iso, y)].v2x_libdem) for y in YEARS} for iso in ISO}
    base = os.path.join(API, 'MIRROR__' + os.path.splitext(VD_FILE)[0])
    made = L.grid_mirror('V-Dem v16 - liberal democracy index (v2x_libdem), 0-1',
                         'Archived file %s (data/vdem.RData of vdemdata 16.0, commit %s), decoded with R. Retrieved %s. '
                         '%d panel countries, values as published (three decimals).'
                         % (VD_FILE, COMMIT[:7], COLLECTED, len(g_vd)), g_vd, YEARS, base,
                         fmt=lambda v: '%.3f' % v,
                         note='The R data file holds the whole V-Dem dataset (%s); this grid shows the one variable the '
                              'panel takes from it, for its countries and years. The 68%% interval and standard deviation '
                              'of each value are in data/vdem_source_comparison.csv. Rendered %s.'
                              % ('all countries, 1789-2025', COLLECTED))
    mirrors.append(dict(scope='API', folder='evidence/api', source_file=VD_FILE,
                        mirrors=';'.join(os.path.basename(m) for m in made), n_mirrors=len(made)))
    g_ow = {iso: {y: owid[(iso, y)] for y in YEARS if (iso, y) in owid} for iso in ISO}
    base = os.path.join(API, 'MIRROR__' + os.path.splitext(OWID_FILE)[0])
    made = L.grid_mirror('Our World in Data - Liberal Democracy Index (V-Dem v16), 0-1',
                         'Query: %s. Retrieved %s. %d panel countries, values as published.'
                         % (OWID_URL, COLLECTED, len(g_ow)), g_ow, YEARS, base, fmt=lambda v: '%.3f' % v)
    mirrors.append(dict(scope='API', folder='evidence/api', source_file=OWID_FILE,
                        mirrors=';'.join(os.path.basename(m) for m in made), n_mirrors=len(made)))
    dfields = [(m_.group(1), m_.group(2).strip()) for m_ in re.finditer(r'^([A-Za-z@]+):\s*(.*(?:\n[ \t].*)*)', desc, re.M)
               if m_.group(1) in ('Package', 'Type', 'Title', 'Version', 'Description', 'License')]
    for rel, title, header, trows, src in (
            (VD_CB, 'vdemdata 16.0 codebook.RData - entry v2x_libdem', ['Field', 'Value'],
             [([k_, v_], k_ in ('name', 'question', 'scale', 'cy_aggregation')) for k_, v_ in cbe.items()], VD_CB_URL),
            (VD_DESC, 'vdemdata DESCRIPTION at the v16 release commit', ['Field', 'Value'],
             [([k_, re.sub(r'\s+', ' ', v_)], k_ in ('Package', 'Version', 'Description')) for k_, v_ in dfields],
             VD_DESC_URL),
            (VD_COMMIT, 'GitHub API - commit %s of vdeminstitute/vdemdata' % COMMIT[:7], ['Field', 'Value'],
             [(['sha', commit['sha']], True), (['committer date', commit['commit']['committer']['date']], True),
              (['message', commit['commit']['message']], True),
              (['files changed', ', '.join(x['filename'] for x in commit.get('files', []))], False)], VD_COMMIT_URL),
            (VD_TREE, 'GitHub API - data folder of vdeminstitute/vdemdata at commit %s' % COMMIT[:7],
             ['File', 'Size (bytes)', 'git blob hash'],
             [([x['name'], format(x['size'], ','), x['sha']], x['name'] in ('vdem.RData', 'codebook.RData'))
              for x in tree.values()], VD_TREE_URL),
            (OWID_META, 'Our World in Data - metadata of the Liberal Democracy Index chart', ['Field', 'Value'],
             [(['title', meta['chart'].get('title', '')], True), (['subtitle', meta['chart'].get('subtitle', '')], False),
              (['column', OWID_COL], True), (['citationLong', ocol.get('citationLong', '')], True),
              (['lastUpdated', str(ocol.get('lastUpdated', ''))], True), (['timespan', str(ocol.get('timespan', ''))], False)],
             OWID_META_URL)):
        mb = os.path.join(API, 'MIRROR__' + os.path.splitext(rel)[0])
        L.table_extract(title, header, trows, mb, 'Archived file %s from %s, retrieved %s.' % (rel, src, COLLECTED),
                        note='The fields of the archived file, unchanged%s. Rendered %s.'
                             % (' (decoded with R)' if rel.endswith('.RData') else '', COLLECTED))
        mirrors.append(dict(scope='API', folder='evidence/api', source_file=rel,
                            mirrors='%s;%s' % (os.path.basename(mb + '.pdf'), os.path.basename(mb + '.png')),
                            n_mirrors=2))
    made = []
    for n_ in sorted(CB_PAGES):
        made += L.page_extract(os.path.join(API, CB_PDF), n_,
                               os.path.join(API, 'MIRROR__%s__p%d' % (os.path.splitext(CB_PDF)[0], n_)))
    mirrors.append(dict(scope='API', folder='evidence/api', source_file=CB_PDF,
                        mirrors=';'.join(os.path.basename(m) for m in made), n_mirrors=len(made)))
    sm = os.path.join(D, 'source_mirrors.csv')
    old = pd.read_csv(sm)
    old = old[~(old.source_file.isin([m['source_file'] for m in mirrors]))]
    pd.concat([old, pd.DataFrame(mirrors)], ignore_index=True).to_csv(sm, index=False, encoding='utf-8-sig')

    pubrows = []
    for p in PUBLISHER_PAGES:
        b = os.path.join(PUB, p['key'])
        made = L.chrome_render(p['page_url'], pdf=b + '.pdf', png=b + '.png', wait_ms=20000)
        note = ''
        if b + '.pdf' in made and b + '.png' in made:
            d_ = fitz.open(b + '.pdf')
            chars = sum(len(x.get_text().strip()) for x in d_)
            d_.close()
            if chars < 500:
                # GitHub's print layout keeps only the page header; the PDF is then made from the screenshot
                img = fitz.open(b + '.png')
                pdfb = img.convert_to_pdf()
                img.close()
                open(b + '.pdf', 'wb').write(pdfb)
                note = ('The page prints only its header in a headless browser, so the PDF holds the screenshot taken '
                        'on %s.' % COLLECTED)
        pubrows.append(dict(p, status='captured' if len(made) == 2 else 'partial',
                            pdf='evidence/api/publisher_pages/%s.pdf' % p['key'] if b + '.pdf' in made else '',
                            png='evidence/api/publisher_pages/%s.png' % p['key'] if b + '.png' in made else '',
                            pdf_bytes=os.path.getsize(b + '.pdf') if b + '.pdf' in made else 0,
                            png_bytes=os.path.getsize(b + '.png') if b + '.png' in made else 0,
                            captured=COLLECTED, note=note))
        print('publisher page %-30s %s' % (p['key'], [os.path.basename(m) for m in made]))
    upsert(os.path.join(D, 'api_publisher_snapshots.csv'), pubrows, 'key')
