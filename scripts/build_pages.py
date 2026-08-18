# -*- coding: utf-8 -*-
"""Bilingual build: Sources, Data files, Verification and Methods pages."""
import os, sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blib import (SITE, D, ACCESS, panel, qual, corr, issues, vlog, reg, codeb, apis,
                  snaps, irrall, pubs, VARS, E, num, pill, filelink, page, table,
                  vlab, fname, t, GRADE_DESC, COMPARABILITY, reason_zh, artifact_links)
import i18n_content as C
from i18n import GRADE_SHORT

S, DT, V, M = C.P['sources'], C.P['data'], C.P['verification'], C.P['methods']

# every archived source file has a rendered visual companion; index them by folder+file
MIRROR = {}
_mp = os.path.join(D, 'source_mirrors.csv')
if os.path.exists(_mp):
    for _, _r in pd.read_csv(_mp).iterrows():
        ms = [x for x in str(_r.get('mirrors') or '').split(';') if x]
        if ms:
            MIRROR[(str(_r['folder']), str(_r['source_file']))] = ms


def mirror_links(folder, filename, lang):
    """Download links for the rendered mirrors of one archived file."""
    out = ''
    for m in MIRROR.get((folder, filename), []):
        lab = ('PDF mirror' if m.lower().endswith('.pdf') else 'screenshot') if lang == 'en'             else ('PDF 鏡像' if m.lower().endswith('.pdf') else '截圖')
        out += filelink(folder + '/' + m, lab)
    return out

snap_by = {}
for _, s in snaps.iterrows():
    snap_by.setdefault((s['iso3'], s['source_url']), []).append(s)


def L(d, lang, *a):
    x = d[lang]
    return (x % a) if a else x


