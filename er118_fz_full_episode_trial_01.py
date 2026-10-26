# -*- coding: utf-8 -*-
"""FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 (DEV専用Trial、Production経路ではない)

ユーザー指示(2026-10-26、原文=docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01_USER.md):
『猿の手』『走れメロス』の Standard/Advanced で、セリフ音声を全件、文脈・感情付き方式で新規生成し、地の文等の既存音声と組み合わせた通し版を作る。

委任_01(Phase 0)の範囲: inventory / budget / llm(Phase 1a、PHASE1_GO.json必須) / candidates のみ。
gen / assemble / page は未実装(Opus条件Aレビュー後の委任_02で実装)。呼ぶと拒否する。

方式は Round 1/2 (er118_fz_dialogue_context_tts_trial_01.py) を import 再利用のみ。
CONTEXT区画書式・EMOTION_DEVELOPER rule 1〜10・leakage検査・ASR検査・決定論抽出は無変更(本ファイルは module globals を作品×レベルへ切り替えるだけ)。
Production file / Master Store / manifest / reuse telemetry へは一切書かない(出力は er118_output/fz_full_episode_trial_01/ のみ)。
"""
import argparse
import contextlib
import datetime
import functools
import json
import os
import subprocess
import sys

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


@contextlib.contextmanager
def use_case(work: str, level: str):
    """Round 1/2 module の globals を作品×レベルへ一時的に切り替え、終了時に必ず元へ戻す(Round 1/2の既定=賢者の贈り物を壊さない。Opus論点⑤)。"""
    saved = {k: getattr(t, k) for k in _T_GLOBALS}
    try:
        yield configure_case(work, level)
    finally:
        for k, v in saved.items():
            setattr(t, k, v)


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
def _require_go() -> dict:
    ap = os.path.join(ROOT, GO_FILE)
    if not os.path.exists(ap):
        raise SystemExit(f"[STOP] {GO_FILE} が無い。有料runは PHASE1_GO.json 無しで起動しない。")
    go = t.load_json(GO_FILE)
    if go.get("managed_id") != MANAGED_ID or go.get("scope") != SCOPE_PHASE1A or not go.get("cap_jpy") or float(go["cap_jpy"]) > PHASE1A_CAP_JPY:
        raise SystemExit(f"[STOP] PHASE1_GO.json の managed_id / scope({SCOPE_PHASE1A}) / cap_jpy(<= {PHASE1A_CAP_JPY}) 不正")
    return go


def _stop_check() -> None:
    r = subprocess.run([sys.executable, "tools/stop_scope_check_01.py", "--managed-id", MANAGED_ID, "--run-dir", OUT_ROOT,
                        "--out", f"{OUT_ROOT}/stop_check_llm.json"], cwd=ROOT)
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


def refuse(cmd: str):
    raise SystemExit(f"[STOP] `{cmd}` は委任_01では未実装(Opus条件Aレビュー反映後の委任_02で実装)。TTS生成・組立・公開ページは本委任で禁止。")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=MANAGED_ID)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("inventory", help="棚卸(API 0)")
    sub.add_parser("budget", help="費用見積(API 0)")
    p = sub.add_parser("llm", help="Phase 1a(有料・cap<=5円・PHASE1_GO.json必須): 感情情報LLM 1 call")
    p.add_argument("--work", choices=tuple(WORK_CFG), required=True)
    p.add_argument("--level", choices=tuple(LEVELS), required=True)
    sub.add_parser("candidates", help="EMOTION_CANDIDATES_01.md(API 0)")
    for c in ("gen", "assemble", "page"):
        sub.add_parser(c, help="未実装(委任_02)")
    a = ap.parse_args(argv)
    if a.cmd in ("gen", "assemble", "page"):
        refuse(a.cmd)
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
