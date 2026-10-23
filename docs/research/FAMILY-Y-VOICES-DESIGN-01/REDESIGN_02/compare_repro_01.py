# -*- coding: utf-8 -*-
"""compare_repro_01.py -- 委任_15: school_phone_ban main と repro の機械的比較(LLM 0 call・費用0)。結果をstdout(JSON)へ。"""
import json
import re
T = "er110_output/family_y_persona_pipeline_01/school_phone_ban/"
L = lambda r, f: json.load(open(T + r + "/" + f + ".json", encoding="utf-8"))
SHIFT = re.compile(r"勤務|シフト|出勤|欠員|職場|勤め|バイト|アルバイト")
INST = {"学校側(教員・校長・養護・教委)": re.compile(r"教員|担任|校長|副校長|管理職|養護教諭|教育委員会"), "保護者": re.compile(r"保護者")}
out = {}
for r in ("main", "repro"):
    st = {s["id"]: s for s in L(r, "s2_stakeholders")["stakeholders"]}
    cl = {c["id"]: c for c in L(r, "s3_claims")["claims"]}
    s4 = L(r, "s4_trios")
    trios = []
    for t in s4["candidate_trios"]:
        mem = []
        for m in t["members"]:
            s = st[m["stakeholder_id"]]
            txt = s["who_ja"] + s["contact_point_ja"] + s["stakes_ja"]
            mem.append({"sid": m["stakeholder_id"], "claim": m["claim_id"], "who": s["who_ja"][:40],
                        "shift_topic": bool(SHIFT.search(s["who_ja"] + s["contact_point_ja"])),
                        "institution": [k for k, rx in INST.items() if rx.search(s["who_ja"])]})
        trios.append({"trio_id": t["trio_id"], "selected": t["trio_id"] == s4["selected_trio_id"], "members": mem,
                      "n_shift_topic": sum(m["shift_topic"] for m in mem),
                      "n_institution": sum(1 for m in mem if m["institution"]),
                      "n_students": sum(1 for m in mem if "高校生" in m["who"] or "生徒" in m["who"])})
    s5 = L(r, "s5_personas"); s6 = L(r, "s6_voices")
    fin = s6["final_voices"]
    sents = []
    for k, v in fin.items():
        ss = [x for x in re.split(r"(?<=[。!?？!])", v) if x.strip()]
        sents.append(round(len(v) / max(1, len(ss)), 1))
    out[r] = {"n_stakeholders": len(st), "n_claims": L(r, "s3_claims")["n_claims"], "factual_risk_yes": L(r, "s3_claims")["n_factual_risk_yes"],
              "coverage": [L(r, "s2_coverage")["n_covered"], L(r, "s2_coverage")["n_listed"]],
              "trios": trios, "selected_why": s4["selected_trio_id"],
              "rework_count": s5["rework_count"], "first_person_redo": s5["log"].get("first_person_redo"), "first_person_duplicates_final": s5["overlaps"]["first_person_duplicates"],
              "first_persons": s5["overlaps"]["first_persons"], "naturalness_flags": s5["naturalness_flags_total"],
              "structure_fire_before": s6["structure_tags_before"]["fire"], "structure_fire_after": s6["structure_tags_after"].get("fire"),
              "structure_regen_slot": s6["structure_regen"]["slot"] if s6.get("structure_regen") else None,
              "gate": s6["gate_status"], "gate_n_judgements": s6["gate_history_n"],
              "mean_sentence_chars": sents, "chars": [len(v) for v in fin.values()],
              "closing_after": [s6["structure_tags_after"]["tags"][k]["closing_type"] for k in fin],
              "opening_after": [s6["structure_tags_after"]["tags"][k]["opening_type"] for k in fin],
              "development_after": [s6["structure_tags_after"]["tags"][k]["development_type"] for k in fin]}
print(json.dumps(out, ensure_ascii=False, indent=1))
