# -*- coding: utf-8 -*-
# ============================================================
# er110_family_y_audio_trial_01.py
# FAMILY-Y-VOICES-DESIGN-01 委任_05 Phase 3: Family Y 統合Trialの音声段(DEV/Trial専用)
# ============================================================
# 位置づけ: DEV/Trial経路のみ。Family Y機能はProduction到達経路に入れない(どのProduction runner/.env/起動scriptからも参照されない。
#   環境変数・flag・CLI切替なし。X/Z Production .py・Prompt・閾値は一切変更しない。このfileはimport(読み取り利用)のみ)。
# 方式: Family X正式Production基盤(er019_family_x_audio_production_runner_01 = xr)の部品をそのまま呼ぶ薄い入口。
#   Xとの差分(Y固有)は次の3点だけ:
#   (1) 本文が5パート(リード → Voice1 → Voice2 → Voice3 → 最終)で、Comment 4を持たない(Comment 3まで)。
#   (2) Voice1〜3は固定TTS Voice(Algieba/Zephyr/Schedar、ユーザー決定。自動割当関数は使わない)。リード/最終/In One LineはAoede。
#       Voice切替は`p9a.VOICE_NAME`のprocess内一時差替え(context manager、finallyで必ず復元。Xの本文生成関数をそのまま使うため)。
#       Pro系TTSは使わない(tts_backend="speech_metadata_flash_lite"固定、gemini-3.8-flash-lite-tts)。
#   (3) 本文segment IDはX共有検証部品(resolve_narrative_role等)がFULL_STORYと解決するIDに合わせたalias:
#         part1=full_story_part1(リード) / part2=full_story_part2(V1) / part3=full_story_part3(V2)
#         / part4=full_story_part3_c2(V3) / part5=full_story_part3_c3(最終)
#       (`full_story_part[1-3]_c[0-9]+`はZのPart内clip用に既存の後方互換パターン。er020等の共有ファイルは無変更)。
#       これによりConnected Speech/Local Rewrite/Repetition QA/disfluency/Std 6%減速がXと同じ経路でY本文5segmentすべてに掛かる。
# Master Audio Store: Trial名前空間(ProductionストアのスナップショットをTrial dirへコピーし、process内でmas.STORE_DIR等を差し替える)。
#   Production storeには書き込まない(読み取りコピーのみ)。
# 適用しない検査: er109(表記違い同音)・PNAP(固有名詞アラーム)のscopeはX/Z限定リテラル(AST test固定)のためY processでは非活性。
# ============================================================
from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import shutil
import sys

import er019_family_x_audio_production_runner_01 as xr

MANAGEMENT_ID = "FAMILY-Y-VOICES-DESIGN-01"
BASE = "er110_output/family_y_trial_01"
SRC = f"{BASE}/school_phone_ban"
OUT_ROOT = f"{BASE}/audio"
TTS_BACKEND = "speech_metadata_flash_lite"          # Pro系TTS不使用(X/Zと同じFlash-Lite)
STYLE_PROFILE = "fx_20261017"                        # X新規run既定profile(Full Story=PD06 ほか)をそのまま継承
CANDIDATES = {"r2": "R2g(主候補)", "r0": "R0g(比較候補)"}

# (y_role, segment_id, tts_voice)。Voice1〜3はユーザー決定の固定割当。
Y_BODY = (
    ("lead", "full_story_part1", "Aoede"),
    ("voice_1", "full_story_part2", "Algieba"),
    ("voice_2", "full_story_part3", "Zephyr"),
    ("voice_3", "full_story_part3_c2", "Schedar"),
    ("final", "full_story_part3_c3", "Aoede"),
)
Y_BODY_IDS = tuple(s for _r, s, _v in Y_BODY)
Y_VOICE_OF = {s: v for _r, s, v in Y_BODY}
Y_ROLE_OF = {s: r for r, s, _v in Y_BODY}
FIXED_VOICE_SLOTS = {"voice_1": "Algieba", "voice_2": "Zephyr", "voice_3": "Schedar"}
VOICE_SEGMENT_IDS = tuple(s for r, s, _v in Y_BODY if r.startswith("voice_"))
# Voice同士・リード/最終との間の無音(Xの語り手切替pauseと同値。Y固有の新規値ではない)
SPEAKER_GAP_SECONDS = xr.asm.CHARON_TO_AOEDE_PAUSE_SECONDS


class YAudioStop(RuntimeError):
    pass


# ============================================================
# 共通
# ============================================================
load_json, save_json, load_text, save_text = xr.load_json, xr.save_json, xr.load_text, xr.save_text


@contextlib.contextmanager
def tts_voice(voice_name: str):
    """X本文生成関数が呼出時に読む`p9a.VOICE_NAME`をprocess内で一時差替え(finallyで必ず復元)。Production fileは編集しない。"""
    p9a = xr.p9a
    prev = p9a.VOICE_NAME
    p9a.VOICE_NAME = voice_name
    try:
        yield
    finally:
        p9a.VOICE_NAME = prev


