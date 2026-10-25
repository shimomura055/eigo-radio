# er120_part2_grammar_production_01_test_01.py
# PART2-GRAMMAR-PRODUCTION-WIRING-01 委任_01: Part 2 Production module のtest(API 0。LLMは全てmock call_fn。実client生成はblock)。
#  A: Trial-07/08資産との同一性(Prompt byte一致・prompt sha一致・Step B prompt再現)
#  B: Trial-08結果の回帰(Trial-07/08の全29標本のraw応答 → 本moduleのparse → select_tiered が Trial-08結果と一致)
#  C: 選定・順位・HR接続(TOP1/TOP2・auto/wait・Human choice・再選定・0件)
#  D: LLM mock end-to-end(call数・resume再利用・retry上限・model不一致・parse不能を0件扱いにしない・予算guard)
#  E: 検証・描画(逐語span・fail-closed・描画規約・Dangling)
#  P: Production境界(未配線・routing未登録はfail-closed・Trial資産を参照しない)
# Trial資産(docs/research)はtestでのみ読む(moduleはimportしない)。
import copy
import glob
import hashlib
import inspect
import json
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
TRIAL = os.path.join(HERE, "docs", "research", "FAMILY-Z-STUDY-TEXT-TRIAL-01")
sys.path.insert(0, HERE)
import er006_model_routing_contract_01 as routing
import er120_part2_grammar_production_01 as m

# ---- API 0 の保証: 実clientの生成を全testでblock(呼ばれたら失敗) ----
API = {"real_client": 0}


@pytest.fixture(autouse=True)
def _block_real_client(monkeypatch):
    import er003_v1_b1_scaffold_01_generate as b1s

    def boom(*a, **k):
        API["real_client"] += 1
        raise AssertionError("real client must not be created in tests (API 0)")
    monkeypatch.setattr(b1s, "get_client", boom)
    yield
    assert API["real_client"] == 0


@pytest.fixture
def routed(monkeypatch):
    """次委任でer006へ追記する2 processを、test内だけで登録(本番のer006は無変更)。"""
    pm = dict(routing.PROCESS_MODEL_MAP)
    pm[m.PROCESS_EXTRACT] = routing.SUPPORT_MODEL
    pm[m.PROCESS_EXPLAIN] = routing.SUPPORT_MODEL
    monkeypatch.setattr(routing, "PROCESS_MODEL_MAP", pm)


def _trial():
    sys.path.insert(0, TRIAL)
    import run_trial_08 as t8
    import run_trial_07 as t7
    import run_trial_04 as t4
    return t8, t7, t4


needs_trial = pytest.mark.skipif(not os.path.isdir(TRIAL), reason="Trial assets absent")

# ============================================================
# A: Trial資産との同一性
# ============================================================


@needs_trial
def test_A1_prompts_byte_identical_to_trial():
    t8, t7, t4 = _trial()
    assert m.STEPA_PROMPT == t8.STEPA8                      # Step A'' = Trial-08(Trial-07の再確認1文のみ差替)
    assert m.STEPB_PROMPT == t4.STEPB                        # Step B = Trial-04 = Trial-07
    assert m.STEPA_PROMPT == t7.STEPA7.replace(t8.OLD_LINE, t8.NEW_LINE)
    assert m.STEPA_PROMPT.count(t8.NEW_LINE) == 1 and t8.OLD_LINE not in m.STEPA_PROMPT
    assert m.STEPA_PROMPT_SHA256 == "51912fe1e2428c347c09969f2f3e8831c73782d5669921e6508c15de8855e15c"
    assert m.STEPB_PROMPT_SHA256 == "59588b5961e88d1be052e9ae5045ed90ca243546d6996027b60336e3083b591c"


@needs_trial
@pytest.mark.parametrize("work", ["gift", "paw", "tth", "promise", "melos"])
def test_A2_full_stepA_prompt_sha_equals_paid_trial08_call(work):
    """有料で実際に送ったTrial-08のprompt_sha256と、本moduleが同じ本文・ラベルから作るpromptのshaが一致する。"""
    t8, t7, _ = _trial()
    d = t7.work_data7(work)
    p = m.stepa_prompt(d["body"], d["label"])
    for f in glob.glob(os.path.join(TRIAL, f"usage_08_08_r*_stepA8_{work}.json")):
        assert json.load(open(f, encoding="utf-8"))["prompt_sha256"] == hashlib.sha256(p.encode()).hexdigest(), f


