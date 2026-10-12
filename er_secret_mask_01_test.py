import io, os, sys, unittest
import er_secret_mask_01 as m

FAKE = "FAKEKEY0123456789abcdefFAKEKEY99"


class T(unittest.TestCase):
    def setUp(self):
        os.environ["TEST_SPEECH_KEY"] = FAKE

    def tearDown(self):
        os.environ.pop("TEST_SPEECH_KEY", None)

    def test_mask_str_and_bytes(self):
        self.assertNotIn(FAKE, m.mask_secrets(f"AUDIT call (1, b'{FAKE}', b'japanwest')"))
        self.assertIn("***", m.mask_secrets(f"x {FAKE} y"))
        self.assertNotIn(FAKE.encode(), m.mask_secrets(FAKE.encode()))

    def test_dotenv_values_masked(self):
        vals = m._secret_values()
        for v in vals:
            self.assertEqual(m.mask_secrets("a " + v + " b"), "a *** b")

    def test_stream(self):
        buf = io.StringIO()
        s = m.MaskingStream(buf)
        s.write(f"err {FAKE}\n")
        self.assertNotIn(FAKE, buf.getvalue())

    def test_extra_and_nonstr(self):
        self.assertEqual(m.mask_secrets(ValueError("zzzz1234"), extra=["zzzz1234"]), "***")


if __name__ == "__main__":
    unittest.main()
