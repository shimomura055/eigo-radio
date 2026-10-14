# -*- coding: utf-8 -*-
"""FAMILY-Z-PREVIEW-COMMENT1-DUAL-TRIAL-01 (Trial専用、Production経路非接続、TTSなし)。
Trial A: A1 Preview(er074条件E逐語) -> A2 Comment1(Production Std Comment1経路+末尾にPreview参照ブロック追加のみ)
Trial B: B1 Comment1(Production Std Comment1経路、content_factsのみ固定文へ差替) -> B2 Preview(er070統一Prompt+er074条件A組立、C1=B1生成物、C2=現行Std Comment2)
各3 take独立(max_attempts=1、再生成/選別なし。Comment生成のみProduction既存の内部品質retry(max_retries=1)を温存)。
--plan-only: API呼出なし。--run: 12生成(6 chain並列、chain内依存順序厳守)。"""
import argparse
import concurrent.futures as cf
import datetime as dt
import json
import os
import sys
import threading

import er074_family_z_std_preview_comment_dependency_01 as e74
import er070_family_z_std_preview_x_alignment_01 as e70

RUN = e70.RUN
STOP_FILES = [f"{RUN}/STOP", "er026_output/family_z_production_e2e_01/STOP_ALL"]
CONTENT_FACTS_PROD = ("これから聞く英文(下の【これから聞く部分】)に実際に書かれている事実のみ。場所・状況、人物関係、"
                      "場面の変化、次の行動、選択や対立点のうち必要なもの。【これから聞く部分】に書かれていない事実・"
                      "人物・結末は使わない。")   # er062 run_support_std L862-865と逐語同一
CONTENT_FACTS_B1 = ("これから聞く英文(下の【これから聞く部分】)に実際に書かれている事実のみを使う。Advanced版のComment 1と同じ性格にする: "
                    "物語の前提を長々と説明せず、聞くときに注目する具体的な点(誰が・何を・どんな約束や条件か)を、1〜2文の短い聴取ガイドとして示す。"
                    "先の展開・結末は述べない。抽象的な教訓・評論調にしない。Standardの学習者が分かる平易な日本語にし、"
                    "理解に必要な前提(人物関係・置かれた状況)は最小限で含める。")
A2_BLOCK = ("\n\n【直前に流れるPreview(すでにリスナーが聞いた内容)】\n{preview}\n\n【Previewとの役割分担】Previewで述べた事実・状況を説明し直さない。"
            "Previewにない背景・理由・条件(なぜその状況になったか、どんな約束や条件があるか等)のうち、これから聞く英文の理解に必要なものを補足する。"
            "単なる言い換えや、説明不足にならないようにする。最後は、これから流れる英文へ自然につなぐ。")
sha = e74.sha_text


def load_all():
    import er062_family_z_structure_01 as st
    import er062_family_z_writer_01 as w62
    c1, c2, std_text, _sa = e74.load()
    plan = json.load(open(f"{RUN}/segment_plan_a2.json", encoding="utf-8"))
    _t, body = st.split_title_body(std_text)
    parts = st.part_texts(st.clean_body_paragraphs(body), *plan["boundaries"])
    return c1, c2, std_text, parts, plan["boundaries"], st, w62


def b2_role(b1_comment, c2):
    return e70.Z_ROLE_TEMPLATE.format(comment_1=b1_comment, comment_2=c2)


def write_prompts(out, a1_t1="{A1_PREVIEW_TAKE1}", b1_t1="{B1_COMMENT1_TAKE1}"):
    import er003_v1_iran01_a2_generate as a2gen
    import er013_family_c_production_01 as fam_c
    c1, c2, std_text, parts, bnd, _st, _w = load_all()
    ctx = f"{e70.CONTEXT_HEAD_X}\n{std_text}"
    pa1 = a2gen.build_support_prompt(e74.build_roles(c1, c2)["E"], ctx)
    art_a2 = f"【これから聞く部分】\n{parts[1]}" + A2_BLOCK.format(preview=a1_t1)
    pa2 = a2gen.build_support_prompt(fam_c.build_family_c_a2_comment_prompt(1, CONTENT_FACTS_PROD, scene_transition=""),
                                     f"【物語全文(参考、新しい設定・事実の追加禁止)】\n{art_a2}")
    art_b1 = f"【これから聞く部分】\n{parts[1]}"
    pb1 = a2gen.build_support_prompt(fam_c.build_family_c_a2_comment_prompt(1, CONTENT_FACTS_B1, scene_transition=""),
                                     f"【物語全文(参考、新しい設定・事実の追加禁止)】\n{art_b1}")
    pb2 = a2gen.build_support_prompt(b2_role(b1_t1, c2), ctx)
    for n, p in (("A1", pa1), ("A2_take1", pa2), ("B1", pb1), ("B2_take1", pb2)):
        open(f"{out}/prompt_{n}_full_01.txt", "w", encoding="utf-8").write(p)
    return {"A1": pa1, "A2": pa2, "B1": pb1, "B2": pb2}, parts, bnd


