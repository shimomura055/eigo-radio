# -*- coding: utf-8 -*-
"""WRITER-EVAL-DUAL-LLM-METHOD-TRIAL-01 評価LLM runner(委任_01c実装・未実行)。

- 入力は eval_items_01.json と eval_prompt_01.txt のみ。人間判定・Checker参考を含む別ファイルは
  コード上いっさい開かない(run_eval_01_test.py が静的に検査する)。
- 1ケース=1呼び出し。評価LLMへ渡すのは case_id/fact/target_sentence/context_before/context_after の5項目のみ
  (context_source は渡さない)。
- Production経路とは無関係のTrial/DEV専用。APIキーは環境変数名のみ参照し値はログに出さない。
使い方:
  python run_eval_01.py --model gpt-6-luna --rep 1 --dry-run
  python run_eval_01.py --model deepseek-v4-flash --rep 1 --dry-run
  実行(別委任): python run_eval_01.py --model gpt-6-luna --rep 1 --max-yen 30
                python run_eval_01.py --model deepseek-v4-flash --rep 1 --allow-unpriced
"""
import argparse
import datetime
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ITEMS_PATH = os.path.join(HERE, "eval_items_01.json")
PROMPT_PATH = os.path.join(HERE, "eval_prompt_01.txt")
PRICING_PATH = os.path.join(HERE, "..", "..", "er005_output", "cost_baseline_01", "pricing_snapshot.json")
USD_JPY = 160  # er006_model_routing_contract_01_cost_recompute.py L14 と同じ
PASS_KEYS = ("case_id", "fact", "target_sentence", "context_before", "context_after")  # 評価LLMへ渡す5項目
LABELS = ("A", "B", "C")
MISREAD_ALL = ("主体対象入替", "肯定否定方向反転", "数量時系列変更", "台帳と逆", "なし", "その他")
MISREAD_FOUR = ("主体対象入替", "肯定否定方向反転", "数量時系列変更", "台帳と逆")
SEED = 20261009
MAX_OUTPUT_TOKENS = 6000  # 推論トークン込み(DeepSeekは可視出力と同一予算)
MODELS = {
    "gpt-6-luna": dict(provider="openai", env_key="OPENAI_API_KEY", priced=True),
    "gpt-5.6-luna": dict(provider="openai", env_key="OPENAI_API_KEY", priced=True),  # 委任_02追加(参考の第2評価者、同じLuna系)
    "gpt-5.6-sol": dict(provider="openai", env_key="OPENAI_API_KEY", priced=True),  # 委任_04追加(単価登録済み)
    "deepseek-v4-flash": dict(provider="deepseek", env_key="DEEPSEEK_API_KEY", priced=True),  # 委任_04で公式単価登録
}
# DeepSeekはreasoning tokenが可視出力と同一予算(er005 _deepseek_call の注記と同じ)。6000だと切り詰めが起きうるため
# 事前登録(PREREGISTRATION_02)でAPI仕様上の必須調整として32000に固定。プロンプト・ケースは不変。
DEEPSEEK_MAX_TOKENS = 32000
OUT_LOW, OUT_HIGH = 600, 4000  # dry-run見積の出力token幅(MODEL_OPTIONS_COST_01.md 4節と同じ)
TRANSIENT_RETRIES = 2  # timeout/5xx/429
FORMAT_RETRIES = 1  # JSON/列挙値違反は1回だけ再呼び出し(上限を増やさない)


def load_items(path=ITEMS_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)["items"]


def load_prompt(path=PROMPT_PATH):
    with open(path, encoding="utf-8") as f:
        return f.read()


def build_user_message(item):
    """評価LLMへ渡すuser内容。5項目のみ、キー順固定。context_source等は渡さない。"""
    return json.dumps({k: item.get(k, "") for k in PASS_KEYS}, ensure_ascii=False)


