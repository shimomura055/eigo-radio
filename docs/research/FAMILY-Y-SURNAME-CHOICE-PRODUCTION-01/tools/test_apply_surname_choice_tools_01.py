# -*- coding: utf-8 -*-
"""apply_v1_intro_patch_01.py / apply_user_decision_surname_choice_02.py の拒否経路・復元経路のunit test(API 0・run_02本体に触れない)。

実行: .venv\\Scripts\\python.exe -m unittest docs/research/FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01/tools/test_apply_surname_choice_tools_01.py -v
  (または .venv\\Scripts\\python.exe docs\\research\\FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01\\tools\\test_apply_surname_choice_tools_01.py)
全てtmp dir上の合成fileで行う(TARGETSの定数は各testで合成fileに差替えて元へ戻す)。
"""
from __future__ import annotations

import copy
import json
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import apply_v1_intro_patch_01 as A  # noqa: E402
import apply_user_decision_surname_choice_02 as B  # noqa: E402

# 合成記事(15行構造ではなく、split_y_articleが読める最小の5段落)
JA = ("# タイトル\n\nリード文。\n\n{intro1}\nVoice1の本文だ。\n\n次は、別の人。\nVoice2の本文だ。\n\n最後は、また別の人。\nVoice3の本文だ。\n\nクロージング。\n")
INTRO_OLD, INTRO_NEW = "旧紹介。", "新紹介。"


def _sha(b: bytes) -> str:
    return A._sha_bytes(b)


class _Patched:
    """TARGETSを合成fileに差替える(終了時に元へ戻す)。"""

    def __init__(self, tmp: str, n_lines_delta: int = 0, old_sha_override: str = None, old_line_override: str = None, new_sha_override: str = None):
        self.tmp, self.saved = tmp, (copy.deepcopy(A.TARGETS), dict(A.NEW_FILE_SHA))
        text = JA.format(intro1=INTRO_OLD)
        os.makedirs(os.path.join(tmp, "text"), exist_ok=True)
        path = os.path.join(tmp, "text", "article_ja.md")
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        lines = text.split("\n")
        line_no = [i for i, ln in enumerate(lines, 1) if ln == INTRO_OLD][0]
        new_text = text.replace(INTRO_OLD, INTRO_NEW)
        A.TARGETS[:] = [{"rel": "text/article_ja.md", "old_sha": old_sha_override or _sha(text.encode("utf-8")), "line_no": line_no, "n_lines": len(lines) + n_lines_delta,
                         "old": old_line_override or INTRO_OLD, "new": INTRO_NEW, "ends_nl": True}]
        A.NEW_FILE_SHA.clear()
        A.NEW_FILE_SHA["text/article_ja.md"] = new_sha_override or _sha(new_text.encode("utf-8"))
        # intros_final.json の意味検査はbuild_patchedが固定relを参照するため、このtestでは呼ばない部分(build_patchedはJSON検査を行うので別関数で検査)
        self.text, self.new_text = text, new_text

    def __enter__(self):
        return self

    def __exit__(self, *a):
        A.TARGETS[:], saved_sha = self.saved[0], self.saved[1]
        A.NEW_FILE_SHA.clear()
        A.NEW_FILE_SHA.update(saved_sha)


def build_only_text(tmp):
    """build_patchedのうちJSON意味検査(intros_final.json固定)を除いた、target検査部分だけを実行する(合成fileにはintros_final.jsonが無いため)。"""
    try:
        return A.build_patched(tmp)
    except KeyError:
        raise
    except A.ToolRefused:
        raise


