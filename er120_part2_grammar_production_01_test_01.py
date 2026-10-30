# er120_part2_grammar_production_01_test_01.py
# PART2-GRAMMAR-PRODUCTION-WIRING-01 委任_01+委任_02: Part 2 Production module のtest(API 0。LLMは全てmock call_fn。実client生成はblock)。
#  M: 委任_02 Opus条件Aレビュー反映(M-1〜M-7・R-1/R-3/R-4/R-7)のtest(ファイル末尾)
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
    assert not hasattr(m, "ZERO_P2")     # 文法0件の固定文面は撤去(コーナー全体を非表示。R-13: Trial定数との一致assertは削除)


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
    return m.build_candidates_doc(parsed, paras, label, level="b1b")


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
    rv = lambda ch, sha=None: {"choice": ch, "candidates_sha256": sha or d["candidates_sha256"], "reason": "r"}
    s = m.select_from_candidates(d, None, AUTO)
    assert s["status"] == "SELECTED" and s["candidate"] == c1 and s["source"] == "auto_top1"          # Human不介入=TOP1(明示auto時のみ)
    s = m.select_from_candidates(d, None, "wait")
    assert s["status"] == "PENDING_REVIEW" and s["candidate"] is None                                  # 既定は待機。勝手に確定しない
    assert m.select_from_candidates(d, rv("top1"), "wait")["candidate"] == c1
    assert m.select_from_candidates(d, rv("top2"), "wait")["candidate"] == c2
    assert m.select_from_candidates(d, rv("top2"), AUTO)["source"] == "human_top2"
    o = m.select_from_candidates(d, rv("omit"), "wait")
    assert (o["status"], o["candidate"], o["source"], o["review_status"]) == ("ZERO", None, "human_omit", "REVIEWED")
    assert m.select_from_candidates(d, rv("reselect"), "wait")["status"] == "RESELECT_REQUESTED"
    with pytest.raises(m.Part2ReviewError):
        m.select_from_candidates(d, rv("top3"), "wait")
    with pytest.raises(m.Part2ReviewError):
        m.select_from_candidates(d, rv("top1", "0" * 64), "wait")                                      # stale review
    with pytest.raises(m.Part2ReviewError):
        m.select_from_candidates(d, None, "maybe")
    with pytest.raises(m.Part2ReviewError):
        m.select_from_candidates(d, None, "auto")                                                       # M-3: 文字列autoは不可
    one = _doc(F_CLEFT)
    with pytest.raises(m.Part2ReviewError):
        m.select_from_candidates(one, {"choice": "top2", "candidates_sha256": one["candidates_sha256"], "reason": "r"}, "wait")


def test_C7_zero_candidates_needs_no_review_and_is_not_pending():
    d = _doc()
    s = m.select_from_candidates(d, None, "wait")
    assert (s["status"], s["candidate"], s["source"], s["review_status"]) == ("ZERO", None, "no_candidate", "NO_CANDIDATE_UNREVIEWED")   # M-6: REVIEWEDではない
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
    d2 = m.reselect_candidates(d, [ids[0]], reason="r1")
    assert [c["candidate_id"] for c in d2["candidates"]] == ids[1:] and d2["round"] == 2 and d2["rejected_ids"] == [ids[0]]
    assert [c["rank"] for c in d2["candidates"]] == [1, 2] and d2["candidates_sha256"] != d["candidates_sha256"] and not d2.get("exhausted")
    d3 = m.reselect_candidates(d2, ids[1:], reason="r2")
    assert d3["status"] == "NO_CANDIDATE" and d3["exhausted"] is True and d3["rejected_ids"] == ids
    # 再抽出時にrejected_idsを渡すと同じ候補は戻らない
    parsed = m.parse_candidates(_stepa_json(F_INV, F_CLEFT, F_SPEC), PARAS)
    d4 = m.build_candidates_doc(parsed, PARAS, "x", rejected_ids=tuple(ids[:2]), level="b1b")
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
AUTO = {"mode": "auto", "declared_by": "tester", "declared_at": "2026-10-25T00:00:00+0900", "reason": "unit test", "source": "declare_absent_cli"}


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
    tr = kw.pop("tr", LLM(TR_OK))        # M-1: T1訳callは廃止。run_part2に渡さず、呼ばれないこと(n==0)をassertする
    kw.setdefault("mode", AUTO)
    r = m.run_part2(PARAS, "Test Story", extract_call_fn=ex, explain_call_fn=xp, **kw, level="b1b")
    return r, ex, xp, tr


def _fresh(r, nxt="x", paras=PARAS, **kw):
    m.require_fresh_part2(r["result"], paras, "Test Story", next_command=nxt, candidates_doc=r["candidates"], grammar_review=r["review_record"], **kw)


def test_D1_first_run_auto_two_calls_and_result(routed):
    r, ex, xp, tr = _run(routed)
    assert (ex.n, tr.n, xp.n) == (1, 0, 1) and r["status"] == "SELECTED"                                  # M-1: T1訳call=0
    res = r["result"]
    assert res["selection"]["feature_class"] == "CLEFT" and res["selection"]["source"] == "auto_top1" and res["translation_source"] == "stepB"
    assert "参考訳(別工程で確定済み)" not in xp.prompts[0] and res["ref_ja"] is None                          # M-1: pool一致なしなら参考訳を渡さない
    assert set(res["sections"]) == {"日本語訳", "文法・構文の仕組み", "通常の表現・語順との比較", "意味・ニュアンス・表現効果"}
    assert res["audit"]["extract"]["model"] == MODEL and res["audit"]["explain"]["process"] == m.PROCESS_EXPLAIN
    assert res["audit"]["explain"]["prompt_template_sha256"] == m.STEPB_PROMPT_SHA256
    assert res["audit"]["extract"]["prompt_template_sha256"] == m.STEPA_PROMPT_SHA256
    _fresh(r, "x")


def test_D2_resume_reuses_everything_api_zero(routed):
    r1, *_ = _run(routed)
    r2, ex, xp, tr = _run(routed, cached_candidates=r1["candidates"], cached_result=r1["result"])
    assert (ex.n, tr.n, xp.n) == (0, 0, 0) and r2["result"]["reused_from_previous_run"] is True and r2["candidates"]["reused_from_previous_run"] is True
    assert r2["result"]["explanation_md"] == r1["result"]["explanation_md"]


