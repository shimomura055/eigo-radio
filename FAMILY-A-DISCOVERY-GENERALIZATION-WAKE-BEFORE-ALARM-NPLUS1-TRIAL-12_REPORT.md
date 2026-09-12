# FAMILY-A-DISCOVERY-GENERALIZATION-WAKE-BEFORE-ALARM-NPLUS1-TRIAL-12_REPORT

## 0. 要点(5行)

1. Discovery Focus Module Part A単独条件は、新テーマ「なぜ目覚ましが鳴る直前に目が覚めることがあるのか?」でも記事レベル(Ledger→Writer→Fact Checker→Ledger Deviation→Point Overlap/Value QA→Support/Key Phrase)は**A2/B1B両方でPASS、Local Rewriteゼロ**という、Trial-11(タオル臭)より一段クリーンな結果になった。
2. Point One/Point Twoは両レベルとも意味的に異なる発見(A2: 予期的な生理反応の段階性 vs 睡眠段階とgrogginess、B1B: 概日リズムの精度限界 vs 自己覚醒の練習効果)であり、機械的なcross_point_overlap比率も低い(A2: 0.15/0.23、B1B: 0.04/0.02)。
3. 音声工程で**A2のsegment `full_story_part1`が既存Human Review Lock(3回連続NG→STOPPED)に到達**し、cool-down 20分観測フックの無人4回目試行もNGだった(自動採用なし、Production側無変更)。B1Bは全segment検証PASS・Assembly PASS・Gate PASS。
4. 費用は記事+Support+Audio合算で**¥141.55**(上限¥300以内)。
5. Closeout: **記事レベルはVALIDATED、音声レベル(A2のみ)はUSER_DECISION_REQUIRED**(下記10節)。Production採用はユーザー判断なしに行っていない。

## 1. 再開時点の状態(タスク開始時に確認)

前回セッションはAPI上限で中断していたが、確認の結果**Ledger stage(researcher+verification)は既に完了済み**だった。
- `er011_output/discovery_generalization_wake_before_alarm_trial_12/research/verified_fact_ledger.txt` に CONFIRMED(VERIFIED) 13件のFactが存在(F001〜F017、うちF009/F010/F015はAMBIGUOUS/REJECTEDで除外済み)。
- `cost_summary.json` は既に ¥44.68(openai、researcher+verification 2件)を記録済み。
- `raw_usage_log.jsonl` に researcher/verification 各1件のみ記録(重複実行なし)。
- 本タスクでは **Ledgerを再生成せず、既存Ledgerをそのまま再利用**して`set_wake_topic()`でWriter用topic_jaを確定し、gate4以降を実行した(既存¥44.68は累計に算入済み)。

## 2. Reconciliation(PM_GOVERNANCE 2-1/2-3)

- `er011_discovery_generalization_wake_before_alarm_trial_12_run.py`(前回セッションで作成済み)のヘッダコメントで、Trial-11 harness(`er011_discovery_generalization_towels_trial_11_run.py`)との再利用関係・無変更のimportリストが既に記録されていることを確認した。重複・競合は無い。
- 音声側harness `er011_discovery_generalization_wake_before_alarm_trial_12_audio_run.py` は本タスクで新規作成(Trial-11の`er011_discovery_generalization_towels_trial_11_audio_run.py`をコピーし、テーマ固有定数[THEME_ID/日本語タイトル/article_id/管理ID文字列]のみ書き換え、Production関数のimport・呼び出しロジックは無変更)。コピー時の機械的な取りこぼし(article_id文字列がTOWELS_TRIAL_11のまま残っていた)を1件発見し修正済み(Production関数自体ではなくTrial harness内のラベル文字列のみ)。
- 標準player生成 `er011_wake_before_alarm_trial12_std_player_01.py` も本タスクで新規作成。Trial-11の`er011_towels_trial11_std_player_01.py`と同一の生成部品(`audio_review_player.py`、`build_b1b_rows()`)を再利用。A2はHuman Review Lock中のため、Trial-11の`build_a2_rows()`をそのまま流用せず、**未承認テイクを公開しない**部分player用の専用セクション生成関数を新規実装した(詳細9節)。
- 費用上限(記事側¥170、管理ID全体¥300)はrun.py側の`combined_cost_check()`をそのまま踏襲。音声側harnessにも同ロジックを追加した(Trial-11のaudio_run.pyには無かった管理ID全体チェックを本Trialで追加、既存¥120単独上限はそのまま維持)。

