# -*- coding: utf-8 -*-
"""Taiwan, 2001-2011 foreign residents and 2001-2009 population.

Foreign residents. The Ministry of the Interior's statistical query system holds one
consolidated table, 外僑居留人數─按國籍別職業別分, from ROC 85 (1996) to ROC 111 (2022). The
bulletins the archive already cites for 2012-2022 are cut from the same data, and all eleven
of those values reproduce exactly from this table (asserted below; the run stops if one
does not). The table also gives 2001-2011.

A caution the input workbook raised is carried, not dropped: its note says the series "on this
basis begins in 2012; 2010 and 2011 are not available on a comparable basis". MOI's own table
shows no break there (2010 418,802; 2011 466,206; 2012 483,921) and carries no footnote about a
definition change, so the earlier years are included, graded on how they were read and flagged
for comparability. A definition change inside the table cannot be ruled out from the table
alone, and the cell notes say so.

Population. MOI's query form needs a JavaScript session, so the year-end series is read from the
National Development Council's Taiwan Statistical Data Book 2019, Table 2-2 (page 51), which
cites MOI. It is published in thousands; the archive's 2010-2016 Taiwan values are the same
figures x 1,000, and 2010-2012 are asserted equal below.
"""
import os
import re
import sys
import io

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ext_lib as L                                    # noqa: E402

SITE = os.path.dirname(HERE)
D = os.path.join(SITE, 'data')
TW = os.path.join(SITE, 'evidence', 'countries', 'TWN')
C = L.COLLECTED
P = L.baseline_panel()   # the panel as it stood before the extension
tw = P[P.iso3 == 'TWN'].set_index('year')

rows = []

# ----------------------------------------------------------------- foreign residents
STATIS = ('https://statis.moi.gov.tw/micst/webMain.aspx?sys=220&kind=21&type=1&funid=c0930103'
          '&cycle=4&outmode=12&utf=1&compmode=0&outkind=3&fldspc=0,29,&codlst0=111'
          '&codspc1=0,1,2,15,18,4,&rdm=ajdqUe3i&ym=8500&ymt=11100')
f_csv = 'foreign_nationals__MOI_statis_c0930103_ROC85-111__retrieved_%s.csv' % C
code, size = L.download(STATIS, os.path.join(TW, f_csv))
print('MOI foreign residents table: http %s, %s bytes' % (code, format(size, ',')))
assert code == '200' and size > 50000, 'MOI table not retrieved'

raw = open(os.path.join(TW, f_csv), 'rb').read().decode('utf-8-sig')
d = pd.read_csv(io.StringIO(raw))
d.columns = [c.strip() for c in d.columns]
lab = d.columns[0]
tot = d[d[lab].astype(str).str.contains('性別總計/ 職業別總計')].copy()
tot['year'] = tot[lab].astype(str).str.extract(r'^(\d+)年')[0].astype(int) + 1911
tot = tot.set_index('year')['總計'].astype(int)
print('years in the table: %d-%d (%d)' % (tot.index.min(), tot.index.max(), len(tot)))

# the already-published years must reproduce exactly, or this collector stops
pub = tw[tw.foreign_nationals.notna()].foreign_nationals
bad = [(y, int(pub[y]), int(tot[y])) for y in pub.index if int(pub[y]) != int(tot[y])]
assert not bad, 'published Taiwan values differ from the MOI table: %s' % bad
print('published Taiwan foreign residents reproduced exactly: %d of %d years' % (len(pub), len(pub)))

# a readable extract of the totals row for every year; the raw CSV is 1,600 rows long
ext_rows = [((str(y), format(int(tot[y]), ',')), 2001 <= y <= 2011) for y in sorted(tot.index)]
x_pdf, x_png, made = L.table_extract(
    'Taiwan: foreign residents (外僑居留人數), year-end totals 1996-2022',
    ['Year', 'Persons'], ext_rows,
    os.path.join(TW, 'SNAPSHOT__foreign_nationals__MOI_statis_c0930103_totals_extract'),
    'Source: Ministry of the Interior, Department of Statistics, statistical query system, table '
    '外僑居留人數─按國籍別職業別分, row 性別總計/職業別總計. Retrieved %s.' % C,
    'Highlighted rows (2001-2011) are the values added to the panel; the 2012-2022 rows are the '
    'values already published, which this table reproduces exactly.')
L.add_snapshot_row('TWN', 'foreign_nationals', STATIS, x_pdf if x_pdf in made else '',
                   x_png if x_png in made else '', f_csv,
                   'Yearly totals read from the archived CSV (the CSV itself is 1,600 rows long).')

