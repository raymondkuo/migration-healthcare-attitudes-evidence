# -*- coding: utf-8 -*-
"""English and Traditional Chinese text for the V-Dem liberal democracy index added on 2026-10-26.

One place for the wording, so the codebook, known issues, data-quality table, methods page and
revision history say the same thing. Counts are computed from the files, never typed in.
"""
import os

import pandas as pd

VAR = 'vdem_libdem'
WHEN = '2026-10-26'
VERSION = 'v16'
RELEASED = '2026-03-17'                  # the vdemdata 16.0 release commit (V-Dem dates v16 "March 2026")
COMMIT = 'f4dd26922e658442524dfd954bf14f7ebe622d5d'
DOI = 'https://doi.org/10.23696/vdemds26'
SOURCE_TYPE = 'expert_index'
_D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
CMP = os.path.join(_D, 'vdem_source_comparison.csv')


def counts():
    """Numbers quoted in the texts, read from the panel and the source comparison."""
    p = pd.read_csv(os.path.join(_D, 'panel_final.csv'), usecols=['iso3', 'country', 'year', VAR])
    c = pd.read_csv(CMP, dtype=str)
    v = p[VAR].dropna()
    w = c.v2x_libdem_codehigh.astype(float) - c.v2x_libdem_codelow.astype(float)
    return dict(n=int(len(v)), n_countries=int(p[p[VAR].notna()].iso3.nunique()),
                y0=int(p[p[VAR].notna()].year.min()), y1=int(p[p[VAR].notna()].year.max()),
                n_cmp=int(len(c)), n_agree=int((c.owid_same == 'yes').sum()),
                lo=float(v.min()), hi=float(v.max()),
                w_mean=float(w.mean()), w_max=float(w.max()))


COMPARABILITY_EN = {
    VAR: 'Comparable across countries and years by design: one source and one definition for every country (V-Dem '
         'v16), estimated by one measurement model that puts all countries and years on a common scale. Each value is '
         'an estimate from expert ratings with a published uncertainty interval; small differences between countries '
         'or years can lie inside it.',
}
COMPARABILITY_ZH = {
    VAR: '設計上可跨國、跨年比較：各國來源與定義一致（V-Dem v16），並由同一測量模型將所有國家與年度置於共同尺度。'
         '每一數值皆為依專家評分所得之估計值，並附公布之不確定區間；國家或年度間之微小差異可能落在區間之內。',
}


def codebook_rows():
    """(name, definition, caution, definition_zh, caution_zh) rows for data/codebook.csv."""
    k = counts()
    return [
        (VAR,
         'V-Dem liberal democracy index (v2x_libdem): "To what extent is the ideal of liberal democracy achieved?", '
         'interval scale from 0 (low) to 1 (high). It combines the electoral democracy index (v2x_polyarchy) with the '
         'liberal component index (v2x_liberal: civil liberties, rule of law, judicial and legislative constraints on '
         'the executive). Annual value = day-weighted mean over the calendar year. Source: V-Dem Country-Year Dataset '
         '%s (%s), read from the V-Dem Institute\'s own data file (R package vdemdata 16.0, released %s), three '
         'decimals. Added %s for all %d countries and every year of the panel (%d-%d).'
         % (VERSION, DOI, RELEASED, WHEN, k['n_countries'], k['y0'], k['y1']),
         'Verified: all %d values are identical at three decimals to Our World in Data\'s copy of V-Dem %s '
         '(data/vdem_source_comparison.csv). Each value is an estimate from V-Dem\'s Bayesian measurement model of '
         'expert ratings; V-Dem publishes a 68%% interval for it (v2x_libdem_codelow/codehigh, in the comparison file; '
         'mean width %.3f). V-Dem re-estimates every past year with each annual release, so values from another '
         'version can differ: cite %s.' % (k['n_cmp'], VERSION, k['w_mean'], VERSION),
         'V-Dem 自由民主指數（v2x_libdem）：「自由民主之理想實現至何種程度？」，區間尺度，0（低）至 1（高）。結合選舉民主指數'
         '（v2x_polyarchy）與自由主義成分指數（v2x_liberal：公民自由、法治、司法與立法對行政之制衡）。年度數值為該曆年之'
         '按日加權平均。來源：V-Dem Country-Year Dataset %s（%s），讀自 V-Dem 研究所自身之資料檔（R 套件 vdemdata 16.0，'
         '%s 發布），小數三位。於 %s 新增，涵蓋全部 %d 國與 panel 之每一年度（%d–%d）。'
         % (VERSION, DOI, RELEASED, WHEN, k['n_countries'], k['y0'], k['y1']),
         '已查證：%d 筆數值與 Our World in Data 轉載之 V-Dem %s 於小數三位完全相同（data/vdem_source_comparison.csv）。'
         '每一數值皆為 V-Dem 以貝氏測量模型彙整專家評分所得之估計值；V-Dem 並公布其 68%% 區間（v2x_libdem_codelow／codehigh，'
         '見比對檔；平均寬度 %.3f）。V-Dem 每年改版時會重新估計所有過去年度，其他版本之數值可能不同：引用時請註明 %s。'
         % (k['n_cmp'], VERSION, k['w_mean'], VERSION)),
    ]


SOURCE_TYPE_EN = (' vdem_libdem: expert_index (an index estimated by V-Dem\'s measurement model from expert ratings) '
                  'for every value.')
SOURCE_TYPE_ZH = ('vdem_libdem：每一筆數值皆為 expert_index（V-Dem 測量模型依專家評分估計之指數）。')
COLLECTED_EN = ' vdem_libdem was collected on %s for every value.' % WHEN
COLLECTED_ZH = 'vdem_libdem 之每一筆數值均於 %s 蒐集。' % WHEN


