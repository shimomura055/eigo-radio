# B1B Human Review パッケージ — FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-AUDIO-02-RESUME

対象記事: タオル臭テーマ(B1B、Discovery Focus Module Part A単独、保険文制約なし)
生成日: 2026-09-11

使った仕組み: A2と同じ既存Production機構(`er011_human_review_lock_01.py`、
ER-011-HUMAN-REVIEW-COST-GUARD-01)。`approve_regenerate()`で1segmentにつき
1回だけREGENERATE_APPROVEDへ遷移させ、既存の「標準3回(この経路は
standard/fallbackの区別を持たない単一cascade)」という自然な追加1roundを
取得した。新しいGate・閾値・retry仕様は一切追加していない。

なお、B1BのSupport(Preview/Comment)・Key Phrase選定は既にstatus=OK/PASSで
完了済み(insurance_hits=0)。Key Phrase選定は初回のみ`KEY_WORDS_STRUCTURE_
INVALID`(display_phraseが1〜5語規約に反する1件、単発のLLM出力ゆらぎ)と
なったが、既存前例(`er011_no18_b1_kp_retry_01.py`等)と同一の手当てとして、
無変更のProduction関数を再呼び出しするだけの最小retryを行い、2回目で
`CANONICALIZATION_PASS`/`REDUNDANCY_PASS`に到達した(新しい仕様判断は
一切行っていない)。

---

## 1. full_story_part1 — 引き続きHuman Review待ち(STOPPED)

**canonical text**:
> A towel can come out of the wash looking clean, then give off a wet-cloth or old-rag smell. That smell may be noticed before washing, while the fabric is still wet after washing, or after the laundry has dried, and these stages can overlap.
>
> A 2022 survey asked 359 households about laundry odors. About 110 reported a smell before washing, while fewer noticed one in wet laundry after washing or after the laundry had dried. These groups could overlap, so the numbers are not a rate for all households. But they show that the wash cycle does not always mark the end of the story.

**現在の状態**: `review_lock_state.json` = `HUMAN_REVIEW_REQUIRED`(6/6take失敗)

### 観測された問題(Sonnetの所見、修正はユーザー判断後)
- **originalラウンド(take 1-3)**: 3/3takeとも「A 2022 survey asked 359
  households about laundry odors. About 110 reported a smell before washing,
  while fewer noticed one in wet laundry after washing or after the laundry
  had dried.」の**文が丸ごと欠落**していた(統計データの文が読まれず、
  段落1の終わりから段落4のフレーズへ直接つながっていた)。これは表記
  ゆれではなく、実際の読み上げ内容が欠落する**genuine content drop**で
  あり、要注意。
- **resumeラウンド(take 4-6)**: 2022 survey文は3/3とも読まれるように
  なったが、別の理由で不合格: take4は「while the fabric is still wet,
  after washing」というフレーズが2回連続する言い直しグリッチ。take5/6は
  canonical「has dried」(現在完了)がASRでは「had dried」(過去完了)と
  書き起こされている(発音が近い"has"/"had"の混同である可能性があり、
  実際に間違って発話されたか、ASR側の書き起こしゆれかは試聴でしか判断
  できない)。
- **人間試聴のおすすめ**: take5(resume attempt2)が内容的に最も
  canonicalへ近い(欠落なし、グリッチなし、差異は"has"→"had"のみ)。

### 試聴用ファイル(全6take、絶対パス)

| take | round | ASR書き起こし(要旨) | ファイルパス |
|---|---|---|---|
| 1 | original#1 | 2022 survey文が丸ごと欠落 | `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\b1b\narration\attempts\full_story_part1_attempt1_englishstyleprefixwidemargin.wav` |
| 2 | original#2 | 同上(欠落) | `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\b1b\narration\attempts\full_story_part1_attempt2_englishstyleprefixwidemargin.wav` |
| 3 | original#3 | 同上(欠落) | `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\b1b\narration\attempts\full_story_part1_attempt3_englishstyleprefixwidemargin.wav` |
| 4 | resume#1 | 2022 survey文は含まれるが「while the fabric is still wet, after washing」が2回言い直しグリッチ | `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\b1b\narration\attempts\full_story_part1_attempt4_englishstyleprefixwidemargin.wav` |
| 5 | resume#2 | **内容ほぼ完全一致**、差異は"has dried"→"had dried"のみ(おすすめ) | `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\b1b\narration\attempts\full_story_part1_attempt5_englishstyleprefixwidemargin.wav` |
| 6 | resume#3 | 内容はほぼ含まれるが"has dried"→"had dried"+文の切れ目が変化("these stages"→"these groups"相当の混線) | `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\b1b\narration\attempts\full_story_part1_attempt6_englishstyleprefixwidemargin.wav` |

