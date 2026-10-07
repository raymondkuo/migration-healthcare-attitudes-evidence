# -*- coding: utf-8 -*-
"""Rewrite every workbook sheet that has a CSV counterpart from that CSV.

Sheets had drifted from the data files twice (Verification_log and Source_register
predated the Eurostat re-test; Known_issues and Codebook then gained translation
columns). Run this after any change to data/*.csv rather than patching sheets by hand.
README counters that quote row counts are refreshed too."""
import os
import openpyxl
import pandas as pd

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(SITE, 'data')
XLSX = os.path.join(D, 'FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx')

SHEETS = {
    'Panel_final': 'panel_final.csv',
    'Data_quality': 'data_quality.csv',
    'Corrections_applied': 'corrections_applied.csv',
    'Known_issues': 'known_issues.csv',
    'Verification_log': 'verification_log.csv',
    'Source_register': 'source_register.csv',
    'Irregular_estimates_all': 'irregular_estimates_all.csv',
    'Codebook': 'codebook.csv',
    'Deleted_values': 'deleted_values.csv',
    'Revision_history': 'revision_history.csv',
    'Audit_changes': 'audit_changes_2026-10-07.csv',
}

# The sheet is written in plain ASCII, but the translation columns are Chinese by
# definition — only fold the typographic punctuation that has an ASCII equivalent.
PUNCT = {'—': '-', '–': '-', '’': "'", '‘': "'", '“': '"', '”': '"'}


def clean(x):
    if not isinstance(x, str):
        return x
    for a, b in PUNCT.items():
        x = x.replace(a, b)
    return x


wb = openpyxl.load_workbook(XLSX)
# a sheet added to SHEETS after the workbook was built is created, placed after README
for s in SHEETS:
    if s not in wb.sheetnames:
        wb.create_sheet(s, 1)
        print('created sheet %s' % s)

for sheet, csv in SHEETS.items():
    fp = os.path.join(D, csv)
    if not os.path.exists(fp):
        print('%-24s SKIP (no %s)' % (sheet, csv))
        continue
    df = pd.read_csv(fp).fillna('')
    pos = wb.sheetnames.index(sheet)
    before = (wb[sheet].max_row - 1, wb[sheet].max_column)
    del wb[sheet]
    ws = wb.create_sheet(sheet, pos)
    ws.append([clean(c) for c in df.columns])
    for rec in df.itertuples(index=False, name=None):
        ws.append([clean(x) for x in rec])
    ws.freeze_panes = 'A2'
    for col in ws.columns:
        w = max((len(str(c.value)) for c in col[:200] if c.value is not None), default=10)
        ws.column_dimensions[col[0].column_letter].width = min(max(w + 2, 10), 62)
    flag = '' if before == (ws.max_row - 1, ws.max_column) else '   <- changed'
    print('%-24s %d x %-3d -> %d x %d%s'
          % (sheet, before[0], before[1], ws.max_row - 1, ws.max_column, flag))

log = pd.read_csv(os.path.join(D, 'verification_log.csv'))
hist = pd.read_csv(os.path.join(D, 'revision_history.csv')).fillna('')
last = str(hist[hist.amends_data == 'yes'].date.max())
ws = wb['README']
for row in range(1, ws.max_row + 1):
    if str(ws.cell(row, 1).value or '') == 'Built':
        ws.cell(row, 2).value = (
            'Sources first retrieved and verified 2026-08-17. Data last revised %s. Every '
            'amendment after first collection is dated on the Revision_history sheet.' % last)
    if str(ws.cell(row, 1).value or '') == 'Revision_history':
        ws.cell(row, 2).value = 'Every amendment to the data after first collection, dated.'
labels = [str(ws.cell(r, 1).value or '') for r in range(1, ws.max_row + 1)]
if 'Audit_changes' not in labels and 'Revision_history' in labels:
    at = labels.index('Revision_history') + 2
    ws.insert_rows(at)
    ws.cell(at, 1).value = 'Audit_changes'
    ws.cell(at, 2).value = 'Every cell changed after the audit of 2026-10-07: old and new value, grade, reason, evidence.'
    print('README: Audit_changes added to the sheet list')
if 'Revision_history' not in labels and 'Deleted_values' in labels:
    at = labels.index('Deleted_values') + 2          # 1-based row after Deleted_values
    ws.insert_rows(at)
    ws.cell(at, 1).value = 'Revision_history'
    ws.cell(at, 2).value = 'Every amendment to the data after first collection, dated.'
    print('README: Revision_history added to the sheet list')
for row in range(1, ws.max_row + 1):
    if str(ws.cell(row, 1).value or '') == 'Verification_log':
        ws.cell(row, 2).value = ('All %d value-by-value comparisons against live sources, each '
                                 'stamped with the stage and the date it was performed.' % len(log))

