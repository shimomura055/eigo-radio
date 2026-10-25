# JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_14: OPEN-333 E4(Candidate Eの便乗PASS是正)のProduction適用test。mock/純関数のみ・API 0・費用0円。
# 承認済み安全条件『entity_like/濁点差はCascade(Azure再確認)へ』の不具合是正。PASS集合は縮むのみ・新しい受理クラスなし。
# 構成: (1)既定値・env非依存 (2)ON/OFF (3)正常は不変 (4)fail-closed (5)M-1(E3例外はNone) (6)M-3 構造遮断 (7)M-4 E2E(数値entry・Azure stub)
#       (8)監視field(判定不変)
import inspect

import pytest

import er007_ja_asr_validator_01 as javal
import er007_ja_secondary_asr_01 as ja
import er011_ja_asr_variant_layer_01 as VL

javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = False

TXT = ("メロスの封鎖について話します", "メラスの風さについて話します")      # E4発火型(非数値entry)
CTRL = ("メロスの封鎖について話します", "メロスの風さについて話します")     # 便乗差分なし
NUM = ("NASAは8,900本で、超です", "ナサは八千九百本で、長です")             # 合成cost num 1件の型(数値entryでE4発火)
NUM_WRONG_SEC = "ナサは八千九百本で、長です"
NUM_OK_SEC = "NASAは8,900本で、超です"


def classify(c, a):
    return javal.classify_ja_asr_match(c, a, allow_reading_resolver=False)


@pytest.fixture
def off(monkeypatch):
    monkeypatch.setattr(VL, "CANDIDATE_E_CASCADE_DIFF_RETURN", False)


def test_default_on():
    assert VL.CANDIDATE_E_CASCADE_DIFF_RETURN is True


def test_on_returns_cascade_for_txt_and_num():
    for c, a in (TXT, NUM):
        r = classify(c, a)
        assert r.classification == "ASR_VALIDATION_UNCERTAIN" and not r.should_pass and not r.should_retry
        assert r.protected.candidate_e_cascade_diffs


def test_off_is_head(off):
    for c, a in (TXT, NUM):
        r = classify(c, a)
        assert r.should_pass and r.classification == "PHONETIC_MATCH"
        assert not hasattr(r.protected, "candidate_e_cascade_diffs")


def test_ctrl_unchanged():
    r = classify(*CTRL)
    assert r.should_pass and r.classification == "PHONETIC_MATCH"
    assert not hasattr(r.protected, "candidate_e_cascade_diffs")


def test_constant_not_read_from_env_or_args():
    src = inspect.getsource(VL.try_rescue_before_resolver)
    assert "environ" not in src and "getenv" not in src
    assert "CANDIDATE_E_CASCADE_DIFF_RETURN" in src
    assert "CANDIDATE_E_CASCADE_DIFF_RETURN" not in inspect.signature(VL.try_rescue_before_resolver).parameters


def test_exception_in_cascade_diff_computation_is_cascade_not_pass(monkeypatch):
    orig = javal.protected_check_ja

    class Boom(list):
        def __iter__(self):
            if getattr(self, "armed", False):
                raise RuntimeError("boom")
            return super().__iter__()

    state = {}

    def patched(*a, **k):
        p = orig(*a, **k)
        b = Boom(p.content_diffs)
        p.content_diffs = b
        state["b"] = b
        return p
    monkeypatch.setattr(javal, "protected_check_ja", patched)
    # remaining_diffs 計算後(armed)に cascade_diffs 計算で例外 -> Cascade(UNCERTAIN)であってPASSではない
    orig_span = VL._span_pair_reading_variant_match

    def arm(*a, **k):
        state["b"].armed = True
        return orig_span(*a, **k)
    monkeypatch.setattr(VL, "_span_pair_reading_variant_match", arm)
    r = classify(*TXT)
    assert r.classification == "ASR_VALIDATION_UNCERTAIN" and not r.should_pass


def test_m1_e3_helper_exception_is_none_tcm_not_cascade(monkeypatch):
    # Opus M-1: E3の拒否判定(_rej)は try/except で囲まない。E3 helper例外は従来どおり TRUE_CONTENT_MISMATCH(None)、_cascadeにしない。
    def boom(*a, **k):
        raise RuntimeError("e3 helper")
    monkeypatch.setattr(VL, "_mask_value_spans", boom)
    r = classify(*NUM)
    assert r.classification == "TRUE_CONTENT_MISMATCH" and not r.should_pass
    assert any(x["kind"].startswith("helper_error") for x in r.protected.candidate_e_rejections)
    assert not hasattr(r.protected, "candidate_e_cascade_diffs")
    # さらに _candidate_e_number_entry_rejections 自体が例外を出しても _cascade ではなく例外が伝播(囲まれていない)
    monkeypatch.setattr(VL, "_candidate_e_number_entry_rejections", boom)
    with pytest.raises(RuntimeError):
        classify(*NUM)


