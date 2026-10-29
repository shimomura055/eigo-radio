# -*- coding: utf-8 -*-
"""JA-ASR-V2-BETA-PRODUCTION-WIRING-01 委任_02A: runtime evidence 有料phase(E1/E2/E3)。runtime_evidence_01.py から呼ばれる。

E1: 月タイトル6本の実wavを、実Production経路(strict、1 attempt)・X scope・実ASR(OpenAI gpt-4o-mini-transcribe + 必要時Azure)で判定する(TTSは偽=保存wavコピー)。
E2: X/Y/Zそれぞれ>=1 Section。Xは family関数 `generate_family_x_a2_segments`(japanese_titleのみ選択)で完了hookまで実走。Y/Zは全family共通の
    Section生成入口 `n3_tts.generate_a2_japanese_with_reading_safety` を各 scope 内で実走し、family完了hookと同じ関数(write_listening_list_safe)+試聴ページ節の
    同じrender関数を実行する(Y/Z family関数は全記事fixtureが必要なため未実走=制約として報告)。
E3: 負例・scope外: 原稿の数値だけ変えた(誤り)原稿を同じwavに照合 -> NG/HR・rescue_basis=None。scope外(None)で同じ入力 -> 新キー無し(従来判定)。
費用: 各Azure呼出は監査record(cost.est_jpy)とrun単位RunStateの集計を突合する(M-2)。上限¥20(実績は<=¥6想定)。超過見込みなら停止。
"""
from __future__ import annotations

import contextlib
import json
import os
import sys
import types

OPENAI_JPY_PER_SEC = 0.045 / 6.0      # gpt-4o-mini-transcribe の概算(委任文: 約¥0.045 / 6秒)


def _openai_est(summaries):
    tot = 0.0
    for s in summaries:
        w = s.get("wav")
        if w and os.path.exists(w):
            tot += R_dur(w) * OPENAI_JPY_PER_SEC * (s.get("attempts") or 1)
    return tot


R_dur = None


def run(phase, work, out_dir, R):
    global R_dur
    R_dur = R._dur
    if phase == "e2dry":      # 内部確認用(API 0): Xのfamily関数を保存済み転写で通す
        R.install_host_guard(block_all=True)
        w = {n: (w, p, a) for n, w, p, a, _ in R.MOON6}["ms_03 a2"]
        r = _x_family_run(work, R, w[0], lambda rows: None, stored=(w[1], w[2]))
        ry = _y_family_run(work, R, w[0], lambda rows: None, stored=(w[1], w[2]))
        rz = _z_family_run(work, R, w[0], lambda rows: None, stored=(w[1], w[2]))
        return {"phase": "e2dry", "paid": False, "X": r, "Y": ry, "Z": rz}
    R.install_host_guard(block_all=False)
    R.stop_check(f"{phase}_paid", out_dir)
    import er005_cost_logger as cl      # 実API呼出のraw usageをこの証跡dirだけに記録(Production raw_usage_logには書かない)
    cl.install(os.path.join(out_dir, f"raw_usage_log_runtime_evidence_{phase}_01.jsonl"))
    ev = {"phase": phase, "paid": True, "models": {"openai_asr": "gpt-4o-mini-transcribe", "azure_asr": "azure-speech-stt"}, "rows": []}
    spent = 0.0

    def account(rows):
        nonlocal spent
        spent += sum(float(r.get("audit_cost_est_jpy_sum") or 0.0) for r in rows) + _openai_est(rows)
        ev["est_jpy_running"] = round(spent, 4)
        if spent > 15.0:
            raise SystemExit(f"cost guard: running estimate {spent:.2f} JPY > 15 (cap 20): stop")

    if phase in ("e1", "e1b", "e1c"):
        for name, wav, prim, azt, exp in R.MOON6:
            s, _ = R.verified_strict(R.MOON, wav, "X", work, "e1_" + name.replace(" ", "_"))
            s["moon_label"], s["r1off_expected_by_delegation"] = name, exp   # 期待は保存済み転写[E0]基準。実ASRは非決定的なので差が出うる
            s["stored_primary_text"], s["stored_secondary_text"] = prim, azt
            ev["rows"].append(s)
            account([s])
    elif phase == "e2":
        ev.update(run_e2(work, out_dir, R, account))
    elif phase == "e3":
        ev.update(run_e3(work, out_dir, R, account))
    else:
        raise SystemExit(f"unknown phase {phase}")
    ev["est_jpy_total_audit_plus_openai_est"] = round(spent, 4)
    ev["net_hosts"] = dict(R._STATE["net_hosts"])
    ev["openai_calls"], ev["azure_calls"] = R._STATE["openai_calls"], R._STATE["azure_calls"]
    return ev


