"""FAMILY-Z-MELOS-PROPER-NOUN-ASR-ROOT-CAUSE-01 委任_01 是正A のtest。
減速後再検証(apply_a2_slowdown_postprocess)へ、減速前と同じ共有Cascade
(Tier3 corroboration等、既承認)を配線したことの確認。有料API・ネットワーク
は使わない(Azure/OpenAI ASR/Ledger research/telemetry書込は全てmock)。"""
import hashlib
import os
import shutil
import tempfile
import unittest
from unittest import mock

import er003_v1_n3_01_tts_generate as tg
import er006_secondary_asr_01 as sec


# ============================================================
# 委任_15 W6(Opus R-C6): M1(複数発音候補、2026-10-13ユーザー承認 ASR-M1-OOV-MULTI-PRONUNCIATION-PRODUCTION-01)のON/OFF 2系統。
# 旧testはM1導入前(2026-10-12以前)の期待値で、かつPronunciation Ledgerの作業ツリー状態[er006_output/pronunciation_ledger_01/ledger.json
# の未commit追記]に依存して結果が変わった(再現性なし)。そこでLedgerを固定fixtureにし、M1 OFF(_m1_frozen_forを無効化)が既定、
# M1 ONは固定Ledger fixture(下記)を注入して明示的に検証する。監査: docs/research/FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01/M1_MELOS_SAID_AUDIT_01.md
# ============================================================
import contextlib as _contextlib

_REAL_M1_FROZEN_FOR = sec._m1_frozen_for
M1_LEDGER_FIXTURE = {
    "ec716e185835dba3": {   # 実Ledger(2026-10-12 Production cascadeのpronunciation research由来、ASR転写由来ではない)のMelos entry相当
        "surface": "melos", "entity_type": "cascade_unresolved_entity", "canonical_spelling": "Melos",
        "expected_pronunciation_ipa": "/ˈmiː.lɑːs/（米国英語の暫定候補）; /ˈmiː.lɒs/（英国英語）",
        "alternate_pronunciations": ["/ˈmɪlɒs/（英語での別読みとして提示される場合あり）",
                                     "/ˈmɛlɒs/ または /ˈmɛloʊs/（音楽用語・一般名詞としての英語の別読み）"],
        "confidence": "low", "sources": ["https://dictionary.cambridge.org/pronunciation/english/melos",
                                         "https://en.wiktionary.org/wiki/melos", "https://www.dictionary.com/browse/melos"],
        "updated_at": "2026-10-12T13:17:58"},
}


@_contextlib.contextmanager
def m1_on(ledger=None):
    """M1 ON: 固定Ledger fixtureを注入(作業ツリーのledger.jsonに依存しない)。ledger={}ならM1は有効だが候補なし(=OFF相当の結果)。"""
    sec._reset_m1_freeze_cache()
    with mock.patch.object(sec, "_m1_frozen_for", _REAL_M1_FROZEN_FOR), \
         mock.patch.object(sec.pronun_ledger, "_load", return_value=(M1_LEDGER_FIXTURE if ledger is None else ledger)):
        try:
            yield
        finally:
            sec._reset_m1_freeze_cache()


def _m1_off_setup_module():
    """既定=M1 OFF(旧testの期待値=M1導入前の承認済み境界)。"""
    patcher = mock.patch.object(sec, "_m1_frozen_for", return_value=None)
    patcher.start()
    unittest.addModuleCleanup(patcher.stop)


