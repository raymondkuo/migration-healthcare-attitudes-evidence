# -*- coding: utf-8 -*-
"""Check manifest/checksums.csv against the files git actually stored (HEAD).

Those are the bytes GitHub Pages serves. The check exists because the manifest was once built
from the working folder, whose text files have CRLF line endings on Windows while the served
files have LF, so no downloaded CSV or page could reproduce its recorded hash.

Run after committing. Exits 1 if any recorded hash differs from the committed file."""
import hashlib
import os
import subprocess
import sys

import pandas as pd

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ck = pd.read_csv(os.path.join(SITE, 'manifest', 'checksums.csv'))
ref = sys.argv[1] if len(sys.argv) > 1 else 'HEAD'

proc = subprocess.Popen(['git', '-C', SITE, 'cat-file', '--batch'], stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE)
bad, missing, ok = [], [], 0
for r in ck.itertuples():
    proc.stdin.write(('%s:%s\n' % (ref, r.path)).encode('utf-8'))
    proc.stdin.flush()
    head = proc.stdout.readline().decode('utf-8', 'replace').split()
    if len(head) < 3 or head[1] != 'blob':
        missing.append(r.path)
        continue
    data = proc.stdout.read(int(head[2]))
    proc.stdout.read(1)                                   # the newline after the blob
    if hashlib.sha256(data).hexdigest() == r.sha256 and len(data) == r.bytes:
        ok += 1
    else:
        bad.append(r.path)
proc.stdin.close()
proc.wait()

print('manifest rows: %d | match %s: %d | differ: %d | not in %s: %d'
      % (len(ck), ref, ok, len(bad), ref, len(missing)))
for p in bad[:20]:
    print('  DIFFERS  ' + p)
for p in missing[:20]:
    print('  MISSING  ' + p)
sys.exit(1 if bad else 0)
