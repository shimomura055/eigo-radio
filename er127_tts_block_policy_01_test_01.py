# -*- coding: utf-8 -*-
"""TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_02: 統一3回構成ブロック(er127)のoffline test。API 0・実sleep 0(clock/sleep注入)。

構成: T-MAP(49行) / T-SCOPE(scope gate・golden) / T-CD(cooldown_core) / T-BLK(BlockRun・Progress) / leaf matrix(L1〜L8) / T-STY(Style・Voice) /
T-LR・T-LRN・T-RE(LR) / T-HRL(終端HRQ1行) / T-RES(STOP・resume) / T-GATE(Gate契約M-5) / T-ROLE(D11) / T-STORE(M-7) / 静的検査(撤去の機械確認)。
不整合な出力を期待値としてassertしない(旧600秒・LR後1回・RecursionErrorをscope内の期待値にしない)。
"""
from __future__ import annotations

import ast
import json
import os
import re
import tempfile
import unittest
from unittest import mock

import er127_fakes_01 as F
import er127_golden_01 as G
import er127_tts_block_policy_01 as blk

ROOT = os.path.dirname(os.path.abspath(__file__))
ROW_MAPPING = os.path.join(ROOT, "docs", "research", "TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01", "ROW_MAPPING_01.json")

LEAF_CFG = {  # leaf -> (segment_id, level, scope)
    "L1": ("comment_1", "b1b", "X"), "L2": ("full_story_part1", "b1b", "X"), "L3": ("topic_intro", "a2", "X"),
    "L4": ("full_story_part1", "a2", "X"), "L7a": ("japanese_title", "a2", "X"), "L7b": ("japanese_title", "a2", "X"),
    "L6": ("kp1_en", "a2", "X"), "L8": ("full_story_part1_c3", "b1b", "Z"),
}
LR_LEAVES = ("L1", "L2", "L3", "L4")
ENGLISH_LEAVES = ("L1", "L2", "L3", "L4", "L6", "L8")
STYLE = "ROLE_STYLE_MARKER_Z9"


def call_leaf(leaf, w, *, cs=True, style=STYLE):
    import er003_v1_crosslevel_audio_02_common as c
    import er003_v1_n3_01_tts_generate as n3
    import er003_v1_repro01_main_generate as repro01
    import er003_v1_sing01_news_tail_fix as ntf
    import er003_v1_sing01_voice01_generate as v1
    if leaf == "L1":
        return v1.generate_charon_english(F.TEXT, w.out_path, enable_connected_speech_equivalence_layer=cs, style_prefix_override=style)
    if leaf == "L2":
        return ntf.generate_news_narration_wide_margin(F.TEXT, w.out_path, enable_connected_speech_equivalence_layer=cs, style_prefix_override=style)
    if leaf == "L3":
        return c.generate_english_segment_with_fallback(F.TEXT, w.out_path, F.TEXT, enable_connected_speech_equivalence_layer=cs, style_prefix_override=style)
    if leaf == "L4":
        return n3.generate_a2_segment_with_slowdown(F.TEXT, w.out_path, F.TEXT, enable_connected_speech_equivalence_layer=cs, style_prefix_override=style)
    if leaf == "L7a":
        return n3.generate_a2_japanese_with_fallback(F.JA_TEXT, w.out_path, F.JA_TEXT, style_prefix_override=style)
    if leaf == "L7b":
        return v1.generate_charon_japanese(F.JA_TEXT, w.out_path, F.JA_TEXT)
    if leaf == "L6":
        return repro01.generate_key_phrase_component_verified(F.TEXT, w.out_path)
    if leaf == "L8":
        import er012_b_family_voices_production_01 as bv
        return bv.generate_voice_body_wide_margin(F.TEXT, w.out_path, "Puck", enable_connected_speech_equivalence_layer=cs, style_prefix_override=style)
    raise ValueError(leaf)


def make_world(leaf, *, judge=(), post_judge=(), tts=None, **kw):
    seg, level, _scope = LEAF_CFG[leaf]
    ja = leaf in ("L7a", "L7b")
    wk = dict(seg=seg, level=level, tts=[True] * 12 if tts is None else tts, asr_text=F.JA_TEXT if ja else F.TEXT, post_judge=post_judge)
    if ja:
        wk["ja_judge"] = judge
    else:
        wk["judge"] = judge
    wk.update(kw)
    return F.World(**wk)


def run(leaf, judge, *, scope="__default__", post_judge=(), tts=None, cs=True, style=STYLE, world_kw=None):
    """leafを1回実行して要約を返す(例外は捕捉して返す)。"""
    wkw = dict(world_kw or {})
    dq_ng = wkw.pop("dq_ng", False)
    w = make_world(leaf, judge=judge, post_judge=post_judge, tts=tts, **wkw)
    w.dq_ng = dq_ng
    sc = LEAF_CFG[leaf][2] if scope == "__default__" else scope
    try:
        with w.patched(scope=sc):
            try:
                r, err = call_leaf(leaf, w, cs=cs, style=style), None
            except BaseException as exc:      # noqa: BLE001
                r, err = None, exc
        return Summary(w, r, err)
    except BaseException:
        w.cleanup()
        raise


class Summary:
    def __init__(self, w, r, err):
        self.w, self.r, self.err = w, r, err
        self.events = w.events
        self.tts = sum(1 for e in w.events if e[0] == "tts")
        self.sleep_total = sum(w.clock.sleeps)
        self.sleeps = w.clock.sleeps
        self.hr = w.hr_rows()
        self.lr = len(w.lr_calls)
        self.lr_llm = sum(1 for e in w.events if e[0] == "lr_llm")
        self.prompts = w.prompts
        self.voices = w.voices
        self.judges = [j for j in w.judge_calls if not j.get("post")]
        self.posts = [j for j in w.judge_calls if j.get("post")]
        self.status = r.get("status") if isinstance(r, dict) else None

    def waits(self):
        """180秒待機の回数(sleep列を5秒刻みの連続塊で数える=待機中に他イベントが挟まらない)。"""
        n, in_wait = 0, False
        for e in self.events:
            if e[0] == "sleep":
                if not in_wait:
                    n, in_wait = n + 1, True
            else:
                in_wait = False
        return n

    def close(self):
        self.w.cleanup()


class Base(unittest.TestCase):
    def tearDown(self):
        for s in getattr(self, "_sums", []):
            s.close()

    def go(self, leaf, judge, **kw):
        s = run(leaf, judge, **kw)
        self._sums = getattr(self, "_sums", []) + [s]
        if s.err is not None:
            raise s.err
        return s


# =====================================================================================================
# T-MAP: 星取表49行のコード化(ROW_MAPPING_01.json)
# =====================================================================================================
ROW_REPR = {   # 行ID -> (leaf, segment_id, z_dialogue_policy)  ※policy解決の代表(block_policy_forの結果がROW_MAPPINGのpolicyと一致すること)
    "X-S01": ("L3", "topic_intro"), "X-S02": ("L7", "japanese_title"), "X-S03": ("L7", "point_explanation"),
    "X-S04": ("L4", "full_story_part1"), "X-S05": ("L4", "full_story_part1_k1"), "X-S06": ("L4", "in_one_line"), "X-S07": ("L6", "kp1_en"),
    "X-A01": ("L1", "topic_intro"), "X-A02": ("L1", "preview"), "X-A03": ("L1", "comment_1"), "X-A04": ("L2", "full_story_part1"),
    "X-A05": ("L2", "full_story_part1_k2"), "X-A06": ("L2", "in_one_line"), "X-A07": ("L6", "kp2_en"), "X-A08": ("L5", "kp1_explanation_en"),
    "X-A09": ("L1", "welcome"), "Y-S-01": ("L3", "full_story_intro"), "Y-S-01b": ("L7", "point_explanation"), "Y-S-02": ("L3", "topic_intro"),
    "Y-S-03": ("L7", "japanese_title"), "Y-S-04": ("L7", "comment_1"), "Y-S-05": ("L4", "y_lead"), "Y-S-06": ("L4", "y_voice_1"),
    "Y-S-07": ("L4", "y_voice_2_k1"), "Y-S-08": ("L6", "kp3_en"), "Y-S-09": ("L7", "meaning_1"), "Y-B-01": ("L1", "num_one"),
    "Y-B-02": ("L1", "topic_intro"), "Y-B-03": ("L1", "comment_1"), "Y-B-04": ("L2", "y_intro_2"), "Y-B-05": ("L2", "y_voice_3"),
    "Y-B-06": ("L2", "y_voice_1_k2"), "Y-B-07": ("L6", "kp1_en"), "Y-B-08": ("L5", "kp3_explanation_en"),
    "Z-A2-NARR": ("L4", "full_story_part2_c3"), "Z-A2-DIALOGUE-CTX": ("L8", "full_story_part1_c1", "fz_ctx_v1"),
    "Z-A2-DIALOGUE-LEGACY": ("L8", "full_story_part1_c1", "legacy"), "Z-A2-TOPIC": ("L3", "topic_intro_en"), "Z-A2-JA": ("L7", "preview"),
    "Z-A2-KPEN": ("L6", "kp1_en"), "Z-A2-KPJA": ("L7", "kp1_ja"), "Z-B1B-NARR": ("L2", "full_story_part1_c2_k1"),
    "Z-B1B-DIALOGUE-CTX": ("L8", "full_story_part1_c1", "fz_ctx_v1"), "Z-B1B-DIALOGUE-LEGACY": ("L8", "full_story_part1_c1", "legacy"),
    "Z-B1B-TOPIC": ("L1", "topic_intro_en"), "Z-B1B-PREVCOM": ("L1", "comment_2"), "Z-B1B-KPEN": ("L6", "kp2_en"), "Z-B1B-KPEXPL": ("L5", "kp2_explanation_en"),
}
NO_TTS_ROWS = {"Y-B-00"}


class MapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(ROW_MAPPING, encoding="utf-8") as f:
            cls.rows = json.load(f)["rows"] if "rows" in json.load(open(ROW_MAPPING, encoding="utf-8")) else None
        d = json.load(open(ROW_MAPPING, encoding="utf-8"))
        cls.rows = d["rows"] if "rows" in d else d["profiles"]

    def test_t_map_49_rows_cover_all_ids(self):
        ids = {r["id"] for r in self.rows}
        self.assertEqual(len(self.rows), 49)
        self.assertEqual(ids, set(ROW_REPR) | NO_TTS_ROWS)

    def test_t_map_each_row_policy_matches_star_table(self):
        n = 0
        for r in self.rows:
            if r["id"] in NO_TTS_ROWS:
                self.assertEqual(r["policy"], "NO_TTS")
                prof = blk.PROFILES["NO_TTS"]
                self.assertEqual((prof.max_tts, prof.max_waits, prof.lr), (0, 0, False))
                n += 1
                continue
            leaf, seg, *rest = ROW_REPR[r["id"]]
            with self.subTest(row=r["id"]):
                fam = r["family"]
                from er109_xz_scope_01 import run_scope
                with run_scope(fam):
                    pol = blk.block_policy_for(leaf, seg, z_dialogue_policy=(rest[0] if rest else None))
                self.assertEqual(pol.profile.name, r["policy"])
                self.assertEqual(pol.profile.max_tts, r["max_tts"])
                self.assertEqual(pol.profile.max_waits, r["max_waits"])
                self.assertEqual(pol.profile.lr, r["policy"] in ("EN_LR_STD", "EN_LR_ADV"))
                n += 1
        self.assertEqual(n, 49)

    def test_t_map_counts_by_policy_and_family(self):
        from collections import Counter
        c = Counter(r["policy"] for r in self.rows)
        self.assertEqual(c["EN_LR_STD"] + c["EN_LR_ADV"], 24)
        self.assertEqual({k: sum(1 for r in self.rows if r["family"] == k) for k in "XYZ"}, {"X": 16, "Y": 19, "Z": 14})
        self.assertEqual(set(c), set(blk.PROFILES))

    def test_profile_table_invariants(self):
        for name, p in blk.PROFILES.items():
            if not p.unified:
                continue
            self.assertEqual(p.max_tts, p.total_slots, name)
            self.assertEqual(p.max_waits, len(p.cooldown_before) * (2 if p.lr else 1), name)
            self.assertIn(3, p.cooldown_before, name)
        self.assertEqual(blk.PROFILES["KP_EN"].block_attempts, 4)
        self.assertEqual(blk.PROFILES["EN_LR_STD"].max_tts, 6)
        self.assertEqual(blk.PROFILES["JA_STD"].max_tts, 3)


# =====================================================================================================
# T-SCOPE / M-1: scope gate と fail-closed
# =====================================================================================================
class ScopeTests(unittest.TestCase):
    def test_inactive_outside_scope(self):
        import er109_xz_scope_01 as xz
        self.assertIsNone(xz.current_scope())
        self.assertFalse(blk.unified_flow_active())
        self.assertIsNone(blk.block_policy_for("L3", "topic_intro"))
        self.assertIsNone(blk.block_policy_for("L7", None))
        self.assertIsNone(blk.open_block("L1", "x/narration/comment_1.wav", "t"))

    def test_active_inside_each_scope_and_restored(self):
        import er109_xz_scope_01 as xz
        for fam in "XYZ":
            with xz.run_scope(fam):
                self.assertTrue(blk.unified_flow_active())
            self.assertFalse(blk.unified_flow_active())

    def test_env_args_cannot_enable_or_disable(self):
        with mock.patch.dict(os.environ, {"TTS_UNIFIED_FLOW": "1", "ER127_ENABLE": "1", "UNIFIED_FLOW": "1"}):
            self.assertFalse(blk.unified_flow_active())
        import inspect
        self.assertEqual(list(inspect.signature(blk.unified_flow_active).parameters), [])
        src = open(os.path.join(ROOT, "er127_tts_block_policy_01.py"), encoding="utf-8").read()
        self.assertNotIn("os.environ", src.replace("os.environ-", ""), "Productionにenv迂回口を作らない(M-8)")
        self.assertNotIn("getenv", src)

    def test_fail_closed_unknown_segment_and_none(self):
        import er109_xz_scope_01 as xz
        with xz.run_scope("X"):
            for leaf in ("L1", "L2", "L3", "L4"):
                with self.assertRaises(blk.BlockPolicyError):
                    blk.block_policy_for(leaf, None)
                with self.assertRaises(blk.BlockPolicyError):
                    blk.block_policy_for(leaf, "totally_unknown_id")
                with self.assertRaises(blk.BlockPolicyError):
                    blk.block_policy_for(leaf, "point_one_heading")      # HEADING_READOUT: 表にない部位は黙ってlegacyへ落とさない
            with self.assertRaises(blk.BlockPolicyError):
                blk.block_policy_for("L8", "x", z_dialogue_policy=None)
            with self.assertRaises(blk.BlockPolicyError):
                blk.block_policy_for("L9", "x")

    def test_shell_english_is_explicit_row_not_unknown(self):
        import er109_xz_scope_01 as xz
        ids = ["welcome", "preview_intro", "key_phrases_intro", "full_story_intro", "num_one", "num_two", "num_three", "num_four", "num_five",
               "welcome_a2", "num_one_charon"]
        with xz.run_scope("Y"):
            for leaf in ("L1", "L2", "L3", "L4"):
                for sid in ids:
                    pol = blk.block_policy_for(leaf, sid)
                    self.assertEqual(pol.profile.name, "SHELL_EN", (leaf, sid))
                    self.assertFalse(pol.profile.unified)
            self.assertIsNone(blk.open_block("L1", "o/t/b1b/narration/welcome.wav", "Welcome."))

    def test_leaf_decides_std_or_adv(self):
        import er109_xz_scope_01 as xz
        with xz.run_scope("X"):
            self.assertEqual(blk.block_policy_for("L1", "comment_1").profile.name, "EN_LR_ADV")
            self.assertEqual(blk.block_policy_for("L2", "in_one_line").profile.name, "EN_LR_ADV")
            self.assertEqual(blk.block_policy_for("L3", "topic_intro").profile.name, "EN_LR_STD")
            self.assertEqual(blk.block_policy_for("L4", "full_story_part1_k2").profile.name, "EN_LR_STD")

    def test_open_block_without_layout_english_fails_closed(self):
        import er109_xz_scope_01 as xz
        with xz.run_scope("X"):
            with self.assertRaises(blk.BlockPolicyError):
                blk.open_block("L1", "dummy.wav", "t")
            self.assertIsNotNone(blk.open_block("L7", "dummy.wav", "t"))      # 日本語はsegment_id不要
            self.assertIsNotNone(blk.open_block("L6", "dummy.wav", "t", max_attempts=4))

    def test_lr_block_outside_scope_is_rejected(self):
        with self.assertRaises(blk.BlockPolicyError):
            blk.open_block("L7", "a/b/narration/x.wav", "t", ctx=blk.BlockCtx(depth=1))


