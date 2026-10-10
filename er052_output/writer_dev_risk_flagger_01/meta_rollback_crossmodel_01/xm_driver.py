# -*- coding: utf-8 -*-
"""META-ROLLBACK-CROSSMODEL-01: META実在稿 x A3/A4 x 8条件(モデルのみ差し替え)。
Prompt/入力/splitter/台帳/parse(validate_flags)/retry機構は rb_driver.py(前回)と同一のコード経路を使う。Providerごとの最適化なし。
usage:
  xm_driver.py dry                      全8条件のリクエスト本体をdry_run/へ出力し前回とのprompt一致を検証(API非呼び出し)
  xm_driver.py estimate                 費用見積 estimate_01.json
  xm_driver.py selftest                 canned応答でadapterのparseを検証(API非呼び出し)
  xm_driver.py run <model_key> <3|4> --execute   課金API呼び出し(Phase 1では実行しない。Phase 2で承認後のみ)
"""
import json, os, sys, time, hashlib, copy
sys.dont_write_bytecode = True
XHERE = os.path.dirname(os.path.abspath(__file__))
PE = os.path.join(XHERE, "..", "post_en_trial_01"); sys.path.insert(0, PE)
import post_en_common as C
from post_en_common import *   # REPO, L, R, P, A, LR, HDR, sha_b, EFFORT ...
os.chdir(REPO)
from dotenv import load_dotenv
load_dotenv()
import requests

ART = "er019_output/meta/run_03/b1b/article.md"; LED = "er019_output/meta/run_03/ledger/verified_fact_ledger.txt"
TARGET = "The company also restored the human concierge feature to the way it had been before, at least for now."
EXPECT = dict(article_sha256="cab7f5f3a147b3944558b738fdcb8888f5c754267d47cf177a9438f3d400b327",
              ledger_sha256="6e271bb24fdf3a587bd803d80cec5d32aaaaeb047ca3389c1597283aa3719db4",
              sha_A3="9d9950428419c3af824cc5b8676a4b564f96aeb87657c547d418cc86ef3538e9",
              sha_A4="c87b95e5bcf1b5c266b8978c5688849eb339a6087efbcaf56bb7399ed128ef01")
PREV_RAW = {3: "er052_output/writer_dev_risk_flagger_01/meta_rollback_check_01/runs/d2_gpt-6.1-sol_rb_A3_meta_run03_b1b_raw.jsonl",
            4: "er052_output/writer_dev_risk_flagger_01/meta_rollback_check_01/runs/d2_gpt-6.1-sol_rb_A4_meta_run03_b1b_raw.jsonl"}
MAX_OUT = 8000   # 前回(flagger_lib.MODELS)と同じ。thinking tokensを含むProviderでも同値
TIMEOUT = 240
LEDGER_XM = os.path.join(XHERE, "cost_ledger_xm_01.jsonl")
PRICES = json.load(open(os.path.join(XHERE, "xm_prices_01.json"), encoding="utf-8"))["prices"]

# model_key -> 条件定義(actual model_idはmodels list(無料)で実在確認済み。置換なし)
CONDS = {
    "gemini35fl": dict(label="Gemini 3.5 Flash-Lite", provider="gemini", model_id="gemini-3.5-flash-lite"),
    "gemini38f": dict(label="Gemini 3.8 Flash", provider="gemini", model_id="gemini-3.8-flash"),
    "dsflash": dict(label="DeepSeek V4 Flash", provider="deepseek", model_id="deepseek-flash", thinking="disabled"),
    "dsflash_think": dict(label="DeepSeek V4 Flash Thinking", provider="deepseek", model_id="deepseek-flash", thinking="enabled"),
    "haiku45": dict(label="Claude Haiku 4.5", provider="anthropic", model_id="claude-haiku-4-5-20251001"),
    "sonnet5": dict(label="Claude Sonnet 5", provider="anthropic", model_id="claude-sonnet-5"),
    "luna": dict(label="Luna", provider="openai", model_id="gpt-6-luna"),
    "sol": dict(label="Sol", provider="openai", model_id="gpt-6.1-sol"),
}

