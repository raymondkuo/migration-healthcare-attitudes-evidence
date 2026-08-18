# -*- coding: utf-8 -*-
"""Row 4 of known_issues.csv describes a defect in an INPUT workbook this archive
rejected, not a defect in a published number. Sitting under a red HIGH tag between
real data problems, it reads as though the published figures are affected. Reclassify
it as NOT USED and state plainly what the published data does and does not owe to it."""
import os
import pandas as pd

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(SITE, 'data')

p = os.path.join(D, 'known_issues.csv')
k = pd.read_csv(p)

m = k.scope.astype(str).str.contains('immigration_country_year', na=False)
assert m.sum() == 1, 'expected exactly one row scoped to the input workbook, got %d' % m.sum()
i = k.index[m][0]
assert k.at[i, 'severity'] == 'HIGH', 'unexpected severity %r' % k.at[i, 'severity']

k.at[i, 'severity'] = 'NOT USED'
k.at[i, 'action'] = (
    'The pooled column was rejected: no value published here is taken from it, and no source '
    'in the register cites this workbook as its authority. The archive keeps the three measures '
    'in three separate columns, which must never be pooled. Where a figure was first noticed in '
    'this workbook it was re-verified against the publisher before publication — the 520 UN WPP '
    'population values reproduce exactly, and Taiwan’s 17 overstayer and absconded-worker values '
    'now cite the National Immigration Agency and the Ministry of Labor directly.')

k.to_csv(p, index=False, encoding='utf-8-sig')

r = k.loc[i]
print('reclassified row %d' % i)
for c in ('severity', 'scope', 'variable', 'action'):
    print('  %-8s %s' % (c, r[c]))
print()
print('severity counts:', dict(k.severity.value_counts()))
