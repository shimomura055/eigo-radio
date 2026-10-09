# -*- coding: utf-8 -*-
"""P0' D0実測(¥0): casebank_01.json の articles(18記事)の各言語版にD0を適用し、Flag数/記事(固有文数)を実測する。
ラベル(ケース・既知重大文)は読まない・照合しない。読むのは articles の ledger/files パスと記事本文のみ。
出力: results/D0_ARTICLE_SWEEP_01.md と results/d0_article_sweep_01.json
 - rollback(和集合投入対象=gate_only=False) と 全D0(gate_only含む) の2系統で、(unit,sentence,type)件数と固有文数を出す。
"""
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import d0_directional as D0  # noqa: E402
import ledger_restore_01 as LR  # noqa: E402
import run_flagger_01 as R  # noqa: E402

CASEBANK = os.path.join(HERE, "..", "casebank", "casebank_01.json")
OUT_MD = os.path.join(HERE, "results", "D0_ARTICLE_SWEEP_01.md")
OUT_JSON = os.path.join(HERE, "results", "d0_article_sweep_01.json")


def sweep():
    with open(CASEBANK, encoding="utf-8") as f:
        data = json.load(f)
    rows = []
    for a in data["articles"]:
        lp = os.path.join(LR.REPO, a["ledger"])
        facts = LR.parse_ledger_file(lp)
        for ver, info in a["files"].items():
            if not info:
                continue
            with open(os.path.join(LR.REPO, info["path"]), encoding="utf-8") as f:
                sents = R._split_sentences(f.read())
            unit = dict(unit_id="%s/%s/%s" % (a["theme"], a["arm"], ver), mode="article", facts=facts,
                        sentences=[dict(sid="s%d" % (i + 1), text=s, before="", after="") for i, s in enumerate(sents)])
            fl = D0.detect(unit)
            rb = [x for x in fl if not x["gate_only"]]
            by_type = {}
            for x in fl:
                by_type.setdefault(x["type"], set()).add(x["sentence_id"])
            rows.append(dict(unit_id=unit["unit_id"], theme=a["theme"], arm=a["arm"], version=ver,
                             lang="JA" if ver.startswith("JA") else "EN", n_facts=len(facts), n_sentences=len(sents),
                             rollback_flags=len({(x["sentence_id"], x["type"]) for x in rb}),
                             rollback_sentences=len({x["sentence_id"] for x in rb}),
                             all_flags=len({(x["sentence_id"], x["type"]) for x in fl}),
                             all_sentences=len({x["sentence_id"] for x in fl}),
                             sentences_by_type={k: len(v) for k, v in by_type.items()}))
    return rows


def stats(vals):
    return "平均%.1f / 中央値%.1f / 最大%d" % (statistics.mean(vals), statistics.median(vals), max(vals)) if vals else "-"


def to_md(rows):
    lines = ["# D0_ARTICLE_SWEEP_01(P0' D0実測、¥0)", "",
             "- 対象: casebank_01.json の articles 18記事の各言語版(JA_R2 / EN_Adv_b1b / EN_Std_a2)。ラベル・既知重大文は一切参照しない。",
             "- 規則: `d0_directional.detect`(方向語を含む文 × 方向語を含むFactの総当たり、言語をまたぐ)。rollback=和集合投入対象(gate_only=False)、"
             "全D0=gate_only(不在断定・数量・増減/許可)を含む。", "- 数え方: 固有文数=Flagが立った異なる文の数 / (sent,type)=同一文の複数タイプは別件。", "",
             "| 記事 | 版 | 文数 | Fact数 | rollback固有文 | rollback(sent,type) | 全D0固有文 | 全D0(sent,type) |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append("| %s/%s | %s | %d | %d | %d | %d | %d | %d |" % (r["theme"], r["arm"], r["version"], r["n_sentences"], r["n_facts"],
                                                                   r["rollback_sentences"], r["rollback_flags"], r["all_sentences"], r["all_flags"]))
    lines += ["", "## 言語版別の要約(KPI3の判定線: 合格 平均≤5 Flag/記事/言語版、不合格線 >12。上限は『人間に見せる件数』= 和集合に入れるrollback)", ""]
    for lang in ("JA", "EN"):
        sub = [r for r in rows if r["lang"] == lang]
        lines.append("- %s版(n=%d): rollback固有文 %s / 全D0固有文 %s" % (
            lang, len(sub), stats([r["rollback_sentences"] for r in sub]), stats([r["all_sentences"] for r in sub])))
    lines.append("- 全版(n=%d): rollback固有文 %s / 全D0固有文 %s" % (len(rows), stats([r["rollback_sentences"] for r in rows]),
                                                               stats([r["all_sentences"] for r in rows])))
    tot_by_type = {}
    for r in rows:
        for k, v in r["sentences_by_type"].items():
            tot_by_type[k] = tot_by_type.get(k, 0) + v
    lines.append("- タイプ別 固有文数の合計(全%d版): %s" % (len(rows), ", ".join("%s=%d" % kv for kv in sorted(tot_by_type.items()))))
    return "\n".join(lines) + "\n"


def main():
    rows = sweep()
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    md = to_md(rows)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(md)
    print(md)


if __name__ == "__main__":
    main()
