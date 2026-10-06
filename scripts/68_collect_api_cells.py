# -*- coding: utf-8 -*-
"""Turn the raw API payloads fetched by 67_fetch_extension_apis.py into dated, attributed
cells for the 2001-2009 extension (and for gaps inside 2010-2022 that the new payloads fill).

Rules, from the plan (migrant_data_availability_2001-2022.md, caveat 1):
  * A blank cell is filled from the SAME source family the country's published series
    already uses, where that source reaches the year (Eurostat extends Eurostat, OECD
    extends OECD). No break is introduced.
  * Only where that family does not reach, the other family fills it, and the cell is
    flagged as a splice together with the measured difference between the two families
    over the years they overlap. Eurostat and OECD differ by roughly 0.05-0.5% for most
    European countries; that is stated, not hidden.
  * No published value is ever changed. Only blank cells are filled.
  * The source's own observation flags (Eurostat b/e/p, OECD OBS_STATUS) are carried into
    the note, because a break flagged by the publisher is a break the user must know about.

Every payload spans 2001-2022, so the 2010-2022 part doubles as a re-verification of what
the archive already publishes; the result is written to extension_overlap_check.csv.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ext_lib as L                                    # noqa: E402

SITE = os.path.dirname(HERE)
D = os.path.join(SITE, 'data')
STAGE = os.path.join(D, 'extension_staging')
os.makedirs(STAGE, exist_ok=True)
COLLECTED = L.COLLECTED

P = L.baseline_panel()   # the panel as it stood before the extension
SNAP = pd.read_csv(os.path.join(D, 'api_snapshots.csv')).set_index('file')
ISO = sorted(P.iso3.unique())
VAR = {'fb': 'foreign_born', 'fn': 'foreign_nationals'}


def url_of(rel):
    return SNAP.loc[rel, 'query_url']


SRC = {
    ('fb', 'EUROSTAT'): dict(data=L.parse_eurostat(L.EUR_CTB), file=L.EUR_CTB,
                             name='Eurostat [migr_pop3ctb]',
                             note='stock at 1 Jan; c_birth=FOR (born in a foreign country)',
                             ref='1 January'),
    ('fn', 'EUROSTAT'): dict(data=L.parse_eurostat(L.EUR_CTZ), file=L.EUR_CTZ,
                             name='Eurostat [migr_pop1ctz]',
                             note='stock at 1 Jan; citizen=FOR_STLS (foreign citizens incl. stateless)',
                             ref='1 January'),
    ('fb', 'OECD'): dict(data=L.parse_oecd(L.OECD_B14), file=L.OECD_B14,
                         name='OECD International Migration Database (stocks of foreign-born '
                              'population, measure B14)', note='', ref=''),
    ('fn', 'OECD'): dict(data=L.parse_oecd(L.OECD_B15), file=L.OECD_B15,
                         name='OECD International Migration Database (stocks of foreign '
                              'population, measure B15)', note='', ref=''),
}
for k, v in SRC.items():
    v['url'] = url_of(v['file'])

LARGE_GAP = 5.0          # % mean difference between source families that counts as a level shift
EURO_FLAG = {'b': 'break in time series', 'e': 'estimated', 'p': 'provisional',
             'd': 'definition differs', 'u': 'low reliability', 'c': 'confidential'}


def r0(v):
    """The panel stores whole persons; OECD returns some values with decimals."""
    return int(np.floor(float(v) + 0.5))


def family_of(source):
    s = str(source)
    if 'migr_pop' in s:
        return 'EUROSTAT'
    if 'OECD' in s:
        return 'OECD'
    return 'OTHER'


def short(fam_name):
    return fam_name.split(' (')[0]


def flag_text(fam, flag):
    if not flag:
        return ''
    if fam == 'EUROSTAT':
        parts = [EURO_FLAG[c] for c in str(flag) if c in EURO_FLAG]
        return ('Eurostat flag: ' + ', '.join(parts)) if parts else ''
    return ''                                          # OECD OBS_STATUS A = normal value


def published(var):
    s = P[P[VAR[var]].notna()]
    return {(r.iso3, int(r.year)): r for r in s.itertuples()}


rows, alts, overlap = [], [], []
SPL = {}                      # (iso3, variable) -> splice summary
for var in ('fb', 'fn'):
    pv = VAR[var]
    pub = published(var)
    for iso in ISO:
        s = P[(P.iso3 == iso) & P[pv].notna()]
        home = {family_of(x) for x in s[pv + '_source']}
        prefs = [f for f in ('EUROSTAT', 'OECD') if f in home] + \
                [f for f in ('EUROSTAT', 'OECD') if f not in home]
        first_pub = min([yy for (c, yy) in pub if c == iso] or [2010])

        def gap_vs(chosen, h):
            """% difference of the chosen family from the home family, over published years."""
            xs = []
            for (c, y), (v_c, _) in SRC[(var, chosen)]['data'].items():
                if c != iso:
                    continue
                rec = pub.get((iso, y))
                if rec is not None and family_of(getattr(rec, pv + '_source')) == h:
                    base = getattr(rec, pv)
                    if base:
                        xs.append((v_c - base) / base * 100.0)
            return xs

        # re-verification of the published cells against today's payload
        for h in ('EUROSTAT', 'OECD'):
            same = diff = 0
            for (c, y), (v_h, _) in SRC[(var, h)]['data'].items():
                if c != iso:
                    continue
                rec = pub.get((iso, y))
                if rec is not None and family_of(getattr(rec, pv + '_source')) == h:
                    same += (getattr(rec, pv) == r0(v_h))
                    diff += (getattr(rec, pv) != r0(v_h))
            if same + diff:
                overlap.append(dict(variable=pv, source=SRC[(var, h)]['name'], iso3=iso,
                                    cells_compared=same + diff, identical=same, different=diff,
                                    retrieved=COLLECTED))

        for y in range(2001, 2023):
            if (iso, y) in pub:
                continue
            avail = {}
            for f in ('EUROSTAT', 'OECD'):
                v = SRC[(var, f)]['data'].get((iso, y))
                if v is not None:
                    avail[f] = v
            if not avail:
                continue
            chosen = next(f for f in prefs if f in avail)
            val, flag = avail[chosen]
            val = r0(val)
            src = SRC[(var, chosen)]
            spliced = (chosen not in home) and bool(home & {'EUROSTAT', 'OECD'})

            # reference date and country-specific caveats come from an existing cell of the
            # same family, so a caveat verified for a country carries into the new years
            ref, note = src['ref'], src['note']
            if chosen == 'OECD' and chosen in home:
                ex = s[s[pv + '_source'].map(family_of) == 'OECD']
                near = ex.iloc[(ex.year - y).abs().argsort().iloc[0]]
                ref, note = str(near[pv + '_ref_date']), str(near[pv + '_note'])
            elif chosen == 'OECD':
                ref = 'See note'
                note = ('OECD IMD stock. The reference date differs by country and is not '
                        'carried in the API response; consult the OECD IMD metadata for this '
                        'country.')

            extra = []
            ft = flag_text(chosen, flag)
            if ft:
                extra.append(ft)
            large = False
            if spliced:
                done = False
                for h in sorted(home & {'EUROSTAT', 'OECD'}):
                    gaps = gap_vs(chosen, h)
                    if gaps:
                        sp = SPL.setdefault((iso, pv), dict(
                            iso3=iso, variable=pv, extension_source=short(src['name']),
                            published_series_source=short(SRC[(var, h)]['name']),
                            overlap_years=len(gaps), mean_gap_pct=round(float(np.mean(gaps)), 3),
                            min_gap_pct=round(min(gaps), 3), max_gap_pct=round(max(gaps), 3),
                            years=[]))
                        sp['years'].append(y)
                        sp['family'] = chosen
                        large = abs(float(np.mean(gaps))) >= LARGE_GAP
                        extra.append(
                            'SPLICE: this country\'s published series from %d on uses %s; %s is '
                            'used here because %s does not reach %d. Over the %d years where '
                            'both exist, %s is %+.2f%% on average (range %+.2f%% to %+.2f%%) '
                            'relative to %s.'
                            % (first_pub, short(SRC[(var, h)]['name']), short(src['name']),
                               short(SRC[(var, h)]['name']), y, len(gaps), short(src['name']),
                               float(np.mean(gaps)), min(gaps), max(gaps),
                               short(SRC[(var, h)]['name'])))
                        if large:
                            extra[-1] = ('LARGE LEVEL GAP (%g%% or more): a step of this size at '
                                         'the join is a source effect, not a change in migration. '
                                         % LARGE_GAP) + extra[-1]
                        done = True
                        break
                if not done:
                    sp = SPL.setdefault((iso, pv), dict(
                        iso3=iso, variable=pv, extension_source=short(src['name']),
                        published_series_source='a different source family', overlap_years=0,
                        mean_gap_pct=None, min_gap_pct=None, max_gap_pct=None, years=[]))
                    sp['years'].append(y)
                    sp['family'] = chosen
                    extra.append('SPLICE: this country\'s published series uses a different '
                                 'source family and no overlap exists to measure the difference.')
            flagtxt = '; '.join(x for x in (('splice (large gap)' if large else
                                             'splice' if spliced else ''), ft) if x)
            rows.append(dict(
                iso3=iso, year=y, variable=pv, value=val, source_id=chosen + '_' + var,
                source_name=src['name'], source_url=src['url'],
                local_file='evidence/api/' + src['file'], ref_date=ref,
                grade='A', source_type='annual', flag=flagtxt,
                note=(note + (' ' if note else '') + ' '.join(extra)).strip(),
                verification='Read directly from the archived API response '
                             '(evidence/api/%s); retrieved %s.' % (src['file'], COLLECTED),
                collected_on=COLLECTED))

            for f, (v2, _) in avail.items():
                alts.append(dict(country=P[P.iso3 == iso].country.iloc[0], iso3=iso, year=y,
                                 variable=pv, source=SRC[(var, f)]['name'], value=r0(v2),
                                 used_in_panel='yes' if f == chosen else 'no',
                                 diff_vs_used_pct=round((r0(v2) - val) / val * 100, 3) if val else None))

# For every spliced series, also keep the extension family's values for the years where the
# published (other-family) series was retained, so that a consistent series from one source
# is available for 2001-2022 whenever the splice has a level gap.
for (iso, pv), v in SPL.items():
    var = 'fb' if pv == 'foreign_born' else 'fn'
    fam = v['family']
    used = {(r['iso3'], r['year'], r['variable']): r['value'] for r in rows}
    pub = published(var)
    for (c, y), (val2, _) in SRC[(var, fam)]['data'].items():
        if c != iso or (iso, y) not in pub:
            continue
        base_v = getattr(pub[(iso, y)], pv)
        alts.append(dict(country=P[P.iso3 == iso].country.iloc[0], iso3=iso, year=y,
                         variable=pv, source=SRC[(var, fam)]['name'], value=r0(val2),
                         used_in_panel='no (published series kept)',
                         diff_vs_used_pct=round((r0(val2) - base_v) / base_v * 100, 3)
                         if base_v else None))
sp_rows = []
for v in SPL.values():
    ys = sorted(v.pop('years'))
    v.pop('family', None)
    v.update(first_year_extended=ys[0], last_year_extended=ys[-1], cells=len(ys))
    sp_rows.append(v)
pd.DataFrame(sp_rows).sort_values(['variable', 'iso3']).to_csv(
    os.path.join(D, 'extension_splice_summary.csv'), index=False, encoding='utf-8-sig')
pd.DataFrame(rows).to_csv(os.path.join(STAGE, 'api_migrant_cells.csv'), index=False,
                          encoding='utf-8-sig')
pd.DataFrame(alts).sort_values(['iso3', 'variable', 'year', 'used_in_panel'],
                               ascending=[True, True, True, False]).to_csv(
    os.path.join(STAGE, 'api_alternatives.csv'), index=False, encoding='utf-8-sig')
ov = pd.DataFrame(overlap)
ov.to_csv(os.path.join(D, 'extension_overlap_check.csv'), index=False, encoding='utf-8-sig')

cells = pd.DataFrame(rows)
print('migrant-stock cells from Eurostat/OECD: %d' % len(cells))
print(cells.groupby(['variable', 'source_id']).size().to_string())
print('\nof which splices: %d | cells in 2001-2009: %d | cells inside 2010-2022: %d'
      % ((cells.flag.str.contains('splice')).sum(), (cells.year <= 2009).sum(),
         (cells.year >= 2010).sum()))
print('\nRe-verification of PUBLISHED cells against today\'s payloads:')
print(ov.groupby('source')[['cells_compared', 'identical', 'different']].sum().to_string())
