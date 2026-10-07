# -*- coding: utf-8 -*-
"""Counts that page text quotes, computed from the data files.

The first version of the site typed these numbers into the prose (156 evidence pages, 78
citations, 160 URLs ...). They went stale as soon as the archive grew, so every count that
the prose quotes is read from here instead. The definitions mirror the tables on the pages."""
import os
import pandas as pd

_D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
_reg = pd.read_csv(os.path.join(_D, 'source_register.csv')).fillna('')
_non = _reg[_reg.retrieval != 'VERIFIED_API']
_docs = _non.drop_duplicates(subset=['iso3', 'source_url'])
_vlog = pd.read_csv(os.path.join(_D, 'verification_log.csv'))
_ovl = pd.read_csv(os.path.join(_D, 'extension_overlap_check.csv'))

N_EVIDENCE = len(pd.read_csv(os.path.join(_D, 'evidence_index.csv')))
N_ALL_URLS = int(_reg.source_url.nunique())
N_DOC_URLS = int(_non.source_url.nunique())
N_CITES = len(_docs)                                    # country-source document citations
N_CITES_HELD = int((~_docs.outcome.astype(str).str.startswith('NOT_RETRIEVED')).sum())
N_CHECKS = len(_vlog)
N_RECHECKED = int(_ovl.cells_compared.sum())

# ---------------------------------------------------------------- statements about the panel itself
_panel = pd.read_csv(os.path.join(_D, 'panel_final.csv'))
N_ROWS = len(_panel)
N_FN_COUNTRIES = int(_panel[_panel.foreign_nationals.notna()].iso3.nunique())
N_FB_COUNTRIES = int(_panel[_panel.foreign_born.notna()].iso3.nunique())
_late = _panel[_panel.year >= 2010]
IRR_STOCK_PCT = 100.0 * float(_late.irregular_stock.notna().mean())          # 2010-2022 denominator
_gap = _panel.dropna(subset=['population_wb_vs_unwpp_pct'])
GAP3_ALL = int((_gap.population_wb_vs_unwpp_pct.abs() > 3).sum())
GAP3_LATE = int((_gap[_gap.year >= 2010].population_wb_vs_unwpp_pct.abs() > 3).sum())
_neg = _gap.loc[_gap.population_wb_vs_unwpp_pct.idxmin()]
_pos = _gap.loc[_gap.population_wb_vs_unwpp_pct.idxmax()]
GAP_NEG = (_neg.country, float(_neg.population_wb_vs_unwpp_pct), int(_neg.year))
GAP_POS = (_pos.country, float(_pos.population_wb_vs_unwpp_pct), int(_pos.year))
N_WB = int((_panel.population.notna() & (_panel.iso3 != 'TWN')).sum())
N_IRR_C = int(_panel[_panel.irregular_stock.notna()].iso3.nunique())
N_OVS_C = int(_panel[_panel.irregular_proxy_overstayers.notna()].iso3.nunique())
N_DET_C = int(_panel[_panel.irregular_proxy_detections.notna()].iso3.nunique())
N_BELOW = int((_panel.foreign_born.notna() & _panel.foreign_nationals.notna()
               & (_panel.foreign_born < _panel.foreign_nationals)).sum())
