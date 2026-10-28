"""er130 採用take分類核のtest(W3 §6-2の新規15ケース + Opus M-5 + allowlist drift + fail-closed + 未配線固定)。API 0。"""
import glob
import hashlib
import json
import os
import re

import pytest

import er127_tts_block_policy_01 as er127
import er129_lr_display_reflection_01 as m129
import er130_adopted_take_classifier_01 as c

AL = c.build_allowlist()
EN_MIN = hashlib.sha256(b"natural, clear, conversational").hexdigest()
ROLE = next(iter(sorted(AL["role_style"])))
LOCK = m129.ENGLISH_LOCK_STYLE_SHA


def take(kind=m129.KIND_NORMAL, sha=ROLE, slot=None, how="final_adoption", source="final_adoption", status="OK", lr_block=False, notes=None, from_sha=ROLE):
    return {"source": source, "how": how, "status": status, "depth": 1 if lr_block else 0, "ordinal": 3, "slot": slot,
            "style_mode": "FALLBACK" if kind in m129.FALLBACK_KINDS else "PRIMARY", "kind": kind,
            "style_name": kind, "style_sha": sha, "from_style_sha": from_sha, "audio_sha": "a" * 64, "lr_block": lr_block,
            "human_superseded_lr": False, "notes": notes or []}


def clip(t=None, lr=False, parity="PASS", t1="PASS", verdict=None, warnings=None):
    d = {"clip_id": "full_story_part1", "adopted_take": t if t is not None else take(), "warnings": warnings or [], "text_parity": None, "overlap": None,
         "lr": None, "verdict": verdict or m129.V_NO_LR, "changed_spans": [], "fallback": {"from_style": "ROLE_STYLE(x)"}}
    if lr:
        d["lr"] = {"adopted_in_final": True, "superseded_by_human": False, "reason": "r"}
        d["text_parity"] = {"verdict": parity}
        d["overlap"] = {"T1": {"status": t1}, "T2": {"status": "PASS"}, "T3": {"status": "PASS"}}
        d["verdict"] = verdict or m129.V_PASS
    return d


CTX_OK = {"asr_state": "PASS", "lr_gates_ok": True, "extra_approved_shas": set(), "human_approved": False}


def run(cl, pol="EN_LR_STD", ctx=None):
    return c.classify_adopted_take(cl, pol, AL, CTX_OK if ctx is None else ctx)


# ---- 1 正常LR
def test_01_normal_lr_pass_with_warning():
    r = run(clip(take(lr_block=True), lr=True))
    assert r.verdict == c.PASS_WITH_WARNING and [w["kind"] for w in r.warnings] == ["LR_APPLIED"]


# ---- 2 正常Fallback(EN③ / JA③ / KP ENGLISH_LOCK / Z Dialogue / LR block ③')
@pytest.mark.parametrize("pol,kind,sha,slot", [
    ("EN_LR_STD", m129.KIND_MINIMAL_EN, EN_MIN, "③"), ("EN_LR_ADV", m129.KIND_MINIMAL_EN, EN_MIN, 3),
    ("JA_STD", m129.KIND_MINIMAL_JA, next(iter(AL["fallback"][m129.KIND_MINIMAL_JA])), 3),
    ("KP_EN", m129.KIND_ENGLISH_LOCK, LOCK, 4), ("KP_EN", m129.KIND_ENGLISH_LOCK, LOCK, 3),
    ("Z_DLG_CTX", m129.KIND_LEGACY_DIALOGUE, next(iter(AL["fallback"][m129.KIND_LEGACY_DIALOGUE])), 3),
    ("EN_LR_STD", m129.KIND_MINIMAL_EN, EN_MIN, "③'"), ("EN_LR_STD", m129.KIND_MINIMAL_EN, EN_MIN, 6)])
