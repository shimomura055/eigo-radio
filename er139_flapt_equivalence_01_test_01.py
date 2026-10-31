# -*- coding: utf-8 -*-
"""ASR-FLAP-T-PRODUCTION-WIRING-01 委任_02: Flap-T救済のProduction配線test(API 0・費用0)。
実行: .venv\\Scripts\\python.exe -m pytest er139_flapt_equivalence_01_test_01.py -q
構成: A 純規則(Trial 36 case移植+M1数字token) / B Voice表 / C 出自台帳(記録点・束縛・子登録・hydrate) / D adapter実経路(Primary/KP票/最終ANDゲート/
      Voice・scope・flagの各fail-closed) / E memo・audit形(Opus 4) / F Store再利用ガード / G 静的(AST)inventory / H A/B/C完全no-op。"""
from __future__ import annotations

import ast
import glob
import json
import os
import random
import re
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import er002_common as common
import er002_gemini_client as gclient
import er005_cost_logger as cost_logger
import er006_asr_provider_routing_01 as routing
import er006_batch_tts_wiring_01 as batch_wiring
import er006_secondary_asr_01 as sec
import er078_asr_unified_judge_01 as uj
import er078_reuse_value_guard_01 as rvg
import er103_proper_noun_alarm_policy_01 as pol
import er104_kp_three_asr_vote_01 as kp3v
import er109_xz_scope_01 as xz
import er139_flapt_equivalence_01 as fe
import er139_flapt_provenance_01 as prov

FL = "gemini-3.8-flash-lite-tts"
PRO = "gemini-2.5-pro-preview-tts"
R, N, X, NA = "RESCUE", "NO_RESCUE", "REQUIRES_EXTRA_EVIDENCE", "NOT_APPLICABLE"
CANON = "The latter option is cheaper."
ASRD = "The ladder option is cheaper."

# ---- A: Trial 36 case(ASR-FLAP-T-EQUIVALENCE-TRIAL-01 test と同一表。期待値は設計判断。N=NG維持[NO_RESCUE/NOT_APPLICABLE可]) ----
CASES = [
    ("P01", "latter", "Ladder", R), ("P02", "metal", "medal", R), ("P03", "betting", "bedding", R), ("P04", "atom", "Adam", R),
    ("P05", "waiting", "wading", R), ("P06", "coating", "coding", R), ("P07", "Bertie", "Birdie", R),
    ("P08", "The latter option is cheaper.", "The ladder option is cheaper.", R), ("P09", "ladder", "latter", R),
    ("P10", "bitter", "bidder", R), ("P11", "tutor", "Tudor", R), ("P12", "rated", "raided", R),
    ("N01", "ten", "den", N), ("N02", "time", "dime", N), ("N03", "putting", "pudding", N), ("N04", "heartbeat", "heartbead", N),
    ("N05", "eaten", "Eden", N), ("N06", "water", "wader", N), ("N07", "letter", "leader", N), ("N08", "battle", "paddle", N),
    ("N09", "party", "pardy", N), ("N10", "attack", "Adak", N), ("N17", "alter", "alder", N), ("N18", "Burton", "burden", N),
    ("N11", "feed", "feet", N), ("N12", "latter", "later", N),
    ("N13", "The latter option is cheaper.", "The ladder option is cheaper today.", NA),
    ("N14", "The latter option is cheaper.", "The ladder option is cheap.", N), ("N15", "total", "toad all", NA), ("N16", "metal", "mettle", N),
    ("X01", "writer", "rider", X), ("X02", "title", "tidal", X), ("X03", "Wright", "ride", N), ("U01", "Zorbo", "Zorpo", N),
]
_WAVS: list = []


def _mkwav(samples=2400, rate=24000, channels=1):
    p = os.path.join(tempfile.gettempdir(), f"flapt_prod_test_{random.random()}.wav")
    data = np.random.uniform(-0.1, 0.1, samples * (2 if channels == 2 else 1))
    common.write_wav_float(p, data, rate, channels)
    _WAVS.append(p)
    return p


def tearDownModule():
    for p in _WAVS:
        try:
            os.remove(p)
        except OSError:
            pass


class Base(unittest.TestCase):
    def setUp(self):
        self.assertIsNone(xz.current_scope(), "前のtestからscopeが漏れている")
        prov.reset_for_tests()
        prov.set_coverage_dir(tempfile.mkdtemp(prefix="flapt_cov_"))
        self._patches = [
            mock.patch.object(sec, "_resolve_unresolved_entity_for_review", lambda span: {"pronunciation_hint": "", "confidence": "unconfirmed", "sources": []}),
            mock.patch.object(sec, "_log_human_review", lambda d: None),
            mock.patch.object(sec.semantic_equivalence, "append_telemetry_log", lambda *a, **k: None),
            mock.patch.object(routing, "transcribe", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("Primary#2 forbidden"))),
        ]
        for p in self._patches:
            p.start()
        self.addCleanup(lambda: [p.stop() for p in reversed(self._patches)])
        self.addCleanup(lambda: prov.set_coverage_dir(None))

    def tearDown(self):
        self.assertIsNone(xz.current_scope(), "testがscopeを残した")

    def coverage_records(self):
        p = prov.coverage_path()
        if not os.path.exists(p):
            return []
        return [json.loads(x) for x in open(p, encoding="utf-8").read().splitlines() if x.strip()]

    # voice/modelを「TTS成功→wav書込み」で台帳に載せ、そのwavをEN adapterで判定する(本番と同じ連鎖)
    def adapter(self, canon, primary, azure=None, *, voice="Aoede", model=FL, scope="X", kp=False, whisper=None, seg="full_story_part1",
                bind=True, wav=None, slowdown_pct=None, actx_extra=None):
        az = azure if azure is not None else primary
        actx = {"slot": 1, "is_last_slot": True}
        if kp:
            actx["vote_required"] = True
            actx["vote_whisper_fn"] = lambda: kp3v.make_voter("whisper", canon, whisper if whisper is not None else primary, lang="en")
        actx.update(actx_extra or {})

        def go():
            w = wav
            if w is None:
                if bind and voice:
                    prov.note_tts_sent(voice, model)
                w = _mkwav()
                if slowdown_pct is not None:
                    import shutil
                    c = w + ".child.wav"
                    shutil.copyfile(w, c)
                    # 変換後wavのsha は別。apply_a2_slowdown 相当の登録を直接行う(ffmpeg不要)
                    with open(c, "ab") as f:
                        f.write(b"\x00\x00")
                    prov.register_child(w, c, {"kind": "atempo", "slowdown_pct": slowdown_pct})
                    _WAVS.append(c)
                    w = c
            with mock.patch.object(sec, "get_full_text_via_azure_stt_with_phrase_list", lambda w_, language="en-US", phrases=None, **kw: (az, None)):
                sec.reset_secondary_cache()
                return sec.evaluate_attempt_with_cascade_detail(canon, primary, [], w, language="en-US", cascade_enabled=True,
                                                                segment_id=(None if kp else seg), attempt_ctx=actx)
        if scope in ("X", "Y", "Z"):
            with pol.run_scope(scope), xz.run_scope(scope):
                return go()
        return go()


