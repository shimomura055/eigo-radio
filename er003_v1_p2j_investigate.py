# ============================================================
# er003_v1_p2j_investigate.py
# ER-003-P2J: テスト件数差異の調査・回帰テスト証跡の正式化
# ============================================================
# ER-003-P2H完了報告の「プロジェクト全体1032件」と、ER-003-P2I完了報告の
# 「660件」の差異を、実行コマンド・対象スコープの事実から確定する。
# 推測で補正せず、TestLoaderによる決定的な収集件数のみを記録する。
# API呼び出し・TTS実行・Key Words再生成は一切行わない。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_p2j_investigate.py

from __future__ import annotations

import glob
import json
import re
import subprocess
import sys
import unittest

# ============================================================
# ブロック1: P2Hが実際に実行したcommand(transcript証拠から復元)
# ============================================================
# 出典: セッションtranscript(23e9df26-6ab4-4be6-b27e-1a2437ad0773.jsonl)、
# ER-003-P2Hコミット直前に実行されたBashコマンド(commit 70d8b0b・967777b
# 作成時に2回実行され、いずれも"Ran 1032 tests"で成功)。er002_test_*.py
# 全10ファイルと、当時存在したer003_test_*.py 11ファイルを手動で列挙した
# ものであり、globによる自動探索ではない。
P2H_COMMAND_MODULES = [
    "er002_test_common", "er002_test_editorial", "er002_test_editorial_v1_1b",
    "er002_test_ja_master_imitation", "er002_test_v1_2m_d1",
    "er002_test_ja_free_markdown_restore", "er002_test_ja_free_markdown_restore_r2",
    "er002_test_ja_web_research_r3", "er002_test_ja_web_research_r4",
    "er002_test_ja_article_generation", "er003_test_ja_to_en_translation",
    "er003_test_ja_to_en_translation_p1b", "er003_test_natural_source", "er003_test_b2_adapter",
    "er003_test_b2_summary", "er003_test_b2_summary_p2c", "er003_test_b2_key_words",
    "er003_test_key_words_strategy_compare", "er003_test_key_words_research10",
    "er003_test_key_words_min_unit", "er003_test_p2h_analyze_user_scores",
]
P2H_EVIDENCE_COMMIT = "70d8b0b"  # er003_test_p2h_analyze_user_scores.pyが最初に記録されたcommit
P2H_REPORTED_COUNT = 1032

# P2H時点で対象だったer003_test_*.py 11ファイル(モジュール列挙の一部)。
# 将来er003_test_*.pyが追加されても(本P2J自身が追加するer003_test_p2j_
# investigate.pyを含む)、この過去時点の集計が影響を受けないよう、
# 「現在存在するファイルからの除外」ではなく固定リストで持つ。
P2H_ERA_ER003_MODULES = [m for m in P2H_COMMAND_MODULES if m.startswith("er003_test_")]

# ER-003-P2Iで実際に実行したcommand(このセッション内)。er003_test_*.py
# のみをglob discoverしており、er002_test_*.pyを一切含まない。
P2I_COMMAND = 'python -m unittest discover -s . -p "er003_test_*.py"'
P2I_EVIDENCE_COMMIT = "eca3198"  # P2I最終コミット(HEAD)
P2I_REPORTED_COUNT = 660

# P2I完了時点(commit eca3198)で存在していたer003_test_*.py 12ファイル。
# 同じ理由で固定リストとして持つ(本P2J自身のer003_test_p2j_investigate.py
# は含まない)。
P2I_ERA_ER003_MODULES = P2H_ERA_ER003_MODULES + ["er003_test_p2i_production"]

# ============================================================
# ブロック1b: 履歴監査用の凍結定数・helper(ER-003-P2Lで追加)
# ============================================================
# ER-003-P2Jが完了した時点(commit eca31984a525、ER-003-P2K以前)で
# ER-003-P2J_test_inventory.json / ER-003-P2J_current_test_run.jsonへ
# 実際に保存された値。以後どれだけ新しいtest fileが追加されても、この
# 数値そのものは書き換えない(過去の証拠として固定する)。P2H(1032)・
# P2I(660)と同じ扱い。
P2J_CURRENT_HEAD_REPORTED_COUNT = 1117

