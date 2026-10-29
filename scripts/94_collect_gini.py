# -*- coding: utf-8 -*-
"""Gini index for every panel country, 2001-2022 (the years of the population and migrant series),
wherever a household survey exists: 100 x the Gini coefficient of income (or consumption) per person.

Sources
  38 countries  World Bank, World Development Indicators SI.POV.GINI, which the World Bank takes from its
                Poverty and Inequality Platform (PIP). Read from the World Bank API and checked cell by
                cell against PIP's own table of survey estimates (PIP API, version pinned below): a WDI
                value is used only if it equals 100 x the Gini of a national PIP survey row of the same
                country and year, rounded to one decimal. The matching row gives the welfare type (income or
                consumption), the survey and its comparability spell. Where a country-year has both an
                income and a consumption survey, WDI publishes the income one (checked on every such case).
  Taiwan        Not in WDI. PIP holds Taiwan's surveys (FIDES-LIS: the DGBAS Survey of Family Income and
                Expenditure, harmonised by LIS); the value is PIP's Gini x 100, rounded to one decimal half up,
                the rule every WDI value above follows.
  New Zealand   The World Bank has no New Zealand data. OECD Income Distribution Database (IDD): Gini of
                equivalised household disposable income, total population, 2012 income definition
                (INC_DISP_GINI, METH2012, D_CUR), OECD SDMX API, x 100. A different income concept (flagged).
  Years without a survey have no value; nothing is interpolated.

Flags
  "consumption-based (not income)" where the survey measures consumption;
  "break in time series: new PIP survey-comparability spell" at the first year of a spell the World Bank
  marks as not comparable with the country's earlier one (within the years used);
  "OECD equivalised disposable income (not World Bank)" on New Zealand.

Usage
  python scripts/94_collect_gini.py           parse the archived files only
  python scripts/94_collect_gini.py --fetch   download them first, and render the mirrors and publisher pages

Writes data/extension_staging/gini_cells.csv (95_add_gini.py puts the cells into the panel) and
data/gini_source_comparison.csv (WDI, PIP and OECD side by side for every country-year).
"""
import json
import os
import re
import sys
from decimal import Decimal, ROUND_HALF_UP

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ext_lib as L                                    # noqa: E402
import gini_texts as GT                                # noqa: E402

SITE = os.path.dirname(HERE)
D = os.path.join(SITE, 'data')
API = os.path.join(SITE, 'evidence', 'api')
PUB = os.path.join(API, 'publisher_pages')
COLLECTED = GT.WHEN
YEARS = list(range(2001, 2023))
VAR = GT.VAR
PV = GT.PIP_VERSION

WB_BASE = 'https://api.worldbank.org/v2/country/all/indicator/SI.POV.GINI'
WB_URL = WB_BASE + '?format=json&date=2001:2022&per_page=20000'
WB_FILE = 'wb_SI_POV_GINI_2001-2022_retrieved_%s.json' % COLLECTED
WB_META_URL = 'https://api.worldbank.org/v2/indicator/SI.POV.GINI?format=json'
WB_META = 'wb_SI_POV_GINI_indicator_metadata_retrieved_%s.json' % COLLECTED
PIP_BASE = 'https://api.worldbank.org/pip/v1/pip'
PIP_URL = PIP_BASE + '?country=all&year=all&fill_gaps=false&version=%s&format=csv' % PV
PIP_FILE = 'pip_survey_estimates_%s_retrieved_%s.csv' % (PV, COLLECTED)
PIP_CIT_URL = 'https://api.worldbank.org/pip/v1/citation?version=%s' % PV
PIP_CIT = 'pip_citation_%s_retrieved_%s.json' % (PV, COLLECTED)
OECD_BASE = ('https://sdmx.oecd.org/public/rest/data/OECD.WISE.INE,DSD_WISE_IDD@DF_IDD,1.0/'
             'NZL.A.INC_DISP_GINI..0_TO_1._T.METH2012.D_CUR.')
OECD_URL = OECD_BASE + '?startPeriod=2001&endPeriod=2022'
OECD_ACCEPT = 'application/vnd.sdmx.data+csv;version=1.0.0'
OECD_FILE = 'oecd_IDD_NZL_INC_DISP_GINI_2001-2022_retrieved_%s.csv' % COLLECTED
OECD_DF_URL = 'https://sdmx.oecd.org/public/rest/dataflow/OECD.WISE.INE/DSD_WISE_IDD@DF_IDD/1.0?references=all'
OECD_DF = 'oecd_IDD_dataflow_retrieved_%s.xml' % COLLECTED

