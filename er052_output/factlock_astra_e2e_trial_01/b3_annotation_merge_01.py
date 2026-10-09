# -*- coding: utf-8 -*-
"""B3注記仕様 v2 の二重注記(A・B)統合スクリプト。決定論・LLM不使用・API支出0・手作業禁止。

入力: 元brief, 台帳, 注記者A/Bの注記版md + サイドカー (それぞれ b3_annotation_check_01 で単独PASS済みであること)
出力 (--out-dir): merged_selected_brief_factlock.md / merged_annotation.json / merged_core_numbers.json /
                  resolution_log.json / agreement.json / merged_check_result.json
解決規則 (仕様 v2 §6(e)。人が裁定しない):
  - 分割不一致 -> 事実数の少ない(粗い)方 = 両者の境界の共通部分。
  - ledger_ids: 統合した各事実について A側の和集合 と B側の和集合 の共通部分。空ならSTOP。
  - 数値: 表記は和集合。種類の食い違い -> 中核不可側 (name_embedded > ordinal > year > range/date_time > magnitude)。
    台帳IDの食い違い -> 共通部分 (空ならSTOP)。概念は A・B のラベルと包含/同一主数字の規則で連結成分に統合。
  - 中核/周辺: 統合入力から b3_annotation_check_01.compute_expected で再計算 (A・Bの宣言は使わない)。
  - 長い表記と短い表記の位置ずれ -> 長い表記に統一 (最長一致)。
  - 統合後に b3_annotation_check_01.run を再実行し、FAILなら STOP (統合版を採用しない)。
一致率の事前登録線 (推定値): 分割一致率 < 0.8 または 中核Jaccard < 0.67 なら「規則を機械的に適用できていない」と報告。
CLI: --brief --ledger --ann-a --side-a --ann-b --side-b --out-dir [--spec]
終了コード: 統合版PASS=0 / STOP=1
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import b3_annotation_check_01 as chk  # noqa: E402

SPLIT_AGREE_MIN = 0.8
CORE_JACCARD_MIN = 0.67
BULLET_PREFIX_RE = re.compile(r"^\s*(?:-|・)\s*")


class Stop(Exception):
    pass


def _lines(prepped, rng):
    s, e = rng
    out, pos = [], s
    for ln in prepped[s:e].split("\n"):
        out.append((pos, pos + len(ln), ln))
        pos += len(ln) + 1
    return out


def _side_facts(brief_prepped, rng, annotated, sidecar, label):
    """注記版から (項目ごとの事実境界, ledger_ids) を取り出す。座標は prep(brief) 上。"""
    r = chk.align(brief_prepped, chk.prep(annotated), rng)
    if not r["ok"]:
        raise Stop(f"{label}: 位置合わせ失敗 {r['reason']}")
    lines = _lines(brief_prepped, rng)
    by_n = {f["n"]: sorted(f.get("ledger_ids", [])) for f in sidecar.get("facts", [])}
    tags = [(off, int(chk.SIMPLE_TAG_RE.fullmatch(t).group(1))) for off, k, t in r["events"]
            if k == "tag" and rng[0] <= off <= rng[1]]
    items = {}
    for off, n in tags:
        for li, (ls, le, ln) in enumerate(lines):
            if ls <= off <= le:
                items.setdefault(li, []).append((off, n))
                break
    res = {}
    for li, lst in items.items():
        ls, le, ln = lines[li]
        res[li] = {"bounds": [o for o, _ in lst], "ids": [by_n.get(n, []) for _, n in lst],
                   "n": [n for _, n in lst], "line": (ls, le)}
    return res


def _default_first(ls, ln):
    m = BULLET_PREFIX_RE.match(ln)
    return ls + (m.end() if m else 0)


def _fact_ids_for_range(side_item, lo, hi):
    """merged fact [lo,hi) と重なる側の事実の ledger_ids の和集合"""
    out = set()
    bounds = side_item["bounds"]
    for k, b in enumerate(bounds):
        nxt = bounds[k + 1] if k + 1 < len(bounds) else side_item["line"][1] + 1
        if b < hi and nxt > lo:
            out |= set(side_item["ids"][k])
    return out


def _union_find(keys):
    parent = {k: k for k in keys}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra
    return find, union


def _merge_numbers(itemsA, itemsB, ledger, log):
    fs = chk.fw
    surf = {}
    for side, items in (("A", itemsA), ("B", itemsB)):
        for it in items:
            surf.setdefault(fs(it["surface"]), {})[side] = it
    keys = list(surf)
    find, union = _union_find(keys)
    for side, items in (("A", itemsA), ("B", itemsB)):
        first = {}
        for it in items:
            k = fs(it["surface"])
            if it["concept"] in first:
                union(first[it["concept"]], k)
            else:
                first[it["concept"]] = k
    merged = {}
    for k, d in surf.items():
        a, b = d.get("A"), d.get("B")
        kinds = [x["kind"] for x in (a, b) if x]
        kind = sorted(kinds, key=lambda t: chk.NUM_ORDER.get(t, 9))[0]
        if len(set(kinds)) > 1:
            log.append({"rule": "kind食い違い->中核不可側", "surface": (a or b)["surface"], "A": a["kind"], "B": b["kind"], "chosen": kind})
        if a and b:
            ia, ib = set(a["ledger_ids"]), set(b["ledger_ids"])
            ids = ia & ib
            if not ids:
                raise Stop(f"数値 '{a['surface']}': 台帳IDの共通部分が空 A={sorted(ia)} B={sorted(ib)} (Fableへ)")
            if ia != ib:
                log.append({"rule": "数値ledger_ids食い違い->共通部分", "surface": a["surface"], "A": sorted(ia), "B": sorted(ib), "chosen": sorted(ids)})
        else:
            only = a or b
            ids = set(only["ledger_ids"])
            log.append({"rule": "片側のみの表記を採用(和集合)", "surface": only["surface"], "side": "A" if a else "B"})
        base = (a or b)
        merged[k] = {"surface": base["surface"], "kind": kind, "ledger_ids": sorted(ids), "role": base.get("role", "")}
    # 包含・同一主数字による連結 (check_concept_bundling と同じ条件)
    ks = list(merged)
    for x in range(len(ks)):
        for y in range(x + 1, len(ks)):
            mx, my = merged[ks[x]], merged[ks[y]]
            if {mx["kind"], my["kind"]} & {"year", "ordinal", "name_embedded"}:
                continue
            if not (set(mx["ledger_ids"]) & set(my["ledger_ids"])):
                continue
            if ks[x] in ks[y] or ks[y] in ks[x] or (
                    mx["kind"] in chk.QUANTITY_KINDS and my["kind"] in chk.QUANTITY_KINDS and
                    chk.main_numbers(mx["surface"], mx["kind"]) == chk.main_numbers(my["surface"], my["kind"])):
                union(ks[x], ks[y])
    return merged, find


def _scan_marks(text, surfaces):
    """最長一致で表記の出現位置を列挙 (台帳IDはマスク)。戻り [(start, end, surface_fw)]"""
    masked = chk.ID_RE.sub(lambda m: "\0" * len(m.group(0)), chk.fw(text))
    alts = sorted({chk.fw(s) for s in surfaces}, key=len, reverse=True)
    if not alts:
        return []
    pat = re.compile("(" + "|".join(re.escape(a) for a in alts) + ")")
    return [(m.start(), m.end(), m.group(1)) for m in pat.finditer(masked)]


def agreement_metrics(brief_prepped, rng, sideA, sideB, itemsA, itemsB, find, merged_ids_by_concept):
    items = sorted(set(sideA) | set(sideB))
    agree = 0
    detail = []
    for li in items:
        a, b = sideA.get(li), sideB.get(li)
        ok = bool(a and b and a["bounds"] == b["bounds"] and [sorted(x) for x in a["ids"]] == [sorted(x) for x in b["ids"]])
        agree += 1 if ok else 0
        detail.append({"item_line": li, "agree": ok, "A_facts": len(a["bounds"]) if a else 0, "B_facts": len(b["bounds"]) if b else 0})
    split_rate = agree / len(items) if items else 1.0

    def core_set(its):
        return {find(chk.fw(i["surface"])) for i in its if i["class"] == "core"}
    ca, cb = core_set(itemsA), core_set(itemsB)
    union = ca | cb
    jac = (len(ca & cb) / len(union)) if union else None
    ca_s = {chk.fw(i["surface"]): i["class"] for i in itemsA}
    cb_s = {chk.fw(i["surface"]): i["class"] for i in itemsB}
    allk = set(ca_s) | set(cb_s)
    cls_agree = sum(1 for k in allk if ca_s.get(k) == cb_s.get(k))
    cls_rate = cls_agree / len(allk) if allk else None
    flags = []
    if split_rate < SPLIT_AGREE_MIN:
        flags.append(f"分割一致率 {split_rate:.2f} < {SPLIT_AGREE_MIN} : 規則を機械的に適用できていない")
    if jac is not None and jac < CORE_JACCARD_MIN:
        flags.append(f"中核Jaccard {jac:.2f} < {CORE_JACCARD_MIN} : 規則を機械的に適用できていない")
    return {"split_agreement_rate": split_rate, "split_items": len(items), "split_item_detail": detail,
            "core_jaccard": jac, "core_union_size": len(union), "core_zero_article": not union,
            "classification_agreement_rate": cls_rate, "classification_union_size": len(allk),
            "pre_registered_lines": {"split_min": SPLIT_AGREE_MIN, "core_jaccard_min": CORE_JACCARD_MIN},
            "flags": flags}


def aggregate(results):
    """複数記事の一致率の全体値。数値0件の記事は中核Jaccardの集計に含めず件数を併記する。"""
    sp = [r["split_agreement_rate"] for r in results]
    jc = [r["core_jaccard"] for r in results if r["core_jaccard"] is not None]
    return {"articles": len(results), "split_agreement_mean": sum(sp) / len(sp) if sp else None,
            "core_jaccard_mean_over_nonzero": (sum(jc) / len(jc)) if jc else None,
            "core_jaccard_articles": len(jc), "core_zero_articles": sum(1 for r in results if r["core_zero_article"])}


def render(b, lines, merged_facts, items):
    """prep済み原文 b に【事実N】・数値印・定義済みレイアウト挿入だけを加えた注記版を決定論で作る。
    merged_facts: [(start, end, item_line, ledger_ids, k)]  items: 分類(class)確定済みの数値表記"""
    ins = {}   # offset -> [(order, text)]
    cls_of = {chk.fw(i["surface"]): i["class"] for i in items}
    for s_, e_, sf in _scan_marks(b, [i["surface"] for i in items]):
        ins.setdefault(e_, []).append((0, chk.MARK_OF[cls_of[sf]]))
    for n, (bo, hi, li, ids, k) in enumerate(merged_facts, 1):
        ls, le, ln = lines[li]
        if k == 0:
            pre = "" if BULLET_PREFIX_RE.match(ln) else "- "
        else:
            pre = "\n- "
        ins.setdefault(bo, []).append((1, pre + f"【事実{n}】"))
    out, last = [], 0
    for off in sorted(ins):
        out.append(b[last:off])
        out.extend(t for _, t in sorted(ins[off], key=lambda x: x[0]))
        last = off
    out.append(b[last:])
    return "".join(out)


def merge(brief, ledger_text, annA, sideA_json, annB, sideB_json, spec_sha256=None, brief_sha256=None):
    log = []
    ledger = chk.parse_ledger(ledger_text)
    schema = chk.ledger_schema(ledger)
    for label, ann, sc in (("A", annA, sideA_json), ("B", annB, sideB_json)):
        r = chk.run(brief, ann, ledger_text, sc, spec_sha256=spec_sha256, brief_sha256=brief_sha256)
        if r["verdict"] != "PASS":
            raise Stop(f"注記者{label}の単独検査がFAIL: " + json.dumps(
                {k: v.get("problems") for k, v in r.items() if isinstance(v, dict) and v.get("problems")}, ensure_ascii=False))
    for key in ("spec_sha256", "brief_sha256"):
        if sideA_json.get(key) != sideB_json.get(key):
            raise Stop(f"A・Bで {key} が異なる")
    b = chk.prep(brief)
    rng = chk.facts_section_range(b)
    if rng is None:
        raise Stop("Selected Facts節が無い")
    lines = _lines(b, rng)
    fa = _side_facts(b, rng, annA, sideA_json, "A")
    fb = _side_facts(b, rng, annB, sideB_json, "B")
    # ---------------- 事実の統合
    merged_facts = []   # (start, end, item_line, ids)
    for li in sorted(set(fa) | set(fb)):
        if li not in fa or li not in fb:
            raise Stop(f"項目(行{li})の事実化が片側のみ (A={li in fa}, B={li in fb}): Fableへ")
        ls, le, ln = lines[li]
        d0 = _default_first(ls, ln)
        if fa[li]["bounds"][0] != d0 or fb[li]["bounds"][0] != d0:
            raise Stop(f"項目(行{li})の最初の事実の位置が既定(行頭/箇条書き直後)と異なる")
        inner = sorted(set(fa[li]["bounds"][1:]) & set(fb[li]["bounds"][1:]))
        bounds = [d0] + inner
        if fa[li]["bounds"] != fb[li]["bounds"]:
            log.append({"rule": "分割不一致->共通の境界(粗い方)", "item_line": li, "A": fa[li]["bounds"], "B": fb[li]["bounds"], "chosen": bounds})
        for k, bo in enumerate(bounds):
            hi = bounds[k + 1] if k + 1 < len(bounds) else le + 1
            ia, ib = _fact_ids_for_range(fa[li], bo, hi), _fact_ids_for_range(fb[li], bo, hi)
            ids = ia & ib
            if not ids:
                raise Stop(f"項目(行{li})の事実{k + 1}: ledger_idsの共通部分が空 A={sorted(ia)} B={sorted(ib)} (Fableへ)")
            if ia != ib:
                log.append({"rule": "事実ledger_ids食い違い->共通部分", "item_line": li, "A": sorted(ia), "B": sorted(ib), "chosen": sorted(ids)})
            merged_facts.append((bo, hi, li, sorted(ids), k))
    for i, (bo, hi, li, ids, k) in enumerate(merged_facts):
        if k > 0 and b[bo - 1] != "。":
            raise Stop(f"統合境界の直前が 。 でない (位置{bo})")
    # ---------------- 数値の統合
    itemsA, itemsB = chk._norm_items(sideA_json.get("numbers", [])), chk._norm_items(sideB_json.get("numbers", []))
    merged_nums, find = _merge_numbers(itemsA, itemsB, ledger, log)
    # 長い表記への統一: 最長一致で一度も採用されない表記は除外
    occ = _scan_marks(b, [m["surface"] for m in merged_nums.values()])
    used = {s for _, _, s in occ}
    for k in list(merged_nums):
        if k not in used:
            log.append({"rule": "位置ずれ->長い表記に統一(短い表記を除外)", "surface": merged_nums[k]["surface"]})
            del merged_nums[k]
    roots = {}
    ordered = sorted(merged_nums, key=lambda s: b.find(s) if b.find(s) >= 0 else 10 ** 9)
    ordered_all = [k for k in ordered]
    for k in ordered_all:
        roots.setdefault(find(k), f"M{len(roots) + 1}")
    items = []
    for k in ordered_all:
        m = merged_nums[k]
        items.append({"surface": m["surface"], "kind": m["kind"], "class": None, "concept": roots[find(k)],
                      "ledger_ids": m["ledger_ids"], "role": m["role"]})
    # 先に仮の注記版(分類は後)を作らず、プレーン本文で再計算する
    story, _ = chk.sections(b)
    exp = chk.compute_expected(items, ledger, schema, b, story)
    for it in items:
        it["class"] = exp["concepts"][it["concept"]]["expected_class"]
    log.append({"rule": "中核/周辺は統合入力から再計算", "core_cap": exp["core_cap"], "expected_core": exp["expected_core"],
                "cap_dropped": exp["cap_dropped"]})
    merged_md = render(b, lines, merged_facts, items)
    merged_side = {"slug": sideA_json.get("slug", ""), "annotator": "MERGED", "spec_sha256": sideA_json.get("spec_sha256"),
                   "brief_sha256": sideA_json.get("brief_sha256"),
                   "facts": [{"n": n, "ledger_ids": ids} for n, (_, _, _, ids, _) in enumerate(merged_facts, 1)],
                   "numbers": items,
                   "unmapped_claims": _dedupe(list(sideA_json.get("unmapped_claims", [])) + list(sideB_json.get("unmapped_claims", []))),
                   "annotation_notes": [dict(x, annotator="A") for x in sideA_json.get("annotation_notes", [])] +
                                       [dict(x, annotator="B") for x in sideB_json.get("annotation_notes", [])]}
    final = chk.run(brief, merged_md, ledger_text, merged_side, spec_sha256=spec_sha256, brief_sha256=brief_sha256)
    agree = agreement_metrics(b, rng, fa, fb, itemsA, itemsB, find, None)
    return {"status": "PASS" if final["verdict"] == "PASS" else "STOP", "merged_md": merged_md, "merged_sidecar": merged_side,
            "resolution_log": log, "agreement": agree, "check_result": final,
            "core_numbers": chk.build_core_json(merged_side) if final["verdict"] == "PASS" else None}


OUT_MD_RE = re.compile(r"=== ANNOTATED_BRIEF_BEGIN ===\n(.*?)\n=== ANNOTATED_BRIEF_END ===", re.S)
OUT_JSON_RE = re.compile(r"=== SIDECAR_JSON_BEGIN ===\n(.*?)\n=== SIDECAR_JSON_END ===", re.S)


def extract_output(text):
    """注記者の返答本文から (注記版md, サイドカーdict) を取り出す。STOP返答は ('STOP', 理由)。形式不正は Stop。"""
    t = chk.norm_nl(text)
    if "=== STOP ===" in t and not OUT_MD_RE.search(t):
        return "STOP", t.split("=== STOP ===", 1)[1].strip()
    m1, m2 = OUT_MD_RE.search(t), OUT_JSON_RE.search(t)
    if not (m1 and m2):
        raise Stop("注記者の返答が所定の形式(ANNOTATED_BRIEF / SIDECAR_JSON の区切り)でない")
    try:
        side = json.loads(m2.group(1))
    except ValueError as e:
        raise Stop(f"サイドカーJSONが不正: {e}")
    return m1.group(1).rstrip("\n") + "\n", side  # 委任_09 P4


def build_delegation(template, annotator, slug, spec_text, brief_text, ledger_text, spec_sha, brief_sha):
    """固定テンプレートの置換欄だけを埋める (記事ごとの補足文は入れない)。"""
    vals = {"ANNOTATOR": annotator, "SLUG": slug, "SPEC_SHA256": spec_sha, "BRIEF_SHA256": brief_sha,
            "SPEC_TEXT": spec_text, "BRIEF_TEXT": brief_text, "LEDGER_TEXT": ledger_text}
    out = template
    for k, v in vals.items():
        out = out.replace("{{" + k + "}}", v)
    if re.search(r"\{\{[A-Z_0-9]+\}\}", out):
        raise Stop("テンプレートに未置換の欄が残っている")
    return out


def _dedupe(lst):
    seen, out = set(), []
    for x in lst:
        k = json.dumps(x, ensure_ascii=False, sort_keys=True)
        if k not in seen:
            seen.add(k)
            out.append(x)
    return out


def main_aux(argv):
    """補助CLI。extract: 注記者の返答本文を注記版md+サイドカーとして保存 / fill: 固定テンプレートから依頼文を生成。"""
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("extract")
    e.add_argument("--reply", required=True)
    e.add_argument("--out-md", required=True)
    e.add_argument("--out-sidecar", required=True)
    f = sub.add_parser("fill")
    for k in ("--template", "--annotator", "--slug", "--spec", "--brief", "--ledger", "--out"):
        f.add_argument(k, required=True)
    a = ap.parse_args(argv)
    if a.cmd == "extract":
        md, side = extract_output(open(a.reply, encoding="utf-8", newline="").read())
        if md == "STOP":
            print("STOP:", side)
            return 1
        open(a.out_md, "w", encoding="utf-8", newline="").write(md)
        json.dump(side, open(a.out_sidecar, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        return 0
    rb = lambda p: open(p, "rb").read()  # noqa: E731
    txt = lambda p: open(p, encoding="utf-8", newline="").read()  # noqa: E731
    out = build_delegation(txt(a.template), a.annotator, a.slug, txt(a.spec), txt(a.brief), txt(a.ledger),
                           chk.sha256_bytes(rb(a.spec)), chk.sha256_bytes(rb(a.brief)))
    open(a.out, "w", encoding="utf-8", newline="").write(out)
    print(chk.sha256_bytes(out.encode("utf-8")))
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] in ("extract", "fill"):
        return main_aux(argv)
    ap = argparse.ArgumentParser()
    for k in ("--brief", "--ledger", "--ann-a", "--side-a", "--ann-b", "--side-b", "--out-dir"):
        ap.add_argument(k, required=True)
    ap.add_argument("--spec")
    a = ap.parse_args(argv)

    def rd(p):
        return open(p, encoding="utf-8", newline="").read()
    spec_sha = chk.sha256_bytes(open(a.spec, "rb").read()) if a.spec else None
    brief_sha = chk.sha256_bytes(open(a.brief, "rb").read())
    os.makedirs(a.out_dir, exist_ok=True)
    try:
        r = merge(rd(a.brief), rd(a.ledger), rd(a.ann_a), json.loads(rd(a.side_a)), rd(a.ann_b), json.loads(rd(a.side_b)),
                  spec_sha, brief_sha)
    except Stop as e:
        json.dump({"status": "STOP", "reason": str(e)}, open(os.path.join(a.out_dir, "merge_stop.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("STOP:", e)
        return 1

    def w(name, obj, text=False):
        open(os.path.join(a.out_dir, name), "w", encoding="utf-8", newline="").write(obj if text else json.dumps(obj, ensure_ascii=False, indent=2))
    w("merged_selected_brief_factlock.md", r["merged_md"], True)
    w("merged_annotation.json", r["merged_sidecar"])
    w("resolution_log.json", r["resolution_log"])
    w("agreement.json", r["agreement"])
    w("merged_check_result.json", r["check_result"])
    if r["core_numbers"]:
        w("merged_core_numbers.json", r["core_numbers"])
    print(json.dumps({"status": r["status"], "agreement_flags": r["agreement"]["flags"]}, ensure_ascii=False))
    return 0 if r["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
