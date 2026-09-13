管理ID: PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01(+PM-CLOSEOUT-CONSOLIDATION-117)
性質: ユーザー正式採用(`APPROVED_FOR_PRODUCTION`、2026-09-13)に基づく**PM運用ルールのProduction配線(Gate 3)**。¥0、API呼び出しなし。Productionコード(er0*)は無編集。並行中のTrialタスク(`FAMILY-A-DISCOVERY-*`、`er011_*`、`EDITORIAL-FUTURE-*`、`er013_*`)のファイルには触れない。`git index.lock`があれば10秒待ち最大3回。

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: transcript退避は完了後Fable側で実施する。Sonnet/Opusは対応不要。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
---

## ユーザー承認(原文、DECISION_LOGへ記録)
> 施策1: 作業効率化ルール こちらはユーザーが正式採用を決定しました。したがってStatusはAPPROVED_FOR_PRODUCTIONとして扱い、ここはTrial継続ではなく、PRODUCTION_WIREDまで完了させてください。正式運用ルールとして、委任文標準へ少なくとも以下を組み込んでください。事前指定Read一覧/事前指定Grep一覧/追記位置・更新位置の手順/実行コマンド全文/Fable側のコマンド引数漏れ・Grep指定不足を防ぐチェック。ただし、単に文書へ追記しただけでPRODUCTION_WIREDとはしません。以下をすべて確認してください。実際の標準委任経路へ反映/次回委任で自然に適用される状態/Trial専用scriptや一時指示だけに存在しない/必要なRegression・validator・governance check PASS/runtimeまたは実委任での発火証拠/CURRENT_SPEC更新/DECISION_LOG更新/OPEN_ITEMSのclose・update/必要なGit commit・push/Dangling Referenceなし/ユーザー承認内容と実際の運用が一致。上記が揃うまでPRODUCTION_WIREDと判定しないでください。もし実委任によるruntime evidence取得が今回直ちに不可能なら、その項目だけを明確に未完として残し、PRODUCTION_WIREDとはせず報告してください。

## 事前指定Read一覧
- `docs/pm/templates/DELEGATION_READ_EFFICIENCY_BLOCK.md`(全文、1回)
- `PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-TRIAL-DESIGN-01_REPORT.md`: 「Trial arm」「計測指標」の節のみ(Grep `^## `で位置特定→該当範囲)
- `docs/pm/tool_uses_trial_log.md`(全文、1回)
- `docs/pm/tools/measure_delegation_task.py`(Grep `argparse|add_argument`の行のみ。CLI仕様を新ツールで揃えるため)

## 事前指定Grep一覧+追記位置手順
1. `docs/pm/PM_GOVERNANCE.md`: Grep `-n` `E-1|D-1|G-1|11節|^## 11` で11節のE-1/D-1/G-1段落の終端を特定→その直後に新小節「D-2 委任文標準(2026-09-13ユーザー正式採用、PRODUCTION_WIRED判定は本節末尾のGate 3表参照)」を追記。既存文の削除禁止。
2. `docs/pm/PM_BRIEF.md`: Grep `-n` `委任|delegation|E-1` で委任に関する箇所を特定→「Fableは全委任文を`docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md`に従って作成し、Sonnet/Opusは受領した委任文を`check_delegation_prompt.py`で検証して結果をRESULT_PACKETに記録する」を1段落追記。
3. `CURRENT_SPEC.md`: Grep `-n` `PM_GOVERNANCE|サンドイッチ|Fable` で PM運用への参照箇所(あれば)を特定→その直後に1行「PM委任文標準(D-2、`docs/pm/PM_GOVERNANCE.md` 11節、2026-09-13 PRODUCTION_WIRED/またはAPPROVED_FOR_PRODUCTION[Gate 3結果に応じて])」を追記。参照箇所がなければ末尾の運用節へ1行。
4. `OPEN_ITEMS.md`: Grep `-n -o` `^\| OPEN-1[0-9][0-9] \|.{0,120}` で `Token|token|tool_uses|TOKEN-EFFICIENCY|効率` を含む既存OPENの有無を確認(該当があればその行末尾へ追記、なければ最大番号+1で新規行を起票し本タスクでStatusを確定)。あわせて棚卸し補正: OPEN-133/142/146の各行末尾400字を`-o`で取得し、最新Statusが「今ユーザー判断が必要」か「既決/defer/WIRED」かを記録(編集しない)。
5. `DECISION_LOG.md`: Grep `-n` `^## PM-CLOSEOUT-CONSOLIDATION-116|^## 参照元`(本文追記位置=`## 参照元`直前)、索引行は`CONSOLIDATION-116`索引行の直後。

