# -*- coding: utf-8 -*-
"""R5(委任_04)のtest。API 0円・Production非接続(FakeClient)。"""
import copy
import json
import os
import shutil
import types

import er019_family_x_storyline_b3_fact_selection_01 as b3mod
import er115_fx_numeric_retention_trial_01 as D
import er115_fx_numeric_r5_score_01 as S

ROOT = D.ROOT
IG_P2 = os.path.join(ROOT, "er115_output", "fx_numeric_retention_trial_01", "ig_nobel_2026", "A", "p2")


def _copy_b3(tmp_path, items):
    d = tmp_path / "s"
    shutil.copytree(os.path.join(IG_P2, "storyline_b3"), d / "storyline_b3")
    with open(d / "storyline_b3" / (D.B3_FIELD_NAME + ".json"), "w", encoding="utf-8") as f:
        json.dump({"items": items}, f, ensure_ascii=False)
    return str(d)


def test_with_field_schema_does_not_mutate_production_schema():
    before = copy.deepcopy(b3mod.STORYLINE_B3_JSON_SCHEMA)
    t = D.with_field_schema({"format": {"type": "json_schema", **b3mod.STORYLINE_B3_JSON_SCHEMA}})
    assert b3mod.STORYLINE_B3_JSON_SCHEMA == before
    assert D.B3_FIELD_NAME not in b3mod.STORYLINE_B3_JSON_SCHEMA["schema"]["properties"]
    sch = t["format"]["schema"]
    assert sch["properties"][D.B3_FIELD_NAME] == {"type": "array", "items": {"type": "string"}}
    assert D.B3_FIELD_NAME in sch["required"] and sch["additionalProperties"] is False


def test_v3_addendum_extends_v2_and_v1_v2_unchanged():
    assert D.B3_ADDENDUM_V3.startswith(D.B3_ADDENDUM_V2)
    assert D.B3_ADDENDUM_V3_FIELD in D.B3_ADDENDUM_V3
    for w in ("重要なほど多く入れるのではなく", "最大2個", "空の配列", "言葉による説明では十分に代替できない", "読みやすさやストーリーの流れ"):
        assert w in D.B3_ADDENDUM_V3_FIELD
    assert D.B3_ADDENDA["v1"] is D.B3_ADDENDUM and D.B3_ADDENDA["v2"] is D.B3_ADDENDUM_V2


def test_defaults_off_no_field_without_v3():
    import inspect
    assert inspect.signature(D.run_b3_dev).parameters["addendum_version"].default == "v1"
    assert inspect.signature(D._AddendumClient.__init__).parameters["field_schema"].default is False
    assert "os.environ" not in open(D.__file__, encoding="utf-8").read()


class _Resp:
    def __init__(self, rid, obj):
        self.id, self.output_text, self.model = rid, json.dumps(obj, ensure_ascii=False), "m"


class _Fake:
    def __init__(self, objs):
        self.objs, self.kws = list(objs), []
        outer = self

        class R:
            def create(self_i, **kw):
                outer.kws.append(kw)
                return _Resp("resp_%d" % len(outer.kws), outer.objs.pop(0))
        self.responses = R()


def test_wrapper_adds_field_schema_and_saves_matching_final_response(tmp_path):
    fake = _Fake([{"x": 1, D.B3_FIELD_NAME: ["A"]}, {"x": 2, D.B3_FIELD_NAME: ["3倍超"]}])
    w = D._AddendumClient(fake, "ADD", field_schema=True)
    base = {"format": {"type": "json_schema", **b3mod.STORYLINE_B3_JSON_SCHEMA}}
    for _ in range(2):
        w.responses.create(model="m", text=base, input=[{"role": "user", "content": "u"}])
    assert D.B3_FIELD_NAME in fake.kws[0]["text"]["format"]["schema"]["properties"]
    assert D.B3_FIELD_NAME not in base["format"]["schema"]["properties"]
    assert fake.kws[0]["input"][-1]["content"] == "uADD"
    d = tmp_path / "o"
    (d / "storyline_b3").mkdir(parents=True)
    json.dump({"response_id": "resp_2"}, open(d / "storyline_b3" / "runtime_evidence.json", "w"))
    rec = D.save_field_from_calls(str(d), w)
    assert rec["items"] == ["3倍超"] and rec["matched_final_response"] is True
    assert [c["items"] for c in rec["all_calls"]] == [["A"], ["3倍超"]]


def test_wrapper_without_field_schema_leaves_text_untouched():
    fake = _Fake([{"a": 1}])
    w = D._AddendumClient(fake, "ADD")
    base = {"format": {"type": "json_schema", **b3mod.STORYLINE_B3_JSON_SCHEMA}}
    w.responses.create(model="m", text=base, input=[{"role": "user", "content": "u"}])
    assert fake.kws[0]["text"] is base


def test_derive_E_r5_picks_field_number_even_if_storyline_has_none(tmp_path):
    d = _copy_b3(tmp_path, ["同質量の哺乳類の乳の3倍超"])
    E = D.derive_E_r5(d)
    assert E["ok"] and [e["news_surface"] for e in E["gate_E"]] == ["3倍"]
    assert E["source"] == D.B3_FIELD_NAME and E["storyline_consistency"]["match"] is False
    assert E["storyline_consistency"]["field_not_in_storyline"] == ["3倍"]


def test_derive_E_r5_empty_field_is_empty_E(tmp_path):
    E = D.derive_E_r5(_copy_b3(tmp_path, []))
    assert E["ok"] and E["gate_E"] == [] and E["candidates"] == []


def test_derive_E_r5_violations(tmp_path):
    E = D.derive_E_r5(_copy_b3(tmp_path, ["3倍超", "1.2 Å", "2026年9月3日"]))
    reasons = [v["reason"] for v in E["violations"]]
    assert not E["ok"] and any(r.startswith("too_many") for r in reasons) and E["gate_E"] == []
    E2 = D.derive_E_r5(_copy_b3(tmp_path / "x", ["とても大きい"]))
    assert not E2["ok"] and E2["violations"][0]["reason"] == "field_item_no_numeric_surface"
    E3 = D.derive_E_r5(_copy_b3(tmp_path / "y", ["99999倍"]))
    assert not E3["ok"] and E3["violations"][0]["reason"] == "unmapped_to_news_field"


def test_storyline_path_of_derive_E_unchanged():
    d = os.path.join(ROOT, "er115_output", "fx_numeric_retention_trial_01", "moon_shrinking", "A", "v2s1")
    E = D.derive_E(d)
    assert E["ok"] and [c["news_surface"] for c in E["candidates"]] == ["約42〜46"]


def test_score_classify_ja_three_classes():
    c = S.classify_ja("月は約42から46メートル縮んだ。約750メートルのずれと3倍の差。2025年に約4億年前の話。", "moon_shrinking")
    assert c["must"] == ["約42〜46"]
    assert c["unneeded_total"] == 2   # 約750 m(表), 3倍(未分類)
    assert c["optional"] and c["context"]
    ig = S.classify_ja("結晶は同じ重さの乳の3倍を超える。1.2オングストロームの分解能。", "ig_nobel_2026")
    assert ig["must"] == ["3倍"] and ig["unneeded_total"] == 1


def test_score_diff_counts_added_removed():
    b = S.classify_ja("約750メートル", "moon_shrinking")
    a = S.classify_ja("約42から46メートル", "moon_shrinking")
    d = S.diff_before_after(b, a)
    assert d["unneeded_delta"] == -1 and d["must"]["added"] == ["約42〜46"]
