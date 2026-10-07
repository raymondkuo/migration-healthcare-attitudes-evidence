# -*- coding: utf-8 -*-
"""Source-chart check: read a value, its year and its series from the chart itself.

Audit finding F01 found that the five Chile irregular-stock values had been taken from the right
chart and placed under the wrong years and series, and that nothing in the archive's checks could
notice: the evidence pages and PDF extracts reproduce whatever the panel holds. This script reads
the chart on page 12 of the INE/SERMIG Sintesis 2023 from the PDF's own geometry, so that a value
is tied to a year and a series by position and colour, not by an eye:

  * each numeric label is matched to its nearest marker (blue diamond = 2022 methodology,
    orange square = 2023 methodology);
  * the marker's x position gives the year (the x-axis year labels);
  * the marker's height, through the y-axis labels, must agree with the printed value (so a label
    cannot be attached to the wrong marker);
  * the Chile values in panel_final.csv must equal the series the panel says it uses.

It exits non-zero on any disagreement and writes verification/source_chart_checks.csv.
"""
import math
import os
import re
import sys

import fitz
import numpy as np
import pandas as pd

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(SITE, 'evidence', 'countries', 'CHL', 'irregular_stock__f8f04e39ba__www.ine.gob.cl.pdf')
PAGE = 12                                           # 1-based

pg = fitz.open(PDF)[PAGE - 1]
words = pg.get_text('words')
assert 'Resultados generales irregularidad' in pg.get_text() and 'Comparación metodología' in pg.get_text(), \
    'page %d is not the irregular-component chart' % PAGE


def center(w):
    return ((w[0] + w[2]) / 2, (w[1] + w[3]) / 2)


# x-axis: the year labels in the bottom row of the plot
years = {int(w[4]): center(w)[0] for w in words if re.fullmatch(r'20(1[89]|2[0-3])', w[4]) and w[1] > 420}
assert sorted(years) == [2018, 2019, 2020, 2021, 2022, 2023], years
# y-axis: labels like 50.000 ... 400.000 at the left of the plot
ylab = [(float(w[4].replace('.', '')), center(w)[1]) for w in words
        if re.fullmatch(r'\d{2,3}\.000', w[4]) and center(w)[0] < 100]
assert len(ylab) >= 6, ylab
vals, ys = zip(*ylab)
slope, intercept = np.polyfit(ys, vals, 1)          # value = slope * y + intercept


def value_at(y):
    return slope * y + intercept


# markers: filled shapes in the series colours, inside the plot area
COLOURS = {'2022 methodology': (0.141, 0.333, 0.816), '2023 methodology': (0.902, 0.569, 0.22)}
markers = []
for d in pg.get_drawings():
    f = d.get('fill')
    if not f:
        continue
    for name, col in COLOURS.items():
        if all(abs(a - b) < 0.01 for a, b in zip(f, col)):
            r = d['rect']
            cx, cy = (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2
            if r.width < 14 and r.height < 14 and 95 < cx < 470 and 215 < cy < 425:
                markers.append((name, cx, cy))
assert len(markers) == 12, 'expected 6 markers per series, found %d' % len(markers)

# value labels: numbers with a thousands dot that are not axis labels, inside the plot
labels = [(float(w[4].replace('.', '')), center(w)) for w in words
          if re.fullmatch(r'\d{1,3}\.\d{3}', w[4]) and 95 < center(w)[0] < 470 and 215 < center(w)[1] < 425
          and not re.fullmatch(r'\d{2,3}\.000', w[4])]
assert len(labels) == 12, 'expected 12 value labels, found %d' % len(labels)

# Pair each year's two labels with its two markers. Two things identify the series: the marker colour
# (legend: blue diamond = 2022 methodology, orange square = 2023 methodology), and the height at which the
# printed value should sit. When two markers lie within a few points of each other (2018) the labels'
# placement settles it: this chart prints orange-series labels ABOVE their markers and blue-series labels
# BELOW them, in all ten unambiguous cases.
import itertools
ypred = lambda v: (v - intercept) / slope            # y position the axis implies for a value
by_year_m, by_year_l = {}, {}
for m in markers:
    by_year_m.setdefault(min(years, key=lambda yy: abs(years[yy] - m[1])), []).append(m)
for val, (lx, ly) in labels:
    by_year_l.setdefault(min(years, key=lambda yy: abs(years[yy] - lx)), []).append((val, lx, ly))
rows = []
for year in sorted(years):
    ms, ls = by_year_m[year], by_year_l[year]
    assert len(ms) == 2 and len(ls) == 2, (year, ms, ls)
    best = None
    for perm in itertools.permutations(ls):
        cost = 0.0
        for (name, mx, my), (val, lx, ly) in zip(ms, perm):
            cost += abs(my - ypred(val))
            if name.startswith('2023') and ly > my + 2:
                cost += 20          # an orange-series label is printed above its marker
            if name.startswith('2022') and ly < my - 2:
                cost += 20          # a blue-series label is printed below its marker
        if best is None or cost < best[0]:
            best = (cost, perm)
    for (name, mx, my), (val, lx, ly) in zip(ms, best[1]):
        rows.append(dict(source='INE/SERMIG Sintesis 2023', page=PAGE, series=name, year=year, value_printed=int(val),
                         value_from_marker_height=int(round(value_at(my), -2)),
                         height_agrees=abs(my - ypred(val)) <= 5.0))      # points; 5 pt is about 10,000 persons
chart = pd.DataFrame(rows).sort_values(['series', 'year']).reset_index(drop=True)
assert chart.height_agrees.all(), chart[~chart.height_agrees]
assert chart.groupby('series').year.apply(lambda s: sorted(s) == [2018, 2019, 2020, 2021, 2022, 2023]).all(), chart

# the panel must hold the series it says it holds, under the years the chart gives
panel = pd.read_csv(os.path.join(SITE, 'data', 'panel_final.csv'))
chl = panel[(panel.iso3 == 'CHL') & panel.irregular_stock.notna()].set_index('year')
chart['panel_value'] = [chl.irregular_stock.get(r.year) if r.series == '2023 methodology' and r.year <= 2022 else np.nan
                        for r in chart.itertuples()]
chart['panel_matches'] = [(abs(r.panel_value - r.value_printed) < 0.5) if pd.notna(r.panel_value) else None
                          for r in chart.itertuples()]
bad = chart[chart.panel_matches == False]                                  # noqa: E712
chart.to_csv(os.path.join(SITE, 'verification', 'source_chart_checks.csv'), index=False, encoding='utf-8-sig')
print(chart.to_string(index=False))
if len(bad):
    print('\nDISAGREE: the panel does not hold the chart value for its year:\n%s' % bad.to_string(index=False))
    sys.exit(1)
print('\nChile 2018-2022: the panel equals the 2023-methodology series of the chart, year by year.')