@needs_trial
def test_A3_stepB_prompt_reproduces_paid_trial07_calls():
    """Trial-07 Step Bの実送信promptのsha256を、保存済み選定(OUTPUT_07 rule_selected.selected)から再現できる。"""
    n = 0
    for f in glob.glob(os.path.join(TRIAL, "usage_07_07_r1_stepB_*.json")):
        work = os.path.basename(f)[len("usage_07_07_r1_stepB_"):-5]
        sel = json.load(open(os.path.join(TRIAL, f"OUTPUT_07_{work}_r1_STEPA_DEV.json"), encoding="utf-8"))["rule_selected"]["selected"]
        sel = [{k: v for k, v in s.items() if k in ("para", "sentence", "construct_ja", "points_ja", "context_ja", "prev", "next", "ref_ja")} for s in sel]
        assert hashlib.sha256(m.stepb_prompt(sel).encode()).hexdigest() == json.load(open(f, encoding="utf-8"))["prompt_sha256"], work
        n += 1
    assert n >= 5


@needs_trial
def test_A4_constants_equal_trial():
    _, t7, t4 = _trial()
    assert (m.STRONG, m.MID, m.PRIORITY, m.TARGETS, m.FRONT_OK) == (t7.STRONG, t7.MID, t7.PRIORITY, t7.TARGETS, t7.FRONT_OK)
    assert (m.MAXOUT_EXTRACT, m.MAXOUT_EXPLAIN) == (t7.MAXOUT_A, t7.MAXOUT_B)
    assert m.ZERO_P2 == t4.ZERO_P2


# ============================================================
# B: 回帰(Trial-07/08の全29標本のraw応答)
# ============================================================
def _samples():
    out = []
    for f in sorted(glob.glob(os.path.join(TRIAL, "_raw_07_07_r*_stepA7_*.txt"))):
        r, work = re.match(r".*_raw_07_07_(r\d)_stepA7_(.+)\.txt", f.replace("\\", "/")).groups()
        out.append(("07", work, r, f))
    for f in sorted(glob.glob(os.path.join(TRIAL, "_raw_08_08_r*_stepA8_*.txt"))):
        r, work = re.match(r".*_raw_08_08_(r\d)_stepA8_(.+)\.txt", f.replace("\\", "/")).groups()
        out.append(("08", work, r, f))
    return out


@needs_trial
def test_B1_sample_count():
    s = _samples()
    assert len([x for x in s if x[0] == "07"]) == 18 and len([x for x in s if x[0] == "08"]) == 11


@needs_trial
@pytest.mark.parametrize("gen,work,run,path", _samples() if os.path.isdir(TRIAL) else [])
def test_B2_parse_and_select_tiered_match_trial(gen, work, run, path):
    """raw応答を本moduleでparse → select_tiered が Trial-08の保存結果(07標本はreselect_08.json、08標本はOUTPUT_08のrule_selected)と一致。
    featuresの逐語解決・適格判定・Tier表も保存値と一致。"""
    _, t7, _ = _trial()
    body = t7.work_data7(work)["body"]
    parsed = m.parse_candidates(open(path, encoding="utf-8").read(), body)
    sel, tier = m.select_tiered(parsed["features"])
    got = [(f["para"], m._cls(f), f["sentence"]) for f in sel]
    if gen == "08":
        saved = json.load(open(os.path.join(TRIAL, f"OUTPUT_08_{work}_{run}_STEPA_DEV.json"), encoding="utf-8"))
        exp = [(r["para"], r["feature_class"], r["sentence"]) for r in saved["rule_selected"]["records"]]
        assert tier == saved["rule_selected"]["tier"]
        assert [(t["para"], t["cls"], t["eligible"], t["tier"], t["why_not"]) for t in m.tier_table(parsed["features"])] == \
               [(t["para"], t["cls"], t["eligible"], t["tier"], t["why_not"]) for t in saved["tier_table"]]
        sv_feats = saved["features"]
    else:
        rs = json.load(open(os.path.join(TRIAL, "reselect_08.json"), encoding="utf-8"))[work][int(run[1:]) - 1]
        assert rs["run"] == run
        exp = [(r["para"], r["feature_class"], r["sentence"]) for r in rs["new"]]
        assert tier == rs["tier"]
        sv_feats = json.load(open(os.path.join(TRIAL, f"OUTPUT_07_{work}_{run}_STEPA_DEV.json"), encoding="utf-8"))["features"]
    assert got == exp
    keys = ("para", "sentence", "resolve_ok", "single_span_ok", "cross_para_flag", "prev", "next", "misread_quote_in_sentence")
    assert [{k: f.get(k) for k in keys} for f in parsed["features"]] == [{k: f.get(k) for k in keys} for f in sv_feats]
    # TOP1(rank_eligible先頭)は常にselect_tieredの1件と一致
    ranked = m.rank_eligible(parsed["features"])
    assert [(f["para"], m._cls(f)) for f, _ in ranked[:1]] == [(p, c) for p, c, _ in got]
    assert len({(f["para"], m._qn(f["sentence"])) for f, _ in ranked}) == len(ranked)      # 同一文の重複なし
    # Tier順: Tier1全件がTier2全件より前
    tiers = [t for _, t in ranked]
    assert tiers == sorted(tiers)


