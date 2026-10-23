# OPEN_482_IMPACT_02 (FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01 委任_04、第2層 value_guard、API 0)

結論: **gate通過**。(a) 採用、(b) 見送り。Production変更は `er078_asr_value_guard_01.py::_guard_en` の1ブロック(+16行、nested関数1+分岐1)のみ。

## 1. 原因(第2層)
- 統一Judge最終ゲート(`er078_asr_unified_judge_01.py:536-545`)の `vg.value_guard` -> `_guard_en`。第1層(er006)修正後、canonは『At 10 30』(num10,num30の2atom)、ASRの『10:30』は1つのtime atom(1030)。diff blockが [num10,num30] vs [time1030] となり `UNKNOWN kind_mismatch:num/time` + `DIFF src_drop(b)`('30') -> DIFF -> NG_PROTECTED(`review_lock_state.json` l.4960-4979)。

## 2. 修正(a)
`_guard_en` の diff block 処理(`an`/`bn` 作成直後)に `_clock_pair`: 片側に数値atomが**ちょうど2つ・隣接**(間にliteral等を挟まない)、他側にtime atom 1つ。条件: 2数値は整数・単位なし・%/通貨/序数なし、時0-24、分10-59、hour*100+minute == time値、time atomにam/pm無し。成立時のみEQUAL(`clock_time_words_vs_digits`)。不成立なら従来コードへ。
- 委任文の「分00-59」より**狭い**(分10-59。分0-9は 2:03 等との取り違え危険を避け、安全側に絞った)。am/pm付きtimeはEQUALにしない(原稿側pmがliteralで検査対象外のため。従来もNGで悪化なし)。

## 3. (b) `er021._tier1_atoms` 純語形 `ten thirty` の扱い = **見送り**
- 実測: `_tier1_atoms('At ten thirty')` は第1層修正と無関係に `number 1030`(`_parse_bare_number_run` の『2つの2桁グループ=年のペア読み』: `_split_into_two_digit_groups` -> [10,30] -> 10*100+30)。`twenty twenty six`=2026、`nineteen ninety`=1990 も同じ経路。つまり『ten thirty』(時刻10:30)と『ten thirty』(年1030)は語形で区別不能。
- (b)で時刻atom化すると、年の読み(twenty twenty six <-> 2026 等、現在EQUAL)を壊す可能性が高く、PASS->NGが出るリスクがある=gate基準(PASS->NG 0)を単独で満たせない。**c8完成には不要**(Judgeに渡るcanonは第1層の正規化後『10 30』。実測: `At 10 30`/`At 10 thirty` vs `10:30` = EQUAL)。純語形canonでは従来どおり UNKNOWN(kind_mismatch)でNG側(安全側)のまま。OPEN-482残存項目として記録。
- (d) 既存の穴 `ten thirty` <-> `1030`(桁連結、純語形のみ)はEQUALのまま、今回修正せず(Fable指示)。

## 4. gate
(i) replay: 全リポジトリの `.json/.jsonl` 47,044ファイルから数値を含む(canon,ASR)対 5,246対を抽出し、`_guard_en` を修正前(HEAD)/修正後で再計算(`replay482b.py`): **変化0件、PASS->NG 0、NG->PASS 0、例外0**。『開いた窓』run_sf_prod_01・melos・X記事群・pool backtest・golden に判定変化なし(変化0のため)。実c8原稿対(『At 10 30, a tall man...』と『At 10:30, a tall man...』)は旧DIFF->新EQUAL。前委任_03の14対の判定レベル(er006)は変更なし(`OPEN_482_IMPACT_01.md`)。
(ii) 合成: `neg482b.py`(結果 `neg482b_result.txt`): 正例8件 全てEQUAL(10 thirty/10 30/2 thirty/1 thirty/7 fifteen vs 時刻表記、逆向き、同形)、負例 27件 全て非EQUAL(10:13/10:15/10:03/11:30/10/40/30/10:30 pm/pm⇄am/2:03/2:13/32/7:50/12:03/13:00/25:30/20:30/10:60/3:04/11:15/9:01/10:30:15/10 apples and 30 pears/10 percent 30/$10 30 等)。旧と新の差は正例のみ(旧DIFF->新EQUAL)。負例の PASS->NG は構造上なし。
(iii) 差分 `er078_asr_value_guard_01.py` +16行(1関数内1ブロック)。新test `er078_time_atom_test_01.py` 4件PASS。既存 `er006_time_numeral_test_01.py`・`er006_cardinal_and_conjunction_test_01.py`・er078既存testは回帰で確認(後述RESULT_PACKET_FZ20Y4)。
