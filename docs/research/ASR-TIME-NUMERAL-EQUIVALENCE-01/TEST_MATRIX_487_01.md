# TEST_MATRIX_487_01(OPEN-487 `one hundred thirty people`↔`1:30 people` 誤PASS、設計段階、API 0、Production変更0)

実行器 `test_matrix_487_01.py`(判定=Primary 1本の最終state、`judge_sim_01.judge_primary`)。生データ `m487_base.json`/`m487_A.json`/`m487_B.json`(+`.txt`)。base=着手時HEAD(`base_HEAD03`)、案A=`proto_487A/`(`er006 despaced()`/冠詞除外despaceが『数字で終わるtoken+数字で始まるtoken』の境界を残す)、案B=`proto_487B/`(`er078 _compare_pair`のnum↔time kind_mismatchをUNKNOWN→DIFF)。期待: NE=PASS不可 / EQ=PASS系 / REF=観測のみ。

**期待不一致: base 11件 / 案A 2件 / 案B 5件。**(案Aの残2件はOPEN-487と無関係=`nine fifty people`↔`9 50 people`はOPEN-482の時刻形統一が意図どおり同一視[期待の置き方が誤り・設計どおり]、`1,000,000`↔`1000000`は修正前から存在する別事象[7桁以上の生数字列をliteral扱いする規則。下記X-5]。案Bの退行=`nineteen thirty`↔`19:30`等の24時間表記が現行PASSからNGに変わる。)

