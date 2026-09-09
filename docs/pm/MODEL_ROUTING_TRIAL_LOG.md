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
| 2026-09-09 | 中間レビュー | 最初のOpus HIGH案件完了(`EDITORIAL-B-FAMILY-VOICES-3V-4V-WRITER-DESIGN-OPUS-REVIEW-01`) | 未判定(採否判断ではない、記録のみ) | Trial開始後の委任数7件(本タスク`PM-CLOSEOUT-CONSOLIDATION-30`含む)。モデル比率: Sonnet 6件・Opus 1件・Haiku 0件。**Opusレビューの寄与**: Fable委任案(3V/4V本文Writer Trial実行計画)の事実誤り2件を検出(0-A「Trial-09系Writer経路」不在/0-B「Ledgerは既存Research primitiveで作成可能」の誤り)、Production欠陥候補1件を検出(OPEN-131 `build_voice_attribution_block()`のevidence 1行抽出によるPASS実績の前提未実証、Fable検証で欠落率91.1%[行]/87.3%[文字]と実測)、fail-open再発点2件を指摘(`DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL`/`B_FAMILY_A2_SLOWDOWN_TARGET_SEGMENTS`のsegment名ハードコードにより3V/4V新segment名が安全機構から静かに漏れる)、未承認仕様候補4件を明示(pairwise Voice Distinctness Check新設/Comment roleのvoice数パラメータ化/required_structureの可変voice数生成方式/N=1では閾値を決定しない方針)。**Haiku未使用**: L0相当(読み取り専用・API支出なし・SSOT/Git操作なし・定型出力)に該当する作業がTrial開始後まだ発生していないため(委任案の性質上、いずれもSSOT編集・コード実測・設計横断レビューを伴いL1/L2相当だった)。**規律違反**: `FAMILY-A-DAILY-NEWS-FOCUS-LAYER-COMPARISON-TRIAL-04`の費用実測用`cl.install()`未設置(ただし本Trial開始[2026-09-09]前のベースライン期間の事案であり、本Trialのルーティング判断とは無関係)。**暫定所見**: Opus 1回の投入により、Fable委任案(Sonnetへの実行指示案)に含まれていた前提の事実誤り・Production安全性論点を着手前に検出でき、Sonnet側の手戻り(委任→着手→誤り発覚→再委任)を未然に回避できた可能性が高い。費用対効果は良好に見えるが、Opus HIGH案件はまだ1件のみ(N=1)であり、一般化した結論(Opus投入基準の妥当性等)は正式Closeout Trigger(Opus HIGH案件2件以上等)到達まで判断しない。**本行は中間レビューの記録であり、Trial継続・変更・中止の採否判断ではない。** |

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
| 2026-09-09 | FAMILY-A-POINT-OVERLAP-GAP-FIX-TRIAL-05(Lane A) | MEDIUM(L1/Sonnet) | Sonnet | 単一module(`er009_diagnostic_full_retry_modules_12.py`)中心の既知パターン修正Trial(G1/G2)、過去承認仕様との対応確認込み | Haiku不適(コード修正・retry判定ロジックを伴う)、Opus見送り(Pre-Audit-01で既存対策との重複が判明済みのため大規模(a)/(b)横断比較は不要、スコープがG1/G2に限定されたため) | 340k | 4152s | 0 | なし | あり(バックグラウンド実行での待機が発生した可能性、通知なしで検出。TTS/ASR実行やProduction/Prompt編集は伴わないためN縮小はSTOP規定内で安全実害なし) | あり(G1=実装漏れ確定・新規OPEN-133[SSOT記載と実装の不一致]・OPEN-134[NG42%はG1対象外]を新規登録、Gate1=`USER_DECISION_REQUIRED`) | 不明(配線未実施) |
| 2026-09-09 | EDITORIAL-B-FAMILY-VOICES-3V-4V-WRITER-DESIGN-OPUS-REVIEW-01 | HIGH(L2/Opus) | Opus | 3V/4V本文Writer Trial実行計画(Fable委任案)の着手前second opinion。Fact Safety(Ledger作成方式・出典帰属)・既存Production定数(Comment Contract/Disfluency QA必須segment表/A2 slowdown対象segment表)への後方互換性・OPEN-131既存PASS実績の前提という複数のProduction安全性論点が重なっており、Sonnet単独レビューでは委任案自体に含まれる事実誤りを検出できていなかったため | Sonnet単独では不足(Fable明示のとおり)、Haiku不適(設計レビュー・複数moduleの横断コード精査を要する) | 108k | 379s | 0 | なし(初回レビューで完了、Sonnetへの追加質問なし) | なし | 不明(本レビュー自体はTrial着手前のためUDR/Production wiring対象外) | 不明 |
| 2026-09-09 | PM-CLOSEOUT-CONSOLIDATION-30 | MEDIUM(L1/Sonnet) | Sonnet | Opusレビュー原文の転記+OPEN-131 evidence欠落の実測(読み取り専用・費用¥0)+中間レビュー記録+SSOT反映+Git統合、既知パターンの踏襲 | Haiku不適(SSOT精密編集・コード実行による実測・Git操作を伴う)、Opus不要(通常のcloseout統合パターン、設計横断レビュー自体は既に前段のOPUS-REVIEW-01で完了済み) | 179k | 778s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-09 | OPEN-131-ATTRIBUTION-BLOCK-MULTILINE-FIX-02 | MEDIUM(L1/Sonnet) | Sonnet | 単一関数(`build_voice_attribution_block()`)の抽出ロジック修正+runtime evidence再取得、既知パターンのProduction修正 | Haiku不適(Ledger書式実測・fail-closed挙動維持の精密なコード修正を要する)、Opus不要(欠陥自体は前段のOpusレビューで既に特定済み、本タスクは修正実装のみ) | 163k | 1322s | 0 | なし | なし | なし(A2のPASS→REVIEW_REQUIRED変化はTP回復でありUDRではない) | 不明 |
| 2026-09-09 | EDITORIAL-B-FAMILY-VOICES-AI-SCREENING-LEDGER-TRIAL-01 | MEDIUM(L1/Sonnet) | Sonnet | 4V本文Trial向け検証済みLedger作成(既存`_perplexity_call()`パターンの再利用+手作業curation)、Fact Safety精度を要する | Haiku不適(Fact Safety判定・curationの正確性を要する)、Opus不要(既存Trial-04〜07パターンの踏襲、新規設計判断なし) | 189k | 1020s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-09 | PM-GOVERNANCE-COST-IMPACT-RULE-03 | LOW(L1/Sonnet) | Sonnet | SSOT(PM_GOVERNANCE.md/PM_BRIEF.md)への定型節追加、機械的な文書間整合 | Haiku不適(SSOT編集を伴う)、Opus不要(定型節追加のみ) | 36k | 81s | 0 | なし | なし | 不明 | 不明 |
| 2026-09-09 | PM-CLOSEOUT-CONSOLIDATION-31(本タスク) | MEDIUM(L1/Sonnet) | Sonnet | SSOT精密編集(巨大単一行テーブルへの追記、OPEN-131修正版反映、Ledger Trial VALIDATED記録)+Git統合、既知パターンの踏襲 | Haiku不適(SSOT編集・Git操作を伴う)、Opus不要(通常のcloseout統合パターン、設計横断レビュー不要) | 355k(OPEN-112-DIAGNOSTIC-RETRY-POINT-BODY-REGRESSION-FIX-01行と同一セッション、合算値。個別内訳なし) | 1778s(同上) | 0 | なし | なし | 不明 | 不明 |
| 2026-09-09 | EDITORIAL-B-FAMILY-VOICES-4V-ARTICLE-TRIAL-01(再開・完了) | HIGH(L2扱いだがOpus予算は同管理ID群[3V/4V Writer Trial系]で既に消費済みのためSonnet実装) | Sonnet | Opus指摘(事実誤り2件・fail-open再発点2件・未承認仕様候補4件)を反映した再設計に基づく4V本文Trial着手。Pairwise Voice Distinctness(LLM)コスト見込み(4V有向12ペア+vs Hook4=16判定、1記事¥5〜15、処理1〜2分)をPM_GOVERNANCE 2-2(コスト影響評価)に沿って事前提示済み、上限¥300 | Opus再投入は見送り(第7節修正提案8項目の反映自体はSonnetで実施可能な既知パターン修正と判断されたため)、Haiku不適(記事本文生成・QA設計を伴う) | 168k(再開セッション分のみ、前回停止分[b1b_run01のWriter attempt1〜2・attempt3途中まで]の消費量は前回セッションのログ未回収のため不明) | 1224s(再開セッション分のみ) | 0 | あり(`b1prod.ARTICLE_PATH`未定義バグ修正[`EXISTING_2V_ARTICLE_PATH_TRIAL09`定数追加で対応]、`b1b_run01_attempt_history.json`/`summary.json`を実態[attempt1〜3全て]に合わせて再構築) | なし | あり(新規failure mode 3件でSTOP: F1=一人称"I"不使用[全attempt]、F2=Analytical Leakage CheckがVoice2/3/4でflagged状態のままMAX_WRITER_ATTEMPTS到達、F3=Production共通`validate_point_structure()`のh3_count≠2 hard-failが4V記事を無条件で弾く[Trial側は`run_writer_no_search()`直接呼び出しで迂回]。Gate1=`USER_DECISION_REQUIRED`、候補B-4V-1〜4提示中) | 不明(Trial STOP、Production採用判断は別途。Gate4=Production/Trial-07/registry無変更を確認済み。実測cumulative cost=¥37.2[Writer¥35.0+QA¥2.1、41 API call]) |
| 2026-09-09 | PM-CLOSEOUT-CONSOLIDATION-34(本タスク) | MEDIUM(L1/Sonnet) | Sonnet | SSOT精密編集(巨大単一行テーブルへの追記、G1 Fable受入反映、観測record初回記録、OPEN-120訂正、OPEN-132 Phase2追加)+Git統合、既知パターンの踏襲 | Haiku不適(SSOT編集・Git操作を伴う)、Opus不要(通常のcloseout統合パターン、設計横断レビュー不要) | 本タスク完了時点で未確定(次回Fable記録時に追記) | 同上 | 0 | なし | なし | 不明 | 不明 |
| 2026-09-09 | OPEN-112-DIAGNOSTIC-RETRY-POINT-BODY-REGRESSION-FIX-01 | MEDIUM(L1/Sonnet) | Sonnet | 単一module(`er009_diagnostic_full_retry_modules_12.py::build_diagnostic_section()`)への引数追加+呼び出し元1箇所の配線修正、既存Trial(`FAMILY-A-POINT-OVERLAP-GAP-FIX-TRIAL-05`)が既に配線案・回帰テスト方針を提示済みの既知パターン、承認済み挙動(ER-009-N1-DIAGNOSTIC-FULL-RETRY-CLOSEOUT-14)への回帰修正 | Haiku不適(retry判定ロジックに波及しないことの精密な確認・Production関数の直接修正を要する)、Opus不要(設計判断は既にTrial-05のReconciliation Checkで完了済み、実装のみ) | 355k(G1配線+PM-CLOSEOUT-CONSOLIDATION-33合算値、両タスクが同一セッションで連続実施されたため個別内訳なし) | 1778s(同上) | 0 | なし | なし | なし(Gate 3宣言はSonnetからは行わない、`PRODUCTION_WIRED候補`のまま。**2026-09-09追記(PM-CLOSEOUT-CONSOLIDATION-34)**: 後日Fableが`PRODUCTION_WIRED`として正式受入) | 不明 |
| 2026-09-09 | PM-CLOSEOUT-CONSOLIDATION-33(本タスク) | MEDIUM(L1/Sonnet) | Sonnet | SSOT精密編集(巨大単一行テーブルへの追記、CURRENT_SPEC訂正、Exit条件全文記録)+Git統合、既知パターンの踏襲 | Haiku不適(SSOT編集・Git操作を伴う)、Opus不要(通常のcloseout統合パターン、設計横断レビュー不要) | 本タスク完了時点で未確定(次回Fable記録時に追記) | 同上 | 0 | なし | なし | 不明 | 不明 |

