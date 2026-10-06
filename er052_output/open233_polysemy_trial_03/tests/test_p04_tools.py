# -*- coding: utf-8 -*-
"""TRIAL-04のAPI非呼出unit test(合成データのみ。5テーマ固有語は使わない)。Opus必須修正1〜9の分岐を検証する。"""
import json
import sys
import types
from pathlib import Path

TRIAL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TRIAL / "tools"))
import gen_notes_p03 as G
import gen_notes_p04 as P
import eval_notes_p04 as E4
import prompt_lint_p04 as L

PATS = TRIAL / "patterns"
PFX = "注意(逆転): "
NEW = ("P1p_gate_hm", "P2p_stable", "P3_writer_compress")
FORBIDDEN = L.load_forbidden(TRIAL / "eval" / "forbidden_terms.txt")


# ---------- 単一仕様lint・禁止語・hash(修正8) ----------
def test_lint_real_patterns_pass():
    for n in NEW:
        res = L.lint_pattern(PATS / n, PATS / "_common" / "stage1_prompt.txt", FORBIDDEN)
        assert res and all(not e for e in res.values()), (n, res)
        assert "cover_prompt.txt" in res and "stage2_prompt.txt" in res


def test_lint_detects_double_output_and_dup_lines():
    bad = "冒頭の説明をここに書く行です。\n【出力】JSONのみ\n{EXAMPLES}\n【出力】JSONのみ(再掲)\n冒頭の説明をここに書く行です。\n{LEDGER_FACTS}\n"
    errs = L.lint_text("stage1_prompt.txt", bad)
    assert any("【出力】が2" in e for e in errs)
    assert any("重複行" in e for e in errs)


def test_lint_detects_unused_and_unknown_placeholder():
    errs = L.lint_text("stage1_prompt.txt", "本文です。\n【出力】x\n{LEDGER_FACTS}\n{UNKNOWN_X}\n")
    assert any("EXAMPLES" in e for e in errs) and any("UNKNOWN_X" in e for e in errs)


def test_lint_forbidden_terms_detected_and_hashes():
    assert L.forbidden_hits("本文にSewerの語", ["sewer", "meta"]) == ["sewer"]
    assert L.forbidden_hits("無関係な本文", ["sewer"]) == []
    h = L.prompt_hashes(PATS / "P1p_gate_hm")
    assert set(h) >= {"stage1_prompt.txt", "stage1_5_prompt.txt", "cover_prompt.txt", "stage2_prompt.txt"} and all(len(v) == 64 for v in h.values())


def test_lint_old_defective_stage1_fails():
    old = TRIAL / "patterns" / "B2_twostage_hint" / "stage1_prompt.txt"
    if old.exists():
        assert L.lint_text("stage1_prompt.txt", old.read_text(encoding="utf-8"))  # 旧欠陥版はFAIL


def test_stage1_identical_across_patterns_and_common():
    c = (PATS / "_common" / "stage1_prompt.txt").read_text(encoding="utf-8")
    for n in NEW:
        assert (PATS / n / "stage1_prompt.txt").read_text(encoding="utf-8") == c
        meta = json.loads((PATS / n / "pattern.json").read_text(encoding="utf-8"))
        assert meta["max_chars"] == 120 and meta["self_check_policy"] == "derivable_only" and meta["hypothesis"]
        assert (PATS / n / "prefix.txt").read_text(encoding="utf-8") == "注意(逆転): "
    for f in ("stage1_5_prompt.txt", "cover_prompt.txt", "stage2_prompt.txt"):
        assert len({(PATS / n / f).read_text(encoding="utf-8") for n in NEW}) == 1  # 判定役・cover・stage2は3pattern共通


def test_stage1_prompt_has_new_fields_and_no_old_cover_field():
    c = (PATS / "_common" / "stage1_prompt.txt").read_text(encoding="utf-8")
    assert "predicate_direction_explicit" in c and "ambiguous_expression" in c and "existing_note_covers" not in c
    assert "polarity)を必ず最初に検討" in c


