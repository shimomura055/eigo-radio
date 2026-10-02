# -*- coding: utf-8 -*-
"""OPEN-233-SELF-RECOVERY-TRIAL-01 委任_49 作業5: 検出器の直接比較(Trial専用、Checker呼び出しのみ)。

目的: 「Also, some calls needed user information to continue.」が残っている英語本文に対して、検出器が
(a)MAJORで指摘する (b)MINORで指摘する (c)指摘しない のどれになるかを、検出器ごとに数える
(「見えていない」のか「MINORで捨てられている」のかの切り分けの材料)。**flowは回さない**(Stage 2・Rewrite・Recheck
の周回は呼ばない。Checkerの呼び出しだけ)。Production正式path(er003等)は編集しない(runnerのimportのみ)。

検出器(モデル・effort等はrunnerの現行のStage 1/Recheckと同一=runnerの関数をそのまま呼ぶ):
- DET-A 現行Recheck: runner.run_recheck(同一Prompt・schema)。prior_issuesは、その本文が得られた実行の記録どおり
  (最後に書き換えが入ったcycleのBLOCKING指摘から、runnerと同じ式で再構成)。P5・N3は周回前なので対象外。
- DET-B 現行のStage 1相当: runner.stage1_fresh_with_enumeration(V4A + 重大誤解原則のdeveloper message、
  prior_issuesなし)。
- DET-C 出口検査の候補Prompt: DET-Bと同じ土台で、Trial専用の追記ブロック(DET_C_BLOCK)を、runnerのTrial用追記の仕組み
  (trial.build_trial_prompt_template)に連結して使う(呼び出し中だけ差し替え。er003/er051は編集しない)。

予算stateは専用ファイル(本ディレクトリのbudget_state_direct_compare_01.json)。runner.BUDGET_STATE_PATH・TOTAL_BUDGET_JPY
を本スクリプト内で差し替えるため、既存の証跡ファイルを上書きしない。
実行: --stage probe(P1の各検出器1回=3 call)→ --stage main → --stage agg。
"""
import argparse
import csv
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "er052_output", "open233_detector_direct_compare_01")
CALLS = os.path.join(OUT, "calls")
BUDGET_PATH = os.path.join(OUT, "budget_state_direct_compare_01.json")

import er052_open233_self_recovery_flow_runner_01 as runner  # noqa: E402
import er051_open233_checker_trial_variant_01 as trial  # noqa: E402
import er052_open233_self_recovery_stage2_production_01 as s2p  # noqa: E402

# 予算stateを専用ファイルへ(runnerのrecord_call/check_budgetが参照する)
runner.BUDGET_STATE_PATH = BUDGET_PATH
runner.TOTAL_BUDGET_JPY = 22.0

TARGET = "Also, some calls needed user information to continue."
PHRASE_POS = "needed user information"  # 判定基準(固定)
PHRASE_NEG = "user information"  # 陰性(書き換え後の文は"needs user information"等)用の補助判定
PHRASE_ENJOYED = "they enjoyed ai's convenience"  # 参考データ
ER = os.path.join(HERE, "er052_output")
P = "open233_self_recovery_flow_runner_01_"

# DET-Cの追記ブロック(Trial専用、実装前に報告へ載せるため定数として持つ。{}を含めない=.format安全)
DET_C_BLOCK = """

【Trial専用の追加指示(OPEN-233、出口検査候補、Production非適用)】
Verified Fact Ledgerのfactを1件ずつ順に取り上げ、記事の中でそのfactに触れている文をすべて確認してください。
Ledgerが条件つき・可能性・懸念として書いている内容を、記事が実際に起きたこととして書いていないかを、各文で確認してください。
確認の結果は、重大度を問わず(MAJORもMINORも)deviationsにすべて列挙してください。
何を逸脱とするか、severityの基準、10種類のflagの基準は変えません。"""

