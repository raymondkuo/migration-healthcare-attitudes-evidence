# -*- coding: utf-8 -*-
"""English and Traditional Chinese text for the authors' decisions of 2026-10-18 on issues #9, #10 and #24.

  #9   Australia's 2021 Census count of non-citizens is carried in a separate column, non_citizens_census.
  #10  South Africa's 2011 Census count is assessed and not added (ten years before the ISSP 2021 interviews).
  #24  The construct and the timing rule are fixed from the ISSP 2021 item (data/ANALYSIS_NOTES.md, sections 1-2).

One place for the wording; counts are read from the files.
"""
import os

import pandas as pd

WHEN = '2026-10-18'
VAR = 'non_citizens_census'
_D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
SCOPE = 'Australia, India, Israel, New Zealand, Russia, South Africa'


def _aus():
    p = pd.read_csv(os.path.join(_D, 'panel_final.csv'), usecols=['iso3', 'year', VAR, VAR + '_pct_pop'])
    r = p[p[VAR].notna()].iloc[0]
    return r.iso3, int(r.year), int(r[VAR]), float(r[VAR + '_pct_pop']) * 100


def known_issue(fn_n):
    """Replaces the row of the 2026-10-07 audit about the countries with no foreign-national series."""
    iso, y, v, pct = _aus()
    return dict(
        severity='MEDIUM', scope=SCOPE, variable='foreign_nationals',
        issue='Australia, India, Israel, New Zealand and South Africa have no foreign-national values, and Russia has '
              'one census value (2002). None of them has an annual register of the kind Eurostat and the OECD collect. '
              'Census counts were assessed instead (issues #9 and #10). Australia: the authors decided on %s to carry '
              'the %d Census count in a separate column, non_citizens_census: %s persons who are not Australian '
              'citizens (place of usual residence, excluding overseas visitors; 1,307,918 or 5.1%% did not state), '
              'census night 10 August 2021, inside Australia\'s ISSP 2021 interviews. South Africa: the 2011 Census '
              'count (1,692,242 answered "No" to South African citizenship; the table covers 50,641,580 of 51,770,560) '
              'was not added, because South Africa\'s ISSP 2021 interviews were in 2021, ten years later.'
              % (WHEN, y, format(v, ',')),
        issue_zh='澳洲、印度、以色列、紐西蘭與南非沒有外國籍人口數值，俄羅斯僅有單一普查數值（2002 年）。這些國家均無 Eurostat '
                 '與 OECD 所蒐集之那種逐年登記統計，故改為評估普查數（議題 #9 與 #10）。澳洲：作者於 %s 決定將 %d 年普查數另列於 '
                 'non_citizens_census 欄：%s 人非澳洲公民（依常住地，不含海外訪客；1,307,918 人即 5.1%% 未填答），普查夜為 '
                 '2021 年 8 月 10 日，落在澳洲 ISSP 2021 訪問期間之內。南非：2011 年普查數（1,692,242 人對「是否為南非公民」'
                 '回答「否」；該表涵蓋 51,770,560 人中的 50,641,580 人）未予加入，因南非之 ISSP 2021 訪問在 2021 年，相隔十年。'
                 % (WHEN, y, format(v, ',')),
        evidence='ABS, Cultural diversity data summary 2021, Table 2, national total (evidence/countries/AUS/); Statistics '
                 'South Africa, Census 2011 in Brief, Table 2.17; ISSP 2021 Variable Report, DATEYR by country (PDF page '
                 '778, evidence/survey/). Audit findings F09 and F10 (2026-10-07); decisions of %s.' % WHEN,
        evidence_zh='澳洲統計局《Cultural diversity data summary 2021》表 2 全國總計（evidence/countries/AUS/）；南非統計局'
                    '《2011 年普查簡報》表 2.17；ISSP 2021 變項報告 DATEYR 分國表（PDF 第 778 頁，evidence/survey/）。'
                    '稽核發現 F09 與 F10（2026-10-07）；%s 之決定。' % WHEN,
        action='Australia: non_citizens_census holds 2021 only (%.2f%% of the World Bank population); use it as a '
               'single-year level or in a sensitivity run, never as part of the foreign_nationals series. South Africa, '
               'India, Israel, New Zealand: no non-citizen value near the interviews; use foreign_born (which counts '
               'naturalised citizens) or restrict the model to the %d countries with foreign_nationals. Annual blanks are '
               'never interpolated.' % (pct, fn_n),
        action_zh='澳洲：non_citizens_census 僅有 2021 年（占世界銀行人口 %.2f%%）；僅可作為單一年度之水準值或用於敏感度分析，'
                  '不得視為 foreign_nationals 序列之一部分。南非、印度、以色列、紐西蘭：訪問時點附近無非公民數值；可改用 '
                  'foreign_born（包含歸化者），或將模型限於有 foreign_nationals 之 %d 國。逐年空白絕不內插。' % (pct, fn_n))