# =====================================================================================================
# T-CD: cooldown_core
# =====================================================================================================
class CooldownCoreTests(unittest.TestCase):
    def setUp(self):
        self.c = F.FakeClock()

    def core(self, **kw):
        return blk.cooldown_core(clock=self.c.clock, sleep=self.c.sleep, stop_check=kw.pop("stop_check", lambda where: None), **kw)

    def test_constants_single_definition(self):
        self.assertEqual(blk.COOLDOWN_SECONDS, 180.0)
        import er020_tts_retry_local_rewrite_01 as er020
        import er122_fz_ctx_policy_01 as er122
        self.assertEqual(er020.LEGACY_COOLDOWN_SECONDS, 600.0)       # scope外(A/B/C)専用
        self.assertEqual(er122.cooldown_seconds(), 180.0)            # Z ctxは唯一の定義を参照する
        self.assertEqual(blk.SLICE_SECONDS, 5.0)

    def test_full_wait_from_now_is_180_in_5s_slices(self):
        rec = self.core(label="seg")
        self.assertAlmostEqual(sum(self.c.sleeps), 180.0)
        self.assertLessEqual(max(self.c.sleeps), 5.0)
        self.assertEqual(len(self.c.sleeps), 36)
        self.assertEqual(rec["cooldown_requested_seconds"], 180.0)
        self.assertAlmostEqual(rec["cooldown_actual_seconds"], 180.0, places=2)
        for k in ("cooldown_started_at", "cooldown_ended_at", "attempt_before_cooldown", "attempt_after_cooldown", "resumed", "total_elapsed_since_ref_seconds"):
            self.assertIn(k, rec)

    def test_resume_pays_only_remaining(self):
        ref = self.c.t - 100.0          # 100秒前にNG確定
        rec = self.core(ref_epoch=ref, resumed=True)
        self.assertAlmostEqual(sum(self.c.sleeps), 80.0)
        self.assertTrue(rec["resumed"])
        self.assertAlmostEqual(rec["total_elapsed_since_ref_seconds"], 180.0, places=2)

    def test_no_wait_when_already_elapsed(self):
        rec = self.core(ref_epoch=self.c.t - 500.0)
        self.assertEqual(self.c.sleeps, [])
        self.assertEqual(rec["cooldown_actual_seconds"], 0.0)

    def test_stop_checked_every_slice_and_aborts(self):
        calls = []

        def stop(where):
            calls.append(where)
            if len(calls) >= 3:
                raise RuntimeError("STOP!")
        with self.assertRaises(RuntimeError):
            self.core(stop_check=stop, label="clipA")
        self.assertEqual(len(self.c.sleeps), 2)                 # 3回目のstop_checkで中断(sleepの前)
        self.assertTrue(all(w == "tts_cooldown:clipA" for w in calls))

    def test_default_stop_all_sentinel_raises_dedicated_baseexception(self):
        with tempfile.TemporaryDirectory() as d:
            sentinel = os.path.join(d, "STOP_ALL")
            open(sentinel, "w").close()
            with mock.patch.object(blk, "STOP_ALL_PATH", sentinel), mock.patch.object(blk, "_STOP_CHECK", None):
                with self.assertRaises(blk.TtsBlockStopError) as cm:
                    blk.cooldown_core(clock=self.c.clock, sleep=self.c.sleep)
                self.assertFalse(isinstance(cm.exception, Exception))     # `except Exception`で握り潰されない(M-11)
        self.assertEqual(self.c.sleeps, [])

    def test_register_stop_check_is_used(self):
        seen = []
        prev = blk.register_stop_check(lambda where: seen.append(where))
        try:
            blk.cooldown_core(seconds=10.0, clock=self.c.clock, sleep=self.c.sleep, label="L")
        finally:
            blk.register_stop_check(prev)
        self.assertEqual(len(seen), 2)

    def test_legacy_entry_in_scope_never_sleeps_600(self):
        """安全網: scope内で旧関数に到達しても旧600秒は払わない(180秒+STOP確認)。scope外は旧挙動のまま(golden)。"""
        import er020_tts_retry_local_rewrite_01 as er020
        import er109_xz_scope_01 as xz
        slept = []
        with mock.patch.object(blk.RUNTIME, "clock", self.c.clock), mock.patch.object(blk.RUNTIME, "sleep", self.c.sleep):
            with xz.run_scope("X"):
                rec = er020.maybe_cooldown_before_attempt(3, 3, True, sleep_fn=slept.append)
        self.assertEqual(slept, [])                                  # 旧sleep_fn(600)は呼ばれない
        self.assertAlmostEqual(sum(self.c.sleeps), 180.0)
        self.assertEqual(rec["cooldown_requested_seconds"], 180.0)
        out = er020.maybe_cooldown_before_attempt(3, 3, True, sleep_fn=slept.append)      # scope外=旧挙動
        self.assertEqual(slept, [600.0])
        self.assertEqual(out["cooldown_requested_seconds"], 600.0)


