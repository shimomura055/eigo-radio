# -*- coding: utf-8 -*-
"""er110_family_y_opinion_based_03 の offline test(API 0)。テーマデータ(再配達)の不変条件・出典IDの実在・属性整合・定義の混入防止・
runnerの一般化(テーマ非依存)・patchの復元・起動ガード・隔離・fake clientでの通しを固定する。"""
import copy
import glob
import json
import os
import re
import subprocess
import sys

import pytest

import er110_family_y_opinion_based_01 as ob
import er110_family_y_opinion_based_02 as ob2
import er110_family_y_opinion_based_03 as ob3
import er110_family_y_persona_pipeline_01 as pl
import er110_family_y_text_trial_01 as y0
from er110_family_y_opinion_based_01_test_01 import Fake

D = "docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02"
VOICES = {v["id"]: v for v in json.load(open(f"{D}/VOICES_02.json", encoding="utf-8"))["voices"]}
SOURCES = json.load(open(f"{D}/VOICES_02.json", encoding="utf-8"))["sources"]
RAW = json.load(open(f"{D}/THEME_DATA_02.json", encoding="utf-8"))


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


def _texts(theme: dict):
    """Sheet・World frameの本文(source_idsなどのID欄は除く)を平らにして返す。"""
    out = []

    def walk(x, key=""):
        if isinstance(x, dict):
            for k, v in x.items():
                if k in ("source_ids", "id", "tbs_only", "kind"):
                    continue
                walk(v, k)
        elif isinstance(x, list):
            for v in x:
                walk(v, key)
        elif isinstance(x, str):
            out.append(x)
    walk(theme["sheets"])
    walk(theme["world_frame"])
    return out


def test_theme_loads_and_validates():
    th = ob3.load_theme()
    assert set(th["sheets"]) == set(ob.SLOTS) and th["theme_id"] == "redelivery_fee"
    for sh in th["sheets"].values():
        assert all("tbs_only" in x for x in sh["experiences"])
        assert len(sh["experiences"]) >= 6
    # ONE: 全項目がR2+/R3の出典(個人ブログ・note)だけが根拠 -> 公開前Gateの確認対象として印が付く
    assert all(x["tbs_only"] for x in th["sheets"]["voice_1"]["experiences"])
    assert not any(x["tbs_only"] for x in th["sheets"]["voice_3"]["experiences"])


def test_validate_theme_rejects_bad_data():
    th = ob3.load_theme()
    bad = copy.deepcopy(th)
    del bad["sheets"]["voice_2"]["stake_ja"]
    with pytest.raises(ValueError, match="MISSING_KEYS"):
        ob3.validate_theme(bad)
    bad = copy.deepcopy(th)
    bad["sheets"]["voice_1"]["opening_type"] = "未定義の型"
    with pytest.raises(ValueError, match="UNKNOWN_OPENING"):
        ob3.validate_theme(bad)
    bad = copy.deepcopy(th)
    bad["sheets"]["voice_3"]["relevant_terms"] = ["未定義の用語"]
    with pytest.raises(ValueError, match="RELEVANT_TERM"):
        ob3.validate_theme(bad)
    bad = copy.deepcopy(th)
    bad["sheets"]["voice_1"]["experiences"][1]["id"] = bad["sheets"]["voice_1"]["experiences"][0]["id"]
    with pytest.raises(ValueError, match="EXPERIENCE_IDS"):
        ob3.validate_theme(bad)


def test_theme_text_has_no_numbers_or_stats():
    """Voice Prompt規則9(数字・漢数字の数量表現を使わない)と整合。IDの数字(RV-55等)は本文に出ない欄なので除外。"""
    th = ob3.load_theme()
    for s in _texts(th):
        assert re.search(r"[0-9０-９]", s) is None, s
        assert y0.NUM_RE.search(s) is None, s
    for s in _texts({"sheets": th["sheets"], "world_frame": {}}):                       # Persona Sheetに統計・調査の言い回しがない(World frameのself_checkの注意書きは除く)
        assert not re.search(r"パーセント|%|％|統計|調査によ|報告書|白書", s), s