def test_stage1_items_hide_existing_notes_in_dry_run(tmp_path):
    a = types.SimpleNamespace(pattern="P1p_gate_hm", patterns_dir=None, ledger_txt=str(TRIAL.parents[1] / "er052_output/open233_polysemy_trial_02/ledgers/hormuz/verified_fact_ledger_control.txt"),
                              draft=None, verif=None, append_to_txt=None, max_chars=None, max_notes=None, web_search="none", budget_jpy=5.0, dry_run=True,
                              no_existing_notes=False, out_dir=str(tmp_path))
    G.run(a)
    p1 = (tmp_path / "stage1_prompt.txt").read_text(encoding="utf-8")
    assert "notes_for_writer" not in p1 and '"claim"' in p1


# ---------- R採用・R lint(修正2) ----------
ITEM = {"fact_id": "T-1", "claim": "甲が乙を取り下げた", "scope": "試験段階", "conditions": "来期まで"}


def _j(props, reversible=True, pred=True, amb=""):
    return {"fact_id": "T-1", "reversible": reversible, "compressed_claim": "甲が乙を取り下げ", "predicate_direction_explicit": pred,
            "ambiguous_expression": amb, "reverse_propositions": props}


def _r(R, comp, quote="取り下げた", ch=True):
    return {"R": R, "flipped_component": comp, "contradicts_ledger_field": "claim", "ledger_quote": quote, "changes_conclusion": ch, "conclusion_change_reason": "x"}


def test_pick_component_order_polarity_first():
    j = _j([_r("R-cause", "cause_effect"), _r("R-so", "subject_object"), _r("R-stage", "stage", "試験段階"), _r("R-pol", "polarity")])
    assert P.pick_reverse_p04(j, ITEM)["R"] == "R-pol"
    j2 = _j([_r("R-cause", "cause_effect"), _r("R-so", "subject_object"), _r("R-stage", "stage", "試験段階")])
    assert P.pick_reverse_p04(j2, ITEM)["R"] == "R-stage"
    j3 = _j([_r("R-cause", "cause_effect"), _r("R-so", "subject_object")])
    assert P.pick_reverse_p04(j3, ITEM)["R"] == "R-so"


def test_pick_filters_conclusion_and_quote():
    j = _j([_r("R-no", "polarity", ch=False), _r("R-badquote", "polarity", quote="台帳に無い語"), _r("R-ok", "interim_final", "来期まで")])
    assert P.pick_reverse_p04(j, ITEM)["R"] == "R-ok"
    assert P.pick_reverse_p04(_j([_r("R-no", "polarity", ch=False)]), ITEM) is None
    assert P.pick_reverse_p04(_j([_r("R", "polarity")], reversible=False), ITEM) is None


def test_r_lint_rejects_vague_words_and_amb_and_logs():
    log = []
    j = _j([_r("甲は乙を元に戻した", "polarity"), _r("甲は乙の方針を見直した", "stage", "試験段階"), _r("甲は乙を丙へ差し替えた", "subject_object")], amb="")
    res = P.stage1_result(j, ITEM, log, 1)
    assert res["passed"] and res["best"]["R"] == "甲は乙を丙へ差し替えた"
    assert {w for e in log for w in e["words"]} >= {"元に戻", "見直し"} and len(log) == 2
    log2 = []
    res2 = P.stage1_result(_j([_r("甲は乙を元に戻した", "polarity")]), ITEM, log2, 1)
    assert not res2["passed"] and res2["why"] == ["R_lint_rejected"]
    # 台帳claim中の曖昧表記そのものもRに使えない(ambはclaimに逐語で存在する場合のみ有効)
    log3 = []
    res3 = P.stage1_result(_j([_r("甲は乙を取り下げたのではなく廃止した", "polarity")], amb="取り下げた"), ITEM, log3, 1)
    assert not res3["passed"] and log3[0]["words"] == ["amb:取り下げた"]
    assert P._amb(_j([], amb="claimに無い表記"), ITEM) == ""


def test_vague_hits_quoted_hyoki_exempt_only_when_strip():
    n = PFX + "台帳の表記'ロールバック'は、機能のない状態の意味。"
    assert P.vague_hits(n, None, strip_quoted=True) == [] and "ロールバック" in P.vague_hits(n)
    assert P.vague_hits("設定を元に戻した", None, True) and P.vague_hits("機能のない状態へ戻した", None, True) == []
    assert P.vague_hits("調整した") and P.vague_hits("Rollback") == ["rollback"]