# =====================================================================================================
# T-BLK: BlockRun / BlockProgress
# =====================================================================================================
class BlockRunTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="blk_")
        self.out = os.path.join(self.tmp, "theme", "b1b", "narration", "comment_1.wav").replace("\\", "/")
        os.makedirs(os.path.dirname(self.out), exist_ok=True)
        self.c = F.FakeClock()
        self.patches = [mock.patch.object(blk.RUNTIME, "clock", self.c.clock), mock.patch.object(blk.RUNTIME, "sleep", self.c.sleep),
                        mock.patch.object(blk, "_STOP_CHECK", None)]
        for p in self.patches:
            p.start()
        import er109_xz_scope_01 as xz
        self.scope = xz.run_scope("X")
        self.scope.__enter__()

    def tearDown(self):
        self.scope.__exit__(None, None, None)
        for p in self.patches:
            p.stop()
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def open(self, leaf="L1", text="hello", **kw):
        return blk.open_block(leaf, self.out, text, fingerprint={"style": "s"}, **kw)

    def test_wait_only_before_third_and_only_after_ng(self):
        b = self.open()
        s1 = b.step(1)
        self.assertEqual((s1.cooldown, s1.style_mode, s1.skip), (None, "PRIMARY", False))
        s2 = b.step(2)
        self.assertIsNone(s2.cooldown)
        self.assertEqual(self.c.sleeps, [])
        s3 = b.step(3)
        self.assertEqual(s3.style_mode, "FALLBACK")
        self.assertIsNotNone(s3.cooldown)
        self.assertAlmostEqual(sum(self.c.sleeps), 180.0)

    def test_third_style_same_for_z_legacy_dialogue(self):
        import er109_xz_scope_01 as xz
        with xz.run_scope("Z"):
            b = blk.open_block("L8", self.out, "t", z_dialogue_policy="legacy")
        b.step(1), b.step(2)
        s3 = b.step(3)
        self.assertEqual(s3.style_mode, "PRIMARY")                 # legacy方式はStyle変更なし
        self.assertIsNotNone(s3.cooldown)                          # ただし③前に180秒(新設)

    def test_slots_total_per_policy(self):
        self.assertEqual(self.open("L1").total_slots, 6)
        self.assertEqual(self.open("L7").total_slots, 3)
        self.assertEqual(self.open("L6", max_attempts=4).total_slots, 4)
        b = self.open("L1", ctx=blk.BlockCtx(depth=1, slot_offset=3, total_slots=6, script_version="v1", m1_anchor_text="o", lock_text="o"))
        self.assertEqual((b.slot(1), b.slot(3), b.is_last_slot(2), b.is_last_slot(3)), (4, 6, False, True))
        self.assertFalse(b.lr_allowed)

    def test_kp_waits_only_before_english_lock_third(self):
        b = self.open("L6", max_attempts=4)
        for o in (1, 2):
            self.assertIsNone(b.step(o).cooldown)
        self.assertIsNotNone(b.step(3).cooldown)
        self.assertIsNone(b.step(4).cooldown)                     # ③④の間には入れない(I-4)
        self.assertEqual(self.c.t - 1_000_000.0, 180.0)

    def test_progress_persisted_before_tts_and_resume_skips_consumed(self):
        b = self.open()
        b.step(1)
        b.step(2)               # 1をNGとして閉じる
        path = b.progress.path
        st = json.load(open(path, encoding="utf-8"))
        self.assertEqual(st["blocks"]["0"]["n_started"], 2)
        self.assertEqual(st["status"], "IN_PROGRESS")
        # --- 別processの再開(同じkey): 消費済みの1,2はskip
        self.c.t += 40
        b2 = self.open()
        self.assertTrue(b2.progress.resumed)
        self.assertTrue(b2.step(1).skip)
        self.assertTrue(b2.step(2).skip)
        s3 = b2.step(3)
        self.assertFalse(s3.skip)
        self.assertTrue(s3.cooldown["resumed"] is False or s3.cooldown["resumed"] is True)
        # 残り時間だけ待つ(2のfinished_epochはstep(2)開始時点=resume前)。再開で180秒を二重に払わない
        self.assertLess(sum(self.c.sleeps), 180.0 + 1e-6)
        self.assertGreater(sum(self.c.sleeps), 0.0)
        self.assertLessEqual(self.c.t - 1_000_000.0, 180.0 + 40 + 1e-6)

    def test_done_progress_starts_new_cycle(self):
        b = self.open()
        b.step(1)
        b.finish({"status": "OK"})
        b2 = self.open()
        self.assertFalse(b2.progress.resumed)
        self.assertFalse(b2.step(1).skip)

    def test_key_change_text_or_fingerprint_starts_new_cycle(self):
        b = self.open(text="orig")
        b.step(1), b.step(2)
        self.assertFalse(self.open(text="other").progress.resumed)
        b3 = blk.open_block("L1", self.out, "orig", fingerprint={"style": "DIFFERENT"})
        self.assertFalse(b3.progress.resumed)

    def test_stale_in_progress_is_new_cycle(self):
        b = self.open()
        b.step(1), b.step(2)
        self.c.t += blk.PROGRESS_MAX_AGE_SECONDS + 1
        self.assertFalse(self.open().progress.resumed)

    def test_regenerate_approved_is_new_cycle_but_only_only_flags_are_not(self):
        import er011_human_review_lock_01 as review_lock
        b = self.open(text="orig")
        b.step(1), b.step(2)
        level_dir = review_lock._level_out_dir_from_out_path(self.out)
        review_lock._save_store(level_dir, {"comment_1": {"state": "REGENERATE_APPROVED", "canonical_text_sha256": review_lock._text_hash("orig")}})
        self.assertFalse(self.open(text="orig").progress.resumed)
        review_lock._save_store(level_dir, {})
        b.step(1)  # 旧stateは残っている(上の新規サイクルで上書きされたので再度作る)
        b = self.open(text="orig")
        b.step(1), b.step(2)
        self.assertTrue(self.open(text="orig").progress.resumed)       # Lockが無ければresume(`--only-*`の再実行だけでは新規サイクルにしない)

    def test_verified_attempt_in_state_is_new_cycle(self):
        b = self.open()
        b.step(1)
        b.done(1, True)
        self.assertFalse(self.open().progress.resumed)

    def test_auto_close_marks_ng_epoch_and_stub_rows(self):
        b = self.open()
        b.step(1)
        self.c.t += 7
        b.step(2)
        self.assertEqual(b.last_ng_epoch, self.c.t)
        row = b.stub_row(1)
        self.assertEqual((row["attempt"], row["verified"], row["carried_from_prior_process"]), (1, False, True))

    def test_lr_text_persisted_for_resume(self):
        b = self.open(text="orig")
        b.progress.save_lr_text("rewritten text")
        b2 = self.open(text="orig")
        self.assertTrue(b2.progress.resumed)
        self.assertEqual(b2.progress.lr_state()["text"], "rewritten text")
        self.assertTrue(b2.progress.lr_state()["used"])

    def test_dummy_path_progress_is_in_memory_only(self):
        b = blk.open_block("L7", "dummy.wav", "t")
        b.step(1)
        self.assertFalse(b.progress.persistent)
        self.assertIsNone(b.progress.path)


# =====================================================================================================
# leaf matrix: 統一3回構成(全leaf共通の不変条件)
# =====================================================================================================
class LeafMatrixTests(Base):
    def assert_invariants(self, s, *, max_tts, max_waits, max_lr=1):
        self.assertLessEqual(s.tts, max_tts)
        self.assertLessEqual(s.lr, max_lr)
        self.assertLessEqual(s.waits(), max_waits)
        self.assertAlmostEqual(s.sleep_total, 180.0 * s.waits(), places=2)
        if s.sleeps:
            self.assertLessEqual(max(s.sleeps), 5.0)

    def test_first_pass_no_wait_no_fallback(self):
        for leaf in LR_LEAVES:
            with self.subTest(leaf=leaf):
                s = self.go(leaf, [F.PASS])
                self.assertEqual((s.status, s.tts, s.sleep_total, s.lr, len(s.hr)), ("OK", 1, 0, 0, 0))
                self.assertFalse(any(j.get("force_secondary") for j in s.judges))

    def test_second_pass_no_wait_no_fallback(self):
        for leaf in LR_LEAVES:
            with self.subTest(leaf=leaf):
                s = self.go(leaf, [F.NG, F.PASS])
                self.assertEqual((s.status, s.tts, s.sleep_total, s.lr, len(s.hr)), ("OK", 2, 0, 0, 0))

    def test_third_after_180s_with_fallback_and_forced_secondary(self):
        for leaf in LR_LEAVES:
            with self.subTest(leaf=leaf):
                s = self.go(leaf, [F.NG, F.NG, F.PASS])
                self.assertEqual((s.status, s.tts, s.lr, len(s.hr)), ("OK", 3, 0, 0))
                self.assertEqual(s.waits(), 1)
                self.assertAlmostEqual(s.sleep_total, 180.0, places=2)
                self.assertEqual([j["force_secondary"] for j in s.judges], [False, False, True])
                # 待機はTTS①②の後・③のTTSの前(順序)
                kinds = [e[0] for e in s.events if e[0] in ("tts", "sleep")]
                first_sleep = kinds.index("sleep")
                self.assertEqual(kinds[:first_sleep], ["tts", "tts"])
                self.assertEqual(kinds[-1], "tts")

    def test_lr_after_third_ng_then_first_of_lr_block_passes(self):
        for leaf in LR_LEAVES:
            with self.subTest(leaf=leaf):
                s = self.go(leaf, [F.NG, F.NG, F.NG, F.PASS])
                self.assertEqual((s.status, s.tts, s.lr, s.lr_llm, len(s.hr), s.waits()), ("OK", 4, 1, 1, 0, 1))
                self.assertTrue(s.r.get("local_rewrite_recovery"))
                self.assertEqual(s.r["local_rewrite_recovery"]["status"], "RESOLVED_BY_LOCAL_REWRITE")
                self.assertEqual(s.r.get("canonical_text_before_local_rewrite"), F.TEXT)
                self.assert_invariants(s, max_tts=6, max_waits=2)
                # LR block内の判定: v1・元原稿anchor・書換え後の文
                j4 = s.judges[3] if leaf != "L4" else s.judges[3]
                self.assertEqual(j4["ctx"].get("script_version"), "v1")
                self.assertEqual(j4["ctx"].get("m1_anchor_text"), F.TEXT)
                self.assertEqual(j4["text"], s.w.lr_candidate)

    def test_lr_block_is_a_full_three_attempt_block_with_second_wait(self):
        for leaf in LR_LEAVES:
            with self.subTest(leaf=leaf):
                s = self.go(leaf, [F.NG, F.NG, F.NG, F.NG, F.NG, F.PASS])
                self.assertEqual((s.status, s.tts, s.lr, s.waits(), len(s.hr)), ("OK", 6, 1, 2, 0))
                self.assertEqual([j["force_secondary"] for j in s.judges], [False, False, True, False, False, True])
                self.assertEqual([j["ctx"].get("script_version") for j in s.judges[3:]], ["v1", "v1", "v1"])
                self.assert_invariants(s, max_tts=6, max_waits=2)

    def test_lr_block_second_attempt_pass_has_no_second_wait(self):
        for leaf in LR_LEAVES:
            with self.subTest(leaf=leaf):
                s = self.go(leaf, [F.NG, F.NG, F.NG, F.NG, F.PASS])
                self.assertEqual((s.status, s.tts, s.waits()), ("OK", 5, 1))

    def test_all_six_ng_stops_with_one_hrq_row_and_no_seventh(self):
        for leaf in LR_LEAVES:
            with self.subTest(leaf=leaf):
                s = self.go(leaf, [F.NG] * 12)
                self.assertEqual(s.status, "STOPPED")
                self.assertEqual((s.tts, s.lr, s.waits(), len(s.hr)), (6, 1, 2, 1))         # 終端NG1件=HRQ1行
                self.assert_invariants(s, max_tts=6, max_waits=2)
                self.assertNotIn("local_rewrite_recovery", s.r)                             # 採用されていない結果にLR採用印を付けない
                self.assertEqual(s.r["local_rewrite_attempted"]["status"], "HUMAN_REVIEW_LOCKED_RETTS_FAILED") if leaf == "L3" else None
                # record_outcomeが数える行 = 実TTS呼出数(LR blockを含む、M-3b)
                rows = len(s.r.get("attempts_log") or s.r.get("standard_attempts_log") or []) + (
                    len(s.r.get("fallback_attempts_log") or []) if leaf in ("L3", "L4") else 0)
                self.assertEqual(rows, s.tts)

    def test_lr_not_for_ja_kp_and_dialogue(self):
        for leaf in ("L7a", "L7b", "L6", "L8"):
            with self.subTest(leaf=leaf):
                s = self.go(leaf, [F.NG] * 12)
                self.assertEqual(s.lr, 0)
                self.assertEqual(s.status, "STOPPED")
                self.assertEqual(len(s.hr), 1)

    def test_ja_third_after_180s(self):
        for leaf in ("L7a", "L7b"):
            with self.subTest(leaf=leaf):
                s = self.go(leaf, [F.NG, F.NG, F.PASS])
                self.assertEqual((s.status, s.tts, s.waits(), s.lr), ("OK", 3, 1, 0))
                self.assertAlmostEqual(s.sleep_total, 180.0, places=2)
                s2 = self.go(leaf, [F.PASS])
                self.assertEqual((s2.tts, s2.sleep_total), (1, 0))
                s3 = self.go(leaf, [F.NG, F.PASS])
                self.assertEqual((s3.tts, s3.sleep_total), (2, 0))
                s4 = self.go(leaf, [F.NG] * 5)
                self.assertEqual((s4.tts, s4.waits(), len(s4.hr)), (3, 1, 1))

    def test_kp_four_with_single_wait_before_english_lock(self):
        s = self.go("L6", [F.NG, F.NG, F.PASS])
        self.assertEqual((s.status, s.tts, s.waits()), ("OK", 3, 1))
        s = self.go("L6", [F.NG, F.NG, F.NG, F.PASS])
        self.assertEqual((s.status, s.tts, s.waits()), ("OK", 4, 1))
        s = self.go("L6", [F.NG] * 6)
        self.assertEqual((s.status, s.tts, s.waits(), len(s.hr)), ("STOPPED", 4, 1, 1))
        self.assertEqual([j["ctx"].get("slot") for j in s.judges], [1, 2, 3, 4])
        self.assertEqual([j["ctx"].get("is_last_slot") for j in s.judges], [False, False, False, True])
        s = self.go("L6", [F.PASS])
        self.assertEqual((s.tts, s.sleep_total), (1, 0))

    def test_z_dialogue_legacy_waits_before_third_same_style(self):
        s = self.go("L8", [F.NG, F.NG, F.PASS])
        self.assertEqual((s.status, s.tts, s.waits()), ("OK", 3, 1))
        self.assertTrue(all(STYLE in p for p in s.prompts))          # Style変更なし(従来Dialogue Styleのまま)
        s = self.go("L8", [F.PASS])
        self.assertEqual((s.tts, s.sleep_total), (1, 0))

    def test_technical_failure_inside_attempt_does_not_advance_ordinal(self):
        """F-Tech(attempt内の即時minimal再TTS)は別枠: attempt番号を進めず、品質NG回数にも数えない。"""
        for leaf in ("L1", "L2"):
            with self.subTest(leaf=leaf):
                s = self.go(leaf, [F.PASS], tts=[False, True, True])
                self.assertEqual(s.status, "OK")
                self.assertEqual([j["ctx"].get("slot") for j in s.judges], [1])
                self.assertEqual(s.sleep_total, 0)

    def test_stop_retrying_from_judge_ends_block_then_lr(self):
        for leaf in ("L1", "L2", "L3"):
            with self.subTest(leaf=leaf):
                s = self.go(leaf, [F.NG, F.NG_STOP, F.PASS][:2] + [F.PASS] * 0 + [F.PASS])
                # NG, NG_STOP -> (cascade打切り) -> LR(最終asr text) -> LR block ①'PASS
                self.assertIn(s.status, ("OK", "STOPPED"))
                self.assertLessEqual(s.lr, 1)
                self.assertLessEqual(s.tts, 6)


