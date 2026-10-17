# Claude Code／Fableへの指示
## Family Z Production完成・Cross-Family共通仕様の配線管理

### 1. 管理対象・目的

- Family Z：`FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01` および関連継続管理ID
- Cross-Family：PM_GOVERNANCEへの上位ルール追加（既存管理体系に従って記録）

**目的：**
1. Family Z「走れメロス」を、ユーザー承認済み最新仕様に従って正式Production E2Eとして完成させる。
2. Family Xで正式採用した共通音声仕様をFamily Zにも適用する。
3. Source Reference ContractをFamily Zの正式KP経路へ反映する。
4. 今後、共通仕様のFamily間配線漏れを防止する。

今回の到達目標は、対象仕様の`PRODUCTION_WIRED`および「走れメロス」の正式Production E2E完走である。

### 2. ユーザー正式判断

以下は今回のユーザー決定として扱う。

**A. Family Z構成・Writer**

- Story本文：3分割
- Comment：3つ
- In One Line／Comment 4：設けない
- Writer：Sol R0→R1→R2
- Advancedを自然な英語で作成し、そこからStandardへ難易度調整
- Preview／Comment 1の生成順序は**現行方式を維持**。A/B Trialの新方式を採用しない。
- 今回問題となった程度の展開の先取りは許容し、Preview改善の追加Trialは行わない。

**B. Family Z音声**

Family Xで正式採用された最新の共通音声仕様をFamily Zにも適用する。

| Role | Family Zへ適用する仕様 |
|---|---|
| Full Story Narrator | PD06（旧N01から変更） |
| Standard日本語Preview／Comment | S3（旧R2から変更） |
| Advanced英語Preview | E1 |
| Key Phrase英語 | K2 |
| Standard KP日本語意味 | P8-KP |
| Advanced KP英語解説 | P7 |
| Standard英語Full Story | 既存6%減速を維持 |
| ASR・音声品質検証 | 承認済みAUW共通基盤 |

**Family Z固有仕様：Dialogue別Voice**

- Fictionの登場人物のセリフは、事前に設定した別Voiceで読み上げる。
- NarratorのPD06を登場人物のセリフへ一律適用しない。
- 既存のspeaker assignment・Dialogue Style・Voice設定を尊重する。
- NarratorとDialogueの切替、speakerの誤割当、音声結合を確認する。

**C. KP**

- Family XのKP候補供給M2P0およびKP選定優先順位A方式は、Family Zでは品質悪化のTrial結果に基づき適用しない。既存のFamily Z方式を維持する。
- **Source Reference ContractはFamily Zへ正式適用する。**
- KP選定結果と元英文の対応を、候補ID等によって決定論的に保証する。
- Source Reference Contract導入を理由に、KP選定方針自体をFamily X方式へ変更しない。

**D. Risk Flagger**

Risk FlaggerはFamily XのNews／Fact Ledger固有仕様として扱う。

今回のFamily Zへの配線対象外とし、不要な仕組みを追加しない。

### 3. 「走れメロス」の再利用方針

**既存成果を最大限再利用し、原稿から無条件に作り直さない。**

基本的な再利用対象：

- Advanced／Standard本文
- Story 3分割構成
- Preview／Comment原稿
- Key Phrase選定結果
- その他、現行仕様に適合する検証済み成果

最初に、既存成果物の内容・SHA・承認状態・Production正式経路からの利用可否を確認する。

**「新仕様との整合確認」は、既存成果物が承認済み仕様と矛盾していないか調べるという意味であり、再生成を前提としない。**

KPについては、既存の選定結果が元英文と一致するかを確認する。既存成果を安全に正式経路へ引き継げる場合は、不必要な再選定を行わない。

一方、音声Styleが変更されるRoleは正式Production経路で再生成し、検証する。

過去のHuman Review承認、ASR結果、wav、テキスト等を無条件に新runへ引き継がない。再利用には正式な検証・provenance・Gateを満たすこと。

### 4. Production Wiringの受入条件

対象仕様ごとに以下を確認する。

1. 正式Production初回経路に配線済み
2. retry／fallback／regeneration／resumeとの整合
3. DEV／Trial専用scriptのみの実装になっていない
4. 正式Productionでruntime発火を確認
5. actual model_id／routing／TTS Style SHA／Voice等が承認内容と一致
6. 必要なRegression／Validator／integration testがPASS
7. AUW・ASR・6%減速・Voice assignment・AssemblyがPASS
8. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMSを更新
9. 必要なcommit／push／mergeを確認
10. ユーザー承認仕様と実際のProduction動作が一致

