# -*- coding: utf-8 -*-
"""Archive the ISSP 2021 documentation that data/ANALYSIS_NOTES.md quotes (issue #24, 2026-10-18).

The authors fixed the construct and the timing rule from the survey item itself. The wording quoted in the notes comes
from two GESIS documents, archived here with an image of every page quoted:

  ISSP 2021 - Health and Health Care II, ZA8000 Variable Report (GESIS, documentation release 2024/08/30,
  doi:10.4232/5.ZA8000.2.0.0): v8 = Q6a (PDF page 51), v13 = Q7d (61), DATEYR and DATEMO by country (778, 779).
  ISSP 2021 Taiwan questionnaire (GESIS ZA8000 country documentation): D2a = ISSP 6a (PDF page 6), C3d = ISSP 7d (5).

GESIS's site refuses automated downloads (HTTP 403 from its web firewall on 2026-10-18), so the files are the
authors' copies of the GESIS documents, copied byte for byte; their SHA-256 is recorded in the README written here.
Only documentation is archived: the ISSP data files are licensed by GESIS and are not part of this archive.

Usage: python scripts/89_archive_survey_documents.py <folder holding ZA8000_cdb.pdf and ZA8000_q_tw.pdf>
"""
import hashlib
import os
import shutil
import sys

import fitz

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(SITE, 'evidence', 'survey')
WHEN = '2026-10-18'
DOCS = [
    ('ZA8000_cdb.pdf', 'ISSP2021_ZA8000_variable_report_v2.0.0.pdf',
     'ISSP 2021 - Health and Health Care II, ZA8000 Variable Report, GESIS documentation release 2024/08/30 '
     '(doi:10.4232/5.ZA8000.2.0.0)',
     [(51, 'v8 - Q6a: access to publicly funded health care even if no citizenship of [country]'),
      (61, 'v13 - Q7d: access to health care easier or harder for citizens than for non-citizens'),
      (778, 'DATEYR - year of interview, by country'),
      (779, 'DATEMO - month of interview')]),
    ('ZA8000_q_tw.pdf', 'ISSP2021_ZA8000_questionnaire_Taiwan.pdf',
     'ISSP 2021 - Health and Health Care II, Taiwan questionnaire (GESIS ZA8000 country documentation)',
     [(5, 'C3d - ISSP 7d: 公民相較於非公民'),
      (6, 'D2a - ISSP 6a: 住在台灣的每個人，就算沒有台灣的身分證，都應該可以使用公共醫療保健服務')]),
]
if len(sys.argv) != 2:
    sys.exit(__doc__)
src_dir = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
lines = ['# ISSP 2021 documentation quoted in the analysis notes', '',
         'Archived %s for issue #24: the authors fixed the construct and the timing rule from the survey item itself '
         '(`data/ANALYSIS_NOTES.md`, sections 1 and 2). GESIS refuses automated downloads (HTTP 403 from its web '
         'firewall on %s), so the PDFs are the authors\' copies of the GESIS documents, copied byte for byte. Only '
         'documentation is held here: the ISSP data files are licensed by GESIS and are not part of this archive.'
         % (WHEN, WHEN), '', '| File | Document | SHA-256 |', '|---|---|---|']
pages = ['', '## Pages quoted', '', '| Image | Page (PDF) | What it shows |', '|---|---:|---|']
for src, dst, title, quoted in DOCS:
    p_src, p_dst = os.path.join(src_dir, src), os.path.join(OUT, dst)
    shutil.copyfile(p_src, p_dst)
    digest = hashlib.sha256(open(p_dst, 'rb').read()).hexdigest()
    assert digest == hashlib.sha256(open(p_src, 'rb').read()).hexdigest()
    lines.append('| `%s` | %s | `%s` |' % (dst, title, digest))
    doc = fitz.open(p_dst)
    for pg, what in quoted:
        png = 'MIRROR__%s_p%d.png' % (os.path.splitext(dst)[0], pg)
        doc[pg - 1].get_pixmap(dpi=110).save(os.path.join(OUT, png))
        pages.append('| `%s` | %d | %s |' % (png, pg, what))
    doc.close()
    print('%-48s %s  pages %s' % (dst, digest[:16], [p for p, _ in quoted]))
open(os.path.join(OUT, 'README.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines + pages) + '\n')
print('evidence/survey/README.md written')
