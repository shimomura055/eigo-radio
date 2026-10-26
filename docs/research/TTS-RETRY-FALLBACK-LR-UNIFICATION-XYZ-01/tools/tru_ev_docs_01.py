# -*- coding: utf-8 -*-
"""EVIDENCE_{X,Y,Z}_01.md の表部分 / COST_01.md / HR_IMPACT_01.md のデータ部分を生成(API 0)。ナラティブは手書きファイルに結合する。"""
import json, os, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
ER = f"{BASE}/evidence_runs"
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(f"{BASE}/../../.."))
import tru_ev_aggregate_01 as agg
import tru_ev_report_01 as rep


def load():
    data = agg.load_all()
    res = json.load(open(f"{ER}/_aggregate_01.json", encoding="utf-8"))["cases"]
    return data, res


def fmt_wait(w):
    return "+".join(str(x) for x in w) if w else "-"


def family_table(fam, data, res):
    out = ["| case | Lv | 方針/leaf | シナリオ | TTS | 待機(秒) | LR | HRQ行 | Style列 | 最終 | 方針Gate(M3/Y/Z、当該seg) | 共有Audio Gate(Assemble、当該seg) | 判定 | 実費(円) |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    ids = [k for k in data if k in agg.CASES and agg.CASES[k]["family"] == fam]
    def key(x):
        import re
        p = x.split("-")
        return (p[1], int(re.match(r"\d+", p[2]).group()), p[2])
    for cid in sorted(ids, key=key):
        d = data[cid]
        r = rep.row(cid, d, res)
        ev = d.get("resume") or d.get("main")
        if cid in res and res[cid]["id"].endswith("(resume)") and d.get("main") is None:
            pass
        # E-S6: TTS/待機は kill前(partial)+再開後(resume)の合算。費用はraw_usage_log累計のためresume側の値をそのまま使う(足さない)。
        tts, waits = r["tts"], r["waits"]
        cost = r["jpy"]
        lrc, hrq = r["lr"], r["hrq"]
        if "resume" in d:
            part = f"{ER}/{cid}.partial_before_kill.json"
            p = json.load(open(part, encoding="utf-8")) if os.path.exists(part) else {}
            pre_w = [round(c.get("actual_seconds") or 0) for c in p.get("cooldown_events") or []] + ([round(p.get("sleep_total_seconds", 0))] if not p.get("cooldown_events") else [])
            waits = pre_w + waits
            lrc = res[cid].get("lr") if res.get(cid, {}).get("lr") is not None else (d["resume"].get("lr_count"))
            hrq = d["resume"].get("hrq_rows")
        try:
            sg = agg.shared_gate_segments(agg.CASES[cid], (d.get("main") or d.get("resume"))["run_dir"])
            shared = "対象なし(結果未保存)" if r["final"] is None else ("PASS" if not sg["blocked"] else "BLOCK(" + ";".join(sg["blocked"]) + ")")
        except Exception as ex:
            shared = f"算出不可({type(ex).__name__})"
        out.append(f"| {cid} | {r['level']} | {r['policy']}/{r['leaf']} | {r['scenario']} | {tts} | {fmt_wait(waits)} | {lrc} | {hrq} | {r['style']} | {r['final']} | {r['gate']} | {shared} | {r['verdict']} | {cost} |")
    return "\n".join(out)


def totals(data):
    fam = collections.defaultdict(float)
    prov = collections.defaultdict(float)
    case = {}
    for cid, d in data.items():
        if cid not in agg.CASES:
            continue
        f = agg.CASES[cid]["family"]
        c = 0.0
        for ev in [d.get("resume") or d.get("main")]:      # resume側のcostはraw_usage_log累計
            if ev:
                c += (ev.get("cost") or {}).get("jpy", 0)
                for k, v in ((ev.get("cost") or {}).get("by_provider") or {}).items():
                    prov[k] += v
        case[cid] = round(c, 3)
        fam[f] += c
    return fam, prov, case


if __name__ == "__main__":
    data, res = load()
    for f in "XYZ":
        open(f"{ER}/_table_{f}.md", "w", encoding="utf-8").write(family_table(f, data, res) + "\n")
    fam, prov, case = totals(data)
    print({k: round(v, 3) for k, v in fam.items()}, {k: round(v, 3) for k, v in prov.items()}, round(sum(fam.values()), 3))