def _isolate_production_queue_paths():
    """HR-QUEUE-TEST-CONTAMINATION-FIX-01(2026-10-22): 本testはmock入力("Melos said."/"Mello said."/"Mellow said.")のまま実際の
    _log_human_review/attempt_historyを通るため、隔離しないとProductionのHuman Review queue
    (er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl)とer011_output/attempt_history.jsonlへmock行が追記される
    (er006_secondary_asr_01.py HUMAN_REVIEW_LOG_PATH / er011_human_review_lock_01.py ATTEMPT_HISTORY_PATH)。tmp配下へ差し替える。"""
    import er011_human_review_lock_01 as _lock
    d = tempfile.mkdtemp(prefix="er026_pscr_isolated_queue_")
    unittest.addModuleCleanup(shutil.rmtree, d, True)
    for patcher in (mock.patch.object(sec, "HUMAN_REVIEW_LOG_PATH", os.path.join(d, "human_review_queue.jsonl")),
                    mock.patch.object(_lock, "ATTEMPT_HISTORY_PATH", os.path.join(d, "attempt_history.jsonl"))):
        patcher.start()
        unittest.addModuleCleanup(patcher.stop)


def setUpModule():
    _isolate_production_queue_paths()
    _m1_off_setup_module()


class PostSlowdownCascadeRescueTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="er026_pscr_test_")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.name = "full_story_part1_c1"
        self.out = f"{self.tmp}/{self.name}.wav"
        with open(self.out, "wb") as f:
            f.write(b"PRE")

    def _fake_stretch(self, src, dst):
        with open(dst, "wb") as f:
            f.write(b"POST_STRETCHED")
        return {"src_duration_seconds": 2.0, "dst_duration_seconds": 2.12}

    def _run(self, canonical, primary_asr, azure_text, *, azure_err=None):
        """実classify_asr_match+実共有Cascadeを使い、ASR/Azure/Ledger research/telemetryだけをmockする。"""
        result = {"status": "OK", "sha256": None, "duration_seconds": 2.0}
        azure_calls = []

        def fake_azure(wav, language="en-US", phrases=None, timeout_seconds=90.0):
            azure_calls.append(phrases)
            return azure_text, azure_err

        with mock.patch.object(tg.a2_slowdown, "apply_a2_slowdown", side_effect=self._fake_stretch), \
             mock.patch.object(tg.routing, "transcribe", return_value=(primary_asr, None)), \
             mock.patch.object(sec.routing, "transcribe", return_value=(primary_asr, None)), \
             mock.patch.object(sec, "get_full_text_via_azure_stt_with_phrase_list", side_effect=fake_azure), \
             mock.patch.object(sec, "_resolve_unresolved_entity_for_review", return_value=None), \
             mock.patch.object(sec.semantic_equivalence, "append_telemetry_log"):
            out = tg.apply_a2_slowdown_postprocess(self.name, self.tmp, canonical, result)
        return out, azure_calls

    # --- 救済される正例(Melosの実事例と同型) ---
    def test_entity_only_uncertain_rescued_when_secondary_spells_canonical(self):
        out, calls = self._run("Melos called across the hall,", "Mellos called across the hall.",
                               "Melos called across the hall.")
        self.assertEqual(out["status"], "OK")
        self.assertTrue(out["post_slowdown_cascade_accepted"])
        self.assertEqual(out["post_slowdown_classification"], "ASR_VALIDATION_UNCERTAIN")
        self.assertTrue(out["post_slowdown_cascade"]["verified"])
        self.assertEqual(out["post_slowdown_cascade"]["final_status"], "SECONDARY_ASR_CORROBORATED_MATCH")
        self.assertTrue(calls)  # Azureが呼ばれた
        # sha256はNone許容(既存契約)のまま、asr_verified/asr_textは更新される
        self.assertTrue(out["asr_verified"])

    # --- 反例: 誤PASSしてはならない ---
    def test_no_rescue_when_secondary_also_misspells(self):
        # 実事例 b1b part1_c5: Azureも"Mellow"と聞く -> 救済しない(従来どおりSTOPPED)
        out, _ = self._run("Melos said.", "Mello said.", "Mellow said.")
        self.assertEqual(out["status"], "STOPPED")
        self.assertFalse(out.get("post_slowdown_cascade_accepted", False))
        self.assertFalse(out["asr_verified"])

    def test_no_rescue_when_secondary_fails(self):
        out, _ = self._run("Melos called across the hall,", "Mellos called across the hall.", None,
                           azure_err="boom")
        self.assertEqual(out["status"], "STOPPED")

    def test_no_rescue_for_artificially_replaced_different_name(self):
        # 人工置換: 別の実在固有名詞に置換された音声(Primary/Secondaryとも"Marcus")
        out, _ = self._run("Melos called across the hall,", "Marcus called across the hall.",
                           "Marcus called across the hall.")
        self.assertEqual(out["status"], "STOPPED")

    def test_no_rescue_for_content_word_error(self):
        # AUW 委任_05(J7、委任_03cの選択肢Aと同じ根拠=ユーザー原文L54「Primary NGなら不一致の種類によらず原則Secondary」・
        # L55「Secondary PASSならPASS_WITH_WARNING」に追随): 旧=非固有名詞の内容語誤り(TRUE_CONTENT_MISMATCH)はCascade対象外で
        # Azureを呼ばずSTOPPED。新=減速後wavにSecondaryを1回呼び、Secondaryが原稿全文を支持すればPASS_WITH_WARNING。
        # 独立証拠なし(Secondaryも同じ誤り)なら従来どおりSTOPPED(誤受理0の安全側は維持)。
        out, calls = self._run("He drank water slowly.", "He dropped water slowly.", "He drank water slowly.")
        self.assertEqual(out["status"], "OK")
        self.assertEqual(len(calls), 1)                                   # Secondary 1回のみ
        self.assertEqual(out["post_slowdown_classification"], "TRUE_CONTENT_MISMATCH")   # Primary層の判定は不変
        self.assertEqual(out["asr_judgement"]["state"], "PASS_WITH_WARNING")
        self.assertEqual(out["asr_judgement"]["reason_code"], "secondary_confirmed")
        out2, calls2 = self._run("He drank water slowly.", "He dropped water slowly.", "He dropped water slowly.")
        self.assertEqual(out2["status"], "STOPPED")
        self.assertEqual(len(calls2), 1)
        self.assertFalse(out2["asr_verified"])

    def test_no_rescue_for_number_error(self):
        out, calls = self._run("Melos waited three days.", "Melos waited five days.", "Melos waited three days.")
        self.assertEqual(out["status"], "STOPPED")
        self.assertEqual(calls, [])

    def test_exception_in_cascade_is_fail_closed(self):
        result = {"status": "OK", "sha256": None, "duration_seconds": 2.0}
        with mock.patch.object(tg.a2_slowdown, "apply_a2_slowdown", side_effect=self._fake_stretch), \
             mock.patch.object(tg.routing, "transcribe", return_value=("Mello said.", None)), \
             mock.patch.object(sec, "evaluate_attempt_with_cascade_detail", side_effect=RuntimeError("x")):
            out = tg.apply_a2_slowdown_postprocess(self.name, self.tmp, "Melos said.", result)
        self.assertEqual(out["status"], "STOPPED")
        self.assertIn("error", out["post_slowdown_cascade"])

    # --- 委任_03 改善(Opus任意改善) ---
    def test_exception_after_cascade_start_records_invoked_true(self):
        result = {"status": "OK", "sha256": None, "duration_seconds": 2.0}
        with mock.patch.object(tg.a2_slowdown, "apply_a2_slowdown", side_effect=self._fake_stretch),              mock.patch.object(tg.routing, "transcribe", return_value=("Mello said.", None)),              mock.patch.object(sec, "evaluate_attempt_with_cascade_detail", side_effect=ConnectionError("net")):
            out = tg.apply_a2_slowdown_postprocess(self.name, self.tmp, "Melos said.", result)
        pc = out["post_slowdown_cascade"]
        self.assertEqual(out["status"], "STOPPED")
        self.assertTrue(pc["invoked"])
        self.assertTrue(pc["aborted_by_exception"])

    def test_cost_logger_misconfiguration_is_not_swallowed(self):
        result = {"status": "OK", "sha256": None, "duration_seconds": 2.0}
        with mock.patch.object(tg.a2_slowdown, "apply_a2_slowdown", side_effect=self._fake_stretch),              mock.patch.object(tg.routing, "transcribe", return_value=("Mello said.", None)),              mock.patch.object(sec, "evaluate_attempt_with_cascade_detail",
                               side_effect=RuntimeError("init_logger()が呼ばれていません")):
            with self.assertRaises(RuntimeError):
                tg.apply_a2_slowdown_postprocess(self.name, self.tmp, "Melos said.", result)

    def test_final_classification_top_level_field(self):
        out, _ = self._run("Melos called across the hall,", "Mellos called across the hall.",
                           "Melos called across the hall.")
        self.assertEqual(out["post_slowdown_final_classification"], "SECONDARY_ASR_CORROBORATED_MATCH")
        out2, _ = self._run("Melos said.", "Mello said.", "Mellow said.")
        self.assertEqual(out2["post_slowdown_final_classification"], "ASR_VALIDATION_UNCERTAIN")
        out3, _ = self._run("Melos called across the hall,", "Melos called across the hall.", None)
        self.assertNotEqual(out3["post_slowdown_final_classification"], "")
        self.assertIn("post_slowdown_final_classification", out3)

    def test_primary2_single_pass_rescues_after_tier3_no_corroboration(self):
        # AUW 委任_03b: DESIGN_01 §4-9 / ユーザー原文「Primary NG→原則Secondary」「同じ音声に対するSecondaryの重複API呼び出しを防ぐ」に追随
        # (旧: Tier3 corroboration無しの後、Primary#2(同音声のOpenAI再転写)が正規綴りで単発PASSして救済 -> step末尾="primary_2")。
        # 新設計: Primary#2は廃止。Tier3(Azure)とjudgeのSecondaryは同一wavのAzure結果を共有(1回)。Secondary("Mellow")も
        # 正規綴りでなければ救済しない(独立証拠なしに受理しない=誤受理0の安全側は維持)。
        result = {"status": "OK", "sha256": None, "duration_seconds": 2.0}
        azure_calls = []
        primary_calls = []
        # (tg.routing と sec.routing は同一module。1回のpatchで足りる。Primary#2が呼ばれればprimary_callsが2以上になる)
        with mock.patch.object(tg.a2_slowdown, "apply_a2_slowdown", side_effect=self._fake_stretch),              mock.patch.object(tg.routing, "transcribe",
                               side_effect=lambda *a, **k: primary_calls.append(1) or ("Mellos called across the hall.", None)),              mock.patch.object(sec, "get_full_text_via_azure_stt_with_phrase_list",
                               side_effect=lambda *a, **k: azure_calls.append(1) or ("Mellow called across the hall.", None)),              mock.patch.object(sec, "_resolve_unresolved_entity_for_review", return_value=None),              mock.patch.object(sec.pronun_ledger, "_load", return_value={}),              mock.patch.object(sec.semantic_equivalence, "append_telemetry_log"):
            # (_load={}: M1がledger.json(未commitの作業ツリー差分に依存して揺れる)の"melos"エントリで受理しないよう空ledgerに固定する)
            out = tg.apply_a2_slowdown_postprocess(self.name, self.tmp, "Melos called across the hall,", result)
        self.assertEqual(out["status"], "STOPPED")
        self.assertFalse(out.get("post_slowdown_cascade_accepted", False))
        self.assertEqual(len(primary_calls), 1, "Primary 1回のみ(Primary#2=同音声のOpenAI再転写は廃止)")
        steps = [s["step"] for s in out["post_slowdown_cascade"]["steps"]]
        self.assertNotIn("primary_2", steps)
        self.assertEqual(len(azure_calls), 1, "Tier3とjudgeのSecondaryでAzureは同一wavにつき1回(重複呼出なし)")

    def test_cmu_case_a_homophone_name_rescued_without_extra_asr(self):
        # CMU辞書上の発音完全一致(Kristie/Christy)はPrimary#1の時点で追加ASRなしにPASS(Case A)
        out, calls = self._run("Kristie called across the hall,", "Christy called across the hall.", None)
        self.assertEqual(out["status"], "OK")
        # AUW 委任_05(J7): 統一judgeのEN adapterは他leafと同順序(Tier3 corroboration[Azure,共有cache]→CMU Case A)。減速後wavへの
        # Azureは最大1回(Tier3の試行のみ。Secondaryとして再呼出しない)。Case Aの受理判定自体は不変。
        self.assertLessEqual(len(calls), 1)
        self.assertTrue(out["post_slowdown_homophone_accepted"])
        self.assertIn(out["post_slowdown_final_classification"],
                      ("PROPER_NOUN_ENTITY_ARPABET_CONFIRMED", "HOMOPHONE_EQUIVALENT"))

    # --- 既存挙動の維持 ---
    def test_primary_pass_does_not_invoke_cascade(self):
        out, calls = self._run("Melos called across the hall,", "Melos called across the hall.", None)
        self.assertEqual(out["status"], "OK")
        self.assertEqual(calls, [])
        self.assertNotIn("post_slowdown_cascade", out)

    def test_cascade_disabled_flag_keeps_old_behavior(self):
        with mock.patch.object(sec, "FEATURE_FLAG_SECONDARY_ASR_ENABLED", False):
            out, calls = self._run("Melos called across the hall,", "Mellos called across the hall.",
                                   "Melos called across the hall.")
        self.assertEqual(out["status"], "STOPPED")
        self.assertEqual(calls, [])

    # --- 委任_15 W6: M1 ON系統(固定Ledger fixture)。上のM1 OFF系統(既定)と対で期待値を固定する ---
    def test_m1_on_melos_said_accepted_via_ledger_candidate_not_asr_derived(self):
        """Primary=Mello / Azure=Mellow: 実Ledger由来のC2候補[melos ~ M EH L OW S、drop_final_S+次語頭S融合]でM1が受理する(PASS_WITH_WARNING)。"""
        with m1_on():
            out, calls = self._run("Melos said.", "Mello said.", "Mellow said.")
        self.assertEqual(out["status"], "OK")
        self.assertTrue(out["post_slowdown_cascade_accepted"])
        self.assertEqual(out["post_slowdown_final_classification"], "M1_MULTI_CANDIDATE_ACCEPT")
        dump = repr(out["post_slowdown_cascade"])
        self.assertIn("ec716e185835dba3", dump)       # 受理に使われたLedger entry(監査でledger_key別に事後集計可能)
        self.assertIn("C2_ledger_alt", dump)

    def test_m1_on_with_empty_ledger_is_same_as_off_stopped(self):
        with m1_on(ledger={}):
            out, _ = self._run("Melos said.", "Mello said.", "Mellow said.")
        self.assertEqual(out["status"], "STOPPED")
        self.assertEqual(out["post_slowdown_final_classification"], "ASR_VALIDATION_UNCERTAIN")