# ---------------------------------------------------------------- E2
def _x_family_run(work, R, wav, account, stored=None):
    """X family関数(生成+完了hook)を、japanese_titleのみ選択・偽TTS・実ASRで実走。"""
    import er019_family_x_audio_production_runner_01 as xr
    import er006_secondary_asr_01 as sec6
    theme = os.path.join(work, "x_theme")
    a2 = os.path.join(theme, "a2")
    os.makedirs(a2, exist_ok=True)
    json.dump({"title": "Sample Title", "title_tts": "Sample Title", "part1": "Part one text.", "part2": "Body two text.", "part3": "Body three text.",
               "in_one_line": "In one line text."}, open(os.path.join(a2, "parts.json"), "w", encoding="utf-8"))
    json.dump({"preview": "プレビュー。", "comment_1": "コメント1。", "comment_2": "コメント2。", "comment_3": "コメント3。", "comment_4": "コメント4。"},
              open(os.path.join(a2, "a2_support_texts.json"), "w", encoding="utf-8"))
    snaps = []
    real_end = sec6.end_secondary_run

    def end_snap():
        rs = sec6._RUN_STATE
        if rs is not None:
            snaps.append({"secondary_calls": rs.secondary_calls, "est_jpy_total": round(rs.est_jpy_total, 4),
                          "consecutive_failures": rs.secondary_consecutive_failures, "circuit_open": rs.circuit_open})
        real_end()
    sec6.end_secondary_run = end_snap
    import io
    buf = io.StringIO()
    prev_only = xr._ONLY_SEGMENTS
    xr._ONLY_SEGMENTS = {"japanese_title"}
    try:
        with R.fake_tts_patch(wav), R.instrumented_asr(stored), contextlib.redirect_stdout(buf):
            out = xr.generate_family_x_a2_segments(theme, R.MOON, tts_backend="structured_separation", style_profile="default")
    finally:
        xr._ONLY_SEGMENTS = prev_only
        sec6.end_secondary_run = real_end
    res_path = os.path.join(a2, "audit", "tts_generation_results.json")
    doc = json.load(open(res_path, encoding="utf-8"))
    seg = doc["segments"]["japanese_title"]
    lst_path = os.path.join(a2, "audit", "pass_with_warning_listening_list.json")
    lst = json.load(open(lst_path, encoding="utf-8")) if os.path.exists(lst_path) else None
    import er078_pass_with_warning_registry_01 as pww
    html = pww.render_html_section(pww.load_listening_list(a2), href_fn=lambda e: e.get("audio_path") or "")
    s = R.summarize("x_family_generate_family_x_a2_segments", "X", wav, R.MOON, seg, None)
    s["run_state_snapshots"] = snaps
    s["segment_statuses"] = {k: v.get("status") for k, v in doc["segments"].items()}
    account([s])
    return {"summary": s, "completion_block_stdout": buf.getvalue(), "listening_list_json": lst, "section_html": html,
            "family_return_keys": sorted(out) if isinstance(out, dict) else None}


YSRC = "er121_output/family_y_production_01/redelivery_fee/run_style_fix_01"      # 既存Y Production run(読み取りのみ。必要なjsonだけ一時dirへコピー)


