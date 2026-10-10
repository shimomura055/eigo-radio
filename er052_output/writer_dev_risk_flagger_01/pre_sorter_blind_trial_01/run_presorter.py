# -*- coding: utf-8 -*-
"""Phase2: Blind pre-sorter。各モデル完全独立・各バッチ1回(JSON不正/ID不一致時のみ同条件で最大1回再試行)。Trial/DEV専用。
使い方: run_presorter.py <model> [<model>...]   (astraは累計費用ガードあり)"""
import os, sys, json, hashlib, datetime, time, threading
sys.stdout.reconfigure(encoding="utf-8"); sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "detectors"))
import flagger_lib as L
from dotenv import load_dotenv; load_dotenv(os.path.join(HERE, "..", "..", "..", ".env"))
from openai import OpenAI
EFFORT, MAX_OUT, GUARD_JPY = "medium", 16000, 300.0
SYS = open(os.path.join(HERE, "prompt_presorter_01.txt"), encoding="utf-8").read()
PK = json.load(open(os.path.join(HERE, "blind_packet_01.json"), encoding="utf-8"))
sha = lambda b: hashlib.sha256(b).hexdigest()
LEDGER = os.path.join(HERE, "cost_ledger_presorter_01.jsonl"); lock = threading.Lock()
def total():
    return L.ledger_total(LEDGER)
def parse(text, ids):
    try:
        s = text.strip(); d = json.loads(s)
        r = d["results"]; assert [x["id"] for x in r] == ids, "id mismatch"
        for x in r:
            assert x["grade"] in "ABCD" and len(x["grade"]) == 1 and x["fix_recommended"] in ("Yes", "No") and x["human_review_value"] in ("High", "Medium", "Low") and x["reason"].strip()
        return r, None
    except Exception as e: return None, repr(e)[:200]
def run_batch(client, model, bi):
    ids = PK["batches"][bi - 1]; user = "Items (%d):\n\n" % len(ids) + open(os.path.join(HERE, "batch_text_%d.txt" % bi), encoding="utf-8").read()
    prices = L.load_prices(model); assert prices, "price unregistered"
    attempts = []; parsed = None
    for a in (1, 2):
        with lock:
            if total() >= GUARD_JPY: raise SystemExit("COST GUARD: cumulative >= JPY%.0f" % GUARD_JPY)
        t0 = time.time(); ts = datetime.datetime.now().isoformat(timespec="seconds"); rec = dict(attempt=a, timestamp=ts)
        try:
            resp = client.responses.create(model=model, instructions=SYS, input=user, reasoning={"effort": EFFORT}, max_output_tokens=MAX_OUT)
            u = resp.usage
            usage = dict(input_tokens=u.input_tokens, output_tokens=u.output_tokens, reasoning_tokens=getattr(getattr(u, "output_tokens_details", None), "reasoning_tokens", None), cached_tokens=getattr(getattr(u, "input_tokens_details", None), "cached_tokens", None))
            cost = L.cost_yen(prices, usage["input_tokens"], usage["output_tokens"], usage["cached_tokens"])
            text = resp.output_text
            rec.update(response_id=resp.id, response_model=resp.model, status=getattr(resp, "status", None), raw_text=text, usage=usage, cost_jpy=cost, elapsed_s=round(time.time() - t0, 2))
            with lock: L.ledger_append(dict(cell="%s_b%d_a%d" % (model, bi, a), model=model, cost_jpy=cost), LEDGER)
            parsed, err = parse(text, ids); rec["parse_error"] = err
        except Exception as e:
            rec.update(api_error=repr(e)[:500], elapsed_s=round(time.time() - t0, 2)); err = "api_error"
        attempts.append(rec)
        if parsed: break
    out = dict(model=model, provider="openai", routing="direct OpenAI Responses API (api.openai.com)", reasoning_effort=EFFORT, max_output_tokens=MAX_OUT, batch=bi, ids=ids,
               prompt_sha256=sha(SYS.encode("utf-8")), user_message_sha256=sha(user.encode("utf-8")), packet_sha256=sha(open(os.path.join(HERE, "blind_packet_01.json"), "rb").read()),
               system_prompt=SYS, user_message=user, attempts=attempts, retried=len(attempts) > 1, parsed=parsed, valid=bool(parsed), total_cost_jpy=sum(x.get("cost_jpy") or 0 for x in attempts))
    d = os.path.join(HERE, "runs", model); os.makedirs(d, exist_ok=True)
    json.dump(out, open(os.path.join(d, "batch_%d.json" % bi), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(model, "batch", bi, "valid", out["valid"], "retried", out["retried"], "cost", round(out["total_cost_jpy"], 2), flush=True)
def run_model(model, parallel):
    client = OpenAI()
    if parallel:
        ts = [threading.Thread(target=run_batch, args=(client, model, b)) for b in (1, 2, 3)]
        [t.start() for t in ts]; [t.join() for t in ts]
    else:
        for b in (1, 2, 3): run_batch(client, model, b)
if __name__ == "__main__":
    ms = sys.argv[1:]
    ths = [threading.Thread(target=run_model, args=(m, m != "gpt-6-astra")) for m in ms]
    [t.start() for t in ths]; [t.join() for t in ths]
    print("cumulative JPY", round(total(), 2))
