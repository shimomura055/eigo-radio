# -*- coding: utf-8 -*-
"""er110_family_y_text_trial_01 の offline test(API 0)。DefaultOffIsolation相当: Yはどのproduction経路からも参照されない。"""
import glob
import json
import os
import re
import types

import pytest

import er110_family_y_text_trial_01 as y
import er053_family_x_factlock_ja_writer_01 as w1


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


GOOD_PARAS = [
    "朝の教室で、スマホの通知音が鳴った。",
    "私は国語を教えている。授業中に画面を見ている生徒の顔が、いちばん気になる。",
    "私は中学生の娘の母親だ。夕方に連絡がつかないと、胸がざわざわする。",
    "私は公園で野球を教えている。休み時間にみんなが画面を見ていると、少し寂しい。",
    "三人とも、子どもが穏やかに過ごせることを望んでいる。守りたいものが違うから、答えが分かれる。",
]
TITLE = "教室のスマホ"


def art(paras=GOOD_PARAS, title=TITLE):
    return y.render_article(title, paras)


def test_contract_ok_and_violations():
    assert y.check_contract(y.parse_article(art()))["ok"]
    assert not y.check_contract(y.parse_article(art(GOOD_PARAS[:4])))["ok"]
    bad = list(GOOD_PARAS)
    bad[2] = "娘の母親は、夕方に連絡がつかないと不安だ。"
    r = y.check_contract(y.parse_article(art(bad)))
    assert any("VOICE_NO_FIRST_PERSON" in v for v in r["violations"])
    bad = list(GOOD_PARAS)
    bad[0] = "私は朝の教室にいる。"
    assert any("NARRATOR_STARTS" in v for v in y.check_contract(y.parse_article(art(bad)))["violations"])


def test_monitors_record_only():
    ps = list(GOOD_PARAS)
    ps[1] += "三年前から続けている。"
    m = y.monitors(y.parse_article(art(ps)))
    assert m["voice_numbers"]["voice_1"]
    assert "note" in m and m["n_paragraphs"] == 5


def _cast(fids=("F1", None, "F3")):
    voices = []
    for s, f in zip(y.VOICE_SLOTS, fids):
        voices.append({"slot": s, "gender": y.VOICE_GENDER[s], "age_band": "40代", "person_label": "x", "difference_axis": "経験",
                       "viewpoint_oneline": "v", "background_fact_id": f})
    return {"voices": voices, "common_ground": "c", "independence_note": "n"}


def _cards(ids=(["F1"], [], ["F3"])):
    cs = []
    for i, (s, f) in enumerate(zip(y.VOICE_SLOTS, ids)):
        k = "アイウ"[i]
        cs.append({"slot": s, "gender": y.VOICE_GENDER[s], "person_label": f"人物{k}", "situation_and_scene": "場面",
                   "concern": f"懸念{k}", "stake": f"賭け{k}", "constraint": "制約", "background_fact_ids": f})
    return {"cards": cs}


def test_validate_cast_and_cards():
    assert y.validate_cast(_cast(), {"F1", "F3"}) == []
    c = _cast()
    c["voices"][0]["gender"] = "女性"
    assert any("GENDER" in e for e in y.validate_cast(c, {"F1", "F3"}))
    assert any("DUPLICATE" in e for e in y.validate_cast(_cast(("F1", "F1", None)), {"F1"}))
    assert y.validate_cards(_cards(), {"F1", "F3"}) == []
    bad = _cards()
    bad["cards"][0]["concern"] = "三割の生徒が"
    assert any("NUMBER" in e for e in y.validate_cards(bad, {"F1", "F3"}))
    bad = _cards()
    bad["cards"][1]["concern"] = bad["cards"][0]["concern"]
    assert any("CONCERN_DUPLICATE" in e for e in y.validate_cards(bad, {"F1", "F3"}))


def test_not_my_point_deterministic():
    n = y.derive_not_my_point(_cards())
    assert n["voice_1"] == ["懸念イ", "懸念ウ"] and n["voice_3"] == ["懸念ア", "懸念イ"]


def test_fixed_tts_voice_assignment_is_not_automatic():
    assert y.TTS_VOICE_FIXED == {"voice_1": "Algieba", "voice_2": "Zephyr", "voice_3": "Schedar"}


