# -*- coding: utf-8 -*-
"""What bytes GitHub Pages serves for a file in this folder.

git on Windows is configured here to check files out with CRLF and store them with LF, so the
working folder is not what the website serves. Text files are stored after git's CRLF -> LF
conversion, which it skips for a file holding a NUL or a lone CR, and which .gitattributes can
switch off (-text) for raw captures that must be kept byte for byte. The checksum manifest and
every check of it must hash the served bytes, so the rule lives in one place."""
import os
import re
import subprocess

TEXT_EXT = {'.csv', '.html', '.md', '.py', '.json', '.txt', '.yml', '.yaml', '.cff', '.css', '.js',
            '.mjs', '.sh', '.svg', '.xml'}
LONE_CR = re.compile(rb'\r(?!\n)')


TEXT_NAMES = {'.gitignore', '.gitattributes'}      # dotfiles have no extension but are text


def is_text_ext(path):
    return (os.path.splitext(path)[1].lower() in TEXT_EXT
            or os.path.basename(path) in TEXT_NAMES)


def text_unset(site, rels):
    """Relative paths that .gitattributes marks -text (stored byte for byte)."""
    rels = list(rels)
    if not rels:
        return set()
    data = ('\0'.join(rels) + '\0').encode('utf-8')
    try:
        p = subprocess.run(['git', '-C', site, 'check-attr', '-z', 'text', '--stdin'],
                           input=data, capture_output=True, timeout=180)
    except Exception:
        return set()
    f = p.stdout.decode('utf-8').split('\0')
    return {f[i].replace('\\', '/') for i in range(0, len(f) - 2, 3) if f[i + 2] == 'unset'}


def served_bytes(path, raw, raw_text=()):
    """The bytes GitHub serves for this file. raw_text: the paths marked -text."""
    if (is_text_ext(path) and path not in raw_text and b'\0' not in raw[:8000]
            and not LONE_CR.search(raw)):
        return raw.replace(b'\r\n', b'\n')
    return raw
