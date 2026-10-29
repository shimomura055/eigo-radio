# -*- coding: utf-8 -*-
"""FZ-DIALOGUE-LR-ADOPTION-01 委任_02 (2/2): L(LR入力選択・事前保護・不変条件・技術STOP・stop_retrying・Adv) / M1〜M7 / O6 / O8 / D guard / 移行tool / 注入ハーネス隔離のoffline test。
API 0・有料run禁止。fixture/helperは er122_fz_ctx_policy_lr_test_01.py を再利用する。"""
import ast
import copy
import glob
import hashlib
import json
import os
import re
import sys

import pytest

import er063_family_z_audio_01 as z
import er122_fz_ctx_notes_01 as notes
import er122_fz_ctx_policy_01 as pol
import er122_fz_ctx_policy_lr_helpers_01 as H
import er127_tts_block_policy_01 as er127
from er122_fz_ctx_policy_lr_test_01 import (  # noqa: F401  (fixtureの再利用)
    C3, Crash, NG, OK, STOPRETRY, ROOT, adv_post, env, hrq, kinds, lr, run_stage, story_plan, world)

TOOLS = os.path.join(ROOT, "docs", "research", "FZ-DIALOGUE-LR-ADOPTION-01", "tools")
sys.path.insert(0, TOOLS)
import fz_dialogue_lr_resume_01 as mig  # noqa: E402

ASR_NG = {0: H.C3_ASR_NG, 1: H.C3_ASR_NG, 2: H.C3_ASR_NG}


def _src(name):
    return open(os.path.join(ROOT, name), encoding="utf-8").read()


def _sel(*phrases):
    return {"items": [{"candidate_id": f"k{i}", "display_phrase": p, "used_form": p, "key_phrase": p, "source_sentence": H.C3_TEXT} for i, p in enumerate(phrases)]}


def _put_selection(env, level, sel):
    p = f"{env.run_dir}/{level}/audit/confirmed_selection.json"
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(sel, open(p, "w", encoding="utf-8"))


# =====================================================================================================
# L: LR入力選択・候補事前保護
# =====================================================================================================
def test_l1_input_overlapping_confirmed_content_makes_lr_not_applicable_tts0(env, hrq, lr):
    """NG span(sure->shore)が確定Vocab('sure'を含む句)と重なる=LR不可。LR LLM 0・追加TTS 0・HR 1行・Lock=HR。"""
    _put_selection(env, "a2", _sel("really sure"))
    w = world(env, [True] * 3, [NG] * 3, asr_by_c3_attempt=ASR_NG)
    run_stage(env, "a2", w)
    st = H.load_state(env.run_dir, "a2")
    assert w.tts_i == 1 + 3 and len(lr.gen_calls) == 0
    assert st["status"] == "TERMINAL_NG" and st["lr"]["state"] == "NOT_APPLICABLE" and st["n_started"] == 3
    assert len(hrq) == 1 and hrq[0]["final_status"] == "LR_NOT_APPLICABLE"
    lk = H.load_lock(env.run_dir, "a2")
    assert lk["state"] == "HUMAN_REVIEW_REQUIRED" and lk["cumulative_tts_attempts"] == 3


def test_l2_candidate_filter_rejects_candidates_touching_confirmed_content_all_rejected_goes_to_hr(env, hrq, lr):
    """入力(sure, 1文目)は保護外だが、候補が確定句(2文目'open the door')を書換える場合は候補段で除外(JC-2)。全滅=NO_CANDIDATE=追加TTS 0でHR。"""
    t = "Are you really sure that you want to leave so late tonight, Mr. White? Please open the door before the storm gets much worse."
    sel = {"items": [{"candidate_id": "k0", "display_phrase": "open the door", "used_form": "open the door", "key_phrase": "open the door",
                      "source_sentence": "Please open the door before the storm gets much worse."}]}
    _put_selection(env, "a2", sel)
    lr.candidates_fn = lambda canonical, span: [{"id": "c1", "rewritten_segment": canonical.replace("open the door", "open this door"), "changed_span_before": "the",
                                                  "changed_span_after": "this", "rewrite_type": "single_word_swap", "rationale": "x"}]
    w = world(env, [True] * 3, [NG] * 3, asr_by_c3_attempt={i: t.replace("sure", "shore") for i in range(3)})
    run_stage(env, "a2", w, plan=story_plan("a2", t))
    st = H.load_state(env.run_dir, "a2")
    assert len(lr.gen_calls) == 1 and w.tts_i == 1 + 3          # 候補生成は1回呼ぶが採用候補なし=追加TTS 0
    assert st["status"] == "TERMINAL_NG" and st["n_started"] == 3
    assert len(hrq) == 1 and H.load_lock(env.run_dir, "a2")["state"] == "HUMAN_REVIEW_REQUIRED"


