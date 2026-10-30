# ASR-FLAP-T-EQUIVALENCE-TRIAL-01 委任_01: 保存済みASR記録から『expected/ASR差分が語中t<->d(flap-t環境)』の実例を集計。API 0・読取専用。
# 母集団: er109_stored_census_01.rows_from_results(全 *tts_generation_results*.json + narration/attempts cascade_steps[Azure転写]) +
#         全 human_review_queue.jsonl の steps(canonical_text x 各ASR転写)。
# 使い方(repo root、.venv): .venv\Scripts\python.exe docs/research/ASR-FLAP-T-EQUIVALENCE-TRIAL-01/tools/flapt_stored_census_01.py --out <json>
import argparse, collections, glob, json, os, sys
sys.path.insert(0, "."); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er109_stored_census_01 as c109
import flapt_equivalence_proto_01 as fl
import er021_en_asr_semantic_equivalence_production_01 as _er021
_er021.append_telemetry_log = lambda *a, **k: None   # 副作用ファイル0: Production telemetry(er021_output/.../telemetry.jsonl)へ追記させない(読取専用census)

def family_of(src):
    p = src.replace("\\", "/").lower()
    for k, f in (("family_x", "X"), ("family_y", "Y"), ("family_z", "Z")):
        if k in p:
            return f
    if p.startswith("er019_output/"):
        return "X"
    if p.startswith("er026_output/"):
        return "Z"
    return "other"

def walk_rows(path):
    """tts_generation_results.json 全体を再帰走査: canonical_text(またはtext)を持つdictの *attempts_log(attempts_log/fallback/minimal/english_lock)
    の各attempt(asr_text + cascade_steps内のazure転写)を行にする。vocab_extra.v3.* と key_phrases.*.english も拾う(rows_from_resultsの取りこぼし補完)。"""
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception:
        return []
    out = []
    def rec(o, trail):
        if isinstance(o, dict):
            canon = o.get("canonical_text") or (o.get("text") if isinstance(o.get("text"), str) else None)
            logs = [(k, v) for k, v in o.items() if k.endswith("attempts_log") and isinstance(v, list)]
            if canon and logs and c109.is_english(canon):
                for k, lst in logs:
                    for a in lst:
                        if not isinstance(a, dict):
                            continue
                        vs = a.get("verified")
                        cls0 = a.get("audio_classification")
                        if a.get("asr_text") is not None:
                            out.append({"src": path.replace("\\", "/"), "seg": "/".join(trail[-2:]) or "seg", "kp": False, "attempt": a.get('attempt'),
                                        "canonical": canon, "asr": a.get("asr_text"), "azure": None, "stored_cls": cls0, "verified": vs,
                                        "final_status": o.get("status")})
                        for st in a.get("cascade_steps") or []:
                            if str(st.get("provider", "")).startswith("azure") and st.get("text") and a.get("asr_text") is not None:
                                out[-1]["azure"] = st.get("text")
            for k, v in o.items():
                rec(v, trail + [str(k)])
        elif isinstance(o, list):
            for i, v in enumerate(o):
                rec(v, trail)
    rec(d, [])
    return out


