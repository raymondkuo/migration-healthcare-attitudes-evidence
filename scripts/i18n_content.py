# -*- coding: utf-8 -*-
"""Traditional Chinese (Taiwan) translations of the long-form content:
known issues, codebook, and the prose on the Sources / Data / Verification /
Methods pages."""

# ---------------------------------------------------------------- known issues
SEV = {'RESOLVED': '已解決', 'HIGH': '高', 'MEDIUM': '中', 'LOW': '低', 'INFO': '說明'}

SCOPE = {
 'Switzerland, Portugal, Sweden': '瑞士、葡萄牙、瑞典',
 'Sweden': '瑞典', 'Taiwan': '臺灣', 'Italy': '義大利', 'Korea': '南韓',
 'Switzerland': '瑞士', 'Japan': '日本', 'all': '全部',
 'immigration_country_year_2010_2022.xlsx': 'immigration_country_year_2010_2022.xlsx',
 'Israel, Bulgaria, France, Turkey, USA, Poland, China, Netherlands':
     '以色列、保加利亞、法國、土耳其、美國、波蘭、中國、荷蘭',
 'Turkey, Czechia, Slovakia, Portugal, Germany': '土耳其、捷克、斯洛伐克、葡萄牙、德國',
 'EU/EFTA': '歐盟／歐洲自由貿易聯盟',
 'Eurostat / OECD countries': 'Eurostat／OECD 國家',
}

# keyed by row index of data/known_issues.csv (fixed content)
ISSUES_ZH = {
 0: ('於 migration_population_panel_40countries_2010-2022.xlsx 中，這三國的 Eurostat 查獲人次序列'
     '整體位移一年：Y+1 年公布之數值被記錄於 Y 年，且真正的 2010 年數值付之闕如。',
     '2026-08-17 重新查詢 Eurostat migr_eipre。例如瑞典：工作表 2013 年為 72,835，'
     '但 Eurostat 2013 年為 24,400、2014 年為 72,835。另一份工作表 '
     'immigration_country_year_2010_2022.xlsx 則記載正確。',
     '已更正：39 筆數值全部替換為年度對齊之 Eurostat 數值。'),
 1: ('原始變項說明書指出瑞典查獲人次序列的斷點為「2013 年：72,835 → 2014 年：1,445」，'
     '此係上述位移一年所導致的假象。',
     'Eurostat migr_eipre：2013 年 = 24,400；2014 年 = 72,835；2015 年 = 1,445。',
     '已更正：斷點實際落在 2014 至 2015 年之間，而非 2013 至 2014 年。'),
 2: ('單一欄位混用兩種不相容的統計：2011–2013 與 2019–2022 年為勞動部「失聯移工」'
     '（屬部分集合），2014–2018 年為內政部移民署「逾期停留／居留」。'
     '若當作時間序列解讀，會在 2014 年產生虛假的 +65% 躍升，2019 年產生虛假的 −47% 下降。',
     '原始工作表本身的來源註記；且 immigration_country_year_2010_2022.xlsx 於 2012–2021 年'
     '一致採用移民署序列。',
     '已更正：本欄位現僅保留移民署逾期停留／居留數（2012–2021）；'
     '勞動部數值已移至獨立欄位 irregular_proxy_absconded_workers。'),
 3: ('2010–2013 年缺漏（儘管 ISMU 有公布），且 2014 年採用 Pew 推估值而其餘年度採用 ISMU，'
     '導致單一序列混用兩種推估方法。',
     'Fondazione ISMU，《Stime stranieri irregolari 1991-2021》（2022 年 5 月更新），'
     '已下載至 countries/ITA_Italy/sources/。',
     '已更正：義大利現為 2010–2021 年一致之 ISMU 序列。'
     'Pew 推估值仍保留於 Irregular_estimates_all 工作表。'),
 4: ('該工作表將五種概念上不同的統計置於同一欄位：274 筆 Eurostat 年度查緝查獲數（屬「流量」），'
     '外加 8 國的逾期停留登記數與推估之無證人口（屬「存量」）。',
     'Sources 工作表 S3–S12；另見 verification/audit_issues.csv。',
     '未採用。最終 panel 將三種統計分置於三個獨立欄位，且絕不可合併使用。'),
 5: ('目前不存在可跨國比較的無證移民人口統計。irregular_stock 僅涵蓋 13／40 國、'
     '逾期停留 5／40 國、查獲人次 25／40 國，且三者不可相加亦不可互換。',
     'Coverage 工作表；verification/audit_issues.csv。',
     '至多僅能作為順序尺度的「議題顯著性」指標。若需跨國迴歸自變項，'
     '建議改用 foreign_nationals_pct_pop。'),
 6: ('兩份原始工作表的人口數不一致，因其一採用 UN WPP 2024、另一採用世界銀行 WDI。'
     '以色列差異 −4.1%、保加利亞 +3.2%、法國 −2.5%。',
     '520 個國家—年度中有 427 個不一致；其中 26 個差異超過 3%。',
     '兩組序列並列保留（population = 世界銀行；population_un_wpp2024 = UN WPP），'
     '差距列於 population_wb_vs_unwpp_pct。請擇一使用並貫徹於所有國家。'),
 7: ('UN DESA 移民存量與 OECD／Eurostat 外國出生人口序列差異極大'
     '（土耳其 +144%、捷克 +55%、斯洛伐克 +42%、葡萄牙 −18%）。',
     '就 110 個重疊之國家—年度進行跨檔比對。',
     '兩者不可混用。土耳其尤為明顯：UN DESA 涵蓋受臨時保護之敘利亞人，OECD 序列則否。'),
 8: ('2010–2015 年數值僅依據單一次級來源（韓國警察大學出版品），該網站現已無回應，'
     '因此無法與任何來源核對。',
     'press.police.ac.kr 無回應；亦無網頁典藏備份可用'
     '（本次作業期間 Wayback Machine 回傳 503）。',
     '予以保留但評為 D 級。2021 與 2022 年數值已對照線上法務部表格完全查證'
     '（388,700 與 411,270）。'),
 9: ('連結失效：所引用之 SEM PDF（ber-sanspapiers-2015-d.pdf）現回傳 404。',
     '2026-08-17 以多種網址型式檢查。',
     '76,000 之推估值由 SRF 對 2016 年 4 月 25 日 SEM 研究發布之報導佐證，'
     '已存至 countries/CHE_Switzerland/sources/。'
     '另請注意該研究本身給出的區間為 58,000–105,000。'),
 10: ('ismu.org 對所有自動化用戶端及真實瀏覽器均回傳 HTTP 403。',
      '2026-08-17 自兩種用戶端檢查。',
      '改以 ISMU 自行發布之機器可讀序列替代，該序列完全確認了每一筆義大利數值。'),
 11: ('一個引用的鏡像站（nisshinkyo.org）回傳 404。',
      '2026-08-17 檢查。',
      '無影響：該檔僅重複出入國在留管理廳 2014 年之數值，而該廳的主要來源已成功下載。'),
 12: ('2015 年（德國 +193%、匈牙利 +655%、奧地利 +161%）與 2021–2022 年'
      '（義大利 +304%、奧地利 +175%、克羅埃西亞 +224%）出現的大幅跳升為真實變動，'
      '反映 2015 年移民危機與 2021–22 年巴爾幹路線及烏克蘭人口移動，並非資料錯誤。',
      '所有數值均與線上 Eurostat 完全一致。',
      '已載明。請勿視為序列斷點。'),
 13: ('Eurostat 與 OECD 之存量統計係以 1 月 1 日為基準，因此標示為 Y 年的列，'
      '描述的是 Y−1 年 12 月 31 日的狀態。',
      'Eurostat migr_pop1ctz／migr_pop3ctb 之後設資料。',
      '若需與年中蒐集之調查資料對應，請考慮落後一期，或改用 ref_date 各欄位。'),
}

