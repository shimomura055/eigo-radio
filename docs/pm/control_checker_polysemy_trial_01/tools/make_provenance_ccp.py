# -*- coding: utf-8 -*-
"""実行前provenance作成 + 18 run wrapper --dry-run(0円)。Production関数(runner.run_instance未パッチ)・承認スイッチdump照合・台帳sha・wrapper sha・Note規則・git HEAD。"""
import hashlib, json, os, subprocess, sys, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "er052_output/open233_ledger_clarity_p_trial_01/tools"))
sys.path.insert(0, os.path.join(ROOT, "docs/pm/control_checker_polysemy_trial_01/tools"))
import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_self_recovery_precheck_01 as precheck
import run_checker_after_p01 as rc
import driver_ccp as drv
assert "er052_open238_precheck_fix_dev_01" not in sys.modules, "DEV patch module imported"
B = drv.B
sha = rc.sha256_file


def git(*a):
    return subprocess.check_output(["git", *a], text=True, encoding="utf-8").strip()


def main():
    applied = runner.apply_open233_approved_flow_switches()
    runner.assert_open233_approved_flow_switches()
    plan = json.load(open("docs/pm/control_checker_polysemy_trial_01/approved_switches_dump_plan_dryrun.json", encoding="utf-8"))["switches"]
    ref = json.load(open("er052_output/open233_prod_e2e_02/approved_switches_dump_worker1.json", encoding="utf-8"))["switches"]
    rc.save(f"{B}/approved_switches_dump.json", {"switches": applied})
    dry = []
    for (s, v, k) in drv.tasks():
        c = drv.cmd_for(s, v, k, "phase1")
        c = [x for x in c if x != "--yes-run-paid"] + ["--dry-run"]
        p = subprocess.run(c, capture_output=True, text=True, encoding="utf-8", env=drv.env_for(v))
        out = p.stdout
        j = json.loads(out[:out.rindex("}") + 1])
        d = drv.rep_dir(s, v, k)
        dry.append({"run": f"{s}/{v}/rep{k}", "rc": p.returncode, "variant": j["variant"],
                    "transfer_block_sha256": j["transfer_block_sha256"], "ledger_txt_sha256": j["ledger_txt_sha256"],
                    "out_dir_created": os.path.exists(d), "dry_run_no_paid": "有料API呼び出しなし" in out})
    prov = {
        "git_head": git("rev-parse", "HEAD"),
        "dirty_vs_head": {f: (git("diff", "--stat", "--", f) or "clean") for f in
                          ["er019_family_x_entertainment_production_runner_01.py", "er019_family_x_storyline_b3_fact_selection_01.py",
                           "er052_open233_self_recovery_flow_runner_01.py", "er052_open233_self_recovery_precheck_01.py", "CURRENT_SPEC.md"]},
        "wrapper_sha256": sha("er052_open233_polysemy_nb_dev_01.py"),
        "wrapper_dirty_vs_head": "dirty(旧Note規則env追加=本委任の変更)" if git("diff", "--stat", "--", "er052_open233_polysemy_nb_dev_01.py") else "clean",
        "er019_sha256": sha("er019_family_x_entertainment_production_runner_01.py"),
        "b3_sha256": sha("er019_family_x_storyline_b3_fact_selection_01.py"),
        "precheck_sha256": sha("er052_open233_self_recovery_precheck_01.py"),
        "runner_sha256": sha("er052_open233_self_recovery_flow_runner_01.py"),
        "dev_patch_module_loaded": "er052_open238_precheck_fix_dev_01" in sys.modules,
        "entry": "runner.run_instance (Production function, unpatched) via run_checker_after_p01.py; writer=er019.main() via DEV wrapper (variant nb/control)",
        "switches_equal_ref_e2e02": applied == ref, "switches_equal_plan_dryrun": applied == plan, "n_switches": len(applied),
        "PRECHECK_MODE": applied.get("PRECHECK_MODE"), "FLOOR_MODE": applied.get("FLOOR_MODE"), "model_id": applied.get("MODEL"),
        "note_rule": {"env": "OPEN233_NOTE_RULE", "meta_nb": drv.LEGACY, "others": "unset(control: transfer block not used)"},
        "meta_transfer_block_sha256": dry[0]["transfer_block_sha256"],
        "ledger_sha256": {"meta_nb(HC-012 Note)": sha(drv.META_LEDGER), **{s: sha(drv.ledger_of(s, "control")) for s in ("hormuz", "space_weapons", "sewer", "ai_control")}},
        "theme_note": "--themeはtopic.txtの内容(TRIAL-04/E2E_02 controlはtopic.txtのパス文字列を渡していた。META-ROLLBACK 0/12は内容を渡していた)",
        "python": drv.PY, "limits": {"cum": drv.CUM_LIMIT, "run": drv.RUN_LIMIT, "maxrerun": drv.MAXRERUN},
        "dry_run_18": dry, "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    assert prov["switches_equal_ref_e2e02"] and prov["switches_equal_plan_dryrun"], "承認スイッチ不一致"
    assert prov["meta_transfer_block_sha256"].startswith("abd16d9a")
    assert all(x["rc"] == 0 and not x["out_dir_created"] and x["dry_run_no_paid"] for x in dry)
    assert all(x["transfer_block_sha256"] is None for x in dry if x["variant"] == "control")
    rc.save(f"{B}/provenance.json", prov)
    print(json.dumps({k: v for k, v in prov.items() if k != "dry_run_18"}, ensure_ascii=False, indent=1)[:3000])
    print("dry-run 18 OK:", len(dry))


if __name__ == "__main__":
    main()
