# JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_12: OPEN-333 E3(Candidate E 数値entryの非数値差・全件再検査)のProduction適用test。
# mock/純関数のみ・API 0・費用0円。承認済み条件(er007:366-380『全文の読み一致/正規化後一致のときだけ通す』)の機能不全の是正であり、PASS集合は縮むのみ。
# 構成: (1)既定値・rollback定数・env非依存 (2)ON/OFFの両固定(OFF=HEAD完全一致) (3)正常は不変 (4)fail-closed (5)値ガード多層防御(R-6)
#       (6)M-6 audit field(判定不変) (7)非数値entry不変 (8)N3-07・月題#1・8,900↔89,000 (9)静的(env/flag非参照)
import inspect

import pytest

import er007_ja_asr_validator_01 as javal
import er007_ja_secondary_asr_01 as ja
import er011_ja_asr_variant_layer_01 as VL

javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = False

N307 = ("月のしわ、8,900本超", "月の巣は八千九百本長。")
MOON1 = ("月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密", "月の詩は八千九百本長。その奥に潜む岩の上着の秘密。")
NORMAL_NUM = ("売上は8,900本超えです", "売上は八千九百本長えです")
NORMAL_NONNUM = ("海からの封鎖", "海からの風さ")
VALUE_DIFF = ("売上は8,900円超です", "売上は八万九千円長です")
MELOS_DAYS = ("三日目", "3日間")


def classify(c, a):
    return javal.classify_ja_asr_match(c, a, allow_reading_resolver=False)


def is_e_pass(r):
    return r.should_pass and "Candidate E" in (r.reason or "")


@pytest.fixture
def off(monkeypatch):
    monkeypatch.setattr(VL, "CANDIDATE_E_FULL_DIFF_CHECK", False)
    monkeypatch.setattr(VL, "CANDIDATE_E_VALUE_GUARD_CHECK", False)


# ---- (1) 既定値 ----
def test_defaults_are_on():
    assert VL.CANDIDATE_E_FULL_DIFF_CHECK is True
    assert VL.CANDIDATE_E_VALUE_GUARD_CHECK is True


# ---- (2) ON/OFF 両方固定 ----
def test_on_blocks_n307():
    r = classify(*N307)
    assert r.classification == "TRUE_CONTENT_MISMATCH" and not r.should_pass
    rej = r.protected.candidate_e_rejections
    assert {"canonical": "しわ", "asr": "巣は", "kind": "unexplained_non_numeric_diff"} in rej


def test_off_is_identical_to_head(off):
    r = classify(*N307)
    assert is_e_pass(r) and r.classification == "PHONETIC_MATCH"
    assert not hasattr(r.protected, "candidate_e_rejections")


def test_on_blocks_moon1_per_approved_spec_and_off_keeps_head(monkeypatch):
    # 月題#1(転写『月の詩は…』)は承認済み仕様(非糊付けの『詩は』↔『しわ』と同じ)ではNG。救済はv2/βの担当(Fable判断、P-1は入れない)。
    assert classify(*MOON1).classification == "TRUE_CONTENT_MISMATCH"
    monkeypatch.setattr(VL, "CANDIDATE_E_FULL_DIFF_CHECK", False)
    monkeypatch.setattr(VL, "CANDIDATE_E_VALUE_GUARD_CHECK", False)
    assert is_e_pass(classify(*MOON1))


def test_each_constant_controls_only_its_layer(monkeypatch):
    monkeypatch.setattr(VL, "CANDIDATE_E_VALUE_GUARD_CHECK", False)
    assert classify(*N307).classification == "TRUE_CONTENT_MISMATCH"           # 非数値差の再検査は有効
    assert is_e_pass(classify(*VALUE_DIFF))                                      # 値ガード層だけOFF=HEADと同じ(値の最終確認はF1に残る)
    monkeypatch.setattr(VL, "CANDIDATE_E_VALUE_GUARD_CHECK", True)
    monkeypatch.setattr(VL, "CANDIDATE_E_FULL_DIFF_CHECK", False)
    assert is_e_pass(classify(*N307))                                            # 再検査だけOFF
    assert classify(*VALUE_DIFF).classification == "TRUE_CONTENT_MISMATCH"       # 値ガード層は有効


# ---- (3) 正常は不変 ----
@pytest.mark.parametrize("pair", [NORMAL_NUM,
                                  ("一緒に8,900本超", "一緒に八千九百本長"), ("千葉で8,900本超", "千葉で八千九百本長"), ("九州で8,900本超", "九州で八千九百本長"),
                                  ("支払いは1万2,000円超です", "支払いは一万二千円長です"), ("ひとつで8,900本超", "一つで八千九百本長"),
                                  ("売上は8,900円で利益は1,200円超です", "売上は八千九百円で利益は千二百円長です"), ("８，９００本超", "八千九百本長")])
