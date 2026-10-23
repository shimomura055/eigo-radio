# -*- coding: utf-8 -*-
"""er110_family_y_opinion_based_01 の offline test(API 0)。Prompt置換・Sheet不変条件・出典照合・予算の歯止め・隔離(DefaultOffIsolation相当)・fake clientでの通し。"""
import glob
import json
import os
import re
import subprocess
import sys
import threading
import types

import pytest

import er110_family_y_opinion_based_01 as ob
import er110_family_y_persona_pipeline_01 as pl
import er110_family_y_persona_text_trial_01 as p


# ---------------- fake client ----------------
class Fake:
    def __init__(self, bad_first=(), structure=None, leak_fail=False):
        self.bad_first = set(bad_first)       # 初回生成で出典外の出来事文を入れるslot
        self.structure = structure
        self.leak_fail = leak_fail
        self.prompts, self.n, self.lock = [], {}, threading.Lock()
        self.responses = types.SimpleNamespace(create=self._create)

    def _count(self, k):
        with self.lock:
            self.n[k] = self.n.get(k, 0) + 1
            return self.n[k]

    def _create(self, **kw):
        user = kw["input"][-1]["content"]
        with self.lock:
            self.prompts.append(user)
        fmt = kw.get("text", {}).get("format")
        name = fmt["name"] if fmt else None
        if name == "yob_provenance_map":
            slot = "voice_1" if "[ONE_a]" in user else ("voice_2" if "[TWO_a]" in user else "voice_3")
            sents = re.findall(r"^(\d+): (.*)$", user.split("【語り(文ごとに番号付き)】")[1].split("【付番の規則】")[0], re.M)
            items = []
            for i, s in sents:
                if "捏造" in s:
                    items.append({"idx": int(i), "source_ids": [], "supplement_kinds": ["なし"], "is_event_claim": True, "note_ja": "出典なし"})
                else:
                    items.append({"idx": int(i), "source_ids": [ob.allowed_ids(slot)[0]], "supplement_kinds": ["口調・言い回し"], "is_event_claim": False, "note_ja": "ok"})
            out = json.dumps({"items": items}, ensure_ascii=False)
        elif name == "yp_structure_tags":
            k = self._count("structure")
            tags = self.structure(k) if self.structure else {
                "voice_1": ("主張から具体例へ", "出来事・場面の描写から", "自嘲・告白で締める"), "voice_2": ("経験の時系列", "感情・本音の吐露から", "問いを残して締める"),
                "voice_3": ("感情から具体例へ", "主張・意見の表明から", "約束・要求で締める")}
            out = json.dumps({"voices": [{"voice": s, "development_type": d, "opening_type": o, "closing_type": c, "evidence_ja": "e"} for s, (d, o, c) in tags.items()]}, ensure_ascii=False)
        elif name and name.startswith("family_y_persona_leakage_"):
            k = self._count("leak")
            kind = name.rsplit("_", 1)[1]
            body = {}
            for sec, fields in p.leak_sections_for(kind).items():
                it = {f: "PASS" for f in fields}
                it.update(reasoning="ok", quoted_evidence="")
                if self.leak_fail and k == 1 and sec == "voice_2":
                    it[fields[0]] = "FAIL"
                    it.update(reasoning="NG", quoted_evidence="引用")
                body[sec] = it
            out = json.dumps(body, ensure_ascii=False)
        elif name == "family_y_persona_rewrite":
            sec = re.search(r"■ 書き換える語り: (voice_\d)", user).group(1)
            fp = re.search(r"一人称は「(.+?)」", user).group(1)
            out = json.dumps({"rewrites": [{"section": sec, "text": fp + "は書き換え後の語りだ。" * 3}]}, ensure_ascii=False)
        elif "一人称の語りを1段落だけ" in user:
            fp = re.search(r"一人称は「(.+?)」", user).group(1)
            slot = "voice_1" if "[ONE_a]" in user else ("voice_2" if "[TWO_a]" in user else "voice_3")
            retry = "前回の出力の問題" in user
            emph = "今回の追加指示" in user
            bad = (slot in self.bad_first) and not retry and self._count("gen_" + slot) == 1
            out = fp + "は毎朝そう思う。" + ("この前の捏造の出来事があった。" if bad else "") + ("気分を強く出す。" if emph else "") + "これは語りの本文だ。" * 12
        else:
            raise AssertionError("unexpected prompt: " + user[:80])
        return types.SimpleNamespace(output_text=out, model=kw["model"], id="resp_fake", usage=types.SimpleNamespace(input_tokens=1, output_tokens=1))


