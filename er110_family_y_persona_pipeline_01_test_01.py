# -*- coding: utf-8 -*-
"""er110_family_y_persona_pipeline_01 の offline test(API 0)。DefaultOffIsolation相当+決定論部分+fake clientによるS2〜S6通し。"""
import glob
import json
import os
import re
import subprocess
import threading
import types

import pytest

import er110_family_y_persona_pipeline_01 as pl
import er110_family_y_persona_text_trial_01 as p
import er110_family_y_text_trial_01 as y0

SH_N = 9


def _stakeholders(n=SH_N, primary_upto=4):
    out = []
    for i in range(1, n + 1):
        out.append({"id": f"S{i:02d}", "who_ja": f"立場{i}の人", "contact_point_ja": f"毎朝の通勤電車で{i}番目の車両に乗り、そこでこの規則の影響を直接受ける暮らしをしている{i}",
                    "stakes_ja": f"利害{i}", "is_primary": i <= primary_upto, "why_would_speak_ja": f"理由{i}"})
    return {"stakeholders": out, "primary_parties_excluded": []}


def _claims():
    out = []
    for i in range(1, SH_N + 1):
        out.append({"stakeholder_id": f"S{i:02d}", "claims": [
            {"claim_ja": f"主張{i}-{k}", "kind": ["自己都合", "要求", "不安"][k], "origin_ja": f"夜遅くまで働いた{i}日目の疲れから生まれる経験{k}", "rationality": "本人なりの理屈",
             "self_contradiction_ja": "", "factual_risk": "no", "necessity_note_ja": "接続している"} for k in range(3)]})
    return {"claim_seeds": out}


def _s4(members_sets, selected="T1", gi=None):
    gi = gi or {}
    trios = []
    st = {x["id"]: x for x in _stakeholders()["stakeholders"]}
    for tid, ids in zip(("T1", "T2", "T3"), members_sets):
        ms = [{"stakeholder_id": s, "claim_id": f"{s}_c1", "gender_intrinsic": gi.get(s, "不問"), "gender_intrinsic_reason_ja": "x"} for s in ids]
        ra = "".join(f"『{st[s]['contact_point_ja']}』" for s in ids)
        rb = "".join("『夜遅くまで働いた%d日目の疲れから生まれる経験0』" % int(s[1:]) for s in ids)
        trios.append({"trio_id": tid, "members": ms, "reason_A_ja": ra, "reason_B_ja": rb, "reason_C_ja": "c", "diversity_note_ja": "d", "listener_note_ja": "l",
                      "strongest_objection_ja": "o"})
    return {"candidate_trios": trios, "selected_trio_id": selected, "why_not_others_ja": "w"}


FPS = ["俺", "僕", "私", "わたし"]


