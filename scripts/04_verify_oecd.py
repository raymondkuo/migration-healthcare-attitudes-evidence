# -*- coding: utf-8 -*-
"""Re-query every OECD SDMX URL cited in FILE2 and compare values."""
import os, json, re, ssl, time, urllib.request
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, 'data_raw', 'oecd')
OUT = os.path.join(BASE, 'verification')
os.makedirs(RAW, exist_ok=True)
F2 = os.path.join(BASE, 'migration_population_panel_40countries_2010-2022.xlsx')
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'

lg = pd.read_excel(F2, sheet_name='Long_all_observations')
oecd = lg[lg.source_url.astype(str).str.contains('sdmx.oecd.org')]
urls = sorted(oecd.source_url.unique())
print('OECD URLs cited:', len(urls))

results = []
for u in urls:
    m = re.search(r'DF_MIG[_A-Z]*,[\d.]+/([A-Z]{3})\.', u)
    tag = (m.group(1) if m else 'X') + '_' + re.search(r'\.(B1[45])\.', u).group(1)
    fn = os.path.join(RAW, tag + '.json')
    if not (os.path.exists(fn) and os.path.getsize(fn) > 200):
        try:
            req = urllib.request.Request(u, headers={'User-Agent': UA, 'Accept': 'application/vnd.sdmx.data+json,*/*'})
            with urllib.request.urlopen(req, timeout=120, context=ctx) as r:
                open(fn, 'wb').write(r.read())
            st = 'ok'
        except Exception as e:
            st = 'FAIL %s' % e
            print('  %-12s %s' % (tag, st)); results.append((u, tag, st, {})); time.sleep(1); continue
        time.sleep(1)
    else:
        st = 'cached'
    # parse SDMX-JSON (dimensionAtObservation=AllDimensions)
    try:
        d = json.load(open(fn, encoding='utf-8'))
        ds = d['data']['dataSets'][0]['observations']
        dims = d['data']['structures'][0]['dimensions']['observation'] \
            if 'structures' in d['data'] else d['data']['structure']['dimensions']['observation']
        tpos = [i for i, dd in enumerate(dims) if dd['id'] in ('TIME_PERIOD',)][0]
        tvals = [v['id'] for v in dims[tpos]['values']]
        series = {}
        for key, val in ds.items():
            parts = key.split(':')
            series[int(tvals[int(parts[tpos])])] = val[0]
        results.append((u, tag, st, series))
        print('  %-12s %-7s %d obs %s' % (tag, st, len(series), sorted(series)[:3]))
    except Exception as e:
        print('  %-12s parse FAIL %s' % (tag, e)); results.append((u, tag, st + '/parse-fail', {}))

rows = []
for u, tag, st, series in results:
    sub = oecd[oecd.source_url == u]
    for _, r in sub.iterrows():
        live = series.get(int(r['year']))
        v = float(r['value'])
        if live is None:
            status, diff, pct = ('SOURCE_UNAVAILABLE' if not series else 'SOURCE_MISSING'), None, None
        else:
            diff = v - float(live); pct = diff / float(live) * 100 if live else None
            status = 'EXACT' if abs(diff) < 0.5 else ('ROUNDING' if abs(pct) < 0.05 else
                     ('MINOR_DIFF' if abs(pct) < 1 else 'MISMATCH'))
        rows.append(dict(workbook='FILE2', country=r['country'], iso3=r['iso3'], year=int(r['year']),
                         variable=r['variable'], source='OECD IMD ' + tag, workbook_value=v,
                         live_source_value=live, diff=diff, pct_diff=pct, status=status, note=st))

df = pd.DataFrame(rows)
df.to_csv(os.path.join(OUT, 'value_checks_oecd.csv'), index=False, encoding='utf-8-sig')
print('\nchecked %d OECD values' % len(df))
print(df.groupby(['source', 'status']).size().to_string())
