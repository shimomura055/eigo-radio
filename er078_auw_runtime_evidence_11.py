# -*- coding: utf-8 -*-
"""AUW 委任_11: 残Section実音声 runtime evidence runner(B-A2-01 narrator / X-B1-06 / fresh JA正例)。

Production コードは無編集。共有 state は evidence_11 配下へ隔離(er077 apply_isolation + 06b begin/finish を再利用)。
有料 API は --execute 指定時のみ。全経路の費用を SDK レベルで事前 wrapper 記録(06b と同じ token_actual 方式)。
監督ループ・自動再試行なし。1 part 1 回のみ実行(再起動しない)。STOP: <out>/STOP と stop_scope_check_01。

  bnarr    : run_tts_a2_2v_new_topic(er012_b_family_production_runner_01.py)を実在 topic の parts.json(隔離複製)でそのまま呼ぶ。
             flag/module monkeypatch なし、tts_backend 渡さず、出力は <theme>/a2/narration/ の本番同一レイアウト。
             その後 finalize_tts_results_a2_2v_new_topic で tts_generation_results.json と事後試聴リストを導出(runner 側処理)。
  xkp_miss : X B1 入口(er019 _generate_or_reuse_kp + shared_narration.ensure_key_phrase_english_component、_generate_key_phrase_segments_b1
             L1065-1075 と同一呼出)で Store miss を確実に起こす新規 phrase 1 本。
  ja_fresh : U1 発効後、既存 JA 原稿(原稿変更なし)を Production 正式 JA 経路(generate_a2_japanese_with_reading_safety)で
             TTS→統一 judge。Secondary 呼出の実発生を確認する。
使い方: .venv\\Scripts\\python.exe er078_auw_runtime_evidence_11.py <bnarr|xkp_miss|ja_fresh> --out <dir> --budget-jpy 16 [--parts <parts.json>] [--execute]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time

import er078_auw_runtime_evidence_06 as e6
import er078_auw_runtime_evidence_06b as b6

ROOT = e6.ROOT
EV = "er058_output/unified_all_roles_production_wiring_01/evidence_12"   # 委任_12(委任_11は evidence_11。実測単価の参照元は EV11)
EV11 = "er058_output/unified_all_roles_production_wiring_01/evidence_11"
b6.EV = EV
b6.LEDGER = f"{EV}/cost/spend_ledger.jsonl"
b6.CAP_JPY = 34.0   # 委任_12 Guardrail(累計、新規ledger)。(委任_11は16)T-3: 到達・接近時は理由を記録して判断(自動継続しない)
e6.MANAGED_IDS[:] = ["AUW-06", "ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01", "AUW-11", "AUW-12"]

DEFAULT_PARTS = "er012_output/b_family_a2_new_topic_production_01/personalized_news_2v_a2/parts.json"   # tension_body を持つ new-topic parts(委任_11 初回実行は E-family parts に tension_body が無く KeyError で終了=s6記録)
REQUIRED_PARTS_KEYS = ("title", "point_one_heading", "point_two_heading", "point_one_body", "point_two_body", "part1", "part2", "tension_body", "in_one_line")
VOICE_A, VOICE_B = "Algieba", "Erinome"   # er012_output/*/audit/voice_resolution.json(Production解決済み値)
NEW_THEME = "auw12_personalized_news_a2"
# 見出し(数値入り)の実音声確認用に point_two_heading のみ数値入りへ差替(隔離複製。Production の parts は不変)
NUMERIC_HEADING = "Why Meta paused the feature after 3 weeks"

XKP_PHRASE = "a quiet refund window"   # Master Store に存在しない新規 phrase(miss 確認は実行前後の manifest で記録)

JA_FRESH2 = [   # 委任_12: Latin文字(A-Z/a-z/数字)を含まない既存原稿のみ(er025 JA web lookup 発火防止)
    ("jf2_hr_comment", "合言葉はブルルクル、グロルプ、ヴンムプ、フヌクです。"),   # evidence_06b ja_hr と同一原稿(Latin無し)
    ("jf3_g8_gas", "熟すと出るガス"),                                              # Phase 0 fixture g8(C1 entity_like「ガス→カス」救済例)と同一原稿(Latin無し)
]

JA_FRESH2 = [   # 委任_12: Latin文字(A-Z/a-z/数字)を含まない既存原稿のみ(er025 JA web lookup 発火防止)
    ("jf2_hr_comment", "合言葉はブルルクル、グロルプ、ヴンムプ、フヌクです。"),   # evidence_06b ja_hr と同一原稿(Latin無し)
    ("jf3_g8_gas", "熟すと出るガス"),                                              # Phase 0 fixture g8(C1 entity_like「ガス→カス」救済例)と同一原稿(Latin無し)
]

JA_FRESH = [
    ("jf1_akb48_title", "AKB48の新曲『好きish』、伊藤百花が2作連続センター、近藤沙樹が初選抜"),   # evidence_10 S3(A6 entity_like 差)と同一原稿
    ("jf2_hr_comment", "合言葉はブルルクル、グロルプ、ヴンムプ、フヌクです。"),                       # evidence_06b ja_hr と同一原稿(固有語)
]


import re
_LATIN = re.compile(r"[A-Za-z0-9]")


def _count_lines(p):
    return sum(1 for _ in open(p, encoding="utf-8")) if os.path.exists(p) else 0


def _summ(r):
    aj = (r or {}).get("asr_judgement") or {}
    sec = aj.get("secondary") or {}
    pri = aj.get("primary") or {}
    return {"status": (r or {}).get("status"), "state": aj.get("state"), "reason": aj.get("reason_code"),
            "primary_passed": pri.get("passed"), "primary_label": pri.get("label"), "primary_text": pri.get("text"),
            "secondary_called": sec.get("called"), "secondary_text": sec.get("text"), "secondary_accepted": sec.get("accepted"),
            "exclusion_rule": aj.get("exclusion_rule"), "warnings": aj.get("warnings"),
            "n_attempts": len((r or {}).get("attempts_log") or []), "has_asr_judgement": bool(aj),
            "asr_text": (r or {}).get("asr_text"), "slowdown_applied": (r or {}).get("slowdown_applied"),
            "model": (r or {}).get("model") or (r or {}).get("tts_model"), "voice": (r or {}).get("voice"),
            "keys": sorted((r or {}).keys())[:40]}


def _run_guarded(res, key, fn):
    try:
        res.setdefault("stage_result", {})[key] = "OK"
        return fn()
    except SystemExit as e_:
        res["stage_result"][key] = f"SystemExit({e_.code})"
    except Exception as e_:  # noqa: BLE001
        import traceback
        res["stage_result"][key] = f"{type(e_).__name__}: {str(e_)[:500]}"
        res["traceback"] = traceback.format_exc()[-2000:]
    return None


def run_bnarr(execute, budget, parts_src, label="bnarr"):
    parts = json.load(open(parts_src, encoding="utf-8"))
    missing = [k for k in REQUIRED_PARTS_KEYS if not parts.get(k)]
    if missing:   # API呼出・隔離・コピーより前に停止(初回実行の教訓)
        raise SystemExit(f"parts.json に必須キーが無い(API呼出前に停止): {missing}")
    out, r77, before, snap0, res, meter, ok = b6.begin(label, budget, execute, copy_master=True)
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    base = f"{out}/{NEW_THEME}/a2"
    narration_dir, audit_dir, kp_dir = f"{base}/narration", f"{base}/audit", f"{base}/key_phrases"
    for d in (narration_dir, audit_dir, kp_dir):
        os.makedirs(d, exist_ok=True)
    orig_h2 = parts["point_two_heading"]
    if label == "bnarr":   # 委任_11互換。委任_12(bnarr_full)は入力parts無改変(全体の実音声)
        parts["point_two_heading"] = NUMERIC_HEADING
    json.dump(parts, open(f"{base}/parts.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"items": []}, open(f"{kp_dir}/keywords_canonicalized.json", "w", encoding="utf-8"))
    res["plan"] = {"parts_source": parts_src, "isolated_copy": f"{base}/parts.json", "new_theme_name": NEW_THEME,
                   "point_two_heading_original": orig_h2, "point_two_heading_used": parts["point_two_heading"],
                   "voices": [VOICE_A, VOICE_B], "n_new_clips_expected": 9, "label": label, "label": label,
                   "segments": ["topic_intro", "point_one_heading", "point_two_heading", "point_one", "point_two",
                                "full_story_part1", "full_story_part2", "tension_body", "in_one_line"]}
    import er012_b_family_production_runner_01 as B
    ah = getattr(__import__("er011_human_review_lock_01"), "ATTEMPT_HISTORY_PATH")
    res["attempt_history_path_isolated"] = ah
    res["attempt_history_rows_before"] = _count_lines(ah)
    store_manifest = f"{out}/master_audio_store/manifest.json"
    res["store_manifest_sha_before"] = e6.sha(store_manifest) if os.path.exists(store_manifest) else None
    if ok:
        t0 = time.time()
        new_results = _run_guarded(res, "run_tts_a2_2v_new_topic",
                                   lambda: B.run_tts_a2_2v_new_topic(parts, VOICE_A, VOICE_B, narration_dir))
        res["elapsed_sec"] = round(time.time() - t0, 1)
        if new_results is not None:
            json.dump(new_results, open(f"{out}/new_results_raw.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
            res["clips"] = {k: _summ(v) for k, v in new_results.items()}
            _run_guarded(res, "finalize_tts_results", lambda: B.finalize_tts_results_a2_2v_new_topic(
                new_results, f"{out}/{NEW_THEME}", audit_dir, kp_dir, VOICE_A, VOICE_B))
            res["tts_generation_results_exists"] = os.path.exists(f"{audit_dir}/tts_generation_results.json")
            ll = [p for p in (f"{out}/{NEW_THEME}/pass_with_warning_listening_list.html",) if os.path.exists(p)]
            res["listening_list_files"] = ll or [os.path.join(dp, f) for dp, _, fs in os.walk(f"{out}/{NEW_THEME}") for f in fs if "listening" in f.lower()]
    res["attempt_history_rows_after"] = _count_lines(ah)
    if os.path.exists(ah):
        rows = [json.loads(l) for l in open(ah, encoding="utf-8") if l.strip()]
        res["attempt_history_segment_keys"] = sorted({str(r.get("segment_key")) for r in rows})[:60]
        res["attempt_history_keys_isolated"] = all(NEW_THEME in str(r.get("segment_key")) or str(r.get("segment_key")).startswith("evidence") or out.split("/")[-1] in str(r.get("segment_key")) for r in rows) if rows else None
    res["store_manifest_sha_after"] = e6.sha(store_manifest) if os.path.exists(store_manifest) else None
    b6.finish(out, r77, before, snap0, res, meter, extra_print=("clips",))


def run_xkp_miss(execute, budget):
    out, r77, before, snap0, res, meter, ok = b6.begin("xkp_miss", budget, execute, copy_master=True)
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    narration_dir = f"{out}/xkp/b1b/narration"
    os.makedirs(narration_dir, exist_ok=True)
    import er019_family_x_audio_production_runner_01 as X
    import er006_audio_cost_pilot_02_shared_narration as shared_narration
    import er006_master_audio_store_01 as store
    import er003_v1_n3_01_tts_generate as n3_tts
    import er005_cost_logger as cl
    import er078_secondary_run_scope_01 as scope
    tel = store.TELEMETRY_PATH
    res["plan"] = {"phrase": XKP_PHRASE, "tts_backend": X.FAMILY_X_APPROVED_PRODUCTION_TTS_BACKEND,
                   "call": "er019:_generate_or_reuse_kp(None,1,'english',...,shared_narration.ensure_key_phrase_english_component(tts_safe_kp_en(used_form),...))"}
    res["telemetry_rows_before"] = _count_lines(tel)
    if ok:
        tb = X.FAMILY_X_APPROVED_PRODUCTION_TTS_BACKEND   # Production の X runner が明示的に渡す値と同一

        @scope.with_secondary_run
        def go():
            wav = f"{narration_dir}/kp1_en.wav"
            with cl.segment_context("kp1_english"):
                return X._generate_or_reuse_kp(
                    None, 1, "english", wav,
                    lambda: shared_narration.ensure_key_phrase_english_component(n3_tts.tts_safe_kp_en(XKP_PHRASE), wav, tts_backend=tb),
                    expected_text=XKP_PHRASE)
        r = _run_guarded(res, "xkp_english", go)
        if r is not None:
            res["clip"] = _summ(r)
            res["raw_result_keys"] = sorted(r.keys())
            json.dump(r, open(f"{out}/xkp_result_raw.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    new_tel = [json.loads(l) for l in open(tel, encoding="utf-8")][res["telemetry_rows_before"]:] if os.path.exists(tel) else []
    res["telemetry_rows_new"] = new_tel
    res["telemetry_rows_after"] = _count_lines(tel)
    b6.finish(out, r77, before, snap0, res, meter, extra_print=("clip", "telemetry_rows_new"))


def run_ja_fresh(execute, budget, label="ja_fresh", items=None):
    items = items or JA_FRESH
    if label == "ja_fresh2":   # 委任_12: Latin token 原稿はAPI呼出・隔離より前に停止(web lookup 発火防止)
        bad = [i for i, t in items if _LATIN.search(t)]
        if bad:
            raise SystemExit(f"Latin文字を含む原稿(er025 web lookup 発火の恐れ。API呼出前に停止): {bad}")
    out, r77, before, snap0, res, meter, ok = b6.begin(label, budget, execute)
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    res["plan"] = [{"id": i, "text": t} for i, t in items]
    import er003_v1_n3_01_tts_generate as n3_tts
    import er012_b_family_voices_a2_production_01 as a2prod
    import er005_cost_logger as cl
    import er078_secondary_run_scope_01 as scope
    import er078_asr_unified_judge_01 as uj
    res["u1_keep_flag"] = uj.U1_KEEP_C1_SIMILARITY_EXCLUSIONS
    if ok:
        @scope.with_secondary_run
        def go():
            rows = []
            for cid, text in items:
                wav = f"{out}/run/a2/narration/{cid}.wav"
                os.makedirs(os.path.dirname(wav), exist_ok=True)
                with cl.segment_context(cid):
                    if cid == "jf1_akb48_title":
                        r = a2prod.generate_japanese_title_for_new_topic(text, wav)   # Production 正式の japanese_title 経路
                    else:
                        r = n3_tts.generate_a2_japanese_with_reading_safety(text, wav, n3_tts.expected_substring_ja(text))
                s = _summ(r)
                s["id"], s["canonical"] = cid, text
                s["wav"] = wav
                rows.append(s)
            return rows
        rows = _run_guarded(res, "ja_fresh", go)
        res["rows"] = rows
    b6.finish(out, r77, before, snap0, res, meter, extra_print=("rows", "u1_keep_flag"))


# ---------------------------------------------------------------- 委任_12 dry-run(API 0。socket.connect を遮断した上で検査)
def _block_network():
    import socket

    def _deny(*a, **k):
        raise RuntimeError("[DRYRUN] network blocked (API 0)")
    socket.socket.connect = _deny   # type: ignore[assignment]
    socket.socket.connect_ex = _deny   # type: ignore[assignment]


def _measured_narr_unit_costs():
    """委任_11 bnarr の usage_log.jsonl(token_actual)から実測単価を算出。"""
    rows = [json.loads(l) for l in open(f"{EV11}/bnarr/usage_log.jsonl", encoding="utf-8") if l.strip()]
    ledger = [json.loads(l) for l in open(f"{EV11}/cost/spend_ledger.jsonl", encoding="utf-8") if l.strip()]
    total = [r for r in ledger if r["run"] == "bnarr"][0]["est_total_jpy"]
    # point_two attempt1(TTS 1412tok 08:36:28 + ASR 08:36:30)までを「retry無し基準」とし、それ以降(Azure Secondary/attempt2 TTS/ASR)をretry費用とみなす
    retry_cost = sum(r["est_jpy"] for r in rows if r["ts"][11:] >= "08:36:31")
    # ただし Azure Secondary 行(08:36:56)は retry の一部(attempt1 のNG判定由来)。attempt1が最初からPASSなら不要 → retry費用側に含める(上の >= で含まれる)
    no_retry_first5 = round(total - retry_cost, 4)
    tts = [r for r in rows if str(r.get("model", "")).endswith("-tts")]
    p1 = [r for r in tts if r["out_tok"] == 542][0]
    p2 = [r for r in tts if r["out_tok"] == 1412][0]
    azure = [r for r in rows if "seconds" in r][-1]
    return {"ledger_total_bnarr": total, "first5_no_retry_jpy": no_retry_first5,
            "per_char_low": round(p1["est_jpy"] / 490, 6), "per_char_high": round(p2["est_jpy"] / 544, 6),
            "asr_per_char": 0.0005, "retry_event_azure_jpy": azure["est_jpy"],
            "basis": "evidence_11/bnarr/usage_log.jsonl (token_actual): point_one 490字=%.4f / point_two 544字(attempt1)=%.4f" % (p1["est_jpy"], p2["est_jpy"])}


def dryrun_bnarr(label, parts_src, budget):
    import shutil
    out = f"{EV}/{label}"
    os.makedirs(out, exist_ok=True)
    _block_network()
    parts = json.load(open(parts_src, encoding="utf-8"))
    missing = [k for k in REQUIRED_PARTS_KEYS if not parts.get(k)]
    segs = {"topic_intro": f"Today's topic is {parts.get('title','')}.", "point_one_heading": parts.get("point_one_heading", ""),
            "point_two_heading": parts.get("point_two_heading", ""), "point_one": parts.get("point_one_body", ""),
            "point_two": parts.get("point_two_body", ""), "full_story_part1": parts.get("part1", ""),
            "full_story_part2": parts.get("part2", ""), "tension_body": parts.get("tension_body", ""), "in_one_line": parts.get("in_one_line", "")}
    chars = {k: len(v) for k, v in segs.items()}
    new4 = chars["full_story_part1"] + chars["full_story_part2"] + chars["tension_body"] + chars["in_one_line"]
    u = _measured_narr_unit_costs()
    low = u["first5_no_retry_jpy"] + new4 * (u["per_char_low"] + u["asr_per_char"])
    high = u["first5_no_retry_jpy"] + new4 * (u["per_char_high"] + u["asr_per_char"])
    retry_event = chars["tension_body"] * (u["per_char_high"] + u["asr_per_char"]) + u["retry_event_azure_jpy"]
    d = {"label": label, "mode": "dry-run", "api_calls": 0, "network_blocked": True, "parts_source": parts_src,
         "required_keys": list(REQUIRED_PARTS_KEYS), "missing_keys": missing, "chars_per_segment": chars,
         "latin_scan": {"note": "narrator は英語TTS経路。er025 JA web lookup は JA経路(er003 L536/L825)のみで英語narratorでは呼ばれない(grep確認)",
                        "ja_lookup_path_in_narrator": False},
         "unit_costs": u, "estimate_jpy": {"nominal_low": round(low, 2), "nominal_high": round(high, 2), "one_retry_event": round(retry_event, 2),
                                           "high_plus_one_retry": round(high + retry_event, 2), "high_plus_two_retry": round(high + 2 * retry_event, 2)},
         "budget_jpy": budget}
    # Store hit/miss 予測: 隔離 Store コピー上で共有narrationを(network遮断のまま)実行。miss ならここで例外=miss
    ok_store, store_info = True, {}
    iso = f"{out}/_dry_store"
    try:
        import er006_audio_cost_pilot_02_shared_narration as sn
        import er006_master_audio_store_01 as store
        if os.path.exists(iso):
            shutil.rmtree(iso)
        shutil.copytree("er006_output/master_audio_store_01", iso)
        store.STORE_DIR, store.AUDIO_DIR = iso, f"{iso}/audio"
        store.MANIFEST_PATH, store.TELEMETRY_PATH = f"{iso}/manifest.json", f"{iso}/reuse_telemetry.jsonl"
        r = sn.ensure_all_shared_narration_a2(f"{out}/_dry_narr")
        store_info = {k: ((v or {}).get("status") if isinstance(v, dict) else str(v)[:40]) for k, v in r.items()}
    except Exception as e_:  # noqa: BLE001
        ok_store, store_info = False, {"error": f"{type(e_).__name__}: {str(e_)[:300]}"}
    d["shared_narration_store_prediction"] = {"all_hit_without_network": ok_store, "detail": store_info}
    d["segment_store_prediction"] = "9 segment は新規topicのため全 miss(本番TTS生成)。既存 Store に当該 segment の Key は無い"
    d["pass"] = bool((not missing) and ok_store and d["estimate_jpy"]["high_plus_one_retry"] <= budget)
    d["pass_rule"] = "必須キー欠落0 かつ 共有narration が network遮断下で全hit(API 0) かつ (nominal_high + 1 retry event) <= budget"
    shutil.rmtree(iso, ignore_errors=True)
    shutil.rmtree(f"{out}/_dry_narr", ignore_errors=True)
    json.dump(d, open(f"{out}/dryrun.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: d[k] for k in ("label", "api_calls", "missing_keys", "estimate_jpy", "shared_narration_store_prediction", "pass")}, ensure_ascii=False, default=str))
    return d


def dryrun_ja(label, items, budget):
    out = f"{EV}/{label}"
    os.makedirs(out, exist_ok=True)
    _block_network()
    import er003_audio_tts_asr_safety as safety
    import er003_v1_n3_01_tts_generate as n3_tts
    rows, any_lookup = [], False
    for cid, text in items:
        latin = _LATIN.findall(text)
        try:
            findings = safety.classify_foreign_tokens_in_japanese_text(text, known_key_phrase_terms=None, reading_dictionary={})
        except Exception as e_:  # noqa: BLE001
            findings = [{"error": str(e_)[:200]}]
        unknown = sorted({f.get("token") for f in findings if f.get("category") == safety.FOREIGN_TOKEN_HUMAN_REVIEW})
        lookup = bool(unknown)
        any_lookup = any_lookup or lookup
        rows.append({"id": cid, "text": text, "n_chars": len(text), "latin_tokens": latin, "foreign_token_findings": findings,
                     "unknown_tokens_needing_lookup": unknown, "predicted_lookup_call": lookup,
                     "expected_substring": n3_tts.expected_substring_ja(text)})
    secs = sum(max(2.0, 0.3 * r["n_chars"]) for r in rows)   # 約0.3秒/字(AKB48題名31字=約8秒の実測から)
    per_sec = 0.0243 + 0.0047 + 0.0444                         # TTS+Primary ASR+Azure(U1_U2_SECTION_PLAN_09 §(e)見積の単価)
    attempts = 3
    est = round(secs * per_sec * attempts, 2)
    d = {"label": label, "mode": "dry-run", "api_calls": 0, "network_blocked": True, "candidates": rows,
         "latin_token_total": sum(len(r["latin_tokens"]) for r in rows),
         "predicted_lookup_calls": int(any_lookup), "est_audio_seconds_per_attempt": round(secs, 1),
         "estimate_jpy": {"per_sec_all_in": round(per_sec, 4), "worst_case_3_attempts_all_secondary": est},
         "note": "text LLM(web lookup)は発火予測0のため見積に含めない(発火予測>0なら実行しない)。unit cost は U1_U2_SECTION_PLAN_09 §(e) の単価(JA clipの委任_11内実測は無い)",
         "budget_jpy": budget}
    d["pass"] = bool(d["latin_token_total"] == 0 and not any_lookup and est <= budget)
    d["pass_rule"] = "Latin token 0 かつ lookup発火予測0 かつ worst-case見積 <= budget"
    json.dump(d, open(f"{out}/dryrun.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: d[k] for k in ("label", "api_calls", "latin_token_total", "predicted_lookup_calls", "estimate_jpy", "pass")}, ensure_ascii=False))
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("part", choices=["bnarr", "xkp_miss", "ja_fresh", "bnarr_full", "ja_fresh2"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--budget-jpy", type=float, required=True)
    ap.add_argument("--parts", default=DEFAULT_PARTS)
    ap.add_argument("--cap-jpy", type=float, default=34.0, help="累計Guardrail(spend_ledger)。T-3: 超過は理由を記録して引き上げる場合のみ")
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="API 0。必須キー/Latin/Store/見積を dryrun.json へ(委任_12)")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    b6.CAP_JPY = a.cap_jpy
    # --out は <EV>/<part> であること(begin が <EV>/<part> を使う)
    assert a.out.replace("\\", "/").rstrip("/") == f"{EV}/{a.part}", f"--out must be {EV}/{a.part}"
    if a.dry_run and a.execute:
        raise SystemExit("--dry-run と --execute は同時指定不可")
    if a.dry_run:
        if a.part == "bnarr_full":
            dryrun_bnarr(a.part, a.parts, a.budget_jpy)
        elif a.part == "ja_fresh2":
            dryrun_ja(a.part, JA_FRESH2, a.budget_jpy)
        else:
            raise SystemExit("--dry-run は bnarr_full / ja_fresh2 のみ")
        return
    if a.part in ("bnarr_full", "ja_fresh2") and a.execute:   # 有料実行は dry-run 合格(pass:true)が前提
        dj = f"{EV}/{a.part}/dryrun.json"
        if not os.path.exists(dj) or not json.load(open(dj, encoding="utf-8")).get("pass"):
            raise SystemExit(f"dry-run 合格(dryrun.json pass:true)が無い。実行しない: {dj}")
    if a.part == "bnarr_full":
        run_bnarr(a.execute, a.budget_jpy, a.parts, label="bnarr_full")
    elif a.part == "ja_fresh2":
        run_ja_fresh(a.execute, a.budget_jpy, label="ja_fresh2", items=JA_FRESH2)
    elif a.part == "bnarr":
        run_bnarr(a.execute, a.budget_jpy, a.parts)
    elif a.part == "xkp_miss":
        run_xkp_miss(a.execute, a.budget_jpy)
    else:
        run_ja_fresh(a.execute, a.budget_jpy)


if __name__ == "__main__":
    main()
