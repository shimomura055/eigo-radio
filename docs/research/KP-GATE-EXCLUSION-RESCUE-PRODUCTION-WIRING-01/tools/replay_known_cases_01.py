# -*- coding: utf-8 -*-
"""KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 委任_02: 既知事例のreplay(正式`er119_kp_candidates_01.generate_candidates`経由)。

固定する入力: 本文(case_fixtures_01.jsonの凍結本文)・選定LLM(call1/call2)の出力・canonicalization LLMの1回目の出力=fixture。
実LLM(実課金): H3の救済後のgloss強制再整合・QA再判定、gloss newgen(gloss未生成itemの意味生成)。Redundancy QAはstub(救済と無関係。API 0)。
実行: .venv\\Scripts\\python.exe docs\\research\\KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01\\tools\\replay_known_cases_01.py <case名|all> <out_root>
出力: <out_root>/<case>/replay_result.json(+候補ファイル一式)。cost loggerは<out_root>/<case>/raw_usage_log.jsonl。
"""
from __future__ import annotations

import json
import os
import sys
import time
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

WD = os.path.join(ROOT, "docs", "research", "KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01")
FX = {c["id"]: c for c in json.load(open(os.path.join(WD, "case_fixtures_01.json"), encoding="utf-8"))}


def body(case_id: int) -> str:
    t = FX[case_id]["text"]
    return t.split("【記事本文】\n", 1)[1] if "【記事本文】\n" in t else t


# case名 -> 定義。canon_keys: canonicalization(1回目)でLLMが返すkey(display_phrase->key)。未指定=display_phraseのまま
CASES = {
    # X: AI島 a2 Std本文。studied separately は区分1の是正で通常フローを通る(救済不要)/ too soon to wave a flag(6語)は短縮救済しない(不採用)
    # call1_attempts: 選定LLMの各attemptの出力(1回目に不適合な句を含め、機械診断後の2回目で除いた実運用に近い流れ。短縮救済しない=1回目はINVALID)
    "X_ai_island_a2": dict(family="X", level="a2", fixture=0, call1_attempts=[["studied separately", "too soon to wave a flag", "removing one memory"],
                                                                              ["studied separately", "removing one memory", "lowered its score"]],
                           call2=[], canon_keys={"studied separately": "study separately"}),
    # Y a2: it can't be helped(選定段=慣用句の核へ救済)/ redelivery fee(CMU未登録=分解救済しない)
    "Y_redelivery_a2": dict(family="Y", level="a2", fixture=9, call1_attempts=[["it can’t be helped", "redelivery fee", "tried to deliver it"],
                                                                                ["it can’t be helped", "tried to deliver it", "fix two things"]],
                            call2=[], canon_keys={}),
    # Y b1b(sns_age_limit本文): catch their interest(選定段=D1再アンカー)
    "Y_sns_b1b": dict(family="Y", level="b1b", fixture=13, call1_attempts=[["catch their interest", "have a say", "keep in touch with friends"]],
                      call2=[], canon_keys={}),
    # Z b1b(melos r3本文): rose above / held out(canonicalization段=M1窓内再導出)
    "Z_melos_b1b": dict(family="Z", level="b1b", fixture=5, call1_attempts=[["rose above", "held out", "threw himself into the flood"]],
                        call2=[], canon_keys={"rose above": "rise above the other voices", "held out": "hold out one's hands"}),
}


def _items_from_msg(msg: str):
    marker = "【Key Phrase候補(JSON)】\n"
    obj, _ = json.JSONDecoder().raw_decode(msg.split(marker, 1)[1].lstrip())
    return obj