# ---------- フロー(スタブLLM) ----------
RS = {"T-1": "甲は乙を継続した", "T-2": "丙は丁を終了した", "T-3": "戊は己を再開した", "T-4": "庚は辛を開始した"}
QUOTES = {"T-1": "取り下げた", "T-2": "開始した", "T-3": "停止した", "T-4": "完了した"}


def _items():
    mk = lambda fid, claim, scope, notes: {"fact_id": fid, "claim": claim, "scope": scope, "conditions": None, "notes_for_writer": notes}
    return [mk("T-1", "甲が乙を取り下げた", "試験段階", "丁と書かない。"), mk("T-2", "丙が丁を開始した", "計画", None),
            mk("T-3", "戊が己を停止した", "全域", None), mk("T-4", "庚が辛を完了した", "一部", None)]


def _stage1_run(flags, pred=None, comp=None, amb=None):
    """flags: {fact_id: bool(reversible)}。pred/comp/amb: {fact_id: 値}(未指定はTrue/polarity/空)。"""
    pred, comp, amb = pred or {}, comp or {}, amb or {}
    out = []
    for fid, ok in flags.items():
        props = [{"R": RS[fid], "flipped_component": comp.get(fid, "polarity"), "contradicts_ledger_field": "claim", "ledger_quote": QUOTES[fid],
                  "changes_conclusion": True, "conclusion_change_reason": "r"}] if ok else []
        out.append({"fact_id": fid, "reversible": ok, "compressed_claim": "圧縮-" + fid, "predicate_direction_explicit": pred.get(fid, True),
                    "ambiguous_expression": amb.get(fid, ""), "reverse_propositions": props})
    return {"judgments": out}


class FakeLLM:
    def __init__(self, stage1_runs, levels, headlines=None, blocking=None, covers=None, s2=None):
        self.stage1_runs, self.levels, self.headlines = list(stage1_runs), levels, headlines or {}
        self.blocking, self.covers, self.s2 = blocking or {}, covers or {}, s2 or {}
        self.prompts = {"s1": [], "judge": [], "headline": [], "cover": [], "s2": []}

    def __call__(self, prompt, web_search="none"):
        base = {"model": "fake", "cost_jpy": 1.0}
        if "【候補】" in prompt and "{CANDIDATES}" not in prompt and "注意書き" in prompt:
            self.prompts["s2"].append(prompt)
            cands = json.loads(prompt.split("【候補】\n", 1)[1].split("\n\n【Fact一覧", 1)[0])
            notes = []
            for c in cands:
                f = c["fact_id"]
                n = {"fact_id": f, "r_echo": c["reverse_reading"], "correct_state": "正しい状態X", "note": PFX + "正しい状態Xである。" + c["reverse_reading"] + "ではない。",
                     "self_check": {"R_is_natural_reading": True, "correct_statement_derivable_from_ledger": True}}
                n.update(self.s2.get(f, {}))
                notes.append(n)
            return dict(base, parsed={"notes": notes})
        if "existing_note_covers" in prompt and "【入力】" in prompt:
            self.prompts["cover"].append(prompt)
            data = json.loads(prompt.split("【入力】\n", 1)[1])
            return dict(base, parsed={"covers": [{"fact_id": d["fact_id"], "existing_note_covers": self.covers.get(d["fact_id"], False), "reason": "r"} for d in data]})
        if "判定役" in prompt:
            self.prompts["judge"].append(prompt)
            data = json.loads(prompt.split("【入力】\n", 1)[1])
            return dict(base, parsed={"verdicts": [{"fact_id": d["fact_id"], "cid": c["cid"], "likelihood": self.levels.get(d["fact_id"], "low"),
                                                   "blocking_word": self.blocking.get(d["fact_id"], "非限定語"), "reason": "r"} for d in data for c in d["candidates"]]})
        if "見出し用に要約する記事執筆者" in prompt:
            self.prompts["headline"].append(prompt)
            data = json.loads(prompt.split("【入力】\n", 1)[1])
            return dict(base, parsed={"headlines": [{"fact_id": d["fact_id"], "headline": self.headlines.get(d["fact_id"], "見出し-" + d["fact_id"])} for d in data]})
        self.prompts["s1"].append(prompt)
        return dict(base, parsed=self.stage1_runs.pop(0))