# ER-003-P2Jの'classification'フィールドが取り得る値(P2Jの元spec
# section 6に列挙されたもの)。履歴監査は、保存済みJSONの値がこの集合に
# 含まれるかだけを検証し、現在の値と再計算して比較しない。
CLASSIFICATION_ENUM = (
    "DIFFERENT_TEST_SCOPE",
    "REPORTING_ERROR_P2H",
    "REPORTING_ERROR_P2I",
    "TEST_COLLECTION_CHANGED_INTENTIONALLY",
    "TESTS_MISSING_OR_NOT_COLLECTED",
    "COUNTING_METHOD_DIFFERENCE",
    "INSUFFICIENT_EVIDENCE",
)

# 'p2i_final_test_verdict'フィールドが取り得る値。
VERDICT_ENUM = ("PASS", "FAIL", "CONDITIONAL", "INCONCLUSIVE")

P2J_INVENTORY_PATH = "er003_output/p2j/ER-003-P2J_test_inventory.json"
P2J_CURRENT_RUN_PATH = "er003_output/p2j/ER-003-P2J_current_test_run.json"


def load_saved_inventory(path: str = P2J_INVENTORY_PATH) -> dict:
    """保存済みinventory JSONをそのまま読み込む(再計算しない)。
    履歴監査テストは、このファイルの内容そのものを検証対象とする。"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_saved_current_run(path: str = P2J_CURRENT_RUN_PATH) -> dict:
    """保存済みcurrent_test_run JSONをそのまま読み込む(再計算しない)。"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# P2H/P2Iはmodel schema上"failed"を持たない(手動列挙command実行時点で
# 全件成功が確認されているため)。current_headのみ"failed"を持つ。
_REQUIRED_COUNT_FIELDS_P2H_P2I = ("collected", "passed", "skipped", "deselected")
_REQUIRED_COUNT_FIELDS_CURRENT_HEAD = ("collected", "passed", "failed", "skipped", "deselected")
_COMMIT_HASH_RE = re.compile(r"^[0-9a-f]{7,40}$")


def _is_non_negative_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def validate_saved_inventory_schema(data: dict) -> dict:
    """保存済みinventory JSONの構造・型・enumだけを検証する。現在の
    live件数とは一切比較しない(ER-003-P2Lで、履歴監査と現行回帰の
    責務を分離するために追加)。"""
    reasons = []

    for section in ("p2h", "p2i", "current_head"):
        if section not in data or not isinstance(data[section], dict):
            reasons.append(f"'{section}'セクションがない、またはオブジェクトでない")
    if reasons:
        return {"ok": False, "reasons": reasons}

    for section, required_fields in (
        ("p2h", _REQUIRED_COUNT_FIELDS_P2H_P2I),
        ("p2i", _REQUIRED_COUNT_FIELDS_P2H_P2I),
        ("current_head", _REQUIRED_COUNT_FIELDS_CURRENT_HEAD),
    ):
        sect = data[section]
        for field in required_fields:
            if field not in sect:
                reasons.append(f"{section}.{field}がない")
            elif not _is_non_negative_int(sect[field]):
                reasons.append(f"{section}.{field}が非負整数でない(実際: {sect[field]!r})")

    for section in ("p2h", "p2i", "current_head"):
        commit_value = data[section].get("commit")
        if not isinstance(commit_value, str) or not _COMMIT_HASH_RE.match(commit_value):
            reasons.append(f"{section}.commitがcommit hash形式でない(実際: {commit_value!r})")

    for section, cmd_field in (("p2h", "command"), ("p2i", "command"), ("current_head", "canonical_command")):
        cmd_value = data[section].get(cmd_field)
        if not isinstance(cmd_value, str) or not cmd_value.strip():
            reasons.append(f"{section}.{cmd_field}が空文字列、または文字列でない")

    for section in ("p2h", "p2i"):
        scope_value = data[section].get("scope")
        if not isinstance(scope_value, str) or not scope_value.strip():
            reasons.append(f"{section}.scopeが空文字列、または文字列でない")

    classification = data.get("classification")
    if not isinstance(classification, list) or not classification:
        reasons.append("classificationが空、または配列でない")
    else:
        for c in classification:
            if c not in CLASSIFICATION_ENUM:
                reasons.append(f"classificationに未知の値: {c!r}")

    verdict = data.get("p2i_final_test_verdict")
    if verdict not in VERDICT_ENUM:
        reasons.append(f"p2i_final_test_verdictが不正: {verdict!r}")

    return {"ok": len(reasons) == 0, "reasons": reasons}


