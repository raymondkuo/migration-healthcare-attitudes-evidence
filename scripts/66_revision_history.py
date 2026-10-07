# -*- coding: utf-8 -*-
"""A dated record of every amendment to the data after it was first collected.

The site said "Every source retrieved and verified 2026-08-17" on every page. That was
true on the day of publication and has not been true since: a value was corrected and
another deleted that evening, sources were re-queried and re-cited on 2026-08-18, five
snapshots were captured that day, and Israel's figures were re-classified on 2026-10-02.

Every entry below was taken from the git history of data/panel_final.csv and the other
data files, and every value change was confirmed by diffing consecutive versions of the
panel. Times are Asia/Taipei. Changes to presentation only - wording, translation, layout,
the credit line - are not data amendments and are left to the git log.

Also adds a date to each row of corrections_applied.csv and deleted_values.csv, and
records the Israel re-classification there, where every other change to an input value
is already itemised.
"""
import os
import pandas as pd

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(SITE, "data")

# amending kinds change a value, its classification, or what it is cited to
AMENDING = {"value corrected", "value deleted", "value reclassified", "flagged as derived",
            "source re-cited", "note amended", "values added", "grade changed", "flag changed"}

H = [
 dict(date="2026-08-17", time="16:53", commit="187428a", kind="first publication", iso3="",
      scope="All 40 countries", before="", after="2,219 values",
      change="Archive first published. Sources had been retrieved and every value compared "
             "with them earlier the same day; 49 values that disagreed with their source were "
             "corrected before publication and are itemised in Corrections applied.",
      change_zh="本存檔首次發布。同日稍早已重新取得各資料來源並逐筆比對；"
                "與來源不符之 49 筆數值已於發布前更正，逐筆列於「已套用之更正」。"),
 dict(date="2026-08-17", time="21:13", commit="812502d", kind="value corrected", iso3="KOR",
      scope="Korea · overstayers · 2015", before="212,596", after="214,168",
      change="The input figure was a 31 August snapshot inside a year-end series. Replaced with "
             "the year-end value from the Ministry of Justice yearbook, and 2010-2015 re-cited to "
             "that official series in place of a secondary source whose host no longer responds. "
             "2010-2014 values unchanged; grades raised from D to A and B.",
      change_zh="原始數值為年底序列中的 8 月 31 日快照，改以法務部統計年報之年底數值取代；"
                "並將 2010–2015 年改引該官方序列，取代主機已無回應之次級來源。"
                "2010–2014 年數值不變；等級自 D 提升為 A 與 B。"),
 dict(date="2026-08-17", time="22:19", commit="23b57c4", kind="value deleted", iso3="RUS",
      scope="Russia · irregular stock · 2020", before="1,200,000", after="deleted",
      change="The cited source, as archived, contains no numeric estimate. Removed under the rule "
             "that a value which cannot be traced to its source is not published.",
      change_zh="所引用之來源於存檔版本中並無任何數值推估。"
                "依「無法追溯至來源之數值不予發布」之原則刪除。"),
 dict(date="2026-08-17", time="22:19", commit="23b57c4", kind="flagged as derived",
      iso3="AUT;CHE;CZE;DEU;FRA;GBR;NLD",
      scope="Irregular stock · 13 cells", before="unmarked", after="marked as derived, grade C",
      change="Values unchanged. Each is the midpoint of a range Pew Research published, not a "
             "figure Pew published; now marked as derived, graded C, and shown beside the range.",
      change_zh="數值不變。各值為 Pew Research 所公布區間之中點，而非其公布之數字；"
                "現標示為推導值、評為 C 級，並與原區間並列呈現。"),
 dict(date="2026-08-18", time="10:21", commit="0d54c7d", kind="re-verified", iso3="",
      scope="Eurostat migr_eipre · 283 values", before="86.2% reproduced",
      after="100% reproduced",
      change="Values unchanged by this step. Every detection value re-queried live and compared "
             "with the corrected panel; all 283 matched. The 86.2% first result reflected the "
             "input workbook's one-year offset, corrected before publication.",
      change_zh="此步驟未變更數值。所有查獲人數數值皆即時重新查詢，並與更正後之 panel 比對，"
                "283 筆全數一致。首次測試之 86.2% 係反映原始工作表之一年位移，該位移已於發布前更正。"),
 dict(date="2026-08-18", time="11:11", commit="f9d7ae3", kind="source re-cited",
      iso3="CHE;ITA;JPN;KOR",
      scope="Switzerland 2015; Italy 2019-2022; Japan 2014; Korea 2010-2015",
      before="dead or blocked URLs cited", after="live source cited",
      change="Values unchanged. Where the citation supplied with the data had gone dead, the "
             "value is now cited to a live document stating the same figure, and the original is "
             "kept as a superseded citation. Italy 2022 moved to the XXVIII Rapporto, because "
             "the ISMU series ends at 2021.",
      change_zh="數值不變。原引用來源已失效者，改引仍可取得且載有相同數字之文件，"
                "原引用則保留為已更替之引用來源。義大利 2022 年改引第 XXVIII 號報告，"
                "因 ISMU 序列止於 2021 年。"),
 dict(date="2026-08-18", time="12:38", commit="34707a5", kind="evidence added",
      iso3="CHE;ITA;KOR",
      scope="Switzerland, Italy, Korea", before="", after="5 snapshots, 2 documents",
      change="Values unchanged. Dated live snapshots captured of the re-cited sources, and the two "
             "ISMU press releases originally cited were retrieved and archived; both state the "
             "published figures. The claim that ismu.org refused every client was corrected.",
      change_zh="數值不變。已擷取改引來源之日期戳記即時快照，"
                "並取得、存檔原引用之兩份 ISMU 新聞稿，其內容均載有所公布之數字。"
                "已更正「ismu.org 拒絕所有用戶端」之敘述。"),
 dict(date="2026-10-02", time="08:56", commit="d50724c", kind="value reclassified",
      iso3="ISR",
      scope="Israel · 2020", before="irregular stock 30,100", after="overstayers 30,100",
      change="The 2020 and 2022 cells of irregular stock counted two mutually exclusive "
             "populations: tourists who overstayed, and infiltrators via the Egyptian border. The "
             "2020 figure is an overstay count, so it now sits under overstayers, credited to the "
             "Central Bureau of Statistics as the source states.",
      change_zh="無證移民存量 2020 與 2022 年兩格所計為互不重疊之兩種人口："
                "逾期停留之觀光客，以及自埃及邊界非法入境者。"
                "2020 年數值屬逾期停留數，現改列於逾期停留欄位，並依來源所載註明出處為中央統計局。"),
 dict(date="2026-10-02", time="08:56", commit="d50724c", kind="note amended", iso3="ISR",
      scope="Israel · irregular stock · 2022", before="26,798", after="26,798 (lower bound)",
      change="Value unchanged. The note now states that it counts infiltrators only and so "
             "understates the unauthorised population, which on that date was at least 49,369.",
      change_zh="數值不變。備註現已載明其僅計入非法入境者，"
                "故低估未經許可人口；該日之未經許可人口至少為 49,369。"),
]

