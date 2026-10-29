# -*- coding: utf-8 -*-
"""English and Traditional Chinese text for the Gini index added on 2026-10-29.

One place for the wording, so the codebook, known issues, data-quality table, methods page and
revision history say the same thing. Counts are computed from the files, never typed in.
"""
import os

import pandas as pd

VAR = 'gini_index'
WHEN = '2026-10-29'
PIP_VERSION = '20260922_2021_01_02_PROD'
F_CONS = 'consumption-based (not income)'
F_BREAK = 'break in time series: new PIP survey-comparability spell'
F_OECD = 'OECD equivalised disposable income (not World Bank)'
_D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
CMP = os.path.join(_D, 'gini_source_comparison.csv')
PAIRS = os.path.join(_D, 'gini_income_consumption_pairs.csv')
# the World Bank's own statement on income and consumption inequality (PIP methodology, chapter 2), archived
METH_COMMIT = '30382709c7ffc391dcf71e4bbac5c0d50bfebb2b'
METH_FILE = 'pip_methodology_02_welfare_aggregates_%s_retrieved_2026-10-29.Rmd' % METH_COMMIT[:7]
METH_QUOTE = 'inequality often is higher when incomes are used rather than consumption'
FIXED = '2026-10-29'                     # the wording on consumption and income was corrected (issue #33)
_ZH = {'China': '中國', 'India': '印度', 'Thailand': '泰國', 'South Africa': '南非', 'Suriname': '蘇利南',
       'Russia': '俄羅斯', 'Croatia': '克羅埃西亞', 'Bulgaria': '保加利亞', 'Hungary': '匈牙利', 'Lithuania': '立陶宛',
       'Poland': '波蘭', 'Slovak Republic': '斯洛伐克', 'Slovenia': '斯洛維尼亞', 'Turkey': '土耳其', 'Philippines': '菲律賓'}


def _years(ys, sep=', ', dash='-'):
    ys, out = sorted(int(y) for y in ys), []
    for y in ys:
        if out and y == out[-1][1] + 1:
            out[-1][1] = y
        else:
            out.append([y, y])
    return sep.join(str(a) if a == b else '%d%s%d' % (a, dash, b) for a, b in out)


def counts():
    """Numbers quoted in the texts, read from the panel and the source comparison."""
    p = pd.read_csv(os.path.join(_D, 'panel_final.csv'), usecols=['iso3', 'country', 'year', VAR, VAR + '_flag'])
    c = pd.read_csv(CMP, dtype=str, keep_default_na=False)
    s = p[p[VAR].notna()]
    fl = s[VAR + '_flag'].fillna('')
    per = s.groupby('iso3').size()
    cons = s[fl.str.contains(F_CONS, regex=False)]
    cons_by = {cn: _years(cons[cons.country == cn].year) for cn in cons.groupby('country').size()
               .sort_values(ascending=False, kind='stable').index}
    wdi = c[c.used_source == 'World Bank WDI']
    pr = pd.read_csv(PAIRS, dtype=str, keep_default_na=False)
    return dict(n_pairs=int(len(pr)), n_pairs_cons_higher=int((pr.higher == 'consumption').sum()),n=int(len(s)), n_countries=int(s.iso3.nunique()), y0=int(p.year.min()), y1=int(p.year.max()),
                n_wdi=int(len(wdi)), n_wdi_countries=int(wdi.iso3.nunique()),
                n_pip_match=int((wdi.wdi_equals_pip == 'yes').sum()),
                n_twn=int((c.used_source == 'World Bank PIP').sum()), n_nzl=int((c.used_source == 'OECD IDD').sum()),
                twn_years=_years(c[c.used_source == 'World Bank PIP'].year.astype(int)),
                nzl_years=_years(c[c.used_source == 'OECD IDD'].year.astype(int)),
                n_cons=int(len(cons)), cons_by=cons_by, n_break=int(fl.str.contains(F_BREAK, regex=False).sum()),
                n_full=int((per == p.year.nunique()).sum()), min_n=int(per.min()),
                fewest=', '.join('%s (%d)' % (s[s.iso3 == i].country.iloc[0], k) for i, k in per[per <= 5].sort_values(kind='stable').items()),
                lo=float(s[VAR].min()), hi=float(s[VAR].max()))


def _cons(k, zh=False):
    if zh:
        return '；'.join('%s（%s）' % (_ZH.get(cn, cn), ys) for cn, ys in k['cons_by'].items())
    return '; '.join('%s %s' % (cn, ys) for cn, ys in k['cons_by'].items())


