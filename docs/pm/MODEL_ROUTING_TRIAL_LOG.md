# MODEL_ROUTING_TRIAL_LOG — モデル選定運用Trialログ

**管理ID: PM-MODEL-ROUTING-TRIAL-SETUP-01(2026-09-09、ユーザー承認)**
**Status: 運用Trial中。最大到達Status = `VALIDATED`。正式採用
(`APPROVED_FOR_PRODUCTION`相当のモデル選定ルール固定化)は別途ユーザー判断。**

このファイルはSSOTではない。正式なPM運用規則は`docs/pm/PM_GOVERNANCE.md`
(1節・11節)であり、本ファイルはそのTrial運用の実績記録・作業ログである。
Fable・Sonnetの委任判断における「モデル選定の妥当性」を事後検証するための
データを蓄積する目的のみを持つ。

## 目的

- 委任先モデル(Haiku/Sonnet/Opus)の選定が、リスクに見合ったコスト・品質・
  安全性で行われているかを、実績ベースで継続的に検証する。
- 目的は「総使用量を同程度に保ちつつ、重要な設計判断のQualityを上げる」こと
  であり、単純なコスト削減それ自体が目的ではない。
- Trialである間はモデル選定ルールを固定化・恒久化しない。ユーザーが正式採用を
  決定するまで、Fableは毎回のRisk分類・選定理由を明示し続ける。

## L0〜L3 定義

- **L0 = Haiku**(`sonnet-worker`定義に`model=haiku`指定で起動):
  読み取り専用・API支出なし・SSOT編集なし・Git操作なし・Production変更なし・
  Gate判断なし・出力はReport/表/定型artifactに限る。Haikuの誤りが仕様判断・
  Production判断へ直接入らないよう、Fableが必ず照合する。
- **L1 = Sonnet**: 実装・Trial・Production配線・SSOT精密編集・Git操作・
  比較検証・通常のfailure mode調査。既定の実行モデル。
- **L2 = Opus(読み取り専用、原則1回)**: HIGH案件の設計レビュー/second
  opinion。Fableが委任前に「なぜHIGHか/Opusで何を確認したいか/Sonnet単独
  では何が不足か」を明示したうえで起動する。儀式的な起用(毎回自動的に
  Opusへ回す運用)は禁止する。
- **L3 = Opus(読み取り専用、原則1回)**: Sonnet差し戻し後も未解決の難問診断
  (既存の`PM_GOVERNANCE.md`11節ルールに基づく)。
- 1管理IDあたりのOpus利用(L2+L3合計)は最大1回とする。

## Risk分類

- **HIGH**: Contract/QA/Gate/Writerなど複数領域を横断する。複数Familyへの
  波及がある。後戻りコストが大きい。新規failure modeへの根本対策である。
  3V/4V・Family追加等、将来拡張の土台になる。誤判断時のQCD影響が大きい。
- **MEDIUM**: 既知パターンを踏襲する。単一module中心である。通常のTrial・
  配線・修正作業である。
- **LOW**: 既存SSOT/JSONだけで機械的に処理可能である。誤りを即座に検知
  できる。Production/SSOTへ書き込まない。

評価は「やり直し込みの総コスト」で行う。1回で正しく終わるHIGH案件と、
複数回の差し戻しを要するLOW/MEDIUM案件を同列に比較しない。

## 記録ルール

- Fableは委任時に、選定したモデル・Risk分類・選定理由・他モデルを使わ
  なかった理由をACTIVE_TASK.mdまたは委任文に明示する。
- 統合(closeout consolidation)タスク実行時に、Sonnetが本ファイルの表へ
  該当管理IDの行を追記する(Fableからの実績値提供を前提とする)。
- 本ファイルには詳細ログ全文を貼らない。詳細証跡は既存の`ER-*_REPORT.md`
  または`er0XX_output/`側に残す。
- 「差し戻し」「規律違反」「UDR発生」の定義は`PM_GOVERNANCE.md`該当節
  (11節・8節等)の既存定義をそのまま用いる。

## 判定Trigger

- Trial開始日: 2026-09-09。
- 委任カウント起点: Trial開始後の委任 = `PM-MODEL-ROUTING-TRIAL-SETUP-01`の
  次の委任からカウントする(SETUP-01自体はカウントに含めない)。

### 中間レビュー Trigger(いずれか到達でFableがLOG集計→中間レビュー報告。
採否判断ではない)

