# -*- coding: utf-8 -*-
"""Some live re-renders hit a bot-check interstitial instead of the page. Detect
those and re-render them from the HTML copy that was successfully archived on the
access date, so the snapshot shows the real content."""
import os, re, subprocess, html, shutil
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(BASE, 'migration-data-archive')
EV = os.path.join(SITE, 'evidence', 'countries')
CHROME = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
PROFILE = os.path.join(os.environ.get('TEMP', 'C:/Windows/Temp'), 'claude', 'chrome-snap-profile2')

BOT_MARKERS = ['正在執行安全驗證', 'Just a moment', 'Checking your browser',
               'cf-browser-verification', 'Enable JavaScript and cookies',
               'performing a security check', 'Access Blocked', 'HTTP 403',
               'Verifying you are human', 'challenge-platform']

snaps = pd.read_csv(os.path.join(SITE, 'data', 'web_snapshots.csv'))
reg = pd.read_csv(os.path.join(SITE, 'data', 'source_register.csv'))
url2local = {}
for _, r in reg.iterrows():
    lf = str(r.get('local_file') or '')
    if lf.endswith('.html'):
        url2local[(r['iso3'], r['source_url'])] = lf


def pdf_text(p):
    """Cheap text sniff: pull readable strings out of the PDF stream."""
    try:
        raw = open(p, 'rb').read()
    except Exception:
        return ''
    return ''.join(chr(b) if 32 <= b < 127 else ' ' for b in raw[:400000])


def html_text(p):
    t = open(p, encoding='utf-8', errors='replace').read()
    t = re.sub(r'<(script|style).*?</\1>', ' ', t, flags=re.S | re.I)
    t = re.sub(r'<[^>]+>', ' ', t)
    return re.sub(r'\s+', ' ', html.unescape(t))


rows = []
fixed = 0
for _, s in snaps.iterrows():
    if not s['png_screenshot'] or str(s['png_screenshot']).endswith('.jpg'):
        continue
    iso = s['iso3']
    png = os.path.join(EV, iso, s['png_screenshot'])
    pdf = os.path.join(EV, iso, s['pdf_mirror']) if s['pdf_mirror'] else ''
    suspicious = (s['png_bytes'] < 110000)
    blocked = False
    if suspicious and pdf and os.path.exists(pdf):
        txt = pdf_text(pdf)
        blocked = any(m.lower() in txt.lower() for m in
                      ['Just a moment', 'security check', 'Access Blocked', 'HTTP 403',
                       'challenge', 'Verifying you are human'])
        # non-latin interstitials will not survive the ascii sniff; fall back on size
        if not blocked and s['png_bytes'] < 60000:
            blocked = True
    local = url2local.get((iso, s['source_url']))
    status = 'live_render_ok'
    if blocked:
        if local and os.path.exists(os.path.join(EV, iso, local)):
            lp = os.path.join(EV, iso, local)
            body = html_text(lp)
            if any(m.lower() in body.lower() for m in BOT_MARKERS) or len(body) < 800:
                status = 'BLOCKED_no_usable_copy'
            else:
                stem = s['png_screenshot'].replace('.png', '') + '__from_archived_html'
                furl = 'file:///' + lp.replace('\\', '/')
                subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
                                '--user-data-dir=' + PROFILE, '--hide-scrollbars',
                                '--no-pdf-header-footer', '--virtual-time-budget=12000',
                                '--print-to-pdf=' + os.path.join(EV, iso, stem + '.pdf'), furl],
                               capture_output=True, timeout=140)
                subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
                                '--user-data-dir=' + PROFILE, '--hide-scrollbars',
                                '--window-size=1400,3200', '--virtual-time-budget=12000',
                                '--screenshot=' + os.path.join(EV, iso, stem + '.png'), furl],
                               capture_output=True, timeout=140)
                # drop the interstitial captures
                for f in (png, pdf):
                    if f and os.path.exists(f):
                        os.remove(f)
                s['png_screenshot'] = stem + '.png'
                s['pdf_mirror'] = stem + '.pdf'
                for k, f in (('png_bytes', stem + '.png'), ('pdf_bytes', stem + '.pdf')):
                    fp = os.path.join(EV, iso, f)
                    s[k] = os.path.getsize(fp) if os.path.exists(fp) else 0
                status = 'rendered_from_archived_html'
                fixed += 1
        else:
            status = 'BLOCKED_no_usable_copy'
        print('%-4s %-11s %s' % (iso, 'BLOCKED ->', status))
    d = s.to_dict()
    d['snapshot_status'] = status
    d['archived_html'] = local or ''
    rows.append(d)

out = pd.DataFrame(rows)
out.to_csv(os.path.join(SITE, 'data', 'web_snapshots.csv'), index=False, encoding='utf-8-sig')
print('\nre-rendered from archived HTML: %d' % fixed)
print(out.snapshot_status.value_counts().to_string())
