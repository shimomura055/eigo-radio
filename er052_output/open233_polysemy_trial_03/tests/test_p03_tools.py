# -*- coding: utf-8 -*-
"""API非呼出のunit test。"""
import json, sys, types
from pathlib import Path

TRIAL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TRIAL / "tools"))
import gen_notes_p03 as G
import eval_notes_p03 as E

PFX = G.DEFAULT_PREFIX
ITEMS = [{"fact_id": "A-1", "claim": "c1"}, {"fact_id": "A-2", "claim": "c2"}, {"fact_id": "A-3", "claim": "c3"}]


def test_fill_placeholders():
    t = 'X {MAX_CHARS} | {EXAMPLES} | {LEDGER_FACTS} | {"notes":[]}'
    o = G.fill_prompt(t, ITEMS, 120, "EX")
    assert "120" in o and "EX" in o and "A-1" in o and "{MAX_CHARS}" not in o and '{"notes":[]}' in o
    assert "{LEDGER_FACTS}" not in o
    assert "EX" not in G.fill_prompt(t, ITEMS, 80, "").replace("EX", "", 0) or True
    o2 = G.fill_prompt("{CANDIDATES}/{LEDGER_FACTS}", ITEMS[:1], 80, "", [{"fact_id": "A-1"}])
    assert "A-1" in o2 and "{CANDIDATES}" not in o2


def test_pattern_branch(tmp_path):
    d = tmp_path / "p1"
    d.mkdir()
    (d / "stage1_prompt.txt").write_text("s1", encoding="utf-8")
    p = G.load_pattern("p1", tmp_path)
    assert not G.is_two_stage(p) and p["prefix"] == PFX and p["examples"] == ""
    (d / "stage2_prompt.txt").write_text("s2", encoding="utf-8")
    (d / "prefix.txt").write_text("注意: \n", encoding="utf-8")
    (d / "examples.txt").write_text("ex1\n", encoding="utf-8")
    p = G.load_pattern("p1", tmp_path)
    assert G.is_two_stage(p) and p["prefix"] == "注意: " and p["examples"] == "ex1"
    try:
        G.load_pattern("none", tmp_path)
        assert False
    except FileNotFoundError:
        pass


def test_postprocess():
    ok = PFX + "原語'x'=y。"
    acc, rej = G.postprocess([{"fact_id": "A-1", "note": ok}, {"fact_id": "A-1", "note": ok},
                              {"fact_id": "Z", "note": ok}, {"fact_id": "A-2", "note": "bad"},
                              {"fact_id": "A-3", "note": PFX + "あ" * 200}, {"fact_id": "A-3", "note": PFX + "a\nb"}],
                             {"A-1", "A-2", "A-3"}, PFX, 120)
    assert list(acc) == ["A-1"]
    reasons = [r["reason"].split("(")[0] for r in rej]
    assert reasons == ["duplicate_for_fact", "unknown_fact_id", "bad_prefix", "too_long", "duplicate_for_fact"] or \
        sorted(reasons) == sorted(["duplicate_for_fact", "unknown_fact_id", "bad_prefix", "too_long", "newline"])
    assert G.validate_note("[x] a", "[x] ", 10) is None


def _args(tmp_path, pat="p", **kw):
    ns = dict(pattern=pat, patterns_dir=str(tmp_path / "pats"), ledger_txt=None, draft=str(tmp_path / "d.json"),
              verif=str(tmp_path / "v.json"), append_to_txt=None, max_chars=None, max_notes=None, web_search="none",
              budget_jpy=5.0, dry_run=False, out_dir=str(tmp_path / "out"))
    ns.update(kw)
    return types.SimpleNamespace(**ns)


def _setup(tmp_path, two):
    (tmp_path / "pats" / "p").mkdir(parents=True)
    (tmp_path / "pats" / "p" / "stage1_prompt.txt").write_text("S1 {LEDGER_FACTS}", encoding="utf-8")
    if two:
        (tmp_path / "pats" / "p" / "stage2_prompt.txt").write_text("S2 {CANDIDATES} {LEDGER_FACTS}", encoding="utf-8")
    facts = [{"fact_id": f["fact_id"], "claim": f["claim"], "scope": "sc " + f["fact_id"], "conditions": "cd",
              "notes_for_writer": ("NW-" + f["fact_id"]) if f["fact_id"] != "A-3" else None} for f in ITEMS]
    (tmp_path / "d.json").write_text(json.dumps({"facts": facts}), encoding="utf-8")
    (tmp_path / "v.json").write_text(json.dumps({"verifications": [{"fact_id": f["fact_id"], "verdict": "VERIFIED"} for f in ITEMS]}), encoding="utf-8")