# ============================================================ A 純規則
class PureRules(unittest.TestCase):
    def test_trial_case_table(self):
        for cid, c, a, exp in CASES:
            with self.subTest(cid=cid):
                r = fe.evaluate(c, a)
                if exp == N:
                    self.assertIn(r.decision, (N, NA), (cid, r.decision, r.reason))
                else:
                    self.assertEqual(r.decision, exp, (cid, r.reason))

    def test_parity_with_trial_proto_except_m1(self):
        sys.path.insert(0, os.path.join(ROOT, "docs", "research", "ASR-FLAP-T-EQUIVALENCE-TRIAL-01", "tools"))
        import flapt_equivalence_proto_01 as proto
        for cid, c, a, _e in CASES:
            with self.subTest(cid=cid):
                self.assertEqual(proto.evaluate(c, a).decision, fe.evaluate(c, a).decision)

    def test_m1_numbers_and_symbols_block_rescue(self):
        for c, a in [("The latter 13 option", "The ladder 30 option"), ("I paid $13 for the latter", "I paid $30 for the ladder"),
                     ("At 3:15 the latter won", "At 3:30 the ladder won"), ("The latter 13 option", "The ladder thirteen option"),
                     ("The latter 50% option", "The ladder 30% option"), ("The 1st latter", "The 2nd ladder")]:
            with self.subTest(c=c):
                self.assertNotEqual(fe.evaluate(c, a).decision, R)

    def test_same_numbers_both_sides_still_rescue(self):
        self.assertEqual(fe.evaluate("The latter 13 option", "The ladder 13 option").decision, R)

    def test_number_and_negation_words_never_pair_rescue(self):
        self.assertNotEqual(fe.judge_pair("eighty", "eighdy").decision, R)
        with mock.patch.object(fe, "_negation_words", lambda w: True):
            self.assertEqual(fe.judge_pair("latter", "ladder").decision, N)

    def test_pure_cache_is_voice_independent(self):
        self.assertIs(fe.evaluate_cached("latter", "ladder"), fe.evaluate_cached("latter", "ladder"))
        self.assertEqual(fe.evaluate_cached.__wrapped__.__code__.co_argcount, 2)    # key=(canonical,text)のみ

    def test_cmu_dictionary_pinned(self):
        self.assertEqual(fe.cmu_info()["cmudict_dict_sha256"], fe.EXPECTED_CMU_DICT_SHA256)
        self.assertTrue(fe.cmu_matches())

    def test_cmu_sha_mismatch_declines_and_warns(self):
        with mock.patch.object(fe, "EXPECTED_CMU_DICT_SHA256", "0" * 64):
            fe.RUN_WARNINGS.clear()
            self.assertFalse(fe.cmu_matches())
            self.assertTrue(any(w["kind"] == "CMU_DICT_SHA_MISMATCH" for w in fe.RUN_WARNINGS))
        fe.RUN_WARNINGS.clear()


# ============================================================ B Voice表
class VoiceTable(unittest.TestCase):
    PLAN_FL = {"Aoede", "Charon", "Algieba", "Schedar", "Zephyr", "Puck", "Fenrir"}          # X/Y/Z flash-lite計画Voice
    PLAN_PRO = {"Algieba", "Schedar", "Fenrir", "Orus", "Puck", "Zephyr", "Kore", "Leda", "Sulafat", "Erinome", "Iapetus", "Charon", "Aoede"}

    def test_every_planned_voice_model_is_in_table_confirmed_or_explicit_false(self):
        for v in self.PLAN_FL:
            self.assertIsNotNone(fe.table_row(v, FL), f"{v}|fl が表に無い(新Voice追加で表更新漏れ)")
        for v in self.PLAN_PRO:
            self.assertIsNotNone(fe.table_row(v, PRO), f"{v}|pro が表に無い")

    def test_puck_pro_is_explicitly_unconfirmed_and_independent_probe_rows_confirmed(self):
        self.assertEqual(fe.table_status("Puck", PRO), "unconfirmed")
        for v in ("Zephyr", "Schedar"):
            self.assertEqual(fe.table_status(v, PRO), "confirmed")
            self.assertIn("voice_probe_03.json", fe.table_row(v, PRO)["evidence_ref"])     # 循環根拠(Bertie保存記録)ではなく独立probe

    def test_exact_key_match_only(self):
        for bad in (("aoede", FL), ("Aoede", "gemini-3.8-flash-lite"), ("Aoede", FL + "x"), ("Aoede ", FL), ("Kore", FL), (None, FL), ("Aoede", None)):
            self.assertEqual(fe.table_status(*bad), "not_in_table", bad)

    def test_table_sha_matches_file(self):
        import hashlib
        self.assertEqual(fe.voice_table()["sha256"], hashlib.sha256(open(fe.VOICE_TABLE_PATH, "rb").read()).hexdigest())

    def test_speed_conditions(self):
        row = fe.table_row("Charon", FL)                 # fast106_confirmed=False
        self.assertTrue(fe.speed_ok(row, [], True)[0])
        self.assertTrue(fe.speed_ok(row, [{"slowdown_pct": 6.0}], True)[0])
        self.assertFalse(fe.speed_ok(row, [{"slowdown_pct": -5.66037}], True)[0])
        self.assertFalse(fe.speed_ok(row, [{"slowdown_pct": 12.0}], True)[0])               # 未知pct
        self.assertFalse(fe.speed_ok(row, [], False)[0])                                    # 変換履歴不明は最も厳しい条件
        ok_row = fe.table_row("Aoede", FL)               # fast106_confirmed=True
        self.assertTrue(fe.speed_ok(ok_row, [{"slowdown_pct": -5.6603773}], True)[0])
        self.assertTrue(fe.speed_ok(ok_row, [], False)[0])


