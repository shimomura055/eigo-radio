# regression_02: 回帰15 job(Coffee/Meta Std/Hormuz)は未実行
管理ID: FAMILY-X-KP-NO-WAY-MINIMAL-FIX-TRIAL-01 委任_02 / 2026-10-13
- 実行しなかった理由: Stage 1(meta_adv n=5)で、ユーザー受入条件(3)「良好な選定の維持」に反する副作用(`concierge` 2/2→0/5、5枠目に`instead of AI`/`talking to AI`等の断片拡張が入る)を確認。ユーザーSTOP条件「良好なKey Phraseが失われる品質悪化 → 追加探索せずSTOP」に該当すると判断した(plan_01のStage 2 Go規則[bare≤2/5・INVALID≤1/5]は技術的には満たすが、副作用の確認時点でSide effect→REJECTED/M2P0維持の規定を優先)。回帰15 job(中央約JPY14)は未使用。
- R1〜R8: 判定せず(未取得)。Coffee・Hormuz・Meta Stdへの影響は未測定。残予算(承認上限JPY30のうち約JPY25)は未使用。Fableが回帰測定も必要と判断した場合のみ、別途Stage 2(`er064_kp_noway_01_run.py --stage 2`、事前登録済)を実行可能。
- 参考(Stage 1のみで取得できたR8相当、meta_adv 5 job vs 対照2 job): 平均JPY/job 0.979 vs 0.816(+20%)、所要 115.0s vs 79.3s(+45%)、reasoning tokens 3,905 vs 3,094(+26%)。対照はn=2で参考値。Round1 M2P0全14 job平均(0.913)比では+7%(R8基準1.15倍以内)。
