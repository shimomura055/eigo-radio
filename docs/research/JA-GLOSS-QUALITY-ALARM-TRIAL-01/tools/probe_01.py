# -*- coding: utf-8 -*-
"""JA-GLOSS-QUALITY-ALARM-TRIAL-01 委任_01: 入力形式・出力schemaの動作確認probe(DEV/Trial専用・Production経路に接続しない)。
モデルは gpt-6-luna 固定(ユーザー決定6)。他モデル禁止。呼出ごとにledger記録。Cap到達見込みで停止(委任_01 Cap=15円、12円で止める)。
使い方: probe_01.py <plan.json>   plan={"jobs":[{"name","items":[id...],"effort","mode":"batch|single"}],"cap_jpy":12}
本probeの結果はPrecision/Recallの主張に使わない(スキーマ遵守・token・費用・所要時間の確認のみ)。
"""
import json, os, sys, time

MODEL = "gpt-6-luna"       # 固定。引数で変更できない
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
ENV = r"C:\Users\tensh\eigo-radio\.env"
# 単価(JA-GLOSS-NUANCE-01 TRIAL_01 §7と同一): 入力$0.10 / キャッシュ$0.01 / 出力$0.50 per 1M、160円/USD
P_IN, P_CACHED, P_OUT, FX = 0.10, 0.01, 0.50, 160.0

SCHEMA = {
    "name": "gloss_quality_check",
    "strict": True,
    "schema": {
        "type": "object", "additionalProperties": False, "required": ["results"],
        "properties": {"results": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["id", "warn", "severity", "confidence", "category", "reason_ja", "suggestion"],
            "properties": {
                "id": {"type": "string"},
                "warn": {"type": "boolean"},
                "severity": {"type": "string", "enum": ["none", "minor", "major"]},
                "confidence": {"type": "string", "enum": ["low", "medium", "high"]},
                "category": {"type": "string", "enum": ["none", "meaning_mismatch", "too_generic", "lost_nuance", "established_term_replaced", "unnatural_ja", "inconsistent"]},
                "reason_ja": {"type": "string"},
                "suggestion": {"type": "string"},
            }}}},
    },
}

DEVELOPER = (
    "あなたは英語学習教材の日本語訳レビュアーです。学習対象の英語表現(expression)について、現在の日本語訳(current_ja)が、"
    "本文のこの箇所での意味を適切に表しているかを、本文の文脈に基づいて判定します。特定の語についての決まりごとはありません。"
    "毎回、本文の文脈から判断してください。訳が妥当なら warn=false にします。疑わしいだけで根拠が弱い場合も warn=false にします。"
    "warn=true にするのは、本文の文脈に照らして、意味が合っていない、文脈上の意味でなく一般的すぎる意味になっている、比喩・ニュアンスが失われている、"
    "自然な定訳があるのに不適切に言い換えている、日本語として不自然・冗長・分かりにくい、のいずれかを具体的に説明できるときだけです。"
    "reason_ja は60字以内で具体的に。suggestion は、より適切な訳が明確にあるときだけ書き、なければ空文字にします。"
)


def cost_jpy(u):
    inp = u.get("input_tokens") or 0
    c = u.get("cached_input_tokens") or 0
    out = u.get("output_tokens") or 0
    return ((inp - c) * P_IN + c * P_CACHED + out * P_OUT) / 1e6 * FX


def build_user(article_text, level, items):
    lines = ["【記事全文(英語)】", article_text, "", "【レベル】" + level, "", "【検査対象】"]
    for it in items:
        lines.append(json.dumps({"id": it["id"], "expression": it["expression"], "current_ja": it["current_ja"], "sentence_en": it["sentence_en"],
                                 "context_before": it["context_before"], "context_after": it["context_after"]}, ensure_ascii=False))
    return "\n".join(lines)


def main(plan_path):
    plan = json.load(open(plan_path, encoding="utf-8"))
    from dotenv import load_dotenv
    load_dotenv(ENV)
    from openai import OpenAI
    client = OpenAI()
    items = {i["id"]: i for i in json.load(open(os.path.join(BASE, "eval_set/items.json"), encoding="utf-8"))}
    arts = json.load(open(os.path.join(BASE, "eval_set/articles.json"), encoding="utf-8"))
    ledger_path = os.path.join(BASE, "probe_01", "ledger.json")
    os.makedirs(os.path.dirname(ledger_path), exist_ok=True)
    ledger = json.load(open(ledger_path, encoding="utf-8")) if os.path.exists(ledger_path) else {"model": MODEL, "calls": [], "total_jpy": 0.0}
    cap = float(plan.get("cap_jpy", 12))
    for j in plan["jobs"]:
        if ledger["total_jpy"] + 0.8 > cap:
            print("STOP: cap approaching", ledger["total_jpy"]); sys.exit(3)
        its = [items[i] for i in j["items"]]
        a = arts[its[0]["article_key"]]
        lk = "adv" if its[0]["level"] == "Advanced" else "std"
        user = build_user(a[lk], its[0]["level"], its)
        t0 = time.time()
        r = client.responses.create(model=MODEL, reasoning={"effort": j["effort"]},
                                    text={"format": {"type": "json_schema", **SCHEMA}},
                                    input=[{"role": "developer", "content": DEVELOPER}, {"role": "user", "content": user}])
        if r.model != MODEL and not str(r.model).startswith(MODEL):
            print("MODEL MISMATCH", r.model); sys.exit(4)
        u = r.usage
        usage = {"input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
                 "cached_input_tokens": getattr(getattr(u, "input_tokens_details", None), "cached_tokens", 0) or 0}
        c = cost_jpy(usage)
        el = round(time.time() - t0, 1)
        out = json.loads(r.output_text)
        os.makedirs(os.path.join(BASE, "probe_01"), exist_ok=True)
        json.dump({"job": j, "model": r.model, "response_id": r.id, "usage": usage, "cost_jpy": c, "elapsed_s": el, "output": out},
                  open(os.path.join(BASE, "probe_01", j["name"] + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        ledger["calls"].append({"name": j["name"], "model": r.model, "response_id": r.id, "usage": usage, "cost_jpy": round(c, 4), "elapsed_s": el})
        ledger["total_jpy"] = round(ledger["total_jpy"] + c, 4)
        json.dump(ledger, open(ledger_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(j["name"], usage, round(c, 4), "s=", el, "cum", ledger["total_jpy"])


if __name__ == "__main__":
    main(sys.argv[1])