def _y_family_run(work, R, wav, account, stored=None):
    """Y family関数 `generate_y_a2_segments`(生成+完了hook)を、既存Y run_dirのparts/support/chunk planを一時dirへコピーして実走(japanese_titleのみ選択)。"""
    import shutil
    import er019_family_x_audio_production_runner_01 as xr
    import er121_family_y_audio_01 as ya
    import er006_secondary_asr_01 as sec6
    theme = os.path.join(work, "y_theme")
    for rel in ("a2/parts.json", "a2/support_texts.json", "a2/key_phrases/keywords_canonicalized.json", "a2/audit/chunk_plan_a2.json", "a2/audit/chunk_tts_decision.json"):
        if os.path.exists(os.path.join(YSRC, rel)):
            os.makedirs(os.path.dirname(os.path.join(theme, rel)), exist_ok=True)
            shutil.copyfile(os.path.join(YSRC, rel), os.path.join(theme, rel))
    snaps = []
    real_end = sec6.end_secondary_run

    def end_snap():
        rs = sec6._RUN_STATE
        if rs is not None:
            snaps.append({"secondary_calls": rs.secondary_calls, "est_jpy_total": round(rs.est_jpy_total, 4),
                          "consecutive_failures": rs.secondary_consecutive_failures, "circuit_open": rs.circuit_open})
        real_end()
    sec6.end_secondary_run = end_snap
    import io
    buf = io.StringIO()
    prev_only = xr._ONLY_SEGMENTS
    xr._ONLY_SEGMENTS = {"japanese_title"}
    try:
        with R.fake_tts_patch(wav), R.instrumented_asr(stored), contextlib.redirect_stdout(buf):
            out = ya.generate_y_a2_segments(theme, R.MOON, style_profile=ya.Y_APPROVED_STYLE_PROFILE)
    finally:
        xr._ONLY_SEGMENTS = prev_only
        sec6.end_secondary_run = real_end
    a2 = os.path.join(theme, "a2")
    doc = json.load(open(os.path.join(a2, "audit", "tts_generation_results.json"), encoding="utf-8"))
    seg = doc["segments"]["japanese_title"]
    lst_path = os.path.join(a2, "audit", "pass_with_warning_listening_list.json")
    lst = json.load(open(lst_path, encoding="utf-8")) if os.path.exists(lst_path) else None
    import er078_pass_with_warning_registry_01 as pww
    import er121_family_y_runner_01 as yr
    import er_user_listening_page_common_01 as cp
    ctx = types.SimpleNamespace(out_dir=theme, pages_dir=os.path.join(theme, "pages"))
    os.makedirs(ctx.pages_dir, exist_ok=True)
    s = R.summarize("y_family_generate_y_a2_segments", "Y", wav, R.MOON, seg, None)
    s["run_state_snapshots"] = snaps
    s["segment_statuses"] = {k: v.get("status") for k, v in doc["segments"].items()}
    account([s])
    return {"summary": s, "completion_block_stdout": buf.getvalue(), "listening_list_json": lst,
            "y_dev_page_section_html": yr._y_pww_aux_html(ctx, "dev", cp), "y_public_page_section_html": yr._y_pww_aux_html(ctx, cp.AUDIENCE_PUBLIC, cp)}


def _z_family_run(work, R, wav, account, stored=None):
    """Z family関数 `run_tts_stage`(生成+PNAP hook+完了hook)を、japanese_title clipのみ(only_clips)・実generators・偽TTS・実ASRで実走(一時run_dir)。"""
    import io
    import er063_family_z_audio_01 as z
    import er006_secondary_asr_01 as sec6
    run_dir = os.path.join(work, "z_run_family")
    story = [{"id": "full_story_part1_c1", "voice": "narrator", "text": "Melos was angry."}]
    kp = [{"rank": 1, "used_form": "run through", "japanese_gloss": "走り抜ける", "japanese_gloss_tts": "走り抜ける"}]
    plan = z.build_level_plan("a2", story, "preview text", {1: "c1 text", 2: "c2 text", 3: "c3 text"}, kp, "The Three-Day Promise", R.MOON)
    jt = [c for c in plan if c.kind == "japanese_title"]
    snaps = []
    real_end = sec6.end_secondary_run

    def end_snap():
        rs = sec6._RUN_STATE
        if rs is not None:
            snaps.append({"secondary_calls": rs.secondary_calls, "est_jpy_total": round(rs.est_jpy_total, 4),
                          "consecutive_failures": rs.secondary_consecutive_failures, "circuit_open": rs.circuit_open})
        real_end()
    sec6.end_secondary_run = end_snap
    buf = io.StringIO()
    try:
        with R.fake_tts_patch(wav), R.instrumented_asr(stored), contextlib.redirect_stdout(buf):
            out = z.run_tts_stage(run_dir, "a2", plan, generators=z.real_generators(), only_clips={jt[0].clip_id})
    finally:
        sec6.end_secondary_run = real_end
    a2 = os.path.join(run_dir, "a2")
    doc = json.load(open(os.path.join(a2, "audit", "tts_generation_results.json"), encoding="utf-8"))
    seg = (doc.get("segments") or {}).get(jt[0].clip_id) or {}
    lst_path = os.path.join(a2, "audit", "pass_with_warning_listening_list.json")
    lst = json.load(open(lst_path, encoding="utf-8")) if os.path.exists(lst_path) else None
    import er078_pass_with_warning_registry_01 as pww
    html = pww.render_html_section(pww.load_listening_list(a2), href_fn=lambda e: e.get("audio_path") or "")
    s = R.summarize("z_family_run_tts_stage", "Z", wav, R.MOON, seg, None)
    s["run_state_snapshots"] = snaps
    s["segment_statuses"] = {k: v.get("status") for k, v in (doc.get("segments") or {}).items()}
    account([s])
    return {"summary": s, "completion_block_stdout": buf.getvalue(), "listening_list_json": lst, "section_html": html,
            "stage_return_keys": sorted(out) if isinstance(out, dict) else None}