def test_m1_try_scope_static():
    src = inspect.getsource(VL.try_rescue_before_resolver)
    i_rej = src.index("_rej = _candidate_e_number_entry_rejections")
    i_try = src.index("try:", i_rej)
    i_rej_use = src.index("if _rej:", i_rej)
    assert i_rej_use < i_try      # E3判定は try より前


# ---- M-3: 構造的な遮断 ----
def test_m3_structural_blocks():
    for c, a in (TXT, NUM):
        r = classify(c, a)
        assert r.classification == "ASR_VALIDATION_UNCERTAIN"
        assert ja._orthographic_reading_confirmed(r) is False            # ORTHOGRAPHIC_VARIANT_CONFIRMED は開かない
        assert VL.try_upgrade_voicing_cascade(c, a, r) is None           # D-2引き上げは開かない
        assert VL._is_pure_phonetic_uncertain_cascade(r) is False
        assert ja._numeric_value_equivalence(c, a, r) is None            # TRUE_CONTENT_MISMATCH専用


# ---- M-4: E2E (統一judge + Azure stub) ----
class Az:
    def __init__(self, text):
        self.text = text
        self.calls = 0

    def __call__(self, wav, language="ja-JP", timeout_seconds=90.0):
        self.calls += 1
        return self.text, None


def run(monkeypatch, canon, primary, az_text, wav="dummy.wav"):
    az = Az(az_text)
    monkeypatch.setattr(ja, "_azure_stt_strict", az)
    r = ja.evaluate_attempt_ja_with_cascade_detail(canon, primary, wav, cascade_enabled=True, attempt_ctx={"max_len": 400})
    return r, az


def test_m4_num_azure_exact_is_pass_with_warning(monkeypatch):
    r, az = run(monkeypatch, NUM[0], NUM[1], NUM_OK_SEC)
    j = r["asr_judgement"]
    assert az.calls >= 1
    assert j["state"] == "PASS_WITH_WARNING"
    assert j["candidate_e_cascade_return"]["diffs"]


def test_m4_num_wrong_secondary_not_pass(monkeypatch):
    # 値を誤ったSecondary転写(8,900->9,900)は PASS にならない(値ガードsvg)
    r, _ = run(monkeypatch, NUM[0], NUM[1], "NASAは9,900本で、超です")
    assert r["asr_judgement"]["state"] not in ("PASS", "PASS_WITH_WARNING")
    r, _ = run(monkeypatch, NUM[0], NUM[1], "ナサは九千九百本で、長です")
    assert r["asr_judgement"]["state"] not in ("PASS", "PASS_WITH_WARNING")


def test_m4_txt_azure_wrong_not_pass_and_exact_pass_with_warning(monkeypatch):
    r, _ = run(monkeypatch, TXT[0], TXT[1], TXT[0])
    assert r["asr_judgement"]["state"] == "PASS_WITH_WARNING"
    r, _ = run(monkeypatch, TXT[0], TXT[1], TXT[1])      # Azureも同じ読み違い転写 -> PASSにならない
    assert r["asr_judgement"]["state"] not in ("PASS", "PASS_WITH_WARNING")


# ---- 監視field ----
def test_monitor_field_absent_when_not_fired_and_judgement_unchanged(monkeypatch):
    r, az = run(monkeypatch, CTRL[0], CTRL[1], CTRL[0])
    j = r["asr_judgement"]
    assert "candidate_e_cascade_return" not in j and j["state"] == "PASS" and az.calls == 0


def test_monitor_field_does_not_change_state(monkeypatch):
    r_on, _ = run(monkeypatch, TXT[0], TXT[1], TXT[0])
    monkeypatch.setattr(VL, "CANDIDATE_E_CASCADE_DIFF_RETURN", False)
    r_off, az = run(monkeypatch, TXT[0], TXT[1], TXT[0])
    assert "candidate_e_cascade_return" not in r_off["asr_judgement"] and r_off["asr_judgement"]["state"] == "PASS" and az.calls == 0
    assert r_on["asr_judgement"]["state"] == "PASS_WITH_WARNING"
