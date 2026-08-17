# -*- coding: utf-8 -*-
"""English / Traditional Chinese (Taiwan) string catalogue for the bilingual archive.

Terminology follows Taiwan usage: 臺灣, 資料 (not 数据), 外國人 / 非本國籍,
逾期停留・居留, 查獲, 內政部移民署, 勞動部.
"""

LANGS = ['en', 'zh']
HTML_LANG = {'en': 'en', 'zh': 'zh-Hant-TW'}
OTHER = {'en': 'zh', 'zh': 'en'}
SWITCH_LABEL = {'en': '中文', 'zh': 'English'}
SWITCH_TITLE = {'en': '切換到繁體中文版', 'zh': 'Switch to the English version'}

# ---------------------------------------------------------------- countries
COUNTRY = {
 'Australia': '澳洲', 'Austria': '奧地利', 'Belgium': '比利時', 'Bulgaria': '保加利亞',
 'Chile': '智利', 'China': '中國', 'Croatia': '克羅埃西亞', 'Czech Republic': '捷克',
 'Denmark': '丹麥', 'Finland': '芬蘭', 'France': '法國', 'Germany': '德國',
 'Hungary': '匈牙利', 'Iceland': '冰島', 'India': '印度', 'Israel': '以色列',
 'Italy': '義大利', 'Japan': '日本', 'Korea (South)': '南韓', 'Lithuania': '立陶宛',
 'Mexico': '墨西哥', 'Netherlands': '荷蘭', 'New Zealand': '紐西蘭', 'Norway': '挪威',
 'Philippines': '菲律賓', 'Poland': '波蘭', 'Portugal': '葡萄牙', 'Russia': '俄羅斯',
 'Slovak Republic': '斯洛伐克', 'Slovenia': '斯洛維尼亞', 'South Africa': '南非',
 'Spain': '西班牙', 'Suriname': '蘇利南', 'Sweden': '瑞典', 'Switzerland': '瑞士',
 'Taiwan': '臺灣', 'Thailand': '泰國', 'Turkey': '土耳其',
 'United Kingdom': '英國', 'United States': '美國',
}

# ---------------------------------------------------------------- variables
VLAB = {
 'en': {'population': 'Population', 'foreign_born': 'Foreign-born',
        'foreign_nationals': 'Foreign nationals', 'irregular_stock': 'Irregular stock',
        'irregular_proxy_overstayers': 'Overstayers',
        'irregular_proxy_detections': 'Detections',
        'irregular_proxy_absconded_workers': 'Absconded workers (TW)',
        'irregular_detections': 'Detections', 'irregular': 'Irregular migration',
        'foreign_workers': 'Foreign workers'},
 'zh': {'population': '總人口', 'foreign_born': '外國出生人口',
        'foreign_nationals': '外國籍人口', 'irregular_stock': '無證移民存量',
        'irregular_proxy_overstayers': '逾期停留・居留',
        'irregular_proxy_detections': '查獲人次',
        'irregular_proxy_absconded_workers': '失聯移工（臺灣）',
        'irregular_detections': '查獲人次', 'irregular': '非常規移民',
        'foreign_workers': '外籍移工'},
}

# ---------------------------------------------------------------- navigation
NAV = {
 'en': [('index.html', 'Overview'), ('countries.html', 'Countries'),
        ('sources.html', 'Sources'), ('data.html', 'Data files'),
        ('verification.html', 'Verification'), ('methods.html', 'Methods')],
 'zh': [('index.html', '總覽'), ('countries.html', '各國'),
        ('sources.html', '資料來源'), ('data.html', '資料檔案'),
        ('verification.html', '查證紀錄'), ('methods.html', '研究方法')],
}

BRAND = {'en': 'Migration &amp; Population Data Archive',
         'zh': '移民與人口資料存檔'}