## 変更履歴

- 2026-09-09(PM-CLOSEOUT-CONSOLIDATION-34、本タスク): OPEN-112-
  DIAGNOSTIC-RETRY-POINT-BODY-REGRESSION-FIX-01行とPM-CLOSEOUT-
  CONSOLIDATION-33行のtoken/所要時間を確定値(355k/1778s、両タスク
  同一セッション実施のため合算値)へ更新した。EDITORIAL-B-FAMILY-
  VOICES-4V-ARTICLE-TRIAL-01行を「再開・完了」へ更新し、再開セッション
  分のtoken/所要時間(168k/1224s、前回停止分は前回セッションのログ
  未回収のため不明)、手戻り(`ARTICLE_PATH`バグ修正等)、UDR発生(新規
  failure mode F1/F2/F3でSTOP、Gate1=USER_DECISION_REQUIRED)を記録した。
  本タスク(Sonnet、MEDIUM)を新規追記した。中間レビュー・正式Closeout
  Triggerの到達判定・再計算はいずれも実施していない。
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
- 2026-09-09(PM-CLOSEOUT-CONSOLIDATION-30): 「## Trial導入後の委任実績」
  表へ、`EDITORIAL-B-FAMILY-VOICES-3V-4V-WRITER-DESIGN-OPUS-REVIEW-01`
  (Opus、HIGH、3V/4V Writer委任案のsecond opinion、108k token・379秒・
  差し戻し0)と本タスク(PM-CLOSEOUT-CONSOLIDATION-30、Sonnet、MEDIUM)の
  2件を追記した。中間レビューTrigger「最初のOpus HIGH案件完了」に到達
  したため、「### 実施記録」表へ中間レビュー1件を記録した(委任数7件・
  モデル比率Sonnet6/Opus1/Haiku0・Opus寄与4点・Haiku未使用理由・既知の
  規律違反1件[Trial開始前の事案]・暫定所見を記載、採否判断ではない旨を
  明記)。正式Closeout Triggerへは未到達(Opus HIGH案件2件以上等の条件を
  満たしていない)。
