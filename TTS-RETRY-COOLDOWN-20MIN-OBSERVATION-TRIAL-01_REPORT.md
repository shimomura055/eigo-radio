# TTS-RETRY-COOLDOWN-20MIN-OBSERVATION-TRIAL-01

## 要点(5行)
1. ユーザー決定(2026-09-12)に基づき、Production retry cascade・Review Lock・
   Gateを一切変更せず、その「外側」に差し込むTrial限定の観測フック
   `er011_tts_cooldown_observation_01.py`を新規実装した(3回連続NG検知後、
   既定OFF・`TTS_COOLDOWN_OBSERVATION=1`のときのみ約20分待機→4回目を1回だけ
   実行→結果を`er011_output/tts_cooldown_observation_01/observations.jsonl`
   へ追記)。
2. Production安全性を3点で機械的に保証した: (1)Review Lock関数
   (`check_before_generation`/`record_outcome`/`approve_regenerate`)を
   一度も呼ばないためProduction状態(review_lock_state.json)は不変、
   (2)`approve_regenerate()`等の人的介入APIを一切呼ばない
   (`no_human_intervention: True`を機械記録)、(3)4回目がPASSしても
   `auto_adopted_to_production: False`を常に記録し自動採用しない(採用は
   既存Human Review機構経由でユーザーが個別判断)。
3. パラメータ不変性は、待機前後で`params`辞書+呼び出し側の`capture_live_
   params_fn()`(ライブ設定再読込)の両方のhashを機械照合することで保証する。
   不一致なら4回目attempt自体を実行せず「観測無効」として記録する
   (コスト浪費防止)。
4. 複数segment同時STOPPEDへの対応は、`ThreadPoolExecutor`によるsegment毎の
   独立並列待機(`run_batch_observations()`)。offline testで4segment×0.5秒
   待機が直列(2.0秒)より明確に短い時間で完了することを確認した(実測
   0.532秒台、4segment分含む全8 testで確認)。
5. Offline test(`er011_tts_cooldown_observation_01_test_01.py`、8件、API
   呼び出し0件・¥0)は全件PASS。本タスクでは実際の3回連続NG→20分待機→
   4回目の実運用は**まだ実行していない**(データ収集は次回以降のTrial実行で
   自然発生する3連続NGを起点に開始する設計)。Closeoutは
   **進行中(データ収集前)**。

---

## 1. 設計

### 1.1 入力
- `level_dir`, `segment_id`, `canonical_text`, `language`
- `three_attempt_records`: 3回連続NG(`verified=False`x3)の直近3回分のattempt
  記録(既存`narration/attempts/*.json`と同一スキーマを想定)
- `params`: 4回目に渡す全パラメータ(voice/model/route/tts設定/prompt本文等、
  呼び出し側が3回目attemptと同一の値を明示的に渡す)
- `single_attempt_fn`: 4回目を1回だけ実行する呼び出し可能オブジェクト
  (**Review Lockデコレータを外した生の関数**、例:
  `er003_v1_repro01_main_generate.generate_narration_snippet_verified_
  strict.__wrapped__`。`functools.wraps`により`__wrapped__`属性で元関数へ
  到達できる)

### 1.2 動作フロー
1. `TTS_COOLDOWN_OBSERVATION != "1"` → 何もせず`SKIPPED_DISABLED`を記録して
   return(0 API call)。
2. `three_attempt_records`が3件かつ全件`verified=False`でない場合 →
   `INELIGIBLE_NOT_EXACTLY_THREE_CONSECUTIVE_NG`を記録してreturn。
3. `params`のhash(+`capture_live_params_fn()`のhash、任意)を待機前に取得。
4. `TTS_COOLDOWN_SECONDS`(既定1200秒=20分)だけ`sleep_fn`で待機し、実測待機
   秒数(`actual_wait_seconds`)を記録。
