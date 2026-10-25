# er003_kp_general_explanation_01_runner_integration_test_01.py
# FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_14: 学習テキスト Part 1 のX/Z runner統合test(API 0。LLMは全てmock)。
# 実行: .venv/Scripts/python.exe -m pytest er003_kp_general_explanation_01_runner_integration_test_01.py -q
#  Z: mock context(er026 build_mock_context)で kp→kp_part1_b1b→TTS前停止・M2(tts/pages)・2段再生成・描画停止(M3 (ii))
#  X: run_theme_scaffold(b1bのみ)・失敗の専用marker/rc=3(M1)・--stage study_text・M2(tts/player入口)・player描画停止
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

import er003_kp_general_explanation_01 as p1
import er003_v1_n3_01_scaffold_generate as sc
import er019_family_x_audio_production_runner_01 as xr
import er026_family_z_fiction_production_runner_01 as zr
import er062_family_z_structure_01 as st62
import er063_family_z_audio_01 as a63
from er119_test_support_01 import declare_ctx as _declare_ctx  # noqa: E402
import er119_kp_wiring_01 as _kpw  # noqa: E402

QUOTE1 = "They tried to cross a bog, but the ground gave way beneath them."
QUOTE2 = "Inventing convincing stories at a moment's notice was Vera's speciality."
QUOTE3 = "She would catch her breath before the long walk home."
XARTICLE = f"{QUOTE1}\n\n{QUOTE2}\n\n{QUOTE3}\n\nA fourth paragraph closes the story.\n"
X_ITEMS = [
    {"rank": 1, "source_span": "gave way", "source_sentence": QUOTE1, "display_phrase": "gave way", "key_phrase": "give way", "used_form": "give way",
     "japanese_gloss": "崩れる", "fulltext_source_ref": "fulltext_exact_v1", "gloss_alignment_status": "ALIGN_PASS"},
    {"rank": 2, "source_span": "at a moment's notice", "source_sentence": QUOTE2, "display_phrase": "at a moment's notice",
     "key_phrase": "at a moment's notice", "used_form": "at a moment's notice", "japanese_gloss": "急なことにも即座に",
     "fulltext_source_ref": "fulltext_exact_v1", "gloss_alignment_status": "ALIGN_PASS"},
    {"rank": 3, "source_span": "catch her breath", "source_sentence": QUOTE3, "display_phrase": "catch her breath",
     "key_phrase": "catch one's breath", "used_form": "catch one's breath", "japanese_gloss": "一息つく",
     "fulltext_source_ref": "fulltext_exact_v1", "gloss_alignment_status": "ALIGN_PASS"},
]
PASS = {"selection": {"status": "KEY_WORDS_STRUCTURE_PASS"}, "canonicalization": {"status": "CANONICALIZATION_PASS"}, "m2_fallback_events": []}


def ja_text(prompt):
    """T1(引用英文の日本語訳)のmock応答。Promptの列挙行の数だけ構造検査を通る訳を返す。"""
    import re
    sents = re.findall(r"^\d+\. (.*)$", prompt.split("# 英文\n", 1)[1].split("\n# 出力形式", 1)[0], re.M)
    return json.dumps({"translations": [{"id": i, "ja": f"これは{i}番の英文の日本語訳です。"} for i, _ in enumerate(sents, 1)]}, ensure_ascii=False)


def ok_text(prompt):
    import re
    if prompt.startswith("あなたは英日翻訳者です"):
        return ja_text(prompt)   # FakeClient(client経路)は解説・訳の両方をこの応答関数で受ける
    phrases = re.findall(r"^\d+\. 英語表現: (.*)$", prompt, re.M)
    return "\n".join(f"### {i}. ({p})\n{p} の一般的な解説です。核となる意味と主要な使い方を**説明**します。*{p}* のように使われます。" for i, p in enumerate(phrases, 1))


def make_call_fn(responder=ok_text, model="gpt-6-luna"):
    calls = []

    def call_fn(prompt):
        calls.append(prompt)
        return responder(prompt), model, {"input_tokens": 100, "cached_input_tokens": 0, "output_tokens": 50}, f"resp_{len(calls)}"
    call_fn.calls = calls
    return call_fn


class FakeClient:
    """実client代替(default call経路 client.responses.create を通す)。"""

    def __init__(self, responder=ok_text, model="gpt-6-luna"):
        self.calls = []
        outer = self

        class _R:
            def create(self, **kw):
                outer.calls.append(kw)
                prompt = kw["input"][0]["content"]
                return SimpleNamespace(output_text=responder(prompt), model=model, id=f"resp_{len(outer.calls)}",
                                       usage=SimpleNamespace(input_tokens=100, output_tokens=50,
                                                             input_tokens_details=SimpleNamespace(cached_tokens=0),
                                                             output_tokens_details=SimpleNamespace(reasoning_tokens=0)))
        self.responses = _R()


