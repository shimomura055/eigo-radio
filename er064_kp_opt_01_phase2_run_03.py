# ============================================================
# er064_kp_opt_01_phase2_run_03.py  (KP-OPT-01 委任_03 / Phase 2 最小有料Trial、Trial専用・Production非接続)
# C0=現行Prompt+current shortlist / C1=現行Prompt+alt_precision_guarded / C2=改善Prompt(prompt_after_02)+guarded /
# C2p=改善Prompt+方式2 V2 shortlist(Phase D成果物、注釈なし)。選定/gate/canonicalization/Redundancy QAはProduction関数。
# 使い方: PYTHONPATH=. .venv/Scripts/python.exe er064_kp_opt_01_phase2_run_03.py --stage prep1|prep2|prep3|1|2|3
# timeout/監督ループ/自動retryなし。各stageは1回だけ手動起動。
# ============================================================
from __future__ import annotations

import argparse
import concurrent.futures as cf
import glob
import hashlib
import json
import os
import sys
import threading
import time

sys.path.insert(0, os.getcwd())
import er003_b1_p2_keywords as bk  # noqa: E402
import er009_n1_routing_governance_10_actual_model_cost as pricing  # noqa: E402
import er030_key_phrase_db_hybrid_selector_01 as selector01  # noqa: E402
import er030_key_phrase_db_hybrid_source_reference_contract_01 as src_ref  # noqa: E402
import er003_key_words_production as prod  # noqa: E402
import er064_kp_idiom_trial_01_matcher as M  # noqa: E402
import er064_kp_idiom_trial_01_pipeline as P  # noqa: E402
import er064_kp_idiom_trial_01_select as S  # noqa: E402
import er064_kp_opt_01_prompt_build_02 as PB  # noqa: E402
import er064_kp_opt_01_upstream_core as U  # noqa: E402

core = U.core
ROOT = "er064_output/kp_extraction_selection_opt_01"
OUT = ROOT + "/phase2"
FIX = ROOT + "/phase1_fix"
BUDGET, STOP_RULE, JOB_CAP = 50.0, 48.0, 2.5
N = 3
STAGE_EST = {1: 18.72, 2: 12.93, 3: 12.93}
STAGE_ARTICLE = {1: "coffee", 2: "meta", 3: "hormuz"}
LEVELS = ("std", "adv")
STATE_FILES = ["er005_output/cost_baseline_01/cost_summary.json", "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl",
               "er006_output/master_audio_store_01/manifest.json", "er006_output/master_audio_store_01/reuse_telemetry.jsonl",
               "er006_output/pronunciation_ledger_01/ledger.json", "er011_output/attempt_history.jsonl",
               "er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl",
               "er025_output/pronunciation_resolution_core_telemetry_01/telemetry.jsonl"]
_W = "er019_output/family_x_audio_production_wiring_01"
PROD_PROMPT = {"coffee_std": _W + "/coffee_prices__run_v5_ms_01/a2/key_phrases/key_phrases_db_hybrid/keywords_selector_prompt.txt",
               "coffee_adv": _W + "/coffee_prices__run_v5_ms_01/b1b/key_phrases/key_phrases_db_hybrid/keywords_selector_prompt.txt",
               "meta_std": _W + "/meta__run_03/a2/key_phrases/key_phrases_db_hybrid/keywords_selector_prompt.txt",
               "meta_adv": _W + "/meta__run_03/b1b/key_phrases/key_phrases_db_hybrid/keywords_selector_prompt.txt"}
V2_CAND = "er064_output/kp_idiom_trial_01/phase_d/m1_recheck_02/coffee_adv/run1/accepted_candidates.json"
V2_ART = "er064_output/kp_idiom_trial_01/phase_a/inputs/v4_adv_article.md"
STOP_EVT = threading.Event()


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def stop_present():
    return (glob.glob(f"{OUT}/STOP") + glob.glob("docs/pm/delegation_log/*STOP_NOTICE*FAMILY-X-KP*")
            + glob.glob("er026_output/family_z_production_e2e_01/STOP_ALL"))


def real_title(key):
    return U.read_article(key).lstrip().splitlines()[0].lstrip("#").strip()


# ---------------- shortlist再構成(phase1_fix/fix_run_02と同一手順。snapshot再生) ----------------
_snap = None
_dbs = None
_S1 = {}


def _init():
    global _snap, _dbs
    if _snap is None:
        _snap = U.Snapshot()
        _dbs = core.load_group1_dbs()