def use_trial_master_store(trial_store_dir: str, production_store_dir: str = "er006_output/master_audio_store_01") -> dict:
    """Trial名前空間のMaster Audio Store。Productionストアのスナップショットをコピーし、process内でmas.*のpathを差し替える
    (Production storeへは書き込まない)。既存コピーがあれば再利用(resume)。"""
    import er006_master_audio_store_01 as mas
    if not os.path.isdir(trial_store_dir):
        shutil.copytree(production_store_dir, trial_store_dir)
    mas.STORE_DIR = trial_store_dir
    mas.AUDIO_DIR = f"{trial_store_dir}/audio"
    mas.MANIFEST_PATH = f"{trial_store_dir}/manifest.json"
    mas.TELEMETRY_PATH = f"{trial_store_dir}/reuse_telemetry.jsonl"
    return {"trial_store_dir": trial_store_dir, "production_store_dir": production_store_dir,
            "method": "snapshot copy + process-local module path override (er006_master_audio_store_01.STORE_DIR/AUDIO_DIR/MANIFEST_PATH/TELEMETRY_PATH)"}


# ============================================================
# prep: Phase 2の英語完成稿・scaffoldからTTS入力(parts/support/KP)を組む(LLM/API 0)
# ============================================================
def split_y_article(text: str) -> dict:
    t = (text or "").strip()
    m = re.match(r"^#\s+(.+?)\s*\n+(.*)$", t, re.S)
    if not m:
        raise YAudioStop("Y article: title行(# ...)がありません")
    title, rest = m.group(1).strip(), m.group(2)
    iol = ""
    mm = re.search(r"\n##\s*In one line\s*\n(.*)$", "\n" + rest, re.S | re.I)
    if not mm:
        raise YAudioStop("Y article: '## In one line' がありません")
    iol = mm.group(1).strip()
    rest = ("\n" + rest)[: mm.start()].strip()
    paras = [b.strip() for b in re.split(r"\n\s*\n", rest) if b.strip()]
    if len(paras) != 5:
        raise YAudioStop(f"Y article: 本文段落が5でありません(={len(paras)})")
    if not iol:
        raise YAudioStop("Y article: In one lineが空です")
    parts = {"title": title, "in_one_line": iol}
    for i, p in enumerate(paras, start=1):
        parts[f"part{i}"] = p
    parts["word_counts"] = {f"part{i}": len(p.split()) for i, p in enumerate(paras, start=1)}
    parts["word_counts"]["in_one_line"] = len(iol.split())
    parts["status"] = "OK"
    parts["y_segment_map"] = {f"part{i}": {"segment_id": s, "y_role": r, "tts_voice": v}
                              for i, (r, s, v) in enumerate(Y_BODY, start=1)}
    return parts


def theme_dir(cand: str) -> str:
    return f"{OUT_ROOT}/{cand}"


def prepare(cand: str) -> dict:
    src = f"{SRC}/english_{cand}"
    theme = theme_dir(cand)
    info = {"cand": cand, "levels": {}}
    for lvl, scaf, sup in (("b1b", "scaffold_b1b", "b1_support_texts.json"), ("a2", "scaffold_a2", "a2_support_texts.json")):
        art_path = f"{src}/{lvl}/article.md"
        parts = split_y_article(load_text(art_path))
        os.makedirs(f"{theme}/{lvl}/audit", exist_ok=True)
        save_json(f"{theme}/{lvl}/parts.json", parts)
        support = load_json(f"{src}/{scaf}/{sup}")
        if any(k not in support for k in ("preview", "comment_1", "comment_2", "comment_3")):
            raise YAudioStop(f"{lvl}: support textsにpreview/comment_1〜3が揃っていません")
        support = {k: support[k] for k in ("preview", "comment_1", "comment_2", "comment_3")}   # Comment 4は廃止(ユーザー決定)
        save_json(f"{theme}/{lvl}/{sup}", support)
        kp_dst = f"{theme}/{lvl}/key_phrases"
        if not os.path.isdir(kp_dst):
            shutil.copytree(f"{src}/{scaf}/key_phrases", kp_dst)
        info["levels"][lvl] = {"article": art_path, "word_counts": parts["word_counts"]}
    save_json(f"{theme}/japanese_title.json", load_json(f"{src}/japanese_title.json"))
    pid, psrc = xr.style_profile_mod.resolve_run_profile(theme, STYLE_PROFILE, write=True, tts_backend=TTS_BACKEND)
    info["style_profile"] = {"profile_id": pid, "source": psrc}
    save_json(f"{theme}/y_entry_point.json", {
        "management_id": MANAGEMENT_ID, "phase": "3_audio_trial", "cand": cand, "source_dir": src, "tts_backend": TTS_BACKEND,
        "style_profile": pid, "fixed_voices": FIXED_VOICE_SLOTS, "y_body": [list(x) for x in Y_BODY],
        "speaker_gap_seconds": SPEAKER_GAP_SECONDS, "production_reachable": False,
        "not_applied_checks": ["er109 orthographic-variant equivalence (X/Z scope only)", "PNAP proper-noun alarm policy (X/Z scope only)",
                               "ensure_rf_record pre-TTS RF insurance (RF already run in Phase 2, not rerun)"],
    })
    return info


