2026-10-16 ユーザー指示原文(Fable受領)

# Claude Code／Fableへの指示
## Coffee Advanced 英語解説TTS・速度／ポーズ改善Trial

**管理ID：FAMILY-X-COFFEE-KP-EN-EXPLANATION-PACING-TRIAL-01**

**現在Status：TRIAL（未検証）**

**今回の到達上限：VALIDATED**

**Production反映：禁止。ユーザー採用判断待ちでSTOP。**

## 1. 目的

Coffee記事のAdvanced向けKey Phrase英語解説について、現在の音声は全体的にやや遅く、意味の塊ごとのポーズが長いため、不自然に聞こえる。

英英解説であることから、**ややゆっくり・明瞭で理解しやすい読み方を維持しつつ、過剰な減速と不自然なポーズを改善する。**

通常のニュース朗読の速さを目指すTrialではない。速度変更は控えめとする。

## 2. 対象・固定条件

- 記事：Coffee
- レベル：Advancedのみ
- Section：Key Phraseの英語解説（explanation_en）
- 対象原稿：現在のCoffee記事で実際に使用している英語解説5本
- 比較：8 Prompt × 5本＝40音声
- Voice：現行Productionと同じAoede
- TTSモデル：現行Productionと同じ `gemini-3.8-flash-lite-tts`
- 音声生成・trim・その他条件：原則現行Productionと同一
- 原稿・Key Phrase・解説文の変更：禁止
- Standard日本語解説、英語Phrase音声、その他Section：対象外

最初に現行Coffee記事の解説原稿5本、採用Prompt、TTS経路を確認する。

現行Promptは、Coffee用style profileのP3を正本とし、Productionで実際に送信されるStyleと照合する。

**既存完成音声は比較用として保存し、上書きしない。**

## 3. 比較する8 Prompt

### P0：現行Production

```text
clear, precise, at a measured pace, without dragging Let the sentence flow from its first word to its last, without stopping partway through.
```

### P1：最小変更・ポーズ調整

```text
clear, precise, at a measured pace, without dragging Keep pauses between phrases brief and natural, letting the explanation flow smoothly.
```

### P2：ややゆっくりを明示

```text
Clear and precise, at a slightly slower than conversational pace. Keep the explanation flowing naturally, with brief pauses.
```

### P3：語句の連結重視

```text
Clear, precise, at a measured pace, without dragging. Connect the words and phrases naturally, with no unnecessary breaks.
```

### P4：自然な英語教師の説明

```text
Explain clearly and naturally, like a patient English teacher speaking to a learner. Use a slightly relaxed pace and smooth phrasing.
```

### P5：理解に必要な短い間だけを許容

```text
Clear and easy to follow, at a gently measured pace. Use only short, natural pauses where they help understanding.
```

### P6：一文としての滑らかさ

```text
Clear, precise, and gently paced. Deliver the explanation as one smooth, connected thought, without stretching the spaces between phrases.
```

### P7：速度・リズムのバランス型

```text
Speak clearly at a slightly relaxed, natural pace. Keep a steady rhythm, with brief transitions between phrases and no drawn-out pauses.
```

上記8案は比較対象として固定する。Claude/Fableの判断で候補を追加・改変しない。

## 4. Trial実施方法

1. Coffee記事の解説5本を、現行Productionの正本から取得する。
2. 8案のStyle文字列をそのまま使って、各5本のTTSを生成する。
3. モデル・Voice・原稿・パラメータを統一する。
4. Trial用の独立ディレクトリへ保存する。
5. 既存の安全QA／ASR検証を行う。
6. 5本を候補別・原稿別に比較できる試聴ページを作成する。

P0は現行Production Promptで新規生成した音声を原則使用する。既存Production音声も参照として表示してよいが、同条件の比較結果と混同しない。

生成条件を変更して不合格音声を都合よく救済しない。

**予定40音声以外の追加Take・派生案・再Trialはユーザー承認なしに実施しない。**

## 5. 評価項目

| 評価 | 内容 |
|---|---|
| 音声速度 | 過度に遅くなく、Advanced英英解説として適度にゆっくりか |
| 文中ポーズ | 意味の塊ごとの長い無音が減っているか |
| リズム | 一文として自然につながっているか |
| 明瞭性 | 英語学習者にとって単語が聞き取りやすいか |
| 自然さ | 機械的・ぶつ切り・過剰な教師口調にならないか |
| 安定性 | 5本で同じ傾向が得られるか |
| ASR／QA | 原稿と音声の内容が一致し、品質に問題がないか |

可能な範囲で、実測WPM、音声全長、発話時間、無音の長さと回数を比較する。

特に**文中ポーズと文末無音を分けて記録**する。

ただし、数値だけで優劣を決めず、最終的には自然さ・聞き取りやすさを重視する。

実際に試聴・評価していないものを「試聴合格」と記載しない。

## 6. 試聴ページ

ユーザーが比較しやすいシンプルなページを作成する。

- 各Key Phraseの英語解説原稿を表示
- 同じ解説文についてP0〜P7を横並び、または切替で比較
- 個別再生ボタン
- Prompt一覧・狙いの表示
- 必要に応じた音声長・WPM・ポーズ指標
- 既存Production完成音声との比較

可能なら、**5本の解説ごとに8候補を聞き比べる構成**とし、速度・間の違いが直感的に分かるようにする。

最終報告には、必ずユーザーがアクセス可能な試聴URLを添付する。ローカルパスだけで報告を終えない。

## 7. QDCと費用

- 既存の原稿・モデル・音声生成資産を再利用する。
- 新しいTTSモデル探索や不要なResearchを行わない。
- 事前に40音声の費用見積もりを作成する。
- 既存のTrial予算・STOP条件を守る。
- 実費・呼出回数・失敗件数を記録する。
- ASR失敗・TTS障害などで予定外のAPI呼出が必要になった場合は、原因と影響を確認してSTOPする。
- 独立した分析・ページ構築等は並列化してよいが、無駄な生成は避ける。

## 8. Trial終了時のGate

Trial結果を以下のいずれかに分類する。

- **VALIDATED**：改善候補として評価可能。
- **REJECTED**：改善効果不足、品質問題、または安定性不足。
- **USER_DECISION_REQUIRED**：候補の採否や追加検証についてユーザー判断が必要。

**Trial成功はProduction採用ではない。**

Coffeeの現行Production Prompt・style profileは変更しない。

他記事・他Familyへの展開も禁止する。

ユーザーが正式採用する場合のみ、別途APPROVED_FOR_PRODUCTIONとしてProduction Wiringへ進む。

## 9. 最終報告

以下を簡潔に報告する。

1. 実際に使用したCoffee英語解説5本。
2. 8候補×5本の生成成否。
3. 試聴ページURL。
4. 速度・ポーズ・自然さの比較結果。
5. 改善効果が見込める上位候補。
6. ASR／音声QAの結果。
7. 実費・TTS呼出数。
8. 各候補のTrial Status。
9. ユーザー判断が必要な事項。

**8案の試聴ページと比較結果を提示したところでSTOPすること。**

ユーザー承認なしに候補PromptをProductionへ反映しない。
