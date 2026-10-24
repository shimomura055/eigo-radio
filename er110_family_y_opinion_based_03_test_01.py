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
                if k in ("source_ids", "id", "tbs_only", "r2plus_only", "kind"):
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
        assert all("r2plus_only" in x and "tbs_only" not in x for x in sh["experiences"])     # 印は r2plus_only に改名(OF-Y8-05)。tbs_onlyは03のthemeに存在しない
        assert len(sh["experiences"]) >= 6
    # V1: ONE_g(RV-29[R2]を含む集約)以外はR2+/R3の出典(個人ブログ・note)だけが根拠 -> 公開前Gateの確認対象として印が付く
    assert [x["id"] for x in th["sheets"]["voice_1"]["experiences"] if not x["r2plus_only"]] == ["ONE_g"]
    assert not any(x["r2plus_only"] for x in th["sheets"]["voice_3"]["experiences"])


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
    # V1(留保型, OF-Y8-02): 立場の根拠 RV-55(反対)・RV-56(慎重)・RV-29(慎重)・RV-59(有料化の賛否は述べず客を責めない態度)。Sheetの項目に実際に結びつく
    assert VOICES["RV-55"]["stance"] == "反対" and VOICES["RV-56"]["stance"] == "慎重" and VOICES["RV-29"]["stance"] == "慎重"
    c1 = th["sheets"]["voice_1"]
    assert "片づく話ではなく" in c1["claim_core_ja"] and "きついのは本当" in c1["claim_core_ja"]
    used1 = {i for x in c1["experiences"] for i in x["source_ids"]}
    assert {"RV-55", "RV-56", "RV-59", "RV-29"} <= used1
    g = [x for x in c1["experiences"] if x["id"] == "ONE_g"][0]
    assert g["source_ids"] == ["RV-55", "RV-29"]
    assert "減ってくれたら" in c1["contradiction_or_weakness_ja"]                       # 矛盾欄はRV-55原文の願い(同じ本人の葛藤)
    # V2: 条件付き反対(配達側の運用が先)。RV-08・RV-63(条件付き反対)。RV-64(最初は無料)はV3のTHREE_hと重複するためV2から外した(OF-Y8-04)
    assert all(VOICES[i]["stance"] == "条件付き反対" for i in ("RV-08", "RV-63"))
    assert "RV-64" not in {i for x in th["sheets"]["voice_2"]["experiences"] for i in x["source_ids"]}
    # V3(明確な賛成, OF-Y8-03): RV-40/41/42/46は賛成、RV-11は条件付き賛成。芯に『整備が先』を持たない
    assert VOICES["RV-11"]["stance"] == "条件付き賛成" and all(VOICES[i]["stance"] == "賛成" for i in ("RV-40", "RV-41", "RV-42", "RV-46"))
    c3 = th["sheets"]["voice_3"]
    assert "有料でいい" in c3["claim_core_ja"] and "整備" not in c3["claim_core_ja"] + c3["persona_sketch_ja"] + c3["arc_ja"]
    assert not any(x["id"] == "THREE_f" for x in c3["experiences"]) and not any("整備" in x["text_ja"] or "整えない" in x["text_ja"] for x in c3["experiences"])
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
        # 01は旧名 tbs_only を読むため、with内の写しにだけ別名を付ける(themeそのものには付けない)
        assert all(x["tbs_only"] == x["r2plus_only"] for sh in ob.SHEETS.values() for x in sh["experiences"]) and not any("tbs_only" in x for sh in th["sheets"].values() for x in sh["experiences"])
        assert {s: {k: v for k, v in sh.items() if k != "experiences"} for s, sh in ob.SHEETS.items()} == {s: {k: v for k, v in sh.items() if k != "experiences"} for s, sh in th["sheets"].items()}
        assert [[{k: v for k, v in x.items() if k != "tbs_only"} for x in sh["experiences"]] for sh in ob.SHEETS.values()] == [sh["experiences"] for sh in th["sheets"].values()]
        assert ob.BUDGET_STOP_JPY == 11.0 and ob.WHO_JA is th["who_ja"] and ob.VOICE_PROMPT_OB is ob2.VOICE_PROMPT_OB2
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


