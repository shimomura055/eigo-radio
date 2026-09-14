## 管理ID

EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-02(OPEN-151完成)
並行タスク衝突確認: 並行して Trend完成(`.../trend/`)・Discovery完成(`.../discovery/`)(いずれもGit操作なし)、Family C Trial-09(er013_*/er013_output/、Git操作なし)が走る。本タスクはer012_*(+関連QAモジュールの2V/3V一般化に必要な最小範囲)+新規テスト+`er014_output/four_type_observation_01/voices/`+SSOTを扱い、`er014_output/.../{news,trend,discovery}/`・er013系には触れない・addしない。Git操作は本タスクのみ。RESULT_PACKETは`docs/pm/RESULT_PACKET_VOICES_VAR2.md`(新規)。ACTIVE_TASKは固定ヘッダ付きで上書き可。

## 性質/到達上限Status/禁止事項

- 性質: Production配線(Gate 3)の完成。OPEN-151(2/3 Voices可変Writer、`APPROVED_FOR_PRODUCTION`)は前回PARTIAL(Fable判定)。ユーザー方針(2026-09-14)で以下3点を修正し、可能な限り**PRODUCTION_WIRED**まで進める。1項目でも未確認なら`PARTIAL`のまま(判定条件は下記)。
- **5-1 Comment Contract未接続の修正**: 新規topic 2V/3V正式Production経路(`main_b1_2v()`/`main_b1_3v()`の`write_new_theme`系)から、既存承認済みComment Contract(Comment 1〜4生成・Contract検証)を正しく呼べるよう配線。新Comment仕様は作らない(既存仕様のProduction wiring不足の解消)。retry/fallback/regeneration経路も含めて整合確認。
- **5-2 2VでFact Safety Gateが発火しない問題の修正**: 3V=6区切り/2V=5区切りのため既存3V保守版Fact Safetyゲート(`VOICE_FACT_SAFETY_GATE_MODE_DEFAULT=True`)が2Vで構造的に不発。対応: **Safety判定内容・安全基準は変えず**、2V→5 section parser/3V→6 section parserのように構造読み取りだけを一般化し、判定ロジックは共通のまま2V/3V双方で発火させる。新Safety仕様追加・Gate緩和禁止。
- **5-3 REVIEW_REQUIRED/Leakage flag残存の個別修正**: 2V記事「Is personalized news good for us?」(`er014_output/four_type_observation_01/voices/`)の残存Fact Checker指摘とLeakage flagの原因を確認し、既存rewrite/regeneration/retry/correction経路で直せるものは直し、正式QAを再実行、**cleanな2V runtime evidence**(全Gate/QAがブロックなしで完走、Comment生成・Fact Safetyゲート発火を含む)を取得。5-1/5-2の配線後に、必要なら同Ledgerで2V記事を再生成してよい(Research再実行禁止、Ledger再利用)。「このLeakage/指摘をどうしますか」とユーザーに戻さない。
- **PRODUCTION_WIRED判定条件(ユーザー指定、全て満たすまでPARTIAL)**: (1)2V新規topic正式Production path/(2)3V既存挙動維持/(3)Comment Contractの2V/3V正式path接続/(4)Fact Safety Gateの2V/3V整合/(5)retry・fallback・regeneration整合/(6)Fact attribution整合/(7)cleanな2V runtime evidence/(8)必要な3V regression evidence/(9)actual model_id・routing evidence/(10)CURRENT_SPEC更新/(11)DECISION_LOG更新/(12)OPEN_ITEMS更新/(13)必要Git commit・push/(14)Dangling Reference Check/(15)ユーザー承認内容とProduction挙動の一致。
- 3V regression: 前回のHEAD版バイト不変テスト(`er012_b_family_voices_variable_voice_count_test_01.py`)を維持・拡張(Comment接続・Gate parser一般化後も3V出力が不変であること)。3V実API再生成は不要(オフライン証明が成立しない場合のみ、上限¥100)。
- 費用上限: 2V clean evidence(Comment生成・ゲート込み、必要なら記事再生成1回)¥150、3V再生成(必要時のみ)¥100、合計¥250。
- 禁止: 新Prompt原則・仕様/retry上限変更/Fact Checker・Leakage Gate基準変更/Gate緩和/Schedar本採用格上げ・mode/level命名の新規決定/TTS経路変更/`git add -A`・`.`・`stash`・`clean`・`amend`・`rebase`・`force push`/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`/er003_*・er006_*・er010_*・er013_*の変更/`er014_output/.../{news,trend,discovery}/`のadd。
- STOP条件(ユーザー指定): 新Prompt原則・仕様が必要/retry上限変更が必要/Fact Checker・Leakage Gate基準変更が必要/Gate緩和が必要/構造的に2Vでは既存仕様が成立しない/最終的に人間の品質判断が必要。STOP時は「Claude側で実施済みの対応・残った問題・ユーザーが判断すべき具体的選択肢」を提示。

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

> 5-1. Comment Contract未接続: これは修正してください。新規topic 2V / 3V正式Production経路から、既存承認済みComment Contractを正しく呼べるよう配線してください。新しいComment仕様を作る必要はありません。既存仕様のProduction wiring不足を解消するタスクとして扱ってください。retry / fallback / regeneration経路も含めて整合確認すること。
> 5-2. 2VでFact Safety Gateが発火しない問題: これも修正してください。Fact Safetyの判定内容・安全基準は変えず、2V/3V双方の構造を読めるよう一般化する。新しいSafety仕様を追加しない。Gateを緩和しない。2VだけSafety Gateがスキップされる状態を解消してください。
> 5-3. REVIEW_REQUIRED / Leakage flag残存: ここはClaude側で可能なところまで個別対応してください。残っているFact Checker指摘とLeakage flagの原因を確認/既存rewrite / regeneration / retry / correction経路で直せるものは直す/正式QAを再実行/cleanな2V runtime evidenceを取得。ユーザーに毎回聞かないこと。
> 6. 以下をすべて満たすまでOPEN-151をPRODUCTION_WIREDとしない(15項目)。一項目でも未確認ならPARTIALのまま。
> 最終REPORT(Voices): Comment wiring結果/Fact Safety Gate 2V/3V対応/Leakage・Fact Checker個別修正結果/2V runtime evidence/3V regression/retry・fallback整合/actual model_id/CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS/Git evidence/Dangling Reference Check/最終Status。

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET_VOICES_VAR.md` 全文と`EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-01_REPORT.md`: Grep `^## |Comment|不発|Leakage|REVIEW_REQUIRED|flagged` → 前回の未充足3点の詳細・記録箇所のみRead。
2. `er012_b_family_production_runner_01.py`: Grep `^def main|write_new_theme|comment|Comment|scaffold|run_scaffold|retry|fallback|regen` → Comment生成・Contract検証の既存呼び出し(main/main_a2側)とwrite_new_theme系stage定義の該当範囲のみRead。
3. `er012_b_family_voices_writer_generic_01.py`: Grep `^def |run_writer_stage_generic|voice_count|2v|3v` → 2V/3V分岐と戻り値(記事構造)の該当範囲のみ。
4. 3V保守版Fact Safetyゲートの実装: Grep `VOICE_FACT_SAFETY_GATE|voice_fact_safety|fact_safety_gate|section|split` を `er012_*.py` で実行 → ゲート本体・section parserの該当範囲のみRead(判定ロジックと構造読み取りの境界を特定)。
5. `er012_b_family_editorial_type_registry_01.py`: Grep `VOICE_FACT_SAFETY_GATE_MODE_DEFAULT|voice_count|comment|Comment|gate` → 該当範囲のみ。
6. `er012_b_family_voices_variable_voice_count_test_01.py`: Grep `^class |^    def test_` → 既存テスト一覧(拡張用)。
7. `er014_output/four_type_observation_01/voices/`配下: Glob `*fact_check*.json`・`*leak*.json`・`*flag*.json`・`run_result*.json` → 残存指摘・flagの原文のみRead。
8. `CURRENT_SPEC.md`: Grep `OPEN-151|Comment Contract|Comment 1|Fact Safety|3V保守版` → 該当範囲のみ(更新位置)。
9. `docs/pm/PM_BRIEF.md` L133-157(ACTIVE_TASK固定ヘッダ書式)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 実装: (5-1)`er012_b_family_production_runner_01.py`の`main_b1_2v()`/`main_b1_3v()`にComment生成+Contract検証stage(既存関数をそのまま呼ぶ)を接続。retry/regeneration時にCommentが記事再生成後に再生成される順序を確認。(5-2)Fact Safetyゲートのsection parserを2V(5区切り)/3V(6区切り)対応に一般化(判定ロジック無変更、既存3Vテストで不変証明)。(5-3)残存指摘の個別修正: 既存rewrite/regeneration経路(Local Rewrite、diff QA、Leakage是正retry等)で対応、必要なら配線後に2V記事を同Ledgerで再生成。
- テスト拡張: `er012_b_family_voices_variable_voice_count_test_01.py`または新規`_test_02.py`に、Comment接続(2V/3V)、Gate parser 2V/3V、3V不変(HEAD版比較)、Dangling Reference(Trial専用import 0)を追加。
- 2V clean evidence: `er014_output/four_type_observation_01/voices/run_voices_2v_b1.py`を更新(または`run_voices_2v_b1_v2.py`)し、`voices/run2_clean/`配下へ出力(記事5区切り全文・Comment 1〜4・Contract検証結果・Fact Safetyゲート発火ログ・Fact Checker/Leakage/Ledger Deviation/diff QA各verdict・`raw_usage_log.jsonl`・`cost_summary.json`・`production_set_cost.json`[Voices Production 1生成セット総原価=Research/Ledger(既存¥46.98)+Writer+Comment+QA/Gate+retry+rewrite])。旧成果物は`voices/run1_partial/`へ退避。
- SSOT: `OPEN_ITEMS.md` OPEN-151行末尾に結果(Status・15項目照合)、OPEN-120行末尾に3Vゲート発火evidence(2V runで発火した場合)。`CURRENT_SPEC.md` OPEN-151段落を更新(Comment接続・Gate 2V/3V整合・Status)。`DECISION_LOG.md`: Grep `PM-CLOSEOUT-CONSOLIDATION-131` → 直後に新エントリ+索引1行。`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`に2V clean run 1行。
- ACTIVE_TASK固定ヘッダ更新(管理ID=本タスク、APPROVED未配線=OPEN-151(結果)/OPEN-83/145/146(+OPEN-120)、報告単位Status: Voices=<結果> / 4TYPE完成=Trend・Discovery進行中 / Family C=Trial-09進行中)。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-02.md --json-out docs\pm\delegation_log\EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-02_check.json`
2. 改修前版保存: `git show HEAD:er012_b_family_production_runner_01.py > er014_output\four_type_observation_01\voices\runner_before_v2.py`(Gate実装ファイルも同様に保存)
3. テスト: `.venv\Scripts\python.exe -m unittest er012_b_family_voices_variable_voice_count_test_01 -v`(拡張後)、新規`_test_02`があれば同様
4. 関連回帰: `.venv\Scripts\python.exe run_project_regression.py --pattern "er012*_test_*.py"` および `.venv\Scripts\python.exe run_project_regression.py --pattern "er011*_test_*.py"`
5. 全件回帰(1回): `.venv\Scripts\python.exe run_project_regression.py`(基準: 直近2668件、既知FAIL3件以外の新規FAILは本タスク起因)
6. 2V clean evidence: `.venv\Scripts\python.exe er014_output\four_type_observation_01\voices\run_voices_2v_b1.py --reuse-ledger --out-subdir run2_clean --budget-jpy 150`(フラグは本タスクで実装。全文コマンドと固定値をRESULT_PACKETへ記録)
7. Dangling Reference: `grep -rn "er012_editorial_b_voices_trial\|_trial_0" er012_b_family_production_runner_01.py er012_b_family_voices_writer_generic_01.py`(Production→Trial importが0件であること。前回RESULT_PACKETで`main()`が`er012_output/editorial_b_voices_trial_07/`固定パスを読む点は既存挙動として記録のみ)
8. `git status --porcelain` → 明示add → commit → `git push origin main`(classifierブロック時は同一コマンド最大3回再試行)。

## SSOT追記文

- OPEN-151末尾: 「(EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-02、2026-09-14) Comment Contract接続<結果>、Fact Safetyゲート2V/3V parser一般化<結果、判定ロジック無変更>、2V記事の残存指摘個別修正<内容>、clean 2V runtime evidence<出力dir、verdict一覧、ゲート発火有無>、3V不変テスト<件数PASS>、回帰<件数>、Dangling 0件、model_id。Voices Production 1生成セット総原価=¥<実費>。Status: <PRODUCTION_WIRED(15項目全✓)/PARTIAL(未充足項目)>。commit <hash>。」
- DECISION_LOG: 「2026-09-14: EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-02(OPEN-151完成)。ユーザー方針(Comment接続/Gate 2V対応/残存指摘個別修正)に基づき実施。結果<Status>、15項目照合、evidence、費用、commit。」
- <>は実値。PARTIALならPRODUCTION_WIREDと書かない。

## Git(明示add対象・コミットメッセージ・trailer)

- 明示add: 変更したer012_*(+一般化に必要な最小範囲のQAモジュール)、テストファイル、`EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-02_REPORT.md`(新規root)、`er014_output/four_type_observation_01/voices/`配下(run2_clean/・run1_partial/・driver。`*_before_v2.py`等の一時比較ファイルは除外)、`CURRENT_SPEC.md`、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`、`docs/pm/delegation_log/EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-02.md`+`_check.json`、`docs/pm/RESULT_PACKET_VOICES_VAR2.md`。他の並行タスク成果物・無関係差分はaddしない。
- コミットメッセージ: `EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-02: OPEN-151完成(Comment Contract接続+Fact Safetyゲート2V/3V対応+2V clean evidence)` の後に空行、末尾に
  `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`
  `Claude-Session: https://claude.ai/code/session_01THnbjj6FiMbJtrKdFteoE4`

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_VOICES_VAR2.md`に: 1) 最終Status(PRODUCTION_WIRED/PARTIAL)と15項目を1つずつ「✓/✗+証跡」、2) Comment wiring結果(2V/3V、retry/regeneration時の順序)、3) Fact Safety Gate 2V/3V対応(parser一般化の内容、判定ロジック無変更の証明、2Vでの発火ログ)、4) Leakage・Fact Checker個別修正結果(原因・使用経路・修正前後・再QA verdict)、5) 2V runtime evidence(出力dir、記事語数、全Gate/QA verdict、Comment 1〜4、Contract検証)、6) 3V regression(不変テスト件数、再生成の有無)、7) retry・fallback整合、8) Fact attribution整合、9) actual model_id・routing、10) Dangling Reference Check、11) 費用: **Voices Production 1生成セット総原価=¥xx.xx**(内訳)、開発・検証費(3V再生成があれば)、12) API token、13) SSOT更新位置、14) commit hash・push結果、15) Open Item候補、16) T-0・事前指定外Read・STOP有無(STOP時は実施済み対応・残問題・選択肢)、17) ACTIVE_TASK更新済み。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥150+¥100)
- [x] 並行タスク衝突回避あり(news/trend/discovery/er013不可、Git本タスクのみ)