| # | group | canon | ASR | 期待 | base | 案A | 案B | 備考 |
|---|---|---|---|---|---|---|---|---|
| 1 | T487 | `one hundred thirty people` | `1:30 people` | NE | PASS **BAD** | NG | NG | 報告原例 |
| 2 | T487 | `1:30 people` | `one hundred thirty people` | NE | PASS **BAD** | NG | NG | 逆向き |
| 3 | T487 | `one hundred and thirty people` | `1:30 people` | NE | PASS **BAD** | NG | NG |  |
| 4 | T487 | `130 people` | `1:30 people` | NE | PASS **BAD** | NG | NG | digits<->time+名詞 |
| 5 | T487 | `It was one hundred thirty.` | `It was 1:30.` | NE | PASS **BAD** | NG | NG | 文末 |
| 6 | T487 | `one hundred twenty` | `1:20` | NE | PASS **BAD** | NG | NG |  |
| 7 | T487 | `two hundred fifteen people` | `2:15 people` | NE | PASS **BAD** | NG | NG |  |
| 8 | T487 | `I saw 130 people` | `I saw 1:30 people` | NE | PASS **BAD** | NG | NG |  |
| 9 | T487 | `one hundred thirty people` | `1 30 people` | NE | NG | NG | NG | ASRが空白区切り数字 |
| 10 | T487 | `10 30` | `1030` | NE | NG | NG | NG | 桁連結と空白区切りは別物 |
| 11 | T487 | `at 10 30` | `at 1030` | NE | NG | NG | NG |  |
| 12 | T487 | `nine fifty people` | `9 50 people` | NE | PASS **BAD** | PASS **BAD** | PASS **BAD** | 950と9 50 |
| 13 | T487 | `twenty twenty-six` | `20 26` | NE | NG | NG | NG | 年と空白区切り |
| 14 | T487 | `3 10-minute rounds` | `310 minute rounds` | NE | NG | NG | NG |  |
| 15 | EQ | `one hundred thirty people` | `130 people` | EQ | PASS | PASS | PASS |  |
| 16 | EQ | `130 people` | `one hundred thirty people` | EQ | PASS | PASS | PASS |  |
| 17 | EQ | `At ten thirty` | `At 10:30` | EQ | PASS | PASS | PASS | OPEN-482 |
| 18 | EQ | `At 10:30` | `At ten thirty` | EQ | PASS | PASS | PASS |  |
| 19 | EQ | `At 10 thirty` | `At 10:30` | EQ | PASS | PASS | PASS |  |
| 20 | EQ | `At ten thirty` | `At 10 30` | EQ | PASS | PASS | PASS |  |
| 21 | EQ | `At 1:30` | `At one thirty` | EQ | PASS | PASS | PASS |  |
| 22 | EQ | `At one thirty` | `At 1:30` | EQ | PASS | PASS | PASS |  |
| 23 | EQ | `At two fifteen` | `At 2:15` | EQ | PASS | PASS | PASS |  |
| 24 | EQ | `At nineteen thirty` | `At 19:30` | EQ | PASS | PASS | NG **BAD** | 24時間表記(現行PASS) |
| 25 | EQ | `At 19:30` | `At nineteen thirty` | EQ | PASS | PASS | NG **BAD** |  |
| 26 | EQ | `at fourteen fifteen` | `at 14:15` | EQ | PASS | PASS | NG **BAD** |  |
| 27 | EQ | `In nineteen ninety nine` | `In 1999` | EQ | PASS | PASS | PASS | 年号 |
| 28 | EQ | `In 1999` | `In nineteen ninety nine` | EQ | PASS | PASS | PASS |  |
| 29 | EQ | `In twenty twenty six` | `In 2026` | EQ | PASS | PASS | PASS |  |
| 30 | EQ | `In twenty twenty` | `In 2020` | EQ | PASS | PASS | PASS |  |
| 31 | EQ | `between 9 and 11` | `between nine and eleven` | EQ | NG **BAD** | PASS | PASS | OPEN-489 |
| 32 | EQ | `one hundred and ten` | `110` | EQ | PASS | PASS | PASS |  |
| 33 | EQ | `two thousand and five` | `2005` | EQ | PASS | PASS | PASS |  |
| 34 | EQ | `ten thirty five` | `10:35` | EQ | PASS | PASS | PASS |  |
| 35 | EQ | `ten thirty-five` | `1035` | REF | NG | NG | NG | ASR桁連結(現行の扱いを観測) |
| 36 | EQ | `storymaking` | `story making` | EQ | PASS | PASS | PASS | 複合語分かち書き |
| 37 | EQ | `blitzscaling` | `blitz-scaling` | EQ | PASS | PASS | PASS |  |
| 38 | EQ | `covid 19` | `covid19` | EQ | PASS | PASS | PASS | 文字+数字境界 |
| 39 | EQ | `e mail` | `email` | EQ | PASS | PASS | PASS |  |
| 40 | EQ | `a wide-scale empirical study` | `Widescale empirical study.` | EQ | PASS | PASS | PASS | 冠詞除外despace |
| 41 | EQ | `Wi-Fi 6` | `wifi 6` | EQ | PASS | PASS | PASS |  |
| 42 | EQ | `3,000 people` | `3000 people` | EQ | PASS | PASS | PASS | 桁区切り |
| 43 | EQ | `1,000,000 dollars` | `1000000 dollars` | EQ | NG **BAD** | NG **BAD** | NG **BAD** |  |
| 44 | EQ | `3.5 percent` | `three point five percent` | EQ | PASS | PASS | PASS |  |
| 45 | EQ | `Room 12` | `Room twelve` | EQ | PASS | PASS | PASS |  |
| 46 | EQ | `20 percent` | `twenty percent` | EQ | PASS | PASS | PASS |  |
| 47 | EQ | `The 2020s` | `The twenty twenties` | REF | NG | NG | NG |  |
| 48 | REF | `At 1:30` | `At 130` | REF | PASS | NG | NG | ASRが桁連結で書く: 現行は偶然PASS |
| 49 | REF | `At 130` | `At 1:30` | REF | PASS | NG | NG |  |
| 50 | REF | `At 1030` | `At 10:30` | REF | PASS | NG | NG | er109承認同値(X/Z) |
| 51 | REF | `At 10:30` | `At 1030` | REF | PASS | NG | NG |  |
| 52 | REF | `Room 1030` | `Room 10:30` | REF | PASS | NG | NG |  |
| 53 | REF | `At 3:45` | `At 345` | REF | PASS | NG | NG |  |
| 54 | REF | `3 4 5` | `345` | REF | NG | NG | NG |  |
| 55 | REF | `tel 555 1234` | `tel 5551234` | REF | NG | NG | NG | 電話番号の分かち書き |
| 56 | REF | `1 000` | `1000` | REF | NG | NG | NG | 桁区切りスペース |