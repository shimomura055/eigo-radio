# OPEN_482_IMPACT_01 (FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01 委任_03 T-1、API 0)

結論: **gate通過**。修正は `er006_preprod_hardening_01_validation.py::_convert_cardinal_words` の1箇所(+23行)のみ。

## 1. 現行仕様(原因箇所)
- `normalize_numeric()` 手順3 → `_convert_cardinal_words()`(l.~296) が連続する数詞語(`_NUM_WORD_VOCAB`)を**1つの語列として`_words_to_number()`で合算**(`_ONES`+`_TENS`を単純加算)。
- このため `ten thirty` → 10+30=`40`、`two thirty` → `32`、`seven fifteen` → `22`、`nineteen ninety nine` → `118`。ASR側 `10:30` は `:` が空白化され `10 30`。→ number_mismatches=[('40','10 30')] → TRUE_CONTENT_MISMATCH(c8のHR Lock)。
- 英語の正しい基数語列は「十の位→一の位」(twenty one)・「scale語の後」(one hundred thirty)の順のみ。「一の位/10-19の語 → 十の位/10-19の語」(ten thirty, two thirty, seven fifteen, nineteen ninety)は基数としてあり得ず、時刻・年号の読み(2桁+2桁)。従来の合算は誤り(意図された設計は未確認: DECISION_LOG/CURRENT_SPECは`CardinalAndTest`(「hundred and」型)の不具合是正記録[2026-10-23 FAMILY-Z-VOICE-PRODUCTION-WIRING-01]のみで、隣接数詞語の合算を仕様として選択した記録なし)。
- 時刻・年号・小数・分数・序数の扱い: 小数=step5(`N point M`)、序数=step7、年号の『nineteen ninety』は従来`109`など誤値(Tier1 er021 は別途 role=5role の clip でのみ早期受理)。時刻の専用分岐は無し。

## 2. 修正(最小差分)
`_convert_cardinal_words` の数値語列(core)を、「直前語が`_ONES`(0-19)で、現在語が`_TENS`または`_ONES`の10以上」の境界で別列へ分割し、各列を従来どおり`_words_to_number`で数値化(分割列が複数のときは単独`one`も`1`へ)。分割が起きない列(twenty one / one hundred thirty / two hundred and five / three thousand two hundred forty five / twenty twenty[従来どおり40])は従来コードパスのまま。Prompt・閾値・辞書・Gate・flag変更なし。

## 3. replay(決定論、API 0)
- 全追跡/未追跡の `.md/.json/.jsonl/.txt` 66,128ファイルを走査(`replay482.py`)。パターン(一の位/10-19語+空白/ハイフン+十の位/10-19語)を含むのは約50ファイル、正規化結果が新旧で変わるsegmentは427(telemetry重複が大半)。パターンを含まないテキストは修正コードに到達しない(同一コード経路)ため正規化結果は不変。『開いた窓』run_sf_prod_01・melos・X記事群・pool backtest・golden にパターンのヒットは0件。
- 判定レベル(`pairs482.py`、canonical/ASR対 14件、`classify_asr_match`新旧比較): 変化7件、**PASS→NG 0件**、NG→PASS 7件(全て隣接数詞語の誤合算に起因): `five thirty`↔`5:30` ×2、`three thirty pm`↔`3:30 pm`、`three ten-minute`↔`310 minute`(相違後の despace 一致)、`1999`↔`nineteen ninety-nine`、`1975`↔`nineteen seventy-five`、本作c8原稿↔`10:30`。
- 限界: 改行/複数空白を挟む隣接語、JSONエスケープ内の隣接語はヒット漏れの可能性(実害は同方向の改善のみ)。