def test_approval_file_matches_delegation_and_run_dirs_inside_er110_output():
    """委任_25でR0(run_01)を1回だけ起動する承認ファイルを作成した(cap_jpy=30, runs=1)。run_02は未起動(承認なしでは起動しない)。"""
    d = json.load(open(ob3.APPROVAL_FILE_03, encoding="utf-8"))
    assert d["cap_jpy"] == 30 and d["runs"] == 1 and ob3.read_cap() == 30.0
    for rd in ob3.RUN_DIRS_03.values():
        assert rd.startswith("er110_output/") and "er011_output" not in rd
    assert not os.path.exists(ob3.RUN_DIRS_03["run_02"])
    assert os.path.exists(os.path.join(ob3.RUN_DIRS_03["run_01"], "entry_point.json"))                   # 起動済み = 再起動不可(mainが5を返す)
    assert ob3.main("run_01", paid=True) == 5


def test_isolation_no_importer_and_api_zero_on_import():
    me = {"er110_family_y_opinion_based_03.py", "er110_family_y_opinion_based_03_test_01.py"}
    bad = []
    for f in glob.glob("*.py") + glob.glob("**/*.py", recursive=True):
        if os.path.basename(f) in me or ".venv" in f or "OPINION_BASED_01" in f or "OPINION_BASED_02/scripts" in f.replace(os.sep, "/"):        # docs配下の解析script(aggregate_04等)はAPI 0のoffline集計
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


# ---- 委任_25: OF-Y8-01〜05 の追加test(API 0) ----
QTY_RE = re.compile(r"[一二三四五六七八九十百千万]+(?:軒|回|度目?|人|つ|か所|ヶ所|件|台|個|枚|杯|本|匹|番目|割)")
PAREN_RE = re.compile(r"[(（][^)）]*[)）]")


def _narrative_texts(theme: dict):
    """Persona本文のうち、モデルへの指示のメタ記述(括弧内)を除いた文。arc_ja(手順の指示)も除く。"""
    out = []
    for sh in theme["sheets"].values():
        for k, v in sh.items():
            if k in ("arc_ja", "identity_cue_ja", "entry_mood_ja"):
                continue
            if isinstance(v, str):
                out.append(PAREN_RE.sub("", v))
            elif k == "experiences":
                out += [PAREN_RE.sub("", x["text_ja"]) for x in v]
            elif k == "speech_style":
                out += [PAREN_RE.sub("", x) for x in v.values()]
    return out


def test_no_kanji_quantity_expressions_in_persona_text():
    """OF-Y8-05: NUM_REが拾わない漢数字の数量表現(一軒・二回・三度・二度目 等)がPersona本文にない(括弧内のメタ指示は除く)。"""
    th = ob3.load_theme()
    for s in _narrative_texts(th):
        assert QTY_RE.search(s) is None, s
    assert QTY_RE.search("一軒の玄関先") and QTY_RE.search("二回目") and QTY_RE.search("三度")        # 検査パターン自体が型を拾う


_PUNCT = re.compile(r"[\s　、。，．,.!！?？「」『』（）()・…\-—:：;；\"'“”]")


def _norm(s: str) -> str:
    return _PUNCT.sub("", s)


def _longest_common(a: str, b: str, n: int) -> str:
    """aとbに共通するn文字以上の部分列があれば、その(伸ばした)一つを返す(なければ空)。nグラム集合で照合。"""
    grams = {b[i:i + n] for i in range(len(b) - n + 1)}
    for i in range(len(a) - n + 1):
        if a[i:i + n] in grams:
            j = i + n
            while j < len(a) and a[i:j + 1] in b:
                j += 1
            return a[i:j]
    return ""


ATTR_LABELS = ("現役の宅配ドライバー", "宅配ドライバー", "宅配ボックス", "置き配")          # 出典本人の属性ラベル(役割の名乗り)とテーマの基本語。表現ではないので長一致の対象から除く(role_ja/age_label・用語定義に必要)


def _strip_labels(t: str) -> str:
    for lab in ATTR_LABELS:
        t = t.replace(_norm(lab), "")
    return t


MATCH_N = 8                                                                    # 8文字以上(句読点・空白除去後)の共通部分列を長一致とみなす


def test_sheet_has_no_long_match_with_r2plus_quotes():
    """OF-Y8-01(f): R2+/R3出典の逐語抜粋(VOICES_02.jsonのquotes。git管理下)とSheet文が、8文字以上の共通部分列を持たない。"""
    th = ob3.load_theme()
    texts = [_strip_labels(_norm(s)) for s in _texts({"sheets": th["sheets"], "world_frame": {}})]
    for rid in RAW["restricted_voice_ids"]:
        for q in VOICES[rid]["quotes"]:
            nq = _norm(q)
            for t in texts:
                m = _longest_common(t, nq, MATCH_N)
                assert m == "", (rid, m)


