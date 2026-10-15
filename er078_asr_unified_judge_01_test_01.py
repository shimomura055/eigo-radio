# AUW 委任_02b: 統一判定(er078_asr_unified_judge_01)のUnit test。mock engineのみ・API 0。
import math

import pytest

import er078_asr_unified_judge_01 as uj
from er078_asr_unified_judge_01 import (AttemptCtx, PrimaryResult, RunState, SecondaryCache, SecondaryOutcome, unified_judge)


class MockSecondary:
    def __init__(self, result="", raises=None):
        self.result = result
        self.raises = raises
        self.calls = 0

    def __call__(self, ctx):
        self.calls += 1
        if self.raises:
            raise self.raises
        return self.result


def ctx_(canon, sha="sha-A", **kw):
    return AttemptCtx(canonical_text=canon, wav_sha256=sha, audio_seconds=kw.pop("audio_seconds", 10.0), **kw)


EN_C = "The rate is 25% today and we waited."
JA_C = "三人で行きました。"


# ---- Primary PASS ----
def test_primary_pass_secondary_not_called():
    sec = MockSecondary("x")
    r = unified_judge(ctx_(EN_C), PrimaryResult(True, EN_C), sec, lang="en", role="full_story")
    assert r.state == uj.PASS and sec.calls == 0 and r.verified


def test_primary_pass_with_primary_warning_becomes_pass_with_warning():
    sec = MockSecondary("x")
    r = unified_judge(ctx_(EN_C), PrimaryResult(True, EN_C, warning_labels=("CONNECTED_SPEECH",)), sec, lang="en", role="full_story")
    assert r.state == uj.PASS_WITH_WARNING and "CONNECTED_SPEECH" in r.warning_labels and sec.calls == 0


def test_final_and_gate_stops_primary_pass_value_diff():
    sec = MockSecondary("x")
    r = unified_judge(ctx_(EN_C), PrimaryResult(True, "The rate is 26% today and we waited."), sec, lang="en", role="full_story")
    assert r.state == uj.NG_PROTECTED and r.reason_code == "final_gate_value_diff" and sec.calls == 0


def test_final_and_gate_stops_primary_pass_negation_diff():
    sec = MockSecondary("x")
    r = unified_judge(ctx_("We can go."), PrimaryResult(True, "We cannot go."), sec, lang="en", role="comment")
    assert r.state == uj.NG_PROTECTED and r.reason_code == "final_gate_negation_diff"


@pytest.mark.parametrize("basis", sorted(uj.APPROVED_EQUIVALENCE_BASES))
def test_final_gate_does_not_reject_approved_equivalence(basis):
    # 承認済みequivalence(例 HOMOPHONE_MATCH_NUMBER_EXCEPTION)は値ガードDIFFでも再否定しない
    sec = MockSecondary("x")
    r = unified_judge(ctx_("He bought 4 books."), PrimaryResult(True, "He bought for books.", equivalence_basis=basis), sec, lang="en", role="comment")
    assert r.state == uj.PASS and sec.calls == 0
    assert r.audit_record["final_gate"]["applied"] is False


def test_final_gate_ambiguous_without_basis_demotes_to_p3_not_pass_as_10min():
    sec = MockSecondary("十分待ちました。")
    r = unified_judge(ctx_("十分待ちました。"), PrimaryResult(True, "10分待ちました。"), sec, lang="ja", role="comment")
    assert sec.calls == 1
    assert r.state == uj.PASS_WITH_WARNING and uj.W_NUMERIC_AMBIGUOUS_SURFACE in r.warning_labels


def test_final_and_gate_off_flag():
    r = unified_judge(ctx_(EN_C), PrimaryResult(True, "The rate is 26% today and we waited."), MockSecondary("x"), lang="en", role="x",
                      final_and_gate=False)
    assert r.state == uj.PASS


# ---- Primary ASR failure ----
def test_primary_asr_failure():
    sec = MockSecondary("x")
    r = unified_judge(ctx_(EN_C), PrimaryResult(False, None), sec, lang="en", role="x")
    assert r.state == uj.NG_PRIMARY_ASR_FAILURE and sec.calls == 0 and not r.verified


# ---- P1 / P2: Secondary不呼出 ----
@pytest.mark.parametrize("lang,canon,hyp", [
    ("ja", JA_C, "四人で行きました。"),
    ("en", EN_C, "The rate is 26% today and we waited."),
    ("en", "He said 20% rose.", "He said 30% rose."),
])
def test_p1_value_diff_never_calls_secondary(lang, canon, hyp):
    sec = MockSecondary(canon)
    r = unified_judge(ctx_(canon), PrimaryResult(False, hyp), sec, lang=lang, role="x")
    assert r.state == uj.NG_PROTECTED and sec.calls == 0
    assert r.audit_record["secondary"]["called"] is False
    assert r.reason_code == "p1_value_diff"