WB_NAME = ('World Bank, World Development Indicators: Gini index (SI.POV.GINI), from the Poverty and Inequality '
           'Platform (PIP version %s)' % PV)
PIP_NAME = ('World Bank, Poverty and Inequality Platform (PIP version %s): survey estimate for Taiwan, China '
            '(FIDES-LIS), Gini x 100' % PV)
OECD_NAME = ('OECD Income Distribution Database (IDD): Gini coefficient of equivalised household disposable income, '
             'total population, 2012 income definition (INC_DISP_GINI, METH2012, D_CUR), OECD SDMX API, x 100')
PUBLISHER_PAGES = [
    dict(key='worldbank_SI_POV_GINI', publisher='World Bank',
         dataset='World Development Indicators - Gini index (SI.POV.GINI)',
         page_url='https://data.worldbank.org/indicator/SI.POV.GINI', backs_payload=WB_FILE),
    dict(key='worldbank_pip_TWN', publisher='World Bank',
         dataset='Poverty and Inequality Platform - country profile, Taiwan, China',
         page_url='https://pip.worldbank.org/country-profiles/TWN', backs_payload=PIP_FILE),
    # the OECD's own site answers a headless browser with a bot check; its Data Explorer shows the same series
    dict(key='oecd_idd', publisher='OECD',
         dataset='OECD Income Distribution Database (IDD) in the OECD Data Explorer, New Zealand, Gini (disposable income)',
         page_url=('https://data-explorer.oecd.org/vis?df[ds]=dsDisseminateFinalDMZ&df[id]=DSD_WISE_IDD%40DF_IDD'
                   '&df[ag]=OECD.WISE.INE&dq=NZL.A.INC_DISP_GINI..0_TO_1._T.METH2012.D_CUR.&pd=2001%2C2022'
                   '&to[TIME_PERIOD]=false'),
         backs_payload=OECD_FILE),
]

P = pd.read_csv(os.path.join(D, 'panel_final.csv'), usecols=['iso3', 'year'])
ISO = sorted(P.iso3.unique())
FETCH = '--fetch' in sys.argv


def fetch(url, dest, accept=None, minimum=200):
    code, size = L.download(url, dest, accept=accept)
    print('%-72s http %s %12s bytes' % (os.path.basename(dest)[:72], code, format(size, ',')))
    if code != '200' or size < minimum:
        sys.exit('download failed: ' + url)
    return size


def upsert(path, rows, key):
    df = pd.read_csv(path)
    new = pd.DataFrame(rows)
    keep = df[~df[key].isin(new[key])]
    pd.concat([keep, new], ignore_index=True)[list(df.columns)].to_csv(path, index=False,
                                                                        encoding='utf-8-sig')


def x100(g):
    """100 x a Gini coefficient, rounded half up to one decimal: how WDI publishes PIP's estimates."""
    return float((Decimal(str(g).strip()) * 100).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))


if FETCH:
    new = []
    for f, url, desc, pub, acc in (
            (WB_FILE, WB_URL, 'Gini index (SI.POV.GINI), all countries 2001-2022 (World Bank estimate from PIP)',
             'World Bank WDI', 'application/json'),
            (WB_META, WB_META_URL, 'Indicator metadata of SI.POV.GINI: name, definition (sourceNote) and source '
                                   'organisation (Poverty and Inequality Platform)', 'World Bank WDI', 'application/json'),
            (PIP_FILE, PIP_URL, 'PIP survey estimates, all countries and years, version %s, CSV: Gini, welfare type, '
                                'reporting level, survey name and comparability spell of every survey; the check of '
                                'the WDI values and the source for Taiwan' % PV, 'World Bank PIP', 'text/csv'),
            (PIP_CIT, PIP_CIT_URL, 'PIP citation of version %s (how the World Bank asks the data set to be cited)' % PV,
             'World Bank PIP', 'application/json'),
            (OECD_FILE, OECD_URL, 'OECD IDD, New Zealand: Gini of equivalised disposable income, total population, '
                                  '2012 income definition, 2001-2022, SDMX-CSV', 'OECD', OECD_ACCEPT),
            (OECD_DF, OECD_DF_URL, 'SDMX dataflow DSD_WISE_IDD@DF_IDD with its structure and code lists: the '
                                   'OECD\'s name and description of the database and the meaning of the codes used',
             'OECD', 'application/xml')):
        dest = os.path.join(API, f)
        size = fetch(url, dest, acc)
        if f.endswith('.json'):
            json.load(open(dest, encoding='utf-8-sig'))
        new.append(dict(file=f, publisher=pub, description=desc, query_url=url, bytes=size,
                        path='evidence/api/' + f))
    upsert(os.path.join(D, 'api_snapshots.csv'), new, 'file')