def test_D3_body_change_regenerates_but_label_same(routed):
    r1, *_ = _run(routed)
    paras2 = PARAS[:3] + ["Nothing else happened on that day."]
    ex, xp, tr = LLM(_stepa_json(F_INV, F_CLEFT, F_SPEC)), LLM(STEPB_OK), LLM(TR_OK)
    r2 = m.run_part2(paras2, "Test Story", mode=AUTO, cached_candidates=r1["candidates"], cached_result=r1["result"],
                     extract_call_fn=ex, explain_call_fn=xp, level="b1b")
    assert ex.n == 1                                                                                    # 本文shaが違えば再抽出
    with pytest.raises(m.Part2Stale):
        m.require_fresh_part2(r1["result"], paras2, "Test Story", next_command="cmd", candidates_doc=r1["candidates"], grammar_review=r1["review_record"])


def test_D4_human_choice_changes_selection_and_regenerates_explanation_only(routed):
    r1, *_ = _run(routed)
    d = r1["candidates"]
    ex, xp, tr = LLM("unused"), LLM(STEPB_OK), LLM(TR_OK)
    r2 = m.run_part2(PARAS, "Test Story", mode="wait", review={"choice": "top2", "candidates_sha256": d["candidates_sha256"], "reason": "r"},
                     cached_candidates=d, cached_result=r1["result"], extract_call_fn=ex, explain_call_fn=xp, level="b1b")
    assert ex.n == 0 and tr.n == 0 and xp.n == 1                                                         # 候補は再利用・TOP2の解説のみ新規
    assert r2["result"]["selection"]["rank"] == 2 and r2["result"]["selection"]["source"] == "human_top2"


def test_D5_pending_review_makes_no_paid_downstream_call(routed):
    r, ex, xp, tr = _run(routed, mode="wait")
    assert r["status"] == "PENDING_REVIEW" and r["result"] is None and r["review_request"]["kind"] == "grammar"
    assert (ex.n, tr.n, xp.n) == (1, 0, 0)
    assert r["selection"]["review_status"] is None and r["review_record"] is None


def test_D6_zero_candidates_no_downstream_calls(routed):
    r, ex, xp, tr = _run(routed, ex=LLM(_stepa_json(_feat("P1", PARAS[0], "INV", tv="LOW"))))
    assert r["status"] == "ZERO" and r["result"]["status"] == "ZERO" and r["result"]["zero_reason"] == "no_candidate" and (tr.n, xp.n) == (0, 0)
    assert m.render_markdown(r["result"]) == "" and m.render_html_block(r["result"]) == ""                  # 0件=コーナー全体を出さない(固定文面なし)
    _fresh(r)
    assert r["review_record"]["status"] == "NO_CANDIDATE_UNREVIEWED"                                       # M-6: REVIEWEDではない


def test_D7_ref_ja_pool_match_passes_reference_to_stepB_only(routed):
    pool = {PARAS[1]: "計画が変わったのは三月だ。"}
    r, ex, xp, tr = _run(routed, ref_ja_pool=pool)
    assert tr.n == 0 and r["result"]["ref_ja_source"] == "part1_pool" and "参考訳(別工程で確定済み): 計画が変わったのは三月だ。" in xp.prompts[0]
    assert r["result"]["translation_ja"] == r["result"]["sections"]["日本語訳"] != "計画が変わったのは三月だ。"       # 画面の訳はStep B自身の訳(Trial-07)


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
    assert [s for s, _ in seen] == ["part2_extract", "part2_explain"]


def test_D13_budget_guard_can_stop_before_api(routed):
    def stop(stage, est):
        raise RuntimeError("budget stop")
    ex = LLM(_stepa_json(F_CLEFT))
    with pytest.raises(RuntimeError):
        _run(routed, ex=ex, budget_guard=stop)
    assert ex.n == 0


def test_D14_no_t1_translation_function_remains():
    """M-1: T1訳(Part 2で常時生成)は廃止。translate_sentence / translate_call_fn は存在しない。"""
    assert not hasattr(m, "translate_sentence") and "translate_call_fn" not in inspect.signature(m.run_part2).parameters


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
        m.require_fresh_part2(res, PARAS, "Test Story", next_command="cmd", candidates_doc=r["candidates"], grammar_review=r["review_record"])
    res2 = copy.deepcopy(r["result"])
    res2["explanation_md"] = ""
    with pytest.raises(m.Part2Stale, match="cmd"):
        m.require_fresh_part2(res2, PARAS, "Test Story", next_command="cmd", candidates_doc=r["candidates"], grammar_review=r["review_record"])
    with pytest.raises(m.Part2Stale):
        m.require_fresh_part2(None, PARAS, "Test Story", next_command="cmd", candidates_doc=r["candidates"], grammar_review=r["review_record"])


def test_E4_render_markdown_and_html_conventions(routed):
    r, *_ = _run(routed)
    md = m.render_markdown(r["result"])
    assert md.startswith("# Grammar & Sentence Structure") and "Part 2" not in md and PARAS[1] in md and "**日本語訳**" in md
    assert r["result"]["translation_ja"] in md                                                                   # 画面の訳=Step B自身の訳(M-1)
    h = m.render_html_block(r["result"])
    assert "<section class='study'>" in h and "<h3>Grammar &amp; Sentence Structure</h3>" in h and "<table" not in h and "<h2" not in h
    assert "<b>It was</b>" in h and PARAS[1] in h and "<style>" in h
    assert "<style>" not in m.render_html_block(r["result"], include_css=False)                             # Part 1直後に連結する場合
    assert not m.PAGE_FORBIDDEN_RE.search(h)
    z0 = m.zero_result(r["candidates"], "no_candidate")
    assert m.render_html_block(z0) == "" and m.render_markdown(z0) == "" and m.expected_grammar_blocks(z0) == 0 and m.expected_grammar_blocks(r["result"]) == 1