def validate_result(text, case_id):
    """応答文字列を検証。戻り値 (obj_or_None, violations(list[str]), warnings(list[str]))。
    違反=形式違反(再呼び出し対象)。reason60字超は警告のみ。"""
    v, w = [], []
    try:
        obj = json.loads(text)
    except Exception as e:  # noqa: BLE001
        return None, ["json_parse_error: %s" % type(e).__name__], w
    if not isinstance(obj, dict):
        return None, ["not_a_json_object"], w
    if obj.get("case_id") != case_id:
        v.append("case_id_mismatch")
    label = obj.get("label")
    mt = obj.get("misread_type")
    if label not in LABELS:
        v.append("label_invalid")
    if mt not in MISREAD_ALL:
        v.append("misread_type_invalid")
    reason = obj.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        v.append("reason_missing")
    elif len(reason) > 60:
        w.append("reason_over_60_chars:%d" % len(reason))
    if label == "A" and mt in MISREAD_ALL and mt != "なし":
        v.append("A_requires_misread_none")
    if label == "B" and mt == "なし":
        v.append("B_misread_none_not_allowed")
    if label == "C" and mt in MISREAD_ALL and mt not in MISREAD_FOUR:
        v.append("C_misread_must_be_one_of_four")  # C+その他/なし は形式違反
    return (obj if not v else None), v, w


def estimate_tokens(text):
    ascii_n = sum(1 for c in text if ord(c) < 128)
    return int(ascii_n / 4 + (len(text) - ascii_n) * 1.3) + 1


def load_prices(model):
    """pricing_snapshot.json から (input, cached_input, output) USD/1M。未登録ならNone。"""
    try:
        with open(PRICING_PATH, encoding="utf-8") as f:
            snap = json.load(f)
    except Exception:  # noqa: BLE001
        return None
    got = {}
    for p in snap.get("prices", []):
        if p.get("tier", "Standard") != "Standard":
            continue  # 割引tier(DeepSeek Off-peak等)は費用算出に使わない(委任_04)
        if p.get("model") == model or str(p.get("service", "")).startswith(model):
            got[p.get("meter")] = p.get("price")
    if "input_tokens" in got and "output_tokens" in got:
        return got["input_tokens"], got.get("cached_input_tokens", got["input_tokens"]), got["output_tokens"]
    return None


def cost_yen(prices, in_tok, out_tok, cached=0):
    if not prices:
        return None
    pin, pc, pout = prices
    usd = ((in_tok - cached) * pin + cached * pc + out_tok * pout) / 1e6
    return usd * USD_JPY


def paths(model, rep):
    results = os.path.join(HERE, "results", "%s_rep%d.jsonl" % (model, rep))
    raw = os.path.join(HERE, "logs", "%s_rep%d_raw.jsonl" % (model, rep))
    return results, raw


def dry_run(model, rep, items, prompt, max_yen, allow_unpriced):
    cfg = MODELS[model]
    n = len(items)
    in_tok = sum(estimate_tokens(prompt) + estimate_tokens(build_user_message(i)) for i in items)
    prices = load_prices(model) if cfg["priced"] else None
    results, raw = paths(model, rep)
    print("[DRY-RUN] model=%s provider=%s rep=%d (API非呼び出し)" % (model, cfg["provider"], rep))
    print("  items=%d 呼び出し数(最小)=%d / 最大(形式再呼び出しを全件で使った場合)=%d" % (n, n, n * (1 + FORMAT_RETRIES)))
    print("  見積入力token(全件)=%d  見積出力token/件=%d-%d  上限 max_output_tokens=%d" % (in_tok, OUT_LOW, OUT_HIGH, MAX_OUTPUT_TOKENS))
    print("  渡す項目=%s (context_source・人間判定・Checker情報は渡さない)" % (list(PASS_KEYS),))
    print("  出力先 results=%s logs=%s" % (os.path.relpath(results, HERE), os.path.relpath(raw, HERE)))
    if prices:
        lo = cost_yen(prices, in_tok, n * OUT_LOW)
        hi = cost_yen(prices, in_tok, n * OUT_HIGH)
        print("  見積費用(登録単価 %s)= JPY %.2f - %.2f (形式再呼び出しなしの1rep) / --max-yen=%s" % (model, lo, hi, max_yen))
    else:
        print("  [WARNING] %s は pricing_snapshot.json に単価未登録 = 費用ガード対象外。見積費用は算出不能。" % model)
        print("  [WARNING] 実行には --allow-unpriced (ユーザー承認) が必要。現在 allow_unpriced=%s -> %s"
              % (allow_unpriced, "実行可能" if allow_unpriced else "実行は拒否される"))
    print("  再試行上限: 形式違反=%d回 / 一時障害=%d回。結果を見た再実行・差し替えは禁止。" % (FORMAT_RETRIES, TRANSIENT_RETRIES))
    return 0


