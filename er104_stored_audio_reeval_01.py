# ============================================================
# er104_stored_audio_reeval_01.py  (API 0 / 費用0 / Production経路外・未配線)
# KP-THREE-ASR-MAJORITY-PRODUCTION-01 委任_01: 保存音声・保存転写に対し、旧方式(両方PASS必須)と新方式(3-ASR多数決)を並べて再評価する。
#   Primary/Secondary = 保存済みの転写(再呼出なし)。Whisper = er091保存転写、または保存wavへのローカルfaster-whisper small再転写。
#   判定関数 = er104_kp_three_asr_vote_01(Production既存分類器 classify_asr_match + 同音救済 + 値/否定ガード)。
# 使い方: .venv\Scripts\python.exe er104_stored_audio_reeval_01.py --out docs/research/KP-THREE-ASR-MAJORITY-PRODUCTION-01/stored_audio_reeval_01.json
# ============================================================
from __future__ import annotations
import argparse, collections, glob, json, os, sys, time
sys.path.insert(0, ".")
import er104_kp_three_asr_vote_01 as vote

E91 = "er091_output/asr_three_way_trial_01"
E96 = "er096_output/kp_dual_prod_01"
MAP = "docs/research/FAMILY-X-BYUS-KP-ASR-LISTENING-PAGE-01/mapping_01.json"
OLD_TP_WAV = "er088_output/kp_asr_dual_pass_trial_01/kp4_en.wav"

_WH_CACHE: dict = {}
LIVE_WHISPER_SEC: list = []


def live_whisper(wav):
    if wav not in _WH_CACHE:
        t = time.time()
        _WH_CACHE[wav] = vote.whisper_transcribe(wav)
        LIVE_WHISPER_SEC.append(round(time.time() - t, 3))
    return _WH_CACHE[wav]


def evaluate(corpus, rid, canon, label, p_text, s_text, w_text_fn, note=""):
    """旧=両方PASS / 新=3-ASR多数決。w_text_fnはWhisper転写を返すcallable(新方式でPとSが割れたときだけ呼ばれる=発火の記録)。
    あわせて参考のため(常時)Whisper転写も1回取得して記録する(判定には使わない)。"""
    P = vote.make_voter("openai", canon, p_text)
    S = vote.make_voter("azure", canon, s_text)
    old_pass = bool(P.passed and S.passed)
    called = {"n": 0}

    def wfn():
        called["n"] += 1
        return vote.make_voter("whisper", canon, w_text_fn())
    d = vote.decide(P, lambda: S, wfn)
    w_ref = w_text_fn()
    W = vote.make_voter("whisper", canon, w_ref)
    return {"corpus": corpus, "id": rid, "canonical": canon, "label": label, "note": note,
            "primary": {"text": p_text, "pass": P.passed}, "secondary": {"text": s_text, "pass": S.passed},
            "whisper": {"text": w_ref, "pass": W.passed},
            "old_dual_pass": old_pass, "new_vote_pass": bool(d.verified), "new_state": d.state, "new_reason": d.reason,
            "whisper_fired_in_new": called["n"] == 1, "changed": old_pass != bool(d.verified)}


def corpus_er091():
    man = [json.loads(l) for l in open(f"{E91}/dataset_manifest.jsonl", encoding="utf-8")]
    raw = [json.loads(l) for l in open(f"{E91}/results/asr_raw.jsonl", encoding="utf-8")]
    by = collections.defaultdict(dict)
    for r in raw:
        if r["rep"] != 1 or r.get("error"):
            continue
        by[r["id"]][(r["method"], r["cond"])] = r["text"]
    rows = []
    for it in man:
        if it["kind"] != "kp":
            continue
        t = by[it["id"]]
        p = t.get(("openai", "prod")) or t.get(("openai", "neutral"))
        s = t.get(("azure", "prod")) or t.get(("azure", "neutral"))
        w = t.get(("whisper", "prod"))
        if p is None or s is None or w is None:
            continue
        lab = "problem" if it["label_class"].startswith("problem") else "normal"
        rows.append(evaluate("er091_kp39", it["id"], it["canonical"], lab, p, s, lambda w=w: " ".join(w.split()),
                             note=f"{it['label_class']} / {it['label_strength']}"))
    return rows


