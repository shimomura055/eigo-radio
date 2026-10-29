# -*- coding: utf-8 -*-
"""JA-ASR-V2-BETA-PRODUCTION-WIRING-01 委任_02A: 新module `er078_ja_v2beta_01` の単体test(API 0・mock ASR・socket guard)と静的test。
TEST_PLAN_01 の T-L1/T-B/T-E/T-M1/T-W1/T-G/T-D/T-NB5/T-NB6 と、Opus必須修正 M-1〜M-6 / R-9 の対応ケース。
実行: .venv\\Scripts\\python.exe -m pytest er078_ja_v2beta_01_test_01.py -q"""
from __future__ import annotations

import ast
import glob
import hashlib
import inspect
import os
import re
import subprocess
import sys

import pytest

import er078_ja_v2beta_test_support_01 as T

import er007_ja_secondary_asr_01 as sec
import er078_asr_unified_judge_01 as uj
import er078_ja_v2beta_01 as v2b

ROOT = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable


def _prod_py_files():
    out = []
    for f in glob.glob(os.path.join(ROOT, "*.py")):
        n = os.path.basename(f)
        if "_test" in n or n.startswith("test_") or n == "conftest.py":
            continue
        out.append(f)
    return out


def _read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


# ============================================================
# T-L1a: v2読み規則(値の表記差・助詞の発音形)
# ============================================================
GENERIC_V2_POSITIVE = [
    # (原稿, ASR転写)  題固有語を含まない汎用題。値表記差+助詞は→わ
    ("今日の売上は1,200円でした。", "今日の売上わ1200円でした。"),
    ("参加者は三十人でした。", "参加者わ30人でした。"),
    ("この店の価格は五百円です。", "この店の価格わ500円です。"),
    ("駅までの距離は2,000メートルです。", "駅までの距離わ2000メートルです。"),
    ("会議の所要時間は三十分でした。", "会議の所要時間わ30分でした。"),
    ("利用者は年間4,500人に増えました。", "利用者わ年間4500人に増えました。"),
    ("今年の売上は約八百円です。", "今年の売上わ約800円です。"),
    ("平均年齢は四十五歳でした。", "平均年齢わ45歳でした。"),
    ("来場者は毎日200人です。", "来場者わ毎日200人です。"),
    ("通勤の時間は一時間ほどです。", "通勤の時間わ1時間ほどです。"),
]


@pytest.mark.parametrize("canon,asr", GENERIC_V2_POSITIVE)
def test_t_g2_generic_v2_positive_is_pass_w_with_newlayer_warning(canon, asr):
    r, az = T.judge(canon, asr, None)
    j = T.aj(r)
    assert j["state"] == uj.PASS_WITH_WARNING, (j["state"], j["reason_code"])
    assert j["verdict"] == "PASS_W" and j["rescue_basis"] == "v2" and j["judge_rule_version"] == v2b.JUDGE_RULE_VERSION
    assert v2b.W_NEWLAYER_PRON in j["warnings"]
    assert az.calls == 0, "Primary救済ではAzureを呼ばない"
    assert r["verified"] is True and r["human_review_required"] is False and r["stop_retrying"] is False


@pytest.mark.parametrize("canon,asr", GENERIC_V2_POSITIVE)
def test_generic_v2_positive_is_ng_without_scope(canon, asr):
    r, _ = T.judge(canon, asr, None, scope=None)
    assert "ja_v2beta" not in T.aj(r) and "verdict" not in T.aj(r)
    assert T.aj(r)["state"] not in uj.PASSING_STATES or T.aj(r)["state"] == uj.PASS_WITH_WARNING   # 従来判定(L0)のまま


GENERIC_NEGATIVE = [
    ("今日の売上は1,200円でした。", "今日の売上わ1300円でした。"),      # 値違い
    ("今日の売上は1,200円でした。", "今日の売上わ12,000円でした。"),    # 桁違い
    ("参加者は三十人でした。", "参加者わ30台でした。"),                   # 助数詞違い
    ("参加者は三十人でした。", "参加者わでした。"),                       # 脱落
    ("参加者は三十人でした。", "参加者わ30人ではありませんでした。"),    # 否定
    ("会議の所要時間は三十分でした。", "会議の所要時間わ30秒でした。"),   # 助数詞違い(単位)
]


@pytest.mark.parametrize("canon,asr", GENERIC_NEGATIVE)
def test_t_n_ng_generic_negatives_have_no_new_pass(canon, asr):
    for az in (None, asr, canon):   # Secondaryなし / Primaryと同じ誤り / 原稿どおり(最悪露出)
        r, _ = T.judge(canon, asr, az)
        j = T.aj(r)
        if j["state"] in uj.PASSING_STATES:
            # 原稿どおりのSecondaryならSecondary自体が受理する(従来から)。新層の寄与(rescue_basis)による通過は不可。
            assert j.get("rescue_basis") is None, (canon, asr, az, j.get("rescue_basis"), j["reason_code"])


