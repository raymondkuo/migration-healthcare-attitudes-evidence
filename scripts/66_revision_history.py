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
            "source re-cited", "note amended"}

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
      change_zh="此步驟未變更數值。所有查獲人次數值皆即時重新查詢，並與更正後之 panel 比對，"
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
hist = pd.DataFrame(H)
missing_zh = [k for k in zip(hist.commit, hist.kind) if k not in ZH]
assert not missing_zh, 'revision rows with no Chinese: %s' % missing_zh
hist['scope_zh'] = [ZH[k][0] for k in zip(hist.commit, hist.kind)]
hist['before_zh'] = [ZH[k][1] for k in zip(hist.commit, hist.kind)]
hist['after_zh'] = [ZH[k][2] for k in zip(hist.commit, hist.kind)]
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