# ------------------------------------------------------------------ metadata
meta = json.load(open(os.path.join(API, WB_META), encoding='utf-8-sig'))[1][0]
assert meta['id'] == 'SI.POV.GINI' and 'Poverty and Inequality Platform' in meta['sourceOrganization'], meta
cit = json.load(open(os.path.join(API, PIP_CIT), encoding='utf-8-sig'))
assert cit['version_id'][0] == PV, cit
dft = re.sub(r'\s+', ' ', open(os.path.join(API, OECD_DF), encoding='utf-8').read())
assert 'Income distribution database' in dft, 'OECD dataflow name'


def code_name(codelist, code):
    """English name (and description, if any) of one code in one code list of the archived structure."""
    m = re.search(r'<structure:Codelist id="%s".*?</structure:Codelist>' % codelist, dft)
    c = re.search(r'<structure:Code id="%s"[^>]*>(.*?)</structure:Code>' % re.escape(code), m.group(0))
    nm = re.search(r'<common:Name xml:lang="en">([^<]+)', c.group(1)).group(1)
    ds = re.search(r'<common:Description xml:lang="en">([^<]+)', c.group(1))
    return nm + (' - ' + ds.group(1) if ds else '')


oecd_codes = {k: code_name(cl, k) for cl, k in (('CL_MEASURE_IDD', 'INC_DISP_GINI'), ('CL_METHODOLOGY', 'METH2012'),
                                                 ('CL_DEFINITION', 'D_CUR'), ('CL_AGE', '_T'),
                                                 ('CL_UNIT_MEASURE', '0_TO_1'))}
assert oecd_codes['INC_DISP_GINI'].startswith('Gini (disposable income)'), oecd_codes
print('OECD code names:', oecd_codes)

# ------------------------------------------------------------------ World Bank WDI and PIP
wbj = json.load(open(os.path.join(API, WB_FILE), encoding='utf-8-sig'))
wb_updated = wbj[0].get('lastupdated', '')
wb = {(r['countryiso3code'], int(r['date'])): float(r['value']) for r in wbj[1] if r.get('value') is not None}
pip = pd.read_csv(os.path.join(API, PIP_FILE), dtype={'gini': str})
pip = pip[pip.reporting_level == 'national']
pipn = {}
for r in pip.itertuples():
    pipn.setdefault((r.country_code, int(r.reporting_year)), []).append(r)
oe = pd.read_csv(os.path.join(API, OECD_FILE), dtype=str)
assert set(oe.MEASURE) == {'INC_DISP_GINI'} and set(oe.AGE) == {'_T'} and set(oe.METHODOLOGY) == {'METH2012'}
assert set(oe.DEFINITION) == {'D_CUR'} and set(oe.UNIT_MEASURE) == {'0_TO_1'} and set(oe.REF_AREA) == {'NZL'}
oecd = {int(r.TIME_PERIOD): r.OBS_VALUE for r in oe.itertuples()}

used, rows, cmp_rows, unmatched, multi = {}, [], [], [], 0
for iso in ISO:
    for y in YEARS:
        w = wb.get((iso, y))
        cands = pipn.get((iso, y), [])
        row = None
        if w is not None:
            m = [c for c in cands if x100(c.gini) == w]
            if not m:
                unmatched.append((iso, y, w))
                continue
            if len(m) > 1:
                multi += 1
                inc = [c for c in m if c.welfare_type == 'income']
                assert inc, (iso, y, 'several PIP rows match and none is income')
                m = inc                                   # WDI publishes the income survey where both exist
            row, src, val = m[0], 'World Bank WDI', w
        elif iso == 'TWN' and cands:
            assert len(cands) == 1, (iso, y, len(cands))
            row, src, val = cands[0], 'World Bank PIP', x100(cands[0].gini)
        elif iso == 'NZL' and y in oecd:
            src, val = 'OECD IDD', float(Decimal(oecd[y]) * 100)
        else:
            src, val = '', None
        used[(iso, y)] = (src, val, row)