# ---------------------------------------------------------------- codebook
# keyed by row index of data/codebook.csv
CODEBOOK_ZH = {
 0: ('國家識別碼。', ''),
 1: ('該國是否納入各期 ISSP／ISPSS 調查。', ''),
 2: ('曆年，2010–2022。', ''),
 3: ('總居住人口。39 國採世界銀行 WDI SP.POP.TOTL 年中人口；臺灣為內政部年底戶籍登記人口。',
     '已查證：507 筆世界銀行數值全部與線上 API 完全一致。'),
 4: ('替代之人口數，來自 UN WPP 2024，為 7 月 1 日總人口，涵蓋全部 40 國（含臺灣）。',
     '已查證：520 筆數值全部與線上 UN WPP 2024 檔案完全一致。'),
 5: ('兩組人口序列之百分比差距。', '可用以檢視人口分母之選擇在何處會造成實質影響。'),
 6: ('出生於報告國以外之居住人口。', '已包含歸化取得公民身分者，故幾乎在所有國家都高於外國籍人口。'),
 7: ('持有外國國籍之居住人口，含有通報之無國籍者。',
     '概念上最接近「非本國籍」使用公費醫療之對象。建議作為跨國分析之主要自變項。'),
 8: ('推估之未經許可居留外國人數。', '較弱。僅 13／40 國有資料，各國推估方法不可比較。'),
 9: ('逾期停留者之行政登記數。', '較弱。僅 5／40 國有資料。屬登記數而非模型推估之存量。'),
 10: ('僅臺灣：勞動部統計之失聯移工人數。', '屬逾期停留者之部分集合。獨立列出以免被誤讀為同一序列。'),
 11: ('該年度查獲之非法居留第三國國民人次。',
      '屬執法事件之「流量」而非人口「存量」，亦非人數統計——同一人可能被查獲多次。'),
 12: ('該變項除以總人口（比例，非百分比）。', '已於更正後重新計算。'),
 13: ('每千名居民之查獲人次。', '因原始流量數與存量占比不可比較，故另行提供。'),
 14: ('底層測量之基準日。', 'Eurostat／OECD 存量為 1 月 1 日；臺灣與南韓為 12 月 31 日；日本為 1 月 1 日。'),
 15: ('各數值之出處資訊。', ''),
 16: ('該儲存格之資料品質等級。A＝自機器可讀之官方來源重新計算並完全一致，'
      '或於本次查證中依該來源更正。B＝經閱讀所取得之來源文件確認。'
      'C＝已取得來源文件，但該數值為推估值，無法以機械方式重新導出。'
      'D＝所引用之來源已無法取得。', ''),
}

