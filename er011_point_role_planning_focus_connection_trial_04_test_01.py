# ============================================================
# er011_point_role_planning_focus_connection_trial_04_test_01.py
# 管理ID: FAMILY-A-DISCOVERY-FOCUS-ROLE-PLANNING-CONNECTION-TRIAL-01
# (Fable修正指示1回目、STOP解除、手順2のGate 4相当機械検証)
# ============================================================
# API呼び出しは一切行わない(FakeClient/mock.patchのみ、実費¥0)。
# 本ファイルはテストのみで、Production/SSOTは編集しない。
# unittest.mock.patch.objectは標準的なテスト技法であり、
# er011_point_role_planning_focus_connection_trial_04.py(実装本体)は
# 一切monkeypatchを行っていない(patchはこのテストファイルの中でのみ、
# テスト実行中だけ有効)。
#
# 検証項目(手順2):
#   (i)   Gate 4静的確認: Production `run_one_pattern`のソースへ既知の
#         置換規則を機械的に適用した結果が、trial_04の
#         `run_one_pattern_connected`のソースとバイト単位で完全一致する
#         こと(差分がhint注入関連の4点のみであることの機械証明)。
#   (ii)  LLMモック統合テスト: point_role_hint_block=""の場合、
#         Production版run_one_patternと新コピーrun_one_pattern_connected
#         の出力(Point Role Planningへ送るprompt文字列、結果構造)が
#         バイト一致すること。
#   (iii) hint指定時、Point Role Planningのprompt文字列にhintが含まれ、
#         Writer本文へ渡されるprompt_with_plan(Writer promptの他部分)は
#         hint有無で不変であること(FakeClientが決定論的な計画JSONを返す
#         ため、hintの影響がRole Planningのrequest側のみに閉じることを
#         機械的に示す)。
# ============================================================
from __future__ import annotations

import difflib
import inspect
import json
import re
import shutil
import tempfile
import unittest
from unittest import mock

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as prod_gen
import er008_directional_fact_precheck_08 as dfp
import er011_point_role_planning_focus_connection_trial_04 as t4
import er011_point_role_value_planning_01 as point_planning

GOOD_PLAN = {
    "point_one": {
        "role": "a methodological nuance", "new_listener_takeaway": "why the comparison is fair",
        "evidence_anchor": "the fixture ledger fact one", "why_it_matters": "it shows the effect is real",
        "must_not_overlap_with_full_story": "the headline finding itself",
        "must_not_overlap_with_other_point": "the psychological reason people comply",
    },
    "point_two": {
        "role": "a psychological reason", "new_listener_takeaway": "why people follow suggested amounts",
        "evidence_anchor": "the fixture ledger fact two",
        "why_it_matters": "it explains listener's own behavior",
        "must_not_overlap_with_full_story": "the headline finding itself",
        "must_not_overlap_with_other_point": "the methodological nuance",
    },
}

FIXED_ARTICLE_TEXT = "## Full Story\nfixture full story text.\n\n## Point One\nfixture point one.\n\n## Point Two\nfixture point two.\n"


