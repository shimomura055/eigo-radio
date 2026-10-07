# -*- coding: utf-8 -*-
"""ALL-6-LUNA-WRITER-REDESIGN-NECESSITY-TRIAL-01: Trial harness(Production経路ではない)。

薄い起動ラッパ。er052_open233_polysemy_nb_dev_01(DEV runner)を同一processで呼び、
--arm all6 のときだけ「現在gpt-5.6-lunaを使う工程」をgpt-6-lunaへmonkeypatchする(Production codeは無編集)。
  - JA Writer R0/R1/R2/must-fix : er019_family_x_ja_writer_o_r1_r2_01.WRITER_MODEL
  - JA/EN Fact Check            : er003_v1_en_direct_vfl_01_generate.run_deviation_check の既定model
  - EN(Advanced faithful translation / In one line): er003_v1_n3_01_advanced_adaptation_generate.generate_family_x_*
  - Checker(run_checker_after_p01.py)は別processでrunner.MODEL(=gpt-6-luna)を使う=両armで同一(本harnessは触れない)。
baselineは無変更。require_model_or_override(process, model, override_reason=...)経由でmodelを決める。
"""
from __future__ import annotations

import argparse
import functools
import glob
import hashlib
import json
import os
import sys
import time

TRIAL_ID = "ALL-6-LUNA-WRITER-REDESIGN-NECESSITY-TRIAL-01"
ALL6_MODEL = "gpt-6-luna"
BASE_ROOT = "er052_output/all6_writer_redesign_necessity_01"
RUNS_ROOT = f"{BASE_ROOT}/runs"


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sha256_file(path):
    if not path or not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _routing():
    import er006_model_routing_contract_01 as routing
    return routing


def resolve_all6_model(process: str) -> str:
    return _routing().require_model_or_override(process, ALL6_MODEL, override_reason=TRIAL_ID)


def apply_all6_patches(mods: dict | None = None) -> dict:
    """all6の差替えを適用し、元へ戻すための辞書を返す。modsはtest用に差替え可能。"""
    if mods is None:
        import er003_v1_en_direct_vfl_01_generate as vfl01
        import er003_v1_n3_01_advanced_adaptation_generate as adv_gen
        import er019_family_x_ja_writer_o_r1_r2_01 as jaw
        mods = {"vfl01": vfl01, "adv_gen": adv_gen, "jaw": jaw}
    vfl01, adv_gen, jaw = mods["vfl01"], mods["adv_gen"], mods["jaw"]
    saved = {
        "jaw.WRITER_MODEL": jaw.WRITER_MODEL,
        "vfl01.run_deviation_check": vfl01.run_deviation_check,
        "adv_gen.generate_family_x_faithful_translation": adv_gen.generate_family_x_faithful_translation,
        "adv_gen.generate_family_x_in_one_line": adv_gen.generate_family_x_in_one_line,
    }
    jaw.WRITER_MODEL = resolve_all6_model("B1_WRITER")
    fc_model = resolve_all6_model("WRITER_FACT_CHECK")
    en_model = resolve_all6_model("A2_WRITER")
    orig_dev = saved["vfl01.run_deviation_check"]

    @functools.wraps(orig_dev)
    def dev_check(client, verified_ledger_text, article_text, model=None, *a, **k):
        return orig_dev(client, verified_ledger_text, article_text, model or fc_model, *a, **k)

    orig_tr = saved["adv_gen.generate_family_x_faithful_translation"]
    orig_iol = saved["adv_gen.generate_family_x_in_one_line"]

    @functools.wraps(orig_tr)
    def tr(ja_text, *a, model=None, **k):
        return orig_tr(ja_text, *a, model=model or en_model, **k)

    @functools.wraps(orig_iol)
    def iol(client, title, body, *a, model=None, **k):
        return orig_iol(client, title, body, *a, model=model or en_model, **k)

    vfl01.run_deviation_check = dev_check
    adv_gen.generate_family_x_faithful_translation = tr
    adv_gen.generate_family_x_in_one_line = iol
    saved["_mods"] = mods
    return saved


def restore_patches(saved: dict) -> None:
    mods = saved["_mods"]
    mods["jaw"].WRITER_MODEL = saved["jaw.WRITER_MODEL"]
    mods["vfl01"].run_deviation_check = saved["vfl01.run_deviation_check"]
    mods["adv_gen"].generate_family_x_faithful_translation = saved["adv_gen.generate_family_x_faithful_translation"]
    mods["adv_gen"].generate_family_x_in_one_line = saved["adv_gen.generate_family_x_in_one_line"]


def collect_models(out_dir: str) -> dict:
    """raw_usage_log.jsonl(APIレスポンスのmodel)からstage別の実使用model_idを集計する。"""
    res = {}
    p = f"{out_dir}/raw_usage_log.jsonl"
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            st = rec.get("stage") or "UNTAGGED"
            res.setdefault(st, set()).add(rec.get("model_id"))
    models = {k: sorted(x for x in v if x) for k, v in res.items()}
    chk = set()
    for f in glob.glob(f"{out_dir}/checker/**/*.json", recursive=True):
        try:
            txt = open(f, encoding="utf-8").read()
        except OSError:
            continue
        for m in ("gpt-6-luna", "gpt-5.6-luna", "gpt-5.6-sol"):
            if f'"{m}"' in txt:
                chk.add(m)
    models["_checker_models_seen"] = sorted(chk)
    return models