目的: Haikuへの落としすぎ/Opus過剰投入/手戻り増加/コスト悪化の早期検知。

- Trial開始後10委任到達
- 最初のOpus HIGH案件完了
- Haiku起因でSonnetへのやり直し・差し戻し発生
- ルーティング起因と考えられる品質事故・規律違反発生
- Sonnet固定baseline比で正規化使用コストが明確に悪化し始めた

### 正式Closeout Trigger(すべて満たす)

- Trial開始後20委任以上
- Haiku 5件以上
- Sonnet 10件以上
- Opus HIGH案件2件以上
- 少なくとも2件がProduction wiringまで到達し後工程の手戻り・追加修正まで
  観測済み
- Haiku→Sonnet再作業・Fable差し戻し・規律違反・token/costが記録済み
- 件数を満たしてもモデル別サンプルが偏っていればcloseoutしない

### 比較方法

Sonnet固定baseline vs Trial。総コスト=初回実行コスト+差し戻し+再調査+
再実装+Production wiring時の追加修正。

最低限比較する項目: 総token・使用量 / Haiku・Sonnet・Opus比率 /
task完了時間 / 手戻り回数 / Fable差し戻し回数 / 設計見落とし /
Production wiring時の追加修正 / 規律違反 / UDR発生 / Quality改善 /
context再読コスト。

### Closeout Status

`REJECTED` / `VALIDATED` / `USER_DECISION_REQUIRED` のいずれかを用いる。
`VALIDATED`でも正式採用ではなく、正式採用はユーザー判断後に
`APPROVED_FOR_PRODUCTION`相当の運用決定へ別途移行する。

現在のStatus: 未判定(中間レビュー・Closeoutいずれも未実施)。

### 実施記録(中間レビュー・Closeout、Fableが到達の都度追記)

| 日付 | 種別(中間レビュー/Closeout) | 到達したTrigger | 結果(Status) | 備考 |
|---|---|---|---|---|
| (未実施) | — | — | — | — |

## ベースライン(Trial開始前、全てSonnet固定)

Trial開始(2026-09-09)より前、2026-09-08〜09に実施した委任の実績を、
Trial導入後との比較対象として記録する。Risk分類はFableの事後判定。
選定理由は全件共通で「Trial前のSonnet固定」(モデル選定の余地がなかった)。
差し戻し・規律違反はFableの記録どおり(記載のない項目は0)。

