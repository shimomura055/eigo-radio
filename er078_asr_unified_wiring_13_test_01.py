# -*- coding: utf-8 -*-
"""AUW 委任_13 test: A3是正(length判定をSecondary採用転写で再評価。Primary内容PASS+length NGもSecondaryへ降格。
呼出元10箇所がmax_lenをjudgeへ渡し、最終ANDは final_length_ok[fail-closed]。max_len未指定は旧挙動=安全ラッチ)。
ユーザー指示 A-2: 「Primaryの差が大きいという理由だけでSecondaryを省略したり、Secondaryの正当なPASSを拒否したりしない」+「数値・否定などの
明確な重大内容差、独立音声品質QAは維持する」。全てmock(API呼出0・費用JPY0)。helperは委任_05 testを再利用。
"""
import ast
import json
import os
import re

import pytest

import er006_asr_provider_routing_01 as routing
import er006_secondary_asr_01 as sec
import er007_ja_secondary_asr_01 as ja
import er078_asr_unified_judge_01 as uj
import er078_pass_with_warning_registry_01 as reg
from er078_asr_unified_judge_01 import AttemptCtx, PrimaryResult, unified_judge
from er078_asr_unified_wiring_05_test_01 import Az, AzJa, CANON, WRONG, _iso, _tts_mocks  # noqa: F401

ROOT = os.path.dirname(os.path.abspath(__file__))
EN = "Hello there my good friend today."          # 33文字
LONG_EN_TAIL = " and so on and so forth" * 4          # Primary転写の水増し(hallucination様の尾部)


class Sec:
    def __init__(self, text):
        self.text, self.calls = text, 0

    def __call__(self, ctx):
        self.calls += 1
        return self.text


def ctx_(canon, **kw):
    return AttemptCtx(canonical_text=canon, wav_sha256="x" * 64, audio_seconds=3.0, segment_key="t", **kw)


# ============================================================
# A. judge unit(11項目 + R1)
# ============================================================
def test_01_primary_ng_with_length_ng_goes_to_secondary_and_secondary_length_ok_passes_with_warning():
    """A-2: Primaryのlength NGだけを理由にSecondaryを省略しない。Secondary正当PASSを拒否しない。"""
    sec_ = Sec(EN)
    mx = len(EN) + 15
    r = unified_judge(ctx_(EN, length_ok=False, max_len=mx), PrimaryResult(False, EN + LONG_EN_TAIL), sec_, lang="en", role="x")
    assert sec_.calls == 1 and r.state == uj.PASS_WITH_WARNING
    ln = r.audit_record["length"]
    assert ln["applied"] is True and ln["max_len"] == mx and ln["adopted_from"] == "secondary" and ln["adopted_ok"] is True
    assert ln["primary_len"] > mx and ln["secondary_len"] == len(EN) and ln["primary_ok"] is False
    assert uj.W_PRIMARY_LENGTH_EXCESS in r.warning_labels and uj.W_SECONDARY_CONFIRMED in r.warning_labels      # R7(試聴対象)
    assert uj.final_length_ok(False, {"asr_judgement": r.audit_record}) is True
    assert r.audit_record.get("exclusion_rule") is None


def test_02_secondary_transcript_over_max_len_is_ng_both_and_final_length_stays_false():
    over = EN + LONG_EN_TAIL
    sec_ = Sec(over)
    mx = len(EN) + 15
    r = unified_judge(ctx_(EN, length_ok=False, max_len=mx), PrimaryResult(False, over), sec_, lang="en", role="x",
                      secondary_accept_fn=lambda c, s: (True, "ACCEPT"))
    assert r.state == uj.NG_BOTH and r.reason_code == "secondary_length_ng" and sec_.calls == 1
    assert r.audit_record["length"]["adopted_ok"] is False
    assert uj.final_length_ok(False, {"asr_judgement": r.audit_record}) is False


