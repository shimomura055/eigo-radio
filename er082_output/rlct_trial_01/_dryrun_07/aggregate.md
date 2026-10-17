# dryrun_07

SYNTHETIC(stub)。dry-runの値であり、実測ではない。

| 記事 | 方式 | status | Trial費用JPY(LLM/検索/計) | 検索呼出(種別) | クエリ | 選定Fact | Jaccard | 再選定/確認パス | 再選定B3/確認B3 JPY | 降格 | 昇格 | 中心AMBIG | 契約 | 本番換算JPY | 削減JPY | 削減% |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| coffee_prices | 案2 | COMPLETED | 9.767/6.4/16.167 | 4 {'search': 4} | 4 | F02,F07,F09,F11 | 0.0 | 0/1 | 0/4.614 |  |  | 0 | True | 36.014 | None | None |
| coffee_prices | 案1+2 | COMPLETED | 5.336/6.4/11.736 | 4 {'search': 4} | 4 | F02,F07,F09,F11 | 0.0 | 0/1 | 0/4.614 |  |  | 0 | True | 36.015 | None | None |
| inbound_tourism | 案2(修正前・参考) | COMPLETED | 9.804/8.0/17.804 | 5 {'search': 5} | 5 | F01,F02,F03,F06 | 0.0 | 1/0 | 4.58/0 |  |  | 1 | False | 46.365 | None | None |
| inbound_tourism | 案1+2(修正前・参考) | COMPLETED | 5.39/8.0/13.39 | 5 {'search': 5} | 5 | F01,F02,F03,F06 | 0.0 | 1/0 | 4.58/0 |  |  | 1 | False | 46.366 | None | None |
| inbound_tourism | 案2(確認パス後) | COMPLETED | 9.994/3.2/13.194 | 2 {'search': 2} | 2 | F01,F02,F03,F06 | 0.0 | 0/2 | 0/9.451 |  | F04,F05 | 1 | False | 59.533 | None | None |
| inbound_tourism | 案1+2(確認パス後) | COMPLETED | 10.004/3.2/13.204 | 2 {'search': 2} | 2 | F01,F02,F03,F06 | 0.0 | 0/2 | 0/9.46 |  | F04,F05 | 1 | False | 55.181 | None | None |
| streaming_price | 案2 | COMPLETED | 8.541/9.6/18.141 | 6 {'search': 6} | 6 | F01,F02,F03,F04,F06,F07 | 0.0 | 0/1 | 0/3.937 |  |  | 2 | True | 39.818 | None | None |
| streaming_price | 案1+2 | COMPLETED | 4.839/9.6/14.439 | 6 {'search': 6} | 6 | F01,F02,F03,F04,F06,F07 | 0.0 | 0/1 | 0/3.937 |  |  | 2 | True | 39.819 | None | None |
| openai_copyright | 案2 | COMPLETED | 4.653/8.0/12.653 | 5 {'search': 5} | 5 | F2,F4,F6,F7,F8 | 0.0 | 0/0 | 0/0 |  |  | 0 | True | 35.474 | None | None |
| openai_copyright | 案1+2 | COMPLETED | 0.815/8.0/8.815 | 5 {'search': 5} | 5 | F2,F4,F6,F7,F8 | 0.0 | 0/0 | 0/0 |  |  | 0 | True | 35.475 | None | None |
| central_bank_mortgage | 案2 | COMPLETED | 4.832/9.6/14.432 | 6 {'search': 6} | 6 | F001,F002,F003,F007,F008,F010 | 0.0 | 0/0 | 0/0 |  |  | 0 | True | 29.379 | None | None |
| central_bank_mortgage | 案1+2 | COMPLETED | 5.064/9.6/14.664 | 6 {'search': 6} | 6 | F001,F002,F003,F007,F008,F010 | 0.0 | 0/1 | 0/4.166 | F002 |  | 1 | True | 33.545 | None | None |