def test_E5_write_and_load_artifacts(routed, tmp_path):
    r, *_ = _run(routed)
    out = m.write_artifacts(str(tmp_path / "study_text"), r["candidates"], r["result"])
    assert os.path.basename(out["candidates"]) == "grammar_candidates.json" and os.path.basename(out["result"]) == "part2_result.json"
    again = m.run_part2(PARAS, "Test Story", mode=AUTO, cached_candidates=m.load_json(out["candidates"]), cached_result=m.load_json(out["result"]),
                        extract_call_fn=LLM("x"), explain_call_fn=LLM("x"), level="b1b")
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
            m.run_part2(bad, "L", extract_call_fn=ex, level="b1b")
    with pytest.raises(m.Part2InputError):
        m.stepa_prompt(PARAS, "multi\nline")
    assert ex.n == 0


# ============================================================
# P: Production境界
# ============================================================
def test_P1_routing_is_registered_and_model_mismatch_is_fail_closed():
    """委任_03(W1): er006へ2 processを登録済み(SUPPORT_MODEL)。登録後も、応答モデルが違えばfallbackせずSTOP(API前の契約検証+応答後の不一致検証)。"""
    assert routing.PROCESS_MODEL_MAP[m.PROCESS_EXTRACT] == routing.SUPPORT_MODEL
    assert routing.PROCESS_MODEL_MAP[m.PROCESS_EXPLAIN] == routing.SUPPORT_MODEL
    assert m.REQUIRED_ROUTING_ENTRIES == {m.PROCESS_EXTRACT: "SUPPORT_MODEL", m.PROCESS_EXPLAIN: "SUPPORT_MODEL"}

    def wrong_model(prompt):
        return _stepa_json(F_CLEFT), "some-other-model", {"input_tokens": 1, "output_tokens": 1, "cached_input_tokens": 0}, "r1"
    with pytest.raises(m.Part2Error):
        m.extract_candidates(PARAS, "x", call_fn=wrong_model, level="b1b")


def test_P2_module_does_not_reference_trial_assets():
    src = open(os.path.join(HERE, "er120_part2_grammar_production_01.py"), encoding="utf-8").read()
    body = "\n".join(l for l in src.split("\n") if not l.lstrip().startswith("#"))
    assert not re.search(r"^\s*(import|from)\s+(run_trial_|analyze_)", body, re.M)
    assert "FAMILY-Z-STUDY-TEXT-TRIAL-01" not in body and "docs/research" not in body and "docs\\research" not in body
    assert not re.search(r"os\.environ", body)                                                           # 環境変数でON/OFFを変えない


def test_P3_only_wiring_and_review_modules_import_the_module():
    """委任_03: 配線済み。このmoduleをimportしてよいのは文法review核(er119_grammar_review_01)・KP/文法共通核(er119_kp_human_review_01/_cli)・
    配線module(er120_part2_wiring_01/_mock_01)だけ。X/Z runnerはwiring module経由(直接importしない)。"""
    me = os.path.basename(__file__)
    allowed = {"er119_grammar_review_01.py", "er119_kp_human_review_01.py", "er119_kp_human_review_cli_01.py",
               "er120_part2_wiring_01.py", "er120_part2_mock_01.py",
               "er128_kp_confirmed_content_01.py"}   # KCP(確定内容保護)M6がfreeze_from_sidecarでPart 2の構造検査(split_sections)を遅延importする。GRAMMAR-PREGEN-ALL-LEVELS-01 委任_02で許可リストへ追加(KCP 02B導入時から失敗していた既存の取りこぼし)
    offenders = []
    for f in glob.glob(os.path.join(HERE, "*.py")):
        b = os.path.basename(f)
        if b in (me, "er120_part2_grammar_production_01.py") or "test" in b:
            continue
        if "er120_part2_grammar_production_01" in open(f, encoding="utf-8", errors="ignore").read() and b not in allowed:
            offenders.append(b)
    assert offenders == [], offenders


def test_P4_public_api_signatures():
    assert list(inspect.signature(m.stepa_prompt).parameters) == ["paragraphs", "label"]
    assert list(inspect.signature(m.select_from_candidates).parameters) == ["doc", "review", "mode"]
    assert inspect.signature(m.run_part2).parameters["mode"].default == "wait"                           # 既定は待機(自動確定は明示宣言のみ)
    assert inspect.signature(m.run_part2).parameters["review"].default is None


def test_P5_defaults_are_the_approved_values():
    assert m.MODEL == routing.SUPPORT_MODEL == "gpt-6-luna" and m.TOP_N == 2
    assert m.LEVELS == {"b1b": "Advanced", "a2": "Standard"}      # 全level化(GRAMMAR-PREGEN-ALL-LEVELS-01): Advanced固定のLEVELではなく、levelは必須引数(LEVELS)


@needs_trial
def test_A5_structure_check_accepts_all_real_trial07_stepB_outputs():
    """構造検査(必須3見出し・順序・日本語含有・ページ非表示語)が、Trial-07の実Step B出力(有料7件)を1件も誤って落とさない。"""
    fs = sorted(glob.glob(os.path.join(TRIAL, "_raw_07_07_r1_stepB_*.txt")))
    assert len(fs) == 7
    for f in fs:
        r = m._parse_stepb_checked(open(f, encoding="utf-8").read())
        assert set(r["sections"]) >= set(m.EXPLANATION_REQUIRED), f


# ============================================================
# M: 委任_02 Opus条件Aレビュー反映(M-1〜M-7・R-1/R-3/R-4/R-7)。全てmock・API 0。
# ============================================================
PARAS2 = ["Under the bed lay a small box. Nothing else happened that day.", "It was in March that the plan changed."]
F2_INV = _feat("P1", "Under the bed lay a small box.", "INV")
F2_SPEC = _feat("P1", "Nothing else happened that day.", "SPEC", mq="Nothing")
F2_WHOLE = _feat("P1", PARAS2[0], "CLEFT", mq="Under")
F2_CLEFT = _feat("P2", PARAS2[1], "CLEFT")


