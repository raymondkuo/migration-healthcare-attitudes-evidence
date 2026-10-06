# -*- coding: utf-8 -*-
"""Regenerate every table derived from the panel after the 2001-2009 extension:

  source_register.csv        one row per source of the new cells (old rows untouched)
  evidence/countries/*/source_manifest.csv   rebuilt from the register
  evidence/countries/*/README.md             a dated "extension" section appended
  data_quality.csv           coverage out of 22 years, sources, usability for a trend
  evidence_index.csv         one line per country x variable series
  known_issues.csv           new rows and one amended row, English and Chinese
  codebook.csv               new rows, English and Chinese, and the year range corrected

The early build scripts that first produced several of these cannot be re-run safely (they
would undo later corrections), so the logic is reproduced here. Idempotent: rows this script
added are replaced, not duplicated.
"""
import os
import re
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ext_lib as L                                    # noqa: E402
import blib                                            # noqa: E402

SITE = os.path.dirname(HERE)
D = os.path.join(SITE, 'data')
EVC = os.path.join(SITE, 'evidence', 'countries')
STAGE = os.path.join(D, 'extension_staging')
C = L.COLLECTED

panel = pd.read_csv(os.path.join(D, 'panel_final.csv'))
won = pd.read_csv(os.path.join(STAGE, 'assembled_winners.txt'))
splice = pd.read_csv(os.path.join(D, 'extension_splice_summary.csv'))
VARS = ['population', 'foreign_born', 'foreign_nationals', 'irregular_stock',
        'irregular_proxy_overstayers', 'irregular_proxy_detections']

# ------------------------------------------------------------------ 0. snapshot rows must point at files that exist
ws = pd.read_csv(os.path.join(D, 'web_snapshots.csv')).fillna('')


def _files_exist(r):
    folder = os.path.join(EVC, r['iso3'])
    return all(not r[c] or os.path.exists(os.path.join(folder, r[c]))
               for c in ('pdf_mirror', 'png_screenshot'))


gone = ws[~ws.apply(_files_exist, axis=1)]
if len(gone):
    ws[ws.apply(_files_exist, axis=1)].to_csv(os.path.join(D, 'web_snapshots.csv'), index=False,
                                              encoding='utf-8-sig')
print('web_snapshots.csv: %d rows (%d pointing at missing files were dropped)'
      % (len(ws) - len(gone), len(gone)))

# ------------------------------------------------------------------ 1. source register
reg = pd.read_csv(os.path.join(D, 'source_register.csv')).fillna('')
reg = reg[reg.from_workbook != 'EXTENSION']
out = []
for (iso, var, url, name, lf), g in won.groupby(['iso3', 'variable', 'source_url', 'source_name',
                                                  'local_file'], dropna=False):
    api = str(lf).startswith('evidence/api/')
    ys = sorted(g.year)
    if api:
        note = ('Read directly from the live source on %s; the raw response is archived at %s. '
                'The values already published for 2010-2022 reproduce exactly from the same '
                'response.' % (C, lf))
    else:
        n0 = str(g.note.iloc[0])
        note = (n0[:230] + '...') if len(n0) > 230 else n0
    out.append(dict(iso3=iso, variable=var, years='%d-%d' % (ys[0], ys[-1]), n_obs=len(ys),
                    from_workbook='EXTENSION', source_name=name, source_url=url,
                    retrieval='VERIFIED_API' if api else 'ARCHIVED', local_file=lf, note=note,
                    outcome='VERIFIED_API' if api else 'DOWNLOADED',
                    superseded_source_name='', superseded_source_url=''))
reg = pd.concat([reg, pd.DataFrame(out)], ignore_index=True)
reg = reg.sort_values(['iso3', 'variable', 'years']).reset_index(drop=True)
reg.to_csv(os.path.join(D, 'source_register.csv'), index=False, encoding='utf-8-sig')
print('source_register.csv: %d rows (%d from the extension)' % (len(reg), len(out)))

# ------------------------------------------------------------------ 2. per-country manifests
MCOLS = ['iso3', 'variable', 'years', 'n_obs', 'workbook', 'source_name', 'source_url',
         'retrieval_status', 'local_file', 'note', 'superseded_source_name',
         'superseded_source_url']
