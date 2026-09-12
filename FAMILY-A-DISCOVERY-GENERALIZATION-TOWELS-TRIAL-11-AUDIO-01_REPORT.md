# FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-AUDIO-01_REPORT

管理ID(本作業): FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-AUDIO-02-RESUME
対象: タオル臭テーマ(A2/B1B、Discovery Focus Module Part A単独、保険文制約なし)
実行日: 2026-09-10(初回AUDIO-01実行、GATE_BLOCKEDで停止)/2026-09-11(本resume作業)

## 1. Status表

| 段階 | A2 | B1B |
|---|---|---|
| 記事(article.md) | 完成・変更なし | 完成・変更なし |
| Support(Preview/Comment) | OK(insurance_hits=0) | OK(insurance_hits=0) |
| Key Phrase選定 | PASS | 初回KEY_WORDS_STRUCTURE_INVALID(1件、display_phrase語数超過)→既存前例と同一の最小retryで2回目PASS(新規retry仕様は追加せず、既存無変更関数の再呼び出しのみ) |
| TTS/ASR | 24segment中23 OK/RESOLVED、1件Human Review待ち(`comment_2`) | 22segment中20 OK、2件Human Review待ち(`full_story_part1`/`full_story_part2`) |
| Assembly/Gate | 未実行(Human Review承認待ちのため意図的に保留) | 未実行(同左) |
| player.html | 未生成(承認後に作成) | 未生成(同左) |

Human Review Lock機構(既存Production機構、ER-011-HUMAN-REVIEW-COST-GUARD-01)により、
`approve_regenerate()`で各segment1回だけ自然な追加take(標準+fallback、既存の
合計上限3回budget内)を取得した。新しいGate・閾値・retry仕様は一切追加していない。

## 2. Human Review待ちsegmentと試聴ファイル

### A2: `comment_2`(1件)
6/6take(元3take+追加3take)ともTRUE_CONTENT_MISMATCHで停止。**所見**:
ASRが「時間がたつ」を「時間が経つ」(6/6take)、「におい」を「ニオイ」/「臭い」
(4/6take)と書き起こしており、いずれも同一発音の表記ゆれの可能性が高い
(内容自体は正しい可能性)。

パッケージ: `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\a2\human_review\review_package.md`
(全6take絶対パス・ASR書き起こし付き)

なお同時に対応した`meaning_4`(Key Phrase 4日本語gloss)は追加takeの1回目で
`EXACT_MATCH`となり解決済み(Human Review不要、詳細は同パッケージ内に記録)。

### B1B: `full_story_part1`・`full_story_part2`(2件)
- `full_story_part1`: 元3takeは3/3で統計文(「A 2022 survey...」)が丸ごと欠落する
  genuine content drop。追加3takeでは統計文は含まれるようになったが、言い直し
  グリッチ(1件)・「has dried」→「had dried」という軽微な差異(2件)で不合格。
  **take5(2回目の追加take)が内容的に最も近い**。
- `full_story_part2`: canonical textに正規に2回登場する「after two months」を
  Repetition QAが誤検知している可能性が高い(6take中4takeは内容としては
  NORMALIZED_MATCH/HIGH_SIMILARITY_SAFE)。**take2・3・6がおすすめ**。

パッケージ: `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\b1b\human_review\review_package.md`
(全6take×2segment、絶対パス・ASR書き起こし付き)

## 3. 保険文(hedging表現)観測結果

既存の広域正規表現(`check/consult/ask/see/refer to/look at/read/follow` +
`instructions/manuals/guides/professionals/labels`等)をarticle本文・
Support文・Key Phrase文全体に適用。**A2・B1Bとも0件**(記事本文・Support・
Key Phraseのいずれにも該当表現なし)。

## 4. 費用

既存`cost_stage()`(openai・openai_asrのみ集計)による報告額: **¥12.76**
(内訳: 元run[2026-09-10、A2 scaffold/keyphrase/tts]=¥4.79、本resume作業
[2026-09-11、A2 resume¥0.26+B1B scaffold/keyphrase/tts¥6.37+B1B resume¥1.34]=¥7.97)。

**発見事項(Sonnetの所見)**: `er011_discovery_generalization_towels_trial_11_
audio_run.py`の`_call_cost_usd()`は`provider=="gemini"`のみを判定しており、
実際のログ記録`provider=="gemini_batch"`(TTS音声生成、69件)を一致させられず
0円計上している(既存script自体の集計バグ、本タスクで新規に発生させたもの
ではない)。`pricing_snapshot.json`のBatch tier単価で手動概算すると、
gemini_batch分だけで約**¥50.07**が未計上であり、実際の合計は概算**¥62.83**
程度と見られる。いずれにせよ事前承認済みの小額範囲(¥300未満)に収まって
いるためSTOPはしていないが、費用集計ロジック自体の恒久修正が必要かは
ユーザー判断を仰ぐ(本タスクでは修正せず報告のみ)。

## 5. 承認後に必要な残作業とコマンド

1. 上記2件のreview_package.md/jsonを試聴し、各segmentについて
   「採用take」か「STOPPEDのまま」かを判断する。