# ==============================================================  SOURCES
def build_sources(lang):
    api_rows = ''.join(
        '<tr><td>%s</td><td class="wrap-any">%s</td><td class="wrap-any">'
        '<a href="%s" rel="nofollow noopener" style="font-size:11.5px;word-break:break-all;'
        'color:var(--muted)">%s</a></td><td class="num">%s</td><td>%s</td></tr>'
        % (E(a['publisher']), E(a['description']), E(a['query_url']),
           E(str(a['query_url'])[:95]), num(a['bytes']),
           filelink(a['path'], os.path.basename(str(a['path'])))
           + mirror_links(os.path.dirname(str(a['path'])), os.path.basename(str(a['path'])), lang))
        for _, a in apis.iterrows())
    api_table = ('<div class="tablewrap"><table><thead><tr><th>' + L(S['col_publisher'], lang)
                 + '</th><th>' + L(S['col_dataset'], lang) + '</th><th>' + L(S['col_query'], lang)
                 + '</th><th class="num">' + L(S['col_bytes'], lang) + '</th><th>'
                 + L(S['col_rawsnap'], lang) + '</th></tr></thead><tbody>'
                 + api_rows + '</tbody></table></div>')

    prows = []
    for _, r in pubs.iterrows():
        links = ''
        if isinstance(r['pdf'], str) and r['pdf']:
            links += filelink(r['pdf'], {'en': 'PDF mirror', 'zh': 'PDF 鏡像'}[lang])
        if isinstance(r['png'], str) and r['png']:
            links += filelink(r['png'], {'en': 'screenshot', 'zh': '截圖'}[lang])
        note = str(r.get('note') or '')
        extra = ('<br><span style="color:var(--muted);font-size:11.5px">%s</span>' % E(note[:230])) \
            if note and note != 'nan' else ''
        prows.append('<tr><td>%s</td><td class="wrap-any">%s%s</td><td class="wrap-any">'
                     '<a href="%s" rel="nofollow noopener" style="font-size:11.5px;'
                     'word-break:break-all;color:var(--muted)">%s</a></td><td>%s</td></tr>'
                     % (E(r['publisher']), E(r['dataset']), extra, E(r['page_url']),
                        E(str(r['page_url'])[:95]),
                        links or '<span class="tag bad">%s</span>' % L(S['tag_notcap'], lang)))
    pub_table = ('<div class="tablewrap"><table><thead><tr><th>' + L(S['col_publisher'], lang)
                 + '</th><th>' + L(S['col_datasetpage'], lang) + '</th><th>' + L(S['col_url'], lang)
                 + '</th><th>' + L(S['col_mirror'], lang) + '</th></tr></thead><tbody>'
                 + ''.join(prows) + '</tbody></table></div>')

    nonapi = reg[reg.retrieval != 'VERIFIED_API']
    docs = nonapi.drop_duplicates(subset=['iso3', 'source_url'])
    TAG = {'DOWNLOADED': ('ok', 'tag_archived'), 'RECOVERED': ('ok', 'tag_recovered'),
           'RECOVERED_SCREENSHOT': ('ok', 'tag_screenshot'),
           'SUBSTITUTED': ('warn', 'tag_substituted'),
           'SUPERSEDED_CITATION': ('warn', 'tag_superseded'),
           'NOT_RETRIEVED': ('bad', 'tag_notret'),
           'NOT_RETRIEVED_REDUNDANT': ('bad', 'tag_notret')}
    drows = []
    for _, r in docs.sort_values(['iso3', 'variable']).iterrows():
        iso, url = r['iso3'], str(r['source_url'])
        links = [artifact_links(iso, url, r.get('local_file'), lang)]
        cls, key = TAG.get(str(r.get('outcome', '')), ('', 'tag_archived'))
        status = '<span class="tag %s">%s</span>' % (cls, L(S[key], lang))

        # the source column names what the value is verified against; anything the archive
        # stopped relying on is named here instead, so the citation is not simply lost
        note = str(r.get('note') or '')
        bits = []
        if note and note != 'nan':
            bits.append(E(note))
        def _s(v):
            v = str(v or '').strip()
            return '' if v == 'nan' else v
        old_n, old_u = _s(r.get('superseded_source_name')), _s(r.get('superseded_source_url'))
        if old_u:
            bits.append('<span style="color:var(--muted)">%s</span><br>%s<br>'
                        '<a href="%s" rel="nofollow noopener" style="word-break:break-all;'
                        'color:var(--faint)">%s</a>'
                        % (t('replaced', lang), E(str(old_n)[:130]), E(old_u), E(old_u[:88])))
        cell_note = ('<span style="font-size:11.5px">' + '<br><br>'.join(bits) + '</span>'
                     if bits else '<span style="color:var(--faint)">&mdash;</span>')

        drows.append('<tr data-t="%s"><td><a href="countries/%s">%s</a></td><td>%s</td>'
                     '<td class="wrap-any">%s<br><a href="%s" rel="nofollow noopener" '
                     'style="font-size:11.5px;word-break:break-all;color:var(--muted)">%s</a></td>'
                     '<td class="wrap-any">%s</td><td class="wrap-any">%s</td><td>%s</td></tr>'
                     % (E((str(iso) + ' ' + str(r['source_name']) + ' ' + url + ' '
                           + old_n + ' ' + old_u).strip().lower()),
                        os.path.basename(fname('countries/' + iso, lang)), iso,
                        E(vlab(r['variable'], lang)), E(str(r['source_name'])[:130]),
                        E(url), E(url[:95]), status, cell_note,
                        ''.join(links) or '<span style="color:var(--faint)">&mdash;</span>'))
    n_arch = int((~docs.outcome.astype(str).str.startswith('NOT_RETRIEVED')).sum())
    n_superseded = int((docs.get('superseded_source_url', pd.Series(dtype=str))
                        .astype(str).str.startswith('http')).sum())
    n_urls = int(nonapi.source_url.nunique())

    body = (
     '<div class="hero"><div class="wrap">\n  <p class="eyebrow">' + L(S['eyebrow'], lang)
     + '</p>\n  <h1>' + L(S['h1'], lang) + '</h1>\n  <p class="lede">' + L(S['lede'], lang)
     + ACCESS + '.</p>\n</div></div>\n\n'
     '<section><div class="wrap">\n  <h2>' + L(S['api_h'], lang) + '</h2>\n  <p class="sub">'
     + (L(S['api_sub'], lang) % (len(apis), format(int((vlog.status == 'EXACT').sum()), ','),
                                 format(len(vlog), ',')))
     + '</p>\n  ' + api_table + '\n  <p style="margin-top:12px">'
     + filelink('data/api_snapshots.csv', 'api_snapshots.csv') + '</p>\n</div></section>\n\n'
     '<section><div class="wrap">\n  <h2>' + L(S['pub_h'], lang) + '</h2>\n  <p class="sub">'
     + L(S['pub_sub'], lang).replace('ACCESS', ACCESS) + '</p>\n  ' + pub_table
     + '\n  <p style="margin-top:12px">'
     + filelink('data/api_publisher_snapshots.csv', 'api_publisher_snapshots.csv')
     + '</p>\n</div></section>\n\n'
     '<section><div class="wrap">\n  <h2>' + L(S['ev_h'], lang) + '</h2>\n  <p class="sub">'
     + L(S['ev_sub'], lang) + '</p>\n  <p>'
     + filelink('data/evidence_index.csv', 'evidence_index.csv')
     + ' &nbsp;<span class="count">' + L(S['ev_count'], lang) + '</span></p>\n</div></section>\n\n'
     '<section><div class="wrap">\n  <h2>' + L(S['doc_h'], lang) + '</h2>\n  <p class="sub">'
     + (L(S['doc_sub'], lang) % (len(docs), n_urls, n_arch, len(docs))) + '</p>\n'
     '  <div class="toolbar">\n    <input type="search" id="q" placeholder="'
     + L(S['filter_ph'], lang) + '" aria-label="' + L(S['filter_ph'], lang) + '">\n'
     '    <span class="count" id="n"></span>\n  </div>\n'
     '  <div class="tablewrap"><table id="tbl"><thead><tr><th>' + t('col_country', lang)
     + '</th><th>' + t('col_var', lang) + '</th><th>' + t('col_source', lang) + '</th><th>'
     + t('col_status', lang) + '</th><th>' + t('col_note', lang) + '</th><th>'
     + t('col_archived', lang) + '</th></tr></thead><tbody>'
     + ''.join(drows) + '</tbody></table></div>\n  <p style="margin-top:12px">'
     + filelink('data/source_register.csv', 'source_register.csv')
     + filelink('data/web_snapshots.csv', 'web_snapshots.csv')
     + filelink('verification/download_log.csv', 'download_log.csv') + '</p>\n</div></section>\n\n'
     '<section><div class="wrap">\n  <h2>' + L(S['fail_h'], lang) + '</h2>\n'
     '  <div class="note ok-note">' + (L(S['fail_note'], lang) % (len(docs), n_superseded))
     + '</div>\n'
     '  <p>' + L(S['fail_p'], lang) + '<a href="' + fname('verification', lang) + '">'
     + L(S['ver_link'], lang) + '</a>。</p>\n</div></section>\n\n'
     '<script>\n(function(){\n'
     "  var q=document.getElementById('q'),n=document.getElementById('n'),\n"
     "      rows=[].slice.call(document.querySelectorAll('#tbl tbody tr'));\n"
     "  function upd(){var s=q.value.trim().toLowerCase(),c=0;\n"
     "    rows.forEach(function(r){var m=!s||r.getAttribute('data-t').indexOf(s)>=0;\n"
     "      r.style.display=m?'':'none'; if(m)c++;});\n"
     "    n.textContent=c+' " + (L(S['of_sources'], lang) % len(docs)) + "';}\n"
     "  q.addEventListener('input',upd); upd();\n})();\n</script>\n")
    page('sources', L(S['h1'], lang), body, lang,
         desc={'en': 'Every data source with its archived copy.',
               'zh': '所有資料來源及其存檔備份。'}[lang])


