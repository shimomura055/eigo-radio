import re, shutil, subprocess, sys
OUT = "er058_output/unified_all_roles_production_wiring_01/patch_03b/"
import os
os.makedirs(OUT, exist_ok=True)

# ---------- F1 ----------
src = open("er011_b1_connected_speech_validator_01_f1_test_01.py", encoding="utf-8").read()
a = src.index("def test_cascade_replay_user_example_stays_non_pass_with_supporting_secondary():")
b = src.index("def test_cascade_replay_normal_connected_speech_still_passes():")
new_f1 = '''def test_cascade_replay_user_example_stays_non_pass_with_supporting_secondary():
    # [PROPOSED 委任_03b / 要Fable承認] F1の不変条件(Primary側P-chain=F1/Eq層はnon-passのまま、Eq層は不発動)を維持し、
    # 最終判定は「独立したSecondaryがcanonical全文を支持した場合のみ secondary_confirmed(PASS_WITH_WARNING)」へ更新
    # (DESIGN_01 §4-3d / ユーザー原文「Primary NGなら、不一致の種類によらず原則Secondary」「Primary NG・Secondary PASSならPASS_WITH_WARNING」)。
    c, a = USER_EXAMPLE
    for seg in SEGS:
        # (1) Secondary/localが「最初の差分位置でcanonicalを支持する」転写(=canonical全文)を返す設定
        r, calls = _replay(c, a, c, seg)
        aj = r["asr_judgement"]
        assert aj["primary"]["passed"] is False, (seg, aj["primary"])  # F1/Eq層のPrimary側判定はnon-passのまま
        assert aj["primary"]["label"] in ("TRUE_CONTENT_MISMATCH", "ASR_VALIDATION_UNCERTAIN")
        assert r["connected_speech_equivalence_layer_invoked"] is False  # CS/F1経由の受理はない
        assert "cs_equivalence" not in aj["adapter"]["layers"]
        assert calls == {"secondary": 1, "local": 0}  # Secondaryは統一judgeの1回のみ
        if r["verified"]:
            assert aj["reason_code"] == "secondary_confirmed" and aj["state"] == "PASS_WITH_WARNING", aj  # 受理はSecondary独立確認のみ+要試聴
        # (2) 独立証拠なし(Secondaryもprimaryと同じ"dogs")ならNGのまま=旧期待(non-pass)を維持
        r2, calls2 = _replay(c, a, a, seg)
        assert r2["verified"] is False, (seg, r2["classification"].classification)
        assert r2["classification"].should_pass is False
        assert r2["classification"].classification in ("TRUE_CONTENT_MISMATCH", "ASR_VALIDATION_UNCERTAIN")


def test_cascade_replay_multi_residual_after_first_eq_eligible_diff_stays_non_pass():
    # [PROPOSED 委任_03b / 要Fable承認] 上と同じ方針(F1残差>=2のEq層ガードは不変。最終受理はSecondary独立確認のみ)。
    canonical = "Young travelers still showed strong interest in the results."
    primary = "Young travelers still show strong interest in the outcomes."
    for seg in SEGS:
        r, calls = _replay(canonical, primary, canonical, seg)
        aj = r["asr_judgement"]
        assert aj["primary"]["passed"] is False
        assert r["connected_speech_equivalence_layer_invoked"] is False
        assert calls == {"secondary": 1, "local": 0}
        if r["verified"]:
            assert aj["reason_code"] == "secondary_confirmed" and aj["state"] == "PASS_WITH_WARNING", aj
        r2, _ = _replay(canonical, primary, primary, seg)
        assert r2["verified"] is False
        assert r2["connected_speech_equivalence_layer_invoked"] is False


'''
open(OUT + "er011_f1_test_PROPOSED.py", "w", encoding="utf-8").write(src[:a] + new_f1 + src[b:])

