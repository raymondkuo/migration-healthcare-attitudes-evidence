# -*- coding: utf-8 -*-
"""English and Traditional Chinese text for the four COVID-19 variables added on 2026-11-06.

One place for the wording, so the codebook, known issues, data-quality table, methods page and
revision history say the same thing. Counts are computed from the files, never typed in.
"""
import os

import pandas as pd

WHEN = '2026-11-06'
CASES, CASES_PCT, DEATHS, DEATHS_PCT = 'covid_cases', 'covid_cases_pct_pop', 'covid_deaths', 'covid_deaths_pct_pop'
VARS = [CASES, CASES_PCT, DEATHS, DEATHS_PCT]
PCT = (CASES_PCT, DEATHS_PCT)
YEARS = (2020, 2021, 2022)
SOURCE_TYPE = 'surveillance'
_D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
CMP = os.path.join(_D, 'covid_source_comparison.csv')
DATECHK = os.path.join(_D, 'covid_who_date_check.csv')
FR_DOM = ('Guadeloupe', 'Martinique', 'French Guiana', 'Réunion', 'Mayotte')
F_CN22 = 'confirmed counts only: most of the December 2022 wave not counted'
F_CN22_ZH = '僅計確診：2022 年 12 月疫情高峰大多未計入'
FIXED_CN22 = '2026-11-06'                # China 2022 added from the last national daily briefing (flagged)
CORR = '2026-11-06'                      # the COVID audit's issues #34-#36 answered (third commit of the day)
# China CDC's report of 15 January 2023 (archived; 96_collect_covid.py asserts these numbers against it): COVID-19-
# related deaths in hospitals, 8 December 2022 - 12 January 2023, of which from respiratory failure caused by the virus,
# and people in hospital with it on 12 January 2023 (in units of 10,000, as published)
HOSP = dict(deaths=59938, resp=5503, other=54435, inpatients_10k=127)
# what earlier commits published, kept for the revision history (the panel now holds the corrected values)
REV1 = dict(n=119, n_cells=476)          # commit 759cd18: China 2022 still empty
OLD_CN22 = dict(cases=294881, deaths=605, cum_cases=397195, cum_deaths=5241,
                flag='incomplete year: national daily reporting ended 23 Dec 2022; confirmed cases only',
                flag_zh='年度不完整：全國每日通報止於 2022 年 12 月 23 日；僅計確診病例')

LABEL = {CASES: ('COVID-19 cases', 'COVID-19 確診病例數'),
         CASES_PCT: ('COVID-19 cases as % of population', 'COVID-19 確診病例占人口百分比'),
         DEATHS: ('COVID-19 deaths', 'COVID-19 死亡數'),
         DEATHS_PCT: ('COVID-19 deaths as % of population', 'COVID-19 死亡數占人口百分比')}


def counts():
    """Numbers quoted in the texts, read from the panel and the source comparison."""
    p = pd.read_csv(os.path.join(_D, 'panel_final.csv'), usecols=['iso3', 'year'] + VARS)
    c = pd.read_csv(CMP, dtype=str, keep_default_na=False)
    who = c[c.source_used == 'WHO']
    j = c[(c.jhu_cases != '') & (c.cases != '')]
    jc = (j.jhu_cases.astype(float) - j.cases.astype(float)).abs() <= 0.01 * j.cases.astype(float).clip(lower=1)
    jd = (j.jhu_deaths.astype(float) - j.deaths.astype(float)).abs() <= 0.01 * j.deaths.astype(float).clip(lower=1)
    s = p[p[CASES].notna()]
    jj = j.assign(c=j.cases.astype(float), jc_=j.jhu_cases.astype(float), d=j.deaths.astype(float),
                  jd_=j.jhu_deaths.astype(float)).groupby('iso3')[['c', 'jc_', 'd', 'jd_']].sum()
    gc = 100 * (jj.jc_ - jj.c).abs() / jj.c.clip(lower=1)
    gd = 100 * (jj.jd_ - jj.d).abs() / jj.d.clip(lower=1)
    cn = p[p.iso3 == 'CHN'].set_index('year')
    dc = pd.read_csv(DATECHK)
    off = dc[(dc.cases_difference != 0) | (dc.deaths_difference != 0)]
    off = off.reindex(off.cases_difference.abs().add(100 * off.deaths_difference.abs())
                      .sort_values(ascending=False, kind='stable').index)
    return dict(cn22_cases=int(cn.loc[2022, CASES]), cn22_deaths=int(cn.loc[2022, DEATHS]),
                cn22_cum_cases=int(cn.loc[[2020, 2021, 2022], CASES].sum()),
                cn22_cum_deaths=int(cn.loc[[2020, 2021, 2022], DEATHS].sum()),
                n_datechk=int(len(dc)), n_dateoff=int(len(off)),
                dateoff=', '.join('%s (%d vs %d cases%s)' % (r.iso3, r.daily_file_cases, r.sitrep24_cases,
                                                            '; %d vs %d deaths' % (r.daily_file_deaths, r.sitrep24_deaths)
                                                            if r.deaths_difference else '')
                                  for r in off.itertuples()),
                dateoff_zh='、'.join('%s（病例 %d 對 %d%s）' % (r.iso3, r.daily_file_cases, r.sitrep24_cases,
                                                            '；死亡 %d 對 %d' % (r.daily_file_deaths, r.sitrep24_deaths)
                                                            if r.deaths_difference else '')
                                     for r in off.itertuples()),
                n_comb=int(len(jj)), n_comb_cases_1pct=int((gc <= 1).sum()), n_comb_deaths_1pct=int((gd <= 1).sum()),
                big_gaps=', '.join(sorted(set(gc[gc > 5].index) | set(gd[gd > 5].index))),n=int(s[CASES].notna().sum()), n_cells=int(sum(p[v].notna().sum() for v in VARS)),
                n_countries=int(s.iso3.nunique()), n_who=int(len(who)), n_who_countries=int(who.iso3.nunique()),
                n_jhu=int(len(j)), n_jhu_cases_1pct=int(jc.sum()), n_jhu_deaths_1pct=int(jd.sum()),
                max_cases_pct=float(s[CASES_PCT].max()), max_deaths_pct=float(s[DEATHS_PCT].max()),
                total_cases=int(s[CASES].sum()), total_deaths=int(s[DEATHS].sum()))