def est_cost(prompts):
    e = lambda p: ((len(p) + 100) * e70.PRICE["input"] + 3000 * e70.PRICE["output"]) / 1e6 * e70.USD_JPY  # noqa: E731
    return {k: round(e(v), 4) for k, v in prompts.items()}


def plan_only(out):
    os.makedirs(out, exist_ok=True)
    P, parts, bnd = write_prompts(out)
    ec = est_cost(P)
    est_total = 3 * (ec["A1"] + 2 * ec["A2"] + 2 * ec["B1"] + ec["B2"])
    est_nominal = 3 * (ec["A1"] + ec["A2"] + ec["B1"] + ec["B2"])
    er74 = json.load(open("er074_output/family_z_std_preview_comment_dependency_01/cost_01.json", encoding="utf-8"))
    per = er74["total_jpy"] / er74["n_calls"]
    md = f"""# plan_01 (FAMILY-Z-PREVIEW-COMMENT1-DUAL-TRIAL-01, 生成前)

## 固定
- model: gpt-6-luna / reasoning effort high / developer message=`日本語のListening Support原稿を作成してください。` / `a2gen.run_support_text`経由(er072/er074と同一)。
  使用モデル=Production Preview/Comment生成と同一。最新世代か=現行Production最新(gpt-6-luna)。例外理由=現行Production出力との比較可能性。
- 原稿: `{RUN}/writer/std.md`、Part境界 boundaries={bnd}(segment_plan_a2.json)、Part1=`parts[1]`(段落0..{bnd[0]-1})。
- A1: er074条件Eの`build_roles()["E"]`+ctx(`{e70.CONTEXT_HEAD_X}`+std全文)を逐語使用。Prompt探索なし。
- A2: `fam_c.generate_family_c_a2_comment(n=1)`、content_facts=Production固定文(逐語)、art=`【これから聞く部分】\\n{{Part1}}`+末尾に追加ブロック(下記)。同TakeのA1 Previewを参照。
- B1: 同経路、content_factsのみ固定文へ差替(下記)。art=Part1。
- B2: er070統一Prompt(Z_ROLE_TEMPLATE)に comment_1=同TakeのB1生成物、comment_2=現行Std Comment2(er074条件Aと同じ組立でC1のみ差替)。ctx=std全文。
- lint: `er062_family_z_structure_01.lint_support_text(text,"ja","melos")`を全12生成に適用・記録のみ(NGでも再生成しない)。Comment生成のみ、Production既存の`check_a2_comment_quality`(40〜170字・禁止語句)内部retry(max_retries=1)が働く(Production経路温存)。

## A2追加ブロック(art末尾へ追加、role本文・content_facts不変)
```
{A2_BLOCK.format(preview='{A1のPreview全文}').strip()}
```
## B1 content_facts固定文
```
{CONTENT_FACTS_B1}
```
## role矛盾の報告(固定文のまま実施)
Production Std Comment1 role(`FAMILY_C_A2_COMMENT_ROLE_JA_1`)は「状況説明に徹し、2〜3文・80〜110字程度」。Advanced COMMENT_1_ROLE(`b1s.COMMENT_1_ROLE`)は「注目点を示す原則1文の非常に短いListening Focus、答え・結論を先に言わない」。
B1固定文は「1〜2文の短い聴取ガイド」であり、role本文の「2〜3文・80〜110字」「状況説明に徹する」と部分的に矛盾する(role本文は変更しない指示のため、LLMがどちらを優先するかはTake結果に依存)。

## 費用見積(生成前)
単価 input $0.10/output $0.50 per 1M(er006_model_routing_pricing_coverage_test_01.py L50-52)、USD/JPY=160。
er074実績: {er74['n_calls']}生成 合計JPY {er74['total_jpy']}(平均 {per:.4f}/生成)。同方式で12生成は約 JPY {per*12:.2f}。
保守的prompt長ベース上限見積(出力3000tok想定): 名目12生成 JPY {est_nominal:.3f}、Comment内部retry最悪(Comment 6件→最大12呼出)含む JPY {est_total:.3f}。上限JPY20に対し十分小さい。
各Prompt別保守見積(JPY/回): {json.dumps(ec)}
"""
    open(f"{out}/plan_01.md", "w", encoding="utf-8").write(md)
    print("est", ec, est_nominal, est_total, "er074 per-call", round(per, 4))
    assert est_total < 20
    return 0


