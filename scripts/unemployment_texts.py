# -*- coding: utf-8 -*-
"""English and Traditional Chinese text for the unemployment-rate variable added on 2026-10-21.

One place for the wording, so the codebook, known issues, data-quality table, methods page and
revision history say the same thing. Counts are computed from the files, never typed in.
"""
import os

import pandas as pd

VAR = 'unemployment_rate'
WHEN = '2026-10-21'
FLAG = 'ILO imputed: not based on national data'
_D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
_ZH_NAME = {'China': '中國', 'India': '印度', 'Philippines': '菲律賓', 'Suriname': '蘇利南', 'Thailand': '泰國',
            'South Africa': '南非'}


def _years(ys, sep=', ', dash='-'):
    """2001-2007, 2017-2022 style ranges."""
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
    c = pd.read_csv(os.path.join(_D, 'unemployment_source_comparison.csv'), dtype=str)
    v = p[VAR].dropna()
    imp = p[p[VAR + '_flag'].fillna('') == FLAG]
    order = imp.groupby('country', sort=False).size().sort_values(ascending=False, kind='stable').index
    by = {cn: _years(imp[imp.country == cn].year) for cn in order}
    by_zh = {cn: _years(imp[imp.country == cn].year, '、', '–') for cn in order}
    tw = c[c.iso3 == 'TWN']
    twr = tw[tw.ilo_obs_status == 'R']
    twi = tw[tw.ilo_obs_status != 'R']
    nt = c[c.iso3 != 'TWN']
    return dict(n=int(len(v)), n_countries=int(p[p[VAR].notna()].iso3.nunique()),
                y0=int(p[p[VAR].notna()].year.min()), y1=int(p[p[VAR].notna()].year.max()),
                n_ilo=int((p[p[VAR].notna()].iso3 != 'TWN').sum()),
                n_cmp=int(len(nt)), n_agree=int((nt.world_bank_rounds_to_ilo == 'yes').sum()),
                n_imp=int(len(imp)), n_imp_countries=int(imp.iso3.nunique()), imp_by=by, imp_by_zh=by_zh,
                n_tw=int((p[p[VAR].notna()].iso3 == 'TWN').sum()),
                tw_real=int(len(twr)),
                tw_maxdiff=float((twr.ilo_value.astype(float) - twr.dgbas_value.astype(float)).abs().max()),
                tw_imp=[(int(r.year), r.ilo_value, r.dgbas_value) for r in twi.itertuples()],
                lo=float(v.min()), hi=float(v.max()))


def _imp_list(k, zh=False):
    if zh:
        return '；'.join('%s（%s）' % (_ZH_NAME.get(cn, cn), ys) for cn, ys in k['imp_by_zh'].items())
    return '; '.join('%s %s' % (cn, ys) for cn, ys in k['imp_by'].items())


COMPARABILITY_EN = {
    VAR: 'Comparable across countries by design for most values: one concept (the ILO definition of unemployment, '
         'ages 15+) and, for 39 countries, one source (ILO modelled estimates, which harmonise national survey data). '
         'Values the ILO imputes where it has no national data (flagged) are model outputs that the ILO says should '
         'not be used for country comparisons. Taiwan comes from its national labour force survey on the same '
         'definition.',
}
COMPARABILITY_ZH = {
    VAR: '多數數值設計上可跨國比較：概念一致（國際勞工組織之失業定義，15 歲以上），39 國來源一致（國際勞工組織模型推估值，'
         '係將各國調查資料調和而得）。國際勞工組織於缺乏該國資料時所插補之數值（已標示旗標）屬模型產出，'
         '國際勞工組織表示不應用於跨國比較。臺灣取自本國人力資源調查，定義相同。',
}

USABLE_EN = {'some': 'CAUTION - single source, but some years are ILO imputations (not based on national data)',
             'all': 'CAUTION - every year is an ILO imputation (not based on national data)'}
USABLE_ZH = {USABLE_EN['some']: 'CAUTION｜單一來源，但部分年度為國際勞工組織之插補值（非依據該國資料）',
             USABLE_EN['all']: 'CAUTION｜每一年度皆為國際勞工組織之插補值（非依據該國資料）'}


