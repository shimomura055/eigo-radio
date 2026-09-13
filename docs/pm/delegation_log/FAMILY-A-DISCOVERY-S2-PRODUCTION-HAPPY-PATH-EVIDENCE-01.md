## 管理ID

FAMILY-A-DISCOVERY-S2-PRODUCTION-HAPPY-PATH-EVIDENCE-01
並行タスク衝突確認: 並行してEDITORIAL-FUTURE-FAMILY-C-V6-…(er013_*とer013_output/のみ、Git操作なし、ACTIVE_TASK/RESULT_PACKET.md不使用)が走る。本タスクはer003_*/er011_output/SSOT/docs/pmを扱い、er013_*に触れない。Git操作は本タスクのみ。RESULT_PACKETは`docs/pm/RESULT_PACKET_S2H.md`(新規)。`docs/pm/ACTIVE_TASK.md`は本タスクが固定ヘッダ付きで上書きしてよい。

## 性質/到達上限Status/禁止事項

- 性質: Production正常系runtime evidence取得(Gate 3最終項目)。Discovery S2は`APPROVED_FOR_PRODUCTION`済み・配線済み(commit 3080105f)で、ユーザーは既存テーマ「Why Do We Wake Up Just Before the Alarm?」のS2生成記事を読み**記事品質の人間評価PASS**と判断済み。残る未確認は「Production正式関数で通常Ledgerを使い記事が最後まで正常完走した実データ証跡0本」の1点のみ。到達Status: 正常完走なら**PRODUCTION_WIRED(正式受入可)**、完走できなければ`PARTIAL`(理由・証跡付き)。
- **禁止(ユーザー明示)**: 新しい改善Trial/新しいPoint設計/Focus変更/多様性改善/Prompt追加調整/コード仕様変更。目的は正常完走証拠の取得のみ。改善案を見つけても実装せず「Open Item候補」としてRESULT_PACKETに報告のみ。
- 実行対象: Production正式関数`er003_discovery_focus_staged_production_01.run_one_pattern_staged_discovery_focus()`を、前回evidence run(`er011_output/discovery_s2_production_runtime_evidence_01/`)と同じ薄いdriver方式(monkeypatch・再実装なし)で呼ぶ。Ledgerは**通常Ledger**(`er011_output/discovery_generalization_wake_before_alarm_trial_12/research/`のverified_fact_ledger.txt・topicをread-only再利用、改変なし)。レベルA2、1本。
- 費用: **開発・検証費**としてDiscovery残額¥88.31内、1本上限¥60。1本目がセットアップ起因(コード/引数ミス、API障害)で不発の場合のみ2本目可(合計¥88.31を超えない)。1本目がモデル挙動起因でfail-closed(NG)した場合は追加生成せずPARTIALで報告。
- 禁止操作: `git add -A`/`.`/`stash`/`clean`/`amend`/`rebase`/`force push`。`run_project_regression.py --pattern`は`_test`を含むglobのみ(ハーネスに拒否ガードあり)。PATH上の素`python`不可。
- STOP条件: 費用上限到達/Production関数の実行に仕様変更が必要と判明(→USER_DECISION_REQUIRED、コード変更しない)。

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

> Discovery残額¥88.31内で、Production正式関数 `run_one_pattern_staged_discovery_focus()` を使い、通常LedgerでA2記事1本を最後まで正常完走させるruntime evidence を取得してください。目安費用: 開発・検証費: ¥40〜60。今回から費用表記を必ず以下に分離してください。開発・Trial / 検証費/量産時1記事あたり単価。
> 正常完走で最低限確認するもの: Production正式path使用/Focus/Stage 1 Main Story/Stage 1 QA/Stage 2 Role Planning/Stage 3 Points/Evidence Compression/Point Overlap / Value QA/final Fact Checker/Ledger Deviation/Local Rewrite / diff QA(発火しなければ未発火でよい)/Directional Precheck/最終記事出力/actual model_id / routing/fail-openではなく正式OKで完走/Trial/DEVファイルへの依存0
> 正常完走した場合のみ、PM側でPRODUCTION_WIREDを正式受入れ可能な状態にしてください。
> Discoveryの追加仕様変更は禁止。新しい改善Trial/新しいPoint設計/Focus変更/追加多様性改善/Prompt追加調整を勝手に始めないでください。それ以外の新規改善案を見つけた場合は、Open Item候補として報告のみしてください。

