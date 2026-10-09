# -*- coding: utf-8 -*-
"""FACTLOCK-ASTRA-E2E-TRIAL-01 委任_05: G0 dry-run / 単体テスト用のAPI stub(API生成支出0)。

Production/Trial経路には混入しない: er052_factlock_astra_e2e_runner_01.py が環境変数 E2E_STUB=1 のときだけ
install_all() を呼ぶ。stubは(1)OpenAI client(Astra / 構造化JSON出力のみ)、(2)jaw.call_fresh /
jaw.call_with_previous_response_id、(3)vfl01.run_deviation_check、(4)efam._run_writer_stage_once、
(5)Checker 1 run を差し替える。jaw.run_ja_writer_o_r1_r2(must-fix・記号Gate込み)と
fl.untagged_check 等は本物のコードを通す。stubが想定外のAPI経路(研究・B3・未知model)を踏んだら例外にする。
シナリオ(環境変数 E2E_STUB_SCENARIO=JSON文字列またはJSONファイルpath):
  {"ja_recheck": {"<arm>": n},      # ENの初回n回が JARecheckRequiredError(ja_source MAJOR)
   "fc_major": {"<stage tag>": n},  # 当該stage tagのFC初回n回がMAJOR(old: ja_original_check / ja_r2_check, new: new_r2_fc)
   "force_research_call": true,     # EN stubが研究関数を呼ぶ((m)即停止のテスト)
   "force_web_search_row": true,    # raw_usage_logにweb_search行を書く((m)ログ検出のテスト)
   "en_attempt1_summary_major": true,  # Advanced attempt1に「要約のみのMAJOR」を書く(影の対照M1(b)のテスト)
   "checker_final_state": {"<theme>_<arm>_<level>": "STAGE4_ESCALATION"}}
stubの費用行は実単価で計算できる体裁(Luna: 1000/200 tok、Astra: 700/1500 tok)。値はstub(実測ではない)。
"""
from __future__ import annotations

import json
import os
import re
import time

import er005_cost_logger as cl

STUB_NOTE = "stub: 値は実測ではない(API生成支出0)"
JA_TEXT = ("スタブの題名\n\n試験用の本文です。【事実1】二つ目の文です。【事実2】どう思いますか。"
           "\n\n三つ目の段落です。【事実3】終わりです。")
TOK = {"luna": (1000, 200), "astra": (700, 1500)}


class StubUnexpectedCall(RuntimeError):
    pass


def strip_fact_tags(t: str) -> str:
    return re.sub(r"【事実\d+】", "", t)


def scenario() -> dict:
    raw = os.environ.get("E2E_STUB_SCENARIO", "")
    if not raw:
        return {}
    if os.path.exists(raw):
        with open(raw, encoding="utf-8") as f:
            return json.load(f)
    return json.loads(raw)


def counter_next(key: str) -> int:
    """E2E_STUB_DIR配下のカウンタ(呼び出し回数、プロセス再起動をまたぐ)。1始まりで返す。"""
    d = os.environ.get("E2E_STUB_DIR") or "."
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, ".stub_counters.json")
    c = {}
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            c = json.load(f)
    c[key] = c.get(key, 0) + 1
    with open(p, "w", encoding="utf-8") as f:
        json.dump(c, f)
    return c[key]


class _U:
    def __init__(self, i, o):
        self.input_tokens, self.output_tokens, self.total_tokens = i, o, i + o
        self.input_tokens_details = type("D", (), {"cached_tokens": 0})()
        self.output_tokens_details = type("D", (), {"reasoning_tokens": 0})()


class StubResp:
    def __init__(self, text, model, kind="luna", rid=None):
        self.output_text, self.model = text, model
        self.id = rid or f"stub_{kind}_{int(time.time() * 1000) % 10 ** 9}"
        self.usage = _U(*TOK[kind])
        self.output = []
        self.status = "completed"


def log_row(model: str, kind: str = "luna", success: bool = True, web_search: int = 0) -> None:
    """cl.record(実cost loggerと同じ形の行)。cl.init_logger未設定なら何もしない。"""
    if getattr(cl, "_LOG_PATH", None) is None:
        return
    i, o = TOK[kind]
    cl.record({"provider": "openai", "api": "responses.create", "model_id": model, "attempt_number": 1, "success": success,
               "elapsed_seconds": 0.0, "usage_source": "STUB", "web_search_call_count": web_search,
               "input_tokens": i, "output_tokens": o, "cached_input_tokens": 0, "stub": True})