def test_02_normal_fallback(pol, kind, sha, slot):
    r = run(clip(take(kind, sha, slot)), pol)
    assert r.verdict == c.PASS_WITH_WARNING and r.warnings[0]["kind"] == "FALLBACK_APPLIED", r


# ---- 3 重複
def test_03_lr_and_fallback_overlap_two_kinds():
    r = run(clip(take(m129.KIND_MINIMAL_EN, EN_MIN, "③'", lr_block=True), lr=True))
    assert r.verdict == c.PASS_WITH_WARNING and sorted(w["kind"] for w in r.warnings) == ["FALLBACK_APPLIED", "LR_APPLIED"]


# ---- 4 未承認Style・非Fallback slotのMinimal
def test_04_unapproved_style_blocks():
    r = run(clip(take(sha="f" * 64, from_sha="f" * 64)))
    assert r.verdict == c.BLOCK and "STYLE_NOT_APPROVED_OR_UNKNOWN" in r.reasons


def test_04b_unapproved_fallback_sha_and_slot():
    assert "STYLE_NOT_APPROVED_OR_UNKNOWN" in run(clip(take(m129.KIND_MINIMAL_EN, "e" * 64, 3))).reasons
    assert "FALLBACK_SLOT_INCONSISTENT" in run(clip(take(m129.KIND_MINIMAL_EN, EN_MIN, 1))).reasons
    assert "FALLBACK_SLOT_INCONSISTENT" in run(clip(take(m129.KIND_MINIMAL_EN, EN_MIN, "②'"))).reasons


# ---- 5 許可されていないFallback方式
@pytest.mark.parametrize("pol,kind,sha", [("SHELL_EN", m129.KIND_MINIMAL_EN, EN_MIN), ("Z_DLG_LEGACY", m129.KIND_LEGACY_DIALOGUE, next(iter(AL["fallback"][m129.KIND_LEGACY_DIALOGUE]))),
                                          ("JA_STD", m129.KIND_MINIMAL_EN, EN_MIN), ("NO_TTS", m129.KIND_MINIMAL_EN, EN_MIN), ("KP_EN", m129.KIND_MINIMAL_EN, EN_MIN)])
def test_05_fallback_not_allowed_for_policy(pol, kind, sha):
    r = run(clip(take(kind, sha, 3)), pol)
    assert r.verdict == c.BLOCK and "FALLBACK_NOT_ALLOWED_FOR_POLICY" in r.reasons


# ---- 6 証拠欠落
def test_06_missing_evidence():
    assert "ADOPTED_TAKE_RECORD_INCOMPLETE" in run({**clip(), "adopted_take": None}).reasons
    assert "ASR_RECORD_MISSING" in run(clip(), ctx={**CTX_OK, "asr_state": None}).reasons
    assert "STYLE_RECORD_MISSING" in run(clip(take(kind=None))).reasons
    assert "STYLE_RECORD_MISSING" in run(clip(take(m129.KIND_MINIMAL_EN, None, 3))).reasons          # Fallback実測shaなし
    assert "STYLE_RECORD_MISSING" in run(clip(take(sha=None, how="attempts_log.verified", from_sha=ROLE))).reasons
    assert "LR_RECORD_INCOMPLETE" in run(clip(take(), lr=True), ctx={**CTX_OK, "lr_gates_ok": None}).reasons


# ---- 7 旧記録(OPEN-564以前): 記録完全なら警告、不完全ならBLOCK(F-6)
def test_07_old_record_complete_warns_incomplete_blocks():
    old_ok = take(m129.KIND_MINIMAL_EN, EN_MIN, None, how="attempt_file_sha_match", source="derived")
    r = run(clip(old_ok))
    assert r.verdict == c.PASS_WITH_WARNING and any("SLOT_UNVERIFIED" in n for n in r.notes)
    old_bad = take(m129.KIND_MINIMAL_EN, None, None, how="fallback_used_flag(no LR)+verified row", source="derived")
    assert run(clip(old_bad)).verdict == c.BLOCK
    assert run({**clip(), "adopted_take": None}).verdict == c.BLOCK             # UNKNOWN
    assert run(clip(take(status=m129.V_RECORD_MISMATCH))).reasons == ["RECORD_MISMATCH"]