def _run(name, llm, tmp_path):
    pat = G.load_pattern(name)
    items = _items()
    fids = [i["fact_id"] for i in items]
    a = types.SimpleNamespace(web_search="none", budget_jpy=5.0, max_notes=None)
    out = tmp_path / name
    out.mkdir(parents=True, exist_ok=True)
    prov = {}
    p1 = G.fill_prompt(pat["stage1"], [{k: v for k, v in i.items() if k != "notes_for_writer"} for i in items], 120, pat["examples"])
    notes, jall, rej = P.run_p04(pat, items, fids, p1, a, llm, out, prov, 120)
    return notes, {j["fact_id"]: j for j in jall}, prov, out, rej


def test_p1_high_medium_pass_and_single_stage1(tmp_path):
    llm = FakeLLM([_stage1_run({"T-1": True, "T-2": True, "T-3": True, "T-4": False})], levels={"T-1": "high", "T-2": "medium", "T-3": "low"})
    notes, jm, prov, out, _ = _run("P1p_gate_hm", llm, tmp_path)
    assert sorted(n["fact_id"] for n in notes) == ["T-1", "T-2"] and jm["T-3"]["dropped_by"] == ["stage1_5_low"]
    assert jm["T-2"].get("warnings") == ["stage1_5_passed_as_medium"] and len(llm.prompts["s1"]) == 1
    assert "圧縮-T-1" in llm.prompts["judge"][0] and prov["calls"] == 4  # stage1 + judge + cover(T-1/T-2のうち既存notesありT-1のみ) + stage2
    assert llm.prompts["headline"] == [] and (out / "lint_rejected.json").exists() and (out / "prompt_hashes.json").exists()


def test_bypass_judge_when_pred_false_and_polarity(tmp_path):
    llm = FakeLLM([_stage1_run({"T-1": True, "T-2": True, "T-3": True, "T-4": False}, pred={"T-1": False, "T-2": False}, comp={"T-2": "stage"})],
                  levels={"T-3": "high"})
    notes, jm, prov, _, _ = _run("P1p_gate_hm", llm, tmp_path)
    assert jm["T-1"]["route"] == "bypass" and jm["T-1"]["bypass_judge"] and jm["T-2"]["route"] == "judge"  # T-2は非polarityなので素通りしない
    assert "圧縮-T-1" not in llm.prompts["judge"][0] and "圧縮-T-2" in llm.prompts["judge"][0] and "圧縮-T-3" in llm.prompts["judge"][0]
    assert sorted(n["fact_id"] for n in notes) == ["T-1", "T-3"] and prov["bypass_count"] == 1 and jm["T-2"]["dropped_by"] == ["stage1_5_low"]
    # pred=None(未出力)はfalse扱いしない
    assert P.is_bypass({"flipped_component": "polarity", "predicate_direction_explicit": None}) is False
    assert P.is_bypass({"flipped_component": "polarity", "predicate_direction_explicit": False}) is True


def test_low_to_medium_promotion_by_limit_word(tmp_path):
    llm = FakeLLM([_stage1_run({"T-1": True, "T-2": True, "T-3": True, "T-4": False})], levels={"T-1": "low", "T-2": "low", "T-3": "low"},
                  blocking={"T-1": "当面", "T-2": "一時的", "T-3": "停止"})
    notes, jm, prov, _, _ = _run("P1p_gate_hm", llm, tmp_path)
    assert sorted(n["fact_id"] for n in notes) == ["T-1", "T-2"]  # 限定語blockingはlow->medium->P1'でhigh+medium通過
    v = jm["T-1"]["stage1_5"][0]
    assert v["likelihood"] == "medium" and v["likelihood_raw"] == "low" and v["promoted_low_to_medium"] and v["blocking_word"] == "当面"
    assert jm["T-3"]["dropped_by"] == ["stage1_5_low"] and prov["promoted_low_to_medium"] == 2
    assert P.is_limit_word("試験的") and P.is_limit_word("暫定措置") and not P.is_limit_word("停止") and not P.is_limit_word("")


