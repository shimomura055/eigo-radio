## 管理ID

FAMILY-A-DISCOVERY-S2-PRODUCTION-WIRING-01
並行タスク衝突確認: 同時にEDITORIAL-FUTURE-FAMILY-C-V5-…(er013_*のみ触る、Git操作なし、`docs/pm/ACTIVE_TASK.md`/`docs/pm/RESULT_PACKET.md`を触らない)が走る。本タスクはer011_*/er003_*/er010_*/SSOT/docs/pmを扱い、er013_*には一切触らない。RESULT_PACKETは`docs/pm/RESULT_PACKET_S2W.md`(新規、本タスク専用)へ書く。`docs/pm/ACTIVE_TASK.md`は本タスクが固定ヘッダ付きで上書きしてよい(PM_BRIEF「ACTIVE_TASK固定ヘッダ」書式)。

## 性質/到達上限Status/禁止事項

- 性質: Production配線(Gate 3)。ユーザーはDiscovery S2設計(`FAMILY-A-DISCOVERY-S2-PRODUCTION-DESIGN-01_REPORT.md`推奨案)を**APPROVED_FOR_PRODUCTION**として正式承認済み。到達目標Statusは**PRODUCTION_WIRED**。Gate 3の全項目(下記14項目)のうち1項目でも未確認ならPRODUCTION_WIREDと宣言せず`PARTIAL`(未達項目を列挙)で報告する。
- 採用内容(ユーザー確定、変更不可): 分割方式P1(Discovery専用新関数をopt-in追加、既存`run_one_pattern`は無変更)/`STAGE1_MAX_REGENERATIONS=1`/Fact Checker FAIL locus=案(ii)簡略ルール(Stage2-3 exhaustion後のみStage1へ)/Trial専用実装はProduction正式側へ移設し暫定importを残さない/Gate 3 runtime evidenceとしてStage 1 escalation実発火を実データ1本で確認。
- 正式処理順(変更不可): Focus解決 → Stage 1 Main Story生成+Stage 1 QA → Stage 2 Point Role Planning(確定Main Story本文を入力、角度hintなし) → Stage 3 Point生成+Evidence Compression → 結合 → Point Overlap/Value QA → 記事全体Fact Checker/Ledger/Local Rewrite/差分QA(OPEN-141 diff QA、既定ON) → Directional Precheck。通常retryではMain Storyを固定しStage 2-3のみ再実行。Main Story自体に重大問題があり既存安全装置でも解消できない場合のみStage 1再生成(上限1回)。Main Story固定原則の例外はLocal Rewrite等既存安全装置による局所修正のみ。
- 費用: runtime evidence用の実データ生成はDiscovery残額¥134.97内。1本あたり上限¥60、本数は原則1本。2本目は「1本目がセットアップ起因(コード/引数ミス)で不発だった」場合のみ許可し、合計¥120を超えない。モデル挙動起因でescalationが発火しなかった場合は追加生成せず、その事実を証跡付きで報告する(PRODUCTION_WIREDにはしない)。
- 禁止: 既存`run_one_pattern`本体の挙動変更(P1違反)/News Major・Daily・Trend Synthesis・現行Discovery非staged経路の出力変更/新テーマの選定(テーマ・LedgerはS2 Trialで再利用したものと同一を再利用する)/`git add -A`・`git add .`・`stash`・`clean`・`amend`・`rebase`・`force push`/er013_*ファイルへの一切の変更/PATH上の素`python`での回帰実行。
- STOP条件(USER_DECISION_REQUIREDとして報告し、それ以上進めない): (1)P1を守ったまま実装できず既存`run_one_pattern`の変更が不可避と判明、(2)設計REPORTの処理順・retry単位と矛盾する既存仕様がCURRENT_SPEC/コードに見つかり仕様変更が必要、(3)費用上限到達、(4)回帰・テストFAILが本タスク起因で解消できない。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
---

## ユーザー指示(原文)