class Proxy:
    """client.responses.createの使用量を記録するプロキシ(送信内容・生成内容は不変)。"""
    def __init__(self, client, rec):
        self._c, self.rec = client, rec
        self.responses = self

    def create(self, *a, **k):
        r = self._c.responses.create(*a, **k)
        u = r.usage
        self.rec.append({"thread": threading.get_ident(), "model": r.model, "id": r.id, "reasoning": str(k.get("reasoning")),
                         "input_tokens": getattr(u, "input_tokens", None), "output_tokens": getattr(u, "output_tokens", None),
                         "reasoning_tokens": getattr(getattr(u, "output_tokens_details", None), "reasoning_tokens", None)})
        return r


def jpy(i, o):
    return ((i or 0) * e70.PRICE["input"] + (o or 0) * e70.PRICE["output"]) / 1e6 * e70.USD_JPY


def run(out, takes, budget):
    sent = [p for p in STOP_FILES if os.path.exists(p)]
    if sent:
        print("STOP sentinel present:", sent)
        return 3
    assert takes == 3
    import er003_v1_iran01_a2_generate as a2gen
    import er013_family_c_production_01 as fam_c
    import er006_model_routing_contract_01 as routing
    import er003_v1_en_direct_vfl_01_generate as vfl01
    c1, c2, std_text, parts, bnd, st, w62 = load_all()
    m = routing.require_model("A2_SUPPORT", routing.SUPPORT_MODEL)
    os.makedirs(out, exist_ok=True)
    P, _p, _b = write_prompts(out)
    ec = est_cost(P)
    est_total = 3 * (ec["A1"] + 2 * ec["A2"] + 2 * ec["B1"] + ec["B2"])
    assert est_total < budget, est_total
    before = e70.state_snapshot()
    rec = []
    client = Proxy(vfl01.get_client(), rec)
    ctx = f"{e70.CONTEXT_HEAD_X}\n{std_text}"
    E_ROLE = e74.build_roles(c1, c2)["E"]
    lint = lambda t: st.lint_support_text(t, "ja", "melos")  # noqa: E731

    def stop():
        return any(os.path.exists(p) for p in STOP_FILES)

    def comment_gen(take, tag, content_facts, art):
        prompts = []

        def fn(cl, prompt, context, model=None):
            r = a2gen.run_support_text(cl, prompt, context, max_attempts=1, model=model)
            prompts.append(r.get("prompt"))
            return r
        try:
            r = fam_c.generate_family_c_a2_comment(client, 1, art, content_facts, scene_transition="",
                                                   label_prefix=f"fz_dual_{tag}_t{take}", model=m, run_support_text_fn=fn)
            return {"status": "OK", "text": r["text"], "attempts": r["attempts"], "prompts": prompts}
        except Exception as e:  # noqa: BLE001
            return {"status": "FAILED", "error": f"{type(e).__name__}: {str(e)[:600]}", "prompts": prompts}

    def chain(method, take):
        if stop():
            return {"method": method, "take": take, "aborted": "STOP"}
        r = {"method": method, "take": take}
        if method == "A":
            res = a2gen.run_support_text(client, E_ROLE, ctx, max_attempts=1, model=m)
            r["step1"] = {"kind": "A1_preview", "status": res["status"], "text": (res.get("text") or "").strip(),
                          "prompt_sha": sha(res["prompt"]), "matches_design": res["prompt"] == P["A1"]}
            if res["status"] != "OK":
                return r
            art = f"【これから聞く部分】\n{parts[1]}" + A2_BLOCK.format(preview=r["step1"]["text"])
            r["step2"] = {"kind": "A2_comment1", "ref_preview_take": take, **comment_gen(take, "A2", CONTENT_FACTS_PROD, art)}
        else:
            c = comment_gen(take, "B1", CONTENT_FACTS_B1, f"【これから聞く部分】\n{parts[1]}")
            r["step1"] = {"kind": "B1_comment1", **c}
            if c["status"] != "OK":
                return r
            res = a2gen.run_support_text(client, b2_role(c["text"], c2), ctx, max_attempts=1, model=m)
            r["step2"] = {"kind": "B2_preview", "ref_comment_take": take, "status": res["status"], "text": (res.get("text") or "").strip(),
                          "prompt_sha": sha(res["prompt"]), "prompt": res["prompt"]}
        return r

    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        futs = [ex.submit(chain, mth, t) for mth in "AB" for t in (1, 2, 3)]
        chains = [f.result() for f in futs]
    for r in chains:
        if r["method"] == "A" and r["take"] == 1 and r.get("step2", {}).get("prompts"):
            open(f"{out}/prompt_A2_take1_full_01.txt", "w", encoding="utf-8").write(r["step2"]["prompts"][0])
        if r["method"] == "B" and r["take"] == 1:
            if r["step1"].get("prompts"):
                open(f"{out}/prompt_B1_full_01.txt", "w", encoding="utf-8").write(r["step1"]["prompts"][0])
            if r.get("step2", {}).get("prompt"):
                open(f"{out}/prompt_B2_take1_full_01.txt", "w", encoding="utf-8").write(r["step2"]["prompt"])
    for r in chains:
        for k in ("step1", "step2"):
            s = r.get(k)
            if s and s.get("status") == "OK":
                s["lint"] = lint(s["text"])
                s["chars"] = e74.charlen(s["text"])
                s["sentences"] = e74.sents_ja(s["text"])
                s["sha"] = sha(s["text"])
    total = sum(jpy(x["input_tokens"], x["output_tokens"]) for x in rec)
    json.dump({"model": m, "chains": chains, "usage_calls": rec, "n_api_calls": len(rec)},
              open(f"{out}/takes_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"price_usd_per_1M": e70.PRICE, "usd_jpy": e70.USD_JPY, "estimate_conservative_jpy": round(est_total, 4),
               "n_api_calls": len(rec), "total_jpy": round(total, 4), "budget_jpy": budget, "hard_stop_jpy": 22,
               "calls": [{**x, "jpy": round(jpy(x["input_tokens"], x["output_tokens"]), 4)} for x in rec]},
              open(f"{out}/cost_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    after = e70.state_snapshot()
    changed = [p for p in before if before[p] != after.get(p)]
    json.dump({"files_checked": len(before), "changed": changed, "unchanged_all": not changed, "generated_at": dt.datetime.now().isoformat(),
               "before_sha256": before, "after_sha256": after}, open(f"{out}/state_guard_01.json", "w", encoding="utf-8"), indent=1)
    for r in chains:
        print("====", r["method"], r["take"])
        for k in ("step1", "step2"):
            s = r.get(k, {})
            print(k, s.get("kind"), s.get("status"), s.get("lint"), s.get("text") or s.get("error"))
    print("api calls", len(rec), "total JPY", round(total, 4), "state changed", changed)
    return 0


def ngrams4(t):
    t = "".join(ch for ch in t if ch not in "。、 \n")
    return {t[i:i + 4] for i in range(len(t) - 3)}


def run_b_corrected(out, budget):
    """委任_03: 承認済みTrial Bを仕様どおり実施(Trial Aは再生成せず takes_01.json を流用)。
    B1'=Advanced型Listening Focus Comment 1(Family X A2の日本語版COMMENT_1_ROLE=a2gen.COMMENT_1_ROLE、無改変。
        b1s.COMMENT_1_ROLEの日本語出力版で役割本文は同一)。ctx=er062 run_support_advのComment1と同形式(【本文(これから聞く部分)】Part1+NOT_NEWS_NOTE)。
    B2'=現行Production Std Previewプロンプト(build_family_z_preview_prompt)+Comment 1重複回避(run_support_stdと同一)。
    各3 take独立、max_attempts=1、再生成/選別なし、lintは記録のみ。"""
    sent = [p for p in STOP_FILES + [f"{out}/STOP"] if os.path.exists(p)]
    if sent:
        print("STOP sentinel present:", sent)
        return 3
    import er003_v1_iran01_a2_generate as a2gen
    import er006_model_routing_contract_01 as routing
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er026_family_z_fiction_production_runner_01 as er026
    c1, c2, std_text, parts, bnd, st, w62 = load_all()
    m = routing.require_model("A2_SUPPORT", routing.SUPPORT_MODEL)
    prev = json.load(open(f"{out}/cost_01.json", encoding="utf-8"))
    remain = budget - prev["total_jpy"]
    role1 = a2gen.COMMENT_1_ROLE
    ctx1 = f"【本文(これから聞く部分)】\n{parts[1]}\n\n{w62.NOT_NEWS_NOTE}"
    pb1 = a2gen.build_support_prompt(role1, ctx1)
    prev_role = er026.build_family_z_preview_prompt()
    dup = "\n\n【重複回避】直前に流れるComment 1は次の通りです。これと内容が重複しないようにしてください。\n"
    ctx2 = f"【物語全文(参考、新しい設定・事実の追加禁止)】\n{std_text}"
    pb2_ex = a2gen.build_support_prompt(prev_role + dup + "{B1_COMMENT1}", ctx2)
    e = lambda p: ((len(p) + 100) * e70.PRICE["input"] + 3000 * e70.PRICE["output"]) / 1e6 * e70.USD_JPY  # noqa: E731
    est = 3 * (e(pb1) + e(pb2_ex))
    print("est conservative JPY", round(est, 4), "remain", round(remain, 4))
    assert est < remain, (est, remain)
    open(f"{out}/prompt_B_full_02.txt", "w", encoding="utf-8").write(
        "=== B1' (Comment 1, prompt) ===\n" + pb1 + "\n\n=== B2' (Preview, prompt; {B1_COMMENT1}=同TakeのB1'生成物) ===\n" + pb2_ex)
    before = e70.state_snapshot()
    rec = []
    client = Proxy(vfl01.get_client(), rec)
    lint = lambda t: st.lint_support_text(t, "ja", "melos")  # noqa: E731

    def chain(take):
        r = {"method": "B2", "take": take}
        if any(os.path.exists(p) for p in STOP_FILES + [f"{out}/STOP"]):
            r["aborted"] = "STOP"
            return r
        res1 = a2gen.run_support_text(client, role1, ctx1, max_attempts=1, model=m)
        r["step1"] = {"kind": "B1prime_comment1", "status": res1["status"], "text": (res1.get("text") or "").strip(),
                      "prompt_sha": sha(res1["prompt"]), "matches_design": res1["prompt"] == pb1}
        if res1["status"] != "OK":
            return r
        role2 = prev_role + dup + r["step1"]["text"]
        res2 = a2gen.run_support_text(client, role2, ctx2, max_attempts=1, model=m)
        r["step2"] = {"kind": "B2prime_preview", "ref_comment_take": take, "status": res2["status"],
                      "text": (res2.get("text") or "").strip(), "prompt_sha": sha(res2["prompt"])}
        return r

    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        chains = [f.result() for f in [ex.submit(chain, t) for t in (1, 2, 3)]]
    for r in chains:
        for k in ("step1", "step2"):
            s = r.get(k)
            if s and s.get("status") == "OK":
                s["lint"] = lint(s["text"])
                s["chars"] = e74.charlen(s["text"])
                s["sentences"] = e74.sents_ja(s["text"])
                s["sha"] = sha(s["text"])
        if r.get("step1", {}).get("status") == "OK" and r.get("step2", {}).get("status") == "OK":
            r["overlap_4gram"] = sorted(ngrams4(r["step1"]["text"]) & ngrams4(r["step2"]["text"]))
    total = sum(jpy(x["input_tokens"], x["output_tokens"]) for x in rec)
    json.dump({"model": m, "trialA_source": "takes_01.json(再生成なし)", "chains_B_corrected": chains, "usage_calls": rec, "n_api_calls": len(rec)},
              open(f"{out}/takes_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    cost02 = {"delegation_01_jpy": prev["total_jpy"], "delegation_03_jpy": round(total, 4),
              "combined_jpy": round(prev["total_jpy"] + total, 4), "budget_jpy": budget, "n_api_calls_03": len(rec),
              "calls_03": [{**x, "jpy": round(jpy(x["input_tokens"], x["output_tokens"]), 4)} for x in rec]}
    json.dump(cost02, open(f"{out}/cost_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    after = e70.state_snapshot()
    changed = [p for p in before if before[p] != after.get(p)]
    json.dump({"files_checked": len(before), "changed": changed, "unchanged_all": not changed, "generated_at": dt.datetime.now().isoformat()},
              open(f"{out}/state_guard_02.json", "w", encoding="utf-8"), indent=1)
    for r in chains:
        print("====", r["take"])
        for k in ("step1", "step2"):
            s = r.get(k, {})
            print(k, s.get("status"), s.get("lint"), s.get("text"))
    print("api calls", len(rec), "total JPY", round(total, 4), "combined", cost02["combined_jpy"], "state changed", changed)
    return 0


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--plan-only", action="store_true")
    g.add_argument("--run", action="store_true")
    g.add_argument("--run-b-corrected", action="store_true")
    ap.add_argument("--takes", type=int, default=3)
    ap.add_argument("--budget-jpy", type=float, default=20.0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.run_b_corrected:
        return run_b_corrected(a.out, a.budget_jpy)
    return plan_only(a.out) if a.plan_only else run(a.out, a.takes, a.budget_jpy)


if __name__ == "__main__":
    sys.exit(main())