# ============================================================ C 出自台帳
class Provenance(Base):
    def test_note_bind_resolves_by_file_sha(self):
        with xz.run_scope("X"):
            prov.note_tts_sent("Aoede", FL)
            w = _mkwav()
            e = prov.resolve(prov.file_sha256(w))
            self.assertEqual((e["voice"], e["model_id"], e["transforms"]), ("Aoede", FL, []))

    def test_pending_consumed_once_and_overwritten_by_latest(self):
        with xz.run_scope("X"):
            prov.note_tts_sent("Charon", FL)
            prov.note_tts_sent("Fenrir", FL)                  # 後着上書き
            w1 = _mkwav()
            w2 = _mkwav()                                     # pendingは消費済み -> 束縛されない
            self.assertEqual(prov.resolve(prov.file_sha256(w1))["voice"], "Fenrir")
            self.assertIsNone(prov.resolve(prov.file_sha256(w2)))

    def test_stereo_and_non_24k_writes_do_not_bind_or_consume(self):
        with xz.run_scope("X"):
            prov.note_tts_sent("Aoede", FL)
            ws = _mkwav(channels=2)
            self.assertIsNone(prov.resolve(prov.file_sha256(ws)))
            w8 = _mkwav(rate=16000)
            self.assertIsNone(prov.resolve(prov.file_sha256(w8)))
            wm = _mkwav()                                     # mono 24kHzで初めて束縛(pendingは消費されていない)
            self.assertEqual(prov.resolve(prov.file_sha256(wm))["voice"], "Aoede")

    def test_pending_expires(self):
        with xz.run_scope("X"):
            prov.note_tts_sent("Aoede", FL)
            with mock.patch.object(prov, "PENDING_TTL_SECONDS", -1.0):
                w = _mkwav()
            self.assertIsNone(prov.resolve(prov.file_sha256(w)))

    def test_outside_scope_everything_is_noop(self):
        prov.note_tts_sent("Aoede", FL)
        self.assertIsNone(getattr(prov._TLS, "pending", None))
        w = _mkwav()
        self.assertIsNone(prov.resolve(prov.file_sha256(w)))
        self.assertEqual(len(prov._LEDGER), 0)

    def test_child_registration_keeps_voice_and_adds_transform(self):
        with xz.run_scope("Z"):
            prov.note_tts_sent("Fenrir", FL)
            parent = _mkwav()
            child = parent + ".c.wav"
            open(child, "wb").write(open(parent, "rb").read() + b"\x00\x00")
            _WAVS.append(child)
            prov.register_child(parent, child, {"kind": "atempo", "slowdown_pct": -5.66})
            e = prov.resolve(prov.file_sha256(child))
            self.assertEqual((e["voice"], e["transforms"][0]["slowdown_pct"], e["parent_sha256"]), ("Fenrir", -5.66, prov.file_sha256(parent)))
            prov.register_child(child + ".nonexistent", child + ".x", {"kind": "atempo", "slowdown_pct": 6.0})   # 親なし -> 何もしない

    def test_apply_a2_slowdown_registers_child_for_6pct_and_z_speedup(self):
        import er008_a2_postprocess_slowdown_01 as sd
        with xz.run_scope("Z"):
            for pct, voice in ((6.0, "Aoede"), (-5.66, "Fenrir")):
                prov.note_tts_sent(voice, FL)
                src = _mkwav(samples=24000)
                dst = src + f".{pct}.wav"
                _WAVS.append(dst)
                sd.apply_a2_slowdown(src, dst, pct)
                e = prov.resolve(prov.file_sha256(dst))
                self.assertEqual((e["voice"], e["transforms"][0]["slowdown_pct"]), (voice, pct))

    def test_hydrate_requires_sha_match_when_file_exists(self):
        with xz.run_scope("X"):
            w = _mkwav()
            self.assertFalse(prov.hydrate("0" * 64, "Aoede", FL, source="store_entry", wav_path=w))
            self.assertTrue(prov.hydrate(prov.file_sha256(w), "Aoede", FL, source="store_entry", wav_path=w))
            self.assertFalse(prov.hydrate("a" * 64, "", FL, source="store_entry"))

    def test_record_extraction_priority_and_unknown_transforms(self):
        sha, v, m, src, tr, known = prov.record_sha_and_provenance(
            {"sha256": "s1", "voice": "Aoede", "model": FL, "asr_judgement": {"audio_sha256": "s2", "tts_provenance": {
                "voice": "Charon", "model_id": FL, "transforms": [{"kind": "atempo", "slowdown_pct": 6.0}]}}})
        self.assertEqual((sha, v, src, known), ("s2", "Charon", "attempt_audit", True))
        sha, v, m, src, tr, known = prov.record_sha_and_provenance({"sha256": "s1", "voice": "Aoede", "model": FL})
        self.assertEqual((sha, v, src, known), ("s1", "Aoede", "store_entry", False))
        self.assertEqual(prov.record_sha_and_provenance({"sha256": "s1"})[1], None)         # 出自なし -> 適用外

    # ---- 記録点(SDK境界) ----
    def test_batch_record_success_notes_even_without_cost_logger(self):
        self.assertIsNone(getattr(cost_logger, "_LOG_PATH", None) if cost_logger._LOG_PATH is None else None)
        with mock.patch.object(cost_logger, "_LOG_PATH", None):
            with xz.run_scope("X"):
                batch_wiring._record("SUCCESS", FL, "Aoede", "job", "item_0", 1.0, None)
                self.assertEqual(prov._TLS.pending["voice"], "Aoede")
                prov._TLS.pending = None
                batch_wiring._record("API_ERROR", FL, "Aoede", "job", "item_0", 1.0, None)       # 失敗は記録しない
                self.assertIsNone(prov._TLS.pending)

    def _fake_batch_client(self, pcm_wav):
        part = SimpleNamespace(inline_data=SimpleNamespace(data=pcm_wav))
        resp = SimpleNamespace(error=None, response=SimpleNamespace(
            candidates=[SimpleNamespace(content=SimpleNamespace(parts=[part]))], usage_metadata=None))
        job = SimpleNamespace(name="job_1", state="JOB_STATE_SUCCEEDED", dest=SimpleNamespace(inlined_responses=[resp]))
        created = []

        class B:
            def create(self, model, src):
                created.append(model)
                return SimpleNamespace(name="job_1", state="JOB_STATE_PENDING")

            def get(self, name):
                return job
        return SimpleNamespace(batches=B()), created

    def test_er006_batch_call_fn_end_to_end_with_z_voice_override(self):
        pcm = np.zeros(2400, dtype=np.int16).tobytes()
        client, created = self._fake_batch_client(pcm)
        with mock.patch.dict(os.environ, {"TTS_EXECUTION_MODE": "BATCH"}), mock.patch.object(cost_logger, "_LOG_PATH", None):
            with xz.run_scope("Z"), gclient.voice_override("Algieba"):
                fn = batch_wiring.make_batch_tts_call_fn(PRO, "Aoede", client=client, poll_interval_seconds=0.001, timeout_seconds=2)
                fn("prompt")
                self.assertEqual((prov._TLS.pending["voice"], prov._TLS.pending["model_id"]), ("Algieba", PRO))   # Aoede既定ではなく実送信値
            self.assertEqual(created, [PRO])

    def test_er033_flash_lite_batch_call_fn_end_to_end(self):
        import er033_tts_flash_lite_backend_wiring_01 as flw
        wavb = common.pcm_to_wav_bytes(np.zeros(2400, dtype=np.int16).tobytes())
        client, created = self._fake_batch_client(wavb)
        with mock.patch.object(cost_logger, "_LOG_PATH", None):
            with xz.run_scope("X"):
                fn = flw.make_speech_metadata_batch_call_fn(FL, "Aoede", client=client, poll_interval_seconds=0.001, timeout_seconds=2)
                fn(("hello", None))
                self.assertEqual((prov._TLS.pending["voice"], prov._TLS.pending["model_id"]), ("Aoede", FL))

    def _fake_std_client(self, payload):
        part = SimpleNamespace(inline_data=SimpleNamespace(data=payload))
        resp = SimpleNamespace(candidates=[SimpleNamespace(content=SimpleNamespace(parts=[part]))])
        return SimpleNamespace(models=SimpleNamespace(generate_content=lambda **kw: resp))

    def test_standard_factories_note_after_success_without_cost_logger(self):
        import er003_b1_p7a_audio as p7a
        import er033_tts_flash_lite_backend_wiring_01 as flw
        pcm = np.zeros(2400, dtype=np.int16).tobytes()
        wavb = common.pcm_to_wav_bytes(pcm)
        with mock.patch.object(cost_logger, "_LOG_PATH", None), xz.run_scope("Z"):
            prov._TLS.pending = None
            gclient.make_tts_call_fn("Aoede", client=self._fake_std_client(pcm))("p")
            self.assertEqual((prov._TLS.pending["voice"], prov._TLS.pending["model_id"]), ("Aoede", common.MODEL_NAME))
            prov._TLS.pending = None
            with gclient.voice_override("Schedar"):
                p7a.make_tts_call_fn_for_model(PRO, "Aoede", client=self._fake_std_client(pcm))("p")
            self.assertEqual((prov._TLS.pending["voice"], prov._TLS.pending["model_id"]), ("Schedar", PRO))
            prov._TLS.pending = None
            flw.make_speech_metadata_call_fn(FL, "Charon", client=self._fake_std_client(wavb))(("hello", "style"))
            self.assertEqual((prov._TLS.pending["voice"], prov._TLS.pending["model_id"]), ("Charon", FL))

    def test_standard_failure_does_not_note(self):
        import er003_b1_p7a_audio as p7a
        with xz.run_scope("X"):
            prov._TLS.pending = None
            with self.assertRaises(RuntimeError):
                p7a.make_tts_call_fn_for_model(PRO, "Aoede", client=self._fake_std_client(b""))("p")
            self.assertIsNone(prov._TLS.pending)


