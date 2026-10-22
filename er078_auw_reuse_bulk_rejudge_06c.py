# AUW 委任_06c (c): Master Audio Store manifest と既存結果cache(tts_generation_results*.json / *.ok.meta.json)を
# **offline(API 0)**で一括再判定し、値ガードDIFF/否定差(再利用禁止対象)を数える。
# 使い方: python er078_auw_reuse_bulk_rejudge_06c.py --out <json> [--apply-marks]
#   既定は読取のみ。--apply-marks指定時のみ、DIFF該当資産のMaster manifest entryへ `reuse_blocked` markを付与する(削除しない)。
# 【運用注記 OF-KPQ-P-03/09、2026-10-22】KP英語(key_phrase_english_component・kp<N>_english・kp<N>_en)は2026-10-22以降数値・否定の保護を解除済み(vote gateが再判定)。
#   本scriptはKP英語entryにも旧保護で`--apply-marks`し得る(KPのS+W合格行等へ`reuse_blocked`が付き再生成になる)。KP英語entryを対象に
#   --apply-marksを使わない(集計のみ=既定は無害)。KP英語の再利用可否は kp_vote_reuse_ok が決める。
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er078_reuse_value_guard_01 as rvg  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))
MANIFEST = "er006_output/master_audio_store_01/manifest.json"
RESULT_NAMES = ("tts_generation_results.json", "tts_generation_results_B.json")


def iter_files():
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in (".git", ".venv", "node_modules", "__pycache__")]
        for f in fn:
            if f in RESULT_NAMES or f.endswith(".ok.meta.json"):
                yield os.path.join(dp, f)


def find_entries(node, path=""):
    """JSONを再帰し、転写(asr_text か asr_judgement)とtext/canonical_textを持つstatus OK系のdictを列挙する。"""
    if isinstance(node, dict):
        has_t = node.get("text") or node.get("canonical_text")
        has_a = node.get("asr_text") or node.get("asr_judgement") or node.get("asr_judgement_inherited")
        if has_t and has_a and node.get("status", "OK") in ("OK", "REUSED_EXISTING_FILE"):
            yield path, node
        for k, v in node.items():
            if isinstance(v, (dict, list)):
                yield from find_entries(v, f"{path}/{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            if isinstance(v, (dict, list)):
                yield from find_entries(v, f"{path}[{i}]")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--apply-marks", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    t0 = time.time()
    rep = {"started": time.strftime("%Y-%m-%dT%H:%M:%S"), "api_calls": 0, "files_scanned": 0, "entries_total": 0,
           "judgeable": 0, "not_judgeable": 0, "rejudge_ok": 0, "rejudge_ng_not_protected": 0, "rejudge_error": 0,
           "diff_count": 0, "diff_entries": [], "master": {}, "by_reason": {}}
    seen = set()
    texts_by_hash = {}
    n = 0
    for fp in iter_files():
        rel = os.path.relpath(fp, ROOT).replace("\\", "/")
        try:
            data = json.load(open(fp, encoding="utf-8"))
        except Exception:
            continue
        rep["files_scanned"] += 1
        if fp.endswith(".ok.meta.json"):
            continue  # canonical textを持たないため単独では判定不能(Master/results側で網羅。meta側は件数のみ)
        for p, e in find_entries(data):
            txt = e.get("text") or e.get("canonical_text")
            for t in (e.get("text"), e.get("canonical_text")):
                if t:
                    texts_by_hash[hashlib.sha256(t.encode("utf-8")).hexdigest()[:16]] = t
            key = (e.get("sha256"), txt, e.get("asr_text"))
            if key in seen:
                continue
            seen.add(key)
            rep["entries_total"] += 1
            n += 1
            if a.limit and n > a.limit:
                break
            g = rvg.guard_entry(e, label=p.rsplit("/", 1)[-1])
            rs = g["reason"].split(":")[0]
            rep["by_reason"][rs] = rep["by_reason"].get(rs, 0) + 1
            if not g["applicable"]:
                rep["not_judgeable"] += 1
                if g["reason"].startswith("REJUDGE_ERROR"):
                    rep["rejudge_error"] += 1
                continue
            rep["judgeable"] += 1
            if g["blocked"]:
                rep["diff_count"] += 1
                rep["diff_entries"].append({"file": rel, "path": p, "canonical_text": txt, "asr_text": e.get("asr_text"),
                                            "sha256": e.get("sha256"), "reason": g["reason"], "unified_state": g["unified_state"]})
            elif g["reason"] == "REJUDGE_OK":
                rep["rejudge_ok"] += 1
            else:
                rep["rejudge_ng_not_protected"] += 1
    # Master manifest (canonical textはhashからresults側のtextで復元。復元不能は判定不能)
    man = json.load(open(os.path.join(ROOT, MANIFEST), encoding="utf-8"))
    ms = {"entries": len(man), "with_asr_text": 0, "text_recovered": 0, "judgeable": 0, "ok": 0, "ng_not_protected": 0,
          "diff": 0, "diff_ids": [], "not_judgeable_no_text": 0}
    for mid, ent in man.items():
        qa = ent.get("qa_evidence") or {}
        if not qa.get("asr_text"):
            continue
        ms["with_asr_text"] += 1
        text = texts_by_hash.get((ent.get("key") or {}).get("canonical_text_hash"))
        if not text:
            ms["not_judgeable_no_text"] += 1
            continue
        ms["text_recovered"] += 1
        probe = dict(qa)
        probe["asr_judgement"] = ent.get("asr_judgement")
        probe["reuse_blocked"] = ent.get("reuse_blocked")
        g = rvg.guard_entry(probe, label="master:" + (ent.get("key") or {}).get("style_instruction_id", ""), canonical_text=text)
        if not g["applicable"]:
            continue
        ms["judgeable"] += 1
        if g["blocked"] and g["reason"] != "REUSE_BLOCKED_MARK":
            ms["diff"] += 1
            ms["diff_ids"].append({"master_audio_id": mid, "canonical_text": text, "asr_text": qa.get("asr_text"), "reason": g["reason"]})
        elif g["reason"] == "REJUDGE_OK":
            ms["ok"] += 1
        else:
            ms["ng_not_protected"] += 1
    rep["master"] = ms
    rep["diff_count_total"] = rep["diff_count"] + ms["diff"]
    if a.apply_marks and ms["diff_ids"]:
        stamp = time.strftime("%Y-%m-%dT%H:%M:%S")
        for d in ms["diff_ids"]:
            man[d["master_audio_id"]]["reuse_blocked"] = {"reason": d["reason"], "marked_at": stamp, "by": "AUW_06c_bulk_rejudge"}
        json.dump(man, open(os.path.join(ROOT, MANIFEST), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        rep["marks_applied"] = len(ms["diff_ids"])
    rep["elapsed_seconds"] = round(time.time() - t0, 1)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(rep, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in rep.items() if k not in ("diff_entries",)}, ensure_ascii=False)[:3000])


if __name__ == "__main__":
    main()
