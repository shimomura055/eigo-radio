# PM-HANDOFF-CHATGPT-001 照合レポート

**このファイルは正式SSOTではない。** ChatGPT側から提出されたHANDOFF PACKET(二次情報、
ChatGPTの会話履歴に基づく要約)と、リポジトリ側の正式SSOT
(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`HISTORY_INDEX.md`/
`CLAUDE.md`/`ER-*_REPORT.md`/`OPEN-*_REPORT.md`/Git/runtime evidence)を
照合した作業記録である。本ファイル自体はいかなる仕様も決定しない。
正式仕様・決定履歴・未決事項は引き続きroot直下の既存SSOTのみが根拠である。

作業日: 2026-09-05 / 実行者: sonnet-worker(1回目) / 管理ID: PM-HANDOFF-CHATGPT-001

---

## 1. 総評(先出し)

- 資料(HANDOFF PACKET)が挙げたcommit群(df40895, 0036e6f, fc48b7e, d64d713,
  9e89bc3, 667ea76, 141084d, b40c1f9, bf4f6de)は**全てmain上に存在**し、
  内容もrepo側の記述と実質一致していた。**Git上のDangling Referenceは
  今回の照合範囲では検出されなかった。**
- OPEN-112・OPEN-113・OPEN-114は資料の記述とOPEN_ITEMS.md実態が概ね一致。
  ただし細部(status文言・件数・危険度評価)は資料側がやや簡略化している
  箇所がある(詳細は§2)。
- 資料が「最終報告未確認」としていた
  `OPEN-112-DISCOVERY-4LAYER-FINAL-ADOPTION-READINESS-AND-OPEN114-REGISTER-07`
  (commit 141084d)は**実施済み**であることを確認した。ただし、
  OPEN_ITEMS.mdが参照する`OPEN-112-DISCOVERY-4LAYER-ADOPTION-READINESS-07_REPORT.md`
  という独立ファイルは**repo上に実在しない**(SSOT内部のdangling link)。
  内容自体はDECISION_LOG.mdへ直接147行で記録されている(commit 141084d)。
- Gate 1〜7・PM Closeout Mandatory Checkという名称・枠組みは、
  `CURRENT_SPEC.md`/`CLAUDE.md`/`docs/pm/PM_BRIEF.md`のいずれにも**一切存在しない**
  (grep 0件)。これは全てCHATGPT_ONLY_CANDIDATEである。
- 「ChatGPT=PM」という旧役割分担は、repo内のどのSSOTファイルにも
  "ChatGPT"という語自体が一度も登場しないため確認不能。現在は
  `CLAUDE.md`(未commit差分)がFableサンドイッチ運用を新PM層として定義済み
  であり、旧役割分担の記述はSTALE(現行体制に置き換わっている)と判断する。
- HISTORY_INDEX.mdは2026-08-09(ER-PM-001)以降更新が止まっており、
  ER-005以降・OPEN-112/113/114関連タスクは一切記載されていない
  (資料と無関係の既存SSOT側の遅延であり、今回のタスクでは修正しない)。

---

## 2. 重点確認項目ごとの結論

### a. Gate 1〜7 / PM Closeout Mandatory Check

`CURRENT_SPEC.md`・`CLAUDE.md`・`docs/pm/PM_BRIEF.md`を"Gate 1"〜"Gate 7"
および"PM Closeout Mandatory Check"でGrepした結果、**0件**。
`CURRENT_SPEC.md`内に存在するGateは全てdomain固有の技術Gate
(`Audio Validation Gate`・`A2 Gate`・`Assemble Gate`)であり、資料が言う
PM運用上のGate構造とは別物。

**分類: CHATGPT_ONLY_CANDIDATE(全7Gate + Closeout Checkの名称・枠組み自体)。**
根拠: grep結果0件(CURRENT_SPEC.md/CLAUDE.md/PM_BRIEF.md)。