def test_t_m1_irregular_reading_numeral_is_never_rescued_by_new_layers():
    # 不規則読み数詞(一日・三日・二十歳等)。ASRの漢数字/算用数字表記から読みの正誤は判別できない。
    for canon, asr in (("会議は三日間でした。", "会議わ3日間でした。"), ("彼は二十歳になりました。", "彼わ20歳になりました。"),
                       ("一日中雨でした。", "1日中雨でした。")):
        for az in (None, asr):
            r, _ = T.judge(canon, asr, az)
            assert T.aj(r).get("rescue_basis") is None, (canon, asr, az)
    # β側: 原稿に不規則読み原子 -> irregular_reading_value でNG
    b = v2b.composite_judge("会議は三日間でした。", "会議は3日間でした。", "会議は3日間でした。",
                            {"engine": "azure", "wav_sha256": "a" * 64, "phrase_list_hash": ""})
    assert b.equal is False and b.blocked_by == "A4a_irregular_reading"


# ============================================================
# T-B: β
# ============================================================
BETA_CANON = "参加者は5,300人でした。"
BETA_PRIMARY_GARBLE = "参加者は5000300人でした。"      # 5000+300 -> 5,300 に説明できる断片(観測形F-A)
BETA_META = {"engine": "azure", "wav_sha256": "b" * 64, "model_id": "azure-speech-stt", "phrase_list_hash": ""}


def test_t_b1_beta_primary_garble_with_secondary_value_is_pass_w():
    r, az = T.judge(BETA_CANON, BETA_PRIMARY_GARBLE, "参加者は5300人でした。")
    j = T.aj(r)
    assert j["state"] == uj.PASS_WITH_WARNING and j["reason_code"] == "ja_beta_composite" and j["rescue_basis"] == "beta"
    assert v2b.W_NEWLAYER_BETA in j["warnings"] and v2b.W_GARBLE_EXPLAINED in j["warnings"] and v2b.W_LISTEN_ADVISED in j["warnings"]
    assert j["ja_v2beta"]["beta"]["secondary_transcript"] == "参加者は5300人でした。"
    assert az.calls == 1
    assert r["final_status"] == "JA_SECONDARY_VALUE_PRIMARY_READING_COMPOSITE"         # R-1: SCG文言ではなくβ専用ラベル
    assert j["final_gate"]["applied"] is True and j["final_gate"]["target"] == "secondary"
    assert j["ja_v2beta"]["beta"]["original"] == {"state": "NG_PROTECTED", "reason_code": "p1_value_diff"}


@pytest.mark.parametrize("prim", ["参加者は500300人でした。", "参加者は5000030人でした。", "参加者は53000人でした。", "参加者は6000300人でした。"])
def test_t_b1_beta_non_observed_forms_are_not_explained(prim):
    r, _ = T.judge(BETA_CANON, prim, "参加者は5300人でした。")
    assert T.aj(r).get("rescue_basis") is None and T.aj(r)["state"] not in uj.PASSING_STATES, prim


def test_t_b2_secondary_failure_keeps_original_ng_and_counts_toward_circuit():
    rs = uj.RunState()
    wav = T.make_wav("b2-fail")
    for i in range(3):
        r, az = T.judge(BETA_CANON, BETA_PRIMARY_GARBLE, None, wav=T.make_wav(f"b2-fail-{i}"), attempt_ctx={"max_len": 400, "run_state": rs})
        j = T.aj(r)
        assert j["state"] == uj.NG_PROTECTED and j["reason_code"] == "p1_value_diff" and j["verdict"] == "NG"     # 判定は元のNGのまま
        assert j["ja_v2beta"]["beta_skipped"] == "secondary_unavailable"
        assert az.calls == 1
        assert rs.secondary_consecutive_failures == i + 1, "R-2: βのSecondary失敗もcircuit計上"
    assert rs.circuit_open is True and rs.secondary_failures_total == 3
    # circuit open後はβもSecondaryを呼ばない(M-1)
    r, az = T.judge(BETA_CANON, BETA_PRIMARY_GARBLE, "参加者は5300人でした。", wav=T.make_wav("b2-open"), attempt_ctx={"max_len": 400, "run_state": rs})
    j = T.aj(r)
    assert az.calls == 0 and j["state"] == uj.NG_PROTECTED and j["ja_v2beta"]["beta_skipped"] == "circuit_open"


