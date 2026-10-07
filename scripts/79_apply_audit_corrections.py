# -*- coding: utf-8 -*-
"""Corrections that follow from the audit of 2026-10-07 (GitHub issues #1-#25).

Every finding was checked against the archived source before anything was changed; the
verdicts are in verification/AUDIT_RESPONSE_2026-10-07.md. This script applies the ones that
change a value, a source citation, a grade or a classification in the panel:

  F01  Chile irregular stock 2018-2022: the chart values were assigned to the wrong years and
       the two INE methodologies were mixed. Now the 2023 methodology for every year; the
       2022-methodology series is kept as the alternative.
  F02  India foreign-born 2011: 5,490,000 was Table 2a of a journal article, which is based on
       Census Table D-2 (place of LAST residence). The official D-01 birthplace total is
       5,363,099.
  F03  Suriname foreign nationals 2012: 36,393 was a residual that contains 3,340 persons of
       unknown nationality. The known foreign nationalities sum to 33,053.
  F06  Taiwan overstayers: per-year citations pointed at a Ministry of Labor table of absconded
       workers; re-pointed to the Legislative Yuan reports that contain the numbers. 2021
       (81,538) has no source anywhere and is deleted.
  F07  Taiwan overstayers are totals for ALL external-population categories, not foreign
       nationals alone; the notes now say so and give the foreign-national component.
  F08  Taiwan population 2010-2016: exact MOI totals instead of the rounded NDC figures.
  F16  Observations the secondary workbook holds that the panel omitted and that the archived
       sources do support: Australia 2015, Japan 2010/2012/2013/2015, Iceland 2021 detections.
  F20  Grades: values read from a printed document are B, not A (Taiwan population, Taiwan
       overstayers, UK foreign-born 2020).

It also rewrites irregular_estimates_all.csv with a status for every record (F14), rebuilds
the country source tables' used_in_panel indicators (F15), routes the register's data_raw/
placeholders to exact files (F21) and corrects the stale folder descriptions in the country
READMEs. Idempotent: values are set, not shifted, and old values come from git commit
0d64a1c, so a second run changes nothing.

The audit trail is written to data/audit_changes_2026-10-07.csv, which 74_assemble_panel.py
reads so that its "no published value changed" assertion exempts exactly these cells.
"""
import glob
import html
import os
import re
import sys

import fitz
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ext_lib as L                                               # noqa: E402

SITE = os.path.dirname(HERE)
D = os.path.join(SITE, 'data')
EV = os.path.join(SITE, 'evidence', 'countries')
API = os.path.join(SITE, 'evidence', 'api')
WHEN = '2026-10-07'
BASE = L.baseline_panel()
panel = pd.read_csv(os.path.join(D, 'panel_final.csv'))
TEXT_SUFFIXES = ('_source', '_url', '_ref_date', '_note', '_verification', '_derived', '_derivation',
                 '_grade', '_flag', '_published_range', '_source_type', '_collected_on')
for c_ in panel.columns:                 # an all-blank column is read as float and cannot hold text
    if c_.endswith(TEXT_SUFFIXES):
        panel[c_] = panel[c_].astype(object)
log = []                    # the audit trail
REGISTER = pd.read_csv(os.path.join(D, 'source_register.csv')).fillna('')


def url_of(local_file, default):
    m = REGISTER[REGISTER.local_file == local_file]
    return str(m.source_url.iloc[0]) if len(m) else default


def ix(iso, yr):
    m = panel.index[(panel.iso3 == iso) & (panel.year == yr)]
    assert len(m) == 1, (iso, yr)
    return m[0]


def base_val(iso, yr, var, suffix=''):
    m = BASE[(BASE.iso3 == iso) & (BASE.year == yr)]
    if not len(m) or var + suffix not in BASE.columns:
        return np.nan
    return m.iloc[0][var + suffix]


def put(iso, yr, var, finding, kind, reason, evidence, value=None, **meta):
    """Set a cell and its metadata; record old and new in the audit trail."""
    i = ix(iso, yr)
    old_v, old_g = base_val(iso, yr, var), base_val(iso, yr, var, '_grade')
    if value is not None:
        panel.at[i, var] = value
    for suf, val in meta.items():
        col = var + '_' + suf
        if col in panel.columns:
            panel.at[i, col] = val
    log.append(dict(finding=finding, kind=kind, iso3=iso, year=yr, variable=var, old_value=old_v,
                    new_value=panel.at[i, var], old_grade=old_g,
                    new_grade=panel.at[i, var + '_grade'] if var + '_grade' in panel.columns else '',
                    reason=reason, evidence=evidence, alternative_label='', alternative_value=np.nan))
    return i


def archive(url, dest, minbytes=1000):
    """Download once; a file already archived is left as it is."""
    if os.path.exists(dest) and os.path.getsize(dest) >= minbytes:
        return
    code, size = L.download(url, dest)
    assert code == '200' and size >= minbytes, 'could not archive %s (%s, %s bytes)' % (url, code, size)