# 本文ID → (出所のinstanceファイル, 該当cycleの指定, instance_id(fixture)), 陽性/陰性
SOURCES = {
    "P1": ("rep22 T1 s1", "rep22/instances_s1/meta_run03_standard.json", "pos"),
    "P2": ("rep22 T1 s3", "rep22/instances_s3/meta_run03_standard.json", "pos"),
    "P3": ("rep22 T1 s4", "rep22/instances_s4/meta_run03_standard.json", "pos"),
    "P4": ("rep21 s2", "rep21/instances_s2/meta_run03_standard.json", "pos"),
    "P5": ("meta_run03_standard 元記事(固定fixture cycle1)", None, "pos"),
    "N1": ("rep22 T1 s2", "rep22/instances_s2/meta_run03_standard.json", "neg"),
    "N2": ("rep20 s1", "rep20/instances_s1/meta_run03_standard.json", "neg"),
    "N3": ("neg1_meta_b3prod_a2 元記事", None, "neg"),
}
DETS = {"A": ["P1", "P2", "P3", "P4", "N1", "N2"], "B": ["P1", "P2", "P3", "P4", "P5", "N1", "N2", "N3"],
        "C": ["P1", "P2", "P3", "P4", "P5", "N1", "N2", "N3"]}


def ws(s):
    return re.sub(r"\s+", " ", s or "").strip()