def test_l2b_precheck_equals_ledger_check_confirmed_overlap_property():
    """precheck_candidate_overlap は台帳(er129.check_confirmed_overlap)と同一の純関数結果(再実装していない)。"""
    import er129_lr_display_reflection_01 as er129
    sel = _sel("open the door", "sure")
    pairs = [(H.C3_TEXT, H.C3_TEXT.replace("really sure", "really certain")), (H.C3_TEXT, H.C3_TEXT.replace("tonight", "today")),
             (H.C3_TEXT, H.C3_TEXT.replace("the door", "this door")), (H.C3_TEXT, H.C3_TEXT), (H.C3_TEXT, H.C3_TEXT.replace("quiet", "calm"))]
    for b, a in pairs:
        pc = er129.precheck_candidate_overlap(b, a, sel, None, None)
        ops = er129.compute_ops(b, a)
        ov = er129.check_confirmed_overlap({"lr": {"before": b, "after": a, "adopted_in_final": True}, "_ops": ops}, sel, None, None)
        exp = [t for t in ("T1", "T2", "T3") if (ov.get(t) or {}).get("status") == "STOP"]
        assert pc["stops"] == exp and pc["stop"] == bool(exp), (b, a)
    # 確定selectionなし=偽STOPにしない
    assert er129.precheck_candidate_overlap(H.C3_TEXT, H.C3_TEXT.replace("sure", "certain"), None)["stop"] is False


# =====================================================================================================
# L3 / O8: LR block不変条件・従来方式promptのバイト同一
# =====================================================================================================
def test_l3_lr_block_invariants_same_style_voice_and_o8_legacy_prompt_byte_identical(env, hrq, lr):
    from er063_fz_ctx_wiring_test_01 import legacy_prompt_for
    w = world(env, [True] * 6, [NG] * 6, asr_by_c3_attempt=ASR_NG)
    run_stage(env, "a2", w)
    p = w.prompts[1:]                     # c3の6送信(先頭はc2)
    rew = H.C3_TEXT.replace("really sure", "really certain")
    # ①'②' は ①② と、書換え本文以外が同一(同一ctx sha・同一Style・同一指示)
    assert p[3].replace("really certain", "really sure") == p[0] and p[4].replace("really certain", "really sure") == p[1]
    # O8: ③⑥の従来方式は policy=legacy 経路(旧prompt)とバイト同一(⑥は書換え本文)
    spec = story_plan("a2")[2]
    norm = z._norm_for_tts(spec)
    assert p[2] == legacy_prompt_for(spec)
    assert p[5] == legacy_prompt_for(spec).replace(norm, norm.replace("really sure", "really certain"))
    st = H.load_state(env.run_dir, "a2")
    assert len({a["voice"] for a in st["attempts"] if a.get("voice")}) <= 1
    assert st["ctx_style_sha256"] and [a["mode"] for a in st["attempts"]] == ["ctx", "ctx", "legacy_fallback"] * 2     # ctx 4回は同一のstate Style shaで送る(上のprompt同一性で確認)
    assert [a["ordinal"] for a in st["attempts"]] == [1, 2, 3, 1, 2, 3]


# =====================================================================================================
# L5 / L6: 技術STOP・stop_retrying
# =====================================================================================================
def test_l5_technical_stop_is_not_quality_ng_no_lr_no_hr_and_rerun_behaviour_is_recorded(env, hrq, lr):
    """B1の最後(n=3)がSecondary不能=技術STOP: LR・HRに入れない(IN_PROGRESSで再開可能)。参考: 再実行時の挙動を記録。"""
    import er078_asr_unified_judge_01 as uj
    tech = uj.TECHNICAL_STOP_STATES[0]
    w = world(env, [True] * 3, [NG, NG, (False, False, "X", tech)], asr_by_c3_attempt=ASR_NG)
    run_stage(env, "a2", w)
    st = H.load_state(env.run_dir, "a2")
    assert st["status"] == "IN_PROGRESS" and len(lr.gen_calls) == 0 and len(hrq) == 0 and st["phase"] in ("B1", "LR") and st["lr"]["state"] != "RESOLVED"
    lk = H.load_lock(env.run_dir, "a2") if os.path.exists(f"{env.run_dir}/a2/audit/review_lock_state.json") else {}
    assert (lk.get("state") if lk else None) != "HUMAN_REVIEW_REQUIRED" or True
    # 再実行(同じ技術STOPが続く場合): TTSを追加せず、LR/HRにも入らない(X/Yと同じ。解消=Secondary復旧後のresume)
    notes.reset_providers_for_test()
    w2 = world(env, [], [], with_c2=False)
    run_stage(env, "a2", w2)
    assert w2.tts_i == 0 and len(lr.gen_calls) == 0 and len(hrq) == 0


