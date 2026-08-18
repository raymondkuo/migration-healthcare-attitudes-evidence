# -*- coding: utf-8 -*-
"""Regenerate the 156 PDF extracts with bilingual (EN + 繁體中文) headings, so the
Chinese pages link to a PDF a Chinese reader can use."""
import os, sys, html, subprocess, time, shutil
import pandas as pd


def _psq(s):
    """A PowerShell single-quoted literal, safe for spaces and CJK in the path."""
    return "'" + str(s).replace("'", "''") + "'"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blib import (SITE, D, ACCESS, panel, vlog, reg, corr, snaps, apis, pubs,
                  ALLVARS, cname, vlab, reason_zh)
from i18n import VERTAG, COUNTRY, VLAB

PRINT = os.path.join(SITE, 'evidence', 'extracts')
CHROME = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
PROFILE = os.path.join(os.environ.get('TEMP', 'C:/Windows/Temp'), 'claude', 'chrome-bi')
CHK = {'irregular_proxy_detections': 'irregular_detections'}

TPL = """<!doctype html><html lang="zh-Hant-TW"><head><meta charset="utf-8">
<title>TITLE_ATTR</title><style>
 @page{margin:15mm}
 body{font:11.6px/1.6 -apple-system,"Segoe UI","PingFang TC","Noto Sans TC",
   "Microsoft JhengHei",sans-serif;color:#1a1a18;margin:0}
 h1{font-size:16.5px;margin:0 0 2px;line-height:1.35}
 h1 .zh{display:block;font-size:14px;color:#3d5a80;font-weight:600}
 .sub{color:#5f5f5a;margin:0 0 14px;font-size:11px}
 h2{font-size:12.6px;margin:17px 0 5px}
 h2 span{color:#5f5f5a;font-weight:400;font-size:11.4px}
 table{border-collapse:collapse;width:100%;font-size:10.8px}
 th,td{border:1px solid #dcdcd6;padding:4px 7px;text-align:left;vertical-align:top}
 th{background:#eef2f7;font-weight:600;line-height:1.35}
 th small{display:block;font-weight:400;color:#5f5f5a;font-size:9.6px}
 td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}
 code{font-family:Consolas,monospace;font-size:10px}
 .box{border-left:3px solid #3d5a80;background:#eef2f7;padding:7px 11px;margin:11px 0;font-size:10.8px}
 ul{margin:5px 0;padding-left:17px} li{margin:2px 0}
 .foot{margin-top:20px;border-top:1px solid #dcdcd6;padding-top:7px;color:#6a6a64;font-size:9.6px;
   line-height:1.55}
</style></head><body>
<h1>TITLE_EN<span class="zh">TITLE_ZH</span></h1>
<p class="sub">Data extract and provenance sheet · retrieved ACCESSDATE ·
資料摘錄與出處說明 · 取得日期 ACCESSDATE · Migration and Population Data Archive 移民與人口資料存檔</p>
<h2>Values <span>數值</span></h2>
<table><thead><tr>
<th class="n">Year<small>年度</small></th><th class="n">Value<small>數值</small></th>
<th>Grade<small>等級</small></th><th>Verification<small>查證結果</small></th>
<th>Source<small>來源</small></th><th>Reference date<small>基準日</small></th>
</tr></thead><tbody>TRS</tbody></table>
NOTEBOX
<h2>Source URL(s) <span>來源網址</span></h2><ul>URLS</ul>
<h2>Archived evidence files <span>存檔佐證檔案</span></h2><ul>ARTS</ul>
<p class="foot">Grades / 品質等級：A = re-derived from a machine-readable official source and matched
exactly, or corrected against one 自機器可讀之官方來源重新計算並完全一致，或依該來源更正 ·
B = confirmed by reading the retrieved source document 經來源文件確認 ·
C = source retrieved but the value is a modelled estimate 已取得來源，但數值為推估值 ·
D = cited source could not be retrieved 來源無法取得。<br>
Joint work of Prof. Raymond Kuo, National Taiwan University, and Claude (Anthropic).
國立臺灣大學郭年真教授與 Claude（Anthropic）共同成果。</p>
</body></html>"""


