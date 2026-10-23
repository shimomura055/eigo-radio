# TEST_MATRIX_01 検証セット(ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_01、API 0)

実行器: `test_matrix_01.py`(`py test_matrix_01.py [--modules proto_C]`)。結果json/txt: `baseline_matrix_01.*`(修正前=HEAD)、`protoC_matrix_01.*`(推奨案C)。
判定は正式経路の純関数だけで再現(`judge_sim_01.py`: classify_asr_match(role=FULL_STORY)→adapterと同じbasis導出→unified_judge。Primary転写1本、Secondary呼出不可)。
**期待値EQ=PASS系(PASS/PASS_WITH_WARNING)であるべき / NE=PASS不可であるべき / REF=期待値を置かない参考(理由を注記)**。
根拠略号: S5=CURRENT_SPEC.md:2834 値ガード5値(値/単位が同じ=EQUAL、違う=DIFF) / S9=同:2835 ユーザー提示9例(同値は表記差許容・異値は不許容) / HP=同:2970 er109(時刻は分を伴う読みのみ同値) / YR=年号の既存EQUAL(OPEN_482_IMPACT_01 §3で救済実績) / ユーザー指示②-2=OPEN-482(2)原文。

- **修正前**: 期待値あり77件中 一致61件 / 誤NG(正常をNG)10件 / 誤PASS(異常をPASS)6件
- **案C**: 期待値あり77件中 一致77件 / 誤NG(正常をNG)0件 / 誤PASS(異常をPASS)0件