# README counters that quote the size of the source register, recomputed rather than typed
reg_ = pd.read_csv(os.path.join(D, 'source_register.csv')).fillna('')
pan_ = pd.read_csv(os.path.join(D, 'panel_final.csv'))
ovl_ = pd.read_csv(os.path.join(D, 'extension_overlap_check.csv'))
spl_ = pd.read_csv(os.path.join(D, 'extension_splice_summary.csv'))
COUNTS = {
    'Document source citations': '%d source rows across %d distinct URLs'
                                 % (len(reg_), reg_.source_url.nunique()),
    '  archived in the country folders':
        '%d of %d (%d verified live via API, %d archived as documents)'
        % (int((reg_.local_file.astype(str).str.len() > 3).sum()), len(reg_),
           int((reg_.retrieval == 'VERIFIED_API').sum()), int((reg_.retrieval == 'ARCHIVED').sum())),
}
for r_ in range(1, ws.max_row + 1):
    lab = str(ws.cell(r_, 1).value or '')
    if lab in COUNTS:
        ws.cell(r_, 2).value = COUNTS[lab]

# counts typed into the README sheet at first release, recomputed from the data files
import re
GRADE_VARS = ['population', 'foreign_born', 'foreign_nationals', 'irregular_stock',
              'irregular_proxy_overstayers', 'irregular_proxy_detections']
gc_ = pd.Series([g for v in GRADE_VARS for g in pan_[v + '_grade'].dropna()
                 if str(g).strip()]).value_counts()
corr_ = pd.read_csv(os.path.join(D, 'corrections_applied.csv'))
n_der_ = int(sum((pan_[v + '_derived'].astype(str).str.strip() == 'yes').sum()
                 for v in ('foreign_born', 'foreign_nationals', 'irregular_stock')))
gap_ = pan_.population_wb_vs_unwpp_pct.dropna()
late_ = pan_[pan_.year >= 2010]
dv_ = pd.read_csv(os.path.join(D, 'deleted_values.csv'))
VAR_LABEL_ = {'irregular_stock': 'irregular stock', 'irregular_proxy_overstayers': 'overstayers'}
dv_text_ = '%d (%s; see Deleted_values)' % (
    len(dv_), '; '.join('%s %d %s' % (pan_.loc[pan_.iso3 == r.iso3, 'country'].iloc[0], r.year,
                                       VAR_LABEL_.get(r.variable, r.variable)) for r in dv_.itertuples()))
EVIDENCE_ROWS = {
    'countries/<ISO3>_<Name>/': ('evidence/countries/<ISO3>/',
                                 'One folder per country: README.md, data_from_source.csv, value_check.csv, '
                                 'source_manifest.csv, and the downloaded documents, web captures and page '
                                 'extracts themselves (there is no sources/ subfolder).'),
    'data_raw/': ('evidence/api/',
                  'The archived bulk and API payloads (World Bank, Eurostat, OECD, UN) and their rendered '
                  'mirrors, each dated in its name or in data/api_snapshots.csv.'),
    'scripts/': ('scripts/',
                 'Every script used. Only the pipeline in REBUILD.md can be re-run safely; the first-release '
                 'builders (numbered below 67) would undo later corrections.'),
}
FIXED = {
    'Values deleted as untraceable': dv_text_,
    'Corrections applied': '%d values across %d countries: %s (see Corrections_applied)'
                           % (len(corr_), corr_.iso3.nunique(), ', '.join(sorted(corr_.iso3.unique()))),
    'Values flagged as derived': str(n_der_),
    'Reference dates': ('Dates differ by source and are recorded per value (*_ref_date). Eurostat stocks are 1 '
                        'January of the labelled year; OECD dates follow the national source (30 June for '
                        "Australia's foreign-born, 1 January for the foreign population of Japan, Turkey, the "
                        'United Kingdom and Germany, none stated for several survey- or census-based series). '
                        'Years are as the publisher labels them and nothing was shifted. If the survey is '
                        'fielded mid-year, either lag the covariate or state the convention explicitly.'),
}
GRADE_LABEL = {
    'A': 'A - decoded from a machine-readable official source (API response, open-data file or official workbook) and matched exactly',
    'B': 'B - read from an archived source document (PDF, web page, printed table or chart) in which the value appears, or summed from figures printed there',
    'C': 'C - computed by the archive as the midpoint of a published range (the source prints no single figure); a single-number estimate a source publishes is A or B',
    'D': 'D - no archived source supports the value (none are published: such values are deleted)',
}
REGEX = {
    'Main regressor': (r'covers \d+ of 40 countries',
                       'covers %d of 40 countries' % pan_[pan_.foreign_nationals.notna()].iso3.nunique()),
    'Second choice': (r'\(\d+ countries\)',
                      '(%d countries)' % pan_[pan_.foreign_born.notna()].iso3.nunique()),
    'Irregular migration': (r'Coverage is [\d.]+% of (?:the 2010-2022 )?country-years for stocks'
                            r'(?: \(not collected earlier\))?',
                            'Coverage is %.1f%% of the 2010-2022 country-years for stocks (not '
                            'collected earlier)' % (100 * late_.irregular_stock.notna().mean())),
    'Population denominator': (r'more than 3% for \d+ country-years',
                               'more than 3%% for %d country-years' % int((gap_.abs() > 3).sum())),
}
for r_ in range(1, ws.max_row + 1):
    lab = str(ws.cell(r_, 1).value or '')
    if lab in FIXED:
        ws.cell(r_, 2).value = FIXED[lab]
    elif lab in EVIDENCE_ROWS:
        ws.cell(r_, 1).value, ws.cell(r_, 2).value = EVIDENCE_ROWS[lab]
    elif lab[:4] in ('A - ', 'B - ', 'C - ', 'D - '):
        ws.cell(r_, 1).value = GRADE_LABEL[lab[0]]
        ws.cell(r_, 2).value = int(gc_.get(lab[0], 0))
    elif lab in REGEX:
        pat, new_ = REGEX[lab]
        old_ = str(ws.cell(r_, 2).value)
        assert re.search(pat, old_), 'README sheet row %s no longer matches %s' % (lab, pat)
        ws.cell(r_, 2).value = re.sub(pat, lambda m: new_, old_, count=1)

