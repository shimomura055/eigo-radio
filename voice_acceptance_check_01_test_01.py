import json, os, tempfile, unittest
import voice_acceptance_check_01 as v


def mk(sent_voice, attempt_voice, planned="Fenrir"):
    d = tempfile.mkdtemp()
    os.makedirs(f"{d}/a2/audit"); os.makedirs(f"{d}/a2/narration/attempts")
    json.dump({"segments": {"c1": {"voice": planned}}}, open(f"{d}/a2/audit/tts_generation_results.json", "w"))
    e = {"provider": "gemini", "api": "models.generate_content(TTS)", "success": True, "stage": "tts_a2", "segment": "c1", "timestamp": "2026-10-28T02"}
    if sent_voice is not None:
        e["tts_voice_sent"] = sent_voice
    open(f"{d}/cost_log.jsonl", "w").write(json.dumps(e) + "\n")
    json.dump({"voice": attempt_voice}, open(f"{d}/a2/narration/attempts/c1_attempt1_x.json", "w"))
    return d


class T(unittest.TestCase):
    def test_match(self):
        self.assertEqual(v.check(mk("Fenrir", "Fenrir"), ["c1"], ("a2",))[1], 0)

    def test_sent_mismatch(self):
        self.assertEqual(v.check(mk("Aoede", "Fenrir"), ["c1"], ("a2",))[1], 1)

    def test_attempt_mismatch(self):
        self.assertEqual(v.check(mk("Fenrir", "Aoede"), ["c1"], ("a2",))[1], 1)

    def test_unmeasured_not_ok(self):
        self.assertEqual(v.check(mk(None, "Fenrir"), ["c1"], ("a2",))[1], 2)

    def test_post_slowdown_json_ignored(self):
        d = mk("Fenrir", "Fenrir")
        json.dump({"route": "post_slowdown"}, open(f"{d}/a2/narration/attempts/c1_attempt2_postslowdown.json", "w"))
        self.assertEqual(v.check(d, ["c1"], ("a2",))[1], 0)

    def test_since_filters_old(self):
        self.assertEqual(v.check(mk("Fenrir", "Fenrir"), ["c1"], ("a2",), since="2026-10-29")[1], 2)


if __name__ == "__main__":
    unittest.main()
