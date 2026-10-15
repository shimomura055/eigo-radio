# -*- coding: utf-8 -*-
"""KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01 委任_02: 有料Trial T1(P1〜P7)/T2(実API少額、予算引数)。DEV/Trial専用(量産runではない)。

Trial専用経路: ga.run_alignment_gate_corrected(mode=corrected、item単位retry、「～」条件なし、追加内容語span対応はrecord-only+gate判定を並記)
を、承認済み規則の実行時抽出(sha256 447e07cb...)込みで、強制投入した合成/実記録itemへ直接かける。Production runner・Prompt・Gateは通らない。
モデル=現行SUPPORT_MODEL(routing.require_model("A2_SUPPORT"))、reasoning effort=high(現行と同一)。独立batch(<=5 item)は並列実行。
usage: .venv/Scripts/python.exe er071_gloss_alignment_correction_01_trial.py --mode corrected --plan <TRIAL_PLAN_02.md> --patterns P1,P2,P3,P4,P5,P6,P7 --reps 2 --budget-jpy 10 --out <dir>
       .venv/Scripts/python.exe er071_gloss_alignment_correction_01_trial.py --mode corrected --plan <TRIAL_PLAN_02.md> --patterns T2 --reps 2 --budget-jpy 10 --out <dir>
(P6はKP短縮/一般化=対象外でAPIに乗らないため、O1でオフライン検証済み。指定されても実行対象は空)
"""
import argparse
import concurrent.futures as cf
import json
import math
import os
import subprocess
import sys
import threading
import time

sys.stdout.reconfigure(encoding="utf-8")
# KP-GLOSS-ALIGNMENT-PRODUCTION-01 委任_03: gloss再整合は既定OFF。DEV/Trialは明示ON(flagが唯一のkill switch。import前に設定)。
os.environ["EIGO_KP_GLOSS_ALIGNMENT"] = "1"
print("Trial: gloss alignment explicitly ON (EIGO_KP_GLOSS_ALIGNMENT=1)")

import er003_key_words_gloss_alignment as ga  # noqa: E402
import er006_model_routing_contract_01 as routing  # noqa: E402

MANAGED_ID = "KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01"


def it(pid, display, kp, gloss, sentence, expect, kw=None, note=""):
    """expect: UNCHANGED(整合済み/自然な既存glossは不変であるべき) / MUST_CHANGE(欠落語を補うべき) / OBSERVE(期待を置かず観察)。
    kw: MUST_CHANGEの自動判定用(各要素=代替語のlist。全要素にヒットで『欠落語が反映された』と機械的に近似。最終判断は目視)。"""
    return {"pattern": pid, "display_phrase": display, "key_phrase": kp, "japanese_gloss": gloss, "source_sentence": sentence,
            "expect": expect, "kw": kw or [], "note": note}