class Fake:
    """schema名で分岐する偽client(API 0)。設定で差戻し・構造発火・Leakage FAIL等を再現。"""

    def __init__(self, s4=None, natural=None, structure=None, leak_fail_first=False, fp_dup=False):
        self.s4 = s4 or _s4([("S01", "S02", "S03"), ("S04", "S05", "S06"), ("S07", "S08", "S09")])
        self.natural = natural or {}      # {call_index_by_who: verdict}
        self.structure = structure
        self.leak_fail_first = leak_fail_first
        self.fp_dup = fp_dup
        self.prompts = []
        self.n = {}
        self.lock = threading.Lock()
        self.responses = types.SimpleNamespace(create=self._create)

    def _count(self, key):
        with self.lock:
            self.n[key] = self.n.get(key, 0) + 1
            return self.n[key]

    def _create(self, **kw):
        user = kw["input"][-1]["content"]
        self.prompts.append(user)
        fmt = kw.get("text", {}).get("format")
        name = fmt["name"] if fmt else None
        if name == "yp_world_frame":
            out = json.dumps(pl.SCHOOL_WORLD_FRAME_APPROVED, ensure_ascii=False)
        elif name == "yp_stakeholders":
            out = json.dumps(_stakeholders(), ensure_ascii=False)
        elif name == "yp_primary_coverage":
            out = json.dumps({"items": [{"listed_party_ja": "a", "covered": True, "matched_stakeholder_ids": ["S01"], "note_ja": "n"}]}, ensure_ascii=False)
        elif name == "yp_claim_seeds":
            out = json.dumps(_claims(), ensure_ascii=False)
        elif name == "yp_trio_selection":
            out = json.dumps(self.s4, ensure_ascii=False)
        elif name == "yp_persona_sheet":
            who = re.search(r"立場(\d)の人", user).group(1)
            gender = "女性" if "gender は「女性」" in user else "男性"
            fp = "私" if self.fp_dup else FPS[int(who) % 4]
            if "重ならない" in user and self.fp_dup:
                fp = "わたし"
            out = json.dumps({"age": 30 + int(who), "gender": gender, "role_ja": "役割", "daily_life_ja": "生活", "world_variant": "common", "contact_point_ja": "接点",
                              "experiences_ja": ["経験1", "経験2"], "troubles_ja": "困", "wishes_honest_ja": "本音", "wishes_public_ja": "建前", "emotion_habit_ja": "癖",
                              "values_ja": "価値", "interests_ja": "利害", "contradiction_or_weakness_ja": "弱さ",
                              "speech_style": {"first_person": fp, "sentence_length_pattern_ja": "短い", "question_back_frequency_ja": "少", "assertion_or_hedging_ja": "断言",
                                               "vocabulary_layer_ja": "口語"},
                              "entry_mood_ja": f"気分{who}", "identity_cue_ja": "手がかり", "claim_core_ja": "芯" + "アイウエオカキクケコ"[int(who)], "why_this_person_says_this_ja": "道筋",
                              "known_fact_id": "", "known_fact_usage_ja": ""}, ensure_ascii=False)
        elif name == "yp_naturalness":
            who = re.search(r"立場(\d)の人", user).group(1)
            c = self._count(f"nat{who}")
            v = self.natural.get((who, c), "natural")
            out = json.dumps({"most_unnatural_point_ja": "p", "would_listener_feel_wrong": v != "natural", "reason_ja": "r", "verdict": v}, ensure_ascii=False)
        elif name == "yp_reeval_c":
            out = json.dumps({"reason_C_ja": "再評価", "diversity_note_ja": "d"}, ensure_ascii=False)
        elif name == "yp_structure_tags":
            k = self._count("structure")
            tags = self.structure(k) if self.structure else {s: ("主張から具体例へ", "出来事・場面の描写から", "問いを残して締める") for s in ()}
            if not self.structure:
                tags = {"voice_1": ("主張から具体例へ", "自分の状況・立場の描写から", "自嘲・告白で締める"), "voice_2": ("経験の時系列", "出来事・場面の描写から", "問いを残して締める"),
                        "voice_3": ("感情から具体例へ", "感情・本音の吐露から", "約束・要求で締める")}
            out = json.dumps({"voices": [{"voice": s, "development_type": d, "opening_type": o, "closing_type": c, "evidence_ja": "e"} for s, (d, o, c) in tags.items()]}, ensure_ascii=False)
        elif name and name.startswith("family_y_persona_leakage_"):
            k = self._count("leak_" + name)
            kind = name.rsplit("_", 1)[1]
            secs = p.leak_sections_for(kind)
            body = {}
            for sec, fields in secs.items():
                it = {f: "PASS" for f in fields}
                it.update(reasoning="ok", quoted_evidence="")
                if self.leak_fail_first and k == 1 and sec in ("voice_2", "tension"):
                    it[fields[0]] = "FAIL"
                    it.update(reasoning="NG", quoted_evidence="引用")
                body[sec] = it
            out = json.dumps(body, ensure_ascii=False)
        elif name == "family_y_persona_rewrite":
            sec = re.search(r"■ 書き換える語り: (voice_\d)", user)
            sec = sec.group(1) if sec else "tension"
            txt = "書き換え後の語りだ。" * 3 if sec != "tension" else "3人とも困っている。夜の居間とベッドの枕元。あなたの家では、どこに置いてある?"
            m_fp = re.search(r"一人称は「(.+?)」", user)
            fp = m_fp.group(1) if (m_fp and sec != "tension") else ""
            out = json.dumps({"rewrites": [{"section": sec, "text": (fp + "は" + txt) if fp else txt}]}, ensure_ascii=False)
        elif "一人称の語りを1段落だけ" in user:
            fp = re.search(r"一人称は「(.+?)」", user).group(1)
            emph = "今回の追加指示" in user
            out = fp + "は毎朝そう思う。" + ("気分を強く出す。" if emph else "") + "これは語りの本文だ。" * 12
        elif "最後の1パート" in user:
            out = "3人とも困っている。夜の居間、朝の枕元、休み時間の連絡。あなたの家では、どこに置いてある？"
        else:
            raise AssertionError("unexpected prompt: " + user[:80])
        return types.SimpleNamespace(output_text=out, model=kw["model"], id="resp_fake", usage=types.SimpleNamespace(input_tokens=1, output_tokens=1))


