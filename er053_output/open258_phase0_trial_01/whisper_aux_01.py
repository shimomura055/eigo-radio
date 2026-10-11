# 無料ローカルfaster-whisper small/medium(language=ja、原稿非提示)。全候補音声(sha重複除く)を転写し、
# 原稿に対するshould_pass(既存classify、Resolver OFF)を補助列として記録。課金0。
import sys, json, os
sys.path.insert(0, "er053_output/open258_phase0_trial_01")
from open258_phase0_common import *
from faster_whisper import WhisperModel
rows = json.load(open(OUT + "/manifest_all_candidates_01.json", encoding="utf8"))
models = {s: WhisperModel(s, device="cpu", compute_type="int8") for s in ("small", "medium")}
cache_p = OUT + "/whisper_aux_01.json"
cache = json.load(open(cache_p, encoding="utf8")) if os.path.exists(cache_p) else {}
texts = cache.setdefault("_text_by_sha", {})
out = {}
for r in rows:
    if r.get("audio_missing"): continue
    k = f'g{r["group"]}_{r["seg"]}_a{r["attempt"]}'
    out[k] = {}
    for s, m in models.items():
        ck = r["sha256"] + "|" + s
        if ck not in texts:
            segs, _ = m.transcribe(r["wav"], language="ja", temperature=0, beam_size=5, condition_on_previous_text=False)
            texts[ck] = "".join(x.text for x in segs).strip()
        t = texts[ck]
        j = javal.classify_ja_asr_match(r["canonical"], t)
        out[k][s] = {"text": t, "cls_vs_canonical": j.classification, "agrees_with_canonical": j.should_pass}
    out[k]["agree_any"] = out[k]["small"]["agrees_with_canonical"] or out[k]["medium"]["agrees_with_canonical"]
    out[k]["agree_both"] = out[k]["small"]["agrees_with_canonical"] and out[k]["medium"]["agrees_with_canonical"]
    print(k, r["canonical"][:20], "|S:", out[k]["small"]["text"][:25], out[k]["small"]["cls_vs_canonical"], "|M:", out[k]["medium"]["text"][:25], out[k]["medium"]["cls_vs_canonical"], flush=True)
out["_text_by_sha"] = texts
json.dump(out, open(cache_p, "w", encoding="utf8"), ensure_ascii=False, indent=1)
print("DONE")
