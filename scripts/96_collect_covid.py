# -*- coding: utf-8 -*-
"""COVID-19 cases and deaths reported in each calendar year 2020-2022, and each as a percentage of the
population, for every panel country (four variables).

Sources
  38 countries  WHO COVID-19 dashboard data, daily file (WHO-COVID-19-global-daily-data.csv): new and
                cumulative cases and deaths by the date they were reported to WHO. A year's value is WHO's
                cumulative count on 31 December minus the count on 31 December of the year before (asserted
                equal to the sum of the year's daily new counts). France: WHO lists the five overseas
                departments (Guadeloupe, Martinique, French Guiana, Reunion, Mayotte) as separate rows, and the
                World Bank's population of France includes them (its country-series note, archived), so they
                are added to France.
  China         WHO's "China" includes Hong Kong SAR, Macao SAR and Taiwan (WHO situation report 24, page 5,
                archived), and from 2022 its composition cannot be reconstructed. Mainland China is taken from
                the National Health Commission's briefings for 24:00 on 31 December 2020 and 2021, as published in
                English by China Daily's government portal (the Commission's own site answers automated requests
                with a bot check). 2022 has no traceable mainland figure: daily national reporting stopped in
                December 2022. The briefings also give Hong Kong, Macao and Taiwan; with them the 2021 mainland
                count reproduces WHO's China total exactly (checked).
  Taiwan        Not in WHO's data as such. Central Epidemic Command Center bulletins of 31 December 2020, 2021
                and 2022 (Taiwan CDC, English): cumulative laboratory-confirmed cases and cumulative deaths.
  Check         Johns Hopkins CSSE COVID-19 time series (GitHub, archived; pinned to the last commit of the
                files): annual values compared with the ones used (data/covid_source_comparison.csv).
  Percentages   cases / population x 100 and deaths / population x 100, with the panel's population of the
                same country and year (World Bank SP.POP.TOTL; Taiwan MOI). Computed by the archive.

Usage
  python scripts/96_collect_covid.py           parse the archived files only
  python scripts/96_collect_covid.py --fetch   download them first, and render the mirrors and publisher page

Writes data/extension_staging/covid_cells.csv (97_add_covid.py puts the cells into the panel) and
data/covid_source_comparison.csv.
"""
import html as _html
import json
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ext_lib as L                                    # noqa: E402
import covid_texts as CT                               # noqa: E402

SITE = os.path.dirname(HERE)
D = os.path.join(SITE, 'data')
API = os.path.join(SITE, 'evidence', 'api')
PUB = os.path.join(API, 'publisher_pages')
EVC = os.path.join(SITE, 'evidence', 'countries')
COLLECTED = CT.WHEN
YEARS = list(CT.YEARS)

WHO_URL = 'https://srhdpeuwpubsa.blob.core.windows.net/whdh/COVID/WHO-COVID-19-global-daily-data.csv'
WHO_FILE = 'who_COVID-19_global_daily_data_retrieved_%s.csv' % COLLECTED
WHO_PAGE = 'https://data.who.int/dashboards/covid19/data'
SITREP_URL = 'https://www.who.int/docs/default-source/coronaviruse/situation-reports/20200213-sitrep-24-covid-19.pdf'
SITREP_FILE = 'who_COVID-19_situation_report_24_2020-02-13_retrieved_%s.pdf' % COLLECTED
SITREP_PAGE = 5
WBFRA_URL = 'https://api.worldbank.org/v2/sources/2/country/FRA/series/SP.POP.TOTL/metadata?format=json'
WBFRA_FILE = 'wb_SP_POP_TOTL_FRA_country_series_note_retrieved_%s.json' % COLLECTED
JHU_COMMIT = '246b73fd28ebab168a764380a5cb62cb375c298d'
JHU_BASE = ('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/%s/csse_covid_19_data/csse_covid_19_time_series/'
            % JHU_COMMIT)
JHU = {k: ('time_series_covid19_%s_global.csv' % k,
           'jhu_csse_time_series_covid19_%s_global_%s_retrieved_%s.csv' % (k, JHU_COMMIT[:7], COLLECTED))
       for k in ('confirmed', 'deaths')}
