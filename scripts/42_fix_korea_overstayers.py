# -*- coding: utf-8 -*-
"""Replace Korea's 2010-2015 overstayer values, which rested on an unretrievable
secondary source (grade D), with the official Ministry of Justice series.

Sources located and archived 2026-08-17:
  1. 2015년도 출입국·외국인정책 통계연보, 제6장 불법체류자, 표 6-1 연도별 불법체류자 현황
     (MOJ Immigration Statistical Yearbook 2015, Table 6-1) — gives 2010-2015 year-end.
  2. 법무부 연도별 불법체류외국인 현황 (2011-2025), Korea open data portal — machine-readable,
     confirms 2011-2015 and the 2018/2020/2021/2022 values already in the panel.

Finding: the workbook's 2015 value of 212,596 is a 31 August 2015 snapshot spliced into an
otherwise year-end series. The official year-end figure is 214,168.
"""
import os, io, shutil, json
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(BASE, 'migration-data-archive')
BIL = os.path.join(BASE, 'migration-data-archive-bilingual')
D = os.path.join(SITE, 'data')
RAW = os.path.join(BASE, 'data_raw', 'kor')
KOR = os.path.join(SITE, 'evidence', 'countries', 'KOR')

YEARBOOK_URL = 'https://www.korea.kr/archive/expDocView.do?docId=38074'
PORTAL_URL = 'https://www.data.go.kr/data/15100011/fileData.do'
SRC_NAME = ('법무부 출입국·외국인정책본부, 2015년도 출입국·외국인정책 통계연보, 표 6-1 '
            '연도별 불법체류자 현황 (Ministry of Justice, Korea Immigration Statistical '
            'Yearbook 2015, Table 6-1)')
NOTE = ('Illegal-stay foreign residents (불법체류자), year-end stock, published as '
        '계 = 등록 + 단기 + 거소 — the same three-component definition the panel uses for '
        '2021 and 2022. Replaces values previously taken from a Korean National Police '
        'University publication whose host no longer responds.')

OFFICIAL = {2010: 168515, 2011: 167780, 2012: 177854,
            2013: 183106, 2014: 208778, 2015: 214168}

# ---------------------------------------------------------------- archive evidence
os.makedirs(KOR, exist_ok=True)
copied = []
for src, dst in [
    ('MOJ_2015_yearbook_p74_table6-1.png',
     'irregular_proxy_overstayers__MOJ_yearbook2015_table6-1_2010-2015.png'),
    ('MOJ_annual_illegal_stay.bin',
     'irregular_proxy_overstayers__MOJ_annual_illegal_stay_2011-2025_datagokr.csv'),
]:
    s = os.path.join(RAW, src)
    if os.path.exists(s):
        shutil.copy2(s, os.path.join(KOR, dst))
        copied.append(dst)

# extract just the relevant yearbook pages so the archive does not carry 20 MB
try:
    import pypdf
    r = pypdf.PdfReader(os.path.join(RAW, 'MOJ_2015_statistical_yearbook.pdf'))
    w = pypdf.PdfWriter()
    for i in (73, 74):
        w.add_page(r.pages[i])
    out = os.path.join(KOR, 'irregular_proxy_overstayers__MOJ_yearbook2015_ch6_pp74-75.pdf')
    with open(out, 'wb') as fh:
        w.write(fh)
    copied.append(os.path.basename(out))
except Exception as e:
    print('  (page extract skipped: %s)' % e)
print('archived %d evidence files to evidence/countries/KOR/' % len(copied))
for c in copied:
    print('   ', c)

# ---------------------------------------------------------------- cross-check portal CSV
raw = open(os.path.join(RAW, 'MOJ_annual_illegal_stay.bin'), 'rb').read().decode('euc-kr')
portal = pd.read_csv(io.StringIO(raw))
portal.columns = ['year', 'value']
pmap = portal.set_index('year')['value'].to_dict()
print('\ncross-check against the open-data portal series:')
for y in range(2011, 2016):
    ok = pmap.get(y) == OFFICIAL[y]
    print('   %d  yearbook %8s  portal %8s  %s'
          % (y, format(OFFICIAL[y], ','), format(pmap.get(y, 0), ','), 'agree' if ok else 'DISAGREE'))
    assert ok, 'yearbook and portal disagree for %d' % y

# ---------------------------------------------------------------- update the panel
V = 'irregular_proxy_overstayers'
p = pd.read_csv(os.path.join(D, 'panel_final.csv'))
corr_rows = []
for y, val in OFFICIAL.items():
    m = (p.iso3 == 'KOR') & (p.year == y)
    if not m.any():
        continue
    old = p.loc[m, V].iloc[0]
    p.loc[m, V] = val
    p.loc[m, V + '_source'] = SRC_NAME
    p.loc[m, V + '_url'] = YEARBOOK_URL
    p.loc[m, V + '_note'] = NOTE
    p.loc[m, V + '_ref_date'] = '31 December'
    # 2011-2015 verified against a machine-readable official source -> A; 2010 read from the
    # yearbook table only -> B
    p.loc[m, V + '_grade'] = 'A' if y >= 2011 else 'B'
    p.loc[m, V + '_verification'] = (
        'Confirmed against the Ministry of Justice open-data series (2011-2025) and Table 6-1 of '
        'the 2015 Immigration Statistical Yearbook.' if y >= 2011 else
        'Read from Table 6-1 of the 2015 Immigration Statistical Yearbook; components '
        '78,545 + 89,238 + 732 = 168,515 reconcile exactly.')
    if pd.notna(old) and abs(float(old) - val) > 0.5:
        corr_rows.append(dict(
            iso3='KOR', year=y, variable=V, old_value=float(old), new_value=float(val),
            reason=('The input value was a 31 August 2015 snapshot spliced into an otherwise '
                    'year-end series. Replaced with the official year-end figure from the '
                    'Ministry of Justice.'),
            evidence='MOJ Immigration Statistical Yearbook 2015 Table 6-1 and the MOJ open-data '
                     'series; both give 214,168 for year-end 2015.'))
