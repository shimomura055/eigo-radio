# -*- coding: utf-8 -*-
"""委任_13(B8): 承認済みevidence driver(tru_ev_run_01.run_case)を、配線後HEADの正式経路・既定profileで1groupぶん1起動する薄いselector。
既存evidence(run_tru_ev_*)を壊さないため case idに"B8-"を付けて新run dirで実行(driver本体・Production codeは無変更)。evidence出力は本dirのevidence_runs/。
使い方: TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe <this> --group X-Std --only X-Std-2,X-Std-6 --approved-budget-jpy 10 [--resume] [--dry]
"""
import argparse, copy, json, os, sys, time
ROOT = os.getcwd()
TOOLS = os.path.join(ROOT, "docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/tools")
sys.path.insert(0, TOOLS)
import tru_ev_run_01 as run   # noqa: E402
import tru_ev_core_01 as core  # noqa: E402
import tru_ev_cases_01 as cases  # noqa: E402

B8 = "docs/research/LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01/B8_evidence_01"
run.EVD = B8
run.EVIDENCE_RUNS = f"{B8}/evidence_runs"
core.MANAGEMENT_ID = "LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--group", required=True)
    ap.add_argument("--only", required=True)
    ap.add_argument("--approved-budget-jpy", type=float, required=True)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--kill-in-cooldown", type=float, default=None)
    a = ap.parse_args()
    if os.environ.get("TTS_EXECUTION_MODE") != "STANDARD":
        print("[STOP] TTS_EXECUTION_MODE=STANDARD required", file=sys.stderr); return 2
    sel = a.only.split(",")
    todo = []
    if "Y-Std-1fb" in sel and a.group == "Y-Std":   # 波2追加: Y Std英語短文Fallback(topic_intro、①②NG→③採用。Y-Std-1と同一leaf・同一policy、planのみ ng=[1,2])
        base = next(c for c in cases.CASES if c["id"] == "Y-Std-1")
        c2 = copy.deepcopy(base); c2["id"] = "B8-Y-Std-1fb"; c2["scenario"] = "E-S1"; c2["plan"] = cases._p(ng=[1, 2]); todo.append(c2)
    if "Y-Std-1lr" in sel and a.group == "Y-Std":   # 波3追加: Y Std LR成功(topic_intro、①②NG→LR①'採用。Y-Std-1と同一leaf、planのみ ng=[1,2,3], sub=[3])
        base = next(c for c in cases.CASES if c["id"] == "Y-Std-1")
        c2 = copy.deepcopy(base); c2["id"] = "B8-Y-Std-1lr"; c2["scenario"] = "E-S2a"; c2["plan"] = cases._p(ng=[1, 2, 3], sub=[3]); todo.append(c2)
    if "Y-Std-4c" in sel and a.group == "Y-Std":     # 波4追加: Y-Std-4b(自然ASR逸脱でHRQ終端となった)の1回のみ再実行(別run dir。同一plan)
        base = next(c for c in cases.CASES if c["id"] == "Y-Std-4b")
        c2 = copy.deepcopy(base); c2["id"] = "B8-Y-Std-4c"; todo.append(c2)
    if "X-Std-2b" in sel and a.group == "X-Std":     # 波3追加: X Std LR成功(X-Std-2と同一plan+X-Std-1bと同じtitle_override。実ASRの"topic→market"自然逸脱を避ける)
        base = next(c for c in cases.CASES if c["id"] == "X-Std-2")
        c2 = copy.deepcopy(base); c2["id"] = "B8-X-Std-2b"; c2["title_override"] = "Coffee Bean Prices Fall"; todo.append(c2)
    for c in cases.CASES:
        if c["group"] == a.group and c["id"] in sel:
            c2 = copy.deepcopy(c); c2["id"] = "B8-" + c["id"]; todo.append(c2)
    spent = 0.0; summ = []
    for c in todo:
        if spent >= a.approved_budget_jpy:
            print("[BUDGET] reached", spent); break
        print(f"[CASE] {c['id']} start {time.strftime('%H:%M:%S')}", flush=True)
        ev = run.run_case(c, budget_left=a.approved_budget_jpy - spent, args=argparse.Namespace(
            resume=a.resume, dry=a.dry, kill_in_cooldown=a.kill_in_cooldown))
        j = float((ev.get("cost") or {}).get("jpy") or 0.0); spent += j
        print(f"[CASE] {c['id']} done tts={ev.get('tts_attempts_count')} cd={ev.get('cooldown_count')} lr={ev.get('lr_count')} jpy={j} exc={(ev.get('exception') or {}).get('type')} spent={spent:.2f}", flush=True)
        summ.append({"case": c["id"], "jpy": j, "exc": (ev.get("exception") or {}).get("type")})
    print(json.dumps({"group": a.group, "spent_jpy": round(spent, 3), "cases": summ}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
