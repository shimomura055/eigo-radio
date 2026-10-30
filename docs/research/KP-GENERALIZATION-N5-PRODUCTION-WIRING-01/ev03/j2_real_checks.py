"""委任_03 J2是正の実API検証(Cap内、費用は逐次合算)。usage: <python> j2_real_checks.py part1|part2 (cwd=repo root)
part1: Trial記録replayで再判定callだけ実API(ai_cha_a2 'clear fall' / moon_b1b 'heat from escaping')。
part2: ④fixture(jwst_m_b1b、委任_02 M10で保存したP7出力+B1返却をそのまま入力)で、公式部品(pool_and_select -> run_l3)を実APIで実行。"""
import sys, os, json
ROOT = os.getcwd(); sys.path.insert(0, ROOT)
from unittest import mock
EV = os.path.join(ROOT, "docs/research/KP-GENERALIZATION-N5-PRODUCTION-WIRING-01")
import er138_kp_n5_generalization_01_test_01 as T
import er138_kp_n5_generalization_01 as n5
import er003_v1_n3_01_scaffold_generate as sc
part = sys.argv[1]
real_send = n5._send
spent = []

def logged_send(stage, model, user, schema, max_out):
    t, m = real_send(stage, model, user, schema, max_out)
    spent.append(m.get("cost_jpy") or 0.0)
    return t, m

if part == "part1":
    out = {}
    for cid in ("ai_cha_a2", "moon_b1b"):
        case = T.FX["cases"][cid]
        items = [{"display_phrase": b["span"], "source_sentence": b.get("sentence") or "", "item": {"display_phrase": b["span"]}} for b in case["base"]]
        rep = T.ReplaySend()

        def send(stage, model, user, schema, max_out, rep=rep):
            try:
                return rep(stage, model, user, schema, max_out)
            except AssertionError:
                return logged_send(stage, model, user, schema, max_out)
        gate = lambda units, screen=None: (lambda c: (dict(c, n5_origin="B1", item={"display_phrase": c["span"], "reason_ja": ""}), []))
        proc = "A2_SUPPORT" if cid.endswith("a2") else "B1_SUPPORT"
        ctx = n5.N5Ctx(proc, sleep_fn=lambda s: None, stop_check_fn=sc.make_stop_check(EV + "/ev03"))
        with mock.patch.object(n5, "_send", send), mock.patch.object(n5, "preflight", lambda: None), mock.patch.object(n5, "make_b1_gate", gate):
            r = n5.pool_and_select(case["text"], items, ctx, include_b1=True, units=[])
        out[cid] = {"deferred_rejudged": r["record"]["deferred_rejudged"], "picked": [p["item"]["display_phrase"] for p in r["picked"]],
                    "trial_final_source_spans": [i["source_span"] for i in case["trial_items"]]}
    out["cost_jpy"] = round(sum(spent), 4)
    json.dump(out, open(EV + "/ev03/j2_part1_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False))
else:
    import er105_kp_fulltext_selector_01 as core_mod  # noqa
    import er119_kp_candidates_01 as kc
    ft = n5.ft
    m10 = EV + "/ev02/m10/jwst_m_b1b"
    text = T.FX["cases"]["jwst_m_b1b"]["text"]
    raw = json.load(open(glob_path := [os.path.join(dp, f) for dp, _, fs in os.walk(m10 + "/kp") for f in fs if f == "keywords_selector_raw_attempts.json"][0], encoding="utf-8"))
    p7 = [i["phrase"] for i in json.loads(raw[0]["raw_text"])["items"]]
    l1 = json.load(open(m10 + "/result.json", encoding="utf-8"))["doc"]["generalization"]["attempts"][0]["l1"][0]
    b1_spans = [r["span"] for r in l1["pool_rejected"] if r.get("origin") == "B1"] + [j["span"] for j in l1["judged"] if j["span"] not in p7]
    assert len(p7) == l1["n_p7_in"] and len(b1_spans) == l1["n_b1_returned"], (len(p7), len(b1_spans))
    import er003_v1_n3_01_scaffold_generate as sc2
    import er030_key_phrase_db_hybrid_core_01 as core
    units = core.build_sentence_units(text)
    v = ft.validate_and_resolve([{"phrase": p, "declared_word_count": ft.count_words(p)} for p in p7], units)
    p7_items = ft.build_original_items(v["resolved"])
    real_call = n5.call_llm

    def fake_call(stage, user, schema, ctx, *, label=""):
        if stage == "b1":
            return {"candidates": [{"span": s, "sentence": ""} for s in b1_spans]}, {"model_id": "replayed-from-m10(委任_02保存のB1返却)", "cost_jpy": 0.0}
        return real_call(stage, user, schema, ctx, label=label)
    ctx = n5.N5Ctx("B1_SUPPORT", sleep_fn=lambda s: None, stop_check_fn=sc.make_stop_check(EV + "/ev03"), article_id="J2_part2")
    with mock.patch.object(n5, "_send", logged_send), mock.patch.object(n5, "call_llm", fake_call):
        l1r = n5.pool_and_select(text, p7_items, ctx, include_b1=True, units=units)
        tg = [{"key": i, "span": pk["item"]["display_phrase"], "sentence": pk["item"].get("source_sentence") or "", "prod_gloss": (pk["item"].get("japanese_gloss") if pk["n5_origin"] != "B1" else None),
               "n5_origin": pk["n5_origin"]} for i, pk in enumerate(l1r["picked"])]
        l3 = n5.run_l3(text, tg, ctx)
    res = {"p7_input": p7, "b1_input": b1_spans, "picked": [(p["item"]["display_phrase"], p["n5_origin"]) for p in l1r["picked"]],
           "deferred_rejudged": l1r["record"]["deferred_rejudged"], "pool_rejected": l1r["record"]["pool_rejected"],
           "l3_kept": {tg[int(k)]["span"] if str(k).isdigit() else str(k): {x: v.get(x) for x in ("display_form", "gloss_ja", "check", "reverted")} for k, v in l3["kept"].items()},
           "l3_dropped": l3["dropped"], "cost_jpy": round(sum(spent), 4)}
    json.dump(res, open(EV + "/ev03/j2_part2_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps(res, ensure_ascii=False, default=str)[:3000])