def esc(x):
    return html.escape('' if x is None or (isinstance(x, float) and pd.isna(x)) else str(x))


snap_by = {}
for _, s in snaps.iterrows():
    snap_by.setdefault((s['iso3'], s['source_url']), []).append(s)
reg_by = {}
for _, r in reg.iterrows():
    reg_by.setdefault((r['iso3'], str(r['source_url'])), []).append(r)

cinfo = panel.groupby(['iso3', 'country']).size().reset_index()[['iso3', 'country']]
jobs = []
for _, ci in cinfo.iterrows():
    iso, en = ci['iso3'], ci['country']
    g = panel[panel.iso3 == iso].sort_values('year')
    for v in ALLVARS:
        if v not in g or g[v].notna().sum() == 0:
            continue
        sub = g[g[v].notna()]
        ucol = v + '_url'
        urls = sorted({str(u) for u in sub[ucol].dropna()}) if ucol in sub else []
        arts = []
        for u in urls:
            for r in reg_by.get((iso, u), []):
                lf = str(r.get('local_file') or '')
                if lf and lf != 'nan' and os.path.isfile(
                        os.path.join(SITE, 'evidence', 'countries', iso, lf)):
                    arts.append('evidence/countries/%s/%s' % (iso, lf))
            for s in snap_by.get((iso, u), []):
                for c in ('pdf_mirror', 'png_screenshot'):
                    f = s[c]
                    if isinstance(f, str) and f and os.path.isfile(
                            os.path.join(SITE, 'evidence', 'countries', iso, f)):
                        arts.append('evidence/countries/%s/%s' % (iso, f))
        arts = list(dict.fromkeys(arts))

        cv = vlog[(vlog.iso3 == iso) & (vlog.variable == CHK.get(v, v))]
        chk = {int(r['year']): r for _, r in cv.iterrows()}
        cc = corr[(corr.iso3 == iso) & (corr.variable == v)]
        corrected = {int(r['year']) for _, r in cc.iterrows()}
        trs = ''
        for _, r in sub.iterrows():
            y = int(r['year'])
            c = chk.get(y)
            if y in corrected:
                ver = '%s／%s' % (VERTAG['en']['corrected'], VERTAG['zh']['corrected'])
            elif c is not None and c['status'] == 'EXACT':
                ver = '%s／%s' % (VERTAG['en']['exact'], VERTAG['zh']['exact'])
            elif str(r.get(v + '_verification') or '') not in ('', 'nan'):
                ver = '%s／%s' % (VERTAG['en']['doc'], VERTAG['zh']['doc'])
            else:
                ver = '%s／%s' % (VERTAG['en']['nomach'], VERTAG['zh']['nomach'])
            trs += ('<tr><td class="n">%d</td><td class="n"><b>%s</b></td><td>%s</td><td>%s</td>'
                    '<td>%s</td><td>%s</td></tr>'
                    % (y, '{:,.0f}'.format(r[v]), esc(r.get(v + '_grade') or '—'),
                       esc(ver), esc(str(r.get(v + '_source') or '')[:88]),
                       esc(str(r.get(v + '_ref_date') or '') if (v + '_ref_date') in r else '')))

        note = next((x for x in (sub[v + '_note'] if (v + '_note') in sub else [])
                     if isinstance(x, str) and x.strip()), '')
        vnote = next((x for x in (sub[v + '_verification'] if (v + '_verification') in sub else [])
                      if isinstance(x, str) and x.strip()), '')
        nb = ''
        if note:
            nb += '<div class="box"><b>Definition note 定義說明.</b> %s</div>' % esc(note)
        if vnote:
            nb += '<div class="box"><b>How this was confirmed 確認方式.</b> %s</div>' % esc(vnote)
        if len(cc):
            rs = '；'.join(sorted({reason_zh(x) for x in cc['reason']}))
            nb += ('<div class="box"><b>Correction applied 已套用更正.</b> %s</div>' % esc(rs))

        doc = (TPL.replace('TITLE_ATTR', esc('%s %s extract' % (iso, v)))
                  .replace('TITLE_EN', esc('%s — %s' % (en, VLAB['en'].get(v, v))))
                  .replace('TITLE_ZH', esc('%s — %s' % (COUNTRY.get(en, en), VLAB['zh'].get(v, v))))
                  .replace('ACCESSDATE', ACCESS).replace('TRS', trs).replace('NOTEBOX', nb)
                  .replace('URLS', ''.join('<li><code>%s</code></li>' % esc(u) for u in urls) or '<li>—</li>')
                  .replace('ARTS', ''.join('<li><code>%s</code></li>' % esc(a) for a in arts) or '<li>—</li>'))
        d = os.path.join(PRINT, iso)
        os.makedirs(d, exist_ok=True)
        src = os.path.join(d, v + '.src.html')
        open(src, 'w', encoding='utf-8').write(doc)
        jobs.append((iso, v, src, os.path.join(d, v + '.pdf')))

