# OPEN-517 R-5 計測(JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_09)のtest。仕様=docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/R5_MEASUREMENT_SPEC_01.md §3/§5。
# 全てmock(Secondary=er007_ja_secondary_asr_01._azure_stt_strict)。API呼出0・費用0円。
import copy
import json
import wave

import pytest

import er007_ja_asr_validator_01 as javal
import er007_ja_secondary_asr_01 as ja
import er006_secondary_asr_01 as en_sec
import er078_asr_unified_judge_01 as uj


class Az:
    def __init__(self, result=(None, "no result")):
        self.result, self.calls = result, 0

    def __call__(self, wav_path, language="ja-JP", timeout_seconds=90.0):
        self.calls += 1
        return self.result


@pytest.fixture(autouse=True)
def _iso(monkeypatch):
    en_sec.reset_secondary_cache()
    monkeypatch.setattr(en_sec, "_RUN_STATE", None)
    monkeypatch.setattr(en_sec, "_RUN_CACHE", None)
    monkeypatch.setattr(javal, "FEATURE_FLAG_A2_READING_RESOLVER_ENABLED", False)
    yield
    en_sec.reset_secondary_cache()


def _wav(tmp_path, name="a.wav"):
    p = tmp_path / name
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(8000)
        w.writeframes(b"\x01\x00" * 8000)
    return str(p)


def run(tmp_path, monkeypatch, canon, primary, az):
    monkeypatch.setattr(ja, "_azure_stt_strict", az)
    return ja.evaluate_attempt_ja_with_cascade_detail(canon, primary, _wav(tmp_path), cascade_enabled=True)


def _judgement_view(a):
    """判定に関わる全フィールド(R-5が足す r5 / canonical_text / secondary.model_id / secondary.provenance_complete と時間計測を除く)。"""
    b = copy.deepcopy(a)
    for k in ("r5", "canonical_text"):
        b.pop(k, None)
    for k in ("model_id", "provenance_complete"):
        b.get("secondary", {}).pop(k, None)
    for k in ("total_ms", "secondary_ms"):
        b.get("timing", {}).pop(k, None)
    return b


CAST = "AIの電話に人間が出演。問題は「キャスト変更」のお知らせでした"
CAST_NG = "AIの電話に人間が出現。問題は、キャスト変更のお知らせでした。"
CAST_OK = "AIの電話に人間が出演。問題はキャスト変更のお知らせでした。"
SCENARIOS = [
    ("pass_exact", "解約できない仕組み", "解約できない仕組み", (None, "no result")),
    ("reading_match_pass", "解約できない仕組み", "かいやくできないしくみ", (None, "no result")),
    ("f1_reject_value", "月のしわ、8,900本超", "月野氏は八万九千本町。", (None, "no result")),
    ("f1_reject_reading", "三日待ちます", "さんにち待ちます", (None, "no result")),
    ("f2_fired_pass", "月のしわ、8,900本超", "つきのしわはっせんきゅうひゃっぽんちょう", (None, "no result")),
    ("f2_fired_warning", "それは三日間です", "それはみっかかんです", (None, "no result")),
    ("primary_ng_secondary_ok", CAST, CAST_NG, (CAST_OK, None)),
    ("secondary_unavailable", CAST, CAST_NG, (None, "boom")),
    ("p1_value_diff", "10人で行く", "とおで行く", (None, "no result")),
    ("secondary_value_diff", "それは5日です", "それはいつかです", ("それは5日です", None)),
]


@pytest.mark.parametrize("name,canon,primary,azres", SCENARIOS, ids=[s[0] for s in SCENARIOS])
def test_measurement_does_not_change_judgement(name, canon, primary, azres, tmp_path, monkeypatch):
    # 計測あり(現行)と、計測を無効化(_r5_record を no-op)した場合で、判定に関わる全フィールドが完全一致する(§5 前後比較)
    d1 = run(tmp_path, monkeypatch, canon, primary, Az(azres))
    en_sec.reset_secondary_cache()
    with monkeypatch.context() as m:
        m.setattr(uj, "_r5_record", lambda *a, **k: None)
        d0 = run(tmp_path, monkeypatch, canon, primary, Az(azres))
    a1, a0 = d1["asr_judgement"], d0["asr_judgement"]
    assert "r5" in a1 and "r5" not in a0
    assert _judgement_view(a1) == _judgement_view(a0)
    for k in ("verified", "final_status", "cascade_invoked", "human_review_required", "technical_stop"):
        assert d1.get(k) == d0.get(k)
    json.dumps(a1, ensure_ascii=False)   # JSON直列化可能


def test_f1_rejection_and_f2_fired_are_recorded(tmp_path, monkeypatch):
    a = run(tmp_path, monkeypatch, "月のしわ、8,900本超", "月野氏は八万九千本町。", Az())["asr_judgement"]
    r = a["r5"]
    assert a["reason_code"] == "final_gate_value_diff" and r["measurement_error"] is None
    assert r["f1"]["final_gate_rejected"] is True and r["f1"]["would_have_passed_before_f1"] is True and r["f1"]["reason_code"] == "final_gate_value_diff"
    assert r["f1"]["rollback_const_READING_MATCH_FINAL_GATE"] is True
    assert a["canonical_text"] == "月のしわ、8,900本超"
    a = run(tmp_path, monkeypatch, "それは三日間です", "それはみっかかんです", Az())["asr_judgement"]
    f2 = a["r5"]["f2"]
    assert f2["enabled"] and f2["fired"] and f2["text_before"] == "それはみっかかんです" and f2["text_after"] == "それは三日間です"
    assert a["r5"]["f1"]["final_gate_rejected"] is False and a["r5"]["models"]["primary"]["model"] == "gpt-4o-mini-transcribe"