class Tmp:
    def new_tmp(self):
        t = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, t, True)
        return t


def decision_record(test, decision="T2"):
    d = tempfile.mkdtemp()
    test.addCleanup(shutil.rmtree, d, True)
    path = os.path.join(d, "part1_translation_decision.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"decision": decision, "source": "test"}, f)
    patcher = mock.patch.object(p1, "TRANSLATION_DECISION_RECORD", path)
    patcher.start()
    test.addCleanup(patcher.stop)


def no_decision_record(test):
    patcher = mock.patch.object(p1, "TRANSLATION_DECISION_RECORD", os.path.join(tempfile.gettempdir(), "no_such_part1_decision_xyz.json"))
    patcher.start()
    test.addCleanup(patcher.stop)


def quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)


# ============================================================
# Z
# ============================================================
class ZPart1Tests(Tmp, unittest.TestCase):
    PRE = ["seed_check", "writer", "std_adjust", "plan", "support", "kp"]

    def _ctx_through_kp(self):
        ctx = zr.build_mock_context(self.new_tmp())
        _declare_ctx(ctx)   # KP Human Review: 既存mock testのfixture(Human不在を明示宣言)
        quiet(zr.run_stages, ctx, self.PRE)
        return ctx

    def test_kp_stage_generates_part1_after_kp_before_tts_with_provenance(self):
        no_decision_record(self)
        ctx = self._ctx_through_kp()
        out = ctx.out_dir
        doc = json.load(open(f"{out}/key_phrases/b1b/kp_general_explanations.json", encoding="utf-8"))
        self.assertEqual(doc["audit"]["model"], "gpt-6-luna")
        self.assertEqual(doc["audit"]["process"], "KEY_PHRASE_GENERAL_EXPLANATION")
        self.assertEqual(len(doc["items"]), 5)   # KP Human Review: Part 1の単語解説は最大5件(vocab_confirmed.json、KP3件を含む)
        prov = json.load(open(f"{out}/writer/provenance.json", encoding="utf-8"))
        ent = prov["downstream_stages"]["kp_part1_b1b"]
        self.assertEqual(ent["model"], "gpt-6-luna")
        self.assertEqual(ent["prompt_sha256"], doc["audit"]["prompt_sha256"])
        self.assertTrue(ent["input_sha256"])
        self.assertFalse(os.path.exists(f"{out}/b1b/audit/tts_generation_results.json"))   # TTS未着手
        rows = json.load(open(f"{out}/study_text/part1_vocabulary_expressions.json", encoding="utf-8"))["rows"]
        self.assertTrue(rows and all(r["source_sentence_ja"] and r["translation_status"] == "PROVIDED" for r in rows))   # T1: 訳は常に生成される
        calls = [json.loads(x) for x in open(f"{out}/mock_api_calls.jsonl", encoding="utf-8")]
        self.assertEqual([c for c in calls if c["kind"] == "kp_part1"].__len__(), 1)
        self.assertEqual([c for c in calls if c["kind"] == "kp_part1_ja"].__len__(), 1)     # 解説とは独立の別call
        jd = json.load(open(f"{out}/key_phrases/b1b/kp_source_sentence_ja.json", encoding="utf-8"))
        self.assertEqual(jd["audit"]["process"], "KEY_PHRASE_SOURCE_SENTENCE_JA")
        ent_ja = prov["downstream_stages"]["kp_part1_ja_b1b"]
        self.assertEqual(ent_ja["prompt_sha256"], jd["audit"]["prompt_sha256"])
        self.assertEqual(ent_ja["model"], "gpt-6-luna")

    def test_resume_reuses_without_new_call(self):
        ctx = self._ctx_through_kp()
        n = sum(1 for _ in open(f"{ctx.out_dir}/mock_api_calls.jsonl", encoding="utf-8"))
        res = quiet(zr.run_stages, ctx, ["kp"])
        self.assertEqual(res["kp"]["kp_part1_b1b"], "reused")
        self.assertEqual(res["kp"]["kp_part1_ja_b1b"], "reused")
        self.assertEqual(n, sum(1 for _ in open(f"{ctx.out_dir}/mock_api_calls.jsonl", encoding="utf-8")))

    def test_failure_is_fail_closed_before_tts_with_next_command(self):
        ctx = zr.build_mock_context(self.new_tmp())
        _declare_ctx(ctx)   # KP Human Review: 既存mock testのfixture(Human不在を明示宣言)
        ctx.hooks["part1_call_fn"] = make_call_fn(lambda prompt: "壊れた出力(見出しなし)")
        with self.assertRaisesRegex(zr.FamilyZE2EStop, "FAMILY_Z_KP_GENERAL_EXPLANATION_NOT_OK.*--regenerate-stage kp_part1_b1b"):
            quiet(zr.run_stages, ctx, self.PRE)
        self.assertEqual(len(ctx.hooks["part1_call_fn"].calls), 2)    # 初回+技術retry1回のみ
        self.assertFalse(os.path.exists(f"{ctx.out_dir}/b1b/audit/tts_generation_results.json"))
        self.assertFalse(os.path.exists(f"{ctx.out_dir}/key_phrases/b1b/kp_general_explanations.json"))   # 空欄で続行しない

    def test_mock_without_hook_stops_without_real_api(self):
        ctx = zr.build_mock_context(self.new_tmp())
        _declare_ctx(ctx)   # KP Human Review: 既存mock testのfixture(Human不在を明示宣言)
        del ctx.hooks["part1_call_fn"]
        with mock.patch("er003_v1_b1_scaffold_01_generate.get_client", side_effect=AssertionError("REAL CLIENT")):
            with self.assertRaisesRegex(zr.FamilyZE2EStop, "FAMILY_Z_KP_PART1_NO_HOOK"):
                quiet(zr.run_stages, ctx, self.PRE)

    def test_tts_and_pages_entrances_stop_when_part1_missing_or_stale(self):
        ctx = self._ctx_through_kp()
        path = f"{ctx.out_dir}/key_phrases/b1b/kp_general_explanations.json"
        good = open(path, encoding="utf-8").read()
        # (a) 欠落(Part 1導入前のrun再開を模擬): load_level_inputs(TTS/Gate/Assembly共有)とstage_pagesがSTOP
        os.remove(path)
        with self.assertRaisesRegex(zr.FamilyZE2EStop, "KP_PART1_NOT_READY.*MISSING.*--regenerate-stage kp_part1_b1b"):
            zr.load_level_inputs(ctx, "b1b")
        with self.assertRaisesRegex(zr.FamilyZE2EStop, "KP_PART1_NOT_READY"):
            zr.stage_pages(ctx)
        with self.assertRaisesRegex(zr.FamilyZE2EStop, "KP_PART1_NOT_READY"):
            quiet(zr.run_stages, ctx, ["tts_b1b"])
        # (b) 最新性: 保存済みsignatureが現在KPと違う
        d = json.loads(good)
        d["phrases_signature"] = "0" * 64
        open(path, "w", encoding="utf-8").write(json.dumps(d))
        with self.assertRaisesRegex(zr.FamilyZE2EStop, "KP_PART1_EXPLANATIONS_STALE"):
            zr.load_level_inputs(ctx, "b1b")
        # (c) a2(Standard)は対象外: 確認されない
        zr.load_level_inputs(ctx, "a2")

    def test_kp_expression_change_needs_two_step_regeneration_with_hints(self):
        ctx = self._ctx_through_kp()
        kp_path = f"{ctx.out_dir}/key_phrases/b1b/keywords_canonicalized.json"
        kp = json.load(open(kp_path, encoding="utf-8"))
        kp["items"][0]["used_form"] = "changed expression"
        open(kp_path, "w", encoding="utf-8").write(json.dumps(kp, ensure_ascii=False, indent=2))
        # 1段目: kp_expl_b1bが止まる(次コマンドに2段再生成を明記)
        with self.assertRaisesRegex(st62.FamilyZProvenanceMismatchStop, "--regenerate-stage kp_expl_b1b.*--regenerate-stage kp_part1_b1b"):
            quiet(zr.run_stages, ctx, ["kp"])
        ctx.regenerate_stage = "kp_expl_b1b"
        with self.assertRaisesRegex(st62.FamilyZProvenanceMismatchStop, "次の一手.*--regenerate-stage kp_part1_b1b"):
            quiet(zr.run_stages, ctx, ["kp"])             # 2段目: kp_part1_b1bが止まる
        ctx.regenerate_stage = "kp_part1_b1b"
        res = quiet(zr.run_stages, ctx, ["kp"])
        self.assertEqual(res["kp"]["kp_part1_b1b"], "generated")
        doc = json.load(open(f"{ctx.out_dir}/key_phrases/b1b/kp_general_explanations.json", encoding="utf-8"))
        self.assertEqual(doc["phrases"][0], "changed expression")

    def test_regenerate_stage_choice_registered(self):
        self.assertIn("kp_part1_b1b", zr.E2E_KP_EXTRA_REGEN_NAMES)
        self.assertIn("kp_part1_b1b", zr.build_parser().parse_args(["--regenerate-stage", "kp_part1_b1b"]).regenerate_stage)

    def test_pages_do_not_render_study_block_without_decision_record_and_are_byte_identical(self):
        no_decision_record(self)
        ctx = self._ctx_through_kp()
        rest = [s for s in zr.E2E_STAGES if s not in self.PRE and s != "page_verify"]
        quiet(zr.run_stages, ctx, rest)
        index = open(f"{ctx.pages_dir}/index.html", encoding="utf-8").read()
        self.assertNotIn("class='study'", index)
        self.assertNotIn("Vocabulary", index)
        # 従来経路(study_html未指定)で直接buildしたものとバイト同一(判断記録なし=従来と完全に同じ出力)
        a63.build_pages(ctx.out_dir, ctx.pages_dir, page_title=zr.STORY_REGISTRY[ctx.story_key]["page_title_ja"],
                        audio_file_prefix=zr.STORY_REGISTRY[ctx.story_key]["audio_file_prefix"], reuse_existing_audio=True)
        self.assertEqual(index, open(f"{ctx.pages_dir}/index.html", encoding="utf-8").read())
        # study_text/は保存されている(生成・保存まで行う)
        self.assertTrue(os.path.exists(f"{ctx.out_dir}/study_text/part1_vocabulary_expressions.md"))

    def test_pages_render_advanced_only_study_block_after_decision_and_pass_standard_check(self):
        decision_record(self, "T2")
        ctx = self._ctx_through_kp()
        rest = [s for s in zr.E2E_STAGES if s not in self.PRE and s != "page_verify"]
        quiet(zr.run_stages, ctx, rest)          # build_pages内でlint+標準適合checkがPASSしなければFamilyZAudioStop
        index = open(f"{ctx.pages_dir}/index.html", encoding="utf-8").read()
        self.assertEqual(index.count("<section class='study'>"), 1)
        adv_pos, study_pos = index.index("id='adv'"), index.index("<section class='study'>")
        self.assertGreater(study_pos, adv_pos)                                  # Advanced節の中
        self.assertNotIn("class='study'", open(f"{ctx.pages_dir}/standard.html", encoding="utf-8").read())
        import er_user_listening_page_common_01 as uc
        self.assertEqual(uc.check_page(index, base_dir=ctx.pages_dir)["overall"], "PASS")
        for pat in ("日本語訳",):
            self.assertNotIn(pat, index.split("<section class='study'>")[1].split("</section>")[0])   # T2=訳欄なし

    def test_stage_pages_does_not_pass_study_html_without_decision_record(self):
        no_decision_record(self)
        ctx = self._ctx_through_kp()
        with mock.patch.object(a63, "build_pages", return_value={}) as bp:
            zr.stage_pages(ctx)
        self.assertNotIn("study_html", bp.call_args.kwargs)             # 判断記録なし=従来と同一の呼出(DefaultOffIsolation)
        decision_record(self, "T2")
        with mock.patch.object(a63, "build_pages", return_value={}) as bp:
            zr.stage_pages(ctx)
        self.assertIn("Vocabulary &amp; Expressions", bp.call_args.kwargs["study_html"])

    def test_t1_pages_render_five_items_with_translation(self):
        ctx = self._ctx_through_kp()     # 実record(T1)のまま
        rest = [s for s in zr.E2E_STAGES if s not in self.PRE and s != "page_verify"]
        quiet(zr.run_stages, ctx, rest)
        index = open(f"{ctx.pages_dir}/index.html", encoding="utf-8").read()
        blk = index.split("<section class='study'>")[1].split("</section>")[0]
        for lab in ("本文中の意味", "本文の英文", "日本語訳", "解説"):
            self.assertEqual(blk.count(f"<dt>{lab}</dt>"), 5, lab)   # KP Human Review: 5件
        self.assertIn("mock日本語訳", blk)
        self.assertNotIn("class='study'", open(f"{ctx.pages_dir}/standard.html", encoding="utf-8").read())

    def test_translation_missing_or_stale_stops_tts_and_pages_with_next_command(self):
        ctx = self._ctx_through_kp()
        path = f"{ctx.out_dir}/key_phrases/b1b/kp_source_sentence_ja.json"
        good = open(path, encoding="utf-8").read()
        os.remove(path)    # T1導入前のrun再開を模擬
        with self.assertRaisesRegex(zr.FamilyZE2EStop, "KP_PART1_JA_NOT_READY.*MISSING.*--regenerate-stage kp_part1_ja_b1b"):
            zr.load_level_inputs(ctx, "b1b")
        with self.assertRaisesRegex(zr.FamilyZE2EStop, "KP_PART1_JA_NOT_READY"):
            zr.stage_pages(ctx)
        d = json.loads(good)
        d["translations_signature"] = "0" * 64
        open(path, "w", encoding="utf-8").write(json.dumps(d))
        with self.assertRaisesRegex(zr.FamilyZE2EStop, "KP_PART1_TRANSLATIONS_STALE"):
            zr.load_level_inputs(ctx, "b1b")
        zr.load_level_inputs(ctx, "a2")   # Standardは対象外

    def test_translation_failure_is_fail_closed_and_does_not_touch_explanation(self):
        ctx = zr.build_mock_context(self.new_tmp())
        _declare_ctx(ctx)   # KP Human Review: 既存mock testのfixture(Human不在を明示宣言)
        ctx.hooks["part1_ja_call_fn"] = make_call_fn(lambda prompt: "壊れた出力(JSONではない)")
        with self.assertRaisesRegex(zr.FamilyZE2EStop, "FAMILY_Z_KP_PART1_JA_NOT_OK.*--regenerate-stage kp_part1_ja_b1b"):
            quiet(zr.run_stages, ctx, self.PRE)
        self.assertEqual(len(ctx.hooks["part1_ja_call_fn"].calls), 2)     # 初回+技術retry1回のみ
        self.assertTrue(os.path.exists(f"{ctx.out_dir}/key_phrases/b1b/kp_general_explanations.json"))   # 解説は無傷で残る
        self.assertFalse(os.path.exists(f"{ctx.out_dir}/key_phrases/b1b/kp_source_sentence_ja.json"))   # 空欄で続行しない
        self.assertFalse(os.path.exists(f"{ctx.out_dir}/b1b/audit/tts_generation_results.json"))
        # 解説は再利用(API 0)、訳だけ明示再生成で回復できる
        ctx.hooks["part1_ja_call_fn"] = make_call_fn(ja_text)
        ctx.regenerate_stage = "kp_part1_ja_b1b"
        res = quiet(zr.run_stages, ctx, ["kp"])
        self.assertEqual(res["kp"]["kp_part1_b1b"], "reused")
        self.assertEqual(res["kp"]["kp_part1_ja_b1b"], "generated")

    def test_translation_call_input_is_quotes_only(self):
        ctx = zr.build_mock_context(self.new_tmp())
        _declare_ctx(ctx)   # KP Human Review: 既存mock testのfixture(Human不在を明示宣言)
        ctx.hooks["part1_ja_call_fn"] = fn = make_call_fn(ja_text)
        quiet(zr.run_stages, ctx, self.PRE)
        kp = json.load(open(f"{ctx.out_dir}/key_phrases/b1b/keywords_canonicalized.json", encoding="utf-8"))
        prompt = fn.calls[0]
        for it in kp["items"]:
            self.assertIn(it["source_sentence"], prompt)
            self.assertNotIn(it["japanese_gloss"], prompt)


