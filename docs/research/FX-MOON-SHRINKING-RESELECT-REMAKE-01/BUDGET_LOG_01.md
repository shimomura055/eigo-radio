# BUDGET_LOG_01 (FX-MOON-SHRINKING-RESELECT-REMAKE-01 委任_01)
| # | 時刻(UTC) | 工程 | 実費(円) | 累計 | stop_check |
|---|---|---|---|---|---|
| 1 | 2026-10-28 00:00〜00:05 | `--stage scaffold --scaffold-only kp`(両level KP候補+gloss整合+QA、openai gpt-6-luna、外側retry含む) | 3.93 | 3.93 | stop_check_kp.json rc=0 |
| 2 | 2026-10-28 00:09〜00:12 | `--stage study_text`(Part2候補抽出×2+Top1/Top2解説×4) | 1.39 | 5.32 | 同上 |
Phase 1実費 **5.32円**(見積4〜9円内、Cap 40円の約13%)。残Cap 34.68円。起動2回(rc=4待機=正常、再起動0・異常終了0)。当日(10/28)累計は約20円+5.32円=約25円/1,000円。
出典: runnerのcost行(`runner_kp_stdout.log` / `runner_study_stdout.log`)。