2. 採用する場合、既存の`record_human_approval()`(`er003_v1_n3_01_assemble.py`)
   でHUMAN_APPROVEDとして記録し、採用takeの音声を最終narration wavとして
   配置する(`comment_2.wav`は既に最新resume takeの内容、`full_story_part1/2.wav`
   も同様。特定のtakeを選ぶ場合は該当attempts配下のwavをコピーする)。
3. `a2/audit/tts_generation_results.json`・`b1b/audit/tts_generation_results.json`
   の該当segmentエントリを、承認結果に合わせて同期する(本タスクでは
   意図的に未実施、既存監査ファイルの書き換えはHuman Review確定後に行う)。
4. 同期後、`.venv/Scripts/python.exe er011_discovery_generalization_towels_trial_11_audio_run.py a2`
   および `... b1b`(またはassembly stageのみの再実行)でAssembly/Audio
   Validation Gateを通し、`... player` でplayer.htmlを生成する。

## 6. 使用した補助script(いずれもProduction関数を無変更で呼ぶだけ、新規Gate/閾値なし)

- `er011_discovery_generalization_towels_trial_11_audio_02_resume_human_review.py`
  (A2 comment_2/meaning_4の追加1round)
- `er011_discovery_generalization_towels_trial_11_audio_03_b1b_kp_retry_resume.py`
  (B1B Key Phrase選定retry+TTS/Assembly Gate確認、既存前例`er011_no18_b1_kp_retry_01.py`
  と同一の最小retryパターン)
- `er011_discovery_generalization_towels_trial_11_audio_04_b1b_fullstory_resume_human_review.py`
  (B1B full_story_part1/2の追加1round)

## 7. 詳細証跡パス

- A2試聴用パッケージ: `er011_output/discovery_generalization_towels_trial_11/a2/human_review/review_package.md`, `.json`
- B1B試聴用パッケージ: `er011_output/discovery_generalization_towels_trial_11/b1b/human_review/review_package.md`, `.json`
- A2 resume生結果: `er011_output/discovery_generalization_towels_trial_11/a2/audit/human_review_resume_02_results.json`
- B1B resume生結果: `er011_output/discovery_generalization_towels_trial_11/b1b/audit/human_review_resume_04_results.json`
- 費用ログ: `er011_output/discovery_generalization_towels_trial_11/audit/raw_usage_log_audio_01.jsonl`

---

## AUDIO-03: B1B個別承認+Assembly

管理ID: `FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-AUDIO-03-B1B-APPROVAL-AND-ASSEMBLY`
実行日: 2026-09-12。実行スクリプト:
`er011_discovery_generalization_towels_trial_11_audio_03_b1b_individual_approval_and_assemble_01.py`
(既存Production関数のみ無変更で呼ぶ、新規TTS/ASR呼び出しは無し、¥0)。

### 1. full_story_part1: take5の個別Human Approval

ユーザー決定(2026-09-12、原文): 「試聴しました。`has dried / had dried`は、
hasの子音部分が弱く、どちらとも聞こえる微妙な音です。今回はtake5でOKと
します。今回のtake5に対する個別Human Approvalとして処理してください。
一般仕様として「has/had差を許容する」という意味ではありません。」

- take5(`full_story_part1_attempt5_englishstyleprefixwidemargin.wav`)を
  `narration/full_story_part1.wav`へ採用(sha256=`12bd5b35...`、置き換え前は
  take6=`4d75b649...`)。
- 既存`record_human_approval()`(`er003_v1_n3_01_assemble.py`)で
  `audit/human_approved_segments.json`へ個別承認を記録(canonical_text_sha256
  照合、approved_by="user")。
- `review_lock_state.json`のfull_story_part1: `HUMAN_REVIEW_REQUIRED`→
  `RESOLVED`/`final_status=HUMAN_APPROVED`。reasonへユーザー原文を明記
  (「一般仕様として…という意味ではない」を含む)。
- `tts_generation_results.json`: status=`STOPPED`のまま維持(6/6take全てが
  自動ASR検証には合格しなかったという事実を正直に記録)。resume round
  (take4-6)の実attempt履歴3件を`attempts_log`へ追記(originalの3件は無変更、
  計6件)。個別承認の経緯を`TRIAL11_AUDIO03_B1B_HUMAN_APPROVAL_NOTE`へ記録。

### 2. full_story_part2: OPEN-121修正後の同期

`review_lock_state.json`は別タスク(`OPEN-121-REPETITION-QA-NUMBER-WORD-
EQUIVALENCE-PRODUCTION-FIX-01`、2026-09-12)で既に`RESOLVED`/`OK`(採用
attempt2)へ更新済み。本タスクでは`tts_generation_results.json`側を同じ
結論へ同期した(選択肢1: 該当エントリを最新結果へ同期): status=`STOPPED`→
`OK`、attempt2/3の`repetition_qa_evidence`を修正後の再判定結果(方式A:
`canonical_repeat_count=2`/`intentional=true`/`flagged=false`、方式D・D'は
元々flagged=falseのまま無変更)へ補正、`verified=true`へ更新。TTS再生成・
新規ASR呼び出しは無し(¥0)。