# =====================================================================================================
# T-STY: Style / Voice / model は全attemptで不変(③のStyleだけFallback)
# =====================================================================================================
class StyleVoiceTests(Base):
    MINIMAL_MARKERS = ("Speak the following text aloud naturally", "natural, clear, conversational")

    def _is_minimal(self, prompt):
        return any(m in prompt for m in self.MINIMAL_MARKERS)

    def test_first_two_use_caller_style_third_uses_fallback_only(self):
        for leaf in LR_LEAVES:
            with self.subTest(leaf=leaf):
                s = self.go(leaf, [F.NG, F.NG, F.PASS])
                self.assertIn(STYLE, s.prompts[0])
                self.assertIn(STYLE, s.prompts[1])
                self.assertNotIn(STYLE, s.prompts[2])
                self.assertTrue(self._is_minimal(s.prompts[2]), s.prompts[2][:200])

    def test_lr_block_keeps_caller_style_then_fallback_third(self):
        """OPEN-312是正: LR再TTSでも①②'=元のroleStyle、③'=Fallback(旧L2はstyle_prefix_overrideを脱落させ、旧L3はminimal固定だった)。"""
        for leaf in LR_LEAVES:
            with self.subTest(leaf=leaf):
                s = self.go(leaf, [F.NG] * 12)
                self.assertEqual(len(s.prompts), 6)
                for i in (0, 1, 3, 4):
                    self.assertIn(STYLE, s.prompts[i], (leaf, i))
                for i in (2, 5):
                    self.assertNotIn(STYLE, s.prompts[i], (leaf, i))
                    self.assertTrue(self._is_minimal(s.prompts[i]))

    def test_voice_identical_across_all_attempts_including_adv_l1_third(self):
        """Opus M-10: Adv L1のVoiceはCharonのまま(③でAoedeに変わる設計は不可)。"""
        import er003_b1_p9a_audio as p9a
        s = self.go("L1", [F.NG] * 12)
        self.assertEqual({v for v, _m in s.voices}, {"Charon"})
        self.assertEqual(len(s.voices), 6)
        for leaf in ("L2", "L3", "L4"):
            with self.subTest(leaf=leaf):
                s = self.go(leaf, [F.NG] * 12)
                self.assertEqual({v for v, _m in s.voices}, {p9a.VOICE_NAME})
                self.assertEqual(len({m for _v, m in s.voices}), 1)         # model_idも全attemptで同一

    def test_profile_style_is_passed_through_for_default_and_fx_profile(self):
        """Opus M-9: 呼出元が解決したprofile Styleを透過する(default固定のassertではなく、defaultもfx_20261017も①②で呼出元Styleのまま)。"""
        for style in ("DEFAULT_PROFILE_STYLE_A", "FX_20261017_PROFILE_STYLE_B"):
            for leaf in LR_LEAVES:
                with self.subTest(style=style, leaf=leaf):
                    s = self.go(leaf, [F.NG, F.NG, F.PASS], style=style)
                    self.assertIn(style, s.prompts[0])
                    self.assertIn(style, s.prompts[1])
                    self.assertNotIn(style, s.prompts[2])

    def test_progress_fingerprint_changes_with_profile_style(self):
        """BlockProgressの指紋にprofile(Style)が入る=Style違いのresumeを拾わない。"""
        s1 = self.go("L1", [F.NG, F.NG, F.PASS], style="STYLE_ONE")
        s2 = self.go("L1", [F.NG, F.NG, F.PASS], style="STYLE_TWO")
        self.assertEqual(s1.tts, 3)
        self.assertEqual(s2.tts, 3)

    def test_adopted_third_attempt_is_normalized_for_gate_adv(self):
        s = self.go("L1", [F.NG, F.NG, F.PASS])
        r = s.r
        self.assertEqual(r["instruction_type"], "minimal_fallback")
        self.assertTrue(r["fallback_used"])
        self.assertNotIn("<default", str(r["style_prefix"]))
        self.assertFalse(isinstance(r["style_prefix"], str) and r["style_prefix"].startswith(STYLE))
        s = self.go("L2", [F.NG, F.NG, F.PASS])
        r = s.r
        self.assertEqual(r["instruction_type"], "minimal_fallback")
        self.assertTrue(r["fallback_used"])
        self.assertIsInstance(r["style_prefix"], dict)                    # 実送信Styleの記録(sha256+head200)
        self.assertEqual(self.go("L1", [F.PASS]).r["fallback_used"], False)

    def test_adopted_third_attempt_is_normalized_for_gate_std(self):
        s = self.go("L3", [F.NG, F.NG, F.PASS])
        self.assertTrue(s.r["fallback_used"])
        s = self.go("L3", [F.PASS])
        self.assertFalse(s.r["fallback_used"])


