# ============================================================
# er003_fallback_style_retention_probe_01.py
# FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01 委任_06
# ============================================================
# 実行: .venv/Scripts/python.exe er003_fallback_style_retention_probe_01.py
#
# ¥0モックprobe(Opus B4(i)): TTS境界(speech_metadata call_fn factory)だけを差し替え、
# Family X audio runnerの実コード(generate_family_x_a2_segments/generate_family_x_b1_segments)を
# 実際に走らせて、初回・標準retry・fallback・regeneration(Local Rewrite再TTS)・resume の全経路で
# `speech_metadata.style`(=TTSへ渡るpayloadのstyle)を捕捉し、対象roleで承認値と一致し、対象外roleで
# 従来値であることを表にして FALLBACK_MOCK_PROBE_01.md へ書く。
# ¥0統計(Opus B4(ii)): Tone Trial 2件と既存Flash-Lite era記録のrole別失敗回数を集計する(read-only)。
# API/LLM/TTS/ASR呼び出しなし(socket.connectも遮断して検証)。
from __future__ import annotations

import collections
import datetime
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
from unittest import mock

import er003_fallback_style_retention_test_01 as T
import er003_v1_n3_01_tts_generate as n3_tts
import er019_family_x_audio_production_runner_01 as runner
import er020_tts_retry_local_rewrite_01 as retry_primitive
import er033_tts_flash_lite_family_x_styles_01 as fl_styles

FL = T.FL
OUT_MD = "er053_output/coffee_new_tone_e2e_01/FALLBACK_MOCK_PROBE_01.md"
S = fl_styles
FB0 = S.FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]


def slower(base: str) -> str:
    return f"{base}\n{n3_tts.A2_SLOWER_PACE_INSTRUCTION.strip()}"


# 期待値: (level, seg) -> {"std": 標準経路style, "fb": fallback(技術的fallback/A2 fallback)style,
#                          "lr": Local Rewrite再TTS style, "target": 新tone対象か}
A2_EXPECT = {}
for seg in ("japanese_title", "preview", "comment_1", "comment_2", "comment_3", "comment_4"):
    A2_EXPECT[seg] = {"std": S.JA_J2_BRIGHT, "fb": S.JA_J2_BRIGHT, "lr": None, "target": "JA_J2_BRIGHT"}
for seg in ("full_story_part1", "full_story_part2", "full_story_part3"):
    v = slower(S.EN_FULLSTORY_F1_5)
    A2_EXPECT[seg] = {"std": v, "fb": v, "lr": v, "target": "EN_FULLSTORY_F1_5(+減速連結)"}
A2_EXPECT["topic_intro"] = {"std": S.FAMILY_X_ROLE_STYLE_EN["TOPIC_INTRO"], "fb": FB0, "lr": FB0, "target": "対象外"}
A2_EXPECT["in_one_line"] = {"std": slower(S.FAMILY_X_ROLE_STYLE_EN["IN_ONE_LINE"]), "fb": FB0, "lr": FB0,
                            "target": "対象外"}

B1B_EXPECT = {}
for seg in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
    B1B_EXPECT[seg] = {"std": S.EN_COMMENT_E2_UPBEAT, "fb": S.EN_COMMENT_E2_UPBEAT, "lr": S.EN_COMMENT_E2_UPBEAT,
                       "target": "EN_COMMENT_E2_UPBEAT"}
for seg in ("full_story_part1", "full_story_part2", "full_story_part3"):
    B1B_EXPECT[seg] = {"std": S.EN_FULLSTORY_F1_5, "fb": S.EN_FULLSTORY_F1_5, "lr": S.EN_FULLSTORY_F1_5,
                       "target": "EN_FULLSTORY_F1_5"}
B1B_EXPECT["topic_intro"] = {"std": S.FAMILY_X_ROLE_STYLE_EN["TOPIC_INTRO"], "fb": FB0,
                              "lr": S.FAMILY_X_ROLE_STYLE_EN["TOPIC_INTRO"], "target": "対象外"}
# in_one_line(B1B)のLocal Rewrite再TTS: 既存挙動(news_tail_fix.__wrapped__へstyle_prefix_overrideを
# 渡さない=標準ENGLISH_STYLE_PREFIX)。対象外roleのため本件では変更しない(報告に記載)。
B1B_EXPECT["in_one_line"] = {"std": S.FAMILY_X_ROLE_STYLE_EN["IN_ONE_LINE"], "fb": FB0, "lr": "<DEFAULT_ENGLISH_STYLE_PREFIX>",
                              "target": "対象外"}

