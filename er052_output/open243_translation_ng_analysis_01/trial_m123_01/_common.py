# -*- coding: utf-8 -*-
"""OPEN-243-TRANSLATION-NG-ANALYSIS-01 委任_03 M1-M3 検証の共通部品(Trial専用、Production経路には使われない)。"""
from __future__ import annotations

import json
import os
import re
import sys
import threading

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import er003_v1_en_direct_vfl_01_generate as vfl01  # noqa: E402
import er003_v1_n3_01_advanced_adaptation_generate as adv_gen  # noqa: E402

OUT = "er052_output/open243_translation_ng_analysis_01"
TRIAL = f"{OUT}/trial_m123_01"
BUDGET_CAP_JPY = 60.0
SPEND_FILE = f"{TRIAL}/spend_ledger.jsonl"

_lock = threading.Lock()
_price = None


def price_fn():
    global _price
    if _price is None:
        _price = adv_gen._load_pricing()
    return _price


def cost_of(model: str, usage: dict) -> float:
    u = usage or {}
    return adv_gen._compute_cost_jpy(price_fn(), model, u.get("input_tokens") or 0,
                                      u.get("cached_input_tokens") or 0, u.get("output_tokens") or 0)[1]


def total_spend() -> float:
    if not os.path.exists(SPEND_FILE):
        return 0.0
    t = 0.0
    for l in open(SPEND_FILE, encoding="utf-8"):
        try:
            t += json.loads(l)["cost_jpy"]
        except Exception:
            pass
    return t


def record_spend(tag: str, model: str, usage: dict, cost_jpy: float | None = None) -> float:
    c = cost_of(model, usage) if cost_jpy is None else cost_jpy
    with _lock:
        os.makedirs(TRIAL, exist_ok=True)
        with open(SPEND_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps({"tag": tag, "model": model, "usage": usage, "cost_jpy": c}, ensure_ascii=False) + "\n")
    return c


def check_budget(extra: float = 0.0) -> None:
    if total_spend() + extra > BUDGET_CAP_JPY:
        raise RuntimeError(f"[STOP] budget cap {BUDGET_CAP_JPY} JPY reached: spent={total_spend():.2f}")


def checked_deviation(client, ledger, article, ja, tag, prior_issues=None):
    check_budget()
    r = vfl01.run_deviation_check(client, ledger, article, hook_aware=False, include_related_fact_id=True,
                                  source_article_text=ja, prior_issues=prior_issues)
    r["cost_jpy"] = record_spend(tag, r["model"], r["usage"])
    return r


def parse_attempt_prompt(prompt: str) -> dict:
    """advanced_attemptN.json の prompt から ledger / EN article / JA を取り出す。"""
    i_led = prompt.index("【Verified Fact Ledger】\n") + len("【Verified Fact Ledger】\n")
    i_art = prompt.index("\n\n【検証対象の記事】\n")
    i_art_s = i_art + len("\n\n【検証対象の記事】\n")
    i_next = prompt.index("\n\n【判定対象は次の10種類の意味変化のみです】")
    i_src = prompt.index("\n【原文記事(翻訳・適応元)】\n") + len("\n【原文記事(翻訳・適応元)】\n")
    ledger = prompt[i_led:i_art]
    article = prompt[i_art_s:i_next]
    ja = prompt[i_src:]
    # prior_issues付きpromptはJA原文の後ろに「前回指摘」節が続くため切る
    j = ja.find("\n\n【追加指示: 前回指摘の解消確認】")
    if j >= 0:
        ja = ja[:j]
    return {"ledger": ledger, "article": article, "ja": ja}


def split_article(article: str) -> dict:
    m = re.match(r"^#\s+(.+?)\s*\n\n(.+?)\n\n## In one line\n(.+)$", article.strip(), re.S)
    if not m:
        return {}
    return {"title": m.group(1).strip(), "body": m.group(2).strip(), "summary": m.group(3).strip()}


def norm(t: str) -> str:
    return re.sub(r"[^0-9a-z]+", "", (t or "").lower())


def sent_match(event_sentence: str, claim: str) -> bool:
    a, b = norm(event_sentence), norm(claim)
    if not a or not b:
        return False
    if len(b) >= 12 and (b in a or a in b):
        return True
    wa = set(re.findall(r"[a-z0-9]+", (event_sentence or "").lower()))
    wb = set(re.findall(r"[a-z0-9]+", (claim or "").lower()))
    if not wa or not wb:
        return False
    return len(wa & wb) / max(1, min(len(wa), len(wb))) >= 0.8


def dev_summary(dev_result: dict) -> list:
    out = []
    for d in (dev_result.get("parsed") or {}).get("deviations", []):
        out.append({"claim": d.get("claim_in_article"), "severity": d.get("severity"), "origin": d.get("origin"),
                    "flags": [k for k in vfl01.DEVIATION_FLAG_KEYS if d.get(k)], "fact_id": d.get("related_fact_id"),
                    "issue": d.get("issue")})
    return out


def jdump(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