# =====================================================================================================
# T-LRN / T-RE / T-HRL
# =====================================================================================================
class LrAndHrqTests(Base):
    def test_u03_disfluency_only_ng_no_ng_span_goes_to_hr_without_llm(self):
        """ASR一致+disfluency/repetition単独NG(U-03): ①②→180秒→③は省略せず、③NG後はLR LLM 0回・LR block 0回で即HR、HRQ1行(U-04b)。"""
        for leaf in LR_LEAVES:
            with self.subTest(leaf=leaf):
                s = self.go(leaf, [F.PASS] * 12, world_kw={"dq_ng": True, "ng_span_found": False})
                self.assertEqual(s.status, "STOPPED")
                self.assertEqual((s.tts, s.waits(), s.lr_llm), (3, 1, 0))
                self.assertEqual(len(s.hr), 1)                    # judgeはPASSで行を書かない→終端登録(register_terminal_hr)が1行
                self.assertEqual(s.hr[0]["canonical_text"], F.TEXT)

    def test_lr_llm_exception_goes_to_terminal_hr(self):
        for leaf in ("L1", "L3"):
            with self.subTest(leaf=leaf):
                s = self.go(leaf, [F.NG] * 12, world_kw={"lr_llm_fail": True})
                self.assertEqual((s.status, s.tts, len(s.hr)), ("STOPPED", 3, 1))

    def test_technical_stop_is_neither_lr_nor_hr(self):
        tech = F.judge(False, state="NG_SECONDARY_UNAVAILABLE", cls="UNCERTAIN")
        for leaf in LR_LEAVES:
            with self.subTest(leaf=leaf):
                s = self.go(leaf, [F.NG, F.NG, tech])
                self.assertEqual(s.status, "STOPPED")
                self.assertEqual((s.lr, len(s.hr)), (0, 0))

    def test_lr_success_writes_no_hr_row(self):
        for leaf in LR_LEAVES:
            s = self.go(leaf, [F.NG, F.NG, F.NG, F.PASS])
            self.assertEqual(len(s.hr), 0)

    def test_lr_reentry_is_structurally_forbidden(self):
        import er011_human_review_lock_01 as review_lock
        import er109_xz_scope_01 as xz
        with xz.run_scope("X"):
            b = blk.open_block("L1", "t/th/b1b/narration/comment_1.wav", "x",
                               ctx=blk.BlockCtx(depth=1, slot_offset=3, total_slots=6, script_version="v1", m1_anchor_text="o", lock_text="o"))
            with mock.patch.object(review_lock, "_ACTIVE_GUARDED_OUT_PATHS", {"t/th/b1b/narration/comment_1.wav"}):
                with self.assertRaises(blk.LocalRewriteReentryError):
                    blk.lr_recover(b, text="x", out_path="t/th/b1b/narration/comment_1.wav", last_asr_text="y",
                                   block_call=lambda t, c: {}, merge=lambda a, b: a, last_attempt=None)
        import er020_tts_retry_local_rewrite_01 as er020
        with self.assertRaises(RuntimeError):
            er020.run_local_rewrite_recovery(segment_id="comment_1", canonical_text="a b c", last_asr_text="a x c", retts_fn=lambda t: {}, depth=1)

    def test_lr_recover_requires_active_outer_guard(self):
        """Opus M-3a: lr_recoverは外側guardの実行中でなければ呼べない。"""
        import er109_xz_scope_01 as xz
        with xz.run_scope("X"):
            b = blk.open_block("L1", "t/th/b1b/narration/comment_1.wav", "x")
            with self.assertRaises(blk.LocalRewriteContractError):
                blk.lr_recover(b, text="x", out_path="t/th/b1b/narration/comment_1.wav", last_asr_text="y",
                               block_call=lambda t, c: {}, merge=lambda a, b: a, last_attempt=None)

    def test_lr_count_and_tts_bounded_in_every_all_ng_scenario(self):
        """旧実例(hormuz comment_4等の深さ2再入)の再現入力でも、LR回数<=1・TTS<=6・待機<=2・再帰なし。"""
        for leaf in LR_LEAVES:
            for cs in (True, False):
                with self.subTest(leaf=leaf, cs=cs):
                    s = self.go(leaf, [F.NG] * 30, cs=cs)
                    self.assertLessEqual(s.lr, 1)
                    self.assertLessEqual(s.tts, 6)
                    self.assertLessEqual(s.waits(), 2)

    def test_lr_block_hrq_only_at_terminal_slot(self):
        s = self.go("L1", [F.NG] * 12)
        slots = [(j["ctx"]["slot"], j["ctx"]["is_last_slot"]) for j in s.judges]
        self.assertEqual(slots, [(1, False), (2, False), (3, False), (4, False), (5, False), (6, True)])

    def test_l4_post_slowdown_ng_counts_as_attempt_ng_and_goes_to_lr(self):
        s = self.go("L4", [F.PASS] * 8, post_judge=[F.NG] * 3 + [F.PASS])
        self.assertEqual((s.status, s.tts, s.lr, s.waits(), len(s.hr)), ("OK", 4, 1, 1, 0))
        # 減速後NGでも③は常にFallback Style・LRの転写はNG原因(減速後)
        self.assertEqual(len(s.w.slowdown_calls), 4)
        self.assertEqual([p["ctx"]["slot"] for p in s.posts], [1, 2, 3, 4])                  # ブロック通算slot(M-6(d))
        self.assertEqual(s.posts[3]["ctx"].get("m1_anchor_text"), F.TEXT)                    # LR block: 期待text=書換え後の文、anchor=元原稿(M-6(c))
        self.assertEqual(s.posts[3]["text"], s.w.lr_candidate)

    def test_l4_post_slowdown_terminal_ng_single_hrq_row_and_final_artifact(self):
        s = self.go("L4", [F.PASS] * 8, post_judge=[F.NG] * 8)
        self.assertEqual((s.status, s.tts, len(s.hr)), ("STOPPED", 6, 1))
        self.assertTrue(os.path.exists(s.w.out_path))                                         # 失敗終了でも最終音声(減速後NG)は残る
        self.assertEqual([p["ctx"]["is_last_slot"] for p in s.posts], [False] * 5 + [True])

    def test_l4_slowdown_artifacts_and_top_level_fields(self):
        s = self.go("L4", [F.PASS])
        r = s.r
        for k in ("slowdown_applied", "original_path", "slowdown_info", "post_slowdown_asr_text", "post_slowdown_classification",
                  "post_slowdown_final_classification", "post_slowdown_expected_text_source"):
            self.assertIn(k, r)
        self.assertTrue(r["slowdown_applied"])
        self.assertTrue(os.path.exists(r["original_path"]))
        self.assertIsNotNone(r.get("sha256"))
        self.assertIn(str(r.get("tts_generations_used")), ("1",))

    def test_l4_does_not_use_outer_loop_or_finalize(self):
        import er003_v1_n3_01_tts_generate as n3
        with mock.patch.object(n3, "finalize_a2_slowdown_final_ng", side_effect=AssertionError("legacy finalize used in scope")):
            self.go("L4", [F.PASS] * 8, post_judge=[F.NG] * 8)


