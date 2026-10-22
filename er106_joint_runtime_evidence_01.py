# -*- coding: utf-8 -*-
"""er106_joint_runtime_evidence_01.py: 合同runtime evidence(PNAP + KP3V + KPFT)の read-only 集計script。

管理ID: JOINT-RUNTIME-EVIDENCE-PREP-01 委任_01(2026-10-22)。OPEN-450(PNAP)/OPEN-451(KP3V)/OPEN-454(KPFT)の横断準備。
目的: 2026-10-23 JSTに実施する「Family X 1 run + Family Z 1 run」の出力dirを読み、3件の発火証拠を1回で集計する。

厳守事項:
- read-only。API呼出0・音声生成0。Production .py(er019/er026/er063/er006/er003/er103/er104/er105 等)はimportもeditもしない
  (test `NoProductionImportTest`がASTで固定)。読むのはrun dirのJSON/JSONL/wav(headerのみ)/HTMLとshared logのみ。
  例外として import するのは (1) docs/pm/tools/daily_dev_cost_01.py(費用換算のPM共通tool、ファイルパス指定load) と
  (2) er_user_listening_page_common_01.py(試聴ページ標準適合checkの純関数module)。どちらもAPI 0。
- 実装側のfield名は10-23の配線結果で変わり得る。期待キーは下の定数に集約し、存在しないキーは推測で補完せず MISSING として報告する。
  10-23当日に実装結果で差し替える箇所は `EXPECTED_*` 定数のみ(各定数の出典=設計書節をコメントに記載)。

使い方:
  # 実行前(snapshot採取。共有HR queue/attempt_history/Ledger/STOP/Lockの前状態)
  .venv\\Scripts\\python.exe er106_joint_runtime_evidence_01.py --snapshot-out <pre.json> --x-run-dir <X> --z-run-dir <Z>
  # 実行後(集計。--snapshot-in で前後差分)
  .venv\\Scripts\\python.exe er106_joint_runtime_evidence_01.py --x-run-dir <X> --z-run-dir <Z> --snapshot-in <pre.json> \\
      --x-source-dir er019_output/<slug>/<run> --out-json <out.json> --out-md <out.md>
"""
from __future__ import annotations

import argparse
import datetime
import glob
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import wave

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
SCHEMA = "er106_joint_runtime_evidence_01/v1"

# ============================================================
# 期待キー(設計書から取った値。10-23に実装結果で差し替える箇所はここだけ)
# ============================================================
# --- KPFT(IMPLEMENTATION_DESIGN_01 KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01 §2, §6, er105 run_fulltext_selection が書くmetadata) ---
KPFT_BACKEND_ID = "fulltext_p2"                      # 設計§2 BACKEND_ID
KPFT_MODEL_ID = "gpt-6-luna"                         # 設計§2 SELECTION_MODEL_ID
KPFT_PROMPT_2_SHA256 = "a12896f485604f32efd52cb159d2615733c0eca262725af78db0b4f1c9a3dc9a"   # 設計§2(testで固定されたsha)
KPFT_KP_COUNT_MAX = 3                                # 設計§2 KP_COUNT_MAX
KPFT_WORDS_MAX = 5                                   # 設計§2 KP_WORDS_MAX
KPFT_SELECTION_MAX_ATTEMPTS = 2                      # 設計§5-1
KPFT_CANON_MAX_ATTEMPTS = 2                          # 設計§5-1(既存MAX_CANONICALIZATION_RETRY_ATTEMPTS)
KPFT_OUTER_RETRY_MAX = 3                             # 設計§5-1(Z_KP_OUTER_RETRY_MAX、Xは新設)
KPFT_REDUNDANCY_RETRY_MAX = 2                        # 設計§5-1(KEY_PHRASE_REDUNDANCY_RETRY_MAX)
EXPECTED_KPFT_METADATA_KEYS = ["kp_backend", "kp_backend_used", "prompt_id", "prompt_sha256", "user_message_sha256", "record_status",
                               "model_requested", "model_id", "response_id", "final_status", "shortfall", "kp_count_max", "attempts",
                               "attempts_detail"]   # 設計§2 run_fulltext_selection の meta(er105:449-456。未配線時点の実装値)
EXPECTED_KP_ITEM_KEYS = ["rank", "display_phrase", "source_span", "source_sentence", "used_form", "japanese_gloss",
                         "normalization_reason", "changed_from_display_phrase"]   # 実在run(Z run_e2e_06)のkeywords_canonicalized.itemsの共通キー+設計§4-2
LEGACY_KP_BACKENDS = ("db_hybrid", "strategy_l")   # 旧経路(設計§7)。値が旧ならKPFT NG
# --- KP3V(IMPLEMENTATION_DESIGN_01 KP-THREE-ASR-MAJORITY-PRODUCTION-01 §1, §6, er104 vote_check_from_audit) ---
EXPECTED_VOTE_CHECK_VERSION = "kp_vote_check_v1"     # 設計§6/er104 CHECK_VERSION
LEGACY_DUAL_CHECK_VERSION = "kp_dual_check_v1"       # 旧(読取のみ。新判定の証拠ではない)
VOTE_CONTAINER_KEYS = ("kp_vote_check", "kp_dual_check")   # 設計§6(容器名kp_dual_checkはversionで区別するとer104コメントにある)
VOTE_AUDIT_KEYS = ("vote", "dual")                   # asr_judgement.audit["vote"](旧"dual")
EXPECTED_VOTE_CHECK_KEYS = ["version", "ok", "source", "canonical_text", "wav_sha256", "vote_state", "judge_state", "reason_code", "row",
                            "pass_count", "tiebreak_enabled", "primary", "secondary", "whisper", "checked_at"]   # er104.vote_check_from_audit
EXPECTED_VOTE_AUDIT_KEYS = ["state", "reason", "row", "pass_count", "tiebreak_enabled", "primary", "secondary", "whisper",
                            "whisper_called", "secondary_called"]   # er104.vote_check_from_audit が読むkey
VOTE_PASS_STATES = ("PASS_DUAL", "PASS_VOTE_2OF3")   # 設計§1 真理値表
VOTE_TECH_STOP_STATES = ("NG_SECONDARY_UNAVAILABLE", "NG_WHISPER_UNAVAILABLE")   # 設計§3
EXPECTED_WHISPER = {"model": "small", "compute_type": "int8"}   # 設計§4
# --- PNAP(IMPLEMENTATION_DESIGN_01 PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01 §6, er103 write_run_alarms) ---
ALARM_FILE = "audit/pronunciation_alarms.json"
ALARM_REPORT_FILE = "audit/operator_alarm_report.md"
ALARM_STATE = "PASS_WITH_PRONUNCIATION_ALARM"        # 設計§4
EXPECTED_ALARM_PAYLOAD_KEYS = ["policy_id", "source", "count", "operator_only", "consistency", "hr_residual", "supply_applied", "alarms"]
EXPECTED_ALARM_RECORD_KEYS = ["alarm_id", "proper_noun", "location", "mismatch", "pronunciation_basis", "tts_supply_result",
                              "final_state", "models"]   # 設計§6-1(ユーザー承認③の必須項目)
PUBLIC_PAGE_FORBIDDEN = ["PASS_WITH_PRONUNCIATION_ALARM", "アラーム付き", "pronunciation_alarm", "operator_alarm", "固有名詞発音アラーム"]   # 設計§6-4
SUPPLY_KEYS = ("supply_map", "supply_decisions")     # 設計P-05(iii): audit.pronunciation_alarm に保存されるTTS供給の記録
LEDGER_REL = "er006_output/pronunciation_ledger_01/ledger.json"          # er006_pronunciation_ledger_01.py LEDGER_PATH
LEDGER_SIDECAR_NAMES = ("negative_cache.json",)                          # er006 PRON_SUPPLY_NEGATIVE_CACHE_FILENAME(Ledger本体と同dirのsidecar)
HR_QUEUE_RELS = ("er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl",
                 "er007_output/ja_asr_cascade_01/human_review_queue.jsonl")
ATTEMPT_HISTORY_REL = "er011_output/attempt_history.jsonl"
STORE_MANIFEST_REL = "er006_output/master_audio_store_01/manifest.json"   # er006_master_audio_store_01.py MANIFEST_PATH(非atomic write・lock無し=並列実行時の競合監視対象)
STOP_ALL_REL = "er026_output/family_z_production_e2e_01/STOP_ALL"
DELEGATION_LOG_REL = "docs/pm/delegation_log"
LOCK_FILE = "audit/review_lock_state.json"
LOCK_OK_STATES = ("RESOLVED",)
# --- 費用(daily_dev_cost_01 の換算を踏襲。出典はMarkdownに明記) ---
COST_TOOL_REL = "docs/pm/tools/daily_dev_cost_01.py"
COST_LOG_NAMES = ("raw_usage_log.jsonl", "cost_log.jsonl")
DESIGN_COST_BASELINE_SAVING_JPY = -4.8   # KPFT設計§13の推定(5->3件で約-4.8円/セット)。実測と比較する参照値
# --- Std/Advの再生順(build_key_phrase_block: 番号 -> 英 -> 第3 -> 英) ---
KP_BLOCK_UPPER_SLACK_SEC = 5.0           # 番号読み上げ+pause3つの上限(間接検査の許容)


# ============================================================
# 基本ユーティリティ
# ============================================================
def jload(path):
    """(data, error)。無ければ (None, 'ABSENT')。"""
    if not path or not os.path.exists(path):
        return None, "ABSENT"
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f), None
    except (OSError, ValueError) as e:
        return None, f"{type(e).__name__}: {e}"


def jl_lines(path):
    if not path or not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                out.append(ln)
    return out


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def norm_path(p):
    return (p or "").replace("\\", "/")


def wav_seconds(path):
    try:
        with wave.open(path, "rb") as w:
            return w.getnframes() / float(w.getframerate())
    except (OSError, EOFError, wave.Error):
        return None


def missing_keys(d, expected):
    if not isinstance(d, dict):
        return list(expected)
    return [k for k in expected if k not in d]


