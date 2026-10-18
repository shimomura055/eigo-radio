# RLCT Stage 1b openai_copyright 集計

MEASURED(実測): 全行 dry_run=false かつ usage_basis=OFFICIAL_API_RESPONSE。

| 記事 | 方式 | status | Trial費用JPY(LLM/検索/計) | 検索呼出(種別) | クエリ | 選定Fact | Jaccard | 再選定/確認パス | 再選定B3/確認B3 JPY | 降格 | 昇格 | 中心AMBIG | 契約 | 本番換算JPY | 削減JPY | 削減% |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| openai_copyright | 従来(M0) | COMPLETED | 6.389/0.0/6.389 | 0 {} | 0 | F2,F4,F6,F7,F8 | 1.0 | None/None | 0/0 |  |  | 0 | True | 38.22 | 0.0 | 0.0 |
| openai_copyright | 従来再実行(M0b) | COMPLETED | 7.296/0.0/7.296 | 0 {} | 0 | F2,F4,F6,F7,F8 | 1.0 | None/None | 0/0 |  |  | 0 | True | 39.127 | -0.907 | -2.4 |
| openai_copyright | 案1 | COMPLETED | 8.634/9.6/18.234 | 6 {'search': 3, 'open_page': 2, 'unknown': 1} | 12 | F2,F4,F6,F7,F8 | 1.0 | None/None | 0/0 | F8 |  | 1 | True | 41.055 | -2.835 | -7.4 |
| openai_copyright | 案2 | COMPLETED | 15.713/11.2/26.913 | 7 {'search': 4, 'open_page': 2, 'find_in_page': 1} | 15 | F2,F4,F6,F7,F8 | 1.0 | 0/1 | 0/7.099 | F8 |  | 0 | True | 49.734 | -11.514 | -30.1 |
| openai_copyright | 案1+2 | COMPLETED | 1.506/14.4/15.906 | 9 {'search': 3, 'open_page': 5, 'find_in_page': 1} | 12 | F2,F4,F6,F7,F8 | 1.0 | 0/0 | 0/0 |  |  | 0 | True | 46.064 | -7.844 | -20.5 |