# Chinese for the short cells, keyed by (commit, kind) so it cannot attach to the wrong row
ZH = {
 ("187428a", "first publication"): ("全部 40 國", "", "2,219 筆數值"),
 ("812502d", "value corrected"): ("南韓 · 逾期停留 · 2015", "212,596", "214,168"),
 ("23b57c4", "value deleted"): ("俄羅斯 · 無證移民存量 · 2020", "1,200,000", "已刪除"),
 ("23b57c4", "flagged as derived"): ("無證移民存量 · 13 格", "未標示", "標示為推導值，C 級"),
 ("0d54c7d", "re-verified"): ("Eurostat migr_eipre · 283 筆數值", "重現率 86.2%", "重現率 100%"),
 ("f9d7ae3", "source re-cited"): ("瑞士 2015；義大利 2019–2022；日本 2014；南韓 2010–2015",
                                  "引用已失效或遭封鎖之網址", "改引仍可取得之來源"),
 ("34707a5", "evidence added"): ("瑞士、義大利、南韓", "", "5 份快照、2 份文件"),
 ("d50724c", "value reclassified"): ("以色列 · 2020", "無證移民存量 30,100", "逾期停留 30,100"),
 ("d50724c", "note amended"): ("以色列 · 無證移民存量 · 2022", "26,798", "26,798（下限）"),
}
# ---------------------------------------------------------------- the 2001 extension
# Counts come from the data files, not from this script. The commit hash and time are not known
# until the extension is committed, so they are read from a stamp file written afterwards and
# are blank until then.
import json
panel = pd.read_csv(os.path.join(D, "panel_final.csv"))
ovl = pd.read_csv(os.path.join(D, "extension_overlap_check.csv"))
spl = pd.read_csv(os.path.join(D, "extension_splice_summary.csv"))
MARK = ["population", "population_un_wpp2024", "foreign_born", "foreign_nationals"]
new = {v: int(panel[v + "_collected_on"].notna().sum()) for v in MARK}
n_new, n_mig = sum(new.values()), new["foreign_born"] + new["foreign_nationals"]
n_rows = int((panel.year < 2010).sum())
n_chk, n_same = int(ovl.cells_compared.sum()), int(ovl.identical.sum())
n_big = int((spl.mean_gap_pct.abs() >= 5).sum())
n_old_flag = int(sum((panel[v + "_collected_on"].isna() & panel[v + "_flag"].notna()
                      & panel[v + "_flag"].astype(str).str.strip().ne("")).sum()
                     for v in ("foreign_born", "foreign_nationals")))
stamp = {}
sp = os.path.join(D, "extension_staging", "commit_stamp.json")
if os.path.exists(sp):
    stamp = json.load(open(sp, encoding="utf-8"))
T, K = stamp.get("time", ""), stamp.get("commit", "")
ALL40 = ";".join(sorted(panel.iso3.unique()))
AMENDING.add("range extended")

