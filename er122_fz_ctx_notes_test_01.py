# -*- coding: utf-8 -*-
"""FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_02: 感情・文脈notesの正式Production経路のoffline test(API 0)。

TEST-01(Trial方式の正確な移植): Trial全編(猿の手/メロス × Std/Adv)の実成果物に対して、本番moduleの
extract_context -> validate_emotion_items -> build_ctx_style が Trial `gen/<cid>/result.json` の style_sha256 と全dialogue clipで一致すること、
emotion_prompt_sha / LLM user message sha がTrialの実call記録と一致すること(= 同一Prompt・同一入力・同一検査・同一CONTEXT書式)。
M-6: build_level_plan(chunk展開あり) -> story_clips_from_plan(畳み戻し) がTrialのsegment_plan clipsと一致し、文脈抽出が変わらないこと。
TEST-11: 本番moduleにTrial module(er118)のimport・Trial一時機構が無いこと。TEST-16: 3値(ACCEPTED/NO_EXPLICIT_CUE/DISCARDED)の決定論検査。
M-7: LLM失敗(1回再試行後も)=技術STOP、再開可(保存済みnotesの再利用でLLM 0)。
"""
import ast
import json
import os

import pytest

import er122_fz_ctx_notes_01 as notes

ROOT = os.path.dirname(os.path.abspath(__file__))
TRIAL_OUT = "er118_output/fz_full_episode_trial_01"
RUN_ROOT = "er026_output/family_z_production_e2e_01"
CASES = [("monkeys_paw", "a2", "the_monkeys_paw", f"{RUN_ROOT}/the_monkeys_paw/run_sf_prod_01"),
         ("monkeys_paw", "b1b", "the_monkeys_paw", f"{RUN_ROOT}/the_monkeys_paw/run_sf_prod_01"),
         ("melos", "a2", "melos", f"{RUN_ROOT}/melos/run_e2e_06"),
         ("melos", "b1b", "melos", f"{RUN_ROOT}/melos/run_e2e_06")]


def _p(rel):
    return os.path.join(ROOT, rel)


def _load(rel):
    with open(_p(rel), encoding="utf-8") as f:
        return json.load(f)


def _have(rel):
    return os.path.exists(_p(rel))


def _plan_clips(run, level):
    return _load(f"{run}/segment_plan_{level}.json")["clips"]


@pytest.fixture(autouse=True)
def _reset():
    notes.reset_providers_for_test()
    yield
    notes.reset_providers_for_test()
    notes.LLM_FN = None


@pytest.mark.parametrize("work,level,story,run", CASES)
def test_01_trial_equivalence_style_sha_all_dialogue_clips(work, level, story, run):
    """Trial実成果物と全dialogue clipで style sha が完全一致(CONTEXT書式・検査・許可語・表示名の逐語移植の証明)。"""
    notes_path = f"{TRIAL_OUT}/{work}/{level}/llm/emotion_notes.json"
    review_path = f"{TRIAL_OUT}/{work}/{level}/llm/emotion_review.json"
    if not (_have(notes_path) and _have(f"{run}/segment_plan_{level}.json")):
        pytest.skip("Trial成果物なし")
    trial = _load(notes_path)
    review = _load(review_path)["items"]
    trial_clips = _plan_clips(run, level)
    # Productionのstory data(正規化後の話者key)を使うため、Trial planの話者keyをProduction正規化へ(melos: king->dionysius, friend->selinuntius)
    import er063_family_z_audio_01 as z
    clips = []
    for c in trial_clips:
        sp = z.normalize_speaker(c["speaker"], story) if c["voice_role"].startswith("dialogue:") else c["speaker"]
        clips.append({**c, "speaker": sp})
    data = notes.story_data(story, sorted({c["speaker"] for c in clips}))
    dlg_ids = [c["id"] for c in clips if c["voice_role"].startswith("dialogue:")]
    ctxs = [notes.extract_context(clips, cid, data["speaker_display"]) for cid in dlg_ids]
    assert notes.emotion_prompt_sha(data["title"]) == trial["prompt_sha256"]
    assert notes.sha_text(notes.emotion_user_message(ctxs)) == trial["user_message_sha256"]
    checked = notes.validate_emotion_items(trial["raw_output"]["items"], ctxs, data["allowed_names"])
    n_cmp = 0
    for ctx in ctxs:
        cid = ctx["clip_id"]
        n = checked[cid]
        assert n["status"] == trial["validated"][cid]["status"]
        if review[cid]["fable_decision"] == "discard":
            n = {**n, "state": "", "scene": "", "reaction": ""}
        res_p = f"{TRIAL_OUT}/{work}/{level}/gen/{cid}/result.json"
        if not _have(res_p):
            continue
        res = _load(res_p)
        style = notes.build_ctx_style(ctx, n)
        assert notes.sha_text(style) == res["style_sha256"], cid
        n_cmp += 1
    assert n_cmp >= 5
    # Trialでの決定済みレビュー: validatorを覆した件0(自動受理が同等であることの記録)
    assert all((review[cid]["fable_decision"] == "accept") == (checked[cid]["status"] in ("ACCEPTED", "NO_EXPLICIT_CUE")) for cid in dlg_ids)