---

## 2. full_story_part2 — 引き続きHuman Review待ち(STOPPED)

**canonical text**:
> Why can the smell return? In laboratory models using cotton and polyester, bacteria linked with skin oil and sweat could move into the fibers and build a sticky layer called a biofilm. That layer was difficult to remove with ordinary washing, and odor could remain after the wash.
>
> In another cotton-cloth model, a particular combination of three bacteria produced a stronger and longer-lasting wet-cloth smell than single bacteria or other combinations.
>
> A separate six-month study followed new cotton towels in 26 Japanese households. Smell and dullness were already observed after two months. During the study, biofilm structures were seen mainly around the towels' lengthwise threads. The layer's components and the number of bacteria that could be grown in the lab also increased over time.
>
> This was what researchers observed in those homes. It does not mean that every towel will smell after two months.

**現在の状態**: `review_lock_state.json` = `HUMAN_REVIEW_REQUIRED`(6/6take失敗)

### 観測された問題(Sonnetの所見、修正はユーザー判断後)
canonical textには「after two months」というフレーズが**本文として正規に
2回**登場する(1回目: 統計の記述「Smell and dullness were already observed
after two months.」、2回目: 注意書き「It does not mean that every towel will
smell after two months.」)。6take中4take(take2, 3, 5, 6)は内容として
`NORMALIZED_MATCH`/`HIGH_SIMILARITY_SAFE`(実質的に内容一致)だったが、
**Repetition QA(意図しない言い直し検出)が「after two months」の2回出現を
機械的なcanonical repeat countと照合できず、誤って言い直しとしてflagして
いる**ように見える(`canonical_repeat_count: 0`という記録があり、QA側が
本文に正規の2回出現があることを認識していない可能性がある)。これは
Sonnetの所見であり、Repetition QA自体の修正はユーザー判断後(Production
コードの変更はこのタスクの範囲外)。take1・take4のみ、"the smell"→"this
smell"、"was"→"is"という軽微な語形差があった。

### 試聴用ファイル(全6take、絶対パス)

| take | round | 分類 | ファイルパス |
|---|---|---|---|
| 1 | original#1 | TRUE_CONTENT_MISMATCH("the smell"→"this smell") | `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\b1b\narration\attempts\full_story_part2_attempt1_englishstyleprefixwidemargin.wav` |
| 2 | original#2 | NORMALIZED_MATCH、Repetition QA flagで不合格(おすすめ) | `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\b1b\narration\attempts\full_story_part2_attempt2_englishstyleprefixwidemargin.wav` |
| 3 | original#3 | NORMALIZED_MATCH、Repetition QA flagで不合格(おすすめ) | `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\b1b\narration\attempts\full_story_part2_attempt3_englishstyleprefixwidemargin.wav` |
| 4 | resume#1 | TRUE_CONTENT_MISMATCH("This is"→"This was"相当の軽微差) | `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\b1b\narration\attempts\full_story_part2_attempt4_englishstyleprefixwidemargin.wav` |
| 5 | resume#2 | HIGH_SIMILARITY_SAFE、Repetition QA flagで不合格 | `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\b1b\narration\attempts\full_story_part2_attempt5_englishstyleprefixwidemargin.wav` |
| 6 | resume#3 | NORMALIZED_MATCH、Repetition QA flagで不合格(おすすめ) | `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\b1b\narration\attempts\full_story_part2_attempt6_englishstyleprefixwidemargin.wav` |

---

## ユーザー判断の選択肢(既存機構の範囲内、両segment共通)
- (a) いずれかのtakeを試聴し「内容として正しい」と判断すれば、既存の
  `record_human_approval()`で承認記録し、そのtakeを最終音声として採用する。
- (b) 試聴して実際に内容誤りがあると判断すれば、STOPPEDのまま維持する。
- (c) さらなる`approve_regenerate()`による追加retry(既存機構)。

## 既知の残作業(承認後)
`b1b/audit/tts_generation_results.json`は両segmentとも元run(2026-09-11)の
STOPPED記録のまま(resumeで得たtake4-6の結果は
`b1b/audit/human_review_resume_04_results.json`にのみ記録し、既存の監査
ファイルは書き換えていない)。承認後、採用takeをこの監査ファイルへ反映し、
`stage_assemble_b1`(Audio Validation Gate込み)を実行すればB1Bの
Assembly/player.htmlが完成する。
