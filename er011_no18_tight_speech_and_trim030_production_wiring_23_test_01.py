# ============================================================
# er011_no18_tight_speech_and_trim030_production_wiring_23_test_01.py
# ER-011-NO18-A2-TIGHT-SPEECH-AND-TRIM030-PRODUCTION-WIRING-23
# ============================================================
# ユーザー正式採用済みの下記2点を、量産Production仕様として恒久的に
# 固定するための回帰テスト。
#   A. A2 Production Assembly(load_a2_sources)がKey Phrase英語音声へ
#      tight_speech_only()による再cropを一切行わないこと
#   B. Key Phrase trim safety margin(0.30秒)のcache identityが、
#      旧0.20秒時代のMaster Audio Store資産を誤ってcache hitさせないこと
#   C. Primary/Fallback両方が同じKEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS
#      (0.30秒)を使うこと
#   D. B1側は元々tight_speech_only()を呼んでおらず、この変更で影響を
#      受けないこと(既存の無変更を回帰確認)
#   E. Key Phrase final-sound safeguard(語末が無音へ消えないこと)の
#      instruction文言がこの変更で失われていないこと

import inspect
import unittest

import numpy as np

import er003_v1_n3_01_assemble as asm
import er003_v1_repro01_main_generate as repro01
import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er006_master_audio_store_01 as store


class A2NoReCropTests(unittest.TestCase):
    """§A: A2 Production Assembly(初回・retry/reassembly/regenerationが
    すべて経由する唯一の関数load_a2_sources)のsource中に
    tight_speech_only()呼び出しが存在しないことを固定する。"""

    def test_load_a2_sources_source_has_no_tight_speech_only_call(self):
        # コメント中にtight_speech_only()への言及(経緯説明)が残るのは
        # 問題ないため、実際の呼び出し構文だけを対象にする。
        src = inspect.getsource(asm.load_a2_sources)
        self.assertNotIn("tight_speech_only(mono", src)
        self.assertNotIn("p7c.tight_speech_only(", src)

    def test_stage_assemble_a2_has_single_call_site_to_load_a2_sources(self):
        src = inspect.getsource(asm.stage_assemble_a2)
        self.assertEqual(src.count("load_a2_sources("), 1)

    def test_tight_speech_only_function_itself_still_defined(self):
        # 関数定義自体は他script参照があるため削除しない、という要件。
        self.assertTrue(hasattr(asm.p9a.p7c, "tight_speech_only"))
        self.assertTrue(callable(asm.p9a.p7c.tight_speech_only))


class B1UnaffectedRegressionTests(unittest.TestCase):
    """§D: B1側(load_b1_sources)は元々tight_speech_only()を呼んでおらず、
    今回の変更で影響を受けないことを確認する。"""

    def test_load_b1_sources_source_has_no_tight_speech_only_call(self):
        src = inspect.getsource(asm.load_b1_sources)
        self.assertNotIn("tight_speech_only(mono", src)
        self.assertNotIn("p7c.tight_speech_only(", src)


class PrimaryFallbackTrimMarginConsistencyTests(unittest.TestCase):
    """§C: Primary(Minimal)・Fallback(English Lock)両方が同一の
    KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS(0.30秒)をgeneration-timeへ
    明示的に渡していることを固定する。"""

    def test_constant_is_030(self):
        self.assertEqual(repro01.KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS, 0.30)

    def test_primary_and_fallback_both_pass_the_constant_explicitly(self):
        src = inspect.getsource(repro01.generate_key_phrase_component_verified)
        self.assertEqual(
            src.count("safety_margin_seconds=KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS"), 2,
            "Primary呼び出し・Fallback呼び出しの両方でKEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDSを"
            "明示的に渡していることを確認できませんでした")


class KeyPhraseFinalSoundSafeguardTests(unittest.TestCase):
    """§E: 語末が自然に発音される(無音へtrail offしない)ことを求める
    instruction文言が、この変更で失われていないことを確認する。"""

    def test_final_sound_safeguard_clause_present(self):
        self.assertIn(
            "not trailed off", repro01.KEY_PHRASE_MINIMAL_INSTRUCTION_CORE_TEXT)