COMPARABILITY_EN = {
    CASES: 'Comparable with caution. Reported (confirmed) cases, not infections: they depend on how much each country '
           'tested and reported, which differed widely and fell sharply in 2022 as testing was scaled back. One source '
           'for 38 countries (WHO, cases by date reported); mainland China and Taiwan from their national authorities.',
    DEATHS: 'Comparable with caution. Deaths reported as COVID-19 deaths; countries define and certify them differently '
            'and some under-report. One source for 38 countries (WHO); mainland China and Taiwan from their national '
            'authorities.',
}
COMPARABILITY_EN[CASES_PCT] = COMPARABILITY_EN[CASES] + ' Divided by the panel\'s population of the same country and year.'
COMPARABILITY_EN[DEATHS_PCT] = COMPARABILITY_EN[DEATHS] + ' Divided by the panel\'s population of the same country and year.'
COMPARABILITY_ZH = {
    CASES: '可謹慎比較。為通報（確診）病例而非感染人數：取決於各國之檢驗與通報量，差異甚大，且 2022 年檢驗縮減後大幅下降。'
           '38 國來源一致（世界衛生組織，依通報日期）；中國大陸與臺灣取自其主管機關。',
    DEATHS: '可謹慎比較。為通報之 COVID-19 死亡數；各國之定義與死因認定不同，部分國家有低報情形。38 國來源一致（世界衛生組織）；'
            '中國大陸與臺灣取自其主管機關。',
}
COMPARABILITY_ZH[CASES_PCT] = COMPARABILITY_ZH[CASES] + '除以 panel 同一國家與年度之人口。'
COMPARABILITY_ZH[DEATHS_PCT] = COMPARABILITY_ZH[DEATHS] + '除以 panel 同一國家與年度之人口。'

_SRC_EN = ('38 countries: WHO COVID-19 dashboard data (daily file, cases and deaths by date reported to WHO); France '
           'includes its five overseas departments, which WHO lists separately but the World Bank population includes. '
           'Mainland China: National Health Commission, cumulative counts as of 24:00 on 31 December (2020, 2021); 2022: '
           'Chinese Center for Disease Control and Prevention (China CDC), which took over the daily figures on 25 '
           'December 2022, cumulative counts as of 24:00 on 31 December. Taiwan: Central Epidemic Command Center / Taiwan '
           'CDC, cumulative counts announced on 31 December.')
_SRC_ZH = ('38 國：世界衛生組織 COVID-19 儀表板資料（每日檔，依向世界衛生組織通報之日期之病例與死亡數）；法國含其五個海外省'
           '（世界衛生組織分列，但世界銀行人口包含之）。中國大陸：國家衛生健康委員會，12 月 31 日 24 時之累計數（2020、2021 年）；'
           '2022 年：中國疾病預防控制中心（自 2022 年 12 月 25 日起接手發布每日數字），12 月 31 日 24 時之累計數。'
           '臺灣：中央流行疫情指揮中心／疾病管制署，12 月 31 日公布之累計數。')


