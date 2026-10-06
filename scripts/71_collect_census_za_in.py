# -*- coding: utf-8 -*-
"""Census figures for 2001: South Africa and India (foreign-born).

South Africa. Figure 3.1 of Statistics South Africa's Census 2022 Statistical Release P0301.4
(page 41 of the PDF already archived for 2011 and 2022) gives the population born outside the
country for Census 1996, 2001, 2011 and 2022. The 2011 and 2022 values already published are
asserted equal to the same figure, so the 2001 value is the same measure.

India. The Registrar General's Census 2001 Table D-01 (population classified by place of
birth and sex, India) lists births in each foreign continent. The identified foreign births
are summed; the 421 persons "unclassifiable" by place of birth are not counted, and the
arithmetic is asserted against total minus born-in-India.
"""
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ext_lib as L                                    # noqa: E402

SITE = os.path.dirname(HERE)
D = os.path.join(SITE, 'data')
EV = os.path.join(SITE, 'evidence', 'countries')
C = L.COLLECTED
P = L.baseline_panel()   # the panel as it stood before the extension
rows = []

# ------------------------------------------------------------------ South Africa
import pdfplumber
ZA_FILE = 'foreign_born__c204ed0e2a__census.statssa.gov.za.pdf'
ZA_URL = 'https://census.statssa.gov.za/assets/documents/2022/P03014_Census_2022_Statistical_Release.pdf'
PAGE = 41
with pdfplumber.open(os.path.join(EV, 'ZAF', ZA_FILE)) as pdf:
    txt = pdf.pages[PAGE - 1].extract_text()
m = re.search(r'Frequency\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)', txt)
assert m and 'Figure 3.1' in txt, 'Figure 3.1 not found on page %d' % PAGE
v1996, v2001, v2011, v2022 = [int(x.replace(',', '')) for x in m.groups()]
za = P[P.iso3 == 'ZAF'].set_index('year')
assert v2011 == int(za.loc[2011, 'foreign_born']) and v2022 == int(za.loc[2022, 'foreign_born']), \
    'Figure 3.1 does not match the published 2011/2022 South African values'
print('ZAF Figure 3.1: 1996 %s | 2001 %s | 2011 %s | 2022 %s (2011 and 2022 equal the published values)'
      % tuple(format(v, ',') for v in (v1996, v2001, v2011, v2022)))
base = os.path.join(EV, 'ZAF', 'SNAPSHOT__foreign_born__StatsSA_Census2022Release_p%d_figure3-1' % PAGE)
x_pdf, x_png = L.page_extract(os.path.join(EV, 'ZAF', ZA_FILE), PAGE, base)
L.add_snapshot_row('ZAF', 'foreign_born', ZA_URL, x_pdf, x_png, ZA_FILE,
                   'Page %d of Census 2022 Statistical Release P0301.4: Figure 3.1, population '
                   'born outside South Africa, Census 1996-2022.' % PAGE)
rows.append(L.cell(
    'ZAF', 2001, 'foreign_born', v2001, 'ZAF_CENSUS2001',
    za.loc[2011, 'foreign_born_source'], ZA_URL, ZA_FILE, 'Census 2001', 'B', 'census',
    'Census count; persons born outside South Africa. Read from Figure 3.1 of the Census 2022 '
    'Statistical Release, which tabulates Census 1996 = %s, 2001 = %s, 2011 = %s, 2022 = %s '
    'on one basis. The 2011 and 2022 values already published are the same figures.'
    % tuple(format(v, ',') for v in (v1996, v2001, v2011, v2022)),
    verification='Confirmed in the archived source document (page %d, Figure 3.1).' % PAGE))