5. 待機後、同じhashを再取得し完全一致を照合。
   - 不一致 → `OBSERVATION_INVALIDATED_PARAM_CHANGE`を記録し、**4回目
     attempt自体を実行しない**(コスト浪費防止)。
   - 一致 → `single_attempt_fn`を1回だけ呼び出し、結果(`status`/
     `asr_verified`/`reason`/`audio_classification`)をそのまま記録
     (`OBSERVED`、`fourth_attempt_result_status`=PASS/NG)。
6. いずれの分岐でも`no_human_intervention: True`・`production_state_
   modified: False`・`auto_adopted_to_production: False`を機械的に記録する。

### 1.3 なぜReview Lockをバイパスするのか(Production安全性の核心)
3回連続NGの時点でProduction側`review_lock_state.json`は既に
`HUMAN_REVIEW_REQUIRED`。もし観測フックがデコレータ付きの関数
(`generate_narration_snippet_verified_strict`そのもの)を呼べば、
`check_before_generation()`が即ブロックし観測不能になる(意図した安全装置)。
そこで観測フックは**デコレータの外側の生関数**(`__wrapped__`)を、
**Production成果物とは別のout_path**で直接呼ぶ設計にした。これにより:
- Production側`review_lock_state.json`・`tts_generation_results.json`・
  最終成果物wavは一切変更されない(観測は完全に副作用のない別系統)。
- 4回目がPASSしても、それはあくまで「観測記録」であり、Production側は
  STOPPEDのまま(採用には既存Human Review機構が必要、1.4節参照)。

### 1.4 採用する場合の手順(4回目PASS時、Production採用は別途ユーザー判断)
1. ユーザーが`observations.jsonl`の該当レコード(4回目のASR文字起こし・
   分類・生成した音声[観測用out_pathに保存されている])を確認する。
2. 採用してよいと判断した場合のみ、`review_lock.approve_regenerate(out_path,
   text, approved_by=...)`をユーザー自身の指示に基づき明示的に呼ぶ
   (=Production側`REGENERATE_APPROVED`へ遷移)。
3. その後、Production側の生成関数(cascade呼び出し元)を通常どおり再実行し、
   `REGENERATE_APPROVED`を消費させる(Production側で改めてTTS+ASRを実行する
   ため、観測用に生成した音声ファイルをProduction out_pathへ直接コピーする
   といったReview Lock迂回は行わない)。

### 1.5 複数segment同時STOPPED時の並列待機設計
`run_batch_observations(segment_jobs)`は`concurrent.futures.
ThreadPoolExecutor`でsegment毎に独立したworker threadを立てる。待機は
`time.sleep`(I/O待ち、GIL解放)のため、N segmentの20分待機がほぼ重なり合い、
合計wall時間は「約20分+各segmentの生成時間」のオーダーに収まる
(直列だと20分×Nになるところを回避)。offline testで4segment×0.5秒待機が
合計0.532秒程度(8 test全体の合計実行時間)で完了することを確認済み
(直列なら2.0秒程度かかるはずの箇所)。

---

## 2. 配線指示書(次のconsolidationで適用、本タスクでは未編集)

以下は**編集していない**。次回、この管理IDの配線consolidationタスクで
適用する変更箇所の指示のみ記載する。

### 2.1 A-Family Discovery/News Trial: `er011_discovery_generalization_towels_trial_11_audio_run.py`
- **このファイルは本タスクでは編集禁止**(別タスクが実行中)。次回
  consolidation時、以下の箇所へ挿入する:
  - `run_level()`関数(370行目付近)、`lock_summary = lock_summary_stage(level)`
    (370行目)の直後・`assembly_result = assembly_stage(level)`(371行目)の
    直前に、新規`cooldown_summary = tts_cooldown_observation_stage(level,
    lock_summary)`を追加。
  - 新規関数`tts_cooldown_observation_stage(level, lock_summary)`
    (`lock_summary_stage()`定義[308行目]の直後に追加想定)は、
    `lock_summary["locked_or_review_required_segments"]`の各`segment_id`
    について、`{OUT_DIR}/{level}/narration/attempts/{segment_id}_attempt*.
    json`から直近3件(`verified=False`x3であること)を読み込み、
    `er011_tts_cooldown_observation_01.run_batch_observations()`へ渡す
    ジョブ一覧を組み立てて呼び出す。
  - `single_attempt_fn`は、対象segmentが`generate_a2_segments`/
    `generate_b1_segments`(`er003_v1_n3_01_tts_generate.py`)経由で
    どの内部関数(`generate_narration_snippet_verified_strict`/
    `generate_english_segment_with_fallback`/`generate_a2_japanese_with_
    fallback`等)へルーティングされたかをsegment種別から判定し、対応する
    `.__wrapped__`版をmax_attempts=1で束縛(`functools.partial`)して渡す。