def run_e2(work, out_dir, R, account):
    """X/Y/Zそれぞれ family関数(生成+完了hook)を実走。Zには、E1の実judgement record(β)を同じ試聴リストへ足した完了blockも生成する。"""
    res = {}
    wav = {n: w for n, w, *_ in R.MOON6}["reselect a2"]       # 実ASRで4/4回 PASS_W(v2)になった音声
    res["X"] = _x_family_run(work, R, wav, account)
    res["Y"] = _y_family_run(work, R, wav, account)
    res["Z"] = _z_family_run(work, R, wav, account)
    # β例: E1/E1b/E1cで実際に得たβ判定のrecordを、Z a2の試聴リスト(v2例と同じrun)に足して完了block/JSON/節を生成
    beta_row = None
    for ph in ("e1", "e1b", "e1c"):
        pth = os.path.join(out_dir, f"runtime_evidence_{ph}_01.out.json")
        if os.path.exists(pth) and beta_row is None:
            for r in json.load(open(pth, encoding="utf-8")).get("rows", []):
                if r.get("rescue_basis") == "beta":
                    beta_row = dict(r, _src=f"{ph}:{r['moon_label']}")
                    break
    if beta_row:
        zdoc_path = None
        extra = {"beta_sample_from_" + beta_row["_src"].replace(" ", "_").replace(":", "_"): {
            "status": "OK", "text": R.MOON, "canonical_text": R.MOON, "path": beta_row["wav"], "sha256": beta_row["wav_sha256"],
            "asr_judgement": beta_row["asr_judgement"]}}
        base_entry = {"status": "OK", "text": R.MOON, "canonical_text": R.MOON, "path": wav, "sha256": res["Z"]["summary"]["wav_sha256"],
                      "asr_judgement": res["Z"]["summary"]["asr_judgement"]}
        res["Z_with_beta_sample"] = {"beta_sample_source": beta_row["_src"],
                                     **R.hook_outputs(os.path.join(work, "z_beta_sample_run", "a2"), "Family Z a2(v2+β例)", base_entry, extra_segments=extra)}
    return res


# ---------------------------------------------------------------- E3
def run_e3(work, out_dir, R, account):
    rows = []
    wavs = {n: w for n, w, *_ in R.MOON6}
    base = wavs["reselect a2"]      # 実ASRで4/4回 PASS_W(v2)になった音声を、正例(正しい原稿)と負例(数値だけ誤った原稿)に使う
    wrong = [("neg_value_8000", "月のしわ、8,000本超！その奥に潜む「岩の上着」の秘密"),
             ("neg_value_9800", "月のしわ、9,800本超！その奥に潜む「岩の上着」の秘密")]
    for tag, canon in wrong:
        s, _ = R.verified_strict(canon, base, "X", work, "e3_" + tag)
        s["note"] = "原稿の数値だけを誤りにした負例(同じwav)。期待=NG/HR・rescue_basis無し"
        rows.append(s)
        account([s])
    # scope外(None): 同じ正例wav・正しい原稿 -> 新キー無し(従来判定)
    s, _ = R.verified_strict(R.MOON, base, None, work, "e3_scope_none_positive")
    s["note"] = "scope外(A/B/C相当): ja_v2beta/verdict/judge_rule_versionのキー自体が無いこと"
    s["has_new_keys"] = {k: (k in (s["asr_judgement"] or {})) for k in ("ja_v2beta", "verdict", "rescue_basis", "judge_rule_version")}
    rows.append(s)
    account([s])
    return {"rows": rows}