def test_p2_medium_requires_stable_and_judge_always(tmp_path):
    # run1: T-1,T-2,T-3 / run2: T-1,T-3。T-1,T-3は2回通過(stable)、T-2は片回のみ。判定役は常に通す(直行なし)
    llm = FakeLLM([_stage1_run({"T-1": True, "T-2": True, "T-3": True, "T-4": False}), _stage1_run({"T-1": True, "T-2": False, "T-3": True, "T-4": False})],
                  levels={"T-1": "medium", "T-2": "medium", "T-3": "high"})
    notes, jm, prov, _, _ = _run("P2p_stable", llm, tmp_path)
    assert len(llm.prompts["judge"]) == 1
    j = llm.prompts["judge"][0].split("【入力】")[1]
    assert "T-1" in j and "T-2" in j and "T-3" in j  # 2回通過のfactも判定役へ渡る
    assert sorted(n["fact_id"] for n in notes) == ["T-1", "T-3"]  # T-1=medium+stable通過、T-3=high通過
    assert jm["T-2"]["dropped_by"] == ["stage1_5_medium_unstable"] and jm["T-1"]["stage1_stable"] and not jm["T-2"]["stage1_stable"]
    assert abs(prov["stage1_jaccard"] - (2 / 3)) < 1e-9 and prov["calls"] == 5  # stage1x2 + judge + cover + stage2
    llm2 = FakeLLM([_stage1_run({"T-1": True, "T-2": True, "T-3": False, "T-4": False}), _stage1_run({"T-1": False, "T-2": False, "T-3": False, "T-4": False})],
                   levels={"T-1": "high", "T-2": "low"})
    notes2, jm2, _, _, _ = _run("P2p_stable", llm2, tmp_path / "x")
    assert [n["fact_id"] for n in notes2] == ["T-1"] and jm2["T-2"]["dropped_by"] == ["stage1_5_low"]  # highは片回でも通過、lowは落ちる


def test_p3_judge_gets_headline_not_stage1_compression(tmp_path):
    llm = FakeLLM([_stage1_run({"T-1": True, "T-2": True, "T-3": False, "T-4": False})], levels={"T-1": "high", "T-2": "low"},
                  headlines={"T-1": "甲が乙を見出し要約"})
    notes, jm, prov, _, _ = _run("P3_writer_compress", llm, tmp_path)
    j = llm.prompts["judge"][0].split("【入力】\n", 1)[1]
    assert "甲が乙を見出し要約" in j and "圧縮-T-1" not in j and RS["T-1"] in j  # 判定役は見出し要約とRのみ
    h = llm.prompts["headline"][0].split("【入力】\n", 1)[1]
    assert RS["T-1"] not in h and "試験段階" not in h and "丁と書かない" not in h  # 見出し要約はclaimのみ
    assert jm["T-1"]["headline"] == "甲が乙を見出し要約" and [n["fact_id"] for n in notes] == ["T-1"]


def test_p3_headline_missing_dropped(tmp_path):
    class NoHead(FakeLLM):
        def __call__(self, prompt, web_search="none"):
            r = super().__call__(prompt, web_search)
            if "見出し用に要約する記事執筆者" in prompt:
                r["parsed"] = {"headlines": []}
            return r
    llm = NoHead([_stage1_run({"T-1": True, "T-2": False, "T-3": False, "T-4": False})], levels={"T-1": "high"})
    notes, jm, _, _, _ = _run("P3_writer_compress", llm, tmp_path)
    assert notes == [] and jm["T-1"]["dropped_by"] == ["headline_missing"]


