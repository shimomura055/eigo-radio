# -*- coding: utf-8 -*-
"""FAMILY-Z-MELOS-PREVIEW-STD-ADV-3TAKE-COMPARE-01 (Trial専用、Production経路非接続)。
Std: er070の統一Prompt(Family X準拠)を3 take / Adv: 現行Family Z Advanced Preview経路(b1s.PREVIEW_ROLE)を3 take。
Prompt・入力は一切変更しない。1 take = 1 call (max_attempts=1、lint NGでも再生成しない)。計6 call。
--mode verify  : API呼出なし。prompt sha検証(Std=er070一致、Adv=run_support_adv mock一致)。
--mode generate: verify後、6 call直列生成。"""
import argparse
import datetime as dt
import hashlib
import json
import os
import sys

import er070_family_z_std_preview_x_alignment_01 as e70

RUN = e70.RUN
USD_JPY = e70.USD_JPY
PRICE = e70.PRICE
ER70_DIR = "er070_output/family_z_std_preview_x_alignment_01"
STOP_FILES = [f"{RUN}/STOP", "er026_output/family_z_production_e2e_01/STOP_ALL"]


def sha_text(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def charlen(t):
    return len(t.replace("\n", ""))


def sents_ja(t):
    return len([s for s in t.replace("。", "。\n").split("\n") if s.strip()])


def sents_en(t):
    import re
    return len([s for s in re.split(r"(?<=[.!?])\s+", t.strip()) if s.strip()])


def build_inputs():
    import er003_v1_b1_scaffold_01_generate as b1s
    import er003_v1_iran01_a2_generate as a2gen
    import er062_family_z_writer_01 as w62
    sa = json.load(open(f"{RUN}/support/a2_support.json", encoding="utf-8"))
    sb = json.load(open(f"{RUN}/support/b1b_support.json", encoding="utf-8"))
    std_text = w62.rd(w62.level_text_path(RUN, "a2"))
    adv_text = w62.rd(w62.level_text_path(RUN, "b1b"))
    # Std
    std_role = e70.assemble_role(sa["comments"]["1"], sa["comments"]["2"])
    std_ctx = f"{e70.CONTEXT_HEAD_X}\n{std_text}"
    std_prompt = a2gen.build_support_prompt(std_role, std_ctx)
    # Adv (run_support_adv の組立と同一式)
    adv_role = b1s.PREVIEW_ROLE.format(comment_1=sb["comments"]["1"], comment_2=sb["comments"]["2"])
    adv_ctx = f"【本文】\n{adv_text}\n\n{w62.NOT_NEWS_NOTE}"
    adv_prompt = b1s.build_support_prompt(adv_role, adv_ctx)
    return dict(sa=sa, sb=sb, std=(std_role, std_ctx, std_prompt), adv=(adv_role, adv_ctx, adv_prompt),
                b1s=b1s, a2gen=a2gen, w62=w62)


def verify(inp):
    """Std: er070送信promptとsha一致 / Adv: run_support_adv(mock)が送るpromptと一致。"""
    res = {}
    er70_prompt = open(f"{ER70_DIR}/prompt_after_full_assembled_01.txt", encoding="utf-8").read()
    std_prompt = inp["std"][2]
    res["std_sha"] = sha_text(std_prompt)
    res["std_er070_sha"] = sha_text(er70_prompt)
    res["std_matches_er070"] = std_prompt == er70_prompt
    # Adv: run_support_adv にmock fnを渡し、Preview callのrole/ctxを捕捉
    w62, b1s, sb = inp["w62"], inp["b1s"], inp["sb"]
    calls = []

    def fn(client, role, ctx, model=None, **kw):
        calls.append((role, ctx))
        return {"status": "OK", "text": "Mock output sentence one. Mock sentence two.", "prompt": "", "attempts": []}
    parts = {1: "Part one.", 2: "Part two.", 3: "Part three.\n\nMore."}
    prior = {"comments": sb["comments"], "attempts": {"comment_1": [], "comment_2": []}}
    w62.run_support_adv(object(), parts, inp["adv_text"], en_support_fn=fn, prior=prior)
    prole, pctx = calls[-1]
    prod_prompt = b1s.build_support_prompt(prole, pctx)
    res["adv_sha"] = sha_text(inp["adv"][2])
    res["adv_production_path_mock_sha"] = sha_text(prod_prompt)
    res["adv_matches_production_path"] = prod_prompt == inp["adv"][2]
    res["adv_mock_calls_total"] = len(calls)
    c1, c2 = inp["sb"]["comments"]["1"], inp["sb"]["comments"]["2"]
    res["adv_comments_embedded"] = c1 in inp["adv"][2] and c2 in inp["adv"][2]
    res["std_comments_embedded"] = inp["sa"]["comments"]["1"] in std_prompt and inp["sa"]["comments"]["2"] in std_prompt
    res["developer_message_std"] = inp["a2gen"].SUPPORT_DEVELOPER_MESSAGE
    res["developer_message_adv"] = b1s.SUPPORT_DEVELOPER_MESSAGE
    res["reasoning_effort_std"] = inp["a2gen"].REASONING_EFFORT
    res["reasoning_effort_adv"] = b1s.REASONING_EFFORT
    res["ok"] = bool(res["std_matches_er070"] and res["adv_matches_production_path"]
                     and res["adv_comments_embedded"] and res["std_comments_embedded"])
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["verify", "generate"], required=True)
    ap.add_argument("--takes", type=int, default=3)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--budget-jpy", type=float, default=5.0)
    a = ap.parse_args()
    out = a.out_dir
    os.makedirs(out, exist_ok=True)
    if a.takes != 3:
        print("takes must be 3")
        return 4
    inp = build_inputs()
    inp["adv_text"] = inp["w62"].rd(inp["w62"].level_text_path(RUN, "b1b"))
    v = verify(inp)
    json.dump(v, open(f"{out}/prompt_sha_verify_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps(v, ensure_ascii=False, indent=1))
    if not v["ok"]:
        print("STOP: prompt verification failed")
        return 4
    if a.mode == "verify":
        return 0
    sent = [p for p in STOP_FILES if os.path.exists(p)]
    if sent:
        print("STOP sentinel present:", sent)
        return 3

    import er006_model_routing_contract_01 as routing
    import er062_family_z_structure_01 as st
    import er003_v1_en_direct_vfl_01_generate as vfl01
    m_std = routing.require_model("A2_SUPPORT", routing.SUPPORT_MODEL)
    m_adv = routing.require_model("B1_SUPPORT", routing.SUPPORT_MODEL)
    est = lambda p: ((len(p) + 100) * PRICE["input"] + 3000 * PRICE["output"]) / 1e6 * USD_JPY  # noqa: E731
    est_total = 3 * est(inp["std"][2]) + 3 * est(inp["adv"][2])
    assert est_total < a.budget_jpy, est_total
    before = e70.state_snapshot()
    open(f"{out}/prompt_std_full_01.txt", "w", encoding="utf-8").write(inp["std"][2])
    open(f"{out}/prompt_adv_full_01.txt", "w", encoding="utf-8").write(inp["adv"][2])

    client = vfl01.get_client()
    cap = {}
    orig = client.responses.create

    def create(*aa, **k):
        r = orig(*aa, **k)
        cap.update(usage=r.usage, model=r.model, id=r.id, effort=k.get("reasoning"))
        return r
    client.responses.create = create

    takes, calls, total = [], [], 0.0
    plan = [("std", i) for i in (1, 2, 3)] + [("adv", i) for i in (1, 2, 3)]
    for lv, i in plan:
        if any(os.path.exists(p) for p in STOP_FILES):
            print("STOP sentinel appeared; abort")
            break
        cap.clear()
        role, ctx, prompt = inp[lv]
        if lv == "std":
            res = inp["a2gen"].run_support_text(client, role, ctx, max_attempts=1, model=m_std)
            lang = "ja"
        else:
            res = inp["b1s"].run_support_text(client, role, ctx, max_attempts=1, model=m_adv)
            lang = "en"
        u = cap.get("usage")
        ui, uo = getattr(u, "input_tokens", None), getattr(u, "output_tokens", None)
        rt = getattr(getattr(u, "output_tokens_details", None), "reasoning_tokens", None)
        act = ((ui or 0) * PRICE["input"] + (uo or 0) * PRICE["output"]) / 1e6 * USD_JPY
        total += act
        calls.append({"level": lv, "take": i, "status": res["status"], "sent_prompt_sha": sha_text(res.get("prompt", prompt)),
                      "input_tokens": ui, "output_tokens": uo, "reasoning_tokens": rt, "jpy": round(act, 4),
                      "response_model_id": cap.get("model"), "response_id": cap.get("id"),
                      "reasoning": str(cap.get("effort")), "requested_model": m_std if lv == "std" else m_adv})
        if res["status"] != "OK":
            takes.append({"level": lv, "take": i, "status": res["status"], "attempts": res["attempts"]})
            print("FAILED", lv, i, res["attempts"])
            continue
        t = res["text"].strip()
        open(f"{out}/{lv}_take{i}.txt", "w", encoding="utf-8").write(t + "\n")
        lint = st.lint_support_text(t, lang, "melos")
        d = {"level": lv, "take": i, "status": "OK", "text": t, "lint": lint}
        if lang == "ja":
            d.update(chars=charlen(t), sentences=sents_ja(t))
        else:
            d.update(words=len(t.split()), sentences=sents_en(t))
        takes.append(d)
        print(lv, i, "lint", lint, "jpy", round(act, 4))
        print(t)
    json.dump({"price_usd_per_1M": PRICE, "price_source": "er006_model_routing_pricing_coverage_test_01.py:50-52",
               "usd_jpy": USD_JPY, "estimate_total_jpy": round(est_total, 4), "calls": calls, "n_calls": len(calls),
               "total_jpy": round(total, 4), "budget_jpy": a.budget_jpy},
              open(f"{out}/cost_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"takes": takes, "current_std_preview": inp["sa"]["preview"], "current_adv_preview": inp["sb"]["preview"],
               "er070_after": open(f"{ER70_DIR}/preview_after_01.txt", encoding="utf-8").read().strip(),
               "std_comments": inp["sa"]["comments"], "adv_comments": inp["sb"]["comments"]},
              open(f"{out}/takes_result_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    after = e70.state_snapshot()
    changed = [p for p in before if before[p] != after.get(p)]
    json.dump({"files_checked": len(before), "changed": changed, "unchanged_all": not changed,
               "generated_at": dt.datetime.now().isoformat(), "before_sha256": before, "after_sha256": after},
              open(f"{out}/state_guard_01.json", "w", encoding="utf-8"), indent=1)
    print("total JPY", round(total, 4), "state changed", changed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