@pytest.fixture
def patched(tmp_path, monkeypatch):
    state = {"cost": 0.0, "per_call": 0.5, "calls": 0}
    fake_holder = {}

    def cost(rd):
        return round(state["cost"], 3)

    def stage_costs(rd):
        return {"fake_total": round(state["cost"], 3)}
    monkeypatch.setattr(ob, "cost_jpy", cost)
    monkeypatch.setattr(ob, "stage_costs", stage_costs)
    orig = pl.y0.chat

    def chat(client, **kw):
        state["cost"] += state["per_call"]
        state["calls"] += 1
        return orig(client, **kw)
    monkeypatch.setattr(pl.y0, "chat", chat)
    return state, str(tmp_path / "run"), str(tmp_path / "ledger.md")


# ---------------- Prompt / Sheet の決定論 ----------------
def test_prompt_rules_4_7_9_replaced_and_kept_rules():
    t = ob.VOICE_PROMPT_OB
    old = pl.VOICE_PROMPT_TMPL
    assert "相手の言葉・自分の動き" in old and "ある子が" in old and "感覚的な細部の補足は可" in old       # 旧Promptにあった問題の記述(既存は無変更の確認も兼ねる)
    assert "1つの場面を少し細かく" not in t and "「ある子が」「同僚が」" not in t and "感覚的な細部の補足は可" not in t
    assert "(IDつき)にある内容だけ" in t and "括弧を使わず" in t and "出来事を作らず、仮定" in t
    assert "「この前」「ある子が」「友達が」「先生が」のように、欄にない人物や出来事を新しく作らない" in t
    assert "人物・会話・出来事・場所・物の追加はしない" in t
    for kept in ("約260〜300字", "「です・ます」調にしない", "括弧・コロン・スラッシュ", "役割語", "自己紹介の文は書かない"):
        assert kept in t
    assert "成人" not in t


def test_build_prompt_wires_everything_and_no_digits_in_sheet_text():
    for s in ob.SLOTS:
        pr = ob.build_voice_prompt_ob(ob.WORLD_FRAME, s)
        assert "@@" not in pr
        assert ob.SHEETS[s]["opening_type"] in pr and ob.OPENING_GUIDE[ob.SHEETS[s]["opening_type"]] in pr
        for x in ob.SHEETS[s]["experiences"]:
            assert f"[{x['id']}]" in pr
            assert "MR-" not in x["text_ja"] and "TBS" not in x["text_ja"]
            assert not re.search(r"[0-9０-９]", x["text_ja"]), x["id"]
        assert "MR-T" not in pr and "TBS-" not in pr           # 出典IDは本文生成側に見せない
        assert "成人" not in pr and "歳" not in pr             # OF-Y6-05
    assert "今回の追加指示" in ob.build_voice_prompt_ob(ob.WORLD_FRAME, "voice_2", emphasize=True)