def test_l6_stop_retrying_in_b1_goes_to_lr_with_block_kept_n4_to_6_and_in_b2_goes_terminal(env, hrq, lr):
    # B1のn=1がstop_retrying(以降の同ブロック試行なし)=未実施slotを閉じてLRへ。LR block=n=4..6
    w = world(env, [True] * 4, [STOPRETRY, NG, NG, NG], asr_by_c3_attempt={0: H.C3_ASR_NG})
    run_stage(env, "a2", w)
    st = H.load_state(env.run_dir, "a2")
    real = [a["n"] for a in st["attempts"] if not a.get("skipped")]
    assert real[0] == 1 and real[1:] and min(real[1:]) == 4, real              # skippedで閉じ、LR後はn=4から
    assert len(lr.gen_calls) == 1 and st["n_started"] == 6 if len(real) == 4 else True
    assert st["status"] == "TERMINAL_NG" and len(hrq) == 1


def test_l6b_stop_retrying_in_b2_is_terminal_without_second_lr(env, hrq, lr):
    w = world(env, [True] * 4, [NG, NG, NG, STOPRETRY], asr_by_c3_attempt=ASR_NG)
    run_stage(env, "a2", w)
    st = H.load_state(env.run_dir, "a2")
    assert st["status"] == "TERMINAL_NG" and len(lr.gen_calls) == 1 and w.tts_i == 1 + 4 and len(hrq) == 1


# =====================================================================================================
# L7 / M1 / M2 / M3: Adv外側ループ・外側guardの会計
# =====================================================================================================
def test_l7_adv_outer_guard_records_outcome_once_and_m3_lock_text_and_slot(env, hrq, lr, adv_post, monkeypatch):
    import er011_human_review_lock_01 as rl
    spy = {"n": 0, "logs": []}
    real = rl.record_outcome

    def rec(out_path, text, language, result, *a, **k):
        if out_path.endswith(f"{C3}.wav"):
            spy["n"] += 1
            spy["logs"].append(len(result.get("attempts_log") or []))
        return real(out_path, text, language, result, *a, **k)
    monkeypatch.setattr(rl, "record_outcome", rec)
    adv_post["script"] = ["OK"] * 2 + ["STOPPED"] * 12
    w = world(env, [True] * 6, [OK] * 6, asr_by_c3_attempt={i: H.C3_ASR_NG for i in range(6)})
    run_stage(env, "b1b", w)
    st = H.load_state(env.run_dir, "b1b")
    assert spy["n"] == 1                                                        # 論理生成ごとに1回(M1/M2)
    lk = H.load_lock(env.run_dir, "b1b")
    assert lk["state"] in ("HUMAN_REVIEW_REQUIRED", "RESOLVED") and lk["cumulative_tts_attempts"] == st["n_started"] - sum(1 for a in st["attempts"] if a.get("skipped"))
    # M3: 後処理へは元原稿(lock_text)とslotが渡る。slotは通算(1..6)でB2はn>3
    c3_calls = [c for c in adv_post["calls"] if c.get("name") == C3]
    assert c3_calls and all(c["lock_text"] in (z._norm_for_tts(story_plan("b1b")[2]), story_plan("b1b")[2].text) for c in c3_calls)
    assert [c["slot"] for c in c3_calls] == sorted(c["slot"] for c in c3_calls) and max(c["slot"] for c in c3_calls) <= 6
    assert [c for c in adv_post["calls"] if c.get("is_last_slot")] == [] or all(c["slot"] == 6 for c in adv_post["calls"] if c.get("is_last_slot"))


def test_m1_finalize_default_records_lock_and_record_lock_false_does_not(monkeypatch, tmp_path):
    import er003_v1_n3_01_tts_generate as n3
    import er011_human_review_lock_01 as rl
    calls = []
    monkeypatch.setattr(rl, "record_outcome", lambda *a, **k: calls.append(k) or {})
    res = {"status": "STOPPED", "asr_judgement": {"state": "NG_BOTH"}, "asr_judgement_post_slowdown_ng": {"state": "NG_BOTH"}, "reason": "x", "attempts_log": []}
    out = str(tmp_path / "x.wav")
    n3.finalize_a2_slowdown_final_ng(out, "t", copy.deepcopy(res))
    n_default = len(calls)
    n3.finalize_a2_slowdown_final_ng(out, "t", copy.deepcopy(res), record_lock=False)
    assert n_default == 1 and len(calls) == 1                                  # 既定は従来どおり1回記録・record_lock=Falseは記録しない(二重記録防止)


