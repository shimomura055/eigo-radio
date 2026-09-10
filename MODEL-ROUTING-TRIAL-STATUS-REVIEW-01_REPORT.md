# MODEL-ROUTING-TRIAL-STATUS-REVIEW-01 — Opus/Sonnet/Haikuモデルルーティング実績レビュー

管理ID: `MODEL-ROUTING-TRIAL-STATUS-REVIEW-01`
性質: 読み取り専用の分析タスク(コード・Prompt・SSOT無変更、Git操作なし、API呼び出しなし、実測費用¥0)
参照SSOT: `docs/pm/MODEL_ROUTING_TRIAL_LOG.md`(以下「LOG」)、`docs/pm/PM_GOVERNANCE.md`(以下「GOV」)、`OPEN_ITEMS.md`

## エグゼクティブサマリー

1. Trial開始(2026-09-09)後の委任84件(LOG 205〜289行)のモデル内訳はSonnet 78件(92.9%)・Opus 4件(4.8%)・Haiku 2件(2.4%)。Sonnet 78件のうち約40件は「SSOT精密編集+Git操作」を伴うcloseout consolidationで、L0(Haiku)定義(SSOT編集なし・Git操作なし)に構造上不適格なため、これ自体は誤ルーティングとは言えない。
2. Opus投入4件は4件とも新しい示唆(事実誤り・因果推論の誤り・未検出構造欠陥)を検出しており、追跡可能な範囲で的中率は高い(LOG 211/238/249/285行)。ただしN=4であり一般化はLOG自身が禁じている(LOG 4行目・107〜116行)。
3. Haikuは2件のみ(LOG 248・251行)。うち1件(retry log集計)はNG定義の不一致でSonnetの追加照合が発生し(Haiku起因の再作業)、もう1件(比較artifact生成)は再作業ゼロだった。
4. Household一本化設計・3V wiring影響分析・Discovery仕様reconcile分析はSonnetのみで実施されOpusレビューを経ていない(LOG該当行に「Opus不要/見送り」の理由記載あり、後述3節)。
5. 正式Closeout Trigger(LOG 78〜87行、6条件)はHaiku 5件以上・モデル別サンプル非偏在の2条件が未達であり、Closeout判定はできない段階。
6. 中間レビューTrigger(LOG 67〜76行)は開始直後に2回到達・記録済み(LOG 122〜123行)だが、その後Opus HIGH案件が2件→4件に増え、委任数も7件→84件に増えているにもかかわらず「### 実施記録」表(LOG 118〜124行)は2件のまま更新されていない。
7. Haiku専用Agent定義(`.claude/agents/haiku-worker.md`)は現状存在しない(`.claude/agents/`には`opus-consultant.md`・`sandwich-pm.md`・`sonnet-worker.md`のみ確認、`sonnet-worker.md`のfrontmatterは`model: sonnet`固定)。LOG上「Haiku」と記録された2件がどの起動経路でHaikuモデルを使ったかは、現行Agent定義だけでは説明できない。
8. コスト影響は案件ごとに方向性が異なる(cost-saving/cost-neutral/cost-increasing)。Opus介入は総じてcost-neutral〜cost-saving方向(追加API費用¥0のレビューで手戻りを未然回避した可能性が高い)、一方でOpus未投入のHousehold一本化はTrial累積費用(¥100.5+¥68.76+¥3.31+¥2.6等)を重ねた末に因果未確定のまま条件付き非推奨となっており、事後的にはcost-increasing方向のリスクが顕在化している。
9. 進行中4案件(Discovery Trial-11/News Trial-12/3V wiring Phase1/Phase2・2V比較記事N=1)は工程別ルーティング表(5節)を提示。設計・優先順位付け・N小データの解釈にOpusレビューを検討する価値があるが、いずれも現状Fableの判断待ち。
10. 結論: Trialは「観測継続中」であり、正式採用(モデル選定ルールの恒久化)には未達。

---

## 1. 実績集計

**期間**: Trial開始 2026-09-09(`PM-MODEL-ROUTING-TRIAL-SETUP-01`の次の委任からカウント、LOG 63〜65行)〜2026-09-10(直近記録行`PM-CLOSEOUT-CONSOLIDATION-66`、LOG 289行)。

### Trial導入後(LOG 205〜289行、84件)

| モデル | 件数 | 割合 |
|---|---|---|
| Sonnet | 78 | 92.9% |
| Opus | 4 | 4.8% |
| Haiku | 2 | 2.4% |
| **合計** | **84** | 100% |

Risk分類内訳(LOG該当列を機械集計、出典: LOG 205〜289行の「risk分類」列):

| Risk | 件数 |
|---|---|
| HIGH | 9 |
| MEDIUM | 40 |
| LOW | 30 |
| LOW〜MEDIUM | 5 |
| **合計** | **84** |