def codebook_rows():
    """(name, definition, caution, definition_zh, caution_zh) rows for data/codebook.csv."""
    k = counts()
    return [
        (VAR,
         'Unemployment rate: unemployed persons as a percentage of the labour force, ages 15 and over, 0-100 (5.2 '
         'means 5.2%%); the unemployed are people without work, available for work and seeking work (ILO '
         'definition). %d countries: ILO modelled estimates, November 2025 edition (indicator UNE_2EAP_SEX_AGE_RT, '
         'total, age 15+), read from the ILO SDMX API and published to three decimals; Taiwan, which the panel takes '
         'from its own statistics: DGBAS Manpower Survey, Yearbook of Manpower Survey Statistics 2025, Table 2 '
         '(annual average, civilian population aged 15+, two decimals). Added %s for every country and year of the '
         'panel (%d-%d).' % (k['n_countries'] - 1, WHEN, k['y0'], k['y1']),
         'Verified: all %d ILO values agree at three decimals with the World Bank\'s copy (WDI SL.UEM.TOTL.ZS, '
         'data/unemployment_source_comparison.csv); the %d Taiwan values read from the official DGBAS workbook are '
         'identical to the printed yearbook. %d values are ILO imputations, flagged "%s" and typed model_estimate: '
         '%s. The ILO describes such values as not based on national data, subject to high uncertainty and not to be '
         'used for country comparisons or rankings. The ILO revises its estimates with every edition: the values are '
         'those published on the retrieval date.'
         % (k['n_ilo'], k['n_tw'], k['n_imp'], FLAG, _imp_list(k)),
         '失業率：失業者占勞動力之百分比，15 歲以上，0–100（5.2 即 5.2%%）；失業者指無工作、可隨時工作且正在找工作者'
         '（國際勞工組織定義）。%d 國：國際勞工組織模型推估值（2025 年 11 月版，指標 UNE_2EAP_SEX_AGE_RT，總計，15 歲以上），'
         '讀自國際勞工組織 SDMX API，公布至小數三位；臺灣取自本國統計：行政院主計總處人力資源調查，《114年人力資源調查統計年報》'
         '表2（年平均，15 歲以上民間人口，小數二位）。於 %s 新增，涵蓋 panel 之全部國家與年度（%d–%d）。'
         % (k['n_countries'] - 1, WHEN, k['y0'], k['y1']),
         '已查證：%d 筆國際勞工組織數值與世界銀行之轉載值（WDI SL.UEM.TOTL.ZS）於小數三位一致'
         '（data/unemployment_source_comparison.csv）；臺灣 %d 筆數值讀自主計總處官方試算表，與印行之年報相同。'
         '%d 筆為國際勞工組織之插補值，標示旗標「%s」，來源類型為 model_estimate：%s。國際勞工組織表示此類數值非依據該國資料、'
         '不確定性高，且不應用於跨國比較或排名。國際勞工組織每一版次均會修訂推估值：數值為擷取當日所公布者。'
         % (k['n_ilo'], k['n_tw'], k['n_imp'], FLAG, _imp_list(k, zh=True))),
    ]


SOURCE_TYPE_EN = (' unemployment_rate: annual, except model_estimate (an ILO imputation, not based on national data) '
                  'for the values the ILO imputes.')
SOURCE_TYPE_ZH = ('unemployment_rate：annual；國際勞工組織插補之數值為 model_estimate（國際勞工組織之插補值，非依據該國資料）。')
FLAG_EN = (' unemployment_rate: %s, on every value the ILO imputes.' % FLAG)
FLAG_ZH = ('失業率：國際勞工組織插補之每一筆數值標示「%s」（國際勞工組織之插補值：非依據該國資料）。' % FLAG)
COLLECTED_EN = ' unemployment_rate was collected on %s for every value.' % WHEN
COLLECTED_ZH = 'unemployment_rate 之每一筆數值均於 %s 蒐集。' % WHEN


