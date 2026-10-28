# NUANCE-EXPLANATION-PRODUCTION-WIRING-01 委任_01b: results_v1/v2 + usage_log から prompt_trial_01.json と結果表(markdown断片)を生成 (API 0)
import os, sys, json, datetime
BASE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.abspath(os.path.join(BASE, ".."))
sys.path.insert(0, BASE)
import nuance_trial_01 as nt
from nuance_prompt_v2 import PROMPT_V2

def L(f): return json.load(open(os.path.join(OUT, f), encoding="utf-8"))
v1 = L("results_v1.json"); v1c = L("results_v1_control.json"); v2 = L("results_v2.json"); probe = L("judge_probe_01.json")
usage = [json.loads(l) for l in open(os.path.join(OUT, "usage_log_01.jsonl"), encoding="utf-8") if l.strip()]
cost_by_tag = {u["tag"]: u for u in usage}

# worker独立所見(Sonnet。モデル自己評価とは別。根拠はPROMPT_TRIAL_01.md §6)
WORKER = {
 ("v1", "ai_island_std"): ("高", "「少なくとも」を下限と取る日本語訳の落とし穴。文脈(一般化を避ける)が明確。"),
 ("v1", "ai_island_adv"): ("高", "同上。For this AI だけでも足りるが At least を足す含みの差まで述べる。"),
 ("v1", "paycheck_std"): ("中", "may の可能性/断定の差。B1既習の基礎寄りだが本文の因果慎重論と結びつく。"),
 ("v1", "paycheck_adv"): ("低", "don't have to vs mustn't はA2既習の基礎対比。Advanced学習者には価値が薄い(Trial-01のFable評価=基礎語の品詞比較不可と同型)。"),
 ("v1", "tth_std"): ("高", "You should have seen ... を『見るべきだった』と誤読しやすい。誇張表現として語感が明確。"),
 ("v1", "tth_adv"): ("中", "perhaps の控えめな認めと perfectly sane の断言の対照。語は基礎的だが対照の読みが本文固有で物語解釈寄り。"),
 ("v1", "y_redelivery_std"): ("中", "feel right to me の主観化。語義説明に近くKP型イディオムの補足に寄る(Adv側KPは sit right)。"),
 ("v1", "y_redelivery_adv"): ("中", "I'd be happy if ... の控えめな要望。仮定法の仕組み(文法コーナー領域)に隣接。"),
 ("v1c", "control_trivial"): ("低", "人工の平易文で stood vs stood up を強制選定=0件が出せない証拠。"),
 ("v2", "ai_island_std"): ("誤り(見逃し)", "0件。ただし同記事Advでは at least を選定。at least は v1 で高価値だったため too_basic 判定は過剰抑制(Std/Adv不整合)。"),
 ("v2", "ai_island_adv"): ("高", "v1と同表現。4条件の根拠(criteria_check)が具体的。"),
 ("v2", "paycheck_std"): ("中〜高", "be linked to=関連≠因果の語感。ただしKP『weak link』と語・論点が近接し、段1構造検査がfail→破棄(境界事例)。"),
 ("v2", "paycheck_adv"): ("妥当(0件)", "v1の低価値候補を回避。残る候補(may have affected 等)は基礎的/記事理解寄りという判断は妥当。"),
 ("v2", "tth_std"): ("高", "v1と同表現。should have の『義務』誤読の落とし穴を明記。"),
 ("v2", "tth_adv"): ("妥当(やや惜しい)", "0件。v1候補(perhaps)は中程度だったので、0件は許容範囲。Std側は You should have seen を選んだのにAdvでは grammar_structure として外す不整合あり。"),
 ("v2", "y_redelivery_std"): ("中", "Am I wrong to feel this way? の意見をやわらげる含み。会話上の含みで文法ではないが価値は中程度。"),
 ("v2", "y_redelivery_adv"): ("中〜高", "I guess it can't be helped の『諦め≠賛成』。ただしこの句は同記事StdのKP。Adv内ではKP/Wordと非重複だが『KP級の定型句』である点に注意。"),
 ("v2", "control_trivial"): ("妥当(0件)", "人工の平易文で0件を返せた=『0件を選べる』ことの確認。"),
}

