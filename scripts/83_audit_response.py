# -*- coding: utf-8 -*-
"""The response to the audit of 2026-10-07: one row per finding, what was checked, the verdict, what changed.

Writes data/audit_response_2026-10-07.csv (read by the Verification page) and
verification/AUDIT_RESPONSE_2026-10-07.md. The verdicts are the outcome of re-checking each finding against
the archived source (and, where the archive held nothing, the publisher's own page); numbers that depend on
the data are computed here from the data files.
"""
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import counts as K                                                  # noqa: E402

SITE = os.path.dirname(HERE)
D = os.path.join(SITE, 'data')
WHEN = '2026-10-07'
chg = pd.read_csv(os.path.join(D, 'audit_changes_%s.csv' % WHEN))
spl = pd.read_csv(os.path.join(D, 'extension_splice_summary.csv'))
dq = pd.read_csv(os.path.join(D, 'data_quality.csv'))
ver = pd.read_csv(os.path.join(D, 'current_panel_verification.csv'))
sec = pd.read_csv(os.path.join(D, 'secondary_workbook_differences.csv'))
below = pd.read_csv(os.path.join(D, 'foreign_born_below_foreign_nationals.csv'))
n_large = int((spl.mean_abs_gap_pct >= 5).sum())
n_large_cells = int(spl[spl.mean_abs_gap_pct >= 5].cells.sum())
n_cautioned = int(dq.usable_for_trend.str.contains('single source').sum())
n_added = int((chg.kind == 'added').sum())

R = []


def add(f, no, title, title_zh, verdict, verdict_zh, checked, checked_zh, result, result_zh, status, status_zh):
    R.append(dict(finding=f, issue=no, title=title, title_zh=title_zh, verdict=verdict, verdict_zh=verdict_zh,
                  checked=checked, checked_zh=checked_zh, resolution=result, resolution_zh=result_zh,
                  status=status, status_zh=status_zh))


C, CQ = 'Confirmed', 'Confirmed, with a qualification'
CZ, CQZ = '屬實', '屬實（附保留）'
RES, RESZ = 'Resolved', '已解決'
DEC, DECZ = 'Resolved; one decision left to the authors', '已解決；有一項決定留待作者'
OPEN, OPENZ = 'Open: for the authors', '未結：留待作者'

add('F01', 1, 'Chile irregular stock: wrong years and methodologies', '智利無證移民存量：年度與方法錯置', C, CZ,
    'Rendered page 12 of the archived INE/SERMIG PDF and read every label from the PDF\'s own coordinates '
    '(scripts/80_check_source_charts.py): marker colour gives the series, x position the year, height must agree with '
    'the printed value.',
    '將所存檔 INE/SERMIG PDF 之第 12 頁轉為圖像，並由 PDF 自身之座標讀取每個標籤'
    '（scripts/80_check_source_charts.py）：標記顏色決定序列、x 位置決定年度、高度須與所印數值一致。',
    'All five 2018-2022 cells held other years\' values and mixed the two methodologies. Now the 2023 methodology for '
    'every year (10,375; 21,833; 53,356; 109,846; 291,149); the 2022 methodology and the press-release 107,223 are '
    'alternatives; the chart check now fails if the panel disagrees with the chart.',
    '五格 2018–2022 年數值均為他年數值，且混用兩種方法。現各年一律採 2023 年方法（10,375；21,833；53,356；109,846；291,149）；'
    '2022 年方法與新聞稿之 107,223 列為替代值；圖表檢查在 panel 與圖表不符時即失敗。',
    DEC, DECZ)
add('F02', 2, 'India 2011: previous residence used as birthplace', '印度 2011：以最近居住地取代出生地', C, CZ,
    'Downloaded the official D-01 workbook from censusindia.gov.in (byte-identical to the audit\'s copy): national row '
    '"Born Outside India" 5,363,099; the five continents sum to it. The cited article\'s 2,513 + 2,977 thousand is its '
    'Table 2a, sourced to Table D-2 (last residence). Authors on the first page: Singh and Biradar.',
    '自印度普查官網下載官方 D-01 活頁簿（與稽核所用副本位元組相同）：全國列「Born Outside India」為 5,363,099，'
    '五大洲加總與之相符。所引論文之 2,513＋2,977 千為其表 2a，來源為表 D-2（最近居住地）。首頁作者為 Singh 與 Biradar。',
    'Corrected to 5,363,099 (grade A); workbook, catalogue page and a table extract archived; authors corrected '
    'wherever the article is cited; the 5.49-million premise removed from the UN discussion.',
    '已更正為 5,363,099（A 級）；活頁簿、目錄頁與表格摘錄已存檔；凡引用該論文處之作者均已更正；'
    '並自 UN 之討論中移除 549 萬之前提。',
    RES, RESZ)
add('F03', 3, 'Suriname 2012: unknown nationality counted as foreign', '蘇利南 2012：國籍不明者被計為外國籍', C, CZ,
    'Read Table H2 (page 24): Surinamese 505,245; Dutch 10,248, Guyanese 8,278, French 3,575, Brazilian 5,027, Chinese 3,758, '
    'other 2,167 (sum 33,053); unknown 3,340; total 541,638. 36,393 is a residual, not a printed figure.',
    '讀取表 H2（第 24 頁）：蘇利南籍 505,245；荷蘭 10,248、圭亞那 8,278、法國 3,575、巴西 5,027、中國 3,758、其他 2,167（合計 33,053）；'
    '不明 3,340；總計 541,638。36,393 為剩餘數，並非表中所印。',
    'Corrected to 33,053 and marked derived; 3,340 unknown excluded; 36,393 kept as an alternative.',
    '已更正為 33,053 並標示為推導值；3,340 名不明者不計入；36,393 保留為替代值。',
    RES, RESZ)