def test_cover_skips_stage2_and_passes_already_prohibited(tmp_path):
    llm = FakeLLM([_stage1_run({"T-1": True, "T-2": True, "T-3": False, "T-4": False})], levels={"T-1": "high", "T-2": "high"}, covers={"T-1": True})
    notes, jm, prov, _, _ = _run("P1p_gate_hm", llm, tmp_path)
    assert [n["fact_id"] for n in notes] == ["T-2"] and jm["T-1"]["dropped_by"] == ["existing_note_covers_R"] and prov["cover_skipped"] == ["T-1"]
    assert len(llm.prompts["cover"]) == 1 and "丁と書かない" in llm.prompts["cover"][0] and "T-2" not in llm.prompts["cover"][0].split("【入力】")[1]  # 既存notesのあるfactだけ
    llm2 = FakeLLM([_stage1_run({"T-1": True, "T-2": False, "T-3": False, "T-4": False})], levels={"T-1": "high"}, covers={"T-1": False})
    notes2, jm2, _, _, _ = _run("P1p_gate_hm", llm2, tmp_path / "y")
    cands = json.loads(llm2.prompts["s2"][0].split("【候補】\n", 1)[1].split("\n\n【Fact一覧", 1)[0])
    assert cands[0]["already_prohibited"] == ["丁と書かない。"]  # 「既に禁じ済み」一覧として渡る
    fl = llm2.prompts["s2"][0].split("【Fact一覧")[1]
    assert "notes_for_writer" not in fl  # Fact一覧側には既存notesを載せない(肯定的ヒントにしない)
    assert [n["fact_id"] for n in notes2] == ["T-1"]


def test_stage2_r_echo_and_r_in_note_and_lint_and_english(tmp_path):
    base = {"T-1": True, "T-2": True, "T-3": True, "T-4": True}
    s2 = {"T-1": {"r_echo": "全く別の命題"},  # r_echo不一致
          "T-2": {"note": PFX + "正しい状態Xである。別の読みではない。"},  # noteのR部分が採用Rと一致しない
          "T-3": {"correct_state": "元に戻した状態"},  # vague語
          "T-4": {"note": PFX + "正しい状態Xである。" + RS["T-4"] + "ではない。Apple社の"}}  # 英語が台帳に無い
    llm = FakeLLM([_stage1_run(base)], levels={f: "high" for f in base}, s2=s2)
    notes, jm, _, out, rej = _run("P1p_gate_hm", llm, tmp_path)
    assert notes == []
    reasons = {r["fact_id"]: r["reason"] for r in rej}
    assert reasons == {"T-1": "r_echo_mismatch", "T-2": "r_not_in_note", "T-3": "lint_rejected", "T-4": "english_not_in_ledger"}
    lr = json.loads((out / "lint_rejected.json").read_text(encoding="utf-8"))
    assert {e["fact_id"] for e in lr if e["stage"] == "stage2"} == {"T-3", "T-4"}
    assert jm["T-1"]["stage2"]["result"] == "r_echo_mismatch" and jm["T-1"]["dropped_by"] == ["stage2_r_echo_mismatch"]


def test_stage2_hyoki_quote_must_be_in_claim_and_accepts_good_note():
    item = {"fact_id": "T-1", "claim": "甲が乙を差し戻した", "scope": "窓口", "conditions": None, "notes_for_writer": None}
    c = {"fact_id": "T-1", "reverse_reading": "甲は乙を廃止した", "ambiguous_expression": "差し戻した"}
    good = {"fact_id": "T-1", "r_echo": "甲は乙を廃止した", "correct_state": "乙の適用が当面行われない状態",
            "note": PFX + "台帳の表記'差し戻した'は、乙の適用が当面行われない状態の意味。甲は乙を廃止したのではない。",
            "self_check": {"R_is_natural_reading": True, "correct_statement_derivable_from_ledger": True}}
    ok, why, det = P.check_stage2(good, c, item)
    assert ok and why is None and det["r_coverage"] >= 0.5
    bad = dict(good, note=good["note"].replace("'差し戻した'", "'撤回した'"))
    assert P.check_stage2(bad, c, item)[1] == "hyoki_not_in_ledger"
    # 曖昧表記を引用符の外(正しい状態欄)で使うとlint違反
    bad2 = dict(good, note=PFX + "甲が乙を差し戻した状態。甲は乙を廃止したのではない。")
    assert P.check_stage2(bad2, c, item)[1] == "lint_rejected"
    # 英語は台帳に実在すれば可
    item2 = dict(item, claim="甲が乙(Pilot)を差し戻した")
    assert P.check_stage2(dict(good, note=good["note"] + "Pilot"), c, item2)[0] is True


