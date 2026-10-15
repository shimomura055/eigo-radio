# -*- coding: utf-8 -*-
"""AUW 委任_06b: evidence_06b 全 run の判定を集計(API 0)。
- 受理(PASS/PASS_WITH_WARNING)のうち 値ガード DIFF / 否定差 のもの = 「数値・否定の誤PASS」
- 独立 oracle: 受理 clip の canonical と 採用転写(secondary_confirmed なら Secondary、他は Primary)で 数字集合・否定語の有無が異なるもの(等価表記は除外)
- 「旧PASS->新NG」候補: 同一 attempt で Primary passed=True なのに最終 state が NG_* のもの
- Secondary 同一wav 重複: usage_log.jsonl の azure sha 重複
使い方: python er078_auw_aggregate_06b.py > <out>"""
import glob
import json
import os
import re

E = "er058_output/unified_all_roles_production_wiring_01/evidence_06b"
NUMW = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
        "twelve": 12, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "hundred": 100}
JANUM = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
NEG_EN = re.compile(r"\b(not|no|never|n't|cannot|without)\b|n't", re.I)
NEG_JA = re.compile(r"(ない|ません|なかった|でない|ずに)")


def nums(t):
    t = (t or "").lower().replace(",", "")
    out = set(int(x) for x in re.findall(r"(?<![\d.])\d+(?![\d.])", t))
    out |= {NUMW[w] for w in re.findall(r"[a-z]+", t) if w in NUMW}
    out |= {JANUM[c] for c in t if c in JANUM}
    return out


def neg(t, lang):
    return bool((NEG_JA if lang == "ja" else NEG_EN).search(t or ""))


def walk(doc):
    for k, e in (doc.get("segments") or {}).items():
        if isinstance(e, dict):
            yield k, e
    for rank, kp in (doc.get("key_phrases") or {}).items():
        for sub, e in (kp or {}).items():
            if isinstance(e, dict):
                yield f"kp{rank}_{sub}", e


def main():
    rows, attempts = [], []
    for f in glob.glob(f"{E}/**/tts_generation_results.json", recursive=True):
        if "attempt0" in f:
            continue
        d = json.load(open(f, encoding="utf-8"))
        run = f.replace("\\", "/").split("evidence_06b/")[1].split("/")[0]
        for k, e in walk(d):
            aj = e.get("asr_judgement")
            if aj:
                rows.append((run, k, e, aj))
    for f in glob.glob(f"{E}/**/attempt_history.jsonl", recursive=True):
        run = f.replace("\\", "/").split("evidence_06b/")[1].split("/")[0]
        for l in open(f, encoding="utf-8"):
            try:
                r = json.loads(l)
            except ValueError:
                continue
            for a in r.get("attempts_detail") or []:
                if a.get("asr_judgement"):
                    attempts.append((run, r.get("segment_id"), a["asr_judgement"]))
    states = {}
    false_num_neg, oracle_mismatch, primary_pass_final_ng = [], [], []
    for run, k, e, aj in rows:
        states[aj["state"]] = states.get(aj["state"], 0) + 1
        if aj["state"] in ("PASS", "PASS_WITH_WARNING"):
            fg = aj.get("final_gate") or {}
            if fg.get("value_guard") == "DIFF" or fg.get("negation_diff"):
                false_num_neg.append((run, k))
            canon = e.get("canonical_text") or e.get("text") or ""
            adopted = (aj.get("secondary") or {}).get("text") if aj.get("reason_code") == "secondary_confirmed" else (aj.get("primary") or {}).get("text")
            lang = aj.get("lang") or "en"
            if adopted and canon:
                if nums(canon) != nums(adopted) or neg(canon, lang) != neg(adopted, lang):
                    oracle_mismatch.append({"run": run, "clip": k, "canonical": canon, "adopted": adopted, "state": aj["state"], "reason": aj.get("reason_code")})
    att_states = {}
    for run, seg, aj in attempts:
        att_states[aj["state"]] = att_states.get(aj["state"], 0) + 1
        if (aj.get("primary") or {}).get("passed") and str(aj["state"]).startswith("NG"):
            primary_pass_final_ng.append((run, seg, aj["state"], aj.get("reason_code")))
    dup = {}
    for f in glob.glob(f"{E}/**/usage_log.jsonl", recursive=True):
        run = f.replace("\\", "/").split("evidence_06b/")[1].split("/")[0]
        by = {}
        for l in open(f, encoding="utf-8"):
            r = json.loads(l)
            if r.get("provider") == "azure" and r.get("sha"):
                by[r["sha"]] = by.get(r["sha"], 0) + 1
        dup[run] = {"azure_calls": sum(by.values()), "distinct_wavs": len(by), "dup_wavs": sum(1 for v in by.values() if v > 1)}
    out = {"final_entries_with_asr_judgement": len(rows), "final_entry_states": states, "attempt_level_judgements": len(attempts), "attempt_states": att_states,
           "false_accept_value_or_negation_by_final_gate": false_num_neg, "oracle_number_negation_mismatch_among_accepted": oracle_mismatch,
           "primary_passed_but_final_NG(旧PASS->新NG候補)": primary_pass_final_ng, "azure_duplicates_by_run": dup}
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