def test_m1_circuit_open_blocks_beta_secondary_call_and_stays_ng():
    rs = uj.RunState(circuit_open=True)
    r, az = T.judge(BETA_CANON, BETA_PRIMARY_GARBLE, "参加者は5300人でした。", attempt_ctx={"max_len": 400, "run_state": rs})
    j = T.aj(r)
    assert az.calls == 0 and j["state"] == uj.NG_PROTECTED and j["reason_code"] == "p1_value_diff"
    assert j["ja_v2beta"]["beta_skipped"] == "circuit_open" and j["rescue_basis"] is None


def test_m2_beta_cost_calls_and_run_state_match_real_call():
    rs = uj.RunState()
    wav = T.make_wav("m2-cost", seconds=3.0)
    r, az = T.judge(BETA_CANON, BETA_PRIMARY_GARBLE, "参加者は5300人でした。", wav=wav, attempt_ctx={"max_len": 400, "run_state": rs})
    j = T.aj(r)
    assert az.calls == 1
    sec_a = j["secondary"]
    assert sec_a["called"] is True and sec_a["cached"] is False and sec_a["text"] == "参加者は5300人でした。"
    assert j["cost"]["azure_calls"] == 1 and j["cost"]["est_jpy"] > 0
    assert rs.secondary_calls == 1 and rs.secondary_consecutive_failures == 0
    assert abs(rs.est_jpy_total - j["cost"]["est_jpy"]) < 1e-9, "auditのcostとrsの集計が一致"
    assert j["adapter"]["azure_real_calls"] == 1                      # er007:786 の集計(sec['called'])がβ呼出を数える
    assert r["cascade_invoked"] is True and any(s.get("provider") == "azure" for s in r["steps"])
    assert sec_a["provenance_complete"] is True


def test_t_d3_beta_azure_call_is_shared_by_sha_cache_no_duplicate_cost():
    rs = uj.RunState()
    cache = uj.SecondaryCache()
    wav = T.make_wav("d3-cache")
    ctx = {"max_len": 400, "run_state": rs, "cache": cache}
    r1, az1 = T.judge(BETA_CANON, BETA_PRIMARY_GARBLE, "参加者は5300人でした。", wav=wav, attempt_ctx=ctx)
    r2, az2 = T.judge(BETA_CANON, BETA_PRIMARY_GARBLE, "参加者は5300人でした。", wav=wav, attempt_ctx=ctx)
    assert az1.calls == 1 and az2.calls == 0 and cache.hits == 1
    assert T.aj(r2)["secondary"]["cached"] is True and T.aj(r2)["cost"]["azure_calls"] == 0
    assert rs.secondary_calls == 1


def test_t_b5_p1_type_precheck_false_does_not_call_azure():
    # Primaryが数値garbleでも断片説明できない形(precheckがFalse) -> Azureを呼ばない(費用0)
    r, az = T.judge(BETA_CANON, "参加者は6000300人でした。", "参加者は5300人でした。")
    j = T.aj(r)
    assert az.calls == 0 and j["state"] == uj.NG_PROTECTED and str(j["ja_v2beta"].get("beta_skipped", "")).startswith("precheck:")


def test_m3_primary_length_ng_is_never_rescued_by_beta_with_and_without_max_len():
    # max_len指定あり: Primary転写がmax_len超過
    r, az = T.judge(BETA_CANON, BETA_PRIMARY_GARBLE, "参加者は5300人でした。", attempt_ctx={"max_len": 5})
    j = T.aj(r)
    assert j["state"] in (uj.NG_PROTECTED, uj.NG_BOTH) and j["rescue_basis"] is None and j["ja_v2beta"]["beta_skipped"] == "M3_primary_length_ng" and az.calls == 0
    assert r["verified"] is False
    # max_len未指定の呼出元(安全ラッチ=旧挙動)で length_ok=False
    r2, az2 = T.judge(BETA_CANON, BETA_PRIMARY_GARBLE, "参加者は5300人でした。", attempt_ctx={}, length_ok=False)
    j2 = T.aj(r2)
    assert j2["rescue_basis"] is None and r2["verified"] is False and az2.calls == 0


def test_t_b3_beta_secondary_value_mismatch_or_sequence_mismatch_is_ng():
    for sec_text in ("参加者は5400人でした。", "参加者は5300人と10人でした。", "参加者は5300でした。"):
        r, _ = T.judge(BETA_CANON, BETA_PRIMARY_GARBLE, sec_text)
        assert T.aj(r).get("rescue_basis") is None and T.aj(r)["state"] not in uj.PASSING_STATES, sec_text
    # かな数詞・あいまい原子(R-4)
    b = v2b.composite_judge("参加者はごひゃく人でした。", "参加者は5000300人でした。", "参加者は500人でした。", BETA_META)
    assert b.equal is False


