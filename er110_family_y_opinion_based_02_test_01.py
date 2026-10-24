# -*- coding: utf-8 -*-
"""er110_family_y_opinion_based_02 の offline test(API 0)。Prompt改訂・Sheet不変条件・反復検出・patchの復元・予算承認ゲート・隔離・fake clientでの通し。"""
import glob
import json
import os
import re
import subprocess
import sys

import pytest

import er110_family_y_opinion_based_01 as ob
import er110_family_y_opinion_based_02 as ob2
import er110_family_y_persona_pipeline_01 as pl
from er110_family_y_opinion_based_01_test_01 import Fake

RUN01_ONE = ("うちの小さい子が、刺激の強いものや課金のあるものを、興味のままに選んでしまったことがある。話をすると、じゃあやらない、となることも多い。"
             "だから、親が話すだけじゃなくて、SNSには年齢に応じた使い方の決まりがあってほしい。はっきりしているほうが、私は安心できる。"
             "ただ、長い移動で静かにしてほしい時、動画を見てくれると助かるんだ。正直、助かっている。制限がかかると、私もしんどい時がある。"
             "子どものために制限してほしいと思っているけど、いや、私の都合では見ていてほしい時もある。"
             "それでも、小さいうちは、SNSの使い方にはっきりした決まりがあってほしいと思う。")


@pytest.fixture
def fake_env(tmp_path, monkeypatch):
    st = {"cost": 0.0}
    monkeypatch.setattr(ob, "cost_jpy", lambda rd: round(st["cost"], 3))
    monkeypatch.setattr(ob, "stage_costs", lambda rd: {"fake_total": round(st["cost"], 3)})
    orig = pl.y0.chat

    def chat(client, **kw):
        st["cost"] += 0.5
        return orig(client, **kw)
    monkeypatch.setattr(pl.y0, "chat", chat)
    return str(tmp_path / "run"), str(tmp_path / "ledger.md")


def test_prompt_adds_think_block_and_keeps_source_rules():
    t = ob2.VOICE_PROMPT_OB2
    assert "【語る前の考え方(出力には書かない)】" in t and "先に「人物像」を確かめる" in t and "一般論を並べない" in t
    assert "新しい事実・気持ち・向きのどれかを足している" in t and "回数で数えるのではなく" in t
    assert t.index("【語る前の考え方") < t.index("【語りの作り方(厳守)】")
    assert ob2._RULE3_OLD not in t and ob2._RULE3_NEW in t
    for kept in ("(IDつき)にある内容だけ", "出来事を作らず、仮定", "人物・会話・出来事・場所・物の追加はしない", "約260〜300字", "「です・ます」調にしない", "括弧・コロン・スラッシュ", "自己紹介の文は書かない"):
        assert kept in t
    assert "成人" not in t
    assert "「この前」「ある子が」「友達が」「先生が」のように、欄にない人物や出来事を新しく作らない" in t


def test_prompt_base_change_is_detected():
    with pytest.raises(ValueError):
        ob2._must_replace("x", "ない文言", "y")


def test_build_prompt_with_patch_wires_everything():
    with ob2.patched_ob(10.0):
        for s in ob.SLOTS:
            pr = ob.build_voice_prompt_ob(ob2.WORLD_FRAME_02, s)
            assert "@@" not in pr and "人物像(最初にここを踏まえる)" in pr and "語りの流れ(目安" in pr
            assert pr.index("人物像(最初にここを踏まえる)") < pr.index("経験・意見(ここにある内容だけ") < pr.index("この人が言いたいことの芯")     # 人物 -> 経験 -> 主張の順
            assert "MR-T" not in pr and "TBS-" not in pr and "成人" not in pr and "歳" not in pr
            assert ob2.SHEETS_02[s]["opening_type"] in pr and ob2.OPENING_GUIDE_02[ob2.SHEETS_02[s]["opening_type"]] in pr
        assert "段階的な制限" in ob.build_voice_prompt_ob(ob2.WORLD_FRAME_02, "voice_3") and "中心の話題にしない" in ob.build_voice_prompt_ob(ob2.WORLD_FRAME_02, "voice_1")