Opus 4件は全てHIGH(L2)。Haiku 2件は全てLOW(L0)。

**タスク種別内訳(見込み、LOGの選定理由列を目視分類)**:
- SSOT反映+Git統合(`PM-CLOSEOUT-CONSOLIDATION-XX`系): 約28件(LOG中`本タスク`と付記された行を数えた見込み値。正確な機械カウントは実施していないため「見込み」)
- Trial実行(記事生成・QA・比較検証): 約20件(3V/4V Voice Trial、News/Discovery段階Trial等)
- Production wiring・修正実装: 約8件(OPEN-131修正、OPEN-112修正、Household公開記事修正等)
- 設計・棚卸し・監査(read-only中心): 約10件(Gap Audit、Reconciliation Gate、News Stage4棚卸し等)
- 設計レビュー・診断(Opus): 4件
- 定型artifact・機械集計(Haiku): 2件

費用(¥、Production API実行を伴うTrialのみ記録、LOGより抜粋・出典行番号付き):
- `EDITORIAL-B-FAMILY-VOICES-4V-ARTICLE-TRIAL-01`: ¥37.2(LOG 217行)
- `EDITORIAL-B-FAMILY-VOICES-4V-ARTICLE-TRIAL-02`: ¥76.6(LOG 221行)
- `EDITORIAL-B-FAMILY-VOICES-3V-PERSON-VOICE-TRIAL-01`: ¥93.63(LOG 225行)
- `EDITORIAL-B-FAMILY-VOICES-3V-PERSON-VOICE-TRIAL-02`: ¥20.57(LOG 226行)
- `EDITORIAL-B-FAMILY-VOICES-3V-AUDIO-TRIAL-01`: ¥93.82(LOG 259行)
- `HOUSEHOLD-LEDGER-FACT-03-REVERIFICATION-01`: ¥2.6(LOG 247行)
- `FAMILY-A-NEWS-STAGE2-DIAGNOSTIC-BRANCH-TRIAL-08`: ¥42.5(LOG 252行)
- `FAMILY-A-DISCOVERY-STAGE2-INTERPRETATION-RULE-TRIAL-08`: ¥70.8(LOG 253行)
- `FAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-TRIAL-09`: ¥240.49(うち二重起動事故分¥2.56、LOG 267行)
- `FAMILY-A-DISCOVERY-STAGE3-RULE-ADJUSTMENT-TRIAL-09`: ¥127.3(LOG 268行)
- `FAMILY-A-DISCOVERY-STAGE4-CAUTIONARY-LANGUAGE-TRIAL-10`: ¥100.5(LOG 276行)
- `HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01`: ¥68.76(LOG 278行)
- `HOUSEHOLD-LEDGER-FACT-03-04-CONSISTENCY-FIX-03`: ¥3.31(LOG 264行)
- `HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-02`(継続1・2合算): ¥37.09(LOG 261行)

上記はいずれもSonnet実行タスクの費用(Production/Trial API呼び出し分)。**Opus・Haikuの委任自体にはこの種の¥API費用の記録がLOG上ない**(Opus/HaikuはSubagentのtoken消費のみ記録、外部API呼び出しなし=読み取り専用のため)。Opus/Haikuの「コスト」はtoken/時間のみで比較可能(3節・4節参照)。

### ベースライン(Trial開始前、2026-09-08〜09、全てSonnet固定、LOG 132〜174行・176〜199行)

| Risk | 件数 | token合計 | 所要時間合計 |
|---|---|---|---|
| LOW | 11 | 約1,156k | 約4,072s |
| MEDIUM | 32(うち18件は`PM-CLOSEOUT-CONSOLIDATION-05〜26`概算) | 約4,165k | 約17,785s |
| HIGH | 14 | 約3,035k | 約19,877s |
| **合計** | **57** | **約8,356k** | **約41,734s** |

差し戻し合計4件・規律違反合計4件(LOG 189〜197行)。全件Sonnet固定(モデル選定の余地なし)。

---

## 2. 役割分担との整合

**Sonnet偏重の有無**: あり(数値上)。Trial導入後84件中78件(92.9%)がSonnet。ただし単純比較は妥当でない。L0(Haiku)定義(LOG 23〜26行)は「読み取り専用・API支出なし・SSOT編集なし・Git操作なし・Production変更なし・Gate判断なし・出力はReport/表/定型artifactに限る」であり、Sonnet 78件の相当数(見込み約28件、`PM-CLOSEOUT-CONSOLIDATION-XX`系)は定義上SSOT編集+Git操作を必須要件とするため、構造的にHaikuへ委任できない。この部分については「偏重」ではなく「L0適用範囲外への正しい割当」と評価できる。

