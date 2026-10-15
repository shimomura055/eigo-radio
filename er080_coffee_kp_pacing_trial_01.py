# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-KP-EN-EXPLANATION-PACING-TRIAL-01 Trial専用harness(Production非経由の隔離実行)。

対象: Coffee Advanced Key Phrase英語解説5本 x 固定8 Prompt(P0..P7) = 40 clip。
方式: Production leaf `er019_family_x_audio_production_runner_01.generate_key_phrase_explanation_en_verified`
      (内部=repro01.generate_narration_snippet_verified_strict: TTS gemini-3.8-flash-lite-tts / Aoede / speech_metadata_flash_lite /
       trim margin 0.30 / Primary ASR+統一judge+Secondary cascade / disfluency QA / max_attempts=KP_EXPLANATION_MAX_ATTEMPTS=3)
      をStyle文字列(style_prefix_override)だけ差し替えて呼ぶ。原稿は現行Production正本(tts_generation_results.json、read-only)から取得。
隔離: 書込先は全てTrial dir。Production共有の HR queue / semantic telemetry / pronunciation ledger はモジュール変数を
      Trial dir内のコピーへ差し替える(ledgerは読み取り内容を保つためコピー)。実行前後で共有state sha256を記録。
禁止: 追加Take・再Trial・不合格clipの救済(同clipは1回のみ呼ぶ。resume時も完了済みclipは再生成しない)。
Trial結果はProduction採用ではない。Coffee現行Prompt/style profileは変更しない。
"""
import argparse, glob, hashlib, json, os, shutil, sys, time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

PROD_RES = "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01/b1b/audit/tts_generation_results.json"
PROD_STYLE_PROFILE = "coffee_n01_r2_p3_e1"
MODEL_EXPECTED = "gemini-3.8-flash-lite-tts"
VOICE_EXPECTED = "Aoede"
BACKEND = "speech_metadata_flash_lite"

# ユーザー指示(2026-10-16)の8案をそのまま固定(Claude/Fableの判断で改変・追加しない)。(狙い, Style文字列)
PROMPTS = {
    "p0": ("現行Production", "clear, precise, at a measured pace, without dragging Let the sentence flow from its first word to its last, without stopping partway through."),
    "p1": ("最小変更・ポーズ調整", "clear, precise, at a measured pace, without dragging Keep pauses between phrases brief and natural, letting the explanation flow smoothly."),
    "p2": ("ややゆっくりを明示", "Clear and precise, at a slightly slower than conversational pace. Keep the explanation flowing naturally, with brief pauses."),
    "p3": ("語句の連結重視", "Clear, precise, at a measured pace, without dragging. Connect the words and phrases naturally, with no unnecessary breaks."),
    "p4": ("自然な英語教師の説明", "Explain clearly and naturally, like a patient English teacher speaking to a learner. Use a slightly relaxed pace and smooth phrasing."),
    "p5": ("理解に必要な短い間だけを許容", "Clear and easy to follow, at a gently measured pace. Use only short, natural pauses where they help understanding."),
    "p6": ("一文としての滑らかさ", "Clear, precise, and gently paced. Deliver the explanation as one smooth, connected thought, without stretching the spaces between phrases."),
    "p7": ("速度・リズムのバランス型", "Speak clearly at a slightly relaxed, natural pace. Keep a steady rhythm, with brief transitions between phrases and no drawn-out pauses."),
}

# 単価(出典 er058_output/unified_all_roles_production_wiring_01/RUNTIME_EVIDENCE_06.md:113): TTS 1clip JPY0.062 / OpenAI ASR 1call JPY0.0094 / Azure JPY0.0444/s
TTS_JPY, OPENAI_JPY, AZURE_JPY_PER_S = 0.062, 0.0094, 0.0444

SHARED = ["er006_output/master_audio_store_01/manifest.json", "er006_output/master_audio_store_01/reuse_telemetry.jsonl",
          "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl", "er007_output/ja_asr_cascade_01/human_review_queue.jsonl",
          "er006_output/pronunciation_ledger_01/ledger.json", "er011_output/attempt_history.jsonl",
          "er005_output/cost_baseline_01/cost_summary.json"]
SHARED_GLOBS = ["er021_output/**/telemetry.jsonl", "er025_output/**/telemetry.jsonl", "er030_output/**/telemetry.jsonl",
                "er011_output/local_rewrite_recovery/**/*"]


def sha_b(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def sha_s(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def shared_sha(out, tag):
    d = {}
    for p in SHARED:
        d[p] = sha_b(p) if os.path.isfile(p) else None
    for g in SHARED_GLOBS:
        for fp in sorted(glob.glob(g, recursive=True)):
            if os.path.isfile(fp):
                d[fp.replace("\\", "/")] = sha_b(fp)
    os.makedirs(f"{out}/audit", exist_ok=True)
    json.dump(d, open(f"{out}/audit/shared_state_sha_{tag}.json", "w", encoding="utf-8"), indent=1)
    return d


def load_scripts():
    d = json.load(open(PROD_RES, encoding="utf-8"))
    rows = []
    for k in sorted(d["key_phrases"], key=int):
        kp = d["key_phrases"][k]
        e = kp["explanation"]
        rows.append({"kp": int(k), "phrase": kp["english"].get("canonical_text"), "text": e["explanation_text"],
                     "prod_wav": e["path"], "prod_style_prefix": e.get("style_prefix"), "prod_duration_s": e.get("duration_seconds"),
                     "prod_asr_text": e.get("asr_text")})
    return rows


def verify_prod_style():
    """Productionで実際に送信されるStyle(style profile解決関数)とユーザー指定P0の照合(API 0)。"""
    import er019_family_x_style_profile_01 as sp
    import er033_tts_flash_lite_family_x_styles_01 as fl
    base = lambda _r: fl.KEY_PHRASE_EXPLANATION_EN
    resolved = sp.resolve_role_style(PROD_STYLE_PROFILE, sp.ROLE_KP_EXPLANATION_EN, "b1b", base)
    return {"resolved_by_production_function": resolved, "p0_user": PROMPTS["p0"][1], "identical": resolved == PROMPTS["p0"][1],
            "sha256_resolved": sha_s(resolved), "sha256_p0_user": sha_s(PROMPTS["p0"][1]), "p3_sha_in_profile": sp.P3_SHA256,
            "model_const": fl.FAMILY_X_FLASH_LITE_MODEL_NAME}


def isolate_shared_state(out):
    """HR queue / semantic telemetry / pronunciation ledger の書込先をTrial dir内へ差し替える(Production共有fileへ書かない)。"""
    import er006_secondary_asr_01 as sec
    import er021_en_asr_semantic_equivalence_production_01 as sem
    import er006_pronunciation_ledger_01 as led
    iso = f"{out}/audit/isolated_state"
    os.makedirs(iso, exist_ok=True)
    sec.HUMAN_REVIEW_LOG_PATH = f"{iso}/human_review_queue.jsonl"
    tel = f"{iso}/semantic_telemetry.jsonl"
    sem.append_telemetry_log.__defaults__ = (tel,)
    sem.TELEMETRY_LOG_PATH = tel
    iso_led = f"{iso}/ledger.json"
    if os.path.isfile(led.LEDGER_PATH) and not os.path.isfile(iso_led):
        shutil.copyfile(led.LEDGER_PATH, iso_led)
    led.LEDGER_PATH = iso_led
    return iso


def est_attempt_cost(att):
    c = TTS_JPY + OPENAI_JPY
    if "azure" in json.dumps(att.get("cascade_steps") or [], default=str).lower():
        c += AZURE_JPY_PER_S * float(att.get("duration_seconds") or 5.0)
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt-set", default="all")
    ap.add_argument("--out", required=True)
    ap.add_argument("--budget-jpy", type=float, default=40.0)
    ap.add_argument("--execute", action="store_true")
    a = ap.parse_args()
    out = a.out.replace("\\", "/").rstrip("/")
    sets = list(PROMPTS) if a.prompt_set == "all" else [a.prompt_set]
    assert all(s in PROMPTS for s in sets), sets
    rows = load_scripts()
    chk = verify_prod_style()
    os.makedirs(f"{out}/audit", exist_ok=True)
    json.dump({"style_check": chk, "texts": rows, "prompts": {k: {"aim": v[0], "style": v[1], "sha256": sha_s(v[1]), "len": len(v[1])} for k, v in PROMPTS.items()}},
              open(f"{out}/audit/plan.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("P0==Production resolved style:", chk["identical"], "| clips planned:", len(sets) * len(rows))
    if not a.execute:
        print("dry-run (API 0). --execute で有料生成。")
        return 0
    assert os.environ.get("TTS_EXECUTION_MODE") == "STANDARD", "TTS_EXECUTION_MODE=STANDARD を明示してください(T-2)"
    assert chk["identical"], "P0とProduction実送信Styleが不一致(差分は記録済み)。Fableへ報告"
    assert chk["model_const"] == MODEL_EXPECTED
    before = shared_sha(out, "before")
    iso = isolate_shared_state(out)
    import er019_family_x_audio_production_runner_01 as X
    import er078_secondary_run_scope_01 as scope
    log_path = f"{out}/audit/clip_results.jsonl"
    done = {}
    if os.path.isfile(log_path):
        for ln in open(log_path, encoding="utf-8"):
            r = json.loads(ln)
            if r.get("status") != "EXCEPTION":
                done[(r["prompt"], r["kp"])] = r
    spent = sum(r.get("est_cost_jpy", 0) for r in done.values())
    calls = {"tts": sum(r.get("attempts", 0) for r in done.values())}
    stop = {"reason": None}

    @scope.with_secondary_run
    def run_all():
        nonlocal spent
        for p in sets:
            for row in rows:
                key = (p, row["kp"])
                if key in done:
                    continue
                for sp_ in (f"{out}/STOP", "er026_output/family_z_production_e2e_01/STOP_ALL"):
                    if os.path.exists(sp_):
                        stop["reason"] = f"STOP sentinel: {sp_}"
                        return
                if spent > a.budget_jpy:
                    stop["reason"] = f"budget guard: est {spent:.3f} > {a.budget_jpy}"
                    return
                wav = f"{out}/work/{p}/b1b/narration/kp{row['kp']}_explanation_en.wav"
                os.makedirs(os.path.dirname(wav), exist_ok=True)
                t0 = time.time()
                try:
                    r = X.generate_key_phrase_explanation_en_verified(row["text"], wav, style_prefix_override=PROMPTS[p][1], tts_backend=BACKEND)
                except Exception as e:  # TTS/ASR技術障害: 再試行せずSTOP(t2)
                    rec = {"prompt": p, "kp": row["kp"], "status": "EXCEPTION", "error": f"{type(e).__name__}: {str(e)[:300]}", "attempts": 0, "est_cost_jpy": 0}
                    open(log_path, "a", encoding="utf-8").write(json.dumps(rec, ensure_ascii=False) + "\n")
                    stop["reason"] = "EXCEPTION(t2): " + rec["error"]
                    return
                logs = r.get("attempts_log") or []
                cost = sum(est_attempt_cost(x) for x in logs) if logs else TTS_JPY
                spent += cost
                calls["tts"] += max(len(logs), 1)
                ok = r.get("status") == "OK" and r.get("asr_verified")
                dst = None
                if ok:
                    dst = f"{out}/audio/{p}/kp{row['kp']:02d}.wav"
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copyfile(wav, dst)
                rec = {"prompt": p, "kp": row["kp"], "status": r.get("status"), "asr_verified": bool(r.get("asr_verified")),
                       "audio": dst, "attempts": len(logs), "est_cost_jpy": round(cost, 4), "elapsed_s": round(time.time() - t0, 1),
                       "asr_text": r.get("asr_text"), "audio_classification": r.get("audio_classification"),
                       "duration_seconds": r.get("duration_seconds"), "style_sha256": sha_s(PROMPTS[p][1]),
                       "asr_judgement": r.get("asr_judgement"), "attempts_log": logs, "reason": r.get("reason"),
                       "human_review_required": bool(r.get("human_review_required"))}
                open(log_path, "a", encoding="utf-8").write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
                done[key] = rec
                print(f"[{p} kp{row['kp']}] {rec['status']} verified={rec['asr_verified']} attempts={rec['attempts']} dur={rec['duration_seconds']} est_jpy={cost:.3f} total={spent:.3f}", flush=True)

    run_all()
    after = shared_sha(out, "after")
    diff = {k: (before.get(k), after.get(k)) for k in set(before) | set(after) if before.get(k) != after.get(k)}
    summary = {"clips_done": len(done), "ok": sum(1 for r in done.values() if r.get("asr_verified")), "est_cost_jpy": round(spent, 4),
               "tts_calls_est": calls["tts"], "stop": stop["reason"], "shared_state_diff": sorted(diff),
               "isolated_state_dir": iso, "model": MODEL_EXPECTED, "voice": VOICE_EXPECTED, "backend": BACKEND}
    json.dump(summary, open(f"{out}/audit/run_summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 3 if stop["reason"] else 0


if __name__ == "__main__":
    sys.exit(main())