## 3. 観察項目ごとの結果(Trial-11比較表)

| 観察項目 | Trial-12(wake-before-alarm) | Trial-11(towels、既出再掲) |
|---|---|---|
| Full Story/Point構成の自然な成立 | A2/B1Bとも成立(「なぜ目覚ましが鳴るのか」の謎提示→機序説明→2つの異なる発見→限界の言及、という一貫した流れ) | 同様に成立(既出) |
| PointがFull Storyの言い換えでないか | Point Overlap QA: A2/B1BともPASS(overlapなし、記事全体retry **0回**で解消) | 同じくPASS、retry 0回(既出) |
| Pointごとに異なる発見か | A2: 予期的な生理反応(ACTH上昇・前頭前野活動・心拍)の段階性 vs 睡眠段階とgrogginessの関係、で異なる。cross_point_overlap比率0.149/0.226(低)。B1B: 概日リズムの精度限界 vs 自己覚醒の練習効果、で異なる。比率0.037/0.024(低) | 同様に低比率で異なる発見(既出) |
| 保険文・過剰注意文 | 本文0件・Support(Preview/Comment)0件、両レベルとも | 0件(既出) |
| Ledger Deviation | 0件(LEDGER_COMPLIANT)、両レベルとも | 0件(既出) |
| Local Rewrite | **発生なし**(local_rewrite_cycles=[]、両レベル) | B1Bで1サイクル発生(Fact Checkerが3件の未確認claimを指摘→Local Rewriteで解消、既出) |
| Fact Checker verdict | A2: PASS(到達1/1)、B1B: PASS(到達1/1) | A2: PASS、B1B: REVIEW_REQUIRED→Local Rewrite後PASS(既出) |
| Point Overlap/Point Value QA | 両方PASS、両レベル | 同様(既出) |
| Support/Key Phrase | 両レベルともselection/canonicalization/redundancy全PASS | 同様(既出) |
| A2/B1B両方での成立性 | 両方成立(記事レベル) | 同様(既出) |
| 音声工程(既存標準player形式維持) | B1B完成・A2は1segmentがHuman Review Lock中につき部分player(4節) | 両方完成(既出) |

**新規結果としての要点**: Trial-12はTrial-11よりも記事生成段階で「クリーン」な結果(Local Rewrite不要、Fact Checker一発PASS)だった。ただしこれはN=1×2レベルの観測であり、Discovery/Why型Focus Module Part Aが常にLocal Rewrite不要になると一般化できるものではない(サンプル数の限界、既存OPEN-135行の量産平均未確定という留保と同じ性質)。

## 4. 音声工程 runtime evidence

### 4.1 A2: Human Review Lock発生(既存安全装置、自動retry・承認代行なし)

- segment `full_story_part1`(英語Full Story前半)が標準2回attemptともRepetition QA(既存`method_a_ngram`検出器)で `"24 -hour day."` という3語フレーズの重複を検出しNG判定(`verified=false`)。ASR文字起こし自体は正字一致(`audio_classification=NORMALIZED_MATCH`、`length_ok=true`)であり、内容・長さ自体には問題がない。
- **観察(新規発見、報告のみ・コード変更なし)**: 該当箇所は記事本文自体が「Light helps this clock match the 24-hour day.」「…usually matched a 24-hour day.」と、意図的に同じ語句を2文にまたいで正当に2回使っている(Point Overlap QA側の`near_duplicate_sentence_pairs`でもratio 0.554で検出済みだが、記事QA自体はこれを許容範囲としてPASSしている)。TTS側のRepetition QA(`canonical_repeat_count: 0`)は、この正当な語句再利用を「ループ再生」と誤検出した可能性がある(false-positiveの疑い)。既存Repetition QAロジック自体は本Trialで一切変更していない。
- 3回目(cool-down観測フックによる無人4回目試行、`fallback`経路)も同じくNG。`review_lock_state.json`は`HUMAN_REVIEW_REQUIRED`(`final_status=STOPPED`)のまま。
- Assembly(Gate OFF経路)は`BLOCKED`、Gate opt-in ON経路は`SKIPPED_ASSEMBLE_NOT_PASS`。
- **人的介入・承認代行は一切行っていない**(review_lock.approve_regenerateは呼んでいない、STOPPEDのまま)。

