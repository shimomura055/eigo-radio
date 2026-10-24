# TEST_MATRIX_03(ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_04、OPEN-489、API 0)

実行器 `test_matrix_02.py`(TEST_MATRIX_02の124件+委任_04追加のOPEN-489 28件=`er021_time_numeral_test_01.CASES`)。修正前=`--modules base_HEAD03`(委任_04着手時点のHEAD `er006`/`er021`の複製)、修正後=working tree。判定=正式経路の純関数(classify_asr_match→unified_judge、Primary 1本、Secondary不可)。生データ=`matrix03_base_03.json`/`matrix03_after_03.json`/`.txt`。

**結果: 152件。修正前 期待不一致=12件 / 修正後 期待不一致=0件(誤NG=EQ期待がNG: 修正前12→修正後0、誤PASS=NE期待がPASS: 修正前0→修正後0)。判定(最終state)が修正前後で変わった行は下表(OPEN-489全行+状態変化行)のとおりで、PASS→NGへ変わった行=0。**

| # | group | canon | ASR | 期待 | 修正前 | 修正後 | 備考 |
|---|---|---|---|---|---|---|---|
| 93 | OF-TN-03 | `between 9 and 10 thirty` | `between nine and ten-thirty` | EQ | **BAD** NG(p1_value_diff) | OK PASS(primary_pass_approved_equiva) | OPEN-489修正で解消(旧PIN-。Opus原例) |
| 98 | OPEN-489 | `between 9 and 11` | `between nine and eleven` | EQ | **BAD** NG(p1_value_diff) | OK PASS(primary_pass_approved_equiva) | 報告原例 |
| 99 | OPEN-489 | `between nine and eleven` | `between nine and eleven` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) |  |
| 100 | OPEN-489 | `between nine and eleven` | `between 9 and 11` | EQ | **BAD** NG(p1_value_diff) | OK PASS(primary_pass_approved_equiva) |  |
| 101 | OPEN-489 | `between 9 and 10` | `between nine and ten` | EQ | **BAD** NG(p1_value_diff) | OK PASS(primary_pass_approved_equiva) | ten and ...: 旧は年ペア1010扱い |
| 102 | OPEN-489 | `between 10 and 11` | `between ten and eleven` | EQ | **BAD** NG(p1_value_diff) | OK PASS(primary_pass_approved_equiva) | 旧は1011の年ペア読み |
| 103 | OPEN-489 | `between 20 and 30` | `between twenty and thirty` | EQ | **BAD** NG(p1_value_diff) | OK PASS(primary_pass_approved_equiva) | 旧は2030 |
| 104 | OPEN-489 | `seven and eight children` | `7 and 8 children` | EQ | **BAD** NG(p1_value_diff) | OK PASS(primary_pass_approved_equiva) |  |
| 105 | OPEN-489 | `two and three` | `2 and 3` | EQ | **BAD** NG(p1_value_diff) | OK PASS(primary_pass_approved_equiva) |  |
| 106 | OPEN-489 | `between nine and eleven` | `between 9 and 12` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) |  |
| 107 | OPEN-489 | `between nine and eleven` | `between 8 and 11` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) |  |
| 108 | OPEN-489 | `between nine and eleven` | `between nine and twelve` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) |  |
| 109 | OPEN-489 | `between 9 and 11` | `between 9 and 11 and 12` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) | 余分な数 |
| 110 | OPEN-489 | `between nine and eleven` | `between 11 and 9` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) | 順序入替 |
| 111 | OPEN-489 | `between ten and eleven` | `between 1011 and` | NE | OK NG(secondary_unavailable) | OK NG(p1_value_diff) | 年ペア桁連結と別物 |
| 112 | OPEN-489 | `one hundred and ten` | `110` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) | scale語直後のandは数の一部(維持) |
| 113 | OPEN-489 | `two thousand and five` | `2005` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) |  |
| 114 | OPEN-489 | `one hundred and ten` | `100 and 10` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) |  |
| 115 | OPEN-489 | `one hundred and ten` | `1010` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) |  |
| 116 | OPEN-489 | `two hundred and fifty and sixty` | `250 and 60` | EQ | **BAD** NG(p1_value_diff) | OK PASS(primary_pass_approved_equiva) | 2つ目のandは接続詞 |
| 117 | OPEN-489 | `between nine and ten thirty` | `between 9 and 10:30` | EQ | **BAD** NG(p1_value_diff) | OK PASS(primary_pass) | and後の時刻形(_try_clock_pair)と干渉しない |
| 118 | OPEN-489 | `between nine and ten thirty` | `between 9 and 1030` | NE | OK NG(p1_value_diff) | OK NG(final_gate_value_diff) |  |
| 119 | OPEN-489 | `between nine and ten-thirty` | `between 9 and 10:30` | EQ | **BAD** NG(p1_value_diff) | OK PASS(primary_pass) |  |
| 120 | OPEN-489 | `in nineteen ninety and twenty twenty` | `in 1990 and 2020` | EQ | **BAD** NG(p1_value_diff) | OK PASS(primary_pass_approved_equiva) | 年号2つ+and |
| 121 | OPEN-489 | `from 1990 to 2020` | `from nineteen ninety to twenty twenty` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) | 年号維持 |
| 122 | OPEN-489 | `five and a half` | `5.5` | PIN- | OK NG(p1_value_diff) | OK NG(p1_value_diff) | and a half系は本件対象外(現行値固定) |
| 123 | OPEN-489 | `ten dollars and fifty cents` | `$10 and 50 cents` | EQ | OK PASS(primary_pass_approved_equiva) | OK PASS(primary_pass_approved_equiva) | 金額 |
| 124 | OPEN-489 | `ten dollars and fifty cents` | `$10 and 15 cents` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) |  |

## 読み方
- 本質: 数詞語runの`and`は『scale語(hundred/thousand/million)の直後で後ろに数詞語が続く』場合だけ数の一部(`one hundred and ten`=110)。それ以外(`nine and eleven`/`ten and twenty`)は接続詞でrunを分割する。修正前は(a)er021 `_consume_number_word_run`が`nine and eleven`全体を1 runとして解析→`nine`が単独一桁語規則で失敗しliteral化 / `ten and eleven`は年ペア読み1011、(b)er006 `_convert_cardinal_words`は不正な`and`位置で列全体を未変換にしていた(`nine and eleven`が`9 and 11`にならない)、の2層で同じ前提(`and`を数の一部として一括解析)が働いていた。
- 年号(`nineteen ninety and twenty twenty`=1990 and 2020)・金額(`ten dollars and fifty cents`)・`and a half`系・`_try_clock_pair`(`between nine and ten thirty`↔`between 9 and 10:30`)・`one hundred and ten`/`two thousand and five`(scale語直後のand)との整合は行 OF-TN-03/OPEN-489 の各caseで固定。
- 副次所見(新OPEN候補、本委任では未修正): TTS入力の数字化(`tts_safe_number_words_en`)が`one hundred and ten`を`one hundred and 10`にするため、ASRが`110`のとき正式再判定経路で`p1_value_diff`になる(scale語+数字の合成。F-1[十の位+1桁]と同型)。保存corpus 5,330対で該当0件(実害未観測)。→ OPEN-491(下記)。