for iso in sorted(reg.iso3.unique()):
    sub = reg[reg.iso3 == iso].copy()
    sub = sub.rename(columns={'from_workbook': 'workbook', 'retrieval': 'retrieval_status'})
    sub['local_file'] = sub.local_file.map(
        lambda x: '(see ../../data_raw/)' if x == 'data_raw/' else x)
    f = os.path.join(EVC, iso, 'source_manifest.csv')
    if os.path.isdir(os.path.join(EVC, iso)):
        sub[MCOLS].to_csv(f, index=False, encoding='utf-8-sig')

# ------------------------------------------------------------------ 3. country README sections
BEGIN, END = '<!-- extension-2001:begin -->', '<!-- extension-2001:end -->'
for iso in sorted(won.iso3.unique()):
    rd = os.path.join(EVC, iso, 'README.md')
    if not os.path.exists(rd):
        continue
    txt = open(rd, encoding='utf-8').read()
    txt = re.sub(re.escape(BEGIN) + r'.*?' + re.escape(END) + r'\s*', '', txt, flags=re.S)
    g = won[won.iso3 == iso]
    lines = [BEGIN, '', '## Extension to 2001 (collected %s)' % C, '',
             'Values for 2001-2009 (and any blank cell inside 2010-2022 that the new sources '
             'filled) were collected on %s. No value published earlier was changed.' % C, '',
             '| variable | years | source | file |', '|---|---|---|---|']
    for (var, name, lf), gg in g.groupby(['variable', 'source_name', 'local_file']):
        ys = sorted(gg.year)
        lines.append('| %s | %s | %s | `%s` |' % (var, '%d-%d (%d)' % (ys[0], ys[-1], len(ys)),
                                                 str(name).replace('|', '/')[:110],
                                                 os.path.basename(str(lf))))
    lines += ['', 'Each cell carries its own note, source type and flag in `data/panel_final.csv`; '
              'the revision history on the Verification page dates the change.', '', END, '']
    open(rd, 'w', encoding='utf-8', newline='\n').write(txt.rstrip('\n') + '\n\n' + '\n'.join(lines))
print('country READMEs and manifests updated: %d countries' % won.iso3.nunique())

# ------------------------------------------------------------------ 4. data_quality
old_q = pd.read_csv(os.path.join(D, 'data_quality.csv'))
COMP = old_q.drop_duplicates('variable').set_index('variable').comparability.to_dict()
NY = panel.year.nunique()
rows = []
for iso, g in panel.groupby('iso3', sort=False):
    cname = g.country.iloc[0]
    for v in VARS:
        s = g[g[v].notna()]
        if not len(s):
            rows.append(dict(iso3=iso, country=cname, variable=v, n_years=0, coverage='0/%d' % NY,
                             years='', modal_grade='', sources='', usable_for_trend='NO - no data',
                             comparability=COMP[v]))
            continue
        gr = s[v + '_grade'].mode()
        srcs = sorted({str(x)[:60] for x in s[v + '_source'].dropna()})
        yrs = sorted(s['year'].tolist())
        gaps = len(yrs) < (max(yrs) - min(yrs) + 1)
        multi = len(srcs) > 1
        if len(yrs) >= 10 and not multi:
            use = 'YES - continuous single-source series'
        elif len(yrs) >= 10 and multi:
            use = 'CAUTION - 10+ years but more than one source in the series'
        elif len(yrs) >= 5:
            use = 'CAUTION - partial coverage%s' % (', with gaps' if gaps else '')
        else:
            use = 'NO - too few years for a trend (use as a level only)'
        rows.append(dict(iso3=iso, country=cname, variable=v, n_years=len(yrs),
                         coverage='%d/%d' % (len(yrs), NY), years='%d-%d' % (min(yrs), max(yrs)),
                         modal_grade=gr.iloc[0] if len(gr) else '', sources=' | '.join(srcs),
                         usable_for_trend=use, comparability=COMP[v]))
qual = pd.DataFrame(rows)
qual.to_csv(os.path.join(D, 'data_quality.csv'), index=False, encoding='utf-8-sig')
print('data_quality.csv: %d rows | usable_for_trend: %s'
      % (len(qual), qual.usable_for_trend.value_counts().to_dict()))

