# -*- coding: utf-8 -*-
"""ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 PN 委任_04 (W-02): `er103.evaluate_alarm_eligibility` のbaseline署名(RET実装**前**の現行出力)を凍結する。

署名の入力は「evaluate_alarm_eligibility への入力」(cls diffs直列化: classification+content_word_diffs、texts、role、p3_entry、Ledger語集合)に固定する
(上流の判定器[val.classify_asr_match]を再計算しない=②UKUS等の上流変更で署名が動かないようにする、Opus W-02)。
コーパス: D1=HR queue(Ledger現行/全除外の2モード)・D2=保存EN pair(pairs_02)・fixture=既存er103 test実行中の呼出を記録。
`freeze()` はRET実装前に1回だけ実行して `er103_ret_baseline_signature_v1.json` を作る。以後は `recompute(entity_table=...)` で再計算比較する。"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from types import SimpleNamespace

ROOT = os.path.dirname(os.path.abspath(__file__))
SIG_PATH = os.path.join(ROOT, "er103_ret_baseline_signature_v1.json")
HR_QUEUE = os.path.join(ROOT, "er006_output", "audio_retry_cascade_prod_01", "human_review_queue.jsonl")
LEDGER_JSON = os.path.join(ROOT, "er006_output", "pronunciation_ledger_01", "ledger.json")
PAIRS = os.path.join(ROOT, "docs", "research", "PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01", "pairs_02.jsonl")
_JA = re.compile(r"[぀-ヿ㐀-䶿一-鿿]")


def _diffs(cls):
    return [dict(d) for d in (cls.protected.content_word_diffs or [])]


def record_from_kwargs(kw: dict):
    for k in ("cmu_has", "zipf", "max_asr_per_canon", "min_similarity", "max_secondary_noise"):
        if k in kw:
            return None                          # 既定以外の注入を伴う呼出は凍結対象外
    pc, sc = kw.get("primary_cls"), kw.get("secondary_cls")
    return {"canonical_text": kw.get("canonical_text"), "p_class": getattr(pc, "classification", None) if pc is not None else None,
            "p_diffs": _diffs(pc) if pc is not None else None, "s_class": getattr(sc, "classification", None) if sc is not None else None,
            "s_diffs": _diffs(sc) if sc is not None else None, "primary_text": kw.get("primary_text"), "secondary_text": kw.get("secondary_text"),
            "judge_state": kw.get("judge_state"), "judge_reason_code": kw.get("judge_reason_code"), "role": kw.get("role"),
            "lang": kw.get("lang", "en"), "vote_required": bool(kw.get("vote_required", False)), "p3_entry": kw.get("p3_entry"),
            "supply_map": kw.get("supply_map"), "ledger": sorted(kw.get("ledger_surfaces") or []), "max_diffs": kw.get("max_diffs")}


def kwargs_from_record(r: dict) -> dict:
    def mk(c, d):
        return None if c is None and d is None else SimpleNamespace(classification=c, protected=SimpleNamespace(content_word_diffs=d))
    kw = dict(canonical_text=r["canonical_text"], primary_cls=mk(r["p_class"], r["p_diffs"]), secondary_cls=mk(r["s_class"], r["s_diffs"]),
              primary_text=r["primary_text"], secondary_text=r["secondary_text"], judge_state=r["judge_state"],
              judge_reason_code=r["judge_reason_code"], role=r["role"], lang=r["lang"], vote_required=r["vote_required"],
              p3_entry=r["p3_entry"], supply_map=r["supply_map"], ledger_surfaces=frozenset(r["ledger"]), enabled=True)
    if r.get("max_diffs") is not None:
        kw["max_diffs"] = r["max_diffs"]
    return kw


def decision_signature(d) -> str:
    diffs = [[x.canonical, x.asr_primary, x.asr_secondary, x.evidence, x.similarity_primary, x.similarity_secondary] for x in d.diffs]
    det = json.dumps(d.detail, sort_keys=True, default=str, ensure_ascii=False)
    return hashlib.sha256(json.dumps([d.accept, d.reason, diffs, det], ensure_ascii=False, default=str).encode("utf-8")).hexdigest()


def _ledger_tokens(exclude: bool) -> list:
    if exclude:
        return []
    import er103_proper_noun_alarm_policy_01 as pol
    L = json.load(open(LEDGER_JSON, encoding="utf-8"))
    s = set()
    for e in L.values():
        if e.get("ledger_disabled") or e.get("entity_type") == "ja_reading_katakana":
            continue
        for t in pol._fold(e["surface"]).split():
            s.add(t.strip("'"))
    return sorted(s)


def build_corpus() -> list:
    import er006_preprod_hardening_01_validation as val
    import er020_tts_retry_local_rewrite_01 as rw
    out = []
    led_cur, led_ex = _ledger_tokens(False), _ledger_tokens(True)
    rows = [json.loads(l) for l in open(HR_QUEUE, encoding="utf-8") if l.strip()]
    for i, r in enumerate(rows):
        wp = r.get("wav_path", "").replace("\\", "/")
        if ("er026_pscr_outer" in wp) or ("/Temp/" in wp) or wp.startswith("C:"):
            continue
        steps = r.get("steps") or []
        prim = next((s for s in steps if s.get("step") == "primary_1"), None)
        sec = [s for s in steps if s.get("provider") == "azure" and s.get("text")]
        if not prim or prim.get("text") is None:
            continue
        canon = r["canonical_text"]
        sec_text = sec[-1]["text"] if sec else None
        cp = val.classify_asr_match(canon, prim["text"])
        cs = val.classify_asr_match(canon, sec_text) if sec_text else None
        try:
            role = rw.resolve_narrative_role(r.get("segment_id")) if r.get("segment_id") else "FULL_STORY"
        except Exception:
            role = "FULL_STORY"
        for tag, led in (("d1_cur", led_cur), ("d1_excl", led_ex)):
            out.append(dict(group=tag, record=record_from_kwargs(dict(
                canonical_text=canon, primary_cls=cp, secondary_cls=cs, primary_text=prim["text"], secondary_text=sec_text,
                judge_state="NG_BOTH", judge_reason_code="secondary_not_accepted", role=role or "FULL_STORY",
                p3_entry=("p3_primary_ng" if not cp.should_pass else "force_secondary"), ledger_surfaces=frozenset(led)))))
    for l in open(PAIRS, encoding="utf-8"):
        if not l.strip():
            continue
        p = json.loads(l)
        canon, asr = p["canonical"], p["asr"]
        if _JA.search(canon):
            continue
        cp = val.classify_asr_match(canon, asr)
        if cp.should_pass:
            continue
        out.append(dict(group="d2", record=record_from_kwargs(dict(
            canonical_text=canon, primary_cls=cp, secondary_cls=cp, primary_text=asr, secondary_text=asr, judge_state="NG_BOTH",
            judge_reason_code="secondary_not_accepted", role="FULL_STORY", p3_entry="p3_primary_ng", ledger_surfaces=frozenset(led_cur)))))
    return out


def record_fixtures() -> list:
    """既存er103系testの `evaluate_alarm_eligibility` 呼出を記録して凍結する(fixture)。"""
    import io
    import unittest
    import er103_proper_noun_alarm_policy_01 as pol
    seen, recs = set(), []
    orig = pol.evaluate_alarm_eligibility

    def rec(*a, **kw):
        r = record_from_kwargs(kw)
        if r is not None:
            k = hashlib.sha256(json.dumps(r, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()
            if k not in seen:
                seen.add(k)
                recs.append(dict(group="fixture", record=r))
        return orig(*a, **kw)
    pol.evaluate_alarm_eligibility = rec
    try:
        for modname in ("er103_proper_noun_alarm_policy_test_01", "er103_pnap_wiring_test_01"):
            suite = unittest.defaultTestLoader.loadTestsFromName(modname)
            unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
    finally:
        pol.evaluate_alarm_eligibility = orig
    return recs


def freeze() -> dict:
    import er103_proper_noun_alarm_policy_01 as pol
    items = [i for i in build_corpus() if i["record"] is not None] + record_fixtures()
    sigs = []
    for it in items:
        d = pol.evaluate_alarm_eligibility(**kwargs_from_record(it["record"]))
        sigs.append(decision_signature(d))
    body = {"schema": "er103_ret_baseline_v1", "n": len(items),
            "groups": {g: sum(1 for i in items if i["group"] == g) for g in sorted({i["group"] for i in items})},
            "items": items, "signatures": sigs, "total_sha256": hashlib.sha256("".join(sigs).encode()).hexdigest()}
    with open(SIG_PATH, "w", encoding="utf-8") as f:
        json.dump(body, f, ensure_ascii=False, sort_keys=True)
    return {k: body[k] for k in ("n", "groups", "total_sha256")}


def load() -> dict:
    with open(SIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def recompute(entity_table=None, extra_kw=None) -> list:
    """凍結入力を現行の evaluate_alarm_eligibility に通した(decision, signature)の列。entity_table=Noneのとき引数自体を渡さない。"""
    import er103_proper_noun_alarm_policy_01 as pol
    body = load()
    out = []
    for it in body["items"]:
        kw = kwargs_from_record(it["record"])
        if entity_table is not None:
            kw["entity_table"] = entity_table
        kw.update(extra_kw or {})
        d = pol.evaluate_alarm_eligibility(**kw)
        out.append((d, decision_signature(d)))
    return out


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "freeze":
        if os.path.exists(SIG_PATH):
            sys.exit("baseline already frozen: " + SIG_PATH)
        print(json.dumps(freeze(), ensure_ascii=False))
    else:
        b = load()
        got = [s for _, s in recompute()]
        print("match" if got == b["signatures"] else "MISMATCH", b["n"])