CODEBOOK_HDR = {'en': ['Variable', 'Definition', 'Caution / verification'],
                'zh': ['變項', '定義', '注意事項／查證情形']}

# ---------------------------------------------------------------- page prose
P = {}

P['sources'] = {
 'eyebrow': {'en': 'Source register', 'zh': '來源清冊'},
 'h1': {'en': 'Every source, and its archived copy', 'zh': '所有資料來源及其存檔備份'},
 'lede': {'en': 'Two kinds of source feed this dataset. Bulk statistical APIs were captured as raw '
                'response payloads. Individual documents and web pages were downloaded, and where '
                'the source is a web page it was additionally rendered to PDF and to a full-page '
                'screenshot. Everything was captured on ',
          'zh': '本資料集有兩類來源。批次統計 API 以原始回應內容完整保存；'
                '個別文件與網頁則直接下載，若來源為網頁，另製作 PDF 與整頁截圖。'
                '全部擷取日期為 '},
 'api_h': {'en': 'Bulk statistical sources (API snapshots)', 'zh': '批次統計來源（API 快照）'},
 'api_sub': {'en': 'These %d payloads are the evidence behind %s of the %s verified values. Each '
                   'file is exactly what the publisher’s server returned; the query URL that '
                   'produced it is given so the request can be repeated.',
             'zh': '這 %d 份回應內容即為 %s／%s 筆已查證數值的佐證。'
                   '每份檔案均為發布機構伺服器回傳的原始內容；並附上產生該回應的查詢網址，以便重複驗證。'},
 'pub_h': {'en': 'Publisher pages for the bulk sources', 'zh': '批次來源之發布機構頁面'},
 'pub_sub': {'en': 'A raw JSON payload is precise but not readable. So the publishers’ own '
                   'dataset pages — the human-facing definition of each series — were '
                   'also mirrored as PDF and screenshot on ACCESS, giving the bulk API sources the '
                   'same kind of visual evidence the document sources have.',
             'zh': 'JSON 原始回應雖精確，卻不易閱讀。因此各發布機構自身的資料集頁面'
                   '——亦即各序列面向人類讀者的定義說明——亦於 ACCESS 製作 PDF 與截圖鏡像，'
                   '使批次 API 來源具備與文件來源同等的視覺佐證。'},
 'ev_h': {'en': 'Per-variable evidence pages', 'zh': '各變項佐證頁'},
 'ev_sub': {'en': 'Beyond the source-level mirrors, every country&times;variable series has its own '
                  'evidence page and a PDF extract listing each year’s value, its grade, what '
                  'it was checked against and every archived file behind it. These are reached by '
                  'clicking any number in a country’s Panel data table.',
            'zh': '除來源層級的鏡像外，每一組國家&times;變項序列都有專屬佐證頁與 PDF 摘錄，'
                  '列出各年度數值、品質等級、核對對象，以及其背後的全部存檔檔案。'
                  '點選任一國家 Panel 資料表中的任何數字即可進入。'},
 'ev_count': {'en': '156 evidence pages · 156 PDF extracts', 'zh': '156 個佐證頁 · 156 份 PDF 摘錄'},
 'doc_h': {'en': 'Document and web-page sources', 'zh': '文件與網頁來源'},
 'doc_sub': {'en': 'Beyond the bulk APIs, the two workbooks cite <strong>%d distinct '
                   'country&ndash;source citations</strong> across %d URLs. <strong>%d of %d</strong> '
                   'are held in this archive; the 2 that are not are named below. Use the filter to '
                   'find a country, a publisher or a URL.',
             'zh': '除批次 API 外，兩份工作表另引用 <strong>%d 筆不重複的國家&ndash;來源</strong>，'
                   '共 %d 個網址。其中 <strong>%d／%d</strong> 已存檔於本站；'
                   '未能存檔的 2 筆列於下方。可使用篩選欄查找國家、發布機構或網址。'},
 'filter_ph': {'en': 'Filter by country, source or URL…', 'zh': '依國家、來源或網址篩選…'},
 'of_sources': {'en': 'of %d sources', 'zh': '／%d 筆來源'},
 'fail_h': {'en': 'Sources that could not be archived', 'zh': '無法存檔的來源'},
 'fail_note': {'en': '<strong>Two of the %d country&ndash;source citations could not be retrieved '
                     'by any means.</strong><br>\n'
                     '<em>press.police.ac.kr</em> — the Korean National Police University '
                     'publication behind Korea’s 2010–2015 overstayer figures. The host '
                     'does not respond and no web archive copy was available. Those six values are '
                     'graded D.<br>\n<em>nisshinkyo.org</em> — a mirror of a Japanese Immigration '
                     'Services Agency table, now 404. No impact: it duplicated a figure whose '
                     'primary ISA source was retrieved successfully.',
               'zh': '<strong>%d 筆國家&ndash;來源引用中，有 2 筆無法以任何方式取得。</strong><br>\n'
                     '<em>press.police.ac.kr</em>——南韓 2010–2015 年逾期停留數所依據的'
                     '韓國警察大學出版品。該網站無回應，亦無網頁典藏備份，該 6 筆數值評為 D 級。<br>\n'
                     '<em>nisshinkyo.org</em>——日本出入國在留管理廳表格的鏡像，現已 404。'
                     '無影響：該檔僅重複一筆數值，其管理廳原始來源已成功取得。'},
 'fail_p': {'en': 'Three further sources block automated and browser access entirely '
                  '(<em>ismu.org</em>) or have moved (<em>sem.admin.ch</em>). In each case an '
                  'equivalent or better source was located and archived instead, and it confirmed '
                  'the values. See ',
            'zh': '另有三個來源完全封鎖自動化與瀏覽器存取（<em>ismu.org</em>）或已更動網址'
                  '（<em>sem.admin.ch</em>）。各案均另尋得同等或更佳之來源並存檔，'
                  '且均確認了原數值。詳見'},
 'ver_link': {'en': 'Verification', 'zh': '查證紀錄'},
 'col_publisher': {'en': 'Publisher', 'zh': '發布機構'},
 'col_dataset': {'en': 'Dataset', 'zh': '資料集'},
 'col_datasetpage': {'en': 'Dataset page', 'zh': '資料集頁面'},
 'col_query': {'en': 'Query URL used', 'zh': '所使用之查詢網址'},
 'col_bytes': {'en': 'Bytes', 'zh': '位元組'},
 'col_rawsnap': {'en': 'Raw snapshot', 'zh': '原始快照'},
 'col_url': {'en': 'URL', 'zh': '網址'},
 'col_mirror': {'en': 'Archived mirror', 'zh': '存檔鏡像'},
 'tag_archived': {'en': 'archived', 'zh': '已存檔'},
 'tag_recovered': {'en': 'recovered', 'zh': '已救回'},
 'tag_screenshot': {'en': 'screenshot', 'zh': '截圖'},
 'tag_substituted': {'en': 'substituted', 'zh': '已替代'},
 'tag_notret': {'en': 'not retrievable', 'zh': '無法取得'},
 'tag_notcap': {'en': 'not captured', 'zh': '未擷取'},
}