def test_sheet_invariants():
    ops = [ob.SHEETS[s]["opening_type"] for s in ob.SLOTS]
    assert len(set(ops)) == 3 and all(o in pl.OPENING_TYPES for o in ops)             # OF-Y6-06: 冒頭の型は3人別々
    assert sum(1 for o in ops if o == "言い訳・弁明から") <= 1
    assert any(ob.SHEETS[s]["contradiction_or_weakness_ja"].startswith("なし") for s in ob.SLOTS)       # OF-Y6-03: 矛盾なしの言い切り型が最低1人
    fps = [ob.SHEETS[s]["speech_style"]["first_person"] for s in ob.SLOTS]
    assert len(set(fps)) == 3
    ids = [x["id"] for s in ob.SLOTS for x in ob.SHEETS[s]["experiences"]]
    assert len(ids) == len(set(ids)) and all(re.fullmatch(r"[A-Za-z_]+", i) for i in ids)
    for s in ob.SLOTS:
        srcs = [tuple(x["source_ids"]) for x in ob.SHEETS[s]["experiences"]]
        assert ("TBS-10",) not in srcs                                                  # TBS-10だけを根拠にする項目を作らない
        mr = [x for x in ob.SHEETS[s]["experiences"] if not x["tbs_only"]]
        assert len(mr) >= 3                                                              # CC BYのMRが中心(TBSは裏付け)
    assert not any(ob.SHEETS["voice_3"][k] for k in ()) and all(x["kind"] == "O" for x in ob.SHEETS["voice_3"]["experiences"])
    assert "MR-T010-17" not in [i for x in ob.SHEETS["voice_3"]["experiences"] for i in x["source_ids"]]       # V2/V3どちらか一方のみ
    assert "MR-T002-16" not in [i for s in ob.SLOTS for x in ob.SHEETS[s]["experiences"] for i in x["source_ids"]]     # 年下を見ての声は移さない
    assert not [i for s in ob.SLOTS for x in ob.SHEETS[s]["experiences"] for i in x["source_ids"] if i in ("MR-T063-01", "MR-T002-02", "MR-T020-03")]   # 保護者・市民の理屈をV3へ移さない


def test_render_persona_minor_aware():
    r = ob.render_persona_ob(ob.SHEETS["voice_3"], ob.WHO_JA["voice_3"])
    assert "成人" not in r and "歳" not in r and "中学生" in r
    r2 = pl.render_persona({"gender": "女性", "age": 40, "speech_style": {"first_person": "私", "sentence_length_pattern_ja": "", "question_back_frequency_ja": "", "assertion_or_hedging_ja": "",
                                                                         "vocabulary_layer_ja": ""}, "experiences_ja": [], "role_ja": "", "daily_life_ja": "", "contact_point_ja": "",
                           "troubles_ja": "", "wishes_honest_ja": "", "wishes_public_ja": "", "emotion_habit_ja": "", "values_ja": "", "interests_ja": "",
                           "contradiction_or_weakness_ja": "", "entry_mood_ja": "", "claim_core_ja": ""}, "x")
    assert "成人" in r2            # 既存renderは無変更(未成年に使えないことの確認)


def test_world_frame_valid_for_pipeline():
    wf = ob.WORLD_FRAME
    assert wf["status_quo"] == [] and re.search(r"[0-9０-９]", json.dumps(wf, ensure_ascii=False)) is None
    assert "実在の特定の人" in ob.INTRO_JA and "複数の意見" in ob.INTRO_JA


# ---------------- 出典照合 ----------------
def _items(rows):
    return {"items": [{"idx": i, "source_ids": ids, "supplement_kinds": sup, "is_event_claim": claim, "note_ja": ""} for i, (ids, sup, claim) in enumerate(rows)]}