class MasterAudioKeyTrimPolicyVersionTests(unittest.TestCase):
    """§B(前半): MasterAudioKeyの識別子(master_audio_id)に、Key Phrase
    trim policyのversionが含まれ、旧versionとは異なるIDになることを
    確認する(=同一textでも旧margin時代の資産とはcacheが分離される)。"""

    def _key(self, style_instruction_version: str) -> store.MasterAudioKey:
        return store.MasterAudioKey(
            language="en", speaker_voice="Aoede", tts_model_id=shared_narration.TTS_MODEL_EN,
            canonical_text="be powered off", level=None,
            style_instruction_id="key_phrase_english_component",
            style_instruction_version=style_instruction_version,
        )

    def test_new_policy_version_differs_from_old_v1(self):
        old_id = self._key("v1").master_audio_id()
        new_id = self._key(shared_narration.KEY_PHRASE_TRIM_POLICY_VERSION).master_audio_id()
        self.assertNotEqual(old_id, new_id)

    def test_ensure_key_phrase_english_component_uses_current_policy_version(self):
        src = inspect.getsource(shared_narration.ensure_key_phrase_english_component)
        self.assertIn("KEY_PHRASE_TRIM_POLICY_VERSION", src)
        self.assertNotIn('style_instruction_version="v1"', src)

    def test_policy_version_is_not_the_bare_generic_default(self):
        # 「trim marginが変わったのにversionを更新し忘れる」再発防止の
        # ための最低限のガード(既定"v1"のまま放置されていないこと)。
        self.assertNotEqual(shared_narration.KEY_PHRASE_TRIM_POLICY_VERSION, "v1")


class MasterAudioStoreStaleAssetNotReusedTests(unittest.TestCase):
    """§B(後半): 実際のstore.get_or_generate()(sandbox化したSTORE_DIR)を
    使い、旧version keyで保存済みのcache済み資産が、新version keyの
    リクエストに対して誤ってcache hit(reused=True)しないことを、実際の
    Production関数で確認する。"""

    def setUp(self):
        import tempfile
        self.tmp = tempfile.mkdtemp(prefix="er011_wiring23_store_test_")
        self._orig_store_dir = store.STORE_DIR
        self._orig_audio_dir = store.AUDIO_DIR
        self._orig_manifest_path = store.MANIFEST_PATH
        self._orig_telemetry_path = store.TELEMETRY_PATH
        store.STORE_DIR = self.tmp
        store.AUDIO_DIR = f"{self.tmp}/audio"
        store.MANIFEST_PATH = f"{self.tmp}/manifest.json"
        store.TELEMETRY_PATH = f"{self.tmp}/reuse_telemetry.jsonl"

    def tearDown(self):
        import shutil
        store.STORE_DIR = self._orig_store_dir
        store.AUDIO_DIR = self._orig_audio_dir
        store.MANIFEST_PATH = self._orig_manifest_path
        store.TELEMETRY_PATH = self._orig_telemetry_path
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _make_key(self, style_instruction_version: str) -> store.MasterAudioKey:
        return store.MasterAudioKey(
            language="en", speaker_voice="Aoede", tts_model_id="test-model",
            canonical_text="settle into a routine", level=None,
            style_instruction_id="key_phrase_english_component",
            style_instruction_version=style_instruction_version,
        )

    def _fake_generate(self, out_path):
        with open(out_path, "wb") as f:
            f.write(b"FAKE_WAV_BYTES")
        return {"status": "OK", "sha256": "fakehash", "asr_verified": True,
                "asr_text": "settle into a routine", "disfluency_checked": True,
                "disfluency_evidence": {"note": "test"}}

    def test_old_version_asset_is_not_reused_under_new_version_key(self):
        old_key = self._make_key("v1")
        out1 = f"{self.tmp}/old_out.wav"
        r1 = store.get_or_generate(old_key, out1, self._fake_generate)
        self.assertEqual(r1["reused"], False)
        self.assertEqual(r1["cache_miss_reason"], "no_existing_master")

        new_key = self._make_key("v2_margin030")
        out2 = f"{self.tmp}/new_out.wav"
        calls = {"n": 0}

        def counting_generate(out_path):
            calls["n"] += 1
            return self._fake_generate(out_path)

        r2 = store.get_or_generate(new_key, out2, counting_generate)
        self.assertEqual(r2["reused"], False,
            "旧versionのcache資産が、versionの異なる新規リクエストへ誤ってreuseされました")
        self.assertEqual(calls["n"], 1, "新versionでのcache missにより、generate_fnが実際に呼ばれるはずです")

    def test_same_version_key_does_reuse_cache_hit(self):
        # 対比: versionが同じであれば正しくcache hitすることも確認する
        # (今回の変更が過剰にcacheを無効化していないことの確認)。
        key_a = self._make_key("v2_margin030")
        out1 = f"{self.tmp}/a.wav"
        store.get_or_generate(key_a, out1, self._fake_generate)

        key_b = self._make_key("v2_margin030")
        out2 = f"{self.tmp}/b.wav"
        calls = {"n": 0}

        def counting_generate(out_path):
            calls["n"] += 1
            return self._fake_generate(out_path)

        r2 = store.get_or_generate(key_b, out2, counting_generate)
        self.assertEqual(r2["reused"], True)
        self.assertEqual(calls["n"], 0, "同一versionのcache hit時にgenerate_fnが呼ばれるべきではありません")


if __name__ == "__main__":
    unittest.main()