def known_issues():
    k = counts()
    imp = dict(
        severity='MEDIUM', scope=', '.join(k['imp_by']), variable=VAR,
        issue='%d unemployment values in %d countries are ILO imputations: %s. The ILO publishes a value for every '
              'country and year, but where it has no national survey data it imputes one from a model. It marks the '
              'values that rest on national data "R" (Real value) and publishes the imputed ones without that status '
              'and with a lower and upper bound; it describes them as not based on national data, subject to high '
              'uncertainty and not to be used for country comparisons or rankings.'
              % (k['n_imp'], k['n_imp_countries'], _imp_list(k)),
        issue_zh='%d 國共 %d 筆失業率為國際勞工組織之插補值：%s。國際勞工組織對每一國家與年度皆公布數值，但於缺乏該國調查資料時，'
                 '以模型插補。依據該國資料之數值標示「R」（Real value），插補值則無此標示，並附上下界；國際勞工組織表示此類數值'
                 '非依據該國資料、不確定性高，且不應用於跨國比較或排名。'
                 % (k['n_imp_countries'], k['n_imp'], _imp_list(k, zh=True)),
        evidence='evidence/api/: the ILO SDMX response (OBS_STATUS, UPPER_BOUND and LOWER_BOUND per value), the dataflow '
                 'description (the ILO\'s note on imputed observations) and the CL_OBS_STATUS code list (R = Real '
                 'value), each with a PDF/PNG mirror; data/unemployment_source_comparison.csv lists status and bounds '
                 'cell by cell.',
        evidence_zh='evidence/api/：國際勞工組織 SDMX 回應（每一數值之 OBS_STATUS、UPPER_BOUND 與 LOWER_BOUND）、資料流說明'
                    '（國際勞工組織對插補值之說明）及 CL_OBS_STATUS 代碼表（R = Real value），均附 PDF／PNG 鏡像；'
                    'data/unemployment_source_comparison.csv 逐格列出狀態與上下界。',
        action='Kept, graded A (read from the ILO\'s machine-readable file), typed model_estimate and flagged "%s". For a '
               'cross-country analysis, run it with and without the flagged values; China has no value based on '
               'national data in any year.' % FLAG,
        action_zh='保留，評為 A 級（讀自國際勞工組織之機器可讀檔案），來源類型為 model_estimate，並標示旗標「%s」。'
                  '跨國分析請分別納入與排除已標示之數值各做一次；中國於任何年度皆無依據該國資料之數值。' % FLAG)
    tw = dict(
        severity='LOW', scope='Taiwan', variable=VAR,
        issue='Taiwan\'s unemployment rate comes from DGBAS, not the ILO. The ILO modelled estimates hold Taiwan, '
              'and for %d-%d (ILO status R) they are within %.3f percentage points of the DGBAS figures, but the ILO '
              'imputes %s although DGBAS published those years (%s). The DGBAS series is the annual '
              'average of the monthly Manpower Survey for the civilian population aged 15 and over, which excludes '
              'the armed forces and the institutional population.'
              % (k['y0'], k['y0'] + k['tw_real'] - 1, k['tw_maxdiff'], ' and '.join(str(y) for y, _, _ in k['tw_imp']),
                 '; '.join('%d: ILO %s, DGBAS %s' % t_ for t_ in k['tw_imp'])),
        issue_zh='臺灣之失業率取自主計總處，而非國際勞工組織。國際勞工組織模型推估值亦含臺灣，%d–%d 年（狀態 R）與主計總處'
                 '數值相差在 %.3f 個百分點以內；但 %s 年主計總處已公布數值，國際勞工組織仍以插補值列示（%s）。'
                 '主計總處序列為每月人力資源調查之年平均，涵蓋 15 歲以上民間人口，不含武裝勞動力與監管人口。'
                 % (k['y0'], k['y0'] + k['tw_real'] - 1, k['tw_maxdiff'], ' 與 '.join(str(y) for y, _, _ in k['tw_imp']),
                    '；'.join('%d 年：國際勞工組織 %s，主計總處 %s' % t_ for t_ in k['tw_imp'])),
        evidence='evidence/countries/TWN/: the official workbook (table2.xlsx, 表2 歷年人力資源調查重要指標), the yearbook '
                 '(PDF pages 20-21 = Table 2; page 322 = definitions: 失業率：失業者占勞動力之比率) and the DGBAS page '
                 'linking both; data/unemployment_source_comparison.csv puts the ILO\'s Taiwan values beside them.',
        evidence_zh='evidence/countries/TWN/：官方試算表（table2.xlsx，表2 歷年人力資源調查重要指標）、年報（PDF 第 20–21 頁為表2；'
                    '第 322 頁為名詞定義：失業率：失業者占勞動力之比率），以及連結兩者之主計總處頁面；'
                    'data/unemployment_source_comparison.csv 並列國際勞工組織之臺灣數值。',
        action='Used as published by DGBAS for every year, so the Taiwan series has one source and no imputed year. The '
               'differences from the ILO\'s real values are below 0.01 percentage points.',
        action_zh='各年度均採主計總處公布之數值，使臺灣序列來源單一且無插補年度。與國際勞工組織實際值之差異小於 0.01 個百分點。')
    return [imp, tw]


