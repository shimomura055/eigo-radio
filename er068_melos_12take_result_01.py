"""ASR-PHONETIC-EQUIVALENCE-MELOS-12TAKE-RESULT-01: Melos said 12件の従来方式 vs 改訂M1(V1') read-only 比較。
既存転写(er069 results_02.json)と既存wavのみ使用。新規TTS/ASR/LLM API 0。既存scriptはimportのみ。"""
import argparse, json, os, sys
sys.path.insert(0, os.getcwd())
import er068_asr_phonetic_equivalence_generalization_01_offline as O  # telemetry追記はno-op化済み(import時)

LV = {("std", "raw"): "Standard減速前", ("std", "slow6"): "Standard減速後", ("adv", "raw"): "Advanced"}


def judge(canon, asr):
    d = O.design_judge(canon, asr)
    acc = d["verdict"] in ("EXACT", "PROD_PASS_UNCHANGED", "ACCEPT_M1")
    return d, acc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-telemetry", action="store_true", required=True)
    a = ap.parse_args()
    rows = json.load(open(os.path.join(a.split_dir, "results_02.json"), encoding="utf-8"))["rows"]
    rows = [r for r in rows if r["name"] == "Melos" and r["verb"] == "said"]
    rows.sort(key=lambda r: (["std", "adv"].index(r["level"]), r["target"] != "raw", r["take"]))
    out = []
    for r in rows:
        wav = f"{a.split_dir}/gen02/wav/{r['job']}_{r['target']}.wav"
        e = {"job": r["job"], "level": LV[(r["level"], r["target"])], "take": r["take"], "wav": wav,
             "wav_exists": os.path.exists(wav), "canonical": r["text"]}
        tail = O.tail_integrity(wav)
        e["tail"] = tail
        for eng in ("openai", "azure"):
            t = r[eng]["text"]
            d, acc = judge(r["text"], t)
            rec_pass = r["openai_verified"] if eng == "openai" else r["azure_pass"]
            e[eng] = {"asr": t, "legacy_recorded_pass": rec_pass,
                      "legacy_recorded_class": r["openai_class"] if eng == "openai" else r["azure_class"],
                      "legacy_recomputed_pass(SEG=full_story_part1,Tier3除外)": bool(d["verdict"] in ("EXACT", "PROD_PASS_UNCHANGED")),
                      "m1_verdict": d["verdict"], "m1_pass": acc, "prod_classification": d.get("prod_classification"),
                      "m1_subs": [(s["from"], s["to"], s.get("basis"), s.get("phoneme_rule")) for s in (d.get("m1") or {}).get("subs", [])],
                      "m1_reason": (d.get("m1") or {}).get("variant_classification"),
                      "v2_verdict": O.v2_verdict(d, tail), "phon_verdict": d.get("phon_verdict")}
        e["azure_no_phraselist"] = {"asr": (r.get("azure_np") or {}).get("text"), "legacy_pass": r.get("azure_np_pass")}
        e["whisper_small_ref"] = r["whisper_small"]["text"]
        e["legacy_or_recorded"] = bool(r["or_pass"])
        e["m1_or"] = e["openai"]["m1_pass"] or e["azure"]["m1_pass"]
        e["v2_or"] = e["openai"]["v2_verdict"] in ("EXACT", "PROD_PASS_UNCHANGED", "ACCEPT_M1") or e["azure"]["v2_verdict"] in ("EXACT", "PROD_PASS_UNCHANGED", "ACCEPT_M1")
        out.append(e)
    n = len(out)
    S = {"n": n, "legacy_or_pass": sum(e["legacy_or_recorded"] for e in out),
         "legacy_openai_pass": sum(e["openai"]["legacy_recorded_pass"] for e in out),
         "legacy_azure_pass": sum(e["azure"]["legacy_recorded_pass"] for e in out),
         "m1_or_pass": sum(e["m1_or"] for e in out), "m1_openai_pass": sum(e["openai"]["m1_pass"] for e in out),
         "m1_azure_pass": sum(e["azure"]["m1_pass"] for e in out), "v2_or_pass": sum(e["v2_or"] for e in out),
         "wav_exists": sum(e["wav_exists"] for e in out), "api_calls": 0}
    json.dump({"summary": S, "rows": out}, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps(S))
    for e in out:
        print(e["job"], e["level"], "| OA", e["openai"]["asr"], e["openai"]["legacy_recorded_pass"], e["openai"]["m1_verdict"], "| AZ", e["azure"]["asr"], e["azure"]["legacy_recorded_pass"], e["azure"]["m1_verdict"], e["azure"]["m1_subs"], "| tail", (e["tail"] or {}).get("tail_ok"), "| v2", e["openai"]["v2_verdict"], e["azure"]["v2_verdict"])

main()
