# -*- coding: utf-8 -*-
"""CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_02: Y runtime evidence(複数段落dev入力)の実行driver(有料: TTS Standard)。

なぜCLIを直接使わないか(事実・Fableへ報告): Y正式runner `er121_family_y_runner_01.py stage_tts()` は毎回 `ya.write_level_inputs(parsed)` で
`<level>/parts.json` を『記事本文(translate/<level>.md)をsplit_y_article[5段落契約: Voice段落=紹介行+本文1行]で解析した結果』で上書きする。
このため(a)parts.jsonへ空行を挿入したdev入力は正式CLIの`--stage tts_a2`で消える (b)記事本文へ空行を入れると段落数5の契約違反でSTOPする。
= 現行の本文契約では正式CLIから複数段落segmentを入力できない(Opus論点6『現行契約では構造的にchunk化条件を満たせない』の具体的な根拠)。
そこで本driverは、正式runnerが`stage_tts`の中で呼ぶ『正式な生成関数そのもの』(ya.generate_y_a2_segments / generate_y_b1_segments、正式Gate ya.y_style_gate、
正式組立 ya.assemble_level)を、正式runnerと同じ条件(build_real_context=STOP確認・RESTART_STORM/RUN_LOCK・費用ログ・予算guard・cost logger・
STANDARD TTS・only_segments_scope・同一guard)で呼ぶ。バイパスするのは `write_level_inputs`(parts.jsonの再生成)だけ。
新しい処理は追加しない(分割規則・減速・ポーズ・Gateは全て正式関数)。公開dir・run_01へは書かない。

使い方: .venv/Scripts/python.exe y_chunk_evidence_driver_01.py --level a2|b1b --segment y_voice_2 --budget-jpy 20 --out <summary.json>
"""
import argparse
import json
import os
import sys
import time

ap = argparse.ArgumentParser()
ap.add_argument("--level", required=True, choices=["a2", "b1b"])
ap.add_argument("--segment", default="y_voice_2")
ap.add_argument("--slug", default="redelivery_fee_stdchunk_ev")
ap.add_argument("--run", default="run_ev_01")
ap.add_argument("--budget-jpy", type=float, default=20.0)
ap.add_argument("--out", required=True)
a = ap.parse_args()
REPO = os.getcwd()
sys.path.insert(0, REPO)

import er121_family_y_audio_01 as ya  # noqa: E402
import er121_family_y_runner_01 as r  # noqa: E402
import er121_family_y_structure_01 as ys  # noqa: E402

assert r.RUN_ROOT == "er121_output/family_y_production_01"
args = r.build_parser().parse_args(["--mode", "real", "--slug", a.slug, "--run", a.run, "--stage", f"tts_{a.level}",
                                    "--approved-budget-jpy", str(a.budget_jpy), "--tts-execution-mode", "STANDARD"])
assert args.slug != "redelivery_fee" and "run_01" not in args.run          # 実Y run・公開dirを触らない
ctx = r.build_real_context(args)                                          # STOP確認・launch guard・予算・cost logger・STOP guardをrunnerと同条件で設置
assert os.environ.get("TTS_EXECUTION_MODE") == "STANDARD"
try:
    out = ctx.out_dir
    lv = a.level
    t0 = time.time()
    guard = lambda label: r._guard(ctx, f"tts_{lv}_{label}", r.TTS_CLIP_EST_JPY)        # noqa: E731  runnerのstage_ttsと同じguard
    summary = {"level": lv, "segment": a.segment, "out_dir": out, "budget_jpy_cap": a.budget_jpy, "tts_execution_mode": os.environ["TTS_EXECUTION_MODE"],
               "bypassed": "write_level_inputs(parts.jsonの記事契約からの再生成)のみ", "started_epoch": t0}
    with ctx.stage_context(f"tts_{lv}"):
        with ya.only_segments_scope({a.segment}):
            if lv == "b1b":
                s = ya.generate_y_b1_segments(out, style_profile=r.STYLE_PROFILE, guard=guard)
            else:
                ja_title = ys.split_y_article(r._rd(r._ja_path(ctx)))["title"]
                s = ya.generate_y_a2_segments(out, ja_title, style_profile=r.STYLE_PROFILE, guard=guard)
    summary["tts_summary"] = s
    summary["tts_seconds"] = round(time.time() - t0, 1)
    gate = ya.y_style_gate(out, lv, r.STYLE_PROFILE)
    summary["gate_status"] = gate["status"]
    summary["gate_y_body_blocked"] = gate["y_body_blocked"]
    summary["gate_x_blocked_after_filter"] = gate["x_gate_blocked_after_filter"]
    if gate["status"] == "PASS":
        article = ys.canonical_body(r._rd(r._level_text_path(ctx, lv)))
        asm_summary = ya.assemble_level(out, lv, style_profile=r.STYLE_PROFILE, slug=ctx.slug, article_text=article)
        summary["assemble"] = {k: asm_summary.get(k) for k in ("status", "out_path", "duration_seconds", "clipping_detected", "peak")}
        summary["assemble_chunk_tts"] = asm_summary.get("chunk_tts")
    import er019_family_x_audio_production_runner_01 as xr  # noqa: E402
    summary["cost_jpy_so_far"] = xr.compute_cost_jpy_so_far(f"{out}/cost_log.jsonl")
    summary["finished_epoch"] = time.time()
    json.dump(summary, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print("WROTE", a.out, "gate=", summary["gate_status"], "cost=", summary["cost_jpy_so_far"])
finally:
    r._release_launch_lock()                                              # RUN_LOCKを必ず解放(commitしない)