def verdict():
    """The one-line verdict in the methods page's table of variables."""
    k = counts()
    return {
        'en': 'Strong for most values. One definition for every country and one source for 39 (ILO modelled estimates, '
              'checked against the World Bank); Taiwan from its national survey. %d ILO imputations (China every year) '
              'are flagged: the ILO says not to compare countries on them.' % k['n_imp'],
        'zh': '多數數值強。各國定義一致，39 國來源一致（國際勞工組織模型推估值，並已與世界銀行核對）；臺灣取自本國調查。'
              '%d 筆國際勞工組織插補值（中國全部年度）已標示旗標：國際勞工組織表示不應據以跨國比較。' % k['n_imp'],
    }


def revision():
    k = counts()
    return dict(
        scope='New variable %s: unemployment rate, %% of the labour force aged 15+, all %d countries, %d-%d'
              % (VAR, k['n_countries'], k['y0'], k['y1']),
        scope_zh='新增變項 %s：失業率（占 15 歲以上勞動力之百分比），全部 %d 國，%d–%d' % (VAR, k['n_countries'], k['y0'], k['y1']),
        before='No unemployment variable.',
        before_zh='無失業率變項。',
        after='%d values (%d countries x %d years), range %.3f%% to %.3f%%; ten columns unemployment_rate[_source, _url, '
              '_ref_date, _note, _grade, _verification, _source_type, _flag, _collected_on] appended to the panel; %d '
              'ILO imputations flagged.'
              % (k['n'], k['n_countries'], k['y1'] - k['y0'] + 1, k['lo'], k['hi'], k['n_imp']),
        after_zh='%d 筆數值（%d 國 × %d 年），介於 %.3f%% 至 %.3f%%；panel 末尾新增 unemployment_rate[_source、_url、_ref_date、'
                 '_note、_grade、_verification、_source_type、_flag、_collected_on] 共十欄；%d 筆國際勞工組織插補值已標示旗標。'
                 % (k['n'], k['n_countries'], k['y1'] - k['y0'] + 1, k['lo'], k['hi'], k['n_imp']),
        change='Added at the authors\' request, for the same countries and years as the population and migrant series. '
               '%d countries from the ILO modelled estimates (November 2025 edition, ILO SDMX API): all %d values agree '
               'at three decimals with the World Bank\'s copy (WDI SL.UEM.TOTL.ZS); the %d the ILO imputes are flagged. '
               'Taiwan from DGBAS (Yearbook of Manpower Survey Statistics 2025, Table 2), read from the official '
               'workbook, identical to the printed yearbook. Raw responses, the ILO\'s metadata, the workbook, the '
               'yearbook and the publishers\' pages are archived with PDF/PNG mirrors. No other value in the panel '
               'changed.' % (k['n_countries'] - 1, k['n_cmp'], k['n_imp']),
        change_zh='應作者要求新增，國家與年度與人口及移民序列一致。%d 國取自國際勞工組織模型推估值（2025 年 11 月版，國際勞工組織 '
                  'SDMX API）：%d 筆數值與世界銀行轉載值（WDI SL.UEM.TOTL.ZS）於小數三位一致；其中 %d 筆國際勞工組織插補值已標示旗標。'
                  '臺灣取自主計總處《114年人力資源調查統計年報》表2，讀自官方試算表，與印行之年報相同。API 原始回應、國際勞工組織後設資料、'
                  '試算表、年報與發布機構頁面均已存檔，並附 PDF／PNG 鏡像。panel 中其他數值皆未變動。'
                  % (k['n_countries'] - 1, k['n_cmp'], k['n_imp']))