def _run_to_voices(tmp_path, fake):
    ctx = pl.Ctx(fake, str(tmp_path), "t")
    wf = pl.SCHOOL_WORLD_FRAME_APPROVED
    s2 = pl.stage_s2(ctx, wf)
    s3 = pl.stage_s3(ctx, wf, s2["stakeholders"])
    s4 = pl.stage_s4(ctx, wf, s2["stakeholders"], s3["claims"])
    s5 = pl.stage_s5(ctx, wf, s2["stakeholders"], s3["claims"], s4)
    return ctx, wf, s2, s3, s4, s5


# ---------------- 決定論部分 ----------------
def test_all_schemas_strict_shape():
    def walk(s, path):
        if s.get("type") == "object":
            assert s["additionalProperties"] is False, path
            assert sorted(s["required"]) == sorted(s["properties"]), path
            for k, v in s["properties"].items():
                walk(v, path + "." + k)
        elif s.get("type") == "array":
            walk(s["items"], path + "[]")
    for nm in dir(pl):
        if nm.startswith("SCHEMA_"):
            sc = getattr(pl, nm)
            assert sc["strict"] is True
            walk(sc["schema"], nm)


def test_assign_slots():
    f = lambda *g: [{"gender_intrinsic": x} for x in g]
    a = pl.assign_slots(f("不問", "不問", "不問"))
    assert {a[s]["assigned_gender"] for s in pl.SLOTS} == {"男性", "女性"} and a["voice_2"]["assigned_gender"] == "女性"
    a = pl.assign_slots(f("女性", "男性", "男性"))
    assert a["voice_2"]["gender_intrinsic"] == "女性" and a["voice_1"]["assigned_gender"] == "男性"
    a = pl.assign_slots(f("男性", "不問", "女性"))
    assert a["voice_2"]["gender_intrinsic"] == "女性" and a["voice_1"]["gender_intrinsic"] == "男性"
    assert pl.assign_slots(f("女性", "女性", "不問")) is None            # 女性2人 -> 割当不能(手作業で直さない)
    assert pl.assign_slots(f("女性", "女性", "女性")) is None
    assert pl.assign_slots(f("男性", "男性", "男性")) is None            # 男性3人 -> 女性スロットが空かない


def _tags(d1, o1, c1, d2, o2, c2, d3="経験の時系列", o3="問いかけから", c3="迷いを残して締める"):
    return {"voice_1": {"development_type": d1, "opening_type": o1, "closing_type": c1}, "voice_2": {"development_type": d2, "opening_type": o2, "closing_type": c2},
            "voice_3": {"development_type": d3, "opening_type": o3, "closing_type": c3}}


