# -*- coding: utf-8 -*-
"""(02: Opus P-01..P-04反映後の再校正)保存済みHR queue(API 0)に対し、アラーム受理判定(er103_proper_noun_alarm_policy_01)を適用して受理/不受理を数える。
読取のみ。Production/Ledger/HR queueは書かない。"""
import json, sys, os, collections
sys.path.insert(0, ".")
import er006_preprod_hardening_01_validation as val
import er103_proper_noun_alarm_policy_01 as pol

Q = "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl"
L = json.load(open("er006_output/pronunciation_ledger_01/ledger.json", encoding="utf-8"))
LEDGER = set()
for e in L.values():
    if e.get("ledger_disabled") or e.get("entity_type") == "ja_reading_katakana":
        continue
    for t in pol._fold(e["surface"]).split():
        LEDGER.add(t.strip("'"))
LEDGER = frozenset(LEDGER)
rows = [json.loads(l) for l in open(Q, encoding="utf-8") if l.strip()]
out = []
for i, r in enumerate(rows):
    steps = r.get("steps") or []
    prim = next((s for s in steps if s.get("step") == "primary_1"), None)
    sec = [s for s in steps if s.get("provider") == "azure" and s.get("text")]
    contaminated = "er026_pscr_outer" in r.get("wav_path", "") or "\Temp\\" in r.get("wav_path", "")
    canon = r["canonical_text"]
    if not prim or prim.get("text") is None:
        out.append({"i": i, "contaminated": contaminated, "skip": "no_primary"}); continue
    sec_text = sec[-1]["text"] if sec else None
    cp = val.classify_asr_match(canon, prim["text"])
    cs = val.classify_asr_match(canon, sec_text) if sec_text else None
    d = pol.evaluate_alarm_eligibility(
        canonical_text=canon, primary_cls=cp, secondary_cls=cs, primary_text=prim["text"], secondary_text=sec_text,
        judge_state="NG_BOTH", judge_reason_code="secondary_not_accepted", role=(r.get("segment_id") and __import__("er020_tts_retry_local_rewrite_01").resolve_narrative_role(r.get("segment_id")) or "FULL_STORY"), enabled=True, ledger_surfaces=LEDGER,
        p3_entry=("p3_primary_ng" if not cp.should_pass else "force_secondary"))
    out.append({"i": i, "contaminated": contaminated, "final_status": r.get("final_status"), "accept": d.accept, "reason": d.reason,
                "canon": canon[:90], "primary_cls": cp.classification, "secondary_cls": cs.classification if cs else None,
                "diffs": [(x.canonical, x.asr_primary, x.asr_secondary, x.similarity_primary, x.similarity_secondary) for x in d.diffs],
                "detail": d.detail, "pd": [(x["canonical"], x["asr"], x["entity_like"]) for x in cp.protected.content_word_diffs]})
json.dump(out, open("docs/research/PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01/calibrate_replay_02_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for flag in (False, True):
    sub = [o for o in out if o["contaminated"] == flag and "skip" not in o]
    print("contaminated" if flag else "real", len(sub), "accept", sum(o["accept"] for o in sub))
    print(collections.Counter(o["reason"] for o in sub).most_common())
for o in out:
    if not o["contaminated"] and "skip" not in o and (o["accept"] or o["reason"] in ("LOW_SPAN_SIMILARITY","ASR_SPAN_TOO_LONG","CANONICAL_TOKEN_IS_GENERAL_WORD","NO_PROPER_NOUN_EVIDENCE","SECONDARY_NOT_ENTITY_ONLY","PRIMARY_NOT_ENTITY_ONLY")):
        print(o["i"], o["accept"], o["reason"], o["pd"] if not o["accept"] else o["diffs"], "|", o["detail"], "|", o["canon"][:60])