def norm_claim(s):
    s = (s or "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return ws(s).lower()


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def final_text_and_prior(path):
    """最後に書き換えが入ったcycleの本文と、そのcycleのRecheckに渡されたprior_issues(runnerと同じ式で再構成)。"""
    d = load(os.path.join(ER, P + path))
    last = None
    for i, c in enumerate(d["cycles"]):
        if c.get("en_text_after_rewrite") is not None:
            last = i
    c = d["cycles"][last]
    prior = []
    for s in c["stage2_results"]:
        if s["materiality"] != "BLOCKING":
            continue
        dev = s["dev"]
        prior.append({"fact_id": dev.get("related_fact_id", ""),
                      "claim_in_article": s.get("claim_span_text") or s["claim_text"],
                      "issue": dev.get("issue", ""), "explanation": dev.get("explanation", "")})
    return c["en_text_after_rewrite"], prior, {"cycle": c["cycle"], "final_state": d["final_state"]}


def build_inputs():
    insts = {i["instance_id"]: i for i in runner.build_target_instances()}
    meta, neg1 = insts["meta_run03_standard"]["fixture"], insts["neg1_meta_b3prod_a2"]["fixture"]
    out = {}
    for tid, (label, path, kind) in SOURCES.items():
        if tid == "P5":
            text, prior, info, fx = meta["article_text"], None, {"cycle": None, "final_state": None}, meta
        elif tid == "N3":
            text, prior, info, fx = neg1["article_text"], None, {"cycle": None, "final_state": None}, neg1
        else:
            text, prior, info = final_text_and_prior(path)
            fx = meta
        has = TARGET in ws(text)
        sent_ui = [x.strip() for x in re.split(r"(?<=[.!?])\s+", text) if "user information" in x]
        out[tid] = {"label": label, "kind": kind, "text": text, "prior_issues": prior, "info": info,
                    "ledger_text": fx["ledger_text"], "source_article_text": fx.get("source_article_text"),
                    "target_exact_present": has, "sentences_with_user_information": sent_ui,
                    "expected_present": kind == "pos"}
    return out


def verify_inputs(inputs):
    ok = True
    for tid, v in inputs.items():
        status = "OK" if v["target_exact_present"] == v["expected_present"] else "MISMATCH"
        if status != "OK":
            ok = False
        print(f"[input check] {tid} ({v['label']}): 該当文の完全一致={v['target_exact_present']} "
              f"(期待={v['expected_present']}) -> {status}; user informationを含む文={v['sentences_with_user_information']}")
    return ok


class RecClient:
    """実クライアントのラッパー(生の応答の記録用)。responses.createの引数と出力を保持する。"""

    def __init__(self, real):
        self._real = real
        self.last = None
        outer = self

        class _R:
            @staticmethod
            def create(**kw):
                resp = real.responses.create(**kw)
                outer.last = {"output_text": getattr(resp, "output_text", None), "usage": s2p._extract_usage(resp),
                              "prompt": kw["input"][-1]["content"], "developer": kw["input"][0]["content"]}
                return resp

        self.responses = _R


def call_one(rc, state, ce, det, tid, k, inp, model_label):
    label = f"dc01_{det}_{tid}_{k}"
    fixture = {"ledger_text": inp["ledger_text"], "article_text": inp["text"],
               "source_article_text": inp["source_article_text"]}
    call_log = []
    rc.last = None
    t0 = time.time()
    err, parsed = None, None
    try:
        if det == "A":
            parsed = runner.run_recheck(rc, state, ce, call_log, label, fixture, inp["text"], inp["prior_issues"])
        elif det == "B":
            parsed = runner.stage1_fresh_with_enumeration(
                rc, state, ce, call_log, label, fixture,
                developer_message=trial.V4A_DEVELOPER_MSG_WITH_MISCONCEPTION_PRINCIPLE)
        else:
            orig = trial.build_trial_prompt_template
            trial.build_trial_prompt_template = lambda v: orig(v) + DET_C_BLOCK
            try:
                parsed = runner.stage1_fresh_with_enumeration(
                    rc, state, ce, call_log, label, fixture,
                    developer_message=trial.V4A_DEVELOPER_MSG_WITH_MISCONCEPTION_PRINCIPLE)
            finally:
                trial.build_trial_prompt_template = orig
    except runner.TrialAbort:
        raise
    except Exception as e:  # noqa: BLE001  (JSON/schema失敗など。応答が得られていれば費用は計上する)
        err = f"{type(e).__name__}: {e}"
        if rc.last is not None:
            cost = round(s2p.official_cost_jpy(rc.last["usage"]), 4)
            state["cumulative_jpy"] += cost
            state["cumulative_calls"] += 1
            state["cumulative_errors"] += 1
            state["history"].append({"label": label, "cost_jpy": cost, "recovery_stage": "dc01_parse_failure",
                                      "usage": rc.last["usage"]})
            runner.save_budget_state(state)
    if parsed is not None and (parsed.get("_stage1_api_failure") or parsed.get("_recheck_api_failure")):
        err = "api_failure"
    last = rc.last or {}
    raw_devs = []
    try:
        raw_devs = json.loads(last.get("output_text") or "{}").get("deviations", [])
    except Exception:  # noqa: BLE001
        pass
    cost = round(sum(c.get("cost_jpy", 0.0) for c in call_log), 4) or (
        round(s2p.official_cost_jpy(last["usage"]), 4) if last.get("usage") else 0.0)
    rec = {"detector": det, "text_id": tid, "k": k, "label": label, "model": model_label, "error": err,
           "cost_jpy": cost, "usage": last.get("usage"), "elapsed_seconds": round(time.time() - t0, 3),
           "prompt_sha256": s2p.sha256_text(last["prompt"]) if last.get("prompt") else None,
           "raw_output_text": last.get("output_text"),
           "raw_model_deviations": raw_devs,
           "final_deviations": ([dict(d) for d in parsed.get("deviations", [])] if parsed else None),
           "overall_status": parsed.get("overall_status") if parsed else None}
    os.makedirs(CALLS, exist_ok=True)
    with open(os.path.join(CALLS, f"{det}_{tid}_{k}.json"), "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=1)
    return rec


def load_state():
    if os.path.exists(BUDGET_PATH):
        return load(BUDGET_PATH)
    return {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}


def planned(pos_n, neg_n):
    plan = []
    for det, tids in DETS.items():
        for tid in tids:
            n = pos_n if SOURCES[tid][2] == "pos" else neg_n
            for k in range(1, n + 1):
                plan.append((det, tid, k))
    return plan


def done(det, tid, k):
    return os.path.exists(os.path.join(CALLS, f"{det}_{tid}_{k}.json"))


# ------------------------------------------------------------ 集計
def classify(devs, phrase):
    """区分(MAJOR/MINOR/none)と該当指摘。claim_in_articleを空白・引用符・大小文字で正規化して部分文字列判定。"""
    hits = [d for d in (devs or []) if phrase in norm_claim(d.get("claim_in_article"))]
    if any(d.get("severity") == "MAJOR" for d in hits):
        return "MAJOR", hits
    if hits:
        return "MINOR", hits
    return "none", hits


def aggregate():
    inputs = build_inputs()
    rows, per = [], defaultdict(Counter)
    tot_cost, n_fail, n_calls = 0.0, 0, 0
    for fn in sorted(os.listdir(CALLS)):
        r = load(os.path.join(CALLS, fn))
        n_calls += 1
        tot_cost += r.get("cost_jpy") or 0.0
        kind = SOURCES[r["text_id"]][2]
        failed = bool(r.get("error"))
        n_fail += 1 if failed else 0
        devs = r.get("final_deviations") or []
        cls, hits = classify(devs, PHRASE_POS)
        cls_raw, _ = classify(r.get("raw_model_deviations"), PHRASE_POS)  # モデルの生の重大度(post-hoc前)
        cls_ui, hits_ui = classify(devs, PHRASE_NEG)
        cls_en, _ = classify(devs, PHRASE_ENJOYED)
        n_major = sum(1 for d in devs if d.get("severity") == "MAJOR")
        n_minor = sum(1 for d in devs if d.get("severity") == "MINOR")
        row = {"detector": r["detector"], "text": r["text_id"], "kind": kind, "k": r["k"], "failed": failed,
               "class_needed_user_information": cls, "class_raw_model_severity": cls_raw,
               "class_user_information_phrase(補助)": cls_ui, "class_they_enjoyed_AI_convenience(参考)": cls_en,
               "hit_fact_ids": sorted({h.get("related_fact_id") for h in hits}),
               "hit_from_enumeration_expansion": [bool(h.get("enumeration_source_claim")) for h in hits],
               "hit_claims": [h.get("claim_in_article") for h in hits],
               "n_major_total": n_major, "n_minor_total": n_minor, "n_deviations_total": len(devs),
               "cost_jpy": r.get("cost_jpy"), "error": r.get("error")}
        rows.append(row)
        if not failed:
            per[(r["detector"], r["text_id"])][cls] += 1
    table = {f"{d}|{t}": dict(c) for (d, t), c in sorted(per.items())}
    summary = {}
    for det in DETS:
        pos = [r for r in rows if r["detector"] == det and r["kind"] == "pos" and not r["failed"]]
        neg = [r for r in rows if r["detector"] == det and r["kind"] == "neg" and not r["failed"]]
        nm = sum(1 for r in pos if r["class_needed_user_information"] == "MAJOR")
        nn = sum(1 for r in pos if r["class_needed_user_information"] == "MINOR")
        summary[det] = {
            "positive_calls": len(pos), "positive_MAJOR": nm, "positive_MINOR": nn,
            "positive_none": len(pos) - nm - nn,
            "positive_MAJOR_rate": round(nm / len(pos), 4) if pos else None,
            "positive_MAJOR_or_MINOR_rate": round((nm + nn) / len(pos), 4) if pos else None,
            "negative_calls": len(neg),
            "negative_calls_with_any_MAJOR": sum(1 for r in neg if r["n_major_total"] > 0),
            "negative_total_MAJOR_deviations": sum(r["n_major_total"] for r in neg),
            "negative_total_MINOR_deviations": sum(r["n_minor_total"] for r in neg),
            "negative_rewritten_sentence_flagged(user information, N1/N2のみ)": dict(Counter(
                r["class_user_information_phrase(補助)"] for r in neg if r["text"] in ("N1", "N2"))),
        }
    enjoyed = defaultdict(Counter)
    for r in rows:
        if not r["failed"]:
            enjoyed[f"{r['detector']}|{r['text']}"][r["class_they_enjoyed_AI_convenience(参考)"]] += 1
    raw_vs_final = [{"detector": r["detector"], "text": r["text"], "k": r["k"], "final": r["class_needed_user_information"],
                     "raw_model": r["class_raw_model_severity"]} for r in rows
                    if r["class_needed_user_information"] != r["class_raw_model_severity"]]
    enum_hit_calls = [{"detector": r["detector"], "text": r["text"], "k": r["k"], "class": r["class_needed_user_information"]}
                      for r in rows if r["hit_from_enumeration_expansion"] and all(r["hit_from_enumeration_expansion"])]
    minor_examples = [{"detector": r["detector"], "text": r["text"], "k": r["k"], "claims": r["hit_claims"]}
                      for r in rows if r["kind"] == "pos" and r["class_needed_user_information"] == "MINOR"]
    res = {"n_calls": n_calls, "n_output_failures(JSON/schema/API)": n_fail, "total_cost_jpy": round(tot_cost, 4),
           "table_detector_x_text(3区分の件数、'none'=指摘なし)": table, "summary_by_detector": summary,
           "positive_texts_where_target_flagged_as_MINOR(全件)": minor_examples,
           "参考_They_enjoyed_AI_convenience_区分(検出器|本文)": {k: dict(v) for k, v in sorted(enjoyed.items())},
           "モデルの生の重大度と最終(post-hoc後)の区分が異なる呼び出し": raw_vs_final,
           "該当文の指摘がすべてsame_fact_id_locations展開(enumeration_source_claim)由来の呼び出し": enum_hit_calls,
           "input_checks": {t: {"target_exact_present": v["target_exact_present"],
                                "sentences_with_user_information": v["sentences_with_user_information"]}
                            for t, v in inputs.items()},
           "caveat": "回数が少ない(陽性は検出器×本文あたりn=2〜3、陰性n=2)ため、率は参考値。結論は書かない。"}
    with open(os.path.join(OUT, "results_01.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT, "cases_01.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        cols = list(rows[0].keys()) if rows else []
        w.writerow(cols)
        for r in rows:
            w.writerow([json.dumps(r[c], ensure_ascii=False) if isinstance(r[c], (list, dict)) else r[c]
                        for c in cols])
    print(json.dumps(res, ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["probe", "main", "agg", "check"])
    ap.add_argument("--pos-n", type=int, default=3)
    ap.add_argument("--neg-n", type=int, default=2)
    ap.add_argument("--budget-jpy", type=float, default=22.0)
    a = ap.parse_args()
    os.makedirs(CALLS, exist_ok=True)
    if a.stage == "agg":
        aggregate()
        return
    inputs = build_inputs()
    ok = verify_inputs(inputs)
    with open(os.path.join(OUT, "inputs_01.json"), "w", encoding="utf-8") as f:
        json.dump({t: {k: v for k, v in x.items() if k != "text"} | {"text_sha256": s2p.sha256_text(x["text"]),
                                                                       "n_chars": len(x["text"])}
                   for t, x in inputs.items()}, f, ensure_ascii=False, indent=1)
    if not ok:
        print("入力の完全一致確認に失敗。課金せず中止。")
        sys.exit(2)
    if a.stage == "check":
        return
    runner.TOTAL_BUDGET_JPY = a.budget_jpy
    state = load_state()
    ce = [0]
    rc = RecClient(runner.vfl01.get_client())
    model_label = runner.MODEL
    if a.stage == "probe":
        for det in ("A", "B", "C"):
            if not done(det, "P1", 1):
                r = call_one(rc, state, ce, det, "P1", 1, inputs["P1"], model_label)
                print(f"probe {det}/P1: cost=¥{r['cost_jpy']} err={r['error']} usage={r['usage']}")
        costs = {d: load(os.path.join(CALLS, f"{d}_P1_1.json"))["cost_jpy"] for d in "ABC"}
        n_a, n_b, n_c = (len([1 for t in DETS[d] if SOURCES[t][2] == "pos"]) for d in "ABC")
        m_a, m_b, m_c = (len([1 for t in DETS[d] if SOURCES[t][2] == "neg"]) for d in "ABC")
        for pos_n in (3, 2):
            est = sum(costs[d] * (n * pos_n + m * 2) for d, n, m in (("A", n_a, m_a), ("B", n_b, m_b), ("C", n_c, m_c)))
            print(f"見込み pos_n={pos_n}, neg_n=2: 合計{sum(n * pos_n + m * 2 for n, m in ((n_a, m_a), (n_b, m_b), (n_c, m_c)))} call, "
                  f"概算¥{est:.2f}(probe単価ベース、検出器別)")
        print("累計(専用state): ¥%.4f" % state["cumulative_jpy"])
        return
    # main
    for det, tid, k in planned(a.pos_n, a.neg_n):
        if done(det, tid, k):
            continue
        if state["cumulative_jpy"] >= a.budget_jpy:
            print(f"予算¥{a.budget_jpy}到達のため停止(未実施のcallが残る)。")
            break
        r = call_one(rc, state, ce, det, tid, k, inputs[tid], model_label)
        print(f"{det}/{tid}/{k}: cost=¥{r['cost_jpy']} err={r['error']} 累計¥{state['cumulative_jpy']:.3f}")
    print("累計(専用state): ¥%.4f" % state["cumulative_jpy"])


if __name__ == "__main__":
    main()