def test_load_pattern_modes():
    for n, m in (("P1p_gate_hm", "p04_gate"), ("P2p_stable", "p04_stable"), ("P3_writer_compress", "p04_gate")):
        p = G.load_pattern(n)
        assert p["mode"] == m and G.is_two_stage(p) and p["stage1_5"] and p["stage2"] and p["cover"]
    assert G.load_pattern("P3_writer_compress")["headline"] and G.load_pattern("P2p_stable")["stage1_repeats"] == 2
    assert G.load_pattern("P2p_stable")["meta"]["medium_requires_stable"] is True and G.load_pattern("P1p_gate_hm")["meta"]["medium_requires_stable"] is False


# ---------- rollback Gate機械チェック(合成文) ----------
def test_rollback_gate_pass_examples():
    ok1 = PFX + "原語'withdrew the pilot program'=試験導入を取り下げた(導入前の状態へ戻した)。試験導入を再開・再提供した意味ではない。"
    ok2 = PFX + "提供者が機能を取り下げ、機能のない状態へ戻した。機能そのものを復活・再提供した意味ではない。"
    for n in (ok1, ok2):
        r = E4.rollback_gate_check(n)
        assert r["result"] == "PASS_CANDIDATE", (n, r)


def test_rollback_gate_fail_examples():
    f1 = PFX + "サービス全体停止ではない。"  # 全体だけの否定
    f2 = PFX + "機能を元に戻した。"  # 元に戻しただけ
    f3 = PFX + "機能を取り下げた。機能の復元ではない。"  # 導入前状態への復帰まで禁じる表現
    f4 = PFX + "機能を取り下げた。サービス全体を再開した意味ではない。"  # 全体だけを否定
    f5 = PFX + "機能を取り下げ、元の状態に戻していない。機能を再提供した意味ではない。"
    for n in (f1, f2, f3, f4, f5):
        r = E4.rollback_gate_check(n)
        assert r["result"] == "FAIL_CANDIDATE", (n, r)
    assert E4.rollback_gate_check(None)["result"] == "FAIL_CANDIDATE"


def test_gate_eval_uncaptured_and_captured():
    assert E4.gate_eval([], "X-1")["captured"] is False
    g = E4.gate_eval([{"fact_id": "X-1", "note": PFX + "機能を取り下げた。機能を再提供した意味ではない。"}], "X-1")
    assert g["captured"] and g["check"]["result"] == "PASS_CANDIDATE"


def test_stability_and_holdout():
    s = E4.stability(["a", "b", "c"], ["b", "c", "d"])
    assert abs(s["jaccard"] - 0.5) < 1e-9 and s["both"] == 2 and s["only_a"] == 1 and s["only_b"] == 1
    assert E4.stability([], [])["jaccard"] == 1.0
    assert E4.holdout_over(3, 2) == 1 and E4.holdout_over(1, 2) == 0 and E4.holdout_over(1, None) is None


def test_holdout_and_targets_files():
    h = json.loads((TRIAL / "eval" / "holdout.json").read_text(encoding="utf-8"))["themes"]
    assert {"A02", "small_bag", "A01"} <= set(h) and all("expected_max" in v for v in h.values())
    assert (TRIAL.parents[1] / h["A01"]["draft"]).exists() and (TRIAL.parents[1] / h["A01"]["txt"]).exists() and (TRIAL.parents[1] / h["A01"]["verif"]).exists()
    t = json.loads((TRIAL / "eval" / "targets.json").read_text(encoding="utf-8"))["themes"]
    assert t["meta"]["gate_fact"] in t["meta"]["targets"]


# ---------- TRIAL-04 L2 (P4_paraphrase / H11-H13) ----------
def test_h13b_vague_word_inside_compound_not_hit_but_word_use_hit():
    assert P.vague_hits("市街化調整区域を定めた") == []  # 両側が漢字の語内一致は除外
    assert P.vague_hits("価格を調整した") and P.vague_hits("制度見直しを行った") and P.vague_hits("設定を元に戻した")
    assert P.vague_hits("調整を行った") and P.vague_hits("仕様変更した")


