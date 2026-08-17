# -*- coding: utf-8 -*-
"""Bilingual build: index, countries index, and the 40 country pages."""
import os, sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blib import (SITE, EV, D, ACCESS, panel, qual, corr, vlog, reg, apis, snaps,
                  VARS, ALLVARS, E, num, pill, filelink, page, table, cname, vlab,
                  fname, usable_zh, T, t, GRADE_DESC, GRADE_SHORT, VERTAG, COMPARABILITY,
                  reason_zh)
import i18n_content as C

snap_by = {}
for _, s in snaps.iterrows():
    snap_by.setdefault((s['iso3'], s['source_url']), []).append(s)

cinfo = panel.groupby(['iso3', 'country']).size().reset_index()[['iso3', 'country']]
n_checked = len(vlog)
n_exact = int((vlog.status == 'EXACT').sum())
# count grades over every displayed variable, including Taiwan's absconded-workers
# column, so the index, the README and the workbook all state the same total
grades = pd.Series([g for v in ALLVARS if v + '_grade' in panel
                    for g in panel[v + '_grade'].dropna()
                    if str(g).strip()]).value_counts()
n_files = sum(len(fs) for _, _, fs in os.walk(os.path.join(SITE, 'evidence')))
ev_bytes = sum(os.path.getsize(os.path.join(rt, f))
               for rt, _, fs in os.walk(os.path.join(SITE, 'evidence')) for f in fs)

FIND = {
 'en': ('<strong>A one-year offset in three countries.</strong> In the input workbook, the '
        'Eurostat irregular-migration detections series for <strong>Switzerland, Portugal and '
        'Sweden</strong> was shifted by one year: the figure Eurostat publishes for year '
        '<em>Y+1</em> sat under year <em>Y</em>. The genuine 2010 values were missing and the 2022 '
        'cell held the 2023 figure. All 39 values were replaced with the year-aligned Eurostat '
        'data.',
        'A consequence worth noting: the input codebook warned that Sweden\'s detections series '
        'breaks between 2013 (72,835) and 2014 (1,445). That break is an artefact of the offset. '
        'In the real Eurostat data it falls between <strong>2014 and 2015</strong>. The evidence '
        'is archived as ',
        'a raw Eurostat API response covering 2010&ndash;2023',
        'Three further corrections were made &mdash; Taiwan\'s overstayer column mixed two '
        'incompatible national measures, Italy\'s irregular series was missing four years and '
        'mixed two methods, and the two input workbooks disagreed on population because they used '
        'different publishers. ', 'All %d corrections are itemised, with evidence.'),
 'zh': ('<strong>三個國家的序列整體位移一年。</strong>在原始工作表中，'
        '<strong>瑞士、葡萄牙與瑞典</strong>的 Eurostat 非常規移民查獲人次序列被位移一年：'
        'Eurostat 公布之 <em>Y+1</em> 年數值被置於 <em>Y</em> 年。'
        '真正的 2010 年數值付之闕如，而 2022 年欄位實際上放的是 2023 年數字。'
        '39 筆數值已全部替換為年度對齊之 Eurostat 資料。',
        '值得一提的後果：原始變項說明書警告瑞典查獲人次序列在 2013 年（72,835）'
        '與 2014 年（1,445）之間出現斷點。該斷點正是位移所造成的假象；'
        '在真實的 Eurostat 資料中，斷點落在 <strong>2014 與 2015 年</strong>之間。'
        '佐證已存檔為',
        '涵蓋 2010&ndash;2023 年之 Eurostat API 原始回應',
        '另有三處更正&mdash;&mdash;臺灣的逾期停留欄位混用兩種不相容的國內統計；'
        '義大利的無證移民序列缺漏四年且混用兩種方法；'
        '兩份原始工作表因採用不同發布機構而在人口數上不一致。',
        '全部 %d 筆更正均逐項載明並附佐證。'),
}

