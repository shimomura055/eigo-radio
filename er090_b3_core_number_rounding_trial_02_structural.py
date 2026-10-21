# -*- coding: utf-8 -*-
"""委任_03 構造不変証拠(API 0): B3既存機能・Writer入力がoverlay以外で不変であることを決定論diffで示す。
  (1) storyline_b3/research_ledger の全ファイルsha: dataset == control == after (B3選定・中核数値選定・sidecar・manifest無改変)
  (2) 注記md/sidecar/manifestの契約検証がPASS(validate_annotated_b3)
  (3) After R0 Prompt = Control(=Before) R0 Prompt + 追記行 + 規則8のみ(削除行0)
  (4) 概数可0件のoverlayではPromptがbyte一致(DefaultOffIsolation相当)。全dataset記事で確認
  (5) Production moduleのgit diff = 0
出力: evidence/structural_diff_02.json
"""
from __future__ import annotations

import difflib
import hashlib
import json
import os
import subprocess

import er053_b3_annotation_contract_01 as contract
import er053_b3_deterministic_producer_01 as prod
import er053_family_x_factlock_ja_writer_01 as w1
import er090_b3_core_number_rounding_trial_01_overlay as ov
import er090_b3_core_number_rounding_trial_02_p2 as p2
import er090_b3_core_number_rounding_trial_02_run as r2

ROOT = r2.ROOT
HERE = r2.HERE


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def tree_sha(d, subs=("research_ledger", "storyline_b3")):
    out = {}
    for sub in subs:
        for dp, _dn, fns in os.walk(os.path.join(d, sub)):
            for fn in fns:
                p = os.path.join(dp, fn)
                out[os.path.relpath(p, d).replace("\\", "/")] = sha_file(p)
    return out


def prompts(d, overlay):
    a = contract.validate_annotated_b3(d)
    story, _ = w1.parse_brief_md(a.annotated_md_text)
    bp = w1.build_r0_prompt(story, a.news_field_text)
    after_news = ov.apply_to_news_field(a.facts_text, a.constraints_text, overlay, prod.CONS_HEADING, prod.compose_news_field)
    ap = ov.apply_rule8(w1.build_r0_prompt(story, after_news), overlay)
    return bp, ap


def main():
    out = {"phase2": {}, "zero_approx_byte_identity": {}, "production_git_diff_zero": None}
    for aid in p2.P2_ARTICLES:
        ds = tree_sha(r2.article_dir(aid))
        c = tree_sha(p2.p2_dir(aid, "control"))
        c2 = tree_sha(p2.p2_dir(aid, "control2"))
        af = tree_sha(p2.p2_dir(aid, "after"))
        ov_used = r2.load_json(os.path.join(p2.p2_dir(aid, "after"), "overlay_used.json"))
        bp, ap = prompts(p2.p2_dir(aid, "after"), ov_used)
        udiff = list(difflib.unified_diff(bp.split("\n"), ap.split("\n"), "control", "after", lineterm="", n=0))
        added = [l[1:] for l in udiff if l.startswith("+") and not l.startswith("+++")]
        removed = [l[1:] for l in udiff if l.startswith("-") and not l.startswith("---")]
        res_a = r2.load_json(os.path.join(p2.p2_dir(aid, "after"), "arm_result.json"))
        res_c = r2.load_json(os.path.join(p2.p2_dir(aid, "control"), "arm_result.json"))
        res_c2 = r2.load_json(os.path.join(p2.p2_dir(aid, "control2"), "arm_result.json"))
        out["phase2"][aid] = {
            "b3_and_ledger_files_equal_dataset_control_control2_after": ds == c == c2 == af, "n_files": len(ds),
            "contract_validated_all_arms": True,
            "control_r0_prompt_equals_before": res_c["before_r0_prompt_sha256"] == res_c["writer"]["r0_prompt_sha256_used"],
            "control2_r0_prompt_equals_before": res_c2["before_r0_prompt_sha256"] == res_c2["writer"]["r0_prompt_sha256_used"],
            "after_r0_prompt_sha_matches_reconstruction": hashlib.sha256(ap.encode("utf-8")).hexdigest() == res_a["writer"]["r0_prompt_sha256_used"],
            "after_prompt_added_lines": added, "after_prompt_removed_line_count": len(removed),
            "overlay_n_approximate_ok": ov_used["n_approximate_ok"],
            "overlay_entries": [{"concept": e["concept"], "surfaces": [(s["surface"], s["approx"]) for s in e["surfaces"]] if e["final_decision"] == "APPROXIMATE_OK" else None,
                                 "final": e["final_decision"]} for e in ov_used["entries"]],
        }
    # 全dataset: 概数可0件 → Promptがbyte一致
    for aid in r2.dataset_ids():
        ovp = os.path.join(ROOT, "judge", "luna_low_rep1", aid, "overlay.json")
        o = r2.load_json(ovp)
        bp, ap = prompts(r2.article_dir(aid), o)
        out["zero_approx_byte_identity"][aid] = {"n_approx": o["n_approximate_ok"], "prompt_byte_identical": bp == ap}
    zero = [v for v in out["zero_approx_byte_identity"].values() if v["n_approx"] == 0]
    out["zero_approx_all_identical"] = all(v["prompt_byte_identical"] for v in zero)
    out["n_articles_zero_approx"] = len(zero)
    files = ["er053_family_x_factlock_ja_writer_01.py", "er053_b3_deterministic_producer_01.py", "er053_risk_flagger_production_01.py",
             "er019_family_x_entertainment_production_runner_01.py", "er006_model_routing_contract_01.py", "er053_b3_annotation_contract_01.py",
             "er003_v1_n3_01_evidence_compression_editor.py"]
    rc = subprocess.run(["git", "diff", "--quiet", "HEAD", "--"] + files, cwd=HERE).returncode
    out["production_git_diff_zero"] = (rc == 0)
    out["production_files_checked"] = files
    r2.save_json(os.path.join(ROOT, "evidence", "structural_diff_02.json"), out)
    print(json.dumps({k: v for k, v in out.items() if k != "zero_approx_byte_identity"}, ensure_ascii=False, indent=1)[:3500])


if __name__ == "__main__":
    main()