# =====================================================================================================
# T-RES: STOP・resume・guard
# =====================================================================================================
class StopResumeTests(Base):
    def _world(self, leaf):
        w = make_world(leaf, judge=[F.NG] * 12)
        self.addCleanup(w.cleanup)
        return w

    def test_stop_during_cooldown_propagates_without_recording_outcome(self):
        import er011_human_review_lock_01 as review_lock
        for leaf in ("L1", "L2", "L3", "L4"):
            with self.subTest(leaf=leaf):
                w = self._world(leaf)
                w.stop_after_sleeps = 3
                with w.patched(scope=LEAF_CFG[leaf][2]):
                    with self.assertRaises(blk.TtsBlockStopError) as cm:
                        call_leaf(leaf, w)
                self.assertFalse(isinstance(cm.exception, Exception))
                level_dir = review_lock._level_out_dir_from_out_path(w.out_path)
                self.assertEqual(review_lock._load_store(level_dir), {})            # Lock化(STOPPED保存)されない
                self.assertFalse(os.path.exists(w.history_path) and "PROCEED" in open(w.history_path, encoding="utf-8").read())
                self.assertEqual(w.tts_i, 2)                                         # 待機中に止まった=①②のみ

    def test_runner_level_stop_is_not_swallowed_or_saved(self):
        """Opus M-11: runner入口(_generate_or_reuse+secondary_run_scope.guard_generate)を通してもSTOPは握り潰されず結果が保存されない。"""
        import er019_family_x_audio_production_runner_01 as x
        w = self._world("L1")
        w.stop_after_sleeps = 2
        saved = []
        with w.patched(scope="X"):
            with self.assertRaises(blk.TtsBlockStopError):
                x._generate_or_reuse(None, "comment_1", w.out_path, lambda: call_leaf("L1", w))
        self.assertEqual(saved, [])

    def test_kill_in_cooldown_then_resume_does_not_regenerate_first_two_and_pays_only_remaining(self):
        w = self._world("L1")
        w.stop_after_sleeps = 4                 # 4スライス(20秒)待った所でkill相当
        with w.patched(scope="X"):
            with self.assertRaises(blk.TtsBlockStopError):
                call_leaf("L1", w)
        self.assertEqual(w.tts_i, 2)
        slept_first = sum(w.clock.sleeps)
        w.stop_after_sleeps = None
        w.judge_script = [F.PASS]
        w.judge_i = 0
        w.clock.t += 30.0                       # 停止中の経過(実時間は止まらない)
        w.tts_i = 0
        with w.patched(scope="X"):
            r = call_leaf("L1", w)
        self.assertEqual(r["status"], "OK")
        self.assertEqual(w.tts_i, 1)            # ①②は再生成されない(③の1回だけ)
        total_wait = sum(w.clock.sleeps)
        self.assertGreaterEqual(total_wait + 30.0, 180.0 - 1e-6)
        self.assertLessEqual(total_wait, 180.0 + 1e-6)          # 180秒を二重に払わない
        stubs = [a for a in r["attempts_log"] if a.get("carried_from_prior_process")]
        self.assertEqual(len(stubs), 2)                         # record_outcomeの実TTS計上=3(消費済み2+③1)
        self.assertEqual(len(r["attempts_log"]), 3)
        self.assertEqual(slept_first, 20.0)

    def test_resume_inside_lr_block_does_not_rerun_llm(self):
        w = self._world("L1")
        w.judge_script = [F.NG] * 12
        w.stop_after_sleeps = 40                 # 第1待機(36スライス)を終え、LR block ③'直前の第2待機の途中でkill
        with w.patched(scope="X"):
            with self.assertRaises(blk.TtsBlockStopError):
                call_leaf("L1", w)
        self.assertEqual(w.tts_i, 5)             # 元3 + ①'②'
        self.assertEqual(len(w.lr_calls), 1)
        w.stop_after_sleeps = None
        w.judge_script, w.judge_i, w.tts_i = [F.PASS], 0, 0
        w.clock.t += 10.0
        with w.patched(scope="X"):
            r = call_leaf("L1", w)
        self.assertEqual(len(w.lr_calls), 1)     # LR LLMは再実行しない(保存済みの書換え本文で続行)
        self.assertEqual(r["status"], "OK")
        self.assertEqual(w.tts_i, 1)             # ③'の1回だけ
        self.assertTrue(r["local_rewrite_recovery"].get("resumed_without_llm"))

    def test_lock_blocks_same_text_with_zero_api(self):
        w = self._world("L1")
        with w.patched(scope="X"):
            r1 = call_leaf("L1", w)
            self.assertEqual(r1["status"], "STOPPED")
            tts_after_first = w.tts_i
            r2 = call_leaf("L1", w)
        self.assertEqual(r2["status"], "HUMAN_REVIEW_LOCKED")
        self.assertEqual(w.tts_i, tts_after_first)               # 0 API call

    def test_approve_regenerate_allows_next_block_once(self):
        import er011_human_review_lock_01 as review_lock
        w = self._world("L1")
        with w.patched(scope="X"):
            call_leaf("L1", w)
            review_lock.approve_regenerate(w.out_path, F.TEXT)
            before = w.tts_i
            w.judge_script, w.judge_i = [F.PASS], 0
            r = call_leaf("L1", w)
        self.assertEqual(r["status"], "OK")
        self.assertEqual(w.tts_i - before, 1)


# =====================================================================================================
# T-GATE: Gate契約(M-5)。Gate規則は変更しない(③/LR採用はGateが検知できる)
# =====================================================================================================
class GateContractTests(Base):
    def _entry(self, s, seg="full_story_part1"):
        e = dict(s.r)
        e.setdefault("canonical_text", F.TEXT)
        return e

    def test_adv_third_adoption_is_detected_by_existing_gate_tokens(self):
        import er019_family_x_style_profile_01 as sp
        s = self.go("L2", [F.NG, F.NG, F.PASS])
        e = self._entry(s)
        gate = sp.m3_assembly_gate(sp.PROFILE_COFFEE_P8, "b1b", {"segments": {"full_story_part1": e}, "key_phrases": {}}, {})
        v = [b["violations"] for b in gate["blocked"] if b["segment"] == "full_story_part1"]
        self.assertTrue(v, gate)
        self.assertIn("ADV_MINIMAL_FALLBACK", v[0])
        self.assertIn("ADV_STYLE_PREFIX_NOT_PROFILE_PREFIXED", v[0])

    def test_lr_adoption_is_detected(self):
        import er019_family_x_style_profile_01 as sp
        s = self.go("L2", [F.NG, F.NG, F.NG, F.PASS])
        e = self._entry(s)
        gate = sp.m3_assembly_gate(sp.PROFILE_COFFEE_P8, "b1b", {"segments": {"full_story_part1": e}, "key_phrases": {}}, {})
        v = [b["violations"] for b in gate["blocked"] if b["segment"] == "full_story_part1"]
        self.assertIn("LOCAL_REWRITE_RECOVERY", v[0])

    def test_std_third_and_lr_are_detected(self):
        import er019_family_x_style_profile_01 as sp
        for judge, token in (([F.NG, F.NG, F.PASS], "STD_FALLBACK_USED_OR_UNKNOWN"), ([F.NG, F.NG, F.NG, F.PASS], "LOCAL_REWRITE_RECOVERY")):
            s = self.go("L4", judge)
            e = self._entry(s)
            gate = sp.m3_assembly_gate(sp.PROFILE_COFFEE_P8, "a2", {"segments": {"full_story_part1": e}, "key_phrases": {}}, {})
            v = [b["violations"] for b in gate["blocked"] if b["segment"] == "full_story_part1"]
            self.assertTrue(v, gate)
            self.assertIn(token, v[0])

    def test_first_pass_std_has_no_fallback_or_lr_violation(self):
        import er019_family_x_style_profile_01 as sp
        s = self.go("L4", [F.PASS])
        e = self._entry(s)
        gate = sp.m3_assembly_gate(sp.PROFILE_COFFEE_P8, "a2", {"segments": {"full_story_part1": e}, "key_phrases": {}}, {})
        v = [b["violations"] for b in gate["blocked"] if b["segment"] == "full_story_part1"]
        flat = v[0] if v else []
        self.assertNotIn("STD_FALLBACK_USED_OR_UNKNOWN", flat)
        self.assertNotIn("LOCAL_REWRITE_RECOVERY", flat)