def codebook_rows():
    """(name, definition, caution, definition_zh, caution_zh) rows for data/codebook.csv."""
    k = counts()
    caution = ('Years 2020-2022 only (none before 2020). Reported counts, not infections or excess deaths. Mainland China '
               'counts confirmed cases and deaths only and misses most of the December 2022 wave (2022 flagged "%s"; see '
               'the known issues); WHO\'s figure for "China" includes Hong Kong, Macao and Taiwan and is not used. WHO\'s '
               'daily file dates some early-2020 counts before WHO reported them (data/covid_who_date_check.csv); all fall '
               'within 2020, so the annual values are unaffected. Verified: the WHO annual values equal the change in WHO\'s '
               'cumulative counts; '
               'against the Johns Hopkins CSSE archive, %d of %d country-years agree within 1%% for cases and %d for deaths, '
               'and over 2020-2022 combined %d and %d of %d countries do; the two compilations differ in reporting dates and, '
               'for some countries (%s, more than 5%% apart), in what they counted (data/covid_source_comparison.csv).'
               % (F_CN22, k['n_jhu_cases_1pct'], k['n_jhu'], k['n_jhu_deaths_1pct'], k['n_comb_cases_1pct'],
                  k['n_comb_deaths_1pct'], k['n_comb'], k['big_gaps']))
    caution_zh = ('僅 2020–2022 年（2020 年前無）。為通報數，而非感染數或超額死亡。中國大陸僅計確診病例與死亡，未能涵蓋 2022 年 12 月'
                  '疫情高峰之大部分（2022 年標示旗標「%s」；見已知問題）；世界衛生組織之「中國」數字含香港、澳門與臺灣，未予採用。'
                  '世界衛生組織每日檔將部分 2020 年初之計數標於早於其當時通報之日期（data/covid_who_date_check.csv）；均仍在 2020 年內，'
                  '故不影響年度值。已查證：世界衛生組織年度值等於其累計數之年度差；%d 個國家年度中，'
                  '病例數有 %d 個、死亡數有 %d 個與 Johns Hopkins CSSE 存檔相差在 1%% 以內；2020–2022 年合計，%d 國中病例數有 %d 國、'
                  '死亡數有 %d 國在 1%% 以內；兩者之差異來自通報日期，部分國家（%s，相差逾 5%%）則來自計入範圍不同'
                  '（data/covid_source_comparison.csv）。'
                  % (F_CN22, k['n_jhu'], k['n_jhu_cases_1pct'], k['n_jhu_deaths_1pct'], k['n_comb'], k['n_comb_cases_1pct'],
                     k['n_comb_deaths_1pct'], k['big_gaps']))
    out = []
    for v, d_en, d_zh in (
            (CASES, 'COVID-19 cases reported in the calendar year (new confirmed cases, a count). ',
             'COVID-19 該曆年通報之確診病例數（新增確診病例，計數）。'),
            (CASES_PCT, 'COVID-19 cases reported in the calendar year as a percentage of the population (covid_cases / '
                        'population x 100; computed by the archive with the panel\'s population). ',
             'COVID-19 該曆年通報確診病例數占人口之百分比（covid_cases ÷ population × 100；由本存檔以 panel 之人口計算）。'),
            (DEATHS, 'COVID-19 deaths reported in the calendar year (a count). ', 'COVID-19 該曆年通報之死亡數（計數）。'),
            (DEATHS_PCT, 'COVID-19 deaths reported in the calendar year as a percentage of the population (covid_deaths / '
                         'population x 100; computed by the archive with the panel\'s population). ',
             'COVID-19 該曆年通報死亡數占人口之百分比（covid_deaths ÷ population × 100；由本存檔以 panel 之人口計算）。')):
        out.append((v, d_en + _SRC_EN + ' Added %s.' % WHEN, caution, d_zh + _SRC_ZH + '於 %s 新增。' % WHEN, caution_zh))
    return out


SOURCE_TYPE_EN = (' covid_*: surveillance (counts reported by public-health surveillance) for every value.')
SOURCE_TYPE_ZH = ('covid_*：每一筆數值皆為 surveillance（公共衛生監測通報之計數）。')
FLAG_EN = (' covid_*: "%s" on mainland China 2022 (China CDC\'s report of 15 January 2023 counts %s COVID-19-related '
           'deaths in hospitals from 8 December 2022 to 12 January 2023).' % (F_CN22, format(HOSP['deaths'], ',')))
FLAG_ZH = ('COVID-19 變項：中國大陸 2022 年標示「%s」（中國疾病預防控制中心 2023 年 1 月 15 日之報告指出，2022 年 12 月 8 日至 2023 年 '
           '1 月 12 日醫療機構在院新冠病毒感染相關死亡 %s 例）。' % (F_CN22, format(HOSP['deaths'], ',')))
COLLECTED_EN = ' covid_* were collected on %s for every value.' % WHEN
COLLECTED_ZH = 'covid_* 之每一筆數值均於 %s 蒐集。' % WHEN


