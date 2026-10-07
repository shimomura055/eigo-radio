# -*- coding: utf-8 -*-
"""OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01 Phase A: B3単独実行の薄い起動ラッパ(Trial専用、Production経路ではない)。
既存DEV runnerは変更しない。--dry-run: API呼び出しなしでprompt全文を --prompt-out へ書く。
有料実行は --yes-run-paid のみ。out-dirは新規必須(混線防止)。台帳はer052_output/open233_polysemy_trial_02/ledgers/<slug>/ を使う。"""
import argparse, json, os, shutil, sys, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT); os.chdir(ROOT)
import er052_open233_b3_variant_dev_01 as dev

LED = "er052_output/open233_polysemy_trial_02/ledgers/{s}"
SLUGS = ("meta", "hormuz", "space_weapons")
RUNS_ROOT = "er052_output/open233_b3_trial_01/runs"


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", required=True, choices=dev.VARIANT_NAMES)
    ap.add_argument("--slug", required=True, choices=SLUGS)
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--budget-jpy", type=float, default=5.0)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--prompt-out", default=None)
    ap.add_argument("--yes-run-paid", action="store_true")
    a = ap.parse_args(argv)
    ledger = f"{LED.format(s=a.slug)}/control/research_ledger/verified_fact_ledger.txt"
    topic = read(f"{LED.format(s=a.slug)}/topic.txt").strip()
    import er019_family_x_storyline_b3_fact_selection_01 as b3
    base = b3.build_user_prompt(topic, read(ledger))
    full = dev.apply_variant(base, a.variant)
    prov = dev.provenance(a.variant, full)
    prov.update({"slug": a.slug, "ledger_sha256": dev.sha256_text(read(ledger)), "topic": topic,
                 "budget_jpy": a.budget_jpy})
    if a.dry_run or not a.yes_run_paid:
        if a.prompt_out:
            os.makedirs(os.path.dirname(a.prompt_out), exist_ok=True)
            with open(a.prompt_out, "w", encoding="utf-8", newline="") as f:
                f.write(full)
        print(json.dumps(prov, ensure_ascii=False, indent=2))
        if not a.dry_run:
            raise SystemExit("--yes-run-paid が必要(有料API)。確認のみなら --dry-run")
        print("[dry-run] API呼び出しなし(JPY0)")
        return 0
    if not a.out_dir:
        raise SystemExit("--out-dir 必須")
    norm = a.out_dir.replace("\\", "/")
    if not norm.startswith(f"{RUNS_ROOT}/{a.slug}/nb/{a.variant}/"):
        raise SystemExit(f"out-dirは {RUNS_ROOT}/{a.slug}/nb/{a.variant}/b<i> 規約: {a.out_dir}")
    if os.path.exists(a.out_dir):
        raise SystemExit(f"out_dir既存(STOP): {a.out_dir}")
    dest = f"{a.out_dir}/research_ledger/verified_fact_ledger.txt"
    os.makedirs(os.path.dirname(dest))
    shutil.copyfile(ledger, dest)
    import er019_family_x_entertainment_production_runner_01 as er019
    argv2 = ["er019", "--theme", topic, "--slug", a.slug, "--out-dir", a.out_dir,
             "--budget-jpy", str(a.budget_jpy), "--stage", "storyline_b3", "--stop-after", "storyline_b3"]
    sent, old, reason = [], sys.argv, "completed"
    pp = f"{a.out_dir}/b3_variant_provenance.json"
    try:
        sys.argv = argv2
        with dev.patched_b3_variant(a.variant, b3, sent):
            er019.main()
    except BaseException as e:  # noqa: BLE001
        reason = f"{type(e).__name__}: {e}"
        raise
    finally:
        sys.argv = old
        prov.update({"runner_argv": argv2, "b3_prompt_sent_sha256_list": sent, "exit_reason": reason,
                     "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S")})
        os.makedirs(a.out_dir, exist_ok=True)
        with open(pp, "w", encoding="utf-8") as f:
            json.dump(prov, f, ensure_ascii=False, indent=2)
    if sent and sent[0] != prov["full_prompt_sha256"]:
        raise SystemExit("送信prompt shaがdry-run予測と不一致(STOP)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