# ---- 8 ASR NG
def test_08_asr_ng():
    assert "ADOPTED_TAKE_ASR_NOT_PASS" in run(clip(), ctx={**CTX_OK, "asr_state": "NG"}).reasons
    assert run(clip(), ctx={**CTX_OK, "asr_state": "PASS_WITH_WARNING"}).verdict == c.PASS


# ---- 9 本文音声不一致(parity)
def test_09_parity_mismatch_and_not_evaluated():
    assert "TEXT_AUDIO_PARITY_MISMATCH" in run(clip(take(), lr=True, parity="FAIL", verdict=m129.V_PARITY)).reasons
    cl = clip(take(), lr=True)
    cl["text_parity"] = None                                    # parity未配線は常にBLOCK
    assert "TEXT_AUDIO_PARITY_NOT_PASS" in run(cl).reasons
    assert "TEXT_AUDIO_PARITY_UNLOCATABLE" in run(clip(take(), lr=True, verdict=m129.V_UNLOCATABLE)).reasons


# ---- 10 LR x 確定内容
def test_10_overlap_blocks():
    assert "LR_OVERLAPS_CONFIRMED_CONTENT" in run(clip(take(), lr=True, t1="STOP")).reasons
    assert "LR_OVERLAPS_CONFIRMED_CONTENT" in run(clip(take(), lr=True, verdict=m129.V_T2)).reasons


# ---- 11 LRが非LR role
@pytest.mark.parametrize("pol", ["JA_STD", "KP_EN", "KP_EXPL", "Z_DLG_CTX", "SHELL_EN"])
def test_11_lr_on_non_lr_role(pol):
    assert "LR_ON_NON_LR_ROLE" in run(clip(take(), lr=True), pol).reasons


# ---- 12 allowlist drift
def test_12_allowlist_drift():
    import er003_b1_p9a_audio as p9a
    import er003_v1_n3_01_tts_generate as n3
    import er003_v1_repro01_main_generate as repro01
    import er019_family_x_style_profile_01 as xsp
    import er033_tts_flash_lite_family_x_styles_01 as er033
    sh = c.sha256_text
    assert AL["fallback"][m129.KIND_MINIMAL_EN] == {sh(er033.FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]), sh(repro01.MINIMAL_INSTRUCTION_PREFIX)}   # B10 D1: KP解説③の既存Production Styleを追加登録
    assert EN_MIN in AL["fallback"][m129.KIND_MINIMAL_EN]
    assert AL["fallback"][m129.KIND_MINIMAL_JA] == {sh(n3._A2_JA_MINIMAL_INSTRUCTION_PREFIX)}
    assert AL["fallback"][m129.KIND_ENGLISH_LOCK] == {sh(repro01.KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION)} == {LOCK}   # er129定数とも一致
    assert AL["fallback"][m129.KIND_LEGACY_DIALOGUE] == {sh(p9a.ENGLISH_STYLE_PREFIX)}
    for prof in xsp.STYLE_PROFILES.values():
        for o in prof["overrides"].values():
            assert o["sha256"] in AL["role_style"]
    # policy.third_style(Fallback可能なもの)は全てallowlist kindに対応(policy表が変わればここが落ちる)
    for name, p in er127.PROFILES.items():
        if p.third_style not in ("SAME", "NONE"):
            assert p.third_style in c.THIRD_STYLE_TO_KIND and c.THIRD_STYLE_TO_KIND[p.third_style] in AL["fallback"], name
    # role Style route名がleaf sourceに存在
    src = open(os.path.join(os.path.dirname(c.__file__), "er003_v1_sing01_news_tail_fix.py"), encoding="utf-8").read() + open(
        os.path.join(os.path.dirname(c.__file__), "er003_v1_repro01_main_generate.py"), encoding="utf-8").read()
    for r in c._ROLE_STYLE_ROUTES:
        assert r in src, r


