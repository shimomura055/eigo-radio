# FXPW(FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01) 委任_02B:
# Family X「In One Line」仕様(基本2文、必要な場合のみ3文。2026-10-16 09:00 JST / 原文§4、APPROVED_FOR_PRODUCTION)の
# 文数カウンタとFamily Xスコープ判定を持つ**中立module**(他のプロジェクトmoduleをimportしない純関数+contextvar)。
# Family X runner(er012 _run_writer_stage_once)とLocal Rewrite(er020 build_full_candidate_records)の
# 両方からimportできるよう、循環importを避けるためここに置く(WIRING_DESIGN_01.md §C-5/R-04)。
# Family A/B/C/Zでは family_x_in_one_line_scope() が立たないため、scope依存の検査は常に不発(挙動不変)。
from __future__ import annotations

import contextlib
import contextvars
import re

IN_ONE_LINE_SPEC_COUNTS = frozenset({2, 3})

_ABBREV = re.compile(
    r"\b(?:U\.S\.A|U\.S|U\.K|e\.g|i\.e|Mr|Mrs|Ms|Dr|Inc|Ltd|Co|vs|No|St|Jr|Sr)\.")
_SPLIT = re.compile(r"(?<=[.!?])[\"')\]”’]*\s+(?=[\"'(\[“‘]?[A-Z0-9$])")
_DOT_PLACEHOLDER = "\x00"


def count_in_one_line_sentences(text: str) -> int:
    """In One Line本文の文数。空は0。改行は文境界(各非空行を別々に数える)。
    略語(U.S./Mr./Mrs./Dr./Inc./vs./e.g./i.e./No./St.等)と小数点(3.5)では分割しない。
    引用符・括弧で閉じた終端(." / .') も文末として扱い、次が大文字・数字・$で始まる場合に分割する。"""
    total = 0
    for line in (text or "").splitlines():
        line = line.strip()
        if not line:
            continue
        protected = _ABBREV.sub(lambda m: m.group(0).replace(".", _DOT_PLACEHOLDER), line)
        total += len([p for p in _SPLIT.split(protected) if p.strip()])
    return total


def is_in_one_line_spec_ok(text: str) -> bool:
    return count_in_one_line_sentences(text) in IN_ONE_LINE_SPEC_COUNTS


_FAMILY_X_SCOPE: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "family_x_in_one_line_scope", default=False)


@contextlib.contextmanager
def family_x_in_one_line_scope():
    """Family X Local Rewrite等で「In One Lineの文数保持gate」を有効にする囲み。
    引数・設定dict・環境変数では有効化できない(このcontext managerのみ)。例外時も必ず元へ戻す。"""
    token = _FAMILY_X_SCOPE.set(True)
    try:
        yield
    finally:
        _FAMILY_X_SCOPE.reset(token)


def is_family_x_in_one_line_scope() -> bool:
    return _FAMILY_X_SCOPE.get()