@needs_trial
def test_B3_representative_eight_works_match_trial08_table():
    """Trial-08代表標本(r1)の結果表: 倒置選定 8作品中1(賢者のみ)。"""
    _, t7, _ = _trial()
    expect = {"open_window": ("P29", "HEAVY"), "ig_nobel": ("P4", "CLEFT"), "gift": ("P22", "INV"), "paw": ("P18", None), "tth": ("P2", "POSTMOD"),
              "promise": None, "boredom": ("P7", "FRONT"), "melos": ("P11", "POSTMOD")}
    got = {}
    for gen, work, run, path in _samples():
        if run != "r1":
            continue
        if work in ("open_window", "ig_nobel", "boredom") and gen == "08":
            continue
        if work in ("gift", "paw", "tth", "promise", "melos") and gen == "07":
            continue
        parsed = m.parse_candidates(open(path, encoding="utf-8").read(), t7.work_data7(work)["body"])
        sel, _t = m.select_tiered(parsed["features"])
        got[work] = (sel[0]["para"], m._cls(sel[0])) if sel else None
    assert set(got) == set(expect)
    for w, e in expect.items():
        if e is None:
            assert got[w] is None, w
        else:
            assert got[w][0] == e[0] and (e[1] is None or got[w][1] == e[1]), (w, got[w])
    assert sum(1 for v in got.values() if v and v[1] == "INV") == 1


# ============================================================
# C: 選定・順位・HR接続
# ============================================================
PARAS = ["Under the bed lay a small box.",
         "It was in March that the plan changed.",
         "She found it impossible to refuse such an offer.",
         "Nothing else happened that day."]


def _feat(para, sent, cls, *, tv="HIGH", mq=None, target="SUBJECT", basic=False, fk="", om=""):
    return {"para": para, "sentence": sent, "feature_class": cls, "front_kind": fk, "misread_target": target,
            "misread_quote": sent.split()[0] if mq is None else mq, "misread_ja": "x", "omitted_words": om, "basic_only": basic,
            "teaching_value": tv, "teaching_value_ja": "読み方" if tv == "HIGH" else "", "construct_ja": "構文", "points_ja": ["p"], "context_ja": "ctx"}


def _stepa_json(*feats):
    return json.dumps({"features": list(feats), "no_feature_paras": []}, ensure_ascii=False)


F_INV = _feat("P1", PARAS[0], "INV")
F_CLEFT = _feat("P2", PARAS[1], "CLEFT")
F_SPEC = _feat("P3", PARAS[2], "SPEC", mq="impossible")


def _doc(*feats, paras=PARAS, label="Test Story"):
    parsed = m.parse_candidates(_stepa_json(*feats), paras)
    return m.build_candidates_doc(parsed, paras, label)


def test_C1_tier_order_inv_after_non_inv():
    d = _doc(F_INV, F_CLEFT, F_SPEC)
    assert [c["feature_class"] for c in d["candidates"]] == ["CLEFT", "SPEC", "INV"]              # Tier1(CLEFT>SPEC) → Tier2(INV)
    assert [c["tier"] for c in d["candidates"]] == ["T1", "T1", "T2"]
    assert [c["rank"] for c in d["candidates"]] == [1, 2, 3]
    assert d["top_ids"] == [d["candidates"][0]["candidate_id"], d["candidates"][1]["candidate_id"]]
    assert d["n_eligible"] == 3 and d["status"] == "HAS_CANDIDATES"