def test_r0_prompt_reuses_x_factlock_block_and_x_prompts_unchanged():
    p = y.build_y_r0_prompt("テーマ", "- 【事実1】何かの事実", _cards())
    assert w1.build_r0_block(__import__("er019_family_x_ja_writer_o_r1_r2_01").CONCRETENESS_CONTROL_AN3_BLOCK) in p
    assert "人物カード1" in p and "この人物の中心の論点にしないこと" in p
    assert y.USER_TMPL_Y.startswith(w1.USER_TMPL)       # X Promptは逐語のまま(追加は末尾のみ)
    assert "【事実1】の範囲" in p


def test_apply_local_rewrite_only_flagged_and_byte_fixed():
    ps = list(GOOD_PARAS)
    new, det = y.apply_local_rewrite(ps, [{"paragraph_index": 3, "text": "私は娘と話し合っている。家のルールは、まだ決まらない。"}], {2}, allow_tags=False)
    assert det["errors"] == [] and new[2] != ps[2]
    assert [new[i] for i in (0, 1, 3, 4)] == [ps[i] for i in (0, 1, 3, 4)]
    # スコープ外・記号違反
    _, det = y.apply_local_rewrite(ps, [{"paragraph_index": 2, "text": "私は…"}], {2}, allow_tags=False)
    assert any("OUT_OF_SCOPE" in e for e in det["errors"])
    _, det = y.apply_local_rewrite(ps, [{"paragraph_index": 3, "text": "私は(括弧)を使う。"}], {2}, allow_tags=False)
    assert any("SYMBOL" in e for e in det["errors"])
    # 不明なFactタグ
    _, det = y.apply_local_rewrite(ps, [{"paragraph_index": 3, "text": "制度がある。【事実9】"}], {2}, allow_tags=True, valid_fact_nums={1, 2})
    assert any("UNKNOWN_FACT_TAG" in e for e in det["errors"])


def _leak(flag_sections):
    d = {}
    for sec, fields in y.LEAK_SECTIONS.items():
        it = {f: "PASS" for f in fields}
        it["reasoning"] = "r"
        it["quoted_evidence"] = ""
        if sec in flag_sections:
            it[fields[0]] = "FAIL"
            it["quoted_evidence"] = "q"
        d[sec] = it
    return json.dumps(d, ensure_ascii=False)


def test_gate_pass_after_one_rewrite(tmp_path):
    stub = Stub([_leak({"voice_2"}), json.dumps({"rewrites": [{"paragraph_index": 3, "text": "私は娘を待っている。メッセージが来ないと、胸がざわつく。"}]}, ensure_ascii=False), _leak(set())])
    r = y.run_gate(stub, stage="t", title=TITLE, paragraphs=list(GOOD_PARAS), cards_obj=_cards(), out_dir=str(tmp_path), judge_model="gpt-6.1-sol", judge_effort="low")
    assert r["status"] == "PASS" and r["n_judgements"] == 2 and len(stub.calls) == 3
    assert r["final_paragraphs"][2] != GOOD_PARAS[2]
    assert [r["final_paragraphs"][i] for i in (0, 1, 3, 4)] == [GOOD_PARAS[i] for i in (0, 1, 3, 4)]
    assert r["first_judgement_flagged"] is True


def test_gate_residual_stop_after_three_judgements_two_rewrites(tmp_path):
    rw = json.dumps({"rewrites": [{"paragraph_index": 2, "text": "私は黒板の前に立っている。画面を見る目が気になる。"}]}, ensure_ascii=False)
    stub = Stub([_leak({"voice_1"}), rw, _leak({"voice_1"}), rw, _leak({"voice_1"})])
    r = y.run_gate(stub, stage="t", title=TITLE, paragraphs=list(GOOD_PARAS), cards_obj=_cards(), out_dir=str(tmp_path), judge_model="gpt-6.1-sol", judge_effort="low")
    assert r["status"] == "LEAKAGE_RESIDUAL_STOP" and r["n_judgements"] == 3 and len(stub.calls) == 5   # 判定3 + 書き換え2。全文書き直しへ戻らない


def test_gate_rewrite_validation_failure_stops(tmp_path):
    bad = json.dumps({"rewrites": [{"paragraph_index": 2, "text": "私は(括弧)で話す。"}]}, ensure_ascii=False)
    stub = Stub([_leak({"voice_1"}), bad, bad])
    with pytest.raises(y.YStop) as e:
        y.run_gate(stub, stage="t", title=TITLE, paragraphs=list(GOOD_PARAS), cards_obj=_cards(), out_dir=str(tmp_path), judge_model="gpt-6.1-sol", judge_effort="low")
    assert e.value.code == "REWRITE_STOP"