ただし、Gateが要求する**個々の中身**(Trial/Production分離、
USER_DECISION_REQUIREDでのSTOP、APPROVED_FOR_PRODUCTIONは人間のみ、
Dangling Reference監査、次工程前のOpen Item確認)は、下記bで確認する通り
`CURRENT_SPEC.md`・`DECISION_LOG.md`・`docs/pm/PM_BRIEF.md`側に**実質的な
運用として個別に存在**している。「Gate 1〜7」という命名・体系化のみが
repo未記録という点に注意(内容が丸ごと無いわけではない)。

### b. 再発防止ルール

- Point-only regen禁止: `OPEN_ITEMS.md` OPEN-112行に
  「Point-only regenerationは既存仕様[ER-008-N8-FINAL-QA-HARDENING-21]
  により無効化されている」と明記。**MATCH**(SSOT記録あり)。
- Diagnostic Full Retry: `CURRENT_SPEC.md`に複数箇所出現
  (Point Value QA・Point Overlap統合箇所)。**MATCH**。
- Dangling Reference Check: `CURRENT_SPEC.md`(2026-08-31、
  ER-010-N1-SPEC-LIFECYCLE-PRODUCTION-GATE-04で正式導入、PROJECT_INDEX.md
  「仕様Lifecycle」節に記録)・`DECISION_LOG.md`双方に存在。**MATCH**。
