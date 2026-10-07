# -*- coding: utf-8 -*-
"""STAGE2-01 委任_01 作業4/5/6: dev既知NG項目のStage1候補化率・Stage2判定・r3 support_fact_ids復元可否・replay対象(API無し、既存ログのみ)。
実行: PYTHONPATH=. python er052_output/open233_stage2_01/precheck/stage1_candidate_rate.py"""
import json, re, pathlib, collections, os, glob
ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).parent
RC = ROOT / "er052_output/open233_stage0_01/reclass"
split = json.load(open(RC / "split.json", encoding="utf-8"))
dev = set(split["dev"])
rows = [json.loads(l) for l in open(RC / "known_relation_ng.jsonl", encoding="utf-8")]
items = [dict(r, src=r.get("src") or "past") for r in rows if r.get("item_id") in dev]
assert len(items) == 100

MAP_CCP = json.load(open(ROOT / "er052_output/open233_control_checker_polysemy_trial_01/eval/_private/MAP_ccp.json", encoding="utf-8"))["articles"]
MAP_RCA = json.load(open(ROOT / "er052_output/open233_ng_root_cause_01/_private/MAP_rca.json", encoding="utf-8"))["articles"]


def run_dir(it):
    if it["src"] == "ccp":
        m = MAP_CCP.get(it["article"])
        return ROOT / m["src"].replace(chr(92), "/") if m else None
    if it["src"] == "rca":
        m = MAP_RCA.get(it["article"])
        if m and m.get("origin") in ("E2E02_control", "E2E02_P2"):
            return ROOT / m["src"].replace(chr(92), "/")
    return None


def load_log(rd):
    fs = glob.glob(str(rd / "checker/runs/*.json"))
    return json.load(open(fs[0], encoding="utf-8")) if fs else None


def grams(s, n=3):
    s = re.sub(r"[\s、。,.「」『』()（）/:：]", "", s or "")
    return {s[i:i + n] for i in range(len(s) - n + 1)}


def en_tokens(s):
    return set(w.lower() for w in re.findall(r"[A-Za-z]{4,}|\d+(?:\.\d+)?", s or ""))


def main_text(t):
    t = re.sub(r"^(R0|R2|EN|JA)[:：「]?\s*", "", t or "")
    return re.split(r"[(（]", t)[0]


GUARD = {"否定・不在": "否定・不在", "全称": "全称", "多義語方向": "方向・極性", "主語新規出現・置換": "主体", "数値": "数値"}


def gtype(st):
    return GUARD.get(st, "非ガード型(" + st + ")")


def link(it, cand):
    """項目↔Stage1候補の対応(API無しの近似)。fact一致=粗い(同fact内の別文を含む)、text一致=文レベルの可能性が高い。"""
    fid = it.get("fact_id")
    fact_hit = bool(fid) and fid in (cand.get("related_fact_ids") or [])
    mt = main_text(it["text"])
    a, b = grams(mt), grams((cand.get("claim_text") or "") + "".join(cand.get("issues") or []))
    ja = len(a & b) / max(1, len(a))
    et = len(en_tokens(it["text"]) & en_tokens(cand.get("claim_text")))
    return fact_hit, ja, et


def stage2_for(log, cand):
    out = []
    for ci, c in enumerate(log["cycles"], 1):
        for r in c.get("stage2_results", []):
            if r.get("claim_text") == cand["claim_text"]:
                so = r.get("second_opinion") or {}
                out.append({"cycle": ci, "llm": r.get("llm_materiality"), "final": r.get("materiality"), "basis": r.get("basis"),
                            "floor": r.get("floor_reason"), "so_first": so.get("first_materiality"), "so_second": so.get("second_materiality"),
                            "so_confirmed_downgrade": so.get("confirmed_downgrade")})
    return out