CN_PAGES = {2020: 'https://govt.chinadaily.com.cn/s/202101/01/WS5ff2b1bf498eaba5051be45b/'
                  'jan-1-daily-briefing-on-novel-coronavirus-cases-in-china.html',
            2021: 'https://govt.chinadaily.com.cn/s/202201/01/WS61d42221498e6a12c121c594/'
                  'jan-1-daily-briefing-on-novel-coronavirus-cases-in-china.html'}
TW_PAGES = {2020: 'https://www.cdc.gov.tw/En/Bulletin/Detail/-ShMvyrZbj9DKWNTBPCyxQ?typeid=158',
            2021: 'https://www.cdc.gov.tw/En/Bulletin/Detail/geVzXO_h2mz_y2Mcv4tW5A?typeid=158',
            2022: 'https://www.cdc.gov.tw/En/Bulletin/Detail/ObLo-99cs63pMzlKVslGxA?typeid=158'}
CN_FILE = 'covid__NHC_briefing_%d-12-31__chinadaily__retrieved_%s.html'
TW_FILE = 'covid__CECC_bulletin_%d-12-31__retrieved_%s.html'
FR_DOM_CODES = ('GP', 'MQ', 'GF', 'RE', 'YT')

WHO_NAME = ('World Health Organization, COVID-19 dashboard data: cases and deaths by date reported to WHO (daily file '
            'WHO-COVID-19-global-daily-data.csv)')
CN_NAME = ('National Health Commission of China, daily briefing on COVID-19 for 24:00 on 31 December %d (mainland), '
           'English text published by China Daily\'s government portal')
TW_NAME = ('Taiwan Centers for Disease Control, Central Epidemic Command Center press release of 31 December %d '
           '(cumulative laboratory-confirmed cases and deaths)')
PUBLISHER_PAGES = [dict(key='who_covid19_dashboard', publisher='World Health Organization',
                        dataset='WHO COVID-19 dashboard - data download page', page_url=WHO_PAGE, backs_payload=WHO_FILE)]

P = pd.read_csv(os.path.join(D, 'panel_final.csv'), usecols=['iso3', 'iso2', 'year', 'population'])
ISO = sorted(P.iso3.unique())
I2 = dict(zip(P.iso2, P.iso3))
POP = {(r.iso3, int(r.year)): float(r.population) for r in P.itertuples()}
FETCH = '--fetch' in sys.argv


def fetch(url, dest, accept=None, minimum=1000):
    code, size = L.download(url, dest, accept=accept)
    print('%-72s http %s %12s bytes' % (os.path.basename(dest)[:72], code, format(size, ',')))
    if code != '200' or size < minimum:
        sys.exit('download failed: ' + url)
    return size


def upsert(path, rows, key):
    df = pd.read_csv(path)
    new = pd.DataFrame(rows)
    keep = df[~df[key].isin(new[key])]
    pd.concat([keep, new], ignore_index=True)[list(df.columns)].to_csv(path, index=False, encoding='utf-8-sig')


def page_text(path):
    s = open(path, encoding='utf-8', errors='replace').read()
    t = re.sub(r'<script.*?</script>|<style.*?</style>', '', s, flags=re.S)
    return re.sub(r'\s+', ' ', _html.unescape(re.sub(r'<[^>]+>', ' ', t)))


def num(s):
    return int(s.replace(',', ''))