def corpus_survey():
    m = json.load(open(MAP, encoding="utf-8"))
    rows = []
    for i in m["items"]:
        wav = i["source_wav"]
        rows.append(evaluate("byus_survey7", i["expression"], i["judge_canonical"], "presumed_normal(user_instruction_s3)",
                             i["primary_openai"]["text"], i["secondary_azure"]["text"], lambda wav=wav: live_whisper(wav),
                             note="保存wav(sha一致はer099で確認済み)に対しWhisper small再転写"))
    return rows


def corpus_take_part():
    m = json.load(open(MAP, encoding="utf-8"))["take_part"]
    rows = []
    pw = m["problem_wav"]
    for t in pw["er088_10_trials"]:
        rows.append(evaluate("take_part_problem_13", f"er088_trial{t['trial']}", "take part", "problem(user_heard_take_tart)",
                             t["primary"], t["secondary"], lambda: live_whisper(OLD_TP_WAV), note="旧問題wav 675cd6b1(同一wavへの10回判定)"))
    for k, t in enumerate(pw["er096_live_3_trials"], 1):
        rows.append(evaluate("take_part_problem_13", f"er096_live{k}", "take part", "problem(user_heard_take_tart)",
                             t["primary_text"], t["secondary_text"], lambda: live_whisper(OLD_TP_WAV), note="Production dual実呼出3回"))
    g = m["passed_wav"]
    rows.append(evaluate("take_part_good", "good_e4405501", "take part", "normal(article_listened)", g["primary"]["text"], g["secondary"]["text"],
                         lambda: live_whisper(g["source"]), note="合格wav"))
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
            rows.append(evaluate("er096_stats24_attempts", f"kp{x['i']}#{n}", x["safe"], "unlabeled(Production生成物。人間試聴なし)",
                                 a["primary_text"], a["secondary_text"], lambda w=wavs[0]: live_whisper(w),
                                 note=f"旧state={a['state']}; wav={os.path.basename(wavs[0])}"))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rows = corpus_er091() + corpus_survey() + corpus_take_part() + corpus_stats_attempts()
    summ = {}
    for c in sorted({r["corpus"] for r in rows}):
        rs = [r for r in rows if r["corpus"] == c]
        summ[c] = {"n": len(rs), "old_pass": sum(r["old_dual_pass"] for r in rs), "new_pass": sum(r["new_vote_pass"] for r in rs),
                   "ng_to_pass": [f"{r['id']}({r['canonical']})" for r in rs if (not r["old_dual_pass"]) and r["new_vote_pass"]],
                   "pass_to_ng": [f"{r['id']}({r['canonical']})" for r in rs if r["old_dual_pass"] and not r["new_vote_pass"]],
                   "whisper_fired": sum(r["whisper_fired_in_new"] for r in rs)}
    prob = [r for r in rows if r["label"].startswith("problem")]
    out = {"generated_by": "er104_stored_audio_reeval_01.py", "api_calls": 0, "cost_jpy": 0,
           "whisper_model": f"faster_whisper {vote.WHISPER_MODEL_SIZE} cpu int8 (er008_disfluency_qa_18 loader)",
           "problem_items": len(prob), "problem_new_false_pass": [f"{r['corpus']}:{r['id']}" for r in prob if r["new_vote_pass"]],
           "problem_old_false_pass": [f"{r['corpus']}:{r['id']}" for r in prob if r["old_dual_pass"]],
           "summary": summ, "live_whisper_sec": {"n": len(LIVE_WHISPER_SEC), "mean": round(sum(LIVE_WHISPER_SEC) / max(1, len(LIVE_WHISPER_SEC)), 3),
                                                  "max": max(LIVE_WHISPER_SEC) if LIVE_WHISPER_SEC else None},
           "rows": rows}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, ensure_ascii=False, indent=1))
    print("--- changed rows ---")
    for r in rows:
        if r["changed"]:
            print(r["corpus"], r["id"], "|", r["canonical"], "| P", r["primary"]["text"], r["primary"]["pass"], "| S", r["secondary"]["text"],
                  r["secondary"]["pass"], "| W", r["whisper"]["text"], r["whisper"]["pass"], "|", r["label"], "|", r["new_state"])


if __name__ == "__main__":
    main()