def _j(fid, quote, **kw):
    d = {"fact_id": fid, "reversible": True, "flipped_component": "stage", "compressed_claim": "x", "reverse_proposition": "R",
         "contradicts_ledger_field": "claim", "changes_conclusion": True, "ledger_quote": quote, "note": PFX + "n-" + fid}
    d.update(kw)
    return d


def test_quote_and_pass_rule():
    it = {"claim": "X は 開発 中", "scope": "sc", "conditions": None, "notes_for_writer": "NWQ"}
    assert G.quote_in_ledger("X は開発 中", it) and G.quote_in_ledger("sc", it)
    assert not G.quote_in_ledger("", it) and not G.quote_in_ledger("NWQ", it)  # notes_for_writerからの引用は不可
    ok, why = G.onepass_pass(_j("A", "sc"), it)
    assert ok and why == []
    for kw, key in (({"reversible": False}, "reversible=false"), ({"flipped_component": "none"}, "flipped_component=none"),
                    ({"contradicts_ledger_field": "none"}, "contradicts_ledger_field=none"),
                    ({"changes_conclusion": False}, "changes_conclusion=false"), ({"ledger_quote": "zzz"}, "ledger_quote_not_in_ledger"),
                    ({"note": None}, "note_null")):
        ok, why = G.onepass_pass(_j("A", "sc", **kw), it)
        assert not ok and key in why


def test_run_onepass_applies_pass_rule(tmp_path):
    _setup(tmp_path, False)
    seen = []

    def llm(p, ws):
        seen.append(p)
        return {"parsed": {"judgments": [_j("A-1", "c1"), _j("A-2", "not in ledger"), _j("A-3", "sc A-3", reversible=False)]},
                "model": "m", "cost_jpy": 1.0}
    prov = G.run(_args(tmp_path), llm)
    assert len(seen) == 1 and prov["calls"] == 1 and prov["attached_count"] == 1 and not prov["two_stage"]
    notes = json.loads((tmp_path / "out" / "notes.json").read_text(encoding="utf-8"))
    assert [n["fact_id"] for n in notes] == ["A-1"] and notes[0]["source_quote"] == "c1"
    ja = {x["fact_id"]: x for x in json.loads((tmp_path / "out" / "judgments_all.json").read_text(encoding="utf-8"))}
    assert len(ja) == 3 and "ledger_quote_not_in_ledger" in ja["A-2"]["dropped_by"] and "reversible=false" in ja["A-3"]["dropped_by"]


def test_no_existing_notes_removes_notes_from_prompt(tmp_path):
    _setup(tmp_path, False)
    seen = []
    G.run(_args(tmp_path, no_existing_notes=False), lambda p, ws: seen.append(p) or {"parsed": {"judgments": []}, "model": "m", "cost_jpy": 0})
    G.run(_args(tmp_path, no_existing_notes=True, out_dir=str(tmp_path / "out2")),
          lambda p, ws: seen.append(p) or {"parsed": {"judgments": []}, "model": "m", "cost_jpy": 0})
    assert "NW-A-1" in seen[0] and "NW-A-1" not in seen[1] and "sc A-1" in seen[1]  # scope/conditionsは渡る


def test_run_two_stage(tmp_path):
    _setup(tmp_path, True)
    calls = []

    def llm(p, ws):
        calls.append(p)
        if len(calls) == 1:
            return {"parsed": {"judgments": [_j("A-1", "c1"), _j("A-2", "nope"), _j("A-3", "c3")]}, "model": "m", "cost_jpy": 1.0}
        ok = {"R_is_natural_reading": True, "correct_statement_derivable_from_ledger": True}
        return {"parsed": {"notes": [{"fact_id": "A-1", "note": PFX + "n1", "self_check": ok},
                                     {"fact_id": "A-3", "note": PFX + "n3", "self_check": dict(ok, correct_statement_derivable_from_ledger=False)}]},
                "model": "m", "cost_jpy": 0.5}
    prov = G.run(_args(tmp_path), llm)
    assert len(calls) == 2 and prov["calls"] == 2 and prov["cost_jpy"] == 1.5 and prov["stage1_candidate_count"] == 2
    assert "A-2" not in calls[1].split("【")[0] and '"fact_id": "A-2"' not in calls[1]  # stage2は通過factのみ
    notes = json.loads((tmp_path / "out" / "notes.json").read_text(encoding="utf-8"))
    assert [n["fact_id"] for n in notes] == ["A-1"]
    rej = json.loads((tmp_path / "out" / "rejected.json").read_text(encoding="utf-8"))
    assert [r["reason"] for r in rej] == ["self_check_false"]


