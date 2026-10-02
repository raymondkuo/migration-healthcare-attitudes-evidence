# -*- coding: utf-8 -*-
"""Israel's irregular_stock column held two different populations.

The archived PIBA booklet "Foreigners in Israel" (Q1 2022) publishes four separate counts,
and its own definitions section makes them mutually exclusive:

  infiltrators (מסתננים)              26,798   31.3.2022   entered via the Egyptian border
  legal foreign workers              103,131   31.3.2022   valid permit + registered employer
  illegal foreign workers             22,571   31.3.2022   WERE legal workers, no longer qualify
  tourists without a valid permit    ~30,100   31.12.2020  entered as tourists, stayed; CBS figure

The panel used the fourth figure for 2020 and the first for 2022, in one column. Read as a
series that is a spurious -11% fall; in fact the two numbers count different people,
published by different agencies at different reference dates. Same defect already corrected
for Taiwan, where one column mixed Ministry of Labor absconded workers with NIA overstayers.

Fixed without inventing a number:
  * 2020's 30,100 is an overstay count, so it moves to irregular_proxy_overstayers and is
    credited to its real publisher, the Central Bureau of Statistics as reproduced by PIBA.
  * 2022 keeps 26,798 in irregular_stock, with a note stating plainly that it counts
    infiltrators only and therefore understates the unauthorised population.
  * The components it excludes go into Irregular_estimates_all, visible rather than hidden.
"""
import os
import pandas as pd

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(SITE, 'data')
PDF = "https://www.gov.il/BlobFolder/generalpage/foreign_workers_stats/he/zarim_2022_q1.pdf"
PIBA = ("Israel Population and Immigration Authority (רשות האוכלוסין וההגירה), "
        "Foreigners in Israel (נתוני זרים בישראל), Q1 2022")
CBS_VIA_PIBA = ("Israel Central Bureau of Statistics press release of 27 January 2022, "
                "reproduced in " + PIBA)

p = pd.read_csv(os.path.join(D, "panel_final.csv"))
m20 = (p.iso3 == "ISR") & (p.year == 2020)
m22 = (p.iso3 == "ISR") & (p.year == 2022)
assert p.loc[m20, "irregular_stock"].iloc[0] == 30100, "unexpected 2020 value"
assert p.loc[m22, "irregular_stock"].iloc[0] == 26798, "unexpected 2022 value"
assert p.loc[m20, "irregular_proxy_overstayers"].isna().all(), "2020 overstayers not empty"
pop20 = float(p.loc[m20, "population"].iloc[0])
pop22 = float(p.loc[m22, "population"].iloc[0])

p.loc[m20, "irregular_proxy_overstayers"] = 30100.0
p.loc[m20, "irregular_proxy_overstayers_source"] = CBS_VIA_PIBA
p.loc[m20, "irregular_proxy_overstayers_url"] = PDF
p.loc[m20, "irregular_proxy_overstayers_grade"] = "B"
p.loc[m20, "irregular_proxy_overstayers_ref_date"] = "2020-12-31"
p.loc[m20, "irregular_proxy_overstayers_note"] = (
    "Foreigners who entered Israel as tourists from less-developed countries between 2008 "
    "and 2020 and remained at the end of 2020 without a valid permit; published as "
    '"30.1 thousand". The booklet credits the Central Bureau of Statistics for this figure. '
    "Mutually exclusive, by the definitions the source itself gives, from infiltrators and "
    "from illegal foreign workers.")
p.loc[m20, "irregular_proxy_overstayers_verification"] = (
    "The published figure appears in the archived source document.")
p.loc[m20, "irregular_proxy_overstayers_pct_pop"] = 30100.0 / pop20

for c in [c for c in p.columns if c.startswith("irregular_stock")]:
    p.loc[m20, c] = pd.NA

p.loc[m22, "irregular_stock_note"] = (
    "Reference date 31 March 2022. Administrative count of infiltrators (מסתננים) resident "
    "in Israel, i.e. persons who entered irregularly via the Egyptian border; 76% Eritrean, "
    "14% Sudanese. A LOWER BOUND on the unauthorised foreign population: it excludes the "
    "22,571 illegal foreign workers the same source reports at the same date, and the "
    "roughly 30,100 tourists without a valid permit at end-2020. By the definitions the "
    "source gives, these three groups do not overlap. Not comparable with the modelled "
    "estimates used for European countries.")
p.to_csv(os.path.join(D, "panel_final.csv"), index=False, encoding="utf-8-sig")
print("panel_final.csv updated")
print("  ISR 2020  irregular_stock removed; overstayers = 30,100 (CBS via PIBA)")
print("  ISR 2022  irregular_stock = 26,798, note now states it is a lower bound")

irr = pd.read_csv(os.path.join(D, "irregular_estimates_all.csv")).fillna("")
ADD = [
    dict(country="Israel", iso3="ISR", year=2022, variable="irregular_stock",
         value=22571, value_pct_pop=22571 / pop22,
         estimate_rank_in_cell="ALTERNATIVE - EXCLUDED COMPONENT",
         source_name=PIBA, source_url=PDF,
         notes="31.3.2022, illegal foreign workers: foreigners who were legal foreign workers "
               "and no longer meet at least one condition of that status. Excluded from the "
               "published irregular_stock, which counts infiltrators only. The two groups do "
               "not overlap, so the unauthorised population at that date is at least "
               "26,798 + 22,571 = 49,369."),
    dict(country="Israel", iso3="ISR", year=2020, variable="irregular_proxy_overstayers",
         value=30100, value_pct_pop=30100 / pop20,
         estimate_rank_in_cell="PANEL PRIMARY",
         source_name=CBS_VIA_PIBA, source_url=PDF,
         notes="End of 2020, tourists without a valid permit. Moved here from irregular_stock: "
               "it is an overstay count, not an estimate of the whole unauthorised population, "
               "and the 2022 cell of irregular_stock counts a different group entirely."),
    dict(country="Israel", iso3="ISR", year=2022, variable="foreign_nationals",
         value=103131, value_pct_pop=103131 / pop22,
         estimate_rank_in_cell="NOT USED - PARTIAL COMPONENT",
         source_name=PIBA, source_url=PDF,
         notes="31.3.2022, legal foreign workers. The only published component of the "
               "foreign-national population of Israel in this source. NOT used as "
               "foreign_nationals: it omits students, diplomats, permit-holding Palestinians "
               "and other visa classes, so it is not comparable with the Eurostat and OECD "
               "foreign-population series used for other countries."),
]
cols = list(irr.columns)
rows = [{c: a.get(c, "") for c in cols} for a in ADD]
irr2 = pd.concat([irr, pd.DataFrame(rows)], ignore_index=True)
irr2 = irr2.sort_values(["iso3", "variable", "year"]).reset_index(drop=True)
irr2.to_csv(os.path.join(D, "irregular_estimates_all.csv"), index=False, encoding="utf-8-sig")
print("irregular_estimates_all.csv: %d -> %d rows" % (len(irr), len(irr2)))
for a in ADD:
    print("   %s %d  %-30s %10s  %s" % (a["iso3"], a["year"], a["variable"],
                                        format(a["value"], ","), a["estimate_rank_in_cell"]))
