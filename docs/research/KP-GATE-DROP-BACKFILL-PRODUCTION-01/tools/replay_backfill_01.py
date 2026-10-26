# -*- coding: utf-8 -*-
"""KP-GATE-DROP-BACKFILL-PRODUCTION-01 委任_03: Gate除外->補完の既知事例replay(正式`er119_kp_candidates_01.generate_candidates`経由)。

凍結(fixture): 本文・call1(Prompt 2)の返答・call2(Prompt 2-V)の初回返答・canonicalization(全候補)の初回返答=元のHR候補docから再構成した初回出力。
実LLM(実課金): 補完call(Prompt 2-V 2回目)・補完分/再試行のcanonicalization・gloss整合・救済後のQA再判定・Redundancy QA。
KPI provenance: replay=凍結初回出力+実LLM補完(freshと混ぜない)。
実行: .venv\\Scripts\\python.exe docs\\research\\KP-GATE-DROP-BACKFILL-PRODUCTION-01\\tools\\replay_backfill_01.py <case名|all> <out_root>
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

FXP = os.path.join(ROOT, "docs", "research", "KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01", "case_fixtures_01.json")
FX = {c["id"]: c for c in json.load(open(FXP, encoding="utf-8"))}


def _fx_body(i: int) -> str:
    t = FX[i]["text"]
    return t.split("【記事本文】\n", 1)[1] if "【記事本文】\n" in t else t


def _read(p: str) -> str:
    return open(os.path.join(ROOT, p), encoding="utf-8").read()


# case: family/level/text取得/凍結元doc(HR候補doc)/任意のsynthetic注入(call2初回返答への追加)
CASES = {
    "R1_X_ai_island_a2": dict(family="X", level="a2", text=lambda: _fx_body(0), doc="er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01/a2/key_phrases/kp_candidates.json"),
    "R2_X_uk_a2": dict(family="X", level="a2", text=lambda: _read("er019_output/uk_train_speaker_playback/run_kprescue_ev_01/a2/article.md"),
                       doc="er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_kprescue_ev_01/a2/key_phrases/kp_candidates.json",
                       inject_call2=["a fine of up to £1,000"], note="synthetic: 凍結call2へ数字を含む句を1件追加(元の数字除外事例のrun docが無いため。Production Gate(validate)の動作確認)"),
    "R3_Y_redelivery_a2": dict(family="Y", level="a2", text=lambda: _fx_body(9), doc="er121_output/family_y_production_01/redelivery_fee/run_01/key_phrases/a2/kp_candidates.json"),
    "R4_Y_sns_b1b": dict(family="Y", level="b1b", text=lambda: _fx_body(13), doc="er121_output/family_y_production_01/sns_age_limit/run_01/key_phrases/b1b/kp_candidates.json"),
    "R6_Z_melos_b1b": dict(family="Z", level="b1b", text=lambda: _fx_body(5), doc="er026_output/family_z_production_e2e_01/melos/run_p2_evidence_r3/key_phrases/b1b/kp_candidates.json"),
}


def _monkeys_text():
    import er026_family_z_fiction_production_runner_01 as z
    return z.canonical_article_text(_read("er026_output/family_z_production_e2e_01/the_monkeys_paw/run_sf_prod_01/writer/r2.md"))


CASES["R5a_Z_monkeys_paw_b1b_frozen_only"] = dict(
    family="Z", level="b1b", text=_monkeys_text,
    doc="docs/research/KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01/runs/monkeys_paw__b1b__current__r1/trial_result.json",
    note="凍結元=KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01の現行方式(Prompt 2+2-V)run。本文sha=run_sf_prod_01 r2.mdのcanonical_article_text(8388280a…)と一致。runnerのseed provenance不一致(後述)のため正式runner経由のfreshは不可")


def register_case(name, **kw):
    CASES[name] = kw


def frozen_from_doc(doc_path: str):
    d = json.load(open(os.path.join(ROOT, doc_path), encoding="utf-8"))
    if "candidates" not in d and "doc" in d:          # trial_result.json形式
        d = d["doc"]
    cands = d["candidates"]
    call1 = [c for c in sorted(cands, key=lambda x: x["ai_rank"]) if c["origin"] == "call1"]
    call1_phr = [c["selection_phrase"] for c in call1]
    for x in d["dropped"]:                            # call1でGate除外された句(canonicalization等)も初回返答に含める
        if x.get("origin") == "call1":
            call1_phr.append(x["phrase"])
    # call2初回返答: dropped(origin=call2, raw_rank)と候補(origin=call2)を合成。候補はraw_rankの空き位置へai_rank順
    c2c = [c for c in sorted(cands, key=lambda x: x["ai_rank"]) if c["origin"] == "call2"]
    ranks = {x["raw_rank"]: x["phrase"] for x in d["dropped"] if x.get("origin", "call2") == "call2" and x.get("raw_rank")}
    total = len(c2c) + len(ranks)
    out, it = [], iter([c["selection_phrase"] for c in c2c])
    for pos in range(1, max(total, max(ranks) if ranks else 0) + 1):
        out.append(ranks[pos] if pos in ranks else next(it, None))
    call2 = [p for p in out if p]
    keys = {}
    for c in cands:
        fl = c.get("flags") or {}
        if fl.get("rescued"):
            sel = (c.get("rescue") or {}).get("selection") or {}
            orig = sel.get("original_phrase")
            if orig:
                keys[orig] = (c.get("rescue") or {}).get("canonicalization", {}).get("llm_key") or orig
            continue
        keys[c["selection_phrase"]] = c["used_form"]
    for x in d["dropped"]:
        m = re.search(r"key_phrase\((?:'|\")(.+?)(?:'|\")\)", " ".join(x.get("reasons") or []))
        if x.get("stage") == "canonicalization" and m:
            keys[x["phrase"]] = m.group(1)
    return call1_phr, call2, keys, d


def _items_from_msg(msg: str):
    marker = "【Key Phrase候補(JSON)】\n"
    obj, _ = json.JSONDecoder().raw_decode(msg.split(marker, 1)[1].lstrip())
    return obj


def run_case(name: str, out_root: str) -> dict:
    import er003_key_words_canonicalization as kc
    import er105_kp_fulltext_selector_01 as ft
    import er005_cost_logger as cl
    import er119_kp_candidates_01 as kcand
    import er119_kp_human_review_01 as rv
    import er119_kp_prompt_2v_01 as p2v

    c = CASES[name]
    text = c["text"]() if callable(c["text"]) else c["text"]
    call1, call2, keys, srcdoc = frozen_from_doc(c["doc"])
    call2 = list(c["call2_override"]) if c.get("call2_override") else call2 + list(c.get("inject_call2") or [])
    out = os.path.join(out_root, name)
    os.makedirs(out, exist_ok=True)
    cl.install(os.path.join(out, "raw_usage_log.jsonl"))
    level = c["level"]
    process = "B1_SUPPORT" if level == "b1b" else "A2_SUPPORT"
    src_level = "B1" if level == "b1b" else "A2"
    real_vocab, real_canon = p2v.make_vocab_selector_fn, kc.make_canonicalization_fn
    seen = {"vocab_calls": 0, "canon_calls": 0, "bf_raw": None, "bf_msg": None, "canon_real_sets": []}

    def sel_make(msg, **kw):
        def fn():
            return json.dumps({"items": [{"phrase": p, "word_count": len(p.split())} for p in call1]}, ensure_ascii=False), "REPLAY_FIXTURE", "replay_call1"
        return fn

    def vocab_make(msg, **kw):
        seen["vocab_calls"] += 1
        if seen["vocab_calls"] == 1:              # 初回返答=凍結
            def fn():
                return json.dumps({"items": [{"phrase": p, "reason_ja": "replay", "word_count": len(p.split())} for p in call2]}, ensure_ascii=False), "REPLAY_FIXTURE", "replay_call2"
            return fn
        real = real_vocab(msg, **kw)                   # 補完call=実LLM(Prompt 2-V、routing契約どおり)
        seen["bf_msg"] = msg

        def fn2():
            r = real()
            seen["bf_raw"] = r[0]
            seen["bf_model"] = r[1]
            return r
        return fn2

    def canon_make(msg, **kw):
        seen["canon_calls"] += 1
        items = _items_from_msg(msg)
        if seen["canon_calls"] == 1:                   # 初回の全候補canonicalization=凍結
            rows = []
            for it in items:
                key = keys.get(it["display_phrase"], it["display_phrase"])
                row = {"rank": it["rank"], "key_phrase": key, "changed_from_display_phrase": key != it["display_phrase"],
                       "normalization_reason": "lemma_normalization" if key != it["display_phrase"] else "none", "reasoning": "replay fixture",
                       "possessor_roles": []}
                for f in kc.QA_FIELDS:
                    row[f] = "PASS"
                rows.append(row)

            def fn():
                return json.dumps({"items": rows}, ensure_ascii=False), "REPLAY_FIXTURE", "replay_canon"
            return fn
        seen["canon_real_sets"].append([it["display_phrase"] for it in items])
        return real_canon(msg, **kw)

    src_fn = kcand.make_z_src_fn(text, level) if c["family"] == "Z" else None
    patches = [mock.patch.object(ft, "make_selector_fn", sel_make), mock.patch.object(p2v, "make_vocab_selector_fn", vocab_make),
               mock.patch.object(kc, "make_canonicalization_fn", canon_make)]
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
                                        person_repair_fn=person_fn)
    finally:
        for p in reversed(patches):
            p.stop()
    summary = {"case": name, "family": c["family"], "level": level, "ok": res.get("ok"), "elapsed_s": round(time.time() - t0, 1),
               "frozen": {"call1": call1, "call2": call2, "canon_keys_n": len(keys), "source_doc": c["doc"], "note": c.get("note")},
               "vocab_calls": seen["vocab_calls"], "canon_calls": seen["canon_calls"], "canon_real_sets": seen["canon_real_sets"],
               "backfill_raw": seen["bf_raw"], "backfill_model": seen.get("bf_model")}
    if res.get("ok"):
        doc = res["doc"]
        with open(os.path.join(out, "kp_candidates_doc.json"), "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
        summary["backfill"] = doc.get("backfill")
        summary["shortfall_detail"] = doc.get("shortfall_detail")
        summary["candidates"] = [{"ai_rank": x["ai_rank"], "origin": x["origin"], "kind": x.get("kind"), "selection_phrase": x["selection_phrase"],
                                  "used_form": x["used_form"], "auto_eligible": x["auto_eligible"], "rescued": bool((x.get("flags") or {}).get("rescued")),
                                  "rescue_codes": (x.get("rescue") or {}).get("codes"), "gates": x.get("gates")} for x in doc["candidates"]]
        summary["dropped"] = [{"phrase": d["phrase"], "stage": d["stage"], "origin": d.get("origin"), "reasons": d["reasons"]} for d in doc["dropped"]]
        summary["outer_retry_log"] = doc["outer_retry_log"]
        saved = rv.save_candidates(kp_dir, dict(doc, text_sha256=rv.sha256_text(text), round=1))
        summary["candidates_sha256"] = saved["candidates_sha256"]
    else:
        summary["failure"] = {k: res.get(k) for k in ("status", "outer_retry_log")}
    cost, n, stages, models = 0.0, 0, {}, {}
    try:
        for line in open(os.path.join(out, "raw_usage_log.jsonl"), encoding="utf-8"):
            d = json.loads(line)
            n += 1
            stages[d.get("stage")] = stages.get(d.get("stage"), 0) + 1
            mk = d.get("model_id") or d.get("model")
            models[mk] = models.get(mk, 0) + 1
            cost += float(d.get("cost_jpy") or 0)
    except OSError:
        pass
    summary.update(api_calls_logged=n, api_calls_by_stage=stages, models=models, cost_jpy_logged=round(cost, 4))
    with open(os.path.join(out, "replay_result.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    return summary


# R5b: R5aの凍結call2のうちsergeant-majorを`interferes`に置換(Trial-02 COMPARISON_02:111のduplicate_of_top3事例の再現。synthetic)
CASES["R5b_Z_monkeys_paw_b1b_dup_inject"] = dict(CASES["R5a_Z_monkeys_paw_b1b_frozen_only"], call2_override=["pay off", "compensation", "snatched", "interferes", "rattled"],
                                                  note="synthetic: 凍結call2のsergeant-majorを`interferes`へ置換(duplicate_of_top3の再現。元事例=KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02/COMPARISON_02.md:111)")


if __name__ == "__main__":
    which, out_root = sys.argv[1], sys.argv[2]
    names = list(CASES) if which == "all" else [which]
    for n in names:
        s = run_case(n, out_root)
        print(json.dumps({k: s.get(k) for k in ("case", "ok", "api_calls_logged", "api_calls_by_stage", "cost_jpy_logged", "models")}, ensure_ascii=False), flush=True)
