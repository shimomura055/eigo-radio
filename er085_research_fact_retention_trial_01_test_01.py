# -*- coding: utf-8 -*-
"""FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 harness test(API 0)。

pytest er085_research_fact_retention_trial_01_test_01.py -q
"""
import json
import os

import pytest

import er085_research_fact_retention_trial_01_lib as lib
import er085_research_fact_retention_trial_01_eval as ev
import er003_v1_en_direct_vfl_01_generate as vfl01

SPEC = lib.load_sources_spec()
GOLD = ev.load_gold()
SOURCES_PRESENT = os.path.exists(os.path.join(lib.OUT_ROOT, "sources", "mey", "S1.txt"))


def mini_packet():
    return [{"id": "S1", "url": "https://example.test/a", "title": "t", "date": "2026-01-01", "body": "A did X to B."}]


def test_e0_prompts_equal_production_except_declared_diffs():
    """E0(R0/V0)は Production Prompt(vfl01)に『No-search化の2置換+出典ブロック』だけを加えたもの。"""
    topic = "テスト題材"
    pk = mini_packet()
    dev, user, schema = lib.build_researcher_prompt("R0", topic, pk)
    prod = vfl01.build_researcher_prompt(topic=topic)
    assert dev == vfl01.RESEARCHER_DEVELOPER_MESSAGE
    assert schema is vfl01.FACT_LEDGER_JSON_SCHEMA
    assert user == prod.replace(lib.R1_OLD, lib.R1_NEW) + lib.SOURCE_HEADER + lib.render_packet(pk)
    ledger = {"facts": []}
    dev, user, schema = lib.build_verification_prompt("V0", topic, ledger, pk)
    prod_v = vfl01.build_verification_prompt(topic, ledger)
    assert dev == vfl01.VERIFICATION_DEVELOPER_MESSAGE and schema is vfl01.VERIFICATION_JSON_SCHEMA
    assert user == prod_v.replace(lib.V1_OLD, lib.V1_NEW) + lib.SOURCE_HEADER + lib.render_packet(pk)


def test_candidate_prompt_diffs_are_exactly_the_declared_inserts():
    topic, pk = "T", mini_packet()
    r0 = lib.build_researcher_prompt("R0", topic, pk)[1]
    ra = lib.build_researcher_prompt("RA", topic, pk)[1]
    assert ra.replace(lib.A_INSERT.rstrip("\n"), "", 1) == r0 and "5. 帰属・行為主体" in ra and "6. 直接の文脈" in ra
    assert "出典が明示していない主体・動機は書かない" in lib.A_INSERT
    rb = lib.build_researcher_prompt("RB", topic, pk)
    assert rb[1].replace(lib.B_PROMPT_ADD, "", 1) == r0 and rb[2]["name"].endswith("_b")
    ledger = {"facts": []}
    v0 = lib.build_verification_prompt("V0", topic, ledger, pk)[1]
    vc = lib.build_verification_prompt("VC", topic, ledger, pk)[1]
    assert vc.replace("\n" + lib.VC_LINE, "", 1) == v0
    # 方式C/D/E のResearcherは E0/A と同一(Researcher不変)
    assert lib.VARIANTS["C"]["research"] == "R0" and lib.VARIANTS["D"]["research"] == "RA" and lib.VARIANTS["E"]["audit"] is True
    # 追加LLM呼出: 検索は0。E以外は現行と同数(2)
    assert [lib.VARIANTS[v]["audit"] for v in "E0 A B C D".split()] == [False] * 5


def test_trial_schema_b_extends_only_and_production_schema_unchanged():
    s = lib.trial_schema_b()
    item = s["schema"]["properties"]["facts"]["items"]
    prod_item = vfl01.FACT_LEDGER_JSON_SCHEMA["schema"]["properties"]["facts"]["items"]
    assert "actor" not in prod_item["properties"] and "context" not in prod_item["properties"]
    assert set(item["properties"]) - set(prod_item["properties"]) == {"actor", "context"}
    assert item["required"][-2:] == ["actor", "context"] and s["strict"] is True
    f = {k: None for k in prod_item["properties"]}
    f.update({"fact_id": "F01", "claim": "c", "subject": "s", "causal_strength": "NOT_APPLICABLE", "source_title": "t", "source_url": "u",
              "source_type": "OTHER", "support_level": "DIRECTLY_STATED", "actor": "UN特使", "context": "戦況の文脈"})
    folded = lib.fold_b_to_ledger({"facts": [f]})
    assert lib.validate_ledger_draft(folded) == []
    g = folded["facts"][0]
    assert "【主体】UN特使" in g["conditions"] and "【背景】戦況の文脈" in g["notes_for_writer"] and "actor" not in g
    assert lib.validate_ledger_draft({"facts": [f]}) != []  # actor/contextを含むままではLedger本体schema不適合