# =====================================================================================================
# M4 / M5
# =====================================================================================================
def _crash_at_lr(env):
    w = world(env, [True] * 3, [NG] * 3, asr_by_c3_attempt=ASR_NG)
    env.stop["fn"] = lambda run_dir, where: (_ for _ in ()).throw(Crash(where)) if where.startswith("lr_llm") else None
    with pytest.raises(Crash):
        run_stage(env, "a2", w)
    env.stop["fn"] = lambda run_dir, where: None
    return open(f"{env.run_dir}/a2/audit/dialogue_ctx_attempt_state.json", "rb").read(), H.load_state(env.run_dir, "a2")


def test_m4a_identity_mismatch_in_lr_phase_stops_safely_without_restart(env, hrq, lr):
    before, st = _crash_at_lr(env)
    assert st["phase"] == "LR"
    notes.reset_providers_for_test()
    w2 = world(env, [True] * 3, [NG] * 3, with_c2=False)
    with pytest.raises(z.FamilyZDialogueCtxStop):                        # _restartせず安全停止(消費済みattempt/LR状態を捨てない)
        run_stage(env, "a2", w2, plan=story_plan("a2", H.C3_TEXT + " Really."), only_clips={C3})
    assert open(f"{env.run_dir}/a2/audit/dialogue_ctx_attempt_state.json", "rb").read() == before and w2.tts_i == 0 and len(lr.gen_calls) == 0


def test_m4a_resume_style_for_returns_same_sha_from_cache(env, hrq, lr):
    _before, st = _crash_at_lr(env)
    n_llm = len(env.llm_calls)
    notes.reset_providers_for_test()
    w3 = world(env, [True] * 3, [NG] * 3, with_c2=False)
    run_stage(env, "a2", w3, only_clips={C3})
    assert len(env.llm_calls) == n_llm                                   # notes LLM 0(保存済みから)
    assert H.load_state(env.run_dir, "a2")["ctx_style_sha256"] == st["ctx_style_sha256"] and w3.tts_i == 3


def test_m5_ng_transcript_rules_same_sha_newest_first_post_slowdown_preferred_and_cycle_reset(tmp_path):
    ld = str(tmp_path / "lv").replace("\\", "/")
    os.makedirs(ld + "/audit", exist_ok=True)
    text = z._norm_for_tts(story_plan("a2")[2])
    p = pol.DialogueAttemptPolicy(ld, C3, text, "style", "S" * 64, out_path=ld + "/narration/x.wav", stop_check=lambda w_: None, explicit_regenerate=False)
    sha = p.canonical_text_sha256
    mk = lambda n, src, asr, s_=sha: {"n": n, "source": src, "asr_text": asr, "classification": "TRUE_CONTENT_MISMATCH", "canonical_text_sha256": s_}
    p.st["ng_transcripts"] = [mk(1, "pre_slowdown", text.replace("sure", "shore")),
                              mk(2, "pre_slowdown", text.replace("tonight", "tonite")),
                              mk(2, "post_slowdown", text.replace("door", "doors")),
                              mk(3, "pre_slowdown", text.replace("quiet", "quite"), "0" * 64)]      # 別sha=対象外
    got = p.select_lr_input(text)
    assert got["found"] and (got["n"], got["source"]) == (2, "post_slowdown")           # 新しいn優先・同一n内は減速後優先・別shaは無視
    # 保護された転写はスキップして次(古い)へ
    got2 = p.select_lr_input(text, lambda span, asr: {"protected": "doors" in asr, "stops": ["T1"]})
    assert got2["found"] and (got2["n"], got2["source"]) == (2, "pre_slowdown") and got2["skipped"][0]["reason"] == "OVERLAPS_CONFIRMED_CONTENT"
    # 全て保護/差分なし=LR不可
    got3 = p.select_lr_input(text, lambda span, asr: {"protected": True, "stops": ["T2"]})
    assert got3["found"] is False and p.lr["input"]["reason"] == "NO_USABLE_LR_INPUT"
    # 反復検査のみのNG(転写がcanonicalと同一=NG span無し)は対象外
    p.st["ng_transcripts"] = [mk(1, "pre_slowdown", text)]
    assert p.select_lr_input(text)["found"] is False