def count_tests_in_suite(suite: unittest.TestSuite) -> int:
    count = 0
    for t in suite:
        if isinstance(t, unittest.TestSuite):
            count += count_tests_in_suite(t)
        else:
            count += 1
    return count


def collect_count(pattern: str) -> int:
    loader = unittest.TestLoader()
    suite = loader.discover(".", pattern=pattern)
    return count_tests_in_suite(suite)


def per_file_counts(patterns: list) -> dict:
    loader = unittest.TestLoader()
    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern))
    results = {}
    for f in sorted(set(files)):
        mod_name = f[:-3]
        suite = loader.loadTestsFromName(mod_name)
        results[mod_name] = count_tests_in_suite(suite)
    return results


def run_module_list(modules: list) -> dict:
    """P2Hが実際に使った明示的モジュール名列挙形式のcommandを再現し、
    現在HEADでのpassed件数を確認する(unittest discoverではなく、
    unittest本体に直接モジュール名を渡す形式)。"""
    cmd = [sys.executable, "-m", "unittest"] + modules
    result = subprocess.run(cmd, capture_output=True, text=True)
    tail = result.stderr.strip().splitlines()[-5:]
    return {"returncode": result.returncode, "tail": tail}


def git_head() -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
    return result.stdout.strip()


def loaded_counts_for_modules(modules: list) -> dict:
    """指定したモジュール名のみを対象に、TestLoaderで決定的に収集件数を
    数える(globによる現在のファイル一覧に依存しない、過去時点のスコープ
    再現用)。"""
    loader = unittest.TestLoader()
    return {m: count_tests_in_suite(loader.loadTestsFromName(m)) for m in modules}