class TestBuildPatchedRefusals(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="v1patch_test_")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _expect_refusal(self, fragment, **kw):
        with _Patched(self.tmp, **kw):
            with self.assertRaises(A.ToolRefused) as cm:
                A.build_patched(self.tmp)
            self.assertIn(fragment, str(cm.exception))

    def test_refuses_old_file_sha_mismatch(self):
        self._expect_refusal("旧file sha", old_sha_override="0" * 64)

    def test_refuses_line_count_mismatch(self):
        self._expect_refusal("行数が定数と一致しません", n_lines_delta=1)

    def test_refuses_old_line_mismatch(self):
        self._expect_refusal("旧行と逐語一致しません", old_line_override="別の行。")

    def test_refuses_missing_target_file(self):
        with _Patched(self.tmp):
            os.remove(os.path.join(self.tmp, "text", "article_ja.md"))
            with self.assertRaises(A.ToolRefused) as cm:
                A.build_patched(self.tmp)
            self.assertIn("対象fileがありません", str(cm.exception))

    def test_refuses_new_file_sha_constant_mismatch(self):
        # 差替え後のfile sha定数が違えば、JSON意味検査の前に拒否(合成fileにはintros_final.jsonが無いので、sha定数検査の例外だけ確認する)
        with _Patched(self.tmp, new_sha_override="1" * 64):
            with self.assertRaises(A.ToolRefused) as cm:
                A.build_patched(self.tmp)
            self.assertIn("差替え後のfile shaが定数と一致しません", str(cm.exception))

    def test_refuses_crlf(self):
        with _Patched(self.tmp):
            p = os.path.join(self.tmp, "text", "article_ja.md")
            raw = open(p, "rb").read().replace(b"\n", b"\r\n")
            open(p, "wb").write(raw)
            A.TARGETS[0]["old_sha"] = _sha(raw)
            with self.assertRaises(A.ToolRefused) as cm:
                A.build_patched(self.tmp)
            self.assertIn("CR文字", str(cm.exception))


class TestConstants(unittest.TestCase):
    def test_targets_are_five_files_with_one_line_each(self):
        self.assertEqual([t["rel"] for t in A.TARGETS],
                         ["text/article_ja.md", "text/article_assembled.md", "text/lead_intro/intros_final.json", "translate/b1b.md", "translate/a2.md"])
        for t in A.TARGETS:
            self.assertEqual(len(t["old_sha"]), 64)
            self.assertNotEqual(t["old"], t["new"])
            self.assertTrue(1 <= t["line_no"] <= t["n_lines"])

    def test_fixed_english_line_is_article_typography_and_a2_has_two_trailing_spaces(self):
        self.assertIn("’", A.EN_NEW)               # U+2019(記事表記)
        self.assertNotIn("'", A.EN_NEW)
        self.assertFalse(A.EN_NEW.endswith(" "))
        self.assertTrue(A.EN_NEW_A2.endswith("  ") and not A.EN_NEW_A2.endswith("   "))
        self.assertNotIn("father", A.EN_NEW.lower())
        self.assertNotIn("父親", A.JA_NEW)

    def test_declared_sets(self):
        self.assertEqual(set(A.DECLARED_STALE), {"tts_b1b", "tts_a2"})          # M1: ttsは付替えずstale化
        self.assertTrue(set(A.DECLARED_CHANGED).isdisjoint(A.DECLARED_STALE))
        self.assertIn("kp_b1b", A.DECLARED_CHANGED)

    def test_split3_keeps_sentence_count_of_old_a2_line(self):
        import re
        n = lambda s: len([x for x in re.split(r"(?<=[.!?])\s+", s.strip()) if x])  # noqa: E731
        self.assertEqual(n(A.EN_A2_OLD), 3)
        self.assertEqual(n(A.EN_NEW_A2_SPLIT3), 3)      # 文番号S<n>がずれない
        self.assertEqual(n(A.EN_NEW_A2), 2)             # fixed2は文番号が1つずれる(ハイライトGateでSTOP=リハーサルで実測)


class TestStdVariant(unittest.TestCase):
    def tearDown(self):
        A.set_std_variant("fixed2")

    def test_switching_variant_updates_target_and_sha_constant(self):
        A.set_std_variant("split3")
        a2 = [t for t in A.TARGETS if t["rel"] == "translate/a2.md"][0]
        self.assertEqual(a2["new"], A.EN_NEW_A2_SPLIT3)
        self.assertEqual(A.NEW_FILE_SHA["translate/a2.md"], A.STD_VARIANT_NEW_SHA["split3"])
        A.set_std_variant("fixed2")
        self.assertEqual(a2["new"], A.STD_VARIANTS["fixed2"])
        self.assertEqual(A.NEW_FILE_SHA["translate/a2.md"], A.STD_VARIANT_NEW_SHA["fixed2"])

    def test_unknown_variant_is_refused(self):
        with self.assertRaises(A.ToolRefused):
            A.set_std_variant("free_text")