H += [
 dict(date="2026-10-07", time=T, commit=K, kind="range extended", iso3=ALL40,
      scope="All 40 countries · 2001-2009 (and 2010-2011 for Taiwan)",
      before="520 rows, 2010-2022", after="880 rows, 2001-2022; %s new values" % format(n_new, ","),
      change="The panel was extended back to 2001. %s values were added - %s foreign-born and "
             "foreign-national values, and %s population values because the share columns need a "
             "denominator - and no value published earlier changed (asserted cell by cell against "
             "the 2026-08-17 panel). Sources were used in this order: the same source as the "
             "country's published series where it reaches the year, then another annual series, "
             "then census and UN benchmark years, each cell stating its source type and flag. "
             "%d series needed a source change at the join; %d of them differ from the series "
             "they were joined to by 5%% or more and are flagged. Irregular-migration variables "
             "were not extended. Flags (UN DESA estimates, the citizenship basis UN DESA "
             "declares, and the flags Eurostat itself attached) were also written for %d cells "
             "published earlier; they are notes about the values, and the values did not change."
             % (format(n_new, ","), format(n_mig, ","),
                format(new["population"] + new["population_un_wpp2024"], ","),
                len(spl), n_big, n_old_flag),
      change_zh="本 panel 已向前延伸至 2001 年。共新增 %s 筆數值——其中外國出生與外國籍人口數值 %s 筆，"
                "另因占比欄位需要分母而新增人口數值 %s 筆——先前已發布之數值無一變動"
                "（已逐格與 2026-08-17 之 panel 比對確認）。來源之採用順序為：若該國已發布序列所用之來源"
                "涵蓋該年度則沿用同一來源，其次為其他逐年序列，再次為普查與聯合國基準年，"
                "每一筆均載明其來源類型與旗標。有 %d 組序列於接合處需更換來源，其中 %d 組"
                "與所銜接之序列相差 5%% 以上，已加註旗標。無證移民相關變項未予延伸。此外，先前已發布之 %d 格亦"
                "補註旗標（UN DESA 估計值、UN DESA 宣告之公民身分基礎，以及 Eurostat 自身所附之旗標）；"
                "旗標僅為對數值之說明，數值本身未變動。"
                % (format(n_new, ","), format(n_mig, ","),
                   format(new["population"] + new["population_un_wpp2024"], ","), len(spl), n_big,
                   n_old_flag)),
 dict(date="2026-10-07", time=T, commit=K, kind="re-verified", iso3="",
      scope="Eurostat, OECD, World Bank, UN WPP, UN DESA mirror · %s published values"
            % format(n_chk, ","),
      before="last checked 2026-08-17 / 08-18", after="%s of %s reproduced exactly"
      % (format(n_same, ","), format(n_chk, ",")),
      change="Every payload retrieved for the extension spans 2001-2022, so the part covering "
             "2010-2022 was compared with the values already published: Eurostat %s, OECD %s, "
             "World Bank population %s, UN WPP %s and the UN DESA mirror %s cells. All reproduced "
             "exactly (OECD's decimal values compared after rounding to whole persons, as the "
             "panel stores them)."
             % tuple(format(int(ovl[ovl.source.str.startswith(k)].cells_compared.sum()), ",")
                     for k in ("Eurostat", "OECD", "World Bank SP.POP.TOTL", "UN WPP 2024",
                               "World Bank SM.POP.TOTL")),
      change_zh="為本次延伸所取得之每一份回應均涵蓋 2001–2022 年，故其涵蓋 2010–2022 年之部分已與先前發布之數值"
                "比對：Eurostat、OECD、世界銀行人口、UN WPP 與 UN DESA 鏡像，共 %s 格，"
                "全數完全一致（OECD 之小數值於四捨五入至整數後比對，與 panel 之儲存方式相同）。"
                % format(n_chk, ",")),
 dict(date="2026-10-07", time=T, commit=K, kind="note amended", iso3="TWN",
      scope="Taiwan · foreign residents · 2012-2022 (11 notes)",
      before="series begins in 2012", after="MOI table 1996-2022 used",
      change="Values unchanged. The note said the series on this basis begins in 2012. The Ministry "
             "of the Interior's consolidated table 1996-2022 gives the earlier years as well, with "
             "all eleven published values reproducing exactly, so 2001-2011 were added with a "
             "comparability caution and the original statement was kept in the note.",
      change_zh="數值不變。原備註稱依此基礎之序列自 2012 年起。內政部統計處 1996–2022 年之彙整表亦提供較早年度，"
                "且已發布之 11 筆數值完全重現，故新增 2001–2011 年並加註可比性提醒，原說明則保留於備註中。"),
 dict(date="2026-10-07", time=T, commit=K, kind="collection attempted, not obtained", iso3="AUS;CHL",
      scope="Australia (foreign nationals) · Chile 2002 (foreign-born)",
      before="", after="not collected",
      change="Australia: the ABS Census QuickStats pages carry no citizenship totals and the other "
             "ABS host did not resolve, so no national count of non-citizens was retrieved. Chile: "
             "the INE Census 2017 synthesis gives 2017 (746,465) but only the 2002 share (1.27%); "
             "the longer INE report that may hold the 2002 count stopped downloading partway, and "
             "a count was not derived from a percentage.",
      change_zh="澳洲：澳洲統計局普查 QuickStats 頁面不含公民身分總數，另一個澳洲統計局主機無法解析，"
                "故未取得全國非公民人數。智利：INE 2017 年普查綜合報告載有 2017 年數（746,465），"
                "但 2002 年僅有比例（1.27%）；可能載有 2002 年人數之較長報告於下載途中中斷，"
                "且不從百分比推算人數。"),
]
ZH.update({
 ("%s" % K, "range extended"): ("全部 40 國 · 2001–2009（臺灣另含 2010–2011）",
                                 "520 列，2010–2022", "880 列，2001–2022；新增 %s 筆數值" % format(n_new, ",")),
 ("%s" % K, "re-verified"): ("Eurostat、OECD、世界銀行、UN WPP、UN DESA 鏡像 · 已發布數值 %s 筆"
                              % format(n_chk, ","), "最近查證：2026-08-17／08-18",
                              "%s 筆中 %s 筆完全重現" % (format(n_chk, ","), format(n_same, ","))),
 ("%s" % K, "note amended"): ("臺灣 · 外僑居留人數 · 2012–2022（11 筆備註）", "序列自 2012 年起",
                               "採用內政部 1996–2022 年彙整表"),
 ("%s" % K, "collection attempted, not obtained"): ("澳洲（外國籍）· 智利 2002（外國出生）", "", "未能蒐集"),
})

