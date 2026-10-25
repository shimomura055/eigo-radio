# -*- coding: utf-8 -*-
"""KGCPW 委任_02: gloss再整合(修正版が唯一の方式・既定ON)のProduction配線test(API不要、mock/fake client、JPY0)。

固定するもの: (1)API request bytes(golden sha、OF-KGCPW-01) (2)X解説text cache署名(M1/OF-KGCPW-06) (3)Z kp_expl署名(OF-KGCPW-07)
(4)ON化前・未評価の決定論検出(M2/OF-KGCPW-08) (5)Z snapshot優先復元+HR停止時のasset配備(M3/OF-KGCPW-09)
(6)X最終行・rc=2・try/finally・assemble level単位捕捉(OF-KGCPW-03/04/05/19) (7)NG_REVIEW_REQUIRED+HR itemでX TTS/assembleが止まり
gloss_alignment_run_status が出る(OF-KGCPW-17) (8)runbook参照・旧Trial script停止(OF-KGCPW-13/14)。
実行時に有料APIへ到達しないことは各testがfake client/mockで保証し、stop_paths testのforbid_real_apisも併用する。
"""
import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
import unittest.mock as mock

import er003_key_words_gloss_alignment as ga
import er003_test_kp_gloss_alignment_stop_paths as sp
import er019_family_x_audio_production_runner_01 as x
from er119_test_support_01 import declare_ctx as _declare_ctx  # noqa: E402

REPO = os.path.dirname(os.path.abspath(__file__))
GOLDEN_DIR = os.path.join(REPO, "er071_output", "m2p0_n01_production_wiring_01", "gloss_alignment_production_wiring_01", "golden")


class _FlagOn(unittest.TestCase):
    def setUp(self):
        old = ga.GLOSS_ALIGNMENT_ENABLED
        ga.GLOSS_ALIGNMENT_ENABLED = True
        self.addCleanup(setattr, ga, "GLOSS_ALIGNMENT_ENABLED", old)


class GoldenRequestBytes(unittest.TestCase):
    def test_alignment_request_bytes_match_golden(self):
        """OF-KGCPW-01: legacy撤去前のHEAD(64d3ec975)で固定したcorrected API request(model/reasoning/text.format全体/input、
        sort_keysなし)と、撤去後の同じ入力のshaが一致する(Prompt本文・schema内容/順序・developer messageが無変更)。"""
        old_env, old_cwd = os.environ.get("EIGO_KP_GLOSS_ALIGNMENT"), os.getcwd()
        try:
            spec = importlib.util.spec_from_file_location("kgcpw_golden_mod", os.path.join(GOLDEN_DIR, "make_alignment_request_golden_01.py"))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            cap = mod.capture()
        finally:
            os.chdir(old_cwd)
            if old_env is None:
                os.environ.pop("EIGO_KP_GLOSS_ALIGNMENT", None)
            else:
                os.environ["EIGO_KP_GLOSS_ALIGNMENT"] = old_env
        golden = json.load(open(os.path.join(GOLDEN_DIR, "alignment_request_golden_01.json"), encoding="utf-8"))
        for label in ("std_a2", "adv_b1b"):
            self.assertEqual(cap[label]["sha256"], golden[label]["sha256"], label)
            self.assertEqual(json.dumps(cap[label]["kwargs"], ensure_ascii=False),
                             json.dumps(golden[label]["kwargs"], ensure_ascii=False), label)
        self.assertEqual(cap["combined_sha256"], golden["combined_sha256"])


def _kp_items(status=None, gloss="インタビューをもとにした", kp="based on interviews"):
    return [{"rank": i, "display_phrase": f"phrase{i}", "key_phrase": kp if i == 2 else f"phrase{i}",
             "japanese_gloss": gloss if i == 2 else f"意味{i}", "source_sentence": "s",
             **({"gloss_alignment_status": status} if status else {})} for i in range(1, 6)]


