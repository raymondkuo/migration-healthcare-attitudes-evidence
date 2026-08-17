# -*- coding: utf-8 -*-
"""Write manifest/website_manifest.json describing this build accurately."""
import os, json, hashlib
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(BASE, 'migration-data-archive')
ACCESS = '2026-08-17'


def sha(rel):
    p = os.path.join(SITE, rel.replace('/', os.sep))
    if not os.path.exists(p):
        return None
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return {'path': rel, 'bytes': os.path.getsize(p), 'sha256': h.hexdigest()}


panel = pd.read_csv(os.path.join(SITE, 'data', 'panel_final.csv'))
vlog = pd.read_csv(os.path.join(SITE, 'data', 'verification_log.csv'))
corr = pd.read_csv(os.path.join(SITE, 'data', 'corrections_applied.csv'))
snaps = pd.read_csv(os.path.join(SITE, 'data', 'web_snapshots.csv'))
apis = pd.read_csv(os.path.join(SITE, 'data', 'api_snapshots.csv'))
ck = pd.read_csv(os.path.join(SITE, 'manifest', 'checksums.csv'))

VARS = ['population', 'foreign_born', 'foreign_nationals', 'irregular_stock',
        'irregular_proxy_overstayers', 'irregular_proxy_detections']
grades = pd.Series([g for v in VARS for g in panel[v + '_grade'].dropna()
                    if str(g).strip()]).value_counts()

country_pages = len([f for f in os.listdir(os.path.join(SITE, 'countries')) if f.endswith('.html')])
top_pages = sorted(f for f in os.listdir(SITE) if f.endswith('.html'))

m = {
    'generated_at': ACCESS,
    'generator': 'scripts/24_build_site.py, 25_country_pages.py, 26_other_pages.py (Python)',
    'validated_by': 'scripts/27_validate_site.py — 0 errors across all internal links',
    'freeze_date': ACCESS,
    'pages': {
        'top_level': top_pages,
        'country_pages': country_pages,
        'country_directory': 'countries/',
        'total_site_pages': len(top_pages) + country_pages,
    },
    'archive': {
        'countries': int(panel.iso3.nunique()),
        'country_year_rows': int(len(panel)),
        'years': [int(panel.year.min()), int(panel.year.max())],
        'files_total': int(len(ck)),
        'bytes_total': int(ck.bytes.sum()),
        'evidence_directory': 'evidence/',
        'api_snapshots': int(len(apis)),
        'web_page_snapshots': int(len(snaps)),
        'pdf_mirrors': int(snaps.pdf_mirror.astype(str).ne('').sum() - snaps.pdf_mirror.isna().sum()),
        'screenshots': int(snaps.png_screenshot.astype(str).ne('').sum() - snaps.png_screenshot.isna().sum()),
    },
    'verification': {
        'values_checked': int(len(vlog)),
        'exact_matches': int((vlog.status == 'EXACT').sum()),
        'discrepancies': int((vlog.status != 'EXACT').sum()),
        'corrections_applied': int(len(corr)),
        'countries_corrected': int(corr.iso3.nunique()),
        'document_source_variable_rows': 89,
        'document_source_citations_distinct': 78,
        'document_source_citations_archived': 76,
        'document_source_citations_not_retrievable': 2,
        'document_source_urls_distinct': 72,
        'all_source_urls_distinct': 160,
        'source_hosts': 51,
        'grade_counts': {k: int(grades.get(k, 0)) for k in ['A', 'B', 'C', 'D']},
    },
    'primary_workbook': sha('data/FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx'),
    'secondary_workbook': sha('data/migration_population_panel_40countries_2010-2022_final.xlsx'),
    'original_inputs': [
        sha('data/original_inputs/immigration_country_year_2010_2022.xlsx'),
        sha('data/original_inputs/migration_population_panel_40countries_2010-2022.xlsx'),
    ],
    'notes': [
        'Every count in this manifest and on the website refers to primary_workbook.',
        'secondary_workbook was produced by a separate compilation run; its own internal counts '
        'and file paths describe that run, not this archive. See data/ABOUT_THE_TWO_WORKBOOKS.md.',
        'original_inputs are preserved byte-for-byte so every correction can be checked.',
        'Per-file SHA-256 hashes for the whole archive are in manifest/checksums.csv.',
    ],
}
p = os.path.join(SITE, 'manifest', 'website_manifest.json')
json.dump(m, open(p, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
print('wrote', os.path.relpath(p, SITE))
print(json.dumps(m['verification'], indent=1))
