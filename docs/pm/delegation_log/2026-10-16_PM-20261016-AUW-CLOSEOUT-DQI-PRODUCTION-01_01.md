## 管理ID

`PM-20261016-AUW-CLOSEOUT-DQI-PRODUCTION-01`(略称DQIP)委任_01(ユーザー指示の全文保存+DQIパッケージP[P1〜P4+重大NG2軸]のPM正式運用への実装[PM_GOVERNANCE/sandwich-pm.md/受入テンプレート/機械Validator+test]+Phase 2机上評価[Day 3・4失敗事例]+AUW Closeout・Family制限・ユーザー判断のSSOT追記文の**下書き作成**)。
**並行委任あり(重要)**: 同時に別Sonnetが`FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01`で`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/ACTIVE_TASK.md`を編集しcommitする。衝突回避のため**本委任ではこれら6ファイルを編集しない・git add/commit/pushを行わない**。これらへの追記文は下書きファイルとして作成し、次の委任_02でFableが適用を指示する。`er0*`配下・Production codeも触らない。

## 前委任の受入記録(Gate 7)
`DECISION-QUALITY-IMPROVEMENT-01` 委任_01〜02(commit `fd0a317e2`): 棚卸し`DQI_INVENTORY_01.md`・提案書`DQI_PROPOSAL_01.md`(パッケージP、Opus独立レビュー原文§8、採否表§9)、Fable受入ACCEPTED(ユーザー判断待ち #88〜#91)。本日ユーザーがパッケージPを`APPROVED_FOR_PRODUCTION`として正式採用(下記原文§2)。

## 性質/到達上限Status/禁止事項
- 性質: PM運用規則の実装(文書)+Validator script実装(`docs/pm/tools/`)+机上評価。到達上限Status: `DQI_P_IMPLEMENTED_DESK_EVALUATED`(PRODUCTION_WIREDはFable独立受入後。Sonnetが判定しない)。
- 禁止: 有料API(LLM呼出含む)、Family A/B/C関連の一切の作業(原文§1-C)、Family Zへの追加調査・改修(§1-B)、AUWの再Trial・再実装・追加改修(§1-A)、Day 5〜6の再開、新しいOpen Item棚卸し、新規運用機構・ファイルの不必要な増設(既存ツール再利用・最小拡張)、上記6ファイルの編集・git操作、Production code変更、Validator結果だけで仕様採用・完了判定すること。
- Opus独立技術レビューGate(11-3): 提案段階でOpus独立レビュー済み(`DQI_PROPOSAL_01.md`§8、OF-DQI-01〜10)。本委任は承認済みパッケージの実装であり、提案書から**設計を変える場合はその差分を明示**する(差分が重要ならFableが再レビューを判断)。
- 時間見込み: 120〜150分。
- 費用/日次: JPY0。承認区分: A(ユーザー承認済み採用の実装)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0: 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2: TTSを伴う委任は`TTS_EXECUTION_MODE=STANDARD`を明示する。(本委任はTTSなし)
T-3: 費用上限[Cap]なし(JPY0)。

T-0保存先(2本・**全文**・要旨化禁止):
(1) 本委任文 → `docs/pm/delegation_log/2026-10-16_PM-20261016-AUW-CLOSEOUT-DQI-PRODUCTION-01_01.md`
(2) 下記`<<<USER>>>`〜`<<<END USER>>>`間を一字も変えずに → `docs/pm/delegation_log/2026-10-16_PM-20261016-AUW-CLOSEOUT-DQI-PRODUCTION-01_USER.md`(先頭に「# ユーザー指示原文(2026-10-16受領、Fable転記)」1行のみ付加可)。文字数を記録。

## ユーザー指示(原文)
<<<USER>>>
# Claude Code／Fableへの正式回答・指示
## 2026-10-16 ユーザー最終判断の反映・DQI実装評価

**管理ID：PM-20261016-AUW-CLOSEOUT-DQI-PRODUCTION-01**

**対象：AUW Closeout／開発対象範囲の固定／DQIパッケージP**

**現在Status**
- AUW：`PRODUCTION_WIRED`（ユーザー正式承認）
- DQI：`APPROVED_FOR_PRODUCTION`
- Family X Coffee：既存の正式指示に従い継続
- Family A／B／C：開発停止

## 1. ユーザー判断の正式記録

以下を2026年10月16日の正式判断として、CURRENT_SPEC・DECISION_LOG・該当OPEN_ITEMS・ユーザー判断台帳へ反映する。

既存の判断記録を重複登録したり、既に承認済みの事項を再度ユーザー判断へ戻したりしない。

### A. AUW（統一ASR判定）

**ユーザーが`PRODUCTION_WIRED`を正式承認。**

- Family X・Zの通常Production生成において、追加指示なしにAUWが自動適用される状態を維持。
- 初回・retry・fallback・regeneration・Local Rewrite後の適用を維持。
- 今回報告されたruntime evidence・test・Git反映をCloseout証跡として紐付ける。
- 承認済みAUWの再Trial・再実装・追加改修は行わない。
- Family Yは将来の開発対象。Yの開発時に正式配線する。現時点では実装しない。

**AUW本体は完了。** 別の改善候補を理由にStatusを後退させない。

### B. Family Zの3件の懸念

Family Cで報告された以下の問題について、ユーザーはFamily Zでの予防的対応を不要と正式判断した。

1. 日本語TTSへの言語指定誤り
2. 原稿の一致を確認しない音声再利用
3. 記号Gateによるコロン検出

**Family Zで実際に問題が発生するまでは、追加調査・Trial・改修を行わない。**

既存のProduction品質Gateは維持する。

### C. 開発対象Familyの制限

**現在の開発対象はFamily X・Z、将来Yのみ。**

Family A・B・Cは開発停止とする。

ユーザーから明示的な依頼がない限り、これらについて以下を禁止する。

- 新規開発・コード修正
- Trial・検証run
- 実音声生成・再生成
- 問題是正
- 調査を名目とした独立タスクの開始
- API費用の発生

AUW等の既存共通コードがA／B／Cから参照されていることと、これらのFamilyの開発を再開することは別である。

共通基盤の変更がA／B／Cの挙動へ影響する場合、勝手に対象を拡張せず、互換性維持と変更範囲を確認すること。

今回Family Cの開発が指示範囲外で進行したことを、スコープ管理上の再発防止事項として記録する。

ただし、この問題を理由にFamily Cの追加調査・改修を開始してはならない。

## 2. DQIパッケージP：正式採用

ユーザーはDQIパッケージPを正式採用した。

**Status：`APPROVED_FOR_PRODUCTION`**

対象はPM自律運営モデル。Family X／Zのコンテンツ生成仕様を変更する指示ではない。

目的：

- 不要なユーザー判断を減らす。
- 承認済み事項を再質問しない。
- 開発側で解決可能な問題をユーザー判断へ回さない。
- 重大NGを見逃して成果物を受け入れない。
- 過剰なSTOPを増やさない。

以下を承認済みパッケージとして扱う。

### P1：受入判定の整合

重大NG、主因、是正対象、STOP理由、ユーザー提示可否を照合する。

重大NGがある場合は、その問題が是正対象またはSTOP理由に必ず含まれること。

重大NGが未解決なら無条件の`ACCEPTED`を禁止する。

不一致がない正常案件では、記録を必要以上に複雑化しない。

### P2：ユーザー判断前の仕分け

ユーザー判断を発行する前に、必ず以下を区別する。

1. **既にユーザーが判断済み**
2. **開発側で解決可能**
3. **現在の依頼とは独立した問題**
4. **本当に新しいユーザー判断が必要**

1は再質問しない。

2は承認済み仕様の範囲内で開発側が是正する。

3は現在の作業を妨げず、ユーザーから依頼されていない独立開発へ展開しない。

4だけを、現在の作業を進めるために不可欠な場合に限りユーザーへ提示する。

**Open Itemに存在することだけを理由に、ユーザーへの判断要求を発行してはならない。**

### P3：ユーザーへの提示制限

判断事項を提示する前に、次を確認する。

- 現在の依頼との直接の関係
- 今判断しなければ進めない理由
- 過去の判断との重複
- 開発側で解決できない理由
- ユーザーが理解するために必要な説明

管理IDやOPEN番号の列挙だけで判断を求めない。

ユーザーが依頼していないOpen Itemの棚卸しや、関連の薄い判断事項の追加提示は禁止。

### P4：機械Validator

**機械Validatorは採用パッケージに含む。省略しない。**

優先するのは被覆チェック。

- 重大NGが是正対象・STOP理由から漏れていないか。
- 受入判定と未解決事項が矛盾していないか。
- 承認済み事項が再度USER_DECISION_REQUIREDになっていないか。
- 現在の依頼と無関係な項目が判断対象に混入していないか。

既存PMツールの再利用・最小拡張を優先する。

初期段階は、DQI提案書どおり非ブロッキングで導入し、誤検出を評価する。

機械判定の結果だけで独断の仕様採用・廃止・Production完了判定は行わない。

### 重大NGの2軸定義

ユーザーはパッケージPを承認しており、この定義もその構成要素として扱う。別途承認を求めない。

**内容品質の重大NG**
- 学習者に重大な誤解を与える意味反転
- 重要Factの欠落
- 学習内容の重大な不一致等

**成果物品質の重大NG**
- 必須音声の欠落
- STOP状態の成果物を完成扱い
- 原稿・記事・音声の取り違え等

過剰STOP防止のため、**厳密には少し異なるというだけでは重大NGとしない。**

既存のPM_GOVERNANCE第23節等との整合を維持する。

## 3. DQIの実装と効果評価

### Phase 1：設計整合・実装

既存のDQI_PROPOSAL_01、PM_GOVERNANCE、sandwich-pm.md、受入テンプレートを照合する。

既存仕様の重複・矛盾を整理したうえで、P1〜P4をPM正式運用へ実装する。

新しい運用機構やファイルを不必要に増やさない。

### Phase 2：評価

**「実装できた」だけで完了扱いにしない。**

評価対象：

1. 承認済み事項の再質問を防げるか。
2. 開発側で解決すべき事項がユーザー判断へ流れないか。
3. 関係のないFamilyやOpen Itemの判断が混入しないか。
4. 重大NGを見逃してACCEPTEDとしないか。
5. 機械Validatorが必要な漏れを検出するか。
6. 誤STOP・過剰なユーザー判断・運用コストが悪化しないか。

まず既存のDay 3・4の失敗事例など、利用可能な記録で無課金検証する。

その結果は、既知の正解を使った机上評価と明示する。

未知ケースでの有効性を実証する必要がある場合は、追加評価の目的・費用・範囲を提示し、承認された範囲で実施する。

**評価不合格の場合、勝手に追加Trialや仕様改善を繰り返さずSTOPする。**

Day 5〜6の保留は維持する。ユーザー判断なしに再開しない。

## 4. 他案件との関係

### Family X Coffee全面再制作

既存管理ID：

`FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01`

こちらの正式指示は変更しない。

- 承認済み仕様のProduction配線
- ResearchからのCoffee全面新規生成
- Writer・KP・TTS等の仕様全件照合
- runtime evidenceと試聴ページ

AUWは既にProductionに組み込まれているため、再実装しない。

DQIのためにCoffee作業を不必要に停止・拡張しない。

独立して進められる範囲では並行可能だが、未承認の仕様変更やGate回避は行わない。

### Family Z

既存Productionを維持する。

今回の報告を契機とした追加改修は不要。

### Family A／B／C

開発再開禁止。

## 5. QCD・作業管理

- 既存仕様・既存コード・既存テストを最大限再利用する。
- 無課金の設計確認・機械テストを優先する。
- 不必要なLLM呼出・再Trial・重複監査を避ける。
- 独立していて安全な作業は並列化してよい。
- ユーザー未承認の対象範囲拡大を禁止する。
- 予算上限・STOP条件を必ず遵守する。
- 今回のDQI導入を理由に、新しいOpen Item棚卸しを始めない。

## 6. Status・Production Wiring Gate

### AUW

ユーザー正式承認済みのため、`PRODUCTION_WIRED`としてCloseout。

既存証跡を参照し、再検証のためだけの有料runは行わない。

### DQI

`APPROVED_FOR_PRODUCTION`から開始する。

以下を確認するまで`PRODUCTION_WIRED`としない。

- P1〜P4の正式運用への反映
- 既存PM運用との整合
- 機械Validatorの実装・テスト
- 必要な評価結果
- 重大NGの2軸定義と過剰STOP防止
- SSOT／DECISION_LOG／必要なOpen Item更新
- commit／push／必要なmerge
- Fable独立受入確認

改善案の実装と、効果が実証されたかは区別して報告する。

## 7. STOP条件

以下はSTOPして報告する。

- 新たなユーザー採用判断が本当に必要になった場合
- 既存の承認済み仕様と衝突する場合
- DQIの評価が不合格となった場合
- 追加Trialが必要となった場合
- Family A／B／Cへの変更が必要となる場合
- 現在の依頼から作業範囲が拡大する場合
- 費用上限・安全Gate・重大品質条件に抵触する場合

ユーザーが明示的に保留した非Blocking事項は、判断要求を再発行せず記録のみ維持する。

## 8. 最終報告

PMが短時間で判断できるよう、以下を報告する。

1. AUWの正式Closeout結果
2. 開発対象Familyの制限が運用上反映されたか
3. DQI P1〜P4の実装内容
4. 機械Validatorの実装・評価結果
5. Day 3・4の失敗事例に対する改善効果
6. 誤STOP・不要な判断・コストの副作用
7. Production正式運用への反映状況
8. Git・SSOT・runtime／test証拠
9. 残るBlocking事項のみ

**報告時、ユーザーに求める判断は本当に必要なものだけに限定する。**

FableはClaude Codeの完了報告を鵜呑みにせず、承認済み仕様・実装・実際の評価結果・QCD・PM Gateと照合して独立受入判定すること。
<<<END USER>>>

## Fableによるユーザー判断の読み取り(REGISTER下書き用、原文逐語引用を付けること)
- #88(DQIパッケージP)・#89(重大NG2軸)・#90(Day3/4遡及机上チェック)・#91(問題1実例の扱い): **判断済み=採用**(§2・§3 Phase 2)。#80〜#82(統合済み)も同じ扱い。
- AUW: ユーザーが`PRODUCTION_WIRED`を正式承認(§1-A)。#85(U3)はユーザー原文に明示なし→Fable読み取り「AUW本体は完了。別の改善候補を理由にStatusを後退させない」に基づき**AUW Closeoutと分離した非Blocking記録**とし、再発行しない(§7末尾)。#93(OPEN-394 Primary層弱点)・#94(OPEN-395)・#95(A7範囲限定)も同様に「承認済みAUWの追加改修は行わない」に該当→記録のみ維持(**判断要求を再発行しない**)。REGISTER下書きではこれらを「記録のみ(2026-10-16§1-A/§7)」へ。
- #92(Family C再利用保証 OPEN-385/387): Family C開発停止(§1-C)により**作業禁止・判断不要**。OPEN-385/386/387は「Family C開発停止(2026-10-16§1-C)。ユーザー明示依頼まで凍結。closeではない」の行内追記を下書き。
- Family Z 3件(§1-B): 予防対応不要。該当Open Item(Family Z向けに起票したものがあれば)に「予防対応不要(2026-10-16§1-B)、実発生まで着手しない」を下書き。
- Family A/B/C開発停止=**新しい運用Guardrail**(PM_GOVERNANCE側へ節追加または既存Scope節へ追記。ユーザー承認済みなので本委任で実装可)。「Family Cの開発が指示範囲外で進行した」の再発防止記録: 事実として、FCJ(`FAMILY-C-JA-TTS-PRODUCTION-FIX-01`)は2026-10-16ユーザー指示Bに基づき実施されたものであることをDL/REPORT_LEDGERで確認し、下書きには「ユーザー指示Bで指示された範囲」と「その後の派生(OPEN-385/387案提示・Family Z懸念3件の提示等)が範囲拡大に当たった」事実関係を、推測を混ぜず記録する(原文が「指示範囲外で進行」と述べている以上、その記載に反論しない。事実関係を証拠付きで並記する)。

## 事前指定Read一覧(D-1厳守)
- `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/dqi/DQI_PROPOSAL_01.md` §3〜§7・§9(パッケージPの正本。P1判定整合行4値、P2 4区分トリアージ[挙証責任・新旧原文競合は新原文優先・Sonnet「判断候補」表記]、P3 K1〜K6、P4非ブロッキングValidator、P5 Opus役割不変)、`DQI_INVENTORY_01.md`(Day 3・4失敗事例の一覧。机上評価のケース集)。
- `docs/pm/PM_GOVERNANCE.md`: Grep `^## 4|^### 4-2|^## 11|^### 11-1|^### 11-6|^## 12|^## 23|^## 9|^### 9-` で節位置→該当節のみRead。既存の受入テンプレート(Grep `受入記録|一致・不一致|是正A|是正B`)。
- `.claude/agents/sandwich-pm.md`: Grep `4-2|受入記録|USER_DECISION_REQUIRED|重大NG`→該当節Read。
- `docs/pm/tools/` 一覧(Glob `docs/pm/tools/*.py`)。`check_delegation_prompt.py`の構造(再利用候補)。RESULT_PACKETの標準見出し(Grep `受入記録` in `docs/pm/RESULT_PACKET*.md`で直近2本)。
- `docs/pm/USER_DECISION_REGISTER_01.md` #80〜#95・FXUD行(Grep `^\| #8[0-9]|^\| #9[0-5]`)。**編集禁止、読むだけ**。
- `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day3/`・`day4/`の失敗事例記録(Glob、見出しGrep)。
- AUW Closeout証跡の所在(参照のみ): `er058_output/unified_all_roles_production_wiring_01/CLOSEOUT_PLAN_07.md` §4-e、`RUNTIME_EVIDENCE_06.md` 見出し、commit `69817ebde`。

## 成果物
A. 運用規則の実装(編集可): `docs/pm/PM_GOVERNANCE.md`(P1〜P4・重大NG2軸・Family対象制限を既存節へ最小追記または新節。23節・4-2・11-1・12節と重複する文は統合し、どちらが正本かを明記)、`.claude/agents/sandwich-pm.md`(4-2受入記録にP1判定整合行[重大NG/主因/是正対象/STOP理由/提示 4値、不一致ゼロなら1行]、UDR発行前P2 4区分トリアージ、P3提示前チェック、Validator実行手順、Family A/B/C禁止)、`.claude/agents/sonnet-worker.md`(「判断候補」表記・RESULT_PACKETへのP1行の記入様式・Family A/B/C禁止。最小追記)、必要なら`.claude/agents/haiku-worker.md`(Validator定型実行を任せる場合の固定手順)。CLAUDE.mdは**編集しない**(必要ならFableへ提案)。
B. 機械Validator: `docs/pm/tools/check_decision_quality.py`(新規1本に限定。既存`check_delegation_prompt.py`の構造・JSON出力様式を踏襲)。入力: RESULT_PACKET(.md)+任意でFable受入記録(.md)。被覆チェック4点(重大NG→是正対象/STOP理由の被覆、ACCEPTEDと未解決重大NGの矛盾、REGISTER判断済み#番号の再UDR化、現在の管理ID/Familyと無関係な項目[Family A/B/C語・他管理ID]の判断欄混入)。非ブロッキング(exit 0、`--json-out`に findings)。`docs/pm/tools/check_decision_quality_test_01.py`(pytest、正例・負例各4点以上)。実行: `.venv\Scripts\python.exe -m pytest docs/pm/tools/check_decision_quality_test_01.py -q`。
C. Phase 2 机上評価: `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/dqi/DQI_DESK_EVAL_01.md`: Day 3・4の失敗事例+本日の実例(FXWA当初UDR9件→5件、AUW #93〜#95、FCJ #92・Family Z懸念3件提示)を**既知正解の机上評価**として、評価対象1〜6ごとに「P適用前の実績/P適用時の期待挙動/Validatorの検出有無(実際に過去RESULT_PACKETへValidatorを走らせた結果)/誤検出」を表にする。合否基準を先に書く(例: 再質問防止=対象事例の全件でP2により区分1へ分類できる、Validator=既知漏れの検出率とFP率)。不合格なら理由を書き**STOP**(改善を繰り返さない)。未知ケース評価の要否・目的・費用(JPY0で可能か)・範囲を提示(実施しない)。
D. SSOT追記文の下書き(編集禁止ファイル用): `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/dqi/SSOT_APPEND_DRAFT_01.md`に、`CURRENT_SPEC.md`(統一ASR判定仕様節末尾「2026-10-16ユーザー正式承認 PRODUCTION_WIRED Closeout(原文逐語)、Family Yは将来」/PM運用節へDQI P APPROVED_FOR_PRODUCTION/Family対象制限)、`DECISION_LOG.md`(本管理ID 委任_01エントリ)、`OPEN_ITEMS.md`(OPEN-385/386/387凍結注記、OPEN-394/395記録のみ、Family Z懸念該当行、AUW関連OPEN-388等の扱い)、`USER_DECISION_REGISTER_01.md`(#80〜#95の更新行)、`REPORT_LEDGER.md`行を、**file名・挿入位置の特定Grepパターン・追記全文**の形で書く(委任_02でそのまま適用できる精度)。
E. `docs/pm/RESULT_PACKET_DQIP1.md`。

## 実行コマンド全文
手順0: `cd C:\Users\tensh\eigo-radio; git fetch origin; git merge --ff-only origin/main`(失敗時=並行委任のcommit中。`git status --short`を確認し**何もせず**続行、Fableへ報告)。
手順1: T-0 2本+check。
手順2: Read→A/B/C/D作成。pytest実行(B)。Validatorを過去RESULT_PACKET(`docs/pm/RESULT_PACKET*.md`の直近5本以上)へ実際に走らせ、結果をCへ。
手順3: `git status --short`で本委任の変更ファイル一覧を取得しRESULT_PACKETへ記載(**add/commitしない**)。secret scanは実施して結果を記録(`--paths`)。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_DQIP1.md`: 1 T-0(2本・文字数・check) / 2 P1〜P4の実装箇所(file:行範囲)と提案書からの差分(なし/あり+理由) / 3 既存規則との重複・矛盾の整理結果(どちらが正本か) / 4 Validator: 仕様・pytest結果・過去RESULT_PACKETへの実走結果(検出/FP) / 5 机上評価の合否(評価対象1〜6ごと)・限界・未知ケース評価の要否 / 6 SSOT追記下書きの所在と件数 / 7 変更ファイル一覧(未commit)・secret scan / 8 逸脱 / 9 費用JPY0・所要 / 10 受入記録5項目(当初目的=原文§2目的5点・§3逐語/最終成果物/証拠/一致・不一致/判定) / 11 **P1判定整合行(本委任自身に適用した初例)**。