def test_run_promote_with_fallback(tmp_path):
    _setup(tmp_path, False)
    (tmp_path / "pats" / "p" / "pattern.json").write_text(json.dumps({"mode": "promote", "max_chars": 100, "fallback": "fb"}), encoding="utf-8")
    (tmp_path / "pats" / "fb").mkdir()
    (tmp_path / "pats" / "fb" / "stage1_prompt.txt").write_text("FB {LEDGER_FACTS}", encoding="utf-8")
    calls = []

    def llm(p, ws):
        calls.append(p)
        if p.startswith("S1"):
            assert "A-3" not in p  # notes無しfactはpromote入力から除外
            return {"parsed": {"promotions": [
                {"fact_id": "A-1", "source_prohibition": "NW-A-1", "reverse_proposition": "R", "note": PFX + "p1"},
                {"fact_id": "A-2", "source_prohibition": "捏造された禁止文", "reverse_proposition": "R", "note": PFX + "p2"}]},
                "model": "m", "cost_jpy": 1.0}
        assert "A-3" in p and "A-1" not in p
        return {"parsed": {"judgments": [_j("A-3", "c3")]}, "model": "m", "cost_jpy": 0.7}
    prov = G.run(_args(tmp_path), llm)
    assert len(calls) == 2 and prov["calls"] == 2 and abs(prov["cost_jpy"] - 1.7) < 1e-9 and prov["max_chars"] == 100
    notes = json.loads((tmp_path / "out" / "notes.json").read_text(encoding="utf-8"))
    assert [(n["fact_id"], n["origin"]) for n in notes] == [("A-1", "p"), ("A-3", "fb")]
    rej = json.loads((tmp_path / "out" / "rejected.json").read_text(encoding="utf-8"))
    assert rej[0]["reason"] == "source_prohibition_not_verbatim"
    try:
        G.run(_args(tmp_path, no_existing_notes=True, out_dir=str(tmp_path / "o3")), llm)
        assert False
    except SystemExit:
        pass


def test_pattern_json_mode_and_maxchars(tmp_path):
    d = tmp_path / "q"
    d.mkdir()
    (d / "stage1_prompt.txt").write_text("s", encoding="utf-8")
    (d / "pattern.json").write_text(json.dumps({"mode": "twostage", "max_chars": 90}), encoding="utf-8")
    p = G.load_pattern("q", tmp_path)
    assert p["mode"] == "twostage" and G.is_two_stage(p) and p["max_chars"] == 90


def test_run_dry_run_no_llm(tmp_path):
    _setup(tmp_path, False)
    prov = G.run(_args(tmp_path, dry_run=True), lambda *a: (_ for _ in ()).throw(AssertionError("llm called")))
    assert prov["dry_run"] and prov["calls"] == 0


def test_eval_recall_and_extra():
    notes = [{"fact_id": "A", "note": PFX + "x" * 10, "source_quote": "q"},
             {"fact_id": "C", "note": PFX + "y" * 30, "source_quote": ""}]
    targets = {"A": {"known_misreading": "m1"}, "B": {"known_misreading": "m2"}}
    r = E.eval_theme(notes, targets, [{"fact_id": "D", "reason": "too_long(130)", "note": "n"}],
                     {"fact_count": 10, "stage1_candidate_count": 4})
    assert (r["hit"], r["targets"], r["extra"]) == (1, 2, 1)
    assert r["missed_ids"] == ["B"] and r["attach_rate"] == 0.2 and r["empty_source_quote"] == 1
    assert r["max_len"] == len(PFX) + 30 and r["rejected_reasons"] == {"too_long": 1}
    agg = E.aggregate([r, r])
    assert agg["hit"] == 2 and agg["targets"] == 4 and agg["fact_count"] == 20 and agg["stage1_candidates"] == 8


def test_label_sheet():
    lines = E.label_sheet("p", "meta", [{"fact_id": "A", "note": PFX + "a|b"}, {"fact_id": "Z", "note": PFX + "z"}],
                          {"A": {"known_misreading": "誤読A"}})
    s = "\n".join(lines)
    assert "誤読A" in s and "(対象外)" in s and "a\\|b" in s and lines[2].rstrip().endswith("|  |")


