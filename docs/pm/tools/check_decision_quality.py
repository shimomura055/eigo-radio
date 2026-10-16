"""check_decision_quality.py

DQIパッケージP(PM_GOVERNANCE.md 27節、2026-10-16ユーザー正式採用)のP4機械Validator。
RESULT_PACKET(.md)と任意のFable受入記録(.md)を読み、PM判断の「被覆・矛盾・再質問・
無関係混入」の疑いを機械的に列挙する記録用ツール。**非ブロッキング**(終了コードは常に0、
findingsは「確認要」であり判定ではない。findingsだけで仕様採用・廃止・完了判定・STOPをしない)。

管理ID: PM-20261016-AUW-CLOSEOUT-DQI-PRODUCTION-01(委任_01)。
構造・JSON出力様式は docs/pm/tools/check_delegation_prompt.py(argparse / --json-out /
--pretty / 終了コード常時0)を踏襲した。

被覆チェック4点:
  C1 重大NGが是正対象・STOP理由から漏れていないか
     (判定整合行 `重大NG=[..] / 主因=[..] / 是正対象=[..] / STOP理由=[..] / 提示=..` を使用)
  C2 ACCEPTEDと未解決の重大NGの矛盾(+主因が重大NGでない/提示「可」と重大NGの併存)
  C3 REGISTERで判断済みの#番号が再びUDR/判断待ち扱いになっていないか
  C4 現在の管理ID/Familyと無関係な項目(Family A/B/C語・他管理ID・OPEN番号の羅列)が
     判断欄へ混入していないか

使い方:
  python docs/pm/tools/check_decision_quality.py --packet <RESULT_PACKET.md>
      [--acceptance <受入記録.md>] [--register docs/pm/USER_DECISION_REGISTER_01.md]
      [--managed-id <ID>] [--decided 83,84] [--json-out <path>] [--pretty]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# 2026-10-16ユーザー正式判断(原文=docs/pm/delegation_log/
# 2026-10-16_PM-20261016-AUW-CLOSEOUT-DQI-PRODUCTION-01_USER.md)で「判断済み/再発行しない」
# 扱いになった#番号。REGISTER本体はこの時点で未更新のため、既定として内蔵する(--decidedで追加可)。
#   80-82,88-91: 判断済み=採用(§2・§3)
#   83,84,86,87: 既存REGISTERで判断済み
#   85,93,94,95: AUW追加改修は行わない=記録のみ、判断要求を再発行しない(§1-A/§7)
#   92: Family C開発停止(§1-C)=判断不要
BUILTIN_DECIDED = {80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95}

# 重大NGの正の言及(IDなし運用の検出用)。否定語を含む行は除外する。
SEVERE_TOKEN_RE = re.compile(
    r"重大NG|意味反転|Fact逆転|MAJOR[\s*]*(?:Fact|意味|逆転|反転)|(?:原稿|記事|音声|成果物)[^。\n]{0,10}取り違え"
    r"|必須音声[^。\n]{0,6}欠落|音声[^。\n]{0,4}欠落|STOPPED[\s]*(?:枠|\d)|Fact欠落|重要Fact欠落"
)
NEGATION_RE = re.compile(
    r"なし|無し|ゼロ|0件|ない|ではない|非該当|解消|是正済|不在|N/A|過剰STOP|歯止め|定義|2軸|例示|基準|検出し(?:ない|なかった)|否定"
)
JUDGE_LINE_RE = re.compile(r"判定整合\s*[::=]\s*(.+)")
FIELD_RE = re.compile(r"(重大NG|主因|是正対象|STOP理由|提示)\s*=\s*(\[[^\]]*\]|[^/\n]*)")
UDR_TRIGGER_RE = re.compile(
    r"USER_DECISION_REQUIRED|\bUDR\b|ユーザー判断が必要|判断を求|判断待ち|ユーザー判断事項|判断候補"
)
UDR_NEGATIVE_RE = re.compile(r"判断済み|再質問しない|再発行しない|記録のみ|判断不要|区分A|A区分|既判断|解消")
NUM_RE = re.compile(r"#(\d{1,3})\b")
FAMILY_ABC_RE = re.compile(r"Family[\s_\-]*([ABC])(?![A-Za-z0-9])|FAMILY-([ABC])-", re.IGNORECASE)
MANAGED_ID_RE = re.compile(r"\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+){2,}\b")
OPEN_RE = re.compile(r"OPEN-\d+")
JUDGMENT_REGION_HEAD_RE = re.compile(
    r"判断候補|ユーザー判断|USER_DECISION|\bUDR\b|判断事項|判断待ち"
)
ACCEPT_RE = re.compile(r"(?<![A-Za-z])ACCEPTED(?![A-Za-z])")
ACCEPT_NEG_RE = re.compile(r"NOT[\s_]*ACCEPTED|ACCEPTED(?:は)?不可|ACCEPTEDとしない|ACCEPTEDにしない|未ACCEPTED|非ACCEPTED")


def _decode(path: str) -> str:
    return Path(path).read_text(encoding="utf-8", errors="replace")


def _norm_field(val: str) -> list[str]:
    """`[A, B]`や`なし`をIDリストへ。なし/空は[]。"""
    v = val.strip().strip("[]").strip()
    if not v or re.fullmatch(r"(なし|無し|none|-|—|N/A)", v, re.IGNORECASE):
        return []
    return [x.strip() for x in re.split(r"[,、，\s]+", v) if x.strip()]


def parse_judgment_line(text: str) -> dict | None:
    """最初の`判定整合:`行を解析する。無ければNone。"""
    for i, line in enumerate(text.splitlines(), 1):
        m = JUDGE_LINE_RE.search(line)
        if not m:
            continue
        body = m.group(1)
        fields = {k: v.strip() for k, v in FIELD_RE.findall(body)}
        if "重大NG" not in fields:
            continue
        return {
            "line": i,
            "raw": line.strip()[:300],
            "severe": _norm_field(fields.get("重大NG", "")),
            "main_cause": _norm_field(fields.get("主因", "")),
            "fix_targets": _norm_field(fields.get("是正対象", "")),
            "stop_reasons": _norm_field(fields.get("STOP理由", "")),
            "present": fields.get("提示", "").strip(),
            "fields": fields,
        }
    return None


def find_accepted(text: str) -> list[dict]:
    """無条件に近いACCEPTED宣言の行を返す(NOT ACCEPTED/ACCEPTED不可は除外)。"""
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        if not ACCEPT_RE.search(line):
            continue
        if "判定" not in line and "受入" not in line:
            continue
        stripped = ACCEPT_NEG_RE.sub("", line)
        if ACCEPT_RE.search(stripped):
            hits.append({"line": i, "text": line.strip()[:200]})
    return hits


def find_unstructured_severe(text: str) -> list[dict]:
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        if SEVERE_TOKEN_RE.search(line) and not NEGATION_RE.search(line):
            hits.append({"line": i, "text": line.strip()[:200]})
    return hits


def decided_numbers(register_text: str | None, extra: set[int]) -> set[int]:
    nums = set(BUILTIN_DECIDED) | set(extra)
    if register_text:
        for m in re.finditer(r"#(\d{1,3})\b[^#\n]{0,60}?判断済み", register_text):
            nums.add(int(m.group(1)))
    return nums


def current_managed_id(packet: str, given: str | None) -> str | None:
    if given:
        return given
    m = re.search(r"管理ID[::]?\s*`?([A-Z][A-Z0-9\-]+)", packet)
    return m.group(1) if m else None


def judgment_region_lines(text: str) -> list[tuple[int, str]]:
    """判断欄とみなす行: 見出し/箇条の先頭が判断語を含む行と、その直後の箇条(空行/見出しまで)。"""
    lines = text.splitlines()
    out: list[tuple[int, str]] = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        if JUDGMENT_REGION_HEAD_RE.search(ln):
            out.append((i + 1, ln))
            j = i + 1
            if ln.lstrip().startswith("#") or ln.rstrip().endswith((":", ":")):
                while j < len(lines) and lines[j].strip() and not lines[j].lstrip().startswith("#"):
                    out.append((j + 1, lines[j]))
                    j += 1
            i = j
        else:
            i += 1
    return out


def run_check(packet: str, acceptance: str | None, register: str | None,
              managed_id: str | None, extra_decided: set[int]) -> dict:
    text = packet + ("\n" + acceptance if acceptance else "")
    findings: list[dict] = []

    def add(check: str, level: str, msg: str, **ev):
        findings.append({"check": check, "level": level, "message": msg, **ev})

    jl = parse_judgment_line(text)
    accepted = find_accepted(text)

    # --- C1/C2 判定整合 ---
    if jl is not None:
        severe = jl["severe"]
        covered = set(jl["fix_targets"]) | set(jl["stop_reasons"])
        for sid in severe:
            if sid not in covered:
                add("C1", "warn", f"重大NG {sid} が是正対象・STOP理由のどちらにも含まれていない",
                    line=jl["line"], evidence=jl["raw"])
        if severe and accepted:
            add("C2", "warn", "重大NGありなのに無条件に近いACCEPTED宣言がある",
                line=accepted[0]["line"], evidence=accepted[0]["text"])
        if severe and jl["main_cause"] and not all(m in severe for m in jl["main_cause"]):
            add("C2", "warn", "重大NGがあるのに主因が重大NGから選ばれていない(主因の選定誤りの疑い)",
                line=jl["line"], evidence=jl["raw"])
        if severe and jl["present"].startswith("可"):
            add("C2", "warn", "重大NGありなのに提示=可(例外K以外は不可)",
                line=jl["line"], evidence=jl["raw"])
    else:
        unstructured = find_unstructured_severe(text)
        if unstructured:
            if accepted:
                add("C2", "warn",
                    "判定整合行がなく、重大NGを示唆する記述とACCEPTED宣言が併存している(P1の判定整合行を要確認)",
                    line=unstructured[0]["line"], evidence=unstructured[0]["text"],
                    accepted_line=accepted[0]["line"])
            else:
                has_form = bool(re.search(r"受入記録|最終受入判定", text))
                add("C1", "warn" if has_form else "info",
                    "判定整合行がなく、重大NGを示唆する記述がある(是正対象・STOP理由への被覆を要確認)",
                    line=unstructured[0]["line"], evidence=unstructured[0]["text"])

    # --- C3 判断済み#の再UDR化 ---
    decided = decided_numbers(register, extra_decided)
    for i, line in enumerate(text.splitlines(), 1):
        if not UDR_TRIGGER_RE.search(line):
            continue
        if UDR_NEGATIVE_RE.search(line):
            continue
        for m in NUM_RE.finditer(line):
            n = int(m.group(1))
            if n in decided:
                add("C3", "warn", f"REGISTER #{n} は判断済み/再発行しない扱いだが、判断要求の文脈に出現",
                    line=i, evidence=line.strip()[:200], number=n)

    # --- C4 判断欄への無関係混入 ---
    mid = current_managed_id(packet, managed_id)
    for i, line in ((n, l) for n, l in judgment_region_lines(text)):
        for m in FAMILY_ABC_RE.finditer(line):
            fam = (m.group(1) or m.group(2)).upper()
            add("C4", "warn", f"判断欄にFamily {fam}(開発停止対象、PM_GOVERNANCE 27-7)の語がある",
                line=i, evidence=line.strip()[:200])
            break
        others = sorted({x for x in MANAGED_ID_RE.findall(line)
                         if mid and x != mid and not x.startswith("OPEN") and x not in ("USER_DECISION_REQUIRED",)
                         and "_" not in x and re.search(r"[A-Z]{3,}", x) and "-" in x})
        # 現管理IDの接頭辞/部分一致と、27節等の定数語は除外
        others = [x for x in others if not (mid and (x in mid or mid in x))]
        if others:
            add("C4", "info", "判断欄に現在の管理IDと異なる管理IDがある(関連が薄くないか要確認)",
                line=i, evidence=line.strip()[:200], ids=others[:5])
        opens = set(OPEN_RE.findall(line))
        if len(opens) >= 3:
            add("C4", "info", "判断欄にOPEN番号が3件以上並ぶ(番号の列挙だけで判断を求めていないか要確認、P3)",
                line=i, evidence=line.strip()[:200], ids=sorted(opens)[:6])

    by_level = {"warn": 0, "info": 0}
    for f in findings:
        by_level[f["level"]] = by_level.get(f["level"], 0) + 1
    return {
        "status": "FINDINGS" if findings else "OK",
        "non_blocking": True,
        "managed_id": mid,
        "parsed": {
            "judgment_line": None if jl is None else {k: v for k, v in jl.items() if k != "fields"},
            "accepted_lines": [a["line"] for a in accepted],
            "decided_count": len(decided),
        },
        "counts": by_level,
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="DQI P4 機械Validator(非ブロッキング、常にexit 0)")
    ap.add_argument("--packet", required=True, help="RESULT_PACKET(.md)")
    ap.add_argument("--acceptance", help="Fable受入記録(.md、任意)")
    ap.add_argument("--register", help="USER_DECISION_REGISTER_01.md(任意、判断済み#の補強)")
    ap.add_argument("--managed-id", help="現在の管理ID(省略時はpacketの『管理ID』行から推定)")
    ap.add_argument("--decided", default="", help="追加の判断済み#番号(カンマ区切り)")
    ap.add_argument("--json-out")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args(argv)

    try:
        packet = _decode(args.packet)
        acceptance = _decode(args.acceptance) if args.acceptance else None
        register = _decode(args.register) if args.register else None
        extra = {int(x) for x in re.split(r"[,\s]+", args.decided) if x.isdigit()}
        result = run_check(packet, acceptance, register, args.managed_id, extra)
    except Exception as e:  # 非ブロッキング: 失敗も結果として記録しexit 0
        result = {"status": "ERROR", "non_blocking": True, "error": f"{type(e).__name__}: {e}", "findings": []}

    out = json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None)
    if args.json_out:
        Path(args.json_out).write_text(out, encoding="utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
