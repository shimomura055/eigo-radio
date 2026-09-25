"""check_delegation_prompt_test_01.py

check_delegation_prompt.py の unit test。
- 合格例(本委任文をそのまま保存したもの): PASS判定
- 不合格例1: Grep一覧欠落(事前指定Grep一覧セクション無し)
- 不合格例2: プレースホルダ混入(前回と同じ/<引数>等)

管理ID: PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01
(+PM-CLOSEOUT-CONSOLIDATION-117、2026-09-13)。

実行: python docs/pm/tools/check_delegation_prompt_test_01.py
または: python -m unittest docs.pm.tools.check_delegation_prompt_test_01
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_DIR))

import check_delegation_prompt as cdp  # noqa: E402

DELEGATION_LOG_DIR = TOOLS_DIR.parent / "delegation_log"
PASS_SAMPLE_PATH = (
    DELEGATION_LOG_DIR
    / "PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01.md"
)


FAIL_SAMPLE_MISSING_GREP = """
管理ID: PM-TEST-FAIL-01
性質: テスト用の不合格サンプル(Grep一覧欠落)。

---
E-1: 同一task内で同一ファイルを再読しない。
D-1: Grep→該当行範囲Readを基本とする。
G-1: git出力は最小化する。
F-1: transcript退避はFable側で実施する。
---

## 事前指定Read一覧
- `docs/pm/PM_BRIEF.md`(全文、1回)

## 実行コマンド全文
- `python docs/pm/tools/check_delegation_prompt.py --file "C:\\path\\to\\file.md"`

## SSOT追記文
DECISION_LOGへ1行追記する。

## Git(明示add対象・コミットメッセージ・trailer)
git add docs/pm/tools/check_delegation_prompt_test_01.py

## 報告(RESULT_PACKET項目)
Gate結果を記載する。
"""


FAIL_SAMPLE_PLACEHOLDER = """
管理ID: PM-TEST-FAIL-02
性質: テスト用の不合格サンプル(プレースホルダ混入)。

---
E-1: 同一task内で同一ファイルを再読しない。
D-1: Grep→該当行範囲Readを基本とする。
G-1: git出力は最小化する。
F-1: transcript退避はFable側で実施する。
---

## 事前指定Read一覧
前回と同じ。

## 事前指定Grep一覧+追記位置・更新位置の手順
前回同様のGrepパターンを使う。

## 実行コマンド全文
- `python <引数> を実行する`

## SSOT追記文
TBD

## Git(明示add対象・コミットメッセージ・trailer)
git add <対象>

## 報告(RESULT_PACKET項目)
同上。
"""


class CheckDelegationPromptTest(unittest.TestCase):
    def test_pass_sample_real_delegation_text(self):
        self.assertTrue(
            PASS_SAMPLE_PATH.exists(),
            f"合格サンプルが見つからない: {PASS_SAMPLE_PATH} "
            "(先に実委任文をdelegation_logへ保存すること)",
        )
        text = PASS_SAMPLE_PATH.read_text(encoding="utf-8")
        result = cdp.run_check(text)
        self.assertEqual(
            result["status"],
            "PASS",
            msg=f"reasons={result['reasons']}",
        )

    def test_fail_sample_missing_grep_section(self):
        result = cdp.run_check(FAIL_SAMPLE_MISSING_GREP)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(
            any("事前指定Grep一覧" in r for r in result["reasons"]),
            msg=f"reasons={result['reasons']}",
        )

    def test_fail_sample_placeholder_contamination(self):
        result = cdp.run_check(FAIL_SAMPLE_PLACEHOLDER)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(
            any("プレースホルダ混入" in r for r in result["reasons"]),
            msg=f"reasons={result['reasons']}",
        )

    def test_fixed_block_labels_detected(self):
        result = cdp.run_check(FAIL_SAMPLE_MISSING_GREP)
        for lbl in ["E-1", "D-1", "G-1", "F-1"]:
            self.assertTrue(result["fixed_block"]["labels"][lbl])


TTS_MENTION_NO_MODE_SAMPLE = """
管理ID: PM-TEST-TTS-WARN-01
性質: テスト用サンプル(TTS言及ありだが実行方式・例外理由引数の明示無し)。

---
E-1: 同一task内で同一ファイルを再読しない。
D-1: Grep→該当行範囲Readを基本とする。
G-1: git出力は最小化する。
F-1: transcript退避はFable側で実施する。
---

## 事前指定Read一覧
- `docs/pm/PM_BRIEF.md`(全文、1回)

## 事前指定Grep一覧+追記位置・更新位置の手順
- `Grep pattern="dummy" path="docs/pm/PM_BRIEF.md"`

## 実行コマンド全文
- `.venv\\Scripts\\python.exe er003_v1_n3_01_tts_generate.py --out-dir C:\\dummy`

## SSOT追記文
DECISION_LOGへ1行追記する。

## Git(明示add対象・コミットメッセージ・trailer)
git add docs/pm/tools/check_delegation_prompt_test_01.py

## 報告(RESULT_PACKET項目)
Gate結果を記載する。
"""


TTS_MENTION_WITH_STANDARD_SAMPLE = TTS_MENTION_NO_MODE_SAMPLE.replace(
    "## SSOT追記文",
    "## 補足\nTTS_EXECUTION_MODE=STANDARD を明示する。\n\n## SSOT追記文",
)


class CheckTtsStandardModeReminderTest(unittest.TestCase):
    def test_tts_mention_without_mode_or_reason_triggers_warning_not_fail(self):
        result = cdp.run_check(TTS_MENTION_NO_MODE_SAMPLE)
        self.assertTrue(result["tts_mode_check"]["triggered"])
        self.assertTrue(
            any("TTS_EXECUTION_MODE=STANDARD" in w for w in result["warnings"])
        )
        # 警告はFAILの理由(reasons)には積まない(ブロッキングではない)
        self.assertFalse(
            any("TTS_EXECUTION_MODE" in r for r in result["reasons"])
        )

    def test_tts_mention_with_standard_explicit_does_not_warn(self):
        result = cdp.run_check(TTS_MENTION_WITH_STANDARD_SAMPLE)
        self.assertFalse(result["tts_mode_check"]["triggered"])
        self.assertEqual(result["warnings"], [])

    def test_no_tts_mention_does_not_warn(self):
        result = cdp.run_check(FAIL_SAMPLE_MISSING_GREP)
        self.assertFalse(result["tts_mode_check"]["triggered"])


if __name__ == "__main__":
    unittest.main()
