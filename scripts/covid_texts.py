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
FR_DOM = ('Guadeloupe', 'Martinique', 'French Guiana', 'Réunion', 'Mayotte')

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
    names = p[['iso3']].drop_duplicates()
    return dict(n_comb=int(len(jj)), n_comb_cases_1pct=int((gc <= 1).sum()), n_comb_deaths_1pct=int((gd <= 1).sum()),
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
           'Mainland China: National Health Commission, cumulative counts as of 24:00 on 31 December (2020, 2021); '
           'Taiwan: Central Epidemic Command Center / Taiwan CDC, cumulative counts announced on 31 December.')
_SRC_ZH = ('38 國：世界衛生組織 COVID-19 儀表板資料（每日檔，依向世界衛生組織通報之日期之病例與死亡數）；法國含其五個海外省'
           '（世界衛生組織分列，但世界銀行人口包含之）。中國大陸：國家衛生健康委員會，12 月 31 日 24 時之累計數（2020、2021 年）；'
           '臺灣：中央流行疫情指揮中心／疾病管制署，12 月 31 日公布之累計數。')


def codebook_rows():
    """(name, definition, caution, definition_zh, caution_zh) rows for data/codebook.csv."""
    k = counts()
    caution = ('Years 2020-2022 only (none before 2020). Reported counts, not infections or excess deaths. Mainland China '
               '2022 is empty: national reporting stopped in December 2022, and WHO\'s figure for "China" includes Hong '
               'Kong, Macao and Taiwan. Verified: the WHO annual values equal the change in WHO\'s cumulative counts; '
               'against the Johns Hopkins CSSE archive, %d of %d country-years agree within 1%% for cases and %d for deaths, '
               'and over 2020-2022 combined %d and %d of %d countries do; the two compilations differ in reporting dates and, '
               'for some countries (%s, more than 5%% apart), in what they counted (data/covid_source_comparison.csv).'
               % (k['n_jhu_cases_1pct'], k['n_jhu'], k['n_jhu_deaths_1pct'], k['n_comb_cases_1pct'],
                  k['n_comb_deaths_1pct'], k['n_comb'], k['big_gaps']))
    caution_zh = ('僅 2020–2022 年（2020 年前無）。為通報數，而非感染數或超額死亡。中國大陸 2022 年留空：其全國通報於 2022 年 12 月停止，'
                  '而世界衛生組織之「中國」數字含香港、澳門與臺灣。已查證：世界衛生組織年度值等於其累計數之年度差；%d 個國家年度中，'
                  '病例數有 %d 個、死亡數有 %d 個與 Johns Hopkins CSSE 存檔相差在 1%% 以內；2020–2022 年合計，%d 國中病例數有 %d 國、'
                  '死亡數有 %d 國在 1%% 以內；兩者之差異來自通報日期，部分國家（%s，相差逾 5%%）則來自計入範圍不同'
                  '（data/covid_source_comparison.csv）。'
                  % (k['n_jhu'], k['n_jhu_cases_1pct'], k['n_jhu_deaths_1pct'], k['n_comb'], k['n_comb_cases_1pct'],
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
COLLECTED_EN = ' covid_* were collected on %s for every value.' % WHEN
COLLECTED_ZH = 'covid_* 之每一筆數值均於 %s 蒐集。' % WHEN


def known_issues():
    k = counts()
    china = dict(
        severity='MEDIUM', scope='China', variable=CASES,
        issue='Mainland China has COVID-19 values for 2020 and 2021 only. WHO\'s series for "China" includes Hong Kong '
              'SAR, Macao SAR and Taiwan (WHO situation report 24 says so; for 31 December 2021 WHO\'s total equals the '
              'National Health Commission\'s mainland count plus the three, case for case). In 2022 that series no longer '
              'adds up (WHO\'s China total is smaller than Hong Kong plus Taiwan alone from March), and China\'s national '
              'daily reporting stopped in December 2022, so no mainland figure for 2022 can be traced to a source.',
        issue_zh='中國大陸僅有 2020 與 2021 年之 COVID-19 數值。世界衛生組織之「中國」序列包含香港、澳門與臺灣（世界衛生組織第 24 號疫情'
                 '報告載明；2021 年 12 月 31 日世界衛生組織之總數，恰等於國家衛生健康委員會之大陸累計數加上三地之數）。2022 年該序列已無法'
                 '加總對應（自 3 月起，世界衛生組織之中國總數小於香港與臺灣兩地之和），且中國之全國每日通報於 2022 年 12 月停止，故 2022 年'
                 '無可追溯至來源之大陸數字。',
        evidence='evidence/countries/CHN/: the National Health Commission\'s briefings for 31 December 2020 and 2021 (mainland, '
                 'Hong Kong, Macao and Taiwan counts); evidence/api/: WHO situation report 24 (page 5 footnote) and the WHO '
                 'daily file; data/covid_source_comparison.csv puts WHO\'s China figures beside the mainland ones.',
        evidence_zh='evidence/countries/CHN/：國家衛生健康委員會 2020 與 2021 年 12 月 31 日之通報（大陸、香港、澳門與臺灣之數）；'
                    'evidence/api/：世界衛生組織第 24 號疫情報告（第 5 頁註腳）與世界衛生組織每日檔；data/covid_source_comparison.csv '
                    '並列世界衛生組織之中國數字與大陸數字。',
        action='China 2022 is empty in all four COVID-19 variables. Do not substitute WHO\'s China figure: it covers a '
               'different territory.',
        action_zh='中國 2022 年於四個 COVID-19 變項皆留空。請勿以世界衛生組織之中國數字替代：其涵蓋範圍不同。')
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
    return [china, rep]


def verdict():
    k = counts()
    return {
        'en': 'Fair. One source for 38 countries (WHO, checked against its own cumulative counts and the Johns Hopkins '
              'archive), mainland China and Taiwan from their national authorities; but reported counts depend on '
              'testing and certification, China 2022 is missing, and only 2020-2022 exist.',
        'zh': '尚可。38 國來源一致（世界衛生組織，並與其累計數及 Johns Hopkins 存檔核對），中國大陸與臺灣取自其主管機關；但通報數取決於'
              '檢驗與死因認定，中國 2022 年缺漏，且僅有 2020–2022 年。',
    }


def revision():
    k = counts()
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
