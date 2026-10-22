# ============================================================
# er104_stored_audio_reeval_02.py  (API 0 / 費用0 / Opus P-01対応)
# KP-THREE-ASR-MAJORITY-PRODUCTION-01 委任_02: 保存音声・保存転写を **本番adapter経路**(er006 evaluate_attempt_with_cascade_detail, vote_required=True)で再評価する。
#   - Primary/Secondary = 保存済み転写(Secondaryはcacheへ注入、Azure再呼出0。呼ばれたらAssertionError)。
#   - Whisper = 割れたときだけ本番既定のローカルfaster-whisper small(whisper_vote、wav sha memo)。保存Whisper転写は使わない(実経路)。
#   - 旧委任_01 script(er104_stored_audio_reeval_01.py)は手書き判定(rejudge相当)で、本番経路との一致が未検証だった(P-01)。本scriptは
#     同じ保存データを本番adapterへ通し、旧script結果(stored_audio_reeval_01.json)との一致/不一致を行ごとに記録する。
# 使い方: .venv\Scripts\python.exe er104_stored_audio_reeval_02.py --out docs/research/KP-THREE-ASR-MAJORITY-PRODUCTION-01/stored_audio_reeval_02.json
# ============================================================
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import sys
import time

sys.path.insert(0, ".")
import er006_secondary_asr_01 as sec
import er104_kp_three_asr_vote_01 as kp3v
import er104_kp_vote_reuse_01 as kv

E91 = "er091_output/asr_three_way_trial_01"
E96 = "er096_output/kp_dual_prod_01"
MAP = "docs/research/FAMILY-X-BYUS-KP-ASR-LISTENING-PAGE-01/mapping_01.json"
OLD_TP_WAV = "er088_output/kp_asr_dual_pass_trial_01/kp4_en.wav"
PRIOR = "docs/research/KP-THREE-ASR-MAJORITY-PRODUCTION-01/stored_audio_reeval_01.json"


def _no_azure(*a, **k):
    raise AssertionError("Azure must not be called in stored-audio re-evaluation (API 0)")


def evaluate(corpus, rid, canon, label, wav, p_text, s_text, note=""):
    t = time.time()
    ev = kv.evaluate_vote(canon, p_text, wav, secondary_text=s_text)      # whisper_text=None -> 本番既定のローカルWhisper(割れたときだけ)
    v = ev["vote"]
    return {"corpus": corpus, "id": rid, "canonical": canon, "label": label, "note": note, "wav": wav,
            "primary": {"text": p_text}, "secondary": {"text": s_text},
            "adapter": {"verified": bool(ev["verified"]), "judge_state": ev["state"], "vote_state": v.get("state"), "row": v.get("row"),
                        "reason": v.get("reason"), "pass_count": v.get("pass_count"), "primary_pass": (v.get("primary") or {}).get("pass"),
                        "secondary_pass": (v.get("secondary") or {}).get("pass"), "whisper_called": bool(v.get("whisper_called")),
                        "whisper_text": (v.get("whisper") or {}).get("text"), "whisper_pass": (v.get("whisper") or {}).get("pass"),
                        "whisper_ms": (v.get("whisper") or {}).get("ms"), "azure_real_calls": ev["azure_real_calls"],
                        "warnings": (ev["asr_judgement"] or {}).get("warnings")},
            "sec": round(time.time() - t, 3)}


def corpus_er091():
    man = {json.loads(l)["id"]: json.loads(l) for l in open(f"{E91}/dataset_manifest.jsonl", encoding="utf-8")}
    raw = [json.loads(l) for l in open(f"{E91}/results/asr_raw.jsonl", encoding="utf-8")]
    by = collections.defaultdict(dict)
    for r in raw:
        if r["rep"] != 1 or r.get("error"):
            continue
        by[r["id"]][(r["method"], r["cond"])] = r["text"]
    rows = []
    for iid, it in man.items():
        if it["kind"] != "kp":
            continue
        t = by[iid]
        p = t.get(("openai", "prod")) or t.get(("openai", "neutral"))
        s = t.get(("azure", "prod")) or t.get(("azure", "neutral"))
        w = t.get(("whisper", "prod"))
        if p is None or s is None or w is None:
            continue
        lab = "problem" if it["label_class"].startswith("problem") else "normal"
        rows.append(evaluate("er091_kp39", iid, it["canonical"], lab, it["wav"], p, s, note=f"{it['label_class']} / {it['label_strength']}"))
    return rows


def corpus_survey():
    m = json.load(open(MAP, encoding="utf-8"))
    return [evaluate("byus_survey7", i["expression"], i["judge_canonical"], "presumed_normal(user_instruction_s3)", i["source_wav"],
                     i["primary_openai"]["text"], i["secondary_azure"]["text"], note="保存wav") for i in m["items"]]


def corpus_take_part():
    m = json.load(open(MAP, encoding="utf-8"))["take_part"]
    rows = []
    pw = m["problem_wav"]
    for t in pw["er088_10_trials"]:
        rows.append(evaluate("take_part_problem_13", f"er088_trial{t['trial']}", "take part", "problem(user_heard_take_tart)", OLD_TP_WAV,
                             t["primary"], t["secondary"], note="旧問題wav 675cd6b1(同一wavへの10回判定)"))
    for k, t in enumerate(pw["er096_live_3_trials"], 1):
        rows.append(evaluate("take_part_problem_13", f"er096_live{k}", "take part", "problem(user_heard_take_tart)", OLD_TP_WAV,
                             t["primary_text"], t["secondary_text"], note="Production dual実呼出3回"))
    g = m["passed_wav"]
    rows.append(evaluate("take_part_good", "good_e4405501", "take part", "normal(article_listened)", g["source"], g["primary"]["text"],
                         g["secondary"]["text"], note="合格wav"))
    return rows