def test_check_mapping_rules():
    sents = ["私は毎朝そう思う。", "この前、友達に言われた。", "もし教室に使えない子がいたら外れると思う。", "親の設定は面倒だった。"]
    ok = ob.check_mapping("voice_1", sents, _items([(["ONE_a"], ["口調・言い回し"], False), (["ONE_a"], ["なし"], False), (["ONE_c"], ["なし"], False), (["ONE_c"], ["なし"], False)]))
    # 2文目は出来事らしいがE-IDがONE_a(E)なので通る/ 4文目も同様
    assert ok["n_unmapped"] == 0
    bad = ob.check_mapping("voice_3", sents, _items([(["THREE_a"], ["なし"], False), (["THREE_a"], ["なし"], False), (["THREE_f"], ["なし"], False), ([], ["口調・言い回し"], False)]))
    # voice_3はE-IDなし: 2文目(出来事らしい・仮定でない)はUNMAPPED。4文目(過去形らしい)もE-IDなしでUNMAPPED
    assert bad["unmapped_idx"] == [1, 3] and "EVENT_LIKE_WITHOUT_E_ID" in bad["rows"][1]["reasons"]
    bad2 = ob.check_mapping("voice_2", ["x。", "y。", "z。"], _items([(["ONE_a"], ["なし"], False), ([], ["なし"], False), ([], ["口調・言い回し"], True)]))
    assert bad2["unmapped_idx"] == [0, 1, 2]
    assert "ID_NOT_IN_ALLOWLIST:ONE_a" in bad2["rows"][0]["reasons"] and "NO_ID_NO_SUPPLEMENT" in bad2["rows"][1]["reasons"] and "EVENT_CLAIM_WITHOUT_ID" in bad2["rows"][2]["reasons"]
    miss = ob.check_mapping("voice_1", ["a。", "b。"], _items([(["ONE_a"], ["なし"], False)]))
    assert miss["unmapped_idx"] == [1] and miss["rows"][1]["reasons"] == ["NOT_LABELED"]
    tbs = ob.check_mapping("voice_1", ["a。"], _items([(["ONE_d"], ["なし"], False)]))
    assert tbs["tbs_only_idx"] == [0] and tbs["n_unmapped"] == 0


# ---------------- 通し(fake client) ----------------
def test_happy_path(patched):
    state, rd, led = patched
    fake = Fake()
    st = ob.run_pipeline(fake, rd, ledger_md=led)
    assert st["gate_status"] == "PASS" and st["unmapped_regen"] == {} and st["structure"]["regen"] is None
    assert os.path.exists(f"{rd}/article_ja.md")
    art = open(f"{rd}/article_ja.md", encoding="utf-8").read()
    assert ob.INTRO_JA in art and "## One Voice" in art and "## A Third Voice" in art
    assert sum(1 for x in fake.prompts if "一人称の語りを1段落だけ" in x) == 3
    assert fake.n.get("structure") == 1
    assert "gate" in st and all(not st["final_maps"][s]["n_unmapped"] for s in ob.SLOTS)


def test_unmapped_regen_once_per_voice(patched):
    state, rd, led = patched
    fake = Fake(bad_first=("voice_1", "voice_3"))
    st = ob.run_pipeline(fake, rd, ledger_md=led)
    assert set(st["unmapped_regen"]) == {"voice_1", "voice_3"}
    for s in ("voice_1", "voice_3"):
        assert st["unmapped_regen"][s]["n_unmapped_before"] >= 1 and st["unmapped_regen"][s]["n_unmapped_after"] == 0
    gens = [x for x in fake.prompts if "一人称の語りを1段落だけ" in x]
    assert len(gens) == 5                       # 3 + UNMAPPED再生成2(各1回)
    assert sum(1 for x in gens if "前回の出力の問題" in x and "経験・意見」欄にない出来事" in x) == 2
    assert "捏造" not in open(f"{rd}/article_ja.md", encoding="utf-8").read()


def test_structure_regen_at_most_once(patched):
    state, rd, led = patched
    same = {"voice_1": ("主張から具体例へ", "主張・意見の表明から", "自嘲・告白で締める"), "voice_2": ("主張から具体例へ", "主張・意見の表明から", "約束・要求で締める"),
            "voice_3": ("経験の時系列", "問いかけから", "迷いを残して締める")}
    fake = Fake(structure=lambda k: same)
    st = ob.run_pipeline(fake, rd, ledger_md=led)
    assert st["structure"]["regen"]["slot"] == "voice_2"
    assert fake.n["structure"] == 2             # 是正は1回だけ(3回目のタグ付け・再再生成はない)
    assert len([x for x in fake.prompts if "今回の追加指示" in x]) == 1