@pytest.mark.parametrize("lang,canon,hyp", [
    ("en", "We can go home.", "We cannot go home."),
    ("en", "We did not go home.", "We did go home."),
    ("ja", "眠くならない。", "眠くなる。"),
])
def test_p1_negation_diff_never_calls_secondary(lang, canon, hyp):
    sec = MockSecondary(canon)
    r = unified_judge(ctx_(canon), PrimaryResult(False, hyp), sec, lang=lang, role="x")
    assert r.state == uj.NG_PROTECTED and sec.calls == 0 and r.reason_code == "p1_negation_diff"


def test_p2_exclusions_table(monkeypatch):
    sec = MockSecondary("x")
    # A3 length NG (en/ja共通)
    r = unified_judge(ctx_("Hello there friend.", length_ok=False), PrimaryResult(False, "Hello their friend."), sec, lang="en", role="x")
    assert r.state == uj.NG_EXCLUDED and r.audit_record["exclusion_rule"] == "A3_LENGTH_NG" and sec.calls == 0
    # A4 C2 同形異音 (ja)
    r = unified_judge(ctx_("今日は晴れ。"), PrimaryResult(False, "今日は晴れ", signals={"c2_homophone_candidate": True}), sec, lang="ja", role="x")
    assert r.state == uj.NG_EXCLUDED and r.audit_record["exclusion_rule"] == "A4_C2_HOMOGRAPH"
    # A5 類似度<0.4 / A6 C1 (委任_10: 既定は解放済み。旧挙動はU1=Trueのロールバック時のみ)
    monkeypatch.setattr(uj, "U1_KEEP_C1_SIMILARITY_EXCLUSIONS", True)
    r = unified_judge(ctx_("今日は晴れ。"), PrimaryResult(False, "全然違う", signals={"similarity": 0.2}), sec, lang="ja", role="x")
    assert r.state == uj.NG_EXCLUDED and r.audit_record["exclusion_rule"] == "A5_SIMILARITY_LT_0_4"
    r = unified_judge(ctx_("今日は晴れ。"), PrimaryResult(False, "今日は晴れ", signals={"c1_proper_noun_diff": True}), sec, lang="ja", role="x")
    assert r.state == uj.NG_EXCLUDED and r.audit_record["exclusion_rule"] == "A6_C1_PROPER_NOUN_DIFF"
    assert sec.calls == 0
    # A7 登録読み保護(U1に関係なく除外)
    monkeypatch.setattr(uj, "U1_KEEP_C1_SIMILARITY_EXCLUSIONS", False)
    r = unified_judge(ctx_("今日は晴れ。"), PrimaryResult(False, "今日は晴れ", signals={"reading_dictionary_mismatch": "x"}), sec, lang="ja", role="x")
    assert r.state == uj.NG_EXCLUDED and r.audit_record["exclusion_rule"] == "A7_READING_DICT_MISMATCH" and sec.calls == 0


def test_u1_flag_releases_a5_a6_in_one_line(monkeypatch):
    assert uj.U1_KEEP_C1_SIMILARITY_EXCLUSIONS is False  # 委任_11: U1発効済み(既定False)
    monkeypatch.setattr(uj, "U1_KEEP_C1_SIMILARITY_EXCLUSIONS", False)
    sec = MockSecondary("今日は晴れ。")
    r = unified_judge(ctx_("今日は晴れ。"), PrimaryResult(False, "全然違う", signals={"similarity": 0.2}), sec, lang="ja", role="x")
    assert sec.calls == 1 and r.state == uj.PASS_WITH_WARNING
    # A3(length)・A4(C2)はU1と無関係に維持
    r = unified_judge(ctx_("今日は晴れ。", length_ok=False), PrimaryResult(False, "全然違う"), sec, lang="ja", role="x")
    assert r.state == uj.NG_EXCLUDED


def test_exclusion_table_is_data_with_expected_ids():
    ids = [x.rule_id for x in uj.SCG_EXCLUSIONS]
    assert ids == ["A1_NUMBER_DIFF", "A2_NEGATION_DIFF", "A3_LENGTH_NG", "A4_C2_HOMOGRAPH", "A5_SIMILARITY_LT_0_4", "A6_C1_PROPER_NOUN_DIFF", "A7_READING_DICT_MISMATCH"]
    assert {x.rule_id for x in uj.SCG_EXCLUSIONS if x.u1_gated} == {"A5_SIMILARITY_LT_0_4", "A6_C1_PROPER_NOUN_DIFF"}