if FETCH:
    new = []
    for f, url, desc, pub in (
            (WHO_FILE, WHO_URL, 'WHO COVID-19 dashboard data, daily file: new and cumulative cases and deaths by date '
                                'reported to WHO, every country and area, 2020 onwards', 'WHO'),
            (SITREP_FILE, SITREP_URL, 'WHO COVID-19 situation report 24 (13 February 2020): its footnote on page 5 says '
                                      'the cases of China include Hong Kong SAR, Macao SAR and Taipei and environs', 'WHO'),
            (WBFRA_FILE, WBFRA_URL, 'World Bank WDI country-series metadata of SP.POP.TOTL for France: the population '
                                    'includes the five overseas departments', 'World Bank WDI'),
            (JHU['confirmed'][1], JHU_BASE + JHU['confirmed'][0], 'Johns Hopkins CSSE COVID-19 time series, confirmed '
             'cases, global, at the last commit of the archived repository; the check of the values used',
             'Johns Hopkins University CSSE'),
            (JHU['deaths'][1], JHU_BASE + JHU['deaths'][0], 'Johns Hopkins CSSE COVID-19 time series, deaths, global, at '
             'the last commit of the archived repository; the check of the values used',
             'Johns Hopkins University CSSE')):
        size = fetch(url, os.path.join(API, f))
        new.append(dict(file=f, publisher=pub, description=desc, query_url=url, bytes=size, path='evidence/api/' + f))
    upsert(os.path.join(D, 'api_snapshots.csv'), new, 'file')
    for y, u in CN_PAGES.items():
        fetch(u, os.path.join(EVC, 'CHN', CN_FILE % (y, COLLECTED)), 'text/html')
    for y, u in TW_PAGES.items():
        fetch(u, os.path.join(EVC, 'TWN', TW_FILE % (y, COLLECTED)), 'text/html')

# ------------------------------------------------------------------ WHO
w = pd.read_csv(os.path.join(API, WHO_FILE), keep_default_na=False, na_values=[''], dtype={'Country_code': str})
w['year'] = w.Date_reported.str[:4].astype(int)
units = {I2[c]: [c] for c in I2 if c in set(w.Country_code)}
assert 'TW' not in set(w.Country_code), 'WHO now lists Taiwan'
units['FRA'] = ['FR'] + list(FR_DOM_CODES)
assert set(FR_DOM_CODES) <= set(w.Country_code), 'overseas departments missing from the WHO file'


def who_year(codes, y, col):
    tot = 0
    for c in codes:
        g = w[w.Country_code == c].sort_values('Date_reported')
        end = g[g.year == y]
        assert end.Date_reported.iloc[-1] == '%d-12-31' % y, (c, y, end.Date_reported.iloc[-1])
        prev = g[g.year < y]
        v = int(end['Cumulative_' + col].iloc[-1]) - (int(prev['Cumulative_' + col].iloc[-1]) if len(prev) else 0)
        assert v == int(end['New_' + col].fillna(0).sum()), (c, y, col)      # the year's daily counts add up
        tot += v
    return tot


who = {(iso, y): (who_year(codes, y, 'cases'), who_year(codes, y, 'deaths'))
       for iso, codes in units.items() for y in YEARS}
print('WHO: %d countries (France with its five overseas departments), annual values equal to the change in the '
      'cumulative counts and to the sum of the daily counts' % len(units))

# ------------------------------------------------------------------ mainland China (NHC briefings)
import fitz                                              # noqa: E402

sr = fitz.open(os.path.join(API, SITREP_FILE))
sr_text = re.sub(r'\s+', ' ', sr[SITREP_PAGE - 1].get_text())
sr.close()
assert 'Confirmed cases in China include cases confirmed in Hong Kong SAR' in sr_text and 'Taipei' in sr_text, 'sitrep'
cn, cn_parts = {}, {}
for y in CN_PAGES:
    t = page_text(os.path.join(EVC, 'CHN', CN_FILE % (y, COLLECTED)))
    m = re.search(r'As of 24:00 on Dec 31, the National Health Commission had received reports of ([\d,]+) confirmed '
                  r'cases and ([\d,]+) deaths in 31 provincial-level regions', t)
    hk = re.search(r'([\d,]+) in Hong Kong \(([\d,]+) had died', t)
    mo = re.search(r'([\d,]+) in Macao \(([^)]*)\)', t)
    tw = re.search(r'([\d,]+) in Taiwan \(([\d,]+) had died', t)
    assert m and hk and mo and tw, y
    mo_d = re.match(r'([\d,]+) had died', mo.group(2))
    cn[y] = (num(m.group(1)), num(m.group(2)))
    cn_parts[y] = dict(hk=(num(hk.group(1)), num(hk.group(2))), mo=(num(mo.group(1)), num(mo_d.group(1)) if mo_d else 0),
                       tw=(num(tw.group(1)), num(tw.group(2))))