def test_03_primary_pass_with_length_ng_is_demoted_to_p3_and_agreement_is_pass_with_warning():
    """R2(A3R-02): Primary内容PASS+length NG -> P3降格。合意でも無警告PASS(force_secondary_agreed)にはしない。"""
    sec_ = Sec(EN)
    mx = len(EN) + 10
    r = unified_judge(ctx_(EN, length_ok=True, max_len=mx), PrimaryResult(True, EN + LONG_EN_TAIL, adopted_text=None),
                      sec_, lang="en", role="x", secondary_accept_fn=lambda c, s: (True, "EXACT"))
    assert sec_.calls == 1 and r.state == uj.PASS_WITH_WARNING
    assert r.reason_code == "secondary_confirmed_primary_length_ng" and r.audit_record["p3_entry"] == "primary_length_ng"
    assert uj.W_PRIMARY_LENGTH_EXCESS in r.warning_labels
    assert uj.final_length_ok(False, {"asr_judgement": r.audit_record}) is True


def test_04_primary_pass_with_length_ng_and_secondary_not_accepted_is_ng_both():
    sec_ = Sec("Totally different words here.")
    r = unified_judge(ctx_(EN, max_len=len(EN) + 10), PrimaryResult(True, EN + LONG_EN_TAIL), sec_, lang="en", role="x",
                      secondary_accept_fn=lambda c, s: (False, "REJECT"))
    assert sec_.calls == 1 and r.state == uj.NG_BOTH and r.reason_code == "secondary_not_accepted"


def test_05_primary_pass_with_length_ok_is_unchanged_no_secondary_call():
    sec_ = Sec(EN)
    r = unified_judge(ctx_(EN, max_len=len(EN) + 15), PrimaryResult(True, EN), sec_, lang="en", role="x")
    assert sec_.calls == 0 and r.state == uj.PASS and r.reason_code == "primary_pass"
    ln = r.audit_record["length"]
    assert ln["adopted_from"] == "primary" and ln["adopted_ok"] is True and ln["primary_ok"] is True
    assert uj.W_PRIMARY_LENGTH_EXCESS not in r.warning_labels
    assert uj.final_length_ok(True, {"asr_judgement": r.audit_record}) is True


def test_06_safety_latch_without_max_len_keeps_legacy_behaviour_en_and_ja():
    """R3(A3R-03): max_len未指定の呼出元は従来挙動(JA=A3事前除外/EN=length_ok既定Trueで従来)。"""
    ja_s = Sec("今日は晴れ。")
    r = unified_judge(ctx_("今日は晴れ。", length_ok=False), PrimaryResult(False, "全然違う"), ja_s, lang="ja", role="x")
    assert r.state == uj.NG_EXCLUDED and r.audit_record["exclusion_rule"] == "A3_LENGTH_NG" and ja_s.calls == 0
    assert r.audit_record["length"]["applied"] is False
    en_s = Sec(EN)
    r2 = unified_judge(ctx_(EN), PrimaryResult(True, EN + LONG_EN_TAIL), en_s, lang="en", role="x")      # max_len無し: PrimaryPASSのまま
    assert r2.state == uj.PASS and en_s.calls == 0


def test_07_module_constant_rollback_restores_a3_even_with_max_len(monkeypatch):
    """R9(A3R-09): module定数でA3是正を無効化できる(env/flagではない)。表からA3ルールは削除していない。"""
    monkeypatch.setattr(uj, "A3_SECONDARY_LENGTH_REEVAL", False)
    s = Sec("今日は晴れ。")
    r = unified_judge(ctx_("今日は晴れ。", length_ok=False, max_len=9), PrimaryResult(False, "全然違う"), s, lang="ja", role="x")
    assert r.state == uj.NG_EXCLUDED and r.audit_record["exclusion_rule"] == "A3_LENGTH_NG" and s.calls == 0
    assert "A3_LENGTH_NG" in [x.rule_id for x in uj.SCG_EXCLUSIONS]


def test_07b_constant_default_is_true_and_not_env_driven():
    src = open(os.path.join(ROOT, "er078_asr_unified_judge_01.py"), encoding="utf-8").read()
    assert re.search(r"^A3_SECONDARY_LENGTH_REEVAL = True\b", src, re.M)
    assert "os.environ" not in src.split("A3_SECONDARY_LENGTH_REEVAL = True")[1].split("CIRCUIT_BREAKER_THRESHOLD")[0]