# ---- P3: Secondary 1回 ----
def test_p3_secondary_pass_gives_pass_with_warning():
    canon = "Researchers studied the parent child relationship."
    sec = MockSecondary(canon)
    r = unified_judge(ctx_(canon), PrimaryResult(False, "Researchers studied the parent child relation ship."), sec, lang="en", role="full_story")
    assert sec.calls == 1 and r.state == uj.PASS_WITH_WARNING
    assert uj.W_SECONDARY_CONFIRMED in r.warning_labels and r.verified


def test_p3_secondary_called_once_for_same_wav_via_cache():
    canon = "Researchers studied the parent child relationship."
    sec = MockSecondary(canon)
    cache = SecondaryCache()
    for _ in range(3):
        r = unified_judge(ctx_(canon, cache=cache), PrimaryResult(False, "Researchers studied the parent child relation ship."), sec,
                          lang="en", role="full_story")
    assert sec.calls == 1 and cache.hits == 2 and r.audit_record["secondary"]["cached"] is True


def test_cache_key_differs_for_different_wav_engine_lang_phrase():
    canon = "Researchers studied the parent child relationship."
    sec = MockSecondary(canon)
    cache = SecondaryCache()
    pr = PrimaryResult(False, "Researchers studied the parent child relation ship.")
    unified_judge(ctx_(canon, sha="A", cache=cache), pr, sec, lang="en", role="x")
    unified_judge(ctx_(canon, sha="B", cache=cache), pr, sec, lang="en", role="x")  # 別wav
    unified_judge(ctx_(canon, sha="A", cache=cache, phrase_list_hash="p2"), pr, sec, lang="en", role="x")
    unified_judge(ctx_(canon, sha="A", cache=cache, engine="azure2"), pr, sec, lang="en", role="x")
    assert sec.calls == 4


def test_p3_secondary_protected_diff_gives_ng_both():
    canon = "The rate is 25% today and we waited."
    # Primaryは内容語差のみ(P1非該当)、Secondary転写に値DIFF
    sec = MockSecondary("The rate is 26% today and we waited.")
    r = unified_judge(ctx_(canon), PrimaryResult(False, "The rate is 25% today and we wait it."), sec, lang="en", role="x")
    assert sec.calls == 1 and r.state == uj.NG_BOTH and r.reason_code == "secondary_value_diff"
    sec2 = MockSecondary("We cannot go home today.")
    r = unified_judge(ctx_("We can go home today."), PrimaryResult(False, "We can go home to day."), sec2, lang="en", role="x")
    assert r.state == uj.NG_BOTH and r.reason_code == "secondary_negation_diff"


def test_p3_secondary_not_in_accepted_set_gives_ng_both():
    canon = "Researchers studied the parent child relationship."
    sec = MockSecondary("Researchers studied the apparent chill relation.")
    r = unified_judge(ctx_(canon), PrimaryResult(False, "Researchers studied the parent child relation ship."), sec, lang="en", role="x")
    assert r.state == uj.NG_BOTH and r.reason_code == "secondary_not_accepted"


def test_accept_fn_injection_is_used_instead_of_reimplementing_classifier():
    canon = "Researchers studied the parent child relationship."
    calls = []

    def accept(c, t):
        calls.append((c, t))
        return True, "NORMALIZED_MATCH"

    sec = MockSecondary("researchers studied the parent-child relationship")
    r = unified_judge(ctx_(canon), PrimaryResult(False, "Researchers studied the parent child relation ship."), sec, lang="en", role="x",
                      secondary_accept_fn=accept)
    assert calls and r.state == uj.PASS_WITH_WARNING and r.audit_record["secondary"]["label"] == "NORMALIZED_MATCH"
    # SecondaryOutcome.accepted=False を注入側が返せばNG
    sec3 = MockSecondary(SecondaryOutcome("totally different text", accepted=False, label="TRUE_CONTENT_MISMATCH"))
    r = unified_judge(ctx_(canon, sha="Z"), PrimaryResult(False, "x y z"), sec3, lang="en", role="x")
    assert r.state == uj.NG_BOTH


def test_ambiguous_p3_secondary_same_surface_gives_warning():
    sec = MockSecondary("十分待ちました。")
    r = unified_judge(ctx_("十分待ちました。"), PrimaryResult(False, "10分待ちました。"), sec, lang="ja", role="comment")
    assert sec.calls == 1
    assert r.state == uj.PASS_WITH_WARNING and r.warning_labels == [uj.W_NUMERIC_AMBIGUOUS_SURFACE]


