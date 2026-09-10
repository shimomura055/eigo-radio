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