# ============================================================
# (i) Gate 4静的確認: ソース再構成による機械証明
# ============================================================
class Gate4SourceReconstructionTests(unittest.TestCase):
    """Production run_one_patternのソースへ既知の置換規則を機械的に適用し、
    trial_04のrun_one_pattern_connectedのソースとバイト単位で一致する
    ことを確認する。単なる目視diffではなく、再現可能な機械証明。"""

    BARE_NAMES = [
        "_writer_process", "_generate_and_compress_article", "run_point_overlap_qa_and_regenerate",
        "split_common_sections_for_point_qa", "build_diagnostic_retry_prompt", "compute_metrics",
        "normalize_article_formatting", "POINT_OVERLAP_ARTICLE_RETRY_MAX", "POINT_TARGET_LOWER",
        "POINT_TARGET_UPPER", "POINT_TOLERANCE_LOWER", "POINT_TOLERANCE_UPPER", "TOTAL_SOFT_LOWER",
        "TOTAL_SOFT_UPPER", "REASONING_EFFORT",
    ]

    def _reconstruct(self) -> tuple:
        prod_src = inspect.getsource(prod_gen.run_one_pattern)
        src = prod_src

        old_sig = ('def run_one_pattern(client, theme_id: str, label: str, prompt: str, verified_ledger_text: str,\n'
                    '                     topic: str, out_dir: str, apply_evidence_compression: bool = True,\n'
                    '                     apply_directional_fact_precheck: bool = True) -> dict:')
        new_sig = ('def run_one_pattern_connected(client, theme_id: str, label: str, prompt: str, verified_ledger_text: str,\n'
                    '                     topic: str, out_dir: str, apply_evidence_compression: bool = True,\n'
                    '                     apply_directional_fact_precheck: bool = True,\n'
                    '                     point_role_hint_block: str = "") -> dict:')
        self.assertEqual(src.count(old_sig), 1, "signature not found exactly once in production source")
        src = src.replace(old_sig, new_sig)

        old_call1 = ('    role_plan_result = point_planning.run_point_role_planning(\n'
                     '        client, topic, verified_ledger_text, model=writer_model, reasoning_effort=REASONING_EFFORT)')
        new_call1 = ('    role_plan_result = run_point_role_planning_connected(\n'
                     '        client, topic, verified_ledger_text, model=writer_model, reasoning_effort=REASONING_EFFORT,\n'
                     '        point_role_hint_block=point_role_hint_block)')
        self.assertEqual(src.count(old_call1), 1, "initial role plan call not found exactly once")
        src = src.replace(old_call1, new_call1)

        old_call2 = ('        role_plan_result = point_planning.run_point_role_planning(\n'
                     '            client, topic, verified_ledger_text, model=writer_model, reasoning_effort=REASONING_EFFORT)')
        new_call2 = ('        role_plan_result = run_point_role_planning_connected(\n'
                     '            client, topic, verified_ledger_text, model=writer_model, reasoning_effort=REASONING_EFFORT,\n'
                     '            point_role_hint_block=point_role_hint_block)')
        self.assertEqual(src.count(old_call2), 1, "retry role plan call not found exactly once")
        src = src.replace(old_call2, new_call2)

        for name in self.BARE_NAMES:
            pattern = re.compile(r'(?<!prod_gen\.)\b' + re.escape(name) + r'\b')
            src = pattern.sub('prod_gen.' + name, src)

        return prod_src, src

    def test_reconstructed_source_matches_trial04_exactly(self):
        prod_src, reconstructed = self._reconstruct()
        trial_src = inspect.getsource(t4.run_one_pattern_connected)
        if reconstructed != trial_src:
            diff = "\n".join(difflib.unified_diff(
                reconstructed.splitlines(), trial_src.splitlines(),
                fromfile="reconstructed_from_production", tofile="trial_04_actual", lineterm=""))
            self.fail(f"trial_04のrun_one_pattern_connectedはhint注入関連の既知差分のみに"
                      f"限定されていません。差分:\n{diff}")

    def test_bare_name_prefix_table(self):
        """置換表(14件)をREPORT用に出力可能な形で保持していることの確認
        (名前重複・空文字列がないこと)。"""
        self.assertEqual(len(self.BARE_NAMES), len(set(self.BARE_NAMES)))
        self.assertTrue(all(self.BARE_NAMES))


# ============================================================
# Role Planningテンプレートのbyte一致・hint注入確認(Trial-03と同型)
# ============================================================
class RolePlanningTemplateTests(unittest.TestCase):
    def test_default_hint_is_byte_identical_to_production(self):
        topic = "テストテーマ"
        ledger = "verified fact ledger fixture text"
        trial_prompt = t4.ROLE_PLANNING_PROMPT_TEMPLATE_CONNECTED.format(
            topic=topic, verified_ledger_text=ledger, point_role_hint_block="")
        prod_prompt = point_planning.ROLE_PLANNING_PROMPT_TEMPLATE.format(
            topic=topic, verified_ledger_text=ledger)
        self.assertEqual(trial_prompt, prod_prompt)
        self.assertEqual(trial_prompt.encode("utf-8"), prod_prompt.encode("utf-8"))

    def test_hint_appears_when_provided(self):
        topic = "テストテーマ"
        ledger = "verified fact ledger fixture text"
        hint = "TEST_HINT_MARKER sentence."
        trial_prompt = t4.ROLE_PLANNING_PROMPT_TEMPLATE_CONNECTED.format(
            topic=topic, verified_ledger_text=ledger, point_role_hint_block=f"{hint}\n\n")
        self.assertIn(hint, trial_prompt)
        self.assertIn("Point One・Point Twoそれぞれについて", trial_prompt)