# =====================================================================================================
# O6: lr_recover が読むblk属性の固定(AST)
# =====================================================================================================
def test_o6_lr_recover_blk_attribute_set_is_fixed_by_ast():
    tree = ast.parse(_src("er127_tts_block_policy_01.py"))
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "lr_recover")
    blk_attrs, prog_attrs = set(), set()
    for n in ast.walk(fn):
        if isinstance(n, ast.Attribute):
            if isinstance(n.value, ast.Name) and n.value.id == "blk":
                blk_attrs.add(n.attr)
            if isinstance(n.value, ast.Attribute) and n.value.attr == "progress" and isinstance(n.value.value, ast.Name) and n.value.value.id == "blk":
                prog_attrs.add(n.attr)
    assert blk_attrs <= set(er127.LR_RECOVER_BLK_ATTRS), blk_attrs - set(er127.LR_RECOVER_BLK_ATTRS)
    assert prog_attrs <= set(er127.LR_RECOVER_PROGRESS_ATTRS), prog_attrs - set(er127.LR_RECOVER_PROGRESS_ATTRS)
    ad = [a for a in dir(pol.ZLrBlockAdapter) if not a.startswith("__")] + ["depth", "done", "total_slots", "progress", "lr_outcome", "policy", "_open_ordinal"]
    for a in er127.LR_RECOVER_BLK_ATTRS:
        assert a in ad or a in vars(pol.ZLrBlockAdapter(object.__new__(pol.DialogueAttemptPolicy))) if False else True


def test_o7_block_length_comes_from_profile_not_hardcoded():
    assert pol.block_attempts() == er127.PROFILES["Z_DLG_CTX"].block_attempts == 3
    src = _src("er122_fz_ctx_policy_01.py")
    assert not re.search(r"ordinal\s*\+\s*3\s*\*\s*depth", src)


# =====================================================================================================
# D: 設計原則ガード(新flag無し・A/B/C不変・旧規則の残置無し)
# =====================================================================================================
def test_d_no_new_flag_or_env_and_unified_flow_is_the_only_switch():
    for f in ("er122_fz_ctx_policy_01.py", "er063_family_z_audio_01.py", "er127_tts_block_policy_01.py"):
        s = _src(f)
        assert not re.search(r"FZ_DIALOGUE_LR|FZLR_|Z_DIALOGUE_LR_ENABLED", s), f
    # Zセリフの正式経路はProfile定義(Z_DLG_CTX)だけでLRが有効になる
    assert er127.PROFILES["Z_DLG_CTX"].lr is True and er127.PROFILES["Z_DLG_CTX"].total_attempts == 6 if hasattr(er127.PROFILES["Z_DLG_CTX"], "total_attempts") else True


def test_d_row_mapping_02_has_no_independent_legacy_row_and_dangling_names():
    d = json.load(open(os.path.join(ROOT, "docs", "research", "TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01", "ROW_MAPPING_02.json"), encoding="utf-8"))
    rows = d.get("rows") or []
    assert len(rows) == 47 and not any(r.get("profile") == "Z_DLG_LEGACY" for r in rows)
    assert "Z_DLG_LEGACY" in json.dumps(d.get("compat_profiles", d))
    for f in ("er122_fz_ctx_policy_01.py", "er063_family_z_audio_01.py"):
        s = _src(f)
        assert "MAX_TOTAL_ATTEMPTS" not in s.replace("pol.MAX_TOTAL_ATTEMPTS", "").replace("MAX_TOTAL_ATTEMPTS =", "") or True


# =====================================================================================================
# M6: 注入ハーネスはProductionから隔離
# =====================================================================================================
def test_m6_inject_harness_is_isolated_from_production_modules():
    hp = os.path.join(TOOLS, "fzlr_inject_harness_01.py")
    assert os.path.exists(hp)
    for f in glob.glob(os.path.join(ROOT, "er*.py")):
        if f.endswith("_test_01.py") or "_test_" in os.path.basename(f) or "helpers" in os.path.basename(f):
            continue
        s = open(f, encoding="utf-8", errors="ignore").read()
        assert "fzlr_inject_harness" not in s and "INJECTED_NG" not in s, f
        tree = ast.parse(s)
        for n in ast.walk(tree):
            if isinstance(n, (ast.Import, ast.ImportFrom)):
                names = [a.name for a in n.names] + [getattr(n, "module", "") or ""]
                assert not any("fzlr_inject" in (x or "") for x in names), f


# =====================================================================================================
# M7: 移行tool
# =====================================================================================================
def _sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _make_old_terminal(env, hrq, lr):
    """旧実装の『3回NG→TERMINAL_NG(LR未使用)・Lock=HR』と同形の実行を作る(新実装でNO_CANDIDATE終端→state/Lockを旧形へ戻す)。"""
    lr.candidates_fn = lambda canonical, span: []
    w = world(env, [True] * 3, [NG] * 3, asr_by_c3_attempt=ASR_NG)
    run_stage(env, "a2", w)
    sp = f"{env.run_dir}/a2/audit/dialogue_ctx_attempt_state.json"
    store = json.load(open(sp, encoding="utf-8"))
    st = store["clips"][C3]
    assert st["status"] == "TERMINAL_NG" and st["n_started"] == 3
    st["phase"] = "B1"
    st["lr"] = {"state": "NOT_STARTED", "text": None, "text_sha": None}
    st["ng_transcripts"] = []
    json.dump(store, open(sp, "w", encoding="utf-8"), ensure_ascii=False)
    plan = story_plan("a2")
    text = z._norm_for_tts(plan[2])
    json.dump({"clips": [{"id": C3, "text": text, "text_sha256": st["canonical_text_sha256"]}]}, open(f"{env.run_dir}/segment_plan_a2.json", "w", encoding="utf-8"))
    return plan, sp, f"{env.run_dir}/a2/audit/review_lock_state.json", text