# ============================================================
# X
# ============================================================
def _x_setup(levels=("b1b",)):
    work, out = tempfile.mkdtemp(), tempfile.mkdtemp()
    src = f"{work}/er019_output/t/r"
    for lv in ("a2", "b1b"):
        os.makedirs(f"{src}/{lv}")
        open(f"{src}/{lv}/article.md", "w", encoding="utf-8").write(XARTICLE)
    return work, src, out


def _kp_writer(out):
    def fake(*a, text=None, kp_dir=None, article_id=None, level=None, **kw):   # KP Human Review: X Productionは確認付きKP経路(run_kp_with_review)を通る
        if a:   # 位置引数呼出(旧sc.run_key_phrases形式)も受ける
            text, kp_dir, article_id, level = (list(a) + [None] * 4)[:4]
        os.makedirs(kp_dir, exist_ok=True)
        with open(f"{kp_dir}/keywords_canonicalized.json", "w", encoding="utf-8") as f:
            json.dump({"items": X_ITEMS, "overall_status": "PASS"}, f, ensure_ascii=False)
        return PASS
    return fake


def _scaffold(src, out, levels, part1_call_fn, kp=None, ja_call_fn=None):
    with mock.patch.object(_kpw, "run_kp_with_review", side_effect=_kp_writer(out)) as rk, \
         mock.patch.object(xr.plan, "split_family_x_article_text_v2", return_value={"status": "OK", "paragraph_count": 4}), \
         mock.patch.object(xr, "run_family_x_b1_scaffold", return_value={}), \
         mock.patch.object(xr, "run_family_x_a2_scaffold", return_value={}), \
         contextlib.redirect_stdout(io.StringIO()):
        res = xr.run_theme_scaffold(None, src, out, list(levels), part1_call_fn=part1_call_fn,
                                    part1_ja_call_fn=ja_call_fn or make_call_fn(ja_text))
    return res, rk