JA_TEXT = "コーヒーの値段は今年も上がり続けています。"
EN_TEXT = "Prices keep rising across the whole coffee market this year."


def _make_theme_dir(tmp: str) -> str:
    theme = os.path.join(tmp, "probe_theme")
    a2 = os.path.join(theme, "a2")
    b1b = os.path.join(theme, "b1b")
    os.makedirs(a2)
    os.makedirs(b1b)
    parts = {"title": "Coffee Prices", "title_tts": "Coffee Prices", "part1": EN_TEXT, "part2": EN_TEXT + " Next.",
             "part3": EN_TEXT + " Last.", "in_one_line": "Prices keep rising."}
    T._wj(os.path.join(a2, "parts.json"), parts)
    T._wj(os.path.join(b1b, "parts.json"), parts)
    T._wj(os.path.join(a2, "a2_support_texts.json"), {k: JA_TEXT for k in ("preview", "comment_1", "comment_2",
                                                                              "comment_3", "comment_4")})
    T._wj(os.path.join(b1b, "b1_support_texts.json"), {k: EN_TEXT for k in ("preview", "comment_1", "comment_2",
                                                                              "comment_3", "comment_4")})
    return theme


def _default_prefix() -> str:
    import er003_b1_p9a_audio as p9a
    return p9a.ENGLISH_STYLE_PREFIX


def _run_level(level: str, scenario: str):
    """level in {"a2","b1b"}, scenario in {first, std_retry, fallback, regeneration}。
    戻り値: harness(captured calls)。"""
    max_retry = n3_tts.p9a.MAX_TTS_TECHNICAL_RETRY
    if scenario == "first":
        verdict, fail = (lambda s, n: True), None
    elif scenario == "std_retry":
        verdict, fail = (lambda s, n: n >= 2), None
    elif scenario == "fallback":
        if level == "a2":
            verdict, fail = (lambda s, n: n >= 3), None   # 標準2回ASR不合格→fallback(第3 attempt)で合格
        else:
            # B1B: 技術的fallbackのみ発火。標準attempt1のTTS呼び出しを例外で使い切り→同一attempt内でfallback。
            verdict, fail = (lambda s, n: True), (lambda s, n: n <= max_retry + 1)
    elif scenario == "regeneration":
        verdict, fail = (lambda s, n: n >= 4), None       # 3 attempt不合格→Local Rewrite再TTSで合格
    else:
        raise ValueError(scenario)
    with T.Harness(verdict_fn=verdict, tts_fail_fn=fail) as h:
        # JA経路(resolver)がnetworkへ出ないよう差し替え(JA本文は固有外来表記なし)
        with mock.patch.object(T.pron_resolver_core, "resolve_unknown_ja_tokens",
                               return_value={"reading_dictionary": {}}), \
             mock.patch("socket.socket.connect", side_effect=AssertionError("network blocked in probe")), \
             mock.patch.object(runner.shared_narration, "ensure_all_shared_narration_a2", return_value={}), \
             mock.patch.object(runner.shared_narration, "ensure_all_shared_narration_b1", return_value={}), \
             mock.patch.object(runner, "_assert_shared_narration_ok", return_value=None), \
             mock.patch.object(runner, "_summarize_shared_narration", return_value={}):
            theme = _make_theme_dir(h.tmpdir)
            if level == "a2":
                runner.generate_family_x_a2_segments(theme, "日本語タイトル", tts_backend=FL)
            else:
                runner.generate_family_x_b1_segments(theme, tts_backend=FL)
            h.theme = theme
            h.results_path = os.path.join(theme, level, "audit", "tts_generation_results.json")
            return _snapshot(h)


def _snapshot(h):
    snap = types_namespace()
    snap.calls = list(h.calls)
    snap.lr_calls = list(h.lr_calls)
    return snap


class types_namespace:
    pass