| # | 区分 | 原稿(canon) | ASR | 期待 | 修正前 | 案C | 根拠/注記 |
|---|---|---|---|---|---|---|---|
| 1 | 正常 | `At ten thirty` | `At 10:30` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) | S5/S9/HP OPEN-482(1) 純語形 |
| 2 | 正常 | `At 10:30` | `At ten thirty` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) | S5/S9/HP 逆向き |
| 3 | 正常 | `At ten-thirty` | `At 10:30` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) | S5/HP ハイフン |
| 4 | 正常 | `At ten thirty` | `At 10 30` | EQ | **BAD** NG(final_gate_value_diff) | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | S5/S9 ASRが空白区切り数字 |
| 5 | 正常 | `At 10 thirty` | `At ten thirty` | EQ | **BAD** NG(final_gate_value_diff) | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | S5/S9 TTS入力の数字化後canon vs ASR語形(実在し得る経路) |
| 6 | 正常 | `At ten thirty` | `At 10 thirty` | EQ | **BAD** NG(final_gate_value_diff) | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | S5/S9  |
| 7 | 正常 | `At 10 thirty` | `At 10:30` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) | S5/HP c8実経路(第2層修正済み) |
| 8 | 正常 | `At ten thirty am` | `At 10:30 am` | EQ | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | S5/HP am付き |
| 9 | 正常 | `At 10 thirty am` | `At 10:30 am` | EQ | **BAD** NG(final_gate_value_diff) | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | S5/HP 数字化canon+am |
| 10 | 正常 | `At 10 thirty pm` | `At 10:30 pm` | EQ | **BAD** NG(final_gate_value_diff) | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | S5/HP 数字化canon+pm(現行は誤NG) |
| 11 | 正常 | `At two fifteen` | `At 2:15` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) | S5/HP  |
| 12 | 正常 | `At 2 fifteen` | `At 2:15` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) | S5/HP  |
| 13 | 正常 | `At one thirty` | `At 1:30` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) | S5/HP oneは数字化されず純語形で届く |
| 14 | 正常 | `At one thirty` | `At 1 30` | EQ | **BAD** NG(final_gate_value_diff) | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | S5/S9  |
| 15 | 正常 | `At two thirty` | `At 2:30` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) | S5/HP  |
| 16 | 正常 | `At ten thirty five` | `At 10:35` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) | S5/HP 分が2語 |
| 17 | 正常 | `At 10 thirty five` | `At 10:35` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) | S5/HP  |
| 18 | 正常 | `At ten thirty. He left.` | `At 10:30. He left.` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) | S5 文末 |
| 19 | 正常 | `Meet at 10 thirty tomorrow` | `Meet at ten thirty tomorrow` | EQ | **BAD** NG(final_gate_value_diff) | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | S5  |
| 20 | 正常 | `At twelve forty five` | `At 12:45` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) | S5/HP  |
| 21 | 異常 | `At ten thirty` | `At 1030` | NE | **BAD** PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | OK NG(final_gate_value_diff) | ユーザー指示②-2/S5 OPEN-482(2) 桁連結は時刻と別物(現行は誤EQUAL) |
| 22 | 異常 | `At 1030` | `At ten thirty` | NE | **BAD** PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | OK NG(final_gate_value_diff) | ユーザー指示②-2/S5 逆向き |
| 23 | 異常 | `At 10 thirty` | `At 1030` | NE | OK NG(final_gate_value_diff) | OK NG(final_gate_value_diff) | S5 数字化canon vs 桁連結 |
| 24 | 異常 | `At ten thirty` | `At 10:13` | NE | OK NG(secondary_unavailable) | OK NG(p1_value_diff) | S5  |
| 25 | 異常 | `At ten thirty` | `At 10:03` | NE | OK NG(secondary_unavailable) | OK NG(p1_value_diff) | S5  |
| 26 | 異常 | `At ten thirty` | `At 11:30` | NE | OK NG(secondary_unavailable) | OK NG(p1_value_diff) | S5  |
| 27 | 異常 | `At ten thirty` | `At 40` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) | S5 合算40 |
| 28 | 異常 | `At ten thirty` | `At forty` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) | S5  |
| 29 | 異常 | `At ten thirty` | `At ten` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) | S5 分の脱落 |
| 30 | 異常 | `At ten thirty` | `At 30` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) | S5 時の脱落 |
| 31 | 異常 | `At ten thirty pm` | `At 10:30 am` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) | S5 pm/am相違 |
| 32 | 異常 | `At 10 thirty pm` | `At 10:30 am` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) | S5  |
| 33 | 異常 | `At ten thirty am` | `At 10:30 pm` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) | S5  |
| 34 | 異常 | `At ten thirty` | `At 10:30 pm` | NE | OK NG(secondary_unavailable) | OK NG(p1_value_diff) | S5 原稿にam/pm無し・ASRのみpm(付加は現行NG維持) |
| 35 | 異常 | `At ten thirty` | `At 10:30:15` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) | S5  |
| 36 | 異常 | `At ten thirty` | `At 20:30` | NE | OK NG(secondary_unavailable) | OK NG(p1_value_diff) | S5  |
| 37 | 異常 | `At ten thirty` | `At 10:30 and 5` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) | S5 余分な数値 |
| 38 | 異常 | `At two thirty` | `At 2:03` | NE | OK NG(secondary_unavailable) | OK NG(p1_value_diff) | S5  |
| 39 | 異常 | `At two thirty` | `At 230` | NE | OK NG(final_gate_value_diff) | OK NG(final_gate_value_diff) | ユーザー指示②-2/S5 桁連結 |
| 40 | 異常 | `At seven fifteen` | `At 7:50` | NE | OK NG(secondary_unavailable) | OK NG(p1_value_diff) | S5  |
| 41 | 異常 | `At ten thirty five` | `At 10:53` | NE | OK NG(secondary_unavailable) | OK NG(p1_value_diff) | S5  |
| 42 | 異常 | `At ten thirty five` | `At 1035` | NE | **BAD** PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | OK NG(final_gate_value_diff) | ユーザー指示②-2/S5 桁連結 |
| 43 | 異常 | `At ten thirty` | `At 10 apples and 30 pears` | NE | OK NG(p1_value_diff) | OK NG(secondary_unavailable) | S5  |
| 44 | 境界 | `In twenty twenty` | `In 2020` | EQ | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | YR 年号(20|20は時刻形だが年として維持) |
| 45 | 境界 | `In twenty twenty six` | `In 2026` | EQ | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | YR  |
| 46 | 境界 | `In 2026` | `In twenty twenty six` | EQ | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | YR  |
| 47 | 境界 | `In nineteen ninety` | `In 1990` | EQ | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | YR 分90は時刻不成立 |
| 48 | 境界 | `In nineteen ninety nine` | `In 1999` | EQ | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | YR  |
| 49 | 境界 | `In 1999` | `In nineteen ninety nine` | EQ | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | YR  |
| 50 | 境界 | `In nineteen seventy five` | `In 1975` | EQ | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | YR  |
| 51 | 境界 | `In twenty twenty` | `In 20:20` | NE | OK NG(secondary_unavailable) | OK NG(secondary_unavailable) | S5 年と時刻を混同しない(現行も非EQUAL) |
| 52 | 境界 | `In twenty twenty` | `In 2021` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) | S5  |
| 53 | 境界 | `In nineteen ninety` | `In 1991` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) | S5  |
| 54 | 境界 | `twenty one people` | `21 people` | EQ | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | S9 十の位→一の位は通常基数 |
| 55 | 境界 | `twenty one people` | `20 1 people` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) | S5  |
| 56 | 境界 | `one hundred thirty people` | `130 people` | EQ | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | S9 scale語後の基数 |
| 57 | 境界 | `one hundred thirty people` | `1:30 people` | REF | PASS(primary_pass) | PASS(primary_pass) | - 既存の別の穴X-2: 一次分類のdespace一致(130==1:30の空白除去)+value_guardのUNKNOWN(kind_mismatch)は止めない仕様でPASS。現行も修正後も同じ(本件のscope外、Opus論点) |
| 58 | 境界 | `two thousand twenty six` | `2026` | EQ | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | YR  |
| 59 | 境界 | `ten people` | `10 people` | EQ | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | S9 単独数 |
| 60 | 境界 | `ten thirty-year-olds` | `10 30-year-olds` | REF | NG(final_gate_value_diff) | PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | - 『時 分』隣接でも年齢語の複合 -> 数字化canonと同じ読みなら一致 |
| 61 | 境界 | `It costs two thirty dollars` | `It costs 2.30 dollars` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) | S5 金額読み(2.30)は時刻/桁連結と別物。非EQUAL維持(安全側) |
| 62 | 境界 | `It costs two thirty dollars` | `It costs 230 dollars` | NE | OK NG(final_gate_value_diff) | OK NG(final_gate_value_diff) | S5 桁連結 |
| 63 | 境界 | `twelve o'clock` | `12 o'clock` | EQ | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | HP o'clock |
| 64 | 境界 | `twelve o'clock` | `12:00` | REF | NG(secondary_unavailable) | NG(secondary_unavailable) | HP 分を伴わない読みは現行どおり(HP:2970はo'clock <-> 時刻の同値を既承認) |
| 65 | 境界 | `At 1030` | `At 1030` | EQ | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | S5 桁連結が原稿にある場合は同表層でEQUAL |
| 66 | 境界 | `At 1030` | `At 10:30` | REF | PASS(primary_pass) | PASS(primary_pass) | er109(CURRENT_SPEC.md:2970) 原稿の桁連結 vs 時刻。er109の承認済み同音規則が1030<->10:30を同値(er109_probe_01: RESCUE)とするため期待値を置かない。現行も修正後も同じ |
| 67 | 境界 | `Chapter eleven fifty is long` | `Chapter 1150 is long` | NE | **BAD** PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | OK NG(final_gate_value_diff) | ユーザー指示②-2と同型 時分形(11|50)の桁連結は一致させない。現行EQUAL->修正後NG=意図したPASS->NG(論点: 中世年号) |
| 68 | 境界 | `Magna Carta in twelve fifteen` | `Magna Carta in 1215` | NE | **BAD** PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | OK NG(final_gate_value_diff) | ユーザー指示②-2と同型 中世年号(12|15)も時分形。現行EQUAL->修正後NG=意図したPASS->NG(論点) |
| 69 | 境界 | `In ten sixty six` | `In 1066` | EQ | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | YR 分66は時刻不成立->年読み維持 |
| 70 | 境界 | `At 3` | `At three` | EQ | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | S9 単独数 |
| 71 | 境界 | `At five ten fifteen` | `At 5:10 15` | NE | OK NG(final_gate_value_diff) | OK NG(final_gate_value_diff) | S5 数詞3連(解釈不能)は安全側 |
| 72 | 正常 | `At 12 forty 5` | `At 12:45` | REF | NG(p1_value_diff) | NG(secondary_unavailable) | - TTS数字化後の実canon。vg層はEQUAL(修正後)だが分類層(normalize_numeric)が `forty 5`を40 5と読みNG=既存の別不具合F-1(`thirty 5 people`vs`35 people`も同じ)。本件範囲外 |
| 73 | 正常 | `At 10 thirty 5` | `At 10:35` | REF | NG(p1_value_diff) | NG(secondary_unavailable) | - 同上 F-1(分類層) |
| 74 | 正常 | `At 10 thirty 5` | `At ten thirty five` | EQ | **BAD** NG(p1_value_diff) | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | S5/S9 ASRが語形 |
| 75 | 正常 | `At 10 thirty 5` | `At 10 35` | EQ | **BAD** NG(p1_value_diff) | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | S5/S9  |
| 76 | 異常 | `At 10 thirty 5` | `At 10:53` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) | S5  |
| 77 | 異常 | `At 10 thirty 5` | `At 1035` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) | ユーザー指示②-2/S5 桁連結 |
| 78 | 異常 | `At 10 thirty 5` | `At 10:30` | NE | OK NG(p1_value_diff) | OK NG(p1_value_diff) | S5 分の末尾脱落 |
| 79 | 異常 | `At 10 thirty 5` | `At 10:30 5` | NE | **BAD** PASS(primary_pass) | OK NG(final_gate_value_diff) | S5  |
| 80 | 正常 | `At 3 fifteen pm` | `At 3:15 pm` | EQ | **BAD** NG(final_gate_value_diff) | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | S5/HP  |
| 81 | 正常 | `At 10 thirty, then 5 people left` | `At 10:30, then five people left` | EQ | OK PASS(primary_pass) | OK PASS(primary_pass) | S5 時刻の後ろの通常数値は独立 |
| 82 | 境界 | `10 thirty people came` | `10 30 people came` | EQ | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | S5 『時 分』形に見えるが数字化canonと同形ならASR数字列と一致 |
| 83 | 境界 | `ten twenty-one people` | `10:21 people` | REF | PASS(primary_pass) | NG(final_gate_value_diff) | - 時刻の直後に可算名詞が続く形は単位付き=数量読みとして_clock_pairが拒否(安全側)。自然な時刻文ではないため期待値を置かない |
| 84 | 境界 | `I saw 5 ten year olds` | `I saw 5 10 year olds` | EQ | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | OK PASS(approved:TIER1_NUMERIC_EQUIVALENCE) | S5 digit+digit列は従来どおり |

## 『品質を守る』ための判定上の注意
- 最終Gateが止めるのは value_guard=DIFF のみ(`er078_asr_unified_judge_01.py:541`)。UNKNOWNは止めない。よって純語形`ten thirty`↔`10:30`(UNKNOWN)は現行でも**PASS**で、OPEN-482(1)が現実にNGを起こすのは canon=数字化後(`10 thirty`)×ASR=語形(`ten thirty`/`ten-thirty`)や`one thirty`↔`1 30`等のDIFF経路(上表の修正前BAD)。
- Tier1由来のPASS(basis=TIER1_NUMERIC_EQUIVALENCE)は最終Gateをskipするため、`ten thirty`↔`1030`(OPEN-482(2))は value_guard まで到達せず PASS。案Cは Tier1の atom 化を直すので value_guard 側で DIFF→NG になる。
- REF行は期待値を置かない(理由は注記): F-1=TTS数字化が`thirty five`の`five`だけ数字化する既存不具合(分類層)、X-2/er109同音規則による既存挙動、等。案Cで変化しないことを確認済み(修正前と同判定)。
