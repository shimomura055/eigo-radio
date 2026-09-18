"""kp_mapping_aggregate.py

USER-TEST-SCRIPT-READABILITY-PROD-01 Phase C-4.
20 level分の `user_test/translations/<article_id>/<level>/kp_mapping.json` を
集約し、全100 Key Phraseの一覧(JSON+Markdown表)と集計(total/mapped/exact/
non_exact種別内訳/unresolved)を出力する。

highlighted(E2E実測)は本スクリプト単独では算出できないため、別途
`--highlight-counts` (article_id:level:count 形式カンマ区切り、または
readability checkの結果JSONパス)を渡した場合のみ埋める。渡されなければ
null(未計測)とする。

使い方:
  python docs/pm/tools/kp_mapping_aggregate.py \
      --translations user_test/translations \
      --out-json docs/pm/closeout_136_e2e/script_readability_prod_01/phase_c/kp_mapping_all100.json \
      --out-md docs/pm/closeout_136_e2e/script_readability_prod_01/phase_c/kp_mapping_all100.md \
      [--e2e-result path/to/e2e_result.json]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_highlight_counts(e2e_result_path: str | None) -> dict:
    """readability checkerの結果JSON(--out相当)から
    {name(=f"{article_id}_{level}"): highlight_count} を取り出す。"""
    if not e2e_result_path:
        return {}
    data = json.loads(Path(e2e_result_path).read_text(encoding="utf-8"))
    out = {}
    for key, r in data.get("results", {}).items():
        if key.endswith("_mobile"):
            continue
        name = r.get("name")
        hl = r.get("checks", {}).get("highlight_count", {})
        if name and hl:
            out[name] = hl.get("actual")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--translations", required=True)
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--out-md", required=True)
    ap.add_argument("--e2e-result", default=None,
                     help="highlighted(E2E実測)を埋めるためのuser_test_readability_check.py出力JSON(任意)")
    args = ap.parse_args()

    tdir = Path(args.translations)
    highlight_counts = load_highlight_counts(args.e2e_result)

    rows = []
    total = mapped = exact = non_exact = unresolved = 0
    non_exact_breakdown: dict[str, int] = {}

    mapping_files = sorted(tdir.glob("*/*/kp_mapping.json"))
    for mp in mapping_files:
        level = mp.parent.name
        article_id = mp.parent.parent.name
        data = json.loads(mp.read_text(encoding="utf-8"))
        name = f"{article_id}_{level}"
        for kp in data.get("key_phrases", []):
            mtype = kp.get("mapping_type")
            total += 1
            if mtype == "UNRESOLVED" or mtype is None:
                unresolved += 1
            else:
                mapped += 1
                if mtype == "exact":
                    exact += 1
                else:
                    non_exact += 1
                    non_exact_breakdown[mtype] = non_exact_breakdown.get(mtype, 0) + 1
            rows.append({
                "article_id": article_id,
                "level": level,
                "phrase": kp.get("phrase"),
                "matched_text": kp.get("matched_text"),
                "mapping_type": mtype,
                "occurrences": kp.get("occurrences"),
                "highlighted": highlight_counts.get(name),
                "unresolved": mtype == "UNRESOLVED" or mtype is None,
                "rationale": kp.get("rationale"),
            })

    summary = {
        "total": total,
        "mapped": mapped,
        "exact": exact,
        "non_exact": non_exact,
        "non_exact_breakdown": non_exact_breakdown,
        "unresolved": unresolved,
        "levels_covered": len(mapping_files),
    }

    out = {"summary": summary, "rows": rows}
    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_json).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        "# Key Phrase mapping 全100一覧 (Phase C-4)",
        "",
        f"levels_covered={summary['levels_covered']} total={total} mapped={mapped} "
        f"exact={exact} non_exact={non_exact} unresolved={unresolved}",
        f"non_exact_breakdown={json.dumps(non_exact_breakdown, ensure_ascii=False)}",
        "",
        "| article_id | level | phrase | matched_text | mapping_type | occurrences | highlighted | unresolved |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        md_lines.append(
            f"| {r['article_id']} | {r['level']} | {r['phrase']} | {r['matched_text']} | "
            f"{r['mapping_type']} | {r['occurrences']} | {r['highlighted']} | {r['unresolved']} |"
        )
    Path(args.out_md).write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
