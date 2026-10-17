# Claude Code／Fableへの回答・指示
## Coffee S3試聴承認／「退屈と攻撃性」Production E2E開始

**管理ID：FAMILY-X-BOREDOM-AGGRESSION-PRODUCTION-E2E-01（継続）**

### 1. ユーザー正式判断

**① Coffee S3正式版：試聴PASS**

ユーザーがCoffee S3正式版を改めて試聴し、問題なしと判断した。

- S3の音声品質：ユーザー試聴PASS
- 追加のStyle調整・音声再生成：不要
- Family X Standard日本語解説の正式Style：S3を維持
- S3の`PRODUCTION_WIRED`判定：変更なし

試聴結果を既存の品質記録・Decision Log等へ反映し、Coffee S3の`USER_LISTENING_PENDING`をcloseすること。

**②「退屈と攻撃性」：制作費用上限180円を承認**

- 期待費用：約95円
- **承認上限：180円**
- 対象：ResearchからStandard／Advanced音声完成までの新規E2E制作
- 費用上限は当該記事限定。別Trialへ流用しない。

費用承認に関する判断待ち項目#106を更新・closeすること。

### 2. 新規記事の正式Production実走

S3のProduction Wiring完了を開始条件として確認済み。

既存の`FAMILY-X-BOREDOM-AGGRESSION-PRODUCTION-E2E-01`の実施方針に従い、新規記事「退屈と攻撃性」を制作すること。

正式Production経路で以下を実施する。

1. Research
2. Verified Fact Ledger
3. B3 Storyline
4. Writer W-1 R0→R1→R2
5. Advanced英語化・Standard調整
6. Key Phrase生成・選定・解説
7. Standard／Advanced音声生成
8. AUW品質判定
9. Assembly
10. 試聴ページ作成
11. 最終品質・費用・runtime evidenceの報告

旧記事原稿やTrial成果の完成品流用は禁止。既存の正式共通資産は利用可能。

テーマの事実関係はResearchで確認すること。特に心理学研究の相関・因果、実験条件、対象者、研究上の限界を正確に扱い、興味深さのために結論を誇張しない。

### 3. 正式Production仕様

**開始時点で承認・配線済みのFamily X正式仕様を使用すること。**

特に以下を確認する。

- Standard日本語Preview／Comment1〜4：**S3**
- B3／Writer R0〜R2：Sol、W-1
- Full Story：PD06
- KP英語音声：K2
- Standard KP日本語意味：P8
- Advanced KP英語解説：P7
- Advanced Preview：E1
- KP候補・選定：M2P0＋A方式
- In One Line：原則2文、必要時3文
- Standard Full Story：既存6%減速
- ASR／品質判定：Production配線済みAUW

既定profile `fx_20261017`が特別なCLI指定なしで適用されること。

retry／fallback／regenerationでも、正式仕様との整合を維持すること。

### 4. コスト記録

今回はコスト改善Trialを混ぜず、**現行Productionでの実測コストを記録することだけ**を求める。

Research／Ledgerの検索上限方式、Select-then-Verify方式等、未承認の改善仕様は使用しない。

工程別Breakdownを円単位の表で報告する。

最低限、Research・Ledger・B3・R0／R1／R2・英語化・Standard調整・KP・TTS・ASR・retry／fallback・総額を区別する。

Research／LedgerはWeb検索手数料とLLM費用も分離する。

実測値・推定値・未取得値を区別し、量産目標70円／記事セットとの差額も示すこと。

**今回は追加のコスト改善案の設計・Trial・実装を行わない。**

### 5. 費用・実行Gate

- **当該E2Eの累計上限：180円**
- 実行前に見積・当日累計・既存STOP条件を確認
- 日次1,000円のsoft budgetを維持
- コスト最適化Trialとは費用・run・成果物を分離
- 180円超過見込み時はSTOP
- Mandatory Human Review／品質Gateを省略しない

コスト最適化Trial等の並行作業と有料実行・Git操作が衝突しないようにする。

**commitを伴う作業は同時に1件のみ。**

### 6. 品質・Production検証

今回の目的は、最新Productionが新規記事をResearchから音声まで完走できるかの確認。

各段階で以下を記録する。

- 正式Production entrypoint
- actual model_id／routing
- Prompt／Style SHA
- 正式Style profileの適用
- Fact Lock・Risk Flagger／Review Queueの結果
- AUW／ASRの判定
- retry／fallback／Human Reviewの発生
- 工程別費用
- 正式成果物の生成状況

既存のMandatory STOPに到達した場合は正式運用どおり停止し、必要なユーザー確認を求めること。

**今回の費用承認は、途中の品質・Human Review Gateを一括解除するものではない。**

### 7. 対象外

- S3の追加Style調整
- Coffeeの再生成
- Research／Ledgerコスト改善方式のProduction適用
- 新しいWriter／TTS Prompt探索
- Family Z／Yの変更
- Family A／B／Cの開発
- 無関係なOpen Itemの棚卸し

新たな問題が生じても、独断で別のTrialや仕様変更を開始しないこと。

### 8. 報告・Closeout

最終報告は次の順で簡潔に提示する。

1. **正式Production E2Eは完走したか**
2. Standard／Advanced試聴ページURL
3. 記事品質・音声品質の確認結果
4. 承認済みStyle／Promptのruntime適用結果
5. 工程別費用Breakdown（円単位の表）
6. 総費用・180円上限との差
7. Production上の問題・未解決Blocking事項
8. ユーザー判断が本当に必要な事項

FableはClaude Codeの報告を鵜呑みにせず、CURRENT_SPEC・承認済み仕様・runtime evidence・実際の成果物・テスト結果と照合して独立判定すること。

記事完成後も、ユーザーによる試聴前に聴感品質をPASS扱いしない。

**Coffee S3は正式試聴PASSとしてcloseし、「退屈と攻撃性」の新規Production E2Eを開始すること。**