def test_C2_inv_only_remains_not_excluded():
    d = _doc(F_INV)
    assert [c["tier"] for c in d["candidates"]] == ["T2"] and len(d["top_ids"]) == 1


def test_C3_low_value_inv_not_forced_zero():
    d = _doc(_feat("P1", PARAS[0], "INV", tv="LOW"))
    assert d["status"] == "NO_CANDIDATE" and d["candidates"] == [] and d["top_ids"] == []


def test_C4_ineligible_recorded_with_reason():
    d = _doc(_feat("P1", PARAS[0], "INV", basic=True), _feat("P2", PARAS[1], "OTHER"))
    assert d["status"] == "NO_CANDIDATE"
    assert any("basic_only" in t["why_not"] for t in d["tier_table"]) and any("class=OTHER" in t["why_not"] for t in d["tier_table"])


def test_C5_same_sentence_not_listed_twice():
    d = _doc(F_CLEFT, dict(F_CLEFT, feature_class="SPEC", misread_quote="plan"), F_SPEC)
    sents = [c["sentence"] for c in d["candidates"]]
    assert len(sents) == len(set(sents)) == 2


def test_C6_select_matrix_and_no_silent_final_approval():
    d = _doc(F_INV, F_CLEFT, F_SPEC)
    c1, c2 = d["candidates"][0], d["candidates"][1]
    rv = lambda ch, sha=None: {"choice": ch, "candidates_sha256": sha or d["candidates_sha256"]}
    s = m.select_from_candidates(d, None, "auto")
    assert s["status"] == "SELECTED" and s["candidate"] == c1 and s["source"] == "auto_top1"          # Human不介入=TOP1(明示auto時のみ)
    s = m.select_from_candidates(d, None, "wait")
    assert s["status"] == "PENDING_REVIEW" and s["candidate"] is None                                  # 既定は待機。勝手に確定しない
    assert m.select_from_candidates(d, rv("top1"), "wait")["candidate"] == c1
    assert m.select_from_candidates(d, rv("top2"), "wait")["candidate"] == c2
    assert m.select_from_candidates(d, rv("top2"), "auto")["source"] == "human_top2"
    assert m.select_from_candidates(d, rv("omit"), "wait") == {"status": "ZERO", "candidate": None, "source": "human_omit"}
    assert m.select_from_candidates(d, rv("reselect"), "wait")["status"] == "RESELECT_REQUESTED"
    with pytest.raises(m.Part2ReviewError):
        m.select_from_candidates(d, rv("top3"), "wait")
    with pytest.raises(m.Part2ReviewError):
        m.select_from_candidates(d, rv("top1", "0" * 64), "wait")                                      # stale review
    with pytest.raises(m.Part2ReviewError):
        m.select_from_candidates(d, None, "maybe")
    one = _doc(F_CLEFT)
    with pytest.raises(m.Part2ReviewError):
        m.select_from_candidates(one, {"choice": "top2", "candidates_sha256": one["candidates_sha256"]}, "wait")


def test_C7_zero_candidates_needs_no_review_and_is_not_pending():
    d = _doc()
    assert m.select_from_candidates(d, None, "wait") == {"status": "ZERO", "candidate": None, "source": "no_candidate"}
    rq = m.review_request(d)
    assert rq["choices"] == ["omit"] and rq["ai_recommended"] is None and rq["auto_default"] == "omit"


def test_C8_review_request_for_er119_kind_grammar():
    d = _doc(F_INV, F_CLEFT, F_SPEC)
    rq = m.review_request(d)
    assert rq["kind"] == "grammar" and [t["rank"] for t in rq["top"]] == [1, 2] and rq["n_more"] == 1
    assert rq["ai_recommended"] == d["candidates"][0]["candidate_id"] and rq["choices"] == ["top1", "top2", "reselect", "omit"]
    assert rq["candidates_sha256"] == d["candidates_sha256"] and rq["auto_default"] == "top1"


