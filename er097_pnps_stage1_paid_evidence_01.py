# -*- coding: utf-8 -*-
"""PNPS Stage 1 E-2: runtime evidence(有料・最小。実API 1回 + 実URL取得)。論点E: Ledger/sidecarのpathを一時コピーへ差し替えて実施し、
Production Ledger・Production sidecarには何も書かない。使い方: .venv/Scripts/python.exe er097_pnps_stage1_paid_evidence_01.py <word>
(a) 辞書外語1語の `_resolve_unresolved_entity_for_review` 実呼出 = research(実Perplexity 1回) -> 一時Ledger登録 -> 出典URLの実GET照合 -> HR表示キー
(b) 同語の再実行 = 調査0回(Ledger命中。実API 0)
(c) 一般語の実行 = 調査0回(実API 0)
research呼出回数は関数をspyで包んで数える(挙動は変えない)。"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
from dotenv import load_dotenv  # noqa: E402

load_dotenv()
import er005_cost_logger as cl  # noqa: E402
import er006_pronunciation_ledger_01 as L  # noqa: E402
import er006_secondary_asr_01 as sec  # noqa: E402

WORD = sys.argv[1] if len(sys.argv) > 1 else "Saoirse"
OUT = "er097_output/pnps_stage1_wiring_01/runtime_paid"
PROD_LEDGER = "er006_output/pronunciation_ledger_01/ledger.json"
PROD_SIDECAR = "er006_output/pronunciation_ledger_01/negative_cache.json"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None


def main():
    os.makedirs(OUT, exist_ok=True)
    prod_before = (sha(PROD_LEDGER), sha(PROD_SIDECAR))
    tmp_ledger = f"{OUT}/ledger_tmp_copy.json"
    shutil.copyfile(PROD_LEDGER, tmp_ledger)
    L.LEDGER_PATH = tmp_ledger                       # sidecarも同じdirのnegative_cache.jsonへ追随(Production側には書かない)
    cl.init_logger(f"{OUT}/cost_log.jsonl")
    calls = []
    orig = sec.pronun_research.research_pronunciations

    def spy(entities, *a, **k):
        calls.append(entities[0]["surface"])
        return orig(entities, *a, **k)
    sec.pronun_research.research_pronunciations = spy
    fetched = []
    orig_fetch = sec._pron_supply_fetch

    def fspy(url, timeout=5.0, max_bytes=512 * 1024):
        r = orig_fetch(url, timeout, max_bytes)
        fetched.append({"url": url, "got_text": r is not None, "chars": len(r or "")})
        return r
    sec._pron_supply_fetch = fspy

    # 保存済みLedger entry(実調査の過去結果)をreplayする語: Perplexityが401(枠切れ・UDR #134)で実調査できない場合の代替。
    # researchは保存結果の再生(API 0)、出典URLの取得・照合は**実HTTP**(課金0)。一時Ledgerから同綴りentryを除いて初回調査を再現する。
    REPLAY = [w for w in (sys.argv[2].split(",") if len(sys.argv) > 2 else [])]
    stored = json.load(open(PROD_LEDGER, encoding="utf-8"))
    replay_items = {}
    for w in REPLAY:
        cands = [e for e in stored.values() if e["surface"].lower() == w.lower() and e.get("expected_pronunciation_ipa")]
        replay_items[w.lower()] = cands[0]
    tmp = json.load(open(tmp_ledger, encoding="utf-8"))
    tmp = {k: e for k, e in tmp.items() if e["surface"].lower() not in replay_items}
    json.dump(tmp, open(tmp_ledger, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    def replay_or_real(entities, *a, **k):
        surf = entities[0]["surface"]
        if surf.lower() in replay_items:
            e = replay_items[surf.lower()]
            calls.append(surf + "(replay)")
            item = {kk: e.get(kk, "") for kk in ("surface", "entity_type", "canonical_spelling", "language_origin", "expected_pronunciation_ipa",
                                                  "pronunciation_hint", "alternate_pronunciations", "confidence", "ambiguity_note")}
            return {"status": "OK", "items": [item], "citations": e.get("sources", [])}
        return spy(entities, *a, **k)
    sec.pronun_research.research_pronunciations = replay_or_real
    steps = [("a_first_research_REAL_API", WORD)] + [(f"a2_first_{w}_REPLAY_stored_research_REAL_HTTP", w) for w in REPLAY]         + [(f"b_rerun_{w}", w) for w in [WORD] + REPLAY] + [("c1_general_word_no_entry", "good morning"), ("c2_general_word_isolated_entry", "main story")]
    res = {"word": WORD, "tmp_ledger": tmp_ledger, "replay_words": REPLAY, "steps": []}
    for label, w in steps:
        n0, f0 = len(calls), len(fetched)
        sec._stage1_clear()
        info = sec._resolve_unresolved_entity_for_review(w)
        s1 = sec._stage1_take()
        res["steps"].append({"step": label, "word": w, "research_calls": calls[n0:], "fetches": fetched[f0:], "action": s1.get("action"),
                             "info": info, "extra": s1.get("extra")})
        print(label, w, "research_calls=", len(calls) - n0, "fetches=", [(f["url"][:60], f["got_text"]) for f in fetched[f0:]], "action=", s1.get("action"),
              "tier=", (s1.get("extra") or {}).get("evidence_tier"), "has_info=", bool(info))
    led = json.load(open(tmp_ledger, encoding="utf-8"))
    res["tmp_ledger_entries"] = [e for e in led.values() if e["surface"].lower() in ([WORD.lower()] + [w.lower() for w in REPLAY])]
    res["sidecar_tmp"] = f"{OUT}/negative_cache.json" if os.path.exists(f"{OUT}/negative_cache.json") else None
    res["prod_ledger_and_sidecar_sha_before_after_equal"] = prod_before == (sha(PROD_LEDGER), sha(PROD_SIDECAR))
    res["cost_log_rows"] = [json.loads(x) for x in open(f"{OUT}/cost_log.jsonl", encoding="utf-8") if x.strip()]
    json.dump(res, open(f"{OUT}/paid_evidence.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print("prod ledger/sidecar unchanged:", res["prod_ledger_and_sidecar_sha_before_after_equal"], "cost rows:", len(res["cost_log_rows"]))


if __name__ == "__main__":
    main()
