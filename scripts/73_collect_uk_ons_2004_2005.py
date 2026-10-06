# -*- coding: utf-8 -*-
"""United Kingdom, 2004 and 2005: foreign-born and foreign nationals from the ONS Annual
Population Survey editions.

OECD (from 2006) and Eurostat (from 2009) cover the later years; the ONS "Historical UK
population data by country of birth and nationality" editions reach back to January-December
2004. Each edition's Table A (country of birth) and Table E (nationality) gives the total
resident population, the UK-born and the British, in thousands. As ONS itself does when it
reports "born abroad" (8.9% in 2004), the foreign-born is the total less the UK-born, and the
non-British is the total less the British.

Three honest limits are written into the cell notes: the figures are survey estimates rounded to
the nearest thousand; the editions were re-weighted to the 2011 Census in March 2015, so they
are not on the basis of the 2004-05 releases; and ONS warns that UK-born plus foreign-born may
not equal the published total (communal establishments), so the difference is an approximation
of the foreign-born rather than a published count.
"""
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ext_lib as L                                    # noqa: E402

SITE = os.path.dirname(HERE)
EV = os.path.join(SITE, 'evidence', 'countries', 'GBR')
C = L.COLLECTED
BASE = ('https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/populationandmigration/'
        'populationestimates/datasets/populationbycountryofbirthandnationality/%s/'
        'underlyingdatasheetsforpopulationbycountryofbirthandnationalityjan%s'
        'todec%s_tcm77-%s.xls')
EDITIONS = {2004: '409287', 2005: '409283'}
NAME = ('Office for National Statistics, Population by country of birth and nationality, Annual '
        'Population Survey, January to December %d (historical edition, re-weighted March 2015)')

rows = []
for yr, tcm in EDITIONS.items():
    yy = str(yr)[2:]
    url = BASE % (yr, yy, yy, tcm)
    f = 'foreign_born__ONS_APS_jan%s-dec%s_historical-edition.xls' % (yy, yy)
    code, size = L.download(url, os.path.join(EV, f))
    print('%d edition: http %s, %s bytes' % (yr, code, format(size, ',')))
    assert code == '200' and size > 1000000

    xl = pd.ExcelFile(os.path.join(EV, f), engine='xlrd')
    birth = pd.read_excel(xl, 'Table A', header=None)
    nat = pd.read_excel(xl, 'Table E', header=None)
    assert 'January %d to December %d' % (yr, yr) in str(birth.iloc[3, 0])

    def row(df, label):
        lab = [str(v).strip() for v in df[0].tolist()]
        i = next(k for k, v in enumerate(lab) if v == label)
        return float(df.iloc[i, 1]), float(df.iloc[i, 2])

    tot, tot_ci = row(birth, 'Total4')
    uk, _ = row(birth, 'United Kingdom')
    tot2, _ = row(nat, 'Total4')
    brit, _ = row(nat, 'British')
    assert tot == tot2, 'totals differ between Table A and Table E'
    fb, fn = (tot - uk) * 1000, (tot - brit) * 1000
    print('   total %s | UK-born %s | British %s thousand  ->  foreign-born %s, non-British %s'
          % (format(int(tot), ','), format(int(uk), ','), format(int(brit), ','),
             format(int(fb), ','), format(int(fn), ',')))

    x_pdf, x_png, made = L.table_extract(
        'ONS Annual Population Survey, January %d to December %d: UK resident population '
        '(thousands)' % (yr, yr), ['Row', 'Estimate (thousands)'],
        [(('Table A, Total', format(int(tot), ',')), False),
         (('Table A, United Kingdom (UK-born)', format(int(uk), ',')), False),
         (('Table A: total less UK-born = foreign-born', format(int(tot - uk), ',')), True),
         (('Table E, British', format(int(brit), ',')), False),
         (('Table E: total less British = non-British', format(int(tot - brit), ',')), True)],
        os.path.join(EV, 'SNAPSHOT__foreign_born__ONS_APS_jan%s-dec%s_extract' % (yy, yy)),
        'Source: ONS, Population by country of birth and nationality (Annual Population Survey), '
        '%d edition. Retrieved %s.' % (yr, C))
    for var in ('foreign_born', 'foreign_nationals'):
        L.add_snapshot_row('GBR', var, url, x_pdf if x_pdf in made else '',
                           x_png if x_png in made else '', f,
                           'Rows of Tables A and E used for %d, rendered from the archived '
                           'workbook, which is archived beside it.' % yr)

    common = (' Survey estimate (Annual Population Survey, 12 months January-December %d), '
              'rounded to the nearest thousand; 95%% confidence interval of the total +/- %d '
              'thousand. These historical editions were re-weighted to the 2011 Census in March '
              '2015, so they are not on the basis of the releases of the time. This source '
              'differs from the OECD values used for 2006-2008 and the Eurostat values used from '
              '2009, and no overlap with this edition exists to measure the difference.'
              % (yr, int(tot_ci)))
    ref = 'January-December %d (12-month survey average)' % yr
    rows.append(L.cell(
        'GBR', yr, 'foreign_born', int(fb), 'GBR_ONS_APS_%d' % yr, NAME % yr, url, f, ref, 'B',
        'survey',
        'DERIVED BY SUBTRACTION: total resident population (%s thousand) less UK-born (%s '
        'thousand), both rows of Table A, which is how ONS reports "born abroad". ONS warns that '
        'UK-born plus foreign-born may not equal the total (some communal establishments are '
        'excluded), so this approximates the foreign-born.%s'
        % (format(int(tot), ','), format(int(uk), ','), common),
        flag='splice; derived by subtraction',
        verification='Confirmed in the archived source file (Table A, rows Total and United '
                     'Kingdom).'))
    rows.append(L.cell(
        'GBR', yr, 'foreign_nationals', int(fn), 'GBR_ONS_APS_%d' % yr, NAME % yr, url, f, ref,
        'B', 'survey',
        'DERIVED BY SUBTRACTION: total resident population (%s thousand) less British nationals '
        '(%s thousand), both rows of Table E.%s'
        % (format(int(tot), ','), format(int(brit), ','), common),
        flag='splice; derived by subtraction',
        verification='Confirmed in the archived source file (Table E, rows Total and British).'))

out = L.write_stage('national_gbr_cells.csv', rows)
print('\ncells written: %d' % len(out))
print(out[['iso3', 'year', 'variable', 'value', 'grade']].to_string(index=False))