> ユーザーは、提示した推奨設計で**Production実装へ進むことを正式承認**しました。したがってStatusを**APPROVED_FOR_PRODUCTION**へ変更し、ここからは**PRODUCTION_WIREDまで完了させてください。** 採用内容は前回推奨案です。分割方式: P1/STAGE1_MAX_REGENERATIONS: 1/Fact Checker FAIL locus: 案(ii)簡略ルール/Trial専用実装はProduction正式側へ移設し、暫定importを残さない/Gate 3 runtime evidenceとして、Stage 1 escalation実発火を実データ1本で確認
> 正式処理順は、Focus解決→Stage 1 Main Story生成+Stage 1 QA→Stage 2 Point Role Planning(確定Main Story本文を入力、角度hintなし)→Stage 3 Point生成+Evidence Compression→結合→Point Overlap / Value QA→記事全体Fact Checker / Ledger / Local Rewrite / 差分QA→Directional Precheck です。通常retryではMain Storyを固定し、Stage 2-3のみ再実行してください。Main Story自体に重大問題があり、既存安全装置でも解消できない場合のみStage 1再生成を許可します。
> Production wiringではGate 3をすべて満たしてください。Production正式初回経路へ実装/retry / fallback / regeneration整合/DEV / Trial専用依存なし/runtime実発火/Regression / Validator / integration test PASS/actual routing / model等必要evidence/CURRENT_SPEC更新/DECISION_LOG更新/OPEN_ITEMS close / update/必要なcommit / push/Dangling Referenceなし/ユーザー承認内容と実挙動一致。1項目でも未確認ならPRODUCTION_WIREDとしないでください。Gate 3 runtime evidenceのTrial費用は、前回見積どおりDiscovery残額内で1本実施して構いません。

## 事前指定Read一覧

1. `FAMILY-A-DISCOVERY-S2-PRODUCTION-DESIGN-01_REPORT.md` L27-232(1〜9節: 分割設計P1、正式処理順、retry単位、Main Story固定原則仕様文案、locus案(ii)、既存QA整合表、競合・共通化、Dangling Reference、Gate 3準備[テスト一覧・runtime evidence計画])。
2. `er011_discovery_focus_s2_full_trial_01.py` 全文(移設元。構造変更対象のため全文Read可)。特にL116-161(import群・SOURCE_TRIAL_DIR/SOURCE_LEDGER_PATH・load_reused_ledger_and_topic)、L215-400(run_stage1_main_story_writer/run_ledger_local_rewrite_loop/run_stage1_qa)。
3. `er011_discovery_focus_s2_full_trial_01_test_01.py` 全文(22テスト、うちGenerateArticleStageBranchTests 6ケースをProduction関数名へ移植する土台)。
4. `er011_discovery_focus_part_a_standalone_trial_01_run.py`: Grep `^def (run_stage2_role_planning|run_stage3_points_writer|assemble_article|extract_stage1_main_story)`→各関数の定義範囲をRead(移設元)。
5. `er011_discovery_stage3_rule_adjustment_trial_09.py`: Grep `CURRENT_FOCUS_BLOCK`→定義範囲のみRead(Focus Module Part A本文、`EDITORIAL_TYPE_MODULE_BLOCKS`へ正式登録する内容)。
6. `er003_v1_n3_01_articles_generate.py` L440-500(`EDITORIAL_TYPE_MODULE_BLOCKS`/`resolve_editorial_type_module_block`/COMMON_BLOCK組立)とL818-1248(`run_one_pattern`本体。無変更のまま、共通ヘルパー呼び出し位置・Fact Checker/Ledger/diff QA/Directional Precheckの呼び出しシグネチャ確認用)。加えてGrep `editorial_mode`でCLI/呼び出し側の受け渡し位置を特定し該当範囲Read。
7. `er010_ledger_local_rewrite_09.py`: Grep `^def (locate_target_sentence|run_diff_qa_for_accepted_rewrite|apply_diff_qa_to_resolved_rewrite)`→シグネチャ+docstringのみRead。
8. `er011_output/discovery_focus_s2_full_trial_01/cost_summary.json` と `e2e_run_summary_partial_a2.json`(S2 Trial実測費用・Stage1 escalation発火有無・使用モデルの比較基準)。
9. `docs/pm/PM_GOVERNANCE.md`: Grep `Gate 3`→Gate 3チェックリスト定義範囲のみRead(14項目の正式文言と照合するため)。
10. `docs/pm/PM_BRIEF.md` L133-157(ACTIVE_TASK固定ヘッダ書式)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- `CURRENT_SPEC.md`: Grep `Discovery Focus|OPEN-135|FAMILY-A-DISCOVERY` → 既存Discovery関連節の末尾を特定し、その直後に新節「## Discovery Focus S2(Production、FAMILY-A-DISCOVERY-S2-PRODUCTION-WIRING-01、2026-09-13)」を追加(処理順・retry単位・`STAGE1_MAX_REGENERATIONS=1`・locus案(ii)・Main Story固定原則[設計REPORT4節の仕様文案を採用]・opt-in `editorial_mode`値・Trial専用ファイルはarchive残置でProduction importなし、を記載)。既存の他節は編集しない。
- `OPEN_ITEMS.md`: Grep `^\| OPEN-135 ` → 該当行の末尾へ追記(下記SSOT追記文)。行の既存内容は削除しない。
- `DECISION_LOG.md`: Grep `^## |^### ` で直近エントリの位置と索引行の書式を確認 → 直近エントリの直後に新エントリ、索引には1行追加(既存書式に従う)。
- `docs/pm/MODEL_ROUTING_TRIAL_LOG.md`: Grep `S2|discovery_focus_s2` → 直近行の直後にruntime evidence run 1行(実使用モデル・費用)を追記。
- Dangling Reference Check: Grep `er011_discovery_(focus|stage3)` を対象 `er003_*.py`・新規Production側モジュール・`er010_*.py`・`er012_*.py` で実行し、Production経路からTrialファイルへのimport/参照が0件であることを証明(結果をRESULT_PACKETへ件数で記載)。