# ---------------------------------------------------------------- the audit of 2026-10-07
# Entries carry their own Chinese in the dict (several share a kind and a commit, so the (commit, kind)
# lookup used above cannot tell them apart). The commit and time come from their own stamp file.
ap = os.path.join(D, "extension_staging", "commit_stamp_audit.json")
astamp = json.load(open(ap, encoding="utf-8")) if os.path.exists(ap) else {}
TA, KA = astamp.get("time", ""), astamp.get("commit", "")
chg = pd.read_csv(os.path.join(D, "audit_changes_2026-10-07.csv"))
n_a2b = int(((chg.old_grade == "A") & (chg.new_grade == "B")).sum())
n_del = int((chg.kind == "deleted").sum())
sp_ = pd.read_csv(os.path.join(D, "extension_splice_summary.csv"))
n_large_new = int((sp_.mean_abs_gap_pct >= 5).sum())
dq_ = pd.read_csv(os.path.join(D, "data_quality.csv"))
n_usable = int(dq_.usable_for_trend.str.contains("single source").sum())
n_added = int((chg.kind == "added").sum())
A = dict(date="2026-10-07", time=TA, commit=KA)
H += [
 dict(A, kind="value corrected", iso3="CHL", scope="Chile - irregular stock - 2018-2022",
      scope_zh="智利 · 無證移民存量 · 2018–2022",
      before="59,682 / 115,059 / 130,017 / 53,356 / 109,846", before_zh="59,682／115,059／130,017／53,356／109,846",
      after="10,375 / 21,833 / 53,356 / 109,846 / 291,149", after_zh="10,375／21,833／53,356／109,846／291,149",
      change="The first release took the five values from the right chart (page 12 of the INE/SERMIG Sintesis 2023) but "
             "placed them under the wrong years and mixed the 2022 and 2023 methodologies. Now the 2023 methodology for "
             "every year; the 2022 methodology and the press-release 107,223 are alternatives. Audit finding F01.",
      change_zh="首次發布由正確之圖表（INE/SERMIG《2023 年摘要》第 12 頁）取得五個數值，卻置於錯誤年度並混用 2022 與 2023 年方法。"
                "現各年一律採 2023 年方法；2022 年方法與新聞稿之 107,223 列為替代值。稽核發現 F01。"),
 dict(A, kind="value corrected", iso3="IND", scope="India - foreign-born - 2011", scope_zh="印度 · 外國出生人口 · 2011",
      before="5,490,000", before_zh="5,490,000", after="5,363,099", after_zh="5,363,099",
      change="5,490,000 was Table 2a of a journal article, built on Census Table D-2 (place of LAST residence). The "
             "official birthplace table D-01 gives 5,363,099 in its national row \"Born Outside India\". Authors of the "
             "article corrected to Singh and Biradar. Audit finding F02.",
      change_zh="5,490,000 為一篇期刊論文之表 2a，以普查表 D-2（最近一次居住地）為基礎。官方出生地表 D-01 全國列「Born Outside India」為 5,363,099。"
                "論文作者更正為 Singh 與 Biradar。稽核發現 F02。"),
 dict(A, kind="value corrected", iso3="SUR", scope="Suriname - foreign nationals - 2012",
      scope_zh="蘇利南 · 外國籍人口 · 2012", before="36,393", before_zh="36,393", after="33,053", after_zh="33,053",
      change="36,393 was total population minus Surinamese nationals and includes 3,340 persons of unknown nationality. "
             "The six printed foreign nationality categories sum to 33,053; 36,393 is kept as an alternative. Audit finding F03.",
      change_zh="36,393 為總人口減蘇利南籍，包含 3,340 名國籍不明者。表中所印六個外國國籍類別加總為 33,053；36,393 保留為替代值。稽核發現 F03。"),
 dict(A, kind="value corrected", iso3="TWN", scope="Taiwan - population - 2010-2016 (7 values)",
      scope_zh="臺灣 · 總人口 · 2010–2016（7 筆）", before="rounded to thousands (NDC)", before_zh="四捨五入至千位（國發會）",
      after="exact totals (MOI yearbook)", after_zh="精確總數（內政部年報）",
      change="The cited MOI yearbook prints exact totals (23,162,123 ... 23,539,816); the panel held the NDC figures rounded to "
             "thousands. Differences -123 to +483 persons; shares recomputed. Audit finding F08.",
      change_zh="所引用之內政部年報載有精確總數（23,162,123 … 23,539,816）；panel 所載為國發會四捨五入至千位之數。差異 −123 至 +483 人；占比已重算。稽核發現 F08。"),
 dict(A, kind="value corrected", iso3="TWN", scope="Taiwan - absconded workers - 2019",
      scope_zh="臺灣 · 失聯移工 · 2019", before="47,632 (31 July)", before_zh="47,632（7 月 31 日）",
      after="48,491 (year-end)", after_zh="48,491（年底）",
      change="The column is the Ministry of Labor year-end stock; 2019 held the 31 July figure of a Legislative Yuan report. Table 12-7 "
             "gives 48,491 for the end of 2019; 47,632 is kept as an alternative. Found while checking finding F06.",
      change_zh="該欄為勞動部年底存量；2019 年所載為立法院報告之 7 月 31 日數字。表 12-7 之 2019 年底為 48,491；47,632 保留為替代值。查核稽核發現 F06 時發現。"),
 dict(A, kind="value deleted", iso3="TWN", scope="Taiwan - overstayers - 2021", scope_zh="臺灣 · 逾期停留 · 2021",
      before="81,538", before_zh="81,538", after="deleted", after_zh="已刪除",
      change="The cited Ministry of Labor table (Table 12-7) is the absconded-worker series; no archived or located document gives "
             "an end-2021 total of 81,538. Deleted under the traceability rule. Audit finding F06.",
      change_zh="所引用之勞動部表（表 12-7）為失聯移工序列；任何存檔或查得之文件均無 2021 年底 81,538 之總數。依可追溯原則刪除。稽核發現 F06。"),
 dict(A, kind="source re-cited", iso3="TWN", scope="Taiwan - overstayers - 2012, 2013, 2019, 2020 (and notes 2014-2018)",
      scope_zh="臺灣 · 逾期停留 · 2012、2013、2019、2020（及 2014–2018 備註）",
      before="cited a Ministry of Labor absconded-worker table", before_zh="引用勞動部失聯移工表",
      after="Legislative Yuan Budget Center reports", after_zh="立法院預算中心報告",
      change="Values unchanged. The numbers are in the Legislative Yuan reports of July 2019 (附表11) and September 2021 (Table 1), "
             "which are now cited. The notes now say the total covers all categories of overstaying persons (foreign nationals, "
             "mainland Chinese, Hong Kong/Macao, no household registration), with the foreign-national component for 2012-2018 as an "
             "alternative; 2019-2020 are labelled as a year whose month the source does not state. Audit findings F06 and F07.",
      change_zh="數值不變。該些數字見立法院預算中心 2019 年 7 月報告（附表11）與 2021 年 9 月報告（表 1），現已改引。備註現載明該總數涵蓋逾期人員之所有類別"
                "（外國人、大陸地區人民、港澳居民、無戶籍國民），2012–2018 年之外國人部分列為替代值；2019–2020 年標示為來源未載月份之年度。稽核發現 F06 與 F07。"),
 dict(A, kind="values added", iso3="AUS;JPN;ISL", scope="Australia 2015; Japan 2010, 2012, 2013, 2015; Iceland 2021 (%d values)" % n_added,
      scope_zh="澳洲 2015；日本 2010、2012、2013、2015；冰島 2021（%d 筆）" % n_added,
      before="blank", before_zh="空白", after="values with sources", after_zh="附來源之數值",
      change="Held by the secondary workbook and omitted from the panel although the archived sources support them: the DIBP Annual "
             "Report 2015-16 (unlawful non-citizens, 62,000 at 30 June 2015), ISA Table 21 (overstayers 1 January) and the archived "
             "Eurostat payload (Iceland 2021 detections, 130). Audit finding F16.",
      change_zh="次要活頁簿載有而 panel 遺漏，但存檔來源可支持：DIBP 2015–16 年報（2015 年 6 月 30 日之非法非公民 62,000）、"
                "入國管理局表 21（1 月 1 日之逾期停留）與所存檔之 Eurostat 回應（冰島 2021 年查獲數 130）。稽核發現 F16。"),
 dict(A, kind="grade changed", iso3="TWN;GBR", scope="%d values: Taiwan population 2010-2022, Taiwan overstayers, UK foreign-born 2020" % n_a2b,
      scope_zh="%d 筆：臺灣 2010–2022 人口、臺灣逾期停留、英國 2020 外國出生人口" % n_a2b,
      before="A", before_zh="A", after="B", after_zh="B",
      change="Values read from a printed table are grade B, not A (grade A is decoded from a machine-readable source). With the deleted "
             "Taiwan 2021 value that is the 19 grade-A values the audit identified. Grades are now defined by provenance only. Audit finding F20.",
      change_zh="讀自印刷表格之數值為 B 級而非 A 級（A 級指由機器可讀來源解出）。連同已刪除之臺灣 2021 年數值，即稽核所指之 19 筆 A 級數值。"
                "等級現僅依出處定義。稽核發現 F20。"),
 dict(A, kind="flag changed", iso3="DEU;POL;PRT;LTU", scope="Splice flags: Germany foreign-born 2006-2008 now \"splice (large gap)\"",
      scope_zh="接續旗標：德國外國出生人口 2006–2008 現標示「splice (large gap)」", before="7 series flagged", before_zh="7 組序列被標示",
      after="%d series flagged" % n_large_new, after_zh="%d 組序列被標示" % n_large_new,
      change="The large-gap rule is a mean ABSOLUTE gap of 5%% or more; the code had tested the signed mean. Both are now reported in "
             "extension_splice_summary.csv. Values unchanged. Audit finding F12." % (),
      change_zh="達 5% 以上之判準為「平均絕對」差距；程式原檢定有號平均。現兩者均載於 extension_splice_summary.csv。數值不變。稽核發現 F12。"),
 dict(A, kind="value reclassified", iso3="CHN;IND;PHL;SUR;THA", scope="UN DESA citizenship-basis migrant stock (20 cells)",
      scope_zh="UN DESA 公民身分基礎之移民存量（20 格）", before="in foreign_born without distinction", before_zh="未加區分地列於 foreign_born",
      after="marked in foreign_born_concept; separate columns in the analysis extract", after_zh="於 foreign_born_concept 標明；分析用資料集中另列欄位",
      change="UN declares these stocks on a citizenship basis. Values unchanged. The extract keeps them out of foreign_born. Audit finding F04.",
      change_zh="UN 將這些存量宣告為公民身分基礎。數值不變。分析用資料集將其排除於 foreign_born 之外。稽核發現 F04。"),
 dict(A, kind="evidence added", iso3="IND;CHL;SUR;TWN;JPN;AUS", scope="India Census 2011 D-01 workbook; page extracts for Chile, Suriname, Taiwan, Japan, Australia; status and verification tables",
      scope_zh="印度 2011 年普查 D-01 活頁簿；智利、蘇利南、臺灣、日本、澳洲之頁面摘錄；狀態與查證表",
      before="", before_zh="", after="archived and registered", after_zh="已存檔並登錄",
      change="Evidence for the corrected and added values, a status for every record of irregular_estimates_all.csv, used_in_panel rebuilt in "
             "every country's data_from_source.csv, the source register's data_raw/ placeholders routed to exact files, "
             "current_panel_verification.csv, secondary_workbook_differences.csv, the chart check and REBUILD.md. Audit findings F14, F15, F16, F21, F23.",
      change_zh="更正與新增數值之佐證、irregular_estimates_all.csv 每筆之狀態、各國 data_from_source.csv 重建之 used_in_panel、"
                "來源清冊 data_raw/ 佔位符改指確切檔案、current_panel_verification.csv、secondary_workbook_differences.csv、圖表檢查與 REBUILD.md。"
                "稽核發現 F14、F15、F16、F21、F23。"),
 dict(A, kind="re-verified", iso3="", scope="Audit of 2026-10-07: 24 findings re-checked against the archived sources",
      scope_zh="2026-10-07 稽核：24 項發現已對照存檔來源重新查核",
      before="last checked 2026-10-07 (extension)", before_zh="最近查證：2026-10-07（延伸）",
      after="24 of 24 confirmed; %d cell changes" % len(chg), after_zh="24 項全部屬實；%d 項儲存格變更" % len(chg),
      change="Each finding was checked against the archived source or the publisher's own page before anything was changed (verification/"
             "AUDIT_RESPONSE_2026-10-07.md). The source links were re-tested, failures retried with curl, and the date and method of each "
             "check recorded (verification/link_sweep.csv). Audit findings F22, F23.",
      change_zh="每項發現均先對照存檔來源或出版機構自身頁面查核，再行變更（verification/AUDIT_RESPONSE_2026-10-07.md）。來源連結已重新測試，"
                "失敗者以 curl 重試，並記錄每次檢查之日期與方法（verification/link_sweep.csv）。稽核發現 F22、F23。"),
]