- 「1記事ずつ完結」原則: `CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/
  `CLAUDE.md`/`docs/pm/PM_BRIEF.md`いずれにも該当文言なし(grep 0件)。
  **CHATGPT_ONLY_CANDIDATE**。実態としては、OPEN-113 Production Wiring
  (9e89bc3)が「採用した仕様をNo.18 B1という個別記事の実経路で再生成し
  確認する」形を取っており、原則自体は運用上体現されているが、
  SSOT上の明文原則としては存在しない。
- 安全化による品質劣化評価: OPEN-112-DISCOVERY-4LAYER-...-07の
  DECISION_LOG.mdエントリに「Fact Checker REVIEW_REQUIRED件数増加を
  無視しない」「安全だから成功、としない」という趣旨の分析が実在
  (Readiness判定が`USER_DECISION_REQUIRED_WITH_RISK`となった理由として
  明記)。**MATCH**(原則名としての明文化はないが、実際の判断ロジックとして
  適用されていることをDECISION_LOG.mdで確認)。

### c. VALIDATED / APPROVED_FOR_PRODUCTION / PRODUCTION_WIRED分離

`docs/pm/PM_BRIEF.md`(28〜36行目)に3語+`REJECTED`+`USER_DECISION_REQUIRED`
の定義が明記され、「`APPROVED_FOR_PRODUCTION`は人間ユーザーだけが決定できる」
と明記。`CLAUDE.md`(未commit差分)にも同旨の1行あり。
DECISION_LOG.md内の実例(9e89bc3で`APPROVED_FOR_PRODUCTION`→`PRODUCTION_WIRED`
の遷移記録、OPEN-83で`APPROVED_FOR_PRODUCTION`のまま`PRODUCTION_WIRED`に
していない実例)からも、この3段階分離は実際の運用ルールとして機能している。
**MATCH**(資料の主張とrepo実態が一致)。

### d. ChatGPT=PM / Claude=実務という旧役割分担の記録

`CLAUDE.md`・`CURRENT_SPEC.md`・`DECISION_LOG.md`・`OPEN_ITEMS.md`・
`HISTORY_INDEX.md`・`docs/pm/PM_BRIEF.md`のいずれにも"ChatGPT"という文字列
は1件も存在しない(grep 0件)。**UNVERIFIED(repo記録なし)**。
`CLAUDE.md`の現在の未commit差分は、旧役割分担ではなく新体制
(`sandwich-pm`(Fable)/`sonnet-worker`)のみを定義しており、
旧体制からの引き継ぎである旨の記述も無い。
**分類: STALE_OR_SUPERSEDED**(現行CLAUDE.mdが新体制に置き換えている)。

### e. Status Matrix(資料§6)・User Decisions(資料§7)個別照合

| 資料の項目 | 資料のStatus | repoの事実 | 分類 | 根拠 |
|---|---|---|---|---|
| No9 shared specs(d64d713) | PRODUCTION_WIRED(会話評価) | commit d64d713はmain上に実在。ただし内容は「Trial仕様の棚卸し・最終承認記録」であり、Storytelling First等の個別仕様自体はそれより前のcommit(ER-010-NO9-STORYTELLING-NOJARGON-PRODUCTION-WIRING-06等)で既にPRODUCTION_WIRED済み。d64d713はその**closeout確認**という位置づけ | MATCH(ただし資料はd64d713を「配線commit」のように書いており厳密には「closeout/最終承認commit」) | `git show --stat d64d713`、`DECISION_LOG.md`該当エントリ |
| No18 Pattern A + Numeric Precision | PRODUCTION_WIRED | `CURRENT_SPEC.md`(ER-011-NO18-EVIDENCE-COMPRESSION-A-PRODUCTION-WIRING-AND-FINAL-CANDIDATE-AUDIO-21R)に`PRODUCTION_WIRED`と明記 | MATCH | CURRENT_SPEC.md該当行 |
| No18 Pattern B/C | UNKNOWN/DEFERRED CANDIDATE | `OPEN_ITEMS.md`(OPEN-100関連記述)に「Pattern B/Cは`DEFERRED CANDIDATE / NOT REJECTED`のまま変更なし」と明記 | MATCH | OPEN_ITEMS.md OPEN-100行 |
| OPEN-107 | REJECTED/WITHDRAWN | `OPEN_ITEMS.md`のOPEN-107欄は`WITHDRAWN`(2026-09-03、ユーザー正式決定)。`CURRENT_SPEC.md`にも同旨記録・Dangling Reference Check完了の記述あり | MATCH | OPEN_ITEMS.md OPEN-107行、CURRENT_SPEC.md該当エントリ |
| No18 trim .30/tight_speech(0036e6f) | PRODUCTION_WIRED | commit 0036e6fはmain上に実在。`CURRENT_SPEC.md`冒頭に全文記録、runtime evidence(sha256一致・単体テスト12件・regression 2047/2051)も記述あり | MATCH | git show、CURRENT_SPEC.md |
| Standard2+Minimal1 TTS(fc48b7e) | PRODUCTION_WIRED | commit fc48b7eはmain上に実在。regression 22テスト・全体2066/2069 PASS、実TTS/ASR runtime evidence取得済みとcommit本文に明記 | MATCH | git show fc48b7e |
| OPEN-113(9e89bc3) | PRODUCTION_WIRED | `OPEN_ITEMS.md`OPEN-113行 = `RESOLVED / PRODUCTION_WIRED`。ただし「恒久課題としてのcloseではなく、今回のトリガーとなった重複問題への対処が完了したという意味でのRESOLVED」という限定付き | MATCH(ただし資料は単純に"PRODUCTION_WIRED"とのみ記載し、この限定条件を落としている) | OPEN_ITEMS.md OPEN-113行 |
| OPEN-114 | Open/non-blocking(実登録UNVERIFIED、資料は登録有無を未確認としていた) | `OPEN_ITEMS.md`に**実在**(OPEN-114行、`DEFERRED / NON-BLOCKING`)。commit 141084dで正式登録 | 資料はUNVERIFIEDとしていたが、repo照合の結果は**MATCH**(実際に登録済みと確認できた) | OPEN_ITEMS.md OPEN-114行、git show 141084d |
| OPEN-112 Discovery 4-layer Trial-05 | VALIDATED | `OPEN_ITEMS.md`OPEN-112行に「OPEN-112-A-FAMILY-4LAYER-PROMPT-DESIGN-TRIAL-05」の記述、Adoption Readiness判定は`USER_DECISION_REQUIRED_WITH_RISK`(単純な`VALIDATED`のみではない、trade-off明記あり) | MATCH(ただし資料はTrial自体の`VALIDATED`のみを書き、後続のAdoption Readiness判定`USER_DECISION_REQUIRED_WITH_RISK`に触れていない箇所がある) | OPEN_ITEMS.md OPEN-112行、DECISION_LOG.md 141084dエントリ |
| OPEN-112 News Mode Design-08 | USER_DECISION_REQUIRED/Design ready | `OPEN_ITEMS.md`OPEN-112行に該当追記あり、`NEWS_MODE_DESIGN_READY`と判定 | MATCH | OPEN_ITEMS.md OPEN-112行 |
| Trial-09 Trend minimal prompt | USER_DECISION_REQUIRED | `OPEN_ITEMS.md`OPEN-112行に該当追記あり、3件のUSER_DECISION_REQUIRED候補を「報告のみ」(OPEN_ITEMSへの正式登録は未実施)と明記 | MATCH | OPEN_ITEMS.md OPEN-112行 |
| Trial-10 Engagement+Reference A/B | USER_DECISION_REQUIRED(全体) | `OPEN_ITEMS.md`OPEN-112行の状態欄が`USER_DECISION_REQUIRED`(2026-09-05、Trial-10)で現在の最新状態 | MATCH | OPEN_ITEMS.md OPEN-112行(状態列) |
| Topic SSOT(POOL_TOPIC_MASTER.md) | canonical | `OPEN_ITEMS.md`OPEN-112行に「POOL_TOPIC_MASTER.mdを唯一の正式SSOTとしてユーザーが再確認した」と明記 | MATCH | OPEN_ITEMS.md OPEN-112行(2026-09-04追記部分) |
| 「なるべく軽く」方針 | 新Validatorを先に増やさずTrialで測る | Trial-09/10いずれも「新規Validator不要と判断」と明記、新規Validator追加はいずれも0件 | MATCH | OPEN_ITEMS.md OPEN-112行 |

### f. APPROVEDだが未配線の疑い

`DECISION_LOG.md`を`APPROVED_FOR_PRODUCTION`でgrep(15件)した中で、対応する
`PRODUCTION_WIRED`への昇格が明記**されていない**ものを検出した:

1. **固有名詞の発音判定基準の変更**(ER-008-N8-HUMAN-APPROVAL-AND-
   PROPER-NOUN-PRONUNCIATION-SPEC-16、DECISION_LOG.md 4820行付近)。
   ユーザーが`APPROVED_FOR_PRODUCTION`と決定した判定基準の変更だが、
   同エントリ内に明記された通り「Cascadeの自動判定ロジックへの実装・
   テスト・Production経路でのruntime確認が完了するまでは
   `PRODUCTION_WIRED`としない」。対応するOPEN-83は現在も
   `STOPPED_FOR_DESIGN_REVIEW`(ユーザー判断待ち)のまま。
   **これは資料(ChatGPT HANDOFF PACKET)には一切記載がない、
   repo側だけで見つかった未配線APPROVED項目である。**
2. OPEN-113のPoint-context-only方式(9e89bc3)は`APPROVED_FOR_PRODUCTION`
   →`PRODUCTION_WIRED`まで到達済みで、未配線の疑いなし(MATCH、資料通り)。
3. No18 trim/TTS/Evidence Compression Pattern Aも同様にPRODUCTION_WIRED
   まで到達済みで未配線の疑いなし。

資料§9「Approved but Not Production Wired」は「該当なしとは断定できない、
Fableが再照合すること」としていたが、今回の照合で**1件(OPEN-83関連の
発音判定基準)を発見した**。これは資料の管理ID・タスク一覧の対象範囲外
(No.8, 2026-08-28)であり、資料が見落としていたという意味では
CHATGPT側の情報の不完全性を示す一例である。

### g. USER_DECISION_REQUIRED全件

`OPEN_ITEMS.md`の状態列(表の第3列)を機械的に抽出したところ、
文字列として現在も`USER_DECISION_REQUIRED`のままなのは**OPEN-112のみ**
(1件、2026-09-05 Trial-10時点)。

その他、`TBD`/`UNDER_REVIEW`/`OPEN`/`STOPPED_FOR_DESIGN_REVIEW`
(実質ユーザー判断待ち)の項目は多数存在するが、いずれも本Handoff資料の
対象範囲外(ER-002〜ER-008時代の旧項目、例: OPEN-83等)であり、
資料末尾「未決事項再掲」9項目とは無関係。

資料末尾の9項目は、実質すべて**OPEN-112 1行に集約**されている
(Discovery採否・Trend severity・Overlap閾値・Ledger自動化・Engagement採否・
Reference Digest・Point長さ、の7項目はOPEN-112行の記述内に個別列挙あり)。
残り2項目(OPEN-114登録有無/他のAPPROVED未配線有無)は本レポート§2-e・
§2-fで個別に解消・追加発見済み。

**DECISION_LOG.md側**は`USER_DECISION_REQUIRED`が57件ヒットするが、
これはDecision Logという性質上「過去に一度そう判定されたが後続エントリで
既に解消済み」の履歴的言及を多数含む(例: No.9関連はd64d713のCloseout監査
で「未処理USER_DECISION_REQUIRED0件」と明記)。個別に全57件を再確認する
ことは今回のscope・costの範囲を超えるため**UNVERIFIED(件数の内訳は
未精査)**とし、`OPEN_ITEMS.md`側の現在値(OPEN-112のみ)を一次情報として
採用する。

### h. 未報告Trial・資料に無いタスク

- `git log --oneline -30`の範囲では、資料に記載の無いTrial/タスクは
  **確認されなかった**(bf4f6de/b40c1f9/667ea76/141084d/9e89bc3/df40895/
  c42e72a/16c92ec/76a90dc/f158e89/e9dbb42はすべて資料のTrial History
  (§11)またはStatus Matrix(§6)に何らかの形で言及がある)。
- `OPEN-112-DISCOVERY-4LAYER-FINAL-ADOPTION-READINESS-AND-OPEN114-REGISTER-07`
  (commit 141084d)は資料が「最終報告未確認」としていたタスクだが、
  **実施済みであることを確認**(§1参照)。ただし、対応する独立ファイル
  `OPEN-112-DISCOVERY-4LAYER-ADOPTION-READINESS-07_REPORT.md`は
  repo上に存在しない(`find`で0件)。DECISION_LOG.mdへの直接記録
  (commit 141084d、147行追加)が実質的な最終報告に相当する。
  **分類: MATCH(実施は確認)+ 別途SSOT内部のdangling link(下記§9参照)。**
- `HISTORY_INDEX.md`はER-PM-001(2026-08-09)以降更新されておらず、
  ER-005〜ER-011・OPEN-112/113/114のいずれも掲載されていない。
  これは資料の照合対象ではないが、既存SSOT側の別の技術的負債として
  記録しておく(今回は修正しない)。

### i. OPEN-114のOPEN_ITEMS.md実登録

確認済み。`OPEN_ITEMS.md` 166行目に独立行として存在し、状態は
`DEFERRED / NON-BLOCKING`(2026-09-05、141084dで正式登録)。
**分類: MATCH**(資料はUNVERIFIEDとしていたが実際は登録済み)。

### j. §16 ChatGPT-only Knowledge Candidatesの照合

| 資料の項目 | repo記録有無 | 分類 |
|---|---|---|
| 「1つ1つの記事で完結させる」原則 | 該当文言なし(grep 0件) | CHATGPT_ONLY_CANDIDATE |
| Discovery baseline=No.18、No.9は補助regression | `OPEN_ITEMS.md`OPEN-112行(2026-09-04追記)に「Discovery検証baselineはNo.18を使用(No.9は補助Regression/比較資料、Primaryではない)とユーザーが決定した」と明記 | MATCH(資料の主張通りrepoに記録済み) |
| Editorial Type候補(Discovery/Why, News/Trend, Voices, Case Story, Future/Scenario) | `OPEN_ITEMS.md`OPEN-112行に「ABC Family大枠(A=Discovery/Why+News/Trend Synthesis、B=Voices+Case Story、C=Future/Scenario)」と明記。資料の表現(B=Perspective/Case)とrepoの表現(B=Voices+Case Story)は**語彙が微妙に異なる**(同一概念の言い換えの可能性が高いが、正式名称としてどちらが正か確定できない) | 概ねMATCHだが名称表記に差異あり。**UNVERIFIED(正式名称)** |
| Family案 A/B/C | 同上、OPEN_ITEMS.mdに記録あり | MATCH(内容)、名称表記はUNVERIFIED |
| NewsをMajor/Daily+Trend Synthesisへ集約 | `OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md`・`OPEN_ITEMS.md`OPEN-112行に明記 | MATCH |
| 将来Personalization/Coverage Required概念 | grep該当なし(OPEN_ITEMS.mdに明示的記述を確認できず) | CHATGPT_ONLY_CANDIDATE |
| Trend Memory/Recent Coverage Check将来候補 | grep該当なし | CHATGPT_ONLY_CANDIDATE |
| Reference ArticlesはFact source不可、構成・切り口専用 | `OPEN_ITEMS.md`OPEN-112行(Trial-10追記)に「Fact source使用禁止」「Reference Articles由来の具体的Factが生成記事へ混入していないことを逐語確認(混入0件)」と明記 | MATCH |
| 「安全になったから成功、としない」PM原則 | 明文原則としては存在しないが、141084dのDECISION_LOG.mdエントリで実質的に適用された判断ロジックとして確認できる(§2-b参照) | 部分MATCH(原則の明文化なし、適用実績あり) |
| OPEN-112-07最終報告未確認 | 実施済みと確認(§1・h参照) | 資料の主張は誤り、repo確認で**解消**(MATCH方向で更新) |

### k. §17 Conflictsの照合

資料が挙げた7項目のConflicts/Ambiguitiesは、いずれもrepo側で個別に
「resolved」または「repoの記述として残っている経緯」として確認できた
(例: Topic Master正式化、News Focus Module 1個→2個への設計変更、
OPEN-113のPRODUCTION_WIRED認定がClaude報告+ユーザー承認ベースであること)。
これらは**MATCH**(資料の記述通りrepo側にも痕跡がある)であり、
新たなCONFLICT(資料の記述とrepoの記述が真に矛盾する事例)は
**今回の照合範囲では発見されなかった**。

### l. Git状況

- 現在のmain HEAD: `bf4f6dee3d7826b83785ee7ca92edcce67818b57`
  (`OPEN-112-TREND-ENGAGEMENT-REFERENCE-AB-TRIAL-10`)
- 資料記載commit全件がmain上に存在することを`git branch --contains`で確認:
  df40895 / 0036e6f / fc48b7e / d64d713 / 9e89bc3 / 667ea76 いずれもmain。
  追加確認した141084d・b40c1f9・bf4f6deもmain。
- `git status --short`: 変更行数282件(ほとんどが`er0XX_output/`配下の
  生成物・`docs/pm/`新規ファイル・`.claude/`設定など、untracked生成物が
  大半)。**Production正式コード・Promptに対する未commit変更は
  `CLAUDE.md`(sandwich-pm運用セクション追加、未commit)のみ確認**。
  `CLAUDE.md`のこの差分はProductionコード/Promptではなく運用ドキュメント
  であり、本タスクのProduction安全性には影響しない。

### m. 次タスクとの整合

`OPEN_ITEMS.md`OPEN-112行の最新状態(`USER_DECISION_REQUIRED`)と、
資料§14「次タスク」(UDR全件照合を目的とする、新規Prompt/Trial/Production
変更は対象外)は整合している。次に許可される工程は、OPEN-112の
USER_DECISION_REQUIRED解消(Discovery採否・Trend/Engagement/Reference/
Ledger/Overlap閾値等のユーザー判断)であり、資料の記載と食い違いはない。

---

## 3. Gate/再発防止ルールのSSOT記録有無(まとめ)

| ルール | SSOT記録 | 分類 |
|---|---|---|
| Gate 1〜7個別名称 | なし | CHATGPT_ONLY_CANDIDATE |
| PM Closeout Mandatory Check名称 | なし | CHATGPT_ONLY_CANDIDATE |
| Point-only regen禁止 | あり(OPEN_ITEMS.md OPEN-112行) | MATCH |
| Diagnostic Full Retry | あり(CURRENT_SPEC.md) | MATCH |
| Dangling Reference Check | あり(CURRENT_SPEC.md/DECISION_LOG.md、2026-08-31正式導入) | MATCH |
| 「1記事ずつ完結」原則(明文) | なし | CHATGPT_ONLY_CANDIDATE |
| VALIDATED/APPROVED/PRODUCTION_WIRED分離 | あり(docs/pm/PM_BRIEF.md) | MATCH |
| 安全化=品質劣化評価(明文原則) | なし(適用実績はあり) | 部分MATCH |

---

## 4. APPROVEDだが未配線の疑い一覧

1. **固有名詞発音判定基準の変更**(ER-008-N8-HUMAN-APPROVAL-AND-PROPER-NOUN-
   PRONUNCIATION-SPEC-16、`APPROVED_FOR_PRODUCTION`のまま、対応する
   OPEN-83は`STOPPED_FOR_DESIGN_REVIEW`)。資料には記載なし、repo照合のみで発見。

他の資料記載項目(No18各種、OPEN-113)は全てPRODUCTION_WIREDまで
到達済みで未配線の疑いなし。

---

## 5. USER_DECISION_REQUIRED全件一覧(現在値)

`OPEN_ITEMS.md`状態列(現在値)で`USER_DECISION_REQUIRED`なのは:

- **OPEN-112**(1件のみ。Discovery 4-layer採否・Trend overclaim severity・
  Point Overlap閾値・Trend Ledger自動化・Engagement根底指示採否・
  Reference Digest採否・Point長さ目安、の7論点が同一行内に集約)

その他多数のTBD/UNDER_REVIEW/STOPPED_FOR_DESIGN_REVIEW項目
(OPEN-83等)は本Handoff資料の対象範囲外(旧ER-002〜ER-008時代)。

---

## 6. 未報告Trial・資料に無いタスク一覧

**発見なし**(git log直近30件・root直下`OPEN-*_REPORT.md`一覧のいずれにも、
資料未記載のTrialは確認されなかった)。
`OPEN-112-DISCOVERY-4LAYER-FINAL-ADOPTION-READINESS-AND-OPEN114-REGISTER-07`
(141084d)は資料が「未確認」としていたが実施済みと確認(§2-h)。

---

## 7. CHATGPT_ONLY_CANDIDATE一覧(SSOT追加候補。追加はしない)

1. Gate 1〜7の個別名称・体系
2. PM Closeout Mandatory Checkという名称
3. 「1つ1つの記事で完結させる」という明文原則
4. 将来Personalization/Coverage Required概念
5. Trend Memory/Recent Coverage Check将来候補
6. 「安全になったから成功、としない」という明文PM原則(適用実績はあるが原則としての明文化なし)
7. ChatGPT=PM/Claude=実務という旧役割分担の記録(現行体制で置き換え済み)

---

## 8. CONFLICT一覧

**なし**(今回の照合範囲では、資料の記述とrepo側の記述が真に矛盾する
事例は発見されなかった)。

---

## 9. STALE_OR_SUPERSEDED一覧

1. 「ChatGPT=PM、Claude Code=実務」という旧役割分担
   (`CLAUDE.md`の現行体制(sandwich-pm/Fable、未commit差分)に置き換え済み)。
2. `OPEN_ITEMS.md`内で参照される`OPEN-112-DISCOVERY-4LAYER-ADOPTION-
   READINESS-07_REPORT.md`というファイル名は、実際には作成されず
   DECISION_LOG.mdへ直接記録された(SSOT内部の軽微なdangling link。
   今回のタスク範囲では修正しない。参考情報として記録)。

---

## 10. UNVERIFIED一覧

1. Family案のB群名称(資料: Perspective/Case、repo: Voices+Case Story)
   ── 同一概念の言い換えの可能性が高いが正式名称としてどちらかは未確定。
2. `DECISION_LOG.md`側の`USER_DECISION_REQUIRED`57件ヒットの内訳
   (履歴的言及と現在有効な未決事項の切り分けは今回未実施、コスト超過のため)。
3. No9関連(d64d713以前)の各PRODUCTION_WIRED項目の**現在の**runtime
   evidence所在(ファイル実在確認は今回未実施、SSOT記述の再確認のみ)。

---

## 11. Git状況(まとめ)

- HEAD: `bf4f6dee3d7826b83785ee7ca92edcce67818b57`
- 資料記載commit(df40895, 0036e6f, fc48b7e, d64d713, 9e89bc3, 667ea76)
  および追加確認したcommit(141084d, b40c1f9, bf4f6de)は**全てmain上に存在**。
- `git status --short`: 282件変更。大半は`er0XX_output/`生成物・
  `docs/pm/`新規ファイル・`.claude/`設定などのuntracked。Production
  コード/Promptの未commit変更は無し。`CLAUDE.md`(運用ドキュメント、
  sandwich-pm節追加)のみ未commit。

---

## 12. 提案Handoff判定: HANDOFF_VALIDATED

理由:
- 資料が主張した主要事項(Status Matrix、User Decisions、Trial History、
  OPEN-112/113/114の状態)は、いずれもrepo側のSSOT・Git・commit本文と
  **概ね一致**しており、真のCONFLICTは発見されなかった。
- 資料が「未確認」としていた2点(OPEN-112-07の実施有無、OPEN-114の
  実登録有無)はいずれも**repo照合により解消(実施・登録済みと確認)**できた。
- 一方で、資料には無かった新規発見(OPEN-83関連の発音判定基準
  APPROVED未配線、Gate体系の完全な不在、「1記事ずつ完結」原則の
  SSOT不在)があり、これらはSSOT追加候補・ユーザー判断事項として
  Fable/ユーザーへ個別に提示する必要がある。
- 現存する未決事項はOPEN-112の1行(7論点)に集約されており、
  この解消はユーザー判断が必要(USER_DECISION_REQUIRED)。
  Handoff自体をBLOCKする性質のものではない。

**HANDOFF_BLOCKEDに該当する事項は無い。ただしOPEN-112のUDR解消と、
本レポートで新規発見した2件(OPEN-83未配線、Gate体系のSSOT不在)は、
次工程着手前にユーザーへ明示すべき事項としてFableへ引き継ぐ。**

---

## 13. 次タスクへ進めるか(Gate 6相当の観点)

- 未処理UDR: OPEN-112(1件、7論点)。→ユーザー判断待ちとして次工程
  (News Focus Module Prompt具体文言のTrial設計等)着手前に提示要。
- APPROVED未配線: OPEN-83関連の発音判定基準(1件、新規発見)。
  → Blockingではない(non-blocking、Human Reviewで安全側運用継続中)が、
  ユーザーへ報告要。
- SSOT記録漏れ: Gate体系・「1記事ずつ完結」原則など、CHATGPT_ONLY_
  CANDIDATE一覧(§7)。→ SSOTへの追加要否はユーザー判断(本タスクでは
  追加していない)。
- 無断追加Trial: 発見なし。
- Trial/DEV誤認: 発見なし(No18/OPEN-113ともにPRODUCTION_WIREDの
  runtime evidenceがrepo記述として存在)。

**結論: blocking itemなし。ただしOPEN-112のUDR7論点・OPEN-83未配線・
Gate体系不在の3点はユーザー明示defer済みではないため、次工程着手前に
ユーザーへ提示することを推奨する。**
