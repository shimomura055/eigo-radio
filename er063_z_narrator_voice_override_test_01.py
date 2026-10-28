# -*- coding: utf-8 -*-
"""FZ-TELL-TALE-HEART-NARRATOR-VOICE-01 委任_03: Z Narrator Voice(ClipSpec.voice)が共有leafの『API送信speech_config』へ届くことのtest(API 0)。
「コード上の設定」ではなく、genai client.models.generate_content / batches.create へ渡る実requestのvoice_nameを捕捉して検証する。"""
import unittest
from types import SimpleNamespace
from unittest import mock

import er002_gemini_client as gclient
import er003_b1_p9a_audio as p9a
import er006_batch_tts_wiring_01 as bw
import er033_tts_flash_lite_backend_wiring_01 as flw
import er063_family_z_audio_01 as z


class FakeModels:
    def __init__(self, log):
        self.log = log

    def generate_content(self, model=None, contents=None, config=None):
        sc = config.speech_config
        self.log.append(sc.voice_config.prebuilt_voice_config.voice_name)
        part = SimpleNamespace(inline_data=SimpleNamespace(data=b"\x00\x01" * 100))
        return SimpleNamespace(candidates=[SimpleNamespace(content=SimpleNamespace(parts=[part]))])


class FakeClient:
    def __init__(self):
        self.sent = []
        self.models = FakeModels(self.sent)


def sent_voice_via_standard(voice_name):
    c = FakeClient()
    gclient.make_tts_call_fn(voice_name, client=c)("hello")
    return c.sent