class OuterLoopIntegrationTests(unittest.TestCase):
    """generate_a2_segment_with_slowdown全体: 救済されれば1回のTTS生成で完了し、取り直しが発生しない。"""

    def _run(self, name, canonical, primary, azure, dur):
        tmp = tempfile.mkdtemp(prefix="er026_pscr_outer_")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        out = f"{tmp}/{name}.wav"
        with open(out, "wb") as f:
            f.write(b"PRE")
        calls = {"tts": 0}

        def fake_inner(*a, **k):
            calls["tts"] += 1
            return {"status": "OK", "sha256": None, "duration_seconds": dur, "standard_attempts_log": [{}]}

        def fake_stretch(src, dst):
            with open(dst, "wb") as f:
                f.write(b"POST")
            return {"src_duration_seconds": dur, "dst_duration_seconds": dur * 1.06}

        with mock.patch.object(tg.c, "generate_english_segment_with_fallback", side_effect=fake_inner),              mock.patch.object(tg.a2_slowdown, "apply_a2_slowdown", side_effect=fake_stretch),              mock.patch.object(tg.routing, "transcribe", return_value=(primary, None)),              mock.patch.object(sec.routing, "transcribe", return_value=(primary, None)),              mock.patch.object(sec, "get_full_text_via_azure_stt_with_phrase_list", return_value=(azure, None)),              mock.patch.object(sec, "_resolve_unresolved_entity_for_review", return_value=None),              mock.patch.object(sec.semantic_equivalence, "append_telemetry_log"),              mock.patch.object(tg.review_lock, "append_attempt_history_event") as hist:
            r = tg.generate_a2_segment_with_slowdown(canonical, out, canonical.split()[0])
        return r, calls, hist

    def test_rescue_prevents_regeneration_and_logs_cascade(self):
        r, calls, hist = self._run("full_story_part1_c1", "Melos called across the hall,",
                                   "Mellos called across the hall.", "Melos called across the hall.", 2.0)
        self.assertEqual(r["status"], "OK")
        self.assertEqual(calls["tts"], 1)
        self.assertEqual(r["tts_generations_used"], 1)
        ev = hist.call_args[0][2]
        self.assertEqual(ev["post_slowdown_cascade"]["final_status"], "SECONDARY_ASR_CORROBORATED_MATCH")

    def test_no_rescue_consumes_budget_as_before(self):
        r, calls, _ = self._run("full_story_part1_c5", "Melos said.", "Mello said.", "Mellow said.", 1.5)
        self.assertEqual(r["status"], "STOPPED")
        self.assertEqual(calls["tts"], 3)            # 既存の通算3回上限(OPEN-270是正)は不変
        self.assertTrue(r["tts_generation_cap_reached"])

    def test_m1_on_melos_said_does_not_consume_regeneration_budget(self):
        with m1_on():
            r, calls, _ = self._run("full_story_part1_c5", "Melos said.", "Mello said.", "Mellow said.", 1.5)
        self.assertEqual(r["status"], "OK")
        self.assertEqual(calls["tts"], 1)


