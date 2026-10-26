# BUDGET_PLAN_01 (KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01 委任_01、2026-10-26)

承認区分: C(承認済みTrial範囲=ユーザー本日指示、案件300円以下、日次1,000円以内)。上限=Guardrail JPY80。

## 見積(実行前)
- 単価: gpt-6-luna = 入力$0.10/M・出力$0.50/M(er005_output/cost_baseline_01/pricing_snapshot.json)、gpt-6.1-sol = 入力$2/M・出力$10/M、USD_JPY=160(daily_dev_cost_01.py)。
- 既存実績(AI島 run_ai_01 raw_usage_log): kp_gloss_alignment 2 call = 約1.09円、scaffold全体20 call = 約2.60円 → 1 call あたり0.05〜0.55円。
- 1 run(P7 + W3 + canonicalization[1〜3 attempt] + gloss再整合 + Redundancy QA ≒ 6〜9 call)= 約0.8〜1.5円(現行方式freshも同等)。
- Trial方式 = 6 level × 2 rep = 12 run → 約10〜18円。現行方式fresh baseline(AI島は既存再利用のため4 level × 1) = 4 run → 約3〜6円。
- LLM judge(gpt-6.1-sol、reasoning low、level単位1 call × 6): 1 callあたり入力約3k tok・出力(reasoning含む)約4〜6k tok ≒ 約0.8〜1.2円〜(出力$10/M換算で6k tok=約9.6円が上限) → 約5〜30円。
- **合計見積 約20〜55円**(委任見積の20〜40円は中央値付近。Guardrail 80円以内。超過見込みは低い)。
- 日次(JST 2026-10-26): 既使用約500円 + 本Trial最大約55円 → 1,000円以内。
- call数・要求件数・返答件数・実費は `trial_runs_01.json`(usage log出典)に実績を記録する。
- 事前STOP確認: `py tools\stop_scope_check_01.py --managed-id KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01 --run-dir docs/research/KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01 --out stop_check_01.json` → rc=0(stop=false)。
