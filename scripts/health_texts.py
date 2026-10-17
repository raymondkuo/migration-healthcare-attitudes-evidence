# -*- coding: utf-8 -*-
"""English and Traditional Chinese text for the health-expenditure variable added on 2026-10-17.

One place for the wording, so the codebook, known issues, data-quality table, methods page and
revision history say the same thing. Counts are computed from the files, never typed in.
"""
import os

import pandas as pd

VAR = 'health_expenditure_pct_gdp'
WHEN = '2026-10-17'
_D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')


def counts():
    """Numbers quoted in the texts, read from the panel and the World Bank / WHO comparison."""
    p = pd.read_csv(os.path.join(_D, 'panel_final.csv'), usecols=['iso3', 'year', VAR, VAR + '_flag'])
    cmp_ = pd.read_csv(os.path.join(_D, 'health_expenditure_wb_vs_who.csv'))
    v = p[VAR].dropna()
    return dict(n=int(len(v)), n_countries=int(p[p[VAR].notna()].iso3.nunique()),
                y0=int(p[p[VAR].notna()].year.min()), y1=int(p[p[VAR].notna()].year.max()),
                n_wb=int((p[p[VAR].notna()].iso3 != 'TWN').sum()),
                n_cmp=int(len(cmp_)), n_same=int((cmp_.identical == 'yes').sum()),
                n_tw=int((p[p[VAR].notna()].iso3 == 'TWN').sum()),
                lo=float(v.min()), hi=float(v.max()))


COMPARABILITY_EN = {
    VAR: 'Comparable across countries by design: one concept (current health expenditure under the System of '
         'Health Accounts) and, for 39 countries, one source (WHO GHED via the World Bank). Taiwan comes from its '
         'own national health accounts on the same concept, and includes long-term care only from 2007. A share '
         'of GDP, so it moves with GDP as well as with spending.',
}
COMPARABILITY_ZH = {
    VAR: '設計上可跨國比較：概念一致（醫療健康帳 SHA 之經常性醫療保健支出），39 國來源一致（世界衛生組織 GHED，經世界銀行發布）。'
         '臺灣取自本國之醫療健康帳，概念相同，惟自 2007 年起始納入長期照顧服務。此為占 GDP 之比率，'
         '故除支出外亦隨 GDP 變動。',
}


def codebook_rows():
    """(name, definition, caution, definition_zh, caution_zh) rows for data/codebook.csv."""
    k = counts()
    return [
        (VAR,
         'Current health expenditure (CHE) as a percentage of GDP, 0-100 (8.5 means 8.5%% of GDP): spending on health '
         'care goods and services consumed during the year, without capital spending such as buildings, machinery '
         'and IT (World Bank definition of SH.XPD.CHEX.GD.ZS). %d countries: WHO Global Health Expenditure '
         'Database as published by the World Bank (WDI SH.XPD.CHEX.GD.ZS); Taiwan, which WHO and the World Bank do '
         'not cover: Ministry of Health and Welfare, National Health Expenditure 2024, Table 1 '
         '(CHE占GDP比重). Added %s for every country and year of the panel (%d-%d).'
         % (k['n_countries'] - 1, WHEN, k['y0'], k['y1']),
         'Verified: all %d World Bank values are identical to full precision to WHO\'s own GHO API '
         '(data/health_expenditure_wb_vs_who.csv); the %d Taiwan values read from the official MOHW workbook are '
         'identical to the published report and recompute from its CHE and GDP columns. WHO revises past years '
         'when it updates the database, and MOHW revises with the national accounts: the values are those '
         'published on the retrieval date. Taiwan includes long-term care services only from 2007 (flagged).'
         % (k['n_wb'], k['n_tw']),
         '經常性醫療保健支出（CHE）占國內生產毛額（GDP）之百分比，0–100（8.5 即 GDP 之 8.5%%）：當年消費之醫療保健財貨與服務支出，'
         '不含建物、設備與資訊系統等資本支出（世界銀行 SH.XPD.CHEX.GD.ZS 之定義）。%d 國：世界衛生組織全球醫療支出資料庫（GHED），'
         '經世界銀行發布（WDI SH.XPD.CHEX.GD.ZS）；世界衛生組織與世界銀行未涵蓋之臺灣：衛生福利部《113年國民醫療保健支出》表1'
         '（CHE占GDP比重）。於 %s 新增，涵蓋 panel 之全部國家與年度（%d–%d）。'
         % (k['n_countries'] - 1, WHEN, k['y0'], k['y1']),
         '已查證：%d 筆世界銀行數值與世界衛生組織 GHO API 之數值完全相同（data/health_expenditure_wb_vs_who.csv）；'
         '臺灣 %d 筆數值讀自衛生福利部官方試算表，與出版之報告相同，且可由其 CHE 與 GDP 欄重新算得。'
         '世界衛生組織更新資料庫時會修訂過去年度，衛生福利部亦隨國民所得統計修正：數值為擷取當日所公布者。'
         '臺灣自 2007 年起始納入長期照顧服務（已標示旗標）。' % (k['n_wb'], k['n_tw'])),
    ]


