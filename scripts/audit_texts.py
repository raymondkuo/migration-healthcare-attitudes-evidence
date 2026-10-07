# -*- coding: utf-8 -*-
"""English and Traditional Chinese text added or rewritten after the audit of 2026-10-07.

Kept in one place so 75_build_derived_tables.py (known issues, codebook, data quality) and the
page builders read the same wording. Numbers come from counts.py, never typed in.
"""
import counts as K

WHEN = '2026-10-07'

# ---------------------------------------------------------------- data_quality comparability text
COMPARABILITY_EN = {
    'population': 'Directly comparable. World Bank WDI mid-year for 39 countries; Taiwan is the registered '
                  '(household-registration) year-end population, which excludes foreign residents.',
    'foreign_born': 'Comparable in concept (born abroad) but sources differ in date and basis (Eurostat 1 January; '
                    'OECD dates vary by country; UN DESA benchmark years, citizenship basis for some countries). '
                    'Includes naturalised citizens.',
    'foreign_nationals': 'Closest match to "non-nationals". Not compiled as an annual series by every country; '
                         'affected by naturalisation rates, so not a pure migration indicator. Some countries '
                         'have census years only.',
    'irregular_stock': 'Not comparable across countries. Estimation method, year and definition differ.',
    'irregular_proxy_overstayers': 'Not comparable across countries. Administrative register count; counts only '
                                   'those already recorded, and the universe differs by country.',
    'irregular_proxy_detections': 'Not comparable across countries, and an annual FLOW of detections, not a stock. '
                                  'Unit differs by source (Eurostat: persons, once per year; Mexico: events). '
                                  'Driven by enforcement intensity and position on migration routes.',
}
COMPARABILITY_ZH = {
    'population': '可直接跨國比較。39 國採世界銀行 WDI 年中人口；臺灣為內政部年底戶籍登記人口，不含外國居民。',
    'foreign_born': '概念上可比較（出生於國外），但各來源之日期與基礎不同（Eurostat 為 1 月 1 日、OECD 依各國而異、'
                    'UN DESA 為基準年，部分國家為公民身分基礎）。已包含歸化取得公民身分者。',
    'foreign_nationals': '最接近「非本國籍」之定義。並非每個國家都編製逐年序列；亦受歸化率影響，'
                         '故非純粹之移民指標。部分國家僅有普查年度。',
    'irregular_stock': '不可跨國比較。各國推估方法、年度與定義均不相同。',
    'irregular_proxy_overstayers': '不可跨國比較。屬行政登記數，僅涵蓋已被登錄者，且各國涵蓋之母體不同。',
    'irregular_proxy_detections': '不可跨國比較，且屬執法查獲之年度「流量」而非「存量」。'
                                  '計量單位因來源而異（Eurostat：人數，同年內每人僅計一次；墨西哥：事件數）。'
                                  '數值受查緝強度與該國在移民路線上的位置影響。',
}

# ---------------------------------------------------------------- trend-usability categories
USABLE_EN = {
    'gaps': 'CAUTION - single source, but years are missing inside the span',
    'break': 'CAUTION - single source, but the publisher flags a break in the series',
    'both': 'CAUTION - single source, with missing years inside the span and a publisher-flagged break',
}
USABLE_ZH = {
    USABLE_EN['gaps']: 'CAUTION｜單一來源，但涵蓋期間內有缺漏年度',
    USABLE_EN['break']: 'CAUTION｜單一來源，但出版機構標示序列有斷裂',
    USABLE_EN['both']: 'CAUTION｜單一來源，但期間內有缺漏年度且出版機構標示序列有斷裂',
}