# ================================================================== F01  Chile
CHL_PDF = 'irregular_stock__f8f04e39ba__www.ine.gob.cl.pdf'
CHL_URL = ('https://www.ine.gob.cl/docs/default-source/demografia-y-migracion/publicaciones-y-anuarios/'
           'migraci%C3%B3n-internacional/estimaci%C3%B3n-poblaci%C3%B3n-extranjera-en-chile-2018/'
           'sintesis-epe2023.pdf?sfvrsn=cc51129c_10')
# Page 12 of the INE/SERMIG Sintesis 2023, chart "Comparacion resultados Estimacion, con
# metodologia 2022 y 2023, componente irregular". Year axis 2018-2023; blue = methodology 2022,
# orange = methodology 2023. Read from the rendered page and confirmed by label position
# (scripts/80_check_source_charts.py repeats that check from the PDF's own coordinates).
M2023 = {2018: 10375, 2019: 21833, 2020: 53356, 2021: 109846, 2022: 291149, 2023: 336984}
M2022 = {2018: 5975, 2019: 14818, 2020: 27162, 2021: 59682, 2022: 115059, 2023: 130017}
CHL_SRC = ('Instituto Nacional de Estadisticas (INE) and Servicio Nacional de Migraciones (SERMIG), '
           'Estimacion de Personas Extranjeras Residentes Habituales en Chile 2023 - Sintesis, page 12 '
           '(2023 revised methodology series)')
x_pdf, x_png = (os.path.join(EV, 'CHL', 'SNAPSHOT__irregular_stock__INE_Sintesis2023_p12_chart.pdf'),
                os.path.join(EV, 'CHL', 'SNAPSHOT__irregular_stock__INE_Sintesis2023_p12_chart.png'))
if not os.path.exists(x_png):
    L.page_extract(os.path.join(EV, 'CHL', CHL_PDF), 12, x_pdf[:-4])
L.add_snapshot_row('CHL', 'irregular_stock', CHL_URL, x_pdf, x_png, CHL_PDF,
                   'Page 12 of the INE/SERMIG Sintesis 2023: the chart that gives the irregular '
                   'component by year for the 2022 and 2023 methodologies.')
for y in range(2018, 2023):
    put('CHL', y, 'irregular_stock', 'F01', 'corrected',
        'The first release assigned the chart values to the wrong years and mixed the two '
        'methodologies (2018-2020 labelled 2023 methodology, 2021-2022 labelled 2022 methodology, '
        'none placed under the year the chart gives).',
        'INE/SERMIG Sintesis 2023, page 12 (evidence/countries/CHL/%s)' % CHL_PDF,
        value=M2023[y], source=CHL_SRC, url=CHL_URL, ref_date='31 December', grade='B',
        note='Reference date 31 December %d. Modelled estimate of residents in an irregular '
             'situation under the REVISED 2023 methodology, which adds Mineduc school-enrolment and '
             'SERMIG biometric-registration records. Read from the chart on page 12 (year axis and '
             'series legend checked); the same year on the 2022 methodology is %s. Corrected on %s: '
             'the first release held other years\' values here.' % (y, format(M2022[y], ','), WHEN),
        verification='Value, year and methodology series read from the chart on page 12 of the '
                     'archived document and checked against the label positions (audit of %s).' % WHEN)

# ================================================================== F02  India 2011
IN_XLSX = 'foreign_born__ORGI_Census2011_D01_India__DS-0000-D01-MDDS.xlsx'
IN_HTML = 'foreign_born__ORGI_Census2011_D01_India__catalog-10671.html'
IN_PAGE = 'https://censusindia.gov.in/nada/index.php/catalog/10671'
IN_XLSX_URL = 'https://censusindia.gov.in/nada/index.php/catalog/10671/download/13783/DS-0000-D01-MDDS.XLSX'
archive(IN_XLSX_URL, os.path.join(EV, 'IND', IN_XLSX), 200000)
archive(IN_PAGE + '/study-description', os.path.join(EV, 'IND', IN_HTML), 20000)
d = pd.read_excel(os.path.join(EV, 'IND', IN_XLSX), header=None, skiprows=5)
d = d[d[3].astype(str).str.upper() == 'INDIA'].reset_index(drop=True)


def inrow(label):
    return d[d[4].astype(str).str.strip() == label].iloc[0]


total, within = int(inrow('Total Population')[5]), int(inrow('Born within India')[5])
outside = int(inrow('Born Outside India')[5])
males, females = int(inrow('Born Outside India')[6]), int(inrow('Born Outside India')[7])
cont = {k: int(inrow(k)[5]) for k in ('Countries in Asia beyond India', 'Countries in Europe',
                                       'Countries in Africa', 'Countries in the Americas',
                                       'Countries in Oceania')}
uncl = int(inrow('Unclassifiable')[5])
assert outside == 5363099, outside
assert sum(cont.values()) == outside and outside + uncl == total - within, 'D-01 rows do not add up'
if not os.path.exists(os.path.join(EV, 'IND', 'SNAPSHOT__foreign_born__ORGI_Census2011_D01_India_extract.png')):
    L.table_extract(
        'Census of India 2011, Table D-01: population classified by place of birth and sex - India, persons',
        ['Row of the table', 'Persons'],
        [(('Total population', format(total, ',')), False), (('Born within India', format(within, ',')), False),
         (('Born Outside India (the value used)', format(outside, ',')), True)]
        + [((k, format(v, ',')), False) for k, v in cont.items()]
        + [(('Unclassifiable (not counted)', format(uncl, ',')), False)],
        os.path.join(EV, 'IND', 'SNAPSHOT__foreign_born__ORGI_Census2011_D01_India_extract'),
        'Source: Office of the Registrar General & Census Commissioner, India; file DS-0000-D01-MDDS.XLSX '
        '(%s). Retrieved %s.' % (IN_PAGE, WHEN))
