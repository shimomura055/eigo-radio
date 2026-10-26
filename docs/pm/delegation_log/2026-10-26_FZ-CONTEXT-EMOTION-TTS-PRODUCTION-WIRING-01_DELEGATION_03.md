## 管理ID

FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_03(Phase 2: 正式runtime evidence E-1〜E-6の取得+受入材料。有料)。並行Agent: (1)FAMILY-Y-VOICE1-MALE7-TRIAL-01(有料TTS、`er121_*`読取、Y系dir) (2)CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01(er117/er019/er121 chunk実装、**er063は編集しない取り決め**) (3)KP-GATE-EXCLUSION-RESCUE-DESIGN-02(KP系)。本委任の所有=`docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/**`(EVIDENCE_01等の追加)、`er026_output/family_z_production_e2e_01/the_monkeys_paw/run_fzcw_*`(新規evidence run dir)、`er122_fzcw_runtime_evidence_01.py`(driver。バグ修正のみ可、Production経路は変更禁止)、`docs/pm/delegation_log/2026-10-26_FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_DELEGATION_03*`、`docs/pm/RESULT_PACKET_FZCW3.md`、`docs/pm/ACTIVE_TASK.md`。**`er063`/`er012_b`/`er003_n3`/`er122_fz_ctx_*`のProduction codeは本委任では編集禁止**(evidence取得中にコードを変えない。不具合が見つかったらSTOPして報告)。SSOTは編集しない(文案のみ。PRODUCTION_WIRED判定・CURRENT_SPEC反映はFable受入後の別委任)。

## 性質/到達上限Status/禁止事項

