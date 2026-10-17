# Claude Code／Fableへの正式指示
## Research／Fact Ledger コスト最適化Trial — Stage 1全体＋任意A

**管理ID：FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01（継続）**

### 1. ユーザー正式判断

**選択肢(b)＋任意Aを承認する。**

- Stage 1a：Coffee＋訪日客統計
- Stage 1b：Disney+値上げ、OpenAI著作権訴訟、FOMC・住宅ローン金利
- 任意A：故障注入によるFact誤り検出力の確認

**承認費用：期待約¥536、累計上限¥1,040。**

Stage 1a・1bは別日で実行し、既存の日次予算ルールを遵守すること。

任意B（B3追加Take）、任意C（Risk Flagger影響比較）、Stage 2条件付き再検証は、今回の承認範囲に含めない。

今回の承認は**Trial実施と費用の承認**であり、改善仕様の正式Production採用ではない。

### 2. 実施前確認

既存の設計・見積を正本として使用する。

- `TRIAL_DESIGN_02.md`
- `COST_ESTIMATE_02.md`
- `OPUS_REVIEW_A_01_VERBATIM.md`
- `PRE_ANALYSIS_SEARCH_CAP_01.md`

Opus条件Aレビューの指摘16件（Blocking 3／Major 7／Minor 6）が設計に反映されていることを確認する。

不要な設計やTrial範囲の拡大は行わない。

### 3. Trial実施内容

5記事それぞれで、以下の4方式を比較する。

| 方式 | 内容 |
|---|---|
| 従来方式 | 全Fact検証 → B3選定 |
| 案1 | Fact単位の検索上限3回 → B3選定 |
| 案2 | B3選定 → 選定Factだけ独立検証 |
| 案1＋案2 | B3選定 → 選定Factだけ検証（検索上限3回） |

保存済みResearch下書きを再利用し、新しいResearchは実行しない。

既存の従来方式のB3が旧モデルによる場合は、比較条件を揃えるため、承認済みの現行Sol Writer設定で基準を生成する。

既存成果物を変更せず、Trial専用領域に複製して比較すること。

### 4. 重要な検証条件

**案1**

- 3回上限は未検証の暫定値として扱う。
- Web検索ツール呼出単位で計測する。
- 2回／3回／5回の机上比較と、実行結果を区別する。
- VERIFIED Factの喪失と検索費用削減を両方評価する。

**案2**

選定FactがREJECTEDとなった場合は、機械的に削除して確定せず、B3に再選定させる。

- 不合格理由をB3へ返す
- 必要なら他のFactを選ぶ
- 新たな選定Factを独立検証する
- 検証済みFactの結果は再利用する
- 再選定はTrial上、最大2回
- 上限到達時は無理にB3を確定しない

AMBIGUOUSとREJECTEDを区別し、既存Fact Lockの安全条件を維持する。

### 5. 任意A：故障注入テスト

**任意Aの実施を正式承認する。**

意図的に誤ったFactをTrial専用データへ注入し、検証機構が誤りを検出できるか確認する。

目的は、案1・案2・組合せ方式によって、Factの誤り検出力が低下しないかを評価すること。

- Productionデータには注入しない
- 元のResearch下書き・Ledger・B3を変更しない
- 誤FactがVERIFIEDとして通過していないか確認する
- 検出漏れがあれば重大NGとして報告する

故障注入テストの結果を、通常記事における誤り検出率の保証として扱わない。

### 6. 実行順序

1. Trial専用harness実装
2. JPY0 dry-run（CP1）
3. Stage 1a：Coffee＋訪日客統計
4. 中間費用・品質Gate確認
5. Stage 1b：残り3記事
6. 任意A：故障注入テスト
7. 全結果の集計
8. Fable独立レビュー
9. ユーザー報告後STOP

Stage 1bへの進行は、設計書の既存条件（Stage 1a実測／見積比1.3以下等）を満たすこと。

条件を満たさない場合は、ユーザー判断を求めてSTOPする。

### 7. 費用管理

**今回の累計上限：¥1,040。**

- Stage 1a上限：¥493
- Stage 1b上限：¥493
- 任意A上限：¥54

期待額は合計¥536。

各Stageの上限と全体上限の両方を守ること。

Web検索手数料を含めた実費を計測する。

日次¥1,000のsoft budgetを維持し、必要に応じて実行日を分割する。

費用上限に近づいた場合は、無理に続きを実行せずSTOPする。

事前見積と実測費用の差が大きい場合は、原因を記録すること。

### 8. 評価・報告

各記事・各方式について、以下を表形式で報告する。

- Research／Ledger／B3の実測費用
- Web検索呼出回数
- Fact判定の変化
- B3で選ばれたFact
- 最終B3構成の差
- ストーリーの品質・一貫性
- 再選定の回数・追加費用
- 故障注入テストの結果
- 従来方式比の削減額・削減率

5記事合計だけでなく、**記事別に効果がどれだけ異なるか**を明確にすること。

削減額と品質差を分けて評価し、70円／記事セットの目標に対する実際の寄与を説明すること。

### 9. Production変更禁止

今回の作業はTrial限定。

- Production runner・Prompt・正式profileを変更しない
- retry／fallback／regenerationを変更しない
- 未承認の検索上限・Select-then-VerifyをProductionへ導入しない
- Family A／B／Cの開発を行わない
- 他のFamily X Production E2EにTrial仕様を混入させない
- 無関係な改善Trialを追加しない

commitを伴う作業は同時に1件のみとする。

### 10. Trial終了・PM Gate

Trial終了時、案1・案2・案1＋案2をそれぞれ以下に分類する。

- `REJECTED`
- `VALIDATED`
- `USER_DECISION_REQUIRED`

**VALIDATEDはProduction採用を意味しない。**

ユーザー承認なしに`APPROVED_FOR_PRODUCTION`へ変更しないこと。

新方式についてはProduction配線を行わず、結果を報告してSTOPする。

Fableは、実測ログ・Fact品質・B3品質・費用・Opusレビュー条件と照合して独立受入を行うこと。

最終報告では、**コスト削減の実力と品質への影響**を最初に示し、採否判断に必要な情報を簡潔に整理すること。
