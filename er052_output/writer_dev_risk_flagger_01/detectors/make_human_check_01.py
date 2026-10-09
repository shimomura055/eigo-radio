# -*- coding: utf-8 -*-
"""朝のユーザー確認パック HUMAN_CHECK_RISK_FLAGGER_01.md の生成(委任_03、API¥0)。
(a) KPI5: 新腕(Fact Lock+Astra)記事のFlag上位(記事あたり<=3)。選定規則: C_main(D2rank上位3+D0rb)とD1v2(新腕JAのみ実行)のFlagを
    『Flag確信度』の降順で統合(同一文は1件)、上位3件。確信度はD2rank(forced listing、低めに出る)とD1v2(高めに出る)で較正が違う点に注意。
(b) ラベル再確認候補(rf_zbe99x + CASEBANK §7 の5件)。ラベルは変えない。
(c) S0反転時の再計算結果(P4_RESULT_01.json があれば転記)。
1回に読む量は2〜3記事相当(バッチ)に区切る。"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import p3_run_01 as PR  # noqa: E402

RES = os.path.join(HERE, "results")
CB = os.path.join(HERE, "..", "casebank")
OUT = os.path.join(HERE, "..", "HUMAN_CHECK_RISK_FLAGGER_01.md")
ORDER = ["byd_recall", "hormuz", "meta", "small_bag", "space_weapons", "streaming_price", "openai_copyright", "semiconductor_earnings"]


def main():
    p3 = json.load(open(os.path.join(RES, "P3_RESULT_01.json"), encoding="utf-8"))
    man = [m for m in PR.load_manifest() if m["role"] in ("arm_new_ja", "arm_new_en")]
    man.sort(key=lambda m: (ORDER.index(m["theme"]), m["lang"]))
    cases = {c["case_id"]: c for c in json.load(open(os.path.join(CB, "casebank_01.json"), encoding="utf-8"))["cases"]}
    L = ["# HUMAN_CHECK_RISK_FLAGGER_01: 朝の確認パック(WRITER-DEV-RISK-FLAGGER-DESIGN-01 委任_03)", "",
         "目的: Risk Flaggerが挙げた『人間が確認した方がよい箇所』が、実際に役に立つかを測ります(KPI5)。**Flaggerは合否判定をしません。**",
         "各Flagの『根拠Fact』(台帳の逐語)と文を見比べ、次のどれかを書いてください:",
         "- A = 重大(読者に事実と逆・別の意味を与える。直すべき) / B = 非重大(問題ないか、軽い言い換え) / C = 判断不能(元資料を見ないと分からない)",
         "- 所要分数欄には、そのFlagの確認にかかった目安の分数(秒でも可)を書いてください(KPI3/5の確認負荷の実測になります)。",
         "", "このパックは3つの部分に分かれています。(a)は5回に分けて読めます(各回2〜3記事)。(b)(c)は別枠です。", ""]
    # ---- (a)
    L += ["## (a) 新腕記事のFlag上位(KPI5)", "",
          "- 対象: Fact Lock+Astra新腕の最終JA 8本とEN Advanced 6本(計14記事)。各記事 最大3Flag。",
          "- 選定: C_main(D2rank上位3+D0 rollback)とD1v2(新腕JAのみ実行。タイプ別+因果創作)のFlagを確信度の降順で統合し上位3件。",
          "  確信度の注意: D2rankは『強制列挙』なので記事が問題なくても3件出て、確信度は低くなる(0.02〜0.35)。D1v2は高め(0.7〜0.96)に出る傾向があり、確信度の絶対値は比較できません。", ""]
    arts = []
    for m in man:
        aid = m["article_id"]
        a = p3["articles"][aid]
        cand = {}
        for e in a["flags"]:
            cand[e["sentence_id"]] = dict(sid=e["sentence_id"], sentence=e["sentence"], conf=e["conf"], type=e["type"], q=e["question"],
                                          facts=e["fact_ids"], src=",".join(e["src"]) + (" 順位%s" % e["rank"] if e["rank"] else ""))
        for f in p3.get("d1v2_flags", {}).get(aid, []):
            c = cand.get(f["sentence_id"])
            if c is None or f["confidence"] > c["conf"]:
                cand[f["sentence_id"]] = dict(sid=f["sentence_id"], sentence=f["sentence"], conf=f["confidence"], type=f["type"], q=f["question"],
                                              facts=f.get("fact_ids", []), src="d1v2:" + f["type"])
        top = sorted(cand.values(), key=lambda c: -c["conf"])[:3]
        arts.append((m, top))
    batches = [arts[i:i + 3] for i in range(0, len(arts), 3)]
    n_flags = 0
    for bi, b in enumerate(batches, 1):
        L += ["### バッチ%d(%d記事)" % (bi, len(b)), ""]
        for m, top in b:
            u = PR.build_unit(m)
            facts = {f["fact_id"]: f["text"] for f in u["facts"]}
            L += ["#### %s %s(%s)" % (m["theme"], m["lang"], m["article_id"]), "- 記事: `%s`" % m["article_path"], ""]
            for i, c in enumerate(top, 1):
                n_flags += 1
                L += ["**Flag %d** (%s、確信度 %.2f、文id %s)" % (i, c["src"], c["conf"], c["sid"]), "",
                      "- Flag文: %s" % c["sentence"],
                      "- 確認質問: %s" % c["q"]]
                for fid in c["facts"][:2]:
                    if fid in facts:
                        L.append("- 根拠Fact `%s`(逐語): %s" % (fid, facts[fid].replace("\n", " ")))
                L += ["- 回答: A 重大 / B 非重大 / C 判断不能 → [   ]　　所要: [   ] 分", ""]
    L += ["(a)の合計 %d Flag。1Flagあたり30〜60秒なら約%d〜%d分。" % (n_flags, n_flags // 2 + 1, n_flags), ""]
    # ---- (b)
    L += ["## (b) ラベル再確認候補(ラベルはまだ変えていません)", "",
          "Flaggerの評価の土台である『正解ラベル』のうち、人間が確認すると評価が確定するものです。重大/非重大のどちらが妥当かだけ教えてください。", ""]
    cand_b = [("rf_zbe99x", "RC-K05(現ラベル=非重大・軽微)。D2(2rep)・D1が一貫してFlagした唯一のclear非重大。ラベルが妥当かの確認"),
              ("rf_sq5c2g", "meta-p2r2-02(開示対象の取り違え)。現ラベル=Sonnet判定の重大"),
              ("rf_apqtyt", "sw-p2r2-02(『初めて』の範囲拡張)。現ラベル=Sonnet判定の重大"),
              ("rf_665ga9", "hormuz-T0M0r2-01(20%の対象入替)。現ラベル=Sonnet判定の重大"),
              ("rf_t9nxuv", "RC-K16(時期の創作)。現ラベル=Sonnet判定の重大"),
              ("rf_nck2y6", "RC-K18/Safety-A2A3-0(支払義務者)。現ラベル=Sonnet判定の重大")]
    for cid, why in cand_b:
        c = cases[cid]
        L += ["### %s: %s" % (cid, why), "",
              "- 文: %s" % c["sentence"],
              "- 前後: 前=%s / 後=%s" % ((c.get("context") or {}).get("before") or "(なし)", (c.get("context") or {}).get("after") or "(なし)"),
              "- 根拠Fact(逐語): %s" % c["fact"]["text"].replace("\n", " "),
              "- 現ラベル: %s(根拠区分=%s)" % (c["label"], c["label_basis"]),
              "- 回答: A 重大 / B 非重大 → [   ]　　所要: [   ] 分", ""]
    # ---- (c)
    L += ["## (c) S0_USER_CHECK 反転時の再計算結果", "",
          "S0-1(rf_aennw4)/S0-2(rf_xyw4mp)/S0-3(rf_8fbz5r)をあなたが『重大』と回答した場合の、保留セットKPIの再計算です(事前登録規則:",
          "当該ケースを重大[ユーザー確認]に移し、Recall_all/Recall_humanの分母+1、FPR_boundary/hardnegの分母-1)。回答待ちのためラベルは変えていません。", ""]
    p4 = os.path.join(RES, "P4_RESULT_01.json")
    if os.path.exists(p4):
        r = json.load(open(p4, encoding="utf-8"))
        L += ["| 反転対象|構成 | Recall_all | Recall_human | FPR_boundary |", "|---|---|---|---|---|"]
        for k, v in r.get("s0", {}).items():
            def fr(d):
                return "-" if not d or not d.get("n") else "%d/%d" % (d["k"], d["n"])
            L.append("| %s | %s | %s | %s |" % (k.replace("|", " / "), fr(v["recall_all"]), fr(v["recall_human"]), fr(v["fpr_boundary"])))
    else:
        L.append("(P4集計後に追記)")
    L += ["", "元の定義は `results/P4_RESULT_01.md` 5節。", ""]
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("written", OUT, "flags", n_flags)


if __name__ == "__main__":
    main()