def known_issues():
    k = counts()
    hosp, inp = format(HOSP['deaths'], ','), HOSP['inpatients_10k'] / 100.0
    china = dict(
        severity='MEDIUM', scope='China', variable=CASES,
        issue='Mainland China\'s COVID-19 values do not come from WHO, whose series for "China" includes Hong Kong SAR, '
              'Macao SAR and Taiwan (WHO situation report 24 says so; for 31 December 2021 WHO\'s total equals the '
              'National Health Commission\'s mainland count plus the three, case for case) and in 2022 no longer adds up '
              '(WHO\'s China total is smaller than Hong Kong plus Taiwan alone from March). 2020 and 2021 come from the '
              'Commission\'s year-end briefings; 2022 from China CDC\'s bulletin for 24:00 on 31 December 2022: the '
              'Commission stopped publishing daily figures on 25 December 2022 and handed them to China CDC, which '
              'continued the same cumulative counts. The counts are confirmed cases and deaths as China defined them '
              '(asymptomatic infections were reported separately and are not included), and they miss most of the '
              'December 2022 wave: China CDC\'s report of 15 January 2023 counts %s COVID-19-related deaths in hospitals '
              'from 8 December 2022 to 12 January 2023 (%s of them from respiratory failure caused by the virus) and %.2f '
              'million people in hospital with it on 12 January 2023, against %s deaths and %s confirmed cases for all of '
              '2022 here. The hospital figures run into 2023 and are not a 2022 value. Flagged "%s".'
              % (hosp, format(HOSP['resp'], ','), inp, format(k['cn22_deaths'], ','), format(k['cn22_cases'], ','), F_CN22),
        issue_zh='中國大陸之 COVID-19 數值並非取自世界衛生組織：世界衛生組織之「中國」序列包含香港、澳門與臺灣（世界衛生組織第 24 號'
                 '疫情報告載明；2021 年 12 月 31 日世界衛生組織之總數，恰等於國家衛生健康委員會之大陸累計數加上三地之數），且 2022 年已'
                 '無法加總對應（自 3 月起，世界衛生組織之中國總數小於香港與臺灣兩地之和）。2020 與 2021 年取自該委員會之年底通報；2022 年'
                 '取自中國疾病預防控制中心 2022 年 12 月 31 日 24 時之通報：該委員會自 2022 年 12 月 25 日起停止發布每日數字，改由中國疾病'
                 '預防控制中心發布，並延續同一累計數。計數為中國定義之確診病例與死亡（無症狀感染者另行通報，未計入），未能涵蓋 2022 年 12 月'
                 '疫情高峰之大部分：中國疾病預防控制中心 2023 年 1 月 15 日之報告指出，2022 年 12 月 8 日至 2023 年 1 月 12 日醫療機構在院'
                 '新冠病毒感染相關死亡 %s 例（其中新冠病毒感染導致呼吸功能衰竭死亡 %s 例），2023 年 1 月 12 日現有住院病例 %d 萬例；本存檔'
                 ' 2022 年全年則為 %s 例死亡、%s 例確診。住院數字跨入 2023 年，並非 2022 年之數值。標示旗標「%s」。'
                 % (hosp, format(HOSP['resp'], ','), HOSP['inpatients_10k'], format(k['cn22_deaths'], ','),
                    format(k['cn22_cases'], ','), F_CN22),
        evidence='evidence/countries/CHN/: the National Health Commission\'s briefings for 31 December 2020 and 2021, China '
                 'CDC\'s bulletin for 31 December 2022, each with mainland, Hong Kong, Macao and Taiwan counts, the '
                 'Commission\'s last daily briefing (23 December 2022), the report of its notice that China CDC would '
                 'publish the figures, and China CDC\'s report of 15 January 2023 (deaths in hospitals); evidence/api/: WHO '
                 'situation report 24 (page 5 footnote) and the WHO daily file; data/covid_source_comparison.csv puts WHO\'s '
                 'China figures beside the mainland ones.',
        evidence_zh='evidence/countries/CHN/：國家衛生健康委員會 2020 與 2021 年 12 月 31 日之通報、中國疾病預防控制中心 2022 年 12 月 '
                    '31 日之通報（均含大陸、香港、澳門與臺灣之數）、該委員會最後一次每日通報（2022 年 12 月 23 日）、其改由中國疾病預防'
                    '控制中心發布之公告報導，以及中國疾病預防控制中心 2023 年 1 月 15 日之報告（在院死亡）；evidence/api/：世界衛生組織'
                    '第 24 號疫情報告（第 5 頁註腳）與世界衛生組織每日檔；data/covid_source_comparison.csv 並列世界衛生組織之中國數字與'
                    '大陸數字。',
        action='China 2022 is kept and flagged in all four COVID-19 variables: leave it out of comparisons of 2022 or of '
               'totals over 2020-2022, or report the result without it. Do not substitute WHO\'s China figure (a different '
               'territory) or the hospital deaths (a different period and definition).',
        action_zh='中國 2022 年於四個 COVID-19 變項皆保留並標示旗標：比較 2022 年或 2020–2022 年合計時請排除之，或另報告排除後之結果。'
                  '請勿以世界衛生組織之中國數字（涵蓋範圍不同）或在院死亡數（期間與定義不同）替代。')
    dates = dict(
        severity='LOW', scope='WHO countries, early 2020', variable=CASES,
        issue='WHO\'s daily file dates some early-2020 counts before WHO itself reported them. WHO situation report 24 '
              'lists the cases and deaths each country had reported by 13 February 2020; for %d of the %d countries taken '
              'from WHO, the daily file\'s counts to that date differ: %s. Germany is the clearest case: the file has one '
              'case on 4 January and three deaths on 5 January 2020, while ECDC dates Germany\'s first confirmed case to '
              '27 January and the Robert Koch Institute counts German deaths from 9 March. The archived sources do not say '
              'how these counts came to be dated earlier, and some small differences may only reflect the hours between '
              'the report\'s cut-off (10:00 CET) and the end of the day. All of them fall within 2020, so the annual '
              'values are not affected; the archive takes the file as published and moves or deletes nothing.'
              % (k['n_dateoff'], k['n_datechk'], k['dateoff']),
        issue_zh='世界衛生組織每日檔將部分 2020 年初之計數標於早於其當時通報之日期。世界衛生組織第 24 號疫情報告列出各國至 2020 年 2 月 '
                 '13 日已通報之病例與死亡；取自世界衛生組織之 %d 國中，有 %d 國之每日檔至該日之計數與之不同：%s。德國最為明顯：每日檔於 '
                 '2020 年 1 月 4 日有 1 例、1 月 5 日有 3 例死亡，但歐洲疾病預防控制中心指出德國首例確診為 1 月 27 日，羅伯特·柯霍研究所則'
                 '自 3 月 9 日起計德國之死亡。所存檔之來源未說明這些計數為何標於較早日期；部分小差異亦可能僅反映該報告截止時間（歐洲中部'
                 '時間 10 時）與當日結束之間的時差。上述計數均在 2020 年內，故不影響年度值；本存檔依其公布之檔案使用，未移動或刪除任何'
                 '計數。' % (k['n_datechk'], k['n_dateoff'], k['dateoff_zh']),
        evidence='data/covid_who_date_check.csv (from the archived WHO daily file and situation report 24, page 5: each '
                 'country\'s counts to 13 February 2020 and its first dates with cases and deaths); evidence/countries/DEU/: '
                 'ECDC\'s statement of 28 January 2020 and the Robert Koch Institute\'s situation report of 23 March 2020 '
                 '(page 4).',
        evidence_zh='data/covid_who_date_check.csv（取自所存檔之世界衛生組織每日檔與第 24 號疫情報告第 5 頁：各國至 2020 年 2 月 13 日'
                    '之計數及每日檔中首次出現病例與死亡之日期）；evidence/countries/DEU/：歐洲疾病預防控制中心 2020 年 1 月 28 日之聲明與'
                    '羅伯特·柯霍研究所 2020 年 3 月 23 日之疫情報告（第 4 頁）。',
        action='Use the annual values as they are. Do not use WHO\'s daily dates (or monthly sums) for early 2020 without '
               'checking them against the national chronology. The archived sources cannot rule out that counts were '
               're-dated across a year boundary as well; the Johns Hopkins comparison (dates as reported at the time) shows '
               'where annual values differ.',
        action_zh='年度值可依現況使用。未經與各國時序核對前，請勿使用世界衛生組織 2020 年初之每日日期（或其月加總）。所存檔之來源無法'
                  '排除計數亦有跨年度改標日期之情形；Johns Hopkins 之比較（依當時通報日期）可顯示年度值之差異所在。')
    rep = dict(
        severity='MEDIUM', scope='All countries', variable=CASES,
        issue='COVID-19 cases and deaths are counts reported by surveillance, by the date they were reported (WHO) or '
              'announced (China, Taiwan), not the date of infection or death. Cases depend on testing, which differed '
              'widely between countries and was scaled back in 2022; deaths depend on how each country certified them. '
              'Reported counts are not infections or excess deaths. The four variables cover 2020-2022 only; before 2020 '
              'they are empty, not zero.',
        issue_zh='COVID-19 病例與死亡數為監測通報之計數，依其向世界衛生組織通報之日期（世界衛生組織）或公布日期（中國、臺灣）歸年，'
                 '而非感染或死亡日期。病例數取決於檢驗量，各國差異甚大，且 2022 年檢驗縮減；死亡數取決於各國之死因認定。通報數並非感染'
                 '數或超額死亡。四個變項僅涵蓋 2020–2022 年；2020 年前為空白而非零。',
        evidence='evidence/api/: the WHO daily file with grids of the annual values, and the Johns Hopkins CSSE time series '
                 'used as a check; data/covid_source_comparison.csv.',
        evidence_zh='evidence/api/：世界衛生組織每日檔及其年度值表格，以及作為核對之 Johns Hopkins CSSE 時間序列；'
                    'data/covid_source_comparison.csv。',
        action='Used as reported. For pre-2020 years set the counts to zero only if the model needs it, and say so; for '
               'comparisons of the pandemic\'s toll, prefer deaths to cases and consider excess mortality from another '
               'source.',
        action_zh='依通報值使用。若模型需要，可將 2020 年前之計數設為零並註明；比較疫情衝擊時，死亡數優於病例數，並可考慮其他來源之超額死亡。')
    return [china, dates, rep]