P['data'] = {
 'eyebrow': {'en': 'Downloads', 'zh': '下載'},
 'h1': {'en': 'Data files', 'zh': '資料檔案'},
 'lede': {'en': 'The dataset and every supporting table, as Excel and CSV. All files are UTF-8 '
                'with a BOM so they open cleanly in Excel, including the Chinese, Japanese, Korean '
                'and Hebrew source names.',
          'zh': '資料集及全部佐證表格，提供 Excel 與 CSV 格式。所有檔案採 UTF-8 with BOM 編碼，'
                '可在 Excel 中正確開啟，包含中文、日文、韓文與希伯來文之來源名稱。'},
 'main_h': {'en': 'The dataset', 'zh': '資料集'},
 'main_sub': {'en': 'Everything on this website — every count, grade and correction — refers to '
                    '<strong>FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx</strong>. It '
                    'is the only workbook whose every value can be traced to a source file held in '
                    'this archive.',
              'zh': '本網站所有內容——每一項統計、等級與更正——均指向 '
                    '<strong>FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx</strong>。'
                    '這是唯一一份每個數值都能追溯到本存檔內來源檔案的工作表。'},
 'alt_h': {'en': 'A second workbook, included for completeness', 'zh': '第二份工作表（為求完整而附上）'},
 'alt_note': {'en': '<strong>This file is not the one the website documents.</strong> It was '
                    'produced by a separate compilation run. Its <em>Verification</em> sheet '
                    'reports 203 source rows, 192 of 203 snapshots and 750 of 750 values matched; '
                    'the figures for this archive are 160 distinct source URLs, 87 of 89 document '
                    'sources retrieved and 2,454 values checked. Its <em>Source Audit</em> and '
                    '<em>Folder Index</em> sheets also point at a folder layout '
                    '(<code>country_sources\\…</code>) that does not exist in this repository. Its '
                    'substantive conclusions agree with this archive’s; its counts are not '
                    'interchangeable with them.',
              'zh': '<strong>本檔案並非本網站所記載的那一份。</strong>'
                    '它由另一次獨立的彙編作業產生。其 <em>Verification</em> 工作表記載 203 筆來源、'
                    '192／203 份快照、750／750 筆數值一致；而本存檔的對應數字為 72 個不重複之'
                    '文件來源網址、76／78 筆國家—來源引用已存檔、2,454 筆數值已查證。'
                    '其 <em>Source Audit</em> 與 <em>Folder Index</em> 工作表所指向的資料夾結構'
                    '（<code>country_sources\\…</code>）在本存放庫中並不存在。'
                    '其實質結論與本存檔一致，但統計數字不可互換引用。'},
 'ctry_h': {'en': 'Per-country files', 'zh': '各國檔案'},
 'ctry_sub': {'en': 'Each country folder carries the same four files. Browse them from any ',
              'zh': '每個國家資料夾均包含相同的四份檔案。可自任一'},
 'ctry_sub2': {'en': ', or reach them directly at ', 'zh': '瀏覽，或直接前往 '},
 'ctry_link': {'en': 'country page', 'zh': '國家頁面'},
 'f_data': {'en': '&mdash; every observation for that country with its live-source check result',
            'zh': '&mdash; 該國每一筆觀察值及其與線上來源之核對結果'},
 'f_check': {'en': '&mdash; input workbook value against the live source value',
             'zh': '&mdash; 原始工作表數值與線上來源數值之對照'},
 'f_manifest': {'en': '&mdash; every cited source and how it was retrieved',
                'zh': '&mdash; 所有引用來源及其取得方式'},
 'f_readme': {'en': '&mdash; what was verified, and any discrepancy found',
              'zh': '&mdash; 查證內容，以及所發現的任何不一致'},
 'cb_h': {'en': 'Codebook', 'zh': '變項說明書'},
 'col_file': {'en': 'File', 'zh': '檔案'},
 'col_size': {'en': 'Size', 'zh': '大小'},
 'col_dl': {'en': 'Download', 'zh': '下載'},
 'orig_h': {'en': 'Original inputs, unmodified', 'zh': '原始輸入檔（未經修改）'},
 'orig_sub': {'en': 'The two workbooks this archive started from, kept exactly as supplied so that '
                    'every correction can be checked against the original.',
              'zh': '本存檔所依據的兩份原始工作表，完全依提供時的原貌保留，'
                    '以便逐項核對每一處更正。'},
}

