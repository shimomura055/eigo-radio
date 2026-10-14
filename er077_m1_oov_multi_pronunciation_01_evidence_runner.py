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
# STOP判定は共通helper(STOP_NOTICE適用範囲規則、STOP-NOTICE-SCOPE-RULE-PRODUCTION-01、ユーザー2026-10-14案a承認)。
# STOP_ALL・自run STOP・RESTART_STORM/RUN_LOCK・自ID宛/全体scope/parse不能(fail-closed)のNOTICEは引き続き停止。
# 他管理IDの「限定run」NOTICEだけが非適用(根拠はhelperの判定JSONに記録)。
MANAGED_IDS = ["ASR-M1-OOV-MULTI-PRONUNCIATION-PRODUCTION-01", "STOP-NOTICE-SCOPE-RULE-PRODUCTION-01"]
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stop_scope_check_01 as _stop_scope  # noqa: E402

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
    r = _stop_scope.check(MANAGED_IDS, os.path.join(ROOT, OUT))
    return [f"{a['kind']}:{a['path']}" for a in r["applicable"]]


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
                                                      cascade_enabled=True, segment_id=rec["segment_id"])
    cls = detail.get("classification")
    return {"id": rec["id"], "text": text, "primary_asr": asr_text, "asr_err": err, "verified": detail.get("verified"),
            "final_status": detail.get("final_status"), "classification": getattr(cls, "classification", None),
            "segment_id": rec["segment_id"],
            "m1_audit": detail.get("m1_multi_candidate"), "m1_rejected": detail.get("m1_multi_candidate_rejected"),
            "human_review_required": detail.get("human_review_required"), "cascade_invoked": detail.get("cascade_invoked"),
            "steps": [{k: v for k, v in st.items() if k not in ("entity_like_source",)} for st in (detail.get("steps") or [])]}



EXISTING_DIR = "er069_output/attribution_clip_split_trial_01/gen02/wav"
EXISTING_IDS = ([f"Melos_said_L2_adv_t{t}_raw" for t in (1, 2, 3, 4)]
                + [f"Melos_said_L2_std_t{t}_{v}" for t in (1, 2, 3, 4) for v in ("raw", "slow6")])
AZURE_JPY_PER_S = 0.0444   # er069 cost_02: 0.08711 JPY / 1.96 s
OPENAI_JPY_PER_CALL = 0.0094
HARD_STOP_JPY = 6.0


class Meter:
    """ASR呼出の実費概算(Azure=秒単価, OpenAI=1call単価)。TTSはgen.runが返す実費を加算。"""
    def __init__(self):
        self.asr_jpy = 0.0
        self.tts_jpy = 0.0
        self.n_openai = 0
        self.n_azure = 0

    @property
    def total(self):
        return self.asr_jpy + self.tts_jpy


def install_meter(meter: Meter):
    import wave
    import er006_asr_provider_routing_01 as routing
    import er006_secondary_asr_01 as sec
    _t, _az = routing.transcribe, sec.get_full_text_via_azure_stt_with_phrase_list

    def dur(wav):
        try:
            with wave.open(wav, "rb") as w:
                return w.getnframes() / float(w.getframerate())
        except Exception:
            return 3.0

    def t_wrap(wav_path, *a, **k):
        if meter.total > HARD_STOP_JPY:
            raise RuntimeError("[STOP] hard stop budget exceeded")
        meter.n_openai += 1
        meter.asr_jpy += OPENAI_JPY_PER_CALL
        return _t(wav_path, *a, **k)

    def az_wrap(wav_path, *a, **k):
        if meter.total > HARD_STOP_JPY:
            raise RuntimeError("[STOP] hard stop budget exceeded")
        meter.n_azure += 1
        meter.asr_jpy += AZURE_JPY_PER_S * dur(wav_path)
        return _az(wav_path, *a, **k)

    routing.transcribe = t_wrap
    sec.get_full_text_via_azure_stt_with_phrase_list = az_wrap