def test_C9_reselect_is_api_free_and_cumulative_and_exhausts():
    d = _doc(F_INV, F_CLEFT, F_SPEC)
    ids = [c["candidate_id"] for c in d["candidates"]]
    d2 = m.reselect_candidates(d, [ids[0]])
    assert [c["candidate_id"] for c in d2["candidates"]] == ids[1:] and d2["round"] == 2 and d2["rejected_ids"] == [ids[0]]
    assert [c["rank"] for c in d2["candidates"]] == [1, 2] and d2["candidates_sha256"] != d["candidates_sha256"] and not d2.get("exhausted")
    d3 = m.reselect_candidates(d2, ids[1:])
    assert d3["status"] == "NO_CANDIDATE" and d3["exhausted"] is True and d3["rejected_ids"] == ids
    # 再抽出時にrejected_idsを渡すと同じ候補は戻らない
    parsed = m.parse_candidates(_stepa_json(F_INV, F_CLEFT, F_SPEC), PARAS)
    d4 = m.build_candidates_doc(parsed, PARAS, "x", rejected_ids=tuple(ids[:2]))
    assert [c["candidate_id"] for c in d4["candidates"]] == [ids[2]]


def test_C10_candidate_id_is_stable():
    assert _doc(F_INV, F_CLEFT)["candidates"][0]["candidate_id"] == _doc(F_CLEFT)["candidates"][0]["candidate_id"]


# ============================================================
# D: LLM mock end-to-end
# ============================================================
STEPB_OK = ("=====ITEM 1=====\n【日本語訳】\n三月に計画が変わったのだ。\n【文法・構文の仕組み】\n**It was** と **that** で強調する文です。\n"
            "【通常の表現・語順との比較】\n比較用：**The plan changed in March.**\n【意味・ニュアンス・表現効果】\n時期に焦点が当たります。\n")
TR_OK = json.dumps({"translations": [{"id": 1, "ja": "計画が変わったのは三月のことだった。"}]}, ensure_ascii=False)
MODEL = routing.SUPPORT_MODEL


class LLM:
    def __init__(self, text, model=MODEL, fail_first=0):
        self.text, self.model, self.n, self.fail_first, self.prompts = text, model, 0, fail_first, []

    def __call__(self, prompt):
        self.n += 1
        self.prompts.append(prompt)
        t = "garbage" if self.n <= self.fail_first else self.text
        return t, self.model, {"input_tokens": 1000, "output_tokens": 500, "cached_input_tokens": 0}, f"resp_{self.n}"


def _run(routed_, **kw):
    ex = kw.pop("ex", LLM(_stepa_json(F_INV, F_CLEFT, F_SPEC)))
    xp = kw.pop("xp", LLM(STEPB_OK))
    tr = kw.pop("tr", LLM(TR_OK))
    kw.setdefault("mode", "auto")
    r = m.run_part2(PARAS, "Test Story", extract_call_fn=ex, explain_call_fn=xp, translate_call_fn=tr, **kw)
    return r, ex, xp, tr


def test_D1_first_run_auto_three_calls_and_result(routed):
    r, ex, xp, tr = _run(routed)
    assert (ex.n, tr.n, xp.n) == (1, 1, 1) and r["status"] == "SELECTED"
    res = r["result"]
    assert res["selection"]["feature_class"] == "CLEFT" and res["selection"]["source"] == "auto_top1" and res["translation_source"] == "T1"
    assert res["translation_ja"] in xp.prompts[0] and "参考訳(別工程で確定済み)" in xp.prompts[0]            # T1訳をStep Bへ参考訳として渡す
    assert set(res["sections"]) == {"日本語訳", "文法・構文の仕組み", "通常の表現・語順との比較", "意味・ニュアンス・表現効果"}
    assert res["audit"]["extract"]["model"] == MODEL and res["audit"]["explain"]["process"] == m.PROCESS_EXPLAIN
    assert res["audit"]["explain"]["prompt_template_sha256"] == m.STEPB_PROMPT_SHA256
    assert res["audit"]["extract"]["prompt_template_sha256"] == m.STEPA_PROMPT_SHA256
    m.require_fresh_part2(res, PARAS, "Test Story", next_command="x")


def test_D2_resume_reuses_everything_api_zero(routed):
    r1, *_ = _run(routed)
    r2, ex, xp, tr = _run(routed, cached_candidates=r1["candidates"], cached_result=r1["result"])
    assert (ex.n, tr.n, xp.n) == (0, 0, 0) and r2["result"]["reused_from_previous_run"] is True and r2["candidates"]["reused_from_previous_run"] is True
    assert r2["result"]["explanation_md"] == r1["result"]["explanation_md"]


