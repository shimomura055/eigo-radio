# -*- coding: utf-8 -*-
"""PNAP 委任_02: 配線後のON/OFF差分(API 0、Stage 1配線時と同じ手法の再利用)。
保存4,032ペア(PNMH-PLAN-01 pairs_02.jsonl)+HR queue(79行相当)を、adapter(evaluate_attempt_with_cascade_detail)へ
Primary転写=保存ASR転写、Secondary=mock(同じ転写)で通し、次の構成で出力を比較する:
  OFF   : flag OFF・scope無し(従来)
  ON_NS : flag ON・scope無し(Family A/B/C・単体呼出相当)           -> OFFと完全一致(差分0)が期待
  ON_KP : flag ON・scope X・dual_required=True(KP英語phrase)         -> OFFと完全一致(差分0)が期待
  ON_JA : flag ON・scope X・日本語text(language=ja-JP)               -> OFFと完全一致(差分0)が期待
  ON_X  : flag ON・scope X・segment_id=full_story_part1(英語本文)    -> NG->ALARM受理のみが差分。全flipが固有名詞のみ不一致であること
Stage 1調査(Perplexity)・HR queue書込・Azureは全てmock/spy(API 0・実ファイル書込0)。"""
import json
import os
import sys
import time
import wave

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
import er006_secondary_asr_01 as sec
import er006_asr_provider_routing_01 as routing
import er103_proper_noun_alarm_policy_01 as pol

HERE = os.path.dirname(os.path.abspath(__file__))
PAIRS = os.path.join(ROOT, "docs", "research", "PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01", "pairs_02.jsonl")
WAV = os.path.join(os.environ.get("TMP", "."), "pnap_diff_silence.wav")
with wave.open(WAV, "wb") as w:
    w.setnchannels(1); w.setsampwidth(1); w.setframerate(8000); w.writeframes(b"\x00" * 8000)

lookups, hr_logged = [], []
sec._resolve_unresolved_entity_for_review = lambda span: lookups.append(span) or {"pronunciation_hint": "", "confidence": "unconfirmed", "sources": []}
sec._log_human_review = lambda d: hr_logged.append(d)
routing.transcribe = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("Primary#2 forbidden"))

import re
_JA = re.compile(r"[぀-ヿ㐀-䶿一-鿿]")


def call(canon, asr, *, segment_id, dual=False, ja=False, slot=1, last=True):
    sec.get_full_text_via_azure_stt_with_phrase_list = lambda wav, language="en-US", phrases=None, **kw: (asr, None)
    sec.reset_secondary_cache()
    ctx = {"slot": slot, "is_last_slot": last}
    if dual:
        ctx["dual_required"] = True
    d = sec.evaluate_attempt_with_cascade_detail(canon, asr, [], WAV, language=("ja-JP" if ja else "en-US"), cascade_enabled=True,
                                                 segment_id=segment_id, attempt_ctx=ctx)
    c = d["classification"]
    return {"verified": bool(d["verified"]), "stop": bool(d["stop_retrying"]), "cls": c.classification, "hr": bool(d.get("human_review_required")),
            "state": (d.get("asr_judgement") or {}).get("state"), "tech": bool(d.get("technical_stop"))}


def sig(r):
    return (r["verified"], r["stop"], r["cls"], r["hr"], r["state"], r["tech"])


pairs = [json.loads(l) for l in open(PAIRS, encoding="utf-8") if l.strip()]
out = {"pairs": len(pairs), "on_ns_diff": 0, "on_kp_diff": 0, "on_ja_diff": 0, "on_x_flips": [], "errors": 0, "examples_diff": []}
t0 = time.time()
n_en = n_ja = 0
for i, p in enumerate(pairs):
    canon, asr = p["canonical"], p["asr"]
    ja = bool(_JA.search(canon))
    seg = "japanese_title" if ja else "full_story_part1"
    try:
        pol.PROPER_NOUN_ALARM_POLICY_ENABLED = False
        pol._RUN_SCOPE = None
        off = call(canon, asr, segment_id=seg, ja=ja)
        pol.PROPER_NOUN_ALARM_POLICY_ENABLED = True
        ns = call(canon, asr, segment_id=seg, ja=ja)
        if sig(ns) != sig(off):
            out["on_ns_diff"] += 1
            out["examples_diff"].append(("ON_NS", i, canon[:60], off, ns))
        if ja:
            n_ja += 1
            with pol.run_scope("X"):
                r = call(canon, asr, segment_id=seg, ja=True)
            if sig(r) != sig(off):
                out["on_ja_diff"] += 1
                out["examples_diff"].append(("ON_JA", i, canon[:60], off, r))
        else:
            n_en += 1
            with pol.run_scope("X"):
                kp = call(canon, asr, segment_id="kp1_en", dual=True)
            pol.PROPER_NOUN_ALARM_POLICY_ENABLED = False
            kp_off = call(canon, asr, segment_id="kp1_en", dual=True)
            if sig(kp) != sig(kp_off):
                out["on_kp_diff"] += 1
                out["examples_diff"].append(("ON_KP", i, canon[:60], kp_off, kp))
            pol.PROPER_NOUN_ALARM_POLICY_ENABLED = True
            with pol.run_scope("X"):
                x = call(canon, asr, segment_id=seg)
            if sig(x) != sig(off):
                out["on_x_flips"].append({"i": i, "canon": canon[:90], "asr": asr[:90], "off": off, "on": x})
    except Exception as exc:  # noqa: BLE001
        out["errors"] += 1
        out.setdefault("error_samples", []).append((i, f"{type(exc).__name__}: {exc}"))
    finally:
        pol.PROPER_NOUN_ALARM_POLICY_ENABLED = True
        pol._RUN_SCOPE = None
    if i % 500 == 0:
        print(i, round(time.time() - t0), "s", flush=True)
out["en_pairs"], out["ja_pairs"] = n_en, n_ja
out["on_x_flip_count"] = len(out["on_x_flips"])
out["on_x_flip_kinds"] = {}
for f in out["on_x_flips"]:
    k = f"{f['off']['cls']}/hr={f['off']['hr']}->{f['on']['cls']}/state={f['on']['state']}"
    out["on_x_flip_kinds"][k] = out["on_x_flip_kinds"].get(k, 0) + 1
out["hr_queue_writes_by_spy"] = len(hr_logged)
out["stage1_lookup_calls_total"] = len(lookups)
out["elapsed_s"] = round(time.time() - t0)
json.dump(out, open(os.path.join(HERE, "onoff_differential_02_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print(json.dumps({k: v for k, v in out.items() if k not in ("on_x_flips", "examples_diff")}, ensure_ascii=False, indent=1, default=str))