def test_patch_restores_01_globals():
    before = {k: getattr(ob, k) for k in ob2._PATCH_KEYS}
    with ob2.patched_ob(7.0):
        assert ob.SHEETS is ob2.SHEETS_02 and ob.BUDGET_STOP_JPY == 7.0
    after = {k: getattr(ob, k) for k in ob2._PATCH_KEYS}
    assert before == after and ob.BUDGET_STOP_JPY == 27.0 and ob.SHEETS["voice_3"]["age_label"].startswith("中学生")
    with pytest.raises(RuntimeError):
        with ob2.patched_ob(7.0):
            raise RuntimeError("x")
    assert ob.SHEETS is not ob2.SHEETS_02


def test_sheet_invariants_02():
    S = ob2.SHEETS_02
    ops = [S[s]["opening_type"] for s in ob.SLOTS]
    assert len(set(ops)) == 3 and all(o in pl.OPENING_TYPES for o in ops) and all(o in ob2.OPENING_GUIDE_02 for o in ops)
    assert sum(1 for o in ops if o == "言い訳・弁明から") <= 1
    assert any(S[s]["contradiction_or_weakness_ja"].startswith("なし") for s in ob.SLOTS)          # OF-Y6-03 維持
    assert len({S[s]["speech_style"]["first_person"] for s in ob.SLOTS}) == 3
    ids = [x["id"] for s in ob.SLOTS for x in S[s]["experiences"]]
    assert len(ids) == len(set(ids)) and all(re.fullmatch(r"[A-Za-z_]+", i) for i in ids)
    for s in ob.SLOTS:
        for k in ("persona_sketch_ja", "stake_ja", "arc_ja", "claim_core_ja", "entry_mood_ja"):
            assert S[s][k]
        for x in S[s]["experiences"]:
            assert not re.search(r"[0-9０-９]", x["text_ja"]) and "MR-" not in x["text_ja"] and "TBS" not in x["text_ja"], x["id"]
        assert len([x for x in S[s]["experiences"] if not x["tbs_only"]]) >= 3
    assert not any(x["tbs_only"] for x in S["voice_2"]["experiences"]) and not any(x["tbs_only"] for x in S["voice_3"]["experiences"])     # TBSのみ根拠はV1のONE_dだけ
    assert [x["id"] for x in S["voice_1"]["experiences"] if x["tbs_only"]] == ["ONE_d"] and "一文だけで触れ" in [x for x in S["voice_1"]["experiences"] if x["id"] == "ONE_d"][0]["text_ja"]
    assert all(x["kind"] == "O" for x in S["voice_3"]["experiences"])                              # V3は出来事を作らない
    assert "MR-T010-17" not in [i for s in ob.SLOTS for x in S[s]["experiences"] for i in x["source_ids"]]


def _fields(sheet):
    return {k: json.dumps(v, ensure_ascii=False) for k, v in sheet.items() if k not in ("experiences",)}


def test_of_y7_01_tbs07_content_only_in_oned_and_contradiction():
    v1 = ob2.SHEETS_02["voice_1"]
    hits = [k for k, v in _fields(v1).items() if re.search(r"助けられ|助かっ|しんどい", v)]
    assert hits == ["contradiction_or_weakness_ja"], hits                      # experiences側のONE_dと合わせて2か所だけ
    hits_ex = [x["id"] for x in v1["experiences"] if re.search(r"助かる|しんどい", x["text_ja"])]
    assert hits_ex == ["ONE_d"]
    v3 = ob2.SHEETS_02["voice_3"]
    hits3 = [k for k, v in _fields(v3).items() if "全部禁止" in v or "全部解禁" in v]
    assert hits3 == ["values_ja"] and "補った整理" in v3["values_ja"], hits3
    assert not any("全部禁止" in x["text_ja"] or "全部解禁" in x["text_ja"] for x in v3["experiences"])


def test_of_y7_02_v1_source_shift_removed():
    v1 = ob2.SHEETS_02["voice_1"]
    assert "ONE_e" not in [x["id"] for x in v1["experiences"]] and "MR-T015-10" not in [i for x in v1["experiences"] for i in x["source_ids"]]
    blob = json.dumps(v1, ensure_ascii=False)
    assert "例外ではない" not in blob and "安心" not in blob and "大人でもやめられない" not in blob


