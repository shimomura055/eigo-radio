# -*- coding: utf-8 -*-
"""CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_03: Z Adv不変golden凍結(実装前HEADで実行、API 0)。
既存Z run(melos run_fzcw_e1_01 / tell_tale run_sf_prod_01)のb1bについて、正式経路 load_level_inputs(for_tts=True) が作るplan(ClipSpec列)・chunk plan・
_z_chunk_parent_display・attach_chunk_meta(level未指定)・build_reuse_key を凍結。実装後はtestがバイト一致を確認する。a2の現状(Std非chunk)も参考凍結。"""
import dataclasses, hashlib, json, os, sys
sys.path.insert(0, os.getcwd())
import er026_family_z_fiction_production_runner_01 as r
import er063_family_z_audio_01 as z
import er117_chunk_tts_production_01 as ct

RUNS = {"melos_run_fzcw_e1_01": ("melos", "melos", "run_fzcw_e1_01"),
        "tell_tale_run_chunk_01": ("the_tell_tale_heart", "the_tell_tale_heart", "run_chunk_01")}


def sha(o):
    return hashlib.sha256(json.dumps(o, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def compute() -> dict:
    out = {"frozen_at_head": os.environ.get("FREEZE_HEAD", "?"), "planner_version": ct.CHUNK_PLANNER_VERSION, "runs": {}}
    for key, (story, slug, run) in RUNS.items():
        ctx = r.E2EContext(story_key=story, slug=slug, run=run, mode="dry-run")
        rec = {}
        for level in ("b1b", "a2"):
            try:
                inp = r.load_level_inputs(ctx, level, for_tts=True)
            except Exception as e:  # noqa: BLE001
                # 正式入力が未確定のrun(例 tell_tale run_chunk_01のb1b=Part2未確定)は、chunk plan関数だけを同じ入力(segment_plan+本文)で凍結する
                m = r._m()
                plan_ = m.w62.rj(f"{ctx.out_dir}/segment_plan_{level}.json")
                _t, _body = m.st.split_title_body(m.w62.rd(m.w62.level_text_path(ctx.out_dir, level)))
                cps_ = ct.plan_z_level(plan_["clips"], m.st.clean_body_paragraphs(_body), level)
                rec[level] = {"fallback_chunk_plans_only": True, "chunk_plans": cps_, "chunk_plans_sha256": sha(cps_), "load_error": e.__class__.__name__}
                continue
            plan = inp["plan"]
            specs = [dataclasses.asdict(s) for s in plan]
            cps = inp["chunk_plans"]
            disp, meta = {}, {}
            for pid, pl in cps.items():
                segs = {c["chunk_id"]: {"z_adoption": "adopted", "style": {"style_prefix_sha256": "x"}} for c in pl["chunks"]}
                disp[pid] = z._z_chunk_parent_display(pl, segs)
                c0 = pl["chunks"][0]
                meta[pid] = ct.attach_chunk_meta({}, pid, {"index": c0["index"], "words": c0["words"], "boundary_kind": c0["boundary_kind"]}, len(pl["chunks"]))
            rec[level] = {"n_specs": len(specs), "specs_sha256": sha(specs), "specs": specs, "chunk_plans": cps, "chunk_plans_sha256": sha(cps),
                          "parent_display": disp, "attach_chunk_meta": meta,
                          "reuse_keys": {s.clip_id: z.build_reuse_key(s) for s in plan if s.kind in ("narrator", "dialogue")},
                          "story_clips": inp["story_clips"]}
        out["runs"][key] = rec
    return out


if __name__ == "__main__":
    out = compute()
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "z_adv_golden_01.json")
    json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True, default=str)
    print({k: {l: (str(v.get("specs_sha256") or v.get("chunk_plans_sha256"))[:14], len(v.get("chunk_plans") or {}), [x for x, pl in (v.get("chunk_plans") or {}).items() if pl["chunked"]]) for l, v in rec.items()} for k, rec in out["runs"].items()})
