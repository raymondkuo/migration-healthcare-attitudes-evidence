# -*- coding: utf-8 -*-
"""Every NUMBER on this site already comes from data/*.csv, and both language builds
read the same file, so a figure cannot differ between EN and ZH. What could drift was
hand-written PROSE: the Chinese text for known_issues and codebook lived in a separate
dict keyed by ROW INDEX. Edit the English in the CSV and the Chinese silently stayed
behind; delete a row and every later key pointed at the wrong row.

Move the translations into the data files as sibling columns, so one row carries both
languages and the index can no longer matter."""
import os
import sys
import pandas as pd

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SITE, 'scripts'))
D = os.path.join(SITE, 'data')

import i18n_content as C

# ------------------------------------------------------------------ known issues
p = os.path.join(D, 'known_issues.csv')
k = pd.read_csv(p).fillna('')
missing = [i for i in range(len(k)) if i not in C.ISSUES_ZH]
for col, pos in (('issue_zh', 0), ('evidence_zh', 1), ('action_zh', 2)):
    k[col] = [C.ISSUES_ZH.get(i, ('', '', ''))[pos] for i in range(len(k))]
k = k[['severity', 'scope', 'variable',
       'issue', 'issue_zh', 'evidence', 'evidence_zh', 'action', 'action_zh']]
k.to_csv(p, index=False, encoding='utf-8-sig')
print('known_issues.csv  : %d rows, %d columns; rows with no Chinese: %s'
      % (len(k), len(k.columns), missing or 'none'))

# ------------------------------------------------------------------ codebook
p = os.path.join(D, 'codebook.csv')
c = pd.read_csv(p).fillna('')
missing_c = [i for i in range(len(c)) if i not in C.CODEBOOK_ZH]
c['definition_zh'] = [C.CODEBOOK_ZH.get(i, ('', ''))[0] for i in range(len(c))]
c['caution_zh'] = [C.CODEBOOK_ZH.get(i, ('', ''))[1] for i in range(len(c))]
c.to_csv(p, index=False, encoding='utf-8-sig')
print('codebook.csv      : %d rows, %d columns' % (len(c), len(c.columns)))
if missing_c:
    print('  rows with NO Chinese definition (fell back to English silently):')
    for i in missing_c:
        print('    [%d] %s' % (i, c.iloc[i, 0]))
