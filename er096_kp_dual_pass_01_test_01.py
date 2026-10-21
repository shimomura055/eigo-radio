"""KP英語phrase「Primary・Secondary両方PASS必須」(FAMILY-XZ-ASR-PASS-CONDITION-SPEC-AUDIT-01 委任_02 D-1)の未配線test(API 0)。
実行: .venv/Scripts/python.exe -m unittest er096_kp_dual_pass_01_test_01 -v
judge層(er078_asr_unified_judge_01)へ保存転写相当の差込み(mock secondary_fn)でユーザー§4の1〜5・7・8を表現する。
二相構成(Production .pyは本D-1では編集しない):
  - 現行(AttemptCtxに`dual_required`欄が無い): `CurrentBehavior`が「現行挙動」を固定する(force_secondaryだけでは①を満たさないGAPの証跡)。
  - D-2後(欄が存在): `DualRequired`が期待値(§4の1〜5)を検証する。欄が無い間はskipされる。
実行時の相は`PHASE`で出力される。"""
import dataclasses, os, sys, unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import er078_asr_unified_judge_01 as uj
import er006_preprod_hardening_01_validation as val

HAS_DUAL = "dual_required" in {f.name for f in dataclasses.fields(uj.AttemptCtx)}
PHASE = "D2_WIRED" if HAS_DUAL else "D1_CURRENT_BEHAVIOR"
CANON = "take part"


def accept(canon, stext):
    """Production _secondary_acceptの最小代理(classify_asr_matchのshould_pass)。API 0。"""
    r = val.classify_asr_match(canon, stext)
    return bool(r.should_pass), r.classification


def run(primary_text, primary_pass, sec_text, *, force=False, dual=False, sec_exc=None, rs=None, role="KP_EN"):
    calls = {"n": 0}

    def sec_fn(_ctx):
        calls["n"] += 1
        if sec_exc:
            raise sec_exc
        return sec_text

    kw = dict(canonical_text=CANON, wav_sha256="sha-" + str(primary_text) + str(sec_text) + str(force) + str(dual),
              audio_seconds=1.7, segment_key="kp4_en", slot=1, is_last_slot=False, force_secondary=force, run_state=rs)
    if dual:
        kw["dual_required"] = True
    ctx = uj.AttemptCtx(**kw)
    jr = uj.unified_judge(ctx, uj.PrimaryResult(passed=primary_pass, text=primary_text), sec_fn, lang="en", role=role,
                          secondary_accept_fn=accept)
    return jr, calls["n"]


class Common(unittest.TestCase):
    def test_phase_is_reported(self):
        print("PHASE=", PHASE)

    # ---- ユーザー§4 ケース7: その他の音声はPrimary PASSでAzure不要(現行維持。両相で成立) ----
    def test_case7_other_audio_primary_pass_no_azure(self):
        jr, n = run("Take part.", True, "Take part.")
        self.assertEqual(jr.state, uj.PASS)
        self.assertEqual(n, 0)

    # ---- ケース8: その他の音声はPrimary NG時に既存Secondary判定が機能(両相で成立) ----
    def test_case8_other_audio_primary_ng_secondary_rescue_remains(self):
        jr, n = run("Take tart.", False, "Take part.")
        self.assertEqual(n, 1)
        self.assertTrue(jr.verified)
        self.assertEqual(jr.state, uj.PASS_WITH_WARNING)

    # ---- minimal fallback(U2): force_secondaryの既存意味は不変(両相) ----
    def test_u2_force_secondary_primary_pass_secondary_pass(self):
        jr, n = run("Take part.", True, "Take part.", force=True)
        self.assertEqual((jr.state, n), (uj.PASS, 1))

    def test_u2_force_secondary_primary_pass_secondary_ng(self):
        jr, n = run("Take part.", True, "Take Tart.", force=True)
        self.assertFalse(jr.verified)
        self.assertEqual(n, 1)