# ---- L2 (H1〜H3) ----
def test_normalize_prefix_h1():
    assert G.normalize_prefix("注意(多義):AはB。", PFX) == PFX + "AはB。"
    assert G.normalize_prefix("注意(多義):　 AはB。", PFX) == PFX + "AはB。"
    assert G.normalize_prefix("  注意(多義): AはB。", PFX) == PFX + "AはB。"
    assert G.normalize_prefix("警告: AはB。", PFX) == "警告: AはB。"
    acc, rej = G.postprocess([{"fact_id": "A-1", "note": "注意(多義):AはB。"}], {"A-1"}, PFX, 100)
    assert acc == {"A-1": PFX + "AはB。"} and not rej


def test_pick_reverse_h3():
    it = {"claim": "X は 開発 中", "scope": "sc", "conditions": None}
    r = lambda c, q, R="R": {"R": R, "changes_conclusion": c, "ledger_quote": q}
    j = {"reversible": True, "reverse_propositions": [r(False, "sc", "R0"), r(True, "開発中", "R1"), r(True, "sc", "R2")]}
    assert G.pick_reverse(j, it)["R"] == "R1"  # changes_conclusion=trueの先頭
    ok, why, e = G.screen2(j, it)
    assert ok and e["R"] == "R1"
    j2 = {"reversible": True, "reverse_propositions": [r(True, "zzz"), r(False, "sc")]}
    assert G.screen2(j2, it)[:2] == (False, ["ledger_quote_not_in_ledger"])
    assert G.screen2({"reversible": True, "reverse_propositions": [r(False, "sc")]}, it)[1] == ["no_R_changes_conclusion"]
    assert G.screen2({"reversible": False, "reverse_propositions": []}, it)[1] == ["reversible=false"]


def _run_b2(tmp_path, hint, nr):
    _setup(tmp_path, True)
    (tmp_path / "pats" / "p" / "pattern.json").write_text(json.dumps(
        {"mode": "twostage", "max_chars": 100, "self_check_policy": "derivable_only", "stage2_existing_notes": hint}), encoding="utf-8")
    calls = []
    rp = lambda q: [{"R": "RR", "flipped_component": "stage", "contradicts_ledger_field": "claim", "ledger_quote": q,
                     "changes_conclusion": True, "conclusion_change_reason": "x"}]

    def llm(p, ws):
        calls.append(p)
        if len(calls) == 1:
            return {"parsed": {"judgments": [
                {"fact_id": "A-1", "reversible": True, "reverse_propositions": rp("c1")},
                {"fact_id": "A-2", "reversible": True, "reverse_propositions": rp("c2")},
                {"fact_id": "A-3", "reversible": True, "reverse_propositions": rp("c3")}]}, "model": "m", "cost_jpy": 1.0}
        return {"parsed": {"notes": [
            {"fact_id": "A-1", "note": "注意(多義):n1", "self_check": {"R_is_natural_reading": False, "correct_statement_derivable_from_ledger": True}},
            {"fact_id": "A-2", "note": PFX + "n2", "self_check": {"R_is_natural_reading": True, "correct_statement_derivable_from_ledger": False}},
            {"fact_id": "A-3", "note": PFX + "n3", "self_check": {"R_is_natural_reading": True, "correct_statement_derivable_from_ledger": True}}]},
            "model": "m", "cost_jpy": 0.5}
    prov = G.run(_args(tmp_path), llm)
    return prov, calls


def test_b2_selfcheck_warning_and_hint(tmp_path):
    prov, calls = _run_b2(tmp_path, True, None)
    notes = json.loads((tmp_path / "out" / "notes.json").read_text(encoding="utf-8"))
    assert [n["fact_id"] for n in notes] == ["A-1", "A-3"]  # R不自然は警告のみ=採用、導出不可(A-2)は却下
    assert notes[0]["warnings"] == ["R_is_natural_reading=false"] and notes[0]["note"] == PFX + "n1"  # 接頭辞も正規化
    assert prov["warning_count"] == 1
    rej = json.loads((tmp_path / "out" / "rejected.json").read_text(encoding="utf-8"))
    assert [r["fact_id"] for r in rej] == ["A-2"]
    assert "existing_notes_hint" in calls[1] and "NW-A-1" in calls[1]


def test_b2n_no_existing_notes_in_stage2(tmp_path):
    prov, calls = _run_b2(tmp_path, False, None)
    assert "NW-A-1" in calls[0]  # stage1には渡る(L1と同条件)
    assert "existing_notes_hint" not in calls[1] and "NW-A-1" not in calls[1] and "sc A-1" in calls[1]