def find_key_dicts(obj, keys, path=""):
    """obj内を再帰し、key名が keys に含まれ値がdictのものを (path, key, dict) で列挙(位置が実装で変わり得るための探索)。"""
    found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else str(k)
            if k in keys and isinstance(v, dict):
                found.append((p, k, v))
            found.extend(find_key_dicts(v, keys, p))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            found.extend(find_key_dicts(v, keys, f"{path}[{i}]"))
    return found


def find_nonempty_key(obj, keys):
    """obj内で key名が keys に含まれ値が空でないものの件数。"""
    n = 0
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in keys and v:
                n += 1
            n += find_nonempty_key(v, keys)
    elif isinstance(obj, list):
        for v in obj:
            n += find_nonempty_key(v, keys)
    return n


def chk(cid, status, detail="", **extra):
    d = {"id": cid, "status": status, "detail": detail}
    d.update(extra)
    return d


# ============================================================
# run dir の配置(X / Z)
# ============================================================
def level_paths(family, run_dir, level):
    rd = run_dir.rstrip("/\\")
    if family == "X":
        ld = f"{rd}/{level}"
        return {"level_dir": ld, "kp_dir": f"{ld}/key_phrases", "audit": f"{ld}/audit", "narration": f"{ld}/narration",
                "results": f"{ld}/audit/tts_generation_results.json", "timeline": f"{ld}/audit/timeline.json",
                "kp_expl": None}
    ld = f"{rd}/{level}"
    return {"level_dir": ld, "kp_dir": f"{rd}/key_phrases/{level}", "audit": f"{ld}/audit", "narration": f"{ld}/narration",
            "results": f"{ld}/audit/tts_generation_results.json", "timeline": f"{ld}/assembly/timeline.json",
            "kp_expl": f"{rd}/key_phrases/{level}/kp_explanations.json"}


def detect_levels(family, run_dir):
    return [lv for lv in ("a2", "b1b") if os.path.isdir(f"{run_dir.rstrip('/\\')}/{lv}")]


def article_text_for(family, level, run_dir, source_dir):
    """本文(KP本文一致検査用)。X: <source_dir>/<level>/article.md、Z: <run>/writer/{r2,std}.md。"""
    if family == "X":
        cands = [f"{source_dir}/{level}/article.md"] if source_dir else []
        cands.append(f"{run_dir.rstrip('/\\')}/{level}/article.md")
    else:
        cands = [f"{run_dir.rstrip('/\\')}/writer/{'r2.md' if level == 'b1b' else 'std.md'}"]
    for c in cands:
        if os.path.exists(c):
            with open(c, encoding="utf-8", errors="replace") as f:
                return f.read(), c
    return None, None


_QUOTES = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-", "‐": "-", "‑": "-"})


def norm_text(s):
    s = (s or "").translate(_QUOTES).lower()
    return re.sub(r"\s+", " ", s).strip()


# ============================================================
# (a) KP選定・件数・metadata(KPFT)
# ============================================================
def collect_kp_selection(family, level, paths, text):
    kd = paths["kp_dir"]
    meta, meta_err = jload(f"{kd}/keywords_runtime_metadata.json")
    canon, canon_err = jload(f"{kd}/keywords_canonicalized.json")
    cmeta, _ = jload(f"{kd}/canonicalization_runtime_metadata.json")
    red, _ = jload(f"{kd}/keyphrase_redundancy_qa.json")
    items = (canon or {}).get("items") if isinstance(canon, dict) else None
    items = items if isinstance(items, list) else []
    nt = norm_text(text) if text else None
    rows = []
    for it in items:
        span = it.get("source_span") or it.get("display_phrase") or ""
        used = it.get("used_form") or it.get("key_phrase") or it.get("display_phrase") or ""
        in_text = (norm_text(span) in nt) if (nt is not None and span) else None
        rows.append({"rank": it.get("rank"), "display_phrase": it.get("display_phrase"), "source_span": it.get("source_span"),
                     "used_form": used, "words_span": len(span.split()) if span else None,
                     "words_used": len(used.split()) if used else None, "span_in_article": in_text,
                     "changed": bool(it.get("changed_from_display_phrase")) or (norm_text(span) != norm_text(used) if span and used else False),
                     "normalization_reason": it.get("normalization_reason"),
                     "has_gloss": bool((it.get("japanese_gloss") or "").strip()),
                     "has_source_sentence": bool((it.get("source_sentence") or "").strip()),
                     "missing_item_keys": missing_keys(it, EXPECTED_KP_ITEM_KEYS)})
    outer_log = None
    if family == "Z":
        outer_log, _ = jload(f"{kd}/outer_retry_log.json")
    outer_dirs = sorted(glob.glob(f"{kd}/outer_retry/attempt_*")) if os.path.isdir(f"{kd}/outer_retry") else []
    stale = sorted(os.path.basename(p) for p in glob.glob(f"{kd}/*STALE*"))
    hybrid = os.path.isdir(f"{kd}/key_phrases_db_hybrid")
    return {
        "kp_dir": kd, "metadata_present": meta is not None, "metadata_error": meta_err,
        "metadata_missing_keys": missing_keys(meta, EXPECTED_KPFT_METADATA_KEYS) if meta is not None else list(EXPECTED_KPFT_METADATA_KEYS),
        "kp_backend": (meta or {}).get("kp_backend"), "kp_backend_used": (meta or {}).get("kp_backend_used"),
        "model_id": (meta or {}).get("model_id"), "model_requested": (meta or {}).get("model_requested"),
        "prompt_sha256": (meta or {}).get("prompt_sha256"), "selection_attempts": (meta or {}).get("attempts"),
        "shortfall": (meta or {}).get("shortfall"), "final_status": (meta or {}).get("final_status"),
        "canonicalization_present": canon is not None, "canonicalization_overall": (canon or {}).get("overall_status") if isinstance(canon, dict) else None,
        "n_items": len(items), "items": rows,
        "canonicalization_attempts": len((cmeta or {}).get("attempts_detail") or []) if cmeta else None,
        "canonicalization_final_status": (cmeta or {}).get("final_status") if cmeta else None,
        "redundancy_status": (red or {}).get("status") if red else None,
        "redundancy_attempts": len((red or {}).get("attempts_detail") or []) if red else None,
        "outer_retry_attempts": (len(outer_log.get("attempts") or []) if isinstance(outer_log, dict) else (len(outer_dirs) if outer_dirs else None)),
        "stale_files": stale, "db_hybrid_dir_present": hybrid,
        "fallback_notice_present": bool(glob.glob(f"{kd}/*m2_fallback*")),
    }


# ============================================================
# (b) KP音声: 3-ASR投票(KP3V)
# ============================================================
def vote_summary(rank, entry):
    """KP英語エントリの投票証跡を探索して要約する。位置は実装で変わり得るため再帰探索し、見つかった位置(path)を記録する。"""
    found = find_key_dicts(entry, set(VOTE_CONTAINER_KEYS) | set(VOTE_AUDIT_KEYS))
    rec = {"rank": rank, "found_paths": [p for p, _, _ in found], "kind": "MISSING"}
    pick = None
    for p, k, d in found:     # 新version(kp_vote_check_v1)を優先
        if d.get("version") == EXPECTED_VOTE_CHECK_VERSION:
            pick = (p, k, d, "vote_check_v1")
            break
    if pick is None:
        for p, k, d in found:
            if k in VOTE_AUDIT_KEYS and ("whisper" in d or "pass_count" in d or str(d.get("state", "")).startswith(("PASS_", "NG_"))):
                pick = (p, k, d, "vote_audit")
                break
    if pick is None:
        for p, k, d in found:
            if d.get("version") == LEGACY_DUAL_CHECK_VERSION or k == "dual":
                rec["kind"] = "LEGACY_DUAL"
                rec["legacy_path"] = p
                return rec
        return rec
    p, k, d, kind = pick
    exp = EXPECTED_VOTE_CHECK_KEYS if kind == "vote_check_v1" else EXPECTED_VOTE_AUDIT_KEYS
    pr, se, wh = d.get("primary") or {}, d.get("secondary") or {}, d.get("whisper") or {}
    state = d.get("vote_state") if kind == "vote_check_v1" else d.get("state")
    called = wh.get("called") if kind == "vote_check_v1" else d.get("whisper_called", wh.get("called"))
    rec.update({"kind": kind, "path": p, "missing_keys": missing_keys(d, exp), "state": state, "row": d.get("row"),
                "primary_pass": pr.get("pass"), "primary_text": pr.get("text"), "secondary_pass": se.get("pass") if se else None,
                "secondary_text": se.get("text") if se else None, "secondary_called": (se.get("called") if se and "called" in se else d.get("secondary_called")),
                "whisper_called": bool(called), "whisper_pass": wh.get("pass"), "whisper_text": wh.get("text"), "whisper_error": wh.get("error"),
                "whisper_model": wh.get("model"), "whisper_compute_type": wh.get("compute_type"), "whisper_ms": wh.get("ms"),
                "pass_count": d.get("pass_count"), "tiebreak_enabled": d.get("tiebreak_enabled"), "ok": d.get("ok"),
                "reason": d.get("reason_code", d.get("reason")), "source": d.get("source")})
    return rec


def vote_invariants(v):
    """真理値表(設計§1/§3)に対する整合検査。違反は文字列で返す(空=OK)。"""
    bad = []
    if v.get("kind") not in ("vote_check_v1", "vote_audit"):
        return bad
    st, wc = v.get("state"), v.get("whisper_called")
    p, s = v.get("primary_pass"), v.get("secondary_pass")
    if wc and p is not None and s is not None and bool(p) == bool(s):
        bad.append("I1: P/Sが一致しているのにWhisperが発火")
    if st == "PASS_VOTE_2OF3" and not (wc and v.get("whisper_pass")):
        bad.append("I2: PASS_VOTE_2OF3なのにWhisper PASSが無い")
    if st == "PASS_DUAL" and not (p and s):
        bad.append("I3: PASS_DUALなのにP/S両PASSでない")
    if v.get("whisper_error") and st in VOTE_PASS_STATES:
        bad.append("I4: Whisper error(未利用/失敗)なのに最終PASS")
    if wc is False and st == "PASS_VOTE_2OF3":
        bad.append("I5: Whisper未発火でPASS_VOTE_2OF3")
    if st in VOTE_PASS_STATES and v.get("ok") is False:
        bad.append("I6: 最終stateがPASSなのにok=False")
    if v.get("pass_count") is not None and st in VOTE_PASS_STATES and v["pass_count"] < 2:
        bad.append("I7: PASSなのにpass_count<2")
    return bad