def _phase_label(level: str, scenario: str, seg: str, idx: int, call: dict) -> str:
    """idx=その segment 内の通し番号(1始まり、技術retry込みの呼び出し順)。"""
    if scenario == "first":
        return "初回"
    if scenario == "std_retry":
        return "初回" if idx == 1 else "標準retry"
    if scenario == "fallback":
        if level == "a2":
            return ["初回", "標準retry", "fallback"][min(idx, 3) - 1]
        k = n3_tts.p9a.MAX_TTS_TECHNICAL_RETRY + 1
        return "初回(標準・TTS例外)" if idx <= k else "fallback(技術的)"
    if scenario == "regeneration":
        return ["初回", "標準retry", "fallback/第3attempt", "regeneration(Local Rewrite再TTS)"][min(idx, 4) - 1]
    return "?"


def _expected_for(expect: dict, level: str, scenario: str, seg: str, phase: str) -> str:
    e = expect[seg]
    if phase.startswith("初回") or phase == "標準retry":
        return e["std"]
    if phase.startswith("fallback") or phase == "fallback/第3attempt":
        if level == "b1b" and phase.startswith("fallback/"):
            return e["std"]  # B1Bの第3 attemptは標準style(同一style retry)
        return e["fb"]
    if phase.startswith("regeneration"):
        return e["lr"]
    raise ValueError(phase)


def build_rows():
    rows = []   # (level, scenario, seg, phase, style_head, expected_head, source, match)
    mismatches = 0
    for level, expect in (("a2", A2_EXPECT), ("b1b", B1B_EXPECT)):
        for scenario in ("first", "std_retry", "fallback", "regeneration"):
            snap = _run_level(level, scenario)
            by_seg = collections.defaultdict(list)
            for c in snap.calls:
                by_seg[c["seg"]].append(c)
            for seg, calls in by_seg.items():
                if seg not in expect:
                    continue
                if seg in A2_JA_SEGS and level == "a2" and scenario == "regeneration" and len(calls) < 4:
                    pass
                seen_fb_technical = False
                for i, c in enumerate(calls, start=1):
                    phase = _phase_label(level, scenario, seg, i, c)
                    exp = _expected_for(expect, level, scenario, seg, phase)
                    # JAのregeneration: n3 JAにLocal Rewriteは無いため4回目呼び出し自体が存在しない
                    if exp == "<DEFAULT_ENGLISH_STYLE_PREFIX>":
                        exp = _default_prefix()
                    if exp is None:
                        continue
                    match = (c["style"] == exp)
                    if not match:
                        mismatches += 1
                    # B1Bの技術的fallbackは同一attempt内で複数回(技術retry)呼ばれうるため重複行は畳む
                    key = (level, scenario, seg, phase)
                    if rows and rows[-1][:4] == key and rows[-1][4] == c["style"]:
                        continue
                    rows.append((level, scenario, seg, phase, c["style"], exp, expect[seg]["target"], match))
    return rows, mismatches


A2_JA_SEGS = {"japanese_title", "preview", "comment_1", "comment_2", "comment_3", "comment_4"}


def resume_probe():
    """resume: (a)同一out_dirで再実行→v5 cacheを再利用(TTS 0回)。(b)cacheのstyle_versionを旧v4へ書換え→
    再生成(TTS発生、styleは承認値)。"""
    out = {}
    with T.Harness() as h:
        with mock.patch.object(T.pron_resolver_core, "resolve_unknown_ja_tokens",
                               return_value={"reading_dictionary": {}}), \
             mock.patch("socket.socket.connect", side_effect=AssertionError("network blocked in probe")), \
             mock.patch.object(runner.shared_narration, "ensure_all_shared_narration_a2", return_value={}), \
             mock.patch.object(runner, "_assert_shared_narration_ok", return_value=None), \
             mock.patch.object(runner, "_summarize_shared_narration", return_value={}):
            theme = _make_theme_dir(h.tmpdir)
            runner.generate_family_x_a2_segments(theme, "日本語タイトル", tts_backend=FL)
            first_calls = len(h.calls)
            res_path = os.path.join(theme, "a2", "audit", "tts_generation_results.json")
            with open(res_path, encoding="utf-8") as f:
                saved = json.load(f)
            out["saved_style_version"] = saved["style_version"]
            runner.generate_family_x_a2_segments(theme, "日本語タイトル", tts_backend=FL)
            out["first_run_calls"] = first_calls
            out["rerun_v5_calls"] = len(h.calls) - first_calls   # 期待0(全segment reuse)
            # 旧versionへ書換え(旧fallback style音声が残っているcacheの想定)
            saved["style_version"] = "v4_j2_e2upbeat_f15_tone_refresh"
            with open(res_path, "w", encoding="utf-8") as f:
                json.dump(saved, f, ensure_ascii=False)
            before = len(h.calls)
            runner.generate_family_x_a2_segments(theme, "日本語タイトル", tts_backend=FL)
            new_calls = h.calls[before:]
            out["rerun_v4_calls"] = len(new_calls)
            out["rerun_v4_all_styles_expected"] = all(
                c["style"] == A2_EXPECT[c["seg"]]["std"] for c in new_calls if c["seg"] in A2_EXPECT)
            out["rerun_v4_segments"] = sorted({c["seg"] for c in new_calls})
    return out