def test_01b_all_53_clips_compared():
    """4 case合計53 clip(猿の手 Std15/Adv17、メロス Std10/Adv11)すべてのstyle shaがTrialと一致すること。"""
    total = 0
    import er063_family_z_audio_01 as z
    for work, level, story, run in CASES:
        if not (_have(f"{TRIAL_OUT}/{work}/{level}/llm/emotion_notes.json") and _have(f"{run}/segment_plan_{level}.json")):
            pytest.skip("Trial成果物なし")
        trial = _load(f"{TRIAL_OUT}/{work}/{level}/llm/emotion_notes.json")
        review = _load(f"{TRIAL_OUT}/{work}/{level}/llm/emotion_review.json")["items"]
        clips = [{**c, "speaker": (z.normalize_speaker(c["speaker"], story) if c["voice_role"].startswith("dialogue:") else c["speaker"])}
                 for c in _plan_clips(run, level)]
        data = notes.story_data(story, sorted({c["speaker"] for c in clips}))
        dlg_ids = [c["id"] for c in clips if c["voice_role"].startswith("dialogue:")]
        ctxs = [notes.extract_context(clips, cid, data["speaker_display"]) for cid in dlg_ids]
        checked = notes.validate_emotion_items(trial["raw_output"]["items"], ctxs, data["allowed_names"])
        for ctx in ctxs:
            res_p = f"{TRIAL_OUT}/{work}/{level}/gen/{ctx['clip_id']}/result.json"
            assert _have(res_p), res_p
            n = checked[ctx["clip_id"]]
            if review[ctx["clip_id"]]["fable_decision"] == "discard":
                n = {**n, "state": "", "scene": "", "reaction": ""}
            assert notes.sha_text(notes.build_ctx_style(ctx, n)) == _load(res_p)["style_sha256"]
            total += 1
    assert total == 53


def test_m6_chunk_fold_back_adapter_matches_trial_segment_plan():
    """Opus M-6: build_level_plan(chunk展開あり)->story_clips_from_plan が Trial segment_plan clips と同じ親clip列に戻り、文脈抽出が変わらない。"""
    import er063_family_z_audio_01 as z
    run = f"{RUN_ROOT}/the_monkeys_paw/run_sf_prod_01"
    if not _have(f"{run}/segment_plan_b1b.json"):
        pytest.skip("plan無し")
    clips = _plan_clips(run, "b1b")
    story_clips = [{"id": c["id"], "part": c["part"], "voice": c["speaker"] if c["voice_role"].startswith("dialogue:") else "narrator",
                    "speaker": c["speaker"], "text": c["text"]} for c in clips]
    # 最初の地の文(2文以上)を2 chunkに展開した擬似chunk plan
    nar = next(c for c in clips if not c["voice_role"].startswith("dialogue:") and len(notes.split_sentences(c["text"])) >= 2)
    sents = notes.split_sentences(nar["text"])
    half = len(sents) // 2
    parts = [" ".join(sents[:half]), " ".join(sents[half:])]
    cp = {nar["id"]: {"chunked": True, "planner_version": "test", "paragraph_info_lost": False,
                      "chunks": [{"chunk_id": f"{nar['id']}_k{j+1}", "index": j + 1, "text": t, "words": notes.n_words(t), "boundary_kind": "sentence"}
                                 for j, t in enumerate(parts)]}}
    plan_chunked = z.build_level_plan("b1b", story_clips, "preview", {1: "c1", 2: "c2", 3: "c3"}, [], "T", story_key="the_monkeys_paw", chunk_plans=cp)
    plan_plain = z.build_level_plan("b1b", story_clips, "preview", {1: "c1", 2: "c2", 3: "c3"}, [], "T", story_key="the_monkeys_paw")
    assert any(s.clip_id.endswith("_k1") for s in plan_chunked)           # chunk展開が実際に起きている
    folded = notes.story_clips_from_plan(plan_chunked)
    plain = notes.story_clips_from_plan(plan_plain)
    assert [c["id"] for c in folded] == [c["id"] for c in plain] == [c["id"] for c in clips]
    assert [c["text"] for c in folded] == [c["text"] for c in clips]
    data = notes.story_data("the_monkeys_paw", sorted({c["speaker"] for c in plain}))
    for c in plain:
        if c["voice_role"].startswith("dialogue:"):
            assert notes.extract_context(folded, c["id"], data["speaker_display"]) == notes.extract_context(plain, c["id"], data["speaker_display"])
    # 畳み戻し無し(chunk idの正規表現で除外する案)なら地の文が欠落して文脈が変わる=adapterの必要性
    no_fold = [c for c in plain if c["id"] != nar["id"]]
    assert len(no_fold) == len(plain) - 1