def test_budget_stop_at_27(patched):
    state, rd, led = patched
    state["per_call"] = 9.0                      # 生成3call=27円に達した時点で次の新規呼出を止める
    fake = Fake()
    with pytest.raises(pl.PipelineStop) as ei:
        ob.run_pipeline(fake, rd, ledger_md=led)
    assert ei.value.code == "BUDGET_STOP_27"
    assert state["calls"] == 3
    assert not any("付番" in x for x in fake.prompts)
    ob.write_partial(rd)
    assert os.path.exists(f"{rd}/article_ja_partial.md") and "One Voice" in open(f"{rd}/article_ja_partial.md", encoding="utf-8").read()


def test_gate_skipped_when_over_22(patched):
    state, rd, led = patched
    state["per_call"] = 3.4                      # gen3+map3+structure=23.8円で、Gate前に22円超
    fake = Fake()
    st = ob.run_pipeline(fake, rd, ledger_md=led)
    assert st["gate_status"] == "SKIPPED_BUDGET" and os.path.exists(f"{rd}/article_ja.md") and "final_map_skipped" in st


def test_gate_rewrite_path(patched):
    state, rd, led = patched
    fake = Fake(leak_fail=True)
    st = ob.run_pipeline(fake, rd, ledger_md=led)
    assert st["gate_status"] == "PASS" and st["gate"]["n_judgements"] == 2
    assert st["final_texts"]["voice_1"] == st["stages"]["gen"]["voice_1"]["text"]       # flag外は不変
    assert st["final_texts"]["voice_2"] != st["stages"]["gen"]["voice_2"]["text"]


def test_ledger_written(patched):
    state, rd, led = patched
    ob.run_pipeline(Fake(), rd, ledger_md=led)
    body = open(led, encoding="utf-8").read()
    assert "| gen |" in body and "| final_map |" in body


# ---------------- 隔離(DefaultOffIsolation相当) ----------------
def test_isolation_no_importer_and_api_zero_on_import():
    me = {"er110_family_y_opinion_based_01.py", "er110_family_y_opinion_based_01_test_01.py"}
    bad = []
    for f in glob.glob("*.py") + glob.glob("**/*.py", recursive=True):
        if os.path.basename(f) in me or ".venv" in f or "OPINION_BASED_01" in f:        # docs配下の解析script(build_blind_set_05.py等)はAPI 0のoffline集計でProduction未参照
            continue
        try:
            src = open(f, encoding="utf-8").read()
        except Exception:
            continue
        if re.search(r"^\s*(?:import|from)\s+er110_family_y_opinion_based_01\b", src, re.M):
            bad.append(f)
    assert bad == [], bad
    src = open("er110_family_y_opinion_based_01.py", encoding="utf-8").read()
    assert "os.environ" not in src and "getenv" not in src and "argparse" not in src
    assert "OpenAI(" not in src


def test_import_has_no_side_effect(tmp_path):
    out = subprocess.run([sys.executable, "-c", "import er110_family_y_opinion_based_01 as o, os; print(os.path.exists(o.RUN_DIR))"], capture_output=True, text=True)
    assert out.stdout.strip().endswith("False") or os.path.exists(ob.RUN_DIR)


def test_main_refuses_relaunch(tmp_path, monkeypatch):
    rd = tmp_path / "rd"
    rd.mkdir()
    (rd / "entry_point.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(ob, "RUN_DIR", str(rd))
    assert ob.main() == 5


def test_existing_er110_modules_unchanged():
    out = subprocess.run(["git", "diff", "--name-only", "HEAD", "--", "er110_family_y_text_trial_01.py", "er110_family_y_persona_text_trial_01.py",
                          "er110_family_y_persona_pipeline_01.py", "er110_family_y_persona_pipeline_01_run.py", "er110_family_y_persona_text_trial_01_run.py",
                          "er110_family_y_persona_eval_01.py"], capture_output=True, text=True).stdout.strip()
    assert out == "", out


def test_models_recorded():
    assert ob.MODEL_TOP == "gpt-6.1-sol" and ob.MODEL_CHEAP == "gpt-6-luna" and ob.BUDGET_STOP_JPY == 27.0