def collect_audio(family, level, paths):
    res, err = jload(paths["results"])
    out = {"results_present": res is not None, "results_error": err, "kp": {}, "n_kp_results": 0}
    if not isinstance(res, dict):
        return out
    kpr = res.get("key_phrases") or {}
    for rank, ent in sorted(kpr.items(), key=lambda x: str(x[0])):
        r = {"keys": sorted(ent.keys()) if isinstance(ent, dict) else []}
        for sub, e in (ent.items() if isinstance(ent, dict) else []):
            if not isinstance(e, dict):
                continue
            r[sub] = {"status": e.get("status"), "reused": e.get("reused"), "sha256": e.get("sha256"), "path": e.get("path"),
                      "asr_verified": e.get("asr_verified"), "tts_generations_used": e.get("tts_generations_used"),
                      "attempts": (len(e["attempts"]) if isinstance(e.get("attempts"), list) else e.get("tts_generations_used")),
                      "attempts_log_len": len(e["attempts_log"]) if isinstance(e.get("attempts_log"), list) else None,
                      "has_text": bool(e.get("text") or e.get("explanation_text") or e.get("canonical_text"))}
        for sub, e in (ent.items() if isinstance(ent, dict) else []):
            if sub != "english" and isinstance(e, dict) and any(k in VOTE_CONTAINER_KEYS for _, k, d in find_key_dicts(e, set(VOTE_CONTAINER_KEYS))
                                                               if d.get("version") == EXPECTED_VOTE_CHECK_VERSION):
                out.setdefault("non_english_vote_evidence", []).append(f"kp{rank}.{sub}")
        eng = ent.get("english") if isinstance(ent, dict) else None
        r["vote"] = vote_summary(rank, eng) if isinstance(eng, dict) else {"rank": rank, "kind": "MISSING"}
        out["kp"][str(rank)] = r
    out["n_kp_results"] = len(out["kp"])
    out["segments_status"] = {}
    out["segments_with_vote"] = []
    for sid, e in (res.get("segments") or {}).items():
        if isinstance(e, dict):
            out["segments_status"][sid] = e.get("status")
            if any(d.get("version") == EXPECTED_VOTE_CHECK_VERSION for _, _, d in find_key_dicts(e, set(VOTE_CONTAINER_KEYS))):
                out["segments_with_vote"].append(sid)
    out["alarm_state_segments"] = [sid for sid, e in (res.get("segments") or {}).items()
                                   if isinstance(e, dict) and isinstance(e.get("asr_judgement"), dict) and e["asr_judgement"].get("state") == ALARM_STATE]
    out["supply_nonempty_count"] = find_nonempty_key(res, set(SUPPLY_KEYS))
    out["_res_for_supply"] = None   # (JSONには出さない)
    return out


# ============================================================
# (c) 固有名詞アラーム(PNAP)
# ============================================================
def collect_alarms(run_dir, levels, family):
    out = {"per_level": {}, "total_alarms": 0}
    for lv in levels:
        base = f"{run_dir.rstrip('/\\')}/{lv}"
        pj, perr = jload(f"{base}/{ALARM_FILE}")
        md = f"{base}/{ALARM_REPORT_FILE}"
        rec = {"alarms_json_present": pj is not None, "alarms_json_error": perr, "report_md_present": os.path.exists(md)}
        if isinstance(pj, dict):
            rec["payload_missing_keys"] = missing_keys(pj, EXPECTED_ALARM_PAYLOAD_KEYS)
            alarms = pj.get("alarms") or []
            rec["count"] = pj.get("count")
            rec["consistency"] = pj.get("consistency")
            rec["hr_residual"] = pj.get("hr_residual")
            rec["supply_applied_count"] = len(pj.get("supply_applied") or [])
            rec["operator_only"] = pj.get("operator_only")
            rec["alarm_records"] = []
            for a in alarms:
                rec["alarm_records"].append({"alarm_id": a.get("alarm_id"), "proper_noun": a.get("proper_noun"), "segment_id": a.get("segment_id"),
                                             "final_state": a.get("final_state"), "missing_keys": missing_keys(a, EXPECTED_ALARM_RECORD_KEYS),
                                             "tts_supply_result": a.get("tts_supply_result"),
                                             "pronunciation_basis": a.get("pronunciation_basis"), "models": a.get("models"),
                                             "mismatch": a.get("mismatch"), "inherited": a.get("inherited")})
            out["total_alarms"] += len(alarms)
        if rec["report_md_present"]:
            with open(md, encoding="utf-8", errors="replace") as f:
                t = f.read()
            rec["report_md_head"] = t[:600]
            rec["report_md_has_section"] = "固有名詞発音アラーム" in t
        out["per_level"][lv] = rec
    return out


def ledger_lookup(repo_root, nouns, ledger_path=None):
    lp = ledger_path or os.path.join(repo_root, LEDGER_REL)
    data, err = jload(lp)
    res = {"ledger_path": norm_path(lp), "error": err, "entries": {}}
    if not isinstance(data, dict):
        return res
    for e in data.values():
        if not isinstance(e, dict):
            continue
        surf = norm_text(e.get("surface"))
        for n in nouns:
            if surf and surf == norm_text(n):
                res["entries"].setdefault(n, []).append({"surface": e.get("surface"), "evidence_tier": e.get("evidence_tier", "MISSING"),
                                                         "human_approved": e.get("human_approved", "MISSING"),
                                                         "tts_respelling": e.get("tts_respelling", "MISSING"),
                                                         "pronunciation_hint": e.get("pronunciation_hint"), "ledger_disabled": e.get("ledger_disabled")})
    return res


# ============================================================
# (d) 費用
# ============================================================
def _load_cost_tool(repo_root):
    p = os.path.join(repo_root, COST_TOOL_REL)
    if not os.path.exists(p):
        return None
    spec = importlib.util.spec_from_file_location("daily_dev_cost_01_for_er106", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


KP_ENGLISH_SEG = re.compile(r"^kp\d+_(english|en)$")
KP_JA_SEG = re.compile(r"^kp\d+_(japanese_meaning|ja|meaning)$")
KP_EXPL_SEG = re.compile(r"^kp\d+_explanation(_en)?$")
KP_CHAIN_STAGE = re.compile(r"kp|key_?phrase|gloss|canonical|redundan|select", re.I)


def classify_record(rec):
    """(bucket, kind)。bucket: kp_chain / kp_audio_english / kp_audio_ja_meaning / kp_audio_explanation / scaffold_llm_unsplit / non_kp_audio / other
    kind: tts / asr_openai / asr_azure / llm / other"""
    prov, model = rec.get("provider") or "", rec.get("model_id") or rec.get("model") or ""
    if prov in ("gemini", "gemini_batch") and "tts" in model:
        kind = "tts"
    elif prov == "openai_asr":
        kind = "asr_openai"
    elif prov == "azure":
        kind = "asr_azure"
    elif prov in ("openai", "gemini", "gemini_batch", "deepseek"):
        kind = "llm"
    else:
        kind = "other"
    seg, stage = rec.get("segment") or "", rec.get("stage") or ""
    if KP_ENGLISH_SEG.match(seg):
        return "kp_audio_english", kind
    if KP_JA_SEG.match(seg):
        return "kp_audio_ja_meaning", kind
    if KP_EXPL_SEG.match(seg):
        return "kp_audio_explanation", kind
    if seg:
        return "non_kp_audio", kind
    if KP_CHAIN_STAGE.search(stage) and kind == "llm":
        return "kp_chain", kind
    if stage == "scaffold":
        return "scaffold_llm_unsplit", kind      # Xのscaffoldはsupport文面生成とKP chainが同stage tag。--scaffold-only kpなら全額KP chain
    return "other", kind


def collect_cost(repo_root, run_dir):
    tool = _load_cost_tool(repo_root)
    res = {"tool": COST_TOOL_REL if tool else None, "usd_jpy": getattr(tool, "USD_JPY", None) if tool else None,
           "pricing_snapshot": getattr(tool, "PRICING_REL", None) if tool else None, "files": [], "records": 0,
           "buckets": {}, "by_kind": {}, "by_model": {}, "unpriced": {}, "total_jpy": 0.0, "synthetic_skipped": 0}
    if tool is None:
        res["error"] = "daily_dev_cost_01.py が見つからない(MISSING)"
        return res
    prices = tool.load_prices(repo_root)
    files = [os.path.join(run_dir, n) for n in COST_LOG_NAMES if os.path.exists(os.path.join(run_dir, n))]
    res["files"] = [norm_path(f) for f in files]
    for f in files:
        for ln in jl_lines(f):
            try:
                rec = json.loads(ln)
            except ValueError:
                continue
            if tool.is_synthetic_record(rec):
                res["synthetic_skipped"] += 1
                continue
            res["records"] += 1
            usd, why = tool.price_record(rec, prices)
            bucket, kind = classify_record(rec)
            key_model = f"{rec.get('provider')}/{rec.get('model_id') or rec.get('model')}"
            if usd is None:
                res["unpriced"][why or key_model] = res["unpriced"].get(why or key_model, 0) + 1
                continue
            jpy = usd * tool.USD_JPY
            b = res["buckets"].setdefault(bucket, {"jpy": 0.0, "calls": 0})
            b["jpy"] += jpy
            b["calls"] += 1
            k = res["by_kind"].setdefault(f"{bucket}:{kind}", {"jpy": 0.0, "calls": 0})
            k["jpy"] += jpy
            k["calls"] += 1
            m = res["by_model"].setdefault(key_model, {"jpy": 0.0, "calls": 0})
            m["jpy"] += jpy
            m["calls"] += 1
            res["total_jpy"] += jpy
    for d in (res["buckets"], res["by_kind"], res["by_model"]):
        for v in d.values():
            v["jpy"] = round(v["jpy"], 4)
    res["total_jpy"] = round(res["total_jpy"], 4)
    kp_audio = sum(res["buckets"].get(b, {}).get("jpy", 0.0) for b in ("kp_audio_english", "kp_audio_ja_meaning", "kp_audio_explanation"))
    res["kp_related_jpy"] = round(kp_audio + res["buckets"].get("kp_chain", {}).get("jpy", 0.0), 4)
    res["kp_related_incl_unsplit_scaffold_jpy"] = round(res["kp_related_jpy"] + res["buckets"].get("scaffold_llm_unsplit", {}).get("jpy", 0.0), 4)
    return res


# ============================================================
# (e) STOP・HR Lock・共有log
# ============================================================
def stop_sentinels(repo_root, run_dirs):
    found = []
    for rd in run_dirs:
        for n in ("STOP", "STOP_ALL"):
            p = os.path.join(rd, n)
            if os.path.exists(p):
                found.append(norm_path(p))
    p = os.path.join(repo_root, STOP_ALL_REL)
    if os.path.exists(p):
        found.append(norm_path(p))
    dl = os.path.join(repo_root, DELEGATION_LOG_REL)
    for p in glob.glob(os.path.join(dl, "*STOP_NOTICE*")):
        found.append(norm_path(p))
    return sorted(set(found))


def run_stop_helper(repo_root, run_dir, managed_id, out_path):
    """tools/stop_scope_check_01.py を実行(rc=3なら停止)。NOTICE本文は自分で解釈しない(rcだけ見る)。"""
    py = sys.executable
    cmd = [py, os.path.join(repo_root, "tools", "stop_scope_check_01.py"), "--managed-id", managed_id, "--run-dir", run_dir, "--out", out_path]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=repo_root)
        return {"rc": r.returncode, "out": norm_path(out_path), "stdout_head": (r.stdout or "")[:300]}
    except Exception as e:  # noqa: BLE001
        return {"rc": None, "error": f"{type(e).__name__}: {e}"}


