# -*- coding: utf-8 -*-
"""ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 委任_03B(兼 SELECTION-UI-BATCH-AND-VOCAB-AUDIO-01 委任_02D): 公開済み本番runのVocabulary & Expressions
「②追加解説」英語音声を、本番run自体に対して生成/再利用する(委任_02Cで配線済みの経路をそのまま呼ぶ。コピーrunではない)。

なぜ `--stage tts` 全体ではなく追加解説の生成関数だけを呼ぶか: runnerのtts stageは全segmentを走査し、status!=OK(例: ⑨ Std part3_k2のHR承認済みSTOPPED)の
segmentを再生成する(有料・Human Review承認済みの採用音声を上書きしうる)。本scriptは02Cが配線した追加解説の生成関数(X/Y=`xr._generate_vocab_extra_segments`、
Z=`a63._run_vocab_extra_specs`)だけを本番runのdirに対して呼び、既存のresults entry・wav・確定recordには触れない(前後のsha256 manifestで差分=追加のみを確認する)。
結果は tts_generation_results.json の top-level `vocab_extra` に追記(既存キーは不変・直前のresultsはarchive)。続けて `er137.gate_hook`(runnerのGate後hookと同一)で
公開用単体mp3 + vocab_audio.json をexportする(API 0)。

使い方: python ejh_run_main.py <WT> <MAIN> tools/ejh03b_vocab_extra_run_01.py --key <KEY> --level a2|b1b [--apply] [--max-cost-jpy 1.5]
  --apply 無し = 計画のみ(API 0・書込 0)。
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import er137_vocab_extra_audio_01 as vx  # noqa: E402
import er005_cost_logger as cl  # noqa: E402
import er011_human_review_lock_01 as review_lock  # noqa: E402

M = "C:/Users/tensh/eigo-radio"
X = f"{M}/er019_output/family_x_audio_production_wiring_01"
Y = f"{M}/er121_output/family_y_production_01"
Z = f"{M}/er026_output/family_z_production_e2e_01"
RUNS = {
    "x_moon": ("x", f"{X}/moon_shrinking__run_reselect_01", "raw_usage_log.jsonl"),
    "x_untidy": ("x", f"{X}/untidiness_family_resource__run_fx4_01", "raw_usage_log.jsonl"),
    "x_aichat": ("x", f"{X}/ai_chat_sponsored_persuasion__run_fx4_01", "raw_usage_log.jsonl"),
    "x_meta": ("x", f"{X}/meta_waddle_world__run_fx4_01", "raw_usage_log.jsonl"),
    "x_jwst": ("x", f"{X}/jwst_mystery_emission_line__run_fx4_01", "raw_usage_log.jsonl"),
    "y_fee": ("y", f"{Y}/redelivery_fee/run_style_fix_01", "cost_log.jsonl"),
    "y_sur": ("y", f"{Y}/surname_choice/run_02", "cost_log.jsonl"),
    "z_melos": ("z", f"{Z}/melos/run_p2_evidence_r3", "cost_log.jsonl"),
    "z_yuki": ("z", f"{Z}/yuki_onna/run_yo_prod_01", "cost_log.jsonl"),
}


def _load(p):
    return json.load(open(p, encoding="utf-8"))


def plan_of(fam: str, run: str, level: str) -> dict:
    ld = f"{run}/{level}"
    kp_dir = vx.find_kp_dir(ld, level)
    if kp_dir is None:
        return {"level_dir": ld, "kp_dir": None, "extras": [], "vocab": 0}
    kp_p = f"{kp_dir}/keywords_canonicalized.json"
    kp = _load(kp_p) if os.path.exists(kp_p) else None
    vocab = vx.load_level_vocab(kp_dir)
    split = vx.split_vocab(vocab, (kp or {}).get("items") or [])
    res_p = f"{ld}/audit/tts_generation_results.json"
    res = _load(res_p) if os.path.exists(res_p) else {}
    have = res.get(vx.RESULTS_KEY) or {}
    return {"level_dir": ld, "kp_dir": kp_dir, "kp": kp, "vocab": len(split), "split": split, "extras": vx.extras_of(split), "results_path": res_p, "results": res,
            "have": sorted(have)}


def run_xy(fam: str, run: str, level: str, pl: dict, log_name: str) -> dict:
    import er019_family_x_audio_production_runner_01 as xr
    import er019_family_x_style_profile_01 as sp
    import er078_secondary_run_scope_01 as srs
    ld = pl["level_dir"]
    rec = sp.read_record(run)
    profile = sp.verify_record(rec) if rec is not None else sp.PROFILE_DEFAULT
    backend = pl["results"].get("tts_backend") or xr.FAMILY_X_APPROVED_PRODUCTION_TTS_BACKEND
    cached = xr._load_cached_tts_results(ld)
    cl.install(f"{run}/{log_name}")

    @srs.with_secondary_run
    def _go():
        with cl.logging_context(os.path.basename(os.path.dirname(run)) if fam == "y" else os.path.basename(run), "tts"):
            return xr._generate_vocab_extra_segments(pl["kp"], f"{ld}/narration", cached, level=level, tts_backend=backend, style_profile=profile)
    return {"profile": profile, "backend": backend, "out": _go()}


def run_z(run: str, level: str, pl: dict, log_name: str) -> dict:
    import er063_family_z_audio_01 as a63
    import er026_family_z_fiction_production_runner_01 as m
    import er078_secondary_run_scope_01 as srs
    ld = pl["level_dir"]
    specs = a63.vocab_extra_specs(level, pl["extras"])
    cached = a63.load_results(ld)
    gens = m.wrap_generators_with_budget(a63.real_generators(), None, state={}, sentinel_dir=run)
    cl.install(f"{run}/{log_name}")
    evidence = []

    @srs.with_secondary_run
    def _go():
        return a63._run_vocab_extra_specs(run, ld, a63.narration_dir_for(run, level), specs, cached, gens, None, evidence, False)
    return {"out": _go(), "evidence": evidence}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", required=True, choices=sorted(RUNS))
    ap.add_argument("--level", required=True, choices=["a2", "b1b"])
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--max-cost-jpy", type=float, default=1.5)
    ap.add_argument("--out", default=None, help="結果summary json")
    a = ap.parse_args(argv)
    fam, run, log_name = RUNS[a.key]
    pl = plan_of(fam, run, a.level)
    brief = {"key": a.key, "level": a.level, "run": run, "vocab": pl["vocab"], "extras": [e["term"] for e in pl["extras"]], "already_in_results": pl.get("have")}
    print(json.dumps(brief, ensure_ascii=False))
    if not pl["extras"]:
        brief["note"] = "②追加解説なし(掲載項目はすべてKP再利用 or Vocabulary無し)"
    if a.apply and pl["vocab"]:
        import er019_family_x_audio_production_runner_01 as xr
        before = xr.compute_cost_jpy_so_far(f"{run}/{log_name}")[0] if os.path.exists(f"{run}/{log_name}") else 0.0
        if pl["extras"]:
            res = run_xy(fam, run, a.level, pl, log_name) if fam in ("x", "y") else run_z(run, a.level, pl, log_name)
            out = res["out"]
        else:
            out = {}                       # ②追加解説なし(掲載はすべてKP再利用): TTS 0。KP英語wavからの単体mp3 exportのみ
        after = xr.compute_cost_jpy_so_far(f"{run}/{log_name}")[0] if os.path.exists(f"{run}/{log_name}") else 0.0
        brief["cost_jpy"] = round(after - before, 4)
        if out:                             # 追加解説の結果をresultsのtop-level `vocab_extra` へ追記(既存キーは不変・直前のresultsはarchive)
            merged = dict((pl["results"].get(vx.RESULTS_KEY) or {}))
            merged.update(out)
            doc = dict(pl["results"])
            review_lock.archive_prior_tts_results(pl["results_path"])
            doc[vx.RESULTS_KEY] = merged
            with open(pl["results_path"], "w", encoding="utf-8") as f:
                json.dump(doc, f, ensure_ascii=False, indent=2, default=str)
        brief["entries"] = {k: {"status": v[vx.ROLE].get("status"), "reused": v[vx.ROLE].get("reused"), "reused_from_previous_run": v[vx.ROLE].get("reused_from_previous_run"),
                                "asr_verified": v[vx.ROLE].get("asr_verified"), "sha256": v[vx.ROLE].get("sha256")} for k, v in out.items()}
        if after - before > a.max_cost_jpy:
            brief["warning"] = f"cost {after - before:.3f} > cap {a.max_cost_jpy}"
        hook = vx.gate_hook(pl["level_dir"], None, a.level)         # runnerのGate後hookと同一(追加項目欠落STOP + 単体mp3 export。API 0)
        brief["export"] = {"complete": hook.get("complete"), "errors": hook.get("errors"), "items": len(hook.get("items") or [])}
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(brief, f, ensure_ascii=False, indent=1)
    print(json.dumps(brief, ensure_ascii=False, indent=1))
    return 0 if (not a.apply or brief.get("export", {}).get("complete", True)) else 4


if __name__ == "__main__":
    sys.exit(main())
