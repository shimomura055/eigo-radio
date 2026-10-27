# -*- coding: utf-8 -*-
"""M2-b evidence(API 0・read-only): 実Z runのa2 KP(japanese_gloss に「～」を含む項目)で、Std利用者向けページ行を新builderで組み、
日本語の意味の欄が確定済みの表示用japanese_gloss(「～」)になること・TTS入力(canonical_text。「なになに」)は不変であることを示す。実runは読むだけ(一時dirへ必要ファイルのみ複製)。"""
import json, os, shutil, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, ROOT)
import er063_family_z_audio_01 as za  # noqa: E402

RUN = sys.argv[1]
out = {}
tmp = tempfile.mkdtemp(prefix="kcp2b_m2b_")
try:
    os.makedirs(f"{tmp}/key_phrases/a2"); os.makedirs(f"{tmp}/a2/audit"); os.makedirs(f"{tmp}/a2/assembly")
    kd_src = f"{RUN}/key_phrases/a2/keywords_canonicalized.json"
    shutil.copy(kd_src, f"{tmp}/key_phrases/a2/keywords_canonicalized.json")
    shutil.copy(f"{RUN}/a2/audit/tts_generation_results.json", f"{tmp}/a2/audit/tts_generation_results.json")
    json.dump({"wav": "", "timeline": []}, open(f"{tmp}/a2/assembly/timeline.json", "w"))
    kw = json.load(open(kd_src, encoding="utf-8"))["items"]
    tts = json.load(open(f"{tmp}/a2/audit/tts_generation_results.json", encoding="utf-8"))["key_phrases"]
    rows, pairs = [], []
    for it in kw:
        n = str(it["rank"])
        ja_tts = (tts.get(n, {}).get("japanese_meaning") or {}).get("canonical_text") or ""
        rows.append({"part": f"key_phrase_{n}", "start": 0.0, "dur": 1.0, "file": "audio/a.mp3", "voice": "-", "style": "-", "script": f"{it['used_form']} / {ja_tts}", "notes": []})
        pairs.append((it["used_form"], ja_tts))
    res = za._user_page_rows(tmp, "a2", rows, pairs, "audio/", f"{tmp}/audio")
    for it in kw:
        n = it["rank"]
        blocks = "".join("".join(r["blocks"]) for r in res if r["part"] == f"Key Phrase {n}")
        ja_tts = (tts.get(str(n), {}).get("japanese_meaning") or {}).get("canonical_text")
        out[f"rank{n}"] = {"used_form": it["used_form"], "display_gloss(確定)": it["japanese_gloss"], "tts_canonical_text(音声入力。不変)": ja_tts,
                           "page_shows_display_gloss": it["japanese_gloss"] in blocks, "page_shows_tts_text_instead": (ja_tts != it["japanese_gloss"]) and (ja_tts in blocks)}
    print(json.dumps(out, ensure_ascii=False, indent=1))
finally:
    shutil.rmtree(tmp, ignore_errors=True)