# ---------------------------------------------------------------- the re-audit of commit 30d6cb1
rp = os.path.join(D, "extension_staging", "commit_stamp_reaudit.json")
rstamp = json.load(open(rp, encoding="utf-8")) if os.path.exists(rp) else {}
B = dict(date="2026-10-07", time=rstamp.get("time", ""), commit=rstamp.get("commit", ""))
H += [
 dict(B, kind="flagged as derived", iso3="HRV", scope="Croatia - foreign nationals - 2011", scope_zh="克羅埃西亞 · 外國籍人口 · 2011",
      before="23,276 (not marked derived)", before_zh="23,276（未標示為推導值）",
      after="23,276 (derived: sum of two printed categories)", after_zh="23,276（推導值：兩個印出分項之加總）",
      change="The value is the sum of foreign citizens (22,527) and stateless persons (749), which the census table prints separately; "
             "it was not marked derived. Value unchanged. The codebook now counts 17 derived values (13 range midpoints, 2 differences, "
             "2 sums), not 16. Re-audit R07.",
      change_zh="該數值為外國公民（22,527）與無國籍者（749）之加總，普查表分別列出此兩項；原未標示為推導值。數值不變。"
                "變數說明書現計 17 筆推導值（13 筆區間中點、2 筆差、2 筆加總），而非 16 筆。再稽核 R07。"),
 dict(B, kind="flag changed", iso3="FRA;NLD;SWE", scope="Detections: Eurostat break-in-series flags on France 2014, Netherlands 2015, Sweden 2014 and 2015",
      scope_zh="查獲數：Eurostat 對法國 2014、荷蘭 2015、瑞典 2014 與 2015 標示之時間序列斷裂旗標",
      before="no flag", before_zh="無旗標", after="Eurostat flag: break in time series", after_zh="Eurostat flag: break in time series",
      change="Eurostat marks these four values \"b\" (break in time series). Values unchanged. A new column irregular_proxy_detections_flag "
             "carries the flag; the data-quality table no longer rates the three detection series as continuous. Re-audit R04.",
      change_zh="Eurostat 對這四筆數值標示「b」（時間序列斷裂）。數值不變。新增 irregular_proxy_detections_flag 欄位載明旗標；"
                "資料品質表不再將這三組查獲數序列評為連續。再稽核 R04。"),
 dict(B, kind="re-verified", iso3="", scope="Independent re-audit of commit 30d6cb1: 11 findings",
      scope_zh="獨立再稽核 commit 30d6cb1：11 項發現",
      before="24 of 24 audit findings confirmed", before_zh="稽核 24 項發現全部屬實",
      after="11 of 11 re-audit findings confirmed", after_zh="再稽核 11 項發現全部屬實",
      change="Each was re-checked against the archived source, the data files or a clean rebuild before anything was changed "
             "(verification/AUDIT_RESPONSE_2026-10-07.md, re-audit section). One was a build defect: the ledger needed audit results "
             "kept outside the repository, which an earlier rebuild test, run beside them, could not show. Re-audit R01-R11.",
      change_zh="每項均先對照存檔來源、資料檔或乾淨重建查核，再行變更（verification/AUDIT_RESPONSE_2026-10-07.md 再稽核一節）。"
                "其中一項為建置缺失：驗證表所需之稽核結果存放於存放庫之外，先前於其旁進行之重建測試無法顯現。再稽核 R01–R11。"),
 dict(B, kind="documentation corrected", iso3="", scope="Descriptions, verification ledger and build inputs",
      scope_zh="說明文字、驗證表與建置輸入",
      before="see the response file", before_zh="見回覆檔案", after="corrected; values unchanged", after_zh="已更正；數值不變",
      change="Grade definitions made mutually exclusive (C only for midpoints the archive computed); overstayer definitions state the mix of "
             "register counts, estimates, a broader Australian group and one component; the large-gap rule reads the mean absolute gap in "
             "every summary; the Eurostat/OECD date row is source-specific; the verification ledger gives each check method and the "
             "population date convention, with its audit inputs committed (data/audit_inputs/); the analysis-notes splice table has "
             "five columns and its lag-rule sentence is corrected; workbook-guide and README counts separate present from first-release "
             "figures; the Chinese label for Eurostat detections says persons. Re-audit R01-R03, R05, R06, R08-R11.",
      change_zh="等級定義改為互斥（C 級僅限本存檔計算之中點）；逾期停留者之定義載明登記數、推估數、範圍較廣之澳洲群體與單一組成部分並存；"
                "各項摘要一律以平均絕對差距判定大幅差距；Eurostat／OECD 之日期列改依來源；驗證表載明每筆查核方式與母體人口日期，"
                "並將其稽核輸入納入存放庫（data/audit_inputs/）；分析說明之接合表改為五欄，並更正其落後規則之敘述；"
                "活頁簿說明與 README 之計數區分現況與首次發布之數字；Eurostat 查獲數之中文標籤改為「人數」。再稽核 R01–R03、R05、R06、R08–R11。"),
]