def _doc2(*feats, ng=(), paras=PARAS2):
    parsed = m.parse_candidates(_stepa_json(*feats), paras)
    return m.build_candidates_doc(parsed, paras, "Test Story", ng=ng, level="b1b")


def _decision(doc, ch, reason="理由あり", **kw):
    return dict({"choice": ch, "candidates_sha256": doc["candidates_sha256"], "reason": reason, "by": "tester"}, **kw)


def _human(r_or_doc, ch, *, paras=PARAS, xp=None, **kw):
    """Human確定を適用してrun_part2(候補は再利用=Step A'' 0 call)。"""
    d = r_or_doc["candidates"] if "review_record" in r_or_doc else r_or_doc
    return m.run_part2(paras, "Test Story", review=_decision(d, ch, **kw), cached_candidates=d, extract_call_fn=LLM("must-not-be-called"),
                       explain_call_fn=xp or LLM(STEPB_OK), level="b1b")


# ---- M-1: 訳の出所はTrial-07どおり ----
def test_M1_screen_translation_is_stepB_own_and_ref_ja_only_when_pool_matches(routed):
    r, ex, xp, tr = _run(routed)
    assert tr.n == 0 and "参考訳(別工程で確定済み)" not in xp.prompts[0]                                                    # pool無し=参考訳なし・T1 callなし
    assert r["result"]["translation_ja"] == "三月に計画が変わったのだ。" and r["result"]["ref_ja"] is None
    assert "三月に計画が変わったのだ。" in m.render_html_block(r["result"]) and "三月に計画が変わったのだ。" in m.render_markdown(r["result"])
    r2, ex2, xp2, tr2 = _run(routed, ref_ja_pool={PARAS[0]: "別の文の訳"})                                  # 一致しない英文の訳は渡さない
    assert tr2.n == 0 and "参考訳(別工程で確定済み)" not in xp2.prompts[0] and r2["result"]["ref_ja"] is None
    r3, ex3, xp3, tr3 = _run(routed, ref_ja_pool={"It was in March that the plan changed.": "計画の変更は三月だった。"})
    assert tr3.n == 0 and "参考訳(別工程で確定済み): 計画の変更は三月だった。" in xp3.prompts[0] and r3["result"]["ref_ja_source"] == "part1_pool"
    assert r3["result"]["translation_ja"] == "三月に計画が変わったのだ。"                                   # 表示は常にStep B自身の訳


def test_M1_lookup_ref_ja_is_trial07_exact_match_after_quote_normalisation():
    assert m.lookup_ref_ja("She said “hi”.", {'She said "hi".': "訳"}) == "訳"                             # run_trial_07: _qn(a)==_qn(b)
    assert m.lookup_ref_ja("She said hi.", {'She said "hi".': "訳"}) is None
    assert m.lookup_ref_ja("x", None) is None and m.lookup_ref_ja("x", {}) is None


@needs_trial
def test_M1_matches_trial07_ref_ja_rule_source():
    src = open(os.path.join(TRIAL, "run_trial_07.py"), encoding="utf-8").read()
    assert 't4._qn(it["sentence"]) == t4._qn(verb): f["ref_ja"] = it["sentence_ja"]' in src                   # 規則の出所(:163)


def test_M1_R7_pool_change_invalidates_cached_result_and_fresh_check(routed):
    pool_a = {PARAS[1]: "訳A"}
    r1, *_ = _run(routed, ref_ja_pool=pool_a)
    r_same, ex, xp, tr = _run(routed, ref_ja_pool=pool_a, cached_candidates=r1["candidates"], cached_result=r1["result"])
    assert (ex.n, xp.n) == (0, 0) and r_same["result"]["reused_from_previous_run"] is True                  # 同じpool=API 0
    r_diff, ex, xp, tr = _run(routed, ref_ja_pool={PARAS[1]: "訳B"}, cached_candidates=r1["candidates"], cached_result=r1["result"])
    assert xp.n == 1 and r_diff["result"]["reused_from_previous_run"] is False                              # poolが変われば解説を再生成
    assert r_diff["result"]["explain_signature"] != r1["result"]["explain_signature"]
    _fresh(r1, ref_ja_pool=pool_a)
    with pytest.raises(m.Part2Stale, match="Part 1訳pool"):
        _fresh(r1, ref_ja_pool={PARAS[1]: "訳B"})
    with pytest.raises(m.Part2Stale, match="Part 1訳pool"):
        _fresh(r1, ref_ja_pool={})                                                                         # pool一致が消えた場合も検出


# ---- M-2: Human確定・候補docと結びつく ----
def test_M2_post_review_top2_rejects_old_auto_result_at_every_entrance(routed):
    r1, *_ = _run(routed)                                                                                  # auto_top1
    assert r1["review_record"]["status"] == "UNREVIEWED_AUTO_ADOPTED"
    _fresh(r1)
    r2 = m.run_part2(PARAS, "Test Story", review=_decision(r1["candidates"], "top2"), cached_candidates=r1["candidates"], extract_call_fn=LLM("x"),
                     explain_call_fn=LLM(STEPB_OK), prior_history=r1["review_record"]["history"], level="b1b")
    assert r2["review_record"]["status"] == "REVIEWED" and r2["result"]["selection"]["source"] == "human_top2"
    _fresh(r2)
    for where in ("tts", "assemble", "load_level_inputs", "stage_pages", "stage_page_verify", "player"):
        with pytest.raises(m.Part2Stale, match="cmd"):
            m.require_fresh_part2(r1["result"], PARAS, "Test Story", next_command="cmd", where=where, candidates_doc=r2["candidates"],
                                  grammar_review=r2["review_record"])                                        # 古いauto_top1結果 + 新しい確定
    with pytest.raises(m.Part2Stale):
        m.require_fresh_part2(r2["result"], PARAS, "Test Story", next_command="cmd", candidates_doc=r1["candidates"], grammar_review=r1["review_record"])
    assert len(r2["review_record"]["history"]) > len(r1["review_record"]["history"])


