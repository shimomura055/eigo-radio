## 管理ID

PROJECT-DELIVERY-SPEED-PARALLELIZATION-RULE-01(委任_01: 「開発時間最小化・並列実行原則」をProject運用SSOTへ統合反映、Decision Log、Claude Code向け実行ルール、Dangling Reference確認、commit/push、PRODUCTION_WIRED判定材料の提示。¥0)。並行タスク: OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01 委任_05b(E2E実行中。`er052_output/open233_prod_e2e_02/`・`er052_output/open233_prod_e2e_01/`・`OPEN_ITEMS.md`[同管理ID行の進捗1文]・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`を編集・commit予定)。**本委任は上記ファイルを編集しない・addしない。** 本委任の編集対象: `docs/pm/PM_GOVERNANCE.md`、`CLAUDE.md`、`DECISION_LOG.md`、`docs/pm/PM_BRIEF.md`、`docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md`、`docs/pm/REPORT_LEDGER.md`、`docs/pm/RESULT_PACKET_RULE.md`(新規、本委任の報告先)、`docs/pm/delegation_log/`。git操作は本委任の対象ファイルのみ明示add。`git commit`でindex.lock競合が出たら5秒待って最大3回再試行。

**作業方式(必須)**: `Write`/`Edit`で小分け(1回40行以内)、Bash heredoc不使用。T-0の委任文保存はWriteを3分割して逐語保存。説明は最小限。

## 性質/到達上限Status/禁止事項

- 性質: Project運用ルールのSSOT反映(ユーザー正式採用済み=APPROVED_FOR_PRODUCTION)。到達上限: 本委任完了時点で「SSOT反映・Decision Log反映・運用文書更新・commit/push・参照可能」を満たした場合、**PRODUCTION_WIRED**としてよい(ユーザー指示: 上記まで確認して初めてPRODUCTION_WIRED)。Fableが最終照合する。
- 禁止: 重複文書の新設(既存SSOTへ統合)/既存のQCD・PM Gate・Safety・予算Guardrail・ユーザー承認Gateを弱める記述/コード変更/有料API/`git add -A`・`stash`・`amend`/`ACTIVE_TASK.md`・`RESULT_PACKET*.md`のadd/`CURRENT_SPEC.md`・`OPEN_ITEMS.md`の編集(本件はProduct仕様ではなくPM運用ルールのため、正式SSOTは`docs/pm/PM_GOVERNANCE.md`。OPEN_ITEMSは委任_05bが編集中のため触らない。必要なら追記文案をRESULT_PACKET_RULEに記す)。
- STOP条件(ユーザー指定): 既存Projectルールと重大な矛盾が見つかった場合のみSTOPして報告。通常の統合・重複整理・commit/pushはユーザー判断待ちにせず完了させる。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)該当判定: 非該当(運用文書。処理構造の変更なし)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ逐語で保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果をRESULT_PACKETへ1行記録する(FAILでも作業は継続)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`): TTSを伴う委任は`TTS_EXECUTION_MODE=STANDARD`を明示する。本委任はTTSなし。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5): TTS実行前4点確認。本委任はTTSなし。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`): 本委任は¥0のためCap定型文は適用対象外。

## ユーザー指示(原文、逐語でDECISION_LOGとPM_GOVERNANCEへ記録)

> 管理ID：PROJECT-DELIVERY-SPEED-PARALLELIZATION-RULE-01
> 目的: 今後の開発について、品質・Safety・再現性・予算管理・PM Gateを維持したまま、可能な限り短時間で完了させることを正式なProject運用ルールにする。ユーザーの正式採用判断です。単なる提案ではなく、ProjectルールとしてProduction/開発運用SSOTへ反映すること。
> 正式ルール「開発時間最小化・並列実行原則」: 開発時間は極めて重要なQCD要素として扱う。各タスク開始時に必ず、作業依存関係/クリティカルパス/並列実行可能な作業/所要時間見込み/並列化した場合の短縮見込み、を確認する。
> 原則: 独立して実行できる作業は原則並列化する/実装待ちの間に、先行可能なtest準備・E2E runner準備・集計script・評価基準・review準備・SSOT/報告準備等を進める/E2Eも、順序依存がなく条件同一性・再現性を保てるなら、複数process/workerで並列実行する/評価・ラベル付け・集計・レビューも独立分割できれば並列化する/長時間作業中に新たな短縮余地を発見した場合、ユーザーから指摘されるのを待たず改善する/「順番にやる方が普通だから」という理由だけで直列化しない。
> 並列化しない条件: 以下のような明確な理由がある場合だけ直列化してよい。前工程の出力がないと次工程を開始できない/同じファイル/branch/stateを触り競合リスクが高い/順序依存がある/API rate limit等で並列化が逆効果/再現性や比較条件が崩れる/Safety/品質/予算管理/PM Gateを弱める/runtime evidenceの信頼性を落とす。その場合は、並列化できない理由を短く明示すること。
> 時間見積もり: 主要タスクでは開始時に、全体所要時間見込み/主な工程別見込み/どこを並列化するか/クリティカルパス、を提示する。途中で見込みが大きく変わった場合は更新する。
> QCD上の位置付け: Speedを優先するが、以下は犠牲にしない。Quality/Safety/Production Gate/再現性/runtime evidence/予算Guardrail/user approvalが必要な仕様判断/CURRENT_SPEC / Decision Log / Open Item整合。「早くするために検証を省く」「承認前にProductionへ入れる」は禁止。
> 今回やること: このルールを、既存Project構成を確認した上で適切な正式SSOTへ反映する。最低限、Project運用ルール/Decision Log/必要ならPM/Claude Code向け実行ルール、へ記録する。既存ルールとの重複がある場合は、重複文書を増やさず、正式な既存SSOTへ統合する。
> Dangling Reference Check: 新しいルール名や参照を追加する場合、正式SSOTに定義されているか/Claude Code指示側だけに孤立していないか/既存QCD/PM Gateと矛盾しないか、を確認する。
> Status: ユーザー正式採用済みなので、現在StatusはAPPROVED_FOR_PRODUCTION。今回の作業で、SSOT反映/Decision Log反映/必要な運用文書更新/Git commit/push/実際に次の開発指示/運用で参照可能な状態、まで確認して、初めてPRODUCTION_WIREDとする。
> 受入条件: 正式Projectルールとして記録済み/開発タスク開始時に時間見積もり・並列化検討が必須になっている/独立作業は原則並列化することが明文化されている/並列化しない場合の理由明示が定義されている/Quality/Safety/PM Gateを弱めない制約が明記されている/Decision Log更新済み/Git commit/push済み/Dangling Referenceなし/今後Claudeへの作業指示でこのルールを適用できる状態。
> STOP条件: 既存Projectルールと重大な矛盾が見つかった場合のみSTOPして報告する。通常の文書統合・重複整理・commit/pushはユーザー判断待ちにせず完了させること。

## KPI provenance欄

該当なし(運用文書)。

## Opus台帳更新

該当なし。

## 事前指定Read一覧

1. `docs/pm/PM_GOVERNANCE.md`: Grep `8-X|並列実行原則|並列` →8-X節全体(既存の並列実行原則、2026-09-27ユーザー決定)と8節の見出し構成。Grep `^## 22|22\.|Trial開始前|終了前チェック|次工程Gate` →22節の見出しと冒頭(開始前チェックの既存項目=時間見積の追記先候補)。Grep `^## 2-2|コスト影響評価` →2-2の冒頭(QCDとの関係)。Grep `^## 9-0|9-0` →9-0の冒頭(報告フォーマット、時間見込み提示の報告位置)。Grep `^## 11\.|D-2|委任文標準` →11節D-2の該当箇所(委任文に時間見積・並列化欄を加える際の整合)。
2. `CLAUDE.md`: 全文(短い。「Fableサンドイッチ運用(PM層)」節へClaude Code向け実行ルール1項目を追加する位置の確認)。
3. `docs/pm/PM_BRIEF.md`: L36-L45(並列実行原則の要約段落=更新先)。
4. `docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md`: 全文(111行。「性質/到達上限Status/禁止事項」欄の説明文へ「時間見込み・並列化判断」の記載を求める1文を追加。**固定見出し文字列は変更しない**=`check_delegation_prompt.py`のセクション検出を壊さない)。
5. `docs/pm/tools/check_delegation_prompt.py`: Grep `SECTION|見出し|required` →必須セクション一覧(新セクションを追加しないことの確認。追加せず既存欄内の記述要件とする)。
6. `DECISION_LOG.md`: Grep `PM-PARALLEL|並列実行原則|2026-09-27` →既存の並列実行原則エントリ(ID・結論行のみ、統合時の参照)。末尾の最新エントリ見出し(追記位置)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- `docs/pm/PM_GOVERNANCE.md` 8-X節: 既存「並列実行原則(2026-09-27)」を**本ルールで拡張・統合**する(新節を作らず8-Xを改訂。節名を「8-X. 開発時間最小化・並列実行原則(2026-09-27ユーザー決定、2026-10-06拡張: PROJECT-DELIVERY-SPEED-PARALLELIZATION-RULE-01)」とし、ユーザー原文の「正式ルール/原則/並列化しない条件/時間見積もり/QCD上の位置付け」を逐語で収め、旧文は「旧(2026-09-27)」として併記または統合)。
- 同22節(Trial開始前チェック): 開始前チェック項目へ「時間見積(全体・工程別)・依存関係・クリティカルパス・並列化計画・短縮見込みの提示(8-X)」を1項目追加(主要タスク必須、途中で見込みが大きく変わった場合は更新)。
- 同9-0(報告フォーマット): 「1結論」または「5次の行動・費用」の説明に「主要タスク開始時は時間見込み・並列化計画・クリティカルパスを提示(8-X)」を1文追加。
- 同2-2(コスト影響評価): 「開発時間はQCDの重要要素として評価対象に含める(8-X)」を1文追加。
- 同11節D-2(委任文標準): 「委任文の性質欄に、主要タスクでは時間見込みと並列化判断(並列化しない場合はその理由)を記す」を1文追加。
- `docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md`: 「性質/到達上限Status/禁止事項」欄の説明に「主要タスクでは時間見込み(全体・工程別)と並列化判断[並列実行する作業/直列化する場合の理由]を1〜2行で記す(PM_GOVERNANCE 8-X)」を追加。「Fable自己チェック」へ「- [ ] 時間見込み・並列化判断あり(主要タスク)」を追加。固定見出しは不変。
- `CLAUDE.md`「Fableサンドイッチ運用(PM層)」節末尾の箇条書きに1項目追加(開発時間最小化・並列実行原則の要約、正本は`docs/pm/PM_GOVERNANCE.md` 8-X節、全文は複製しない)。
- `docs/pm/PM_BRIEF.md` L41-L44の並列実行原則段落を更新(2026-10-06拡張の要点と8-X参照)。
- `DECISION_LOG.md`: 末尾の最新エントリ直後に本管理IDの新エントリ(3回のEditに分割): (a)見出し+Status、(b)ユーザー指示原文、(c)反映先一覧+既存ルールとの統合+Dangling Reference確認結果+Fable判断欄(空欄)。
- `docs/pm/REPORT_LEDGER.md`: 末尾に1行追記(2026-10-06 | PROJECT-DELIVERY-SPEED-PARALLELIZATION-RULE-01 委任_01 | ...、Fable判定: [記入])。
- Dangling Reference Check: (1)新ルール名がPM_GOVERNANCE 8-Xに定義/(2)CLAUDE.md・PM_BRIEF・テンプレートからの参照先が8-Xで実在/(3)既存QCD(2-2)・PM Gate(1〜7)・22節・11-3 Opus Gate・7-6予算Capと矛盾しない/(4)`check_delegation_prompt.py`の必須セクションを変えていない(既存委任文1件でPASS維持を確認)。結果を表でRESULT_PACKET_RULEへ。
- 既存ルールとの矛盾チェック: 「Sonnet委任は1管理IDあたり初回+修正3回」(並列委任の数え方=並列の初回委任は1回と数える旨を8-Xに注記、上限自体は不変)、「複数Agentの並列起動は8節の条件を満たす場合のみ可」(8-Xの「並列化しない条件」と対応付け)、「Opus任意レビュー1日2回」(不変)。重大矛盾があればSTOP、軽微な整合は注記で解消。