def voice_guard_cached(cached: dict | None) -> dict | None:
    """M4(Opus S/M): 同一out_dirのresume時、本文segmentの前回entryを再利用してよいのは『要求Voiceが一致する』場合だけ。
    XのMaster Audio Storeはspeaker_voiceをkeyに含むが、run内cache(tts_generation_results.json)はsegment ID+テキストのみで照合するため、
    Y側でVoice名を追加照合する薄いラッパー(X関数は無変更)。記録のないentry・Voice不一致entryは再利用せず再生成させる(cacheから外す)。"""
    if not cached:
        return cached
    segs = dict(cached.get("segments") or {})
    dropped = []
    for sid, voice in Y_VOICE_OF.items():
        e = segs.get(sid)
        if e is not None and e.get("y_tts_voice_requested") != voice:
            segs.pop(sid)
            dropped.append(sid)
    out = dict(cached)
    out["segments"] = segs
    if dropped:
        out["y_m4_dropped_for_voice_mismatch"] = dropped
    return out


# ============================================================
# TTS: Advanced(b1b)
# ============================================================
def _role_style_fn(level: str):
    import er033_tts_flash_lite_family_x_styles_01 as fl_styles

    def _base(role: str):
        return fl_styles.FAMILY_X_ROLE_STYLE_EN.get(role)

    def _role_style(role: str):
        return xr.style_profile_mod.resolve_role_style(STYLE_PROFILE, role, level, _base)
    return _role_style, _base, fl_styles


@xr.secondary_run_scope.with_secondary_run
@xr.fx_iol.family_x_in_one_line_scope()
def generate_y_b1_segments(theme_out_dir: str) -> dict:
    xr.style_profile_mod.assert_profile_backend(STYLE_PROFILE, TTS_BACKEND)
    n3_tts, voice01, news_tail_fix = xr.n3_tts, xr.voice01, xr.news_tail_fix
    cl, retry_primitive, vi, sp = xr.cl, xr.retry_primitive, xr.validation_inheritance, xr.style_profile_mod
    _role_style, _base, _fl = _role_style_fn("b1b")
    out_dir = f"{theme_out_dir}/b1b"
    narration_dir = f"{out_dir}/narration"
    os.makedirs(narration_dir, exist_ok=True)
    parts = load_json(f"{out_dir}/parts.json")
    support = load_json(f"{out_dir}/b1_support_texts.json")
    kp_path = f"{out_dir}/key_phrases/keywords_canonicalized.json"
    kp = load_json(kp_path) if os.path.exists(kp_path) else None
    shared_raw = xr.shared_narration.ensure_all_shared_narration_b1(narration_dir, tts_backend=TTS_BACKEND)
    shared_status = xr._summarize_shared_narration(shared_raw)
    cached = voice_guard_cached(xr._load_cached_tts_results(out_dir))
    results = {}

    topic_text = f"Today's topic is {parts['title']}."
    with cl.segment_context("topic_intro"):
        results["topic_intro"] = xr._generate_or_reuse(
            cached, "topic_intro", f"{narration_dir}/topic_intro.wav", lambda: voice01.generate_charon_english(
                xr._pnap_supply(topic_text, n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(topic_text))),
                f"{narration_dir}/topic_intro.wav",
                enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for("topic_intro"),
                enable_pronunciation_resolver=True, style_prefix_override=_role_style("TOPIC_INTRO"),
                tts_backend=TTS_BACKEND), expected_text=topic_text)
    results["topic_intro"]["canonical_text"] = topic_text

    for name in ("preview", "comment_1", "comment_2", "comment_3"):      # Comment 4は廃止
        text = support[name]
        with cl.segment_context(name):
            results[name] = xr._generate_or_reuse(
                cached, name, f"{narration_dir}/{name}.wav", lambda text=text, name=name: voice01.generate_charon_english(
                    xr._pnap_supply(text, n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(text))), f"{narration_dir}/{name}.wav",
                    style_prefix_override=(_role_style("PREVIEW" if name == "preview" else "COMMENT") or n3_tts.B1_PREVIEW_STYLE_PREFIX_CALM),
                    disfluency_qa=True,
                    enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(name),
                    enable_pronunciation_resolver=True, tts_backend=TTS_BACKEND), expected_text=text)
        results[name]["canonical_text"] = text
        if name == "preview" and not vi.is_untouched_entry(results[name]):
            sp.attach_segment_profile_record(results[name], STYLE_PROFILE, sp.ROLE_PREVIEW, _role_style("PREVIEW"))

    body = [(f"part{i}", s) for i, s in enumerate(Y_BODY_IDS, start=1)] + [("in_one_line", "in_one_line")]
    for key, name in body:
        text = parts[key]
        voice = Y_VOICE_OF.get(name, "Aoede")
        role = "IN_ONE_LINE" if name == "in_one_line" else "FULL_STORY"
        with cl.segment_context(name):
            def _gen(text=text, name=name, voice=voice, role=role):
                with tts_voice(voice):
                    return news_tail_fix.generate_news_narration_wide_margin(
                        xr._pnap_supply(text, n3_tts.tts_safe_news_en(text)), f"{narration_dir}/{name}.wav",
                        disfluency_qa=(name == "in_one_line"),
                        enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(name),
                        enable_repetition_qa=(name in Y_BODY_IDS), enable_pronunciation_resolver=True,
                        style_prefix_override=_role_style(role), tts_backend=TTS_BACKEND)
            results[name] = xr._generate_or_reuse(cached, name, f"{narration_dir}/{name}.wav", _gen, expected_text=text)
        results[name]["canonical_text"] = text
        results[name]["y_tts_voice_requested"] = voice
        results[name]["y_role"] = Y_ROLE_OF.get(name, "in_one_line")
        if not vi.is_untouched_entry(results[name]):
            sp.attach_segment_profile_record(results[name], STYLE_PROFILE, role, _role_style(role))

    if kp is not None:
        kp_results, kp_bundle = xr._generate_key_phrase_segments_b1(kp, narration_dir, cached, tts_backend=TTS_BACKEND,
                                                                    style_profile=STYLE_PROFILE)
    else:
        kp_results, kp_bundle = {}, None
    kp_status_str = "OK" if kp is not None else "KP_SCAFFOLD_JSON_MISSING"
    return _finish_results(out_dir, results, kp_results, kp_bundle, shared_status, kp_status_str, level="b1b")