### 4.2 B1B: 全segment PASS

- 全22segment(preview/comment×4/point見出し×2/full story×2/point本体×2/in one line/topic intro/key phrase×5)がTTS+ASR検証を1回でPASS。Human Review Lock発火なし。
- Assembly: `duration=316.544s / peak=0.8467 / clipping=False`、Gate OFF経路PASS、Gate opt-in ON経路PASS。

### 4.3 OPEN-121(数字↔数詞同値化、connected_speech_equivalence_layer)

- A2英語本文4segment(`full_story_part1/2`, `point_one`, `point_two`)すべてで対象フラグは有効だったが、`connected_speech_info`は全attempt・全segmentで`null`(**非発火**)。数字↔数詞表記のASR不一致は本Trialでは発生しなかった。

### 4.4 OPEN-145(日本語ASR表記ゆれ層)

- A2/B1B両レベルの全日本語segment(Comment×4・Preview・Japanese title・Key Phrase日本語gloss5件)で`reading_resolver_info`は全件`null`または未設定(**非発火**)。表記ゆれ判定が必要になるケースはなかった。

### 4.5 OPEN-146(Ledger公式英語表記機構)

- 本テーマの検証済みFactはすべて英語一次情報源(PubMed等)であり、日本人名の英語表記対象が記事本文・Ledgerに存在しない。該当artifact(canonical_en_spelling系)は生成されておらず、**想定どおり非発火**。

### 4.6 Directional Fact Precheck(参考、既存の非ブロッキング層)

- A2/B1Bとも`overall_status=DIRECTION_REVIEW_REQUIRED`(Trial-11と同一の値)。`conflicts`は全項目で空配列であり、「片方にのみ方向表現がありconflictではなく機械的に比較不能」という理由のみ。新規の矛盾は検出されていない。

## 5. Cool-down観測(TTS-RETRY-COOLDOWN-20MIN-OBSERVATION-TRIAL-01)

- **N=1**(対象segment: A2 `full_story_part1`のみ、B1Bは対象ゼロ)。
- `requested_cooldown_seconds=1200.0` / `actual_wait_seconds=1200.006`。待機前後で`params_hash`一致(`params_unchanged_verified=true`)。
- 4回目試行: `fourth_attempt_executed=true` / `fourth_attempt_result_status=NG`(`raw_status_field=STOPPED`)。
- `no_human_intervention=true` / `production_state_modified=false` / `auto_adopted_to_production=false`(4回目がPASSしていたとしても自動採用しない設計どおり、実際もNGだったため採用対象なし)。

## 6. 1記事総コスト(A2+B1B合算、5区分)

Trial-11とは異なりTTSは`TTS_EXECUTION_MODE=STANDARD`(同期)で実行しており、OPEN-144のようなBatch計上バグは対象外(azureが1件unpriced=¥0計上、既存`pricing_snapshot.json`に単価未定義のため開示のみ、独自単価は追加していない)。

| 区分 | 金額(¥) | 説明 |
|---|---|---|
| ①今回実測合計(実際の実行経路=Standard同期) | **141.55** | Ledger+記事生成 78.98(researcher+verification 44.68を含む) + Support/Audio 62.57(a2: 34.07, b1b: 25.93, other: 2.57) |
| ②今回実測(公式script報告値) | 141.55 | ①と同値(訂正不要。unpriced_records=1件[azure]のみ開示、¥0計上) |
| ③量産想定(Batch適用時の1記事見込み、机上換算・未実行) | 約114.65 | audio側gemini分(¥53.80)をBatch tier(Standardの50%)換算した理論値。実行はしていない |
| ④retry/Human Review由来の上振れ分(内数) | 5.07 | A2 `full_story_part1`の2回目attempt(¥2.60)+cool-down 4回目attempt(¥2.47、azure診断分¥0含む)。1回目attempt(¥2.57)は通常運用でも必要な費用のため上振れに含めない |
| ⑤参考: 通常運用相当分(①-④) | 136.48 | Human Review発生に伴う異常対応コストを除いた実質必要額 |

