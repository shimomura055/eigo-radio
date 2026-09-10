# TTS-RETRY-TIMING-OBSERVATION-MONITOR-01 調査報告

読み取り専用の集計基盤構築(¥0、API呼び出しなし、追加TTS生成なし、SSOT/Production Prompt・コード・docs/pm/は無編集、Git操作なし)。先行調査`TTS-REGENERATION-TIMING-DEPENDENCY-ANALYSIS-01_REPORT.md`(CAR-T記事`full_story_part1`の3回連続NG→14時間21分後PASS 1件)を土台に、同種の観測を継続的・機械的に再現できる決定論的(LLM不使用)集計scriptを作成し、初回集計を実施した。

## サマリー(5行)

1. scriptは `er011_tts_retry_timing_monitor_01.py`。`er0*_output/**/narration/attempts/*.json` 421件(既知の重複なし、冪等=再実行でハッシュ完全一致を確認済み)を横断走査し、320 segment系列(うちattempt2回以上=77系列)に整理した。
2. 種別B(品質NG)の直前連続NG回数×retry間隔bucketの表で、短間隔(<5分)・連続NG1回後のPASS率は67.7%(N=34)、連続NG2回後は22.2%(N=9)、連続NG3回以上後は33.3%(N=3)。長間隔(30分〜6時間)・連続NG3回以上後はN=1で**失敗**(kp5_ja_charon、39分)。6時間以上の間隔・連続NG3回以上後はN=1で**成功**(CAR-T `full_story_part1`、14時間21分)。**いずれのセルもN=1〜9の極小サンプルであり、傾向と呼べる段階ではない(先行調査の判定を覆す材料はない)**。
3. 類似事例5パターン全てに該当例が見つかった: 即時NG×1→PASS(25系列)、即時NG×2→後でPASS(2系列)、NG×3以上→後でPASS(3系列: household point_one/9.45分、kp5_ja_charon/7回中6NG、CAR-T/14時間21分)、間隔を空けてもNG(kp5_ja_charon attempt4、39分)、**何度生成しても解消せず(ログ上未解決)6系列**(household topic_intro型の音声byte不変・検証ロジック変更ケースは別枠、下記4参照)。
4. Household `fact03_fix_02/topic_intro`(6回連続FAIL→事後cascade再照合でPASS、音声byte不変)は、**narration/attempts/*.json 形式のログが存在せず**(旧世代の`audit/tts_generation_results.json`独自形式、per-attemptタイムスタンプ自体が無い)、本scriptの自動集計対象から構造的に外れる既知の欠落。定性事例として本REPORTに別掲する。
5. 判定: **現時点でも「時間依存性あり」と結論する材料は増えていない(判断材料不足のまま)。仕様変更の提案はしない。** 再評価Trigger案を6節に提示(ユーザー判断待ち)。

## 1. 作成したscript

`er011_tts_retry_timing_monitor_01.py`(リポジトリroot直下)。

- 入力: `er0*_output/**/narration/attempts/*.json`(421件)を主データ源とし、同じ`level_dir`(`narration`フォルダの親)配下の`audit/review_lock_state.json`・`audit/human_approved_segments.json`・`audit/tts_generation_results.json`、および`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`(32件、`wav_path`で`source_out_path`と突合)を補助データ源として読み込む。
- グルーピング: `(level_dir, segment_id)`単位(`theme_id`/`level`/`segment_id`の値がrerunフォルダ間で重複しうるため、フォルダパス実体でグルーピングし誤結合を防止)。
- 出力フィールド(抜粋): theme_id/level/segment_id、attempt番号・max_attempts・`generation_path`(`attempt_number > max_attempts`のとき`manual_regenerate_beyond_loop_cap`、それ以外`automatic_retry_within_loop_cap`)、model/voice/route/language、saved_at、直前attemptからの経過秒(`gap_seconds_since_prev_attempt_in_group`)、間隔bucket、直前連続NG回数、audio_classification/verified/length_ok、asr_text(+sha256)、disfluency/repetition_qa関連フィールド、cascade関連フィールド、`verification_schema_variant`(cascade/repetition_qa/disfluencyフィールドの有無の組み合わせ=検証ロジックのスキーマ世代の代理指標)、NG理由分類(下記2節)、直前attemptとの再現有無、Human Review Lock状態スナップショット・human_approved_segments該当有無・human_review_queue一致、`canonical_text_final_state`(取れる範囲、既知の限界を明記)、`missing_fields`。
- 冪等性: 再実行のたびに`observations.jsonl`/`summary.json`/`summary.md`を全件再生成して上書き(追記ではない)。本セッションで2回実行しMD5完全一致を確認済み(`bb731742ae8cd1cabcd78e4e92450f43`)。
- API呼び出し・TTS生成・LLM推論は一切行わない。ローカルJSON/JSONLの読み込みと決定論的な文字列比較・日時差分計算のみ。

## 2. NG理由分類(種別A/B)の実装と限界

- 種別A(API/infra error: 429/5xx/timeout等)を判定する専用フィールドは`narration/attempts/*.json`スキーマに存在しない。scriptはレコード全体の文字列表現に対する保守的キーワード検索(`429`/`timeout`/`5xx`/`rate limit`等)のみで代用しており、**「0件」は「infra errorが無かった」ではなく「このログ形式からは検出できなかった」という意味**であることをsummary.json/summary.mdに明記した(誤読防止)。実際にキーワード一致した3件(種別A扱い)は文脈上いずれも偽陽性の可能性があり、専用フィールドがない限りこの分類は参考値にとどまる。
- 種別B(品質NG)は`audio_classification`(`TRUE_CONTENT_MISMATCH`/`ASR_VALIDATION_UNCERTAIN`/`TTS_FAILURE`)、`repetition_qa_evidence.flagged`、`length_ok=false`から決定論的にサブタイプを付与。

## 3. 集計表(種別Bのみ、主表)

出典: `er011_output/tts_retry_timing_monitor_01/summary.md`(自動生成)。間隔bucket定義: 1=即時<5分(<300秒)、2=5〜30分(300〜1800秒)、3=30分〜6時間(1800〜21600秒)、4=6時間〜翌日以降(21600秒以上)。

| 直前連続NG回数 | 間隔bucket | N | PASS数 | PASS率 |
|---|---|---|---|---|
| 1 | 即時<5分 | 34 | 23 | 67.7% |
| 1 | 30分〜6時間 | 1 | 1 | 100.0%(N=1) |
| 2 | 即時<5分 | 9 | 2 | 22.2% |
| 3以上 | 即時<5分 | 3 | 1 | 33.3% |
| 3以上 | 5〜30分 | 1 | 1 | 100.0%(N=1、household `point_one`、9.45分) |
| 3以上 | 30分〜6時間 | 1 | 0 | 0.0%(N=1、kp5_ja_charon、39分、**失敗**) |
| 3以上 | 6時間〜翌日以降 | 1 | 1 | 100.0%(N=1、CAR-T `full_story_part1`、14時間21分) |

種別A(infra疑い、参考値・上記の限界注記あり): 連続NG1回・即時=N2/PASS2、連続NG3以上・即時=N1/PASS0。

**読み方の注意**: 「3以上」バケットはNG回数3・4・5・6回超を一括りにしている(先行調査のattempt番号別集計と粒度が異なるため数値は先行調査の生表とは一対一対応しない。個別ケースの整合は本REPORT該当箇所・observations.jsonlで確認可能、CAR-T事例・kp5_ja_charon事例とも先行調査記載の間隔・結果と一致を確認済み)。いずれのセルもN=1〜9で、統計的な傾向判定はできない。

## 4. 類似事例一覧(パターン分類、決定論的ルールによる自動分類)

segment系列320件を検証結果の並び(True/False列)から6パターンに分類(件数はsummary.json参照)。

| パターン | 件数 | 代表例 |
|---|---|---|
| single_attempt_only(1回でPASS、リトライなし) | 243 | (大多数) |
| all_pass_no_retry_needed(複数回生成だが全てPASS) | 41 | `kp5_en`(family_a、b1b) |
| ng_x1_then_pass_simple_retry(即時NG1回→即PASS) | 25 | `comment_1`(family_a、b1b) |
| ng_x2_then_eventually_pass(NG2回→後でPASS) | 2 | `kp4_ja_charon`(family_a、b1b、3回で決着) |
| **ng_x3plus_then_eventually_pass(NG3回以上→後でPASS)** | 3 | 下記(a)〜(c) |
| **never_resolved_all_ng_in_log(ログ上、最後まで未解決)** | 6 | 下記(d) |

(a) `er003_output/n3_01/household/fact03_fix_02/b1b/point_one`: attempt1〜3(17:40:37〜17:41:13、間隔17〜19秒の即時連続NG、全てTRUE_CONTENT_MISMATCH)→attempt4(17:50:40、**9.45分後**)でNORMALIZED_MATCH・PASS。先行調査では「この3回で尽きた後の解決経路は未追跡」とされていたが、本集計で**attempt4の存在と間隔(567秒)が新たに判明した**(narration/attempts配下に4件目が存在)。
(b) `er011_output/family_a_completion_a2_trend_end_to_end_01/b1b/kp5_ja_charon`: 7回中6回NG、39分の間隔を置いたattempt4も失敗、最終的に通算7回目でPASS(先行調査事例3と一致、間隔・結果とも再現確認)。
(c) CAR-T `full_story_part1`(先行調査の起点事例、本REPORT冒頭参照、間隔14時間21分・PASS、`generation_path=manual_regenerate_beyond_loop_cap`と自動判定=Human Review Lock解除後の手動再生成であることが`attempt_number(4) > max_attempts(3)`から機械的に確認できた)。

(d) 「ログ上、最後まで未解決」6件全リスト(いずれも本データセットの範囲内で最後の記録がNGのまま、後続の解決有無は本scriptの走査範囲外の可能性がある):
- `er011_output/discovery_generalization_towels_trial_11/a2/comment_2`(3回連続NG)
- `er011_output/open112_trend_theme2_b_final_audio_rerun_02/a2/point_two`(2回連続NG)
- `er011_output/open112_trend_theme2_b_final_audio_rerun_04/a2/point_two`(2回連続NG)
- `er011_output/tts_attempt_audio_retention_wiring_01/evidence01/a2/kp_new_normal`(4回連続TTS_FAILURE。英語キーフレーズ"new normal"のTTSが一貫して日本語「新常態」を発話する言語混同型の異常。`runtime_evidence_summary.json`にstatus="STOPPED"と記録済みの既知の未解決ケース)
- `er012_output/editorial_b_family_production_phase1_02/b1b/point_two`(3回連続NG。repetition_qa flagged型)
- `er012_output/editorial_b_voices_trial_08_audio/p3/b1b/point_two`(3回連続NG)

(e) **検証ロジック変更による事後PASS(household topic_intro型、最重要の反証候補、本scriptの自動対象外)**: `er003_output/n3_01/household/fact03_fix_02/b1b/audit/tts_generation_results.json` の `segments.topic_intro`(2026-08-17実行分、`narration/attempts/*.json`形式では保存されていない旧世代ログ、per-attemptタイムスタンプなし)。attempts_log 6回全てFAIL(一貫して"crisper"を"CRISPR"と誤認識)、`status="STOPPED"`のまま。同ファイル内`legacy_asr_reverify`フィールドに、**音声バイトを一切再生成せず**、現行ASR cascade(Primary OpenAI×2→entity_like該当でSecondary Azureへエスカレーション)による事後再照合でNORMALIZED_MATCH・PASSと記録(2026-09-09付、`human_approved_segments.json`のnoteに「事後再照合であり当時のFAIL記録を書き換えるものではない」と明記)。**「時間を置いたら直った」ように見える外形と、「検証ロジック自体が変わった」という実態が区別できることを裏付ける直接証拠であり、本scriptの表3の「時間経過→PASS率」解釈に混ぜてはならない事例として明示的に除外扱いとする**(この特定ケースはタイムスタンプ欠如のためobservations.jsonlには行として現れず、集計にも混入していない=除外は構造的に自動達成されている)。

## 5. 交絡・バイアスの注記

- **選択バイアス(selection bias)**: 長間隔まで残るケースは、そもそも自動リトライ枠(`max_attempts`、多くは3回)を使い切った後にHuman Review Lock経由で手動再生成された「難しいセグメント」に限られる(`generation_path=manual_regenerate_beyond_loop_cap`は421件中12件のみ)。時間を置いたから直ったのではなく、「時間を置いてでも解決させる価値がある/人手が介入した」セグメントだけが長間隔サンプルに残る構造的偏りがある。
- **入力難易度・言語・voice・segment長の交絡**: 短間隔サンプル(N=34〜9)と長間隔サンプル(N=1)は、segment種別(英語本文/日本語キーフレーズ/見出し等)・voice・語長が揃っておらず、単純比較はできない。
- **validator/runtime差**: `verification_schema_variant`(cascade/repetition_qa/disfluencyフィールドの有無)は時期によって異なり、古い記録ほどrepetition_qa等の追加検証が無効だった可能性がある(4節(e)が典型例)。
- **ASR-only false positive**: household `comment_3`の"prevent"→"perfect"誤認識(先行調査事例5、独立local ASRのみのdisfluency QA不一致で主判定はPASS)のような、主判定に影響しないASR側ゆらぎは本表には現れない(そもそも`verified=true`のため)。今回のobservations.jsonlには当該segmentの2attemptとも`verified=true`で記録されている。

## 6. 継続モニタリング手順・再評価Trigger案(提案のみ、決定はユーザー)

- 運用: 各closeout consolidation時にFableがSonnet(script実行にはBashが必要なためhaiku-worker単体では不可)へ「`python3 er011_tts_retry_timing_monitor_01.py`を実行しsummary.md差分を報告」を委任する。scriptは冪等なので、実行しても既存ログを破壊しない。
- **再評価Trigger案(例、決定はユーザー)**: 種別B・間隔30分以上のretry事例が累計20件以上、かつ直前連続NG2回以上のサンプルが累計10件以上に達した時点で、時間依存性の再評価を検討する。現状(2026-09-10時点)は30分以上のセルが合計3件(N=1が3セル)、連続NG2回以上のサンプルは合計14件(9+3+1+1+1)であり、いずれもTrigger未達。
- **ログ設計改善案(実装はしない、提案のみ)**:
  1. 各attemptで実際にTTS APIへ渡した最終text文字列をper-attempt JSONに保存する(先行調査6節と同じ指摘、`canonical_text_final_state`は現状「そのsegmentの最終状態」であり各attempt個別の入力ではない)。
  2. household topic_intro型の旧世代ログ(`audit/tts_generation_results.json`のattempts_log、タイムスタンプなし)にも`saved_at`を付与し、本scriptの自動対象に含められるようにする。
  3. 種別A(infra/API error)を判定できる専用フィールド(HTTPステータス・エラー種別)をattempt記録に追加する。

## 7. QCD

- Quality: 決定論的集計(LLM不使用)、冪等性を2回実行のMD5一致で確認、先行調査記載の主要事例(CAR-T・kp5_ja_charon・household point_one)の間隔・結果を本集計値と突合し一致を確認。
- Cost: ¥0(API呼び出し・TTS生成なし)。
- Duration: 本セッション内で完了(script作成・初回実行・検証・本REPORT作成)。

## 出典ファイル

- `er011_tts_retry_timing_monitor_01.py`(新規script、リポジトリroot)
- `er011_output/tts_retry_timing_monitor_01/observations.jsonl`(421行)
- `er011_output/tts_retry_timing_monitor_01/summary.json`
- `er011_output/tts_retry_timing_monitor_01/summary.md`
- `TTS-REGENERATION-TIMING-DEPENDENCY-ANALYSIS-01_REPORT.md`(先行調査、土台)
- `er003_output/n3_01/household/fact03_fix_02/b1b/audit/tts_generation_results.json`(topic_intro legacy_asr_reverify)
- `er003_output/n3_01/household/fact03_fix_02/b1b/audit/human_approved_segments.json`
- `er011_output/tts_attempt_audio_retention_wiring_01/runtime_evidence_summary.json`(kp_new_normal未解決ケース)