@unittest.skipIf(HAS_DUAL, "D-2後は欄が存在するためCurrentBehavior(GAP記録)は対象外")
class CurrentBehavior(unittest.TestCase):
    """現行コードでのGAP記録。force_secondaryだけではKPの①を満たさない点を固定(D-2で`dual_required`新設の根拠)。"""
    def test_gap1_force_secondary_primary_ng_secondary_pass_is_accepted(self):
        # ケース3相当: 現行はPASS_WITH_WARNING(verified=True)。①の要件(不合格)を満たさない=GAP-1
        jr, n = run("Take tart.", False, "Take part.", force=True)
        self.assertTrue(jr.verified)
        self.assertEqual(jr.state, uj.PASS_WITH_WARNING)

    def test_gap2_default_primary_pass_never_calls_azure(self):
        # KPの現行呼出(force_secondaryなし): Primary PASSでAzure不呼出=take part型(Primary PASS/Azure NG)を見逃す
        jr, n = run("Take part.", True, "Take Tart.")
        self.assertEqual((jr.state, n), (uj.PASS, 0))

    def test_case5_azure_failure_with_force_secondary_is_not_pass(self):
        # ケース5: 現行force_secondaryでもAzure障害はPASS不可(NG_SECONDARY_UNAVAILABLE)。両相で守るべき不変条件
        for exc in (RuntimeError("timeout"), None):
            jr, n = run("Take part.", True, None if exc is None else "x", force=True, sec_exc=exc)
            self.assertFalse(jr.verified)
            self.assertEqual(jr.state, uj.NG_SECONDARY_UNAVAILABLE)
            self.assertTrue(jr.secondary_unavailable)

    def test_circuit_open_is_not_pass(self):
        rs = uj.RunState()
        rs.circuit_open = True
        jr, n = run("Take part.", True, "Take part.", force=True, rs=rs)
        self.assertEqual((jr.state, n), (uj.NG_SECONDARY_UNAVAILABLE, 0))


@unittest.skipUnless(HAS_DUAL, "dual_required未実装(D-1段階)。D-2で有効化")
class DualRequired(unittest.TestCase):
    """D-2後の期待値(ユーザー§4 ケース1〜5)。KP英語phraseは`dual_required=True`。"""
    def test_case1_both_pass(self):
        jr, n = run("Take part.", True, "Take part.", dual=True)
        self.assertEqual(jr.state, uj.PASS); self.assertEqual(n, 1)
        self.assertTrue(jr.audit_record["dual"]["primary_pass"] and jr.audit_record["dual"]["secondary_pass"])

    def test_case2_primary_pass_secondary_ng_rejected(self):  # take part型
        jr, n = run("Take part.", True, "Take Tart.", dual=True)
        self.assertFalse(jr.verified); self.assertEqual(n, 1)

    def test_case3_primary_ng_secondary_pass_rejected_no_warning_pass(self):
        jr, n = run("Take tart.", False, "Take part.", dual=True)
        self.assertFalse(jr.verified)
        self.assertNotEqual(jr.state, uj.PASS_WITH_WARNING)

    def test_case4_both_ng(self):
        jr, n = run("Take tart.", False, "Take Tart.", dual=True)
        self.assertFalse(jr.verified)

    def test_case5_azure_failure_not_primary_only_pass(self):
        for exc in (RuntimeError("timeout"),):
            jr, n = run("Take part.", True, "x", dual=True, sec_exc=exc)
            self.assertFalse(jr.verified); self.assertTrue(jr.secondary_unavailable)
        jr, n = run("Take part.", True, "", dual=True)  # 空転写
        self.assertFalse(jr.verified)

    def test_primary_rescued_by_secondary_layer_counts_as_primary_ng(self):
        # 非ラテンKP層/Tier3 corroborationはAzure転写でPrimaryをPASSさせた救済。①ではOpenAI自身のPASSではないため不合格
        pr = uj.PrimaryResult(passed=True, text="テイクパート", adopted_text="Take part.", signals={"primary_rescued_by_secondary": True})
        ctx = uj.AttemptCtx(canonical_text=CANON, wav_sha256="sha-rescued", audio_seconds=1.7, dual_required=True)
        jr = uj.unified_judge(ctx, pr, lambda c: "Take part.", lang="en", role="KP_EN", secondary_accept_fn=accept)
        self.assertFalse(jr.verified)

    def test_dual_not_applied_without_flag(self):
        jr, n = run("Take part.", True, "Take Tart.")  # 非KP: Azure不要のまま
        self.assertEqual((jr.state, n), (uj.PASS, 0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
