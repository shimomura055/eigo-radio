## 管理ID

PM-GOVERNANCE-SSOT-SERIALIZATION-RULE-01(新規、ユーザー正式採用)+ KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01 / PRONUNCIATION-RESOLUTION-PHASE-4-A2-FALLBACK-WIRING-AND-ASR-ENTITY-LIKE-01 のStatus同期(Fable Gate 3判定済み)。¥0、コード変更なし。一時ファイル `docs/pm/ACTIVE_TASK_GOV1.md` / `docs/pm/RESULT_PACKET_GOV1.md`(commitしない)。**本タスクがSSOT 4点(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`)+`docs/pm/PM_GOVERNANCE.md` を編集する唯一のAgent**(他のSonnet 3件はコード/REPORTのみ)。ただしKP 4+1 Phase B Agentが終盤でSSOTを触る可能性があるため、開始時と各commit直前に `git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/REPORT_LEDGER.md docs/pm/PM_GOVERNANCE.md` で差分所有者を確認し、自分以外の差分があるファイルはaddしない(最大10分待機→解消しなければそのファイル分は文案をRESULT_PACKETへ残して未適用で報告)。

## 性質/到達上限Status/禁止事項

- 性質: ガバナンス正式ルール追記+Status文字列同期。到達上限Status: PM_GOVERNANCE追記はユーザー正式採用済み(`APPROVED`)、Status同期はFable判定済みの `PRODUCTION_WIRED` を転記。
- 費用: ¥0。API呼び出しなし。
- 禁止: コード変更、`git add -A`、履歴書き換え、他Agentの差分の巻き込み。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 下記「実行コマンド全文」のtranscript退避コマンドを実行する。
T-0: 受領した委任文を `docs/pm/delegation_log/2026-09-28_PM-GOVERNANCE-SSOT-SERIALIZATION-RULE-01.md` へ保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_PM-GOVERNANCE-SSOT-SERIALIZATION-RULE-01.md --json-out docs/pm/delegation_log/2026-09-28_PM-GOVERNANCE-SSOT-SERIALIZATION-RULE-01.md_check.json` を実行、結果1行記録。
T-2: TTSなし。T-3: 費用上限¥0。

## ユーザー指示(原文)

「3. SSOT直列化ルール 正式採用します。PM_GOVERNANCEへ以下を正式ルールとして反映してください。- SSOT 4点の編集は1 Agentずつ直列化 - 他Agentの未commit差分が存在するファイルを git add しない - commit前に対象ファイルの差分所有者を確認 - 並列Agentが同一SSOTファイルを同時編集しない 再発が2回あるため、単なる運用注意ではなく正式な再発防止ルールとして記録してください。」(2026-09-28、ユーザー正式承認)

## 事前指定Read一覧

- `docs/pm/PM_GOVERNANCE.md` 8節(Grep `^## 8` → 節末尾まで。並列Agent条件の既存記述)と 11節 D-2(:1775-1808)
- `docs/pm/REPORT_LEDGER.md`: Grep `KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01` / `PRONUNCIATION-RESOLUTION-PHASE-4` の行
- `CURRENT_SPEC.md`: Grep `Sonnetは\`PRODUCTION_WIRED\`を宣言しない` と `Phase 4` の該当行(Source Reference Contract行、固有名詞読み解決節Phase 4行)
- `KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01_REPORT.md` §11 Gate 3表(Grep `PRODUCTION_WIRED`)、`PRONUNCIATION-RESOLUTION-PHASE-4-A2-FALLBACK-WIRING-AND-ASR-ENTITY-LIKE-01_REPORT.md` Gate 3表(Grep `PRODUCTION_WIRED`)
- 巻き込み事故の一次記録: `docs/pm/delegation_log/2026-09-28_KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01_03.md`(Grep `混入`)、`docs/pm/RESULT_PACKET_FLX2.md`:105-115、`docs/pm/RESULT_PACKET_ASRO.md`(Grep `6b0e792d`)

## 事前指定Grep一覧+追記位置・更新位置の手順

1. PM_GOVERNANCE 8節末尾へ新小節「8-x. SSOT編集の直列化ルール(2026-09-28、`PM-GOVERNANCE-SSOT-SERIALIZATION-RULE-01`、ユーザー正式採用、再発防止ルール)」を追記: (a) SSOT 4点(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`)および `docs/pm/PM_GOVERNANCE.md` の編集は同時に1 Agentのみ(Fableは委任時にSSOT編集権を持つAgentを1件に限定し、他の並行AgentにはSSOT追記文案をRESULT_PACKETへ書くよう指示する)。(b) 他Agentの未commit差分が存在するファイルは `git add` しない。(c) commit前に `git status --porcelain <対象ファイル>` と `git diff <対象ファイル>` で差分所有者を確認し、自分の編集以外が含まれる場合はaddしない(最大10分待機→解消しなければ文案をRESULT_PACKETへ残し未適用で報告)。(d) 並列Agentが同一SSOTファイルを同時編集しない。(e) 背景: 2026-09-28に3回(commit `3d9a28be`にKPS1のCURRENT_SPEC/DECISION_LOG編集が混入、`8bb1518c`系でREPORT_LEDGER、`6b0e792d`にASRO行が混入)、いずれも内容は正しく実害なし・履歴書き換えなしだが、ファイル単位 `git add` は他Agentの編集途中を構造的に巻き込むため運用注意ではなく正式ルールとする。(f) 11節 D-2 テンプレートの「Git」欄に「SSOT編集権の有無」を明記する運用(テンプレ本文 `docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md` の「## Git」欄へ1行追記)。
2. DECISION_LOG新規エントリ `## PM-GOVERNANCE-SSOT-SERIALIZATION-RULE-01: SSOT編集直列化ルール正式採用(2026-09-28)`(ユーザー指示原文・背景3件・ルール内容・根拠path)。
3. Status同期(Fable Gate 3判定、2026-09-28): 
   - `docs/pm/REPORT_LEDGER.md` の KP contract行 Status を `PRODUCTION_WIRED`(Family X配線+Family Z共通仕様、Z runner未配線)へ、Phase 4行 Status を `PRODUCTION_WIRED`(Ledger surface条件はDEFERRED/NOT_ADOPTED)へ更新。
   - `CURRENT_SPEC.md` の該当行の「Sonnetは`PRODUCTION_WIRED`を宣言しない(最終判定はFable/ユーザー)」等の文言を「**Fable Gate 3判定: `PRODUCTION_WIRED`(2026-09-28、根拠: Opus L2所見反映 `9fa6f388`+SSOT反映 `b2736e13`/`b63fb35d`、既定backendやFamily Z runnerは未変更)**」へ更新(Phase 4も同様、根拠 `535bb391`/`f8d5887c`+OPEN-208登録)。
   - 両REPORTのGate 3表「`PRODUCTION_WIRED`最終判定」行を「Fable判定 `PRODUCTION_WIRED`(2026-09-28)」へ更新。
   - DECISION_LOG に短い判定エントリ(2 ID分、1エントリにまとめて可)。
   - OPEN_ITEMS: 関連OPEN(OPEN-202/206/207/208)のStatusは変更しない(継続監視項目のため)。
4. `docs/pm/OPEN_ITEMS.md` へ新規OPEN 1件: 「Flash-Lite -01 のOpus L2所見がREPORTへ逐語保存されず失われた(Fable側の転記漏れ、`TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02_REPORT.md` §9注記参照)。以後Opus所見は受領直後に逐語保存する運用(F-1既存ルールの徹底)」、Status `CLOSED`(記録即Close)。

## 実行コマンド全文

- transcript退避(F-1恒久手順): `.venv\Scripts\python.exe docs/pm/tools/collect_subagent_transcripts.py --apply --only-task-ids a2286905b6ad3e6df,a6766c1a2bab065a4,a619d97da468044a9,ae36e39ba5f70d0be,ab0cf09c5b58d6a8a,a3d33e539e99608b3,ae79148c7483d8bc9,af13a9e4c92c882db,a49103463801b89f6`(必要な `--tasks-dir`/`--subagents-dir`/`--transcripts-dir` は `docs/pm/delegation_log/2026-09-28_PM-CHECK-LUNA-TEST-AND-TRANSCRIPTS-01.md` に記録された前回の実行例に倣う。session id `f1538907-8efe-486d-9790-ef5c6cd789fa`。既定の上限20MB、超過見込みなら `--max-total-mb 40` で再実行し記録)。退避先 `docs/pm/transcripts/` の新規ファイルをcommitに含める。
- 検証: `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_PM-GOVERNANCE-SSOT-SERIALIZATION-RULE-01.md --json-out docs/pm/delegation_log/2026-09-28_PM-GOVERNANCE-SSOT-SERIALIZATION-RULE-01.md_check.json`

## SSOT追記文

上記1〜4のとおり(本タスクが直接適用)。

## Git(明示add対象・コミットメッセージ・trailer)

- add対象: `docs/pm/PM_GOVERNANCE.md`、`docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md`、`CURRENT_SPEC.md`、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/REPORT_LEDGER.md`、2 REPORT、delegation_log+`_check.json`、`docs/pm/transcripts/` 新規分。各ファイルは差分所有者確認後にのみadd。
- コミットは2つに分ける: (1) `PM-GOVERNANCE-SSOT-SERIALIZATION-RULE-01: SSOT編集直列化ルールを正式採用(ユーザー承認)+transcript退避9件`(trailer `Management-ID: PM-GOVERNANCE-SSOT-SERIALIZATION-RULE-01`)、(2) `KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01 / PRONUNCIATION-RESOLUTION-PHASE-4: Fable Gate 3判定 PRODUCTION_WIRED をSSOT/REPORTへ同期`(trailer `Management-ID: KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01`)。`git push origin main`。

## 報告(RESULT_PACKET項目)

T-0結果/適用箇所一覧(ファイル・見出し・行)/差分所有者確認の結果(待機の有無)/未適用があればその文案/transcript退避結果/commit hash 2件/raw URL(PM_GOVERNANCE、CURRENT_SPEC、DECISION_LOG、OPEN_ITEMS、REPORT_LEDGER)。
