# -*- coding: utf-8 -*-
"""FCJ 委任_03: Run A/B 結果をclipごとに表へ集計する(API 0、読取専用)。出力: evidence_03/clip_table_{run}.json + clip_table.md"""
import json
import os
import wave

EV = "er079_output/family_c_ja_tts_production_fix_01/evidence_03"


def secs(p):
    try:
        with wave.open(p, "rb") as w:
            return round(w.getnframes() / float(w.getframerate()), 2)
    except Exception:  # noqa: BLE001
        return None


def table(run):
    a2 = f"{EV}/{run}/a2"
    aud = json.load(open(f"{a2}/audit/tts_generation_results.json", encoding="utf-8"))["segments"]
    raw = [json.loads(l) for l in open(f"{a2}/raw_usage_log.jsonl", encoding="utf-8") if l.strip()]
    lang_gen = {}
    for r in raw:
        m = r.get("meta") or {}
        if r.get("kind") == "tts" and m.get("status") == "OK":
            lang_gen.setdefault(r["label"], m.get("language"))
    rows = []
    for cid, e in aud.items():
        wav = f"{a2}/audio/{cid}.wav"
        meta_p = wav + ".ok.meta.json"
        meta = json.load(open(meta_p, encoding="utf-8")) if os.path.exists(meta_p) else {}
        aj = e.get("asr_judgement") or {}
        generated = cid in lang_gen
        rows.append({"clip": cid, "generated_this_run": generated, "language_actual": lang_gen.get(cid),
                     "seconds": secs(wav), "state": aj.get("state") if aj else None, "reason": aj.get("reason_code") if aj else None,
                     "primary_label": (aj.get("primary") or {}).get("label"), "secondary_called": (aj.get("secondary") or {}).get("called"),
                     "provenance_basis": meta.get("provenance_basis"), "reuse_from_source": meta.get("reuse_from_source"),
                     "meta_tts_text_sha256": (meta.get("tts_text_sha256") or "")[:12], "wav_sha256": (e.get("sha256") or "")[:12]})
    return rows


out = {}
md = []
for run in ("run_a", "run_b"):
    rows = table(run)
    out[run] = rows
    json.dump(rows, open(f"{EV}/clip_table_{run}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    md.append(f"## {run}\n\n| clip | 生成 | language | 秒 | state | reason | Secondary | 由来 |\n|---|---|---|---|---|---|---|---|")
    for r in rows:
        if r["clip"].startswith(("kp", "welcome", "preview_intro", "key_phrases", "full_story")):
            continue
        md.append(f"| {r['clip']} | {'新規' if r['generated_this_run'] else '再利用'} | {r['language_actual']} | {r['seconds']} | {r['state']} | {r['reason']} | {r['secondary_called']} | {r['provenance_basis']} |")
    md.append("")
open(f"{EV}/clip_table.md", "w", encoding="utf-8").write("\n".join(md))
print("\n".join(md))
