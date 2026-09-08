# ============================================================
# er011_open112_trend_synthesis_mode_production_wiring_01_test_01.py
# OPEN-112-TREND-SYNTHESIS-MODE-PRODUCTION-WIRING-01: Gate 3配線の単体
# テスト(無料、API呼び出し無し)。
# ============================================================
# 1. build_common_block()の既定挙動(editorial_type_module_block未指定)
#    が、配線前(git HEAD時点、fixtures/配下に固定保存)とバイト単位で
#    完全一致することを固定する(既存A-Family出力への影響ゼロを保証)。
# 2. editorial_mode="trend_synthesis"を指定した場合にFocus Module/
#    Engagement原則が実際に注入されることを確認する。
# 3. Diagnostic Full Retry経路(build_diagnostic_retry_prompt)が、
#    editorial_type_module_blockを含む元のprompt文字列をそのまま
#    引き継ぐ(通常modeへ落ちない)ことをコードレベルで確認する。
# 4. 未知のeditorial_modeに対してfail-closedでValueErrorを送出すること。
from __future__ import annotations

import os
import unittest

import er003_v1_n3_01_articles_generate as gen

FIXTURE_DIR = "er011_output/open112_trend_synthesis_mode_production_wiring_01/fixtures"

MASTER = "MASTER TEXT sample\n日本語 including unicode\nline2"
TOPIC = "TOPIC sample テーマ"
LEDGER = "LEDGER sample\n[F-001] fact one\n[F-002] fact two"


def _read_fixture(name: str) -> str:
    with open(os.path.join(FIXTURE_DIR, name), encoding="utf-8") as f:
        return f.read()


class TestBuildCommonBlockDefaultByteParity(unittest.TestCase):
    """既定値(editorial_type_module_block未指定)でのCOMMON_BLOCK_TEMPLATE
    出力が、配線前(git HEAD、Gate 3着手前)にfixturesへ固定保存した出力と
    バイト単位で完全一致することを確認する。fixturesは、配線前コードを
    git showで取得して同一入力で実際に生成したもの(手作業での再現では
    ない)。"""

    def test_default_matches_pre_wiring_baseline(self):
        out = gen.build_common_block(MASTER, TOPIC, LEDGER)
        expected = _read_fixture("common_block_baseline_default.txt")
        self.assertEqual(out, expected)

    def test_default_with_shared_point_blueprint_block_matches_pre_wiring_baseline(self):
        out = gen.build_common_block(MASTER, TOPIC, LEDGER,
                                      shared_point_blueprint_block="BLUEPRINT_BLOCK_SAMPLE")
        expected = _read_fixture("common_block_baseline_with_blueprint.txt")
        self.assertEqual(out, expected)

    def test_default_with_evidence_compression_matches_pre_wiring_baseline(self):
        out = gen.build_common_block(MASTER, TOPIC, LEDGER, evidence_compression=True)
        expected = _read_fixture("common_block_baseline_with_ec.txt")
        self.assertEqual(out, expected)

    def test_editorial_type_module_block_placeholder_never_leaks_into_default_output(self):
        out = gen.build_common_block(MASTER, TOPIC, LEDGER)
        self.assertNotIn("{editorial_type_module_block}", out)
        self.assertNotIn("editorial_type_module_block", out)


class TestTrendSynthesisModeInjection(unittest.TestCase):
    def test_resolve_editorial_type_module_block_none_returns_empty_string(self):
        self.assertEqual(gen.resolve_editorial_type_module_block(None), "")
        self.assertEqual(gen.resolve_editorial_type_module_block(""), "")

    def test_resolve_editorial_type_module_block_unknown_mode_raises(self):
        with self.assertRaises(ValueError):
            gen.resolve_editorial_type_module_block("not_a_real_mode")

    def test_trend_synthesis_mode_injects_focus_module_and_engagement_block(self):
        block = gen.resolve_editorial_type_module_block("trend_synthesis")
        out = gen.build_common_block(MASTER, TOPIC, LEDGER, editorial_type_module_block=block)
        self.assertIn("Trend Synthesis Focus", out)
        self.assertIn("counter-signal", out)
        self.assertIn("Interesting/Engaging/Entertaining原則", out)
        self.assertIn("時系列の出来事列挙にしない", out)

    def test_trend_synthesis_module_inserted_immediately_before_spoken_first_anchor(self):
        block = gen.resolve_editorial_type_module_block("trend_synthesis")
        out = gen.build_common_block(MASTER, TOPIC, LEDGER, editorial_type_module_block=block)
        anchor = "【Spoken-first原則(数字の扱い)】"
        idx_anchor = out.index(anchor)
        idx_focus = out.index("Trend Synthesis Focus")
        idx_engagement = out.index("Interesting/Engaging/Entertaining原則")
        # Focus Module → Engagement Block → Anchorの順で、Anchor直前に連続して
        # 挿入されていること(Trial-09/10と同一の挿入位置パターン)。
        self.assertLess(idx_focus, idx_engagement)
        self.assertLess(idx_engagement, idx_anchor)
        gap = out[idx_engagement:idx_anchor]
        # EngagementブロックとAnchorの間に「\n\n」以外の余計な地の文が
        # 挟まっていないこと(Engagementブロック本文終端から直接Anchorへ
        # つながる)。
        self.assertTrue(gap.rstrip().endswith("throughlineを持つことを優先してください。"""))

    def test_trend_synthesis_module_not_injected_when_mode_not_specified(self):
        out = gen.build_common_block(MASTER, TOPIC, LEDGER)
        self.assertNotIn("Trend Synthesis Focus", out)
        self.assertNotIn("Interesting/Engaging/Entertaining原則", out)