# ---------------------------------------------------------------- footer
FOOTER = {
 'en': ['<p class="credit"><strong>This archive is joint work of '
        '<a href="https://raymond.cph.ntu.edu.tw/" rel="noopener">Prof. Raymond Kuo</a>, '
        'National Taiwan University, and Claude (Anthropic).</strong></p>',
        '<p><strong>Migration and population data archive, 40 countries, 2010&ndash;2022.</strong> '
        'Every source retrieved and verified ACCESS.</p>',
        '<p>Companion archive to a study of attitudes toward publicly funded healthcare for '
        'non-nationals. Prepared for journal editors and peer reviewers.</p>',
        '<p>All files here are mirrors held for verification. Copyright in each source document '
        'remains with its publisher; every entry links to the original URL.</p>'],
 'zh': ['<p class="credit"><strong>本存檔為國立臺灣大學'
        '<a href="https://raymond.cph.ntu.edu.tw/" rel="noopener">郭柏秀教授</a>'
        '與 Claude（Anthropic）之共同成果。</strong></p>',
        '<p><strong>移民與人口資料存檔，40 國，2010&ndash;2022 年。</strong>'
        '所有資料來源均於 ACCESS 重新取得並完成查證。</p>',
        '<p>本存檔為「民眾對非本國籍人士使用公費醫療之態度」研究之配套資料，'
        '供期刊編輯與審查委員查核之用。</p>',
        '<p>本站所存檔案均為查證用之備份。各來源文件之著作權仍屬其原出版機構所有，'
        '每筆條目均附原始網址連結。</p>'],
}

# ---------------------------------------------------------------- grades
GRADE_DESC = {
 'en': {'A': 'Re-derived from a machine-readable official source and matched exactly, or '
             'corrected against one during this verification',
        'B': 'Confirmed by reading the retrieved source document',
        'C': 'Source document retrieved, but the value is a modelled estimate that cannot be '
             'mechanically re-derived',
        'D': 'Cited source could not be retrieved by any means'},
 'zh': {'A': '自機器可讀之官方來源重新計算並完全一致，或於本次查證中依該來源更正',
        'B': '經閱讀所取得之來源文件確認',
        'C': '已取得來源文件，但該數值為推估值，無法以機械方式重新導出',
        'D': '所引用之來源已無法以任何方式取得'},
}

GRADE_SHORT = {
 'en': {'A': 'verified against a machine-readable official source',
        'B': 'confirmed in the source document',
        'C': 'modelled estimate', 'D': 'source unretrievable'},
 'zh': {'A': '已對照機器可讀之官方來源查證',
        'B': '經來源文件確認', 'C': '推估值', 'D': '來源無法取得'},
}

# ---------------------------------------------------------------- verification tags
VERTAG = {
 'en': {'corrected': 'corrected &amp; re-derived', 'exact': 'reproduced exactly',
        'doc': 'confirmed in document', 'nomach': 'not machine-checkable'},
 'zh': {'corrected': '已更正並重新導出', 'exact': '完全重現',
        'doc': '經文件確認', 'nomach': '無法機械核對'},
}

# ---------------------------------------------------------------- data-quality strings
USABLE = {
 'YES - continuous single-source series': 'YES｜單一來源之連續序列',
 'CAUTION - 10+ years but more than one source in the series': 'CAUTION｜逾 10 年，但序列中含多個來源',
 'CAUTION - partial coverage': 'CAUTION｜涵蓋不完整',
 'CAUTION - partial coverage, with gaps': 'CAUTION｜涵蓋不完整且有缺漏年度',
 'NO - too few years for a trend (use as a level only)': 'NO｜年數過少，不足以呈現趨勢（僅可作為水準值）',
 'NO - no data': 'NO｜無資料',
}

COMPARABILITY = {
 'population': '可直接跨國比較。39 國採世界銀行 WDI 年中人口；臺灣為內政部年底戶籍登記人口。',
 'foreign_born': '概念上可比較（出生於國外），但來源不一（Eurostat 為 1 月 1 日、OECD 為年中、'
                 'UN DESA 為基準年）。已包含歸化取得公民身分者。',
 'foreign_nationals': '最接近「非本國籍」之定義。採出生地主義之國家不編製此統計；'
                      '亦受歸化率影響，故非純粹之移民指標。',
 'irregular_stock': '不可跨國比較。各國推估方法、年度與定義均不相同。',
 'irregular_proxy_overstayers': '不可跨國比較。屬行政登記數，僅涵蓋已被登錄之逾期停留者。',
 'irregular_proxy_detections': '不可跨國比較，且屬執法事件之「流量」而非人口「存量」。'
                               '數值受查緝強度與該國在移民路線上的位置影響。',
}

