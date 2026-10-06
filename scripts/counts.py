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
