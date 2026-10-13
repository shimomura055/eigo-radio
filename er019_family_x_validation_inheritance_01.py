# -*- coding: utf-8 -*-
"""FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 是正②: 再利用segmentの「検証済み状態」の証拠つき引継ぎ(API呼出なし)。

背景(OPEN-346②): `--only-segments`のtts実行が非選択segmentのresults entryを`SKIPPED_NOT_SELECTED`で上書きする、
また他runから音声wavだけをseed(copy)したsegmentにはAdv側のresults entry自体が無い、の2点により、元の正式Validation
(ASR検証OK)が済んだsegmentでもAudio Validation Gateが`UNVALIDATED`としてassemblyをBLOCKしていた。

方針(Gateは無変更・緩和しない): 次の証拠がすべて揃うsegmentに限り、元の検証済みentryを(status=OK、元のASR/QA証拠を保持
したまま)引き継ぎ、`validation_inheritance`(label=REUSED_VALIDATED、元記録へのポインタ・sha256)を付与する。
  1. 元entryが status=="OK" かつ asr_verified is True (元の正式Validation結果)
  2. 現在のwavが存在し、wavのsha256が同一性の証拠と一致する:
       (a) 元entryが`sha256`を持つ場合: 現在のwav sha256 == entry.sha256
       (b) 持たない場合: 呼び出し側が渡すwitness(seed provenanceに記録されたcopy時sha256 かつ 元runに残る元wavの
           現在sha256)の両方が現在のwav sha256と一致
     どちらも無ければ引継ぎしない(NO_IDENTITY_EVIDENCE、fail-closed)。
  3. expected_textが渡された場合、元entryのcanonical_textが完全一致(古い文面の音声を引き継がない)。
証拠が揃わないsegmentは従来どおりUNVALIDATEDのまま(Gate BLOCK維持)。
引き継いだentryには現在のwav sha256を`sha256`として記録するため、Gateの`ASSET_HASH_MISMATCH`(stale検知)も有効になる。
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import shutil
import time
from typing import Optional

REUSED_VALIDATED = "REUSED_VALIDATED"


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def entry_fingerprint(entry: dict) -> str:
    return hashlib.sha256(json.dumps(entry, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def evaluate_inheritance(entry: Optional[dict], wav_path: str, expected_text: Optional[str] = None,
                         witness_sha256s: Optional[list] = None) -> dict:
    """戻り値: {ok, reason, current_sha256, evidence}。reasonは不許可理由(ok時は"OK")。"""
    if not isinstance(entry, dict):
        return {"ok": False, "reason": "NO_SOURCE_ENTRY", "current_sha256": None, "evidence": None}
    if entry.get("status") != "OK":
        return {"ok": False, "reason": f"SOURCE_STATUS_NOT_OK({entry.get('status')})", "current_sha256": None, "evidence": None}
    if entry.get("asr_verified") is not True:
        return {"ok": False, "reason": "SOURCE_ASR_NOT_VERIFIED", "current_sha256": None, "evidence": None}
    if not wav_path or not os.path.exists(wav_path):
        return {"ok": False, "reason": "WAV_MISSING", "current_sha256": None, "evidence": None}
    current = sha256_file(wav_path)
    if expected_text is not None and entry.get("canonical_text") != expected_text:
        return {"ok": False, "reason": "CANONICAL_TEXT_MISMATCH", "current_sha256": current, "evidence": None}
    recorded = entry.get("sha256")
    if recorded:
        if recorded != current:
            return {"ok": False, "reason": "ENTRY_SHA256_MISMATCH", "current_sha256": current, "evidence": None}
        return {"ok": True, "reason": "OK", "current_sha256": current, "evidence": "entry_sha256"}
    if witness_sha256s:
        if all(w == current for w in witness_sha256s):
            return {"ok": True, "reason": "OK", "current_sha256": current,
                    "evidence": "seed_provenance_and_source_wav_sha256"}
        return {"ok": False, "reason": "WITNESS_SHA256_MISMATCH", "current_sha256": current, "evidence": None}
    return {"ok": False, "reason": "NO_IDENTITY_EVIDENCE", "current_sha256": current, "evidence": None}


def build_inherited_entry(entry: dict, wav_path: str, evaluation: dict, source_ref: dict) -> dict:
    """元entryを深いcopyし、status=OKと元の検証証拠を保ったまま、現在wavのpath/sha256と引継ぎ記録を付ける。
    style_profile等の元の記録は書き換えない(呼び出し側で現行profileを上書き付与しない)。"""
    new_entry = copy.deepcopy(entry)
    new_entry["path"] = wav_path
    new_entry["sha256"] = evaluation["current_sha256"]
    new_entry["reused_from_previous_run"] = True
    new_entry["validation_inheritance"] = {
        "label": REUSED_VALIDATED,
        "evidence": evaluation["evidence"],
        "wav_sha256": evaluation["current_sha256"],
        "source_entry_fingerprint_sha256": entry_fingerprint(entry),
        "source_ref": source_ref,
        "inherited_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    return new_entry


def try_inherit_from_cached(cached_entry: Optional[dict], wav_path: str, expected_text: Optional[str],
                            cached_style_version: Optional[str], current_style_version: str,
                            source_ref: dict) -> Optional[dict]:
    """runner(`--only-segments`で非選択のsegment)用: 同一out_dirの前回results entryを、上記証拠が揃う場合に限り
    引き継ぐ。style_version不一致の旧cacheは通常のreuseと同様に引き継がない。引き継げなければNone。"""
    if cached_style_version != current_style_version:
        return None
    ev = evaluate_inheritance(cached_entry, wav_path, expected_text=expected_text)
    if not ev["ok"] or ev["evidence"] != "entry_sha256":
        return None  # 同一out_dir内の引継ぎはentry自身のsha256を必須とする(witnessなしでは同一性を証明できない)
    return build_inherited_entry(cached_entry, wav_path, ev, source_ref)


# ------------------------------------------------------------
# 別run由来のseed segment(音声wavだけをcopyし、results entryが無い)用の再構築(明示CLI、既定dry-run)
# ------------------------------------------------------------
def rebuild_state(level_dir: str, source_results_path: str, source_root: str, provenance_path: str,
                  labels: list, expected_texts: Optional[dict] = None) -> dict:
    """level_dir=<theme>/<level>(例 .../b1b)。source_results_path=元runのaudit/tts_generation_results.json。
    source_root=元runの相対pathを解決するroot。provenance_path=seed provenance(roles[label].sha256=copy時sha256)。
    現在のresults(level_dir/audit/tts_generation_results.json)は変更しない。戻り値=判定結果(merged_segments案を含む)。"""
    cur_path = f"{level_dir}/audit/tts_generation_results.json"
    cur = json.load(open(cur_path, encoding="utf-8")) if os.path.exists(cur_path) else {"segments": {}}
    src = json.load(open(source_results_path, encoding="utf-8"))
    prov = json.load(open(provenance_path, encoding="utf-8"))
    roles = prov.get("roles") or {}
    report = {"level_dir": level_dir, "source_results_path": source_results_path, "provenance_path": provenance_path,
              "labels": {}, "merged_segments": {}}
    for label in labels:
        wav = f"{level_dir}/narration/{label}.wav"
        existing = (cur.get("segments") or {}).get(label)
        if existing and existing.get("status") not in (None, "SKIPPED_NOT_SELECTED"):
            report["labels"][label] = {"ok": False,
                                       "reason": f"EXISTING_ENTRY_PRESENT({existing.get('status')})_NOT_OVERWRITTEN"}
            continue
        src_entry = (src.get("segments") or {}).get(label)
        witnesses, notes = [], {}
        role = roles.get(label)
        if role and role.get("sha256"):
            witnesses.append(role["sha256"])
            notes["seed_provenance_sha256"] = role["sha256"]
            notes["seed_src"] = role.get("src")
        else:
            notes["seed_provenance_sha256"] = None
            witnesses.append("NO_SEED_PROVENANCE")
        src_wav = None
        if isinstance(src_entry, dict) and src_entry.get("path"):
            src_wav = (src_entry["path"] if os.path.isabs(src_entry["path"])
                       else os.path.join(source_root, src_entry["path"]))
        if src_wav and os.path.exists(src_wav):
            notes["source_wav_current_sha256"] = sha256_file(src_wav)
            witnesses.append(notes["source_wav_current_sha256"])
        else:
            notes["source_wav_current_sha256"] = None
            witnesses.append("SOURCE_WAV_MISSING")
        ev = evaluate_inheritance(src_entry, wav, expected_text=(expected_texts or {}).get(label),
                                  witness_sha256s=witnesses)
        rec = {"ok": ev["ok"], "reason": ev["reason"], "current_wav_sha256": ev["current_sha256"], **notes,
               "source_style_version": src.get("style_version"),
               "current_style_version_in_results": cur.get("style_version")}
        report["labels"][label] = rec
        if ev["ok"]:
            report["merged_segments"][label] = build_inherited_entry(
                src_entry, wav, ev, {"kind": "other_run_results_with_seed_provenance",
                                      "source_results_path": source_results_path,
                                      "provenance_path": provenance_path})
    report["inherited"] = sorted(report["merged_segments"])
    report["not_inherited"] = sorted(l for l, r in report["labels"].items() if not r["ok"])
    return report


def apply_state(level_dir: str, report: dict) -> str:
    """rebuild_stateの結果(inheritedのみ)を、level_dir/audit/tts_generation_results.jsonへ書き込む。
    実行前に元のresultsを同ディレクトリへ`.pre_inherit_<ts>.json`としてcopy保全する。非OK entryは上書きしない
    (rebuild_stateが既存OK/STOPPED等を除外済み)。戻り値=バックアップpath。"""
    path = f"{level_dir}/audit/tts_generation_results.json"
    cur = json.load(open(path, encoding="utf-8"))
    backup = f"{level_dir}/audit/tts_generation_results.pre_inherit_{time.strftime('%Y%m%dT%H%M%S')}.json"
    shutil.copyfile(path, backup)
    for label, entry in report["merged_segments"].items():
        existing = cur["segments"].get(label)
        assert not existing or existing.get("status") in (None, "SKIPPED_NOT_SELECTED"), label
        cur["segments"][label] = entry
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cur, f, ensure_ascii=False, indent=2)
    return backup


def main():
    ap = argparse.ArgumentParser(description="seed segmentの検証済み状態の証拠つき引継ぎ(既定dry-run: 新規ファイルへ出力のみ)")
    ap.add_argument("--level-dir", required=True)
    ap.add_argument("--source-results", required=True)
    ap.add_argument("--source-root", required=True)
    ap.add_argument("--provenance", required=True)
    ap.add_argument("--labels", required=True, help="カンマ区切り")
    ap.add_argument("--expected-texts-json", default=None, help="label->期待canonical_textのjson")
    ap.add_argument("--output", required=True, help="判定結果の出力先(新規ファイル。既存なら中止)")
    ap.add_argument("--apply", action="store_true", help="resultsへ実際に書込む(バックアップ後)。既定はdry-run")
    a = ap.parse_args()
    if os.path.exists(a.output):
        raise SystemExit(f"出力先が既に存在します(上書き禁止): {a.output}")
    exp = json.load(open(a.expected_texts_json, encoding="utf-8")) if a.expected_texts_json else None
    rep = rebuild_state(a.level_dir, a.source_results, a.source_root, a.provenance,
                        [x.strip() for x in a.labels.split(",") if x.strip()], exp)
    if a.apply:
        rep["applied_backup"] = apply_state(a.level_dir, rep)
    os.makedirs(os.path.dirname(a.output) or ".", exist_ok=True)
    with open(a.output, "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=2)
    print(json.dumps({"inherited": rep["inherited"], "not_inherited": rep["not_inherited"],
                      "reasons": {l: r["reason"] for l, r in rep["labels"].items()}}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
