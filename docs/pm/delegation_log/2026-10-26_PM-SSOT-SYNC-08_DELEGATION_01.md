## 管理ID

PM-SSOT-SYNC-08(FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01 Closeout: Fable判定PRODUCTION_WIREDのSSOT反映。API 0・JPY0)。並行タスク衝突確認: 並行Agent 1件(TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 委任_02[read-only統合、SSOT編集権なし])。**SSOT編集権は本Agentのみ**(`CURRENT_SPEC.md`/`OPEN_ITEMS.md`/`DECISION_LOG.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`docs/pm/ACTIVE_TASK.md`)。これ以外は編集しない。git index.lock競合時は10秒待って再実行(最大3回)。

## 性質/到達上限Status/禁止事項

- 性質: SSOT転記。到達上限Status: 転記完了。転記内容のStatusはFable判定どおり。
- 禁止: Production/コード変更、API支出、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。編集前に`git diff HEAD --stat -- <path>`で差分なしを確認(差分があればHEAD blob+自hunk方式)。pathspec付きcommit。
- 費用/日次: JPY0。
- Opus独立技術レビューGate(11-3): 非該当(転記。配線は候補表の読み取り専用データ追加+固定Voice値変更で新機構なし=条件A非該当、採用はユーザー決定済み=条件C非該当)。
- 時間見込み: 約30分。並列化: なし。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし)
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。

T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_PM-SSOT-SYNC-08_DELEGATION_01.md` をN=661から順に試し、先頭が「## 管理ID」+「PM-SSOT-SYNC-08」で始まるものを採用(`--index -1`不可)。

## ユーザー指示(原文)

ユーザー決定原文=`docs/pm/delegation_log/2026-10-26_FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01_USER.md` §1(Y表採用・Z不変・差分許容・既存完成音声は差し替えない・Trial問題の記録)、§6(PRODUCTION_WIRED判定条件9項目)。Grep `APPROVED_FOR_PRODUCTION|PRODUCTION_WIREDの判定条件` で該当箇所を確認し逐語引用。

## Fable判定(転記する内容。文言はこのまま使う)

**FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01 = PRODUCTION_WIRED(2026-10-26、Fable判定。ユーザー承認=APPROVED_FOR_PRODUCTION 2026-10-26)**
- 承認仕様: Family Y Voice候補表 男性1 Puck/2 Schedar/3 Fenrir/4 Orus/5 Iapetus、女性1 Zephyr/2 Kore/3 Leda/4 Sulafat/5 Erinome。AlgiebaはY候補から除外。固定割当 Voice 1=Puck(旧Algieba)、Voice 2=Zephyr、Voice 3=Schedar(不変)。Family Z Voice表は不変(Z男性1=Algieba、Z男性5=Puck)。Y/Z差分は承認済みFamily固有仕様。既存の完成音声は差し替えず、今後の制作に適用(本記事の完成版制作はユーザー別指示により実施中)。
- 実装: `er121_family_y_structure_01.py` `Y_DIALOGUE_VOICE_POOL`(読み取り専用データ、選定機構の新設なし)・`FIXED_VOICE_SLOTS` Voice 1=Puck・`verify_voice_assignment`をY表pool参照へ(旧: Z表との一致要求=Yを Puckにすると STOPする構造を是正)。commit 31c41ea76。
- test: 新規`er121_family_y_voice_table_test_01.py` 9件(表一致・Algieba除外・Voice 1=Puck・Z表不変とY/Z差分・メロスpin不変・Production経路にAlgieba残存なし・run_01/公開ページ不変)、既存test 3箇所更新、er121回帰 306 PASS/1 skip、接続試行0。
- runtime evidence(正式CLI `er121_family_y_runner_01.py`、新規run dir `er121_output/family_y_production_01/redelivery_fee/run_voice_puck_ev_01`、公開なし): Std `y_voice_1`=voice Puck・model gemini-3.8-flash-lite-tts・STANDARD・attempt 1・ASR NORMALIZED_MATCH・slowdown 5.967%・41.698秒。Adv `y_voice_1`=voice Puck・同model・backend speech_metadata_flash_lite・attempt 1・ASR EXACT_MATCH・Repetition旗なし・39.52秒。同引数再起動2回でAPI 0(cost_log 5行・spent_jpy 2.511不変)。Y style profile gate a2/b1b PASS、key_phrase_source_gate 3/3、組立 A2 342.261秒/B1 315.85秒(clippingなし)。旧Algieba cache非復活=`er121_family_y_audio_01.py:191-212 voice_guard_cached`(要求Voice不一致entryを破棄)。`EVIDENCE_01.md`/`EVIDENCE_02.md`。
- 費用: 実費2.511円(Std 1.3459+Adv等1.17、Guardrail 60)。
- 運用逸脱(記録): 委任_01で起動手順ミス(`--theme-package`漏れrc=2→Std成功→Adv rc=3、300秒内3起動)により自己発動RESTART_STORM。原因把握・課金異常なしのためFable許可で`--clear-stop`(17:29:12、reason記録)。以後150秒規律順守。
- Trial問題の記録(OPEN-533追記): Algieba=Repetition旗率72%・take最終OK率38%(平均2.31 attempt/take)に対し、Puck=Trial fresh 24/24・平均1.21 attempt/take、本番runtime Std/Advとも1 attempt(n=2、継続観察)。
- 新規OPEN(11-8分類=修正へ進む・非blocking): 「Y Voice 1の旧人間承認記録(`human_approved_segments.json`、scope=this single segment/this attempt only)が残っていると、Voice変更後の再生成がHUMAN_APPROVEDでスキップされる、または旧音声が新Voice表示(`y_tts_voice_requested`無条件刻印)で組立に通る恐れ」(FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01 委任_01 `PLAN_01.md`で発見、実測=承認残存で`proceed=False HUMAN_APPROVED`)。対処方針=承認記録をVoiceと紐付けて照合するY側guard(別委任)。本記事の完成版制作では承認記録の扱いで回避。
- PRODUCTION_WIRED判定条件(ユーザー§6 9項目): 1承認仕様一致○/2正式初回経路実装○/3 retry・fallback・regeneration・resume整合○(再起動API 0+voice_guard_cached)/4正式runtime発火証拠○(Std/Adv)/5 Regression・Validator test PASS○/6 actual model_id・routing○/7 SSOT更新=本syncで完了/8 Git○(31c41ea76、50e6e7673)/9未承認仕様・Dangling Referenceなし○。

## KPI provenance欄

該当なし(転記。出典=`docs/pm/RESULT_PACKET_YVT1.md`・`RESULT_PACKET_YVT2.md`・`docs/research/FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01/EVIDENCE_01.md`・`EVIDENCE_02.md`・`docs/research/FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01/PLAN_01.md`)。

## Opus台帳更新

該当なし。

## 事前指定Read一覧

- `docs/pm/RESULT_PACKET_YVT2.md`: Grep `SSOT文案|^\*\*10` → ±15
- `docs/pm/RESULT_PACKET_YRF1.md`: Grep `重大所見|HUMAN_APPROVED|OPEN` → ±10(新規OPEN文案の根拠)
- `docs/pm/ACTIVE_TASK.md` 全文
- `CURRENT_SPEC.md`: Grep `Family Y Voice候補表` → 該当節全体(SYNC-06で新設。Status行を更新)

## 事前指定Grep一覧+追記位置・更新位置の手順

- `CURRENT_SPEC.md` 「Family Y Voice候補表」節: Status=「APPROVED・配線中」→「PRODUCTION_WIRED(2026-10-26 Fable判定)」へ。実装・test・evidence要約・Trial問題・既存音声不差し替えの行を追記。
- `OPEN_ITEMS.md`: Grep `OPEN-531` → Status=CLOSED(PRODUCTION_WIRED、Voice 1=Puck)。Grep `OPEN-533` → Puck実績追記。Grep `^\| OPEN-53[0-9]` → 最大番号確認し次番号(OPEN-535想定)で新規OPEN(上記)。
- `DECISION_LOG.md`: 本日末尾に1件。
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `OPEN-531` → 「PRODUCTION_WIRED反映済み(2026-10-26)」。
- `docs/pm/REPORT_LEDGER.md`: FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01=Fable報告予定、FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01 委任_01=完了(委任_02へ)、本件。
- `docs/pm/ACTIVE_TASK.md`: 上書き(並行=TTS-RETRY…委任_02(JPY0)、次=FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01 委任_02(制作、Y-F01確認後)、UDR-blocking=OPEN-526・527・529(区分2)・534、STOP条件=猿の手run_fzcw_e1_01残置、QDC=当日約552円/1,000)。

## 実行コマンド全文

- `git diff HEAD --stat -- CURRENT_SPEC.md OPEN_ITEMS.md DECISION_LOG.md docs/pm/REPORT_LEDGER.md docs/pm/USER_DECISION_REGISTER_01.md`(編集前)
- `git diff --cached --stat`
- Secret grep: `git diff --cached -- CURRENT_SPEC.md OPEN_ITEMS.md DECISION_LOG.md docs/pm/REPORT_LEDGER.md docs/pm/USER_DECISION_REGISTER_01.md | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

上記Fable判定の文言をそのまま使う。

## Git(明示add対象・コミットメッセージ・trailer)

- add対象: `CURRENT_SPEC.md`、`OPEN_ITEMS.md`、`DECISION_LOG.md`、`docs/pm/USER_DECISION_REGISTER_01.md`、`docs/pm/REPORT_LEDGER.md`、`docs/pm/delegation_log/2026-10-26_PM-SSOT-SYNC-08_DELEGATION_01.md`(+`_check.json`)。pathspec付きcommit。ACTIVE_TASK/RESULT_PACKETはaddしない。
- commit message: `PM-SSOT-SYNC-08: Family Y Voice候補表(Voice 1=Puck) Fable判定PRODUCTION_WIRED(CURRENT_SPEC・OPEN-531 CLOSED・OPEN-533追記・新規OPEN[Voice変更時の旧承認記録]・DECISION_LOG・UDR・報告台帳、API 0)`
- trailer: `Delegation: PM-SSOT-SYNC-08/01`
- push: `git push origin HEAD:main`(non-ffなら`git fetch origin`→`git merge --no-edit origin/main`→push。競合はSTOPし報告)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_SSOT8.md`: (0)T-0、(1)編集前状態、(2)更新行(ファイル:行)、(3)`git diff --cached --stat`、(4)commit hash・push・raw URL(CURRENT_SPEC.md/OPEN_ITEMS.md/DECISION_LOG.md)、(5)必須4行+「判定整合: 重大NG=<なし|あり>」、(6)一覧外Read。末尾に要約5行以内。