# A correction to the published record itself, not to a value (so not in AMENDING). It has no
# commit stamp: the commit that carries it cannot name its own hash.
H.append(dict(
    date="2026-10-07", time="", commit="", kind="manifest corrected", iso3="",
    scope="manifest/checksums.csv · text files and 24 raw captures",
    before="hashes of the Windows working copy", after="hashes of the bytes the site serves",
    change="Values unchanged. The checksum manifest had been built from the working folder, where "
           "git on Windows writes text files with CRLF line endings, while GitHub serves them with "
           "LF; the hash of any downloaded CSV, page or Markdown file therefore differed from the "
           "recorded one (PDF, image and spreadsheet files were not affected). The manifest now "
           "hashes the bytes the site serves, scripts/78_verify_checksums.py checks every row "
           "against what git stored, and 24 downloaded web pages and CSV files whose servers send "
           "CRLF are now stored byte for byte as saved (.gitattributes) instead of with the line "
           "endings converted.",
    change_zh="數值不變。雜湊清單原是依工作資料夾計算；在 Windows 上，git 於工作資料夾以 CRLF 寫入文字檔，"
              "而 GitHub 提供之檔案為 LF，故任何下載之 CSV、網頁或 Markdown 檔之雜湊值皆與記錄不符"
              "（PDF、圖片與試算表檔不受影響）。現清單改依網站實際提供之位元組計算，"
              "並以 scripts/78_verify_checksums.py 將每一列與 git 所存內容核對；另有 24 個下載之網頁與 CSV 檔"
              "（其伺服器以 CRLF 傳送）現已逐位元組依所存內容保存（.gitattributes），不再轉換換行字元。"))
