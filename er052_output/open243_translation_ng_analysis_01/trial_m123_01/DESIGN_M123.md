# DESIGN_M123: OPEN-243 M1〜M3 Trial 実装設計メモ(委任_03、2026-10-08)

Status: MEASURED(Trial)。Production変更なし(全てフラグ既定OFF、VALIDATED/APPROVED_FOR_PRODUCTION未宣言)。CURRENT_SPEC.md 無変更。承認済みChecker構成 `OPEN233_APPROVED_FLOW_SWITCHES` の値は無変更(Trial用スイッチは別名・環境変数のみ)。
ベースcommit: 45b3fa420c02b22ce7a96ff7c5dedaed6a6e4766(検証実行時は未commitの作業ツリー。実行時の対象ファイルsha256[先頭16桁]は末尾「固定SHA」)。

## 1. フラグ一覧(全て既定OFF)

| フラグ | 種別 | 効果 | 変更ファイル |
|---|---|---|---|
| `OPEN243_M1=1` | 環境変数 | (a)要約「In one line」の生成入力へ日本語R2本文とLedgerを追加。(b)初回EN検査で「MAJORの全件が要約の文を指し本文には無い」場合、本文は作り直さず要約だけを最大2回再生成(各回: 前回指摘[must-fix]付きで再生成→prior_issues付きEN検査。COMPLIANTかつ前回指摘が全解消で成功、それ以外はSTOP)。本文側にもMAJORがある・ja_source MAJOR・引用が短すぎて位置判定不能の場合は従来どおり。対象=Advanced(Family X)枝のみ(Standard/A2枝は未実装) | `er003_v1_n3_01_advanced_adaptation_generate.py`、`er012_e_family_entertainment_two_level_runner_01.py` |
| `OPEN243_M2=1` | 環境変数 | `run_deviation_check()` のprompt文言のみ差し替え: D1 changed_actorの説明拡張、ユーザー回答反映の1項目、D3 origin判定文の修正。severity規則(判定ルール節)・10フラグ・JSON schemaは不変 | `er003_v1_en_direct_vfl_01_generate.py` |
| `OPEN233_RECLASSIFY_PROTECT_FLAGS=changed_actor` | 環境変数(承認構成に含めない) | 再分類で、Stage 1のmodel候補のうち指定フラグtrueのものを再分類対象にせず(除外されず)CANDIDATEのままStage 2へ。未知のフラグ名はValueError。カンマ区切りで複数可 | `er052_open233_stage1_reclassify_01.py` |
| `OPEN243_G3_TELEMETRY_PATH=<jsonl>` | 環境変数 | G3(観測のみ、API費用0): (i)EN検査のtranslation起源MINORを1件1行で追記(runner)、(ii)再分類で除外されたStage 1フラグ付き候補を追記(reclassify。infoに`g3_n_excluded_flagged`) | runner、reclassify |

フラグ未設定時の確認: prompt文字列は従来と完全同一(単体テストで逐語比較)、reclassify/runnerの戻り値のキー集合も不変。回帰テストはフラグ未設定でPASS(`regression/flags_off_final.log`)。

## 2. M1 設計

- `generate_family_x_in_one_line(client, title, body, *, model=None, ja_text=None, ledger_text=None, must_fix=None)`: 追加3引数が全て未指定なら従来promptと完全同一(戻り値に`prompt`キーも足さない)。指定時は `FAMILY_X_IN_ONE_LINE_INSTRUCTION_TEMPLATE_M1`(下記P1)に[Japanese source article]と[Verified Fact Ledger]を追加し、must_fixがあれば既存 `build_must_fix_block()`(無変更)の出力を末尾に付ける。
- 変更は「要件1行」+「入力欄2つ」+(再生成時のみ)既存のmust-fixブロック。禁止事項の列挙は増やしていない。使用model・developer message(FAMILY_X_TRANSLATOR_DEVELOPER)・語数ガイドは不変。
- runner: `open243_majors_only_in_summary()`(位置判定: 引用を英数字のみに正規化し、本文に含まれず要約に含まれる/含むときだけTrue。先頭の「In one line:」ラベルは除去。8文字未満はFalse=従来経路)、`open243_m1_summary_only_retry()`(要約だけ再生成、最大2回、検査→STOP判定)。要約だけ再生成した場合は `advanced_attempt2.json`(,3)を保存。
- 既存のretry/fallback機構との整合: 本文MAJOR時の「must-fix付き全体再生成1回」・ja_source→JA再確認STOP・段落数retry・「再生成後もMAJORならSTOP」は変更なし。M1は「要約のみMAJOR」の場合だけ、全体再生成1回の代わりに要約再生成最大2回を行い、それでも未解消ならSTOP(上限を回避・無効化していない)。

## 3. M2 設計(D1・D3・校正)

