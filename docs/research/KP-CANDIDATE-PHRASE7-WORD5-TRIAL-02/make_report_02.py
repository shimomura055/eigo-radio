# -*- coding: utf-8 -*-
"""Trial-02の集計(trial_runs_02.json / gate_results_02.json)とRESULT_02.md(候補全文)を生成する。判断文章は含めない。"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)
import er124_kp_phrase_word_trial_01 as t   # noqa: E402

P1 = os.path.join(ROOT, "docs", "research", "KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01")
own = json.load(open(os.path.join(HERE, "own_rubric_02.json"), encoding="utf-8"))
prev = json.load(open(os.path.join(P1, "trial_runs_01.json"), encoding="utf-8"))["runs"]
base = json.load(open(os.path.join(P1, "current_baseline_01.json"), encoding="utf-8"))["levels"]


def own_v(key, form):
    d = {k.lower(): v for k, v in own[key].items()}
    return d.get(form.lower())


def adv_fit(v):
    """③④適合(機械規則): N かつ note に『易しい/基本語』→不適合 / B かつ note に『基本寄り』→境界 / それ以外→適合。"""
    if not v:
        return "?"
    n = v["note"]
    if v["verdict"] == "N" and ("易しい" in n or "基本語" in n):
        return "不適合"
    if v["verdict"] == "B" and "基本寄り" in n:
        return "境界"
    return "適合"


def judge_map(p):
    if not os.path.exists(p):
        return {}
    rec = json.load(open(p, encoding="utf-8"))
    return {rec["candidates"][j["id"]]["used_form"].lower(): j for j in rec["judged"]}


def jv_prev(article, lv):
    return judge_map(os.path.join(P1, "judge", f"judge_{article}__{lv}.json"))


def jv_new(article, lv):
    return judge_map(os.path.join(HERE, "judge", f"judge_{article}__{lv}.json"))


def rows_of(cands, key, article, lv):
    """フレーズのjudge=前回judge再利用、単語のjudge=Trial-02 judge(単語のみ新規)。"""
    out = []
    for c in cands:
        f = c["used_form"]
        kind = t.classify_kind(f)
        ov = own_v(key, f)
        j = (jv_new(article, lv) if kind == "word" else jv_prev(article, lv)).get(f.lower())
        out.append({"rank": c.get("ai_rank"), "origin": c.get("origin"), "raw_rank": c.get("raw_rank"), "used_form": f, "kind": kind,
                    "gloss": c.get("japanese_gloss"), "reason_ja": c.get("reason_ja"),
                    "own": ov["verdict"] if ov else None, "own_note": ov["note"] if ov else None,
                    "judge": j["verdict"] if j else None, "judge_level_fit": j["level_fit"] if j else None,
                    "adv_fit": adv_fit(ov) if kind == "word" else None})
    return out


levels = {}
tot_cost = {"calls": 0, "jpy": 0.0}
for article in t.ARTICLES:
    for lv in t.LEVELS:
        key = f"{article}:{lv}"
        tag = f"{article}__{lv}__p7w5__r1"
        r = json.load(open(os.path.join(HERE, "runs", tag, "trial_result.json"), encoding="utf-8"))
        cost = t.cost_of_log(os.path.join(HERE, "runs", tag, "usage_log.jsonl"))
        tot_cost["calls"] += cost["calls"]
        tot_cost["jpy"] += cost["jpy"]
        st = r["state"]
        doc = r["doc"]
        pr = prev[f"{article}__{lv}__p7w3__r1"]
        cur = base[key].get("current")
        w5_raw = [i["phrase"] for i in json.loads(st["w3_raw"])["items"]]
        levels[key] = {
            "article": article, "level": lv, "tag": tag, "cost": cost, "elapsed_sec": r["elapsed_sec"],
            "p7_returned_reused": st["p7_returned"], "p7_calls": st["p7_calls"], "p7_reused_from": st.get("p7_reused_from"),
            "w5_returned": st["w3_returned"], "w5_calls": st["w3_calls"], "w5_raw_phrases": w5_raw, "w5_over_request": st["w3_over_request"],
            "w5_model": st["w3_model"], "w5_prompt_sha256": r["w5_prompt_sha256"], "p7_prompt_sha256": r["p7_prompt_sha256"],
            "p7_dropped": st["p7_dropped"], "doc_dropped": doc.get("dropped"), "redundancy_qa": (doc.get("redundancy_qa") or {}).get("status"),
            "outer_attempts": doc.get("outer_attempts"), "text_sha256": r["text_sha256"],
            "w5_final": rows_of(doc["candidates"], key, article, lv),
            "w3_r1_final": rows_of(pr["candidates"], key, article, lv),
            "current_final": rows_of((cur or {}).get("candidates") or prev.get(f"{article}__{lv}__current__r1", {}).get("candidates") or [], key, article, lv),
            "w3_r1_cost": t.cost_of_log(os.path.join(P1, "runs", f"{article}__{lv}__p7w3__r1", "usage_log.jsonl")),
            "w3_r1_elapsed_sec": pr.get("elapsed_sec"),
        }
tot_cost["jpy"] = round(tot_cost["jpy"], 3)
jc = t.cost_of_log(os.path.join(HERE, "judge", "usage_log.jsonl"))
json.dump({"n_runs": 6, "run_cost": tot_cost, "judge_cost": jc, "levels": levels},
          open(os.path.join(HERE, "trial_runs_02.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump({k: {"p7_dropped": v["p7_dropped"], "doc_dropped": v["doc_dropped"], "w5_raw": v["w5_raw_phrases"]} for k, v in levels.items()},
          open(os.path.join(HERE, "gate_results_02.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def fmt(rows):
    L = ["| 順位 | 区分 | 候補(used_form) | 意味 | 自(Y/B/N) | judge | ③④適合 | 備考(自ルーブリック理由) |", "|---|---|---|---|---|---|---|---|"]
    for x in rows:
        k = "フレーズ" if x["kind"] == "phrase" else "単語"
        L.append(f"| {x['rank']} | {k} | {x['used_form']} | {x['gloss']} | {x['own'] or '—'} | {x['judge'] or '—'} | {x['adv_fit'] or '—'} | {x['own_note'] or ''} |")
    return L


L = ["# RESULT_02 (KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02 委任_01、2026-10-26)", "",
     "自動生成(`make_report_02.py`)。Trial=P7(前回r1の返答を再利用・API 0)→W5(単語最大5)。Gate=Production関数同一適用。順位=最終候補の`ai_rank`(フレーズ→単語の順)。"
     "自=自ルーブリックY/B/N(`own_rubric_02.json`、judge前に確定)、judge=gpt-6.1-sol(フレーズは前回judge再利用、単語は今回新規)。"
     "③④適合=単語のみ(適合/境界[基本寄り]/不適合[易しい語])。", ""]
for key, v in levels.items():
    nph = sum(1 for x in v["w5_final"] if x["kind"] == "phrase")
    nw = sum(1 for x in v["w5_final"] if x["kind"] == "word")
    L.append(f"## {key}（{t.ARTICLES[v['article']]['ja']} / {t.LEVELS[v['level']]}）")
    L.append(f"- P7返答(再利用)={v['p7_returned_reused']}件、W5返答={v['w5_returned']}件(生の語: {', '.join(v['w5_raw_phrases'])})、最終 フレーズ{nph}＋単語{nw}、"
             f"call {v['cost']['calls']}、¥{v['cost']['jpy']}、{v['elapsed_sec']}秒、RQA={v['redundancy_qa']}")
    dr = v["p7_dropped"] + (v["doc_dropped"] or [])
    L.append("- Gate除外: " + ("; ".join(f"[{d.get('origin')}] {d['phrase']} ({d['stage']})" for d in dr) or "なし"))
    L.append("")
    L += fmt(v["w5_final"])
    L.append("")
open(os.path.join(HERE, "RESULT_02.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print(json.dumps({"run_cost": tot_cost, "judge_cost": {k: jc[k] for k in ("calls", "jpy")}}, ensure_ascii=False))