### 2.2 News Trial: `er011_news_stage3_new_theme_ledger_trial_09_b1b_full_pipeline.py`
- `main()`関数(172-173行目)、`tts_result = run_tts()`(172行目)の直後・
  `assemble_result = run_assembly()`(173行目)の直前に、新規
  `cooldown_result = run_cooldown_observation_stage(tts_result)`を追加。
- 新規関数`run_cooldown_observation_stage(tts_result)`(`run_tts()`定義
  [130-134行目]の直後に追加想定)は、`tts_result`内で`status`が`STOPPED`
  だったsegmentを抽出し、`{LEVEL_OUT_DIR}/narration/attempts/{segment_id}_
  attempt*.json`の直近3件を読み込んで2.1と同様に
  `run_batch_observations()`を呼ぶ。

### 2.3 B-Family Trial: `er012_editorial_b_voices_trial_09_audio.py`(以降のtrial_10以上でも同型)
- `run_tts_new_segments()`関数内、Voice A/B本文ループ(754-764行目)、
  `results[name] = generate_voice_body_wide_margin(...)`(761-762行目)の
  直後に、`if results[name].get("status") == "STOPPED": cooldown_jobs.
  append(...)`を追加し、ループ終了後(764行目`assert_budget_ok(...)`の後)
  で`er011_tts_cooldown_observation_01.run_batch_observations(cooldown_jobs)`
  を1回呼ぶ(segment毎に即時呼ぶのではなくバッチ化し、複数segment同時
  STOPPEDでも並列待機の恩恵を受ける)。
- `single_attempt_fn`は`generate_voice_body_wide_margin.__wrapped__`
  (`@review_lock.guarded_generate("en")`デコレータの生関数)を
  `max_attempts=1`で束縛して渡す。`out_path`はProduction成果物
  (`{NARRATION_DIR}/{name}.wav`)ではなく、Trial専用の観測パス
  (例: `{NARRATION_DIR}/_cooldown_observation_01/{name}.wav`)にする。
- `capture_live_params_fn`は、`{"model": p9a.ENGLISH_MODEL_NAME, "voice":
  voice_name, "style_prefix": p9a.ENGLISH_STYLE_PREFIX, "safety_margin":
  news_tail_fix.LONG_FORM_TRIM_SAFETY_MARGIN_SECONDS}`を返すlambdaとする
  (待機前後で該当するProduction定数が変わっていないかを機械検証するため)。

### 2.4 共通の未実施事項(次回consolidationでの確認事項)
- いずれの配線も、`three_attempt_records`の抽出元は
  `narration/attempts/*.json`(既存の保存済みattempt記録)であり、
  `style_prefix_override`/`asr_prompt`本文等、ログへ保存されない一部の
  呼び出し時kwargsは、Trial harness側のその場のローカル変数(3回目
  attemptを実際に生成したのと同じ呼び出しコンテキスト)から`params`/
  `single_attempt_kwargs`へ明示的に渡す必要がある(1.3節の限界注記参照)。
- **Production runner(`er012_b_family_voices_production_01.py`等)には
  組み込まない**(本タスクの指示範囲外、Trial限定)。

---

## 3. 事前定義の十分性基準と比較設計

### 3.1 baseline(比較対象)
- **baseline A(同一Trial群、即時)**: 「2回連続NG後の3回目(即時、<5分)
  PASS率」。既存`er011_output/tts_retry_timing_monitor_01/summary.json`の
  表1(`consecutive_ng_before_bucket=="2"`)実測値: **N=12、PASS率16.7%**
  (95%Wilson CI [4.7%, 44.8%]、`TTS-RETRY-TIMING-SELECTION-EFFECT-
  REANALYSIS-01_REPORT.md`「選別効果の可視化」節より再掲)。
