# -*- coding: utf-8 -*-
"""FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 (DEV専用Trial、Production経路ではない)

ユーザー指示(2026-10-26、原文=docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01_USER.md):
『猿の手』『走れメロス』の Standard/Advanced で、セリフ音声を全件、文脈・感情付き方式で新規生成し、地の文等の既存音声と組み合わせた通し版を作る。

委任_01(Phase 0): inventory / budget / llm(Phase 1a、scope=Phase 1a・cap<=5円) / candidates。
委任_02(Phase 1b、Opus条件A M-1〜M-8反映済): preflight / dryrun-sinks / gen / assemble / analyze / page-all(scope=Phase 1b・cap<=100円、PHASE1_GO.json必須)。

方式は Round 1/2 (er118_fz_dialogue_context_tts_trial_01.py) を import 再利用のみ。
CONTEXT区画書式・EMOTION_DEVELOPER rule 1〜10・leakage検査・ASR検査・決定論抽出は無変更(本ファイルは module globals を作品×レベルへ切り替えるだけ)。
Production file / Master Store / manifest / reuse telemetry へは一切書かない(出力は er118_output/fz_full_episode_trial_01/ のみ)。
"""
import argparse
import contextlib
import copy
import datetime
import functools
import hashlib
import html as H
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import er118_fz_dialogue_context_tts_trial_01 as t   # noqa: E402  (読取・import再利用のみ。編集しない)

MANAGED_ID = "FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01"
OUT_ROOT = "er118_output/fz_full_episode_trial_01"
PAGE_ROOT = "user_test/fz_full_episode_trial_01"
DOC_DIR = "docs/research/FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01"
COST_LOG = f"{OUT_ROOT}/raw_usage_log.jsonl"
GO_FILE = f"{OUT_ROOT}/PHASE1_GO.json"
PHASE1A_CAP_JPY = 5.0          # 委任_01の個別Guardrail(感情情報LLMのみ)
SCOPE_PHASE1A = "Phase 1a"
SCOPE_PHASE1B = "Phase 1b"
PHASE1B_CAP_JPY = 100.0        # R-9: 委任_02(Phase 1b)の個別Guardrail(見積 期待25/保守31/天井75円)
_RUN_ROOT = "er026_output/family_z_production_e2e_01"

# 作品×レベル。run = 公開済み完成版の正本run。pages = 公開済みProduction試聴ページ(参照のみ・上書き禁止)。
WORK_CFG = {
    "monkeys_paw": {
        "title_ja": "猿の手", "title": "The Monkey's Paw", "run": f"{_RUN_ROOT}/the_monkeys_paw/run_sf_prod_01",
        "pages": "user_test/family_z_monkeys_paw_01", "audio_prefix": "MonkeysPaw", "story_key": "the_monkeys_paw",
        "speaker_display": dict(t.WORKS["monkeys_paw"]["speaker_display"]),
        # Round 2の許可名に複数形 whites(= Mr. White + Mrs. White の言い換え。入力に与えた名前の屈折形で新規固有名詞ではない)を追加。検査規則は無変更(初回runで scene の "the Whites" 12件が誤DISCARD)
        "allowed_names": set(t.WORKS["monkeys_paw"]["allowed_names"]) | {"whites"},
        "emotion_title": "The Monkey's Paw"},
    "melos": {
        "title_ja": "走れメロス", "title": "Before the Last Light (Melos)", "run": f"{_RUN_ROOT}/melos/run_e2e_06",
        "pages": "user_test/family_z_melos_02", "audio_prefix": "Melos", "story_key": "melos",
        "speaker_display": {"melos": "Melos", "king": "the ruler", "friend": "Melos's friend"}, "allowed_names": {"melos"},
        "emotion_title": "Before the Last Light (Melos)"},
}
LEVELS = {"a2": {"label": "Standard", "page": "audio_standard", "speed": "std_dialogue_none"},
          "b1b": {"label": "Advanced", "page": "audio_advanced", "speed": "adv_dialogue_fast6"}}
CASES = [("monkeys_paw", "a2"), ("monkeys_paw", "b1b"), ("melos", "a2"), ("melos", "b1b")]

# Round 2 実測(BUDGET_LOG_02.md): Gemini TTS 26.20円/50 call、OpenAI ASR 1.12円/50 call + Azure 0.48円/2 call、感情LLM 約0.095円/call
R2_TTS_PER_CALL_JPY = 26.20 / 50
R2_ASR_PER_CALL_JPY = (1.12 + 0.48) / 50
R2_LLM_PER_CALL_JPY = 0.0969
R2_CALLS_PER_CLIP = 50 / 48           # Round 2 実測 (2 retry / 48 clip)


def case_key(work: str, level: str) -> str:
    return f"{work}/{level}"


def case_dir(work: str, level: str) -> str:
    return f"{OUT_ROOT}/{work}/{level}"


_T_GLOBALS = ("LEVEL", "SRC_RUN", "PLAN_PATH", "TTS_RESULTS_PATH", "NARR_DIR", "SPEAKER_DISPLAY", "ALLOWED_NAMES", "WORK_TITLE", "WORK_TITLE_JA", "EMOTION_DEVELOPER", "voice_map")


_USE_CASE_ACTIVE = {"v": None}


@contextlib.contextmanager
def use_case(work: str, level: str):
    """Round 1/2 module の globals を作品×レベルへ一時的に切り替え、終了時に必ず元へ戻す(Round 1/2の既定=賢者の贈り物を壊さない。Opus論点⑤)。
    R-8(a): 単一thread・単一case前提。実行中の再入(並列/入れ子)はassertで拒否する(例外時もfinallyで復元・解除)。"""
    if _USE_CASE_ACTIVE["v"] is not None:
        raise RuntimeError(f"use_case は再入禁止(実行中={_USE_CASE_ACTIVE['v']}、要求={(work, level)})。並列実行は禁止(Opus R-8a)")
    _USE_CASE_ACTIVE["v"] = (work, level)
    saved = {k: getattr(t, k) for k in _T_GLOBALS}
    try:
        yield configure_case(work, level)
    finally:
        for k, v in saved.items():
            setattr(t, k, v)
        _USE_CASE_ACTIVE["v"] = None


def with_case(fn):
    """fn(work, level, ...) を use_case の中で実行する。"""
    @functools.wraps(fn)
    def w(work, level, *a, **kw):
        with use_case(work, level):
            return fn(work, level, *a, **kw)
    return w


def configure_case(work: str, level: str) -> dict:
    """(内部用。直接呼ぶ場合は呼出側が復元責任を持つ。通常は use_case を使う) module globals を作品×レベルへ切り替える(方式関数は無変更)。"""
    c = WORK_CFG[work]
    t.LEVEL = level
    t.SRC_RUN = c["run"]
    t.PLAN_PATH = f"{c['run']}/segment_plan_{level}.json"
    t.TTS_RESULTS_PATH = f"{c['run']}/{level}/audit/tts_generation_results.json"
    t.NARR_DIR = f"{c['run']}/{level}/narration"
    t.SPEAKER_DISPLAY = dict(c["speaker_display"])
    t.ALLOWED_NAMES = set(c["allowed_names"])
    t.WORK_TITLE, t.WORK_TITLE_JA = c["emotion_title"], c["title_ja"]
    t.EMOTION_DEVELOPER = t._EMOTION_DEVELOPER_MAGI.replace("The Gift of the Magi", c["emotion_title"])
    t.voice_map = _production_voice_map     # plan側のspeaker key(例 king)と voice_assignment のkey(例 dionysius)が異なる作品があるため、Production結果の実Voiceを正とする
    return c


def _production_voice_map() -> dict:
    """plan clipのspeaker key -> Production実Voice。正本=当該runの tts_generation_results の各dialogue segmentの voice(voice_assignment.json=APPROVED_FOR_PRODUCTION と一致することを test で確認)。"""
    plan, res = t.load_plan(), t.load_json(t.TTS_RESULTS_PATH)["segments"]
    return {x["speaker"]: res[x["id"]]["voice"] for x in plan["clips"] if str(x.get("voice_role", "")).startswith("dialogue:")}


def dialogue_clips(plan: dict) -> list:
    return [x for x in plan["clips"] if str(x.get("voice_role", "")).startswith("dialogue:")]


# ============================================================
# 1. 棚卸(API 0、読取のみ)
# ============================================================
@with_case
def inventory_case(work: str, level: str) -> dict:
    c = WORK_CFG[work]
    run = c["run"]
    plan = t.load_plan()
    res = t.load_json(t.TTS_RESULTS_PATH)["segments"]
    tl = t.load_json(f"{run}/{level}/assembly/timeline.json")
    dur_of = {e["part"]: e["duration_seconds"] for e in tl["timeline"]}
    d_clips = dialogue_clips(plan)
    rows = []
    for x in d_clips:
        s = res[x["id"]]
        orig = f"{t.NARR_DIR}/{x['id']}_original.wav"
        use = orig if os.path.isfile(os.path.join(ROOT, orig)) else f"{t.NARR_DIR}/{x['id']}.wav"
        a_dur = None
        try:
            xx, sr = t.read_mono(use)
            a_dur = round(len(xx) / sr, 3)
        except Exception:      # noqa: BLE001
            pass
        asr = s.get("asr_judgement") or {}
        legacy = s.get("asr_judgement_inherited") or s.get("asr_judgement_legacy_post_slowdown") or {}
        rows.append({
            "clip_id": x["id"], "speaker": x["speaker"], "voice": t.tts_voice(x), "words": x["word_count"], "text": x["text"],
            "production_attempts": len(s.get("attempts") or []), "tts_generations_used": s.get("tts_generations_used"),
            "asr_state": asr.get("state") or ("(inherited)" + str(legacy.get("state")) if legacy else None),
            "asr_label": (asr.get("primary") or {}).get("label"), "status": s.get("status"),
            "speed_profile": (s.get("speed_profile") or {}).get("profile"), "tempo": (s.get("speed_profile") or {}).get("tempo"),
            "reused_from_previous_run": s.get("reused_from_previous_run"),
            "base_style_sha_matches": (s.get("style") or {}).get("effective_style_prefix_sha256") == t.EXPECTED_BASE_STYLE_SHA,
            "original_audio_s": a_dur, "final_in_episode_s": dur_of.get(x["id"]),
            "tts_model": (s.get("model_ids_measured") or [None])[0],
            "in_round2_selection": (work == "monkeys_paw" and level == "b1b" and x["id"] in {y["id"] for y in t.WORKS["monkeys_paw"]["targets"]}),
        })
    n_clips = len(plan["clips"])
    narr_story = [x for x in plan["clips"] if x not in d_clips]
    total = tl["duration_seconds"]
    d_total = sum(dur_of.get(x["id"], 0.0) for x in d_clips)
    sp_count = {}
    for r in rows:
        sp_count[r["speaker"]] = sp_count.get(r["speaker"], 0) + 1
    pg = f"{c['pages']}/{LEVELS[level]['page']}/{c['audio_prefix']}_{level}_full.mp3"
    return {
        "work": work, "level": level, "level_label": LEVELS[level]["label"], "title_ja": c["title_ja"], "run": run,
        "plan_title": plan.get("title"), "n_story_clips": n_clips, "n_dialogue": len(d_clips), "n_story_narration": len(narr_story),
        "speaker_counts": sp_count, "dialogue_words_total": sum(r["words"] for r in rows),
        "dialogue_words_min": min(r["words"] for r in rows), "dialogue_words_max": max(r["words"] for r in rows),
        "dialogue_le2_words": sum(1 for r in rows if r["words"] <= 2),
        "episode_duration_s": total, "dialogue_in_episode_s": round(d_total, 2), "dialogue_share": round(d_total / total, 3),
        "timeline_parts_total": len(tl["timeline"]), "gain_target_rms": (tl.get("gain_report") or {}).get("target_rms"),
        "headroom": tl.get("headroom"),
        "production_wav": tl["wav"], "production_wav_exists": os.path.isfile(os.path.join(ROOT, tl["wav"])),
        "public_full_mp3": pg, "public_full_mp3_exists": os.path.isfile(os.path.join(ROOT, pg)),
        "public_page": f"https://shimomura055.github.io/eigo-radio/{c['pages']}/index.html",
        "voices": {r["speaker"]: r["voice"] for r in rows}, "speed_profile": LEVELS[level]["speed"],
        "all_base_style_sha_match": all(r["base_style_sha_matches"] for r in rows),
        "all_status_ok": all(r["status"] == "OK" for r in rows),
        "production_calls_total": sum(r["production_attempts"] for r in rows),
        "rows": rows,
    }