両エントリとも、変更前の`tts_generation_results.json`全体を
`tts_generation_results.pre_sync_backup.json`へバックアップ済み。

### 3. B1B Assembly + Audio Validation Gate

`er011_discovery_generalization_towels_trial_11_audio_run.py`の
`assembly_stage("b1b")`(`stage_assemble_b1`+Gate opt-in確認、無変更)を実行。

| 項目 | 結果 |
|---|---|
| Gate(常時ON、`load_b1_sources`内) | PASS |
| Gate opt-in(構造完全性チェック込み) | PASS |
| Assembly status | OK |
| duration_seconds | 345.284 |
| peak | 0.89427 |
| clipping_detected | False |
| headroom_safety_valve.applied | False |

新たなNGは発生しなかった(retryなし)。

### 4. 成果物

- 最終wav: `er011_output/discovery_generalization_towels_trial_11/b1b/assembled/English_Your_Way_B1B_DISCOVERY_GENERALIZATION_TOWELS_TRIAL_11.wav`
- 最終mp3(既存プロジェクト前例`er003_v1_b1_scaffold_audio_01_generate.py`と
  同じ`soundfile`書き出し方式で追加生成、Production assemble関数自体は
  無変更): `er011_output/discovery_generalization_towels_trial_11/b1b/assembled/English_Your_Way_B1B_DISCOVERY_GENERALIZATION_TOWELS_TRIAL_11.mp3`
- player.html(B1B単独版。既存`player_stage()`はA2+B1B結合ページのみ生成
  でありA2側`run_summary_assemble.json`が無いと動かないため、同じ既存部品
  [`build_b1b_rows()`/`audio_review_player`]だけを再利用してB1B単独ページを
  別途生成した。新しいレンダリング仕様は追加していない):
  `er011_output/discovery_generalization_towels_trial_11/b1b/assembled/player.html`
  (`file:///C:/Users/tensh/eigo-radio/er011_output/discovery_generalization_towels_trial_11/b1b/assembled/player.html`)

### 5. A2の残作業(未着手、本タスク対象外)

A2は`comment_2`がUDR#11(表記ゆれ対策採用)待ちのため、本タスクでは
Assemblyしていない。既知の同期対象: `meaning_4`(追加takeの1回目で
`EXACT_MATCH`、Human Review不要と既に判明済み、`tts_generation_results.json`
への反映は未実施)、`comment_2`はUDR#11採用後に対応。

### 6. 費用

本タスク(B1B個別承認+Assembly+player/mp3生成)による新規API呼び出しは
無し(TTS/ASR呼び出し0件、`audit/raw_usage_log_audio_01.jsonl`は179行の
まま不変)。**本作業費用: ¥0**。

Trial-11の1記事総コスト(既存`FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-
TRIAL-11-COST-01_REPORT.md`の5区分、本作業分¥0を加算):

| 区分 | 金額(¥) | 説明 |
|---|---|---|
| ①今回実測(訂正後、実際の実行経路=Batch API) | **180.55**(不変) | text-gen 117.72 + audio(訂正後)62.83 + 本作業¥0 |
| ②今回実測(未訂正、公式script報告値) | 130.48(不変) | OPEN-144未修正のまま参照すると過小 |
| ③量産想定(Batch適用時の1記事見込み) | 180.55(不変) | ①と同値 |
| ④retry/Human Review由来の上振れ分(内数) | 16.00(不変) | 本作業はAssembly/player生成のみでTTS/ASR呼び出しが無いため上振れなし |
| ⑤(参考、机上換算)Standard同期TTSで実行した場合 | 約230.6(不変) | 未実行の理論値 |

**発見事項(Sonnetの所見、報告のみ)**: 上記①〜⑤には、別タスク
(`FAMILY-A-DISCOVERY-TOWELS-B1B-SECONDARY-ASR-AND-RETRY-TIMING-RECONCILE-01`、
2026-09-12)でtake5音声へ実施したAzure Secondary ASR単独診断呼び出し
(実費用**約¥1.81**、`audit/secondary_asr_manual_diagnostic_take5_cost_log.jsonl`、
本タスクとは別の管理IDで既に支出済み)が含まれていない。本タスクの
スコープ外の別作業の費用のため本表には加算していないが、Trial-11全体の
真の累計を追う場合は¥180.55+¥1.81=**約¥182.36**が実態に近い(費用を
隠蔽しないための開示、コード修正は行っていない)。

### 7. 参照ファイル

- 実行スクリプト: `er011_discovery_generalization_towels_trial_11_audio_03_b1b_individual_approval_and_assemble_01.py`
- 実行サマリ: `er011_output/discovery_generalization_towels_trial_11/b1b/audit/audio_03_b1b_individual_approval_and_assemble_01/run_summary.json`
- 事前バックアップ: `er011_output/discovery_generalization_towels_trial_11/b1b/audit/tts_generation_results.pre_sync_backup.json`
- 人間承認記録: `er011_output/discovery_generalization_towels_trial_11/b1b/audit/human_approved_segments.json`
