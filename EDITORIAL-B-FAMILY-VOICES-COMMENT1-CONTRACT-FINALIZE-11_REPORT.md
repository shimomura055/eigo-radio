# EDITORIAL-B-FAMILY-VOICES-COMMENT1-CONTRACT-FINALIZE-11 Report

管理ID: EDITORIAL-B-FAMILY-VOICES-COMMENT1-CONTRACT-FINALIZE-11
日付: 2026-09-08
Lane: Lane B / Voices-Perspective(Comment Contract確定版検証)

## 背景(ユーザー決定、2026-09-08)

Voices Comment Contract全体(Comment 1〜4)を`APPROVED_FOR_PRODUCTION`。
Comment 1はTRIAL-10修正版がベース。あわせて"the question"漏出対策として、
Comment 1 Contractへ禁止句1行を追加(Comment 2〜4は無変更)。ただし
B-Family(Voices)のProduction正式経路は未設計のため、**本タスクは
Production wiringを行っていない**(Lane B側Trial定義ファイル内で確定版
Contractを保持・検証したのみ)。

## 1. Contract diff

対象: `er012_editorial_b_voices_trial_10_comment1.py::VOICES_COMMENT_1_ROLE_TRIAL10`
(TRIAL-10で修正済みのComment 1 Contract定義そのもの)。既存の禁止事項
リスト(避けてください:の4項目)へ1項目のみ追加、他は無変更。

```diff
 以下は避けてください:
 - The Questionで語られる具体的な状況・問いの先取り(内容の先出し)
 - "First point"/"Second point"のようなPoint要約めいた話法
 - 事実を解説するような硬い、Discovery的な説明口調
 - テーマ・場面についての一般的な説明・主張文(聞き方の案内ではなく、内容そのものを
   語ってしまう文)
+- "the question"という語句そのもの(大文字・小文字を問わず)を出力文中で使用すること
+  (番組構成上のPart名"The Question"と紛らわしいため)

 1文程度の、非常に短いListening Focusにしてください。
```

加えて、追加の経緯を残すコメントブロックを1つ追記(コード動作に影響なし)。
役割名・役割記述・既存禁止事項4点・構造ラベル非出力制約(【重要・出力への
制約】段落)・分量指定・Comment 2〜4(`VOICES_COMMENT_2/3/4_ROLE`、
`er012_editorial_b_voices_trial_09_audio.py`)は**一切変更していない**
(importで参照すらしていない)。

## 2. n=3生成 + 機械チェック

新規スクリプト`er012_editorial_b_voices_comment1_contract_finalize_11.py`
(root)から、確定版Contract(禁止句追加済み)で、TRIAL-10/09と同一記事
(`er012_output/editorial_b_voices_trial_07/b1b_run02_attempt2/article.md`、
読み取り専用)・同一Writer primitive(`er003_v1_b1_scaffold_01_generate.run_support_text`)
を使いComment 1テキストをn=3生成(TTSなし、LLM費用のみ)。機械チェックは
Trial-10 Fable追加委任で使った既存関数
(`er012_editorial_b_voices_trial_10_comment1_reproducibility.check_text`、
無変更・importのみ)を再利用。

| run | テキスト | (i) 聞き方案内型 | (ii) 要約・先取り・評価なし | (iii) "the question"/内部section名の非出現 |
|---|---|---|---|---|
| run1 | "As you listen, notice how the speaker compares two different feelings about the same place." | 該当(marker検出) | 該当(断定的要約なし) | 漏出なし |
| run2 | "Listen for the words that show what people prefer and how they feel." | 該当(marker検出) | 該当 | 漏出なし |
| run3 | "As you listen, notice how different people respond to the same workplace." | 該当(marker検出) | 該当 | 漏出なし |

n=3すべてで(i)(ii)(iii)を満たした。TRIAL-10のFable追加委任時(n=3)は
run1のみ"the question"漏出が検出されていたが、禁止句追加後の本n=3では
漏出0/3(n=3という少数試行のため「再発ゼロを保証」するものではないが、
禁止句追加による改善方向とは整合する)。
詳細JSON: `er012_output/editorial_b_voices_comment1_contract_finalize_11/audit/n3_generation.json`

## 3. 最良1本の選定 + Standard TTS + ASR Gate

選定ロジック(`select_best_run()`): (i)(ii)(iii)を全て満たすrunを優先、
複数該当時はrun1を優先。今回は3本とも全条件を満たしたため**run1を選定**
(Fable/ユーザーが別のrunを選び直せるよう3本とも上表に列挙済み)。