- **baseline B(過去データ、3回以上NG後の即時4回目)**: 現行アーキテクチャ
  では「`max_attempts`到達後、人的介入なしで即座に4回目が自動実行される」
  ケースは構造的に存在しない(`review_lock.py`の設計上、4回目以降は必ず
  人間が明示的に`approve_regenerate()`を呼ぶ)。よって**N=0**(観測不能)。
  この空白こそが今回の観測フックが埋めようとしている部分である
  (=本Trialの20分待機・4回目1回のみ実行という設計は、`max_attempts`到達
  直後に人的介入なしで4回目を実行できる、初めての機械的経路)。

### 3.2 比較設計と因果主張の限界
ユーザー指定手順(3回NG後、常に20分待ってから4回目)は**単群観測**であり、
「20分待ったからPASSした」のか「4回目という順番自体でPASSしやすい
(選別効果)」のかを、この設計だけでは分離できない。真に「時間経過単独の
効果」を主張するには、**Trial限定でのランダム化対照実験**
(3回NG後、即時4回目群/20分後4回目群へ無作為割当)が必要である。

- **既定(ユーザー指定手順)**: 3回NG後は必ず20分待ってから4回目
  (ランダム化なし、単群)。まずこの単群でPASS率が上記baseline A/Bより
  明確に高いかどうかの傾向を見る(数時間待つ方式より開発速度を落とさない
  というユーザー方針に従う)。
- **選択肢(ランダム化対照)**: 因果主張が必要になった段階
  (単群観測でPASS率が明確に高い傾向が見えた場合等)で、
  Trial限定のランダム化対照(即時4回目 vs 20分後4回目)を追加実施するか
  どうかは、**closeout時にUSER_DECISION_REQUIREDとして提示する**
  (本タスクの範囲では実装・実施しない)。

### 3.3 必要N(検出力計算、想定効果量: PASS率差20pt)
`TTS-RETRY-TIMING-SELECTION-EFFECT-REANALYSIS-01_REPORT.md`の検出力計算
(alpha=0.05、power=0.80、正規近似)をそのまま再掲する:

| 即時PASS率(仮定) | 非即時(20分後)PASS率(仮定) | 差(ポイント) | 必要N/群 |
|---|---|---|---|
| 10% | 40% | 30 | 29 |
| **20%** | **40%** | **20** | **79** |
| 30% | 40% | 10 | 354 |

指示された想定効果量(PASS率差20pt、20%→40%相当)では、**各群79件程度**の
自然発生(または今後のランダム化Trialでの)観測が必要。現時点(本タスク終了
時点)では単群手順の実測値も0件(データ収集前)であり、この必要件数に対し
有効サンプルはゼロ。

---

## 4. Offline test結果

`er011_tts_cooldown_observation_01_test_01.py`(8 test、API呼び出し0件、
TTS/ASRは全てモック関数に差し替え、¥0):

```
test_appends_to_observations_jsonl ... ok
test_cooldown_seconds_from_env_var ... ok
test_default_off_is_noop ... ok
test_enabled_params_unchanged_fourth_ng ... ok
test_enabled_params_unchanged_fourth_pass ... ok
test_ineligible_when_not_exactly_three_ng ... ok
test_param_change_invalidates_observation_and_skips_fourth_attempt ... ok
test_run_batch_observations_runs_concurrently ... ok

Ran 8 tests in 0.532s
OK
```

実行コマンド: `python -m unittest er011_tts_cooldown_observation_01_test_01 -v`
(2026-09-12実行、Windows環境、実行環境ローカル)。

pin済み事項:
- 既定OFF(`TTS_COOLDOWN_OBSERVATION`未設定)ではno-op(sleep/4回目生成とも
  0回呼び出し)。
