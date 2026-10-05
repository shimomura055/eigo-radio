# -*- coding: utf-8 -*-
# OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 委任_03: Stage 1再設計案の0円事前評価(既存データのみ、API呼出なし、実装なし)。
# 案4の決定論pre-checkは「設計レベルの簡易模擬」(本実装ではない)。限界はmd/jsonに明記。
import json, os, sys, io, re, glob, math
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
os.chdir(ROOT); sys.path.insert(0, ROOT)
import er052_open233_stage1_phase1_recall_check_01 as P
import er052_open233_self_recovery_precheck_01 as PC
runner = P.runner
A = "er052_output/open233_stage1_phase1_recall_check_01/a_frozen_fresh_01"
OUTD = "er052_output/open233_kpi_recovery_02_offline_01"
REP30 = P.REP30
INSA = P.instances_a()
SC_SUBS = {  # 既存SAFETY_CRITICAL_CLAIM_DEFS(期待BLOCKINGのみ)から。定義は変更しない
    d["sub_id"]: (k, d) for k, ds in runner.SAFETY_CRITICAL_CLAIM_DEFS.items() for d in ds
    if d.get("expected", "BLOCKING") == "BLOCKING"}


def sentences(text):
    out = []
    for para in re.split(r"\n+", text or ""):
        para = para.strip()
        if not para:
            continue
        if para.startswith("#"):
            continue  # 見出しは候補化しない(本文のみ)。見出し内容は文として扱わない簡易仕様
        for s in re.split(r"(?<=[.!?])\s+", para):
            if len(s.strip()) > 3:
                out.append(s.strip())
    return out


def norm(s):
    return re.sub(r"\s+", " ", (s or "").lower().replace("’", "'").replace("“", '"').replace("”", '"')).strip()


def gold_sentence_test(inst, fx):
    """gold文の判定関数群: (label, 判定(sentence)->bool)。定義は既存DEFS/V0記録の再利用のみ。"""
    gs = []
    for sub, (k, d) in SC_SUBS.items():
        if k == inst:
            pat = d.get("text_pattern")
            gs.append((sub, d["related_fact_id"],
                       (lambda s, pat=pat, sub_=d["text_substring"]: bool(re.search(pat, s, re.I)) if pat else sub_.lower() in s.lower())))
    if inst == "bgroup_B2_hormuz":  # HF-011(SC定義外のB群既知重大): V0記録の該当claim
        for dv in P.majors(fx.get("baseline_parsed")):
            c = norm(dv.get("claim_in_article"))[:60]
            gs.append(("HF-011", dv.get("related_fact_id") or "HF-011", (lambda s, c=c: norm(s).startswith(c) or c in norm(s))))
    return gs