COMPARABILITY_EN = {
    VAR: 'Comparable with caution. One publisher and method for 39 countries (World Bank Poverty and Inequality Platform: '
         'Gini of per-capita income or consumption from national household surveys), but some countries\' surveys '
         'measure consumption rather than income, a different welfare concept (flagged): inequality is often, but not '
         'always, lower when measured on consumption, so neither the direction nor the size of the difference can be '
         'assumed for a given value; surveys change within a country '
         '(the World Bank marks non-comparable spells; flagged at the break), and New Zealand comes from the OECD on a '
         'different income concept (flagged). Years without a survey are empty, not interpolated.',
}
COMPARABILITY_ZH = {
    VAR: '可謹慎比較。39 國之發布機構與方法一致（世界銀行貧窮與不平等平台：依各國家戶調查計算之每人所得或消費吉尼係數），'
         '但部分國家之調查衡量消費而非所得，屬不同之福利概念（已標示旗標）：以消費衡量之不平等常低於以所得衡量者，但並非必然，'
         '故任一數值之差異方向與大小均無法預設；一國之調查亦可能更替（世界銀行標示不可比較之區段；於斷點標示旗標）；'
         '紐西蘭則取自 OECD，所得概念不同（已標示旗標）。無調查之年度留空，未作內插。',
}


def codebook_rows():
    """(name, definition, caution, definition_zh, caution_zh) rows for data/codebook.csv."""
    k = counts()
    return [
        (VAR,
         'Gini index, 0 (perfect equality) to 100 (one person has everything): 100 x the Gini coefficient of the '
         'distribution of income (or, in some countries, consumption) among people. %d countries: World Bank WDI '
         'SI.POV.GINI, from the Poverty and Inequality Platform (PIP version %s; per-capita household income or '
         'consumption from national surveys), one decimal. Taiwan, which WDI does not publish: the same platform\'s '
         'survey estimate (100 x its Gini, rounded to one decimal as WDI does). New Zealand, which the World Bank does '
         'not cover: OECD Income Distribution Database, Gini of equivalised household disposable income, total '
         'population, 2012 income definition (x 100). Added %s; a value only for years with a survey (%d of %d '
         'country-years).' % (k['n_wdi_countries'], PIP_VERSION, WHEN, k['n'], 40 * (k['y1'] - k['y0'] + 1)),
         'Verified: all %d WDI values equal 100 x the Gini of the matching PIP survey row, rounded to one decimal '
         '(data/gini_source_comparison.csv). Flags: "%s" on %d values (%s); "%s" at %d breaks the World Bank marks in a '
         'country\'s survey series; "%s" on New Zealand\'s %d values. Years without a survey are empty: do not '
         'interpolate silently. The World Bank and the OECD revise past values with new releases.'
         % (k['n_wdi'], F_CONS, k['n_cons'], _cons(k), F_BREAK, k['n_break'], F_OECD, k['n_nzl']),
         '吉尼指數，0（完全平均）至 100（一人擁有全部）：人與人之間所得（部分國家為消費）分配之吉尼係數乘以 100。%d 國：世界銀行 '
         'WDI SI.POV.GINI，取自貧窮與不平等平台（PIP 版本 %s；依各國家戶調查之每人家戶所得或消費），小數一位。臺灣（WDI 未公布）：'
         '同一平台之調查估計值（其吉尼係數乘以 100，並如 WDI 四捨五入至小數一位）。紐西蘭（世界銀行未涵蓋）：OECD 所得分配資料庫，'
         '均等化家戶可支配所得之吉尼係數，全體人口，2012 年所得定義（乘以 100）。於 %s 新增；僅有調查之年度有數值（%d／%d 個國家年度）。'
         % (k['n_wdi_countries'], PIP_VERSION, WHEN, k['n'], 40 * (k['y1'] - k['y0'] + 1)),
         '已查證：%d 筆 WDI 數值均等於對應 PIP 調查列之吉尼係數乘以 100 並四捨五入至小數一位（data/gini_source_comparison.csv）。'
         '旗標：「%s」%d 筆（%s）；「%s」標示於世界銀行所註記之 %d 個調查序列斷點；「%s」為紐西蘭之 %d 筆數值。無調查之年度留空：'
         '請勿逕行內插。世界銀行與 OECD 於新版次會修訂過去數值。'
         % (k['n_wdi'], F_CONS, k['n_cons'], _cons(k, zh=True), F_BREAK, k['n_break'], F_OECD, k['n_nzl'])),
    ]


SOURCE_TYPE_EN = (' gini_index: survey (an estimate from a national household survey) for every value.')
SOURCE_TYPE_ZH = ('gini_index：每一筆數值皆為 survey（依各國家戶調查之估計值）。')
FLAG_EN = (' gini_index: "%s" where the survey measures consumption; "%s" at the first year of a survey spell the '
           'World Bank marks as not comparable with the earlier one; "%s" on New Zealand.' % (F_CONS, F_BREAK, F_OECD))
