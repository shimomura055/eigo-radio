# -*- coding: utf-8 -*-
"""第2巡 arm群のunit test(Trial専用)。official無視(S2R-08)・縮約・弱化母音・Primary正綴り非根拠(S2R-06)・母音1つ差の判定不能(S2R-07)・断片へのG2P禁止。"""
import ast, copy, json, os, sys, unittest
sys.path.insert(0, os.getcwd())
import er100_pnps_stage2_trial_01_r2_arms as AR
import er100_pnps_stage2_trial_01_replay as RP


def sets(**kw):
    base = {"R1_V4": set(), "R1_EXT": set(), "n3": set(), "sup2": set()}
    base.update(kw)
    return base


class T(unittest.TestCase):
    def test_official_not_read(self):
        src = open(AR.__file__.replace(".pyc", ".py"), encoding="utf-8").read()
        tree = ast.parse(src)
        names = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str) and "official" in n.value.lower()]
        names = [n for n in names if len(n) < 40]   # docstring(長文)を除く。コード中の文字列定数に'official'が無いこと
        self.assertEqual(names, [])
        est = json.load(open("er100_output/pnps_stage2_trial_01/est_e2_e3.json", encoding="utf-8"))
        r0 = json.load(open("er100_output/pnps_stage2_trial_01/r0_extractions.json", encoding="utf-8"))
        est2 = copy.deepcopy(est)
        for w in est2:
            if est2[w].get("E3_llm") and est2[w]["E3_llm"].get("json") is not None:
                est2[w]["E3_llm"]["json"]["official"] = not est2[w]["E3_llm"]["json"].get("official", False)
        outs = []
        for e in (est, est2):
            S = RP.build_sets(e, r0)
            A = {w: RP.accepted(w, S[w]) for w in S}
            outs.append({w: AR.build_arm_sets(w, S[w], A[w], {}) for w in S})
        for w in outs[0]:
            self.assertEqual(outs[0][w]["n3"], outs[1][w]["n3"])

    def test_degemination_and_weak(self):
        cand = {("M", "EH", "L", "AH", "S")}
        a = sets(n3=cand, R1_EXT=cand)
        obs = {"primary": ["mello"], "azure": ["mellow"]}
        # N1(縮約のみ): 'mello'=M EH L OW。縮約でSは落ちるが OW≠AH なのでPASSしない
        self.assertNotEqual(AR.judge("melos", "Melos said.", obs, a, "N1_DEGEM")["verdict"], "PASS_WITH_WARNING")
        # N2(弱化母音同一視): OW0とAHは弱化母音同士 -> PASS
        self.assertEqual(AR.judge("melos", "Melos said.", obs, a, "N2_WEAK")["verdict"], "PASS_WITH_WARNING")
        # 次語がS始まりでなければ縮約は適用されない(真の語末子音脱落をPASSさせない)
        self.assertNotEqual(AR.judge("melos", "Melos ran.", obs, a, "N2_WEAK")["verdict"], "PASS_WITH_WARNING")

    def test_primary_exact_alone_is_not_evidence(self):
        a = sets(n3={("K", "EY", "T")}, R1_EXT={("K", "EY", "T")})
        v = AR.judge("khaite", "Khaite is here.", {"primary": ["khaite"]}, a, "N3_SUP2")["verdict"]
        self.assertNotEqual(v, "PASS_WITH_WARNING")
        v = AR.judge("khaite", "Khaite is here.", {"primary": ["khaite"], "azure": ["kate"]}, a, "N3_SUP2")["verdict"]
        self.assertEqual(v, "PASS_WITH_WARNING")   # 音素照合MATCH(Azure)が1つ必要

    def test_khaite_kite_stays_ng(self):
        a = sets(n3={("K", "EY", "T")}, R1_EXT={("K", "EY", "T")}, R1_V4={("K", "EY", "T")})
        for arm in AR.ARMS:
            v = AR.judge("khaite", "Khaite is here.", {"primary": ["kite"], "azure": ["kite"], "whisper_small": ["kite"]}, a, arm)["verdict"]
            self.assertIn(v, ("NG",), arm)

    def test_near_vowel_undecidable_when_engines_disagree(self):
        a = sets(n3={("K", "EY", "T")}, R1_EXT={("K", "EY", "T")})
        v = AR.judge("khaite", "Khaite is here.", {"primary": ["kite"], "azure": ["kate"]}, a, "N5_UND")["verdict"]
        self.assertNotEqual(v, "PASS_WITH_WARNING")
        self.assertTrue(v.startswith("HR_MAINTAINED"))

    def test_g2p_not_for_fragments(self):
        self.assertIsNone(AR.variants(["kt"], True))
        self.assertIsNotNone(AR.variants(["zabalina"], True))
        self.assertIsNone(AR.variants(["zabalina"], False))


if __name__ == "__main__":
    unittest.main()