CATALOG = {
    # P1: 拡張KP・既知不整合(実記録由来6ユニーク。3表記違い含む)
    "P1": [
        it("P1", "based on", "based on interviews", "～をもとにした", "However, \"about nine months\" is an estimate based on interviews", "MUST_CHANGE", [["インタビュー", "取材", "聞き取り"]]),
        it("P1", "based on", "based on interviews", "〜をもとにして", "However, \"about nine months\" is an estimate based on interviews", "MUST_CHANGE", [["インタビュー", "取材", "聞き取り"]]),
        it("P1", "raw-bean", "raw-bean prices", "焙煎前のコーヒー豆", "They estimate raw-bean prices take at least about nine months to appear in US shop prices", "MUST_CHANGE", [["価格", "値段", "相場", "値"]]),
        it("P1", "bring in", "bring in a human helper", "人を呼んで加える", "So, is it wrong by itself to bring in a human helper", "MUST_CHANGE", [["助っ人", "手伝", "助け", "ヘルパー", "人の手", "補助"]]),
        it("P1", "close around", "close around me", "周りから迫ってくる", "Inside, the rows of books seemed to close around me.", "MUST_CHANGE", [["私", "自分", "わたし"]]),
        it("P1", "the urge to", "urge to watch", "～したい衝動", "She felt the urge to watch the sea again.", "MUST_CHANGE", [["見", "眺め", "観"]]),
    ],
    # P2: 既に正しいgloss(不変保証の実測)
    "P2": [
        it("P2", "be locked into", "locked into a narrow view", "狭い見方に閉じ込められる", "the other fears being quietly locked into a narrow view.", "UNCHANGED"),
        it("P2", "based on", "based on interviews", "インタビューをもとにした", "However, \"about nine months\" is an estimate based on interviews", "UNCHANGED"),
    ],
    # P3: 「～」を含む正当な辞書表現(対象へ強制投入。規則15行型の`put solo travel at`は外し、P4bへ)
    "P3": [
        it("P3", "point to", "point to", "～を示す", "Recent studies point to a steady rise in demand.", "UNCHANGED"),
        it("P3", "answer for", "answer for", "～の責任を負う", "The manager must answer for the delay.", "UNCHANGED"),
        it("P3", "keep up with", "keep up with", "～に遅れずについていく", "It is hard to keep up with new technology.", "UNCHANGED"),
        it("P3", "fall into", "fall into", "～に落ちる", "Many small shops fall into debt within a year.", "UNCHANGED"),
        it("P3", "speak for", "speak for", "～の代わりに話す", "No one can speak for every customer.", "UNCHANGED"),
        it("P3", "turn out not to be", "turn out not to be", "結局〜ではないと分かる", "The rumor turned out not to be true.", "UNCHANGED"),
        it("P3", "be associated with", "be associated with", "～と関連している", "Long hours are associated with poor sleep.", "UNCHANGED"),
        it("P3", "put good odds on", "put good odds on", "～の可能性が高いと見る", "Experts put good odds on a quick recovery.", "UNCHANGED"),
    ],
    # P4: 具体語欠落の注入(合成): glossが追加された目的語/修飾語を落としている
    "P4": [
        it("P4", "lead to", "lead to higher costs", "～につながる", "Poor planning can lead to higher costs for everyone.", "MUST_CHANGE", [["費用", "コスト", "経費", "出費"], ["高", "増", "上"]]),
        it("P4", "point to", "point to the cause", "～を示す", "The data point to the cause of the failure.", "MUST_CHANGE", [["原因"]]),
        it("P4", "based on", "based on public data", "～をもとにした", "The forecast is based on public data from the city.", "MUST_CHANGE", [["公"], ["データ", "情報", "資料"]]),
        it("P4", "put pressure on", "put pressure on small firms", "～に圧力をかける", "The new rule puts pressure on small firms.", "MUST_CHANGE", [["小"], ["企業", "会社", "事業", "店", "商店"]]),
        it("P4", "rely on", "rely on local farmers", "～に頼る", "The town relies on local farmers for its food.", "MUST_CHANGE", [["地元", "地域", "近隣", "地方"], ["農"]]),
        it("P4", "run out of", "run out of fresh water", "～を使い果たす", "The village may run out of fresh water by summer.", "MUST_CHANGE", [["真水", "淡水", "きれいな水", "新鮮", "清潔", "飲み水", "水"]]),
    ],
    # P4b: 承認規則15行違反型(数値の穴埋め必須)。期待NG側として観察のみ(選定段で除外されるべき表現。再整合段の合否に使わない)
    "P4b": [
        it("P4b", "put solo travel at", "put solo travel at", "ソロ旅行を～％とする", "Analysts put solo travel at ten percent of all trips.", "OBSERVE", note="規則15行違反型(期待NG)"),
    ],
    # P5: 人称・主語語
    "P5": [
        it("P5", "close in", "close in on me", "迫ってくる", "The walls began to close in on me.", "MUST_CHANGE", [["私", "自分", "わたし"]]),
        it("P5", "take", "take one's time", "取る", "You should take your time with this decision.", "MUST_CHANGE", [["ゆっくり", "時間", "急がず"]]),
        it("P5", "catch", "catch one's breath", "捕まえる", "We stopped to catch our breath.", "MUST_CHANGE", [["息"]]),
    ],
    # P7: 追加語あり x 自然な慣用的訳が正解(機械検査の誤NG・直訳化・HR到達率の測定)
    "P7": [
        it("P7", "bring in", "bring in a human helper", "人の手を借りる", "So, is it wrong by itself to bring in a human helper", "UNCHANGED", note="多語->1span(人の手)"),
        it("P7", "raw-bean", "raw-bean prices", "生豆の値段", "They estimate raw-bean prices take at least about nine months to appear in US shop prices", "UNCHANGED", note="ハイフン複合語->生豆"),
        it("P7", "close around", "close around me", "私を取り囲むように迫る", "Inside, the rows of books seemed to close around me.", "UNCHANGED", note="機能語around+代名詞me"),
        it("P7", "make ends", "make ends meet", "やりくりする", "Many families struggle to make ends meet.", "UNCHANGED", note="慣用句全体->1語(meet)"),
        it("P7", "break", "break the ice", "緊張をほぐす", "A joke can help break the ice at a meeting.", "UNCHANGED", note="慣用句(ice)"),
        it("P7", "spill", "spill the beans", "うっかり秘密をばらす", "Someone spilled the beans about the plan.", "UNCHANGED", note="慣用句(beans)"),
    ],
    # T2: span実在・意味違いの注入(誤PASS検出力)。currentは不自然/誤訳で、LLMは不一致と判定すべき
    "T2": [
        it("T2", "based on", "based on interviews", "ニュースをもとにした", "However, \"about nine months\" is an estimate based on interviews", "MUST_CHANGE", [["インタビュー", "取材", "聞き取り"]], "span(ニュース)は存在するが別語"),
        it("T2", "raw-bean", "raw-bean prices", "焙煎前のコーヒー豆の量", "They estimate raw-bean prices take at least about nine months to appear in US shop prices", "MUST_CHANGE", [["価格", "値段", "相場", "値"]], "pricesを量と誤訳"),
        it("T2", "close around", "close around me", "彼らの周りから迫ってくる", "Inside, the rows of books seemed to close around me.", "MUST_CHANGE", [["私", "自分", "わたし"]], "me->彼ら"),
        it("T2", "bring in", "bring in a human helper", "機械の助けを借りる", "So, is it wrong by itself to bring in a human helper", "MUST_CHANGE", [["人"]], "human->機械"),
        it("T2", "lead to", "lead to higher costs", "利益の増加につながる", "Poor planning can lead to higher costs for everyone.", "MUST_CHANGE", [["費用", "コスト", "経費", "出費"]], "costs->利益"),
        it("T2", "put pressure on", "put pressure on small firms", "大企業に圧力をかける", "The new rule puts pressure on small firms.", "MUST_CHANGE", [["小"]], "small->大"),
        it("T2", "point to", "point to the cause", "結果を示す", "The data point to the cause of the failure.", "MUST_CHANGE", [["原因"]], "cause->結果"),
        it("T2", "rely on", "rely on local farmers", "外国の農家に頼る", "The town relies on local farmers for its food.", "MUST_CHANGE", [["地元", "地域", "近隣", "地方"]], "local->外国"),
        it("T2", "run out of", "run out of fresh water", "塩水を使い果たす", "The village may run out of fresh water by summer.", "MUST_CHANGE", [["真水", "淡水", "きれいな水", "飲み水", "新鮮"]], "fresh->塩"),
        it("T2", "take", "take one's time", "すぐに取る", "You should take your time with this decision.", "MUST_CHANGE", [["ゆっくり", "時間", "急がず"]], "意味反転"),
        it("T2", "spill", "spill the beans", "豆をこぼす", "Someone spilled the beans about the plan.", "MUST_CHANGE", [["秘密", "ばら", "漏"]], "直訳(慣用句の意味喪失)"),
        it("T2", "break", "break the ice", "氷を割る", "A joke can help break the ice at a meeting.", "MUST_CHANGE", [["緊張", "打ち解け", "雰囲気", "ほぐ", "和ら"]], "直訳(慣用句の意味喪失)"),
    ],
}