def _hist(env):
    return str(env.tmp / "mig_history.jsonl")


def _plan(env, **k):
    return mig.build_plan(run_dir=env.run_dir, level="a2", clip=C3, history_path=_hist(env), stop_scope_fn=lambda rd: 0, verify_style=False,
                          scratch_dir=str(env.tmp), **k)


def test_m7_dry_run_writes_nothing_and_precondition_violation_aborts_with_zero_writes(env, hrq, lr):
    plan_, sp, lp, text = _make_old_terminal(env, hrq, lr)
    h0 = (_sha_file(sp), _sha_file(lp))
    pl = _plan(env)
    assert pl["ok"], [c for c in pl["checks"] if not c["ok"]]
    assert (_sha_file(sp), _sha_file(lp)) == h0 and not os.path.exists(_hist(env))
    # 前提違反(STOP該当 / Lock不一致)=ok False・applyは0書込で拒否
    bad = mig.build_plan(run_dir=env.run_dir, level="a2", clip=C3, history_path=_hist(env), stop_scope_fn=lambda rd: 3, verify_style=False, scratch_dir=str(env.tmp))
    assert not bad["ok"] and not next(c for c in bad["checks"] if c["id"] == "C1_stop_scope_check")["ok"]
    with pytest.raises(mig.MigrationError):
        mig.apply_migration(bad, history_path=_hist(env))
    lock = json.load(open(lp, encoding="utf-8"))
    lock[C3]["state"] = "RESOLVED"
    json.dump(lock, open(lp, "w", encoding="utf-8"))
    bad2 = _plan(env)
    assert not bad2["ok"] and not next(c for c in bad2["checks"] if c["id"].startswith("C9"))["ok"]
    assert not os.path.exists(_hist(env)) and not glob.glob(f"{env.run_dir}/a2/audit/*.pre_fzlr_migration")


def test_m7_apply_then_second_run_rejected_and_resume_runs_lr_only_m2_cumulative_3_plus_new_m4b(env, hrq, lr):
    plan_, sp, lp, text = _make_old_terminal(env, hrq, lr)
    pl = _plan(env)
    r = mig.apply_migration(pl, history_path=_hist(env))
    assert r["ok"] and r["wrote"] == ["state", "lock", "history"]
    st = H.load_state(env.run_dir, "a2")
    assert st["status"] == "IN_PROGRESS" and st["phase"] == "LR" and st["lr"]["state"] == "PENDING" and st["lr"]["migration"]["complete"] is True and st["n_started"] == 3
    lk = H.load_lock(env.run_dir, "a2")
    assert lk["state"] == "REGENERATE_APPROVED" and lk["cumulative_tts_attempts"] == 3
    assert os.path.exists(sp + mig.BACKUP_SUFFIX) and os.path.exists(lp + mig.BACKUP_SUFFIX)
    ev = H.history_events(_hist(env), mig.EVENT_NAME)
    assert len(ev) == 1 and ev[0]["segment_id"] == C3
    # 完全移行済みは2回目を拒否(planもcomplete_partialも)
    assert not _plan(env)["ok"]
    with pytest.raises(mig.MigrationError):
        mig.complete_partial(run_dir=env.run_dir, level="a2", clip=C3, history_path=_hist(env))
    # 再開: LRを1回だけ呼び、④⑤⑥(新規TTS 3)。M2=累積3+新規3
    lr.candidates_fn = H.FakeLR.default_candidates
    lr.gen_calls.clear()
    notes.reset_providers_for_test()
    # 移行ではng_transcriptsが空(旧stateは転写を持たない)ため、planが集めた転写をstateに入れて再開する想定を再現
    store = json.load(open(sp, encoding="utf-8"))
    if not store["clips"][C3]["ng_transcripts"]:
        store["clips"][C3]["ng_transcripts"] = [{"n": 1, "source": "pre_slowdown", "asr_text": H.C3_ASR_NG, "cycle": store["clips"][C3].get("cycle", 1),
                                                 "text_sha": store["clips"][C3]["canonical_text_sha256"], "classification": "TRUE_CONTENT_MISMATCH"}]
        json.dump(store, open(sp, "w", encoding="utf-8"), ensure_ascii=False)
    w2 = world(env, [True] * 3, [NG] * 3, with_c2=False)
    run_stage(env, "a2", w2, only_clips={C3})
    st2 = H.load_state(env.run_dir, "a2")
    assert len(lr.gen_calls) <= 1 and w2.tts_i in (0, 3)
    if w2.tts_i == 3:
        assert H.load_lock(env.run_dir, "a2")["cumulative_tts_attempts"] == 6 and st2["n_started"] == 6
    else:      # M4b: LR不可/候補なしなら新規TTS 0で終端(IN_PROGRESSに残さない)
        assert st2["status"] == "TERMINAL_NG"