# ------------------------------------------------------------------ 5. evidence_index
idx = []
for iso, g in panel.groupby('iso3', sort=False):
    for v in blib.ALLVARS:
        if v not in g.columns or g[v].notna().sum() == 0:
            continue
        s = g[g[v].notna()]
        urls = sorted({str(u) for u in s[v + '_url'].dropna()}) if (v + '_url') in s else []
        seen = set()
        for u in urls:
            for _, rr in reg[(reg.iso3 == iso) & (reg.source_url == u)].iterrows() if len(urls) else []:
                for lab, rel in blib.artifacts(iso, u, rr.get('local_file'), 'en'):
                    seen.add(rel)
            for lab, rel in blib.artifacts(iso, u, None, 'en'):
                seen.add(rel)
        idx.append(dict(iso3=iso, country=g.country.iloc[0], variable=v, n_values=int(len(s)),
                        years='%d-%d' % (s.year.min(), s.year.max()),
                        evidence_page='evidence-pages/%s__%s.html' % (iso, v),
                        pdf_extract='evidence/extracts/%s/%s.pdf' % (iso, v), artifacts=len(seen)))
pd.DataFrame(idx).to_csv(os.path.join(D, 'evidence_index.csv'), index=False, encoding='utf-8-sig')
print('evidence_index.csv: %d series' % len(idx))

# ------------------------------------------------------------------ 6. known issues
ki = pd.read_csv(os.path.join(D, 'known_issues.csv')).fillna('')
n_sp = len(splice)
n_fb = int((splice.variable == 'foreign_born').sum())
n_fn = int((splice.variable == 'foreign_nationals').sum())
n_cells = int(splice.cells.sum())
med = float(splice.mean_gap_pct.abs().median())
big = splice[splice.mean_gap_pct.abs() >= 5]
n_big, n_big_cells = len(big), int(big.cells.sum())