def test_of_y7_03_04_v2_no_unsourced_and_no_nonsequitur():
    v2 = ob2.SHEETS_02["voice_2"]
    blob = json.dumps(v2, ensure_ascii=False)
    assert "未成年だから" not in blob and "MR-T041-03" not in blob and "かといって" not in blob and "仕方がない" not in blob
    assert "安全フィルター" in v2["wishes_public_ja"] or "別の対策" in v2["wishes_public_ja"]
    assert "自分で判断" in v2["contradiction_or_weakness_ja"] and "大人に頼" in v2["contradiction_or_weakness_ja"]
    f = [x for x in v2["experiences"] if x["id"] == "TWO_f"][0]
    assert "任意" in f["text_ja"] and f["text_ja"].count("見られる") == 1          # 監視は理由として1か所・任意
    assert "かといって" not in json.dumps(ob2.SHEETS_02["voice_3"], ensure_ascii=False)


def test_of_y7_05_closing_types_differ_and_v3_hypothetical():
    S = ob2.SHEETS_02
    assert "抱えたまま" in S["voice_1"]["arc_ja"] and "注文" in S["voice_2"]["arc_ja"] and "たとえ" in S["voice_3"]["arc_ja"] and "心配の像" in S["voice_3"]["arc_ja"]
    assert "仮定" in S["voice_3"]["arc_ja"] and "うちの子" in S["voice_3"]["arc_ja"] and "うちの子" in S["voice_3"]["identity_cue_ja"] and "出来事は足さない" in S["voice_3"]["arc_ja"]


def test_v3_voice_is_male_and_distinct_from_v2():
    S = ob2.SHEETS_02
    assert S["voice_3"]["gender"] == "男性" and S["voice_2"]["gender"] == "男性" and S["voice_1"]["gender"] == "女性"
    assert len({S[s]["speech_style"]["first_person"] for s in ob.SLOTS}) == 3


def test_attributes_match_source_labels():
    """発言者属性を変えない: V3の出典はすべて『中学生の保護者』、V2は『高校生』ラベルのMR(sources/が手元にある場合のみ原文で確認)。"""
    p = "docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_01/sources/mirai_topics/_ops_v2.json"
    if not os.path.exists(p):
        pytest.skip("sources/ はgit管理外")
    d = {e["id"]: e for e in json.load(open(p, encoding="utf-8"))}
    for x in ob2.SHEETS_02["voice_3"]["experiences"]:
        for i in x["source_ids"]:
            assert "中学生" in d[i]["attr"] and "保護者" in d[i]["attr"], (x["id"], i, d[i]["attr"])
    for x in ob2.SHEETS_02["voice_2"]["experiences"]:
        for i in x["source_ids"]:
            assert "高校生" in d[i]["attr"] and "保護者" not in d[i]["attr"], (x["id"], i, d[i]["attr"])


def test_repetition_report_flags_run01_one_voice_and_not_clean_text():
    r = ob2.repetition_report(RUN01_ONE)
    assert r["n_repeat_pairs"] >= 2 and r["contrast_turns"] >= 3 and "記録専用" in r["note"]
    clean = "うちの子は、動画をよく見る。私は、見守りの設定が面倒だと感じている。使える時間を決めても、終わるとむくれる。そんな日は、少し疲れる。"
    assert ob2.repetition_report(clean)["n_repeat_pairs"] == 0


def test_world_frame_02_valid():
    wf = ob2.WORLD_FRAME_02
    assert wf["status_quo"] == [] and re.search(r"[0-9０-９]", json.dumps(wf, ensure_ascii=False)) is None
    assert ob.WORLD_FRAME["shared_premise_ja"] != wf["shared_premise_ja"]            # 01側は無変更
    assert len(ob.WORLD_FRAME["distinctions"]) == 3 and len(wf["distinctions"]) == 4


def test_happy_path_with_fake_and_restore(fake_env):
    rd, led = fake_env
    fake = Fake()
    st = ob2.run_pipeline_02(fake, rd, cap_jpy=27.0, ledger_md=led)
    assert st["gate_status"] == "PASS" and set(st["repetition_02"]) == set(ob.SLOTS)
    assert os.path.exists(f"{rd}/repetition_report_02.json") and os.path.exists(f"{rd}/article_ja.md")
    gens = [x for x in fake.prompts if "一人称の語りを1段落だけ" in x]
    assert len(gens) == 3 and all("【語る前の考え方" in g and "人物像(最初にここを踏まえる)" in g for g in gens)
    assert ob.SHEETS["voice_3"]["age_label"].startswith("中学生")            # with を抜けたら 01 に戻る