add('F04', 4, '20 citizenship-based UN cells in foreign_born', '20 格公民身分基礎之 UN 數值列於 foreign_born', C, CZ,
    'Confirmed the 20 cells (5 countries x 4 benchmark years) equal the UN workbook and that UN declares type C for them. '
    'The archive had already flagged them; the audit is right that a flag does not make them birthplace counts.',
    '確認 20 格（5 國 × 4 個基準年）與 UN 活頁簿一致，且 UN 對其宣告為類型 C。本存檔原已加註旗標；'
    '稽核所言屬實：旗標並不使其成為依出生地計算之數。',
    'foreign_born_concept names the basis cell by cell; the analysis extract holds these cells in separate columns so '
    'its foreign_born is birthplace only; coverage and codebook updated. Not moved to foreign_nationals (that needs a '
    'universe check).',
    'foreign_born_concept 逐格載明其基礎；分析用資料集將這些數值存放於獨立欄位，使其 foreign_born 僅含出生地數；'
    '涵蓋範圍與變項說明書已更新。未移入 foreign_nationals（那需先查核母體範圍）。',
    DEC, DECZ)
add('F05', 5, 'Eurostat detections described as repeat events', 'Eurostat 查獲數被描述為重複事件', C, CZ,
    'Read the Eurostat enforcement metadata (migr_eil ESMS): "Each person is counted only once within the reference '
    'period"; units are persons; rounded to the nearest 5; and checked all 32 EU and country values of the 2023 table '
    'are multiples of 5. That the same person can recur in different years follows from the calendar-year period; the '
    'metadata does not say it. Mexico\'s source does count events.',
    '讀取 Eurostat 執法統計後設資料（migr_eil ESMS）：「同一參考期間內每人僅計一次」；單位為人數；四捨五入至最接近之 5；'
    '並確認 2023 年表中 32 個歐盟與各國數值皆為 5 的倍數。同一人可於不同年度重複出現，係由曆年期間推得，後設資料並未明言。'
    '墨西哥之來源確實計事件數。',
    'Codebook, methods page, workbook and extract now state the unit per source (Eurostat persons, once per year; Mexico '
    'events; Turkey apprehended migrants); Chinese label 查獲人次 changed to 查獲人數.',
    '變項說明書、研究方法頁、活頁簿與分析用資料集現依來源載明單位（Eurostat：人數，每年每人一次；墨西哥：事件數；'
    '土耳其：被逮捕之移民）；中文標籤「查獲人次」改為「查獲人數」。',
    RES, RESZ)
add('F06', 6, 'Taiwan overstay citations and the 2021 value', '臺灣逾期停留之引註與 2021 年數值', C, CZ,
    'The MOL PDF cited for 2012, 2013, 2019, 2020 and 2021 is Table 12-7 (absconded workers). 66,696 and 69,929 are in the '
    'Legislative Yuan report of July 2019 (附表11); 83,465 and 86,061 in its September 2021 Table 1; 81,538 is in no '
    'archived document, and a further search of National Immigration Agency and Legislative Yuan documents found no '
    'end-2021 total.',
    '2012、2013、2019、2020、2021 年所引之勞動部 PDF 為表 12-7（失聯移工）。66,696 與 69,929 見立法院預算中心 2019 年 7 月報告（附表11）；'
    '83,465 與 86,061 見其 2021 年 9 月報告表 1；81,538 不在任何存檔文件中，再查移民署與立法院文件亦無 2021 年底總數。',
    'Citations repointed to the reports that hold the numbers; 2019-2020 dates stated as "month not stated"; 2021 deleted '
    '(deleted_values.csv). While checking, the absconded-worker value for 2019 was found to be the 31 July figure in a '
    'year-end column and was replaced by the year-end 48,491.',
    '引註已改指載有該數字之報告；2019–2020 年之日期標示為「來源未載月份」；2021 年數值刪除（deleted_values.csv）。'
    '查核過程中發現 2019 年失聯移工數為年底欄中之 7 月 31 日數字，已改為年底數 48,491。',
    RES, RESZ)
add('F07', 7, 'Taiwan overstay universe', '臺灣逾期停留之母體', C, CZ,
    '附表11 splits each year-end total into foreign nationals, mainland Chinese, Hong Kong/Macao and nationals without '
    'household registration; the panel values equal the totals, not the foreign-national column, for 2012-2018, and '
    '2019-2020 are the same series.',
    '附表11 將各年底總數拆為外國人、大陸地區人民、港澳居民與無戶籍國民；panel 於 2012–2018 年之數值等於總數而非外國人欄，'
    '2019–2020 年為同一序列。',
    'Notes and the codebook now say the total covers all categories; the foreign-national component for 2012-2018 is an '
    'alternative. Which universe the study needs is the authors\' decision; the total was kept because it is the only '
    'consistent series for 2012-2020.',
    '備註與變項說明書現載明該總數涵蓋所有類別；2012–2018 年之外國人部分為替代值。研究需要何種母體由作者決定；'
    '保留總數，因其為 2012–2020 年唯一一致之序列。',
    DEC, DECZ)
add('F08', 8, 'Taiwan population 2010-2016 rounded', '臺灣 2010–2016 人口被四捨五入', C, CZ,
    'MOI Statistical Yearbook 2019 edition, PDF page 151, prints exact totals (23,162,123 ... 23,539,816); the panel '
    'held the NDC figures rounded to thousands; differences -123 to +483.',
    '內政部統計年報 108 年版 PDF 第 151 頁載有精確總數（23,162,123 … 23,539,816）；panel 所載為國發會四捨五入至千位之數，差異為 −123 至 +483。',
    'Exact totals now (grade B: read from a printed table); 2001-2009 stay rounded to thousands and the cell text and '
    'codebook say so; shares recomputed.',
    '現採精確總數（B 級：讀自印刷表格）；2001–2009 年仍為千位且儲存格文字與變項說明書已載明；占比已重算。',
    RES, RESZ)