# ---------------------------------------------------------------- 入力(rb_driver.build と同一ロジック)
def build():
    ap = os.path.join(REPO, ART); lp = os.path.join(REPO, LED)
    art = open(ap, encoding="utf-8").read(); txt = open(lp, encoding="utf-8").read()
    lines = txt.splitlines()
    n_broad = sum(1 for l in lines if l.startswith("[")); n_hdr = sum(1 for l in lines if HDR.match(l))
    facts = LR.parse_ledger_text(txt)
    ss = [dict(sid="s%d" % (i + 1), text=s, before="", after="") for i, s in enumerate(R._split_sentences(art))]
    unit = dict(unit_id="RB01", mode="article", facts=facts, sentences=ss, ledger_complete=True, article_path=ap)
    info = dict(article=ART, article_sha256=sha_b(open(ap, "rb").read()), ledger=LED, ledger_sha256=sha_b(txt.encode("utf-8")),
                n_facts=len(facts), n_sentences=len(ss), target_sids=[s["sid"] for s in ss if "restored the human concierge" in s["text"]])
    assert n_broad == n_hdr == len(facts) == 15 and TARGET in art and info["target_sids"] == ["s23"], info
    assert info["article_sha256"] == EXPECT["article_sha256"] and info["ledger_sha256"] == EXPECT["ledger_sha256"], "input sha mismatch"
    return unit, info

def system_for(level):
    s = A.antenna_system(level)
    assert A.sha(s) == EXPECT["sha_A%d" % level], "prompt sha mismatch A%d" % level
    return s

# ---------------------------------------------------------------- Provider adapters
def _key(name):
    k = os.environ.get(name)
    if not k: raise RuntimeError("環境変数 %s が未設定(値は出力しない)" % name)
    return k

def build_request(cond, system, user):
    """(url, headers_without_secret, body)。dry-runにも実呼び出しにも同じ関数を使う。"""
    p, mid = cond["provider"], cond["model_id"]
    if p == "openai":   # 前回と同一: Responses API, reasoning effort=medium, max_output_tokens=8000(SDK kwargsと同じ)
        return ("openai-sdk:responses.create", {}, dict(model=mid, instructions=system, input=user, reasoning={"effort": EFFORT},
                max_output_tokens=MAX_OUT))
    if p == "anthropic":  # 追加必須: max_tokens, anthropic-version。thinking/effort/temperatureは送らない(Provider既定)
        return ("https://api.anthropic.com/v1/messages", {"anthropic-version": "2023-06-01", "content-type": "application/json"},
                dict(model=mid, max_tokens=MAX_OUT, system=system, messages=[{"role": "user", "content": user}]))
    if p == "gemini":    # 追加必須: contents形式。thinkingConfig/temperature/responseMimeTypeは送らない(Provider既定)
        return ("https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent" % mid, {"content-type": "application/json"},
                dict(systemInstruction={"parts": [{"text": system}]}, contents=[{"role": "user", "parts": [{"text": user}]}],
                     generationConfig={"maxOutputTokens": MAX_OUT}))
    if p == "deepseek":  # OpenAI互換chat.completions。thinkingは明示(既定がenabledのため、非Thinking条件はdisabledを明示)。reasoning_effort/temperature/response_formatは送らない
        return ("https://api.deepseek.com/chat/completions", {"content-type": "application/json"},
                dict(model=mid, messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                     max_tokens=MAX_OUT, thinking={"type": cond["thinking"]}))
    raise ValueError(p)