# ---- 案4の簡易模擬: 6カテゴリの英語側マーカーと日本語側対応語(設計レベル、約40語の小辞書) ----
CAUS = r"\b(so|because|therefore|thus|as a result|led to|lead to|leading to|caused?|due to|thanks to|since|which is why|result(?:ed)? in|driven by|triggered|prompted|behind)\b"
NEG = r"\b(not|no|never|none|neither|nor|without|cannot|hardly|failed to)\b|n't|n’t"
COMP = r"\b(more|less|fewer|higher|lower|larger|smaller|greater|than|increase[sd]?|decrease[sd]?|rose|fell|dropped|grew|rise|fall|rebound\w*|recover\w*|pulled back|put back|rolled? back|restor\w+|raised|cut|doubl\w+|halv\w+|up|down)\b"
TIME_W = r"\b(temporarily|currently|now|still|already|then|until|before|after|later|earlier|yesterday|today|last (?:week|month|year)|during|while)\b"
MONTHS = "january|february|march|april|may|june|july|august|september|october|november|december"
DATE_RE = r"\b(?:%s)\.?\s+\d{1,2}\b|\b\d{4}\b|\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b" % MONTHS
NUMW = r"\b(one|two|three|four|five|six|seven|eight|nine|ten|half|third|quarter|fifth|dozen|hundred|thousand|million|billion|percent|most|majority|all|some|many|few|every|only|both)\b"
ACTW = r"\b(staff|workers?|humans?|person|people|users?|employees?|contractors?|company|president|executives?|officials?|government|agents?|vice president|team|leaders?|customers?)\b"
JP_NEG = r"ない|ず|なかった|せず|未|不|ありません|なし|否定|いない|できない"
JP_CAUS = r"ため|ので|により|によって|受け|背景|理由|ことで|原因|結果|から|を受けて"
JP_COMP = r"増|減|上|下|高|低|より|以上|以下|拡大|縮小|回復|撤回|ロールバック|戻|倍|割|引き上げ|引き下げ|置き換え"
JP_TIME = r"当面|一時|現在|まだ|すでに|現時点|当時|以前|以後|まで|時点|同日|後|前"
ACT_JP = {"staff": "スタッフ", "worker": "スタッフ|従業員|作業|契約", "human": "人間|人", "person": "人間|人", "people": "人",
          "user": "ユーザー", "employee": "従業員|社員", "contractor": "契約", "company": "企業|会社|Meta", "president": "大統領",
          "executive": "副社長|幹部|役員", "official": "当局|当局者|政府|高官", "government": "政府", "agent": "エージェント",
          "vice president": "副社長", "team": "チーム", "leader": "指導者|首脳", "customer": "顧客|ユーザー"}
CONCEPT = {"feature": "機能", "call": "電話", "plan": "案|計画", "fee": "料", "charge": "料", "price": "価格|原油", "oil": "原油",
           "chart": "チャート|価格|原油", "strait": "海峡", "tanker": "タンカー", "blockade": "封鎖", "deal": "協議|合意|取引",
           "talks": "協議", "trade": "貿易", "invest": "投資", "repay": "償還|返", "money": "費用|料", "cost": "費用|料",
           "test": "テスト|実験", "ai": "AI", "exchange": "やり取り", "disclos": "開示", "rollback": "ロールバック"}


def jp_hit(pat, text):
    return bool(re.search(pat, text or ""))


def fact_text(f):
    return " ".join(str(f.get(k) or "") for k in ("claim", "scope", "conditions", "numeric_value", "date_or_period", "notes_for_writer"))


def anchors(sent, fact):
    """日英alignmentの簡易アンカー: 数値、Latin固有名、概念辞書。共有したアンカー集合を返す。"""
    ft = fact_text(fact)
    out = set()
    for n in re.findall(r"\d+(?:\.\d+)?", sent):
        if re.search(r"(?<![\d.])" + re.escape(n) + r"(?![\d])", ft):
            out.add("num:" + n)
    ftl = ft.lower()
    for w in set(re.findall(r"[A-Za-z][A-Za-z0-9\-]{2,}", ft)):
        if re.search(r"\b" + re.escape(w.lower()) + r"\b", sent.lower()) and w.lower() not in ("the", "and", "http", "https", "www", "com"):
            out.add("lat:" + w.lower())
    for en, jp in CONCEPT.items():
        if en in sent.lower() and jp_hit(jp, ft):
            out.add("cn:" + en)
    for en, jp in ACT_JP.items():
        if re.search(r"\b" + en + r"s?\b", sent.lower()) and jp_hit(jp, ft):
            out.add("act:" + en)
    return out


def triggers(sent):
    t = {}
    if re.search(CAUS, sent, re.I): t["causal"] = True
    if re.search(NEG, sent, re.I): t["negation"] = True
    if re.search(COMP, sent, re.I): t["comparison"] = True
    if re.search(TIME_W, sent, re.I) or re.search(DATE_RE, sent, re.I): t["time"] = True
    if re.search(r"\d", sent) or re.search(NUMW, sent, re.I): t["number"] = True
    if re.search(ACTW, sent, re.I): t["actor"] = True
    return t