NEW = [
 dict(severity='MEDIUM', scope='Spliced series (OECD values extend a Eurostat series)',
      variable='foreign_born / foreign_nationals',
      issue='For %d country-series (%d foreign-born, %d foreign-national) the 2001-2009 values come '
            'from OECD while the 2010-2022 values published earlier come from Eurostat, because '
            'Eurostat\'s tables start later. The two sources do not count exactly the same thing: '
            'where both exist, the median difference between the series is %.1f%%, and %d of the %d '
            'differ by 5%% or more (next row).' % (n_sp, n_fb, n_fn, med, n_big, n_sp),
      issue_zh='有 %d 組國家序列（外國出生 %d 組、外國籍 %d 組）之 2001–2009 年數值取自 OECD，'
               '而先前發布之 2010–2022 年數值取自 Eurostat，原因是 Eurostat 之表格起始較晚。'
               '兩個來源所計並不完全相同：兩者並存之年度，序列間差異之中位數為 %.1f%%，'
               '其中 %d 組差異達 5%% 以上（見下一列）。' % (n_sp, n_fb, n_fn, med, n_big),
      evidence='data/extension_splice_summary.csv lists, for every spliced series, the years of '
               'overlap and the mean, minimum and maximum difference; data/migrant_stock_alternatives.csv '
               'holds the OECD values for every year so that a single-source series can be built.',
      evidence_zh='data/extension_splice_summary.csv 列出每一組接續序列之重疊年數與差異之平均、最小及最大值；'
                  'data/migrant_stock_alternatives.csv 保留 OECD 全部年度之數值，以便建立單一來源之序列。',
      action='Every spliced cell is flagged "splice" and its note states the measured gap. Nothing was '
             'rescaled or adjusted. For a trend that must not contain a source change, use the OECD '
             'values in migrant_stock_alternatives.csv for 2001-2022, or start the series in 2010.',
      action_zh='每一筆接續之數值均標示為「splice」，備註載明實測之差距，且未作任何縮放或調整。'
                '若趨勢分析不容許來源變動，請改用 migrant_stock_alternatives.csv 中 OECD '
                '2001–2022 年之數值，或自 2010 年起算。'),
 dict(severity='MEDIUM', scope='Denmark, Slovakia, Czechia, Lithuania, Poland, Portugal',
      variable='foreign_born / foreign_nationals',
      issue='%d spliced series differ from the series they were joined to by 5%% or more: Denmark '
            'foreign-born %.1f%% (every year between %.0f%% and %.0f%%), Slovakia %+.1f%%, Czechia '
            '%+.1f%%, Lithuania %+.1f%%, Portugal foreign-nationals %+.1f%%, and Poland and Portugal '
            'foreign-born on one or two overlapping years only.'
            % (n_big, big[(big.iso3 == 'DNK')].mean_gap_pct.iloc[0],
               abs(big[(big.iso3 == 'DNK')].max_gap_pct.iloc[0]),
               abs(big[(big.iso3 == 'DNK')].min_gap_pct.iloc[0]),
               big[(big.iso3 == 'SVK')].mean_gap_pct.iloc[0],
               big[(big.iso3 == 'CZE')].mean_gap_pct.iloc[0],
               big[(big.iso3 == 'LTU')].mean_gap_pct.iloc[0],
               big[(big.iso3 == 'PRT') & (big.variable == 'foreign_nationals')].mean_gap_pct.iloc[0]),
      issue_zh='有 %d 組接續序列與其所銜接之序列相差 5%% 以上：丹麥外國出生 %.1f%%（各年介於 %.0f%% 至 %.0f%%）、'
               '斯洛伐克 %+.1f%%、捷克 %+.1f%%、立陶宛 %+.1f%%、葡萄牙外國籍 %+.1f%%，'
               '另有波蘭與葡萄牙之外國出生序列僅憑一至兩個重疊年度。'
               % (n_big, big[(big.iso3 == 'DNK')].mean_gap_pct.iloc[0],
                  abs(big[(big.iso3 == 'DNK')].max_gap_pct.iloc[0]),
                  abs(big[(big.iso3 == 'DNK')].min_gap_pct.iloc[0]),
                  big[(big.iso3 == 'SVK')].mean_gap_pct.iloc[0],
                  big[(big.iso3 == 'CZE')].mean_gap_pct.iloc[0],
                  big[(big.iso3 == 'LTU')].mean_gap_pct.iloc[0],
                  big[(big.iso3 == 'PRT') & (big.variable == 'foreign_nationals')].mean_gap_pct.iloc[0]),
      evidence='Measured over the years where both sources publish a value for the country '
               '(data/extension_splice_summary.csv). The Danish gap is systematic, so it is a '
               'difference in what the two sources count, not noise.',
      evidence_zh='差距係以兩個來源均有發布該國數值之年度計算（data/extension_splice_summary.csv）。'
                  '丹麥之差距具系統性，反映兩個來源所計內容之不同，並非隨機誤差。',
      action='The %d affected cells are flagged "splice (large gap)". A step of this size at the join '
             'is a source effect, not a change in migration; do not difference across it. The OECD '
             'series for all years is in migrant_stock_alternatives.csv.' % n_big_cells,
      action_zh='受影響之 %d 筆數值標示為「splice (large gap)」。接合處如此幅度之變動屬來源效應，'
                '並非移民之實際變化，請勿跨越該處計算差分。OECD 全部年度之序列見 '
                'migrant_stock_alternatives.csv。' % n_big_cells),
 dict(severity='MEDIUM', scope='China, India, Philippines, Suriname, Thailand',
      variable='foreign_born',
      issue='UN DESA\'s own file declares the migrant stock of these countries (and of Japan and '
            'Taiwan) to be based on foreign citizens (data type C), yet the panel carries them in '
            'foreign_born for 2010, 2015 and 2020, and the extension adds a 2005 value in the same '
            'column. For India the numbers look like place-of-birth counts (5.6 million for 2010 '
            'against 5.49 million in the 2011 census cell), so the declaration may not describe what '
            'was counted.',
      issue_zh='聯合國經社部（UN DESA）自身之檔案將這些國家（以及日本與臺灣）之移民存量宣告為以外國公民'
               '為基礎（資料類型 C），但本 panel 於 2010、2015、2020 年將其列於 foreign_born，'
               '本次延伸亦於同一欄位加入 2005 年數值。以印度而言，數值近似依出生地計算之人數'
               '（2010 年 560 萬，對照 2011 年普查格之 549 萬），故該宣告未必反映實際之計算方式。',
      evidence='evidence/api/UN_DESA_IMS2024_stock_by_sex_and_destination.xlsx, Table 1, column '
               '"Data type".',
      evidence_zh='evidence/api/UN_DESA_IMS2024_stock_by_sex_and_destination.xlsx，Table 1，'
                  '「Data type」欄。',
      action='Not moved: the published cells are unchanged and the 2005 value extends the series '
             'consistently. Every UN DESA cell of these countries (2005, 2010, 2015 and 2020) is flagged '
             '"declared citizenship basis". Until the basis '
             'is confirmed with UN DESA, treat these as the UN "international migrant stock", not as '
             'comparable to born-abroad counts.',
      action_zh='未予移動：已發布之數值不變，2005 年數值以一致方式延伸該序列；這些國家取自 UN DESA 之各格（2005、2010、2015、2020 年）'
                '均標示為「declared citizenship basis」。在向 UN DESA 確認其計算基礎之前，請將其視為聯合國之'
                '「國際移民存量」，而非與依出生地計算之人數具可比性。'),
 dict(severity='LOW', scope='Taiwan', variable='foreign_nationals',
      issue='Taiwan\'s foreign residents for 2001-2011 come from the Ministry of the Interior\'s '
            'consolidated table 1996-2022. The input workbook stated that the series on this basis '
            'begins in 2012 and that 2010 and 2011 are not comparable.',
      issue_zh='臺灣 2001–2011 年之外僑居留人數取自內政部統計處 1996–2022 年之彙整表。'
               '原始工作表曾載明，依此基礎之序列自 2012 年起，且 2010、2011 年不具可比性。',
      evidence='The 11 values for 2012-2022 already published reproduce exactly from the same table; '
               'the table shows no break at 2011/2012 (2010: 418,802; 2011: 466,206; 2012: 483,921) '
               'and carries no footnote on a change of definition.',
      evidence_zh='先前已發布之 2012–2022 年 11 筆數值與同一彙整表完全一致；該表於 2011／2012 年間'
                  '未見斷裂（2010 年 418,802；2011 年 466,206；2012 年 483,921），'
                  '亦無關於定義變更之註腳。',
      action='Included, with a comparability caution on every 2001-2011 cell. A change of definition '
             'inside the table cannot be ruled out from the table alone; the 2012-2022 cell notes '
             'record the original statement.',
      action_zh='予以納入，並於 2001–2011 年每一筆數值標示可比性提醒。僅憑該表無法排除表內曾變更定義'
                '之可能；2012–2022 年各筆備註已記錄原始工作表之說明。'),
 dict(severity='MEDIUM', scope='Not collected for 2001-2009',
      variable='foreign_born / foreign_nationals',
      issue='Looked for and not collected: Australia foreign nationals (the ABS pages reachable give '
            'no national citizenship total) and Chile\'s 2002 census foreign-born count (the INE '
            'document retrieved gives only the 1.27% share; the server stopped serving the longer '
            'report). Not attempted, because each would add a single census year to an otherwise '
            'empty series: Germany foreign-born before 2006, the 2001/2002 census counts for '
            'Bulgaria, Croatia, Czechia, Poland, Portugal and Slovakia, and census years for China, '
            'the Philippines, Suriname and Thailand. No comparable source exists for Japan '
            '(foreign-born) or for Israel and New Zealand (foreign nationals).',
      issue_zh='已尋找但未能蒐集者：澳洲外國籍人口（可取得之澳洲統計局頁面不含全國公民身分總數），'
               '以及智利 2002 年普查之外國出生人數（所取得之 INE 文件僅載 1.27%% 之比例，'
               '較長之報告檔案伺服器已停止回應）。未嘗試者，因各僅能為原本空白之序列增加單一普查年度：'
               '德國 2006 年前之外國出生、保加利亞、克羅埃西亞、捷克、波蘭、葡萄牙、斯洛伐克之 2001／2002 年'
               '普查數，以及中國、菲律賓、蘇利南、泰國之普查年度。日本（外國出生）、'
               '以色列與紐西蘭（外國籍）則無可比較之來源。'.replace('%%', '%'),
      evidence='Attempts and their outcomes are recorded in the revision history of 2026-10-07 and '
               'in the per-country evidence folders; years between census rounds do not exist for '
               'these countries in any source found.',
      evidence_zh='嘗試與結果見 2026-10-07 之修訂紀錄與各國證據資料夾；就所尋得之來源而言，'
                  '這些國家於兩次普查之間之年度並無資料。',
      action='Left empty rather than approximated. Coverage by country and variable is in '
             'data_quality.csv and on the Coverage sheet of the analysis extract.',
      action_zh='保留空白而不作近似推估。各國各變項之涵蓋情形見 data_quality.csv 與分析用資料集之 Coverage 工作表。'),
]
# year-on-year changes of 25% or more that involve an added year, so a reader can see where the
# extended series moves abruptly; the archive does not judge which are real
LC = []
for v in ('foreign_born', 'foreign_nationals'):
    for iso, g in panel.sort_values(['iso3', 'year']).groupby('iso3'):
        g = g.set_index('year')
        s = g[v].dropna()
        for y in s.index:
            if y - 1 not in s.index or s[y - 1] <= 0:
                continue
            if not (pd.notna(g.at[y, v + '_collected_on']) or pd.notna(g.at[y - 1, v + '_collected_on'])):
                continue
            ch = (s[y] / s[y - 1] - 1) * 100
            if abs(ch) >= 25:
                LC.append(dict(iso3=iso, country=g.country.iloc[0], variable=v, year=int(y),
                               previous_value=int(s[y - 1]), value=int(s[y]), change_pct=round(ch, 1),
                               previous_source_type=g.at[y - 1, v + '_source_type'],
                               source_type=g.at[y, v + '_source_type'],
                               previous_flag=g.at[y - 1, v + '_flag'], flag=g.at[y, v + '_flag']))