def test_structure_fire_rule_of_y5_06():
    # 旧V1/V3型: 展開同一・冒頭同一・締めのみ違う -> 発火(冒頭一致があるため)
    t = _tags("主張から具体例へ", "主張・意見の表明から", "自嘲・告白で締める", "主張から具体例へ", "主張・意見の表明から", "約束・要求で締める")
    f = pl.structure_fire(t)
    assert f["fired"] and f["regenerate_slot"] == "voice_2"
    # 展開同一・冒頭違い・締め違い -> 発火しない(締めの違いだけでは『異なる』とみなさないが、一致もしていない)
    t = _tags("主張から具体例へ", "主張・意見の表明から", "自嘲・告白で締める", "主張から具体例へ", "問いかけから", "約束・要求で締める")
    assert not pl.structure_fire(t)["fired"]
    # 展開同一・冒頭違い・締め一致 -> 発火
    t = _tags("主張から具体例へ", "主張・意見の表明から", "自嘲・告白で締める", "主張から具体例へ", "問いかけから", "自嘲・告白で締める")
    assert pl.structure_fire(t)["fired"]
    # 展開が違えば冒頭・締めが同じでも発火しない
    t = _tags("主張から具体例へ", "主張・意見の表明から", "自嘲・告白で締める", "経験の時系列", "主張・意見の表明から", "自嘲・告白で締める", d3="感情から具体例へ")
    assert not pl.structure_fire(t)["fired"]
    # 『その他』同士は一致としない
    t = _tags("その他", "その他", "その他", "その他", "その他", "その他")
    assert not pl.structure_fire(t)["fired"]
    assert "自嘲・告白で締める" in pl.CLOSING_TYPES


def test_quote_hits_and_s4_validation():
    shs = _stakeholders()["stakeholders"]
    cls = [{**c, "id": f"{cs['stakeholder_id']}_c{k}", "stakeholder_id": cs["stakeholder_id"]} for cs in _claims()["claim_seeds"] for k, c in enumerate(cs["claims"], 1)]
    ok = _s4([("S01", "S02", "S03"), ("S04", "S05", "S06"), ("S07", "S08", "S09")])
    v = pl.validate_s4(ok, shs, cls)
    assert v["errors"] == [], v
    bad = json.loads(json.dumps(ok))
    bad["candidate_trios"][0]["reason_A_ja"] = "ざっくりした理由"
    assert any(e.startswith("S4_REASON_A_QUOTES_LT2") for e in pl.validate_s4(bad, shs, cls)["errors"])
    bad = json.loads(json.dumps(ok))
    bad["candidate_trios"][1]["members"][0]["stakeholder_id"] = "S05"
    assert any("SAME_STAKEHOLDER" in e for e in pl.validate_s4(bad, shs, cls)["errors"])


def test_s3_validation_counts():
    flat = pl.number_claims(_claims())
    assert flat[0]["id"] == "S01_c1" and len(flat) == SH_N * 3
    v = pl.validate_claims(flat, [f"S{i:02d}" for i in range(1, SH_N + 1)])
    assert v["errors"] == []
    assert pl.validate_claims(flat[:-1], [f"S{i:02d}" for i in range(1, SH_N + 1)])["errors"]


def test_office_and_school_ledger_parsing():
    raw = open("er012_output/editorial_b_voices_trial_06/research/verified_fact_ledger.txt", encoding="utf-8").read()
    o = pl.office_ledger_facts(raw)
    assert len(o.split("\n")) == 12 and "VOICE_" not in o and "固定席側" not in o
    s = open("er110_output/family_y_persona_trial_01/school_phone_ban/research_ledger/verified_fact_ledger.txt", encoding="utf-8").read()
    assert "JP-03" in pl.school_ledger_facts(s)


def test_s1_compare_to_approved():
    r = pl.compare_s1_to_approved(pl.SCHOOL_WORLD_FRAME_APPROVED, pl.SCHOOL_WORLD_FRAME_APPROVED)
    assert r["n_pass"] >= 8
    assert pl.validate_world_frame(pl.SCHOOL_WORLD_FRAME_APPROVED, {"JP-03"}) == []


# ---------------- Prompt: 撤去・残置(DESIGN_PROPOSAL_05 §7 / OF-Y5-05) ----------------
def test_voice_prompt_removed_and_kept_rules():
    t = pl.VOICE_PROMPT_TMPL
    for gone in ("closing_type", "中心となる見方", "20代以上", "主張の核は1つだけ", "締めの一言で主張の核に戻る", "ためらい（", "ためらい(言い淀み", "@@ORDER@@", "@@CLOSING@@", "語りの順序:", "領分", "締めはまとめ"):
        assert gone not in t, gone
    assert "order" not in re.sub(r"[A-Za-z]*(?:border|order_)[A-Za-z]*", "", t).replace("@@", "")
    assert "冒頭の3文以内" in t                      # 規則3 identity_cue(残置、位置は緩和)
    assert "一言で言える" in t                       # 規則4の目標1行(残置)
    assert "数字" in t and "役割語" in t and "一般化" in t.replace("一般化", "一般化") and "括弧" in t      # 規則9〜13(残置)
    assert "調査や事実の説明" in t


