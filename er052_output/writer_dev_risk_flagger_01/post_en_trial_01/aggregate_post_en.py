# -*- coding: utf-8 -*-
"""Phase3(JPY0): 集計・RESULT_01.md / HUMAN_REVIEW_POST_EN_01.md 生成。有用/不要の最終ラベルは確定しない(提案ラベルのみ)。"""
import json, os, glob, collections
HERE = os.path.dirname(os.path.abspath(__file__))
man = json.load(open(os.path.join(HERE, "manifest_post_en_01.json"), encoding="utf-8"))
UN = [u["unit"] for u in man["units"]]
umap = {u["unit"]: u for u in man["units"]}
F = {}
for lv in (3, 4):
    for u in UN:
        p = glob.glob(os.path.join(HERE, "flags", "A%d" % lv, u + "_*.json"))
        assert len(p) == 1
        F[(lv, u)] = json.load(open(p[0], encoding="utf-8"))
# 提案ラベル(Claude機械的提案。最終ラベルはユーザー)
KN = {
 ("U01","s18"):("New","(旧Check指摘なし)"),
 ("U02","s18"):("New","(旧Check指摘なし。U02は旧CheckでCOMPLIANT)"),
 ("U03","s1"):("Known系統","能力の秘匿・不在断定系(旧Check: b1b_prev_b1 attempt1『has not explained what they can do』= changed_fact/unsupported_new_claim, translation)。ただし最終稿U03自体は旧CheckがCOMPLIANT"),
 ("U03","s5"):("Known系統","同上(能力・性能が秘密/非開示という断定)。文がU.S.の位置で分割されており途中で切れている"),
 ("U03","s13"):("Known系統","同上(『no specific system names or attack capabilities have been given』)"),
 ("U03","s17"):("Known系統","旧Check: space a2稿attempt1/2が『Russia has destroyed satellites』複数形を翻訳由来MAJOR(changed_number等)と指摘。b1b稿には旧Check指摘なし"),
 ("U03","s33"):("Known系統","同上(『has not disclosed their capabilities』。E2E EVALが最終Adv『In one line』に残存と記録した文)"),
 ("U04","s7"):("New","(旧Check指摘なし)"),
 ("U04","s15"):("New","(旧Check指摘なし)"),
 ("U05","s1"):("Known関連","BYD In One Lineの条件落ち(旧Check A2稿 changed_scope)と同系統の『極端な場合』条件落ちだが、Flagされたのは見出し文。In One Line文(s27)自体は未Flag"),
 ("U05","s4"):("New","(旧Check指摘なし。Fact無し=台帳にない主張)"),
 ("U05","s6"):("New","(旧Check指摘なし。台帳BYD-RECALL-01は『2件の公告の合算』)"),
 ("U06","s8"):("New","(旧Check指摘なし)"),
 ("U06","s9"):("New","(旧Check指摘なし)"),
 ("U06","s16"):("New","(旧Check指摘なし。Fact無し)"),
 ("U06","s17"):("New","(旧Check指摘なし)"),
 ("U06","s21"):("New","(旧Check指摘なし。台帳F05の第三者請求条件の脱落)"),
 ("U07","s1"):("Known","旧Check: 見出し『AI Lawsuits Are About More Than Money』のscope拡張(changed_scope, origin=ja_source, F6)= U07がSTOPした直接原因。A3は未Flag、A4のみ"),
 ("U07","s5"):("New","(旧Check指摘なし)"),
 ("U07","s21"):("New","(旧Check指摘なし)"),
 ("U07","s22"):("New","(旧Check指摘なし。Fact無し)"),
 ("U08","s25"):("Known(境界例)","旧Check: unsupported_new_claim(F6)。ユーザー判断は『ベストではないが問題視するほどではない』= 過剰Flagを見る境界例"),
 ("X09","s8"):("New","(旧Check指摘なし。『U.S.』で文が分割され『ensuring U.S.』で切れた分割アーティファクトの可能性)"),
 ("X09","s10"):("New","(旧Check指摘なし。Fact無し)"),
 ("X10","s5"):("Known","旧Check: space a2_prev_b1 Standard attempt1『The main subject is not a weapon that can blow up Earth.』(unsupported_new_claim, ja_source)と同一文。A3は未Flag、A4のみ"),
 ("X11","s7"):("Known","旧Check: changed_actor(MAJOR, ja_source, F4)『They also say the models' output … removed copyright management information.』= OpenAI actor drift"),
 ("X11","s4"):("New","(旧Check指摘なし)"),
 ("X11","s17"):("New","(旧Check指摘なし)"),
 ("X11","s25"):("New","(旧Check指摘なし)"),
}
# 意味上の問題単位への束ね方(Claudeの機械的提案。同一の意味問題を複数文で指摘した場合のみ束ねる)
BUNDLE = {
 "U03": [("能力・性能の秘匿/非開示の断定(F-001注記)", ["s1","s5","s13","s33"]), ("ロシアの衛星破壊の複数形(F-003)", ["s17"])],
 "U04": [("小型クラッチ特定の評価をミニバッグ全般へ拡張(MB-05/MB-03)", ["s7","s15"])],
 "U06": [("値上げ適用の範囲・時期(will go from…。F02/F03/F05/F06)", ["s8","s9"])],
 "X11": [("破棄請求の対象範囲(原告のコンテンツ→広い表現。F6)", ["s4","s17"])],
}
def bundles(u, sids):
    bs, used = [], set()
    for name, ss in BUNDLE.get(u, []):
        got = [s for s in ss if s in sids]
        if got: bs.append((name, got)); used |= set(got)
    for s in sorted(sids, key=lambda x: int(x[1:])):
        if s not in used: bs.append((None, [s]))
    return bs
