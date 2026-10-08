## P1. 要約 In one line プロンプト(M1)

### 変更前(FAMILY_X_IN_ONE_LINE_INSTRUCTION_TEMPLATE、全文。{article_text}を差し込む)
```text
Below is a finished English news feature article (already translated from Japanese, no section headings). Write ONE short, natural sentence that captures the core of the story, in a way a listener can understand by hearing it just once.

Requirements:
- Exactly one sentence.
- Understandable on a single listen.
- Do not pack in multiple separate points; focus on the single most important point or twist of the story.
- Do not add any new fact, conclusion, or lesson that is not already stated in the article below.

As a rough guide only (Trial-only guidance, not a strict rule): aim for one main clause with at most one subordinate clause, roughly 12-18 words.

Output only the sentence itself, nothing else (no quotation marks, no label like "In one line:", no Markdown heading markup).

[Article]
{article_text}
```

### 変更後(OPEN243_M1、FAMILY_X_IN_ONE_LINE_INSTRUCTION_TEMPLATE_M1、全文。再生成時は末尾に build_must_fix_block(既存関数、無変更)の出力を追加)
```text
Below is a finished English news feature article (already translated from Japanese, no section headings). Write ONE short, natural sentence that captures the core of the story, in a way a listener can understand by hearing it just once.

Requirements:
- Exactly one sentence.
- Understandable on a single listen.
- Do not pack in multiple separate points; focus on the single most important point or twist of the story.
- Do not add any new fact, conclusion, or lesson that is not already stated in the article below.
- Keep who did what to whom, and what exactly it applied to, the same as in the Japanese source article and the Ledger below.

As a rough guide only (Trial-only guidance, not a strict rule): aim for one main clause with at most one subordinate clause, roughly 12-18 words.

Output only the sentence itself, nothing else (no quotation marks, no label like "In one line:", no Markdown heading markup).

[Article]
{article_text}

[Japanese source article]
{ja_text}

[Verified Fact Ledger]
{ledger_text}
```

### build_must_fix_block の出力例(既存、無変更。再生成時のみ末尾に付く)
```text
The previous version had the following Fact Safety issues when checked against the Verified Fact Ledger. You must resolve every item below. Fix only what is necessary to make each claim consistent with the Ledger; do not introduce new claims, details, or scope while fixing these.
1. Fact ID: <fact_id> | Claim in article: <要約の該当文> | Issue: <指摘> | Explanation: <説明>
```

### 差分(unified diff)
```diff
--- before
+++ after
@@ -5,6 +5,7 @@
 - Understandable on a single listen.
 - Do not pack in multiple separate points; focus on the single most important point or twist of the story.
 - Do not add any new fact, conclusion, or lesson that is not already stated in the article below.
+- Keep who did what to whom, and what exactly it applied to, the same as in the Japanese source article and the Ledger below.
 
 As a rough guide only (Trial-only guidance, not a strict rule): aim for one main clause with at most one subordinate clause, roughly 12-18 words.
 
@@ -12,3 +13,9 @@
 
 [Article]
 {article_text}
+
+[Japanese source article]
+{ja_text}
+
+[Verified Fact Ledger]
+{ledger_text}
```

## P2. EN deviation check プロンプト(M2)

