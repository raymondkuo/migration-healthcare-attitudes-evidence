# -*- coding: utf-8 -*-
"""Recompute the SHA-256 manifest for every file the archive publishes."""
import os, hashlib, subprocess
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_here = os.path.dirname(os.path.abspath(__file__))
_parent = os.path.dirname(_here)
if os.path.isdir(os.path.join(_parent, 'data')) and os.path.isdir(os.path.join(_parent, 'evidence')):
    SITE = _parent          # scripts/ lives inside the published archive
else:
    SITE = os.path.join(BASE, 'migration-data-archive')


def _ignored(paths):
    """Paths git will not publish. The manifest must not promise a file the site
    does not serve, so anything .gitignore excludes is left out of it."""
    if not paths:
        return set()
    # NUL-separated, as bytes: with --stdin and text mode Windows turns every \n into
    # \r\n, git compares paths that end in \r, and nothing ever matches.
    data = ('\0'.join(paths) + '\0').encode('utf-8')
    try:
        p = subprocess.run(['git', '-C', SITE, 'check-ignore', '-z', '--stdin'],
                           input=data, capture_output=True, timeout=180)
    except Exception:
        return set()
    return {x.replace('\\', '/') for x in p.stdout.decode('utf-8').split('\0') if x}


rows = []
SKIP = {'__pycache__', '.git'}
candidates = []
for root, dirs, files in os.walk(SITE):
    dirs[:] = [d for d in dirs if d not in SKIP]
    if 'manifest' in os.path.relpath(root, SITE).split(os.sep):
        continue
    for f in files:
        candidates.append(os.path.relpath(os.path.join(root, f), SITE).replace('\\', '/'))

skipped = _ignored(candidates)
for rel in candidates:
    if rel in skipped:
        continue
    fp = os.path.join(SITE, rel.replace('/', os.sep))
    h = hashlib.sha256()
    with open(fp, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    rows.append(dict(path=rel, bytes=os.path.getsize(fp), sha256=h.hexdigest()))

d = pd.DataFrame(rows).sort_values('path')
d.to_csv(os.path.join(SITE, 'manifest', 'checksums.csv'), index=False, encoding='utf-8-sig')
print('files: %d   total: %.1f MB' % (len(d), d.bytes.sum() / 1e6))
print()
print(d.path.str.split('/').str[0].value_counts().to_string())