def sk(s): return int(s[1:])
S = dict(a3=0, a4=0, overlap=0, union=0, units=0)
per = collections.OrderedDict()
for u in UN:
    a3 = {f["sentence_id"]: f for f in F[(3, u)]["flags"]}; a4 = {f["sentence_id"]: f for f in F[(4, u)]["flags"]}
    assert len(a3) == len(F[(3, u)]["flags"]) and len(a4) == len(F[(4, u)]["flags"]), "同一文の重複Flag"
    un = sorted(set(a3) | set(a4), key=sk)
    ov = sorted(set(a3) & set(a4), key=sk)
    for s in un: assert (u, s) in KN, (u, s)
    bu = bundles(u, set(un))
    per[u] = dict(a3=a3, a4=a4, union=un, overlap=ov, bundles=bu)
    S["a3"] += len(a3); S["a4"] += len(a4); S["overlap"] += len(ov); S["union"] += len(un); S["units"] += len(bu)
core8 = [u for u in UN if u.startswith("U")]
S8 = dict(union=sum(len(per[u]["union"]) for u in core8), units=sum(len(per[u]["bundles"]) for u in core8))
cost = [F[(lv, u)]["cost_jpy"] for lv in (3, 4) for u in UN]
usage_in = sum(x["input_tokens"] for lv in (3, 4) for u in UN for x in F[(lv, u)]["usage"])
usage_out = sum(x["output_tokens"] for lv in (3, 4) for u in UN for x in F[(lv, u)]["usage"])
models = sorted({m for k in F for m in F[k]["model_ids"]})
agg = dict(sentence_level_total=S["a3"] + S["a4"], a3=S["a3"], a4=S["a4"], overlap=S["overlap"], union=S["union"], semantic_units=S["units"],
           avg_union_per_article_11=round(S["union"] / 11, 2), avg_units_per_article_11=round(S["units"] / 11, 2),
           union_core8=S8["union"], units_core8=S8["units"], avg_union_core8=round(S8["union"] / 8, 2), avg_units_core8=round(S8["units"] / 8, 2),
           cost_jpy=round(sum(cost), 3), n_calls=len(cost), input_tokens=usage_in, output_tokens=usage_out, model_ids=models,
           attempts=[F[k]["attempts"] for k in F], valid=[F[k]["valid_json"] for k in F],
           per_article={u: dict(a3=len(per[u]["a3"]), a4=len(per[u]["a4"]), overlap=len(per[u]["overlap"]), union=len(per[u]["union"]), units=len(per[u]["bundles"])) for u in UN})