class ExplanationCacheSignatureX(unittest.TestCase):
    """OF-KGCPW-06 (M1): X Adv解説text cache。"""

    def _resolve(self, items, cached):
        calls = []

        def gen(inp, **k):
            calls.append(inp)
            return {"items": {it["rank"]: {"status": "OK", "english_explanation": "e"} for it in inp}}
        with mock.patch.object(x.kp_explanation_gen, "generate_kp_explanations", side_effect=gen):
            out = x._resolve_kp_explanations_text(items, cached)
        return out, len(calls)

    def test_status_less_artifact_keeps_old_signature_compat(self):
        items = _kp_items()
        old_bundle = {"phrases_signature": [i["display_phrase"] for i in items], "items": {}}   # gloss_signatureなし(旧bundle)
        out, n = self._resolve(items, {"key_phrase_explanations_text": old_bundle})
        self.assertEqual(n, 0)
        self.assertTrue(out["reused_from_previous_run"])

    def test_status_artifact_with_old_bundle_regenerates(self):
        items = _kp_items(status=ga.STATUS_ALIGNED)
        old_bundle = {"phrases_signature": [i["display_phrase"] for i in items], "items": {}}   # gloss_signature欠落=不一致
        out, n = self._resolve(items, {"key_phrase_explanations_text": old_bundle})
        self.assertEqual(n, 1)
        self.assertFalse(out["reused_from_previous_run"])
        self.assertIn("gloss_signature", out)
        # 生成された新bundleは同じ入力なら再利用される
        out2, n2 = self._resolve(items, {"key_phrase_explanations_text": out})
        self.assertEqual(n2, 0)
        self.assertTrue(out2["reused_from_previous_run"])

    def test_key_phrase_or_gloss_change_regenerates(self):
        items = _kp_items(status=ga.STATUS_ALIGNED)
        first, _ = self._resolve(items, {})
        out, n = self._resolve(_kp_items(status=ga.STATUS_ALIGNED, kp="based on interview data"), {"key_phrase_explanations_text": first})
        self.assertEqual(n, 1)                                  # display_phraseが同じでもkey_phraseの変化で再生成
        out, n = self._resolve(_kp_items(status=ga.STATUS_HUMAN_RESOLVED, gloss="別の訳"), {"key_phrase_explanations_text": first})
        self.assertEqual(n, 1)                                  # glossの変化で再生成