def test_generate_r0_regenerates_once_then_stops(tmp_path):
    four = TITLE + "\n\n" + "\n\n".join(GOOD_PARAS[:4])
    stub = Stub([four, art()])
    r = y.generate_r0(stub, prompt="P", out_dir=str(tmp_path))
    assert len(stub.calls) == 2 and y.check_contract(y.parse_article(r["final"]))["ok"]
    assert "前回の出力の問題" in stub.calls[1]["input"][-1]["content"]
    stub = Stub([four, four])
    with pytest.raises(y.YStop):
        y.generate_r0(stub, prompt="P", out_dir=str(tmp_path / "b"))
    assert len(stub.calls) == 2


def test_provenance_model_mismatch_stops():
    class Bad:
        def __init__(self):
            self.responses = types.SimpleNamespace(create=lambda **kw: _resp("x", model="other-model"))
    with pytest.raises(y.ProvenanceViolation):
        y.chat(Bad(), model="gpt-6.1-sol", effort="low", user="u", stage="s")


def test_en_contract():
    en = "# Phones\n\n" + "\n\n".join(["Morning begins.", "I teach Japanese. I watch screens.", "I am a mother. My daughter is late.", "I coach baseball. I miss talking.", "All three want calm."]) + "\n\n## In one line\nTwo sentences here. Another one."
    assert y.check_en_contract(en)["ok"]
    assert not y.check_en_contract(en.replace("\n\nAll three want calm.", ""))["ok"]


def test_no_production_reference():
    """Yのtrial module / run scriptを参照する.pyは、Y自身のfile以外に存在しない(Production到達経路0)。"""
    me = {os.path.normpath(p) for p in glob.glob("er110_family_y_*.py")}
    offenders = []
    for p in glob.glob("*.py"):
        if os.path.normpath(p) in me:
            continue
        b = os.path.basename(p)
        if "_test" in b or b.startswith("test_"):   # 委任_27(2026-10-24): testファイルはProduction到達経路でない(他3つのer110 isolation testと同じ除外)。X/Z側testがY隔離確認のためer110名を文字列で持つ
            continue
        try:
            txt = open(p, encoding="utf-8").read()
        except Exception:
            continue
        if re.search(r"er110_family_y", txt):
            offenders.append(p)
    assert offenders == []


def test_no_env_flag_or_cli_switch_in_module():
    txt = open("er110_family_y_text_trial_01.py", encoding="utf-8").read()
    assert "os.environ" not in txt and "getenv" not in txt


def test_y_comment_roles_have_no_x_part_structure_and_no_comment4():
    for lv in ("b1b", "a2"):
        for role in (y.Y_COMMENT_2_ROLE[lv], y.Y_COMMENT_3_ROLE[lv]):
            assert "第1部" not in role and "第2部" not in role and "第3部" not in role
            assert "Comment 4" not in role
    assert "Comment 4" not in "".join(y.Y_COMMENT_2_ROLE.values()) + "".join(y.Y_COMMENT_3_ROLE.values())


def test_ablation_light_prompt_is_evaluation_only_and_has_no_factlock():
    p = y.build_y_r0_light_prompt("x", "- 【事実1】a", _cards())
    assert "出典タグの規則" not in p and "この人物の中心の論点にしないこと" not in p


def test_acceptance_gate_blocks_non_pass_articles_from_downstream(tmp_path):
    d = tmp_path / "g"
    d.mkdir()
    (d / "article_final.md").write_text(art(), encoding="utf-8")
    with pytest.raises(y.YStop) as e:
        y.load_gated_article_or_stop(str(d))                 # gate_result.jsonなし
    assert e.value.code == "GATE_RESULT_MISSING"
    (d / "gate_result.json").write_text(json.dumps({"status": "LEAKAGE_RESIDUAL_STOP"}), encoding="utf-8")
    with pytest.raises(y.YStop) as e:
        y.load_gated_article_or_stop(str(d))
    assert e.value.code == "ACCEPTANCE_GATE_NOT_PASSED"
    (d / "gate_result.json").write_text(json.dumps({"status": "PASS"}), encoding="utf-8")
    assert y.load_gated_article_or_stop(str(d)).startswith(TITLE)