## 実装(新規ファイル)
A. `docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md`: 委任文の標準テンプレ。必須セクション(見出し文字列を固定): 「管理ID」「性質/到達上限Status/禁止事項」「固定ブロック(E-1/D-1/G-1/F-1/T-1、DELEGATION_READ_EFFICIENCY_BLOCK.mdの本文をそのまま)」「ユーザー指示(原文)」「事前指定Read一覧」「事前指定Grep一覧+追記位置・更新位置の手順」「実行コマンド全文(引数実値を含む。『同上』『前回と同じ』『<引数>』等のプレースホルダ禁止)」「SSOT追記文(そのまま使用)」「Git(明示add対象・コミットメッセージ・trailer)」「報告(RESULT_PACKET項目)」「Fable自己チェック(送信前): □Read一覧に行範囲/Grepパターンあり □追記位置手順あり □コマンドに引数実値あり □禁止事項・費用上限あり □並行タスク衝突回避あり」。
B. `docs/pm/tools/check_delegation_prompt.py`: 委任文テキスト(ファイルまたはstdin)を検証し、必須セクション見出しの有無、E-1/D-1/G-1/F-1ラベル、プレースホルダ語(同上/前回と同じ/前回同様/<引数>/TBD)の混入、「実行コマンド全文」節内の各コマンド行に`--`引数または絶対パスが含まれるか、を判定してPASS/FAIL+理由をJSONと人間可読で出力。終了コードはFAILでも0(ブロッキングではなく記録用)。`--help`あり。
C. `docs/pm/tools/check_delegation_prompt_test_01.py`: 合格例(本委任文をそのまま保存したもの)・不合格例(Grep一覧欠落、プレースホルダ混入)のunit test。`run_project_regression.py --pattern "check_delegation*"`→PASS確認、最後にdefault全件1回。
D. **runtime evidence(実委任)**: 本委任文自体を`docs/pm/delegation_log/PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01.md`に保存し、Bで検証してその出力を`docs/pm/delegation_log/..._check.json`として保存(実委任での初回発火証拠)。あわせて`docs/pm/templates/DELEGATION_READ_EFFICIENCY_BLOCK.md`の固定ブロックに「T-0: 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行、結果をRESULT_PACKETへ1行記録(FAILでも作業は継続)」を追加(以後の全委任で自然に発火する経路)。
E. `docs/pm/tools/README.md`(なければ新規、あれば追記)にツール3件の用途と使い方。

## Gate 3チェック(結果を表で。1項目でも未充足なら`APPROVED_FOR_PRODUCTION`[配線実装済み・未充足項目明記]、全充足で`PRODUCTION_WIRED`)
1 実際の標準委任経路へ反映(PM_GOVERNANCE 11節D-2+PM_BRIEF+テンプレ)/2 次回委任で自然に適用(固定ブロックT-0+PM_BRIEF記載)/3 Trial専用・一時指示だけに存在しない(templates・tools・governanceに恒久配置)/4 Regression・validator・governance check PASS(C+全件回帰)/5 runtimeまたは実委任での発火証拠(D)/6 CURRENT_SPEC更新/7 DECISION_LOG更新/8 OPEN_ITEMS close・update/9 Git commit・push/10 Dangling Referenceなし(新規ツール・テンプレの相互参照パスが実在、旧名参照なし)/11 ユーザー承認内容と実運用の一致(5項目[Read一覧/Grep一覧/位置手順/コマンド全文/チェック]がテンプレ+検証器に対応)。

## SSOT追記文
- DECISION_LOG `## PM-CLOSEOUT-CONSOLIDATION-117(2026-09-13)`: ユーザー承認原文(上記)+実装場所一覧+Gate 3表の結果+Status(`PRODUCTION_WIRED`または`APPROVED_FOR_PRODUCTION`+未充足項目)+施策1 Trial最終数値(6arm中央値28、Before比▲44%、Sonnet側手戻り0、Fable側委任文不備4件→本標準で防止)。索引行1行。
- OPEN_ITEMS: 手順4で確定した行に同内容の要約+Status。
- CURRENT_SPEC: 手順3の1行。
- `docs/pm/tool_uses_trial_log.md`末尾: 「2026-09-13 ユーザー正式採用→配線(CONSOLIDATION-117)、Trial終了」。

## 実行コマンド全文
- `python docs/pm/tools/check_delegation_prompt.py --help`
- `python docs/pm/tools/check_delegation_prompt.py --file "C:\Users\tensh\eigo-radio\docs\pm\delegation_log\PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01.md" --json-out "C:\Users\tensh\eigo-radio\docs\pm\delegation_log\PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01_check.json"`
- `python run_project_regression.py --pattern "check_delegation*"`
- `python run_project_regression.py`
- `python docs/pm/tools/collect_subagent_transcripts.py --help`→表示引数で退避: taskId `a4368e132f7f81b1d`(tasks dir=`C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\tasks`、subagents dir=`C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\subagents`)
- `git status --porcelain`

## Git
明示`git add`: `docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md`、`docs/pm/templates/DELEGATION_READ_EFFICIENCY_BLOCK.md`、`docs/pm/tools/check_delegation_prompt.py`、`docs/pm/tools/check_delegation_prompt_test_01.py`、`docs/pm/tools/README.md`、`docs/pm/delegation_log/`(新規2件)、`docs/pm/PM_GOVERNANCE.md`、`docs/pm/PM_BRIEF.md`、`CURRENT_SPEC.md`、`OPEN_ITEMS.md`、`DECISION_LOG.md`、`docs/pm/tool_uses_trial_log.md`、`docs/pm/transcripts/`追加分。`-A`/`stash`/`amend`禁止、他の未追跡差分(Trial系)を含めない。コミットメッセージ`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01: 委任文標準(D-2)のProduction配線+検証器+実委任evidence(CONSOLIDATION-117)`、末尾に
```
Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01THnbjj6FiMbJtrKdFteoE4
```
`git push origin main`まで(拒否時はエラー原文を報告し回避しない)。

## 報告
`docs/pm/RESULT_PACKET_W1.md`(20行以内): Gate 3表(11項目の充足/未充足)、最終Status、実装場所、runtime evidenceパスと検証結果、テスト件数、SSOT追記位置、commit hash/push、棚卸し補正(OPEN-133/142/146の最新Status)、一覧外操作の有無。最終メッセージ8行以内。