def entry(ver, key, r, tpl_sha):
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(timespec="seconds")
    cand = r.get("candidate_raw")
    gu = r.get("gen_usage") or {}; ju = r.get("judge_usage") or {}
    e = dict(schema="nuance_candidate_v1", family=r.get("family"), article_id=r.get("article"), level=("standard" if r.get("level") == "Standard" else "advanced"), generated_at=now,
             candidate=None, no_candidate_reason=None,
             kp_word_basis=dict(status=r["kp_word_basis"]["status"], items=r["kp_word_basis"]["items"], source_path=r["kp_word_basis"]["source_path"]),
             model=gu.get("model_actual"), prompt_sha=r.get("prompt_sha"),
             usage=dict(input_tokens=gu.get("input_tokens", 0) + ju.get("input_tokens", 0), output_tokens=gu.get("output_tokens", 0) + ju.get("output_tokens", 0), cost_jpy=round(gu.get("cost_jpy", 0) + ju.get("cost_jpy", 0), 4)),
             trial_extra=dict(target_key=key, version=ver, rejected_candidates=r.get("rejected_candidates"), worker_value_assessment=dict(zip(("rating", "note"), WORKER.get((ver if key != "control_trivial" or ver == "v2" else "v1c", key), ("", ""))))))
    if cand:
        s1 = r["stage1_structural"]; s2 = r["stage2_llm"]
        oc = dict(verdict=r["final_overlap_verdict"], stage1_structural=dict(verdict=s1["verdict"], matched=s1["matched"]),
                  stage2_llm=dict(verdict=s2["verdict"], reason=s2["reason"], model=s2["model"]),
                  reason=("構造検査fail: " + str(s1["matched"]) if s1["verdict"] == "fail" else s2["reason"]),
                  against=[dict(item=p.get("item"), kind="kp|word", same_focus=p.get("same_focus"), note=p.get("note")) for p in (s2.get("per_item") or [])])
        c = dict(expression=cand["expression"], focus=cand["focus"], explanation_ja=cand["explanation_ja"], quote_en=cand["quote_en"], quote_ja=cand["quote_ja"], overlap_check=oc)
        e["trial_extra"].update(quote_verbatim=r.get("quote_verbatim"), explanation_len=r.get("explanation_len"), model_self_rating=cand.get("learning_value_self_rating"),
                                differs_from_kp_word_ja=cand.get("differs_from_kp_word_ja"), learning_value_reason_ja=cand.get("learning_value_reason_ja"), criteria_check=cand.get("criteria_check"))
        if r["final_overlap_verdict"] == "pass": e["candidate"] = c
        else:
            e["no_candidate_reason"] = "overlap_ng"; e["trial_extra"]["rejected_candidate_audit"] = c
    else:
        e["no_candidate_reason"] = r.get("no_candidate_reason") or "no_candidate"
    return e

runs = dict(v1=[entry("v1", k, r, "") for k, r in v1.items()] + [entry("v1", "control_trivial", v1c["control_trivial"], "")],
            v2=[entry("v2", k, r, "") for k, r in v2.items()])
tot = round(sum(u["cost_jpy"] for u in usage), 4)
data = dict(schema_note="各要素は WIRING_DESIGN_01.md §3 の nuance_candidate_v1 に準拠。candidate は overlap_check.verdict==pass のときのみ非null、fail時は candidate=null・no_candidate_reason='overlap_ng' とし破棄前の候補は trial_extra.rejected_candidate_audit に保存(§3規則)。追加キーは trial_extra(§3に無い試験用情報)のみ。",
            prompt_v1_sha=nt.hashlib.sha256(nt.PROMPT_V1.encode()).hexdigest(), prompt_v2_sha=nt.hashlib.sha256(PROMPT_V2.encode()).hexdigest(), judge_prompt_sha=nt.hashlib.sha256(nt.PROMPT_JUDGE.encode()).hexdigest(),
            model=nt.MODEL, total_cost_jpy=tot, runs=runs, judge_probe=probe)
json.dump(data, open(os.path.join(OUT, "prompt_trial_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- markdown断片 ----
def short(s, n): return s if len(s) <= n else s[: n - 1] + "…"
def table(ver, rs, ctrl=None):
    rows = ["| 記事 | レベル | 候補表現 | 焦点 | 重複判定(段1構造/段2LLM/引用逐語) | 理由 | モデル自己評価 / worker所見 | 費用(円) |", "|---|---|---|---|---|---|---|---|"]
    items = list(rs.items()) + ([("control_trivial", ctrl)] if ctrl else [])
    for k, r in items:
        c = r.get("candidate_raw"); cost = (r.get("gen_usage") or {}).get("cost_jpy", 0) + (r.get("judge_usage") or {}).get("cost_jpy", 0)
        wk = WORKER.get(("v1c" if (ver == "v1" and k == "control_trivial") else ver, k), ("", ""))
        if c:
            s1 = r["stage1_structural"]["verdict"]; s2 = r["stage2_llm"]["verdict"]
            why = ("段1 " + ", ".join(f"{m['candidate_part']}~{m['kp']}" for m in r["stage1_structural"]["matched"]) + " / ") if s1 == "fail" else ""
            why += short(r["stage2_llm"]["reason"], 90)
            rows.append(f"| {r['article']} | {r['level']} | {c['expression']} | {c['focus']} | **{r['final_overlap_verdict'].upper()}** ({s1}/{s2}/{'OK' if r['quote_verbatim'] else 'NG'}) | {why} | {c['learning_value_self_rating']} / {wk[0]}: {wk[1]} | {cost:.3f} |")
        else:
            rows.append(f"| {r.get('article', k)} | {r.get('level', '')} | (0件) | - | - | {short(r.get('no_candidate_reason') or '', 90)} | - / {wk[0]}: {wk[1]} | {cost:.3f} |")
    return "\n".join(rows)
open(os.path.join(OUT, "_table_v1.md"), "w", encoding="utf-8").write(table("v1", v1, v1c["control_trivial"]))
open(os.path.join(OUT, "_table_v2.md"), "w", encoding="utf-8").write(table("v2", {k: r for k, r in v2.items() if k != "control_trivial"}, v2["control_trivial"]))

def cost_sum(prefix, filt=None):
    return round(sum(u["cost_jpy"] for u in usage if u["tag"].startswith(prefix) and (filt is None or filt(u["tag"]))), 4)
real = lambda t: "control" not in t
print("total", tot, "v1_real", cost_sum("v1_", real), "v1_control", cost_sum("v1_control"), "v2_real", cost_sum("v2_", real), "v2_control", cost_sum("v2_control"), "probe", cost_sum("probe_"))
print("calls", len(usage), "v1 gen/judge elapsed max", max(u["elapsed_sec"] for u in usage))