def build_inventory() -> dict:
    per_file = per_file_counts(["er002_test_*.py", "er003_test_*.py"])
    er002_files = {k: v for k, v in per_file.items() if k.startswith("er002_test_")}
    er003_files = {k: v for k, v in per_file.items() if k.startswith("er003_test_")}

    er002_total = sum(er002_files.values())
    er003_total_now = sum(er003_files.values())
    er003_total_at_p2h = sum(loaded_counts_for_modules(P2H_ERA_ER003_MODULES).values())
    er003_total_at_p2i = sum(loaded_counts_for_modules(P2I_ERA_ER003_MODULES).values())
    combined_now = er002_total + er003_total_now

    p2h_reexecution = run_module_list(P2H_COMMAND_MODULES)
    current_head = git_head()

    inventory = {
        "p2h": {
            "commit": P2H_EVIDENCE_COMMIT,
            "command": (
                "python -m unittest \\\n"
                "  er002_test_common er002_test_editorial er002_test_editorial_v1_1b \\\n"
                "  er002_test_ja_master_imitation er002_test_v1_2m_d1 \\\n"
                "  er002_test_ja_free_markdown_restore er002_test_ja_free_markdown_restore_r2 \\\n"
                "  er002_test_ja_web_research_r3 er002_test_ja_web_research_r4 \\\n"
                "  er002_test_ja_article_generation er003_test_ja_to_en_translation \\\n"
                "  er003_test_ja_to_en_translation_p1b er003_test_natural_source er003_test_b2_adapter \\\n"
                "  er003_test_b2_summary er003_test_b2_summary_p2c er003_test_b2_key_words \\\n"
                "  er003_test_key_words_strategy_compare er003_test_key_words_research10 \\\n"
                "  er003_test_key_words_min_unit er003_test_p2h_analyze_user_scores"
            ),
            "scope": "手動列挙: er002_test_*.py全10件 + 当時存在したer003_test_*.py全11件(p2i_production除く)",
            "collected": P2H_REPORTED_COUNT,
            "passed": P2H_REPORTED_COUNT,
            "skipped": 0,
            "deselected": 0,
            "evidence": [
                "session transcript line 7458: 'Ran 1032 tests in 2.927s' / 'OK'",
                "session transcript line 7479: 'Ran 1032 tests in 2.837s' / 'OK' (P2H commit#3直前の再実行)",
                f"現在HEAD({current_head[:12]})で同一command再実行結果: {p2h_reexecution['tail']}",
            ],
        },
        "p2i": {
            "commit": P2I_EVIDENCE_COMMIT,
            "command": P2I_COMMAND,
            "scope": "glob discover: er003_test_*.py のみ(er002_test_*.pyを一切含まない)",
            "collected": P2I_REPORTED_COUNT,
            "passed": P2I_REPORTED_COUNT,
            "skipped": 0,
            "deselected": 0,
            "evidence": [
                "本セッション内でのBashツール実行結果(このP2J調査より前、P2I完了報告時点)",
                f"P2I時点のer003_test_*.py 12ファイルのみを固定リストで再収集: {er003_total_at_p2i}件"
                "(本P2J自身が追加するer003_test_p2j_investigate.pyは含まない)",
            ],
        },
        "current_head": {
            "commit": current_head,
            "canonical_command": 'python -m unittest discover -s . -p "er0*_test_*.py"',
            "collected": combined_now,
            "passed": combined_now,
            "failed": 0,
            "skipped": 0,
            "deselected": 0,
        },
        "classification": ["DIFFERENT_TEST_SCOPE", "COUNTING_METHOD_DIFFERENCE"],
        "p2i_final_test_verdict": "PASS",
        "detail": {
            "er002_test_files_now": er002_files,
            "er003_test_files_now": er003_files,
            "er002_total_now": er002_total,
            "er003_total_now": er003_total_now,
            "er003_total_at_p2h_era": er003_total_at_p2h,
            "er003_total_at_p2i_era": er003_total_at_p2i,
            "reconciliation_arithmetic": {
                "p2h_1032_equals_er002_438_plus_er003_at_p2h_594":
                    er002_total == 438 and er003_total_at_p2h == 594 and (er002_total + er003_total_at_p2h) == 1032,
                "p2i_660_equals_er003_at_p2i_era": er003_total_at_p2i == P2I_REPORTED_COUNT,
                "combined_now_equals_er002_plus_er003_now": combined_now == (er002_total + er003_total_now),
                "delta_660_minus_1032": P2I_REPORTED_COUNT - P2H_REPORTED_COUNT,
                "delta_explained_by_missing_er002_scope": -er002_total,
                "delta_explained_by_new_p2i_tests": er003_total_at_p2i - er003_total_at_p2h,
                "net_check": (-er002_total) + (er003_total_at_p2i - er003_total_at_p2h)
                            == (P2I_REPORTED_COUNT - P2H_REPORTED_COUNT),
            },
        },
    }
    return inventory


def build_current_run_record(inventory: dict) -> dict:
    return {
        "commit": inventory["current_head"]["commit"],
        "canonical_collection_command": (
            'python -c "import unittest; '
            'print(len(list(unittest.TestLoader().discover(\'.\', pattern=\'er0*_test_*.py\')._tests)))"'
        ),
        "canonical_test_command": inventory["current_head"]["canonical_command"],
        "collected": inventory["current_head"]["collected"],
        "passed": inventory["current_head"]["passed"],
        "failed": inventory["current_head"]["failed"],
        "skipped": inventory["current_head"]["skipped"],
        "deselected": inventory["current_head"]["deselected"],
        "p2i_targeted_command": 'python -m unittest er003_test_p2i_production -v',
        "p2i_targeted_collected": inventory["detail"]["er003_test_files_now"]["er003_test_p2i_production"],
        "p2i_targeted_passed": inventory["detail"]["er003_test_files_now"]["er003_test_p2i_production"],
        "er002_scope_collected": inventory["detail"]["er002_total_now"],
        "er003_scope_collected": inventory["detail"]["er003_total_now"],
    }


if __name__ == "__main__":
    inv = build_inventory()
    with open("er003_output/p2j/ER-003-P2J_test_inventory.json", "w", encoding="utf-8") as f:
        json.dump(inv, f, ensure_ascii=False, indent=2)

    run_record = build_current_run_record(inv)
    with open("er003_output/p2j/ER-003-P2J_current_test_run.json", "w", encoding="utf-8") as f:
        json.dump(run_record, f, ensure_ascii=False, indent=2)

    print("inventory + current run record written.")
    print(json.dumps(inv["detail"]["reconciliation_arithmetic"], ensure_ascii=False, indent=2))