def verdict():
    k = counts()
    return {
        'en': 'Fair. One source for 38 countries (WHO, checked against its own cumulative counts and the Johns Hopkins '
              'archive), mainland China and Taiwan from their national authorities; but reported counts depend on '
              'testing and certification, mainland China 2022 misses most of the December wave (flagged), and only '
              '2020-2022 exist.',
        'zh': '尚可。38 國來源一致（世界衛生組織，並與其累計數及 Johns Hopkins 存檔核對），中國大陸與臺灣取自其主管機關；但通報數取決於'
              '檢驗與死因認定，中國大陸 2022 年未能涵蓋 12 月疫情高峰之大部分（已標示旗標），且僅有 2020–2022 年。',
    }


def revision_cn2022():
    """The second entry of 2026-11-06: China 2022 added after the first commit left it empty. It records what that
    commit (7f138c3) published; the values were corrected later the same day (revision_cn2022_cdc)."""
    o = OLD_CN22
    return dict(
        scope='COVID-19, mainland China 2022 (all four variables)',
        scope_zh='COVID-19，中國大陸 2022 年（四個變項）',
        before='empty', before_zh='空白',
        after='%s cases and %s deaths (1 January-23 December 2022), flagged "%s"'
              % (format(o['cases'], ','), format(o['deaths'], ','), o['flag']),
        after_zh='%s 例確診、%s 例死亡（2022 年 1 月 1 日至 12 月 23 日），標示旗標「%s」'
                 % (format(o['cases'], ','), format(o['deaths'], ','), o['flag']),
        change='Added from the National Health Commission\'s last daily briefing (24 December 2022, data to 24:00 on 23 '
               'December; its English website), minus the 2021 year-end count. The year is incomplete and the counts are '
               'confirmed cases only, so the values are flagged and a known issue says how to treat them. The notice that '
               'daily publication stopped on 25 December 2022 is archived.',
        change_zh='取自國家衛生健康委員會最後一次每日通報（2022 年 12 月 24 日，資料至 12 月 23 日 24 時；其英文網站），減去 2021 年底之累計數。'
                  '該年度不完整且僅計確診病例，故標示旗標，並於已知問題說明處理方式。停止每日發布（2022 年 12 月 25 日）之公告亦已存檔。')