def lock_states(run_dir, levels):
    out = {}
    for lv in levels:
        d, err = jload(f"{run_dir.rstrip('/\\')}/{lv}/{LOCK_FILE}")
        if not isinstance(d, dict):
            out[lv] = {"present": False, "error": err}
            continue
        counts = {}
        bad = []
        for sid, e in d.items():
            st = (e or {}).get("state") if isinstance(e, dict) else None
            counts[st] = counts.get(st, 0) + 1
            if st not in LOCK_OK_STATES:
                bad.append(sid)
        out[lv] = {"present": True, "state_counts": counts, "non_resolved_segments": bad}
    return out


def take_snapshot(repo_root, run_dirs):
    snap = {"taken_at": datetime.datetime.now().isoformat(timespec="seconds"), "hr_queues": {}, "attempt_history_lines": 0,
            "ledger": {}, "stop_sentinels": stop_sentinels(repo_root, run_dirs)}
    for rel in HR_QUEUE_RELS:
        snap["hr_queues"][rel] = len(jl_lines(os.path.join(repo_root, rel)))
    snap["attempt_history_lines"] = len(jl_lines(os.path.join(repo_root, ATTEMPT_HISTORY_REL)))
    lp = os.path.join(repo_root, LEDGER_REL)
    if os.path.exists(lp):
        data, _ = jload(lp)
        snap["ledger"] = {"sha256": sha256_file(lp), "n_entries": len(data) if isinstance(data, dict) else None}
    side = {}
    for n in LEDGER_SIDECAR_NAMES:
        sp = os.path.join(os.path.dirname(lp), n)
        side[n] = {"exists": os.path.exists(sp), "sha256": sha256_file(sp) if os.path.exists(sp) else None}
    snap["ledger_sidecars"] = side
    mp = os.path.join(repo_root, STORE_MANIFEST_REL)
    md, merr = jload(mp)
    snap["store_manifest"] = {"exists": os.path.exists(mp), "valid_json": isinstance(md, dict), "n_entries": len(md) if isinstance(md, dict) else None}
    return snap


def compare_snapshot(repo_root, snap, run_dirs):
    """前後差分。新規行のうち、今回のrun(run dir名/パスが行に含まれる)に帰属するものだけをNG判定の対象にする。
    他agentの同時実行などによる帰属不能な新規行は別カウント(情報)。Ledger sidecar(negative_cache.json)はLedger本体の変更判定から除外。"""
    keys = sorted({norm_path(rd).rstrip("/") for rd in run_dirs} | {os.path.basename(rd.rstrip("/\\")) for rd in run_dirs})
    res = {"hr_queues": {}, "attempt_history": {}, "ledger": {}, "stop_sentinels_before": snap.get("stop_sentinels"), "stop_sentinels_after": stop_sentinels(repo_root, run_dirs)}
    for rel, n0 in (snap.get("hr_queues") or {}).items():
        lines = jl_lines(os.path.join(repo_root, rel))
        new = lines[n0:]
        attributed = [l for l in new if any(k in norm_path(l) for k in keys)]
        res["hr_queues"][rel] = {"before": n0, "after": len(lines), "new_total": len(new), "new_attributed_to_these_runs": len(attributed),
                                 "new_not_attributed": len(new) - len(attributed)}
    lines = jl_lines(os.path.join(repo_root, ATTEMPT_HISTORY_REL))
    new = lines[snap.get("attempt_history_lines", 0):]
    attributed = []
    for l in new:
        try:
            d = json.loads(l)
        except ValueError:
            d = {}
        th = str(d.get("theme_id") or "")
        if any(k in th or k in norm_path(l) for k in keys):
            attributed.append(d)
    hr_reached = [d for d in attributed if d.get("human_review_reached")]
    res["attempt_history"] = {"before": snap.get("attempt_history_lines"), "after": len(lines), "new_total": len(new),
                              "new_attributed_to_these_runs": len(attributed), "new_not_attributed": len(new) - len(attributed),
                              "attributed_human_review_reached": len(hr_reached)}
    mp = os.path.join(repo_root, STORE_MANIFEST_REL)
    md, merr = jload(mp)
    b = snap.get("store_manifest") or {}
    n_after = len(md) if isinstance(md, dict) else None
    res["store_manifest"] = {"before_entries": b.get("n_entries"), "after_entries": n_after, "valid_json_after": isinstance(md, dict),
                             "entries_decreased": (b.get("n_entries") is not None and n_after is not None and n_after < b["n_entries"]),
                             "note": "非atomic write・lock無し。X/Z並列TTSでは更新消失/部分読込が起き得る。valid_json_after=False または entries_decreased=True は競合の兆候"}
    lp = os.path.join(repo_root, LEDGER_REL)
    now = sha256_file(lp) if os.path.exists(lp) else None
    res["ledger"] = {"sha256_before": (snap.get("ledger") or {}).get("sha256"), "sha256_after": now,
                     "changed": now != (snap.get("ledger") or {}).get("sha256"), "sidecars_excluded": list(LEDGER_SIDECAR_NAMES)}
    sidenow = {}
    for n in LEDGER_SIDECAR_NAMES:
        sp = os.path.join(os.path.dirname(lp), n)
        sidenow[n] = sha256_file(sp) if os.path.exists(sp) else None
        res["ledger"].setdefault("sidecar_changed", {})[n] = sidenow[n] != ((snap.get("ledger_sidecars") or {}).get(n) or {}).get("sha256")
    return res


# ============================================================
# (f) 試聴ページ・再生順
# ============================================================
def find_pages(run_dir, explicit=None):
    if explicit and os.path.exists(explicit):
        return [explicit]
    pats = ["**/index.html", "**/player.html"]
    out = []
    for p in pats:
        out.extend(glob.glob(os.path.join(run_dir, p), recursive=True))
    return sorted(set(out))


def page_report(repo_root, run_dir, explicit=None):
    pages = find_pages(run_dir, explicit)
    rep = {"pages_found": [norm_path(p) for p in pages], "checks": []}
    mod = None
    p = os.path.join(repo_root, "er_user_listening_page_common_01.py")
    if os.path.exists(p):
        spec = importlib.util.spec_from_file_location("er_user_listening_page_common_01_for_er106", p)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    for pg in pages:
        with open(pg, encoding="utf-8", errors="replace") as f:
            html = f.read()
        leaks = [w for w in PUBLIC_PAGE_FORBIDDEN if w in html]
        sib = [os.path.join(os.path.dirname(pg), n) for n in ("standard.html", "advanced.html")]
        for s in sib:
            if os.path.exists(s):
                with open(s, encoding="utf-8", errors="replace") as f:
                    h2 = f.read()
                leaks += [f"{os.path.basename(s)}:{w}" for w in PUBLIC_PAGE_FORBIDDEN if w in h2]
        r = {"page": norm_path(pg), "alarm_words_leaked": leaks}
        if mod is not None and os.path.basename(pg) == "index.html":
            try:
                c = mod.check_page(html, base_dir=os.path.dirname(pg))
                r["standard_check_overall"] = c.get("overall")
                r["standard_check_failed"] = [k for k, v in c.get("checks", {}).items() if not v.get("ok")]
                r["kp_rows"] = {k: v.get("detail") for k, v in c.get("checks", {}).items() if k.endswith("key_phrases_en_ja")}
            except Exception as e:  # noqa: BLE001
                r["standard_check_error"] = f"{type(e).__name__}: {e}"
        rep["checks"].append(r)
    return rep