- 性質: 承認済み仕様(APPROVED_FOR_PRODUCTION)のruntime evidence取得。到達上限=EVIDENCE_COLLECTED(Fable照合待ち)。**PRODUCTION_WIREDとは書かない。**
- 実行計画の正本=`docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/EVIDENCE_PLAN_02.md`(E-1 正常経路: 猿の手Std+Adv正式runner、注入0をassert/E-2 1・2回目強制NG→cooldown→3回目従来方式PASS/E-3 cooldown中にkill→再開/E-4 3回NG→STOPPED→HR Lock→STOP(Std/Adv両方)/E-5 1回目のみ強制NG→2回目即時PASS+n=1 NG後kill→再開/E-6 Adv外側ループ継続[減速後判定側で注入])。計画どおりに実行し、逸脱が必要なら理由を記録(計画の事後改訂は履歴付き)。
- 禁止: 公開page出力禁止(`pages` stage禁止)/既存公開run(`run_sf_prod_01`等)の上書き禁止/強制NGはNG方向のみ(driver既定)/HR Lock・STOP・Gate迂回禁止(E-4でSTOPに到達したらそれが期待結果。`--clear-stop`等の解除はFable権限のため実行しない。STOP sentinelが残る場合はrun dir限定であることを確認し報告)/Git禁止操作(`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・`reset --hard`・`checkout -f`・`git checkout -- <file>`)/wav・raw_usage_log・STOP・lock・RUN_LOCKはcommitしない。
- 有料run規律: `.venv\Scripts\python.exe`、`TTS_EXECUTION_MODE=STANDARD`明示、各起動前に`py tools/stop_scope_check_01.py`(rc=0)、起動間隔150秒以上(`Get-Date`記録)、同一run 5分以内3回起動禁止(E-3/E-5のkill→再開は「再開」であり再起動に当たるため、kill後150秒以上空けてから再開し記録)。**並行してY Voice Trialが同一TTS backendを使用中**: 429/5xx等の技術失敗が起きた場合、その試行は品質evidenceとして扱わず(`effective_mode`/error種別を記録)、該当ケースは150秒以上空けて再実行(費用は記録)。技術失敗が3件以上連続したらSTOPして報告。
- 費用上限: 「上限¥200(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」見積=期待約49円・保守約62円・天井約80円(BUDGET_PLAN_02)。
- Opus独立技術レビューGate(11-3): 条件A済み(再利用)。本委任は非該当(evidence取得)。
- 時間見込み: 3〜4時間(E-1 約30分、E-2〜E-6 各cooldown 600秒×Std/Adv含め約2〜2.5時間、整理30分)。並列化: 他案件と並列。本委任内はE-1→E-5→E-2→E-6→E-3→E-4の順(早く終わるものから。E-4はSTOP到達で終わるため最後)。cooldown待機中にevidence整理を進める。
- 費用/日次: 当日(JST 2026-10-26)既使用JPY約214+Y Voice Trial進行中(Cap 250)/本委任見積JPY約49〜80/承認区分: C(承認済みScope内・300円以下・日次内)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認(E-1は新規run dirのため再利用なし=全dialogue新規生成が計画どおりであることを確認。`REUSE_DENY`で旧runからの流用が無いことを記録)、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は上記定型文に従う。ユーザー承認済みの総予算・個別run上限・STOP条件を優先し、Fable/Workerが独自に過度に厳しい停止条件を追加しない(2026-10-05)。

委任文保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 641 --out docs\pm\delegation_log\2026-10-26_FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_DELEGATION_03.md`(先頭が「## 管理ID」+「FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_03」でなければ637〜652を順に試す)→check実行。

## ユーザー指示(原文)

`docs/pm/delegation_log/2026-10-26_FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_USER.md` §6(受入条件表6ケース)「Mockテストに加え、正式Production runtimeで文脈・感情付き方式が実際に発火した証拠を取得すること。Fallbackは3回目まで偶発的に失敗するのを待たず、強制NGによるテストで遷移を検証してよい。ただし、Mockだけで通常経路全体をPRODUCTION_WIREDと判定しないこと。実際の正常経路・Fallback経路を区別して証拠を記録する。」§7「完了報告では、Family Z Standard／Advancedそれぞれについて、正式初回生成・retry・fallback・resume・QA・実音声・コストを明示すること。」

## KPI provenance欄

E-1=production_formal_path(fresh、正式runner・注入0)。E-2〜E-6=fresh(正式runner+NG方向のみ上書き=forced)。表ごとに`path=normal|forced_*`を明記。E2E自己確認=Yes(E-1はfresh Production初回pathを含む)。

## Opus台帳更新

OF-FZCW-M-10(runtime evidence不足)→本委任でEVIDENCED候補(Fable確定)。OF-FZCW-R-1(共有ファイル汚染)→駆動時の前後行数記録・HR queue行の無効化文案で対応。台帳編集はしない(文案のみ)。

## 事前指定Read一覧

1. `docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/{EVIDENCE_PLAN_02,BUDGET_PLAN_02,DESIGN_02 §C・§E・§H}.md`、`docs/pm/RESULT_PACKET_FZCW2.md`(開示事項・driver使い方)。
2. `er122_fzcw_runtime_evidence_01.py` 全文(driver、実行前に引数・assert・出力schemaを把握)。
3. `er122_fz_ctx_policy_01.py` :1-80(state schema、既定policy)、`er122_fz_ctx_notes_01.py` 先頭docstring。
4. `tools/stop_scope_check_01.py --help`。
5. `er026_output/family_z_production_e2e_01/the_monkeys_paw/run_sf_prod_01/`のe2e_stage_log.jsonl末尾(現行原価の対照用、読取のみ)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 共有台帳の前後行数: `er011_output/attempt_history.jsonl`、`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`、cost log(driverが記録。各E前後で`(Get-Content <file>).Count`も記録)。
- ACTIVE_TASK.md: 固定ヘッダで上書き(管理ID=本件 委任_03/APPROVED未配線=OPEN-528(Phase 2 evidence取得中→完了)/並行3件/当日費用=2026-10-26 約214+本委任実費+Y Trial実費/1,000)。

## 実行コマンド全文(EVIDENCE_PLAN_02の実値に合わせる。以下は形式例)

```
py tools\stop_scope_check_01.py
Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$env:TTS_EXECUTION_MODE="STANDARD"; .venv\Scripts\python.exe er122_fzcw_runtime_evidence_01.py --case E-1 --work the_monkeys_paw --level a2 --run run_fzcw_e1_a2_01 --budget-jpy 40
$env:TTS_EXECUTION_MODE="STANDARD"; .venv\Scripts\python.exe er122_fzcw_runtime_evidence_01.py --case E-1 --work the_monkeys_paw --level b1b --run run_fzcw_e1_b1b_01 --budget-jpy 40
$env:TTS_EXECUTION_MODE="STANDARD"; .venv\Scripts\python.exe er122_fzcw_runtime_evidence_01.py --case E-5 --work the_monkeys_paw --level a2 --run run_fzcw_e5_a2_01 --clip <plan指定> --budget-jpy 15
… E-2/E-6/E-3/E-4(Std/Adv)
```
- 事後集計: `py docs\research\FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01\tools\fzcw_evidence_summarize_01.py --runs er026_output\family_z_production_e2e_01\the_monkeys_paw --prefix run_fzcw_ --out docs\research\FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01\EVIDENCE_01.md --json …\evidence_01.json`(新規script可: 各runのstate/attempt履歴/style sha/mode/cooldown経過秒/HR Lock/STOP/ASR判定/費用/peak分布/minimal_fallback件数/共有台帳前後行数を表化)。
- Production不変: `git status --short -- er063_family_z_audio_01.py er012_b_family_voices_production_01.py er003_v1_n3_01_tts_generate.py er122_fz_ctx_policy_01.py er122_fz_ctx_notes_01.py`(本委任由来差分0)。
- secret grep: `git diff --cached | findstr /R /C:"sk-[A-Za-z0-9]" /C:"AIza[A-Za-z0-9_-]" /C:"BEGIN PRIVATE KEY"`(0件)。

## 成果物

`docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/EVIDENCE_01.md`(ケース×レベル表: 期待動作/観測/判定PASS・FAIL、各attemptのmode[ctx/ctx/legacy]・style sha・ASR/QA判定・cooldown実経過秒・再開時の復元内容・HR Lock/STOP到達・注入件数・`effective_mode`・minimal_fallback件数・技術失敗件数)、`COST_01.md`(E別実費、E-1の量産単価換算=15-8「Production 1生成セット総原価」のZ行構成を明記し現行46.82円と対比、区分1〜6の実測更新)、`PEAK_OBS_01.md`(ctx音声のpeak分布観測値、`check_clip_audio_quality` peak_max=0.999超過の有無。新基準ではない)、`SHARED_LEDGER_01.md`(共有台帳前後行数、forced由来HR queue行の無効化文案「evidence専用・対応不要」)、`EVIDENCE_PLAN_02.md`からの逸脱履歴、`docs/pm/RESULT_PACKET_FZCW3.md`。

## SSOT追記文

文案のみ: OPEN-528更新(Phase 2結果、Status候補=PRODUCTION_WIRED判定材料そろい/不足)、DECISION_LOG(Fable判定後)、CURRENT_SPEC(DESIGN_02 §J文案をevidence値で補完)、OPUS台帳(M-10/R-1遷移)。

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: なし。
- 明示add: `docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/{EVIDENCE_01,COST_01,PEAK_OBS_01,SHARED_LEDGER_01,evidence_01.json,tools/fzcw_evidence_summarize_01.py}`、EVIDENCE_PLAN_02(逸脱履歴追記時)、delegation_log+check.json、driver修正があればそのファイル。run dir配下はcommitしない(evidence JSONの写しは研究dirへ)。
- commit: `git commit --only <paths…> -m "FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_03: Phase 2 runtime evidence E-1〜E-6(猿の手Std/Adv、正常経路+強制NG fallback/resume/exhaust、実費<X>円、PRODUCTION_WIRED判定はFable)"`→`git push origin HEAD:main`(non-fast-forwardは`git fetch origin`→`git merge --no-edit origin/main`→再push。競合は両方残してSTOP)。

## 報告(RESULT_PACKET項目)

(0)T-0 (1)結論(6ケース×Std/AdvのPASS/FAIL、PRODUCTION_WIRED判定材料の充足/不足一覧) (2)E-1正常経路の詳細(ctx方式の実発火証拠: 各clipのmode/style sha/ASR OK初回率/NG発生とその遷移/組立・headroom.scalar・gain_report/実音声path) (3)fallback/resume/exhaustの遷移表(cooldown実経過秒、再開復元、HR Lock/STOP) (4)費用(E別・合計/Cap 200、E-1の量産単価換算、区分1〜6更新) (5)peak観測・minimal_fallback件数・技術失敗件数 (6)共有台帳前後行数と無効化文案 (7)計画逸脱の有無 (8)Production不変・保全 (9)commit/push・raw URL (10)一覧外Read (11)Fable向け懸念(PRODUCTION_WIRED判定で確認すべき点、CURRENT_SPEC文案の補完値)。最終行に要約10行以内。