@pytest.mark.skipif(not SOURCES_PRESENT, reason="sources/ 未作成(--prepare-sources を先に実行)")
def test_gold_quotes_are_verbatim_in_sources():
    for t, d in GOLD["topics"].items():
        for it in d["items"]:
            body = lib.read_text(os.path.join(lib.OUT_ROOT, "sources", t, f"{it['source_id']}.txt"))
            assert lib.norm_q(it["quote"]) in lib.norm_q(body), it["id"]
            assert it["tier"] in ("KEY", "SEC", "CTRL") and it["groups"]


def test_gold_scoring_positive_and_negative():
    items = {i["id"]: i for i in GOLD["topics"]["mey"]["items"]}
    pos = ("[VERIFIED] F11: 国連イエメン担当特使は、サウジアラビアの民間インフラに対する継続的な攻撃（アンサール・アッラーによるもの）を非難し、"
           "10月10日のリヤド空港攻撃を重大なエスカレーションと述べた。")
    neg = "[VERIFIED] F11: 国連イエメン担当特使は、サウジアラビアの民間インフラに対する継続的な攻撃を非難し、10月10日のリヤド空港攻撃で12人が死亡した。"
    assert ev.lib.item_matches(items["M-A1"], pos) is True
    assert ev.lib.item_matches(items["M-A1"], neg) is False  # 主体脱落(現行の欠落パターン)は不保持
    # 主体が別Factにしか無い場合は単一ブロック要件を満たさない
    m = lib.match_gold([items["M-A1"]], [neg, "[VERIFIED] F02: アンサール・アッラーは紅海で活動している。"])
    assert m["M-A1"] is None
    # gold_02の厳格化: 別出典由来の『特使→Ansar Allah→サウジ施設攻撃』Fact(空港を含まない)ではM-A1は充足されない(gold_01の妥当性欠陥の修正)
    f5 = "[VERIFIED] F5: 特使は、アンサール・アッラーがサウジアラビアの民間インフラおよびエネルギー関連インフラに対して死者を伴う攻撃を行ったと述べた。"
    assert lib.item_matches(items["M-A1"], f5) is False and lib.item_matches({i["id"]: i for i in GOLD["topics"]["mey"]["items"]}["M-A2"], f5) is True
    g1 = ev.load_gold(os.path.join(lib.DOC_DIR, "gold_01.json"))
    a1_old = {i["id"]: i for i in g1["topics"]["mey"]["items"]}["M-A1"]
    assert lib.item_matches(a1_old, f5) is True  # gold_01では充足されてしまっていた(訂正理由の固定)
    bg = items["M-B2"]
    assert lib.item_matches(bg, "フーシ派(アンサール・アッラー)は紅海でサウジ関連の商船を脅かしていると特使は述べた") is True
    assert lib.item_matches(bg, "紅海の商船航行は通常どおり") is False


def test_fabrication_flags_positive_and_negative():
    watch = GOLD["topics"]["mey"]["watch"]
    bad = lib.split_blocks("[VERIFIED] F20: フーシ派はイランの指示に従い、報復のためサウジを攻撃した。\n  causal_strength: CAUSAL_STATED_BY_SOURCE\n")
    ok = lib.split_blocks("[VERIFIED] F21: 国連特使は、アンサール・アッラーによる攻撃を非難した。\n  causal_strength: OBSERVED_REPORTED\n")
    fb = lib.fabrication_flags(bad, watch)
    assert fb and {"motive_causal_marker", "causal_stated_by_source", "watch:iran", "watch:motive_words"} <= set(fb[0]["reasons"])
    assert lib.fabrication_flags(ok, watch) == []


