# -*- coding: utf-8 -*-
"""FAMILY-Y-PRODUCTION-LAUNCH-01 委任_03: runner.stage_text -> 実text core(produce_article) の結線test(API 0・偽clientのみ・socket遮断)。
- Cap=170円、--reuse-manifest引数、theme_package_path/reuse の受け渡し
- 実text coreを通した新規生成(SNS)・R0再利用+案B(宅配)がrunnerのstage_text経由で動く
- 補助routing 2keyがer006へ登録済み(未登録fail-closed)"""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from unittest import mock

import er006_model_routing_contract_01 as routing
import er121_family_y_runner_01 as r
import er121_family_y_text_core_01 as c
from er121_family_y_text_core_article_test_01 import (CONNECT_ATTEMPTS, RED_PKG, RED_REUSE, SNS_PKG, Smart, setUpModule, tearDownModule)  # noqa: F401


class Wiring(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        n = len(CONNECT_ATTEMPTS)
        self.addCleanup(lambda: self.assertEqual(len(CONNECT_ATTEMPTS), n))

    def ctx(self, slug, pkg, reuse=None, client=None):
        ctx = r.build_mock_context(self.tmp.name, run="run_w", slug=slug, theme_package_path=pkg, hooks={"text_core": c})
        ctx.llm_client = client or Smart()
        ctx.reuse_manifest_path = reuse
        return ctx

    def test_cap_is_170_and_above_is_refused(self):
        self.assertEqual(r.APPROVED_BUDGET_MAX_JPY, 170.0)
        r.E2EBudget(170.0)
        with self.assertRaises(r.YBudgetStop):
            r.E2EBudget(170.01)

    def test_cli_accepts_reuse_manifest_default_none(self):
        p = r.build_parser()
        self.assertIsNone(p.parse_args([]).reuse_manifest)
        self.assertEqual(p.parse_args(["--reuse-manifest", "x.json"]).reuse_manifest, "x.json")

    def test_aux_routing_keys_registered_in_er006(self):
        for k in ("FAMILY_Y_VOICE_PROVENANCE_MAP", "FAMILY_Y_VOICE_STRUCTURE_TAG"):
            self.assertEqual(routing.PROCESS_MODEL_MAP[k], "gpt-6-luna")
            self.assertEqual(c.ROUTE_AUX[k]["model"], "gpt-6-luna")
        seed = r.stage_seed_check(self.ctx("sns_age_limit", SNS_PKG))
        self.assertIn("FAMILY_Y_VOICE_PROVENANCE_MAP", seed["routing"])

    def test_text_stage_passes_package_path_and_reuse_to_produce_article(self):
        seen = {}

        class TC:
            def produce_article(self, client, **kw):
                seen.update(kw)
                raise r.YE2EStop("stop_after_capture")
        ctx = self.ctx("redelivery_fee", RED_PKG, reuse=RED_REUSE)
        ctx.hooks["text_core"] = TC()
        with self.assertRaises(r.YE2EStop):
            r.stage_text(ctx)
        self.assertEqual(seen["theme_package_path"], RED_PKG)
        self.assertEqual(seen["reuse"], RED_REUSE)
        self.assertEqual(seen["slug"], "redelivery_fee")

    def test_text_stage_input_sha_changes_with_reuse_manifest(self):
        seen = []

        class TC:
            def produce_article(self, client, **kw):
                raise r.YE2EStop("x")
        for reuse in (None, RED_REUSE):
            ctx = self.ctx("redelivery_fee", RED_PKG, reuse=reuse)
            ctx.hooks["text_core"] = TC()
            with mock.patch.object(r, "_ensure", side_effect=lambda ctx_, prov, unit, in_sha, *a, **k: seen.append(in_sha) or {"status": "x", "entry": {}}):
                r.stage_text(ctx)
        self.assertEqual(len(seen), 2)
        self.assertNotEqual(seen[0], seen[1])

    def test_sns_new_generation_through_runner_stage_text(self):
        fc = Smart()
        ctx = self.ctx("sns_age_limit", SNS_PKG, client=fc)
        res = r.stage_text(ctx)
        rec = json.load(open(f"{ctx.out_dir}/text/text_records.json", encoding="utf-8"))
        self.assertEqual(rec["closing_record"]["source"], "general_prompt_02")
        self.assertTrue(rec["closing_record"]["general_method_used"])
        self.assertTrue(os.path.exists(r._ja_path(ctx)))
        self.assertTrue(fc.by("gpt-6.1-sol"))                      # Voice/Lead/紹介/Closing(Sol high)が実際に呼ばれる
        st = json.load(open(f"{ctx.out_dir}/text/article_status.json", encoding="utf-8"))
        self.assertEqual(st["status"], "DONE")

    def test_redelivery_reuse_plan_b_through_runner_stage_text(self):
        fc = Smart()
        ctx = self.ctx("redelivery_fee", RED_PKG, reuse=RED_REUSE, client=fc)
        r.stage_text(ctx)
        rec = json.load(open(f"{ctx.out_dir}/text/text_records.json", encoding="utf-8"))
        self.assertEqual(rec["closing_record"]["source"], "fixed_user_approved")
        self.assertFalse(rec["closing_record"]["general_method_used"])
        self.assertEqual(len(fc.calls), 2)                         # Lead+紹介の補助判定1 + 案B判定1
        self.assertEqual(fc.by("gpt-6.1-sol"), [])


if __name__ == "__main__":
    unittest.main()
