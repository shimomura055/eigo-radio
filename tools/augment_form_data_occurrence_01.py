# -*- coding: utf-8 -*-
"""既存の選定フォームdata(1記事x1水準)へ出現回数(occ-v1: 各entryの`occurrence`+記事の`occurrence_meta`)だけを足した、**別stemのdata**を出力する(API 0・入力は変更しない)。
SELECTION-UI-OCCURRENCE-COUNT-01 委任_02。通常のexport(`export_form_data_01.py`)は既定で回数を焼き込むため、新規記事ではこのtoolは不要。
本toolは「既にexport済みのdataへ、export再実行なしで回数を足したい」場合(出現回数表示のテストbatch等)に使う。
公開済みbatchが参照するdata fileは上書きしない(M4): --out が公開済みbatchの参照stemで、内容が異なる場合は rc=5 で拒否する(既定は別stemへ)。

実行: .venv\\Scripts\\python.exe tools\\augment_form_data_occurrence_01.py --data user_test/selection_form_v3/data/<stem>.json --out user_test/selection_form_v3/data/<new stem>.json
        [--cand-root <dir>]   (候補doc・run dir[parts.json等]を探す追加root。cwdが先。既定=cwdのみ)
"""
import argparse
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EXPORTER = os.path.join(ROOT, "docs", "research", "KP-GATE-DROP-BACKFILL-PRODUCTION-01", "tools", "export_form_data_01.py")


def _load_exporter():
    sys.path.insert(0, ROOT)
    spec = importlib.util.spec_from_file_location("export_form_data_01_aug", EXPORTER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cand-root", action="append", default=[])
    ap.add_argument("--slug", default=None, help="出力dataのslug(articles.jsonの状態キー slug__level は一意でなければならないため、同じ記事を別stemで載せるときは別slugにする)")
    ap.add_argument("--name-suffix", default="", help="出力dataの表示名へ付ける接尾辞(テストbatch識別用)")
    a = ap.parse_args(argv)
    x = _load_exporter()
    with open(a.data, encoding="utf-8") as f:
        data = json.load(f)
    cp = data.get("source_kp_candidates_path")
    if not cp:
        print(json.dumps({"status": "NO_SOURCE_PATH", "data": a.data}, ensure_ascii=False), file=sys.stderr)
        return 3
    roots = [os.getcwd()] + a.cand_root
    cand_doc = None
    for r in roots:
        p = os.path.join(r, cp)
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                cand_doc = json.load(f)
            break
    out = x.augment_form_data(data, cand_doc, cand_path=cp, roots=roots)
    if a.slug:
        out["slug"] = a.slug
    if a.name_suffix:
        out["name"] = out["name"] + a.name_suffix
    text = json.dumps(out, ensure_ascii=False, indent=1)
    conflict = x.published_reference_conflict(a.out, text)
    if conflict:
        print(json.dumps({"status": "REFUSED_PUBLISHED_REFERENCE", "out": a.out, "conflicts": conflict}, ensure_ascii=False), file=sys.stderr)
        return 5
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(text)
    om = out["occurrence_meta"]
    sc = om.get("selfcheck") or {}
    print(json.dumps({"out": a.out, "status": "UNAVAILABLE" if om.get("error") else "OK", "unavailable": om.get("unavailable"), "selfcheck_checked": sc.get("checked"),
                      "selfcheck_mismatches": len(sc.get("mismatches") or []), "zero_candidates": len(om.get("zero_candidates") or []), "issues": om.get("issues") or []}, ensure_ascii=False))
    for i in om.get("issues") or []:
        print("[OCCURRENCE][WARN] " + i["code"] + ": " + i["message"], file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
