# -*- coding: utf-8 -*-
"""FACTLOCK-WRITER-REDESIGN-TRIAL-01 委任_06: R3-MINIMAL-01 (Trial/DEV。Production経路ではない)。
既存「6x現行(all6)」R2記事12本へ、ユーザー提示の1文でRevise 3回目を1回だけ追加し、面白さ(pairwise)・事実逸脱(JA FC)・文体指標を測る。
既存harness/Production codeは編集しない(importして関数を呼ぶのみ)。cl.install(グローバルpatch)は使わず、各responseのusageから自前で費用記録する。
"""
from __future__ import annotations
import argparse, json, os, re, sys, threading, time
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

BASE = "er052_output/factlock_writer_trial_01/r3_minimal_01"
SRC = "er052_output/all6_writer_redesign_necessity_01/runs"
MODEL = "gpt-6-luna"
R3_SENTENCE = "事実は変えずにエンターテイメント性をもっと上げた記事にReviseください。"
PW_INSTR = ("以下は同じニュースをもとにした、日本語ラジオで読み上げる記事AとBです。"
            "あなたが聞き手だとして、続きを聞きたい、誰かに話したくなるのはどちらですか。"
            "事実の正確さは別に評価するので考えなくてかまいません。"
            "winnerはA/B/tie。reasonは、そう感じた箇所を具体的に挙げて日本語2文以内で。")
PW_DEV = "あなたはラジオ番組の聞き手です。"
PW_SCHEMA = {"name": "pairwise", "strict": True, "schema": {
    "type": "object", "additionalProperties": False, "required": ["winner", "reason"],
    "properties": {"winner": {"type": "string", "enum": ["A", "B", "tie"]}, "reason": {"type": "string"}}}}
PRICE = (0.10, 0.01, 0.50)   # gpt-6-luna USD/1M: input, cached input, output
USD_JPY = 160.0
SLUGS = ["meta", "hormuz", "space_weapons"]
_LOCK = threading.Lock()
_STATE = {"cost": 0.0}


def jpy(inp, cached, out):
    inp, cached, out = inp or 0, cached or 0, out or 0
    return ((inp - cached) * PRICE[0] + cached * PRICE[1] + out * PRICE[2]) / 1e6 * USD_JPY