def test_m6_allowed_names_is_per_story_not_global():
    """validate_emotion_items の許可語は引数(グローバルALLOWED_NAMESではない)。同じ入力でstory別の許可語により判定が変わる。"""
    ctx = {"clip_id": "c1", "speaker": "a", "speaker_display": "A", "text": "Hello there.", "prev_dialogue": [], "next_dialogue": [],
           "narration_before": "He waited.", "narration_after": "", "stage_direction_sentences": [], "manner_words": [], "voice": "v", "part": 1}
    item = {"clip_id": "c1", "speaker_state": "He is calm, as Zorro would be.", "scene": "A quiet room.", "reaction_to_previous": "",
            "evidence": ["Hello there."], "has_explicit_cue": True}
    r_no = notes.validate_emotion_items([item], [ctx], set())["c1"]
    r_yes = notes.validate_emotion_items([item], [ctx], {"zorro"})["c1"]
    assert r_no["status"] == "DISCARDED" and any(x.startswith("new_proper_noun") for x in r_no["discard_reasons"])
    assert r_yes["status"] == "ACCEPTED"


def test_11_no_trial_module_import_or_trial_temp_mechanisms():
    """Trial一時機構(er118 import / use_case / configure_case / PHASE1_GO / redirect_production_sinks / setattr(t,)を本番moduleへ持ち込まない。"""
    for fn in ("er122_fz_ctx_notes_01.py", "er122_fz_ctx_policy_01.py"):
        src = open(_p(fn), encoding="utf-8").read()
        tree = ast.parse(src)
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                assert not any(a.name.startswith("er118") for a in n.names), fn
            if isinstance(n, ast.ImportFrom):
                assert not (n.module or "").startswith("er118"), fn
        for banned in ("use_case(", "configure_case(", "PHASE1_GO", "redirect_production_sinks", "setattr(t,"):
            assert banned not in src, (fn, banned)


def _ctx_for_validation(text="I am here.", before="She whispered softly.", after=""):
    return {"clip_id": "c1", "speaker": "a", "speaker_display": "A", "text": text, "prev_dialogue": [], "next_dialogue": [],
            "narration_before": before, "narration_after": after, "stage_direction_sentences": [before] if before else [], "manner_words": ["softly", "whisper"],
            "voice": "v", "part": 1}


