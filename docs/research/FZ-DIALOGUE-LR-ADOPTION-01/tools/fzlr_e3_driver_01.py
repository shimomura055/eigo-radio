# -*- coding: utf-8 -*-
"""FZ-DIALOGUE-LR-ADOPTION-01 委任_03 E3: 注入runtime evidence driver(evidence専用。Production codeではない・成果物の根拠にしない)。

正式runner(er026 main)を copy-run(run_sf_prod_01の複製・対象clipのstate/Lock/wavのみ初期化)に対して同一process内で1回起動し、
 * tru_ev_core_01.installed(空Plan) = 台帳分離(HRQ/attempt_history/Master Audio Storeはcase専用dir)+観測(TTS resolve/sleep/cooldown/LR)
 * fzlr_inject_harness_01.NgInjector = 指定通算attempt番号のASR判定のみ『注入NG』(全記録INJECTED)
を重ねる。Style・Voice・速度・待機・回数・Gate実装には触れない。

使い方: python fzlr_e3_driver_01.py --case std --prep   (copy-run作成+stop_scope_check。有料runなし)
        python fzlr_e3_driver_01.py --case std --run-once [--kill-in-cooldown 60] --launch-tag L1
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "docs", "research", "TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01", "tools"))
sys.path.insert(0, HERE)
import tru_ev_core_01 as core  # noqa: E402  (chdir(REPO))
import fzlr_inject_harness_01 as H  # noqa: E402

EVD = "docs/research/FZ-DIALOGUE-LR-ADOPTION-01/e3_evidence"
SRC = "er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01"
ROOT_RUNS = "er026_output/family_z_production_e2e_01/in_a_grove"
CASES = {
    # Std: ①〜⑥の全6スロットをNG注入(LR実走・2回目180秒・⑥従来Dialogue・終端Lock/HRQ1行)
    "std": {"level": "a2", "run": "run_fzlr_ev_a2_01", "clip": "full_story_part2_c1", "ng": [1, 2, 3, 4, 5, 6], "stage": "tts_a2", "budget": 20},
    # Adv: ①〜③NG注入→LR→④は実判定(途中PASS即終了・減速後再検証・Voice/Style維持)。①②後の待機でkill→再開(消費済み不再実行)
    # std2: 偽T2不具合(level_facts)是正後の再実走。Std全6スロットNG注入
    "std2": {"level": "a2", "run": "run_fzlr_ev_a2_02", "clip": "full_story_part1_c1", "ng": [1, 2, 3, 4, 5, 6], "stage": "tts_a2", "budget": 20},
    "std3": {"level": "a2", "run": "run_fzlr_ev_a2_03", "clip": "full_story_part1_c1", "ng": [1, 2, 3, 4, 5, 6], "stage": "tts_a2", "budget": 20},
    "std4": {"level": "a2", "run": "run_fzlr_ev_a2_04", "clip": "full_story_part1_c1", "ng": [1, 2, 3, 4, 5, 6], "stage": "tts_a2", "budget": 20},
    "std5": {"level": "a2", "run": "run_fzlr_ev_a2_05", "clip": "full_story_part1_c6", "ng": [1, 2, 3, 4, 5, 6], "stage": "tts_a2", "budget": 20},
    "adv": {"level": "b1b", "run": "run_fzlr_ev_b1b_01", "clip": "full_story_part2_c1", "ng": [1, 2, 3], "stage": "tts_b1b", "budget": 20},
}


def _rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _wj(p, o):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(o, f, ensure_ascii=False, indent=2)


def prep(c):
    dst = f"{ROOT_RUNS}/{c['run']}"
    if os.path.exists(dst):
        raise SystemExit(f"copy-run already exists: {dst}")
    ign = shutil.ignore_patterns("run_launch_log.jsonl", "cost_log.jsonl", "STOP", "*.pre_*", "voice_assignment_STALE*")
    shutil.copytree(SRC, dst, ignore=ign)
    open(f"{dst}/cost_log.jsonl", "w").close()
    lv, clip = c["level"], c["clip"]
    sp = f"{dst}/{lv}/audit/dialogue_ctx_attempt_state.json"
    st = _rj(sp)
    st["clips"].pop(clip, None)
    _wj(sp, st)
    lp = f"{dst}/{lv}/audit/review_lock_state.json"
    lk = _rj(lp)
    lk.pop(clip, None)
    _wj(lp, lk)
    rp = f"{dst}/{lv}/audit/tts_generation_results.json"
    if os.path.exists(rp):
        r = _rj(rp)
        (r.get("segments") or {}).pop(clip, None)
        _wj(rp, r)
    for p in (f"{dst}/{lv}/narration/{clip}.wav",):
        if os.path.exists(p):
            os.remove(p)
    ad = f"{dst}/{lv}/narration/attempts"
    if os.path.isdir(ad):
        for fn in os.listdir(ad):
            if fn.startswith(clip + "_"):
                os.remove(os.path.join(ad, fn))
    pb = f"{dst}/{lv}/audit/tts_block_progress/{clip}.json"
    if os.path.exists(pb):
        os.remove(pb)
    os.makedirs(f"{EVD}/{c['run']}", exist_ok=True)
    rc = core.stop_scope_check(dst, f"{EVD}/{c['run']}/stop_scope_prep.json")
    print("prep done", dst, "stop_scope rc=", rc)
    return rc


def canonical_of(c):
    plan = _rj(f"{SRC}/segment_plan_{c['level']}.json")
    return [x for x in plan["clips"] if x["id"] == c["clip"]][0]["text"]


def run_once(c, tag, kill_s):
    import er026_family_z_fiction_production_runner_01 as runner
    dst = f"{ROOT_RUNS}/{c['run']}"
    out = f"{EVD}/{c['run']}"
    os.makedirs(out, exist_ok=True)
    rc = core.stop_scope_check(dst, f"{out}/stop_scope_{tag}.json")
    if rc != 0:
        print("STOP scope rc=", rc)
        return 3
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    inj = H.NgInjector(c["clip"], {n: None for n in c["ng"]}, f"{out}/injection_{tag}.jsonl", canonical_text=canonical_of(c))
    rec = core.Recorder()
    iso = f"{out}/ledgers"
    t_start = time.time()
    if kill_s:
        sp = f"{dst}/{c['level']}/audit/dialogue_ctx_attempt_state.json"

        def watcher():
            while True:
                time.sleep(2)
                try:
                    cl = (_rj(sp)["clips"].get(c["clip"]) or {})
                    cd = cl.get("cooldown") or {}
                    if cl.get("status") == "IN_PROGRESS" and cd.get("started_epoch") and cd["started_epoch"] >= t_start and not cd.get("ended_epoch"):
                        time.sleep(kill_s)
                        with open(f"{out}/kill_{tag}.json", "w", encoding="utf-8") as f:
                            json.dump({"killed_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "pid": os.getpid(), "self_kill_after_cooldown_start_s": kill_s,
                                       "n_started": cl.get("n_started"), "cooldown": cd, "note": "evidence用: 自process(自分が起動したPID)の意図的終了。外部停止ではない"}, f, ensure_ascii=False, indent=2)
                        os._exit(137)
                except Exception:   # noqa: BLE001
                    pass
        threading.Thread(target=watcher, daemon=True).start()
    argv = ["--story", "in_a_grove", "--run", c["run"], "--mode", "real", "--approved-budget-jpy", str(c["budget"]),
            "--tts-execution-mode", "STANDARD", "--stages", c["stage"], "--only-clips", c["clip"]]
    exc = None
    code = None
    try:
        with core.installed(core.Plan(), rec, iso, cost_log=f"{dst}/cost_log.jsonl"):
            with inj.patched():
                code = runner.main(argv)
    except SystemExit as e:
        code = e.code
    except BaseException as e:   # noqa: BLE001
        exc = f"{type(e).__name__}: {e}"[:600]
    t_end = time.time()
    ev = {"management_id": "FZ-DIALOGUE-LR-ADOPTION-01", "INJECTED": True, "note": "NG注入evidence(成果物の品質根拠にしない)", "case": c, "launch_tag": tag,
          "argv": argv, "rc": code, "exception": exc, "started_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(t_start)),
          "ended_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(t_end)), "wall_seconds": round(t_end - t_start, 1), "pid": os.getpid(),
          "tts_resolve": rec.tts_resolve, "tts_resolve_count": len(rec.tts_resolve), "tts_api_calls": rec.tts_api, "sleep_total_seconds": round(rec.sleep_total, 1),
          "cooldowns": rec.cooldowns, "lr_calls": rec.lr_calls, "judges": rec.judges, "post_judges": rec.post_judges,
          "injection_records": inj.records, "stop_checks": rec.stop_checks}
    _wj(f"{out}/evidence_{tag}.json", ev)
    print("evidence ->", f"{out}/evidence_{tag}.json", "rc=", code, "exc=", exc)
    return 0 if exc is None else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", choices=list(CASES), required=True)
    ap.add_argument("--prep", action="store_true")
    ap.add_argument("--run-once", action="store_true")
    ap.add_argument("--launch-tag", default="L1")
    ap.add_argument("--kill-in-cooldown", type=float, default=0.0)
    a = ap.parse_args()
    cfg = CASES[a.case]
    if a.prep:
        sys.exit(prep(cfg))
    if a.run_once:
        sys.exit(run_once(cfg, a.launch_tag, a.kill_in_cooldown))
    ap.print_help()
