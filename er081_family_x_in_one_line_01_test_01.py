# ============================================================
# er081_family_x_in_one_line_01_test_01.py
# FXPW(FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01) 委任_02B
# Family X「In One Line」基本2文・必要な場合のみ3文(2026-10-16承認)の全経路適用のtest。実API呼出0、費用0円。
#   (1) Adv Prompt template(旧「1文」文言の撤去、_M1_REQ_ANCHOR保持、M1変種)
#   (2) 文数カウンタ
#   (3) Writer段のevidence保存・fail-closed STOP・Adv/Std不一致はWARNのみ(fake client)
#   (4) Std Promptの追加1文
#   (5) Local Rewrite文数保持gate(Family X scope内のみ有効、scope外不発)
#   (6) parts.jsonのin_one_line複数文
# 実行: .venv/Scripts/python.exe -m pytest er081_family_x_in_one_line_01_test_01.py -q
# ============================================================
from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

import er003_v1_n3_01_advanced_adaptation_generate as adv_gen
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_standard_a2_generate as std_gen
import er012_e_family_entertainment_two_level_runner_01 as efam
import er020_tts_retry_local_rewrite_01 as lr
import er081_family_x_in_one_line_01 as iol

T = adv_gen.FAMILY_X_IN_ONE_LINE_INSTRUCTION_TEMPLATE


class TemplateTests(unittest.TestCase):
    def test_old_one_sentence_wording_removed(self):
        for old in ("Exactly one sentence", "12-18", "Trial-only", "ONE short", "single most important",
                    "for the listener"):
            self.assertNotIn(old, T, old)
            self.assertNotIn(old, adv_gen.FAMILY_X_IN_ONE_LINE_INSTRUCTION_TEMPLATE_M1, old)

    def test_new_wording_present(self):
        for s in ("normally TWO short", "Normally exactly two sentences", "Never write more than three sentences",
                  "never add a third sentence just to add detail", "roughly 12-22 words per sentence",
                  "its meaning or why it matters, as the article states it", "{article_text}"):
            self.assertIn(s, T, s)

    def test_m1_anchor_preserved_and_m1_variant_assembled(self):
        self.assertIn(adv_gen._M1_REQ_ANCHOR, T)
        self.assertNotEqual(adv_gen.FAMILY_X_IN_ONE_LINE_INSTRUCTION_TEMPLATE_M1, T)
        self.assertIn(adv_gen.FAMILY_X_IN_ONE_LINE_M1_REQUIREMENT_LINE,
                      adv_gen.FAMILY_X_IN_ONE_LINE_INSTRUCTION_TEMPLATE_M1)
        p = adv_gen.build_family_x_in_one_line_prompt("Ttl", "Body.", ja_text="JA", ledger_text="LED")
        self.assertIn("[Japanese source article]\nJA", p)
        self.assertIn("[Verified Fact Ledger]\nLED", p)
        self.assertIn("# Ttl\n\nBody.", p)
        self.assertEqual(adv_gen.build_family_x_in_one_line_prompt("Ttl", "Body."), T.format(article_text="# Ttl\n\nBody."))


class CounterTests(unittest.TestCase):
    def test_counts(self):
        c = iol.count_in_one_line_sentences
        self.assertEqual(c("It rose. It matters."), 2)
        self.assertEqual(c("It rose. It matters. It may not last."), 3)
        self.assertEqual(c("It rose and it matters."), 1)
        self.assertEqual(c("One. Two. Three. Four."), 4)
        self.assertEqual(c(""), 0)

    def test_abbreviations_quotes_numbers_dollar_newline(self):
        c = iol.count_in_one_line_sentences
        self.assertEqual(c("The U.S. Army said so. It ended."), 2)
        self.assertEqual(c("Mr. Smith paid Dr. Lee 3.5 dollars. Fine."), 2)
        self.assertEqual(c('He said "go." Then he left.'), 2)
        self.assertEqual(c("Prices rose 3.5 percent. $5 coffee is now common."), 2)
        self.assertEqual(c("It rose.\nIt matters."), 2)
        self.assertEqual(c("What happened? It rose! It matters."), 3)

    def test_spec_counts(self):
        self.assertEqual(set(iol.IN_ONE_LINE_SPEC_COUNTS), {2, 3})


