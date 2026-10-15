# AUW 委任_10: U1是正(JA C1固有名詞差・類似度<0.4の事前除外撤廃)のunit負例・ロールバック・U2静的・EN不変test。
# 全てmock(API呼出0・費用JPY0)。helperは委任_04のJA wiring testを再利用。
import ast
import os

import pytest

import er006_secondary_asr_01 as en_sec
import er007_ja_secondary_asr_01 as ja
import er078_asr_unified_judge_01 as uj
from er078_asr_unified_ja_wiring_test_01 import Az, CANON, PRIMARY_NG, AZURE_OK, run, _iso  # noqa: F401

META_CANON = "Metaが新しい発表をしました"
ER_META = {"meta": "メタ"}


# ---- (a) unit負例: 登録読み保護(A7)。U1解放後もSecondaryの表層一致で素通りさせない(U1R-01) ----
@pytest.mark.parametrize("primary", ["エムイーティーエーが新しい発表をしました", "メタンが新しい発表をしました"])
def test_registered_latin_word_reading_mismatch_stays_excluded(primary, monkeypatch):
    monkeypatch.setattr(uj, "U1_KEEP_C1_SIMILARITY_EXCLUSIONS", False)   # 解放後の挙動(既定は暫定True: s1)
    az = Az((META_CANON, None))      # Azureは原稿表記を返す(表層EXACT)
    d = run(META_CANON, primary, az, monkeypatch, expected_readings=ER_META)
    assert d["verified"] is False and az.calls == 0
    assert d["asr_judgement"]["state"] == uj.NG_EXCLUDED
    assert d["asr_judgement"]["exclusion_rule"] == "A7_READING_DICT_MISMATCH"


def test_registered_kanji_word_reading_mismatch_stays_excluded(monkeypatch):
    monkeypatch.setattr(uj, "U1_KEEP_C1_SIMILARITY_EXCLUSIONS", False)
    canon, primary = "昨日は雨でした", "アクジツは雨でした"
    az = Az((canon, None))
    d = run(canon, primary, az, monkeypatch, expected_readings={"昨日": "きのう"})
    assert d["verified"] is False and az.calls == 0
    assert d["asr_judgement"]["exclusion_rule"] == "A7_READING_DICT_MISMATCH"


def test_unregistered_entity_like_is_released_to_secondary(monkeypatch):
    monkeypatch.setattr(uj, "U1_KEEP_C1_SIMILARITY_EXCLUSIONS", False)   # 解放後の挙動(既定は暫定True: s1)
    # 辞書未登録のカタカナ同士(entity_like)は解放: Primary NGでもSecondaryへ回り、正当に支持されればWARNING付き採用
    canon, primary = "熟すと出るガス", "じくすと出るカス。"
    az = Az((canon, None))
    d = run(canon, primary, az, monkeypatch)
    assert az.calls == 1 and d["verified"] is True
    assert d["asr_judgement"]["state"] == uj.PASS_WITH_WARNING
    # Secondaryも誤り(Primaryと同じ誤読)ならNG_BOTH(過剰救済なし)
    az2 = Az((primary, None))
    d2 = run(canon, primary, az2, monkeypatch)
    assert az2.calls == 1 and d2["verified"] is False and d2["asr_judgement"]["state"] == uj.NG_BOTH


def test_protected_diffs_and_length_still_excluded(monkeypatch):
    # P1(数値DIFF・否定差)は解放後もSecondary不呼出
    az = Az(("会議は3時に始まります。", None))
    d = run("会議は3時に始まります。", "会議は5時に始まります。", az, monkeypatch)
    assert d["verified"] is False and az.calls == 0 and d["asr_judgement"]["state"] == uj.NG_PROTECTED
    az = Az(("これは問題ではありません。", None))
    d = run("これは問題ではありません。", "これは問題です。", az, monkeypatch)
    assert d["verified"] is False and az.calls == 0 and d["asr_judgement"]["state"] == uj.NG_PROTECTED
    # A3 length NGは維持(本委任ではA3を変えない。是正はOPEN起票)
    az = Az((AZURE_OK, None))
    d = run(CANON, PRIMARY_NG, az, monkeypatch, length_ok=False)
    assert d["verified"] is False and az.calls == 0 and d["asr_judgement"]["exclusion_rule"] == "A3_LENGTH_NG"