# ---------- CS mixed ----------
src = open("er011_connected_speech_equivalence_layer_production_wiring_01_test_01.py", encoding="utf-8").read()
a = src.index("def test_enabled_mixed_evidence_does_not_accept_but_records_diagnostic():")
b = src.index("def test_never_fires_on_number_mismatch_even_if_enabled():")
new_cs = '''def test_enabled_mixed_evidence_does_not_accept_but_records_diagnostic():
    # [PROPOSED 委任_03b / 要Fable承認] Eq層のMIXED判定(診断記録・Eq層による受理なし)は不変。最終判定は、独立Secondaryがcanonicalを
    # 支持した場合のみ secondary_confirmed(PASS_WITH_WARNING)。Secondaryも支持しなければNGのまま。
    orig_secondary_fn = secondary.get_full_text_via_azure_stt_with_phrase_list
    orig_local_fn = disfluency_qa.transcribe_verbatim
    canonical = "The cars turned back before reaching the bridge."
    primary = "The cars turn back before reaching the bridge."

    # Secondaryは誤ってcanonicalを支持、localは正しく実発話を支持(MIXED)。
    secondary.get_full_text_via_azure_stt_with_phrase_list = lambda *a, **k: (canonical, None)
    disfluency_qa.transcribe_verbatim = lambda *a, **k: [{"text": w} for w in primary.split()]
    try:
        r = secondary.evaluate_attempt_with_cascade_detail(
            canonical, primary, [], "dummy.wav", cascade_enabled=True,
            enable_connected_speech_equivalence_layer=True)
        aj = r["asr_judgement"]
        assert aj["primary"]["passed"] is False and aj["primary"]["label"] == "TRUE_CONTENT_MISMATCH"
        assert r["connected_speech_equivalence_layer_invoked"] is True
        eq_steps = [s for s in r["steps"] if s["step"] in ("connected_speech_equivalence_secondary", "connected_speech_equivalence_local")]
        assert eq_steps and all(s["layer_judgment"] == "EQUIVALENCE_LAYER_MIXED_EVIDENCE_INSUFFICIENT" for s in eq_steps)
        assert r["verified"] is False or (aj["reason_code"] == "secondary_confirmed" and aj["state"] == "PASS_WITH_WARNING")
        # Secondaryも支持しない(primaryと同じ"turn")ならNGのまま(旧期待を維持)
        secondary.get_full_text_via_azure_stt_with_phrase_list = lambda *a, **k: (primary, None)
        r2 = secondary.evaluate_attempt_with_cascade_detail(
            canonical, primary, [], "dummy2.wav", cascade_enabled=True,
            enable_connected_speech_equivalence_layer=True)
        assert r2["verified"] is False
        assert r2["classification"].classification == "TRUE_CONTENT_MISMATCH"
        assert r2["classification"].should_pass is False
        info = r2["classification"].connected_speech_info
        assert info is not None
        assert info["layer_judgment"] not in cs_equiv.ACCEPT_JUDGMENTS  # Secondaryが支持しない場合のEq層判定(INSUFFICIENT_EVIDENCE)も非受理
    finally:
        secondary.get_full_text_via_azure_stt_with_phrase_list = orig_secondary_fn
        disfluency_qa.transcribe_verbatim = orig_local_fn
    print("PASS: test_enabled_mixed_evidence_does_not_accept_but_records_diagnostic")


'''
open(OUT + "er011_cs_wiring_test_PROPOSED.py", "w", encoding="utf-8").write(src[:a] + new_cs + src[b:])

# ---------- Tier3 ----------
src = open("er021_en_asr_semantic_equivalence_production_wiring_01_test_01.py", encoding="utf-8").read()
a = src.index("    def test_role_not_applicable_tier3_not_attempted(self):")
b = src.index("    def test_numeric_mismatch_still_true_content_mismatch_not_swallowed_by_tier3(self):")
new_t3 = '''    def test_role_not_applicable_tier3_not_attempted(self):
        # [PROPOSED 委任_03b / 要Fable承認] role gate(Tier3は5role限定)は不変: role非適用ではTier3は発火しない
        # (steps/layersにtier3なし)。最終判定は、独立Secondaryがcanonicalを支持した場合のみ secondary_confirmed
        # (PASS_WITH_WARNING)。Secondaryがcanonicalを支持しなければNG(旧期待)。
        canonical = "We need to bring the main point together."
        asr = "We need to bring the main points together."
        detail = self._run(canonical, asr, corroborating_text=canonical,
                            segment_id=NON_APPLICABLE_SEGMENT_ID)
        self.assertNotIn("tier3", detail["asr_judgement"]["adapter"]["layers"])
        self.assertFalse(any(s["step"] == "tier3_corroboration_secondary" for s in detail["steps"]))
        self.assertEqual(detail["asr_judgement"]["state"], "PASS_WITH_WARNING")
        self.assertEqual(detail["asr_judgement"]["reason_code"], "secondary_confirmed")
        self.assertNotEqual(detail["final_status"], "SECONDARY_ASR_CORROBORATED_MATCH")  # Tier3経由の受理ではない
        detail2 = self._run(canonical, asr, corroborating_text=asr, segment_id=NON_APPLICABLE_SEGMENT_ID)
        self.assertFalse(detail2["verified"])

    def test_no_segment_id_tier3_not_attempted(self):
        # [PROPOSED 委任_03b / 要Fable承認] 上と同じ方針(segment_id未指定=role gate非適用)。
        canonical = "We need to bring the main point together."
        asr = "We need to bring the main points together."
        detail = self._run(canonical, asr, corroborating_text=canonical, segment_id=None)
        self.assertNotIn("tier3", detail["asr_judgement"]["adapter"]["layers"])
        self.assertFalse(any(s["step"] == "tier3_corroboration_secondary" for s in detail["steps"]))
        self.assertEqual(detail["asr_judgement"]["reason_code"], "secondary_confirmed")
        detail2 = self._run(canonical, asr, corroborating_text=asr, segment_id=None)
        self.assertFalse(detail2["verified"])

'''
open(OUT + "er021_tier3_test_PROPOSED.py", "w", encoding="utf-8").write(src[:a] + new_t3 + src[b:])
print("ok")
