# -*- coding: utf-8 -*-
"""er121_family_y_calibration_01.py
FAMILY-Y-PRODUCTION-LAUNCH-01 委任_02A: Evidence runner(DEV/証跡用。Production runnerではない・どのProduction経路からも参照されない)。

  gate   : M-1較正。過去Closing 11件+案B+Lead/紹介(2版)を、M-1修正後のProduction版Tension判定promptで再判定し、旧判定との差分表を作る。
           旧判定と新判定が食い違った項目だけ、旧prompt(DEV原文)で同じ本文を再判定する(判定器のばらつきと、prompt変更の効果を切り分ける対照。数円)。
  rewrite: M-2書換え経路evidence。過去FAIL稿(R1宅配gen_1、R2宅配H2)を入力に、Production版の局所書換え→再判定→check_closing を通す(新規生成なし)。

有料runは --paid と --cap-jpy が必要。各call前に tools/stop_scope_check_01.py を実行(rc=3で停止)し、実費累計+見積>capで予約停止する。
er006へのY routing key登録は02Bの担当。それまでの証跡runに限り、本processの中だけでPROCESS_MODEL_MAPへ期待値を一時登録する(登録内容は出力に記録)。
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import sys

import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er121_family_y_text_core_01 as c

OUT = "er110_output/family_y_production_launch_01"
CAL = f"{OUT}/calibration_01"
RWE = f"{OUT}/rewrite_evidence_01"
MID = "FAMILY-Y-PRODUCTION-LAUNCH-01"
R1 = "er110_output/family_y_closing_general_01"
R2 = "er110_output/family_y_closing_general_02"
REV = "er110_output/family_y_redelivery_audio_01/revision_01"
CLOSING_EST_JPY = 0.8
REWRITE_EST_JPY = 9.0


def _j(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _t(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def targets() -> list:
    """(name, text_path, old_check_path)"""
    t = []
    for theme in ("redelivery_fee", "sns_age_limit"):
        for g in (1, 2):
            d = f"{R1}/{theme}/gen_{g}"
            t.append((f"R1_{theme}_gen{g}", f"{d}/closing_final.txt", f"{d}/gate_leak_check.json"))
    for theme in ("redelivery_fee", "sns_age_limit"):
        for tag in ("high_1", "high_2", "medium_1"):
            d = f"{R2}/{theme}/gen_{tag}"
            t.append((f"R2_{theme}_{tag}", f"{d}/closing_final.txt", f"{d}/gate_leak_check.json"))
    t.append(("A_v1_initial", f"{REV}/closing_A_v1/closing_final.txt", f"{REV}/closing_A_v1/gate/leak_check_1.json"))
    t.append(("B_fixed", f"{REV}/closing_B/closing_final.txt", f"{REV}/closing_B/gate/leak_check_1.json"))
    return t


def leadintro_targets() -> list:
    out = []
    for name, lead, intro, old in (("leadintro_final", f"{REV}/lead/lead.txt", f"{REV}/intro/intros.json", f"{REV}/gate_lead_intro/leak_check.json"),):
        out.append((name, lead, intro, old))
    return out


def stop_check(tag: str):
    r = subprocess.run([sys.executable, "tools/stop_scope_check_01.py", "--managed-id", MID, "--run-dir", CAL, "--out", f"{CAL}/stop_check_{tag}.json"],
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode == 3:
        raise SystemExit(f"[STOP] stop_scope_check rc=3 ({tag}): 新規API呼出をしない")
    if r.returncode != 0:
        raise SystemExit(f"[STOP] stop_scope_check rc={r.returncode} ({tag}): {r.stderr[:200]}")


def spent_jpy(dirs) -> float:
    import er053_cost_aggregate_01 as ca
    return round(sum(ca.compute_stage_cost_breakdown_multi(f)["total_jpy"] for d in dirs for f in glob.glob(f"{d}/raw_usage_log*.jsonl")), 3)


class Guard:
    def __init__(self, cap, dirs):
        self.cap, self.dirs = cap, dirs

    def reserve(self, est, note):
        s = spent_jpy(self.dirs)
        if s + est > self.cap:
            raise SystemExit(f"[BUDGET_RESERVE_STOP] spent {s} + est {est} > cap {self.cap} ({note})")
        stop_check(note.replace(" ", "_")[:40])
        return s


def register_routing_for_evidence():
    for k, v in c.ROUTE.items():
        routing.PROCESS_MODEL_MAP.setdefault(k, v["model"])
    return {k: v for k, v in c.ROUTE.items()}


def _old_prompt_judge(client, text, stage):
    """対照: M-1修正前(DEV原文)のTension判定prompt。Production版と『上記と同じ意味』行の展開だけが違う。"""
    prompt = c.build_leak_prompt("tension", {"tension": text}).replace(c._REF_EXPANDED, c._REF_LINE)
    resp = c.chat(client, route_key="FAMILY_Y_LEAK_JUDGE", user=prompt, developer=c.LEAKAGE_DEVELOPER_JA, schema=c.leak_schema_for("tension"), stage=stage)
    parsed = json.loads(resp.output_text)["tension"]
    return {"fails": [f for f in c.TENSION_FIELDS if parsed[f] == "FAIL"], "reasoning": parsed["reasoning"], "quoted_evidence": parsed["quoted_evidence"],
            "prompt_sha256": c.w1.sha_text(prompt), "meta": c.resp_meta(resp)}


def _fails(chk_or_old) -> list:
    items = chk_or_old.get("flagged_items", [])
    return sorted({x for it in items for x in it["fail_fields"]})


def cmd_gate(a, client, g):
    os.makedirs(CAL, exist_ok=True)
    rows = []
    for name, tp, op in targets():
        text = _t(tp).strip()
        old = _j(op)
        g.reserve(CLOSING_EST_JPY, f"gate {name}")
        new = c.run_leak(client, "tension", {"tension": text}, stage=f"cal_{name}")
        c.w1.wj(f"{CAL}/{name}_new.json", new)
        row = {"name": name, "text_path": tp, "text_sha256": c.w1.sha_text(text), "chars": len(text), "old_fails": _fails(old), "new_fails": _fails(new),
               "old_prompt_sha256": old.get("prompt_sha256"), "new_prompt_sha256": new["prompt_sha256"],
               "new_reasoning": [x["reasoning"] for x in new["flagged_items"]], "new_quoted": [x["quoted_evidence"] for x in new["flagged_items"]],
               "old_reasoning": [x["reasoning"] for x in old.get("flagged_items", [])], "old_quoted": [x["quoted_evidence"] for x in old.get("flagged_items", [])]}
        row["changed"] = row["old_fails"] != row["new_fails"]
        if row["changed"]:
            g.reserve(CLOSING_EST_JPY, f"control {name}")
            ctl = _old_prompt_judge(client, text, f"cal_{name}_ctl")
            row["control_old_prompt_fails"] = ctl["fails"]
            row["control_prompt_sha256"] = ctl["prompt_sha256"]
            c.w1.wj(f"{CAL}/{name}_control.json", ctl)
        rows.append(row)
        print(f"[CAL] {name}: old={row['old_fails']} new={row['new_fails']}" + (f" ctl={row.get('control_old_prompt_fails')}" if row["changed"] else ""))
    for name, lp, ip, op in leadintro_targets():
        lead = _t(lp).strip()
        intros = _j(ip)
        comb = "\n".join([lead] + [intros[s] for s in c.SLOTS])
        old = _j(op)
        g.reserve(CLOSING_EST_JPY, f"gate {name}")
        new = c.run_leak(client, "tension", {"tension": comb}, stage=f"cal_{name}")
        c.w1.wj(f"{CAL}/{name}_new.json", new)
        row = {"name": name, "text_sha256": c.w1.sha_text(comb), "chars": len(comb), "old_fails": _fails(old), "new_fails": _fails(new),
               "old_applicable": c.split_leadintro_flags(old), "new_applicable": c.split_leadintro_flags(new),
               "new_reasoning": [x["reasoning"] for x in new["flagged_items"]], "old_prompt_sha256": old.get("prompt_sha256"), "new_prompt_sha256": new["prompt_sha256"]}
        row["changed"] = row["old_fails"] != row["new_fails"]
        rows.append(row)
        print(f"[CAL] {name}: old={row['old_fails']} new={row['new_fails']}")
    c.w1.wj(f"{CAL}/calibration_table.json", {"rows": rows, "spent_jpy": spent_jpy([CAL]), "routing_override": "process-local evidence override (02B registration pending)"})


def cmd_repeat(a, client, g):
    """判定器のばらつき測定: 案Bは新prompt6回+旧prompt6回、その他の本文は新prompt追加2回(1回目はcmd_gateの結果)。"""
    rows = []
    for name, tp, op in targets():
        text = _t(tp).strip()
        n_new, n_old = (6, 6) if name == "B_fixed" else (2, 0)
        rec = {"name": name, "text_sha256": c.w1.sha_text(text), "new_prompt_fails": [], "old_prompt_fails": []}
        for i in range(n_new):
            g.reserve(CLOSING_EST_JPY, f"rep new {name} {i}")
            chk = c.run_leak(client, "tension", {"tension": text}, stage=f"rep_{name}_new{i}")
            rec["new_prompt_fails"].append(_fails(chk))
            if name == "B_fixed":
                rec.setdefault("new_reasoning", []).append([x["reasoning"] for x in chk["flagged_items"]])
        for i in range(n_old):
            g.reserve(CLOSING_EST_JPY, f"rep old {name} {i}")
            rec["old_prompt_fails"].append(_old_prompt_judge(client, text, f"rep_{name}_old{i}")["fails"])
        rows.append(rec)
        print("[REP]", name, "new:", rec["new_prompt_fails"], "old:", rec["old_prompt_fails"])
    c.w1.wj(f"{CAL}/repeat_table.json", {"rows": rows, "spent_jpy": spent_jpy([CAL])})


def cmd_leadrepeat(a, client, g):
    """Lead+人物紹介(ナレーター文)の判定器ばらつき: 新prompt3回+旧prompt3回(cmd_gateの1回に追加)。"""
    name, lp, ip, op = leadintro_targets()[0]
    lead = _t(lp).strip()
    intros = _j(ip)
    comb = chr(10).join([lead] + [intros[s] for s in c.SLOTS])
    rec = {"name": name, "text_sha256": c.w1.sha_text(comb), "new_prompt_fails": [], "old_prompt_fails": [], "new_applicable_fails": []}
    for i in range(3):
        g.reserve(CLOSING_EST_JPY, f"leadrep new {i}")
        chk = c.run_leak(client, "tension", {"tension": comb}, stage=f"leadrep_new{i}")
        rec["new_prompt_fails"].append(_fails(chk))
        rec["new_applicable_fails"].append(sorted({x for it in c.split_leadintro_flags(chk)["applicable_flagged"] for x in it["fail_fields"]}))
    for i in range(3):
        g.reserve(CLOSING_EST_JPY, f"leadrep old {i}")
        rec["old_prompt_fails"].append(_old_prompt_judge(client, comb, f"leadrep_old{i}")["fails"])
    print("[LEADREP]", json.dumps(rec, ensure_ascii=False))
    c.w1.wj(f"{CAL}/leadintro_repeat_table.json", {"row": rec, "spent_jpy": spent_jpy([CAL])})


def cmd_rewrite(a, client, g):
    os.makedirs(RWE, exist_ok=True)
    parts = c.load_prompt_parts()
    rules = c.closing_rules_section(parts)
    cases = [("R1_redelivery_gen1", f"{R1}/redelivery_fee/gen_1", "redelivery_fee"),
             ("R2_redelivery_high2", f"{R2}/redelivery_fee/gen_high_2", "redelivery_fee")]
    import er110_family_y_redelivery_revision_01 as rev        # 証跡runnerのみDEVの入力(Voice本文・Theme)を読む。Production moduleは非import
    import er110_family_y_redelivery_audio_01 as rr
    r0 = rr.load_r0()
    voices = {s: r0[s] for s in c.SLOTS}
    results = []
    for name, d, slug in cases:
        text = _t(f"{d}/closing_final.txt").strip()
        analysis = _j(f"{d}/analysis_final.json")
        selected = next(x for x in analysis["candidates"] if x["id"] == analysis["selected_id"])
        out = f"{RWE}/{name}"
        g.reserve(CLOSING_EST_JPY + REWRITE_EST_JPY, f"rewrite {name}")
        # 入力は『過去にFAILした稿』。Production run_gateを通す(判定→局所書換え→再判定→check_closing)。判定1回目でPASSした場合は書換え経路を通らない(記録する)。
        try:
            r = c.run_gate(client, kind="tension", stage=f"rwe_{name}", texts={"tension": text}, out_dir=f"{out}/gate", voices_ctx=voices,
                           selected=selected, rules_section=rules)
            status, final = r["status"], r["final_texts"]["tension"]
            post = c.check_closing(final)
            row = {"name": name, "input_sha256": c.w1.sha_text(text), "status": status, "n_judgements": r["n_judgements"], "rewritten": r["rewritten"],
                   "final_sha256": c.w1.sha_text(final), "post_check": post, "selected_id": analysis["selected_id"], "stop": None}
            c.w1.wt(f"{out}/closing_after.txt", final + "\n")
        except c.YStop as e:
            row = {"name": name, "input_sha256": c.w1.sha_text(text), "status": "STOP", "stop": {"code": e.code, "message": str(e)}}
        c.w1.wj(f"{out}/summary.json", row)
        results.append(row)
        print("[REWRITE]", json.dumps({k: v for k, v in row.items() if k != "post_check"}, ensure_ascii=False))
    c.w1.wj(f"{RWE}/rewrite_evidence_table.json", {"rows": results, "spent_jpy": spent_jpy([RWE]), "routing_override": "process-local evidence override (02B registration pending)"})


def main():
    ap = argparse.ArgumentParser(description="Family Y M-1較正 / M-2書換えevidence(証跡用)")
    ap.add_argument("cmd", choices=("gate", "repeat", "leadrepeat", "rewrite"))
    ap.add_argument("--paid", action="store_true")
    ap.add_argument("--cap-jpy", type=float, required=True)
    a = ap.parse_args()
    if not a.paid:
        raise SystemExit("[NO_PAID_FLAG] --paid が無いため有料runを起動しません")
    import er003_v1_en_direct_vfl_01_generate as vfl01
    d = RWE if a.cmd == "rewrite" else CAL
    os.makedirs(d, exist_ok=True)
    cl.install(f"{d}/raw_usage_log.jsonl")
    reg = register_routing_for_evidence()
    c.w1.wj(f"{d}/entry_point_{a.cmd}.json", {"runner": "er121_family_y_calibration_01.py", "cmd": a.cmd, "management_id": MID, "production_reachable": False,
                                      "cap_jpy": a.cap_jpy, "routing_registered_in_process": reg, "prompt_sha256": c.PROMPT_SHA256})
    client = vfl01.get_client()
    g = Guard(a.cap_jpy, [d])
    {"gate": cmd_gate, "repeat": cmd_repeat, "leadrepeat": cmd_leadrepeat, "rewrite": cmd_rewrite}[a.cmd](a, client, g)


if __name__ == "__main__":
    main()
