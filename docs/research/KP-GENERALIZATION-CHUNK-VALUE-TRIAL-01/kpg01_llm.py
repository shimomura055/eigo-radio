# -*- coding: utf-8 -*-
"""KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01 Trial専用LLM wrapper(Production module非依存・費用ledger付き)。"""
import json, os, sys, time, hashlib, threading
HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "kpg01_work", "cost_ledger.jsonl")
CACHE_DIR = os.path.join(HERE, "kpg01_work", "llm_cache")
os.makedirs(CACHE_DIR, exist_ok=True)
USD_JPY = 160.0
# $/1M (input, cached_input, output)。出典: docs/pm/dev_eval_model_inventory_01.md(公式2026-10-09取得)
PRICE = {"gpt-6-luna": (0.10, 0.01, 0.50), "gpt-6.1-sol": (2.00, 0.10, 10.00), "gpt-6-astra": (10.0, 1.0, 50.0),
         "gemini-3.8-flash": (0.75, 0.075, 3.75), "gemini-3.1-pro-preview": (2.0, 0.2, 12.0), "deepseek-v4-pro": (1.32, 0.044, 3.96), "deepseek-flash": (0.30, 0.006, 1.20)}
_lock = threading.Lock()

def _load_env():
    from dotenv import load_dotenv
    load_dotenv(os.path.join(HERE, "..", "..", "..", ".env"))

def _cost(model, tin, tout, cached=0):
    p = PRICE[model]
    usd = ((tin - cached) * p[0] + cached * p[1] + tout * p[2]) / 1e6
    return usd * USD_JPY

def _ledger(rec):
    with _lock:
        with open(LEDGER, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def total_cost():
    if not os.path.exists(LEDGER): return 0.0
    return sum(json.loads(l)["cost_jpy"] for l in open(LEDGER, encoding="utf-8") if l.strip())

def call(model, user, schema=None, *, system=None, effort=None, tag="", use_cache=True, max_out=None, think_budget=None):
    """returns (parsed_or_text, meta)。schema=dict(name, schema)でJSON Schema強制。"""
    key = hashlib.sha256(json.dumps([model, user, system, schema, effort, think_budget], ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:24]
    cp = os.path.join(CACHE_DIR, key + ".json")
    if use_cache and os.path.exists(cp):
        d = json.load(open(cp, encoding="utf-8"))
        d["meta"]["cached"] = True
        return d["out"], d["meta"]
    _load_env()
    t0 = time.time()
    if model.startswith("gpt-"):
        from openai import OpenAI
        client = OpenAI()
        kw = dict(model=model, input=([{"role": "developer", "content": system}] if system else []) + [{"role": "user", "content": user}])
        if schema: kw["text"] = {"format": {"type": "json_schema", "name": schema["name"], "strict": True, "schema": schema["schema"]}}
        if effort: kw["reasoning"] = {"effort": effort}
        if max_out: kw["max_output_tokens"] = max_out
        r = client.responses.create(**kw)
        text = r.output_text
        u = r.usage
        tin, tout = u.input_tokens, u.output_tokens
        cached = getattr(getattr(u, "input_tokens_details", None), "cached_tokens", 0) or 0
        rtok = getattr(getattr(u, "output_tokens_details", None), "reasoning_tokens", 0) or 0
        mid = r.model
    elif model.startswith("gemini-"):
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        cfg = dict(system_instruction=system) if system else {}
        if schema:
            cfg["response_mime_type"] = "application/json"
            cfg["response_schema"] = _strip(schema["schema"])
        if think_budget is not None:
            cfg["thinking_config"] = types.ThinkingConfig(thinking_budget=think_budget)
        r = client.models.generate_content(model=model, contents=user, config=types.GenerateContentConfig(**cfg))
        text = r.text
        um = r.usage_metadata
        tin, tout = um.prompt_token_count or 0, (um.candidates_token_count or 0) + (getattr(um, "thoughts_token_count", 0) or 0)
        cached, rtok, mid = 0, getattr(um, "thoughts_token_count", 0) or 0, model
    else:
        raise ValueError(model)
    cost = _cost(model, tin, tout, cached)
    meta = {"model_req": model, "model_id": mid, "tag": tag, "in": tin, "out": tout, "reasoning": rtok, "cost_jpy": round(cost, 4),
            "sec": round(time.time() - t0, 1), "cached": False}
    _ledger({**meta, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")})
    out = json.loads(text) if schema else text
    json.dump({"out": out, "meta": meta}, open(cp, "w", encoding="utf-8"), ensure_ascii=False)
    return out, meta


def _strip(s):
    if isinstance(s, dict):
        return {k: _strip(v) for k, v in s.items() if k != "additionalProperties"}
    if isinstance(s, list):
        return [_strip(x) for x in s]
    return s


def call_deepseek(model, user, schema_hint=None, *, system=None, tag="", use_cache=True, no_think=False):
    """DeepSeek(OpenAI互換chat API、JSON mode)。独立判定用。returns (parsed_json, meta)。"""
    key = hashlib.sha256(json.dumps(["ds", model, user, system, no_think], ensure_ascii=False).encode()).hexdigest()[:24]
    cp = os.path.join(CACHE_DIR, key + ".json")
    if use_cache and os.path.exists(cp):
        d = json.load(open(cp, encoding="utf-8")); d["meta"]["cached"] = True
        return d["out"], d["meta"]
    _load_env()
    from openai import OpenAI
    cl = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
    t0 = time.time()
    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
    r = cl.chat.completions.create(model=model, messages=msgs, response_format={"type": "json_object"}, **({"extra_body": {"thinking": {"type": "disabled"}}} if no_think else {}))
    text = r.choices[0].message.content
    u = r.usage
    tin, tout = u.prompt_tokens, u.completion_tokens
    cost = _cost(model, tin, tout)
    meta = {"model_req": model, "model_id": r.model, "tag": tag, "in": tin, "out": tout, "reasoning": 0, "cost_jpy": round(cost, 4), "sec": round(time.time() - t0, 1), "cached": False}
    _ledger({**meta, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")})
    out = json.loads(text)
    json.dump({"out": out, "meta": meta}, open(cp, "w", encoding="utf-8"), ensure_ascii=False)
    return out, meta
