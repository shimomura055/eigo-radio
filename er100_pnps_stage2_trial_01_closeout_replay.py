# -*- coding: utf-8 -*-
"""PNPS Stage 2 委任_10 Closeout (A): 保存済み転写を『本番の判定器』(er006_secondary_asr_01.evaluate_attempt_with_cascade_detail
= Primary P-chain + CS Equivalence + Tier3 + CMU Case A/homophone + M1複数候補 + 統一judge[Secondary Azure許容集合])へ通し、
Human Review(最終slot NG)基準値を取り直す。API 0・Production/HR queue/Store/Ledger/attempt_history不変(実行前後sha256 assert)。
隔離: Ledgerはtmp複製、HUMAN_REVIEW_LOG_PATHはtmp、research/pron_supply fetch/routing.transcribe/Azure STT/local ASRはstub(保存転写を返す)。"""
import hashlib, json, os, re, shutil, sys, tempfile, collections
sys.path.insert(0, os.getcwd())
import er006_asr_provider_routing_01 as routing
import er006_pronunciation_ledger_01 as L
import er006_secondary_asr_01 as sec

OUT = "er100_output/pnps_stage2_trial_01"
CL = OUT + "/closeout"
WATCH = {
    "hr_queue": "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl",
    "ledger": "er006_output/pronunciation_ledger_01/ledger.json",
    "store_manifest": "er006_output/master_audio_store_01/manifest.json",
    "attempt_history": "er011_output/attempt_history.jsonl",
}
M1_WIRED = "2026-10-14"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None


before = {k: sha(v) for k, v in WATCH.items()}

TMP = tempfile.mkdtemp(prefix="pnps_closeout_")
shutil.copyfile(WATCH["ledger"], TMP + "/ledger.json")
L.LEDGER_PATH = TMP + "/ledger.json"
sec.HUMAN_REVIEW_LOG_PATH = TMP + "/hr.jsonl"
sec.pronun_research.research_pronunciations = lambda *a, **k: {"status": "FAILED", "http_status": 401}
sec._pron_supply_fetch = lambda *a, **k: None
sec._connected_speech_equivalence_local_asr_text = lambda w: None   # local ASR転写は保存無し=unavailable


def judge(canon, primary, secondary, wav, segment_id="full_story_part1"):
    routing.transcribe = lambda *a, **k: (primary, None)
    sec.get_full_text_via_azure_stt_with_phrase_list = lambda *a, **k: (secondary, None)
    try:
        d = sec.evaluate_attempt_with_cascade_detail(
            canon, primary, [], wav, language="en-US", cascade_enabled=True,
            enable_connected_speech_equivalence_layer=True, segment_id=segment_id,
            attempt_ctx={"slot": 3, "is_last_slot": True})
    except Exception as e:
        return {"verdict": "ERROR", "error": repr(e)}
    aj = d.get("asr_judgement") or {}
    st = aj.get("state")
    has_sec = secondary is not None
    m1 = (d.get("final_status") == "M1_MULTI_CANDIDATE_ACCEPT") or any(
        "M1_MULTI" in str(s.get("classification", "")) for s in d.get("steps", []))
    if d.get("human_review_required"):
        v = "NG_HR"
    elif st == "PASS":
        v = "PASS"
    elif st == "PASS_WITH_WARNING":
        v = "PASS_WITH_WARNING"
    else:
        v = "NG_HR" if (not d.get("verified")) else "PASS"
    return {"verdict": v, "state": st, "reason_code": aj.get("reason_code"), "final_status": d.get("final_status"),
            "m1_accepted": bool(m1), "secondary_used": has_sec,
            "judged_by": "Primary+Secondary" if has_sec else "Primary only"}


def jl(p):
    return json.load(open(p, encoding="utf-8"))