### 変更前(DEVIATION_PROMPT_TEMPLATE、全文)
```text
以下の記事本文が、Verified Fact Ledgerが保証する「意味上のFact」の
範囲内に収まっているかを、Fact Safetyの観点のみで確認してください。

【Verified Fact Ledger】
{verified_ledger_text}

【検証対象の記事】
{article_text}

【判定対象は次の10種類の意味変化のみです】
- changed_fact: Ledgerに存在しない、またはLedgerと矛盾する具体的事実を主張している
- changed_scope: Ledgerが確認した対象(誰が・どこで・いつ・どの集団か)を超えて一般化・拡張している
- changed_causality: 相関を因果に変えている、または因果の方向を変えている
- changed_certainty: Ledgerでは仮説・自己申告・専門家の解釈にすぎないものを、断定的な事実であるかのように強めている
- changed_number: 数値・割合・件数をLedgerと異なる値に変えている(単位の違いだけの言い換えは含まない)
- changed_actor: 発言主体・調査主体をLedgerと異なる人物・組織にすり替えている
- changed_negation: 肯定・否定を反転させている
- changed_comparison: 比較の方向(より多い/少ない、より高い/低い等)を反転・変更している
- changed_time: 時期・年代をLedgerと異なるものに変えている
- unsupported_new_claim: Ledgerに全く存在しない新しい具体的主張を追加している

【deviationとして報告しないもの(許容範囲)】
- 自然なparaphrase、A2/B1向けの平易な言い換え、語順変更、同義語への置換
- 出典名を一般的な言い方(a report, a studyなど)に置き換えること自体
- 意味を変えない軽いbridge sentence(異なるEvidence間をつなぐだけの文)
- 明確な新規Factを伴わない一般的な情景描写(例: 支払い画面はレストランやカフェにもある、
  という一般常識レベルの前置き)
- Ledgerの特定の一文と一字一句一致しないが、同じ意味を保っている表現

【判定ルール】
- 上記10種類のいずれかが明確にtrueである場合のみ、severityをMAJORにしてください。
- 10種類すべてがfalseなのにMAJORにすることは禁止です。
- 意味はおおむね保っているが言い回しがやや粗い場合(出典に勝手な肩書きを補う、
  自己申告の調査結果を断定的な行動として書く等)はMINORとして記録してください。
- 判断に迷う場合は、「記事の主張がLedgerの主張とほぼ同じ意味を保っているか」を
  最優先の基準にしてください。厳密な文言一致は求めません。
- 各deviationについて、上記10種類のフラグ全てにtrue/falseを明示し、
  explanationでどのフラグに基づいてその判定になったかを一言で説明してください。

該当するdeviationがなければ、deviationsを空配列にしてください。
```

### 変更後(OPEN243_M2、全文)
```text
以下の記事本文が、Verified Fact Ledgerが保証する「意味上のFact」の
範囲内に収まっているかを、Fact Safetyの観点のみで確認してください。

【Verified Fact Ledger】
{verified_ledger_text}

【検証対象の記事】
{article_text}

【判定対象は次の10種類の意味変化のみです】
- changed_fact: Ledgerに存在しない、またはLedgerと矛盾する具体的事実を主張している
- changed_scope: Ledgerが確認した対象(誰が・どこで・いつ・どの集団か)を超えて一般化・拡張している
- changed_causality: 相関を因果に変えている、または因果の方向を変えている
- changed_certainty: Ledgerでは仮説・自己申告・専門家の解釈にすぎないものを、断定的な事実であるかのように強めている
- changed_number: 数値・割合・件数をLedgerと異なる値に変えている(単位の違いだけの言い換えは含まない)
- changed_actor: 発言主体・調査主体・依頼主体・行為主体、または受け手/かけ手(誰が誰に対して行ったか)をLedgerと異なる人物・組織に入れ替えている(受動化による主体の転換、主語省略の誤った補完を含む)
- changed_negation: 肯定・否定を反転させている
- changed_comparison: 比較の方向(より多い/少ない、より高い/低い等)を反転・変更している
- changed_time: 時期・年代をLedgerと異なるものに変えている
- unsupported_new_claim: Ledgerに全く存在しない新しい具体的主張を追加している

【deviationとして報告しないもの(許容範囲)】
- 自然なparaphrase、A2/B1向けの平易な言い換え、語順変更、同義語への置換
- 出典名を一般的な言い方(a report, a studyなど)に置き換えること自体
- 意味を変えない軽いbridge sentence(異なるEvidence間をつなぐだけの文)
- 明確な新規Factを伴わない一般的な情景描写(例: 支払い画面はレストランやカフェにもある、
  という一般常識レベルの前置き)
- Ledgerの特定の一文と一字一句一致しないが、同じ意味を保っている表現
- 文脈から一般に想像できる補足(例: 開示の相手が利用者であること)や、指標の一般化(例: Brent先物の動きをoil pricesと言うこと)は、新しい具体的主張を伴わない限り報告しない(因果関係の付与はこの対象外)

【判定ルール】
- 上記10種類のいずれかが明確にtrueである場合のみ、severityをMAJORにしてください。
- 10種類すべてがfalseなのにMAJORにすることは禁止です。
- 意味はおおむね保っているが言い回しがやや粗い場合(出典に勝手な肩書きを補う、
  自己申告の調査結果を断定的な行動として書く等)はMINORとして記録してください。
- 判断に迷う場合は、「記事の主張がLedgerの主張とほぼ同じ意味を保っているか」を
  最優先の基準にしてください。厳密な文言一致は求めません。
- 各deviationについて、上記10種類のフラグ全てにtrue/falseを明示し、
  explanationでどのフラグに基づいてその判定になったかを一言で説明してください。

該当するdeviationがなければ、deviationsを空配列にしてください。
```