# ---- 13 未配線の固定(Production codeから参照されない。A/B/C runnerも含む)
# 委任_11(B-wire): 設計上の利用者(Gate 3か所=X M3/Y gate/Z style gate)だけを許可し、TTS leaf・ASR・KP表示・Style Prompt・公開ページ生成器は直接importしない
ER130_ALLOWED_USERS = ("er019_family_x_style_profile_01.py", "er121_family_y_audio_01.py", "er063_family_z_audio_01.py")


def test_13_not_imported_by_production():
    root = os.path.dirname(c.__file__)
    for f in glob.glob(os.path.join(root, "*.py")):
        b = os.path.basename(f)
        if b.startswith("er130_") or b.startswith("er129_") or "_test" in b or b in ER130_ALLOWED_USERS:
            continue
        txt = open(f, encoding="utf-8", errors="ignore").read()
        assert not re.search(r"\ber130_adopted_take_classifier_01\b", txt), b


# ---- 14 fail-closed(例外・想定外型)
def test_14_exception_blocks():
    assert run("not a dict").reasons == ["INPUT_INVALID"]
    assert run(clip(), pol=None).reasons == ["POLICY_UNRESOLVED"]
    assert run(clip(), pol="NOPE").reasons == ["POLICY_UNRESOLVED"]
    r = c.classify_adopted_take({"adopted_take": {"status": "OK", "kind": "FALLBACK_MINIMAL_EN", "style_sha": EN_MIN, "slot": object()}}, "EN_LR_STD", AL, CTX_OK)
    assert r.verdict == c.BLOCK
    r = c.classify_adopted_take(clip(), "EN_LR_STD", AL, {"asr_state": "PASS", "extra_approved_shas": 5})     # 想定外型でも通さない
    assert r.verdict == c.BLOCK and r.reasons == ["CLASSIFIER_EXCEPTION"]


# ---- 15 維持項目の回帰: 正常でないものは正常化されない
def test_15_no_event_normal_take_passes_without_warning():
    r = run(clip(take()))
    assert r.verdict == c.PASS and r.warnings == []


# ---- Opus M-5
def test_m5_hr_adopted_take_not_false_blocked():
    t = take(sha=ROLE, source="human_approval", how="human_attempt_file")
    r = run(clip(t), ctx={**CTX_OK, "asr_state": "NG", "human_approved": True})
    assert r.verdict == c.PASS and any("HUMAN_APPROVED_TAKE" in n for n in r.notes)


def test_m5_store_reuse_not_mismatch_and_wav_sha_irrelevant():
    # KP_EN Store key B hit(ordinal=null・source=store_reuse): BlockProgressに対応attemptが無くてもRECORD_MISMATCHにならない(er129で優先順位②として処理)
    fa = {"source": "store_reuse", "style_mode": "FALLBACK", "depth": 0, "ordinal": None, "sent_style_sha": LOCK, "style_name": "ENGLISH_LOCK", "attempt_audio_sha": None, "slot": None}
    entry = {"status": "OK", "reused": True, "final_adoption": fa, "language": "en"}
    bp = {"blocks": {"0": {"attempts": {"2": {"verified": True}}}}}
    t = m129.resolve_adopted_take(entry, bp, None, seg_id="kp2_en")
    assert t["status"] == "OK" and t["source"] == "store_reuse" and t["kind"] == m129.KIND_ENGLISH_LOCK
    r = run({**clip(), "adopted_take": dict(t)}, "KP_EN")
    assert r.verdict == c.PASS_WITH_WARNING and r.warnings[0]["kind"] == "FALLBACK_APPLIED"
    # wav shaがfinish後の加工で変わってもclassifyはaudio shaを条件にしない
    t2 = dict(t, audio_sha="0" * 64)
    assert run({**clip(), "adopted_take": t2}, "KP_EN").verdict == c.PASS_WITH_WARNING