# ============================================================
# (ii)/(iii) LLMモック統合テスト
# ============================================================
class _FakeRolePlanningClient:
    """responses.create呼び出しをtrackし、常にGOOD_PLANを返す決定論的な
    Fake。response.modelはリクエストされたmodelをそのまま返すため、
    RolePlanningModelMismatchErrorは発生しない。"""

    def __init__(self, plan=None):
        self.plan = plan if plan is not None else GOOD_PLAN
        self.calls = []

    @property
    def responses(self):
        outer = self

        class _Responses:
            @staticmethod
            def create(**kwargs):
                outer.calls.append(kwargs)

                class _FakeResponse:
                    model = kwargs["model"]
                    output_text = json.dumps(outer.plan)
                    id = f"resp_fake_{len(outer.calls)}"

                return _FakeResponse()

        return _Responses()


def _fake_generate_and_compress_article(client, theme_id, label, prompt, out_dir, apply_evidence_compression, model):
    """_generate_and_compress_article(Writer呼び出し+Evidence Compression)の
    決定論的Fake。captured_promptsに実際に渡されたprompt(role plan込みの
    Writer prompt)を記録する。"""
    _fake_generate_and_compress_article.captured_prompts.append(prompt)
    return {
        "status": "OK", "article_text": FIXED_ARTICLE_TEXT,
        "fact_usage_report": None, "evidence_compression_applied": False,
    }


_fake_generate_and_compress_article.captured_prompts = []


def _fake_run_point_overlap_qa_and_regenerate(client, article_text, verified_ledger_text, model,
                                               reasoning_effort, out_dir):
    return {
        "status": "OK",
        "report": {
            "point_one": {"before_overlap": {"flagged": False}},
            "point_two": {"before_overlap": {"flagged": False}},
        },
    }


def _fake_run_fact_checker_with_gates(make_fact_checker_fn, max_attempts=1, sleep_fn=None):
    fc_result = {
        "verdict": "PASS", "contradictions": [], "unsupported_specific_claims": [],
        "verified_claims_summary": "", "sources": [], "notes": "",
    }
    return fc_result, "FACT_CHECK_COMPLETED", [], "fake-fc-model", "fc-resp-1", {"web_search_call_count": 1}, []


def _fake_run_deviation_check(client, verified_ledger_text, article_text, model, hook_aware=True):
    return {"parsed": {"overall_status": "LEDGER_COMPLIANT", "deviations": []}}


def _fake_audit_article_directional_facts(article_text, ledger_text, vfl_path=None):
    return {"overall_status": "OK"}


