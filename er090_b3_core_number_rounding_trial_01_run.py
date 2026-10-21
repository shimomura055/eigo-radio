# -*- coding: utf-8 -*-
"""FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01 Trial専用runner(Production経路ではない。Production module無改変)。

使い方(各stepは独立process。再起動・自動retryラッパなし):
  .venv/Scripts/python.exe er090_b3_core_number_rounding_trial_01_run.py --step prep
  ... --step judge
  ... --step writer --arm after      (並列可)
  ... --step writer --arm control    (並列可。概数情報なし=Production同等Prompt)
  ... --step en                      (after のみ Advanced/Standard)
  ... --step check                   (LDC + Risk Flagger。Review Queue保存なし)
Guardrail: 全log合計 JPY100(超過でSTOP。90超で新規call前に停止)。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er012_e_family_entertainment_two_level_runner_01 as efam
import er019_family_x_entertainment_production_runner_01 as runner
import er053_b3_annotation_contract_01 as contract
import er053_b3_deterministic_producer_01 as prod
import er053_cost_aggregate_01 as ca
import er053_family_x_factlock_ja_writer_01 as w1
import er053_risk_flagger_production_01 as rf
import er090_b3_core_number_rounding_trial_01_overlay as ov

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "er090_output", "b3_core_number_rounding_trial_01")
RUN_A = os.path.join(HERE, "er019_output", "paycheck_personality", "run_pp_01")
GUARD_STOP_JPY = 90.0           # 新規call前の停止線(Guardrail JPY100に対する安全余裕)
JUDGE_EFFORT = "high"
THEME_TAG = "FAMILY_X_B3_CORE_NUMBER_ROUNDING_TRIAL_01"

# 判定対象の出典(記事A + 丸めないケースの実Ledger出典)。期待ラベルはここ(評価側)にのみ存在しLLMへは渡さない。
SOURCES = {
    "A": {"run": RUN_A, "contract": True},
    "coffee": {"run": os.path.join(HERE, "er019_output", "coffee_prices", "run_fxpw_01"), "contract": False},
    "boredom": {"run": os.path.join(HERE, "er019_output", "boredom_aggression", "run_bape_01"), "contract": False},
    "semi": {"run": os.path.join(HERE, "er019_output", "semiconductor_earnings", "run_devconfirm_01"), "contract": False},
}
EXPECTED = {   # (source, surface) -> 事前登録ラベル(TRIAL_DESIGN_01 (f))
    ("A", "134,515人"): "APPROXIMATE_OK", ("A", "11件"): "EXACT_REQUIRED", ("A", "3回以上"): "EXACT_REQUIRED",
    ("A", "0.0630"): "EXACT_REQUIRED",
    ("coffee", "4.30"): "EXACT_REQUIRED", ("coffee", "2025年2月"): "EXACT_REQUIRED",
    ("boredom", "1,332"): "APPROXIMATE_OK", ("boredom", "5分"): "EXACT_REQUIRED", ("boredom", "最大50"): "EXACT_REQUIRED",
    ("semi", "295億9,100万ドル"): "APPROXIMATE_OK",
}
BOUNDARY = {("semi", "295億9,100万ドル")}   # 境界ケース(合否に使わない)


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def sha_text(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def save_json(p, o):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(o, f, ensure_ascii=False, indent=2)


def load_json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def total_cost_jpy() -> float:
    tot = 0.0
    for dp, _dn, fn in os.walk(ROOT):
        if "raw_usage_log.jsonl" in fn:
            tot += ca.compute_stage_cost_breakdown_multi(os.path.join(dp, "raw_usage_log.jsonl"))["total_jpy"]
    return round(tot, 3)


def guard(note=""):
    t = total_cost_jpy()
    print(f"[ROUNDING-TRIAL][guard] cumulative={t:.3f} JPY (stop>{GUARD_STOP_JPY}) {note}")
    if t > GUARD_STOP_JPY:
        raise RuntimeError(f"[GUARDRAIL_STOP] cumulative {t} JPY > {GUARD_STOP_JPY} ({note})")


# ------------------------------------------------------------------ prep
def step_prep():
    man = {}
    for arm in ("after", "control"):
        for sub in ("research_ledger", "storyline_b3"):
            dst = os.path.join(ROOT, arm, sub)
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(os.path.join(RUN_A, sub), dst)
    src_files = {}
    for sub in ("research_ledger", "storyline_b3"):
        for dp, _d, fns in os.walk(os.path.join(RUN_A, sub)):
            for fn in fns:
                p = os.path.join(dp, fn)
                rel = os.path.relpath(p, RUN_A).replace("\\", "/")
                src_files[rel] = sha_file(p)
    for arm in ("after", "control"):
        for rel, s in src_files.items():
            assert sha_file(os.path.join(ROOT, arm, rel)) == s, rel
    man["source"] = RUN_A
    man["copied_file_sha256"] = src_files
    man["note"] = "storyline_b3/research_ledger をbyte copy。B3選定・注記producer・sidecar・manifestは再実行/改変なし。"
    save_json(os.path.join(ROOT, "prep_manifest.json"), man)
    print("[prep] ok files=", len(src_files))


# ------------------------------------------------------------------ judge
def load_source(key):
    cfg = SOURCES[key]
    run = cfg["run"]
    sc = load_json(os.path.join(run, "storyline_b3", "annotation.json"))
    ledger_text = open(os.path.join(run, "research_ledger", "verified_fact_ledger.txt"), encoding="utf-8").read()
    annotated = open(os.path.join(run, "storyline_b3", "selected_brief_annotated.md"), encoding="utf-8").read()
    story, facts_text = w1.parse_brief_md(annotated)
    cpath = os.path.join(run, "storyline_b3", "writer_constraints.txt")
    cons = open(cpath, encoding="utf-8").read() if os.path.exists(cpath) else ""
    return {"sidecar": sc, "ledger_text": ledger_text, "story": story, "facts_text": facts_text, "constraints": cons, "run": run}


def judge_call(client, user_prompt: str, tag: str, effort: str = JUDGE_EFFORT):
    model = routing.require_model("FAMILY_X_STORYLINE_B3", "gpt-6.1-sol")    # 丸め判断=B3と同一model(比較目的)
    t0 = time.time()
    with cl.logging_context(THEME_TAG, tag):
        resp = client.responses.create(
            model=model, reasoning={"effort": effort},
            text={"format": {"type": "json_schema", **ov.JUDGE_JSON_SCHEMA}},
            input=[{"role": "developer", "content": ov.JUDGE_DEVELOPER_MESSAGE}, {"role": "user", "content": user_prompt}])
    return {"parsed": json.loads(resp.output_text), "raw_text": resp.output_text, "model": resp.model,
            "response_id": resp.id, "sec": round(time.time() - t0, 1)}


def step_judge(only=None):
    jobs = [("A", "A_rep1", "high"), ("coffee", "coffee", "high"), ("boredom", "boredom", "high"), ("A", "A_med", "medium"),
            ("A", "A_rep2", "high"), ("semi", "semi", "high")]
    if only:
        jobs = [j for j in jobs if j[1] == only]
    else:
        jobs = [j for j in jobs if j[1] in ("A_rep1", "coffee", "boredom", "A_med")]
    cl.install(os.path.join(ROOT, "judge", "raw_usage_log.jsonl"))
    client = vfl01.get_client()
    for src, tag, effort in jobs:
        out = os.path.join(ROOT, "judge", tag)
        if os.path.exists(os.path.join(out, "overlay.json")):
            print(f"[judge] skip existing {tag}")
            continue
        guard(f"before judge {tag}")
        d = load_source(src)
        recs = ov.parse_ledger_records(d["ledger_text"])
        prompt = ov.build_judge_user_prompt(storyline=d["story"], facts_text=d["facts_text"], constraints_text=d["constraints"],
                                            sidecar=d["sidecar"], ledger_records=recs)
        os.makedirs(out, exist_ok=True)
        open(os.path.join(out, "prompt.txt"), "w", encoding="utf-8", newline="\n").write(prompt)
        r = judge_call(client, prompt, f"judge_{tag}", effort)
        r["effort"] = effort
        save_json(os.path.join(out, "response.json"), r)
        overlay = ov.build_overlay(d["sidecar"], r["parsed"])
        overlay["source"] = src
        overlay["judge_model"] = r["model"]
        overlay["judge_response_id"] = r["response_id"]
        save_json(os.path.join(out, "overlay.json"), overlay)
        print(f"[judge] {tag}: approx_ok={overlay['n_approximate_ok']} violations={overlay['violations']} sec={r['sec']}")
        for e in overlay["entries"]:
            print("   ", e["concept"], [s["surface"] for s in e["surfaces"]], "llm=", e["llm_decision"], "final=", e["final_decision"], e["downgrade_reasons"])


def step_rebuild():
    """保存済みresponse.jsonから、現行の決定論検証でoverlayを再構築する(API 0)。"""
    for dp, _d, fns in os.walk(os.path.join(ROOT, "judge")):
        if "response.json" in fns:
            tag = os.path.basename(dp)
            src = {"A_rep1": "A", "A_rep2": "A", "A_med": "A"}.get(tag, tag)
            r = load_json(os.path.join(dp, "response.json"))
            d = load_source(src)
            o = ov.build_overlay(d["sidecar"], r["parsed"])
            o["source"], o["judge_model"], o["judge_response_id"], o["effort"] = src, r["model"], r["response_id"], r.get("effort")
            save_json(os.path.join(dp, "overlay.json"), o)
            print("[rebuild]", tag, "approx_ok=", o["n_approximate_ok"], [(e["concept"], e["llm_decision"], e["final_decision"]) for e in o["entries"] if e["llm_decision"] != e["final_decision"]])


# ------------------------------------------------------------------ writer
def step_writer(arm):
    d = os.path.join(ROOT, arm)
    cl.install(os.path.join(d, "raw_usage_log.jsonl"))
    client = vfl01.get_client()
    a = contract.validate_annotated_b3(d)
    story, _ = w1.parse_brief_md(a.annotated_md_text)
    before_news = a.news_field_text
    before_prompt = w1.build_r0_prompt(story, before_news)
    meta0 = load_json(os.path.join(RUN_A, "ja_writer", "factlock", "r0_meta.json"))
    assert sha_text(before_prompt) == meta0["r0_prompt_sha256"], "Before R0 prompt not reproducible"
    info = {"arm": arm, "before_r0_prompt_sha256": sha_text(before_prompt),
            "w1_module_sha256": sha_file(w1.__file__), "overlay_module_sha256": sha_file(ov.__file__)}
    if arm == "after":
        overlay = load_json(os.path.join(ROOT, "judge", "A_rep1", "overlay.json"))
        after_news = ov.apply_to_news_field(a.facts_text, a.constraints_text, overlay, prod.CONS_HEADING, prod.compose_news_field)
        orig = w1.build_r0_prompt

        def patched(storyline_line, brief_facts_text):
            assert brief_facts_text == before_news, "unexpected news field"
            return ov.apply_rule8(orig(storyline_line, after_news), overlay)
        w1.build_r0_prompt = patched      # Trial runner process内のみ。ファイルは無改変
        info["after_r0_prompt_sha256"] = sha_text(patched(story, before_news))
        info["overlay_n_approximate_ok"] = overlay["n_approximate_ok"]
    else:
        info["after_r0_prompt_sha256"] = None
    guard(f"before writer {arm}")
    t0 = time.time()
    res = w1.run_w1_writer(d, client=client, budget_check=lambda: guard(f"writer {arm}"))
    info["sec"] = round(time.time() - t0, 1)
    ev = res["runtime_evidence"]
    info["r0_prompt_sha256_used"] = load_json(os.path.join(d, "ja_writer", "factlock", "r0_meta.json"))["r0_prompt_sha256"]
    info["r0_marks_echoed"] = load_json(os.path.join(d, "ja_writer", "factlock", "r0_meta.json"))["marks_echoed"]
    info["models"] = {"r0": ev["original"]["model"], "r1": ev["r1"]["model"], "r2": ev["r2"]["model"]}
    save_json(os.path.join(d, "trial_writer_info.json"), info)
    print("[writer]", arm, json.dumps(info, ensure_ascii=False))


# ------------------------------------------------------------------ en
def step_en():
    d = os.path.join(ROOT, "after")
    cl.install(os.path.join(d, "raw_usage_log.jsonl"))
    client = vfl01.get_client()
    ja_text = open(os.path.join(d, "ja_writer", "revision2.md"), encoding="utf-8").read()
    ledger_text = open(os.path.join(d, "research_ledger", "verified_fact_ledger.txt"), encoding="utf-8").read()
    ep = load_json(os.path.join(RUN_A, "entry_point.json"))["args"]
    theme = {"theme_id": ep["slug"], "topic": ep["theme"], "out_dir": d, "ledger_path": os.path.join(d, "research_ledger", "verified_fact_ledger.txt")}
    for only in ("advanced", "standard"):
        guard(f"before {only}")
        with cl.logging_context(runner.RUNNER_TAG, only):
            efam.run_writer_stage(client, theme, ja_text, ledger_text, 90.0, only=only)
        print("[en]", only, "done")


# ------------------------------------------------------------------ check (LDC + RF)
def step_check():
    cl.install(os.path.join(ROOT, "check", "raw_usage_log.jsonl"))
    client = vfl01.get_client()
    targets = {
        "after_ja": os.path.join(ROOT, "after", "ja_writer", "revision2.md"),
        "after_b1b": os.path.join(ROOT, "after", "b1b", "article.md"),
        "after_a2": os.path.join(ROOT, "after", "a2", "article.md"),
        "before_ja": os.path.join(RUN_A, "ja_writer", "revision2.md"),
        "before_b1b": os.path.join(RUN_A, "b1b", "article.md"),
        "before_a2": os.path.join(RUN_A, "a2", "article.md"),
        "control_ja": os.path.join(ROOT, "control", "ja_writer", "revision2.md"),
    }
    ledger_text = open(os.path.join(RUN_A, "research_ledger", "verified_fact_ledger.txt"), encoding="utf-8").read()
    for k, p in targets.items():
        out = os.path.join(ROOT, "check", f"ldc_{k}.json")
        if os.path.exists(out) or not os.path.exists(p):
            print("[check] skip", k)
            continue
        guard(f"ldc {k}")
        art = open(p, encoding="utf-8").read()
        with cl.logging_context(THEME_TAG, f"ldc_{k}"):
            r = vfl01.run_deviation_check(client, ledger_text, art, hook_aware=True)
        save_json(out, {"article_path": p, "article_sha256": sha_text(art), "audit": vfl01.deviation_audit_record(r), "parsed": r["parsed"]})
        devs = r["parsed"].get("deviations", [])
        print(f"[check] ldc {k}: status={r['parsed'].get('overall_status')} n_dev={len(devs)}")
    for lvl in ("b1b", "a2"):
        p = os.path.join(ROOT, "after", lvl, "article.md")
        out = os.path.join(ROOT, "check", f"rf_after_{lvl}.json")
        if os.path.exists(out) or not os.path.exists(p):
            continue
        guard(f"rf after {lvl}")
        res = rf.run_risk_flagger(article_path=p, ledger_path=os.path.join(RUN_A, "research_ledger", "verified_fact_ledger.txt"),
                                  article_id=f"rounding_trial_after_{lvl}", article_level=lvl, out_dir=os.path.join(ROOT, "check", f"rf_{lvl}"),
                                  producer="deterministic_v2", run_label=THEME_TAG, record_entry_point=False,
                                  budget_check=lambda: guard("rf"))
        save_json(out, res)
        print(f"[check] rf after {lvl}: status={res['status']} issues={len(res['issues'])}")



SEMDIFF_SCHEMA = {
    "name": "blind_semantic_diff", "strict": True,
    "schema": {"type": "object", "properties": {
        "differences": {"type": "array", "items": {"type": "object", "properties": {
            "category": {"type": "string", "enum": ["NUMBER_EXPRESSION", "FACT_CONTENT", "STRUCTURE_TONE"]},
            "x_text": {"type": "string"}, "y_text": {"type": "string"}, "comment": {"type": "string"},
            "severity": {"type": "string", "enum": ["none", "minor", "major"]}},
            "required": ["category", "x_text", "y_text", "comment", "severity"], "additionalProperties": False}},
        "facts_preserved_in_both": {"type": "boolean"},
        "summary": {"type": "string"}},
        "required": ["differences", "facts_preserved_in_both", "summary"], "additionalProperties": False}}


def step_semdiff():
    """ラベル伏せの意味差分判定(gpt-6.1-sol, effort=medium)。X/Yの割付はpair idのsha256由来で固定し記録する。"""
    cl.install(os.path.join(ROOT, "semdiff", "raw_usage_log.jsonl"))
    client = vfl01.get_client()
    a = contract.validate_annotated_b3(RUN_A)
    brief = a.facts_text
    B = RUN_A
    pairs = {
        "P1_ja_after_vs_before": (os.path.join(ROOT, "after", "ja_writer", "revision2.md"), os.path.join(B, "ja_writer", "revision2.md")),
        "P2_ja_control_vs_before": (os.path.join(ROOT, "control", "ja_writer", "revision2.md"), os.path.join(B, "ja_writer", "revision2.md")),
        "P3_b1b_after_vs_before": (os.path.join(ROOT, "after", "b1b", "article.md"), os.path.join(B, "b1b", "article.md")),
        "P4_a2_after_vs_before": (os.path.join(ROOT, "after", "a2", "article.md"), os.path.join(B, "a2", "article.md")),
    }
    dev = ("あなたは記事の差分検査者です。2つの文書XとYの違いを、ラベルに頼らず本文だけから列挙し、分類します。"
           "どちらが新しいか・どちらが基準かは知らされていません。")
    for pid, (p_new, p_base) in pairs.items():
        out = os.path.join(ROOT, "semdiff", pid + ".json")
        if os.path.exists(out) or not os.path.exists(p_new):
            continue
        guard(f"semdiff {pid}")
        new_t, base_t = open(p_new, encoding="utf-8").read(), open(p_base, encoding="utf-8").read()
        swap = int(hashlib.sha256(pid.encode()).hexdigest(), 16) % 2 == 1
        X, Y = (base_t, new_t) if swap else (new_t, base_t)
        user = ("同じ事実素材(下記の採用Fact)から別々に作られた2つの記事XとYがあります。2つの違いを列挙してください。\n"
                "分類: NUMBER_EXPRESSION=数値の表現差(丸め・「約」の有無・単位表記など)、FACT_CONTENT=事実の追加・削除・範囲・確かさ・因果・比較方向の変化、"
                "STRUCTURE_TONE=構成・語り口・比喩・文順・分量などの差。FACT_CONTENTは採用Fact本文と照らして判断します。"
                "severityは、事実として誤りまたは読者に別の意味を伝えるものをmajor、表現差で意味が保たれるものをminor、無視できる差をnoneとします。"
                "「facts_preserved_in_both」は、XとYの両方が採用Factの範囲を逸脱していないかです。\n\n"
                f"【採用Fact】\n{brief}\n\n【文書X】\n{X}\n\n【文書Y】\n{Y}\n")
        with cl.logging_context(THEME_TAG, "semdiff_" + pid):
            resp = client.responses.create(model=routing.require_model("FAMILY_X_STORYLINE_B3", "gpt-6.1-sol"), reasoning={"effort": "medium"},
                                           text={"format": {"type": "json_schema", **SEMDIFF_SCHEMA}},
                                           input=[{"role": "developer", "content": dev}, {"role": "user", "content": user}])
        res = json.loads(resp.output_text)
        save_json(out, {"pair": pid, "X_is": "base(Before)" if swap else "new", "Y_is": "new" if swap else "base(Before)",
                        "new_path": p_new, "base_path": p_base, "model": resp.model, "response_id": resp.id, "result": res})
        cnt = {}
        for dd in res["differences"]:
            cnt[(dd["category"], dd["severity"])] = cnt.get((dd["category"], dd["severity"]), 0) + 1
        print("[semdiff]", pid, "facts_preserved_in_both=", res["facts_preserved_in_both"], cnt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", required=True, choices=("prep", "judge", "rebuild", "writer", "en", "check", "semdiff"))
    ap.add_argument("--arm", choices=("after", "control"))
    ap.add_argument("--only")
    a = ap.parse_args()
    os.makedirs(ROOT, exist_ok=True)
    if a.step == "prep":
        step_prep()
    elif a.step == "judge":
        step_judge(a.only)
    elif a.step == "rebuild":
        step_rebuild()
    elif a.step == "semdiff":
        step_semdiff()
    elif a.step == "writer":
        step_writer(a.arm)
    elif a.step == "en":
        step_en()
    elif a.step == "check":
        step_check()


if __name__ == "__main__":
    main()