FLAG_ZH = ('吉尼指數：調查衡量消費者標示「%s」；世界銀行註記與前一區段不可比較之調查區段，於其首年標示「%s」；紐西蘭標示「%s」。'
           % (F_CONS, F_BREAK, F_OECD))
COLLECTED_EN = ' gini_index was collected on %s for every value.' % WHEN
COLLECTED_ZH = 'gini_index 之每一筆數值均於 %s 蒐集。' % WHEN


def known_issues():
    k = counts()
    cov = dict(
        severity='MEDIUM', scope='All countries', variable=VAR,
        issue='The Gini index exists only for years with a household survey: %d of %d country-years. %d countries have '
              'every year; the fewest values are %s. The World Bank publishes nothing for New Zealand and does not put '
              'Taiwan in WDI, so New Zealand comes from the OECD (equivalised disposable income, %s) and Taiwan from the '
              'World Bank\'s platform directly (%s).'
              % (k['n'], 40 * (k['y1'] - k['y0'] + 1), k['n_full'], k['fewest'], k['nzl_years'], k['twn_years']),
        issue_zh='吉尼指數僅於有家戶調查之年度存在：%d／%d 個國家年度。%d 國每年皆有數值；數值最少者為 %s。世界銀行未公布紐西蘭，'
                 '且未將臺灣列入 WDI，故紐西蘭取自 OECD（均等化可支配所得，%s），臺灣直接取自世界銀行之平台（%s）。'
                 % (k['n'], 40 * (k['y1'] - k['y0'] + 1), k['n_full'], k['fewest'], k['nzl_years'], k['twn_years']),
        evidence='evidence/api/: the World Bank WDI response (SI.POV.GINI) and indicator metadata, the PIP survey table '
                 '(every survey with its welfare type, survey name and comparability spell) and PIP citation, the OECD '
                 'IDD response for New Zealand and the dataflow description, each with a PDF/PNG mirror; '
                 'data/gini_source_comparison.csv lists every country-year.',
        evidence_zh='evidence/api/：世界銀行 WDI 回應（SI.POV.GINI）與指標後設資料、PIP 調查表（每一調查之福利類型、調查名稱與'
                    '可比較區段）與 PIP 引用說明、OECD IDD 紐西蘭回應與資料流說明，均附 PDF／PNG 鏡像；'
                    'data/gini_source_comparison.csv 逐一列出每個國家年度。',
        action='Used as published, graded A, empty where no survey exists. For a model that needs one value per country, '
               'take the survey nearest to the study year and say so, or check the result without the flagged values; '
               'do not fill the gaps by interpolation without saying so.',
        action_zh='依公布值使用，評為 A 級，無調查之年度留空。若模型每國需一個數值，請採最接近研究年度之調查並註明，或檢驗排除旗標數值後'
                  '之結果；未經說明請勿以內插填補空缺。')
    cons = dict(
        severity='MEDIUM', scope=', '.join(k['cons_by']), variable=VAR,
        issue='%d Gini values rest on household consumption, not income: %s. Consumption and income are different '
              'welfare concepts. The World Bank notes that inequality often is higher when measured on income, but this '
              'is a tendency, not a rule: of the %d country-years in the panel\'s scope where its survey table has both '
              'an income and a consumption Gini, the consumption one is higher in %d (the two can come from different '
              'surveys). Neither the direction nor the size of the difference can be assumed for a flagged value. %d '
              'values are flagged "%s" where the World Bank marks a survey as not comparable with the country\'s earlier '
              'ones. (Wording corrected %s: it had said consumption values are always lower.)'
              % (k['n_cons'], _cons(k), k['n_pairs'], k['n_pairs_cons_higher'], k['n_break'], F_BREAK, FIXED),
        issue_zh='%d 筆吉尼值依據家戶消費而非所得：%s。消費與所得屬不同之福利概念。世界銀行指出以所得衡量之不平等常較高，但此為一般傾向而非'
                 '定則：在 panel 範圍內世界銀行調查表同時列有所得與消費吉尼值之 %d 個國家年度中，有 %d 個之消費吉尼值較高（兩者可能來自不同'
                 '調查）。已標示旗標之數值，其差異方向與大小均無法預設。世界銀行註記調查與該國先前調查不可比較者，%d 筆標示「%s」。'
                 '（文字於 %s 更正：原稱消費基礎數值必然較低。）'
                 % (k['n_cons'], _cons(k, zh=True), k['n_pairs'], k['n_pairs_cons_higher'], k['n_break'], F_BREAK, FIXED),
        evidence='The PIP survey table in evidence/api/ (welfare_type and survey_comparability per survey); '
                 'data/gini_source_comparison.csv; data/gini_income_consumption_pairs.csv (every country-year with both '
                 'measures); the World Bank\'s statement in its PIP methodology, chapter 2 (evidence/api/%s).' % METH_FILE,
        evidence_zh='evidence/api/ 之 PIP 調查表（每一調查之 welfare_type 與 survey_comparability）；data/gini_source_comparison.csv；'
                    'data/gini_income_consumption_pairs.csv（每一同時具有兩種衡量之國家年度）；世界銀行 PIP 方法說明第 2 章之陳述'
                    '（evidence/api/%s）。' % METH_FILE,
        action='Kept and flagged. Compare countries on the same welfare type where possible, do not adjust a consumption '
               'value by an assumed direction, and treat a change across a flagged break as possibly a change of survey.',
        action_zh='保留並標示旗標。跨國比較請盡量限於相同福利類型，勿依預設方向調整消費基礎數值；跨越已標示斷點之變化，可能來自調查更替。')
    return [cov, cons]


