# OPEN-127-EM-DASH-TOKEN-BOUNDARY-PRODUCTION-WIRING-01 レポート

管理ID: OPEN-127-EM-DASH-TOKEN-BOUNDARY-PRODUCTION-WIRING-01
Lane: Production配線(ユーザー2026-09-08`APPROVED_FOR_PRODUCTION`。
candidate1a[em dash(—, U+2014)のみを空白=token境界として扱う前処理]、
en dash(–)・hyphen(-)は対象外、汎用regex tokenizerへの拡張は禁止)。
到達Status: **コード実装・回帰テスト・Runtime evidence・project-wide
regression いずれも完了**。Git操作はPart 3で実施。

採用元: `TTS-REPETITION-QA-INTENTIONAL-REPEAT-FALSE-POSITIVE-TRIAL-01_
REPORT.md`(candidate1a、`VALIDATED`)。判定ロジックはTrialから無変更。

---

## 1. 実装箇所

[er011_open121_repetition_qa_production_01.py](er011_open121_repetition_qa_production_01.py)
`_normalize_tokens()`(方式A・`_canonical_repeat_count()`のcanonical側
tokenization専用関数)へ1行追加:

```python
def _normalize_tokens(text):
    text = re.sub("—", " ", text)  # OPEN-127: em dash(U+2014)のみ空白へ
    return [dq18._normalize_token(w) for w in text.split()]
```

`import re`をファイル冒頭へ追加。Trial candidate1aと完全に同一のロジック
(1関数・1行のみ)。ASR側token(`detect_ngram_repetition`が使う
`words`、faster-whisper word-level出力)はem dashという文字自体が
書き起こしに現れないため無変更。en dash(–, U+2013)・hyphen(-)・
%記号・小数点数字は対象外のまま(regressionテストで確認、§2)。

## 2. 回帰テスト

`er011_open121_repetition_qa_production_wiring_01_test_01.py`
`NgramRepetitionLogicTests`クラス直後へ`EmDashTokenBoundaryTests`
(4件)を追加(全PASS、既存30件と合わせて計34件全PASS):

- (a) `test_a_voice_b_style_intentional_repeat_canonical_2_asr_2_not_
  flagged`: Voice B point_two実データ(`...I need—or do not need—around
  me.`)相当。「do not need」がcanonical・ASR双方で2回ずつ出現する
  意図的な並行構文がflagged=Falseとなることを確認。
- (b) `test_b_true_duplicate_canonical_1_asr_2_still_flagged`:
  em dashが無関係箇所に存在しても、canonical側1回・ASR側2回の真の
  重複は引き続きflagged=Trueであることを確認。
- (c) `test_c_hyphen_en_dash_percent_numeric_cases_unchanged`:
  hyphen(`well-known`)・en dash(`10–12`)・%記号・小数点数字
  (`108.95`)いずれも`_normalize_tokens()`の出力が既存
  `dq18._normalize_token`ベースの分割と完全一致(無変更)であることを
  確認。
- (d) `test_d_em_dash_with_and_without_surrounding_whitespace`:
  `"need—or"`(空白なし)・`"need — or"`(空白あり)の両方が
  `["need", "or"]`へ正しく分割されることを確認。

## 3. Production正式path(コード追跡)

`enable_repetition_qa=True`を渡す既存4segmentループ
(`er003_v1_n3_01_tts_generate.py::generate_a2_segments()`/
`generate_b1_segments()`、`full_story_part1/2`・`point_one`・
`point_two`のみ)→各種generate関数(`generate_narration_snippet_
verified_strict()`等、OPEN-121-TTS-REPETITION-QA-PRODUCTION-WIRING-01
で配線済み・無変更)→retry loop内`apply_repetition_qa_gate()`→
`evaluate_repetition_qa()`→`run_ngram_check()`→`detect_ngram_
repetition()`→`_normalize_tokens(canonical_text)`(修正箇所)。
flag時は既存のretry loop(TTS再生成→ASR再判定)へそのまま合流し、
`review_lock.PRODUCTION_MAX_TTS_ATTEMPTS`上限到達後は既存のSTOPPED→
Human Review Lock自動遷移に合流する(新規retry・新規Cost Guardは
追加していない、無変更)。

## 4. Runtime evidence

`er011_output/open127_em_dash_wiring_01/run_runtime_evidence.py`
(Production entry`evaluate_repetition_qa()`を直接呼ぶ、ローカル
faster-whisperのみ・追加API課金ゼロ)。

- **positive controls(10件、既知真の重複)**: `method_d_flag23_
  review_01/classification_table.json`index0-7(真の重複8件)+
  known_case 2件(`point_two_BUGGY_UNFIXED_backup`・`in_one_line_
  BEFORE_FIX_buggy_backup`)。結果: **10/10 flagged=True**維持。
- **negative controls(4件、Voice B意図的並行構文)**: phase1_02
  point_two attempt1-3(実wav・実ASR)+ trial_08 point_two。結果:
  **4/4 flagged=False**(修正前は4/4ともflagged=True)。
  `method_a_ngram_flagged`はいずれもFalse(em dash修正が正しく機能)。
  attempt3のみ、修正直後の中間状態では方式D(spectral、em dashとは
  無関係な独立の誤flag、run=0.12秒でOPEN-121既知FP帯)により全体
  flagged=Trueが一時的に残っていたが、OPEN-128配線後の再実行で
  4/4ともflagged=False(§5参照)。

