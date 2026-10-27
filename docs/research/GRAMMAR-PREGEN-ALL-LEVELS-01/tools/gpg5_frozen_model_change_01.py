# -*- coding: utf-8 -*-
"""GRAMMAR-PREGEN-ALL-LEVELS-01 委任_05 (viii): 凍結(ユーザー確定)後に Part 2 の MODEL 名を変えても require_final が Part2Stale にならない(05B是正)ことの実証(API 0・read-only)。
対象= 確定済み(confirmed_grammar_frozen.json あり)のrun dir。runner本体は起動せず、関数 require_final を MODEL patch 下で呼ぶ。run dirへは何も書かない。
使い方: gpg5_frozen_model_change_01.py --family z --story melos --slug melos --run run_gpg5_z_01 --level b1b"""
from __future__ import annotations
import argparse, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, ROOT)
from unittest import mock  # noqa: E402
import er120_part2_grammar_production_01 as g  # noqa: E402
import er120_part2_wiring_01 as p2w  # noqa: E402
import er128_kp_confirmed_content_01 as cc  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True, choices=("z", "y", "x")); ap.add_argument("--story", default="melos"); ap.add_argument("--slug", required=True)
    ap.add_argument("--run", required=True); ap.add_argument("--level", required=True, choices=("a2", "b1b"))
    ap.add_argument("--xslug"); a = ap.parse_args()
    if a.family == "z":
        import er026_family_z_fiction_production_runner_01 as zr
        ctx = zr.E2EContext(story_key=a.story, slug=a.slug, run=a.run, mode="dry-run")
        paragraphs, label = zr._part2_inputs(ctx, a.level)
        sd = zr._part2_dir(ctx, a.level)
        pool = zr._part2_pool(ctx, a.level)
    elif a.family == "x":
        import er019_family_x_audio_production_runner_01 as xr
        src = f"er019_output/{a.slug}/{a.run}"; out = f"er019_output/family_x_audio_production_wiring_01/{a.slug}__{a.run}"
        paragraphs, label = xr._part2_inputs_x(src, a.level)
        sd = xr._part2_study_dir(out, a.level)
        pool = xr._part2_pool_x(out, a.level)
    else:
        raise SystemExit("family y は個別に呼ぶ")
    fz = cc.load_frozen_grammar(sd)
    out = {"study_dir": sd, "frozen": bool(fz), "model_before": g.MODEL, "frozen_ids": [f.get("candidate_id") for f in (fz or [])] if isinstance(fz, list) else (fz or {}).get("candidate_id")}
    r0 = p2w.require_final(sd, paragraphs, label, level=a.level, next_command="x", ref_ja_pool=pool)
    out["baseline"] = "PASS(Part2Stale無し)"
    with mock.patch.object(g, "MODEL", "some-other-model-id"):
        out["model_patched"] = g.MODEL
        try:
            r1 = p2w.require_final(sd, paragraphs, label, level=a.level, next_command="x", ref_ja_pool=pool)
            out["after_model_change"] = "PASS(Part2Staleにならない)"
            out["result_unchanged"] = (r0.get("items") == r1.get("items"))
        except g.Part2Stale as e:
            out["after_model_change"] = "Part2Stale: " + str(e)[:300]
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0 if out["after_model_change"].startswith("PASS") else 3


if __name__ == "__main__":
    sys.exit(main())