def test_M2_omit_and_zero_are_bound_to_the_confirmation(routed):
    r1, *_ = _run(routed)
    z = _human(r1, "omit")
    assert z["status"] == "ZERO" and z["result"]["zero_reason"] == "human_omit"
    _fresh(z)
    with pytest.raises(m.Part2Stale):                                                                      # omit確定後に旧SELECTED結果は不可
        m.require_fresh_part2(r1["result"], PARAS, "Test Story", next_command="c", candidates_doc=z["candidates"], grammar_review=z["review_record"])
    with pytest.raises(m.Part2Stale):                                                                      # omit確定に対しZERO(no_candidate)は不可
        m.require_fresh_part2(m.zero_result(z["candidates"], "no_candidate"), PARAS, "Test Story", next_command="c",
                              candidates_doc=z["candidates"], grammar_review=z["review_record"])
    zero0, ex, xp, tr = _run(routed, ex=LLM(_stepa_json(_feat("P1", PARAS[0], "INV", tv="LOW"))))
    _fresh(zero0)
    with pytest.raises(m.Part2Stale):                                                                      # 0件確定にhuman_omit結果は不可
        m.require_fresh_part2(m.zero_result(zero0["candidates"], "human_omit"), PARAS, "Test Story", next_command="c",
                              candidates_doc=zero0["candidates"], grammar_review=zero0["review_record"])


def test_M2_tampered_review_or_candidates_or_signature_rejected(routed):
    r, *_ = _run(routed)
    rv = copy.deepcopy(r["review_record"])
    rv["status"] = "REVIEWED"                                                                              # AUTOをREVIEWEDへ偽装(署名不一致)
    with pytest.raises(m.Part2Stale, match="signature"):
        m.require_fresh_part2(r["result"], PARAS, "Test Story", next_command="c", candidates_doc=r["candidates"], grammar_review=rv)
    rv = copy.deepcopy(r["review_record"])
    rv["mode_declaration"] = None                                                                          # auto宣言が無いAUTO採用
    rv["selection_signature"] = m.grammar_selection_signature(rv)
    with pytest.raises(m.Part2Stale, match="auto宣言"):
        m.require_fresh_part2(r["result"], PARAS, "Test Story", next_command="c", candidates_doc=r["candidates"], grammar_review=rv)
    for st in ("PENDING_REVIEW", "RESELECTION_REQUESTED", "STALE"):
        rv = copy.deepcopy(r["review_record"])
        rv["status"] = st
        rv["selection_signature"] = m.grammar_selection_signature(rv)
        with pytest.raises(m.Part2Stale, match="前進不可"):
            m.require_fresh_part2(r["result"], PARAS, "Test Story", next_command="c", candidates_doc=r["candidates"], grammar_review=rv)
    doc = copy.deepcopy(r["candidates"])
    doc["candidates"][0]["construct_ja"] = "改変"                                                           # 候補docの材料欄改変(sha不一致)
    with pytest.raises(m.Part2Stale):
        m.require_fresh_part2(r["result"], PARAS, "Test Story", next_command="c", candidates_doc=doc, grammar_review=r["review_record"])
    res = copy.deepcopy(r["result"])
    res["explain_signature"] = "0" * 64                                                                    # (iv) 材料欄から再計算した署名と不一致
    with pytest.raises(m.Part2Stale, match="signature"):
        m.require_fresh_part2(res, PARAS, "Test Story", next_command="c", candidates_doc=r["candidates"], grammar_review=r["review_record"])
    res = copy.deepcopy(r["result"])
    res["translation_ja"] = "すり替えた訳"                                                                   # 画面の訳はStep Bの【日本語訳】と一致必須
    with pytest.raises(m.Part2Stale, match="訳"):
        m.require_fresh_part2(res, PARAS, "Test Story", next_command="c", candidates_doc=r["candidates"], grammar_review=r["review_record"])
    with pytest.raises(m.Part2Stale):
        m.require_fresh_part2(r["result"], PARAS, "Test Story", next_command="c", candidates_doc=None, grammar_review=r["review_record"])
    with pytest.raises(m.Part2Stale):
        m.require_fresh_part2(r["result"], PARAS, "Test Story", next_command="c", candidates_doc=r["candidates"], grammar_review=None)
    with pytest.raises(TypeError):                                                                         # 引数省略は不可(fail-closed)
        m.require_fresh_part2(r["result"], PARAS, "Test Story", next_command="c")


# ---- M-3: autoは明示宣言dictのみ ----
def test_M3_auto_only_via_er119_declaration_dict():
    for bad in ("auto", "AUTO", True, {"mode": "auto"}, dict(AUTO, source="runner_arg"), dict(AUTO, reason=""), dict(AUTO, declared_by=None)):
        with pytest.raises(m.Part2ReviewError):
            m.normalize_mode(bad)
    assert m.normalize_mode(AUTO)[0] == "auto" and m.normalize_mode("wait") == ("wait", None) and m.normalize_mode(None) == ("wait", None)
    for name, fn in inspect.getmembers(m, inspect.isfunction):
        for p in inspect.signature(fn).parameters.values():
            assert p.default != "auto" and not (p.name == "mode" and isinstance(p.default, dict)), (name, p.name)
    src = open(os.path.join(HERE, "er120_part2_grammar_production_01.py"), encoding="utf-8").read()
    assert "os.environ" not in "\n".join(l for l in src.split("\n") if not l.lstrip().startswith("#"))