def test_sheet_has_no_long_match_with_r2plus_source_pages_if_present():
    """OF-Y8-01(f): 保存したR2+/R3出典の本文全体(sources/、git管理外)とSheet文が、8文字以上の共通部分列を持たない。ファイルが無い環境ではskip。"""
    if not glob.glob(f"{D}/sources/pages/*.txt"):
        pytest.skip("sources/ is untracked and not present in this checkout")
    sys.path.insert(0, f"{D}/scripts")
    import verify_voices_02 as vv
    th = ob3.load_theme()
    texts = [_strip_labels(_norm(s)) for s in _texts({"sheets": th["sheets"], "world_frame": {}})]          # 対象=Persona Sheet(World frameは3人共通の中立な定義文)
    checked = 0
    for src in sorted({VOICES[r]["src"] for r in RAW["restricted_voice_ids"]}):
        body = vv.cut_ai_and_sidebar(vv.load_page_text(SOURCES[src]["url"].split("?")[0]))
        assert body, src
        nb = _norm(body)
        checked += 1
        for t in texts:
            m = _longest_common(t, nb, MATCH_N)
            assert m == "", (src, m)
    assert checked >= 6
    # 検査自体が働くこと: 原文の一部をそのままSheet文に入れると検出される
    nb = _norm(vv.cut_ai_and_sidebar(vv.load_page_text(SOURCES["S22"]["url"])))
    assert _longest_common("あいう" + nb[300:320] + "えお", nb, MATCH_N) != ""


def test_no_single_source_dominates_experience_column():
    """OF-Y8-05 公開前Gate(e): 1つのVoiceの経験欄(E)の過半が、単一の出典(src)だけに依存していないか。
    結果: V1・V3は満たす。V2はE全件がRV-08(S03、知恵袋の1人の質問)の1出典に依存する=(e)を満たさない既知の例外(Opus論点1でV2の根拠は問題なしと確認済み。
    Trial内は可。公開前Gateで再確認する対象としてここに固定し、他のVoice・他の出典へ広がったら失敗させる)。"""
    th = ob3.load_theme()
    known = {"voice_2": "S03"}
    for slot, sh in th["sheets"].items():
        ex = [x for x in sh["experiences"] if x["kind"] == "E"]
        dominated = {src for src in {VOICES[i]["src"] for x in ex for i in x["source_ids"]}
                     if len([x for x in ex if all(VOICES[i]["src"] == src for i in x["source_ids"])]) * 2 > len(ex)}
        assert dominated == ({known[slot]} if slot in known else set()), (slot, dominated)


def test_v1_not_structured_after_single_note_article():
    """OF-Y8-01: V1のRV-55だけを根拠にする項目は3つ以下で、RV-55由来の固有の言い回しを持たない。"""
    sh1 = ob3.load_theme()["sheets"]["voice_1"]
    only55 = [x["id"] for x in sh1["experiences"] if x["source_ids"] == ["RV-55"]]
    assert len(only55) <= 3, only55
    body = "".join(x["text_ja"] for x in sh1["experiences"]) + sh1["stake_ja"] + sh1["persona_sketch_ja"]
    for banned in ("眠る準備", "落ち込んでいる暇", "次から次へ", "個人のお客さんに求める", "経営の問題", "すり替え", "報酬を上げ"):
        assert banned not in body, banned


def test_v2_hypothetical_and_no_first_time_item_duplicate():
    """OF-Y8-04/05: V2のTWO_eは『もし家にいる日に〜』の仮定形、TWO_hは無い。V3のTHREE_hだけが『最初は無料で、くり返す人から』を持つ。"""
    th = ob3.load_theme()["sheets"]
    v2 = {x["id"]: x for x in th["voice_2"]["experiences"]}
    assert v2["TWO_e"]["text_ja"].startswith("もし家にいる日に") and "TWO_h" not in v2
    assert not any("最初" in x["text_ja"] for x in th["voice_2"]["experiences"])
    assert any("最初は無料で" in x["text_ja"] for x in th["voice_3"]["experiences"])
    assert "大目に見る" not in json.dumps(th, ensure_ascii=False)


def test_source_log_gate_has_e_and_f_and_tbs_only_renamed():
    sl = open(f"{D}/SOURCE_LOG_02.md", encoding="utf-8").read()
    assert "(e)" in sl and "(f)" in sl and "単一の出典" in sl and "長く一致" in sl
    assert "tbs_only" not in json.dumps(RAW)
    src = open("er110_family_y_opinion_based_03.py", encoding="utf-8").read()
    assert 'x["tbs_only"] = bool' not in src                                   # 03のloaderは tbs_only を付けない(r2plus_only)