def corpus_stats_attempts():
    r = json.load(open(f"{E96}/stats/stats_rows.json", encoding="utf-8"))
    rows = []
    adir = f"{E96}/stats/theme/b1b/narration/attempts"
    for x in r:
        for n, a in enumerate(x["attempts"], 1):
            wavs = sorted(glob.glob(f"{adir}/kp{x['i']}_en_attempt{n}_*.wav"))
            if not wavs or a.get("primary_text") is None or a.get("secondary_text") is None:
                continue
            rows.append(evaluate("er096_stats24_attempts", f"kp{x['i']}#{n}", x["safe"], "unlabeled(Production生成物。人間試聴なし)", wavs[0],
                                 a["primary_text"], a["secondary_text"], note=f"旧state={a['state']}; wav={os.path.basename(wavs[0])}"))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    sec.get_full_text_via_azure_stt_with_phrase_list = _no_azure           # API 0を機械的に保証
    sec.semantic_equivalence.append_telemetry_log = lambda *x, **k: None   # 再評価でtelemetry fileを増やさない
    kp3v.reset_whisper_state()
    rows = corpus_er091() + corpus_survey() + corpus_take_part() + corpus_stats_attempts()
    prior = {(r["corpus"], r["id"]): r for r in json.load(open(PRIOR, encoding="utf-8"))["rows"]}
    mism = []
    for r in rows:
        pr = prior.get((r["corpus"], r["id"]))
        r["prior_script_new_vote_pass"] = pr["new_vote_pass"] if pr else None
        r["prior_script_old_dual_pass"] = pr["old_dual_pass"] if pr else None
        r["match_prior_script"] = (pr is not None and pr["new_vote_pass"] == r["adapter"]["verified"])
        if not r["match_prior_script"]:
            mism.append(f"{r['corpus']}:{r['id']}({r['canonical']}) adapter={r['adapter']['verified']} prior={r['prior_script_new_vote_pass']}")
    prob = [r for r in rows if r["label"].startswith("problem")]
    changed4 = [r for r in rows if (not r["prior_script_old_dual_pass"]) and r["adapter"]["verified"]]
    summ = {}
    for c in sorted({r["corpus"] for r in rows}):
        rs = [r for r in rows if r["corpus"] == c]
        summ[c] = {"n": len(rs), "old_dual_pass": sum(bool(r["prior_script_old_dual_pass"]) for r in rs),
                   "adapter_vote_pass": sum(r["adapter"]["verified"] for r in rs),
                   "ng_to_pass": [f"{r['id']}({r['canonical']})" for r in rs if (not r["prior_script_old_dual_pass"]) and r["adapter"]["verified"]],
                   "pass_to_ng": [f"{r['id']}({r['canonical']})" for r in rs if r["prior_script_old_dual_pass"] and not r["adapter"]["verified"]],
                   "whisper_fired": sum(r["adapter"]["whisper_called"] for r in rs)}
    wms = [r["adapter"]["whisper_ms"] for r in rows if r["adapter"]["whisper_called"] and r["adapter"]["whisper_ms"] is not None]
    out = {"generated_by": "er104_stored_audio_reeval_02.py", "path": "production adapter (er006 evaluate_attempt_with_cascade_detail, vote_required=True)",
           "api_calls": 0, "cost_jpy": 0, "azure_real_calls_total": sum(r["adapter"]["azure_real_calls"] for r in rows),
           "whisper_model": f"faster_whisper {kp3v.WHISPER_MODEL_SIZE} {kp3v.WHISPER_COMPUTE_TYPE} cpu (er008_disfluency_qa_18 loader)",
           "n_rows": len(rows), "problem_items": len(prob),
           "problem_new_false_pass": [f"{r['corpus']}:{r['id']}" for r in prob if r["adapter"]["verified"]],
           "problem_old_false_pass": [f"{r['corpus']}:{r['id']}" for r in prob if r["prior_script_old_dual_pass"]],
           "ng_to_pass_items": [f"{r['corpus']}:{r['id']}({r['canonical']})" for r in changed4],
           "mismatch_vs_prior_script": mism, "all_match_prior_script": not mism,
           "whisper_fired_total": sum(r["adapter"]["whisper_called"] for r in rows),
           "whisper_ms": {"n": len(wms), "mean": round(sum(wms) / max(1, len(wms)), 1) if wms else None, "max": max(wms) if wms else None},
           "summary": summ, "rows": rows}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, ensure_ascii=False, indent=1))
    for r in rows:
        if r["adapter"]["whisper_called"]:
            print("WHISPER", r["corpus"], r["id"], "|", r["canonical"], "| P", r["primary"]["text"], "| S", r["secondary"]["text"], "| W",
                  r["adapter"]["whisper_text"], "->", r["adapter"]["vote_state"], r["adapter"]["row"], r["label"])


if __name__ == "__main__":
    main()