def test_m5_old_cache_without_final_adoption_and_z_build_entry():
    # 旧cache(final_adoptionなし)/Z build_entryでfinal_adoptionが落ちた形: 旧記録導出の完全なtakeなら偽BLOCKしない
    t = take(m129.KIND_ENGLISH_LOCK, LOCK, None, how="english_lock_attempts_log.verified", source="derived")
    assert run({**clip(), "adopted_take": t}, "KP_EN").verdict == c.PASS_WITH_WARNING
    t = take(m129.KIND_LEGACY_DIALOGUE, None, None, how="dialogue_tts.final_mode", source="derived")
    assert run({**clip(), "adopted_take": t}, "Z_DLG_CTX").verdict == c.PASS_WITH_WARNING


def test_normal_style_hint_prefix_and_route():
    txt = next(t for t in AL["role_style_texts"] if len(t) > 50) + " Pronounce 'x' as y."
    r = run(clip(take(sha="9" * 64, from_sha=None)), ctx={**CTX_OK, "adopted_instruction_text": txt})
    assert r.verdict == c.PASS
    r = run(clip(take(sha=None, how="attempt_file_sha_match", source="derived", notes=["route=english_style_prefix_wide_margin"], from_sha=ROLE)))
    assert r.verdict == c.PASS
    r = run(clip(take(sha=None, how="attempt_file_sha_match", source="derived", notes=["route=english_style_prefix_wide_margin"], from_sha="d" * 64)))
    assert "STYLE_NOT_APPROVED_OR_UNKNOWN" in r.reasons


def test_normalize_slot():
    assert [c.normalize_slot(x) for x in ("①", "③", "③'", "②′", 3, 6, None, "x")] == [1, 3, 6, 5, 3, 6, None, None]


# ---- 実データ(保存run、読取のみ)
def _real(path, sid, level, pol=None):
    res = json.load(open(path, encoding="utf-8"))
    led = m129.build_lr_ledger("", "", results_path=path)
    cl = next(x for x in led["clips"] if x["clip_id"] == sid)
    e = (res.get("segments") or {}).get(sid)
    if e is None:
        mm = re.fullmatch(r"kp(\d+)_(.+)", sid)
        e = (res["key_phrases"][mm.group(1)] or {})["english" if mm.group(2) == "en" else mm.group(2)]
    pol = pol or c.policy_for_clip(sid, e, level)
    t = cl.get("adopted_take") if isinstance(cl.get("adopted_take"), dict) else None
    return c.classify_adopted_take(cl, pol, AL, c.ctx_from_entry(e, take=t))


AI = "er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01"
TTH = "er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_reselect_01/b1b/audit/tts_generation_results.json"


@pytest.mark.skipif(not os.path.exists(AI), reason="saved run absent")
@pytest.mark.parametrize("lv,pol", [("a2", "EN_LR_STD"), ("b1b", "EN_LR_ADV")])
def test_real_ai_island_released(lv, pol):
    r = _real(f"{AI}/{lv}/audit/tts_generation_results.json", "full_story_part1_k2", lv)
    assert r.verdict == c.PASS_WITH_WARNING and [w["kind"] for w in r.warnings] == ["LR_APPLIED"]


@pytest.mark.skipif(not os.path.exists(TTH), reason="saved run absent")
def test_real_tell_tale_heart_adv_kp2_en_is_english_lock_pass():
    r = _real(TTH, "kp2_en", "b1b")
    assert r.verdict == c.PASS_WITH_WARNING and r.warnings[0]["style_kind"] == m129.KIND_ENGLISH_LOCK