lc = pd.DataFrame(LC).fillna('')
lc.to_csv(os.path.join(D, 'extension_large_changes.csv'), index=False, encoding='utf-8-sig')
print('extension_large_changes.csv: %d rows' % len(lc))
NEW.append(dict(
    severity='LOW', scope='Added years 2001-2010, several countries', variable='foreign_born / foreign_nationals',
    issue='%d year-on-year changes of 25%% or more involve a year added in the extension (for example '
          'Austria 2001-2002 foreign-born, Portugal 2003-2004 and Spain 2002-2003 foreign nationals). '
          'Some may be real movements, such as administrative regularisations or accession effects; '
          'others may be breaks inside the source. The data alone do not say which.' % len(lc),
    issue_zh='延伸之年度中，有 %d 筆相鄰年度間之變動達 25%% 以上（例如奧地利 2001–2002 年外國出生、'
             '葡萄牙 2003–2004 年與西班牙 2002–2003 年外國籍）。其中部分可能為實際之變動，例如行政上之身分'
             '合法化或入盟效應；另有部分可能是來源內部之斷裂。僅憑資料本身無法分辨。' % len(lc),
    evidence='data/extension_large_changes.csv lists each one with the source type and flag on both '
             'sides of the change.',
    evidence_zh='data/extension_large_changes.csv 逐筆列出，並載明變動前後兩端之來源類型與旗標。',
    action='Nothing was adjusted or removed: each value is what its source published. Before using '
           'the added years in a trend, check these rows, and treat a jump that coincides with a '
           'flagged splice as a source effect.',
    action_zh='未作任何調整或刪除：每一筆數值均為來源所發布者。在以延伸之年度建立趨勢之前，請先檢視這些'
              '資料列；與已標示之接續處重合的跳動，應視為來源效應。'))