class ScopeTests(unittest.TestCase):
    def test_scope_default_off_and_restored(self):
        self.assertFalse(iol.is_family_x_in_one_line_scope())
        with iol.family_x_in_one_line_scope():
            self.assertTrue(iol.is_family_x_in_one_line_scope())
        self.assertFalse(iol.is_family_x_in_one_line_scope())
        with self.assertRaises(ValueError):
            with iol.family_x_in_one_line_scope():
                raise ValueError("x")
        self.assertFalse(iol.is_family_x_in_one_line_scope())


class StdPromptTests(unittest.TestCase):
    def test_std_prompt_contains_sentence_count_inheritance(self):
        p = std_gen.build_family_x_no_heading_prompt("# T\n\nA.\n\nB.\n\nC.\n\n## In one line\nX. Y.")
        self.assertIn('Keep the "In one line" section at the same number of sentences as in the article below '
                      "(normally two), each as a short A2 sentence; do not merge it into one sentence.", p)
        self.assertIn("do not add or remove sections. Keep the", p)


# ------------------------------------------------------------
# Writer段(fake client、API 0)
# ------------------------------------------------------------
JA = "日本語記事"
ADV_BODY = ("Para one has enough words here today.\n\nPara two has enough words here today.\n\n"
            "Para three has enough words here today.")


def _adv_result():
    return SimpleNamespace(title="Adv Title", body=ADV_BODY, model_id_requested="m", model_id_actual="m-actual",
                           fallback_detected=False, response_id="resp_adv", structure_status="STRUCTURE_PASS",
                           attempts=1, retried=False, usage={"input_tokens": 1}, cost_usd=0.0, cost_jpy=0.0,
                           elapsed_seconds=0.1)


def _iol(text, rid="resp_iol"):
    return {"text": text, "model": "m-iol", "response_id": rid, "usage": {"input_tokens": 5},
            "cost_usd": 0.0, "cost_jpy": 0.0, "elapsed_seconds": 0.1, "prompt": "SENT PROMPT " + text}


def _std_result(iol_text):
    text = ("# Std Title\n\nS one has enough simple words here.\n\nS two has enough simple words here.\n\n"
            f"S three has enough simple words here.\n\n## In one line\n{iol_text}")
    return SimpleNamespace(text=text, model_id_requested="m", model_id_actual="m-std", fallback_detected=False,
                           response_id="resp_std", structure_status="STRUCTURE_PASS", attempts=1, retried=False,
                           usage={"input_tokens": 9}, cost_usd=0.0, cost_jpy=0.0, elapsed_seconds=0.1, checks={})


class WriterStageTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="fxpw2b_")
        self.theme = {"theme_id": "t", "out_dir": self.d}

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def _run(self, adv_iol_text, std_iol_text=None, only=None):
        with mock.patch.object(efam.adv_gen, "generate_family_x_faithful_translation",
                               return_value=_adv_result()), \
             mock.patch.object(efam.adv_gen, "generate_family_x_in_one_line",
                               return_value=_iol(adv_iol_text)) as m_iol, \
             mock.patch.object(efam.std_gen, "generate_family_x_standard_a2_no_heading",
                               return_value=_std_result(std_iol_text or adv_iol_text)):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                try:
                    ev = efam.run_writer_stage(object(), self.theme, JA, "LEDGER", 1000.0, only=only)
                    return ev, buf.getvalue(), None
                except RuntimeError as e:
                    return None, buf.getvalue(), e

    def _summary(self):
        with open(f"{self.d}/writer_run_summary.json", encoding="utf-8") as f:
            return json.load(f)

    def test_two_sentences_pass_and_evidence_saved(self):
        ev, out, err = self._run("It rose last year. It matters for daily life.")
        self.assertIsNone(err)
        a = ev["advanced"]["in_one_line"]
        self.assertEqual(set(a), {"sentence_count", "spec_ok", "model_id_actual", "response_id", "prompt_sha256", "usage"})
        self.assertEqual(a["sentence_count"], 2)
        self.assertTrue(a["spec_ok"])
        self.assertEqual(a["response_id"], "resp_iol")
        self.assertEqual(a["model_id_actual"], "m-iol")
        import hashlib
        self.assertEqual(a["prompt_sha256"], hashlib.sha256(
            "SENT PROMPT It rose last year. It matters for daily life.".encode("utf-8")).hexdigest())
        s = ev["standard"]["in_one_line"]
        self.assertEqual((s["sentence_count"], s["spec_ok"], s["response_id"]), (2, True, "resp_std"))
        saved = self._summary()
        self.assertIn("in_one_line", saved["advanced"])
        self.assertIn("in_one_line", saved["standard"])
        self.assertNotIn("[WARN][IOL-SPEC]", out)
        self.assertTrue(os.path.exists(f"{self.d}/b1b/article.md"))
        self.assertTrue(os.path.exists(f"{self.d}/a2/article.md"))

    def test_three_sentences_pass(self):
        ev, out, err = self._run("It rose. It may not last. It matters.")
        self.assertIsNone(err)
        self.assertEqual(ev["advanced"]["in_one_line"]["sentence_count"], 3)
        self.assertTrue(ev["advanced"]["in_one_line"]["spec_ok"])

    def test_one_sentence_advanced_stops_before_article_saved(self):
        ev, out, err = self._run("It rose last year and it matters.", only="advanced")
        self.assertIsNotNone(err)
        self.assertIn("[STOP]", str(err))
        self.assertIn("IN_ONE_LINE_SPEC", str(err))
        self.assertFalse(os.path.exists(f"{self.d}/b1b/article.md"))
        self.assertFalse(os.path.exists(f"{self.d}/b1b/parts.json"))
        self.assertTrue(os.path.exists(f"{self.d}/b1b/rejected_in_one_line_spec_article.md"))
        s = self._summary()["advanced"]["in_one_line"]
        self.assertEqual((s["sentence_count"], s["spec_ok"]), (1, False))

    def test_four_sentences_advanced_stops(self):
        ev, out, err = self._run("One a. Two b. Three c. Four d.", only="advanced")
        self.assertIsNotNone(err)
        self.assertEqual(self._summary()["advanced"]["in_one_line"]["sentence_count"], 4)

    def test_one_sentence_standard_stops(self):
        ev, out, err = self._run("It rose. It matters.", std_iol_text="It rose and it matters.")
        self.assertIsNotNone(err)
        self.assertIn("Standard", str(err))
        self.assertFalse(os.path.exists(f"{self.d}/a2/article.md"))
        self.assertTrue(os.path.exists(f"{self.d}/a2/rejected_in_one_line_spec_article.md"))
        self.assertTrue(os.path.exists(f"{self.d}/b1b/article.md"))      # Advancedは仕様内なので保存済み
        self.assertEqual(self._summary()["standard"]["in_one_line"]["sentence_count"], 1)

    def test_adv2_std3_warns_only(self):
        ev, out, err = self._run("It rose. It matters.", std_iol_text="It rose. It matters. It may end.")
        self.assertIsNone(err)
        self.assertIn("[WARN][IOL-SPEC]", out)
        self.assertEqual(ev["standard"]["in_one_line"]["sentence_count"], 3)

    def test_parts_json_accepts_multi_sentence_in_one_line(self):
        ev, out, err = self._run("It rose last year. It matters for daily life.")
        with open(f"{self.d}/b1b/parts.json", encoding="utf-8") as f:
            parts = json.load(f)
        self.assertEqual(parts["status"], "OK")
        self.assertEqual(parts["in_one_line"], "It rose last year. It matters for daily life.")
        self.assertEqual(sc.split_family_x_article_text_v2(open(f"{self.d}/b1b/article.md", encoding="utf-8").read())["status"], "OK")