USING = {
 'en': ['<strong>Every file is downloadable at a stable relative URL.</strong> Nothing is behind a '
        'script, a query string, or an external service.',
        '<strong>API data is archived as raw responses.</strong> The exact JSON and spreadsheet '
        'payloads returned by the World Bank, Eurostat, OECD and UN DESA on ACCESS are in '
        '<code>evidence/api/</code>, together with the query URL that produced each one.',
        '<strong>Web pages are archived three ways</strong> where possible: the original HTML, a '
        'PDF mirror, and a full-page PNG screenshot, all captured on ACCESS.',
        '<strong>Integrity is checkable.</strong> <a href="manifest/checksums.csv">SHA-256 '
        'checksums</a> are published for every file in the archive.',
        '<strong>The verification is re-runnable.</strong> Every script used is included in '
        '<code>scripts/</code>.'],
 'zh': ['<strong>每份檔案都有穩定的相對網址可供下載。</strong>'
        '沒有任何內容藏在腳本、查詢字串或外部服務之後。',
        '<strong>API 資料以原始回應形式存檔。</strong>世界銀行、Eurostat、OECD 與 UN DESA '
        '於 ACCESS 回傳的 JSON 與試算表內容原封保存於 <code>evidence/api/</code>，'
        '並附上產生各該回應的查詢網址。',
        '<strong>網頁來源以三種方式存檔</strong>（在可行的情況下）：原始 HTML、PDF 鏡像，'
        '以及整頁 PNG 截圖，全部擷取於 ACCESS。',
        '<strong>完整性可供驗證。</strong>本存檔每一份檔案的 '
        '<a href="manifest/checksums.csv">SHA-256 校驗碼</a>均已公布。',
        '<strong>查證過程可重複執行。</strong>所使用的每一支腳本均收錄於 <code>scripts/</code>。'],
}

EVLINK = {
 'en': ['Click any value &mdash; or the grade pill beside it &mdash; and you land on the evidence '
        'for that exact figure: the source, the query URL that produced it, what it was checked '
        'against, the correction applied if there was one, and every archived file that supports '
        'it. There are <strong>156 such evidence pages</strong>, one per country and variable, '
        'each with its own <strong>PDF extract</strong> so the numbers exist in a fixed, citable '
        'document as well as on the page.',
        'This holds for the bulk statistical sources too. The World Bank, Eurostat, OECD and UN '
        'DESA series are backed not only by their raw API payloads but by <strong>PDF and '
        'screenshot mirrors of the publishers\' own dataset pages</strong>, captured on the access '
        'date.'],
 'zh': ['點選任何數值&mdash;&mdash;或其旁的等級標記&mdash;&mdash;即可進入該筆數字的佐證頁：'
        '包含來源、產生該數值的查詢網址、核對對象、若有更正則載明更正內容，'
        '以及支持該數值的全部存檔檔案。此類佐證頁共 <strong>156 個</strong>，'
        '每個國家的每個變項各一，並各附 <strong>PDF 摘錄</strong>，'
        '使這些數字除網頁外亦存在於可引用的固定文件中。',
        '批次統計來源亦同。世界銀行、Eurostat、OECD 與 UN DESA 的序列，'
        '除原始 API 回應外，另有<strong>各發布機構自身資料集頁面的 PDF 與截圖鏡像</strong>，'
        '皆擷取於取得當日。'],
}