@pytest.mark.skipif(not os.path.exists(TTH), reason="saved run absent")
def test_real_run_is_not_modified():
    def snap():
        h = hashlib.sha256()
        for f in sorted(glob.glob(os.path.dirname(os.path.dirname(TTH)) + "/**/*.json", recursive=True)):
            h.update(open(f, "rb").read())
        return h.hexdigest()
    a = snap()
    _real(TTH, "kp2_en", "b1b")
    assert snap() == a


# ---- 委任_15(B10) D1: KP解説③(既存Production Style repro01.MINIMAL_INSTRUCTION_PREFIX)の登録
KP_MIN = hashlib.sha256(__import__("er003_v1_repro01_main_generate").MINIMAL_INSTRUCTION_PREFIX.encode("utf-8")).hexdigest()


def test_b10_d1_kp_expl_fallback_sha_in_allowlist_and_passes():
    import er019_family_x_audio_production_runner_01 as r19
    import inspect
    assert KP_MIN.startswith("b66d3a74")
    assert KP_MIN in AL["fallback"][m129.KIND_MINIMAL_EN]
    assert "repro01.MINIMAL_INSTRUCTION_PREFIX" in inspect.getsource(r19._kp_explanation_unified)    # leafが現に送るStyleと同一定数(X/Y/Z共通の単一関数)
    r = run(clip(take(m129.KIND_MINIMAL_EN, KP_MIN, 3)), "KP_EXPL")
    assert r.verdict == c.PASS_WITH_WARNING and r.warnings[0]["kind"] == "FALLBACK_APPLIED", r


def test_b10_d1_unapproved_and_slot_still_block():
    assert "STYLE_NOT_APPROVED_OR_UNKNOWN" in run(clip(take(m129.KIND_MINIMAL_EN, "f" * 64, 3)), "KP_EXPL").reasons
    assert "FALLBACK_SLOT_INCONSISTENT" in run(clip(take(m129.KIND_MINIMAL_EN, KP_MIN, 2)), "KP_EXPL").reasons
    assert "STYLE_RECORD_MISSING" in run(clip(take(m129.KIND_MINIMAL_EN, None, 3)), "KP_EXPL").reasons


# ---- 委任_15(B10) D2: Z会話ctx→legacy_fallback(final_adoptionはsent_style_shaを持たない)
def _dt(final_mode="legacy_fallback", policy="fz_ctx_v1", n=3, verified=True, mode="legacy_fallback"):
    return {"policy": policy, "final_mode": final_mode, "final_attempt_n": n,
            "attempts": [{"n": 1, "mode": "ctx", "verified": False}, {"n": 2, "mode": "ctx", "verified": False}, {"n": n, "mode": mode, "verified": verified}]}


def test_b10_d2_z_dialogue_legacy_fallback_direct_record_passes():
    t = take(m129.KIND_LEGACY_DIALOGUE, None, 3)
    ctx = c.ctx_from_entry({"dialogue_tts": _dt(), "status": "OK", "asr_judgement": {"state": "PASS"}}, take=t)
    assert ctx["dialogue_legacy_direct"] is True
    r = run(clip(t), "Z_DLG_CTX", ctx)
    assert r.verdict == c.PASS_WITH_WARNING and r.warnings[0]["kind"] == "FALLBACK_APPLIED", r


@pytest.mark.parametrize("dt", [None, _dt(final_mode="ctx"), _dt(n=2), _dt(verified=False), _dt(mode="ctx"), _dt(policy="legacy")])
def test_b10_d2_abnormal_dialogue_record_still_blocks(dt):
    t = take(m129.KIND_LEGACY_DIALOGUE, None, 3)
    ctx = c.ctx_from_entry({"dialogue_tts": dt, "status": "OK", "asr_judgement": {"state": "PASS"}} if dt else {"status": "OK", "asr_judgement": {"state": "PASS"}}, take=t)
    assert ctx["dialogue_legacy_direct"] is False
    assert "STYLE_RECORD_MISSING" in run(clip(t), "Z_DLG_CTX", ctx).reasons