# ---- M-4: stage来歴・再finalize・PENDING ----
def test_M4_stage_input_shas_and_refinalize_without_extraction(routed, tmp_path):
    r1, *_ = _run(routed)
    c0 = m.cand_stage_input_sha(PARAS, "Test Story")
    assert c0 == m.cand_stage_input_sha(PARAS, "Test Story") and c0 != m.cand_stage_input_sha(PARAS, "Other") and c0 != m.cand_stage_input_sha(PARAS2, "Test Story")
    f0 = m.final_stage_input_sha(PARAS, "Test Story", r1["review_record"])
    xp = LLM(STEPB_OK)
    r2 = m.finalize_part2(PARAS, "Test Story", candidates_doc=r1["candidates"], review=_decision(r1["candidates"], "top2"), explain_call_fn=xp, level="b1b")
    assert xp.n == 1 and f0 != m.final_stage_input_sha(PARAS, "Test Story", r2["review_record"])             # 確定が変わるとinput_shaが変わる
    with pytest.raises(m.Part2Stale):                                                                      # 保存済み候補が無い/古い=再抽出せずStale(API 0)
        m.finalize_part2(PARAS, "Test Story", candidates_doc=None, mode=AUTO, level="b1b")
    with pytest.raises(m.Part2Stale):
        m.finalize_part2(PARAS2, "Test Story", candidates_doc=r1["candidates"], mode=AUTO, level="b1b")
    xp2 = LLM(STEPB_OK)                                                                                    # PENDING: 専用例外で抜け、出力ファイルを作らない。失敗(Part2Error)ではない
    with pytest.raises(m.Part2PendingReview) as ei:
        m.finalize_part2(PARAS, "Test Story", candidates_doc=r1["candidates"], mode="wait", explain_call_fn=xp2, level="b1b")
    assert ei.value.status == "PENDING_REVIEW" and ei.value.review_request["kind"] == "grammar" and xp2.n == 0
    assert not issubclass(m.Part2PendingReview, m.Part2Error) and list(tmp_path.iterdir()) == []


# ---- M-5: NG ----
def test_M5_ng_three_way_matching():
    d = _doc2(F2_INV, F2_CLEFT)
    c = next(x for x in d["candidates"] if x["feature_class"] == "INV")
    assert m.ng_match_methods(c, {"candidate_id": c["candidate_id"], "para": "P9", "sentence": "x", "span": None}) == ["candidate_id"]
    assert m.ng_match_methods(c, {"candidate_id": "gZZZ", "para": "P7", "sentence": "under  the bed lay a SMALL box.", "span": None}) == ["sentence"]   # 段落番号が違っても正規化した文が一致
    a, b = c["span"]
    assert m.ng_match_methods(c, {"candidate_id": "g0", "para": c["para"], "sentence": "other", "span": [a + 3, b + 40]}) == ["range"]      # 重なり
    assert m.ng_match_methods(c, {"candidate_id": "g0", "para": c["para"], "sentence": "other", "span": [a - 5, b + 5]}) == ["range"]       # 包含
    assert m.ng_match_methods(c, {"candidate_id": "g0", "para": c["para"], "sentence": "other", "span": [b, b + 9]}) == []                # 隣接は重ならない
    assert m.ng_match_methods(c, {"candidate_id": "g0", "para": "P2", "sentence": "other", "span": [a, b]}) == []                         # 別段落の範囲は無関係


def test_M5_ng_persists_across_runs_even_with_different_quote_range():
    d1 = _doc2(F2_INV, F2_CLEFT)
    inv = next(c for c in d1["candidates"] if c["feature_class"] == "INV")
    ng = [m.ng_entry_from_candidate(inv, reason="却下", by="h")]
    d2 = _doc2(F2_WHOLE, F2_CLEFT, ng=ng)                                                                  # 別run: LLMが段落全体で同じ箇所を引用 -> 範囲の重なりでNG
    assert [c["feature_class"] for c in d2["candidates"]] == ["CLEFT"] and d2["candidates"][0]["para"] == "P2"
    assert d2["filtered_by_ng"] and d2["filtered_by_ng"][0]["methods"] == ["range"]
    d3 = _doc2(F2_INV, ng=[dict(ng[0], para="P5", candidate_id="gOLD", span=None)])                        # 同じ文を別段落番号で出しても文一致でNG
    assert d3["candidates"] == [] and d3["exhausted"] is True and d3["filtered_by_ng"][0]["methods"] == ["sentence"]
    d4 = m.apply_ng(d1, ng)                                                                                # 保存済み候補へ後からregistryを適用
    assert all(c["feature_class"] != "INV" for c in d4["candidates"]) and d4["candidates_sha256"] != d1["candidates_sha256"]
    assert m.apply_ng(d1, []) is d1


def test_M5_exhaustion_never_auto_zero_and_human_rejected_all():
    d = m.reselect_candidates(_doc2(F2_CLEFT), None, reason="どれも不適切", by="h")
    assert d["exhausted"] is True and d["candidates"] == [] and d["status"] == "NO_CANDIDATE"
    for mode in ("wait", AUTO):                                                                            # autoでもHuman却下を『適格なし』にしない
        s = m.select_from_candidates(d, None, mode)
        assert s["status"] == "RESELECT_EXHAUSTED" and s["review_status"] is None
    rq = m.review_request(d)
    assert rq["exhausted"] is True and rq["choices"] == ["omit", "reextract"] and rq["auto_default"] is None
    r = m.run_part2(PARAS2, "Test Story", mode=AUTO, cached_candidates=d, extract_call_fn=LLM("x"), level="b1b")
    assert r["status"] == "RESELECT_EXHAUSTED" and r["result"] is None and r["review_record"] is None
    z = _human(d, "omit", paras=PARAS2, reason="全候補を却下済みのため省略")
    assert z["status"] == "ZERO" and z["result"]["zero_reason"] == "human_rejected_all" and z["review_record"]["status"] == "REVIEWED"
    assert z["review_record"]["selection"]["zero_reason"] == "human_rejected_all"
    m.require_fresh_part2(z["result"], PARAS2, "Test Story", next_command="c", candidates_doc=z["candidates"], grammar_review=z["review_record"])
    with pytest.raises(m.Part2ReviewError):
        m.select_from_candidates(d, _decision(d, "top1"), "wait")                                          # 枯渇時の選択肢はomit/reextractのみ
    assert m.select_from_candidates(_doc2(), None, "wait")["source"] == "no_candidate"                     # 本当に0件(NGなし)は従来どおりno_candidate