class GenerateInOneLineSendsNewPromptTests(unittest.TestCase):
    def test_generate_returns_prompt_with_new_wording(self):
        sent = {}

        def fake_run(client, prompt, **kw):
            sent["p"] = prompt
            return {"raw_text": "A. B.", "model": "gpt-x", "response_id": "r1", "usage": {"input_tokens": 1}}
        with mock.patch.object(adv_gen.vfl01, "run_writer_no_search", side_effect=fake_run), \
             mock.patch.object(adv_gen.routing, "require_model", return_value="gpt-x"), \
             mock.patch.object(adv_gen, "_load_pricing", return_value=None), \
             mock.patch.object(adv_gen, "_compute_cost_jpy", return_value=(0.0, 0.0)):
            out = adv_gen.generate_family_x_in_one_line(object(), "T", "Body.", ja_text="JA", ledger_text="L")
        self.assertEqual(out["prompt"], sent["p"])
        self.assertIn("normally TWO short", sent["p"])
        self.assertNotIn("Exactly one sentence", sent["p"])


# ------------------------------------------------------------
# Local Rewrite文数保持gate
# ------------------------------------------------------------
def _g(ok=True):
    return {"pass": ok, "reason": "ok"}


def _qa(cid):
    return {"candidate_id": cid, "meaning_preserved": _g(), "role_preserved": _g(),
            "fact_non_contradiction": _g(), "context_connection": _g(), "natural_english": _g()}


ORIG = "It rose last year. It matters for daily life."
MERGED = "It rose last year, it matters for daily life."      # 句読点のみ変更(2文->1文)
SAME = "It rose last year. It matters for everyday life."     # 1語変更(2文のまま)


def _cand(cid, text, before, after):
    return {"id": cid, "rewrite_type": "single_word_swap", "rewritten_segment": text,
            "changed_span_before": before, "changed_span_after": after, "rationale": "t"}


