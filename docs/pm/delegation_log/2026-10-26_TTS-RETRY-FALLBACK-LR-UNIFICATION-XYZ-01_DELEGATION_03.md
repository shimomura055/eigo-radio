## 管理ID

TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_03(Family X/Y/Z別のruntime evidence: 統一3回構成ブロック[①②同Style→180秒→③Fallback Style]、LRあり部位のLR1回+同構成、KP英語2+180秒+2、Zセリフctx2→180秒→従来③、Adv③短文Style、Z冒頭英語の共通化、終端HRQ1行、STOP/resume、Gate契約、A/B/C不変、Opus 4-c追加実走2本[Std chunk減速後NG→②PASS→Gate PASS、Adv L1③のVoice=Charon確認]。有料: EVIDENCE_PLAN Lean 46case+追加2本)。並行Agent: KP-GATE-DROP-BACKFILL-PRODUCTION-01 委任_03(KP stage限定のLLM run、X/Y/Zの別run dir `run_kpbf_ev_01`。**TTSは走らせない取り決め**。Master Audio Storeは共有=M-7のmerge実装済み)。あなたの所有=新run dir(各Family `run_tru_ev_*`、wav/raw_usage_log/STOP/lock不追跡)、driver(`docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/tools/**`、monkeypatchはdriver側のみ=M-8)、`docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/{EVIDENCE_01,EVIDENCE_X_01,EVIDENCE_Y_01,EVIDENCE_Z_01,COST_01,HR_IMPACT_01}.md`+`evidence_runs/`、`docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01_DELEGATION_03.md`(+check.json)、`docs/pm/RESULT_PACKET_TRU3.md`。Productionコード編集禁止(不具合発見時は原因・最小修正案を報告。軽微な修正でevidence継続が合理的な場合は、修正内容・影響範囲・testを記録したうえで実施可=11-8範囲内の不具合修正。Style/Prompt/Gate/Voice/回数/待機秒の変更は不可)。既存公開ページ・既存run dir不変。SSOT編集権なし。pathspec付きcommit。

## 性質/到達上限Status/禁止事項

