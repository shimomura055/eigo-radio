"""委任_07: labels_w1/2/3.json -> labels_merged.json (aggregate_report_abcde_01.py形式 {"labels":[...]})。
Fable突合判定1〜5を上書き(confirmed_by=fable_2026-10-06)、6はUNDECIDABLE維持、
rewrite_neededは実Rewrite対象(rewrite_records.handoff.checker_claim_text)のみ確定。¥0。"""
import glob
import json
import os
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(os.path.dirname(BASE), "runs")
FB = "fable_2026-10-06"


def norm(s):
    return unicodedata.normalize("NFKC", s or "").lower().strip()


merged = []
for w in (1, 2, 3):
    d = json.load(open(os.path.join(BASE, "labels_w%d.json" % w), encoding="utf-8"))
    for k, v in d.items():
        run, cyc, claim = k.split("|", 2)
        e = dict(v)
        e.update({"run": run, "cycle": int(cyc), "claim": claim, "key": k, "worker": "w%d" % w})
        merged.append(e)
assert len(merged) == 123, len(merged)


def setf(e, sev, tp, tc, reason, rn=None):
    e.update({"severity_eval": sev, "true_problem": tp, "true_critical": tc, "reason": reason,
              "confirmed_by": FB, "label_source": e.get("label_source", "") + "+" + FB})
    if rn is not None:
        e["rewrite_needed"] = rn


APPLIED = []
for e in merged:
    c = e["claim"]
    r = e["run"]
    if r == "meta_run03_advanced" and "restored the human concierge feature to the way it had been before" in c:
        setf(e, "重大", "Y", "Y", "HC-012ロールバック(撤回)を復元と記述=方向反転、A5-0同型", "N_A")
        APPLIED.append("判定1")
    elif r == "meta_run03_standard" and "inappropriate comments about race during calls" in c:
        e["confirmed_by"] = FB
        e["reason"] += " [Fable: 複数化+報告元不明、重大/Y/Y維持]"
        APPLIED.append("判定2")
    elif r == "neg3_hormuz_prodrunner_b1b" and "20 percent reimbursement" in c:
        e["confirmed_by"] = FB
        e["reason"] += " [Fable: Ledger一致、問題なし/N/N維持(見本Bとの差異: 報告元・日付ともLedger一致)]"
        APPLIED.append("判定3")
    elif r == "neg7_meta_prodrunner_b1b" and "handles everything for you" in c:
        setf(e, "軽微", "Y", "N", "Hook修辞だがHC-002の範囲を超え万能と読める(境界)", "N_A")
        APPLIED.append("判定4")
    elif r == "neg2_meta_refresh_a2" and "enjoyed the ease of AI" in c:
        setf(e, "問題なし", "N", "N", "Factを含まない修辞", "N_A")
        APPLIED.append("判定5")
    elif r == "neg1_meta_b3prod_a2" and "alone finds difficult" in c:
        e["confirmed_by"] = ""
        e["note"] = "判定6: UNDECIDABLE維持(Fable保留、材料はRESULT_PACKET)"
        APPLIED.append("判定6")

# 判定7: 実Rewrite対象のみrewrite_needed確定
RW = []
for p in sorted(glob.glob(os.path.join(RUNS, "*.json"))):
    d = json.load(open(p, encoding="utf-8"))
    run = os.path.splitext(os.path.basename(p))[0]
    for c in d["cycles"]:
        for w in c.get("rewrite_records", []):
            RW.append((run, c["cycle"], norm((w.get("handoff") or {}).get("checker_claim_text", ""))))
hit = 0
for e in merged:
    if (e["run"], e["cycle"], norm(e["claim"])) in RW:
        s = e["severity_eval"]
        e["rewrite_needed"] = "Y" if s in ("重大", "軽微") else ("N" if s == "問題なし" else "UNDECIDABLE")
        hit += 1
    elif e["rewrite_needed"] in ("Y", "UNDECIDABLE", "N") and e["run"]:
        e["rewrite_needed"] = "N_A"  # Rewrite対象外はrewrite_needed評価対象外
assert hit == len(RW) == 6, (hit, len(RW))
json.dump({"labels": merged, "applied": APPLIED, "n": len(merged)}, open(os.path.join(BASE, "labels_merged.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(merged), APPLIED, hit)
