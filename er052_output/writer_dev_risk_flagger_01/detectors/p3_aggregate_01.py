# -*- coding: utf-8 -*-
"""委任_03 P3(記事モード、調整用)集計。ラベルを読むのは既知重大文の特定(casebank_01.json cases[*].sentence)のみ。
C_main = D0rollback ∪ D2rank(上位3件強制列挙)。副構成 D1v2 = D1full(D0ゲート) + 因果創作。
出力: results/P3_RESULT_01.md / P3_RESULT_01.json / P3_FLAGS_FOR_HUMAN_01.json (確認質問つきFlag一覧)
P3ゲート(事前登録): KPI3平均<=5 かつ 既知重大元記事(dev側)でのRecall@top3 >= 50% -> P4へ。"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import aggregate_flagger_01 as AG  # noqa: E402
import p3_run_01 as PR  # noqa: E402

RES = os.path.join(HERE, "results")
CB = os.path.join(HERE, "..", "casebank")
KNOWN_DEV = {"dev_meta_p2rep2_b1b": ["rf_sq5c2g"], "dev_space_p2rep2_b1b": ["rf_apqtyt"], "dev_ai_control_p2rep2_cyc0": ["rf_5qddqw"]}


def load(name):
    p = os.path.join(RES, name + ".jsonl")
    if not os.path.exists(p):
        return {}
    return {json.loads(l)["unit_id"]: json.loads(l) for l in open(p, encoding="utf-8") if l.strip()}


def sid_num(s):
    return int(re.sub(r"\D", "", s))


def cmain_flags(d0row, d2row):
    """C_main: D2rank上位3 + D0 rollbackのFlag(gate_onlyは除く)。文単位に統合。順序=D2rank順位、D0のみの文は後ろ。"""
    by = {}
    for f in (d2row or {}).get("flags", []):
        e = by.setdefault(f["sentence_id"], dict(sentence_id=f["sentence_id"], sentence=f["sentence"], src=[], rank=f.get("rank"), conf=f["confidence"],
                                                 type=f["type"], question=f["question"], fact_ids=f.get("fact_ids", []), mismatch=f.get("mismatch_terms", [])))
        e["src"].append("d2rank")
    for f in (d0row or {}).get("flags", []):
        if f.get("gate_only"):
            continue
        e = by.setdefault(f["sentence_id"], dict(sentence_id=f["sentence_id"], sentence=f["sentence"], src=[], rank=None, conf=f["confidence"],
                                                 type=f["type"], question=f["question"], fact_ids=f.get("fact_ids", []), mismatch=[]))
        if "d0rb" not in e["src"]:
            e["src"].append("d0rb")
    return sorted(by.values(), key=lambda e: (e["rank"] is None, e["rank"] or 99, -e["conf"]))


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else None


def f2(x, nd=2):
    return "-" if x is None else ("%.*f" % (nd, x))


def main():
    man = {m["article_id"]: m for m in PR.load_manifest()}
    d0, d2, d1 = load("d0_none_p3"), load("d2rank_gpt-6.1-sol_p3"), load("d1v2_gpt-6.1-sol_p3")
    cases = {c["case_id"]: c for c in json.load(open(os.path.join(CB, "casebank_01.json"), encoding="utf-8"))["cases"]}
    out = dict(articles={})
    lines = ["# P3_RESULT_01: 記事モード(調整用)結果 -- C_main(D0rollback ∪ D2rank) と D1v2(D0ゲート+因果創作)", "",
             "- モデル gpt-6.1-sol。対象: 新腕JA8/EN6、旧腕JA7/EN7(KPI3用)、dev既知重大元記事3本。保留側ケースの元記事は使っていない。",
             "- C_main = D2rank上位3文(強制列挙)に、D0のrollback Flagがあればそれを加えた『人間に見せる文』。KPI3=この固有文数/記事。", ""]
    rows = []
    for aid, m in man.items():
        if aid not in d2:
            continue
        flags = cmain_flags(d0.get(aid), d2.get(aid))
        rows.append((aid, m, flags))
        out["articles"][aid] = dict(role=m["role"], lang=m["lang"], arm=m["arm"], theme=m["theme"], n_flag_sentences=len(flags),
                                    flags=flags, d2rank_valid=d2[aid]["valid_json"], cost_d2rank=d2[aid]["cost_jpy"])
    lines += ["## 1. KPI3(1記事あたりのFlag固有文数、C_main)", "", "| 区分 | 記事数 | 平均 | 中央値 | 最大 | 確信度>=0.5の文/記事 | 確信度>=0.8の文/記事 |", "|---|---|---|---|---|---|---|"]
    groups = {}
    for aid, m, flags in rows:
        if m["role"].startswith("arm_"):
            for k in (m["role"], "arm_%s_all" % m["arm"], "lang_" + m["lang"], "ALL_arm"):
                groups.setdefault(k, []).append(flags)
    kpi3 = {}
    for k in sorted(groups):
        g = groups[k]
        cnt = sorted(len(f) for f in g)
        med = cnt[len(cnt) // 2] if len(cnt) % 2 else (cnt[len(cnt) // 2 - 1] + cnt[len(cnt) // 2]) / 2
        c5 = mean(sum(1 for e in f if e["conf"] >= 0.5) for f in g)
        c8 = mean(sum(1 for e in f if e["conf"] >= 0.8) for f in g)
        kpi3[k] = dict(n=len(g), mean=mean(cnt), median=med, max=max(cnt), mean_conf05=c5, mean_conf08=c8)
        lines.append("| %s | %d | %s | %s | %d | %s | %s |" % (k, len(g), f2(mean(cnt)), med, max(cnt), f2(c5), f2(c8)))
    out["kpi3"] = kpi3
    kpi3_all = kpi3.get("ALL_arm", {}).get("mean")
    lines += ["", "- KPI3の判定線: 合格 平均<=5(言語版別でも)、不合格線 >12。C_mainは**構造上、上位3件の強制列挙+D0 rollback**なので上限が定義で決まる点に注意(『記事に問題が無くても3件出る』)。", ""]
    lines += ["## 2. 新腕(Fact Lock+Astra) vs 旧腕: D2rankの順位別確信度", "",
              "| 区分 | 記事数 | rank1 確信度 平均 | rank2 平均 | rank3 平均 | rank1>=0.8の記事数 | D0 rollback Flagの記事数 |", "|---|---|---|---|---|---|---|"]
    arm = {}
    for aid, m, flags in rows:
        if not m["role"].startswith("arm_"):
            continue
        rk = {f["rank"]: f["confidence"] for f in d2[aid]["flags"]}
        key = "%s_%s" % (m["arm"], m["lang"])
        e = arm.setdefault(key, dict(n=0, r1=[], r2=[], r3=[], hi=0, d0=0))
        e["n"] += 1
        e["r1"].append(rk.get(1, 0))
        e["r2"].append(rk.get(2, 0))
        e["r3"].append(rk.get(3, 0))
        e["hi"] += int(rk.get(1, 0) >= 0.8)
        e["d0"] += int(any("d0rb" in x["src"] for x in flags))
    for k in sorted(arm):
        e = arm[k]
        lines.append("| %s | %d | %s | %s | %s | %d | %d |" % (k, e["n"], f2(mean(e["r1"])), f2(mean(e["r2"])), f2(mean(e["r3"])), e["hi"], e["d0"]))
    out["arm_conf"] = {k: dict(n=e["n"], r1=mean(e["r1"]), r2=mean(e["r2"]), r3=mean(e["r3"]), hi_articles=e["hi"], d0=e["d0"]) for k, e in arm.items()}
    lines += ["", "- 解釈の注意: 強制列挙のため『Flag数』は新旧で差が出ない。差が出るのは**確信度**。N(6〜8本)が小さく、テーマ・言語・腕が交絡する。", ""]
    lines += ["## 3. dev既知重大元記事でのRecall@top3(文脈内)", "", "| 記事 | 既知重大(case) | 文の位置 | C_main内の順位 | top3内 | ±2文窓内 | D1v2で同文Flag | D1v2の型 |", "|---|---|---|---|---|---|---|---|"]
    hit3, win, n_loc, rec = 0, 0, 0, []
    for aid, cids in KNOWN_DEV.items():
        if aid not in d2:
            continue
        u = PR.build_unit(man[aid])
        texts = [s["text"] for s in u["sentences"]]
        flags = out["articles"][aid]["flags"]
        for cid in cids:
            ks = cases[cid]["sentence"]
            pos = AG.locate_sentence(texts, ks)
            rank = None
            in3 = None
            inwin = None
            d1t = "-"
            d1hit = "-"
            if pos is not None:
                n_loc += 1
                sids = {sid_num(e["sentence_id"]) - 1: i for i, e in enumerate(flags)}
                rank = (sids[pos] + 1) if pos in sids else None
                in3 = pos in {sid_num(f["sentence_id"]) - 1 for f in d2[aid]["flags"]}
                inwin = any(abs(i - pos) <= 2 for i in sids)
                hit3 += int(in3)
                win += int(inwin)
                if aid in d1:
                    ts = [f["type"] for f in d1[aid]["flags"] if sid_num(f["sentence_id"]) - 1 == pos]
                    d1hit = "あり" if ts else "なし"
                    d1t = ",".join(ts) or "-"
            rec.append(dict(article=aid, case=cid, pos=pos, rank=rank, in_top3=in3, in_window=inwin, d1_hit=d1hit, d1_types=d1t))
            lines.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (aid, cid, "s%d" % (pos + 1) if pos is not None else "未特定", rank or "-", "YES" if in3 else "NO", "YES" if inwin else "NO", d1hit, d1t))
    r3 = hit3 / float(n_loc) if n_loc else None
    out["recall_at_top3"] = dict(hit=hit3, n=n_loc, rate=r3, window_hit=win, records=rec)
    lines += ["", "- **Recall@top3(D2rank上位3、dev既知重大元記事) = %d/%d = %s**、±2文窓内 %d/%d。" % (hit3, n_loc, f2(r3 * 100 if r3 is not None else None, 0) + "%", win, n_loc),
              "- n=3記事と極めて小さく、統計的な根拠にはならない(調整用の方向確認)。rf_g7k93w(仕組みの創作)とrf_ur5649(K03)は元記事が保存されておらず(文のみ)記事モードでは測れない。", ""]
    gate_ok = (kpi3_all is not None and kpi3_all <= 5) and (r3 is not None and r3 >= 0.5)
    out["p3_gate"] = dict(kpi3_all_mean=kpi3_all, recall_at_top3=r3, passed=gate_ok)
    lines += ["## 4. P3ゲート(事前登録)", "", "- KPI3平均(全腕記事) = %s (<=5) / dev既知重大Recall@top3 = %s (>=50%%) -> **%s**" % (f2(kpi3_all), f2(r3 * 100 if r3 is not None else None, 0) + "%", "合格(P4へ自動進行)" if gate_ok else "不合格(STOP、ループ3判断)"), ""]
    if d1:
        lines += ["## 5. D1v2(D0ゲート+因果創作、Flag上限3/型)記事モード", "", "| 記事 | 呼び出し数 | Flag固有文 | Flag(sent,type) | 型内訳 | 費用¥ |", "|---|---|---|---|---|---|"]
        cs = []
        for aid, r in d1.items():
            fl = r["flags"]
            by = {}
            for f in fl:
                by[f["type"]] = by.get(f["type"], 0) + 1
            uq = len({f["sentence_id"] for f in fl})
            cs.append(uq)
            lines.append("| %s | %d | %d | %d | %s | %s |" % (aid, len(r["calls"]), uq, len(fl), " ".join("%s:%d" % kv for kv in sorted(by.items())) or "-", f2(r["cost_jpy"])))
        lines += ["", "- D1v2のFlag固有文/記事: 平均 %s、最大 %s(記事数 %d)。" % (f2(mean(cs)), max(cs) if cs else "-", len(cs)), ""]
        out["d1v2_mean_flag_sentences"] = mean(cs)
        out["d1v2_flags"] = {aid: r["flags"] for aid, r in d1.items()}
    human = []
    for aid, m, flags in rows:
        if m["role"] in ("arm_new_ja", "arm_new_en", "dev_known"):
            for e in flags:
                human.append(dict(article=aid, role=m["role"], lang=m["lang"], rank=e["rank"], sentence_id=e["sentence_id"], sentence=e["sentence"],
                                  conf=e["conf"], type=e["type"], fact_ids=e["fact_ids"], question=e["question"], mismatch=e["mismatch"], src=e["src"]))
    json.dump(human, open(os.path.join(RES, "P3_FLAGS_FOR_HUMAN_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    lines += ["## 6. 費用", ""]
    tot = 0.0
    for nm, d in (("D2rank", d2), ("D1v2", d1)):
        c = sum(r["cost_jpy"] or 0 for r in d.values())
        tot += c
        lines.append("- %s: ¥%.2f(%d unit)" % (nm, c, len(d)))
    out["cost_p3"] = tot
    lines.append("- P3合計 ¥%.2f(上限¥250、レイアウト回帰確認の別枠 ¥10.75 は含まない)" % tot)
    open(os.path.join(RES, "P3_RESULT_01.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    json.dump(out, open(os.path.join(RES, "P3_RESULT_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
