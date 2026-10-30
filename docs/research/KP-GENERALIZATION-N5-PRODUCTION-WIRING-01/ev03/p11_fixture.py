"""P11 fixture: Z人称整合(er026 _person_repair_factory + er119.make_person_repair_fn)を通した N5 gloss書換の観測。usage: python p11_fixture.py (cwd=repo root)
自然発生の実例ではなくfixture: ev03/z の実候補doc(N5記録あり)を複製し、japanese_gloss(とn5.gloss_ja)だけ具体的人称語入りに差替えて
『N5確定後のglossが人称不整合』という発火条件を作る。処理は正式関数 er119._gate_chain(人称整合step) -> kcand.make_person_repair_fn -> ga.align_glosses(実LLM)。
Production code無変更・mockなし。"""
import sys, os, json, copy, types
ROOT = os.path.abspath(os.getcwd()); sys.path.insert(0, ROOT)
EV = "docs/research/KP-GENERALIZATION-N5-PRODUCTION-WIRING-01/ev03"
OUT = f"{EV}/p11_02"; os.makedirs(OUT, exist_ok=True)
import er005_cost_logger as cl
cl.install(f"{OUT}/cost_log.jsonl")
import er119_kp_candidates_01 as kcand
import er026_family_z_fiction_production_runner_01 as z
import er003_key_words_gloss_alignment as ga
import er138_kp_n5_generalization_01 as n5
text = open("er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_n5ev3/writer/std.md", encoding="utf-8").read()
src = json.load(open(f"{EV}/z/kp_candidates_a2_round1.json", encoding="utf-8"))
base = next(c for c in src["candidates"] if c["selection_phrase"] == "made my blood turn cold")["item"]
assert base.get("n5") and ga.indefinite_person_tokens(base["key_phrase"])

def _locs(o, s, p=""):
    out = []
    if isinstance(o, dict):
        for k, v in o.items(): out += _locs(v, s, f"{p}.{k}")
    elif isinstance(o, list):
        for n, v in enumerate(o): out += _locs(v, s, f"{p}[{n}]")
    elif isinstance(o, str) and s in o: out.append(p)
    return out

def run(label, concrete_gloss):
    it = copy.deepcopy(base)
    it["rank"] = 1
    if concrete_gloss:      # fixture: N5確定後のglossが具体人称入りという発火条件を作る(それ以外は実docのまま)
        it["japanese_gloss"] = concrete_gloss; it["n5"]["gloss_ja"] = concrete_gloss
        it["japanese_gloss_tts"] = concrete_gloss
    gloss0, n5gloss0 = it["japanese_gloss"], it["n5"]["gloss_ja"]
    mismatch_before = ga.person_reference_mismatch(it["key_phrase"], it["japanese_gloss"])
    work = f"{OUT}/{label}"; os.makedirs(work, exist_ok=True)
    ctx = types.SimpleNamespace(hooks={}, mode="real")       # er026._person_repair_factory が参照するのは hooks / mode のみ
    person_fn = kcand.make_person_repair_fn(text, z._person_repair_factory(ctx, "a2"), f"{work}/gloss_person_repair_candidates", "P11_FIXTURE")
    meta = [{"raw_rank": 1, "selection_phrase": "made my blood turn cold", "origin": "call1", "reason_ja": "fixture", "n5_target": False}]
    stages, dropped = {}, []
    canon_fn = lambda t, items, w, a, process=None: {"status": "CANONICALIZATION_PASS", "merged": {"items": [copy.deepcopy(it)]}}   # 入力供給(canon段の代替=fixture入力)
    with cl.logging_context(theme="P11_FIXTURE", stage="kp_gloss_person_repair"):
        r = kcand._gate_chain(text, work, "P11_FIXTURE", "A2_SUPPORT", [{"selection_phrase": "made my blood turn cold"}], meta, [0], dropped,
                              ng_entries=[], canon_fn=canon_fn, src_fn=None, person_repair_fn=person_fn, stages=stages, n5_ctx=n5.N5Ctx("A2_SUPPORT", tag="p11"))
    res = {"label": label, "fixture_not_natural": True, "status": r["status"], "dropped": dropped, "stages": stages,
           "mismatch_before": mismatch_before, "gloss_before": gloss0, "n5_gloss_ja_before": n5gloss0}
    if r["status"] == "OK" and r["cands"]:
        c = r["cands"][0]; i2 = c["item"]
        res.update(japanese_gloss_after=i2.get("japanese_gloss"), cand_japanese_gloss=c.get("japanese_gloss"), japanese_gloss_tts_after=i2.get("japanese_gloss_tts"),
                   n5_gloss_ja_after=i2["n5"].get("gloss_ja"), n5_person_repair=i2["n5"].get("person_repair"), gloss_alignment_status=i2.get("gloss_alignment_status"),
                   mismatch_after=ga.person_reference_mismatch(i2["key_phrase"], i2["japanese_gloss"]), gates=c.get("gates"),
                   old_gloss_locations=(_locs(i2, gloss0) if concrete_gloss else None), item_after=i2)
    return res
results = [run("fire", "あなたをぞっとさせ、強い恐怖を感じさせる"), run("control_no_mismatch", None)]
b = __import__("er053_cost_aggregate_01").compute_stage_cost_breakdown_multi(f"{OUT}/cost_log.jsonl")
json.dump({"note": "自然発生の実例ではなくfixture", "results": results, "cost_jpy": b["total_jpy"]}, open(f"{EV}/p11_fixture_result_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print(json.dumps(results, ensure_ascii=False, indent=1, default=str)); print("cost", b["total_jpy"])
