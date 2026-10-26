# -*- coding: utf-8 -*-
"""FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 Phase 2 runtime evidence driver(委任_02で実装。**本委任では実行しない**=mock testのみ。実行は別委任・費用承認後)。

目的: 正式Production runner(`er026_family_z_fiction_production_runner_01.main`)を**同一プロセス内**で起動し(STOP確認・SDK入口STOP guard・cost loggerなど
runner起動時のguardを全部通す)、Gateの出力を **NG方向にだけ** 上書きして、文脈・感情付きTTS -> 600秒cooldown -> 従来方式 の遷移を実TTS/実ASRで検証する。

Gate迂回ではない理由(DESIGN_02 §H):
  - 注入口はProduction codeに無い(env/flag/設定dictなし)。本driverはProductionから参照されない独立scriptで、同一プロセス内のmodule属性を包むだけ。
  - 実TTS呼出・実ASR(Primary/Secondary統一judge)・disfluency gateは**全て実際に実行された後**に、同attemptの最後(repetition QA gate / Advは減速後の統一judge再検証)の
    戻り値を NG方向(verified:True -> False)にだけ上書きする。NG -> OK方向の上書きは実装しない(testで固定)。上書きが無いattempt(3回目の従来方式を含む)は完全な本物の判定。
  - E-1(正常経路)は注入計画が空であることをassertし、注入(上書き)呼出0を証拠に記録する。
  - 強制NGはrepetition QA段階なので、ASRの判定自体はPASSのまま=最終slotでASRがHR queueへ書く経路は発火しない(Opus M-10(d))。強制NG由来のHR queue行・attempt_history行は
    「evidence専用・対応不要」として台帳で無効化する(Opus R-1)。費用は量産単価ではなく開発費に計上する。

使い方(実行は別委任。T-2: 正式リリース前のTTSは STANDARD を明示):
  $env:TTS_EXECUTION_MODE="STANDARD"; .venv\\Scripts\\python.exe er122_fzcw_runtime_evidence_01.py --case E-1 --work the_monkeys_paw --run run_fzcw_e1_01 --budget-jpy 60
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import subprocess
import sys
import time

MANAGEMENT_ID = "FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01"
ROOT = os.path.dirname(os.path.abspath(__file__))
EVIDENCE_DIR = "docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01"
E2E_RUN_ROOT = "er026_output/family_z_production_e2e_01"
FORBIDDEN_STAGES = ("pages", "page_verify")        # 公開page出力は一切しない
SHARED_LEDGERS = ("er011_output/attempt_history.jsonl", "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl",
                  "er007_output/ja_asr_cascade_01/human_review_queue.jsonl", "er006_output/master_audio_store_01/manifest.json",
                  "er006_output/master_audio_store_01/reuse_telemetry.jsonl")
CTX_MARK = "CONTEXT FOR THIS ONE LINE"

# case -> 既定の注入計画。repetition QA gate の呼出ordinal(clipごとの何回目のASR chain終端か)でNG方向に上書きする。
#   rep: {clip_id: {ordinal,...}}  post: {clip_id: {ordinal,...}}(Adv: 減速後の統一judge再検証の呼出ordinal)
CASE_DEFAULT_PLANS = {
    "E-1": {"path": "normal", "rep": {}, "post": {}},
    "E-2": {"path": "forced_ng_fallback", "rep": {"*": [1, 2]}, "post": {}},          # attempt 1・2を強制NG -> 600秒 -> attempt 3(本物の判定)
    "E-3": {"path": "forced_ng_resume", "rep": {"*": [1, 2]}, "post": {}},           # E-2と同形 + cooldown中に自起動PIDをterminate -> 同一argsで再起動
    "E-4": {"path": "forced_ng_exhaust", "rep": {"*": [1, 2, 3]}, "post": {}},       # 3回すべて強制NG -> STOPPED -> HR Lock
    "E-5": {"path": "forced_ng_first_only", "rep": {"*": [1]}, "post": {}},          # 1回目だけ強制NG -> 2回目(ctx)で即時PASS(待機0) + n=1 NG後kill -> 再開
    "E-6": {"path": "forced_ng_adv_post_slowdown", "rep": {}, "post": {"*": [1]}},   # Adv: n=1が減速後NG -> 外側ループ継続(通算n=2もctx)
}


class DriverError(RuntimeError):
    pass


# ============================================================
# 注入計画 / 記録
# ============================================================
class InjectionPlan:
    def __init__(self, case: str, rep: dict | None = None, post: dict | None = None, path: str | None = None):
        d = CASE_DEFAULT_PLANS[case]
        self.case = case
        self.path = path or d["path"]
        self.rep = {k: {int(x) for x in v} for k, v in (rep if rep is not None else d["rep"]).items()}
        self.post = {k: {int(x) for x in v} for k, v in (post if post is not None else d["post"]).items()}

    @property
    def injects(self) -> bool:
        return bool(self.rep or self.post)

    def wanted(self, kind: str, clip_id: str, ordinal: int) -> bool:
        table = self.rep if kind == "rep" else self.post
        for key in (clip_id, "*"):
            if key in table and ordinal in table[key]:
                return True
        return False


class Recorder:
    def __init__(self):
        self.rep_calls: dict = {}
        self.post_calls: dict = {}
        self.overrides: list = []
        self.requests: list = []
        self.policy_events: list = []
        self.cooldown_slept = 0.0
        self.ordinal_offset = 0     # 再開起動で、前processで消費済みのattempt数(強制NGの呼出ordinalが再開後に1へ戻って再注入されるのを防ぐ。委任_03で追加)
        self.before_exit = None     # 自起動PID終了の直前に呼ぶ(部分evidenceの書出し)


def clip_of(out_path: str) -> str:
    return os.path.splitext(os.path.basename(out_path))[0]


# ============================================================
# patch(module属性を包む。NG方向のみ)
# ============================================================
def make_rep_gate_wrapper(orig, plan: InjectionPlan, rec: Recorder):
    def wrapper(verified, out_path, text, *a, **k):
        res = orig(verified, out_path, text, *a, **k)
        clip = clip_of(out_path)
        rec.rep_calls[clip] = rec.rep_calls.get(clip, rec.ordinal_offset) + 1
        n = rec.rep_calls[clip]
        if plan.wanted("rep", clip, n) and res.get("verified"):      # NG方向のみ(元がNGなら何もしない)
            res = dict(res)
            res["verified"] = False
            ev = dict(res.get("repetition_qa_evidence") or {})
            ev.update({"forced_ng_by_driver": True, "driver_ordinal": n, "driver_case": plan.case})
            res["repetition_qa_evidence"] = ev
            rec.overrides.append({"kind": "rep", "clip": clip, "ordinal": n})
        return res
    return wrapper


def make_post_slowdown_wrapper(orig, plan: InjectionPlan, rec: Recorder):
    def wrapper(name, narration_dir, tts_input, result, *a, **k):
        res = orig(name, narration_dir, tts_input, result, *a, **k)
        clip = str(name)
        rec.post_calls[clip] = rec.post_calls.get(clip, rec.ordinal_offset) + 1
        n = rec.post_calls[clip]
        if plan.wanted("post", clip, n) and isinstance(res, dict) and res.get("status") == "OK":     # NG方向のみ
            res = dict(res)
            res["status"] = "STOPPED"
            res["asr_verified"] = False
            res["reason"] = f"[evidence driver] 減速後再検証を強制NG(NG方向のみ。driver_ordinal={n})"
            rec.overrides.append({"kind": "post", "clip": clip, "ordinal": n})
        return res
    return wrapper


def make_tts_capture_wrapper(orig, rec: Recorder):
    def wrapper(call_fn, prompt, *a, **k):
        seg = None
        try:
            import er005_cost_logger as cl
            seg = cl._CONTEXT.get("segment")
        except Exception:
            pass
        # 駆動中に発見したバグ修正(2026-10-26 委任_03): promptがstr以外(tuple等)で来る経路があり.encodeで落ちた。記録用にstr化する(送信promptは変更しない)。
        ptxt = prompt if isinstance(prompt, str) else repr(prompt)
        rec.requests.append({"clip": seg, "prompt_sha256": hashlib.sha256(ptxt.encode("utf-8")).hexdigest(), "prompt_chars": len(ptxt),
                             "prompt_type": type(prompt).__name__, "has_context": CTX_MARK in ptxt, "t": time.time()})
        return orig(call_fn, prompt, *a, **k)
    return wrapper


def make_kill_wrappers(kill_after_attempt: int | None, kill_in_cooldown_seconds: float | None, rec: Recorder, exit_fn=os._exit):
    """自起動PIDのみterminate(os._exit=SIGKILL相当・cleanupなし)。他processは一切触らない。"""
    import er122_fz_ctx_policy_01 as pol
    patches = []
    if kill_after_attempt is not None:
        orig = pol.DialogueAttemptPolicy.after_attempt

        def after(self, attempt, rows, verified, instruction_type, technical_failure=False):
            r = orig(self, attempt, rows, verified, instruction_type, technical_failure=technical_failure)
            n = self._cur["n"]
            rec.policy_events.append({"event": "after_attempt", "clip": self.clip_id, "n": n, "verified": bool(verified)})
            if n == kill_after_attempt:
                rec.policy_events.append({"event": "SELF_TERMINATE_AFTER_ATTEMPT", "pid": os.getpid(), "n": n})
                if rec.before_exit:
                    rec.before_exit()
                exit_fn(137)
            return r
        patches.append((pol.DialogueAttemptPolicy, "after_attempt", after))
    if kill_in_cooldown_seconds is not None:
        orig_sleep = pol.RUNTIME.sleep

        def sleep(s):
            orig_sleep(s)
            rec.cooldown_slept += s
            if rec.cooldown_slept >= kill_in_cooldown_seconds:
                rec.policy_events.append({"event": "SELF_TERMINATE_IN_COOLDOWN", "pid": os.getpid(), "slept": rec.cooldown_slept})
                if rec.before_exit:
                    rec.before_exit()
                exit_fn(137)
        patches.append((pol.RUNTIME, "sleep", sleep))
    return patches


@contextlib.contextmanager
def install_patches(plan: InjectionPlan, rec: Recorder, *, kill_after_attempt=None, kill_in_cooldown_seconds=None, exit_fn=os._exit):
    """module属性の差替え。終了時に必ず元へ戻す。injects=Falseのplan(E-1)ではrep/post wrapperも入れない(上書き呼出0を構造的に保証)。"""
    import er002_common as common
    import er003_v1_n3_01_tts_generate as n3
    import er011_open121_repetition_qa_production_01 as rq
    targets = [(common, "_call_tts_with_retry", make_tts_capture_wrapper(common._call_tts_with_retry, rec))]
    if plan.rep:
        targets.append((rq, "apply_repetition_qa_gate", make_rep_gate_wrapper(rq.apply_repetition_qa_gate, plan, rec)))
    if plan.post:
        targets.append((n3, "apply_a2_slowdown_postprocess", make_post_slowdown_wrapper(n3.apply_a2_slowdown_postprocess, plan, rec)))
    targets += make_kill_wrappers(kill_after_attempt, kill_in_cooldown_seconds, rec, exit_fn=exit_fn)
    saved = [(o, n, getattr(o, n)) for o, n, _ in targets]
    try:
        for o, n, w in targets:
            setattr(o, n, w)
        yield rec
    finally:
        for o, n, v in saved:
            setattr(o, n, v)


# ============================================================
# 共有台帳 / 観測
# ============================================================
def ledger_snapshot(root: str | None = None) -> dict:
    root = root or ROOT
    snap = {}
    for rel in SHARED_LEDGERS:
        p = os.path.join(root, rel)
        if os.path.exists(p):
            with open(p, "rb") as f:
                data = f.read()
            snap[rel] = {"exists": True, "bytes": len(data), "lines": data.count(b"\n"), "sha256": hashlib.sha256(data).hexdigest()}
        else:
            snap[rel] = {"exists": False, "bytes": 0, "lines": 0, "sha256": None}
    return snap


def ledger_diff(before: dict, after: dict) -> dict:
    return {rel: {"lines_before": before[rel]["lines"], "lines_after": after[rel]["lines"], "added_lines": after[rel]["lines"] - before[rel]["lines"],
                  "changed": before[rel]["sha256"] != after[rel]["sha256"]} for rel in before}


def collect_added_rows(before: dict, run_name: str, root: str | None = None) -> list:
    """共有台帳(jsonl)に今回のrunが追記した行のうち、run名を含む行を『evidence専用・対応不要』候補として識別子つきで返す(Opus R-1)。
    台帳自体は共有のため削除・書換えしない(append-onlyの記録を保つ)。"""
    root = root or ROOT
    out = []
    for rel, b in before.items():
        if not rel.endswith(".jsonl"):
            continue
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8", errors="replace") as f:
            lines = f.read().split("\n")
        for i, ln in enumerate(lines[b["lines"]:], start=b["lines"]):
            if ln.strip() and run_name in ln:
                out.append({"ledger": rel, "line_index": i, "sha256": hashlib.sha256(ln.encode("utf-8")).hexdigest(), "head": ln[:300],
                            "classification": "evidence_only_no_action_required"})
    return out


def assembly_observations(run_dir: str, levels=("a2", "b1b")) -> dict:
    """E-1: 組立のheadroom.scalar / gain_report(観測値の記録。判定には使わない)。"""
    obs = {}
    for lv in levels:
        d = {}
        for name in ("headroom_report", "gain_report"):
            p = f"{run_dir}/{lv}/audit/{name}.json"
            if os.path.exists(p):
                try:
                    with open(p, encoding="utf-8") as f:
                        d[name] = json.load(f)
                except Exception as e:      # noqa: BLE001
                    d[name] = {"error": str(e)}
        if d:
            obs[lv] = d
    return obs


def peak_distribution(narration_dir: str, clip_ids=None) -> dict:
    """ctx音声のpeak分布(観測値。新基準ではない)。check_clip_audio_quality(peak_max=0.999)の既存条件との比較用。"""
    out = {}
    try:
        import soundfile as sf
        import numpy as np
    except Exception as e:      # noqa: BLE001
        return {"error": f"{e.__class__.__name__}: {e}"}
    if not os.path.isdir(narration_dir):
        return out
    for fn in sorted(os.listdir(narration_dir)):
        if not fn.endswith(".wav") or fn.endswith("_original.wav"):
            continue
        cid = fn[:-4]
        if clip_ids and cid not in clip_ids:
            continue
        x, _sr = sf.read(os.path.join(narration_dir, fn))
        out[cid] = round(float(np.max(np.abs(x))) if len(x) else 0.0, 5)
    return out


# ============================================================
# 起動
# ============================================================
def stop_scope_check(run_dir: str, out_path: str) -> int:
    """有料run開始前の必須確認(PM_GOVERNANCE 26節)。rc=3なら新規API呼出をせず停止。"""
    r = subprocess.run([sys.executable, "tools/stop_scope_check_01.py", "--managed-id", MANAGEMENT_ID, "--run-dir", run_dir, "--out", out_path],
                       cwd=ROOT, capture_output=True, text=True)
    return r.returncode


def build_runner_argv(args) -> list:
    stages = args.stages
    for st in [x.strip() for x in stages.split(",")]:
        if st in FORBIDDEN_STAGES:
            raise DriverError(f"公開page出力stage({st})はevidence driverでは実行しません")
    argv = ["--mode", "real", "--story", args.work, "--slug", args.work, "--run", args.run, "--stages", stages,
            "--approved-budget-jpy", str(args.budget_jpy), "--tts-execution-mode", "STANDARD",
            "--pages-dir", f"{E2E_RUN_ROOT}/{args.work}/{args.run}/pages_evidence_unpublished"]       # 公開dirへ出さない(念のため分離)
    if args.only_clips:
        argv += ["--only-clips", args.only_clips]
    return argv


def default_stages(case: str, level: str | None) -> str:
    if case == "E-1":
        return "tts_b1b,tts_a2,provision_shell,gate,assemble"
    return "tts_b1b" if level == "b1b" else "tts_a2"


def run_case(args, *, runner_main=None, exit_fn=os._exit, stop_check=stop_scope_check) -> dict:
    """1起動。evidence dictを返す(JSONも書く)。runner_mainはtest用に差し替え可。"""
    plan = InjectionPlan(args.case, path=args.path)
    if args.case == "E-1" and plan.injects:
        raise DriverError("E-1(正常経路)は注入計画が空でなければなりません")
    run_dir = f"{E2E_RUN_ROOT}/{args.work}/{args.run}"
    os.makedirs(run_dir, exist_ok=True)
    rc_stop = stop_check(run_dir, f"{EVIDENCE_DIR}/stop_scope_check_{args.case}_{args.run}.json")
    if rc_stop == 3:
        raise DriverError("STOP通知が適用されます(rc=3)。新規API呼出をしません")
    if not args.stages:
        args.stages = default_stages(args.case, args.level)
    argv = build_runner_argv(args)
    with open(f"{run_dir}/_driver_pid.json", "a", encoding="utf-8") as f:       # 自起動PIDの記録(終了は自PIDのみ)
        f.write(json.dumps({"pid": os.getpid(), "case": args.case, "argv": argv, "started_at": time.strftime("%Y-%m-%dT%H:%M:%S")}) + "\n")
    before = ledger_snapshot()
    rec = Recorder()
    rec.ordinal_offset = int(getattr(args, "ordinal_offset", 0) or 0)
    out = args.evidence_out or f"{EVIDENCE_DIR}/RUNTIME_EVIDENCE_{args.case}_{args.run}.json"

    def write_partial():
        part = {"management_id": MANAGEMENT_ID, "case": args.case, "partial_before_self_terminate": True, "pid": os.getpid(),
                "injected_overrides": rec.overrides, "rep_gate_calls": rec.rep_calls, "post_slowdown_calls": rec.post_calls,
                "tts_requests": rec.requests, "policy_events": rec.policy_events, "shared_ledgers": ledger_diff(before, ledger_snapshot()),
                "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
        pp = os.path.join(ROOT, out.replace(".json", f".partial_{int(time.time())}.json"))
        os.makedirs(os.path.dirname(pp) or ".", exist_ok=True)
        with open(pp, "w", encoding="utf-8") as f:
            json.dump(part, f, ensure_ascii=False, indent=1, default=str)
    rec.before_exit = write_partial
    if runner_main is None:
        import er026_family_z_fiction_production_runner_01 as runner
        runner_main = runner.main
    with install_patches(plan, rec, kill_after_attempt=args.kill_after_attempt, kill_in_cooldown_seconds=args.kill_in_cooldown, exit_fn=exit_fn):
        rc = runner_main(argv)
    after = ledger_snapshot()
    ev = {"management_id": MANAGEMENT_ID, "case": args.case, "path": plan.path, "forced_ng_injection": bool(rec.overrides),
          "injection_plan": {"rep": {k: sorted(v) for k, v in plan.rep.items()}, "post": {k: sorted(v) for k, v in plan.post.items()}},
          "injected_overrides": rec.overrides, "injected_override_count": len(rec.overrides), "ordinal_offset": rec.ordinal_offset,
          "rep_gate_calls": rec.rep_calls, "post_slowdown_calls": rec.post_calls,
          "runner_rc": rc, "run_dir": run_dir, "argv": argv, "pid": os.getpid(), "tts_requests": rec.requests,
          "tts_requests_with_context": sum(1 for r in rec.requests if r["has_context"]), "tts_requests_total": len(rec.requests),
          "policy_events": rec.policy_events, "shared_ledgers": ledger_diff(before, after),
          "evidence_only_rows": collect_added_rows(before, args.run) if plan.injects else [],
          "assembly_observations": assembly_observations(run_dir) if args.case == "E-1" else None,
          "ledger_invalidation": ("forced run由来のHR queue行・attempt_history行は『evidence専用・対応不要』(台帳で無効化)。費用は開発費に計上" if plan.injects else None),
          "peak_distribution_observation": peak_distribution(f"{run_dir}/{args.level}/narration") if args.level else None,
          "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    if args.case == "E-1":
        assert ev["injected_override_count"] == 0 and ev["forced_ng_injection"] is False, "E-1で上書きが発生した"
    os.makedirs(os.path.dirname(os.path.join(ROOT, out)) or ".", exist_ok=True)
    with open(os.path.join(ROOT, out), "w", encoding="utf-8") as f:
        json.dump(ev, f, ensure_ascii=False, indent=1, default=str)
    return ev


def build_parser():
    ap = argparse.ArgumentParser(description="FZCW Phase 2 runtime evidence driver(正式runner main()を同一processで起動、Gate出力をNG方向のみ上書き)")
    ap.add_argument("--case", required=True, choices=sorted(CASE_DEFAULT_PLANS))
    ap.add_argument("--work", required=True, help="story key(例 the_monkeys_paw / melos)")
    ap.add_argument("--level", default=None, choices=("a2", "b1b"), help="E-2〜E-6のlevel(E-1は両level)")
    ap.add_argument("--run", required=True, help="専用run dir名(公開dir・既存完成版runとは別)")
    ap.add_argument("--budget-jpy", type=float, required=True, help="runnerの--approved-budget-jpy")
    ap.add_argument("--only-clips", default=None)
    ap.add_argument("--stages", default=None)
    ap.add_argument("--path", default=None, help="evidence JSONのpath記録値の上書き(既定=caseの既定値)")
    ap.add_argument("--kill-after-attempt", type=int, default=None, help="attempt Nのstate永続化直後に自起動PIDをos._exit(137)で終了(E-5)")
    ap.add_argument("--kill-in-cooldown", type=float, default=None, help="cooldownの累積待機がS秒に達したら自起動PIDを終了(E-3)")
    ap.add_argument("--ordinal-offset", type=int, default=0, help="再開起動用: 前processで消費済みのattempt数。強制NGの呼出ordinalをこの値から数える(再開後に再注入しない)")
    ap.add_argument("--evidence-out", default=None)
    return ap


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if os.environ.get("TTS_EXECUTION_MODE") not in (None, "STANDARD"):
        print("[STOP] TTS_EXECUTION_MODE=STANDARD を明示してください(T-2)", file=sys.stderr)
        return 2
    if args.case != "E-1" and not args.level:
        print("[STOP] E-2〜E-6は --level が必要です", file=sys.stderr)
        return 2
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    try:
        ev = run_case(args)
    except DriverError as e:
        print(f"[STOP] {e}", file=sys.stderr)
        return 3
    print(json.dumps({k: ev[k] for k in ("case", "path", "forced_ng_injection", "injected_override_count", "runner_rc", "tts_requests_total",
                                         "tts_requests_with_context")}, ensure_ascii=False))
    return int(ev["runner_rc"] or 0)


if __name__ == "__main__":
    sys.exit(main())