class RunOnePatternConnectedIntegrationTests(unittest.TestCase):
    """全ての重い依存(Writer生成、Fact Checker、Ledger Deviation、
    Directional Fact Precheck、Point Overlap QA)を決定論的Fakeへ
    mock.patch.objectで差し替え、Point Role Planningのみ実際にFakeClient
    経由で呼ぶ。Production版run_one_patternと新コピー
    run_one_pattern_connectedを同一入力・同一Fake下で実行し、出力の
    構造・呼び出し内容がbyte一致することを確認する。"""

    def setUp(self):
        _fake_generate_and_compress_article.captured_prompts = []
        self._tmp_out_root = tempfile.mkdtemp(prefix="er011_trial04_gate4_test_")
        self.addCleanup(lambda: shutil.rmtree(self._tmp_out_root, ignore_errors=True))
        self.patches = [
            mock.patch.object(prod_gen, "_generate_and_compress_article", _fake_generate_and_compress_article),
            mock.patch.object(prod_gen, "run_point_overlap_qa_and_regenerate", _fake_run_point_overlap_qa_and_regenerate),
            mock.patch.object(prod_gen, "split_common_sections_for_point_qa", lambda article_text: None),
            mock.patch.object(r3, "run_fact_checker_with_gates", _fake_run_fact_checker_with_gates),
            mock.patch.object(vfl01, "run_deviation_check", _fake_run_deviation_check),
            mock.patch.object(dfp, "audit_article_directional_facts", _fake_audit_article_directional_facts),
        ]
        for p in self.patches:
            p.start()
        self.addCleanup(lambda: [p.stop() for p in self.patches])

    def _common_kwargs(self, out_dir):
        return dict(
            theme_id="fixture_theme", label="A2", prompt="FIXTURE WRITER PROMPT",
            verified_ledger_text="fixture ledger text (no canonical_en_spelling line)",
            topic="fixture topic ja", out_dir=out_dir,
        )

    def test_default_hint_empty_produces_byte_identical_role_planning_request_and_result(self):
        prod_client = _FakeRolePlanningClient()
        conn_client = _FakeRolePlanningClient()

        prod_result = prod_gen.run_one_pattern(
            prod_client, **self._common_kwargs(f"{self._tmp_out_root}/prod"))
        conn_result = t4.run_one_pattern_connected(
            conn_client, **self._common_kwargs(f"{self._tmp_out_root}/conn"), point_role_hint_block="")

        # Role Planning呼び出しは各1回のみ(overlap QA/value QAはOKでretryなし)
        self.assertEqual(len(prod_client.calls), 1)
        self.assertEqual(len(conn_client.calls), 1)

        prod_call, conn_call = prod_client.calls[0], conn_client.calls[0]
        self.assertEqual(prod_call["model"], conn_call["model"])
        self.assertEqual(prod_call["reasoning"], conn_call["reasoning"])
        self.assertEqual(prod_call["input"], conn_call["input"],
                          "hint=''の場合、Point Role Planningへ送るprompt(developer/userメッセージ含む)は"
                          "byte一致するはず")

        # 結果構造のbyte一致(article_text含む、Fakeが固定値を返すため一致するはず)
        self.assertEqual(prod_result, conn_result)

        # Writerへ渡されたprompt(role plan込み)もbyte一致
        self.assertEqual(len(_fake_generate_and_compress_article.captured_prompts), 2)
        self.assertEqual(_fake_generate_and_compress_article.captured_prompts[0],
                          _fake_generate_and_compress_article.captured_prompts[1])

    def test_hint_appears_in_role_planning_request_only_writer_prompt_unaffected(self):
        hint = "TEST_HINT_MARKER: prefer a distinct causal mechanism."
        no_hint_client = _FakeRolePlanningClient()
        hint_client = _FakeRolePlanningClient()

        _fake_generate_and_compress_article.captured_prompts = []
        no_hint_result = t4.run_one_pattern_connected(
            no_hint_client, **self._common_kwargs(f"{self._tmp_out_root}/nohint"), point_role_hint_block="")
        no_hint_writer_prompt = _fake_generate_and_compress_article.captured_prompts[-1]

        _fake_generate_and_compress_article.captured_prompts = []
        hint_result = t4.run_one_pattern_connected(
            hint_client, **self._common_kwargs(f"{self._tmp_out_root}/hint"), point_role_hint_block=hint)
        hint_writer_prompt = _fake_generate_and_compress_article.captured_prompts[-1]

        # hintはRole Planningへのrequestにのみ現れる
        no_hint_prompt_text = no_hint_client.calls[0]["input"][1]["content"]
        hint_prompt_text = hint_client.calls[0]["input"][1]["content"]
        self.assertNotIn(hint, no_hint_prompt_text)
        self.assertIn(hint, hint_prompt_text)

        # FakeClientは常にGOOD_PLANを返すため、Writer prompt(role plan込み)は
        # hint有無で不変(hintの影響はRole Planning requestのみに閉じる)。
        self.assertEqual(no_hint_writer_prompt, hint_writer_prompt)
        self.assertEqual(no_hint_result, hint_result)


if __name__ == "__main__":
    unittest.main()