def revision_cn2022_cdc():
    """Third entry of 2026-11-06 (GitHub issue #35): China 2022 to 31 December from China CDC."""
    k, o = counts(), OLD_CN22
    return dict(
        scope='COVID-19, mainland China 2022 (all four variables; GitHub issue #35, COVID audit C02)',
        scope_zh='COVID-19，中國大陸 2022 年（四個變項；GitHub issue #35，COVID-19 稽核發現 C02）',
        before='%s cases and %s deaths (1 January-23 December 2022, the National Health Commission\'s last daily '
               'briefing), flagged "%s"' % (format(o['cases'], ','), format(o['deaths'], ','), o['flag']),
        before_zh='%s 例確診、%s 例死亡（2022 年 1 月 1 日至 12 月 23 日，國家衛生健康委員會最後一次每日通報），標示旗標「%s」'
                  % (format(o['cases'], ','), format(o['deaths'], ','), o['flag_zh']),
        after='%s cases and %s deaths (calendar year, China CDC\'s bulletin for 31 December 2022), flagged "%s"'
              % (format(k['cn22_cases'], ','), format(k['cn22_deaths'], ','), F_CN22),
        after_zh='%s 例確診、%s 例死亡（全年，中國疾病預防控制中心 2022 年 12 月 31 日之通報），標示旗標「%s」'
                 % (format(k['cn22_cases'], ','), format(k['cn22_deaths'], ','), F_CN22_ZH),
        change='The archived notice says the Commission handed the daily figures to China CDC when it stopped publishing '
               'them on 25 December 2022, so the cut-off at 23 December and the flag "national daily reporting ended" '
               'were wrong. 2022 now runs to 24:00 on 31 December: %s cases and %s deaths cumulative (China CDC\'s '
               'bulletin, archived, whose Taiwan figures equal the CECC\'s of the same day), minus the Commission\'s 2021 '
               'year-end counts: %s cases and %s deaths more than before, and the two percentages with them. The flag now '
               'names what limits the value: China CDC\'s report of 15 January 2023 (archived) counts %s COVID-19-related '
               'deaths in hospitals from 8 December 2022 to 12 January 2023. No other value changed.'
               % (format(k['cn22_cum_cases'], ','), format(k['cn22_cum_deaths'], ','),
                  format(k['cn22_cases'] - o['cases'], ','), format(k['cn22_deaths'] - o['deaths'], ','),
                  format(HOSP['deaths'], ',')),
        change_zh='所存檔之公告指出，該委員會於 2022 年 12 月 25 日停止發布每日數字時已改由中國疾病預防控制中心發布，故截至 12 月 23 日'
                  '與「全國每日通報止於」之旗標均有誤。2022 年現涵蓋至 12 月 31 日 24 時：累計 %s 例確診、%s 例死亡（中國疾病預防控制中心'
                  '通報，已存檔；其臺灣數字與疾病管制署同日之數字相同），減去該委員會 2021 年底之累計數；較先前多 %s 例確診、%s 例死亡，'
                  '兩個百分比隨之更新。旗標現改為說明此數值之限制：中國疾病預防控制中心 2023 年 1 月 15 日之報告（已存檔）指出，2022 年 '
                  '12 月 8 日至 2023 年 1 月 12 日醫療機構在院新冠病毒感染相關死亡 %s 例。其他數值皆未變動。'
                  % (format(k['cn22_cum_cases'], ','), format(k['cn22_cum_deaths'], ','),
                     format(k['cn22_cases'] - o['cases'], ','), format(k['cn22_deaths'] - o['deaths'], ','),
                     format(HOSP['deaths'], ',')))