**Haikuで十分な軽作業をSonnetで実施した具体例**:
- `FAMILY-A-COMPLETION-GAP-AUDIT-A1-01`(LOG 224・231行、MEDIUM/Sonnet): 「Family A 3 Editorial Typeの15項目×3タイプGap Audit」は読み取り専用の棚卸しだが、選定理由は「SSOT・コード・Trial Report横断の正確な照合を要する」とSonnet側が判断(=単純な件数確認ではなく判定を伴うため、L0の「Gate判断なし」要件に抵触する可能性がある)。Haiku起用が妥当だったかは、判定を伴わない機械照合だけで済んだかどうかに依存し、ログ上は判定の有無が明確に切り分けられていない。
- `FAMILY-A-NEWS-STAGE4-REDESIGN-INVENTORY-01`(LOG 281行、MEDIUM/Sonnet): 「既存48 run・248 Point-attempt観測の¥0 offline再集計」は定型集計に近い性質を持つが、「候補1〜4のいずれを次Trial対象とするか等、UDR候補5点を提示」という設計判断を含むため、L0(判断を含まない)には収まらずMEDIUM/Sonnetとした判断は妥当と考えられる。
- `PM-GOVERNANCE-COST-IMPACT-RULE-03`(LOG 215行、LOW/Sonnet)・`PM-MODEL-ROUTING-TRIAL-TRIGGER-02`(LOG 207行、LOW〜MEDIUM/Sonnet): いずれもSSOT編集を伴うためL0不適格、Sonnet選定は妥当。

→ 結論: 「読み取り専用の件数確認」に見える案件の大半は、実際には「判断を含む照合」が付随しており、L0定義の厳密な要件(Gate判断なし)を満たさない。真にHaiku級で済んだのに見送られた明確な誤ルーティング事例は、ログ上特定できなかった(不明)。

**Opusを使うべき設計・原因分析をSonnetだけで進めた具体例**(Fable提供の事実に基づき確認):
- `EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PLAN-01_REPORT.md`(3V wiring影響分析): LOGの表に対応する専用行が見当たらず(LOG全289行を確認したがこの管理IDの行は存在しない)。Opusレビューを経た記録もない。**LOG自体の記録漏れの可能性がある**(LOG 54〜55行の記録ルール「統合タスク実行時にFableからの実績値提供を前提に追記する」が徹底されていない)。
- `HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01`(Household一本化設計、LOG 278行、MEDIUM/Sonnet): 「新候補採用可否/Part B案1 Production採用/`editorial_mode="discovery_why"`registry登録」という複数の未承認仕様候補・Production採用判断に関わる設計だが、選定理由は「Haiku不適・Opus不要(既存Production経路の適用)」のみで、Opus見送りの積極的理由（既存パターンの適用に留まる根拠）が薄い。実際、後続の`FAMILY-A-DISCOVERY-STAGE4-CAUTIONARY-LANGUAGE-TRIAL-10`(LOG 276行)でREVIEW率上振れ(0/6→2/6)の因果未確定という問題が発覚し、Household一本化への進行がSonnet自身の判断で条件付き非推奨とされた。この因果未確定という論点は、News Stage4のOpus L2レビュー(LOG 285行)が検出した「根拠指標が閾値未再校正のartifact」という論点と構造的に類似しており、Opus事前投入で早期検出できた可能性がある(見込み)。
- `FAMILY-A-DISCOVERY-STAGE2-INTERPRETATION-RULE-TRIAL-08`(Discovery仕様reconcile分析、LOG 253行、MEDIUM/Sonnet): Ledger v4のFACT-03/FACT-04内部矛盾という新規課題をSonnet自身が発見し別タスク(`HOUSEHOLD-LEDGER-FACT-03-04-CONSISTENCY-FIX-03`)を起動する結果になった。この種の見落としはA4 Discovery設計レビュー(LOG 238行)でOpusが検出したPOOL_TOPIC_MASTER事実誤りと同系統であり、Opus未投入のまま進めたことが遠因となった可能性がある(見込み)。

**News Stage4棚卸し→Opus L2レビュー実施済みの例**(比較対象として明示、LOG 281・285行): `FAMILY-A-NEWS-STAGE4-REDESIGN-INVENTORY-01`(Sonnet棚卸し)→`FAMILY-A-NEWS-STAGE4-REDESIGN-INVENTORY-01-OPUS-L2-REVIEW`(Opus)という段階分けが機能した唯一の明確な好例。これと対比すると、Household一本化・Discovery仕様reconcile・3V wiring影響分析はいずれも同様の「Sonnet整理→Opusレビュー」の2段階を経ていない。

---

## 3. Opus案件の整理(4件、全てL2)