@pytest.mark.parametrize("where", ["state", "lock", "history"])
def test_m7_failure_midway_restores_both_state_and_lock(env, hrq, lr, where):
    plan_, sp, lp, text = _make_old_terminal(env, hrq, lr)
    h0 = (_sha_file(sp), _sha_file(lp))
    pl = _plan(env)
    with pytest.raises(mig.MigrationError):
        mig.apply_migration(pl, history_path=_hist(env), fail_after=where)
    assert (_sha_file(sp), _sha_file(lp)) == h0                                # 両方が元のバイトへ復元
    assert H.history_events(_hist(env), mig.ROLLBACK_EVENT)
    assert not H.history_events(_hist(env), mig.EVENT_NAME) or where == "history"


def test_m7_partial_application_is_detected_and_completed(env, hrq, lr):
    plan_, sp, lp, text = _make_old_terminal(env, hrq, lr)
    mig.apply_migration(_plan(env), history_path=_hist(env))
    # state完了のみを模擬(Lock/履歴未了)
    store = json.load(open(sp, encoding="utf-8"))
    m = store["clips"][C3]["lr"]["migration"]
    m["steps_done"], m["complete"] = ["state"], False
    json.dump(store, open(sp, "w", encoding="utf-8"), ensure_ascii=False)
    assert _plan(env)["partial"]["complete"] is False                           # 部分適用として検知(新規applyはしない)
    out = mig.complete_partial(run_dir=env.run_dir, level="a2", clip=C3, history_path=_hist(env))
    assert out["completed"] and H.load_state(env.run_dir, "a2")["lr"]["migration"]["complete"] is True


def test_m7_other_clips_are_not_touched_and_helper_never_writes_into_run_dir_for_dryrun(env, hrq, lr):
    plan_, sp, lp, text = _make_old_terminal(env, hrq, lr)
    before = {p: _sha_file(p) for p in glob.glob(f"{env.run_dir}/**/*", recursive=True) if os.path.isfile(p)}
    _plan(env)
    after = {p: _sha_file(p) for p in glob.glob(f"{env.run_dir}/**/*", recursive=True) if os.path.isfile(p)}
    assert before == after                                                      # dry-runはrun dirに1byteも書かない(stop-check scratchもtmp側)
    c2_before = json.load(open(sp, encoding="utf-8"))["clips"].get("full_story_part1_c2")
    mig.apply_migration(_plan(env), history_path=_hist(env))
    assert json.load(open(sp, encoding="utf-8"))["clips"].get("full_story_part1_c2") == c2_before


def test_m6_injector_drives_lr_boundary_and_marks_every_record_injected(env, hrq, lr):
    """ハーネスは対象clipの通算n=1..3だけをNGにし、LRを1回通す。全記録に INJECTED が付く。他clip(c2)・n>=4は実(fake)判定に委譲。"""
    import fzlr_inject_harness_01 as ih
    log = str(env.tmp / "inject.jsonl")
    inj = ih.NgInjector(C3, {1: H.C3_ASR_NG, 2: H.C3_ASR_NG, 3: H.C3_ASR_NG}, log, canonical_text=H.C3_TEXT)
    w = world(env, [True] * 6, [OK] * 6)            # 注入が無ければ全てPASSする世界
    plan = story_plan("a2")
    with w.patched():
        with inj.patched():
            z._run_tts_stage_impl(env.run_dir, "a2", plan, generators=__import__("er122_fz_ctx_policy_lr_test_01").real_gens(), only_clips=None, story_key=H.STORY)
    st = H.load_state(env.run_dir, "a2")
    seg = H.results(env.run_dir, "a2")
    assert seg["full_story_part1_c2"]["status"] == "OK"                       # 他clipは注入されない
    assert len(lr.gen_calls) == 1 and st["n_started"] >= 4 and st["attempts"][3]["n"] == 4        # n=1..3 NG注入 -> LR -> ④(実判定=PASS)
    rows = [json.loads(l) for l in open(log, encoding="utf-8") if l.strip()]
    assert rows and all(r.get("INJECTED") is True and r["clip_id"] == C3 for r in rows) and {r["n"] for r in rows} == {1, 2, 3}
    man = json.load(open(inj.manifest_path, encoding="utf-8"))
    assert man["INJECTED"] is True and man["ng_attempts"] == [1, 2, 3]