def test_dryrun_pipeline_api0_ledger_and_b3_ids(tmp_path):
    import er019_family_x_storyline_b3_fact_selection_01 as b3
    out = str(tmp_path / "er085_output" / "research_fact_retention_trial_01")
    spec = {"topics": {"tt": {"topic_text": "テスト", "sources": [
        {"id": "S1", "raw": "tt/raw.txt", "url": "https://example.test/a", "title": "t", "date": "2026-01-01", "http": 200,
         "fetched_at": "x", "start": "BEGIN", "end": "END"}]}}}
    lib.write_text(os.path.join(out, "sources_raw", "tt", "raw.txt"), "nav\nBEGIN\nA did X to B.\nEND\nfooter")
    lib.prepare_sources(spec, out)
    assert lib.read_text(os.path.join(out, "sources", "tt", "S1.txt")) == "BEGIN\nA did X to B."
    stub = lib.StubClient()
    res = {}
    for v in ("E0", "A", "B", "C", "D", "E"):
        res[v] = lib.run_variant(stub, v, "tt", 1, spec, out, guard=None, dry_run=True)
    assert [res[v]["n_llm_calls"] for v in ("E0", "A", "B", "C", "D", "E")] == [2, 2, 2, 2, 2, 3]
    assert all(r["web_search_calls"] == 0 and r["schema_errors"] == [] for r in res.values())
    # stage cache共有: R0はE0/C/Eで共有 -> 全6方式で stub呼出は 10 回(R0,RA,RB,V0@R0,V0@RA,V0@RB,VC@R0,VC@RA,AU,V0@E)
    assert stub.calls == 10
    txt = lib.read_text(os.path.join(out, "_dryrun", "tt", "s1", "B", "verified_fact_ledger.txt"))
    assert "【主体】" in txt  # Bのactorが既存欄conditionsへ畳み込まれ、Production rendererでLedgerに出る
    assert b3.extract_fact_ids_from_ledger(txt) == ["F01"]
    assert b3.verified_fact_ids(txt) == ["F01"]  # B3下限2件の算定(VERIFIEDのみ)に使われる関数でも解釈できる
    assert not os.path.exists(os.path.join(out, "raw_usage_log.jsonl"))  # dry-runは費用ログを作らない
    assert os.path.exists(os.path.join(out, "_dryrun", "calls_dryrun.jsonl"))


def test_budget_guard_and_cost_formula(tmp_path):
    # 実測(run_mey_01 cost.json research=26.995 JPY: in119459/out13549/web_search 15)との一致
    assert abs(lib.cost_jpy("gpt-6-luna", 119459, 13549, 15) - 26.995) < 0.01
    # 検索なしの同規模呼出は検索料(15x$0.01)が無く桁違いに安い
    assert lib.cost_jpy("gpt-6-luna", 12000, 12000, 0) < 2.0
    log = str(tmp_path / "calls.jsonl")
    lib.append_jsonl(log, {"cost_jpy": 29.0})
    g = lib.BudgetGuard(log, 30.0)
    with pytest.raises(RuntimeError, match="BUDGET_GUARD"):
        g.check(est_next=1.5)
    g.check(est_next=0.5)


def test_aggregate_delta_facts_and_flags():
    def cell(var, n, key_ok, flags=()):
        return {"variant": var, "topic": "mey", "sample": 1, "n_facts_draft": n, "cost_jpy": 1.0, "n_llm_calls": 2, "web_search_calls": 0,
                "latency_seconds": 10, "schema_errors": [], "flags": list(flags),
                "per_item": {"x": {"tier": "KEY", "ledger": key_ok, "draft": key_ok}, "y": {"tier": "KEY", "ledger": False, "draft": True}}}
    agg = ev.aggregate([cell("E0", 10, False), cell("A", 13, True, [{"fact_id": "F1", "reasons": ["x"], "adjudication": "UNADJUDICATED"}])])
    assert agg["E0|mey"]["key_ledger"] == 0.0 and agg["A|mey"]["key_ledger"] == 0.5
    assert agg["A|mey"]["delta_facts_vs_E0"] == 3.0 and agg["A|mey"]["flags_unadjudicated"] == 1 and agg["A|mey"]["key_draft"] == 1.0


def test_extract_body_fails_loudly_on_missing_marker():
    with pytest.raises(ValueError):
        lib.extract_body("abc", {"start": "zzz", "end": "c"})
    assert lib.extract_body("x\n A \n\n B \nEND", {"start": "A", "end": "END"}) == "A\nB"
    assert lib.extract_body("x BEGIN k1 DROP k2 ok END", {"start": "BEGIN", "end": "END", "drop": [["DROP", "k2"]]}) == "BEGIN k1  ok"