def test_t_b4_m7_phrase_list_hash_not_empty_or_unknown_is_fail_closed():
    for meta in (dict(BETA_META, phrase_list_hash="abc"), {k: v for k, v in BETA_META.items() if k != "phrase_list_hash"},
                 dict(BETA_META, wav_sha256=""), dict(BETA_META, wav_sha256="nosha:1")):
        b = v2b.composite_judge(BETA_CANON, BETA_PRIMARY_GARBLE, "参加者は5300人でした。", meta)
        assert b.equal is False, meta
    b_ok = v2b.composite_judge(BETA_CANON, BETA_PRIMARY_GARBLE, "参加者は5300人でした。", BETA_META)
    assert b_ok.equal is True
    # adapterは原稿をAzureへ渡さない: _azure_stt_strictはphrase list系関数を呼ばない(静的)
    src = inspect.getsource(sec._azure_stt_strict)
    assert "phrase_list" not in src.lower() or "with_phrase_list" not in src


def test_t_b6_beta_does_not_fire_on_negation_or_p2_exclusion():
    r, az = T.judge("参加者は5,300人ではありません。", "参加者は5000300人です。", "参加者は5300人ではありません。")
    assert T.aj(r).get("rescue_basis") is None
    # 登録読み辞書(A7)不一致 -> βは発火しない
    r2, _ = T.judge(BETA_CANON, BETA_PRIMARY_GARBLE, "参加者は5300人でした。", expected_readings={"参加者": "サンカシャ"})
    assert T.aj(r2)["state"] in uj.PASSING_STATES or T.aj(r2).get("rescue_basis") is None


def test_r1_beta_no_speech_secondary_is_not_beta_input():
    r, az = T.judge(BETA_CANON, BETA_PRIMARY_GARBLE, "   ")        # 空転写 = NO_SPEECH(障害ではない)
    j = T.aj(r)
    assert j.get("rescue_basis") is None and j["state"] not in uj.PASSING_STATES


# ============================================================
# T-E / T-W: 維持する安全対策・新層救済は必ず警告付き
# ============================================================
def test_t_e_m6_e3_e4_blocks_all_new_layers():
    import er109_xz_scope_01 as xz
    with xz.run_scope("X"):
        s3 = v2b.begin("x", "y", e3=[("a", "b")], e4=None)
        s4 = v2b.begin("x", "y", e3=None, e4=[("a", "b")])
        s0 = v2b.begin("x", "y", e3=None, e4=None)
    assert s3.blocked_by == "M6_E3" and not s3.usable
    assert s4.blocked_by == "M6_E4" and not s4.usable
    assert s0.blocked_by is None and s0.usable


def test_t_e1_real_e3_input_gets_blocked_by_and_equals_l0():
    # OPEN-333 E3(candidate_e_rejections)が非空の実入力: 新層は全て不適用(従来判定と同一)で、blocked_byを記録する
    canon, prim = "月のしわ、8,900本超", "月の八千九百本長"
    base, _ = T.judge(canon, prim, "月の八千九百本長", scope=None)
    r, az = T.judge(canon, prim, "月の八千九百本長", scope="X")
    j, jb = T.aj(r), T.aj(base)
    assert j["ja_v2beta"].get("blocked_by") == "M6_E3"
    assert (j["state"], j["reason_code"], j["warnings"]) == (jb["state"], jb["reason_code"], jb["warnings"]) and j["rescue_basis"] is None


def test_t_w1_new_layer_rescue_is_always_pass_with_warning_never_clean_pass():
    assert not ({v2b.PRON_LABEL, v2b.COMPOSITE_LABEL, *v2b.NEWLAYER_WARNINGS} & set(uj.APPROVED_EQUIVALENCE_BASES))
    assert v2b.PRON_LABEL not in sec._READING_MATCH_CLASSIFICATIONS and v2b.COMPOSITE_LABEL not in sec._READING_MATCH_CLASSIFICATIONS
    assert uj.READING_MATCH_BASIS not in (v2b.PRON_LABEL, v2b.COMPOSITE_LABEL)
    for canon, asr in GENERIC_V2_POSITIVE:
        r, _ = T.judge(canon, asr, None)
        assert T.aj(r)["state"] == uj.PASS_WITH_WARNING
    r, _ = T.judge(BETA_CANON, BETA_PRIMARY_GARBLE, "参加者は5300人でした。")
    assert T.aj(r)["state"] == uj.PASS_WITH_WARNING