add('F09', 9, 'Australia: citizenship-data unavailability overstated', '澳洲：公民身分資料不可得之說法過當', CQ, CQZ,
    'Fetched the ABS 2021 Census QuickStats page (2102_AUS): the national total column gives 2,808,214 not Australian '
    'citizens (11.0%); the figure sits on a country-of-birth page, the all-persons page has no citizenship row, and 5.1% '
    'did not state.',
    '取得澳洲統計局 2021 年普查 QuickStats 頁（2102_AUS）：全國總數欄為 2,808,214 人非澳洲公民（11.0%）；該數字位於出生地頁面，'
    '全體人口頁面無公民身分列，且有 5.1% 未填答。',
    'The change report\'s "ABS QuickStats carry no citizenship totals" was wrong and is corrected in the known issues. '
    'Not added to the panel: the universe (not stated, overseas visitors) is for the authors to settle; nothing was '
    'interpolated.',
    '變更報告所稱「ABS QuickStats 無公民身分總數」有誤，已於已知問題中更正。未加入 panel：母體範圍（未填答、海外訪客）留待作者決定；未作任何內插。',
    OPEN, OPENZ)
add('F10', 10, 'South Africa 2011: citizenship question exists', '南非 2011：確有公民身分題', C, CZ,
    'Downloaded the official Census 2011 in Brief: Table 2.17 "South African citizenship by province": Yes 48,949,338, '
    'No 1,692,242, total 50,641,580 (census population 51,770,560); the enumeration form asks "Is (name) a South African '
    'citizen? Yes / No".',
    '下載官方《2011 年普查簡報》：表 2.17「各省南非公民身分」：是 48,949,338、否 1,692,242、合計 50,641,580（普查人口 51,770,560）；'
    '調查表題目為「（姓名）是否為南非公民？是／否」。',
    'The availability memo\'s "no citizenship question" is false and is corrected there. Not added: 1,128,980 persons '
    'are outside the table and the universe is the authors\' call; the foreign-born subgroup count is not substituted.',
    '可得性備忘錄所稱「無公民身分題」有誤，已於該處更正。未加入：有 1,128,980 人不在該表內，母體範圍由作者決定；亦不以外國出生子群之數取代。',
    OPEN, OPENZ)
add('F11', 11, 'Blanket OECD reference-date statement', '籠統之 OECD 基準日說法', C, CZ,
    'Read the OECD International Migration Outlook 2024 metadata for the foreign-born and foreign-population tables: only '
    'Australia states 30 June; Japan, Turkey, the United Kingdom and Germany state 1 January for the foreign population; '
    'many (United States, Chile, Mexico, New Zealand, Israel, United Kingdom foreign-born) state no date. (OECD\'s own page '
    'blocked automated access; a mirror of the printed annex was read.)',
    '讀取《OECD 國際移民展望 2024》外國出生人口與外國人口表之後設資料：僅澳洲載明 6 月 30 日；日本、土耳其、英國與德國之外國人口載明 1 月 1 日；'
    '多國（美國、智利、墨西哥、紐西蘭、以色列、英國之外國出生人口）未載明日期。（OECD 官網阻擋自動化存取，改讀其印刷附錄之鏡像。）',
    'The blanket statements in the methods page, codebook, workbook README and analysis extract are replaced by the '
    'source-specific wording; per-value dates were already in *_ref_date and are unchanged; no year was shifted.',
    '研究方法頁、變項說明書、活頁簿 README 與分析用資料集中籠統之說法已改為依來源之文字；逐值之日期原已載於 *_ref_date 且未變；未移動任何年度。',
    RES, RESZ)
add('F12', 12, 'Splice rule: mean absolute gap not implemented', '接合規則：未實作平均絕對差距', C, CZ,
    'The collector tested abs(mean(gap)). Recomputed for all 28 splices: Germany foreign-born signed +1.565%%, mean absolute '
    '7.372%%; Portugal foreign-born -5.892%% and 21.290%%; %d series reach 5%% by the declared rule against 7 reported.' % n_large,
    '收集程式檢定的是 abs(mean(gap))。重算全部 28 組接續序列：德國外國出生人口有號 +1.565%%、平均絕對 7.372%%；'
    '葡萄牙外國出生人口 −5.892%% 與 21.290%%；依所宣告之規則有 %d 組達 5%%，原報告為 7 組。' % n_large,
    'Rule implemented as stated; both the signed mean and the mean absolute gap are in extension_splice_summary.csv; '
    'Germany 2006-2008 now carries "splice (large gap)"; flags, summaries and pages regenerated.',
    '依所述規則實作；有號平均與平均絕對差距均載於 extension_splice_summary.csv；德國 2006–2008 年現標示「splice (large gap)」；'
    '旗標、摘要與頁面已重新產生。',
    RES, RESZ)
add('F13', 13, 'Ten trend-usability descriptions', '十項趨勢可用性描述', C, CZ,
    'Recomputed continuity and the Eurostat break flags for every series: exactly the ten series the audit named change '
    'category, and no other series does.',
    '重算每組序列之連續性與 Eurostat 斷裂旗標：恰為稽核所列十組序列改變類別，其餘皆無。',
    'Coverage, continuity and comparability are separated: "continuous" is given only to a single-source series with no '
    'missing years inside its span and no publisher-flagged break; the years are listed in data_quality.csv (continuity_detail).',
    '涵蓋、連續性與可比較性分開處理：僅對單一來源、期間內無缺漏年度且無出版機構標示斷裂之序列給予「連續」；年度明細列於 '
    'data_quality.csv（continuity_detail）。',
    RES, RESZ)
add('F14', 14, 'Rejected inputs in the irregular-estimates table', '無證估計表中之被否決輸入值', C, CZ,
    'Compared every record with the current panel: 39 Eurostat detections for Switzerland, Portugal and Sweden are the '
    'year-shifted input values; Taiwan missing-worker counts sit under the overstay variable; Israel components.',
    '逐筆與現行 panel 比對：瑞士、葡萄牙、瑞典之 39 筆 Eurostat 查獲數為位移一年之輸入值；臺灣失聯移工數置於逾期停留變項下；以色列為分項。',
    'Every record has a status (current, valid alternative, rejected, superseded, reclassified, deleted, component) '
    'and a reason; Chile\'s alternatives rebuilt; Taiwan components added.',
    '每筆均有狀態（現行、有效替代值、被否決、被取代、重新歸類、已刪除、分項）與理由；智利之替代值已重建；已加入臺灣之分項。',
    RES, RESZ)