def _client(cfg):
    from openai import OpenAI  # 遅延import(テスト・dry-runでは不要)
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


def call_model(client, model, cfg, prompt, user_msg, temperature, eff):
    """1回のAPI呼び出し。戻り値 (text, usage_dict, response_id, model_id)。
    temperature非対応の場合は指定なしで再実行し eff['temperature'] に 'unspecified(rejected)' を記録する。"""
    if cfg["provider"] == "openai":
        kw = dict(model=model, instructions=prompt, input=user_msg, reasoning={"effort": "medium"},
                  max_output_tokens=MAX_OUTPUT_TOKENS)
        eff.update(reasoning="medium", seed="not_supported_not_sent")
        send_t = eff.get("temperature") != "unspecified(rejected)" and temperature is not None
        if send_t:
            kw["temperature"] = temperature
        try:
            resp = client.responses.create(**kw)
            if send_t:
                eff["temperature"] = temperature
        except Exception as e:  # noqa: BLE001
            if send_t and "temperature" in str(e).lower():
                eff["temperature"] = "unspecified(rejected)"
                del kw["temperature"]
                resp = client.responses.create(**kw)
            else:
                raise
        u = resp.usage
        usage = dict(input_tokens=getattr(u, "input_tokens", None), output_tokens=getattr(u, "output_tokens", None),
                     reasoning_tokens=getattr(getattr(u, "output_tokens_details", None), "reasoning_tokens", None),
                     cached_tokens=getattr(getattr(u, "input_tokens_details", None), "cached_tokens", None))
        return resp.output_text, usage, resp.id, getattr(resp, "model", model)
    kw = dict(model=model, messages=[{"role": "system", "content": prompt}, {"role": "user", "content": user_msg}],
              response_format={"type": "json_object"}, max_tokens=DEEPSEEK_MAX_TOKENS)
    eff.update(reasoning="provider_default", seed="not_supported_not_sent")
    send_t = eff.get("temperature") != "unspecified(rejected)" and temperature is not None
    if send_t:
        kw["temperature"] = temperature
    try:
        resp = client.chat.completions.create(**kw)
        if send_t:
            eff["temperature"] = temperature
    except Exception as e:  # noqa: BLE001
        if send_t and "temperature" in str(e).lower():
            eff["temperature"] = "unspecified(rejected)"
            del kw["temperature"]
            resp = client.chat.completions.create(**kw)
        else:
            raise
    u = resp.usage
    usage = dict(input_tokens=u.prompt_tokens, output_tokens=u.completion_tokens,
                 reasoning_tokens=getattr(getattr(u, "completion_tokens_details", None), "reasoning_tokens", None),
                 cached_tokens=getattr(u, "prompt_cache_hit_tokens", None))
    return resp.choices[0].message.content or "", usage, resp.id, resp.model


