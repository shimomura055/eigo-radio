# -*- coding: utf-8 -*-
"""FAMILY-Z-MELOS-SOL-B3Z-COMPARISON-TRIAL-01 委任_01: 機械指標(API無し)+ AI品質評価(gpt-6-luna、N=2、Blind)。

AI評価はユーザーの実読評価ではない。評価Prompt(5項目)は Trial専用(英語Story向け。er054 D方式は『原作の再話適性』評価であり
英語Story評価へは流用不可のため新規の簡潔Prompt)。評価modelはrouting Trial key FAMILY_Z_TRIAL_STORY_QUALITY_EVAL(gpt-6-luna)。
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
OUT = os.path.join(ROOT, "er059_output", "melos_sol_b3z_trial_01")
SEED_DIR = os.path.join(ROOT, "er018_output", "fiction_external_seed_selection_criteria_trial_02", "stories", "03_japanese_lit_2")
METHODS = {"M1": f"{SEED_DIR}/story.md", "M2": f"{OUT}/m2_sol_only/r2.md", "M3": f"{OUT}/m3_sol_b3z/r2.md"}
CHAINS = {"M2": f"{OUT}/m2_sol_only", "M3": f"{OUT}/m3_sol_b3z"}
EVAL_MODEL_KEY = "FAMILY_Z_TRIAL_STORY_QUALITY_EVAL"
USD_JPY = 160.0
ITEMS = ("hook", "development", "emotion", "central_story", "ending")

SCENES = {   # 原作の重要場面 -> 英語本文の機械的キーワード(粗い近似。目視評価の補助のみ)
    "妹の結婚": r"\b(wedding|sister|married)\b",
    "王との約束(3日)": r"\b(three days|third day|promise|return)\b",
    "友人が人質(セリヌンティウス役)": r"\b(friend)\b.*\b(stay|stays|stayed|place|hostage|wait)\b|\b(stay|place|hostage)\b.*\bfriend\b",
    "帰路の困難:濁流": r"\b(river|flood|flooded|water|rain)\b",
    "帰路の困難:山賊": r"\b(attack|attacker|attackers|bandit|bandits|robber|robbers|men)\b",
    "疲労・絶望(諦めかけ)": r"\b(give up|could stay|could rest|could live|wanted to|did not want to stand|hide)\b",
    "信頼で再起": r"\b(trust|trusted|remembered|gave my word|promised)\b",
    "間に合う(処刑直前)": r"\b(sword|execution|stop|wait|just in time)\b",
    "友の信頼と王の改心": r"\b(free him|free them|let them|fair trial|fair trials|lowered|learned|trust)\b",
}


def rd(p):
    return open(p, encoding="utf-8").read()


def body_of(t):
    return "\n".join(l for l in t.splitlines() if not l.lstrip().startswith("#")).strip()


def title_of(t):
    for l in t.splitlines():
        if l.lstrip().startswith("#"):
            return l.lstrip("# ").strip()
    return t.splitlines()[0].strip()


def metrics():
    import er003_a2_article as a2
    res = {}
    for k, p in METHODS.items():
        t = rd(p)
        m = a2.compute_a2_sentence_metrics(t)
        h = a2.compute_a2_grammar_vocab_heuristics(t)
        b = body_of(t)
        words = re.findall(r"[A-Za-z][A-Za-z'\-]*", b)
        swc = m["sentence_word_counts"]
        ss = sorted(swc)
        res[k] = {
            "title": title_of(t), "words_body": len(b.split()),
            "in_range_280_420": 280 <= len(b.split()) <= 420,
            "sentences": m["total_sentence_count"], "avg_words_per_sentence": m["avg_words_per_sentence"],
            "median_sentence_len": ss[len(ss) // 2], "p90_sentence_len": ss[int(len(ss) * 0.9) - 1] if len(ss) > 1 else ss[0],
            "max_sentence_len": m["longest_sentence_word_count"], "sentences_over_18": m["sentences_over_18_word_count"],
            "short_sentences_le4_words": sum(1 for x in swc if x <= 4),
            "long_word_ge9_candidates": h["long_word_candidates"], "long_word_rate_pct": round(100 * h["long_word_candidate_count"] / max(len(words), 1), 2),
            "subordinate_markers": h["subordinate_marker_count"], "relative_clause": h["relative_clause_candidate_count"],
            "passive": h["passive_candidate_count"], "past_perfect": h["past_perfect_candidate_count"], "participial": h["participial_phrase_candidate_count"],
            "avg_within_a2_target_11": m["avg_words_per_sentence_within_target"],
            "markdown_symbols_in_body": sorted(set(re.findall(r"[*_]{1,2}[^*_\n]+[*_]{1,2}", b))),
            "scene_keywords_hit": {n: bool(re.search(rx, b, re.I | re.S)) for n, rx in SCENES.items()},
        }
        res[k]["scene_coverage"] = f"{sum(res[k]['scene_keywords_hit'].values())}/{len(SCENES)}"
    return res


def chain_changes():
    import difflib
    out = {}
    for k, d in CHAINS.items():
        r0, r1, r2 = (body_of(rd(f"{d}/{x}.md")) for x in ("r0", "r1", "r2"))
        sp = lambda s: [x.strip() for x in re.split(r"(?<=[.!?”\"])\s+|\n+", s) if x.strip()]
        o = {}
        for a, b, n in ((r0, r1, "r0_to_r1"), (r1, r2, "r1_to_r2"), (r0, r2, "r0_to_r2")):
            sa, sb = sp(a), sp(b)
            sm = difflib.SequenceMatcher(None, sa, sb)
            same = sum(x.size for x in sm.get_matching_blocks())
            o[n] = {"words": f"{len(a.split())}->{len(b.split())}", "sentences": f"{len(sa)}->{len(sb)}", "identical_sentences": same,
                    "sentence_ratio": round(sm.ratio(), 3), "text_ratio": round(difflib.SequenceMatcher(None, a, b).ratio(), 3)}
        out[k] = o
    return out


EVAL_DEV = ("あなたは英語学習マガジンのFiction編集部の評価者です。同じ原作(下の『原作の要点』)から作られた3つの英語短編(X/Y/Z。方式は伏せてある)を、"
            "本文だけを根拠に比較評価します。方式・モデル・工程・過去の評価は考慮しません。引用は本文中の連続した文字列のコピーのみ(言い換え・省略記号禁止)。")
EVAL_USER = """【原作の要点(Seed、評価の基準として使う)】
{seed}

