# JA-ASR-FALSE-NG-ROOT-FIX-02 委任_03 正例拡張の列挙(API 0)。事前登録=PREREGISTERED_03.md §3。
# 人間承認(human_approved_segments.json)で最終採用された日本語a2 attempt(wav shaがattemptと一致)のうち、X/Y/Z系列(er019/er026/er110/er121)のもの。sha重複は1本に畳む。
# 再現: PYTHONUTF8=1 .venv/Scripts/python.exe -X utf8 docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/collect_pos_ext_03.py
import glob, hashlib, json, os, wave
OUT = "docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/"
PICK = {  # (run dir 末尾, seg) -> 凍結済み4本(PREREGISTERED_03 §3)。検索結果がこの集合と一致しなければassert
    ("middle_east_yemen_saudi__run_mey_02", "comment_2"), ("run_e2e_02", "comment_1"), ("run_01", "preview"), ("run_gpg5_y_01", "preview")}  # run_gpg5_y_01 / run_gpg5_y_01_s23f / run_style_fix_01 は同sha(最初に見つかった run_gpg5_y_01 に畳む)
rows, seen = [], {}
for root in ("er019_output", "er026_output", "er110_output", "er121_output"):
    for f in sorted(glob.glob(root + "/**/audit/human_approved_segments.json", recursive=True)):
        f = f.replace("\\", "/")
        ad = os.path.dirname(os.path.dirname(f))
        if not ad.endswith("/a2"):
            continue
        run = ad.split("/")[-2]
        for seg in json.load(open(f, encoding="utf8")):
            wavp = f"{ad}/narration/{seg}.wav"
            if not os.path.exists(wavp):
                continue
            sha = hashlib.sha256(open(wavp, "rb").read()).hexdigest()
            for aj in sorted(glob.glob(f"{ad}/narration/attempts/{seg}_attempt*.json")):
                a = json.load(open(aj, encoding="utf8"))
                if a.get("sha256") != sha or a.get("language") != "ja":
                    continue
                tg = json.load(open(f"{ad}/audit/tts_generation_results.json", encoding="utf8"))["segments"][seg]
                canon = tg["canonical_text"]
                sec = (a.get("scg_info") or {}).get("secondary_transcript")
                w = wave.open(aj.replace(".json", ".wav")); dur = round(w.getnframes() / w.getframerate(), 2)
                rec = {"run": run, "seg": seg, "attempt_json": aj.replace("\\", "/"), "wav": aj.replace(".json", ".wav").replace("\\", "/"), "sha256": sha, "canonical": canon,
                       "stored_openai": a.get("asr_text"), "azure_stored": sec, "dur_s": dur}
                if sha in seen:
                    seen[sha]["same_sha_as"].append(f"{run}/{seg}")
                    continue
                rec["same_sha_as"] = []
                seen[sha] = rec
                rows.append(rec)
                break
keep = [r for r in rows if (r["run"], r["seg"]) in PICK]
got = {(r["run"], r["seg"]) for r in keep}
assert got == PICK, (got ^ PICK)
json.dump({"managed_id": "JA-ASR-FALSE-NG-ROOT-FIX-02", "items": keep, "excluded_other_ja_x_y_z_approved": [{"run": r["run"], "seg": r["seg"]} for r in rows if (r["run"], r["seg"]) not in PICK]},
          open(OUT + "pos_ext_03.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(keep), sum(r["dur_s"] for r in keep), [(r["run"], r["seg"], r["dur_s"], bool(r["azure_stored"]), r["same_sha_as"]) for r in keep])
