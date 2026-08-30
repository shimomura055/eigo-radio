# ============================================================
# er009_n1_routing_governance_10_legacy_scan.py
# ER-009-N1-POINT-RETRY-ROUTING-GOVERNANCE-10: Legacy Sol Hardcode Validator
# ============================================================
# 目的: 新パイプライン(er003_v1_*/er006_*/er008_*/er009_*)のソースコード内に、
# ER-006-MODEL-ROUTING-CONTRACT-01のSSOT(Luna)を迂回する"gpt-5.6-sol"の
# 生literal代入が紛れ込んでいないかを検出する。
#
# 対象外(誤検知させない):
#   - er002_* (ER-002 Japanese-source pipeline。CURRENT_SPEC.mdに現行仕様と
#     しての記載がなく、複数ファイルのdocstringで「Production(er002_*)は
#     一切変更せず」と明記されている、意図的に維持されている旧パイプライン。
#     WRITER_MODEL = "gpt-5.6-sol"のoriginal hardcode source
#     [er002_ja_free_markdown_restore.py]はここに属する)
#   - er003_v1_p*_preflight.py / er003_*_key_words*.py / er003_b1_article.py等
#     P-series(Point構造導入前、CURRENT_SPEC.mdで`HISTORICAL`と明記)の
#     preflight/test。これらはer002由来のSol設計を検証するための
#     `== "gpt-5.6-sol"`比較であり、hardcode代入ではない
#   - *_test.py / *_static_audit.py / *_boundary_test.py: fake response生成
#     やaudit対象文字列としての参照であり、実際のAPI callには使われない
#   - 本ファイル自身、er006_model_routing_contract_01.py(コメント内で
#     歴史的経緯として言及)
#
# 検出対象: 新パイプライン内で、識別子への"gpt-5.6-sol"直接代入
# (`XXX = "gpt-5.6-sol"`または`XXX == "gpt-5.6-sol"`という生literal)が
# 見つかった場合。routing.require_model()/require_model_or_override()を
# 経由しないSSOT迂回の兆候として扱う。
from __future__ import annotations

import os
import re

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

NEW_PIPELINE_PREFIXES = ("er003_v1_", "er006_", "er007_", "er008_", "er009_", "er011_")

# ファイル名(拡張子含む)完全一致での明示allowlist。理由は上記docstring参照。
FILE_ALLOWLIST = {
    "er009_n1_routing_governance_10_legacy_scan.py",
    "er009_n1_routing_governance_10_legacy_scan_test.py",
    "er009_n1_point_overlap_cost_closeout_09.py",  # ER-009-N1-...-09: 本件バグそのものを報告する分析文書(過去のSol誤用を引用)
}

SOL_LITERAL_RE = re.compile(r'[A-Za-z_][A-Za-z0-9_.]*\s*={1,2}\s*"gpt-5\.6-sol"')

# er003_v1_p<digit>...: Point構造導入前のP-series(p1/p1b/p2/p2b/p2d/p2e/p2f/p2g等)。
# CURRENT_SPEC.mdで`HISTORICAL`と明記されたシェルで、er002由来のSol設計を
# 検証するpreflightの`== "gpt-5.6-sol"`比較を含むが、SSOT迂回ではない。
P_SERIES_RE = re.compile(r"^er003_v1_p\d")


def _is_new_pipeline_file(filename: str) -> bool:
    if not filename.endswith(".py"):
        return False
    if P_SERIES_RE.match(filename):
        return False
    return filename.startswith(NEW_PIPELINE_PREFIXES)


def _is_test_or_audit_file(filename: str) -> bool:
    return (filename.endswith("_test.py") or filename.endswith("_test_01.py")
            or "_static_audit" in filename or "_boundary_test" in filename
            or filename.startswith("test_"))


def scan_repository(repo_root: str = REPO_ROOT) -> dict:
    """新パイプラインファイルを走査し、SSOT迂回のSol literal代入を検出する。
    戻り値: {"violations": [...], "scanned_files": int, "skipped_test_files": int}"""
    violations = []
    scanned = 0
    skipped_test = 0
    for entry in sorted(os.listdir(repo_root)):
        if not entry.endswith(".py"):
            continue
        if not _is_new_pipeline_file(entry):
            continue
        if entry in FILE_ALLOWLIST:
            continue
        if _is_test_or_audit_file(entry):
            skipped_test += 1
            continue
        path = os.path.join(repo_root, entry)
        if not os.path.isfile(path):
            continue
        scanned += 1
        with open(path, encoding="utf-8") as f:
            for lineno, line in enumerate(f, start=1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                code_part = line.split("#", 1)[0]  # 末尾のinlineコメントはliteral判定に含めない
                if SOL_LITERAL_RE.search(code_part):
                    violations.append({"file": entry, "line": lineno, "text": stripped})
    return {"violations": violations, "scanned_files": scanned, "skipped_test_files": skipped_test}


if __name__ == "__main__":
    result = scan_repository()
    print(f"走査対象ファイル数: {result['scanned_files']} "
          f"(test/audit除外: {result['skipped_test_files']})")
    if result["violations"]:
        print(f"違反 {len(result['violations'])}件検出:")
        for v in result["violations"]:
            print(f"  {v['file']}:{v['line']}: {v['text']}")
    else:
        print("違反なし。新パイプライン内にSSOT迂回のSol literal代入は見つかりませんでした。")