# ============================================================
# TTS: Standard(a2)
# ============================================================
@xr.secondary_run_scope.with_secondary_run
@xr.fx_iol.family_x_in_one_line_scope()
def generate_y_a2_segments(theme_out_dir: str, japanese_title: str) -> dict:
    xr.style_profile_mod.assert_profile_backend(STYLE_PROFILE, TTS_BACKEND)
    n3_tts, crosslevel_common = xr.n3_tts, xr.crosslevel_common
    cl, retry_primitive, vi, sp = xr.cl, xr.retry_primitive, xr.validation_inheritance, xr.style_profile_mod
    _role_style, _base, fl_styles = _role_style_fn("a2")

    def _base_slower(role: str):
        base = _base(role)
        if base is None:
            return None
        combined = f"{base}\n{n3_tts.A2_SLOWER_PACE_INSTRUCTION.strip()}"
        import er002_common as common
        common.assert_no_wpm_specification(combined)
        return combined

    def _role_style_slower(role: str):
        return sp.resolve_role_style(STYLE_PROFILE, role, "a2", _base_slower)

    def _role_style_ja():
        return fl_styles.FAMILY_X_ROLE_STYLE_JA

    def _role_style_ja_support():
        return sp.resolve_role_style(STYLE_PROFILE, sp.ROLE_SUPPORT_JA, "a2", lambda _r: _role_style_ja())

    out_dir = f"{theme_out_dir}/a2"
    narration_dir = f"{out_dir}/narration"
    os.makedirs(narration_dir, exist_ok=True)
    parts = load_json(f"{out_dir}/parts.json")
    support = load_json(f"{out_dir}/a2_support_texts.json")
    kp_path = f"{out_dir}/key_phrases/keywords_canonicalized.json"
    kp = load_json(kp_path) if os.path.exists(kp_path) else None
    shared_raw = xr.shared_narration.ensure_all_shared_narration_a2(narration_dir, tts_backend=TTS_BACKEND)
    shared_status = xr._summarize_shared_narration(shared_raw)
    cached = voice_guard_cached(xr._load_cached_tts_results(out_dir))
    results = {}

    topic_text = f"Today's topic is {parts['title']}."
    with cl.segment_context("topic_intro"):
        results["topic_intro"] = xr._generate_or_reuse(
            cached, "topic_intro", f"{narration_dir}/topic_intro.wav",
            lambda: crosslevel_common.generate_english_segment_with_fallback(
                xr._pnap_supply(topic_text, n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(topic_text))),
                f"{narration_dir}/topic_intro.wav", n3_tts.first_words(parts["title"], 3), max_extra_chars=30,
                style_prefix_override=_role_style("TOPIC_INTRO"),
                enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for("topic_intro"),
                tts_backend=TTS_BACKEND), expected_text=topic_text)
    results["topic_intro"]["canonical_text"] = topic_text

    with cl.segment_context("japanese_title"):
        results["japanese_title"] = xr._generate_or_reuse(
            cached, "japanese_title", f"{narration_dir}/japanese_title.wav",
            lambda: n3_tts.generate_a2_japanese_with_reading_safety(
                japanese_title, f"{narration_dir}/japanese_title.wav", n3_tts.expected_substring_ja(japanese_title),
                max_extra_chars=30, style_prefix_override=_role_style_ja(), tts_backend=TTS_BACKEND),
            expected_text=japanese_title)

    for name in ("preview", "comment_1", "comment_2", "comment_3"):      # Comment 4は廃止
        text = support[name]
        with cl.segment_context(name):
            results[name] = xr._generate_or_reuse(
                cached, name, f"{narration_dir}/{name}.wav",
                lambda text=text, name=name: n3_tts.generate_a2_japanese_with_reading_safety(
                    text, f"{narration_dir}/{name}.wav", n3_tts.expected_substring_ja(text),
                    style_prefix_override=_role_style_ja_support(), tts_backend=TTS_BACKEND), expected_text=text)
        if not vi.is_untouched_entry(results[name]):
            sp.attach_segment_profile_record(results[name], STYLE_PROFILE, sp.ROLE_SUPPORT_JA, _role_style_ja_support())

    body = [(f"part{i}", s) for i, s in enumerate(Y_BODY_IDS, start=1)] + [("in_one_line", "in_one_line")]
    for key, name in body:
        text = parts[key]
        voice = Y_VOICE_OF.get(name, "Aoede")
        role = "IN_ONE_LINE" if name == "in_one_line" else "FULL_STORY"
        tts_input = xr._pnap_supply(text, n3_tts.tts_safe_news_en(text))
        sub = n3_tts.first_words(text)
        with cl.segment_context(name):
            def _gen(tts_input=tts_input, sub=sub, name=name, voice=voice, role=role):
                with tts_voice(voice):
                    return n3_tts.generate_a2_segment_with_slowdown(
                        tts_input, f"{narration_dir}/{name}.wav", sub,
                        style_prefix_override=(_role_style_slower(role) or n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER),
                        disfluency_qa=(name == "in_one_line"),
                        enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(name),
                        enable_repetition_qa=(name in Y_BODY_IDS), tts_backend=TTS_BACKEND)
            results[name] = xr._generate_or_reuse(cached, name, f"{narration_dir}/{name}.wav", _gen, expected_text=text)
        results[name]["canonical_text"] = text
        results[name]["y_tts_voice_requested"] = voice
        results[name]["y_role"] = Y_ROLE_OF.get(name, "in_one_line")
        if not vi.is_untouched_entry(results[name]):
            sp.attach_segment_profile_record(results[name], STYLE_PROFILE, role, _role_style_slower(role))

    kp_results = xr._generate_key_phrase_segments_a2(kp, narration_dir, cached, tts_backend=TTS_BACKEND,
                                                     style_profile=STYLE_PROFILE) if kp is not None else {}
    kp_status_str = "OK" if kp is not None else "KP_SCAFFOLD_JSON_MISSING"
    return _finish_results(out_dir, results, kp_results, None, shared_status, kp_status_str, level="a2")


