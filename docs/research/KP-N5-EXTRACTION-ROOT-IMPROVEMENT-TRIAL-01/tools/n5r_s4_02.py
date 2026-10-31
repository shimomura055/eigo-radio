"""Trial専用。TRIAL_PLAN_02 §7 S4(価値判定、アーム名・新規/既存を伏せた混在リスト)。
build  <tag> <eval_json_name> <arm,arm,...> : 対象アームの入場項目+A0最終7件(同一反復)をcase別に集め、固定seedでshuffle。blind=ev02/s4_blind_<tag>.json(伏せ)、key=ev02/s4_key_<tag>.json
judgeB <tag> <proc_label>                  : 独立promptのLLM(判定者B)でYES/NO/UNSURE。ev02/s4_judgeB_<tag>.json
score  <tag> <arm,arm,...>                 : 判定者A(ev02/s4_judgeA_<tag>.json: {id:{v,why}})とBを統合し、アーム別の価値率を算出
"""
import sys, os, json, random, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import n5r_lib_02 as L
n5 = L.n5
MODE, TAG = sys.argv[1], sys.argv[2]
SEED = 20261031

if MODE == "build":
    ev = json.load(open(f"{L.EV}/{sys.argv[3]}.json", encoding="utf-8")); arms = sys.argv[4].split(",")
    items = {}
    for r in ev["rows"]:
        if "final" not in r: continue
        ents = set(r.get("entrants", [])) if r["arm"] != "A0" else {c["span"] for c in r["final"]}
        if r["arm"] not in arms + ["A0"]: continue
        for c in r["final"]:
            if r["arm"] != "A0" and c["span"] not in ents: continue
            k = (r["case"], L.norm_key(c["span"]))
            it = items.setdefault(k, {"case": r["case"], "span": c["span"], "form": c["form"], "gloss": c["gloss"], "members": []})
            it["members"].append([r["arm"], r["rep"]])
    fx = L.fixture()
    for it in items.values():
        sents = [s for s in fx["cases"][it["case"]]["text"].replace("\n", " ").split(". ") if n5.span_in_text(it["span"], s)]
        it["sentence"] = (sents[0] if sents else "")
    lst = list(items.values()); random.Random(SEED).shuffle(lst)
    arts = {c: f"ART{chr(65 + i)}" for i, c in enumerate(sorted({x["case"] for x in lst}))}
    blind, key = [], {}
    for i, it in enumerate(lst, 1):
        blind.append({"id": i, "article": arts[it["case"]], "span": it["span"], "display_form": it["form"], "gloss_ja": it["gloss"], "sentence": it["sentence"]})
        key[i] = {"case": it["case"], "span": it["span"], "members": it["members"]}
    json.dump(blind, open(f"{L.EV}/s4_blind_{TAG}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(key, open(f"{L.EV}/s4_key_{TAG}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("blind items", len(blind))

elif MODE == "judgeB":
    L.install_log(sys.argv[3]); n5.preflight()
    blind = json.load(open(f"{L.EV}/s4_blind_{TAG}.json", encoding="utf-8")); key = json.load(open(f"{L.EV}/s4_key_{TAG}.json", encoding="utf-8"))
    fx = L.fixture(); out = {}
    SCH = {"name": "kp_valuejudge", "schema": {"type": "object", "additionalProperties": False, "required": ["j"], "properties": {"j": {"type": "array", "items": {
        "type": "object", "additionalProperties": False, "required": ["id", "verdict", "why"], "properties": {"id": {"type": "integer"}, "verdict": {"type": "string", "enum": ["YES", "NO", "UNSURE"]}, "why": {"type": "string"}}}}}}}
    for art in sorted({b["article"] for b in blind}):
        bs = [b for b in blind if b["article"] == art]; case = key[str(bs[0]["id"])]["case"]; text = fx["cases"][case]["text"]
        ctx = L.make_ctx(case, sys.argv[3], f"s4B_{art}")
        lines = [f"{b['id']}. {b['span']}  (学習用の形: {b['display_form']})\n   文: {b['sentence']}" for b in bs]
        pr = ("あなたは英語学習用の表現リストを検収する第2の判定者です。以下の各項目が、この記事から『ひと塊で覚える価値のある学習項目』として妥当かを判定してください。\n"
              "YES=次の判定テストT1〜T4をすべて通り、学習者が塊として覚える価値がある / NO=1つでも当てはまれば塊でない(自由な組合せ・字面どおり) / UNSURE=迷う。\n"
              "T1 辞書テスト: 学習者用英英辞書の見出し・句動詞項目・連語欄に載りそうか。載らなければNO。\nT2 置換テスト: 構成語の1つを同類の別の語に替えても同じ型で自然に成り立つならNO。\n"
              "T3 予測テスト: すべての語を知っていれば、意味も組合せ(この動詞にこの前置詞/粒子)も自力で推測・再現できるならNO。\nT4 理由テスト: なぜひと塊で覚える価値があるかを具体的に言えなければNO。\n"
              "難易度が易しいことだけを理由にNOとしない(基本語だけの句動詞でも塊ならYES)。題名・見出しの句は、本文内の用法として塊かで判定する。各項目のidとverdictと理由(30字以内)だけ返す。\n\n【判定対象】\n"
              + "\n".join(lines) + L.BODY + text)
        L.guard(0.8)
        with L.cl.logging_context("N5R2", f"s4B_{art}"):
            o, m = n5.call_llm("sel", pr, SCH, ctx, label="N5R2_S4B")
        for x in o["j"]:
            out[str(x["id"])] = {"v": x["verdict"], "why": x["why"]}
        print(art, len(bs), "cost", m.get("cost_jpy"), "spent", round(L.spent(), 2))
    json.dump(out, open(f"{L.EV}/s4_judgeB_{TAG}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

else:  # score
    arms = sys.argv[3].split(",")
    key = json.load(open(f"{L.EV}/s4_key_{TAG}.json", encoding="utf-8"))
    A = json.load(open(f"{L.EV}/s4_judgeA_{TAG}.json", encoding="utf-8")); B = json.load(open(f"{L.EV}/s4_judgeB_{TAG}.json", encoding="utf-8"))
    ids = sorted(key, key=int)
    agree = sum(1 for i in ids if A[i]["v"] == B[i]["v"]) / len(ids)
    res = {"n_items": len(ids), "AB_agreement": round(agree, 4), "disagree": [{"id": i, "span": key[i]["span"], "A": A[i], "B": B[i]} for i in ids if A[i]["v"] != B[i]["v"]], "unsure_A": [i for i in ids if A[i]["v"] == "UNSURE"], "arms": {}}
    def rate(J, sel):
        return round(sum(1 for i in sel if J[i]["v"] == "YES") / len(sel), 4) if sel else None
    # A0の最終7件=A0 member。アームの入場項目=当該アームのmember(A0以外)。
    a0 = [i for i in ids if any(m[0] == "A0" for m in key[i]["members"])]
    res["A0_final_value"] = {"A": rate(A, a0), "B": rate(B, a0), "n": len(a0)}
    for arm in arms:
        ent = [i for i in ids if any(m[0] == arm and ["A0", m[1]] not in key[i]["members"] for m in key[i]["members"])]
        res["arms"][arm] = {"n_entrants": len(ent), "value_A": rate(A, ent), "value_B": rate(B, ent), "ge_threshold_A": (rate(A, ent) is not None and rate(A, a0) is not None and rate(A, ent) >= rate(A, a0) - 0.10),
                            "ge_threshold_B": (rate(B, ent) is not None and rate(B, a0) is not None and rate(B, ent) >= rate(B, a0) - 0.10), "entrants": [{"id": i, "span": key[i]["span"], "A": A[i]["v"], "B": B[i]["v"]} for i in ent]}
    json.dump(res, open(f"{L.EV}/s4_score_{TAG}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k not in ("disagree",)}, ensure_ascii=False, indent=1)[:4000]); print("disagree", len(res["disagree"]))
