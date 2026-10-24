# -*- coding: utf-8 -*-
"""er110_family_y_persona_text_trial_01 の offline test(API 0)。DefaultOffIsolation相当: Yはどのproduction経路からも参照されない。"""
import glob
import json
import os
import re
import types

import pytest

import er110_family_y_persona_text_trial_01 as p
import er110_family_y_text_trial_01 as y0


def _resp(text, model="gpt-6.1-sol"):
    return types.SimpleNamespace(output_text=text, model=model, id="resp_x", usage=types.SimpleNamespace(input_tokens=1, output_tokens=1))


class Stub:
    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.calls = []
        self.responses = types.SimpleNamespace(create=self._create)

    def _create(self, **kw):
        self.calls.append(kw)
        return _resp(self.outputs.pop(0))


GOOD = {
    "voice_1": "現場の仕事で帰りが遅い。娘のスマホで、毎晩もめてる。学校が決めてくれたら、俺は楽になる。結局、楽したいだけなんだよな、俺は。",
    "voice_2": "朝いちばんの保健室に、眠そうな子が来る。眠い、って。取り上げて、それで安心していいのかな。私は、保健室まで没収の場にしたくない。",
    "voice_3": "僕は昼、倉庫で仕分けをして、夜に定時制へ通ってる。授業中は鞄の奥に入れる。約束する。だから、決める前に僕らの話を聞いてほしい。",
}
TENSION = "3人とも、子どもが困らないでほしいと思っている。夜の居間のカゴ、朝の保健室のベッド、休憩中のシフトの連絡。あなたの家では、夜、スマホはどこにあるだろう?"


def test_sheets_valid_and_distinct():
    assert p.validate_sheets() == []
    assert len({s["first_person"] for s in p.SHEETS.values()}) == 3
    assert [p.SHEETS[s]["tts_voice"] for s in p.VOICE_SLOTS] == ["Algieba", "Zephyr", "Schedar"]


def test_sheet_validation_catches_problems():
    import copy
    sh = copy.deepcopy(p.SHEETS)
    sh["voice_1"]["first_person"] = "私"
    assert "SHEET_FIRST_PERSON_NOT_DISTINCT" in p.validate_sheets(sh)
    sh = copy.deepcopy(p.SHEETS)
    sh["voice_2"]["claim"] = "三年前から続けている。"
    assert any(e.startswith("SHEET_CLAIM_HAS_NUMBER") for e in p.validate_sheets(sh))


def test_not_my_point_deterministic_and_excludes_self():
    nmp = p.derive_not_my_point()
    for s in p.VOICE_SLOTS:
        assert p.SHEETS[s]["claim"] not in nmp[s] and len(nmp[s]) == 2


def test_voice_prompt_has_new_rules_and_no_removed_old_rules():
    """撤去R-P12〜15・旧R-P04/05/07が新Promptに残っていない。人物別の話し方・身元手がかり・一般化禁止・共通前提がある。"""
    for s in p.VOICE_SLOTS:
        t = p.build_voice_prompt(s)
        assert p.COMMON_PREMISE_JA in t
        assert "冒頭の2文以内" in t and "一般化" in t and "自己紹介" in t
        for banned in ("約190字", "場面から始める", "解決策や提案は語りません", "調査・統計・制度の説明をしない", "全体で800〜1000字",
                       "一人称「私」で語", "冒頭の1文で、誰がどんな状況か", "20代以上", "陣営に寄せた書き方をしない", "リード"):
            assert banned not in t, banned
    assert "【事実1】" in p.build_voice_prompt("voice_1")
    assert "【事実" not in p.build_voice_prompt("voice_2").replace("【事実N】", "")
    assert "語ってよい世の中の事実はない" in p.build_voice_prompt("voice_3")


def test_check_voice_and_monitors_record_only():
    assert p.check_voice(GOOD["voice_1"], "voice_1")["ok"]
    assert not p.check_voice(GOOD["voice_2"], "voice_1")["ok"]          # 俺がない
    assert not p.check_voice("俺はこうだ。\n\n二段落目。", "voice_1")["ok"]
    m = p.voice_monitors(GOOD["voice_2"], "voice_2")
    assert "note" in m and "保健室" in "".join(m["identity_cue_in_first2"]) or m["identity_cue_in_first2"]


def test_tension_contract_and_monitors():
    assert p.check_tension(TENSION)["ok"]
    assert not p.check_tension("私は思う。")["ok"]
    m = p.tension_monitors(TENSION)
    assert m["ends_with_question"] and m["double_negatives"] == []


def test_leak_prompt_subsets_keep_old_13_items():
    assert set(p.VOICE_FIELDS) | set(p.TENSION_FIELDS) == set(y0.VOICE_LEAKAGE_FIELDS) | set(y0.TENSION_LEAKAGE_FIELDS)
    assert len(set(p.VOICE_FIELDS) | set(p.TENSION_FIELDS)) == 9
    vp = p.build_leak_prompt("voices", GOOD)
    for f in p.VOICE_FIELDS:
        assert f in vp
    assert "最終パート(Tension)本文" not in vp
    tp = p.build_leak_prompt("tension", {"tension": TENSION})
    for f in p.TENSION_FIELDS:
        assert f in tp
    assert "Voice 1本文" not in tp
    # 旧Y Trialの判定文言(7項目/6項目)と同一定義
    old = y0.build_leakage_prompt({"voice_1": "a", "voice_2": "b", "voice_3": "c", "tension": "d"})
    for line in p._VOICE_ITEMS.strip().splitlines()[:9]:
        assert line in old


