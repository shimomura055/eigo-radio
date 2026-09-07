# OPEN-121-TTS-REPETITION-QA-PRODUCTION-WIRING-01 レポート

管理ID: OPEN-121-TTS-REPETITION-QA-PRODUCTION-WIRING-01
Lane: Production配線(ユーザー2026-09-07`APPROVED_FOR_PRODUCTION`。
範囲=**A2/B1英語本文segment[`full_story_part1`/`full_story_part2`/
`point_one`/`point_two`]のProduction正式経路のみ**。Key Phrase・日本語
segment・Comment/Preview/Title/In One Line等は対象外)。到達Status:
**コード実装・Runtime evidence・回帰いずれも完了。Git操作は未実施**
(タスク仕様によりFableが統合commitを行う。`PRODUCTION_WIRED`の正式宣言は
commit後まで保留)。

採用元: `OPEN-121-TTS-REPETITION-HALLUCINATION-GENERAL-QA-TRIAL-01/02_
REPORT.md`(いずれも`VALIDATED`)。判定ロジック(方式A/D/D')はTrialから
無変更で移植した。

---

## 1. 配線場所

新規[er011_open121_repetition_qa_production_01.py](er011_open121_repetition_qa_production_01.py)
(Trialロジックを無変更で移植、Trialのテスト/コスト計測ハーネス等は
含めない)。

配線先(いずれも新規opt-inフラグ`enable_repetition_qa`、既定`False`、
既存`enable_connected_speech_equivalence_layer`[OPEN-122]と同一の設計
パターン):

- `er003_v1_repro01_main_generate.py::generate_narration_snippet_
  verified_strict()`(英語分岐のみ。既存`dq18.apply_disfluency_gate()`
  呼び出し直後へ`repetition_qa.apply_repetition_qa_gate()`を追加)
- `er003_v1_crosslevel_audio_02_common.py::generate_english_segment_
  with_fallback()`(標準経路は上記関数を経由、fallback[minimal
  instruction]経路にも同様のゲートを個別追加)
- `er003_v1_sing01_news_tail_fix.py::generate_news_narration_wide_
  margin()`
- `er003_v1_n3_01_tts_generate.py::generate_a2_segment_with_slowdown()`
  (フラグを中継するだけ)、`generate_a2_segments()`/`generate_b1_
  segments()`の本文4segmentループ(`full_story_part1`/`full_story_
  part2`/`point_one`/`point_two`)のみが`enable_repetition_qa=True`を
  明示的に渡す(既存`enable_connected_speech_equivalence_layer`と
  完全に同じ条件式)

いずれの経路も最終的に`apply_repetition_qa_gate()`へ到達する。既定
`False`のため、引数を渡さない全既存呼び出し元(Key Phrase・日本語・
comment/preview/title・in_one_line等)は無変更(`inspect.getsource`に
よるソースコード直接確認テストで実証、§4参照)。

---

## 2. 統合スペクトル計算の設計

方式D・D'は同一音声に対し独立に対数スペクトル自己相関(FFTフレーム
計算)を行うと同じ計算を2回行う非効率がある(Trial-02 §4/§7-5で指摘
済み)。本配線では`compute_shared_self_similarity()`で類似度行列を
1回だけ計算し、2つの独立したプロファイル関数へ渡す:

- `analyze_profile_d_long_lag()`(既存方式D): `min_lag_s=1.0`秒・
  `top_k=5`・run長計算用sim閾値`0.85`(top-k類似度優先探索)・決定
  閾値run長`0.12`秒(Trial-01較正値: 陰性最大run長0.10秒/検知対象
  陽性最小run長0.16秒)