def _finish_results(out_dir, results, kp_results, kp_bundle, shared_status, kp_status_str, level):
    review_lock = xr.review_lock
    all_status = {k: v.get("status") for k, v in results.items()}
    if level == "b1b":
        kp_status = {r: {"en": v["english"].get("status"), "explanation": v["explanation"].get("status")} for r, v in kp_results.items()}
    else:
        kp_status = {r: {"en": v["english"].get("status"), "ja": v["japanese_meaning"].get("status")} for r, v in kp_results.items()}
    review_lock.archive_prior_tts_results(f"{out_dir}/audit/tts_generation_results.json")
    doc = {"segments": results, "key_phrases": kp_results, "shared_narration": shared_status, "kp_scaffold_status": kp_status_str,
           "tts_backend": TTS_BACKEND, "style_version": xr.FAMILY_X_VARIABLE_ROLE_STYLE_VERSION}
    if level == "b1b":
        doc["key_phrase_explanations_text"] = kp_bundle
    save_json(f"{out_dir}/audit/tts_generation_results.json", doc)
    xr.pww_registry.write_listening_list_safe(out_dir)
    summary = {"segment_status": all_status, "key_phrase_status": kp_status,
               "shared_narration_status": {k: v["status"] for k, v in shared_status.items()},
               "kp_scaffold_status": kp_status_str, "tts_backend": TTS_BACKEND}
    save_json(f"{out_dir}/run_summary_tts.json", summary)
    xr._assert_shared_narration_ok(shared_status, level)
    return summary


# ============================================================
# Assemble
# ============================================================
def _read(narration_dir, name):
    mono, sr, _, _ = xr.common.read_wav_float(f"{narration_dir}/{name}.wav")
    assert sr == xr.common.SAMPLE_RATE
    return mono


def load_y_b1_sources(theme: str, source_dir: str) -> dict:
    out_dir = f"{theme}/b1b"
    nd = f"{out_dir}/narration"
    p9a = xr.p9a
    article_text = load_text(f"{source_dir}/b1b/article.md")
    xr.asm.verify_episode_audio_validation_gate(out_dir, "B1", article_text=article_text)
    narration = {n: _read(nd, f"{n}_charon") for n in ("welcome", "preview_intro", "key_phrases_intro", "full_story_intro",
                                                         "num_one", "num_two", "num_three", "num_four", "num_five")}
    narration["topic_intro"] = _read(nd, "topic_intro")
    segs = {n: _read(nd, n) for n in (*Y_BODY_IDS, "comment_1", "comment_2", "comment_3", "preview", "in_one_line")}
    kp = load_json(f"{out_dir}/key_phrases/keywords_canonicalized.json")
    items = sorted(kp["items"], key=lambda it: it["rank"])
    comp = {it["rank"]: _read(nd, f"kp{it['rank']}_en") for it in items}
    mean = {it["rank"]: _read(nd, f"kp{it['rank']}_explanation_en") for it in items}
    return {"intro": p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH), "notification": p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH),
            "outro": p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH), "narration": narration, "b1_segments": segs,
            "key_phrase_components": comp, "key_phrase_meanings": mean, "kp_items": items}