def known_issue():
    k = counts()
    return dict(
        severity='LOW', scope='All countries', variable=VAR,
        issue='The V-Dem liberal democracy index is an estimate, not a count: V-Dem\'s measurement model turns the '
              'ratings of several country experts into a score with an uncertainty interval (68%% interval, mean width '
              '%.3f, widest %.3f across the %d values). V-Dem also re-estimates every past year with each annual '
              'release, so a value from another version of the dataset can differ from the %s value archived here.'
              % (k['w_mean'], k['w_max'], k['n'], VERSION),
        issue_zh='V-Dem 自由民主指數為估計值而非計數：V-Dem 之測量模型將多位國家專家之評分轉為附不確定區間之分數'
                 '（68%% 區間，%d 筆數值之平均寬度 %.3f，最寬 %.3f）。V-Dem 每年改版時亦會重新估計所有過去年度，'
                 '故其他版本之數值可能與此處存檔之 %s 數值不同。' % (k['n'], k['w_mean'], k['w_max'], VERSION),
        evidence='evidence/api/: the V-Dem %s data file (vdem.RData of the V-Dem Institute\'s R package vdemdata 16.0) '
                 'with a PDF/PNG grid of the values, its codebook entry, the V-Dem Codebook %s (pages on the index, the '
                 'intervals and the annual aggregation) and Our World in Data\'s copy; data/vdem_source_comparison.csv '
                 'lists value, interval and standard deviation cell by cell.' % (VERSION, VERSION),
        evidence_zh='evidence/api/：V-Dem %s 資料檔（V-Dem 研究所 R 套件 vdemdata 16.0 之 vdem.RData）及其數值之 PDF／PNG 表格、'
                    '其編碼簿條目、《V-Dem Codebook %s》（指數、區間與年度彙整之頁面），以及 Our World in Data 之轉載；'
                    'data/vdem_source_comparison.csv 逐格列出數值、區間與標準差。' % (VERSION, VERSION),
        action='Used as published in %s, graded A (read from V-Dem\'s machine-readable file). Cite the version; '
               'before reading a small difference between countries or years as real, check the intervals in '
               'data/vdem_source_comparison.csv.' % VERSION,
        action_zh='依 %s 公布之數值使用，評為 A 級（讀自 V-Dem 之機器可讀檔案）。引用時請註明版本；將國家或年度間之微小差異'
                  '視為實質差異前，請先查閱 data/vdem_source_comparison.csv 之區間。' % VERSION)


def verdict():
    """The one-line verdict in the methods page's table of variables."""
    k = counts()
    return {
        'en': 'Strong. One source and one definition for all %d countries (V-Dem %s), read from V-Dem\'s own data file '
              'and identical to Our World in Data\'s copy. An expert-based estimate with a published uncertainty '
              'interval; V-Dem revises past years with each release.' % (k['n_countries'], VERSION),
        'zh': '強。全部 %d 國來源與定義一致（V-Dem %s），讀自 V-Dem 自身之資料檔，並與 Our World in Data 之轉載完全相同。'
              '為依專家評分所得之估計值，附公布之不確定區間；V-Dem 每次改版會修訂過去年度。' % (k['n_countries'], VERSION),
    }


def revision():
    k = counts()
    return dict(
        scope='New variable %s: V-Dem liberal democracy index (0-1), all %d countries, %d-%d'
              % (VAR, k['n_countries'], k['y0'], k['y1']),
        scope_zh='新增變項 %s：V-Dem 自由民主指數（0–1），全部 %d 國，%d–%d' % (VAR, k['n_countries'], k['y0'], k['y1']),
        before='No democracy variable.',
        before_zh='無民主程度變項。',
        after='%d values (%d countries x %d years), range %.3f to %.3f; ten columns vdem_libdem[_source, _url, '
              '_ref_date, _note, _grade, _verification, _source_type, _flag, _collected_on] appended to the panel.'
              % (k['n'], k['n_countries'], k['y1'] - k['y0'] + 1, k['lo'], k['hi']),
        after_zh='%d 筆數值（%d 國 × %d 年），介於 %.3f 至 %.3f；panel 末尾新增 vdem_libdem[_source、_url、_ref_date、_note、'
                 '_grade、_verification、_source_type、_flag、_collected_on] 共十欄。'
                 % (k['n'], k['n_countries'], k['y1'] - k['y0'] + 1, k['lo'], k['hi']),
        change='Added at the authors\' request, for the same countries and years as the population and migrant series. '
               'Read from the V-Dem Country-Year Dataset %s, the V-Dem Institute\'s own data file (R package vdemdata '
               '16.0, released %s; the file\'s hash matches the one GitHub records for it); all %d values are '
               'identical at three decimals to Our World in Data\'s copy. The data file, its codebook entry, the V-Dem '
               'Codebook, Our World in Data\'s copy and the publishers\' pages are archived with PDF/PNG mirrors. No '
               'other value in the panel changed.' % (VERSION, RELEASED, k['n_cmp']),
        change_zh='應作者要求新增，國家與年度與人口及移民序列一致。讀自 V-Dem Country-Year Dataset %s，即 V-Dem 研究所自身之資料檔'
                  '（R 套件 vdemdata 16.0，%s 發布；檔案雜湊值與 GitHub 所記錄者相同）；%d 筆數值與 Our World in Data '
                  '之轉載於小數三位完全相同。資料檔、其編碼簿條目、《V-Dem Codebook》、Our World in Data 之轉載與發布機構頁面'
                  '均已存檔，並附 PDF／PNG 鏡像。panel 中其他數值皆未變動。' % (VERSION, RELEASED, k['n_cmp']))
