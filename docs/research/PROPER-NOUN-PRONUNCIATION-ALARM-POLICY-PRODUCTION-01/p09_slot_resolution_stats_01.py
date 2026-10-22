# -*- coding: utf-8 -*-
"""OF-PNAP-P-09(0円集計): 保存済みtts_generation_results.json(全run)の attempts_log から、
「attempt k で固有名詞のみ不一致(primary_1 が ASR_VALIDATION_UNCERTAIN ∧ entity_like_source あり ∧ 未verified)だったsegment」が
後続slotで解消(verified)した率を数える。Fable規則: 全体でslot2解消率>=25% なら ALARM_ACCEPT_MIN_SLOT=2、未満なら1。読取のみ。"""
import glob, json, collections, os, sys

paths = [p for p in glob.glob("**/tts_generation_results.json", recursive=True) if ".venv" not in p]
seg = []   # 1 segment = attempts_log を持つentry
def walk(x, p, path):
    if isinstance(x, dict):
        if isinstance(x.get("attempts_log"), list) and x["attempts_log"]:
            seg.append((p, path, x))
        for k, v in x.items():
            if k in ("attempts_log", "standard_attempts_log", "fallback_attempts_log"):
                continue
            walk(v, p, path + "/" + str(k))
    elif isinstance(x, list):
        for i, v in enumerate(x):
            walk(v, p, path + f"[{i}]")
for p in paths:
    try:
        walk(json.load(open(p, encoding="utf-8")), p, "")
    except Exception:
        pass

sys.path.insert(0, ".")
import er006_preprod_hardening_01_validation as val

def entity_only(att, canon):
    """attemptが『固有名詞のみ不一致で未verified』か(audit保存のclassification=ASR_VALIDATION_UNCERTAIN ∧ 現行判定器での再分類が
    全diff entity_like)。canon=entryのtext/canonical_text(TTS整形差は無視できる程度)。"""
    if att.get("verified") or att.get("audio_classification") != "ASR_VALIDATION_UNCERTAIN" or not att.get("asr_text") or not canon:
        return False
    try:
        r = val.classify_asr_match(canon, att["asr_text"])
    except Exception:
        return False
    ds = r.protected.content_word_diffs
    return r.classification == "ASR_VALIDATION_UNCERTAIN" and bool(ds) and all(d.get("entity_like") for d in ds)

def family(p):
    return "X" if p.startswith("er019_output") else "Z" if p.startswith("er026_output") or "family_z" in p else "other"

stats = collections.defaultdict(lambda: collections.Counter())
dedup = set()
for p, path, e in seg:
    atts = e["attempts_log"]
    key = (e.get("sha256"), e.get("canonical_text") or e.get("text"), tuple(a.get("asr_text") for a in atts))
    if key in dedup:
        continue
    dedup.add(key)
    fam = family(p)
    canon = e.get("canonical_text") or e.get("text")
    first = next((n for n, a in enumerate(atts) if entity_only(a, canon)), None)
    if first is None:
        continue
    for scope in (fam, "ALL"):
        st = stats[scope]
        st["entity_only_failed_segments"] += 1
        later = atts[first + 1:]
        if not later:
            st["no_later_attempt"] += 1
        elif later[0].get("verified"):
            st["resolved_at_next_slot"] += 1
        elif len(later) > 1 and later[1].get("verified"):
            st["resolved_at_slot_plus2"] += 1
        else:
            st["unresolved_after_all_attempts"] += 1
# HR queue(最終slotまで解消しなかったsegment)を unresolved として追加(生存者バイアス補正: 解消例はresultsにだけ残り、未解消はHR queueにだけ残るため)
seen_canon = {(e.get("canonical_text") or e.get("text")) for _p, _path, e in seg}
hrq = "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl"
hr_added = 0
hr_seen = set()
if os.path.exists(hrq):
    for line in open(hrq, encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        canon = r.get("canonical_text")
        wp = r.get("wav_path", "")
        if not canon or canon in seen_canon or canon in hr_seen or "er026_pscr_outer" in wp or "\Temp\\" in wp:
            continue
        prim = next((s_ for s_ in (r.get("steps") or []) if s_.get("step") == "primary_1"), None)
        if not prim or not prim.get("text"):
            continue
        if entity_only({"asr_text": prim["text"], "audio_classification": "ASR_VALIDATION_UNCERTAIN", "verified": False}, canon):
            hr_seen.add(canon)
            hr_added += 1
            for scope in ("ALL", "HRQ"):
                stats[scope]["entity_only_failed_segments"] += 1
                stats[scope]["unresolved_after_all_attempts"] += 1
out = {"hr_queue_unresolved_segments_added": hr_added, "files": len(paths), "segments_with_attempts_log": len(dedup)}
for k, c in stats.items():
    base = c["entity_only_failed_segments"] - c["no_later_attempt"]
    out[k] = {**c, "denominator_with_later_attempt": base,
              "slot2_resolution_rate": round(c["resolved_at_next_slot"] / base, 4) if base else None,
              "slot2or3_resolution_rate": round((c["resolved_at_next_slot"] + c["resolved_at_slot_plus2"]) / base, 4) if base else None}
rate = out.get("ALL", {}).get("slot2_resolution_rate")
out["fable_rule"] = "ALARM_ACCEPT_MIN_SLOT=2 if overall slot2 resolution >= 0.25 else 1"
out["applied_min_slot"] = 2 if (rate is not None and rate >= 0.25) else 1
json.dump(out, open("docs/research/PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01/p09_slot_resolution_stats_01_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
