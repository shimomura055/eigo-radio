# -*- coding: utf-8 -*-
"""AUW 委任_06b: tts_generation_results.json 群から asr_judgement 表(Section x clip)と誤受理チェックを機械集計する(API 0)。
使い方: python er078_auw_tabulate_06b.py <results.json> [...] --out <md>"""
import argparse
import json
import os
import sys


def walk(doc):
    for k, e in (doc.get("segments") or {}).items():
        if isinstance(e, dict):
            yield k, e
    for rank, kp in (doc.get("key_phrases") or {}).items():
        for sub, e in (kp or {}).items():
            if isinstance(e, dict):
                yield f"kp{rank}_{sub}", e


def row(src, key, e):
    aj = e.get("asr_judgement") or {}
    sec = aj.get("secondary") or {}
    fg = aj.get("final_gate") or {}
    return {"src": src, "key": key, "status": e.get("status"), "role": e.get("role") or e.get("clip_kind"), "lang": aj.get("lang") or e.get("language"),
            "has_aj": bool(aj), "state": aj.get("state"), "reason": aj.get("reason_code"), "slot": aj.get("slot"),
            "script_version": aj.get("script_version"), "sec_called": sec.get("called"), "sec_cached": sec.get("cached"),
            "azure_calls": (aj.get("cost") or {}).get("azure_calls"), "value_guard": fg.get("value_guard"), "neg_diff": fg.get("negation_diff"),
            "warnings": aj.get("warnings"), "tts_used": e.get("tts_generations_used"), "n_attempts": len(e.get("attempts") or []),
            "slowdown": e.get("slowdown_applied"), "aj_inherited": "asr_judgement_inherited" in e,
            "deviation": bool(e.get("audio_text_deviation"))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--out", default=None)
    ap.add_argument("--json-out", default=None)
    a = ap.parse_args()
    rows = []
    for f in a.files:
        d = json.load(open(f, encoding="utf-8"))
        src = os.path.relpath(f).replace("\\", "/").split("evidence_06b/")[-1]
        for k, e in walk(d):
            if e.get("clip_kind") == "shell":
                continue
            rows.append(row(src, k, e))
    bad = [r for r in rows if r["status"] == "OK" and r["state"] in ("PASS", "PASS_WITH_WARNING") and (r["value_guard"] == "DIFF" or r["neg_diff"])]
    lines = ["| run | clip | role | lang | status | has asr_judgement | state | reason | slot/ver | Secondary called | azure calls | value_guard | slowdown | tts used |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['src'].split('/audit')[0]} | {r['key']} | {r['role']} | {r['lang']} | {r['status']} | {r['has_aj']} | {r['state']} | {r['reason']} | {r['slot']}/{r['script_version']} | {r['sec_called']} | {r['azure_calls']} | {r['value_guard']} | {r['slowdown']} | {r['tts_used']} |")
    summ = {"n_clips": len(rows), "n_ok": sum(1 for r in rows if r["status"] == "OK"), "n_with_asr_judgement": sum(1 for r in rows if r["has_aj"]),
            "ok_without_asr_judgement": [r["key"] for r in rows if r["status"] == "OK" and not r["has_aj"] and not r["aj_inherited"]],
            "false_accepts_value_or_negation": [r["key"] for r in bad], "n_pww": sum(1 for r in rows if r["state"] == "PASS_WITH_WARNING"),
            "sec_called_clips": sum(1 for r in rows if r["sec_called"])}
    out = "\n".join(lines) + "\n\n```json\n" + json.dumps(summ, ensure_ascii=False, indent=1) + "\n```\n"
    if a.out:
        open(a.out, "w", encoding="utf-8").write(out)
    if a.json_out:
        json.dump({"rows": rows, "summary": summ}, open(a.json_out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(out)


if __name__ == "__main__":
    main()