class TestDeclaredSet(unittest.TestCase):
    def test_exact_declared_set_passes(self):
        A.check_declared(set(A.DECLARED_CHANGED))

    def test_missing_entry_is_refused(self):
        with self.assertRaises(A.ToolRefused):
            A.check_declared(set(A.DECLARED_CHANGED) - {"support_a2"})

    def test_extra_entry_is_refused(self):
        with self.assertRaises(A.ToolRefused):
            A.check_declared(set(A.DECLARED_CHANGED) | {"kp_expl_b1b"})


class TestInvariants(unittest.TestCase):
    def _patched(self, old_en, new_en):
        mk = lambda t: {"old_text": t[0], "new_text": t[1]}  # noqa: E731
        ja_o, ja_n = JA.format(intro1=INTRO_OLD), JA.format(intro1=INTRO_NEW)
        return {"text/article_ja.md": mk((ja_o, ja_n)), "text/article_assembled.md": mk((ja_o, ja_n)),
                "translate/b1b.md": mk((old_en, new_en)), "translate/a2.md": mk((old_en, new_en))}

    EN = "# Title\n\nLead.\n\n{i}\nVoice one.\n\nNext intro.\nVoice two.\n\nLast intro.\nVoice three.\n\nClosing.\n"

    def test_voice_body_change_is_refused(self):
        old = self.EN.format(i="Old intro.")
        new = self.EN.format(i="New intro.").replace("Voice one.", "Voice ONE changed.")
        with self.assertRaises(A.ToolRefused) as cm:
            A.check_article_invariants(self._patched(old, new), tempfile.gettempdir())
        self.assertIn("Voice1本文", str(cm.exception))

    def test_other_intro_change_is_refused(self):
        old = self.EN.format(i="Old intro.")
        new = self.EN.format(i="New intro.").replace("Next intro.", "Changed next intro.")
        with self.assertRaises(A.ToolRefused) as cm:
            A.check_article_invariants(self._patched(old, new), tempfile.gettempdir())
        self.assertIn("V2/V3紹介", str(cm.exception))

    def test_unchanged_v1_intro_is_refused(self):
        old = self.EN.format(i="Same intro.")
        with self.assertRaises(A.ToolRefused) as cm:
            A.check_article_invariants(self._patched(old, old), tempfile.gettempdir())
        self.assertIn("V1紹介が変わっていません", str(cm.exception))

    def test_support_with_father_is_refused(self):
        tmp = tempfile.mkdtemp(prefix="v1patch_sup_")
        try:
            os.makedirs(os.path.join(tmp, "support"))
            for lv in A.LEVELS:
                with open(os.path.join(tmp, "support", f"{lv}_support.json"), "w", encoding="utf-8") as f:
                    json.dump({"preview": "A father speaks." if lv == "b1b" else "ok"}, f)
            old, new = self.EN.format(i="Old intro."), self.EN.format(i="New intro.")
            with self.assertRaises(A.ToolRefused) as cm:
                A.check_article_invariants(self._patched(old, new), tmp)
            self.assertIn("father", str(cm.exception))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TestBackupRestoreAndManifest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="v1patch_bk_")
        self.run = os.path.join(self.tmp, "run")
        os.makedirs(os.path.join(self.run, "text"))
        os.makedirs(os.path.join(self.run, "key_phrases", "b1b"))
        os.makedirs(os.path.join(self.run, "b1b", "assembled"))
        self.files = {"text/a.md": b"A", "key_phrases/b1b/k.json": b"{}", "provenance.json": b"{\"x\":1}", "b1b/assembled/x.wav": b"WAV"}
        for rel, data in self.files.items():
            with open(os.path.join(self.run, rel), "wb") as f:
                f.write(data)
        self.saved = (A.MUTABLE_SUBTREES, A.MUTABLE_FILES)
        A.MUTABLE_SUBTREES = ("text", "key_phrases")
        A.MUTABLE_FILES = ("provenance.json",)

    def tearDown(self):
        A.MUTABLE_SUBTREES, A.MUTABLE_FILES = self.saved
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_restore_reverts_changes_and_removes_new_files_in_mutable_area(self):
        bk = os.path.join(self.tmp, "bk")
        man = A.backup_run(self.run, bk)
        self.assertEqual(set(man), {"text/a.md", "key_phrases/b1b/k.json", "provenance.json"})      # wavは退避対象外
        # 破壊: 変更・追加・削除
        open(os.path.join(self.run, "text", "a.md"), "wb").write(b"CHANGED")
        open(os.path.join(self.run, "text", "new.md"), "wb").write(b"NEW")
        os.remove(os.path.join(self.run, "key_phrases", "b1b", "k.json"))
        open(os.path.join(self.run, "provenance.json"), "wb").write(b"BROKEN")
        A.restore_run(self.run, bk)
        for rel in ("text/a.md", "key_phrases/b1b/k.json", "provenance.json"):
            self.assertEqual(open(os.path.join(self.run, rel), "rb").read(), self.files[rel])
        self.assertFalse(os.path.exists(os.path.join(self.run, "text", "new.md")))

    def test_manifest_flags_changes_outside_mutable_area(self):
        before = A.tree_manifest(self.run)
        open(os.path.join(self.run, "b1b", "assembled", "x.wav"), "wb").write(b"OTHER")
        open(os.path.join(self.run, "text", "a.md"), "wb").write(b"CHANGED")
        after = A.tree_manifest(self.run)
        changed = sorted(r for r in set(before) | set(after) if before.get(r) != after.get(r))
        outside = [r for r in changed if not A._in_mutable(r)]
        self.assertEqual(outside, ["b1b/assembled/x.wav"])
        self.assertIn("text/a.md", changed)

    def test_atomic_write_replaces_without_leftover_tmp(self):
        p = os.path.join(self.run, "text", "a.md")
        A._write_atomic(p, b"NEWDATA")
        self.assertEqual(open(p, "rb").read(), b"NEWDATA")
        self.assertEqual([n for n in os.listdir(os.path.join(self.run, "text")) if n.startswith(".tmp_v1patch_")], [])