def test_08_primary_length_is_measured_on_gate_text_adopted_transcript():
    """R2: Primary length計測はgate_text(adopted_text)基準。"""
    s = Sec(EN)
    mx = len(EN) + 5
    r = unified_judge(ctx_(EN, max_len=mx), PrimaryResult(True, EN + LONG_EN_TAIL, equivalence_basis="TIER1_DIFF_ANCHORED", adopted_text=EN),
                      s, lang="en", role="x")
    assert s.calls == 0 and r.state == uj.PASS
    assert r.audit_record["length"]["primary_len"] == len(EN) and r.audit_record["length"]["primary_ok"] is True


@pytest.mark.parametrize("detail,primary,expected", [
    (None, True, True), (None, False, False), ({}, False, False), ("x", False, False),
    ({"asr_judgement": None}, False, False),
    ({"asr_judgement": {"state": "NG_BOTH", "length": {"adopted_from": "secondary", "adopted_ok": True}}}, False, False),
    ({"asr_judgement": {"state": "PASS_WITH_WARNING", "length": {"adopted_from": "primary", "adopted_ok": True}}}, False, False),
    ({"asr_judgement": {"state": "PASS_WITH_WARNING", "length": {"adopted_from": "secondary", "adopted_ok": None}}}, False, False),
    ({"asr_judgement": {"state": "PASS_WITH_WARNING", "length": {"adopted_from": "secondary", "adopted_ok": False}}}, False, False),
    ({"asr_judgement": {"state": "PASS_WITH_WARNING", "length": "bad"}}, False, False),
    ({"asr_judgement": {"state": "PASS_WITH_WARNING"}}, False, False),
    ({"asr_judgement": {"state": "PASS_WITH_WARNING", "length": {"adopted_from": "secondary", "adopted_ok": True}}}, False, True),
    ({"state": "PASS", "length": {"adopted_from": "secondary", "adopted_ok": True}}, False, True),     # asr_judgement自体を渡しても可
    ({"asr_judgement": {"state": "PASS", "length": {"adopted_from": "primary", "adopted_ok": True}}}, True, True),
])
def test_09_final_length_ok_is_fail_closed(detail, primary, expected):
    assert uj.final_length_ok(primary, detail) is expected


def test_10_value_negation_guards_and_exclusions_still_win_over_length_rescue():
    """#7維持: 数値・否定の重大差、A4(同形異音)・A7(登録読み)は max_len指定でも救済されない。"""
    s = Sec("The store opens at three o'clock sharp today.")
    r = unified_judge(ctx_("The store opens at three o'clock sharp today.", length_ok=False, max_len=100),
                      PrimaryResult(False, "The store opens at five o'clock sharp today."), s, lang="en", role="x")
    assert r.state == uj.NG_PROTECTED and s.calls == 0
    s = Sec("店は午後三時に開きます。")
    r = unified_judge(ctx_("店は午後三時に開きます。", length_ok=False, max_len=100), PrimaryResult(False, "店は午後五時に開きます。"), s, lang="ja", role="x")
    assert r.state == uj.NG_PROTECTED and s.calls == 0
    # Secondary側の数値DIFFは長さが収まっていてもNG_BOTH
    s = Sec("The store opens at five o'clock sharp today.")
    r = unified_judge(ctx_("The store opens at three o'clock sharp today.", length_ok=False, max_len=100),
                      PrimaryResult(False, "The store opens at three o'clock sharp today and so on and so forth and so on and so forth and so on and so forth and so on."),
                      s, lang="en", role="x", secondary_accept_fn=lambda c, t: (True, "X"))
    assert r.state == uj.NG_BOTH and r.reason_code == "secondary_value_diff"
    for sig, rule in (({"c2_homophone_candidate": True}, "A4_C2_HOMOGRAPH"), ({"reading_dictionary_mismatch": True}, "A7_READING_DICT_MISMATCH")):
        s = Sec("橋を渡ります。")
        r = unified_judge(ctx_("橋を渡ります。", length_ok=False, max_len=100), PrimaryResult(False, "箸を渡ります。", signals=sig), s, lang="ja", role="x")
        assert r.state == uj.NG_EXCLUDED and r.audit_record["exclusion_rule"] == rule and s.calls == 0


