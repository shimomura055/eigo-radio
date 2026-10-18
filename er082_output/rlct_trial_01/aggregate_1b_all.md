# RLCT Stage 1b 3記事合計

MEASURED(実測): 全行 dry_run=false かつ usage_basis=OFFICIAL_API_RESPONSE。

| 記事 | 方式 | status | Trial費用JPY(LLM/検索/計) | 検索呼出(種別) | クエリ | 選定Fact | Jaccard | 再選定/確認パス | 再選定B3/確認B3 JPY | 降格 | 昇格 | 中心AMBIG | 契約 | 本番換算JPY | 削減JPY | 削減% |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| streaming_price | 従来(M0) | COMPLETED | 5.735/0.0/5.735 | 0 {} | 0 | F02,F03,F04,F07 | 1.0 | None/None | 0/0 |  |  | 1 | True | 40.195 | 0.0 | 0.0 |
| streaming_price | 従来再実行(M0b) | COMPLETED | 6.487/0.0/6.487 | 0 {} | 0 | F01,F02,F03,F04,F07 | 0.8 | None/None | 0/0 |  |  | 1 | True | 40.947 | -0.752 | -1.9 |
| streaming_price | 同日再検証のみ(M0p) | COMPLETED | 1.263/9.6/10.863 | 6 {'search': 5, 'open_page': 1} | 18 |  | 0.0 | None/None | 0/0 | F04 | F07 | None | None | None | None | None |
| streaming_price | 案1 | COMPLETED | 7.728/8.0/15.728 | 5 {'search': 3, 'open_page': 1, 'find_in_page': 1} | 12 | F02,F03,F04,F06,F07 | 0.8 | None/None | 0/0 | F04 | F07 | 0 | True | 37.405 | 2.79 | 6.9 |
| streaming_price | 案2 | COMPLETED | 15.831/14.4/30.231 | 9 {'search': 6, 'open_page': 3} | 21 | F02,F03,F04,F07 | 1.0 | 0/1 | 0/7.189 | F04 | F07 | 1 | True | 51.908 | -11.713 | -29.1 |
| streaming_price | 案1+2 | COMPLETED | 7.484/9.6/17.084 | 6 {'search': 4, 'open_page': 1, 'find_in_page': 1} | 23 | F02,F03,F04 | 0.75 | 1/0 | 5.806/0 |  |  | 1 | True | 45.73 | -5.535 | -13.8 |
| openai_copyright | 従来(M0) | COMPLETED | 6.389/0.0/6.389 | 0 {} | 0 | F2,F4,F6,F7,F8 | 1.0 | None/None | 0/0 |  |  | 0 | True | 38.22 | 0.0 | 0.0 |
| openai_copyright | 従来再実行(M0b) | COMPLETED | 7.296/0.0/7.296 | 0 {} | 0 | F2,F4,F6,F7,F8 | 1.0 | None/None | 0/0 |  |  | 0 | True | 39.127 | -0.907 | -2.4 |
| openai_copyright | 案1 | COMPLETED | 8.634/9.6/18.234 | 6 {'search': 3, 'open_page': 2, 'unknown': 1} | 12 | F2,F4,F6,F7,F8 | 1.0 | None/None | 0/0 | F8 |  | 1 | True | 41.055 | -2.835 | -7.4 |
| openai_copyright | 案2 | COMPLETED | 15.713/11.2/26.913 | 7 {'search': 4, 'open_page': 2, 'find_in_page': 1} | 15 | F2,F4,F6,F7,F8 | 1.0 | 0/1 | 0/7.099 | F8 |  | 0 | True | 49.734 | -11.514 | -30.1 |
| openai_copyright | 案1+2 | COMPLETED | 1.506/14.4/15.906 | 9 {'search': 3, 'open_page': 5, 'find_in_page': 1} | 12 | F2,F4,F6,F7,F8 | 1.0 | 0/0 | 0/0 |  |  | 0 | True | 46.064 | -7.844 | -20.5 |
| central_bank_mortgage | 従来(M0) | COMPLETED | 8.06/0.0/8.06 | 0 {} | 0 | F002,F003,F006,F008,F010 | 1.0 | None/None | 0/0 |  |  | 0 | True | 30.392 | 0.0 | 0.0 |
| central_bank_mortgage | 従来再実行(M0b) | COMPLETED | 8.564/0.0/8.564 | 0 {} | 0 | F002,F003,F007,F008,F010 | 0.667 | None/None | 0/0 |  |  | 0 | True | 30.896 | -0.504 | -1.7 |
| central_bank_mortgage | 案1 | COMPLETED | 11.402/6.4/17.802 | 4 {'search': 1, 'open_page': 2, 'find_in_page': 1} | 10 | F001,F002,F003,F006,F008 | 0.667 | None/None | 0/0 |  |  | 0 | True | 32.749 | -2.357 | -7.8 |
| central_bank_mortgage | 案2 | COMPLETED | 8.266/4.8/13.066 | 3 {'search': 1, 'open_page': 2} | 4 | F002,F003,F006,F008,F010 | 1.0 | 0/0 | 0/0 |  |  | 0 | True | 28.013 | 2.379 | 7.8 |
| central_bank_mortgage | 案1+2 | COMPLETED | 0.565/3.2/3.765 | 2 {'search': 1, 'open_page': 1} | 4 | F002,F003,F006,F008,F010 | 1.0 | 0/0 | 0/0 |  |  | 0 | True | 26.293 | 4.099 | 13.5 |