def test_source_ids_exist_and_are_personal_voices():
    th = ob3.load_theme()
    used = set()
    for sh in th["sheets"].values():
        for x in sh["experiences"]:
            assert x["source_ids"], x["id"]
            for i in x["source_ids"]:
                assert i in VOICES, (x["id"], i)
                used.add(i)
    assert used <= set(VOICES)
    # 声は『個人の本人発言』だけ。統計・AI回答・記事解説の出典IDは存在しない
    assert all(not v["src"].startswith(("ST", "EX", "AI")) for v in VOICES.values())
    assert set(RAW["restricted_voice_ids"]) <= set(VOICES)
    for rid in RAW["restricted_voice_ids"]:
        assert SOURCES[VOICES[rid]["src"]]["rights"] in ("R2+", "R3"), rid


def test_attributes_match_source_labels():
    """発言者属性を変えない: 各Personaの役割・属性が、根拠にした声の『本人記載』と矛盾しない。"""
    th = ob3.load_theme()
    s1, s2, s3 = (th["sheets"][k] for k in ("voice_1", "voice_2", "voice_3"))
    assert "宅配ドライバー" in s1["role_ja"] and "ドライバー" in VOICES["RV-55"]["who_stated"] and "現役" in VOICES["RV-55"]["who_stated"]
    assert "ドライバー" in VOICES["RV-59"]["who_stated"] or "ドライバー" in VOICES["RV-58"]["who_stated"]
    assert "共働き" in s2["role_ja"] and "仕事" in VOICES["RV-08"]["who_stated"] and "夫婦" in VOICES["RV-08"]["who_stated"]
    assert "受取人" in s3["role_ja"] and "ロッカー" in VOICES["RV-26"]["who_stated"]
    # 性別は出典に記載がない/推定のため、補った表現であることを欄に明記している
    assert "補った" in s1["age_label"] and "補った" in s3["age_label"] and "推定" in s2["age_label"]
    assert s1["gender"] != s2["gender"] and s2["gender"] != s3["gender"]
    # 声ごとに一人称が違う
    assert len({s["speech_style"]["first_person"] for s in th["sheets"].values()}) == 3


def test_stance_basis_matches_persona_claims():
    """Personaの立場の芯が、根拠の声の立場(分類)と整合している。"""
    th = ob3.load_theme()
    # V1: 反対/慎重(請求は筋違い)。立場の根拠 RV-55(反対), RV-56(慎重)
    assert VOICES["RV-55"]["stance"] == "反対" and VOICES["RV-56"]["stance"] == "慎重"
    assert "反対" in th["sheets"]["voice_1"]["claim_core_ja"]
    # V2: 条件付き反対(配達側の運用が先)。RV-08(条件付き反対)+RV-63/64(条件付き反対)
    assert all(VOICES[i]["stance"] == "条件付き反対" for i in ("RV-08", "RV-63", "RV-64"))
    # V3: 賛成系(有料化は賛成、ただし整備が先)。RV-11(条件付き賛成)・RV-40/41/42(賛成)・RV-26(条件付き賛成)
    assert VOICES["RV-11"]["stance"] == "条件付き賛成" and all(VOICES[i]["stance"] == "賛成" for i in ("RV-40", "RV-41", "RV-42"))
    assert "賛成" in th["sheets"]["voice_3"]["claim_core_ja"]
    # 各Personaは、立場の声が3件以上(OF-Y6-02準用)。V1は立場2件+経験の声3件
    for slot, sh in th["sheets"].items():
        ids = {i for x in sh["experiences"] for i in x["source_ids"]}
        assert len(ids) >= 3, (slot, ids)


def test_personas_are_differentiated_and_conflict_is_kept_to_sourced():
    th = ob3.load_theme()
    sh = th["sheets"]
    assert len({sh[s]["opening_type"] for s in sh}) == 3                          # 冒頭の型が3人別々
    assert [t for t in ("具体的な注文", "問い返し", "引け目") if t in sh["voice_1"]["arc_ja"] + sh["voice_2"]["arc_ja"] + sh["voice_3"]["arc_ja"]] == ["具体的な注文", "問い返し", "引け目"]
    assert "具体的な注文" in sh["voice_1"]["arc_ja"] and "問い返し" in sh["voice_2"]["arc_ja"] and "引け目" in sh["voice_3"]["arc_ja"]   # 結びの型が3人別々
    for s in sh.values():
        assert any(k in s["arc_ja"] for k in ("解消しない", "言い切って結ばない", "決めきれない"))
        assert "新しい場面" in s["identity_cue_ja"]                                  # 出来事を足さない指示を維持