def kp_order_check(family, level, paths, n_kp):
    """再生順の間接検査: timelineのkey_phrase_N durationが 2*dur(en)+dur(第3) 以上かつ +KP_BLOCK_UPPER_SLACK_SEC 以下。
    第3=Std: 日本語意味(Z kp{r}_ja / X meaning_{idx}) / Adv: 英語解説(kp{r}_explanation_en)。build_key_phrase_block の並びは 番号->英->第3->英 (er003_b1_p9a_audio.py:423-440)。"""
    tl, err = jload(paths["timeline"])
    res = {"timeline_present": tl is not None, "timeline_error": err, "per_kp": {}}
    if tl is None:
        return res
    entries = tl.get("timeline") if isinstance(tl, dict) else tl
    third_tpl = ["kp{r}_explanation_en.wav"] if level == "b1b" else ["kp{r}_ja.wav", "meaning_{i}.wav"]
    pat = re.compile(r"^(?:key[ _]phrase)[ _](\d+)$", re.I)
    rows = {}
    for e in entries or []:
        m = pat.match(str(e.get("part", "")).strip())
        if m:
            rows[int(m.group(1))] = e.get("duration_seconds")
    ranks = sorted(rows)
    for i, r in enumerate(ranks, start=1):
        en = wav_seconds(f"{paths['narration']}/kp{r}_en.wav")
        if en is None:
            en = wav_seconds(f"{paths['narration']}/kp{r}_english.wav")
        third = None
        for t in third_tpl:
            third = wav_seconds(f"{paths['narration']}/" + t.format(r=r, i=i))
            if third is not None:
                break
        if en is None or third is None:
            res["per_kp"][r] = {"status": "MISSING", "detail": f"component wav不明 en={en} third={third}", "block_seconds": rows[r]}
            continue
        lo = 2 * en + third
        ok = rows[r] is not None and lo - 0.05 <= rows[r] <= lo + KP_BLOCK_UPPER_SLACK_SEC
        res["per_kp"][r] = {"status": "OK" if ok else "NG", "block_seconds": rows[r], "lower_bound": round(lo, 3), "en": round(en, 3), "third": round(third, 3)}
    res["n_timeline_kp"] = len(ranks)
    res["n_kp_expected"] = n_kp
    return res


# ============================================================
# run/level統合
# ============================================================
WHISPER_PREFLIGHT_RX = re.compile(r"whisper[_ ]?(?:model[_ ])?preflight|preflight.{0,60}whisper", re.I)   # KP3V設計§16-1 P-08(名称は配線後に確認。未確認のためregexで探索)


def find_whisper_preflight(run_dir):
    """run dir直下のjson/jsonl/log/txtにWhisper preflight記録があるか(実装後に名称確認。無ければMISSING扱い)。"""
    hits = []
    for pat in ("*.json", "*.jsonl", "*.log", "*.txt"):
        for f in glob.glob(os.path.join(run_dir, pat)):
            try:
                with open(f, encoding="utf-8", errors="replace") as fh:
                    if WHISPER_PREFLIGHT_RX.search(fh.read(2_000_000)):
                        hits.append(os.path.basename(f))
            except OSError:
                continue
    return hits


def collect_family(repo_root, family, run_dir, source_dir=None, page=None):
    levels = detect_levels(family, run_dir)
    out = {"family": family, "run_dir": norm_path(run_dir), "exists": os.path.isdir(run_dir), "levels": {}, "entry_point": None}
    if family == "X":
        ep, _ = jload(f"{run_dir.rstrip('/\\')}/entry_point.json")
        out["entry_point"] = {"kp_backend_used_by_level": (ep or {}).get("kp_backend_used_by_level"), "m2_fallback_by_level": (ep or {}).get("m2_fallback_by_level"),
                              "kp_stage_status": (ep or {}).get("kp_stage_status"), "tts_backend": (ep or {}).get("tts_backend"),
                              "stage": (ep or {}).get("stage"), "present": ep is not None} if ep is not None else {"present": False}
        sd = source_dir or (ep or {}).get("source_dir")
    else:
        sd = None
    for lv in levels:
        paths = level_paths(family, run_dir, lv)
        text, tpath = article_text_for(family, lv, run_dir, sd)
        sel = collect_kp_selection(family, lv, paths, text)
        aud = collect_audio(family, lv, paths)
        aud.pop("_res_for_supply", None)
        out["levels"][lv] = {"article_text_path": norm_path(tpath) if tpath else None, "selection": sel, "audio": aud,
                             "order": kp_order_check(family, lv, paths, sel["n_items"]), "locks": lock_states(run_dir, [lv])[lv]}
        if family == "Z":
            ex, _ = jload(paths["kp_expl"])
            out["levels"][lv]["z_explanations_present"] = isinstance(ex, dict) and bool(ex.get("items"))
    out["whisper_preflight_files"] = find_whisper_preflight(run_dir)
    out["alarms"] = collect_alarms(run_dir, levels, family)
    out["cost"] = collect_cost(repo_root, run_dir)
    out["pages"] = page_report(repo_root, run_dir, page)
    out["levels_detected"] = levels
    return out


# ============================================================
# 判定(3件 x 確認項目へのマッピング)
# ============================================================
def _each_level(fam, fn):
    return [(lv, fn(lv, d)) for lv, d in fam["levels"].items()]


def agg_status(items):
    """複数(level)判定の集約: NG > MISSING > NOT_FIRED > MANUAL > INFO > OK。levelなしは MISSING。"""
    if not items:
        return "MISSING"
    order = ["NG", "MISSING", "NOT_FIRED", "MANUAL", "INFO", "OK"]
    for s in order:
        if s in items:
            return s
    return "MISSING"


def evaluate_kpft(fam):
    """KPFT USER.md §6 12確認項目 + §8 9項目報告のうち機械判定できるもの(family単位)。"""
    cks = []
    lv_items = fam["levels"].items()

    def per_level(cid, fn, label=""):
        sts, det = [], []
        for lv, d in lv_items:
            s, t = fn(lv, d)
            sts.append(s)
            det.append(f"{lv}:{s}({t})")
        cks.append(chk(cid, agg_status(sts), "; ".join(det)))

    per_level("KPFT-1 全文直接選定(候補DBでない)", lambda lv, d: (
        ("OK" if d["selection"]["kp_backend_used"] == KPFT_BACKEND_ID and d["selection"]["kp_backend"] == KPFT_BACKEND_ID
         and not d["selection"]["db_hybrid_dir_present"] else
         ("MISSING" if (not d["selection"]["metadata_present"] or d["selection"]["kp_backend_used"] is None) else "NG")),
        f"kp_backend={d['selection']['kp_backend']} used={d['selection']['kp_backend_used']} db_hybrid_dir={d['selection']['db_hybrid_dir_present']}"))
    per_level("KPFT-2 actual model ID=gpt-6-luna", lambda lv, d: (
        ("OK" if d["selection"]["model_id"] == KPFT_MODEL_ID else ("MISSING" if d["selection"]["model_id"] is None else "NG")),
        f"model_id={d['selection']['model_id']} requested={d['selection']['model_requested']}"))
    per_level("KPFT-3 正式Prompt 2のsha", lambda lv, d: (
        ("OK" if d["selection"]["prompt_sha256"] == KPFT_PROMPT_2_SHA256 else ("MISSING" if d["selection"]["prompt_sha256"] is None else "NG")),
        f"prompt_sha256={str(d['selection']['prompt_sha256'])[:16]}"))
    per_level("KPFT-4 KP最大3件", lambda lv, d: (
        ("OK" if 1 <= d["selection"]["n_items"] <= KPFT_KP_COUNT_MAX else ("MISSING" if not d["selection"]["canonicalization_present"] else "NG")),
        f"n_items={d['selection']['n_items']} shortfall={d['selection']['shortfall']} (期待3, 1-2はshortfall記録つきで許容)"))

    def _tx(lv, d):
        rows = d["selection"]["items"]
        if not rows:
            return "MISSING", "items無し"
        if any(r["span_in_article"] is None for r in rows):
            return "MANUAL", f"本文未取得({d['article_text_path']})。--x-source-dirを指定"
        bad = [r["rank"] for r in rows if not r["span_in_article"] or (r["words_span"] or 0) > KPFT_WORDS_MAX]
        return ("NG" if bad else "OK"), f"本文不一致/6語以上のrank={bad} (全{len(rows)}件のsource_span本文一致+<=5語)"
    per_level("KPFT-5 本文外/6語以上が不採用", _tx)

    def _norm(lv, d):
        rows = d["selection"]["items"]
        if not rows:
            return "MISSING", "items無し"
        ch = [(r["rank"], r["source_span"], r["used_form"], r["normalization_reason"]) for r in rows if r["changed"]]
        return "INFO", f"変更{len(ch)}件(要:聴取/目視で一般化の妥当性確認): {ch}"
    per_level("KPFT-6 原形化・一般化", _norm)

    def _after(lv, d):
        a, o = d["audio"], d["order"]
        if not a["results_present"]:
            return "MISSING", "tts_generation_results.json無し"
        n = d["selection"]["n_items"]
        bad = []
        for r in range(1, n + 1):
            e = a["kp"].get(str(r))
            if not e or (e.get("english") or {}).get("status") not in ("OK", "OK_REUSED", "REUSED"):
                bad.append(f"kp{r}.english")
        if lv_is_std(lv):
            for r in range(1, n + 1):
                e = a["kp"].get(str(r)) or {}
                ja = [k for k in e.get("keys", []) if re.search(r"japanese|_ja|^ja", k)]
                if ja and any((e.get(k) or {}).get("status") != "OK" for k in ja):
                    bad.append(f"kp{r}.ja")
        else:
            for r in range(1, n + 1):
                e = (a["kp"].get(str(r)) or {}).get("explanation") or {}
                if e.get("status") != "OK":
                    bad.append(f"kp{r}.explanation")
        ord_bad = [r for r, v in o["per_kp"].items() if v["status"] == "NG"]
        ord_miss = [r for r, v in o["per_kp"].items() if v["status"] == "MISSING"]
        if not o["timeline_present"]:
            return ("NG" if bad else "MISSING"), f"timeline無し(assemble未実施?) 未OK={bad}"
        if o.get("n_timeline_kp") != n:
            bad.append(f"timeline KP={o.get('n_timeline_kp')}!=items={n}")
        if bad or ord_bad:
            return "NG", f"未OK={bad} 再生順間接検査NG={ord_bad}"
        return ("MISSING" if ord_miss else "OK"), f"KP音声/解説/ja意味 OK、timeline KP={o.get('n_timeline_kp')}、再生順間接検査 miss={ord_miss}"
    per_level("KPFT-7 後段(意味/解説/音声/ASR/組立)", _after)

    def _retry(lv, d):
        s = d["selection"]
        info = f"選定{s['selection_attempts']}/{KPFT_SELECTION_MAX_ATTEMPTS} canon{s['canonicalization_attempts']}/{KPFT_CANON_MAX_ATTEMPTS} red{s['redundancy_attempts']}({s['redundancy_status']}) outer{s['outer_retry_attempts']}/{KPFT_OUTER_RETRY_MAX} stale={s['stale_files']} fallback_notice={s['fallback_notice_present']}"
        over = ((s["selection_attempts"] or 0) > KPFT_SELECTION_MAX_ATTEMPTS or (s["canonicalization_attempts"] or 0) > KPFT_CANON_MAX_ATTEMPTS
                or (s["outer_retry_attempts"] or 0) > KPFT_OUTER_RETRY_MAX or s["fallback_notice_present"])
        return ("NG" if over else "INFO"), info
    per_level("KPFT-8 retry/fallback/regen/resume", _retry)
    cks.append(chk("KPFT-9 旧DB/5件のDangling Reference", "MANUAL", "--dangling-grep で別途集計(下記)。run出力からは判定しない"))
    cks.append(chk("KPFT-10 必須Regression/Validator/test", "MANUAL", "当日手順書の事前チェック(全回帰PASS)で確認"))
    cks.append(chk("KPFT-11 X/Z双方の正式runtime evidence", "INFO" if fam["levels"] else "MISSING", f"levels={list(fam['levels'])}"))
    cks.append(chk("KPFT-12 SSOT/Git", "MANUAL", "Fable受入時"))
    return cks