### 差分(unified diff)
```diff
--- before
+++ after
@@ -13,7 +13,7 @@
 - changed_causality: 相関を因果に変えている、または因果の方向を変えている
 - changed_certainty: Ledgerでは仮説・自己申告・専門家の解釈にすぎないものを、断定的な事実であるかのように強めている
 - changed_number: 数値・割合・件数をLedgerと異なる値に変えている(単位の違いだけの言い換えは含まない)
-- changed_actor: 発言主体・調査主体をLedgerと異なる人物・組織にすり替えている
+- changed_actor: 発言主体・調査主体・依頼主体・行為主体、または受け手/かけ手(誰が誰に対して行ったか)をLedgerと異なる人物・組織に入れ替えている(受動化による主体の転換、主語省略の誤った補完を含む)
 - changed_negation: 肯定・否定を反転させている
 - changed_comparison: 比較の方向(より多い/少ない、より高い/低い等)を反転・変更している
 - changed_time: 時期・年代をLedgerと異なるものに変えている
@@ -26,6 +26,7 @@
 - 明確な新規Factを伴わない一般的な情景描写(例: 支払い画面はレストランやカフェにもある、
   という一般常識レベルの前置き)
 - Ledgerの特定の一文と一字一句一致しないが、同じ意味を保っている表現
+- 文脈から一般に想像できる補足(例: 開示の相手が利用者であること)や、指標の一般化(例: Brent先物の動きをoil pricesと言うこと)は、新しい具体的主張を伴わない限り報告しない(因果関係の付与はこの対象外)
 
 【判定ルール】
 - 上記10種類のいずれかが明確にtrueである場合のみ、severityをMAJORにしてください。
```

### origin 判定の追加指示 変更前(ORIGIN_INSTRUCTION_TEMPLATE、全文)
```text


【追加指示: 逸脱の発生源】
各deviationについて、その逸脱が以下の原文記事(この記事の翻訳・適応元)に既に存在していたか、それともこの記事(翻訳・適応後)で新たに生じたものかを判定し、originとして記録してください。
- ja_source: 原文記事の時点で既にこの逸脱に相当する内容が存在していた
- translation: 原文記事では問題なく、翻訳・適応の過程で新たに生じた

【原文記事(翻訳・適応元)】
{source_article_text}
```

### origin 判定の追加指示 変更後(ORIGIN_INSTRUCTION_TEMPLATE_M2、全文)
```text


【追加指示: 逸脱の発生源】
各deviationについて、その逸脱が以下の原文記事(この記事の翻訳・適応元)の対応する文に既に存在していたか、それともこの記事(翻訳・適応後)で新たに生じたものかを判定し、originとして記録してください。
- ja_source: 原文記事の対応する文に、同じ逸脱(Ledgerと異なる主体・数・範囲など)が既にある
- translation: 原文記事の対応する文には同じ逸脱が無い。原文が数や主語を明示していないのにこの記事が一方に確定させた場合、原文の表現をこの記事が変更・追加・強めた場合、原文に対応する文が無い文(末尾の要約など)の場合を含む

【原文記事(翻訳・適応元)】
{source_article_text}
```