res = {"meta": {"function": "er006_secondary_asr_01.evaluate_attempt_with_cascade_detail (m1_enabled=True既定, CS Equivalence層 ON, 最終slot ctx)",
                "segment_id_used_for_trial": "full_story_part1(narrative=FULL_STORY role; Tier3適用)",
                "isolation": "Ledger=tmp複製, HR log=tmp, research/pron_supply/transcribe/Azure/local ASR=stub(保存転写)",
                "scope_note": "api_scopeがclipのものはclip単位のcanonical(api_canon)と転写で判定(HR queue行も同様にsegment/clip単位)",
                "m1_wired_date": M1_WIRED}, "items": [], "stored": []}

# ---- Trial音声 ----
for tag, f in [("r2_take1", "r2/gen_take1.json"), ("r2_take2", "r2/gen_take2.json"), ("r2_neg", "r2/gen_neg.json"),
               ("r3", "r3/gen.json"), ("r3b", "r3/gen_b.json")]:
    for x in jl(f"{OUT}/{f}"):
        r = judge(x["api_canon"], x["primary"], x["azure"], x["wav"])
        r.update({"set": tag, "id": x["id"], "take": x.get("take"), "word": x.get("word"), "arm": x.get("arm"),
                  "wrong_supply": x.get("wrong"), "kind": x.get("kind"), "supplied": x.get("supplied"),
                  "primary": x["primary"], "azure": x["azure"], "canon": x["api_canon"]})
        res["items"].append(r)

# ---- 保存HR事象58 ----
rows = [json.loads(l) for l in open(WATCH["hr_queue"], encoding="utf-8") if l.strip()]
excl = jl("er006_output/audio_retry_cascade_prod_01/human_review_queue_exclusions_01.json")
excl_lines = {e["line_number"] for e in excl["excluded_rows"]}
pop = jl(f"{OUT}/o0_population.json")["table"]
seen = set()
for p in pop:
    rn = p["row"]
    r = rows[rn]
    if r["timestamp"] != p["ts"]:
        raise SystemExit(f"row mismatch {rn}")
    prims = [s.get("text") for s in r["steps"] if str(s.get("step", "")).startswith("primary")]
    secs = [s.get("text") for s in r["steps"] if str(s.get("step", "")).startswith("secondary")]
    pairs = []
    for i, pt in enumerate(prims):
        st = secs[i] if i < len(secs) else (secs[-1] if secs else None)
        pairs.append((pt or "", st))
    out = {"row": rn, "ts": p["ts"], "word": p["word"], "contamination": (rn + 1) in excl_lines,
           "post_M1": p["ts"][:10] >= M1_WIRED, "wav_exists": os.path.exists(r["wav_path"]),
           "stored_final_status": r.get("final_status"), "n_pairs": len(pairs), "canon": r["canonical_text"]}
    for sidname, sid in [("narr", "full_story_part1"), ("none", None)]:
        vs = [judge(r["canonical_text"], a, b, r["wav_path"], segment_id=sid) for a, b in pairs] or [{"verdict": "NO_STEPS"}]
        out[sidname] = {"last": vs[-1], "first": vs[0], "any_pass": any(v["verdict"].startswith("PASS") for v in vs),
                        "all": [v["verdict"] for v in vs]}
    res["stored"].append(out)

after = {k: sha(v) for k, v in WATCH.items()}
res["protect"] = {"before": before, "after": after, "unchanged": {k: before[k] == after[k] for k in WATCH}}
json.dump(res, open(CL + "/prod_judge_replay.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(res["protect"], open(CL + "/protect_closeout.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
shutil.rmtree(TMP, ignore_errors=True)
print(json.dumps(res["protect"], indent=1))
for k in ("hr_queue", "ledger", "store_manifest"):
    assert before[k] == after[k], k
if before["attempt_history"] != after["attempt_history"]:
    print("WARN attempt_history changed (別agentの並行作業の可能性; 本scriptはattempt_historyを書くmoduleをimportしない)")
print("items", len(res["items"]), "stored", len(res["stored"]))
