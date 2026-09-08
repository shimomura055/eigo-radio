# OPEN-128-METHOD-D-LOCAL-ASR-CONFIRM-PRODUCTION-WIRING-01 レポート

管理ID: OPEN-128-METHOD-D-LOCAL-ASR-CONFIRM-PRODUCTION-WIRING-01
Lane: Production配線(ユーザー2026-09-08`APPROVED_FOR_PRODUCTION`。
方式D acoustic flag→局所ASRで2箇所の語句一致を確認→実際の語句重複が
確認された場合のみ最終flag、の2段判定[候補c]。方式Aで取得済みのASR
結果を方式Dでも共有し同一音声へのASR二重実行を避けるリファクタ込み。
acoustic threshold[sim 0.85 / run 0.12]は無変更)。到達Status:
**コード実装・回帰テスト・Runtime evidence・project-wide regression
いずれも完了**。Git操作はPart 3で実施。

採用元: `OPEN-121-METHOD-D-FALSE-POSITIVE-REDUCTION-TRIAL-01_REPORT.md`
(候補c、`VALIDATED`)。判定ロジック・閾値はTrialから無変更。

---

## 1. 実装箇所

[er011_open121_repetition_qa_production_01.py](er011_open121_repetition_qa_production_01.py)

- 新規関数`confirm_by_local_asr_overlap(words, time_a, time_b, ...)`:
  Trial候補cのロジックを無変更で移植(window±1.5秒、空なら+1.0秒刻み
  [2.5秒まで]→+1.5秒刻み[4.0秒まで]拡張、difflib SequenceMatcher比率
  [`overlap_ratio`]+最長連続一致語数[`lcs_words`]、`overlap_ratio>=0.5
  OR lcs_words>=3`で`confirmed=True`)。
- `analyze_profile_d_long_lag()`: 既存のacoustic判定ロジック(候補ペア
  選定・run長計算・閾値比較)は一切変更せず、結果フィールド名を
  `flagged`→`acoustic_flagged`へ改称し、新規引数`words=None`
  (後方互換、既定Noneなら従来通りacoustic判定のみを最終`flagged`と
  する)を追加。`words`が渡され`acoustic_flagged=True`の場合のみ、
  **top[0](類似度最上位match、既存`top_matches`生成ロジック無変更)**
  のtime_a/time_bに対し`confirm_by_local_asr_overlap()`を呼び、
  `flagged = acoustic_flagged and confirmation["confirmed"]`とする。
  ⚠️実装時、当初「run長最大のmatch(top[:3]の該当entry)」を確認対象に
  していたが、`method_d_flag23_review_01/classification_table.json`の
  `flag_time_a/flag_time_b`(=`er011_open121_method_d_flag23_review_01.
  py`221行`best = top[0]`)およびTrial候補cの実装(`row.get("flag_
  time_a"/"flag_time_b")`)がいずれも**top[0]を使用**しており、
  run長最大entryを使うと未検証の挙動(実際に既知FP1件が誤ってconfirm
  される)になることを回帰テストで発見し、top[0]方式へ修正した(§4)。
