# -*- coding: utf-8 -*-
"""Traditional Chinese (Taiwan) translations of the long-form page prose.

Row-level text for known_issues and codebook is NOT here: it lives beside the English
in data/known_issues.csv and data/codebook.csv, one row carrying both languages, so
the two cannot drift apart or be mis-keyed by row index."""

from counts import (N_EVIDENCE, N_ALL_URLS, N_CITES, N_CITES_HELD, N_CHECKS,  # noqa: E402
                    N_RECHECKED)


# ---------------------------------------------------------------- known issues
SEV = {'RESOLVED': '已解決', 'HIGH': '高', 'MEDIUM': '中', 'LOW': '低', 'INFO': '說明'}

SCOPE = {
 'Switzerland, Portugal, Sweden': '瑞士、葡萄牙、瑞典',
 'Sweden': '瑞典', 'Taiwan': '臺灣', 'Italy': '義大利', 'Korea': '南韓',
 'Switzerland': '瑞士', 'Japan': '日本', 'all': '全部',
 'Israel': '以色列',
 'Australia, India, Israel, New Zealand, Russia, South Africa':
     '澳洲、印度、以色列、紐西蘭、俄羅斯、南非',
 'Israel, Bulgaria, France, Turkey, USA, Poland, China, Netherlands':
     '以色列、保加利亞、法國、土耳其、美國、波蘭、中國、荷蘭',
 'Turkey, Czechia, Slovakia, Portugal, Germany': '土耳其、捷克、斯洛伐克、葡萄牙、德國',
 'Spliced series (OECD values extend a Eurostat series)':
     '接續序列（以 OECD 數值延伸 Eurostat 序列）',
 'Denmark, Slovakia, Czechia, Lithuania, Poland, Portugal':
     '丹麥、斯洛伐克、捷克、立陶宛、波蘭、葡萄牙',
 'China, India, Philippines, Suriname, Thailand': '中國、印度、菲律賓、蘇利南、泰國',
 'Not collected for 2001-2009': '2001–2009 年未能蒐集者',
 'Added years 2001-2010, several countries': '延伸之年度 2001–2010，多國',
 'EU/EFTA': '歐盟／歐洲自由貿易聯盟',
 'Eurostat / OECD countries': 'Eurostat／OECD 國家',
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
                'screenshot. Capture began on ',
          'zh': '本資料集有兩類來源。批次統計 API 以原始回應內容完整保存；'
                '個別文件與網頁則直接下載，若來源為網頁，另製作 PDF 與整頁截圖。'
                '擷取始於 '},
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
 'ev_count': {'en': str(N_EVIDENCE) + ' evidence pages · ' + str(N_EVIDENCE) + ' PDF extracts',
              'zh': str(N_EVIDENCE) + ' 個佐證頁 · ' + str(N_EVIDENCE) + ' 份 PDF 摘錄'},
 'doc_h': {'en': 'Document and web-page sources', 'zh': '文件與網頁來源'},
 'doc_sub': {'en': 'Beyond the bulk APIs, this archive rests on <strong>%d distinct '
                   'country&ndash;source citations</strong> across %d URLs, and <strong>%d of '
                   '%d</strong> are held here. The source column names the document each value is '
                   'actually verified against. Where the citation originally supplied with the '
                   'data had gone dead, it was replaced by a live source carrying the same figure, '
                   'and the original is recorded in the Note column rather than discarded. Use the '
                   'filter to find a country, a publisher or a URL.',
             'zh': '除批次 API 外，本典藏另依據 <strong>%d 筆不重複的國家&ndash;來源</strong>，'
                   '共 %d 個網址，其中 <strong>%d／%d</strong> 已存檔於本站。'
                   '「來源」欄所列為各數值實際據以查證之文件；'
                   '若原始資料所附之引用來源已失效，則改以仍可取得、且載有相同數字的來源替代，'
                   '原引用來源則保留於「備註」欄，不予刪除。'
                   '可使用篩選欄查找國家、發布機構或網址。'},
 'filter_ph': {'en': 'Filter by country, source or URL…', 'zh': '依國家、來源或網址篩選…'},
 'of_sources': {'en': 'of %d sources', 'zh': '／%d 筆來源'},
 'fail_h': {'en': 'Citations that were replaced', 'zh': '已更替的引用來源'},
 'fail_note': {'en': '<strong>Every one of the %d citations this archive relies on has been '
                     'retrieved and stored here.</strong> In %d cases the citation originally '
                     'supplied with the data had gone dead — a moved government PDF, a publisher '
                     'that refuses all automated and browser access, a host that no longer '
                     'responds. None of those values was left resting on a dead link: each was '
                     're-verified against a live source that carries the same figure, and the '
                     'original citation is preserved in the Note column above.<br>\n'
                     '<em>sem.admin.ch</em> — the Swiss SEM study PDF moved; the 76,000 figure is '
                     'stated in the SRF report on its release.<br>\n'
                     '<em>ismu.org</em> — serves a 403 bot wall to a browser; replaced by ISMU’s '
                     'own published series and, for 2022, the XXVIII Rapporto. Retrieved by '
                     'direct request on 2026-08-18, the original press releases state the same '
                     'figures and are archived here as corroboration.<br>\n'
                     '<em>press.police.ac.kr</em> — no longer responds; Korea’s 2010–2015 figures '
                     'now come from the Ministry of Justice yearbook and open-data series.<br>\n'
                     '<em>nisshinkyo.org</em> — a mirror of a Japanese Immigration Services Agency '
                     'table, now 404; the ISA document itself is archived here and prints the same '
                     'figure.',
               'zh': '<strong>本典藏所依據的 %d 筆引用來源，已全數取得並存檔於本站。</strong>'
                     '其中 %d 筆之原始引用來源已失效——政府 PDF 移轉網址、'
                     '發布機構封鎖所有自動化與瀏覽器存取、或主機不再回應。'
                     '此類數值均未停留於失效連結之上：每一筆均已改對照仍可取得、'
                     '且載有相同數字之來源重新查證，原引用來源則保留於上方「備註」欄。<br>\n'
                     '<em>sem.admin.ch</em>——瑞士 SEM 研究 PDF 已移轉網址；'
                     '76,000 之數字載於 SRF 對該研究發布之報導。<br>\n'
                     '<em>ismu.org</em>——對瀏覽器型式的請求回傳 403 機器人阻擋頁；'
                     '改以 ISMU 自行發布之序列替代，2022 年則採第 XXVIII 號報告。'
                     '2026-08-18 以直接請求取得原新聞稿，其內容確載相同數字，已一併存檔作為佐證。<br>\n'
                     '<em>press.police.ac.kr</em>——已不再回應；南韓 2010–2015 年數值'
                     '現改採法務部統計年報與公開資料序列。<br>\n'
                     '<em>nisshinkyo.org</em>——日本出入國在留管理廳表格之鏡像，現已 404；'
                     '該廳原始文件已存檔於本站，並載有相同數字。'},
 'fail_p': {'en': 'Each replacement URL was checked live and the figure it supports was located '
                  'in the archived copy before the substitution was recorded. The full '
                  'value-by-value results are in ',
            'zh': '每一個替代網址均經即時檢查，且於存檔副本中確認其所支持之數字後，'
                  '方登錄為替代來源。逐筆查證結果詳見'},
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
 'tag_superseded': {'en': 'citation superseded', 'zh': '引用來源已更替'},
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
                    '<strong>FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx</strong>. '
                    'Every value in it traces to a source file held in this archive.',
              'zh': '本網站所有內容——每一項統計、等級與更正——均指向 '
                    '<strong>FINAL_migration_population_panel_2010-2022_VERIFIED.xlsx</strong>。'
                    '其中每一個數值都可追溯至本存檔內的來源檔案。'},
 'alt_h': {'en': 'A second workbook, included for completeness', 'zh': '第二份工作表（為求完整而附上）'},
 'alt_note': {'en': '<strong>This file is not the one the website documents.</strong> It was '
                    'produced by a separate compilation run. Its <em>Verification</em> sheet '
                    'reports 203 source rows, 192 of 203 snapshots and 750 of 750 values matched; '
                    'the figures for this archive are ' + str(N_ALL_URLS) + ' distinct source URLs, '
                    + str(N_CITES_HELD) + ' of ' + str(N_CITES) + ' document citations retrieved '
                    'and ' + format(N_CHECKS, ',') + ' value comparisons (' + format(N_RECHECKED, ',')
                    + ' of them repeated on 2026-10-07). Its <em>Source Audit</em> and '
                    '<em>Folder Index</em> sheets also point at a folder layout '
                    '(<code>country_sources\\…</code>) that does not exist in this repository. Its '
                    'substantive conclusions agree with this archive’s; its counts are not '
                    'interchangeable with them.',
              'zh': '<strong>本檔案並非本網站所記載的那一份。</strong>'
                    '它由另一次獨立的彙編作業產生。其 <em>Verification</em> 工作表記載 203 筆來源、'
                    '192／203 份快照、750／750 筆數值一致；而本存檔的對應數字為 ' + str(N_ALL_URLS)
                    + ' 個不重複之來源網址、' + str(N_CITES_HELD) + '／' + str(N_CITES)
                    + ' 筆國家—來源引用已存檔、' + format(N_CHECKS, ',') + ' 筆數值比對（其中 '
                    + format(N_RECHECKED, ',') + ' 筆於 2026-10-07 重複比對）。'
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
                'values that did not match. Everything done to the data after that day - '
                'every correction, deletion, re-classification, re-citation and re-check - '
                'is dated in the revision history below.',
          'zh': '所有資料來源均於 ACCESS 重新取得，並將原始工作表中的每一筆數值與之比對。'
                '本頁完整呈現結果，包含未能一致的數值。'
                '此後對資料所做之一切處理——每一項更正、刪除、重新歸類、改引來源與重新查證——'
                '均於下方修訂紀錄中載明日期。'},
 'rev_h': {'en': 'Revision history', 'zh': '修訂紀錄'},
 'rev_sub': {'en': 'Every change to the data after sources were first retrieved on ACCESS, '
                   'taken from the version history of this archive (Taipei time). Rows '
                   'marked <strong>data</strong> changed a value, how it is classified or '
                   'what it is cited to; the others are checks and added evidence that left '
                   'the numbers as they were. Wording, translation and layout changes are '
                   'not data amendments and are not listed.',
             'zh': '資料來源於 ACCESS 首次取得後，對資料所做之每一項變更，'
                   '取自本存檔之版本紀錄（臺北時間）。標示<strong>資料</strong>者，'
                   '變更了數值、其歸類或其引用來源；其餘為查證與新增佐證，數值未變。'
                   '文字、翻譯與版面之修改不屬資料修訂，不予列入。'},
 'ext_h': {'en': 'The extension back to 2001', 'zh': '向前延伸至 2001 年'},
 'ext_sub': {'en': 'On 2026-10-07 the panel was extended from 2010&ndash;2022 back to 2001. This '
                   'section shows what was added, how it relates to the series already published, '
                   'and what could not be collected. Every added value is still a link to its '
                   'evidence, and no value published before the extension changed.',
             'zh': '2026-10-07 本 panel 由 2010–2022 年向前延伸至 2001 年。本節說明新增了什麼、'
                   '與先前發布之序列有何關係，以及哪些無法蒐集。每一筆新增數值仍連結至其佐證，'
                   '且延伸前已發布之數值無一變動。'},
 'ext_added_h': {'en': 'What was added', 'zh': '新增內容'},
 'ext_col_what': {'en': 'Variable and source type', 'zh': '變項與來源類型'},
 'ext_col_n': {'en': 'New values', 'zh': '新增數值'},
 'ext_col_c': {'en': 'Countries', 'zh': '國家數'},
 'ext_type': {'en': {'annual': 'annual official series', 'census': 'census', 'survey': 'household survey',
                     'un_estimate': 'UN DESA model estimate', 'other': 'other'},
              'zh': {'annual': '官方逐年序列', 'census': '普查', 'survey': '家戶調查',
                     'un_estimate': 'UN DESA 模型估計值', 'other': '其他'}},
 'ext_recheck_h': {'en': 'Re-check of values already published', 'zh': '對已發布數值之重新查核'},
 'ext_recheck_sub': {'en': 'Each payload retrieved for the extension spans 2001&ndash;2022, so the '
                           'part covering 2010&ndash;2022 was compared with what the archive already '
                           'published.',
                     'zh': '為本次延伸所取得之每份回應均涵蓋 2001–2022 年，故其涵蓋 2010–2022 年之部分'
                           '已與本存檔先前發布之數值比對。'},
 'ext_col_src': {'en': 'Source', 'zh': '來源'},
 'ext_col_cmp': {'en': 'Compared', 'zh': '已比對'},
 'ext_col_same': {'en': 'Identical', 'zh': '完全一致'},
 'ext_splice_h': {'en': 'Where the source changes at the join', 'zh': '於接合處更換來源者'},
 'ext_splice_sub': {'en': 'Where the source of the earlier years differs from the one already used '
                          'for 2010&ndash;2022, the two were compared over the years they share. '
                          '%d series needed a change; %d differ by 5%% or more and are shown here. A '
                          'step of that size at the join is a source effect, not a change in '
                          'migration. The rest are listed in the file below.',
                    'zh': '若較早年度所用之來源與 2010–2022 年已使用者不同，則於兩者共有之年度加以比較。'
                          '共有 %d 組序列須更換來源，其中 %d 組相差 5%% 以上，列於下表。接合處如此幅度之變動'
                          '屬來源效應，並非移民之實際變化。其餘序列見下方檔案。'},
 'ext_col_gap': {'en': 'Mean gap', 'zh': '平均差距'},
 'ext_col_range': {'en': 'Range over the overlap', 'zh': '重疊年度之範圍'},
 'ext_col_ext': {'en': 'Years extended', 'zh': '延伸之年度'},
 'ext_col_ov': {'en': 'Overlap (years)', 'zh': '重疊年數'},
 'ext_none_h': {'en': 'What could not be collected', 'zh': '無法蒐集者'},
 'ext_none_p': {'en': 'Australia\'s foreign nationals and Chile\'s 2002 foreign-born count were looked '
                      'for and not obtained; several countries have only census years, and Japan, '
                      'Israel and New Zealand have no comparable statistic for one of the two '
                      'variables. The full list, with reasons, is in the issues table below and in '
                      'the revision history above.',
                'zh': '已尋找但未取得者為澳洲外國籍人口與智利 2002 年外國出生人數；數個國家僅有普查年度；'
                      '日本、以色列與紐西蘭則有一項變項無可比較之統計。完整清單與原因見下方問題表與上方修訂紀錄。'},
 'col_when': {'en': 'Date', 'zh': '日期'},
 'col_kind': {'en': 'Change', 'zh': '變更類型'},
 'col_ba': {'en': 'Before &rarr; after', 'zh': '變更前 &rarr; 變更後'},
 'col_detail': {'en': 'What and why', 'zh': '內容與理由'},
 'tag_data': {'en': 'data', 'zh': '資料'},
 'kind': {'en': {}, 'zh': {'first publication': '首次發布', 'value corrected': '數值更正',
                          'value deleted': '數值刪除', 'flagged as derived': '標示為推導值',
                          're-verified': '重新查證', 'source re-cited': '改引來源',
                          'evidence added': '新增佐證', 'value reclassified': '數值重新歸類',
                          'note amended': '備註修訂', 'range extended': '期間延伸',
                          'collection attempted, not obtained': '嘗試蒐集而未取得',
                          'manifest corrected': '雜湊清單更正'}},
 'rate_h': {'en': 'Reproduction rate by source, as verified to date',
            'zh': '各來源之重現率（截至最近查證日）'},
 'rate_sub': {'en': 'Each row shows the most recent verification of that source and the date it '
                    'was carried out. Every source currently reproduces at 100%: every value the '
                    'archive publishes matches the live source exactly.',
              'zh': '每一列呈現該來源最近一次查證的結果與查證日期。'
                    '目前所有來源之重現率均為 100%：本存檔所發布的每一筆數值，'
                    '皆與線上來源完全一致。'},
 'rate_hist': {'en': '<strong>Eurostat migr_eipre was not 100% at first.</strong> Verified on '
                     '2026-08-17 it reproduced 244 of 283 values (86.2%): the detections series '
                     'for Switzerland, Portugal and Sweden was offset by one year in one of the '
                     'input workbooks. All 39 values were corrected, and the series was re-queried '
                     'live and re-tested on 2026-08-18, when it reproduced 283 of 283 (100%). '
                     'Both tests are kept in the verification log under the <code>stage</code> '
                     'column, and the corrections are itemised below.',
               'zh': '<strong>Eurostat migr_eipre 起初並非 100%。</strong>'
                     '於 2026-08-17 查證時，283 筆中有 244 筆一致（86.2%）：'
                     '其中一份原始工作表的瑞士、葡萄牙、瑞典查獲人次序列整體位移一年。'
                     '該 39 筆全部更正後，已於 2026-08-18 重新向 Eurostat 查詢並重測，'
                     '283 筆全部一致（100%）。兩次測試均保留於查證紀錄的 '
                     '<code>stage</code> 欄位，更正內容逐項列於下方。'},
 'col_date': {'en': 'Verified on', 'zh': '查證日期'},
 'col_prev': {'en': 'Earlier test', 'zh': '先前測試'},
 'col_src': {'en': 'Source', 'zh': '來源'},
 'col_nchk': {'en': 'Values checked', 'zh': '已查證數值'},
 'col_exact': {'en': 'Exact', 'zh': '完全一致'},
 'col_rate': {'en': 'Rate', 'zh': '一致率'},
 'fulllog': {'en': 'full verification log (CSV)', 'zh': '完整查證紀錄（CSV）'},
 'corr_h': {'en': 'Corrections applied', 'zh': '已套用之更正'},
 'corr_sub': {'en': '%d values across %d countries. Each change is itemised below with the reason '
                    'and the evidence behind it.',
              'zh': '共 %d 筆數值，涵蓋 %d 個國家。以下逐項列出每一處改動的理由與佐證。'},
 'corr_sub2': {'en': '', 'zh': ''},
 'iss_h': {'en': 'Issues found', 'zh': '所發現的問題'},
 'iss_sub': {'en': 'Every row here concerns the data this archive publishes: first the issues '
                   'that were found and fixed, then the caveats that remain and must be carried '
                   'into any analysis.',
             'zh': '本表各列均涉及本典藏所發布之資料：先列已發現並更正者，'
                   '其後為仍然存在、分析時必須一併納入考量的問題。'},
 'col_sev': {'en': 'Severity', 'zh': '嚴重度'},
 'col_scope': {'en': 'Scope', 'zh': '範圍'},
 'col_issue': {'en': 'Issue', 'zh': '問題'},
 'col_evid': {'en': 'Evidence', 'zh': '佐證'},
 'col_action': {'en': 'Action taken', 'zh': '已採取之處理'},
 'held_h': {'en': 'What held up', 'zh': '通過查證的部分'},
 'held_sub': {'en': 'Worth stating as plainly as the problems.', 'zh': '這些同樣值得如實載明。'},
 'held': {'en': ['All 520 UN WPP 2024 population values for 2010&ndash;2022 reproduced exactly.',
                 'All 507 World Bank population values for 2010&ndash;2022 reproduced exactly.',
                 'All 584 Eurostat foreign-born and foreign-national values for 2010&ndash;2022 reproduced exactly.',
                 'All 139 OECD International Migration Database values for 2010&ndash;2022 reproduced exactly.',
                 'On 2026-10-07, against fresh responses, all 1,777 values published before the '
                 'extension to 2001 reproduced exactly again (see the revision history above).',
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
          'zh': ['520 筆 UN WPP 2024 人口數值（2010–2022 年）全部完全重現。',
                 '507 筆世界銀行人口數值（2010–2022 年）全部完全重現。',
                 '584 筆 Eurostat 外國出生與外國籍人口數值（2010–2022 年）全部完全重現。',
                 '139 筆 OECD 國際移民資料庫數值（2010–2022 年）全部完全重現。',
                 '2026-10-07 對照全新取得之回應，延伸至 2001 年之前已發布之 1,777 筆數值再次全數完全重現'
                 '（見上方修訂紀錄）。',
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
 'inputs_h': {'en': 'Which inputs were used', 'zh': '採用哪些原始輸入'},
 'inputs_p': {'en': 'Two workbooks were supplied. The panel is built on '
                    '<code>migration_population_panel_40countries_2010-2022.xlsx</code>. The '
                    'earlier <code>immigration_country_year_2010_2022.xlsx</code> was examined '
                    'and used only as a cross-check, because its '
                    '<code>Illegal_immigrants_number</code> column pools five conceptually '
                    'different measures — annual enforcement detections, which are a flow, '
                    'together with overstayer register counts and modelled unauthorised-population '
                    'estimates, which are stocks. Pooled that way the column cannot be read as a '
                    'series, so this archive keeps the three measures in three separate columns '
                    'and no published value is taken from the pooled column. Where a figure was '
                    'first noticed in that workbook it was re-verified against the publisher '
                    'before publication.',
              'zh': '本研究獲提供兩份工作表。本 panel 係以 '
                    '<code>migration_population_panel_40countries_2010-2022.xlsx</code> 為基礎建立。'
                    '較早的 <code>immigration_country_year_2010_2022.xlsx</code> 已經檢視，'
                    '但僅作為交叉核對之用，因其 <code>Illegal_immigrants_number</code> 欄位'
                    '將五種概念上不同的統計合併於同一欄：屬「流量」的年度查緝查獲數，'
                    '與屬「存量」的逾期停留登記數及推估之無證人口數。'
                    '如此合併後該欄位無法作為時間序列解讀，'
                    '故本典藏將三種統計分置於三個獨立欄位，'
                    '所發布之數值亦無一取自該合併欄位。'
                    '若某一數值最初係於該工作表中發現，發布前均已重新對照原始發布機關查證。'},
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
                 'country&times;variable series &mdash; ' + str(N_EVIDENCE) + ' in all &mdash; listing each '
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
                 '&mdash;&mdash;共 ' + str(N_EVIDENCE) + ' 個&mdash;&mdash;列出各年度數值、品質等級、核對對象，'
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