class TestDiagnosticFullRetryPreservesEditorialMode(unittest.TestCase):
    """Diagnostic Full Retry(run_one_pattern内のPoint Overlap NG retry)は
    build_diagnostic_retry_prompt(original_prompt, ...)で「original_prompt
    + 診断セクション」を返すだけで、COMMON_BLOCK_TEMPLATEやbuild_common_
    block()を再呼び出ししない(er003_v1_n3_01_articles_generate.py内の
    run_one_pattern実装、diagnostic_promptの構築箇所を参照)。そのため、
    original_promptに含まれるeditorial_type_module_blockの内容は、retry
    後も文字列としてそのまま保持される。本テストはこの結合の性質を
    build_diagnostic_retry_prompt()を直接呼び出すことで確認する(API
    呼び出し無し、ダミーarticle_textを使用)。"""

    def test_diagnostic_retry_prompt_preserves_editorial_module_text(self):
        block = gen.resolve_editorial_type_module_block("trend_synthesis")
        common_block = gen.build_common_block(MASTER, TOPIC, LEDGER, editorial_type_module_block=block)
        original_prompt = gen.build_prompt(common_block, gen.B1_B_DIRECT_INSTRUCTION)
        self.assertIn("Trend Synthesis Focus", original_prompt)

        dummy_article = (
            "# Title\n\nSome main story text here that is long enough to be treated as a "
            "full story paragraph for the point overlap QA splitter to find.\n\n"
            "### A first heading\n\nPoint one body text.\n\n"
            "### A second heading\n\nPoint two body text.\n\n"
            "## In one line\n\nA short closing line."
        )
        point_overlap = {
            "point_one": {"overlap_ratio": 0.5, "flagged": True, "shared_words": ["sample"], "threshold": 0.40},
            "point_two": {"overlap_ratio": 0.1, "flagged": False, "shared_words": [], "threshold": 0.40},
        }
        retry_prompt = gen.build_diagnostic_retry_prompt(original_prompt, dummy_article, point_overlap)

        # original_promptの全文(Trend Synthesis Focus Module含む)が、retry
        # prompt内にそのまま部分文字列として残っていること(モード引き継ぎの
        # 直接的な証拠)。
        self.assertIn(original_prompt, retry_prompt)
        self.assertIn("Trend Synthesis Focus", retry_prompt)
        self.assertIn("Interesting/Engaging/Entertaining原則", retry_prompt)
        self.assertGreater(len(retry_prompt), len(original_prompt))


class TestRunWriterForThemeEditorialModeParam(unittest.TestCase):
    """er006_pool_pilot_01_writer.py::run_writer_for_theme()(Production
    Writer正式初回path)の新規引数editorial_mode/trend_gate_checklistが、
    build_common_block()呼び出しへ正しくスレッドされることを、実際の
    ソースコードから静的に確認する(API呼び出し無し)。"""

    def test_writer_module_source_threads_editorial_mode_into_build_common_block(self):
        import er006_pool_pilot_01_writer as writer_mod
        import inspect
        source = inspect.getsource(writer_mod.run_writer_for_theme)
        self.assertIn("editorial_mode", source)
        self.assertIn("resolve_editorial_type_module_block", source)
        self.assertIn("editorial_type_module_block=editorial_type_module_block", source)
        self.assertIn("trend_gate_checklist", source)


if __name__ == "__main__":
    unittest.main()