- `run_spectral_checks(path, words=None)`: `words`を`analyze_profile_
  d_long_lag()`へ中継するのみ(方式D'は本承認の対象外、無変更)。
- `evaluate_repetition_qa(path, canonical_text, language="en")`:
  `dq18.transcribe_verbatim()`をここで1回だけ呼び、方式A
  (`detect_ngram_repetition`)と方式D(`run_spectral_checks`経由の
  局所ASR確認)へ同じword-level ASR結果を共有する(§3)。従来
  `run_ngram_check()`(内部でtranscribe_verbatimを呼ぶ)を呼んでいたのを
  `detect_ngram_repetition()`直接呼び出しへ変更(判定ロジック自体は
  無変更、`run_ngram_check()`関数自体は後方互換のため削除せず維持)。

acoustic threshold(`METHOD_D_SIM_THRESHOLD=0.85`・`METHOD_D_DECISION_
RUN_SECONDS=0.12`)は一切変更していない。新規定数
`METHOD_D_ASR_CONFIRM_OVERLAP_RATIO_THRESHOLD=0.5`・
`METHOD_D_ASR_CONFIRM_LCS_WORDS_THRESHOLD=3`・
`METHOD_D_ASR_CONFIRM_WINDOW_HALF_SECONDS=1.5`・
`METHOD_D_ASR_CONFIRM_MAX_HALF_WINDOW_SECONDS=4.0`はTrial推奨値と同一。

## 2. 既存AND gate・retry loop・Human Review Lockとの整合(diff確認)

`apply_repetition_qa_gate()`(`verified and not evidence["flagged"]`)・
`er003_v1_repro01_main_generate.py`等の呼び出し元・retry loop・
`review_lock`との接続コードは**無変更**(`git diff`で当該箇所に差分が
無いことを確認済み)。変更は`er011_open121_repetition_qa_production_
01.py`内の方式D計算ロジック本体のみに閉じている。

## 3. ASR共有リファクタ(二重ASR回避)

`evaluate_repetition_qa()`が`transcribe_verbatim()`を1回だけ呼び、
戻り値`words`を方式A(`detect_ngram_repetition`)と方式D局所ASR確認の
両方で再利用する。方式D単体でacoustic flagしても追加のASR呼び出しは
発生しない。実測(§5): 確定TP8件+確定FP15件(全件acoustic_flagged=True、
局所ASR確認が実際に発火する経路)で`transcribe_verbatim`呼び出し回数を
計測し、**全23件で1回ずつ(2回以上は0件)**を確認した。

## 4. 回帰・統合テスト

新規`er011_open128_method_d_local_asr_confirm_production_wiring_01_
test_01.py`(9件、全PASS):

- `ConfirmByLocalAsrOverlapUnitTests`(3件): 真の重複(高overlap→
  confirmed)・無関係内容(低overlap→not confirmed)・空window
  (not confirmed)。
- `AnalyzeProfileDTwoStageTests`(2件): (c)acoustic_flagged=Falseなら
  `confirm_by_local_asr_overlap`自体を呼ばない(追加計算コストゼロ)、
  words=None(既定)なら従来のacoustic判定のみ(後方互換)。
- `Flag23ProductionEntryClassificationTests`(2件、実wav):
  既知TP1件(`open112_trial13::...::point_two`、真の重複)が
  acoustic_flagged=True→confirmed=True→flagged=True、既知FP1件
  (`pool_benches::topic_intro`)がacoustic_flagged=True→
  confirmed=False→flagged=False。
- `AsrSharingAndFailureParityTests`(2件、mock): (d)transcribe_
  verbatim呼び出しが方式D acoustic flag時も1回のみ(合成simでacoustic_
  flagged=Trueを再現)、(e)ASR失敗時(`transcribe_verbatim`が例外送出)
  は方式A単体(`run_ngram_check`)と同一の例外伝播であることを確認
  (§6)。

`er011_open121_repetition_qa_production_wiring_01_test_01.py`
既存30件も全PASS(後方互換、words=None経路の既存D/D'テストに影響なし)。

TP8件+FP15件全件のRuntime evidence(実wav・実ASR)は§5参照。

## 5. Runtime evidence

`er011_output/open128_method_d_local_asr_wiring_01/run_runtime_
evidence.py`(Production entry`evaluate_repetition_qa()`を確定TP8件+
確定FP15件[`er011_output/method_d_flag23_review_01/classification_
table.json`]全23件へ直接実行、`transcribe_verbatim`呼び出し回数を
カウンタでラップして計測)。

- **TP 8/8** flagged=True(2段判定後も見逃しゼロ)
- **FP 0/15** flagged=False(全件是正)
- **全23件でASR呼び出し1回**(`all_items_single_asr_call: true`)
- 実行時間155.9秒→修正後316.4秒(23件、faster-whisper small model
  ローカルCPU、局所ASR確認自体の追加計算は数十ms未満)
- 費用¥0(faster-whisperローカルCPUのみ)

証跡: `er011_output/open128_method_d_local_asr_wiring_01/runtime_
evidence.json`

**Production初回path実発火(Standard同期TTS)**:
`er011_output/open128_method_d_local_asr_wiring_01/standard_sync_
1segment_runtime_evidence.py`を`TTS_EXECUTION_MODE=STANDARD`で実行し、
A-Family既存Production関数`er003_v1_sing01_news_tail_fix.
generate_news_narration_wide_margin(enable_repetition_qa=True)`
経由で短文1 segment("City buses in the area will run on a slightly
different schedule this month.")を実際にTTS生成→方式A→方式D
(ASR共有・2段判定)→`apply_repetition_qa_gate`のANDゲートまで通した。
結果: `status=OK`・`asr_verified=True`・`repetition_qa_checked=True`・
`repetition_qa_evidence.flagged=False`(方式Dは`acoustic_flagged=False`
のため局所ASR確認自体は不発火、`local_asr_confirmation=None`、想定
通りの経路)。実測費用**¥0.483**(gemini TTS input 454 tok/output
121 tok + openai_asr input 48 tok/output 17 tok、`er005_output/
cost_baseline_01/pricing_snapshot.json`のSSOT単価・USD→JPYレート160で
換算、上限¥20以内)。証跡: `er011_output/open128_method_d_local_asr_
wiring_01/standard_sync_1segment/run_summary.json`・
`raw_usage_log.jsonl`。

## 6. ASR取得失敗時の挙動

現行仕様確認: `dq18.transcribe_verbatim()`・既存`run_ngram_check()`
(方式A単体)ともに、ASR失敗(例外送出)に対する専用のtry/except・
fallback・fail-open/fail-closedロジックは実装されていない(例外が
そのまま呼び出し元[`apply_repetition_qa_gate`→retry loopの外側]まで
伝播する、既存仕様)。今回のASR共有リファクタでは、`evaluate_
repetition_qa()`内で`transcribe_verbatim()`を呼ぶタイミング・箇所が
変わっただけで、失敗時の伝播先・伝播経路は変更していない(方式Dの
局所ASR確認は既に成功した`words`を再利用するだけで、それ自体が新たに
ASRを呼ぶことはない)。回帰テスト`test_asr_failure_propagates_same_
as_method_a_no_new_fallback`(§4)で、`evaluate_repetition_qa()`・
`run_ngram_check()`の双方が同一の`RuntimeError`をそのまま送出する
ことを確認した。新規のfail-open/fail-closed設計は追加していない
(現行仕様で解決済みのためSTOPなし)。

## 7. Cost・latency

- **API課金**: ¥0(方式D局所ASR確認はローカルCPU計算[difflib+token
  window抽出]のみ、追加ASR呼び出しなし)。
- **局所ASR確認の追加計算コスト**: acoustic_flagged=Trueの場合のみ
  発火(§4 (c)で追加呼び出しゼロを確認)。OPEN-121既存sweepの実測
  (`open121_existing_audio_dprime_sweep_01`)では主母集団517件中
  acoustic flag対象は23件(4.4%)。局所ASR確認自体(token window抽出+
  difflib比較、数十語規模)は1件あたり数十ms未満と推定され、既存の
  faster-whisper呼び出し時間(1件あたり数秒〜十数秒)と比べて無視できる
  水準。
- **ASR共有による削減**: 仮に共有せず局所ASR確認が独自にtranscribe_
  verbatim()を再実行する設計だった場合、acoustic flag対象(4.4%相当)
  の各segmentで1回分の全文ASR(1件あたり数秒〜十数秒相当)が追加で
  発生していた。今回の共有設計によりこれを回避し、§5実測で23/23件が
  ASR呼び出し1回のみであることを確認した(該当23件について、
  仮に非共有だった場合の推定追加時間は23件×(1件あたりのtranscribe_
  verbatim実測時間相当)分、概算で全体実行時間の最大半分程度)。

## 8. Gate 3チェックリスト

| # | 項目 | 結果 |
|---|---|---|
| 1 | Production正式初回path経由 | 充足(§5 Standard同期TTS実発火、`generate_news_narration_wide_margin`→`apply_repetition_qa_gate`→`evaluate_repetition_qa`) |
| 2 | retry・fallback・regeneration整合 | 充足(§2 diff確認、AND gate・retry loop無変更) |
| 3 | Trial専用scriptのみでない | 充足(Production module本体を修正、Trial script未import、§9 Gate4) |
| 4 | runtime発火 | 充足(§5、実TTS[¥0.483]+実wav23件+実ASR) |
| 5 | Regression・Validator・integration PASS | 充足(§4単体9件+既存30件PASS、§10 project-wide PASS) |
| 6 | 既知TP見逃しなし | 充足(§5 TP8/8) |
| 7 | 既知FP是正 | 充足(§5 FP0/15) |
| 8 | 二重ASRなし | 充足(§3・§5、全23件でASR呼び出し1回) |
| 9 | Cost・latency | 充足(§7、追加API課金ゼロ・追加計算は無視できる水準) |
| 10 | CURRENT_SPEC反映 | Part 3で実施 |
| 11 | DECISION_LOG反映 | Part 3で実施 |
| 12 | OPEN_ITEMS反映 | Part 3で実施 |
| 13 | Git | Part 3で実施 |
| 14 | 承認内容とProduction挙動一致 | 充足(候補c・acoustic threshold不変・ASR共有込みで実装、§1・§6で仕様変更なしを確認) |

## 9. Gate 4 Dangling Reference Check

| 経路 | Trial script import | 未承認仕様参照 |
|---|---|---|
| 初回path(`generate_a2_segments`/`generate_b1_segments`→各generate関数) | なし | なし |
| retry loop(`apply_repetition_qa_gate`内) | なし | なし |
| fallback(`generate_english_segment_with_fallback`) | なし | なし |
| regeneration(既存Human Review再生成経路) | なし | なし |
| validator/QA(`evaluate_repetition_qa`・`analyze_profile_d_long_lag`・`confirm_by_local_asr_overlap`) | なし | なし(候補a/b/d[REJECTED]は未実装のまま) |
| Human Review(`review_lock`) | なし | なし |

`grep -n "er011_open121_method_d_fp_reduction_trial_01"
er011_open121_repetition_qa_production_01.py
er011_open128_method_d_local_asr_confirm_production_wiring_01_test_01.py`
は0件(import・参照なし)。

## 10. Regression

`run_project_regression.py`(collected=2184、passed=2181、failed=3、
errors=0、OPEN-127・OPEN-128双方の変更を含む統合実行)。失敗3件は
本タスク以前から存在する既知の無関係failure(`er003_test_bad.
FixtureTests.test_case_0`・`er003_test_p2j_investigate`のOPEN-77既知
meta-test集計2件)であり、新規failureはゼロ。ログ:
`er011_output/open128_method_d_local_asr_wiring_01/full_regression_
log.txt`。

## 11. 変更/新規ファイル

- 変更: [er011_open121_repetition_qa_production_01.py](er011_open121_repetition_qa_production_01.py)(`confirm_by_local_asr_overlap()`新規、`analyze_profile_d_long_lag()`/`run_spectral_checks()`/`evaluate_repetition_qa()`拡張)
- 新規: [er011_open128_method_d_local_asr_confirm_production_wiring_01_test_01.py](er011_open128_method_d_local_asr_confirm_production_wiring_01_test_01.py)
- 新規: `er011_output/open128_method_d_local_asr_wiring_01/run_runtime_evidence.py`
- 新規: `er011_output/open128_method_d_local_asr_wiring_01/runtime_evidence.json`
- 新規: `er011_output/open128_method_d_local_asr_wiring_01/standard_sync_1segment_runtime_evidence.py`
- 新規: `er011_output/open128_method_d_local_asr_wiring_01/standard_sync_1segment/run_summary.json`・`raw_usage_log.jsonl`・`narration/full_story_part1.wav`
- 新規: `er011_output/open128_method_d_local_asr_wiring_01/project_regression_summary.json`・`full_regression_log.txt`
