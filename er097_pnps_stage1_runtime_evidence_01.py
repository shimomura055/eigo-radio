# -*- coding: utf-8 -*-
"""PNPS Stage 1 E-2: Family X/Z Production関数 発火証拠 runner(API 0)。

er094_pnmh_runtime_evidence_01 のharness(TTS/ASR seamだけ差替え、Production関数・Validator・unified judge・cascade・review_lock・retry loopは実コード)を再利用し、
最終slot NG(entity-like) -> `_resolve_unresolved_entity_for_review`(Stage 1) の分岐を X(crosslevel fallback)・Z(er063.run_tts_stage kp_en)で記録する。
research(Perplexity)は記録付きmock、出典ページ取得は記録付きmock(api0のため)。共有state・Ledgerは隔離(out dir配下のsnapshot)。Production file無編集。
使い方: .venv/Scripts/python.exe er097_pnps_stage1_runtime_evidence_01.py
"""
from __future__ import annotations

import json
import os
import socket
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
_argv = sys.argv[:]
sys.argv = [sys.argv[0], "api0"]
import er094_pnmh_runtime_evidence_01 as base  # noqa: E402  (harness再利用。importの副作用はchdir/環境変数のみ)
sys.argv = _argv
import er006_pronunciation_ledger_01 as ledger_mod  # noqa: E402

ORIG_UPSERT = ledger_mod.upsert            # apply_isolationがno-opへ差し替える前に保持(隔離snapshotへは実upsertする)
EV = "er097_output/pnps_stage1_wiring_01/runtime_api0"
LOG = {"research": [], "fetch": [], "lookups": []}
MODE = {"research": "FOUND"}


def research_mock(entities, *a, **k):
    surf = entities[0]["surface"]
    LOG["research"].append(surf)
    if MODE["research"] == "EMPTY":
        return {"status": "OK", "items": [], "citations": []}
    return {"status": "OK", "citations": ["https://example.test/ottoni"], "items": [{
        "surface": surf, "entity_type": "person", "canonical_spelling": "Ottoni", "language_origin": "Japanese-English",
        "expected_pronunciation_ipa": "/oʊˈtoʊni/", "pronunciation_hint": "oh-TOH-nee", "alternate_pronunciations": [],
        "confidence": "medium", "ambiguity_note": "api0 mock"}]}


def fetch_mock(url, timeout=5.0, max_bytes=0):
    LOG["fetch"].append(url)
    return "<html><body><p>Ottoni (oh-TOH-nee) is an Italian name.</p></body></html>"


def install():
    import er006_secondary_asr_01 as sec
    ledger_mod.upsert = ORIG_UPSERT
    sec.pronun_research.research_pronunciations = research_mock
    sec._pron_supply_fetch = fetch_mock
    socket.getaddrinfo = lambda host, *a, **k: [(2, 1, 6, "", ("93.184.216.34", 0))]   # is_safe_url用(実DNS 0)
    orig = sec.evaluate_attempt_with_cascade_detail

    def obs(canonical_text, asr_text, prior_results, wav_path, *a, **k):
        d = orig(canonical_text, asr_text, prior_results, wav_path, *a, **k)
        pl = d.get("pronunciation_lookups")
        if pl:
            LOG["lookups"].append({"wav": os.path.basename(str(wav_path)), "final_status": d.get("final_status"),
                                   "human_review_required": d.get("human_review_required"), "verified": d.get("verified"),
                                   "lookups": pl})
        return d
    sec.evaluate_attempt_with_cascade_detail = obs


SUF = {"v": ""}
T_BODY = "Ottoni and colleagues published a new study in Nature last week."
T_KP = "Make one yourself with Ottoni."
BAD_B = "A Tony and colleagues published a new study in Nature last week."
BAD_K = "Make one yourself with A Tony."


@base.scenario("X_ENTITY_NG_final_slot")
def x_ent(out):
    import er003_v1_crosslevel_audio_02_common as cl
    p = base._wav(out, "a2", "ent_body" + SUF["v"])
    return base.run_scn("X_ENTITY_NG_final_slot",
                        lambda: cl.generate_english_segment_with_fallback(T_BODY, p, "Ottoni and", max_extra_chars=30, tts_backend=base.FL),
                        [BAD_B] * 3, [BAD_B] * 3, "NOT_PASS", "X",
                        "er003_v1_crosslevel_audio_02_common.generate_english_segment_with_fallback (標準2回NG後 minimal fallback, force_secondary=True, 最終slot)")


