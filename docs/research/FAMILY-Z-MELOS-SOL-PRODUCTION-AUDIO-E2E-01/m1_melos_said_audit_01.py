# -*- coding: utf-8 -*-
"""委任_15 W6: M1(er006_m1_multi_candidate_01)が「Melos said.」に対する ASR「Mello said.」/「Mellow said.」を受理する経路のオフライン監査。
JPY0・API呼出なし・Production非接続(読み取りのみ。Ledgerは読取snapshot、書込なし)。
実行: .venv/Scripts/python.exe docs/research/FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01/m1_melos_said_audit_01.py"""
from __future__ import annotations

import copy
import json
import os
import sys

sys.path.insert(0, os.getcwd())
import er006_m1_multi_candidate_01 as m1
import er006_pronunciation_ledger_01 as pl

CASES = [("Melos said.", "Mello said."), ("Melos said.", "Mellow said."), ("Melos said.", "Melo said."),
         ("Melos called across the hall,", "Mellos called across the hall.")]


def run(label, ledger):
    out = []
    fz = m1.freeze_candidates("Melos said. Melos called across the hall,", ledger_snapshot=ledger,
                              segment_started_at="2026-10-17T00:00:00")
    words = {fw.word: {"candidates": [{"pron": list(c.pron), "source": c.source, "confidence": c.confidence,
                                       "ledger_key": c.ledger_key, "updated_at": c.updated_at, "ipa_raw": c.ipa_raw}
                                      for c in fw.candidates],
                       "excluded": [json.loads(x) for x in fw.excluded]} for fw in fz.words if fw.word in ("melos", "said")}
    for canon, asr in CASES:
        r = m1.m1_multi_candidate_judge(canon, asr, fz)
        out.append({"canonical": canon, "asr": asr, "accepted": r.accepted, "reason": r.reason,
                    "subs": r.audit.get("subs"), "no_match_reason": r.audit.get("no_match_reason")})
    return {"label": label, "frozen_words": words, "results": out}


def main():
    live = copy.deepcopy(pl._load())
    melos_entries = {k: {kk: v for kk, v in e.items() if kk in ("surface", "entity_type", "canonical_spelling", "expected_pronunciation_ipa",
                                                                 "alternate_pronunciations", "sources", "confidence", "updated_at")}
                     for k, e in live.items() if (e.get("surface") or "").strip().lower() in ("melos", "mello", "mellow", "mellos")}
    doc = {"cmu_melos": [list(x) for x in m1.default_cmu("melos")], "cmu_mello": [list(x) for x in m1.default_cmu("mello")],
           "cmu_mellow": [list(x) for x in m1.default_cmu("mellow")], "ledger_melos_family_entries": melos_entries,
           "systems": [run("M1 ON / live Ledger snapshot", live), run("M1 ON / empty Ledger (CMU only)", {})]}
    print(json.dumps(doc, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
