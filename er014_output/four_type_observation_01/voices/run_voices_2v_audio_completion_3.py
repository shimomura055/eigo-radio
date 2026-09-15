# ============================================================
# er014_output/four_type_observation_01/voices/run_voices_2v_audio_completion_3.py
# 管理ID: USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-VOICES(継続CONT1、Fable修正指示1回目)
# ============================================================
# 目的: 一人称化修正後にr3(status=OK、run3_first_person_r3/b1_2v_new_theme_
# attempt3/article.md)で確定した2V canonical candidateを、run_voices_2v_
# audio_completion.py(run1、記事ゼロからのフル音声化driver)と完全同一の
# primitive呼び出し順序・引数規約で音声化する。er012_*/Writer/Gate/Promptは
# 一切変更しない。--article-dirでarticle.mdを含むディレクトリ(attempt dir)を
# 指定できるよう引数化しただけで、Comment Contract結果の参照元
# (b1_support_texts.json)・Leakage evidence参照元はarticle-dirの親
# (b1_2v_new_theme/、同一runの兄弟ディレクトリ)から自動導出する
# (run1のARTICLE_PATH/SUPPORT_TEXTS_PATH/LEAKAGE_EVIDENCE_PATHの決め方を
# そのまま一般化しただけで、新しいロジックは追加していない)。
#
# run_voices_2v_audio_completion_2.py(CONT1)はrun1が既に生成した資産を
# 前提にcomment_2のみ差し替える継続driverだったが、本タスクの記事は
# 一人称化修正後に新規生成された別の記事(Comment/Key Phrase/TTS一式が
# 未生成)であるため、run1と同じ「ゼロから全segment生成」の経路を踏む
# 必要がある(run1のstep構成をそのまま踏襲、run_voices_2v_audio_
# completion_2.pyの差分適用パターンではなく)。
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
os.chdir(_REPO_ROOT)

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

PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0
ARTICLE_ID = "voices_fix02_first_person_b1_2v_r3"
SOURCE_LEVEL = "B1"
EPISODE_WAV_NAME = "Voices_Fix02_FirstPerson_B1_2V.wav"


def load_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


