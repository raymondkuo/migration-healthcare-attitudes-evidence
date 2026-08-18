# -*- coding: utf-8 -*-
"""Where a cited source went dead and was replaced, the register still displayed the
DEAD original in the source column and buried the replacement in a note. A reader
following the citation landed on a 404. Invert it: the source column names the source
the value is actually verified against, and the original citation moves to explicit
superseded_source_name / superseded_source_url columns.

Two rows had no retrievable source at all (a dead Japanese mirror, a dead Korean
secondary) and duplicated a row that WAS retrieved. They are folded into the row that
carries the live source, with the dead citation preserved in the superseded columns.

Every replacement URL below was checked live (HTTP 200) and the value it supports was
located in the archived copy before this script was written."""
import os
import pandas as pd

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(SITE, 'data')

ISMU_XLS = ('https://test.ismu.org/wp-content/uploads/2022/11/'
            'Stime-irregolari-ISMU_1991_2021_agg_maggio-2022.xls')
ISMU_NAME = ('Fondazione ISMU, Stima della presenza straniera in Italia per status '
             'giuridico-amministrativo, 1991-2021 (aggiornamento maggio 2022)')
ISMU_FILE = 'irregular_stock__ISMU_Stime_irregolari_1991_2021_agg_maggio2022.xls'
CARIPLO = 'https://www.fondazionecariplo.it/xxviii-rapporto-ismu-sulle-migrazioni-2022/'
SRF = ('https://www.srf.ch/news/schweiz/'
       'schweiz-sem-schaetzt-zahl-der-sans-papiers-in-der-schweiz-auf-76-000')

# key: (iso3, variable, years) of the row as it stands -> how it should read
REWRITE = {
    ('CHE', 'irregular_stock', '2015-2015'): dict(
        source_name='SRF News, "SEM schatzt Zahl der Sans-Papiers in der Schweiz auf 76\'000" '
                    '(25 April 2016), reporting the SEM study on its release',
        source_url=SRF,
        local_file='irregular_stock__SRF_SEM_76000_sanspapiers_CORROBORATION.html',
        note='The SEM study PDF originally cited now returns HTTP 404. The 76,000 figure is '
             'stated in this report on the study\'s release; the study\'s own range was '
             '58,000-105,000.'),
    ('ITA', 'irregular_stock', '2019-2019'): dict(
        source_name=ISMU_NAME, source_url=ISMU_XLS, local_file=ISMU_FILE,
        note='The originally cited press release returns HTTP 403 to every client, including a '
             'real browser. ISMU\'s own published series gives 2019 = 562,000.'),
    ('ITA', 'irregular_stock', '2020-2020'): dict(
        source_name=ISMU_NAME, source_url=ISMU_XLS, local_file=ISMU_FILE,
        note='The originally cited host is unreachable. ISMU\'s own published series gives '
             '2020 = 517,000.'),
}

# the 2021-2022 row must split: the ISMU series ends at 2021, so 2022 rests on a different
# document (the XXVIII Rapporto, which states 506mila against 519mila the year before)
SPLIT = {
    ('ITA', 'irregular_stock', '2021-2022'): [
        dict(years='2021-2021', n_obs=1, source_name=ISMU_NAME, source_url=ISMU_XLS,
             local_file=ISMU_FILE,
             note='The originally cited press release returns HTTP 403 to every client. '
                  'ISMU\'s own published series gives 2021 = 519,000.'),
        dict(years='2022-2022', n_obs=1,
             source_name='Fondazione Cariplo, XXVIII Rapporto ISMU sulle migrazioni 2022',
             source_url=CARIPLO,
             local_file='irregular_stock__Cariplo_XXVIII_Rapporto_ISMU_2022_CORROBORATION.html',
             note='The ISMU series ends at 2021, so 2022 rests on the XXVIII Rapporto, which '
                  'states 506mila irregular residents against 519mila the previous year.'),
    ],
}

# (iso3, variable, years, dead_url) folded into the row keyed by (iso3, variable, keep_years)
FOLD = [
    dict(iso3='JPN', variable='irregular_proxy_overstayers', drop_years='2014-2014',
         drop_url='https://www.nisshinkyo.org/news/pdf/G-26-2.pdf',
         keep_years='2014-2014',
         keep_url='https://www.moj.go.jp/isa/content/001459199.pdf',
         note='A mirror of this figure originally cited at nisshinkyo.org now returns HTTP 404. '
              'It is not needed: 59,061 for 1 January 2014 is printed in the Immigration '
              'Services Agency document archived here.'),
    dict(iso3='KOR', variable='irregular_proxy_overstayers', drop_years='2010-2015',
         drop_url='https://press.police.ac.kr/pds/1476878914562.pdf',
         keep_years='2010-2015',
         keep_url='https://www.korea.kr/archive/expDocView.do?docId=38074',
         note='The secondary source originally cited for these years is on a host that no longer '
              'responds. It is not relied upon: the values come from the Ministry of Justice '
              'yearbook archived here.'),
]

reg = pd.read_csv(os.path.join(D, 'source_register.csv')).fillna('')
for c in ('superseded_source_name', 'superseded_source_url'):
    if c not in reg.columns:
        reg[c] = ''