res, excluded = [], collections.Counter()
for it in items:
    rd = run_dir(it)
    row = {"item_id": it["item_id"], "src": it["src"], "article": it.get("article"), "sentence_type": it.get("sentence_type"),
           "guard_type": gtype(it.get("sentence_type") or ""), "fact_id": it.get("fact_id"), "origin": it.get("origin"),
           "severity": it.get("severity_final")}
    if it["src"] == "b3":
        excluded["b3_no_checker(--no-checker)"] += 1; row["status"] = "excluded:b3_no_checker"; res.append(row); continue
    if not it["src"] in ("ccp", "rca"):
        excluded["past_major_old_runs_not_in_logset"] += 1; row["status"] = "excluded:past_major_no_log"; res.append(row); continue
    if rd is None:
        excluded["rca_b3v0_no_checker"] += 1; row["status"] = "excluded:rca_b3v0_no_checker"; res.append(row); continue
    log = load_log(rd)
    if log is None:
        excluded["log_missing"] += 1; row["status"] = "excluded:log_missing"; res.append(row); continue
    cands = log["stage1_coverage"]["union_candidates"]
    best = None
    for c in cands:
        fh, ja, et = link(it, c)
        score = (1 if (fh and (ja >= 0.25 or et >= 2)) else 0, ja + 0.1 * et)
        if best is None or score > best[0]:
            best = (score, c, fh, ja, et)
    # 文レベル(text)一致: fact一致+JA3gram>=0.25またはEN語>=2、もしくはJA3gram>=0.4(fact無関係)
    sent = [(c, link(it, c)) for c in cands if (lambda l: l[2] >= 3 or (l[0] and l[1] >= 0.4))(link(it, c))]
    sent.sort(key=lambda x: (-x[1][2], -x[1][1]))
    factonly = [c for c in cands if link(it, c)[0]]
    if it["item_id"] == "ai_control-jb9k-n3":  # RCA_jb9k_qvqc.md(人間判定・ログ確認済み): S7.4が候補化(MAJOR)、Stage2がQUALITYへ格下げ。機械近似では拾えないため手動で固定
        sent = [(c, None) for c in cands if "S7.4" in (c.get("unit_ids") or [])]
        row["manual_override"] = "RCA_jb9k_qvqc.md(S7.4候補化を確認済み)"
    row["run"] = str(rd.relative_to(ROOT)).replace(chr(92), "/")
    row["n_stage1_candidates_in_article"] = len(cands)
    row["fact_id_known"] = bool(it.get("fact_id"))
    if sent:
        c = sent[0][0]
        row["status"] = "candidate_sentence_level"
        row["matched_claim"] = c["claim_text"]; row["matched_unit_ids"] = c.get("unit_ids")
        row["stage2"] = stage2_for(log, c)
    elif factonly:
        row["status"] = "candidate_fact_level_only"
        row["matched_claim"] = factonly[0]["claim_text"]; row["n_fact_candidates"] = len(factonly)
        row["stage2"] = stage2_for(log, factonly[0])
    else:
        row["status"] = "no_candidate" if row["fact_id_known"] else "indeterminate_fact_id_null"
    res.append(row)

eligible = [r for r in res if not r["status"].startswith("excluded")]


def rate(rs):
    n = len(rs)
    s = sum(1 for r in rs if r["status"] == "candidate_sentence_level")
    f = sum(1 for r in rs if r["status"] == "candidate_fact_level_only")
    ind = sum(1 for r in rs if r["status"] == "indeterminate_fact_id_null")
    nc = sum(1 for r in rs if r["status"] == "no_candidate")
    return {"n": n, "sentence_level": s, "fact_level_only": f, "no_candidate": nc, "indeterminate_fact_id_null": ind,
            "rate_lower_sentence": round(s / n, 3) if n else None, "rate_upper_sentence_or_fact": round((s + f) / n, 3) if n else None,
            "rate_upper_among_determinable": round((s + f) / (n - ind), 3) if n - ind else None}