def _base(key):
    _init()
    if key not in _S1:
        st = core.run_stage1_for_article(U.read_article(key), _dbs)
        _S1[key] = (st, U.pool_for_article(st)[0])
    return _S1[key]


def _replay(key, mode, k, budget):
    st0, pool = _base(key)
    rare = [c["canonical_form"] for c in st0["word_survivors"]]
    fn = U.make_order_fn(mode, rare, k=k)
    try:
        with U.patched(fn, _snap, allow_net_mw=False, allow_net_uni=False):
            return core.run_stage1_and_shortlist(U.read_article(key), _dbs, real_title(key), wiktionary_multiword_lookup_budget=budget)
    except RuntimeError:
        with U.patched(fn, _snap, allow_net_mw=False, allow_net_uni=True):
            return core.run_stage1_and_shortlist(U.read_article(key), _dbs, real_title(key), wiktionary_multiword_lookup_budget=budget)


def _mw_survivors(stage1):
    out = set()
    for lst in ("important_noun_candidates", "phrase_survivors"):
        for c in stage1[lst]:
            if c.get("db_categories") == ["multiword_term"] and c.get("matched_dbs") == ["wiktionary"]:
                out.add(c["canonical_form"])
    return out


def build_method1(key, name):
    """name: 'current' | 'alt_precision_guarded'"""
    st0, pool = _base(key)
    n2 = sum(1 for p in pool if len(p.split()) == 2)
    cur = _replay(key, "default", 10, 60)
    if name == "current":
        out = U.assemble_shortlist(cur["stage1"], dbs=_dbs)
    else:
        exp = _replay(key, "default", 10, n2 + U.THREEGRAM_CAP)
        out = U.assemble_shortlist(exp["stage1"], dbs=_dbs, demoted_allow=_mw_survivors(cur["stage1"]), u2="tierH+S", u3_exclude=True,
                                   u3_annotate=True, phrase_cap=20, realign=True, r2=True, r3=True)
    title = real_title(key)
    rows = U.candidate_row_text(out["shortlist"], out["sentence_reference"], with_annotations=True, pairs=out["containment_pairs"], title=title)
    return {"shortlist": out["shortlist"], "sentence_reference": out["sentence_reference"], "pairs": out["containment_pairs"], "rows_text": rows,
            "title": title}


def build_v2():
    t = open(V2_ART, encoding="utf-8").read()
    base = P.load_base(t)
    dbs = core.load_group1_dbs()
    pats = M.build_pattern_index(dbs)
    st = base["stage1"]
    pc = M.placeholder_candidates(st["sentence_units"], pats, dbs, P._canon_set(st))
    acc = json.load(open(V2_CAND, encoding="utf-8"))["accepted_candidates"]
    sl = P.build_variant_shortlist(base, "V2", placeholder_cands=pc, llm_cands=acc)
    return t, sl["shortlist_info"]


def cand_block(prompt_text):
    return prompt_text[prompt_text.index("【Topic】title:"):prompt_text.index("【選定方針】")]


def static_for(cond, level):
    if cond in ("C0", "C1"):
        return selector01.extract_static_instructions(bk.load_prompt_template()), S.prod_guidance()
    return PB.after_static(level), PB.AFTER_TAIL


def make_msg(static, guidance, cand_text):
    """候補ブロック(【Topic】〜SENTENCE REFERENCE)をstatic/guidanceで挟む。select.build_messageと同一の接合。"""
    return static.rstrip() + "\n\n" + cand_text.strip("\n") + "\n" + guidance.rstrip() + "\n"