- D1: changed_actor の説明文のみ変更(severity規則・フラグ集合は不変)。
- D3: 現状の origin 判定は決定論コードではなく、`ORIGIN_INSTRUCTION_TEMPLATE`(Checkerへの追加質問)に任されている。現状文言は「ja_source: 原文記事の時点で既にこの逸脱に相当する内容が存在していた / translation: 原文記事では問題なく、翻訳・適応の過程で新たに生じた」。この「相当する内容」が緩く、台帳の「副社長」に対しJAが「幹部」(役職の一般化)と書いていると、ENの "executives"(複数化)も「JAに既に相当する逸脱がある」としてja_sourceに分類され得る(ANALYSIS_01の「幹部→executives」3事象)。差分: 「対応する原文の文に**同じ**逸脱(Ledgerと異なる主体・数・範囲など)がある」ときだけja_source、原文が数・主語を明示していないのに英語が一方に確定させた場合・原文を変更/追加/強めた場合・原文に対応する文が無い文(末尾要約など)はtranslation、と明記。
- 校正(ユーザー回答): 「文脈から一般に想像できる補足(例: 開示の相手が利用者)」「指標の一般化(例: Brent先物→oil prices)」は新しい具体的主張を伴わない限り報告しない旨を、許容範囲リストに1項目追加(因果関係の付与は対象外と明記=ユーザー注記「潜在的リスク」を反映)。
- 適用: `run_deviation_check()` 内で hook_aware 版にも効く(`apply_open243_m2_to_prompt_template`)。置換元の文言が無ければAssertionError。

## 4. M3 設計

- `claims_for_candidates(cands, protected_claims=(), protect_flags=None)`: protect_flags未指定=環境変数。指定フラグがtrueの model 候補(同一keyのいずれか)を「保護key」にし、再分類callの対象から外す(=除外判定が付かず、後段で `kept` に残る)。`reclassify_candidates` は M3 ON 時のみ info に `protect_flags`・`n_protected_by_flags` を追加。
- 既存の「前回指摘と同文の保護(is_protected)」と同じ仕組み(fail-closed側)に載せた。再分類call・予算・未返却時のCANDIDATE維持は不変。

## 5. プロンプト変更前後の全文(自動生成: _gen_design_prompts.py)

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


## 6. 検証ハーネス(Trial専用、Productionから呼ばれない)

- `v1_summary_regen.py`(V1)、`v2_en_check.py`(V2)、`v3_reclassify_replay.py`(V3)、`analyze_v1/2/3.py`、`_common.py`(費用台帳 `spend_ledger.jsonl`、予算上限¥60のfail-closed)。
- V3 は `run_instance`(承認構成のまま、`apply_open233_approved_flow_switches()` と `assert_open233_approved_flow_switches()` を通す)に、保存済み Stage 1 候補(`stage1_coverage.per_route.{r3,r5}.candidates`=合流前)を注入。再分類(実call)→合流→Stage 2→第2意見まで本番コードで実行し、cycle 1 の Stage 2 結果確定時点(`_wobble_observe` 呼び出し時)で打ち切る。Rewrite以降は実行しない。
- 実行コマンド:
  - V1: `.venv/Scripts/python.exe er052_output/open243_translation_ng_analysis_01/trial_m123_01/v1_summary_regen.py --phase A` / `--phase B`(phase BのみOPEN243_M2=1をプロセス内で設定)
  - V2: `... v2_en_check.py --arm new --scope all --threads 3` / `--arm old --scope tolerance|posevents|sample_rest --threads 3`(`--arm new`のみOPEN243_M2=1を設定)
  - V3: `... v3_reclassify_replay.py --proc P1..P6 --runs <T01..T10> --budget-jpy 12 [--tag _rerun2] --yes-run-paid`(OPEN233_RECLASSIFY_PROTECT_FLAGS=changed_actor を内部で設定)
  - 集計: `analyze_v1.py`・`analyze_v2.py`・`analyze_v3.py`

## 7. 固定SHA(検証実行時の作業ツリー、sha256先頭16桁)

ベースcommit 45b3fa420c02b22ce7a96ff7c5dedaed6a6e4766 + 未commitの作業ツリー(commitは result.md 記載)。改行コードはLF換算ではなくファイルバイト列のsha256。

| ファイル | sha256[:16] |
|---|---|
| `er003_v1_en_direct_vfl_01_generate.py` | fb6622f7a1ac2d21 |
| `er003_v1_n3_01_advanced_adaptation_generate.py` | b7bfb8df1fa5df1a |
| `er012_e_family_entertainment_two_level_runner_01.py` | a2ac3d1f9cbb015b |
| `er052_open233_stage1_reclassify_01.py` | 33762f70984b4034 |
| `er052_open243_m123_trial_test_01.py` | 722f47ad209ebdd1 |
| `er052_output/open243_translation_ng_analysis_01/trial_m123_01/_common.py` | 0bfe8cae49186e2b |
| `er052_output/open243_translation_ng_analysis_01/trial_m123_01/v1_summary_regen.py` | 1467b6cddd522588 |
| `er052_output/open243_translation_ng_analysis_01/trial_m123_01/v2_en_check.py` | 6e23df4df3e02b55 |
| `er052_output/open243_translation_ng_analysis_01/trial_m123_01/v3_reclassify_replay.py` | a52fc595e6d1b54f |
| `er052_output/open243_translation_ng_analysis_01/trial_m123_01/analyze_v1.py` | 5cb5aed8d7cb75bf |
| `er052_output/open243_translation_ng_analysis_01/trial_m123_01/analyze_v2.py` | b6854421aff351d5 |
| `er052_output/open243_translation_ng_analysis_01/trial_m123_01/analyze_v3.py` | e50a1440440f1b1a |
| `er052_output/open243_translation_ng_analysis_01/trial_m123_01/_gen_design_prompts.py` | 55cf35b7c6d17f81 |