def test_11_force_secondary_with_length_ng_is_warning_not_silent_pass_and_length_ok_force_secondary_is_unchanged():
    s = Sec(EN)
    r = unified_judge(ctx_(EN, max_len=len(EN) + 10, force_secondary=True), PrimaryResult(True, EN + LONG_EN_TAIL), s, lang="en", role="x",
                      secondary_accept_fn=lambda c, t: (True, "EXACT"))
    assert r.state == uj.PASS_WITH_WARNING                   # 無警告PASS(force_secondary_agreed)にしない
    s2 = Sec(EN)
    r2 = unified_judge(ctx_(EN, max_len=len(EN) + 10, force_secondary=True), PrimaryResult(True, EN), s2, lang="en", role="x",
                       secondary_accept_fn=lambda c, t: (True, "EXACT"))
    assert r2.state == uj.PASS and r2.reason_code == "force_secondary_agreed"        # 従来どおり


@pytest.mark.parametrize("extra", [10, 15, 20, 30, 40, 60])
def test_12_judge_uses_caller_max_len_not_a_fixed_recomputation(extra):
    """R1(A3R-01): 呼出元ごとの余裕文字数(10/15/20/30/40/60)をそのまま使う。len(text)+15等の固定再計算をしない。"""
    tail = "x" * 30
    text = "Hello there my good friend today."
    prim = text + tail                  # +30文字
    s = Sec(text)
    r = unified_judge(ctx_(text, max_len=len(text) + extra), PrimaryResult(True, prim), s, lang="en", role="x",
                      secondary_accept_fn=lambda c, t: (True, "EXACT"))
    if extra >= 30:
        assert s.calls == 0 and r.state == uj.PASS                       # Primaryは長さOK
    else:
        assert s.calls == 1 and r.state == uj.PASS_WITH_WARNING          # Primary超過 -> 降格


# ============================================================
# B. 試聴リスト導出(R7)
# ============================================================
def test_13_primary_length_excess_label_reaches_listening_list():
    sec_ = Sec(EN)
    r = unified_judge(ctx_(EN, max_len=len(EN) + 10), PrimaryResult(True, EN + LONG_EN_TAIL), sec_, lang="en", role="x",
                      secondary_accept_fn=lambda c, t: (True, "EXACT"))
    seg = {"status": "OK", "text": EN, "path": "a.wav", "sha256": "abc", "asr_judgement": r.audit_record}
    entries = reg.derive_listening_list({"seg": seg})
    assert len(entries) == 1 and uj.W_PRIMARY_LENGTH_EXCESS in entries[0]["warning_labels"]


# ============================================================
# C. 呼出元10箇所(mock leaf)。Primary転写が長い+Secondaryが原稿一致 -> 救済(status OK)、Secondaryも長い -> STOPPED
# ============================================================
JA = "ありがとうございます、今日は晴れです"
JA_NG = "さようなら明日は雨でしょう"
LONG_EN = CANON + " and so on and so forth" * 8
LONG_JA = JA + "そしてさらにまたまたたくさんの余計なことばが続きます" * 4

SITES = {
    # id: (言語, 期待max_len = len(text) + 余裕, fallback位置か)
    "s1_crosslevel_fallback": ("en", len(CANON) + 60, True),
    "s3_repro01_en": ("en", len(CANON) + 15, False),
    "s5_news_tail_fix": ("en", len(CANON) + 15, False),
    "s6_point_headings": ("en", len(CANON) + 15, False),
    "s7_voice01_en": ("en", len(CANON) + 15, False),
    "s10_bvoices": ("en", len(CANON) + 15, False),
    "s2_n3_ja_fallback": ("ja", len(JA) + 40, True),
    "s4_repro01_ja": ("ja", len(JA) + 15, False),
    "s8_voice01_ja_standard": ("ja", len(JA) + 15, False),
    "s9_voice01_ja_fallback": ("ja", len(JA) + 15, True),
}


