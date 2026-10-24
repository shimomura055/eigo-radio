FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_03 = Trial-02(Fableから): ユーザー指示「Family Z 英語学習テキスト解説 Trial-02」を実施。Trial-01(`docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/{PROMPT_01,OUTPUT_01_RAW,EVAL_01,FABLE_EVAL_01}.md`、`run_trial_01.py`、commit e3285a2d1)と同一の本文(『賢者の贈り物』Adv r2、434語)・同一KP 3件・同一model_id(gpt-6-luna)・同一API設定で、**Part 1の解説指示のみ差し替え**、1回生成、無編集保存、Trial-01と比較。Production変更なし、追加生成・自動修正・KP追加選定は禁止。到達上限VALIDATED。上限5円。UDR #182(次工程A/B/C)はユーザーが本指示で別方向(Part 1方針変更の比較Trial)を選んだため「判断済み(Trial-02実施へ置換)」に更新。

## 0. 記録(0円)
- ユーザー指示原文(本委任文末尾【ユーザー原文】、逐語)を `docs/pm/delegation_log/2026-10-24_FAMILY-Z-STUDY-TEXT-TRIAL-01_USER_02.md` に保存。
- 入力同一性の確認(本文sha256・KP・model_id・API設定がTrial-01と一致することを `INPUT_CHECK_02.md` に。差異があれば明示)。

## 1. Prompt(`PROMPT_02.md` 全文保存、Trial-01との差分を `PROMPT_DIFF_02.md`)
- Trial-01のPromptをベースに、**Part 1の指示だけ**を次に差し替える(Part 2〜4・制約・本文・KP入力は1字も変えない):
  「## Part 1. Vocabulary & Expressions — 上のKey Phrase 3件それぞれについて、次を書く: 1 英語表現 / 2 日本語の意味 / 3 本文中の英文(逐語引用) / 4 英文の日本語訳 / 5 実用性を重視した解説。実用性重視の解説ルール: その単語・フレーズが、本文以外のどのような日常・仕事・社会的場面で使えるかを、具体的かつ簡潔に説明する。重視する点: 実際にどのような状況で使えるか / その表現を使うと何が伝わるか / 学習者が自分の英語表現に取り入れやすい説明になっているか。文法構造の解説は原則としてPart 2に任せる。『ほかの場面で使うと』という独立した追加例文は書かない。実用場面は日本語の解説文で伝える。」
