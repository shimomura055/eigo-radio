# -*- coding: utf-8 -*-
"""旧4テーマ(META/ホルムズ/宇宙兵器/ミニバッグ)の元briefに B3注記仕様 v2 の規則をスクリプトで適用し、
過去の人手注記と比較する (注記の実施ではなく規則の検証。API支出0、LLM不使用)。

- 事実分割: 仕様 v2 §2 の S1/S2 を近似する決定論ヒューリスティック (文を台帳記録へ文字bigram重なりで対応付け、
  限定文[ただし/これは/…ない 等]は直前の事実へ付ける、明示台帳IDのある項目は割らない)。注記者の判断の代替ではなく、
  「規則を機械的に当てるとどうなるか」の目安。
- 数値: 表記・種類・概念・台帳IDは旧4について本スクリプト内に固定した表 (注記者入力に相当)。中核/周辺は
  b3_annotation_check_01.compute_expected が計算する。
- 出力: B3_ANNOTATION_SPEC_v2_OLD4_EXPECTED.md (隔離ファイル。注記者には見せない) と old4_expected_eval_01.json
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import b3_annotation_check_01 as chk  # noqa: E402
import b3_annotation_merge_01 as mrg  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
FW = os.path.join(ROOT, "er052_output", "factlock_writer_trial_01")
B3 = os.path.join(ROOT, "er052_output", "open233_b3_trial_01", "runs")


def N(surface, kind, concept, ids):
    return {"surface": surface, "kind": kind, "concept": concept, "ledger_ids": ids, "class": None}


THEMES = {
    "meta": {
        "brief": f"{B3}/meta/nb/V0/b2/storyline_b3/selected_brief.md",
        "ledger": f"{FW}/runs/meta/control/b2__factlock__r1/research_ledger/verified_fact_ledger.txt",
        "past": f"{FW}/briefs/meta/b2/selected_brief_factlock.md",
        "past_ids": None,
        "numbers": [],
    },
    "hormuz": {
        "brief": f"{B3}/hormuz/nb/V0/b2/storyline_b3/selected_brief.md",
        "ledger": f"{FW}/runs/hormuz/control/b2__factlock__r1/research_ledger/verified_fact_ledger.txt",
        "past": f"{FW}/briefs/hormuz/b2/selected_brief_factlock.md",
        "past_ids": None,
        "numbers": [
            N("20％", "magnitude", "Q_rate", ["HF-002", "HF-007"]),
            N("約2.6％", "magnitude", "Q_brent_pct", ["HF-009"]),
            N("1バレル85ドル", "magnitude", "Q_brent_price", ["HF-009"]),
            N("7月13日午前10時16分", "date_time", "D_0713", ["HF-002"]),
            N("7月13日", "date_time", "D_0713", ["HF-002"]),
            N("7月14日午前11時4分", "date_time", "D_0714", ["HF-007"]),
            N("14日", "date_time", "D_0714", ["HF-007"]),
        ],
    },
    "space_weapons": {
        "brief": f"{B3}/space_weapons/nb/V0/b2/storyline_b3/selected_brief.md",
        "ledger": f"{FW}/runs/space_weapons/control/b2__factlock__r1/research_ledger/verified_fact_ledger.txt",
        "past": f"{FW}/briefs/space_weapons/b2/selected_brief_factlock.md",
        "past_ids": None,
        "numbers": [
            N("2026年9月14日", "date_time", "D_0914", ["F-001"]),
            N("2026年9月", "date_time", "D_0914", ["F-001"]),
            N("2021年11月15日", "date_time", "D_2021", ["F-003"]),
            N("1,500個超", "magnitude", "Q_debris", ["F-003"]),
            N("COSMOS 1408", "name_embedded", "N_cosmos", ["F-003"]),
            N("第4条", "ordinal", "N_art4", ["F-016"]),
        ],
    },
    "small_bag": {
        "brief": f"{ROOT}/er052_output/gpt6_wiring_e2e_01/run_02/storyline_b3/selected_brief.md",
        "ledger": f"{ROOT}/er052_output/gpt6_wiring_e2e_01/run_02/research_ledger/verified_fact_ledger.txt",
        "past": f"{FW}/astra_revise_matrix_02/inputs/small_bag/selected_brief_factlock.md",
        "past_ids": None,
        "numbers": [
            N("2026年", "year", "Y_2026", ["MB-01"]),
            N("2026年9月", "date_time", "D_ELLE", ["MB-01"]),
            N("Fall 2026", "name_embedded", "N_fall", ["MB-01", "MB-05"]),
            N("2026年10月", "date_time", "D_WWW", ["MB-06"]),
        ],
    },
}

QUAL_START = ("ただし", "これは", "これも", "したがって", "なお", "つまり")
QUAL_END = ("ない。", "しない。", "ではない。", "書かない。", "意味しない。", "扱わない。", "指さない。", "できない。", "されていない。")


def rd(p):
    with open(p, encoding="utf-8", newline="") as f:
        return f.read()


def bigrams(s):
    s = re.sub(r"\s+", "", s)
    return {s[i:i + 2] for i in range(len(s) - 1)}


def best_ledger(sentence, ledger):
    bs = bigrams(sentence)
    best, score = None, -1.0
    for rid, r in ledger.items():
        sc = len(bs & bigrams(r["full"])) / (len(bs) or 1)
        if sc > score:
            best, score = rid, sc
    return best, score


def propose_facts(b, rng, ledger):
    """prep済み brief の Selected Facts から (行, [(開始offset, ledger_ids, 根拠)]) を提案。"""
    out = []
    lines = mrg._lines(b, rng)
    for li, (ls, le, ln) in enumerate(lines):
        body = ln.strip()
        if not body or body.startswith("Storyline") or body.startswith("素材"):
            continue
        m0 = mrg.BULLET_PREFIX_RE.match(ln)
        start0 = ls + (m0.end() if m0 else 0)
        text = ln[(m0.end() if m0 else 0):]
        # 文に分割 (offset付き)
        sents, pos = [], 0
        for m in re.finditer(r"[^。]*。?", text):
            if m.group(0) == "":
                continue
            sents.append((start0 + m.start(), m.group(0)))
        explicit = [i for i in chk.ID_RE.findall(text) if i in ledger]
        facts = []
        if explicit:
            facts.append((start0, sorted(set(explicit[:1])), "明示台帳ID(割らない)"))
        else:
            cur = None
            for off, s in sents:
                st = s.strip()
                qual = st.startswith(QUAL_START) or st.endswith(QUAL_END)
                rid, sc = best_ledger(st, ledger)
                if not facts:
                    facts.append((off, [rid], f"対応 {rid} ({sc:.2f})"))
                    cur = rid
                    continue
                if qual:
                    continue
                if rid != cur and len(facts) < 3:
                    facts.append((off, [rid], f"対応 {rid} ({sc:.2f})"))
                    cur = rid
        out.append((li, facts))
    return out, lines


def main():
    results, md = {}, []
    md.append("# B3_ANNOTATION_SPEC_v2_OLD4_EXPECTED(旧4テーマへの v2 規則のスクリプト適用の実測、隔離ファイル)\n")
    md.append("**注記者には見せない**(過去注記との比較を含むため)。本書は注記の実施ではなく規則の検証。生成: `b3_old4_expected_eval_01.py`(¥0、LLM不使用)。\n")
    md.append("読み方と限界: (1)数値の表記・種類・概念・台帳IDは本スクリプト内の固定表(注記者の入力に相当、人手で作成)。中核/周辺は `compute_expected` が計算。"
              "(2)事実分割は文の文字bigram重なりによる近似(S1/S2の厳密適用ではない)。限定文はヒューリスティックで直前の事実に付ける。"
              "(3)よって「v2規則を機械的に当てた目安」であり、注記者(AI worker)の実際の一致を示すものではない。"
              "(4)過去注記は人手指定で規則文書がなく、過去との一致は規則の正しさの証明ではない(過去注記に合わせて規則を設計した面がある=循環の危険)。\n")
    for slug, t in THEMES.items():
        brief, ledger_text, past = rd(t["brief"]), rd(t["ledger"]), rd(t["past"])
        ledger = chk.parse_ledger(ledger_text)
        schema = chk.ledger_schema(ledger)
        b = chk.prep(brief)
        rng = chk.facts_section_range(b)
        plan, lines = propose_facts(b, rng, ledger)
        # --- 過去注記の事実分割
        pr = mrg._side_facts(b, rng, past, {"facts": []}, "past")
        # --- 数値: 中核/周辺を計算
        items = [dict(x) for x in t["numbers"]]
        story, _ = chk.sections(b)
        exp = chk.compute_expected(items, ledger, schema, b, story)
        for it in items:
            it["class"] = exp["concepts"][it["concept"]]["expected_class"]
        # 過去の分類 (過去注記の印)
        pal = chk.align(b, chk.prep(past), rng)
        mark_at = {off: txt for off, k, txt in pal["events"] if k == "mark"}
        past_cls = {}
        for s_, e_, sf in mrg._scan_marks(b, [i["surface"] for i in items]):
            past_cls.setdefault(sf, set()).add(mark_at.get(e_, "印なし"))
        rows = []
        mism = 0
        for it in items:
            pc = sorted(past_cls.get(chk.fw(it["surface"]), {"出現なし"}))
            pcs = "/".join(pc)
            exp_mark = chk.MARK_OF[it["class"]]
            same = pc == [exp_mark]
            mism += 0 if same else 1
            rows.append({"surface": it["surface"], "kind": it["kind"], "concept": it["concept"], "v2_class": it["class"],
                         "past_mark": pcs, "same": same,
                         "eligible": exp["concepts"][it["concept"]]["eligible"]})
        # --- 事実分割の比較
        facts_rows = []
        facts_equal = 0
        merged_facts = []
        for li, facts in plan:
            ls, le, ln = lines[li]
            past_n = len(pr.get(li, {}).get("bounds", []))
            eq = len(facts) == past_n
            facts_equal += 1 if eq else 0
            facts_rows.append({"item_line": li, "v2_facts": len(facts), "past_facts": past_n, "same_count": eq,
                               "v2_ids": [f[1] for f in facts], "basis": [f[2] for f in facts]})
            for k, (off, ids, _) in enumerate(facts):
                merged_facts.append((off, facts[k + 1][0] if k + 1 < len(facts) else le + 1, li, ids, k))
        # --- 描画して v2 検査にかけてPASSを実測 (スクリプトが作った注記版が自己検査を通るか)
        md_text = mrg.render(b, lines, merged_facts, items)
        side = {"annotator": "A", "facts": [{"n": n, "ledger_ids": f[3]} for n, f in enumerate(merged_facts, 1)], "numbers": items}
        chk_res = chk.run(brief, md_text, ledger_text, side)
        results[slug] = {
            "ledger_schema_warnings": schema["warnings"], "countable_concepts": exp["countable_concepts"],
            "core_cap": exp["core_cap"], "v2_core": exp["expected_core"], "cap_dropped": exp["cap_dropped"],
            "numbers": rows, "number_mismatches": mism, "facts": facts_rows,
            "fact_count_equal_items": facts_equal, "fact_items": len(plan),
            "v2_total_facts": len(merged_facts), "past_total_facts": sum(len(v["bounds"]) for v in pr.values()),
            "rendered_check_verdict": chk_res["verdict"],
            "rendered_check_problems": {k: v.get("problems") for k, v in chk_res.items() if isinstance(v, dict) and v.get("problems")},
            "rendered_md": md_text,
        }
        md.append(f"## {slug}\n")
        md.append(f"- 概念数 n={exp['countable_concepts']}、上限={exp['core_cap']}、上限で外れた適格概念={len(exp['cap_dropped'])}({exp['cap_dropped']})。"
                  f"台帳スキーマ警告: {schema['warnings'] or 'なし'}")
        md.append(f"- v2 規則を当てた注記版の自己検査(b3_annotation_check_01): **{chk_res['verdict']}**"
                  f"(事実{len(merged_facts)}件、過去注記は{results[slug]['past_total_facts']}件)")
        md.append("\n| 表記 | 種類 | 概念 | 適格 | v2計算結果 | 過去の人手注記 | 一致 |\n|---|---|---|---|---|---|---|")
        for r in rows:
            md.append(f"| {r['surface']} | {r['kind']} | {r['concept']} | {','.join(r['eligible']) or '-'} | "
                      f"{chk.MARK_OF[r['v2_class']]} | {r['past_mark']} | {'一致' if r['same'] else '**不一致**'} |")
        if not rows:
            md.append("| (数値0件) | | | | | | 一致 |")
        md.append("\n| 項目(行) | v2事実数 | 過去事実数 | 台帳ID(v2) | 根拠 |\n|---|---|---|---|---|")
        for f in facts_rows:
            md.append(f"| {f['item_line']} | {f['v2_facts']} | {f['past_facts']} | {f['v2_ids']} | {'; '.join(f['basis'])} |")
        md.append("")
    tot_num = sum(len(r["numbers"]) for r in results.values())
    tot_mis = sum(r["number_mismatches"] for r in results.values())
    md.append("## 集計\n")
    md.append(f"- 数値表記 {tot_num} 件中、過去の人手注記と分類が異なるもの {tot_mis} 件。")
    md.append(f"- 事実数が過去注記と同じ項目: " + ", ".join(f"{k} {v['fact_count_equal_items']}/{v['fact_items']}" for k, v in results.items()))
    out_md = os.path.join(HERE, "B3_ANNOTATION_SPEC_v2_OLD4_EXPECTED.md")
    with open(out_md, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(md) + "\n")
    with open(os.path.join(HERE, "old4_expected_eval_01.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
