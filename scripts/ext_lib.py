# -*- coding: utf-8 -*-
"""Parsers for the raw API payloads used by the 2001-2009 extension. Each returns
{(iso3, year): (value, flag)} with the source's own observation flag kept, so series
breaks, estimates and provisional values survive into the panel notes instead of being
lost at parse time."""
import json
import os

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = os.path.join(SITE, 'evidence', 'api')
COLLECTED = '2026-10-07'

OECD_B14 = 'oecd/OECD_B14_foreign-born_2001-2022_retrieved_%s.json' % COLLECTED
OECD_B15 = 'oecd/OECD_B15_foreign-population_2001-2022_retrieved_%s.json' % COLLECTED
EUR_CTB = 'eurostat_migr_pop3ctb_2001-2022_retrieved_%s.json' % COLLECTED
EUR_CTZ = 'eurostat_migr_pop1ctz_2001-2022_retrieved_%s.json' % COLLECTED
WB_POP = 'wb_SP_POP_TOTL_2001-2022_retrieved_%s.json' % COLLECTED
WB_MIG = 'wb_SM_POP_TOTL_2001-2022_retrieved_%s.json' % COLLECTED

# Eurostat geo code -> panel ISO3 (Eurostat writes the United Kingdom as UK)
EUROSTAT_GEO = {'AT': 'AUT', 'BE': 'BEL', 'BG': 'BGR', 'CH': 'CHE', 'CZ': 'CZE', 'DE': 'DEU',
                'DK': 'DNK', 'ES': 'ESP', 'FI': 'FIN', 'FR': 'FRA', 'UK': 'GBR', 'HR': 'HRV',
                'HU': 'HUN', 'IS': 'ISL', 'IT': 'ITA', 'LT': 'LTU', 'NL': 'NLD', 'NO': 'NOR',
                'PL': 'POL', 'PT': 'PRT', 'SK': 'SVK', 'SI': 'SVN', 'SE': 'SWE', 'TR': 'TUR'}


def _load(rel):
    return json.load(open(os.path.join(API, rel.replace('/', os.sep)), encoding='utf-8'))


def parse_oecd(rel):
    d = _load(rel)['data']
    st = d.get('structures') or [d.get('structure')]
    dims = st[0]['dimensions']['observation']
    names = [x['id'] for x in dims]
    ai, ti = names.index('REF_AREA'), names.index('TIME_PERIOD')
    areas, times = dims[ai]['values'], dims[ti]['values']
    attrs = st[0].get('attributes', {}).get('observation', [])
    status_i = next((i for i, a in enumerate(attrs) if a['id'] == 'OBS_STATUS'), None)
    out = {}
    for key, obs in d['dataSets'][0]['observations'].items():
        if obs[0] is None:
            continue
        idx = [int(x) for x in key.split(':')]
        flag = ''
        if status_i is not None and len(obs) > 1 + status_i and obs[1 + status_i] is not None:
            vals = attrs[status_i].get('values', [])
            code = obs[1 + status_i]
            flag = vals[code]['id'] if isinstance(code, int) and code < len(vals) else str(code)
        out[(areas[idx[ai]]['id'], int(times[idx[ti]]['id']))] = (float(obs[0]), flag)
    return out


