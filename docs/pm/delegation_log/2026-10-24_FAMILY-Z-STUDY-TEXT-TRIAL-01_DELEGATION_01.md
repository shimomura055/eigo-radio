FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_01(Fableから): ユーザー指示「Family Z 英語学習テキスト解説 Trial-01」を実施する。Trial専用(DEV)、ProductionのPrompt・コード・経路・成果物は変更しない。到達上限VALIDATED。**一発生成の実力評価が最優先: 初回出力をそのまま保存し、Prompt修正・再生成を繰り返さない。**

## 0. 最初に(0円)
- ユーザー指示原文(本委任文末尾【ユーザー原文】、逐語・改変禁止)を `docs/pm/delegation_log/2026-10-24_FAMILY-Z-STUDY-TEXT-TRIAL-01_USER.md` に保存。
- 入力の確認(`docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/INPUT_CHECK_01.md`): 対象=『賢者の贈り物』Advanced完成本文(`er026_output/family_z_production_e2e_01/the_gift_of_the_magi/run_sf_prod_01/` のAdv最終稿=Writer r2、434語30段落。ユーザー承認済みPASS、UDR #177)、既存Key Phrase(Adv: `hand down`/`catch sight of`/`catch one's breath`、`keywords_canonicalized.json`等から英語・日本語gloss・本文該当文・既存の音声解説文を取得)、Production KP段のモデル設定(gpt-6-luna、reasoning設定、temperature等)。**AdvのKPは3件しかない**ため「最大5個」は3個で実施(新たな選定はしない。Std KPは対象外)。完成本文が見つからなければ代用せずSTOPして報告。
- 費用上限5円(Fable 7-3自律。日次10-24把握分約460円+X/Z制作残≤60円で1,000円内)。

## 1. Prompt作成(`PROMPT_01.md` に全文保存)
- 入力: Adv完成本文全文(段落番号付き)、KP 3件(英語/日本語gloss/本文の該当文/既存音声解説の要約=重複回避用)、作品名・レベル(Advanced=CEFR B1〜B2相当。CURRENT_SPECのAdvanced定義を節Grepして記載)。
- 出力仕様(ユーザー原文§3を忠実に): Part 1 Vocabulary & Expressions(KP 3件: 英語表現/日本語意味/本文中の英文と日本語訳/表現の意味・学習上の重要性。追加例文不要。既存音声解説の単純な繰り返し禁止) / Part 2 Grammar & Sentence Structure(0〜2個、無理に選ばない。本文引用+日本語訳、仕組みと本文中での意味・効果) / Part 3 Nuance & Deeper Understanding(0〜1テーマ、無理に作らない。Part1・2と重複禁止、本文に根拠のない説明禁止、感想・一般論禁止) / Part 4 Think & Express(1問: 英語質問/日本語訳/英語回答例/日本語訳)。理解度チェック・クイズ不要。
- 制約を明示: 引用は本文から**逐語**(改変禁止)、本文にない事実・表現を作らない、日本語は学習者向けに読みやすく、Markdown見出し構成を指定。出力形式はMarkdown(JSON不要)。
- Promptは「必要十分」に留め、few-shotや段階生成を入れない(一発生成の評価が目的)。

## 2. 生成(1回)
- モデル: gpt-6-luna(Production KP段と同じmodel_id、reasoning設定を記録)。API 1 call。出力を `OUTPUT_01_RAW.md` に**そのまま**保存(編集禁止)、usage(入出力/reasoningトークン・円)を `BUDGET_LOG_01.md` に。
- 通信エラー等の技術的失敗のみ再送可(内容理由の再生成は禁止)。再送した場合は記録。

## 3. 機械・目視評価(`EVAL_01.md`。Fable独立評価は別途)
- A 整合性: 出力中の英文引用を全て抽出し、Adv本文に逐語で存在するかを機械照合(存在/不一致/部分一致の表)。日本語訳・文法説明の誤りをagent目視で列挙(断定できないものは「要Fable確認」)。本文にない内容・事実の創作の有無。
- B 学習価値: Advanced適性、表面的でないか、文法・ニュアンス選定の妥当性(選ばれた対象と、本文中の他の候補との比較を1〜2行)、無理な解説の有無(Part2/3が0個の場合はその判断の妥当性)。
- C Production適性: 1回で実用品質か、確認・修正に要する手間の見積(分)、量産での再現性の懸念、追加費用(1記事セットあたり)。
- Part 1が既存KP音声解説の繰り返しになっていないか(既存解説文と並べて示す)。

## 4. 記録・Git
- `OPEN_ITEMS.md` に本Trialの項目を新規登録(分類: Trial・ユーザー判断待ち)、`DECISION_LOG.md` は本委任では触らない(Fable評価後)。
- `git status`でindex確認→`git commit --only -- <本委任ファイル>`→`git push origin HEAD:main`。禁止操作(add -A/-u/-f/-N、amend、rebase、force push、stash、clean、reset --hard、checkout -f)。raw_usage_log・ACTIVE_TASK・RESULT_PACKET不追跡。他agent(X/Z制作中)のSSOT差分を巻き込まない(一時index方式)。secret grep 0件。
- 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_FAMILY-Z-STUDY-TEXT-TRIAL-01_DELEGATION_01.md`(Nは先頭「FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_01」を含むAgent呼出の0始まり通番、直近466以降)。

## 5. handback(ユーザー原文§6の7項目)
1 生成テキスト全文(省略不可、OUTPUT_01_RAWをそのまま) / 2 使用本文(run・語数)・KP・実際のmodel_id・設定 / 3 Prompt全文 / 4 初回品質評価(A/B/C) / 5 問題点と原因 / 6 実測費用・量産単価への追加影響 / 7 Production化の課題・改善提案(追加Trial案は提案のみ、実施しない)。RESULT_PACKET 4行、commit hash、raw URL。

【ユーザー原文】
# Claude Codeへの指示
## Family Z 英語学習テキスト解説 Trial-01

### 1. 目的

eigo-radioの有料サービス向けに、音声コンテンツと連動した英語学習テキストを追加したい。

今回のTrialでは、**Lunaによる一発生成で、学習価値の高い解説を安定的に制作できるか**を検証する。

特に、文法・構文解説とニュアンス解説の品質を重視する。

### 2. 対象・前提

- 対象作品：Family Z『賢者の贈り物（The Gift of the Magi）』
- 使用本文：既存の完成済み英語本文
- 対象レベル：Advanced
- 生成モデル：Luna
- 既存Key Phraseの選定結果を再利用
- 今回はTrial専用。ProductionのPrompt・コード・経路は変更しない

まず既存Repoから対象作品の本文・Key Phrase・モデル設定を確認する。

該当する完成本文が存在しない場合は、別の本文を無断で代用せず報告する。

### 3. 生成する学習コンテンツ

#### Part 1. Vocabulary & Expressions

- 既存Key Phraseから最大5個を使用する。
- 新たなフレーズ選定は行わない。
- 英語表現、日本語意味、本文中の英文と日本語訳、表現の意味・学習上の重要性を解説。
- 「ほかの場面で使うと」の追加例文は不要。
- 既存のKey Phrase音声解説の単純な繰り返しにならないようにする。

#### Part 2. Grammar & Sentence Structure

- 本文から学習価値の高い文法・構文を0〜2個選ぶ。
- 無理に2個選定しない。適切なものがなければ0個でもよい。
- 実際の本文を引用し、日本語訳を付ける。
- 文法・構文の仕組みと、本文中での意味・効果をわかりやすく解説。
- 教科書的な説明だけでなく、英文を理解する助けになることを重視する。

#### Part 3. Nuance & Deeper Understanding

- 本文から価値のある英語表現・ニュアンスを0〜1テーマ選ぶ。
- 適切なテーマがない場合は0個とし、無理に生成しない。
- 単語の意味だけでは伝わりにくいニュアンス、似た表現との違い、英語の表現による印象の違いなどを深掘りする。
- Part 1・2と内容が重複しないようにする。
- 物語の感想や一般論ではなく、英語学習としての価値を重視する。
- 本文に根拠のない説明や表現を作らない。

#### Part 4. Think & Express

- 作品の内容に関連して、自分の考えを英語で表現する問いを1問作る。
- 英語の質問、日本語訳、英語回答例、日本語訳を付ける。
- 回答例は学習者が参考にできる自然な英語とする。

理解度チェック・クイズは不要。

### 4. Trial方法

今回は**一発生成の実力を評価することが最優先**。

1. 既存の完成本文・Key Phraseを入力する。
2. 必要十分なPromptを作成する。
3. Lunaで4 Partを一括生成する。
4. 初回出力をそのまま保存し、評価する。

初回結果が不十分でも、自動的なPrompt修正・再生成を繰り返さない。

失敗原因と改善可能性を分析し、必要なら追加Trial案として報告する。

既存の承認済み仕様や品質基準は変更しない。

### 5. 評価項目

以下を確認する。

**A. 本文との整合性**
- 解説対象の英文が実際の完成本文に存在するか。
- 英文・日本語訳・文法説明に誤りがないか。
- 本文にない内容や事実を創作していないか。

**B. 学習価値**
- Advanced学習者にとって適切か。
- 表面的な意味説明に終わっていないか。
- 文法・ニュアンスの選定が妥当か。
- 不要な解説を無理に作っていないか。

**C. Production適性**
- 原則1回の生成で実用的な品質に達するか。
- 品質確認や修正にどの程度の手間が必要か。
- 量産時に安定して再現できそうか。
- 追加生成費用はいくらか。

### 6. 成果物

次の内容を報告すること。

1. **生成した学習テキスト全文**（省略不可）
2. 使用した本文・Key Phrase・実際のmodel_id
3. Lunaに渡したPrompt全文
4. 初回生成結果の品質評価
5. 発見した問題点と原因
6. 実測費用・量産単価への追加影響見込み
7. Production化に向けた課題と改善提案

学習テキストは、ユーザーが実際に読んで評価できるよう、読みやすい形式で提示すること。今回は専用Webページの制作までは不要。

### 7. PM Gate・STOP条件

- 今回の到達可能StatusはVALIDATED／REJECTED／USER_DECISION_REQUIRED。
- Trial成功でもProductionへの正式採用・配線は行わない。
- 追加Trial、新仕様採用、品質基準変更はユーザー判断を要する。
- 既存の正式Production経路・成果物は変更しない。
- 既存作品の入力データが不足するなど、評価の前提が成立しない場合はSTOP。
- Trial費用は実測・記録し、承認済み開発予算内で実施する。
- 結果と判断待ち事項は既存のSSOT管理ルールに従って記録する。

### 8. 最重要事項

今回は、完成度を高めるために何度も生成することが目的ではない。

**Lunaが初回生成でどこまで優れた教材を作れるかを、ありのまま評価すること。**

特に文法・ニュアンス解説について、AIが適切な対象を自律選定し、必要十分な品質の解説を作れるかを見極めること。

Trial終了時にFableによる独立評価を行い、ユーザーの正式採用判断に必要な情報を揃えて報告すること。