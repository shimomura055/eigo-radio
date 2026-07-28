"""AI実装タスクIssue本文のpreflight validator(AUTO-001-05-01)。

`.github/ISSUE_TEMPLATE/agent_task.md` が定義する単一Markdown Issue契約
(開始・終了マーカー、固定見出し12件、必須/なし許容セクションの区分、
管理ID形式、受入条件ID形式)を、Claude CodeやAnthropic API・GitHub API
を一切呼び出さずに、文字列だけから決定論的に判定する。

設計上の制約(意図的な簡略化。詳細はAUTO-001-05-01の実装報告を参照):

* 完全なMarkdownパーサーは実装しない。判定に必要な最小限の構造
  (fenced code block、単純なHTMLコメント、見出し行)だけを認識する。
* HTMLコメントは、1行で開いて1行で閉じる形式(`<!-- ... -->`が1行に
  収まる)、または開始行が`<!--`単独・終了行が`-->`単独のブロック形式
  の2パターンだけを認識する。同一行内に複数のコメントが混在する、
  あるいは1行の途中からコメントが始まって別のテキストへ続くような
  複雑な形式は対象としない(既存テンプレート・想定される記入例の
  いずれもこの2パターンに収まる)。
* fenced code blockは、行頭(前後空白を除く)が``` または ~~~ で
  始まる行をトグルとして扱う、単純なオン/オフ判定とする。
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# 正式な契約(source of truth)
#
# ここで定義する値が、Issue本文が満たすべき契約の唯一の正とする。
# `.github/ISSUE_TEMPLATE/agent_task.md` を変更する場合は、この定数群も
# 同時に更新すること(auto001_test_issue_preflight_validator.pyに、実際の
# テンプレートファイルをこの定数で検証し続けるテストがあり、値がずれると
# 検知される)。
# ---------------------------------------------------------------------------

START_MARKER = "<!-- AGENT_TASK_SPEC_START -->"
END_MARKER = "<!-- AGENT_TASK_SPEC_END -->"

# この順序が、Issue本文中に見出しが出現すべき正式な順序でもある。
CANONICAL_HEADINGS: tuple[str, ...] = (
    "管理ID",
    "現在の問題",
    "原因に関する仮説",
    "目的",
    "期待動作・決定事項",
    "非対象範囲",
    "受入条件",
    "テスト観点",
    "リスク",
    "人間確認事項",
    "変更区分",
    "参考資料",
)

# 実質的な記載(空欄・「なし」不可)が必須の8セクション
REQUIRED_SUBSTANTIVE_HEADINGS = frozenset({
    "管理ID", "現在の問題", "目的", "期待動作・決定事項",
    "非対象範囲", "受入条件", "テスト観点", "変更区分",
})

# 該当なしの場合に限り「なし」を認める4セクション
NONE_ALLOWED_HEADINGS = frozenset({"原因に関する仮説", "リスク", "人間確認事項", "参考資料"})

assert REQUIRED_SUBSTANTIVE_HEADINGS | NONE_ALLOWED_HEADINGS == set(CANONICAL_HEADINGS)
assert REQUIRED_SUBSTANTIVE_HEADINGS.isdisjoint(NONE_ALLOWED_HEADINGS)

MANAGEMENT_ID_HEADING = "管理ID"
ACCEPTANCE_CRITERIA_HEADING = "受入条件"
CHANGE_SCOPE_HEADING = "変更区分"

# 「変更区分」内の固定ラベル(テンプレート実体に合わせた正式な表記)。
# `.github/ISSUE_TEMPLATE/agent_task.md` を変更する場合はこの一覧も
# 同時に更新すること(auto001_test_issue_preflight_validator.pyの
# ChangeScopeRealTemplateSyncTestsで実テンプレートとの整合を検証する)。
CHANGE_SCOPE_LABELS: tuple[str, ...] = (
    "サービス仕様変更",
    "リポジトリ運用仕様変更",
    "実装方法だけの変更",
)

# 管理IDの正式な形式(厳密)。例: AUTO-001-05-01, ER-003-B1-P4C
MANAGEMENT_ID_STRICT_RE = re.compile(r"^[A-Z][A-Z0-9]*-\d{3}(?:-[A-Z0-9]+)*$")
# 管理ID欄の中から「IDらしきトークン」を拾うための緩い形状(大文字小文字を問わない)
_ID_SHAPE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)+$")

# 受入条件の正式な行形式。厳密一致で通ったものだけを「整形済み」として扱う。
_AC_STRICT_LINE_RE = re.compile(r"^- \[ \] AC-(\d+): ?(.*)$")
_AC_LOOSE_HINT_RE = re.compile(r"AC-\d+")

_HEADING_LINE_RE = re.compile(r"^## (\S.*)$")
_FENCE_RE = re.compile(r"^(```|~~~)")

# 「変更区分」の1行(例: `- サービス仕様変更：なし`)からラベルと値を取り出す。
_CHANGE_SCOPE_LINE_RE = re.compile(r"^-\s*(.+?)\s*[：:]\s*(.*)$")

_TOKEN_STRIP_CHARS = "`'\"“”‘’.,()（）[]「」『』、。:：;；!！?？*_~ \t"

# なし判定・空欄判定のために取り除く「装飾・区切り」文字の集合。
_DECORATION_CHARS_RE = re.compile(
    r"[#*_`>\-~|:：、。,\.!！?？()（）\[\]「」『』\s]+"
)


class ValidationStatus(str, Enum):
    """呼び出し側が機械的に区別できる3状態。"""

    PASS = "PASS"
    CONTRACT_VIOLATION = "CONTRACT_VIOLATION"
    INTERNAL_ERROR = "INTERNAL_ERROR"


@dataclass(frozen=True)
class ValidationError:
    code: str
    message: str
    section: Optional[str] = None

    def to_dict(self) -> dict:
        return {"code": self.code, "section": self.section, "message": self.message}


@dataclass(frozen=True)
class ValidationResult:
    status: ValidationStatus
    errors: list[ValidationError] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return self.status is ValidationStatus.PASS

    def to_machine_dict(self) -> dict:
        return {
            "valid": self.valid,
            "status": self.status.value,
            "errors": [e.to_dict() for e in self.errors],
        }

    def to_human_text(self) -> str:
        if self.status is ValidationStatus.PASS:
            return "合格: Issue本文はAI実装タスクの契約を満たしています。"
        if self.status is ValidationStatus.INTERNAL_ERROR:
            lines = ["validator自体の内部エラーにより判定を完了できませんでした。"]
            for e in self.errors:
                lines.append(f"  - {e.message}")
            return "\n".join(lines)
        lines = [f"不合格: {len(self.errors)}件の契約違反が見つかりました。"]
        for i, e in enumerate(self.errors, start=1):
            where = f"[{e.section}] " if e.section else ""
            lines.append(f"  {i}. {where}{e.message} (code={e.code})")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 前処理: 改行正規化・fenced code block検出・HTMLコメント除去
# ---------------------------------------------------------------------------

def _normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _fence_mask(lines: list[str]) -> list[bool]:
    """行インデックスごとに、fenced code blockの内側(フェンス行自身を含む)かどうかを返す。"""
    mask = [False] * len(lines)
    in_fence = False
    for i, line in enumerate(lines):
        if _FENCE_RE.match(line.strip()):
            mask[i] = True
            in_fence = not in_fence
            continue
        mask[i] = in_fence
    return mask


def _comment_mask(lines: list[str], fence_mask: list[bool]) -> list[bool]:
    """行インデックスごとに、HTMLコメントとして除去すべき行かどうかを返す。

    対応する2パターン:
      (a) 1行で完結する `<!-- ... -->`
      (b) `<!--` 単独行で始まり `-->` 単独行で終わるブロック
    fenced code block内の行はコメット判定の対象にしない。
    """
    mask = [False] * len(lines)
    in_comment = False
    for i, line in enumerate(lines):
        if fence_mask[i]:
            continue
        stripped = line.strip()
        if in_comment:
            mask[i] = True
            if stripped == "-->":
                in_comment = False
            continue
        if stripped.startswith("<!--") and stripped.endswith("-->") and len(stripped) >= len("<!---->"):
            mask[i] = True
            continue
        if stripped == "<!--":
            mask[i] = True
            in_comment = True
            continue
    return mask


def _strip_html_comments(text: str) -> str:
    """1行完結コメントとブロックコメントの両方を、まとめて正規表現で取り除く。

    セクション内容(数行程度の断片)に対してだけ使う想定で、
    ネストしたコメントは考慮しない(最初の`-->`で閉じる)。
    """
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


# ---------------------------------------------------------------------------
# マーカー検証
# ---------------------------------------------------------------------------

def _find_exact_marker_lines(lines: list[str], fence_mask: list[bool], marker: str) -> list[int]:
    return [
        i for i, line in enumerate(lines)
        if not fence_mask[i] and line.strip() == marker
    ]


def _validate_markers(lines: list[str], fence_mask: list[bool]) -> tuple[Optional[int], Optional[int], list[ValidationError]]:
    errors: list[ValidationError] = []
    starts = _find_exact_marker_lines(lines, fence_mask, START_MARKER)
    ends = _find_exact_marker_lines(lines, fence_mask, END_MARKER)

    if not starts:
        errors.append(ValidationError("MARKER_START_MISSING", "開始マーカー(AGENT_TASK_SPEC_START)が見つかりません。"))
    elif len(starts) > 1:
        errors.append(ValidationError("MARKER_START_DUPLICATE", f"開始マーカーが{len(starts)}件あります(1件だけにしてください)。"))

    if not ends:
        errors.append(ValidationError("MARKER_END_MISSING", "終了マーカー(AGENT_TASK_SPEC_END)が見つかりません。"))
    elif len(ends) > 1:
        errors.append(ValidationError("MARKER_END_DUPLICATE", f"終了マーカーが{len(ends)}件あります(1件だけにしてください)。"))

    if len(starts) == 1 and len(ends) == 1:
        if starts[0] >= ends[0]:
            errors.append(ValidationError("MARKER_ORDER_INVALID", "終了マーカーが開始マーカーより前(または同じ位置)にあります。"))
            return None, None, errors
        return starts[0], ends[0], errors

    return None, None, errors


# ---------------------------------------------------------------------------
# 見出し検証
# ---------------------------------------------------------------------------

@dataclass
class _HeadingScan:
    canonical_positions: dict[str, list[int]]
    any_heading_lines: list[int]


def _scan_headings(spec_lines: list[str], mask: list[bool]) -> _HeadingScan:
    canonical_positions: dict[str, list[int]] = {h: [] for h in CANONICAL_HEADINGS}
    any_heading_lines: list[int] = []
    for i, line in enumerate(spec_lines):
        if mask[i]:
            continue
        m = _HEADING_LINE_RE.match(line)
        if not m:
            continue
        any_heading_lines.append(i)
        text = m.group(1).strip()
        if text in canonical_positions:
            canonical_positions[text].append(i)
    return _HeadingScan(canonical_positions=canonical_positions, any_heading_lines=any_heading_lines)


def _validate_headings(scan: _HeadingScan) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for heading in CANONICAL_HEADINGS:
        positions = scan.canonical_positions[heading]
        if not positions:
            errors.append(ValidationError("MISSING_HEADING", f"見出し「## {heading}」が見つかりません。", section=heading))
        elif len(positions) > 1:
            errors.append(ValidationError(
                "DUPLICATE_HEADING", f"見出し「## {heading}」が{len(positions)}回出現しています(1回だけにしてください)。",
                section=heading,
            ))

    present_in_order = [
        (heading, scan.canonical_positions[heading][0])
        for heading in CANONICAL_HEADINGS
        if len(scan.canonical_positions[heading]) == 1
    ]
    sorted_by_line = sorted(present_in_order, key=lambda pair: pair[1])
    if [h for h, _ in present_in_order] != [h for h, _ in sorted_by_line]:
        errors.append(ValidationError(
            "HEADING_ORDER_INVALID",
            "見出しの順序が正式な順序(管理ID→現在の問題→原因に関する仮説→目的→"
            "期待動作・決定事項→非対象範囲→受入条件→テスト観点→リスク→"
            "人間確認事項→変更区分→参考資料)と一致していません。",
        ))
    return errors


# ---------------------------------------------------------------------------
# セクション内容抽出・実質的記載の判定
# ---------------------------------------------------------------------------

def _extract_section_raw_lines(
    spec_lines: list[str], scan: _HeadingScan,
) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    for heading in CANONICAL_HEADINGS:
        positions = scan.canonical_positions[heading]
        if len(positions) != 1:
            continue
        start = positions[0]
        end = next((ln for ln in scan.any_heading_lines if ln > start), len(spec_lines))
        sections[heading] = spec_lines[start + 1:end]
    return sections


class _ContentKind(str, Enum):
    EMPTY = "EMPTY"
    NONE_TOKEN = "NONE_TOKEN"
    CONTENT = "CONTENT"


def _classify_content(raw_lines: list[str]) -> _ContentKind:
    text = _strip_html_comments("\n".join(raw_lines))
    if not text.strip():
        return _ContentKind.EMPTY
    normalized = _DECORATION_CHARS_RE.sub("", text)
    if not normalized:
        return _ContentKind.EMPTY
    if normalized == "なし":
        return _ContentKind.NONE_TOKEN
    return _ContentKind.CONTENT


def _validate_section_content(sections: dict[str, list[str]]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for heading, raw_lines in sections.items():
        if heading == CHANGE_SCOPE_HEADING:
            continue  # 専用の_validate_change_scopeが判定する(固定ラベルとの区別が必要なため)
        kind = _classify_content(raw_lines)
        if heading in REQUIRED_SUBSTANTIVE_HEADINGS:
            if kind is not _ContentKind.CONTENT:
                errors.append(ValidationError(
                    "MISSING_REQUIRED_CONTENT", f"「{heading}」に実質的な内容がありません。", section=heading,
                ))
        else:
            if kind is _ContentKind.EMPTY:
                errors.append(ValidationError(
                    "MISSING_REQUIRED_CONTENT",
                    f"「{heading}」が空欄です。該当が無い場合は「なし」と記載してください。",
                    section=heading,
                ))
    return errors


# ---------------------------------------------------------------------------
# 変更区分検証
#
# 「変更区分」はテンプレート自体が固定ラベル付きの空欄骨組み
# (`- サービス仕様変更：`等)を含むため、汎用の_classify_contentだけでは
# 「ラベル文字がある=実質内容あり」と誤判定してしまう(ラベルの値部分が
# 空でも、ラベル自体の文字列に実在の文字が含まれるため)。
#
# AUTO-001-05-01-R2: 当初は「既知の固定ラベルに一致しない残り行」を
# 無条件に合格材料として扱うフォールバックを持っていたが、これは
# 3つの正式区分のいずれにも属さない自由記述(例: 本文末尾の無関係な
# 補足、「その他の変更」のような非正式ラベル)で合格してしまう抜け道
# になっていた。そのため、このフォールバックは完全に廃止し、値として
# 数えるのは次の2種類だけに限定する。
#   (a) 正式な固定ラベルと同じ行に書かれた値
#   (b) 正式な固定ラベル行(または同じラベルへの継続行)に直後で連続し、
#       かつ行頭に半角スペースまたはタブでインデントされている継続行
#       (Markdownのリスト項目としての字下げによる構造的な関連付け)
# 空行、非インデント行、未知のラベル行はいずれも継続関係を断ち切り、
# 以後の行は次に正式ラベル行が現れるまでどの区分にも属さない
# (安全側: 曖昧な場合は合格材料に含めない)。
# ---------------------------------------------------------------------------

_CHANGE_SCOPE_INDENT_RE = re.compile(r"^[ \t]")


def _validate_change_scope(sections: dict[str, list[str]]) -> list[ValidationError]:
    raw_lines = sections.get(CHANGE_SCOPE_HEADING)
    if raw_lines is None:
        return []  # 見出し自体が無い/重複している場合は既にMISSING_HEADING等で報告済み

    label_value_lines: dict[str, list[str]] = {label: [] for label in CHANGE_SCOPE_LABELS}
    current_label: Optional[str] = None

    for line in raw_lines:
        if not line.strip():
            current_label = None  # 空行は継続関係を断ち切る
            continue

        m = _CHANGE_SCOPE_LINE_RE.match(line.strip())
        if m and m.group(1) in CHANGE_SCOPE_LABELS:
            label = m.group(1)
            label_value_lines[label].append(m.group(2))
            current_label = label
            continue

        if current_label is not None and _CHANGE_SCOPE_INDENT_RE.match(line):
            # インデントされた継続行だけを、直前の正式ラベルへ構造的に関連付ける
            label_value_lines[current_label].append(line.strip())
            continue

        # 未知のラベル行・非インデントの無関係行はどの区分にも属さない
        current_label = None

    has_specified_label = any(
        _classify_content(values) is _ContentKind.CONTENT
        for values in label_value_lines.values()
    )
    if has_specified_label:
        return []

    return [ValidationError(
        "MISSING_REQUIRED_CONTENT",
        f"「{CHANGE_SCOPE_HEADING}」に実質的な値が記載された分類がありません"
        "(各項目が空欄・HTMLコメントのみ・「なし」のいずれか、または正式な区分に"
        "構造的に関連付けられていない記述のみです)。",
        section=CHANGE_SCOPE_HEADING,
    )]


# ---------------------------------------------------------------------------
# 管理ID検証
# ---------------------------------------------------------------------------

def _validate_management_id(sections: dict[str, list[str]]) -> list[ValidationError]:
    raw_lines = sections.get(MANAGEMENT_ID_HEADING)
    if raw_lines is None:
        return []
    text = _strip_html_comments("\n".join(raw_lines))
    if _classify_content(raw_lines) is not _ContentKind.CONTENT:
        return []  # 空欄等はMISSING_REQUIRED_CONTENTが既に報告する

    tokens = [t.strip(_TOKEN_STRIP_CHARS) for t in re.split(r"\s+", text)]
    tokens = [t for t in tokens if t]
    candidates = sorted({t for t in tokens if _ID_SHAPE_RE.match(t)})

    if not candidates:
        return [ValidationError(
            "INVALID_MANAGEMENT_ID", f"管理IDの形式(例: AUTO-001-05-01)に一致する記載が見つかりません: {text.strip()!r}",
            section=MANAGEMENT_ID_HEADING,
        )]
    if len(candidates) > 1:
        return [ValidationError(
            "AMBIGUOUS_MANAGEMENT_ID",
            f"管理IDらしき記載が複数あり一意に決定できません: {candidates}",
            section=MANAGEMENT_ID_HEADING,
        )]
    candidate = candidates[0]
    if not MANAGEMENT_ID_STRICT_RE.match(candidate):
        return [ValidationError(
            "INVALID_MANAGEMENT_ID", f"管理ID「{candidate}」が形式(例: AUTO-001-05-01)を満たしていません。",
            section=MANAGEMENT_ID_HEADING,
        )]
    return []


# ---------------------------------------------------------------------------
# 受入条件検証
# ---------------------------------------------------------------------------

def _validate_acceptance_criteria(sections: dict[str, list[str]]) -> list[ValidationError]:
    raw_lines = sections.get(ACCEPTANCE_CRITERIA_HEADING)
    if raw_lines is None:
        return []

    errors: list[ValidationError] = []
    well_formed: list[tuple[int, int, str]] = []  # (line_no, id_int, id_str)
    any_ac_like = False

    for line in raw_lines:
        stripped_for_check = line.strip()
        if not stripped_for_check:
            continue
        m = _AC_STRICT_LINE_RE.match(line)
        if m:
            any_ac_like = True
            digits, desc = m.group(1), m.group(2)
            if len(digits) != 2:
                errors.append(ValidationError(
                    "ACCEPTANCE_CRITERION_FORMAT",
                    f"受入条件ID「AC-{digits}」は2桁の連番形式(例: AC-01)にしてください。",
                    section=ACCEPTANCE_CRITERIA_HEADING,
                ))
                continue
            if not _strip_html_comments(desc).strip():
                errors.append(ValidationError(
                    "ACCEPTANCE_CRITERION_DESCRIPTION_MISSING",
                    f"受入条件「AC-{digits}」に実質的な説明がありません。",
                    section=ACCEPTANCE_CRITERIA_HEADING,
                ))
                continue
            well_formed.append((0, int(digits), digits))
            continue

        if _AC_LOOSE_HINT_RE.search(line):
            any_ac_like = True
            errors.append(ValidationError(
                "ACCEPTANCE_CRITERION_FORMAT",
                f"「{stripped_for_check}」は`- [ ] AC-01: 説明`の形式ではありません。",
                section=ACCEPTANCE_CRITERIA_HEADING,
            ))

    if not any_ac_like:
        errors.append(ValidationError(
            "ACCEPTANCE_CRITERIA_MISSING", "受入条件が1件も見つかりません(`- [ ] AC-01: ...`形式で記載してください)。",
            section=ACCEPTANCE_CRITERIA_HEADING,
        ))
        return errors

    seen: dict[str, int] = {}
    for _, _, digits in well_formed:
        seen[digits] = seen.get(digits, 0) + 1
    for digits, count in seen.items():
        if count > 1:
            errors.append(ValidationError(
                "ACCEPTANCE_CRITERION_DUPLICATE_ID", f"受入条件ID「AC-{digits}」が{count}回重複しています。",
                section=ACCEPTANCE_CRITERIA_HEADING,
            ))

    ints_in_order = [n for (_, n, _) in well_formed]
    if ints_in_order and ints_in_order != list(range(1, len(ints_in_order) + 1)):
        errors.append(ValidationError(
            "ACCEPTANCE_CRITERION_SEQUENCE_INVALID",
            f"受入条件IDはAC-01から1ずつ連番にしてください(実際の並び: {['AC-%02d' % n for n in ints_in_order]})。",
            section=ACCEPTANCE_CRITERIA_HEADING,
        ))

    return errors


# ---------------------------------------------------------------------------
# 公開API
# ---------------------------------------------------------------------------

def _run_validation(text: str) -> list[ValidationError]:
    normalized = _normalize_newlines(text)
    lines = normalized.split("\n")
    fence_mask_full = _fence_mask(lines)

    start_idx, end_idx, marker_errors = _validate_markers(lines, fence_mask_full)
    if start_idx is None or end_idx is None:
        return marker_errors

    spec_lines = lines[start_idx + 1:end_idx]
    spec_fence_mask = _fence_mask(spec_lines)
    spec_comment_mask = _comment_mask(spec_lines, spec_fence_mask)
    heading_mask = [a or b for a, b in zip(spec_fence_mask, spec_comment_mask)]

    scan = _scan_headings(spec_lines, heading_mask)
    heading_errors = _validate_headings(scan)

    sections = _extract_section_raw_lines(spec_lines, scan)
    content_errors = _validate_section_content(sections)
    change_scope_errors = _validate_change_scope(sections)
    management_id_errors = _validate_management_id(sections)
    ac_errors = _validate_acceptance_criteria(sections)

    return [
        *marker_errors,
        *heading_errors,
        *content_errors,
        *change_scope_errors,
        *management_id_errors,
        *ac_errors,
    ]


def validate_issue_body(text: str) -> ValidationResult:
    """Issue本文の文字列を受け取り、判定結果を返す。

    GitHub API・Anthropic API・その他の外部通信は一切行わない。
    どのような文字列入力に対しても例外を送出せず、想定外の内部エラーは
    ValidationStatus.INTERNAL_ERROR として結果に包んで返す。
    """
    try:
        if not isinstance(text, str):
            raise TypeError(f"text must be str, got {type(text).__name__}")
        errors = _run_validation(text)
    except Exception as exc:  # noqa: BLE001 - 内部エラーとして状態化するために意図的に広く捕捉する
        return ValidationResult(
            status=ValidationStatus.INTERNAL_ERROR,
            errors=[ValidationError("INTERNAL_ERROR", f"validator内部で例外が発生しました: {exc!r}")],
        )

    if errors:
        return ValidationResult(status=ValidationStatus.CONTRACT_VIOLATION, errors=errors)
    return ValidationResult(status=ValidationStatus.PASS, errors=[])


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _read_input(argv: list[str]) -> str:
    if argv and argv[0] not in ("--json", "--human-only"):
        return Path(argv[0]).read_text(encoding="utf-8")
    return sys.stdin.read()


def main(argv: Optional[list[str]] = None) -> int:
    import json as _json

    argv = list(sys.argv[1:] if argv is None else argv)
    human_only = "--human-only" in argv
    positional = [a for a in argv if not a.startswith("--")]

    try:
        text = _read_input(positional)
    except OSError as exc:
        print(f"入力の読み込みに失敗しました: {exc}", file=sys.stderr)
        return 2

    result = validate_issue_body(text)

    if human_only:
        print(result.to_human_text())
    else:
        payload = result.to_machine_dict()
        payload["human_summary"] = result.to_human_text()
        print(_json.dumps(payload, ensure_ascii=False, indent=2))

    if result.status is ValidationStatus.PASS:
        return 0
    if result.status is ValidationStatus.CONTRACT_VIOLATION:
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