add('F15', 15, 'Country source tables: used_in_panel', '各國來源表：used_in_panel', C, CZ,
    'Recomputed against the panel: 51 records marked yes did not match (39 + 4 + 7 + 1).',
    '與 panel 重新比對：51 筆標示為 yes 者並不相符（39＋4＋7＋1）。',
    'used_in_panel is recomputed for every row, historical_status says why a record is not used, and every current panel '
    'value without a row (extension, corrected, added) was added; country READMEs describe the file correctly.',
    '每列之 used_in_panel 皆已重算，historical_status 說明該筆為何未採用，並為每個尚無對應列之現行 panel 數值（延伸、更正、新增）補列；'
    '各國 README 已正確描述該檔。',
    RES, RESZ)
add('F16', 16, 'Secondary workbook is not an equivalent dataset', '次要活頁簿並非等效資料集', C, CZ,
    'Compared 1,696 primary values: 17 differ. Six of them are values the panel omitted although archived sources support '
    'them (Australia 2015 in the DIBP Annual Report p.63; Japan 2010, 2012, 2013, 2015 in ISA Table 21 p.46; Iceland 2021 '
    'in the archived Eurostat payload).',
    '比對 1,696 個主要數值：17 項不同。其中六項為 panel 遺漏而存檔來源可支持者（澳洲 2015 見 DIBP 年報第 63 頁；日本 2010、2012、2013、2015 '
    '見入國管理局表 21 第 46 頁；冰島 2021 見存檔之 Eurostat 回應）。',
    '%d values added to the panel; every difference has a disposition (secondary_workbook_differences.csv); the workbook is '
    'labelled a historical compilation in the data page and ABOUT_THE_TWO_WORKBOOKS.md.' % n_added,
    '已將 %d 個數值加入 panel；每項差異均有處置（secondary_workbook_differences.csv）；資料頁與 ABOUT_THE_TWO_WORKBOOKS.md '
    '已將該活頁簿標示為歷史彙編。' % n_added,
    RES, RESZ)
add('F17', 17, 'ABOUT_THE_TWO_WORKBOOKS.md is stale', 'ABOUT_THE_TWO_WORKBOOKS.md 已過時', C, CZ,
    'Read the file: first-release counts (2,454 checks, 49 corrections, grades with six D) and a first-release sheet list, undated.',
    '閱讀該檔：載有未標日期之首次發布數字（2,454 筆查核、49 項更正、含 6 筆 D 級之等級）與首次發布之工作表清單。',
    'Rewritten for the 2001-2022 release with computed numbers; first-release figures kept as dated history.',
    '已為 2001–2022 版本重寫並採用計算所得數字；首次發布之數字作為標示日期之歷史保留。',
    RES, RESZ)
add('F18', 18, 'Methods page: stale coverage, grade and denominator statements', '研究方法頁：過時之涵蓋、等級與分母敘述', C, CZ,
    'Checked each: 35 vs 34 countries (35 is right); 10.6% stock coverage (57/880 = 6.5%; 11.0% of 2010-2022 country-years); '
    '"six values graded D" (D = 0); "26 country-years over 3%" (30; 25 in 2010-2022).',
    '逐項查核：35 對 34 國（35 為正確）；存量涵蓋 10.6%（57/880＝6.5%；2010–2022 年國家—年度之 11.0%）；「6 筆 D 級」（D＝0）；'
    '「26 個國家—年度差異超過 3%」（實為 30；2010–2022 年為 25）。',
    'The statements are generated from the data in both languages, with the denominator stated.',
    '各敘述現由資料產生（中英文版），並載明分母。',
    RES, RESZ)
add('F19', 19, 'Known-issue actions and missingness wording', '已知問題之處置建議與缺漏說明', C, CZ,
    'Checked the "other 34 countries" action (35 now), the register-versus-census wording, and the country READMEs.',
    '查核「其他 34 國」之建議（現為 35 國）、登記與普查之用語，以及各國 README。',
    'Annual availability, census availability, attempts and comparability are separated in the issue texts; the counts are '
    'computed; folder descriptions corrected; dated first-release observations kept as history.',
    '問題內容已將逐年可得性、普查可得性、嘗試過程與可比較性分開；數字為計算所得；資料夾描述已更正；標示日期之首次發布觀察保留為歷史。',
    RES, RESZ)
add('F20', 20, 'Grades and the criteria they state', '等級與其所述之判準', C, CZ,
    'Listed grade-A cells whose verification is not a machine-readable decode: exactly 19 (13 Taiwan population, 5 Taiwan '
    'overstay, UK foreign-born 2020).',
    '列出驗證並非機器可讀解出之 A 級格：恰為 19 格（臺灣人口 13、臺灣逾期停留 5、英國外國出生 2020）。',
    'Grades are defined by provenance (A decoded from a machine-readable source; B read from an archived document; C '
    'the midpoint of a published range, computed by the archive; D none, deleted); precision and comparability are kept apart; the 19 were regraded B '
    '(one of the five Taiwan overstay values has since been deleted).',
    '等級依出處定義（A：由機器可讀來源解出；B：讀自已存檔文件；C：本存檔計算之已公布區間中點；D：無，已刪除）；精確度與可比較性另行處理；'
    '該 19 格已改評 B 級（五筆臺灣逾期停留中有一筆其後已刪除）。',
    RES, RESZ)
add('F21', 21, 'Reproducibility and source-artifact routing', '可重現性與來源檔案之指向', C, CZ,
    'Counted the register\'s data_raw/ placeholders (232), looked for the sources/ folders the READMEs describe (none), and '
    'for the build-site.mjs the old report names (not in the archive).',
    '清點來源清冊中 data_raw/ 之佔位符（232 筆）、查找各 README 所述 sources/ 資料夾（不存在），以及舊報告所稱 build-site.mjs（不在本存檔）。',
    'REBUILD.md gives the supported order, names the first-release builders that must not be re-run, and pins the baseline; '
    'all placeholders now name exact files; README text corrected. The first rebuild test was run beside the audit '
    'folder and so could not show that the verification ledger depended on it (re-audit R01); the audit\'s result tables '
    'are now committed (data/audit_inputs/) and the test was repeated in a clone with no sibling folders (REBUILD.md, '
    '"Tested").',
    'REBUILD.md 載明受支援之順序、不得重跑之首次發布建置程式，並固定基準；佔位符現皆指向確切檔案；README 文字已更正；'
    '首次重建測試係在稽核資料夾旁進行，故未能顯現驗證表依賴該資料夾（再稽核 R01）；稽核之結果表現已納入存放庫（data/audit_inputs/），'
    '並於無任何同層資料夾之複本中重做測試（REBUILD.md「Tested」）。',
    RES, RESZ)