def sha(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def _load_pricing():
    prices = load_json(PRICING_SNAPSHOT_PATH)["prices"]

    def price(provider, model, meter):
        return next(p["price"] for p in prices
                    if p["provider"] == provider and p["model"] == model and p["meter"] == meter
                    and p.get("tier", "Standard") == "Standard")
    return price


class HumanReviewLockStop(RuntimeError):
    """Human Review Lock発動時にSTOPするための専用例外(承認代行しない、
    run_voices_2v_audio_completion_2.py/er012_editorial_b_voices_3v_audio_trial_01.pyと同一パターン)。"""


def assert_not_locked(result: dict, segment_name: str) -> None:
    if isinstance(result, dict) and result.get("status") == "HUMAN_REVIEW_LOCKED":
        raise HumanReviewLockStop(
            f"[HUMAN_REVIEW_LOCK] segment={segment_name} でHuman Review Lockが発動しました。"
            f"承認代行はせず実行を中止します。詳細: {result}")


class Ctx:
    """CLI引数から導出するpath/定数一式(run1のmodule-globalをinstanceへ変えただけ)。"""

    def __init__(self, article_dir: str, out_subdir: str, budget_jpy: float):
        self.article_dir = article_dir.rstrip("/")
        # article_dirの親(...のb1_2v_new_theme/)にComment Contract結果がある
        # (run_voices_2v_b1_v2.py::main()のout_dir_base設計と同一)。
        run_dir = os.path.dirname(self.article_dir)  # 例: voices/run3_first_person_r3
        theme_dir = f"{run_dir}/b1_2v_new_theme"
        attempt_stem = os.path.basename(self.article_dir)  # 例: b1_2v_new_theme_attempt3
        self.article_path = f"{self.article_dir}/article.md"
        self.support_texts_path = f"{theme_dir}/b1_support_texts.json"
        self.leakage_evidence_path = f"{self.article_dir}/analytical_leakage_check_2v_{attempt_stem.split('_')[-1]}.json"
        self.fact_qa_path = f"{self.article_dir}/fact_qa.json"
        self.ledger_deviation_path = f"{self.article_dir}/ledger_deviation.json"

        self.out_base = f"er014_output/four_type_observation_01/voices/{out_subdir}"
        self.out_b1b_dir = f"{self.out_base}/b1b"
        self.narration_dir = f"{self.out_b1b_dir}/narration"
        self.kp_dir = f"{self.out_b1b_dir}/key_phrases"
        self.web_dir = f"{self.out_base}/web"
        self.web_seg_dir = f"{self.web_dir}/segments"
        self.cost_log_path = f"{self.out_base}/cost_log_raw.jsonl"
        self.budget_jpy_cap = budget_jpy
        self.theme = {"theme_id": ARTICLE_ID, "out_dir": self.out_base}

    def compute_cost_jpy_so_far(self) -> tuple:
        if not os.path.exists(self.cost_log_path):
            return 0.0, {}
        price = _load_pricing()
        total_usd = 0.0
        by_provider = {}
        with open(self.cost_log_path, encoding="utf-8") as f:
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

    def assert_budget_ok(self, note: str = "") -> float:
        jpy, by_provider = self.compute_cost_jpy_so_far()
        print(f"[VOICES-2V-AUDIO-FIX02][cost] so far={jpy:.2f} JPY by_provider={by_provider} ({note})")
        if jpy > self.budget_jpy_cap:
            raise RuntimeError(
                f"[BUDGET_GUARD] cost so far {jpy:.2f} JPY > cap {self.budget_jpy_cap} JPY. Stopping ({note}).")
        return jpy


# ============================================================
# Step 0: prepare(記事読み取り、5区切りparse。b1prod.build_parts無変更)
# ============================================================
def step_prepare(ctx: Ctx) -> tuple:
    with open(ctx.article_path, encoding="utf-8") as f:
        article_text = f.read()
    parts = b1prod.build_parts(article_text)
    os.makedirs(f"{ctx.out_b1b_dir}/audit", exist_ok=True)
    with open(f"{ctx.out_b1b_dir}/article.md", "w", encoding="utf-8") as f:
        f.write(article_text)
    save_json(f"{ctx.out_b1b_dir}/parts.json", parts)
    return article_text, parts


# ============================================================
# Step 1: Voice可用性確認 + 解決(b1prod.run_voice_availability_check/
# resolve_voice_names無変更、2V=voice_a/voice_bのみ)
# ============================================================
def step_voice_check(ctx: Ctx, parts: dict) -> tuple:
    sample_text = b1prod.first_n_sentences(parts["point_one_body"], 3)
    sample_dir = f"{ctx.out_base}/audit/voice_samples"
    results = b1prod.run_voice_availability_check(sample_text, sample_dir)
    save_json(f"{sample_dir}/voice_sample_results.json", {"sample_text": sample_text, "results": results})
    voice_a, voice_b, reasons = b1prod.resolve_voice_names(results)
    save_json(f"{ctx.out_base}/audit/voice_resolution.json",
              {"voice_a": voice_a, "voice_b": voice_b, "reasons": reasons})
    return voice_a, voice_b, reasons


# ============================================================
# Step 2: Key Phrase(新規生成。sc.run_key_phrases無変更、内部で選定→
# canonicalization→redundancy QAを最大3回まで自動retry)
# ============================================================
def step_key_phrases(ctx: Ctx, article_text: str) -> dict:
    # 冪等性: 本scriptがAssembly以降で例外停止し再実行された場合に、既に成功している
    # Key Phrase生成(選定+canonicalization+redundancy QA、LLM呼び出し)を不要に
    # 繰り返さない。既存keywords_canonicalized.jsonがあればそれをそのまま採用する
    # (追加API呼び出しなし)。
    kp_canon_path = f"{ctx.kp_dir}/keywords_canonicalized.json"
    summary_path = f"{ctx.out_base}/audit/key_phrase_generation_summary.json"
    if os.path.exists(kp_canon_path) and os.path.exists(summary_path):
        print(f"[VOICES-2V-AUDIO-FIX02] 既存{kp_canon_path}を再利用します(再実行のため、追加API呼び出しなし)。")
        return load_json(summary_path)
    os.makedirs(ctx.kp_dir, exist_ok=True)
    result = sc.run_key_phrases(article_text, ctx.kp_dir, ARTICLE_ID, SOURCE_LEVEL, process="B1_SUPPORT")
    save_json(summary_path, result)
    ctx.assert_budget_ok("after Key Phrase generation")
    return result


_SEGMENT_OUTER_RETRY_MAX = 2  # 初回+最大2回=合計3回(run1と同じ規約)


def _call_with_segment_retry(name: str, gen_fn, *args, **kwargs) -> dict:
    attempts = []
    for outer_attempt in range(0, _SEGMENT_OUTER_RETRY_MAX + 1):
        r = gen_fn(*args, **kwargs)
        attempts.append({"outer_attempt": outer_attempt, "status": r.get("status")})
        if r.get("status") == "OK":
            if outer_attempt > 0:
                r["outer_retry_log"] = attempts
                print(f"[VOICES-2V-AUDIO-FIX02][segment-retry] {name}: outer_attempt={outer_attempt}でOK")
            return r
        print(f"[VOICES-2V-AUDIO-FIX02][segment-retry] {name}: outer_attempt={outer_attempt} status="
              f"{r.get('status')} reason={r.get('reason')}")
    r["outer_retry_log"] = attempts
    return r


# ============================================================
# Step 3: TTS(production_runner_01.py::run_tts()と完全同一の呼び出し
# 順序・引数規約、出力先のみNARRATION_DIRへ差し替え)
# ============================================================
def step_tts(ctx: Ctx, parts: dict, support_texts: dict, voice_a: str, voice_b: str) -> dict:
    # 冪等性: 本scriptがAssembly以降で例外停止し再実行された場合に、既に成功している
    # TTS呼び出しを不要に繰り返さないよう、既存tts_generation_results.jsonの全segmentが
    # status=OKなら再利用する(API呼び出しなし)。segment数(14件、Key Phrase除く)が
    # 既存記録と一致することを条件にする(記事差し替え時の取り違え防止)。
    existing_tts_path = f"{ctx.out_b1b_dir}/audit/tts_generation_results.json"
    if os.path.exists(existing_tts_path):
        existing = load_json(existing_tts_path)
        existing_segments = existing.get("segments", {})
        expected_names = {"topic_intro", "preview", "comment_1", "comment_2", "comment_3", "comment_4",
                           "point_one_heading", "point_two_heading", "point_one", "point_two",
                           "full_story_part1", "full_story_part2", b1prod.EXTRA_SEGMENT_NAME, "in_one_line"}
        if expected_names.issubset(existing_segments.keys()) and \
                all(existing_segments[n].get("status") == "OK" for n in expected_names):
            print(f"[VOICES-2V-AUDIO-FIX02] 既存{existing_tts_path}(14 segment全件OK)を再利用します"
                  f"(再実行のため、追加API呼び出しなし)。")
            return {n: existing_segments[n] for n in expected_names}

    shared_narration.ensure_all_shared_narration_b1(ctx.narration_dir)  # Production、無変更(Master Audio Store経由)

    results = {}
    topic_intro_text = f"Today's topic is {parts['title']}."
    print("[VOICES-2V-AUDIO-FIX02] topic_intro生成(Charon)...")
    with cl.segment_context("topic_intro"):
        results["topic_intro"] = _call_with_segment_retry(
            "topic_intro", voice01.generate_charon_english,
            tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(topic_intro_text)),
            f"{ctx.narration_dir}/topic_intro.wav")
    results["topic_intro"]["canonical_text"] = topic_intro_text
    ctx.assert_budget_ok("after topic_intro TTS")

    for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
        text = support_texts[name]
        print(f"[VOICES-2V-AUDIO-FIX02] {name}生成(Charon、Comment Contract結果再利用)...")
        with cl.segment_context(name):
            results[name] = _call_with_segment_retry(
                name, voice01.generate_charon_english,
                tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(text)), f"{ctx.narration_dir}/{name}.wav",
                style_prefix_override=tts_gen.B1_PREVIEW_STYLE_PREFIX_CALM, disfluency_qa=True)
        results[name]["canonical_text"] = text
    ctx.assert_budget_ok("after preview/comment TTS")

    for name in ("point_one_heading", "point_two_heading"):
        text = parts[name]
        sc.assert_no_point_number_label(text, name)
        print(f"[VOICES-2V-AUDIO-FIX02] {name}生成(Narrator=Aoede、既存point_headings.generate)...")
        with cl.segment_context(name):
            results[name] = point_headings.generate(
                tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(text)), f"{ctx.narration_dir}/{name}.wav")
        results[name]["canonical_text"] = text
    ctx.assert_budget_ok("after Narrator heading TTS")

    for name, text, voice_name in (
        ("point_one", parts["point_one_body"], voice_a),
        ("point_two", parts["point_two_body"], voice_b),
    ):
        sc.assert_no_point_number_label(text, name)
        print(f"[VOICES-2V-AUDIO-FIX02] {name}生成({voice_name}、既存generate_voice_body_wide_margin)...")
        with cl.segment_context(name):
            results[name] = b1prod.generate_voice_body_wide_margin(
                tts_gen.tts_safe_news_en(text), f"{ctx.narration_dir}/{name}.wav", voice_name,
                enable_connected_speech_equivalence_layer=True, enable_repetition_qa=True)
        results[name]["canonical_text"] = text
    ctx.assert_budget_ok("after Voice A/B TTS")

    for name, text in (
        ("full_story_part1", parts["part1"]), ("full_story_part2", parts["part2"]),
        (b1prod.EXTRA_SEGMENT_NAME, parts["tension_body"]), ("in_one_line", parts["in_one_line"]),
    ):
        print(f"[VOICES-2V-AUDIO-FIX02] {name}生成(Aoede、既存news_tail_fix.generate_news_narration_wide_margin)...")
        with cl.segment_context(name):
            results[name] = news_tail_fix.generate_news_narration_wide_margin(
                tts_gen.tts_safe_news_en(text), f"{ctx.narration_dir}/{name}.wav",
                disfluency_qa=(name == "in_one_line"),
                enable_connected_speech_equivalence_layer=(name in ("full_story_part1", "full_story_part2")),
                enable_repetition_qa=(name in ("full_story_part1", "full_story_part2")))
        results[name]["canonical_text"] = text
    ctx.assert_budget_ok("after Hook/Tension/Closing TTS")

    return results


