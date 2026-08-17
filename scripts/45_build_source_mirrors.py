# -*- coding: utf-8 -*-
"""Give every archived source a human-viewable mirror.

Raw payloads (JSON/CSV/XLSX) and PDFs cannot be checked for authenticity by eye, so each
archived file gets a rendered visual companion:
    *.pdf                -> PNG of its first pages
    *.html               -> PDF + PNG rendered from the archived copy
    *.json/.csv/.xls(x)  -> an HTML data preview rendered to PDF + PNG
Existing snapshots are not regenerated.
"""
import os, re, sys, json, html, shutil, subprocess, time
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(BASE, 'migration-data-archive')
EVC = os.path.join(SITE, 'evidence', 'countries')
EVA = os.path.join(SITE, 'evidence', 'api')
CHROME = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
PROFILE = os.path.join(os.environ.get('TEMP', 'C:/Windows/Temp'), 'claude', 'chrome-mirror')
TMP = os.path.join(os.environ.get('TEMP', 'C:/Windows/Temp'), 'claude', 'mirrorwork')
os.makedirs(TMP, exist_ok=True)
ACCESS = '2026-08-17'

PREVIEW_CSS = """
 @page{margin:12mm}
 body{font:11px/1.5 -apple-system,"Segoe UI","PingFang TC","Noto Sans TC",sans-serif;margin:0;color:#1a1a18}
 h1{font-size:15px;margin:0 0 3px} .sub{color:#5f5f5a;font-size:10.5px;margin:0 0 10px}
 table{border-collapse:collapse;width:100%;font-size:9.6px;table-layout:fixed}
 th,td{border:1px solid #dcdcd6;padding:2px 4px;text-align:left;word-break:break-word;
   vertical-align:top;max-width:210px;overflow:hidden}
 th{background:#eef2f7;font-weight:600}
 pre{white-space:pre-wrap;word-break:break-all;font:9.4px/1.45 Consolas,monospace;
   background:#f7f8fa;border:1px solid #e3e2dd;padding:8px;border-radius:4px}
 .foot{margin-top:14px;border-top:1px solid #dcdcd6;padding-top:6px;color:#6a6a64;font-size:9px}
"""


def shell(dst_pdf, dst_png, src_url):
    ok = 0
    for flags, dst in (((['--no-pdf-header-footer', '--print-to-pdf=' + dst_pdf]), dst_pdf),
                       ((['--window-size=1400,2400', '--screenshot=' + dst_png]), dst_png)):
        if os.path.exists(dst) and os.path.getsize(dst) > 4000:
            ok += 1
            continue
        try:
            subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
                            '--user-data-dir=' + PROFILE, '--hide-scrollbars',
                            '--virtual-time-budget=12000'] + flags + [src_url],
                           capture_output=True, timeout=150)
        except Exception:
            pass
        if os.path.exists(dst) and os.path.getsize(dst) > 4000:
            ok += 1
    return ok


def preview_html(path, title, note):
    """Build a readable HTML preview of a data file."""
    low = path.lower()
    body = ''
    try:
        if low.endswith('.json'):
            raw = open(path, encoding='utf-8', errors='replace').read()
            txt = raw if len(raw) <= 14000 else raw[:14000] + '\n… truncated for display; the '\
                'complete payload is the archived file itself …'
            body = '<pre>%s</pre>' % html.escape(txt)
        elif low.endswith('.csv'):
            try:
                df = pd.read_csv(path)
            except Exception:
                df = pd.read_csv(path, encoding='euc-kr')
            body = ('<p class="sub">%d rows × %d columns; first 60 rows shown.</p>' % df.shape
                    + df.head(60).to_html(index=False, border=0))
        elif low.endswith(('.xlsx', '.xls')):
            book = pd.read_excel(path, sheet_name=None)
            parts = []
            for nm, df in list(book.items())[:3]:
                parts.append('<h2 style="font-size:12px;margin:12px 0 4px">Sheet: %s '
                             '<span style="font-weight:400;color:#5f5f5a">(%d × %d)</span></h2>'
                             % (html.escape(str(nm)), df.shape[0], df.shape[1]))
                parts.append(df.head(35).to_html(index=False, border=0))
            body = ''.join(parts)
    except Exception as e:
        body = '<pre>preview unavailable: %s</pre>' % html.escape(str(e))
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>%s</title>'
            '<style>%s</style></head><body><h1>%s</h1><p class="sub">%s</p>%s'
            '<p class="foot">Rendered preview of an archived source file · Migration and Population '
            'Data Archive · captured %s. This preview exists so the payload can be read and checked '
            'by eye; the authoritative artifact is the archived file itself.</p></body></html>'
            % (html.escape(title), PREVIEW_CSS, html.escape(title), html.escape(note), body, ACCESS))


