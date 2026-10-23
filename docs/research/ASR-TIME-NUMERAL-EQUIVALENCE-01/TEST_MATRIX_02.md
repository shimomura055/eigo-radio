# TEST_MATRIX_02(ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_02、API 0)

実行器 `test_matrix_02.py`(TEST_MATRIX_01の表+Opus追加test全件=`er021_time_numeral_test_01.CASES`)。修正前=`--modules base_HEAD`(HEAD `er021`)、修正後=working tree。判定=正式経路の純関数(classify_asr_match→unified_judge、Primary 1本、Secondary不可)。
期待: EQ=PASS系 / NE=PASS不可 / PIN+/PIN-=現行値を固定(PASS/NG) / REF=観測のみ。生データ=`matrix02_base_02.json`/`matrix02_after_02.json`/`.txt`。

**結果: 124件。修正前 期待不一致=29件 / 修正後 期待不一致=0件(誤NG=EQ期待がNG: 0、誤PASS=NE期待がPASS: 0)。PIN/REFで修正前後に変化した行は下表の※2件のみ(意図どおり・開示)。**

| # | group | role | canon | ASR | 期待 | 修正前 | 修正後 | 備考 |
|---|---|---|---|---|---|---|---|---|
| 1 | M01 | FULL | `At ten thirty` | `At 10:30` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) | OPEN-482(1) 純語形 |
| 2 | M01 | FULL | `At 10:30` | `At ten thirty` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) | 逆向き |
| 3 | M01 | FULL | `At ten-thirty` | `At 10:30` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) | ハイフン |
| 4 | M01 | FULL | `At ten thirty` | `At 10 30` | EQ | **BAD** NG(final_gate_value_diff) | OK PASS(primary_pass_approved_equiva) | ASRが空白区切り数字 |
| 5 | M01 | FULL | `At 10 thirty` | `At ten thirty` | EQ | **BAD** NG(final_gate_value_diff) | OK PASS(primary_pass_approved_equiva) | TTS入力の数字化後canon vs ASR語形(実在し得る経路) |
| 6 | M01 | FULL | `At ten thirty` | `At 10 thirty` | EQ | **BAD** NG(final_gate_value_diff) | OK PASS(primary_pass_approved_equiva) |  |
| 7 | M01 | FULL | `At 10 thirty` | `At 10:30` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) | c8実経路(第2層修正済み) |
| 8 | M01 | FULL | `At ten thirty am` | `At 10:30 am` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) | am付き |
| 9 | M01 | FULL | `At 10 thirty am` | `At 10:30 am` | EQ | **BAD** NG(final_gate_value_diff) | OK PASS(primary_pass_approved_equiva) | 数字化canon+am |
| 10 | M01 | FULL | `At 10 thirty pm` | `At 10:30 pm` | EQ | **BAD** NG(final_gate_value_diff) | OK PASS(primary_pass_approved_equiva) | 数字化canon+pm(現行は誤NG) |
| 11 | M01 | FULL | `At two fifteen` | `At 2:15` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) |  |
| 12 | M01 | FULL | `At 2 fifteen` | `At 2:15` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) |  |
| 13 | M01 | FULL | `At one thirty` | `At 1:30` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) | oneは数字化されず純語形で届く |
| 14 | M01 | FULL | `At one thirty` | `At 1 30` | EQ | **BAD** NG(final_gate_value_diff) | OK PASS(primary_pass_approved_equiva) |  |
| 15 | M01 | FULL | `At two thirty` | `At 2:30` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) |  |
| 16 | M01 | FULL | `At ten thirty five` | `At 10:35` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) | 分が2語 |
| 17 | M01 | FULL | `At 10 thirty five` | `At 10:35` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) |  |
| 18 | M01 | FULL | `At ten thirty. He left.` | `At 10:30. He left.` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) | 文末 |
| 19 | M01 | FULL | `Meet at 10 thirty tomorrow` | `Meet at ten thirty tomorrow` | EQ | **BAD** NG(final_gate_value_diff) | OK PASS(primary_pass_approved_equiva) |  |
| 20 | M01 | FULL | `At twelve forty five` | `At 12:45` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) |  |
| 21 | M01 | FULL | `At ten thirty` | `At 1030` | NE | **BAD** PASS(primary_pass_approved_equiva) | OK NG(final_gate_value_diff) | OPEN-482(2) 桁連結は時刻と別物(現行は誤EQUAL) |
| 22 | M01 | FULL | `At 1030` | `At ten thirty` | NE | **BAD** PASS(primary_pass_approved_equiva) | OK NG(final_gate_value_diff) | 逆向き |
| 23 | M01 | FULL | `At 10 thirty` | `At 1030` | NE | OK NG(final_gate_value_diff) | OK NG(final_gate_value_diff) | 数字化canon vs 桁連結 |
| 24 | M01 | FULL | `At ten thirty` | `At 10:13` | NE | OK NG(secondary_unavailable) | OK NG(p1_value_diff) |  |
| 25 | M01 | FULL | `At ten thirty` | `At 10:03` | NE | OK NG(secondary_unavailable) | OK NG(p1_value_diff) |  |
| 26 | M01 | FULL | `At ten thirty` | `At 11:30` | NE | OK NG(secondary_unavailable) | OK NG(p1_value_diff) |  |
| 27 | M01 | FULL | `At ten thirty` | `At 40` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) | 合算40 |
| 28 | M01 | FULL | `At ten thirty` | `At forty` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) |  |
| 29 | M01 | FULL | `At ten thirty` | `At ten` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) | 分の脱落 |
| 30 | M01 | FULL | `At ten thirty` | `At 30` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) | 時の脱落 |
| 31 | M01 | FULL | `At ten thirty pm` | `At 10:30 am` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) | pm/am相違 |
| 32 | M01 | FULL | `At 10 thirty pm` | `At 10:30 am` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) |  |
| 33 | M01 | FULL | `At ten thirty am` | `At 10:30 pm` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) |  |
| 34 | M01 | FULL | `At ten thirty` | `At 10:30 pm` | NE | OK NG(secondary_unavailable) | OK NG(p1_value_diff) | 原稿にam/pm無し・ASRのみpm(付加は現行NG維持) |
| 35 | M01 | FULL | `At ten thirty` | `At 10:30:15` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) |  |
| 36 | M01 | FULL | `At ten thirty` | `At 20:30` | NE | OK NG(secondary_unavailable) | OK NG(p1_value_diff) |  |
| 37 | M01 | FULL | `At ten thirty` | `At 10:30 and 5` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) | 余分な数値 |
| 38 | M01 | FULL | `At two thirty` | `At 2:03` | NE | OK NG(secondary_unavailable) | OK NG(p1_value_diff) |  |
| 39 | M01 | FULL | `At two thirty` | `At 230` | NE | OK NG(final_gate_value_diff) | OK NG(final_gate_value_diff) | 桁連結 |
| 40 | M01 | FULL | `At seven fifteen` | `At 7:50` | NE | OK NG(secondary_unavailable) | OK NG(p1_value_diff) |  |
| 41 | M01 | FULL | `At ten thirty five` | `At 10:53` | NE | OK NG(secondary_unavailable) | OK NG(p1_value_diff) |  |
| 42 | M01 | FULL | `At ten thirty five` | `At 1035` | NE | **BAD** PASS(primary_pass_approved_equiva) | OK NG(final_gate_value_diff) | 桁連結 |
| 43 | M01 | FULL | `At ten thirty` | `At 10 apples and 30 pears` | NE | OK NG(p1_value_diff) | OK NG(secondary_unavailable) |  |
| 44 | M01 | FULL | `In twenty twenty` | `In 2020` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) | 年号(20|20は時刻形だが年として維持) |
| 45 | M01 | FULL | `In twenty twenty six` | `In 2026` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) |  |
| 46 | M01 | FULL | `In 2026` | `In twenty twenty six` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) |  |
| 47 | M01 | FULL | `In nineteen ninety` | `In 1990` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) | 分90は時刻不成立 |
| 48 | M01 | FULL | `In nineteen ninety nine` | `In 1999` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) |  |
| 49 | M01 | FULL | `In 1999` | `In nineteen ninety nine` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) |  |
| 50 | M01 | FULL | `In nineteen seventy five` | `In 1975` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) |  |
| 51 | M01 | FULL | `In twenty twenty` | `In 20:20` | NE | OK NG(secondary_unavailable) | OK NG(secondary_unavailable) | 年と時刻を混同しない(現行も非EQUAL) |
| 52 | M01 | FULL | `In twenty twenty` | `In 2021` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) |  |
| 53 | M01 | FULL | `In nineteen ninety` | `In 1991` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) |  |
| 54 | M01 | FULL | `twenty one people` | `21 people` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) | 十の位→一の位は通常基数 |
| 55 | M01 | FULL | `twenty one people` | `20 1 people` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) |  |
| 56 | M01 | FULL | `one hundred thirty people` | `130 people` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) | scale語後の基数 |
| 57 | M01 | FULL | `one hundred thirty people` | `1:30 people` | REF | OK PASS(primary_pass) | OK PASS(primary_pass) | 既存の別の穴X-2: 一次分類のdespace一致(130==1:30の空白除去)+value_guardのUNKNOWN(kind_mismatch)は止めない仕様でPASS。現行も修正後も同じ(本件のscope外、Opus論点) |
| 58 | M01 | FULL | `two thousand twenty six` | `2026` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) |  |
| 59 | M01 | FULL | `ten people` | `10 people` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) | 単独数 |
| 60 | M01 | FULL | `ten thirty-year-olds` | `10 30-year-olds` | REF | OK NG(final_gate_value_diff) | OK PASS(primary_pass_approved_equiva)※ | 『時 分』隣接でも年齢語の複合 -> 数字化canonと同じ読みなら一致 |
| 61 | M01 | FULL | `It costs two thirty dollars` | `It costs 2.30 dollars` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) | 金額読み(2.30)は時刻/桁連結と別物。非EQUAL維持(安全側) |
| 62 | M01 | FULL | `It costs two thirty dollars` | `It costs 230 dollars` | NE | OK NG(final_gate_value_diff) | OK NG(final_gate_value_diff) | 桁連結 |
| 63 | M01 | FULL | `twelve o'clock` | `12 o'clock` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) | o'clock |
| 64 | M01 | FULL | `twelve o'clock` | `12:00` | REF | OK NG(secondary_unavailable) | OK NG(secondary_unavailable) | 分を伴わない読みは現行どおり(HP:2970はo'clock <-> 時刻の同値を既承認) |
| 65 | M01 | FULL | `At 1030` | `At 1030` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) | 桁連結が原稿にある場合は同表層でEQUAL |
| 66 | M01 | FULL | `At 1030` | `At 10:30` | REF | OK PASS(primary_pass) | OK PASS(primary_pass) | 原稿の桁連結 vs 時刻。er109の承認済み同音規則が1030<->10:30を同値(er109_probe_01: RESCUE)とするため期待値を置かない。現行も修正後も同じ |
| 67 | M01 | FULL | `Chapter eleven fifty is long` | `Chapter 1150 is long` | NE | **BAD** PASS(primary_pass_approved_equiva) | OK NG(final_gate_value_diff) | 時分形(11|50)の桁連結は一致させない。現行EQUAL->修正後NG=意図したPASS->NG(論点: 中世年号) |
| 68 | M01 | FULL | `Magna Carta in twelve fifteen` | `Magna Carta in 1215` | NE | **BAD** PASS(primary_pass_approved_equiva) | OK NG(final_gate_value_diff) | 中世年号(12|15)も時分形。現行EQUAL->修正後NG=意図したPASS->NG(論点) |
| 69 | M01 | FULL | `In ten sixty six` | `In 1066` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) | 分66は時刻不成立->年読み維持 |
| 70 | M01 | FULL | `At 3` | `At three` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) | 単独数 |
| 71 | M01 | FULL | `At five ten fifteen` | `At 5:10 15` | NE | OK NG(final_gate_value_diff) | OK NG(final_gate_value_diff) | 数詞3連(解釈不能)は安全側 |
| 72 | M01 | FULL | `At 12 forty 5` | `At 12:45` | REF | OK NG(p1_value_diff) | OK NG(secondary_unavailable) | TTS数字化後の実canon。vg層はEQUAL(修正後)だが分類層(normalize_numeric)が `forty 5`を40 5と読みNG=既存の別不具合F-1(`thirty 5 people`vs`35 people`も同じ)。本件範囲外 |
| 73 | M01 | FULL | `At 10 thirty 5` | `At 10:35` | REF | OK NG(p1_value_diff) | OK NG(secondary_unavailable) | 同上 F-1(分類層) |
| 74 | M01 | FULL | `At 10 thirty 5` | `At ten thirty five` | EQ | **BAD** NG(p1_value_diff) | OK PASS(primary_pass_approved_equiva) | ASRが語形 |
| 75 | M01 | FULL | `At 10 thirty 5` | `At 10 35` | EQ | **BAD** NG(p1_value_diff) | OK PASS(primary_pass_approved_equiva) |  |
| 76 | M01 | FULL | `At 10 thirty 5` | `At 10:53` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) |  |
| 77 | M01 | FULL | `At 10 thirty 5` | `At 1035` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) | 桁連結 |
| 78 | M01 | FULL | `At 10 thirty 5` | `At 10:30` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) | 分の末尾脱落 |
| 79 | M01 | FULL | `At 10 thirty 5` | `At 10:30 5` | NE | **BAD** PASS(primary_pass) | OK NG(final_gate_value_diff) |  |
| 80 | M01 | FULL | `At 3 fifteen pm` | `At 3:15 pm` | EQ | **BAD** NG(final_gate_value_diff) | OK PASS(primary_pass_approved_equiva) |  |
| 81 | M01 | FULL | `At 10 thirty, then 5 people left` | `At 10:30, then five people left` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) | 時刻の後ろの通常数値は独立 |
| 82 | M01 | FULL | `10 thirty people came` | `10 30 people came` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) | 『時 分』形に見えるが数字化canonと同形ならASR数字列と一致 |
| 83 | M01 | FULL | `ten twenty-one people` | `10:21 people` | REF | OK PASS(primary_pass) | OK NG(final_gate_value_diff)※ | 時刻の直後に可算名詞が続く形は単位付き=数量読みとして_clock_pairが拒否(安全側)。自然な時刻文ではないため期待値を置かない |
| 84 | M01 | FULL | `I saw 5 ten year olds` | `I saw 5 10 year olds` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) | digit+digit列は従来どおり |
| 85 | OF-TN-02 | FULL | `At 10 thirty pm` | `At 10 30 pm` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) |  |
| 86 | OF-TN-02 | FULL | `At ten thirty pm` | `At 10 30 pm` | EQ | **BAD** NG(final_gate_value_diff) | OK PASS(primary_pass_approved_equiva) |  |
| 87 | OF-TN-02 | FULL | `At ten thirty pm` | `At 10 30 am` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) |  |
| 88 | OF-TN-01 | FULL | `10 twenty-dollar bills` | `10 $20 bills` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) |  |
| 89 | OF-TN-01 | FULL | `2 fifteen percent` | `2 15%` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) |  |
| 90 | OF-TN-01 | FULL | `3 twenty euros` | `3 €20` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) |  |
| 91 | OF-TN-01 | FULL | `twelve fifty dollars` | `$12.50` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) |  |
| 92 | OF-TN-03 | FULL | `between 9 and 10 thirty` | `between 9 and ten-thirty` | EQ | **BAD** NG(final_gate_value_diff) | OK PASS(primary_pass_approved_equiva) | Opus原例`between nine and ten-thirty`はnine側が別件X-3(数詞run `nine and ten`のmis-parse)で不成立のため9を数字にして分離 |
| 93 | OF-TN-03 | FULL | `between 9 and 10 thirty` | `between nine and ten-thirty` | PIN- | OK NG(p1_value_diff) | OK NG(p1_value_diff) | X-3(別OPEN): 修正前から`between 9 and 11`<->`between nine and eleven`もNG |
| 94 | OF-TN-03 | FULL | `between 9 and ten thirty` | `between 9 and 1030` | NE | **BAD** PASS(primary_pass_approved_equiva) | OK NG(final_gate_value_diff) |  |
| 95 | OF-TN-03 | FULL | `between nine and ten thirty` | `between nine and 1030` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) |  |
| 96 | OF-TN-03 | FULL | `one hundred and ten` | `110` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) |  |
| 97 | OF-TN-03 | FULL | `and ten thirty` | `and 1030` | NE | **BAD** PASS(primary_pass_approved_equiva) | OK NG(final_gate_value_diff) |  |
| 98 | KP | KEY_ | `ten thirty` | `1030` | NE | **BAD** PASS(primary_pass) | OK NG(final_gate_value_diff) |  |
| 99 | KP | KEY_ | `ten thirty` | `10:30` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) |  |
| 100 | KP | KEY_ | `ten thirty` | `10 30` | EQ | **BAD** NG(final_gate_value_diff) | OK PASS(primary_pass) |  |
| 101 | YEAR | FULL | `in 1215` | `in twelve fifteen` | NE | **BAD** PASS(primary_pass_approved_equiva) | OK NG(final_gate_value_diff) | PIN(開示): 年号の語形<->桁連結は不一致側。本文経路では修正前から同じ向き |
| 102 | YEAR | FULL | `in 2010` | `in twenty ten` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) |  |
| 103 | YEAR | FULL | `in 1066` | `in ten sixty six` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) |  |
| 104 | YEAR | FULL | `in 1905` | `in nineteen oh five` | PIN- | OK NG(p1_value_diff) | OK NG(p1_value_diff) |  |
| 105 | NOUN | FULL | `the 10 thirty bus` | `the 10:30 bus` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) |  |
| 106 | NOUN | FULL | `the eleven fifteen train` | `the 11:15 train` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) |  |
| 107 | MULTI | FULL | `from 9 fifteen to 10 thirty` | `from 9:15 to 10:30` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) |  |
| 108 | MULTI | FULL | `at 9 fifteen, 10 thirty` | `at 9:15, 10:30` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) |  |
| 109 | BASIC | FULL | `ten thirty-five` | `10:35` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) |  |
| 110 | BASIC | FULL | `ten-thirty a.m.` | `10:30 a.m.` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) |  |
| 111 | BASIC | FULL | `one fifteen` | `1:15` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) |  |
| 112 | BASIC | FULL | `one fifteen` | `fifteen` | PIN- | OK NG(secondary_unavailable) | OK NG(secondary_unavailable) |  |
| 113 | BASIC | FULL | `ten oh five` | `10:05` | PIN- | OK NG(p1_value_diff) | OK NG(p1_value_diff) |  |
| 114 | BASIC | FULL | `ten o'clock` | `10 o'clock` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) |  |
| 115 | C8 | FULL | `At 10 thirty` | `At ten-thirty` | EQ | **BAD** NG(final_gate_value_diff) | OK PASS(primary_pass_approved_equiva) | ROOT_CAUSE_01記載の実対 |
| 116 | C8 | FULL | `At ten thirty` | `At 10:30` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) | PRODUCTION_PLAN_01記載の実対 |
| 117 | NEG | FULL | `At ten thirty` | `At 1030` | NE | **BAD** PASS(primary_pass_approved_equiva) | OK NG(final_gate_value_diff) |  |
| 118 | NEG | FULL | `At 1030` | `At ten thirty` | NE | **BAD** PASS(primary_pass_approved_equiva) | OK NG(final_gate_value_diff) |  |
| 119 | NEG | FULL | `At ten thirty five` | `At 1035` | NE | **BAD** PASS(primary_pass_approved_equiva) | OK NG(final_gate_value_diff) |  |
| 120 | NEG | FULL | `At ten thirty` | `At 10:13` | NE | OK NG(secondary_unavailable) | OK NG(p1_value_diff) |  |
| 121 | NEG | FULL | `At ten thirty` | `At 11:30` | NE | OK NG(secondary_unavailable) | OK NG(p1_value_diff) |  |
| 122 | NEG | FULL | `Chapter eleven fifty is long` | `Chapter 1150 is long` | NE | **BAD** PASS(primary_pass_approved_equiva) | OK NG(final_gate_value_diff) |  |
| 123 | NEG | FULL | `Magna Carta in twelve fifteen` | `Magna Carta in 1215` | NE | **BAD** PASS(primary_pass_approved_equiva) | OK NG(final_gate_value_diff) |  |
| 124 | F-1 | FULL | `At 10 thirty 5` | `At 10:35` | PIN- | OK NG(p1_value_diff) | OK NG(secondary_unavailable) | F-1由来で残存(OPEN新規) |

※ 変化したREF行(意図どおり): (a) `ten twenty-one people`↔`10:21 people` PASS→NG(修正前は`ten twenty-one`を年ペア読み1021と読んで時刻10:21と偶然一致していた型=#21と同じ穴。数量/時刻が曖昧な不自然文で、NG側=安全)。(b) `ten thirty-year-olds`↔`10 30-year-olds` NG→PASS(同じ数字列の表記差で正しい)。

## Opus OF-TN-03の原例について(開示)
`between 9 and 10 thirty`↔`between nine and ten-thirty` は、`nine`側が時刻形と無関係な既存不具合X-3(数詞run `nine and ten ...`の貪欲解析が失敗し`nine`がliteral化、value_guard側も`9`をsrc_drop)でNG。修正前から`between 9 and 11`↔`between nine and eleven`もNG(本件の外・別OPEN)。時刻形の`and`直後除外の検証は9を数字にした `between 9 and 10 thirty`↔`between 9 and ten-thirty` EQ と `between 9 and ten thirty`↔`between 9 and 1030` NE、`and ten thirty`↔`and 1030` NE で行い、原例は PIN(NG)として固定した。