L.add_snapshot_row('IND', 'foreign_born', IN_PAGE,
                   os.path.join(EV, 'IND', 'SNAPSHOT__foreign_born__ORGI_Census2011_D01_India_extract.pdf'),
                   os.path.join(EV, 'IND', 'SNAPSHOT__foreign_born__ORGI_Census2011_D01_India_extract.png'),
                   IN_HTML, 'National rows of Census 2011 Table D-01 used for the 2011 value, rendered '
                            'from the archived workbook; the workbook and catalogue page are archived beside it.')
put('IND', 2011, 'foreign_born', 'F02', 'corrected',
    'The first release used 5,490,000 (2,513 + 2,977 thousand), which is Table 2a of a journal article '
    'built on Census Table D-2 (place of LAST residence); the official birthplace table D-01 gives '
    'a different number.',
    'Census of India 2011 Table D-01, row "Born Outside India" (evidence/countries/IND/%s)' % IN_XLSX,
    value=outside,
    source='Office of the Registrar General & Census Commissioner, India, Census of India 2011, Table '
           'D-01 Population classified by place of birth and sex, India (row "Born Outside India")',
    url=IN_PAGE, ref_date='Census reference date (1 March 2011)', grade='A',
    note='Census count; persons enumerated in India who were born in another country: the official '
         'national row "Born Outside India" of Table D-01 (males %s, females %s). The five foreign-continent '
         'rows add up to it; %s persons of unclassifiable place of birth are not counted, as for 2001. '
         'Replaces 5,490,000, a figure from Table 2a of Singh and Biradar (Demography India 51(1), 2022), '
         'which is built on Table D-2 (place of last residence) and is not a birthplace count. '
         'Corrected on %s.' % (format(males, ','), format(females, ','), format(uncl, ','), WHEN),
    verification='Read directly from the official D-01 workbook (archived; byte-identical to a fresh '
                 'download of %s).' % WHEN)

# ================================================================== F03  Suriname 2012
SUR_PDF = 'foreign_nationals__f68b5eee2a__statistics-suriname.org.pdf'
pg = fitz.open(os.path.join(EV, 'SUR', SUR_PDF))[23].get_text()
assert 'Tabel H2' in pg and 'Onbekend' in pg, 'page 24 is not Table H2'
h2 = {}
for lab in ('Surinaamse', 'Nederlandse', 'Guyanese', 'Franse', 'Braziliaanse', 'Chinese', 'Overige',
            'Onbekend', 'Totaal'):
    m = re.search(lab + r'\s*\n\s*[\d,]+\s*\n\s*[\d,]+\s*\n\s*([\d,]+)', pg)
    assert m, lab
    h2[lab] = int(m.group(1).replace(',', ''))
known = sum(h2[k] for k in ('Nederlandse', 'Guyanese', 'Franse', 'Braziliaanse', 'Chinese', 'Overige'))
assert h2['Totaal'] - h2['Surinaamse'] == known + h2['Onbekend'] == 36393 and known == 33053, h2
if not os.path.exists(os.path.join(EV, 'SUR', 'SNAPSHOT__foreign_nationals__Suriname_Census2012_p24_tableH2.png')):
    L.page_extract(os.path.join(EV, 'SUR', SUR_PDF), 24,
                   os.path.join(EV, 'SUR', 'SNAPSHOT__foreign_nationals__Suriname_Census2012_p24_tableH2'))
SUR_URL = panel.at[ix('SUR', 2012), 'foreign_nationals_url']
L.add_snapshot_row('SUR', 'foreign_nationals', SUR_URL,
                   os.path.join(EV, 'SUR', 'SNAPSHOT__foreign_nationals__Suriname_Census2012_p24_tableH2.pdf'),
                   os.path.join(EV, 'SUR', 'SNAPSHOT__foreign_nationals__Suriname_Census2012_p24_tableH2.png'),
                   SUR_PDF, 'Page 24 of Census 8 (2012) Volume 1: Table H2, population by nationality.')
i = put('SUR', 2012, 'foreign_nationals', 'F03', 'corrected',
        'The first release took total population minus Surinamese nationals (36,393), a residual that '
        'includes 3,340 persons whose nationality is unknown; unknown nationality is not foreign '
        'nationality.',
        'Census 8 (2012) Volume 1, Table H2 (evidence/countries/SUR/%s, PDF page 24)' % SUR_PDF,
        value=known, grade='B',
        note='Census count, reference date 13 Aug 2012. Sum of the six foreign nationality categories '
             'printed in Table H2: Dutch 10,248 + Guyanese 8,278 + French 3,575 + Brazilian 5,027 + '
             'Chinese 3,758 + other 2,167 = 33,053. The 3,340 persons of unknown nationality (Onbekend) '
             'are NOT included; adding them gives 36,393, the value held before %s. Multiple '
             'nationality was not investigated by the census.' % WHEN,
        verification='Sum of the printed Table H2 categories (page 24 of the archived census volume); '
                     'the table total 541,638 minus Surinamese 505,245 equals the sum plus unknown.',
        derived='yes',
        derivation='Sum of the six printed foreign nationality categories of Table H2; the 3,340 '
                   'unknown-nationality persons are excluded')