class LocalRewriteSentenceCountGateTests(unittest.TestCase):
    def _records(self, orig, cands, segment_id):
        rng = lr.find_problem_span_token_range(orig, "daily life")
        return lr.build_full_candidate_records(orig, cands, [_qa(c["id"]) for c in cands], rng, segment_id=segment_id)

    def test_in_scope_sentence_merging_candidate_rejected(self):
        # 語は変えず「. It」->", it」のみ(tokenizeがpunctuationを落とすため従来のlocality検査をすり抜ける)
        cands = [_cand("c_merge", MERGED, "daily life", "daily life"),
                 _cand("c_ok", SAME, "daily life", "everyday life")]
        with iol.family_x_in_one_line_scope():
            recs = {r["id"]: r for r in self._records(ORIG, cands, "in_one_line")}
            self.assertFalse(recs["c_merge"]["8_sentence_count_unchanged"])
            self.assertEqual(recs["c_merge"]["sentence_count_check"]["before"], 2)
            self.assertEqual(recs["c_merge"]["sentence_count_check"]["after"], 1)
            self.assertFalse(recs["c_merge"]["adoptable"])
            self.assertTrue(recs["c_ok"]["8_sentence_count_unchanged"])
            sel = lr.select_final_candidate(list(recs.values()))
            self.assertNotEqual((sel["selected"] or {}).get("id"), "c_merge")

    def test_seven_gates_keys_unchanged(self):
        cands = [_cand("c_ok", SAME, "daily life", "everyday life")]
        with iol.family_x_in_one_line_scope():
            r = self._records(ORIG, cands, "in_one_line")[0]
        self.assertEqual(list(r["seven_gates"]), [
            "1_meaning_preserved", "2_role_preserved", "3_fact_non_contradiction", "4_context_connection",
            "5_natural_english_gate", "6_localized_minimal_change", "7_not_full_rewrite"])
        self.assertNotIn("8_sentence_count_unchanged", r["seven_gates"])

    def test_out_of_scope_gate_does_not_fire(self):
        cands = [_cand("c_merge", MERGED, "daily life", "daily life"),
                 _cand("c_ok", SAME, "daily life", "everyday life")]
        # scopeなし(Family A/B/C/Z相当): 同じ入力で追加gateは常にTrue、既存7 gateの結果はscope内と同一
        recs_out = {r["id"]: r for r in self._records(ORIG, cands, "in_one_line")}
        with iol.family_x_in_one_line_scope():
            recs_in = {r["id"]: r for r in self._records(ORIG, cands, "in_one_line")}
        for cid in recs_out:
            self.assertTrue(recs_out[cid]["8_sentence_count_unchanged"])
            self.assertFalse(recs_out[cid]["sentence_count_check"]["applicable"])
            self.assertEqual(recs_out[cid]["seven_gates"], recs_in[cid]["seven_gates"])
            self.assertEqual(recs_out[cid]["all_seven_gates_pass"], recs_in[cid]["all_seven_gates_pass"])
            self.assertEqual(recs_out[cid]["adoptable"], recs_out[cid]["all_seven_gates_pass"])

    def test_in_scope_other_roles_not_affected(self):
        cands = [_cand("c_merge", MERGED, "daily life", "daily life")]
        with iol.family_x_in_one_line_scope():
            for seg in ("full_story_part1", "preview", "comment", None):
                r = self._records(ORIG, cands, seg)[0]
                self.assertTrue(r["8_sentence_count_unchanged"], seg)
                self.assertFalse(r["sentence_count_check"]["applicable"], seg)

    def test_default_segment_id_none_backward_compatible(self):
        rng = lr.find_problem_span_token_range(ORIG, "daily life")
        recs = lr.build_full_candidate_records(ORIG, [_cand("c", SAME, "daily life", "everyday life")],
                                               [_qa("c")], rng)
        self.assertTrue(recs[0]["adoptable"])

class AudioRunnerScopeIntegrationTests(unittest.TestCase):
    """FXPW 委任_04: audio runnerのFamily X TTS段でのみLR文数gate用scopeが立つ(Zでは立たない)。"""

    class _Stop(Exception):
        pass

    def _capture(self, module, attr, call):
        seen = []

        def _spy(*a, **k):
            seen.append(iol.is_family_x_in_one_line_scope())
            raise self._Stop()
        self.assertFalse(iol.is_family_x_in_one_line_scope())
        with mock.patch.object(module, attr, side_effect=_spy):
            with self.assertRaises(self._Stop):
                call()
        self.assertFalse(iol.is_family_x_in_one_line_scope())  # 終了後に必ず元へ戻る
        return seen

    def test_b1_segments_run_inside_scope(self):
        import er019_family_x_audio_production_runner_01 as runner
        seen = self._capture(runner.style_profile_mod, "assert_profile_backend",
                             lambda: runner.generate_family_x_b1_segments("nonexistent_dir_fxpw04"))
        self.assertEqual(seen, [True])

    def test_a2_segments_run_inside_scope(self):
        import er019_family_x_audio_production_runner_01 as runner
        seen = self._capture(runner.style_profile_mod, "assert_profile_backend",
                             lambda: runner.generate_family_x_a2_segments("nonexistent_dir_fxpw04", "title"))
        self.assertEqual(seen, [True])

    def test_family_z_tts_stage_does_not_set_scope(self):
        import er063_family_z_audio_01 as z
        seen = self._capture(z, "assert_style_table_integrity",
                             lambda: z.run_tts_stage("nonexistent_dir_fxpw04", "a2", []))
        self.assertEqual(seen, [False])


if __name__ == "__main__":
    unittest.main()