| 管理ID | LOG行 | 何をレビュー/診断させたか | Sonnetだけでは得にくかった新しい示唆 | 後続の¥0監査・方針転換につながったか |
|---|---|---|---|---|
| `EDITORIAL-B-FAMILY-VOICES-3V-4V-WRITER-DESIGN-OPUS-REVIEW-01` | 211(要約122) | 3V/4V本文Writer Trial実行計画(Fable委任案)の着手前second opinion | 事実誤り2件(Trial-09系Writer経路不在/Ledger作成方式の誤り)、Production欠陥候補1件(OPEN-131 evidence欠落率91.1%[行]/87.3%[文字]の実測)、fail-open再発点2件、未承認仕様候補4件 | あり。`OPEN-131-ATTRIBUTION-BLOCK-MULTILINE-FIX-02`(LOG 213行)で実修正、4V Trial設計もOpus指摘反映版で再開(LOG 217行) |
| `FAMILY-A-COMPLETION-A4-DISCOVERY-DESIGN-OPUS-REVIEW-01` | 238 | Discovery設計案(判定木Q1〜Q5、境界事例)の3タイプ横断排他性・網羅性検証 | HIGH重大度: 判定木循環(Q1/Q3)、Q3とGate項目1の矛盾、Q5判定不能バケット、Q2先行によるTrend誤送、POOL_TOPIC_MASTER事実誤り(全20件Why主張が誤り、実際は英語Why7件+日本語なぜ7件) | あり。v2設計(`...DESIGN-02`、LOG 239行)へ反映、事実誤り訂正+2軸判定への再構成 |
| `FAMILY-A-POINT-QUALITY-RECONCILIATION-OPUS-REVIEW-01` | 249 | Reconciliation Gate(Sonnet横断整理)のsecond opinion | 因果連鎖の誤り2件(もぐらたたきが主因という主張、Focus ModuleがRole収束を引き起こすという主張)、実装欠陥候補1件、交絡候補1件(overlap_ratioへのPoint語数交絡) | あり。`FAMILY-A-POINT-QUALITY-STAGE1-RECOMPUTATION-01`(LOG 250行)で事後検証し、いずれも支持または条件付き支持と確認 |
| `FAMILY-A-NEWS-STAGE4-REDESIGN-INVENTORY-01-OPUS-L2-REVIEW` | 285 | News段階4整理(Sonnet)の改善候補4件・優先順位付けの妥当性 | 候補案根拠(§3-2entity除外)が閾値未再校正のartifactと指摘、真の見落とし論点H(Ledger fact供給量/evidence allocation)を提起 | あり。¥0監査`FAMILY-A-NEWS-STAGE4-EVIDENCE-ALLOCATION-AUDIT-01`(LOG 286行)を誘発、新規`OPEN-140`発見 |

**所見**: 4件とも「Sonnet単独では見落としていた具体的な誤り・欠陥・見落とし論点」を検出しており、追跡可能な範囲での的中率は4/4。いずれも後続タスクで支持または実修正につながっている(手戻り削減・判断精度向上の方向)。ただしN=4は小さく、LOG自身が正式Closeout Trigger未達として一般化を禁じている(LOG 78〜87行)。またOpus 4件は全てL2(事前・整理直後レビュー)で、L3(Sonnet差し戻し後の難問診断)は0件(GOV 676行の定義上、L3はまだ発動条件に至っていない)。

---

## 4. Haiku案件の整理(2件、全てL0)

| 管理ID | LOG行 | 適していた軽作業 | 品質問題 | Sonnet比のコスト/時間 | Sonnet再確認・やり直し |
|---|---|---|---|---|---|
| `FAMILY-A-POINT-QUALITY-RETRY-LOG-AGGREGATION-L0-01` | 248 | 過去Trial-04/05/06/07のretry log 50 runの機械集計 | あり。「NG」の定義(status基準かFact Checker FAIL基準か)・flag入れ替わり回数の数え方をFableが委任文で事前固定しなかったため、Haiku集計結果が既存Sonnet報告と不一致 | 43k token・126s・¥0(同種のSonnet LOW案件が平均約105k token・約370s、ベースライン集計より)、token/時間は約4割・3分の1程度 | **あり**。定義照合のためSonnetによる追加確認が発生し、集計結果は定義照合完了まで判断材料に使わない扱いとなった |
| `NEWS-DISCOVERY-COMPARISON-ARTIFACT-L0-01` | 251 | News/Discovery再改善の新Trial起票前に必要な既存比較artifact(baseline・approved/reference等)の定型生成 | なし。「Haiku→Sonnet再作業0件、定型artifact生成というL0適合タスクだったため」と明記 | 38k token・158s・¥0 | なし |

