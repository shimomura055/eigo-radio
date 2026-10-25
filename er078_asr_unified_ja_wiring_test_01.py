# AUW 委任_04: JA統一judge配線(adapter)・J11継承再判定・Section固有例外維持のtest。
# 全てmock(Primary ASR=渡すtext、Secondary=er007_ja_secondary_asr_01._azure_stt_strict)。API呼出0・費用JPY0。
import copy
import inspect
import json
import os
import unittest.mock as mock
import wave

import numpy as np
import pytest

import er006_asr_provider_routing_01 as routing
import er006_secondary_asr_01 as en_sec
import er007_ja_asr_validator_01 as javal
import er007_ja_secondary_asr_01 as ja
import er011_human_review_lock_01 as review_lock
import er019_family_x_validation_inheritance_01 as vi
import er078_asr_unified_judge_01 as uj
import er078_pass_with_warning_registry_01 as reg

CANON = "AIの電話に人間が出演。問題は「キャスト変更」のお知らせでした"
PRIMARY_NG = "AIの電話に人間が出現。問題は、キャスト変更のお知らせでした。"
AZURE_OK = "AIの電話に人間が出演。問題はキャスト変更のお知らせでした。"   # NORMALIZED_MATCH
AZURE_NG = "AIの電話に人間が出現。問題はキャスト変更のお知らせでした。"


class Az:
    """Secondary(Azure strict)のmock。calls=実呼出回数。"""

    def __init__(self, result=(None, "no result"), raises=None):
        self.result, self.raises, self.calls = result, raises, 0

    def __call__(self, wav_path, language="ja-JP", timeout_seconds=90.0):
        self.calls += 1
        if self.raises:
            raise self.raises
        return self.result


@pytest.fixture(autouse=True)
def _iso(monkeypatch):
    en_sec.reset_secondary_cache()
    monkeypatch.setattr(en_sec, "_RUN_STATE", None)
    monkeypatch.setattr(en_sec, "_RUN_CACHE", None)
    monkeypatch.setattr(javal, "FEATURE_FLAG_A2_READING_RESOLVER_ENABLED", False)   # LLM(Reading Resolver)をOFF=課金0
    # Primary#2(同一音声のOpenAI再転写)が呼ばれたら失敗(廃止の確認)
    monkeypatch.setattr(routing, "_transcribe_openai_mini", lambda *a, **k: pytest.fail("Primary#2は廃止のはず"))
    yield
    en_sec.reset_secondary_cache()


def run(canon, primary, az, monkeypatch, wav="dummy.wav", **kw):
    monkeypatch.setattr(ja, "_azure_stt_strict", az)
    kw.setdefault("cascade_enabled", True)
    return ja.evaluate_attempt_ja_with_cascade_detail(canon, primary, wav, **kw)


def _wav(tmp_path, name="a.wav", seconds=1, rate=8000, fill=b"\x00"):
    p = tmp_path / name
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(1)
        w.setframerate(rate)
        w.writeframes(fill * (rate * seconds))
    return str(p)


# ============================================================
# 1. 状態機械(JA)
# ============================================================
def test_primary_pass_never_calls_secondary_and_has_judgement(monkeypatch):
    az = Az()
    d = run(CANON, CANON, az, monkeypatch)
    assert d["verified"] is True and az.calls == 0 and d["cascade_invoked"] is False
    assert d["asr_judgement"]["state"] == uj.PASS and d["asr_judgement"]["secondary"]["called"] is False


def test_primary_ng_secondary_pass_is_pass_with_warning_and_adopted(monkeypatch):
    az = Az((AZURE_OK, None))
    d = run(CANON, PRIMARY_NG, az, monkeypatch)
    j = d["asr_judgement"]
    assert d["verified"] is True and az.calls == 1
    assert j["state"] == uj.PASS_WITH_WARNING and uj.W_SECONDARY_CONFIRMED in j["warnings"]
    assert d["final_status"] == ja.SCG_FINAL_STATUS and d["classification"].should_pass
    assert d["classification"].scg_info["scg_result"] == "PASS"       # 呼出元キー(scg_info)維持
    assert j["primary"]["text"] == PRIMARY_NG and j["secondary"]["text"] == AZURE_OK


def test_secondary_also_ng_is_ng_both_and_next_regeneration(monkeypatch):
    az = Az((AZURE_NG, None))
    d = run(CANON, PRIMARY_NG, az, monkeypatch)
    assert d["verified"] is False and d["stop_retrying"] is False and az.calls == 1
    assert d["asr_judgement"]["state"] == uj.NG_BOTH and d["human_review_required"] is False


