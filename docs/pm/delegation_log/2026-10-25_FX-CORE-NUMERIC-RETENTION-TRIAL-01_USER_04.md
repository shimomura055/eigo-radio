# Claude Codeへの指示｜Family X 中核数値保持方式 Production正式採用・配線

## 1. ユーザー正式承認

Family X「中核数値保持方式」（Trial v4）について、ユーザーが**Production正式採用を承認**した。

- 対象：Family X（Standard／Advanced）
- Status：**APPROVED_FOR_PRODUCTION**
- 目標：**PRODUCTION_WIRED**
- Family Y／Zへの展開は今回の対象外
- 承認済みTrial方式を基本とし、品質基準や仕様を独断で変更しない

## 2. 採用する方式

B3が決定した記事の切り口に基づいて「読者が聞くべき重要数値」を選定し、その数値を後続工程で保持する。

重要な原則：

1. 数値は記事の切り口に対する必要性で判断する。記事ごとに固定しない。
2. 選定した中核数値は、R0→R1→R2→英語Standard／Advancedまで保持する。
3. 不要な数値の混入を防ぎ、数値の羅列による文章品質・エンターテインメント性の低下を避ける。
4. **既存の承認済み「数字の丸め」仕様を維持する。** 中核数値保持と矛盾させず、不要な桁数を復活させない。
5. 新たな事実・数値を創作しない。

TrialでVALIDATEDとなったv4を採用基準とする。検証済みの判定ロジックや境界条件を省略しない。

## 3. 実装前確認

CURRENT_SPEC、DECISION_LOG、OPEN_ITEMS、Trial結果、既存Production経路を照合する。

特に以下を確認する。

- Opus条件Cレビューの結果と未解決指摘
- 半導体記事で見られた、不適切な見通し数値の初回選定傾向
- 既存の数値丸め・数値保持・Fact整合性検査との関係
- B3再実行条件、Writer再生成、retry／fallback／resumeとの整合
- DEV／Trial専用処理と正式Production処理の相違

既存機構を最大限利用し、検査の重複や不要なLLM呼出を増やさない。

Opusレビューに重大な未解決事項がある場合は、承認済み仕様内で解決する。仕様変更が必要ならUSER_DECISION_REQUIREDとして報告する。

## 4. Production Wiring

正式Production初回経路に、承認された中核数値保持方式を配線する。

以下を満たすこと。

- Family XのStandard／Advanced双方に適用
- B3から最終英語原稿までの保持
- retry／fallback／regeneration／resumeでも仕様を維持
- 既存の数字丸め仕様との整合
- 既存のFact・文章品質・数値検査との整合
- DEV限定の実装や設定変更で終わらせない
- 不要になった旧処理・重複検査を整理する

## 5. 検証・受入条件

Trialの成功だけでProduction配線完了としない。

正式Production経路でruntime検証を行い、以下を確認する。

1. B3が記事の切り口に沿って中核数値を選定している。
2. R0／R1／R2／Standard／Advancedまで中核数値が保持される。
3. 不要数値の混入・数値創作がない。
4. 承認済みの数字丸め仕様が正常に機能する。
5. retry／fallback等の後続経路でも同じ品質を維持する。
6. 文章の自然さ・エンターテインメント性が損なわれない。
7. 必須Regression／Validator／Integration TestがPASSする。

Trialで確認した4記事型の知見を回帰検証に活用する。不要な有料Trialを繰り返さず、既存証跡と無料テストを最大限再利用する。

正式runtime evidence、実際のモデル・Prompt・routing、テスト結果を記録する。

## 6. QCD

優先順位は **品質＞完成速度＞量産単価≫開発費**。

- Trialで確認された品質水準を守る。
- 不要な追加改善・日付分割・待機を行わない。
- 独立作業は並列化し、最速で完成させる。
- 量産単価の増分はTrial推定で約4円／記事。これを基準に実測・評価する。
- 70円／記事セットの目標を意識し、品質を維持した原価低減を図る。
- 既存承認予算内で自律的に不具合を修正・検証する。

## 7. 完了条件・報告

以下をすべて確認した時点で **PRODUCTION_WIRED** とする。

- 正式Production経路への配線
- Standard／Advancedの正式runtime検証
- retry／fallback等との整合
- 必須テストPASS
- 承認内容と実動作の一致
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS更新
- 必要なGit commit／push
- 未処理の判断待ち・Dangling Referenceがないこと

最後に、Fableの独立受入評価を実施する。

**最終報告は以下を簡潔に示すこと。**

- Production Wiringの完了Status
- 中核数値保持・数字丸めのruntime evidence
- 回帰テスト結果
- 制作時間・量産単価への影響
- 残存リスク・Open Item
- Git／SSOT反映状況

承認済み範囲の不具合は自律的に解決し、技術上の軽微な判断をユーザーに求めない。

未承認の仕様変更、重大な品質リスク、予算超過が必要な場合のみSTOPして報告する。

**必要十分な品質を満たしたら、それ以上の磨き込みをせず速やかに完了すること。**