| 日付 | 管理ID | risk分類 | 使用モデル | 選定理由 | 他モデルを使わなかった理由 | Subagent token | 所要時間 | 差し戻し回数 | 手戻り | 規律違反 | UDR発生 | Production wiring時の追加修正 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-08〜09 | EDITORIAL-B-FAMILY-VOICES-COMMENT1-CONTRACT-FIX-TRIAL-10 | MEDIUM | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 144k | 649s | 1(n=3再現性) | あり | なし | 不明 | 不明 |
| 2026-09-08〜09 | PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-FORMAT-11 | MEDIUM | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 120k | 671s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | OPEN-112-THEME2-B1-NUMERIC-PRECISION-WIRING-AUDIT-01 | LOW(読取) | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 109k | 373s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | OPEN-112-THEME2-B1-NUMERIC-PRECISION-MINIMAL-FIX-RERUN-04 | MEDIUM | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 193k | 1114s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | NUMERIC-PRECISION-RETROACTIVE-AUDIT-01 | LOW | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 108k | 309s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | EDITORIAL-B-FAMILY-PRODUCTION-PATH-DESIGN-01 | HIGH | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 155k | 384s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01 | HIGH | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 初回281k+修正2回(181k+148k)=610k | 1820+1535+561=3916s | 2(安全機構未適用/GATE_BLOCKED対応) | あり | 0 | あり | 不明 |
| 2026-09-08〜09 | OPEN-112-THEME2-A2-NUMERIC-PRECISION-COMMON-WIRING-CHECK-01 | MEDIUM | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 165k | 969s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | OPEN-126-INDEPENDENCE-REEVALUATION-01 | LOW | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 58k | 150s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | OPEN-121-METHOD-D-FLAG23-REVIEW-ARTIFACT-01 | LOW(定型artifact) | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 138k | 683s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | OPEN-124-UNTRACKED-FILES-CLASSIFICATION-01 | LOW | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 115k | 772s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | PM-CONTEXT-MANAGEMENT-LIGHTWEIGHT-DESIGN-01 | MEDIUM | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 103k | 427s | 0 | Fableの誤り2点を訂正 | なし | 不明 | 不明 |
| 2026-09-08〜09 | PM-CONTEXT-MANAGEMENT-PLAN-B-IMPLEMENTATION-02 | MEDIUM | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 179k | 566s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | OPEN-121-METHOD-D-FLAG15-REVIEW-ARTIFACT-02 | LOW(定型artifact) | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 98k | 519s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | TTS-REPETITION-QA-INTENTIONAL-REPEAT-FALSE-POSITIVE-TRIAL-01 | MEDIUM | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 135k | 796s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | OPEN-121-METHOD-D-FALSE-POSITIVE-REDUCTION-TRIAL-01 | HIGH | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 133k | 1176s | 0 | なし | あり(バックグラウンド待機・重複通知) | 不明 | 不明 |
| 2026-09-08〜09 | OPEN-127/128 PRODUCTION WIRING(順次) | HIGH | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 359k | 2789s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | FAMILY-A-DESIGN-FIX-INVENTORY-01 | LOW | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 113k | 325s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | EDITORIAL-B-FAMILY-VOICES-PHASE1-5-FOUR-VOICES-AXIS-DESIGN-TRIAL-01 | HIGH | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 57k | 324s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | FAMILY-A-BRANCH-FACT-CHECK-02 | LOW | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 91k | 285s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | EDITORIAL-B-FAMILY-VOICES-PHASE1-5-FOUR-VOICES-STRUCTURE-DESIGN-TRIAL-02 | HIGH | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 67k | 307s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | FAMILY-A-TREND-SYNTHESIS-PRODUCTION-READINESS-01 | MEDIUM | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 146k | 471s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | FAMILY-A-DISCOVERY-DEFERRED-CLASSIFICATION-01 | LOW | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 106k | 211s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | FAMILY-A-LEGACY-NEWS-ASSET-SURVEY-01 | LOW | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 119k | 261s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | EDITORIAL-B-FAMILY-VOICES-PHASE1-5-3V-4V-INTEGRATED-DESIGN-TRIAL-03 | HIGH | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 124k | 658s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | OPEN-112-TREND-SYNTHESIS-MODE-PRODUCTION-WIRING-01 | HIGH | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 初回341k+修正1回120k=461k | 3643+1252=4895s | 1(A2 OK evidence) | あり | あり(費用上限超過・誤Ledger run) | 不明 | 不明 |
| 2026-09-08〜09 | FAMILY-A-DAILY-NEWS-SPEC-DRAFT-01 | LOW | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 101k | 184s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | EDITORIAL-B-FAMILY-VOICES-A2-FREE-ADDRESS-COMPLETION-TRIAL-01(STOP) | MEDIUM | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 67k | 185s | 0 | STOP | なし | あり | 不明 |
| 2026-09-08〜09 | EDITORIAL-B-FAMILY-VOICES-A2-FREE-ADDRESS-COMPLETION-TRIAL-02 | MEDIUM | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 321k | 2160s | 0 | なし | あり(バックグラウンド待機、費用ログ漏れ) | 不明 | 不明 |
| 2026-09-08〜09 | FAMILY-A-DAILY-NEWS-REFERENCE-FORMALIZATION-01 | MEDIUM(SSOT編集) | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 107k | 328s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | FAMILY-A-DAILY-NEWS-FOCUS-LAYER-DESIGN-TRIAL-01 | HIGH | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 87k | 345s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | EDITORIAL-B-FAMILY-VOICES-A2-CROSS-AUDIT-AND-FIX-03 | MEDIUM | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 186k | 1056s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | FAMILY-A-DAILY-NEWS-FOCUS-LAYER-COMPARISON-TRIAL-02 | MEDIUM | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 164k | 1376s | 0 | なし | あり(バックグラウンド待機) | 不明 | 不明 |
| 2026-09-08〜09 | EDITORIAL-B-FAMILY-VOICES-A2-SLOWDOWN-AND-KEYPHRASE-REGEN-04 | MEDIUM | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 245k | 1617s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | EDITORIAL-B-FAMILY-MULTI-VOICE-FACT-ATTRIBUTION-TRIAL-01 | HIGH | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 137k | 617s | 0 | 重複実行2回 | なし | 不明 | 不明 |
| 2026-09-08〜09 | FAMILY-A-POINT-ROLE-PLANNING-FOCUS-MODULE-CONNECTION-TRIAL-03 | HIGH | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 200k | 1081s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | EDITORIAL-B-FAMILY-VOICES-A2-PRODUCTION-WIRING-01 | HIGH | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 421k | 2054s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | EDITORIAL-B-FAMILY-MULTI-VOICE-FACT-ATTRIBUTION-TRIAL-02 | HIGH | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 121k | 644s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | OPEN-129-AUDIO-GATE-STRUCTURAL-COMPLETENESS-TRIAL-01 | HIGH | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 103k | 687s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | PM-CLOSEOUT-CONSOLIDATION-05〜26(SSOT+Git統合、計18件) | MEDIUM | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 平均約105k×18件 | 平均約300s×18件 | 0 | なし | なし | 不明 | 不明 |
| 2026-09-08〜09 | FAMILY-A-DAILY-NEWS-FOCUS-LAYER-COMPARISON-TRIAL-04 | MEDIUM | Sonnet | Trial前のSonnet固定 | ルーティング制度導入前 | 164k+ | 3408s | 0 | なし | あり(費用実測用`cl.install()`をバックグラウンド実行run2/3で呼び忘れ、生ログ欠落。response_id再取得+同型ギャップ推定で事後回復、TTS/ASR不実行のため安全実害なし) | 不明 | 不明 |