def build_index(lang):
    g = grades
    tot = int(g.sum())
    f = FIND[lang]
    rows = ''.join(
        '<tr><td>%s</td><td>%s</td><td class="num">%s</td><td class="num">%.1f%%</td></tr>'
        % (pill(k), GRADE_DESC[lang][k], format(int(g.get(k, 0)), ','), g.get(k, 0) / tot * 100)
        for k in ['A', 'B', 'C', 'D'])
    body = (
     '<div class="hero"><div class="wrap">\n'
     '  <p class="eyebrow">' + t('access_prefix', lang) + ACCESS + '</p>\n'
     '  <h1>' + t('idx_title', lang) + '</h1>\n'
     '  <p class="lede">' + t('idx_lede', lang) + '</p>\n</div></div>\n\n'
     '<section><div class="wrap">\n  <div class="stats">\n'
     '    <div class="stat"><span class="n">%s</span><span class="l">%s</span></div>\n'
     '    <div class="stat"><span class="n">%.1f%%</span><span class="l">%s</span></div>\n'
     '    <div class="stat"><span class="n">%d</span><span class="l">%s</span></div>\n'
     '    <div class="stat"><span class="n">%.0f MB</span><span class="l">%s</span></div>\n'
     '    <div class="stat"><span class="n">40</span><span class="l">%s</span></div>\n'
     '    <div class="stat"><span class="n">%d</span><span class="l">%s</span></div>\n'
     '    <div class="stat"><span class="n">156</span><span class="l">%s</span></div>\n'
     '  </div>\n</div></section>\n\n'
     % (format(n_checked, ','), t('stat_checked', lang), n_exact / n_checked * 100,
        t('stat_exact', lang), n_files, t('stat_files', lang), ev_bytes / 1e6, t('stat_mb', lang),
        t('stat_countries', lang), len(corr), t('stat_corr', lang), t('stat_ev', lang))
     + '<section><div class="wrap">\n  <h2>' + t('start_here', lang) + '</h2>\n'
     '  <p class="sub">' + t('start_sub', lang) + '</p>\n  <div class="cards">\n'
     '    <div class="card"><h3>' + t('card_data_h', lang) + '</h3><p>' + t('card_data_p', lang)
     + '</p><a class="go" href="' + fname('data', lang) + '">' + t('card_data_go', lang) + '</a></div>\n'
     '    <div class="card"><h3>' + t('card_ctry_h', lang) + '</h3><p>' + t('card_ctry_p', lang)
     + '</p><a class="go" href="' + fname('countries', lang) + '">' + t('card_ctry_go', lang) + '</a></div>\n'
     '    <div class="card"><h3>' + t('card_src_h', lang) + '</h3><p>' + t('card_src_p', lang)
     + '</p><a class="go" href="' + fname('sources', lang) + '">' + t('card_src_go', lang) + '</a></div>\n'
     '    <div class="card"><h3>' + t('card_ver_h', lang) + '</h3><p>'
     + ({'en': 'All %s value-by-value comparisons, the corrections applied, and the issues that '
                'remain.' % format(n_checked, ','),
         'zh': '全部 %s 筆逐值比對、已套用之更正，以及仍然存在的問題。' % format(n_checked, ',')}[lang])
     + '</p><a class="go" href="' + fname('verification', lang) + '">' + t('card_ver_go', lang)
     + '</a></div>\n  </div>\n</div></section>\n\n'
     '<section><div class="wrap">\n  <h2>' + t('reliab_h', lang) + '</h2>\n'
     '  <p class="sub">'
     + ({'en': 'Every one of the %s values in the panel carries a grade. Grades are assigned per '
               'value, not per country.' % format(tot, ','),
         'zh': 'Panel 中全部 %s 筆數值均標註品質等級。等級係逐值給定，而非逐國給定。'
               % format(tot, ',')}[lang])
     + '</p>\n  <div class="tablewrap"><table><thead><tr><th>' + t('grade_col', lang)
     + '</th><th>' + t('mean_col', lang) + '</th><th class="num">' + t('values_col', lang)
     + '</th><th class="num">' + t('share_col', lang) + '</th></tr></thead><tbody>'
     + rows + '</tbody></table></div>\n  <div class="note">' + t('d_note', lang) + '</div>\n'
     '</div></section>\n\n'
     '<section><div class="wrap">\n  <h2>' + t('finding_h', lang) + '</h2>\n'
     '  <p class="sub">' + t('finding_sub', lang) + '</p>\n'
     '  <div class="note bad">' + f[0] + '</div>\n'
     '  <p>' + f[1] + '<a href="evidence/api/eurostat_migr_eipre_CH_PT_SE_2010_2023.json">'
     + f[2] + '</a>.</p>\n'
     '  <p>' + f[3] + '<a href="' + fname('verification', lang) + '">' + (f[4] % len(corr))
     + '</a></p>\n</div></section>\n\n'
     '<section><div class="wrap">\n  <h2>' + t('evlink_h', lang) + '</h2>\n'
     '  <p class="sub">' + t('evlink_sub', lang) + '</p>\n'
     + ''.join('  <p>' + x + '</p>\n' for x in EVLINK[lang]) + '</div></section>\n\n'
     '<section><div class="wrap">\n  <h2>' + t('author_h', lang) + '</h2>\n'
     '  <p>' + t('author_p', lang) + '</p>\n</div></section>\n\n'
     '<section><div class="wrap">\n  <h2>' + t('using_h', lang) + '</h2>\n'
     '  <p class="sub">' + t('using_sub', lang) + '</p>\n  <ul class="clean">\n'
     + ''.join('   <li>' + x.replace('ACCESS', ACCESS) + '</li>\n' for x in USING[lang])
     + '  </ul>\n</div></section>\n')
    page('index', {'en': 'Migration & Population Data Archive, 40 countries 2010–2022',
                   'zh': '移民與人口資料存檔，40 國，2010–2022'}[lang], body, lang,
         desc={'en': 'Source archive and verification record for a 40-country migration and '
                     'population panel, 2010-2022.',
               'zh': '40 國移民與人口 panel 資料（2010–2022）之來源存檔與查證紀錄。'}[lang])