# 委任_10 R2: Az(("", None))[エラーなし完了の空転写]は障害ではなくNG_BOTH(tests: er078_asr_unified_wiring_10_test_01.py)。
@pytest.mark.parametrize("az", [Az((None, "boom")), Az(raises=RuntimeError("down"))])
def test_secondary_unavailable_is_never_pass(az, monkeypatch):
    d = run(CANON, PRIMARY_NG, az, monkeypatch)
    assert d["verified"] is False
    assert d["asr_judgement"]["state"] == uj.NG_SECONDARY_UNAVAILABLE and d["asr_judgement"]["secondary"]["unavailable"] is True
    assert d["asr_judgement"]["technical_stop"]["type"] == "SECONDARY_UNAVAILABLE"


def test_primary_asr_failure(monkeypatch):
    az = Az((AZURE_OK, None))
    d = run(CANON, None, az, monkeypatch)
    assert d["verified"] is False and az.calls == 0 and d["asr_judgement"]["state"] == uj.NG_PRIMARY_ASR_FAILURE


def test_last_slot_ng_sets_human_review_only_when_last(monkeypatch):
    az = Az((AZURE_NG, None))
    assert run(CANON, PRIMARY_NG, az, monkeypatch)["human_review_required"] is False
    assert run(CANON, PRIMARY_NG, Az((AZURE_NG, None)), monkeypatch, attempt_ctx={"is_last_slot": True})["human_review_required"] is True
    # 最終slotでもPASSならHRなし
    assert run(CANON, PRIMARY_NG, Az((AZURE_OK, None)), monkeypatch, attempt_ctx={"is_last_slot": True})["human_review_required"] is False


def test_cascade_disabled_matches_plain_classify_no_judge(monkeypatch):
    az = Az()
    d = run("定期サービスをやめにくくする仕組み", "定期サービスをやめにくくする仕組み", az, monkeypatch, cascade_enabled=False)
    assert d["verified"] is True and "asr_judgement" not in d and az.calls == 0


# ============================================================
# 2. 値ガード(JA): DIFF -> NG_PROTECTED / EQUAL -> Primary PASS / AMBIGUOUS -> P3
# ============================================================
@pytest.mark.parametrize("canon,asr", [
    ("三人が来ました。", "四人が来ました。"),            # 漢数字の値違い(ユーザー原文の必須負例)
    ("三十人が来ました。", "40人が来ました。"),
    ("売上は25％増えました。", "売上は26％増えました。"),
    ("150人の女性を対象とした調査", "140人の女性を対象とした調査"),
])
def test_value_diff_is_ng_protected_even_when_secondary_would_pass(canon, asr, monkeypatch):
    az = Az((canon, None))      # Secondaryが原稿と一致を返しても、値DIFFはSecondary不呼出で不採用
    d = run(canon, asr, az, monkeypatch)
    assert d["verified"] is False and az.calls == 0
    assert d["asr_judgement"]["state"] == uj.NG_PROTECTED


def test_secondary_transcript_value_diff_is_ng_both(monkeypatch):
    # Primaryは値DIFFなし(固有名詞系の差)だが、Secondary転写が値DIFFなら不採用
    canon = "AIの電話に三人が出演。問題は「キャスト変更」のお知らせでした"
    primary = "AIの電話に三人が出現。問題は、キャスト変更のお知らせでした。"
    az = Az(("AIの電話に四人が出演。問題はキャスト変更のお知らせでした。", None))
    d = run(canon, primary, az, monkeypatch)
    assert d["verified"] is False and d["asr_judgement"]["state"] == uj.NG_BOTH
    assert d["asr_judgement"]["reason_code"] == "secondary_value_diff"


@pytest.mark.parametrize("canon,asr", [
    ("三十人が来ました。", "30人が来ました。"),
    ("三人が来ました。", "3人が来ました。"),
    ("百円で買いました。", "100円で買いました。"),
    ("1万2000人が来ました。", "一万二千人が来ました。"),
])
def test_value_equal_notation_difference_passes_at_primary_without_secondary(canon, asr, monkeypatch):
    az = Az()
    d = run(canon, asr, az, monkeypatch)
    assert d["verified"] is True and az.calls == 0
    assert d["final_status"] == ja.NUMERIC_VALUE_EQUIVALENT_MATCH
    assert d["asr_judgement"]["state"] == uj.PASS and d["asr_judgement"]["adapter"]["layers"] == ["numeric_value_equivalence"]


def test_value_equal_but_other_text_differs_is_not_rescued_by_equivalence_layer(monkeypatch):
    # 数値表記だけ違うのではなく、他の語も違う -> 値等価層では救わない(既存判定のまま)
    az = Az((None, "unavailable"))
    d = run("三十人がバナナを食べました。", "30人がリンゴを食べました。", az, monkeypatch)
    assert d["verified"] is False and d["final_status"] != ja.NUMERIC_VALUE_EQUIVALENT_MATCH