- `analyze_profile_d_prime_short_lag()`(新方式D'): lag範囲`0.5〜2.0`
  秒・sim閾値`0.7`(run長優先探索)・決定閾値run長`0.6`秒(Trial-02
  較正値: 陰性最大run長0.5秒[`a2_comment_3`]/陽性最小run長0.7秒、
  マージン0.2秒)。full-file構成(Trial-02の推奨構成、head6s限定は
  未使用)

検知ロジック(閾値・探索アルゴリズム自体)はTrialから一切変更していない
(計算の重複だけを解消)。方式A(n-gram、`find_repeated_spans`/
`_canonical_repeat_count`/`detect_ngram_repetition`、min_words=3)も
Trial-01から無変更で移植。

**境界値monitoring**: `evaluate_repetition_qa()`はflag/非flagにかかわらず
方式D/D'それぞれの最大run長・lag・similarityを常に戻り値へ含める
(`repetition_qa_evidence`として`attempts_log`/`save_tts_attempt_audio`
のメタデータへ記録される設計。後から閾値再校正できるようにするための
記録形式、生JSONの構造は`known_positive_negative_result.json`・
`theme2_b1_fsp1_regen/run_summary.json`参照)。

**接続パターン**: 既存`er008_disfluency_qa_18.apply_disfluency_gate()`
と同一のANDゲート(`verified = verified and not evidence["flagged"]`)。
新規retry回数・新規Cost Guard予算は一切追加していない(方式A/D/D'は
いずれもローカルCPU計算のみで追加API課金ゼロ、既存`review_lock.
PRODUCTION_MAX_TTS_ATTEMPTS`予算内でretryが自動発生し、上限到達後は
既存のSTOPPED→Human Review Lock自動遷移にそのまま合流する)。

---

## 3. Runtime evidence表

| 区分 | 対象 | 結果 |
|---|---|---|
| (a)既知陽性 | Theme2 A2 Point Two(保全済attempt、句・文まるごと反復) | flagged=True(方式A・D検知、方式D'は非検知[想定通り、gap>8秒のため方式D'の対象外]) |
| (a)既知陽性 | Theme2 A2 In One Line(保全済attempt、同上型) | flagged=True(方式A・D検知) |
| (a)既知陽性 | Theme2 B1 FSP1 false start(保全済) | flagged=True(方式D'のみ検知、run長0.74秒。方式A・Dは構造的に検知不能、想定通り) |
| (b)既知陰性 | Trial-02陰性セットのEN代表10件(a2_full_story_part1/2_clean・a2_in_one_line_fixed_clean・a2_kp1-5_en・a2_point_one_clean・a2_topic_intro) | FP 0/10(全件非flag) |
| (c)Theme2 B1 FSP1再生成 | `full_story_part1`(false startが実在した原本と同一canonical text)をProduction関数`generate_news_narration_wide_margin(enable_repetition_qa=True)`でStandard同期実生成 | attempt1でstatus=OK・asr_verified=True・repetition_qa_checked=True・flagged=False(方式D'run長0.33秒、閾値0.6秒未満)。既存PASS音声・player.htmlは上書きせず新ディレクトリへ保存のみ、episode全体の再Assemblyは今回未実施 |

TP 3/3、FP 0/10(既知陰性代表10件、実データで実証)。

証跡: `er011_output/open121_tts_repetition_qa_production_wiring_01/`
(`known_positive_negative_result.json`、実行script
`known_positive_negative_runtime_evidence.py`)、
`theme2_b1_fsp1_regen/run_summary.json`(実行script
`theme2_b1_fsp1_regen_runtime_evidence.py`、`TTS_EXECUTION_MODE=STANDARD`
明示)。

---

## 4. 適用範囲限定の証拠

新規テスト`er011_open121_repetition_qa_production_wiring_01_test_01.py`
(unittest.TestCase形式、26件全PASS)の`ProductionScopeSourceInspection
Tests`クラスで以下を`inspect.getsource`により直接確認:

- `generate_key_phrase_component_verified()`のソースが`enable_
  repetition_qa`を一切含まない
- `er007_ja_secondary_asr_01.py`が本モジュールを一切importしていない
- `er003_v1_a2_audio_02_generate.py`(A2 Comment/Preview経路)が本
  モジュールを一切importしていない
- `generate_a2_segments()`/`generate_b1_segments()`内で`enable_
  repetition_qa=(`が1箇所ずつのみ出現し、対象4segmentのタプルと一致

加えて`NarrationSnippetVerifiedStrictRepetitionQaScopeTests`で、
`enable_repetition_qa`を渡さない既存呼び出し(英語・日本語とも)が
`evaluate_repetition_qa()`を一切呼ばないことをmonkeypatchで直接確認
(呼び出し回数0を実証)。

---

## 5. 境界値monitoringの記録形式

`evaluate_repetition_qa()`の戻り値構造(flag/非flagにかかわらず常に
含まれる):

```
{
  "flagged": bool,
  "duration_seconds": float,
  "method_a_ngram": {...},
  "method_d_spectral_long_lag": {
    "best_run_length_seconds": float, "min_lag_seconds": 1.0,
    "sim_threshold": 0.85, "decision_threshold_seconds": 0.12,
    "flagged": bool, "top_matches": [...]
  },
  "method_d_prime_spectral_short_lag": {
    "best_run_length_seconds": float, "time_a": float, "lag": float,
    "similarity_at_start": float, "lag_range_seconds": [0.5, 2.0],
    "sim_threshold": 0.7, "decision_threshold_seconds": 0.6,
    "flagged": bool
  }
}
```

`apply_repetition_qa_gate()`経由でProduction呼び出し時は、この構造が
`repetition_qa_evidence`として`attempts_log`各attempt・
`save_tts_attempt_audio()`のメタデータへそのまま記録される。将来
閾値を再校正する場合は、蓄積されたこれらの記録から
`method_d_spectral_long_lag.best_run_length_seconds`/
`method_d_prime_spectral_short_lag.best_run_length_seconds`の分布を
flag/非flagどちらの場合でも遡って再集計できる。

---

## 6. Regression

`run_project_regression.py`(canonical entry point): collected=2138、
passed=2135、failed=3、errors=0。failed 3件は本タスク以前から存在する
既知の無関係failure(`er003_test_bad`の意図的self-check・`er003_test_
p2j_investigate`のOPEN-77既知meta-test集計、いずれも音声/ASR/Validator
とは無関係な別ドメインのfixture)で、OPEN-122時点(collected=2112)と
同一件数のまま増加していない(新規26件が純増)。

既存`er011_keyphrase_en_asr_false_rejection_cascade_prod_wiring_01_
test_01.py`(5件)・`er011_tts_attempt_audio_retention_wiring_01_test.py`
(9件)は新規kwarg追加後も無変更でPASS(既存fake関数が`**kwargs`受け皿
のため破壊的影響なし、mock signature更新は不要だった)。

新規[er011_open121_repetition_qa_production_wiring_01_test_01.py]
(er011_open121_repetition_qa_production_wiring_01_test_01.py)26件
(unittest.TestCase形式、`run_project_regression.py`のglobパターン
`er0*_test_*.py`に実際に収集される、OPEN-122の姉妹テストが平文function
形式で回帰収集されなかった既知gapを踏まえた選択)全PASS:
- 方式A(n-gram)判定ロジック3件(合成データ)
- 方式D/D'(スペクトル、統合計算)実fixture5件
- 統合判定(方式A+D+D')実fixture end-to-end 3件
- `apply_repetition_qa_gate()`ANDゲート4件
- Production配線(適用範囲限定)9件(`generate_narration_snippet_
  verified_strict`・`generate_english_segment_with_fallback`・
  `generate_news_narration_wide_margin`のopt-in/デフォルト無効/日本語
  独立性確認)
- ソースコード直接確認によるスコープ限定証拠4件

---

## 7. model/routing/cost

- Primary ASR: `gpt-4o-mini-transcribe`(既存`er006_asr_provider_
  routing_01.py`、変更なし)
- TTS: Gemini(既存`er003_b1_p9a_audio.py`/`er006_batch_tts_wiring_01.py`
  経由、変更なし)。Theme2 B1 FSP1再生成は`TTS_EXECUTION_MODE=STANDARD`
  を明示指定(タスク仕様の「Standard同期」要件)
- 方式A/D/D': ローカルfaster-whisper(`small`モデル、CPU)+ローカル
  NumPy FFT計算のみ、追加API課金ゼロ

Cost実測合計: **¥3.64**(Theme2 B1 FSP1再生成1回分、gemini TTS 1回
[570 input/1050 output tokens]+openai_asr 1回[420 input/127 output
tokens]、`er005_output/cost_baseline_01/pricing_snapshot.json`の公式
価格・1USD=160円換算)。既知陽性/陰性のRuntime evidence(§3(a)(b))は
既存保全音声・既存PASS音声の読み取りのみで追加API課金なし。上限¥500に
対し0.7%。

---

## 8. 未配線ギャップ(正直に記録)

1. **gap<0.5秒の即座の言い直し(Trial-01方式C-v2)は今回配線していない**
   (タスク仕様により対象外と明示された既知ギャップ)。`OPEN_ITEMS.md`
   OPEN-121行へ項番(7)として追跡項目を明記した。
2. Secondary ASR(Azure)窓検知・A-ext v2(単語duration異常)は今回配線
   していない(タスク仕様によりcorroboration専用または対象外、OPEN_
   ITEMS.md既存USER_DECISION_REQUIRED項目のまま)。
3. A2 6% time-stretch後の独立再検証経路(`apply_a2_slowdown_
   postprocess`、`classify_asr_match()`を直接呼ぶだけの別コードパス)
   には今回も配線していない(OPEN-122と同一の既知ギャップ、既存slowdown
   retry機構で吸収されるため安全上の懸念は低い)。
4. Theme2 B1 episode全体の再Assemblyは今回行っていない(タスク仕様
   により、FSP1単体のPASS音声とrun-summaryのみを取得する段階に限定)。

---

## 9. USER_DECISION_REQUIRED

新規のUSER_DECISION_REQUIREDは発生していない。OPEN_ITEMS.md OPEN-121
行に既存記録済みの未決事項(Point Two残存重複の扱い・disfluency QA
検知ロジック自体の一般拡張・適用スコープの一般拡張・Production ASR
非決定性への一般対応方針・gap<0.5秒C-v2の扱い)は、今回の承認範囲
(A+D+D'をA2/B1英語本文4segmentへ配線することのみ)を超える論点として
引き続き未決のまま維持した(いずれもユーザー承認なしに実装しない)。

---

## 10. 変更ファイル一覧

### 新規

- `er011_open121_repetition_qa_production_01.py`(Production判定ロジック
  本体)
- `er011_open121_repetition_qa_production_wiring_01_test_01.py`(単体
  テスト26件)
- `OPEN-121-TTS-REPETITION-QA-PRODUCTION-WIRING-01_REPORT.md`(本ファイル)
- `er011_output/open121_tts_repetition_qa_production_wiring_01/`配下
  (`known_positive_negative_runtime_evidence.py`・
  `known_positive_negative_result.json`・
  `theme2_b1_fsp1_regen_runtime_evidence.py`・
  `theme2_b1_fsp1_regen/`[narration・run_summary.json・raw_usage_log.jsonl・
  review_lock監査])

### 既存編集

- `er003_v1_repro01_main_generate.py`(`generate_narration_snippet_
  verified_strict()`へ新規kwarg`enable_repetition_qa`追加・ゲート接続)
- `er003_v1_crosslevel_audio_02_common.py`(`generate_english_segment_
  with_fallback()`へ新規kwarg追加・標準/fallback両経路へ転送・ゲート
  接続)
- `er003_v1_sing01_news_tail_fix.py`(`generate_news_narration_wide_
  margin()`へ新規kwarg追加・ゲート接続)
- `er003_v1_n3_01_tts_generate.py`(`generate_a2_segment_with_slowdown()`
  へ新規kwarg追加・転送、A2/B1本文4segmentループでのみ`True`を明示的に
  渡すよう変更)
- `CURRENT_SPEC.md`・`DECISION_LOG.md`・`OPEN_ITEMS.md`(SSOT更新)

---

## 11. Git

**未実施**。タスク仕様により本タスクではコード変更・テスト追加・
Runtime evidence取得のみを行い、commit/pushは一切行っていない。Fableが
統合commitを行った後に`PRODUCTION_WIRED`を正式宣言する。

なお作業中、本タスクと無関係な既存差分(`er006_preprod_hardening_01_
validation.py`の`OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-PRODUCTION-
WIRING-01`関連変更、他タスクによる既存dirty state)を確認したが、
一切編集・stageしていない(統合commit時にFableが別途扱う対象)。