- 対象テキスト(run1): "As you listen, notice how the speaker compares two different feelings about the same place."
- TTS primitive: `er003_v1_sing01_voice01_generate.generate_charon_english`
  (Trial-09/10のcomment_1生成と同一関数・同一`style_prefix_override`
  [`B1_PREVIEW_STYLE_PREFIX_CALM`]・`disfluency_qa=True`)
- 結果: `status=OK`、`asr_verified=True`(1回目のattemptでPASS、retryなし)
- `audio_classification=NORMALIZED_MATCH`(ASR文字列は正規化後に一致、
  内容語の欠落・変化なし)
- `disfluency_checked=True`、`disfluency_evidence.flagged=False`
  (反復検出なし)、`clipping_detected=False`
- wav: `er012_output/editorial_b_voices_comment1_contract_finalize_11/narration/comment_1_run1.wav`
- 詳細JSON: `er012_output/editorial_b_voices_comment1_contract_finalize_11/audit/comment1_tts_result.json`

## 4. 確定版Contract全文(Comment 1〜4、Production wiring設計タスクの入力用)

### Comment 1(確定版、`VOICES_COMMENT_1_ROLE_TRIAL10`、禁止句追加済み)

```
あなたはPodcastのナビゲーターです。これから、あるテーマ・場面を短く
提示する「The Question」(冒頭の問いかけ本文)をリスナーが聞きます。その直前に流す、
Comment 1(役割: Listening Focus)を書いてください。

役割: リスナーがこれから聞くThe Questionに対して、何に注目して聞けばよいかを
明確に案内します(例: "Listen for ..."/"As you listen, notice ..."のような、
聞き方を指示する話法)。テーマ・場面についての一般的な説明文や、内容についての
主張・結論めいた文を語ってはいけません(悪い例:「〜は人によって違って感じられる」
のような、The Questionの内容そのものを述べる文)。

以下は避けてください:
- The Questionで語られる具体的な状況・問いの先取り(内容の先出し)
- "First point"/"Second point"のようなPoint要約めいた話法
- 事実を解説するような硬い、Discovery的な説明口調
- テーマ・場面についての一般的な説明・主張文(聞き方の案内ではなく、内容そのものを
  語ってしまう文)
- "the question"という語句そのもの(大文字・小文字を問わず)を出力文中で使用すること
  (番組構成上のPart名"The Question"と紛らわしいため)

1文程度の、非常に短いListening Focusにしてください。

【重要・出力への制約】出力する文章自体に"Part 1"・"Part 2"・"Hook"・"The Question"
のような制作内部の構造ラベルを含めないでください。リスナーは番組の内部構成を
意識しません。
```

### Comment 2(無変更、`VOICES_COMMENT_2_ROLE`)

```
あなたはPodcastのナビゲーターです。リスナーはThe Question(冒頭の
問いかけ)をすでに聞き終わり、これから、この問いに対する異なる立場からの一人称の
語り(One Voiceの後、続けてAnother Voice)を聞きます。その間に流す、Comment 2
(役割: Hookの問いから「ここから異なるVoiceを聞く」への橋渡し)を書いてください。

役割: The Questionで示された問いを受け、「ここから、違う視点を持つ声を順番に
聞いていく」ことへリスナーを橋渡しします。

以下は避けてください:
- One Voice・Another Voiceの具体的な内容の先取り
- これから聞く見出しの文言そのものを、この時点で言うこと(見出しはこの直後に
  Narratorが読み上げます)
- "Point One"・"Point Two"のような表現

1〜2文にしてください。

【重要・出力への制約】出力する文章自体に制作内部の構造ラベルを含めないでください。
```

### Comment 3(無変更、`VOICES_COMMENT_3_ROLE`)

```
あなたはPodcastのナビゲーターです。リスナーは、ある問いに対する
異なる立場からの一人称の語り(One Voice・Another Voice)を両方すでに聞き終わり、
これから「なぜ同じ状況を人によって違って感じるのか」という視点の深掘りを聞きます。
その間に流す、Comment 3(役割: 「どちらが正しいか」ではなく「なぜ違って感じるのか」
への視点の移動)を書いてください。

役割: 2つの声を聞き終えたリスナーの意識を、「どちらが正しいか」という判定ではなく、
「なぜ同じ状況が人によって違って感じられるのか」という問いへ移します。

以下は避けてください:
- これから聞く深掘り部分の答え(視点の違いの正体)を先に説明すること
- どちらか一方の声を「正しい」「間違っている」と評価すること

2〜3文にしてください。

【重要・出力への制約】出力する文章自体に制作内部の構造ラベルを含めないでください。
```