# the 2021 year-end reproduces WHO's China total case for case
wc = w[w.Country_code == 'CN'].set_index('Date_reported')
tot21 = cn[2021][0] + sum(v[0] for v in cn_parts[2021].values())
assert tot21 == int(wc.loc['2021-12-31', 'Cumulative_cases']), (tot21, wc.loc['2021-12-31', 'Cumulative_cases'])
assert cn[2021][1] + sum(v[1] for v in cn_parts[2021].values()) == int(wc.loc['2021-12-31', 'Cumulative_deaths'])
cn_year = {2020: cn[2020], 2021: (cn[2021][0] - cn[2020][0], cn[2021][1] - cn[2020][1])}
print('China (mainland): 2020 %s, 2021 %s; mainland + Hong Kong + Macao + Taiwan on 31 Dec 2021 = WHO China (%s)'
      % (cn_year[2020], cn_year[2021], format(tot21, ',')))

# ------------------------------------------------------------------ Taiwan (CECC bulletins)
tw_cum = {}
for y in TW_PAGES:
    t = page_text(os.path.join(EVC, 'TWN', TW_FILE % (y, COLLECTED)))
    assert re.search(r'PublishTime：?\s*%d-12-31' % y, t), y
    c = re.search(r'laboratory-confirmed in ([\d,]+) cases', t)
    d = re.search(r'cumulative total of ([\d,]+) COVID-19 deaths', t) or re.search(r'there have been ([\d,]+) deaths', t)
    assert c and d, y
    tw_cum[y] = (num(c.group(1)), num(d.group(1)))
for y in (2020, 2021):                     # the NHC briefing quotes the same Taiwan totals
    assert tw_cum[y] == cn_parts[y]['tw'], (y, tw_cum[y], cn_parts[y]['tw'])
tw_year = {y: (tw_cum[y][0] - (tw_cum[y - 1][0] if y > 2020 else 0), tw_cum[y][1] - (tw_cum[y - 1][1] if y > 2020 else 0))
           for y in YEARS}
print('Taiwan: cumulative %s; annual %s' % (tw_cum, tw_year))

# ------------------------------------------------------------------ Johns Hopkins (check)
NAMES = pd.read_csv(os.path.join(D, 'panel_final.csv'), usecols=['iso3', 'country']).drop_duplicates() \
    .set_index('iso3').country.to_dict()
JHU_NAME = {'KOR': 'Korea, South', 'USA': 'US', 'RUS': 'Russia', 'CZE': 'Czechia', 'SVK': 'Slovakia'}
jhu = {}
for k, col in (('confirmed', 0), ('deaths', 1)):
    j = pd.read_csv(os.path.join(API, JHU[k][1]))
    for iso in ISO:
        if iso == 'TWN':
            sel = j[j['Country/Region'] == 'Taiwan*']
        elif iso == 'CHN':
            sel = j[(j['Country/Region'] == 'China') & ~j['Province/State'].isin(['Hong Kong', 'Macau'])]
        elif iso == 'FRA':
            sel = j[(j['Country/Region'] == 'France') & (j['Province/State'].isna() | j['Province/State'].isin(
                ['Guadeloupe', 'Martinique', 'French Guiana', 'Reunion', 'Mayotte']))]
        else:
            rows_ = j[j['Country/Region'] == JHU_NAME.get(iso, NAMES[iso])]
            # the national row where Johns Hopkins has one (other rows are overseas territories); Australia is
            # published by state only, so its states are added up
            sel = rows_[rows_['Province/State'].isna()] if rows_['Province/State'].isna().any() else rows_
        assert len(sel), (iso, k)
        prev = 0
        for y in YEARS:
            cum = int(sel['12/31/%02d' % (y % 100)].sum())
            jhu.setdefault((iso, y), [None, None])[col] = cum - prev
            prev = cum

