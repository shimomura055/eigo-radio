# ============================================================
# er021_offline_false_reject_detector_01.py
# 管理ID: EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02(Phase 2)
# ============================================================
# 性質: read-only・¥0(API呼び出しなし、Sonnet不要のread-only集計。
# haiku-workerへ委任可)。既存telemetry.jsonl(er021_output/en_asr_
# semantic_equivalence_production_wiring_01/telemetry.jsonl)を定期的に
# 走査し、strict版Tier1合成規則(diff-anchored+punctuation由来局所差分
# 吸収)実装後もなお救済されていないNG記録のうち、「punctuation起因の
# 可能性がある新種候補」(=diff-anchored opがすべてliteral atomのみで
# 構成されている、すなわち数値/時刻の真の値相違ではない)を抽出し、
# 一覧化する。**自動でルールへ組み込むことはしない**(read-only、
# 人間/Fableのレビュー対象を挙げるだけ)。
#
# 実行方法(推奨頻度: 新規記事生成のたびに増分するtelemetryに対して、
# 週次〜記事1本ごとの単位で実行。判断を含まない定型集計のため
# haiku-worker委任可):
#   .venv/Scripts/python.exe er021_offline_false_reject_detector_01.py
#   > er021_output/coverage_review_02/offline_false_reject_detector_01_result.json
#
# 出力: 母数・「punctuation起因候補」件数・各候補のcanonical/asr/diff内訳
# (人間が目視で「新しい閉じた吸収規則を追加すべきか」を判断するための
# 一次情報)。

from __future__ import annotations

import json
import re
import sys

sys.path.insert(0, ".")
import er021_en_asr_semantic_equivalence_production_01 as tier1  # noqa: E402

TELEMETRY_PATH = "er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl"


import difflib  # noqa: E402


def _diagnose(canonical: str, asr: str) -> dict | None:
    """診断用の内部呼び出し(read-onlyの分析目的でのみtier1内部関数を
    直接使う。Production呼び出し経路[classify_asr_match]には一切影響
    しない)。現行のstrict版Tier1合成規則で救済されない(=まだNGの)
    記録を2種類に分類する:
    (a) "cap_limited": 個々のop単位では既存の`_closed_punctuation_diff_
        ok()`と同じ閉じた規則(literalのみ・alnum内容完全一致)を満たす
        にもかかわらず、op数上限(`_TIER1_MAX_ABSORBED_PUNCT_OPS`)または
        atom比率上限(`_TIER1_MAX_ABSORBED_PUNCT_ATOM_RATIO`)超過のみを
        理由に全体が非等価のままになっているケース。これは「規則自体は
        正しく機能しているが、防御的上限が厳しすぎる可能性がある」という
        明確に actionable な信号であり、上限値の見直し候補として扱う。
    (b) "near_match": 個々のopのalnum内容が完全一致はしないが高い類似度
        (0.85以上)を持つケース(略語・綴りゆれ等の**未知の**新しい閉じた
        吸収規則の候補になり得るが、対義語[can/cannot]・単複[point/
        points]等の**真の内容差**も紛れ込みやすいため、必ず人間が目視で
        判断すること。自動採用は絶対にしない)。
    どちらにも該当しない場合はNone(数値/時刻atomが絡む真の値相違、または
    alnum類似度が低い無関係な内容差である可能性が高い)。"""
    try:
        ca = tier1._tier1_atoms(canonical)
        aa = tier1._tier1_atoms(asr)
    except Exception:
        return None
    if not ca or not aa:
        return None
    ca_keys = [tier1._atom_key(a) for a in ca]
    aa_keys = [tier1._atom_key(a) for a in aa]
    sm = difflib.SequenceMatcher(None, ca_keys, aa_keys, autojunk=False)
    ops = [op for op in sm.get_opcodes() if op[0] != "equal"]
    if not ops:
        return None
    all_literal = all(
        all(a["kind"] == "literal" for a in ca[i1:i2]) and all(a["kind"] == "literal" for a in aa[j1:j2])
        for _, i1, i2, j1, j2 in ops
    )
    if not all_literal:
        return None  # 数値/時刻atomが絡む=真の値相違の可能性が高い、候補から除外

    op_ratios = []
    all_ops_exact_alnum_match = True
    for _, i1, i2, j1, j2 in ops:
        canon_alnum = "".join(re.sub(r"[^a-z0-9]", "", a["word"]) for a in ca[i1:i2])
        asr_alnum = "".join(re.sub(r"[^a-z0-9]", "", a["word"]) for a in aa[j1:j2])
        if not canon_alnum or not asr_alnum:
            return None
        ratio = difflib.SequenceMatcher(None, canon_alnum, asr_alnum, autojunk=False).ratio()
        op_ratios.append(ratio)
        if ratio < 1.0:
            all_ops_exact_alnum_match = False

    total_atoms = max(len(ca), len(aa), 1)
    absorbed_atom_total = sum((i2 - i1) + (j2 - j1) for _, i1, i2, j1, j2 in ops)
    atom_ratio = absorbed_atom_total / total_atoms

    if all_ops_exact_alnum_match:
        exceeds_op_cap = len(ops) > tier1._TIER1_MAX_ABSORBED_PUNCT_OPS
        exceeds_ratio_cap = atom_ratio > tier1._TIER1_MAX_ABSORBED_PUNCT_ATOM_RATIO
        if exceeds_op_cap or exceeds_ratio_cap:
            category = "cap_limited"
        else:
            return None  # 理論上到達しない(全op exact matchかつcap内なら既にPASSしているはず)
    elif min(op_ratios) >= 0.85:
        category = "near_match"
    else:
        return None

    return {
        "category": category,
        "op_count": len(ops),
        "absorbed_atom_total": absorbed_atom_total,
        "atom_ratio": round(atom_ratio, 4),
        "op_alnum_ratios": [round(r, 4) for r in op_ratios],
        "ops_preview": [
            {"tag": tag, "canonical_words": [a["word"] for a in ca[i1:i2]],
             "asr_words": [a["word"] for a in aa[j1:j2]]}
            for tag, i1, i2, j1, j2 in ops[:5]
        ],
    }