# ============================================================ D adapter実経路
class AdapterIntegration(Base):
    def test_rescue_primary_pass_with_warning_and_audit(self):
        r = self.adapter(CANON, ASRD)
        aj = r["asr_judgement"]
        self.assertTrue(r["verified"])
        self.assertEqual(aj["state"], "PASS_WITH_WARNING")
        self.assertIn("FLAP_T_EQUIVALENT", aj["warnings"])
        self.assertEqual(aj["tts_provenance"]["voice"], "Aoede")
        site = aj["orthographic_equivalence"]["sites"][0]
        fl = site["er109"]["flapt"]
        for k in ("cmudict_dict_sha256", "voice_table_sha256", "voice", "model_id", "wav_sha256", "rules_version", "provenance_source"):
            self.assertTrue(fl.get(k), k)
        self.assertEqual(site["er109"]["spans"][0]["canon"], ["latter"])
        self.assertTrue(xz.ortho_contributed(aj) and xz.flapt_contributed(aj) and not xz.ukus_contributed(aj))

    def test_pass_with_warning_reaches_listening_registry(self):
        import er078_pass_with_warning_registry_01 as pww
        r = self.adapter(CANON, ASRD)
        self.assertIn("FLAP_T_EQUIVALENT", r["asr_judgement"]["warnings"])
        src = open(os.path.join(ROOT, "er078_pass_with_warning_registry_01.py"), encoding="utf-8").read()
        self.assertIn("warnings", src)     # registryは judgement.warnings から導出(ORTHO専用の登録先なし=汎用)

    def test_all_x_y_z_scopes_rescue(self):
        for sc in ("X", "Y", "Z"):
            with self.subTest(scope=sc):
                self.assertTrue(self.adapter(CANON, ASRD, scope=sc)["verified"])

    def test_not_rescued_without_provenance_logs_provenance_missing(self):
        r = self.adapter(CANON, ASRD, bind=False)
        self.assertFalse(r["verified"])
        self.assertEqual(r["asr_judgement"]["flapt_declined"][0]["reason"], "provenance_missing")

    def test_unconfirmed_and_unknown_voice_not_rescued(self):
        for voice, model in (("Puck", PRO), ("Kore", FL), ("Aoede", "gemini-2.5-flash-tts"), ("Nobody", FL)):
            with self.subTest(voice=voice, model=model):
                r = self.adapter(CANON, ASRD, voice=voice, model=model)
                self.assertFalse(r["verified"])
                self.assertEqual(r["asr_judgement"]["flapt_declined"][0]["reason"], "voice_unconfirmed")

    def test_independent_probe_pro_voices_rescued(self):
        for voice in ("Zephyr", "Schedar", "Algieba", "Charon", "Aoede", "Fenrir"):
            with self.subTest(voice=voice):
                self.assertTrue(self.adapter("Bertie, why?", "Birdie, why?", voice=voice, model=PRO)["verified"])

    def test_speed_conditions_through_adapter(self):
        self.assertTrue(self.adapter(CANON, ASRD, voice="Charon", slowdown_pct=6.0)["verified"])              # Std 6%減速: 確認済み
        self.assertFalse(self.adapter(CANON, ASRD, voice="Charon", slowdown_pct=-5.66)["verified"])           # Charon|fl は1.06x未probe
        self.assertTrue(self.adapter(CANON, ASRD, voice="Aoede", slowdown_pct=-5.66)["verified"])             # Aoede|fl は1.06x確認済み
        self.assertFalse(self.adapter(CANON, ASRD, voice="Aoede", slowdown_pct=33.0)["verified"])             # 未知pct

    def test_ay_aw_and_homograph_not_rescued(self):
        for c, a in (("The writer left.", "The rider left."), ("The title page.", "The tidal page.")):
            with self.subTest(c=c):
                self.assertFalse(self.adapter(c, a)["verified"])

    def test_value_and_negation_diff_never_unlocked_by_flap(self):
        r = self.adapter("The latter 13 option is cheaper.", "The ladder 30 option is cheaper.")
        self.assertFalse(r["verified"])
        self.assertIn(r["asr_judgement"]["state"], ("NG_PROTECTED", "NG_BOTH"))
        r = self.adapter("It is not the latter.", "It is the ladder.")
        self.assertFalse(r["verified"])

    def test_flag_off_and_scope_outside_are_conventional_ng(self):
        with mock.patch.object(fe, "FLAP_T_EQUIVALENCE_ENABLED", False):
            self.assertFalse(self.adapter(CANON, ASRD)["verified"])
        self.assertFalse(self.adapter(CANON, ASRD, scope=None)["verified"])
        import er109_asr_orthographic_equivalence_01 as e109
        with mock.patch.object(e109, "ORTHOGRAPHIC_EQUIVALENCE_ENABLED", False):        # 親flag rollbackでFlap-Tも停止(仕様)
            self.assertFalse(self.adapter(CANON, ASRD)["verified"])

    def test_normal_pass_and_ng_have_no_flapt_keys(self):
        r = self.adapter(CANON, CANON)
        aj = r["asr_judgement"]
        self.assertTrue(r["verified"])
        self.assertNotIn("flapt_declined", aj)
        self.assertNotIn(xz.AUDIT_KEY, aj)
        r = self.adapter(CANON, "Completely different words here.")
        self.assertNotIn("flapt_declined", r["asr_judgement"])
        self.assertFalse(xz.flapt_contributed(r["asr_judgement"]))

    def test_kp_vote_rescue_and_numbers_not_rescued(self):
        r = self.adapter("Pick the latter.", "Pick the ladder.", kp=True)
        self.assertTrue(r["verified"])
        self.assertIn("FLAP_T_EQUIVALENT", r["asr_judgement"]["warnings"])
        r = self.adapter("Pick the latter 13.", "Pick the ladder 30.", kp=True)
        self.assertFalse(r["verified"])

    def test_kp_vote_warning_survives_double_decision_calls(self):
        # make_voter が _classify と末尾で decision() を2回呼ぶ。2回目も同一結果(memo)で警告が消えない(I-10)
        r = self.adapter("Pick the latter.", "Pick the ladder.", kp=True)
        vote = r["asr_judgement"].get("vote") or {}
        self.assertTrue(any(vote.get(s, {}) and "FLAP_T_EQUIVALENT" in (vote[s].get("ortho_warnings") or []) for s in ("primary", "secondary", "whisper")) or
                        "FLAP_T_EQUIVALENT" in r["asr_judgement"]["warnings"])

    def test_secondary_transcript_also_rescued_by_flap(self):
        # Primary NG(別語) / Secondary がladder -> Secondary側でもFlap-T判定(同一基準)
        r = self.adapter(CANON, "The lemon option is cheaper.", azure=ASRD)
        self.assertTrue(r["verified"])
        self.assertIn("FLAP_T_EQUIVALENT", r["asr_judgement"]["warnings"])

    def test_sidecar_coverage_every_en_judgement_resolved(self):
        self.adapter(CANON, ASRD)
        self.adapter(CANON, ASRD, voice="Puck", model=PRO)
        recs = self.coverage_records()
        self.assertEqual(len(recs), 2)
        for rec in recs:
            self.assertTrue(rec["provenance_resolved"])
            self.assertTrue(rec["voice"] and rec["model_id"] and rec["source"])
        self.assertEqual(recs[0]["flap_candidates"][0]["outcome"], "rescued")
        self.assertEqual(recs[1]["flap_candidates"][0]["outcome"], "declined")
        self.assertEqual(recs[1]["table_status"], "unconfirmed")

    def test_sidecar_records_unresolved_for_missing_provenance(self):
        self.adapter(CANON, ASRD, bind=False)
        self.assertFalse(self.coverage_records()[0]["provenance_resolved"])

    def test_no_sidecar_or_ctx_outside_scope(self):
        self.adapter(CANON, ASRD, scope=None)
        self.assertEqual(self.coverage_records(), [])

    def test_ja_language_does_not_open_context(self):
        seen = []
        orig = prov.judging_wav
        fn = prov.adapter_context(lambda canonical_text, asr_text, prior_results, wav_path, language="en-US": "ok")
        w = _mkwav()
        with mock.patch.object(prov, "judging_wav", lambda sha, **kw: seen.append(sha) or orig(sha, **kw)):
            with pol.run_scope("X"), xz.run_scope("X"):
                self.assertEqual(fn("c", "a", [], w, language="ja-JP"), "ok")
                self.assertEqual(seen, [])
                self.assertEqual(fn("c", "a", [], w, language="en-US"), "ok")
                self.assertEqual(seen, [prov.file_sha256(w)])


