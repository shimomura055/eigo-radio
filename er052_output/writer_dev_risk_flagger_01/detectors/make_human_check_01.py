# -*- coding: utf-8 -*-
"""朝のユーザー確認パック HUMAN_CHECK_RISK_FLAGGER_01.md の生成(委任_03、委任_04で v2 に修正、API¥0)。
(a) KPI5: 新腕(Fact Lock+Astra)記事のFlag。各記事で C_main(D2rank上位3 + D0 rollback)を必ず提示。
    D1v2 がC_mainの文以外に挙げたFlagは『追加分』として分離(別集計)。選択肢=A重大/B1要確認で価値あり/B2問題なし/C判断不能。
    事前登録KPI5条件(20件・層別無作為・新腕+旧腕)との差を冒頭に明記。
(b) ラベル再確認候補(rf_zbe99x + CASEBANK §7 の5件)。各件に『疑われている点』。登録時ラベルが主値。ラベルは変えない。
(c) S0_USER_CHECK の3文と質問、反転時の再計算結果(P4_RESULT_01.json)。
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

SUSPECT = {
    "rf_zbe99x": "台帳は『従業員1件の報告』で『契約スタッフ全体へ一般化しない』と注意しているが、文は報告の出所と件数を落として事実として書いているように読める。現ラベル(非重大)が軽すぎないか。",
    "rf_sq5c2g": "『知らされていなかったのは人間(契約スタッフ)』と書いているが、台帳は開示の相手(誰に開示しなかったか)を特定していない。開示対象の取り違えにあたるか。",
    "rf_apqtyt": "台帳の『初めて』は『宇宙に兵器を配備したと初めて認めた』ことだが、文は『宇宙を確保する準備が初めて公になった』と範囲を広げているように読める。",
    "rf_665ga9": "台帳の20%は『すべての貨物に対する償還率』だが、文は『安全確保にかかる費用の20%』とも読める。20%が何に対する率かの取り違えか。",
    "rf_t9nxuv": "台帳は『撤回発表後、Brent先物が一時縮小しその後ほどなく戻った』だけだが、文は『価格を動かす出来事も戻った』と、台帳にない出来事・時期を足しているように読める。",
    "rf_nck2y6": "台帳は『貨物に20%の率で償還を求める』だが、文は『貨物を運ぶ側が米国の警備費用を返す』と支払義務者を特定している。台帳に支払主体の記載があるか。",
}

OPT = "- 回答: A 重大 / B1 要確認で価値あり / B2 問題なし / C 判断不能 → [   ]　　新規重大候補か(はい/いいえ) → [   ]　　所要: [   ] 分"


def main():
    p3 = json.load(open(os.path.join(RES, "P3_RESULT_01.json"), encoding="utf-8"))
    man = [m for m in PR.load_manifest() if m["role"] in ("arm_new_ja", "arm_new_en")]
    man.sort(key=lambda m: (ORDER.index(m["theme"]), m["lang"]))
    cases = {c["case_id"]: c for c in json.load(open(os.path.join(CB, "casebank_01.json"), encoding="utf-8"))["cases"]}
    L = ["# HUMAN_CHECK_RISK_FLAGGER_01 v2: 朝の確認パック(WRITER-DEV-RISK-FLAGGER-DESIGN-01 委任_04で修正)", "",
         "目的: Risk Flaggerが挙げた『人間が確認した方がよい箇所』が、実際に役に立つかを測ります(KPI5)。**Flaggerは合否判定をしません。**",
         "各Flagの『根拠Fact』(台帳の逐語)と文を見比べ、次のどれかを書いてください:",
         "- A = 重大(読者に事実と逆・別の意味を与える。直すべき)",
         "- B1 = 要確認で価値あり(重大とまでは言えないが、言われて確認する意味があった)",
         "- B2 = 問題なし(台帳の範囲内で、確認しても無駄だった)",
         "- C = 判断不能(元資料を見ないと分からない)",
         "- 『新規重大候補か』欄: Aと答えた箇所のうち、これまでの既知事故(Rollback反転、開示対象の取り違え、『初めて』の範囲拡張、20%の対象入替、時期の創作、因果・仕組みの創作)に当てはまらない新しい種類の重大なら『はい』。",
         "- 所要分数欄: そのFlagの確認にかかった目安の分数(秒でも可)。KPI3/5の確認負荷の実測になります。", "",
         "このパックは3つの部分に分かれています。(a)は5回に分けて読めます(各回2〜3記事)。(b)(c)は別枠です。", ""]
    # ---- (a)
    L += ["## (a) 新腕記事のFlag(KPI5)", "",
          "### 事前登録のKPI5条件との差(重要)", "",
          "事前登録(DESIGN_RISK_FLAGGER_01.md KPI5): 新腕・旧腕の実記事に立ったFlagのうち、既知ケースと無関係な箇所から**最大20件を層別無作為抽出**し、重大/要確認で価値あり=有用、問題なし=無用で裁定。",
          "このパックは次の点が登録条件と**異なります**(結果の解釈時に明記します)。",
          "- 旧腕(Fact Lock+Astra以前の記事)は含みません。新腕14記事のみです(旧腕との比較はできません)。",
          "- 無作為抽出ではなく、新腕14記事の**C_mainのFlag全件**です。件数が20件を超えます。負担が大きければ、バッチ1から順に答えられる所までで構いません(答えた範囲だけで暫定集計し、暫定と明記します。未回答は抜かして集計します)。",
          "- 有用率の計算: Useful_rate = (A + B1) / 回答済みFlag数(C=判断不能は分母から外して別掲)。合格線は 40%以上、または新規重大候補1件以上かつ25%以上。",
          "- **提示の仕方を分けています**: 各記事で、まず『C_main』(D2rankの上位3文 + D0 rollbackがあればそれ)を必ず提示します。これが推奨構成の実際の出力で、KPI5の主集計はここだけです。D1v2(タイプ別専用、新腕JA8記事のみ実行)がC_mainの文以外に追加で挙げたFlagは『追加分』として**別に**提示し、別集計します(混ぜると、推奨構成の有用率が測れなくなるため)。", "",
          "- 対象: Fact Lock+Astra新腕の最終JA 8本とEN Advanced 6本(計14記事)。",
          "- 確信度の注意: D2rankは『強制列挙』なので記事が問題なくても3件出て、確信度は低くなる(0.02〜0.35)。D1v2は高め(0.7〜0.96)に出る傾向があり、確信度の絶対値は比較できません。", ""]
    arts = []
    for m in man:
        aid = m["article_id"]
        a = p3["articles"][aid]
        cmain = []
        for e in sorted(a["flags"], key=lambda e: (e["rank"] or 99)):
            cmain.append(dict(sid=e["sentence_id"], sentence=e["sentence"], conf=e["conf"], type=e["type"], q=e["question"],
                              facts=e["fact_ids"], src=",".join(e["src"]) + (" 順位%s" % e["rank"] if e["rank"] else "")))
        have = {c["sid"] for c in cmain}
        extra = []
        for f in p3.get("d1v2_flags", {}).get(aid, []):
            if f["sentence_id"] in have or any(x["sid"] == f["sentence_id"] for x in extra):
                continue
            extra.append(dict(sid=f["sentence_id"], sentence=f["sentence"], conf=f["confidence"], type=f["type"], q=f["question"],
                              facts=f.get("fact_ids", []), src="d1v2:" + f["type"]))
        arts.append((m, cmain, sorted(extra, key=lambda c: -c["conf"])))
    batches = [arts[i:i + 3] for i in range(0, len(arts), 3)]
    n_main = n_extra = 0

    def emit(c, label, facts_map):
        L.extend(["**%s** (%s、確信度 %.2f、文id %s)" % (label, c["src"], c["conf"], c["sid"]), "",
                  "- Flag文: %s" % c["sentence"],
                  "- 確認質問: %s" % c["q"]])
        for fid in c["facts"][:2]:
            if fid in facts_map:
                L.append("- 根拠Fact `%s`(逐語): %s" % (fid, facts_map[fid].replace("\n", " ")))
        L.extend([OPT, ""])

    for bi, b in enumerate(batches, 1):
        L += ["### バッチ%d(%d記事)" % (bi, len(b)), ""]
        for m, cmain, extra in b:
            u = PR.build_unit(m)
            facts = {f["fact_id"]: f["text"] for f in u["facts"]}
            L += ["#### %s %s(%s)" % (m["theme"], m["lang"], m["article_id"]), "- 記事: `%s`" % m["article_path"], ""]
            for i, c in enumerate(cmain, 1):
                n_main += 1
                emit(c, "C_main Flag %d" % i, facts)
            if extra:
                L += ["追加分(D1v2のみが挙げた別の文。主集計には入れず別集計):", ""]
                for i, c in enumerate(extra, 1):
                    n_extra += 1
                    emit(c, "追加分 Flag %d" % i, facts)
    L += ["(a)の合計: C_main %d Flag + D1v2追加分 %d Flag。1Flagあたり30〜60秒なら、C_mainだけで約%d〜%d分。" % (n_main, n_extra, n_main // 2 + 1, n_main), ""]
    # ---- (b)
    L += ["## (b) ラベル再確認候補(ラベルはまだ変えていません)", "",
          "Flaggerの評価の土台である『正解ラベル』のうち、人間が確認すると評価が確定するものです。重大/非重大のどちらが妥当かだけ教えてください。",
          "**取り扱い**: 事前登録のKPIは『登録時のラベル』の値を**主値**として確定済みです(結果を見てからラベルを直すと、都合よく合わせた数字になるため)。回答でラベルが変わる場合も、報告では登録時ラベルの値を主値とし、修正後の値は**併記**します。", ""]
    cand_b = [("rf_zbe99x", "RC-K05(現ラベル=非重大・軽微)。D2(2rep)・D1が一貫してFlagした唯一のclear非重大。ラベルが妥当かの確認"),
              ("rf_sq5c2g", "meta-p2r2-02(開示対象の取り違え)。現ラベル=Sonnet判定の重大"),
              ("rf_apqtyt", "sw-p2r2-02(『初めて』の範囲拡張)。現ラベル=Sonnet判定の重大"),
              ("rf_665ga9", "hormuz-T0M0r2-01(20%の対象入替)。現ラベル=Sonnet判定の重大"),
              ("rf_t9nxuv", "RC-K16(時期の創作)。現ラベル=Sonnet判定の重大"),
              ("rf_nck2y6", "RC-K18/Safety-A2A3-0(支払義務者)。現ラベル=Sonnet判定の重大")]
    for cid, why in cand_b:
        c = cases[cid]
        L += ["### %s: %s" % (cid, why), "",
              "- 疑われている点: %s" % SUSPECT[cid],
              "- 文: %s" % c["sentence"],
              "- 前後: 前=%s / 後=%s" % ((c.get("context") or {}).get("before") or "(なし)", (c.get("context") or {}).get("after") or "(なし)"),
              "- 根拠Fact(逐語): %s" % c["fact"]["text"].replace("\n", " "),
              "- 現ラベル(登録時、主値): %s(根拠区分=%s)" % (c["label"], c["label_basis"]),
              "- 回答: A 重大 / B 非重大 → [   ]　　所要: [   ] 分", ""]
    # ---- (c)
    S0 = [("S0-1", "rf_aennw4", "保留", "「users」(開示を受ける相手)を書いたことは重大か",
           "台帳(MUSE-HC-012)は『適切な開示なしに契約スタッフが電話をかけるテストを開始したことをミスと認め、機能を当面ロールバック』。開示の相手の記載なし。",
           "Ledgerは適切な開示がなかったことを記録しているが、誰に開示されなかったかは特定していない(deviation checkの指摘、MAJOR)。"),
          ("S0-2", "rf_xyw4mp", "dev", "「so」で因果をつなぐことは重大か",
           "台帳(MUSE-HC-012)は『ミスの認定とロールバックを並記』。因果は明示なし。",
           "『so』が開示なしをロールバックの原因として示しているが、Ledgerは因果を明示していない(deviation checkの指摘、MAJOR)。"),
          ("S0-3", "rf_8fbz5r", "保留", "Brent先物の動きを「oil prices」と一般化することは重大か",
           "台帳(HF-009)は『Brent先物が一時縮小後ほどなく高水準へ戻った』(scope: 国際指標Brent原油先物の短時間の値動き)。",
           "Brent先物の値動きを原油価格全般の動きとして表現している(deviation checkの指摘、MAJOR)。")]
    L += ["## (c) S0_USER_CHECK(3文)と、反転時の再計算結果", "",
          "出典: `er052_output/open243_translation_ng_analysis_01/S0_USER_CHECK.md`。**質問は3問とも同じ**です: 『この要約文は、台帳の範囲で書いたものとして許容してよいか(許容/不許容)』。",
          "不許容=重大と回答された場合に、下の再計算(事前登録規則)が適用されます。現在のラベルは『非重大(Sonnet判定・境界例)』のままです。", ""]
    for sid, cid, sp, title, fact, why in S0:
        c = cases[cid]
        L += ["### %s(%s、%s): %s" % (sid, cid, sp, title), "",
              "- 要約文: %s" % c["sentence"],
              "- 台帳: %s" % fact,
              "- 指摘理由: %s" % why,
              "- 回答: 許容 / 不許容 → [   ]　　所要: [   ] 分", ""]
    p4 = os.path.join(RES, "P4_RESULT_01.json")
    L += ["### 反転時の再計算結果", "",
          "S0-1(rf_aennw4)/S0-2(rf_xyw4mp)/S0-3(rf_8fbz5r)を『不許容=重大』と回答した場合の保留セットKPIの再計算です(事前登録規則:",
          "当該ケースを重大[ユーザー確認]に移し、Recall_all/Recall_humanの分母+1、FPR_boundary/hardnegの分母-1)。回答待ちのためラベルは変えていません。", ""]
    if os.path.exists(p4):
        r = json.load(open(p4, encoding="utf-8"))
        L += ["(保留セットのみの再計算。S0-2はdev側のため『全て』でも保留の値は変わらない)", "", "| 反転対象 / 構成 | Recall_all | Recall_human | FPR_boundary |", "|---|---|---|---|"]
        for k, v in r.get("s0", {}).items():
            def fr(d):
                return "-" if not d or not d.get("n") else "%d/%d" % (d["k"], d["n"])
            L.append("| %s | %s | %s | %s |" % (k.replace("|", " / "), fr(v["recall_all"]), fr(v["recall_human"]), fr(v["fpr_boundary"])))
    else:
        L.append("(P4集計後に追記)")
    L += ["", "元の定義は `results/P4_RESULT_01.md` 5節。", ""]
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("written", OUT, "main", n_main, "extra", n_extra)


if __name__ == "__main__":
    main()