def test_m6_secondary_side_v2_contribution_gets_warning_and_upgrades_clean_pass():
    # Secondary側v2の寄与 (adapter): Primaryは別内容でNG、Secondaryが助詞は→わ+値表記差
    r, az = T.judge("今日の売上は1,200円でした。", "今日の運動は千二百円でした。", "今日の売上わ1200円でした。")
    j = T.aj(r)
    assert j["state"] == uj.PASS_WITH_WARNING and j["rescue_basis"] == "v2" and v2b.W_NEWLAYER_PRON in j["warnings"] and j["reason_code"] == "secondary_confirmed"
    assert j["ja_v2beta"]["layers"][0]["side"] == "secondary" and j["ja_v2beta"]["layers"][0]["effective"] is True
    # force_secondary_agreed (state=PASS) にSecondary側v2寄与が重なる場合は PASS_W へ格上げ
    ctx = uj.AttemptCtx(canonical_text="x", wav_sha256="c" * 64)
    audit = {"state": uj.PASS, "reason_code": "force_secondary_agreed", "warnings": [], "p3_entry": "force_secondary", "secondary": {}, "length": {}}
    jr = uj.JudgeResult(uj.PASS, [], audit, "force_secondary_agreed")
    st = v2b.V2bState(active=True, scope="X")
    st.layers.append({"layer": "v2_pron", "side": "secondary", "cause": "A2_particle", "effective": None})
    st.secondary_layer_accepted = True
    jr2 = v2b.apply_secondary_layer_contribution(st, jr)
    assert jr2.state == uj.PASS_WITH_WARNING and v2b.W_NEWLAYER_PRON in jr2.warning_labels
    assert jr2.audit_record["state"] == uj.PASS_WITH_WARNING and v2b.W_NEWLAYER_PRON in jr2.audit_record["warnings"]


def test_r3_effectiveness_follows_final_path_primary_demoted_by_length_is_not_a_contribution():
    r, az = T.judge("今日の売上は千二百円でした。", "今日の売上わ1200円でした。", "今日の売上は千二百円でした。", attempt_ctx={"max_len": 10})
    j = T.aj(r)
    assert j["state"] == uj.NG_BOTH
    layers = j["ja_v2beta"]["layers"]
    assert layers and all(x["effective"] is False for x in layers)
    assert j["rescue_basis"] is None and v2b.contributed(j) is False        # NG recordに警告が残っても寄与にならない


def test_r1_pass_w_secondary_confirmed_label_is_not_overwritten_for_non_beta():
    r, _ = T.judge("今日の売上は1,200円でした。", "今日の運動は千二百円でした。", "今日の売上わ1200円でした。")
    assert r["final_status"] != "JA_SECONDARY_VALUE_PRIMARY_READING_COMPOSITE"


# ============================================================
# R-7: flag定数 / scope外byte同一
# ============================================================
def test_r7_constant_off_in_scope_records_disabled_by_constant_and_equals_l0(monkeypatch):
    base, _ = T.judge("今日の売上は1,200円でした。", "今日の売上わ1200円でした。", None, scope=None)
    monkeypatch.setattr(v2b, "JA_V2_BETA_ENABLED", False)
    r, _ = T.judge("今日の売上は1,200円でした。", "今日の売上わ1200円でした。", None, scope="X")
    j, jb = T.aj(r), T.aj(base)
    assert j["ja_v2beta"] == {"active": False, "scope": "X", "disabled_by": "constant"}
    assert (j["state"], j["reason_code"], j["warnings"]) == (jb["state"], jb["reason_code"], jb["warnings"])
    assert "verdict" not in j and "judge_rule_version" not in j


def test_scope_none_adds_no_keys_at_all():
    r, _ = T.judge("今日の売上は1,200円でした。", "今日の売上わ1200円でした。", None, scope=None)
    j = T.aj(r)
    for k in ("ja_v2beta", "verdict", "rescue_basis", "judge_rule_version", "rescue_reason_ja"):
        assert k not in j


def test_t_d1_default_on_is_true_and_only_the_reader_function_reads_the_constant():
    assert v2b.JA_V2_BETA_ENABLED is True
    # 読取は is_active_for_run() のみ(AST)。他module/他関数が直接読まない
    tree = ast.parse(_read(os.path.join(ROOT, "er078_ja_v2beta_01.py")))
    readers = []
    for fn in ast.walk(tree):
        if isinstance(fn, ast.FunctionDef):
            for n in ast.walk(fn):
                if isinstance(n, ast.Name) and n.id == "JA_V2_BETA_ENABLED":
                    readers.append(fn.name)
    assert set(readers) == {"is_active_for_run"}, readers
    # 他のProduction fileは定数名を参照しない(env/引数/設定dictからの迂回路なし)
    hits = [os.path.basename(f) for f in _prod_py_files() if os.path.basename(f) != "er078_ja_v2beta_01.py" and "JA_V2_BETA_ENABLED" in _read(f)]
    assert hits == [], hits
    # env/起動scriptでON/OFFしていない
    for pat in ("*.bat", "*.ps1", "*.sh", "*.cmd"):
        for p in glob.glob(os.path.join(ROOT, pat)):
            assert "JA_V2_BETA" not in _read(p)
    assert not os.path.exists(os.path.join(ROOT, ".env")) or "JA_V2_BETA" not in _read(os.path.join(ROOT, ".env"))