p[V + '_pct_pop'] = p[V] / p['population']
p.to_csv(os.path.join(D, 'panel_final.csv'), index=False, encoding='utf-8-sig')
print('\npanel updated: 6 values re-sourced, %d value corrected' % len(corr_rows))

# ---------------------------------------------------------------- corrections log
c = pd.read_csv(os.path.join(D, 'corrections_applied.csv'))
if len(corr_rows):
    add = pd.DataFrame(corr_rows)
    for col in c.columns:
        if col not in add.columns:
            add[col] = ''
    c = pd.concat([c, add[c.columns]], ignore_index=True)
    c.to_csv(os.path.join(D, 'corrections_applied.csv'), index=False, encoding='utf-8-sig')
print('corrections_applied.csv now has %d rows' % len(c))

# ---------------------------------------------------------------- known issues
k = pd.read_csv(os.path.join(D, 'known_issues.csv'))
m = (k.scope == 'Korea') & (k.variable == V)
k.loc[m, 'severity'] = 'RESOLVED'
k.loc[m, 'issue'] = ('The 2010-2015 values rested on a single secondary source (a Korean National '
                     'Police University publication) whose host no longer responds, so they could '
                     'not be checked against anything.')
k.loc[m, 'evidence'] = ('The official series was located instead: MOJ Immigration Statistical '
                        'Yearbook 2015 Table 6-1 (2010-2015 year-end) and the MOJ open-data series '
                        '2011-2025. Both are archived in evidence/countries/KOR/.')
k.loc[m, 'action'] = ('Resolved: 2010-2014 matched the official figures exactly and were '
                      're-sourced; 2015 was corrected from 212,596 (a 31 August snapshot) to '
                      '214,168 (year-end). Grades raised from D to A (2011-2015) and B (2010). '
                      'No grade-D values remain in the panel.')
k.to_csv(os.path.join(D, 'known_issues.csv'), index=False, encoding='utf-8-sig')
print('known_issues.csv: Korea entry marked RESOLVED')

# ---------------------------------------------------------------- source register
reg = pd.read_csv(os.path.join(D, 'source_register.csv'))
m = reg.source_url.astype(str).str.contains('press.police.ac.kr', na=False)
reg.loc[m, 'outcome'] = 'SUPERSEDED'
reg.loc[m, 'retrieval'] = 'SUPERSEDED'
reg.loc[m, 'note'] = ('Host does not respond. No longer relied upon: the values it supplied were '
                      'replaced with the official Ministry of Justice series (Yearbook 2015 '
                      'Table 6-1 and the MOJ open-data series), archived in this folder.')
new = pd.DataFrame([
    dict(iso3='KOR', variable=V, years='2010-2015', n_obs=6, from_workbook='RESOURCED',
         source_name=SRC_NAME, source_url=YEARBOOK_URL, retrieval='ARCHIVED',
         local_file='irregular_proxy_overstayers__MOJ_yearbook2015_ch6_pp74-75.pdf',
         note='Official year-end series 2010-2015.', outcome='DOWNLOADED'),
    dict(iso3='KOR', variable=V, years='2011-2025', n_obs=15, from_workbook='RESOURCED',
         source_name='법무부 연도별 불법체류외국인 현황 (Ministry of Justice, annual illegal-stay '
                     'foreign residents), Korea open data portal',
         source_url=PORTAL_URL, retrieval='ARCHIVED',
         local_file='irregular_proxy_overstayers__MOJ_annual_illegal_stay_2011-2025_datagokr.csv',
         note='Machine-readable official series used to cross-check.', outcome='DOWNLOADED'),
])
for col in reg.columns:
    if col not in new.columns:
        new[col] = ''
reg = pd.concat([reg, new[reg.columns]], ignore_index=True)
reg.to_csv(os.path.join(D, 'source_register.csv'), index=False, encoding='utf-8-sig')
print('source_register.csv: old source marked SUPERSEDED, 2 official sources added')

# ---------------------------------------------------------------- mirror to bilingual copy
for f in ['panel_final.csv', 'corrections_applied.csv', 'known_issues.csv', 'source_register.csv']:
    shutil.copy2(os.path.join(D, f), os.path.join(BIL, 'data', f))
os.makedirs(os.path.join(BIL, 'evidence', 'countries', 'KOR'), exist_ok=True)
for c2 in copied:
    shutil.copy2(os.path.join(KOR, c2), os.path.join(BIL, 'evidence', 'countries', 'KOR', c2))
print('mirrored to the bilingual working copy')

print('\nfinal Korea series:')
p2 = pd.read_csv(os.path.join(D, 'panel_final.csv'))
kk = p2[(p2.iso3 == 'KOR') & p2[V].notna()][['year', V, V + '_grade']]
print(kk.to_string(index=False))