class XPart1ScaffoldTests(Tmp, unittest.TestCase):
    def test_scaffold_runs_part1_only_for_b1b_after_kp_pass_and_saves(self):
        no_decision_record(self)
        work, src, out = _x_setup()
        fn = make_call_fn()
        res, rk = _scaffold(src, out, ("a2", "b1b"), fn)
        self.assertEqual(len(fn.calls), 1)                                      # a2では呼ばれない・b1bで1 call
        self.assertEqual(res["b1b"]["part1"]["status"], "OK")
        self.assertNotIn("part1", res["a2"])
        doc = json.load(open(f"{out}/b1b/key_phrases/kp_general_explanations.json", encoding="utf-8"))
        self.assertEqual(doc["phrases"], ["give way", "at a moment's notice", "catch one's breath"])
        self.assertFalse(os.path.exists(f"{out}/a2/key_phrases/kp_general_explanations.json"))
        rows = json.load(open(f"{out}/b1b/study_text/part1_vocabulary_expressions.json", encoding="utf-8"))["rows"]
        self.assertTrue(all(r["source_sentence_ja"] and r["translation_status"] == "PROVIDED" for r in rows))   # T1
        self.assertEqual(res["b1b"]["study_text"], "saved")
        self.assertTrue(os.path.exists(f"{out}/b1b/key_phrases/kp_source_sentence_ja.json"))
        self.assertFalse(os.path.exists(f"{out}/a2/key_phrases/kp_source_sentence_ja.json"))
        self.assertFalse(os.path.exists(f"{out}/b1b/key_phrases/{xr.KP_PART1_FAILED_MARKER}"))

    def test_input_never_contains_gloss_quote_or_display_phrase(self):
        work, src, out = _x_setup()
        fn = make_call_fn()
        _scaffold(src, out, ("b1b",), fn)
        sent = fn.calls[0]
        for it in X_ITEMS:
            self.assertNotIn(it["japanese_gloss"], sent)
            self.assertNotIn(it["source_sentence"], sent)
        self.assertNotIn("catch her breath", sent)                              # display_phrase(本文表層形)は渡さない

    def test_part1_failure_uses_dedicated_marker_not_kp_failure(self):
        work, src, out = _x_setup()
        fn = make_call_fn(lambda prompt: "壊れた出力")
        res, _ = _scaffold(src, out, ("b1b",), fn)
        self.assertEqual(len(fn.calls), 2)                                      # 技術retry1回のみ
        self.assertTrue(res["b1b"]["part1_stage_status"].startswith("KP_PART1_FAILED("))
        self.assertNotIn("kp_stage_status", res["b1b"])                         # KP失敗statusは使わない
        kp_dir = f"{out}/b1b/key_phrases"
        self.assertTrue(os.path.exists(f"{kp_dir}/{xr.KP_PART1_FAILED_MARKER}"))
        self.assertFalse(os.path.exists(f"{kp_dir}/{xr.KP_STAGE_FAILED_MARKER}"))
        self.assertFalse(os.path.exists(f"{kp_dir}/kp_general_explanations.json"))
        self.assertIn("--stage study_text", json.load(open(f"{kp_dir}/{xr.KP_PART1_FAILED_MARKER}", encoding="utf-8"))["next_command"])

    def test_kp_failure_does_not_run_part1(self):
        work, src, out = _x_setup()
        fn = make_call_fn()
        bad = {"selection": {}, "canonicalization": {"status": "CANONICALIZATION_INVALID"}}
        with mock.patch.object(_kpw, "run_kp_with_review", return_value=bad), \
             mock.patch.object(xr.plan, "split_family_x_article_text_v2", return_value={"status": "OK", "paragraph_count": 4}), \
             mock.patch.object(xr, "run_family_x_b1_scaffold", return_value={}), contextlib.redirect_stdout(io.StringIO()):
            res = xr.run_theme_scaffold(None, src, out, ["b1b"], part1_call_fn=fn)
        self.assertEqual(fn.calls, [])
        self.assertTrue(res["b1b"]["kp_stage_status"].startswith("KP_STAGE_FAILED("))


