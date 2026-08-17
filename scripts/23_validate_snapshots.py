# -*- coding: utf-8 -*-
"""Validate every web snapshot by dumping the rendered DOM for its URL. Any page
that answers with a bot-check / block interstitial is re-rendered from the HTML
copy archived on the access date."""
import os, re, subprocess, html
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(BASE, 'migration-data-archive')
EV = os.path.join(SITE, 'evidence', 'countries')
CHROME = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
PROFILE = os.path.join(os.environ.get('TEMP', 'C:/Windows/Temp'), 'claude', 'chrome-val')

BLOCK = ['sorry, you have been blocked', 'you are unable to access', 'just a moment',
         'checking your browser', 'verifying you are human', 'enable javascript and cookies',
         'access blocked', 'attention required', 'cf-browser-verification',
         'performing a security check', '正在執行安全驗證', '安全驗證',
         'request has been blocked', 'error 1015', 'access denied', '403 forbidden']


def text_of(h):
    h = re.sub(r'<(script|style|noscript).*?</\1>', ' ', h, flags=re.S | re.I)
    h = re.sub(r'<[^>]+>', ' ', h)
    return re.sub(r'\s+', ' ', html.unescape(h)).strip()


def dom(url, timeout=120):
    try:
        p = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
                            '--user-data-dir=' + PROFILE, '--virtual-time-budget=15000',
                            '--dump-dom', url], capture_output=True, timeout=timeout)
        return p.stdout.decode('utf8', 'replace')
    except Exception:
        return ''


def render(url, stem, iso):
    d = os.path.join(EV, iso)
    for args in ([('--no-pdf-header-footer', '--print-to-pdf=' + os.path.join(d, stem + '.pdf'))],
                 [('--window-size=1400,3200', '--screenshot=' + os.path.join(d, stem + '.png'))]):
        flat = [x for t in args for x in t]
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
                        '--user-data-dir=' + PROFILE, '--hide-scrollbars',
                        '--virtual-time-budget=15000'] + flat + [url],
                       capture_output=True, timeout=160)


snaps = pd.read_csv(os.path.join(SITE, 'data', 'web_snapshots.csv'))
reg = pd.read_csv(os.path.join(SITE, 'data', 'source_register.csv'))
url2local = {(r['iso3'], r['source_url']): str(r.get('local_file') or '')
             for _, r in reg.iterrows() if str(r.get('local_file') or '').endswith('.html')}

rows = []
for i, (_, s) in enumerate(snaps.iterrows(), 1):
    iso, url = s['iso3'], s['source_url']
    st = str(s.get('snapshot_status', ''))
    if st == 'rendered_from_archived_html' or str(s['png_screenshot']).endswith('.jpg'):
        rows.append(s.to_dict())
        print('%2d %-4s skip (%s)' % (i, iso, st or 'interactive capture'))
        continue

    body = text_of(dom(url))[:6000].lower()
    blocked = any(m in body for m in BLOCK) or len(body) < 400
    d = s.to_dict()
    if not blocked:
        d['snapshot_status'] = 'live_render_verified'
        print('%2d %-4s OK   %s' % (i, iso, url[:70]))
    else:
        local = url2local.get((iso, url), '')
        lp = os.path.join(EV, iso, local) if local else ''
        ok_local = False
        if lp and os.path.exists(lp):
            lt = text_of(open(lp, encoding='utf-8', errors='replace').read())
            ok_local = len(lt) > 800 and not any(m in lt.lower() for m in BLOCK)
        if ok_local:
            stem = str(s['png_screenshot']).replace('.png', '') + '__from_archived_html'
            render('file:///' + lp.replace('\\', '/'), stem, iso)
            for f in (s['pdf_mirror'], s['png_screenshot']):
                fp = os.path.join(EV, iso, str(f))
                if f and os.path.exists(fp):
                    os.remove(fp)
            d['pdf_mirror'], d['png_screenshot'] = stem + '.pdf', stem + '.png'
            d['pdf_bytes'] = os.path.getsize(os.path.join(EV, iso, stem + '.pdf')) \
                if os.path.exists(os.path.join(EV, iso, stem + '.pdf')) else 0
            d['png_bytes'] = os.path.getsize(os.path.join(EV, iso, stem + '.png')) \
                if os.path.exists(os.path.join(EV, iso, stem + '.png')) else 0
            d['snapshot_status'] = 'rendered_from_archived_html'
            print('%2d %-4s BLOCKED -> re-rendered from archived HTML  %s' % (i, iso, url[:52]))
        else:
            for f in (s['pdf_mirror'], s['png_screenshot']):
                fp = os.path.join(EV, iso, str(f))
                if f and os.path.exists(fp):
                    os.remove(fp)
            d['pdf_mirror'] = d['png_screenshot'] = ''
            d['pdf_bytes'] = d['png_bytes'] = 0
            d['snapshot_status'] = 'BLOCKED_no_usable_copy'
            print('%2d %-4s BLOCKED, no usable copy  %s' % (i, iso, url[:52]))
    d['archived_html'] = url2local.get((iso, url), '')
    rows.append(d)

out = pd.DataFrame(rows)
out.to_csv(os.path.join(SITE, 'data', 'web_snapshots.csv'), index=False, encoding='utf-8-sig')
print('\n' + out.snapshot_status.value_counts().to_string())