**全項目を満たすまで`PRODUCTION_WIRED`にしない。**

Production側のPromptやretryに新しい仕様名を追加する場合は、正式な初回経路・承認済み仕様への参照が存在するか、Dangling Reference Checkも実施する。

### 5. Cross-Family同時Production配線原則【上位ルール】

以下を、個別Familyより上位の恒久的な開発・PM運用ルールとして正式記録すること。

**基本原則：Family固有ではない共通仕様は、あるFamilyでProduction配線する際、原則として他の対象Familyにも同時に配線する。**

対象：

- Family X
- Family Z
- 将来のFamily Y

運用：

1. 仕様変更時に、必ず「共通仕様／Family固有仕様」を分類する。
2. 共通仕様としてユーザー承認されたものは、対象Familyごとに`APPROVED_FOR_PRODUCTION`として追跡する。
3. あるFamilyでProduction配線する際、他の対象Familyでも原則同時に配線・テスト・runtime確認を行う。
4. Family別に`PRODUCTION_WIRED`の成立を判定する。1つのFamilyでの成功を他Familyの証拠として代用しない。
5. 同時配線が技術的・運用上困難な場合は、理由・未完了事項・解消予定をOpen Itemに記録し、無条件にタスクをcloseしない。
6. Family固有仕様およびユーザーが明示的に不採用とした仕様は例外。
7. 新規Family（将来のY等）をProduction化する際は、既存の共通承認仕様を最初から配線対象に含める。
8. 今後の仕様変更・Production Wiring・新規Family記事E2Eの開始／終了チェックに、この原則を組み込む。

**「Family Xで採用したがZには未反映」「Zで改善したがX／Yには未反映」という状態の放置を防止することが目的。**

今回決定した共通仕様の対象範囲をCURRENT_SPEC・DECISION_LOGへ明記し、配線追跡をOPEN_ITEMSで管理する。

### 6. 実施順序・費用管理

1. 既存の承認・Production状態・未解決Open Item・既存runをread-only確認
2. Family Zの現行構成と承認済み仕様との差分を確定
3. 必要なProduction配線を実装
4. 必要最小限の新規有料音声生成
5. 正式E2E・QA・runtime検証
6. 試聴ページ作成・費用集計
7. Fable独立受入判定
8. SSOT・Decision Log・Open Items・Git反映結果の最終確認

並列化・キャッシュ・既存資産再利用により費用と時間を抑える。

**重要：過去の¥300承認が今回の追加再生成までカバーするか、既存累計・残枠を先に照合すること。**

費用上限や対象範囲が不明な状態で新しい有料実行を開始しない。追加費用承認が必要なら、その時点でSTOPして金額と理由を報告する。

### 7. STOP条件

以下の場合はSTOPする。

- 承認済み仕様と実装が矛盾する
- Family Z固有仕様が共通仕様の導入で破壊される
- 未承認の新機能・仕様変更が必要になる
- 正式Production経路で期待したStyle／Voice／KP contractが発火しない
- 費用上限に達する、または超過が予見される
- Human Review等、ユーザー承認必須Gateが発火する
- 必須テスト・Validatorが不合格
- Production Wiring Checklistを満たせない

新たなTrial・Prompt探索・品質基準の緩和を独断で開始しない。

### 8. 最終報告

ユーザーには以下を簡潔に報告する。

1. Family Z「走れメロス」のProduction E2E完走可否
2. Standard／Advanced試聴URL
3. Family X共通音声仕様のFamily Z適用一覧とruntime証拠
4. Dialogue別Voiceの適用結果
5. Source Reference ContractのProduction配線状況
6. 既存成果の再利用範囲と新規生成範囲
7. 実測費用・工程別内訳
8. Regression／ASR／Assemblyの結果
9. 各仕様の`PRODUCTION_WIRED`判定
10. 未解決Open Item・ユーザー判断が必要な事項

FableはClaude Codeの「完了」報告をそのまま受け入れず、CURRENT_SPEC・ユーザー承認内容・Production実経路・runtime evidenceと照合して判定すること。

**「走れメロス」の音声を生成しただけで、Family Z全体の`PRODUCTION_WIRED`と判断しないこと。**

なお、既存の「走れメロス」最終試聴・受入保留については、今回のProduction仕様整備とは区別する。新しい正式試聴ページが完成した段階で結果を提示し、ユーザー判断を求めること。

---

**今回の中心方針は、既存成果の最大限再利用、Family X共通音声仕様のFamily Z正式配線、そしてCross-Family配線漏れの恒久的防止である。**