def test_ambiguous_juubun_requires_same_surface_secondary(monkeypatch):
    canon, asr = "十分な量です。", "10分な量です。"
    d = run(canon, asr, Az((canon, None)), monkeypatch)                    # 同表層 -> NUMERIC_AMBIGUOUS_SURFACE
    assert d["verified"] is True and d["asr_judgement"]["state"] == uj.PASS_WITH_WARNING
    assert uj.W_NUMERIC_AMBIGUOUS_SURFACE in d["asr_judgement"]["warnings"]
    az = Az(("充分な量です。", None))                                       # 異表層 -> NG
    d2 = run(canon, asr, az, monkeypatch)
    assert d2["verified"] is False and az.calls == 1 and d2["asr_judgement"]["state"] == uj.NG_BOTH


def test_negation_reversal_is_ng_protected_no_secondary(monkeypatch):
    az = Az(("解約を変えるために作った", None))
    d = run("解約を変えるために作った", "解約を変えないために作った", az, monkeypatch)
    assert d["verified"] is False and az.calls == 0 and d["asr_judgement"]["state"] == uj.NG_PROTECTED


def test_reading_match_is_subject_to_final_gate_and_passes_when_no_diff(monkeypatch):
    # OPEN-517(2026-10-25、承認済み安全条件の不具合是正): 読み一致(PHONETIC_MATCH)のPrimary PASSにも最終ANDゲートを適用する(旧: 『再否定しない』skip)。
    # 否定語を含むが原稿と転写で同じ(否定差なし)なので、最終ゲートは適用されたうえでPASS維持(Secondary不呼出)。理由は承認根拠skipではなく primary_pass。
    az = Az()
    d = run("解約できない仕組み", "かいやくできないしくみ", az, monkeypatch)
    assert d["verified"] is True and az.calls == 0
    assert d["asr_judgement"]["primary"]["equivalence_basis"] == "READING_MATCH"
    fg = d["asr_judgement"]["final_gate"]
    assert fg["applied"] is True and "skipped" not in fg and fg["negation_diff"] is False
    assert d["asr_judgement"]["reason_code"] == "primary_pass"


def test_irregular_numeric_reading_is_warning(monkeypatch):
    d = run("二十歳になりました。", "はたちになりました。", Az(), monkeypatch)
    assert d["verified"] is True and d["asr_judgement"]["state"] == uj.PASS_WITH_WARNING
    assert "JA_NUMERIC_IRREGULAR_READING" in d["asr_judgement"]["warnings"]


# ============================================================
# 3. 既存の除外(U1現行維持 / C2 / length / SCG flag / COST_GUARD)
# ============================================================
def test_u1_constants_unchanged():
    # 委任_10: s1条件付きSTOPにより既定は暫定True(旧挙動)。Fable判断で解放(False)する際は judge定数と、このassertと
    # er078_asr_unified_wiring_10_test_01.py::test_u1_default_state_documented の2箇所だけを更新する。
    # U2死定数は撤去(呼出点は静的testで固定: er078_asr_unified_wiring_10_test_01.py)
    assert uj.U1_KEEP_C1_SIMILARITY_EXCLUSIONS is False and not hasattr(uj, "U2_FORCE_SECONDARY_SCOPE")  # 委任_11: U1発効


def test_c1_proper_noun_and_low_similarity_excluded_u1_current(monkeypatch):
    monkeypatch.setattr(uj, "U1_KEEP_C1_SIMILARITY_EXCLUSIONS", True)   # 委任_10: 既定値に依存せず旧挙動を固定
    canon = "解約を難しくする壁は、「スラッジ」と考えられます。"      # UNCERTAIN(entity_like)ではなくTCM側のC1: Latin含む原稿差
    az = Az((canon, None))
    d = run("Metaが説明しました。今日は晴れです。", "Beta が説明しました。今日は晴れです。", az, monkeypatch)
    sig = d["asr_judgement"]
    if d["classification"].classification == "TRUE_CONTENT_MISMATCH":
        assert d["verified"] is False and az.calls == 0 and sig["state"] == uj.NG_EXCLUDED
        assert d["scg_info"]["exclusion_reason"].startswith(("latin_in_canonical_diff", "entity_like_diff", "reading_dictionary_mismatch"))
    d2 = run("あ" * 30, "ん" * 30, Az((None, "x")), monkeypatch)       # 類似度0.4未満
    assert d2["verified"] is False and d2["asr_judgement"]["state"] == uj.NG_EXCLUDED
    assert d2["scg_info"]["exclusion_reason"].startswith("similarity_lt_0.4")


def test_u1_release_flag_changes_behavior_only_via_constant(monkeypatch):
    # U1を解放した場合のみ類似度<0.4でもSecondaryを呼ぶ(委任_10: 既定は暫定True)
    monkeypatch.setattr(uj, "U1_KEEP_C1_SIMILARITY_EXCLUSIONS", False)
    az = Az(("あ" * 30, None))
    d = run("あ" * 30, "ん" * 30, az, monkeypatch)
    assert az.calls == 1 and d["verified"] is True


