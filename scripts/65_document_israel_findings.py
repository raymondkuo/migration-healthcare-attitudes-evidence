# -*- coding: utf-8 -*-
"""Record the two Israel findings in known_issues, in both languages.

1. RESOLVED - irregular_stock mixed two mutually exclusive populations across 2020 and 2022.
2. MEDIUM  - foreign_nationals is absent for six countries, Israel among them. Verified
   against the live OECD API: the B15 "Stocks of foreign population" series exists for
   Israel but every observation is null, so there is nothing to retrieve rather than
   something that was overlooked.
"""
import os
import pandas as pd

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(SITE, "data")
p = os.path.join(D, "known_issues.csv")
k = pd.read_csv(p).fillna("")

NEW = [
 dict(severity="RESOLVED", scope="Israel", variable="irregular_stock",
      issue="One column held two mutually exclusive populations. 2020 carried tourists who "
            "overstayed (30,100, end-2020, a Central Bureau of Statistics figure); 2022 carried "
            "infiltrators who entered via the Egyptian border (26,798, 31.3.2022, PIBA). Read "
            "as a series that is a spurious -11% fall between two counts of different people.",
      issue_zh="單一欄位混用兩種互不重疊的人口。2020 年為逾期停留之觀光客"
               "（30,100，2020 年底，中央統計局數據）；2022 年為自埃及邊界非法入境者"
               "（26,798，2022 年 3 月 31 日，以色列人口及移民署）。"
               "若當作時間序列解讀，會在兩筆計算不同人群的數值之間產生虛假的 −11% 下降。",
      evidence="The archived PIBA booklet publishes four separate counts and its own definitions "
               "section makes them mutually exclusive: infiltrators 26,798; legal foreign workers "
               "103,131; illegal foreign workers 22,571 (all 31.3.2022); tourists without a valid "
               "permit about 30,100 (31.12.2020).",
      evidence_zh="所存檔之以色列人口及移民署手冊載有四項獨立統計，其自身定義章節明示四者互不重疊："
                  "非法入境者 26,798；合法外籍勞工 103,131；非法外籍勞工 22,571"
                  "（均為 2022 年 3 月 31 日）；無有效簽證之觀光客約 30,100（2020 年 12 月 31 日）。",
      action="Corrected: the 2020 figure moved to irregular_proxy_overstayers, which is what it "
             "measures, and is now credited to the Central Bureau of Statistics as reproduced by "
             "PIBA. 2022 keeps 26,798 in irregular_stock with the note stating that it counts "
             "infiltrators only and is therefore a lower bound - at that date the unauthorised "
             "population is at least 26,798 + 22,571 = 49,369. The excluded components are "
             "recorded in Irregular_estimates_all.",
      action_zh="已更正：2020 年數值移至其實際測量之欄位 irregular_proxy_overstayers，"
                "並改註明出處為中央統計局（經人口及移民署轉載）。"
                "2022 年仍以 26,798 列於 irregular_stock，並於備註明示其僅計入非法入境者，"
                "故屬下限——該日之未經許可人口至少為 26,798 + 22,571 = 49,369。"
                "被排除之組成項目已登錄於 Irregular_estimates_all 工作表。"),
 dict(severity="MEDIUM",
      scope="Australia, India, Israel, New Zealand, Russia, South Africa",
      variable="foreign_nationals",
      issue="These six countries have no foreign-national stock in the panel. They do not "
            "compile a foreign-population register of the kind Eurostat and the OECD collect.",
      issue_zh="這六個國家在本 panel 中沒有外國籍人口存量資料。"
               "其並未編製 Eurostat 與 OECD 所蒐集之該類外國人口登記統計。",
      evidence="Verified against the live OECD API on 2026-10-02: the B15 Stocks of foreign "
               "population series is defined for Israel but returns four observations whose values "
               "are all null. Israel is not in the Eurostat migr_pop1ctz universe. The only "
               "published component is legal foreign workers (103,131 at 31.3.2022), which omits "
               "students, diplomats, permit-holding Palestinians and other visa classes.",
      evidence_zh="已於 2026-10-02 對照線上 OECD API 查證：以色列雖有 B15"
                  "「外國人口存量」序列之定義，但回傳之四筆觀測值全為空值。"
                  "以色列亦不在 Eurostat migr_pop1ctz 之範圍內。"
                  "該國唯一公布之組成項目為合法外籍勞工（2022 年 3 月 31 日為 103,131），"
                  "未涵蓋學生、外交人員、持證巴勒斯坦人及其他簽證類別。",
      action="Left empty rather than approximated: no comparable figure exists, and summing the "
             "published components would not match the Eurostat and OECD definitions used for the "
             "other 34 countries. Use foreign_born for these countries, noting that it counts "
             "naturalised citizens as migrants, or restrict the model to the 34 countries that "
             "have foreign_nationals.",
      action_zh="予以留空而不作近似推估：並無可比較之數值，"
                "且將已公布之組成項目加總後，仍與其他 34 國所採用之 Eurostat 與 OECD 定義不符。"
                "此六國建議改用 foreign_born（惟須注意其將歸化公民計為移民），"
                "或將模型限於具備 foreign_nationals 之 34 國。"),
]
for row in NEW:
    dup = (k.scope == row["scope"]) & (k.variable == row["variable"])
    assert not dup.any(), "a row already exists for %s / %s" % (row["scope"], row["variable"])
k = pd.concat([k, pd.DataFrame(NEW)], ignore_index=True)[list(k.columns)]
k.to_csv(p, index=False, encoding="utf-8-sig")
print("known_issues.csv: %d rows" % len(k))
print(dict(k.severity.value_counts()))
for row in NEW:
    print("  + %-8s %-56s %s" % (row["severity"], row["scope"][:56], row["variable"]))