def load_y_a2_sources(theme: str, source_dir: str, voice_noslow: bool = False) -> dict:
    out_dir = f"{theme}/a2"
    nd = f"{out_dir}/narration"
    p9a = xr.p9a
    article_text = load_text(f"{source_dir}/a2/article.md")
    xr.asm.verify_episode_audio_validation_gate(out_dir, "A2", article_text=article_text)
    preview_mono = _read(nd, "preview")
    narration = {n: _read(nd, n) for n in ("welcome", "preview_intro", "key_phrases_intro", "full_story_intro",
                                             "num_one", "num_two", "num_three", "num_four", "num_five", "topic_intro", "japanese_title")}
    kp = load_json(f"{out_dir}/key_phrases/keywords_canonicalized.json")
    items = sorted(kp["items"], key=lambda it: it["rank"])
    comp = {}
    for i, it in enumerate(items, start=1):
        comp[it["rank"]] = _read(nd, f"kp{it['rank']}_en")
        narration[f"meaning_{i}"] = _read(nd, f"meaning_{i}")
    segs = {}
    for n in (*Y_BODY_IDS, "comment_1", "comment_2", "comment_3", "in_one_line"):
        read_name = f"{n}_original" if (voice_noslow and n in VOICE_SEGMENT_IDS) else n
        segs[n] = _read(nd, read_name)
    return {"intro": p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH), "notification": p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH),
            "outro": p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH), "preview_mono": preview_mono, "narration": narration,
            "key_phrase_components": comp, "a2_segments": segs, "kp_items": items}


def _body_seq(seg: dict, comment_to_story_gap: float, story_to_comment_gap: float) -> list:
    p9a = xr.p9a
    S = p9a.silence_stereo
    gap = SPEAKER_GAP_SECONDS
    return [
        ("Comment 1", seg["comment_1"]), ("pause_comment_to_story", S(comment_to_story_gap)),
        ("Full Story: Lead (Aoede)", seg["full_story_part1"]), ("pause_story_to_comment", S(story_to_comment_gap)),
        ("Comment 2", seg["comment_2"]), ("pause_comment_to_story", S(comment_to_story_gap)),
        ("Full Story: Voice 1 (Algieba)", seg["full_story_part2"]), ("pause_voice_gap", S(gap)),
        ("Full Story: Voice 2 (Zephyr)", seg["full_story_part3"]), ("pause_voice_gap", S(gap)),
        ("Full Story: Voice 3 (Schedar)", seg["full_story_part3_c2"]), ("pause_story_to_comment", S(story_to_comment_gap)),
        ("Comment 3", seg["comment_3"]), ("pause_comment_to_story", S(comment_to_story_gap)),
        ("Full Story: Closing (Aoede)", seg["full_story_part3_c3"]), ("pause_closing_to_in_one_line", S(gap)),
    ]


def build_y_b1_timeline(parts: dict) -> list:
    p9a, asm = xr.p9a, xr.asm
    S = p9a.silence_stereo
    blocks = asm.build_b1_key_phrase_blocks(parts)
    b1 = parts["b1_segments"]
    seq = [("Intro", parts["intro"]), ("Welcome (Charon)", parts["welcome"]), ("pause_0.5", S(0.5)),
           ("Topic intro (Charon)", parts["topic_intro"]), ("pause_0.65", S(0.65)), ("Notification 1", parts["notification"]),
           ("pause_0.4", S(0.4)), ("Preview intro (Charon)", parts["preview_intro"]), ("pause_0.65", S(0.65)),
           ("Preview (Charon)", b1["preview"]), ("pause_0.5", S(0.5)), ("Notification 2", parts["notification"]),
           ("pause_0.4", S(0.4)), ("Key phrases intro (Charon)", parts["key_phrases_intro"]), ("pause_0.5", S(0.5))]
    for i, block in enumerate(blocks, start=1):
        seq.append((f"Key Phrase {i}", block))
    seq += [("Notification 3", parts["notification"]), ("pause_0.4", S(0.4)), ("Full story intro (Charon)", parts["full_story_intro"]),
            ("pause_1.0", S(asm.AOEDE_TO_CHARON_PAUSE_SECONDS))]
    seq += _body_seq(b1, asm.CHARON_TO_AOEDE_PAUSE_SECONDS, asm.AOEDE_TO_CHARON_PAUSE_SECONDS)
    seq += [("In One Line (Aoede)", b1["in_one_line"]), ("pause_0.8_in_one_line_to_outro", S(asm.IN_ONE_LINE_TO_OUTRO_PAUSE_SECONDS)),
            ("Outro (Charon)", parts["outro"])]
    return seq


