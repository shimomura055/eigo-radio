# -*- coding: utf-8 -*-
"""TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_03: Y生成関数の共通decoratorが所定の関数に付いていることの回帰test(API 0)。

委任_02(commit e8773980a)で `_register_y_stop_check` を `generate_y_b1_segments` の直前に挿入した際、b1b用の
`@secondary_run_scope.with_secondary_run` と `@y_family_scope("b1b")` が補助関数側へ移りb1b生成関数から外れていた(委任_03のruntime evidence中に発見・是正)。
"""
import unittest

import er121_family_y_audio_01 as ya


class YGeneratorDecoratorTest(unittest.TestCase):
    def test_generators_have_secondary_run_and_er109_scope(self):
        for fn in (ya.generate_y_b1_segments, ya.generate_y_a2_segments):
            self.assertTrue(getattr(fn, "__secondary_run_scoped__", False), fn.__name__)
            self.assertEqual(getattr(fn, "__er109_scoped__", None), "Y", fn.__name__)

    def test_helper_is_plain(self):
        self.assertFalse(getattr(ya._register_y_stop_check, "__secondary_run_scoped__", False))
        self.assertIsNone(getattr(ya._register_y_stop_check, "__er109_scoped__", None))


if __name__ == "__main__":
    unittest.main()