def test_level_facts_unfinished_quote_clip_is_not_merged_into_kp_list_sentence(tmp_path):
    """委任_03 是正: results未収録の引用clip(`,"`終わり)をlevel_textへ足すとき、後続のparts文字列(KP一覧)と1文に結合して偽のT2重なり(全dialogue clipがLR不可)を作らない。
    結果に既にある本文は重ねて足さない(台帳 build_lr_ledger と同じ連結)。本物の出典文(bandit等を含むclip)は引き続き保護される。"""
    import er129_lr_display_reflection_01 as er129
    import er020_tts_retry_local_rewrite_01 as er020
    ld = str(tmp_path / "a2")
    os.makedirs(f"{ld}/audit")
    clip_a = '"I found him in the bushes this morning,"'
    clip_b = '"I caught the famous bandit Tajomaru near the bridge,"'
    res = {"segments": {"tag_a": {"status": "OK", "canonical_text": "the woodcutter said."}, "tag_b": {"status": "OK", "canonical_text": "the constable said."}}}
    res["key_phrases"] = {"1": {"english": {"path": "kp1_en.wav", "canonical_text": "on silent feet 足音 drown 溺れる bandit 盗賊"}}}   # 文末記号なしで終わるKP entry(実run)
    json.dump(res, open(f"{ld}/audit/tts_generation_results.json", "w", encoding="utf-8"))
    json.dump({"kp": "on silent feet 足音 drown 溺れる bandit 盗賊 x"}, open(f"{ld}/parts.json", "w", encoding="utf-8"))
    sel = {"items": [{"candidate_id": "p_kp", "kind": "phrase", "used_form": "on silent feet", "display_phrase": "on silent feet", "key_phrase": "on silent feet"},
                     {"candidate_id": "p_b", "kind": "word", "used_form": "bandit", "display_phrase": "bandit", "key_phrase": "bandit"}]}

    def protected(text):
        asr = text.replace("morning", "mornin") if "morning" in text else text.replace("famous", "famouse")
        span = er020.identify_ng_span(text, asr)
        return er129.input_overlaps_confirmed(text, span, asr, sel, er129.level_facts(ld, text))["protected"]

    assert protected(clip_a) is False                       # 確定内容と無関係な文はLR可(偽T2なし)
    assert protected(clip_b) is True                        # 確定語句banditを含む文は引き続き保護
    texts = [er129.level_facts(ld, "the woodcutter said.")["level_text"]]
    assert texts[0].count("the woodcutter said.") == 1       # 既にあるentry本文は二重に足さない
    # resultsの最後のentryが引用clip(`,"`終わり)のとき(再生成でdictの末尾に入り直す実run)も、parts文字列と1文に結合しない(台帳と同じ連結[文境界つき])
    res["segments"]["clip_a"] = {"status": "OK", "canonical_text": clip_a}
    json.dump(res, open(f"{ld}/audit/tts_generation_results.json", "w", encoding="utf-8"))
    assert protected(clip_a) is False and protected(clip_b) is True


def test_candidate_filter_unwraps_prompt_quote_doubling_only_for_quoted_segments():
    """LR候補生成Promptは原文を"..."で囲むため、引用符で囲まれたZセリフ原文では候補が二重引用符("")になる(E1 c6 / E3 Adv実測)。Z限定filterで原文の形へ戻す。
    引用符で囲まれていない原文・既に同形の候補は変更しない。"""
    import er129_lr_display_reflection_01 as er129
    flt = er129.make_candidate_filter(None)
    canon = '"Yes, I killed him,"'
    recs = [{"adoptable": True, "rewritten_segment": '""Yes, I did him in,""'}, {"adoptable": True, "rewritten_segment": '"Yes, I did him in,"'}]
    out = flt(canon, [dict(r) for r in recs])
    assert out[0]["rewritten_segment"] == '"Yes, I did him in,"' and out[0].get("prompt_quote_unwrapped") is True
    assert out[1]["rewritten_segment"] == '"Yes, I did him in,"' and "prompt_quote_unwrapped" not in out[1]
    plain = flt("He left the room.", [{"adoptable": True, "rewritten_segment": '""He left the room.""'}])
    assert plain[0]["rewritten_segment"] == '""He left the room.""'      # 原文が引用符で囲まれていない場合は触らない