def codebook_rows():
    iso, y, v, pct = _aus()
    return [
        (VAR,
         'Census count of persons who are not citizens of the country, for a country with no annual foreign-national '
         'series, kept out of foreign_nationals (decision of %s, issue #9). One value: Australia %d, %s (ABS 2021 '
         'Census, Cultural diversity data summary, Table 2; place of usual residence, excluding overseas visitors; '
         'census night 10 August 2021). non_citizens_census_pct_pop is the share of the World Bank population, as for '
         'every other share.' % (WHEN, y, format(v, ',')),
         'A single census year, not a series: never splice it into foreign_nationals or difference it against a register '
         'value. 5.1% of persons did not state their citizenship and are not in the count. South Africa\'s 2011 count '
         'was assessed and not added (issue #10).',
         '非該國公民之普查人數，僅用於沒有逐年外國籍人口序列之國家，另列而不併入 foreign_nationals（%s 之決定，議題 #9）。'
         '目前一筆：澳洲 %d 年，%s 人（澳洲統計局 2021 年普查《Cultural diversity data summary》表 2；依常住地，不含海外訪客；'
         '普查夜 2021 年 8 月 10 日）。non_citizens_census_pct_pop 為占世界銀行人口之比例，與其他占比相同。' % (WHEN, y, format(v, ',')),
         '單一普查年度，並非序列：不得接續至 foreign_nationals，亦不得與登記數相減。5.1% 之人未填答公民身分，不在此數之內。'
         '南非 2011 年之普查數經評估後未予加入（議題 #10）。'),
    ]


def revision():
    """Entries for data/revision_history.csv (keys besides date/time/commit)."""
    iso, y, v, pct = _aus()
    return [
        dict(kind='values added', iso3='AUS',
             scope='Australia - non-citizens (census) - %d' % y, scope_zh='澳洲 · 非公民（普查） · %d' % y,
             before='no value', before_zh='無數值',
             after='%s in a new column non_citizens_census' % format(v, ','),
             after_zh='%s，列於新欄位 non_citizens_census' % format(v, ','),
             change='The authors\' decision on issue #9: the 2021 Census count of persons who are not Australian citizens, '
                    'read from the official ABS workbook (Cultural diversity data summary 2021, Table 2, national total), '
                    'in a separate column so that foreign_nationals stays an annual series. Archived with the ABS release '
                    'and census-date pages and their mirrors. No other value changed.',
             change_zh='作者對議題 #9 之決定：2021 年普查中非澳洲公民之人數，讀自澳洲統計局官方試算表（Cultural diversity data '
                       'summary 2021，表 2，全國總計），另列一欄，使 foreign_nationals 維持為逐年序列。已存檔澳洲統計局之發布頁與'
                       '普查日期頁及其鏡像。其他數值皆未變動。'),
        dict(kind='documentation corrected', iso3='',
             scope='South Africa 2011 census count: assessed, not added (issue #10)',
             scope_zh='南非 2011 年普查數：已評估，未加入（議題 #10）',
             before='candidate, universe to be settled', before_zh='候選資料，母體範圍待釐清',
             after='not added: ten years before the ISSP 2021 interviews', after_zh='不加入：早於 ISSP 2021 訪問十年',
             change='The authors\' decision: 1,692,242 persons answered "No" to South African citizenship in the 2011 Census, '
                    'but South Africa\'s ISSP 2021 interviews were in 2021 (Variable Report, DATEYR by country). The count stays '
                    'documented in the known issues; no value changed.',
             change_zh='作者之決定：2011 年普查中有 1,692,242 人對南非公民身分回答「否」，但南非之 ISSP 2021 訪問在 2021 年'
                       '（變項報告 DATEYR 分國表）。此數仍記載於已知問題；數值未變動。'),
        dict(kind='documentation corrected', iso3='',
             scope='Analysis notes: construct and timing rule fixed from the ISSP 2021 item (issue #24)',
             scope_zh='研究使用說明：依 ISSP 2021 題目確定構念與時間規則（議題 #24）',
             before='marked [AUTHORS]', before_zh='標示為〔作者〕待填',
             after='decided: foreign_nationals_pct_pop; latest stock on or before the first interview',
             after_zh='已決定：foreign_nationals_pct_pop；首次訪問當日或之前之最近一筆存量',
             change='The authors\' decision: item Q6a names people who "do not hold citizenship of [country]", so the main '
                    'regressor is foreign_nationals_pct_pop, with foreign_born_pct_pop as a robustness check and the irregular '
                    'series not used for this item; the primary timing rule is the latest stock dated on or before the first '
                    'interview, with same-year and nearest-stock rows as sensitivity. The ISSP documentation quoted is '
                    'archived in evidence/survey/. No value changed.',
             change_zh='作者之決定：題目 Q6a 所指為「不具有［該國］公民身分」之人，故主要自變項為 foreign_nationals_pct_pop，'
                       '以 foreign_born_pct_pop 作穩健性檢驗，無證移民序列不用於此題；主要時間規則為首次訪問當日或之前之最近一筆'
                       '存量，同年列與最近存量列作為敏感度分析。所引用之 ISSP 文件存檔於 evidence/survey/。數值未變動。'),
    ]