# ------------------------------------------------------------------ cells and comparison
VER_WHO = ('Read from the archived WHO daily file (evidence/api/%s): the cumulative count on 31 December minus the one on '
           '31 December of the year before, equal to the sum of the year\'s daily counts%s. Retrieved %s.')
rows, cmp_rows = [], []
for iso in ISO:
    for y in YEARS:
        pop = POP[(iso, y)]
        if iso == 'TWN':
            (c, d), src = tw_year[y], 'CECC'
            url, lf, name, grade = TW_PAGES[y], TW_FILE % (y, COLLECTED), TW_NAME % y, 'B'
            ref = 'Calendar year (cumulative count announced on 31 December, minus the previous year-end count)'
            note = ('Taiwan CECC: cumulative laboratory-confirmed cases and cumulative deaths announced on 31 December %d '
                    '(%s cases, %s deaths)%s; the year\'s value is the difference.'
                    % (y, format(tw_cum[y][0], ','), format(tw_cum[y][1], ','),
                       '' if y == 2020 else ', minus those of 31 December %d' % (y - 1)))
            ver = ('Read from the archived CECC press release of 31 December %d (evidence/countries/TWN/%s)%s; the National '
                   'Health Commission\'s briefing quotes the same Taiwan totals for 2020 and 2021. Retrieved %s.'
                   % (y, lf, '' if y == 2020 else ' and the one of 31 December %d' % (y - 1), COLLECTED))
        elif iso == 'CHN':
            if y not in cn_year:
                cmp_rows.append(dict(iso3=iso, year=y, source_used='', cases='', deaths='', population=repr(pop),
                                     cases_pct='', deaths_pct='', who_cases=who[(iso, y)][0], who_deaths=who[(iso, y)][1],
                                     jhu_cases=jhu[(iso, y)][0], jhu_deaths=jhu[(iso, y)][1],
                                     note='No mainland figure: national daily reporting stopped in December 2022; WHO\'s '
                                          '"China" includes Hong Kong, Macao and Taiwan.'))
                continue
            (c, d), src = cn_year[y], 'NHC'
            url, lf, name, grade = CN_PAGES[y], CN_FILE % (y, COLLECTED), CN_NAME % y, 'B'
            ref = 'Calendar year (cumulative count as of 24:00 on 31 December, minus the previous year-end count)'
            note = ('Mainland China (31 provincial-level regions and the Xinjiang Production and Construction Corps), '
                    'National Health Commission: %s confirmed cases and %s deaths reported by 24:00 on 31 December %d%s; '
                    'Hong Kong, Macao and Taiwan are not included (WHO\'s "China" includes them).'
                    % (format(cn[y][0], ','), format(cn[y][1], ','), y,
                       '' if y == 2020 else ', minus those of 31 December %d' % (y - 1)))
            ver = ('Read from the archived briefing (evidence/countries/CHN/%s)%s. The same briefing gives Hong Kong, Macao '
                   'and Taiwan; with them the 31 December 2021 counts equal WHO\'s China totals case for case. Retrieved %s.'
                   % (lf, '' if y == 2020 else ' and the one of 31 December %d' % (y - 1), COLLECTED))
        else:
            (c, d), src = who[(iso, y)], 'WHO'
            url, lf, name, grade = WHO_URL, 'evidence/api/' + WHO_FILE, WHO_NAME, 'A'
            ref = 'Calendar year (1 January-31 December, by date reported to WHO)'
            note = ('WHO, cases and deaths by date reported%s.'
                    % (': France plus Guadeloupe, Martinique, French Guiana, Reunion and Mayotte, which WHO lists '
                       'separately and the World Bank population of France includes' if iso == 'FRA' else ''))
            ver = VER_WHO % (WHO_FILE, ' (France: the sum of France and its five overseas departments)' if iso == 'FRA'
                             else '', COLLECTED)
        cpct, dpct = 100.0 * c / pop, 100.0 * d / pop
        for var, val, extra in ((CT.CASES, c, ''), (CT.DEATHS, d, ''),
                                (CT.CASES_PCT, cpct, ' Computed by the archive: %s cases / population %s x 100 (the '
                                                     'panel\'s population of %s %d).' % (format(c, ','), format(int(pop), ','), iso, y)),
                                (CT.DEATHS_PCT, dpct, ' Computed by the archive: %s deaths / population %s x 100 (the '
                                                      'panel\'s population of %s %d).' % (format(d, ','), format(int(pop), ','), iso, y))):
            rows.append(L.cell(iso, y, var, val, 'COVID_' + src, name, url, lf, ref, grade, CT.SOURCE_TYPE,
                               note=note + extra, flag='', verification=ver, collected_on=COLLECTED))
        cmp_rows.append(dict(iso3=iso, year=y, source_used=src, cases=c, deaths=d, population=repr(pop),
                             cases_pct=repr(cpct), deaths_pct=repr(dpct),
                             who_cases='' if iso == 'TWN' else who[(iso, y)][0],
                             who_deaths='' if iso == 'TWN' else who[(iso, y)][1],
                             jhu_cases=jhu[(iso, y)][0], jhu_deaths=jhu[(iso, y)][1],
                             note={'CHN': 'WHO\'s "China" includes Hong Kong, Macao and Taiwan.',
                                   'FRA': 'France with its five overseas departments (WHO and Johns Hopkins alike).'}
                             .get(iso, '')))