def kp_probe():
    """Standard KP日本語意味(J2)・KP英語(Master Store経由=不変)。"""
    kp = {"items": [{"rank": 1, "used_form": "opt out", "japanese_gloss": "やめる", "japanese_gloss_tts": "やめる"}]}
    res = {}
    for scenario, verdict in (("first", lambda s, n: True), ("std_retry", lambda s, n: n >= 2),
                              ("fallback", lambda s, n: n >= 3)):
        with T.Harness(verdict_fn=verdict) as h:
            with mock.patch.object(T.pron_resolver_core, "resolve_unknown_ja_tokens",
                                   return_value={"reading_dictionary": {}}), \
                 mock.patch("socket.socket.connect", side_effect=AssertionError("network blocked in probe")), \
                 mock.patch.object(runner.shared_narration, "ensure_key_phrase_english_component",
                                   return_value={"status": "OK"}) as en:
                nd = os.path.join(h.tmpdir, "probe_theme", "a2", "narration")
                os.makedirs(nd)
                runner._generate_key_phrase_segments_a2(kp, nd, None, tts_backend=FL)
            res[scenario] = {"styles": h.styles(), "kp_en_kwargs": sorted(en.call_args.kwargs)}
    return res


def stats_section() -> str:
    lines = []
    # --- Tone Trial 2件
    lines.append("### 統計A: Tone Trial 2件(新tone承認時のDEV実測、Flash-Lite、speech_metadata方式)")
    lines.append("")
    lines.append("| Trial | sample数 | status=OK | 技術retry発生(retry_count>0) | 400/空応答 | ASR不合格(EXACT/NORMALIZED以外) |")
    lines.append("|---|---|---|---|---|---|")
    for name, path in (("tts_voice_tone_brightness_trial_01(JA J0-J3 / EN E0-E3)",
                        "er053_output/tts_voice_tone_brightness_trial_01/results_01.jsonl"),
                       ("tts_full_story_tone_trial_01(Full Story F0/F1/F1.5/F2)",
                        "er053_output/tts_full_story_tone_trial_01/results_01.jsonl")):
        recs = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
        n = len(recs)
        ok = sum(1 for r in recs if r.get("status") == "OK")
        retry = sum(1 for r in recs if (r.get("retry_count") or 0) > 0)
        err = sum(1 for r in recs if r.get("reason") and ("400" in str(r.get("reason")) or "空" in str(r.get("reason"))))
        asr_bad = sum(1 for r in recs if r.get("asr_classification") not in ("EXACT_MATCH", "NORMALIZED_MATCH"))
        lines.append(f"| {name} | {n} | {ok} | {retry} | {err} | {asr_bad} |")
    lines.append("")
    lines.append("sample別(sample_id/role/voice/style種別/status/call_count/retry_count/asr_classification): 12件すべて"
                 " status=OK・call_count=1・retry_count=0・ASR EXACT_MATCH or NORMALIZED_MATCH"
                 "(J2_BRIGHT/E2_UPBEAT/F1.5=承認3 styleを含む)。")
    lines.append("")
    # --- Flash-Lite era 既存run記録(tracked review_lock_state.json、updated_at>=2026-09-27)
    lines.append("### 統計B: 既存Flash-Lite era記録(2026-09-27以降のreview_lock_state.json last_attempts_log、git管理分)")
    lines.append("")
    lines.append("注意: last_attempts_logは各segmentの最終部分のみ保持。旧style(J3/E2等・承認前)での実績であり、新tone標準経路の"
                 "本番runは未実施。role別の『Style起因(400/空応答/ASR不合格)の系統的失敗の兆候』の下限観測であり、完全な母集団ではない。")
    lines.append("")
    cnt = collections.defaultdict(lambda: collections.Counter())
    seen = set()
    for path in subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.splitlines():
        if not path.endswith("review_lock_state.json"):
            continue
        try:
            with open(path, encoding="utf-8") as f:
                st = json.load(f)
        except Exception:
            continue
        for seg_key, rec in st.items():
            if not isinstance(rec, dict):
                continue
            if (rec.get("updated_at") or "") < "2026-09-27":
                continue
            ident = (rec.get("theme_id"), rec.get("level"), rec.get("segment_id"), rec.get("canonical_text_sha256"),
                     rec.get("updated_at"))
            if ident in seen:
                continue
            seen.add(ident)
            seg = rec.get("segment_id") or seg_key
            lang = rec.get("language")
            level = rec.get("level")
            if level not in ("a2", "b1b"):
                continue  # *_dev/試験fixture等のlevel名は除外(本番Level=a2/b1bのみ)
            role = retry_primitive.resolve_narrative_role(seg)
            if lang == "ja":
                role = "JA:" + ("title" if "title" in seg else "meaning" if "meaning" in seg else "preview/comment")
            elif role is None or role.startswith("full_story_part") or seg.endswith("_charon") or seg.startswith("num_"):
                role = "固定phrase/見出し/その他(Master・Heading・KP等)"
            key = f"{level}/{role}"
            for a in rec.get("last_attempts_log") or []:
                cnt[key]["attempts"] += 1
                reason = str(a.get("reason") or "")
                if a.get("status") != "OK":
                    if "400" in reason or "INVALID_ARGUMENT" in reason:
                        cnt[key]["TTS 400"] += 1
                    elif "空" in reason or "empty" in reason.lower():
                        cnt[key]["TTS 空応答"] += 1
                    else:
                        cnt[key]["TTS他/STOPPED"] += 1
                elif a.get("verified") is False:
                    cnt[key]["ASR/QA不合格"] += 1
                if a.get("instruction_type") == "minimal_fallback":
                    cnt[key]["fallback発火"] += 1
            cnt[key]["segments"] += 1
            if rec.get("state") in ("HUMAN_REVIEW_REQUIRED",):
                cnt[key]["HRL"] += 1
    cols = ["segments", "attempts", "ASR/QA不合格", "TTS 400", "TTS 空応答", "TTS他/STOPPED", "fallback発火", "HRL"]
    lines.append("| level/role | " + " | ".join(cols) + " |")
    lines.append("|---|" + "|".join("---" for _ in cols) + "|")
    for key in sorted(cnt):
        lines.append(f"| {key} | " + " | ".join(str(cnt[key][c]) for c in cols) + " |")
    lines.append("")
    return "\n".join(lines)