def test_D3_body_change_regenerates_but_label_same(routed):
    r1, *_ = _run(routed)
    paras2 = PARAS[:3] + ["Nothing else happened on that day."]
    ex, xp, tr = LLM(_stepa_json(F_INV, F_CLEFT, F_SPEC)), LLM(STEPB_OK), LLM(TR_OK)
    r2 = m.run_part2(paras2, "Test Story", mode="auto", cached_candidates=r1["candidates"], cached_result=r1["result"],
                     extract_call_fn=ex, explain_call_fn=xp, translate_call_fn=tr)
    assert ex.n == 1                                                                                    # 本文shaが違えば再抽出
    with pytest.raises(m.Part2Stale):
        m.require_fresh_part2(r1["result"], paras2, "Test Story", next_command="cmd")


def test_D4_human_choice_changes_selection_and_regenerates_explanation_only(routed):
    r1, *_ = _run(routed)
    d = r1["candidates"]
    ex, xp, tr = LLM("unused"), LLM(STEPB_OK), LLM(TR_OK)
    r2 = m.run_part2(PARAS, "Test Story", mode="wait", review={"choice": "top2", "candidates_sha256": d["candidates_sha256"]},
                     cached_candidates=d, cached_result=r1["result"], extract_call_fn=ex, explain_call_fn=xp, translate_call_fn=tr)
    assert ex.n == 0 and tr.n == 1 and xp.n == 1                                                         # 候補は再利用・TOP2の解説のみ新規
    assert r2["result"]["selection"]["rank"] == 2 and r2["result"]["selection"]["source"] == "human_top2"


def test_D5_pending_review_makes_no_paid_downstream_call(routed):
    r, ex, xp, tr = _run(routed, mode="wait")
    assert r["status"] == "PENDING_REVIEW" and r["result"] is None and r["review_request"]["kind"] == "grammar"
    assert (ex.n, tr.n, xp.n) == (1, 0, 0)


def test_D6_zero_candidates_no_downstream_calls(routed):
    r, ex, xp, tr = _run(routed, ex=LLM(_stepa_json(_feat("P1", PARAS[0], "INV", tv="LOW"))))
    assert r["status"] == "ZERO" and r["result"]["status"] == "ZERO" and r["result"]["zero_reason"] == "no_candidate" and (tr.n, xp.n) == (0, 0)
    assert m.render_markdown(r["result"]).strip().endswith(m.ZERO_P2)
    m.require_fresh_part2(r["result"], PARAS, "Test Story", next_command="x")


def test_D7_ref_ja_pool_skips_t1_call(routed):
    pool = {m._norm_sentence(PARAS[1]): "計画が変わったのは三月だ。"}
    r, ex, xp, tr = _run(routed, ref_ja_pool=pool)
    assert tr.n == 0 and r["result"]["translation_source"] == "part1_pool" and "計画が変わったのは三月だ。" in xp.prompts[0]


def test_D8_technical_retry_once_then_fail_closed(routed):
    r, ex, xp, tr = _run(routed, ex=LLM(_stepa_json(F_CLEFT), fail_first=1))
    assert ex.n == 2 and r["candidates"]["audit"]["retried_for_parse"] is True                            # 構造不正→retry1回で成功
    with pytest.raises(m.Part2Error):
        _run(routed, ex=LLM("garbage", fail_first=99))
    ex2 = LLM("garbage", fail_first=99)
    with pytest.raises(m.Part2Error):
        _run(routed, ex=ex2)
    assert ex2.n == 2                                                                                    # 上限は初回+retry1回


def test_D9_unparseable_extract_is_never_treated_as_zero(routed):
    with pytest.raises(m.Part2Error):
        _run(routed, ex=LLM("{not json", fail_first=0))


def test_D10_explain_structure_failures_fail_closed(routed):
    bad = STEPB_OK.replace("【文法・構文の仕組み】", "【意味】")
    xp = LLM(bad)
    with pytest.raises(m.Part2Error):
        _run(routed, xp=xp)
    assert xp.n == 2
    with pytest.raises(m.Part2Error):
        _run(routed, xp=LLM(STEPB_OK + "\n(B1)"))                                                      # ページ非表示語


def test_D11_model_mismatch_stops_without_retry_or_fallback(routed):
    ex = LLM(_stepa_json(F_CLEFT), model="gpt-6.1-sol")
    with pytest.raises(m.Part2Error, match="不一致"):
        _run(routed, ex=ex)
    assert ex.n == 1


def test_D12_budget_guard_called_before_each_llm_call(routed):
    seen = []
    _run(routed, budget_guard=lambda stage, est: seen.append((stage, est)))
    assert [s for s, _ in seen] == ["part2_extract", "part2_translate", "part2_explain"]