def test_definitions_do_not_leak_into_personas():
    """前回run_03の教訓: 世界設定の定義文が、Personaの意見として混入していない。relevant_termsは定義にある用語だけ。"""
    th = ob3.load_theme()
    defs = {d["term_ja"]: d["definition_ja"] for d in th["world_frame"]["distinctions"]}
    persona_text = "\n".join(_texts({"sheets": th["sheets"], "world_frame": {}}))
    for term, dfn in defs.items():
        core = dfn.rstrip("。")
        assert core not in persona_text, term
    for slot, sh in th["sheets"].items():
        assert set(sh["relevant_terms"]) <= set(defs), slot
    assert th["sheets"]["voice_1"]["relevant_terms"] != th["sheets"]["voice_3"]["relevant_terms"]


def test_world_frame_valid_and_theme_scoped():
    wf = ob3.load_theme()["world_frame"]
    assert wf["status_quo"] == [] and "再配達" in wf["question_ja"]
    assert "物流業界全体" in wf["shared_premise_ja"] and "中心にしない" in wf["shared_premise_ja"]            # 拡散させない(ユーザー原文§3)
    assert len(wf["distinctions"]) == 5


def test_theme_file_matches_generator():
    sys.path.insert(0, f"{D}/scripts")
    import build_theme_data_02 as g
    assert json.loads(json.dumps(g.THEME, ensure_ascii=False)) == RAW


def test_runner_code_has_no_theme_specific_words():
    """一般化の証明: runner(03)のコードとPromptにテーマ固有の語がない(テーマ固有情報はデータ側)。"""
    src = open("er110_family_y_opinion_based_03.py", encoding="utf-8").read()
    code = re.sub(r'""".*?"""', "", src, flags=re.S)
    for w in ("再配達", "宅配", "配達員", "置き配", "ロッカー", "営業所", "有料化", "ドライバー"):
        assert w not in code, w
    assert "os.environ" not in src and "getenv" not in src and "argparse" not in src and "OpenAI(" not in src
    # Promptは02のものをそのまま使う(本moduleで文面を作らない)
    assert "VOICE_PROMPT_OB2" in src and "THINK_BLOCK" not in src


def test_patch_restores_01_globals():
    th = ob3.load_theme()
    saved = {k: getattr(ob, k) for k in ob2._PATCH_KEYS}
    with ob3.patched_ob_03(11.0, th):
        assert ob.SHEETS is th["sheets"] and ob.BUDGET_STOP_JPY == 11.0 and ob.WHO_JA is th["who_ja"] and ob.VOICE_PROMPT_OB is ob2.VOICE_PROMPT_OB2
        p = ob.build_voice_prompt_ob(th["world_frame"], "voice_1")
        assert "【語る前の考え方" in p and "人物像(最初にここを踏まえる)" in p
        assert "- 再配達:" in p and "- 時間帯指定:" in p and "- 宅配ボックス:" not in p and "- 有料化:" not in p     # relevant_termsだけ渡す
        p3 = ob.build_voice_prompt_ob(th["world_frame"], "voice_3")
        assert "- 宅配ボックス:" in p3 and "- 有料化:" in p3 and "- 時間帯指定:" not in p3
    for k, v in saved.items():
        assert getattr(ob, k) is v, k
    assert ob.SHEETS["voice_1"]["role_ja"].startswith("小さい子ども")            # withを抜けたら01(SNSテーマ)に戻る