def test_16_three_valued_deterministic_acceptance():
    ctx = _ctx_for_validation()
    good = {"clip_id": "c1", "speaker_state": "She is quiet and careful.", "scene": "A room at night.", "reaction_to_previous": "",
            "evidence": ["She whispered softly."], "has_explicit_cue": True}
    nocue = {"clip_id": "c1", "speaker_state": "Plain.", "scene": "A room at night.", "reaction_to_previous": "", "evidence": [], "has_explicit_cue": False}
    bad_quote = {**good, "evidence": ["She shouted loudly at him."]}
    intensity = {**good, "speaker_state": "She is devastated."}
    ok = notes.validate_emotion_items([good], [ctx], set())["c1"]
    nc = notes.validate_emotion_items([nocue], [ctx], set())["c1"]
    bq = notes.validate_emotion_items([bad_quote], [ctx], set())["c1"]
    iw = notes.validate_emotion_items([intensity], [ctx], set())["c1"]
    miss = notes.validate_emotion_items([], [ctx], set())["c1"]
    assert (ok["status"], nc["status"], bq["status"], iw["status"], miss["status"]) == ("ACCEPTED", "NO_EXPLICIT_CUE", "DISCARDED", "DISCARDED", "DISCARDED")
    # CONTEXT blockへの反映: ACCEPTED=state/scene行あり、NO_EXPLICIT_CUE=scene行のみ、DISCARDED=LLM由来行なし
    b_ok, b_nc, b_bq = (notes.build_context_block(ctx, x) for x in (ok, nc, bq))
    assert "Speaker's state of mind:" in b_ok and "Scene:" in b_ok
    assert "Speaker's state of mind:" not in b_nc and "Scene: A room at night." in b_nc
    assert "Speaker's state of mind:" not in b_bq and "Scene:" not in b_bq and "Speaker of this line: A." in b_bq


def test_16b_story_data_fallback_for_trial_unverified_story_records_source():
    d = notes.story_data("after_twenty_years", ["bob", "patrolman", "detective"])
    assert d["title_source"] == "fallback_key_title"
    assert set(d["speaker_display_source"]) == {"bob", "patrolman", "detective"}
    assert all(v in ("attr_roster_text", "fallback_key_title") for v in d["speaker_display_source"].values())
    assert {"bob", "patrolman", "detective"} <= d["allowed_names"]      # 話者key tokenは許可語(誤DISCARD=中立化の方向=安全側)
    t = notes.story_data("the_monkeys_paw", ["morris", "whoever"])
    assert t["speaker_display"]["morris"] == "the retired sergeant-major" and "whites" in t["allowed_names"]
    assert t["speaker_display_source"] == {"morris": "trial_verified", "whoever": "fallback_key_title"}


def _clips3():
    return [{"id": "full_story_part1_c1", "speaker": "narrator", "voice_role": "narrator", "text": "It was night. She whispered softly.", "part": 1, "voice": "N"},
            {"id": "full_story_part1_c2", "speaker": "della", "voice_role": "dialogue:della", "text": "I am here.", "part": 1, "voice": "V"},
            {"id": "full_story_part1_c3", "speaker": "jim", "voice_role": "dialogue:jim", "text": "Are you?", "part": 1, "voice": "W"}]


def _fake_llm(calls, fail_times=0):
    state = {"i": 0}

    def fn(developer, user):
        calls.append((developer, user))
        state["i"] += 1
        if state["i"] <= fail_times:
            raise RuntimeError("transport error")
        return {"raw": {"items": [
            {"clip_id": "full_story_part1_c2", "speaker_state": "She is quiet.", "scene": "A room at night.", "reaction_to_previous": "",
             "evidence": ["She whispered softly."], "has_explicit_cue": True},
            {"clip_id": "full_story_part1_c3", "speaker_state": "Plain.", "scene": "A room.", "reaction_to_previous": "", "evidence": [], "has_explicit_cue": False}]},
            "model_returned": "gpt-6-luna-x", "cost_jpy": 0.1}
    return fn


def test_14_notes_saved_once_and_reused_zero_llm(tmp_path):
    calls = []
    notes.LLM_FN = _fake_llm(calls)
    ld = str(tmp_path / "run" / "a2")
    p1 = notes.get_provider(ld, "the_gift_of_the_magi", _clips3())
    s2 = p1.style_for("full_story_part1_c2")
    p1.style_for("full_story_part1_c3")
    assert len(calls) == 1 and s2["note_status"] == "ACCEPTED"
    assert os.path.exists(os.path.join(ld, notes.NOTES_RELPATH))
    # 別プロセス相当(providerを作り直す)でも保存済みを再利用 -> LLM 0
    notes.reset_providers_for_test()
    p2 = notes.get_provider(ld, "the_gift_of_the_magi", _clips3())
    s2b = p2.style_for("full_story_part1_c2")
    assert len(calls) == 1 and s2b["style_sha256"] == s2["style_sha256"]
    # 本文が変わった場合はlevel単位でLLM 1 call(Opus R-2)。旧notesは.prevへ
    changed = _clips3()
    changed[1]["text"] = "I am here now."
    notes.reset_providers_for_test()
    p3 = notes.get_provider(ld, "the_gift_of_the_magi", changed)
    p3.style_for("full_story_part1_c2")
    assert len(calls) == 2 and os.path.exists(os.path.join(ld, notes.NOTES_RELPATH) + ".prev")