add('F22', 22, 'Source reachability claims', '來源可連線性之說法', CQ, CQZ,
    'Re-tested the failures with curl and valid TLS: three URLs return 404 (porCausa, Nisshinkyo, SEM), several block automated '
    'clients (403), two hosts did not answer; the two INE pages that my sweep of the same day had recorded as unreachable '
    'answer on retry. The audit and the archive used different URL sets (193 vs 194 at the time; the archive\'s sweep now covers every URL '
    'the rebuilt site publishes), so the counts differ.',
    '以 curl 並啟用有效 TLS 重測失敗者：三個網址回 404（porCausa、Nisshinkyo、SEM），數個封鎖自動化用戶端（403），兩個主機未回應；'
    '本存檔當日掃描曾記為無法連線之兩個 INE 頁面，重試後可連線。稽核與本存檔所用網址集不同（當時 193 對 194；本存檔之掃描現涵蓋重建後網站所發布之全部網址），故筆數不同。',
    'link_sweep.csv now records the date, the method and the first result of each check; failures are retried with curl and '
    'a transport failure is not called a dead link; each dead URL sits beside its archived copy; no grade D follows from a moved URL.',
    'link_sweep.csv 現記錄每次檢查之日期、方法與首次結果；失敗者以 curl 重試，傳輸失敗不稱為失效連結；每個失效網址旁列有存檔副本；'
    '網址變動不導致 D 級。',
    RES, RESZ)
add('F23', 23, 'Verification totals are comparison records', '查證總數為比對紀錄', C, CZ,
    'The 2,737-row log is 2,454 first-release comparisons plus 283 re-checks; it contains no extension observation.',
    '2,737 列之紀錄為 2,454 筆首次發布之比對加 283 筆複查；不含任何延伸觀測值。',
    'Labelled as comparison records on the index, Verification and README pages; data/current_panel_verification.csv gives '
    'one row per current observation (source, year, unit, concept, grade, how checked, audit result); the chart check is a '
    'source-label validation beside the consistency checks.',
    '已於首頁、查證紀錄頁與 README 標示為比對紀錄；data/current_panel_verification.csv 為現行每筆觀測值一列（來源、年度、單位、概念、等級、'
    '查核方式、稽核結果）；圖表檢查為與一致性檢查並列之來源標示驗證。',
    RES, RESZ)
add('F24', 24, 'Research construct, timing and comparability', '研究概念、時間對齊與可比較性', CQ, CQZ,
    'This is an analytical qualification, not a data error. Recounted the cases with foreign-born below foreign nationals: '
    '25 in the audited revision, %d now (Suriname 2012 no longer, after F03).' % len(below),
    '此為分析上之保留，並非資料錯誤。重算外國出生低於外國籍之案例：稽核版本為 25 個，現為 %d 個（蘇利南 2012 因 F03 而不再屬此）。' % len(below),
    'data/ANALYSIS_NOTES.md sets out the choices (construct, timing, universes, denominators, source families, breaks) and the '
    'sensitivity analyses, with the numbers behind each; the choices themselves are the authors\' to make.',
    'data/ANALYSIS_NOTES.md 列出各項選擇（概念、時間對齊、母體、分母、來源類型、斷裂）與敏感度分析及其數字；選擇本身由作者決定。',
    OPEN, OPENZ)

RA = {
    'F05': ('Re-audit R11: the Chinese definition of detections per 1,000 residents and the README term list still said 人次; '
            'now 查獲數 with the unit named per source (人數 for Eurostat, 人次 for Mexico), and the Eurostat texts say 人數.',
            '再稽核 R11：每千名居民查獲數之中文定義與 README 詞彙表仍用「人次」；現為「查獲數」並依來源載明單位（Eurostat 為人數、墨西哥為人次），'
            'Eurostat 相關文字一律為「人數」。'),
    'F11': ('Re-audit R02: the same blanket rule survived in the known-issues row for Eurostat / OECD; now source-specific.',
            '再稽核 R02：同一種一律基準之說法仍留在 Eurostat／OECD 之已知問題列；現已改依來源。'),
    'F12': ('Re-audit R03: the known-issues summary, the extract notes, the README and the Verification table still selected on '
            'the signed mean; all now use the mean absolute gap (%d series, %d cells) and show both statistics.' % (n_large, n_large_cells),
            '再稽核 R03：已知問題摘要、分析用資料集說明、README 與查證紀錄頁之表格仍以有號平均篩選；現一律採平均絕對差距'
            '（%d 組序列、%d 筆數值），並同時列出兩項統計。' % (n_large, n_large_cells)),
    'F13': ('Re-audit R04: four publisher break flags on Eurostat detections (France 2014, Netherlands 2015, Sweden 2014 and 2015) '
            'were not carried; they are now a flag column and the three series are no longer rated continuous.',
            '再稽核 R04：Eurostat 查獲數有四筆出版機構之斷裂旗標（法國 2014、荷蘭 2015、瑞典 2014 與 2015）未被帶入；'
            '現已成為旗標欄，且這三組序列不再評為連續。'),
    'F17': ('Re-audit R09: the guide now separates the %d present differences from the %d disposition records, and the README '
            'freezes its first-release block.' % (int((sec.status_now == 'in secondary workbook only').sum()), len(sec)),
            '再稽核 R09：說明現區分 %d 項現存差異與 %d 筆處置紀錄，README 之首次發布區塊亦已凍結。'
            % (int((sec.status_now == 'in secondary workbook only').sum()), len(sec))),
    'F20': ('Re-audit R05: grade C overlapped A and B; the grades are now mutually exclusive and C is only a midpoint the archive computed.',
            '再稽核 R05：等級 C 與 A、B 重疊；現各等級互斥，C 級僅限本存檔計算之中點。'),
}
for r_ in R:
    if r_['finding'] in RA:
        r_['resolution'] = r_['resolution'] + ' ' + RA[r_['finding']][0]
        r_['resolution_zh'] = r_['resolution_zh'] + RA[r_['finding']][1]