P['verification'] = {
 'eyebrow': {'en': 'Verification record', 'zh': '查證紀錄'},
 'h1': {'en': 'What was checked, and what changed', 'zh': '查證了什麼，以及改動了什麼'},
 'lede': {'en': 'Every source was retrieved again on ACCESS and each value in the input workbooks '
                'was compared against it. This page reports the result in full, including the '
                'values that did not match.',
          'zh': '所有資料來源均於 ACCESS 重新取得，並將原始工作表中的每一筆數值與之比對。'
                '本頁完整呈現結果，包含未能一致的數值。'},
 'rate_h': {'en': 'Reproduction rate of the input workbooks, as received',
            'zh': '原始工作表（收到時）之重現率'},
 'rate_sub': {'en': 'This table records the comparison as it stood <strong>before any '
                    'correction</strong> — it is the audit trail, not the state of the published '
                    'data. Every discrepancy fell in one place: the Eurostat detections series for '
                    'three countries in one of the two input workbooks. All 39 were corrected; the '
                    're-test below shows the result.',
              'zh': '本表記錄的是<strong>更正前</strong>的比對結果——屬稽核軌跡，'
                    '而非目前已發布資料的狀態。所有不一致都集中於同一處：'
                    '兩份原始工作表其中之一，其三個國家的 Eurostat 查獲人次序列。'
                    '該 39 筆均已更正，重測結果見下表。'},
 're_h': {'en': 'Re-test after correction: the data this archive publishes',
          'zh': '更正後重測：本存檔目前發布之資料'},
 're_sub': {'en': 'The Eurostat detections series was re-queried live on %s and every value the '
                  'archive now publishes was compared against it again. The raw payload from that '
                  're-query is archived as '
                  '<code>evidence/api/eurostat_migr_eipre_REVERIFY_2026-08-17.json</code>.',
            'zh': '已於 %s 重新向 Eurostat 查詢查獲人次序列，並將本存檔目前發布的每一筆數值'
                  '再次與之比對。該次查詢之原始回應已存檔為 '
                  '<code>evidence/api/eurostat_migr_eipre_REVERIFY_2026-08-17.json</code>。'},
 're_result': {'en': '<strong>283 of 283 values reproduce the live source exactly — 100.0%, '
                     'across all 23 countries.</strong> The 39 values that failed the first test '
                     'were replaced with the year-aligned Eurostat figures and now match.',
               'zh': '<strong>283 筆數值全部與線上來源完全一致——100.0%，涵蓋全部 23 國。</strong>'
                     '首次測試未通過的 39 筆已替換為年度對齊之 Eurostat 數值，現已完全相符。'},
 'col_stage': {'en': 'Stage', 'zh': '階段'},
 'col_src': {'en': 'Source', 'zh': '來源'},
 'col_nchk': {'en': 'Values checked', 'zh': '已查證數值'},
 'col_exact': {'en': 'Exact', 'zh': '完全一致'},
 'col_rate': {'en': 'Rate', 'zh': '一致率'},
 'fulllog': {'en': 'full verification log (CSV)', 'zh': '完整查證紀錄（CSV）'},
 'corr_h': {'en': 'Corrections applied', 'zh': '已套用之更正'},
 'corr_sub': {'en': '%d values across %d countries. The original workbooks are kept unmodified on '
                    'the ', 'zh': '共 %d 筆數值，涵蓋 %d 個國家。原始工作表未經修改，保存於'},
 'corr_sub2': {'en': ' page so every change can be checked.', 'zh': '頁面，以便逐項查核每一處改動。'},
 'iss_h': {'en': 'Issues found', 'zh': '所發現的問題'},
 'iss_sub': {'en': 'Resolved issues first, then those that remain and must be carried into any '
                   'analysis.',
             'zh': '先列已解決者，其後為仍然存在、分析時必須一併納入考量的問題。'},
 'col_sev': {'en': 'Severity', 'zh': '嚴重度'},
 'col_scope': {'en': 'Scope', 'zh': '範圍'},
 'col_issue': {'en': 'Issue', 'zh': '問題'},
 'col_evid': {'en': 'Evidence', 'zh': '佐證'},
 'col_action': {'en': 'Action taken', 'zh': '已採取之處理'},
 'held_h': {'en': 'What held up', 'zh': '通過查證的部分'},
 'held_sub': {'en': 'Worth stating as plainly as the problems.', 'zh': '這些同樣值得如實載明。'},
 'held': {'en': ['All 520 UN WPP 2024 population values reproduced exactly.',
                 'All 507 World Bank population values reproduced exactly.',
                 'All 584 Eurostat foreign-born and foreign-national values reproduced exactly.',
                 'All 139 OECD International Migration Database values reproduced exactly.',
                 'All 274 Eurostat detections in input workbook 1 reproduced exactly &mdash; '
                 'including the three countries workbook 2 had wrong.',
                 'Workbook 2’s Panel sheet is perfectly consistent with its own audit trail: '
                 '1,690 values, zero mismatches, and every percentage column recomputes to '
                 'floating-point precision.',
                 'Korea 2021 and 2022 verified against the live Ministry of Justice table: '
                 '125,022 + 262,251 + 1,427 = <strong>388,700</strong> and 138,013 + 269,532 + '
                 '3,725 = <strong>411,270</strong>.',
                 'The Philippines 2020 figure verified against the PSA census release: '
                 '<strong>78,396</strong>.',
                 'Every Italian irregular-migration value verified against ISMU’s own '
                 'published series.'],
          'zh': ['520 筆 UN WPP 2024 人口數值全部完全重現。',
                 '507 筆世界銀行人口數值全部完全重現。',
                 '584 筆 Eurostat 外國出生與外國籍人口數值全部完全重現。',
                 '139 筆 OECD 國際移民資料庫數值全部完全重現。',
                 '原始工作表 1 之 274 筆 Eurostat 查獲人次全部完全重現'
                 '&mdash;&mdash;包含工作表 2 記載錯誤的那三個國家。',
                 '工作表 2 的 Panel 分頁與其自身稽核軌跡完全一致：1,690 筆數值、'
                 '零筆不符，且所有百分比欄位重新計算後均達浮點精度一致。',
                 '南韓 2021 與 2022 年已對照線上法務部表格查證：'
                 '125,022 + 262,251 + 1,427 = <strong>388,700</strong>；'
                 '138,013 + 269,532 + 3,725 = <strong>411,270</strong>。',
                 '菲律賓 2020 年數值已對照 PSA 普查發布查證：<strong>78,396</strong>。',
                 '義大利每一筆無證移民數值均已對照 ISMU 自行發布之序列查證。']},
}