def clopper_pearson_upper(k, n, alpha=0.05):
    """片側95%上限(exact binomial)。n=0なら1.0。"""
    if n == 0:
        return 1.0
    if k >= n:
        return 1.0
    lo, hi = k / n, 1.0
    for _ in range(100):
        mid = (lo + hi) / 2
        cdf = sum(math.comb(n, i) * mid ** i * (1 - mid) ** (n - i) for i in range(k + 1))
        if cdf > alpha:
            lo = mid
        else:
            hi = mid
    return round(hi, 4)


def build_batches(patterns, reps):
    items = []
    for rep in range(1, reps + 1):
        for pid in patterns:
            for base in CATALOG.get(pid, []):
                items.append({**base, "rep": rep})
    batches = []
    for rep in range(1, reps + 1):
        seq = [x for x in items if x["rep"] == rep]
        for i in range(0, len(seq), 5):
            batches.append(seq[i:i + 5])
    return batches


def run_batch(idx, batch, model, rules, lock, state, budget):
    with lock:
        if state["cost"] > budget:
            return {"batch": idx, "skipped": "BUDGET_EXCEEDED", "rows": []}
    targets = []
    for j, x in enumerate(batch, 1):
        targets.append({"rank": j, "display_phrase": x["display_phrase"], "key_phrase": x["key_phrase"],
                        "japanese_gloss": x["japanese_gloss"], "source_sentence": x["source_sentence"]})
    article = "\n".join(x["source_sentence"] for x in batch)

    def make(msg):
        return ga.make_alignment_fn(msg, model=model, reasoning_effort="high", schema=ga.GLOSS_ALIGNMENT_JSON_SCHEMA_CORRECTED)
    t0 = time.time()
    gate = ga.run_alignment_gate_corrected(make, targets, article, rules, mapping_gate=False)
    cost = round(sum(a.get("cost_jpy") or 0 for a in gate["attempts"]), 4)
    with lock:
        state["cost"] += cost
        state["calls"] += len(gate["attempts"])
    rows = []
    for j, x in enumerate(batch, 1):
        log = gate["item_log"][j]
        adopted = gate["adopted"].get(j)
        first = log[0] if log else {}
        last = log[-1] if log else {}
        final_gloss = adopted["adopt_gloss"] if adopted else None
        probe = adopted or {}
        mc = (adopted or {}).get("machine_check") or last.get("machine_check")
        changed = (final_gloss is not None) and (ga._norm_tilde_space(final_gloss) != ga._norm_tilde_space(x["japanese_gloss"]))
        kw_hit = None
        if x["kw"] and final_gloss is not None:
            kw_hit = all(any(a in final_gloss for a in grp) for grp in x["kw"])
        if x["expect"] == "UNCHANGED":
            expected_ok = bool(adopted) and not changed
        elif x["expect"] == "MUST_CHANGE":
            expected_ok = bool(adopted) and changed and bool(kw_hit)
        else:
            expected_ok = None
        rows.append({
            "batch": idx, "pattern": x["pattern"], "rep": x["rep"], "display": x["display_phrase"], "kp": x["key_phrase"],
            "gloss_before": x["japanese_gloss"], "expect": x["expect"], "note": x["note"],
            "unresolved": adopted is None, "first_attempt_verdict": first.get("verdict"),
            "first_attempt_reasons": first.get("reasons"), "attempts_used": len(log),
            "final_gloss": final_gloss, "llm_current_consistent": (adopted or last).get("current_gloss_consistent") if adopted else last.get("current_gloss_consistent"),
            "changed": changed, "kw_hit": kw_hit, "expected_ok_auto": expected_ok,
            "machine_check_pass_gate": (mc or {}).get("pass"), "machine_check": mc,
            "added_word_mappings": (adopted or last).get("added_word_mappings") if adopted else last.get("added_word_mappings"),
            "reasoning": (adopted or last).get("reasoning") if adopted else last.get("reasoning"),
            "attempt_log": log,
        })
    return {"batch": idx, "cost_jpy": cost, "n_calls": len(gate["attempts"]), "elapsed_sec": round(time.time() - t0, 1),
            "attempts": [{k: v for k, v in a.items() if k not in ("parsed",)} for a in gate["attempts"]], "rows": rows}