## 実行コマンド全文

(すべてリポジトリroot `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\FAMILY-A-DISCOVERY-S2-PRODUCTION-WIRING-01.md --json-out docs\pm\delegation_log\FAMILY-A-DISCOVERY-S2-PRODUCTION-WIRING-01_check.json`
2. 新規テスト単体: `.venv\Scripts\python.exe -m pytest <新規テストファイル名> -q`(新規テストファイル名は実装時に確定した実ファイル名を使用。例 `er003_discovery_focus_s2_production_test_01.py`)
3. 関連回帰: `.venv\Scripts\python.exe run_project_regression.py --pattern "er003*"` および `.venv\Scripts\python.exe run_project_regression.py --pattern "er011*"`
4. 全件回帰(1回): `.venv\Scripts\python.exe run_project_regression.py`(基準: 直近CONSOLIDATION時点2557件中2554 PASS・既知無関係差分3件[harness自己診断1件+`er003_test_p2j_investigate`既存2件]。これ以外の新規FAILは本タスク起因として扱う)
5. runtime evidence run: Production正式入口(`er003_v1_n3_01_articles_generate.py`のCLIまたは正式呼び出し関数)から新`editorial_mode`値でA2 1本を生成。テーマ・LedgerはS2 Trialの`SOURCE_TRIAL_DIR`(`er011_discovery_focus_s2_full_trial_01.py` L129-130で定義)と同一のものを再利用し、Stage 1 escalationを実発火させるため設計REPORT9節の「意図的にMAJORを発生させるLedger」を`er011_output/discovery_s2_production_runtime_evidence_01/research/`配下へ生成(元Ledgerは無編集)。出力先: `er011_output/discovery_s2_production_runtime_evidence_01/`。費用ログ(`raw_usage_log.jsonl`・`cost_summary.json`)、Stage別summary(escalation発火・regeneration回数・使用モデル・reasoning_effort・各QA verdict・diff QA発火有無・Directional Precheck結果)、`reader_facing_article.txt`、`index.html`を保存。実行コマンド(引数実値)はRESULT_PACKETへ記録すること。
6. Git状態確認: `git status --porcelain` / `git diff --stat`。

## SSOT追記文

- OPEN-135末尾追記: 「(FAMILY-A-DISCOVERY-S2-PRODUCTION-WIRING-01、2026-09-13) ユーザー正式承認により`APPROVED_FOR_PRODUCTION`(分割方式P1/`STAGE1_MAX_REGENERATIONS=1`/locus案(ii)/Trial専用実装の正式移設/runtime evidence 1本)。配線結果: <PRODUCTION_WIRED または PARTIAL(未達項目)>。実装先<モジュール名>、opt-in `editorial_mode="<値>"`、既存`run_one_pattern`無変更(バイト不変テストPASS)、Dangling Reference 0件、runtime evidence <出力dir>(Stage 1 escalation発火<有/無>、費用¥<実費>)。Discovery残額¥134.97→¥<残額>。」
- DECISION_LOGエントリ: 「2026-09-13: FAMILY-A-DISCOVERY-S2-PRODUCTION-WIRING-01。ユーザー正式承認(APPROVED_FOR_PRODUCTION)に基づきDiscovery S2をProduction正式経路へ配線。採用: P1/STAGE1_MAX_REGENERATIONS=1/locus案(ii)/正式移設。結果: <Status>、Gate 3 14項目照合結果、runtime evidence、費用、commit。詳細は`FAMILY-A-DISCOVERY-S2-PRODUCTION-WIRING-01_REPORT.md`。」
- CURRENT_SPEC新節: 上記Grep手順のとおり。
- 上記の<>は実値で埋める。PRODUCTION_WIREDに未達の場合はSSOTにもPARTIALと未達項目を正直に書く(PRODUCTION_WIREDと書かない)。

## Git(明示add対象・コミットメッセージ・trailer)

- 明示`git add`対象のみ: 新規/変更したProduction側モジュール、新規テストファイル、`er003_v1_n3_01_articles_generate.py`(変更した場合)、`FAMILY-A-DISCOVERY-S2-PRODUCTION-WIRING-01_REPORT.md`(新規、root)、`CURRENT_SPEC.md`、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`、`docs/pm/delegation_log/FAMILY-A-DISCOVERY-S2-PRODUCTION-WIRING-01.md`、同`_check.json`、`er011_output/discovery_s2_production_runtime_evidence_01/`配下の証跡(記事txt・summary json・cost json・index.html・改変Ledger。音声等の大容量ファイルは含めない)。
- 他タスクの変更ファイル(er013_*、docs/pm/RESULT_PACKET_FC5.md等)は絶対にaddしない。`git add -A`/`.`禁止。
- コミットメッセージ: `FAMILY-A-DISCOVERY-S2-PRODUCTION-WIRING-01: Discovery S2段階生成(P1 opt-in)のProduction配線+runtime evidence+SSOT更新` の後に空行、末尾に
  `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`
  `Claude-Session: https://claude.ai/code/session_01THnbjj6FiMbJtrKdFteoE4`
- `git push origin main`。push失敗(権限・classifier・conflict)時はforceせず失敗内容を報告。`index.lock`エラー時は並行タスクではない(並行タスクはGit操作しない)ため、10秒待って1回だけ再試行し、それでも失敗なら報告(lockファイルは削除しない)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_S2W.md`(新規)に以下を記載。root REPORT `FAMILY-A-DISCOVERY-S2-PRODUCTION-WIRING-01_REPORT.md`に詳細。
1. 到達Status(PRODUCTION_WIRED / PARTIAL / USER_DECISION_REQUIRED)と根拠。
2. Gate 3チェックリスト14項目を1項目ずつ「✓/✗+証跡(ファイル・行・テスト名・数値)」で列挙: Production正式初回経路へ実装/retry・fallback・regeneration整合/DEV・Trial専用依存なし/runtime実発火/Regression・Validator・integration test PASS/actual routing・model等evidence/CURRENT_SPEC更新/DECISION_LOG更新/OPEN_ITEMS update/commit・push/Dangling Referenceなし/ユーザー承認内容と実挙動一致(処理順・retry単位・上限値・locusルールをコード行で対応付け)。
3. 実装概要: 新関数名・配置モジュール・opt-in `editorial_mode`値・`EDITORIAL_TYPE_MODULE_BLOCKS`登録内容・移設した関数一覧(移設元→移設先)・既存`run_one_pattern`が無変更である証明(`git diff --stat`でL818-1248に変更なし、またはバイト不変テスト)。
4. テスト結果: 新規テスト件数と結果/`er003*`・`er011*`回帰/全件回帰(件数・PASS数・FAIL内訳と既知3件との照合)。
5. runtime evidence: 実行コマンド全文、使用モデル・reasoning_effort(実ログ由来)、Stage 1 escalation発火の有無と発火ログ、Stage 1再生成回数、Stage 2-3 retry回数、各QA verdict、diff QA発火有無、Directional Precheck結果、記事語数、出力dir、実費(API別)、Discovery残額。
6. Dangling Reference Check結果(Grep件数)。
7. commit hash・push結果。
8. T-0結果1行、事前指定外Read(理由付き)1行ずつ、STOP該当の有無。
9. ACTIVE_TASK.md固定ヘッダを更新済みであること。
Git操作はG-1に従い最小出力で。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり
- [x] 並行タスク衝突回避あり(er013_*不可・RESULT_PACKET分離・並行側Git操作なし)