### Comment 4(無変更、`VOICES_COMMENT_4_ROLE`)

```
あなたはPodcastのナビゲーターです。リスナーは「なぜ同じ状況を
人によって違って感じるのか」という視点の深掘りをすでに聞き終わり、これから結びの
まとめを聞きます。その間に流す、Comment 4(役割: 表面的な対立から一段深い問いへの
視点移動)を書いてください。

役割: 「どちらが正しいか」という表面的な対立から、一段深い問い(何がこの状況を
成り立たせているのか)へリスナーの視点を移します。

以下は避けてください:
- これから聞く結びのまとめの要約・結論の先取り
- 解決策の提案

2〜3文にしてください。

【重要・出力への制約】出力する文章自体に制作内部の構造ラベルを含めないでください。
```

出典: Comment 2〜4は`er012_editorial_b_voices_trial_09_audio.py`
(行369〜418、Trial-09以来無変更)からの転記。

## 5. コスト

累積¥0.79(内訳: openai[scaffold n=3] ¥0.16 + gemini[TTS] ¥0.60 +
openai_asr ¥0.03)。TTS+ASR Gate単体¥0.63(上限¥50に対し十分な余裕)。
全体上限¥100に対しても十分な余裕。

## 6. Gate 1 分類

**VALIDATED**(Contract定義への禁止句1行追加、n=3全てで(i)(ii)(iii)
充足、最良1本のASR Gate `NORMALIZED_MATCH`・disfluencyなしでPASS)。

ただし以下は本タスクの範囲外・**USER_DECISION_REQUIRED**のまま:
- 確定版Comment 1テキスト(run1〜3のいずれか)の内容・文体についての
  ユーザー最終試聴確認(本タスクはwav 1本[run1]のみ生成、player.htmlは
  作成していない)。
- n=3という少数試行のため、"the question"漏出ゼロが禁止句追加の効果か
  偶然かは統計的に断定できない(Trial-10 Fable追加委任時のn=3でも
  1/3のみ漏出だったため、母数を増やさない限り確実な再発防止の証明には
  ならない)。
- B-Family Production wiring自体は本タスクの範囲外(ユーザー決定どおり
  未実施)。Production wiring設計タスクは別途進行中。

## 7. 変更・生成ファイル一覧

- 変更(既存Trial定義ファイル、diffは上記1参照):
  `er012_editorial_b_voices_trial_10_comment1.py`
- 新規: `er012_editorial_b_voices_comment1_contract_finalize_11.py`(root)
- 新規: `er012_output/editorial_b_voices_comment1_contract_finalize_11/audit/n3_generation.json`
- 新規: `er012_output/editorial_b_voices_comment1_contract_finalize_11/audit/comment1_tts_result.json`
- 新規: `er012_output/editorial_b_voices_comment1_contract_finalize_11/audit/run_summary.json`
- 新規: `er012_output/editorial_b_voices_comment1_contract_finalize_11/audit/raw_usage_log.jsonl`
- 新規: `er012_output/editorial_b_voices_comment1_contract_finalize_11/narration/comment_1_run1.wav`
  (+ `narration/attempts/`、`er011_human_review_lock_01`の既存attempt保存機構による自動生成物)

Trial-09/10の既存出力ファイル(`er012_output/editorial_b_voices_trial_09_audio/`、
`er012_output/editorial_b_voices_trial_10_comment1/`配下)は一切書き換えて
いない(読み取りのみ)。Production コード・Prompt(Lane A共有)・SSOT・
`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`は未編集。Git操作は行っていない。

補足: `er011_output/attempt_history.jsonl`は、指定どおりProduction TTS
primitive(`generate_charon_english`)を無変更のまま呼び出したことに伴い、
既存の`er011_human_review_lock_01`安全機構が**自動的に1行追記**した
(run_id `12080226-...`、theme_id `er012_output`、
level `editorial_b_voices_comment1_contract_finalize_11`、
`result_status=OK`、`human_review_reached=false`)。これは既存の安全装置
自体の通常動作(append-onlyログ)であり、本タスクが内容を編集・削除した
ものではない。同ファイルには本タスク開始前から他タスク由来の未commit差分
(git status上`M`)が既に存在しており、本タスクはその既存差分を編集して
いない。