# ---------------------------------------------------------------- codebook edits: (name, field, en, zh)
CODEBOOK_EDITS = {
    'irregular_proxy_detections': dict(
        definition='Persons found or apprehended as illegally present during the calendar year, as the source '
                   'counts them. Eurostat (migr_eipre): third-country nationals found to be illegally present.',
        definition_zh='於該曆年被查獲或逮捕為非法在留之人，依來源之計算方式。Eurostat（migr_eipre）：被查獲非法在留之第三國國民。',
        caution='An annual FLOW of enforcement detections, NOT a stock and not an estimate of the unauthorised '
                'population. The unit differs by source: Eurostat counts persons, each once within the reference '
                'year, rounded to the nearest 5; Mexico counts EVENTS (a person can be recorded more than once); '
                'Turkey counts irregular migrants apprehended, Syrians under temporary protection excluded. The '
                'same person can appear in different years.',
        caution_zh='為執法查獲之年度「流量」，並非存量，亦非對無證人口之估計。計量單位因來源而異：'
                   'Eurostat 計人數，同一參考年內每人僅計一次，並四捨五入至最接近之 5；'
                   '墨西哥計「事件數」（同一人可被重複記錄）；土耳其計被逮捕之非常規移民，不含受臨時保護之敘利亞人。'
                   '同一人可出現於不同年度。'),
    'irregular_proxy_detections_per_1000_pop': dict(
        caution='Provided because a raw flow is not comparable to a stock share; the unit differs by source (see '
                'irregular_proxy_detections).',
        caution_zh='因原始流量無法與存量占比比較而提供；計量單位因來源而異（見 irregular_proxy_detections）。'),
    '*_ref_date': dict(
        caution='Dates differ by source and are kept per value. Eurostat stocks are 1 January. OECD dates follow '
                'the national source: 30 June for Australia\'s foreign-born, 1 January for the foreign population '
                'of Japan, Turkey, the United Kingdom and Germany, no stated date for several survey- or census-'
                'based series. Taiwan and Korea registers are year-end. Years are as the publisher labels them; '
                'no value was shifted to another year.',
        caution_zh='基準日因來源而異，並逐值保留。Eurostat 存量為 1 月 1 日。OECD 之日期依各國來源：澳洲外國出生人口為 6 月 30 日，'
                   '日本、土耳其、英國與德國之外國人口為 1 月 1 日，若干以調查或普查為基礎之序列未載明日期。'
                   '臺灣與南韓之登記數為年底。年度一律依出版機構之標示，未將任何數值移至其他年度。'),
    '*_grade': dict(
        definition='Provenance grade for that cell. A = decoded from a machine-readable official source and '
                   'matched exactly; B = read from an archived document in which the value appears, or summed '
                   'from figures printed there; C = published estimate or range (point estimate or midpoint); '
                   'D = no archived source (none are published).',
        definition_zh='該格之出處等級。A＝自機器可讀之官方來源解出並完全一致；B＝自已存檔之文件讀取，或由文件中所印數字加總；'
                      'C＝公布之推估值或區間（點估計或中點）；D＝無存檔來源（現無此類數值）。',
        caution='A grade says where a value was read from. It does not say how precise it is, whether the quantity '
                'is comparable across countries or years, or whether the source\'s own estimate is accurate. '
                'Grades of first-release values were assigned under an earlier wording; of the 19 grade-A values that '
                'rest on documents, 18 were regraded B on 2026-10-07 and one (Taiwan overstayers 2021) was deleted.',
        caution_zh='等級表示數值「讀自何處」，並不表示其精確程度、該量是否可跨國或跨年度比較，或來源本身之估計是否準確。'
                   '首次發布之數值依較早之文字標準評級；2026-10-07 已將 19 筆依賴文件之 A 級數值中的 18 筆改評為 B 級，1 筆（臺灣 2021 年逾期停留）已刪除。'),
    'population': dict(
        caution='Verified: all %d World Bank values come from the archived live API response. Taiwan is the registered '
                '(household-registration) population, which excludes foreign residents, so its shares have a '
                'different denominator from every other country; 2001-2009 is rounded to thousands, 2010-2022 is '
                'exact.' % K.N_WB,
        caution_zh='已查證：%d 筆世界銀行數值皆來自所存檔之線上 API 回應。臺灣為戶籍登記人口，不含外國居民，'
                   '故其占比之分母與其他國家不同；2001–2009 年四捨五入至千位，2010–2022 年為精確值。' % K.N_WB),
    'foreign_born': dict(
        caution='Includes naturalised citizens, so it usually exceeds foreign_nationals (%d country-years do not: '
                'data/foreign_born_below_foreign_nationals.csv; no ordering was forced). BIRTHPLACE counts only in '
                'the analysis extract: UN DESA stocks that UN declares on a citizenship basis are marked in '
                'foreign_born_concept and held apart there.' % K.N_BELOW,
        caution_zh='包含歸化者，故通常大於 foreign_nationals（有 %d 個國家—年度並非如此：'
                   'data/foreign_born_below_foreign_nationals.csv；未強行排序）。分析用資料集僅含依出生地計算者：'
                   'UN DESA 宣告以公民身分為基礎之存量，於 foreign_born_concept 標明並於該資料集中分開存放。' % K.N_BELOW),
}
CODEBOOK_NEW = [
    ('foreign_born_concept',
     'What the foreign_born cell counts: "born abroad (country of birth)" or, for UN DESA stocks that UN declares on a '
     'citizenship basis (data type C), "UN migrant stock on a citizenship basis, not birthplace".',
     'Filter on this to keep strictly birthplace counts. The citizenship-basis cells are not moved into foreign_nationals: '
     'their population universe and estimate status have not been checked against national citizenship counts.',
     '該筆外國出生人口數所計為何：「born abroad (country of birth)」，或對於 UN DESA 宣告以公民身分為基礎（資料類型 C）之存量，'
     '標示為「UN migrant stock on a citizenship basis, not birthplace」。',
     '依此欄篩選即可僅保留依出生地計算之數值。公民身分基礎之各格並未移入 foreign_nationals：其母體範圍與推估性質尚未對照各國公民身分統計查核。'),
]