def build_countries_index(lang):
    boxes = []
    for _, r in cinfo.sort_values('country').iterrows():
        iso = r['iso3']
        g = panel[panel.iso3 == iso]
        nv = sum(g[v].notna().sum() for v in ALLVARS if v in g)
        nf = len(os.listdir(os.path.join(EV, iso))) if os.path.isdir(os.path.join(EV, iso)) else 0
        boxes.append('<a class="cbox" href="countries/%s"><span class="cn">%s</span>'
                     '<span class="cm">%s · %d %s · %d %s</span></a>'
                     % (os.path.basename(fname('countries/' + iso, lang)),
                        E(cname(r['country'], lang)), iso, nv, t('values_word', lang),
                        nf, t('files_word', lang)))
    body = (
     '<div class="hero"><div class="wrap">\n'
     '  <p class="eyebrow">' + ({'en': '40 countries', 'zh': '40 個國家'}[lang]) + '</p>\n'
     '  <h1>' + t('ctry_idx_title', lang) + '</h1>\n'
     '  <p class="lede">' + t('ctry_idx_lede', lang) + '</p>\n</div></div>\n'
     '<section><div class="wrap">\n  <div class="toolbar">\n'
     '    <input type="search" id="q" placeholder="' + t('filter_ph', lang) + '" aria-label="'
     + t('filter_ph', lang) + '">\n    <span class="count" id="n">40 ' + t('n_countries', lang)
     + '</span>\n  </div>\n  <div class="cgrid" id="grid">' + ''.join(boxes) + '</div>\n'
     '</div></section>\n<script>\n(function(){\n'
     "  var q=document.getElementById('q'),grid=document.getElementById('grid'),\n"
     "      n=document.getElementById('n'),items=[].slice.call(grid.children);\n"
     "  q.addEventListener('input',function(){\n"
     "    var s=q.value.trim().toLowerCase(),c=0;\n"
     "    items.forEach(function(el){var m=!s||el.textContent.toLowerCase().indexOf(s)>=0;\n"
     "      el.style.display=m?'':'none'; if(m)c++;});\n"
     "    n.textContent=c+' " + t('n_countries', lang) + "';\n  });\n})();\n</script>\n")
    page('countries', {'en': 'Country pages — Migration Data Archive',
                       'zh': '各國頁面 — 移民與人口資料存檔'}[lang], body, lang,
         desc={'en': 'Per-country data, verification results and archived source documents.',
               'zh': '各國資料、查證結果與已存檔之來源文件。'}[lang])