assert not unmatched, unmatched[:5]
assert not any(k[0] in ('TWN', 'NZL') and v[0] == 'World Bank WDI' for k, v in used.items()), 'WDI now covers TWN/NZL'
n_wdi = sum(1 for v in used.values() if v[0] == 'World Bank WDI')
print('WDI values: %d, every one equal to 100 x a national PIP survey Gini (one decimal); %d with an income and a '
      'consumption survey, the income one used' % (n_wdi, multi))

# a break: the comparability spell differs from the previous value used for the country
for iso in ISO:
    prev = None
    for y in YEARS:
        src, val, row = used[(iso, y)]
        if val is None:
            continue
        flags = []
        if row is not None:
            if row.welfare_type == 'consumption':
                flags.append(GT.F_CONS)
            if prev is not None and row.survey_comparability != prev:
                flags.append(GT.F_BREAK)
            prev = row.survey_comparability
        if src == 'OECD IDD':
            flags.append(GT.F_OECD)
        flag = '; '.join(flags)
        if src == 'World Bank WDI':
            note = ('World Bank PIP national estimate from the %s survey (%s), %s-based: 100 x the Gini coefficient of '
                    '%s per person, 0-100.%s' % (row.survey_acronym, 'survey year %s' % row.survey_year,
                                                  row.welfare_type, 'household ' + row.welfare_type,
                                                  ' PIP assembles China\'s national value from its urban and rural '
                                                  'surveys.' if iso == 'CHN' else ''))
            ver = ('Read directly from the archived World Bank WDI response (evidence/api/%s, data last updated %s); it '
                   'equals 100 x the Gini of the matching PIP survey row (evidence/api/%s: %s, %s, survey comparability '
                   'spell %s), rounded to one decimal. Retrieved %s.'
                   % (WB_FILE, wb_updated, PIP_FILE, row.survey_acronym, row.welfare_type, row.survey_comparability,
                      COLLECTED))
            rows.append(L.cell(iso, y, VAR, val, 'WB_SI_POV_GINI', WB_NAME, WB_BASE, 'evidence/api/' + WB_FILE,
                               'Year of the survey data (World Bank PIP reporting year)', 'A', 'survey', note=note,
                               flag=flag, verification=ver, collected_on=COLLECTED))
        elif src == 'World Bank PIP':
            note = ('World Bank PIP national estimate for Taiwan from the %s survey (the DGBAS Survey of Family Income '
                    'and Expenditure, harmonised by LIS), income-based. WDI does not publish Taiwan: the archive takes '
                    'PIP\'s Gini coefficient and publishes 100 x it rounded to one decimal, the rule every WDI value '
                    'follows (PIP value %s).' % (row.survey_acronym, row.gini))
            ver = ('Read directly from the archived PIP survey table (evidence/api/%s, version %s, national row of '
                   'Taiwan, China for %d); rescaled by the archive to 0-100 (100 x %s, rounded half up to one decimal). '
                   'Retrieved %s.' % (PIP_FILE, PV, y, row.gini, COLLECTED))
            rows.append(L.cell(iso, y, VAR, val, 'WB_PIP', PIP_NAME, PIP_BASE, 'evidence/api/' + PIP_FILE,
                               'Year of the survey data (World Bank PIP reporting year)', 'A', 'survey', note=note,
                               flag=flag, verification=ver, collected_on=COLLECTED))
        else:
            note = ('OECD IDD: Gini coefficient of equivalised household disposable income (after taxes and transfers), '
                    'total population, 2012 income definition. The World Bank has no data for New Zealand; this concept '
                    '(equivalised household income) differs from the World Bank\'s (income per person), so the value is '
                    'flagged. The archive publishes 100 x the OECD value (%s).' % oecd[y])
            ver = ('Read directly from the archived OECD SDMX response (evidence/api/%s); rescaled by the archive to '
                   '0-100 (100 x %s). Retrieved %s.' % (OECD_FILE, oecd[y], COLLECTED))
            rows.append(L.cell(iso, y, VAR, val, 'OECD_IDD', OECD_NAME, OECD_BASE, 'evidence/api/' + OECD_FILE,
                               'Year as labelled by the OECD IDD', 'A', 'survey', note=note, flag=flag,
                               verification=ver, collected_on=COLLECTED))