def s2sum(rs):
    c = collections.Counter()
    for r in rs:
        if "stage2" in r and r["stage2"]:
            s = r["stage2"][0]
            c[("final_" + str(s["final"]))] += 1
            if s["llm"] == "BLOCKING" and s["final"] != "BLOCKING": c["llm_BLOCKING_then_downgraded"] += 1
            if s["so_confirmed_downgrade"]: c["second_opinion_confirmed_downgrade"] += 1
            if s["final"] == "BLOCKING": c["final_blocking_total"] += 1
            else: c["final_non_blocking_total"] += 1
        elif r["status"].startswith("candidate"):
            c["candidate_but_no_stage2_entry"] += 1
    return dict(c)


by_type = {}
for t in sorted({r["guard_type"] for r in eligible}):
    sub = [r for r in eligible if r["guard_type"] == t]
    by_type[t] = {"stage1": rate(sub), "stage2": s2sum(sub)}
summary = {"dev_items_total": 100, "excluded": dict(excluded), "eligible_n": len(eligible), "overall": {"stage1": rate(eligible), "stage2": s2sum(eligible)},
           "by_guard_type": by_type,
           "method_caveat": "項目はJA文(R0/R2由来)、Stage1候補はEN文。文レベル対応は(EN語/数値の共有3語以上)または(fact_id一致 かつ 項目JA文とCheckerのissue+claimのJA3gram重なり>=0.4)で近似した機械判定(人間確認なし)。fact_level_onlyは同factの別文を拾っただけの可能性を含む。fact_id不明(保留項目)は判定不能として別掲。"}
