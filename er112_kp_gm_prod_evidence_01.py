# -*- coding: utf-8 -*-
"""FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_20: 課題②+A-1 Production配線後のruntime evidence採取script(証跡採取専用・Production変更0)。

Productionのcanonicalization部品(kc.load_prompt_template[fulltext] / kc.build_user_message / kc.make_canonicalization_fn[fulltext schema] /
kc.run_canonicalization_gate[postprocess=er105.postprocess_possessor_roles] / kc.merge_canonicalization_result)を**DEV patchなしで**直接呼び、
既存Trial_04の36 unit(`er112_output/kp_gm_trial_04/poss_units.json`)のtextで1rep実行する(P-T2確認 + 正式経路の関数evidence)。
記録: actual model_id / routing(process/model) / template sha / schema sha / developer message sha / flag状態 / 生出力(後処理前)と後処理後のkey /
roles / person_role_repair / 外側retry相当(gate attempts数)/ 費用(円)。音声なし・公開物を書き換えない(出力は`er112_output/kp_gm_prod_01/`のみ)。
サブコマンド: pt2 (36 unit x 1rep) / summary
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

import er003_key_words_canonicalization as kc   # noqa: E402
import er105_kp_fulltext_selector_01 as ft      # noqa: E402
import er006_model_routing_contract_01 as routing  # noqa: E402
import er009_n1_routing_governance_10_actual_model_cost as pricing  # noqa: E402
import er019_family_x_kp_explanation_01 as kx   # noqa: E402

OUT = ROOT / "er112_output" / "kp_gm_prod_01"
UNITS = ROOT / "er112_output" / "kp_gm_trial_04" / "poss_units.json"
LEDGER = OUT / "paid_calls.jsonl"
STOP_PATHS = [OUT / "STOP", OUT / "STOP_ALL", ROOT / "er026_output/family_z_production_e2e_01/STOP_ALL"]
_lock = threading.Lock()


def stop() -> bool:
    return any(p.exists() for p in STOP_PATHS)


def total() -> float:
    t = 0.0
    if LEDGER.exists():
        for line in LEDGER.read_text(encoding="utf-8").splitlines():
            if line.strip():
                t += json.loads(line).get("cost_jpy") or 0
    return t


def ledger_add(rec: dict) -> None:
    with _lock:
        LEDGER.parent.mkdir(parents=True, exist_ok=True)
        with open(LEDGER, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


class _RecResponses:
    def __init__(self, real, tag):
        self._real, self._tag = real, tag

    def create(self, **kw):
        r = self._real.responses.create(**kw)
        u = kx._usage_dict(getattr(r, "usage", None))
        c = pricing.cost_jpy_for_call("openai", r.model or kw.get("model"), u.get("input_tokens"), u.get("cached_input_tokens"), u.get("output_tokens"))
        ledger_add({"tag": self._tag, "model": r.model, "response_id": r.id, "usage": u, "cost_jpy": c})
        return r


class RecClient:
    """openai clientの薄いラッパ(usageを台帳へ記録するだけ。リクエスト/レスポンスは無改変)。"""
    def __init__(self, tag):
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
        from openai import OpenAI
        self.responses = _RecResponses(OpenAI(), tag)


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def run_unit(u: dict, process: str = "B1_SUPPORT") -> dict:
    items = u["original_items"]
    template = kc.load_prompt_template(kc.FULLTEXT_PROMPT_TEMPLATE_PATH)
    user_message = kc.build_user_message(items, u["article_text"], template=template)
    model = routing.require_model(process, routing.SUPPORT_MODEL)
    client = RecClient(f"canon:{u['unit_id']}")

    def make_factory():
        return kc.make_canonicalization_fn(user_message, client=client, model=model, schema=kc.CANONICALIZATION_JSON_SCHEMA_FULLTEXT)

    parsed, status, attempts, model_id, response_id = kc.run_canonicalization_gate(
        make_factory, items, postprocess=ft.postprocess_possessor_roles)
    rec = {"unit_id": u["unit_id"], "status": status, "model_id": model_id, "response_id": response_id, "process": process,
           "routing_model": model, "n_attempts": len(attempts),
           "attempt_statuses": [a.get("status") for a in attempts],
           "template_sha256": sha(template), "schema_sha256": sha(json.dumps(kc.CANONICALIZATION_JSON_SCHEMA_FULLTEXT, sort_keys=True)),
           "developer_message_sha256": sha(kc.DEVELOPER_MESSAGE), "user_message_sha256": sha(user_message), "items": []}
    raw_by_rank = {}
    if attempts and attempts[-1].get("raw_text"):
        try:
            raw_by_rank = {x["rank"]: x for x in json.loads(attempts[-1]["raw_text"])["items"]}
        except Exception:   # noqa: BLE001
            raw_by_rank = {}
    if parsed:
        for it in parsed["items"]:
            raw = raw_by_rank.get(it["rank"], {})
            disp = next(o["display_phrase"] for o in items if o["rank"] == it["rank"])
            rec["items"].append({
                "rank": it["rank"], "display": disp, "key_raw_llm": raw.get("key_phrase"), "reason_raw_llm": raw.get("normalization_reason"),
                "key_final": it["key_phrase"], "reason_final": it.get("normalization_reason"), "roles": it.get("possessor_roles"),
                "person_role_repair": it.get("person_role_repair"), "gold": (u.get("gold") or {}).get(str(it["rank"]))})
        if status in ("CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
            merged = kc.merge_canonicalization_result(items, parsed["items"])
            rec["merged_overall_status"] = merged["overall_status"]
            rec["merged_used_form"] = [m["used_form"] for m in merged["items"]]
    return rec


def cmd_pt2(a):
    units = json.load(open(UNITS, encoding="utf-8"))["units"]
    if a.units:
        units = [u for u in units if any(w in u["unit_id"] for w in a.units.split(","))]
    d = OUT / "pt2"
    d.mkdir(parents=True, exist_ok=True)

    def w(u):
        if stop() or total() >= a.cap:
            return (u["unit_id"], "SKIP")
        p = d / f"{u['unit_id']}.json"
        if p.exists():
            return (u["unit_id"], "EXISTS")
        rec = run_unit(u)
        p.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
        return (u["unit_id"], rec["status"])
    with ThreadPoolExecutor(a.workers) as ex:
        for f in as_completed([ex.submit(w, u) for u in units]):
            print(f.result(), "cum=%.3f" % total(), flush=True)


def cmd_summary(a):
    import collections
    d = OUT / "pt2"
    st, rp, rows = collections.Counter(), collections.Counter(), []
    n_items = n_poss = 0
    for p in sorted(d.glob("*.json")):
        r = json.loads(p.read_text(encoding="utf-8"))
        st[r["status"]] += 1
        for it in r["items"]:
            n_items += 1
            prr = it.get("person_role_repair") or {}
            rp[prr.get("status")] += 1
            if prr.get("status") not in (None, "NO_POSSESSIVE"):
                n_poss += 1
                rows.append((r["unit_id"], it["display"], it["key_raw_llm"], it["key_final"], prr.get("status"), it.get("roles"), it.get("gold")))
    print("units", sum(st.values()), "canon_status", dict(st), "items", n_items, "possessive items", n_poss, "repair_status", dict(rp))
    print("total_cost_jpy %.3f" % total())
    for row in rows:
        print(row)


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("pt2")
    p.add_argument("--cap", type=float, default=14.0)
    p.add_argument("--workers", type=int, default=3)
    p.add_argument("--units", default="")
    p.set_defaults(fn=cmd_pt2)
    q = sp.add_parser("summary")
    q.set_defaults(fn=cmd_summary)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