def test_D13_budget_guard_can_stop_before_api(routed):
    def stop(stage, est):
        raise RuntimeError("budget stop")
    ex = LLM(_stepa_json(F_CLEFT))
    with pytest.raises(RuntimeError):
        _run(routed, ex=ex, budget_guard=stop)
    assert ex.n == 0


def test_D14_t1_failure_is_fail_closed(routed):
    with pytest.raises(Exception):
        _run(routed, tr=LLM("garbage", fail_first=99))


# ============================================================
# E: 検証・描画・Dangling
# ============================================================
def test_E1_resolve_cross_paragraph_quote_regression():
    """Trial-07 open_window r2 P21の引用文連結(コロン終わり+次段落の引用)を、本moduleのparseが誤修復せず主張段落のspanへ再解決する。"""
    paras = ["Across the quiet garden came a young voice:", "“Bertie, why do you bound?”", "Nothing more."]
    f = _feat("P1", "Across the quiet garden came a young voice: “Bertie, why do you bound?”", "INV", mq="Across")
    p = m.parse_candidates(_stepa_json(f), paras)["features"][0]
    assert p["resolve_ok"] and p["sentence"] == paras[0] and p["cross_para_flag"] == "cross_para_trimmed_tail" and p["single_span_ok"]
    g = _feat("P1", "Totally different words that are not in the text at all.", "INV")
    assert m.parse_candidates(_stepa_json(g), paras)["features"][0]["resolve_ok"] is False                 # 誤修復しない


def test_E2_unresolvable_sentence_is_not_a_candidate():
    d = _doc(_feat("P1", "Under the bed lay a large trunk.", "INV"))
    assert d["status"] == "NO_CANDIDATE"


def test_E3_fresh_check_detects_tampering(routed):
    r, *_ = _run(routed)
    res = copy.deepcopy(r["result"])
    res["selection"]["sentence"] = "Under the bed lay a small box"                                       # 改変(末尾.欠落でもspanだが候補IDが不一致)
    with pytest.raises(m.Part2Stale):
        m.require_fresh_part2(res, PARAS, "Test Story", next_command="cmd")
    res2 = copy.deepcopy(r["result"])
    res2["explanation_md"] = ""
    with pytest.raises(m.Part2Stale, match="cmd"):
        m.require_fresh_part2(res2, PARAS, "Test Story", next_command="cmd")
    with pytest.raises(m.Part2Stale):
        m.require_fresh_part2(None, PARAS, "Test Story", next_command="cmd")


def test_E4_render_markdown_and_html_conventions(routed):
    r, *_ = _run(routed)
    md = m.render_markdown(r["result"])
    assert md.startswith("# Grammar & Sentence Structure") and "Part 2" not in md and PARAS[1] in md and "**日本語訳**" in md
    h = m.render_html_block(r["result"])
    assert "<section class='study'>" in h and "<h3>Grammar &amp; Sentence Structure</h3>" in h and "<table" not in h and "<h2" not in h
    assert "<b>It was</b>" in h and PARAS[1] in h and "<style>" in h
    assert "<style>" not in m.render_html_block(r["result"], include_css=False)                             # Part 1直後に連結する場合
    assert not m.PAGE_FORBIDDEN_RE.search(h)
    z = m.render_html_block(m.zero_result(r["candidates"], "no_candidate"))
    assert m.ZERO_P2 in z


def test_E5_write_and_load_artifacts(routed, tmp_path):
    r, *_ = _run(routed)
    out = m.write_artifacts(str(tmp_path / "study_text"), r["candidates"], r["result"])
    assert os.path.basename(out["candidates"]) == "grammar_candidates.json" and os.path.basename(out["result"]) == "part2_result.json"
    again = m.run_part2(PARAS, "Test Story", mode="auto", cached_candidates=m.load_json(out["candidates"]), cached_result=m.load_json(out["result"]),
                        extract_call_fn=LLM("x"), explain_call_fn=LLM("x"), translate_call_fn=LLM("x"))
    assert again["result"]["reused_from_previous_run"] is True
    assert open(out["md"], encoding="utf-8").read() == m.render_markdown(r["result"])


