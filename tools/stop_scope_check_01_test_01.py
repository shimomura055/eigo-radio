# -*- coding: utf-8 -*-
"""stop_scope_check_01 の Regression(9系統+補強)。一時ディレクトリの擬似ファイルのみ使用。実NOTICE・実センチネルは作らない。"""
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stop_scope_check_01 as S  # noqa: E402

MY = "ASR-M1-OOV-MULTI-PRONUNCIATION-PRODUCTION-01"
REAL_NOTICE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "pm", "delegation_log",
                           "2026-10-12_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_STOP_NOTICE.md")


class T(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.repo = self.d
        os.makedirs(os.path.join(self.d, "docs", "pm", "delegation_log"))
        os.makedirs(os.path.join(self.d, "er026_output", "family_z_production_e2e_01"))
        self.run = os.path.join(self.d, "er077_output", "evidence_01")
        os.makedirs(self.run)

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def notice(self, name, body):
        with open(os.path.join(self.d, "docs", "pm", "delegation_log", name), "w", encoding="utf-8") as f:
            f.write(body)

    def chk(self, **kw):
        kw.setdefault("pid_alive", lambda p: False)
        return S.check([MY], self.run, repo=self.repo, **kw)

    # 1 自ID宛NOTICE -> 停止
    def test_01_own_id_notice_stops(self):
        self.notice(f"2026-10-14_{MY}_STOP_NOTICE.md", f"# STOP NOTICE ({MY}, 2026-10-14)\n\n停止。\n")
        r = self.chk()
        self.assertTrue(r["stop"])
        self.assertEqual(r["notices"][0]["rule"], "b_own_or_parent_id_in_text")

    def test_01b_own_id_in_other_named_notice_stops(self):
        # ファイル名は別IDでも本文が自IDを名指しなら適用
        self.notice("2026-10-14_OTHER-ID_STOP_NOTICE.md", f"# STOP NOTICE (OTHER-ID, 2026-10-14)\n{MY} も停止する。\nrun_x の以降の実行は無効\n")
        self.assertTrue(self.chk()["stop"])

    # 2 STOP_ALL -> 停止
    def test_02_stop_all_stops(self):
        open(os.path.join(self.d, "er026_output", "family_z_production_e2e_01", "STOP_ALL"), "w").close()
        r = self.chk()
        self.assertTrue(r["stop"])
        self.assertEqual(r["applicable"][0]["kind"], "STOP_ALL")

    # 3 自run STOP -> 停止
    def test_03_run_stop_stops(self):
        open(os.path.join(self.run, "STOP"), "w").close()
        self.assertEqual(self.chk()["applicable"][0]["kind"], "RUN_STOP")

    def test_03b_other_run_stop_not_applied(self):
        other = os.path.join(self.d, "other_run")
        os.makedirs(other)
        open(os.path.join(other, "STOP"), "w").close()
        self.assertFalse(self.chk()["stop"])

    # 4 RUN_LOCK(生存PID) -> 停止 / stale・自PIDは非停止 / RESTART_STORM_LOCK -> 停止
    def test_04_run_lock_alive_stops(self):
        json.dump({"pid": 424242}, open(os.path.join(self.run, "RUN_LOCK.json"), "w"))
        r = self.chk(pid_alive=lambda p: True, self_pids={1})
        self.assertTrue(r["stop"])
        self.assertEqual(r["applicable"][0]["kind"], "RUN_LOCK")

    def test_04b_run_lock_stale_or_self_not_stop(self):
        json.dump({"pid": 424242}, open(os.path.join(self.run, "RUN_LOCK.json"), "w"))
        self.assertFalse(self.chk(pid_alive=lambda p: False)["stop"])
        self.assertFalse(self.chk(pid_alive=lambda p: True, self_pids={424242})["stop"])

    def test_04c_run_lock_unparsable_and_storm(self):
        open(os.path.join(self.run, "RUN_LOCK.json"), "w").write("{bad")
        self.assertTrue(self.chk()["stop"])
        os.remove(os.path.join(self.run, "RUN_LOCK.json"))
        open(os.path.join(self.run, "RESTART_STORM_LOCK.json"), "w").write("{}")
        self.assertEqual(self.chk()["applicable"][0]["kind"], "RESTART_STORM_LOCK")

    # 5 scope=ALL -> 停止(他IDでも)
    def test_05_scope_all_stops(self):
        for sc in ("ALL", "全体", "有料run全般", "API", "親scope(PARENT)"):
            with self.subTest(sc=sc):
                self.notice("2026-10-14_OTHER-ID_STOP_NOTICE.md",
                            f"# STOP NOTICE (OTHER-ID, 2026-10-14)\nscope: {sc}\nstatus: ACTIVE\nissuer: user\n")
                r = self.chk()
                self.assertTrue(r["stop"])
                self.assertEqual(r["notices"][0]["rule"], "c_scope_global")

    # 6 CLOSED -> 非停止(自ID宛でも)
    def test_06_closed_not_stop(self):
        self.notice(f"2026-10-14_{MY}_STOP_NOTICE.md", f"# STOP NOTICE ({MY}, 2026-10-14)\nstatus: CLOSED\n")
        r = self.chk()
        self.assertFalse(r["stop"])
        self.assertEqual(r["notices"][0]["rule"], "a_status_inactive")

    def test_06b_expired_not_stop_unparsable_expiry_stops(self):
        self.notice("2026-10-14_OTHER-ID_STOP_NOTICE.md", "# STOP NOTICE (OTHER-ID, 2026-10-14)\nscope: ALL\nexpires: 2020-01-01T00:00:00\n")
        self.assertFalse(self.chk()["stop"])
        self.notice("2026-10-14_OTHER-ID_STOP_NOTICE.md", "# STOP NOTICE (OTHER-ID, 2026-10-14)\nscope: ALL\nexpires: someday\n")
        self.assertTrue(self.chk()["stop"])

    # 7 他ID・限定run -> 非停止
    def test_07_other_id_limited_run_not_stop(self):
        self.notice("2026-10-14_OTHER-ID_STOP_NOTICE.md", "# STOP NOTICE (OTHER-ID, 2026-10-14)\nscope: run:run_e2e_01\nissuer: Fable\n")
        r = self.chk()
        self.assertFalse(r["stop"])
        self.assertEqual(r["notices"][0]["rule"], "c_scope_limited_other")

    def test_07b_limited_scope_naming_my_run_stops(self):
        self.notice("2026-10-14_OTHER-ID_STOP_NOTICE.md", "# STOP NOTICE (OTHER-ID, 2026-10-14)\nscope: run:evidence_01\n")
        self.assertTrue(self.chk()["stop"])

    # 8 parse不能 -> 停止(fail-closed)
    def test_08_unparsable_fail_closed(self):
        for body in ("", "あ。何かの文章だけ\n", "scope: ???\n", "# STOP NOTICE\nrun_a の以降の実行は無効\n"):
            with self.subTest(body=body):
                self.notice("garbage_STOP_NOTICE.txt", body)
                self.assertTrue(self.chk()["stop"])

    def test_08b_unreadable_fail_closed(self):
        os.makedirs(os.path.join(self.d, "docs", "pm", "delegation_log", "dir_STOP_NOTICE.md"))  # 読めない(ディレクトリ)
        r = self.chk()
        self.assertTrue(r["stop"])
        self.assertEqual(r["notices"][0]["rule"], "unreadable")

    # 9 旧書式: ID一致かつ限定run -> 非停止 / 根拠が欠ければ停止
    LEGACY = "# STOP NOTICE (LEGACY-ID, 2026-10-12, ローカルのみ)\n\nユーザー仕様変更により run_e2e_01 の以降の実行は無効。\n"

    def test_09_legacy_id_match_limited_run_not_stop(self):
        self.notice("2026-10-12_LEGACY-ID_STOP_NOTICE.md", self.LEGACY)
        r = self.chk()
        self.assertFalse(r["stop"])
        self.assertEqual(r["notices"][0]["rule"], "d_legacy_id_match_run_limited")

    def test_09b_legacy_failclosed_variants(self):
        # ファイル名IDと見出しIDが不一致
        self.notice("2026-10-12_OTHER_STOP_NOTICE.md", self.LEGACY)
        self.assertTrue(self.chk()["stop"])
        os.remove(os.path.join(self.d, "docs", "pm", "delegation_log", "2026-10-12_OTHER_STOP_NOTICE.md"))
        # 限定文言なし
        self.notice("2026-10-12_LEGACY-ID_STOP_NOTICE.md", "# STOP NOTICE (LEGACY-ID, 2026-10-12)\n\n停止する。\n")
        self.assertTrue(self.chk()["stop"])
        # 全体宣言文言あり
        self.notice("2026-10-12_LEGACY-ID_STOP_NOTICE.md", self.LEGACY + "全run を停止する。\n")
        self.assertTrue(self.chk()["stop"])
        # 限定対象が自run
        self.notice("2026-10-12_LEGACY-ID_STOP_NOTICE.md", self.LEGACY.replace("run_e2e_01", "evidence_01"))
        self.assertTrue(self.chk()["stop"])

    # 既存停止を弱めない: 非適用NOTICEがあっても STOP_ALL/自run STOP は引き続き検出
    def test_10_inapplicable_notice_does_not_mask_sentinels(self):
        self.notice("2026-10-12_LEGACY-ID_STOP_NOTICE.md", self.LEGACY)
        open(os.path.join(self.run, "STOP"), "w").close()
        r = self.chk()
        self.assertTrue(r["stop"])
        self.assertEqual([a["kind"] for a in r["applicable"]], ["RUN_STOP"])
        open(os.path.join(self.d, "er026_output", "family_z_production_e2e_01", "STOP_ALL"), "w").close()
        self.assertEqual([a["kind"] for a in self.chk()["applicable"]], ["STOP_ALL", "RUN_STOP"])

    def test_11_helper_is_readonly(self):
        self.notice("2026-10-12_LEGACY-ID_STOP_NOTICE.md", self.LEGACY)
        before = sorted(os.listdir(os.path.join(self.d, "docs", "pm", "delegation_log")))
        self.chk()
        self.assertEqual(before, sorted(os.listdir(os.path.join(self.d, "docs", "pm", "delegation_log"))))
        self.assertEqual(os.listdir(self.run), [])

    def test_12_parent_id_applies(self):
        self.notice("2026-10-14_PARENT-X_STOP_NOTICE.md", "# STOP NOTICE (PARENT-X, 2026-10-14)\nrun_e2e_01 の以降の実行は無効\nPARENT-X 配下全て\n")
        self.assertTrue(S.check([MY], self.run, repo=self.repo, parent_ids=["PARENT-X"], pid_alive=lambda p: False)["stop"])

    @unittest.skipUnless(os.path.exists(REAL_NOTICE), "実NOTICEなし")
    def test_13_real_melos_notice_not_applicable_to_m1_but_applicable_to_its_own_run(self):
        shutil.copy(REAL_NOTICE, os.path.join(self.d, "docs", "pm", "delegation_log", os.path.basename(REAL_NOTICE)))  # コピーに対して判定
        self.assertFalse(self.chk()["stop"])
        run2 = os.path.join(self.d, "run_e2e_01")
        os.makedirs(run2)
        self.assertTrue(S.check([MY], run2, repo=self.repo, pid_alive=lambda p: False)["stop"])
        self.assertTrue(S.check(["FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01"], self.run, repo=self.repo, pid_alive=lambda p: False)["stop"])


if __name__ == "__main__":
    unittest.main()