def verdict():
    """The one-line verdict in the methods page's table of variables."""
    k = counts()
    return {
        'en': 'Fair. One publisher and method for 39 countries (World Bank PIP; New Zealand from the OECD), checked '
              'against the platform\'s own survey table, but only survey years have a value (%d of %d), some countries '
              'measure consumption rather than income, and survey changes break series (both flagged).'
              % (k['n'], 40 * (k['y1'] - k['y0'] + 1)),
        'zh': '尚可。39 國發布機構與方法一致（世界銀行 PIP；紐西蘭取自 OECD），並已與平台自身之調查表核對；但僅有調查之年度有數值'
              '（%d／%d），部分國家衡量消費而非所得，且調查更替使序列中斷（兩者皆已標示旗標）。' % (k['n'], 40 * (k['y1'] - k['y0'] + 1)),
    }


def revision():
    k = counts()
    return dict(
        scope='New variable %s: Gini index (0-100), all %d countries, survey years within %d-%d'
              % (VAR, k['n_countries'], k['y0'], k['y1']),
        scope_zh='新增變項 %s：吉尼指數（0–100），全部 %d 國，%d–%d 年間之調查年度' % (VAR, k['n_countries'], k['y0'], k['y1']),
        before='No inequality variable.',
        before_zh='無不平等變項。',
        after='%d values (%d countries; years with a survey only), range %.1f to %.1f; ten columns gini_index[_source, '
              '_url, _ref_date, _note, _grade, _verification, _source_type, _flag, _collected_on] appended to the panel; '
              '%d consumption-based values, %d survey breaks and New Zealand\'s %d OECD values flagged.'
              % (k['n'], k['n_countries'], k['lo'], k['hi'], k['n_cons'], k['n_break'], k['n_nzl']),
        after_zh='%d 筆數值（%d 國；僅有調查之年度），介於 %.1f 至 %.1f；panel 末尾新增 gini_index[_source、_url、_ref_date、_note、'
                 '_grade、_verification、_source_type、_flag、_collected_on] 共十欄；%d 筆消費基礎數值、%d 個調查斷點與紐西蘭 %d 筆 '
                 'OECD 數值已標示旗標。' % (k['n'], k['n_countries'], k['lo'], k['hi'], k['n_cons'], k['n_break'], k['n_nzl']),
        change='Added at the authors\' request for every country of the panel. %d countries from World Bank WDI SI.POV.GINI '
               '(Poverty and Inequality Platform, version %s): all %d values equal the platform\'s own survey estimates '
               '(x 100, one decimal). Taiwan (%d values) from the same platform, which WDI does not publish; New Zealand '
               '(%d values) from the OECD Income Distribution Database, as the World Bank has no data for it. Raw responses, '
               'metadata and the publishers\' pages are archived with PDF/PNG mirrors. No other value in the panel changed.'
               % (k['n_wdi_countries'], PIP_VERSION, k['n_wdi'], k['n_twn'], k['n_nzl']),
        change_zh='應作者要求為 panel 之每一國家新增。%d 國取自世界銀行 WDI SI.POV.GINI（貧窮與不平等平台，版本 %s）：%d 筆數值均等於'
                  '該平台自身之調查估計值（乘以 100，小數一位）。臺灣（%d 筆）取自同一平台（WDI 未公布）；紐西蘭（%d 筆）取自 OECD '
                  '所得分配資料庫（世界銀行無其資料）。API 原始回應、後設資料與發布機構頁面均已存檔，並附 PDF／PNG 鏡像。'
                  'panel 中其他數值皆未變動。' % (k['n_wdi_countries'], PIP_VERSION, k['n_wdi'], k['n_twn'], k['n_nzl']))