log[-1].update(alternative_label='Residual incl. 3,340 persons of unknown nationality (value held before '
                                 + WHEN + ')', alternative_value=36393)

# ================================================================== F08 / F20  Taiwan population
MOI_EXACT = {2010: 23162123, 2011: 23224912, 2012: 23315822, 2013: 23373517, 2014: 23433753,
             2015: 23492074, 2016: 23539816}
moi_pdf = os.path.join(EV, 'TWN', 'population__19060caafa__ws.moi.gov.tw.pdf')
page151 = fitz.open(moi_pdf)[150].get_text().replace(',', '')
for y, v in MOI_EXACT.items():
    assert str(v) in page151, 'MOI yearbook page 151 does not print %d for %d' % (v, y)
x_base = os.path.join(EV, 'TWN', 'SNAPSHOT__population__MOI_Yearbook2019_p151_table1')
if not os.path.exists(x_base + '.png'):
    L.page_extract(moi_pdf, 151, x_base)
MOI_URL = panel.at[ix('TWN', 2010), 'population_url']
L.add_snapshot_row('TWN', 'population', MOI_URL, x_base + '.pdf', x_base + '.png',
                   'population__19060caafa__ws.moi.gov.tw.pdf',
                   'Page 151 of the MOI Statistical Yearbook 2019 edition: Table 1, year-end population '
                   '2010-2016 as exact person counts.')
for y, v in MOI_EXACT.items():
    put('TWN', y, 'population', 'F08', 'corrected',
        'The first release held the National Development Council figures rounded to thousands; the '
        'cited MOI yearbook prints exact totals.',
        'MOI Statistical Yearbook 2019 edition, Table 1, PDF page 151',
        value=v, grade='B',
        verification='Exact year-end total read from Table 1 (page 151) of the archived yearbook; the '
                     'NDC data book prints the same total rounded to thousands.')
for y in range(2017, 2023):
    put('TWN', y, 'population', 'F20', 'regraded',
        'Exact total read from a printed bulletin table, not decoded from a machine-readable source.',
        'MOI Monthly Bulletin of Interior Statistics (archived PDF)',
        grade='B',
        verification='Exact year-end total read from the archived MOI monthly bulletin table.')

# ================================================================== F06 / F07  Taiwan overstayers
LY1_URL = 'https://www.ly.gov.tw/Pages/Detail.aspx?nodeid=33342&pid=184411'
LY2_URL = 'https://www.ly.gov.tw/Pages/Detail.aspx?nodeid=45128&pid=211927'
LY3_URL = 'https://www.ly.gov.tw/Pages/Detail.aspx?nodeid=33580&pid=188916'
txt1 = html.unescape(re.sub(r'<[^>]+>', '\n', open(os.path.join(EV, 'TWN', 'irregular__539a03cf36__www.ly.gov.tw.html'),
                                                    encoding='utf-8', errors='replace').read()))
txt1 = re.sub(r'\s*\n\s*', '\n', txt1)
COMP = {}
for y, lab in ((2012, '101年底'), (2013, '102年底'), (2014, '103年底'), (2015, '104年底'), (2016, '105年底'),
               (2017, '106年底'), (2018, '107年底')):
    m = re.search(re.escape(lab) + r'\n([\d,]+)\n([\d,]+)\n([\d,]+)\n([\d,]+)\n([\d,]+)\n([\d,]+)\n([\d,]+)', txt1)
    assert m, lab
    t, mal, fem, fn, cn, hk, nr = [int(x.replace(',', '')) for x in m.groups()]
    assert mal + fem == t == fn + cn + hk + nr, (y, m.groups())
    COMP[y] = dict(total=t, fn=fn, cn=cn, hk=hk, nr=nr)
assert [COMP[y]['total'] for y in range(2012, 2019)] == [66696, 69929, 68998, 77422, 79392, 79909, 89965]
txt2 = html.unescape(re.sub(r'<[^>]+>', '\n', open(os.path.join(EV, 'TWN', 'irregular__40806cb930__www.ly.gov.tw.html'),
                                                    encoding='utf-8', errors='replace').read()))
txt2 = re.sub(r'\s*\n\s*', '\n', txt2)
m = re.search(r'逾期居留人數\(A\)\n([\d,]+)\n([\d,]+)\n([\d,]+)\n([\d,]+)\n逾期停留人數\(B\)\n([\d,]+)\n([\d,]+)\n'
              r'([\d,]+)\n([\d,]+)\n逾期外來人口數\(C=A\+B\)\n([\d,]+)\n([\d,]+)\n([\d,]+)\n([\d,]+)', txt2)