def test_b10_d2_override_drops_dialogue_mismatch_only_for_normal_fallback():
    t = take(m129.KIND_LEGACY_DIALOGUE, None, 3)
    entry = {"dialogue_tts": _dt(), "status": "OK", "asr_judgement": {"state": "PASS"}}
    ov = c.override_violations("full_story_part1", entry, "a2", ["Z_DIALOGUE_STYLE_ACTUAL_MISMATCH"], {"full_story_part1": clip(t)},
                               replaced=c.Z_REPLACED, replaced_when_fallback=c.Z_REPLACED_WHEN_FALLBACK)
    assert ov["violations"] == [] and ov["warnings"][0]["kind"] == "FALLBACK_APPLIED"
    # 記録欠落(dialogue_ttsなし)=BLOCK、旧違反も残る
    ov = c.override_violations("full_story_part1", {"dialogue_tts": _dt(verified=False), "status": "OK", "asr_judgement": {"state": "PASS"}}, "a2", ["Z_DIALOGUE_STYLE_ACTUAL_MISMATCH"],
                               {"full_story_part1": clip(t)}, replaced=c.Z_REPLACED, replaced_when_fallback=c.Z_REPLACED_WHEN_FALLBACK)
    assert "Z_DIALOGUE_STYLE_ACTUAL_MISMATCH" in ov["violations"] and "STYLE_RECORD_MISSING" in ov["violations"]
    # 通常(非Fallback)takeに付いたmismatchは置換されない
    ov = c.override_violations("full_story_part1", entry, "a2", ["Z_DIALOGUE_STYLE_ACTUAL_MISMATCH"], {"full_story_part1": clip(take())},
                               replaced=c.Z_REPLACED, replaced_when_fallback=c.Z_REPLACED_WHEN_FALLBACK)
    assert "Z_DIALOGUE_STYLE_ACTUAL_MISMATCH" in ov["violations"]


def test_b10_d2_z_gate_uses_replaced_when_fallback():
    import inspect
    import er063_family_z_audio_01 as z
    assert "replaced_when_fallback=_c130.Z_REPLACED_WHEN_FALLBACK" in inspect.getsource(z._z_row_for_clip)


# ---- 委任_15(B10) D6: Master Audio Store再利用(asr_judgement_inherited)
def test_b10_d6_store_reuse_inherited_asr_state():
    base = {"status": "OK"}
    assert c.adopted_asr_state({**base, "asr_judgement_inherited": {"state": "PASS_WITH_WARNING"}}) == ("PASS_WITH_WARNING", "asr_judgement_inherited")
    assert c.adopted_asr_state({**base, "asr_judgement": {"state": "PASS"}, "asr_judgement_inherited": {"state": "FAIL"}}) == ("PASS", "asr_judgement")
    assert c.adopted_asr_state({**base, "asr_judgement_inherited": {}}) == (None, None)       # stateなし=従来どおり記録欠落
    assert c.adopted_asr_state({**base, "asr_judgement_inherited": "PASS"}) == (None, None)
    t = take(source="store_reuse", sha=None, how="store_reuse")
    ctx = c.ctx_from_entry({"asr_judgement_inherited": {"state": "PASS"}}, take=t)
    assert run(clip(t), "KP_EN", ctx).verdict in (c.PASS, c.PASS_WITH_WARNING)
    ctx0 = c.ctx_from_entry({}, take=t)
    assert "ASR_RECORD_MISSING" in run(clip(t), "KP_EN", ctx0).reasons
    ctxn = c.ctx_from_entry({"asr_judgement_inherited": {"state": "FAIL"}}, take=t)
    assert "ADOPTED_TAKE_ASR_NOT_PASS" in run(clip(t), "KP_EN", ctxn).reasons