print('rendering %d bilingual PDF extracts' % len(jobs))
t0 = time.time()

# Chrome will not render when spawned directly from this process: it exits 0, writes
# nothing, and reports "opening in an existing browser session" whenever the user has a
# browser open. Launched through Start-Process it renders normally, so the render pass
# is handed to PowerShell. One script for all jobs, so PowerShell starts once.
#
# Nothing is written over a good PDF: each job renders to a .new file, and the existing
# PDF is replaced only after the new one is checked. An earlier version deleted the
# target before calling Chrome and destroyed 137 extracts when Chrome silently failed.
work = os.path.join(PRINT, '_render')
os.makedirs(work, exist_ok=True)
listing = os.path.join(work, 'jobs.tsv')
with open(listing, 'w', encoding='utf-8') as fh:
    for iso, v, src, pdf in jobs:
        fh.write('%s\t%s\n' % (src, pdf + '.new'))

ps1 = os.path.join(work, 'render.ps1')
with open(ps1, 'w', encoding='utf-8-sig', newline='\r\n') as fh:
    fh.write(
        '$ErrorActionPreference = "Stop"\n'
        '$chrome = %s\n'
        '$jobs = Get-Content -LiteralPath %s -Encoding UTF8\n'
        '$i = 0\n'
        'foreach ($line in $jobs) {\n'
        '  if (-not $line.Trim()) { continue }\n'
        '  $parts = $line -split "`t"\n'
        '  $src = $parts[0]; $out = $parts[1]\n'
        '  $url = "file:///" + ($src -replace "\\\\", "/")\n'
        '  $a = @("--headless=new","--disable-gpu","--no-sandbox",\n'
        '         "--user-data-dir=$env:TEMP\\claude\\chrome-extract","--hide-scrollbars",\n'
        '         "--no-pdf-header-footer","--virtual-time-budget=6000",\n'
        '         "--print-to-pdf=$out", $url)\n'
        '  try { Start-Process -FilePath $chrome -ArgumentList $a -PassThru -Wait '
        '-WindowStyle Hidden | Out-Null } catch { }\n'
        '  $i++\n'
        '  if ($i %% 30 -eq 0) { Write-Host ("  {0}/{1}" -f $i, $jobs.Count) }\n'
        '}\n' % (_psq(CHROME), _psq(listing)))

subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
                '-File', ps1], timeout=3600)

ok, failed = 0, []
for iso, v, src, pdf in jobs:
    new = pdf + '.new'
    if os.path.exists(new) and os.path.getsize(new) > 3000:
        os.replace(new, pdf)          # atomic; the old file survives until this point
        ok += 1
        if os.path.exists(src):
            os.remove(src)
    else:
        failed.append((iso, v))
        if os.path.exists(new):
            os.remove(new)

shutil.rmtree(work, ignore_errors=True)
print('rendered %d of %d in %.0fs' % (ok, len(jobs), time.time() - t0))
if failed:
    print('FAILED (previous PDF left in place): %d' % len(failed))
    for iso, v in failed[:12]:
        print('   %s %s' % (iso, v))
    sys.exit(1)