- 性質: APPROVED_FOR_PRODUCTION仕様のruntime evidence取得。到達上限Status=EVIDENCE_COLLECTED(PRODUCTION_WIRED判定はFable)。
- 禁止: Production経路へのhook/env追加(M-8)、Gate/Style/Prompt/Voice/回数/待機の変更、HRなし宣言(ユーザー宣言なし)、同一run 5分3回超・起動間隔150秒未満、既存公開ページ・run dir改変、禁止Git操作(`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`)。
- 費用: 上限¥280(Guardrail。EVIDENCE_PLAN保守約200+Opus追加2本約10+余裕)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。**日次1,000円(JST)の残額**: 当日既使用約¥595+並行KP evidence見積¥30=約¥625。本委任の期待値約¥134〜保守¥210で日次内。累計が¥950に達する見込みになったら、その時点で残作業をまとめて報告しSTOP(翌日継続可。日付分割はこの理由のみ許容)。
- 費用/日次: 上記。承認区分: C(300円以下、承認済みScope)。`--budget-jpy`推奨: X130/Y60/Z75(+追加2本は該当Familyに+10)。
- 修正範囲の線引き(11-8): 範囲内=evidence取得・driver・軽微な不具合修正(記録付き)。範囲外=仕様変更。
- 時間見込み: 約2h(6 process並列約51分+追加2本+集計・文書)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1/D-1/G-1/F-1: 従来どおり。T-0: 委任文保存+`check_delegation_prompt.py`、結果をRESULT_PACKETへ1行(FAILでも継続)。T-2: 全runで`TTS_EXECUTION_MODE=STANDARD`を環境変数とCLI引数で明示(Batch不使用)。T-2追記4点: (1)差分再生成=対象segment限定起動が可能か確認、(2)新run dirでcache再利用なし(Store再利用は仕様どおり)、(3)`--budget-jpy`明示、(4)想定外の全再生成はAPI前にSTOP。T-3: 上記定型文。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01_DELEGATION_03.md` をN=690から順に試し、先頭「## 管理ID」+「TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_03」のものを採用。

## 事前指定Read一覧

- `docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/{EVIDENCE_PLAN_01,BUDGET_PLAN_01,IMPLEMENTATION_01(§5-6),DESIGN_02(§1 M表)}.md`、`BUDGET_CASES_01.json`、`BUDGET_WALLTIME_01.json`
- `docs/research/FZ-CONTEXT-*/`のFZCW driver方式(強制NG注入の先例、Grep `driver|inject|monkeypatch`)
- `er127_tts_block_policy_01.py`: Grep `block_evidence|BlockProgress|cooldown_core|STOP` → 出力項目の確認
- 各Family runnerの`--help`(KP救済evidence・Y Style是正で使った引数を踏襲: X `er019_family_x_audio_production_runner_01.py`、Y `er121_family_y_runner_01.py`[`--theme-package`必須]、Z `er063`/`er026`)

## 事前指定Grep一覧+追記位置・更新位置の手順

- 各run前: `py tools/stop_scope_check_01.py --managed-id TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 --run-dir <run dir> --out docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/stop_check_<family>_<case>.json`
- 起動は`.venv\Scripts\python.exe`。並列はFamily別run dirで最大6 process(EVIDENCE_PLAN)。

## 実施事項

1. **Lean 46case**(EVIDENCE_PLAN「代表+固定」): 強制NGはdriver側monkeypatch(判定のNG方向のみ。LR経路はPrimary転写の1語置換注入で`identify_ng_span`成立、U-03はQA gate単独NG)。実TTS・実ASR・実180秒待機・実LR(gpt-6-luna)・実Gate。記録: `block_evidence`(ordinal/Style実送信prefix/待機秒・STOP確認回数/LR回数/HRQ行数/採用attempt/Gate結果)、`injected_override_count`(ordinal別)、actual model_id・Voice(`speech_metadata`/sidecar)・routing、費用(raw_usage_log)。
2. **Opus 4-c追加実走2本**: (a)Std chunk「①減速後NG→②PASS→Assemble Gate PASS(誤BLOCKなし)」、(b)Adv L1 ③実走でVoice=Charon確認。任意(R-5): LR block内kill→resume 1本(費用に余裕があれば)。
3. **Family別観測表**(`EVIDENCE_X/Y/Z_01.md`): 部位(policy)×観測case×結果。未観測は未観測と明記。
4. **A/B/C不変**: evidence中にA/B/C runを走らせない(golden testで担保済み、再掲)。
5. **HR影響(R-7、`HR_IMPACT_01.md`)**: Adv③採用・LR採用がGate対象になることによるHR待ち件数の見込み(evidence内の③/LR採用件数と、Gate BLOCK件数から算出)。
6. **R-4**: Trial/toolがscope内で新flowになる点を再掲。
7. **費用**(`COST_01.md`): Family別・case別実績、量産原価影響(+0〜1円/セット推定の実測更新)、制作時間差分(1ブロック−420秒/新規待機+180秒)。
8. `EVIDENCE_01.md`: 受入条件(ユーザー原文§7 必須検証12項目)対応表+Family別達成状況。

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-26_TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01_DELEGATION_03.md --json-out docs\pm\delegation_log\2026-10-26_TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01_DELEGATION_03.md_check.json`
- 正式CLI(Family別、実値は`--help`で確認し全文記録。driver経由の場合もrunner本体を起動)
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

SSOT編集権なし。`RESULT_PACKET_TRU3.md`(9)にOPEN-540更新文案(EVIDENCE_COLLECTED、Family別)、OPEN-376/312/U-04/U-12解消文案、CURRENT_SPEC新節案(統一仕様表=ROW_MAPPING §2、旧記述:1531/:1647-1651/:1857/:2185の履歴化)、DECISION_LOG案、er011コメント1行修正(次委任)。

## Git

- add対象: `docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/`配下(evidence・tools・stop_check)、delegation_log。軽微修正を行った場合はそのコード+test。pathspec付きcommit。
- commit message: `TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_03: X/Y/Z runtime evidence(Lean 46case+Opus追加2本、実TTS/ASR/180秒/LR/Gate、実費¥X)`
- trailer: `Delegation: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/03`
- push: `git push origin HEAD:main`。

## 報告

`docs/pm/RESULT_PACKET_TRU3.md`: (0)T-0、(1)Family別観測表の要約(達成/未観測)、(2)必須検証12項目の対応表、(3)追加実走2本の結果、(4)HR影響見込み、(5)費用実績・単価・時間影響、(6)不具合・軽微修正の記録、(7)判断候補、(8)必須4行+「判定整合: 重大NG=<なし|あり>」、(9)SSOT文案、(10)一覧外Read、commit hash、raw URL。末尾10行要約。