assert m, 'Table 1 of the 2021 report not found'
g = [int(x.replace(',', '')) for x in m.groups()]
A_, B_, C_ = g[0:4], g[4:8], g[8:12]
assert [a + b for a, b in zip(A_, B_)] == C_ and C_[2:] == [83465, 86061] and C_[0] == COMP[2017]['total']
LY_DOC = {2012: 'irregular__539a03cf36__www.ly.gov.tw.html', 2013: 'irregular__539a03cf36__www.ly.gov.tw.html',
          2019: 'irregular__40806cb930__www.ly.gov.tw.html', 2020: 'irregular__40806cb930__www.ly.gov.tw.html'}
NIA_SRC1 = ('National Immigration Agency (內政部移民署), as tabulated in the Legislative Yuan Budget Center report '
            'of July 2019 (附表11: 101年底至108年3月底我國外來人口逾期停(居)留情形表, 總計)')
NIA_SRC2 = ('National Immigration Agency (內政部移民署), as tabulated in the Legislative Yuan Budget Center report '
            'of September 2021 (表1 106至109年外來人口逾期停(居)留情形表, 逾期外來人口數 C=A+B)')
UNIVERSE = ('Administrative register count of ALL overstaying persons the National Immigration Agency '
            'records (逾期居留 + 逾期停留): foreign nationals %s, mainland Chinese %s, Hong Kong/Macao '
            'residents %s and nationals without household registration %s. It is not a count of '
            'foreign nationals alone.')
for y in range(2012, 2019):
    c = COMP[y]
    old = base_val('TWN', y, 'irregular_proxy_overstayers', '_note')   # the first-release note
    split = re.search(r'(\d+) overstaying residence \(逾期居留\) plus (\d+) overstaying visit \(逾期停留\)', str(old))
    extra = (' Of the total, %s are overstaying residence (逾期居留) and %s overstaying visit (逾期停留).'
             % (format(int(split.group(1)), ','), format(int(split.group(2)), ','))) if split else ''
    kw = dict(
        value=c['total'], grade='B', ref_date='31 December',
        note='Reference date 31 December %d (%s in the source). %s%s Source: Legislative Yuan Budget '
             'Center report reproducing National Immigration Agency figures.'
             % (y, '%d年底' % (y - 1911),
                UNIVERSE % tuple(format(c[k], ',') for k in ('fn', 'cn', 'hk', 'nr')), extra))
    if y in (2012, 2013):
        kw.update(source=NIA_SRC1, url=LY1_URL,
                  verification='Confirmed in the archived Legislative Yuan report (附表11, row %d年底).' % (y - 1911))
        kind = 'source corrected'
        why = ('The cell cited a Ministry of Labor table of absconded workers (Table 12-7), which does '
               'not contain this number; the number is in the archived Legislative Yuan report.')
    else:
        kw.update(verification='Confirmed in the archived Legislative Yuan report (附表11, row %d年底); '
                               'also reproduced in the later report that tabulates 106-109.' % (y - 1911))
        kind = 'relabelled'
        why = 'The note called the total "overstaying foreign nationals"; it covers all categories.'
    put('TWN', y, 'irregular_proxy_overstayers', 'F06' if y in (2012, 2013) else 'F07', kind, why,
        'Legislative Yuan Budget Center report, July 2019, 附表11 (evidence/countries/TWN/irregular__539a03cf36__'
        'www.ly.gov.tw.html)', **kw)
    if y not in (2012, 2013):
        log[-1]['finding'] = 'F07'
for y, a, b, c in ((2019, A_[2], B_[2], C_[2]), (2020, A_[3], B_[3], C_[3])):
    col = '108年度' if y == 2019 else '109年'
    put('TWN', y, 'irregular_proxy_overstayers', 'F06', 'source corrected',
        'The cell cited a Ministry of Labor table of absconded workers (Table 12-7) or a report that gives '
        'only July 2019; the number is in the Legislative Yuan report of September 2021.',
        'Legislative Yuan Budget Center report, September 2021, Table 1 (evidence/countries/TWN/%s)' % LY_DOC[y],
        value=c, grade='B', source=NIA_SRC2, url=LY2_URL,
        ref_date='Year %d (column "%s"; the month is not stated in the source)' % (y, col),
        note='Column "%s" of Table 1: overstaying residence (逾期居留) %s + overstaying visit (逾期停留) %s = '
             '%s. All categories of overstaying persons the National Immigration Agency records '
             '(foreign nationals, mainland Chinese, Hong Kong/Macao residents, nationals without household '
             'registration), the same universe as 2012-2018. The report does not state the date within '
             'the year%s.'
             % (col, format(a, ','), format(b, ','), format(c, ','),
                '; its Table 2 gives 85,804 for the end of July 2020' if y == 2020 else ''),
        verification='Confirmed in the archived Legislative Yuan report (Table 1, column %s).' % col)