- ユーザーの参考例3件(hand down/catch sight of/catch one's breath)は**Promptに入れない**(入れると一発生成の評価にならない。参考例は評価時の比較基準として使う)。この判断はPROMPT_DIFF_02に明記。

## 2. 生成(1回)
- `run_trial_01.py` と同じ呼出(model_id・Responses API・reasoning/temperature既定)で1 call。出力を `OUTPUT_02_RAW.md` に無編集保存、usage・費用・所要秒を `BUDGET_LOG_01.md` に追記(cost実測)。通信エラー以外の再送禁止。

## 3. 評価(`EVAL_02.md`、Fable独立評価は別途)
1. Part 1が実用性重視か(各KPについて: 使える場面の具体性/何が伝わるか/取り入れやすさ、文法解説の混入有無)。
2. ユーザー参考例との比較(具体性・自然さを同程度/上回る/下回るで、根拠の引用付き)。
3. Part 2〜4のTrial-01との比較(選定対象・説明の質・形式。同じ対象を選んだか、品質維持か)。
4. 正確性: 引用の逐語一致(機械照合)、日本語訳・文法・説明の誤り、創作の有無。
5. 1回生成で実用品質か(人手確認の見積)。
6. 費用・所要時間(Trial-01=0.230円/24.7秒との比較)。
- 評価は出力を見てから基準を変えない。Trial-01とTrial-02の全文を並べた比較表(Part別)を作る。

## 4. 記録・Git
- `OPEN_ITEMS.md` OPEN-497にTrial-02実施を1行、`docs/pm/USER_DECISION_REGISTER_01.md` #182を上記のとおり更新。DECISION_LOGは触らない(Fable評価後)。
- `git status`→`git commit --only`→`git push origin HEAD:main`(他agent差分を巻き込まない=一時index、禁止操作なし、secret grep 0件)。
- 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_FAMILY-Z-STUDY-TEXT-TRIAL-01_DELEGATION_03.md`(Nは先頭「FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_03 = Trial-02」を含むAgent呼出の0始まり通番、直近475以降)。

## 5. handback(ユーザー原文§7): 1 Trial-02全文(無編集・省略不可) / 2 Trial-01との比較(特にPart 1、参考例との比較含む) / 3 Part 2〜4の維持状況 / 4 Prompt全文(本文は〈本文〉で省略可、Part 1差分は逐語)・model_id・設定 / 5 費用・所要時間 / 6 (Fable評価欄は空) / 7 残存課題とStatus案。RESULT_PACKET 4行、commit hash、raw URL。

【ユーザー原文】
# Claude Codeへの指示
## Family Z 英語学習テキスト解説 Trial-02

### 1. 目的

Lunaによる英語学習テキスト解説の品質改善・再現性確認を行う。

Trial-01では、本文整合性・文法解説は概ね良好だったが、Part 1の解説が文法・構文寄りになっていた。

今回、ユーザーが承認した**「実用性重視」の解説方針**を適用し、学習者が「自分でも使える」と感じられる解説になるか検証する。

### 2. 対象・モデル

- 対象：Family Z『賢者の贈り物』
- レベル：Advanced
- 本文：Trial-01と同一の完成英語本文
- Key Phrase：Trial-01と同一の3個
  - hand down
  - catch sight of
  - catch one's breath
- モデル：Luna（Trial-01と同一のmodel_id・API設定）
- 生成回数：原則1回
- Production変更なし

### 3. 今回の変更内容

**Part 1. Vocabulary & Expressionsのみ、解説方針を変更する。**

各表現について以下を出力する。

1. 英語表現
2. 日本語の意味
3. 本文中の英文（逐語引用）
4. 英文の日本語訳
5. 実用性を重視した解説

#### 実用性重視の解説ルール

その単語・フレーズが、本文以外のどのような日常・仕事・社会的場面で使えるかを、具体的かつ簡潔に説明する。

以下を重視する。

- 実際にどのような状況で使えるか。
- その表現を使うと何が伝わるか。
- 学習者が自分の英語表現に取り入れやすい説明になっているか。

文法構造の解説は原則としてPart 2に任せる。

「ほかの場面で使うと」という独立した追加例文は不要。実用場面は日本語の解説文で伝える。

#### 期待する品質の具体例

**hand down**

家族の思い出の品だけでなく、伝統、技術、価値観などにも使えます。例えば、何世代にもわたって受け継がれてきた伝統や、先輩から後輩へ伝えられる技術を説明するときにも役立つ表現です。

**catch sight of**

人や物を偶然見かけたときに使う表現です。街中で知り合いを見かけたり、人混みの中で探していた人を見つけたりする場面で役立ちます。意識的に探して見るというより、何かがふと視界に入ったことを伝えられます。

**catch one's breath**

走った後や階段を上った後など、息が上がったときによく使います。また、忙しい仕事が続いた後に、少し落ち着く時間が欲しいときにも使えます。身体的な息切れだけでなく、慌ただしい状況から一息つくことも表現できます。

これらは品質・方向性の参考例であり、必ずしも逐語的な再現を要求しない。

### 4. その他のPart

**Part 2. Grammar & Sentence Structure**
- 0〜2個。
- Trial-01のPrompt・仕様を変更しない。

**Part 3. Nuance & Deeper Understanding**
- 0〜1テーマ。
- Trial-01のPrompt・仕様を変更しない。
- 前回の `worthy of` と `worth` の解説もユーザーの許容範囲であり、今回の改善対象にはしない。

**Part 4. Think & Express**
- 1問。
- Trial-01のPrompt・仕様を変更しない。

### 5. Key Phrase追加選定について

将来的には、既存の3個に加え、学習価値の高い表現を最大2個追加し、合計5個とする案を検討している。

ただし、**この案は現在保留であり、未承認。**

今回のTrialでは追加選定を行わず、既存の3個のみ使用する。

ProductionのKey Phrase選定仕様も変更しない。

### 6. Trial方法・評価

Trial-01のPromptをベースに、Part 1の解説指示のみ差し替える。

- Lunaで4 Partを一括生成する。
- 初回出力を無編集で保存する。
- 自動修正・追加生成は行わない。
- Trial-01との比較を実施する。

評価観点：

1. Part 1が実用性重視の解説になっているか。
2. ユーザーが承認した参考例と同程度の具体性・自然さがあるか。
3. Part 2〜4の品質がTrial-01と同程度に維持されているか。
4. 本文引用・日本語訳・文法・説明の正確性に問題がないか。
5. 1回の生成で実用的な品質に到達するか。
6. 生成費用と所要時間。

Fableによる独立評価を実施すること。

### 7. 成果物・報告

以下を提出する。

1. **Trial-02の学習テキスト全文（無編集）**
2. Trial-01との比較評価（特にPart 1）
3. Part 2〜4の品質維持状況
4. 使用Prompt全文・実際のmodel_id
5. 生成費用・所要時間
6. Fable独立評価
7. 残存課題とTrial Closeout Status

### 8. Gate・STOP条件

- 今回はTrialのみ。
- 新しいPromptのProduction採用・配線は禁止。
- Trial終了時はVALIDATED／REJECTED／USER_DECISION_REQUIREDに分類する。
- 正式採用はユーザー判断とする。
- Trial-01と同じ本文・モデル条件が使えない場合は、差異を明示する。
- 既存承認済み予算内で実施する。
- 品質基準を独断で引き上げたり、追加Trialを始めたりしない。
- SSOT・OPEN_ITEMS・Gitへ必要な結果を記録する。

**最重要：今回はPart 1の改善効果を確かめる比較Trialであり、他のPartの改善やKey Phraseの追加選定を同時に行わないこと。**

初回生成結果をそのまま提出し、ユーザーが品質を判断できる状態にする。