def test_build_voice_prompt_wires_persona_without_other_voices():
    fake = Fake()
    sheet = json.loads(fake._create(model="gpt-6.1-sol", input=[{"role": "user", "content": "立場3の人 gender は「男性」 yp"}], text={"format": pl.SCHEMA_S5}).output_text)
    pr = pl.build_voice_prompt(pl.SCHOOL_WORLD_FRAME_APPROVED, sheet, "立場3の人")
    assert "@@" not in pr and "手がかり" in pr and "芯エ" in pr and "気分3" in pr
    assert pl.SCHOOL_WORLD_FRAME_APPROVED["distinctions"][1]["term_ja"] in pr
    pr2 = pl.build_voice_prompt(pl.SCHOOL_WORLD_FRAME_APPROVED, sheet, "立場3の人", emphasize_entry_mood=True)
    assert "今回の追加指示" in pr2 and "今回の追加指示" not in pr


# ---------------- 通し(fake client) ----------------
def test_happy_path_s2_to_gate(tmp_path):
    fake = Fake()
    ctx, wf, s2, s3, s4, s5 = _run_to_voices(tmp_path, fake)
    assert s5["rework_count"] == 0 and s5["naturalness_flags_total"] == 0
    assert set(s5["members"]) == set(pl.SLOTS)
    assert s5["personas"]["voice_2"]["assigned_gender"] == "女性"
    sh_by = {x["id"]: x for x in s2["stakeholders"]}
    s6 = pl.stage_voices(ctx, wf, s5, sh_by, str(tmp_path))
    assert s6["gate_status"] == "PASS" and s6["structure_regen"] is None
    assert set(s6["final_voices"]) == set(pl.SLOTS)
    # S3にFact(台帳)を渡していない: S3 promptにfact ID(JP-xx)が無いことは world_frame の status_quo basis を除きS3 promptに出ない
    s3_prompt = [x for x in fake.prompts if "主張の種を探索" in x][0]
    assert "台帳" not in s3_prompt
    # S6 promptは他Voiceの本文・Persona Sheetを含まない
    v_prompts = [x for x in fake.prompts if "一人称の語りを1段落だけ" in x]
    assert len(v_prompts) == 3 and all("気分" in x for x in v_prompts)


def test_rework_adjust_and_replace(tmp_path):
    # voice_2(立場2?)ではなく、S5の自然さ判定をsloting後に差し込む: whoは立場番号。S01=俺... S02, S03
    fake = Fake(natural={("2", 1): "adjust_claim", ("3", 1): "replace_person"})
    ctx, wf, s2, s3, s4, s5 = _run_to_voices(tmp_path, fake)
    assert s5["rework_count"] == 2
    kinds = [r["kind"] for r in s5["log"]["rework"]]
    assert kinds == ["adjust_claim", "replace_person"]
    assert s5["reeval_C"] is not None
    assert s5["members"]["voice_2"]["claim_id"] != "S02_c1" or s5["members"]["voice_2"]["stakeholder_id"] != "S02"


def test_rework_limit_exceeded_stops(tmp_path):
    fake = Fake(natural={("1", 1): "adjust_claim", ("1", 2): "adjust_claim", ("1", 3): "adjust_claim", ("2", 1): "adjust_claim", ("2", 2): "adjust_claim",
                         ("3", 1): "adjust_claim", ("3", 2): "adjust_claim"})
    with pytest.raises(pl.PipelineStop) as e:
        _run_to_voices(tmp_path, fake)
    assert e.value.code == "REWORK_LIMIT_EXCEEDED"
    assert os.path.exists(os.path.join(str(tmp_path), "s5_personas_FAILED.json")) and not os.path.exists(os.path.join(str(tmp_path), "s5_personas.json"))


def test_slot_infeasible_stops(tmp_path):
    fake = Fake(s4=_s4([("S01", "S02", "S03"), ("S04", "S05", "S06"), ("S07", "S08", "S09")], gi={"S01": "女性", "S02": "女性"}))
    with pytest.raises(pl.PipelineStop) as e:
        _run_to_voices(tmp_path, fake)
    assert e.value.code == "SLOT_ASSIGNMENT_INFEASIBLE"


