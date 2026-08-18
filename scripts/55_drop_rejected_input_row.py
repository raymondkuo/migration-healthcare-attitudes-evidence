# -*- coding: utf-8 -*-
"""An input the archive never drew a number from is not an issue with the data, and
listing it under "Issues found" invited readers to ask whether the published figures
were affected. The reason FILE 1's pooled column was not used is a design decision, so
it now lives on the Methods page under "Which inputs were used". Drop the row.

The Chinese translation keyed by row index moves with it: ISSUES_ZH is re-keyed so the
remaining rows keep their translations."""
import os
import re
import pandas as pd

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(SITE, 'data')

p = os.path.join(D, 'known_issues.csv')
k = pd.read_csv(p)
m = k.scope.astype(str).str.contains('immigration_country_year', na=False)
assert m.sum() == 1, 'expected one row, found %d' % m.sum()
drop_at = int(k.index[m][0])
print('dropping row %d: %s / %s' % (drop_at, k.at[drop_at, 'scope'], k.at[drop_at, 'variable']))

k = k.drop(index=drop_at).reset_index(drop=True)
k.to_csv(p, index=False, encoding='utf-8-sig')
print('known_issues.csv: %d rows, severities %s' % (len(k), dict(k.severity.value_counts())))

# ---- re-key the Chinese translations, which are indexed by row number ----
src = os.path.join(SITE, 'scripts', 'i18n_content.py')
text = open(src, encoding='utf-8').read()
start = text.index('ISSUES_ZH = {')
end = text.index('\n}\n', start) + 3
block = text[start:end]

keys = [int(x) for x in re.findall(r'^\s*(\d+):\s*\(', block, re.M)]
assert drop_at in keys, 'row %d has no Chinese translation to move' % drop_at


def shift(mo):
    n = int(mo.group(1))
    if n == drop_at:
        return mo.group(0)          # handled by removal below
    return '%s%d: (' % (mo.group(0)[:-len('%d: (' % n)], n - 1 if n > drop_at else n)


# rebuild the block entry by entry so the removal and the renumbering are unambiguous
entries = []
for i, key in enumerate(keys):
    a = re.search(r'^(\s*)%d:\s*\(' % key, block, re.M)
    b = re.search(r'^(\s*)%d:\s*\(' % keys[i + 1], block, re.M) if i + 1 < len(keys) else None
    entries.append((key, block[a.start():(b.start() if b else block.rindex('}'))]))

out = ['ISSUES_ZH = {\n']
for key, body in entries:
    if key == drop_at:
        continue
    new = key - 1 if key > drop_at else key
    out.append(re.sub(r'^(\s*)%d:\s*\(' % key, lambda mo: '%s%d: (' % (mo.group(1), new),
                      body, count=1, flags=re.M))
out.append('}\n')
text = text[:start] + ''.join(out) + text[end:]
open(src, 'w', encoding='utf-8', newline='\n').write(text)

import ast
ast.parse(text)
sys_keys = [int(x) for x in re.findall(r'^\s*(\d+):\s*\(', ''.join(out), re.M)]
print('ISSUES_ZH keys now: %s' % sys_keys)
assert sys_keys == list(range(len(k))), 'translation keys do not line up with %d rows' % len(k)
print('translations re-keyed and file parses')