def run(model, rep, items, prompt, max_yen, temperature):
    cfg = MODELS[model]
    results_path, raw_path = paths(model, rep)
    if os.path.exists(results_path):
        print("既存の結果ファイルがあるため中止します(上書き・選択的再実行の禁止): %s" % results_path)
        return 3
    os.makedirs(os.path.dirname(results_path), exist_ok=True)
    os.makedirs(os.path.dirname(raw_path), exist_ok=True)
    prices = load_prices(model) if cfg["priced"] else None
    client = _client(cfg)
    spent = 0.0
    eff = {}
    format_violation_count = 0
    with open(results_path, "a", encoding="utf-8") as fres, open(raw_path, "a", encoding="utf-8") as fraw:
        for item in items:
            cid = item["case_id"]
            user_msg = build_user_message(item)
            adopted = None
            attempts = 0
            fmt_retry_used = 0
            transient_used = 0
            while True:
                attempts += 1
                if prices and max_yen is not None and spent >= max_yen:
                    print("費用上限 JPY %s に到達したため停止(累計 %.3f)" % (max_yen, spent))
                    return 4
                ts = datetime.datetime.now().isoformat(timespec="seconds")
                try:
                    text, usage, rid, mid = call_model(client, model, cfg, prompt, user_msg, temperature, eff)
                except Exception as e:  # noqa: BLE001
                    fraw.write(json.dumps(dict(case_id=cid, rep=rep, attempt=attempts, ts=ts,
                                               request=dict(system=prompt, user=user_msg),
                                               error=type(e).__name__ + ": " + str(e)[:300],
                                               effective_params=dict(eff)), ensure_ascii=False) + "\n")
                    fraw.flush()
                    if transient_used < TRANSIENT_RETRIES:
                        transient_used += 1
                        time.sleep(2 * transient_used)
                        continue
                    break
                c = cost_yen(prices, usage.get("input_tokens") or 0, usage.get("output_tokens") or 0,
                             usage.get("cached_tokens") or 0)
                if c is not None:
                    spent += c
                obj, viol, warn = validate_result(text, cid)
                fraw.write(json.dumps(dict(case_id=cid, rep=rep, attempt=attempts, ts=ts,
                                           request=dict(system=prompt, user=user_msg),
                                           response_text=text, usage=usage, response_id=rid, model_id=mid,
                                           effective_params=dict(eff), violations=viol, warnings=warn,
                                           cost_jpy_est=c), ensure_ascii=False) + "\n")
                fraw.flush()
                if obj is not None:
                    adopted = (obj, warn, c)
                    break
                format_violation_count += 1
                if fmt_retry_used < FORMAT_RETRIES:
                    fmt_retry_used += 1
                    continue
                break
            if adopted:
                obj, warn, c = adopted
                row = dict(case_id=cid, rep=rep, label=obj["label"], reason=obj["reason"],
                           misread_type=obj["misread_type"], valid_json=True, attempts=attempts,
                           cost_jpy_est=c, warnings=warn)
            else:
                row = dict(case_id=cid, rep=rep, label=None, reason=None, misread_type=None, valid_json=False,
                           attempts=attempts, cost_jpy_est=None, warnings=[])
            fres.write(json.dumps(row, ensure_ascii=False) + "\n")
            fres.flush()
        fres.write(json.dumps(dict(_summary=True, model=model, rep=rep, effective_params=eff,
                                   format_violation_count=format_violation_count,
                                   spent_jpy_est=spent if prices else None), ensure_ascii=False) + "\n")
    print("完了: %s rep%d 形式違反=%d 累計費用(登録単価分)=%s"
          % (model, rep, format_violation_count, ("JPY %.3f" % spent) if prices else "対象外(未登録)"))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=sorted(MODELS))
    ap.add_argument("--rep", type=int, default=1)
    ap.add_argument("--items", default=ITEMS_PATH)
    ap.add_argument("--prompt", default=PROMPT_PATH)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-yen", type=float, default=None, help="費用上限(登録単価のモデルのみ有効)")
    ap.add_argument("--allow-unpriced", action="store_true", help="単価未登録モデル(DeepSeek)の実行をユーザー承認済みとして許可")
    ap.add_argument("--temperature", type=float, default=0.0)
    a = ap.parse_args(argv)
    items, prompt = load_items(a.items), load_prompt(a.prompt)
    cfg = MODELS[a.model]
    if a.dry_run:
        return dry_run(a.model, a.rep, items, prompt, a.max_yen, a.allow_unpriced)
    if not cfg["priced"] and not a.allow_unpriced:
        print("[REFUSED] %s は単価未登録(費用ガード対象外)。--allow-unpriced (ユーザー承認) なしでは起動しません。" % a.model)
        return 2
    if cfg["priced"] and a.max_yen is None:
        print("[REFUSED] --max-yen が必須です。")
        return 2
    if not cfg["priced"]:
        print("[WARNING] %s は単価未登録のため費用ガードが効きません(--allow-unpriced 指定済み)。" % a.model)
    return run(a.model, a.rep, items, prompt, a.max_yen, a.temperature)


if __name__ == "__main__":
    sys.exit(main())