SOURCE_TYPE_EN = (' health_expenditure_pct_gdp: annual for every value.')
SOURCE_TYPE_ZH = ('health_expenditure_pct_gdp：每一筆皆為 annual。')
FLAG_EN = (' health_expenditure_pct_gdp: Taiwan only, narrower scope: excludes long-term care services '
           '(included from 2007) for 2001-2006 and break in time series: long-term care services included from '
           '2007 for 2007.')
FLAG_ZH = ('醫療保健支出：僅臺灣，2001–2006 年為 narrower scope（不含長期照顧服務，自 2007 年起納入），'
           '2007 年為 break in time series（自 2007 年起納入長期照顧服務）。')
COLLECTED_EN = ' health_expenditure_pct_gdp was collected on %s for every value.' % WHEN
COLLECTED_ZH = 'health_expenditure_pct_gdp 之每一筆數值均於 %s 蒐集。' % WHEN


def known_issue():
    k = counts()
    return dict(
        severity='LOW', scope='Taiwan', variable=VAR,
        issue='Taiwan is not in the WHO Global Health Expenditure Database or the World Bank indicator, so its '
              'health expenditure comes from the Ministry of Health and Welfare\'s national health accounts. The '
              'concept is the same (current health expenditure under the System of Health Accounts, without '
              'capital formation), but the series includes long-term care services only from 2007 (Table 1, '
              'note 4: 民國96年(含)起含長期照顧服務支出; the English version of that note in the report says "Since '
              '1997", which contradicts the Chinese).',
        issue_zh='臺灣不在世界衛生組織全球醫療支出資料庫與世界銀行指標之內，故其醫療保健支出取自衛生福利部之國民醫療保健支出統計。'
                 '概念相同（醫療健康帳 SHA 之經常性醫療保健支出，不含資本形成），但自 2007 年起始納入長期照顧服務'
                 '（表1 附註4：民國96年(含)起含長期照顧服務支出；報告英文版之附註寫作「Since 1997」，與中文不符）。',
        evidence='evidence/countries/TWN/: the official workbook (113年NHE統計表.xlsx, sheet 表1), the report '
                 '(PDF page 18 = Table 1; page 9 states that NHE follows the SHA definitions of the OECD, Eurostat '
                 'and WHO) and the MOHW statistics page linking both. The %d values are identical in the workbook '
                 'and the report.' % k['n_tw'],
        evidence_zh='evidence/countries/TWN/：官方試算表（113年NHE統計表.xlsx，表1 工作表）、報告（PDF 第 18 頁為表1；'
                    '第 9 頁說明 NHE 依 OECD、Eurostat 與 WHO 之醫療健康帳 SHA 定義計算），以及連結兩者之衛生福利部統計處頁面。'
                    '%d 筆數值於試算表與報告中完全相同。' % k['n_tw'],
        action='Used as published. 2001-2006 are flagged "narrower scope" and 2007 "break in time series"; for a trend '
               'across 2007, or a comparison with countries whose long-term care is included throughout, start '
               'Taiwan in 2007.',
        action_zh='依公布數值使用。2001–2006 年標示「narrower scope」，2007 年標示「break in time series」；'
                  '若趨勢須跨越 2007 年，或須與全期均含長期照顧之國家比較，臺灣請自 2007 年起算。')


