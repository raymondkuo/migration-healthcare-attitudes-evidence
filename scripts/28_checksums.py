# -*- coding: utf-8 -*-
"""Recompute the SHA-256 manifest for every file in the archive."""
import os, hashlib
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_here = os.path.dirname(os.path.abspath(__file__))
_parent = os.path.dirname(_here)
if os.path.isdir(os.path.join(_parent, 'data')) and os.path.isdir(os.path.join(_parent, 'evidence')):
    SITE = _parent          # scripts/ lives inside the published archive
else:
    SITE = os.path.join(BASE, 'migration-data-archive')


rows = []
SKIP = {'__pycache__', '.git'}
for root, dirs, files in os.walk(SITE):
    dirs[:] = [d for d in dirs if d not in SKIP]
    if 'manifest' in os.path.relpath(root, SITE).split(os.sep):
        continue
    for f in files:
        fp = os.path.join(root, f)
        rel = os.path.relpath(fp, SITE).replace('\\', '/')
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