class ExplanationSignatureZ(unittest.TestCase):
    """OF-KGCPW-07: Z kp_expl_b1b署名。status無し=従来(display_phraseのみ・Melos互換)、status有り=gloss含有(T3(l-Z)も参照)。"""

    def test_status_less_keeps_display_only_signature(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = __import__("er026_family_z_fiction_production_runner_01")
            ctx = r.build_mock_context(tmp)
            _declare_ctx(ctx)   # KP Human Review: 既存mock testのfixture(Human不在を明示宣言)
            with contextlib.redirect_stdout(io.StringIO()):
                r.run_stages(ctx, ["seed_check", "writer", "std_adjust", "plan", "support", "kp"])
            installed = json.load(open(f"{ctx.out_dir}/b1b/key_phrases/keywords_canonicalized.json", encoding="utf-8"))
            items = sorted(installed["items"], key=lambda i: i["rank"])
            self.assertFalse(any(i.get("gloss_alignment_status") for i in items))
            payload = [i["display_phrase"] for i in items]
            if any(i.get("source_reference_contract") for i in items):
                # 委任_16(SRC D1): source_reference_contractを持つitemがあれば解説sigにsrc(source_sentence_id/source_sentence)が加わる
                # (FZQI委任_06で期待値更新: status無し=glossは含まない/displayのみ+src。実装不変)
                payload = {"display": payload, "src": [[i.get("source_sentence_id", ""), i.get("source_sentence", "")] for i in items]}
            expected = r._sha(json.dumps(payload, ensure_ascii=False))
            pv = r._m().w62.rj(f"{ctx.out_dir}/writer/provenance.json")
            self.assertEqual(pv["downstream_stages"]["kp_expl_b1b"]["input_sha256"], expected)


class UnevaluatedDetection(_FlagOn):
    """OF-KGCPW-08 (M2): ON化前・未評価の成果物はX TTS関所/assemble前/Z stage_kp再利用/load_level_inputsで停止、対象0件は通過。"""

    def _pre_on_artifact(self, d):
        """kill switch OFFでrun_key_phrasesを実行 = ON化前に作られた成果物(対象itemにstatus無し)を再現する。"""
        ga.GLOSS_ALIGNMENT_ENABLED = False
        try:
            res, fn, out = sp.run_kp(d, [])
        finally:
            ga.GLOSS_ALIGNMENT_ENABLED = True
        self.assertEqual(res["canonicalization"]["gloss_alignment_status"], "DISABLED")
        return sp.load_kp(d)

    def test_x_tts_gate_and_assemble_stop_on_unevaluated(self):
        with tempfile.TemporaryDirectory() as base, sp.forbid_real_apis():
            lvl = os.path.join(base, "a2"); kp_dir = os.path.join(lvl, "key_phrases"); os.makedirs(kp_dir)
            kp = self._pre_on_artifact(kp_dir)
            self.assertEqual([i["rank"] for i in ga.collect_unevaluated(kp)], [2])
            narr = os.path.join(lvl, "narration"); os.makedirs(narr)
            with sp.x_stubs(x):
                results, delta = sp.stub_delta(lambda: x._generate_key_phrase_segments_a2(kp, narr, None))
                (results_b, bundle), delta_b = sp.stub_delta(lambda: x._generate_key_phrase_segments_b1(kp, narr, None))
            self.assertEqual(delta, {"tts": 0, "expl_llm": 0, "expl_tts": 0})
            self.assertEqual(delta_b, {"tts": 0, "expl_llm": 0, "expl_tts": 0})
            self.assertIsNone(bundle)
            ent = results[2]["english"]
            self.assertEqual(ent["status"], ga.STOPPED_STATUS)
            self.assertIn("未評価", ent["reason"])
            self.assertIn("KPを再生成", ent["reason"])
            with self.assertRaises(RuntimeError) as cm:
                x._assert_no_gloss_alignment_hr(lvl, "A2")
            self.assertIn("EPISODE_BLOCKED_BY_GLOSS_ALIGNMENT", str(cm.exception))
            self.assertIn("未評価", str(cm.exception))

    def test_x_zero_targets_pass(self):
        with tempfile.TemporaryDirectory() as base, sp.forbid_real_apis():
            lvl = os.path.join(base, "a2"); kp_dir = os.path.join(lvl, "key_phrases"); os.makedirs(kp_dir)
            res, fn, out = sp.run_kp(kp_dir, [], parsed=sp.canon_parsed(kp2="based on"))     # 対象0件
            kp = sp.load_kp(kp_dir)
            self.assertEqual(ga.collect_unevaluated(kp), [])
            narr = os.path.join(lvl, "narration"); os.makedirs(narr)
            with sp.x_stubs(x):
                results, delta = sp.stub_delta(lambda: x._generate_key_phrase_segments_a2(kp, narr, None))
            self.assertEqual(delta["tts"], 10)
            x._assert_no_gloss_alignment_hr(lvl, "A2")      # 例外なし

    def _z(self, tmp, fail_levels, align_enabled):
        r, ctx = sp.z_ctx(tmp, [], fail_levels=fail_levels, align_enabled=align_enabled)
        with contextlib.redirect_stdout(io.StringIO()):
            r.run_stages(ctx, ["seed_check", "writer", "std_adjust", "plan", "support"])
        return r, ctx

    def test_z_stage_kp_reuse_of_pre_on_stage_stops_with_regenerate_instruction(self):
        with tempfile.TemporaryDirectory() as tmp, sp.forbid_real_apis():
            r, ctx = self._z(tmp, ("B1",), align_enabled=False)    # ON化前のKP段(対象itemにstatus無し)
            msgs = []
            for _ in range(2):                                      # 1回目=生成直後、2回目=ensure_stage再利用
                with contextlib.redirect_stdout(io.StringIO()):
                    with self.assertRaises(r.FamilyZE2EStop) as cm:
                        r.run_stage(ctx, "kp")
                msgs.append(str(cm.exception))
            for m in msgs:
                self.assertIn("GLOSS_ALIGNMENT_UNEVALUATED(b1b)", m)
                self.assertIn("--regenerate-stage kp_b1b", m)
            # load_level_inputs(TTS/Gate/Assemblyの共有入力)も同じ理由で止まる
            os.makedirs(f"{ctx.out_dir}/b1b/key_phrases", exist_ok=True)
            import shutil
            shutil.copy(f"{ctx.out_dir}/key_phrases/b1b/keywords_canonicalized.json",
                        f"{ctx.out_dir}/b1b/key_phrases/keywords_canonicalized.json")
            with self.assertRaises(r.FamilyZE2EStop) as cm:
                r.load_level_inputs(ctx, "b1b")
            # KP Human Review(M-9): 消費側入口は先にreview/確定物の整合検査(KP_VOCAB_CONSUMER_CHECK_FAILED=同じgloss未評価の検出)で止まる。
            # 止まる理由(gloss未評価itemがある)は従来と同じで、止まる層が前段に1つ増えただけ(従来の検査も後段に残る)。
            self.assertTrue("GLOSS_ALIGNMENT_UNEVALUATED" in str(cm.exception) or "gloss未評価" in str(cm.exception), str(cm.exception))

    def test_z_zero_targets_pass(self):
        with tempfile.TemporaryDirectory() as tmp, sp.forbid_real_apis():
            r, ctx = self._z(tmp, (), align_enabled=False)         # 対象0件(KPが候補より伸びない)
            with contextlib.redirect_stdout(io.StringIO()):
                res = r.run_stage(ctx, "kp")
            self.assertIn("b1b", res)
            self.assertIn("gloss_alignment_flag", res["b1b"])


class ZSnapshotPriorityAndAssetInstall(_FlagOn):
    """OF-KGCPW-09 (M3)。"""

    def test_regenerate_hr_resolve_rerun_uses_snapshot_and_old_asset_not_left(self):
        """KP Human Review(M-3(b)導入後の等価検証)。旧: --regenerate-stage kp_b1bが選定を引き直し、gloss HRで停止して旧assetを置換した。
        新: --regenerate-stage kp_<lv>は『現在のreviewからの再finalize(再選定なし)』なので引き直しは起きない。選定の引き直しは
        reselect(新round)だけで、gloss HRの候補はAUTO対象外=確定物へ入らない。いずれの経路でも『旧glossが通る/HR itemが確定に混入する』ことはない。"""
        import er119_kp_human_review_01 as rv
        with tempfile.TemporaryDirectory() as tmp, sp.forbid_real_apis():
            calls: list = []
            fail_levels = []                                        # 可変: 最初はHRなし(旧=ON化前に相当する健全asset)
            r, ctx = sp.z_ctx(tmp, calls, fail_levels=fail_levels)
            with contextlib.redirect_stdout(io.StringIO()):
                r.run_stages(ctx, ["seed_check", "writer", "std_adjust", "plan", "support", "kp"])
            asset = f"{ctx.out_dir}/b1b/key_phrases/keywords_canonicalized.json"
            self.assertEqual(ga.collect_unresolved(json.load(open(asset, encoding="utf-8"))), [])
            self.assertEqual(calls, ["B1", "A2"])
            # (a) b1bを明示再生成: 再選定しない(kp_fnは呼ばれない)。確定物・assetは健全のまま
            fail_levels.append("B1")
            ctx.regenerate_stage = "kp_b1b"
            with contextlib.redirect_stdout(io.StringIO()):
                r.run_stage(ctx, "kp")
            self.assertEqual(calls, ["B1", "A2"])
            self.assertEqual(ga.collect_unresolved(json.load(open(asset, encoding="utf-8"))), [])
            # (b) 選定の引き直しはreselect(Human操作)。新round(宣言はround 1のみ有効=失効)に対し明示宣言し直すと、新しい候補に
            # gloss HRの候補(rank 2)が含まれるが、AUTO対象外=確定物に入らず、assetにgloss HR itemは残らない
            kp_dir = f"{ctx.out_dir}/key_phrases/b1b"
            rv.op_reselect(kp_dir, ng={}, note="gloss HR経路の確認", by="tester")
            rv.add_declaration(run_dirs=[ctx.out_dir], by="tester", reason="Human不在(round 2)", rounds=[2])
            with contextlib.redirect_stdout(io.StringIO()):
                try:
                    r.run_stage(ctx, "kp")
                except r._m().st.FamilyZProvenanceMismatchStop as e:   # 解説(kp_expl_b1b)は新署名で2段再生成が必要(既存仕様)
                    self.assertIn("kp_expl_b1b", str(e))
            self.assertEqual(calls, ["B1", "A2", "B1"])             # b1bだけ新roundで候補を引き直した
            cands = rv.load_candidates(kp_dir)
            hr = [c for c in cands["candidates"] if c["flags"]["gloss_hr_pending"]]
            self.assertTrue(hr and all(not c["auto_eligible"] for c in hr))
            inst = json.load(open(asset, encoding="utf-8"))
            self.assertEqual(ga.collect_unresolved(inst), [])
            self.assertNotIn(hr[0]["candidate_id"], [i["candidate_id"] for i in inst["items"]])
            # 消費側(TTS/Gate/Assembly共有入力)は、KP表現が変わったので旧Part 1(解説)を通さず止まる(既存の2段再生成の案内。HR itemは無関係)
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(r.FamilyZE2EStop) as cm:
                r.load_level_inputs(ctx, "b1b")
            self.assertIn("KP_PART1", str(cm.exception))

    def test_stage_kp_runs_preflight_first(self):
        with tempfile.TemporaryDirectory() as tmp, sp.forbid_real_apis():
            r, ctx = sp.z_ctx(tmp, [])
            with mock.patch.object(ga, "preflight", side_effect=ga.GlossRulesExtractionError("boom")) as pf:
                with self.assertRaises(ga.GlossRulesExtractionError):
                    r.stage_kp(ctx)
            self.assertEqual(pf.call_count, 1)


def _hr_artifact(d, status=None):
    os.makedirs(d, exist_ok=True)
    attempts = [{"attempt": n, "verdict": "INVALID", "reasons": ["qa!=PASS"], "proposed_gloss": "x"} for n in (1, 2)]
    doc = {"items": [dict(sp.ga_item(sp.ORIGINALS[1], "based on interviews"), gloss_alignment_status=status or ga.STATUS_HR_REQUIRED,
                          gloss_alignment={"original_japanese_gloss": "～をもとにした", "failure": {"attempts": attempts}})]}
    json.dump(doc, open(os.path.join(d, "keywords_canonicalized.json"), "w", encoding="utf-8"), ensure_ascii=False)
    return doc


class XFinalLineRcAndAssemble(_FlagOn):
    def test_final_line_is_artifact_based_and_not_stale_after_resolve(self):
        """OF-KGCPW-05: 報告書ファイルが残っていても、artifactのHRが解消済みなら最終行を出さない。"""
        with tempfile.TemporaryDirectory() as out:
            kp_dir = os.path.join(out, "a2", "key_phrases")
            _hr_artifact(kp_dir)
            open(os.path.join(kp_dir, ga.HR_REPORT_MD), "w", encoding="utf-8").write("stale report")
            with contextlib.redirect_stdout(io.StringIO()):
                line = x.print_gloss_hr_final_line(out)
            self.assertIn("[GLOSS-ALIGN][HUMAN-REVIEW-REQUIRED][FINAL]", line)
            self.assertEqual(x._gloss_hr_levels_from_artifacts(out), {"a2": [2]})
            ga.resolve_gloss(os.path.join(kp_dir, "keywords_canonicalized.json"), 2, "インタビューをもとにした", "tester")
            self.assertTrue(os.path.exists(os.path.join(kp_dir, ga.HR_REPORT_MD)))      # 報告書は履歴として残る
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(x.print_gloss_hr_final_line(out), "")
            self.assertEqual(x._gloss_hr_levels_from_artifacts(out), {})

    def _run_main(self, out, stage, assemble_a2, assemble_b1):
        argv = ["er019", "--slug", "kgcpw_slug", "--run", "r1", "--stage", stage, "--level", "both", "--out-dir", out]
        buf = io.StringIO()
        with mock.patch.object(sys, "argv", argv), \
                mock.patch.object(x, "derive_japanese_title", return_value={"japanese_title": "t", "source": "mock"}), \
                mock.patch.object(x.style_profile_mod, "resolve_run_profile", return_value=("default", "mock")), \
                mock.patch.object(x.style_profile_mod, "assert_profile_backend"), \
                mock.patch.object(x.cl, "install"), \
                mock.patch("er003_v1_en_direct_vfl_01_generate.get_client", return_value=object()), \
                mock.patch.object(x, "stage_assemble_family_x_a2", side_effect=assemble_a2), \
                mock.patch.object(x, "stage_assemble_family_x_b1", side_effect=assemble_b1), \
                mock.patch.object(x, "compute_cost_jpy_so_far", return_value=(0.0, {})), \
                mock.patch.object(x, "ensure_rf_record"), \
                mock.patch.object(x, "_require_part1_fresh_x", return_value={}), \
                mock.patch.object(x, "_require_part1_ja_fresh_x", return_value={}), \
                contextlib.redirect_stdout(buf):
            # 委任_14: 後段入口のPart 1(Vocabulary & Expressions)存在確認(Opus M2)は本testの関心(gloss HR)と直交するため無効化。
            # M2自体は er003_kp_general_explanation_01_runner_integration_test_01.py で検証する。
            try:
                x.main()
                rc, exc = 0, None
            except SystemExit as e:
                rc, exc = e.code, None
            except Exception as e:  # noqa: BLE001
                rc, exc = None, e
        return rc, exc, buf.getvalue()

    def test_assemble_catches_gloss_block_per_level_and_exits_2(self):
        """OF-KGCPW-19/04: a2がHRで止まってもb1b(健全)のassembleは続行。HR levelはBLOCKED記録。rc=2。最終行が出る。"""
        with tempfile.TemporaryDirectory() as out:
            _hr_artifact(os.path.join(out, "a2", "key_phrases"))
            b1_calls = []
            ok_doc = {"items": [sp.ga_item(sp.ORIGINALS[0], "right away")]}
            os.makedirs(os.path.join(out, "b1b", "key_phrases"))
            json.dump(ok_doc, open(os.path.join(out, "b1b", "key_phrases", "keywords_canonicalized.json"), "w", encoding="utf-8"))

            def a2(*a, **k):
                raise RuntimeError("EPISODE_BLOCKED_BY_GLOSS_ALIGNMENT: a2のepisode assemblyを中止しました。")

            def b1(*a, **k):
                b1_calls.append(1)
                return {"status": "OK"}
            rc, exc, stdout = self._run_main(out, "assemble", a2, b1)
            self.assertEqual((rc, exc), (2, None))
            self.assertEqual(len(b1_calls), 1)                                           # 健全levelは続行
            summ = json.load(open(os.path.join(out, "a2", "run_summary_assemble.json"), encoding="utf-8"))
            self.assertEqual(summ["status"], "EPISODE_BLOCKED_BY_GLOSS_ALIGNMENT")
            self.assertIn("[GLOSS-ALIGN][HUMAN-REVIEW-REQUIRED][FINAL]", stdout)
            self.assertIn("levels={'a2': [2]}", stdout)

    def test_final_line_printed_even_when_stage_raises_other_error(self):
        """OF-KGCPW-03: --stage all/assemble中に別例外で落ちても最終stdoutの1行(try/finally)が出る。"""
        with tempfile.TemporaryDirectory() as out:
            _hr_artifact(os.path.join(out, "a2", "key_phrases"))

            def a2(*a, **k):
                raise RuntimeError("some other failure")
            rc, exc, stdout = self._run_main(out, "assemble", a2, lambda *a, **k: {"status": "OK"})
            self.assertIsNone(rc)
            self.assertIn("some other failure", str(exc))
            self.assertIn("[GLOSS-ALIGN][HUMAN-REVIEW-REQUIRED][FINAL]", stdout)

    def test_no_hr_exits_normally(self):
        with tempfile.TemporaryDirectory() as out:
            rc, exc, stdout = self._run_main(out, "assemble", lambda *a, **k: {"status": "OK"}, lambda *a, **k: {"status": "OK"})
            self.assertEqual((rc, exc), (0, None))
            self.assertNotIn("[GLOSS-ALIGN][HUMAN-REVIEW-REQUIRED]", stdout)
            self.assertIn("実効flag=ON", stdout)                                          # OF-KGCPW-11: run開始時に実効値を出す
            ep = json.load(open(os.path.join(out, "entry_point.json"), encoding="utf-8"))
            self.assertEqual(ep["gloss_alignment_flag"]["enabled"], True)

    def test_flag_off_warning_printed_at_start(self):
        with tempfile.TemporaryDirectory() as out:
            ga.GLOSS_ALIGNMENT_ENABLED = False
            with mock.patch.object(ga, "_FLAG_RAW", "0"), mock.patch.object(ga, "_FLAG_SOURCE", "env"):
                rc, exc, stdout = self._run_main(out, "assemble", lambda *a, **k: {"status": "OK"}, lambda *a, **k: {"status": "OK"})
            self.assertIn("[GLOSS-ALIGN][WARN] DISABLED by EIGO_KP_GLOSS_ALIGNMENT=0", stdout)
            ep = json.load(open(os.path.join(out, "entry_point.json"), encoding="utf-8"))
            self.assertEqual((ep["gloss_alignment_flag"]["enabled"], ep["gloss_alignment_flag"]["raw"]), (False, "0"))


class NgReviewRequiredPlusHrBlocksX(_FlagOn):
    """OF-KGCPW-17: OPEN-359本体((b)(c))は実装しないが、gloss HR itemが同居するNG_REVIEW_REQUIREDでもXのTTS/assembleは止まり、
    summaryにgloss_alignment_run_statusが出る(artifact直読みの関所が戻り値statusに依存しないことの固定)。"""

    def test_ng_review_required_with_hr_item(self):
        import er003_v1_n3_01_scaffold_generate as sc
        with tempfile.TemporaryDirectory() as base, sp.forbid_real_apis():
            src = os.path.join(base, "src"); out = os.path.join(base, "out")
            os.makedirs(f"{src}/a2"); os.makedirs(f"{out}/a2")
            open(f"{src}/a2/article.md", "w", encoding="utf-8").write(
                "# T\n\nFirst paragraph here. It is fine.\n\nSecond paragraph here. It is fine.\n\nThird paragraph here. It is fine.\n\n## In one line\nA line.\n")
            json.dump({"comment_1": "x"}, open(f"{out}/a2/a2_support_texts.json", "w"))
            impl = {"selection": {"status": "KEY_WORDS_STRUCTURE_PASS"}, "canonicalization": None, "redundancy_qa": None,
                    "status": "NG_REVIEW_REQUIRED"}

            def real_run(article_text, kp_dir, article_id, level, **kw):
                _hr_artifact(kp_dir)       # 途中attemptのHR artifactがdiskに残っている
                with mock.patch.object(sc, "_run_key_phrases_impl", return_value=dict(impl)):
                    return sc_orig(article_text, kp_dir, article_id, level, **kw)
            sc_orig = sc.run_key_phrases
            with mock.patch.object(sc, "run_key_phrases", side_effect=real_run), contextlib.redirect_stdout(io.StringIO()):
                x.run_theme_scaffold(None, src, out, ["a2"], scaffold_only="kp", kp_backend="strategy_l")   # KPFT: 既定はfulltext_p2のため、_run_key_phrases_implを経由するA/B/C系backendで固定
            summ = json.load(open(f"{out}/scaffold_run_summary.json", encoding="utf-8"))["a2"]
            self.assertEqual(summ["kp_run_status"], "NG_REVIEW_REQUIRED")
            self.assertEqual(summ["gloss_alignment_run_status"], ga.STOPPED_STATUS)
            self.assertEqual(summ["gloss_alignment_human_review_events"][0]["ranks"], [2])
            kp = sp.load_kp(f"{out}/a2/key_phrases")
            narr = f"{out}/a2/narration"; os.makedirs(narr)
            with sp.x_stubs(x):
                results, delta = sp.stub_delta(lambda: x._generate_key_phrase_segments_a2(kp, narr, None))
            self.assertEqual(delta["tts"], 0)
            self.assertTrue(all(v["status"] == ga.STOPPED_STATUS for d_ in results.values() for v in d_.values()))
            with self.assertRaises(RuntimeError):
                x._assert_no_gloss_alignment_hr(f"{out}/a2", "A2")


class RunbookAndHistoricalScripts(unittest.TestCase):
    def test_runbook_exists_and_code_references_new_path(self):
        self.assertTrue(os.path.exists(os.path.join(REPO, ga.HR_RESOLVE_RUNBOOK)))
        self.assertEqual(ga.HR_RESOLVE_RUNBOOK, "docs/pm/runbooks/KP_GLOSS_ALIGNMENT_HR_RESOLVE_01.md")
        for f in ("er003_key_words_gloss_alignment.py", "er019_family_x_audio_production_runner_01.py",
                  "er026_family_z_fiction_production_runner_01.py", "er003_v1_n3_01_scaffold_generate.py"):
            self.assertNotIn("HR_RESOLVE_PROCEDURE_01", open(os.path.join(REPO, f), encoding="utf-8").read(), f)
        with tempfile.TemporaryDirectory() as d:
            ga.emit_human_review_notice(d, "A", "a2", {"items": [dict(sp.ga_item(sp.ORIGINALS[1], "based on interviews"),
                                                                   gloss_alignment_status=ga.STATUS_HR_REQUIRED,
                                                                   gloss_alignment={"failure": {"attempts": [
                                                                       {"attempt": 1, "reasons": ["r"]}]}})]},
                                        print_fn=lambda *_: None)
            self.assertIn("KP_GLOSS_ALIGNMENT_HR_RESOLVE_01.md", open(os.path.join(d, ga.HR_REPORT_MD), encoding="utf-8").read())

    def test_historical_trial_scripts_stop_before_any_api(self):
        scripts = ["er071_gloss_alignment_01_census.py", "er071_gloss_alignment_01_replay.py",
                   "er071_gloss_alignment_correction_01_offline_audit.py", "er071_gloss_alignment_correction_01_offline_audit_02.py",
                   "er071_gloss_alignment_correction_01_trial.py", "er071_completion_04_gloss_realign.py",
                   "er071_completion_04_gloss_census_replay.py"]
        env = {**os.environ, "OPENAI_API_KEY": "", "PYTHONUTF8": "1"}
        for s in scripts:
            p = subprocess.run([sys.executable, os.path.join(REPO, s)], capture_output=True, text=True, encoding="utf-8",
                               errors="replace", env=env, cwd=REPO, timeout=120)
            self.assertNotEqual(p.returncode, 0, s)
            self.assertIn("HISTORICAL", (p.stderr or "") + (p.stdout or ""), s)

    def test_removed_symbols_are_gone(self):
        for n in ("GLOSS_ALIGNMENT_MODE", "GLOSS_ALIGNMENT_MODES", "resolve_mode", "FALLBACK_KEEP_KP", "FALLBACK_REVERT_IF_SAFE",
                  "GLOSS_ALIGNMENT_FALLBACK_MODE", "SLOT_TOKENS", "kp_has_slot_word", "gloss_has_unjustified_slot",
                  "revert_to_candidate_allowed", "build_gloss_alignment_fallback_record", "write_failed_notice",
                  "format_failed_stdout", "validate_alignment_response", "run_alignment_gate", "apply_alignment",
                  "build_user_message", "GLOSS_ALIGNMENT_JSON_SCHEMA_CORRECTED", "_align_glosses_corrected",
                  "GLOSS_ALIGNMENT_NOTICE_FILENAME", "GLOSS_ALIGNMENT_MODE_CORRECTED", "GLOSS_ALIGNMENT_MODE_LEGACY"):
            self.assertFalse(hasattr(ga, n), n)
        r = __import__("er026_family_z_fiction_production_runner_01")
        self.assertFalse(hasattr(r.E2EContext(), "gloss_alignment_mode"))
        import inspect
        self.assertNotIn("gloss_alignment_mode", inspect.signature(x.run_theme_scaffold).parameters)


if __name__ == "__main__":
    unittest.main()
