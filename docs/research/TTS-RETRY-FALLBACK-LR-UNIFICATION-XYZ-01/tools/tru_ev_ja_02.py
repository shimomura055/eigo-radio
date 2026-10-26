# -*- coding: utf-8 -*-
"""TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_05: JA終端NG→HRQ1行の実経路evidence driver(1case: JA_02)。
判定戻り値の注入ではなく、Primary(routing.transcribe[ja-JP])とSecondary(er007._azure_stt_strict)の転写に1語置換を入れ、
JA判定器自身にNG(TRUE_CONTENT_MISMATCH)を出させる(委任_03のX-Std-7[judge戻り値注入]との差分)。Production無改変(driver monkeypatchのみ、終了時に復元)。
使い方: TTS_EXECUTION_MODE=STANDARD py docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/tools/tru_ev_ja_02.py --tts-execution-mode STANDARD --budget-jpy 3
"""
from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import tru_ev_core_01 as core  # noqa: E402
import tru_ev_run_01 as run  # noqa: E402
from tru_ev_core_01 import Plan  # noqa: E402

_RUN = re.compile(r"[一-龥ァ-ヶー]{2,}")


def ja_substitute(text: str) -> str:
    """最長の漢字/カタカナ連続を別語へ置換(ASRが別語を聞いた状況の再現。NG方向のみ)。"""
    runs = _RUN.findall(text or "")
    if not runs:
        return text
    target = max(runs, key=len)
    rep = "天気予報" if target != "天気予報" else "新聞記事"
    return text.replace(target, rep, 1)


CASE = {"id": "JA_02", "group": "X-Std", "family": "X", "level": "a2", "scenario": "E-S3(JA転写置換)", "leaf": "L7", "policy": "JA_STD",
        "segments": ["japanese_title"], "plan": Plan(), "root": run.X_ROOT, "theme_prefix": "coffee_prices"}

OBS = {"register_terminal_hr": [], "register_ja_terminal_hr": [], "log_human_review": [], "subs": []}


def _count(p):
    return len(core.read_jsonl(p))


def _wrap_installed(orig_installed):
    @contextlib.contextmanager
    def installed(plan, rec, iso_dir, *, cost_log):
        with orig_installed(plan, rec, iso_dir, cost_log=cost_log) as r:
            import er006_asr_provider_routing_01 as routing
            import er006_secondary_asr_01 as sec
            import er007_ja_secondary_asr_01 as jasec
            import er127_tts_block_policy_01 as er127
            saved = []

            def patch(obj, name, new):
                saved.append((obj, name, getattr(obj, name)))
                setattr(obj, name, new)

            o_tr = routing.transcribe

            def tr(path, *a, **k):
                res = o_tr(path, *a, **k)
                lang = k.get("language") or (a[0] if a else "")
                if str(lang).lower().startswith("ja") and isinstance(res, tuple) and res and res[0]:
                    new = ja_substitute(res[0])
                    OBS["subs"].append({"engine": "primary", "clip": core.clip_of(path), "before": res[0], "after": new})
                    r.overrides.append({"kind": "transcript_substitution_primary", "clip": core.clip_of(path), "before": res[0], "after": new})
                    res = (new,) + tuple(res[1:])
                return res
            patch(routing, "transcribe", tr)

            o_az = jasec._azure_stt_strict

            def az(wav, *a, **k):
                res = o_az(wav, *a, **k)
                if isinstance(res, tuple) and res and res[0] and str(res[0]).strip():
                    new = ja_substitute(res[0])
                    OBS["subs"].append({"engine": "secondary_azure", "clip": core.clip_of(wav), "before": res[0], "after": new})
                    r.overrides.append({"kind": "transcript_substitution_secondary", "clip": core.clip_of(wav), "before": res[0], "after": new})
                    res = (new,) + tuple(res[1:])
                return res
            patch(jasec, "_azure_stt_strict", az)

            # 観測のみ(挙動不変): どの経路がHRQへ書いたか
            ctx = {"in_register": False, "in_ja_register": False}
            o_rth = er127.register_terminal_hr

            def rth(**kw):
                ctx["in_register"] = True
                try:
                    ret = o_rth(**kw)
                finally:
                    ctx["in_register"] = False
                OBS["register_terminal_hr"].append({"wav": kw.get("out_path"), "returned": ret, "via_register_ja": ctx["in_ja_register"]})
                return ret
            patch(er127, "register_terminal_hr", rth)

            o_rjh = er127.register_ja_terminal_hr

            def rjh(blk, text, out_path, last_attempt):
                ctx["in_ja_register"] = True
                try:
                    ret = o_rjh(blk, text, out_path, last_attempt)
                finally:
                    ctx["in_ja_register"] = False
                OBS["register_ja_terminal_hr"].append({"out_path": out_path, "returned": ret, "blk_depth": getattr(blk, "depth", None),
                                                       "last_attempt_status": (last_attempt or {}).get("status"),
                                                       "last_attempt_verified": (last_attempt or {}).get("verified")})
                return ret
            patch(er127, "register_ja_terminal_hr", rjh)

            def mk(mod, label, path_fn):
                o = mod._log_human_review

                def lg(detail):
                    before = _count(path_fn())
                    o(detail)
                    after = _count(path_fn())
                    OBS["log_human_review"].append({"target": label, "called_from_register_terminal_hr": ctx["in_register"],
                                                    "via_register_ja": ctx["in_ja_register"], "wav": detail.get("wav_path"),
                                                    "rows_before": before, "rows_after": after, "wrote_row": after > before})
                return lg
            patch(jasec, "_log_human_review", mk(jasec, "ja_queue(HUMAN_REVIEW_LOG_PATH_JA)", lambda: jasec.HUMAN_REVIEW_LOG_PATH_JA))
            patch(sec, "_log_human_review", mk(sec, "en_queue(HUMAN_REVIEW_LOG_PATH)", lambda: sec.HUMAN_REVIEW_LOG_PATH))
            try:
                yield r
            finally:
                for obj, name, val in reversed(saved):
                    setattr(obj, name, val)
    return installed


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget-jpy", type=float, required=True)
    ap.add_argument("--tts-execution-mode", required=True)
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args(argv)
    if args.tts_execution_mode != "STANDARD" or os.environ.get("TTS_EXECUTION_MODE") != "STANDARD":
        print("[STOP] TTS_EXECUTION_MODE=STANDARD を環境変数とCLI引数の両方で明示してください(T-2)", file=sys.stderr)
        return 2
    core.installed = _wrap_installed(core.installed)
    a = argparse.Namespace(dry=args.dry, resume=False, kill_in_cooldown=None)
    ev = run.run_case(CASE, budget_left=args.budget_jpy, args=a)
    if isinstance(ev, dict) and not ev.get("dry") and not ev.get("stopped_by_scope_check"):
        ev["driver_observation"] = OBS
        out = f"{core.EVIDENCE_RUNS}/JA_02.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(ev, f, ensure_ascii=False, indent=1, default=str)
        print(f"[JA_02] tts={ev.get('tts_attempts_count')} cd={ev.get('cooldown_count')} lr={ev.get('lr_count')} hrq={ev.get('hrq_rows')} "
              f"jpy={(ev.get('cost') or {}).get('jpy')} exc={(ev.get('exception') or {}).get('type')}")
    else:
        print(json.dumps(ev, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
