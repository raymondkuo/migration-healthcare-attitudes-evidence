# -*- coding: utf-8 -*-
"""The Italy entry asserted that ismu.org "returns HTTP 403 to every automated client
and to a real browser". Re-checked on 2026-08-18 that is not true: a direct request is
answered with the full page, and only a browser-shaped request meets the 403 bot wall.
Both press releases were retrieved and both state the figures this archive publishes.

Correct the claim in both languages, and record that the originally cited pages are now
archived here as corroboration."""
import os
import pandas as pd

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(SITE, 'data')

NEW = {
 'issue': 'ismu.org serves an HTTP 403 bot wall to browser-shaped requests, so the cited '
          'press releases could not be captured as live page renders.',
 'issue_zh': 'ismu.org 對瀏覽器型式的請求回傳 HTTP 403 機器人阻擋頁，'
             '因此所引用之新聞稿無法以即時網頁繪製方式擷取。',
 'evidence': 'Checked 2026-08-17 from two clients and re-checked 2026-08-18: a direct request '
             'returns the full page (HTTP 200), a headless browser returns 403 "Access Blocked".',
 'evidence_zh': '2026-08-17 自兩種用戶端檢查，並於 2026-08-18 重新檢查：'
                '直接請求可取得完整頁面（HTTP 200），無頭瀏覽器則回傳 403「Access Blocked」。',
 'action': 'Cited to ISMU\'s own machine-readable series, which reproduces every Italian value '
           'for 2010-2021 exactly. That series ends at 2021, so 2022 (506,000) is cited to the '
           'XXVIII Rapporto ISMU 2022, which states it against 519,000 for the year before. '
           'On 2026-08-18 both originally cited press releases were retrieved and do state the '
           'same figures - 562mila for 2019, and 519mila against 517mila for 2021 and 2020 - '
           'so they are archived here as corroboration, with their visual rendered from the '
           'archived copy because the live page cannot be rendered.',
 'action_zh': '改引 ISMU 自行發布之機器可讀序列，該序列完全重現 2010–2021 年每一筆義大利數值。'
              '該序列止於 2021 年，故 2022 年（506,000）改引第 XXVIII 號 ISMU 移民報告，'
              '其中載明該數字並與前一年之 519,000 對照。'
              '2026-08-18 已成功取得原引用之兩份新聞稿，其內容確載相同數字'
              '——2019 年為 562mila，2021 與 2020 年為 519mila 對 517mila'
              '——故一併存檔作為佐證；因即時頁面無法繪製，其視覺檔改由存檔副本產生。',
}

p = os.path.join(D, 'known_issues.csv')
k = pd.read_csv(p).fillna('')
m = (k.scope == 'Italy') & (k.variable == 'sources')
assert m.sum() == 1, 'expected one Italy/sources row, found %d' % m.sum()
for col, val in NEW.items():
    k.loc[m, col] = val
k.to_csv(p, index=False, encoding='utf-8-sig')
print('known_issues.csv: Italy/sources corrected in both languages')

rp = os.path.join(D, 'source_register.csv')
reg = pd.read_csv(rp).fillna('')
m2 = reg.superseded_source_url.astype(str).str.contains('ismu.org', na=False)
reg.loc[m2, 'note'] = (
    "Cited to ISMU's own machine-readable series, which reproduces every year exactly. "
    "The press release originally cited serves a 403 bot wall to a browser; retrieved by "
    "direct request on 2026-08-18 it states the same figure, and is archived here too.")
reg.to_csv(rp, index=False, encoding='utf-8-sig')
print('source_register.csv: %d ISMU note(s) corrected' % int(m2.sum()))

for col in ('issue', 'action'):
    print('\n%s: %s...' % (col, NEW[col][:110]))
