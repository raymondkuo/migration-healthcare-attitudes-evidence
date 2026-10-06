# -*- coding: utf-8 -*-
"""Bilingual build: the per-country, per-variable evidence pages in each language."""
import os, sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blib import (SITE, EV, D, ACCESS, revised_note, panel, vlog, reg, corr, snaps, apis, pubs,
                  artifacts as blib_artifacts,
                  ALLVARS, E, num, pill, filelink, page, table, cname, vlab, fname, t,
                  reason_zh)
import i18n_content as C

CHK = {'irregular_proxy_detections': 'irregular_detections'}
snap_by = {}
for _, s in snaps.iterrows():
    snap_by.setdefault((s['iso3'], s['source_url']), []).append(s)
reg_by = {}
for _, r in reg.iterrows():
    reg_by.setdefault((r['iso3'], str(r['source_url'])), []).append(r)
pub_by_key = {r['key']: r for _, r in pubs.iterrows()}

RAWFILE = {
 'worldbank_SP_POP_TOTL': 'evidence/api/wb_SP_POP_TOTL.json',
 'worldbank_SM_POP_TOTL': 'evidence/api/wb_SM_POP_TOTL.json',
 'eurostat_migr_pop3ctb': 'evidence/api/eurostat_migr_pop3ctb.json',
 'eurostat_migr_pop1ctz': 'evidence/api/eurostat_migr_pop1ctz.json',
 'eurostat_migr_eipre': 'evidence/api/eurostat_migr_eipre.json',
 'un_wpp_2024': 'evidence/api/UN_WPP2024_demographic_indicators_compact.xlsx',
 'un_desa_international_migrant_stock_2024':
     'evidence/api/UN_DESA_IMS2024_stock_by_sex_and_destination.xlsx',
}


def publisher_for(u):
    u = str(u)
    if 'api.worldbank.org' in u and 'SP.POP.TOTL' in u:
        return 'worldbank_SP_POP_TOTL'
    if 'api.worldbank.org' in u and 'SM.POP.TOTL' in u:
        return 'worldbank_SM_POP_TOTL'
    for k in ('migr_pop3ctb', 'migr_pop1ctz', 'migr_eipre'):
        if k in u:
            return 'eurostat_' + k
    if 'sdmx.oecd.org' in u:
        return 'oecd_international_migration_database'
    if 'population.un.org' in u:
        return 'un_wpp_2024'
    if 'un.org/development/desa' in u:
        return 'un_desa_international_migrant_stock_2024'
    return None