# ============================================================
# Step 2b: Key Phrase音声(run1のstep_key_phrases()はtext選定[keywords_
# canonicalized.json]のみでaudio[kp{rank}_en.wav/kp{rank}_ja_charon.wav]を
# 生成しないため[run1到達点の既知の欠落、run_voices_2v_audio_completion_2.py
# ::step_key_phrase_audioと同一原因]、Assembly[asm.load_b1_sources]が
# これらのwavを必須とすることを踏まえ、ここで生成する。呼び出し規約は
# er014.../voices/run_voices_2v_audio_completion_2.py::step_key_phrase_audio()
# (無変更、shared_narration.ensure_key_phrase_english_component/tts_gen.
# generate_charon_japanese_with_reading_safety)と同一。
# ============================================================
def step_key_phrase_audio(ctx: Ctx, kp_items: list) -> dict:
    existing_path = f"{ctx.out_b1b_dir}/audit/kp_tts_results.json"
    if os.path.exists(existing_path):
        existing = load_json(existing_path)
        if all(v["english"].get("status") == "OK" and v["japanese"].get("status") == "OK"
               for v in existing.values()):
            print(f"[VOICES-2V-AUDIO-FIX02] 既存{existing_path}(全件OK)を再利用します"
                  f"(再実行のため、追加API呼び出しなし)。")
            return {int(k): v for k, v in existing.items()}

    kp_results = {}
    for item in sorted(kp_items, key=lambda it: it["rank"]):
        rank = item["rank"]
        used_form = item["used_form"]
        ja_gloss = item["japanese_gloss"]
        ja_gloss_tts, ja_gloss_tts_fallback = tts_gen.resolve_key_phrase_ja_gloss_tts(item)
        print(f"[VOICES-2V-AUDIO-FIX02] Key Phrase {rank} 英語Component生成(Aoede、Master Audio Store経由): "
              f"{used_form!r}...")
        with cl.segment_context(f"kp{rank}_english"):
            en_r = shared_narration.ensure_key_phrase_english_component(
                tts_gen.tts_safe_kp_en(used_form), f"{ctx.narration_dir}/kp{rank}_en.wav")
        assert_not_locked(en_r, f"kp{rank}_english")
        print(f"[VOICES-2V-AUDIO-FIX02] Key Phrase {rank} 日本語meaning生成(Charon)...")
        with cl.segment_context(f"kp{rank}_japanese"):
            ja_r = tts_gen.generate_charon_japanese_with_reading_safety(
                ja_gloss_tts, f"{ctx.narration_dir}/kp{rank}_ja_charon.wav", tts_gen.expected_substring_ja(ja_gloss_tts),
                known_key_phrase_terms=[used_form])
        assert_not_locked(ja_r, f"kp{rank}_japanese")
        ja_r["display_gloss"] = ja_gloss
        ja_r["japanese_gloss_tts_fallback_derived"] = ja_gloss_tts_fallback
        kp_results[rank] = {"english": en_r, "japanese": ja_r}
        print(f"[VOICES-2V-AUDIO-FIX02] Key Phrase {rank}: en={en_r.get('status')} ja={ja_r.get('status')}")
    save_json(f"{ctx.out_b1b_dir}/audit/kp_tts_results.json", kp_results)
    ctx.assert_budget_ok("after Key Phrase audio generation")
    return kp_results