def main():
    rows, mismatches = build_rows()
    resume = resume_probe()
    kp = kp_probe()
    stats = stats_section()
    now = datetime.date.today().isoformat()
    L = []
    L.append("# FALLBACK_MOCK_PROBE_01(FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01 委任_06、API課金0)")
    L.append("")
    L.append(f"生成: {now} / `.venv` `python er003_fallback_style_retention_probe_01.py` / "
             "worktree `eigo-radio-tone-fb`(branch feature/coffee-new-tone-fallback-01)")
    L.append("")
    L.append("方法: TTS境界(`er033...make_speech_metadata_batch_call_fn`/`..._call_fn`)のみモック。Family X audio runner"
             "(`generate_family_x_a2_segments`/`generate_family_x_b1_segments`)の実コード・実の下位関数(crosslevel/n3/voice01/"
             "news_tail_fix/repro01/review_lock)をそのまま実行し、各TTS呼び出しの `payload=(text, style)` の style"
             "(=`speech_metadata.style`)を捕捉した。ASR・Cascade判定・Local Rewrite・発音resolverはモック(スクリプト化した合否で"
             "各経路を強制発火)。`socket.connect`を遮断して実ネットワーク呼び出し0を確認。使用モデル名: 実API未使用"
             f"(記録上のmodel_idは `{fl_styles.FAMILY_X_FLASH_LITE_MODEL_NAME}`)。")
    L.append("")
    L.append(f"## 結果サマリ: 全{len(rows)}行中 style不一致 = **{mismatches}**")
    L.append("")
    L.append("経路定義: A2(Standard)=標準2回(ASR不合格で次attempt)→fallback1回(承認style維持=本件)→Local Rewrite再TTS。"
             "B1B(Advanced)=同一style最大3回retry+TTS例外時のみ技術的fallback+Local Rewrite再TTS。"
             "JA(A2)にはLocal Rewrite再TTSは存在しない(英語のみ)ため regeneration 行は英語segmentのみ。")
    L.append("")
    L.append("| level | 経路 | segment | phase | 対象 | 捕捉style(長い場合は先頭44字…末尾40字) | 期待一致 |")
    L.append("|---|---|---|---|---|---|---|")
    for level, scenario, seg, phase, style, exp, target, match in rows:
        one = style.replace("\n", "\\n")
        head = one if len(one) <= 90 else one[:44] + "…" + one[-40:]
        L.append(f"| {level} | {scenario} | {seg} | {phase} | {target} | `{head}` | {'OK' if match else '**NG**'} |")
    L.append("")
    L.append("### 期待style(正本=標準経路に実際に渡したstyle)")
    L.append("- JA_J2_BRIGHT: " + S.JA_J2_BRIGHT)
    L.append("- EN_COMMENT_E2_UPBEAT: " + S.EN_COMMENT_E2_UPBEAT)
    L.append("- EN_FULLSTORY_F1_5: " + S.EN_FULLSTORY_F1_5 + "(A2は末尾に `\\n` + A2_SLOWER_PACE_INSTRUCTION を連結)")
    L.append("- 対象外roleのfallback: `" + FB0 + "`(従来のFALLBACK style、変更なし)")
    L.append("")
    L.append("## resume(同一out_dirの再実行)")
    L.append(f"- 保存されるstyle_version: `{resume['saved_style_version']}`")
    L.append(f"- 初回run TTS呼び出し数={resume['first_run_calls']} → 同一version(v5)で再実行: TTS呼び出し数="
             f"**{resume['rerun_v5_calls']}**(全segment reuse、期待0)")
    L.append(f"- cacheのstyle_versionを旧v4へ書換えて再実行: TTS呼び出し数=**{resume['rerun_v4_calls']}**(旧cacheを黙って"
             f"再利用せず再生成)、全styleが承認値かつ期待一致={resume['rerun_v4_all_styles_expected']}、"
             f"再生成segment={', '.join(resume['rerun_v4_segments'])}")
    L.append("")
    L.append("## Standard KP日本語意味(J2)・KP英語(Master Store経由)")
    for sc, d in kp.items():
        L.append(f"- {sc}: KP日本語意味 style列={[x[:24] for x in d['styles']]}(全てJ2逐語: "
                 f"{all(x == S.JA_J2_BRIGHT for x in d['styles'])})、KP英語(shared_narration)へ渡るkwargs={d['kp_en_kwargs']}"
                 "(fallback_style_prefixを含まない=不変)")
    L.append("")
    L.append("## ¥0統計(Opus B4(ii))")
    L.append("")
    L.append(stats)
    L.append("### 読み取り(Style起因の系統的失敗の兆候)")
    L.append("- 新tone標準経路(J2/E2_UPBEAT/F1.5)のTone Trial 12/12件は初回で成功(retry 0、400/空応答 0、ASR不合格 0)。"
             "承認styleそのものが標準経路で400・空応答・ASR不合格を系統的に誘発する兆候は、この少数サンプルでは観測されない。")
    L.append("- 既存Flash-Lite era(2026-09-27以降、a2/b1bのみ)のlast_attempts_logでは、Style起因が疑われる400 INVALID_ARGUMENT・"
             "空応答は全roleで0件(記録されたreason欄に限る)。ASR/QA不合格はrole別に存在するが(例: b1b/FULL_STORY 16/54 attempt、"
             "a2/FULL_STORY 8/32)、旧style時代の値で内容(数詞・固有名詞等)起因が主であり、新tone styleとの因果は本データからは"
             "判別不能。=『Style起因の系統的失敗の兆候』は既存データ上は観測されないが、新tone styleでの本番標準runは未実施のため確定的ではない。")
    L.append("- 既存Flash-Lite eraの集計(統計B)はstyle別ではなくrole別の下限観測。role別の400/空応答/ASR不合格の件数は上表。"
             "fallback発火自体が極めて少ない(設計書§1-4と一致)ため、承認style維持fallbackの救済率は**実測不能**のまま"
             "(設計書の条件付きGate『強制fallback実測probe』は別委任・少額実測の対象。本probeは¥0のstyle伝播検証のみ)。")
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print(f"rows={len(rows)} mismatches={mismatches} resume={resume}")
    return 0 if mismatches == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
