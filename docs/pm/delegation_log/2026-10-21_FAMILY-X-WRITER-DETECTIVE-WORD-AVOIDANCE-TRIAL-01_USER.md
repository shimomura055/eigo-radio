# ユーザー指示原文(2026-10-21)
管理ID: FAMILY-X-WRITER-DETECTIVE-WORD-AVOIDANCE-TRIAL-01(§2〜§9) / FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02 委任_05(§1)

# 中東記事 最終Closeout ＋ Writer「Detective」表現改善Trial

## 1. ユーザー正式判断：中東記事を受入

中東記事 E2E-02について、**Standard／Advanced両方のユーザー試聴PASSを正式確定する。**

対象：
https://shimomura055.github.io/eigo-radio/user_test/middle_east_yemen_saudi_e2e_02/index.html

- 音声・記事品質ともに今回の完成版を承認。
- `USER_LISTENING_PENDING` を解消する。
- 既存成果物の再生成・再組立は不要。
- OPEN-416、DECISION_LOG、REGISTER、REPORT_LEDGER等を必要十分に更新し、正式Closeoutする。
- FableがCloseoutを独立確認する。

**今回のDetective表現は中東記事の受入を妨げない。** 新たな改善Trialとして切り分ける。

## 2. 新Trialの目的

**目的：ニュース記事のエンターテインメント性を損なわず、Writerが「Detective」という単語を使用しないようにする。**

現状の課題：

Writerにエンターテインメント性を高めるよう指示すると、ニュースを探偵・捜査になぞらえる表現が出現しやすい。

ただし、ユーザーは謎解き的な展開や構成自体を否定していない。

今回、禁止したい対象は**Detectiveという単語**であり、ニュースの構成上の自由度を不必要に狭めないことが重要。

### TrialのStatus

- 新Prompt候補：`TRIAL`
- Trial成功時の到達上限：`VALIDATED`
- Production採用：ユーザーの別途明示承認が必要
- 正式Production Writerへの配線：今回の対象外

## 3. 比較条件

中東記事E2E-02を題材とする。

既存の承認済みResearch／Fact Ledger／B3入力とWriterの現行Prompt・モデル・生成条件を再利用し、**追加指示だけを変える**。

Research、Fact抽出、B3選定、TTS、Assemblyは再実行しない。

既存完成原稿はBaselineとして保存し、変更しない。

### Pattern A：単語のみ禁止

Writerへの追加指示：

> Do not use the word "detective" anywhere in the article.

検証目的：
単純な禁止だけで指定単語を排除できるか。

### Pattern B：単語禁止＋構成の自由を明示

Writerへの追加指示：

> Do not use the word "detective" anywhere in the article. However, this restriction does not prohibit a mystery-like narrative structure or a detective-like progression of the news story, as long as it remains faithful to the verified facts.

検証目的：
Detectiveという単語だけを禁止し、ニュース展開・構成の自由度と面白さを維持できるか。

### Pattern C：単語禁止＋面白さの作り方を誘導

Writerへの追加指示：

> Do not use the word "detective" anywhere in the article. Create an engaging news story through the actual events, surprising developments, decisions, consequences, and connections between verified facts. Avoid relying on a detective metaphor to make the story entertaining. A mystery-like narrative structure is acceptable when it naturally follows the facts.

検証目的：
Detectiveという比喩に頼らず、事実そのものから面白さを引き出せるか。

**注意：Pattern Cでも、探偵的な構成そのものは禁止しない。**

## 4. Trial設計

### 基本方針

1. BaselineとA／B／Cを同一条件で比較する。
2. 各Patternは原則として独立した生成とする。
3. 現行WriterのEntertainment Revisionなど、既存の生成・改稿工程を維持する。
4. 各工程で追加指示が有効に作用しているか確認する。
5. 特定Patternだけ別のモデルや改稿工程を使わない。
6. Trial専用の成果物として保存し、Productionへ影響させない。

比較可能性を確保しながら、必要な生成回数・費用を最小化する。

### 比較対象

- Baseline：既存完成記事
- Pattern A
- Pattern B
- Pattern C