class _Responses:
    def create(self, **kw):
        model = kw.get("model", "")
        fmt = ((kw.get("text") or {}).get("format") or {}).get("name")
        if str(model).startswith("gpt-6-astra"):
            if "previous_response_id" in kw:
                raise StubUnexpectedCall("Astra呼び出しにprevious_response_idは使わない")
            log_row("gpt-6-astra", "astra")
            return StubResp(strip_fact_tags(JA_TEXT), "gpt-6-astra-stub", "astra")
        if fmt == "factlock_untagged_check":
            prompt = kw["input"][-1]["content"]
            idx = [int(m) for m in re.findall(r"^\[(\d+)\]", prompt.split("【タグなし文】")[-1], flags=re.M)]
            log_row("gpt-6-luna")
            return StubResp(json.dumps({"items": [{"sentence_index": i, "label": "neutral", "reason": "stub"} for i in idx]}),
                            "gpt-6-luna")
        raise StubUnexpectedCall(f"stubが想定しないAPI呼び出し: model={model!r} format={fmt!r}")


class StubClient:
    def __init__(self):
        self.responses = _Responses()


def stub_deviation(client, verified_ledger_text, article_text, model=None, hook_aware=False, prior_issues=None,
                   include_related_fact_id=False, source_article_text=None):
    stage = (cl._CONTEXT.get("stage") if hasattr(cl, "_CONTEXT") else None) or "unknown"
    n = counter_next(f"fc:{stage}")
    major = n <= int((scenario().get("fc_major") or {}).get(stage, 0))
    devs = []
    if major:
        devs = [{"severity": "MAJOR", "origin": "ja_source", "related_fact_id": "ZZ-001", "claim_in_article": "スタブの誤り",
                 "issue": "stub issue", "explanation": "stub"}]
    parsed = {"overall_status": "LEDGER_DEVIATION" if major else "LEDGER_COMPLIANT", "deviations": devs,
              "all_prior_issues_resolved": (not major) if prior_issues else True}
    log_row("gpt-6-luna")
    return {"prompt": "stub", "raw_text": json.dumps(parsed), "parsed": parsed, "response_id": "stub_fc", "model": "gpt-6-luna",
            "usage": {"input_tokens": TOK["luna"][0], "output_tokens": TOK["luna"][1]}, "elapsed_seconds": 0.0,
            "hook_aware": hook_aware}


def stub_call_fresh(client, developer, user, effort, stage):
    log_row("gpt-6-luna")
    return StubResp(JA_TEXT, "gpt-6-luna", rid=f"stub_fresh_{stage}")


def stub_call_prev(client, user, effort, previous_response_id, stage):
    log_row("gpt-6-luna")
    return StubResp(strip_fact_tags(JA_TEXT), "gpt-6-luna", rid=f"stub_prev_{stage}")


def _en_article(title: str, level: str) -> str:
    body = "\n\n".join(f"This is stub paragraph {i}." for i in (1, 2, 3))
    return f"# {title}\n\n{body}" + ("\n\n## In one line\nStub summary." if level == "advanced" else "")