def test_budget_cap_applied_from_argument(fake_env):
    rd, led = fake_env
    with pytest.raises(pl.PipelineStop):
        ob2.run_pipeline_02(Fake(), rd, cap_jpy=0.2, ledger_md=led)           # 1call(0.5)で到達 -> 次の呼出前に止まる


def test_main_requires_paid_flag_budget_approval_run_name_and_refuses_relaunch(tmp_path, monkeypatch):
    import er003_v1_en_direct_vfl_01_generate as vfl01
    calls = []
    monkeypatch.setattr(vfl01, "get_client", lambda *a, **k: calls.append("get_client"))            # network/API入口。呼ばれたら記録
    monkeypatch.setattr(ob2, "run_pipeline_02", lambda *a, **k: calls.append("run_pipeline_02"))
    monkeypatch.setattr(ob2, "APPROVAL_FILE", str(tmp_path / "none.json"))
    monkeypatch.setattr(ob2, "RUN_DIRS_02", {"run_02a": str(tmp_path / "rd_a"), "run_02b": str(tmp_path / "rd_b"), "run_03": str(tmp_path / "rd_c")})
    assert ob2.main("run_02a") == 8 and not os.path.exists(tmp_path / "rd_a")           # --paid が無ければ起動しない(承認の有無に関係なくAPI 0・ファイル0)
    assert ob2.main(None) == 7 and ob2.main("run_01") == 7 and ob2.main("../x") == 7      # run名は許可リストのみ
    (tmp_path / "ok.json").write_text('{"cap_jpy": 30}', encoding="utf-8")
    monkeypatch.setattr(ob2, "APPROVAL_FILE", str(tmp_path / "ok.json"))                  # 承認ファイルがあっても --paid が無ければ起動しない
    assert ob2.main("run_03") == 8 and ob2.main("run_02b") == 8 and not os.path.exists(tmp_path / "rd_c")
    assert calls == []                                                                     # testはpaid=Trueを与えない。API/network入口は一度も呼ばれない
    (tmp_path / "bad.json").write_text('{"cap_jpy": 0}', encoding="utf-8")
    assert ob2.read_cap(str(tmp_path / "bad.json")) is None and ob2.read_cap(str(tmp_path / "none.json")) is None
    assert ob2.read_cap(str(tmp_path / "ok.json")) == 30.0
    (tmp_path / "ok2.json").write_text('{"cap_jpy": 45, "runs": 2}', encoding="utf-8")
    assert ob2.read_cap(str(tmp_path / "ok2.json")) == 22.5
    rd = tmp_path / "rd_a"
    rd.mkdir()
    (rd / "entry_point.json").write_text("{}", encoding="utf-8")
    assert ob2.main("run_02a") == 5 and calls == []                                        # 起動済みrunは再起動不可


def test_cli_guard_source_fixed():
    src = open("er110_family_y_opinion_based_02.py", encoding="utf-8").read()
    assert '"--paid" in _args' in src and "paid: bool = False" in src and "if not paid:" in src
    assert src.index("if not paid:") < src.index("cap = read_cap()")               # 承認ファイル読取・client生成より前に止める


def test_run03_definition_leak_countermeasure():
    t = ob2.VOICE_PROMPT_OB2
    assert "D. 【区別の定義】は、用語の意味を取り違えないための前提であり、語る中身ではない" in t and "同じたとえや言い回しは、一度使ったら語りの中で繰り返さない" in t
    with ob2.patched_ob(10.0):
        p1 = ob.build_voice_prompt_ob(ob2.WORLD_FRAME_02, "voice_1")
        p2 = ob.build_voice_prompt_ob(ob2.WORLD_FRAME_02, "voice_2")
        p3 = ob.build_voice_prompt_ob(ob2.WORLD_FRAME_02, "voice_3")
    assert "段階的な制限:" not in p1 and "利用禁止:" not in p1 and "年齢による制限:" in p1        # V1には段階的な制限の定義を渡さない
    assert "利用禁止:" in p2 and "段階的な制限:" not in p2
    assert "段階的な制限:" in p3
    assert ob.build_voice_prompt_ob is not ob2.build_voice_prompt_02                             # with を抜けたら元に戻る