def test_is_active_for_run_reads_only_current_scope_not_the_ortho_flag(monkeypatch):
    import er109_xz_scope_01 as xz
    assert v2b.is_active_for_run() is False
    with xz.run_scope("Y"):
        assert v2b.is_active_for_run() is True
        # ortho flagをOFFにしても本機能はそれと連動しない
        import er109_asr_orthographic_equivalence_01 as e109
        monkeypatch.setattr(e109, "ORTHOGRAPHIC_EQUIVALENCE_ENABLED", False)
        assert xz.is_active_for_run() is False and v2b.is_active_for_run() is True


# ============================================================
# T-D2 / T-G1 / T-NB5 / T-NB6 / import graph: 静的test
# ============================================================
def test_t_d2_removed_rules_are_not_present_in_production():
    banned = {"r1_block", "KUNYOMI_OKURIGANA", "consensus", "best_of_n", "best_of_n_ref", "_getframe", "retry_eligible", "l3_judge", "l3_rewrite_one",
              "make_layer", "_adapter", "contradicts", "design_a"}
    for n in ("er078_ja_v2beta_01.py", "er007_ja_secondary_asr_01.py"):
        tree = ast.parse(_read(os.path.join(ROOT, n)))
        idents = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                idents.add(node.id)
            elif isinstance(node, ast.Attribute):
                idents.add(node.attr)
            elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                idents.add(node.name)
        assert not (idents & banned), (n, idents & banned)
    assert "JA_COMPOSITE_LISTEN_REQUIRED" not in "".join(_read(f) for f in _prod_py_files())
    # veto(Secondary読み相違のNG化)・ASR再試行は無い: 読み相違は警告のみ
    src = _read(os.path.join(ROOT, "er078_ja_v2beta_01.py"))
    assert "secondary_reading_conflict(veto)" not in src


def test_t_g1_new_module_source_has_no_theme_specific_words():
    src = _read(os.path.join(ROOT, "er078_ja_v2beta_01.py"))
    for w in ("月", "しわ", "皺", "詩", "超", "岩", "縮", "上着", "8,900", "8900", "杉野", "メロス", "AI島", "yemen", "Yemen"):
        assert w not in src, w
    # 許可: 助詞「は」「へ」・数詞文字・桁区切りのみ(題由来の名詞を持たない)。数詞文字以外のCJK漢字は日本語の説明語(コメント/文言)に限る


def test_t_g4_no_article_or_topic_id_reference_in_new_module():
    src = _read(os.path.join(ROOT, "er078_ja_v2beta_01.py"))
    assert not re.search(r"moon|MOON|theme_id|article_id|topic_id|FX-MOON", src)


def test_nb5_control_flow_never_reads_report_only_fields():
    allowed = {"er078_ja_v2beta_01.py", "er078_pass_with_warning_registry_01.py", "er078_reuse_value_guard_01.py"}   # 生成/報告/再利用可否(guard_entry内contributed)
    needles = ("rescue_basis", "listen_advised", "weak_rank", "W_LISTEN_ADVISED", "JA_COMPOSITE_LISTEN_ADVISED", "rescue_reason_ja")
    hits = {}
    for f in _prod_py_files():
        n = os.path.basename(f)
        if n in allowed:
            continue
        txt = _read(f)
        for w in needles:
            if w in txt:
                hits.setdefault(n, []).append(w)
    assert hits == {}, hits
    # er007は新moduleの関数を呼ぶだけ(verdict/rescue_basisを条件分岐で読まない)
    tree = ast.parse(_read(os.path.join(ROOT, "er007_ja_secondary_asr_01.py")))
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            assert n.value not in ("PASS_W", "rescue_basis", "listen_advised")
    # 新moduleでverdict/rescue_basis/listen_advisedを『読む』のは finalize_audit(書込み)・rescue_basis_of・contributed のみ
    tree2 = ast.parse(_read(os.path.join(ROOT, "er078_ja_v2beta_01.py")))
    readers = set()
    for fn in tree2.body:
        if isinstance(fn, ast.FunctionDef):
            for n in ast.walk(fn):
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "get" and n.args and isinstance(n.args[0], ast.Constant) \
                        and n.args[0].value in ("rescue_basis", "verdict", "listen_advised"):
                    readers.add(fn.name)
    assert readers <= {"contributed"}, readers