def stub_run_writer_stage_once(client, theme, ja_text, ledger_text, budget_jpy, only=None):
    """efam._run_writer_stage_once のstub。ファイル構造・audit出力は本物と同じキーで最小限を書く。"""
    import er012_e_family_entertainment_two_level_runner_01 as efam
    arm = os.environ.get("E2E_ARM", "?")
    if scenario().get("force_research_call"):
        efam.run_researcher_for_topic(client, "stub topic")      # (m)テスト: 研究関数を踏ませる(shimのguardが止める)
    out = theme["out_dir"]
    ev = {}
    for level, key, dname in (("advanced", "advanced", "b1b"), ("standard", "standard", "a2")):
        if only not in (None, key):
            continue
        n = counter_next(f"en:{arm}:{key}")
        if key == "advanced" and n <= int((scenario().get("ja_recheck") or {}).get(arm, 0)):
            raise efam.JARecheckRequiredError(
                stage=key, message="[STOP] JA_RECHECK_REQUIRED(stub)",
                major_deviations=[{"origin": "ja_source", "severity": "MAJOR", "related_fact_id": "ZZ-001",
                                   "claim_in_article": "スタブ", "issue": "stub", "explanation": "stub"}])
        with cl.logging_context("STUB_EN", key):
            log_row("gpt-6-luna")
            log_row("gpt-6-luna")
        text = _en_article("Stub title", level)
        efam.save_text(f"{out}/{dname}/article.md", text)
        efam.save_json(f"{out}/{dname}/parts.json", {"status": "OK", "paragraph_count": 3, "title": "Stub title"})
        devs = []
        if key == "advanced" and scenario().get("en_attempt1_summary_major"):
            devs = [{"severity": "MAJOR", "origin": "translation", "related_fact_id": "ZZ-001", "claim_in_article": "Stub summary.",
                     "issue": "stub", "explanation": "stub"}]
        att = {"prompt": "stub", "raw_text": "{}", "parsed": {"overall_status": "LEDGER_DEVIATION" if devs else "LEDGER_COMPLIANT",
                                                             "deviations": devs},
               "response_id": "stub", "model": "gpt-6-luna", "usage": {}, "elapsed_seconds": 0.0, "hook_aware": False}
        efam.save_json(f"{out}/{dname}/audit/deviation_checks/{key}_attempt1.json", att)
        efam.save_json(f"{out}/{dname}/audit/deviation_check.json", att["parsed"])
        ev[key] = {"model_id_actual": "gpt-6-luna", "fallback_detected": False, "retried_for_deviation": False, "must_fix_used": [],
                   "deviation_overall_status": "LEDGER_COMPLIANT", "stub": True, "env_OPEN243_M1": os.environ.get("OPEN243_M1")}
    sp = f"{out}/writer_run_summary.json"
    merged = {**(efam.load_json(sp) if os.path.exists(sp) else {}), **ev}
    efam.save_json(sp, merged)
    if scenario().get("force_web_search_row"):
        log_row("gpt-6-luna", web_search=1)
    return ev


def stub_in_one_line(client, title, body, *, model=None, ja_text=None, ledger_text=None, must_fix=None):
    log_row("gpt-6-luna")
    return {"text": "Stub alternative summary text.", "m1_inputs": ja_text is not None}


def stub_translate(ja_text, *a, client=None, model=None, must_fix=None, **k):
    log_row("gpt-6-luna")
    return type("R", (), {"title": "Stub title", "body": "Stub body one.\n\nStub body two.\n\nStub body three."})()


def stub_check_one(inst: dict, arm: str) -> dict:
    iid = inst["instance_id"]
    fs = (scenario().get("checker_final_state") or {}).get(iid, "RESOLVED_STAGE2_DOWNGRADE")
    protect = os.environ.get("OPEN233_RECLASSIFY_PROTECT_FLAGS", "")
    return {"instance_id": iid, "group": "e2e", "final_state": fs,
            "stage4_reason": "stub" if fs == "STAGE4_ESCALATION" else None,
            "cycles": [], "stage1_call_used": True, "stage1_recall_miss_substituted": False, "call_log": [],
            "total_cost_jpy": 3.5, "total_calls": 0, "elapsed_seconds": 0.0, "stub": True,
            "stage1_coverage": {"union_candidates": [], "n_union_candidates": 0, "candidate_filter": {
                "status": "ok", "n_protected_keys": 1 if protect else 0, "n_excluded_claims": 2, "verdicts": []}},
            "stage1_reclassify": {"reclassify_status": "ok", "n_protected_keys": 1 if protect else 0, "n_excluded_claims": 2},
            "residual_at_pass": {"defs": []}, "waste_flags": [], "provenance_violations": [], "env_protect_flags": protect}


def install_all() -> list:
    """stubを差し込み、差し込んだ名前のlistを返す。研究/B3関数は触らない(runner側guardが担当)。"""
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er012_e_family_entertainment_two_level_runner_01 as efam
    import er019_family_x_ja_writer_o_r1_r2_01 as jaw
    import er003_v1_n3_01_advanced_adaptation_generate as adv_gen
    adv_gen.generate_family_x_in_one_line = stub_in_one_line
    adv_gen.generate_family_x_faithful_translation = stub_translate
    vfl01.get_client = lambda: StubClient()
    vfl01.run_deviation_check = stub_deviation
    jaw.call_fresh = stub_call_fresh
    jaw.call_with_previous_response_id = stub_call_prev
    efam._run_writer_stage_once = stub_run_writer_stage_once
    return ["vfl01.get_client", "vfl01.run_deviation_check", "jaw.call_fresh", "jaw.call_with_previous_response_id",
            "efam._run_writer_stage_once"]