resp = pd.DataFrame(R)
assert len(resp) == 24
resp.to_csv(os.path.join(D, 'audit_response_%s.csv' % WHEN), index=False, encoding='utf-8-sig')

# ------------------------------------------------------------------ the re-audit of commit 30d6cb1
RR = []
n = lambda x: format(int(x), ',')


def radd(f, no, title, title_zh, checked, checked_zh, result, result_zh):
    RR.append(dict(finding=f, issue=no, title=title, title_zh=title_zh, verdict=C, verdict_zh=CZ, checked=checked,
                   checked_zh=checked_zh, resolution=result, resolution_zh=result_zh, status=RES, status_zh=RESZ))


ledger = pd.read_csv(os.path.join(D, 'current_panel_verification.csv'))
n_led = len(ledger)
radd('R01', 21, 'Isolated rebuild loses the audit statuses', '獨立重建遺失稽核結果',
     'Ran step 82 in a clone of the commit placed in an otherwise empty folder: 3,328 of the 3,365 audit statuses became "not in '
     'the audited revision". The earlier rebuild test had been run beside the audit folder, which is why it did not show this.',
     '於僅含該 commit 複本之空資料夾中執行步驟 82：3,365 筆稽核結果中有 3,328 筆變為「not in the audited revision」。'
     '先前之重建測試係在稽核資料夾旁進行，故未顯現此問題。',
     'The independent audit\'s result tables, which cover all %s observations, are committed in data/audit_inputs/ and read from '
     'there; step 82 stops with a message if they are missing or do not cover an observation. The rebuild test was repeated in a '
     'clone with no sibling folders (REBUILD.md, "Tested"), and the F21 disposition says what was tested.' % n(n_led),
     '稽核之結果表（涵蓋全部 %s 筆觀測值）已納入 data/audit_inputs/ 並由該處讀取；若缺漏或未涵蓋某筆觀測值，步驟 82 即停止並說明。'
     '已於無任何同層資料夾之複本中重做重建測試（REBUILD.md「Tested」），F21 之處置亦已改為載明實際測試之內容。' % n(n_led))
radd('R02', 11, 'Blanket 1 January rule left in the known issues', '已知問題中仍有一律以 1 月 1 日為基準之說法',
     'The INFO row "Eurostat / OECD countries" of known_issues.csv (and its copies in the workbook and on the Verification '
     'pages) said that Eurostat and OECD stocks are measured at 1 January. All 22 Australian foreign-born cells are 30 June.',
     'known_issues.csv 之 INFO 列「Eurostat / OECD countries」（及其於活頁簿與查證紀錄頁之副本）稱 Eurostat 與 OECD 存量均以 1 月 1 日為基準。'
     '澳洲 22 筆外國出生人口格均為 6 月 30 日。',
     'The row now states the source-specific rule in both languages (Eurostat 1 January; OECD by national source; Taiwan and Korea '
     'year-end). No value was shifted.',
     '該列現以兩種語言載明依來源之規則（Eurostat 為 1 月 1 日；OECD 依各國來源；臺灣與南韓為年底）。未移動任何數值。')
radd('R03', 12, 'Signed mean still used in known-issue summaries', '已知問題摘要仍採有號平均',
     'scripts/75 selected on the signed mean: 7 series and 15 cells in the known-issues row. Recomputed from the splice summary: '
     '%d series and %d cells by the mean absolute gap (Germany foreign-born: signed +1.6%%, mean absolute 7.4%%). The same selection '
     'was in the extract notes, the README, the extension entry of the revision history and the Verification table.' % (n_large, n_large_cells),
     'scripts/75 以有號平均篩選：已知問題列為 7 組序列、15 筆數值。依接合摘要重算，以平均絕對差距計為 %d 組序列、%d 筆數值'
     '（德國外國出生：有號 +1.6%%、平均絕對 7.4%%）。分析用資料集說明、README、修訂紀錄之延伸條目與查證紀錄頁之表格亦有相同之篩選。' % (n_large, n_large_cells),
     'Every current summary and flag definition uses the mean absolute gap (%d series, %d cells, Germany included); the signed mean is '
     'reported beside it and named as such. The extension\'s own revision-history entry keeps its original wording (7 flagged at that time).' % (n_large, n_large_cells),
     '所有現行摘要與旗標定義均採平均絕對差距（%d 組序列、%d 筆數值，含德國）；有號平均並列且標明。延伸之修訂紀錄條目維持原敘述（當時標示 7 組）。' % (n_large, n_large_cells))
radd('R04', 13, 'Publisher break flags on detections not carried', '查獲數之出版機構斷裂旗標未帶入',
     'Decoded the status flags of the archived Eurostat migr_eipre payload: "b" (break in time series) on FR 2014 (96,375), NL 2015 '
     '(3,150), SE 2014 (72,835) and SE 2015 (1,445). All four values match the publisher. The three "d" flags are on the EU27 '
     'aggregate, which the panel does not hold.',
     '解碼所存檔 Eurostat migr_eipre 之狀態旗標：FR 2014（96,375）、NL 2015（3,150）、SE 2014（72,835）、SE 2015（1,445）標示「b」'
     '（時間序列斷裂）。四筆數值與出版機構一致。三個「d」旗標屬 EU27 彙總，panel 未持有。',
     'New column irregular_proxy_detections_flag carries the Eurostat flag on those four cells (values unchanged); it reaches the '
     'analysis extract (detections_flag), the ledger and the evidence pages. data_quality.csv now rates the France, Netherlands and '
     'Sweden detection series "single source, but the publisher flags a break" and lists the years; a known-issue row explains it.',
     '新增 irregular_proxy_detections_flag 欄，於該四格載明 Eurostat 旗標（數值不變）；旗標進入分析用資料集（detections_flag）、驗證表與佐證頁。'
     'data_quality.csv 現將法國、荷蘭、瑞典之查獲數序列評為「單一來源，但出版機構標示序列有斷裂」並列出年度；已知問題另有一列說明。')