def test_run03_dirs_inside_er110_output_only():
    for k, v in ob2.RUN_DIRS_02.items():
        assert v.startswith("er110_output/"), (k, v)
    assert "er011_output" not in open("er110_family_y_opinion_based_02.py", encoding="utf-8").read()


def test_approval_file_if_present_is_recorded_decision():
    if not os.path.exists(ob2.APPROVAL_FILE):
        return
    d = json.load(open(ob2.APPROVAL_FILE, encoding="utf-8"))
    assert d["approved_by"] and d["cap_jpy"] <= 45 and d["runs"] in (1, 2)


def test_isolation_no_importer_and_api_zero_on_import():
    me = {"er110_family_y_opinion_based_02.py", "er110_family_y_opinion_based_02_test_01.py"}
    bad = []
    for f in glob.glob("*.py") + glob.glob("**/*.py", recursive=True):
        if os.path.basename(f) in me or ".venv" in f or "OPINION_BASED_01" in f:
            continue
        try:
            src = open(f, encoding="utf-8").read()
        except Exception:
            continue
        if re.search(r"^\s*(?:import|from)\s+er110_family_y_opinion_based_02\b", src, re.M):
            bad.append(f)
    assert bad == [], bad
    src = open("er110_family_y_opinion_based_02.py", encoding="utf-8").read()
    assert "os.environ" not in src and "getenv" not in src and "argparse" not in src and "OpenAI(" not in src


def test_import_has_no_side_effect(tmp_path):
    repo = os.getcwd()
    out = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, sys.argv[1]); import er110_family_y_opinion_based_02 as o, er110_family_y_opinion_based_01 as b; "
                          "print(b.BUDGET_STOP_JPY, b.SHEETS['voice_3']['age_label'][:3])", repo],
                         capture_output=True, text=True, encoding="utf-8", cwd=str(tmp_path), env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    assert out.stdout.strip() == "27.0 中学生", out.stdout + out.stderr
    assert os.listdir(tmp_path) == []                       # import時にファイルを作らない(cwdで確認。run dirは相対pathなのでrepo側にも作られない)


def test_01_and_existing_modules_unchanged():
    out = subprocess.run(["git", "diff", "--name-only", "HEAD", "--", "er110_family_y_opinion_based_01.py", "er110_family_y_text_trial_01.py",
                          "er110_family_y_persona_text_trial_01.py", "er110_family_y_persona_pipeline_01.py"], capture_output=True, text=True).stdout.strip()
    assert out == "", out


def test_open493_local_rewrite_recovery_redirected_under_er110(tmp_path, monkeypatch):
    """Y音声段は共通moduleが固定する er011_output 出力先を、er110_output配下へ付け替える(API 0)。"""
    import er020_tts_retry_local_rewrite_01 as rp
    import er110_family_y_audio_trial_01 as ya
    import er110_family_y_persona_audio_trial_01 as pa
    seen = []
    monkeypatch.setattr(rp, "run_local_rewrite_recovery", lambda *a, **kw: seen.append(kw.get("out_dir")) or {"status": "X"})
    orig = rp.run_local_rewrite_recovery
    with ya.local_rewrite_recovery_under_er110(pa.OUT_ROOT):
        rp.run_local_rewrite_recovery(segment_id="s", out_dir="er011_output/local_rewrite_recovery/t/a2")
        rp.run_local_rewrite_recovery(segment_id="s", out_dir="er110_output/x/y")        # 既にer110配下ならそのまま
    assert seen[0] == f"{pa.OUT_ROOT}/local_rewrite_recovery/t/a2" and seen[0].startswith("er110_output/") and seen[1] == "er110_output/x/y"
    assert rp.run_local_rewrite_recovery is orig                                          # with を抜けたら復元
    for f in ("er110_family_y_audio_trial_01.py", "er110_family_y_persona_audio_trial_01.py"):
        src = open(f, encoding="utf-8").read()
        assert "with local_rewrite_recovery_under_er110" in src or "with old.local_rewrite_recovery_under_er110" in src