json.dump(agg, open(os.path.join(HERE, "aggregate_post_en_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
def trunc(s, n):
    s = s.replace("\n", " ").replace("|", "/")
    return s if len(s) <= n else s[:n] + "…"
def cell(f):
    return "%s %.2f" % (f["type"], f["confidence"]) if f else "-"
def reason(u, s):
    q3 = per[u]["a3"].get(s); q4 = per[u]["a4"].get(s)
    r = []
    if q3: r.append("A3: " + trunc(q3["question"], 200))
    if q4: r.append("A4: " + trunc(q4["question"], 200))
    return " / ".join(r)
R = ["# RESULT_01: WRITER-DEV-RISK-FLAGGER-POST-EN-TRIAL-01 結果(Trial/DEV、2026-10-10)", "",
"**Closeout分類(Sonnet提案、Fable確定): USER_DECISION_REQUIRED。** VALIDATED/REJECTEDではなく、A3+A4の英訳後配置・R0後Hard STOP Check除去・翻訳後Hard STOP Check除去の正式判断をユーザー確認待ちでSTOP。APPROVED_FOR_PRODUCTION/PRODUCTION_WIREDへは進めない。Production変更ゼロ。",
"有用/不要の最終ラベルは確定しない。下記の『Known/New』『束ね方』は機械的な提案で、ユーザー確認用。旧Hard STOP Checkを正解教師として扱わない。", "",
"## 0. 実施概要", "",
"- 11本(既定8テーマ + 既知例用の追加3本。INVENTORY_01.md)× A3/A4 = 22呼び出し。全22完走、全てattempts=1・valid JSON、再試行なし。",
"- Flagger: model `gpt-6.1-sol`(API応答のmodel欄の実測値: %s)/ reasoning effort=medium / ANTENNA-TRIAL-01と同一構成。最新モデル原則(PM_GOVERNANCE 25節)に沿う構成(ANTENNA-TRIAL-01と同一であること以外に新たな最新性の再確認はしていない)。" % ", ".join(models),
"- A3/A4 prompt: ANTENNA-TRIAL-01と**バイト一致**(A3 `9d995042...`、A4 `c87b95e5...`。英語注記追加なし = 差分ゼロ。EN_ADAPTATION_01.md)。強制TopNなし・0件許容・confidence閾値なし・A5/A6なし・再生成なし・STOPなし。",
"- 費用: 実測 JPY%.2f(見積中央値 JPY50.83、高位 JPY78.75、累計上限 JPY76.25。逸脱なし)。入力 %d tokens / 出力 %d tokens。1セル平均 JPY%.2f。" % (agg["cost_jpy"], usage_in, usage_out, agg["cost_jpy"] / 22),
"- 所在差異(要確認): ユーザー指示のOpenAI日本語R2と英語引用は別世代の稿。詳細 INVENTORY_01.md §2。『STOP稿』(U07, U08, X11)は完成記事ではない。", "",
"## 1. 記事別結果(Union = A3 ∪ A4、同一文は1行、typeが違えば併記)", ""]
for u in UN:
    uu = umap[u]; p = per[u]
    R += ["### %s %s — %s" % (u, uu["theme"], uu["route"]), "",
          "- English source: `%s`(%s)" % (uu["input_path"].split("post_en_trial_01/")[1], uu["status"]),
          "- A3 Flag: %d件 %s / A4 Flag: %d件 %s / Union: %d件 / A3∩A4 overlap: %d件 / 意味上の問題単位: %d件" % (len(p["a3"]), sorted(p["a3"], key=sk), len(p["a4"]), sorted(p["a4"], key=sk), len(p["union"]), len(p["overlap"]), len(p["bundles"])), ""]
    if not p["union"]:
        R += ["Flagなし(A3/A4とも0件)。", ""]; continue
    R += ["| 文ID / 対象文 | A3 type conf | A4 type conf | Related Fact | Reason(Flaggerのquestion、原文のまま日本語) | Known issue(提案) | New issue(提案) |", "|---|---|---|---|---|---|---|"]
    for s in p["union"]:
        ids = sorted(set((p["a3"].get(s) or {"fact_ids": []})["fact_ids"]) | set((p["a4"].get(s) or {"fact_ids": []})["fact_ids"]))
        k, note = KN[(u, s)]
        R.append("| %s: %s | %s | %s | %s | %s | %s | %s |" % (s, trunc(F[(3, u)]["sentences"][s], 150), cell(p["a3"].get(s)), cell(p["a4"].get(s)), ", ".join(ids) if ids else "(なし)", reason(u, s), (k + ": " + note) if k.startswith("Known") else "-", ("New: " + note) if k == "New" else "-"))
    R += [""]
    if any(len(b[1]) > 1 for b in p["bundles"]):
        R += ["束ね方(提案): " + " / ".join("【%s】= %s" % (n or "単独", ",".join(ss)) for n, ss in p["bundles"] if len(ss) > 1), ""]
R += ["## 2. 集計", "",
"| 指標 | 11本(U01-U08 + X09-X11) | 既定8本(U01-U08のみ) |", "|---|---|---|",
"| sentence-level Flag総数(A3+A4) | %d(A3 %d + A4 %d) | %d |" % (agg["sentence_level_total"], agg["a3"], agg["a4"], sum(len(per[u]["a3"]) + len(per[u]["a4"]) for u in core8)),
"| A3/A4 overlap(同一記事・同一文) | %d | %d |" % (agg["overlap"], sum(len(per[u]["overlap"]) for u in core8)),
"| Union総数(重複除去後) | %d | %d |" % (agg["union"], S8["union"]),
"| 意味上の問題単位に束ねた候補数 | %d | %d |" % (agg["semantic_units"], S8["units"]),
"| 1記事あたり平均 Union | %.2f | %.2f |" % (agg["avg_union_per_article_11"], agg["avg_union_core8"]),
"| 1記事あたり平均 問題単位 | %.2f | %.2f |" % (agg["avg_units_per_article_11"], agg["avg_units_core8"]), "",
"記事別: " + " / ".join("%s=A3 %d・A4 %d・Union %d・単位 %d" % (u, len(per[u]["a3"]), len(per[u]["a4"]), len(per[u]["union"]), len(per[u]["bundles"])) for u in UN),
"", "- A3のみ / A4のみ / 両方の内訳: A3のみ %d、A4のみ %d、両方 %d(Union %d)。" % (sum(len(set(per[u]["a3"]) - set(per[u]["a4"])) for u in UN), sum(len(set(per[u]["a4"]) - set(per[u]["a3"])) for u in UN), agg["overlap"], agg["union"]),
"- 0件の記事(A3/A4どちらも0): " + (", ".join(u for u in UN if not per[u]["union"]) or "なし") + "。A3が0件でA4が1件以上: " + (", ".join(u for u in UN if not per[u]["a3"] and per[u]["a4"]) or "なし") + "。",
"- 量産可能な水準かの判断はしない(ユーザー確認用)。参考として、既定8本の平均は1記事あたり約%.1f問題単位。" % agg["avg_units_core8"], ""]
a3s7, a4s7 = per["X11"]["a3"]["s7"], per["X11"]["a4"]["s7"]
R += ["## 3. OpenAI actor drift(専用節)", "",
"対象: **X11(B1回復前のSTOP稿、`They also say the models' output copied or put articles together in new ways, and removed copyright management information.` = s7)**。対照: U07(B1回復後の最終STOP稿、s11『They further accuse OpenAI of removing copyright management information.』= 主体OpenAI明示)。", "",
"| | A3 | A4 |", "|---|---|---|",
"| X11 s7を拾ったか | **拾った**(%s、confidence %.2f、Fact %s) | **拾った**(%s、confidence %.2f、Fact %s) |" % (a3s7["type"], a3s7["confidence"], a3s7["fact_ids"], a4s7["type"], a4s7["confidence"], a4s7["fact_ids"]),
"| 拾った文 | s7(上記英文全文) | s7(同) |", "| actor/主体の問題として認識したか | **認識した**。理由欄原文: 「%s」 | **認識した**。理由欄原文: 「%s」 |" % (a3s7["question"], a4s7["question"]), "",
"- 両方とも、台帳F4が『OpenAIが著作権管理情報を除去したと主張』と述べているのに英文がthe models' outputを主体に読める、という**OpenAI→モデル出力の主体入替**を文言どおりに指摘している(type=主体対象入替)。この稿でFlaggerが付けた最高水準のconfidence(0.94〜0.96)。",
"- U07(主体OpenAI明示の稿)のs11はA3/A4とも**Flagなし**(= actor driftが無い稿を過剰に拾っていない)。U07でFlagされたのは s5(A3 .62/A4 .65: GPTなど全般への範囲拡張)、s1(A4 .30: 見出しのAI訴訟一般への拡張。旧Check STOPの原因)、s21、s22。",
"- 起源判定への疑義: ユーザー指摘『日本語R2には明示的にOpenAIがあるのに旧Checkはorigin=ja_source』は、日本語R2が世代違い(B1回復後 `ja_writer/revision2.md` にはOpenAI明示、X11の元の `ja_writer_prev_b1/revision2.md` には『さらに、モデルの出力が記事を複製したり、組み直したりしたほか、著作権管理情報も取り除いたとしています』で主語なし)であることで説明がつく可能性がある(ファイル内容の照合結果。ただしCheckerの判定過程そのものは再検証していない)。", ""]
a3s25, a4s25 = per["U08"]["a3"]["s25"], per["U08"]["a4"]["s25"]
R += ["## 4. Semiconductor境界例(U08 s25。過剰Flagかの最終判定はしない)", "",
"- 該当文(s25は2文が1IDに結合): 「But even if the company's forecast appears beside that line, we cannot say, “AI demand is strong, so revenue will be about $34.8 billion.” **This announcement alone does not explain how the two are connected.**」",
"- A3: 拾った(%s、confidence **%.2f**、Fact %s)。理由: 「%s」" % (a3s25["type"], a3s25["confidence"], a3s25["fact_ids"], a3s25["question"]),
"- A4: 拾った(%s、confidence **%.2f**、Fact %s)。理由: 「%s」" % (a4s25["type"], a4s25["confidence"], a4s25["fact_ids"], a4s25["question"]),
"- U08でFlagされたのはこのs25のみ(両レベルとも1件)。他の文は過剰にFlagされていない。Flaggerは『STOP/Rewriteではなく確認箇所を示すだけ』の位置づけなので、このFlagはHuman Review候補1件(A3 0.68/A4 0.35)として表示される。confidence閾値で除外するか、1件程度は許容するかはユーザー判断(Claudeは閾値を追加していない)。", ""]
R += ["## 5. 旧Hard STOP Check指摘との対応(旧Checkを正解教師としない。参照のみ)", "",
"| 旧Check既知例 | 該当稿 | 本文に実在 | A3 | A4 |", "|---|---|---|---|---|",
"| OpenAI actor drift | X11 s7 | 実在 | 拾った(.96) | 拾った(.94) |",
"| OpenAI 見出しscope拡張(STOP直接原因) | U07 s1 | 実在 | 拾わない | 拾った(.30) |",
"| Semiconductor 説明不在の断定(境界例) | U08 s25 | 実在 | 拾った(.68) | 拾った(.35) |",
"| BYD In One Line条件落ち | U05 s27 | 実在 | 拾わない(隣接の見出しs1で『極端な場合』条件に言及して.35) | 拾わない |",
"| Hormuz Brent→oil prices | X09 s2, s13 | X09に実在(U02には不在) | **拾わない** | **拾わない**(X09では別文s8/s10) |",
"| Space『blow up Earth』能力否定 | X10 s5 | X10に実在(U03には不在) | 拾わない | 拾った(.30) |",
"| Space『capabilities』不在断定(旧Check b1b_prev_b1 attempt1相当) | U03 s33, s13 | 実在 | 拾った(.68, .70) | 拾った(.35, .35) |",
"| Space ロシア破壊の複数形(a2稿の旧Check指摘) | U03 s17 | b1b稿に実在 | 拾った(.76) | 拾った(.40) |", "",
"**見逃し(Flagされなかった既知例)**: Hormuz『oil prices』への一般化(X09 s2, s13)はA3/A4どちらもFlagしなかった。BYD In One Line文(U05 s27)そのものも未Flag。Space blow-up Earth(X10 s5)はA3が拾わなかった。**100% recallを要求するTrialではない**が、事実として記録する。", ""]
R += ["## 6. 過剰Flag候補(ユーザー確認用。確定しない)", "",
"- U08 s25(境界例。上記)。",
"- 低確信度でFactなし(台帳に対応記述のない一般的説明・比喩): U05 s4(.28)、U06 s16(.20)、U07 s22(.20)、X09 s10(.28)。いずれもA4のみ(A4レベルは『台帳に対応記述がない事実の主張』を拾う設計)。",
"- 文分割アーティファクトの疑い: X09 s8(A3 .65/A4 .83。『ensuring U.S.』で切れた文を、安全確保の対象が米国自体と読めると指摘)、U03 s5(『while the U.S.』で切れた文)。分割ミスが理由の一部の可能性がある(確定ではない)。",
"- 『will go from…』の価格改定文(U06 s8, s9)や『a mini bag』(U04 s7, s15)など、台帳の限定条件(適用日・特定の形状)を超えた一般化という指摘は、人間が見る価値があるかが主観的。", "",
"## 7. 新規Flag候補(旧Check指摘になかった。ユーザー確認用。確定しない)", "",
"- U05 s6(A3 .88/A4 .94): 『A recall notice … named 183,211 cars』。台帳BYD-RECALL-01は『2件の公告の台数を合算した数』。単数公告と読める点。高confidence・Factあり。",
"- U03 s17(A3 .76): ロシアのCOSMOS 1408(1基)を『satellites』複数形に広げた点(a2稿では旧Checkが指摘していたがb1b稿では旧Check未指摘)。",
"- U06 s17・s21: 適用日・第三者請求パートナー条件の落ち(台帳F05/F06)。",
"- U07 s5, s21 / X11 s4, s17, s25: 破棄請求対象の範囲、OpenAIの応答状況の広げ。", "",
"## 8. 参考: 旧Hard STOP Checkを外した場合の実務的価値", "",
"- 旧CheckはU03(最終稿)とU05(最終稿)をCOMPLIANTにしたが、A3/A4はU03に5文、U05に2文のHuman Review候補を出した。逆に旧CheckがSTOPさせたU07・U08・X11も、A3/A4は候補として表面化した(U07のSTOP理由はA4のみ、U08は両方、X11のactor driftは両方)。",
"- ただし旧Checkが指摘した全ての問題をA3/A4が拾ったわけではない(上記見逃し)。今回は英訳後配置の初期観察であり、Production採否の根拠にはしない。", "",
"## 9. 条件同一性・信頼性", "",
"- 全22セル同一モデル・同一effort・同一prompt(A3, A4各1つ)・同一splitter・完全台帳(8テーマ全PASS)。cap/retry発動なし。応答JSONは全て有効(valid=True、attempts=1)。",
"- 1回ずつの実行であり、同一入力の再実行による再現性(ノイズ幅)は今回測っていない。confidence値・件数は1サンプル。",
"- 文分割は既存splitterの限界(閉じ引用符直後で分割されない/『U.S.』で分割)がそのまま現れる。文IDは対象文の厳密な単位ではない場合がある。", "",
"## 10. 費用・model_id・routing evidence", "",
"- 実測 JPY%.2f / %d呼び出し(`cost_ledger_post_en_01.jsonl`、`cost_estimate_post_en_01.json`)。見積中央 JPY50.83に対し %.1f%%。" % (agg["cost_jpy"], 22, agg["cost_jpy"] / 50.83 * 100),
"- API応答の `model`: `gpt-6.1-sol`(全22呼び出し。`flags/*/*.json` の `model_ids`、`logs/*_raw.jsonl` の `model_id`)。レイテンシ等の追加routing情報は取っていない。", "",
"## 11. 未決事項・USER_DECISION_REQUIRED", "",
"1. A3+A4の英訳後・音声化前配置の採否(未VALIDATED。Production wiring未実施)。2. R0後Hard STOP Check除去の採否。3. 翻訳後Hard STOP Check除去の採否。4. 確認すべきFlagの範囲(confidence閾値を設けるか。今回は追加していない)。5. 文分割の改善要否(英語稿の閉じ引用符・略語)。6. OpenAI世代差(INVENTORY_01.md §2)の認識確認。7. 見逃し既知例(Hormuz oil prices、BYD In One Line文)をどう扱うか。8. 『新Writer+Production Checkerなし+A3/A4+Human Review』運用コンセプトはAPPROVED_FOR_PRODUCTION・未PRODUCTION_WIREDのまま(closeしない)。"]
open(os.path.join(HERE, "RESULT_01.md"), "w", encoding="utf-8").write("\n".join(R) + "\n")
H = ["# HUMAN_REVIEW_POST_EN_01: ユーザー確認用一覧(記事→Union Flag→該当英文/対応Fact(日本語台帳原文)/理由/Known or New)", "",
"Risk FlaggerはCheckerではない(STOPしない・PASS/FAILしない・自動Rewriteしない)。『人間が見る場所』の候補一覧。有用/不要の判断は未確定(ユーザー確認用)。STOP稿(U07/U08/X11)は完成記事ではない。Hormuz X09/Space X10/OpenAI X11はB1回復前の旧稿(既知例用に追加)。", ""]
for u in UN:
    p = per[u]; uu = umap[u]
    H += ["## %s %s(%s)" % (u, uu["theme"], uu["status"][:40]), "", "Union %d件 / 問題単位 %d件。" % (len(p["union"]), len(p["bundles"])), ""]
    if not p["union"]:
        H += ["Flagなし。", ""]; continue
    for s in p["union"]:
        a3, a4 = p["a3"].get(s), p["a4"].get(s)
        ids = sorted(set((a3 or {"fact_ids": []})["fact_ids"]) | set((a4 or {"fact_ids": []})["fact_ids"]))
        k, note = KN[(u, s)]
        H += ["### %s %s(A3 %s / A4 %s)" % (u, s, ("%s %.2f" % (a3["type"], a3["confidence"])) if a3 else "なし", ("%s %.2f" % (a4["type"], a4["confidence"])) if a4 else "なし"), "",
              "- 該当英文: " + F[(3, u)]["sentences"][s],
              "- 対応Fact(日本語台帳原文): " + (" / ".join("**%s** %s" % (i, F[(3, u)]["facts"][i].replace("\n", " ")[:600]) for i in ids) if ids else "(Flaggerが対応Factを特定していない = 台帳にない主張の疑い)"),
              "- 理由(A3): " + (a3["question"] if a3 else "-"), "- 理由(A4): " + (a4["question"] if a4 else "-"),
              "- %s" % (("Known issue(提案): " + k + " — " + note) if k.startswith("Known") else ("New issue(提案): " + note)), ""]
open(os.path.join(HERE, "HUMAN_REVIEW_POST_EN_01.md"), "w", encoding="utf-8").write("\n".join(H) + "\n")
print(json.dumps({k: v for k, v in agg.items() if k not in ("attempts", "valid", "per_article")}, ensure_ascii=False))
print(agg["per_article"])