radd('R05', 20, 'Grade C overlaps A and B', '等級 C 與 A、B 重疊',
     'Counted: 38 UN migrant-stock estimates are graded A, and 44 irregular-stock estimates other than range midpoints are A (5) or B '
     '(39); only the 13 range midpoints are C. The stated criterion for C ("a published estimate or range") did not separate them.',
     '清點：38 筆 UN 移民存量推估為 A 級；44 筆非區間中點之無證存量推估為 A（5）或 B（39）；僅 13 筆區間中點為 C。'
     '所述 C 級判準（「公布之推估值或區間」）無法區分它們。',
     'The grades are mutually exclusive provenance classes: A decoded from a machine-readable source, B read from an archived document '
     '(both may hold publisher estimates, which the cell note and the source type identify), C only the midpoint of a published range '
     'that the archive computed, D none. Rewritten in the methods page, both codebooks, the workbook README, the README and the '
     'extract. No grade changed.',
     '各等級為互斥之出處類別：A＝自機器可讀來源解出、B＝自已存檔文件讀取（兩者皆可能是出版機構之推估值，由各格備註與來源類型標明）、'
     'C＝僅限本存檔計算之已公布區間中點、D＝無。已改寫於研究方法頁、兩份變數說明書、活頁簿 README、README 與分析用資料集。未變更任何等級。')
radd('R06', 27, 'Verification ledger: check methods and population dates', '驗證表：查核方式與人口日期',
     'Of the %s ledger rows, 905 observations decoded from machine-readable files (880 UN WPP, 11 Taiwan MOI, 9 Korea MOJ, 5 ISMU) '
     'were described as read from an archived document, and all 880 population rows had an empty reference date.' % n(n_led),
     '於 %s 列驗證表中，905 筆實為自機器可讀檔解出之觀測值（UN WPP 880、臺灣內政部 11、南韓法務部 9、ISMU 5）被描述為自存檔文件讀取，'
     '且 880 筆人口列之參照日期為空白。' % n(n_led),
     'The check method now comes from the audit\'s record of the source family; the population date follows the declared convention '
     '(World Bank mid-year, Taiwan registered year-end) and claims no finer day. All %s keys and values are unchanged.' % n(n_led),
     '查核方式現取自稽核對來源類別之記錄；人口日期依所宣告之慣例（世界銀行為年中、臺灣為戶籍登記年底），不主張更精確之日期。'
     '全部 %s 筆鍵與數值不變。' % n(n_led))
radd('R07', 28, 'Croatia 2011 derivation unflagged; derived categories wrong', '克羅埃西亞 2011 推導值未標示；推導類別有誤',
     'The census table prints foreign citizens (22,527) and stateless persons (749) separately; 23,276 is their sum and was not marked '
     'derived. The codebook counted 16 derived values as 13 midpoints and 3 UK subtractions; there are 2 UK subtractions, and Suriname '
     '2012 is a sum.',
     '普查表分別列出外國公民（22,527）與無國籍者（749）；23,276 為其加總，原未標示為推導值。變數說明書將 16 筆推導值記為 13 筆中點與 '
     '3 筆英國減法；實際英國減法為 2 筆，蘇利南 2012 為加總。',
     'Croatia 2011 is flagged derived with its derivation (value unchanged). The codebook classifies from the data: 17 derived values, '
     '13 midpoints, 2 differences and 2 sums. Russia 2002 and India 2001 stay unflagged because their totals are printed.',
     '克羅埃西亞 2011 已標示為推導值並載明推導方式（數值不變）。變數說明書依資料分類：17 筆推導值，13 筆中點、2 筆差、2 筆加總。'
     '俄羅斯 2002 與印度 2001 因其總數為直接印出，維持未標示。')
radd('R08', 29, 'Splice table in the analysis notes has the wrong columns', '分析說明之接合表欄位錯誤',
     'The Markdown table has four header cells and five cells in each of its eight rows, so GitHub shows the variable under "Mean gap" '
     'and drops the overlap count.',
     'Markdown 表標頭為四欄，但八列資料各為五格，GitHub 因此將變項顯示於「Mean gap」之下並捨棄重疊年數。',
     'The generator writes five columns (country, variable, signed mean gap, mean absolute gap, overlap years) and five separators; '
     'the table lists the %d series of the corrected rule.' % n_large,
     '產生程式現輸出五欄（國家、變項、有號平均差距、平均絕對差距、重疊年數）及五個分隔線；表列依更正後之規則共 %d 組序列。' % n_large)
radd('R09', 17, 'Present differences and historical counts conflated', '現存差異與歷史計數混用',
     'The workbook guide said the secondary workbook differs in 31 of 1,696 values; 25 differ now and 6 more records are first-release '
     'omissions since added. The README\'s first-release block quoted the current 67 corrections and 88 citations, and "2,478 displayed '
     'values" counted six variables only.',
     '活頁簿說明稱次要活頁簿於 1,696 個數值中有 31 項差異；現存差異為 25 項，另 6 筆為首次發布時遺漏而後已補入者。'
     'README 之首次發布區塊引用了現行之 67 筆更正與 88 筆文件引用，且「2,478 個顯示數值」僅計六個變項。',
     'The guide says 25 present differences plus 6 resolved omissions (31 disposition records). The README freezes the first-release block at '
     'the published figures (49 corrections in 5 countries; 76 of 78 citations) and gives the current figures separately, with the grade '
     'totals labelled (six variables 2,478; with the seven Taiwan absconded-worker values 2,485).',
     '說明現載明 25 項現存差異加 6 筆已解決之遺漏（共 31 筆處置紀錄）。README 將首次發布區塊凍結於當時所發布之數字'
     '（5 國 49 筆更正；78 筆引用中 76 筆），現況數字另列，並標明等級合計（六個變項 2,478；加計七筆臺灣失聯移工數值為 2,485）。')