証跡: `er011_output/open127_em_dash_wiring_01/runtime_evidence.json`
(OPEN-128配線後の最終実行結果を含む、`run_runtime_evidence.py`は
2回実行し2回目の結果で上書き)。

## 5. OPEN-128配線との相互作用(隠蔽せず記録)

OPEN-127単体を配線した直後、phase1_02 attempt3の runtime evidence で
`method_a_ngram_flagged=False`(em dash修正は正しく機能)にもかかわらず
`method_d_spectral_long_lag.acoustic_flagged=True`(run長0.12秒、
OPEN-121既知のFP帯[0.12〜0.16秒])により全体`flagged=True`が一時的に
残る事実を発見した。これはOPEN-127のスコープ外(方式D単体の誤flag、
無関係な既存事象)であり、OPEN-127の修正自体に不備はない。OPEN-128
(方式D局所ASR確認)配線後に同一runtime evidenceスクリプトを再実行した
ところ、attempt3を含む4/4全件がflagged=Falseとなることを確認した
(§4記載の最終結果)。

## 6. Regression

`run_project_regression.py`(collected=2184、passed=2181、failed=3、
errors=0)。失敗3件は本タスク以前から存在する既知の無関係failure
(`er003_test_bad.FixtureTests.test_case_0`[意図的なself-check
fixture]、`er003_test_p2j_investigate`のOPEN-77既知meta-test集計
2件)であり、新規failureはゼロ。ログ:
`er011_output/open128_method_d_local_asr_wiring_01/full_regression_
log.txt`(OPEN-127・OPEN-128双方の変更を含めた統合実行、Part 2参照)。

## 7. Gate 3チェックリスト

| # | 項目 | 結果 |
|---|---|---|
| 1 | Production正式初回path経由 | 充足(§3、コード追跡+§4 Production entry`evaluate_repetition_qa()`直接実行) |
| 2 | retry・fallback・regeneration整合 | 充足(既存ANDゲート・retry loop無変更、新規ロジックなし) |
| 3 | Trial専用scriptのみでない | 充足(Production module本体を修正、Trial script[`er011_repetition_qa_intentional_repeat_trial_01.py`]は未import、§Gate4) |
| 4 | runtime発火 | 充足(§4、実wav・実ASRで実行) |
| 5 | Regression・Validator・integration PASS | 充足(§2単体34件PASS、§6 project-wide PASS) |
| 6 | 既知TP見逃しなし | 充足(§4 positive 10/10維持) |
| 7 | 既知FP是正 | 充足(§4 negative 4/4是正、最終確認は§5経由) |
| 8 | 二重ASRなし(該当する場合) | 対象外(OPEN-127はASR呼び出し回数に影響しない、OPEN-128側で確認) |
| 9 | Cost・latency | 充足(追加API課金ゼロ、ローカルCPU計算1行追加のみで計算量増加なし) |
| 10 | CURRENT_SPEC反映 | Part 3で実施 |
| 11 | DECISION_LOG反映 | Part 3で実施 |
| 12 | OPEN_ITEMS反映 | Part 3で実施 |
| 13 | Git | Part 3で実施 |
| 14 | 承認内容とProduction挙動一致 | 充足(承認範囲=em dashのみ・en dash/hyphen対象外、実装・テストとも一致) |

## 8. Gate 4 Dangling Reference Check

| 経路 | Trial script import | 未承認仕様参照 |
|---|---|---|
| 初回path(`generate_a2_segments`/`generate_b1_segments`→各generate関数) | なし | なし |
| retry loop(`apply_repetition_qa_gate`内) | なし | なし |
| fallback(`generate_english_segment_with_fallback`) | なし | なし |
| regeneration(既存Human Review再生成経路) | なし | なし |
| validator/QA(`evaluate_repetition_qa`・`detect_ngram_repetition`) | なし | なし(candidate2[汎用regex tokenizer]・candidate1b[en dash込み]はいずれも未採用のまま) |
| Human Review(`review_lock`) | なし | なし |

`grep -n "er011_repetition_qa_intentional_repeat_trial_01"
er011_open121_repetition_qa_production_01.py
er011_open121_repetition_qa_production_wiring_01_test_01.py`は0件
(import・参照なし)。

## 9. 費用

¥0(TTS/LLM有料API呼び出しなし、faster-whisperローカルCPU実行のみ)。

## 10. 変更/新規ファイル

- 変更: [er011_open121_repetition_qa_production_01.py](er011_open121_repetition_qa_production_01.py)(`_normalize_tokens()`1行追加、方式D関連はOPEN-128参照)
- 変更: [er011_open121_repetition_qa_production_wiring_01_test_01.py](er011_open121_repetition_qa_production_wiring_01_test_01.py)(`EmDashTokenBoundaryTests`4件追加)
- 新規: `er011_output/open127_em_dash_wiring_01/run_runtime_evidence.py`
- 新規: `er011_output/open127_em_dash_wiring_01/runtime_evidence.json`
