# -*- coding: utf-8 -*-
"""FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01 委任_02 Step C: runtime evidence収集(読み取りのみ・API 0)。
使い方: python collect_runtime_evidence_01.py x|z <audio level dir(b1b)> <出力json>"""
import hashlib, json, os, sys, wave
import numpy as np


def rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def read_wav(p):
    with wave.open(p, "rb") as w:
        sr, ch, n = w.getframerate(), w.getnchannels(), w.getnframes()
        raw = w.readframes(n)
    x = np.frombuffer(raw, dtype="<i2").reshape(-1, ch).astype(np.float64) / 32768.0
    return sr, x


def gap_check(wav, gaps):
    sr, x = read_wav(wav)
    out = []
    for a, b in gaps:
        i0, i1 = int(round(a * sr)), int(round(b * sr))
        seg = x[i0:i1]
        m = float(np.max(np.abs(seg))) if seg.size else None
        # 前後各50msの音声(無音でないこと)
        pre = float(np.sqrt(np.mean(x[max(0, i0 - int(0.05 * sr)):i0] ** 2))) if i0 > 0 else None
        post = float(np.sqrt(np.mean(x[i1:i1 + int(0.05 * sr)] ** 2)))
        out.append({"gap_s": [a, b], "len_s": round((i1 - i0) / sr, 4), "max_abs_inside": m, "rms_pre50ms": round(pre, 5), "rms_post50ms": round(post, 5)})
    return out


def main():
    fam, lv, out = sys.argv[1], sys.argv[2], sys.argv[3]
    audit = os.path.join(lv, "audit")
    res_p = os.path.join(audit, "tts_generation_results.json")
    res = rj(res_p)
    segs = res["segments"]
    ev = {"family": fam.upper(), "level_dir": lv, "parents": {}}
    chunks_all = {k: v for k, v in segs.items() if "_k" in k and k.startswith("full_story")}
    attempts = hr = lr = fb = dev = 0
    for k, v in sorted(segs.items()):
        if not isinstance(v, dict):
            continue
        if k in chunks_all or k.startswith("full_story") or k.startswith("comment") or True:
            pass
    for k, v in sorted(chunks_all.items()):
        att = v.get("attempt_count") or len(v.get("attempts") or []) or 0
        attempts += att if isinstance(att, int) else 0
        if v.get("local_rewrite_recovery"):
            lr += 1
        if v.get("status") not in ("OK",):
            hr += 1
        if v.get("audio_text_deviation"):
            dev += 1
    ev["chunk_entry_count"] = len(chunks_all)
    ev["chunk_status_counts"] = {}
    for v in chunks_all.values():
        ev["chunk_status_counts"][v.get("status")] = ev["chunk_status_counts"].get(v.get("status"), 0) + 1
    ev["chunks"] = {k: {"status": v.get("status"), "words": len((v.get("canonical_text") or "").split()), "sha256": v.get("sha256"),
                         "asr_state": ((v.get("asr_judgement") or {}).get("state")), "reason_code": ((v.get("asr_judgement") or {}).get("reason_code")),
                         "local_rewrite": bool(v.get("local_rewrite_recovery")), "audio_text_deviation": bool(v.get("audio_text_deviation")),
                         "style_profile": (v.get("style_profile") or {}).get("profile_id")} for k, v in sorted(chunks_all.items())}
    ev["local_rewrite_chunks"] = lr
    ev["deviation_chunks"] = dev
    for k, v in sorted(segs.items()):
        ct = v.get("chunk_tts") if isinstance(v, dict) else None
        if ct is None or "chunk_ids" not in ct:
            continue
        ev["parents"][k] = {"status": v.get("status"), "chunk_ids": ct.get("chunk_ids"), "words": ct.get("words"),
                            "boundary_kinds": ct.get("boundary_kinds"), "chunk_gate_statuses": ct.get("chunk_gate_statuses"),
                            "parent_sha256": v.get("sha256"), "raw_parent_sha256": ct.get("raw_parent_sha256"),
                            "planner_version": ct.get("planner_version")}
    # parent wav = chunk PCM連結 + 0.2秒の整数sample一致
    chk = {}
    for k, p in ev["parents"].items():
        wavs = []
        nd = None
        for d in (os.path.join(lv, "narration"), os.path.join(os.path.dirname(lv), "narration")):
            if os.path.isdir(d):
                nd = d
                break
        if nd is None:
            nd = os.path.join(lv, "narration")
        try:
            raws = []
            for cid in p["chunk_ids"]:
                sr, x = read_wav(os.path.join(nd, cid + ".wav"))
                raws.append((sr, x))
            sr = raws[0][0]
            pad = np.zeros((int(round(0.2 * sr)), raws[0][1].shape[1]))
            parts = []
            for i, (s, x) in enumerate(raws):
                parts.append(x)
                if i < len(raws) - 1:
                    parts.append(pad)
            exp = np.concatenate(parts)
            sr2, got = read_wav(os.path.join(nd, k + ".wav"))
            chk[k] = {"samples_expected": int(exp.shape[0]), "samples_parent_wav": int(got.shape[0]), "equal": bool(exp.shape == got.shape and np.array_equal(np.round(exp * 32768), np.round(got * 32768))),
                      "sr": sr2}
        except Exception as e:   # pragma: no cover
            chk[k] = {"error": str(e)[:200]}
    ev["parent_concat_check"] = chk
    for name in ("chunk_tts_assembly_b1b.json", "chunk_tts_evidence_b1b.json", "chunk_tts_evidence_b1b.json"):
        pass
    ev["audit_files"] = sorted(os.listdir(audit))
    asm = os.path.join(audit, "chunk_tts_assembly_b1b.json")
    if os.path.exists(asm):   # X: 組立済み通し音声内の0.2秒gapの実測(整数sample無音)
        a = rj(asm)
        wavd = os.path.join(lv, "assembled")
        wavs = [os.path.join(wavd, f) for f in os.listdir(wavd) if f.endswith(".wav")] if os.path.isdir(wavd) else []
        if wavs:
            ev["assembled_gap_check"] = {pk: gap_check(wavs[0], pv.get("gap_offsets_in_episode_s") or []) for pk, pv in (a.get("parents") or {}).items()}
    out_d = os.path.dirname(out)
    if out_d:
        os.makedirs(out_d, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(ev, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: ev[k] for k in ("chunk_entry_count", "chunk_status_counts", "local_rewrite_chunks", "deviation_chunks")}, ensure_ascii=False))
    print({k: v.get("equal", v) for k, v in chk.items()})


if __name__ == "__main__":
    main()
