# RLCT Trial 集計

MEASURED(実測): 全行 dry_run=false かつ usage_basis=OFFICIAL_API_RESPONSE。

| 記事 | 方式 | status | Trial費用JPY(LLM/検索/計) | 検索呼出(種別) | クエリ | 選定Fact | Jaccard | 再選定/確認パス | 再選定B3/確認B3 JPY | 降格 | 昇格 | 中心AMBIG | 契約 | 本番換算JPY | 削減JPY | 削減% |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| coffee_prices | 従来(M0) | COMPLETED | 0.0/0.0/0.0 | 0 {} | 0 | F02,F07,F09,F11 | 1.0 | None/None | 0/0 |  |  | 1 | True | 55.919 | 0.0 | 0.0 |
| coffee_prices | 従来再実行(M0b) | COMPLETED | 12.695/0.0/12.695 | 0 {} | 0 | F02,F07,F09,F11 | 1.0 | None/None | 0/0 |  |  | 2 | True | 57.677 | -1.758 | -3.1 |
| coffee_prices | 同日再検証のみ(M0p) | COMPLETED | 1.996/16.0/17.996 | 10 {'search': 4, 'open_page': 4, 'find_in_page': 2} | 16 |  | 0.0 | None/None | 0/0 | F02 | F12,F17 | None | None | None | None | None |
| coffee_prices | 案1 | COMPLETED | 12.956/20.8/33.756 | 13 {'search': 6, 'open_page': 6, 'find_in_page': 1} | 23 | F02,F07,F09,F15 | 0.6 | None/None | 0/0 |  | F12,F16,F17 | 1 | True | 53.603 | 2.316 | 4.1 |
| coffee_prices | 案2 | COMPLETED | 23.781/8.0/31.781 | 5 {'search': 3, 'open_page': 1, 'find_in_page': 1} | 10 | F01,F09,F15 | 0.167 | 1/None | 11.346/0 |  |  | 0 | True | 51.628 | 4.291 | 7.7 |
| coffee_prices | 案1+2 | COMPLETED | 12.003/6.4/18.403 | 4 {'search': 2, 'open_page': 1, 'find_in_page': 1} | 7 | F01,F09,F10,F15 | 0.143 | 1/None | 11.055/0 |  |  | 0 | True | 49.65 | 6.269 | 11.2 |
| inbound_tourism | 従来(M0) | COMPLETED | 8.465/0.0/8.465 | 0 {} | 0 | F01,F02,F09 | 1.0 | None/None | 0/0 |  |  | 1 | True | 65.283 | 0.0 | 0.0 |
| inbound_tourism | 従来再実行(M0b) | COMPLETED | 8.328/0.0/8.328 | 0 {} | 0 | F01,F02,F03,F09 | 0.75 | None/None | 0/0 |  |  | 2 | False | 65.146 | 0.137 | 0.2 |
| inbound_tourism | 同日再検証のみ(M0p) | COMPLETED | 2.326/22.4/24.726 | 14 {'search': 5, 'open_page': 8, 'find_in_page': 1} | 17 |  | 0.0 | None/None | 0/0 |  | F04 | None | None | None | None | None |
| inbound_tourism | 案1 | COMPLETED | 12.271/17.6/29.871 | 11 {'search': 5, 'open_page': 4, 'find_in_page': 2} | 20 | F01,F02,F04,F05 | 0.4 | None/None | 0/0 |  | F04,F05,F12 | 2 | False | 58.432 | 6.851 | 10.5 |
| inbound_tourism | 案2(修正前・参考) | COMPLETED | 11.378/6.4/17.778 | 4 {'search': 2, 'open_page': 1, 'find_in_page': 1} | 7 | F01,F02,F04,F05 | 0.4 | 0/None | 0/0 |  | F04,F05 | 1 | False | 46.339 | 18.944 | 29.0 |
| inbound_tourism | 案1+2(修正前・参考) | COMPLETED | 1.001/8.0/9.001 | 5 {'search': 3, 'open_page': 2} | 9 | F01,F02,F04,F05 | 0.4 | 0/None | 0/0 |  | F04,F05 | 1 | False | 48.029 | 17.254 | 26.4 |
| inbound_tourism | 案2(確認パス後) | COMPLETED | 9.72/0.0/9.72 | 0 {} | 0 | F01,F02,F04,F05 | 0.4 | 0/1 | 0/9.72 |  | F04,F05 | 1 | False | 56.059 | 9.224 | 14.1 |
| inbound_tourism | 案1+2(確認パス後) | COMPLETED | 10.289/0.0/10.289 | 0 {} | 0 | F01,F02,F04,F05 | 0.4 | 0/1 | 0/10.289 |  | F04,F05 | 1 | False | 58.318 | 6.965 | 10.7 |