管理ID全体上限¥300に対し、実測¥141.55(47.2%)。超過なし。

## 7. Closeout

- **記事レベル(A2/B1B、Discovery Focus Module Part A単独)**: **VALIDATED**。Trial-11(タオル臭)に続き、テーマを「身体・睡眠」領域に変えても、Full Story/Point構成の自然な成立・Point間の意味的差異・保険文ゼロ・Ledger準拠・Fact Checker PASSが再現された(むしろLocal Rewrite不要という点でTrial-11より結果が良好)。ただしN=2テーマの観測であり、量産平均としての一般化主張はしない。
- **音声レベル**: B1Bは**VALIDATED**(全工程PASS)。A2は`full_story_part1`のHuman Review Lock(既存安全装置)により未完成であり、**USER_DECISION_REQUIRED**とする。
  - 決定が必要な点: (a) A2 `full_story_part1`のcool-down 4回目試行結果(NG)を踏まえ、このまま追加対応せず本Trialの音声成果物をB1Bのみの完成+A2部分player(9節)で確定として良いか、(b) 既存Human Review機構(`review_lock.approve_regenerate`)を使った人的承認・再生成を別タスクとして依頼するか、(c) Repetition QAが正当な語句再利用("24-hour day"の2回使用)を誤検出した可能性がある点について、新規OPEN item化を希望するか(コード変更は本Trialでは行っていない)。
- **Production採用**: 本Trialでは一切判断していない(Discovery Focus Module Part AのProduction採用可否はユーザー試聴待ち、既存方針どおり)。

## 8. 段階別artifact(確定結果)

| 段階 | 状態 | 主なartifact |
|---|---|---|
| Ledger(Researcher+Verification) | 完了(前回セッションから再利用) | `er011_output/discovery_generalization_wake_before_alarm_trial_12/research/` |
| Gate4静的確認 | PASS | `.../audit/gate4_check.json` |
| 記事A2 | OK(fact_verdict PASS, ledger LEDGER_COMPLIANT) | `.../a2/article.md`, `.../a2/run_summary.json` |
| 記事B1B | OK(fact_verdict PASS, ledger LEDGER_COMPLIANT) | `.../b1b/article.md`, `.../b1b/run_summary.json` |
| Support/Key Phrase A2 | 全PASS | `.../a2/a2_support_texts.json`, `.../a2/key_phrases/` |
| Support/Key Phrase B1B | 全PASS | `.../b1b/b1_support_texts.json`, `.../b1b/key_phrases/` |
| 音声A2 | 部分完成(1segment Human Review Lock、Assembly BLOCKED) | `.../a2/audit/review_lock_state.json`, `.../a2/audit/tts_cooldown_observation_stage_summary.json` |
| 音声B1B | 完成(Assembly PASS、Gate PASS) | `.../b1b/run_summary_assemble.json` |
| 標準player | 生成済み(B1B完成+A2部分、未承認テイク非公開) | `er011_output/discovery_generalization_wake_before_alarm_trial_12/player_std/index.html` |

## 9. 標準player(player_std)についての補足

`er011_wake_before_alarm_trial12_std_player_01.py`(本タスクで新規作成、Production関数は呼ばずTTS/ASR再生成なし・¥0)で生成。B1Bは完成episode音声込みでTrial-11と同一形式。A2はHuman Review Lock中の`full_story_part1`および未完成のepisode音声を**一切含めていない**(未承認テイクの公開を避けるため)。他の検証PASS済みsegment(13件)とKey Phrase(5件)は個別mp3で参照可能。push(Git記録)はFable統合時に別途実施予定。

## 10. 新規結果・過去再掲の区別

- **新規結果**: 3節の記事レベル観測全項目(Trial-12固有の値)、4.1節のA2 Human Review Lock発生と原因分析(Repetition QA false-positive疑い)、5節のcool-down観測(N=1)、6節のコスト実測、9節の部分player設計。
- **過去再掲(Trial-11既出、比較のための参照のみ)**: 3節のTrial-11列の値、4.6節のDirection Precheckの非ブロッキング挙動一般。