def test_h13a_r_echo_trailing_punct_normalized():
    item = {"fact_id": "T-1", "claim": "甲が乙を差し戻した", "scope": "窓口", "conditions": None, "notes_for_writer": None}
    c = {"fact_id": "T-1", "reverse_reading": "甲は乙を廃止した", "ambiguous_expression": "差し戻した"}
    n = {"fact_id": "T-1", "r_echo": "甲は乙を廃止した。", "correct_state": "乙の適用が当面行われない状態",
         "note": PFX + "表記'差し戻した'=乙の適用が当面行われない状態。甲は乙を廃止したのではない。",
         "self_check": {"R_is_natural_reading": True, "correct_statement_derivable_from_ledger": True}}
    assert P.check_stage2(n, c, item)[0] is True


def test_h13d_acronym_allowed_but_other_english_rejected():
    item = {"claim": "甲が乙を停止", "scope": None, "conditions": None}
    assert P.english_not_in_ledger("FW25 と SS25 の", item) == [] and P.english_not_in_ledger("Apple社", item) == ["Apple"]


def test_h13e_missing_verdict_keys_and_subset():
    per = {"T-1": [{"cid": "A"}], "T-2": [{"cid": "A"}, {"cid": "B"}]}
    v = [{"fact_id": "T-1", "cid": "A", "likelihood": "high"}, {"fact_id": "T-2", "cid": "A", "likelihood": "bogus"}]
    miss = P.missing_verdict_keys(["T-1", "T-2"], per, v)
    assert miss == [("T-2", "A"), ("T-2", "B")]
    o2, p2 = P.subset_order_per(["T-1", "T-2"], per, miss)
    assert o2 == ["T-2"] and len(p2["T-2"]) == 2


def test_p4_pattern_loads_lint_pass_and_prompt_has_h11_h12():
    res = L.lint_pattern(PATS / "P4_paraphrase", PATS / "_common" / "stage1_prompt.txt", FORBIDDEN)
    assert all(not e for e in res.values()), res
    p = G.load_pattern("P4_paraphrase")
    assert p["mode"] == "p04_gate" and p["meta"]["stage1_existing_notes"] is True and p["meta"]["cover_record_only"] is True
    s1 = p["stage1"]
    assert "2つ以上" in s1 and "両方向" in s1 and "別の読み" in s1 and "paraphrase_readings" in s1
    assert "のではない" in p["stage2"] and "already_prohibited" not in p["stage2"]


def test_p4_cover_record_only_keeps_note_and_no_already_prohibited(tmp_path):
    llm = FakeLLM([_stage1_run({"T-1": True, "T-2": True, "T-3": False, "T-4": False})], levels={"T-1": "high", "T-2": "high"}, covers={"T-1": True})
    notes, jm, prov, _, _ = _run("P4_paraphrase", llm, tmp_path)
    assert sorted(n["fact_id"] for n in notes) == ["T-1", "T-2"]  # cover=trueでも除外しない
    assert jm["T-1"]["existing_note"]["dup_of_existing"] is True and prov["cover_dup_ids"] == ["T-1"] and prov["cover_skipped"] == []
    cands = json.loads(llm.prompts["s2"][0].split("【候補】\n", 1)[1].split("\n\n【Fact一覧", 1)[0])
    assert all("already_prohibited" not in c for c in cands)


def test_p4_judge_missing_verdict_requeried_once(tmp_path):
    class Miss(FakeLLM):
        n = 0

        def __call__(self, prompt, web_search="none"):
            r = super().__call__(prompt, web_search)
            if "判定役" in prompt:
                Miss.n += 1
                if Miss.n == 1:
                    r["parsed"]["verdicts"] = [v for v in r["parsed"]["verdicts"] if v["fact_id"] != "T-2"]
            return r
    llm = Miss([_stage1_run({"T-1": True, "T-2": True, "T-3": False, "T-4": False})], levels={"T-1": "high", "T-2": "high"})
    notes, jm, prov, out, _ = _run("P4_paraphrase", llm, tmp_path)
    assert len(llm.prompts["judge"]) == 2 and prov["judge_missing_first"] == 1 and prov["judge_missing_after_requery"] == 0
    assert "T-1" not in llm.prompts["judge"][1].split("【入力】")[1] and sorted(n["fact_id"] for n in notes) == ["T-1", "T-2"]
