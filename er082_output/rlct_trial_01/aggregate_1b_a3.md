# RLCT Stage 1b 記事3 central_bank_mortgage

MEASURED(実測): 全行 dry_run=false かつ usage_basis=OFFICIAL_API_RESPONSE。

| 記事 | 方式 | status | Trial費用JPY(LLM/検索/計) | 検索呼出(種別) | クエリ | 選定Fact | Jaccard | 再選定/確認パス | 再選定B3/確認B3 JPY | 降格 | 昇格 | 中心AMBIG | 契約 | 本番換算JPY | 削減JPY | 削減% |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| central_bank_mortgage | 従来(M0) | COMPLETED | 8.06/0.0/8.06 | 0 {} | 0 | F002,F003,F006,F008,F010 | 1.0 | None/None | 0/0 |  |  | 0 | True | 30.392 | 0.0 | 0.0 |
| central_bank_mortgage | 従来再実行(M0b) | COMPLETED | 8.564/0.0/8.564 | 0 {} | 0 | F002,F003,F007,F008,F010 | 0.667 | None/None | 0/0 |  |  | 0 | True | 30.896 | -0.504 | -1.7 |
| central_bank_mortgage | 案1 | COMPLETED | 11.402/6.4/17.802 | 4 {'search': 1, 'open_page': 2, 'find_in_page': 1} | 10 | F001,F002,F003,F006,F008 | 0.667 | None/None | 0/0 |  |  | 0 | True | 32.749 | -2.357 | -7.8 |
| central_bank_mortgage | 案2 | COMPLETED | 8.266/4.8/13.066 | 3 {'search': 1, 'open_page': 2} | 4 | F002,F003,F006,F008,F010 | 1.0 | 0/0 | 0/0 |  |  | 0 | True | 28.013 | 2.379 | 7.8 |
| central_bank_mortgage | 案1+2 | COMPLETED | 0.565/3.2/3.765 | 2 {'search': 1, 'open_page': 1} | 4 | F002,F003,F006,F008,F010 | 1.0 | 0/0 | 0/0 |  |  | 0 | True | 26.293 | 4.099 | 13.5 |
