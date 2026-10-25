# API 0: 保存済みJA attempt (er*_output/**/attempts/*.json, language=ja) とcanonical(同runのaudit/tts_generation_results.json)を集める。
# 出力: attempt_pool_01.json  (read-only収集。Production出力は変更しない)
import glob, json, os, sys
OUT = "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/attempt_pool_01.json"
cache = {}


def canon_for(att_path, seg):
    d = os.path.dirname(os.path.dirname(os.path.dirname(att_path)))  # .../a2/narration/attempts/x.json -> .../a2
    p = os.path.join(d, "audit", "tts_generation_results.json")
    if p not in cache:
        try:
            cache[p] = json.load(open(p, encoding="utf8")).get("segments", {})
        except Exception:
            cache[p] = {}
    s = cache[p].get(seg) or {}
    return s.get("canonical_text") or s.get("text")


rows, nocanon = [], 0
for p in glob.glob("er*_output/**/attempts/*.json", recursive=True):
    try:
        d = json.load(open(p, encoding="utf8"))
    except Exception:
        continue
    if not isinstance(d, dict) or d.get("language") != "ja" or d.get("asr_text") is None:
        continue
    c = canon_for(p.replace("\\", "/"), d.get("segment_id"))
    if not c:
        nocanon += 1
        continue
    rows.append({"file": p.replace("\\", "/"), "seg": d.get("segment_id"), "canon": c, "primary": d.get("asr_text"),
                 "verified": d.get("verified"), "cls": d.get("audio_classification")})
json.dump(rows, open(OUT, "w", encoding="utf8"), ensure_ascii=False)
print("attempts with canon:", len(rows), "no canon:", nocanon, "verified True:", sum(1 for r in rows if r["verified"]))