# the existing row about countries with no foreign-national stock now has one census value
mask = (ki.scope == 'Australia, India, Israel, New Zealand, Russia, South Africa') & \
       (ki.variable == 'foreign_nationals')
assert mask.sum() == 1
ki.loc[mask, 'issue'] = ('These six countries have no annual foreign-national series. They do not '
                         'compile a foreign-population register of the kind Eurostat and the OECD '
                         'collect. Russia has a single census value (2002).')
ki.loc[mask, 'issue_zh'] = ('這六個國家沒有逐年之外國籍人口序列，其並未編製 Eurostat 與 OECD 所蒐集之該類'
                            '外國人口登記統計。俄羅斯僅有單一普查數值（2002 年）。')
# the population row quoted counts for the 2010-2022 panel; restate them for the whole panel
mask = (ki.variable == 'population') & ki.scope.str.startswith('Israel, Bulgaria')
assert mask.sum() == 1
_pp = pd.read_csv(os.path.join(D, 'panel_final.csv'))
_gap = _pp.population_wb_vs_unwpp_pct.dropna()
_g10 = _pp[_pp.year >= 2010].population_wb_vs_unwpp_pct.dropna()
_a, _b = int((_gap.abs() > 1e-9).sum()), int((_gap.abs() > 3).sum())
_a10, _b10 = int((_g10.abs() > 1e-9).sum()), int((_g10.abs() > 3).sum())
ki.loc[mask, 'evidence'] = ('%d of %d country-years differ (2001-2022); %d by more than 3%%. For '
                            '2010-2022 alone: %d of %d, %d by more than 3%%.'
                            % (_a, len(_gap), _b, _a10, len(_g10), _b10))