def pdf_to_png(src, dst, pages=2):
    if os.path.exists(dst) and os.path.getsize(dst) > 4000:
        return True
    try:
        import pdfplumber
        with pdfplumber.open(src) as pdf:
            n = min(pages, len(pdf.pages))
            if n == 0:
                return False
            ims = [pdf.pages[i].to_image(resolution=110) for i in range(n)]
            if n == 1:
                ims[0].save(dst)
            else:
                from PIL import Image
                pil = [im.original.convert('RGB') for im in ims]
                w = max(p.width for p in pil)
                h = sum(p.height for p in pil)
                out = Image.new('RGB', (w, h), 'white')
                y = 0
                for p in pil:
                    out.paste(p, (0, y)); y += p.height
                out.save(dst)
        return os.path.exists(dst)
    except Exception as e:
        return False


# ---------------------------------------------------------------- gather targets
targets = []          # (folder, filename, kind)
for iso in sorted(os.listdir(EVC)):
    d = os.path.join(EVC, iso)
    if not os.path.isdir(d):
        continue
    for f in sorted(os.listdir(d)):
        low = f.lower()
        if low.startswith('mirror__') or low.startswith('snapshot__'):
            continue
        if f in ('README.md', 'data_from_source.csv', 'value_check.csv', 'source_manifest.csv'):
            continue
        if low.endswith(('.pdf', '.html', '.htm', '.json', '.csv', '.xls', '.xlsx')):
            targets.append((d, f, iso))
for root, _, files in os.walk(EVA):
    for f in sorted(files):
        if f.lower().endswith(('.json', '.csv', '.xls', '.xlsx', '.xml')):
            targets.append((root, f, 'API'))

print('archived source files needing a viewable mirror: %d' % len(targets))
rows = []
t0 = time.time()
for i, (d, f, tag) in enumerate(targets, 1):
    src = os.path.join(d, f)
    stem = 'MIRROR__' + re.sub(r'[^A-Za-z0-9._-]+', '_', os.path.splitext(f)[0])[:70]
    png = os.path.join(d, stem + '.png')
    pdf = os.path.join(d, stem + '.pdf')
    low = f.lower()
    made = []
    if low.endswith('.pdf'):
        if pdf_to_png(src, png):
            made.append(os.path.basename(png))
    elif low.endswith(('.html', '.htm')):
        url = 'file:///' + src.replace('\\', '/')
        shell(pdf, png, url)
        made = [os.path.basename(x) for x in (pdf, png)
                if os.path.exists(x) and os.path.getsize(x) > 4000]
    else:
        note = 'Archived source file: %s' % f
        tmp = os.path.join(TMP, stem + '.html')
        open(tmp, 'w', encoding='utf-8').write(preview_html(src, f, note))
        shell(pdf, png, 'file:///' + tmp.replace('\\', '/'))
        made = [os.path.basename(x) for x in (pdf, png)
                if os.path.exists(x) and os.path.getsize(x) > 4000]
        try:
            os.remove(tmp)
        except Exception:
            pass
    rows.append(dict(scope=tag, folder=os.path.relpath(d, SITE).replace('\\', '/'),
                     source_file=f, mirrors=';'.join(made), n_mirrors=len(made)))
    if i % 25 == 0:
        print('  %3d/%d  (%.0fs)' % (i, len(targets), time.time() - t0)); sys.stdout.flush()

mf = pd.DataFrame(rows)
mf.to_csv(os.path.join(SITE, 'data', 'source_mirrors.csv'), index=False, encoding='utf-8-sig')
print('\nfiles with at least one mirror : %d of %d' % ((mf.n_mirrors > 0).sum(), len(mf)))
print('files still without a mirror   : %d' % (mf.n_mirrors == 0).sum())
for _, r in mf[mf.n_mirrors == 0].head(15).iterrows():
    print('   %-22s %s' % (r['scope'], r['source_file'][:70]))
print('elapsed %.0fs' % (time.time() - t0))