## 4. 合成負例(`neg482.py`、21ケース全て期待通り)
`ten thirty` vs `10:13`/`ten`/`10`/`10:15`/`10:03`/`11:30`/`30` → NG維持。`two thirty` vs `2:03`/`2:13`/`32` → NG。`seven fifteen` vs `7:50` → NG。`ten thirty` vs `40`/`forty` → 旧PASS→**新NG**(誤って`forty`と読まれた場合を旧は見逃していた。検出力は強まる)。`twenty one` vs `20:1` → NG。正例: `ten thirty`↔`10:30`/`ten-thirty`、`two thirty`↔`2:30`、`one thirty`↔`1:30`、`seven fifteen`↔`7:15` → PASS。

## 5. gate判定
(i) 保存済み判定の再計算でPASS→NG 0件、NG→PASSは全て隣接数詞語の正規化誤り起因 → 成立。(ii) 数値・否定の安全条件: 合成負例全てNG維持(1件は旧より厳格化) → 成立。(iii) 1関数1ブロック → 成立。**通過**。
注意: 本関数は共有(Family A/B/C Productionも同じ正規化を通る)。変化は「隣接数詞語を含む文」に限られ、方向は誤合算の解消のみ(27-7: A/B/C自体の開発・是正ではなくX/Z共通検査の不具合是正が目的、波及は同方向の改善のみ)。

## 6. T-2/T-3 実施結果と新所見(第2層: 最終ゲートの値ガード)
- T-2: 上記修正を適用。新test `er006_time_numeral_test_01.py`(5件)PASS、関連 `er006_cardinal_and_conjunction_test_01.py` PASS。全回帰(`run_project_regression.py`) collected=6977 passed=6964 failed=3 skipped=10。失敗3件は既存(er019 `test_fallback_used_consumers...`、er020 `test_recorded_candidates`、er003_test_bad fixture)＋er064 `test_no_tracked_py_or_template_modified`(未commitの本修正を検出するだけの設計で、commit後に解消)。今回の修正由来の失敗0。
- T-3: c8を`approve_regenerate`(根拠=委任_03・ユーザー原文§5、原稿不変、記録`audit_hr_lock_release_fz20y03.json`、旧状態は`_preserve_c8_hr_lock_20261023/`に保全)後、`--only-clips full_story_part2_c8`で再生成。attempt6/7(標準2回)とminimal fallback(attempt8)の3回とも、**一次分類(classify_asr_match)はNORMALIZED_MATCHで通った(本修正が効いた証拠)が、統一Judgeの最終ゲート`final_gate_value_diff`(er078_asr_value_guard_01 `value_guard`)で NG_PROTECTED**。再びHR Lock(cumulative 6)。
- 第2層の原因: `er078_asr_value_guard_01._guard_en` は原稿側の語/数字を別atomに分け(`At 10 thirty` → num10, num30。TTS入力の数字化`tts_safe_number_words_en`により『10 thirty』)、ASR側の `10:30` は`er021._tier1_atoms`が time atom(1030)にする。pairs: `UNKNOWN kind_mismatch:num/time '10'->'1030'` + `DIFF src_drop(b) '30'->None`。純語形の`ten thirty`は`_tier1_atoms`自体が合算(→40)して`kind_mismatch`(UNKNOWN)になる。
- 第2層の候補修正(未適用・Production変更なし): `_guard_en` の置換ブロックに『数値2atom(時0-24・分10-59、修飾extra全て無し)と、反対側の1 time atom が hour*100+minute で一致』なら EQUAL とする時刻パターン分岐(`OPEN_482_VALUE_GUARD_CANDIDATE_01.diff`、約9行)。scratch複製での検証(`cand482.py`): `10 thirty`↔`10:30`=EQUAL、`10:13`/`10:15`/`11:30`/`2:03`/`ten`/`40`/`30`/`20:1`/`am⇄pm`=従来どおり非EQUAL(負例維持)。**ただし純語形`ten thirty`(tier1が40に合算)は未対応**であり、その分岐を足すには`_tier1_atoms`側の合算(number-word run)にも同方向の修正が要る=委任_03の『当該正規化1箇所のみ』を超えるため未実装、Fableへ。
- 副次所見(既存の穴): `ten thirty`↔`1030`(桁連結)は旧・新ともEQUAL(value_guardのtime atom/数字列の扱い)。今回のスコープ外。
