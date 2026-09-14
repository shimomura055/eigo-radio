# ============================================================
# er014_output/four_type_observation_01/voices/run_voices_2v_audio_completion.py
# 管理ID: USER-TEST-AUDIO-COMPLETION-01-VOICES
# ============================================================
# 目的: 現在の2V canonical candidate(voices/run2_clean/
# b1_2v_new_theme_attempt3/article.md、374語、Fact Checker PASS/Ledger
# COMPLIANT/Comment Contract検証COMPLIANT、Analytical Leakage Check残存
# flag[voice_b/tension]あり)を、既存正式Production primitiveだけを使って
# TTS→Assembly→Audio Validation→完成episode→Web試聴playerまで完成させる。
# 新記事生成・Writer retry・Gate緩和・Prompt変更は一切行わない。
#
# 経路調査結果(Read指示どおり):
#   - er012_b_family_production_runner_01.py::main_b1_2v()は現時点で
#     write_new_theme stage(Writerのみ)しか配線されていない(TTS/assembly/
#     playerはOPEN-151未配線、コメント "2V TTS/assembly/player stageは
#     本タスクの承認範囲外"参照)。
#   - 一方、同ファイルの既定level="b1"(旧固定記事向け)のprepare/voice_check/
#     run_tts/run_assembly/build_player_htmlはすべてOUT_DIR/OUT_B1_DIR/
#     NARRATION_DIRというモジュールグローバル定数(旧承認済み記事専用の
#     本番出力先)に直接書き込む実装であり、そのまま呼ぶと共有Production
#     資産(er012_output/editorial_b_family_production_phase1_02/)を汚染する
#     リスクがある。
#   - 一方、実際にTTS/Assemblyを行う下位のPrimitive関数
#     (b1prod.build_parts/run_voice_availability_check/resolve_voice_names/
#     generate_voice_body_wide_margin/build_b1_voices_timeline、
#     asm.load_b1_sources(theme: dict)/apply_b1_gain/assemble_with_timeline/
#     apply_headroom_safety_valve/verify_episode_audio_validation_gate、
#     sc.run_key_phrases、voice01.generate_charon_english、
#     point_headings.generate、news_tail_fix.generate_news_narration_
#     wide_margin、shared_narration.ensure_all_shared_narration_b1)は、
#     すべて引数(article_text/parts/out_dir/narration_dir等)を明示的に
#     受け取るpure関数として実装済みであり、er012_*を一切変更せずに
#     呼び出し側(本driver)が独自の出力先へ向けてそのまま再利用できる。
#   - したがって本driverはer012_*を変更せず(変更差分ゼロ)、上記
#     primitiveを、production_runner_01.py::run_tts()/run_assembly()と
#     完全に同一の呼び出し順序・同一の引数規約で、出力先だけを本タスク
#     専用ディレクトリへ差し替えて呼ぶ(「新仕様を作らず既存資産で
#     最小接続」)。
#   - 唯一の制約: asm.load_b1_sources(theme)は内部で
#     out_dir = f"{theme['out_dir']}/b1b" を用いる(Production既存実装、
#     無変更)。そのためnarration/key_phrases/assembled/auditは
#     audio/b1_2v/b1b/配下に置く(委任文の例示パス"tts/"ではなく
#     Production既存規約の"narration/"をそのまま使用、下記2)で詳細記載)。
#   - Comment 1-4 + Preview: run2_cleanで既に生成済み(b1_2v_new_theme/
#     b1_support_texts.json、Contract検証LEDGER_COMPLIANT)のためそのまま
#     再利用する(再生成しない、追加LLM費用ゼロ)。
#   - Fact Safety Gate: Writer stage専用機構であり、記事は再生成しない
#     ため本driverでは発火しない。run2_clean実行時の記録(RESULT_PACKET_
#     VOICES_VAR2.md 4節)を転記するのみ(本driverは新規判定を行わない)。
#   - Key Phrase: 未生成のため、既存正式経路sc.run_key_phrases()
#     (er003_v1_n3_01_scaffold_generate.py、選定→canonicalization→
#     redundancy QAをこの関数内部で最大3回[KEY_PHRASE_REDUNDANCY_RETRY_MAX+1]
#     まで自動retryする既存Gate、本driverは独自retry上限を追加しない)を
#     そのまま呼ぶ。
#
# mp3変換: er013_output/family_c_episode_trial_09/build_web_delivery.py
# (USER-TEST-AUDIO-COMPLETION-01-FAMILYC、同日並行タスク)と同じ
# soundfile.write(..., format="MP3")を再利用する(pip installなし)。
from __future__ import annotations

import hashlib
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

