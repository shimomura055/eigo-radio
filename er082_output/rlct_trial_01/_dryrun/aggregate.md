# RLCT dry-run集計(SYNTHETIC・stub)

dry-runの値はSYNTHETIC(stub)。実測ではない。

| 記事 | 方式 | status | Trial費用JPY(LLM/検索/計) | 検索呼出(種別) | クエリ | 選定Fact | Jaccard | 再選定 | 降格 | 昇格 | 中心AMBIG | 契約 | 本番換算JPY | 削減JPY | 削減% |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| coffee_prices | M0 | COMPLETED | 0.0/0.0/0.0 | 0 {} | 0 | F02,F07,F09,F11 | 1.0 | None |  |  | 1 | True | 55.919 | 0.0 | 0.0 |
| coffee_prices | M0b | COMPLETED | 4.35/0.0/4.35 | 0 {} | 0 | F02,F07,F09,F11 | 1.0 | None |  |  | 1 | True | 49.332 | 6.587 | 11.8 |
| coffee_prices | M0p | COMPLETED | 1.872/27.2/29.072 | 17 {'search': 17} | 17 |  | 0.0 | None |  |  | None | None | None | None | None |
| coffee_prices | M1 | COMPLETED | 6.233/27.2/33.433 | 17 {'search': 17} | 17 | F02,F07,F09,F11 | 1.0 | None | F05 |  | 1 | True | 53.28 | 2.639 | 4.7 |
| coffee_prices | M2 | COMPLETED | 5.153/6.4/11.553 | 4 {'search': 4} | 4 | F02,F07,F09,F11 | 1.0 | 0 |  |  | 0 | True | 31.4 | 24.519 | 43.8 |
| coffee_prices | M3 | COMPLETED | 0.722/6.4/7.122 | 4 {'search': 4} | 4 | F02,F07,F09,F11 | 1.0 | 0 |  |  | 0 | True | 31.401 | 24.518 | 43.8 |
| inbound_tourism | M0 | COMPLETED | 4.251/0.0/4.251 | 0 {} | 0 | F01,F02,F03,F06 | 1.0 | None |  |  | 2 | False | 61.069 | 0.0 | 0.0 |
| inbound_tourism | M0b | COMPLETED | 4.251/0.0/4.251 | 0 {} | 0 | F01,F02,F03,F06 | 1.0 | None |  |  | 2 | False | 61.069 | 0.0 | 0.0 |
| inbound_tourism | M0p | COMPLETED | 1.696/24.0/25.696 | 15 {'search': 15} | 15 |  | 0.0 | None |  |  | None | None | None | None | None |
| inbound_tourism | M1 | COMPLETED | 5.947/24.0/29.947 | 15 {'search': 15} | 15 | F01,F02,F03,F06 | 1.0 | None | F07 |  | 3 | False | 58.508 | 2.561 | 4.2 |
| inbound_tourism | M2 | COMPLETED | 9.791/8.0/17.791 | 5 {'search': 5} | 5 | F01,F02,F03,F06 | 1.0 | 1 |  |  | 1 | False | 46.352 | 14.717 | 24.1 |
| inbound_tourism | M3 | COMPLETED | 5.377/8.0/13.377 | 5 {'search': 5} | 5 | F01,F02,F03,F06 | 1.0 | 1 |  |  | 1 | False | 46.353 | 14.716 | 24.1 |
| streaming_price | M0 | COMPLETED | 3.666/0.0/3.666 | 0 {} | 0 | F01,F02,F03,F04,F06,F07 | 1.0 | None |  |  | 2 | True | 38.126 | 0.0 | 0.0 |
| streaming_price | M0b | COMPLETED | 3.666/0.0/3.666 | 0 {} | 0 | F01,F02,F03,F04,F06,F07 | 1.0 | None |  |  | 2 | True | 38.126 | 0.0 | 0.0 |
| streaming_price | M0p | COMPLETED | 0.989/11.2/12.189 | 7 {'search': 7} | 7 |  | 0.0 | None |  |  | None | None | None | None | None |
| streaming_price | M1 | COMPLETED | 4.666/11.2/15.866 | 7 {'search': 7} | 7 | F01,F02,F03,F04,F06,F07 | 1.0 | None | F05 |  | 3 | True | 37.543 | 0.583 | 1.5 |
| streaming_price | M2 | COMPLETED | 4.604/9.6/14.204 | 6 {'search': 6} | 6 | F01,F02,F03,F04,F06,F07 | 1.0 | 0 |  |  | 2 | True | 35.881 | 2.245 | 5.9 |
| streaming_price | M3 | COMPLETED | 0.902/9.6/10.502 | 6 {'search': 6} | 6 | F01,F02,F03,F04,F06,F07 | 1.0 | 0 |  |  | 2 | True | 35.882 | 2.244 | 5.9 |
| openai_copyright | M0 | COMPLETED | 3.791/0.0/3.791 | 0 {} | 0 | F2,F4,F6,F7,F8 | 1.0 | None |  |  | 0 | True | 35.622 | 0.0 | 0.0 |
| openai_copyright | M0b | COMPLETED | 3.791/0.0/3.791 | 0 {} | 0 | F2,F4,F6,F7,F8 | 1.0 | None |  |  | 0 | True | 35.622 | 0.0 | 0.0 |
| openai_copyright | M0p | COMPLETED | 1.081/12.8/13.881 | 8 {'search': 8} | 8 |  | 0.0 | None |  |  | None | None | None | None | None |
| openai_copyright | M1 | COMPLETED | 4.873/12.8/17.673 | 8 {'search': 8} | 8 | F2,F4,F6,F7,F8 | 1.0 | None |  |  | 0 | True | 40.494 | -4.872 | -13.7 |
| openai_copyright | M2 | COMPLETED | 4.653/8.0/12.653 | 5 {'search': 5} | 5 | F2,F4,F6,F7,F8 | 1.0 | 0 |  |  | 0 | True | 35.474 | 0.148 | 0.4 |
| openai_copyright | M3 | COMPLETED | 0.815/8.0/8.815 | 5 {'search': 5} | 5 | F2,F4,F6,F7,F8 | 1.0 | 0 |  |  | 0 | True | 35.475 | 0.147 | 0.4 |
| central_bank_mortgage | M0 | COMPLETED | 3.901/0.0/3.901 | 0 {} | 0 | F001,F002,F003,F007,F008,F010 | 1.0 | None |  |  | 0 | True | 26.233 | 0.0 | 0.0 |
| central_bank_mortgage | M0b | COMPLETED | 3.901/0.0/3.901 | 0 {} | 0 | F001,F002,F003,F007,F008,F010 | 1.0 | None |  |  | 0 | True | 26.233 | 0.0 | 0.0 |
| central_bank_mortgage | M0p | COMPLETED | 1.341/17.6/18.941 | 11 {'search': 11} | 11 |  | 0.0 | None |  |  | None | None | None | None | None |
| central_bank_mortgage | M1 | COMPLETED | 5.269/17.6/22.869 | 11 {'search': 11} | 11 | F001,F002,F003,F007,F008,F010 | 1.0 | None | F002,F011 |  | 1 | True | 37.816 | -11.583 | -44.2 |
| central_bank_mortgage | M2 | COMPLETED | 4.832/9.6/14.432 | 6 {'search': 6} | 6 | F001,F002,F003,F007,F008,F010 | 1.0 | 0 |  |  | 0 | True | 29.379 | -3.146 | -12.0 |
| central_bank_mortgage | M3 | COMPLETED | 0.898/9.6/10.498 | 6 {'search': 6} | 6 | F001,F002,F003,F007,F008,F010 | 1.0 | 0 | F002 |  | 1 | True | 29.379 | -3.146 | -12.0 |