def build_y_a2_timeline(parts: dict) -> list:
    p9a, asm = xr.p9a, xr.asm
    S = p9a.silence_stereo
    blocks = asm.build_a2_key_phrase_blocks(parts)
    a2 = parts["a2_segments"]
    seq = [("Intro", parts["intro"]), ("Welcome", parts["welcome"]), ("pause_0.5", S(0.5)), ("Topic intro", parts["topic_intro"]),
           ("pause_0.65", S(0.65)), ("Japanese title", parts["japanese_title"]), ("pause_0.5", S(0.5)),
           ("Notification 1", parts["notification"]), ("pause_0.4", S(0.4)), ("Preview intro", parts["preview_intro"]),
           ("pause_0.65", S(0.65)), ("Preview", parts["preview"]), ("pause_0.5", S(0.5)), ("Notification 2", parts["notification"]),
           ("pause_0.4", S(0.4)), ("Key phrases intro", parts["key_phrases_intro"]), ("pause_0.5", S(0.5))]
    for i, block in enumerate(blocks, start=1):
        seq.append((f"Key Phrase {i}", block))
    seq += [("Notification 3", parts["notification"]), ("pause_0.4", S(0.4)), ("Full story intro", parts["full_story_intro"]),
            ("pause_1.0_en_to_ja", S(1.0))]
    seq += _body_seq(a2, 0.8, 1.0)
    seq += [("In One Line", a2["in_one_line"]), ("pause_0.5", S(0.5)), ("Outro", parts["outro"])]
    return seq


def y_style_gate(theme: str, level: str) -> dict:
    """XのM3 Assembly前Gateを継承しつつ、Y本文5segment(alias ID含む)にも同じ判定を掛ける。
    X側のROLE_SEGMENTS固定(part1〜3/comment_4)に起因する『Yに存在しないsegment』の欠落のみ除外し、それ以外は一切緩和しない。"""
    sp = xr.style_profile_mod
    out_dir = f"{theme}/{level}"
    results = load_json(f"{out_dir}/audit/tts_generation_results.json")
    approvals_path = xr.asm.human_approval_path(out_dir)
    approvals = load_json(approvals_path) if os.path.exists(approvals_path) else {}
    gate = sp.m3_assembly_gate(STYLE_PROFILE, level, results, approvals)
    blocked = [b for b in gate["blocked"] if not (b["segment"] == "comment_4" and b["violations"] == ["NO_SEGMENT_RECORD"])]
    extra = []
    segs = results.get("segments") or {}
    exp_text = sp.get_profile(STYLE_PROFILE)["overrides"]["FULL_STORY"]["text"]
    for name in Y_BODY_IDS:
        entry = segs.get(name)
        viol = []
        if entry is None:
            viol.append("NO_SEGMENT_RECORD")
        else:
            ev = sp.evaluate_segment_evidence(entry, level, STYLE_PROFILE, "FULL_STORY")
            viol.extend(ev["reasons"])
            if level == "b1b":
                spx = entry.get("style_prefix")
                if not (isinstance(spx, str) and spx.startswith(exp_text)):
                    viol.append("ADV_STYLE_PREFIX_NOT_PROFILE_PREFIXED")
                if entry.get("instruction_type") == "minimal_fallback":
                    viol.append("ADV_MINIMAL_FALLBACK")
            elif entry.get("fallback_used") is not False:
                viol.append("STD_FALLBACK_USED_OR_UNKNOWN")
            if entry.get("local_rewrite_recovery"):
                viol.append("LOCAL_REWRITE_RECOVERY")
        extra.append({"segment": name, "violations": viol})
    extra_blocked = [e for e in extra if e["violations"] and name_not_approved(approvals, e["segment"], segs.get(e["segment"]))]
    if level == "a2":   # Std減速の必須適用をY本文5segment全てで確認(X共有検査はpart1/2/in_one_lineのみ対象のため、Yが追加で確認)
        for name in Y_BODY_IDS + ("in_one_line",):
            e = segs.get(name) or {}
            if e.get("slowdown_applied") is not True:
                extra_blocked.append({"segment": name, "violations": ["Y_MISSING_MANDATORY_A2_SLOWDOWN"]})
    res = {"status": "BLOCK" if (blocked or extra_blocked) else "PASS", "x_gate_blocked_after_filter": blocked,
           "y_body_checks": extra, "y_body_blocked": extra_blocked, "x_gate": {k: gate[k] for k in ("status", "checked", "human_approved", "warnings")}}
    save_json(f"{out_dir}/audit/y_style_profile_gate.json", res)
    return res


def name_not_approved(approvals, name, entry) -> bool:
    return not (entry is not None and xr.style_profile_mod._approved(approvals, name, entry))