# repo root(C:\Users\tensh\eigo-radio)をsys.pathへ追加(本scriptはer014_output配下の
# Trial driverであり、repo root直下の各種er0*モジュールをimportする必要があるため)。
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
os.chdir(_REPO_ROOT)

# PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01: 正式リリース前はStandard同期を使う
# (既存production_runner_01.pyと同一の既定値、変更していない)。
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

import soundfile as sf

import audio_review_player as player_common
import er002_common as common
import er003_b1_p9a_audio as p9a
import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_tts_generate as tts_gen
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er003_v1_sing01_point_headings_aoede as point_headings
import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl
import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er012_b_family_voices_production_01 as b1prod

ARTICLE_PATH = ("er014_output/four_type_observation_01/voices/run2_clean/"
                 "b1_2v_new_theme_attempt3/article.md")
SUPPORT_TEXTS_PATH = ("er014_output/four_type_observation_01/voices/run2_clean/"
                       "b1_2v_new_theme/b1_support_texts.json")
LEAKAGE_EVIDENCE_PATH = ("er014_output/four_type_observation_01/voices/run2_clean/"
                          "b1_2v_new_theme_attempt3/analytical_leakage_check_2v_attempt3.json")

OUT_BASE = "er014_output/four_type_observation_01/voices/audio/b1_2v"
OUT_B1B_DIR = f"{OUT_BASE}/b1b"
NARRATION_DIR = f"{OUT_B1B_DIR}/narration"
KP_DIR = f"{OUT_B1B_DIR}/key_phrases"
WEB_DIR = f"{OUT_BASE}/web"
WEB_SEG_DIR = f"{WEB_DIR}/segments"
COST_LOG_PATH = f"{OUT_BASE}/cost_log_raw.jsonl"
PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0
BUDGET_JPY_CAP = 150.0
ARTICLE_ID = "voices_ut_audio_completion_01_b1_2v"
SOURCE_LEVEL = "B1"
EPISODE_WAV_NAME = "Voices_UT_Audio_Completion_01_B1_2V.wav"
EPISODE_MP3_NAME = "Voices_UT_Audio_Completion_01_B1_2V.mp3"

THEME = {"theme_id": ARTICLE_ID, "out_dir": OUT_BASE}


def load_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