### ベースライン集計

件数・token合計・平均はSonnet実行回数ベース(修正・再生成往復を含む累積)。
PM-CLOSEOUT-CONSOLIDATION-05〜26は18件として件数・合計へ算入(個別値は
Fable記録の平均値からの概算)。

| risk分類 | 件数 | token合計 | token平均 | 所要時間合計 | 所要時間平均 |
|---|---|---|---|---|---|
| LOW | 11 | 約1,156k | 約105k | 約4,072s | 約370s |
| MEDIUM | 32(うち18件はCLOSEOUT-CONSOLIDATION概算) | 約4,165k | 約130k | 約17,785s | 約556s |
| HIGH | 14 | 約3,035k | 約217k | 約19,877s | 約1,420s |
| **合計** | **57** | **約8,356k** | — | **約41,734s** | — |

- 差し戻し合計: 4(MEDIUM 1件[COMMENT1-CONTRACT-FIX-TRIAL-10]、HIGH 3件
  [PRODUCTION-PATH-PHASE1-WIRING-01が2回、TREND-SYNTHESIS-MODE-PRODUCTION-
  WIRING-01が1回])
- 規律違反合計: 4(MEDIUM 2件[A2-FREE-ADDRESS-COMPLETION-TRIAL-02、
  DAILY-NEWS-FOCUS-LAYER-COMPARISON-TRIAL-02]、HIGH 2件
  [METHOD-D-FALSE-POSITIVE-REDUCTION-TRIAL-01、TREND-SYNTHESIS-MODE-
  PRODUCTION-WIRING-01])
- UDR発生: 個別記録なし(不明)の項目が大半。既知のUDR発生1件
  (A2-FREE-ADDRESS-COMPLETION-TRIAL-01のSTOP)。
- 上記は「全件Sonnet固定」時代の実績であり、Trial導入後の比較対象
  (基準値)として使う。Trial導入後の行はFableの委任時に新規追記する。