def _drive(site, tmp_path, monkeypatch, secondary_ok):
    import er003_v1_crosslevel_audio_02_common as cl
    import er003_v1_n3_01_tts_generate as n3
    import er003_v1_repro01_main_generate as r1
    import er003_v1_sing01_news_tail_fix as ntf
    import er003_v1_sing01_point_headings_aoede as ph
    import er003_v1_sing01_voice01_generate as v01
    import er012_b_family_voices_production_01 as bv
    lang, _mx, fb = SITES[site]
    n = []
    _tts_mocks(monkeypatch, n)
    out_en = str(tmp_path / "wiring_theme_auw13" / "b1b" / "narration" / "full_story_part1.wav").replace("\\", "/")
    os.makedirs(os.path.dirname(out_en), exist_ok=True)
    if lang == "en":
        good, bad_long = CANON, LONG_EN

        def tr(*a, **k):
            return ((bad_long if (not fb or len(n) >= 3) else WRONG), None)

        monkeypatch.setattr(routing, "transcribe", tr)

        class _Az(Az):
            def __call__(self, wav_path, language="en-US", phrases=None, **kw):
                self.calls += 1
                if fb and len(n) < 3:
                    return (WRONG, None)
                return ((good if secondary_ok else bad_long), None)
        az = _Az()
        monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", az)
        monkeypatch.setattr(sec, "_log_human_review", lambda d: None)
        monkeypatch.setattr(sec, "_connected_speech_equivalence_layer_attempt", lambda *a, **k: None)
        monkeypatch.setattr(r1.pron_resolver_core, "resolve_and_augment_en_style_prefix", lambda b, t: (b, {"hints_applied": False}))
        monkeypatch.setattr(r1.pronun_ledger, "get_hint_for_text", lambda *a, **k: [])
        if site == "s1_crosslevel_fallback":
            monkeypatch.setattr(cl.pronun_ledger, "get_hint_for_text", lambda *a, **k: [])
            monkeypatch.setattr(r1, "generate_english_component_minimal_instruction",
                                lambda text, out_path, **k: (n.append(1), {"status": "OK", "path": out_path, "duration_seconds": 1.0})[1])
            r = cl.generate_english_segment_with_fallback(CANON, str(tmp_path / "dummy.wav"), "quick")
        elif site == "s3_repro01_en":
            r = r1.generate_narration_snippet_verified_strict(CANON, "en", out_en, CANON, max_attempts=3)
        elif site == "s5_news_tail_fix":
            r = ntf.generate_news_narration_wide_margin(CANON, out_en, max_attempts=3)
        elif site == "s6_point_headings":
            r = ph.generate(CANON, out_en, max_attempts=3)
        elif site == "s7_voice01_en":
            r = v01.generate_charon_english(CANON, out_en, max_attempts=3)
        else:
            r = bv.generate_voice_body_wide_margin(CANON, out_en, "Puck", max_attempts=3)
        return r, az
    # ja
    def trj(*a, **k):
        return ((LONG_JA if (not fb or len(n) >= 3) else JA_NG), None)
    monkeypatch.setattr(routing, "transcribe", trj)

    class _AzJa(AzJa):
        def __call__(self, wav_path, language="ja-JP", timeout_seconds=90.0):
            self.calls += 1
            if fb and len(n) < 3:
                return (JA_NG, None)
            return ((JA if secondary_ok else LONG_JA), None)
    azj = _AzJa()
    monkeypatch.setattr(ja, "_azure_stt_strict", azj)
    monkeypatch.setattr(ja, "_log_human_review", lambda d: None)
    dummy = str(tmp_path / "dummy.wav")
    if site == "s2_n3_ja_fallback":
        monkeypatch.setattr(n3, "_generate_a2_japanese_minimal_instruction", lambda text, out_path, tts_backend="x": (n.append(1), {"status": "OK", "path": out_path})[1])
        r = n3.generate_a2_japanese_with_fallback(JA, dummy, "ありがとう")
    elif site == "s4_repro01_ja":
        r = r1.generate_narration_snippet_verified_strict(JA, "ja", dummy, "ありがとう", max_attempts=3)
    elif site == "s8_voice01_ja_standard":
        monkeypatch.setattr(v01, "generate_charon_japanese_minimal_instruction", lambda text, out_path, tts_backend="x": (n.append(1), {"status": "OK", "path": out_path})[1])
        r = v01.generate_charon_japanese(JA, dummy, "ありがとう")
    else:
        monkeypatch.setattr(v01, "generate_charon_japanese_minimal_instruction", lambda text, out_path, tts_backend="x": (n.append(1), {"status": "OK", "path": out_path})[1])
        r = v01.generate_charon_japanese(JA, dummy, "ありがとう")
    return r, azj


