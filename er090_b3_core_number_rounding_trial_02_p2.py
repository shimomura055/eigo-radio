# -*- coding: utf-8 -*-
"""FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01 委任_03 Phase 2 runner(Trial専用。Production module無改変)。

1 process = 1記事 x 1 arm(control|after)。Writer(R0/R1/R2) -> Advanced/Standard -> Risk Flagger(Review Queue保存なし)
-> 旧LDC(Trial専用の追加参考検査)。Writer STOP相当の例外は記録して下流へ進まない(再実行しない)。
使い方: .venv/Scripts/python.exe er090_b3_core_number_rounding_trial_02_p2.py --art art_xxx --arm control|after
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er012_e_family_entertainment_two_level_runner_01 as efam
import er019_family_x_entertainment_production_runner_01 as runner
import er053_b3_annotation_contract_01 as contract
import er053_b3_deterministic_producer_01 as prod
import er053_family_x_factlock_ja_writer_01 as w1
import er053_risk_flagger_production_01 as rf
import er090_b3_core_number_rounding_trial_01_overlay as ov
import er090_b3_core_number_rounding_trial_02_run as r2

ROOT, THEME_TAG = r2.ROOT, r2.THEME_TAG
P2_ARTICLES = ("art_a31992b5", "art_701612d8", "art_9bd6834e", "art_36b2c87d")   # 事前規則: luna_low rep1でAPPROX>=1の記事から多様性優先4本
P2_JUDGE_VARIANT = "luna_low_rep1"                                                # Phase 2の丸め判断=Luna(effort=low)の1回判断をそのまま使う


def p2_dir(aid, arm):
    return os.path.join(ROOT, "phase2", aid, arm)


def sha_text(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def run(aid, arm):
    d = p2_dir(aid, arm)
    os.makedirs(d, exist_ok=True)
    result_path = os.path.join(d, "arm_result.json")
    if os.path.exists(result_path):
        print("[p2] skip existing", aid, arm)
        return
    for sub in ("research_ledger", "storyline_b3"):
        if not os.path.exists(os.path.join(d, sub)):
            shutil.copytree(os.path.join(r2.article_dir(aid), sub), os.path.join(d, sub))
    cl.install(os.path.join(d, "raw_usage_log.jsonl"))
    client = vfl01.get_client()
    a = contract.validate_annotated_b3(d)
    story, _ = w1.parse_brief_md(a.annotated_md_text)
    before_news = a.news_field_text
    before_prompt = w1.build_r0_prompt(story, before_news)
    res = {"article": aid, "arm": arm, "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "stages": {}, "stop": None, "events": [],
           "w1_module_sha256": hashlib.sha256(open(w1.__file__, "rb").read()).hexdigest(),
           "before_r0_prompt_sha256": sha_text(before_prompt)}
    if arm == "after":
        overlay = r2.load_json(os.path.join(ROOT, "judge", P2_JUDGE_VARIANT, aid, "overlay.json"))
        r2.save_json(os.path.join(d, "overlay_used.json"), overlay)
        after_news = ov.apply_to_news_field(a.facts_text, a.constraints_text, overlay, prod.CONS_HEADING, prod.compose_news_field)
        orig = w1.build_r0_prompt

        def patched(storyline_line, brief_facts_text):
            assert brief_facts_text == before_news, "unexpected news field"
            return ov.apply_rule8(orig(storyline_line, after_news), overlay)
        w1.build_r0_prompt = patched      # このprocess内のみ。ファイルは無改変
        res["after_r0_prompt_sha256"] = sha_text(patched(story, before_news))
        res["overlay_n_approximate_ok"] = overlay["n_approximate_ok"]
    topic = story.split("\n")[0][:200]
    theme = {"theme_id": aid, "topic": topic, "out_dir": d, "ledger_path": os.path.join(d, "research_ledger", "verified_fact_ledger.txt")}
    ledger_text = open(theme["ledger_path"], encoding="utf-8").read()

    def timed(name, fn):
        t0 = time.time()
        try:
            r = fn()
            res["stages"][name] = {"sec": round(time.time() - t0, 1), "ok": True}
            return r
        except Exception as exc:           # noqa: BLE001 - Production停止相当は記録して下流へ進まない(再実行しない)
            res["stages"][name] = {"sec": round(time.time() - t0, 1), "ok": False, "error": f"{type(exc).__name__}: {str(exc)[:300]}"}
            res["stop"] = {"stage": name, "type": type(exc).__name__, "message": str(exc)[:500]}
            raise

    try:
        r2.guard(f"before writer {aid} {arm}")
        wres = timed("writer_r0_r1_r2", lambda: w1.run_w1_writer(d, client=client, budget_check=lambda: r2.guard(f"writer {aid} {arm}")))
        ev = wres["runtime_evidence"]
        r0m = r2.load_json(os.path.join(d, "ja_writer", "factlock", "r0_meta.json"))
        res["writer"] = {"models": {"r0": ev["original"]["model"], "r1": ev["r1"]["model"], "r2": ev["r2"]["model"]},
                         "r0_prompt_sha256_used": r0m["r0_prompt_sha256"], "marks_echoed": r0m["marks_echoed"],
                         "symbol_qa_r0_regenerated": ev["symbol_qa"]["r0"].get("regenerated"),
                         "symbol_qa_r2_rerun": ev["symbol_qa"]["r2"].get("rerun"), "r0_calls": len(ev["original"]["r0_calls"]),
                         "r2_attempts": len(ev["r2_all_attempts"]), "r2_echo": ev["r2_echo_after_revision"]}
        ja_text = wres["ja_text"]
        for only in ("advanced", "standard"):
            r2.guard(f"before {only} {aid} {arm}")

            def _en(only=only):
                with cl.logging_context(runner.RUNNER_TAG, only):
                    return efam.run_writer_stage(client, theme, ja_text, ledger_text, 90.0, only=only)
            timed("en_" + only, _en)
        for lvl in ("b1b", "a2"):
            p = os.path.join(d, lvl, "article.md")
            r2.guard(f"before rf {lvl} {aid} {arm}")

            def _rf(lvl=lvl, p=p):
                sha0 = hashlib.sha256(open(p, "rb").read()).hexdigest()
                r = rf.run_risk_flagger(article_path=p, ledger_path=theme["ledger_path"], article_id=f"d03_{aid}_{arm}_{lvl}", article_level=lvl,
                                        out_dir=os.path.join(d, f"rf_{lvl}"), producer="deterministic_v2", run_label=THEME_TAG,
                                        record_entry_point=False, budget_check=lambda: r2.guard("rf"))
                assert hashlib.sha256(open(p, "rb").read()).hexdigest() == sha0
                r2.save_json(os.path.join(d, f"rf_{lvl}.json"), r)
                return r
            r = timed("rf_" + lvl, _rf)
            res["stages"]["rf_" + lvl]["status"] = r["status"]
            res["stages"]["rf_" + lvl]["issues"] = len(r["issues"])
        for tag, path in (("ldc_ja", os.path.join(d, "ja_writer", "revision2.md")), ("ldc_b1b", os.path.join(d, "b1b", "article.md")),
                          ("ldc_a2", os.path.join(d, "a2", "article.md"))):
            r2.guard(f"before {tag}")

            def _ldc(tag=tag, path=path):
                art = open(path, encoding="utf-8").read()
                with cl.logging_context(THEME_TAG, f"{tag}_{aid}_{arm}"):
                    r = vfl01.run_deviation_check(client, ledger_text, art, hook_aware=True)
                r2.save_json(os.path.join(d, f"{tag}.json"), {"article_sha256": sha_text(art), "parsed": r["parsed"]})
                return r
            r = timed(tag, _ldc)
            res["stages"][tag]["overall"] = r["parsed"].get("overall_status")
            res["stages"][tag]["n_deviation"] = len(r["parsed"].get("deviations", []))
    except Exception as exc:               # noqa: BLE001
        res["events"].append(f"STOPPED: {type(exc).__name__}: {str(exc)[:300]}")
        print("[p2] STOPPED", aid, arm, type(exc).__name__, str(exc)[:200])
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    r2.save_json(result_path, res)
    print("[p2] done", aid, arm, "stop=", res["stop"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--art", required=True)
    ap.add_argument("--arm", required=True, choices=("control", "control2", "after"))
    a = ap.parse_args()
    assert a.art in P2_ARTICLES, "Phase 2対象外"
    run(a.art, a.arm)


if __name__ == "__main__":
    main()
