# -*- coding: utf-8 -*-
"""FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01 委任_06 C-2 Phase 4: P-11 証拠(API 0、費用0円)。実run(記事A run_pp_02)のartifactを一時copyして検査。
 (2') 実run overlayの n_approximate_ok=0 のため、実artifactで「概数可が1件以上のときのPrompt組立」をoffline検証(判断は**仮定**=Lunaの判断ではない。
      Writer呼出なし)。R0 Promptに規則8と【概数表記】行が入り、overlay無し/0件時のPromptとの差が追加分だけであること。
 (3)  resume経路の実走: 既存revision2.md+実overlayの状態で runner の producer -> 丸めhelper -> load_reused_ja_text を実コードで実行。
      client は使用すると例外を投げるbomb(api_calls=0の証明)。W5照合PASS、overlay差替/改ざんでSTOP。
出力: <run>/audit/p11_check_01.json
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from types import SimpleNamespace
from unittest import mock

import er019_family_x_entertainment_production_runner_01 as runner
import er053_b3_annotation_contract_01 as contract
import er053_family_x_factlock_ja_writer_01 as w1
import er095_b3_core_number_rounding_01 as m


class Bomb:
    calls = 0

    def __getattr__(self, name):
        Bomb.calls += 1
        raise AssertionError("API client was used (resume must be API 0)")


def main(run_dir: str):
    tmp = tempfile.mkdtemp(prefix="p11_")
    work = os.path.join(tmp, "run")
    shutil.copytree(run_dir, work, ignore=shutil.ignore_patterns("raw_usage_log.jsonl"))
    res = {"source_run": run_dir, "note": "一時copyで実行。実runのファイルは変更しない"}
    ledger = open(os.path.join(work, "research_ledger", "verified_fact_ledger.txt"), encoding="utf-8").read()
    real_ev = json.load(open(os.path.join(work, "ja_writer", "runtime_evidence.json"), encoding="utf-8"))
    real_overlay = json.load(open(m.overlay_path(work), encoding="utf-8"))
    res["real_overlay"] = {"status": real_overlay["status"], "n_approximate_ok": real_overlay["n_approximate_ok"],
                           "model_returned": real_overlay["judge"]["model_returned"], "effort": real_overlay["judge"]["effort"],
                           "overlay_sha256": real_overlay["overlay_sha256"]}

    # ---- (2') 仮定の概数指定でのPrompt組立(offline) ----
    a = contract.validate_annotated_b3(work)
    story, facts_text = w1.parse_brief_md(a.annotated_md_text)
    base_prompt = w1.build_r0_prompt(story, a.news_field_text)
    res["prompt_without_overlay_sha256"] = w1.sha_text(base_prompt)
    res["actual_run_r0_prompt_sha256"] = real_ev["rounding"]["r0_prompt_sha256"]
    res["actual_run_prompt_equals_no_overlay_prompt"] = (w1.sha_text(base_prompt) == real_ev["rounding"]["r0_prompt_sha256"])
    hypo = {"最大134,515人": "最大約13万5千人", "134,515人": "約13万5千人"}   # 仮定(Lunaの判断ではない)。V8: |135000-134515|/134515=0.36%

    def hypo_judge(client, prompt, tag):
        decisions = []
        for c in m.core_concepts(a.sidecar):
            if all(s in hypo for s in c["surfaces"]):
                decisions.append({"concept": c["concept"], "decision": m.DECISION_APPROX, "reason": "HYPOTHETICAL(offline Prompt組立検証)",
                                  "surfaces": [{"surface": s, "approx_surface": hypo[s]} for s in c["surfaces"]],
                                  "basis_fact_ids": list(c["ledger_ids"]), "approved_condition": "hypothetical"})
            else:
                decisions.append({"concept": c["concept"], "decision": m.DECISION_EXACT, "reason": "r", "approved_condition": "c",
                                  "surfaces": [{"surface": s, "approx_surface": None} for s in c["surfaces"]], "basis_fact_ids": list(c["ledger_ids"])})
        return {"parsed": {"decisions": decisions}, "model_requested": "gpt-6-luna", "model_returned": "gpt-6-luna(HYPOTHETICAL_STUB)",
                "response_id": "hypothetical", "sec": 0.0, "effort": "low", "usage": {}}

    work2 = os.path.join(tmp, "run_hypo")
    shutil.copytree(work, work2)
    os.remove(m.overlay_path(work2))
    r = m.run_core_number_rounding(None, work2, contract.validate_annotated_b3(work2), w1.parse_brief_md, ledger, judge=hypo_judge)
    ov, ev = m.load_overlay_for_writer(work2, a.annotated_md_sha256)
    from er053_b3_deterministic_producer_01 import CONS_HEADING, compose_news_field
    news = m.news_field_for_writer(a.news_field_text, facts_text, a.constraints_text, ov, CONS_HEADING, compose_news_field)
    p = w1.build_r0_prompt(story, news, ov)
    added = p[len(base_prompt):] if False else None
    res["hypothetical"] = {"status": r["status"], "n_approximate_ok": r["n_approximate_ok"], "applied": ev["applied"],
                           "rule8_in_prompt": p.endswith(m.RULE8_TEXT), "constraint_lines": m.constraint_lines(ov),
                           "prompt_sha256": w1.sha_text(p), "prompt_len_added": len(p) - len(base_prompt),
                           "expected_added_len": len(m.RULE8_TEXT) + len("\n".join(m.constraint_lines(ov)) + "\n"),
                           "news_field_changed": news != a.news_field_text,
                           "contains_概数表記_line": all(l in p for l in m.constraint_lines(ov))}
    res["hypothetical"]["added_equals_expected"] = res["hypothetical"]["prompt_len_added"] == res["hypothetical"]["expected_added_len"]

    # ---- (3) resume経路の実走(実コード、API 0) ----
    with mock.patch.object(runner.efam, "assert_budget_ok", return_value=0.0):
        runner.run_annotation_producer(work)            # 決定論・LLM 0(冪等)
        out = {}
        for stage in ("standard", "advanced", "writer"):
            args = SimpleNamespace(regenerate_stage=None, budget_jpy=60.0)
            out[stage] = runner.run_core_number_rounding(Bomb(), work, ledger, args, stage)
    text = runner.load_reused_ja_text(work)
    res["resume"] = {"helper_results": {k: {kk: v.get(kk) for kk in ("status", "api_calls", "reused", "n_approximate_ok")} for k, v in out.items()},
                     "api_client_uses": Bomb.calls, "ja_text_reused_equals_revision2": text == open(os.path.join(work, "ja_writer", "revision2.md"), encoding="utf-8").read(),
                     "provenance": m.check_resume_provenance(work, real_ev.get("rounding")),
                     "recorded_overlay_sha256": real_ev["rounding"]["overlay_sha256"], "current_overlay_sha256": m.current_overlay_sha(work)}
    # 負例: overlay差替(同一B3版で内容が違う)ならSTOP
    ov_bad = json.load(open(m.overlay_path(work), encoding="utf-8"))
    ov_bad["note"] = "tampered"
    json.dump(ov_bad, open(m.overlay_path(work), "w", encoding="utf-8"), ensure_ascii=False)
    try:
        runner.load_reused_ja_text(work)
        res["resume"]["tampered_overlay_stops"] = False
    except runner.LegacyWriterProvenanceStop as e:
        res["resume"]["tampered_overlay_stops"] = "PROVENANCE_MISMATCH" in str(e)
    out_path = os.path.join(run_dir, "audit", "p11_check_01.json")
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    shutil.rmtree(tmp, ignore_errors=True)
    print(json.dumps(res, ensure_ascii=False, indent=1)[:3500])


if __name__ == "__main__":
    main(sys.argv[1])