def build_country(iso, en_name, lang):
    cn = cname(en_name, lang)
    g = panel[panel.iso3 == iso].sort_values('year')
    cq = qual[qual.iso3 == iso]
    cv = vlog[vlog.iso3 == iso]
    cr = reg[reg.iso3 == iso]
    cc = corr[(corr.iso3 == iso)]
    evdir = os.path.join(EV, iso)
    evfiles = sorted(os.listdir(evdir)) if os.path.isdir(evdir) else []

    extra = ['irregular_proxy_absconded_workers'] \
        if g['irregular_proxy_absconded_workers'].notna().any() else []
    show = VARS + extra
    head = '<th class="num">' + t('year', lang) + '</th>' + \
           ''.join('<th class="num">%s</th>' % vlab(v, lang) for v in show)
    rows = []
    for _, r in g.iterrows():
        cells = ['<td class="num">%d</td>' % int(r['year'])]
        for v in show:
            val = r[v]
            if pd.isna(val):
                cells.append('<td class="num">%s</td>' % num(val))
                continue
            href = '../%s#y%d' % (os.path.basename(
                fname('evidence-pages/%s__%s' % (iso, v), lang)), int(r['year']))
            href = '../evidence-pages/%s#y%d' % (os.path.basename(
                fname('evidence-pages/%s__%s' % (iso, v), lang)), int(r['year']))
            tip = ({'en': 'Evidence for %s %s %d', 'zh': '%s %s %d 年之佐證'}[lang]
                   % (cn, vlab(v, lang), int(r['year'])))
            der = ''
            if str(r.get(v + '_derived') or '') == 'yes':
                dtip = t('derived_tip', lang) % (
                    str(r.get(v + '_derivation') or ''), str(r.get(v + '_published_range') or ''))
                der = '<abbr class="der" title="%s">%s</abbr>' % (E(dtip), t('derived_mark', lang))
            cells.append('<td class="num"><a class="cell" href="%s" title="%s">%s</a>'
                         '<a class="cellg" href="%s" title="%s">%s</a>%s</td>'
                         % (href, E(tip), num(val), href, E(tip),
                            pill(r.get(v + '_grade', '')), der))
        rows.append('<tr>' + ''.join(cells) + '</tr>')
    dtable = ('<div class="tablewrap"><table><thead><tr>' + head + '</tr></thead><tbody>'
              + ''.join(rows) + '</tbody></table></div>')

    nchk, nex = len(cv), int((cv.status == 'EXACT').sum())
    if nchk:
        vsum = '<p class="sub">' + (t('ver_ok', lang) % ((nex, nchk, cn) if lang == 'en'
                                                         else (cn, nex, nchk))) + '</p>'
    else:
        vsum = '<p class="sub">' + t('ver_none', lang) + '</p>'
    disc = cv[cv.status != 'EXACT']
    if len(disc):
        dv = disc.sort_values(['variable', 'year']).copy()
        dv['year'] = dv['year'].astype(int).astype(str)
        dv['variable'] = dv['variable'].map(lambda v: vlab(v, lang))
        vsum += '<div class="note bad">' + (t('ver_disc', lang) % len(disc)) + '</div>'
        vsum += table(dv, ['year', 'variable', 'workbook_value', 'live_source_value', 'diff', 'source'],
                      [t('year', lang), t('col_var', lang), t('col_input', lang),
                       t('col_live', lang), t('col_diff', lang), t('col_source', lang)],
                      numcols=('workbook_value', 'live_source_value', 'diff'))

    csec = ''
    if len(cc):
        c2 = cc.copy()
        c2['what'] = [('%s %d' % (vlab(v, lang), int(y))) for v, y in zip(c2['variable'], c2['year'])]
        if lang == 'zh':
            c2['reason'] = c2['reason'].map(reason_zh)
        csec = ('<h3>' + t('corr_h', lang) + '</h3>'
                + table(c2, ['what', 'old_value', 'new_value', 'reason'],
                        [t('col_value', lang), t('col_was', lang), t('col_now', lang),
                         t('col_why', lang)], numcols=('old_value', 'new_value')))

    srows = []
    for _, r in cr.drop_duplicates(subset=['source_url', 'variable']).iterrows():
        url = str(r['source_url'])
        links = []
        lf = str(r.get('local_file') or '')
        if r['retrieval'] == 'VERIFIED_API':
            base = url.split('?')[0]
            for _, a in apis[apis.query_url.astype(str).str.split('?').str[0] == base].iterrows():
                links.append(filelink('../' + a['path'], t('art_raw', lang)))
        else:
            if lf and lf != 'nan':
                links.append(filelink('../evidence/countries/%s/%s' % (iso, lf),
                                      {'en': 'archived copy', 'zh': '存檔備份'}[lang]))
            for s in snap_by.get((iso, url), []):
                if isinstance(s['pdf_mirror'], str) and s['pdf_mirror']:
                    links.append(filelink('../evidence/countries/%s/%s' % (iso, s['pdf_mirror']),
                                          {'en': 'PDF mirror', 'zh': 'PDF 鏡像'}[lang]))
                if isinstance(s['png_screenshot'], str) and s['png_screenshot']:
                    links.append(filelink('../evidence/countries/%s/%s' % (iso, s['png_screenshot']),
                                          {'en': 'screenshot', 'zh': '截圖'}[lang]))
        if not links:
            links.append('<span class="tag bad">%s</span>' % C.P['sources']['tag_notret'][lang])
        srows.append('<tr><td>%s</td><td class="num">%s</td><td class="wrap-any">%s<br>'
                     '<a href="%s" rel="nofollow noopener" style="font-size:11.5px;'
                     'word-break:break-all;color:var(--muted)">%s</a></td><td>%s</td></tr>'
                     % (E(vlab(r['variable'], lang)), E(r['years']),
                        E(str(r['source_name'])[:150]), E(url), E(url[:100]), ''.join(links)))
    stable = ('<div class="tablewrap"><table><thead><tr><th>' + t('col_var', lang)
              + '</th><th class="num">' + t('col_years', lang) + '</th><th>'
              + t('col_source', lang) + '</th><th>' + t('col_archived', lang)
              + '</th></tr></thead><tbody>' + ''.join(srows) + '</tbody></table></div>')

    qrows = []
    for _, r in cq.iterrows():
        if r['n_years'] == 0:
            continue
        u = usable_zh(r['usable_for_trend']) if lang == 'zh' else r['usable_for_trend']
        qrows.append('<tr><td>%s</td><td class="num">%s</td><td class="num">%s</td><td>%s</td>'
                     '<td>%s</td></tr>' % (E(vlab(r['variable'], lang)), E(r['coverage']),
                                           E(r['years']), pill(r['modal_grade']), E(u)))
    qtable = ('<div class="tablewrap"><table><thead><tr><th>' + t('col_var', lang)
              + '</th><th class="num">' + t('col_cov', lang) + '</th><th class="num">'
              + t('col_years', lang) + '</th><th>' + t('grade_col', lang) + '</th><th>'
              + t('col_trend', lang) + '</th></tr></thead><tbody>' + ''.join(qrows)
              + '</tbody></table></div>')

    flinks = ''.join(filelink('../evidence/countries/%s/%s' % (iso, f), f) for f in evfiles)
    gl = GRADE_SHORT[lang]
    body = (
     '<div class="hero"><div class="wrap">\n'
     '  <p class="eyebrow">' + iso + t('ctry_eyebrow', lang) + '</p>\n'
     '  <h1>' + E(cn) + '</h1>\n'
     '  <p class="lede">' + (t('ctry_lede', lang) % E(cn)) + ACCESS + '</p>\n</div></div>\n\n'
     '<section><div class="wrap">\n  <h2>' + t('panel_h', lang) + '</h2>\n'
     '  <p class="sub">' + t('panel_sub', lang)
     + pill('A') + ' ' + gl['A'] + '、' * (lang == 'zh') + (', ' if lang == 'en' else '')
     + pill('B') + ' ' + gl['B'] + ('、' if lang == 'zh' else ', ')
     + pill('C') + ' ' + gl['C'] + ('。' if lang == 'zh' else '.') + '</p>\n'
     + '  <p class="sub" style="margin-top:-10px">'
     + (t('derived_legend', lang) % ('<abbr class="der">%s</abbr>' % t('derived_mark', lang)))
     + '</p>\n  ' + dtable + '\n'
     '  <p style="margin-top:12px">'
     + filelink('../evidence/countries/%s/data_from_source.csv' % iso, t('dl_csv', lang))
     + filelink('../evidence/countries/%s/value_check.csv' % iso, t('dl_check', lang))
     + filelink('../evidence/countries/%s/source_manifest.csv' % iso, t('dl_manifest', lang))
     + filelink('../evidence/countries/%s/README.md' % iso, t('dl_readme', lang))
     + '</p>\n</div></section>\n\n'
     '<section><div class="wrap">\n  <h2>' + t('ver_h', lang) + '</h2>\n  ' + vsum + csec
     + '\n</div></section>\n\n'
     '<section><div class="wrap">\n  <h2>' + t('dq_h', lang) + '</h2>\n'
     '  <p class="sub">' + t('dq_sub', lang) + '</p>\n  ' + qtable + '\n</div></section>\n\n'
     '<section><div class="wrap">\n  <h2>' + t('src_h', lang) + '</h2>\n'
     '  <p class="sub">' + t('src_sub', lang) + ACCESS + '</p>\n  ' + stable + '\n</div></section>\n\n'
     '<section><div class="wrap">\n  <h2>' + t('allfiles_h', lang) + '</h2>\n'
     '  <p class="sub">' + (t('allfiles_sub', lang) % len(evfiles))
     + '<code>evidence/countries/' + iso + '/</code>.</p>\n  <p>'
     + (flinks or '<span class="tag">' + t('nodocs', lang) + '</span>') + '</p>\n</div></section>\n')
    page('countries/%s' % iso,
         '%s — %s' % (cn, {'en': 'Migration Data Archive', 'zh': '移民與人口資料存檔'}[lang]),
         body, lang, up='../',
         desc={'en': 'Data, verification and archived sources for %s, 2010-2022.' % cn,
               'zh': '%s 2010–2022 年之資料、查證與存檔來源。' % cn}[lang])


if __name__ == '__main__':
    for lang in ['en', 'zh']:
        build_index(lang)
        build_countries_index(lang)
        for _, ci in cinfo.iterrows():
            build_country(ci['iso3'], ci['country'], lang)
        print('%s: index, countries, %d country pages' % (lang, len(cinfo)))