def test_nb6_no_publish_or_delivery_mechanism_in_new_module():
    src = _read(os.path.join(ROOT, "er078_ja_v2beta_01.py"))
    for w in ("publish", "upload", "git push", "requests", "smtplib", "urllib", "subprocess", "socket", "boto3"):
        assert w not in src, w
    assert "試聴必須" not in src and "listen_required" not in src and "LISTEN_REQUIRED" not in src


def test_import_graph_scope_outside_never_imports_new_module_or_heavy_libs():
    code = (
        "import sys, wave, os, tempfile\n"
        "import test_state_isolation_01\n"
        "import er007_ja_secondary_asr_01 as s\n"
        "assert 'er078_ja_v2beta_01' not in sys.modules\n"
        "p=os.path.join(tempfile.mkdtemp(),'a.wav'); w=wave.open(p,'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000); w.writeframes(b'\\0\\0'*8000); w.close()\n"
        "s._azure_stt_strict=lambda *a,**k:(None,'stub')\n"
        "import er007_ja_asr_validator_01 as j; j.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED=False\n"
        "r=s.evaluate_attempt_ja_with_cascade_detail('売上は100円です。','売上は100円です。',p,cascade_enabled=True)\n"
        "assert 'er078_ja_v2beta_01' not in sys.modules, 'scope外で新moduleをimportした'\n"
        "assert 'ja_v2beta' not in r['asr_judgement']\n"
        "print('OK')\n")
    out = subprocess.run([PY, "-c", code], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    assert out.returncode == 0 and "OK" in out.stdout, out.stderr[-600:]
    # 新module単体のimportはJA adapter/検証器/読み辞書/Variant Layerを引かない(判定時の遅延import。循環importなし)
    code2 = ("import sys\nimport er078_ja_v2beta_01\n"
             "for m in ('er007_ja_secondary_asr_01', 'er007_ja_asr_validator_01', 'er008_asr_variant_hardening_15_ja_kanji_readings'):\n"
             "    assert m not in sys.modules, m\nprint('OK')\n")
    out2 = subprocess.run([PY, "-c", code2], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    assert out2.returncode == 0 and "OK" in out2.stdout, out2.stderr[-600:]


# ============================================================
# M-5: 依存lib欠落/新module障害 -> 従来判定(L0)へ+ ja_v2beta.error 記録(無言で従来挙動に戻らない)
# ============================================================
def test_m5_dependency_failure_falls_back_to_l0_and_records_error(monkeypatch):
    canon, asr = "今日の売上は1,200円でした。", "今日の売上わ1200円でした。"
    base, _ = T.judge(canon, asr, None, scope=None)
    monkeypatch.setattr(v2b, "_d", lambda: (_ for _ in ()).throw(ImportError("No module named 'jaconv'")))
    r, _ = T.judge(canon, asr, None, scope="X")
    j, jb = T.aj(r), T.aj(base)
    assert (j["state"], j["reason_code"], j["warnings"]) == (jb["state"], jb["reason_code"], jb["warnings"])
    assert "jaconv" in str(j["ja_v2beta"].get("error"))
    assert j["verdict"] in ("NG", "PASS", "PASS_W", "HR") and j.get("rescue_basis") is None
    # beginの失敗(新module初期化)も同様
    monkeypatch.undo()
    monkeypatch.setattr(v2b, "begin", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    r2, _ = T.judge(canon, asr, None, scope="X")
    assert (T.aj(r2)["state"], T.aj(r2)["reason_code"]) == (jb["state"], jb["reason_code"])
    assert "boom" in T.aj(r2)["ja_v2beta"]["error"] and T.aj(r2)["ja_v2beta"]["active"] is False


def test_m5_beta_exception_falls_back_to_ng_and_config_stop_error_is_reraised(monkeypatch):
    monkeypatch.setattr(v2b, "composite_judge", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("beta boom")))
    r, _ = T.judge(BETA_CANON, BETA_PRIMARY_GARBLE, "参加者は5300人でした。")
    j = T.aj(r)
    assert j["state"] == uj.NG_PROTECTED and "beta boom" in j["ja_v2beta"]["error"]
    monkeypatch.setattr(v2b, "composite_judge", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("init_logger未呼出")))
    with pytest.raises(RuntimeError):
        T.judge(BETA_CANON, BETA_PRIMARY_GARBLE, "参加者は5300人でした。")


# ============================================================
# M-4 の版固定: 判定核hash <-> JUDGE_RULE_VERSION
# ============================================================
CORE_FUNCS = ("pron_hira", "_tag_pron", "_diff_spans", "c2_blocked", "irregular_atoms", "pron_value_equivalence", "to_classification", "value_layer",
              "explain_garble", "analyze_primary_values", "composite_core", "composite_judge", "precheck_composite", "_numeric_notation_ok",
              "_segments", "_place_ok", "_mask", "_atom_seq", "_unit_surface")
CORE_CONSTS = ("ELIG", "_PARTICLE_PRON", "_NUM_CHARS", "_RUN_CHARS", "TOKEN", "PRON_LABEL", "COMPOSITE_LABEL")
# 判定核を変えたら JUDGE_RULE_VERSION を上げ、ここの (版 -> hash) を更新する。版を上げずに核を変えるとこのtestが落ちる。
PINNED = {"ja_v2beta_r1off_01": "5548ee939c56d601044c684ae282cce3b09963b4ea644aa16b970650a53a922e"}


def _core_hash() -> str:
    h = hashlib.sha256()
    for n in CORE_FUNCS:
        h.update(inspect.getsource(getattr(v2b, n)).replace("\r\n", "\n").encode("utf-8"))
    for n in CORE_CONSTS:
        h.update(f"{n}={getattr(v2b, n)!r}".encode("utf-8"))
    return h.hexdigest()


def test_m4_judge_core_hash_is_pinned_to_judge_rule_version():
    assert v2b.JUDGE_RULE_VERSION in PINNED, "新しいJUDGE_RULE_VERSIONはPINNEDに登録する"
    assert PINNED[v2b.JUDGE_RULE_VERSION] == _core_hash(), f"判定核が変わった。JUDGE_RULE_VERSIONを上げて PINNED を更新する: {_core_hash()}"


# ============================================================
# R-9(a): precheck の健全性: composite_judge成立 => precheck成立 (corpus全行)
# ============================================================
def test_r9a_precheck_is_sound_over_the_stored_eval_corpus():
    import json
    p = os.path.join(ROOT, "docs", "research", "JA-ASR-FALSE-NG-ROOT-FIX-02", "eval_unified_03.out.json")
    if not os.path.exists(p):
        pytest.skip("eval corpus missing")
    rows = json.load(open(p, encoding="utf-8"))["rows"]
    checked = bad = 0
    from itertools import islice
    for r in rows:
        c, pr, sc = r["canon"], r["primary"], r["secondary"]
        if not (c and pr and sc):
            continue
        b = v2b.composite_judge(c, pr, sc, BETA_META)
        if b.equal:
            checked += 1
            pc = v2b.precheck_composite(c, pr)
            if not pc.may_call_secondary:
                bad += 1
    assert bad == 0 and checked > 0, (bad, checked)


# ============================================================
# 汎用性(T-G3 metamorphic): 題材語・前置き・数値を差し替えても verdict / rescue_basis が不変(題固有の分岐が無いことの検査)
# ============================================================
_META_SUBST = [("売上", "入場料"), ("売上", "気温"), ("参加者", "来場者"), ("会議", "授業")]


@pytest.mark.parametrize("canon,asr", GENERIC_V2_POSITIVE[:6])
def test_t_g3_metamorphic_topic_noun_swap_keeps_the_verdict(canon, asr):
    r0, _ = T.judge(canon, asr, None)
    base = (T.aj(r0)["verdict"], T.aj(r0)["rescue_basis"])
    assert base == ("PASS_W", "v2")
    for a, b in _META_SUBST:
        if a in canon and a in asr:
            r, _ = T.judge(canon.replace(a, b), asr.replace(a, b), None)
            assert (T.aj(r)["verdict"], T.aj(r)["rescue_basis"]) == base, (a, b)
    # 無関係な前置きを足しても不変(Primary側・原稿側の両方に同じ前置き)
    r, _ = T.judge("まず最初に。" + canon, "まず最初に。" + asr, None)
    assert (T.aj(r)["verdict"], T.aj(r)["rescue_basis"]) == base


@pytest.mark.parametrize("canon,asr", GENERIC_NEGATIVE)
def test_t_g3_metamorphic_negative_stays_non_rescued_after_noun_swap(canon, asr):
    for a, b in _META_SUBST:
        if a in canon and a in asr:
            c2, s2 = canon.replace(a, b), asr.replace(a, b)
            for az in (None, s2):
                r, _ = T.judge(c2, s2, az)
                j = T.aj(r)
                assert j.get("rescue_basis") is None, (c2, s2, az, j["state"], j["reason_code"])