def mismatch(cat, sent, F):
    """Fが空(alignment失敗)なら fail-closed で候補化(True)。Fあり: カテゴリ別に不一致を判定。"""
    if not F:
        return True
    ft = " ".join(fact_text(f) for f in F)
    if cat == "causal":
        return not (any(str(f.get("causal_strength") or "").startswith("CAUSAL_STATED") for f in F) or jp_hit(JP_CAUS, ft))
    if cat == "negation":
        return not jp_hit(JP_NEG, ft)
    if cat == "comparison":
        return not jp_hit(JP_COMP, ft)
    if cat == "time":
        md = re.findall(r"\b(%s)\.?\s+(\d{1,2})\b" % MONTHS, sent, re.I)
        for m, d in md:
            mi = MONTHS.split("|").index(m.lower()) + 1
            if not re.search(r"%d月%s日|%d月 ?%s\b|-%02d-%02d" % (mi, d, mi, d, mi, int(d)), ft):
                return True
        if re.search(TIME_W, sent, re.I) and not jp_hit(JP_TIME, ft):
            return True
        return False
    if cat == "number":
        nums = re.findall(r"\d+(?:\.\d+)?", sent)
        fn = re.findall(r"\d+(?:\.\d+)?", ft)
        return any(not any(abs(float(a) - float(b)) <= 0.05 * max(float(b), 1) for b in fn) for a in nums if len(a) <= 3) if nums else False
    if cat == "actor":
        acts = [en for en in ACT_JP if re.search(r"\b" + en + r"s?\b", sent.lower())]
        return any(not jp_hit(ACT_JP[en], ft) for en in acts)
    return False


def sim_precheck(fx):
    facts = PC.parse_ledger_text(fx["ledger_text"])
    rows = []
    for s in sentences(fx["article_text"]):
        anc = [(f, anchors(s, f)) for f in facts]
        al = [f for f, a in anc if a]
        best = max([len(a) for _, a in anc] or [0])
        al2 = [f for f, a in anc if best >= 2 and len(a) == best]  # L2: 最多アンカーのfactのみ(厳格alignment)
        tr = triggers(s)
        l0 = sorted(tr)
        l1 = sorted(c for c in tr if mismatch(c, s, al))
        l2 = sorted(c for c in tr if mismatch(c, s, al2))
        rows.append({"sentence": s, "aligned_fact_ids": [f["fact_id"] for f in al], "L0_cats": l0, "L1_cats": l1,
                     "L2_cats": l2, "aligned_n": len(al), "L2_aligned_ids": [f["fact_id"] for f in al2]})
    return facts, rows


def all_instances():
    d = {k: fx for k, (fx, _) in INSA.items()}
    extra = {}
    try:
        for k, (fx, vp) in P.instances().items():
            if k not in d and fx.get("article_text") and fx.get("ledger_text"):
                extra[k] = fx
                v0, _ = P.v0_record(fx, vp)
                if v0 and not fx.get("baseline_parsed"):
                    fx = dict(fx, baseline_parsed=v0)
                    extra[k] = fx
    except Exception as e:  # noqa
        print("extra instances unavailable:", e)
    return d, extra


