# -*- coding: utf-8 -*-
"""全rawサンプルを計測して measure/samples_measured.json へ(再実行可。計測済みはwav sha256で再利用)。API 0。"""
import hashlib, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import yvp_measure_lib_01 as lib

OUT = "docs/research/FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01/measure/samples_measured.json"


def main():
    prev = {}
    if os.path.exists(OUT):
        for r in json.load(open(OUT, encoding="utf-8")):
            prev[r["sha256"]] = r
    res = []
    texts = {(lv, b): lib.body_text(lv, b) for lv in ("a2", "b1b") for b in (1, 2, 3)}
    for s in lib.collect_samples():
        sha = hashlib.sha256(open(s["wav"], "rb").read()).hexdigest()
        key = sha
        if key in prev and prev[key].get("body") == s["body"] and prev[key].get("src") == s["src"] and prev[key].get("take") == s["take"] and prev[key].get("wav") == s["wav"]:
            res.append(prev[key]); continue
        m = lib.measure_wav(s["wav"], texts[(s["level"], s["body"])])
        res.append({**s, "sha256": sha, **m})
    for r in res:     # attempt json(隣接)からASR/QA・条件情報を付与(毎回更新)
        j = r["wav"][:-4] + ".json"
        if os.path.exists(j):
            d = json.load(open(j, encoding="utf-8"))
            ev = d.get("repetition_qa_evidence") or {}
            r["asr_verified"] = d.get("verified")
            r["audio_classification"] = d.get("audio_classification")
            r["rep_flag"] = (ev.get("flagged") if isinstance(ev, dict) else None)
            r["route"] = d.get("route")
            r["model"] = d.get("model")
            r["voice_name"] = d.get("voice")
            it = d.get("instruction_text") or ""
            r["instr_sha"] = hashlib.sha256(it.encode("utf-8")).hexdigest()[:12] if it else None
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(res), "samples ->", OUT)


if __name__ == "__main__":
    main()