def render_inventory_md(inv: dict) -> str:
    L = ["# INVENTORY_01 — 全編通しTrialの対象棚卸(FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 委任_01、API 0)", "",
         "出典: 各作品の公開済み完成版runの `segment_plan_<lv>.json` / `<lv>/audit/tts_generation_results.json` / `<lv>/assembly/timeline.json` / `voice_assignment.json`(読取のみ)。"
         "機械可読: `er118_output/fz_full_episode_trial_01/inventory.json`(`py er118_fz_full_episode_trial_01.py inventory` で再生成可)。", "",
         "## 1. 作品×レベルの総括", "",
         "| 作品 | レベル | 正本run | 話者別セリフ数 | セリフ計 | 語数(min/max/計/≤2語) | 地の文clip | 通し秒 | セリフ占有 | Production試行/clip数 | base style一致 | 速度仕様 | 公開通しmp3 |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for k in inv["cases"]:
        v = inv["cases"][k]
        L.append(f"| {v['title_ja']} | {v['level_label']}({v['level']}) | `{v['run']}` | {v['speaker_counts']} | {v['n_dialogue']} | "
                 f"{v['dialogue_words_min']}/{v['dialogue_words_max']}/{v['dialogue_words_total']}/{v['dialogue_le2_words']} | {v['n_story_narration']} | "
                 f"{v['episode_duration_s']:.1f} | {v['dialogue_share']*100:.1f}% | {v['production_calls_total']}/{v['n_dialogue']} | {v['all_base_style_sha_match']} | "
                 f"{v['speed_profile']} | `{v['public_full_mp3']}`(実在={v['public_full_mp3_exists']}) |")
    tot = sum(v["n_dialogue"] for v in inv["cases"].values())
    L += ["", f"- **新規生成対象セリフ総数: {tot} clip**(猿の手 Std {inv['cases']['monkeys_paw/a2']['n_dialogue']} / Adv {inv['cases']['monkeys_paw/b1b']['n_dialogue']}、"
          f"メロス Std {inv['cases']['melos/a2']['n_dialogue']} / Adv {inv['cases']['melos/b1b']['n_dialogue']})。両作品とも Standard(a2)・Advanced(b1b)の2レベルが既存完成版に存在する。",
          "- 地の文・Intro/Welcome/Preview/Key Phrase/Comment/Outro等の既存音声は Production run の `<lv>/narration/` を再利用(新規生成しない)。",
          "- 公開ページURL(Production・比較用の参照のみ): " + " / ".join(sorted({v["public_page"] for v in inv["cases"].values()})), "",
          "## 2. セリフclip一覧(作品×レベル)", ""]
    for k, v in inv["cases"].items():
        L += [f"### {v['title_ja']} / {v['level_label']} (`{k}`) — Voice {v['voices']}", "",
              "| clip_id | 話者 | 語数 | 原音秒 | Production試行 | ASR | status | 速度 | Round 2流用禁止 | 本文 |", "|---|---|---|---|---|---|---|---|---|---|"]
        for r in v["rows"]:
            L.append(f"| `{r['clip_id']}` | {r['speaker']} | {r['words']} | {r['original_audio_s']} | {r['production_attempts']} | {r['asr_state']}/{r['asr_label']} | {r['status']} | "
                     f"{r['speed_profile']} | {'**はい**' if r['in_round2_selection'] else '-'} | {r['text'][:70]} |")
        L.append("")
    mp = inv["cases"]["monkeys_paw/b1b"]
    r2 = [r["clip_id"] for r in mp["rows"] if r["in_round2_selection"]]
    L += ["## 3. 流用禁止・再利用の範囲(ユーザー原文§2)", "",
          f"- 猿の手 Adv のうちRound 2 A/Bで生成済みの {len(r2)} clip(`{', '.join(r2)}`)は **新規に作り直す**(Round 2の生成音声を流用しない)。Std側はRound 2に無く全件新規。",
          "- メロスは全セリフ新規(Round 1/2に未登場)。",
          "- 比較条件が変わる範囲(明示): 地の文・Intro/Preview/KP/Comment/Outro・無音・gainルールは Production と同一音声/同一規則。**差はセリフclipのみ**(ただしgain/平均RMSはclip単位のProduction規則を適用、Production試行で確定した音声ではなく新規生成のため音量は規則で再計算される)。", "",
          "## 4. 注意・限界(観測事実)", ""]
    for k, v in inv["cases"].items():
        notes = []
        if v["dialogue_le2_words"]:
            notes.append(f"2語以下のセリフ {v['dialogue_le2_words']} 件(短文は話速が不安定=Round 2 EVAL_02 §5)")
        if any(r["reused_from_previous_run"] for r in v["rows"]):
            notes.append("Production clipは前run再利用(reused_from_previous_run)")
        if any(str(r["asr_state"]).startswith("(inherited)") for r in v["rows"]):
            notes.append("ASR判定は新形式でなく継承/旧形式(asr_judgement_inherited等)")
        if not v["all_status_ok"]:
            notes.append("status!=OKのclipあり")
        L.append(f"- `{k}`: " + ("; ".join(notes) if notes else "特記なし"))
    L.append("")
    return "\n".join(L)


def cmd_inventory() -> dict:
    inv = {"managed_id": MANAGED_ID, "generated_at": t.now_jst(), "cases": {}}
    for w, lv in CASES:
        inv["cases"][case_key(w, lv)] = inventory_case(w, lv)
    t.save_json(f"{OUT_ROOT}/inventory.json", inv)
    t._write_lines(f"{DOC_DIR}/INVENTORY_01.md", render_inventory_md(inv).split("\n"))
    return inv


# ============================================================
# 2. 費用見積(API 0)
# ============================================================
@with_case
def budget_case(work: str, level: str) -> dict:
    plan = t.load_plan()
    rows, tts_exp, tts_base = [], 0.0, 0.0
    for x in dialogue_clips(plan):
        ctx = t.extract_context(plan, x["id"])
        orig = f"{t.NARR_DIR}/{x['id']}_original.wav"
        use = orig if os.path.isfile(os.path.join(ROOT, orig)) else f"{t.NARR_DIR}/{x['id']}.wav"
        xx, sr = t.read_mono(use)
        dur = len(xx) / sr
        txt = t.tts_text_for(x)
        base_chars = len(t.build_prompt(txt, t.style_for_arm("base", ctx, None)))
        ctx_chars = len(t.build_prompt(txt, t.style_for_arm("ctx", ctx, None))) + 350     # +350 = LLM由来state/scene/reaction行の見込み(Round 2と同一)
        c_ctx, c_base = t.est_tts_jpy(ctx_chars, dur * 1.05), t.est_tts_jpy(base_chars, dur)
        tts_exp += c_ctx
        tts_base += c_base
        rows.append({"clip_id": x["id"], "audio_s": round(dur, 2), "base_chars": base_chars, "ctx_chars": ctx_chars, "ctx_est_jpy": round(c_ctx, 3), "base_est_jpy": round(c_base, 3)})
    n = len(rows)
    return {"work": work, "level": level, "n_clips": n, "tts_ctx_est_jpy_1call_per_clip": round(tts_exp, 3), "tts_base_est_jpy_1call_per_clip": round(tts_base, 3),
            "style_increment_est_jpy": round(tts_exp - tts_base, 3), "rows": rows}


def cmd_budget() -> dict:
    out = {"managed_id": MANAGED_ID, "generated_at": t.now_jst(), "cases": {}, "assumptions": {
        "r2_tts_per_call_jpy": R2_TTS_PER_CALL_JPY, "r2_asr_per_call_jpy": R2_ASR_PER_CALL_JPY, "r2_llm_per_call_jpy": R2_LLM_PER_CALL_JPY, "r2_calls_per_clip": R2_CALLS_PER_CLIP}}
    inv = t.load_json(f"{OUT_ROOT}/inventory.json")
    tot = {"n_clips": 0, "tts_1call": 0.0, "base_1call": 0.0}
    for w, lv in CASES:
        b = budget_case(w, lv)
        pa = inv["cases"][case_key(w, lv)]
        b["production_calls_total"], b["production_calls_per_clip"] = pa["production_calls_total"], round(pa["production_calls_total"] / pa["n_dialogue"], 3)
        out["cases"][case_key(w, lv)] = b
        tot["n_clips"] += b["n_clips"]
        tot["tts_1call"] += b["tts_ctx_est_jpy_1call_per_clip"]
        tot["base_1call"] += b["tts_base_est_jpy_1call_per_clip"]
    n = tot["n_clips"]
    prod_calls = sum(c["production_calls_total"] for c in out["cases"].values())
    scen = {}
    for name, cpc in (("expected(Round2実測 1.042 call/clip)", R2_CALLS_PER_CLIP), ("conservative(1.25 call/clip)", 1.25), ("ceiling(Production retry上限3 call/clip)", 3.0)):
        tts = tot["tts_1call"] * cpc
        asr = n * cpc * R2_ASR_PER_CALL_JPY
        llm = len(CASES) * R2_LLM_PER_CALL_JPY
        scen[name] = {"tts_jpy": round(tts, 2), "asr_jpy": round(asr, 2), "llm_jpy": round(llm, 2), "total_jpy": round(tts + asr + llm, 2)}
    out["totals"] = {"n_clips": n, "tts_ctx_est_jpy_1call_per_clip_sum": round(tot["tts_1call"], 3), "tts_base_est_jpy_sum": round(tot["base_1call"], 3),
                     "style_increment_est_jpy_sum": round(tot["tts_1call"] - tot["base_1call"], 3), "production_calls_total": prod_calls,
                     "production_calls_per_clip": round(prod_calls / n, 3), "scenarios": scen}
    t.save_json(f"{OUT_ROOT}/budget_plan.json", out)
    return out


# ============================================================
# 3. Phase 1a: 感情情報LLM(有料、cap<=5円。GO必須)
# ============================================================
def _require_go(scope: str = SCOPE_PHASE1A, max_cap: float = PHASE1A_CAP_JPY) -> dict:
    """R-9: scopeごとに上限を分離(Phase 1a=5円 / Phase 1b=100円)。scope不一致のGOでは起動しない。"""
    ap = os.path.join(ROOT, GO_FILE)
    if not os.path.exists(ap):
        raise SystemExit(f"[STOP] {GO_FILE} が無い。有料runは PHASE1_GO.json 無しで起動しない。")
    go = t.load_json(GO_FILE)
    if go.get("managed_id") != MANAGED_ID or go.get("scope") != scope or not go.get("cap_jpy") or float(go["cap_jpy"]) > max_cap:
        raise SystemExit(f"[STOP] PHASE1_GO.json の managed_id / scope({scope}) / cap_jpy(<= {max_cap}) 不正")
    return go


def _stop_check(out_name: str = "stop_check_llm.json") -> None:
    r = subprocess.run([sys.executable, "tools/stop_scope_check_01.py", "--managed-id", MANAGED_ID, "--run-dir", OUT_ROOT,
                        "--out", f"{OUT_ROOT}/{out_name}"], cwd=ROOT)
    if r.returncode == 3:
        raise SystemExit("[STOP] stop_scope_check rc=3")
    if r.returncode != 0:
        raise SystemExit(f"[STOP] stop_scope_check 異常 rc={r.returncode}")


@with_case
def run_llm_case(work: str, level: str, client=None) -> dict:
    """Round 2と同一の EMOTION_DEVELOPER / EMOTION_SCHEMA / gpt-6-luna / reasoning low で、当該作品×レベルの全セリフを1 call。"""
    go = _require_go()
    _stop_check()
    out_dir = f"{case_dir(work, level)}/llm"
    plan = t.load_plan()
    contexts = [t.extract_context(plan, x["id"]) for x in dialogue_clips(plan)]
    if client is None:
        import er019_family_x_audio_production_runner_01 as runner
        spent, _ = runner.compute_cost_jpy_so_far(os.path.join(ROOT, COST_LOG))
        if spent >= float(go["cap_jpy"]):
            raise SystemExit(f"[STOP] 個別Guardrail {go['cap_jpy']}円到達(実績{spent:.3f}円)")
        from dotenv import load_dotenv
        load_dotenv()
        import er005_cost_logger as cl
        cl.install(os.path.join(ROOT, COST_LOG))
        import er003_v1_en_direct_vfl_01_generate as vfl01
        client = vfl01.get_client()
    import er062_family_z_writer_01 as zw
    msgs = [{"role": "developer", "content": t.EMOTION_DEVELOPER}, {"role": "user", "content": t.emotion_user_message(contexts)}]
    kw = {"model": t.LLM_MODEL, "reasoning": {"effort": "low"}, "input": msgs, "text": {"format": {"type": "json_schema", **t.EMOTION_SCHEMA}}}
    r = client.responses.create(**kw)
    cost = zw.cost_jpy(t.LLM_MODEL, r.usage)
    if not str(r.model).startswith(t.LLM_MODEL):
        raise SystemExit(f"[STOP] 返却modelが{t.LLM_MODEL}で始まらない: {r.model}")
    raw = json.loads(r.output_text)
    checked = t.validate_emotion_items(raw.get("items"), contexts)
    for c in contexts:
        checked[c["clip_id"]]["evidence_sources"] = t.evidence_sources(c, checked[c["clip_id"]].get("llm_raw", {}).get("evidence", []))
    rec = {"managed_id": MANAGED_ID, "work": work, "level": level, "model_requested": t.LLM_MODEL, "model_returned": str(r.model), "cost_jpy": round(cost, 4),
           "n_clips": len(contexts), "prompt_sha256": t.emotion_prompt_sha(), "user_message_sha256": t.sha_text(msgs[1]["content"]), "raw_output": raw, "validated": checked,
           "n_accepted": sum(1 for v in checked.values() if v["status"] == "ACCEPTED"),
           "n_discarded": sum(1 for v in checked.values() if v["status"] == "DISCARDED"),
           "n_no_explicit_cue": sum(1 for v in checked.values() if v["status"] == "NO_EXPLICIT_CUE"), "saved_at": t.now_jst()}
    t.save_json(f"{out_dir}/emotion_notes.json", rec)
    t.save_json(f"{out_dir}/emotion_review.json", {"managed_id": MANAGED_ID, "reviewer": "Fable", "note": "fable_decisionを accept か discard に設定してからctx生成(委任_02)。discardはCONTEXTから"
              "LLM由来の項目(状態/場面/返答)を全て外し中立にする。", "items": {c["clip_id"]: {"llm_status": checked[c["clip_id"]]["status"], "fable_decision": None, "summary_ja": "", "reviewer_note": ""} for c in contexts}})
    return rec


@with_case
def _candidate_lines(work: str, level: str, rec: dict) -> list:
    plan = t.load_plan()
    L = [f"## 作品: {WORK_CFG[work]['title_ja']} / {LEVELS[level]['label']}({level}) — `{work}/{level}`", "",
         f"- LLM: 要求 `{rec['model_requested']}` / 返却 `{rec['model_returned']}`、1 call、{rec['n_clips']}セリフ、実費 {rec['cost_jpy']} 円。prompt sha256 `{rec['prompt_sha256'][:16]}…`。",
         f"- 決定論検査: ACCEPTED {rec['n_accepted']} / NO_EXPLICIT_CUE {rec['n_no_explicit_cue']} / DISCARDED {rec['n_discarded']}。レビュー記入先 `{case_dir(work, level)}/llm/emotion_review.json`。", ""]
    for i, x in enumerate(dialogue_clips(plan), 1):
        ctx = t.extract_context(plan, x["id"])
        v = rec["validated"][x["id"]]
        raw = v.get("llm_raw") or {}
        L += [f"### {work}/{level} {i}. `{x['id']}` — {ctx['speaker_display']}(Voice {ctx['voice']}) / status `{v['status']}`" + (f" 破棄理由 {v['discard_reasons']}" if v["discard_reasons"] else ""), "",
              f"- セリフ(英): {ctx['text']}",
              "- 前のセリフ: " + (" / ".join(f"{d['speaker_display']}: {t._unq(d['text'])}" for d in ctx["prev_dialogue"]) or "なし"),
              "- 後のセリフ: " + (" / ".join(f"{d['speaker_display']}: {t._unq(d['text'])}" for d in ctx["next_dialogue"]) or "なし"),
              f"- 直前の地の文: {ctx['narration_before'] or 'なし'}", f"- 直後の地の文: {ctx['narration_after'] or 'なし'}",
              f"- manner_words: {', '.join(ctx['manner_words']) or 'なし'}",
              f"- speaker_state: {raw.get('state')}", f"- scene: {raw.get('scene')}", f"- reaction_to_previous: {raw.get('reaction') or '(空)'}", "- 根拠引用(出どころ):"]
        for e in v.get("evidence_sources", []):
            src = "本人の台詞" if e["in_own_line"] else ("地の文" if e["in_narration"] else ("他者の台詞" if e["in_other_speaker_line"] else "不明"))
            L.append(f"  - 「{e['quote']}」 — {src}")
        L.append("")
    return L


def render_candidates() -> str:
    L = ["# EMOTION_CANDIDATES_01 — 全編通しTrialの感情情報(Fableレビュー用。TTS前に各 `emotion_review.json` へ accept / discard)", "",
         "方式はRound 2と同一(gpt-6-luna、reasoning low、EMOTION_DEVELOPER rule 1〜10、決定論検査=根拠引用の逐語一致・語数・新規固有名詞・強度語deny)。"
         "作品×レベルごとに全セリフを1 call。Std/Advの同一場面は文面が違うため別callで評価する。", ""]
    summ = []
    for w, lv in CASES:
        p = f"{case_dir(w, lv)}/llm/emotion_notes.json"
        if not os.path.exists(os.path.join(ROOT, p)):
            L += [f"## {w} / {lv}: 未実行", ""]
            continue
        rec = t.load_json(p)
        summ.append((w, lv, rec))
        L += _candidate_lines(w, lv, rec)
    tot = {k: sum(r[k] for _, _, r in summ) for k in ("n_accepted", "n_no_explicit_cue", "n_discarded", "n_clips")}
    tot_cost = round(sum(r["cost_jpy"] for _, _, r in summ), 4)
    L += ["## 合計", "", f"- {len(summ)}/4 call: ACCEPTED {tot['n_accepted']} / NO_EXPLICIT_CUE {tot['n_no_explicit_cue']} / DISCARDED {tot['n_discarded']}(計{tot['n_clips']}セリフ)、LLM実費 {tot_cost} 円。", ""]
    t._write_lines(f"{DOC_DIR}/EMOTION_CANDIDATES_01.md", L)
    return f"{DOC_DIR}/EMOTION_CANDIDATES_01.md"


# ============================================================
# 4. Phase 1b(委任_02、Opus条件A M-1〜M-8 / R-1〜R-9 反映)
#    生成(セリフ53 clip・ctx方式) -> DEV隔離組立 -> 解析 -> 試聴ページ。Production経路ではない(書込みは OUT_ROOT / PAGE_ROOT のみ)。
#    M-6: Round 1/2 module(t)は『純関数の許可list』だけを使う。generate_arm / load_reviewed_notes既定path / snapshot_protected /
#         est_next_clip_jpy / trial_reuse_key / _require_go / _stop_check は呼ばず、本module側に再実装している。
# ============================================================
NG_MAX_RECORDED = 2                 # M-8(PREREGISTERED_CRITERIA_02): NG(上限到達で不採用)<=2 clip なら C1 は記録付き成立
MIN_UNIT_INTERVAL_S = 150           # 起動間隔(委任文: 150秒以上)
Z_PAGES_PREFIXES = tuple(c["pages"] for c in WORK_CFG.values())


# ---------- 4-1 書込ガード(M-4) ----------
def _abs(p: str) -> str:
    return p if os.path.isabs(p) else os.path.join(ROOT, p)


def _real(p: str) -> str:
    return os.path.normcase(os.path.realpath(_abs(p)))


def under(path: str, root: str) -> bool:
    """M-4(a): 文字列prefixではなく realpath の commonpath で判定。"""
    a, r = _real(path), _real(root)
    try:
        return os.path.commonpath([a, r]) == r
    except ValueError:
        return False


def assert_writable(path: str) -> None:
    if not (under(path, OUT_ROOT) or under(path, PAGE_ROOT)):
        raise SystemExit(f"[STOP] 書込先が OUT_ROOT/PAGE_ROOT 配下でない(realpath判定): {path}")


def assert_out_root(path: str) -> None:
    if not under(path, OUT_ROOT):
        raise SystemExit(f"[STOP] run_dir/out_path が OUT_ROOT 配下でない(realpath判定): {path}")


def file_sha(path: str):
    ap = _abs(path)
    if not os.path.isfile(ap):
        return None
    h = hashlib.sha256()
    with open(ap, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def safe_write_json(path: str, obj) -> str:
    assert_writable(path)
    os.makedirs(os.path.dirname(_abs(path)), exist_ok=True)
    with open(_abs(path), "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)
    return path


def safe_write_text(path: str, text: str) -> str:
    assert_writable(path)
    os.makedirs(os.path.dirname(_abs(path)), exist_ok=True)
    with open(_abs(path), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return path


def safe_copy(src: str, dst: str) -> str:
    """M-4(b): shutil.copyfile のみ(hardlink/symlink/junction禁止)。既存dstがhardlink(nlink>1)なら書かずにSTOP(Production破壊防止)。"""
    assert_writable(dst)
    os.makedirs(os.path.dirname(_abs(dst)), exist_ok=True)
    if os.path.lexists(_abs(dst)):
        if os.path.islink(_abs(dst)) or os.stat(_abs(dst)).st_nlink > 1:
            raise SystemExit(f"[STOP] 既存dstがsymlink/hardlink: {dst}")
    shutil.copyfile(_abs(src), _abs(dst))
    if os.path.samefile(_abs(src), _abs(dst)):
        raise SystemExit(f"[STOP] copy後にsrc==dst(同一ファイル): {src} -> {dst}")
    return dst


def jload(path: str):
    with open(_abs(path), encoding="utf-8") as f:
        return json.load(f)


# ---------- 4-2 Production snapshot(R-1 tree-hash)・汚染判定・mtime走査(M-4d) ----------
def tree_hashes(rel_dir: str) -> dict:
    base = _abs(rel_dir)
    out = {}
    for dp, _dn, fns in os.walk(base):
        for fn in sorted(fns):
            ap = os.path.join(dp, fn)
            out[os.path.relpath(ap, base).replace("\\", "/")] = file_sha(ap)
    return out


def prod_snapshot() -> dict:
    """R-1: 2作品のProduction run dir全体・公開ページdir全体を全ファイルsha、共有store(PROTECTED_STORES+PROTECTED_TREES)をer113のsnapshotで取る。"""
    import er113_fx_paragraph_chunk_trial_01 as t113
    return {"runs": {w: tree_hashes(c["run"]) for w, c in WORK_CFG.items()},
            "pages": {w: tree_hashes(c["pages"]) for w, c in WORK_CFG.items()},
            "stores": t113.snapshot_protected()}


def snapshot_diff(before: dict, after: dict) -> dict:
    d = {"runs": [], "pages": [], "stores": []}
    for g in ("runs", "pages"):
        for w in before[g]:
            b, a = before[g][w], after[g][w]
            d[g] += [f"{w}/{k}" for k in sorted(set(b) | set(a)) if b.get(k) != a.get(k)]
    d["stores"] = [k for k in before["stores"] if before["stores"][k] != after["stores"].get(k)]
    return d


def store_contamination(changed_keys: list, t_start: float) -> dict:
    """共有store差分の帰属判定: 本Trialの出力先path(OUT_ROOT)が差分ファイルの内容に含まれれば『本Trial由来(汚染)』、含まれなければ『他agent由来(外部変更)』。"""
    contaminated, external = [], []
    for k in changed_keys:
        files = []
        if k.startswith("tree:"):
            base = _abs(k[5:])
            for dp, _dn, fns in os.walk(base):
                for fn in fns:
                    ap = os.path.join(dp, fn)
                    try:
                        if os.path.getmtime(ap) >= t_start - 2:
                            files.append(ap)
                    except OSError:
                        pass
        else:
            files = [_abs(k)]
        hit = False
        for ap in files:
            try:
                if os.path.getsize(ap) > 80_000_000:
                    continue
                with open(ap, "rb") as f:
                    if OUT_ROOT.encode() in f.read():
                        hit = True
            except OSError:
                pass
        (contaminated if hit else external).append(k)
    return {"contaminated": contaminated, "external_changes_not_from_this_trial": external}


def scan_repo_mtime(t_start: float) -> dict:
    """M-4(d): Round 1のdirではなく本Trialの OUT_ROOT / PAGE_ROOT を除外に入れた版。Z Production run dir / Z公開ページ配下のヒットだけを厳格(STOP)対象とする。"""
    import er113_fx_paragraph_chunk_trial_01 as t113
    old = t113.SCAN_EXCLUDE_DIRS
    t113.SCAN_EXCLUDE_DIRS = tuple(old) + (OUT_ROOT, PAGE_ROOT)
    try:
        r = t113.scan_new_files(t_start - 2)
    finally:
        t113.SCAN_EXCLUDE_DIRS = old
    strict = tuple(c["run"] for c in WORK_CFG.values()) + Z_PAGES_PREFIXES
    allhits = list(r.get("suspicious", [])) + list(r.get("benign_other_agent_or_docs", []))
    r["z_production_hits"] = [h for h in allhits if h.startswith(strict)]
    r["n_other_hits_not_z"] = len([h for h in allhits if not h.startswith(strict)])
    return r


# ---------- 4-3 Production入力の読取専用再構成(Part1/Part2 freshness検査は除く。自己検証で再構成の正しさを実測する) ----------
_INP_CACHE: dict = {}


def prod_inputs(work: str, level: str) -> dict:
    """er026 load_level_inputs と同じ決定論手順(読取のみ)。b1bはProduction run が Part1/Part2導入前のため load_level_inputs の鮮度検査で止まる
    (FAMILY_Z_KP_PART1_NOT_READY)ので、story_clips/kp_items/chunk_plans/plan の再構成部だけを複製する。誤りは selfcheck の厳密一致で検出する(OK-3)。"""
    key = (work, level)
    if key in _INP_CACHE:
        return _INP_CACHE[key]
    import er026_family_z_fiction_production_runner_01 as r
    m = r._m()
    a63, w62, st = m.a63, m.w62, m.st
    c = WORK_CFG[work]
    run = c["run"]
    ctx = r.E2EContext(story_key=c["story_key"], slug=c["story_key"], run=os.path.basename(run))
    if ctx.out_dir != run:
        raise SystemExit(f"[STOP] E2EContext.out_dir({ctx.out_dir}) != WORK_CFG run({run})")
    text = w62.rd(r._level_text_path(ctx, level))
    plan_j = w62.rj(f"{run}/segment_plan_{level}.json")
    support = w62.rj(f"{run}/support/{level}_support.json")
    kp = w62.rj(f"{r._kp_assets_dir(ctx, level)}/keywords_canonicalized.json")
    items = sorted(kp["items"], key=lambda x: x["rank"])
    kp_items = [{"rank": it["rank"], "used_form": it["used_form"], "japanese_gloss": it.get("japanese_gloss", ""), "display_phrase": it["display_phrase"]} for it in items]
    expl = None
    if level == "b1b":
        ex = w62.rj(f"{run}/key_phrases/b1b/kp_explanations.json")
        expl = {int(k): v["english_explanation"] for k, v in ex["items"].items()}
    cfg = r.STORY_REGISTRY[ctx.story_key]
    comments = {int(n): tx for n, tx in support["comments"].items()}
    story_clips = plan_j["clips"]
    _t, _body = st.split_title_body(text)
    chunk_plans = a63.chunk_tts.plan_z_level(story_clips, st.clean_body_paragraphs(_body), level)
    segs = ((a63.load_results(f"{run}/{level}") or {}).get("segments")) or {}
    chunk_plans = {cid: a63.chunk_tts.effective_plan(pl, segs) for cid, pl in chunk_plans.items()}
    spec_plan = a63.build_level_plan(level, story_clips, support["preview"], comments, kp_items, cfg["topic_title"],
                                     cfg.get("japanese_title_tts") if level == "a2" else None, kp_explanations=expl,
                                     story_key=ctx.story_key, chunk_plans=chunk_plans)
    out = {"plan": spec_plan, "story_clips": story_clips, "kp_items": kp_items, "chunk_plans": a63.chunk_plans_from_specs(spec_plan),
           "article_text": r.canonical_article_text(text), "story_key": c["story_key"],
           "shell_names": list(a63.SHELL_ASSET_SOURCES) + [f"kp{it['rank']}_number" for it in kp_items]}
    _INP_CACHE[key] = out
    return out


def dialogue_specs(work: str, level: str) -> dict:
    return {s.clip_id: s for s in prod_inputs(work, level)["plan"] if s.kind == "dialogue"}


# ---------- 4-4 trial_run_dir の構築(M-1/M-2/M-3/M-4) ----------
_NARR_WAV_RE = re.compile(r"[\\/]narration[\\/]([^\\/]+\.wav)$")


def _narr(run_dir: str, level: str) -> str:
    return f"{run_dir}/{level}/narration"


def _rewrite_paths(obj, dst_narr: str) -> None:
    """M-3(2): path / narration_path / original_path の narration/<file>.wav を trial_run_dir へ書き換える(再帰)。"""
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            if k in ("path", "narration_path", "original_path") and isinstance(v, str) and _NARR_WAV_RE.search(v):
                obj[k] = f"{dst_narr}/{_NARR_WAV_RE.search(v).group(1)}"
            else:
                _rewrite_paths(v, dst_narr)
    elif isinstance(obj, list):
        for v in obj:
            _rewrite_paths(v, dst_narr)


def build_run_dir(work: str, level: str, run_name: str, adopted: dict | None) -> dict:
    """Production run の <lv>/narration/*.wav を copy(shutil.copyfileのみ)し、adopted(cid -> {gen_wav, gen_original, entry})のdialogueだけTrial音声で置換する。
    adopted=None は selfcheck(Production dialogueのまま。_original も保持)。M-2: adoptedのdialogueは Production の _original.wav を削除してから
    (Advは)生成で新しく作られた _original のみ置く。"""
    c = WORK_CFG[work]
    prod_run = c["run"]
    run_dir = f"{case_dir(work, level)}/{run_name}"
    assert_out_root(run_dir)
    if os.path.isdir(_abs(run_dir)):
        shutil.rmtree(_abs(run_dir))
    prod_narr, dst_narr = _narr(prod_run, level), _narr(run_dir, level)
    n_copied = 0
    for fn in sorted(os.listdir(_abs(prod_narr))):
        if os.path.isfile(_abs(f"{prod_narr}/{fn}")) and fn.endswith(".wav"):
            safe_copy(f"{prod_narr}/{fn}", f"{dst_narr}/{fn}")
            n_copied += 1
    res = copy.deepcopy(jload(f"{prod_run}/{level}/audit/tts_generation_results.json"))
    _rewrite_paths(res, dst_narr)
    installed = []
    for cid, ad in (adopted or {}).items():
        for fn in (f"{cid}.wav", f"{cid}_original.wav"):          # M-2: Production原音の dialogue wav / _original を除去
            ap = _abs(f"{dst_narr}/{fn}")
            if os.path.exists(ap):
                os.remove(ap)
        safe_copy(ad["gen_wav"], f"{dst_narr}/{cid}.wav")
        if ad.get("gen_original"):
            safe_copy(ad["gen_original"], f"{dst_narr}/{cid}_original.wav")
        e = copy.deepcopy(ad["entry"])
        e["path"] = e["narration_path"] = f"{dst_narr}/{cid}.wav"
        if isinstance(e.get("speed_profile"), dict) and e["speed_profile"].get("applied") and ad.get("gen_original"):
            e["original_path"] = f"{dst_narr}/{cid}_original.wav"
        res["segments"][cid] = e
        installed.append(cid)
    safe_write_json(f"{run_dir}/{level}/audit/tts_generation_results.json", res)
    ha = f"{prod_run}/{level}/audit/human_approved_segments.json"        # M-3(3)
    if os.path.exists(_abs(ha)):
        safe_copy(ha, f"{run_dir}/{level}/audit/human_approved_segments.json")
    kp_src = f"{prod_run}/{level}/key_phrases"                               # key phrase source gate の入力
    if os.path.isdir(_abs(kp_src)):
        for fn in sorted(os.listdir(_abs(kp_src))):
            if os.path.isfile(_abs(f"{kp_src}/{fn}")):
                safe_copy(f"{kp_src}/{fn}", f"{run_dir}/{level}/key_phrases/{fn}")
    os.makedirs(_abs(f"{run_dir}/{level}/assembly"), exist_ok=True)
    return {"run_dir": run_dir, "n_wav_copied": n_copied, "installed_trial": installed}


def verify_isolation(work: str, level: str, run_dir: str) -> dict:
    """M-4(b)/M-3 test: (1) trial narration の全ファイルが Production と別ファイル(inode/ nlink==1) (2) results の path 系keyが全て OUT_ROOT 配下。"""
    prod_narr, dst_narr = _narr(WORK_CFG[work]["run"], level), _narr(run_dir, level)
    bad_link, n = [], 0
    for fn in sorted(os.listdir(_abs(dst_narr))):
        d, p = _abs(f"{dst_narr}/{fn}"), _abs(f"{prod_narr}/{fn}")
        n += 1
        if os.stat(d).st_nlink > 1 or os.path.islink(d) or (os.path.exists(p) and os.path.samefile(d, p)):
            bad_link.append(fn)
    res = jload(f"{run_dir}/{level}/audit/tts_generation_results.json")
    outside = []

    def walk(o, trail=""):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("path", "narration_path", "original_path") and isinstance(v, str) and _NARR_WAV_RE.search(v) and not under(v, OUT_ROOT):
                    outside.append(f"{trail}/{k}={v}")
                else:
                    walk(v, f"{trail}/{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{trail}[{i}]")
    walk(res)
    return {"n_files": n, "hardlink_or_same_file": bad_link, "result_paths_outside_out_root": outside, "ok": not bad_link and not outside}


# ---------- 4-5 組立(M-4a/M-5)・比較・Gate(C6) ----------
def assemble_run(work: str, level: str, run_dir: str) -> dict:
    assert_out_root(run_dir)
    import er063_family_z_audio_01 as a63
    inp = prod_inputs(work, level)
    return a63.run_assembly(run_dir, level, inp["story_clips"], inp["kp_items"], story_key=inp["story_key"],
                            kp_third="explanation" if level == "b1b" else "japanese", chunk_plans=inp["chunk_plans"])


def _read_wav(path: str):
    import soundfile as sf
    x, sr = sf.read(_abs(path), dtype="float64", always_2d=True)
    return x, sr


def compare_to_production(work: str, level: str, tl: dict, *, identical: bool) -> dict:
    """identical=True(selfcheck): wav/timeline/gain/headroom 全て一致。identical=False(Trial): M-5の3点(target_rms / dialogue以外のgain / headroom.scalar)。"""
    import numpy as np
    ptl = jload(f"{WORK_CFG[work]['run']}/{level}/assembly/timeline.json")
    dlg = set(dialogue_specs(work, level))
    g_t, g_p = tl["gain_report"], ptl["gain_report"]
    nd = [k for k in g_p if k != "target_rms" and k not in dlg]
    rep = {"target_rms_trial": g_t.get("target_rms"), "target_rms_prod": g_p.get("target_rms"), "target_rms_equal": g_t.get("target_rms") == g_p.get("target_rms"),
           "n_nondialogue_gain_labels": len(nd), "nondialogue_gain_mismatch": [k for k in nd if g_t.get(k) != g_p.get(k)],
           "nondialogue_gain_missing_in_trial": [k for k in nd if k not in g_t],
           "headroom_trial": tl["headroom"], "headroom_prod": ptl["headroom"],
           "headroom_scalar_equal": tl["headroom"].get("scalar") == ptl["headroom"].get("scalar"),
           "story_clips_0_is_non_dialogue": prod_inputs(work, level)["story_clips"][0]["id"] not in dlg}
    # M-5(3) 観測後改訂(委任_03、Fable案A、PREREGISTERED_CRITERIA_02 §6): scalar不一致でも、(i)原因がTrial dialogue clipのみ(非dialogue gain不変・Production側は安全弁非作動)
    # (ii)Production安全弁(閾値同一)の設計どおりの作動 (iii)差が0.1 dB以内、の3点を満たす場合のみ『記録付き成立』。M-5(1)(2)は不変。
    ht, hp = tl["headroom"], ptl["headroom"]
    st, sp = ht.get("scalar"), hp.get("scalar")
    rep["headroom_scalar_diff_db"] = (round(20.0 * float(np.log10(st / sp)), 5) if (st and sp) else None)
    if rep["headroom_scalar_equal"]:
        rep["m5_3_recorded_exception"] = False
        m53 = True
    else:
        c_i = bool(ht.get("cause_piece") in dlg and not rep["nondialogue_gain_mismatch"] and not rep["nondialogue_gain_missing_in_trial"] and hp.get("applied") is False and sp == 1.0)
        c_ii = bool(ht.get("threshold") == hp.get("threshold") and ht.get("applied") is True and (ht.get("peak_before") or 0) > ht.get("threshold", 0)
                    and abs((ht.get("peak_after") or 0) - ht.get("threshold", 0)) < 1e-6)
        c_iii = bool(rep["headroom_scalar_diff_db"] is not None and abs(rep["headroom_scalar_diff_db"]) <= 0.1)
        rep["m5_3_conditions"] = {"i_cause_trial_dialogue_only": c_i, "ii_safety_valve_by_design": c_ii, "iii_within_0.1dB": c_iii}
        m53 = bool(c_i and c_ii and c_iii)
        rep["m5_3_recorded_exception"] = m53
    rep["m5_ok"] = bool(rep["target_rms_equal"] and not rep["nondialogue_gain_mismatch"] and not rep["nondialogue_gain_missing_in_trial"] and m53
                        and rep["story_clips_0_is_non_dialogue"])
    if identical:
        parts_t, parts_p = [(e["part"], round(e["duration_seconds"], 4)) for e in tl["timeline"]], [(e["part"], round(e["duration_seconds"], 4)) for e in ptl["timeline"]]
        rep["timeline_parts_equal"] = parts_t == parts_p
        rep["gain_report_equal"] = g_t == g_p
        rep["headroom_equal"] = tl["headroom"] == ptl["headroom"]
        xt, sr_t = _read_wav(tl["wav"])
        xp, sr_p = _read_wav(ptl["wav"])
        rep["sr_equal"] = sr_t == sr_p
        rep["shape_equal"] = xt.shape == xp.shape
        if xt.shape == xp.shape:
            d = np.abs(xt - xp)
            rep["wav_max_abs_diff"] = float(d.max())
            rep["wav_n_diff_samples"] = int((d > 0).sum())
        else:
            rep["wav_max_abs_diff"], rep["wav_n_diff_samples"] = None, None
        rep["identical_ok"] = bool(rep["timeline_parts_equal"] and rep["gain_report_equal"] and rep["headroom_equal"] and rep["sr_equal"] and rep["shape_equal"]
                                   and rep["wav_max_abs_diff"] is not None and rep["wav_max_abs_diff"] <= 3.1e-5)
    return rep


def run_gate(work: str, level: str, run_dir: str) -> dict:
    """C6: a63.run_audio_gate を trial_run_dir に適用(書込みは trial_run_dir/<lv>/audit/ のみ)。例外は握りつぶさず結果に記録する(PASS扱いにしない)。"""
    assert_out_root(run_dir)
    import er063_family_z_audio_01 as a63
    inp = prod_inputs(work, level)
    try:
        r = a63.run_audio_gate(run_dir, level, inp["plan"], inp["shell_names"], article_text=inp["article_text"])
        return {"ok": r.get("shared_gate") == "PASS", "shared_gate": r.get("shared_gate"), "audio_text_deviation_clips": r.get("audio_text_deviation_clips"),
                "n_speed_profile_clips": len((r.get("z_speed_profile") or {}).get("clips") or {})}
    except BaseException as e:      # noqa: BLE001  (STOP系の例外もGate不成立として記録)
        return {"ok": False, "error": f"{type(e).__name__}: {str(e)[:600]}"}


def mp3_from_wav(wav: str, mp3: str) -> dict:
    """R-4/M-4(c): build_pagesは呼ばず、er063 build_page_rows と同一の sf.write(..., format='MP3') を PAGE_ROOT 配下へ直接書く。"""
    import soundfile as sf
    assert_writable(mp3)
    os.makedirs(os.path.dirname(_abs(mp3)), exist_ok=True)
    x, sr = sf.read(_abs(wav), dtype="float32")
    sf.write(_abs(mp3), x, sr, format="MP3")
    return {"mp3": mp3, "wav_duration_s": round(len(x) / sr, 3), "mp3_duration_s": round(float(sf.info(_abs(mp3)).duration), 3), "bytes": os.path.getsize(_abs(mp3))}


def selfcheck_case(work: str, level: str) -> dict:
    """生成前の自己検証(API 0): Production原clipをそのまま入れて同じ run_assembly を実行し、Production組立wavと厳密一致することを確認。
    あわせて C6 Gate(Production音声で)・公開mp3長の一致(R-4)・Production版試聴用mp3(同一sf.write経路)を作る。"""
    with use_case(work, level):
        t0 = time.time()
        b = build_run_dir(work, level, "run_selfcheck", None)
        iso = verify_isolation(work, level, b["run_dir"])
        tl = assemble_run(work, level, b["run_dir"])
        cmp_ = compare_to_production(work, level, tl, identical=True)
        gate = run_gate(work, level, b["run_dir"])
        pub = f"{WORK_CFG[work]['pages']}/{LEVELS[level]['page']}/{WORK_CFG[work]['audio_prefix']}_{level}_full.mp3"
        import soundfile as sf
        pub_dur = float(sf.info(_abs(pub)).duration) if os.path.exists(_abs(pub)) else None
        ptl = jload(f"{WORK_CFG[work]['run']}/{level}/assembly/timeline.json")
        mp3 = mp3_from_wav(tl["wav"], f"{PAGE_ROOT}/{work}/{level}/production_full.mp3")
        rep = {"work": work, "level": level, "isolation": iso, "compare": cmp_, "gate": gate, "production_mp3_public": pub, "production_mp3_public_duration_s": pub_dur,
               "production_wav_duration_s": ptl["duration_seconds"],
               "public_mp3_vs_wav_diff_s": (round(abs(pub_dur - ptl["duration_seconds"]), 3) if pub_dur is not None else None),
               "production_listening_mp3": mp3, "elapsed_s": round(time.time() - t0, 1), "saved_at": t.now_jst()}
        rep["pass"] = bool(iso["ok"] and cmp_["identical_ok"] and gate["ok"] and rep["public_mp3_vs_wav_diff_s"] is not None and rep["public_mp3_vs_wav_diff_s"] < 0.3)
        safe_write_json(f"{case_dir(work, level)}/selfcheck.json", rep)
        return rep


# ---------- 4-6 TEXT同一性(R-3) ----------
def text_identity_case(work: str, level: str) -> dict:
    """Z scope内で53 clipのTTS入力を計算し、(a)Productionと同一関数 a63._norm_for_tts の結果と t.tts_text_for が一致すること (b)発音供給(PNAP)の効果=
    scope内と scope外の差 を全clipで記録する。Productionの実送信入力は保存されていないため『現行ledger copyでの再現』を比較対象とする(R-3)。"""
    import er063_family_z_audio_01 as a63
    import er003_v1_n3_01_tts_generate as n3
    import er078_secondary_run_scope_01 as sec_scope
    import er109_xz_scope_01 as scope
    with use_case(work, level):
        plan = t.load_plan()
        specs = dialogue_specs(work, level)
        res = t.load_json(t.TTS_RESULTS_PATH)["segments"]
        rows = []

        def _in_scope(_d=None):
            for x in dialogue_clips(plan):
                sp = specs[x["id"]]
                rows.append({"clip_id": x["id"], "canonical": x["text"], "tts_in_scope": a63._norm_for_tts(sp), "tts_text_for": t.tts_text_for(x),
                             "tts_safe_only": n3.tts_safe_news_en(x["text"])})
        sec_scope.with_secondary_run(scope.family_scope("Z")(_in_scope))(None)
        out = []
        for r_ in rows:
            e = res.get(r_["clip_id"]) or {}
            out.append({**r_, "same_function_equal": r_["tts_in_scope"] == r_["tts_text_for"], "pnap_effect": r_["tts_in_scope"] != r_["tts_safe_only"],
                        "reused_from_previous_run": e.get("reused_from_previous_run"), "production_status": e.get("status")})
        rep = {"work": work, "level": level, "n": len(out), "all_same_function_equal": all(o["same_function_equal"] for o in out),
               "n_pnap_effect": sum(1 for o in out if o["pnap_effect"]), "rows": out,
               "note": "Productionの実送信TTS入力は未保存のため、現行ledger copy(Z scope内)での再現値。pnap_effect=発音供給(綴り置換)が掛かるclip"}
        safe_write_json(f"{case_dir(work, level)}/text_identity.json", rep)
        return rep


# ---------- 4-7 費用(R-6) ----------
def spent_now() -> tuple:
    import er019_family_x_audio_production_runner_01 as runner
    return runner.compute_cost_jpy_so_far(_abs(COST_LOG))


def est_next_clip_jpy(prompt: str, audio_s: float) -> float:
    return t.est_tts_jpy(len(prompt), audio_s * 1.05)


def _ref_audio_s(work: str, level: str, cid: str) -> float:
    narr = t.NARR_DIR
    orig = f"{narr}/{cid}_original.wav"
    x, sr = t.read_mono(orig if os.path.isfile(_abs(orig)) else f"{narr}/{cid}.wav")
    return len(x) / sr


# ---------- 4-8 生成 ----------
def gen_dir(work: str, level: str, cid: str) -> str:
    return f"{case_dir(work, level)}/gen/{cid}"


def gen_wav_path(work: str, level: str, cid: str) -> str:
    """M-1: clipごとの別ディレクトリ(Round 2と同形。review lock用の <run>/<lv>/narration/<id>.wav 配置)。"""
    return f"{gen_dir(work, level, cid)}/{level}/narration/{cid}.wav"


def trial_reuse_key(clip: dict, style: str, voice: str) -> dict:
    """M-6: 本module版(Round 1のMANAGED_IDが入る t.trial_reuse_key は使わない)。"""
    return {"managed_id": MANAGED_ID, "arm": "ctx", "take": 1, "canonical_text_sha256": t.sha_text(clip["text"]), "voice": voice, "model": t.TTS_MODEL,
            "style_sha256": t.sha_text(style), "tts_backend_note": "gemini_standard_sync(Production Z実行と同じSTANDARD)"}


def adopt_decision(rec: dict) -> dict:
    """M-1/M-7/M-8: 組立入力に採用してよいか。C1(status OK)・C2(Production ASRカスケードの最終判定PASS系[=status OK] かつ repetition QA済み)・
    C3(leakage_final.flagged無し。flaggedは『保留=Fable聴取確認待ち』で採用しない)・C4(comparison_valid)。token_equal/similarityは観測値でblockingに使わない。"""
    reasons = []
    if rec.get("status") != "OK":
        reasons.append("C1:status!=OK")
    if not rec.get("repetition_qa_checked"):
        reasons.append("C2:repetition_qa未実施")
    if not rec.get("comparison_valid"):
        reasons.append("C4:comparison_valid=false")
    hold = bool((rec.get("leakage") or {}).get("leakage_final"))
    if hold:
        reasons.append("C3:leakage_final.flagged(保留・Fable聴取確認待ち)")
    return {"adopted": not reasons, "hold_pending_fable_listen": hold, "reasons": reasons}


def _load_notes(work: str, level: str) -> dict:
    """M-6: t.load_reviewed_notes を path 明示で呼ぶ(既定pathはRound 1)。Fable全件accept/discard記入済みを要求(require_review=True)。"""
    d = f"{case_dir(work, level)}/llm"
    return t.load_reviewed_notes(f"{d}/emotion_notes.json", f"{d}/emotion_review.json", require_review=True)


def _make_live_gen_fn(level: str, cid: str):
    import er003_v1_n3_01_tts_generate as n3_tts
    import er012_b_family_voices_production_01 as bvoices
    import er063_family_z_audio_01 as a63

    def fn(text: str, wav_rel: str, voice: str, style: str) -> dict:
        if level == "b1b":
            # Production dialogue() と同形(er063:917-928): 速度後ASR再検証つき外側ループ・通算TTS3回・atempo=1.06。style_prefix_overrideのみ差(ctx方式)。
            return n3_tts.generate_with_a2_slowdown_outer_loop(
                cid, text, wav_rel,
                lambda max_attempts: bvoices.generate_voice_body_wide_margin(text, wav_rel, voice, max_attempts=max_attempts, style_prefix_override=style),
                slowdown_pct=a63.Z_ADV_DIALOGUE_SLOWDOWN_PCT)
        return bvoices.generate_voice_body_wide_margin(text, wav_rel, voice, style_prefix_override=style)   # Std: 速度後処理なし(Productionと同形)
    return fn


def _ensure_selfcheck_and_dryrun(work: str, level: str) -> None:
    sc = f"{case_dir(work, level)}/selfcheck.json"
    if not os.path.exists(_abs(sc)) or not jload(sc).get("pass"):
        raise SystemExit(f"[STOP] {sc} が無い/不成立。生成前の自己検証(preflight)に合格するまで有料生成は起動しない")
    dr = f"{OUT_ROOT}/dryrun_sinks.json"
    if not os.path.exists(_abs(dr)) or not jload(dr).get("pass"):
        raise SystemExit(f"[STOP] {dr} が無い/不成立。R-2のdry-run(書込先3経路の実測)に合格するまで有料生成は起動しない")
    ti = f"{case_dir(work, level)}/text_identity.json"
    if not os.path.exists(_abs(ti)):
        raise SystemExit(f"[STOP] {ti} が無い(R-3)")


def _wait_interval() -> float:
    """起動間隔(150秒以上): 他unitのgen_summaryの最新finished_epochから経過が足りなければ待つ。"""
    last = 0.0
    for w, lv in CASES:
        p = f"{case_dir(w, lv)}/gen_summary.json"
        if os.path.exists(_abs(p)):
            last = max(last, float(jload(p).get("finished_epoch") or 0))
    wait = max(0.0, last + MIN_UNIT_INTERVAL_S - time.time())
    if wait > 0:
        print(f"[WAIT] 前unit終了から{MIN_UNIT_INTERVAL_S}秒未満。{wait:.0f}秒待機", flush=True)
        time.sleep(wait)
    return wait


def gen_case(work: str, level: str, *, gen_fn_factory=None, only: list | None = None, go: dict | None = None) -> dict:
    """1作品×レベルのセリフ全件を ctx方式で新規生成(1 take)。gen_fn_factory(level, cid)->fn(text, wav_rel, voice, style)->result: testのinjection用
    (本番はNone=Production関数。このときだけ GO・STOP確認・自己検証確認・sink隔離・Zscope・実費Guardrailを適用)。1 clipのNGでは中断しない。"""
    live = gen_fn_factory is None
    import er078_secondary_run_scope_01 as sec_scope
    import er109_xz_scope_01 as scope
    if live:
        go = _require_go(SCOPE_PHASE1B, PHASE1B_CAP_JPY)
        _ensure_selfcheck_and_dryrun(work, level)
        _stop_check(f"stop_check_gen_{work}_{level}.json")
        waited = _wait_interval()
    else:
        waited = 0.0
    cap = float(go["cap_jpy"]) if go else 1e9
    started_epoch = time.time()
    specs_all = dialogue_specs(work, level)
    results: dict = {}
    reqs: list = []
    cur = {"label": None}
    before = after = None
    spent0 = spent_now()[0] if live else 0.0
    baseline_path = f"{OUT_ROOT}/phase1b_baseline.json"
    if live:
        if not os.path.exists(_abs(baseline_path)):
            safe_write_json(baseline_path, {"spent_before_phase1b_jpy": spent0, "saved_at": t.now_jst(), "scope": SCOPE_PHASE1B})
        base_total = jload(baseline_path)["spent_before_phase1b_jpy"]
    else:
        base_total = 0.0

    with use_case(work, level):
        plan = t.load_plan()
        notes = _load_notes(work, level) if live else (gen_fn_factory.notes if hasattr(gen_fn_factory, "notes") else {})
        clip_by_id = {c_["id"]: c_ for c_ in plan["clips"]}
        tts_voice = {cid: t.tts_voice(clip_by_id[cid]) for cid in specs_all}
        for cid, sp in specs_all.items():
            if sp.voice != tts_voice[cid]:
                raise SystemExit(f"[STOP] Voice不一致 {cid}: spec={sp.voice} / Production結果={tts_voice[cid]}")

        def _run(_d=None):
            runner_cl = None
            if live:
                import er005_cost_logger as cl_mod
                runner_cl = cl_mod
            for x in dialogue_clips(plan):
                cid = x["id"]
                if only and cid not in only:
                    continue
                sp = specs_all[cid]
                ctx = t.extract_context(plan, cid)
                note = notes.get(cid)
                style = t.style_for_arm("ctx", ctx, note)
                text = a63_norm(sp)
                prompt_expected = t.build_prompt(text, style)
                spent_clip0 = spent_now()[0] if live else 0.0
                if live:
                    if spent_clip0 - base_total >= cap:
                        raise SystemExit(f"[STOP] Phase 1b Guardrail {cap}円到達(実績{spent_clip0 - base_total:.2f}円)。暴走疑いの有無を確認して報告")
                    est = est_next_clip_jpy(prompt_expected, _ref_audio_s(work, level, cid))
                    if spent_clip0 - base_total + est > cap:
                        raise SystemExit(f"[STOP] 次clip({cid})見積{est:.2f}円を足すと Guardrail {cap}円を超える(実績{spent_clip0 - base_total:.2f}円)")
                wav = gen_wav_path(work, level, cid)
                assert_out_root(wav)
                os.makedirs(os.path.dirname(_abs(wav)), exist_ok=True)
                cur["label"] = f"{work}/{level}:{cid}"
                n_before = len(reqs)
                t0 = time.time()
                fn = gen_fn_factory(level, cid) if not live else _make_live_gen_fn(level, cid)
                if live:
                    with runner_cl.segment_context(cid):
                        res = fn(text, wav, tts_voice[cid], style) or {}
                else:
                    res = fn(text, wav, tts_voice[cid], style) or {}
                sent = reqs[n_before:]
                attempts_asr = [a.get("asr_text") for a in (res.get("attempts_log") or []) if isinstance(a, dict)]
                leak = t.leakage_all_attempts(attempts_asr, res.get("asr_text"), ctx, note) if (res.get("asr_text") is not None or attempts_asr) else None
                import er063_family_z_audio_01 as a63
                entry = a63.build_entry(sp, wav, res) if res.get("status") is not None else None
                if entry is not None:
                    entry["trial_style_sha256"] = t.sha_text(style)
                    entry["trial_reuse_key"] = trial_reuse_key(clip_by_id[cid], style, tts_voice[cid])
                orig = f"{os.path.dirname(wav)}/{cid}_original.wav"
                rec = {"managed_id": MANAGED_ID, "work": work, "level": level, "clip_id": cid, "speaker": x["speaker"], "voice": tts_voice[cid],
                       "status": res.get("status"), "wav": wav, "wav_sha256": file_sha(wav),
                       "original_wav": orig if os.path.exists(_abs(orig)) else None, "original_sha256": file_sha(orig),
                       "tts_text": text, "style_sha256": t.sha_text(style), "prompt_expected_sha256": t.sha_text(prompt_expected),
                       "requests_sent": [{k: v for k, v in q.items() if k != "prompt"} for q in sent],
                       "request_prompt_matches_expected": [q["prompt_sha256"] == t.sha_text(prompt_expected) for q in sent],
                       "n_tts_calls_captured": len(sent), "tts_generations_used": res.get("tts_generations_used"),
                       "attempts_log_n": len(res.get("attempts_log") or []), "slowdown_attempts_n": len(res.get("slowdown_attempts_log") or []),
                       "asr_text": res.get("asr_text"), "attempts_asr_texts": attempts_asr, "audio_classification": res.get("audio_classification"),
                       "asr_judgement": res.get("asr_judgement"), "instruction_type": res.get("instruction_type"),
                       "repetition_qa_checked": res.get("repetition_qa_checked"), "trim_info": res.get("trim_info"),
                       "leakage": leak, **t.comparison_validity(res, sent, t.sha_text(prompt_expected)),
                       "verbatim_observation": t.verbatim_check(res.get("asr_text") or "", x["text"]) if res.get("asr_text") is not None else None,
                       "reason": res.get("reason"), "tts_cap_reached": res.get("tts_generation_cap_reached"),
                       "cost_jpy_clip": round((spent_now()[0] - spent_clip0) if live else 0.0, 4),
                       "elapsed_s": round(time.time() - t0, 2), "saved_at": t.now_jst(), "entry": entry,
                       "trial_reuse_key": trial_reuse_key(clip_by_id[cid], style, tts_voice[cid])}
                rec["adopt"] = adopt_decision(rec)
                safe_write_json(f"{gen_dir(work, level, cid)}/request_full.json", {"clip_id": cid, "requests": sent})
                safe_write_json(f"{gen_dir(work, level, cid)}/result.json", rec)
                results[cid] = rec
                print(f"[GEN] {work}/{level} {cid} status={rec['status']} calls={rec['n_tts_calls_captured']} gens={rec['tts_generations_used']} "
                      f"adopt={rec['adopt']['adopted']} cost={rec['cost_jpy_clip']} t={rec['elapsed_s']}s", flush=True)

        with contextlib.ExitStack() as stack:
            if live:
                import er005_cost_logger as cl_mod
                import er113_fx_paragraph_chunk_trial_01 as t113
                from dotenv import load_dotenv
                load_dotenv()
                cl_mod.install(_abs(COST_LOG))
                before = prod_snapshot()
                stack.enter_context(t113.redirect_production_sinks(f"{case_dir(work, level)}/sinks"))
                stack.enter_context(t.capture_tts_requests(reqs, lambda: cur["label"]))
            sec_scope.with_secondary_run(scope.family_scope("Z")(_run))(gen_dir(work, level, "_"))

    finished = time.time()
    by_prov_after = spent_now()[1] if live else {}
    summary = {"managed_id": MANAGED_ID, "work": work, "level": level, "started_epoch": started_epoch, "finished_epoch": finished,
               "started_at_jst": datetime.datetime.fromtimestamp(started_epoch, datetime.timezone(datetime.timedelta(hours=9))).isoformat(timespec="seconds"),
               "wall_s": round(finished - started_epoch, 1), "waited_for_interval_s": round(waited, 1), "live": live,
               "n_clips": len(results), "n_ok": sum(1 for r_ in results.values() if r_["status"] == "OK"), "n_adopted": sum(1 for r_ in results.values() if r_["adopt"]["adopted"]),
               "n_hold": sum(1 for r_ in results.values() if r_["adopt"]["hold_pending_fable_listen"]),
               "spent_unit_jpy": round(spent_now()[0] - spent0, 4) if live else 0.0, "spent_phase1b_total_jpy": round(spent_now()[0] - base_total, 4) if live else 0.0,
               "spent_by_provider_cumulative": by_prov_after, "tts_model_requested": t.TTS_MODEL}
    if live:
        after = prod_snapshot()
        diff = snapshot_diff(before, after)
        contam = store_contamination(diff["stores"], started_epoch)
        scan = scan_repo_mtime(started_epoch)
        summary.update({"snapshot_diff": diff, "store_attribution": contam, "mtime_z_production_hits": scan["z_production_hits"],
                        "mtime_n_other_hits": scan["n_other_hits_not_z"], "mtime_total": scan["n_total"]})
        bad = diff["runs"] + diff["pages"] + contam["contaminated"] + scan["z_production_hits"]
        if bad:
            summary["STOP"] = f"Production保護対象が変化/汚染: {bad[:10]}"
    safe_write_json(f"{case_dir(work, level)}/gen_summary.json", summary)
    if summary.get("STOP"):
        raise SystemExit(f"[STOP] {summary['STOP']}")
    return {"summary": summary, "results": results}


def a63_norm(spec) -> str:
    """Productionと同一の TTS 入力整形(er063 _norm_for_tts。Z scope内で発音供給が有効)。"""
    import er063_family_z_audio_01 as a63
    return a63._norm_for_tts(spec)



# ---------- 4-11 生成結果の読込・採用判定・DEV隔離組立(M-1〜M-5)・C6・mp3 ----------
def load_gen_results(work: str, level: str) -> dict:
    out = {}
    for cid in dialogue_specs(work, level):
        rp = f"{gen_dir(work, level, cid)}/result.json"
        if not os.path.exists(_abs(rp)):
            raise SystemExit(f"[STOP] {rp} が無い(gen未完了のunitは組立しない)")
        out[cid] = jload(rp)
    return out


def final_adoption(rec: dict, clearance: dict) -> dict:
    """生成時の adopt 判定に Fable の聴取確認(fable_clearance.json)を反映した最終判定。cleared は C3保留のみが理由の場合に採用、confirmed_leak はNG。"""
    ad = rec["adopt"]
    cl = clearance.get(rec["clip_id"])
    other = [r_ for r_ in ad["reasons"] if not r_.startswith("C3:")]
    if ad["adopted"]:
        return {"adopted": True, "kind": "adopted", "reasons": []}
    if ad["hold_pending_fable_listen"] and not other:
        if cl == "cleared":
            return {"adopted": True, "kind": "adopted_after_fable_clearance", "reasons": []}
        if cl == "confirmed_leak":
            return {"adopted": False, "kind": "ng_confirmed_leak", "reasons": ["C3:Fable聴取でconfirmed_leak"]}
        return {"adopted": False, "kind": "hold_pending_fable_listen", "reasons": ad["reasons"]}
    return {"adopted": False, "kind": "ng", "reasons": ad["reasons"]}


def _slice_mp3(x, sr, start_s: float, dur_s: float, mp3: str) -> None:
    import soundfile as sf
    assert_writable(mp3)
    os.makedirs(os.path.dirname(_abs(mp3)), exist_ok=True)
    sf.write(_abs(mp3), x[int(round(start_s * sr)): int(round((start_s + dur_s) * sr))], sr, format="MP3")


def assemble_case(work: str, level: str) -> dict:
    """採用clipだけをTrial音声に置換した trial_run_dir を作り、Productionと同一の run_assembly で通し組立(API 0)。M-1 sha assert → M-4 隔離検査 →
    M-5 3点assert(不一致はSTOP) → C6 Gate → mp3(Trial版・個別A/B)。"""
    import numpy as np
    import soundfile as sf
    sc = f"{case_dir(work, level)}/selfcheck.json"
    if not os.path.exists(_abs(sc)) or not jload(sc).get("pass"):
        raise SystemExit(f"[STOP] {sc} 不成立。組立しない")
    with use_case(work, level):
        recs = load_gen_results(work, level)
        cpath = f"{case_dir(work, level)}/fable_clearance.json"
        clearance = jload(cpath) if os.path.exists(_abs(cpath)) else {}
        decisions = {cid: final_adoption(rec, clearance) for cid, rec in recs.items()}
        adopted = {cid: {"gen_wav": recs[cid]["wav"], "gen_original": recs[cid].get("original_wav"), "entry": recs[cid]["entry"]} for cid, d in decisions.items() if d["adopted"]}
        b = build_run_dir(work, level, "run", adopted)
        run_dir = b["run_dir"]
        narr = _narr(run_dir, level)
        sha_assert = {}
        for cid in adopted:                           # M-1: dialogue wavのsha == 採用済みTrial結果のsha
            got, want, ent = file_sha(f"{narr}/{cid}.wav"), recs[cid]["wav_sha256"], recs[cid]["entry"].get("sha256")
            sha_assert[cid] = bool(got == want == ent)
            if not sha_assert[cid]:
                raise SystemExit(f"[STOP] M-1 sha不一致 {cid}: trial_dir={got} result={want} entry={ent}")
        iso = verify_isolation(work, level, run_dir)
        if not iso["ok"]:
            raise SystemExit(f"[STOP] M-4 隔離検査NG: {iso}")
        prod_sha_by_name = {fn: file_sha(f"{_narr(WORK_CFG[work]['run'], level)}/{fn}") for fn in os.listdir(_abs(_narr(WORK_CFG[work]['run'], level)))}
        orig_clash = [cid for cid in adopted if os.path.exists(_abs(f"{narr}/{cid}_original.wav")) and file_sha(f"{narr}/{cid}_original.wav") in set(prod_sha_by_name.values())]
        tl = assemble_run(work, level, run_dir)
        cmp_ = compare_to_production(work, level, tl, identical=False)
        res = {"managed_id": MANAGED_ID, "work": work, "level": level, "run_dir": run_dir, "decisions": decisions, "n_adopted": len(adopted),
               "n_ng": sum(1 for d in decisions.values() if d["kind"] in ("ng", "ng_confirmed_leak")),
               "n_hold": sum(1 for d in decisions.values() if d["kind"] == "hold_pending_fable_listen"),
               "sha_assert_m1": sha_assert, "original_clash_with_production": orig_clash, "isolation": iso, "compare_m5": cmp_, "saved_at": t.now_jst()}
        if not cmp_["m5_ok"]:
            res["STOP"] = "M-5: 『差はセリフclipのみ』が組立で崩れた(target_rms/非dialogue gain/headroom.scalar のいずれか不一致)"
            safe_write_json(f"{case_dir(work, level)}/assemble_result.json", res)
            raise SystemExit(f"[STOP] {res['STOP']}: {json.dumps(cmp_, ensure_ascii=False)[:800]}")
        gate = run_gate(work, level, run_dir)
        x_t, sr = sf.read(_abs(tl["wav"]), dtype="float32")
        peak = float(np.max(np.abs(x_t)))
        prod_tl = jload(f"{case_dir(work, level)}/run_selfcheck/{level}/assembly/timeline.json")
        x_p, sr_p = sf.read(_abs(prod_tl["wav"]), dtype="float32")
        pg = f"{PAGE_ROOT}/{work}/{level}"
        trial_mp3 = mp3_from_wav(tl["wav"], f"{pg}/trial_full.mp3")
        if not os.path.exists(_abs(f"{pg}/production_full.mp3")):
            raise SystemExit("[STOP] production_full.mp3 が無い(selfcheck未実施)")
        te = {e["part"]: e for e in tl["timeline"]}
        pe = {e["part"]: e for e in prod_tl["timeline"]}
        chapters = []
        for i, cid in enumerate(recs, 1):
            d = decisions[cid]
            row = {"n": i, "clip_id": cid, "kind": d["kind"], "trial_start": round(te[cid]["start_seconds"], 3), "trial_dur": round(te[cid]["duration_seconds"], 3),
                   "prod_start": round(pe[cid]["start_seconds"], 3), "prod_dur": round(pe[cid]["duration_seconds"], 3)}
            _slice_mp3(x_p, sr_p, pe[cid]["start_seconds"], pe[cid]["duration_seconds"], f"{pg}/clips/{cid}_prod.mp3")
            if d["adopted"]:
                _slice_mp3(x_t, sr, te[cid]["start_seconds"], te[cid]["duration_seconds"], f"{pg}/clips/{cid}_trial.mp3")
            elif d["kind"] == "hold_pending_fable_listen" and recs[cid].get("wav") and os.path.exists(_abs(recs[cid]["wav"])):
                xw, srw = sf.read(_abs(recs[cid]["wav"]), dtype="float32")
                os.makedirs(os.path.dirname(_abs(f"{pg}/held/x")), exist_ok=True)
                sf.write(_abs(f"{pg}/held/{cid}_generated_unverified.mp3"), xw, srw, format="MP3")
            chapters.append(row)
        res.update({"gate_c6": gate, "peak_trial_wav": round(peak, 4), "c5_peak_ok": bool(peak <= 0.99), "trial_wav": tl["wav"], "trial_duration_s": tl["duration_seconds"],
                    "prod_reassembled_wav": prod_tl["wav"], "prod_duration_s": prod_tl["duration_seconds"], "trial_mp3": trial_mp3, "chapters": chapters})
        safe_write_json(f"{case_dir(work, level)}/assemble_result.json", res)
        summary = {"n_adopted": res["n_adopted"], "n_ng": res["n_ng"], "n_hold": res["n_hold"], "m5_ok": cmp_["m5_ok"], "gate_ok": gate["ok"], "peak": res["peak_trial_wav"],
                   "trial_s": tl["duration_seconds"], "prod_s": prod_tl["duration_seconds"]}
        return {"summary": summary, "result": res}


# ---------- 4-12 解析(API 0): 指標・N1〜N6・費用(R-6) ----------
def _mono(x):
    return x.mean(axis=1) if getattr(x, "ndim", 1) > 1 else x


def _rms_db(x) -> float:
    import numpy as np
    return 20 * math.log10(max(float(np.sqrt(np.mean(np.square(x)))) if len(x) else 0.0, 1e-9))


def _edge_window(seg, sr: int, which: str, dur: float = 0.3, thr_db: float = -40.0):
    import numpy as np
    f = int(sr * 0.02)
    n = len(seg) // f
    if n == 0:
        return seg
    fr = seg[:n * f].reshape(n, f)
    db = 20 * np.log10(np.sqrt((fr ** 2).mean(axis=1)) + 1e-9)
    idx = np.where(db > thr_db)[0]
    if len(idx) == 0:
        return seg
    a, b = int(idx[0] * f), int((idx[-1] + 1) * f)
    w = int(sr * dur)
    return seg[a:a + w] if which == "head" else seg[max(a, b - w):b]


def boundary_steps(wav: str, timeline: list, dlg_ids: set) -> dict:
    """N3: セリフclipと直前/直後の地の文clipの境界RMS段差(dB、clip内の無音を除いた先頭/末尾300ms窓)。"""
    x, sr = _read_wav(wav)
    xm = _mono(x)
    parts = [e for e in timeline if not e["part"].startswith("_silence_")]

    def seg(e):
        return xm[int(round(e["start_seconds"] * sr)): int(round((e["start_seconds"] + e["duration_seconds"]) * sr))]
    out = {}
    for i, e in enumerate(parts):
        if e["part"] not in dlg_ids:
            continue
        d, rec = seg(e), {}
        if i > 0 and parts[i - 1]["part"] not in dlg_ids:
            rec["prev_part"] = parts[i - 1]["part"]
            rec["step_in_db"] = round(abs(_rms_db(_edge_window(d, sr, "head")) - _rms_db(_edge_window(seg(parts[i - 1]), sr, "tail"))), 2)
        if i + 1 < len(parts) and parts[i + 1]["part"] not in dlg_ids:
            rec["next_part"] = parts[i + 1]["part"]
            rec["step_out_db"] = round(abs(_rms_db(_edge_window(seg(parts[i + 1]), sr, "head")) - _rms_db(_edge_window(d, sr, "tail"))), 2)
        out[e["part"]] = rec
    return out


def cost_breakdown(work: str, level: str) -> dict:
    """R-6(a)(b): raw_usage_log.jsonl のprovider別実績(unitの時間窓内)。clip別(segment)のTTS call数・ASR call数・円。"""
    import er019_family_x_audio_production_runner_01 as runner
    import er005_cost_logger as cl
    gs = jload(f"{case_dir(work, level)}/gen_summary.json")
    lo, hi = gs["started_epoch"] - 1, gs["finished_epoch"] + 1
    price = runner._load_pricing()
    seg = {}
    tot = {}
    with open(_abs(COST_LOG), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            ts = datetime.datetime.fromisoformat(rec["timestamp"]).timestamp()
            if not (lo <= ts <= hi):
                continue
            provider = rec.get("provider")
            model = rec.get("model_id") or rec.get("model")
            usd = rec["cost_usd"] if rec.get("cost_usd") is not None else 0.0
            if rec.get("cost_usd") is None:
                if provider == "azure":
                    usd = cl.azure_stt_cost_usd(rec, price)
                elif provider in ("gemini", "openai", "openai_asr") and model:
                    usd = (rec.get("input_tokens") or 0) * price(provider, model, "input_tokens") / 1e6 + (rec.get("output_tokens") or 0) * price(provider, model, "output_tokens") / 1e6
            jpy = usd * runner.USD_JPY
            s = seg.setdefault(rec.get("segment"), {})
            kind = "tts" if provider == "gemini" else ("asr_openai" if provider == "openai_asr" else ("asr_azure" if provider == "azure" else provider))
            e = s.setdefault(kind, {"calls": 0, "jpy": 0.0})
            e["calls"] += 1
            e["jpy"] += jpy
            e2 = tot.setdefault(kind, {"calls": 0, "jpy": 0.0})
            e2["calls"] += 1
            e2["jpy"] += jpy
    for d in (seg, ):
        for s in d.values():
            for e in s.values():
                e["jpy"] = round(e["jpy"], 4)
    return {"by_segment": seg, "by_kind": {k: {"calls": v["calls"], "jpy": round(v["jpy"], 4)} for k, v in tot.items()}, "window_epoch": [lo, hi]}


def _cv(vals: list):
    import numpy as np
    return round(float(np.std(vals) / np.mean(vals)), 4) if len(vals) >= 2 and np.mean(vals) else None


def _sd_semitones(f0s: list):
    import numpy as np
    s = [12 * math.log2(v) for v in f0s if v]
    return round(float(np.std(s)), 3) if len(s) >= 2 else None


def analyze_case(work: str, level: str) -> dict:
    import numpy as np
    with use_case(work, level):
        plan = t.load_plan()
        specs = dialogue_specs(work, level)
        recs = load_gen_results(work, level)
        ar = jload(f"{case_dir(work, level)}/assemble_result.json")
        notes = jload(f"{case_dir(work, level)}/llm/emotion_notes.json")["validated"]
        prod_narr = _narr(WORK_CFG[work]["run"], level)
        band = jload(f"{OUT_ROOT}/noise_band_r2.json")
        band_sha = file_sha(f"{OUT_ROOT}/noise_band_r2.json")
        costs = cost_breakdown(work, level)
        clips = {}
        for x in dialogue_clips(plan):
            cid = x["id"]
            rec = recs[cid]
            nw = t.n_words(x["text"])
            p_ref = f"{prod_narr}/{cid}_original.wav"
            p_ref = p_ref if os.path.exists(_abs(p_ref)) else f"{prod_narr}/{cid}.wav"
            t_ref = rec.get("original_wav") or rec.get("wav")
            m_p = t.analyze_wav(p_ref, nw)
            m_t = t.analyze_wav(t_ref, nw) if t_ref and os.path.exists(_abs(t_ref)) else None
            for _m in (m_p, m_t):
                if _m:
                    _m['rms_lin'] = round(10 ** (_m['rms_dbfs'] / 20), 6)
            ratios, flags = {}, {}
            if m_t:
                for k, f in NOISE_METRICS.items():
                    a, b = f(m_p), f(m_t)
                    ratios[k] = round(math.log(b / a), 4) if a and b and a > 0 and b > 0 else None
                wr = (m_t["articulation_wpm_300"] / m_p["articulation_wpm_300"]) if m_p["articulation_wpm_300"] else None
                flags = {"N2a_new_long_pause": bool(m_t["max_mid_pause_s"] > 0.7 and not m_p["max_mid_pause_s"] > 0.7),
                         "N2b_wpm_outside_0.6_1.6": bool(wr is not None and not (0.6 <= wr <= 1.6)),
                         "N2c_length_listen": bool(t.length_listen_flag(m_t["duration_s"], [m_p["duration_s"]]))}
            clips[cid] = {"speaker": x["speaker"], "voice": rec["voice"], "text": x["text"], "words": nw, "emotion_status": notes[cid]["status"],
                          "prod": m_p, "trial": m_t, "log_ratio": ratios, "flags": flags, "adopt": ar["decisions"][cid],
                          "n_tts_calls_log": (costs["by_segment"].get(cid) or {}).get("tts", {}).get("calls"),
                          "cost_jpy": round(sum(v["jpy"] for v in (costs["by_segment"].get(cid) or {}).values()), 4),
                          "verbatim_observation": rec.get("verbatim_observation"), "asr_judgement_state": (rec.get("asr_judgement") or {}).get("state"),
                          "leakage_final": (rec.get("leakage") or {}).get("leakage_final"), "leakage_any_attempt": (rec.get("leakage") or {}).get("leakage_any_attempt"),
                          "instruction_type": rec.get("instruction_type"), "elapsed_s": rec.get("elapsed_s")}
        # N1 話者内ばらつき(両側全件併記。判定列は補助)
        n1 = {}
        for spk in sorted({c["speaker"] for c in clips.values()}):
            cs = [c for c in clips.values() if c["speaker"] == spk and c["trial"]]
            if len(cs) < 3:
                continue
            tw, pw = [c["trial"]["articulation_wpm_300"] for c in cs], [c["prod"]["articulation_wpm_300"] for c in cs]
            tf, pf = [c["trial"]["f0"]["median_hz"] for c in cs], [c["prod"]["f0"]["median_hz"] for c in cs]
            row = {"n_clips": len(cs), "trial_wpm_cv": _cv(tw), "prod_wpm_cv": _cv(pw), "trial_f0_sd_semitones": _sd_semitones(tf), "prod_f0_sd_semitones": _sd_semitones(pf),
                   "trial_wpm_values": tw, "prod_wpm_values": pw, "trial_f0_values": tf, "prod_f0_values": pf}
            a, b, c_, d_ = row["trial_wpm_cv"], row["prod_wpm_cv"], row["trial_f0_sd_semitones"], row["prod_f0_sd_semitones"]
            row["unstable_speaker_flag"] = bool((a is not None and b is not None and a > 2 * b and a - b > 0.05) or (c_ is not None and d_ is not None and c_ > 2 * d_ and c_ - d_ > 1.0))
            n1[spk] = row
        # N3 境界RMS段差(組立後wav同士。Trial版 vs 再組立Production版)
        dlg = set(specs)
        prod_tl = jload(f"{case_dir(work, level)}/run_selfcheck/{level}/assembly/timeline.json")
        tr_tl = jload(f"{ar['run_dir']}/{level}/assembly/timeline.json")
        bs_t, bs_p = boundary_steps(tr_tl["wav"], tr_tl["timeline"], dlg), boundary_steps(prod_tl["wav"], prod_tl["timeline"], dlg)
        n3_rows, n_over, n_total = {}, 0, 0
        for cid in dlg:
            r_ = {}
            for k in ("step_in_db", "step_out_db"):
                if k in bs_t.get(cid, {}) and k in bs_p.get(cid, {}):
                    d = round(bs_t[cid][k] - bs_p[cid][k], 2)
                    r_[k] = {"trial": bs_t[cid][k], "prod": bs_p[cid][k], "delta": d, "over_3db": bool(d > 3.0 and ar["decisions"][cid]["adopted"])}
                    n_total += 1
                    n_over += int(r_[k]["over_3db"])
            n3_rows[cid] = r_
        # N4 感情あり/なし別の |log比| 中央値
        def med_abs(group):
            vals = {k: [abs(c["log_ratio"][k]) for c in group if c["log_ratio"].get(k) is not None] for k in NOISE_METRICS}
            return {k: (round(float(np.median(v)), 4) if v else None) for k, v in vals.items()} | {"n": len(group)}
        measured = [c for c in clips.values() if c["trial"]]
        n4 = {"emotion_accepted": med_abs([c for c in measured if c["emotion_status"] == "ACCEPTED"]), "no_explicit_cue": med_abs([c for c in measured if c["emotion_status"] != "ACCEPTED"]),
              "noise_band_median": {k: band["metrics"][k]["median"] for k in NOISE_METRICS}, "noise_band_p90": {k: band["metrics"][k]["p90"] for k in NOISE_METRICS},
              "prediction": "感情ありのほうが|log比|が大きい(外れても結果として報告)"}
        # N5/N6
        calls = [c["n_tts_calls_log"] for c in clips.values() if c["n_tts_calls_log"]]
        n5 = {"n_clips": len(clips), "tts_calls_total_raw_log": sum(calls), "k_ctx": round(sum(calls) / len(clips), 4) if clips else None,
              "first_try_ok": sum(1 for v in calls if v == 1), "first_try_rate": round(sum(1 for v in calls if v == 1) / len(clips), 4),
              "regen_clips": {cid: c["n_tts_calls_log"] for cid, c in clips.items() if (c["n_tts_calls_log"] or 0) > 1},
              "ng_clips": [cid for cid, c in clips.items() if c["adopt"]["kind"] in ("ng", "ng_confirmed_leak")],
              "hold_clips": [cid for cid, c in clips.items() if c["adopt"]["kind"] == "hold_pending_fable_listen"],
              "production_calls_per_clip": jload("er118_output/fz_full_episode_trial_01/inventory.json")["cases"][case_key(work, level)]["production_calls_total"] / len(clips),
              "costs_by_kind": costs["by_kind"]}
        gs = jload(f"{case_dir(work, level)}/gen_summary.json")
        n6 = {"gen_wall_s": gs["wall_s"], "per_clip_mean_s": round(gs["wall_s"] / len(clips), 2), "per_clip_s": {cid: c["elapsed_s"] for cid, c in clips.items()},
              "started_at_jst": gs["started_at_jst"]}
        n2 = {"N2a_new_long_pause": [cid for cid, c in clips.items() if c["flags"].get("N2a_new_long_pause")],
              "N2b_wpm_outside": [cid for cid, c in clips.items() if c["flags"].get("N2b_wpm_outside_0.6_1.6")],
              "N2c_length_listen": [cid for cid, c in clips.items() if c["flags"].get("N2c_length_listen")]}
        cond = {"C1_ng_count": n5["ng_clips"], "C1_ok_all_adopted_or_recorded": len(n5["ng_clips"]) <= NG_MAX_RECORDED,
                "C2_all_production_pass_and_repetition_qa": all(c["adopt"]["kind"] != "ng" for c in clips.values()),
                "C3_hold_clips": n5["hold_clips"], "C4_all_comparison_valid": all(recs[cid].get("comparison_valid") for cid in clips),
                "C5_i_selfcheck": jload(f"{case_dir(work, level)}/selfcheck.json")["pass"], "C5_ii_m5": ar["compare_m5"]["m5_ok"], "C5_iii_peak_ok": ar["c5_peak_ok"],
                "C6_gate": ar["gate_c6"]["ok"], "C7_gen_snapshot_diff_empty": not (gs.get("snapshot_diff", {}).get("runs") or gs.get("snapshot_diff", {}).get("pages")),
                "C7_no_store_contamination": not (gs.get("store_attribution", {}).get("contaminated")), "C7_mtime_z_hits_empty": not gs.get("mtime_z_production_hits"),
                "C7_isolation_ok": ar["isolation"]["ok"] and not ar["original_clash_with_production"]}
        out = {"managed_id": MANAGED_ID, "work": work, "level": level, "noise_band_sha256": band_sha, "clips": clips, "N1": n1, "N2": n2,
               "N3": {"rows": n3_rows, "n_boundaries": n_total, "n_over_3db": n_over}, "N4": n4, "N5": n5, "N6": n6, "conditions": cond, "saved_at": t.now_jst()}
        safe_write_json(f"{case_dir(work, level)}/analysis.json", out)
        return {"summary": {"n": len(clips), "ng": len(n5["ng_clips"]), "hold": len(n5["hold_clips"]), "k_ctx": n5["k_ctx"], "first_try_rate": n5["first_try_rate"],
                            "N3_over_3db": f"{n_over}/{n_total}"}, "analysis": out}


def r2_base_k() -> dict:
    """R-6(c): Round 1/2 の base arm(同一session・同一コード系)の実測 TTS call/clip。"""
    import glob
    n_calls = n_clips = 0
    for p in glob.glob(os.path.join(ROOT, "er118_output", "fz_dialogue_context_tts_trial_0*", "**", "base_t1", "*", "result.json"), recursive=True):
        r_ = json.load(open(p, encoding="utf-8"))
        if r_.get("n_tts_calls") is not None:
            n_calls += r_["n_tts_calls"]
            n_clips += 1
    return {"base_t1_clips": n_clips, "base_t1_tts_calls": n_calls, "k_r2_base": round(n_calls / n_clips, 4) if n_clips else None}


def analyze_all() -> dict:
    """4単位の集計: C1〜C8・Status候補(事前登録02写像)・費用/時間・Δ/set(幅)・70円/setに対する評価。"""
    A = {f"{w}/{lv}": jload(f"{case_dir(w, lv)}/analysis.json") for w, lv in CASES}
    inv = jload(f"{OUT_ROOT}/inventory.json")
    bp = jload(f"{OUT_ROOT}/budget_plan.json")
    r2 = r2_base_k()
    n_ng = sum(len(a["N5"]["ng_clips"]) for a in A.values())
    n_hold = sum(len(a["N5"]["hold_clips"]) for a in A.values())
    n_clips = sum(a["N5"]["n_clips"] for a in A.values())
    cond_all = {k: all(a["conditions"][k] for a in A.values()) for k in ("C4_all_comparison_valid", "C5_i_selfcheck", "C5_ii_m5", "C5_iii_peak_ok", "C6_gate", "C7_gen_snapshot_diff_empty",
                                                                        "C7_no_store_contamination", "C7_mtime_z_hits_empty", "C7_isolation_ok")}
    if not all(cond_all.values()) or n_ng >= NG_MAX_RECORDED + 1:
        status = "REJECTED候補(TRIAL_FAILED_QUALITY/方式不安定)"
    elif n_hold:
        status = "PHASE1B_DONE_HOLD_PENDING_FABLE_LISTEN"
    else:
        status = "PHASE1B_DONE_USER_LISTENING_PENDING" + ("(NG記録付き)" if n_ng else "")
    # 費用(R-6): 実Trial支出(raw log) と 量産想定増分Δ/set(幅)
    llm_per_call = round(sum(jload(f"{case_dir(w, lv)}/llm/emotion_notes.json")["cost_jpy"] for w, lv in CASES) / 4, 4)
    spent = {k: round(sum(a["N5"]["costs_by_kind"].get(k, {}).get("jpy", 0.0) for a in A.values()), 4) for k in ("tts", "asr_openai", "asr_azure")}
    delta = {}
    for w in WORK_CFG:
        tot = {"k_prod_1.019": 0.0, "k_r2_base": 0.0}
        rows = {}
        for lv in LEVELS:
            a = A[f"{w}/{lv}"]
            n5 = a["N5"]
            n = n5["n_clips"]
            ck = n5["costs_by_kind"]
            c_ctx = ck.get("tts", {}).get("jpy", 0.0) / max(ck.get("tts", {}).get("calls", 1), 1)                          # 実測 TTS円/call (ctx style)
            est_ctx = bp["cases"][case_key(w, lv)]["tts_ctx_est_jpy_1call_per_clip"]
            est_base = bp["cases"][case_key(w, lv)]["tts_base_est_jpy_1call_per_clip"]
            c_base = c_ctx * (est_base / est_ctx) if est_ctx else 0.0                                                      # base call単価 = 実測ctx単価 × 見積比
            c_asr = (ck.get("asr_openai", {}).get("jpy", 0.0) + ck.get("asr_azure", {}).get("jpy", 0.0)) / max(ck.get("tts", {}).get("calls", 1), 1)   # TTS call当たりASR実費
            k_ctx = n5["k_ctx"]
            for kname, k_prod in (("k_prod_1.019", 1.019), ("k_r2_base", r2["k_r2_base"] or 1.0)):
                d = n * (k_ctx * c_ctx - k_prod * c_base + (k_ctx - k_prod) * c_asr)
                tot[kname] += d
            rows[lv] = {"n": n, "k_ctx": k_ctx, "c_ctx_per_call": round(c_ctx, 4), "c_base_per_call_est": round(c_base, 4), "c_asr_per_call": round(c_asr, 4)}
        delta[w] = {"levels": rows, **{k: round(v + 2 * llm_per_call, 3) for k, v in tot.items()}, "llm_2calls_jpy": round(2 * llm_per_call, 4),
                    "share_of_70yen": {k: round((v + 2 * llm_per_call) / 70.0, 4) for k, v in tot.items()}}
    spent_total = round(sum(spent.values()), 3)
    wall = sum(a["N6"]["gen_wall_s"] for a in A.values())
    out = {"managed_id": MANAGED_ID, "status_candidate": status, "n_clips": n_clips, "n_ng": n_ng, "n_hold": n_hold, "conditions_all_units": cond_all,
           "c1_recorded": bool(n_ng <= NG_MAX_RECORDED), "spent_phase1b_jpy_by_kind": spent, "spent_phase1b_total_jpy": spent_total,
           "llm_cost_per_call_jpy_phase1a": llm_per_call, "r2_base_k": r2, "k_ctx_by_unit": {k: a["N5"]["k_ctx"] for k, a in A.items()},
           "k_ctx_overall": round(sum(a["N5"]["tts_calls_total_raw_log"] for a in A.values()) / n_clips, 4),
           "first_try_rate_overall": round(sum(a["N5"]["first_try_ok"] for a in A.values()) / n_clips, 4),
           "production_k": 1.019, "delta_per_set": delta, "gen_wall_s_total": round(wall, 1),
           "n3_over_3db_total": {k: f"{a['N3']['n_over_3db']}/{a['N3']['n_boundaries']}" for k, a in A.items()},
           "n2_flags": {k: a["N2"] for k, a in A.items()}, "n1_unstable_speakers": {k: [s for s, r_ in a["N1"].items() if r_["unstable_speaker_flag"]] for k, a in A.items()},
           "saved_at": t.now_jst()}
    safe_write_json(f"{OUT_ROOT}/analysis_all.json", out)
    return {"summary": {"status": status, "n_ng": n_ng, "n_hold": n_hold, "spent_total": spent_total, "k_ctx": out["k_ctx_overall"],
                        "delta_per_set": {w: delta[w]["k_prod_1.019"] for w in delta}}, "all": out}



# ---------- 4-13 試聴ページ(PAGE_ROOT配下のみ。noindex。Production公開物は一切変更しない) ----------
PAGE_BASE_URL = "https://shimomura055.github.io/eigo-radio/user_test/fz_full_episode_trial_01"
_KIND_LABEL = {"adopted": "", "adopted_after_fable_clearance": "(Fable聴取確認済み)",
               "ng": "この箇所は現行音声（Trial生成NG）", "ng_confirmed_leak": "この箇所は現行音声（Trial生成NG: 文脈語の混入を確認）",
               "hold_pending_fable_listen": "この箇所は現行音声（Trial生成は保留中: 文脈語の混入疑いをFableが確認待ち）"}
_PAGE_JS = ("<script>function seek(id,s){var a=document.getElementById(id);if(!a)return;a.currentTime=s;a.play();}</script>")
_PAGE_CSS2 = (t._PAGE_CSS + ".nowprod{background:#fff0f0;border:1px solid #d99;border-radius:6px;padding:6px 10px;font-size:.9rem}"
              ".ctxbox{background:#f7f7f7;border-radius:6px;padding:4px 8px;font-size:.85rem;margin:4px 0}.btn{font-size:.8rem;margin:2px 4px 2px 0;padding:2px 8px}"
              "table.s{border-collapse:collapse;font-size:.88rem}table.s td,table.s th{border:1px solid #bbb;padding:3px 8px}")


def _fmt_t(s: float) -> str:
    return f"{int(s // 60)}:{int(s % 60):02d}"


def _metrics_line(c: dict) -> str:
    p, tr = c["prod"], c["trial"]
    if not tr:
        return "<div class='lab'>機械指標: Trial音声なし</div>"
    return (f"<div class='lab'>機械指標(参考・開発側): 長さ 現行{p['duration_s']:.2f}s → Trial{tr['duration_s']:.2f}s / 調音話速 {p['articulation_wpm_300']:.0f} → {tr['articulation_wpm_300']:.0f} wpm / "
            f"F0中央値 {p['f0']['median_hz']:.0f} → {tr['f0']['median_hz']:.0f} Hz / F0幅 {p['f0']['range_semitones_p10_p90']:.1f} → {tr['f0']['range_semitones_p10_p90']:.1f} 半音</div>")


def _context_html(ctx: dict) -> str:
    prev = " / ".join(f"{d['speaker_display']}: {t._unq(d['text'])}" for d in ctx["prev_dialogue"]) or "なし"
    nxt = " / ".join(f"{d['speaker_display']}: {t._unq(d['text'])}" for d in ctx["next_dialogue"]) or "なし"
    return (f"<details><summary>前後の文脈（Trial生成時にStyleへ渡した決定論の抜き出し）</summary><div class='ctxbox'>前のセリフ: {H.escape(prev)}<br>後のセリフ: {H.escape(nxt)}<br>"
            f"直前の地の文: {H.escape(ctx['narration_before'] or 'なし')}<br>直後の地の文: {H.escape(ctx['narration_after'] or 'なし')}</div></details>")


def _level_section(work: str, level: str, A: dict, AR: dict, review: dict, plan: dict, ctxs: dict) -> str:
    lab = LEVELS[level]["label"]
    n_ng = AR["n_ng"] + AR["n_hold"]
    sec = [f"<section id='{level}'><h2>{lab}</h2>",
           f"<div class='note'>採用したTrialセリフ {AR['n_adopted']}/{len(AR['decisions'])} 件" + (f"、現行音声のまま {n_ng} 件（下の各カードに明記）" if n_ng else "（全件Trial音声）") +
           f"。通しの長さ: Trial {_fmt_t(AR['trial_duration_s'])}（{AR['trial_duration_s']:.1f}秒）/ 現行 {_fmt_t(AR['prod_duration_s'])}（{AR['prod_duration_s']:.1f}秒）。"
           "地の文・導入・Key Phrase・まとめ・無音・音量規則は現行と同じで、<b>差はセリフの音声だけ</b>です（Trial版はセリフの長さが変わるため、通し全体の秒数と各セリフの開始時刻が少しずれます）。</div>",
           "<div class='row'>"
           f"<div class='col'><div class='lab'>Trial版 通し（セリフ=文脈・感情付きで新規生成）</div><audio id='tf_{level}' controls preload='none' src='{level}/trial_full.mp3'></audio></div>"
           f"<div class='col'><div class='lab'>現行版 通し（同じ経路でmp3化した再組立。本番公開物ではなくコピー）</div><audio id='pf_{level}' controls preload='none' src='{level}/production_full.mp3'></audio></div></div>"]
    for ch in AR["chapters"]:
        cid = ch["clip_id"]
        c = A["clips"][cid]
        d = AR["decisions"][cid]
        rv = review[cid]
        ctx = ctxs[cid]
        spk = ctx["speaker_display"]
        trial_part = (f"<audio controls preload='none' src='{level}/clips/{cid}_trial.mp3'></audio>" if d["adopted"]
                      else f"<div class='nowprod'><b>{H.escape(_KIND_LABEL.get(d['kind'], ''))}</b>。通し版のこの箇所には現行音声を置いています。</div>")
        held = ""
        if d["kind"] == "hold_pending_fable_listen":
            held = (f"<details><summary>保留中のTrial生成音声（未確認・参考。採用していません）</summary><audio controls preload='none' src='{level}/held/{cid}_generated_unverified.mp3'></audio></details>")
        sec.append(
            f"<div class='card'><h2>#{ch['n']} {H.escape(spk)}（{H.escape(c['voice'])}） {('<span class=na>' + H.escape(_KIND_LABEL[d['kind']]) + '</span>') if d['kind'] != 'adopted' else ''}</h2>"
            f"<div class='en'>{H.escape(c['text'])}</div>"
            f"<div class='scene'>場面・演出（日本語要約）: {H.escape(rv['summary_ja'])}</div>{_context_html(ctx)}"
            "<div class='row'>"
            f"<div class='col'><div class='lab'>現行（Production）</div><audio controls preload='none' src='{level}/clips/{cid}_prod.mp3'></audio></div>"
            f"<div class='col'><div class='lab'>Trial（文脈・感情付き）</div>{trial_part}{held}</div></div>"
            f"<div>通しの該当箇所へ: <button class='btn' onclick=\"seek('pf_{level}',{ch['prod_start']})\">現行 {_fmt_t(ch['prod_start'])}</button>"
            f"<button class='btn' onclick=\"seek('tf_{level}',{ch['trial_start']})\">Trial {_fmt_t(ch['trial_start'])}</button></div>"
            f"{_metrics_line(c)}</div>")
    sec.append("</section>")
    return "\n".join(sec)


def _doc(title: str, body: str) -> str:
    return (f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><meta name='robots' content='noindex,nofollow'>"
            f"<meta name='viewport' content='width=device-width, initial-scale=1'><title>{H.escape(title)}</title><style>{_PAGE_CSS2}</style></head><body>{body}{_PAGE_JS}</body></html>")


def build_pages_all() -> dict:
    """試聴ページ: index.html + 作品別(monkeys_paw.html / melos.html) + dev_details.html。PAGE_ROOT配下のみ書く(safe_write_text)。"""
    AR = {f"{w}/{lv}": jload(f"{case_dir(w, lv)}/assemble_result.json") for w, lv in CASES}
    AN = {f"{w}/{lv}": jload(f"{case_dir(w, lv)}/analysis.json") for w, lv in CASES}
    ALL = jload(f"{OUT_ROOT}/analysis_all.json")
    written = []
    for w in WORK_CFG:
        secs = []
        for lv in LEVELS:
            key = f"{w}/{lv}"
            with use_case(w, lv):
                plan = t.load_plan()
                ctxs = {x["id"]: t.extract_context(plan, x["id"]) for x in dialogue_clips(plan)}
            review = jload(f"{case_dir(w, lv)}/llm/emotion_review.json")["items"]
            secs.append(_level_section(w, lv, AN[key], AR[key], review, plan, ctxs))
        body = (f"<h1>『{H.escape(WORK_CFG[w]['title_ja'])}』全編通し（Trial）</h1><p><a href='index.html'>← 一覧へ</a> / <a href='#a2'>Standard</a> / <a href='#b1b'>Advanced</a></p>"
                "<div class='note'><b>状態: Trial（Production採用ではありません・既存の公開音声は差し替えていません）</b>。セリフ音声を、前後の会話・地の文の演出・話者の気持ちをStyle（話し方の指示）に添えた方式で"
                "<b>全件新規に生成</b>し、地の文などの既存音声と同じ手順で通しに組み立てました。「現行版」は比較用のコピーです。音量はすべて本番と同じ規則で揃えています。</div>"
                + "\n".join(secs))
        written.append(safe_write_text(f"{PAGE_ROOT}/{w}.html", _doc(f"{WORK_CFG[w]['title_ja']} 全編通しTrial", body)))
    rows = []
    for w in WORK_CFG:
        for lv in LEVELS:
            key = f"{w}/{lv}"
            ar, an = AR[key], AN[key]
            rows.append(f"<tr><td>{H.escape(WORK_CFG[w]['title_ja'])}</td><td>{LEVELS[lv]['label']}</td><td>{ar['n_adopted']}/{len(ar['decisions'])}</td><td>{ar['n_ng'] + ar['n_hold']}</td>"
                        f"<td>{_fmt_t(ar['trial_duration_s'])} / {_fmt_t(ar['prod_duration_s'])}</td><td><a href='{w}.html#{lv}'>聴く</a></td></tr>")
    body = ("<h1>セリフ音声 全編通しTrial（文脈・感情付き）</h1>"
            "<div class='note'><b>状態: Trial（Production採用ではありません）</b>。『猿の手』『走れメロス』の Standard / Advanced で、セリフ音声を<b>全件</b>「前後の会話・地の文の演出・話者の気持ち」を足した方式で新規生成し、"
            "既存の地の文などと組み合わせて<b>最初から最後まで通して聴ける</b>ようにしました。既存の公開音声は一切差し替えていません。機械指標は開発側の参考で、最終判断はあなたの試聴です。</div>"
            f"<div class='note'>{t.PAGE_VOLUME_NOTE}</div>"
            "<table class='s'><tr><th>作品</th><th>レベル</th><th>Trial採用セリフ</th><th>現行音声のままの箇所</th><th>通しの長さ（Trial / 現行）</th><th></th></tr>" + "".join(rows) + "</table>"
            "<h2>聴いていただきたい観点</h2><ol>"
            "<li><b>表現</b>: ①セリフの感情が場面に合っているか ②感情表現が過剰でないか ③前後のセリフと演技がつながっているか ④地の文からセリフへの切り替わりが自然か ⑤通しで聴いたとき現行版より没入感が増すか</li>"
            "<li><b>安定性</b>: ⑥同じ人物の演技に大きなばらつきがないか ⑦感情の強いセリフと弱いセリフで効果がどう違うか ⑧不自然な速度変化・長すぎる間がないか</li></ol>"
            "<p class='lab'>前回のTrial（比較用）: "
            "<a href='../fz_dialogue_context_trial_01/index.html'>1回目（賢者の贈り物・8セリフ）</a> / <a href='../fz_dialogue_context_trial_02/index.html'>2回目（猿の手・開けた窓）</a></p>"
            "<p class='lab'>開発者向けの詳細: <a href='dev_details.html'>dev_details.html</a></p>")
    written.append(safe_write_text(f"{PAGE_ROOT}/index.html", _doc("セリフ音声 全編通しTrial", body)))
    dev = ("<h1>開発者向け詳細（Trial）</h1><p>状態候補: " + H.escape(ALL["status_candidate"]) + "</p><pre style='white-space:pre-wrap;font-size:.78rem'>" +
           H.escape(json.dumps({"analysis_all": ALL, "units": {k: {"conditions": v["conditions"], "N2": v["N2"], "N3": {"n_boundaries": v["N3"]["n_boundaries"], "n_over_3db": v["N3"]["n_over_3db"]},
                                                                      "N5": {kk: v["N5"][kk] for kk in ("k_ctx", "first_try_rate", "regen_clips", "ng_clips", "hold_clips")}} for k, v in AN.items()}},
                                ensure_ascii=False, indent=1)) + "</pre>")
    written.append(safe_write_text(f"{PAGE_ROOT}/dev_details.html", _doc("dev details", dev)))
    return {"pages": written, "index_url": f"{PAGE_BASE_URL}/index.html"}



# ---------- 4-9 R-2: 外側ループの書込先 dry-run(API 0。PYTHONPATH=netblock_harness_01 NETBLOCK_LOG=... 下でのみ実行) ----------
def dryrun_sinks(work: str = "monkeys_paw", level: str = "b1b") -> dict:
    """gen_fn と ASR を差し替え、Adv外側ループ(sink差替え + Z scope + secondary run scope の内側)を3回NGで走らせ、
    append_attempt_history_event / _log_human_review / finalize→record_outcome(review lock state) の書込先を実測する。
    Productionの保護store・run dir・公開pageが不変であること、本Trial由来の書込みが全てOUT_ROOT配下であることを確認する。"""
    if not os.environ.get("NETBLOCK_LOG"):
        raise SystemExit("[STOP] dryrun-sinks は PYTHONPATH=netblock_harness_01 NETBLOCK_LOG=<log> 下で実行する(接続試行0の保証)")
    import numpy as np
    import soundfile as sf
    import er003_v1_n3_01_tts_generate as n3
    import er006_secondary_asr_01 as secondary_asr
    import er063_family_z_audio_01 as a63
    import er078_secondary_run_scope_01 as sec_scope
    import er109_xz_scope_01 as scope
    import er113_fx_paragraph_chunk_trial_01 as t113
    t_start = time.time()
    before = prod_snapshot()
    out_files_before = set(_list_files(OUT_ROOT))
    info: dict = {}
    with use_case(work, level):
        plan = t.load_plan()
        cid = dialogue_clips(plan)[0]["id"]
        sp = dialogue_specs(work, level)[cid]
        dry_dir = f"{case_dir(work, level)}/dryrun/{cid}"
        wav = f"{dry_dir}/{level}/narration/{cid}.wav"
        assert_out_root(wav)
        os.makedirs(os.path.dirname(_abs(wav)), exist_ok=True)
        text = sp.text
        calls = {"gen": 0, "asr": 0}

        def stub_gen(max_attempts):
            calls["gen"] += 1
            sr = 24000
            tt = np.arange(int(sr * 1.2)) / sr
            sf.write(_abs(wav), (0.2 * np.sin(2 * np.pi * 220 * tt)).astype("float32"), sr)
            return {"status": "OK", "text": text, "path": wav, "voice": sp.voice, "asr_verified": True, "asr_text": text,
                    "attempts_log": [{"attempt": 1, "status": "OK", "verified": True}], "instruction_type": "english_style_prefix_wide_margin",
                    "trim_info": None, "duration_seconds": 1.2, "repetition_qa_checked": True}

        def stub_transcribe(path, language="en-US"):
            calls["asr"] += 1
            return "zzz qqq completely different words", None

        old_tr, old_flag = n3.routing.transcribe, secondary_asr.FEATURE_FLAG_SECONDARY_ASR_ENABLED
        n3.routing.transcribe = stub_transcribe
        secondary_asr.FEATURE_FLAG_SECONDARY_ASR_ENABLED = False      # Secondary(Azure)を呼ばない = API 0
        sinks_dir = f"{case_dir(work, level)}/sinks_dryrun"
        err = None
        try:
            with t113.redirect_production_sinks(sinks_dir):
                def _run(_d=None):
                    return n3.generate_with_a2_slowdown_outer_loop(cid, text, wav, stub_gen, slowdown_pct=a63.Z_ADV_DIALOGUE_SLOWDOWN_PCT)
                res = sec_scope.with_secondary_run(scope.family_scope("Z")(_run))(None)
                # HR queue経路が外側ループ内で実行されなかった場合に備え、同じ関数を同じredirect下で直接1回プローブ(書込先の実測)
                hr_probe = None
                if not (os.path.exists(_abs(f"{sinks_dir}/sink_er006_secondary_asr_01_HUMAN_REVIEW_LOG_PATH.jsonl"))):
                    try:
                        secondary_asr._log_human_review({"canonical_text": text, "wav_path": wav, "steps": [], "cost_guard_triggered": False, "final_status": "DRYRUN_PROBE",
                                                         "classification": None})
                        hr_probe = "probe_executed"
                    except BaseException as e:      # noqa: BLE001
                        hr_probe = f"probe_error:{type(e).__name__}:{str(e)[:200]}"
                    info["hr_probe"] = hr_probe
        except BaseException as e:      # noqa: BLE001
            err = f"{type(e).__name__}: {str(e)[:500]}"
            res = {}
        finally:
            n3.routing.transcribe = old_tr
            secondary_asr.FEATURE_FLAG_SECONDARY_ASR_ENABLED = old_flag
        info.update({"clip_id": cid, "stub_gen_calls": calls["gen"], "stub_asr_calls": calls["asr"], "error": err,
                     "final_status": res.get("status"), "tts_generations_used": res.get("tts_generations_used"),
                     "review_lock_state_final": res.get("review_lock_state_final"), "human_review_required": res.get("human_review_required"),
                     "slowdown_attempts": len(res.get("slowdown_attempts_log") or [])})
    after = prod_snapshot()
    diff = snapshot_diff(before, after)
    contam = store_contamination(diff["stores"], t_start)
    scan = scan_repo_mtime(t_start)
    new_files = sorted(set(_list_files(OUT_ROOT)) - out_files_before)
    sink_files = {f: os.path.getsize(_abs(f)) for f in new_files if "/sinks_dryrun/" in f}
    lock_files = [f for f in new_files if f.endswith("review_lock_state.json")]
    outside_new = [f for f in new_files if not under(f, OUT_ROOT)]
    ah = [f for f in sink_files if f.endswith("ATTEMPT_HISTORY_PATH.jsonl")]
    hr = [f for f in sink_files if f.endswith("HUMAN_REVIEW_LOG_PATH.jsonl")]
    nb_log = os.environ["NETBLOCK_LOG"]
    nb_lines = open(nb_log, encoding="utf-8").read().splitlines() if os.path.exists(nb_log) else []
    rep = {"work": work, "level": level, **info, "snapshot_diff": diff, "store_attribution": contam,
           "z_production_mtime_hits": scan["z_production_hits"], "mtime_n_other_hits": scan["n_other_hits_not_z"],
           "new_files_under_out_root": len(new_files), "sink_files": sink_files, "review_lock_state_files": lock_files,
           "attempt_history_sink_landed": bool(ah), "human_review_sink_landed": bool(hr), "lock_state_landed": bool(lock_files),
           "netblock_log": nb_log, "netblock_blocked_lines": nb_lines, "saved_at": t.now_jst()}
    rep["pass"] = bool(not info.get("error") and info.get("stub_gen_calls", 0) >= 1 and rep["attempt_history_sink_landed"] and rep["lock_state_landed"]
                       and not diff["runs"] and not diff["pages"] and not contam["contaminated"] and not scan["z_production_hits"] and not outside_new
                       and not nb_lines)
    safe_write_json(f"{OUT_ROOT}/dryrun_sinks.json", rep)
    return rep


def _list_files(rel_dir: str) -> list:
    out = []
    for dp, _dn, fns in os.walk(_abs(rel_dir)):
        for fn in fns:
            out.append(os.path.relpath(os.path.join(dp, fn), ROOT).replace("\\", "/"))
    return out


# ---------- 4-10 R-7(a): Round 1/2 の自然ゆれ固定値(生成前に作成・以後更新しない) ----------
NOISE_SOURCES = ("er118_output/fz_dialogue_context_tts_trial_01/analysis.json", "er118_output/fz_dialogue_context_tts_trial_02/monkeys_paw/analysis.json",
                 "er118_output/fz_dialogue_context_tts_trial_02/open_window/analysis.json")
NOISE_METRICS = {"articulation_wpm_300": lambda a: a.get("articulation_wpm_300"), "f0_median_hz": lambda a: (a.get("f0") or {}).get("median_hz"),
                 "f0_range_semitones": lambda a: (a.get("f0") or {}).get("range_semitones_p10_p90"), "rms_lin": lambda a: a.get("rms_lin"),
                 "duration_s": lambda a: a.get("duration_s"), "max_mid_pause_s": lambda a: a.get("max_mid_pause_s")}


def noise_band_r2() -> dict:
    """Production原音(existing_A)と同styleの別take(base_t1)の |ln比| を Round 1/2 の全clipで集計(中央値・90%点)。ctx効果の判断前の『自然ゆれの目安』。"""
    import numpy as np
    vals = {k: [] for k in NOISE_METRICS}
    n_pairs = 0
    for src in NOISE_SOURCES:
        d = jload(src)
        for cid, c in d["clips"].items():
            a, b = c.get("existing_A"), c.get("base_t1")
            if not a or not b:
                continue
            n_pairs += 1
            for k, f in NOISE_METRICS.items():
                x, y = f(a), f(b)
                if x and y and x > 0 and y > 0:
                    vals[k].append(abs(math.log(y / x)))
    out = {"managed_id": MANAGED_ID, "definition": "|ln(base_t1 / existing_A)|(同style別take対Production原音)。Round 1(8 clip)+Round 2(猿の手8+open_window)", "sources": list(NOISE_SOURCES),
           "source_sha256": {s: file_sha(s) for s in NOISE_SOURCES}, "n_pairs": n_pairs, "metrics": {}}
    for k, v in vals.items():
        out["metrics"][k] = {"n": len(v), "median": round(float(np.median(v)), 4) if v else None, "p90": round(float(np.percentile(v, 90)), 4) if v else None}
    out["fixed_at"] = t.now_jst()
    safe_write_json(f"{OUT_ROOT}/noise_band_r2.json", out)
    return out


def cmd_preflight(work: str, level: str) -> dict:
    sc = selfcheck_case(work, level)
    ti = text_identity_case(work, level)
    return {"selfcheck_pass": sc["pass"], "text_identity_all_same_function": ti["all_same_function_equal"], "n_pnap_effect": ti["n_pnap_effect"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=MANAGED_ID)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("inventory", help="棚卸(API 0)")
    sub.add_parser("budget", help="費用見積(API 0)")
    p = sub.add_parser("llm", help="Phase 1a(有料・cap<=5円・scope=Phase 1a): 感情情報LLM 1 call")
    p.add_argument("--work", choices=tuple(WORK_CFG), required=True)
    p.add_argument("--level", choices=tuple(LEVELS), required=True)
    sub.add_parser("candidates", help="EMOTION_CANDIDATES_01.md(API 0)")
    for c in ("preflight", "gen", "assemble", "analyze"):
        p = sub.add_parser(c, help={"preflight": "生成前の自己検証+TEXT同一性(API 0)", "gen": "セリフ新規生成(有料・scope=Phase 1b・cap<=100円)",
                                    "assemble": "DEV隔離の通し組立+M-5 assert+C6 Gate+mp3(API 0)", "analyze": "解析(API 0)"}[c])
        p.add_argument("--work", choices=tuple(WORK_CFG), required=True)
        p.add_argument("--level", choices=tuple(LEVELS), required=True)
    p = sub.add_parser("dryrun-sinks", help="R-2 書込先dry-run(API 0、netblock harness必須)")
    p.add_argument("--work", choices=tuple(WORK_CFG), default="monkeys_paw")
    p.add_argument("--level", choices=tuple(LEVELS), default="b1b")
    sub.add_parser("noise-band", help="R-7(a) noise_band_r2.json(API 0)")
    sub.add_parser("page-all", help="試聴ページ(API 0)")
    sub.add_parser("analyze-all", help="全unit解析+集計(API 0)")
    a = ap.parse_args(argv)
    if a.cmd == "inventory":
        inv = cmd_inventory()
        print(json.dumps({k: v["n_dialogue"] for k, v in inv["cases"].items()}, ensure_ascii=False))
    elif a.cmd == "budget":
        print(json.dumps(cmd_budget()["totals"], ensure_ascii=False))
    elif a.cmd == "llm":
        r = run_llm_case(a.work, a.level)
        print(json.dumps({k: r[k] for k in ("cost_jpy", "n_clips", "n_accepted", "n_discarded", "n_no_explicit_cue")}, ensure_ascii=False))
    elif a.cmd == "candidates":
        print(render_candidates())
    elif a.cmd == "preflight":
        print(json.dumps(cmd_preflight(a.work, a.level), ensure_ascii=False))
    elif a.cmd == "dryrun-sinks":
        r = dryrun_sinks(a.work, a.level)
        print(json.dumps({k: r.get(k) for k in ("pass", "error", "stub_gen_calls", "attempt_history_sink_landed", "human_review_sink_landed", "lock_state_landed", "netblock_blocked_lines")}, ensure_ascii=False))
    elif a.cmd == "noise-band":
        print(json.dumps(noise_band_r2()["metrics"], ensure_ascii=False))
    elif a.cmd == "gen":
        r = gen_case(a.work, a.level)
        s = r["summary"]
        print(json.dumps({k: s.get(k) for k in ("n_clips", "n_ok", "n_adopted", "n_hold", "spent_unit_jpy", "spent_phase1b_total_jpy", "wall_s")}, ensure_ascii=False))
    elif a.cmd == "assemble":
        print(json.dumps(assemble_case(a.work, a.level)["summary"], ensure_ascii=False))
    elif a.cmd == "analyze":
        print(json.dumps(analyze_case(a.work, a.level)["summary"], ensure_ascii=False))
    elif a.cmd == "analyze-all":
        print(json.dumps(analyze_all()["summary"], ensure_ascii=False))
    elif a.cmd == "page-all":
        print(json.dumps(build_pages_all(), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

