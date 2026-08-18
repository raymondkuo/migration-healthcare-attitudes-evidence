# -*- coding: utf-8 -*-
"""Re-run the reproduction test for Eurostat migr_eipre against the CORRECTED panel.

The original verification log records the input workbooks as received, before any
correction. This adds a second stage: the same test re-run against the values the
archive now publishes, so both the finding and the current state are visible.
"""
import os, json, shutil
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(BASE, 'migration-data-archive')
BIL = os.path.join(BASE, 'migration-data-archive-bilingual')
D = os.path.join(SITE, 'data')
RAW = os.path.join(BASE, 'data_raw', 'reverify')
ACCESS = '2026-08-17'

# ---------------------------------------------------------------- live data
d = json.load(open(os.path.join(RAW, 'eurostat_migr_eipre_REVERIFY.json'), encoding='utf-8'))
ids, size = d['id'], d['size']
idx = {k: d['dimension'][k]['category']['index'] for k in ids}
strides = [1] * len(size)
for i in range(len(size) - 2, -1, -1):
    strides[i] = strides[i + 1] * size[i + 1]
gi, ti = ids.index('geo'), ids.index('time')
ig = {v: k for k, v in idx['geo'].items()}
it = {v: k for k, v in idx['time'].items()}
live = {}
for g in range(size[gi]):
    for tt in range(size[ti]):
        val = d['value'].get(str(g * strides[gi] + tt * strides[ti]))
        if val is not None:
            live[(ig[g], int(it[tt]))] = val
print('live Eurostat migr_eipre values retrieved: %d (updated %s)' % (len(live), d.get('updated')))

# ---------------------------------------------------------------- current panel
panel = pd.read_csv(os.path.join(D, 'panel_final.csv'))
ctr = pd.read_csv(os.path.join(D, 'panel_final.csv'))[['iso3', 'iso2']].drop_duplicates()
iso2 = dict(zip(ctr.iso3, ctr.iso2))
iso2['GBR'] = 'UK'
iso2['GRC'] = 'EL'

V = 'irregular_proxy_detections'
sub = panel[panel[V].notna() &
            panel[V + '_url'].astype(str).str.contains('migr_eipre', na=False)]
print('panel values sourced from migr_eipre: %d across %d countries'
      % (len(sub), sub.iso3.nunique()))

rows = []
for _, r in sub.iterrows():
    iso, y, val = r['iso3'], int(r['year']), float(r[V])
    lv = live.get((iso2.get(iso, ''), y))
    if lv is None:
        st, diff = 'SOURCE_MISSING', None
    else:
        diff = val - float(lv)
        st = 'EXACT' if abs(diff) < 0.5 else 'MISMATCH'
    rows.append(dict(stage='after_correction', workbook='PANEL_FINAL', country=r['country'],
                     iso3=iso, year=y, variable='irregular_detections',
                     source='Eurostat migr_eipre', workbook_value=val,
                     live_source_value=lv, diff=diff,
                     pct_diff=(diff / lv * 100 if lv else None), status=st,
                     note='Re-queried live %s and compared against the corrected panel.' % ACCESS))

re_df = pd.DataFrame(rows)
n, ok = len(re_df), int((re_df.status == 'EXACT').sum())
print()
print('=== RE-VERIFICATION RESULT ===')
print('  values compared : %d' % n)
print('  exact           : %d' % ok)
print('  mismatched      : %d' % (n - ok))
print('  reproduction    : %.1f%%' % (ok / n * 100))
bad = re_df[re_df.status != 'EXACT']
if len(bad):
    print()
    print(bad[['iso3', 'year', 'workbook_value', 'live_source_value', 'diff']].to_string(index=False))
else:
    print('  every value the archive publishes now reproduces the live source exactly.')
print()
print('  by country:')
byc = re_df.groupby('iso3').agg(n=('year', 'size'),
                                exact=('status', lambda s: int((s == 'EXACT').sum()))).reset_index()
byc['rate'] = (byc.exact / byc.n * 100).round(1)
print('  countries at 100%%: %d of %d' % ((byc.rate == 100).sum(), len(byc)))
for _, x in byc[byc.rate < 100].iterrows():
    print('    %s %d/%d' % (x['iso3'], x['exact'], x['n']))

# ---------------------------------------------------------------- append to the log
log = pd.read_csv(os.path.join(D, 'verification_log.csv'))
if 'stage' not in log.columns:
    log.insert(0, 'stage', 'as_received')
log = log[log.stage != 'after_correction']          # idempotent re-run
for c in log.columns:
    if c not in re_df.columns:
        re_df[c] = ''
log = pd.concat([log, re_df[log.columns]], ignore_index=True)
log.to_csv(os.path.join(D, 'verification_log.csv'), index=False, encoding='utf-8-sig')
print()
print('verification_log.csv: %d rows (%s)'
      % (len(log), dict(log.stage.value_counts())))

# archive the fresh payload as evidence
dst = os.path.join(SITE, 'evidence', 'api', 'eurostat_migr_eipre_REVERIFY_2026-08-17.json')
shutil.copy2(os.path.join(RAW, 'eurostat_migr_eipre_REVERIFY.json'), dst)
shutil.copy2(dst, os.path.join(BIL, 'evidence', 'api', os.path.basename(dst)))
shutil.copy2(os.path.join(D, 'verification_log.csv'),
             os.path.join(BIL, 'data', 'verification_log.csv'))
json.dump({'compared': n, 'exact': ok, 'rate': round(ok / n * 100, 1)},
          open(os.path.join(BASE, 'verification', '_reverify_summary.json'), 'w'), indent=1)
print('fresh payload archived as evidence/api/%s' % os.path.basename(dst))