# ---------------------------------------------------------------- known issues: rewritten and new rows
def known_issues():
    c = K
    fn_n = c.N_FN_COUNTRIES
    return [
        dict(severity='HIGH', scope='all', variable='irregular_stock / overstayers / detections',
             issue='No internationally comparable measure of the irregular population exists. irregular_stock covers '
                   '%d/40 countries, overstayers %d/40, detections %d/40, and the three are not additive or '
                   'interchangeable. They start in 2010: nothing earlier was collected for them.'
                   % (c.N_IRR_C, c.N_OVS_C, c.N_DET_C),
             issue_zh='不存在任何可跨國比較之無證人口指標。irregular_stock 涵蓋 40 國中的 %d 國，overstayers 涵蓋 %d 國，'
                      'detections 涵蓋 %d 國，且三者不可相加或互換。三者自 2010 年起，更早年度未蒐集。'
                      % (c.N_IRR_C, c.N_OVS_C, c.N_DET_C),
             evidence='data/data_quality.csv and the Coverage sheet of the analysis extract.',
             evidence_zh='data/data_quality.csv 與分析用資料集之 Coverage 工作表。',
             action='Use at most as an ordinal salience signal; see the methods page.',
             action_zh='至多作為順序尺度之議題顯著性指標；見研究方法頁面。'),
        dict(severity='MEDIUM', scope='Australia, India, Israel, New Zealand, Russia, South Africa',
             variable='foreign_nationals',
             issue='Australia, India, Israel, New Zealand and South Africa have no foreign-national values, and Russia has '
                   'one census value (2002). None of them has an ANNUAL register of the kind Eurostat and the OECD '
                   'collect, so the OECD B15 and Eurostat tables hold nothing for them. That is not the same as '
                   'having no census count: Australia\'s 2021 Census gives 2,808,214 people who are not Australian '
                   'citizens (5.1% did not state), and South Africa\'s 2011 Census gives 1,692,242 who answered "No" to '
                   'South African citizenship (the table covers 50,641,580 of 51,770,560). These are candidates, not '
                   'yet added: their universes (not stated, visitors, stateless persons) have not been settled.',
             issue_zh='澳洲、印度、以色列、紐西蘭與南非沒有外國籍人口數值，俄羅斯僅有單一普查數值（2002 年）。'
                      '這些國家均無 Eurostat 與 OECD 所蒐集之那種「逐年」登記統計，故 OECD B15 與 Eurostat 表中無其資料。'
                      '但這並不等於沒有普查數：澳洲 2021 年普查有 2,808,214 人非澳洲公民（5.1% 未填答），南非 2011 年普查有 1,692,242 人'
                      '對「是否為南非公民」回答「否」（該表涵蓋 51,770,560 人中的 50,641,580 人）。'
                      '這些是候選資料，尚未加入：其母體範圍（未填答、訪客、無國籍者）尚待釐清。',
             evidence='ABS 2021 Census QuickStats (Not an Australian citizen, national total); Statistics South Africa, '
                      'Census 2011 in Brief, Table 2.17. Audit findings F09 and F10, 2026-10-07.',
             evidence_zh='澳洲統計局 2021 年普查 QuickStats（非澳洲公民，全國總數）；南非統計局《2011 年普查簡報》表 2.17。'
                         '稽核發現 F09 與 F10，2026-10-07。',
             action='Left empty rather than approximated. Use foreign_born for these countries, noting that it counts '
                    'naturalised citizens, or restrict the model to the %d countries that have foreign_nationals. A '
                    'census year may be added once the universe is agreed; annual blanks are never interpolated.' % fn_n,
             action_zh='保留空白而不作近似推估。對這些國家可改用 foreign_born（須注意其包含歸化者），'
                       '或將模型限於有 foreign_nationals 之 %d 國。待母體範圍確定後可加入普查年度；逐年空白絕不內插。' % fn_n),
        dict(severity='MEDIUM', scope='China, India, Philippines, Suriname, Thailand', variable='foreign_born',
             issue='UN DESA\'s own file declares the migrant stock of these countries (and of Japan and Taiwan) to be '
                   'based on foreign citizens (data type C). The panel carries them in foreign_born for 2005, 2010, 2015 '
                   'and 2020 (20 cells). The values reproduce the UN workbook exactly, but they are citizenship-based '
                   'international migrant stock and are not birthplace counts. Whether UN\'s declaration describes what '
                   'was counted is not something the numbers can show.',
             issue_zh='UN DESA 自身之檔案將這些國家（以及日本與臺灣）之移民存量宣告為以外國公民為基礎（資料類型 C）。'
                      '本 panel 於 2005、2010、2015、2020 年將其列於 foreign_born（共 20 格）。這些數值與 UN 活頁簿完全一致，'
                      '但屬公民身分基礎之國際移民存量，並非依出生地計算。UN 之宣告是否描述實際計算內容，無法由數字本身判定。',
             evidence='evidence/api/UN_DESA_IMS2024_stock_by_sex_and_destination.xlsx, Table 1, column "Data type".',
             evidence_zh='evidence/api/UN_DESA_IMS2024_stock_by_sex_and_destination.xlsx，Table 1，「Data type」欄。',
             action='Flagged ("declared citizenship basis") and marked in foreign_born_concept. In the analysis extract '
                    'they are held in the separate columns un_stock_citizenship_basis (and its share), so foreign_born '
                    'there is birthplace only. Not moved to foreign_nationals: that would need a universe check against '
                    'national citizenship counts. Until UN DESA confirms the basis, treat them as the UN '
                    '"international migrant stock".',
             action_zh='已加註旗標（「declared citizenship basis」）並於 foreign_born_concept 標明。分析用資料集中，這些數值存放於'
                       '獨立欄位 un_stock_citizenship_basis（及其占比），故該處之 foreign_born 僅含依出生地計算者。'
                       '未移入 foreign_nationals：那需要先對照各國公民身分統計查核母體範圍。在 UN DESA 確認其基礎之前，'
                       '請將其視為聯合國之「國際移民存量」。'),
        dict(severity='MEDIUM', scope='Not collected for 2001-2009', variable='foreign_born / foreign_nationals',
             issue='Looked for and not collected: Chile\'s 2002 census foreign-born count (the INE document retrieved gives '
                   'only the 1.27% share; the longer report did not download completely and was not retried). Australia '
                   'foreign nationals was reported as unobtainable on 2026-10-07; that was wrong for the 2021 census year '
                   '(see the row on census counts above). Not attempted, because each would add a single census year to an '
                   'otherwise empty series: Germany foreign-born before 2006, the 2001/2002 census counts for Bulgaria, '
                   'Croatia, Czechia, Poland, Portugal and Slovakia, and census years for China, the Philippines, Suriname '
                   'and Thailand. No comparable source is known for Japan (foreign-born) or for Israel and New Zealand '
                   '(foreign nationals).',
             issue_zh='已尋找但未蒐集：智利 2002 年普查外國出生人數（所取得之 INE 文件僅載有 1.27% 之比例；較長之報告下載未完整，且未再嘗試）。'
                      '澳洲外國籍人口曾於 2026-10-07 被回報為無法取得；就 2021 年普查而言該說法有誤（見上方普查數之列）。'
                      '未嘗試者，因各僅能為原本空白之序列增加單一普查年度：德國 2006 年前之外國出生、保加利亞、克羅埃西亞、捷克、波蘭、'
                      '葡萄牙、斯洛伐克之 2001／2002 年普查數，以及中國、菲律賓、蘇利南、泰國之普查年度。'
                      '日本（外國出生）、以色列與紐西蘭（外國籍）則無已知之可比較來源。',
             evidence='Attempts and their outcomes are recorded in the revision history of 2026-10-07 and in the per-country '
                      'evidence folders.',
             evidence_zh='嘗試與結果見 2026-10-07 之修訂紀錄與各國證據資料夾。',
             action='Left empty rather than approximated. Coverage by country and variable is in data_quality.csv and on '
                    'the Coverage sheet of the analysis extract.',
             action_zh='保留空白而不作近似推估。各國各變項之涵蓋情形見 data_quality.csv 與分析用資料集之 Coverage 工作表。'),
        dict(severity='RESOLVED', scope='Chile', variable='irregular_stock',
             issue='The first release assigned the five 2018-2022 values to the wrong years and mixed the 2022 and 2023 '
                   'INE methodologies: the chart on page 12 of the INE/SERMIG Sintesis 2023 shows 2021, 2022 and 2023 '
                   '(2022 methodology) where the panel had 2018-2020, and 2020 and 2021 (2023 methodology) where it had '
                   '2021-2022 (audit F01).',
             issue_zh='首次發布將 2018–2022 年五個數值置於錯誤年度並混用 INE 之 2022 與 2023 方法：INE/SERMIG《2023 年摘要》第 12 頁圖表中，'
                      '本 panel 之 2018–2020 年數值其實是 2022 年方法之 2021、2022、2023 年，'
                      '2021–2022 年數值其實是 2023 年方法之 2020、2021 年（稽核 F01）。',
             evidence='evidence/countries/CHL/irregular_stock__f8f04e39ba__www.ine.gob.cl.pdf, page 12; '
                      'data/audit_changes_2026-10-07.csv.',
             evidence_zh='evidence/countries/CHL/irregular_stock__f8f04e39ba__www.ine.gob.cl.pdf，第 12 頁；'
                         'data/audit_changes_2026-10-07.csv。',
             action='Corrected on 2026-10-07 to the 2023 methodology for every year (10,375; 21,833; 53,356; 109,846; '
                    '291,149). The 2022-methodology series and the 2022 press-release figure (107,223) are kept as '
                    'alternatives in irregular_estimates_all.csv.',
             action_zh='已於 2026-10-07 更正為各年度一律採用 2023 年方法（10,375；21,833；53,356；109,846；291,149）。'
                       '2022 年方法之序列與 2022 年新聞稿數字（107,223）保留為 irregular_estimates_all.csv 之替代值。'),
        dict(severity='RESOLVED', scope='India', variable='foreign_born',
             issue='The 2011 value 5,490,000 came from Table 2a of a journal article built on Census Table D-2 (place of '
                   'LAST residence), not from the birthplace table. The article was also cited under the wrong authors '
                   '(audit F02).',
             issue_zh='2011 年數值 5,490,000 取自一篇期刊論文之表 2a，該表以普查表 D-2（最近一次居住地）為基礎，並非出生地表；'
                      '該論文亦被誤列作者（稽核 F02）。',
             evidence='Census of India 2011, Table D-01 (evidence/countries/IND/foreign_born__ORGI_Census2011_D01_India__'
                      'DS-0000-D01-MDDS.xlsx).',
             evidence_zh='印度 2011 年普查表 D-01（evidence/countries/IND/foreign_born__ORGI_Census2011_D01_India__'
                         'DS-0000-D01-MDDS.xlsx）。',
             action='Corrected on 2026-10-07 to the official "Born Outside India" total, 5,363,099 (grade A). The article '
                    'is Singh and Biradar, Demography India 51(1), 2022, and is kept as the superseded source.',
             action_zh='已於 2026-10-07 更正為官方「Born Outside India」總數 5,363,099（A 級）。該論文為 Singh 與 Biradar，'
                       'Demography India 51(1)，2022，保留為被取代之來源。'),
        dict(severity='RESOLVED', scope='Suriname', variable='foreign_nationals',
             issue='The 2012 value 36,393 was total population minus Surinamese nationals, a residual that includes 3,340 '
                   'persons of unknown nationality (audit F03).',
             issue_zh='2012 年數值 36,393 為總人口減蘇利南籍，此剩餘數包含 3,340 名國籍不明者（稽核 F03）。',
             evidence='Census 8 (2012) Volume 1, Table H2 (evidence/countries/SUR/foreign_nationals__f68b5eee2a__'
                      'statistics-suriname.org.pdf, page 24).',
             evidence_zh='第 8 次普查（2012）第 1 冊，表 H2（evidence/countries/SUR/foreign_nationals__f68b5eee2a__'
                         'statistics-suriname.org.pdf，第 24 頁）。',
             action='Corrected on 2026-10-07 to 33,053, the sum of the six printed foreign nationality categories; the 3,340 '
                    'unknown are excluded and 36,393 is kept as an alternative. The cell is marked derived.',
             action_zh='已於 2026-10-07 更正為 33,053，即表中所印六個外國國籍類別之加總；3,340 名國籍不明者不計入，'
                       '36,393 保留為替代值。該格標示為推導值。'),
        dict(severity='MEDIUM', scope='Taiwan', variable='irregular_proxy_overstayers',
             issue='The overstay values for 2012, 2013, 2019 and 2020 cited a Ministry of Labor table of absconded workers '
                   'that does not contain them, and 2021 (81,538) had no source at all (audit F06). The series is the '
                   'National Immigration Agency total for ALL overstaying persons (foreign nationals, mainland Chinese, '
                   'Hong Kong/Macao residents, nationals without household registration), although the notes called it '
                   'overstaying foreign nationals (audit F07).',
             issue_zh='2012、2013、2019、2020 年之逾期停留數值所引用之勞動部失聯移工表並不含該數值，2021 年（81,538）則完全沒有來源（稽核 F06）。'
                      '該序列為移民署「所有」逾期人員之總數（外國人、大陸地區人民、港澳居民、無戶籍國民），'
                      '備註卻稱其為逾期外國籍人士（稽核 F07）。',
             evidence='Legislative Yuan Budget Center reports of July 2019 (附表11) and September 2021 (Table 1), archived '
                      'under evidence/countries/TWN/.',
             evidence_zh='立法院預算中心 2019 年 7 月報告（附表11）與 2021 年 9 月報告（表 1），存於 evidence/countries/TWN/。',
             action='Re-sourced on 2026-10-07 to the Legislative Yuan reports; 2021 deleted (deleted_values.csv); notes now '
                    'say the total covers all categories. The foreign-national component for 2012-2018 is kept as an '
                    'alternative. Which universe the study needs is a decision for the authors: the total is the '
                    'consistent series for 2012-2020; the foreign-national component is published for 2012-2018 only.',
             action_zh='已於 2026-10-07 改引立法院報告；2021 年數值刪除（deleted_values.csv）；備註現載明該總數涵蓋所有類別。'
                       '2012–2018 年之外國人部分保留為替代值。研究需要何種母體，由作者決定：總數為 2012–2020 年一致之序列，'
                       '外國人部分僅公布 2012–2018 年。'),
        dict(severity='RESOLVED', scope='Taiwan', variable='population',
             issue='The 2010-2016 values were the National Development Council figures rounded to thousands; the cited MOI '
                   'yearbook prints exact totals (audit F08).',
             issue_zh='2010–2016 年數值為國家發展委員會四捨五入至千位之數字；所引用之內政部年報載有精確總數（稽核 F08）。',
             evidence='MOI Statistical Yearbook 2019 edition, Table 1, PDF page 151.',
             evidence_zh='內政部統計年報 108 年版，表一，PDF 第 151 頁。',
             action='Corrected on 2026-10-07 to the exact totals (differences of -123 to +483 persons). 2001-2009 remain '
                    'rounded to thousands and say so.',
             action_zh='已於 2026-10-07 更正為精確總數（差異為 −123 至 +483 人）。2001–2009 年仍為四捨五入至千位，並已載明。'),
        dict(severity='RESOLVED', scope='Germany and seven other spliced series', variable='foreign_born / foreign_nationals',
             issue='The splice rule was documented as "mean absolute gap of 5% or more" but the code tested the absolute '
                   'value of the signed mean, so differences of opposite sign cancelled: Germany foreign-born (signed '
                   '+1.6%, mean absolute 7.4%) escaped the flag (audit F12).',
             issue_zh='接合規則之文件載明為「平均絕對差距達 5% 以上」，程式卻是檢定有號平均數之絕對值，'
                      '使正負相反之差異相互抵銷：德國外國出生人口（有號 +1.6%、平均絕對 7.4%）因而未被標示（稽核 F12）。',
             evidence='data/extension_splice_summary.csv now holds both the signed mean and the mean absolute difference.',
             evidence_zh='data/extension_splice_summary.csv 現同時載有有號平均與平均絕對差距。',
             action='Corrected on 2026-10-07: 8 of the 28 series are flagged "splice (large gap)", Germany foreign-born '
                    '2006-2008 among them.',
             action_zh='已於 2026-10-07 更正：28 組序列中有 8 組標示為「splice (large gap)」，含德國 2006–2008 年外國出生人口。'),
        dict(severity='RESOLVED', scope='all', variable='irregular_proxy_detections',
             issue='The codebook, methods page and Chinese labels described detections as repeat enforcement events or '
                   '人次 (person-times). Eurostat counts persons, each once within the reference year; only Mexico counts '
                   'events (audit F05).',
             issue_zh='變項說明書、研究方法頁面與中文標籤將查獲數描述為重複之執法事件或「人次」。Eurostat 計人數，同一參考年內每人僅計一次；'
                      '僅墨西哥計事件數（稽核 F05）。',
             evidence='Eurostat enforcement metadata (migr_eil_esms), counting rule for persons found to be illegally present.',
             evidence_zh='Eurostat 執法統計後設資料（migr_eil_esms），非法在留者之計算規則。',
             action='Corrected on 2026-10-07: unit stated per source, labels changed to 查獲人數.',
             action_zh='已於 2026-10-07 更正：依來源載明計量單位，標籤改為「查獲人數」。'),
        dict(severity='RESOLVED', scope='Australia, Japan, Iceland', variable='irregular_proxy_overstayers / detections',
             issue='Six values the secondary workbook holds were missing from the panel although the archived sources '
                   'support them: Australia 2015, Japan 2010, 2012, 2013 and 2015, Iceland 2021 detections (audit F16).',
             issue_zh='次要活頁簿所載之六個數值未納入 panel，而所存檔之來源可支持：澳洲 2015、日本 2010、2012、2013、2015，'
                      '冰島 2021 年查獲數（稽核 F16）。',
             evidence='data/audit_changes_2026-10-07.csv; data/secondary_workbook_differences.csv.',
             evidence_zh='data/audit_changes_2026-10-07.csv；data/secondary_workbook_differences.csv。',
             action='Added on 2026-10-07 with their sources. Every other difference is an input value that was corrected, '
                    'rejected, reclassified, superseded or deleted; each has a disposition in the same file.',
             action_zh='已於 2026-10-07 連同來源加入。其餘差異均為已更正、否決、重新歸類、被取代或刪除之原始輸入值，各項處置見同一檔案。'),
        dict(severity='MEDIUM', scope='all', variable='research use',
             issue='Source correctness does not settle research suitability. The questionnaire construct, the alignment '
                   'between survey year and stock year, the nationality / citizenship / stateless universes and the '
                   'choice of denominator are analysis decisions that are not recorded here as made (audit F24).',
             issue_zh='來源正確並不等於適用於研究。問卷題目所指涉之概念、調查年度與存量年度之對齊、國籍／公民身分／無國籍者之母體，'
                      '以及分母之選擇，均屬分析決定，此處並未記載為已決定（稽核 F24）。',
             evidence='data/ANALYSIS_NOTES.md.',
             evidence_zh='data/ANALYSIS_NOTES.md。',
             action='Fix the construct and timing rules before the final analysis and report sensitivity to source family, '
                    'concept exclusions, denominator and breaks; data/ANALYSIS_NOTES.md lists the choices and what each '
                    'affects. The authors have to complete it.',
             action_zh='於最終分析前確定概念與時間對齊規則，並報告對來源類型、概念排除、分母與斷裂之敏感度；'
                       'data/ANALYSIS_NOTES.md 列出各項選擇及其影響。須由作者填定。'),
    ]


SCOPE_ZH = {
    'Germany and seven other spliced series': '德國及另外七組接續序列',
    'Australia, Japan, Iceland': '澳洲、日本、冰島',
    'Chile': '智利', 'India': '印度', 'Suriname': '蘇利南', 'Taiwan': '臺灣',
    'all': '全部',
}
VARIABLE_ZH = {'research use': '研究使用',
               'irregular_proxy_overstayers / detections': '逾期停留・居留／查獲人數'}