# ==============================================================  DATA
def build_data(lang):
    def sizeof(rel):
        p = os.path.join(SITE, rel)
        return os.path.getsize(p) if os.path.exists(p) else 0

    MAIN_EN = [
     ('data/FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx',
      ('The verified panel, all sheets', '已查證之 panel 資料（全部工作表）'),
      ('Excel workbook, ten sheets: README, Panel_final, Data_quality, Corrections_applied, '
       'Known_issues, Verification_log, Source_register, Irregular_estimates_all, Codebook '
       'and Deleted_values.',
       'Excel 活頁簿，共十個工作表：README、Panel_final、Data_quality、Corrections_applied、'
       'Known_issues、Verification_log、Source_register、Irregular_estimates_all、Codebook '
       '與 Deleted_values。')),
     ('data/panel_final.csv', ('Panel_final as CSV', 'Panel_final（CSV 格式）'),
      ('520 rows, one per country-year, with source, URL, reference date and quality grade on '
       'every value.', '520 列，每列為一個國家—年度，每個數值均附來源、網址、基準日與品質等級。')),
     ('data/codebook.csv', ('Codebook', '變項說明書'),
      ('Variable definitions and cautions.', '變項定義與注意事項。')),
     ('data/data_quality.csv', ('Data quality by country and variable', '各國各變項之資料品質'),
      ('Coverage, modal grade, sources and whether each series can carry a trend.',
       '涵蓋率、主要品質等級、來源，以及各序列是否足以支撐趨勢分析。')),
     ('data/corrections_applied.csv', ('Corrections applied', '已套用之更正'),
      ('Every value changed from the input workbooks, with reason and evidence.',
       '相對於原始工作表的每一處數值改動，含理由與佐證。')),
     ('data/known_issues.csv', ('Known issues', '已知問題'),
      ('Resolved and unresolved, with severity.', '已解決與未解決者，並標註嚴重度。')),
     ('data/verification_log.csv', ('Verification log', '查證紀錄'),
      ('All %s value-by-value comparisons against live sources.' % format(len(vlog), ','),
       '全部 %s 筆與線上來源之逐值比對。' % format(len(vlog), ','))),
     ('data/source_register.csv', ('Source register', '來源清冊'),
      ('Every cited source and how it was retrieved.', '所有引用來源及其取得方式。')),
     ('data/irregular_estimates_all.csv',
      ('All competing irregular-migration estimates', '所有並存之無證移民推估值'),
      ('Every published estimate side by side, so alternatives are visible rather than hidden.',
       '所有已發表之推估值並列呈現，使替代估計可見而非被隱藏。')),
     ('data/evidence_index.csv', ('Evidence page index', '佐證頁索引'),
      ('Each country x variable with its evidence page and PDF extract.',
       '各國家 × 變項及其佐證頁與 PDF 摘錄。')),
     ('data/api_snapshots.csv', ('API snapshot index', 'API 快照索引'),
      ('Each raw payload with the query URL that produced it.',
       '各原始回應內容及產生該回應之查詢網址。')),
     ('data/api_publisher_snapshots.csv',
      ('Publisher page mirrors', '發布機構頁面鏡像'),
      ('PDF and screenshot mirror of each publisher dataset page.',
       '各發布機構資料集頁面之 PDF 與截圖鏡像。')),
     ('data/web_snapshots.csv', ('Web snapshot index', '網頁快照索引'),
      ('Each page with its PDF mirror and screenshot.', '各網頁及其 PDF 鏡像與截圖。')),
     ('manifest/checksums.csv', ('SHA-256 checksums', 'SHA-256 校驗碼'),
      ('Integrity hash for every file in this archive.', '本存檔每一份檔案之完整性雜湊值。')),
    ]
    i = 0 if lang == 'en' else 1

    def flist(items):
        out = ''.join(
            '<tr><td><strong>%s</strong><br><span style="color:var(--muted);font-size:13px">%s'
            '</span></td><td class="num">%s KB</td><td>%s</td></tr>'
            % (E(name[i]), E(desc[i]), format(sizeof(rel) // 1024, ','),
               filelink(rel, os.path.basename(rel)))
            for rel, name, desc in items)
        return ('<div class="tablewrap"><table><thead><tr><th>' + L(DT['col_file'], lang)
                + '</th><th class="num">' + L(DT['col_size'], lang) + '</th><th>'
                + L(DT['col_dl'], lang) + '</th></tr></thead><tbody>' + out + '</tbody></table></div>')

    # codebook
    hdr = C.CODEBOOK_HDR[lang]
    crows = []
    for idx, r in codeb.iterrows():
        if lang == 'zh' and idx in C.CODEBOOK_ZH:
            d, c = C.CODEBOOK_ZH[idx]
        else:
            d, c = r.iloc[1], r.iloc[2]
        crows.append('<tr><td><code>%s</code></td><td>%s</td><td>%s</td></tr>'
                     % (E(r.iloc[0]), E(d), E(c)))
    cb = ('<div class="tablewrap"><table><thead><tr>'
          + ''.join('<th>%s</th>' % E(x) for x in hdr) + '</tr></thead><tbody>'
          + ''.join(crows) + '</tbody></table></div>')

    body = (
     '<div class="hero"><div class="wrap">\n  <p class="eyebrow">' + L(DT['eyebrow'], lang)
     + '</p>\n  <h1>' + L(DT['h1'], lang) + '</h1>\n  <p class="lede">' + L(DT['lede'], lang)
     + '</p>\n</div></div>\n\n'
     '<section><div class="wrap">\n  <h2>' + L(DT['main_h'], lang) + '</h2>\n  <p class="sub">'
     + L(DT['main_sub'], lang) + '</p>\n' + flist(MAIN_EN) + '\n</div></section>\n\n'
     '<section><div class="wrap">\n  <h2>' + L(DT['ctry_h'], lang) + '</h2>\n  <p class="sub">'
     + L(DT['ctry_sub'], lang) + '<a href="' + fname('countries', lang) + '">'
     + L(DT['ctry_link'], lang) + '</a>' + L(DT['ctry_sub2'], lang)
     + '<code>evidence/countries/&lt;ISO3&gt;/</code>.</p>\n  <ul class="clean">\n'
     '   <li><code>data_from_source.csv</code> ' + L(DT['f_data'], lang) + '</li>\n'
     '   <li><code>value_check.csv</code> ' + L(DT['f_check'], lang) + '</li>\n'
     '   <li><code>source_manifest.csv</code> ' + L(DT['f_manifest'], lang) + '</li>\n'
     '   <li><code>README.md</code> ' + L(DT['f_readme'], lang) + '</li>\n'
     '  </ul>\n</div></section>\n\n'
     '<section><div class="wrap">\n  <h2>' + L(DT['cb_h'], lang) + '</h2>\n  ' + cb
     + '\n</div></section>\n')
    page('data', L(DT['h1'], lang), body, lang,
         desc={'en': 'Download the verified panel, codebook and supporting tables.',
               'zh': '下載已查證之 panel 資料、變項說明書與佐證表格。'}[lang])


# ==============================================================  VERIFICATION
def build_verification(lang):
    # one row per source: its most recent verification and the date that test ran
    by = pd.read_csv(os.path.join(D, 'reproduction_rate_latest.csv'))
    by['rate'] = (by.exact / by.n * 100).round(1)
    by = by.sort_values('n', ascending=False)
    def _prev(r):
        v = str(r.get('earlier_date') or '')
        if not v.strip() or v == 'nan':
            return '<span style="color:var(--faint)">&mdash;</span>'
        return ('<span style="color:var(--muted)">%s &middot; %s%%</span>'
                % (E(v), E(r['earlier_rate'])))

    srows = ''.join('<tr><td>%s</td><td class="num">%s</td><td class="num">%s</td>'
                    '<td class="num">%s</td><td class="num">%.1f%%</td><td class="num">%s</td></tr>'
                    % (E(r['source']), E(r['verified_on']), num(r['n']), num(r['exact']),
                       r['rate'], _prev(r))
                    for _, r in by.iterrows())
    srctab = ('<div class="tablewrap"><table><thead><tr><th>' + L(V['col_src'], lang)
              + '</th><th class="num">' + L(V['col_date'], lang) + '</th><th class="num">'
              + L(V['col_nchk'], lang) + '</th><th class="num">' + L(V['col_exact'], lang)
              + '</th><th class="num">' + L(V['col_rate'], lang) + '</th><th class="num">'
              + L(V['col_prev'], lang) + '</th></tr></thead><tbody>'
              + srows + '</tbody></table></div>')

    order = {'RESOLVED': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'INFO': 4}
    iss = issues.copy()
    iss['o'] = iss.severity.map(lambda s: order.get(s, 9))
    iss = iss.sort_values('o')
    irows = []
    for idx, r in iss.iterrows():
        cls = {'RESOLVED': 'ok', 'HIGH': 'bad', 'MEDIUM': 'warn'}.get(r['severity'], '')
        if lang == 'zh':
            sev = C.SEV.get(r['severity'], r['severity'])
            scope = C.SCOPE.get(str(r['scope']), str(r['scope']))
            iz, ez, az = C.ISSUES_ZH.get(idx, (r['issue'], r['evidence'], r['action']))
        else:
            sev, scope, iz, ez, az = r['severity'], r['scope'], r['issue'], r['evidence'], r['action']
        irows.append('<tr><td><span class="tag %s">%s</span></td><td>%s<br>'
                     '<span style="color:var(--muted);font-size:12.5px">%s</span></td>'
                     '<td class="wrap-any">%s</td>'
                     '<td class="wrap-any" style="color:var(--muted)">%s</td>'
                     '<td class="wrap-any">%s</td></tr>'
                     % (cls, E(sev), E(scope), E(r['variable']), E(iz), E(ez), E(az)))
    isstab = ('<div class="tablewrap"><table><thead><tr><th>' + L(V['col_sev'], lang)
              + '</th><th>' + L(V['col_scope'], lang) + '</th><th>' + L(V['col_issue'], lang)
              + '</th><th>' + L(V['col_evid'], lang) + '</th><th>' + L(V['col_action'], lang)
              + '</th></tr></thead><tbody>' + ''.join(irows) + '</tbody></table></div>')

    cr = corr.copy()
    cr['what'] = [('%s %d' % (vlab(v, lang), int(y))) for v, y in zip(cr['variable'], cr['year'])]
    if lang == 'zh':
        cr['reason'] = cr['reason'].map(reason_zh)
    ctab = table(cr, ['iso3', 'what', 'old_value', 'new_value', 'reason'],
                 [t('col_country', lang), t('col_value', lang), t('col_was', lang),
                  t('col_now', lang), t('col_why', lang)], numcols=('old_value', 'new_value'))

    body = (
     '<div class="hero"><div class="wrap">\n  <p class="eyebrow">' + L(V['eyebrow'], lang)
     + '</p>\n  <h1>' + L(V['h1'], lang) + '</h1>\n  <p class="lede">'
     + L(V['lede'], lang).replace('ACCESS', ACCESS) + '</p>\n</div></div>\n\n'
     '<section><div class="wrap">\n  <div class="stats">\n'
     '    <div class="stat"><span class="n">%s</span><span class="l">%s</span></div>\n'
     '    <div class="stat"><span class="n">%s</span><span class="l">%s</span></div>\n'
     '    <div class="stat"><span class="n">%d</span><span class="l">%s</span></div>\n'
     '    <div class="stat"><span class="n">%d</span><span class="l">%s</span></div>\n'
     '  </div>\n</div></section>\n\n'
     % (format(len(vlog), ','), t('stat_checked', lang),
        format(int((vlog.status == 'EXACT').sum()), ','), t('stat_exact', lang),
        int((vlog.status != 'EXACT').sum()),
        {'en': 'discrepancies', 'zh': '筆不一致'}[lang], len(corr), t('stat_corr', lang))
     + '<section><div class="wrap">\n  <h2>' + L(V['rate_h'], lang) + '</h2>\n  <p class="sub">'
     + L(V['rate_sub'], lang) + '</p>\n  ' + srctab + '\n'
     + '  <div class="note">' + L(V['rate_hist'], lang) + '</div>\n'
     + '  <p style="margin-top:12px">'
     + filelink('data/verification_log.csv', L(V['fulllog'], lang))
     + filelink('data/reproduction_rate_latest.csv', 'reproduction_rate_latest.csv')
     + filelink('evidence/api/eurostat_migr_eipre_REVERIFY_2026-08-18.json',
                {'en': 'the 2026-08-18 re-query payload',
                 'zh': '2026-08-18 重測查詢之原始回應'}[lang])
     + '</p>\n</div></section>\n\n'
     + '<section><div class="wrap">\n  <h2>' + L(V['corr_h'], lang) + '</h2>\n  <p class="sub">'
     + (L(V['corr_sub'], lang) % (len(corr), corr.iso3.nunique()))
     + '</p>\n  ' + ctab + '\n</div></section>\n\n'
     '<section><div class="wrap">\n  <h2>' + L(V['iss_h'], lang) + '</h2>\n  <p class="sub">'
     + L(V['iss_sub'], lang) + '</p>\n  ' + isstab + '\n</div></section>\n\n'
     '<section><div class="wrap">\n  <h2>' + L(V['held_h'], lang) + '</h2>\n  <p class="sub">'
     + L(V['held_sub'], lang) + '</p>\n  <ul class="clean">\n'
     + ''.join('   <li>%s</li>\n' % x for x in V['held'][lang]) + '  </ul>\n</div></section>\n')
    page('verification', L(V['h1'], lang), body, lang,
         desc={'en': 'Full verification record and corrections.',
               'zh': '完整查證紀錄與更正內容。'}[lang])


# ==============================================================  METHODS
def build_methods(lang):
    qsum = qual[qual.n_years > 0].groupby('variable').agg(
        countries=('iso3', 'nunique'), obs=('n_years', 'sum')).reset_index()
    qrows = ''
    for v in VARS:
        row = qsum[qsum.variable == v]
        obs = int(row.obs.iloc[0]) if len(row) else 0
        nc = int(row.countries.iloc[0]) if len(row) else 0
        qrows += ('<tr><td>%s</td><td class="num">%d / 520</td><td class="num">%d / 40</td>'
                  '<td>%s</td></tr>' % (E(vlab(v, lang)), obs, nc, E(M['verdict'][lang][v])))
    qtab = ('<div class="tablewrap"><table><thead><tr><th>' + t('col_var', lang)
            + '</th><th class="num">' + L(M['col_cy'], lang) + '</th><th class="num">'
            + L(M['col_ctries'], lang) + '</th><th>' + L(M['col_verdict'], lang)
            + '</th></tr></thead><tbody>' + qrows + '</tbody></table></div>')
    grows = ''.join('<tr><td>%s</td><td>%s</td></tr>' % (pill(k), M['grade_full'][lang][k])
                    for k in ['A', 'B', 'C', 'D'])

    body = (
     '<div class="hero"><div class="wrap">\n  <p class="eyebrow">' + L(M['eyebrow'], lang)
     + '</p>\n  <h1>' + L(M['h1'], lang) + '</h1>\n  <p class="lede">' + L(M['lede'], lang)
     + '</p>\n</div></div>\n\n'
     '<section><div class="wrap">\n  <h2>' + L(M['proc_h'], lang) + '</h2>\n'
     '  <ol style="max-width:78ch;line-height:1.75">\n'
     + ''.join('   <li>%s</li>\n' % x for x in M['proc'][lang]) + '  </ol>\n</div></section>\n\n'
     '<section><div class="wrap">\n  <h2>' + L(M['inputs_h'], lang) + '</h2>\n  <p>'
     + L(M['inputs_p'], lang) + '</p>\n</div></section>\n\n'
     + '<section><div class="wrap">\n  <h2>' + t('author_h', lang) + '</h2>\n  <p>'
     + t('author_p', lang) + '</p>\n</div></section>\n\n'
     '<section><div class="wrap">\n  <h2>' + L(M['grade_h'], lang) + '</h2>\n  <p class="sub">'
     + L(M['grade_sub'], lang) + '</p>\n  <div class="tablewrap"><table><thead><tr><th>'
     + t('grade_col', lang) + '</th><th>' + L(M['col_crit'], lang) + '</th></tr></thead><tbody>'
     + grows + '</tbody></table></div>\n</div></section>\n\n'
     '<section><div class="wrap">\n  <h2>' + L(M['weight_h'], lang) + '</h2>\n  ' + qtab + '\n'
     '  <div class="note">' + L(M['rec_note'], lang) + '</div>\n'
     '  <div class="note warn">' + L(M['warn_note'], lang) + '</div>\n</div></section>\n\n'
     '<section><div class="wrap">\n  <h2>' + L(M['caut_h'], lang) + '</h2>\n  <ul class="clean">\n'
     + ''.join('   <li>%s</li>\n' % x for x in M['caut'][lang]) + '  </ul>\n</div></section>\n\n'
     '<section><div class="wrap">\n  <h2>' + L(M['lim_h'], lang) + '</h2>\n  <p>'
     + L(M['lim1'], lang) + '<a href="' + fname('verification', lang) + '">'
     + L(V['h1'], lang) + '</a>' + L(M['lim2'], lang) + '</p>\n  <p>' + L(M['lim3'], lang)
     + '</p>\n</div></section>\n')
    page('methods', L(M['h1'], lang), body, lang,
         desc={'en': 'Verification procedure, grading scheme and variable guidance.',
               'zh': '查證流程、品質分級標準與變項使用建議。'}[lang])


if __name__ == '__main__':
    for lang in ['en', 'zh']:
        build_sources(lang); build_data(lang); build_verification(lang); build_methods(lang)
        print('%s: sources, data, verification, methods' % lang)