def evaluate_instance(k, fx, kind):
    facts, rows = sim_precheck(fx)
    gold = []
    for sub, fid, test in gold_sentence_test(k, fx):
        hit_s = [r for r in rows if test(r["sentence"])]
        g = {"sub": sub, "fact_id": fid, "sentence_found": bool(hit_s)}
        if hit_s:
            r = hit_s[0]
            g.update({"L0_cats": r["L0_cats"], "L1_cats": r["L1_cats"], "in_L0_candidates": bool(r["L0_cats"]),
                      "in_L1_candidates": bool(r["L1_cats"]), "L2_cats": r["L2_cats"], "in_L2_candidates": bool(r["L2_cats"]),
                      "L2_aligned_ids": r["L2_aligned_ids"], "L2_aligned_to_related": fid in r["L2_aligned_ids"], "aligned_to_related_fact": fid in r["aligned_fact_ids"],
                      "n_aligned_facts": r["aligned_n"], "sentence": r["sentence"][:140]})
        gold.append(g)
    try:
        real = PC.run_precheck(fx["ledger_text"], fx["article_text"])
    except Exception as e:  # noqa
        real = [{"error": str(e)}]
    real_n = len([x for x in real if "error" not in x])
    pairs = sum(r["aligned_n"] for r in rows)
    return {"kind": kind, "n_facts": len(facts), "n_sentences": len(rows),
            "L0_candidate_sentences": sum(1 for r in rows if r["L0_cats"]),
            "L1_candidate_sentences": sum(1 for r in rows if r["L1_cats"]),
            "L2_candidate_sentences": sum(1 for r in rows if r["L2_cats"]),
            "L1_cat_counts": {c: sum(1 for r in rows if c in r["L1_cats"]) for c in ("actor", "number", "negation", "comparison", "time", "causal")},
            "pairs_L2": sum(max(1, len(r["L2_aligned_ids"])) for r in rows),
            "rows": rows,
            "unaligned_sentences": sum(1 for r in rows if r["aligned_n"] == 0),
            "aligned_pairs_fact_x_sentence": pairs,
            "existing_run_precheck_candidates": real_n,
            "existing_run_precheck_kinds": sorted({x.get("kind") or x.get("type") or x.get("flag") or "?" for x in real if "error" not in x}),
            "gold": gold}


# ---- 実測データの読込(A構成fresh 32 run、rep30 Stage 2、案2の既存集計) ----
RATES = P.RATES["gpt-6-luna"]
USD_JPY = P.USD_JPY


def cost_tok(inp, out):
    return (inp / 1e6 * RATES[0] + out / 1e6 * RATES[2]) * USD_JPY


def fresh_runs(k):
    res = []
    for i in range(1, 5):
        f = "%s/%s/run_%d.json" % (A, k, i)
        if os.path.exists(f):
            res.append(json.load(open(f, encoding="utf8")))
    return res


def stage2_rep30():
    """rep30のcycle1 Stage 2(body/hook/S1)の費用をinstance別に集計し、Stage 1 MAJOR件数との関係を返す。"""
    rows = []
    for f in glob.glob(REP30 + "/instances_s*/*.json"):
        x = json.load(open(f, encoding="utf8"))
        s2 = sum(c.get("cost_jpy", 0) or 0 for c in x["call_log"] if "_c1_" in c.get("label", "") and c.get("recovery_stage") == "stage2_second_judge")
        nmaj = sum(1 for d in x["all_deviations_raw"]["stage1"] if d.get("severity") == "MAJOR")
        if s2 > 0:
            rows.append({"instance": x["instance_id"], "stage1_major_n": nmaj, "stage2_c1_cost_jpy": round(s2, 4)})
    return rows