def test_prompts_carry_no_cross_voice_content():
    th = ob3.load_theme()
    with ob3.patched_ob_03(11.0, th):
        ps = {s: ob.build_voice_prompt_ob(th["world_frame"], s) for s in ob.SLOTS}
    assert "[ONE_a]" in ps["voice_1"] and "[TWO_a]" not in ps["voice_1"] and "[THREE_a]" not in ps["voice_1"]
    assert "[TWO_a]" in ps["voice_2"] and "[ONE_a]" not in ps["voice_2"]
    assert "[THREE_a]" in ps["voice_3"] and "[ONE_a]" not in ps["voice_3"]
    for s, p in ps.items():
        assert "RV-" not in p and "出典" in p                       # 声IDはPromptに出ない(IDはSheet内の英字ID)


def test_happy_path_with_fake_and_restore(fake_env):
    rd, led = fake_env
    fake = Fake()
    st = ob3.run_pipeline_03(fake, rd, cap_jpy=27.0, ledger_md=led)
    assert st["gate_status"] == "PASS" and set(st["repetition_03"]) == set(ob.SLOTS)
    assert os.path.exists(f"{rd}/repetition_report_03.json") and os.path.exists(f"{rd}/article_ja.md")
    gens = [x for x in fake.prompts if "一人称の語りを1段落だけ" in x]
    assert len(gens) == 3 and all("【語る前の考え方" in g for g in gens)
    assert any("営業所やロッカーでの受け取りを選ぶ" in g for g in gens) and any("夜の配達" in g for g in gens)     # 再配達テーマのSheetが渡っている
    assert not any("年齢による制限" in g for g in gens)                                       # SNSテーマの語が混入していない
    assert ob.SHEETS["voice_3"]["age_label"].startswith("中学生")                           # with を抜けたら 01 に戻る


def test_budget_cap_applied_from_argument(fake_env):
    rd, led = fake_env
    with pytest.raises(pl.PipelineStop):
        ob3.run_pipeline_03(Fake(), rd, cap_jpy=0.2, ledger_md=led)


def test_main_requires_paid_flag_budget_approval_run_name_valid_theme_and_refuses_relaunch(tmp_path, monkeypatch):
    import er003_v1_en_direct_vfl_01_generate as vfl01
    calls = []
    monkeypatch.setattr(vfl01, "get_client", lambda *a, **k: calls.append("get_client"))
    monkeypatch.setattr(ob3, "run_pipeline_03", lambda *a, **k: calls.append("run_pipeline_03"))
    monkeypatch.setattr(ob3, "APPROVAL_FILE_03", str(tmp_path / "none.json"))
    monkeypatch.setattr(ob3, "RUN_DIRS_03", {"run_01": str(tmp_path / "rd_a"), "run_02": str(tmp_path / "rd_b")})
    assert ob3.main("run_01") == 8 and not os.path.exists(tmp_path / "rd_a")           # --paid が無ければ起動しない(承認の有無に関係なくAPI 0・ファイル0)
    assert ob3.main(None) == 7 and ob3.main("run_03") == 7 and ob3.main("../x") == 7
    assert ob3.main("run_01", paid=True) == 6 and not os.path.exists(tmp_path / "rd_a")  # 承認ファイルが無ければ --paid でも起動しない
    (tmp_path / "ok.json").write_text('{"cap_jpy": 30}', encoding="utf-8")
    monkeypatch.setattr(ob3, "APPROVAL_FILE_03", str(tmp_path / "ok.json"))
    assert ob3.main("run_01") == 8 and ob3.main("run_02") == 8
    # 承認+--paid でも、テーマデータが不正なら有料run前に止まる(rc=9、dirも作らない)
    monkeypatch.setattr(ob3, "THEME_FILE", str(tmp_path / "bad_theme.json"))
    (tmp_path / "bad_theme.json").write_text(json.dumps({"theme_id": "x", "world_frame": {"distinctions": []}, "sheets": {}, "who_ja": {}}), encoding="utf-8")
    assert ob3.main("run_01", paid=True) == 9 and not os.path.exists(tmp_path / "rd_a")
    assert calls == []                                                                  # API/network入口は一度も呼ばれない
    assert ob3.read_cap(str(tmp_path / "none.json")) is None and ob3.read_cap(str(tmp_path / "ok.json")) == 30.0
    (tmp_path / "ok2.json").write_text('{"cap_jpy": 60, "runs": 2}', encoding="utf-8")
    assert ob3.read_cap(str(tmp_path / "ok2.json")) == 30.0
    rd = tmp_path / "rd_a"
    rd.mkdir()
    (rd / "entry_point.json").write_text("{}", encoding="utf-8")
    assert ob3.main("run_01", paid=True) == 5 and calls == []                           # 起動済みrunは再起動不可