**所見**: 2件中1件でHaiku起因のSonnet再作業が発生(50%)。LOGが導いた教訓(LOG 123行)は「L0(Haiku)へ委任する際は、集計対象の用語定義(NG/差し戻し/入れ替わり等の数え方)を委任文側で明示的に固定することが、照合コスト削減の前提条件になる」。これはHaiku自体の能力問題というより、**委任文の事前定義不足**が原因と評価できる。もう1件(定型artifact生成)は問題なく機能しており、「既存フォーマットの機械的再現」に限定すればHaikuは有効という見込みが立つ(N=2のため確証ではない)。

---

## 5. 進行中案件の推奨ルーティング

対象(`OPEN_ITEMS.md` 1〜35行より確認した現行管理ID):
- Discovery Focus Module一般化Trial-11: `FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11`(N=1、towelsテーマ、A2/B1B)
- News再改善Trial-12: `FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12`(Ledger拡充A/B、後続¥0分析込み)
- 3V Production wiring: `EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1-01`(Phase 1確定事項に基づき並列実施中)、Phase 2(新テーマ「schools/homework」)・2V比較記事N=1(「supermarkets/food discount」)はPhase 1完了待ちで未着手

| 案件 | 工程 | 推奨モデル | 理由 |
|---|---|---|---|
| Discovery Trial-11 | 実行(記事生成・QA判定) | Sonnet | 記事生成・Fact Checker/Ledger判定を伴い、Haiku不適(L0はGate判断なし要件のため)。設計自体は既にOpusレビュー済み(LOG 238行)の延長 |
| Discovery Trial-11 | 結果の採否設計(N=1一般化の解釈) | **Opusレビューを検討する価値あり** | N=1データからの一般化判断は「N小データの因果解釈」に該当し、9節ルール案の対象。Household一本化で見られた「因果未確定のまま進行」パターンの再発防止 |
| News Trial-12 | 実行(Ledger拡充実装+記事生成) | Sonnet | 既存Research/Writer経路の適用、判定ロジックの精密な実装を要する |
| News Trial-12 | 結果解釈(A/B比較の統計的意味付け) | **Opusレビューを検討する価値あり** | Opus L2レビュー(LOG 285行)が既に「論点H」を提起した経緯があり、後続比較結果の解釈も同種の誤帰属リスクを持つ。過去のReconciliation Gateで因果推論の誤りが複数回検出された実績(LOG 249行)を踏まえる |
| News Trial-12 | regressionログ集計・費用集計 | **Haikuへ落とせる**(Agent定義新設が前提) | 定型集計・読み取り専用、L0要件に合致(LOG 248行の教訓=用語定義を委任文で固定する前提) |
| 3V wiring Phase 1 | 設計反映・offline regression実装 | Sonnet | Production配線・既存2V挙動不変の精密な確認を要する |
| 3V wiring Phase 1 | 差分レビュー(Production coreへの影響確認) | **Opusレビューを検討する価値あり** | ベースライン実績で類似の大型wiring案件(`EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01`、LOG 140行)は差し戻し2回・GATE_BLOCKED対応が発生しており、複数領域横断(Contract/QA/Gate/Writer)というHIGH classification基準(LOG 39〜41行)に該当する |
| 3V wiring Phase 1 | artifact存在確認・チェックリスト消化 | **Haikuへ落とせる**(Agent定義新設が前提) | 定型確認、判断を伴わない範囲に限定できれば |
| Phase 2記事(新テーマ)・2V比較記事N=1 | 記事生成・QA実行 | Sonnet | 既存パターンの適用、Phase 1完了待ちのため現時点では着手なし |
| Phase 2・2V比較記事 | Production採用可否の優先順位付け | **Opusレビューを検討する価値あり**(該当時) | 複数テーマ・複数Voice構成の優先順位付けは「複数候補の優先順位付け」に該当(9節ルール案) |

**Haiku Agent定義の欠如について**: 上記「Haikuへ落とせる」工程は、現状Fableが起動できるAgent定義が`sonnet-worker`/`opus-consultant`のみ(2節参照)であるため、**実行不可能**。必要であれば`.claude/agents/haiku-worker.md`の新設を提案するが、これはAgent構成の追加でありユーザー判断が必要(7節・末尾参照)。

---

## 6. モデルルーティングTrial自体のStatus

**現在のStatus(LOG 105行、変更履歴末尾まで一貫)**: 「未判定(中間レビュー・Closeoutいずれも未実施)」。LOGの「変更履歴」節(LOG 295〜576行)を通じて、直近行(LOG 574行付近)まで「中間レビュー・正式Closeout Triggerの到達判定・再計算はいずれも実施していない」という記述が一貫している。

**正式Closeout Trigger(LOG 78〜87行、6条件)との照合**:

| 条件 | 判定 | 根拠 |
|---|---|---|
| Trial開始後20委任以上 | 満たす | 84件(1節) |
| Haiku 5件以上 | **未達** | 2件のみ(4節) |
| Sonnet 10件以上 | 満たす | 78件 |
| Opus HIGH案件2件以上 | 満たす | 4件(3節) |
| 少なくとも2件がProduction wiringまで到達し手戻り・追加修正まで観測済み | **ログ上で特定不可(不確実)** | `OPEN-112-DIAGNOSTIC-RETRY-POINT-BODY-REGRESSION-FIX-01`は後日`PRODUCTION_WIRED`として受入れられた記録があるが(LOG 219行追記)、その後の手戻り観測有無は不明。3V自体は`APPROVED_FOR_PRODUCTION`のみで`PRODUCTION_WIRED`未到達(OPEN_ITEMS.md冒頭)。2件以上の明確な該当は確認できない |
| Haiku→Sonnet再作業・Fable差し戻し・規律違反・token/costが記録済み | 満たす | 4節のHaiku再作業1件、多数の規律違反(二重起動¥2.56等)がLOGに記録済み |
| 件数を満たしてもモデル別サンプルが偏っていればcloseoutしない | **未達方向** | Haiku 2件・Opus 4件・Sonnet 78件は明確に偏っている |

→ **6条件中2条件(Haiku 5件以上、サンプル非偏在)が未達、1条件(Production wiring到達2件+手戻り観測)が不確実**。正式Closeoutには進めない段階。

**中間レビューTriggerとの照合**: 開始直後(LOG 122〜123行)に2回到達・記録済み。その後もOpus HIGH案件が2件→4件に増加(3節)、Haiku起因の再作業も既に記録済み(4節)にもかかわらず、「### 実施記録」表(LOG 118〜124行)への追記がない。**運用手続き上の緩み**として7節で扱う。

**結論**: Trialは観測継続中。追加観測(特にHaiku件数の積み増し、Production wiring到達後の手戻り観測)が必要。Production運用ルールとしての正式化(恒久化)はまだ早い段階。

---

## 7. 逸脱と是正案

| 逸脱 | 理由(見込み含む) | 是正案 |
|---|---|---|
| Haiku Agent定義が存在しない(`.claude/agents/haiku-worker.md`なし、`sonnet-worker.md`は`model: sonnet`固定) | Fable(PM層)が起動できるAgent定義がsonnet-worker/opus-consultantのみという運用制約(タスク冒頭の既知事実)。LOG上の「Haiku」2件がどの経路で実行されたかは、現行Agent定義だけでは説明できない | `.claude/agents/haiku-worker.md`の新設(ユーザー判断、Production安全性のcode/Prompt変更ではなくAgent構成の追加のため、影響範囲の説明を先に行うべき) |
| 中間レビューTrigger複数回超過も「実施記録」表が2件のまま更新されていない | closeout consolidationタスク側でTrigger到達判定を機械チェックする手順が徹底されていない見込み | 委任テンプレート(closeout consolidationの定型手順)に「LOGのTrigger到達判定」チェック項目を追加する |
| L2 Opus起動条件が「設計着手前のsecond opinion」中心で運用され、L3(Sonnet差し戻し後の難問診断)は0件のまま | GOV定義上(GOV 663〜676行)L2はHIGH案件の事前レビュー、L3は差し戻し後の診断であり、この使い分け自体は定義通り。逸脱というより「Opus起動条件がSonnet差し戻し後に限定されている」という懸念はL3のみに該当し、L2には該当しない(誤解のリスクがある点を明記) | 特になし(定義通りの運用)。ただしL2/L3の使い分けをFableの委任文で毎回明示する運用を継続する |
| Household一本化設計・3V wiring影響分析にOpusレビューが入っていない | 選定理由欄に「既存Production経路の適用」等の簡潔な記載のみで、News Stage4のような「Sonnet整理→Opusレビュー」の2段階が踏まれていない(2節参照) | HIGH classification基準(LOG 39〜41行「複数Familyへの波及がある」「後戻りコストが大きい」)に該当する設計判断は、着手前に一律でOpus要否をFableが明示的に検討する運用を徹底する |
| `EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PLAN-01`のLOG行が見当たらない | LOGの記録ルール(LOG 54〜55行)「統合タスク実行時にFableからの実績値提供を前提に追記する」の徹底漏れの可能性 | 次回closeout consolidationで当該管理IDの行を追記する |

---

## 8. コスト影響評価(案件ごと)

総コスト観点(初回実行+差し戻し+再調査+再実装+Production wiring時の追加修正、LOG 89〜97行の比較方法に準拠)で評価する。Opus/Haikuの委任自体は外部API費用を伴わない(token消費のみ)ため、ここでの「コスト」はSonnet実行が伴うProduction/Trial API費用(¥)を主軸とし、Opusレビューが「回避できた可能性のある再作業コスト」を方向性(見込み)で評価する。