def verdict():
    """The one-line verdict in the methods page's table of variables."""
    return {
        'en': 'Strong. One concept for every country and one source for 39 (WHO GHED via the World Bank, checked '
              'against WHO); Taiwan from its national health accounts, long-term care included from 2007.',
        'zh': '強。各國概念一致，39 國來源一致（世界衛生組織 GHED，經世界銀行發布，並已與世界衛生組織核對）；'
              '臺灣取自本國醫療健康帳，自 2007 年起含長期照顧。',
    }


def revision():
    k = counts()
    return dict(
        scope='New variable %s: current health expenditure as %% of GDP, all %d countries, %d-%d'
              % (VAR, k['n_countries'], k['y0'], k['y1']),
        scope_zh='新增變項 %s：經常性醫療保健支出占 GDP 比率，全部 %d 國，%d–%d' % (VAR, k['n_countries'], k['y0'], k['y1']),
        before='No health-expenditure variable.',
        before_zh='無醫療保健支出變項。',
        after='%d values (%d countries x %d years), range %.2f%% to %.2f%% of GDP; ten columns '
              'health_expenditure_pct_gdp[_source, _url, _ref_date, _note, _grade, _verification, _source_type, '
              '_flag, _collected_on] appended to the panel.'
              % (k['n'], k['n_countries'], k['y1'] - k['y0'] + 1, k['lo'], k['hi']),
        after_zh='%d 筆數值（%d 國 × %d 年），介於 GDP 之 %.2f%% 至 %.2f%%；panel 末尾新增 health_expenditure_pct_gdp'
                 '[_source、_url、_ref_date、_note、_grade、_verification、_source_type、_flag、_collected_on] 共十欄。'
                 % (k['n'], k['n_countries'], k['y1'] - k['y0'] + 1, k['lo'], k['hi']),
        change='Added at the authors\' request, for the same countries and years as the population and migrant '
               'series. %d countries from the World Bank (WDI SH.XPD.CHEX.GD.ZS, the WHO Global Health Expenditure '
               'Database): all %d values identical to full precision to WHO\'s own GHO API. Taiwan from the Ministry '
               'of Health and Welfare (National Health Expenditure 2024, Table 1), read from the official workbook, '
               'identical to the published report; long-term care is included from 2007 and the earlier years are '
               'flagged. Raw responses, the workbook, the report and the publishers\' pages are archived with PDF/PNG '
               'mirrors. No other value in the panel changed.'
               % (k['n_countries'] - 1, k['n_cmp']),
        change_zh='應作者要求新增，國家與年度與人口及移民序列一致。%d 國取自世界銀行（WDI SH.XPD.CHEX.GD.ZS，即世界衛生組織全球醫療支出資料庫）：'
                  '%d 筆數值與世界衛生組織 GHO API 完全相同。臺灣取自衛生福利部《113年國民醫療保健支出》表1，讀自官方試算表，'
                  '與出版之報告相同；自 2007 年起始含長期照顧，較早年度已標示旗標。API 原始回應、試算表、報告與發布機構頁面均已存檔，'
                  '並附 PDF／PNG 鏡像。panel 中其他數值皆未變動。' % (k['n_countries'] - 1, k['n_cmp']))