def test_f1_off_when_primary_is_not_reading_match(tmp_path, monkeypatch):
    a = run(tmp_path, monkeypatch, "解約できない仕組み", "解約できない仕組み", Az())["asr_judgement"]
    assert a["r5"]["f1"]["reading_match_primary_pass"] is False and a["r5"]["f2"]["enabled"] is False and a["r5"]["f2"]["fired"] is False


def test_secondary_provenance_recorded_only_when_called(tmp_path, monkeypatch):
    # Azure不呼出(Primary PASS / P1打ち切り)ではS転写・provenanceを捏造しない
    for canon, primary in (("解約できない仕組み", "解約できない仕組み"), ("10人で行く", "とおで行く")):
        a = run(tmp_path, monkeypatch, canon, primary, Az())["asr_judgement"]
        assert a["secondary"]["called"] is False and a["secondary"]["text"] is None
        assert "provenance_complete" not in a["secondary"] and "model_id" not in a["secondary"]
    a = run(tmp_path, monkeypatch, CAST, CAST_NG, Az((CAST_OK, None)))["asr_judgement"]
    s = a["secondary"]
    assert s["called"] and s["text"] and s["engine"] == "azure" and s["model_id"] == "azure-speech-stt" and s["provenance_complete"] is True
    assert a["audio_sha256"] and not a["audio_sha256"].startswith("nosha:")


def test_provenance_incomplete_when_sha_is_placeholder_or_transcript_missing():
    pr = uj.PrimaryResult(False, "x", "L", None)
    audit = {"lang": "ja", "state": "NG_SECONDARY_UNAVAILABLE", "reason_code": "secondary_unavailable", "secondary": {"called": True, "engine": "azure", "text": None, "error": "boom"},
             "audio_sha256": "nosha:x", "value_guard": {}}
    uj._r5_record(audit, None, pr, "canon", {})
    assert audit["secondary"]["provenance_complete"] is False
    audit = {"lang": "ja", "state": "PASS_WITH_WARNING", "reason_code": "secondary_confirmed", "secondary": {"called": True, "engine": "azure", "text": "t", "error": None},
             "audio_sha256": "a" * 64, "value_guard": {}}
    uj._r5_record(audit, None, pr, "canon", {})
    assert audit["secondary"]["provenance_complete"] is True
    audit["secondary"]["text"] = ""
    uj._r5_record(audit, None, pr, "canon", {})
    assert audit["secondary"]["provenance_complete"] is False


def test_measurement_exception_is_recorded_and_does_not_affect_judgement(tmp_path, monkeypatch):
    d0 = run(tmp_path, monkeypatch, "月のしわ、8,900本超", "月野氏は八万九千本町。", Az())["asr_judgement"]
    en_sec.reset_secondary_cache()
    monkeypatch.setattr(uj, "_R5_WEAK_KANA_MARKS", 5)   # 計測内で TypeError を起こす
    d1 = run(tmp_path, monkeypatch, "月のしわ、8,900本超", "月野氏は八万九千本町。", Az())["asr_judgement"]
    assert d1["r5"]["measurement_error"].startswith("TypeError")
    assert (d1["state"], d1["reason_code"], d1["warnings"]) == (d0["state"], d0["reason_code"], d0["warnings"]) == ("NG_PROTECTED", "final_gate_value_diff", [])


def test_demote_p3_is_recorded_for_reading_match_when_demoted():
    # READING_MATCH Primary PASS + 曖昧表層(AMBIGUOUS) -> P3降格。judge直呼びで降格が起きた場合に記録されることを確認する(起きない入力なら記録欠落のみ検証)。
    ctx = uj.AttemptCtx(canonical_text="10分待つ", wav_sha256="b" * 64, engine="azure")
    pr = uj.PrimaryResult(True, "10分待つ", "PHONETIC_MATCH", "READING_MATCH")
    jr = uj.unified_judge(ctx, pr, lambda c: uj.SecondaryOutcome(None, error="x"), lang="ja", role=None)
    a = jr.audit_record
    assert a["r5"]["measurement_error"] is None
    if a.get("p3_entry") == "primary_pass_demoted_ambiguous_value":
        assert a["r5"]["f1"]["demoted_p3"] is True and a["r5"]["f1"]["would_have_passed_before_f1"] is True
    else:
        assert a["r5"]["f1"]["demoted_p3"] is False


def test_english_judgement_is_unchanged_no_r5_keys():
    # R-5はJAのみ。ENのasr_judgementには r5 / canonical_text を足さない(A/B/C・EN KPの保存形式不変)
    ctx = uj.AttemptCtx(canonical_text="Hello world.", wav_sha256="c" * 64, engine="azure")
    pr = uj.PrimaryResult(True, "Hello world.", "EXACT_MATCH", None)
    a = uj.unified_judge(ctx, pr, lambda c: uj.SecondaryOutcome(None, error="x"), lang="en", role=None).audit_record
    assert "r5" not in a and "canonical_text" not in a and a["state"] == uj.PASS


def test_unknown_keys_are_not_read_by_registry():
    # §3-3: 追加キー(r5 / canonical_text / secondary.model_id / provenance_complete)は台帳(registry)が参照しない=未知キーは無視される。
    import er078_pass_with_warning_registry_01 as reg
    src = open(reg.__file__, encoding="utf8").read()
    assert '"r5"' not in src and "provenance_complete" not in src