| 案件 | 分類 | 根拠 |
|---|---|---|
| News Stage4 Opus L2レビュー(`...-OPUS-L2-REVIEW`、LOG 285行) | **cost-neutral〜cost-saving** | レビュー自体の追加API費用は¥0(Opus token消費のみ)。指摘(§3-2閾値未再校正artifact、論点H)は後続の¥0監査(`EVIDENCE-ALLOCATION-AUDIT-01`)へ直結し、候補1/2/4への誤った方向でのTrial投資(見込みで数十〜百円規模、過去のNews Trialの実測費用[¥42.5〜¥240.49、LOG 252/267行]が参考値)を未然に回避した可能性が高い。ただし回避額そのものはログ上で特定不可(見込み） |
| A4 Discovery設計 Opus L2レビュー(LOG 238行) | **cost-saving方向(見込み)** | レビュー自体は¥0。POOL_TOPIC_MASTER事実誤り・判定木循環という構造欠陥をTrial実行前(Production API呼び出し前)に検出しており、誤った判定木のままTrialを実行していた場合に発生したであろう再Trial費用(Discovery Trialの実測費用実績は¥70.8〜¥127.3、LOG 253/268行)を回避した可能性が高い |
| Household一本化(Sonnetのみ、LOG 253/261/264/276/278行等) | **cost-increasing方向(事後的に顕在化)** | Opus未投入のままStage2〜4のTrial(¥70.8+¥100.5等)・FACT-03関連修正(¥2.6+¥3.31+¥37.09)・最終候補生成(¥68.76)を積み重ねた末に、REVIEW率上振れ(0/6→2/6)の因果未確定という論点が残り、一本化への進行が条件付き非推奨となった(LOG 276行)。累積費用(見込み約¥283)がかかった段階でなお因果未確定という結果は、より早期にOpusレビューを挟んでいれば同種の論点(News Stage4のように)を先に検出できた可能性がある(見込み) |
| `FAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-TRIAL-09`二重起動事故(LOG 267行) | **cost-increasing** | 誤操作による二重起動で¥2.56の無駄なScaffold呼び出しが発生(規律違反として記録)。モデルルーティングとは直接関係しない運用事故だが、コストログの一部として存在する |
| 3V Production wiring計画(Sonnetのみ、設計段階) | **判定保留(未着手)** | 現時点でPhase 1実行中のため直接の総コスト評価は時期尚早。参考として、ベースライン期の類似大型wiring案件`EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01`(LOG 140行)は差し戻し2回・610k token・3916sを要しており、Opus未投入のwiring作業で差し戻しが発生した実績がある。Phase 1でも同種のリスクがあり、Opus事前レビューがあれば差し戻し2回分(見込みで数百k token・数十分規模の追加コスト)を削減できた可能性がある |
| Trial-09/Trial-10のバックグラウンド待機規律違反(LOG 267・276・277行) | **cost-increasing(小規模)** | 引き継ぎ担当による二重稼働(同一REPORT・comparison.html再作成)が発生(LOG 277行)。追加API費用は¥0だが、Sonnet実行の重複というコストは発生している |

**Quality/Cost分離評価**: News Stage4・A4 DiscoveryのOpusレビューは「品質向上(見落とし検出)に寄与し、かつレビュー自体のコスト増分がほぼゼロ(¥0のClaude Code内tokenのみ)」という、コスト増を伴わない品質向上の事例。一方Household一本化は「Opusレビュー費用を払わなかった代わりに、複数回のTrial(¥283相当)を経てなお因果未確定という結果」であり、**レビュー費用を惜しんだことが必ずしも総コスト削減にはなっていない可能性**を示唆する(見込み、確証ではない)。

---

## 9. 実務ルール案

**Opus投入が費用対効果に合う条件(見込み)**:
1. Production仕様変更を伴う設計判断(例: Discovery判定木、Household一本化のようなProduction採用可否に直結する設計)→ 費用見込み: Opus 1回分のtoken消費のみ(¥0、参考: 過去4件は100k〜121k token・327〜379s)。誤ルーティング検知方法: 後続Trialで因果未確定・方向修正が発生した場合(Household一本化のように)、遡及的に「Opusを入れるべきだった」と判定できる
2. 複数候補の優先順位付け(例: News Stage4の候補1〜4)→ 費用見込み: 同上。誤ルーティング検知方法: 優先順位付け後に採用した候補が後から棄却される(News Stage2診断ブランチTrial-08で条件分岐案がGate1=REJECTEDになったような)頻度が高い場合
3. N小データ(N=1〜3)の因果解釈(例: Discovery Trial-11のN=1一般化判断)→ 費用見込み: 同上。誤ルーティング検知方法: N小データからの結論が後の追試(N拡大)で覆る頻度
4. Sonnet差し戻し2回超(GOV 634〜637行のFable↔Sonnet往復上限に近い状態)→ L3相当。費用見込み: 同上。検知方法: 差し戻し回数そのものがLOGに記録される
5. HIGH Risk(LOG 39〜41行の定義: 複数領域横断、複数Family波及、後戻りコスト大)→ 費用見込み: 同上。検知方法: HIGH分類でOpus未投入のまま進めた案件で差し戻し・規律違反・UDR発生が起きた場合

**Haikuへ落としてよい条件(見込み、Agent定義新設が前提)**:
1. 読み取り専用かつGate判断を含まない機械集計(例: regressionログ集計、費用集計)→ 費用見込み: 過去実績で40k程度token・2〜3分、Sonnet比で概ね半分以下
2. 既知フォーマットの存在確認(例: artifact存在確認、固定チェックリスト消化)
3. 判断を含まない定型artifact生成(例: 比較用baseline artifact生成、LOG 251行の実績が唯一の成功例)
- **前提条件(4節の教訓)**: 集計対象の用語定義(NG/差し戻し/入れ替わり等の数え方)を委任文側で事前に明示的に固定すること。これを怠るとSonnetによる定義照合という追加コストが発生する(LOG 248行の実例)
- 検知方法: Haiku結果とSonnet既存報告の不一致が生じた場合、それはHaiku適性ではなく委任文の定義不足が原因である可能性を優先的に疑う

**Sonnetのままでよい条件**:
1. 記事生成・QA判定・retry判定ロジックを伴う実行(Production/Trial実行全般)
2. SSOT精密編集・Git操作を伴う統合作業(closeout consolidation全般、L0の「SSOT編集なし」要件に構造上抵触するため)
3. 既存承認済みパターンの適用のみ(新規設計判断を伴わない)
4. 設計自体が既にOpusレビュー済みで、その反映のみを行う場合

---

## ユーザー判断が必要な項目

1. **`.claude/agents/haiku-worker.md`の新設可否**: 現状Fableは Haikuへ委任できない(Agent定義不在)。5節・7節で提案したHaikuへ落とせる工程(regressionログ集計、artifact存在確認、費用集計)を実行するには新設が前提となる。推奨: 新設(理由: L0適用可能な定型作業がTrial期間中も継続的に発生しており[News Trial-12・3V wiring Phase1でも該当工程あり]、Agent定義がないため機会損失が続いている)。
2. **Household一本化・3V wiring・Discovery仕様reconcileへのOpus遡及レビュー要否**: 既に進行/完了した設計判断にOpusのsecond opinionを追加で入れるか。推奨: 3V wiring Phase 1差分レビューは着手前にOpus投入を検討(理由: HIGH classification基準に該当し、過去の類似wiring案件で差し戻し2回の実績があるため)。Household一本化は既に一定の結論[条件付き非推奨]が出ているため遡及レビューの必要性は低い(見込み)。
3. **モデルルーティングTrialの中間レビュー再実施**: LOGの「実施記録」表が2件のまま更新されていない状態を、次回closeout consolidationで更新するか。推奨: 実施(理由: Trigger超過が続いている状態を放置すると運用ルールの形骸化リスクがある)。
4. **正式Closeoutの時期**: 現状Haiku 5件未達・サンプル偏在のため時期尚早。推奨: Haiku Agent定義新設後、Haiku案件を追加観測してから再判定。

## QCD

- **Quality**: LOG・PM_GOVERNANCE.md・OPEN_ITEMS.mdの該当箇所を直接照合し、数値は全て出典行番号付きで記載。全文読込は避けGrep/Read範囲指定で実施(MODEL_ROUTING_TRIAL_LOG.mdのみ表集計のため全行走査)。
- **Cost**: 本タスク自体はAPI呼び出しなし(¥0)、読み取り専用。
- **Delivery**: 指定範囲(分析・REPORT作成)のみを実施し、SSOT・コード・Prompt・Gitへの変更は一切行っていない。

---

**証跡**: `C:\Users\tensh\eigo-radio\docs\pm\MODEL_ROUTING_TRIAL_LOG.md`(全576行のうち表本体1〜354行を精読、以降は変更履歴の反復確認)、`C:\Users\tensh\eigo-radio\docs\pm\PM_GOVERNANCE.md`(1節91〜108行、2-2節208〜226行、11節630〜709行)、`C:\Users\tensh\eigo-radio\OPEN_ITEMS.md`(1〜35行)、`C:\Users\tensh\eigo-radio\.claude\agents\`(ディレクトリ一覧・sonnet-worker.mdフロントマター確認)。
