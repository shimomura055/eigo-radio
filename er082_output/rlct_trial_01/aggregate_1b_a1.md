# RLCT 1b 記事1(streaming_price) 集計

MEASURED(実測): 全行 dry_run=false かつ usage_basis=OFFICIAL_API_RESPONSE。

| 記事 | 方式 | status | Trial費用JPY(LLM/検索/計) | 検索呼出(種別) | クエリ | 選定Fact | Jaccard | 再選定/確認パス | 再選定B3/確認B3 JPY | 降格 | 昇格 | 中心AMBIG | 契約 | 本番換算JPY | 削減JPY | 削減% |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| streaming_price | 従来(M0) | COMPLETED | 5.735/0.0/5.735 | 0 {} | 0 | F02,F03,F04,F07 | 1.0 | None/None | 0/0 |  |  | 1 | True | 40.195 | 0.0 | 0.0 |
| streaming_price | 従来再実行(M0b) | COMPLETED | 6.487/0.0/6.487 | 0 {} | 0 | F01,F02,F03,F04,F07 | 0.8 | None/None | 0/0 |  |  | 1 | True | 40.947 | -0.752 | -1.9 |
| streaming_price | 同日再検証のみ(M0p) | COMPLETED | 1.263/9.6/10.863 | 6 {'search': 5, 'open_page': 1} | 18 |  | 0.0 | None/None | 0/0 | F04 | F07 | None | None | None | None | None |
| streaming_price | 案1 | COMPLETED | 7.728/8.0/15.728 | 5 {'search': 3, 'open_page': 1, 'find_in_page': 1} | 12 | F02,F03,F04,F06,F07 | 0.8 | None/None | 0/0 | F04 | F07 | 0 | True | 37.405 | 2.79 | 6.9 |
| streaming_price | 案2 | COMPLETED | 15.831/14.4/30.231 | 9 {'search': 6, 'open_page': 3} | 21 | F02,F03,F04,F07 | 1.0 | 0/1 | 0/7.189 | F04 | F07 | 1 | True | 51.908 | -11.713 | -29.1 |
| streaming_price | 案1+2 | COMPLETED | 7.484/9.6/17.084 | 6 {'search': 4, 'open_page': 1, 'find_in_page': 1} | 23 | F02,F03,F04 | 0.75 | 1/0 | 5.806/0 |  |  | 1 | True | 45.73 | -5.535 | -13.8 |