ZH[("", "manifest corrected")] = ("manifest/checksums.csv · 文字檔與 24 個原始擷取檔",
                                 "依 Windows 工作資料夾計算之雜湊值", "依網站實際提供之位元組計算之雜湊值")
hist = pd.DataFrame(H)
for col in ('scope_zh', 'before_zh', 'after_zh'):
    if col not in hist.columns:
        hist[col] = None
direct = hist.scope_zh.notna()
missing_zh = [k for k, d in zip(zip(hist.commit, hist.kind), direct) if not d and k not in ZH]
assert not missing_zh, 'revision rows with no Chinese: %s' % missing_zh
for i, col in enumerate(('scope_zh', 'before_zh', 'after_zh')):
    hist[col] = [r[col] if d else ZH[(r['commit'], r['kind'])][i]
                 for (_, r), d in zip(hist.iterrows(), direct)]
hist["amends_data"] = hist.kind.isin(AMENDING).map({True: "yes", False: ""})
hist = hist[["date", "time", "commit", "kind", "amends_data", "iso3",
             "scope", "scope_zh", "before", "before_zh", "after", "after_zh",
             "change", "change_zh"]]
hist.to_csv(os.path.join(D, "revision_history.csv"), index=False, encoding="utf-8-sig")
print("revision_history.csv: %d entries, %s to %s" % (len(hist), hist.date.min(), hist.date.max()))
for _, r in hist.iterrows():
    print("  %s %s  %-19s %s" % (r.date, r.time, r.kind, r.scope[:60]))