def hr_rows():
    rows = []
    for f in glob.glob("**/human_review_queue*.jsonl", recursive=True):
        if f.startswith(".venv"):
            continue
        for i, line in enumerate(open(f, encoding="utf-8", errors="replace")):
            try:
                d = json.loads(line)
            except Exception:
                continue
            canon = d.get("canonical_text")
            if not canon or not c109.is_english(canon):
                continue
            for st in d.get("steps") or []:
                t = st.get("text")
                if t:
                    rows.append({"src": f.replace("\\", "/") + f"#L{i+1}", "seg": d.get("segment_id") or d.get("seg") or "hrq", "kp": False,
                                 "attempt": st.get("step"), "canonical": canon, "asr": t, "azure": None,
                                 "stored_cls": st.get("classification"), "verified": False, "final_status": "HR_QUEUE"})
    return rows

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args()
    files = sorted(f for f in glob.glob("**/*tts_generation_results*.json", recursive=True) if not f.startswith(".venv"))
    rows = []
    for f in files:
        rows += c109.rows_from_results(f)
        rows += walk_rows(f)
    _seen = set(); _u = []
    for r in rows:
        k = (r['src'], r.get('attempt'), r['canonical'], r['asr'], r.get('azure'))
        if k in _seen:
            continue
        _seen.add(k); _u.append(r)
    rows = _u
    nres = len(rows)
    rows += hr_rows()
    stats = collections.Counter(); res_rows = []; req_rows = []; norescue_td = []
    declined = []
    seen = set()
    for r in rows:
        stored_ng = (r["stored_cls"] not in c109.PASS_LABELS) and (not r["verified"])
        for which, txt in (("openai", r["asr"]), ("azure", r.get("azure"))):
            if not txt:
                continue
            stats["transcripts"] += 1
            if not stored_ng and which == "openai":
                continue
            if which == "azure" and not stored_ng:
                continue
            stats["ng_transcripts"] += 1
            if c109.current_pass(r["canonical"], txt, r["seg"])[0]:
                continue                       # 現行コードで既にPASS(旧コード由来のNG記録)
            stats["ng_and_now_ng"] += 1
            res = fl.evaluate(r["canonical"], txt)
            if res.decision == "NO_RESCUE" and any(p.reason.startswith(("not_flap_environment", "canonical_multiple_readings")) for p in res.pairs):
                declined.append({"src": r["src"], "seg": r["seg"], "provider": which, "reason": res.reason, "pairs": [(p.canonical, p.asr, p.reason) for p in res.pairs]})
            key = (r["canonical"], txt)
            if res.decision == "NOT_APPLICABLE":
                continue
            # 語中 t<->d 差を含むもの(flap判定が走った)だけ記録
            tdish = any(p.reason not in ("cmu_unresolved",) and ("T" in (p.detail.get("canonical_phones", "") + p.detail.get("asr_phones", "")) ) for p in res.pairs) or res.decision in ("RESCUE", "REQUIRES_EXTRA_EVIDENCE")
            if res.decision == "RESCUE" or res.decision == "REQUIRES_EXTRA_EVIDENCE":
                rec = {"src": r["src"], "seg": r["seg"], "attempt": r["attempt"], "provider": which, "family": family_of(r["src"]),
                       "final_status": r["final_status"], "decision": res.decision, "reason": res.reason,
                       "pairs": [(p.canonical, p.asr, p.decision, p.reason) for p in res.pairs],
                       "canonical_head": r["canonical"][:120], "asr_head": txt[:120], "distinct_key": hash(key)}
                (res_rows if res.decision == "RESCUE" else req_rows).append(rec)
    def summarize(lst):
        d = collections.Counter(); words = collections.Counter(); fam = collections.Counter(); route = collections.Counter(); ds = set(); segs = set(); stopped = set()
        for x in lst:
            ds.add(x["distinct_key"]); segs.add((x["src"].split("#")[0], x["seg"]))
            fam[x["family"]] += 1
            for p in x["pairs"]:
                words[f"{p[0]}->{p[1]}"] += 1
            kind = "KP/vocab(*_en)" if (x["seg"].startswith("kp") or "vocab" in x["seg"] or x["seg"].endswith("_en")) else ("HR_QUEUE" if x["final_status"] == "HR_QUEUE" else "body")
            route[kind] += 1
            if str(x["final_status"]) in ("STOPPED", "HUMAN_REVIEW_LOCKED", "HUMAN_REVIEW_REQUIRED", "HR_QUEUE"):
                stopped.add((x["src"].split("#")[0], x["seg"]))
        return {"rows": len(lst), "distinct_canonical_asr": len(ds), "distinct_src_seg": len(segs), "distinct_src_seg_final_stopped_or_hr": len(stopped),
                "by_family": dict(fam), "by_route": dict(route), "word_pairs": words.most_common(60)}
    _st = {(r["src"], r["seg"]) for r in rows if str(r["final_status"]) in ("STOPPED", "HUMAN_REVIEW_LOCKED", "HUMAN_REVIEW_REQUIRED")}
    _all = {(r["src"], r["seg"]) for r in rows if r["final_status"] != "HR_QUEUE"}
    out = {"population": {"results_rows": nres, "hr_queue_rows": len(rows) - nres, "tts_results_files": len(files),
                          "distinct_segments": len(_all), "distinct_stopped_or_hr_segments": len(_st),
                          "stopped_segments_by_family": dict(collections.Counter(family_of(x[0]) for x in _st))},
           "stats": dict(stats), "RESCUE": summarize(res_rows), "REQUIRES_EXTRA_EVIDENCE": summarize(req_rows),
           "td_diff_declined": {"rows": len(declined), "reasons": collections.Counter(x["reason"] for x in declined).most_common(), "examples": declined[:40]},
           "RESCUE_examples": res_rows[:80], "REQUIRES_EXTRA_EVIDENCE_examples": req_rows[:40]}
    for x in out["RESCUE_examples"] + out["REQUIRES_EXTRA_EVIDENCE_examples"]:
        x.pop("distinct_key", None)
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: out[k] for k in ("population", "stats", "RESCUE", "REQUIRES_EXTRA_EVIDENCE", "td_diff_declined")}, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