def summarize(rows):
    def grp(pred):
        return [r for r in rows if pred(r)]
    out = {}
    pats = sorted({r["pattern"] for r in rows})
    for p in pats:
        pr = grp(lambda r: r["pattern"] == p)
        n = len(pr)
        d = {"n_evals": n,
             "first_attempt_invalid": sum(1 for r in pr if r["first_attempt_verdict"] != "VALID"),
             "unresolved_after_2": sum(1 for r in pr if r["unresolved"])}
        d["first_attempt_invalid_rate"] = round(d["first_attempt_invalid"] / n, 4) if n else None
        d["unresolved_rate"] = round(d["unresolved_after_2"] / n, 4) if n else None
        d["unresolved_rate_upper95"] = clopper_pearson_upper(d["unresolved_after_2"], n)
        ex = [r for r in pr if r["expected_ok_auto"] is not None]
        d["expected_ok_auto"] = sum(1 for r in ex if r["expected_ok_auto"])
        d["expected_evaluated"] = len(ex)
        if pr and pr[0]["expect"] == "UNCHANGED":
            changed = sum(1 for r in pr if r["changed"])
            d["unchanged_expected_but_changed"] = changed
            d["rewrite_rate_upper95"] = clopper_pearson_upper(changed, n)
            d["record_only_false_ng"] = sum(1 for r in pr if r["unresolved"] or r["changed"])
            d["gate_false_ng_extra"] = sum(1 for r in pr if (not r["unresolved"]) and (not r["changed"]) and r["machine_check_pass_gate"] is False)
            d["gate_false_ng_total"] = d["record_only_false_ng"] + d["gate_false_ng_extra"]
        if pr and pr[0]["expect"] == "MUST_CHANGE":
            d["false_pass_llm_said_consistent_or_unchanged"] = sum(1 for r in pr if (not r["unresolved"]) and not r["changed"])
            d["final_missing_keyword_auto"] = sum(1 for r in pr if (not r["unresolved"]) and r["changed"] and r["kw_hit"] is False)
            d["gate_would_catch_but_record_only_adopted"] = sum(1 for r in pr if (not r["unresolved"]) and r["machine_check_pass_gate"] is False)
        out[p] = d
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=["corrected"])
    ap.add_argument("--plan", required=True)
    ap.add_argument("--patterns", required=True)
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--budget-jpy", type=float, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=7)
    a = ap.parse_args()
    assert os.path.exists(a.plan), a.plan
    os.makedirs(a.out, exist_ok=True)
    # 有料run直前のSTOP確認(センチネル/STOP_NOTICE)。STOPなら新規API呼出をしない。
    rc = subprocess.run([sys.executable, "tools/stop_scope_check_01.py", "--managed-id", MANAGED_ID, "--run-dir", a.out],
                        capture_output=True, text=True).returncode
    if rc != 0:
        print("STOP applicable; no API calls")
        return 3
    patterns = [p.strip() for p in a.patterns.split(",") if p.strip()]
    expand = []
    for p in patterns:
        if p == "P4":
            expand += ["P4", "P4b"]
        else:
            expand.append(p)
    patterns = expand
    model = routing.require_model("A2_SUPPORT", routing.SUPPORT_MODEL)
    pf = ga.preflight(True)
    batches = build_batches(patterns, a.reps)
    print(f"mode={a.mode} model={model} effort=high patterns={patterns} reps={a.reps} batches={len(batches)} "
          f"evals={sum(len(b) for b in batches)} budget={a.budget_jpy} rules_sha256={pf['sha256'][:12]}")
    lock, state = threading.Lock(), {"cost": 0.0, "calls": 0}
    results = []
    t0 = time.time()
    with cf.ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(run_batch, i, b, model, pf["rules"], lock, state, a.budget_jpy): i for i, b in enumerate(batches, 1)}
        for f in cf.as_completed(futs):
            r = f.result()
            results.append(r)
            print(f"batch {r['batch']}/{len(batches)} cost={r.get('cost_jpy')} calls={r.get('n_calls')} cum={state['cost']:.4f}", flush=True)
    results.sort(key=lambda r: r["batch"])
    rows = [row for r in results for row in r["rows"]]
    summary = summarize(rows)
    models = sorted({a_.get("model") for r in results for a_ in r.get("attempts", []) if a_.get("model")})
    usage_tot = {"input_tokens": 0, "output_tokens": 0, "cached_input_tokens": 0}
    for r in results:
        for a_ in r.get("attempts", []):
            for k in usage_tot:
                usage_tot[k] += (a_.get("usage") or {}).get(k) or 0
    doc = {"managed_id": MANAGED_ID, "delegation": "03", "mode": a.mode, "patterns": patterns, "reps": a.reps,
           "model_requested": model, "models_returned": models, "reasoning_effort": "high", "rules_sha256": pf["sha256"],
           "n_batches": len(batches), "n_api_calls": state["calls"], "total_cost_jpy": round(state["cost"], 4),
           "budget_jpy": a.budget_jpy, "elapsed_sec": round(time.time() - t0, 1), "usage_total": usage_tot,
           "mapping_gate": False, "summary": summary, "batches": results, "rows": rows}
    tag = "_".join(patterns)
    json.dump(doc, open(os.path.join(a.out, f"results_{tag}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({"total_cost_jpy": doc["total_cost_jpy"], "n_api_calls": doc["n_api_calls"], "models": models,
                      "summary": summary}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