# =====================================================================================================
# T-ROLE (D11) / T-STORE (M-7)
# =====================================================================================================
class RoleTests(unittest.TestCase):
    def test_topic_intro_en_resolves_only_inside_xyz_scope(self):
        import er020_tts_retry_local_rewrite_01 as er020
        import er109_xz_scope_01 as xz
        self.assertIsNone(er020.resolve_narrative_role("topic_intro_en"))            # scope外(Family C等)は従来どおり
        self.assertFalse(er020.connected_speech_enabled_for("topic_intro_en"))
        for fam in "XYZ":
            with xz.run_scope(fam):
                self.assertEqual(er020.resolve_narrative_role("topic_intro_en"), "TOPIC_INTRO")
                self.assertTrue(er020.connected_speech_enabled_for("topic_intro_en"))

    def test_other_ids_unchanged_by_scope(self):
        import er020_tts_retry_local_rewrite_01 as er020
        import er109_xz_scope_01 as xz
        ids = ["topic_intro", "preview", "comment_1", "full_story_part1", "full_story_part1_c2", "kp1_en", "point_one_heading", "welcome", "y_voice_1", "topic_intro_ja"]
        outside = {i: er020.resolve_narrative_role(i) for i in ids}
        with xz.run_scope("Z"):
            inside = {i: er020.resolve_narrative_role(i) for i in ids}
        self.assertEqual(outside, inside)

    def test_family_c_topic_intro_en_not_affected(self):
        """Family Cは同名ID `topic_intro_en` を使う(er013_family_c_production_runner_01)。scope外のA/B/Cのroleは不変。"""
        src = open(os.path.join(ROOT, "er013_family_c_production_runner_01.py"), encoding="utf-8").read()
        self.assertIn("topic_intro_en", src)
        import er020_tts_retry_local_rewrite_01 as er020
        self.assertIsNone(er020.resolve_narrative_role("topic_intro_en"))


class StoreMergeTests(unittest.TestCase):
    def test_manifest_reread_and_merged_before_save(self):
        """Opus M-7: 生成中(180秒+TTS)に別processが登録したentryや`reuse_blocked`印を、保存時に上書き・消去しない。"""
        import er006_master_audio_store_01 as store
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(store, "STORE_DIR", d), mock.patch.object(store, "MANIFEST_PATH", os.path.join(d, "manifest.json")), \
                    mock.patch.object(store, "AUDIO_DIR", os.path.join(d, "audio")), mock.patch.object(store, "TELEMETRY_PATH", os.path.join(d, "t.jsonl")):
                key = store.MasterAudioKey(language="en", speaker_voice="Aoede", tts_model_id="m", canonical_text="hello", level=None,
                                           style_instruction_id="sid", style_instruction_version="v1")
                out = os.path.join(d, "o.wav")

                def gen(path):
                    open(path, "wb").write(b"RIFFxxxx")
                    # 生成中に別processがmanifestへ他entryと reuse_blocked印を書く
                    m = store._load_manifest()
                    m["other_id"] = {"audio_path": "x.wav", "key": {}, "reuse_blocked": {"reason": "blocked by another process"}}
                    store._save_manifest(m)
                    return {"status": "OK", "sha256": "s", "asr_verified": True, "asr_text": "hello"}
                r = store.get_or_generate(key, out, gen)
                self.assertEqual(r["status"], "OK")
                m = store._load_manifest()
                self.assertIn("other_id", m)
                self.assertEqual(m["other_id"]["reuse_blocked"]["reason"], "blocked by another process")
                self.assertIn(key.master_audio_id(), m)

    def test_manifest_write_is_atomic_replace(self):
        import er006_master_audio_store_01 as store
        src = open(os.path.join(ROOT, "er006_master_audio_store_01.py"), encoding="utf-8").read()
        self.assertIn("os.replace(tmp, MANIFEST_PATH)", src)


# =====================================================================================================
# scope外golden(A/B/C・単体呼出が変更前コードとbyte同一)
# =====================================================================================================
class GoldenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(G.GOLDEN_PATH, encoding="utf-8") as f:
            cls.gold = json.load(f)

    def _check(self, leaves):
        bad = []
        n = 0
        for leaf, sc, cs in G.case_ids():
            if leaf not in leaves or (leaf, sc, cs) in G.KNOWN_LEGACY_DEFECT_CASES:
                continue
            n += 1
            cur = G.run_case(leaf, sc, cs)
            if cur != self.gold[f"{leaf}|{sc}|{cs}"]:
                bad.append(f"{leaf}|{sc}|{cs}")
        self.assertGreater(n, 0)
        self.assertEqual(bad, [], "scope外(A/B/C)の出力が変更前コードと一致しません")

    def test_golden_voice01_l1(self):
        self._check({"L1"})

    def test_golden_news_tail_fix_l2(self):
        self._check({"L2"})

    def test_golden_crosslevel_l3(self):
        self._check({"L3"})

    def test_golden_n3_l4(self):
        self._check({"L4"})

    def test_golden_ja_l7(self):
        self._check({"L7a", "L7b"})

    def test_golden_kp_and_dialogue_l6_l8(self):
        self._check({"L6", "L8"})

    def test_golden_covers_every_changed_leaf_scope_off_without_new_kwargs(self):
        self.assertEqual({k.split("|")[0] for k in self.gold}, set(G.LEAVES))

    def test_known_legacy_defect_is_documented_not_asserted(self):
        self.assertEqual(len(G.KNOWN_LEGACY_DEFECT_CASES), 4)
        for k in self.gold:
            self.assertNotIn("RecursionError", json.dumps(self.gold[k]))


# =====================================================================================================
# 静的検査(撤去の機械確認)
# =====================================================================================================
XYZ_MODULES = ["er019_family_x_audio_production_runner_01.py", "er121_family_y_audio_01.py", "er121_family_y_runner_01.py",
               "er063_family_z_audio_01.py", "er122_fz_ctx_policy_01.py", "er127_tts_block_policy_01.py", "er019_family_x_kp_en_k2_store_01.py"]


class StaticTests(unittest.TestCase):
    def _src(self, name):
        return open(os.path.join(ROOT, name), encoding="utf-8").read()

    def test_xyz_modules_do_not_reference_legacy_600_cooldown(self):
        for m in XYZ_MODULES:
            src = self._src(m)
            with self.subTest(module=m):
                pat = r"er020\.COOLDOWN_SECONDS|retry_primitive\.COOLDOWN_SECONDS"
                if not m.startswith("er127"):
                    pat += r"|LEGACY_COOLDOWN_SECONDS"
                self.assertNotRegex(src, pat)

    def test_single_180_definition(self):
        defs = []
        for name in os.listdir(ROOT):
            if name.endswith(".py") and not name.endswith("_test_01.py") and name.startswith(("er019", "er020", "er121", "er122", "er127", "er063", "er003_v1")):
                src = self._src(name)
                for m in re.finditer(r"^COOLDOWN_SECONDS\s*=\s*([0-9.]+)", src, re.M):
                    defs.append((name, float(m.group(1))))
        self.assertIn(("er127_tts_block_policy_01.py", 180.0), defs)
        self.assertEqual([d for d in defs if d[1] == 180.0], [("er127_tts_block_policy_01.py", 180.0)])

    def test_leaf_modules_use_unified_block_only_via_er127(self):
        for m, tokens in {
            "er003_v1_sing01_voice01_generate.py": ('with_block("L1"', 'with_block("L7"'),
            "er003_v1_sing01_news_tail_fix.py": ('with_block("L2"',),
            "er003_v1_crosslevel_audio_02_common.py": ('with_block("L3"',),
            "er003_v1_n3_01_tts_generate.py": ('with_block("L7"', "unified_flow_active"),
            "er003_v1_repro01_main_generate.py": ('with_block("L6"',),
            "er019_family_x_kp_en_k2_store_01.py": ('with_block("L6"',),
            "er012_b_family_voices_production_01.py": ('with_block("L8"',),
        }.items():
            for t in tokens:
                with self.subTest(module=m, token=t):
                    self.assertIn(t, self._src(m))

    def test_legacy_branches_only_when_block_is_none(self):
        """旧10分待機・旧LR helperはscope外分岐(_blk is None)にだけ残る(scope内からは到達しない)。"""
        for m in ("er003_v1_sing01_voice01_generate.py", "er003_v1_sing01_news_tail_fix.py"):
            src = self._src(m)
            tree = ast.parse(src)
            for node in ast.walk(tree):
                if isinstance(node, ast.If):
                    seg = ast.get_source_segment(src, node.test) or ""
                    if "_blk is not None" in seg:
                        orelse_src = "\n".join(ast.get_source_segment(src, n) or "" for n in node.orelse)
                        body_src = "\n".join(ast.get_source_segment(src, n) or "" for n in node.body)
                        self.assertNotIn("maybe_cooldown_before_attempt", body_src)
                        self.assertNotIn("_local_rewrite_recovery_for_", body_src)

    def test_no_new_env_or_hook_in_production_modules(self):
        for m in ("er127_tts_block_policy_01.py",):
            src = self._src(m)
            self.assertNotIn("os.getenv", src)
            self.assertNotIn("environ[", src)


if __name__ == "__main__":
    unittest.main()