# ------------------------------------------------------------------ India
IN_PAGE = 'https://censusindia.gov.in/nada/index.php/catalog/19293'
IN_XLS_URL = 'https://censusindia.gov.in/nada/index.php/catalog/19293/download/22425/PC01_D01_00.xls'
f_xls = 'foreign_born__ORGI_Census2001_D01_India__PC01_D01_00.xls'
f_html = 'foreign_born__ORGI_Census2001_D01_India__catalog-19293.html'
c1, s1 = L.download(IN_XLS_URL, os.path.join(EV, 'IND', f_xls))
c2, s2 = L.download(IN_PAGE, os.path.join(EV, 'IND', f_html))
print('India D-01 workbook: http %s, %s bytes | catalogue page: http %s, %s bytes'
      % (c1, format(s1, ','), c2, format(s2, ',')))
assert c1 == '200' and s1 > 400000 and c2 == '200'

d = pd.read_excel(os.path.join(EV, 'IND', f_xls), header=None, skiprows=5, engine='xlrd')
d = d[d[3].astype(str).str.upper() == 'INDIA'].reset_index(drop=True)
get = lambda label: int(float(d[d[4].astype(str).str.strip() == label].iloc[0][5]))
total, born_in = get('Total Population'), get('Born in India')
cont = {k: get(k) for k in ('Countries in Asia beyond India', 'Countries in Europe',
                            'Countries in Africa', 'Countries in America',
                            'Countries in Oceania')}
unclass = get('Unclassifiable')
foreign = sum(cont.values())
assert foreign + unclass == total - born_in, 'rows do not add up to total minus born in India'
print('India 2001: identified foreign births %s + unclassifiable %s = total %s - born in India %s'
      % (format(foreign, ','), unclass, format(total, ','), format(born_in, ',')))

xrows = [(('Total population', format(total, ',')), False), (('Born in India', format(born_in, ',')), False)]
xrows += [((k, format(v, ',')), True) for k, v in cont.items()]
xrows += [(('Sum of the five foreign continents (the value used)', format(foreign, ',')), True),
          (('Unclassifiable (not counted)', format(unclass, ',')), False)]
x_pdf, x_png, made = L.table_extract(
    'Census of India 2001, Table D-01: population classified by place of birth and sex - India, persons',
    ['Row of the table', 'Persons'], xrows,
    os.path.join(EV, 'IND', 'SNAPSHOT__foreign_born__ORGI_Census2001_D01_India_extract'),
    'Source: Office of the Registrar General & Census Commissioner, India; file PC01_D01_00.xls '
    '(%s). Retrieved %s.' % (IN_PAGE, C))
print('extract rendered:', [os.path.basename(x) for x in made])
L.add_snapshot_row('IND', 'foreign_born', IN_PAGE, x_pdf if x_pdf in made else '',
                   x_png if x_png in made else '', f_html,
                   'Rows of Table D-01 (India) used for the 2001 value, rendered from the archived '
                   'workbook; the workbook and the catalogue page are archived beside it.')
ind = P[(P.iso3 == 'IND') & P.foreign_born.notna()].set_index('year')
rows.append(L.cell(
    'IND', 2001, 'foreign_born', foreign, 'IND_CENSUS2001',
    'Office of the Registrar General & Census Commissioner, India, Census of India 2001, Table '
    'D-01 Population classified by place of birth and sex, India', IN_PAGE, f_xls,
    'Census reference date', 'B', 'census',
    'Census count; persons enumerated in India who were born in another country: the sum of '
    'the five foreign-continent rows of Table D-01 (Asia beyond India %s, Europe %s, Africa %s, '
    'America %s, Oceania %s). A further %d persons are "unclassifiable" by place of birth and '
    'are not counted. Unlike the 2011 value, which is published rounded to the nearest '
    'thousand (5,490,000), this figure is exact.'
    % tuple([format(v, ',') for v in cont.values()] + [unclass]),
    verification='Confirmed in the archived source file (Table D-01, rows for the foreign '
                 'continents); the rows add up to total population minus born in India.'))

out = L.write_stage('national_census_za_in_cells.csv', rows)
print('\ncells written: %d' % len(out))
print(out[['iso3', 'year', 'variable', 'value', 'grade']].to_string(index=False))