# ============================================================ E memo / audit形
class MemoAndAudit(Base):
    def test_decide_memo_within_judging_wav_returns_identical_object_and_replays_notes(self):
        with xz.run_scope("X"):
            prov.note_tts_sent("Aoede", FL)
            w = _mkwav()
            sha = prov.file_sha256(w)
            with prov.judging_wav(sha):
                s1, s2 = {}, {}
                a = fe.decide(CANON, ASRD, s1)
                b = fe.decide(CANON, ASRD, s2)
                self.assertIs(a, b)
                self.assertEqual(len(prov.current_ctx()["cands"]), 1)       # 評価は1回
            prov.note_tts_sent("Puck", PRO)
            w2 = _mkwav()
            with prov.judging_wav(prov.file_sha256(w2)):
                s1, s2 = {}, {}
                self.assertIsNone(fe.decide(CANON, ASRD, s1))
                self.assertIsNone(fe.decide(CANON, ASRD, s2))
                self.assertEqual(s1["flapt_declined"], s2["flapt_declined"])   # memo hitでも不発火理由がsinkへ再転記される
                self.assertEqual(s1["flapt_declined"][0]["reason"], "voice_unconfirmed")

    def test_decide_without_context_is_provenance_missing(self):
        with xz.run_scope("X"):
            s = {}
            self.assertIsNone(fe.decide(CANON, ASRD, s))
            self.assertEqual(s["flapt_declined"][0]["reason"], "provenance_missing")

    def test_decision_called_twice_same_result_in_xz(self):
        with xz.run_scope("X"):
            prov.note_tts_sent("Aoede", FL)
            sha = prov.file_sha256(_mkwav())
            with prov.judging_wav(sha):
                d1, d2 = xz.decision(CANON, ASRD), xz.decision(CANON, ASRD)
                self.assertEqual(d1.warning_labels, ("FLAP_T_EQUIVALENT",))
                self.assertEqual(d1.warning_labels, d2.warning_labels)

    def test_flapeq_audit_shape_for_ukus_contributed_guard(self):
        with xz.run_scope("X"):
            prov.note_tts_sent("Aoede", FL)
            with prov.judging_wav(prov.file_sha256(_mkwav())):
                d = xz.decision(CANON, ASRD)
        a = d.eq.audit()
        self.assertIsInstance(a, dict)
        self.assertTrue(a["version"].startswith("er139_flapt_equivalence_v1+cmu"))
        self.assertEqual(a["rules"], ["flap_t_equivalence"])
        self.assertTrue(a["spans"])
        self.assertNotIn("ukus_pairs", a)
        self.assertFalse(hasattr(d.eq, "ukus_pairs"))
        aj = {"orthographic_equivalence": {"applied": True, "version": "er109_orthographic_equivalence_v2_ukus01",
                                            "sites": [{"site": "primary", "er109": a}], "warnings": ["FLAP_T_EQUIVALENT"]}}
        self.assertFalse(xz.ukus_contributed(aj))
        self.assertTrue(xz.flapt_contributed(aj))

    def test_explain_protected_never_unlocks_for_flap_decision(self):
        with xz.run_scope("X"):
            prov.note_tts_sent("Aoede", FL)
            with prov.judging_wav(prov.file_sha256(_mkwav())):
                d = xz.decision(CANON, ASRD)
        ex = xz.explain_protected(d, None, True, CANON, ASRD)
        self.assertFalse(ex.explained)
        self.assertEqual(ex.reason, "decision_not_equivalent_or_version_mismatch")

    def test_exception_inside_decide_is_fail_closed_with_sink(self):
        with xz.run_scope("X"):
            prov.note_tts_sent("Aoede", FL)
            with prov.judging_wav(prov.file_sha256(_mkwav())):
                with mock.patch.object(fe, "evaluate_cached", side_effect=RuntimeError("boom")):
                    s = {}
                    self.assertIsNone(fe.decide(CANON, ASRD, s))
                    self.assertIn("boom", s["orthographic_equivalence_errors"][0])