NOTE = ('Foreign residents holding a valid resident certificate (外僑居留人數), year-end 31 '
        'December. INCLUDES migrant workers (移工), who are roughly 75-84% of the total. EXCLUDES '
        'people from Mainland China, Hong Kong and Macau (including Mainland Chinese spouses '
        '陸配), who are counted separately. Read from the MOI Department of Statistics '
        'consolidated table 1996-2022, from which the 2012-2022 values already published also '
        'reproduce exactly. COMPARABILITY CAUTION: the input workbook states that the series on '
        'this basis begins in 2012 and that earlier years are not available on a comparable '
        'basis. This table shows no break at 2011/2012 (2010: 418,802; 2011: 466,206; 2012: '
        '483,921) and carries no footnote on a change of definition, but one inside the table '
        'cannot be ruled out.')
for y in range(2001, 2012):
    rows.append(L.cell(
        'TWN', y, 'foreign_nationals', int(tot[y]), 'TWN_MOI_STATIS',
        'Taiwan Ministry of the Interior, Department of Statistics, statistical query system '
        '(內政統計查詢網), 外僑居留人數─按國籍別職業別分', STATIS, f_csv, '31 December', 'A',
        'annual', NOTE, flag='comparability caution',
        verification='Read directly from the archived CSV (evidence/countries/TWN/%s); the 11 '
                     'values 2012-2022 already published reproduce exactly from the same table. '
                     'Retrieved %s.' % (f_csv, C)))

# ----------------------------------------------------------------- population
NDC = ('https://ws.ndc.gov.tw/Download.ashx?u=LzAwMS9hZG1pbmlzdHJhdG9yLzExL3JlbGZpbGUvNTgxNy8zMjg0'
       'Mi9lMGI5MDNmOC02MDliLTQ4ODAtOTAxNy0yN2JmYzg4M2QyYWQucGRm&n=VGFpd2FuIFN0YXRpc3RpY2FsIERhdGE'
       'gQm9vayAyMDE5LnBkZg%3D%3D&icon=..pdf')
f_pdf = 'population__NDC_TaiwanStatisticalDataBook2019.pdf'
code, size = L.download(NDC, os.path.join(TW, f_pdf))
print('NDC Taiwan Statistical Data Book 2019: http %s, %s bytes' % (code, format(size, ',')))
assert code == '200' and size > 500000, 'NDC data book not retrieved'

import pdfplumber
PAGE = 51
with pdfplumber.open(os.path.join(TW, f_pdf)) as pdf:
    text = pdf.pages[PAGE - 1].extract_text()
assert '2-2. Population' in text and 'End of Year' in text, 'page %d is not Table 2-2' % PAGE
thou = {}
for line in text.split('\n'):
    m = re.match(r'^\s*(20(?:0\d|1[0-2]))\s+([\d,]+)\s+[\d,]+\s+[\d,]+\b', line)
    if m:
        thou[int(m.group(1))] = int(m.group(2).replace(',', ''))
print('Table 2-2 years read: %s' % sorted(thou))
for y in (2010, 2011, 2012):
    assert thou[y] * 1000 == int(tw.loc[y, 'population']), \
        'Table 2-2 %d = %s thousand but the panel holds %s' % (y, thou[y], tw.loc[y, 'population'])
print('Taiwan 2010-2012 population in Table 2-2 equals the published values: yes')

base = os.path.join(TW, 'SNAPSHOT__population__NDC_TaiwanStatisticalDataBook2019_p%d_table2-2' % PAGE)
x_pdf, x_png = L.page_extract(os.path.join(TW, f_pdf), PAGE, base)
L.add_snapshot_row('TWN', 'population', NDC, x_pdf, x_png, f_pdf,
                   'Page %d of the Taiwan Statistical Data Book 2019 (Table 2-2, Population, End of '
                   'Year), cut out so the table can be read without opening the 432-page file.'
                   % PAGE)

for y in range(2001, 2010):
    rows.append(L.cell(
        'TWN', y, 'population', thou[y] * 1000, 'TWN_NDC_DATABOOK',
        'National Development Council, Taiwan Statistical Data Book 2019, Table 2-2 Population '
        '(End of Year; source cited there: Ministry of the Interior)', NDC, f_pdf,
        '31 December', 'B', 'annual',
        'Year-end registered population, published in thousands (so rounded to the nearest '
        '1,000), as the archive\'s existing 2010-2016 Taiwan values are. Page %d of the archived '
        'PDF.' % PAGE,
        verification='Confirmed in the archived source document (page %d, Table 2-2): the '
                     '2010-2012 values in the same table equal the values already published.'
                     % PAGE))

out = L.write_stage('national_twn_cells.csv', rows)
print('\ncells written: %d' % len(out))
print(out.groupby('variable').size().to_string())
print(out[out.variable == 'foreign_nationals'][['year', 'value']].to_string(index=False))