def checker_summary(out_dir: str) -> dict:
    s = {"present": False}
    for f in glob.glob(f"{out_dir}/checker/runs/*.json"):
        try:
            r = json.load(open(f, encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        s = {"present": True, "file": f, "final_state": r.get("final_state"), "run_cost_jpy": r.get("run_cost_jpy")}
    d = f"{out_dir}/checker/approved_switches_dump_after_p01.json"
    s["switch_dump_sha256"] = sha256_file(d)
    if os.path.exists(d):
        try:
            s["switches"] = json.load(open(d, encoding="utf-8")).get("switches")
        except Exception:  # noqa: BLE001
            pass
    return s


def build_parser():
    p = argparse.ArgumentParser()
    p.add_argument("--arm", choices=("baseline", "all6"), required=True)
    p.add_argument("--slug", required=True)
    p.add_argument("--brief-md", required=True)
    p.add_argument("--ledger-txt", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--budget-jpy", type=float, default=12.0)
    p.add_argument("--theme-file", default=None)
    p.add_argument("--checker-budget-jpy", type=float, default=10.0)
    p.add_argument("--yes-run-paid", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    return p


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    theme_file = args.theme_file or os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(args.ledger_txt))), "topic.txt")
    theme = open(theme_file, encoding="utf-8").read().strip()
    os.environ["OPEN233_RUNS_ROOT"] = RUNS_ROOT
    os.environ.pop("OPEN233_B3_VARIANT", None)   # 未設定=control(briefは--brief-mdで固定、B3は実行されない)
    import er052_open233_polysemy_nb_dev_01 as dev
    import er019_family_x_ja_writer_o_r1_r2_01 as jaw
    import er003_v1_en_direct_vfl_01_generate as vfl01

    manifest = {
        "trial_id": TRIAL_ID, "arm": args.arm, "slug": args.slug, "out_dir": args.out_dir,
        "brief_md": args.brief_md, "brief_sha256": sha256_file(args.brief_md),
        "ledger_sha256": sha256_file(args.ledger_txt),
        "prompt_sha256": {"R0_PROMPT": sha256_text(jaw.R0_PROMPT), "DEVELOPER_MESSAGE": sha256_text(jaw.DEVELOPER_MESSAGE),
                          "DEVIATION_DEVELOPER_MESSAGE": sha256_text(vfl01.DEVIATION_DEVELOPER_MESSAGE)},
        "reasoning_effort": vfl01.REASONING_EFFORT,
        "checker_enabled": True, "budget_jpy": args.budget_jpy, "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "all6_model": ALL6_MODEL if args.arm == "all6" else None,
        "phases": [],
    }
    if args.dry_run or not args.yes_run_paid:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0 if args.dry_run else 2

    saved = apply_all6_patches() if args.arm == "all6" else None
    t0 = time.time()
    rc = 0
    exit_reason = "completed"
    try:
        common = ["--theme", theme, "--slug", args.slug, "--ledger-txt", args.ledger_txt, "--out-dir", args.out_dir,
                  "--yes-run-paid"]
        for phase in ("phase1", "phase2"):
            argv2 = common + ["--phase", phase, "--budget-jpy", str(args.budget_jpy)]
            if phase == "phase1":
                argv2 += ["--brief-md", args.brief_md]
            else:
                argv2 += ["--checker-budget-jpy", str(args.checker_budget_jpy)]
            ts = time.time()
            try:
                prc = dev.main(argv2)
                manifest["phases"].append({"phase": phase, "rc": prc, "sec": round(time.time() - ts, 1)})
                if prc not in (0, None):
                    rc = prc if isinstance(prc, int) else 1
                    exit_reason = f"{phase}_rc={prc}"
                    break
            except SystemExit as e:
                manifest["phases"].append({"phase": phase, "rc": f"SystemExit:{e}", "sec": round(time.time() - ts, 1)})
                rc, exit_reason = 1, f"{phase}_SystemExit: {e}"
                break
            except Exception as e:  # noqa: BLE001
                manifest["phases"].append({"phase": phase, "rc": f"error:{e!r}", "sec": round(time.time() - ts, 1)})
                rc, exit_reason = 1, f"{phase}_error: {e!r}"
                break
    finally:
        if saved is not None:
            restore_patches(saved)
        manifest["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        manifest["wall_sec"] = round(time.time() - t0, 1)
        manifest["exit_reason"] = exit_reason
        manifest["model_ids_actual"] = collect_models(args.out_dir)
        manifest["checker"] = checker_summary(args.out_dir)
        cj = f"{args.out_dir}/cost.json"
        manifest["cost"] = json.load(open(cj, encoding="utf-8")) if os.path.exists(cj) else None
        os.makedirs(args.out_dir, exist_ok=True)
        with open(f"{args.out_dir}/manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
    return rc


if __name__ == "__main__":
    sys.exit(main())