def revision_units():
    """Third commit of 2026-11-06 (GitHub issue #36): the unit of the *_pct_pop columns."""
    return dict(
        scope='Codebook and clean workbook: the unit of the *_pct_pop columns (GitHub issue #36, COVID audit C03)',
        scope_zh='編碼簿與精簡活頁簿：*_pct_pop 欄之單位（GitHub issue #36，COVID-19 稽核發現 C03）',
        before='"*_pct_pop: variable divided by population (proportion, not percent)" with no exception; the clean '
               'workbook\'s README said the archive stores every *_pct_pop as a proportion (0-1)',
        before_zh='「*_pct_pop：該變項除以總人口（比例，非百分比）」，未列例外；精簡活頁簿 README 稱本存檔之 *_pct_pop 均為比例（0–1）',
        after='the rule names the five migration shares (proportions, 0-1) and the two COVID-19 percentages (0-100); the '
              'build stops if a stored scale and its documentation disagree',
        after_zh='規則列明五個移民占比（比例，0–1）與兩個 COVID-19 百分比（0–100）；儲存之尺度與說明不一致時，建置即中止',
        change='Values unchanged. covid_cases_pct_pop and covid_deaths_pct_pop store count / population x 100, as their '
               'own codebook rows say, but the general row said every *_pct_pop is a proportion: read that way, '
               'Australia 2020\'s 0.1107 (0.11% of the population) would be taken for 11%. The codebook (CSV and both '
               'workbooks) and the clean workbook\'s README now give each scale, in English and Chinese.',
        change_zh='數值不變。covid_cases_pct_pop 與 covid_deaths_pct_pop 儲存計數 ÷ 人口 × 100，與其各自之編碼簿列相符，但通則列稱所有 '
                  '*_pct_pop 均為比例：依此解讀，澳洲 2020 年之 0.1107（人口之 0.11%）將被誤讀為 11%。編碼簿（CSV 與兩個活頁簿）與精簡'
                  '活頁簿 README 現以中英文載明各自之尺度。')