class TestJsonEqualIgnoringSha(unittest.TestCase):
    def test_ignores_sha_signature_and_timestamps_only(self):
        a = json.dumps({"x": 1, "text_sha256": "a", "selection_signature": "s1", "finalized_at": "t1", "items": [{"k": "v", "candidates_sha256": "c1"}]}).encode()
        b = json.dumps({"x": 1, "text_sha256": "b", "selection_signature": "s2", "finalized_at": "t2", "items": [{"k": "v", "candidates_sha256": "c2"}]}).encode()
        self.assertEqual(A._json_equal_ignoring_sha(a, b), (True, []))

    def test_detects_content_difference(self):
        a = json.dumps({"items": [{"used_form": "taking offense"}]}).encode()
        b = json.dumps({"items": [{"used_form": "take offense"}]}).encode()
        ok, diffs = A._json_equal_ignoring_sha(a, b)
        self.assertFalse(ok)
        self.assertEqual(diffs, ["/items[0]/used_form"])


class TestNoApiClient(unittest.TestCase):
    def test_any_attribute_access_raises(self):
        c = A._NoApiClient()
        with self.assertRaises(RuntimeError):
            c.chat


class TestToolBGuards(unittest.TestCase):
    def _cand(self, **over):
        item = {"rank": 1, "source_span": "taking offense", "display_phrase": "taking offense", "key_phrase": "taking offense", "used_form": "taking offense",
                "source_sentence": "I was grateful that both sets of parents accepted my decision without taking offense", "normalization_reason": "none",
                "person_role_repair": {"role_ok_poss": []}}
        item.update(over.pop("item_over", {}))
        c = {"candidate_id": "p_85cbe0223d", "selection_phrase": "taking offense", "used_form": "taking offense", "item": item, "ai_rank": 1}
        c.update(over)
        return c

    TEXT = "I was grateful that both sets of parents accepted my decision without taking offense. Other sentence."

    def test_rule7_is_exempted_only_for_closed_pair(self):
        dg = B.deterministic_gates(self._cand(), self.TEXT, [])
        self.assertIsNotNone(dg["exemption"])
        self.assertEqual(dg["exemption"]["pair"], ["taking offense", "take offense"])
        self.assertEqual(dg["item"]["used_form"], "take offense")
        self.assertEqual(dg["item"]["display_phrase"], "taking offense")
        self.assertEqual(dg["item"]["source_span"], "taking offense")
        self.assertTrue(dg["item"]["changed_from_display_phrase"])

    def test_refuses_other_candidate_id(self):
        with self.assertRaises(B.ToolRefused):
            B.deterministic_gates(self._cand(candidate_id="p_other"), self.TEXT, [])

    def test_refuses_when_display_phrase_differs(self):
        with self.assertRaises(B.ToolRefused):
            B.deterministic_gates(self._cand(item_over={"display_phrase": "taking offence", "source_span": "taking offence"}), self.TEXT, [])

    def test_refuses_when_surface_not_in_text(self):
        with self.assertRaises(B.ToolRefused):
            B.deterministic_gates(self._cand(), "No such phrase here.", [])

    def test_patched_payload_changes_only_the_target_term(self):
        src = {"article": {"candidates_sha256": "old", "text_sha256": "oldt"},
               "selection": {"key_phrase": [{"candidate_id": "p_85cbe0223d", "term": "taking offense"}, {"candidate_id": "p_x", "term": "adopted"}],
                             "extra_explanation": [], "meaning_display": []}}
        out = B.patched_payload(src, {"candidates_sha256": "new"}, text_sha="newt")
        dd = B.diff_payloads(src, out)
        self.assertEqual(sorted(dd), ["/article/candidates_sha256", "/article/text_sha256", "/selection/key_phrase[0]/term"])
        self.assertTrue(all(B.ALLOWED_DIFFS.match(d) for d in dd))

    def test_patched_payload_refuses_wrong_old_term_and_duplicates(self):
        base = {"article": {}, "selection": {"key_phrase": [{"candidate_id": "p_85cbe0223d", "term": "taking offence"}], "extra_explanation": [], "meaning_display": []}}
        with self.assertRaises(B.ToolRefused):
            B.patched_payload(base, None, text_sha="t")
        dup = {"article": {}, "selection": {"key_phrase": [{"candidate_id": "p_85cbe0223d", "term": "taking offense"}],
                                            "extra_explanation": [{"candidate_id": "p_85cbe0223d", "term": "taking offense"}], "meaning_display": []}}
        with self.assertRaises(B.ToolRefused):
            B.patched_payload(dup, None, text_sha="t")
        none = {"article": {}, "selection": {"key_phrase": [], "extra_explanation": [], "meaning_display": []}}
        with self.assertRaises(B.ToolRefused):
            B.patched_payload(none, None, text_sha="t")

    def test_allowed_diff_set_rejects_other_paths(self):
        self.assertIsNone(B.ALLOWED_DIFFS.match("/selection/key_phrase[1]/term"))
        self.assertIsNone(B.ALLOWED_DIFFS.match("/selection/key_phrase[0]/ja_gloss"))
        self.assertIsNone(B.ALLOWED_DIFFS.match("/comment"))

    def test_regen_sequence_constants(self):
        self.assertEqual(B.REGEN_SEQUENCE, ("kp_expl_b1b", "kp_part1_b1b", "part2_b1b"))      # 単一regen制約に合わせて順に実行
        self.assertEqual((B.OLD_FORM, B.NEW_FORM, B.CAND_ID), ("taking offense", "take offense", "p_85cbe0223d"))

    def test_user_ref_constants_are_shared_and_pinned(self):
        self.assertEqual(B.USER_REF_SHA256, A.USER_REF_SHA256)
        self.assertEqual(len(B.SOURCE_PAYLOAD_SHA256), 64)


class TestCliRefusals(unittest.TestCase):
    def test_apply_requires_by(self):
        self.assertEqual(A.main(["--rehearsal-dir", os.path.join(tempfile.gettempdir(), "no_such_root_zzz")]), 2)

    def test_missing_run_dir_is_refused(self):
        self.assertEqual(A.main(["--dry-run", "--rehearsal-dir", os.path.join(tempfile.gettempdir(), "no_such_root_zzz")]), 2)
        self.assertEqual(B.main(["dry-run", "--by", "x", "--rehearsal-dir", os.path.join(tempfile.gettempdir(), "no_such_root_zzz")]), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