def build(iso3, en_name, v, lang):
    cn = cname(en_name, lang)
    g = panel[panel.iso3 == iso3].sort_values('year')
    sub = g[g[v].notna()]
    scol, ucol = v + '_source', v + '_url'
    urls = sorted({str(u) for u in sub[ucol].dropna()}) if ucol in sub else []

    # Files are collected per source URL, not into one undifferentiated basket, so each
    # archived file can be shown against the years it is actually evidence for.
    arts, seen = [], set()
    groups, _cur = [], None

    def add(label, rel):
        if not rel:
            return
        if not os.path.isfile(os.path.join(SITE, rel.replace('/', os.sep))):
            return
        if rel not in seen:
            seen.add(rel)
            arts.append((label, rel))
        # recorded against every URL group it belongs to, so a file that supports more than one
        # group of years (an old and a new payload of the same series) shows all of them
        if _cur is not None and (label, rel) not in _cur:
            _cur.append((label, rel))

    for u in urls:
        _cur = []
        groups.append((u, _cur))
        # the shared resolver covers archived originals, rendered mirrors, raw payloads,
        # publisher-page mirrors and page snapshots
        _regrows = reg_by.get((iso3, u), [])
        _lfs = [r0.get('local_file') for r0 in _regrows] or [None]
        for _lf in _lfs:
            for lab, rel in blib_artifacts(iso3, u, _lf, lang):
                add(lab, rel)
        k = publisher_for(u)
        if k:
            pr = pub_by_key.get(k)
            if pr is not None:
                if isinstance(pr['pdf'], str) and pr['pdf']:
                    add(t('art_pubpdf', lang), pr['pdf'])
                if isinstance(pr['png'], str) and pr['png']:
                    add(t('art_pubpng', lang), pr['png'])
            if k in RAWFILE:
                add(t('art_raw', lang), RAWFILE[k])
            if k == 'oecd_international_migration_database':
                add(t('art_oecdxml', lang), 'evidence/api/oecd/DSD_MIG_dataflow_metadata.xml')
                for _, a in apis[apis.path.str.contains('oecd/%s_' % iso3, na=False)].iterrows():
                    add(t('art_sdmx', lang) % os.path.basename(a['path']), a['path'])
        for r in reg_by.get((iso3, u), []):
            lf = str(r.get('local_file') or '')
            if lf and lf != 'nan':
                ext = os.path.splitext(lf)[1].lstrip('.').upper() or 'file'
                host = u.split('/')[2] if '://' in u else ''
                add(t('art_doc', lang) % (host, ext), 'evidence/countries/%s/%s' % (iso3, lf))
        for s in snap_by.get((iso3, u), []):
            if isinstance(s['pdf_mirror'], str) and s['pdf_mirror']:
                add(t('art_pdfmirror', lang), 'evidence/countries/%s/%s' % (iso3, s['pdf_mirror']))
            if isinstance(s['png_screenshot'], str) and s['png_screenshot']:
                add(t('art_screenshot', lang), 'evidence/countries/%s/%s' % (iso3, s['png_screenshot']))

    cv = vlog[(vlog.iso3 == iso3) & (vlog.variable == CHK.get(v, v))]
    chk = {int(r['year']): r for _, r in cv.iterrows()}
    cc = corr[(corr.iso3 == iso3) & (corr.variable == v)]
    corrected = {int(r['year']) for _, r in cc.iterrows()}
    VT = {'en': C.P and None, 'zh': None}
    from i18n import VERTAG
    vt = VERTAG[lang]

    # source type and comparability flags exist for the two migrant-stock variables
    has_flags = (v + '_flag') in sub.columns and sub[v + '_flag'].fillna('').astype(str).str.strip().ne('').any()
    TYPE_ZH = {'annual': '逐年', 'census': '普查', 'survey': '調查', 'un_estimate': 'UN 估計值',
               'other': '其他'}
    FLAG_ZH = {'splice (large gap)': '接續（差距大）', 'splice': '接續', 'un_estimate': 'UN 估計值',
               'declared citizenship basis': '宣告為公民身分基礎',
               'comparability caution': '可比性提醒', 'includes former-USSR births': '含前蘇聯出生者',
               'derived by subtraction': '以相減推得',
               'Eurostat flag: break in time series': 'Eurostat 旗標：時間序列斷裂',
               'Eurostat flag: estimated': 'Eurostat 旗標：估計值',
               'Eurostat flag: provisional': 'Eurostat 旗標：暫定值',
               'Eurostat flag: estimated, provisional': 'Eurostat 旗標：估計值、暫定值'}

    def flag_html(r):
        f = str(r.get(v + '_flag') or '').strip()
        if not f or f == 'nan':
            return '<span style="color:var(--faint)">&mdash;</span>'
        parts = [x.strip() for x in f.split(';') if x.strip()]
        if lang == 'zh':
            parts = [FLAG_ZH.get(x, x) for x in parts]
        big = 'large gap' in f
        return ('<span class="tag %s">%s</span>' % ('bad' if big else 'warn', E('；'.join(parts)
                                                                                  if lang == 'zh' else '; '.join(parts))))

    rows = []
    for _, r in sub.iterrows():
        y = int(r['year'])
        c = chk.get(y)
        vtext = str(r.get(v + '_verification') or '')
        if y in corrected:
            ver = '<span class="tag ok">%s</span>' % vt['corrected']
        elif c is not None and c['status'] == 'EXACT':
            ver = '<span class="tag ok">%s</span>' % vt['exact']
        elif vtext.startswith('Read directly from the archived'):
            ver = '<span class="tag ok">%s</span>' % vt['api']
        elif vtext not in ('', 'nan'):
            ver = '<span class="tag ok">%s</span>' % vt['doc']
        else:
            ver = '<span class="tag">%s</span>' % vt['nomach']
        src = str(r.get(scol) or '')
        stype = str(r.get(v + '_source_type') or '') if (v + '_source_type') in r else ''
        stype = '' if stype == 'nan' else stype
        srccell = E(src[:110]) + ('<br><span style="color:var(--muted);font-size:11.5px">%s</span>'
                                  % E(TYPE_ZH.get(stype, stype) if lang == 'zh' else stype)
                                  if stype else '')
        ref = str(r.get(v + '_ref_date') or '') if (v + '_ref_date') in r else ''
        rows.append('<tr id="y%d"><td class="num">%d</td><td class="num"><strong>%s</strong></td>'
                    '<td>%s</td><td>%s</td><td class="wrap-any">%s</td><td>%s</td>%s</tr>'
                    % (y, y, num(r[v]), pill(r.get(v + '_grade', '')), ver, srccell, E(ref),
                       ('<td class="wrap-any">%s</td>' % flag_html(r)) if has_flags else ''))

    def yrs_label(ys):
        ys = sorted(set(ys))
        out, i = [], 0
        while i < len(ys):
            j = i
            while j + 1 < len(ys) and ys[j + 1] == ys[j] + 1:
                j += 1
            out.append(str(ys[i]) if i == j else '%d&ndash;%d' % (ys[i], ys[j]))
            i = j + 1
        return ', '.join(out)

    def grouped_notes(col):
        """Distinct texts of a column with the years each applies to, in order of first year."""
        found = {}
        for _, r in sub.iterrows():
            x = r.get(col)
            if isinstance(x, str) and x.strip() and x.strip() != 'nan':
                found.setdefault(x.strip(), []).append(int(r['year']))
        return sorted(found.items(), key=lambda kv: kv[1][0])

    def note_boxes(col, label):
        gs = grouped_notes(col)
        return ''.join('  <div class="note">%s%s%s</div>\n'
                       % (label, ('<strong>%s</strong>: ' % yrs_label(ys)) if len(gs) > 1 else '',
                          E(text)) for text, ys in gs)

    derived = next((x for x in (sub[v + '_derived'] if (v + '_derived') in sub else [])
                    if isinstance(x, str) and x.strip() == 'yes'), '')
    drange = next((x for x in (sub[v + '_published_range'] if (v + '_published_range') in sub else [])
                   if isinstance(x, str) and x.strip()), '')
    dhow = next((x for x in (sub[v + '_derivation'] if (v + '_derivation') in sub else [])
                 if isinstance(x, str) and x.strip()), '')
    note = next((x for x in (sub[v + '_note'] if (v + '_note') in sub else [])
                 if isinstance(x, str) and x.strip()), '')
    vnote = next((x for x in (sub[v + '_verification'] if (v + '_verification') in sub else [])
                  if isinstance(x, str) and x.strip()), '')

    corrhtml = ''
    if len(cc):
        c2 = cc.copy()
        if lang == 'zh':
            c2['reason'] = c2['reason'].map(reason_zh)
        rr = ''.join('<tr><td class="num">%d</td><td class="num">%s</td><td class="num">%s</td>'
                     '<td>%s</td></tr>' % (int(x['year']), num(x['old_value']),
                                           num(x['new_value']), E(x['reason']))
                     for _, x in c2.iterrows())
        corrhtml = ('<h2>' + t('corr_h', lang) + '</h2><div class="tablewrap"><table><thead><tr>'
                    '<th class="num">' + t('year', lang) + '</th><th class="num">'
                    + t('col_was', lang) + '</th><th class="num">' + t('col_now', lang)
                    + '</th><th>' + t('col_why', lang) + '</th></tr></thead><tbody>'
                    + rr + '</tbody></table></div>')

    pdfrel = 'evidence/extracts/%s/%s.pdf' % (iso3, v)

    # ---- one table row per archived file, against the years it is evidence for ----
    yv = {int(r['year']): r[v] for _, r in sub.iterrows()}
    url_years = {}
    for _, r in sub.iterrows():
        url_years.setdefault(str(r.get(ucol) or ''), []).append(int(r['year']))

    def supports(years):
        if not years:
            return '<span style="color:var(--faint)">&mdash;</span>'
        return ' &middot; '.join('%d&nbsp;<strong>%s</strong>' % (y, num(yv[y]))
                                 for y in sorted(years))

    def srcname(u):
        for r0 in reg_by.get((iso3, u), []):
            s0 = str(r0.get('source_name') or '')
            if s0 and s0 != 'nan':
                return s0
        for _, r0 in sub.iterrows():
            if str(r0.get(ucol) or '') == u:
                s0 = str(r0.get(scol) or '')
                if s0 and s0 != 'nan':
                    return s0
        return u.split('/')[2] if '://' in u else u

    arows = ['<tr><td class="wrap-any">%s</td><td>%s</td><td class="wrap-any">%s</td>'
             '<td class="wrap-any">%s</td></tr>'
             % (filelink('../' + pdfrel, os.path.basename(pdfrel)), t('ev_pdf', lang),
                E(cn) + ' &mdash; ' + E(vlab(v, lang)),
                '<span style="color:var(--muted)">%s</span>' % t('ev_arch_all', lang))]
    # one row per file: the union of the years of every source group it is evidence for
    finfo, forder = {}, []
    for u, files in groups:
        for lab, rel in files:
            d = finfo.setdefault(rel, dict(lab=lab, years=set(), src=[]))
            d['years'].update(url_years.get(u, []))
            nm = srcname(u)[:110]
            if nm not in d['src']:
                d['src'].append(nm)
            if rel not in forder:
                forder.append(rel)
    for rel in forder:
        d = finfo[rel]
        arows.append('<tr><td class="wrap-any">%s</td><td>%s</td><td class="wrap-any">%s</td>'
                     '<td class="wrap-any">%s</td></tr>'
                     % (filelink('../' + rel, os.path.basename(rel)), E(d['lab']),
                        E(' / '.join(d['src'])[:150]), supports(sorted(d['years']))))
    arttable = ('<div class="tablewrap"><table><thead><tr><th>' + t('ev_arch_file', lang)
                + '</th><th>' + t('ev_arch_kind', lang) + '</th><th>' + t('col_source', lang)
                + '</th><th>' + t('ev_arch_for', lang) + '</th></tr></thead><tbody>'
                + ''.join(arows) + '</tbody></table></div>')

    body = (
     '<div class="hero"><div class="wrap">\n'
     '  <p class="eyebrow">' + iso3 + t('ev_eyebrow', lang) + '</p>\n'
     '  <h1>' + E(cn) + ' &mdash; ' + E(vlab(v, lang)) + '</h1>\n'
     '  <p class="lede">' + t('ev_lede', lang) + ACCESS
     + {'en': '.', 'zh': '。'}[lang] + revised_note(iso3, lang, up='../')
     + '</p>\n</div></div>\n\n'
     '<section><div class="wrap">\n  <h2>' + t('ev_values', lang) + '</h2>\n'
     '  <div class="tablewrap"><table><thead><tr><th class="num">' + t('year', lang)
     + '</th><th class="num">' + t('col_value', lang) + '</th><th>' + t('grade_col', lang)
     + '</th><th>' + t('col_verif', lang) + '</th><th>' + t('col_source', lang)
     + '</th><th>' + t('col_refdate', lang) + '</th>'
     + ('<th>' + t('col_flag', lang) + '</th>' if has_flags else '') + '</tr></thead><tbody>'
     + ''.join(rows) + '</tbody></table></div>\n'
     + ('  <div class="note warn"><strong>' + t('derived_h', lang) + ' <abbr class="der">'
        + t('derived_mark', lang) + '</abbr></strong><br>' + t('derivation_label', lang) + '：'
        + E(dhow) + (('<br>' + t('derived_range_label', lang) + '：<strong>' + E(drange)
                      + '</strong>') if drange else '') + '</div>\n' if derived else '')
     + note_boxes(v + '_note', t('ev_defnote', lang))
     + note_boxes(v + '_verification', t('ev_confirm', lang))
     + '</div></section>\n\n'
     '<section><div class="wrap">\n  <h2>' + t('ev_src_h', lang) + '</h2>\n'
     '  <p class="sub">' + t('ev_src_sub', lang) + '</p>\n  <ul class="clean">'
     + ''.join('<li><a href="%s" rel="nofollow noopener" style="word-break:break-all">%s</a></li>'
               % (E(u), E(u)) for u in urls) + '</ul>\n</div></section>\n\n'
     + ('<section><div class="wrap">' + corrhtml + '</div></section>\n\n' if corrhtml else '')
     + '<section><div class="wrap">\n  <h2>' + t('ev_arch_h', lang) + '</h2>\n'
     '  <p class="sub">' + t('ev_arch_sub', lang) + '</p>\n  ' + arttable + '\n'
     '  <p style="margin-top:10px">'
     + filelink('../evidence/countries/%s/data_from_source.csv' % iso3, t('ev_country_csv', lang))
     + filelink('../evidence/countries/%s/value_check.csv' % iso3, t('ev_check_csv', lang))
     + '</p>\n</div></section>\n\n'
     '<section><div class="wrap">\n  <p><a href="../countries/'
     + os.path.basename(fname('countries/' + iso3, lang)) + '">'
     + t('back_to', lang) + E(cn) + '</a></p>\n</div></section>\n')

    page('evidence-pages/%s__%s' % (iso3, v),
         '%s — %s — %s' % (cn, vlab(v, lang), {'en': 'evidence', 'zh': '佐證'}[lang]),
         body, lang, up='../',
         desc={'en': 'Every value, source and archived file for %s %s, 2001-2022.' % (cn, vlab(v, lang)),
               'zh': '%s %s 2001–2022 年之全部數值、來源與存檔檔案。' % (cn, vlab(v, lang))}[lang])


if __name__ == '__main__':
    n = 0
    cinfo = panel.groupby(['iso3', 'country']).size().reset_index()[['iso3', 'country']]
    for lang in ['en', 'zh']:
        c = 0
        for _, ci in cinfo.iterrows():
            g = panel[panel.iso3 == ci['iso3']]
            for v in ALLVARS:
                if v in g and g[v].notna().sum() > 0:
                    build(ci['iso3'], ci['country'], v, lang)
                    c += 1
        print('%s: %d evidence pages' % (lang, c))
        n += c
    print('total %d' % n)