class XPart1MainTests(Tmp, unittest.TestCase):
    def setUp(self):
        self._cwd = os.getcwd()
        self.addCleanup(os.chdir, self._cwd)
        no_decision_record(self)

    def _main(self, work, out, stage, *, client=None, extra=()):
        os.chdir(work)
        argv = ["x", "--slug", "t", "--run", "r", "--out-dir", out, "--stage", stage, "--level", "b1b", *extra]
        tts, asm = mock.Mock(), mock.Mock()
        patches = [mock.patch.object(sys, "argv", argv),
                   mock.patch.object(xr, "generate_family_x_b1_segments", tts),
                   mock.patch.object(xr, "stage_assemble_family_x_b1", asm),
                   mock.patch.object(xr, "assert_production_tts_backend"),
                   mock.patch.object(xr, "ensure_rf_record"),
                   mock.patch.object(xr, "assert_budget_ok"),
                   mock.patch.object(xr, "compute_cost_jpy_so_far", return_value=(0.0, {})),
                   mock.patch.object(_kpw, "run_kp_with_review", side_effect=_kp_writer(out)),
                   mock.patch.object(xr.plan, "split_family_x_article_text_v2", return_value={"status": "OK", "paragraph_count": 4}),
                   mock.patch.object(xr, "run_family_x_b1_scaffold", return_value={}),
                   mock.patch("er003_v1_en_direct_vfl_01_generate.get_client", return_value=client)]
        rc, buf = None, io.StringIO()
        with contextlib.ExitStack() as es:
            for p in patches:
                es.enter_context(p)
            es.enter_context(contextlib.redirect_stdout(buf))
            try:
                xr.main()
            except SystemExit as e:
                rc = e.code
        return rc, tts, asm, buf.getvalue()

    def test_scaffold_part1_failure_rc3_message_points_to_study_text_not_scaffold_and_blocks_tts(self):
        work, src, out = _x_setup()
        bad_client = FakeClient(lambda prompt: "壊れた出力")
        rc, tts, asm, log = self._main(work, out, "all", client=bad_client, extra=("--allow-legacy-backend",))
        self.assertEqual(rc, 3)
        self.assertIn("--stage study_text", log)
        self.assertIn("scaffold stageの再実行はしないでください", log)
        tts.assert_not_called()
        ep = json.load(open(f"{out}/entry_point.json", encoding="utf-8"))
        self.assertIn("part1_stage_status", ep)
        self.assertNotIn("kp_stage_status", ep)
        # markerが残る間はtts/assembleも止まる(Part 1なしで進めない)
        for stage in ("tts", "assemble"):
            rc, tts, asm, log = self._main(work, out, stage, client=bad_client)
            self.assertEqual(rc, 3)
            tts.assert_not_called()
            asm.assert_not_called()

    def test_study_text_stage_recovers_without_scaffold_rerun_then_marker_removed(self):
        work, src, out = _x_setup()
        rc, *_ = self._main(work, out, "scaffold", client=FakeClient(lambda prompt: "壊れた出力"))
        self.assertEqual(rc, 3)
        good = FakeClient()
        with mock.patch.object(_kpw, "run_kp_with_review", side_effect=AssertionError("KP再選定してはいけない")):
            rc, tts, asm, log = self._main(work, out, "study_text", client=good)
        self.assertIsNone(rc, log)
        self.assertEqual(len(good.calls), 2)                                     # Part 1: 解説1 call+訳1 call(独立)
        self.assertEqual(good.calls[0]["model"], "gpt-6-luna")
        self.assertFalse(os.path.exists(f"{out}/b1b/key_phrases/{xr.KP_PART1_FAILED_MARKER}"))
        self.assertTrue(os.path.exists(f"{out}/b1b/study_text/part1_vocabulary_expressions.json"))
        # 再実行はsignature一致でAPI 0。保存済みファイル(生成時のaudit)は書き換えない
        before_bytes = open(f"{out}/b1b/key_phrases/kp_general_explanations.json", "rb").read()
        again = FakeClient()
        rc, *_ = self._main(work, out, "study_text", client=again)
        self.assertIsNone(rc)
        self.assertEqual(again.calls, [])
        self.assertEqual(before_bytes, open(f"{out}/b1b/key_phrases/kp_general_explanations.json", "rb").read())

    def test_study_text_stage_requires_kp_pass_no_kp_failed_marker(self):
        work, src, out = _x_setup()
        os.makedirs(f"{out}/b1b/key_phrases")
        open(f"{out}/b1b/key_phrases/{xr.KP_STAGE_FAILED_MARKER}", "w").write("{}")
        _kp_writer(out)(XARTICLE, f"{out}/b1b/key_phrases", "a", "b1b")
        c = FakeClient()
        rc, _t, _a, log = self._main(work, out, "study_text", client=c)
        self.assertEqual(rc, 3)
        self.assertEqual(c.calls, [])
        # KP成果物なしもSTOP
        work2, src2, out2 = _x_setup()
        rc, _t, _a, log = self._main(work2, out2, "study_text", client=FakeClient())
        self.assertEqual(rc, 3)

    def test_tts_assemble_player_entrances_stop_when_part1_missing_or_stale(self):
        work, src, out = _x_setup()
        _kp_writer(out)(XARTICLE, f"{out}/b1b/key_phrases", "a", "b1b")          # KPはあるがPart 1が無い(導入前runの再開を模擬)
        for stage in ("tts", "assemble", "player"):
            rc, tts, asm, log = self._main(work, out, stage, client=FakeClient())
            self.assertEqual(rc, 3, stage)
            self.assertIn("KP_PART1_NOT_READY", log)
            self.assertIn("--stage study_text", log)
            tts.assert_not_called()
            asm.assert_not_called()
        # 生成後はtts入口を通る。KP表現が変わるとSTALEでSTOP(次コマンド付き)
        rc, *_ = self._main(work, out, "study_text", client=FakeClient())
        self.assertIsNone(rc)
        rc, tts, asm, log = self._main(work, out, "tts", client=FakeClient())
        self.assertIsNone(rc, log)
        tts.assert_called()
        items = json.load(open(f"{out}/b1b/key_phrases/keywords_canonicalized.json", encoding="utf-8"))
        items["items"][0]["used_form"] = "give up"
        json.dump(items, open(f"{out}/b1b/key_phrases/keywords_canonicalized.json", "w", encoding="utf-8"), ensure_ascii=False)
        rc, tts, asm, log = self._main(work, out, "tts", client=FakeClient())
        self.assertEqual(rc, 3)
        self.assertIn("EXPLANATIONS_STALE", log)
        tts.assert_not_called()

    def test_x_regenerates_automatically_when_expression_changes_via_study_text(self):
        work, src, out = _x_setup()
        _kp_writer(out)(XARTICLE, f"{out}/b1b/key_phrases", "a", "b1b")
        c1 = FakeClient()
        self._main(work, out, "study_text", client=c1)
        items = json.load(open(f"{out}/b1b/key_phrases/keywords_canonicalized.json", encoding="utf-8"))
        items["items"][1]["used_form"] = "on short notice"
        json.dump(items, open(f"{out}/b1b/key_phrases/keywords_canonicalized.json", "w", encoding="utf-8"), ensure_ascii=False)
        c2 = FakeClient()
        rc, *_ = self._main(work, out, "study_text", client=c2)
        self.assertIsNone(rc)
        self.assertEqual(len(c2.calls), 1)                                       # Xは自動再生成(Zは明示再生成STOP)。引用英文は不変なので訳は再利用(API 0)
        doc = json.load(open(f"{out}/b1b/key_phrases/kp_general_explanations.json", encoding="utf-8"))
        self.assertEqual(doc["phrases"][1], "on short notice")

    def test_player_has_no_study_block_without_decision_and_default_html_is_unchanged(self):
        work, src, out = _x_setup()
        _kp_writer(out)(XARTICLE, f"{out}/b1b/key_phrases", "a", "b1b")
        self._main(work, out, "study_text", client=FakeClient())
        self.assertEqual(xr.part1_study_html_for_player(src, out), "")
        base = open(xr.build_player_html(out, "t", None), encoding="utf-8").read()
        self.assertEqual(base, open(xr.build_player_html(out, "t", None, study_html=""), encoding="utf-8").read())
        self.assertNotIn("Vocabulary", base)

    def test_player_renders_study_block_in_advanced_section_after_decision(self):
        decision_record(self, "T2")
        work, src, out = _x_setup()
        _kp_writer(out)(XARTICLE, f"{out}/b1b/key_phrases", "a", "b1b")
        self._main(work, out, "study_text", client=FakeClient())
        html_block = xr.part1_study_html_for_player(src, out)
        self.assertIn("Vocabulary &amp; Expressions", html_block)
        page = open(xr.build_player_html(out, "t", None, study_html=html_block), encoding="utf-8").read()
        self.assertLess(page.index("Advanced(B1)"), page.index("<section class='study'>"))
        self.assertLess(page.index("<section class='study'>"), page.index("Standard(A2)"))


class OtherFamiliesUnchangedTests(unittest.TestCase):
    def test_other_families_do_not_import_or_call_part1(self):
        for fn in ("er019_family_x_entertainment_production_runner_01.py", "er003_v1_n3_01_scaffold_generate.py",
                   "er110_family_y_audio_page_01.py"):
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), fn)
            if os.path.exists(path):
                self.assertNotIn("kp_general_explanation", open(path, encoding="utf-8").read(), fn)

    def test_strategy_l_kp_items_are_rejected_as_part1_input(self):
        legacy = [{"rank": 1, "display_phrase": "gave way", "used_form": "give way", "source_sentence": QUOTE1, "japanese_gloss": "x"}]
        with self.assertRaises(p1.KpGeneralExplanationInputError):
            p1.phrases_signature(legacy)


if __name__ == "__main__":
    unittest.main()