ki.loc[mask, 'evidence_zh'] = ('%d 個國家—年度中有 %d 個不一致（2001–2022）；其中 %d 個差異超過 3%%。'
                               '僅就 2010–2022：%d 個中有 %d 個不一致，其中 %d 個超過 3%%。'
                               % (len(_gap), _a, _b, len(_g10), _a10, _b10))
for r in NEW:
    ki = ki[~((ki.scope == r['scope']) & (ki.variable == r['variable']))]
ki = pd.concat([ki, pd.DataFrame(NEW)], ignore_index=True)[list(ki.columns)]
ki.to_csv(os.path.join(D, 'known_issues.csv'), index=False, encoding='utf-8-sig')
print('known_issues.csv: %d rows' % len(ki))

# ------------------------------------------------------------------ 7. codebook
cb = pd.read_csv(os.path.join(D, 'codebook.csv')).fillna('')
cols = list(cb.columns)
yr = cb.index[cb[cols[0]] == 'year']
assert len(yr) == 1
cb.loc[yr, cols[1]] = 'Calendar year, 2001-2022.'
cb.loc[yr, 'definition_zh'] = '曆年，2001–2022。'
# the "derived" flag no longer means only "midpoint of a published range"
n_mid = n_sub = 0
for v in ('foreign_born', 'foreign_nationals', 'irregular_stock'):
    if v + '_derived' in panel.columns:
        d = panel[panel[v + '_derived'].astype(str).str.strip() == 'yes']
        rng = d[v + '_published_range'].fillna('').astype(str).str.strip().ne('')
        n_mid += int(rng.sum())
        n_sub += int((~rng).sum())
dr = cb.index[cb[cols[0]] == '*_derived']
assert len(dr) == 1
cb.loc[dr, cols[2]] = ('Marked with ≈ on the website. %d such values: %d are midpoints of '
                       'published ranges and %d are the difference of two published rows (UK '
                       'foreign-born 2004-2005).' % (n_mid + n_sub, n_mid, n_sub))
cb.loc[dr, 'caution_zh'] = ('網站上以 ≈ 標示。共 %d 筆：%d 筆為已公布區間之中點，%d 筆為兩個已公布列之差'
                            '（英國外國出生 2004–2005 年）。' % (n_mid + n_sub, n_mid, n_sub))
# counts the first release typed in (and that later went stale) are recomputed from the panel
def set_caution(name, en, zh):
    i = cb.index[cb[cols[0]] == name]
    assert len(i) == 1, name
    cb.loc[i, cols[2]] = en
    cb.loc[i, 'caution_zh'] = zh


_NC = panel.iso3.nunique()
_late = panel.year >= 2010
_wb = panel.population.notna() & (panel.iso3 != 'TWN')
_n = lambda m: format(int(m.sum()), ',')
set_caution('population',
            'Verified: all %s World Bank values come from the archived live API response; the %s '
            'for 2010-2022 matched on 2026-08-17 and again on 2026-10-07.' % (_n(_wb), _n(_wb & _late)),
            '已查證：%s 筆世界銀行數值皆來自所存檔之線上 API 回應；其中 2010–2022 年之 %s 筆於 2026-08-17 '
            '及 2026-10-07 兩度比對一致。' % (_n(_wb), _n(_wb & _late)))