def test_M5_reextract_once_then_limit_stop(routed):
    d = m.reselect_candidates(_doc2(F2_CLEFT), None, reason="r1")
    ex = LLM(_stepa_json(F2_CLEFT))
    d2 = m.reextract_candidates(d, PARAS2, "Test Story", reason="再抽出", by="h", call_fn=ex)
    assert ex.n == 1 and d2["exhausted"] is True and d2["reselect_count"] == 2 and d2["reextract_count"] == 1                     # 同じ候補はNGで戻らない
    assert d2["round"] == d["round"] + 1 and [e["event"] for e in d2["reselect_log"]] == ["reselect", "reextract"]
    assert m.review_request(d2)["choices"] == ["omit"]                                                     # 上限到達: 再抽出も再選定も提示しない
    ex2 = LLM(_stepa_json(F2_CLEFT))
    with pytest.raises(m.Part2ReselectLimit):
        m.reextract_candidates(d2, PARAS2, "Test Story", reason="もう一度", call_fn=ex2)
    with pytest.raises(m.Part2ReselectLimit):
        m.select_from_candidates(d2, _decision(d2, "reextract"), "wait")
    assert ex2.n == 0
    with pytest.raises(m.Part2ReviewError):
        m.reextract_candidates(_doc2(F2_CLEFT), PARAS2, "Test Story", reason="r", call_fn=LLM("x"))        # 枯渇していなければ不可
    assert issubclass(m.Part2ReselectLimit, m.Part2Error)                                                  # STOP(Part2Error系)


def test_M5_reselect_limit_is_two_and_choice_hidden_afterwards():
    d = _doc(F_INV, F_CLEFT, F_SPEC, _feat("P4", PARAS[3], "HEAVY", mq="Nothing"))
    assert m.review_request(d)["choices"] == ["top1", "top2", "reselect", "omit"]
    e1 = m.reselect_candidates(d, None, reason="r1")
    e2 = m.reselect_candidates(e1, None, reason="r2")
    assert e2["reselect_count"] == 2 and "reselect" not in m.review_request(e2)["choices"]
    with pytest.raises(m.Part2ReselectLimit):
        m.reselect_candidates(e2, None, reason="r3")
    big = _doc(F_INV, F_CLEFT, F_SPEC)
    capped = dict(big, reselect_count=2)                                                                   # 候補が残っていても上限後にreselectを選ぶとSTOP
    with pytest.raises(m.Part2ReselectLimit):
        m.select_from_candidates(capped, _decision(capped, "reselect"), "wait")


def test_M5_ng_vs_not_selected_distinction(routed):
    r1, *_ = _run(routed)
    d = r1["candidates"]
    ids = [c["candidate_id"] for c in d["candidates"][:2]]
    r2 = _human(r1, "top2")
    v = r2["review_record"]["verdicts"]
    assert v == {ids[0]: "NOT_SELECTED", ids[1]: "SELECTED"} and r2["review_record"]["ng"] == []           # top2を選んだときのTOP1はNGではない
    assert [c["candidate_id"] for c in r2["candidates"]["candidates"]] == [c["candidate_id"] for c in d["candidates"]]   # NOT_SELECTEDは再選定時も除外されない
    dd = m.reselect_candidates(d, None, reason="どちらも違う", by="h")                                       # reselectで外したTOP1/TOP2はNG
    assert {e["candidate_id"] for e in dd["ng"]} == set(ids) and all(e["reason"] == "どちらも違う" for e in dd["ng"])
    r3 = _human(dd, "top1")
    v3 = r3["review_record"]["verdicts"]
    assert v3[ids[0]] == "NG" and v3[ids[1]] == "NG" and r3["review_record"]["reselect_count"] == 1
    assert m.verdicts_for_choice(d, "omit") == {ids[0]: "NOT_SELECTED", ids[1]: "NOT_SELECTED"}


# ---- M-6 ----
def test_M6_reason_required_and_history_records_rejected_details(routed):
    d = _doc(F_INV, F_CLEFT, F_SPEC)
    for ch in ("top2", "reselect", "omit"):
        for bad in (None, "", "   "):
            with pytest.raises(m.Part2ReviewError, match="reason"):
                m.select_from_candidates(d, {"choice": ch, "candidates_sha256": d["candidates_sha256"], "reason": bad}, "wait")
    assert m.select_from_candidates(d, {"choice": "top1", "candidates_sha256": d["candidates_sha256"]}, "wait")["source"] == "human_top1"   # top1は理由任意
    with pytest.raises(m.Part2ReviewError):
        m.reselect_candidates(d, None, reason=" ")
    d2 = m.reselect_candidates(d, None, reason="TOP1/2が不適切", by="alice")
    ev = d2["reselect_log"][0]
    assert ev["reason"] == "TOP1/2が不適切" and ev["by"] == "alice" and len(ev["rejected"]) == 2
    rj = ev["rejected"][0]
    assert {"sentence", "feature_class", "tier", "tier_table_row", "candidate_id"} <= set(rj) and rj["tier_table_row"]["eligible"] is True
    rec = _human(d2, "top1")["review_record"]
    assert [h["event"] for h in rec["history"]] == ["reselect", "finalize"]
    assert rec["history"][0]["detail"]["rejected"][0]["sentence"] == rj["sentence"] and rec["history"][0]["detail"]["reason"] == "TOP1/2が不適切"


def test_M6_zero_is_never_reviewed_and_auto_never_counted_as_reviewed(routed):
    z, *_ = _run(routed, ex=LLM(_stepa_json(_feat("P1", PARAS[0], "INV", tv="LOW"))))
    assert z["review_record"]["status"] == "NO_CANDIDATE_UNREVIEWED" and z["review_record"]["status"] != "REVIEWED"
    a, *_ = _run(routed)
    d = a["candidates"]
    hr = _human(a, "top1")
    acc = _human(a, "top1", accept_ai=True)
    assert acc["review_record"]["status"] == "REVIEWED" and acc["review_record"]["accept_ai_default"] is True                  # accept-ai=人が見て了承(AUTOとは区別)
    assert acc["review_record"]["accepted_candidates_sha256"] == d["candidates_sha256"]
    assert hr["review_record"]["accept_ai_default"] is False and a["review_record"]["accept_ai_default"] is False
    s = m.summarize_review_statuses([a["review_record"], z["review_record"], hr["review_record"], acc["review_record"], None])
    assert s == {"reviewed": 2, "unreviewed_auto_adopted": 1, "no_candidate_unreviewed": 1, "other": 1, "total": 5, "human_reviewed": 2}
    with pytest.raises(m.Part2ReviewError):
        m.select_from_candidates(d, _decision(d, "top2", accept_ai=True), "wait")                          # accept_aiはtop1のみ
    assert a["selection"]["review_status"] == "UNREVIEWED_AUTO_ADOPTED" and a["review_record"]["verdicts"][d["top_ids"][0]] is None   # AUTO=未レビュー(null)