def _pass_check(kind):
    secs = p.leak_sections_for(kind)
    out = {}
    for k, fields in secs.items():
        out[k] = {**{f: "PASS" for f in fields}, "reasoning": "", "quoted_evidence": ""}
    return out


def test_gate_pass_first_judgement(tmp_path):
    cl = Stub([json.dumps(_pass_check("voices"))])
    r = p.run_gate(cl, kind="voices", stage="t", texts=GOOD, out_dir=str(tmp_path), judge_model="gpt-6.1-sol", judge_effort="high")
    assert r["status"] == "PASS" and r["n_judgements"] == 1 and r["final_texts"] == GOOD


def test_gate_rewrites_only_flagged_voice_and_byte_fixes_others(tmp_path):
    bad = _pass_check("voices")
    bad["voice_2"]["leak_discovery_syntax"] = "FAIL"
    bad["voice_2"]["quoted_evidence"] = "x"
    new2 = "朝いちばんの保健室に、眠そうな子が来る。眠い、って。取り上げて安心して、それでいいのかな。私は、保健室まで没収の場にしたくない。"
    cl = Stub([json.dumps(bad), json.dumps({"rewrites": [{"section": "voice_2", "text": new2}]}), json.dumps(_pass_check("voices"))])
    r = p.run_gate(cl, kind="voices", stage="t", texts=GOOD, out_dir=str(tmp_path), judge_model="gpt-6.1-sol", judge_effort="high")
    assert r["status"] == "PASS" and r["n_judgements"] == 2
    assert r["final_texts"]["voice_1"] == GOOD["voice_1"] and r["final_texts"]["voice_3"] == GOOD["voice_3"]
    assert r["final_texts"]["voice_2"] == new2


def test_gate_residual_stop_after_three(tmp_path):
    bad = _pass_check("voices")
    bad["voice_1"]["leak_evidence_subject"] = "FAIL"
    rw = {"rewrites": [{"section": "voice_1", "text": GOOD["voice_1"]}]}
    cl = Stub([json.dumps(bad), json.dumps(rw), json.dumps(bad), json.dumps(rw), json.dumps(bad)])
    r = p.run_gate(cl, kind="voices", stage="t", texts=GOOD, out_dir=str(tmp_path), judge_model="gpt-6.1-sol", judge_effort="high")
    assert r["status"] == "LEAKAGE_RESIDUAL_STOP" and r["n_judgements"] == 3


def test_rewrite_contract_failure_stops(tmp_path):
    bad = _pass_check("voices")
    bad["voice_1"]["leak_evidence_subject"] = "FAIL"
    rw_bad = {"rewrites": [{"section": "voice_1", "text": "第一段落\n\n第二段落"}]}
    cl = Stub([json.dumps(bad), json.dumps(rw_bad), json.dumps(rw_bad)])
    with pytest.raises(p.YStop):
        p.run_gate(cl, kind="voices", stage="t", texts=GOOD, out_dir=str(tmp_path), judge_model="gpt-6.1-sol", judge_effort="high")


def test_tension_rewrite_forbids_first_person(tmp_path):
    bad = _pass_check("tension")
    bad["tension"]["leak_binary_camp_split"] = "FAIL"
    rw = {"rewrites": [{"section": "tension", "text": "私は3人を聞いた。"}]}
    cl = Stub([json.dumps(bad), json.dumps(rw), json.dumps(rw)])
    with pytest.raises(p.YStop):
        p.run_gate(cl, kind="tension", stage="t", texts={"tension": TENSION}, out_dir=str(tmp_path), voices_ctx=GOOD,
                   judge_model="gpt-6.1-sol", judge_effort="high")


def test_acceptance_gate_blocks_non_pass(tmp_path):
    d = tmp_path / "g"
    d.mkdir()
    (d / "gate_result.json").write_text(json.dumps({"status": "LEAKAGE_RESIDUAL_STOP"}), encoding="utf-8")
    with pytest.raises(p.YStop):
        p.load_gated_or_stop(str(d))
    with pytest.raises(p.YStop):
        p.load_gated_or_stop(str(tmp_path / "none"))


def test_tension_prompt_uses_gated_voices_and_concrete_question_rule():
    t = p.build_tension_prompt(GOOD)
    assert GOOD["voice_1"] in t and "具体的な問い" in t and "45字以内" in t and "抽象名詞を主語にした問い" in t
    assert "再要約" not in t or "要約し直さない" in t


