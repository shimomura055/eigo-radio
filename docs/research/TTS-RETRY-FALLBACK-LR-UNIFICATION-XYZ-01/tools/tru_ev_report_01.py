# -*- coding: utf-8 -*-
"""evidence JSON + _aggregate_01.json から EVIDENCE_{X,Y,Z}_01.md / COST_01.md / HR_IMPACT_01.md の表を生成(API 0)。"""
import glob, json, os, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
ER = f"{BASE}/evidence_runs"
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(f"{BASE}/../../.."))
import tru_ev_aggregate_01 as agg
import tru_ev_core_01 as core
CASES = agg.CASES


def sty_seq(ev, clip):
    at = agg.clip_attempts(ev, clip)
    letters, seq = {}, []
    for a in at:
        s = a.get("style_sha")
        if s not in letters:
            lab = core.label_style(a.get("style_head", ""), s)
            letters[s] = "ABCDEFG"[len(letters)] + (f"[{lab}]" if lab else "")
        seq.append(letters[s])
    return "".join(x[0] for x in seq) if not any("[" in x for x in seq) else ",".join(seq)


def row(cid, d, res):
    case = CASES[cid.split(" ")[0]]
    ev = d.get("main") or d.get("resume") or {}
    clip = case["segments"][0]
    r = res.get(cid, {})
    fin = agg.status_of(ev, clip)
    cds = [round(c.get("actual_seconds") or 0) for c in ev.get("cooldown_events") or []]
    g = (ev.get("gate_observation") or {})
    mine = [x for x in (g.get("my_segment_blocked") or []) if x.get("violations") != ["NO_SEGMENT_RECORD"]]     # 未生成の他segment(NO_SEGMENT_RECORD)は対象外
    warns = [w.get("warning") for w in (g.get("my_segment_warnings") or [])]
    gate = ("BLOCKなし" if not mine else "BLOCK(" + ";".join(f"{x['segment']}:{'+'.join(x['violations'])}" for x in mine) + ")") + (f" WARN({','.join(warns)})" if warns else "")
    if g.get("error"):
        gate = "結果未保存(STOP中断のためGate対象なし)"
    elif case["family"] == "Z" and (g.get("m2_complete") or g.get("audio_gate")):
        zb = (g.get("audio_gate") or {}).get("BLOCK") or (g.get("m2_complete") or {}).get("BLOCK")
        gate = ("Z Gate BLOCK(" + str(zb).split(":", 1)[0] + (":" + str(zb).split("未採択=")[1].strip("[]'") if "未採択=" in str(zb) else ":結果ファイル未生成") + ")") if zb else "Z Gate PASS(m2_complete/audio_gate)"
    if (g.get("std_chunk_slowdown_gate") or {}).get("status") and not mine:
        gate += " 減速Gate当該chunk違反なし"
    sh = (r.get("checks") and next((c for c in r["checks"] if c["check"].startswith("共有Gate")), None))
    return {"id": cid, "family": case["family"], "level": case["level"], "scenario": case["scenario"], "leaf": case["leaf"], "policy": case["policy"], "clip": clip,
            "tts": r.get("tts"), "waits": cds, "lr": ev.get("lr_count"), "hrq": ev.get("hrq_rows"), "style": sty_seq(ev, clip), "final": fin,
            "gate": gate, "verdict": r.get("verdict"), "jpy": (ev.get("cost") or {}).get("jpy"), "wall": ev.get("wall_seconds")}


def main():
    data = agg.load_all()
    res = json.load(open(f"{ER}/_aggregate_01.json", encoding="utf-8"))["cases"]
    rows = []
    for cid, d in data.items():
        if cid.split(" ")[0] in CASES:
            rows.append(row(cid, d, res))
    json.dump(rows, open(f"{ER}/_rows_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(rows), "rows")


if __name__ == "__main__":
    main()