# ---------------------------------------------------------------- correction reasons
REASON = {
 'Series was offset by one year: the input workbook carried the Eurostat value for year Y+1 '
 'under year Y. Replaced with the correct year-aligned value.':
   '整組序列位移一年：原始工作表將 Eurostat 之 Y+1 年數值誤置於 Y 年。已更正為年度對齊之正確數值。',
 'Value absent from the input workbook; added from the official ISMU series.':
   '原始工作表缺漏此數值；依 ISMU 官方序列補入。',
 'Input used the Pew Research estimate for this year while every other year in the series used '
 'ISMU. Replaced with ISMU so the Italian series has one consistent method.':
   '原始工作表此年度採用 Pew Research 推估值，但序列其餘年度均採 ISMU。'
   '已改用 ISMU，使義大利序列採一致之推估方法。',
}
REASON_TWN_PREFIX = 'The input column mixed two incompatible Taiwanese measures'
REASON_TWN_ZH = ('原始欄位在不同年度混用兩種不相容的臺灣統計：2011–2013 與 2019–2022 年為'
                 '勞動部「失聯移工」（屬部分集合），2014–2018 年為移民署「逾期停留・居留」，'
                 '導致 2014 年出現虛假的躍升、2019 年出現虛假的下降。'
                 '本欄位現僅保留移民署逾期停留・居留數；勞動部數值已移至 '
                 'irregular_proxy_absconded_workers 欄位。')


def reason_zh(text):
    t = str(text)
    if t.startswith(REASON_TWN_PREFIX):
        return REASON_TWN_ZH
    return REASON.get(t, t)