def _judgement_of(r):
    j = r.get("asr_judgement")
    if j is None:
        for k in ("fallback_attempts_log", "attempts_log"):
            for a in reversed(r.get(k) or []):
                if a.get("asr_judgement"):
                    return a["asr_judgement"]
    return j


@pytest.mark.parametrize("site", list(SITES))
def test_14_caller_site_rescues_long_primary_when_secondary_matches_and_passes_max_len(site, tmp_path, monkeypatch):
    r, az = _drive(site, tmp_path, monkeypatch, secondary_ok=True)
    assert r["status"] == "OK", (site, r.get("status"), r.get("reason"))
    j = _judgement_of(r)
    assert j is not None and j["state"] == uj.PASS_WITH_WARNING, (site, j and j.get("state"), j and j.get("reason_code"))
    ln = j["length"]
    assert ln["applied"] is True and ln["adopted_from"] == "secondary" and ln["adopted_ok"] is True
    assert ln["max_len"] == SITES[site][1], (site, ln["max_len"])                       # R1: 呼出元ごとのmax_len
    assert ln["primary_ok"] is False and uj.W_PRIMARY_LENGTH_EXCESS in j["warnings"]


@pytest.mark.parametrize("site", list(SITES))
def test_15_caller_site_still_stops_when_secondary_transcript_also_exceeds_max_len(site, tmp_path, monkeypatch):
    r, az = _drive(site, tmp_path, monkeypatch, secondary_ok=False)
    assert r["status"] != "OK", (site, r.get("status"))                                  # 品質維持: Secondaryも長いなら不合格のまま


# ============================================================
# D. 静的監査(R3: Production 10箇所がmax_lenを渡し、Primary由来のANDが残っていない)
# ============================================================
PRODUCTION_FILES = {
    "er003_v1_crosslevel_audio_02_common.py": 1, "er003_v1_n3_01_tts_generate.py": 1, "er003_v1_repro01_main_generate.py": 2,
    "er003_v1_sing01_news_tail_fix.py": 1, "er003_v1_sing01_point_headings_aoede.py": 1, "er003_v1_sing01_voice01_generate.py": 3,
    "er012_b_family_voices_production_01.py": 1,
}
# legacy / Trial script(委任_11 IMPLEMENTATION_11.md §3-1。Production正式経路ではない=max_len未指定の旧挙動のまま)
LEGACY_TRIAL_EXCLUDED = {
    "er003_v1_b1_scaffold_audio_01_generate.py", "er003_v1_b1_scaffold_audio_03_generate.py", "er003_v1_iran01_b1_audio_fix.py",
    "er003_v1_sing01_audio_generate.py", "er010_no9_a2_keyphrase_article_reduction_trial_26.py",
    "er010_no9_keyphrase_english_lock_fallback_trial_21.py", "er010_no9_keyphrase_minimal_instruction_minitrial_20_r2.py",
    "er012_editorial_b_voices_trial_09_audio.py", "er038_tts_all_spoken_role_style_trial_01.py", "er057_tone_trial_final_build_03.py",
    "er058_kp_english_lock_trial_01.py",
}