def test_ambiguous_p3_secondary_same_10min_is_ng_both():
    sec = MockSecondary("10分待ちました。")
    r = unified_judge(ctx_("十分待ちました。"), PrimaryResult(False, "10分待ちました。"), sec, lang="ja", role="comment")
    assert r.state == uj.NG_BOTH and r.reason_code in ("ambiguous_value_secondary_not_same_surface", "secondary_ambiguous_value_not_same_surface")


def test_ja_irregular_reading_warning_propagates_on_primary_pass():
    r = unified_judge(ctx_("二十歳になりました。"), PrimaryResult(True, "はたちになりました。"), MockSecondary("x"), lang="ja", role="x")
    assert r.state == uj.PASS_WITH_WARNING and uj.W_JA_NUMERIC_IRREGULAR_READING in r.warning_labels


# ---- Secondary障害 ----
@pytest.mark.parametrize("result,raises", [(None, None), ("", None), ("   ", None), (None, TimeoutError("timeout")),
                                           (SecondaryOutcome(None, error="http 500"), None), (None, RuntimeError("boom"))])
def test_secondary_failure_cannot_pass_and_is_not_cached(result, raises):
    canon = "Researchers studied the parent child relationship."
    sec = MockSecondary(result, raises=raises)
    cache = SecondaryCache()
    rs = RunState()
    r = unified_judge(ctx_(canon, cache=cache, run_state=rs), PrimaryResult(False, "Researchers studied the parent child relation ship."),
                      sec, lang="en", role="x")
    assert r.state == uj.NG_SECONDARY_UNAVAILABLE and r.secondary_unavailable and not r.verified
    assert r.audit_record["technical_stop"]["restartable"] is True and r.audit_record["technical_stop"]["approval_required"] is False
    assert cache._store == {}  # 失敗は非キャッシュ
    # 同一wavで再試行 -> 再度Secondaryが呼ばれる(失敗結果を再利用しない)
    unified_judge(ctx_(canon, cache=cache, run_state=rs), PrimaryResult(False, "Researchers studied the parent child relation ship."),
                  sec, lang="en", role="x")
    assert sec.calls == 2
    assert rs.secondary_failures_total == 2 and len(rs.technical_stop_events) >= 2
    assert not hasattr(rs, "human_review_lock")  # Lock状態は増やさない


def test_circuit_breaker_stops_secondary_calls_after_consecutive_failures():
    canon = "Researchers studied the parent child relationship."
    sec = MockSecondary(None)
    rs = RunState(circuit_breaker_threshold=3)
    for i in range(3):
        unified_judge(ctx_(canon, sha=f"w{i}", run_state=rs), PrimaryResult(False, "Researchers studied the parent child relation ship."),
                      sec, lang="en", role="x")
    assert rs.circuit_open is True and sec.calls == 3
    r = unified_judge(ctx_(canon, sha="w9", run_state=rs), PrimaryResult(False, "Researchers studied the parent child relation ship."),
                      sec, lang="en", role="x")
    assert sec.calls == 3  # open後はSecondaryを呼ばない
    assert r.state == uj.NG_SECONDARY_UNAVAILABLE and r.reason_code == "secondary_circuit_open"
    assert any(e["type"] == "SECONDARY_CIRCUIT_OPEN" for e in rs.technical_stop_events)


def test_success_resets_consecutive_failure_counter():
    canon = "Researchers studied the parent child relationship."
    rs = RunState(circuit_breaker_threshold=3)
    bad, good = MockSecondary(None), MockSecondary(canon)
    pr = PrimaryResult(False, "Researchers studied the parent child relation ship.")
    unified_judge(ctx_(canon, sha="a", run_state=rs), pr, bad, lang="en", role="x")
    unified_judge(ctx_(canon, sha="b", run_state=rs), pr, bad, lang="en", role="x")
    unified_judge(ctx_(canon, sha="c", run_state=rs), pr, good, lang="en", role="x")
    assert rs.secondary_consecutive_failures == 0 and rs.circuit_open is False


# ---- LR後v1 / force_secondary ----
def test_lr_v1_always_pass_with_warning_lr_rewritten():
    r = unified_judge(ctx_(EN_C, script_version="v1"), PrimaryResult(True, EN_C), MockSecondary("x"), lang="en", role="x")
    assert r.state == uj.PASS_WITH_WARNING and uj.W_LR_REWRITTEN in r.warning_labels