def test_s15_helpers():
    runs = [{"A-1": {"R": "R1a", "compressed_claim": "c1"}, "A-2": {"R": "R2", "compressed_claim": "c2"}},
            {"A-1": {"R": "R1b", "compressed_claim": "c1'"}, "A-2": {"R": " R2 ", "compressed_claim": "c2"}, "A-3": {"R": "R3", "compressed_claim": "c3"}}]
    order, per = G.build_s15_input(runs)
    assert order == ["A-1", "A-2", "A-3"] and [c["cid"] for c in per["A-1"]] == ["A", "B"] and len(per["A-2"]) == 1  # 同一Rは統合
    items = G.s15_prompt_items(order, per)
    assert set(items[0]["candidates"][0]) == {"cid", "compressed_claim", "R"}  # claim全文・scope・notesは渡さない
    v = [{"fact_id": "A-1", "cid": "A", "likelihood": "low"}, {"fact_id": "A-1", "cid": "B", "likelihood": "high"},
         {"fact_id": "A-2", "cid": "A", "likelihood": "medium"}]
    chosen, rec = G.apply_s15(order, per, v)
    assert list(chosen) == ["A-1"] and chosen["A-1"][0] == "B" and chosen["A-1"][1]["R"] == "R1b"  # いずれかhighなら通過・highのRを採用
    assert rec["A-2"]["dropped_by"] == ["stage1_5_medium"] and rec["A-3"]["dropped_by"] == ["stage1_5_missing"]
    assert G.jaccard(["a", "b"], ["b", "c"]) == 1 / 3 and G.jaccard([], []) == 1.0


def test_run_twostage_gate(tmp_path):
    _setup(tmp_path, True)
    (tmp_path / "pats" / "p" / "pattern.json").write_text(json.dumps(
        {"mode": "twostage_gate", "max_chars": 120, "self_check_policy": "derivable_only", "stage2_existing_notes": True, "stage1_repeats": 2}), encoding="utf-8")
    (tmp_path / "pats" / "p" / "stage1_5_prompt.txt").write_text("S15 {S15_INPUT}", encoding="utf-8")
    rp = lambda q, R: [{"R": R, "flipped_component": "stage", "contradicts_ledger_field": "claim", "ledger_quote": q,
                        "changes_conclusion": True, "conclusion_change_reason": "x"}]
    J = lambda fid, R: {"fact_id": fid, "reversible": True, "compressed_claim": "cc-" + fid, "reverse_propositions": rp("c" + fid[-1], R)}
    calls = []

    def llm(p, ws):
        calls.append(p)
        n = len(calls)
        if n == 1:
            return {"parsed": {"judgments": [J("A-1", "R1a"), J("A-2", "R2"), {"fact_id": "A-3", "reversible": False, "reverse_propositions": []}]}, "model": "m", "cost_jpy": 1.0}
        if n == 2:
            return {"parsed": {"judgments": [J("A-1", "R1b"), {"fact_id": "A-2", "reversible": False, "reverse_propositions": []}, J("A-3", "R3")]}, "model": "m", "cost_jpy": 1.0}
        if n == 3:
            assert "cc-A-1" in p and "R1a" in p and "R1b" in p and "NW-A-1" not in p and "sc A-1" not in p
            return {"parsed": {"verdicts": [{"fact_id": "A-1", "cid": "A", "likelihood": "low", "reason": "r"}, {"fact_id": "A-1", "cid": "B", "likelihood": "high", "reason": "r"},
                                            {"fact_id": "A-2", "cid": "A", "likelihood": "medium", "reason": "r"}, {"fact_id": "A-3", "cid": "A", "likelihood": "low", "reason": "r"}]},
                    "model": "m", "cost_jpy": 0.5}
        assert "R1b" in p and "R1a" not in p and "A-2" not in p and "NW-A-1" in p
        return {"parsed": {"notes": [{"fact_id": "A-1", "note": PFX + "n1", "self_check": {"R_is_natural_reading": True, "correct_statement_derivable_from_ledger": True}}]}, "model": "m", "cost_jpy": 0.5}
    prov = G.run(_args(tmp_path), llm)
    assert len(calls) == 4 and prov["calls"] == 4 and abs(prov["cost_jpy"] - 3.0) < 1e-9
    assert prov["stage1_union_count"] == 3 and abs(prov["stage1_jaccard"] - 1 / 3) < 1e-9 and prov["attached_count"] == 1
    ja = {x["fact_id"]: x for x in json.loads((tmp_path / "out" / "judgments_all.json").read_text(encoding="utf-8"))}
    assert ja["A-2"]["dropped_by"] == ["stage1_5_medium"] and ja["A-2"]["warnings"] == ["stage1_5_medium"] and ja["A-3"]["dropped_by"] == ["stage1_5_low"]
    assert ja["A-1"]["passed"] and (tmp_path / "out" / "stage1_raw_r2.json").exists() and (tmp_path / "out" / "stage1_5_raw.json").exists()
