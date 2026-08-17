# -*- coding: utf-8 -*-
"""Render every print-ready extract to PDF, so each number in the panel has a PDF mirror."""
import os, subprocess, sys, time
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(BASE, 'migration-data-archive')
PRINT = os.path.join(SITE, 'evidence', 'extracts')
CHROME = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
PROFILE = os.path.join(os.environ.get('TEMP', 'C:/Windows/Temp'), 'claude', 'chrome-extract')

jobs = []
for iso3 in sorted(os.listdir(PRINT)):
    d = os.path.join(PRINT, iso3)
    if not os.path.isdir(d):
        continue
    for f in sorted(os.listdir(d)):
        if f.endswith('.src.html'):
            jobs.append((iso3, f[:-9], os.path.join(d, f)))

print('rendering %d PDF extracts' % len(jobs))
t0 = time.time()
ok = fail = 0
for i, (iso3, var, src) in enumerate(jobs, 1):
    pdf = os.path.join(PRINT, iso3, var + '.pdf')
    if os.path.exists(pdf) and os.path.getsize(pdf) > 3000:
        ok += 1
        continue
    try:
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
                        '--user-data-dir=' + PROFILE, '--hide-scrollbars',
                        '--no-pdf-header-footer', '--virtual-time-budget=6000',
                        '--print-to-pdf=' + pdf, 'file:///' + src.replace('\\', '/')],
                       capture_output=True, timeout=90)
    except Exception:
        pass
    if os.path.exists(pdf) and os.path.getsize(pdf) > 3000:
        ok += 1
    else:
        fail += 1
        print('  FAILED %s %s' % (iso3, var))
    if i % 20 == 0:
        print('  %3d/%d  (%.0fs elapsed)' % (i, len(jobs), time.time() - t0))
        sys.stdout.flush()

print('\nrendered %d, failed %d, %.0fs total' % (ok, fail, time.time() - t0))

# remove the intermediate print sources once rendered
removed = 0
for iso3, var, src in jobs:
    pdf = os.path.join(PRINT, iso3, var + '.pdf')
    if os.path.exists(pdf) and os.path.getsize(pdf) > 3000 and os.path.exists(src):
        os.remove(src)
        removed += 1
print('cleaned up %d intermediate files' % removed)

tot = sum(os.path.getsize(os.path.join(r, f))
          for r, _, fs in os.walk(PRINT) for f in fs)
print('extracts folder: %.1f MB' % (tot / 1e6))