def test_force_secondary_requires_secondary_even_on_primary_pass():
    sec = MockSecondary(EN_C)
    r = unified_judge(ctx_(EN_C, script_version="v1", force_secondary=True), PrimaryResult(True, EN_C), sec, lang="en", role="x")
    assert sec.calls == 1 and r.state == uj.PASS_WITH_WARNING
    sec2 = MockSecondary("a completely different sentence now")
    r = unified_judge(ctx_(EN_C, sha="Q", script_version="v1", force_secondary=True), PrimaryResult(True, EN_C), sec2, lang="en", role="x")
    assert r.state == uj.NG_BOTH


# ---- est_jpy・監査record ----
def test_est_jpy_seconds_based_same_formula_as_scg():
    assert uj.est_jpy_for_seconds(None) is None
    assert uj.est_jpy_for_seconds(10) == round(10 * 1.0 / 3600.0 * 160.0, 4)
    assert uj.est_jpy_for_seconds(10.2) == uj.est_jpy_for_seconds(11)  # 秒切上げ
    canon = "Researchers studied the parent child relationship."
    rs = RunState()
    r = unified_judge(ctx_(canon, audio_seconds=30.0, run_state=rs), PrimaryResult(False, "Researchers studied the parent child relation ship."),
                      MockSecondary(canon), lang="en", role="x")
    assert r.audit_record["cost"]["est_jpy"] == round(30 * 160.0 / 3600.0, 4) and rs.est_jpy_total == r.audit_record["cost"]["est_jpy"]
    # キャッシュヒット時は追加費用なし
    r2 = unified_judge(ctx_(canon, audio_seconds=30.0, run_state=rs, cache=None), PrimaryResult(False, "Researchers studied the parent child relation ship."),
                       MockSecondary(canon), lang="en", role="x")
    assert r2.audit_record["cost"]["azure_calls"] == 1  # cache=Noneは新規cache(別instance)


def test_est_jpy_cache_hit_no_extra_cost():
    canon = "Researchers studied the parent child relationship."
    cache = SecondaryCache()
    sec = MockSecondary(canon)
    pr = PrimaryResult(False, "Researchers studied the parent child relation ship.")
    a = unified_judge(ctx_(canon, audio_seconds=20, cache=cache), pr, sec, lang="en", role="x")
    b = unified_judge(ctx_(canon, audio_seconds=20, cache=cache), pr, sec, lang="en", role="x")
    assert a.audit_record["cost"]["azure_calls"] == 1 and b.audit_record["cost"]["azure_calls"] == 0 and b.audit_record["cost"]["est_jpy"] == 0.0


def test_audit_record_fields():
    canon = "Researchers studied the parent child relationship."
    r = unified_judge(ctx_(canon, segment_key="seg1", slot=2), PrimaryResult(False, "Researchers studied the parent child relation ship."),
                      MockSecondary(canon), lang="en", role="full_story")
    a = r.audit_record
    for k in ("state", "reason_code", "slot", "script_version", "primary", "secondary", "value_guard", "negation_guard", "warnings", "cost", "timing"):
        assert k in a
    assert a["primary"]["text"] and a["secondary"]["text"] == canon and a["timing"]["total_ms"] >= 0 and a["slot"] == 2
    assert a["value_guard"]["primary"]["kind"] == "NO_VALUES"


def test_unsupported_lang_raises():
    with pytest.raises(ValueError):
        unified_judge(ctx_("x"), PrimaryResult(True, "x"), MockSecondary("x"), lang="fr", role="x")


def test_judge_module_has_no_own_asr_classifier_or_api_calls():
    import ast
    import inspect
    tree = ast.parse(inspect.getsource(uj))
    called = {n.func.attr if isinstance(n.func, ast.Attribute) else getattr(n.func, "id", "") for n in ast.walk(tree) if isinstance(n, ast.Call)}
    assert not (called & {"transcribe", "classify_asr_match", "classify_ja_asr_match", "evaluate_attempt", "post", "urlopen"})
    imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    imported |= {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    assert not any(m and (m.startswith("openai") or m.startswith("requests") or m.startswith("azure")) for m in imported)


def test_parity_with_scg_constants_and_formula():
    import er007_ja_secondary_asr_01 as scg
    assert uj.AZURE_USD_PER_HOUR == scg.SCG_AZURE_USD_PER_HOUR
    assert uj.JPY_PER_USD == scg.SCG_JPY_PER_USD
    assert uj.SCG_MIN_SIMILARITY == scg.SCG_MIN_SIMILARITY
    assert uj.est_jpy_for_seconds(37.2) == round(math.ceil(37.2) * scg.SCG_AZURE_USD_PER_HOUR / 3600.0 * scg.SCG_JPY_PER_USD, 4)