@base.scenario("Z_ENTITY_NG_kp_en")
def z_ent(out):
    return base._z("Z_ENTITY_NG_kp_en", out, "kp_en", "a2", "kp9_en" + SUF["v"], T_KP, "KP_EN", "narrator", "Aoede", [BAD_K] * 4, [BAD_K] * 4, "NOT_PASS",
                   "er063.run_tts_stage kp_en -> _kp_en_two_stage -> repro01(最終slot NG)", rank=9 if not SUF['v'] else 8)


def run(name, phase):
    n_r, n_f, n_l = len(LOG["research"]), len(LOG["fetch"]), len(LOG["lookups"])
    rec = base.REGISTRY[name](EV)
    out = {"phase": phase, "scenario": name, "family": rec.get("family"), "entrypoint": rec.get("entrypoint"),
           "status": rec.get("status"), "exception": rec.get("exception"), "network_attempts": rec.get("network_attempts"),
           "research_calls": LOG["research"][n_r:], "fetch_calls": LOG["fetch"][n_f:], "lookups": LOG["lookups"][n_l:]}
    return out


def main():
    os.makedirs(EV, exist_ok=True)
    r77, before, iso = base.setup(EV)
    install()
    base.install_api0_stubs()
    # 隔離snapshotからbyus系の既存entryを除く(初回調査の再現。Production Ledgerは無編集)
    snap = iso["ledger_snapshot"]
    led = json.load(open(snap, encoding="utf-8"))
    led = {k: e for k, e in led.items() if "ottoni" not in e.get("surface", "").lower()}
    json.dump(led, open(snap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    sidecar = os.path.join(os.path.dirname(snap), "negative_cache.json")
    res = {"isolation": iso, "sidecar": sidecar, "runs": []}
    # Phase A: 調査成功 -> Ledger登録+出典ページ照合 -> 別Familyで同語はLedger命中(調査0)
    MODE["research"] = "FOUND"
    res["runs"].append(run("X_ENTITY_NG_final_slot", "A1_found_first_X"))
    res["runs"].append(run("Z_ENTITY_NG_kp_en", "A2_ledger_hit_Z"))
    # Phase B: 調査したが情報0件(items=[]) -> 否定記録 -> 別Familyで同語は調査0。Ledgerのbyus entryを除き初回調査を再現
    led = {k: e for k, e in json.load(open(snap, encoding="utf-8")).items() if "ottoni" not in e.get("surface", "").lower()}
    json.dump(led, open(snap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    for f in ("human_review_queue.jsonl", "attempt_history.jsonl"):
        p = os.path.join(EV, f)
        if os.path.exists(p):
            open(p, "w").close()
    MODE["research"] = "EMPTY"
    SUF["v"] = "_b"      # 別clip(Review Lockは同一clip/文で再生成を止めるため、Phase Bは別clip idで初回調査を再現)
    res["runs"].append(run("Z_ENTITY_NG_kp_en", "B1_empty_first_Z"))
    res["sidecar_after_B1"] = json.load(open(sidecar, encoding="utf-8")) if os.path.exists(sidecar) else None
    res["runs"].append(run("X_ENTITY_NG_final_slot", "B2_negative_hit_X"))
    res["network_attempts_total"] = len(base.STATE["net_attempts"])
    after = r77.snapshot_state()
    res["shared_state_unchanged"] = (before == after)
    json.dump(res, open(f"{EV}/runner_api0.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    for r in res["runs"]:
        print(r["phase"], r["scenario"], "status=", r["status"], "exc=", r["exception"], "research=", r["research_calls"], "fetch=", len(r["fetch_calls"]),
              "lookups=", [(k, v.get("lookup_action"), v.get("evidence_tier")) for x in r["lookups"] for k, v in x["lookups"].items()])
    print("shared_state_unchanged:", res["shared_state_unchanged"], "net:", res["network_attempts_total"])


if __name__ == "__main__":
    main()