def lv_is_std(lv):
    return lv == "a2"


def evaluate_kp3v(fam):
    """KP3V USER.md §5 9確認項目(family単位)。"""
    cks = []
    votes = []
    for lv, d in fam["levels"].items():
        for r, e in d["audio"]["kp"].items():
            v = dict(e.get("vote") or {})
            v["level"] = lv
            v["reused"] = (e.get("english") or {}).get("reused")
            votes.append(v)
    kinds = [v.get("kind") for v in votes]
    if not votes:
        cks.append(chk("KP3V-0 KP英語voteの存在", "MISSING", "KP英語音声のresultsが無い"))
        return cks, votes
    legacy = [v for v in votes if v["kind"] == "LEGACY_DUAL"]
    miss = [v for v in votes if v["kind"] == "MISSING"]
    new = [v for v in votes if v["kind"] in ("vote_check_v1", "vote_audit")]
    cks.append(chk("KP3V-0 KP英語voteの存在", "OK" if new and not miss and not legacy else ("MISSING" if not new else "NG"),
                   f"new={len(new)} legacy_dual={len(legacy)} missing={len(miss)} (旧dual/証跡無しが残る=新判定が通っていない)"))
    mk = sorted({k for v in new for k in (v.get("missing_keys") or [])})
    cks.append(chk("KP3V-0b 期待キー不一致", "MISSING" if (mk or not new) else "OK", f"missing_keys={mk}(実装側の名称が設計書と違う可能性。推測補完しない)"))
    fired = [v for v in new if v.get("whisper_called")]
    split = [v for v in new if v.get("primary_pass") is not None and v.get("secondary_pass") is not None and bool(v["primary_pass"]) != bool(v["secondary_pass"])]
    i1_bad = [(v["level"], v["rank"]) for v in new if any(x.startswith("I1") for x in vote_invariants(v))]
    unfired_split = [(v["level"], v["rank"]) for v in split if not v.get("whisper_called") and v.get("state") not in VOTE_TECH_STOP_STATES
                     and v.get("state") != "NG_PROTECTED" and v.get("state") != "NG_SPLIT_TIEBREAK_OFF"]
    cks.append(chk("KP3V-1 割れた場合のみWhisper発動", "NG" if (i1_bad or unfired_split) else ("OK" if new else "MISSING"),
                   f"split(P!=S)={len(split)} whisper_fired={len(fired)} 割れ無しで発火(I1違反)={i1_bad} 割れたのに未発火={unfired_split}"))
    cks.append(chk("KP3V-1b Whisperの自然発火(発火証拠)", "OK" if fired else "NOT_FIRED",
                   "割れが発生しなかった場合は NOT_FIRED(自然発火待ち。保存wavのreplayは正式runtime証拠に当たらない=PNAP設計§10と同じ扱い)"))
    p2 = [v for v in new if v.get("state") == "PASS_VOTE_2OF3"]
    cks.append(chk("KP3V-1c Whisper事前確認(preflight)の記録(設計§16-1 P-08)", "OK" if fam.get("whisper_preflight_files") else "MISSING",
                   f"記録を含むファイル={fam.get('whisper_preflight_files')}(名称は配線後に確認。無い場合は実装側の記録先を確認)"))
    cks.append(chk("KP3V-2 2/3 PASSで正常終了", "OK" if p2 else "NOT_FIRED", f"PASS_VOTE_2OF3={len(p2)}件 rank={[(v['level'], v['rank']) for v in p2]}"))
    n23 = [v for v in new if v.get("state") in ("NG_VOTE_WHISPER_NG", "NG_BOTH", "NG_PROTECTED_DISSENT", "NG_SPLIT_TIEBREAK_OFF")]
    cks.append(chk("KP3V-3 2/3 NGは従来どおりNG", "INFO", f"NG系state={len(n23)}件(最終採用wavがNG stateでないかはKP3V-4/invariantsで検査。NG attemptはattempts履歴側)"))
    inv = {f"{v['level']}#{v['rank']}": vote_invariants(v) for v in new if vote_invariants(v)}
    cks.append(chk("KP3V-4 Whisper error/未利用でPASSにしない(不変条件I1-I7)", "NG" if inv else ("OK" if new else "MISSING"),
                   f"違反={inv}" if inv else f"{len(new)}件の投票記録でI1-I7違反なし"))
    cfg = sorted({(v.get("whisper_model"), v.get("whisper_compute_type")) for v in fired})
    bad_cfg = [c for c in cfg if (c[0] != EXPECTED_WHISPER["model"] or c[1] != EXPECTED_WHISPER["compute_type"])]
    cks.append(chk("KP3V-4b Whisper構成(small/int8)", "NG" if bad_cfg else ("OK" if fired else "NOT_FIRED"), f"observed={cfg}"))
    cks.append(chk("KP3V-5 retry/fallback/regen/resumeへの一貫適用", "INFO",
                   "再利用(reused=True)のvote=" + str([(v["level"], v["rank"], v.get("source"), v.get("state")) for v in new if v.get("reused")])
                   + " / attempts=" + str({f'{lv}#{r}': (e.get('english') or {}).get('attempts') for lv, d in fam['levels'].items() for r, e in d['audio']['kp'].items()})))
    cks.append(chk("KP3V-6 Store再利用時にも新判定", "OK" if any(v.get("reused") and v["kind"] in ("vote_check_v1", "vote_audit") for v in votes) else
                   ("NOT_FIRED" if not any(v.get("reused") for v in votes) else "NG"),
                   f"reused={sum(1 for v in votes if v.get('reused'))}件"))
    leak = [(lv, x) for lv, d in fam["levels"].items() for x in d["audio"].get("non_english_vote_evidence", [])]
    leak += [(lv, sid) for lv, d in fam["levels"].items() for sid in d["audio"].get("segments_with_vote", [])]
    cks.append(chk("KP3V-7 KP英語解説・その他音声に影響なし(voteの証跡が英語phrase以外に付かない)", "NG" if leak else "OK", f"英語phrase以外にvote証跡が付いた箇所={leak}"))
    cks.append(chk("KP3V-8 固有名詞アラームとの適用範囲整合", "INFO", "KP segmentにPNAPアラーム状態が付いていないこと: PNAP側のKP混入検査を参照"))
    cks.append(chk("KP3V-9 X/Z双方の正式runtime evidence", "INFO", f"levels={list(fam['levels'])}"))
    return cks, votes