# ---------------- 費用 ----------------
class Cost:
    lock = threading.Lock()
    path = f"{OUT}/cost_03.json"

    @classmethod
    def load(cls):
        if os.path.exists(cls.path):
            return json.load(open(cls.path, encoding="utf-8"))
        return {"budget_jpy": BUDGET, "stop_rule_jpy": STOP_RULE, "job_cap_jpy": JOB_CAP, "model": S.MODEL, "usd_jpy": pricing.USD_TO_JPY,
                "pricing_source": "er005_output/cost_baseline_01/pricing_snapshot.json (via er009 PRICING_USD_PER_M)", "calls": []}

    @classmethod
    def spent(cls):
        return round(sum(c["cost_jpy"] for c in cls.load()["calls"]), 4)

    @classmethod
    def append(cls, rec):
        with cls.lock:
            c = cls.load()
            c["calls"].append(rec)
            c["cumulative_jpy"] = round(sum(x["cost_jpy"] for x in c["calls"]), 4)
            json.dump(c, open(cls.path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


class Client2(S.UsageClient):
    """UsageClient + reasoning token分離 + 呼出ごとにcost_03.jsonへ即時追記。"""

    def __init__(self, label, tag, phase):
        super().__init__(label=label)
        outer = self

        class _Resp:
            def create(self, **kw):
                t0 = time.time()
                started = time.strftime("%Y-%m-%dT%H:%M:%S%z")
                r = outer._real.responses.create(**kw)
                u = getattr(r, "usage", None)
                usage = {}
                if u is not None:
                    usage = {"input_tokens": getattr(u, "input_tokens", None), "output_tokens": getattr(u, "output_tokens", None),
                             "reasoning_tokens": getattr(getattr(u, "output_tokens_details", None), "reasoning_tokens", 0) or 0,
                             "cached_input_tokens": getattr(getattr(u, "input_tokens_details", None), "cached_tokens", 0) or 0}
                rec = {"tag": tag, "phase": phase, "started_at": started, "model": r.model, "response_id": r.id, "usage": usage,
                       "elapsed_sec": round(time.time() - t0, 3),
                       "cost_jpy": pricing.cost_jpy_for_call("openai", r.model, usage.get("input_tokens"), usage.get("cached_input_tokens"),
                                                             usage.get("output_tokens"))}
                outer.log.append(rec)
                Cost.append(rec)
                return r
        self.responses = _Resp()


# ---------------- job ----------------
def run_gate(msg, article_text, id2c, cids, sentence_reference, client, out_dir, tag):
    selector01.assert_no_full_article_body(msg, article_text)
    open(os.path.join(out_dir, "selector_prompt.txt"), "w", encoding="utf-8").write(msg)
    usage_sink, viol = [], []
    factory = src_ref.make_instrumented_selector_factory(msg, S.MODEL, cids, usage_sink, contract_violation_sink=viol, client=client)
    gate = src_ref.run_source_reference_contract_gate(f"kp_p2_{tag}", factory, article_text, id2c, sentence_reference,
                                                      strategy_id=prod.STANDARD_STRATEGY_ID, family_profile="family_x")
    return gate, viol


def job(spec, ctx):
    article, level, cond, k = spec
    tag = f"{article}_{level}_{cond}_run{k}"
    if STOP_EVT.is_set() or stop_present():
        raise RuntimeError("STOP present / stop event")
    if Cost.spent() >= STOP_RULE:
        raise RuntimeError(f"cumulative >= {STOP_RULE}: stop before job")
    d = f"{OUT}/runs/{tag}"
    os.makedirs(d, exist_ok=True)
    c = ctx[(article, level, cond)]
    t = c["article_text"]
    c_sel = Client2(tag, tag, "selection")
    c_qa = Client2(tag, tag, "canon_qa")
    res = {"article": article, "level": level, "cond": cond, "run": k, "tag": tag, "msg_sha256": sha(c["msg"]), "model": S.MODEL}
    t0 = time.time()
    gate, viol = run_gate(c["msg"], t, c["id2c"], c["cids"], c["sentence_reference"], c_sel, d, tag)
    res.update(selection_status=gate["status"], validation_reasons=gate.get("validation_reasons"), item_reasons=gate.get("item_reasons"),
               topic_slot_filled_by_backup=gate.get("topic_slot_filled_by_backup"), contract_violation=viol)
    parsed = gate.get("parsed") or {}
    res["backup_item"] = parsed.get("backup_item")
    if gate["status"] == "KEY_WORDS_STRUCTURE_PASS":
        items = parsed["items"]
        id2 = c["id2c"]
        res["source_span_missing"] = selector01._verify_source_spans_against_raw_article(items, t)
        res["raw_selected_items"] = items
        res["selected_items"] = [{"rank": i.get("rank"), "role": i.get("key_phrase_role"), "display_phrase": i.get("display_phrase"),
                                  "source_span": i.get("source_span"), "source_candidate_id": i.get("source_candidate_id"),
                                  "ja_gloss": i.get("ja_gloss"), "phrase_type": i.get("phrase_type"),
                                  "evidence": (id2.get(i.get("source_candidate_id")) or {}).get("evidence"),
                                  "candidate_surface": (id2.get(i.get("source_candidate_id")) or {}).get("surface_form")} for i in items]
        qa = S.run_canonicalization_and_qa(t, items, c_qa)
        res["canonicalization_status"] = qa.get("canonicalization_status")
        res["canonicalization_item_reasons"] = [x.get("item_reasons") for x in qa.get("canonicalization_attempts", [])]
        res["canonicalization_attempt_statuses"] = [x.get("status") for x in qa.get("canonicalization_attempts", [])]
        res["redundancy_status"] = qa.get("redundancy_status")
        res["redundancy_duplicate_pairs"] = qa.get("redundancy_duplicate_pairs")
        if qa.get("merged"):
            res["canonicalized"] = [{"rank": i["rank"], "key_phrase": i["key_phrase"], "display_phrase": i["display_phrase"],
                                     "ja_gloss": i.get("ja_gloss"), "normalization_reason": i["normalization_reason"],
                                     "qa_overall_status": i["qa_overall_status"]} for i in qa["merged"]["items"]]
            res["merged_overall_status"] = qa["merged"]["overall_status"]
    res["usage"] = {"selection": c_sel.log, "canon_qa": c_qa.log}
    res["cost_jpy"] = round(c_sel.total_cost() + c_qa.total_cost(), 4)
    res["elapsed_sec"] = round(time.time() - t0, 2)
    if res["cost_jpy"] > JOB_CAP:
        STOP_EVT.set()
        res["job_cap_exceeded"] = True
    json.dump(res, open(f"{d}/job_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return res


# ---------------- context構築(有料呼出なし) ----------------
def build_ctx(stage):
    art = STAGE_ARTICLE[stage]
    ctx, info, specs = {}, {}, []
    for lv in LEVELS:
        key = f"{art}_{lv}"
        t = U.read_article(key)
        m1 = {n: build_method1(key, n) for n in ("current", "alt_precision_guarded")}
        for cond, nm in (("C0", "current"), ("C1", "alt_precision_guarded"), ("C2", "alt_precision_guarded")):
            if cond == "C1" and not (art == "coffee" and lv == "adv"):
                continue
            b = m1[nm]
            ids = src_ref.assign_candidate_ids(b["shortlist"])
            corr = src_ref.correct_shortlist_source_span_consistency(ids["shortlist_with_ids"], b["sentence_reference"])
            assert not corr["excluded"], f"span consistency除外あり {key} {cond}: {corr['excluded']}"
            static, guid = static_for(cond, lv)
            msg = make_msg(static, guid, cand_block(b["rows_text"]))
            ctx[(art, lv, cond)] = {"article_text": t, "msg": msg, "id2c": corr["id_to_candidate"],
                                    "cids": corr["candidate_ids"], "sentence_reference": b["sentence_reference"]}
            info[f"{art}_{lv}_{cond}"] = {"shortlist_config": nm, "msg_sha256": sha(msg), "rows_block_sha256": sha(cand_block(b["rows_text"])),
                                          "n_candidates": len(b["shortlist"]),
                                          "annotation_in_rows": any(x in b["rows_text"] for x in (U.LABEL_CONTAINS, U.LABEL_CONTAINED, U.LABEL_FRAGMENT)),
                                          "title": b["title"]}
    if art == "coffee":
        t2, si = build_v2()
        title = selector01.extract_article_title(t2)
        ids = src_ref.assign_candidate_ids(si["shortlist"])
        corr = src_ref.correct_shortlist_source_span_consistency(ids["shortlist_with_ids"], si["sentence_reference"])
        static, guid = static_for("C2", "adv")
        msg = S.build_message(title, corr["shortlist_with_ids"], si["sentence_reference"], static, guid)
        ctx[(art, "adv", "C2p")] = {"article_text": t2, "msg": msg, "id2c": corr["id_to_candidate"],
                                    "cids": corr["candidate_ids"], "sentence_reference": si["sentence_reference"]}
        info["coffee_adv_C2p"] = {"shortlist_config": "V2(Phase D成果物、注釈なし)", "msg_sha256": sha(msg), "n_candidates": len(corr["shortlist_with_ids"]),
                                  "excluded_by_span": corr["excluded"], "annotation_in_rows": False,
                                  "v2_candidate_source_sha256": sha_file(V2_CAND), "article_sha256": sha_file(V2_ART)}
    for lv in LEVELS:
        for cond in ("C0", "C2", "C1", "C2p"):
            if (art, lv, cond) in ctx:
                for k in range(1, N + 1):
                    specs.append((art, lv, cond, k))
    return ctx, info, specs


def state_hashes():
    return {f: (sha_file(f) if os.path.exists(f) else None) for f in STATE_FILES}


def update_guard(label):
    p = f"{OUT}/state_guard_03.json"
    g = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    g[label] = state_hashes()
    if "before" in g and label != "before":
        g[f"unchanged_{label}"] = g[label] == g["before"]
    json.dump(g, open(p, "w", encoding="utf-8"), indent=1)
    return g


def verify_fidelity(ctx, stage):
    """C0のProduction実runバイト一致(候補一覧方式のrun) + C2 PromptのSpecimen一致(Coffeeのみ)。"""
    art = STAGE_ARTICLE[stage]
    rep = {}
    for lv in LEVELS:
        key = f"{art}_{lv}"
        if key in PROD_PROMPT:
            p = open(PROD_PROMPT[key], encoding="utf-8").read()
            rep[f"{key}_C0_full_prompt_vs_production_run"] = (p == ctx[(art, lv, "C0")]["msg"])
        if art == "coffee":
            b = build_method1(key, "current")
            static, guid = static_for("C2", lv)
            m = make_msg(static, guid, cand_block(b["rows_text"]))
            spec = open(f"{FIX}/specimen_after_{lv}_v5_02.txt", encoding="utf-8").read()
            rep[f"{key}_C2prompt_with_current_rows_vs_specimen02"] = (m == spec)
    return rep


def stage_prep(stage):
    os.makedirs(OUT, exist_ok=True)
    assert not stop_present(), stop_present()
    if not os.path.exists(f"{OUT}/state_guard_03.json"):
        update_guard("before")
    ctx, info, specs = build_ctx(stage)
    fid = verify_fidelity(ctx, stage)
    fx = json.load(open(f"{FIX}/shortlists_fixed_02.json", encoding="utf-8"))["articles"]
    match = {}
    for lv in LEVELS:
        key = f"{STAGE_ARTICLE[stage]}_{lv}"
        for cond, nm in (("C0", "current"), ("C2", "alt_precision_guarded")):
            match[f"{key}_{cond}"] = sha(cand_block(fx[key][nm]["rows_text"])) == info[f"{key}_{cond}"]["rows_block_sha256"]
    out = {"stage": stage, "n_jobs": len(specs), "jobs": [list(s) for s in specs], "fidelity": fid, "rows_match_fixed_shortlist": match, "info": info,
           "prompt_after_02_sha256": sha_file(f"{FIX}/prompt_after_02.txt"), "shortlists_fixed_02_sha256": sha_file(f"{FIX}/shortlists_fixed_02.json")}
    json.dump(out, open(f"{OUT}/prep_stage{stage}_03.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({"jobs": len(specs), "fidelity": fid, "rows_match": match}, ensure_ascii=False, indent=1))


def stage_run(stage):
    os.makedirs(OUT, exist_ok=True)
    if stop_present():
        sys.exit(f"STOP present {stop_present()}")
    spent = Cost.spent()
    if spent + STAGE_EST[stage] > STOP_RULE:
        sys.exit(f"budget guard: spent {spent} + est {STAGE_EST[stage]} > {STOP_RULE}")
    ctx, info, specs = build_ctx(stage)
    fid = verify_fidelity(ctx, stage)
    assert all(v for v in fid.values()), f"fidelity NG {fid}"
    print("fidelity", fid, "jobs", len(specs), "spent_before", spent, flush=True)
    res, err = [], []
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(job, s, ctx): s for s in specs}
        for f in cf.as_completed(futs):
            try:
                res.append(f.result())
            except Exception as e:
                err.append({"job": list(futs[f]), "error": f"{type(e).__name__}: {e}"})
    res.sort(key=lambda r: (r["level"], r["cond"], r["run"]))
    json.dump({"stage": stage, "runs": res, "errors": err, "cumulative_jpy": Cost.spent(), "info": info, "fidelity": fid},
              open(f"{OUT}/stage{stage}_summary_03.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    for r in res:
        print(r["tag"], r["selection_status"], r.get("canonicalization_status"), r.get("redundancy_status"),
              [i["display_phrase"] for i in r.get("selected_items", [])], r["cost_jpy"], r["elapsed_sec"])
    print("errors", err, "cum", Cost.spent())
    update_guard(f"after_stage{stage}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["prep1", "prep2", "prep3", "1", "2", "3"])
    a = ap.parse_args()
    if a.stage.startswith("prep"):
        stage_prep(int(a.stage[-1]))
    else:
        stage_run(int(a.stage))