# ---- 空転写(R2/U1R-02): 障害ではなくNG_BOTH ----
@pytest.mark.parametrize("empty", ["", "   ", "\n"])
def test_empty_secondary_transcript_is_ng_both_not_technical_stop(empty, monkeypatch):
    az = Az((empty, None))
    d = run(CANON, PRIMARY_NG, az, monkeypatch, attempt_ctx={"is_last_slot": True})
    j = d["asr_judgement"]
    assert d["verified"] is False and az.calls == 1
    assert j["state"] == uj.NG_BOTH and j["secondary"]["unavailable"] is False
    assert j["secondary"]["label"] == "NO_SPEECH" and j["secondary"]["text"] == ja.NO_SPEECH_SENTINEL
    assert j["technical_stop"] is None and "technical_stop_status" not in d
    assert d["human_review_required"] is True       # 最終slotのNG_BOTHは従来どおりHR(技術STOPではない)


def test_empty_transcripts_do_not_open_circuit_breaker(monkeypatch):
    rs = uj.RunState() if hasattr(uj, "RunState") else None
    for i in range(5):
        az = Az(("", None))
        run(CANON, PRIMARY_NG, az, monkeypatch, attempt_ctx={"segment_key": f"s{i}", "slot": 1, "run_state": rs, "cache": uj.SecondaryCache()})
    if rs is not None:
        assert rs.secondary_consecutive_failures == 0 and rs.circuit_open is False


def test_genuine_secondary_error_still_unavailable(monkeypatch):
    az = Az((None, "boom"))
    d = run(CANON, PRIMARY_NG, az, monkeypatch)
    assert d["asr_judgement"]["state"] == uj.NG_SECONDARY_UNAVAILABLE


# ---- EN不変: A4〜A7はJAのみ ----
def test_en_not_affected_by_a5_a6_a7():
    en_rules = [r.rule_id for r in uj.SCG_EXCLUSIONS if "en" in r.langs]
    assert en_rules == ["A1_NUMBER_DIFF", "A2_NEGATION_DIFF", "A3_LENGTH_NG"]
    assert all(r.langs == ("ja",) for r in uj.SCG_EXCLUSIONS if r.rule_id.startswith(("A4", "A5", "A6", "A7")))
    from er078_asr_unified_judge_01_test_01 import ctx_, MockSecondary
    for sig in ({"similarity": 0.1}, {"c1_proper_noun_diff": True}, {"reading_dictionary_mismatch": "x"}):
        sec = MockSecondary("Hello there friend.")
        r = uj.unified_judge(ctx_("Hello there friend."), uj.PrimaryResult(False, "Hallo thair frend.", signals=sig), sec, lang="en", role="x")
        assert sec.calls == 1 and r.state != uj.NG_EXCLUDED


# ---- (d) ロールバックtest: U1=Trueで旧挙動(A5/A6再有効)。A7はU1と無関係 ----
def test_u1_true_rolls_back_to_previous_exclusions(monkeypatch):
    monkeypatch.setattr(uj, "U1_KEEP_C1_SIMILARITY_EXCLUSIONS", True)
    az = Az(("あ" * 30, None))
    d = run("あ" * 30, "ん" * 30, az, monkeypatch)
    assert az.calls == 0 and d["asr_judgement"]["exclusion_rule"] == "A5_SIMILARITY_LT_0_4"
    az = Az(("熟すと出るガス", None))
    d = run("熟すと出るガス", "じくすと出るカス。", az, monkeypatch)
    assert az.calls == 0 and d["asr_judgement"]["exclusion_rule"] == "A6_C1_PROPER_NOUN_DIFF"
    az = Az((META_CANON, None))
    d = run(META_CANON, "メタンが新しい発表をしました", az, monkeypatch, expected_readings=ER_META)
    assert az.calls == 0 and d["asr_judgement"]["state"] == uj.NG_EXCLUDED