class ProductionQueueIsolationTests(unittest.TestCase):
    """隔離の検証: 本moduleのmock実行がProductionのHR queue/attempt_historyを1バイトも変えない(行数・sha256不変)。"""
    PROD = ("er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl", "er011_output/attempt_history.jsonl")

    @staticmethod
    def _snap(path):
        if not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            b = f.read()
        return (b.count(b"\n"), hashlib.sha256(b).hexdigest())

    def test_module_paths_are_redirected_away_from_production(self):
        import er011_human_review_lock_01 as lock
        self.assertNotEqual(os.path.abspath(sec.HUMAN_REVIEW_LOG_PATH), os.path.abspath(self.PROD[0]))
        self.assertNotEqual(os.path.abspath(lock.ATTEMPT_HISTORY_PATH), os.path.abspath(self.PROD[1]))

    def test_stopped_flow_writes_isolated_queue_and_leaves_production_unchanged(self):
        before = [self._snap(p) for p in self.PROD]
        outer = OuterLoopIntegrationTests("test_no_rescue_consumes_budget_as_before")
        outer.addCleanup = self.addCleanup
        r, calls, _ = outer._run("full_story_part1_c5", "Melos said.", "Mello said.", "Mellow said.", 1.5)
        self.assertEqual(r["status"], "STOPPED")
        self.assertTrue(os.path.exists(sec.HUMAN_REVIEW_LOG_PATH), "STOPPED経路は隔離先queueへ書かれる(=実際にwriterを通った証拠)")
        self.assertEqual([self._snap(p) for p in self.PROD], before)


if __name__ == "__main__":
    unittest.main()