# 2021: no source anywhere
i21 = ix('TWN', 2021)
deleted_val = float(panel.at[i21, 'irregular_proxy_overstayers'])
assert deleted_val == 81538.0 or np.isnan(deleted_val)
if not np.isnan(deleted_val):
    old_g = panel.at[i21, 'irregular_proxy_overstayers_grade']
    for suf in ('', '_grade', '_source', '_url', '_ref_date', '_note', '_verification', '_derived',
                '_derivation', '_published_range', '_pct_pop'):
        c_ = 'irregular_proxy_overstayers' + suf
        if c_ in panel.columns:
            panel.at[i21, c_] = np.nan
    log.append(dict(finding='F06', kind='deleted', iso3='TWN', year=2021, variable='irregular_proxy_overstayers',
                    old_value=81538.0, new_value=np.nan, old_grade=old_g, new_grade='',
                    reason='No source located: the cited Ministry of Labor table is the absconded-worker series '
                           '(55,805 at end-2021); the Legislative Yuan reports archived here end at 2020; the '
                           'audit of 2026-10-07 and a further search of National Immigration Agency documents '
                           'found no end-2021 total of 81,538.',
                    evidence='MOL Table 12-7; LY reports of July 2019 and September 2021',
                    alternative_label='', alternative_value=np.nan))
else:                                                                  # re-run: keep the record
    log.append(dict(finding='F06', kind='deleted', iso3='TWN', year=2021, variable='irregular_proxy_overstayers',
                    old_value=81538.0, new_value=np.nan, old_grade='A', new_grade='',
                    reason='No source located (see deleted_values.csv).', evidence='',
                    alternative_label='', alternative_value=np.nan))
# the absconded-worker value of 31 July 2019 is not a year-end figure
# The 2019 absconded-worker value was the 31 July figure of a Legislative Yuan report while every other
# year is the Ministry of Labor year-end stock; Table 12-7 gives the year-end 2019 stock (48,491).
mol = fitz.open(os.path.join(EV, 'TWN', 'irregular_proxy_overstayers__0756fa9f58__statdb.mol.gov.tw.pdf'))
moltxt = ' '.join(p_.get_text() for p_ in mol)
assert '48,491' in moltxt and '47,632' not in moltxt
put('TWN', 2019, 'irregular_proxy_absconded_workers', 'F06', 'corrected',
    'The cell held the 31 July 2019 figure (47,632) of a Legislative Yuan report while the column is the '
    'Ministry of Labor year-end stock; Table 12-7 gives 48,491 for the end of 2019.',
    'MOL Monthly Bulletin Table 12-7 (evidence/countries/TWN/irregular_proxy_overstayers__0756fa9f58__'
    'statdb.mol.gov.tw.pdf), column "End of 2019"',
    value=48491.0,
    source=panel.at[ix('TWN', 2020), 'irregular_proxy_absconded_workers_source'],
    url='https://statdb.mol.gov.tw/html/mon/212070.pdf', ref_date='31 December', grade='B',
    note='absconded / missing migrant workers (失聯移工), stock at END OF YEAR 2019. Counts migrant workers '
         'whose employment permit has lapsed and who have not been located. This is the Ministry of Labor '
         'absconded-worker measure, a DIFFERENT series from the National Immigration Agency 逾期停留/逾期居留 '
         '(overstaying visit / overstaying residence) counts; the two are not additive and not directly '
         'comparable. The 31 July 2019 figure of the Legislative Yuan report (47,632) was held here before %s.'
         % WHEN,
    verification='Confirmed in the archived Ministry of Labor Table 12-7 (column End of 2019).')
log[-1].update(alternative_label='Legislative Yuan Budget Center report, October 2019: stock at 31 July 2019 '
                                 '(value held before ' + WHEN + ')', alternative_value=47632)

# ================================================================== F20  UK 2020
put('GBR', 2020, 'foreign_born', 'F20', 'regraded',
    'Read from a printed ONS table published rounded to 0.1 million (exact only to +/-50,000), not '
    'decoded from a machine-readable source.', 'ONS, Population of the UK by country of birth and nationality',
    grade='B',
    verification='Read from the archived ONS release; published rounded to the nearest 0.1 million.')

# ================================================================== F16  omitted but supported values
JPN_PDF = 'irregular__ccfa80d7df__www.moj.go.jp.pdf'
jp = fitz.open(os.path.join(EV, 'JPN', JPN_PDF))[45].get_text().replace(',', '')
JPN = {2010: 91778, 2012: 67065, 2013: 62009, 2015: 60007}
for y, v in JPN.items():
    assert str(v) in jp, 'ISA Table 21 does not print %d' % v
assert 'Table 21' in jp and '59061' in jp and '78488' in jp
jb = os.path.join(EV, 'JPN', 'SNAPSHOT__irregular_proxy_overstayers__ISA_ImmigrationControl2015_p46_table21')
if not os.path.exists(jb + '.png'):
    L.page_extract(os.path.join(EV, 'JPN', JPN_PDF), 46, jb)
JPN_URL = url_of(JPN_PDF, 'https://www.moj.go.jp/isa/content/001459199.pdf')
L.add_snapshot_row('JPN', 'irregular_proxy_overstayers', JPN_URL, jb + '.pdf', jb + '.png', JPN_PDF,
                   'Page 46 of the Immigration Services Agency report "Immigration Control" (2015 edition): '
                   'Table 21, estimated number of foreign nationals overstaying, 1 January 2010-2015.')