def test_u1_default_state_documented():
    # 委任_10 s1条件付きSTOP(live負例対照でPrimary PASSが3件)により暫定True。Fable判断で解放する際はjudge定数とこのassertを更新する。
    assert uj.U1_KEEP_C1_SIMILARITY_EXCLUSIONS is False  # 委任_11: U1発効(Fable判断でs1非該当)


def test_a7_independent_of_u1():
    assert not any(r.u1_gated for r in uj.SCG_EXCLUSIONS if r.rule_id == "A7_READING_DICT_MISMATCH")


# ---- U2静的test(A-4): force_secondary=Trueの呼出点が1箇所のみ・死定数撤去・拡大なし ----
def _repo_py_files():
    root = os.path.dirname(os.path.abspath(__file__))
    return [os.path.join(root, f) for f in os.listdir(root) if f.endswith(".py")]


def test_force_secondary_true_call_sites_are_exactly_one_production_site():
    sites = []
    for p in _repo_py_files():
        name = os.path.basename(p)
        if "_test" in name or name.startswith("test_") or "audit" in name:
            continue
        try:
            tree = ast.parse(open(p, encoding="utf-8").read())
        except (SyntaxError, UnicodeDecodeError):
            continue
        for n in ast.walk(tree):
            if isinstance(n, ast.keyword) and n.arg == "force_secondary" and isinstance(n.value, ast.Constant) and n.value.value is True:
                sites.append((name, n.value.lineno))
    assert [s[0] for s in sites] == ["er003_v1_crosslevel_audio_02_common.py"], sites
    root = os.path.dirname(os.path.abspath(__file__))
    src = open(os.path.join(root, "er003_v1_crosslevel_audio_02_common.py"), encoding="utf-8").read()
    fn = [n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef) and n.name == "_run_a2_minimal_fallback_attempt"]
    assert fn and any(isinstance(k, ast.keyword) and k.arg == "force_secondary" for k in ast.walk(fn[0]))


def test_u2_dead_constant_removed_everywhere():
    for p in _repo_py_files():
        name = os.path.basename(p)
        if name == os.path.basename(__file__):
            continue
        txt = open(p, encoding="utf-8", errors="ignore").read()
        for ln in txt.splitlines():
            if "U2_FORCE_SECONDARY_SCOPE" in ln:
                assert ln.lstrip().startswith("#") or "not hasattr" in ln, (name, ln)   # 撤去記録のコメント行/不在assert以外には存在しない


# ---- 解放後(U1=False)のfrozen 25行Regression: 旧Phase0 fixtureに対し、解放はg7/g8のみ変える・C群は不変NG ----
def test_released_frozen_25_rows_only_g7_g8_change_and_c_group_stays_ng(monkeypatch):
    import er007_ja_scg_phase0_regression_test_01 as P
    monkeypatch.setattr(uj, "U1_KEEP_C1_SIMILARITY_EXCLUSIONS", True)
    kept = {k: P._run_prod(k)[0]["verified"] for k in P.FIX}
    monkeypatch.setattr(uj, "U1_KEEP_C1_SIMILARITY_EXCLUSIONS", False)
    released = {k: P._run_prod(k)[0]["verified"] for k in P.FIX}
    changed = sorted(k for k in P.FIX if kept[k] != released[k])
    assert changed == sorted([P.G7_SHORT_EXCLUDED, P.G8_C1_EXCLUDED])
    assert all(released[k] for k in changed)                       # Secondary正答=救済
    assert not any(released[k] for k in P.FALSE_PASS_C_5)           # 誤PASS用C群5行は解放後もNG(誤受理0)
    assert sum(kept.values()) == 13 and sum(released.values()) == 15