# ============================================================ F Store再利用ガード / hydrate
class ReuseAndHydrate(Base):
    def _entry_from_pass(self):
        r = self.adapter(CANON, ASRD)
        return {"asr_judgement": r["asr_judgement"], "text": CANON, "asr_text": ASRD, "sha256": r["asr_judgement"]["audio_sha256"],
                "voice": "Aoede", "model": FL}

    def test_reuse_valid_in_scope_and_blocked_when_table_changes_or_unconfirmed_or_flag_off(self):
        e = self._entry_from_pass()
        ok, why = fe.reuse_still_valid(e["asr_judgement"])
        self.assertTrue(ok, why)
        with mock.patch.object(fe, "table_row", lambda v, m: {"confirmed": False}):
            self.assertFalse(fe.reuse_still_valid(e["asr_judgement"])[0])
        with mock.patch.object(fe, "voice_table", lambda: {"sha256": "x" * 64, "rows": {}, "n_rows": 0}):
            self.assertEqual(fe.reuse_still_valid(e["asr_judgement"])[1], "voice_table_sha_changed")
        with mock.patch.object(fe, "FLAP_T_EQUIVALENCE_ENABLED", False):
            self.assertFalse(fe.reuse_still_valid(e["asr_judgement"])[0])
        self.assertFalse(fe.reuse_still_valid({"orthographic_equivalence": {"sites": []}})[0])     # audit読めない -> fail-closed

    def test_reuse_guard_blocks_outside_scope_and_with_unconfirmed_voice_inside(self):
        e = self._entry_from_pass()
        src = open(os.path.join(ROOT, "er078_reuse_value_guard_01.py"), encoding="utf-8").read()
        self.assertIn("flapt_contributed", src)
        self.assertIn("REUSE_BLOCK_REASON", src)
        self.assertTrue(xz.ortho_contributed(e["asr_judgement"]))      # scope外は既存のortho guardが先に止める

    def test_rejudge_with_current_judge_hydrates_from_store_entry_and_rescues(self):
        import er019_family_x_validation_inheritance_01 as vi
        sha = "f" * 64
        entry = {"text": CANON, "asr_text": ASRD, "sha256": sha, "voice": "Aoede", "model": FL}
        with mock.patch.object(vi, "is_japanese_label", lambda level, label: False):
            with pol.run_scope("X"), xz.run_scope("X"):
                rj = vi.rejudge_with_current_judge(entry, "b1b", "vocab_extra_3_en", force_lang="en")
            self.assertTrue(rj["ok"], rj)
            self.assertIn("FLAP_T_EQUIVALENT", rj["asr_judgement_inherited"]["warnings"])
            # 出自なしの保存音声は適用外(従来どおりNG)
            e2 = {"text": CANON, "asr_text": ASRD, "sha256": "e" * 64}
            with pol.run_scope("X"), xz.run_scope("X"):
                rj2 = vi.rejudge_with_current_judge(e2, "b1b", "vocab_extra_3_en", force_lang="en")
            self.assertFalse(rj2["ok"])
            # scope外(A/B/C)は従来どおりNG
            rj3 = vi.rejudge_with_current_judge(dict(entry), "b1b", "vocab_extra_3_en", force_lang="en")
            self.assertFalse(rj3["ok"])

    def test_rejudge_ja_entries_do_not_open_context_and_sidecar_has_phase(self):
        import er019_family_x_validation_inheritance_01 as vi
        seen = []
        orig = prov.judging_wav
        with mock.patch.object(prov, "judging_wav", lambda sha, **kw: seen.append((sha, kw.get("phase"))) or orig(sha, **kw)):
            with pol.run_scope("X"), xz.run_scope("X"):
                vi.rejudge_with_current_judge({"text": "こんにちは", "asr_text": "こんにちは", "sha256": "9" * 64}, "a2", "japanese_title", force_lang="ja")
                self.assertEqual(seen, [])
                vi.rejudge_with_current_judge({"text": CANON, "asr_text": ASRD, "sha256": "8" * 64, "voice": "Aoede", "model": FL}, "b1b", "x", force_lang="en")
        self.assertEqual(seen, [("8" * 64, "rejudge")])
        rec = self.coverage_records()[-1]
        self.assertEqual((rec["phase"], rec["tag"], rec["provenance_resolved"]), ("rejudge", "x", True))
        self.adapter(CANON, ASRD)
        self.assertEqual(self.coverage_records()[-1]["phase"], "generation")

    def test_store_entry_without_transform_history_speed_rule_by_level(self):
        """変換履歴を持たない保存entry: Std(a2)は高速化があり得ない=確認済み扱い、Adv(b1b)はfast106_confirmed未確認Voiceでは適用外(fail-closed)。"""
        import er019_family_x_validation_inheritance_01 as vi
        entry = {"text": "Bertie, why?", "asr_text": "Birdie, why?", "sha256": "6" * 64, "voice": "Zephyr", "model": PRO}      # Zephyr|pro: fast106_confirmed=False
        with mock.patch.object(vi, "is_japanese_label", lambda level, label: False):
            with pol.run_scope("Z"), xz.run_scope("Z"):
                self.assertTrue(vi.rejudge_with_current_judge(dict(entry), "a2", "full_story_part1_c14", force_lang="en")["ok"])
                self.assertFalse(vi.rejudge_with_current_judge(dict(entry), "b1b", "full_story_part1_c14", force_lang="en")["ok"])
                e2 = dict(entry, voice="Aoede", model=FL, sha256="5" * 64)                                                    # Aoede|fl: fast106_confirmed=True
                self.assertTrue(vi.rejudge_with_current_judge(e2, "b1b", "full_story_part1_c14", force_lang="en")["ok"])

    def test_kp_vote_reuse_ok_is_wrapped_and_hydrates_store_entry(self):
        import er104_kp_vote_reuse_01 as kvr
        self.assertTrue(getattr(kvr.kp_vote_reuse_ok, "__flapt_rejudge_context__", False))
        seen = {}

        @prov.rejudge_entry_context(lambda entry, *a, **kw: False)
        def fake(entry, *, label=""):
            seen["ctx"] = prov.current_ctx()
            seen["ent"] = prov.resolve("7" * 64)
        entry = {"sha256": "7" * 64, "voice": "Aoede", "model": FL}
        with xz.run_scope("X"):
            fake(entry, label="kp1_english")
            self.assertEqual((seen["ctx"]["sha"], seen["ctx"]["tag"], seen["ctx"]["phase"]), ("7" * 64, "kp1_english", "rejudge"))
            self.assertEqual((seen["ent"]["voice"], seen["ent"]["source"]), ("Aoede", "store_entry"))
        seen.clear()
        fake(entry, label="x")                  # scope外は素通し(文脈なし)
        self.assertIsNone(seen["ctx"])

    def test_rejudge_with_attempt_audit_provenance_known_transforms(self):
        import er019_family_x_validation_inheritance_01 as vi
        entry = {"text": CANON, "asr_text": ASRD, "sha256": "d" * 64,
                 "asr_judgement": {"audio_sha256": "d" * 64, "tts_provenance": {"voice": "Charon", "model_id": FL, "transforms": [{"kind": "atempo", "slowdown_pct": 6.0}]}}}
        with mock.patch.object(vi, "is_japanese_label", lambda level, label: False):
            with pol.run_scope("X"), xz.run_scope("X"):
                self.assertTrue(vi.rejudge_with_current_judge(entry, "b1b", "x", force_lang="en")["ok"])

    def test_hr_rejudge_entry_carries_voice_model(self):
        src = open(os.path.join(ROOT, "er109_hr_lock_rejudge_01.py"), encoding="utf-8").read()
        self.assertIn('"voice": att.get("voice")', src)
        self.assertIn("rejudge_context", src)