def log_usage(stage, key, usage, model, sec):
    """usage: dict(input_tokens, cached_input_tokens, output_tokens)。費用を累積しJSONLへ追記。"""
    c = jpy(usage.get("input_tokens"), usage.get("cached_input_tokens"), usage.get("output_tokens"))
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "stage": stage, "key": key, "model": model,
           "sec": round(sec, 2), "cost_jpy": round(c, 4), **{k: usage.get(k) for k in ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_tokens")}}
    with _LOCK:
        _STATE["cost"] += c
        with open(f"{BASE}/usage_log.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return c


def usage_of(resp):
    u = getattr(resp, "usage", None)
    if u is None:
        return {}
    ind, outd = getattr(u, "input_tokens_details", None), getattr(u, "output_tokens_details", None)
    return {"input_tokens": getattr(u, "input_tokens", None), "output_tokens": getattr(u, "output_tokens", None),
            "cached_input_tokens": getattr(ind, "cached_tokens", None) if ind else None,
            "reasoning_tokens": getattr(outd, "reasoning_tokens", None) if outd else None}


def select_sources():
    """12本: rep r1 が completed ならr1、STOP(completed以外)ならr2。MANIFEST.jsonのexit_reasonで判定。"""
    man = {r["key"]: r for r in json.load(open("er052_output/all6_writer_redesign_necessity_01/MANIFEST.json", encoding="utf-8"))["runs"]}
    out = []
    for s in SLUGS:
        for b in (1, 2, 3, 4):
            chosen = None
            for rep in (1, 2):
                k = f"{s}/b{b}__all6__r{rep}"
                d = f"{SRC}/{s}/control/b{b}__all6__r{rep}"
                if man.get(k, {}).get("exit_reason") == "completed" and os.path.exists(f"{d}/ja_writer/revision2.md"):
                    chosen = (rep, d, k)
                    break
            if chosen is None:
                raise SystemExit(f"元記事が無い: {s} b{b}")
            out.append({"slug": s, "b": b, "rep": chosen[0], "dir": chosen[1], "key": chosen[2],
                        "r2_path": f"{chosen[1]}/ja_writer/revision2.md",
                        "ledger_path": f"{chosen[1]}/research_ledger/verified_fact_ledger.txt",
                        "out": f"{BASE}/runs/{s}/b{b}"})
    return out


def build_fresh_input(r2_text, symbol_block):
    return f"以下の記事:\n\n{r2_text}\n\n{R3_SENTENCE}{symbol_block}"


def build_chain_instruction(symbol_block):
    return f"{R3_SENTENCE}{symbol_block}"


def read(p):
    return open(p, encoding="utf-8").read()


def write(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)


def jwrite(p, o):
    write(p, json.dumps(o, ensure_ascii=False, indent=1))


def retry(fn, n=3):
    for a in range(1, n + 1):
        try:
            return fn()
        except Exception:  # noqa: BLE001
            if a == n:
                raise
            time.sleep(5 * a)


def check_budget(budget):
    if _STATE["cost"] > budget * 2:   # 暴走防止(Guardrail超過は記録継続、2倍で停止)
        raise RuntimeError(f"[STOP] cost {_STATE['cost']:.1f} > 2x budget {budget}")


# ---------------- 生成 ----------------
def gen_one(client, jaw, item, arm, budget, chain_ok):
    out = f"{item['out']}/r3_{arm}.md"
    if os.path.exists(out):
        return
    r2 = read(item["r2_path"]).strip()
    sym = jaw.SYMBOL_PREVENTION_BLOCK_JA
    ev = json.load(open(f"{item['dir']}/ja_writer/runtime_evidence.json", encoding="utf-8"))
    prev_id = (ev.get("r2") or {}).get("response_id")
    t0 = time.time()
    meta = {"arm": arm, "key": item["key"], "r2_sha_len": len(r2)}
    check_budget(budget)
    if arm == "fresh":
        user = build_fresh_input(r2, sym)
        resp = retry(lambda: client.responses.create(model=MODEL, reasoning={"effort": jaw.WRITER_EFFORT},
                                                     input=[{"role": "developer", "content": jaw.DEVELOPER_MESSAGE},
                                                            {"role": "user", "content": user}]))
        meta["method"] = "fresh"
    else:
        method = None
        if prev_id and chain_ok.get(item["key"]):
            try:
                resp = client.responses.create(model=MODEL, reasoning={"effort": jaw.WRITER_EFFORT},
                                               previous_response_id=prev_id,
                                               input=[{"role": "user", "content": build_chain_instruction(sym)}])
                method = "previous_response_id"
            except Exception as exc:  # noqa: BLE001
                meta["chain_error"] = repr(exc)
                resp = None
        else:
            resp = None
        if resp is None:
            user = build_fresh_input(r2, sym)   # 近似: R2本文を貼る(現行fallback_full_textと同書式)
            resp = retry(lambda: client.responses.create(model=MODEL, reasoning={"effort": jaw.WRITER_EFFORT},
                                                         input=[{"role": "developer", "content": jaw.DEVELOPER_MESSAGE},
                                                                {"role": "user", "content": user}]))
            method = "fallback_full_text_approx"
        meta["method"] = method
        meta["previous_response_id"] = prev_id
    sec = time.time() - t0
    meta.update({"response_id": resp.id, "model": resp.model, "sec": round(sec, 1)})
    meta["cost_jpy"] = round(log_usage(f"r3_{arm}", item["key"], usage_of(resp), resp.model, sec), 4)
    write(out, (resp.output_text or "").strip())
    jwrite(f"{item['out']}/r3_{arm}_meta.json", meta)
    print(f"[gen] {item['key']} {arm} {meta['method']} {sec:.0f}s cum=¥{_STATE['cost']:.1f}", flush=True)


def probe_chain(client, items):
    """前段R2のresponse_idを取得し、保存済みR2本文と一致するときだけ本物のchainを使う(retrieveは無料)。"""
    ok = {}
    for it in items:
        ev = json.load(open(f"{it['dir']}/ja_writer/runtime_evidence.json", encoding="utf-8"))
        rid = (ev.get("r2") or {}).get("response_id")
        try:
            r = client.responses.retrieve(rid)
            same = (r.output_text or "").strip() == read(it["r2_path"]).strip()
            ok[it["key"]] = bool(same)
            if not same:
                print(f"[probe] {it['key']}: response_id本文とrevision2.mdが不一致→近似にfallback", flush=True)
        except Exception as exc:  # noqa: BLE001
            ok[it["key"]] = False
            print(f"[probe] {it['key']}: retrieve失敗 {exc!r}→近似", flush=True)
    return ok


# ---------------- JA FC ----------------
def fc_one(client, vfl01, item, name, text_path, budget):
    out = f"{item['out']}/fc_{name}.json"
    if os.path.exists(out):
        return
    check_budget(budget)
    ledger = read(item["ledger_path"])
    t0 = time.time()
    res = retry(lambda: vfl01.run_deviation_check(client, ledger, read(text_path).strip(), model=MODEL,
                                                  hook_aware=False, include_related_fact_id=True))
    sec = time.time() - t0
    log_usage(f"fc_{name}", item["key"], res["usage"], res["model"], sec)
    jwrite(out, {"parsed": res["parsed"], "model": res["model"], "response_id": res["response_id"], "sec": round(sec, 1)})
    print(f"[fc] {item['key']} {name} {res['parsed'].get('overall_status')} cum=¥{_STATE['cost']:.1f}", flush=True)


# ---------------- pairwise ----------------
def pw_one(client, item, arm, order, budget):
    out = f"{item['out']}/pairwise_{arm}_o{order}.json"
    if os.path.exists(out):
        return
    check_budget(budget)
    r3, r2 = read(f"{item['out']}/r3_{arm}.md").strip(), read(item["r2_path"]).strip()
    a, b = (r3, r2) if order == 0 else (r2, r3)
    prompt = f"{PW_INSTR}\n\n# 記事A\n{a}\n\n# 記事B\n{b}\n"
    t0 = time.time()
    resp = retry(lambda: client.responses.create(model=MODEL, reasoning={"effort": "medium"},
                                                 text={"format": {"type": "json_schema", **PW_SCHEMA}},
                                                 input=[{"role": "developer", "content": PW_DEV},
                                                        {"role": "user", "content": prompt}]))
    sec = time.time() - t0
    log_usage(f"pw_{arm}", item["key"], usage_of(resp), resp.model, sec)
    p = json.loads(resp.output_text)
    lab = p["winner"]
    r3_wins = (lab == "A" and order == 0) or (lab == "B" and order == 1)
    r2_wins = (lab == "B" and order == 0) or (lab == "A" and order == 1)
    jwrite(out, {"order": order, "A": "r3" if order == 0 else "r2", "B": "r2" if order == 0 else "r3",
                 "winner_label": lab, "winner": "r3" if r3_wins else ("r2" if r2_wins else "tie"),
                 "reason": p["reason"], "model": resp.model})
    print(f"[pw] {item['key']} {arm} o{order} -> {'r3' if r3_wins else 'r2' if r2_wins else 'tie'} cum=¥{_STATE['cost']:.1f}", flush=True)


def pmap(fn, jobs, par):
    with ThreadPoolExecutor(max_workers=par) as ex:
        list(ex.map(lambda j: fn(*j), jobs))


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="fresh,chain")
    ap.add_argument("--budget-jpy", type=float, default=60.0)
    ap.add_argument("--parallel", type=int, default=2)
    ap.add_argument("--yes-run-paid", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--phases", default="gen,fc,pw")
    args = ap.parse_args(argv)
    args.parallel = min(args.parallel, 2)
    arms = args.arms.split(",")
    import er006_model_routing_contract_01 as routing
    import er019_family_x_ja_writer_o_r1_r2_01 as jaw
    import er003_v1_en_direct_vfl_01_generate as vfl01
    routing.require_model_or_override("B1_WRITER", MODEL, override_reason="FACTLOCK R3-MINIMAL-01")
    routing.require_model_or_override("WRITER_FACT_CHECK", MODEL, override_reason="FACTLOCK R3-MINIMAL-01")
    items = select_sources()
    if args.dry_run or not args.yes_run_paid:
        for it in items:
            r2 = read(it["r2_path"]).strip()
            print(it["key"], "len", len(r2), "ledger", os.path.exists(it["ledger_path"]))
        print("--- fresh input head ---")
        print(build_fresh_input(read(items[1]["r2_path"]).strip()[:60] + "...", jaw.SYMBOL_PREVENTION_BLOCK_JA)[:400])
        print("--- chain instruction ---")
        print(build_chain_instruction(jaw.SYMBOL_PREVENTION_BLOCK_JA)[:200])
        return 0 if args.dry_run else 2
    os.makedirs(BASE, exist_ok=True)
    client = vfl01.get_client()
    t_all = time.time()
    chain_ok = {}
    if "gen" in args.phases:
        if "chain" in arms:
            chain_ok = probe_chain(client, items)
            jwrite(f"{BASE}/chain_probe.json", chain_ok)
        pmap(lambda it, arm: gen_one(client, jaw, it, arm, args.budget_jpy, chain_ok), [(it, a) for it in items for a in arms], args.parallel)
    if "fc" in args.phases:
        jobs = [(client, vfl01, it, f"{a}", f"{it['out']}/r3_{a}.md", args.budget_jpy) for it in items for a in arms]
        jobs += [(client, vfl01, it, "orig_r2", it["r2_path"], args.budget_jpy) for it in items]
        pmap(fc_one, jobs, args.parallel)
    if "pw" in args.phases:
        pmap(pw_one, [(client, it, a, o, args.budget_jpy) for it in items for a in arms for o in (0, 1)], args.parallel)
    man = {"trial": "FACTLOCK-WRITER-REDESIGN-TRIAL-01/R3-MINIMAL-01", "model": MODEL, "arms": arms,
           "sources": [{k: it[k] for k in ("key", "rep", "r2_path", "ledger_path")} for it in items],
           "r3_sentence": R3_SENTENCE, "total_cost_jpy": round(_STATE["cost"], 2), "wall_sec": round(time.time() - t_all, 1),
           "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    jwrite(f"{BASE}/MANIFEST.json", man)
    print("done cost", round(_STATE["cost"], 2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