各Patternについて、まず1セットの原稿を生成する。

結果が明確であれば追加生成せず終了する。効果が不明瞭で、承認済みTrial予算内で追加比較する価値が高い場合に限り、必要最小限の再現確認を行う。

追加のPrompt候補D／E等を独断で増やさない。

## 5. 品質評価

以下の4項目を比較する。

### ① Detectiveの排除

- `detective` の大文字・小文字違いを含め、本文中の出現が0件であること。
- 完成記事全体を確認する。
- Preview／Comment等が今回のWriter評価範囲に含まれる場合は、本文と区別して結果を報告する。
- 単純な表記置換で済ませず、Writerが自然な文章を生成できるかを見る。

### ② エンターテインメント性

- 冒頭の引き
- 展開の自然さ
- 意外性・興味を引く構成
- 読み進めたくなる面白さ
- 不自然な比喩や演出の有無

**単語を消せたことだけでTrial成功としない。**

### ③ 事実・ニュース品質

- Ledger外の事実追加がない。
- 攻撃主体（フーシ派）の記述が維持されている。
- 「誰の発表・主張か」という帰属が正確である。
- 原因・動機を根拠なしに創作しない。
- 時系列・因果関係・人物関係に新たな誤りがない。

### ④ QCD

- Pattern別のLLM呼出回数
- 使用モデル
- 実費
- 所要時間
- retry／再生成の有無
- Production適用時の量産単価への影響

既存工程に追加API呼出を必要としないPrompt変更であれば、その点を明確にする。

## 6. Fable独立評価

Fableは単にDetective出現件数を見るのではなく、次の観点で評価する。

- A／B／Cのどれが今回のユーザー目的に最も忠実か。
- Detective禁止によって、面白さ・自然さが低下していないか。
- `investigator` など類似表現への不自然な言い換えが起きていないか。
- 類似表現の使用を理由に、今回の未承認の禁止語リストを新設していないか。
- 中東記事固有の効果なのか、他のニュースにも適用できそうか。
- 追加Promptの長さ・複雑さに見合う効果があるか。

必要十分な品質に達した時点で比較を終了する。無益な反復をしない。

## 7. 予算・STOP条件

- 日次開発予算1,000円（JST）を遵守する。
- Trialの個別費用枠は既存承認を確認し、その範囲内で実行する。未承認の費用枠を新設しない。
- 既存入力・出力を再利用し、Researchや音声生成に費用をかけない。
- 品質・費用・技術上の理由がなければ独立作業を並列化する。
- 既存Production経路は変更しない。

以下の場合はSTOPする。

- ユーザー承認のない仕様変更が必要
- 個別承認予算の超過見込み
- 重大な事実改変・品質問題を承認範囲内で解決できない
- 明示的なSTOP条件に抵触

既存仕様・予算内の技術的不具合は自律的に解決する。

## 8. 最終報告・Trial Closeout

以下を報告する。

1. **A／B／Cの比較結果とFable推奨Pattern**
2. 各Patternの原稿を確認できる比較ページまたはリンク
3. Detective出現件数
4. エンターテインメント性・自然さの比較
5. 事実整合性・攻撃主体・帰属の検査結果
6. 使用モデル・実費・所要時間・量産原価影響
7. Trial Status（REJECTED／VALIDATED／USER_DECISION_REQUIRED）
8. Production採用に必要なユーザー判断

A／B／Cの原稿は、ユーザーが内容を比較して評価できる形で提示する。

**Fableの推奨があっても、Production採用は自動決定しない。**

Trial完了後、ユーザーが正式採用を判断するまでProduction WriterのPrompt・コード・実行経路を変更しない。

---

## 9. PM上の最重要事項

今回の問題は「探偵的な構成をなくしたい」ではない。

**「Detectiveという単語を使わずに、これまでのニュース記事の面白さを維持したい」ことが目的である。**

- 過剰に禁止範囲を広げない。
- 元のニュースの事実・品質を守る。
- 中東記事の完成承認は維持する。
- 今回のTrial成功を正式採用と混同しない。

既存仕様とQCDを守り、最小限の比較で結論を得ること。