def main() -> None:
    total = 0
    still_ng = 0
    cap_limited = []
    near_match = []

    with open(TELEMETRY_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            total += 1
            canonical, asr = rec.get("canonical"), rec.get("asr")
            if tier1.tier1_numeric_equivalence(canonical, asr) is not None:
                continue  # 現行実装で既に救済済み(reversalはoffline_telemetry_reclassify_01側の担当)
            still_ng += 1
            diag = _diagnose(canonical, asr)
            if diag is None:
                continue
            entry = {
                "canonical": canonical,
                "asr": asr,
                "prior_classification": rec.get("classification"),
                "prior_sub_reason": rec.get("sub_reason"),
                "diagnosis": diag,
            }
            (cap_limited if diag["category"] == "cap_limited" else near_match).append(entry)

    summary = {
        "telemetry_path": TELEMETRY_PATH,
        "total_records": total,
        "still_ng_after_current_tier1": still_ng,
        "cap_limited_count": len(cap_limited),
        "near_match_count": len(near_match),
        "note": ("cap_limited: op単位ではstrict版Tier1合成規則の閉じた基準"
                 "(literalのみ・alnum内容完全一致)を満たすが、op数上限/atom"
                 "比率上限のみで全体が非等価のままの record(上限値見直しの"
                 "actionableな候補)。near_match: alnum内容が完全一致では"
                 "ないが類似度0.85以上の record(未知の新しい閉じた吸収規則の"
                 "候補になり得るが、対義語・単複等の真の内容差も混在し得る"
                 "ため必ず人間が目視で判断すること)。いずれも本スクリプトは"
                 "自動でルールへ組み込まない(read-only)。"),
        "cap_limited_candidates": cap_limited,
        "near_match_candidates": near_match[:50],
        "near_match_candidates_truncated": len(near_match) > 50,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
