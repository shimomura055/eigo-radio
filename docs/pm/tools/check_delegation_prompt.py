"""check_delegation_prompt.py

Fableが作成した委任文(Sonnet/Opusへの委任テキスト)が、
docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md の必須構成を満たしているか
を機械的に検証する記録用ツール(ブロッキングではない。終了コードは常に0)。

管理ID: PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01
(+PM-CLOSEOUT-CONSOLIDATION-117、2026-09-13)。

検証項目:
  1. 必須セクション見出し(の代表キーワード)の有無
     - 管理ID / 性質 / 事前指定Read / 事前指定Grep / 実行コマンド全文 /
       SSOT / Git / 報告
  2. 固定ブロックのラベル(E-1/D-1/G-1/F-1)の有無(T-1は任意)
  3. プレースホルダ語の混入(同上/前回と同じ/前回同様/<引数>/TBD)
  4. 「実行コマンド全文」セクション内の各コマンド行に、`--`長形式引数
     または絶対パスが含まれているか

使い方:
  python docs/pm/tools/check_delegation_prompt.py --file <path> [--json-out <path>] [--pretty]
  python docs/pm/tools/check_delegation_prompt.py --stdin

--fileも--stdinも指定しない場合は標準入力を読む。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_KEYWORDS = [
    ("管理ID", "管理ID"),
    ("性質", "性質(または到達上限Status/禁止事項)"),
    ("事前指定Read", "事前指定Read一覧"),
    ("事前指定Grep", "事前指定Grep一覧+追記位置・更新位置の手順"),
    ("実行コマンド全文", "実行コマンド全文"),
    ("SSOT", "SSOT追記文"),
    ("Git", "Git(明示add対象・コミットメッセージ・trailer)"),
    ("報告", "報告(RESULT_PACKET項目)"),
]

FIXED_BLOCK_LABELS = ["E-1", "D-1", "G-1", "F-1"]
OPTIONAL_LABEL = "T-1"

PLACEHOLDER_PATTERNS = ["同上", "前回と同じ", "前回同様", "<引数>", "TBD"]

SECTION_HEADER_RE = re.compile(r"^#{1,6}\s*(.+)$", re.MULTILINE)

ABS_PATH_RE = re.compile(
    r"[A-Za-z]:[\\/][^\s`\"']+|(?<![\w.])/[\w][\w./-]*"
)


def find_section_text(text: str, keyword: str) -> str | None:
    """keyword を含む見出し行から次の見出し行の手前までを返す。"""
    headers = list(SECTION_HEADER_RE.finditer(text))
    for i, m in enumerate(headers):
        if keyword in m.group(1):
            start = m.end()
            end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
            return text[start:end]
    # 見出し形式でなくても本文中にキーワードがあれば別途 present 判定は別関数で行う
    return None


def check_required_keywords(text: str) -> list[dict]:
    results = []
    for kw, label in REQUIRED_KEYWORDS:
        present = kw in text
        results.append({"keyword": kw, "label": label, "present": present})
    return results


def check_fixed_block(text: str) -> dict:
    labels_found = {lbl: (lbl in text) for lbl in FIXED_BLOCK_LABELS}
    optional_found = OPTIONAL_LABEL in text
    all_required_present = all(labels_found.values())
    return {
        "labels": labels_found,
        "optional_T1_present": optional_found,
        "all_required_present": all_required_present,
    }


PLACEHOLDER_CHECK_SECTION_KEYWORDS = [
    "事前指定Read",
    "事前指定Grep",
    "実行コマンド全文",
    "SSOT",
    "Git",
    "報告",
]


def get_placeholder_check_scope(text: str) -> str:
    """プレースホルダ検査の対象は実行内容セクションに限定する。

    「実装(新規ファイル)」等の設計説明中に禁止語を例示として引用する記述
    (例: 『同上』『前回と同じ』等のプレースホルダ禁止、という説明文そのもの)
    を誤検知しないため、実際にプレースホルダが混入してはならない具体セクション
    (Read一覧/Grep一覧/実行コマンド全文/SSOT追記文/Git/報告)のみを対象とする。
    見出し形式で該当セクションが1つも見つからない場合は全文を対象にする
    (見出しが無い簡易テキストでも検知できるようにするフォールバック)。
    """
    parts = []
    for kw in PLACEHOLDER_CHECK_SECTION_KEYWORDS:
        sec = find_section_text(text, kw)
        if sec:
            parts.append(sec)
    if not parts:
        return text
    return "\n".join(parts)


def check_placeholders(text: str) -> list[dict]:
    scope = get_placeholder_check_scope(text)
    hits = []
    for pat in PLACEHOLDER_PATTERNS:
        count = scope.count(pat)
        if count > 0:
            hits.append({"pattern": pat, "count": count})
    return hits


def extract_command_lines(section_text: str) -> list[str]:
    """箇条書き1行(または単独のバッククォート行)を1コマンド単位として扱う。

    1行内に複数のバッククォート断片(コマンド本体+補足パス等)が含まれる
    場合でも、行全体を1単位として引数/絶対パスの有無を判定する
    (断片ごとに分割すると、補足テキスト部分だけを見て誤検知するため)。
    """
    lines = []
    for raw_line in section_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("-") or line.startswith("*"):
            content = line.lstrip("-*").strip()
            if content:
                lines.append(content)
        elif line.startswith("`") and line.endswith("`") and len(line) > 1:
            lines.append(line)
    return lines


def is_bare_complete_invocation(line: str) -> bool:
    """`python <script>.py` のみで完結する単純呼び出しは、引数が欠落している
    のではなく、そもそも引数を取らない完結したコマンドと判定して除外する
    (デフォルト全件回帰の`python run_project_regression.py`等)。
    バッククォート・句読点を除去した上でトークン数2(python + *.py)のみ許可。
    """
    stripped = line.strip("`。、").strip()
    tokens = stripped.split()
    if len(tokens) != 2:
        return False
    prog, script = tokens
    return prog.lower() in {"python", "python3"} and script.endswith(".py")


def check_commands_have_args_or_paths(text: str) -> dict:
    section = find_section_text(text, "実行コマンド全文")
    if section is None:
        return {
            "section_found": False,
            "command_lines_total": 0,
            "command_lines_missing_arg_or_path": [],
        }
    cmd_lines = extract_command_lines(section)
    missing = []
    for line in cmd_lines:
        has_long_arg = "--" in line
        has_abs_path = bool(ABS_PATH_RE.search(line))
        if has_long_arg or has_abs_path:
            continue
        if is_bare_complete_invocation(line):
            continue
        missing.append(line)
    return {
        "section_found": True,
        "command_lines_total": len(cmd_lines),
        "command_lines_missing_arg_or_path": missing,
    }


TTS_MENTION_RE = re.compile(r"TTS|tts|音声化|narration")
TTS_STANDARD_EXPLICIT_RE = re.compile(r"TTS_EXECUTION_MODE\s*=\s*STANDARD")
TTS_BATCH_REASON_RE = re.compile(r"batch-reason", re.IGNORECASE)


def check_tts_standard_mode_reminder(text: str) -> dict:
    """PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01(2026-09-25)。

    委任文がTTS生成に言及している(`TTS`/`tts`/`音声化`/`narration`)のに、
    `TTS_EXECUTION_MODE=STANDARD`の明示も`batch-reason`(PM_GOVERNANCE.md
    7-2の例外理由明示)の言及も無い場合に警告する。ブロッキングではない
    (status/PASS判定には影響しない、`warnings`にのみ記録する)。
    """
    mentions_tts = bool(TTS_MENTION_RE.search(text))
    has_standard_explicit = bool(TTS_STANDARD_EXPLICIT_RE.search(text))
    has_batch_reason = bool(TTS_BATCH_REASON_RE.search(text))
    triggered = mentions_tts and not has_standard_explicit and not has_batch_reason
    return {
        "triggered": triggered,
        "mentions_tts": mentions_tts,
        "has_standard_explicit": has_standard_explicit,
        "has_batch_reason": has_batch_reason,
    }


TTS_DIFF_REGEN_RE = re.compile(r"差分再生成")
TTS_BUDGET_FLAG_RE = re.compile(r"--budget")


def check_tts_budget_deviation_reminder(text: str) -> dict:
    """PM_GOVERNANCE.md 7-5(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`)。

    委任文がTTS生成に言及している(`TTS`/`tts`/`音声化`/`narration`)のに、
    「差分再生成」の確認への言及も`--budget`(または`--budget-jpy`等)の
    明示への言及も無い場合に警告する。ブロッキングではない(status/PASS
    判定には影響しない、`warnings`にのみ記録する)。
    """
    mentions_tts = bool(TTS_MENTION_RE.search(text))
    has_diff_regen_mention = bool(TTS_DIFF_REGEN_RE.search(text))
    has_budget_flag_mention = bool(TTS_BUDGET_FLAG_RE.search(text))
    triggered = mentions_tts and not has_diff_regen_mention and not has_budget_flag_mention
    return {
        "triggered": triggered,
        "mentions_tts": mentions_tts,
        "has_diff_regen_mention": has_diff_regen_mention,
        "has_budget_flag_mention": has_budget_flag_mention,
    }


BUDGET_OLD_STOP_PHRASE_RE = re.compile(r"超えそうなら[^。\n]{0,15}(実行前)?STOP")
BUDGET_GUARDRAIL_WORDING_RE = re.compile(r"Guardrail|継続条件")


def check_budget_cap_guardrail_wording(text: str) -> dict:
    """PM-BUDGET-CAP-GUARDRAIL-POLICY-01(2026-09-26)。

    委任文の費用上限(Cap)記載が、旧文言「上限¥X、超えそうなら実行前STOP」
    (継続条件・Guardrail表記の書き分けが無いもの)のまま残っている場合に
    警告する。ブロッキングではない(status/PASS判定には影響しない、
    `warnings`にのみ記録する)。PM_GOVERNANCE.md 7-6/T-3参照。
    """
    has_old_phrase = bool(BUDGET_OLD_STOP_PHRASE_RE.search(text))
    has_guardrail_wording = bool(BUDGET_GUARDRAIL_WORDING_RE.search(text))
    triggered = has_old_phrase and not has_guardrail_wording
    return {
        "triggered": triggered,
        "has_old_phrase": has_old_phrase,
        "has_guardrail_wording": has_guardrail_wording,
    }


def run_check(text: str) -> dict:
    keyword_results = check_required_keywords(text)
    fixed_block = check_fixed_block(text)
    placeholder_hits = check_placeholders(text)
    command_check = check_commands_have_args_or_paths(text)
    tts_mode_check = check_tts_standard_mode_reminder(text)
    tts_budget_check = check_tts_budget_deviation_reminder(text)
    budget_cap_wording_check = check_budget_cap_guardrail_wording(text)

    missing_keywords = [r["label"] for r in keyword_results if not r["present"]]
    missing_fixed_labels = [
        lbl for lbl, present in fixed_block["labels"].items() if not present
    ]

    reasons = []
    if missing_keywords:
        reasons.append(f"必須セクション欠落: {', '.join(missing_keywords)}")
    if missing_fixed_labels:
        reasons.append(f"固定ブロックラベル欠落: {', '.join(missing_fixed_labels)}")
    if placeholder_hits:
        pats = ", ".join(f"{h['pattern']}x{h['count']}" for h in placeholder_hits)
        reasons.append(f"プレースホルダ混入: {pats}")
    if command_check["section_found"] and command_check[
        "command_lines_missing_arg_or_path"
    ]:
        reasons.append(
            "実行コマンドに引数実値/絶対パスが無い行: "
            + " | ".join(command_check["command_lines_missing_arg_or_path"])
        )
    if not command_check["section_found"]:
        reasons.append("「実行コマンド全文」セクションが見つからない")

    # 警告(FAILにしない、statusには影響させない。reasonsとは別のwarningsへ記録する)
    warnings = []
    if tts_mode_check["triggered"]:
        warnings.append(
            "TTSを伴う委任文だが TTS_EXECUTION_MODE=STANDARD の明示も "
            "batch-reason の記載も見つからない(PM_GOVERNANCE.md 7-1/7-2、"
            "PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01)"
        )
    if tts_budget_check["triggered"]:
        warnings.append(
            "TTSを伴う委任文だが「差分再生成」確認への言及も --budget 明示への"
            "言及も見つからない(PM_GOVERNANCE.md 7-5、"
            "NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02)"
        )
    if budget_cap_wording_check["triggered"]:
        warnings.append(
            "費用上限(Cap)記載が旧文言「超えそうなら実行前STOP」のままで、"
            "Guardrail/継続条件への言及が見つからない(PM_GOVERNANCE.md 7-6、"
            "PM-BUDGET-CAP-GUARDRAIL-POLICY-01)"
        )

    status = "PASS" if not reasons else "FAIL"

    return {
        "status": status,
        "reasons": reasons,
        "warnings": warnings,
        "required_keywords": keyword_results,
        "fixed_block": fixed_block,
        "placeholder_hits": placeholder_hits,
        "command_check": command_check,
        "tts_mode_check": tts_mode_check,
        "tts_budget_check": tts_budget_check,
        "budget_cap_wording_check": budget_cap_wording_check,
    }


def format_human_readable(result: dict) -> str:
    lines = [f"status: {result['status']}"]
    if result["reasons"]:
        lines.append("reasons:")
        for r in result["reasons"]:
            lines.append(f"  - {r}")
    else:
        lines.append("reasons: (none)")
    if result.get("warnings"):
        lines.append("warnings:")
        for w in result["warnings"]:
            lines.append(f"  - {w}")
    else:
        lines.append("warnings: (none)")
    lines.append("required_keywords:")
    for r in result["required_keywords"]:
        mark = "OK" if r["present"] else "MISSING"
        lines.append(f"  [{mark}] {r['label']}")
    lines.append("fixed_block_labels:")
    for lbl, present in result["fixed_block"]["labels"].items():
        mark = "OK" if present else "MISSING"
        lines.append(f"  [{mark}] {lbl}")
    lines.append(
        f"  T-1(optional): {'present' if result['fixed_block']['optional_T1_present'] else 'absent'}"
    )
    cc = result["command_check"]
    lines.append(
        f"command_check: section_found={cc['section_found']}, "
        f"total={cc['command_lines_total']}, "
        f"missing={len(cc['command_lines_missing_arg_or_path'])}"
    )
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--file", help="検証対象の委任文テキストファイルパス")
    ap.add_argument(
        "--stdin", action="store_true", help="標準入力から委任文テキストを読む"
    )
    ap.add_argument("--json-out", help="JSON結果の出力先パス")
    ap.add_argument("--pretty", action="store_true", help="JSONを整形出力する")
    args = ap.parse_args()

    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()

    result = run_check(text)

    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None),
            encoding="utf-8",
        )

    print(format_human_readable(result))
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
