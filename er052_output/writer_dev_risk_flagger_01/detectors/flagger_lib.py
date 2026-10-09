# -*- coding: utf-8 -*-
"""WRITER-DEV-RISK-FLAGGER-DESIGN-01 委任_01B 共通部品(DEV専用・Production経路とは無関係)。
- 単価: er005_output/cost_baseline_01/pricing_snapshot.json (Standard tierのみ)
- cross-detector合算台帳: detectors/cost_ledger.jsonl (全検出器・全runの実費を追記)
- LLM呼び出し: OpenAI Responses API / DeepSeek chat.completions (run_eval_01.pyの実装を流用)
旧モデルは使わない(開発評価=最新モデル原則、PM_GOVERNANCE 25節)。MODELSに載せるのは最新世代のみ。
"""
import datetime
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PRICING_PATH = os.path.join(HERE, "..", "..", "..", "er005_output", "cost_baseline_01", "pricing_snapshot.json")
LEDGER_PATH = os.path.join(HERE, "cost_ledger.jsonl")
USD_JPY = 160  # er006_model_routing_contract_01_cost_recompute.py L14 と同じ

# 最新世代のみ。gpt-5.6-* / gpt-6-luna(効率系は予算上の参考のみ) は載せない。
MODELS = {
    "gpt-6.1-sol": dict(provider="openai", env_key="OPENAI_API_KEY", max_out=8000),
    "gpt-6-astra": dict(provider="openai", env_key="OPENAI_API_KEY", max_out=8000),
    "deepseek-v4-pro": dict(provider="deepseek", env_key="DEEPSEEK_API_KEY", max_out=32000),
}


# 盲検: 検出器に渡してはいけない/ラベル側ファイルにだけ置くキー(make_blind_01.pyとrun_flagger_01.pyが共有)。
# 委任_02 P0(Opus所見1,2): label_basis*/label_src/accident_type/notes/near_dup_group/legacy_ids/synthetic/split等を追加。
LABEL_KEYS = {"label", "labels", "gold", "expected", "human_label", "human_judgement", "severity_label",
              "known_incident", "incident_id", "checker_reference", "checker_verdict", "label_note", "type_label",
              "label_basis", "label_basis_detail", "label_src", "accident_type", "secondary_type", "notes",
              "near_dup_group", "legacy_ids", "legacy_case_id", "synthetic", "split", "neg_group", "hard_negative",
              "sentence_locator", "article_full_text", "ja_counterpart", "origin", "note"}


def estimate_tokens(text):
    ascii_n = sum(1 for c in text if ord(c) < 128)
    return int(ascii_n / 4 + (len(text) - ascii_n) * 1.3) + 1


def load_prices(model, path=PRICING_PATH):
    """(input, cached_input, output) USD/1M。未登録ならNone(fail-closed: 呼び出し側は実行を拒否する)。"""
    try:
        with open(path, encoding="utf-8") as f:
            snap = json.load(f)
    except Exception:  # noqa: BLE001
        return None
    got = {}
    for p in snap.get("prices", []):
        if p.get("tier", "Standard") != "Standard":
            continue
        if p.get("model") == model:
            got[p.get("meter")] = p.get("price")
    if "input_tokens" in got and "output_tokens" in got:
        return got["input_tokens"], got.get("cached_input_tokens", got["input_tokens"]), got["output_tokens"]
    return None


def cost_yen(prices, in_tok, out_tok, cached=0):
    if not prices:
        return None
    pin, pc, pout = prices
    cached = cached or 0
    usd = ((in_tok - cached) * pin + cached * pc + out_tok * pout) / 1e6
    return usd * USD_JPY


def ledger_total(path=None):
    path = path or LEDGER_PATH
    tot = 0.0
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for ln in f:
                ln = ln.strip()
                if ln:
                    try:
                        tot += float(json.loads(ln).get("cost_jpy") or 0)
                    except Exception:  # noqa: BLE001
                        pass
    return tot


def ledger_append(entry, path=None):
    path = path or LEDGER_PATH
    entry = dict(entry)
    entry.setdefault("ts", datetime.datetime.now().isoformat(timespec="seconds"))
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def client_for(cfg):
    from openai import OpenAI
    key = os.environ.get(cfg["env_key"])
    if not key:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            key = os.environ.get(cfg["env_key"])
        except Exception:  # noqa: BLE001
            pass
    if not key:
        raise RuntimeError("環境変数 %s が未設定です(値は出力しません)" % cfg["env_key"])
    if cfg["provider"] == "deepseek":
        return OpenAI(api_key=key, base_url="https://api.deepseek.com")
    return OpenAI(api_key=key)


def call_model(client, model, system, user, max_out=None, effort="medium", cache_key=None):
    """1回呼び出し。戻り値 (text, usage_dict, response_id, model_id)。temperature/seedは送らない(最新モデルは非対応が多い)。"""
    cfg = MODELS[model]
    max_out = max_out or cfg["max_out"]
    if cfg["provider"] == "openai":
        kw = dict(model=model, instructions=system, input=user, reasoning={"effort": effort}, max_output_tokens=max_out)
        if cache_key:  # 委任_03: 同一プレフィックスを同じキャッシュへ寄せる(prompt_cache_key)
            kw["prompt_cache_key"] = cache_key
        resp = client.responses.create(**kw)
        u = resp.usage
        usage = dict(input_tokens=getattr(u, "input_tokens", None), output_tokens=getattr(u, "output_tokens", None),
                     reasoning_tokens=getattr(getattr(u, "output_tokens_details", None), "reasoning_tokens", None),
                     cached_tokens=getattr(getattr(u, "input_tokens_details", None), "cached_tokens", None))
        return resp.output_text, usage, resp.id, getattr(resp, "model", model)
    resp = client.chat.completions.create(
        model=model, messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        response_format={"type": "json_object"}, max_tokens=max_out)
    u = resp.usage
    usage = dict(input_tokens=u.prompt_tokens, output_tokens=u.completion_tokens,
                 reasoning_tokens=getattr(getattr(u, "completion_tokens_details", None), "reasoning_tokens", None),
                 cached_tokens=getattr(u, "prompt_cache_hit_tokens", None))
    return resp.choices[0].message.content or "", usage, resp.id, resp.model