## 実行コマンド全文

1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_PROJECT-DELIVERY-SPEED-PARALLELIZATION-RULE-01_01.md --json-out docs\pm\delegation_log\2026-10-06_PROJECT-DELIVERY-SPEED-PARALLELIZATION-RULE-01_01.md_check.json`
2. 上記Edit(小分け)。
3. テンプレート変更後の検証: 同scriptを`docs\pm\delegation_log\2026-10-06_OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01_04.md`へ実行(`--json-out ..._check_recheck.json`、addしない)。
4. `git status --porcelain`→本委任対象のみ明示add→commit→push(index.lock競合時は5秒待って最大3回再試行)。

## SSOT追記文

上記「追記位置の手順」のとおり。OPEN_ITEMSへの行追加が必要と判断する場合は文案のみRESULT_PACKET_RULEに記す(本委任では編集しない)。

## Git

明示add対象のみ: `docs/pm/PM_GOVERNANCE.md`、`CLAUDE.md`、`DECISION_LOG.md`、`docs/pm/PM_BRIEF.md`、`docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md`、`docs/pm/REPORT_LEDGER.md`、本委任文(+`_check.json`)。委任_05bのファイル・`OPEN_ITEMS.md`・`ACTIVE_TASK.md`・`RESULT_PACKET*.md`はaddしない。
コミットメッセージ: `PROJECT-DELIVERY-SPEED-PARALLELIZATION-RULE-01: 開発時間最小化・並列実行原則(ユーザー正式採用)をPM_GOVERNANCE 8-X(2026-09-27原則を拡張統合)/22/9-0/2-2/11 D-2・委任テンプレート・CLAUDE.md・PM_BRIEFへ反映、DECISION_LOG記録、Dangling Referenceなし(委任_01、¥0)`
SSOT編集権: あり(`docs/pm/PM_GOVERNANCE.md`/`DECISION_LOG.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/PM_BRIEF.md`/`CLAUDE.md`/テンプレート)。`CURRENT_SPEC.md`・`OPEN_ITEMS.md`は編集しない。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_RULE.md`へ: 1. T-0結果。2. 反映箇所一覧。3. 既存ルールとの統合内容と矛盾チェック結果。4. Dangling Reference Check表(4項目)。5. 受入条件9項目の充足表。6. `check_delegation_prompt.py`再検証結果。7. commit hash・push結果・raw URL。8. 一覧外Read理由。9. PRODUCTION_WIRED判定の材料。最終報告は12行以内。