# ---- M-7(module側): 失敗後の再開で有料callをやり直さない ----
def test_M7_resume_after_stepB_failure_does_not_reextract(routed, tmp_path):
    ex = LLM(_stepa_json(F_INV, F_CLEFT, F_SPEC))
    doc = m.resolve_candidates(PARAS, "Test Story", None, call_fn=ex, level="b1b")                                      # 抽出stage(1 call)
    with pytest.raises(m.Part2Error) as ei:
        m.finalize_part2(PARAS, "Test Story", candidates_doc=doc, mode=AUTO, explain_call_fn=LLM("garbage", fail_first=99), level="b1b")
    p = m.write_failed_record(str(tmp_path / "study_text"), ei.value, next_command="py er019_x.py --stage study_text", stage="part2")
    rec = json.load(open(p, encoding="utf-8"))
    assert rec["next_command"].endswith("--stage study_text") and rec["error_type"] == "Part2Error" and os.path.basename(p) == "part2_failed.json"
    xp = LLM(STEPB_OK)
    r = m.finalize_part2(PARAS, "Test Story", candidates_doc=doc, mode=AUTO, explain_call_fn=xp, level="b1b")           # 再開
    assert ex.n == 1 and xp.n == 1 and r["status"] == "SELECTED"                                           # Step A''は再実行されない


# ---- R-1 / R-3 / R-4 ----
def test_R1_compose_includes_css_when_part1_is_empty(routed):
    import er003_kp_general_explanation_01 as p1
    r, *_ = _run(routed)
    assert m.compose_study_html("", r["result"]).count(p1.STUDY_CSS) == 1 and m.compose_study_html(None, r["result"]).startswith(p1.STUDY_CSS)
    try:
        m.compose_study_html("", r["result"], None)                                                          # ニュアンス解説は廃止(2026-10-30): 第3引数は存在しない
        assert False, "compose_study_htmlがnuance引数を受け付けている"
    except TypeError:
        pass
    part1 = p1.STUDY_CSS + "<section class='study'><h3>Vocabulary &amp; Expressions</h3></section>"
    out = m.compose_study_html(part1, r["result"])
    assert out.startswith(part1) and out.count(p1.STUDY_CSS) == 1                                           # CSSは1回だけ・Part 1の直後
    assert out.endswith(m.render_html_block(r["result"], include_css=False))


def test_R3_verify_selection_matches_outputs(routed):
    r, *_ = _run(routed)
    md, hb = m.render_markdown(r["result"]), m.render_html_block(r["result"], include_css=False)
    kw = dict(paragraphs=PARAS, label="Test Story", candidates_doc=r["candidates"], grammar_review=r["review_record"], result=r["result"], next_command="cmd")
    m.verify_selection_matches_outputs(md_text=md, html_text="<html>" + hb + "</html>", **kw)
    with pytest.raises(m.Part2Stale, match="markdown"):
        m.verify_selection_matches_outputs(md_text=md.replace(PARAS[1], "tampered"), **kw)
    with pytest.raises(m.Part2Stale, match="HTML"):
        m.verify_selection_matches_outputs(html_text="<html>" + hb.replace("仕組み", "x") + "</html>", **kw)
    with pytest.raises(m.Part2Stale, match="HTML"):
        m.verify_selection_matches_outputs(html_text="<html></html>", **kw)
    with pytest.raises(ValueError):
        m.verify_selection_matches_outputs(kind="kp", **kw)
    r2 = _human(r, "top2", xp=LLM(STEPB_OK.replace("三月に", "三月には")))
    kw2 = dict(kw, grammar_review=r2["review_record"], candidates_doc=r2["candidates"], result=r2["result"])
    m.verify_selection_matches_outputs(md_text=m.render_markdown(r2["result"]), html_text=m.render_html_block(r2["result"], include_css=False), **kw2)
    with pytest.raises(m.Part2Stale):                                                                      # 確定がtop2になった後に旧(auto_top1)のmd/HTMLが残っていたら拒否
        m.verify_selection_matches_outputs(md_text=md, html_text="<html>" + hb + "</html>", **kw2)


def test_R4_overlapping_ranges_dropped_and_top2_hidden_when_single():
    d = _doc2(F2_INV, F2_SPEC, F2_WHOLE)                                                                   # P1全体(CLEFT)が部分文2つを包含
    assert [c["feature_class"] for c in d["candidates"]] == ["CLEFT"]
    assert m.review_request(d)["choices"] == ["top1", "reselect", "omit"]
    d2 = _doc2(F2_INV, F2_SPEC)                                                                            # 重ならない2文は両方残る
    assert [c["feature_class"] for c in d2["candidates"]] == ["SPEC", "INV"]
    with pytest.raises(m.Part2ReviewError):
        m.select_from_candidates(d, _decision(d, "top2"), "wait")


@needs_trial
def test_R4_does_not_change_top1_on_29_samples():
    """R-4(範囲重なり除外)はTOP1(select_tiered)に影響しない。候補数分布を確認(委任_01: 2件以上19/1件4/0件6)。"""
    _, t7, _ = _trial()
    dist = {"ge2": 0, "one": 0, "zero": 0}
    for gen, work, run, path in _samples():
        parsed = m.parse_candidates(open(path, encoding="utf-8").read(), t7.work_data7(work)["body"])
        sel, _t = m.select_tiered(parsed["features"])
        ranked = m.rank_eligible(parsed["features"])
        assert [(f["para"], f["sentence"]) for f, _ in ranked[:1]] == [(f["para"], f["sentence"]) for f in sel]
        dist["ge2" if len(ranked) >= 2 else ("one" if len(ranked) == 1 else "zero")] += 1
    assert sum(dist.values()) == 29 and dist["zero"] == 6
    print("candidate-count distribution after R-4:", dist)
