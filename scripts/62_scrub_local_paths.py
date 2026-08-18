# -*- coding: utf-8 -*-
"""Absolute local paths were published, and the workspace folder is named after a
co-author of the study. That put a real person's name into files this archive serves:
321 rows of verification/country_source_manifest.csv alone, live and downloadable.

The name has nothing to do with the website, and the paths are meaningless to any
external reader - they point at a drive that does not exist for them. So the workspace
prefix is stripped everywhere, leaving the part that carries information
(countries/AUS_Australia), and the two scripts that hardcoded it are made to derive
their own location like the rest of the build.

This matters beyond tidiness: the archive goes to journal editors and reviewers, and
under blind review an author name in a published file is an identity leak."""
import os
import subprocess

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# every spelling of the workspace prefix that appears in the tree
PREFIXES = [
    'D:\\研究計畫\\其他投稿\\2026_移民對非本國籍使用公共醫療態度（葉明叡）\\claude-work\\',
    'D:/研究計畫/其他投稿/2026_移民對非本國籍使用公共醫療態度（葉明叡）/claude-work/',
    'D:\\研究計畫\\其他投稿\\2026_移民對非本國籍使用公共醫療態度（葉明叡）\\claude-work',
    'D:/研究計畫/其他投稿/2026_移民對非本國籍使用公共醫療態度（葉明叡）/claude-work',
    'D:\\研究計畫\\其他投稿\\2026_移民對非本國籍使用公共醫療態度（葉明叡）',
    'D:/研究計畫/其他投稿/2026_移民對非本國籍使用公共醫療態度（葉明叡）',
]
NAME = '葉明叡'

tracked = subprocess.run(['git', 'ls-files'], cwd=SITE, capture_output=True
                         ).stdout.decode('utf-8').splitlines()

TEXT = ('.csv', '.md', '.py', '.sh', '.json', '.txt', '.html', '.yml', '.yaml', '.cff')
changed = []
for rel in tracked:
    if not rel.lower().endswith(TEXT):
        continue
    p = os.path.join(SITE, rel.replace('/', os.sep))
    if not os.path.exists(p):
        continue
    try:
        s = open(p, encoding='utf-8').read()
    except (UnicodeDecodeError, PermissionError):
        continue
    if NAME not in s:
        continue
    out = s
    for pre in PREFIXES:
        out = out.replace(pre, '')
    if out != s:
        n = s.count(NAME) - out.count(NAME)
        open(p, 'w', encoding='utf-8', newline='').write(out)
        changed.append((rel, n, out.count(NAME)))

print('=== workspace prefix stripped ===')
for rel, n, left in changed:
    print('  %-58s removed %4d  remaining %d' % (rel[:58], n, left))

# anything the prefix replacement could not reach
still = []
for rel in tracked:
    if not rel.lower().endswith(TEXT):
        continue
    p = os.path.join(SITE, rel.replace('/', os.sep))
    if not os.path.exists(p):
        continue
    try:
        if NAME in open(p, encoding='utf-8').read():
            still.append(rel)
    except (UnicodeDecodeError, PermissionError):
        pass
print('\ntracked text files still containing the name: %d' % len(still))
for r in still:
    print('   %s' % r)