def test_length_ng_excluded_without_secondary(monkeypatch):
    az = Az((AZURE_OK, None))
    d = run(CANON, PRIMARY_NG, az, monkeypatch, length_ok=False)
    assert d["verified"] is False and az.calls == 0 and d["asr_judgement"]["state"] == uj.NG_EXCLUDED
    assert "length_not_ok" in d["scg_info"]["exclusion_reason"]


def test_scg_emergency_flag_off_never_calls_azure(monkeypatch):
    monkeypatch.setattr(ja, "FEATURE_FLAG_JA_SCG_ENABLED", False)
    az = Az((AZURE_OK, None))
    d = run(CANON, PRIMARY_NG, az, monkeypatch)
    assert d["verified"] is False and az.calls == 0 and d["scg_result"] == "DISABLED_BY_FLAG"
    monkeypatch.setenv("JA_SCG_ENABLED", "0")
    monkeypatch.setattr(ja, "FEATURE_FLAG_JA_SCG_ENABLED", True)
    assert run(CANON, PRIMARY_NG, Az((AZURE_OK, None)), monkeypatch)["scg_result"] == "DISABLED_BY_FLAG"


def test_cost_guard_actual_seconds_fail_closed(monkeypatch):
    az = Az((AZURE_OK, None))
    monkeypatch.setattr(ja, "_wav_duration_seconds", lambda p: 200.0)     # 200秒 > 180秒(=$0.05)
    d = run(CANON, PRIMARY_NG, az, monkeypatch)
    assert az.calls == 0 and d["cost_guard_triggered"] is True
    assert d["asr_judgement"]["state"] == uj.NG_SECONDARY_UNAVAILABLE and d["verified"] is False
    monkeypatch.setattr(ja, "_wav_duration_seconds", lambda p: 179.0)
    az2 = Az((AZURE_OK, None))
    d2 = run(CANON, PRIMARY_NG, az2, monkeypatch)
    assert az2.calls == 1 and d2["verified"] is True


def test_scg_cost_formula_values_unchanged():
    assert ja.SCG_AZURE_USD_PER_HOUR == 1.0 and ja.SCG_JPY_PER_USD == 160.0 and ja.SCG_MIN_SIMILARITY == 0.4
    assert ja.SCG_PASS_CLASSIFICATIONS == ("EXACT_MATCH", "NORMALIZED_MATCH")
    assert uj.AZURE_USD_PER_HOUR == ja.SCG_AZURE_USD_PER_HOUR and uj.JPY_PER_USD == ja.SCG_JPY_PER_USD
    assert uj.est_jpy_for_seconds(10) == round(10 * 1.0 / 3600 * 160, 4)


# ============================================================
# 4. Secondary重複呼出防止(SecondaryCache共有)
# ============================================================
def test_same_wav_secondary_called_once_across_attempt_calls(monkeypatch, tmp_path):
    wav = _wav(tmp_path)
    az = Az((AZURE_NG, None))
    cache = uj.SecondaryCache()
    for _ in range(3):
        run(CANON, PRIMARY_NG, az, monkeypatch, wav=wav, attempt_ctx={"cache": cache})
    assert az.calls == 1 and cache.hits == 2


def test_failed_secondary_is_not_cached(monkeypatch, tmp_path):
    wav = _wav(tmp_path)
    az = Az((None, "boom"))
    cache = uj.SecondaryCache()
    run(CANON, PRIMARY_NG, az, monkeypatch, wav=wav, attempt_ctx={"cache": cache})
    run(CANON, PRIMARY_NG, az, monkeypatch, wav=wav, attempt_ctx={"cache": cache})
    assert az.calls == 2     # 失敗は非cache


def test_run_level_cache_shared_with_en_adapter_when_run_started(monkeypatch, tmp_path):
    wav = _wav(tmp_path)
    az = Az((AZURE_NG, None))
    st = en_sec.begin_secondary_run()
    try:
        run(CANON, PRIMARY_NG, az, monkeypatch, wav=wav)
        run(CANON, PRIMARY_NG, az, monkeypatch, wav=wav)
        assert az.calls == 1                     # EN adapterのrun cache(begin_secondary_run)をJAも共有
        assert st.secondary_calls == 1
    finally:
        en_sec.end_secondary_run()


def test_circuit_breaker_opens_after_consecutive_failures(monkeypatch, tmp_path):
    az = Az((None, "down"))
    st = en_sec.begin_secondary_run(circuit_breaker_threshold=2)
    try:
        for i in range(4):
            run(CANON, PRIMARY_NG, az, monkeypatch, wav=_wav(tmp_path, f"w{i}.wav", fill=bytes([i + 1])))
        assert st.circuit_open is True and az.calls == 2      # 3回目以降はAzureを呼ばない
    finally:
        en_sec.end_secondary_run()