n_new_ = sum(int(pan_[v + '_collected_on'].notna().sum()) for v in
             ('population', 'population_un_wpp2024', 'foreign_born', 'foreign_nationals'))
aud_ = pd.read_csv(os.path.join(D, 'audit_changes_2026-10-07.csv'))
ROWS_ADD = [
    ('Audit of 2026-10-07',
     'The audit of 2026-10-07 (GitHub issues #1-#25) was checked finding by finding against the archived '
     'sources. %d cell changes follow (Audit_changes sheet: %s); values changed are in Corrections_applied, the '
     'deletion in Deleted_values, and the verdicts in verification/AUDIT_RESPONSE_2026-10-07.md. Grades mean '
     'provenance only: A decoded from a machine-readable source, B read from an archived document, C the midpoint '
     'of a published range computed by the archive.'
     % (len(aud_), ', '.join('%d %s' % (v, k) for k, v in aud_.kind.value_counts().items()))),
    ('Extension to 2001',
     'On 2026-10-07 the panel was extended from 2010-2022 back to 2001: %d rows, %s new values. '
     'The extension itself changed no value published earlier; the audit later the same day did change '
     'some (see Audit of 2026-10-07). Every cell has a source_type and flag column; '
     '%d series needed a source change at the join and are flagged (see Source_register, '
     'data/extension_splice_summary.csv and the website). The file name is kept from the first '
     'release so that existing links still work.'
     % (len(pan_), format(n_new_, ','), len(spl_))),
    ('Re-check on 2026-10-07',
     '%s values published before the extension were compared with fresh responses from '
     'Eurostat, OECD, the World Bank and UN WPP: %s reproduced exactly.'
     % (format(int(ovl_.cells_compared.sum()), ','), format(int(ovl_.identical.sum()), ','))),
]
labels_ = [str(ws.cell(r_, 1).value or '') for r_ in range(1, ws.max_row + 1)]
anchor = labels_.index('Corrections applied') + 1 if 'Corrections applied' in labels_ else None
for lab, text in ROWS_ADD:
    labels_ = [str(ws.cell(r_, 1).value or '') for r_ in range(1, ws.max_row + 1)]
    if lab in labels_:
        ws.cell(labels_.index(lab) + 1, 2).value = text
    elif anchor:
        ws.insert_rows(anchor + 1)
        ws.cell(anchor + 1, 1).value, ws.cell(anchor + 1, 2).value = lab, text
        anchor += 1
wb.save(XLSX)
# the README sheet is also published as data/readme.csv: re-export it so that the two cannot drift apart again
# (the CSV still carried the first-release reference-date, coverage and grade statements; re-audit R02)
pd.read_excel(XLSX, sheet_name='README').to_csv(os.path.join(D, 'readme.csv'), index=False, encoding='utf-8-sig')

chk = openpyxl.load_workbook(XLSX, read_only=True)
print()
bad = 0
for sheet, csv in SHEETS.items():
    fp = os.path.join(D, csv)
    if not os.path.exists(fp):
        continue
    df = pd.read_csv(fp)
    ws = chk[sheet]
    ok = (ws.max_row - 1 == len(df) and ws.max_column == len(df.columns))
    bad += not ok
    print('  %-24s %-12s csv %-12s %s'
          % (sheet, '%d x %d' % (ws.max_row - 1, ws.max_column),
             '%d x %d' % (len(df), len(df.columns)), 'ok' if ok else '*** DRIFT ***'))
assert not bad, '%d sheet(s) still drift' % bad
print('\nall %d sheets match data/*.csv' % len(SHEETS))