out = L.write_stage('gini_cells.csv', rows)
print('cells written: %d of %d country-years, %d countries (WDI %d, PIP Taiwan %d, OECD New Zealand %d)'
      % (len(out), len(ISO) * len(YEARS), out.iso3.nunique(), n_wdi, (out.source_id == 'WB_PIP').sum(),
         (out.source_id == 'OECD_IDD').sum()))
assert out.iso3.nunique() == len(ISO), sorted(set(ISO) - set(out.iso3))

cell_by = {(r['iso3'], r['year']): r for r in rows}
for iso in ISO:
    for y in YEARS:
        src, val, row = used[(iso, y)]
        w = wb.get((iso, y))
        cmp_rows.append(dict(
            iso3=iso, year=y, wdi_value='' if w is None else repr(w),
            pip_gini='' if row is None else row.gini, pip_x100_one_decimal='' if row is None else repr(x100(row.gini)),
            pip_welfare_type='' if row is None else row.welfare_type,
            pip_survey='' if row is None else row.survey_acronym,
            pip_survey_year='' if row is None else repr(float(row.survey_year)),
            pip_survey_comparability='' if row is None else str(row.survey_comparability),
            wdi_equals_pip='' if w is None else ('yes' if row is not None and x100(row.gini) == w else 'no'),
            oecd_value=oecd.get(y, '') if iso == 'NZL' else '',
            used_source=src, used_value='' if val is None else repr(val),
            flag=cell_by[(iso, y)]['flag'] if (iso, y) in cell_by else ''))
pd.DataFrame(cmp_rows).to_csv(GT.CMP, index=False, encoding='utf-8-sig')

