# -*- coding: utf-8 -*-
"""END-USER-LISTENING-PAGE-PRODUCTION-WIRING-01 委任_03 WP-E: runner hook・一括生成・未実装ゲート§6-2(4)(5)・公開copy補助のtest(API 0)。

 H1 hook存在/配置: X `main`が`build_enduser_after_page`を呼ぶ・Y/Zの`stage_page_verify`は既存検査(raise)の後、Yはfinal manifestの前に`_build_enduser_page`を呼ぶ。
 H2 失敗時: X rc=5でdev index.html不変+既存enduser/不変 / Y・Zは`YE2EStop`/`FamilyZE2EStop`(メッセージが`ENDUSER_*`で始まる)。
 H3 Y manifest: `final_manifest.json`の`enduser`にenduser/のfile shaとdev_index_sha256が入る。
 H4 episode_checks: 一致=PASS / 位置ずれ(>0.05s)=ENDUSER_EPISODE_OFFSET / 全編長差(>0.15s)=ENDUSER_EPISODE_LENGTH。
 H5 publish_copy: enduser/だけcopyしdev index.html・音声は不変 / 公開dirのdevが違えばstale検出 / 失敗時に既存enduser/が残る。
 H6 produce: 同期は`sync_level`のみ(API 0)で、runnerが渡す引数にtts_textを含めない。"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import er135_enduser_page_01 as E  # noqa: E402


def _src(name):
    return (ROOT / name).read_text(encoding="utf-8")


def _func_src(src, name):
    tree = ast.parse(src)
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name == name:
            return ast.get_source_segment(src, n)
    raise AssertionError(name)


class H1_HookPlacement(unittest.TestCase):
    def test_x_main_calls_hook_after_page_written(self):
        body = _func_src(_src("er019_family_x_listening_page_01.py"), "main")
        self.assertLess(body.index("build_page("), body.index("build_enduser_after_page("))
        self.assertIn("return build_enduser_after_page(", body)

    def test_y_hook_between_existing_checks_and_manifest(self):
        body = _func_src(_src("er121_family_y_runner_01.py"), "stage_page_verify")
        i_viol = body.index("FAMILY_Y_PAGE_VERIFY_FAILED")
        i_hook = body.index("_build_enduser_page(ctx)")
        i_man = body.index("write_final_manifest(ctx)")
        self.assertLess(i_viol, i_hook)
        self.assertLess(i_hook, i_man)
        for needed in ("evaluate_page_verify(", "_verify_part2_outputs(", "_verify_kp_selection(", "_verify_highlights_on_page("):
            self.assertLess(body.index(needed), i_hook, needed)

    def test_z_hook_after_all_existing_checks(self):
        body = _func_src(_src("er026_family_z_fiction_production_runner_01.py"), "stage_page_verify")
        i_hook = body.index("_build_enduser_page(ctx)")
        self.assertLess(body.index("FAMILY_Z_PAGE_VERIFY_LOCAL_NG"), i_hook)
        for needed in ("_verify_part2_outputs(", "_verify_learning_items(", "verify_selection_matches_outputs("):
            self.assertLess(body.index(needed), i_hook, needed)

    def test_y_and_z_hooks_use_run_scoped_cache_not_public_dir(self):
        for fn, name in (("er121_family_y_runner_01.py", "_build_enduser_page"), ("er026_family_z_fiction_production_runner_01.py", "_build_enduser_page")):
            b = _func_src(_src(fn), name)
            self.assertIn("ctx.out_dir}/enduser_sync_cache", b)
            self.assertNotIn("cache_dir=f\"{ctx.pages_dir}", b)

    def test_no_new_stage_name(self):
        """新stage名を足さない(Z完成段 provision_shell,gate,assemble,pages,page_verify の1起動運用=RESTART_STORM回避)。"""
        self.assertNotIn("enduser", _src("er121_family_y_runner_01.py").split("STAGES")[1].split("\n")[0].lower())
        z = _src("er026_family_z_fiction_production_runner_01.py")
        self.assertNotIn('"enduser"', z.split("E2E_STAGES")[1][:300])


class H2_FailureKeepsDevAndOldEnduser(unittest.TestCase):
    def test_x_failure_rc5_and_dev_unchanged(self):
        import er019_family_x_listening_page_01 as X
        with tempfile.TemporaryDirectory() as td:
            web = Path(td)
            (web / "index.html").write_bytes(b"<html>dev</html>")
            (web / "enduser").mkdir()
            (web / "enduser" / "old.txt").write_text("old")
            before = (hashlib.sha256((web / "index.html").read_bytes()).hexdigest(), (web / "enduser" / "old.txt").read_text())
            with mock.patch.object(E, "hook_run", side_effect=E.EnduserPageStop("ENDUSER_SYNC_TOKEN_MATCH", "x")):
                rc = X.build_enduser_after_page("s", "r", str(web), run_root=td, source_root=td)
            self.assertEqual(rc, 5)
            self.assertEqual(before, (hashlib.sha256((web / "index.html").read_bytes()).hexdigest(), (web / "enduser" / "old.txt").read_text()))

    def test_x_success_rc0(self):
        import er019_family_x_listening_page_01 as X
        fake = {"enduser_dir": "d", "consistency": "ok", "total_wall_s": 1.0, "api_calls": 0}
        with mock.patch.object(E, "hook_run", return_value=fake) as m:
            rc = X.build_enduser_after_page("s", "r", "web", run_root="rr", source_root="ss")
        self.assertEqual(rc, 0)
        kw = m.call_args.kwargs
        self.assertEqual(kw["run_dir"], "rr/s__r")
        self.assertEqual(kw["cache_dir"], "rr/s__r/enduser_sync_cache")
        self.assertTrue(kw["result_json"].endswith("enduser_page_result.json"))

    def test_y_failure_is_ye2estop_with_code(self):
        import er121_family_y_runner_01 as Y
        ctx = mock.Mock(pages_dir="p", out_dir="o", mode="real")
        with mock.patch.object(Y, "_ja_path", return_value="ja.md"), mock.patch.object(E, "hook_run", side_effect=E.EnduserPageStop("ENDUSER_EPISODE_OFFSET", "m")):
            with self.assertRaises(Y.YE2EStop) as cm:
                Y._build_enduser_page(ctx)
        self.assertTrue(str(cm.exception).startswith("ENDUSER_EPISODE_OFFSET"))

    def test_z_failure_is_stop_with_code(self):
        import er026_family_z_fiction_production_runner_01 as Z
        ctx = mock.Mock(pages_dir="p", out_dir="o", mode="real")
        with mock.patch.object(E, "hook_run", side_effect=E.EnduserPageStop("ENDUSER_SYNC_GATE", "m")):
            with self.assertRaises(Z.FamilyZE2EStop) as cm:
                Z._build_enduser_page(ctx)
        self.assertTrue(str(cm.exception).startswith("ENDUSER_SYNC_GATE"))

    def test_mock_and_dryrun_skip_enduser_but_real_never_skips(self):
        """mock/dry-run=偽TTS音声でASR同期は成立しないためhookをskipして記録する。real(正式Production)は必ず生成(skipできる引数・flagは無い)。"""
        import er121_family_y_runner_01 as Y
        import er026_family_z_fiction_production_runner_01 as Z
        for mod, fn in ((Y, Y._build_enduser_page), (Z, Z._build_enduser_page)):
            for mode in ("mock", "dry-run"):
                with mock.patch.object(E, "hook_run", side_effect=AssertionError("must not run")):
                    r = fn(mock.Mock(pages_dir="p", out_dir="o", mode=mode))
                self.assertTrue(r["skipped"])
                self.assertIsNone(r["enduser_dir"])
        for fn_src in (_func_src(_src("er121_family_y_runner_01.py"), "_build_enduser_page"), _func_src(_src("er026_family_z_fiction_production_runner_01.py"), "_build_enduser_page")):
            self.assertEqual(fn_src.count("skipped"), 1)
            self.assertIn('ctx.mode != "real"', fn_src)
            self.assertNotIn("environ", fn_src)           # env等で迂回できない
        with mock.patch.object(E, "hook_run", return_value={"ok": True}) as m:
            Y._build_enduser_page(mock.Mock(pages_dir="p", out_dir="o", mode="real"))
        self.assertEqual(m.call_count, 1)

    def test_y_passes_family_and_ja_article(self):
        import er121_family_y_runner_01 as Y
        ctx = mock.Mock(pages_dir="pages", out_dir="out", mode="real")
        with mock.patch.object(Y, "_ja_path", return_value="ja.md"), mock.patch.object(E, "hook_run", return_value={"ok": True}) as m:
            Y._build_enduser_page(ctx)
        self.assertEqual(m.call_args.args[:2], ("pages", "y"))
        self.assertEqual(m.call_args.kwargs["y_article_ja"], "ja.md")
        self.assertEqual(m.call_args.kwargs["cache_dir"], "out/enduser_sync_cache")


class H3_YManifest(unittest.TestCase):
    def test_enduser_manifest_has_file_shas(self):
        import er121_family_y_runner_01 as Y
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "enduser").mkdir()
            bi = {"dev_index_sha256": "abc", "files": {"index.html": "s1", "data/article.json": "s2"}, "assets": {"app.js": "s3"}, "cost": {"api_calls": 0}}
            (Path(td) / "enduser" / "build_info.json").write_text(json.dumps(bi), encoding="utf-8")
            m = Y._enduser_manifest(mock.Mock(pages_dir=td))
            self.assertEqual(m["dev_index_sha256"], "abc")
            self.assertEqual(m["files"]["data/article.json"], "s2")
            self.assertEqual(m["cost"]["api_calls"], 0)
            self.assertIsNone(Y._enduser_manifest(mock.Mock(pages_dir=td + "_none")))


def _ffmpeg():
    return E._ffmpeg()


def _write_noise_mp3(path, seconds, seed):
    import numpy as np
    rng = np.random.default_rng(seed)
    a = (rng.standard_normal(int(16000 * seconds)) * 0.2).astype("float32")
    wav = str(path) + ".wav"
    import wave
    with wave.open(wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes((np.clip(a, -1, 1) * 32767).astype("<i2").tobytes())
    subprocess.run([_ffmpeg(), "-y", "-loglevel", "error", "-i", wav, "-b:a", "96k", str(path)], check=True)
    os.remove(wav)
    return a


class H4_EpisodeChecks(unittest.TestCase):
    def _build(self, td, shift=0.0, extra_tail=0.0):
        """3 segment(3秒ずつ) -> 全編mp3(連結)。shift秒だけdata-tをずらす/全編末尾にextra_tail秒の無音を足す。"""
        import numpy as np
        td = Path(td)
        segs = [_write_noise_mp3(td / f"s{i}.mp3", 3.0, 10 + i) for i in range(3)]
        full = np.concatenate(segs + [np.zeros(int(16000 * extra_tail), dtype="float32")])
        wav = td / "full.wav"
        import wave
        with wave.open(str(wav), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(16000)
            w.writeframes((np.clip(full, -1, 1) * 32767).astype("<i2").tobytes())
        subprocess.run([_ffmpeg(), "-y", "-loglevel", "error", "-i", str(wav), "-b:a", "128k", str(td / "full.mp3")], check=True)
        probe = E.make_probe(td)
        rows = [{"row_id": f"std_{i}", "audio_rel": f"s{i}.mp3", "data_t": 3.0 * i + shift} for i in range(3)]
        return {"std": rows}, {"level_main": {"std": "full.mp3"}}, probe, td

    def test_pass(self):
        with tempfile.TemporaryDirectory() as td:
            rows, meta, probe, d = self._build(td)
            r = E.episode_checks(d, rows, meta, probe)["std"]
            self.assertEqual(r["rows_checked"], 3)
            self.assertLessEqual(r["max_abs_lag_s"], 0.05)
            self.assertGreaterEqual(r["min_corr"], 0.99)

    def test_offset_violation(self):
        with tempfile.TemporaryDirectory() as td:
            rows, meta, probe, d = self._build(td, shift=0.1)
            with self.assertRaises(E.EnduserPageStop) as cm:
                E.episode_checks(d, rows, meta, probe)
            self.assertEqual(cm.exception.code, "ENDUSER_EPISODE_OFFSET")

    def test_length_violation(self):
        with tempfile.TemporaryDirectory() as td:
            rows, meta, probe, d = self._build(td, extra_tail=0.5)
            with self.assertRaises(E.EnduserPageStop) as cm:
                E.episode_checks(d, rows, meta, probe)
            self.assertEqual(cm.exception.code, "ENDUSER_EPISODE_LENGTH")

    def test_thresholds_are_design_values(self):
        self.assertEqual(E.EPISODE_OFFSET_TOL_S, 0.05)
        self.assertEqual(E.EPISODE_LEN_TOL_S, 0.15)


class H5_PublishCopy(unittest.TestCase):
    def _mk(self, td):
        td = Path(td)
        pages, pub = td / "pages", td / "pub"
        for d in (pages, pub):
            d.mkdir()
            (d / "index.html").write_text("<html>dev</html>", encoding="utf-8")
        (pages / "enduser").mkdir()
        (pages / "enduser" / "index.html").write_text("new", encoding="utf-8")
        (pages / "enduser" / "build_info.json").write_text(json.dumps({"dev_index_sha256": E.sha256_text_bytes(b"<html>dev</html>")}), encoding="utf-8")
        return pages, pub

    def test_copy_only_enduser_and_dev_untouched(self):
        with tempfile.TemporaryDirectory() as td:
            pages, pub = self._mk(td)
            (pub / "audio").mkdir()
            (pub / "audio" / "a.mp3").write_bytes(b"x")
            before = {p.name: p.read_bytes() for p in (pub / "index.html", pub / "audio" / "a.mp3")}
            with mock.patch.object(E, "verify_consistency", return_value={"ok": True, "violations": [], "checked": {}}):
                r = E.publish_copy(pages, pub, browser_verify=False)
            self.assertTrue(r["ok"])
            self.assertEqual((pub / "enduser" / "index.html").read_text(encoding="utf-8"), "new")
            self.assertEqual(before, {p.name: p.read_bytes() for p in (pub / "index.html", pub / "audio" / "a.mp3")})
            self.assertEqual([p.name for p in pub.iterdir() if p.name.startswith(".enduser.")], [])

    def test_stale_public_dev_is_reported_before_copy(self):
        """公開dirのdev index.htmlがenduser生成時と違う(公開後の手編集等)=copy前に不合格。公開dir(既存enduser/・dev)は一切変更しない。"""
        with tempfile.TemporaryDirectory() as td:
            pages, pub = self._mk(td)
            (pub / "index.html").write_text("<html>dev edited after publish</html>", encoding="utf-8")
            (pub / "enduser").mkdir()
            (pub / "enduser" / "index.html").write_text("old", encoding="utf-8")
            r = E.publish_copy(pages, pub, browser_verify=False)
            self.assertFalse(r["ok"])
            self.assertFalse(r["copied"])
            self.assertEqual(r["consistency"]["violations"][0]["code"], "ENDUSER_STALE_DEV_CHANGED")
            self.assertEqual((pub / "enduser" / "index.html").read_text(encoding="utf-8"), "old")
            self.assertEqual([p.name for p in pub.iterdir() if p.name.startswith(".enduser.")], [])

    def test_post_copy_verification_failure_rolls_back(self):
        with tempfile.TemporaryDirectory() as td:
            pages, pub = self._mk(td)
            (pub / "enduser").mkdir()
            (pub / "enduser" / "index.html").write_text("old", encoding="utf-8")
            bad = {"ok": False, "violations": [{"code": "ENDUSER_AUDIO_CHANGED", "message": "m"}], "checked": {}}
            with mock.patch.object(E, "verify_consistency", return_value=bad):
                r = E.publish_copy(pages, pub, browser_verify=False)
            self.assertFalse(r["ok"])
            self.assertTrue(r["rolled_back"])
            self.assertEqual((pub / "enduser" / "index.html").read_text(encoding="utf-8"), "old")
            self.assertEqual([p.name for p in pub.iterdir() if p.name.startswith(".enduser.")], [])

    def test_missing_source_stops(self):
        with tempfile.TemporaryDirectory() as td:
            pages, pub = self._mk(td)
            shutil.rmtree(pages / "enduser")
            with self.assertRaises(E.EnduserPageStop) as cm:
                E.publish_copy(pages, pub, browser_verify=False)
            self.assertEqual(cm.exception.code, "ENDUSER_NOT_BUILT")

    def test_copy_failure_restores_old(self):
        with tempfile.TemporaryDirectory() as td:
            pages, pub = self._mk(td)
            (pub / "enduser").mkdir()
            (pub / "enduser" / "index.html").write_text("old", encoding="utf-8")
            with mock.patch("shutil.copytree", side_effect=OSError("disk")):
                with self.assertRaises(E.EnduserPageStop) as cm:
                    E.publish_copy(pages, pub, browser_verify=False)
            self.assertEqual(cm.exception.code, "ENDUSER_WRITE_FAILED")
            self.assertEqual((pub / "enduser" / "index.html").read_text(encoding="utf-8"), "old")


class H6_ProduceContract(unittest.TestCase):
    def test_sync_called_without_tts_text_and_direct(self):
        src = _func_src(_src("er135_enduser_page_01.py"), "produce_enduser")
        self.assertIn("rows_for_sync(rows)", src)
        self.assertIn('align_mode="direct"', _src("er135_enduser_page_01.py").split("def produce_enduser")[1].split(") -> dict:")[0])
        self.assertNotIn("tts_text=", src)
        self.assertNotIn("\"tts_text\"", src)
        self.assertNotIn("openai", src.lower())

    def test_sync_error_becomes_enduser_stop(self):
        import er135_enduser_sync_01 as S
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "index.html").write_text("x", encoding="utf-8")
            with mock.patch.object(E, "build_rows_from_dev_html", return_value=({"std": []}, {}, {"level_main": {}})), \
                    mock.patch.object(S, "sync_level", side_effect=S.EnduserSyncError("ENDUSER_SYNC_TOKEN_MATCH", "m")):
                with self.assertRaises(E.EnduserPageStop) as cm:
                    E.produce_enduser(td, "x", cache_dir=os.path.join(td, "c"))
            self.assertEqual(cm.exception.code, "ENDUSER_SYNC_TOKEN_MATCH")

    def test_relative_dev_dir_is_resolved_to_absolute(self):
        """runnerのctx.pages_dirは相対path。音声pathが二重結合(ENDUSER_SYNC_AUDIO_MISSING)にならないこと(Y surname run_02の実行で発見)。"""
        import er135_enduser_sync_01 as S
        seen = {}

        def fake_rows(html, ctx):
            seen["dev_dir"] = ctx["dev_dir"]
            raise E.EnduserPageStop("ENDUSER_STOP_HERE", "stop after capture")
        cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as td:
            os.makedirs(os.path.join(td, "rel", "pages"))
            Path(td, "rel", "pages", "index.html").write_text("x", encoding="utf-8")
            os.chdir(td)
            try:
                with mock.patch.object(E, "build_rows_from_dev_html", side_effect=fake_rows):
                    with self.assertRaises(E.EnduserPageStop):
                        E.produce_enduser("rel/pages", "y", cache_dir="c")
            finally:
                os.chdir(cwd)
        self.assertTrue(os.path.isabs(str(seen["dev_dir"])), seen)

    def test_x_manuscript_priority(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "ja_writer").mkdir()
            self.assertIsNone(E.find_x_ja_manuscript(td))
            (Path(td) / "ja_writer" / "original.md").write_text("o", encoding="utf-8")
            (Path(td) / "ja_writer" / "revision1.md").write_text("1", encoding="utf-8")
            self.assertTrue(E.find_x_ja_manuscript(td).endswith("revision1.md"))
            (Path(td) / "ja_writer" / "revision2.md").write_text("2", encoding="utf-8")
            self.assertTrue(E.find_x_ja_manuscript(td).endswith("revision2.md"))


if __name__ == "__main__":
    unittest.main(verbosity=1)