for y, v in JPN.items():
    put('JPN', y, 'irregular_proxy_overstayers', 'F16', 'added',
        'Held by the secondary workbook and omitted from the panel; Table 21 of the archived Immigration '
        'Services Agency report prints it, with the 2011 and 2014 values the panel already holds.',
        'ISA, Immigration Control (2015 edition), Table 21, PDF page 46 (evidence/countries/JPN/%s)' % JPN_PDF,
        value=float(v),
        source='Immigration Services Agency of Japan (Ministry of Justice), Immigration Control (2015 edition), '
               'Table 21 Changes in the estimated number of foreign nationals staying beyond the authorized '
               'period of stay',
        url=JPN_URL, ref_date='1 January', grade='B',
        note='As of 1 January %d. Estimated number of foreign nationals staying beyond the authorized '
             'period of stay (不法残留者), total of Table 21; the 1 January 2011 (78,488) and 2014 (59,061) '
             'values in the same table equal the values already in the panel. Added on %s.' % (y, WHEN),
        verification='Confirmed in the archived source document (page 46, Table 21).')
AUS_PDF = 'irregular__9fcb57f01c__www.homeaffairs.gov.au.pdf'
au = fitz.open(os.path.join(EV, 'AUS', AUS_PDF))[62].get_text()
assert re.search(r'62,000 at 30 June 2015', au) and '64,600 at 30 June 2016' in au
ab = os.path.join(EV, 'AUS', 'SNAPSHOT__irregular_proxy_overstayers__HomeAffairs_AnnualReport2015-16_p63')
if not os.path.exists(ab + '.png'):
    L.page_extract(os.path.join(EV, 'AUS', AUS_PDF), 63, ab)
AUS_URL = url_of(AUS_PDF, 'https://www.homeaffairs.gov.au/reports-and-pubs/files/annual-reports/annual-report-2015-16.pdf')
L.add_snapshot_row('AUS', 'irregular_proxy_overstayers', AUS_URL, ab + '.pdf', ab + '.png', AUS_PDF,
                   'Page 63 of the Department of Immigration and Border Protection Annual Report 2015-16: '
                   'unlawful non-citizens in the community, 62,000 at 30 June 2015 and 64,600 at 30 June 2016.')
put('AUS', 2015, 'irregular_proxy_overstayers', 'F16', 'added',
    'Held by the secondary workbook and omitted from the panel; the archived Annual Report 2015-16 states it '
    'on the same basis as the 2016 value already in the panel.',
    'DIBP Annual Report 2015-16, PDF page 63 (evidence/countries/AUS/%s)' % AUS_PDF,
    value=62000.0,
    source='Australian Department of Immigration and Border Protection, Annual Report 2015-16, page 63',
    url=AUS_URL, ref_date='Mid-year / 30 June', grade='B',
    note='Reference date 30 June 2015. Number of unlawful non-citizens in the Australian community '
         '("62,000 at 30 June 2015 and 64,600 at 30 June 2016"): the same measure as the 2016 value already '
         'in the panel (64,600). Added on %s.' % WHEN,
    verification='Confirmed in the archived source document (PDF page 63).')
put('ISL', 2021, 'irregular_proxy_detections', 'F16', 'added',
    'Held by the secondary workbook and omitted from the panel; the archived Eurostat payload holds it.',
    'Eurostat migr_eipre payload (evidence/api/eurostat_migr_eipre_REVERIFY_2026-08-18.json), IS 2021',
    value=130.0, source='Eurostat, Third country nationals found to be illegally present (migr_eipre)',
    url='https://ec.europa.eu/eurostat/databrowser/view/migr_eipre/default/table',
    ref_date='Full calendar year', grade='A',
    note='Eurostat enforcement statistic: third-country nationals found to be illegally present during the '
         'calendar year (a person is counted once within the reference period; rounded to the nearest 5 by '
         'Eurostat). Dataset migr_eipre, freq=A citizen=TOTAL reason=TOTAL apprehen=TOTAL sex=T age=TOTAL '
         'unit=PER. Iceland reports only sporadically (2016, 2017, 2019, 2021). Added on %s.' % WHEN,
    verification='Read directly from the archived API response (evidence/api/'
                 'eurostat_migr_eipre_REVERIFY_2026-08-18.json); retrieved 2026-08-18.')

# ================================================================== shares follow the counts
# Only the rows this script touched are recomputed: recomputing every row would move the last
# digit of untouched values and make them look changed.
chg_keys = {(r['iso3'], int(r['year']), r['variable']) for r in log}
pop_rows = panel.index.isin([ix(i, y) for (i, y, v) in chg_keys if v == 'population'])
den = panel.population


def rows_for(v):
    own = panel.index.isin([ix(i, y) for (i, y, vv) in chg_keys if vv == v])
    return own | pop_rows


for v in ('foreign_born', 'foreign_nationals', 'irregular_stock', 'irregular_proxy_overstayers'):
    t = rows_for(v)
    m = t & panel[v].notna().values & den.notna().values
    panel.loc[m, v + '_pct_pop'] = panel.loc[m, v] / den[m]
    panel.loc[t & panel[v].isna().values, v + '_pct_pop'] = np.nan
