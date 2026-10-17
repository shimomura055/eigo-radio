# -*- coding: utf-8 -*-
"""FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_17: run_e2e_03 全clip Style適用表 + Dialogue別Voice突合(有料APIなし、read-only)。
BAPE er019_bape_style_table_04.py相当。入力: <run>/{a2,b1b}/audit/{tts_generation_results.json,style_record.json}、
dialogue_attribution_*.json、speaker_table.md、(比較用)run_e2e_02の同tts_generation_results.json。
exp_match = clipの effective_style_prefix_sha256 == style_record.roles[role_style_key].style_prefix_sha256(null roleはNone)。
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er063_family_z_audio_01 as z  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--run-dir", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--compare-run-dir", default="er026_output/family_z_production_e2e_01/melos/run_e2e_02")
A = ap.parse_args()


def rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


rows = []
sha_to_label = {v: k for k, v in z._STYLE_SHA256.items()}


def add(level, seg, d, rec_roles):
    rk = d.get("role_style_key")
    st = d.get("style") or {}
    exp = (rec_roles.get(rk) or {}).get("style_prefix_sha256") if rk else None
    eff = st.get("effective_style_prefix_sha256")
    first = st.get("style_prefix_sha256")
    ds = d.get("attempts") or []
    rows.append({
        "level": level, "segment": seg, "clip_kind": d.get("clip_kind"), "speaker": d.get("speaker"), "voice": d.get("voice"),
        "role_style_key": rk, "style_label": st.get("instruction_label"),
        "expected_label": (rec_roles.get(rk) or {}).get("style_label") if rk else None,
        "style_sha12": (first or "")[:12], "effective_sha12": (eff or "")[:12], "expected_sha12": (exp or "")[:12],
        "exp_match": (eff == exp) if exp else None,
        "sha_known_label": sha_to_label.get(eff),
        "fallback_used": st.get("fallback_used"),
        "actual_model_ids": d.get("model_ids_measured"), "attempt_models": sorted({a.get("tts_model_id") for a in ds if a.get("tts_model_id")}),
        "tts_backend": d.get("tts_backend"), "status": d.get("status"), "attempts_n": len(ds),
        "audio_classification_last": (ds[-1].get("audio_classification") if ds else None),
        "slowdown_ratio": d.get("slowdown_ratio"), "slowdown_applied": d.get("slowdown_applied"),
        "audio_text_deviation": d.get("audio_text_deviation"), "z_adoption": d.get("z_adoption"),
        "duration_seconds": d.get("duration_seconds"), "sha256_12": (d.get("sha256") or "")[:12],
    })


roles_by_level = {}
for level in ("b1b", "a2"):
    pr = f"{A.run_dir}/{level}/audit/tts_generation_results.json"
    ps = f"{A.run_dir}/{level}/audit/style_record.json"
    if not (os.path.exists(pr) and os.path.exists(ps)):
        continue
    r, sr = rj(pr), rj(ps)
    roles_by_level[level] = sr["roles"]
    for seg, d in r["segments"].items():
        add(level, seg, d, sr["roles"])
    for n, k in sorted(r["key_phrases"].items()):
        for part, d in k.items():
            if isinstance(d, dict):
                add(level, f"kp{n}_{part}", d, sr["roles"])

by_role = {}
for x in rows:
    b = by_role.setdefault(f"{x['level']}|{x['role_style_key']}", {"label": x["expected_label"], "clips": 0, "exp_match_true": 0, "exp_match_false": 0,
                                                              "exp_match_none": 0, "fallback": 0, "models": set(), "voices": set()})
    b["clips"] += 1
    b["exp_match_true"] += 1 if x["exp_match"] is True else 0
    b["exp_match_false"] += 1 if x["exp_match"] is False else 0
    b["exp_match_none"] += 1 if x["exp_match"] is None else 0
    b["fallback"] += 1 if x["fallback_used"] else 0
    b["models"].update(x["actual_model_ids"] or x["attempt_models"])
    b["voices"].add(x["voice"])
for b in by_role.values():
    b["models"] = sorted(m for m in b["models"] if m)
    b["voices"] = sorted(v for v in b["voices"] if v)

# X定数sha照合(style_recordの共通label sha == X定数(_xs)のsha256か)
x_const = {}
for lab in z._COMMON_STYLE_LABELS:
    x_const[lab] = {"z_literal": z._STYLE_SHA256[lab], "x_text_sha": z._sha256_text(z._STYLE_TEXT[lab]),
                    "match": z._sha256_text(z._STYLE_TEXT[lab]) == z._STYLE_SHA256[lab]}
rec_vs_x = []
for lv, roles in roles_by_level.items():
    for rk, spec in roles.items():
        lab = (spec.get("style_label") or "")
        if lab in z._COMMON_STYLE_LABELS:
            rec_vs_x.append({"level": lv, "role": rk, "label": lab, "record_sha_eq_x_const": spec.get("style_prefix_sha256") == z._STYLE_SHA256[lab]})

# Dialogue別Voice
dlg = {"dialogue_clips": [], "pd06_sha_on_dialogue": 0, "voice_same_as_e02": None, "mismatch_vs_e02": []}
pd06 = z._STYLE_SHA256["PD06"]
cmp_voices = {}
for level in ("b1b", "a2"):
    pc = f"{A.compare_run_dir}/{level}/audit/tts_generation_results.json"
    if os.path.exists(pc):
        for seg, d in rj(pc)["segments"].items():
            if d.get("clip_kind") == "dialogue":
                cmp_voices[(level, seg)] = (d.get("speaker"), d.get("voice"))
for x in rows:
    if x["clip_kind"] == "dialogue":
        eff_full = x["effective_sha12"]
        on_pd06 = bool(eff_full) and pd06.startswith(eff_full)
        dlg["pd06_sha_on_dialogue"] += 1 if on_pd06 else 0
        e02 = cmp_voices.get((x["level"], x["segment"]))
        same = (e02 == (x["speaker"], x["voice"])) if e02 else None
        if same is False:
            dlg["mismatch_vs_e02"].append({"level": x["level"], "segment": x["segment"], "e03": [x["speaker"], x["voice"]], "e02": list(e02)})
        dlg["dialogue_clips"].append({"level": x["level"], "segment": x["segment"], "speaker": x["speaker"], "voice": x["voice"],
                                      "effective_sha12": eff_full, "pd06_applied": on_pd06, "same_as_e02": same})
dlg["n"] = len(dlg["dialogue_clips"])
dlg["voice_same_as_e02"] = (len(dlg["mismatch_vs_e02"]) == 0) if dlg["n"] and cmp_voices else None
dlg["speaker_voice_pairs"] = sorted({(c["speaker"], c["voice"]) for c in dlg["dialogue_clips"]})
dlg["speaker_voice_pairs"] = [list(p) for p in dlg["speaker_voice_pairs"]]
# dialogue_attribution と clip speaker の突合
attr_chk = {}
for level in ("b1b", "a2"):
    pa = f"{A.run_dir}/dialogue_attribution_{level}.json"
    if os.path.exists(pa):
        a = rj(pa)
        attr_chk[level] = {"keys": list(a.keys())[:6] if isinstance(a, dict) else f"list[{len(a)}]"}

styled = [x for x in rows if x["exp_match"] is not None]
out = {
    "run_dir": A.run_dir, "n_rows": len(rows), "styled_rows": len(styled),
    "exp_match_true": sum(1 for x in styled if x["exp_match"] is True), "exp_match_false": sum(1 for x in styled if x["exp_match"] is False),
    "exp_match_none_rows_sha_undefined_dialogue": sum(1 for x in rows if x["exp_match"] is None),
    "k2_fallback_count": sum(1 for x in rows if x["role_style_key"] == "KP_EN" and x["fallback_used"]),
    "by_level_role": by_role, "x_const_vs_z_literal": x_const, "style_record_vs_x_const": rec_vs_x,
    "dialogue": dlg, "dialogue_attribution_files": attr_chk, "rows": rows,
}
os.makedirs(os.path.dirname(os.path.abspath(A.out)), exist_ok=True)
with open(A.out, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in out.items() if k not in ("rows", "dialogue", "by_level_role")}, ensure_ascii=False)[:1800])
print("dialogue:", json.dumps({k: v for k, v in dlg.items() if k != "dialogue_clips"}, ensure_ascii=False)[:800])
for k, v in sorted(by_role.items()):
    print(k, json.dumps(v, ensure_ascii=False, default=list))
