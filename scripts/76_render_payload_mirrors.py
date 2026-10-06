# -*- coding: utf-8 -*-
"""A readable mirror for each raw API payload fetched for the extension: a country x year grid
of the values read from it (the generic previewer truncates JSON at 14,000 characters, which
would show structure and never the numbers behind a cell). Written as MIRROR__<stem>.pdf/.png
beside the payload, which is where the site looks for mirrors, and build_source_mirrors.py
leaves existing mirrors alone."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ext_lib as L                                    # noqa: E402

SITE = os.path.dirname(HERE)
API = os.path.join(SITE, 'evidence', 'api')
ISO3 = ('AUS AUT BEL BGR CHE CHL CHN CZE DEU DNK ESP FIN FRA GBR HRV HUN IND ISL ISR ITA '
        'JPN KOR LTU MEX NLD NOR NZL PHL POL PRT RUS SUR SVK SVN SWE THA TUR TWN USA ZAF').split()
YEARS = list(range(2001, 2023))

JOBS = [
    (L.OECD_B14, L.parse_oecd, 'OECD IMD B14 - stocks of foreign-born population',
     'Query: SDMX data/OECD.ELS.IMD,DSD_MIG_F@DF_MIG_POPF,1.0, measure B14, all 40 panel countries'),
    (L.OECD_B15, L.parse_oecd, 'OECD IMD B15 - stocks of foreign population',
     'Query: SDMX data/OECD.ELS.IMD,DSD_MIG@DF_MIG,1.0, measure B15, all 40 panel countries'),
    (L.EUR_CTB, L.parse_eurostat, 'Eurostat migr_pop3ctb - population born in a foreign country',
     'Query: migr_pop3ctb, c_birth=FOR, age=TOTAL, sex=T, unit=NR, 1 January, 2001-2022'),
    (L.EUR_CTZ, L.parse_eurostat, 'Eurostat migr_pop1ctz - foreign citizens incl. stateless',
     'Query: migr_pop1ctz, citizen=FOR_STLS, age=TOTAL, sex=T, unit=NR, 1 January, 2001-2022'),
    (L.WB_POP, L.parse_worldbank, 'World Bank WDI SP.POP.TOTL - total population',
     'Query: api.worldbank.org country/all/indicator/SP.POP.TOTL, 2001-2022'),
    (L.WB_MIG, L.parse_worldbank, 'World Bank WDI SM.POP.TOTL - international migrant stock '
     '(mirror of UN DESA)', 'Query: api.worldbank.org country/all/indicator/SM.POP.TOTL, 2001-2022'),
]
for rel, parser, title, query in JOBS:
    data = parser(rel)
    grid = {}
    for (iso, y), (v, _) in data.items():
        if iso in ISO3 and y in YEARS:
            grid.setdefault(iso, {})[y] = v
    stem = os.path.splitext(os.path.basename(rel))[0]
    stem = 'MIRROR__' + re.sub(r'[^A-Za-z0-9._-]+', '_', stem)[:70]
    base = os.path.join(API, os.path.dirname(rel).replace('/', os.sep), stem)
    made = L.grid_mirror(title, '%s. Retrieved %s. %d countries with at least one value.'
                         % (query, L.COLLECTED, len(grid)), grid, YEARS, base)
    print('%-58s %2d countries  mirrors: %s' % (os.path.basename(rel)[:58], len(grid),
                                                [os.path.basename(m)[-4:] for m in made]))