json.dump({"summary": summary, "items": res}, open(OUT / "stage1_candidate_rate.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(summary, ensure_ascii=False, indent=1))

# ---- md出力 ----
def row_md(t, v):
    s1, s2 = v["stage1"], v["stage2"]
    return (f"| {t} | {s1['n']} | {s1['sentence_level']} | {s1['fact_level_only']} | {s1['no_candidate']} | {s1['indeterminate_fact_id_null']} | "
            f"{s1['rate_lower_sentence']} / {s1['rate_upper_sentence_or_fact']} | "
            f"{s2.get('final_BLOCKING', 0)} / {s2.get('final_QUALITY', 0)} / {s2.get('final_ACCEPTABLE', 0)} |")


runs_used = sorted({r["run"] for r in eligible})
lines = ["# Stage1候補化率・Stage2判定(dev既知NG 100件、¥0・既存ログのみ)",
         "", "委任: OPEN-233-CHECKER-ACTION-POLICY-STAGE2-01 委任_01 作業4。生成: `stage1_candidate_rate.py`(同ディレクトリ)。詳細はstage1_candidate_rate.json。",
         "", "## 分母",
         f"- dev項目 100件(split.json dev)。Checkerログあり=**{len(eligible)}件**(ccp 26[18本中13記事]+rca 31のうちE2E_02由来21、{len(runs_used)}本のrun)。",
         f"- 対象外 {sum(excluded.values())}件: B3 Trial {excluded['b3_no_checker(--no-checker)']}件(--no-checkerでChecker未通過)、RCA盲検再採点のB3 V0由来 {excluded['rca_b3v0_no_checker']}件(Checker無し)、過去重大(PAST-*) {excluded['past_major_old_runs_not_in_logset']}件(旧版runのログがログ集合に無い)。",
         "- 版: 使用した33本(ccp 18+E2E_02の従来版5+P2版10)は全て stage1_coverage_v1、PROMPT_SHA256が現行と一致(replay_targets.json)。",
         "", "## 方法と限界(重要)",
         "- 項目はJA文(R0/R2由来)・評価者の説明、Stage1候補はEN文+日本語issue。**同一文かの対応付けはAPI無しの機械近似**。",
         "  - `sentence_level`: (EN語/数値の共有3語以上)または(項目のfact_id一致 かつ 項目JA文とCheckerのissue+claimのJA3gram重なり>=0.4)。jb9k-n3のみRCA_jb9k_qvqc.md(S7.4候補化)で手動固定。人間確認なし。",
         "  - `fact_level_only`: 同じfact_idの候補は在るが文までは確認できない(同factの別文を拾っただけの可能性を含む)。**候補化率の上限側を押し上げる**。",
         "  - `indeterminate_fact_id_null`: 保留項目でfact_idが無く、機械では対応不能。",
         "  - 目視で怪しい文レベル判定: hormuz-d5qr-p2、meta-7aqr-n1の2件(下限側は実質9件の可能性)。",
         "- Stage1の「候補化」=当該runの初回Stage1 union_candidates(Rewrite後の再検出は含めない)。評価対象ENは採用版(Rewrite後の場合あり)で、初回Stage1が見た文と異なりうる。",
         "- Stage2判定=対応候補のcycle1(初出)判定。`BLOCKING/QUALITY/ACCEPTABLE`は最終materiality。", "",
         "## 全体", "| 区分 | n | 文レベル | fact一致のみ | 候補なし | 判定不能 | 候補化率(下限=文/上限=文+fact) | Stage2最終 BLOCKING/QUALITY/ACCEPTABLE |", "|---|---|---|---|---|---|---|---|",
         row_md("全体", summary["overall"]), "", "## ガード対象型別(`sentence_type`をガード型へ写像)",
         "ガード型の写像: 否定・不在=否定・不在 / 全称 / 多義語方向=方向・極性 / 主語新規出現・置換=主体 / 数値。その他は非ガード型(参考)。",
         "| 型 | n | 文レベル | fact一致のみ | 候補なし | 判定不能 | 候補化率(下限/上限) | Stage2 BLOCKING/QUALITY/ACCEPTABLE |", "|---|---|---|---|---|---|---|---|"]
for t, v in by_type.items():
    lines.append(row_md(t, v))
ov = summary["overall"]["stage2"]
n_s2 = ov.get("final_blocking_total", 0) + ov.get("final_non_blocking_total", 0)
lines += ["", "## Stage2格下げ", f"- Stage1が(文/fact)対応候補にしたうちStage2のentryが見つかったのは{n_s2}件。最終BLOCKING {ov.get('final_blocking_total', 0)}件、"
          f"非BLOCKING(QUALITY/ACCEPTABLE) {ov.get('final_non_blocking_total', 0)}件 = **非BLOCKING率 {round(ov.get('final_non_blocking_total', 0) / n_s2, 3) if n_s2 else None}**。",
          "- 初回のStage2 LLM判定(llm_materiality)がBLOCKINGで後から格下げされた例は0件(`llm_BLOCKING_then_downgraded`)。ほぼ全件がStage2 LLMの初回判定から非BLOCKING。",
          "- 2nd opinion(`second_opinion.confirmed_downgrade=true`)は非BLOCKING判定のほぼ全てに付いている(下限を弱める方向の確認ではなく、2回目も非BLOCKINGで同意した記録)。2nd opinionが非BLOCKING→BLOCKINGへ引き上げた例は対象全記事で3件(別集計・本表の項目とは別)。",
          "- 旧BLOCKING寄りの根拠(`s1_second_opinion_blocking`)等の詳細はjsonの`stage2`欄。", "",
          "## 含意(事実のみ)",
          "- ガード対象型(否定・不在/全称/方向・極性/主体/数値)のdev項目はeligible内でn=17。数値型は2件とも保留でfact_idが無く判定不能。",
          "- Stage1の候補化は、fact_idが分かる項目の範囲では96.7%(fact一致を含む上限)だが、文レベル確証は23.4%に留まる。候補化後のStage2が非BLOCKINGとする点が主な取りこぼし経路。",
          "- 文レベルの人間確認と、Stage1が文を直接拾ったかの確定にはr3 per-unit(support_fact_ids含む)の保存付きreplayが要る(作業5参照)。"]
(OUT / "stage1_candidate_rate.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