【読者】A2英語学習者(短く平易な文、280〜420語)。物語として読み、聞いて楽しめること。

【3つの短編】
{stories}

【採点】X/Y/Zそれぞれを5項目1〜5の整数で採点(5=非常に優れる、3=標準、1=弱い。差を付ける必要も避ける必要もない):
- hook(引き込み): 冒頭から読み進めたくなるか
- development(展開): 場面の進行・緊張の高まり・テンポが良いか
- emotion(感情): 読者が感情(緊張・不安・安堵・感動)を実際に感じるか
- central_story(中心Story維持): 原作の要点(対立・約束・障害・諦めかけ・再起・間に合う・王の改心)が損なわれず因果が通っているか。原作にない出来事の追加・重要要素の欠落があれば減点
- ending(結末): クライマックスと結末の余韻が効いているか
各項目に短い日本語の理由(1文)。さらにbest_quote(最も良い1文)とweak_quote(最も弱い/不自然な1文)を本文から引用し、
a2_concern(A2として難しすぎる/不自然な点があれば日本語で、なければ空文字)、new_events(原作にない追加の出来事・設定を日本語で列挙、なければ空配列)を書く。
最後にranking(良い順に["X","Y","Z"]の並べ替え)と日本語のoverall_comment(2文以内)。出力はJSONのみ。"""
EVAL_SCHEMA = {"name": "story_eval", "strict": True, "schema": {
    "type": "object", "additionalProperties": False, "required": ["evals", "ranking", "overall_comment"],
    "properties": {"evals": {"type": "array", "items": {"type": "object", "additionalProperties": False,
        "required": ["label", *ITEMS, "reasons", "best_quote", "weak_quote", "a2_concern", "new_events"],
        "properties": {"label": {"type": "string", "enum": ["X", "Y", "Z"]},
                       **{i: {"type": "integer", "minimum": 1, "maximum": 5} for i in ITEMS},
                       "reasons": {"type": "object", "additionalProperties": False, "required": list(ITEMS),
                                   "properties": {i: {"type": "string"} for i in ITEMS}},
                       "best_quote": {"type": "string"}, "weak_quote": {"type": "string"},
                       "a2_concern": {"type": "string"}, "new_events": {"type": "array", "items": {"type": "string"}}}}},
        "ranking": {"type": "array", "items": {"type": "string", "enum": ["X", "Y", "Z"]}},
        "overall_comment": {"type": "string"}}}}


def run_eval(budget, reps=2):
    from dotenv import load_dotenv
    load_dotenv()
    import er005_cost_logger as cl
    import er006_model_routing_contract_01 as routing
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er059_melos_sol_b3z_trial_01 as gen
    model = routing.PROCESS_MODEL_MAP[EVAL_MODEL_KEY]
    assert model == "gpt-6-luna"
    d = f"{OUT}/eval"
    os.makedirs(d, exist_ok=True)
    cl.install(f"{OUT}/raw_usage_log.jsonl")
    client = vfl01.get_client()
    seed = json.load(open(f"{SEED_DIR}/seed.json", encoding="utf-8"))
    seed_txt = "\n".join("- " + s for s in seed["seed_elements"])
    spent = 0.0
    perms = [["M1", "M2", "M3"], ["M3", "M1", "M2"]]
    for rep in range(1, reps + 1):
        order = perms[(rep - 1) % len(perms)]
        labels = dict(zip(["X", "Y", "Z"], order))     # label -> method(rep間で並び替え、Blind)
        stories = "\n\n".join(f"=== {lb} ===\n{rd(METHODS[m]).strip()}" for lb, m in labels.items())
        user = EVAL_USER.format(seed=seed_txt, stories=stories)
        if spent + 1.0 > budget:
            raise SystemExit("[STOP] 評価費用上限")
        t0 = time.time()
        with cl.logging_context(gen.THEME_TAG, "eval"):
            r = client.responses.create(model=model, reasoning={"effort": "medium"},
                                        text={"format": {"type": "json_schema", **EVAL_SCHEMA}},
                                        input=[{"role": "developer", "content": EVAL_DEV}, {"role": "user", "content": user}])
        c = gen.cost_jpy(model, r.usage) if model in ("gpt-6.1-sol",) else _luna_cost(r.usage)
        spent += c
        p = json.loads(r.output_text)
        json.dump({"rep": rep, "label_to_method": labels, "model": r.model, "response_id": r.id, "elapsed_sec": round(time.time() - t0, 1),
                   "cost_jpy": round(c, 3), "result": p}, open(f"{d}/eval_rep{rep}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"rep{rep} done cost={c:.3f}")
    print("eval spent_jpy", round(spent, 3))


def _luna_cost(u):
    inp, outp = u.input_tokens or 0, u.output_tokens or 0
    return (inp * 0.1 + outp * 0.5) / 1e6 * USD_JPY


def aggregate_eval():
    res = {m: {i: [] for i in ITEMS} for m in METHODS}
    ranks = {m: [] for m in METHODS}
    details = []
    for rep in (1, 2):
        p = f"{OUT}/eval/eval_rep{rep}.json"
        if not os.path.exists(p):
            continue
        j = json.load(open(p, encoding="utf-8"))
        l2m = j["label_to_method"]
        for e in j["result"]["evals"]:
            m = l2m[e["label"]]
            for i in ITEMS:
                res[m][i].append(e[i])
            details.append({"rep": rep, "method": m, **e})
        for pos, lb in enumerate(j["result"]["ranking"], 1):
            ranks[l2m[lb]].append(pos)
    summ = {m: {i: round(sum(v) / len(v), 2) if v else None for i, v in d.items()} for m, d in res.items()}
    for m in summ:
        vals = [x for x in summ[m].values() if x is not None]
        summ[m]["total_avg"] = round(sum(vals) / len(vals), 2) if vals else None
        summ[m]["ranks"] = ranks[m]
    return summ, details


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", choices=("metrics", "eval", "aggregate"), required=True)
    ap.add_argument("--budget-jpy", type=float, default=5.0)
    a = ap.parse_args()
    if a.step == "metrics":
        m = metrics()
        c = chain_changes()
        json.dump({"metrics": m, "chain_changes": c}, open(f"{OUT}/metrics_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(json.dumps({k: {x: v[x] for x in ("words_body", "sentences", "avg_words_per_sentence", "max_sentence_len", "sentences_over_18",
                                                "long_word_rate_pct", "scene_coverage", "markdown_symbols_in_body")} for k, v in m.items()}, ensure_ascii=False, indent=1))
        print(json.dumps(c, ensure_ascii=False, indent=1))
    elif a.step == "eval":
        run_eval(a.budget_jpy)
    else:
        s, d = aggregate_eval()
        json.dump({"summary": s, "details": d}, open(f"{OUT}/eval_summary_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(json.dumps(s, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