def assemble_level(theme: str, level: str, source_dir: str, voice_noslow: bool = False) -> dict:
    asm, p9a, common = xr.asm, xr.p9a, xr.common
    out_dir = f"{theme}/{level}"
    sub = "assembled_voice_noslow" if voice_noslow else "assembled"
    os.makedirs(f"{out_dir}/{sub}", exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    tag = "voice_noslow_" if voice_noslow else ""
    if not os.path.exists(f"{out_dir}/key_phrases/keywords_canonicalized.json"):
        raise YAudioStop(f"{level}: keywords_canonicalized.jsonがありません")
    xr._assert_no_gloss_alignment_hr(out_dir, "B1" if level == "b1b" else "A2")
    shared_blocked = xr._shared_narration_gate_blocked_summary(out_dir)
    if shared_blocked is not None:
        save_json(f"{out_dir}/run_summary_assemble.json", shared_blocked)
        return shared_blocked
    if not voice_noslow:
        gate = y_style_gate(theme, level)
        if gate["status"] != "PASS":
            summary = {"status": "BLOCKED_STYLE_PROFILE_GATE", "gate": gate}
            save_json(f"{out_dir}/run_summary_assemble.json", summary)
            return summary
    if level == "b1b":
        sources = load_y_b1_sources(theme, source_dir)
        parts = xr.apply_family_x_b1_gain(sources)
        seq = build_y_b1_timeline(parts)
    else:
        sources = load_y_a2_sources(theme, source_dir, voice_noslow=voice_noslow)
        parts = xr.apply_family_x_a2_gain(sources)
        seq = build_y_a2_timeline(parts)
    result = asm.assemble_with_timeline(seq)
    headroom = asm.apply_headroom_safety_valve(result["assembled"], seq)
    assembled = headroom["assembled"]
    out_path = f"{out_dir}/{sub}/Family_Y_Trial_{'B1' if level == 'b1b' else 'A2'}_{os.path.basename(theme).upper()}{'_VOICE_NOSLOW' if voice_noslow else ''}.wav"
    save_json(f"{out_dir}/audit/{tag}gain_report.json", parts["gain_report"])
    save_json(f"{out_dir}/audit/{tag}timeline.json", result["timeline"])
    save_json(f"{out_dir}/audit/{tag}headroom_report.json", headroom["report"])
    common.write_wav_float(out_path, assembled, xr.SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], xr.SR)
    summary = {"status": "OK", "out_path": out_path, "duration_seconds": result["total_duration_seconds"],
               "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
               "sample_rate": xr.SR, "channels": 2, "headroom_safety_valve": headroom["report"], "voice_noslow_variant": voice_noslow}
    if not voice_noslow:
        xr._attach_kp_vote_audit(summary, out_dir, level)
    save_json(f"{out_dir}/run_summary_assemble{'_voice_noslow' if voice_noslow else ''}.json", summary)
    return summary


# ============================================================
# CLI
# ============================================================
def main() -> None:
    ap = argparse.ArgumentParser(description="Family Y Trial Phase 3 音声段(DEV/Trial専用)")
    ap.add_argument("--cand", required=True, choices=sorted(CANDIDATES))
    ap.add_argument("--stage", required=True, choices=["prep", "tts", "assemble", "all"])
    ap.add_argument("--level", default="both", choices=["a2", "b1b", "both"])
    ap.add_argument("--budget-jpy", type=float, default=60.0, help="この候補のTTS/ASR費用上限(raw_usage_log累計)。超過見込みで停止")
    a = ap.parse_args()
    theme = theme_dir(a.cand)
    levels = ["b1b", "a2"] if a.level == "both" else [a.level]
    source_dir = f"{SRC}/english_{a.cand}"
    if a.stage in ("prep", "all"):
        info = prepare(a.cand)
        print(f"[Y-AUDIO] prep done: {json.dumps(info, ensure_ascii=False)[:400]}")
        if a.stage == "prep":
            return
    store_info = use_trial_master_store(f"{OUT_ROOT}/master_store_trial_{a.cand}")
    save_json(f"{theme}/trial_store_info.json", store_info)
    xr.cl.install(f"{theme}/raw_usage_log.jsonl")
    try:
        if a.stage in ("tts", "all"):
            import er003_v1_en_direct_vfl_01_generate as vfl01
            vfl01.get_client()
            xr.assert_production_tts_backend(TTS_BACKEND, False)
            ja_title = load_json(f"{theme}/japanese_title.json")["japanese_title"]
            with xr.cl.logging_context(f"family_y_{a.cand}", "tts"):
                for level in levels:
                    if level == "b1b":
                        generate_y_b1_segments(theme)
                    else:
                        generate_y_a2_segments(theme, ja_title)
                    xr.assert_budget_ok(theme, a.budget_jpy, f"after y tts {level}")
        if a.stage in ("assemble", "all"):
            for level in levels:
                s = assemble_level(theme, level, source_dir)
                print(f"[Y-AUDIO] assemble {level}: {s.get('status')} {s.get('duration_seconds')}")
            if "a2" in levels:
                s = assemble_level(theme, "a2", source_dir, voice_noslow=True)
                print(f"[Y-AUDIO] assemble a2 voice_noslow: {s.get('status')} {s.get('duration_seconds')}")
    finally:
        pass
    jpy, by = xr.compute_cost_jpy_so_far(f"{theme}/raw_usage_log.jsonl")
    print(f"[Y-AUDIO] cand={a.cand} stage={a.stage} 累計費用(JPY)={jpy:.2f} by_provider={by}")


if __name__ == "__main__":
    main()
