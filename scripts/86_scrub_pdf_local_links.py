# -*- coding: utf-8 -*-
"""Remove local-file link targets from every PDF in the archive (2026-10-17).

PDF mirrors of archived web pages were rendered by Chrome from the copy on disk. Chrome resolves a
page's relative links against the folder the copy was opened from, so the link annotations of
those PDFs held absolute file:/// paths of the build machine - and the workspace folder is named
after a co-author of the study, so the paths put a person's name (percent-encoded, in one case
twice, inside a share link) into published files. scripts/62_scrub_local_paths.py removed the
same paths from the text files; PDFs were not covered.

The links never worked for a reader (they point at a drive that does not exist for them). They are
deleted; the visible page is unchanged. Each PDF that had one is rewritten without the old objects,
and every PDF is then searched, raw and inside its compressed streams, for any trace of the path.
ext_lib.chrome_render and 45_build_source_mirrors.py now scrub what they render, so new mirrors do
not reintroduce it. Idempotent: a second run finds nothing to remove.
"""
import os
import re
import subprocess
import sys
import urllib.parse
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ext_lib as L                                    # noqa: E402

SITE = os.path.dirname(HERE)
# written as code points so that this published script does not carry the string it removes
NAME = ''.join(chr(c) for c in (0x8449, 0x660E, 0x53E1))
DIR = ''.join(chr(c) for c in (0x7814, 0x7A76, 0x8A08, 0x756B))        # the top folder of the path
NEEDLES = []
for s in (NAME, DIR):
    q = urllib.parse.quote(s)
    NEEDLES += [s.encode('utf-8'), s.encode('utf-16-be'), s.encode('utf-16-le'), q.encode(),
                q.lower().encode(), urllib.parse.quote(q).encode()]
NEEDLES += [b'claude-work', b'file:///D:', b'file:///C:']


def traces(path):
    b = open(path, 'rb').read()
    found = {n for n in NEEDLES if n in b}
    for m in re.finditer(rb'stream\r?\n(.*?)\r?\nendstream', b, re.S):
        try:
            d = zlib.decompress(m.group(1))
        except Exception:
            continue
        found |= {n for n in NEEDLES if n in d}
    return found


listed = subprocess.run(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '*.pdf'],
                        cwd=SITE, capture_output=True).stdout.decode('utf-8').splitlines()
pdfs = sorted(p for p in listed if os.path.isfile(os.path.join(SITE, p)))
removed = {}
for p in pdfs:
    n = L.scrub_local_links(os.path.join(SITE, p))
    if n:
        removed[p] = n
left = {p: t for p in pdfs for t in [traces(os.path.join(SITE, p))] if t}
print('PDFs searched: %d | PDFs with local links removed: %d (%d links)'
      % (len(pdfs), len(removed), sum(removed.values())))
for p, n in sorted(removed.items()):
    print('   %4d  %s' % (n, p))
if left:
    print('TRACES REMAIN:')
    for p, t in left.items():
        print('   ', p, sorted(t)[:3])
    sys.exit(1)
print('no PDF carries the local path, raw or inside a compressed stream')