def linfit(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx if sxx else 0.0
    a = my - b * mx
    sy = sum((y - my) ** 2 for y in ys)
    r = (sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(sxx * sy)) if sxx and sy else 0.0
    return a, b, r


def nonsc_coverage(k, ev):
    """frozen(rep30)が拾いfresh全runが拾わなかったMAJOR claim(B4/B1の非SC)の文が、案4模擬の候補に入るか。"""
    out = []
    fz = P.rep30_stage1(k)
    if not fz:
        return out
    fr = [P.majors(r["parsed"]) for r in fresh_runs(k)]
    for d in fz[0]:
        if d.get("severity") != "MAJOR":
            continue
        if any(P.same_claim(d, e) for run in fr for e in run):
            continue
        c = norm(d.get("claim_in_article"))[:50]
        row = next((r for r in ev["rows"] if c and c in norm(r["sentence"])), None)
        out.append({"related_fact_id": d.get("related_fact_id"), "claim": (d.get("claim_in_article") or "")[:90],
                    "sentence_located": bool(row), "in_L0": bool(row and row["L0_cats"]), "in_L2": bool(row and row["L2_cats"])})
    return out


def main():
    d, extra = all_instances()
    ev = {k: evaluate_instance(k, fx, "A") for k, fx in d.items()}
    ev.update({k: evaluate_instance(k, fx, "er009_synthetic") for k, fx in extra.items()})
    gold = [dict(instance=k, **g) for k, e in ev.items() for g in e["gold"]]
    ng = len(gold)
    summ = {"n_gold": ng, "found": sum(g["sentence_found"] for g in gold)}
    for lv in ("L0", "L1", "L2"):
        summ["gold_in_%s" % lv] = sum(bool(g.get("in_%s_candidates" % lv)) for g in gold)
    summ["gold_aligned_loose"] = sum(bool(g.get("aligned_to_related_fact")) for g in gold)
    summ["gold_aligned_L2"] = sum(bool(g.get("L2_aligned_to_related")) for g in gold)
    negs = [k for k in P.A_NEG]
    negs_s = {}
    for lv in ("L0", "L1", "L2"):
        key = lv + "_candidate_sentences"
        v = [ev[k][key] for k in negs]
        negs_s[lv] = {"per_instance": dict(zip(negs, v)), "mean": round(sum(v) / len(v), 2),
                      "instances_with_ge1": sum(1 for x in v if x >= 1), "n": len(v),
                      "mean_sentences": round(sum(ev[k]["n_sentences"] for k in negs) / len(negs), 1)}
    nonsc = {k: nonsc_coverage(k, ev[k]) for k in ("bgroup_B4", "bgroup_B1")}
    real_total = sum(e["existing_run_precheck_candidates"] for e in ev.values())
    return d, extra, ev, gold, summ, negs_s, nonsc, real_total


def compute_costs(d, ev, negs):
    per = {}
    for k, fx in d.items():
        rr = fresh_runs(k)
        if not rr:
            continue
        per[k] = {"in": sum(r["usage"]["input_tokens"] for r in rr) / len(rr), "out": sum(r["usage"]["output_tokens"] for r in rr) / len(rr),
                  "cost": sum(r["cost_jpy"] for r in rr) / len(rr), "lc": len(fx["ledger_text"]), "ac": len(fx["article_text"]),
                  "nf": ev[k]["n_facts"], "ns": ev[k]["n_sentences"], "nrun": len(rr)}
    allc = [r["cost_jpy"] for k in per for r in fresh_runs(k)]
    a, b, rr_ = linfit([v["lc"] + v["ac"] for v in per.values()], [v["in"] for v in per.values()])
    out = {"A_single_mean_cost_jpy": round(sum(allc) / len(allc), 4), "n_runs": len(allc), "input_fit": {"a": round(a, 1), "b_per_char": round(b, 4), "r": round(rr_, 3)}}
    mean = lambda f: sum(f(v) for v in per.values()) / len(per)
    out["A_mean_in_tokens"] = round(mean(lambda v: v["in"])); out["A_mean_out_tokens"] = round(mean(lambda v: v["out"]))
    # 案5: fact群batch(g facts/call)。入力=a+b*(article+ledger*g/nf)、出力=out*(g/nf)*kappa
    for g in (3, 5):
        for kp in (1.0, 1.5):
            cs = [sum(cost_tok(a + b * (v["ac"] + v["lc"] * min(g, v["nf"] - i) / v["nf"]), v["out"] * min(g, v["nf"] - i) / v["nf"] * kp)
                  for i in range(0, v["nf"], g)) for v in per.values()]
            out["plan5_g%d_kappa%.1f_cost_jpy" % (g, kp)] = round(sum(cs) / len(cs), 3)
    out["plan5_mean_calls_g3"] = round(mean(lambda v: math.ceil(v["nf"] / 3)), 1); out["plan5_mean_calls_g5"] = round(mean(lambda v: math.ceil(v["nf"] / 5)), 1)
    # 案3'(文ID強制1 call分類): 入出力=実測+文ID/判定のオーバーヘッド(40 tok/文)、reasoningはkappa倍
    for kp in (1.0, 1.5):
        out["plan3p_sentenceid_kappa%.1f_cost_jpy" % kp] = round(sum(cost_tok(v["in"] + 12 * v["ns"], v["out"] * kp + 40 * v["ns"]) for v in per.values()) / len(per), 3)
    # 案3(候補対のLLM分類、L2 alignment対): 1 call、対あたり入力100tok・出力150/400tok(仮定)
    for ot in (150, 400):
        out["plan3_pairs_out%d_cost_jpy" % ot] = round(sum(cost_tok(a + b * v["ac"] + 100 * ev[k]["pairs_L2"], ot * ev[k]["pairs_L2"]) for k, v in per.items()) / len(per), 3)
    out["plan3_mean_pairs_L2"] = round(sum(ev[k]["pairs_L2"] for k in per) / len(per), 1)
    base = out["A_single_mean_cost_jpy"]
    out["plan2_n2"] = round(base * 2, 3); out["plan2_n3"] = round(base * 3, 3)
    out["plan6_extra_assumed_range"] = [round(base * 0.5, 3), round(base * 1.0, 3)]
    # Stage 2: rep30実測の比例推定
    s2 = stage2_rep30()
    sa, sb, sr = linfit([x["stage1_major_n"] for x in s2], [x["stage2_c1_cost_jpy"] for x in s2])
    out["stage2_fit"] = {"a": round(sa, 3), "b_per_major": round(sb, 3), "r": round(sr, 3), "n": len(s2), "major_n_range": [min(x["stage1_major_n"] for x in s2), max(x["stage1_major_n"] for x in s2)]}
    cur = []
    for k in negs:
        for r in fresh_runs(k):
            n = len(P.majors(r["parsed"])); cur.append(0 if n == 0 else sa + sb * n)
    out["neg_stage2_cost_now_A_single"] = round(sum(cur) / len(cur), 3)
    for lv in ("L0", "L2"):
        out["neg_stage2_cost_if_all_%s_candidates_sent" % lv] = round(sum(sa + sb * ev[k][lv + "_candidate_sentences"] for k in negs) / len(negs), 3)
    return out


def case2_recap():
    j = json.load(open(OUTD + "/agg_stage1_variance_impact_01.json", encoding="utf8"))
    r = {sub: {"A_single": v["A_single_rate"], "union_run1_run2": v["A_union_run1_run2"], "union_all_runs": v["A_union_all_runs"], "n": v["n_runs"]}
         for sub, v in j["sc"].items()}
    r["HF-011"] = {"A_single": j["hf011"]["A_single_rate"], "union_run1_run2": j["hf011"]["A_union_run1_run2"]}
    return r, j["neg"]


def write_md(summ, negs_s, nonsc, real_total, costs, case2, ev):
    L = ["# Stage 1再設計案 ¥0事前評価(委任_03、既存データのみ・API 0・実装なし)", "",
         "出典: `stage1_redesign_offline_eval_01.py`/同名json。案4の決定論pre-checkは**設計レベルの簡易模擬**(日英辞書約40語・アンカー照合)で本実装ではない。数値は模擬の性質上、設計判断の材料(採否の確定根拠ではない)。", "",
         "## (a) 案4 決定論pre-check模擬: Safety-critical gold文(%d件)が候補に入るか" % summ["n_gold"], "",
         "- L0(カテゴリ語マーカーがあれば候補。alignmentなし): %d/%d" % (summ["gold_in_L0"], summ["n_gold"]),
         "- L1(マーカー+緩いalignment[アンカー1つ共有のfact全部]+不一致): %d/%d" % (summ["gold_in_L1"], summ["n_gold"]),
         "- L2(マーカー+厳格alignment[最多アンカーfactのみ]+不一致): %d/%d" % (summ["gold_in_L2"], summ["n_gold"]),
         "- gold文が関連factにalignされた数: 緩い%d/%d、厳格(L2)%d/%d" % (summ["gold_aligned_loose"], summ["n_gold"], summ["gold_aligned_L2"], summ["n_gold"]),
         "- 既存`run_precheck`(Ledger×本文の機械照合)が24 fixture(A15+er009合成9)で立てた候補合計: %d(er009_changed_numberの1件のみ)" % real_total, "",
         "| instance | sub | L0 | L1 | L2 | 関連factにalign(緩/厳) | カテゴリ(L0) |", "|---|---|---|---|---|---|---|"]
    for k, e in ev.items():
        for g in e["gold"]:
            L.append("| %s | %s | %s | %s | %s | %s/%s | %s |" % (k, g["sub"], "○" if g.get("in_L0_candidates") else "×", "○" if g.get("in_L1_candidates") else "×",
                     "○" if g.get("in_L2_candidates") else "×", "○" if g.get("aligned_to_related_fact") else "×", "○" if g.get("L2_aligned_to_related") else "×", ",".join(g.get("L0_cats", []))))
    L += ["", "## (a') 負例/NORMAL 6 instanceの候補文数(平均本文文数%.1f)" % negs_s["L0"]["mean_sentences"], "", "| 方式 | 平均候補文数 | ≥1文立つinstance |", "|---|---|---|"]
    for lv in ("L0", "L1", "L2"):
        L.append("| %s | %s | %d/%d |" % (lv, negs_s[lv]["mean"], negs_s[lv]["instances_with_ge1"], negs_s[lv]["n"]))
    L += ["", "現行A単発のMAJOR出現率は7/12(58.3%)。L0/L2は全instanceで候補が立つため、候補を全てStage 2へ渡す設計はStage 2発動率100%・候補8〜20文/記事となる。", "",
          "## (a'') B4非SC(frozenが拾いfresh 2runが拾わなかったMAJOR 4件)の文が候補に入るか", ""]
    for r in nonsc["bgroup_B4"]:
        L.append("- %s: 文特定=%s / L0=%s / L2=%s / %s" % (r["related_fact_id"], r["sentence_located"], r["in_L0"], r["in_L2"], r["claim"]))
    L += ["", "## (b)(d) 費用見込み(円/記事、gpt-6-luna単価、A単発実測平均%.3f=%dtok in/%dtok out)" % (costs["A_single_mean_cost_jpy"], costs["A_mean_in_tokens"], costs["A_mean_out_tokens"]), "",
          "| 案 | 費用/記事(円) | 備考 |", "|---|---|---|",
          "| 案1/案2(n=1) | %.3f | 実測 |" % costs["A_single_mean_cost_jpy"],
          "| 案2 n=2 / n=3 | %.3f / %.3f | 単純倍(実測平均×n) |" % (costs["plan2_n2"], costs["plan2_n3"]),
          "| 案3 候補対LLM分類(1 call、対%.1f件) | %.3f〜%.3f | 対あたり出力150〜400tok仮定(推測) |" % (costs["plan3_mean_pairs_L2"], costs["plan3_pairs_out150_cost_jpy"], costs["plan3_pairs_out400_cost_jpy"]),
          "| 案3' 文ID強制1 call分類 | %.3f〜%.3f | reasoning 1.0〜1.5倍仮定(推測) |" % (costs["plan3p_sentenceid_kappa1.0_cost_jpy"], costs["plan3p_sentenceid_kappa1.5_cost_jpy"]),
          "| 案4 | 0 | 機械照合のみ。ただしStage 2費用が増える(下記) |",
          "| 案5 fact群batch(3facts/call, %.1f call) | %.3f〜%.3f | 出力は担当fact比例×1.0〜1.5仮定(推測) |" % (costs["plan5_mean_calls_g3"], costs["plan5_g3_kappa1.0_cost_jpy"], costs["plan5_g3_kappa1.5_cost_jpy"]),
          "| 案5 fact群batch(5facts/call, %.1f call) | %.3f〜%.3f | 同上 |" % (costs["plan5_mean_calls_g5"], costs["plan5_g5_kappa1.0_cost_jpy"], costs["plan5_g5_kappa1.5_cost_jpy"]),
          "| 案6 最終安全確認(+1 call) | +%.3f〜+%.3f | A単発の0.5〜1.0倍と仮定(推測。S1-Uは約14.6%%増の記録) |" % tuple(costs["plan6_extra_assumed_range"]), "",
          "Stage 2(rep30実測の比例推定): cycle1 Stage 2費用 ≒ %.3f + %.3f×Stage 1 MAJOR件数(r=%.2f, n=%d instance、MAJOR件数範囲%s)。" % (costs["stage2_fit"]["a"], costs["stage2_fit"]["b_per_major"], costs["stage2_fit"]["r"], costs["stage2_fit"]["n"], costs["stage2_fit"]["major_n_range"]),
          "負例/NORMAL 1記事あたりStage 2費用: 現行A単発 %.3f円 → 候補(L2)全件投入 %.3f円 → 候補(L0)全件投入 %.3f円(件数がfit範囲外のため外挿・過小評価の可能性)。" % (costs["neg_stage2_cost_now_A_single"], costs["neg_stage2_cost_if_all_L2_candidates_sent"], costs["neg_stage2_cost_if_all_L0_candidates_sent"]), "",
          "## (c) 案2 Stage 1複数回∪(RCA既出の再掲)", "", "| claim | A単発 | 2回∪ | 全run∪ |", "|---|---|---|---|"]
    for sub, v in case2[0].items():
        L.append("| %s | %s | %s | %s |" % (sub, v["A_single"], "検出" if v["union_run1_run2"] else "見逃し", ("検出" if v.get("union_all_runs") else "見逃し") if "union_all_runs" in v else "-"))
    L += ["", "負例/NORMAL MAJOR率: 単発58.3% → 2回∪66.7%(RCA既出)。neg5 B3-sameとHF-011は∪でも見逃し(n=2)。", "",
          "## 限界(推測の明示)", "",
          "- 案4模擬の辞書・マーカーは小辞書で、Ledger/本文が日英であることの辞書依存が大きい。精度が低いのは模擬の粗さの影響も含む(本実装の上限ではない)。ただし『Ledger factのcausal_strengthが記事の因果表現の"
          "原因側まで保証しない(B3: HF-007は因果stated)』『A2A3-0のような主体差替えはマーカー語を持たない』は構造上の限界【確認: 該当fixture】。",
          "- 費用は単価と実測tokensからの算術。案3/5/6の出力tokensは仮定(推測)。実測ではない。n=24〜32のfixture/runの小標本。",
          "- Stage 2費用fitはn=30、MAJOR件数0〜10の範囲。候補20件は外挿。", "- 本評価は検出率の保証ではない。E2E(fresh)でのみKPI判定できる。"]
    open(OUTD + "/stage1_redesign_offline_eval_01.md", "w", encoding="utf8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    d, extra, ev, gold, summ, negs_s, nonsc, real_total = main()
    costs = compute_costs(d, ev, P.A_NEG)
    case2 = case2_recap()
    slim = {k: {kk: vv for kk, vv in e.items() if kk != "rows"} for k, e in ev.items()}
    json.dump({"summary": summ, "negatives": negs_s, "nonsc_B4": nonsc, "existing_precheck_total": real_total, "costs": costs,
               "case2_recap": case2[0], "per_instance": slim}, open(OUTD + "/stage1_redesign_offline_eval_01.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    write_md(summ, negs_s, nonsc, real_total, costs, case2, ev)
    print(json.dumps({"summary": summ, "costs": costs}, ensure_ascii=False, indent=1))