# ============================================================
# 5. ORTHOGRAPHIC_VARIANT_CONFIRMED(Primary#1 + Secondary#1 の2エンジン確認): 制御のみmockで固定
# ============================================================
def test_orthographic_variant_requires_two_engines(monkeypatch):
    canon = "聞き終えるころには、変化が始まっている。"
    asr = "聞き終える頃には、変化が始まっている。"
    unc = javal.ClassificationResultJA("ASR_VALIDATION_UNCERTAIN", 0.9, javal.ProtectedCheckResultJA(passed=True),
                                       should_pass=False, should_retry=False, reason="x")
    monkeypatch.setattr(javal, "classify_ja_asr_match", lambda c, a, **k: unc)
    monkeypatch.setattr(ja, "_apply_variant_layer_voicing_upgrade", lambda c, a, s: s)
    monkeypatch.setattr(ja, "_orthographic_reading_confirmed", lambda s: True)
    d = run(canon, asr, Az((asr, None)), monkeypatch)
    assert d["verified"] is True and d["final_status"] == ja.ORTHOGRAPHIC_VARIANT_CONFIRMED
    assert d["asr_judgement"]["state"] == uj.PASS_WITH_WARNING
    # Primary側が読み候補を満たさない(=単一エンジンだけが満たす)なら確定しない
    calls = iter([True, False])
    monkeypatch.setattr(ja, "_orthographic_reading_confirmed", lambda s: next(calls))
    d2 = run(canon, asr, Az((asr, None)), monkeypatch)
    assert d2["verified"] is False


# ============================================================
# 6. Section固有例外の維持: 日本語KP/日本語LRは原則HR(統一judgeはLRを提案しない・JA leafはLRを呼ばない)
# ============================================================
def test_ja_adapter_and_judge_have_no_local_rewrite_path():
    src = inspect.getsource(ja)
    assert "local_rewrite" not in src and "run_local_rewrite_recovery" not in src
    ju = inspect.getsource(uj)
    assert "local_rewrite" not in ju.lower() and "run_local_rewrite" not in ju
    for st in (uj.PASS, uj.PASS_WITH_WARNING, uj.NG_PROTECTED, uj.NG_EXCLUDED, uj.NG_BOTH, uj.NG_SECONDARY_UNAVAILABLE,
               uj.NG_PRIMARY_ASR_FAILURE):
        assert st != "LR"


def test_ja_leaf_functions_do_not_call_local_rewrite_and_end_in_stopped_for_hr_lock():
    import er003_v1_n3_01_tts_generate as n3
    import er003_v1_sing01_voice01_generate as v01
    for fn in (v01.generate_charon_japanese, n3.generate_a2_japanese_with_fallback):
        src = inspect.getsource(fn)
        assert "run_local_rewrite" not in src and "local_rewrite" not in src.lower().replace("local rewrite", "")
        assert '"status": "STOPPED"' in src          # 3NG -> STOPPED -> 既存のHR Lock(record_outcome)経路
    assert "guarded_generate" in inspect.getsource(n3).split("def generate_a2_japanese_with_fallback")[0][-400:]


def test_hr_lock_module_not_modified_by_wiring():
    import subprocess
    out = subprocess.run(["git", "diff", "--name-only", "HEAD", "--", "er011_human_review_lock_01.py"],
                         capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__))).stdout
    assert out.strip() == ""


# ============================================================
# 7. 呼出元互換
# ============================================================
OLD_DETAIL_KEYS = {"verified", "stop_retrying", "classification", "cascade_invoked", "steps", "final_status",
                   "human_review_required", "canonical_text", "wav_path"}


def test_detail_keys_superset_and_wrapper_tuple_and_detail_out(monkeypatch):
    monkeypatch.setattr(ja, "_azure_stt_strict", Az((AZURE_OK, None)))
    d = ja.evaluate_attempt_ja_with_cascade_detail(CANON, PRIMARY_NG, "dummy.wav", cascade_enabled=True)
    assert OLD_DETAIL_KEYS <= set(d) and {"asr_judgement", "scg_applied", "scg_result", "scg_info"} <= set(d)
    out = {}
    v, stop, cls = ja.evaluate_attempt_ja_with_cascade(CANON, PRIMARY_NG, "dummy.wav", detail_out=out)
    assert v is True and stop is False and cls.classification == ja.SCG_FINAL_STATUS and "asr_judgement" in out
    sig = inspect.signature(ja.evaluate_attempt_ja_with_cascade_detail)
    for k in ("cascade_enabled", "expected_readings", "length_ok", "attempt_ctx"):
        assert k in sig.parameters
    # 呼出元(leaf)が使う旧引数だけで呼べる
    ja.evaluate_attempt_ja_with_cascade(CANON, CANON, "dummy.wav", cascade_enabled=True, expected_readings=None, length_ok=True)


