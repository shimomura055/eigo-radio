# -*- coding: utf-8 -*-
"""STAGE2-01 委任_01 作業3: スイッチOFF時の差分0確認(API無し)。
保存済みログ(qvqc=meta nb rep2、jb9k=ai_control control rep1)の各cycleについて、
  (1) coverage_changed_scope(en_text_before_rewrite, en_text_after_rewrite) を HEAD版(_cov_head_snapshot.py) と 現行版 で再計算し、
      両者一致 かつ 保存済み recheck_coverage.scope_ids/changed_ids とも一致するか
  (2) run_recheck_scope が組み立てるr3/r5v promptが HEAD版と現行版(structural_pairs無し)でバイト同一か
  (3) 現行テンプレートsha(PROMPT_SHA256)が保存済みログのprompt_sha256と一致するか
を検査する。確認できない部分(Stage1/Stage2のLLM判定そのもの、W1のRewrite出力)は再現不能(APIが必要)。"""
import importlib.util, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_stage1_coverage_checker_01 as new
sp = importlib.util.spec_from_file_location("cov_head", pathlib.Path(__file__).parent / "_cov_head_snapshot.py")
head = importlib.util.module_from_spec(sp); sp.loader.exec_module(head)
RUNS = ROOT / "er052_output/open233_control_checker_polysemy_trial_01/runs"
TARGETS = {"qvqc_meta_nb_rep2": RUNS / "meta/nb/rep2", "jb9k_ai_control_control_rep1": RUNS / "ai_control/control/rep1"}
seg = dict(segment_fn=runner.vs_sentence_segments_l6, initial_extra=runner.CAUSAL_SENTENCE_INITIAL_EN)


class Cap:
    def __init__(self): self.calls = []
    def __call__(self, label, dev, prompt, schema):
        self.calls.append((label, prompt)); return None, {"cost_jpy": 0.0}


out = {"sha_current": new.PROMPT_SHA256, "targets": {}}
for name, d in TARGETS.items():
    run = json.load(open(d / "checker/runs/meta_run03_advanced.json", encoding="utf-8"))
    ledger = (d / "research_ledger/verified_fact_ledger.txt").read_text(encoding="utf-8")
    rec = {"sha_matches_saved": run["stage1_coverage"]["prompt_sha256"] == new.PROMPT_SHA256, "cycles": []}
    for c in run["cycles"]:
        if not c.get("recheck_coverage"):
            continue
        b, a = c["en_text_before_rewrite"], c["en_text_after_rewrite"]
        pi = [{"claim_in_article": r.get("claim_text") or ""} for r in (c.get("stage2_results") or []) if r.get("materiality") == "BLOCKING"]
        pcl = [x["claim_in_article"] for x in pi]
        sn, sh = new.coverage_changed_scope(b, a, prior_claims=pcl, **seg), head.coverage_changed_scope(b, a, prior_claims=pcl, **seg)
        saved = c["recheck_coverage"]
        pr_n, pr_h = Cap(), Cap()
        fx = {"ledger_text": ledger, "article_text": a}
        new.run_recheck_scope(fx, pr_n, b, pi, **seg)
        head.run_recheck_scope(fx, pr_h, b, pi, **seg)
        rec["cycles"].append({"cycle": c["cycle"],
                              "scope_new_eq_head": sn["scope_ids"] == sh["scope_ids"] and sn["changed_ids"] == sh["changed_ids"],
                              "scope_eq_saved": sn["scope_ids"] == saved["scope_ids"],
                              "changed_eq_saved": sn["changed_ids"] == saved["changed_ids"],
                              "prompts_byte_identical_head_vs_new": pr_n.calls == pr_h.calls, "n_prompts": len(pr_n.calls),
                              "note_scope_eq_saved": "prior_issuesはcycleのBLOCKING stage2_resultsのclaim_textで近似(実際のprior_issue列と細部が違いうる)"})
    out["targets"][name] = rec
(pathlib.Path(__file__).parent / "replay_off_identity.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(out, ensure_ascii=False, indent=1))