- 2026-09-09(PM-CLOSEOUT-CONSOLIDATION-31、本タスク): PM-CLOSEOUT-
  CONSOLIDATION-30行のtoken/所要時間を確定値(179k/778s)へ更新した。
  「## Trial導入後の委任実績」表へ4件を新規追記した:
  OPEN-131-ATTRIBUTION-BLOCK-MULTILINE-FIX-02(Sonnet、MEDIUM、163k・
  1322s)、EDITORIAL-B-FAMILY-VOICES-AI-SCREENING-LEDGER-TRIAL-01
  (Sonnet、MEDIUM、189k・1020s)、PM-GOVERNANCE-COST-IMPACT-RULE-03
  (Sonnet、LOW、36k・81s)、本タスク(Sonnet、MEDIUM、token/時間は次回
  記録時に追記)。あわせて並列稼働中(本タスクでは触れていない)
  EDITORIAL-B-FAMILY-VOICES-4V-ARTICLE-TRIAL-01(Sonnet、HIGH、Opus
  レビュー済み設計を反映、Opus予算は同管理ID群で消費済みのためSonnet
  実装、Pairwise Voice Distinctnessのコスト見込みをPM_GOVERNANCE 2-2
  に沿って事前提示済み[上限¥300])を記録のみ追加した。中間レビュー・
  正式Closeout Triggerの到達判定・再計算はいずれも実施していない。
- 2026-09-09(PM-CLOSEOUT-CONSOLIDATION-32、本タスク): 「## Trial導入後の
  委任実績」表のFAMILY-A-POINT-OVERLAP-GAP-FIX-TRIAL-05行を確定値
  (Sonnet、MEDIUM、340k token・4152秒)へ更新した。規律違反列へ
  「バックグラウンド実行での待機が発生した可能性(通知なしで検出)」を
  記録した(TTS/ASR実行・Production/Prompt編集は伴わないためSTOP規定内、
  安全実害なし)。費用超過見込みによりN=3→N=2へ縮小した判断もSTOP規定内
  として扱う。UDR発生列へ、G1(前回Point本文埋め込み漏れ)=実装漏れ確定・
  新規`OPEN-133`(SSOT記載と実装の不一致)・`OPEN-134`(NG 42%はG1対象外)
  を新規登録した旨を記録した。中間レビュー・正式Closeout Triggerの
  到達判定・再計算はいずれも実施していない。