def parse_eurostat(rel):
    d = _load(rel)
    ids, size = d['id'], d['size']
    gi, ti = ids.index('geo'), ids.index('time')
    gidx = {v: k for k, v in d['dimension']['geo']['category']['index'].items()}
    tidx = {v: k for k, v in d['dimension']['time']['category']['index'].items()}
    stride = [1] * len(size)
    for i in range(len(size) - 2, -1, -1):
        stride[i] = stride[i + 1] * size[i + 1]
    status = d.get('status', {}) or {}
    out = {}
    for flat, val in d['value'].items():
        if val is None:
            continue
        f = int(flat)
        g = gidx[(f // stride[gi]) % size[gi]]
        if g not in EUROSTAT_GEO:
            continue
        t = int(tidx[(f // stride[ti]) % size[ti]])
        out[(EUROSTAT_GEO[g], t)] = (float(val), str(status.get(flat, status.get(f, ''))))
    return out


def parse_worldbank(rel):
    rows = _load(rel)[1]
    out = {}
    for r in rows:
        if r.get('value') is None:
            continue
        out[(r['countryiso3code'], int(r['date']))] = (float(r['value']), '')
    return out


# ---------------------------------------------------------------- national-source helpers
import subprocess
import pandas as pd

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126 Safari/537.36')
STAGE = os.path.join(SITE, 'data', 'extension_staging')
CELL_COLS = ['iso3', 'year', 'variable', 'value', 'source_id', 'source_name', 'source_url',
             'local_file', 'ref_date', 'grade', 'source_type', 'flag', 'note', 'verification',
             'collected_on']


def download(url, dest, referer=None, accept=None):
    """Save the response body untouched. Returns (http_code, bytes). curl, because Python's
    urllib is blocked in this environment."""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    cmd = ['curl', '-s', '-L', '--max-time', '300', '-A', UA, '-o', dest, '-w', '%{http_code}']
    if referer:
        cmd += ['-e', referer]
    if accept:
        cmd += ['-H', 'Accept: ' + accept]
    r = subprocess.run(cmd + [url], capture_output=True, text=True)
    return r.stdout.strip(), (os.path.getsize(dest) if os.path.exists(dest) else 0)


def page_extract(pdf_path, page_no, out_base, resolution=120):
    """One page of a long PDF as its own PDF and PNG, so the page that carries the figure can
    be looked at without scrolling a 400-page document. page_no is 1-based. Returns the two
    file paths."""
    import pdfplumber
    from pypdf import PdfReader, PdfWriter
    w = PdfWriter()
    w.add_page(PdfReader(pdf_path).pages[page_no - 1])
    out_pdf, out_png = out_base + '.pdf', out_base + '.png'
    with open(out_pdf, 'wb') as fh:
        w.write(fh)
    with pdfplumber.open(pdf_path) as pdf:
        pdf.pages[page_no - 1].to_image(resolution=resolution).save(out_png)
    return out_pdf, out_png


def add_snapshot_row(iso3, variable, source_url, pdf_mirror, png_screenshot, archived,
                     note, status='page_extract', captured=COLLECTED):
    """Register a page extract / screenshot against the URL printed on the page, so the
    evidence page lists it beside the cell."""
    fp = os.path.join(SITE, 'data', 'web_snapshots.csv')
    ws = pd.read_csv(fp).fillna('')
    folder = os.path.join(SITE, 'evidence', 'countries', iso3)
    row = dict(iso3=iso3, variable=variable, source_url=source_url,
               pdf_mirror=os.path.basename(pdf_mirror) if pdf_mirror else '',
               png_screenshot=os.path.basename(png_screenshot) if png_screenshot else '',
               pdf_bytes=os.path.getsize(pdf_mirror) if pdf_mirror and os.path.exists(pdf_mirror) else 0,
               png_bytes=os.path.getsize(png_screenshot) if png_screenshot and os.path.exists(png_screenshot) else 0,
               captured=captured, snapshot_status=status, archived_html=archived, note=note)
    ws = ws[~((ws.iso3 == iso3) & (ws.source_url == source_url) &
              (ws.png_screenshot == row['png_screenshot']))]
    pd.concat([ws, pd.DataFrame([row])], ignore_index=True).to_csv(fp, index=False,
                                                                   encoding='utf-8-sig')


def write_stage(name, rows):
    """Write one collector's cells to its own staging file (replaced on every run)."""
    os.makedirs(STAGE, exist_ok=True)
    df = pd.DataFrame(rows)
    for c in CELL_COLS:
        if c not in df.columns:
            df[c] = ''
    df[CELL_COLS].to_csv(os.path.join(STAGE, name), index=False, encoding='utf-8-sig')
    return df


def cell(iso3, year, variable, value, source_id, source_name, source_url, local_file,
         ref_date, grade, source_type, note, flag='', verification='', collected_on=COLLECTED):
    return dict(iso3=iso3, year=int(year), variable=variable, value=value, source_id=source_id,
                source_name=source_name, source_url=source_url, local_file=local_file,
                ref_date=ref_date, grade=grade, source_type=source_type, flag=flag, note=note,
                verification=verification, collected_on=collected_on)


def chrome_render(url, pdf=None, png=None, wait_ms=15000):
    """Render a URL (file:/// or https://) to PDF and/or PNG with headless Chrome.

    Chrome exits 0 and writes nothing when spawned directly while the user has a browser
    open ("opening in an existing browser session"); through PowerShell Start-Process it
    renders normally, so that is how it is called. Returns the files actually written."""
    chrome = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
    prof = os.path.join(os.environ.get('TEMP', 'C:/Windows/Temp'), 'claude', 'chrome-ext')
    made = []
    for dst, flags in ((pdf, ['--no-pdf-header-footer', '--print-to-pdf=%s']),
                       (png, ['--window-size=1400,2000', '--screenshot=%s'])):
        if not dst:
            continue
        if os.path.exists(dst):
            os.remove(dst)
        args = ['--headless=new', '--disable-gpu', '--no-sandbox', '--user-data-dir=' + prof,
                '--hide-scrollbars', '--virtual-time-budget=%d' % wait_ms] + \
               [f % dst if '%s' in f else f for f in flags] + [url]
        ps = ('$a = @(%s); $p = Start-Process -FilePath %s -ArgumentList $a -PassThru -Wait '
              '-WindowStyle Hidden; exit $p.ExitCode'
              % (','.join("'" + x.replace("'", "''") + "'" for x in args),
                 "'" + chrome.replace("'", "''") + "'"))
        try:
            subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-Command', ps],
                           capture_output=True, timeout=300)
        except Exception:
            pass
        if os.path.exists(dst) and os.path.getsize(dst) > 3000:
            made.append(dst)
    return made


def table_extract(title, header, rows, out_base, source_line, note=''):
    """Render a small table of the rows that carry the figure, with the title, source line and
    retrieval date, as PDF + PNG. The extract shows what was read from the archived file; the
    file itself stays archived beside it."""
    import html as _h
    css = ('body{font:13px/1.5 "Segoe UI","Noto Sans TC",sans-serif;margin:24px;color:#1a1a18}'
           'h1{font-size:17px;margin:0 0 4px}.s{color:#5f5f5a;font-size:12px;margin:0 0 14px}'
           'table{border-collapse:collapse;width:100%%}th,td{border:1px solid #cfcec7;padding:4px 9px;'
           'text-align:left}th{background:#eef2f7}td.n{text-align:right;font-variant-numeric:'
           'tabular-nums}tr.hl td{background:#fbf1dc;font-weight:600}.f{margin-top:14px;'
           'color:#5f5f5a;font-size:11.5px}')
    body = ''.join('<tr%s>%s</tr>' % (' class="hl"' if hl else '', ''.join(
        '<td%s>%s</td>' % (' class="n"' if i > 0 else '', _h.escape(str(c)))
        for i, c in enumerate(r))) for r, hl in rows)
    doc = ('<!doctype html><meta charset="utf-8"><style>%s</style><h1>%s</h1><p class="s">%s</p>'
           '<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table><p class="f">%s</p>'
           % (css, _h.escape(title), _h.escape(source_line),
              ''.join('<th>%s</th>' % _h.escape(h) for h in header), body,
              _h.escape(note or 'Rows highlighted are the ones used. Extract prepared %s from the '
                        'archived source file beside it.' % COLLECTED)))
    tmp = out_base + '.tmp.html'
    open(tmp, 'w', encoding='utf-8').write(doc)
    made = chrome_render('file:///' + tmp.replace(chr(92), '/'), pdf=out_base + '.pdf',
                         png=out_base + '.png')
    os.remove(tmp)
    return out_base + '.pdf', out_base + '.png', made


# The collectors must always judge what is "already published" against the panel as it stood
# before the extension, not against the working file, which the assembler overwrites. Otherwise
# a re-run would find every cell filled and collect nothing.
BASELINE = '0d64a1c'


def baseline_panel():
    import io
    out = subprocess.run(['git', '-C', SITE, 'show', '%s:data/panel_final.csv' % BASELINE],
                         capture_output=True).stdout
    return pd.read_csv(io.BytesIO(out))


def grid_mirror(title, source_line, grid, years, out_base, note=''):
    """Render a country x year grid of the values read from a payload as PDF + PNG, A3
    landscape. grid is {iso3: {year: value}}; empty cells show a dash. This is the visual
    companion of a raw API payload: it shows the numbers the panel actually takes from it."""
    import html as _h
    css = ('@page{size:A3 landscape;margin:8mm}body{font:10px/1.35 "Segoe UI","Noto Sans TC",'
           'sans-serif;margin:10px;color:#1a1a18}h1{font-size:15px;margin:0 0 3px}.s{color:#5f5f5a;'
           'font-size:10.5px;margin:0 0 8px}table{border-collapse:collapse;width:100%}'
           'th,td{border:1px solid #d9d8d2;padding:2px 4px;text-align:right;'
           'font-variant-numeric:tabular-nums;white-space:nowrap}th{background:#eef2f7}'
           'td.c,th.c{text-align:left;font-weight:600;background:#f7f8fa}.f{margin-top:8px;'
           'color:#5f5f5a;font-size:9.5px}')
    head = '<th class="c">ISO3</th>' + ''.join('<th>%d</th>' % y for y in years)
    body = ''
    for iso in sorted(grid):
        cells = ''.join('<td>%s</td>' % (format(int(grid[iso][y]), ',') if y in grid[iso] else '&ndash;')
                        for y in years)
        body += '<tr><td class="c">%s</td>%s</tr>' % (_h.escape(iso), cells)
    doc = ('<!doctype html><meta charset="utf-8"><style>%s</style><h1>%s</h1><p class="s">%s</p>'
           '<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table><p class="f">%s</p>'
           % (css, _h.escape(title), _h.escape(source_line), head, body,
              _h.escape(note or 'Values read from the archived payload beside this file, '
                                'rendered %s so they can be checked by eye; the payload is the '
                                'authoritative record.' % COLLECTED)))
    tmp = out_base + '.tmp.html'
    open(tmp, 'w', encoding='utf-8').write(doc)
    made = chrome_render('file:///' + tmp.replace(chr(92), '/'), pdf=out_base + '.pdf',
                         png=out_base + '.png')
    os.remove(tmp)
    return made


EURO_FLAG = {'b': 'break in time series', 'e': 'estimated', 'p': 'provisional',
             'd': 'definition differs', 'u': 'low reliability', 'c': 'confidential'}


def eurostat_flag_text(flag):
    """The flag Eurostat attached to an observation, worded for the flag column."""
    parts = [EURO_FLAG[c] for c in str(flag or '') if c in EURO_FLAG]
    return ('Eurostat flag: ' + ', '.join(parts)) if parts else ''
