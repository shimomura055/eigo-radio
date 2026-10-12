# -*- coding: utf-8 -*-
"""FAMILY-Z-SHORT-CLIP-ASR-CONTEXT-GENERALIZATION-TRIAL-01: 条件(結合音声)ビルダー(Trial/DEV only, オフライン・無料)。

configJSON(作品固有語・clip pool・targets・recipes)を読み、結合wavとconditions_manifestを生成する。
作品固有語はconfigに閉じ、本コードにはMelos固有値を持たない。

使い方:
  python er065_short_clip_asr_context_trial_01_build.py --config <config.json> --out-dir <trial dir> --manifest-name <name>.json

config形式:
 {"work_id","focus_word","target_canonical","gap_ms",
  "pools": {pool: {"slots": {slot: [clip_id,...]}, "clips": {clip_id: {path,text,voice,model,note}}}},
  "targets": [{"id","path","pool","note","label_hint"}],
  "recipes": [{"id","pre":[slot..],"post":[slot..],"kind":"alone|same_voice|diff_voice|mixed_real"}],
  "targets_recipes": {target_id: [recipe_id...] | "all"}}
 recipeのpre/postはslot名のリスト(poolのslotsで解決。slot値のclip列を順に連結)。
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er065_short_clip_asr_context_trial_01_lib as L


def build(cfg: dict, out_dir: str, name: str) -> dict:
    gap = int(cfg.get("gap_ms", 300))
    audio_dir = os.path.join(out_dir, "concat_audio", name.replace(".json", ""))
    os.makedirs(audio_dir, exist_ok=True)
    conds = []
    recipes = {r["id"]: r for r in cfg["recipes"]}
    for t in cfg["targets"]:
        pool = cfg["pools"][t["pool"]]
        t_clip = {"clip_id": t["id"], "path": t["path"], "text": t.get("canonical", cfg["target_canonical"]), "voice": t.get("voice"),
                  "model": t.get("model"), "role": "target"}
        t_clip["dur"] = round(L.wav_duration(t["path"]), 3)
        t_clip["sha256"] = L.sha256_file(t["path"])
        rids = cfg.get("targets_recipes", {}).get(t["id"], "all")
        if rids == "all":
            rids = [r["id"] for r in cfg["recipes"]]
        for rid in rids:
            r = recipes[rid]

            def resolve(slots):
                out = []
                for s in slots:
                    for cid in pool["slots"][s]:
                        c = pool["clips"][cid]
                        out.append({"clip_id": cid, "path": c["path"], "text": c["text"], "voice": c.get("voice"),
                                    "model": c.get("model"), "role": "ctx", "slot": s,
                                    "dur": round(L.wav_duration(c["path"]), 3), "sha256": L.sha256_file(c["path"])})
                return out
            pre, post = resolve(r.get("pre", [])), resolve(r.get("post", []))
            parts = pre + [t_clip] + post
            tidx = len(pre)
            cond_id = f"{t['id']}__{rid}"
            wav_path = os.path.join(audio_dir, cond_id + ".wav")
            if len(parts) == 1:
                samples, spans = L.concat_parts(parts, gap)
            else:
                samples, spans = L.concat_parts(parts, gap)
            L.write_wav(wav_path, samples)
            tv = t.get("voice")
            for p in parts:
                p["same_voice_as_target"] = (p.get("voice") == tv) if p["role"] == "ctx" else None
                p["contains_focus_word"] = t.get("focus_word", cfg["focus_word"]).lower() in (p["text"] or "").lower()
            for i, p in enumerate(parts):
                p["span"] = spans[i]
            pre_sec = round(sum(p["dur"] for p in pre), 2)
            post_sec = round(sum(p["dur"] for p in post), 2)
            conds.append({
                "cond_id": cond_id, "target_id": t["id"], "recipe_id": rid, "kind": r.get("kind"),
                "group": cfg.get("group", "main"), "work_id": cfg["work_id"], "pool": t["pool"],
                "target_note": t.get("note"), "label_hint": t.get("label_hint"),
                "parts": parts, "target_index": tidx,
                "expected_parts": [p["text"] for p in parts],
                "canonical_target": t.get("canonical", cfg["target_canonical"]), "focus_word": t.get("focus_word", cfg["focus_word"]),
                "category": t.get("category"), "defect": t.get("defect"),
                "gap_ms": gap, "wav": wav_path.replace("\\", "/"),
                "wav_sha256": L.sha256_file(wav_path), "total_sec": round(len(samples) / 24000, 3),
                "pre_ctx_sec": pre_sec, "post_ctx_sec": post_sec, "n_ctx_clips": len(pre) + len(post),
                "target_span": spans[tidx],
                "ctx_all_same_voice": all(p["same_voice_as_target"] for p in parts if p["role"] == "ctx") if (pre or post) else None,
                "ctx_has_focus_word": any(p["contains_focus_word"] for p in parts if p["role"] == "ctx"),
            })
    return {"work_id": cfg["work_id"], "focus_word": cfg["focus_word"], "target_canonical": cfg["target_canonical"],
            "gap_ms": gap, "n_conditions": len(conds), "conditions": conds}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--manifest-name", required=True)
    a = ap.parse_args()
    L.install_write_guard([a.out_dir])
    cfg = json.load(open(a.config, encoding="utf-8"))
    m = build(cfg, a.out_dir, a.manifest_name)
    with open(os.path.join(a.out_dir, a.manifest_name), "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=1)
    print("conditions:", m["n_conditions"], "->", os.path.join(a.out_dir, a.manifest_name))
    print(L.write_guard_report()["blocked_write_attempts"])


if __name__ == "__main__":
    main()