def step_finalize_tts(ctx: Ctx, new_results: dict, kp_results: dict) -> tuple:
    data = {"segments": new_results, "key_phrases": {}}
    for rank, v in kp_results.items():
        data["key_phrases"][str(rank)] = {"en": v["english"], "ja_charon": v["japanese"]}
    save_json(f"{ctx.out_b1b_dir}/audit/tts_generation_results.json", data)
    all_status = {k: v.get("status") for k, v in new_results.items()}
    save_json(f"{ctx.out_b1b_dir}/run_summary_tts.json", {"segment_status": all_status})
    print(f"[VOICES-2V-AUDIO-FIX02] TTS完了。segment_status={all_status}")
    return data, all_status


# ============================================================
# Step 4: Assembly(asm.load_b1_sources/apply_b1_gain/assemble_with_
# timeline/apply_headroom_safety_valve無変更。load_b1_sources内部で
# verify_episode_audio_validation_gate(Audio Validation Gate)を実行する)
# ============================================================
def step_assembly(ctx: Ctx, voice_a: str, voice_b: str) -> tuple:
    os.makedirs(f"{ctx.out_b1b_dir}/assembled", exist_ok=True)
    os.makedirs(f"{ctx.out_b1b_dir}/audit", exist_ok=True)

    gate_record = {"gate": "verify_episode_audio_validation_gate", "result": None, "error": None}
    try:
        sources = asm.load_b1_sources(ctx.theme)  # Production、無変更(Gate検証・shared assets copy含む)
        gate_record["result"] = "PASS"
    except RuntimeError as e:
        gate_record["result"] = "BLOCKED"
        gate_record["error"] = str(e)
        save_json(f"{ctx.out_base}/audio_validation.json", gate_record)
        raise

    mono, sr, _, _ = common.read_wav_float(f"{ctx.narration_dir}/{b1prod.EXTRA_SEGMENT_NAME}.wav")
    assert sr == common.SAMPLE_RATE
    sources["b1_segments"][b1prod.EXTRA_SEGMENT_NAME] = mono

    parts = asm.apply_b1_gain(sources)  # Production、無変更
    seq = b1prod.build_b1_voices_timeline(parts, voice_a, voice_b)  # Production、無変更(B-Family専用)
    result = asm.assemble_with_timeline(seq)  # Production、無変更
    headroom = asm.apply_headroom_safety_valve(result["assembled"], seq)  # Production、無変更
    assembled = headroom["assembled"]

    out_path = f"{ctx.out_b1b_dir}/assembled/{EPISODE_WAV_NAME}"
    save_json(f"{ctx.out_b1b_dir}/audit/gain_report.json", parts["gain_report"])
    save_json(f"{ctx.out_b1b_dir}/audit/timeline.json", result["timeline"])
    save_json(f"{ctx.out_b1b_dir}/audit/headroom_report.json", headroom["report"])
    common.write_wav_float(out_path, assembled, asm.SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], asm.SR)

    summary = {
        "status": "OK", "out_path": out_path, "duration_seconds": result["total_duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": asm.SR, "channels": 2, "headroom_safety_valve": headroom["report"],
        "voice_a": voice_a, "voice_b": voice_b,
    }
    save_json(f"{ctx.out_b1b_dir}/run_summary_assemble.json", summary)

    tts_data = load_json(f"{ctx.out_b1b_dir}/audit/tts_generation_results.json")
    segment_gate_statuses = {
        name: ("VALIDATED" if entry.get("status") == "OK" else entry.get("status"))
        for name, entry in tts_data.get("segments", {}).items()
    }
    gate_record["segment_statuses"] = segment_gate_statuses
    save_json(f"{ctx.out_base}/audio_validation.json", gate_record)

    print(f"[VOICES-2V-AUDIO-FIX02] Assembly status={summary['status']} duration={summary['duration_seconds']} "
          f"peak={summary['peak']} clipping={summary['clipping_detected']} gate={gate_record['result']}")
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


def step_web_delivery(ctx: Ctx, assemble_summary: dict) -> dict:
    os.makedirs(ctx.web_dir, exist_ok=True)
    os.makedirs(ctx.web_seg_dir, exist_ok=True)
    conversions = []
    ep_mp3 = f"{ctx.web_dir}/episode.mp3"
    conversions.append({"kind": "episode", **convert_one(assemble_summary["out_path"], ep_mp3)})
    wav_names = sorted(n for n in os.listdir(ctx.narration_dir) if n.endswith(".wav"))
    for name in wav_names:
        stem = name[:-4]
        conversions.append({"kind": "segment", "segment_id": stem,
                             **convert_one(f"{ctx.narration_dir}/{name}", f"{ctx.web_seg_dir}/{stem}.mp3")})
    result = {"episode_mp3": ep_mp3, "segment_count": len(wav_names), "conversions": conversions}
    save_json(f"{ctx.out_base}/web_delivery.json", result)
    return result


# ============================================================
# Step 6: player.html(標準Audio Review Player、相対パスのみ、
# run1のラベル→text/voice/audioマッピングを再利用)
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


def build_player_html(ctx: Ctx, assemble_summary: dict, timeline: list, parts: dict, support_texts: dict,
                       voice_a: str, voice_b: str, voice_resolution_reasons: dict, leakage: dict) -> str:
    kp_data = load_json(f"{ctx.kp_dir}/keywords_canonicalized.json")
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

    leak_flagged = leakage.get("any_flagged")
    leak_items = leakage.get("flagged_items") or []
    leak_note = "、".join(f"{it['voice']}({','.join(it['fail_fields'])})" for it in leak_items) or "なし"

    episode_url = "./web/episode.mp3"
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-VOICES player(B1 2V, 一人称版)</title>
<style>
{player_common.PLAYER_STANDARD_CSS}
</style>
<script>
{player_common.SEEK_SCRIPT}
</script>
</head><body>
<h1>Voices / Is personalized news good for us? — B1 2V 完成episode(一人称版)</h1>
<p class="note">
<b>Status: PARTIAL / USER TEST READY(一人称版、Analytical Leakage残存)。PRODUCTION_WIRED未承認。</b><br>
2V(2 Voices)構成、完成episode(1本化wav、Standard同期)。管理ID:
USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-VOICES(OPEN-151、継続CONT1)。duration={assemble_summary['duration_seconds']}s
peak={assemble_summary['peak']} clipping={assemble_summary['clipping_detected']}
headroom_safety_valve_applied={assemble_summary['headroom_safety_valve']['applied']}。
voice_a={voice_a} / voice_b={voice_b}(Narrator見出しは全てAoede固定)。<br>
<b>今回の変更点:</b> 2V Focus Moduleの一人称"I"指示block欠落(2026-09-08 APPROVED_FOR_PRODUCTION
仕様(4)未反映、Production不整合)を修正したWriter Promptで記事を再生成した(r3、Writer
status=OK、Fact Checker A' verdict=PASS、Ledger Deviation overall_status=LEDGER_COMPLIANT)。
Voice A/Bは各人物本人が一人称で自分の立場を語る構造に戻っている
(<a href="../../pov_check_final.json">pov_check_final.json</a>で機械確認)。<br>
<b>既知の限界:</b> Analytical Leakage Check残存flag: {leak_note}(3attempt上限到達後もflagged
残存のまま採用。ユーザー承認: 追加Prompt改善・Gate緩和は行わずPARTIALのままユーザー実検証へ
進める)。詳細原文は<a href="./comment_fact_safety_evidence.json">comment_fact_safety_evidence.json</a>参照。
</p>
{reason_note}

<h2>Episode audio</h2>
<audio id="episode_audio" class="main" controls preload="none" src="{episode_url}"></audio>

<h2>Key Phrases(5件)</h2>
{kp_table}

<h2>タイムライン・全スクリプト(収録順、同一行にSeek+voice+script)</h2>
{timeline_table}
</body></html>"""
    with open(f"{ctx.out_base}/player.html", "w", encoding="utf-8") as f:
        f.write(html)
    return f"{ctx.out_base}/player.html"


# ============================================================
# Step 7: 記事⇔音声一致確認 + Comment/Fact Safety evidence
# ============================================================
def step_consistency_and_evidence(ctx: Ctx, article_text: str, parts: dict, support_texts: dict,
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
        "article_path": ctx.article_path,
        "section_body_substring_checks": checks,
        "all_section_bodies_verbatim_from_article": all(
            v for k, v in checks.items() if k != "hook_part1_and_part2_reconstruct_hook_body"),
        "tts_input_text_matches_parts_extracted_from_article": tts_canonical_matches_parts,
        "all_tts_input_matches_parts": all(tts_canonical_matches_parts.values()),
    }
    save_json(f"{ctx.out_base}/article_audio_consistency.json", consistency)

    leakage = load_json(ctx.leakage_evidence_path)
    fact_qa = load_json(ctx.fact_qa_path) if os.path.exists(ctx.fact_qa_path) else None
    ledger_deviation = load_json(ctx.ledger_deviation_path) if os.path.exists(ctx.ledger_deviation_path) else None
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
        "first_person_fix_context": {
            "note": ("USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-VOICES: 2V Focus Moduleに一人称\"I\"指示block"
                     "欠落(2026-09-08 APPROVED_FOR_PRODUCTION仕様(4)未反映)というProduction不整合を"
                     "発見・修正(前回タスク、Writer Prompt修正・単体テスト44件/回帰185件PASS)。今回"
                     "(継続CONT1)、修正後Promptで3回目の再生成(r3)を実施し、Writer status=OK/Fact "
                     "Checker verdict=PASS/Ledger Deviation=LEDGER_COMPLIANTで記事を確定、本driverで"
                     "音声化した。"),
            "fact_checker_a_prime_result": (fact_qa or {}).get("result", {}).get("verdict"),
            "ledger_deviation_overall_status": (ledger_deviation or {}).get("overall_status"),
        },
        "comment_contract": {
            "source": (f"{os.path.dirname(ctx.article_dir)}/b1_2v_new_theme/audit/"
                       "new_theme_comment_contract_summary.json + b1_support_texts.json"
                       "(既存生成、run_voices_2v_b1_v2.py実行時のComment Contract結果、再生成なし)"),
            "support_status_at_generation": {
                "preview": "OK", "comment_1": "OK", "comment_2": "OK", "comment_3": "OK", "comment_4": "OK"},
            "deviation_overall_status_at_generation": "LEDGER_COMPLIANT",
            "texts": support_texts,
            "segment_files": segment_name_by_comment,
            "episode_timeline_start_seconds": comment_timeline,
        },
        "fact_safety_gate": {
            "mode": ("Writer stage専用機構(記事生成時に発火判定)。r1(run3_first_person)ではFact "
                     "Checker A'がFAILし(Tension文の政治的態度変化claimが2026-02のNature論文と矛盾)、"
                     "r2(run3_first_person_r2)ではLedger Deviation Local Rewriteの自動位置特定が失敗し"
                     "human_review_required=Trueとなった(いずれもGateが実際に発火・停止したevidence、"
                     "OPEN-120)。r3(本記事)ではFact Checker A' verdict=PASS/Ledger Deviation="
                     "LEDGER_COMPLIANTで、Gate発火なしに記事が確定した。詳細: "
                     "docs/pm/RESULT_PACKET_FIX02_VOICES_2.md。"),
            "fired_in_this_article": False,
            "fired_in_prior_attempts_same_task": True,
        },
        "analytical_leakage_check_residual_flag": {
            "source_file": ctx.leakage_evidence_path,
            "any_flagged": leakage.get("any_flagged"),
            "flagged_items": leakage.get("flagged_items"),
            "note": ("ユーザー承認: 追加Prompt改善・Gate緩和は行わず、PARTIALのままユーザー"
                     "実検証へ進める。試聴対象から隠さず本ファイルとplayer.html双方に記録する"
                     "(OPEN-151残存事象)。"),
        },
    }
    save_json(f"{ctx.out_base}/comment_fact_safety_evidence.json", evidence)
    return consistency, evidence


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--article-dir", required=True,
                         help="article.mdを含むディレクトリ(例: .../run3_first_person_r3/b1_2v_new_theme_attempt3)")
    parser.add_argument("--out", default="audio/b1_2v_v2")
    parser.add_argument("--budget-jpy", type=float, default=50.0)
    args = parser.parse_args()

    ctx = Ctx(
        article_dir=f"er014_output/four_type_observation_01/voices/{args.article_dir}"
        if not args.article_dir.startswith("er014_output") else args.article_dir,
        out_subdir=args.out, budget_jpy=args.budget_jpy)

    cl.install(ctx.cost_log_path)

    article_text, parts = step_prepare(ctx)
    voice_a, voice_b, voice_reasons = step_voice_check(ctx, parts)
    kp_result = step_key_phrases(ctx, article_text)
    if kp_result.get("status") == "NG_REVIEW_REQUIRED" or not kp_result.get("canonicalization") \
            or "merged" not in (kp_result.get("canonicalization") or {}):
        raise RuntimeError(f"[KEY_PHRASE_BLOCKED] Key Phrase生成がPASSしませんでした"
                            f"(既存Validator既定の自動不採用ポリシー、Gate緩和はしない): {kp_result}")

    support_texts = load_json(ctx.support_texts_path)
    kp_items = kp_result["canonicalization"]["merged"]["items"]

    tts_results = step_tts(ctx, parts, support_texts, voice_a, voice_b)
    kp_results = step_key_phrase_audio(ctx, kp_items)
    step_finalize_tts(ctx, tts_results, kp_results)

    assemble_summary, timeline = step_assembly(ctx, voice_a, voice_b)
    web_result = step_web_delivery(ctx, assemble_summary)
    leakage = load_json(ctx.leakage_evidence_path)
    player_path = build_player_html(ctx, assemble_summary, timeline, parts, support_texts,
                                     voice_a, voice_b, voice_reasons, leakage)
    consistency, evidence = step_consistency_and_evidence(
        ctx, article_text, parts, support_texts, tts_results, timeline)

    jpy, by_provider = ctx.compute_cost_jpy_so_far()
    cost_summary = {
        "budget_jpy_cap_new_spend_only": ctx.budget_jpy_cap,
        "new_spend_jpy_total": round(jpy, 2),
        "new_spend_by_provider_jpy": by_provider,
        "note": ("Key Phrase LLM(選定+canonicalization+redundancy QA)+TTS一式(Master Audio Store既存"
                 "shared narration再利用分は追加費用ゼロ)。Comment 1-4/Preview LLMはrun3_first_person_r3"
                 "既存生成の再利用のため本driverでの追加費用はゼロ。"),
    }
    save_json(f"{ctx.out_base}/cost_summary_audio.json", cost_summary)

    print(f"[VOICES-2V-AUDIO-FIX02] DONE player={os.path.abspath(player_path)} "
          f"episode_mp3={web_result['episode_mp3']} duration={assemble_summary['duration_seconds']}s "
          f"new_spend_jpy={jpy:.2f}")


if __name__ == "__main__":
    main()