def test_no_approval_file_created_and_run_dirs_inside_er110_output():
    assert not os.path.exists(ob3.APPROVAL_FILE_03), "本委任では有料run承認ファイルを作らない(次委任でFableの委任文を根拠に作成)"
    for rd in ob3.RUN_DIRS_03.values():
        assert rd.startswith("er110_output/") and "er011_output" not in rd and not os.path.exists(rd)


def test_isolation_no_importer_and_api_zero_on_import():
    me = {"er110_family_y_opinion_based_03.py", "er110_family_y_opinion_based_03_test_01.py"}
    bad = []
    for f in glob.glob("*.py") + glob.glob("**/*.py", recursive=True):
        if os.path.basename(f) in me or ".venv" in f or "OPINION_BASED_01" in f:
            continue
        try:
            src = open(f, encoding="utf-8").read()
        except Exception:
            continue
        if re.search(r"^\s*(?:import|from)\s+er110_family_y_opinion_based_03\b", src, re.M):
            bad.append(f)
    assert bad == [], bad


def test_import_has_no_side_effect(tmp_path):
    repo = os.getcwd()
    out = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, sys.argv[1]); import er110_family_y_opinion_based_03 as o, er110_family_y_opinion_based_01 as b; "
                          "print(b.BUDGET_STOP_JPY, b.SHEETS['voice_3']['age_label'][:3])", repo],
                         capture_output=True, text=True, encoding="utf-8", cwd=str(tmp_path), env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    assert out.stdout.strip() == "27.0 中学生", out.stdout + out.stderr
    assert os.listdir(tmp_path) == []


def test_01_02_and_existing_modules_unchanged():
    out = subprocess.run(["git", "diff", "--name-only", "HEAD", "--", "er110_family_y_opinion_based_01.py", "er110_family_y_opinion_based_02.py", "er110_family_y_text_trial_01.py",
                          "er110_family_y_persona_text_trial_01.py", "er110_family_y_persona_pipeline_01.py"], capture_output=True, text=True).stdout.strip()
    assert out == "", out


def test_docs_reference_only_existing_voice_ids():
    pat = re.compile(r"RV-(\d\d)")
    for f in ("SOURCE_LOG_02.md", "AXIS_ANALYSIS_03.md", "PERSONAS_05.md", "PROVENANCE_PLAN_05.md"):
        p = f"{D}/{f}"
        if not os.path.exists(p):
            continue
        for m in pat.findall(open(p, encoding="utf-8").read()):
            assert f"RV-{m}" in VOICES, (f, m)


def test_voices_quotes_exist_in_saved_sources_if_present():
    """逐語抜粋が、保存した出典本文(sources/、git管理外)に実在する。ファイルが無い環境ではskip。"""
    if not glob.glob(f"{D}/sources/pages/*.txt"):
        pytest.skip("sources/ is untracked and not present in this checkout")
    out = subprocess.run([sys.executable, f"{D}/scripts/verify_voices_02.py"], capture_output=True, text=True, encoding="utf-8", env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    assert out.returncode == 0, out.stdout + out.stderr


def test_voice_catalog_invariants():
    assert len(VOICES) >= 30
    for v in VOICES.values():
        assert v["quotes"] and v["summary"] and v["src"] in SOURCES
        assert v["stance"] in ("賛成", "条件付き賛成", "条件付き反対", "反対", "慎重", "不明")
        assert not re.search(r"@|ID[:：]|ユーザー名", v["who_stated"])             # ハンドル名・IDを保存しない
    assert not any("AI" in v["who_stated"] and "回答" in v["who_stated"] and "お助け" in v["who_stated"] for v in VOICES.values())
