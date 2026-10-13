# -*- coding: utf-8 -*-
"""FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_02 OF-X3: 既存成果物の候補ID方式itemに
canonicalization_view_itemsをoffline適用し、source_span拡張が起きる件数と前後文字列を一覧(API0円)。"""
import glob, json, os, sys
import er003_key_words_canonicalization as kc

OUT = "er071_output/m2p0_n01_production_wiring_01/completion_03/expansion_census_03.md"


def walk(o, found):
    if isinstance(o, dict):
        if o.get("source_reference_contract") and o.get("source_span") and o.get("source_sentence"):
            found.append(o)
        for v in o.values():
            walk(v, found)
    elif isinstance(o, list):
        for v in o:
            walk(v, found)


def main():
    seen = {}
    files = 0
    for path in glob.glob("er*_output/**/*.json", recursive=True):
        if os.path.getsize(path) > 20_000_000:
            continue
        try:
            raw = open(path, encoding="utf-8").read()
        except Exception:
            continue
        if '"source_reference_contract"' not in raw:
            continue
        try:
            d = json.loads(raw)
        except Exception:
            continue
        found = []
        walk(d, found)
        if found:
            files += 1
        for it in found:
            key = (it["source_span"], it["source_sentence"])
            seen.setdefault(key, []).append((path, it))
    expanded, total = [], 0
    for (span, sent), lst in sorted(seen.items()):
        total += 1
        it = lst[0][1]
        exp = kc.expand_dangling_source_span(it)
        if exp != span:
            expanded.append((span, exp, sent, len(lst), lst[0][0], it.get("key_phrase_role", "")))
    lines = ["# expansion_census_03 (案A-prime, OF-Y2、API 0円)", "",
             f"対象: er*_output配下で`source_reference_contract`を持つitem(候補ID方式)を含むJSON {files}ファイル。ユニーク(source_span, source_sentence) {total}件。",
             f"拡張が起きた件数: **{len(expanded)}件** / {total}。拡張はcanonicalization入力・Rule7判定にのみ使い、選定結果source_spanは不変。左端ガード(OF-X1)あり。", "",
             "| # | 元source_span | 拡張後 | 出現ファイル数 | 代表ファイル | role |", "|---|---|---|---|---|---|"]
    for i, (s, e, sent, n, p, role) in enumerate(expanded, 1):
        lines.append(f"| {i} | `{s}` | `{e}` | {n} | {p} | {role} |")
    lines += ["", "## 文(前後確認用)", ""]
    for i, (s, e, sent, n, p, role) in enumerate(expanded, 1):
        lines.append(f"{i}. `{s}` -> `{e}`: {sent}")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(files, total, len(expanded))


if __name__ == "__main__":
    sys.exit(main())
