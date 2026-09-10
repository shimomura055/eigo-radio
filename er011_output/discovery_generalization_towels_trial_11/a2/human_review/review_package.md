# A2 Human Review パッケージ — FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-AUDIO-02-RESUME

対象記事: タオル臭テーマ(A2、Discovery Focus Module Part A単独、保険文制約なし)
生成日: 2026-09-11

使った仕組み: 既存Production機構(`er011_human_review_lock_01.py`、
ER-011-HUMAN-REVIEW-COST-GUARD-01)。`approve_regenerate()`で1segmentにつき
1回だけREGENERATE_APPROVEDへ遷移させ、既存の「標準2回+fallback1回(合計上限
3回)」という自然な追加1roundを取得した。新しいGate・閾値・retry仕様は
一切追加していない。

---

## 1. comment_2 — 引き続きHuman Review待ち(STOPPED)

**canonical text(記事本文どおり、A2 Comment 2)**:
> 洗濯して乾かしても、においが残ることがあります。では、タオルの中には、時間がたつと何が残るのでしょうか。

**現在の状態**: `review_lock_state.json` = `HUMAN_REVIEW_REQUIRED`(6/6take失敗)

### 観測された共通パターン(Sonnetの所見、修正はユーザー判断後)
6take全てで「時間がたつ」(ひらがな)が「時間が**経つ**」(漢字)とASR書き起こしされ、
6take中4takeで「におい」(ひらがな)が「**ニオイ**」(カタカナ)または「**臭い**」
(漢字)と書き起こされている。これらは同一発音・同一意味の表記ゆれであり、
機械分類(TRUE_CONTENT_MISMATCH)は表記差を検出しているだけで、実際の発話
内容そのものは正しい可能性がある。**実際に誤りがあるかどうかは試聴による
Human Review判断が必要。**

### 試聴用ファイル(全6take、絶対パス)

| take | round | 経路 | ASR書き起こし | ファイルパス |
|---|---|---|---|---|
| 1 | original | standard#1 | 洗濯して乾かしても、ニオイが残ることがあります。では、タオルの中には、時間が経つと何が残るのでしょうか? | `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\a2\narration\attempts\comment_2_attempt1_standard.wav` |
| 2 | original | standard#2 | 洗濯して乾かしても、においが残ることがあります。では、タオルの中には、時間が経つと何が残るのでしょうか? | `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\a2\narration\attempts\comment_2_attempt2_standard.wav` |
| 3 | original | fallback#1 | 洗濯して乾かしても、においが残ることがあります。では、タオルの中には、時間が経つと何が残るのでしょうか。 | `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\a2\narration\attempts\comment_2_attempt3_minimalfallback.wav` |
| 4 | resume | standard#1 | 洗濯して乾かしても、ニオイが残ることがあります。では、タオルの中には時間が経つと何が残るのでしょうか。 | `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\a2\narration\attempts\comment_2_attempt4_standard.wav` |
| 5 | resume | standard#2 | 洗濯して乾かしても、ニオイが残ることがあります。では、タオルの中には、時間が経つと何が残るのでしょうか。 | `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\a2\narration\attempts\comment_2_attempt5_standard.wav` |
| 6 | resume | fallback#1 | 洗濯して乾かしても、臭いが残ることがあります。では、タオルの中には、時間が経つと何が残るのでしょうか。 | `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\a2\narration\attempts\comment_2_attempt6_minimalfallback.wav` |

### ユーザー判断の選択肢(既存機構の範囲内)
- (a) いずれかのtakeを試聴し「内容として正しい」と判断すれば、既存の
  `record_human_approval()`で承認記録し、そのtakeをcomment_2.wavとして採用する。
- (b) 試聴して実際に内容誤りがあると判断すれば、STOPPEDのまま維持し、記事
  本文(comment_2のtext)側の言い回し変更を検討する(本タスクでは本文未変更)。
- (c) さらなる`approve_regenerate()`による追加retry(既存機構)。

---

## 2. meaning_4(Key Phrase 4 日本語gloss) — 解決済み、Human Review不要

**canonical text**: 活動し続ける(英語Key Phrase「stay active」の日本語gloss)

**現在の状態**: `review_lock_state.json` = `RESOLVED`(resume roundの最初のtakeで
`EXACT_MATCH`)。`narration/meaning_4.wav`は既にこのtakeの音声に更新済み。

| take | round | 経路 | ASR書き起こし | 結果 |
|---|---|---|---|---|
| 1 | original | standard#1 | 活動をし続ける。 | TRUE_CONTENT_MISMATCH |
| 2 | original | standard#2 | 活動を広げる | TRUE_CONTENT_MISMATCH |
| 3 | original | fallback#1 | 活動を続ける | TRUE_CONTENT_MISMATCH |
| 4 | resume | standard#1 | 活動し続ける | **EXACT_MATCH(採用)** |

採用take(参考試聴用): `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\a2\narration\attempts\meaning_4_attempt4_standard.wav`

---

## 既知の残作業(承認後)

`a2/audit/tts_generation_results.json`は、この2segmentとも**元run(2026-09-10)
のSTOPPED記録のまま**残っている(本resumeで得た新規take結果は
`a2/audit/human_review_resume_02_results.json`にのみ記録し、既存の監査
ファイルは書き換えていない)。このため、meaning_4は実際にはRESOLVED/OKだが
Gateはまだ古いSTOPPED記録を見てしまう状態。comment_2のHuman Review結果
確定後、以下のいずれかをユーザー承認のうえ実施する必要がある:
1. `tts_generation_results.json`の該当2エントリ(`segments.comment_2`、
   `key_phrases["4"].japanese_meaning`)を最新結果へ同期する、または
2. `run_level("a2")`相当の完全再実行(support/keyphraseも含む、追加コスト
   発生)を行う。

同期後に `stage_assemble_a2` (Audio Validation Gate込み) を実行すれば、A2の
Assembly/player.htmlが完成する。
