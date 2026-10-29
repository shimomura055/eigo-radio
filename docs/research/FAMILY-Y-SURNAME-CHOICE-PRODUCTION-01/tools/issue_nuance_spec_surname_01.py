# -*- coding: utf-8 -*-
"""使い捨てtool D(FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01 委任_05。由来=ユーザー原文USER_03 §3)。

目的: 制作時期(KP review作成=2026-10-29 11:54、ニュアンス解説runner配線commit 1f7bf405a=13:18)の関係でLEGACY(nuance_spec.json無し)になっている
Family Y「夫が妻の姓を選ぶとき」run_02のStd(a2)・Adv(b1b)に、ユーザーの明示指示(USER_03 §3)に基づいてニュアンス解説の仕様マーク(nuance_spec.json)を発行し、
**既存の正式経路**(runnerの `_nuance_cand_step` = er134.n1_stage: 候補生成v3.1・構造検査・KP/Word重複判定[提示前除外]・QA)で候補を生成する。
新しい対象条件・Prompt・閾値・Gateは作らない(呼出順だけ: ensure_spec[new_review=True] -> runner._nuance_cand_step)。**確定はしない**(採否はHuman Review。ユーザー選定が必要)。
`er128 cmd_nuance_issue_spec` はcopy-run限定(実運用runへ遡及させない設計)のため使えない。本toolは『ユーザーが本記事への適用を明示した』場合の単発の例外手順であり、
一般経路(既存run=LEGACY)の挙動は変更しない。run_02・slug=surname_choice・level=b1b/a2に固定(他記事・他runは拒否)。
HR提示物: study dirへ `nuance_request.md`(er134.render_request_md)、run_02/hr/へ nuance_show_<lv>.json を書く。
実行: .venv\\Scripts\\python.exe docs\\research\\FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01\\tools\\issue_nuance_spec_surname_01.py apply|dry-run --by <名> [--rehearsal-dir <root>] --budget-jpy <円>
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import apply_user_decision_surname_choice_02 as T2  # noqa: E402  (build_real_ctx)
import apply_v1_intro_patch_01 as A  # noqa: E402

TOOL_ID = "issue_nuance_spec_surname_01"
LEVELS = ("b1b", "a2")
USER_REF = "docs/pm/delegation_log/2026-10-29_FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01_USER_03.md"
USER_REF_SHA256 = "30fd4011ca6d6f7a131025e5497f03c7f2193ea132c8c59982ac2da3cbffd5ab"


class ToolRefused(Exception):
    pass


def _sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("apply", "dry-run"))
    ap.add_argument("--by", required=True)
    ap.add_argument("--rehearsal-dir", default=None)
    ap.add_argument("--budget-jpy", type=float, default=3.0)
    ap.add_argument("--report", default=None)
    a = ap.parse_args(argv)
    run_dir = A.run_dir_of(a.rehearsal_dir)
    report = {"tool": TOOL_ID, "cmd": a.cmd, "run_dir": run_dir, "rehearsal": bool(a.rehearsal_dir), "at": _now()}
    lock_taken, st, created = False, None, []
    try:
        if not os.path.isdir(run_dir):
            raise ToolRefused(f"run dirがありません: {run_dir}")
        if _sha_bytes(open(USER_REF, "rb").read()) != USER_REF_SHA256:
            raise ToolRefused("ユーザー原文(USER_03)のfile shaが定数と一致しません")
        import er119_kp_human_review_01 as rv
        import er134_nuance_explanation_01 as nx
        cc = rv._cc()
        with A._quiet():
            R0, ctx0 = A.build_ctx(a.rehearsal_dir)
        st = R0._m().st
        st.check_stop_sentinel("tool:start", run_dir)
        pre = {}
        for lv in LEVELS:
            kp_dir, sd = R0._kp_src_dir(ctx0, lv), R0._part2_dir(ctx0, lv)
            review, cands = rv.load_review(kp_dir), rv.load_candidates(kp_dir)
            if review is None or cands is None or review.get("status") != rv.ST_REVIEWED:
                raise ToolRefused(f"{lv}: KP review/候補docが確定済み(REVIEWED)ではありません")
            if cc.live_user_record(kp_dir) is None:
                raise ToolRefused(f"{lv}: ユーザー確定のKPレコード(live)がありません。ニュアンス解説の重複判定は確定①②に対して行うため、KP確定後に実行します")
            sf = nx.study_files(sd)
            pre[lv] = {"study_dir": sd, "spec_exists": os.path.exists(sf["spec"]), "candidate_exists": os.path.exists(sf["candidate"]),
                       "nuance_decided": cc.nuance_state(sd) is not None}
            if pre[lv]["nuance_decided"]:
                raise ToolRefused(f"{lv}: 既にニュアンス解説の採否が確定しています")
        report["pre"] = pre
        if a.cmd == "dry-run":
            report["result"] = "DRY_RUN_OK(LLM 0・何も書いていません)"
            print(json.dumps(report, ensure_ascii=False, indent=1, default=str))
            return 0
        st.acquire_run_lock(run_dir, sys.argv)
        lock_taken = True
        R, ctx, spend = T2.build_real_ctx(a.rehearsal_dir, a.budget_jpy)
        report["budget_cap_jpy"] = a.budget_jpy
        hr_dir = os.path.join(run_dir, "hr")
        os.makedirs(hr_dir, exist_ok=True)
        out = {}
        for lv in LEVELS:
            sd = R._part2_dir(ctx, lv)
            sf = nx.study_files(sd)
            before = {k: os.path.exists(p) for k, p in sf.items()}
            sp = nx.ensure_spec(sd, level=lv, new_review=True, issuer=f"user_instruction_USER_03_s3:{a.by}")
            if sp["issued_now"]:
                created.append(sf["spec"])
            # 既存の正式経路(runner)の関数。review_existed=True=『spec発行は済んでいる』として通常のN1(候補生成・重複判定)だけを走らせる
            nz = R._nuance_cand_step(ctx, lv, True)
            for k, p in sf.items():
                if os.path.exists(p) and not before[k]:
                    created.append(p)
            doc = json.load(open(sf["candidate"], encoding="utf-8")) if os.path.exists(sf["candidate"]) else None
            o = {"spec": sp["state"], "spec_issued_now": sp["issued_now"], "n1": {k: nz.get(k) for k in ("state", "status", "api_calls", "cost_jpy", "reused")},
                 "candidate_status": (doc or {}).get("status"), "no_candidate_reason": (doc or {}).get("no_candidate_reason"),
                 "failed_technical": (doc or {}).get("failed_technical")}
            if doc and doc.get("status") == nx.ST_CANDIDATE:
                c = doc["candidate"]
                o["candidate"] = {k: c.get(k) for k in ("expression", "focus", "explanation_ja", "quote_en", "quote_ja", "candidate_sha256", "pool_conflicts", "grammar_conflicts")}
                o["overlap_check"] = {"verdict": (c.get("overlap_check") or {}).get("verdict"), "reason": (c.get("overlap_check") or {}).get("reason")}
                req = nz.get("pending") or {}
                o["request_md"] = req.get("request_md")
                o["usage"] = doc.get("usage")
            show = cc.cmd_nuance_show(run_dir, lv)
            with open(os.path.join(hr_dir, f"nuance_show_{lv}.json"), "w", encoding="utf-8", newline="\n") as f:
                json.dump(show, f, ensure_ascii=False, indent=1)
            o["nuance_show"] = show
            out[lv] = o
        report["levels"] = out
        report["spent_jpy"] = spend.used()
        report["created_files"] = [p.replace("\\", "/") for p in created]
        report["result"] = "APPLIED(候補生成のみ。採否は未確定=ユーザー選定待ち)"
        if a.report:
            with open(a.report, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=1, default=str)
        print(json.dumps(report, ensure_ascii=False, indent=1, default=str))
        return 0
    except BaseException as e:   # noqa: BLE001  失敗=このtoolが新規作成したnuance_*だけ削除(費用は戻らない)
        for p in created:
            try:
                os.remove(p)
            except OSError:
                pass
        kind = "REFUSED" if isinstance(e, ToolRefused) else "FAILED"
        print(f"[{TOOL_ID}][{kind}] {e.__class__.__name__}: {e}  (removed_new_files={len(created)})", file=sys.stderr)
        if isinstance(e, (KeyboardInterrupt, SystemExit)):
            raise
        return 2
    finally:
        if lock_taken and st is not None:
            st.release_run_lock(run_dir)


if __name__ == "__main__":
    sys.exit(main())