def parse_response(cond, j):
    """-> (text, usage, response_id, model_id_returned)。usage: input_tokens, output_tokens(thinking込み), reasoning_tokens, cached_tokens"""
    p = cond["provider"]
    if p == "anthropic":
        txt = "".join(b.get("text", "") for b in j.get("content", []) if b.get("type") == "text")
        u = j.get("usage", {}); cr = u.get("cache_read_input_tokens", 0) or 0; cc = u.get("cache_creation_input_tokens", 0) or 0
        usage = dict(input_tokens=(u.get("input_tokens", 0) or 0) + cr + cc, output_tokens=u.get("output_tokens", 0), reasoning_tokens=None,
                     cached_tokens=cr, cache_creation_tokens=cc, thinking_blocks=sum(1 for b in j.get("content", []) if b.get("type") in ("thinking", "redacted_thinking")),
                     stop_reason=j.get("stop_reason"))
        return txt, usage, j.get("id"), j.get("model")
    if p == "gemini":
        cands = j.get("candidates") or [{}]
        parts = (cands[0].get("content") or {}).get("parts", [])
        txt = "".join(x.get("text", "") for x in parts if not x.get("thought"))
        u = j.get("usageMetadata", {}); th = u.get("thoughtsTokenCount", 0) or 0
        usage = dict(input_tokens=u.get("promptTokenCount", 0), output_tokens=(u.get("candidatesTokenCount", 0) or 0) + th, reasoning_tokens=th,
                     cached_tokens=u.get("cachedContentTokenCount", 0) or 0, finish_reason=cands[0].get("finishReason"))
        return txt, usage, j.get("responseId"), j.get("modelVersion")
    if p == "deepseek":
        ch = j["choices"][0]; u = j.get("usage", {})
        usage = dict(input_tokens=u.get("prompt_tokens", 0), output_tokens=u.get("completion_tokens", 0),
                     reasoning_tokens=(u.get("completion_tokens_details") or {}).get("reasoning_tokens"),
                     cached_tokens=u.get("prompt_cache_hit_tokens", 0) or 0, finish_reason=ch.get("finish_reason"))
        return ch["message"].get("content") or "", usage, j.get("id"), j.get("model")
    raise ValueError(p)

RAW_HTTP = {}   # (model_key, level) -> list of raw responses(A<level>.json の raw_http に保存)

def call_adapter(model_key, level, system, user):
    cond = CONDS[model_key]; url, hdr, body = build_request(cond, system, user)
    if cond["provider"] == "openai":
        from openai import OpenAI
        resp = OpenAI(api_key=_key("OPENAI_API_KEY")).responses.create(**body)
        u = resp.usage
        usage = dict(input_tokens=getattr(u, "input_tokens", None), output_tokens=getattr(u, "output_tokens", None),
                     reasoning_tokens=getattr(getattr(u, "output_tokens_details", None), "reasoning_tokens", None),
                     cached_tokens=getattr(getattr(u, "input_tokens_details", None), "cached_tokens", None))
        RAW_HTTP.setdefault((model_key, level), []).append(resp.model_dump())
        return resp.output_text, usage, resp.id, getattr(resp, "model", cond["model_id"])
    h = dict(hdr)
    if cond["provider"] == "anthropic": h["x-api-key"] = _key("ANTHROPIC_API_KEY")
    elif cond["provider"] == "gemini": h["x-goog-api-key"] = _key("GEMINI_API_KEY")
    elif cond["provider"] == "deepseek": h["Authorization"] = "Bearer " + _key("DEEPSEEK_API_KEY")
    r = requests.post(url, headers=h, json=body, timeout=TIMEOUT)
    try: j = r.json()
    except Exception: j = {"_non_json": r.text[:500]}
    RAW_HTTP.setdefault((model_key, level), []).append(dict(http_status=r.status_code, body=j))
    if r.status_code != 200:
        raise RuntimeError("HTTP %s: %s" % (r.status_code, json.dumps(j, ensure_ascii=False)[:300]))
    return parse_response(cond, j)