P['methods'] = {
 'eyebrow': {'en': 'Methods', 'zh': '研究方法'},
 'h1': {'en': 'How this archive was built', 'zh': '本存檔的建置方式'},
 'lede': {'en': 'The procedure, the grading scheme, and the judgements a reader needs in order to '
                'decide how much weight each variable can carry.',
          'zh': '作業流程、品質分級標準，以及讀者判斷各變項可承載多少推論重量所需的資訊。'},
 'proc_h': {'en': 'Procedure', 'zh': '作業流程'},
 'proc': {'en': ['<strong>Catalogue.</strong> Every source reference was extracted from both input '
                 'workbooks: 171 references, 160 distinct URLs across 51 hosts.',
                 '<strong>Re-query.</strong> Each bulk statistical source was requested again and '
                 'the raw response saved unaltered. Each value in the workbooks was then '
                 'recomputed from that response and compared.',
                 '<strong>Retrieve.</strong> Every document source was downloaded into a '
                 'per-country folder. Where the first attempt was refused, a full browser header '
                 'set, then an interactive browser, then an equivalent official source were tried '
                 'in turn.',
                 '<strong>Snapshot.</strong> Every web-page source was rendered to PDF and to a '
                 'full-page screenshot. Each render was then validated by dumping the rendered DOM '
                 'and checking it against a list of bot-wall and block-page markers; any page that '
                 'had answered with an interstitial was re-rendered from the HTML copy archived '
                 'earlier the same day, and is labelled as such.',
                 '<strong>Audit.</strong> Internal consistency, derived columns, cross-file '
                 'agreement and year-on-year breaks were tested independently of the source check.',
                 '<strong>Correct and grade.</strong> Discrepancies traced to a demonstrable error '
                 'were corrected against the live source and itemised; every value was graded.',
                 '<strong>Make it traceable.</strong> One evidence page was generated for every '
                 'country&times;variable series &mdash; 156 in all &mdash; listing each '
                 'year&rsquo;s value, its grade, what it was checked against, and every archived '
                 'file supporting it. Each was also rendered to a PDF extract, so every number '
                 'exists in a fixed citable document as well as on a web page. Every value in '
                 'every country&rsquo;s Panel data table links to its own evidence.',
                 '<strong>Checksum.</strong> A SHA-256 hash was recorded for every file.'],
          'zh': ['<strong>建立清冊。</strong>自兩份原始工作表擷取所有來源引用：'
                 '171 筆引用、160 個不重複網址，分布於 51 個網域。',
                 '<strong>重新查詢。</strong>每一個批次統計來源均重新請求，原始回應原封保存。'
                 '再由該回應重新計算工作表中的每一筆數值並比對。',
                 '<strong>取得文件。</strong>所有文件來源均下載至各國資料夾。'
                 '若首次請求遭拒，則依序改以完整瀏覽器標頭、互動式瀏覽器、'
                 '以及同等之官方來源嘗試。',
                 '<strong>製作快照。</strong>所有網頁來源均轉製為 PDF 與整頁截圖。'
                 '每次轉製後再傾印其算繪後的 DOM，比對機器人牆與封鎖頁的特徵字串加以驗證；'
                 '凡回應為攔截頁者，改以當日稍早已存檔之 HTML 備份重新轉製，並明確標示。',
                 '<strong>稽核。</strong>另行獨立檢驗內部一致性、衍生欄位、跨檔一致性'
                 '與年度間斷點，不倚賴來源核對之結果。',
                 '<strong>更正與分級。</strong>可明確歸因於錯誤的不一致，'
                 '均依線上來源更正並逐項載明；所有數值均給予品質等級。',
                 '<strong>建立可追溯性。</strong>為每一組國家&times;變項序列產生一個佐證頁'
                 '&mdash;&mdash;共 156 個&mdash;&mdash;列出各年度數值、品質等級、核對對象，'
                 '以及支持該數值的全部存檔檔案。每頁另轉製為 PDF 摘錄，'
                 '使每個數字除網頁外亦存在於可引用的固定文件中。'
                 '每個國家 Panel 資料表中的每一筆數值，均連結至其專屬佐證。',
                 '<strong>校驗碼。</strong>為每一份檔案記錄 SHA-256 雜湊值。']},
 'grade_h': {'en': 'Grading scheme', 'zh': '品質分級標準'},
 'grade_sub': {'en': 'Grades describe how a value was checked, not how plausible it looks.',
               'zh': '等級描述的是該數值「如何被查證」，而非其「看起來是否合理」。'},
 'grade_full': {'en': {'A': 'Recomputed from a machine-readable official source and matched '
                            'exactly, or replaced during this verification with a value taken from '
                            'one.',
                       'B': 'Confirmed by reading the retrieved source document, including cases '
                            'where the published components had to be summed.',
                       'C': 'Source document retrieved and archived, but the value is a modelled or '
                            'survey-based estimate that cannot be mechanically re-derived from it.',
                       'D': 'The cited source could not be retrieved by any means, so the value '
                            'rests on the original compiler’s transcription alone.'},
                'zh': {'A': '自機器可讀之官方來源重新計算並完全一致，'
                            '或於本次查證中以該來源之數值替換。',
                       'B': '經閱讀所取得之來源文件確認，包含須將公布之分項加總者。',
                       'C': '已取得並存檔來源文件，但該數值為模型推估或調查推估值，'
                            '無法由該文件以機械方式重新導出。',
                       'D': '所引用之來源已無法以任何方式取得，故該數值僅能依賴'
                            '原編製者的轉錄。'}},
 'col_crit': {'en': 'Criterion', 'zh': '判準'},
 'weight_h': {'en': 'How much weight each variable can carry', 'zh': '各變項可承載的推論重量'},
 'col_cy': {'en': 'Country-years', 'zh': '國家—年度'},
 'col_ctries': {'en': 'Countries', 'zh': '國家數'},
 'col_verdict': {'en': 'Verdict', 'zh': '評斷'},
 'verdict': {'en': {'population': 'Strong. Use freely.',
                    'foreign_born': 'Strong, but includes naturalised citizens.',
                    'foreign_nationals': 'Strong, and conceptually the right variable for this study.',
                    'irregular_stock': 'Weak. Not comparable across countries.',
                    'irregular_proxy_overstayers': 'Weak. Register counts; they understate the true figure.',
                    'irregular_proxy_detections': 'Weakest. A flow of enforcement events, not a stock.'},
             'zh': {'population': '強。可放心使用。',
                    'foreign_born': '強，但已包含歸化取得公民身分者。',
                    'foreign_nationals': '強，且在概念上正是本研究所需之變項。',
                    'irregular_stock': '弱。不可跨國比較。',
                    'irregular_proxy_overstayers': '弱。屬登記數，會低估實際人數。',
                    'irregular_proxy_detections': '最弱。屬執法事件之流量，而非人口存量。'}},
 'rec_note': {'en': '<strong>Recommendation.</strong> Use <code>foreign_nationals_pct_pop</code> as '
                    'the main cross-national regressor. It is the population the survey question is '
                    'actually about, it covers 34 of 40 countries, and every value is graded A or '
                    'B. Use <code>foreign_born_pct_pop</code> as a robustness check, noting that it '
                    'includes naturalised citizens, who <em>are</em> nationals.',
              'zh': '<strong>建議。</strong>以 <code>foreign_nationals_pct_pop</code> '
                    '作為跨國分析的主要自變項。它正是調查題目所指涉的人口，涵蓋 40 國中的 34 國，'
                    '且每一筆數值均為 A 或 B 級。可用 <code>foreign_born_pct_pop</code> '
                    '進行穩健性檢驗，但須注意其已包含歸化者，而這些人<em>本身即為本國籍</em>。'},
 'warn_note': {'en': '<strong>Do not use any irregular-migration variable as a continuous '
                     'cross-national regressor.</strong> Stocks cover 10.6% of country-years, the '
                     'estimation methods are not comparable between countries, and detections are a '
                     'flow driven by enforcement intensity and by a country’s position on '
                     'migration routes. If irregular migration matters to the argument, treat it as '
                     'an ordinal salience indicator or exploit within-country variation only.',
               'zh': '<strong>請勿將任何無證移民變項作為跨國連續型自變項。</strong>'
                     '存量僅涵蓋 10.6% 的國家—年度，各國推估方法不可比較；'
                     '查獲人次則屬流量，受查緝強度與該國在移民路線上的位置驅動。'
                     '若論證確實需要無證移民，請將其視為順序尺度的議題顯著性指標，'
                     '或僅利用國家內部的變異。'},
 'caut_h': {'en': 'Two cautions to carry into the analysis', 'zh': '分析時須留意的兩點'},
 'caut': {'en': ['<strong>Reference dates differ.</strong> Eurostat and OECD stocks are measured at '
                 '1 January, so the row labelled year <em>Y</em> describes 31 December of '
                 '<em>Y&minus;1</em>. Taiwan and Korea are year-end; Japan is 1 January. The '
                 '<code>*_ref_date</code> columns carry this per value.',
                 '<strong>Choose one population denominator.</strong> Both World Bank '
                 '(<code>population</code>) and UN WPP 2024 (<code>population_un_wpp2024</code>) '
                 'are supplied because the two input workbooks disagreed. They differ by more than '
                 '3% for 26 country-years &mdash; Israel by 4.1%. Pick one and keep it for every '
                 'country.'],
          'zh': ['<strong>基準日不一致。</strong>Eurostat 與 OECD 之存量以 1 月 1 日為準，'
                 '故標示為 <em>Y</em> 年的列，描述的是 <em>Y&minus;1</em> 年 12 月 31 日的狀態。'
                 '臺灣與南韓為年底；日本為 1 月 1 日。各數值之基準日載於 '
                 '<code>*_ref_date</code> 欄位。',
                 '<strong>請擇一人口分母。</strong>因兩份原始工作表不一致，'
                 '本站同時提供世界銀行（<code>population</code>）與 UN WPP 2024'
                 '（<code>population_un_wpp2024</code>）兩組序列。'
                 '其中 26 個國家—年度差異超過 3%（以色列達 4.1%）。'
                 '請擇一使用並貫徹於所有國家。']},
 'lim_h': {'en': 'Limits of this archive', 'zh': '本存檔的限制'},
 'lim1': {'en': 'The archive fixes what could be demonstrated wrong and documents what could not be '
                'fixed. It does not make the irregular-migration variables comparable across '
                'countries, because no source does. Six values rest on a source that no longer '
                'exists anywhere reachable; they are graded D and named rather than quietly '
                'dropped. Five sources block or have moved, and were replaced by equivalents that '
                'confirmed the values &mdash; the substitutions are itemised on the ',
          'zh': '本存檔更正了所有能被證明有誤之處，並載明無法更正者。'
                '它並未使無證移民變項變得可跨國比較——因為沒有任何來源做得到。'
                '有 6 筆數值所依據的來源已完全無法取得，這些數值評為 D 級並明確標示，'
                '而非默默刪除。另有 5 個來源遭封鎖或已更動網址，'
                '均以同等來源替代且確認了原數值&mdash;&mdash;各項替代均逐筆載明於'},
 'lim2': {'en': ' page.', 'zh': '頁面。'},
 'lim3': {'en': 'Mirrors are held for verification only. Copyright in each source document remains '
                'with its publisher, and every entry links to the original URL.',
          'zh': '本站鏡像僅供查證之用。各來源文件之著作權仍屬其原出版機構所有，'
                '每筆條目均附原始網址連結。'},
}