class T(unittest.TestCase):
    # (a) Z narrator spec.voice=Fenrir が実requestのvoice名へ到達
    def test_a_override_reaches_request(self):
        with gclient.voice_override("Fenrir"):
            self.assertEqual(sent_voice_via_standard(p9a.VOICE_NAME), ["Fenrir"])
            c = FakeClient()
            with mock.patch.dict("os.environ", {"TTS_EXECUTION_MODE": "STANDARD"}):
                bw.make_batch_tts_call_fn(p9a.ENGLISH_MODEL_NAME, p9a.VOICE_NAME, client=c)("hello")
            self.assertEqual(c.sent, ["Fenrir"])
            c2 = FakeClient()
            import er003_b1_p7a_audio as p7a
            p7a.make_tts_call_fn_for_model(p9a.ENGLISH_MODEL_NAME, p9a.VOICE_NAME, client=c2)("hello")
            self.assertEqual(c2.sent, ["Fenrir"])

    def test_a2_speech_metadata_factories_voice(self):
        # flash-liteのspeech_metadata factory(Z本番backend)の送信speech_config voice(Standard同期)
        c = FakeClient()
        with mock.patch.object(flw, "assert_sdk_supports_speech_metadata", lambda: None), \
             mock.patch.object(flw.routing_contract, "require_model", lambda p, m: m), \
             gclient.voice_override("Fenrir"):
            fn = flw.make_speech_metadata_call_fn("m", p9a.VOICE_NAME, client=c)
        # factory生成時にvoiceが確定する(scope外で呼んでも確定済み=attempt途中でscopeが切れても同じVoice)
        import inspect
        self.assertIn("Fenrir", [cell.cell_contents for cell in fn.__closure__ if isinstance(cell.cell_contents, str)])

    def test_a3_batch_request_voice(self):
        # Batch経路: er006 make_batch_tts_call_fn は speech_config(build_speech_config)をfactory時点で確定
        captured = {}
        orig = gclient.build_speech_config
        def spy(v):
            sc = orig(v)
            captured["v"] = sc.voice_config.prebuilt_voice_config.voice_name
            return sc
        with mock.patch.object(gclient, "build_speech_config", spy), gclient.voice_override("Fenrir"):
            bw.make_batch_tts_call_fn(p9a.ENGLISH_MODEL_NAME, p9a.VOICE_NAME, client=object())
        self.assertEqual(captured["v"], "Fenrir")

    # (b) スコープ外(X/A/B/C既存呼出)はVOICE_NAME不変。他Voice(Charon/Algieba)はscope内でも不変
    def test_b_default_unchanged_outside_scope(self):
        self.assertEqual(sent_voice_via_standard(p9a.VOICE_NAME), ["Aoede"])
        self.assertEqual(gclient.effective_voice("Aoede"), "Aoede")
        with gclient.voice_override("Fenrir"):
            self.assertEqual(sent_voice_via_standard("Charon"), ["Charon"])
            self.assertEqual(sent_voice_via_standard("Algieba"), ["Algieba"])
        self.assertEqual(sent_voice_via_standard(p9a.VOICE_NAME), ["Aoede"])   # scope終了後に残留しない
        with gclient.voice_override(None):
            self.assertEqual(sent_voice_via_standard(p9a.VOICE_NAME), ["Aoede"])
        with gclient.voice_override("Aoede"):
            self.assertEqual(sent_voice_via_standard(p9a.VOICE_NAME), ["Aoede"])

    def test_b2_no_flag_or_env_can_enable(self):
        with mock.patch.dict("os.environ", {"VOICE_OVERRIDE": "Fenrir", "NARRATOR_VOICE": "Fenrir"}):
            self.assertEqual(sent_voice_via_standard(p9a.VOICE_NAME), ["Aoede"])

    # (c) Z narrator(): retry/fallback/LR/resumeの全attemptが同一scope=同一Voice。leaf mockが各attemptでrequestを組む
    def _run_narrator(self, level, voice, attempts=5):
        sent, recorded = [], []

        def fake_leaf(*a, **k):
            for _ in range(attempts):   # standard 2 + 180s + fallback + LR相当の複数attempt
                sent.extend(sent_voice_via_standard(p9a.VOICE_NAME))
                recorded.append(gclient.effective_voice(p9a.VOICE_NAME))
            return {"status": "OK"}

        spec = z.ClipSpec("full_story_part1_c1", level, "narrator", "text", voice=voice, speaker="narrator",
                          role_key=z.role_key_for("narrator", level, "narrator"), part=1, language="en")
        import er003_v1_n3_01_tts_generate as n3
        import er003_v1_sing01_news_tail_fix as ntf
        with mock.patch.object(ntf, "generate_news_narration_wide_margin", fake_leaf), \
             mock.patch.object(n3, "generate_a2_segment_with_slowdown", fake_leaf), \
             mock.patch.object(z, "_check_stop_sentinel", lambda *a, **k: None):
            z.real_generators()["narrator"](spec, "x.wav")
        return sent, recorded

    def test_c_narrator_all_attempts_same_voice_std_adv(self):
        for level in ("a2", "b1b"):
            sent, rec = self._run_narrator(level, "Fenrir")
            self.assertEqual(sent, ["Fenrir"] * 5, level)
            self.assertEqual(rec, ["Fenrir"] * 5, level)     # (d) 記録voice=実送信voice
        sent, rec = self._run_narrator("a2", "Aoede")      # Melos等Aoede narrator = 従来どおり
        self.assertEqual(sent, ["Aoede"] * 5)

    def test_c2_scope_resets_after_exception(self):
        def boom(*a, **k):
            raise RuntimeError("x")
        spec = z.ClipSpec("full_story_part1_c1", "a2", "narrator", "t", voice="Fenrir", speaker="narrator",
                          role_key=z.role_key_for("narrator", "a2", "narrator"), part=1, language="en")
        import er003_v1_n3_01_tts_generate as n3
        with mock.patch.object(n3, "generate_a2_segment_with_slowdown", boom), mock.patch.object(z, "_check_stop_sentinel", lambda *a, **k: None):
            with self.assertRaises(RuntimeError):
                z.real_generators()["narrator"](spec, "x.wav")
        self.assertEqual(gclient.effective_voice("Aoede"), "Aoede")


    # (c3) resume: block progress fingerprintにoverride Voiceが入る(別Voice旧progressの再利用防止)。override無し=従来fingerprint(不変)
    def test_c3_block_progress_fingerprint_includes_override_voice_only(self):
        import er127_tts_block_policy_01 as e127
        seen = []
        def spy_open_block(leaf, out_path, text, ctx=None, max_attempts=3, fingerprint=None, z_dialogue_policy=None):
            seen.append(dict(fingerprint))
            return None
        @e127.with_block("L2", fingerprint_params=("style_prefix_override",))
        def leaf(text, out_path, max_attempts=3, style_prefix_override=None, _blk=None):
            return {"status": "OK"}
        with mock.patch.object(e127, "open_block", spy_open_block):
            leaf("t", "a.wav", style_prefix_override="s")
            with gclient.voice_override("Fenrir"):
                leaf("t", "a.wav", style_prefix_override="s")
            with gclient.voice_override("Aoede"):
                leaf("t", "a.wav", style_prefix_override="s")
        self.assertNotIn("voice", seen[0])
        self.assertEqual(seen[1]["voice"], "Fenrir")
        self.assertNotIn("voice", seen[2])
        self.assertEqual(seen[0], seen[2])


    # (d2) SDK境界の独立記録: cost_log(er005)のTTS行へ実request configのvoice名(tts_voice_sent)が残る(textには付かない)
    def test_d2_cost_logger_records_sent_voice(self):
        import er005_cost_logger as cl
        from google.genai import models as gm
        recs = []
        orig = gm.Models.generate_content
        try:
            gm.Models.generate_content = lambda self, *a, **k: SimpleNamespace(candidates=[SimpleNamespace(content=SimpleNamespace(parts=[]))], usage_metadata=None)
            with mock.patch.object(cl, "record", lambda e: recs.append(e)):
                cl._patch_gemini()
                cfg = gclient.types.GenerateContentConfig(response_modalities=["AUDIO"], speech_config=gclient.build_speech_config("Algieba"))
                gm.Models.generate_content(object(), model="m", contents="x", config=cfg)
                gm.Models.generate_content(object(), model="m", contents="x", config=gclient.types.GenerateContentConfig())
        finally:
            gm.Models.generate_content = orig
        self.assertEqual(recs[0]["tts_voice_sent"], "Algieba")
        self.assertNotIn("tts_voice_sent", recs[1])

    def test_d_attempt_record_sites_use_effective_voice(self):
        import re
        for f in ("er003_v1_sing01_news_tail_fix.py", "er003_v1_crosslevel_audio_02_common.py",
                  "er003_v1_repro01_main_generate.py", "er003_b1_p9a_audio.py"):
            with open(f, encoding="utf-8") as fh:
                src = fh.read()
            self.assertNotRegex(src, r'"voice": (p9a\.)?VOICE_NAME[,}]', f)

    def test_e_z_narrator_voice_for_tell_tale_is_fenrir(self):
        import er062_family_z_structure_01 as s62
        self.assertEqual(s62.narrator_voice_for("the_tell_tale_heart"), "Fenrir")


if __name__ == "__main__":
    unittest.main()