def test_m7_llm_failure_after_one_retry_is_technical_stop_and_resumable(tmp_path):
    ld = str(tmp_path / "run" / "b1b")
    calls = []
    notes.LLM_FN = _fake_llm(calls, fail_times=99)
    p = notes.get_provider(ld, "the_gift_of_the_magi", _clips3())
    import er063_family_z_audio_01 as z
    with pytest.raises(z.FamilyZDialogueCtxStop) as ei:
        p.style_for("full_story_part1_c2")
    assert isinstance(ei.value, z.FamilyZAudioStop) and len(calls) == 2         # 初回+1回再試行
    assert not os.path.exists(os.path.join(ld, notes.NOTES_RELPATH))            # 中立notesを保存して続行していない
    # 再開: 次回は成功。全clip中立の退化状態を作らない
    notes.reset_providers_for_test()
    calls2 = []
    notes.LLM_FN = _fake_llm(calls2)
    s = notes.get_provider(ld, "the_gift_of_the_magi", _clips3()).style_for("full_story_part1_c2")
    assert s["note_status"] == "ACCEPTED" and len(calls2) == 1


def test_m7_one_failure_then_success_uses_retry(tmp_path):
    calls = []
    notes.LLM_FN = _fake_llm(calls, fail_times=1)
    p = notes.get_provider(str(tmp_path / "run" / "a2"), "the_gift_of_the_magi", _clips3())
    s = p.style_for("full_story_part1_c2")
    assert len(calls) == 2 and s["note_status"] == "ACCEPTED"


def test_missing_item_stays_discarded_and_run_continues(tmp_path):
    """個別項目の欠落(missing_item)は既存のDISCARDED処理のまま続行(技術STOPにしない)。"""
    def fn(developer, user):
        return {"raw": {"items": [{"clip_id": "full_story_part1_c3", "speaker_state": "Plain.", "scene": "", "reaction_to_previous": "", "evidence": [],
                                   "has_explicit_cue": False}]}, "model_returned": "gpt-6-luna", "cost_jpy": 0.0}
    notes.LLM_FN = fn
    p = notes.get_provider(str(tmp_path / "run" / "a2"), "the_gift_of_the_magi", _clips3())
    s = p.style_for("full_story_part1_c2")
    assert s["note_status"] == "DISCARDED" and "Speaker's state of mind:" not in s["style"]


def test_base_style_sha_fail_closed(monkeypatch):
    import er003_b1_p9a_audio as p9a
    import er063_family_z_audio_01 as z
    assert notes.sha_text(p9a.ENGLISH_STYLE_PREFIX) == notes.EXPECTED_BASE_STYLE_SHA
    monkeypatch.setattr(p9a, "ENGLISH_STYLE_PREFIX", p9a.ENGLISH_STYLE_PREFIX + " x")
    with pytest.raises(z.FamilyZDialogueCtxStop):
        notes.base_style()


def test_leakage_is_observation_only_and_never_flags_orthographic_variants():
    """ASRの表記違い(three/3 等)だけでflagしない。leakage検査自体が観測のみ(NG理由にしない)。"""
    ctx = _ctx_for_validation(text="The paw gives 3 wishes.")
    r = notes.leakage_check("The paw gives three wishes.", ctx, None)
    assert r["flagged"] is False
    allr = notes.leakage_all_attempts(["The paw gives three wishes."], "The paw gives three wishes.", ctx, None)
    assert allr["observation_only"] is True and allr["leakage_final"] is False


def test_story_key_resolution_keeps_trial_data_for_custom_slug():
    """runnerは story_key=--slug を渡す。既知storyの接頭辞/接尾辞を持つslug(複製run等)でもTrial検証済みdataを使い、黙ってfallbackに落ちない。"""
    assert notes.resolve_story_key("melos") == "melos"
    assert notes.resolve_story_key("melos_chunk01") == "melos"
    assert notes.resolve_story_key("the_monkeys_paw") == "the_monkeys_paw"
    assert notes.resolve_story_key("run2_the_open_window") == "the_open_window"
    assert notes.resolve_story_key("totally_unknown_story") == "totally_unknown_story"