def test_E6_paragraphs_from_article_md():
    txt = "# Title\n\nPara one.\n\nPara two.\n\n## In one line\n\nsummary\n"
    assert m.paragraphs_from_article_md(txt) == ["Para one.", "Para two."]
    assert m.paragraphs_from_article_md(txt, stop_heading_prefixes=()) == ["Para one.", "Para two.", "## In one line", "summary"]
    with pytest.raises(m.Part2InputError):
        m.paragraphs_from_article_md("no title\n\nx")


@needs_trial
def test_E7_paragraphs_from_article_md_matches_trial_for_boredom_and_melos():
    _, t7, _ = _trial()
    for w in ("boredom", "melos"):
        path, _label, dol = t7.SRC7[w]
        txt = open(os.path.join(HERE, path), encoding="utf-8").read()
        assert m.paragraphs_from_article_md(txt, stop_heading_prefixes=("## In one line",) if dol else ()) == t7.work_data7(w)["body"]


def test_E8_input_validation_before_any_call(routed):
    ex = LLM("x")
    for bad in ([], [""], "text", None):
        with pytest.raises(m.Part2InputError):
            m.run_part2(bad, "L", extract_call_fn=ex)
    with pytest.raises(m.Part2InputError):
        m.stepa_prompt(PARAS, "multi\nline")
    assert ex.n == 0


# ============================================================
# P: Production境界
# ============================================================
def test_P1_unregistered_routing_is_fail_closed_before_api():
    ex = LLM(_stepa_json(F_CLEFT))
    with pytest.raises(routing.ModelContractViolation):
        m.extract_candidates(PARAS, "x", call_fn=ex)
    assert ex.n == 0
    assert m.PROCESS_EXTRACT not in routing.PROCESS_MODEL_MAP and m.PROCESS_EXPLAIN not in routing.PROCESS_MODEL_MAP   # 次委任でer006へ追記(本委任はer006無変更)
    assert m.REQUIRED_ROUTING_ENTRIES == {m.PROCESS_EXTRACT: "SUPPORT_MODEL", m.PROCESS_EXPLAIN: "SUPPORT_MODEL"}


def test_P2_module_does_not_reference_trial_assets():
    src = open(os.path.join(HERE, "er120_part2_grammar_production_01.py"), encoding="utf-8").read()
    body = "\n".join(l for l in src.split("\n") if not l.lstrip().startswith("#"))
    assert not re.search(r"^\s*(import|from)\s+(run_trial_|analyze_)", body, re.M)
    assert "FAMILY-Z-STUDY-TEXT-TRIAL-01" not in body and "docs/research" not in body and "docs\\research" not in body
    assert not re.search(r"os\.environ", body)                                                           # 環境変数でON/OFFを変えない


def test_P3_no_production_file_imports_the_module_yet():
    """委任_01時点では未配線(runner/er119/ページ無改変)。次委任でhookを入れる際はこのtestを『配線済み』assertへ置換する。"""
    me = os.path.basename(__file__)
    offenders = []
    for f in glob.glob(os.path.join(HERE, "*.py")):
        b = os.path.basename(f)
        if b in (me, "er120_part2_grammar_production_01.py"):
            continue
        if "er120_part2_grammar_production_01" in open(f, encoding="utf-8", errors="ignore").read():
            offenders.append(b)
    assert offenders == [], offenders


def test_P4_public_api_signatures():
    assert list(inspect.signature(m.stepa_prompt).parameters) == ["paragraphs", "label"]
    assert list(inspect.signature(m.select_from_candidates).parameters) == ["doc", "review", "mode"]
    assert inspect.signature(m.run_part2).parameters["mode"].default == "wait"                           # 既定は待機(自動確定は明示宣言のみ)
    assert inspect.signature(m.run_part2).parameters["review"].default is None


def test_P5_defaults_are_the_approved_values():
    assert m.MODEL == routing.SUPPORT_MODEL == "gpt-6-luna" and m.TOP_N == 2 and m.LEVEL == "Advanced"


@needs_trial
def test_A5_structure_check_accepts_all_real_trial07_stepB_outputs():
    """構造検査(必須3見出し・順序・日本語含有・ページ非表示語)が、Trial-07の実Step B出力(有料7件)を1件も誤って落とさない。"""
    fs = sorted(glob.glob(os.path.join(TRIAL, "_raw_07_07_r1_stepB_*.txt")))
    assert len(fs) == 7
    for f in fs:
        r = m._parse_stepb_checked(open(f, encoding="utf-8").read())
        assert set(r["sections"]) >= set(m.EXPLANATION_REQUIRED), f