radd('R10', 30, 'Overstayer definitions: estimates and a broader Australian measure', '逾期停留之定義：推估數與範圍較廣之澳洲指標',
     'Read the sources: Australia 2015 (62,000) and 2016 (64,600) are departmental estimates of unlawful non-citizens in the community, '
     'a broader group than overstayers; Japan Table 21 gives an estimated number; New Zealand is a register-derived estimate; Korea and '
     'Taiwan are register counts; Israel is one component.',
     '查閱來源：澳洲 2015（62,000）與 2016（64,600）為移民部對社區內非法非公民之估計，範圍較逾期停留者為廣；日本表 21 為估計數；'
     '紐西蘭為依登記資料之推估；南韓與臺灣為登記數；以色列僅為一個組成部分。',
     'The codebooks, methods page, analysis notes and ledger now call the column a heterogeneous stock proxy and state, per country, '
     'whether a cell is a register count, an estimate, a broader group or a component. No value changed.',
     '變數說明書、研究方法頁、分析說明與驗證表現將此欄稱為異質之存量代理指標，並逐國載明各格屬登記數、推估數、較廣之群體或組成部分。'
     '未變更任何數值。')
radd('R11', 5, 'Chinese per-1,000 detections label kept 人次', '每千名居民查獲數之中文標籤仍用「人次」',
     'The Chinese definition of detections per 1,000 residents read 每千名居民之查獲人次, applied to Eurostat person counts as well as '
     'Mexican event counts; the README term list and four Chinese texts about the Eurostat series kept 人次.',
     '每千名居民查獲數之中文定義為「每千名居民之查獲人次」，同時適用於 Eurostat 之人數與墨西哥之事件數；README 詞彙表與四處關於 Eurostat '
     '序列之中文敘述仍用「人次」。',
     'Source-neutral label 每千名居民之查獲數 with the unit per source (人數 for Eurostat, 人次 for Mexico); the Eurostat texts say '
     '人數. The F05 response above now says what was changed and when.',
     '改為不分來源之標籤「每千名居民之查獲數」並依來源載明單位（Eurostat 為人數、墨西哥為人次）；Eurostat 相關敘述一律為「人數」。上列 F05 之回覆亦已載明更動內容。')
rresp = pd.DataFrame(RR)
assert len(rresp) == 11
rresp.to_csv(os.path.join(D, 'reaudit_response_%s.csv' % WHEN), index=False, encoding='utf-8-sig')

# ------------------------------------------------------------------ the markdown record
extra = [
    ('Taiwan absconded workers 2019', 'The cell held 47,632 (31 July 2019) in a year-end column; the Ministry of Labor Table 12-7 year-end value is 48,491. Replaced; 47,632 kept as an alternative.'),
    ('Omitted values the archived sources support', 'Australia 2015, Japan 2010/2012/2013/2015 and Iceland 2021 detections (see F16).'),
    ('Typed counts that had gone stale', 'Several counts typed into prose (stock coverage, the six D grades, 13/40 and 5/40 countries, 156 evidence pages) were replaced by counts computed from the data files.'),
    ('Chile press release', 'The INE press release of 29 December 2023 gives 107,223 irregular residents at 31 December 2022 (6.6%); it differs from both chart series for 2022 and is kept as an alternative.'),
]
md = ['# Response to the audit of %s' % WHEN, '',
      'Each of the 24 findings (GitHub issues #1-#24, tracker #25) was re-checked against the archived source before anything was '
      'changed; where the archive held nothing, against the publisher\'s own page. **All 24 were confirmed** (%d with '
      'a qualification, stated in the table). What changed is in `data/audit_changes_%s.csv` (every cell), `data/corrections_applied.csv`, '
      '`data/deleted_values.csv` and the revision history on the Verification page.' % (int(resp.verdict.str.contains('qualification').sum()), WHEN), '',
      '| Finding | Verdict | Status | What was checked | What changed |', '|---|---|---|---|---|']
for r in R:
    md.append('| **%s** %s (#%d) | %s | %s | %s | %s |' % (r['finding'], r['title'], r['issue'], r['verdict'], r['status'],
                                                          r['checked'].replace('|', '/'), r['resolution'].replace('|', '/')))
md += ['', '## Re-audit of commit 30d6cb1 (%s)' % WHEN, '',
       'An independent re-audit of the revision that contained the response above found %d further defects. Each was checked '
       'against the archived source, the data files or a clean rebuild before anything was changed; **all %d were confirmed**. '
       'Seven earlier issues were reopened and four were opened (#27-#30).' % (len(rresp), len(rresp)), '',
       '| Finding | Verdict | Status | What was checked | What changed |', '|---|---|---|---|---|']
for r in RR:
    md.append('| **%s** %s (#%d) | %s | %s | %s | %s |' % (r['finding'], r['title'], r['issue'], r['verdict'], r['status'],
                                                          r['checked'].replace('|', '/'), r['resolution'].replace('|', '/')))
md += ['', '## Found while checking, not in the audit', ''] + ['- **%s.** %s' % e for e in extra]
md += ['', '## What stays with the authors', '',
       '- the Chile methodology (the 2023 methodology was chosen for every year; the 2022 series is the alternative);',
       '- whether the Taiwan overstay series should be the all-category total (kept) or the foreign-national component;',
       '- whether the 20 UN citizenship-basis cells should be dropped, kept apart, or tested against national citizenship counts;',
       '- whether to add the Australian 2021 and South African 2011 census citizenship counts, and under which universe;',
       '- the research construct and timing rules (`data/ANALYSIS_NOTES.md`).', '']
open(os.path.join(SITE, 'verification', 'AUDIT_RESPONSE_%s.md' % WHEN), 'w', encoding='utf-8', newline='\n').write('\n'.join(md))
print('audit response written: %d findings; %s; re-audit: %d findings' % (len(resp), resp.status.value_counts().to_dict(), len(rresp)))