- 3回連続NG(`verified=False`x3)以外は対象外(`INELIGIBLE_...`)。
- パラメータ同一性検証: 待機前後で`params`/ライブ設定hashが一致すれば
  4回目実行、不一致なら4回目をスキップし観測無効化。
- 4回目PASSでも`auto_adopted_to_production=False`・`production_state_
  modified=False`を常に記録(自動採用しない)。
- `observations.jsonl`は追記のみ(上書きしない、複数回呼び出しで行数が
  累積することを確認)。
- `run_batch_observations()`は4segment×0.5秒待機ジョブを、直列実行の想定
  時間(2.0秒)より明確に短い時間で完了させる(並列独立待機の裏付け)。

---

## 5. 費用見込み

- 本タスク自体はAPI呼び出し0件(¥0、モックのみ)。
- 実運用時、4回目1回の実行コストは「通常のTTS 1回 + ASR検証1回(cascade
  発動時は追加Secondary ASR呼び出しを含みうる)」相当であり、既存retry
  cascadeの1 attempt分と同一オーダー(既存`er005_cost_logger`の実測ログ
  [`raw_usage_log.jsonl`等]を参照すれば、対象segment種別ごとの過去実測
  yen単価がそのまま流用できる、新しいコスト構造は導入していない)。
- パラメータ変更検知で観測が無効化された場合は4回目自体を実行しないため、
  その回のコストは発生しない(0円)。

---

## 6. Closeout

- **判定: 進行中(データ収集前)**。REJECTED/VALIDATED/USER_DECISION_REQUIRED
  のいずれの判定も、実際の3回連続NG→20分待機→4回目1回の実測データが
  1件も無い現時点では出せない。
- 次のTrial実行(A-Family Discovery/News Trial、B-Family Trial、2.1〜2.3節の
  配線適用後)で自然発生する3連続NGから観測を開始する。目標件数は3.3節の
  必要N(20pt効果量想定で各群79件程度)。
- ランダム化対照(即時4回目 vs 20分後4回目)を追加実施するかどうかは、
  今回のTrialで単群観測がある程度蓄積した段階で、改めて
  USER_DECISION_REQUIREDとして提示する(3.2節)。
- Production採用(`APPROVED_FOR_PRODUCTION`)は本タスクの範囲外であり、
  引き続き人間ユーザーの判断事項。

---

## 7. 出力・証跡パス
- 新規module: `er011_tts_cooldown_observation_01.py`(観測フック本体、
  Production retry/cascade/Gateコードを一切import・変更しない)
- 新規offline test: `er011_tts_cooldown_observation_01_test_01.py`
  (8 test、API呼び出し0件、¥0)
- 出力(実運用開始後に追記される想定、本タスク終了時点ではまだ0件):
  `er011_output/tts_cooldown_observation_01/observations.jsonl`
- 参照した既存REPORT: `TTS-RETRY-TIMING-SELECTION-EFFECT-REANALYSIS-01_
  REPORT.md`、`TTS-REGENERATION-TIMING-DEPENDENCY-ANALYSIS-01_REPORT.md`
- 参照した既存Production/Trialコード(読み取りのみ、無変更):
  `er011_human_review_lock_01.py`、`er003_v1_repro01_main_generate.py`、
  `er011_tts_retry_timing_monitor_01.py`、
  `er011_discovery_generalization_towels_trial_11_audio_run.py`(**このタスク
  では未編集、別タスクが実行中のため**)、
  `er011_news_stage3_new_theme_ledger_trial_09_b1b_full_pipeline.py`(未編集)、
  `er012_editorial_b_voices_trial_09_audio.py`(未編集)。
- 本タスクでの変更: 上記2新規ファイル・本REPORTのみ。SSOT
  (`CURRENT_SPEC.md`等)・`docs/pm/`・Production retry/cascade/Gateコード・
  `er011_discovery_generalization_towels_trial_11_audio_run.py`は無変更。
  API呼び出し・TTS/ASR生成は0件(¥0)。Git操作(`add`/`commit`/`push`)は
  本タスクでは実施していない(上位から明示的な指示があれば別途)。