out = L.write_stage('covid_cells.csv', rows)
print('cells written: %d (%d country-years x 4 variables)' % (len(out), len(out) // 4))
pd.DataFrame(cmp_rows).to_csv(CT.CMP, index=False, encoding='utf-8-sig')
cm = pd.DataFrame(cmp_rows)
cm = cm[cm.cases != '']
within = lambda a, b: (a - b).abs() <= 0.01 * b.clip(lower=1)
print('Johns Hopkins within 1%%: cases %d of %d, deaths %d of %d'
      % (within(cm.jhu_cases.astype(float), cm.cases.astype(float)).sum(), len(cm),
         within(cm.jhu_deaths.astype(float), cm.deaths.astype(float)).sum(), len(cm)))

# ------------------------------------------------------------------ mirrors, extracts, publisher page
if FETCH:
    mirrors = []
    made = []
    for col, lab in ((0, 'cases'), (1, 'deaths')):
        g = {iso: {y: who[(iso, y)][col] for y in YEARS} for iso in sorted(units)}
        base = os.path.join(API, 'MIRROR__%s__annual_%s' % (os.path.splitext(WHO_FILE)[0], lab))
        made += L.grid_mirror('WHO COVID-19 data - %s reported in the calendar year' % lab,
                              'Archived file %s (query %s), retrieved %s. Cumulative count on 31 December minus the one a '
                              'year earlier. France includes its five overseas departments; "CHN" is WHO\'s China, which '
                              'includes Hong Kong, Macao and Taiwan (the panel uses the mainland figures).'
                              % (WHO_FILE, WHO_URL, COLLECTED), g, YEARS, base)
    mirrors.append(dict(scope='API', folder='evidence/api', source_file=WHO_FILE,
                        mirrors=';'.join(os.path.basename(m) for m in made), n_mirrors=len(made)))
    for k, col in (('confirmed', 0), ('deaths', 1)):
        g = {iso: {y: jhu[(iso, y)][col] for y in YEARS} for iso in ISO}
        base = os.path.join(API, 'MIRROR__' + os.path.splitext(JHU[k][1])[0])
        made = L.grid_mirror('Johns Hopkins CSSE - %s in the calendar year (from the cumulative time series)' % k,
                             'Archived file %s (commit %s), retrieved %s. CHN = mainland provinces; FRA with its five '
                             'overseas departments.' % (JHU[k][1], JHU_COMMIT[:7], COLLECTED), g, YEARS, base)
        mirrors.append(dict(scope='API', folder='evidence/api', source_file=JHU[k][1],
                            mirrors=';'.join(os.path.basename(m) for m in made), n_mirrors=len(made)))
    made = L.page_extract(os.path.join(API, SITREP_FILE), SITREP_PAGE,
                          os.path.join(API, 'MIRROR__%s__p%d' % (os.path.splitext(SITREP_FILE)[0], SITREP_PAGE)))
    mirrors.append(dict(scope='API', folder='evidence/api', source_file=SITREP_FILE,
                        mirrors=';'.join(os.path.basename(m) for m in made), n_mirrors=len(made)))
    fm = json.load(open(os.path.join(API, WBFRA_FILE), encoding='utf-8-sig'))
    notes = []

    def walk(x):
        if isinstance(x, dict):
            if x.get('id') in ('Country-Series', 'Longdefinition') and isinstance(x.get('value'), str):
                notes.append((x['id'], x['value']))
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for i in x:
                walk(i)
    walk(fm)
    mb = os.path.join(API, 'MIRROR__' + os.path.splitext(WBFRA_FILE)[0])
    L.table_extract('World Bank WDI - SP.POP.TOTL, France: country-series note', ['Field', 'Value'],
                    [([k_, v_], k_ == 'Country-Series') for k_, v_ in notes], mb,
                    'Archived file %s from %s, retrieved %s.' % (WBFRA_FILE, WBFRA_URL, COLLECTED),
                    note='The fields of the archived response, unchanged. Rendered %s.' % COLLECTED)
    mirrors.append(dict(scope='API', folder='evidence/api', source_file=WBFRA_FILE,
                        mirrors='%s;%s' % (os.path.basename(mb + '.pdf'), os.path.basename(mb + '.png')), n_mirrors=2))
    # the briefings and bulletins, rendered from the archived copies (with the page's own address as base)
    for iso, pages, fname in (('CHN', CN_PAGES, CN_FILE), ('TWN', TW_PAGES, TW_FILE)):
        for y, u in pages.items():
            f = fname % (y, COLLECTED)
            folder = os.path.join(EVC, iso)
            hb = os.path.join(folder, 'MIRROR__' + os.path.splitext(f)[0])
            raw = open(os.path.join(folder, f), encoding='utf-8', errors='replace').read()
            tmp = hb + '.tmp.html'
            open(tmp, 'w', encoding='utf-8').write(re.sub(r'(<head[^>]*>)', r'\1<base href="%s">' % u, raw, count=1,
                                                          flags=re.I))
            made = L.chrome_render('file:///' + tmp.replace(chr(92), '/'), pdf=hb + '.pdf', png=hb + '.png')
            os.remove(tmp)
            mirrors.append(dict(scope=iso, folder='evidence/countries/%s' % iso, source_file=f,
                                mirrors=';'.join(os.path.basename(m) for m in made), n_mirrors=len(made)))
            print('mirror %-60s %s' % (f[:60], [os.path.basename(m) for m in made]))
    sm = os.path.join(D, 'source_mirrors.csv')
    old = pd.read_csv(sm)
    old = old[~(old.source_file.isin([m['source_file'] for m in mirrors]))]
    pd.concat([old, pd.DataFrame(mirrors)], ignore_index=True).to_csv(sm, index=False, encoding='utf-8-sig')

    pubrows = []
    for p in PUBLISHER_PAGES:
        b = os.path.join(PUB, p['key'])
        made = L.chrome_render(p['page_url'], pdf=b + '.pdf', png=b + '.png', wait_ms=30000)
        pubrows.append(dict(p, status='captured' if len(made) == 2 else 'partial',
                            pdf='evidence/api/publisher_pages/%s.pdf' % p['key'] if b + '.pdf' in made else '',
                            png='evidence/api/publisher_pages/%s.png' % p['key'] if b + '.png' in made else '',
                            pdf_bytes=os.path.getsize(b + '.pdf') if b + '.pdf' in made else 0,
                            png_bytes=os.path.getsize(b + '.png') if b + '.png' in made else 0,
                            captured=COLLECTED, note=''))
        print('publisher page %-30s %s' % (p['key'], [os.path.basename(m) for m in made]))
    upsert(os.path.join(D, 'api_publisher_snapshots.csv'), pubrows, 'key')
