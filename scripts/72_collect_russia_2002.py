# -*- coding: utf-8 -*-
"""Russia, Census 2002: foreign-born and foreign nationals.

Source: United Nations Expert Group Meeting on Measuring international migration (4-7 December
2006), paper ESA/STAT/AC.119/17, "Data sources on international migration: Case of the Russian
Federation", prepared by Olga Antonova of the State Committee of the Russian Federation on
Statistics (Rosstat). Page 5 gives the two migrant-stock definitions the 2002 census allows:

    by citizenship        1,455,304 persons not citizens of the RF
    by place of birth    11,976,822 persons born outside the RF (8.3%)

Both are read from the sentence and from Table 1 on that page, and the script asserts that the
two renderings agree. The paper itself cautions that the place-of-birth figure includes USSR
citizens who moved to the RF before the dissolution of the USSR, whom it is "difficult to agree"
are international migrants; that caution is carried into the cell note.
"""
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ext_lib as L                                    # noqa: E402

SITE = os.path.dirname(HERE)
EV = os.path.join(SITE, 'evidence', 'countries', 'RUS')
C = L.COLLECTED

URL = 'https://unstats.un.org/unsd/demographic/meetings/egm/migrationegm06/DOC%2017%20Russia.pdf'
f_pdf = 'foreign_born__UN_EGM2006_Antonova_Russia_ESA-STAT-AC119-17.pdf'
code, size = L.download(URL, os.path.join(EV, f_pdf))
print('UN EGM paper: http %s, %s bytes' % (code, format(size, ',')))
assert code == '200' and size > 100000

import pdfplumber
PAGE = 5
with pdfplumber.open(os.path.join(EV, f_pdf)) as pdf:
    txt = pdf.pages[PAGE - 1].extract_text()
m1 = re.search(r'citizenship \((\d+) persons or 1 % of RF residents were foreigners\)', txt)
m2 = re.search(r'place of birth \((\d+)\s+persons were born outside of the RF, or 8\.3%\)', txt, re.S)
assert m1 and m2, 'the two census sentences were not found on page %d' % PAGE
foreign_citizens, foreign_born = int(m1.group(1)), int(m2.group(1))
t1c = re.search(r'Citizenship\s+(\d+)\s+(\d+)', txt)
t1b = re.search(r'Place of birth\s+(\d+)\s+(\d+)', txt)
assert int(t1c.group(2)) == foreign_citizens and int(t1b.group(2)) == foreign_born, \
    'sentence and Table 1 disagree'
print('Russia Census 2002: not RF citizens %s | born outside the RF %s (sentence and Table 1 agree)'
      % (format(foreign_citizens, ','), format(foreign_born, ',')))

base = os.path.join(EV, 'SNAPSHOT__foreign_born__UN_EGM2006_Antonova_Russia_p%d_census2002' % PAGE)
x_pdf, x_png = L.page_extract(os.path.join(EV, f_pdf), PAGE, base)
L.add_snapshot_row('RUS', 'foreign_born', URL, x_pdf, x_png, f_pdf,
                   'Page %d of the UN expert-group paper: the 2002 census figures by place of birth '
                   'and by citizenship, with Table 1.' % PAGE)
L.add_snapshot_row('RUS', 'foreign_nationals', URL, x_pdf, x_png, f_pdf,
                   'Page %d of the UN expert-group paper: the 2002 census figures by place of birth '
                   'and by citizenship, with Table 1.' % PAGE)

NAME = ('Rosstat (State Committee of the Russian Federation on Statistics), All-Russia Census 2002, '
        'as reported in UN Expert Group Meeting paper ESA/STAT/AC.119/17 (O. Antonova, 2006)')
rows = [
    L.cell('RUS', 2002, 'foreign_born', foreign_born, 'RUS_CENSUS2002_BIRTH', NAME, URL, f_pdf,
           'Census, October 2002', 'B', 'census',
           'Census count; persons born outside the Russian Federation (8.3% of residents). The '
           'source cautions that this includes USSR citizens who moved to the Russian Federation '
           'before the dissolution of the USSR, whom it is "difficult to agree" are international '
           'migrants, so the level is far above a conventional immigrant count. Read from page 5 '
           'of the archived paper (sentence and Table 1 agree).',
           flag='includes former-USSR births',
           verification='Confirmed in the archived source document (page %d).' % PAGE),
    L.cell('RUS', 2002, 'foreign_nationals', foreign_citizens, 'RUS_CENSUS2002_CITIZEN', NAME, URL,
           f_pdf, 'Census, October 2002', 'B', 'census',
           'Census count; persons who are not citizens of the Russian Federation (about 1% of '
           'residents), which the source calls "foreigners". This counts by citizenship, so it '
           'includes stateless persons, as the panel\'s foreign_nationals definition does. Read '
           'from page 5 of the archived paper (sentence and Table 1 agree).',
           verification='Confirmed in the archived source document (page %d).' % PAGE),
]
out = L.write_stage('national_rus_cells.csv', rows)
print(out[['iso3', 'year', 'variable', 'value', 'grade']].to_string(index=False))