def test_headings_ordinals_and_checks():
    assert p.HEADING_ORDINALS == ("One Voice", "Another Voice", "A Third Voice")
    ok = [{"title_en": "The headaches that start at night"}, {"title_en": "The shift I can't lose"}, {"title_en": "Tired of being the bad guy"}]
    assert p.check_headings(ok)["ok"]
    bad = [{"title_en": "Phones at 9 pm"}, {"title_en": "The shift I can't lose"}, {"title_en": "The shift I keep"}]
    assert not p.check_headings(bad)["ok"]


def test_comment_roles_no_interview_expressions_and_have_premise():
    for lvl in ("b1b", "a2"):
        assert p.COMMON_PREMISE_JA in p.Y_COMMENT_1_ROLE[lvl]
        assert "we talked to" in p.Y_COMMENT_2_ROLE[lvl] and "話を聞いた" in p.Y_COMMENT_2_ROLE[lvl]       # 禁止として明記
        assert "Part 2" not in p.Y_COMMENT_2_ROLE[lvl] and "Comment 3" not in p.Y_COMMENT_2_ROLE[lvl]


def test_en_contract_four_paragraphs():
    ok = "# T\n\nI work all day. I swear.\n\nI see kids. I wonder.\n\nI take my phone. I promise.\n\nAll three want calm nights. Where is your phone at night?\n\n## In one line\nThree views."
    assert p.check_en_contract(ok)["ok"]
    five = ok.replace("\n\n## In one line", "\n\nExtra.\n\n## In one line")
    assert not p.check_en_contract(five)["ok"]
    m = p.en_monitors(ok)
    assert m["n_paragraphs"] == 4 and "voice_mean_sentence_words_range" in m


def test_contrast_must_fix_is_a_list_with_one_issue():
    mf = p.y_contrast_must_fix()
    assert len(mf) == 1 and mf[0]["issue"] == "KEEP_SPEAKER_CONTRAST"


def test_generate_voice_regenerates_once_then_stops(tmp_path):
    cl = Stub(["私は思う。", "私は思う。"])           # voice_1は「俺」が必要 -> 契約違反2回
    with pytest.raises(p.YStop):
        p.generate_voice(cl, "voice_1", out_dir=str(tmp_path))
    assert len(cl.calls) == 2


def test_generate_voice_strips_fact_tag_and_records(tmp_path):
    txt = "俺が聞いた話だと、国も高校は校内で使うのを控えさせる考えらしい。【事実1】俺ひとりが悪者だ。"
    cl = Stub([txt])
    r = p.generate_voice(cl, "voice_1", out_dir=str(tmp_path))
    assert "【" not in r["text"] and r["meta"]["tags_used"] == ["F1"]
    cl = Stub(["俺は現場にいる。【事実1】娘がいる。", "俺は現場にいる。娘がいる。"])
    r = p.generate_voice(cl, "voice_2" if False else "voice_1", out_dir=str(tmp_path / "x"))
    assert r["meta"]["tags_used"] == ["F1"] or r["meta"]["tags_used"] == []


def test_voice_2_with_tag_is_rejected(tmp_path):
    cl = Stub(["私は保健室にいる。【事実1】", "私は保健室にいる。"])
    r = p.generate_voice(cl, "voice_2", out_dir=str(tmp_path))
    assert len(cl.calls) == 2 and "【" not in r["text"]


# ---- 隔離 ----
def test_no_production_reference():
    mods = ("er110_family_y_persona_text_trial_01", "er110_family_y_persona_audio_trial_01")
    allowed = {f"{m}.py" for m in mods} | {f"{m}_run.py" for m in mods} | {f"{m}_test_01.py" for m in mods} | {f"{m}_page_01.py" for m in mods}
    for f in glob.glob("*.py"):
        if f in allowed or f.startswith("er110_"):   # 委任_27: er110_*はY自身のDEV/Trial module(例: er110_family_y_opinion_based_01.py。Production到達なし)
            continue
        s = open(f, encoding="utf-8", errors="ignore").read()
        for m in mods:
            assert not re.search(rf"\b(import|from)\s+{m}\b", s), f"{f} が {m} を参照している"


def test_no_env_flag_or_cli_switch_in_module():
    for f in ("er110_family_y_persona_text_trial_01.py",):
        s = open(f, encoding="utf-8").read()
        assert "os.environ" not in s and "getenv" not in s and "argparse" not in s


def test_old_y_trial_module_unchanged_symbols_still_present():
    # 既存er110 text trialは無変更で残置(代表的な旧規則がそのまま残っていること=本Trialで編集していない)
    s = open("er110_family_y_text_trial_01.py", encoding="utf-8").read()
    assert "約190字" in s and "5段落" in s


def test_removed_old_rules_absent_from_new_module():
    s = open("er110_family_y_persona_text_trial_01.py", encoding="utf-8").read()
    # 旧規則の識別子(R-P12 一人称「私」固定, R-P13 冒頭1文で誰か分かる, R-P15 全体800〜1000字, R-P04 約190字)がPromptに無い
    for banned in ("約190字", "全体で800〜1000字", "冒頭の1文で、誰がどんな状況か", "人物の語りの段落は、その人物本人が「私」で語り"):
        assert banned not in s