def test_first_person_duplicate_redo_once(tmp_path):
    fake = Fake(fp_dup=True)
    ctx, wf, s2, s3, s4, s5 = _run_to_voices(tmp_path, fake)
    assert "first_person_redo" in s5["log"]
    assert s5["rework_count"] == 0       # 差戻し回数には数えない


def test_structure_fire_regenerates_only_later_voice_once(tmp_path):
    same = {"voice_1": ("主張から具体例へ", "主張・意見の表明から", "自嘲・告白で締める"), "voice_2": ("主張から具体例へ", "主張・意見の表明から", "約束・要求で締める"),
            "voice_3": ("経験の時系列", "問いかけから", "迷いを残して締める")}
    fake = Fake(structure=lambda k: same)
    ctx, wf, s2, s3, s4, s5 = _run_to_voices(tmp_path, fake)
    sh_by = {x["id"]: x for x in s2["stakeholders"]}
    s6 = pl.stage_voices(ctx, wf, s5, sh_by, str(tmp_path))
    assert s6["structure_regen"]["slot"] == "voice_2"
    assert s6["structure_tags_after"] is not None                 # 2回目は記録のみ
    assert fake.n["structure"] == 2                               # 是正は1回だけ(3回目のタグ付け・再再生成はない)
    emph = [x for x in fake.prompts if "今回の追加指示" in x]
    assert len(emph) == 1


def test_gate_rewrite_path(tmp_path):
    fake = Fake(leak_fail_first=True)
    ctx, wf, s2, s3, s4, s5 = _run_to_voices(tmp_path, fake)
    sh_by = {x["id"]: x for x in s2["stakeholders"]}
    s6 = pl.stage_voices(ctx, wf, s5, sh_by, str(tmp_path))
    assert s6["gate_status"] == "PASS" and s6["gate_history_n"] == 2
    assert s6["final_voices"]["voice_1"] == s6["generated"]["voice_1"]["text"]       # flag外は不変
    assert s6["final_voices"]["voice_2"] != s6["generated"]["voice_2"]["text"]
    t = pl.stage_tension(ctx, wf, s6["final_voices"], str(tmp_path))
    assert t["gate_status"] == "PASS" and t["n_judgements"] == 2


# ---------------- 隔離(DefaultOffIsolation相当) ----------------
def test_isolation_no_importer_and_api_zero_on_import():
    me = {"er110_family_y_persona_pipeline_01.py", "er110_family_y_persona_pipeline_01_run.py", "er110_family_y_persona_pipeline_01_test_01.py"}
    bad = []
    for f in glob.glob("*.py") + glob.glob("**/*.py", recursive=True):
        if os.path.basename(f) in me or ".venv" in f:
            continue
        try:
            src = open(f, encoding="utf-8").read()
        except Exception:
            continue
        if re.search(r"^\s*(?:import|from)\s+er110_family_y_persona_pipeline_01\b", src, re.M):
            bad.append(f)
    assert bad == [], bad
    src = open("er110_family_y_persona_pipeline_01.py", encoding="utf-8").read()
    assert "os.environ" not in src and "getenv" not in src and "argparse" not in src       # flag/環境変数/CLI経路なし
    assert "OpenAI(" not in src                                                          # import時にclientを作らない


def test_existing_er110_modules_unchanged():
    out = subprocess.run(["git", "diff", "--name-only", "HEAD", "--", "er110_family_y_text_trial_01.py", "er110_family_y_persona_text_trial_01.py",
                          "er110_family_y_persona_text_trial_01_run.py", "er110_family_y_persona_eval_01.py"], capture_output=True, text=True).stdout.strip()
    assert out == "", out


def test_models_recorded():
    assert pl.MODEL_TOP == "gpt-6.1-sol" and pl.MODEL_CHEAP == "gpt-6-luna"
    assert pl.TTS_VOICE == y0.TTS_VOICE_FIXED and all(pl.SLOT_GENDER[s] == y0.VOICE_GENDER[s] for s in pl.SLOTS)