t = rows_for('irregular_proxy_detections')
m = t & panel.irregular_proxy_detections.notna().values & den.notna().values
panel.loc[m, 'irregular_proxy_detections_per_1000_pop'] = panel.loc[m, 'irregular_proxy_detections'] / den[m] * 1000
m = pop_rows & panel.population.notna().values & panel.population_un_wpp2024.notna().values
panel.loc[m, 'population_wb_vs_unwpp_pct'] = (panel.loc[m, 'population'] - panel.loc[m, 'population_un_wpp2024'])     / panel.loc[m, 'population_un_wpp2024'] * 100
# metadata left behind in a cell whose value was moved out (Taiwan missing-worker counts that sat
# under the overstayer column) is cleared
for v in ('irregular_proxy_overstayers',):
    blank = panel[v].isna() & (panel.iso3 == 'TWN')
    bb = BASE[(BASE.iso3 == 'TWN') & BASE[v].isna() & BASE[v + '_ref_date'].notna()]   # judged on the baseline
    for r_ in bb.itertuples():
        log.append(dict(finding='F06', kind='metadata cleared', iso3='TWN', year=int(r_.year), variable=v,
                        old_value=np.nan, new_value=np.nan, old_grade=getattr(r_, v + '_grade'), new_grade='',
                        reason='The cell was empty but still carried the date and citation of a missing-worker '
                               'count that belongs to the absconded-worker column.',
                        evidence='MOL Table 12-7', alternative_label='', alternative_value=np.nan))
    for suf in ('_ref_date', '_source', '_url', '_note', '_grade', '_verification'):
        c_ = v + suf
        if c_ in panel.columns:
            panel.loc[blank, c_] = np.nan

# ================================================================== write the panel and the audit trail
panel.to_csv(os.path.join(D, 'panel_final.csv'), index=False, encoding='utf-8-sig')
chg = pd.DataFrame(log)
chg.insert(0, 'applied_on', WHEN)
chg.to_csv(os.path.join(D, 'audit_changes_%s.csv' % WHEN), index=False, encoding='utf-8-sig')
print('panel: %d audit changes (%s)' % (len(chg), chg.kind.value_counts().to_dict()))

# migrant_stock_alternatives.csv: the competing value recorded with each corrected migrant-stock cell.
# 74_assemble_panel.py adds the same rows when it finds the audit file; doing it here as well means one
# pass of 74 then 79 reaches the final state (rows are matched on country-year-variable-source, so
# running either script again changes nothing).
MIG = ('foreign_born', 'foreign_nationals')
alt = pd.read_csv(os.path.join(D, 'migrant_stock_alternatives.csv'))
for r in chg[chg.alternative_value.notna() & chg.variable.isin(MIG)].itertuples():
    hit = ((alt.iso3 == r.iso3) & (alt.year == int(r.year)) & (alt.variable == r.variable)
           & (alt.source == r.alternative_label))
    if hit.any():
        continue
    alt = pd.concat([alt, pd.DataFrame([dict(
        country=panel.loc[panel.iso3 == r.iso3, 'country'].iloc[0], iso3=r.iso3, year=int(r.year),
        variable=r.variable, source=r.alternative_label, value=int(r.alternative_value),
        used_in_panel='no',
        diff_vs_used_pct=round((r.alternative_value - r.new_value) / r.new_value * 100, 3))])],
        ignore_index=True)
alt = alt.sort_values(['iso3', 'variable', 'year', 'used_in_panel'], ascending=[True, True, True, False])
alt.to_csv(os.path.join(D, 'migrant_stock_alternatives.csv'), index=False, encoding='utf-8-sig')
print('migrant_stock_alternatives.csv: %d rows' % len(alt))

# corrections_applied.csv: value changes; deleted_values.csv: the deletion
ca = pd.read_csv(os.path.join(D, 'corrections_applied.csv'))
ca = ca[~((ca.corrected_on == WHEN))]
new = chg[chg.kind == 'corrected'][['iso3', 'year', 'variable', 'old_value', 'new_value', 'reason', 'evidence']].copy()
new['corrected_on'] = WHEN
ca = pd.concat([ca, new[ca.columns]], ignore_index=True)
ca.to_csv(os.path.join(D, 'corrections_applied.csv'), index=False, encoding='utf-8-sig')
dv = pd.read_csv(os.path.join(D, 'deleted_values.csv'))
dv = dv[~((dv.iso3 == 'TWN') & (dv.year == 2021) & (dv.variable == 'irregular_proxy_overstayers'))]
dv = pd.concat([dv, pd.DataFrame([dict(
    iso3='TWN', year=2021, variable='irregular_proxy_overstayers', deleted_value=81538.0, deleted_on=WHEN,
    reason='The cited source (Ministry of Labor Table 12-7) is the series of absconded workers, 55,805 at the '
           'end of 2021; the National Immigration Agency total of overstaying persons for 2021 is not in any '
           'archived or located document (the Legislative Yuan reports archived here end at 2020). Per the '
           'traceability rule the value was deleted rather than retained unverified (audit finding F06).')])],
               ignore_index=True)
dv.to_csv(os.path.join(D, 'deleted_values.csv'), index=False, encoding='utf-8-sig')
vc = os.path.join(SITE, 'verification', 'corrections_applied.csv')
print('corrections_applied.csv: %d rows | deleted_values.csv: %d rows' % (len(ca), len(dv)))
