# -*- coding: utf-8 -*-
"""FAMILY-X-WRITER-DETECTIVE-WORD-AVOIDANCE-TRIAL-01 評価(決定論Grep + LLM判定 + QCD集計)。

LLM判定は gpt-6-luna(judge_prompts_01.json全文)。Baseline/A/B/Cはラベルを伏せ(X1..)ランダム順で提示、2回実行。
再実行時は eval/ 配下のキャッシュ(judgments_*.json)があれば再利用する(--force-llmで再実行)。
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import time

import er086_writer_detective_avoidance_trial_01_lib as lib

VARIANTS = ["Baseline", "A", "B", "C"]
CRITERIA = ["hook", "flow", "surprise_structure", "readability_pull", "no_unnatural_staging"]
SIMILAR_EN = lib.SIMILAR_RE
JUDGE_PROMPTS = os.path.join(lib.DOC_DIR, "judge_prompts_01.json")


def vdir(root, base, v):
    if v == "Baseline":
        return base
    d = os.path.join(root, v)
    if not os.path.exists(os.path.join(d, "a2", "article.md")) and os.path.exists(os.path.join(root, v + "_rerun1", "a2", "article.md")):
        return os.path.join(root, v + "_rerun1")   # 初回がProduction Gate(JA記号QA)でSTOPした場合の再生成分(結果に明記)
    return d


def load_variant(root, base, v):
    d = vdir(root, base, v)
    g = lambda rel: lib.read_text(os.path.join(d, rel)) if os.path.exists(os.path.join(d, rel)) else None
    return {"dir": d, "R0": g("ja_writer/original.md"), "R1": g("ja_writer/revision1.md"), "R2": g("ja_writer/revision2.md"),
            "Adv": g("b1b/article.md"), "Std": g("a2/article.md")}


def parse_json(text):
    i, j = text.find("{"), text.rfind("}")
    return json.loads(text[i:j + 1])


def llm_call(client, cl, system, user, stage, effort="medium"):
    with cl.logging_context("DWA_TRIAL_01_EVAL", stage):
        r = client.responses.create(model="gpt-6-luna", reasoning={"effort": effort},
                                    input=[{"role": "developer", "content": system}, {"role": "user", "content": user}])
    return r.output_text, getattr(r, "model", None), getattr(r, "id", None)


def run_entertainment(client, cl, jp, arts, level, run_idx, evdir, force):
    cache = os.path.join(evdir, f"judgment_ent_{level}_run{run_idx}.json")
    if os.path.exists(cache) and not force:
        return json.loads(lib.read_text(cache))
    order = list(VARIANTS)
    random.Random(1000 + run_idx * 7 + (0 if level == "Adv" else 1)).shuffle(order)
    ids = {v: f"X{k + 1}" for k, v in enumerate(order)}
    blocks = "".join(jp["article_block_template"].format(id=ids[v], text=arts[v].strip()) + "\n" for v in order)
    user = jp["entertainment_user_template"].format(n=len(order), articles=blocks)
    raw, model, rid = llm_call(client, cl, jp["entertainment_system"], user, f"ent_{level}_{run_idx}", "medium")
    rec = {"level": level, "run": run_idx, "label_map": ids, "order": order, "model": model, "response_id": rid, "raw": raw,
           "parsed": parse_json(raw)}
    lib.write_text(cache, json.dumps(rec, ensure_ascii=False, indent=2))
    return rec


def run_fact(client, cl, jp, ledger, art, v, level, evdir, force):
    cache = os.path.join(evdir, f"judgment_fact_{level}_{v}.json")
    if os.path.exists(cache) and not force:
        return json.loads(lib.read_text(cache))
    user = jp["fact_user_template"].format(ledger=ledger, article=art.strip())
    raw, model, rid = llm_call(client, cl, jp["fact_system"], user, f"fact_{level}_{v}", "medium")
    rec = {"variant": v, "level": level, "model": model, "response_id": rid, "raw": raw, "parsed": parse_json(raw)}
    lib.write_text(cache, json.dumps(rec, ensure_ascii=False, indent=2))
    return rec


def mean(xs):
    return round(sum(xs) / len(xs), 3) if xs else None


def ent_scores(recs, v):
    out = {c: [] for c in CRITERIA}
    for r in recs:
        s = r["parsed"]["scores"][r["label_map"][v]]
        for c in CRITERIA:
            out[c].append(s[c]["score"])
    return out


def capitalized_unsupported(article, source_text):
    low = source_text.lower()
    toks = set(re.findall(r"\b[A-Z][a-zA-Z\-]{2,}\b", article)) | set(re.findall(r"\b\d[\d,\.]*\b", article))
    return sorted(t for t in toks if t.lower() not in low)


def houthi_sentences(article):
    sents = re.split(r"(?<=[\.\?\!])\s+|\n+", article)
    return [s for s in sents if re.search(r"Houthi|Ansar", s)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--force-llm", action="store_true")
    ap.add_argument("--no-llm", action="store_true")
    a = ap.parse_args()
    root, base = a.root, a.baseline
    evdir = os.path.join(root, "eval")
    os.makedirs(evdir, exist_ok=True)
    jp = json.loads(lib.read_text(JUDGE_PROMPTS))
    ledger = lib.read_text(os.path.join(base, "research_ledger/verified_fact_ledger.txt"))
    brief = lib.read_text(os.path.join(base, "storyline_b3/selected_brief_annotated.md"))
    V = {v: load_variant(root, base, v) for v in VARIANTS if os.path.exists(vdir(root, base, v))}
    res = {"variants": list(V)}

    # 1. detective count(工程別) + 類似語観測
    det = {}
    for v, d in V.items():
        det[v] = {}
        for st in ("R0", "R1", "R2", "Adv", "Std"):
            t = d[st]
            if t is None:
                det[v][st] = None
                continue
            c = lib.count_detective(t)
            det[v][st] = {**c, "snips": lib.context_snips(t, lib.DET_RE) + lib.context_snips(t, lib.JA_DET_RE, 20)}
    sim = {}
    for v, d in V.items():
        sim[v] = {}
        for st in ("R2", "Adv", "Std"):
            t = d[st] or ""
            rx = lib.JA_SIMILAR_RE if st == "R2" else SIMILAR_EN
            sim[v][st] = {"count": len(rx.findall(t)), "snips": lib.context_snips(t, rx, 40)}
    res["detective"], res["similar_observation"] = det, sim

    # 2. QCD
    qcd = {}
    for v in V:
        d = V[v]["dir"]
        cj = json.loads(lib.read_text(os.path.join(d, "cost.json"))) if os.path.exists(os.path.join(d, "cost.json")) else {}
        bs = cj.get("by_stage_jpy", {})
        wr = {k: x for k, x in bs.items() if k.startswith("w1_") or k in ("advanced", "standard")}
        n_calls = None
        lp = os.path.join(d, "raw_usage_log.jsonl")
        calls = []
        if os.path.exists(lp):
            for line in lib.read_text(lp).splitlines():
                if line.strip():
                    r = json.loads(line)
                    if r.get("stage") in wr:
                        calls.append(r)
        n_calls = len(calls)
        models = sorted({c.get("model_id") for c in calls if c.get("model_id")})
        retries = sum(1 for c in calls if not c.get("success", True))   # attempt_numberはstage内の通番でIOL呼出も2になるためretry判定に使わない
        llm_sec = round(sum(c.get("elapsed_seconds") or 0 for c in calls), 1)
        ws = {}
        wp = os.path.join(d, "writer_run_summary.json")
        if os.path.exists(wp):
            ws = json.loads(lib.read_text(wp))
        tr = {}
        tp = os.path.join(d, "trial_run_summary.json")
        if os.path.exists(tp):
            tr = json.loads(lib.read_text(tp))
        qcd[v] = {"writer_stage_jpy": wr, "writer_total_jpy": round(sum(wr.values()), 3), "llm_calls_writer_stages": n_calls,
                  "models": models, "failed_or_retried_calls": retries,
                  "adv_retried": (ws.get("advanced") or {}).get("retried"), "adv_para_retried": (ws.get("advanced") or {}).get("paragraph_retried"),
                  "std_retried": (ws.get("standard") or {}).get("retried"), "std_para_retried": (ws.get("standard") or {}).get("paragraph_retried"),
                  "timings": tr.get("timings"), "llm_elapsed_sum_sec": llm_sec, "chars": {st: len(V[v][st] or "") for st in ("R2", "Adv", "Std")}}
    res["qcd"] = qcd

    # 3. 決定論の事実検査
    src = ledger + "\n" + brief
    fdet = {}
    for v, d in V.items():
        fdet[v] = {}
        for st in ("Adv", "Std"):
            t = d[st] or ""
            fdet[v][st] = {"unsupported_tokens": capitalized_unsupported(t, src), "houthi_sentences": houthi_sentences(t)}
    res["fact_deterministic"] = fdet

    # 4. LLM判定
    if not a.no_llm:
        import er005_cost_logger as cl
        import er003_v1_en_direct_vfl_01_generate as vfl01
        cl.install(os.path.join(evdir, "raw_usage_log.jsonl"))
        client = vfl01.get_client()
        ent = {}
        for level, st in (("Adv", "Adv"), ("Std", "Std")):
            arts = {v: V[v][st] for v in V}
            recs = [run_entertainment(client, cl, jp, arts, level, k, evdir, a.force_llm) for k in (1, 2)]
            ent[level] = {}
            for v in V:
                sc = ent_scores(recs, v)
                ent[level][v] = {"per_criterion_mean": {c: mean(sc[c]) for c in CRITERIA}, "per_run_mean": [mean([sc[c][i] for c in CRITERIA]) for i in (0, 1)],
                                 "mean": mean([x for c in CRITERIA for x in sc[c]]),
                                 "quotes": {c: [r["parsed"]["scores"][r["label_map"][v]][c]["quote"] for r in recs] for c in CRITERIA},
                                 "rank_positions": [r["parsed"].get("overall_ranking_best_to_worst", []).index(r["label_map"][v]) + 1
                                                    if r["label_map"][v] in r["parsed"].get("overall_ranking_best_to_worst", []) else None for r in recs]}
            ent[level]["_judge"] = {"model": recs[0]["model"], "label_maps": [r["label_map"] for r in recs]}
        res["entertainment"] = ent
        fct = {}
        for level, st in (("Adv", "Adv"), ("Std", "Std")):
            fct[level] = {}
            for v in V:
                fct[level][v] = run_fact(client, cl, jp, ledger, V[v][st], v, level, evdir, a.force_llm)["parsed"]
        res["fact_llm"] = fct
        res["judge_cost"] = __import__("er053_cost_aggregate_01").compute_stage_cost_breakdown_multi(os.path.join(evdir, "raw_usage_log.jsonl"))

    # 5. 機械判定
    man_p = os.path.join(lib.DOC_DIR, "manual_fact_review_01.json")
    manual = json.loads(lib.read_text(man_p)) if os.path.exists(man_p) else {}
    machine = {}
    if "entertainment" in res:
        for v in V:
            if v == "Baseline":
                continue
            d0 = det[v]
            det_ok = all((d0[st] or {}).get("substring_ci", 1) == 0 for st in ("Adv", "Std"))
            n_major = sum((res["fact_llm"][lv][v] or {}).get("new_major_error_count", 0) or 0 for lv in ("Adv", "Std"))
            mj = manual.get(v, {}).get("major_errors")
            fact_ok = (n_major == 0) and (mj == 0) if mj is not None else None
            ent_ok = res["entertainment"]["Adv"][v]["mean"] >= res["entertainment"]["Adv"]["Baseline"]["mean"] - 0.5
            ent_ok_std = res["entertainment"]["Std"][v]["mean"] >= res["entertainment"]["Std"]["Baseline"]["mean"] - 0.5
            status = ("PENDING_MANUAL_FACT_REVIEW" if fact_ok is None and det_ok and ent_ok else
                      "CANDIDATE" if (det_ok and fact_ok and ent_ok) else "NOT_CANDIDATE")
            machine[v] = {"detective_zero_adv_std": det_ok, "llm_new_major_errors": n_major, "manual_major_errors": mj,
                          "fact_ok": fact_ok, "entertainment_adv_ok": ent_ok, "entertainment_std_ok": ent_ok_std, "status": status}
        cands = [v for v in machine if machine[v]["status"] == "CANDIDATE"]
        machine["_overall"] = {"candidates": cands, "pick_if_tie_shortest_instruction": cands[0] if cands else None,
                               "label": ("CANDIDATE_MACHINE:" + ",".join(cands)) if cands else (
                                   "PENDING_MANUAL" if any(machine[v]["status"] == "PENDING_MANUAL_FACT_REVIEW" for v in machine if v != "_overall")
                                   else "REJECTED_CANDIDATE_MACHINE")}
    res["machine_judgment"] = machine
    lib.write_text(os.path.join(evdir, "results.json"), json.dumps(res, ensure_ascii=False, indent=2))
    lib.write_text(a.out, render_md(res))
    print("[EVAL] wrote", a.out, "overall=", (machine.get("_overall") or {}).get("label"))


def render_md(res):
    L = ["# COMPARISON_RESULT_01: Writer Detective単語回避 Trial 比較結果", "",
         "- 生成: `er086_output/writer_detective_avoidance_trial_01/{A,B,C}`、Baseline=`er019_output/middle_east_yemen_saudi/run_mey_02`(変更なし)。詳細=`eval/results.json`。",
         "- 注: Pattern Aの初回生成(out-dir `A`)はProduction JA記号QA(R2再実行後も全角コロン残存)でSTOPし本文未完成のため、評価には再生成分(`A_rerun1`、同一条件)を使用。初回A費用JPY14.221は総費用に含む。",
         "- 注: 各Pattern n=1。Production過去のFamily X JA R2 24件中の『探偵』出現は2件(約8%、Grep)であり、n=1でdetective=0でも追加指示の効果の証明にはならない(効果判定ではなく『単語を消しつつ品質を保てるか』の確認)。",
         "- 評価LLM: " + str((res.get("entertainment", {}).get("Adv", {}).get("_judge") or {}).get("model")) + "(ラベル伏せ・ランダム順・2回)。", ""]
    L += ["## 1. detective件数(工程別、大小文字不問substring/派生/JA探偵)", "", "| 変種 | R0(JA) | R1(JA) | R2(JA) | Advanced | Standard |", "|---|---|---|---|---|---|"]
    for v in res["variants"]:
        row = []
        for st in ("R0", "R1", "R2", "Adv", "Std"):
            c = res["detective"][v][st]
            row.append("-" if c is None else (f"探偵{c['ja_tantei']}" if st in ("R0", "R1", "R2") else f"{c['substring_ci']}(派生{c['derivatives_ci']})"))
        L.append(f"| {v} | " + " | ".join(row) + " |")
    L += ["", "出現文(0件でないもののみ):"]
    for v in res["variants"]:
        for st in ("R2", "Adv", "Std"):
            c = res["detective"][v][st]
            if c and c["snips"]:
                L.append(f"- {v}/{st}: " + " / ".join(f"「…{s}…」" for s in c["snips"]))
    L += ["", "## 2. 類似語観測(件数と文脈のみ。禁止リスト化しない)", "", "| 変種 | R2(JA) | Advanced | Standard |", "|---|---|---|---|"]
    for v in res["variants"]:
        L.append(f"| {v} | {res['similar_observation'][v]['R2']['count']} | {res['similar_observation'][v]['Adv']['count']} | {res['similar_observation'][v]['Std']['count']} |")
    L.append("")
    for v in res["variants"]:
        for st in ("R2", "Adv"):
            s = res["similar_observation"][v][st]["snips"]
            if s:
                L.append(f"- {v}/{st}: " + " / ".join(f"「…{x}…」" for x in s))
    if "entertainment" in res:
        L += ["", "## 3. Entertainment(LLM判定、5観点×2回の平均、1〜5)", ""]
        for level in ("Adv", "Std"):
            L += [f"### {level}", "", "| 変種 | 平均 | " + " | ".join(CRITERIA) + " | run1平均 | run2平均 | 順位(run1,run2) |", "|---|---|" + "---|" * (len(CRITERIA) + 3)]
            for v in res["variants"]:
                e = res["entertainment"][level][v]
                L.append(f"| {v} | {e['mean']} | " + " | ".join(str(e['per_criterion_mean'][c]) for c in CRITERIA) + f" | {e['per_run_mean'][0]} | {e['per_run_mean'][1]} | {e['rank_positions']} |")
            L.append("")
        L += ["根拠引用(hook、run1/run2):"]
        for level in ("Adv",):
            for v in res["variants"]:
                L.append(f"- {level}/{v}: " + " / ".join(f"「{q}」" for q in res["entertainment"][level][v]["quotes"]["hook"]))
        L += ["", "## 4. 事実(決定論 + LLM事実検査)", "", "| 変種 | レベル | LLM unsupported件数(MAJOR/MINOR) | new_major_error_count | Houthi launcher | 連合軍報道官帰属 | Ledger+briefに無い固有語/数字 |", "|---|---|---|---|---|---|---|"]
        for lv in ("Adv", "Std"):
            for v in res["variants"]:
                f = res["fact_llm"][lv][v]
                uc = f.get("unsupported_claims", [])
                mj = sum(1 for x in uc if str(x.get("severity", "")).upper() == "MAJOR")
                h = f.get("houthi_attribution", {})
                L.append(f"| {v} | {lv} | {len(uc)}({mj}/{len(uc) - mj}) | {f.get('new_major_error_count')} | {h.get('houthis_named_as_launcher')} | {h.get('attributed_to_coalition_spokesperson')} | {', '.join(res['fact_deterministic'][v][lv]['unsupported_tokens'])} |")
        L += ["", "### LLM指摘の詳細(unsupported_claims)", ""]
        for lv in ("Adv", "Std"):
            for v in res["variants"]:
                for x in res["fact_llm"][lv][v].get("unsupported_claims", []):
                    L.append(f"- {v}/{lv} [{x.get('severity')}] 「{x.get('sentence')}」: {x.get('reason')}")
        L += ["", "### Houthi言及文(Advanced)", ""]
        for v in res["variants"]:
            for s in res["fact_deterministic"][v]["Adv"]["houthi_sentences"]:
                L.append(f"- {v}: {s}")
    L += ["", "## 5. QCD(Writer工程のみ。Research/B3/RF/音声は含まない)", "",
          "| 変種 | Writer費用JPY | R0 | R1 | R2 | Advanced(英訳+IOL) | Standard | LLM呼出数 | 失敗呼出(success=False) | Adv/Std 段落retry | LLM呼出秒合計 / 壁時計秒(writer/adv/std/total) | 文字数(R2JA/Adv/Std) |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for v in res["variants"]:
        q = res["qcd"][v]
        s = q["writer_stage_jpy"]
        t = q.get("timings") or {}
        L.append(f"| {v} | {q['writer_total_jpy']} | {s.get('w1_r0')} | {s.get('w1_astra_r1')} | {s.get('w1_astra_r2')} | {s.get('advanced')} | {s.get('standard')} | {q['llm_calls_writer_stages']} | {q['failed_or_retried_calls']} | {q['adv_para_retried']}/{q['std_para_retried']} | {q['llm_elapsed_sum_sec']} / {t.get('writer_sec')}/{t.get('advanced_sec')}/{t.get('standard_sec')}/{t.get('total_sec')} | {q['chars']['R2']}/{q['chars']['Adv']}/{q['chars']['Std']} |")
    L.append("")
    L.append("モデル: " + "; ".join(f"{v}={res['qcd'][v]['models']}" for v in res["variants"]))
    if "judge_cost" in res:
        L.append(f"評価LLM費用(判定): JPY {res['judge_cost'].get('total_jpy')}")
    if res.get("machine_judgment"):
        L += ["", "## 6. 機械判定(事前固定規則)", "", "```json", json.dumps(res["machine_judgment"], ensure_ascii=False, indent=2), "```"]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    sys.exit(main())
