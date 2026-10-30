# ASR-FLAP-T-EQUIVALENCE-TRIAL-01 委任_01: 保存済みattempt記録から EN TTS の (voice, model, backend, language) 実使用を集計。API 0・読取専用。
# 使い方: .venv\Scripts\python.exe docs/research/ASR-FLAP-T-EQUIVALENCE-TRIAL-01/tools/flapt_voice_census_01.py --out <json>
import argparse, collections, glob, json, os, re

def family_of(path):
    p = path.replace("\\", "/").lower()
    for k, f in (("family_x", "X"), ("family_y", "Y"), ("family_z", "Z")):
        if k in p:
            return f
    if re.search(r"(^|/)er019_output/", p):
        return "X"      # er019_output = Family X audio production wiring
    return "other(A/B/C/Trial/research)"

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args()
    files = [f for f in glob.glob("**/narration/attempts/*.json", recursive=True) if not f.startswith(".venv")]
    files += [f for f in glob.glob("**/attempts/*.json", recursive=True) if not f.startswith(".venv") and f not in files]
    cnt = collections.Counter(); langs = collections.Counter(); n = 0; err = 0
    for f in files:
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            err += 1; continue
        if not isinstance(d, dict) or "voice" not in d:
            continue
        n += 1
        key = (family_of(f), str(d.get("language")), str(d.get("model")), str(d.get("tts_backend")), str(d.get("voice")))
        cnt[key] += 1
    rows = [dict(family=k[0], language=k[1], model=k[2], tts_backend=k[3], voice=k[4], attempts=v) for k, v in sorted(cnt.items())]
    en = [r for r in rows if r["language"] == "en"]
    out = dict(files_scanned=len(files), attempt_records=n, unreadable=err, rows=rows,
               en_voice_summary=sorted(collections.Counter({}).items()))
    # EN voice x family 集計
    vf = collections.defaultdict(collections.Counter)
    for r in en:
        vf[r["voice"]][r["family"]] += r["attempts"]
    out["en_voice_by_family"] = {v: dict(c) for v, c in sorted(vf.items())}
    mf = collections.Counter()
    for r in en:
        mf[(r["model"], r["tts_backend"])] += r["attempts"]
    out["en_model_backend"] = [dict(model=k[0], tts_backend=k[1], attempts=v) for k, v in mf.most_common()]
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: out[k] for k in ("files_scanned", "attempt_records", "unreadable", "en_voice_by_family", "en_model_backend")}, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