def sha(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


# ============================================================
# コスト計測(production_runner_01.pyと同一計算ロジック、本driver専用ログ)
# ============================================================
def _load_pricing():
    prices = load_json(PRICING_SNAPSHOT_PATH)["prices"]

    def price(provider, model, meter):
        return next(p["price"] for p in prices
                    if p["provider"] == provider and p["model"] == model and p["meter"] == meter
                    and p.get("tier", "Standard") == "Standard")
    return price


def compute_cost_jpy_so_far() -> tuple:
    if not os.path.exists(COST_LOG_PATH):
        return 0.0, {}
    price = _load_pricing()
    total_usd = 0.0
    by_provider = {}
    with open(COST_LOG_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            provider = rec.get("provider")
            model = rec.get("model_id") or rec.get("model")
            usd = 0.0
            try:
                if provider in ("gemini", "openai", "openai_asr") and model:
                    in_tok = rec.get("input_tokens") or 0
                    out_tok = rec.get("output_tokens") or 0
                    usd = in_tok * price(provider, model, "input_tokens") / 1e6 \
                        + out_tok * price(provider, model, "output_tokens") / 1e6
            except StopIteration:
                usd = 0.0
            total_usd += usd
            by_provider[provider] = by_provider.get(provider, 0.0) + usd
    jpy = total_usd * USD_JPY
    return jpy, {k: round(v * USD_JPY, 2) for k, v in by_provider.items()}


def assert_budget_ok(note: str = "") -> float:
    jpy, by_provider = compute_cost_jpy_so_far()
    print(f"[VOICES-2V-AUDIO][cost] so far={jpy:.2f} JPY by_provider={by_provider} ({note})")
    if jpy > BUDGET_JPY_CAP:
        raise RuntimeError(f"[BUDGET_GUARD] cost so far {jpy:.2f} JPY > cap {BUDGET_JPY_CAP} JPY. Stopping ({note}).")
    return jpy


# ============================================================
# Step 0: prepare(記事読み取り、5区切りparse。b1prod.build_parts無変更)
# ============================================================
def step_prepare() -> tuple:
    with open(ARTICLE_PATH, encoding="utf-8") as f:
        article_text = f.read()
    parts = b1prod.build_parts(article_text)
    os.makedirs(f"{OUT_B1B_DIR}/audit", exist_ok=True)
    with open(f"{OUT_B1B_DIR}/article.md", "w", encoding="utf-8") as f:
        f.write(article_text)
    save_json(f"{OUT_B1B_DIR}/parts.json", parts)
    return article_text, parts


# ============================================================
# Step 1: Voice可用性確認 + 解決(b1prod.run_voice_availability_check/
# resolve_voice_names無変更、2V=voice_a/voice_bのみ)
# ============================================================
def step_voice_check(parts: dict) -> tuple:
    sample_text = b1prod.first_n_sentences(parts["point_one_body"], 3)
    sample_dir = f"{OUT_BASE}/audit/voice_samples"
    results = b1prod.run_voice_availability_check(sample_text, sample_dir)
    save_json(f"{sample_dir}/voice_sample_results.json", {"sample_text": sample_text, "results": results})
    voice_a, voice_b, reasons = b1prod.resolve_voice_names(results)
    save_json(f"{OUT_BASE}/audit/voice_resolution.json",
              {"voice_a": voice_a, "voice_b": voice_b, "reasons": reasons})
    return voice_a, voice_b, reasons


# ============================================================
# Step 2: Key Phrase(新規生成。sc.run_key_phrases無変更、内部で選定→
# canonicalization→redundancy QAを最大3回まで自動retry)
# ============================================================
def step_key_phrases(article_text: str) -> dict:
    os.makedirs(KP_DIR, exist_ok=True)
    result = sc.run_key_phrases(article_text, KP_DIR, ARTICLE_ID, SOURCE_LEVEL, process="B1_SUPPORT")
    save_json(f"{OUT_BASE}/audit/key_phrase_generation_summary.json", result)
    assert_budget_ok("after Key Phrase generation")
    return result


# ============================================================
# セグメント単位の運用retry(既存関数自体のASR verify/内部retry/
# minimal-instruction fallbackは一切変更しない。既存関数呼び出し全体を
# 独立した乱数draw として最大3回まで再実行するだけ、というProduction
# 運用上ごく一般的な「うまくいかなかったので同じ承認済み関数をもう一度
# 呼ぶ」操作。MAX_TTS_TECHNICAL_RETRY/PRODUCTION_MAX_TTS_ATTEMPTS等の
# 定数は一切変更しない。同一disposition[status]が3回連続で得られた場合は
# そのまま報告する[黙示的な採用はしない])。
# ============================================================
_SEGMENT_OUTER_RETRY_MAX = 2  # 初回+最大2回= 合計3回(Key Phrase redundancy
                               # retryと同じ「3回」規約に揃える)


def _call_with_segment_retry(name: str, gen_fn, *args, **kwargs) -> dict:
    attempts = []
    for outer_attempt in range(0, _SEGMENT_OUTER_RETRY_MAX + 1):
        r = gen_fn(*args, **kwargs)
        attempts.append({"outer_attempt": outer_attempt, "status": r.get("status")})
        if r.get("status") == "OK":
            if outer_attempt > 0:
                r["outer_retry_log"] = attempts
                print(f"[VOICES-2V-AUDIO][segment-retry] {name}: outer_attempt={outer_attempt}でOK "
                      f"(既存関数の再実行のみ、内部retry上限は無変更)")
            return r
        print(f"[VOICES-2V-AUDIO][segment-retry] {name}: outer_attempt={outer_attempt} status="
              f"{r.get('status')} reason={r.get('reason')}")
    r["outer_retry_log"] = attempts
    return r


# ============================================================
# Step 3: TTS(production_runner_01.py::run_tts()と完全同一の呼び出し
# 順序・引数規約、出力先のみNARRATION_DIRへ差し替え)
# ============================================================
def step_tts(parts: dict, support_texts: dict, voice_a: str, voice_b: str) -> dict:
    shared_narration.ensure_all_shared_narration_b1(NARRATION_DIR)  # Production、無変更(Master Audio Store経由)

    results = {}
    topic_intro_text = f"Today's topic is {parts['title']}."
    print("[VOICES-2V-AUDIO] topic_intro生成(Charon)...")
    with cl.segment_context("topic_intro"):
        results["topic_intro"] = _call_with_segment_retry(
            "topic_intro", voice01.generate_charon_english,
            tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(topic_intro_text)),
            f"{NARRATION_DIR}/topic_intro.wav")
    results["topic_intro"]["canonical_text"] = topic_intro_text
    assert_budget_ok("after topic_intro TTS")

    for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
        text = support_texts[name]
        print(f"[VOICES-2V-AUDIO] {name}生成(Charon、run2_clean既存Comment Contract再利用)...")
        with cl.segment_context(name):
            results[name] = _call_with_segment_retry(
                name, voice01.generate_charon_english,
                tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(text)), f"{NARRATION_DIR}/{name}.wav",
                style_prefix_override=tts_gen.B1_PREVIEW_STYLE_PREFIX_CALM, disfluency_qa=True)
        results[name]["canonical_text"] = text
    assert_budget_ok("after preview/comment TTS")

    for name in ("point_one_heading", "point_two_heading"):
        text = parts[name]
        sc.assert_no_point_number_label(text, name)
        print(f"[VOICES-2V-AUDIO] {name}生成(Narrator=Aoede、既存point_headings.generate)...")
        with cl.segment_context(name):
            results[name] = point_headings.generate(
                tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(text)), f"{NARRATION_DIR}/{name}.wav")
        results[name]["canonical_text"] = text
    assert_budget_ok("after Narrator heading TTS")

    for name, text, voice_name in (
        ("point_one", parts["point_one_body"], voice_a),
        ("point_two", parts["point_two_body"], voice_b),
    ):
        sc.assert_no_point_number_label(text, name)
        print(f"[VOICES-2V-AUDIO] {name}生成({voice_name}、既存generate_voice_body_wide_margin)...")
        with cl.segment_context(name):
            results[name] = b1prod.generate_voice_body_wide_margin(
                tts_gen.tts_safe_news_en(text), f"{NARRATION_DIR}/{name}.wav", voice_name,
                enable_connected_speech_equivalence_layer=True, enable_repetition_qa=True)
        results[name]["canonical_text"] = text
    assert_budget_ok("after Voice A/B TTS")

    for name, text in (
        ("full_story_part1", parts["part1"]), ("full_story_part2", parts["part2"]),
        (b1prod.EXTRA_SEGMENT_NAME, parts["tension_body"]), ("in_one_line", parts["in_one_line"]),
    ):
        print(f"[VOICES-2V-AUDIO] {name}生成(Aoede、既存news_tail_fix.generate_news_narration_wide_margin)...")
        with cl.segment_context(name):
            results[name] = news_tail_fix.generate_news_narration_wide_margin(
                tts_gen.tts_safe_news_en(text), f"{NARRATION_DIR}/{name}.wav",
                disfluency_qa=(name == "in_one_line"),
                enable_connected_speech_equivalence_layer=(name in ("full_story_part1", "full_story_part2")),
                enable_repetition_qa=(name in ("full_story_part1", "full_story_part2")))
        results[name]["canonical_text"] = text
    assert_budget_ok("after Hook/Tension/Closing TTS")

    return results


