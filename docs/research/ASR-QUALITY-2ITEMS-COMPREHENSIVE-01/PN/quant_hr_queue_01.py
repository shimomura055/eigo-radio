# -*- coding: utf-8 -*-
"""ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 PN 委任_01: 保存HR queue(API 0)に現行PNAPを適用し、不受理理由・証拠源依存を集計する。read-only。"""
import json, sys, os, collections
sys.path.insert(0, ".")
import er006_preprod_hardening_01_validation as val
import er103_proper_noun_alarm_policy_01 as pol
import er020_tts_retry_local_rewrite_01 as rw

OUT = "docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/PN/quant_hr_queue_01_result.json"
Q = "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl"
L = json.load(open("er006_output/pronunciation_ledger_01/ledger.json", encoding="utf-8"))
def ledger_set(excl=frozenset()):
    s = set()
    for e in L.values():
        if e.get("ledger_disabled") or e.get("entity_type") == "ja_reading_katakana":
            continue
        for t in pol._fold(e["surface"]).split():
            t = t.strip("'")
            if t not in excl:
                s.add(t)
    return frozenset(s)
LEDGER = ledger_set()
rows = [json.loads(l) for l in open(Q, encoding="utf-8") if l.strip()]
out = []
def run(r, ledger):
    steps = r.get("steps") or []
    prim = next((s for s in steps if s.get("step") == "primary_1"), None)
    sec = [s for s in steps if s.get("provider") == "azure" and s.get("text")]
    if not prim or prim.get("text") is None:
        return None
    canon = r["canonical_text"]
    sec_text = sec[-1]["text"] if sec else None
    cp = val.classify_asr_match(canon, prim["text"])
    cs = val.classify_asr_match(canon, sec_text) if sec_text else None
    try:
        role = rw.resolve_narrative_role(r.get("segment_id")) if r.get("segment_id") else "FULL_STORY"
    except Exception:
        role = "FULL_STORY"
    d = pol.evaluate_alarm_eligibility(canonical_text=canon, primary_cls=cp, secondary_cls=cs, primary_text=prim["text"],
        secondary_text=sec_text, judge_state="NG_BOTH", judge_reason_code="secondary_not_accepted", role=role or "FULL_STORY",
        enabled=True, ledger_surfaces=ledger, p3_entry=("p3_primary_ng" if not cp.should_pass else "force_secondary"))
    return d, cp, cs
for i, r in enumerate(rows):
    wp = r.get("wav_path", "").replace("\\", "/")
    contaminated = ("er026_pscr_outer" in wp) or ("/Temp/" in wp) or wp.startswith("C:")
    res = run(r, LEDGER)
    if res is None:
        out.append({"i": i, "contaminated": contaminated, "skip": "no_primary", "ts": r.get("timestamp")}); continue
    d, cp, cs = res
    res0 = run(r, frozenset())
    d0 = res0[0]
    pd = [(x["canonical"], x["asr"], bool(x["entity_like"])) for x in cp.protected.content_word_diffs]
    out.append({"i": i, "contaminated": contaminated, "ts": r.get("timestamp"), "wav": wp[-90:], "final_status": r.get("final_status"),
        "accept": d.accept, "reason": d.reason, "accept_noledger": d0.accept, "reason_noledger": d0.reason, "detail": d.detail,
        "evidence": [x.evidence for x in d.diffs], "diffs": [(x.canonical, x.asr_primary, x.asr_secondary) for x in d.diffs],
        "pd": pd, "canon": r["canonical_text"][:140], "prim_cls": cp.classification, "entity_like_source": r.get("entity_like_source")})
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
real = [o for o in out if not o["contaminated"] and "skip" not in o]
print("rows", len(rows), "real", len(real), "contaminated/skip", len(out) - len(real))
print("current-ledger accept", sum(o["accept"] for o in real), "reasons", collections.Counter(o["reason"] for o in real).most_common())
print("empty-ledger accept", sum(o["accept_noledger"] for o in real), "reasons", collections.Counter(o["reason_noledger"] for o in real).most_common())
print("accept evidence labels", collections.Counter(e for o in real if o["accept"] for e in o["evidence"]).most_common())
print("--- NO_PROPER_NOUN_EVIDENCE rows (current ledger)")
for o in real:
    if o["reason"] == "NO_PROPER_NOUN_EVIDENCE":
        print(o["i"], o["ts"][:10], o["detail"], o["pd"], "|", o["canon"][:100])