# ---- date every itemised correction, and add Israel's
c = pd.read_csv(os.path.join(D, "corrections_applied.csv"))
if "corrected_on" not in c.columns:
    c.insert(5, "corrected_on", "2026-08-17")
add = pd.DataFrame([
    dict(iso3="ISR", year=2020, variable="irregular_stock", old_value=30100.0, new_value=None,
         corrected_on="2026-10-02",
         reason="Moved, not discarded: an overstay count, not an estimate of the unauthorised "
                "population, and the 2022 cell of this column counts a different, mutually "
                "exclusive group. See irregular_proxy_overstayers for the same year.",
         evidence="PIBA, Foreigners in Israel Q1 2022, definitions section; figure credited "
                  "there to the Central Bureau of Statistics press release of 27 January 2022."),
    dict(iso3="ISR", year=2020, variable="irregular_proxy_overstayers", old_value=None,
         new_value=30100.0, corrected_on="2026-10-02",
         reason="The tourists-without-a-valid-permit figure, moved here from irregular_stock.",
         evidence="As above."),
])
have = set(zip(c.iso3, c.year, c.variable))
add = add[[k not in have for k in zip(add.iso3, add.year, add.variable)]]
c = pd.concat([c, add], ignore_index=True)
c.to_csv(os.path.join(D, "corrections_applied.csv"), index=False, encoding="utf-8-sig")
print("\ncorrections_applied.csv: %d rows, dated %s" %
      (len(c), dict(c.corrected_on.value_counts())))

dv = pd.read_csv(os.path.join(D, "deleted_values.csv"))
if "deleted_on" not in dv.columns:
    dv.insert(4, "deleted_on", "2026-08-17")
dv.to_csv(os.path.join(D, "deleted_values.csv"), index=False, encoding="utf-8-sig")
print("deleted_values.csv: %d row(s), dated" % len(dv))