def find(iso3, variable, years, url=None):
    m = (reg.iso3 == iso3) & (reg.variable == variable) & (reg.years == years)
    if url is not None:
        m &= (reg.source_url == url)
    idx = reg.index[m]
    assert len(idx) == 1, '%s %s %s -> %d rows' % (iso3, variable, years, len(idx))
    return idx[0]


print('=== source column now names the source the value is verified against ===')
for (iso3, var, yrs), new in REWRITE.items():
    i = find(iso3, var, yrs)
    reg.at[i, 'superseded_source_name'] = reg.at[i, 'source_name']
    reg.at[i, 'superseded_source_url'] = reg.at[i, 'source_url']
    for k, v in new.items():
        reg.at[i, k] = v
    reg.at[i, 'retrieval'] = 'ARCHIVED'
    print(' %s %s %s' % (iso3, var, yrs))
    print('    now : %s' % new['source_url'][:92])
    print('    was : %s' % reg.at[i, 'superseded_source_url'][:92])

for (iso3, var, yrs), parts in SPLIT.items():
    i = find(iso3, var, yrs)
    base = reg.loc[i].to_dict()
    reg = reg.drop(index=i)
    for part in parts:
        row = dict(base)
        row['superseded_source_name'] = base['source_name']
        row['superseded_source_url'] = base['source_url']
        row['retrieval'] = 'ARCHIVED'
        row['outcome'] = 'SUBSTITUTED'
        row.update(part)
        reg = pd.concat([reg, pd.DataFrame([row])], ignore_index=True)
        print(' %s %s %s (split from %s)' % (iso3, var, part['years'], yrs))
        print('    now : %s' % part['source_url'][:92])
        print('    was : %s' % base['source_url'][:92])

print()
print('=== rows with no retrievable source, folded into the row that has one ===')
for f in FOLD:
    drop = find(f['iso3'], f['variable'], f['drop_years'], f['drop_url'])
    dead_name, dead_url = reg.at[drop, 'source_name'], reg.at[drop, 'source_url']
    reg = reg.drop(index=drop)
    keep = find(f['iso3'], f['variable'], f['keep_years'], f['keep_url'])
    reg.at[keep, 'superseded_source_name'] = dead_name
    reg.at[keep, 'superseded_source_url'] = dead_url
    reg.at[keep, 'note'] = f['note']
    reg.at[keep, 'outcome'] = 'SUPERSEDED_CITATION'
    print(' %s %s %s' % (f['iso3'], f['variable'], f['keep_years']))
    print('    kept   : %s' % f['keep_url'][:92])
    print('    dropped: %s' % dead_url[:92])

reg = reg.sort_values(['iso3', 'variable', 'years']).reset_index(drop=True)
reg.to_csv(os.path.join(D, 'source_register.csv'), index=False, encoding='utf-8-sig')

# ------------------------------------------------------------------ panel pointers
panel = os.path.join(D, 'panel_final.csv')
p = pd.read_csv(panel)
PANEL_FIX = {
    ('CHE', 2015): (REWRITE[('CHE', 'irregular_stock', '2015-2015')]['source_name'], SRF),
    ('ITA', 2019): (ISMU_NAME, ISMU_XLS),
    ('ITA', 2020): (ISMU_NAME, ISMU_XLS),
    ('ITA', 2021): (ISMU_NAME, ISMU_XLS),
    ('ITA', 2022): ('Fondazione Cariplo, XXVIII Rapporto ISMU sulle migrazioni 2022', CARIPLO),
}
print()
print('=== panel_final.csv: the number now points at the source that verifies it ===')
for (iso3, yr), (name, url) in PANEL_FIX.items():
    m = (p.iso3 == iso3) & (p.year == yr)
    assert m.sum() == 1 and p.loc[m, 'irregular_stock'].notna().all(), '%s %s' % (iso3, yr)
    old = p.loc[m, 'irregular_stock_url'].iloc[0]
    p.loc[m, 'irregular_stock_source'] = name
    p.loc[m, 'irregular_stock_url'] = url
    print(' %s %d  %s' % (iso3, yr, format(int(p.loc[m, 'irregular_stock'].iloc[0]), ',')))
    print('    now : %s' % url[:92])
    print('    was : %s' % str(old)[:92])
p.to_csv(panel, index=False, encoding='utf-8-sig')

# ------------------------------------------------------------------ per-country manifests
print()
for iso3 in ('CHE', 'ITA', 'JPN', 'KOR'):
    f = os.path.join(SITE, 'evidence', 'countries', iso3, 'source_manifest.csv')
    if not os.path.exists(f):
        continue
    sub = reg[reg.iso3 == iso3].copy()
    m = pd.read_csv(f).fillna('')
    keep = [c for c in m.columns if c in sub.columns]
    out = sub[keep + [c for c in ('superseded_source_name', 'superseded_source_url')
                      if c not in keep]]
    out.to_csv(f, index=False, encoding='utf-8-sig')
    print('rewrote %s (%d rows)' % (os.path.relpath(f, SITE), len(out)))

print()
print('register rows: %d' % len(reg))
print('rows with no local_file: %d'
      % int((reg.local_file.astype(str).str.strip().str.len() < 3).sum()))
print('rows carrying a superseded citation: %d'
      % int((reg.superseded_source_url.astype(str).str.len() > 3).sum()))