# ---------------------------------------------------------------- dry-run / estimate / selftest
def cmd_dry():
    unit, info = build()
    out_dir = os.path.join(XHERE, "dry_run"); os.makedirs(out_dir, exist_ok=True)
    report = dict(info=info, conds={}, prompt_match={})
    for lv in (3, 4):
        sysm = system_for(lv); user = P.build_user(unit)
        prev = json.loads(open(os.path.join(REPO, PREV_RAW[lv]), encoding="utf-8").readline())["request"]
        report["prompt_match"]["A%d" % lv] = dict(system_sha=A.sha(sysm), system_equal_prev_raw=(sysm == prev["system"]),
                                                  user_sha=sha_b(user.encode("utf-8")), user_equal_prev_raw=(user == prev["user"]),
                                                  user_chars=len(user), system_chars=len(sysm))
        assert sysm == prev["system"] and user == prev["user"], "prompt differs from previous run A%d" % lv
        for k, cond in CONDS.items():
            url, hdr, body = build_request(cond, sysm, user)
            d = os.path.join(out_dir, k); os.makedirs(d, exist_ok=True)
            json.dump(dict(model_key=k, level=lv, endpoint=url, extra_headers=hdr, auth="(実行時にヘッダへ鍵を付与するが値は記録しない)", body=body),
                      open(os.path.join(d, "A%d_request.json" % lv), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            report["conds"].setdefault(k, {})["A%d" % lv] = dict(body_sha=sha_b(json.dumps(body, sort_keys=True, ensure_ascii=False).encode("utf-8")))
    json.dump(report, open(os.path.join(out_dir, "dry_run_report_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(report["prompt_match"], ensure_ascii=False, indent=1)); print("written:", out_dir)

PREV_USAGE = {3: (5060, 692), 4: (5210, 632)}   # 前回実測(gpt-6.1-sol): (input, output incl reasoning)
THINK_DEFAULT_ON = {"gemini35fl", "gemini38f", "dsflash_think", "sonnet5"}   # Provider既定でthinking有り(sonnet5は未確認=保守側で扱う)
def cmd_estimate():
    est = {}; tot = dict(low=0.0, central=0.0, high=0.0)
    for k, cond in CONDS.items():
        pr = PRICES.get(cond["model_id"])
        row = {}
        if not pr: est[k] = dict(status="PRICE_UNCONFIRMED"); continue
        for lv in (3, 4):
            i, o = PREV_USAGE[lv]
            f = lambda it, ot: (it * pr["in"] + ot * pr["out"]) / 1e6 * L.USD_JPY
            hi_o = max(o * 3, 4000) if k in THINK_DEFAULT_ON else o * 3
            row["A%d" % lv] = dict(low=round(f(i * 0.9, o * 0.5), 3), central=round(f(i, o), 3), high=round(f(i * 1.35, hi_o), 3))
        row["total_2call"] = {x: round(row["A3"][x] + row["A4"][x], 3) for x in ("low", "central", "high")}
        est[k] = row
        for x in tot: tot[x] += row["total_2call"][x]
    res = dict(basis="前回実測(gpt-6.1-sol) A3 in5060/out692, A4 in5210/out632。low=in*0.9,out*0.5 / central=同値 / high=in*1.35(tokenizer差),out=max(3x,thinking既定ONなら4000)。format再試行・transient再試行が各1回発生した場合は最悪で約2倍(高位に含まず)",
               usd_jpy=L.USD_JPY, per_model=est, total={k: round(v, 3) for k, v in tot.items()})
    json.dump(res, open(os.path.join(XHERE, "estimate_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False, indent=1))

def cmd_selftest():
    canned = {
        "anthropic": dict(id="msg_x", model="claude-sonnet-5", content=[{"type": "thinking", "thinking": "..."}, {"type": "text", "text": '{"flags": []}'}],
                          usage=dict(input_tokens=10, output_tokens=5, cache_read_input_tokens=0), stop_reason="end_turn"),
        "gemini": dict(responseId="r1", modelVersion="gemini-3.8-flash", candidates=[dict(content=dict(parts=[{"text": "t", "thought": True}, {"text": '{"flags": []}'}]), finishReason="STOP")],
                       usageMetadata=dict(promptTokenCount=10, candidatesTokenCount=4, thoughtsTokenCount=6, cachedContentTokenCount=0)),
        "deepseek": dict(id="d1", model="deepseek-flash", choices=[dict(message=dict(content='{"flags": []}', reasoning_content="r"), finish_reason="stop")],
                         usage=dict(prompt_tokens=10, completion_tokens=9, completion_tokens_details=dict(reasoning_tokens=5), prompt_cache_hit_tokens=0)),
    }
    for p, j in canned.items():
        cond = next(c for c in CONDS.values() if c["provider"] == p)
        t, u, rid, mid = parse_response(cond, j)
        assert json.loads(t) == {"flags": []}, (p, t); print(p, "parse OK", u)

# ---------------------------------------------------------------- 実行(Phase 2のみ。--execute必須)
def cmd_run(model_key, level):
    assert "--execute" in sys.argv, "--execute が必要(Phase 1では実行しない)"
    assert level in (3, 4) and model_key in CONDS
    cond = CONDS[model_key]; mid = cond["model_id"]; pr = PRICES.get(mid)
    assert pr, "price unconfirmed: " + mid
    unit, info = build(); sysm = system_for(level)
    run_dir = os.path.join(XHERE, "runs", model_key); os.makedirs(run_dir, exist_ok=True)
    out_json = os.path.join(run_dir, "A%d.json" % level)
    assert not os.path.exists(out_json), "既存結果あり(各1回のみ・上書き禁止): " + out_json
    # R.run_llm(前回と同じ検証/retry機構)を、モデル呼び出しだけ差し替えて使う
    L.LEDGER_PATH = LEDGER_XM
    L.MODELS[model_key] = dict(provider="xm", env_key="-", max_out=MAX_OUT)
    L.load_prices = lambda m: (pr["in"], pr["cached"], pr["out"]) if m == model_key else None
    L.client_for = lambda cfg: None
    L.call_model = lambda client, model, system, user, max_out=None, effort="medium", cache_key=None: call_adapter(model_key, level, system, user)
    P.d2_system = lambda: A.antenna_system(level)
    R.RESULTS_DIR = run_dir; R.LOGS_DIR = run_dir
    cell = "xm_A%d_meta_run03_b1b" % level
    t0 = time.time(); ts = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    rc = R.run_llm([unit], "d2", model_key, cell, 8.0, 40.0, None, EFFORT, None, False)
    el = time.time() - t0
    rp = R.result_paths("d2", model_key, cell)
    d2 = json.loads(open(rp[0], encoding="utf-8").readline())
    raw = [json.loads(x) for x in open(rp[1], encoding="utf-8") if x.strip()]
    out = dict(level=level, model_key=model_key, label=cond["label"], model_id_requested=mid, model_ids_returned=sorted({r.get("model_id") for r in raw if r.get("model_id")}),
               provider=cond["provider"], thinking_setting=cond.get("thinking", "provider_default"), started=ts, system_prompt_sha256=A.sha(sysm),
               max_out=MAX_OUT, **info, rc=rc, valid_json=d2["valid_json"], attempts=d2["attempts"], cost_jpy=d2["cost_jpy"], elapsed_s=round(el, 2),
               usage=[r.get("usage") for r in raw if r.get("usage")], flags=d2["flags"], sentences={s["sid"]: s["text"] for s in unit["sentences"]},
               facts={f["fact_id"]: f["text"] for f in unit["facts"]}, raw_http=RAW_HTTP.get((model_key, level), []))
    json.dump(out, open(out_json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(model_key, "A%d" % level, "flags=%d cost=%.3f valid=%s attempts=%s rc=%s" % (len(d2["flags"]), d2["cost_jpy"], d2["valid_json"], d2["attempts"], rc))

if __name__ == "__main__":
    a = sys.argv[1]
    if a == "dry": cmd_dry()
    elif a == "estimate": cmd_estimate()
    elif a == "selftest": cmd_selftest()
    elif a == "run": cmd_run(sys.argv[2], int(sys.argv[3]))
    else: sys.exit("unknown")