def run_case(name: str, out_root: str) -> dict:
    import er003_key_words_canonicalization as kc
    import er003_key_words_gloss_alignment as ga
    import er003_v1_n3_01_scaffold_generate as sc
    import er005_cost_logger as cl
    import er105_kp_fulltext_selector_01 as ft
    import er119_kp_candidates_01 as kcand
    import er119_kp_human_review_01 as rv
    import er119_kp_prompt_2v_01 as p2v
    import er125_kp_rescue_production_01 as r125

    c = CASES[name]
    text = body(c["fixture"])
    out = os.path.join(out_root, name)
    os.makedirs(out, exist_ok=True)
    cl.install(os.path.join(out, "raw_usage_log.jsonl"))
    level = c["level"]
    process = "B1_SUPPORT" if level == "b1b" else "A2_SUPPORT"
    src_level = "B1" if level == "b1b" else "A2"
    real_make = kc.make_canonicalization_fn
    seen = {"main_calls": 0, "qa_calls": 0, "qa_msgs": [], "call1_n": 0}

    def sel_make(msg, **kw):
        k = min(seen["call1_n"], len(c["call1_attempts"]) - 1)
        seen["call1_n"] += 1

        def fn():
            return json.dumps({"items": [{"phrase": p, "word_count": len(p.split())} for p in c["call1_attempts"][k]]}, ensure_ascii=False), "REPLAY_FIXTURE", f"replay_call1_{k + 1}"
        return fn

    def vocab_make(msg, **kw):
        def fn():
            return json.dumps({"items": [{"phrase": p, "reason_ja": "replay", "word_count": len(p.split())} for p in c["call2"]]}, ensure_ascii=False), "REPLAY_FIXTURE", "replay_call2"
        return fn

    main_set = {"v": None}

    def canon_make(msg, **kw):
        items = _items_from_msg(msg)
        disp = [it["display_phrase"] for it in items]
        if main_set["v"] is None or disp == main_set["v"]:
            main_set["v"] = disp                     # 1回目の全候補canonicalization = fixture(LLMの出力を凍結)
            seen["main_calls"] += 1
            rows = []
            for it in items:
                key = c["canon_keys"].get(it["display_phrase"], it["display_phrase"])
                row = {"rank": it["rank"], "key_phrase": key, "changed_from_display_phrase": key != it["display_phrase"],
                       "normalization_reason": "lemma_normalization" if key != it["display_phrase"] else "none", "reasoning": "replay fixture",
                       "possessor_roles": []}
                for f in kc.QA_FIELDS:
                    row[f] = "PASS"
                rows.append(row)

            def fn():
                return json.dumps({"items": rows}, ensure_ascii=False), "REPLAY_FIXTURE", "replay_canon"
            return fn
        seen["qa_calls"] += 1                           # 救済後のQA再判定 = 実LLM(承認済みprompt/schema)
        seen["qa_msgs"].append(disp)
        return real_make(msg, **kw)

    def red_stub(text_, items, work, article_id, process=None):
        return {"status": "REDUNDANCY_PASS", "duplicate_pairs": [], "model_id": None, "response_id": None, "attempts_detail": [],
                "skipped": "replay: Redundancy QAは救済と無関係のためstub(API 0)"}

    src_fn = kcand.make_z_src_fn(text, level) if c["family"] == "Z" else None
    patches = [mock.patch.object(ft, "make_selector_fn", sel_make), mock.patch.object(p2v, "make_vocab_selector_fn", vocab_make),
               mock.patch.object(kc, "make_canonicalization_fn", canon_make), mock.patch("time.sleep", lambda s: None)]
    for p in patches:
        p.start()
    t0 = time.time()
    try:
        kp_dir = os.path.join(out, "key_phrases")
        person_fn = None
        if c["family"] == "Z":
            import er003_key_words_gloss_alignment as ga_
            def _align_factory(msg):
                from er006_model_routing_contract_01 import SUPPORT_MODEL
                return ga_.make_alignment_fn(msg, model=SUPPORT_MODEL)
            person_fn = kcand.make_person_repair_fn(text, _align_factory, os.path.join(kp_dir, "kp_candidates", "round_1", "work"), f"replay_{name}")
        res = kcand.generate_candidates(text, kp_dir, f"replay_{name}", src_level, level, 1, [], process=process, src_fn=src_fn,
                                        person_repair_fn=person_fn, redundancy_fn=red_stub, sleep_fn=lambda s: None)
    finally:
        for p in reversed(patches):
            p.stop()
    elapsed = round(time.time() - t0, 1)
    summary = {"case": name, "family": c["family"], "level": level, "fixture_id": c["fixture"], "ok": res.get("ok"), "elapsed_s": elapsed,
               "main_canon_calls_fixture": seen["main_calls"], "qa_rejudge_calls_real": seen["qa_calls"], "qa_rejudge_batches": seen["qa_msgs"],
               "kill_switch_env": os.environ.get("EIGO_KP_RESCUE"), "rescue_enabled": r125.rescue_enabled()}
    if res.get("ok"):
        doc = res["doc"]
        with open(os.path.join(out, "kp_candidates_doc.json"), "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
        summary["rescue_provenance"] = doc.get("rescue_provenance")
        summary["candidates"] = [{
            "ai_rank": x["ai_rank"], "origin": x["origin"], "selection_phrase": x["selection_phrase"], "used_form": x["used_form"],
            "auto_eligible": x["auto_eligible"], "rescued": bool((x.get("flags") or {}).get("rescued")), "rescue_note": x.get("rescue_note"),
            "rescue_codes": (x.get("rescue") or {}).get("codes"), "gates": x.get("gates"),
            "rescue_selection": (x.get("rescue") or {}).get("selection"),
            "rescue_canonicalization": ({k: v for k, v in ((x.get("rescue") or {}).get("canonicalization") or {}).items() if k != "reasons_before"} or None),
            "rescue_gloss": (x.get("rescue") or {}).get("gloss"), "rescue_qa": (x.get("rescue") or {}).get("qa"),
            "japanese_gloss": x.get("japanese_gloss"), "idiom_exception_flag": (x.get("flags") or {}).get("idiom_exception"),
            "verify_persisted_rescue": r125.verify_persisted_rescue(x), "reverify": r125.reverify_persisted_rescue(x)} for x in doc["candidates"]]
        summary["dropped"] = [{"phrase": d["phrase"], "stage": d["stage"], "reasons": d["reasons"]} for d in doc["dropped"]]
        summary["outer_retry_log"] = doc["outer_retry_log"]
        # resume読み戻し: 保存→同じ文書を読み戻して再計算なし(API 0)であることはcandidates_sha256の一致で示す
        saved = rv.save_candidates(kp_dir, dict(doc, text_sha256=rv.sha256_text(text), round=1))
        summary["candidates_sha256"] = saved["candidates_sha256"]
        summary["candidates_sha256_recomputed_equal"] = rv.candidates_sha256(rv.load_candidates(kp_dir)) == saved["candidates_sha256"]
    else:
        summary["failure"] = {k: res.get(k) for k in ("status", "outer_retry_log")}
    # cost
    try:
        cost = 0.0
        n = 0
        stages = {}
        with open(os.path.join(out, "raw_usage_log.jsonl"), encoding="utf-8") as f:
            for line in f:
                d = json.loads(line)
                n += 1
                stages[d.get("stage")] = stages.get(d.get("stage"), 0) + 1
                cost += float(d.get("cost_jpy") or 0)
        summary["api_calls_logged"] = n
        summary["api_calls_by_stage"] = stages
        summary["cost_jpy_logged"] = round(cost, 4)
    except OSError:
        summary["api_calls_logged"] = 0
    with open(os.path.join(out, "replay_result.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    return summary


if __name__ == "__main__":
    which, out_root = sys.argv[1], sys.argv[2]
    names = list(CASES) if which == "all" else [which]
    for n in names:
        s = run_case(n, out_root)
        print(json.dumps({k: s.get(k) for k in ("case", "ok", "api_calls_logged", "api_calls_by_stage", "cost_jpy_logged", "qa_rejudge_calls_real")}, ensure_ascii=False))
