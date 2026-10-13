# -*- coding: utf-8 -*-
"""ASR-M1-OOV-MULTI-PRONUNCIATION-PRODUCTION-01 委任_02: Melos 短 clip の runtime evidence runner(作成のみ。実行は委任_03)。

目的: M1 配線(委任_03)後に、Production cascade 経路(secondary_asr.evaluate_attempt_with_cascade_detail)を実音声で通し、
M1_MULTI_CANDIDATE_ACCEPT の実機挙動と誤PASS抑止(非歯擦音文脈・同語反復・否定/数値)を確認する。
OF-186: 共有状態の完全隔離。
  * HR queue / attempt_history / master_audio_store(manifest, audio, reuse_telemetry) / er021 telemetry / er025 telemetry /
    cost log の出力先を er077_output/m1_oov_multi_pronunciation_01/evidence_01/ 配下へ差し替える。
  * Pronunciation Ledger は snapshot コピーを読取専用で使う(upsert は no-op、Tier3 research は無効化=API 0 + Ledger 不変)。
  * run 前後で本番 Ledger と共有 state ファイルの md5 を記録し、不変を確認する。
  * 既存 Production file は編集しない(この runner が実行時に module 変数を差し替えるだけ)。
安全: 既定は --dry-run(API 0、隔離の検証と plan 出力のみ)。有料実行は --execute --budget-jpy N を明示した場合のみ。
STOP 確認(docs/pm/delegation_log/*STOP_NOTICE* / <out>/STOP / er026_output/family_z_production_e2e_01/STOP_ALL)。
監督ループ・自動再試行なし。技術失敗(TTS 例外)は 1 clip につき 1 回まで。外部プロセスを再起動しない。
コマンド(委任_03):
  .venv\\Scripts\\python.exe er077_m1_oov_multi_pronunciation_01_evidence_runner.py --dry-run
  .venv\\Scripts\\python.exe er077_m1_oov_multi_pronunciation_01_evidence_runner.py --execute --budget-jpy 10
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import shutil
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

OUT = "er077_output/m1_oov_multi_pronunciation_01/evidence_01"
PROD_LEDGER = "er006_output/pronunciation_ledger_01/ledger.json"
SHARED_STATE = [
    "er005_output/cost_baseline_01/cost_summary.json",
    "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl",
    "er006_output/master_audio_store_01/manifest.json",
    "er006_output/master_audio_store_01/reuse_telemetry.jsonl",
    PROD_LEDGER,
    "er011_output/attempt_history.jsonl",
    "er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl",
    "er025_output/pronunciation_resolution_core_telemetry_01/telemetry.jsonl",
]
STOP_GLOBS = ["docs/pm/delegation_log/*STOP_NOTICE*", OUT + "/STOP", "er026_output/family_z_production_e2e_01/STOP_ALL"]

# clip 構成(OF-186)。existing_wav: er069 の既存 12-take(ASR+cascade のみ再実行=TTS 不要)。new: 新規 TTS(Std 3 take ずつ)。
EXISTING_MELOS_SAID = "er069_output/attribution_clip_split_trial_01/results_02.json"  # name=Melos/verb=said の 12 行(wav は gen/gen02 配下)
NEW_CLIPS = [
    ("nonsib_left", "Melos left.", "非歯擦音文脈(次語が歯擦音でない): F1 explained 不成立 → 非PASS 維持が期待"),
    ("nonsib_ran", "Melos ran.", "同上(第2語)"),
    ("repeat", "Melos said Melos left.", "同語反復(2 出現のうち 2 つ目が非歯擦音文脈): 非PASS 維持が期待"),
    ("neg_num", "Melos did not wait five days.", "否定・数値を含む文: M1 が成立しても否定/数値の差分は非PASS が期待"),
]
TAKES = 3
EST_JPY_PER_OBSERVATION = 0.137  # 出典: er069_output/attribution_clip_split_trial_01/cost_02.json(1観測=TTS+ASR の実績平均)


def stop_present() -> list:
    return [p for g in STOP_GLOBS for p in glob.glob(g)]


def md5(p: str):
    return hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None


def snapshot_state() -> dict:
    return {p: md5(p) for p in SHARED_STATE}


def plan(n_existing: int = 12) -> dict:
    new = [{"id": f"{k}_t{t}", "text": text, "take": t, "purpose": why, "tts": True} for k, text, why in NEW_CLIPS for t in range(1, TAKES + 1)]
    n_obs = n_existing + len(new)
    return {"existing_wav_reasr": n_existing, "new_tts_clips": new, "n_observations": n_obs,
            "estimated_jpy": round(n_obs * EST_JPY_PER_OBSERVATION, 2),
            "estimate_basis": "er069 実績 1観測≈¥0.137(cost_02.json)×観測数。既存12件は TTS 不要のため実際はこれ以下"}


def apply_isolation(out_dir: str) -> dict:
    """共有状態の出力先を out_dir 配下へ差し替える(module 変数のみ。Production file 無編集)。差し替え結果を返す。"""
    os.makedirs(out_dir, exist_ok=True)
    mapping = {}
    import er005_cost_logger as cl
    import er006_secondary_asr_01 as sec
    import er006_master_audio_store_01 as store
    import er006_pronunciation_ledger_01 as ledger_mod
    import er006_pronunciation_research_01 as research
    import er011_human_review_lock_01 as lock
    import er021_en_asr_semantic_equivalence_production_01 as semeq
    import er025_entity_pronunciation_resolver_core_01 as er025

    sec.HUMAN_REVIEW_LOG_PATH = f"{out_dir}/human_review_queue.jsonl"
    lock.ATTEMPT_HISTORY_PATH = f"{out_dir}/attempt_history.jsonl"
    store.STORE_DIR = f"{out_dir}/master_audio_store"
    store.AUDIO_DIR = f"{store.STORE_DIR}/audio"
    store.MANIFEST_PATH = f"{store.STORE_DIR}/manifest.json"
    store.TELEMETRY_PATH = f"{store.STORE_DIR}/reuse_telemetry.jsonl"
    er025.TELEMETRY_PATH = f"{out_dir}/er025_telemetry.jsonl"
    iso_sem = f"{out_dir}/er021_telemetry.jsonl"
    _orig_append = semeq.append_telemetry_log
    semeq.append_telemetry_log = lambda record, path=iso_sem: _orig_append(record, path=iso_sem)  # 既定引数は def 時に束縛済みのため関数ごと包む
    cl.init_logger(f"{out_dir}/cost_log.jsonl")
    # Ledger: snapshot コピーを読取専用で使う。upsert は no-op、Tier3 research は無効化(API 0・Ledger 不変)
    snap = f"{out_dir}/ledger_snapshot.json"
    shutil.copyfile(PROD_LEDGER, snap)
    ledger_mod.LEDGER_PATH = snap
    ledger_mod.upsert = lambda key, entry: "TIER3_WRITE_DISABLED_EVIDENCE_RUN"
    research.research_pronunciations = lambda entities, *a, **k: {"status": "DISABLED_EVIDENCE_RUN"}
    mapping.update({"human_review_queue": sec.HUMAN_REVIEW_LOG_PATH, "attempt_history": lock.ATTEMPT_HISTORY_PATH,
                    "master_audio_store": store.STORE_DIR, "reuse_telemetry": store.TELEMETRY_PATH, "er021_telemetry": iso_sem,
                    "er025_telemetry": er025.TELEMETRY_PATH, "cost_log": f"{out_dir}/cost_log.jsonl", "ledger_snapshot": snap,
                    "tier3_research": "disabled(stub)", "ledger_upsert": "disabled(no-op)"})
    assert all(str(v).replace("\\", "/").startswith(out_dir) or v.startswith("disabled") for v in mapping.values()), mapping
    return mapping


def run_clip(rec: dict, out_dir: str) -> dict:  # pragma: no cover  (有料。委任_03 で実行)
    """1 観測: (必要なら TTS)→ Production primary ASR(routing.transcribe)→ evaluate_attempt_with_cascade_detail。
    secondary(Azure)転写は cascade 内で取得される。M1 が配線済みなら detail に m1 audit が入る。"""
    import er006_asr_provider_routing_01 as routing
    import er006_pronunciation_ledger_01 as ledger_mod
    import er006_secondary_asr_01 as sec
    text, wav = rec["text"], rec["wav"]
    asr_text, err = routing.transcribe(wav, language="en-US")
    phrases = [h["canonical_spelling"] for h in ledger_mod.get_hint_for_text(text, min_confidence="low")]
    detail = sec.evaluate_attempt_with_cascade_detail(text, asr_text, [], wav, language="en-US", ledger_phrases=phrases,
                                                      cascade_enabled=True, segment_id=rec.get("segment_id", "full_story_part1"))
    cls = detail.get("classification")
    return {"id": rec["id"], "text": text, "primary_asr": asr_text, "asr_err": err, "verified": detail.get("verified"),
            "final_status": detail.get("final_status"), "classification": getattr(cls, "classification", None),
            "m1_audit": detail.get("m1_multi_candidate") or detail.get("m1_audit"),  # 委任_03 配線時のキー名に合わせる
            "steps": detail.get("steps")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="既定。API 0。隔離適用と plan 出力のみ")
    ap.add_argument("--execute", action="store_true", help="有料 API を実行(委任_03 のみ)")
    ap.add_argument("--budget-jpy", type=float, default=0.0)
    a = ap.parse_args()
    os.chdir(ROOT)
    hit = stop_present()
    # 旧 STOP_NOTICE(過去事故の記録)も存在確認の対象。存在した場合は新規 API 呼出をしない(dry-run は可)
    p = plan()
    before = snapshot_state()
    iso = apply_isolation(OUT)
    result = {"mode": "execute" if a.execute else "dry-run", "stop_files_present": hit, "plan": p, "isolation": iso,
              "state_md5_before": before, "started_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    if a.execute:
        if hit:
            result["aborted"] = "STOP present: no API call"
        elif a.budget_jpy <= 0 or p["estimated_jpy"] > a.budget_jpy:
            result["aborted"] = f"budget {a.budget_jpy} < estimate {p['estimated_jpy']}"
        else:
            result["aborted"] = "execute body is run by 委任_03 after M1 wiring (clips wav generation + run_clip loop)"  # 配線前に有料実行しない
    after = snapshot_state()
    result["state_md5_after"] = after
    result["shared_state_unchanged"] = before == after
    json.dump(result, open(f"{OUT}/runner_{result['mode']}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: result[k] for k in ("mode", "stop_files_present", "shared_state_unchanged")}, ensure_ascii=False),
          "estimate_jpy", p["estimated_jpy"], "n_obs", p["n_observations"])


if __name__ == "__main__":
    main()