# ---------------------------------------------------------------- generic UI
T = {
 # page furniture
 'access_prefix': {'en': 'Replication &amp; source archive · accessed ',
                   'zh': '重製與來源存檔 · 取得日期 '},
 'retrieved': {'en': 'Retrieved ', 'zh': '取得日期 '},
 'back_to': {'en': '&larr; back to ', 'zh': '&larr; 返回 '},
 # index
 'idx_title': {'en': 'Migration and population data for 40 countries, 2010–2022',
               'zh': '40 國移民與人口資料，2010–2022 年'},
 'idx_lede': {'en': 'Every number in the accompanying dataset is traced here to a source file you '
                    'can download. Statistical-agency APIs were captured as raw response '
                    'snapshots; web pages were mirrored as PDF and full-page screenshots on the '
                    'access date. Nothing in this archive depends on a live external server still '
                    'being available.',
              'zh': '本資料集中的每一個數字，都可在此追溯到一份可下載的來源檔案。'
                    '各統計機構 API 的原始回應已完整保存；網頁來源則於取得當日製作 PDF 鏡像'
                    '與整頁截圖。本存檔的任何內容都不依賴外部伺服器是否仍然運作。'},
 'stat_checked': {'en': 'values re-derived from live sources', 'zh': '筆數值自線上來源重新導出'},
 'stat_exact': {'en': 'matched the source exactly', 'zh': '與來源完全一致'},
 'stat_files': {'en': 'source files archived', 'zh': '份來源檔案已存檔'},
 'stat_mb': {'en': 'of mirrored evidence', 'zh': '的鏡像佐證資料'},
 'stat_countries': {'en': 'countries, 13 years each', 'zh': '個國家，各 13 年'},
 'stat_corr': {'en': 'values corrected', 'zh': '筆數值已更正'},
 'stat_ev': {'en': 'per-variable evidence pages, each with a PDF extract',
             'zh': '個別變項佐證頁，各附 PDF 摘錄'},
 'start_here': {'en': 'Start here', 'zh': '從這裡開始'},
 'start_sub': {'en': 'Four routes into the archive, depending on what you want to check.',
               'zh': '依查核目的，提供四條進入本存檔的路徑。'},
 'card_data_h': {'en': 'The dataset', 'zh': '資料集'},
 'card_data_p': {'en': 'The verified panel as Excel and CSV, with a quality grade on every value, '
                       'plus the codebook and the two original input workbooks.',
                 'zh': '已查證之 panel 資料（Excel 與 CSV），每一數值均標註品質等級，'
                       '並附變項說明書及兩份原始輸入工作表。'},
 'card_data_go': {'en': 'Data files &rarr;', 'zh': '資料檔案 &rarr;'},
 'card_ctry_h': {'en': 'Country by country', 'zh': '逐國查核'},
 'card_ctry_p': {'en': 'One page per country: the data, the check against the live source, and '
                       'every source document held locally for that country.',
                 'zh': '每國一頁：該國資料、與線上來源的核對結果，以及本站所保存的所有來源文件。'},
 'card_ctry_go': {'en': '40 countries &rarr;', 'zh': '40 個國家 &rarr;'},
 'card_src_h': {'en': 'Every source', 'zh': '所有資料來源'},
 'card_src_p': {'en': 'The complete source register: 78 country&ndash;source citations, 76 of them '
                      'archived here, each linking to both the original URL and the local copy.',
                'zh': '完整的來源清冊：78 筆國家&ndash;來源引用，其中 76 筆已存檔於本站，'
                      '每筆均同時連結原始網址與本站備份。'},
 'card_src_go': {'en': 'Source register &rarr;', 'zh': '來源清冊 &rarr;'},
 'card_ver_h': {'en': 'What was checked', 'zh': '查證了什麼'},
 'card_ver_go': {'en': 'Verification &rarr;', 'zh': '查證紀錄 &rarr;'},
 'reliab_h': {'en': 'How reliable is each value?', 'zh': '每個數值的可靠程度如何？'},
 'grade_col': {'en': 'Grade', 'zh': '等級'}, 'mean_col': {'en': 'Meaning', 'zh': '定義'},
 'values_col': {'en': 'Values', 'zh': '數值數'}, 'share_col': {'en': 'Share', 'zh': '占比'},
 'd_note': {'en': '<strong>No values are graded D.</strong> The six that were &mdash; '
                  "Korea's 2010–2015 overstayer figures, whose only cited source had gone "
                  'offline &mdash; were re-sourced to the Ministry of Justice Immigration '
                  'Statistical Yearbook and open-data series. Five matched exactly; the 2015 '
                  'value proved to be a 31 August snapshot in an otherwise year-end series and '
                  'was corrected to the official 214,168.',
            'zh': '<strong>目前已無評為 D 級的數值。</strong>原先的 6 筆&mdash;&mdash;'
                  '南韓 2010–2015 年逾期停留人數，其唯一來源已離線&mdash;&mdash;'
                  '已改採法務部《出入國·外國人政策統計年報》與政府開放資料之官方序列。'
                  '其中 5 筆完全一致；2015 年該筆經查為 8 月 31 日之時點數，'
                  '與其餘年度之年底數不一致，已更正為官方年底數 214,168。'},
 'derived_mark': {'en': '≈', 'zh': '≈'},
 'derived_tip': {'en': 'Derived value: %s. Published source range: %s. Use the range, not this midpoint, for any claim about level.',
                 'zh': '推導值：%s。來源公布區間：%s。若要陳述水準，請引用區間而非此中點值。'},
 'derived_legend': {'en': 'A number marked %s is <strong>derived</strong> from its source rather than published by it — for example the midpoint of a published range. The source’s own range is shown on the evidence page.',
                    'zh': '標示 %s 的數字為<strong>推導值</strong>，並非來源直接公布之數字——例如公布區間的中點。來源本身的區間載於佐證頁。'},
 'derived_h': {'en': 'Derived value', 'zh': '推導值'},
 'derived_range_label': {'en': 'Published source range', 'zh': '來源公布區間'},
 'derivation_label': {'en': 'How it was derived', 'zh': '推導方式'},
 'finding_h': {'en': 'The substantive finding', 'zh': '實質發現'},
 'finding_sub': {'en': 'Verification was not a formality. It changed the data.',
                 'zh': '查證並非形式作業，它實際改動了資料。'},
 'evlink_h': {'en': 'Every number is a link', 'zh': '每個數字都是連結'},
 'evlink_sub': {'en': 'On each country page, the Panel data table is fully clickable.',
                'zh': '在每個國家頁面上，Panel 資料表格的每個數字都可點選。'},
 'author_h': {'en': 'Authorship', 'zh': '作者'},
 'author_p': {'en': 'This archive is joint work of <a href="https://raymond.cph.ntu.edu.tw/" '
                    'rel="noopener"><strong>Prof. Raymond Kuo</strong></a>, National Taiwan '
                    'University, and <strong>Claude</strong> (Anthropic).',
              'zh': '本存檔為國立臺灣大學<a href="https://raymond.cph.ntu.edu.tw/" '
                    'rel="noopener"><strong>郭柏秀教授</strong></a>與 <strong>Claude</strong>'
                    '（Anthropic）之共同成果。'},
 'using_h': {'en': 'Using this archive', 'zh': '如何使用本存檔'},
 'using_sub': {'en': 'For editors and reviewers.', 'zh': '供編輯與審查委員參考。'},
 # countries index
 'ctry_idx_title': {'en': 'Country pages', 'zh': '各國頁面'},
 'ctry_idx_lede': {'en': 'Each page shows that country\'s data with a grade on every value, the '
                         'result of checking it against the live source, and every source document '
                         'archived locally for it.',
                   'zh': '每一頁呈現該國資料（每個數值均標註品質等級）、與線上來源的核對結果，'
                         '以及本站為該國所保存的全部來源文件。'},
 'filter_ph': {'en': 'Filter countries…', 'zh': '篩選國家…'},
 'n_countries': {'en': 'countries', 'zh': '個國家'},
 'values_word': {'en': 'values', 'zh': '筆數值'},
 'files_word': {'en': 'files', 'zh': '份檔案'},
 # country page
 'ctry_eyebrow': {'en': ' &middot; country archive', 'zh': ' &middot; 國家存檔'},
 'ctry_lede': {'en': 'Data, verification result and every archived source document for %s, '
                     '2010&ndash;2022. All sources retrieved ',
               'zh': '%s 2010&ndash;2022 年之資料、查證結果，以及全部已存檔之來源文件。'
                     '所有來源取得日期為 '},
 'panel_h': {'en': 'Panel data', 'zh': 'Panel 資料'},
 'panel_sub': {'en': '<strong>Every number below is a link.</strong> Click a value, or the grade '
                     'pill beside it, to open the evidence for that exact figure &mdash; the '
                     'source, the query URL, what it was checked against, and the snapshots, PDF '
                     'mirrors and files held in this archive that support it. Grades: ',
               'zh': '<strong>以下每個數字都是連結。</strong>點選數值或其旁的等級標記，'
                     '即可開啟該筆數字的佐證頁——包含來源、查詢網址、核對對象，'
                     '以及本存檔中支持該數值的截圖、PDF 鏡像與檔案。等級說明：'},
 'year': {'en': 'Year', 'zh': '年度'},
 'ver_h': {'en': 'Verification', 'zh': '查證'},
 'ver_ok': {'en': '<strong>%d of %d</strong> machine-checkable values for %s reproduced the live '
                  'source exactly.',
            'zh': '%s 可機械核對之數值中，有 <strong>%d／%d</strong> 筆與線上來源完全一致。'},
 'ver_none': {'en': 'No machine-readable bulk source applies to this country.',
              'zh': '本國無適用之機器可讀批次資料來源。'},
 'ver_disc': {'en': '<strong>%d discrepancies were found in the input workbook and '
                    'corrected.</strong> Input value against the live source:',
              'zh': '<strong>於原始工作表中發現 %d 筆不一致並已更正。</strong>'
                    '原始數值與線上來源對照如下：'},
 'col_input': {'en': 'Input workbook', 'zh': '原始工作表'},
 'col_live': {'en': 'Live source', 'zh': '線上來源'},
 'col_diff': {'en': 'Difference', 'zh': '差異'},
 'col_source': {'en': 'Source', 'zh': '來源'},
 'col_var': {'en': 'Variable', 'zh': '變項'},
 'col_years': {'en': 'Years', 'zh': '年度範圍'},
 'col_value': {'en': 'Value', 'zh': '數值'},
 'col_was': {'en': 'Was', 'zh': '原值'},
 'col_now': {'en': 'Now', 'zh': '更正後'},
 'col_why': {'en': 'Why', 'zh': '更正理由'},
 'col_cov': {'en': 'Coverage', 'zh': '涵蓋率'},
 'col_trend': {'en': 'Usable as a trend?', 'zh': '可否作為趨勢使用？'},
 'col_country': {'en': 'Country', 'zh': '國家'},
 'col_status': {'en': 'Status', 'zh': '狀態'},
 'col_archived': {'en': 'Archived copies', 'zh': '本站存檔'},
 'col_refdate': {'en': 'Reference date', 'zh': '基準日'},
 'col_verif': {'en': 'Verification', 'zh': '查證結果'},
 'corr_h': {'en': 'Corrections applied', 'zh': '已套用之更正'},
 'dq_h': {'en': 'Data quality by variable', 'zh': '各變項資料品質'},
 'dq_sub': {'en': 'Coverage, and whether this series can carry a trend for this country.',
            'zh': '涵蓋率，以及該序列於本國是否足以支撐趨勢分析。'},
 'src_h': {'en': 'Sources', 'zh': '資料來源'},
 'src_sub': {'en': 'Each row links to the original URL and to the copy held in this archive. API '
                   'sources link to the raw response captured on ',
             'zh': '每一列同時連結原始網址與本存檔之備份。API 來源連結至擷取日為以下日期之原始回應：'},
 'allfiles_h': {'en': 'All archived files', 'zh': '本國全部存檔檔案'},
 'allfiles_sub': {'en': '%d files in ', 'zh': '共 %d 份檔案，位於 '},
 'nodocs': {'en': 'No country-specific documents &mdash; every source for this country is a bulk '
                  'statistical API, archived under evidence/api/.',
            'zh': '本國無專屬文件來源——所有來源皆為批次統計 API，已存檔於 evidence/api/。'},
 'dl_csv': {'en': 'this country as CSV', 'zh': '本國資料 CSV'},
 'dl_check': {'en': 'value-by-value check', 'zh': '逐筆核對表'},
 'dl_manifest': {'en': 'source manifest', 'zh': '來源清單'},
 'dl_readme': {'en': 'country README', 'zh': '國家說明檔'},
 # evidence page
 'ev_eyebrow': {'en': ' &middot; evidence for one variable', 'zh': ' &middot; 單一變項佐證'},
 'ev_lede': {'en': 'Every value behind this series, what it was checked against, and every file '
                   'held in this archive that supports it. Retrieved ',
             'zh': '本序列的每一筆數值、其核對對象，以及本存檔中支持該數值的全部檔案。取得日期 '},
 'ev_values': {'en': 'Values', 'zh': '數值'},
 'ev_defnote': {'en': '<strong>Definition note.</strong> ', 'zh': '<strong>定義說明。</strong>'},
 'ev_confirm': {'en': '<strong>How this was confirmed.</strong> ',
                'zh': '<strong>確認方式。</strong>'},
 'ev_src_h': {'en': 'Source', 'zh': '來源'},
 'ev_src_sub': {'en': 'The query or document URL this series was taken from.',
                'zh': '本序列所依據之查詢網址或文件網址。'},
 'ev_arch_h': {'en': 'Archived evidence for these numbers', 'zh': '支持這些數字的存檔佐證'},
 'ev_arch_sub': {'en': 'Every file below is stored in this archive and downloads from this site '
                       '&mdash; no external server is involved.',
                 'zh': '以下每份檔案均儲存於本存檔並自本站下載，不涉及任何外部伺服器。'},
 'ev_pdf': {'en': 'PDF extract of this table', 'zh': '本表之 PDF 摘錄'},
 'ev_country_csv': {'en': 'country data (CSV)', 'zh': '國家資料（CSV）'},
 'ev_check_csv': {'en': 'value check (CSV)', 'zh': '核對表（CSV）'},
 'art_pubpdf': {'en': 'Publisher page (PDF)', 'zh': '發布機構頁面（PDF）'},
 'art_pubpng': {'en': 'Publisher page (screenshot)', 'zh': '發布機構頁面（截圖）'},
 'art_raw': {'en': 'Raw API response', 'zh': 'API 原始回應'},
 'art_oecdxml': {'en': 'OECD dataflow definition (XML)', 'zh': 'OECD 資料流定義（XML）'},
 'art_sdmx': {'en': 'Raw SDMX response (%s)', 'zh': 'SDMX 原始回應（%s）'},
 'art_doc': {'en': 'Archived source document (%s, %s)', 'zh': '存檔來源文件（%s，%s）'},
 'art_pdfmirror': {'en': 'PDF mirror of source page', 'zh': '來源頁面 PDF 鏡像'},
 'art_screenshot': {'en': 'Screenshot of source page', 'zh': '來源頁面截圖'},
}


def t(key, lang):
    v = T.get(key)
    if v is None:
        return key
    return v.get(lang, v.get('en', key))