## Trial導入後の委任実績(2026-09-09 Trial開始後、`PM-MODEL-ROUTING-
TRIAL-SETUP-01`の次から起算)

| 日付 | 管理ID | risk分類 | 使用モデル(L) | 選定理由 | 他モデルを使わなかった理由 | Subagent token | 所要時間 | 差し戻し回数 | 手戻り | 規律違反 | UDR発生 | Production wiring時の追加修正 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-09 | FAMILY-A-POINT-OVERLAP-COUNTERMEASURE-PRE-AUDIT-01 | MEDIUM(L1/Sonnet) | Sonnet | 既存コード・過去決定の読み取り監査だがコード追跡精度が必要 | Haiku不適(コード根拠の正確な引用・判定を要する)、Opus不要(通常の監査パターン) | 102k | 285s | 0 | なし | なし | なし(STOP推奨提示のみ) | 不明 |
| 2026-09-09 | PM-MODEL-ROUTING-TRIAL-TRIGGER-02 | LOW〜MEDIUM(L1/Sonnet) | Sonnet | SSOT(本ファイル)への定型節追加、機械的だが文書間整合を要する | Haiku不適(SSOT編集を伴う)、Opus不要 | 34k | 71s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-09 | PM-CLOSEOUT-CONSOLIDATION-28(本タスク) | MEDIUM(L1/Sonnet) | Sonnet | SSOT精密編集(巨大単一行テーブルへの追記)+Git統合、既知パターンの踏襲 | Haiku不適(SSOT編集・Git操作を伴う)、Opus不要(通常のcloseout統合パターン) | 本タスク完了時点で未確定(次回Fable記録時に追記) | 同上 | 0 | なし | なし | 不明 | 不明 |
| 2026-09-09 | PM-CLOSEOUT-CONSOLIDATION-29(本タスク) | MEDIUM(L1/Sonnet) | Sonnet | SSOT精密編集(巨大単一行テーブルへの追記、新規Open Item起票、PM_GOVERNANCE新小節追加)+Git統合、既知パターンの踏襲 | Haiku不適(SSOT編集・Git操作を伴う)、Opus不要(通常のcloseout統合パターン、設計横断レビュー不要) | 本タスク完了時点で未確定(次回Fable記録時に追記) | 同上 | 0 | なし | なし | 不明 | 不明 |
| 2026-09-09 | FAMILY-A-POINT-OVERLAP-GAP-FIX-TRIAL-05(Lane A、並列稼働) | MEDIUM(L1/Sonnet) | Sonnet | 単一module(`er009_diagnostic_full_retry_modules_12.py`)中心の既知パターン修正Trial(G1/G2)、過去承認仕様との対応確認込み | Haiku不適(コード修正・retry判定ロジックを伴う)、Opus見送り(Pre-Audit-01で既存対策との重複が判明済みのため大規模(a)/(b)横断比較は不要、スコープがG1/G2に限定されたため) | 未確定(Lane A側タスクで記録) | 未確定 | 0 | 不明(Lane A側で記録) | 不明 | 不明 | 不明 |

## 変更履歴

- 2026-09-09(PM-MODEL-ROUTING-TRIAL-SETUP-01): 新設。L0(Haiku)〜L3(Opus)の
  定義・Risk分類・記録ルールを明記し、Trial開始前(2026-09-08〜09、全て
  Sonnet固定)の委任実績40件(うちPM-CLOSEOUT-CONSOLIDATION-05〜26は
  18件分をまとめた概算行)をベースラインとして記録した。
- 2026-09-09(PM-MODEL-ROUTING-TRIAL-TRIGGER-02): 「判定Trigger」節を新設。
  中間レビューTrigger・正式Closeout Trigger・比較方法・Closeout Statusの
  定義と、実施記録用の空表を追加した。Trial開始日・委任カウント起点
  (SETUP-01の次から)を明記した。既存Trial内容・Status・ベースライン表は
  変更していない。
- 2026-09-09(PM-CLOSEOUT-CONSOLIDATION-28): 新設「## Trial導入後の委任
  実績」表へ、Trial開始後の委任3件(FAMILY-A-POINT-OVERLAP-COUNTERMEASURE-
  PRE-AUDIT-01・PM-MODEL-ROUTING-TRIAL-TRIGGER-02・本タスク)を追記した。
  ベースライン表(Trial開始前)へ、未記録だった`FAMILY-A-DAILY-NEWS-FOCUS-
  LAYER-COMPARISON-TRIAL-04`(164k+、3408s、規律違反=費用実測用
  `cl.install()`未設置)を新規行として追加した(Trial開始前の委任のため
  ベースライン側、Trial開始後の表とは区別)。中間レビュー・正式Closeout
  Triggerの到達判定・集計値の再計算はいずれも実施していない(Fableの
  今後の判断事項)。
- 2026-09-09(PM-CLOSEOUT-CONSOLIDATION-29): 「## Trial導入後の委任実績」
  表へ、本タスク(PM-CLOSEOUT-CONSOLIDATION-29、Sonnet、MEDIUM)と、並列
  稼働中のLane A `FAMILY-A-POINT-OVERLAP-GAP-FIX-TRIAL-05`(Sonnet、
  MEDIUM、選定理由=単一module・既知パターン、Opus見送り理由=Pre-Audit-01
  で既存対策との重複が判明済みのため大規模(a)/(b)横断比較が不要になった
  こと)の2件を追記した。中間レビュー・正式Closeout Triggerの到達判定は
  実施していない。