def execute(out_dir: str, budget: float, result: dict) -> None:  # pragma: no cover  (有料)
    import er006_secondary_asr_01 as sec
    meter = Meter()
    install_meter(meter)
    rows = []
    state = {"soft_stop": False}

    def one(rec):
        if stop_present():
            state["soft_stop"] = True
            return
        if meter.total > budget:
            state["soft_stop"] = True
            result.setdefault("budget_stops", []).append(rec["id"])
            return
        sec._reset_m1_freeze_cache()  # 1 clip = 1 segment の初回試行を再現
        r = run_clip(rec, out_dir)
        fz = sec._M1_FROZEN_CACHE.get(rec["text"])
        r["frozen_hash"] = getattr(fz, "candidate_set_hash", None)
        r["source"] = rec.get("source")
        r["wav"] = rec["wav"]
        r["meter_total_jpy"] = round(meter.total, 4)
        rows.append(r)
        json.dump(rows, open(f"{out_dir}/clip_results.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # 1) 既存12-take(wav再利用=TTS 0): segment_id=full_story_part1相当
    for i in EXISTING_IDS:
        one({"id": i, "text": "Melos said.", "wav": f"{EXISTING_DIR}/{i}.wav", "segment_id": "full_story_part1", "source": "existing_er069"})
    # 2) 同12-take: segment_id=None相当(dialogue/point_headings相当=Tier3不発、M1はP1で完結しAzure不要)
    for i in EXISTING_IDS:
        one({"id": i + "__segNone", "text": "Melos said.", "wav": f"{EXISTING_DIR}/{i}.wav", "segment_id": None, "source": "existing_er069"})
    # 3) 新規 4文x3take(TTS Aoede, er069と同条件=Std style)
    import er069_attribution_clip_split_trial_01_gen as gen
    import er063_family_z_audio_01 as Z
    import er057_tone_trial_final_build_03 as B
    styles = {"std": Z.FAMILY_Z_ROLE_STYLE["NARRATOR_FULL_STORY_STD"]["text"]}
    call = B.make_tts_call()
    gen_out = f"{out_dir}/gen"
    os.makedirs(f"{gen_out}/wav", exist_ok=True)
    log_path = f"{gen_out}/generation_log.jsonl"
    stopflag = {"stop": False}
    for key, text, why in NEW_CLIPS:
        for t in range(1, TAKES + 1):
            jid = f"{key}_t{t}"
            if state["soft_stop"] or stop_present():
                break
            if meter.total > budget:
                state["soft_stop"] = True
                result.setdefault("budget_stops", []).append(jid)
                break
            task = {"id": jid, "name": "Melos", "boundary": "n/a", "length": "L2", "level": "std", "take": t, "text": text}
            g = gen.run(task, call, gen_out, HARD_STOP_JPY, styles, log_path, stopflag)
            if g.get("status") != "OK":
                result.setdefault("tts_failures", []).append(g)
                continue
            meter.tts_jpy += g.get("jpy", 0.0)
            one({"id": jid, "text": text, "wav": f"{gen_out}/wav/{jid}_raw.wav", "segment_id": "full_story_part1",
                 "source": "new_tts", "purpose": why})
    tts_models = set()
    if os.path.exists(log_path):
        for l in open(log_path, encoding="utf-8"):
            tts_models.add(json.loads(l).get("model_version"))
    result.update({"rows": rows,
                   "cost": {"asr_jpy": round(meter.asr_jpy, 4), "tts_jpy": round(meter.tts_jpy, 4), "total_jpy": round(meter.total, 4),
                            "n_openai_asr_calls": meter.n_openai, "n_azure_calls": meter.n_azure, "budget_jpy": budget,
                            "basis": "Azure 0.0444 JPY/s, OpenAI 0.0094 JPY/call, TTS=gen.run実測(トークン単価)"},
                   "models": {"primary_asr": "gpt-4o-mini-transcribe", "secondary_asr": "azure_speech(phrase list)",
                              "tts_model_version": sorted(x for x in tts_models if x), "tts_voice": "Aoede"},
                   "soft_stop": state["soft_stop"]})
    json.dump({"total_jpy": round(meter.total, 4), "asr_jpy": round(meter.asr_jpy, 4), "tts_jpy": round(meter.tts_jpy, 4),
               "n_observations": len(rows), "n_azure_calls": meter.n_azure, "n_openai_asr_calls": meter.n_openai,
               "budget_jpy": budget, "hard_stop_jpy": HARD_STOP_JPY},
              open(f"{out_dir}/cost_01.json", "w", encoding="utf-8"), indent=1)


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
            execute(OUT, a.budget_jpy, result)
    after = snapshot_state()
    result["state_md5_after"] = after
    result["shared_state_unchanged"] = before == after
    json.dump(result, open(f"{OUT}/runner_{result['mode']}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: result[k] for k in ("mode", "stop_files_present", "shared_state_unchanged")}, ensure_ascii=False),
          "estimate_jpy", p["estimated_jpy"], "n_obs", p["n_observations"])


if __name__ == "__main__":
    main()