# ------------------------------------------------------------------ mirrors, extracts, publisher pages
if FETCH:
    import fitz                                          # noqa: E402
    mirrors = []
    g_wb = {iso: {y: wb[(iso, y)] for y in YEARS if (iso, y) in wb} for iso in ISO if any((iso, y) in wb for y in YEARS)}
    base = os.path.join(API, 'MIRROR__' + os.path.splitext(WB_FILE)[0])
    made = L.grid_mirror('World Bank WDI SI.POV.GINI - Gini index (0-100)',
                         'Query: %s. Retrieved %s (data last updated %s). %d panel countries; a dash is a year without '
                         'a survey.' % (WB_URL, COLLECTED, wb_updated, len(g_wb)), g_wb, YEARS, base,
                         fmt=lambda v: '%.1f' % v)
    mirrors.append(dict(scope='API', folder='evidence/api', source_file=WB_FILE,
                        mirrors=';'.join(os.path.basename(m) for m in made), n_mirrors=len(made)))
    g_pip = {}
    for iso in ISO:
        for y in YEARS:
            src, val, row = used[(iso, y)]
            if row is not None:
                g_pip.setdefault(iso, {})[y] = '%.1f%s' % (x100(row.gini), ' c' if row.welfare_type == 'consumption' else '')
    base = os.path.join(API, 'MIRROR__' + os.path.splitext(PIP_FILE)[0])
    made = L.grid_mirror('World Bank PIP (version %s) - national survey Gini x 100, panel countries' % PV,
                         'Query: %s. Retrieved %s. The survey row WDI publishes (or, for Taiwan, the only one), 100 x '
                         'Gini rounded to one decimal.' % (PIP_URL, COLLECTED), g_pip, YEARS, base, fmt=lambda v: v,
                         note='"c" marks a consumption survey. The CSV beside this file holds every survey of every '
                              'country, with its welfare type, survey name and comparability spell. Rendered %s.'
                              % COLLECTED)
    mirrors.append(dict(scope='API', folder='evidence/api', source_file=PIP_FILE,
                        mirrors=';'.join(os.path.basename(m) for m in made), n_mirrors=len(made)))
    for rel, title, header, trows, src in (
            (WB_META, 'World Bank indicator metadata - SI.POV.GINI', ['Field', 'Value'],
             [(['id', meta['id']], False), (['name', meta['name']], True), (['sourceNote', meta['sourceNote']], True),
              (['sourceOrganization', meta['sourceOrganization']], True), (['source', meta['source']['value']], False)],
             WB_META_URL),
            (PIP_CIT, 'World Bank PIP - citation of version %s' % PV, ['Field', 'Value'],
             [(['citation', cit['citation'][0]], True), (['version_id', cit['version_id'][0]], True),
              (['date_accessed', cit['date_accessed'][0]], False)], PIP_CIT_URL),
            (OECD_FILE, 'OECD IDD - New Zealand, Gini of equivalised disposable income (0-1)',
             ['Year', 'OBS_VALUE', 'x 100 (used)', 'MEASURE', 'AGE', 'METHODOLOGY', 'DEFINITION'],
             [([r.TIME_PERIOD, r.OBS_VALUE, '%.1f' % float(Decimal(r.OBS_VALUE) * 100), r.MEASURE, r.AGE, r.METHODOLOGY,
                r.DEFINITION], True) for r in oe.sort_values('TIME_PERIOD').itertuples()], OECD_URL),
            (OECD_DF, 'OECD SDMX dataflow DSD_WISE_IDD@DF_IDD - name, description and the codes used', ['Field', 'Value'],
             [(['Name (en)', re.search(r'<structure:Dataflow [^>]*>.*?<common:Name xml:lang="en">([^<]+)', dft).group(1)], True),
              (['Description (en)', re.search(r'<structure:Dataflow [^>]*>.*?<common:Description xml:lang="en">([^<]+)',
                                              dft).group(1)], True)]
             + [(['code %s' % k_, v_], True) for k_, v_ in oecd_codes.items()], OECD_DF_URL)):
        mb = os.path.join(API, 'MIRROR__' + os.path.splitext(rel)[0])
        L.table_extract(title, header, trows, mb, 'Archived file %s from %s, retrieved %s.' % (rel, src, COLLECTED),
                        note='The fields of the archived file, unchanged. Rendered %s.' % COLLECTED)
        mirrors.append(dict(scope='API', folder='evidence/api', source_file=rel,
                            mirrors='%s;%s' % (os.path.basename(mb + '.pdf'), os.path.basename(mb + '.png')),
                            n_mirrors=2))
    sm = os.path.join(D, 'source_mirrors.csv')
    old = pd.read_csv(sm)
    old = old[~(old.source_file.isin([m['source_file'] for m in mirrors]))]
    pd.concat([old, pd.DataFrame(mirrors)], ignore_index=True).to_csv(sm, index=False, encoding='utf-8-sig')

    pubrows = []
    for p in PUBLISHER_PAGES:
        b = os.path.join(PUB, p['key'])
        made = L.chrome_render(p['page_url'], pdf=b + '.pdf', png=b + '.png', wait_ms=40000)
        note = ''
        if b + '.pdf' in made and b + '.png' in made:
            d_ = fitz.open(b + '.pdf')
            chars = sum(len(x.get_text().strip()) for x in d_)
            d_.close()
            if chars < 500:
                img = fitz.open(b + '.png')
                pdfb = img.convert_to_pdf()
                img.close()
                open(b + '.pdf', 'wb').write(pdfb)
                note = ('The page prints almost nothing in a headless browser, so the PDF holds the screenshot taken on '
                        '%s.' % COLLECTED)
        pubrows.append(dict(p, status='captured' if len(made) == 2 else 'partial',
                            pdf='evidence/api/publisher_pages/%s.pdf' % p['key'] if b + '.pdf' in made else '',
                            png='evidence/api/publisher_pages/%s.png' % p['key'] if b + '.png' in made else '',
                            pdf_bytes=os.path.getsize(b + '.pdf') if b + '.pdf' in made else 0,
                            png_bytes=os.path.getsize(b + '.png') if b + '.png' in made else 0,
                            captured=COLLECTED, note=note))
        print('publisher page %-30s %s %s' % (p['key'], [os.path.basename(m) for m in made], note[:40]))
    upsert(os.path.join(D, 'api_publisher_snapshots.csv'), pubrows, 'key')
