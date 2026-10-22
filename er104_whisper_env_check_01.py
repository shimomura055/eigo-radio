# ============================================================
# er104_whisper_env_check_01.py  (API 0 / 費用0 / Production経路外・未配線)
# KP-THREE-ASR-MAJORITY-PRODUCTION-01 委任_01: ローカルfaster-whisper(small int8)のProduction実行環境確認と処理時間実測。
# 使い方: .venv\Scripts\python.exe er104_whisper_env_check_01.py --out docs/research/KP-THREE-ASR-MAJORITY-PRODUCTION-01/whisper_env_check_01.json
# ============================================================
from __future__ import annotations
import argparse, glob, json, os, platform, sys, time
sys.path.insert(0, ".")

CLIPS_GLOB = "er096_output/kp_dual_prod_01/stats_store/audio/*.wav"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--model", default="small")
    a = ap.parse_args()
    res = {"python": sys.version, "platform": platform.platform(), "cpu_count": os.cpu_count(), "model_size": a.model, "compute_type": "int8", "device": "cpu"}
    t0 = time.time()
    import faster_whisper, ctranslate2
    res["import_sec"] = round(time.time() - t0, 3)
    res["faster_whisper"] = faster_whisper.__version__
    res["ctranslate2"] = ctranslate2.__version__
    import er008_disfluency_qa_18 as dq
    hub = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub")
    res["hf_hub_dir"] = hub
    res["cached_models"] = sorted(d for d in os.listdir(hub)) if os.path.isdir(hub) else []
    t0 = time.time()
    dq._get_model(a.model)   # Production(er008/er006)と同一のloader。初回ロード時間
    res["model_load_sec"] = round(time.time() - t0, 3)
    clips = sorted(glob.glob(CLIPS_GLOB))[: a.n]
    rows = []
    for c in clips:
        t1 = time.time()
        words = dq.transcribe_verbatim(c, language="en", model_size=a.model)
        dt = time.time() - t1
        import wave
        with wave.open(c) as w:
            dur = w.getnframes() / w.getframerate()
        rows.append({"wav": c, "audio_sec": round(dur, 2), "whisper_sec": round(dt, 3), "text": " ".join("".join(x["text"] for x in words).split())})
    res["clips"] = rows
    ts = [r["whisper_sec"] for r in rows]
    res["per_clip_sec"] = {"n": len(ts), "first": ts[0] if ts else None, "mean": round(sum(ts) / len(ts), 3) if ts else None,
                           "mean_excluding_first": round(sum(ts[1:]) / max(1, len(ts) - 1), 3) if len(ts) > 1 else None, "max": max(ts) if ts else None}
    res["api_calls"] = 0
    res["cost_jpy"] = 0
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(res, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in res.items() if k != "clips"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
