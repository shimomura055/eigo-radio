# -*- coding: utf-8 -*-
"""COFFEE-P8 runtime evidence集計(FAMILY-X-COFFEE-P8-FINAL-AUDIO-AND-PRODUCTION-WIRING-01 委任_03、API 0)。
raw_usage_log.jsonlの全Gemini TTS呼出の style 実送信文字列sha256とP8を照合し、Full Story WPMを測る。"""
import sys, json, hashlib, importlib.util, collections
ROOT = "C:/Users/tensh/eigo-radio"; sys.path.insert(0, ROOT)
OUT = "er019_output/coffee_prices/run_p8_wiring_01"
P8 = "3eadf4f6f788b822c90f17ba56d893bccb5fab840358cf48845472cd4f4e5595"
# raw_usage_log.jsonlの"style"は先頭200字に切り詰め記録される(実測)ため、per-call照合はhead200(P8[:200])で行う。
# 全文sha256照合は tts_generation_results.json の style_prefix(sha256+len+head200)と style_profile で行う。
spec = importlib.util.spec_from_file_location("mw", f"{ROOT}/er057_output/coffee_final_listening_tone_trial_01/wpm_measurement_01/measure_wpm_01.py")
mw = importlib.util.module_from_spec(spec); spec.loader.exec_module(mw)
import soundfile as sf

def sha(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()
P8_HEAD200 = json.load(open(f"{ROOT}/{OUT}/a2/audit/tts_generation_results.json", encoding="utf-8"))["segments"]["full_story_part1"]["attempts_log"][0]["style_prefix"]["head200"]

def calls():
    rows = []
    for line in open(f"{ROOT}/{OUT}/raw_usage_log.jsonl", encoding="utf-8"):
        r = json.loads(line)
        if r.get("provider") == "gemini_batch":
            op = (r.get("output_path") or "").replace("\\", "/")
            lv = "a2" if "/a2/" in op else "b1b" if "/b1b/" in op else "shared"
            st = r.get("style")
            rows.append({"seg": r.get("segment"), "level": lv, "ts": r.get("timestamp"), "model_id": r.get("model_id"), "voice": r.get("voice"),
                         "style_sha": sha(st) if isinstance(st, str) else None, "style_len": len(st) if isinstance(st, str) else None,
                         "is_P8": (st == P8_HEAD200) if isinstance(st, str) else None, "jpy": r.get("cost_jpy"), "ok": r.get("success")})
    return rows

def meas(p, words):
    x, sr = sf.read(p, dtype="float64"); x = x if x.ndim == 1 else x[:, 0]
    dur = len(x) / sr; db = mw.frame_rms_db(x, sr); ps = mw.find_pauses(db, 500, dur)
    sp = dur - sum(q["dur"] for q in ps)
    return {"dur": round(dur, 2), "wpm": round(words / dur * 60, 1), "speech_wpm500": round(words / sp * 60, 1), "n_pause500": len(ps), "words": words}

def wpm(wav_override=None):
    wav_override = wav_override or {}
    res = {}
    for lv, key in (("a2", "std"), ("b1b", "adv")):
        d = json.load(open(f"{ROOT}/{OUT}/{lv}/audit/tts_generation_results.json", encoding="utf-8"))
        rows = []; W = D = S = 0
        for n in (1, 2, 3):
            seg = d["segments"][f"full_story_part{n}"]
            words = mw.count_primary(seg["text"])
            p = wav_override.get((lv, n), f"{ROOT}/{OUT}/{lv}/narration/full_story_part{n}.wav")
            m = meas(p, words); rows.append(m); W += words; D += m["dur"]; S += words / m["speech_wpm500"] * 60
        res[key] = {"parts": rows, "total_wpm": round(W / D * 60, 1), "total_speech_wpm500": round(W / S * 60, 1), "total_dur": round(D, 2), "words": W}
    v4 = json.load(open(f"{ROOT}/er057_output/coffee_final_v4/wpm_v4_01.json", encoding="utf-8"))
    for key in ("std", "adv"):
        a = v4[f"{key}_v4"]; b = res[key]
        res[key]["vs_v4_pct"] = {"total_wpm": round((b["total_wpm"] / a["total_wpm"] - 1) * 100, 1),
                                 "speech_wpm500": round((b["total_speech_wpm500"] / a["total_speech_wpm500"] - 1) * 100, 1),
                                 "dur": round((b["total_dur"] / a["total_dur"] - 1) * 100, 1)}
        res[key]["v4"] = {"total_wpm": a["total_wpm"], "total_speech_wpm500": a["total_speech_wpm500"], "total_dur": a["total_dur"]}
    return res

if __name__ == "__main__":
    cs = calls()
    agg = collections.OrderedDict()
    for c in cs:
        k = (c["level"], c["seg"]); agg.setdefault(k, []).append(c)
    table = []
    for (lv, seg), cc in agg.items():
        table.append({"level": lv, "segment": seg, "n_calls": len(cc), "all_P8": all(x["is_P8"] for x in cc), "any_P8": any(x["is_P8"] for x in cc),
                      "models": sorted({x["model_id"] for x in cc}), "voices": sorted({x["voice"] for x in cc}), "jpy": round(sum(x["jpy"] or 0 for x in cc), 3),
                      "style_sha8": sorted({(x["style_sha"] or "")[:8] for x in cc})})
    out = {"calls": cs, "per_segment": table, "wpm": wpm() if (len(sys.argv) < 2 or sys.argv[1] != "nowpm") else None}
    path = f"{ROOT}/{OUT}/audit/wiring_evidence_data_{sys.argv[2] if len(sys.argv) > 2 else 'pre_regen'}.json"
    json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for t in table: print(t)
    print(json.dumps(out["wpm"], ensure_ascii=False, indent=1))