def test_all_ja_callers_are_enumerated_and_use_wrapper():
    # 全呼出点(Production)のGrep結果を固定: leaf 4 module / 5 call site。判定はadapter(wrapper)経由のみ。
    import re
    root = os.path.dirname(os.path.abspath(__file__))
    prod = ["er003_v1_n3_01_tts_generate.py", "er003_v1_repro01_main_generate.py", "er003_v1_sing01_voice01_generate.py",
            "er038_tts_all_spoken_role_style_trial_01.py"]
    counts = {m: len(re.findall(r"= ja_secondary\.evaluate_attempt_ja_with_cascade\(", open(os.path.join(root, m), encoding="utf-8").read()))
              for m in prod}
    assert counts == {"er003_v1_n3_01_tts_generate.py": 1, "er003_v1_repro01_main_generate.py": 1,
                      "er003_v1_sing01_voice01_generate.py": 2, "er038_tts_all_spoken_role_style_trial_01.py": 2}, counts


# ============================================================
# 8. e2e(mock): JA Primary NG・Secondary PASS の音声が最終成果物でPASS_WITH_WARNINGとして採用され、試聴リストに載る
# ============================================================
def test_e2e_voice01_ja_primary_ng_secondary_pass_to_listening_list(tmp_path, monkeypatch):
    import er003_v1_sing01_voice01_generate as v01
    monkeypatch.setattr(ja, "_azure_stt_strict", Az((AZURE_OK, None)))
    monkeypatch.setattr(v01.routing, "transcribe", lambda *a, **k: (PRIMARY_NG, None))
    monkeypatch.setattr(review_lock, "save_tts_attempt_audio", lambda *a, **k: "saved.wav")
    with mock.patch.object(v01.batch_wiring, "make_batch_tts_call_fn", return_value=lambda *a, **k: None), \
         mock.patch.object(v01.p4c, "build_tts_prompt", return_value="dummy prompt"), \
         mock.patch.object(v01.common, "_call_tts_with_retry", return_value=(b"pcm", 0, True, None)), \
         mock.patch.object(v01.common, "pcm_bytes_to_float_mono", return_value=np.zeros(100, dtype=np.float32)), \
         mock.patch.object(v01.p3u, "trim_english_keyword_silence",
                           return_value=(np.zeros(100, dtype=np.float32), {"raw_duration_seconds": 1.0, "trimmed_duration_seconds": 1.0})), \
         mock.patch.object(v01.safety, "detect_duration_anomaly", return_value={"is_anomaly": False}), \
         mock.patch.object(v01.common, "write_wav_float", return_value=None), \
         mock.patch.object(v01.common, "measure_metrics", return_value={"clipping_detected": False}):
        result = v01.generate_charon_japanese(CANON, "dummy_out.wav", "出演")
    assert result["status"] == "OK" and result["asr_verified"] is True
    assert result["asr_judgement"]["state"] == uj.PASS_WITH_WARNING
    assert result["attempts_log"][-1]["asr_judgement"]["state"] == uj.PASS_WITH_WARNING
    run_dir = tmp_path / "wiring_theme_auw4" / "a2"
    (run_dir / "audit").mkdir(parents=True)
    (run_dir / "audit" / "tts_generation_results.json").write_text(
        json.dumps({"segments": {"japanese_title": dict(result, sha256="abc", language="ja")}}, ensure_ascii=False, default=str),
        encoding="utf-8")
    rep = reg.write_listening_list_safe(str(run_dir), standalone_html=True)
    assert rep["error"] is None and rep["count"] == 1
    lst = json.load(open(rep["json"], encoding="utf-8"))["entries"][0]
    assert lst["segment_id"] == "japanese_title" and uj.W_SECONDARY_CONFIRMED in lst["warning_labels"]
    assert lst["primary_text"] == PRIMARY_NG and lst["secondary_text"] == AZURE_OK
    page = open(rep["html"], encoding="utf-8").read()
    assert "事後試聴リスト(PASS_WITH_WARNING)" in page and "japanese_title" in page and "SECONDARY_CONFIRMED" in page


