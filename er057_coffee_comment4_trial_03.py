# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-COMMENT4-MINIMAL-PROMPT-TRIAL-03 Trial専用(Production非経由、文章のみ、3回生成)。
trial_02 scriptを変更せず経路を流用。modes: prompts / gen / metrics"""
import os, sys, json, re, difflib
sys.path.insert(0, os.getcwd())
import er057_coffee_comment4_trial_02 as t2
ROOT = t2.ROOT
OUT = f"{ROOT}/er057_output/coffee_comment4_trial_03"
C0 = t2.C0
OLD = t2.OLD_ROLE
NEW = """役割: 記事全体の意味を軽く回収し、In One Lineへつなぎます。本文を再説明し
すぎないでください。2〜3文にしてください。
In One Lineは、番組の最後に流れる英語による要点整理です。橋渡しの表現では、
「続いて」より「最後に」を使ってください。"""
CURRENT = "コーヒー豆の値段が下がっても、店の値札がすぐに変わるとは限りません。値段が変わる時期には、豆以外の費用も関わります。続いて、記事の要点を英語で聞いていきましょう。"
TRIAL = C0.replace(OLD, NEW)
BAD = {"事務的つなぎ": r"続いて|ここからは|次は|それでは|では、", "聞き終え宣言": r"聞き終|すべて聞|全部聞", "構造ラベル": r"Part ?\d|Full Story|第\d部|本文\d",
       "文数断定": r"一文で|ひとことで|一言で|1文|one sentence|ワンセンテンス"}
def prompts():
    base = open(f"{ROOT}/er057_output/coffee_comment4_trial_02/prompts/prompt_baseline_current.md", encoding="utf-8").read()
    assert C0 in base.replace("\r\n", "\n"), "baseline mismatch"
    open(f"{OUT}/prompts/prompt_trial_03.md", "w", encoding="utf-8").write("# Trial-03 Prompt(現行+2点追加のみ)\n\n```\n" + TRIAL + "\n```\n")
    d = "\n".join(difflib.unified_diff(C0.splitlines(), TRIAL.splitlines(), "current(FAMILY_X_A2_COMMENT_4_ROLE)", "trial_03", lineterm=""))
    open(f"{OUT}/prompt_diff_03.md", "w", encoding="utf-8").write("# Prompt差分(現行→Trial-03)\n\n```diff\n" + d + "\n```\n\n全文(Trial):\n\n```\n" + TRIAL + "\n```\n")
    print(d)
def gen():
    for p in (f"{OUT}/STOP", f"{ROOT}/er026_output/family_z_production_e2e_01/STOP_ALL_NOT_APPLICABLE_CHECKED_BY_FABLE"): assert not os.path.exists(p)
    import er003_v1_iran01_a2_generate as a2gen, er006_model_routing_contract_01 as routing
    model = routing.require_model("A2_SUPPORT", routing.SUPPORT_MODEL)
    client = a2gen.vfl01.get_client(); usages = []; orig = client.responses.create
    def w(**kw):
        r = orig(**kw); u = getattr(r, "usage", None)
        usages.append({"model": r.model, "in": getattr(u, "input_tokens", 0), "out": getattr(u, "output_tokens", 0)}); return r
    client.responses.create = w
    c = t2.ctx(); rows = []
    for i in (1, 2, 3):
        r = a2gen.run_support_text(client, TRIAL, c, model=model)
        rows.append({"run": i, "status": r["status"], "text": r["text"], "model_id": r["attempts"][-1].get("model"), "attempts": len(r["attempts"])})
    with open(f"{OUT}/generations.jsonl", "w", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    inp = sum(u["in"] or 0 for u in usages); out = sum(u["out"] or 0 for u in usages); jpy = (inp * 0.10 + out * 0.50) / 1e6 * 160
    json.dump({"routing_model": model, "response_models": sorted({u["model"] for u in usages}), "calls": len(usages), "in_tokens": inp, "out_tokens": out, "est_jpy": round(jpy, 4),
               "basis": "gpt-6-luna in0.10/out0.50 USD per M x 160 (trial_01/02同一)"}, open(f"{OUT}/cost_llm.json", "w"), indent=1)
    for r in rows: print(r["run"], r["status"], r["text"])
    print(jpy, model, len(usages))
def metrics():
    rows = [json.loads(l) for l in open(f"{OUT}/generations.jsonl", encoding="utf-8")]
    cur = t2.nchars(CURRENT); res = {"current_chars": cur, "current_sentences": len(t2.sents(CURRENT)), "runs": []}
    for r in rows:
        t = r["text"] or ""
        d = {"run": r["run"], "chars": t2.nchars(t), "ratio_vs_current": round(t2.nchars(t) / cur, 2), "sentences": len(t2.sents(t)),
             "ends_with_saigoni": "最後に" in t.split("。")[-2] if t.count("。") >= 1 else False, "has_saigoni": "最後に" in t,
             "bad": [k for k, rx in BAD.items() if re.search(rx, t)], "text": t}
        res["runs"].append(d); print({k: v for k, v in d.items() if k != "text"})
    json.dump(res, open(f"{OUT}/metrics.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1); print("current", cur)
if __name__ == "__main__":
    {"prompts": prompts, "gen": gen, "metrics": metrics}[sys.argv[1]]()