def test_normal_number_entry_still_passes(pair):
    r = classify(*pair)
    assert r.should_pass, (pair, r.classification, r.reason)


# ---- (4) fail-closed ----
def test_helper_exception_rejects(monkeypatch):
    def boom(_t):
        raise RuntimeError("x")
    monkeypatch.setattr(VL, "_mask_value_spans", boom)
    r = classify(*NORMAL_NUM)
    assert r.classification == "TRUE_CONTENT_MISMATCH"
    assert r.protected.candidate_e_rejections[0]["kind"] == "helper_error:RuntimeError"


def test_value_guard_exception_rejects(monkeypatch):
    import er078_asr_value_guard_01 as vg

    def boom(*_a, **_k):
        raise RuntimeError("x")
    monkeypatch.setattr(vg, "value_guard_kana_unified", boom)
    r = classify(*NORMAL_NUM)
    assert r.classification == "TRUE_CONTENT_MISMATCH"
    assert r.protected.candidate_e_rejections[0]["kind"] == "value_guard_error:RuntimeError"


# ---- (5) 値ガード多層防御(R-6) ----
def test_value_guard_veto_blocks_8900_vs_89000_at_candidate_e():
    r = classify(*VALUE_DIFF)
    assert r.classification == "TRUE_CONTENT_MISMATCH"
    assert any(x["kind"] == "value_guard:DIFF" for x in r.protected.candidate_e_rejections)


def test_melos_days_known_false_pass_blocked():
    r = classify(*MELOS_DAYS)                              # 三日間→三日目(OPEN-333 N1の既知誤PASS型)
    assert r.classification == "TRUE_CONTENT_MISMATCH"


# ---- (6) M-6: audit field(判定不変) ----
class _NoNet:
    pass


def _adapter(canon, asr):
    orig = ja._azure_stt_strict
    ja._azure_stt_strict = lambda p, language="ja-JP", timeout_seconds=90: (None, "api0_stub_no_call")
    try:
        import tempfile, wave, os
        w = os.path.join(tempfile.gettempdir(), "e3_test_dummy.wav")
        f = wave.open(w, "wb"); f.setnchannels(1); f.setsampwidth(2); f.setframerate(16000); f.writeframes(b"\x00\x00" * 16000); f.close()
        return ja.evaluate_attempt_ja_with_cascade_detail(canon, asr, w, cascade_enabled=True, attempt_ctx={"max_len": 400})
    finally:
        ja._azure_stt_strict = orig


def test_audit_field_recorded_and_judgement_unchanged_by_recording():
    res = _adapter(*N307)
    aud = res["asr_judgement"]["candidate_e_full_diff"]
    assert aud["rejected"] >= 1 and aud["pairs"][0]["canonical"] == "しわ"
    assert res["asr_judgement"]["state"] not in ("PASS", "PASS_WITH_WARNING")
    # 正常側にはfieldが付かない(出力不変)
    assert "candidate_e_full_diff" not in _adapter(*NORMAL_NUM)["asr_judgement"]


def test_audit_field_absent_when_off(off):
    res = _adapter(*N307)
    assert "candidate_e_full_diff" not in res["asr_judgement"]


# ---- (7) 非数値entryは不変 ----
def test_non_number_entry_unchanged():
    r = classify(*NORMAL_NONNUM)
    assert is_e_pass(r)
    assert not hasattr(r.protected, "candidate_e_rejections")


# ---- (8) 他の拒否例(M-3 block型) ----
@pytest.mark.parametrize("pair", [("月のしわ、8,900本超", "月の八千九百本長"), ("月の8,900本超", "月のしわ八千九百本長"), ("しわ8,900本超", "巣は八千九百本長"),
                                  ("はし、8,900本超", "わし八千九百本長"), ("へや、8,900本超", "えや八千九百本長"), ("千葉で8,900本超", "千駄で八千九百本長")])
def test_glued_or_mismatched_non_numeric_residue_never_passes(pair):
    assert not classify(*pair).should_pass


# ---- (9) 静的: env/flag/引数で迂回できない ----
def test_constants_not_read_from_env_or_args():
    src = inspect.getsource(VL._candidate_e_number_entry_rejections) + inspect.getsource(VL._mask_value_spans)
    assert "environ" not in src and "getenv" not in src
    sig = inspect.signature(VL._candidate_e_number_entry_rejections)
    assert not any("flag" in p or "enable" in p for p in sig.parameters)
    full = inspect.getsource(VL.try_rescue_before_resolver)
    assert "_candidate_e_number_entry_rejections(" in full