# ============================================================ G 静的(AST)
def _py(rel):
    return ast.parse(open(os.path.join(ROOT, rel), encoding="utf-8").read(), rel)


def _calls(tree, names):
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            f = n.func
            nm = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else None)
            if nm in names:
                out.append((nm, n.lineno))
    return out


def _func(tree, name):
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name:
            return n
    raise AssertionError(name)


def production_py_files():
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, "*.py"))):
        b = os.path.basename(p)
        if re.search(r"(_test|_trial|test_|_static_audit)", b) or b.startswith("er001") or b.startswith("tts_"):
            continue
        out.append(b)
    return out


class StaticInventory(unittest.TestCase):
    def test_flag_is_literal_true_and_single_reader(self):
        tree = _py("er139_flapt_equivalence_01.py")
        assigns = [n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "FLAP_T_EQUIVALENCE_ENABLED" for t in n.targets)]
        self.assertEqual(len(assigns), 1)
        self.assertIsInstance(assigns[0].value, ast.Constant)
        self.assertIs(assigns[0].value.value, True)
        for rel in ("er139_flapt_equivalence_01.py", "er139_flapt_provenance_01.py"):
            src = open(os.path.join(ROOT, rel), encoding="utf-8").read()
            self.assertNotIn("os.environ", src)
            self.assertNotIn("getenv", src)
        refs = [os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "*.py")) if "FLAP_T_EQUIVALENCE_ENABLED" in open(p, encoding="utf-8", errors="ignore").read()]
        self.assertEqual(sorted(b for b in refs if not b.endswith("_test_01.py")), ["er139_flapt_equivalence_01.py"])

    def test_no_launch_script_or_env_sets_flapt(self):
        for rel in glob.glob(os.path.join(ROOT, "*.bat")) + glob.glob(os.path.join(ROOT, "*.sh")) + glob.glob(os.path.join(ROOT, "*.ps1")) + glob.glob(os.path.join(ROOT, ".env*")):
            try:
                self.assertNotIn("FLAPT", open(rel, encoding="utf-8", errors="ignore").read().upper(), rel)
            except FileNotFoundError:
                pass

    def test_decide_is_called_only_from_er109_decision(self):
        callers = {}
        for b in production_py_files() + ["er139_flapt_provenance_01.py"]:
            if b == "er139_flapt_equivalence_01.py":
                continue
            try:
                tree = _py(b)
            except SyntaxError:
                continue
            hits = [(nm, ln) for nm, ln in _calls(tree, {"decide", "evaluate_cached", "judge_pair"}) if nm == "decide"]
            src = open(os.path.join(ROOT, b), encoding="utf-8", errors="ignore").read()
            if hits and "er139_flapt_equivalence_01" in src:
                callers[b] = hits
        self.assertEqual(list(callers), ["er109_xz_scope_01.py"], callers)
        self.assertEqual(len(callers["er109_xz_scope_01.py"]), 1)

    def test_note_tts_sent_inventory_exactly_the_four_record_points(self):
        found = {}
        for b in production_py_files() + ["er139_flapt_provenance_01.py"]:
            try:
                tree = _py(b)
            except SyntaxError:
                continue
            for nm, ln in _calls(tree, {"note_tts_sent", "_flapt_note"}):
                found.setdefault(b, []).append(nm)
        self.assertEqual(sorted(found), ["er002_gemini_client.py", "er003_b1_p7a_audio.py", "er006_batch_tts_wiring_01.py",
                                          "er033_tts_flash_lite_backend_wiring_01.py"], found)

    def test_every_audio_generate_content_and_batches_create_callsite_reaches_a_record_point(self):
        """Production moduleの batches.create( / AUDIO用 generate_content( 呼出点を全列挙し、各々が記録点へ到達することを固定する。
        新規に呼出点が増えたら(= 記録漏れの可能性)このtestが落ちる。"""
        sites = []
        for b in production_py_files():
            src = open(os.path.join(ROOT, b), encoding="utf-8", errors="ignore").read()
            if "batches.create(" not in src and "response_modalities" not in src:
                continue
            try:
                tree = ast.parse(src)
            except SyntaxError:
                continue
            if "runtime_evidence" in b:
                continue                       # DEV runtime-evidence script(Production経路ではない)
            for fn in [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
                seg = ast.get_source_segment(src, fn) or ""
                if re.search(r"batches\.create\(|generate_content\(", seg) and ("response_modalities" in seg or "batches.create(" in seg):
                    sites.append((b, fn.name))
        expected = {
            ("er002_gemini_client.py", "make_tts_call_fn"), ("er003_b1_p7a_audio.py", "make_tts_call_fn_for_model"),
            ("er006_batch_tts_wiring_01.py", "make_batch_tts_call_fn"), ("er006_batch_tts_wiring_01.py", "submit_batch_multi"),
            ("er033_tts_flash_lite_backend_wiring_01.py", "make_speech_metadata_call_fn"),
            ("er033_tts_flash_lite_backend_wiring_01.py", "make_speech_metadata_batch_call_fn"),
            ("er005_cost_logger.py", "_patch_gemini"),                   # SDK monkeypatch(記録のみ・呼出点ではない)
        }
        extra = {s for s in sites if s not in expected and s[0] != "er005_cost_logger.py"}
        # 許可リスト外のProduction音声TTS呼出点がある場合は、記録点を持つか個別に確認(ここで落ちたら記録点を追加するか、Production外であることを示す)
        legacy_non_xyz = {s for s in extra if re.match(r"er00[0-9]|er001", s[0])}
        extra -= legacy_non_xyz
        self.assertEqual(extra, set(), f"未登録のTTS呼出点(Flap-T出自の記録点が必要): {sorted(extra)}")

    def test_batch_callsites_reach_record_via__record_success_branch(self):
        t = _py("er006_batch_tts_wiring_01.py")
        rec = _func(t, "_record")
        first_if = next(n for n in rec.body if isinstance(n, ast.If))
        self.assertIn("SUCCESS", ast.dump(first_if.test))
        self.assertTrue(_calls(first_if, {"note_tts_sent"}))
        # cost logger未install即returnより前
        ret_idx = next(i for i, n in enumerate(rec.body) if isinstance(n, ast.If) and "cost_logger" in ast.dump(n.test))
        self.assertLess(rec.body.index(first_if), ret_idx)
        # make_batch_tts_call_fn(_resolve_single_item) と er033 batch の両方が SUCCESS を _record へ渡す
        self.assertTrue(any("SUCCESS" in ast.dump(c) for c in ast.walk(_func(t, "_resolve_single_item")) if isinstance(c, ast.Call)))
        t33 = _py("er033_tts_flash_lite_backend_wiring_01.py")
        self.assertTrue(any("SUCCESS" in ast.dump(c) for c in ast.walk(_func(t33, "make_speech_metadata_batch_call_fn")) if isinstance(c, ast.Call)))

    def test_submit_batch_multi_not_called_from_production(self):
        callers = []
        for b in production_py_files():
            if b == "er006_batch_tts_wiring_01.py":
                continue
            src = open(os.path.join(ROOT, b), encoding="utf-8", errors="ignore").read()
            if "submit_batch_multi" in src:
                callers.append(b)
        self.assertEqual(callers, [])         # 呼出が増えたら item単位記録が必要

    def test_standard_record_after_empty_check_and_independent_of_cost_logger(self):
        for rel, fn in (("er002_gemini_client.py", "make_tts_call_fn"), ("er003_b1_p7a_audio.py", "make_tts_call_fn_for_model"),
                        ("er033_tts_flash_lite_backend_wiring_01.py", "make_speech_metadata_call_fn")):
            src_ = open(os.path.join(ROOT, rel), encoding="utf-8").read()
            seg = ast.get_source_segment(src_, _func(_func(ast.parse(src_), fn), "tts_call_fn"))      # 戻り値のcall_fn本体(docstringを除く)
            self.assertIn("_flapt_note", seg, rel)
            self.assertNotIn("cost_logger", seg, rel)
            self.assertLess(seg.index("raise RuntimeError"), seg.index("_flapt_note"))     # 空音声(失敗)では記録しない

    def test_bind_point_is_write_wav_float_only_and_child_point_is_apply_a2_slowdown_only(self):
        found = {}
        for b in production_py_files() + ["er139_flapt_provenance_01.py"]:
            try:
                tree = _py(b)
            except SyntaxError:
                continue
            for nm, ln in _calls(tree, {"bind_pending", "register_child"}):
                found.setdefault(nm, set()).add(b)
        self.assertEqual(found.get("bind_pending"), {"er002_common.py"})
        self.assertEqual(found.get("register_child"), {"er008_a2_postprocess_slowdown_01.py"})

    def test_adapter_and_rejudge_decorators_applied(self):
        self.assertTrue(getattr(sec.evaluate_attempt_with_cascade_detail, "__flapt_adapter_context__", False))
        import er019_family_x_validation_inheritance_01 as vi
        self.assertTrue(getattr(vi.rejudge_with_current_judge, "__flapt_rejudge_context__", False))

    def test_hook_first_statement_returns_when_inactive(self):
        src = open(os.path.join(ROOT, "er139_flapt_provenance_01.py"), encoding="utf-8").read()
        for fn in ("note_tts_sent", "bind_pending", "register_child", "hydrate"):
            seg = ast.get_source_segment(src, _func(ast.parse(src), fn))
            self.assertIn("_active()", seg, fn)


# ============================================================ H Family A/B/C 完全no-op
class AbcNoop(Base):
    def test_no_scope_decision_is_none_and_ledger_untouched(self):
        prov.note_tts_sent("Aoede", FL)
        w = _mkwav()
        self.assertEqual(len(prov._LEDGER), 0)
        self.assertIsNone(xz.decision(CANON, ASRD))
        self.assertEqual(self.coverage_records(), [])

    def test_judgement_output_identical_outside_scope(self):
        r1 = self.adapter(CANON, ASRD, scope=None, bind=False)
        r2 = self.adapter(CANON, ASRD, scope=None, voice="Aoede")
        for r in (r1, r2):
            self.assertFalse(r["verified"])
            self.assertNotIn("tts_provenance", r["asr_judgement"])
            self.assertNotIn("flapt_declined", r["asr_judgement"])


if __name__ == "__main__":
    unittest.main()