def test_e2e_n3_fallback_ja_propagates_asr_judgement(tmp_path, monkeypatch):
    import er003_v1_n3_01_tts_generate as n3
    monkeypatch.setattr(ja, "_azure_stt_strict", Az((AZURE_OK, None)))
    monkeypatch.setattr(n3.routing, "transcribe", lambda *a, **k: (PRIMARY_NG, None))
    monkeypatch.setattr(review_lock, "save_tts_attempt_audio", lambda *a, **k: "saved.wav")
    with mock.patch.object(n3.c, "generate_narration_snippet_verified_strict",
                           return_value={"status": "STOPPED", "attempts_log": [], "reason": "x"}), \
         mock.patch.object(n3, "_generate_a2_japanese_minimal_instruction", return_value={"status": "OK", "path": "dummy.wav"}):
        r = n3.generate_a2_japanese_with_fallback(CANON, "dummy.wav", "出演")
    assert r["status"] == "OK" and r["fallback_used"] is True
    assert r["asr_judgement"]["state"] == uj.PASS_WITH_WARNING
    assert r["fallback_attempts_log"][-1]["asr_judgement"]["state"] == uj.PASS_WITH_WARNING


# ============================================================
# 9. J11: 引継ぎ・再利用の再判定(API 0、Secondary新規呼出なし)
# ============================================================
@pytest.fixture
def no_api(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("J11でASR/Secondaryの外部呼出は禁止")
    monkeypatch.setattr(ja, "_azure_stt_strict", boom)
    monkeypatch.setattr(routing, "transcribe", boom)
    monkeypatch.setattr(en_sec, "get_full_text_via_azure_stt_with_phrase_list", boom)
    return boom


def _ja_entry(text, asr, **kw):
    e = {"status": "OK", "asr_verified": True, "text": text, "canonical_text": text, "asr_text": asr, "sha256": "s" * 64,
         "audio_classification": "PHONETIC_MATCH"}
    e.update(kw)
    return e


def test_j11_ja_applicable_gate_passes_and_records_inherited(no_api):
    e = _ja_entry("三十人が来ました。", "30人が来ました。")
    rj = vi.rejudge_with_current_judge(e, "a2", "comment_1")
    assert rj["applicable"] is True and rj["ok"] is True and rj["secondary_new_calls"] == 0
    rec = rj["asr_judgement_inherited"]
    assert rec["inherited"]["via"] == "J11_rejudge_with_current_judge" and rec["inherited"]["api_calls"] == 0


def test_j11_ja_value_diff_or_negation_blocks_inheritance(no_api):
    assert vi.rejudge_with_current_judge(_ja_entry("三人が来ました。", "四人が来ました。"), "a2", "comment_1")["ok"] is False
    rj = vi.rejudge_with_current_judge(_ja_entry("解約を変えるために作った", "解約を変えないために作った"), "a2", "preview")
    assert rj["ok"] is False and rj["unified_state"] == uj.NG_PROTECTED


def test_j11_inherits_original_warning_and_uses_stored_secondary_only(no_api, monkeypatch):
    orig = run(CANON, PRIMARY_NG, Az((AZURE_OK, None)), monkeypatch)["asr_judgement"]
    assert orig["state"] == uj.PASS_WITH_WARNING
    e = _ja_entry(CANON, PRIMARY_NG, asr_judgement=copy.deepcopy(orig))
    rj = vi.rejudge_with_current_judge(e, "a2", "japanese_title")
    assert rj["ok"] is True and rj["secondary_new_calls"] == 0
    rec = rj["asr_judgement_inherited"]
    assert rec["state"] == uj.PASS_WITH_WARNING and uj.W_SECONDARY_CONFIRMED in rec["warnings"]
    # 継承entryでは asr_judgement -> asr_judgement_inherited に移り、試聴リストに「継承」として残る
    ev = {"current_sha256": "s" * 64, "evidence": "entry_sha256"}
    new = vi.build_inherited_entry(e, "x.wav", ev, {"kind": "t"}, f1_rejudge=rj, expected_text=CANON)
    assert "asr_judgement" not in new and new["asr_judgement_inherited"]["state"] == uj.PASS_WITH_WARNING
    assert "asr_judgement_inherited" not in new["validation_inheritance"]["f1_rejudge"]
    entries = reg.derive_listening_list({"segments": {"japanese_title": dict(new, path="x.wav")}})
    assert len(entries) == 1 and entries[0]["inherited"] is True


def test_j11_en_goes_through_unified_judge_and_keeps_fail_closed(no_api):
    e = {"status": "OK", "asr_verified": True, "text": "Beans cost less now.", "asr_text": "Beans cost less now.", "sha256": "e" * 64}
    ok = vi.rejudge_with_current_judge(e, "b1b", "full_story_part1")
    assert ok["applicable"] is True and ok["ok"] is True and ok["classification"] and ok["secondary_new_calls"] == 0
    bad = vi.rejudge_with_current_judge(dict(e, asr_text="Totally different words appear here."), "b1b", "in_one_line")
    assert bad["ok"] is False                       # Secondary保存なし -> 新規Secondary呼出もせずNG(fail-closed)
    val_diff = vi.rejudge_with_current_judge(dict(e, text="There were 25 people.", asr_text="There were 35 people."), "b1b", "full_story_part2")
    assert val_diff["ok"] is False


def test_j11_no_asr_text_is_fail_closed(no_api):
    assert vi.rejudge_with_current_judge({"status": "OK", "text": "x"}, "a2", "comment_1")["ok"] is False


def test_j11_real_stored_results_offline_rejudge_api0(no_api):
    # 実データ(既存run)の保存転写を再判定(読取のみ・API 0): JA 6件が最終ANDゲートを通り、結果recordを得る
    p = "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01/a2/audit/tts_generation_results.json"
    if not os.path.exists(p):
        pytest.skip("evidence file absent")
    segs = json.load(open(p, encoding="utf-8"))["segments"]
    n = 0
    for label, e in segs.items():
        if label in ("japanese_title", "preview") or label.startswith("comment_"):
            rj = vi.rejudge_with_current_judge(e, "a2", label)
            assert rj["applicable"] is True and rj["secondary_new_calls"] == 0
            assert rj["ok"] is True, (label, rj.get("reason"))
            n += 1
    assert n >= 5


# ============================================================
# 10. 新ラベル下流(OF-AUW-17、JA側): allowlist/件数集計/HR queue投入条件に未知ラベルで例外が出る箇所が無い
# ============================================================
def test_new_ja_labels_flow_through_hr_detail_and_timing_monitor_without_exception(monkeypatch):
    import er011_tts_retry_timing_monitor_01 as tm
    d = run("三十人が来ました。", "30人が来ました。", Az(), monkeypatch)
    assert d["final_status"] == ja.NUMERIC_VALUE_EQUIVALENT_MATCH
    result = {"attempts_log": [{"attempt": 1, "status": "OK", "asr_text": "30人が来ました。", "verified": True,
                                "audio_classification": d["classification"].classification, "asr_judgement": d["asr_judgement"]}],
              "fallback_attempts_log": [{"attempt": 1, "status": "OK", "verified": False,
                                         "audio_classification": "SECONDARY_CONFIRMED_PRIMARY_FALSE_NG",
                                         "asr_judgement": {"state": uj.NG_SECONDARY_UNAVAILABLE}}]}
    det = review_lock.build_attempts_detail(result)
    assert det[0]["audio_classification"] == ja.NUMERIC_VALUE_EQUIVALENT_MATCH and det[0]["asr_judgement"]["state"] == uj.PASS
    # NG側(timing monitor)はPASS(verified=True)を分類対象にせず、未知ラベルのNGでも例外にならない
    assert tm.classify_ng({"verified": True, "audio_classification": ja.NUMERIC_VALUE_EQUIVALENT_MATCH}) == (None, None)
    assert tm.classify_ng({"verified": False, "audio_classification": "NG_SOME_FUTURE_LABEL"})[0] == "B_quality_ng"


def test_new_ja_label_is_not_embedded_in_any_downstream_allowlist():
    import glob
    root = os.path.dirname(os.path.abspath(__file__))
    hits = []
    for f in glob.glob(os.path.join(root, "*.py")):
        name = os.path.basename(f)
        if name.endswith(("_test.py", "_test_01.py", "_test_02.py")) or name.startswith(("er058_", "er109_")):   # er109_*=ASR-HOMOPHONE調査の研究script(未配線)
            continue
        try:
            if "NUMERIC_VALUE_EQUIVALENT_MATCH" in open(f, encoding="utf-8").read():
                hits.append(name)
        except OSError:
            pass
    assert hits == ["er007_ja_secondary_asr_01.py"], hits      # 新ラベルの定義/使用はJA adapterのみ(下流に許可リストが無い)


# ============================================================
# 11. judge単体: adapterが渡す signals["protected_diff"](JA既存の保護差)は値DIFF/否定差と同じくSecondary不呼出でNG_PROTECTED
# ============================================================
def test_judge_protected_diff_signal_blocks_secondary_without_call():
    calls = {"n": 0}

    def sec_fn(_ctx):
        calls["n"] += 1
        return uj.SecondaryOutcome(CANON)

    ctx = uj.AttemptCtx(canonical_text=CANON, wav_sha256="x" * 64)
    pr = uj.PrimaryResult(passed=False, text=PRIMARY_NG, label="TRUE_CONTENT_MISMATCH",
                          signals={"protected_diff": "negation_marker_diff:'ず'->''"})
    jr = uj.unified_judge(ctx, pr, sec_fn, lang="ja", role=None)
    assert jr.state == uj.NG_PROTECTED and calls["n"] == 0 and jr.reason_code.startswith("p1_protected_diff:")
    jr2 = uj.unified_judge(ctx, uj.PrimaryResult(passed=False, text=PRIMARY_NG, label="TRUE_CONTENT_MISMATCH"), sec_fn, lang="ja", role=None)
    assert jr2.state != uj.NG_PROTECTED and calls["n"] == 1        # signalが無ければ従来どおりP3でSecondaryを呼ぶ