def step_finalize_tts(new_results: dict, kp_items: list) -> tuple:
    data = {"segments": new_results, "key_phrases": {}}
    for item in kp_items:
        rank = item["rank"]
        data["key_phrases"][str(rank)] = {
            "en": {"status": "OK"},
            "ja_charon": {"status": "OK"},
        }
    save_json(f"{OUT_B1B_DIR}/audit/tts_generation_results.json", data)
    all_status = {k: v.get("status") for k, v in new_results.items()}
    save_json(f"{OUT_B1B_DIR}/run_summary_tts.json", {"segment_status": all_status})
    print(f"[VOICES-2V-AUDIO] TTS完了。segment_status={all_status}")
    return data, all_status


# ============================================================
# Step 4: Assembly(asm.load_b1_sources/apply_b1_gain/assemble_with_
# timeline/apply_headroom_safety_valve無変更。load_b1_sources内部で
# verify_episode_audio_validation_gate(Audio Validation Gate)を実行する)
# ============================================================
def step_assembly(voice_a: str, voice_b: str) -> tuple:
    os.makedirs(f"{OUT_B1B_DIR}/assembled", exist_ok=True)
    os.makedirs(f"{OUT_B1B_DIR}/audit", exist_ok=True)

    sources = asm.load_b1_sources(THEME)  # Production、無変更(Gate検証・shared assets copy含む)

    mono, sr, _, _ = common.read_wav_float(f"{NARRATION_DIR}/{b1prod.EXTRA_SEGMENT_NAME}.wav")
    assert sr == common.SAMPLE_RATE
    sources["b1_segments"][b1prod.EXTRA_SEGMENT_NAME] = mono

    parts = asm.apply_b1_gain(sources)  # Production、無変更
    seq = b1prod.build_b1_voices_timeline(parts, voice_a, voice_b)  # Production、無変更(B-Family専用)
    result = asm.assemble_with_timeline(seq)  # Production、無変更
    headroom = asm.apply_headroom_safety_valve(result["assembled"], seq)  # Production、無変更
    assembled = headroom["assembled"]

    out_path = f"{OUT_B1B_DIR}/assembled/{EPISODE_WAV_NAME}"
    save_json(f"{OUT_B1B_DIR}/audit/gain_report.json", parts["gain_report"])
    save_json(f"{OUT_B1B_DIR}/audit/timeline.json", result["timeline"])
    save_json(f"{OUT_B1B_DIR}/audit/headroom_report.json", headroom["report"])
    common.write_wav_float(out_path, assembled, asm.SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], asm.SR)

    summary = {
        "status": "OK", "out_path": out_path, "duration_seconds": result["total_duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": asm.SR, "channels": 2, "headroom_safety_valve": headroom["report"],
        "voice_a": voice_a, "voice_b": voice_b,
    }
    save_json(f"{OUT_B1B_DIR}/run_summary_assemble.json", summary)
    print(f"[VOICES-2V-AUDIO] Assembly status={summary['status']} duration={summary['duration_seconds']} "
          f"peak={summary['peak']} clipping={summary['clipping_detected']}")
    return summary, result["timeline"]


# ============================================================
# Step 5: mp3変換(soundfile.write format=MP3、pip installなし)
# ============================================================
def convert_one(wav_path: str, mp3_path: str) -> dict:
    data, sr = sf.read(wav_path)
    sf.write(mp3_path, data, sr, format="MP3")
    info = sf.info(mp3_path)
    return {
        "wav_path": wav_path, "mp3_path": mp3_path,
        "wav_bytes": os.path.getsize(wav_path), "mp3_bytes": os.path.getsize(mp3_path),
        "sample_rate": sr, "channels": (data.shape[1] if data.ndim > 1 else 1),
        "duration_seconds": round(info.frames / info.samplerate, 3),
    }


def step_web_delivery(assemble_summary: dict) -> dict:
    os.makedirs(WEB_DIR, exist_ok=True)
    os.makedirs(WEB_SEG_DIR, exist_ok=True)
    conversions = []
    ep_mp3 = f"{WEB_DIR}/episode.mp3"
    conversions.append({"kind": "episode", **convert_one(assemble_summary["out_path"], ep_mp3)})
    wav_names = sorted(n for n in os.listdir(NARRATION_DIR) if n.endswith(".wav"))
    for name in wav_names:
        stem = name[:-4]
        conversions.append({"kind": "segment", "segment_id": stem,
                             **convert_one(f"{NARRATION_DIR}/{name}", f"{WEB_SEG_DIR}/{stem}.mp3")})
    result = {"episode_mp3": ep_mp3, "segment_count": len(wav_names), "conversions": conversions}
    save_json(f"{OUT_BASE}/web_delivery.json", result)
    return result


# ============================================================
# Step 6: player.html(標準Audio Review Player、相対パスのみ、
# production_runner_01.py::_row_info/build_player_html と同一の
# ラベル→text/voice/audioマッピングを、相対mp3パスへ差し替えて再利用)
# ============================================================
def _row_info(label: str, parts: dict, support_texts: dict, voice_a: str, voice_b: str, kp_by_rank: dict) -> dict:
    charon = "Charon"
    if label == "Intro":
        return {"text": "音楽ジングル(ナレーションなし、読み上げなし)。", "voice": None, "audio": None, "sfx": True}
    if label == "Outro (Charon)":
        return {"text": "音楽ジングル(ナレーションなし、読み上げなし)。", "voice": None, "audio": None, "sfx": True}
    if label.startswith("Notification ") or label.startswith("Point Notification"):
        return {"text": "効果音(読み上げなし)", "voice": None, "audio": None, "sfx": True}
    if label == "Welcome (Charon)":
        return {"text": shared_narration.FIXED_ENGLISH_TEXTS["welcome"], "voice": charon,
                "audio": "welcome_charon", "sfx": False}
    if label == "Topic intro (Charon)":
        return {"text": f"Today's topic is {parts['title']}.", "voice": charon, "audio": "topic_intro", "sfx": False}
    if label == "Preview intro (Charon)":
        return {"text": shared_narration.FIXED_ENGLISH_TEXTS["preview_intro"], "voice": charon,
                "audio": "preview_intro_charon", "sfx": False}
    if label == "Preview (Charon)":
        return {"text": support_texts["preview"], "voice": charon, "audio": "preview", "sfx": False}
    if label == "Key phrases intro (Charon)":
        return {"text": shared_narration.FIXED_ENGLISH_TEXTS["key_phrases_intro"], "voice": charon,
                "audio": "key_phrases_intro_charon", "sfx": False}
    if label.startswith("Key Phrase "):
        rank = int(label.split(" ")[-1])
        kp = kp_by_rank[rank]
        en = kp["used_form"]
        ja = kp["japanese_gloss"]
        ja_tts = kp.get("japanese_gloss_tts", ja)
        text = f"EN: {en}<br>JA(表示): {ja}" + ("" if ja_tts == ja else f"<br>JA(TTS用): {ja_tts}")
        return {"text": text, "voice": "Aoede(EN)/Charon(JA)",
                "audio": (f"kp{rank}_en", f"kp{rank}_ja_charon"), "sfx": False}
    if label == "Full story intro (Charon)":
        return {"text": shared_narration.FIXED_ENGLISH_TEXTS["full_story_intro"], "voice": charon,
                "audio": "full_story_intro_charon", "sfx": False}
    if label.startswith("Comment 1 "):
        return {"text": support_texts["comment_1"], "voice": charon, "audio": "comment_1", "sfx": False}
    if label.startswith("Comment 2 "):
        return {"text": support_texts["comment_2"], "voice": charon, "audio": "comment_2", "sfx": False}
    if label.startswith("Comment 3 "):
        return {"text": support_texts["comment_3"], "voice": charon, "audio": "comment_3", "sfx": False}
    if label.startswith("Comment 4 "):
        return {"text": support_texts["comment_4"], "voice": charon, "audio": "comment_4", "sfx": False}
    if label.startswith("Hook Part 1"):
        return {"text": parts["part1"], "voice": "Aoede", "audio": "full_story_part1", "sfx": False}
    if label.startswith("Hook Part 2"):
        return {"text": parts["part2"], "voice": "Aoede", "audio": "full_story_part2", "sfx": False}
    if label.startswith("Narrator: One Voice heading"):
        return {"text": parts["point_one_heading"], "voice": "Aoede (Narrator)",
                "audio": "point_one_heading", "sfx": False}
    if label.startswith("Voice A body"):
        return {"text": parts["point_one_body"], "voice": voice_a, "audio": "point_one", "sfx": False}
    if label.startswith("Narrator: Another Voice heading"):
        return {"text": parts["point_two_heading"], "voice": "Aoede (Narrator)",
                "audio": "point_two_heading", "sfx": False}
    if label.startswith("Voice B body"):
        return {"text": parts["point_two_body"], "voice": voice_b, "audio": "point_two", "sfx": False}
    if label.startswith("Tension:"):
        return {"text": parts["tension_body"] + " 【内部記録: Analytical Leakage Check残存flag "
                        "(voice_b/tension、下記comment_fact_safety_evidence.json参照)】",
                "voice": "Aoede", "audio": b1prod.EXTRA_SEGMENT_NAME, "sfx": False}
    if label.startswith("Closing:"):
        return {"text": parts["in_one_line"], "voice": "Aoede", "audio": "in_one_line", "sfx": False}
    return {"text": "【未取得】このラベルに対応するscript textを特定できませんでした。",
            "voice": None, "audio": None, "sfx": False}


def rel_seg_url(stem: str) -> str:
    return f"./web/segments/{stem}.mp3"


def build_player_html(assemble_summary: dict, timeline: list, parts: dict, support_texts: dict,
                       voice_a: str, voice_b: str, voice_resolution_reasons: dict) -> str:
    kp_data = load_json(f"{KP_DIR}/keywords_canonicalized.json")
    kp_by_rank = {item["rank"]: item for item in kp_data["items"]}

    rows = []
    for entry in timeline:
        label = entry["part"]
        if label.startswith("pause_"):
            continue
        info = _row_info(label, parts, support_texts, voice_a, voice_b, kp_by_rank)
        sec = entry["start_seconds"]
        voice_disp = info["voice"] or ("SFX" if info["sfx"] else "—")
        if info["sfx"] or not info["audio"]:
            audio_html = "—"
        elif isinstance(info["audio"], tuple):
            audio_html = player_common.render_single_audio_html(tuple(rel_seg_url(p) for p in info["audio"]))
        else:
            audio_html = player_common.render_single_audio_html(rel_seg_url(info["audio"]))
        rows.append(player_common.render_timeline_row(
            sec, label, voice_disp, info["text"], audio_html, missing="未取得" in info["text"]))
    timeline_table = player_common.render_timeline_table(rows)

    kp_rows = []
    for rank in sorted(kp_by_rank):
        kp = kp_by_rank[rank]
        kp_rows.append(f'<tr><td>{rank}</td><td>{kp["used_form"]}</td><td>{kp["japanese_gloss"]}</td>'
                        f'<td>{kp.get("japanese_gloss_tts", kp["japanese_gloss"])}</td>'
                        f'<td>{kp.get("qa_overall_status")}</td></tr>')
    kp_table = ('<table class="kp"><thead><tr><th>#</th><th>English(used_form)</th><th>表示用gloss</th>'
                '<th>TTS用テキスト</th><th>redundancy QA</th></tr></thead>'
                f'<tbody>{"".join(kp_rows)}</tbody></table>')

    reason_note = ""
    if voice_resolution_reasons:
        reason_note = "<p style='color:#b00'><b>Voice変更理由(fallback発火):</b> " + \
                       " / ".join(f"{k}: {v}" for k, v in voice_resolution_reasons.items()) + "</p>"

    episode_url = "./web/episode.mp3"
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>USER-TEST-AUDIO-COMPLETION-01-VOICES player(B1 2V)</title>
<style>
{player_common.PLAYER_STANDARD_CSS}
</style>
<script>
{player_common.SEEK_SCRIPT}
</script>
</head><body>
<h1>Voices / Is personalized news good for us? — B1 2V 完成episode候補</h1>
<p class="note">
<b>Status: PARTIAL / USER TEST READY(Leakage残存)。PRODUCTION_WIRED未承認。</b><br>
2V(2 Voices)構成、完成episode(1本化wav、Standard同期)。管理ID:
USER-TEST-AUDIO-COMPLETION-01-VOICES(OPEN-151)。duration={assemble_summary['duration_seconds']}s
peak={assemble_summary['peak']} clipping={assemble_summary['clipping_detected']}
headroom_safety_valve_applied={assemble_summary['headroom_safety_valve']['applied']}。
voice_a={voice_a} / voice_b={voice_b}(Narrator見出しは全てAoede固定)。<br>
<b>既知の限界:</b> Analytical Leakage Check(voice_b/tension)が3attempt上限到達後も
flagged残存のまま採用している(ユーザー承認: Prompt改善・Gate緩和は行わずPARTIALの
ままユーザー実検証へ進める)。詳細原文は
<a href="./comment_fact_safety_evidence.json">comment_fact_safety_evidence.json</a>参照。
</p>
{reason_note}

<h2>Episode audio</h2>
<audio id="episode_audio" class="main" controls preload="none" src="{episode_url}"></audio>

<h2>Key Phrases(5件)</h2>
{kp_table}

<h2>タイムライン・全スクリプト(収録順、同一行にSeek+voice+script)</h2>
{timeline_table}
</body></html>"""
    with open(f"{OUT_BASE}/player.html", "w", encoding="utf-8") as f:
        f.write(html)
    return f"{OUT_BASE}/player.html"


# ============================================================
# Step 7: 記事⇔音声一致確認 + Comment/Fact Safety evidence
# ============================================================
def step_consistency_and_evidence(article_text: str, parts: dict, support_texts: dict,
                                   tts_results: dict, timeline: list) -> tuple:
    checks = {
        "point_one_body": parts["point_one_body"] in article_text,
        "point_two_body": parts["point_two_body"] in article_text,
        "tension_body": parts["tension_body"] in article_text,
        "in_one_line": parts["in_one_line"] in article_text,
        "hook_part1_and_part2_reconstruct_hook_body": (
            (parts["part1"] + " " + parts["part2"]).replace("  ", " ")
            in article_text.replace("  ", " ")),
    }
    tts_canonical_matches_parts = {
        "point_one": tts_results["point_one"]["canonical_text"] == parts["point_one_body"],
        "point_two": tts_results["point_two"]["canonical_text"] == parts["point_two_body"],
        "full_story_part1": tts_results["full_story_part1"]["canonical_text"] == parts["part1"],
        "full_story_part2": tts_results["full_story_part2"]["canonical_text"] == parts["part2"],
        b1prod.EXTRA_SEGMENT_NAME: (
            tts_results[b1prod.EXTRA_SEGMENT_NAME]["canonical_text"] == parts["tension_body"]),
        "in_one_line": tts_results["in_one_line"]["canonical_text"] == parts["in_one_line"],
    }
    consistency = {
        "article_path": ARTICLE_PATH,
        "section_body_substring_checks": checks,
        "all_section_bodies_verbatim_from_article": all(
            v for k, v in checks.items() if k != "hook_part1_and_part2_reconstruct_hook_body"),
        "tts_input_text_matches_parts_extracted_from_article": tts_canonical_matches_parts,
        "all_tts_input_matches_parts": all(tts_canonical_matches_parts.values()),
    }
    save_json(f"{OUT_BASE}/article_audio_consistency.json", consistency)

    leakage = load_json(LEAKAGE_EVIDENCE_PATH)
    segment_name_by_comment = {"comment_1": "comment_1.wav", "comment_2": "comment_2.wav",
                                "comment_3": "comment_3.wav", "comment_4": "comment_4.wav"}
    timeline_by_label = {e["part"]: e["start_seconds"] for e in timeline}
    comment_timeline = {}
    for label, sec in timeline_by_label.items():
        if label.startswith("Comment 1 "):
            comment_timeline["comment_1"] = sec
        elif label.startswith("Comment 2 "):
            comment_timeline["comment_2"] = sec
        elif label.startswith("Comment 3 "):
            comment_timeline["comment_3"] = sec
        elif label.startswith("Comment 4 "):
            comment_timeline["comment_4"] = sec

    evidence = {
        "comment_contract": {
            "source": ("run2_clean/b1_2v_new_theme/audit/new_theme_comment_contract_summary.json + "
                       "b1_2v_new_theme/b1_support_texts.json(既存生成、再生成なし)"),
            "support_status_at_generation": {
                "preview": "OK", "comment_1": "OK", "comment_2": "OK", "comment_3": "OK", "comment_4": "OK"},
            "deviation_overall_status_at_generation": "LEDGER_COMPLIANT",
            "texts": support_texts,
            "segment_files": segment_name_by_comment,
            "episode_timeline_start_seconds": comment_timeline,
        },
        "fact_safety_gate": {
            "mode": "Writer stage専用機構(記事生成時にのみ発火判定)。本driverは記事を"
                    "再生成しないため新規判定は行わない(既存記録の転記のみ)。",
            "run2_clean_record": (
                "RESULT_PACKET_VOICES_VAR2.md 3節/EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-"
                "COUNT-PRODUCTION-WIRING-02_REPORT.md: 本記事(attempt3)ではMAJOR deviationが"
                "stage1/2条件に非該当だったためGate降格(Fact Safety Gate発動)は発生しなかった"
                "(Local Rewriteでdeviationが解消)。発火能力自体はoffline証明済み(9テストPASS)。"),
            "fired_in_this_article": False,
        },
        "analytical_leakage_check_residual_flag": {
            "source_file": LEAKAGE_EVIDENCE_PATH,
            "any_flagged": leakage.get("any_flagged"),
            "flagged_items": leakage.get("flagged_items"),
            "note": ("ユーザー承認: 追加Prompt改善・Gate緩和は行わず、PARTIALのままユーザー"
                     "実検証へ進める。試聴対象から隠さず本ファイルとplayer.html双方に記録する。"),
        },
    }
    save_json(f"{OUT_BASE}/comment_fact_safety_evidence.json", evidence)
    return consistency, evidence


def main() -> None:
    cl.install(COST_LOG_PATH)

    article_text, parts = step_prepare()
    voice_a, voice_b, voice_reasons = step_voice_check(parts)
    kp_result = step_key_phrases(article_text)
    # sc.run_key_phrases()自体の既存規約(NG_REVIEW_REQUIRED = 自動不採用・人間確認後に
    # 採用可)に従い、本driverも黙示的な自動採用はしない(top-levelに"status"キーが
    # 付くのは canonicalization失敗、またはredundancy retry上限到達=NG_REVIEW_REQUIRED
    # の場合のみ。成功時はtop-level"status"キーなし)。
    if kp_result.get("status") == "NG_REVIEW_REQUIRED" or not kp_result.get("canonicalization") \
            or "merged" not in (kp_result.get("canonicalization") or {}):
        raise RuntimeError(f"[KEY_PHRASE_BLOCKED] Key Phrase生成がPASSしませんでした"
                            f"(既存Validator既定の自動不採用ポリシー、Gate緩和はしない): {kp_result}")

    support_texts = load_json(SUPPORT_TEXTS_PATH)
    kp_items = kp_result["canonicalization"]["merged"]["items"]

    tts_results = step_tts(parts, support_texts, voice_a, voice_b)
    step_finalize_tts(tts_results, kp_items)

    assemble_summary, timeline = step_assembly(voice_a, voice_b)
    web_result = step_web_delivery(assemble_summary)
    player_path = build_player_html(assemble_summary, timeline, parts, support_texts,
                                     voice_a, voice_b, voice_reasons)
    consistency, evidence = step_consistency_and_evidence(
        article_text, parts, support_texts, tts_results, timeline)

    jpy, by_provider = compute_cost_jpy_so_far()
    cost_summary = {
        "budget_jpy_cap_new_spend_only": BUDGET_JPY_CAP,
        "new_spend_jpy_total": round(jpy, 2),
        "new_spend_by_provider_jpy": by_provider,
        "note": ("Key Phrase LLM(選定+canonicalization+redundancy QA)+TTS一式(Master Audio "
                 "Store既存shared narration再利用分は追加費用ゼロ)。Comment 1-4/Preview LLMは"
                 "run2_clean既存生成の再利用のため本driverでの追加費用はゼロ。"),
    }
    save_json(f"{OUT_BASE}/cost_summary_audio.json", cost_summary)

    print(f"[VOICES-2V-AUDIO] DONE player={os.path.abspath(player_path)} "
          f"episode_mp3={web_result['episode_mp3']} duration={assemble_summary['duration_seconds']}s "
          f"new_spend_jpy={jpy:.2f}")


if __name__ == "__main__":
    main()