def evaluate_pnap(fam, snapshot_diff, ledger, pages):
    """PNAP USER.md §5 9確認項目。アラームは自然発火待ち(NOT_FIRED)があり得る。"""
    cks = []
    al = fam["alarms"]
    per = al["per_level"]
    n_alarm = al["total_alarms"]
    levels = list(per)
    json_ok = [lv for lv, r in per.items() if r["alarms_json_present"]]
    cks.append(chk("PNAP-0 audit/pronunciation_alarms.json と operator_alarm_report.md の生成", "OK" if levels and len(json_ok) == len(levels) and all(r["report_md_present"] for r in per.values()) else ("MISSING" if not json_ok else "NG"),
                   f"levels={levels} json={json_ok}"))
    mk = sorted({k for r in per.values() for k in (r.get("payload_missing_keys") or [])})
    rmk = sorted({k for r in per.values() for a in r.get("alarm_records", []) for k in a["missing_keys"]})
    cks.append(chk("PNAP-0b 期待キー不一致(payload/record)", "MISSING" if (mk or rmk or not json_ok) else "OK", f"payload_missing={mk} record_missing={rmk}"))
    cons = [(lv, r.get("consistency")) for lv, r in per.items()]
    bad_cons = [lv for lv, c in cons if isinstance(c, dict) and not c.get("match")]
    cks.append(chk("PNAP-6 アラームが完成報告へ引継ぎ(集計一致P-08)", "NG" if bad_cons else ("OK" if json_ok else "MISSING"),
                   f"consistency={cons} / ALARM state segments(results)={ {lv: d['audio'].get('alarm_state_segments') for lv, d in fam['levels'].items()} }"))
    cks.append(chk("PNAP-2 不一致時にアラーム記録+制作継続(発火証拠)", "OK" if n_alarm else "NOT_FIRED",
                   f"alarms={n_alarm}件 nouns={[a['proper_noun'] for r in per.values() for a in r.get('alarm_records', [])]}(0件=自然発火せず。再実行は別素材へ。設計§10)"))
    # アラーム必須項目(ユーザー承認③)
    need = []
    for lv, r in per.items():
        for a in r.get("alarm_records", []):
            if not (a.get("proper_noun") and a.get("mismatch") and a.get("pronunciation_basis") is not None and a.get("tts_supply_result") is not None
                    and a.get("final_state") and a.get("models")):
                need.append((lv, a.get("alarm_id")))
    cks.append(chk("PNAP-2b アラーム記録の必須項目(固有名詞/箇所/不一致/根拠/TTS供給結果/最終状態/models)", "NG" if need else ("OK" if n_alarm else "NOT_FIRED"), f"欠落={need}"))
    hr_new = None
    if snapshot_diff:
        hq = snapshot_diff["hr_queues"]
        hr_new = sum(v["new_attributed_to_these_runs"] for v in hq.values())
        ah = snapshot_diff["attempt_history"]["attributed_human_review_reached"]
        lock_bad = {lv: d["locks"].get("non_resolved_segments") for lv, d in fam["levels"].items() if d["locks"].get("non_resolved_segments")}
        cks.append(chk("PNAP-3 固有名詞不一致のみでHRに回らない(HR queue/attempt_history新規行なし・Lock RESOLVED)",
                       "NG" if (hr_new or ah or lock_bad) else "OK",
                       f"HR queue新規(このrun帰属)={hr_new} attempt_history HR到達(帰属)={ah} 非RESOLVED lock={lock_bad} / 帰属不能の新規HR行={sum(v['new_not_attributed'] for v in hq.values())}(他agent等・情報)"))
    else:
        lock_bad = {lv: d["locks"].get("non_resolved_segments") for lv, d in fam["levels"].items() if d["locks"].get("non_resolved_segments")}
        cks.append(chk("PNAP-3 固有名詞不一致のみでHRに回らない", "MANUAL" if not lock_bad else "NG",
                       f"snapshot未指定のためHR queue/attempt_history前後比較不可。非RESOLVED lock={lock_bad}"))
    sup = sum(d["audio"].get("supply_nonempty_count", 0) for d in fam["levels"].values())
    sup_applied = sum(r.get("supply_applied_count", 0) for r in per.values())
    cks.append(chk("PNAP-1 発音情報取得・TTS供給(respelling)の発火記録", "OK" if (sup or sup_applied) else "NOT_FIRED",
                   f"results内supply記録(非空)={sup} / payload.supply_applied={sup_applied}"))
    nouns = sorted({a["proper_noun"] for r in per.values() for a in r.get("alarm_records", []) if a.get("proper_noun")})
    cks.append(chk("PNAP-1b Ledger evidence_tier/human_approved", "INFO" if ledger["entries"] or not nouns else "MISSING",
                   f"対象語={nouns} Ledger一致={ {n: ledger['entries'].get(n) for n in nouns} }"))
    cks.append(chk("PNAP-4 通常ASR/retry/fallback/regen/resume整合", "INFO", "tts_generation_results.segments statusとattempts: " + str({lv: d['audio'].get('segments_status') for lv, d in fam['levels'].items()})[:400]))
    cks.append(chk("PNAP-5 固有名詞以外の不一致は従来どおり", "MANUAL", "アラーム対象外のNG/HRが従来どおり残るかは、HR residual(payload.hr_residual)で確認: " + str({lv: r.get('hr_residual') for lv, r in per.items()})[:300]))
    leaks = [(p["page"], p["alarm_words_leaked"]) for p in pages["checks"] if p["alarm_words_leaked"]]
    cks.append(chk("PNAP-7 一般リスナー(公開ページ)に非露出", "NG" if leaks else ("OK" if pages["checks"] else "MISSING"),
                   f"leaks={leaks} pages={[p['page'] for p in pages['checks']]}"))
    kp_alarm = [(lv, sid) for lv, d in fam["levels"].items() for sid in d["audio"].get("alarm_state_segments", []) if re.match(r"^kp\d", sid)]
    cks.append(chk("PNAP-8 KP segmentにアラーム受理が適用されていない(範囲外)", "NG" if kp_alarm else "OK", f"KP alarm segments={kp_alarm}"))
    cks.append(chk("PNAP-9 必須Regression/Validator/test", "MANUAL", "当日手順書の事前チェック"))
    return cks


def assess(report):
    """3件へのマッピング。family別の判定を集約する。"""
    out = {"KPFT": {}, "KP3V": {}, "PNAP": {}}
    ledger = report["shared"]["ledger_lookup"]
    sd = report["shared"].get("snapshot_diff")
    all_votes = {}
    for fk in ("X", "Z"):
        fam = report["families"].get(fk)
        if not fam or not fam.get("exists"):
            for k in out:
                out[k][fk] = [chk(f"{k}-ALL", "MISSING", f"{fk} run dirが存在しない")]
            continue
        out["KPFT"][fk] = evaluate_kpft(fam)
        c3, votes = evaluate_kp3v(fam)
        out["KP3V"][fk] = c3
        all_votes[fk] = votes
        out["PNAP"][fk] = evaluate_pnap(fam, sd, ledger, fam["pages"])
    # 合同判定(自然発火はX/Zのどちらかで観測できればKP3Vは足りる=設計§16-1 P-06。PNAPはユーザー原文§5-9によりX/Z双方)
    joint = {"KP3V": [], "PNAP": []}
    fired = {fk: any(v.get("whisper_called") for v in all_votes.get(fk, [])) for fk in ("X", "Z")}
    joint["KP3V"].append(chk("KP3V-J Whisper正式runtime発火(X/Zいずれか)", "OK" if any(fired.values()) else "NOT_FIRED",
                             f"X={fired['X']} Z={fired['Z']}。双方未発火なら『Xで発火観測+Z同adapterをtestで固定』は不成立→別素材で追加run(設計P-06)"))
    al = {fk: (report["families"][fk].get("alarms") or {}).get("total_alarms", 0) for fk in ("X", "Z") if report["families"][fk].get("exists")}
    joint["PNAP"].append(chk("PNAP-J アラーム発火(X・Z双方、PNAP原文§5-9)", "OK" if al.get("X") and al.get("Z") else "NOT_FIRED", f"alarms X={al.get('X')} Z={al.get('Z')}"))
    for k, v in joint.items():
        out[k]["JOINT"] = v
    report["vote_table"] = {fk: [{k: v for k, v in x.items() if k in ("level", "rank", "kind", "state", "row", "primary_pass", "secondary_pass", "whisper_called",
                                                                 "whisper_pass", "whisper_text", "whisper_error", "reused", "path", "source", "reason")}
                                 for x in vs] for fk, vs in all_votes.items()}
    return out


# ============================================================
# 旧識別子のDangling grep(KPFT-9 / KP3V旧判定残存)。read-only
# ============================================================
DANGLING_PATTERNS = {
    # KPFT設計§7 / KP3V設計§7 の撤去対象識別子(実装後に「0件」を受入条件にする)
    "KPFT: db_hybrid経路": r'kp_backend\s*=\s*"db_hybrid"|run_db_hybrid_selection|db_hybrid_with_fallback',
    "KPFT: m2_fallback": r"m2_fallback|strategy_l_fallback|build_m2_fallback_record|write_m2_fallback_notice",
    "KPFT: KP_ARTICLE_COST_CAP": r"KP_ARTICLE_COST_CAP",
    "KP3V: 旧dual識別子(撤去対象)": r"dual_pass_required|dual_required|NG_DUAL_PRIMARY|\+dual1|secondary_dual|KP_EN_PHRASE_DUAL",
    # KP3V設計§16-1 P-05: 保存容器名 kp_dual_check とtelemetry名(kp_dual_gate等)は**維持**(撤去対象でない)。件数は情報として出す
    "KP3V: 維持する容器名/telemetry名(情報。0件でなくてよい)": r"kp_dual_check|reuse_blocked_by_kp_dual_gate|kp_dual_gate|kp_dual_reuse_gate",
}
DANGLING_SCOPE = ("er019_*.py", "er026_*.py", "er062_*.py", "er063_*.py", "er003_v1_n3_01_scaffold*.py", "er078_*.py", "er006_secondary_asr_01.py", "er096_*.py")
DANGLING_EXCLUDE_TEST = re.compile(r"_test|test_")


def dangling_grep(repo_root):
    res = {}
    files = []
    for g in DANGLING_SCOPE:
        files.extend(glob.glob(os.path.join(repo_root, g)))
    files = sorted(set(files))
    for name, pat in DANGLING_PATTERNS.items():
        rx = re.compile(pat)
        hits_prod, hits_test = [], []
        for f in files:
            try:
                with open(f, encoding="utf-8", errors="replace") as fh:
                    for i, ln in enumerate(fh, start=1):
                        if rx.search(ln):
                            (hits_test if DANGLING_EXCLUDE_TEST.search(os.path.basename(f)) else hits_prod).append(f"{os.path.basename(f)}:{i}")
            except OSError:
                continue
        res[name] = {"production_hits": len(hits_prod), "test_hits": len(hits_test), "production_sample": hits_prod[:8]}
    return res