def revision_who_dates():
    """Third commit of 2026-11-06 (GitHub issue #34): early-2020 dates in WHO's daily file."""
    k = counts()
    return dict(
        scope='COVID-19: dates in WHO\'s daily file, early 2020 (GitHub issue #34, COVID audit C01)',
        scope_zh='COVID-19：世界衛生組織每日檔 2020 年初之日期（GitHub issue #34，COVID-19 稽核發現 C01）',
        before='no caution on the dates of the WHO file',
        before_zh='未就世界衛生組織每日檔之日期提出說明',
        after='a known issue (low) and data/covid_who_date_check.csv (%d countries, %d differ from WHO\'s situation report '
              'of 13 February 2020); ECDC\'s and the Robert Koch Institute\'s chronology of Germany archived'
              % (k['n_datechk'], k['n_dateoff']),
        after_zh='新增已知問題（低）與 data/covid_who_date_check.csv（%d 國，其中 %d 國與世界衛生組織 2020 年 2 月 13 日之疫情報告不同）；'
                 '歐洲疾病預防控制中心與羅伯特·柯霍研究所之德國時序已存檔' % (k['n_datechk'], k['n_dateoff']),
        change='Values unchanged. The audit found Germany\'s first case and first deaths dated in early January 2020 in '
               'WHO\'s file, weeks before ECDC and the Robert Koch Institute date them; the archive\'s check of the daily '
               'counts against the cumulative ones cannot catch that. Comparing the file with WHO\'s own situation report '
               '24 shows the same for other countries. All the counts concerned fall within 2020, so no annual value '
               'changes; the known issue says not to use the file\'s early dates without checking them.',
        change_zh='數值不變。稽核發現世界衛生組織每日檔將德國首例病例與首批死亡標於 2020 年 1 月初，較歐洲疾病預防控制中心與羅伯特·柯霍'
                  '研究所所載早數週；本存檔以累計數核對每日數之方法無法察覺此情形。將每日檔與世界衛生組織自身之第 24 號疫情報告比對，'
                  '其他國家亦有相同情形。相關計數均在 2020 年內，故無年度值變動；已知問題說明未經核對前勿使用該檔之早期日期。')


def revision_history_fix():
    """Third commit of 2026-11-06: the revision history's own COVID-19 entries."""
    return dict(
        scope='Revision history: the COVID-19 entries of 6 November',
        scope_zh='修訂紀錄：11 月 6 日之 COVID-19 條目',
        before='the entry for commit 759cd18 said %d country-years per variable (%d values), recomputed from the data '
               'after China 2022 was added' % (REV1['n'] + 1, REV1['n_cells'] + 4),
        before_zh='commit 759cd18 之條目稱每一變項 %d 個國家年度（%d 筆數值），係於補增中國 2022 年後依資料重算'
                  % (REV1['n'] + 1, REV1['n_cells'] + 4),
        after='%d country-years per variable (%d values), as committed; each COVID-19 entry keeps the numbers of its own '
              'commit' % (REV1['n'], REV1['n_cells']),
        after_zh='每一變項 %d 個國家年度（%d 筆數值），與當時之 commit 相符；每一 COVID-19 條目均保留其 commit 當時之數字'
                 % (REV1['n'], REV1['n_cells']),
        change='Values unchanged. The history computed the first entry\'s counts from the current data, so adding China '
               '2022 rewrote what the earlier commit had published; the entries now carry the counts and values of their '
               'own commits.',
        change_zh='數值不變。修訂紀錄原依現行資料計算第一個條目之數字，故補增中國 2022 年後改寫了先前 commit 所發布之內容；各條目現保留'
                  '其 commit 當時之數字與數值。')


def revision():
    """The first entry of 2026-11-06, as committed in 759cd18 (China 2022 was still empty then)."""
    k = dict(counts(), n=REV1['n'], n_cells=REV1['n_cells'])
    return dict(
        scope='Four new variables: COVID-19 cases and deaths reported in the year, and each as %% of population, all %d '
              'countries, 2020-2022' % k['n_countries'],
        scope_zh='新增四個變項：COVID-19 年度通報病例數與死亡數，及其占人口百分比，全部 %d 國，2020–2022' % k['n_countries'],
        before='No COVID-19 variables.',
        before_zh='無 COVID-19 變項。',
        after='%d country-years per variable (%d values in all), 2020-2022; 44 columns appended to the panel (ten for each '
              'variable, and _derived/_derivation for the two percentages).' % (k['n'], k['n_cells']),
        after_zh='每一變項 %d 個國家年度（共 %d 筆數值），2020–2022；panel 末尾新增 44 欄（每一變項十欄，兩個百分比變項另加 _derived／'
                 '_derivation）。' % (k['n'], k['n_cells']),
        change='Added at the authors\' request. %d countries from WHO\'s COVID-19 data (daily file; France with its overseas '
               'departments); mainland China (2020-2021) from the National Health Commission; Taiwan from the Central '
               'Epidemic Command Center. Percentages computed with the panel\'s population. Checked against WHO\'s own '
               'cumulative counts and the Johns Hopkins CSSE archive. No other value in the panel changed.' % k['n_who_countries'],
        change_zh='應作者要求新增。%d 國取自世界衛生組織 COVID-19 資料（每日檔；法國含海外省）；中國大陸（2020–2021）取自國家衛生健康委員會；'
                  '臺灣取自中央流行疫情指揮中心。百分比以 panel 之人口計算。已與世界衛生組織之累計數及 Johns Hopkins CSSE 存檔核對。'
                  'panel 中其他數值皆未變動。' % k['n_who_countries'])