def test_16_production_sites_pass_max_len_use_final_length_ok_and_no_primary_only_and_remains():
    total = 0
    for fn, expected in PRODUCTION_FILES.items():
        src = open(os.path.join(ROOT, fn), encoding="utf-8").read()
        assert "verified_content and length_ok" not in src, fn
        n_final = src.count("verified = verified_content and final_len_ok")
        assert n_final == expected, (fn, n_final)
        total += n_final
        # final_len_okはfinal_length_okの結果で、max_lenがattempt_ctxに入っている
        tree = ast.parse(src)
        calls = [c for c in ast.walk(tree) if isinstance(c, ast.Call)
                 and getattr(c.func, "attr", "") in ("evaluate_attempt_with_cascade", "evaluate_attempt_ja_with_cascade")]
        assert len(calls) >= expected, fn
        for c in calls:
            kw = {k.arg: ast.dump(k.value) for k in c.keywords}
            assert "attempt_ctx" in kw and "max_len" in kw["attempt_ctx"], (fn, c.lineno)
    assert total == 10


def test_17_every_remaining_primary_only_and_pattern_is_in_the_explicit_legacy_trial_list():
    pat = re.compile(r"verified_content and length_ok|(?:match\[\"passed\"\]|substring_ok) and length_ok")
    found = set()
    for fn in os.listdir(ROOT):
        if not fn.endswith(".py") or fn.endswith("_test_01.py") or fn.startswith("er078_asr_unified_wiring_13_test"):
            continue
        try:
            src = open(os.path.join(ROOT, fn), encoding="utf-8").read()
        except Exception:
            continue
        if pat.search(src):
            found.add(fn)
    # er058_kp_english_lock_trial_01.pyは別形(`cls.should_pass and length_ok`、primary_pass記録のみ)でこの正規表現に該当しないが除外listには載せる
    assert found <= LEGACY_TRIAL_EXCLUDED and not (found & set(PRODUCTION_FILES)), sorted(found ^ LEGACY_TRIAL_EXCLUDED)
    assert LEGACY_TRIAL_EXCLUDED - found <= {"er058_kp_english_lock_trial_01.py"}


def test_18_legacy_trial_scripts_never_pass_max_len_so_they_keep_the_old_behaviour():
    for fn in LEGACY_TRIAL_EXCLUDED:
        src = open(os.path.join(ROOT, fn), encoding="utf-8").read()
        assert "max_len=max_len))" not in src or "attempt_ctx" not in src, fn      # attempt_ctxにmax_lenを渡していない(安全ラッチ)


def test_19_disfluency_and_repetition_gate_order_unchanged_in_every_production_file():
    for fn in PRODUCTION_FILES:
        src = open(os.path.join(ROOT, fn), encoding="utf-8").read()
        for m in re.finditer(r"verified = verified_content and final_len_ok\n(.*?)\n", src):
            pass
        # AND順: length AND -> disfluency gate -> repetition gate(出現する場合は順序保持)
        i_and = src.find("verified = verified_content and final_len_ok")
        i_dis = src.find("apply_disfluency_gate", i_and)
        i_rep = src.find("apply_repetition_qa_gate", i_and)
        if i_dis != -1 and i_rep != -1:
            assert i_and < i_dis < i_rep, fn


def test_20_build_attempt_ctx_max_len_is_additive_and_default_absent():
    import er078_asr_unified_attempt_ctx_01 as a
    assert a.build_attempt_ctx(1, 3) == {"slot": 1, "is_last_slot": False, "script_version": "v0"}
    assert a.build_attempt_ctx(1, 3, max_len=47)["max_len"] == 47


def test_21_adapters_forward_max_len_and_default_none():
    d = sec.evaluate_attempt_with_cascade_detail(CANON, CANON, [], "nofile.wav", cascade_enabled=True, attempt_ctx={"is_last_slot": True})
    assert d["asr_judgement"]["length"]["max_len"] is None and d["asr_judgement"]["length"]["applied"] is False
    d2 = sec.evaluate_attempt_with_cascade_detail(CANON, CANON, [], "nofile.wav", cascade_enabled=True,
                                                  attempt_ctx={"is_last_slot": True, "max_len": 99})
    assert d2["asr_judgement"]["length"]["max_len"] == 99 and d2["asr_judgement"]["length"]["applied"] is True


def test_22_ja_length_not_ok_diagnostic_only_for_legacy_callers():
    src = open(os.path.join(ROOT, "er007_ja_secondary_asr_01.py"), encoding="utf-8").read()
    assert "max_len未指定の旧挙動" in src and "_a3_reeval_active(ctx)" in src
