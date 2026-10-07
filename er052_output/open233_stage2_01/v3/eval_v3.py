# -*- coding: utf-8 -*-
"""STAGE2-01 委任_03 T2 集計: v3 replay(v3/runs)と段階2のv2保存値(replay_dev/stage3_rewrite/*_on.json)を同じ監査規則で並べる。
監査=v3規則(役割クラス比較+語り枠保持+極性・数値・形式)の決定論再実行。出力: v3/eval_v3.json、標準出力にMarkdown表。"""
import glob
import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import replay_lib as L  # noqa: E402

cap2, OUT = L.cap2, L.OUT
cache_dir = HERE / "entity_class_cache"


def ctx_for(ledger):
    p = cache_dir / (cap2._ledger_sha(ledger) + ".json")
    return {"classes": json.loads(p.read_text(encoding="utf-8"))["classes"]}


def audit(rec):
    run, ledger, art = L.load_run(rec["run"])
    vocab = cap2.proper_noun_vocab(ledger, art)
    b, a = rec.get("before_fragment"), rec.get("after_fragment")
    if not (rec["guard_ok"] and b and a):
        return None
    kind = "title" if b.lstrip().startswith("#") else ("hook" if rec["section_type"] == "hook" else rec["section_type"])
    r3 = cap2.four_checks(kind, b, a, vocab, art, ctx_for(ledger))
    r2 = cap2.four_checks(kind, b, a, vocab, art)
    return {"v3_ok": r3["ok"], "v3_violations": r3["violations"], "v3_reasons": r3["v3"]["role_reasons"], "frame_lost": r3["v3"]["frame_lost"],
            "v2_ok": r2["ok"], "v2_violations": r2["violations"], "kind": kind}


def load(globpat):
    rows = []
    for f in sorted(glob.glob(globpat)):
        d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        if "guard_ok" in d:
            d["_file"] = pathlib.Path(f).name
            rows.append(d)
    return rows


def summarize(rows, label):
    out = {"label": label, "n": len(rows), "accepted": 0, "stop": 0, "deleted_sentences": 0, "violations_v3_audit": [], "rows": []}
    for r in rows:
        au = audit(r)
        out["accepted"] += 1 if r["guard_ok"] else 0
        out["stop"] += 1 if r["exhausted"] else 0
        out["deleted_sentences"] += r["deleted_sentences"] + (1 if r.get("hook_last_resort_delete") else 0) * 0
        row = {"file": r["_file"], "i": r.get("i"), "section": r["section_type"], "guard_ok": r["guard_ok"], "exhausted": r["exhausted"],
               "before": r.get("before_fragment"), "after": r.get("after_fragment"), "audit": au,
               "regen": (r.get("structural_rules") or {}).get("regen_calls"),
               "rejected_levels": (r.get("structural_rules") or {}).get("rejected_levels"),
               "check_log": (r.get("structural_rules") or {}).get("checks"),
               "recheck": (r.get("recheck") or {}).get("overall_status"), "cost": r.get("total_cost_jpy")}
        if au and not au["v3_ok"]:
            out["violations_v3_audit"].append({"file": r["_file"], "before": r.get("before_fragment"), "after": r.get("after_fragment"),
                                              "violations": au["v3_violations"], "reasons": au["v3_reasons"]})
        out["rows"].append(row)
    out["cost_jpy"] = round(sum((r.get("total_cost_jpy") or 0) for r in rows), 3)
    return out


def main():
    v3 = load(str(HERE / "runs" / "*.json"))
    tg = json.loads((OUT / "eval" / "stage3_targets.json").read_text(encoding="utf-8"))
    for r in v3:
        r.setdefault("i", int(r["_file"].split("_")[0][1:]))
    v2 = [r for r in load(str(OUT / "replay_dev" / "stage3_rewrite" / "*_on.json"))
          if (r["_file"].startswith(tuple(f"t{i}_" for i in range(7))))]
    for r in v2:
        r["i"] = int(r["_file"].split("_")[0][1:])
    res = {"v3": summarize(v3, "v3(規則=2)"), "v2_stage2": summarize(v2, "v2(段階2保存値、v3規則で再監査)")}
    # 盲点2種の実replay再発(v3受理出力のうち、役割クラスをまたぐ・語り枠消失・一般名詞入替)
    (HERE / "eval_v3.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    for k, v in res.items():
        print(f"## {v['label']}: n={v['n']} accepted={v['accepted']} STOP(exhausted)={v['stop']} 削除文={v['deleted_sentences']} "
              f"v3監査違反={len(v['violations_v3_audit'])} 費用=¥{v['cost_jpy']}")
        for x in v["violations_v3_audit"]:
            print("  VIOL", x["file"], x["violations"], x["reasons"], "|", (x["before"] or "")[:60], "=>", (x["after"] or "")[:80])
    print()
    print("| i | rep | section | v3: 結果 | 再生成 | v3出力(after) | v2出力(after、v3監査) |")
    print("|---|---|---|---|---|---|---|")
    v2m = {(r["i"], r["rep"]): r for r in v2}
    for r in sorted(res["v3"]["rows"], key=lambda x: (x["i"], x["file"])):
        rep = int(r["file"].split("_r")[1][0])
        o = v2m.get((r["i"], rep))
        o_after = (o or {}).get("after_fragment")
        oa = audit(o) if o else None
        print(f"| {r['i']} | {rep} | {r['section']} | {'受理' if r['guard_ok'] else ('STOP' if r['exhausted'] else 'NG')} | {r['regen']} | "
              f"{(r['after'] or '-')[:70]} | {(o_after or ('STOP' if o and o['exhausted'] else '-'))[:70]}"
              f"{'' if not oa or oa['v3_ok'] else ' [v3違反:' + ','.join(oa['v3_violations']) + ']'} |")


if __name__ == "__main__":
    main()
