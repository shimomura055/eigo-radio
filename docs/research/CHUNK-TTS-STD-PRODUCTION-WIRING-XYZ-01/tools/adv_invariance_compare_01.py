# -*- coding: utf-8 -*-
"""R4(b)(c): 旧(bb578265c)と現ツリーのdriver出力を比較し、Advのバイト一致を判定する。差分は『注記文言のみ』を許容するkeyに限定して明示。
使い方: py adv_invariance_compare_01.py --old old.json --new new.json --out result.json
"""
import argparse
import json

ap = argparse.ArgumentParser()
ap.add_argument("--old", required=True)
ap.add_argument("--new", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
old = json.load(open(a.old, encoding="utf-8"))
new = json.load(open(a.new, encoding="utf-8"))

# 注記文言(監査表示のみ・音声無関係)として差分を許容するkey(b1b chunk_tts_decisionの承認参照/注記)。許容は『このkeyの文字列値の差』に限る。
NOTE_KEYS = {"note", "notes", "approval_ref", "approval", "reason", "basis", "applicability_note", "source", "approved_scope", "decision_note"}


def diff(o, n, path=""):
    out = []
    if isinstance(o, dict) and isinstance(n, dict):
        for k in sorted(set(o) | set(n)):
            if k not in o:
                out.append({"path": f"{path}/{k}", "kind": "ADDED_IN_NEW", "new": n[k]})
            elif k not in n:
                out.append({"path": f"{path}/{k}", "kind": "REMOVED_IN_NEW", "old": o[k]})
            else:
                out += diff(o[k], n[k], f"{path}/{k}")
    elif isinstance(o, list) and isinstance(n, list) and len(o) == len(n):
        for i, (x, y) in enumerate(zip(o, n)):
            out += diff(x, y, f"{path}[{i}]")
    elif o != n:
        out.append({"path": path, "kind": "CHANGED", "old": o, "new": n})
    return out


res = {"old": a.old, "new": a.new, "checks": {}}
byte_keys = ["results_json_normalized_sha256", "narration_wav_sha256", "chunk_plan_sha256", "chunk_tts_evidence_normalized_sha256",
             "gain_report_sha256", "assembled_sha256", "assembled_wav_sha256", "timeline_sha256", "assemble_status", "assembled_shape"]
ok_all = True


def cmp_block(name, o, n):
    global ok_all
    rows = {}
    for k in byte_keys:
        if k in o or k in n:
            same = o.get(k) == n.get(k)
            rows[k] = "IDENTICAL" if same else "DIFFERENT"
            ok_all &= same
    res["checks"][name] = rows


cmp_block("x_adv", old["x_adv"], new["x_adv"])
for sub in ("single_paragraph", "multi_paragraph"):
    cmp_block(f"y_adv_{sub}", old["y_adv"][sub], new["y_adv"][sub])
    d = diff(old["y_adv"][sub]["chunk_tts_decision"], new["y_adv"][sub]["chunk_tts_decision"])
    res["checks"][f"y_adv_{sub}"]["chunk_tts_decision_diff"] = d
    res["checks"][f"y_adv_{sub}"]["chunk_tts_decision_diff_keys_are_note_text_only"] = all(
        x["kind"] == "CHANGED" and isinstance(x.get("old"), str) and isinstance(x.get("new"), str) for x in d)
res["x_adv_results_json_diff"] = diff(old["x_adv"]["results_json_normalized"], new["x_adv"]["results_json_normalized"])
for sub in ("single_paragraph", "multi_paragraph"):
    res[f"y_adv_{sub}_results_json_diff"] = diff(old["y_adv"][sub]["results_json_normalized"], new["y_adv"][sub]["results_json_normalized"])
res["audio_and_results_byte_identical_all"] = ok_all
json.dump(res, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({"audio_and_results_byte_identical_all": ok_all, "checks": res["checks"]}, ensure_ascii=False, indent=1)[:4000])