## 事前指定Read一覧

1. `FAMILY-A-DISCOVERY-S2-PRODUCTION-WIRING-01_REPORT.md` L94-140(前回runtime evidenceの実行方法・driver・出力構成)。
2. `er011_output/discovery_s2_production_runtime_evidence_01/`: Glob `*.py`と`*.json`(最上位のみ)→driver script(存在すれば)全文と`cost_summary.json`(費用集計形式の再利用)。driverが別置きならGrep `run_one_pattern_staged_discovery_focus` を`er011_output/discovery_s2_production_runtime_evidence_01/`と`*.py`(root)で行い、該当driverを特定してRead。
3. `er003_discovery_focus_staged_production_01.py`: Grep `^def run_one_pattern_staged_discovery_focus|^def |^[A-Z_]+ = ` → 関数シグネチャ・戻り値dict構造・定数(`STAGE1_MAX_REGENERATIONS`等)の該当範囲のみRead。
4. `docs/pm/PM_GOVERNANCE.md`: Grep `15-5|5区分` → 費用報告5区分の定義範囲のみRead。
5. `docs/pm/PM_BRIEF.md` L133-157(ACTIVE_TASK固定ヘッダ書式)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 出力先: `er011_output/discovery_s2_production_runtime_evidence_02/`(新規)。driverは前回と同じ薄いrunnerを`er011_output/discovery_s2_production_runtime_evidence_02/run_happy_path_a2.py`として置く(rootに新規Production風ファイルを増やさない)。保存物: `reader_facing_article.txt`、`audit/stage_trace.json`(各Stage・QAの実行順とverdict)、`raw_usage_log.jsonl`、`cost_summary.json`、`index.html`(記事本文+Stage/QA表+費用表)、Point Overlap/Value QA・Fact Checker・Ledger Deviation・Directional Precheckの各生JSON。
- `OPEN_ITEMS.md`: Grep `^\| OPEN-135 ` → 行末尾へ追記(下記SSOT追記文①)。
- `DECISION_LOG.md`: Grep `PM-CLOSEOUT-CONSOLIDATION-124` で直近エントリ位置・索引書式を確認 → 直後に新エントリ(②)+索引1行。
- `CURRENT_SPEC.md`: Grep `Discovery Focus S2` → 当該節末尾に1段落追記(③、Statusを正常完走証跡付きでPRODUCTION_WIRED確定と記載。完走しなかった場合は追記せずRESULT_PACKETに理由のみ)。
- `docs/pm/MODEL_ROUTING_TRIAL_LOG.md`: Grep `discovery_s2_production_runtime_evidence_01` → 直後に本run 1行追記。
- Dangling Reference再確認: Grep `er011_discovery_focus|er011_discovery_stage3` を `er003_discovery_focus_staged_production_01.py` と driver で実行し、import 0件を記録。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\FAMILY-A-DISCOVERY-S2-PRODUCTION-HAPPY-PATH-EVIDENCE-01.md --json-out docs\pm\delegation_log\FAMILY-A-DISCOVERY-S2-PRODUCTION-HAPPY-PATH-EVIDENCE-01_check.json`
2. 事前確認(¥0): `.venv\Scripts\python.exe -m pytest er003_discovery_focus_staged_production_01_test_01.py -q`(期待24 passed)
3. 本run: `.venv\Scripts\python.exe er011_output\discovery_s2_production_runtime_evidence_02\run_happy_path_a2.py`(driver内で`editorial_mode="discovery_focus_staged"`・level=a2・Ledger/topicパスは上記通常Ledgerの絶対/相対パス実値・出力dir実値を固定し、費用上限¥60で停止するガードを入れる)
4. Git確認: `git status --porcelain` / `git diff --stat`

## SSOT追記文

① OPEN-135末尾: 「(FAMILY-A-DISCOVERY-S2-PRODUCTION-HAPPY-PATH-EVIDENCE-01、2026-09-14) ユーザーがS2生成記事(Why Do We Wake Up Just Before the Alarm?)を読み記事品質の人間評価PASS。Production正式関数`run_one_pattern_staged_discovery_focus()`+通常LedgerでA2 1本を<正常完走/未完走>(出力`er011_output/discovery_s2_production_runtime_evidence_02/`、model_id=<実値>、各Stage/QA verdict=<要約>、Local Rewrite/diff QA=<発火/未発火>、Directional Precheck=<実値>)。開発・検証費¥<実費>(Discovery残額¥88.31→¥<残>)。量産時1記事あたり単価(A2、本run実測ベース、retry込み/除き)=¥<値>(B1は未確定)。Status: <PRODUCTION_WIRED(正式受入可)/PARTIAL>。」
② DECISION_LOG新エントリ: 「2026-09-14: FAMILY-A-DISCOVERY-S2-PRODUCTION-HAPPY-PATH-EVIDENCE-01。ユーザー人間評価PASS(記事)を受け、正常系runtime evidence取得。結果<…>。追加仕様変更なし(ユーザー指示)。Open Item候補<あれば列挙/なし>。」
③ CURRENT_SPEC「Discovery Focus S2」節末尾(完走時のみ): 「2026-09-14 正常系runtime evidence(`er011_output/discovery_s2_production_runtime_evidence_02/`)で通常LedgerによるA2完走を確認し、Gate 3全項目充足によりPRODUCTION_WIRED確定。」
- <>は実値で埋める。

## Git(明示add対象・コミットメッセージ・trailer)

- 明示add: `er011_output/discovery_s2_production_runtime_evidence_02/`配下(記事txt・json・html・driver。音声等大容量なし想定)、`FAMILY-A-DISCOVERY-S2-PRODUCTION-HAPPY-PATH-EVIDENCE-01_REPORT.md`(新規root)、`OPEN_ITEMS.md`、`DECISION_LOG.md`、`CURRENT_SPEC.md`(完走時)、`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`、`docs/pm/delegation_log/FAMILY-A-DISCOVERY-S2-PRODUCTION-HAPPY-PATH-EVIDENCE-01.md`+`_check.json`、`docs/pm/RESULT_PACKET_S2H.md`。er013_*・無関係既存差分はaddしない。
- コミットメッセージ: `FAMILY-A-DISCOVERY-S2-PRODUCTION-HAPPY-PATH-EVIDENCE-01: Discovery S2 Production正式関数の正常完走runtime evidence(A2)+SSOT更新` の後に空行、末尾に
  `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`
  `Claude-Session: https://claude.ai/code/session_01THnbjj6FiMbJtrKdFteoE4`
- `git push origin main`。classifierブロック時は同一コマンドを最大3回まで再試行、それでも失敗なら報告(回避操作禁止)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_S2H.md`に: 1) 到達Status(PRODUCTION_WIRED正式受入可/PARTIAL)、2) ユーザー指定16確認項目を1つずつ「✓/✗/未発火+証跡(ファイル・値)」、3) 最終記事(語数・出力パス)、4) 各QA verdict(Stage 1 QA、Overlap/Value QA各attempt、final Fact Checker、Ledger Deviation、Local Rewrite/diff QA発火有無、Directional Precheck)、5) actual model_id/routing/reasoning_effort(raw_usage_log実値)、6) 費用を**開発・検証費**(本run実費、API別+5区分)と**量産時1記事あたり単価**(A2、本run実測から算出、retry込み/除き両方、B1未確定と明記)に分離、Discovery残額、7) Gate 3 14項目の最終照合表(前回REPORTの表を更新)、8) Dangling Reference 0件、9) Open Item候補(あれば、実装せず)、10) commit hash・push結果、11) T-0結果・事前指定外Read・STOP有無、12) ACTIVE_TASK固定ヘッダ更新済み。root REPORTに詳細。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり
- [x] 並行タスク衝突回避あり