_wpp = panel.population_un_wpp2024.notna()
set_caution('population_un_wpp2024',
            'Verified: all %s values come from the archived UN WPP 2024 file; the %s for 2010-2022 '
            'matched on 2026-08-17 and again on 2026-10-07.' % (_n(_wpp), _n(_wpp & _late)),
            '已查證：%s 筆數值皆來自所存檔之 UN WPP 2024 檔案；其中 2010–2022 年之 %s 筆於 2026-08-17 '
            '及 2026-10-07 兩度比對一致。' % (_n(_wpp), _n(_wpp & _late)))
_irr = panel[panel.irregular_stock.notna()].iso3.nunique()
_ovs = panel[panel.irregular_proxy_overstayers.notna()].iso3.nunique()
set_caution('irregular_stock',
            'WEAK. %d/%d countries. Methods not comparable across countries. Not extended before 2010.'
            % (_irr, _NC),
            '薄弱。%d／%d 國。各國方法不可比。2010 年以前未延伸。' % (_irr, _NC))
set_caution('irregular_proxy_overstayers',
            'WEAK. %d/%d countries. A register count, not a modelled stock. Not extended before 2010.'
            % (_ovs, _NC),
            '薄弱。%d／%d 國。為登記統計數，並非模型推估之存量。2010 年以前未延伸。' % (_ovs, _NC))

ADD = [
 ('*_source_type', 'Kind of source behind a foreign_born or foreign_nationals value: annual '
  '(official annual series such as Eurostat, OECD, MOI), census, survey (household-survey '
  'estimate), un_estimate (UN DESA model estimate) or other.',
  'Filter on this to keep only annual series.',
  '外國出生或外國籍人口數值所依據之來源類型：annual（Eurostat、OECD、內政部等官方逐年序列）、census（普查）、'
  'survey（家戶調查估計）、un_estimate（UN DESA 模型估計）或 other。',
  '依此欄篩選即可僅保留逐年序列。'),
 ('*_flag', 'Comparability flags on a foreign_born or foreign_nationals value, separated by '
  'semicolons: splice (source differs from the one used for the rest of the series), splice '
  '(large gap) (and the two sources differ by 5% or more where they overlap), un_estimate, declared '
  'citizenship basis, comparability caution, includes former-USSR births, derived by subtraction, '
  'and the publisher\'s own flags (Eurostat: break in time series, estimated, provisional).',
  'Blank means no flag. Attached to every cell, including those published before the '
  'extension (UN DESA estimates and the flags Eurostat itself attached). See the cell note and '
  'data/extension_splice_summary.csv.',
  '外國出生或外國籍人口數值之可比性旗標，以分號分隔：splice（來源與序列其餘部分不同）、splice (large gap)'
  '（且兩來源於重疊年度相差 5% 以上）、un_estimate、declared citizenship basis、comparability caution、'
  'includes former-USSR births、derived by subtraction，以及發布機構自身之旗標'
  '（Eurostat：時間序列斷裂、估計值、暫定值）。',
  '空白表示無旗標。適用於每一格，包括延伸前已發布者（UN DESA 估計值與 Eurostat 自身之旗標）。'
  '請參閱各筆備註與 data/extension_splice_summary.csv。'),
 ('*_collected_on', 'Date a value was collected, for values added in the 2001 extension '
  '(2026-10-07); blank for values collected on 2026-08-17.',
  'Present for population, population_un_wpp2024, foreign_born and foreign_nationals.',
  '數值蒐集之日期：2001 年延伸所新增之數值為 2026-10-07；於 2026-08-17 蒐集者則為空白。',
  '適用於 population、population_un_wpp2024、foreign_born 與 foreign_nationals。'),
]
cb = cb[~cb[cols[0]].isin([a[0] for a in ADD])]
add = pd.DataFrame([{cols[0]: a[0], cols[1]: a[1], cols[2]: a[2], 'definition_zh': a[3],
                     'caution_zh': a[4]} for a in ADD])
cb = pd.concat([cb, add], ignore_index=True)[cols]
cb.to_csv(os.path.join(D, 'codebook.csv'), index=False, encoding='utf-8-sig')
print('codebook.csv: %d rows' % len(cb))