# ============================================================
# Markdown
# ============================================================
def render_markdown(rep):
    L = []
    A = L.append
    A("# 合同runtime evidence 集計(er106)")
    A(f"- schema: `{SCHEMA}` / generated_at: {rep['generated_at']}")
    A(f"- X run: `{rep['inputs']['x_run_dir']}` / Z run: `{rep['inputs']['z_run_dir']}`")
    A("- 状態語: OK / NG / MISSING(期待キー・成果物が無い=実装側の名称差または未配線。推測補完しない) / NOT_FIRED(自然発火せず) / MANUAL(機械判定不可) / INFO")
    for fk in ("X", "Z"):
        fam = rep["families"][fk]
        A(f"\n## Family {fk}: `{fam['run_dir']}` (levels={fam.get('levels_detected')})")
        if not fam.get("exists"):
            A("- run dirが存在しない")
            continue
        if fam.get("entry_point"):
            A(f"- entry_point: {json.dumps(fam['entry_point'], ensure_ascii=False)}")
        A("### (a) KP選定・件数")
        A("| level | n_items | backend(used) | model_id | prompt sha | sel/canon/red/outer | shortfall | 変更(原形化)件 | stale |")
        A("|---|---|---|---|---|---|---|---|---|")
        for lv, d in fam["levels"].items():
            s = d["selection"]
            A(f"| {lv} | {s['n_items']} | {s['kp_backend_used']} | {s['model_id']} | {str(s['prompt_sha256'])[:12]} | {s['selection_attempts']}/{s['canonicalization_attempts']}/{s['redundancy_attempts']}/{s['outer_retry_attempts']} | {s['shortfall']} | {sum(1 for r in s['items'] if r['changed'])} | {s['stale_files']} |")
        for lv, d in fam["levels"].items():
            for r in d["selection"]["items"]:
                A(f"- {lv}#{r['rank']}: span=`{r['source_span']}` used=`{r['used_form']}` (本文一致={r['span_in_article']}, 語数={r['words_span']}, gloss={r['has_gloss']}, reason={r['normalization_reason']})")
            if d["selection"]["metadata_missing_keys"]:
                A(f"- {lv} metadataの未存在キー: {d['selection']['metadata_missing_keys']}")
        A("### (b) KP音声の3-ASR投票")
        A("| level | rank | 記録種別 | state | row | P | S | W発火 | W | W error | reused |")
        A("|---|---|---|---|---|---|---|---|---|---|---|")
        for v in rep["vote_table"].get(fk, []):
            A(f"| {v.get('level')} | {v.get('rank')} | {v.get('kind')} | {v.get('state')} | {v.get('row')} | {v.get('primary_pass')} | {v.get('secondary_pass')} | {v.get('whisper_called')} | {v.get('whisper_pass')} | {v.get('whisper_error')} | {v.get('reused')} |")
        A("### (c) 固有名詞アラーム")
        for lv, r in fam["alarms"]["per_level"].items():
            A(f"- {lv}: json={r['alarms_json_present']} md={r['report_md_present']} count={r.get('count')} consistency={r.get('consistency')} hr_residual={r.get('hr_residual')} supply_applied={r.get('supply_applied_count')}")
            for a in r.get("alarm_records", []):
                A(f"  - {a['proper_noun']} @ {a['segment_id']}: state={a['final_state']} 供給={a['tts_supply_result']} 根拠={a['pronunciation_basis']}")
        A("### (d) 費用(JPY換算)")
        c = fam["cost"]
        A(f"- 出典: `{c.get('tool')}`(USD_JPY={c.get('usd_jpy')}、価格表 `{c.get('pricing_snapshot')}`、cost_usd優先→tokens×単価、synthetic行は除外{c.get('synthetic_skipped')}件)。Whisperはローカル=0円(ログ対象外)。logs={c.get('files')}")
        A(f"- 合計 **{c.get('total_jpy')}円** / KP関連(chain+音声) {c.get('kp_related_jpy')}円 (+未分離scaffold {c['buckets'].get('scaffold_llm_unsplit', {}).get('jpy', 0)}円を含めると {c.get('kp_related_incl_unsplit_scaffold_jpy')}円) / unpriced={c.get('unpriced')}")
        A("| bucket | 円 | calls |")
        A("|---|---|---|")
        for b, v in sorted(c["buckets"].items()):
            A(f"| {b} | {v['jpy']} | {v['calls']} |")
        A("| bucket:kind | 円 | calls |")
        A("|---|---|---|")
        for b, v in sorted(c["by_kind"].items()):
            A(f"| {b} | {v['jpy']} | {v['calls']} |")
        A("### (f) 試聴ページ・再生順")
        for p in fam["pages"]["checks"]:
            A(f"- page `{p['page']}`: 標準適合={p.get('standard_check_overall')} failed={p.get('standard_check_failed')} KP行={p.get('kp_rows')} アラーム語漏れ={p['alarm_words_leaked']}")
        if not fam["pages"]["checks"]:
            A("- pageが見つからない(--x-page/--z-pageで指定)")
        for lv, d in fam["levels"].items():
            A(f"- {lv} 再生順(間接: key_phrase_N長 >= 2*英+第3): " + ", ".join(f"kp{k}:{v['status']}" for k, v in d["order"]["per_kp"].items()) + f" (timeline={d['order']['timeline_present']})")
    A("\n## (e) STOP・HR・共有log")
    sh = rep["shared"]
    A(f"- STOPセンチネル(現在): {sh['stop_sentinels_now']}")
    if sh.get("stop_helper"):
        A(f"- stop_scope_check_01 rc: {sh['stop_helper']}")
    if sh.get("snapshot_diff"):
        A(f"- 前後差分: {json.dumps(sh['snapshot_diff'], ensure_ascii=False)}")
    else:
        A("- 前後差分: snapshot未指定")
    A(f"- Ledger対象語照合: {json.dumps(sh['ledger_lookup']['entries'], ensure_ascii=False)}")
    if rep.get("dangling_grep"):
        A("\n## Dangling Reference grep(Production .py、testは別掲)")
        for k, v in rep["dangling_grep"].items():
            A(f"- {k}: production={v['production_hits']} test={v['test_hits']} {v['production_sample']}")
    for feat, title in (("KPFT", "KPFT(KP全文選定+3件化) 確認項目"), ("KP3V", "KP3V(3-ASR多数決) 確認項目"), ("PNAP", "PNAP(固有名詞アラーム) 確認項目")):
        A(f"\n## {title}")
        A("| 項目 | X | Z | 根拠(X) / (Z) |")
        A("|---|---|---|---|")
        xs = {c["id"]: c for c in rep["assessment"][feat].get("X", [])}
        zs = {c["id"]: c for c in rep["assessment"][feat].get("Z", [])}
        for cid in list(dict.fromkeys(list(xs) + list(zs))):
            x, z = xs.get(cid), zs.get(cid)
            A(f"| {cid} | {x['status'] if x else '-'} | {z['status'] if z else '-'} | {(x or {}).get('detail', '')[:180]} / {(z or {}).get('detail', '')[:180]} |".replace("\n", " "))
        for c in rep["assessment"][feat].get("JOINT", []):
            A(f"| {c['id']} | (合同) | (合同) | {c['status']}: {c['detail'][:200]} |".replace("\n", " "))
    A("\n## 総括")
    for k, v in rep["summary"].items():
        A(f"- {k}: {v}")
    return "\n".join(L) + "\n"


def summarize(assessment):
    out = {}
    for feat, d in assessment.items():
        cnt = {}
        for fk, cks in d.items():
            for c in cks:
                cnt[c["status"]] = cnt.get(c["status"], 0) + 1
        out[feat] = cnt
    return out


# ============================================================
# main
# ============================================================
def build_report(args):
    repo = args.repo_root
    run_dirs = [d for d in (args.x_run_dir, args.z_run_dir) if d]
    rep = {"schema": SCHEMA, "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
           "inputs": {"x_run_dir": args.x_run_dir, "z_run_dir": args.z_run_dir, "x_source_dir": args.x_source_dir},
           "families": {}, "shared": {}}
    rep["families"]["X"] = collect_family(repo, "X", args.x_run_dir, args.x_source_dir, args.x_page) if args.x_run_dir else {"family": "X", "exists": False, "run_dir": None}
    rep["families"]["Z"] = collect_family(repo, "Z", args.z_run_dir, None, args.z_page) if args.z_run_dir else {"family": "Z", "exists": False, "run_dir": None}
    nouns = sorted({a["proper_noun"] for fk in ("X", "Z") for r in (rep["families"][fk].get("alarms") or {"per_level": {}})["per_level"].values()
                    for a in r.get("alarm_records", []) if a.get("proper_noun")})
    rep["shared"]["ledger_lookup"] = ledger_lookup(repo, nouns, args.ledger)
    rep["shared"]["stop_sentinels_now"] = stop_sentinels(repo, run_dirs)
    if args.check_stop and run_dirs:
        outp = os.path.join(os.path.dirname(os.path.abspath(args.out_json or "er106_stop.json")), "er106_stop_check.json")
        rep["shared"]["stop_helper"] = run_stop_helper(repo, run_dirs[0], args.managed_id, outp)
    if args.snapshot_in:
        snap, _ = jload(args.snapshot_in)
        rep["shared"]["snapshot_diff"] = compare_snapshot(repo, snap, run_dirs) if snap else None
    if args.dangling_grep:
        rep["dangling_grep"] = dangling_grep(repo)
    rep["assessment"] = assess(rep)
    rep["summary"] = summarize(rep["assessment"])
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser(description="合同runtime evidence集計(read-only、API 0)")
    ap.add_argument("--x-run-dir")
    ap.add_argument("--z-run-dir")
    ap.add_argument("--x-source-dir", help="Xの入力記事dir(er019_output/<slug>/<run>)。KP本文一致検査用。省略時はentry_point.source_dir")
    ap.add_argument("--x-page")
    ap.add_argument("--z-page")
    ap.add_argument("--ledger", help="Ledger path(省略時 er006_output/pronunciation_ledger_01/ledger.json)")
    ap.add_argument("--repo-root", default=REPO_ROOT)
    ap.add_argument("--snapshot-out", help="実行前の共有log/Ledger/STOP状態を保存して終了")
    ap.add_argument("--snapshot-in", help="実行前snapshotとの差分を集計に含める")
    ap.add_argument("--check-stop", action="store_true", help="tools/stop_scope_check_01.py を実行しrcを記録")
    ap.add_argument("--managed-id", default="JOINT-RUNTIME-EVIDENCE-01")
    ap.add_argument("--dangling-grep", action="store_true")
    ap.add_argument("--out-json")
    ap.add_argument("--out-md")
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    run_dirs = [d for d in (args.x_run_dir, args.z_run_dir) if d]
    if args.snapshot_out:
        snap = take_snapshot(args.repo_root, run_dirs)
        os.makedirs(os.path.dirname(os.path.abspath(args.snapshot_out)), exist_ok=True)
        with open(args.snapshot_out, "w", encoding="utf-8") as f:
            json.dump(snap, f, ensure_ascii=False, indent=2)
        print(f"snapshot saved: {args.snapshot_out}")
        return 0
    rep = build_report(args)
    md = render_markdown(rep)
    if args.out_json:
        os.makedirs(os.path.dirname(os.path.abspath(args.out_json)), exist_ok=True)
        with open(args.out_json, "w", encoding="utf-8") as f:
            json.dump(rep, f, ensure_ascii=False, indent=2, default=str)
    if args.out_md:
        os.makedirs(os.path.dirname(os.path.abspath(args.out_md)), exist_ok=True)
        with open(args.out_md, "w", encoding="utf-8") as f:
            f.write(md)
    print(md if not args.out_md else f"summary: {json.dumps(rep['summary'], ensure_ascii=False)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
