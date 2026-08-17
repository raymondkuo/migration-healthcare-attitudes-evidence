# -*- coding: utf-8 -*-
"""For every value that is not machine-verified, confirm the number actually appears
in the archived source document. Produces verification/trace_c_values.csv.

A value counts as traced if any of these appears in the extracted text of an archived
file for that country-variable-source:
  exact          1234567 / 1,234,567 / 1 234 567 / 1.234.567
  thousands      1234.567 / 1,234.6 / 1234,6      (value expressed in thousands)
  millions       1.23 / 1.2                        (value expressed in millions)
  rounded        to 2 or 3 significant figures, as published estimates often are
"""
import os, re, sys, html, json
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(BASE, 'migration-data-archive')
D = os.path.join(SITE, 'data')
EVC = os.path.join(SITE, 'evidence', 'countries')

panel = pd.read_csv(os.path.join(D, 'panel_final.csv'))
reg = pd.read_csv(os.path.join(D, 'source_register.csv'))
VARS = ['population', 'foreign_born', 'foreign_nationals', 'irregular_stock',
        'irregular_proxy_overstayers', 'irregular_proxy_detections',
        'irregular_proxy_absconded_workers']

# ---------------------------------------------------------------- text extraction
_cache = {}


def text_of(path):
    if path in _cache:
        return _cache[path]
    t = ''
    low = path.lower()
    try:
        if low.endswith('.pdf'):
            import pdfplumber
            with pdfplumber.open(path) as pdf:
                t = '\n'.join((pg.extract_text() or '') for pg in pdf.pages)
        elif low.endswith(('.html', '.htm')):
            raw = open(path, encoding='utf-8', errors='replace').read()
            raw = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', raw, flags=re.S | re.I)
            t = html.unescape(re.sub(r'<[^>]+>', ' ', raw))
        elif low.endswith(('.csv', '.txt')):
            try:
                t = open(path, encoding='utf-8', errors='replace').read()
            except Exception:
                t = open(path, encoding='euc-kr', errors='replace').read()
        elif low.endswith(('.xlsx', '.xls')):
            book = pd.read_excel(path, sheet_name=None, header=None)
            t = '\n'.join(df.to_string() for df in book.values())
        elif low.endswith('.json'):
            t = open(path, encoding='utf-8', errors='replace').read()
    except Exception as e:
        t = ''
    t = re.sub(r'[   ]', ' ', t)
    _cache[path] = t
    return t


def variants(v):
    """Plausible printed forms of a number."""
    v = float(v)
    n = int(round(v))
    out = set()
    for s in (str(n), '%d' % n):
        out.add(s)
        out.add('{:,}'.format(n))
        out.add('{:,}'.format(n).replace(',', ' '))
        out.add('{:,}'.format(n).replace(',', '.'))
        out.add('{:,}'.format(n).replace(',', "'"))
    # thousands
    for dec in (0, 1, 2, 3):
        th = round(v / 1000.0, dec)
        s = ('%.*f' % (dec, th))
        out.add(s); out.add(s.replace('.', ',')); out.add('{:,}'.format(th))
    # millions
    for dec in (1, 2, 3):
        mn = round(v / 1e6, dec)
        s = ('%.*f' % (dec, mn))
        out.add(s); out.add(s.replace('.', ','))
    # significant-figure rounding, as published estimates often are
    for sig in (2, 3):
        try:
            from decimal import Decimal
            q = float('%.*g' % (sig, v))
            out.add('{:,}'.format(int(q)))
            out.add(str(int(q)))
            out.add('%.*f' % (0, q / 1000.0))
            out.add('{:,}'.format(int(q / 1000.0)))
        except Exception:
            pass
    return {x for x in out if len(x) >= 3}


def files_for(iso, url, lf):
    out = []
    d = os.path.join(EVC, iso)
    if not os.path.isdir(d):
        return out
    if isinstance(lf, str) and lf and lf != 'nan':
        p = os.path.join(d, lf)
        if os.path.isfile(p):
            out.append(p)
    return out


# map (iso,url) -> archived local files
reg_files = {}
for _, r in reg.iterrows():
    key = (r['iso3'], str(r['source_url']))
    fs = files_for(r['iso3'], str(r['source_url']), r.get('local_file'))
    if fs:
        reg_files.setdefault(key, []).extend(fs)

rows = []
for v in VARS:
    if v + '_grade' not in panel:
        continue
    sub = panel[panel[v + '_grade'].isin(['C'])]
    for _, r in sub.iterrows():
        iso, y, val = r['iso3'], int(r['year']), r[v]
        url = str(r.get(v + '_url') or '')
        cand = list(reg_files.get((iso, url), []))
        # fall back to any file in the country folder matching the variable name
        if not cand:
            d = os.path.join(EVC, iso)
            if os.path.isdir(d):
                cand = [os.path.join(d, f) for f in os.listdir(d)
                        if f.startswith(v) and f.lower().endswith(
                            ('.pdf', '.html', '.htm', '.csv', '.xls', '.xlsx', '.json'))]
        vs = variants(val)
        hit, where = False, ''
        for p in cand:
            t = text_of(p)
            if not t:
                continue
            for s in vs:
                if s in t:
                    hit, where = True, os.path.basename(p)
                    break
            if hit:
                break
        rows.append(dict(iso3=iso, year=y, variable=v, value=val,
                         source=str(r.get(v + '_source') or '')[:90], url=url,
                         n_files=len(cand), traced='YES' if hit else 'NO',
                         found_in=where,
                         files=';'.join(os.path.basename(x) for x in cand)[:200]))

df = pd.DataFrame(rows)
df.to_csv(os.path.join(BASE, 'verification', 'trace_c_values.csv'),
          index=False, encoding='utf-8-sig')
print('C-graded values checked: %d' % len(df))
print(df.traced.value_counts().to_string())
print()
print('=== NOT traced, by country/variable ===')
nt = df[df.traced == 'NO']
if len(nt):
    g = nt.groupby(['iso3', 'variable']).agg(n=('year', 'size'),
                                             yrs=('year', lambda x: '%d-%d' % (min(x), max(x))),
                                             files=('n_files', 'max')).reset_index()
    for _, r in g.iterrows():
        print('  %-4s %-32s %2d  %-10s archived files: %d'
              % (r['iso3'], r['variable'], r['n'], r['yrs'], r['files']))
else:
    print('  none')
