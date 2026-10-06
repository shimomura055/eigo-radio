# -*- coding: utf-8 -*-
"""OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-02 委任_P0c: 案N+B用DEV専用ラッパ(Production経路ではない)。

- import時は何もしない。main()内のcontextmanagerでのみ b3.build_user_prompt を「元+転記規則ブロック」へ差替、終了時(例外時含む)復元。
- env OPEN233_B3_VARIANT: 未設定/control=差替なし、nb=差替、他=ValueError。
- 固定台帳(--ledger-txt)を out_dir/research_ledger/verified_fact_ledger.txt へコピーし、er019 runnerの既存txt再利用により
  Researcher/Verificationは実行されない(実行後 raw_usage_log に research/ledger段callが無いことをassert)。
- phase1: --stage advanced --stop-after writer(B3 brief+JA R0/R1/R2まで、EN前で停止)。
- phase2: 同out_dirで --stage advanced --stop-after advanced(brief/R2再利用でENのみ)後、run_checker_after_p01.py を呼ぶ。
- 有料APIは --yes-run-paid 指定時のみ。--dry-run は¥0。
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

ENV_NAME = "OPEN233_B3_VARIANT"
VARIANTS = ("control", "nb")
SEP = "\n\n"
FREEZE_PATH = "er052_output/open233_ledger_polysemy_note_01/phase0/FREEZE_T01_CONFIG.json"
CHECKER_TOOL = "er052_output/open233_ledger_clarity_p_trial_01/tools/run_checker_after_p01.py"
DEFAULT_RUNS_ROOT = "er052_output/open233_polysemy_trial_02/runs"
RUNS_ROOT_ENV = "OPEN233_RUNS_ROOT"
RUNS_ROOT = DEFAULT_RUNS_ROOT  # 後方互換(既定値)。実際の検証は get_runs_root() を使う


def get_runs_root() -> str:
    return (os.environ.get(RUNS_ROOT_ENV) or DEFAULT_RUNS_ROOT).replace("\\", "/").rstrip("/")
PHASE_DEFAULT_BUDGET = {"phase1": 12.0, "phase2": 10.0}

PREFIX_ENV = "OPEN233_NOTE_PREFIX"
DEFAULT_NOTE_PREFIX = "注意(多義):"
_TRANSFER_TEMPLATE = (
    "【多義語注意の引き継ぎ規則】\n"
    "台帳のnotes_for_writerに『{prefix}』で始まる注意がある場合、そのfactをbriefで使うときは、"
    "その注意文を意味を変えずそのままbriefの該当箇所の直後に1行で引き継ぐ"
    "(要約・言い換え・新しい解釈の追加・削除をしない)。注意のないfactには何も足さない。"
)


def build_transfer_block(env=None) -> str:
    """接頭辞は環境変数OPEN233_NOTE_PREFIX(既定『注意(多義):』)で差し替え可能。"""
    env = os.environ if env is None else env
    return _TRANSFER_TEMPLATE.format(prefix=env.get(PREFIX_ENV) or DEFAULT_NOTE_PREFIX)


TRANSFER_BLOCK = build_transfer_block({})


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sha256_file(path: str):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def resolve_variant(env=None) -> str:
    env = os.environ if env is None else env
    v = env.get(ENV_NAME)
    if v is None:
        return "control"
    if v not in VARIANTS:
        raise ValueError(f"{ENV_NAME}={v!r} は不正(許可: {VARIANTS}、未設定=control)")
    return v


def append_block(base: str) -> str:
    return base + SEP + build_transfer_block()


@contextlib.contextmanager
def patched_b3(variant: str, b3_module=None, sent_log=None):
    """variant=nbの間だけ b3.build_user_prompt を差替。終了時(例外含む)に必ず元へ戻す。controlは差替なし(記録のみ)。"""
    if variant not in VARIANTS:
        raise ValueError(f"variant不正: {variant!r}")
    if b3_module is None:
        import er019_family_x_storyline_b3_fact_selection_01 as b3_module
    orig = b3_module.build_user_prompt
    try:
        if variant == "nb" or sent_log is not None:
            def wrapped(*a, **k):
                out = orig(*a, **k)
                if variant == "nb":
                    out = append_block(out)
                if sent_log is not None:
                    sent_log.append(sha256_text(out))
                return out
            b3_module.build_user_prompt = wrapped
        yield variant
    finally:
        b3_module.build_user_prompt = orig


def assert_fresh_out_dir(out_dir: str, phase: str = "phase1") -> None:
    if phase == "phase1":
        if os.path.exists(out_dir):
            raise SystemExit(f"out_dir既存(混線防止でSTOP): {out_dir}")
    else:
        if not os.path.exists(f"{out_dir}/ja_writer/revision2.md"):
            raise SystemExit(f"phase2にはphase1完了済みout_dirが必要: {out_dir}")
        if os.path.exists(f"{out_dir}/b1b/article.md"):
            raise SystemExit(f"EN記事が既に存在(混線防止でSTOP): {out_dir}/b1b/article.md")


def ledger_dest(out_dir: str) -> str:
    return f"{out_dir}/research_ledger/verified_fact_ledger.txt"


def count_research_calls(usage_log_path: str) -> int:
    n = 0
    if not os.path.exists(usage_log_path):
        return 0
    with open(usage_log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("stage") in ("research", "ledger", "research_ledger"):
                n += 1
    return n


def _write_json(path, obj):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--theme", required=True)
    p.add_argument("--slug", required=True)
    p.add_argument("--ledger-txt", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--phase", choices=("phase1", "phase2"), default="phase1")
    p.add_argument("--budget-jpy", type=float, default=None)
    p.add_argument("--checker-budget-jpy", type=float, default=PHASE_DEFAULT_BUDGET["phase2"])
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--yes-run-paid", action="store_true")
    return p


def build_runner_argv(args, budget):
    stop = "writer" if args.phase == "phase1" else "advanced"
    return ["er019", "--theme", args.theme, "--slug", args.slug, "--out-dir", args.out_dir,
            "--budget-jpy", str(budget), "--stage", "advanced", "--stop-after", stop]


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = build_arg_parser().parse_args(argv)
    variant = resolve_variant()
    budget = args.budget_jpy if args.budget_jpy is not None else PHASE_DEFAULT_BUDGET[args.phase]
    if not os.path.exists(args.ledger_txt):
        raise SystemExit(f"--ledger-txt が無い: {args.ledger_txt}")
    norm = args.out_dir.replace("\\", "/")
    runs_root = get_runs_root()
    if not norm.startswith(runs_root + "/") or f"/{variant}/" not in norm + "/":
        raise SystemExit(f"out_dirは {runs_root}/<slug>/{variant}/rep<k> 規約で、variantと一致させる: {args.out_dir}")
    assert_fresh_out_dir(args.out_dir, args.phase)

    prov = {
        "variant": variant, "env": ENV_NAME, "phase": args.phase, "topic": args.theme, "slug": args.slug,
        "transfer_block_sha256": sha256_text(build_transfer_block()) if variant == "nb" else None,
        "ledger_txt_source": args.ledger_txt, "ledger_txt_sha256": sha256_file(args.ledger_txt),
        "ledger_txt_dest": ledger_dest(args.out_dir),
        "freeze_t01_config_sha256": sha256_file(FREEZE_PATH),
        "budget_jpy": budget, "runner_argv": build_runner_argv(args, budget),
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "args": vars(args),
    }
    prov_path = f"{args.out_dir}/nb_provenance_{args.phase}.json"
    if args.dry_run or not args.yes_run_paid:
        print(json.dumps(prov, ensure_ascii=False, indent=2))
        if not args.dry_run:
            raise SystemExit("--yes-run-paid が必要(有料API実行)。確認のみなら --dry-run")
        print("[dry-run] 有料API呼び出しなし(JPY0)。out_dirは作成していない。")
        return 0

    import er019_family_x_entertainment_production_runner_01 as er019
    import er019_family_x_storyline_b3_fact_selection_01 as b3
    if args.phase == "phase1":
        os.makedirs(os.path.dirname(ledger_dest(args.out_dir)), exist_ok=True)
        shutil.copyfile(args.ledger_txt, ledger_dest(args.out_dir))
    if sha256_file(ledger_dest(args.out_dir)) != prov["ledger_txt_sha256"]:
        raise SystemExit("台帳txtのsha256が一致しない(STOP)")
    _write_json(prov_path, prov)

    sent = []
    old_argv = sys.argv
    sys.argv = build_runner_argv(args, budget)
    exit_reason = "completed"
    try:
        with patched_b3(variant, b3, sent):
            er019.main()
    except SystemExit as e:
        exit_reason = f"SystemExit: {e}"
        raise
    except Exception as e:  # noqa: BLE001
        exit_reason = f"error: {e!r}"
        raise
    finally:
        sys.argv = old_argv
        prov["b3_prompt_sent_sha256_list"] = sent
        prov["research_calls"] = count_research_calls(f"{args.out_dir}/raw_usage_log.jsonl")
        be = f"{args.out_dir}/storyline_b3/runtime_evidence.json"
        if os.path.exists(be):
            with open(be, encoding="utf-8") as f:
                prov["b3_model_id_actual"] = json.load(f).get("model_id_actual")
        cj = f"{args.out_dir}/cost.json"
        if os.path.exists(cj):
            with open(cj, encoding="utf-8") as f:
                prov["cost"] = json.load(f)
        prov["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        prov["exit_reason"] = exit_reason
        _write_json(prov_path, prov)
    assert prov["research_calls"] == 0, f"Researcher/Ledger段のcallが検出された: {prov['research_calls']}"

    if args.phase == "phase2":
        cmd = [sys.executable, CHECKER_TOOL,
               "--ledger-path", ledger_dest(args.out_dir),
               "--article-path", f"{args.out_dir}/b1b/article.md",
               "--source-path", f"{args.out_dir}/ja_writer/revision2.md",
               "--out-dir", f"{args.out_dir}/checker",
               "--budget-jpy", str(args.checker_budget_jpy), "--yes-run-paid"]
        rc = subprocess.call(cmd)
        prov["checker_exit_code"] = rc
        _write_json(prov_path, prov)
        return rc
    return 0


if __name__ == "__main__":
    sys.exit(main())
