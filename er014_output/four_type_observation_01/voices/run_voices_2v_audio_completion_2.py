# ============================================================
# er014_output/four_type_observation_01/voices/run_voices_2v_audio_completion_2.py
# 管理ID: USER-TEST-AUDIO-COMPLETION-01-VOICES(継続CONT1、Fable修正指示1回目)
# ============================================================
# 目的: run_voices_2v_audio_completion.py(前回到達点、docs/pm/
# RESULT_PACKET_UT_VOICES.md)の続きとして、comment_2のみ既存の接続済み
# Comment Contract経路(er012_b_family_production_runner_01.py::
# run_comment_contract_for_new_theme、無変更)で再生成し、その新テキストで
# TTSをやり直し(Human Review Lockはcanonical_text_sha256が変わるため
# 通常の初回TTSとして扱われる、approve_regenerate()は呼ばない)、その後
# Assembly→Audio Validation Gate→完成episode→mp3→標準player→記事⇔音声
# 一致確認→comment_fact_safety_evidence.jsonまで進める。
#
# 記事本文(2V canonical candidate)・MAX_WRITER_ATTEMPTS・Leakage Gate/
# Fact Safety Gate・Promptは一切変更しない。er012_*は無変更(既存の
# public関数をそのままimportして呼ぶだけ)。
from __future__ import annotations

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
import er003_v1_n3_01_tts_generate as tts_gen
import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl
import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er012_b_family_production_runner_01 as runner_mod  # er012_*、無変更、関数呼び出しのみ
import er012_b_family_voices_production_01 as b1prod

ARTICLE_PATH = ("er014_output/four_type_observation_01/voices/run2_clean/"
                 "b1_2v_new_theme_attempt3/article.md")
OLD_SUPPORT_TEXTS_PATH = ("er014_output/four_type_observation_01/voices/run2_clean/"
                           "b1_2v_new_theme/b1_support_texts.json")
LEAKAGE_EVIDENCE_PATH = ("er014_output/four_type_observation_01/voices/run2_clean/"
                          "b1_2v_new_theme_attempt3/analytical_leakage_check_2v_attempt3.json")
LEDGER_PATH = "er014_output/four_type_observation_01/voices/research/verified_fact_ledger.txt"

OUT_BASE = "er014_output/four_type_observation_01/voices/audio/b1_2v"
OUT_B1B_DIR = f"{OUT_BASE}/b1b"
NARRATION_DIR = f"{OUT_B1B_DIR}/narration"
KP_DIR = f"{OUT_B1B_DIR}/key_phrases"
WEB_DIR = f"{OUT_BASE}/web"
WEB_SEG_DIR = f"{WEB_DIR}/segments"
COMMENT_REGEN_DIR = f"{OUT_BASE}/comment_regen"
COST_LOG_PATH = f"{OUT_BASE}/cost_log_raw_cont1.jsonl"  # 本タスク専用(run1のcost_log_raw.jsonlとは別集計)
PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0
BUDGET_JPY_CAP = 60.0  # 本タスク上限(委任文どおり)
ARTICLE_ID = "voices_ut_audio_completion_01_b1_2v"
EPISODE_WAV_NAME = "Voices_UT_Audio_Completion_01_B1_2V.wav"
COMMENT_CONTRACT_MAX_ATTEMPTS = 2  # 既存経路そのまま、最大2回(委任文どおり)

THEME = {"theme_id": ARTICLE_ID, "out_dir": OUT_BASE}
COMMENT_KEYS = ("preview", "comment_1", "comment_2", "comment_3", "comment_4")


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
# コスト計測(run1 driverと同一ロジック、本タスク専用ログのみ集計)
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
    print(f"[VOICES-2V-AUDIO-CONT1][cost] so far={jpy:.2f} JPY by_provider={by_provider} ({note})")
    if jpy > BUDGET_JPY_CAP:
        raise RuntimeError(f"[BUDGET_GUARD] cost so far {jpy:.2f} JPY > cap {BUDGET_JPY_CAP} JPY. Stopping ({note}).")
    return jpy


class HumanReviewLockStop(RuntimeError):
    """Human Review Lock発動時にSTOPするための専用例外(承認代行しない、
    er012_editorial_b_voices_3v_audio_trial_01.pyと同一パターン)。"""


def assert_not_locked(result: dict, segment_name: str) -> None:
    if isinstance(result, dict) and result.get("status") == "HUMAN_REVIEW_LOCKED":
        raise HumanReviewLockStop(
            f"[HUMAN_REVIEW_LOCK] segment={segment_name} でHuman Review Lockが発動しました。"
            f"承認代行はせず実行を中止します。詳細: {result}")


# ============================================================
# Step 0: Key Phrase音声(run1でtext選定[keywords_canonicalized.json]は
# 完了済みだが、音声(kp{rank}_en.wav/kp{rank}_ja_charon.wav)は未生成
# だったため生成する(Assembly[asm.load_b1_sources]がこれらのwavを必須と
# するため、run1到達点の欠落として本タスクで補う)。呼び出し規約は
# er012_editorial_b_voices_3v_audio_trial_01.py::run_key_phrase_tts()
# (同じB-Family Voices、最新の新規記事Key Phrase音声化前例)と同一
# (shared_narration.ensure_key_phrase_english_component/tts_gen.
# generate_charon_japanese_with_reading_safety、いずれも無変更)。
# Key Phraseのtext自体は再選定しない(run1の既存keywords_canonicalized.
# jsonをそのまま使う)。
# ============================================================
def step_key_phrase_audio() -> dict:
    existing_path = f"{OUT_B1B_DIR}/audit/kp_tts_results.json"
    if os.path.exists(existing_path):
        existing = load_json(existing_path)
        if all(v["english"].get("status") == "OK" and v["japanese"].get("status") == "OK"
               for v in existing.values()):
            print(f"[VOICES-2V-AUDIO-CONT1] 既存{existing_path}(全件OK)を再利用します"
                  f"(再実行のため、追加API呼び出しなし)。")
            return {int(k): v for k, v in existing.items()}

    kp_data = load_json(f"{KP_DIR}/keywords_canonicalized.json")
    kp_results = {}
    for item in sorted(kp_data["items"], key=lambda it: it["rank"]):
        rank = item["rank"]
        used_form = item["used_form"]
        ja_gloss = item["japanese_gloss"]
        ja_gloss_tts, ja_gloss_tts_fallback = tts_gen.resolve_key_phrase_ja_gloss_tts(item)
        print(f"[VOICES-2V-AUDIO-CONT1] Key Phrase {rank} 英語Component生成(Aoede、Master Audio Store経由): "
              f"{used_form!r}...")
        with cl.segment_context(f"kp{rank}_english"):
            en_r = shared_narration.ensure_key_phrase_english_component(
                tts_gen.tts_safe_kp_en(used_form), f"{NARRATION_DIR}/kp{rank}_en.wav")
        assert_not_locked(en_r, f"kp{rank}_english")
        print(f"[VOICES-2V-AUDIO-CONT1] Key Phrase {rank} 日本語meaning生成(Charon)...")
        with cl.segment_context(f"kp{rank}_japanese"):
            ja_r = tts_gen.generate_charon_japanese_with_reading_safety(
                ja_gloss_tts, f"{NARRATION_DIR}/kp{rank}_ja_charon.wav", tts_gen.expected_substring_ja(ja_gloss_tts),
                known_key_phrase_terms=[used_form])
        assert_not_locked(ja_r, f"kp{rank}_japanese")
        ja_r["display_gloss"] = ja_gloss
        ja_r["japanese_gloss_tts_fallback_derived"] = ja_gloss_tts_fallback
        kp_results[rank] = {"english": en_r, "japanese": ja_r}
        print(f"[VOICES-2V-AUDIO-CONT1] Key Phrase {rank}: en={en_r.get('status')} ja={ja_r.get('status')}")
    save_json(f"{OUT_B1B_DIR}/audit/kp_tts_results.json", kp_results)
    assert_budget_ok("after Key Phrase audio generation")
    return kp_results


# ============================================================
# Step 1: Comment 2再生成(既存の接続済みComment Contract経路、無変更)
# 冪等性: 本scriptがAssembly以降で例外停止し再実行された場合に、既に
# 成功しているComment再生成LLM呼び出しを不要に繰り返さないよう、
# 既存comment_2_regeneration.jsonがあればそれをそのまま再利用する
# (API呼び出しなし)。
# ============================================================
def step_comment_regeneration(article_text: str, old_support_texts: dict) -> tuple:
    existing_path = f"{OUT_BASE}/comment_2_regeneration.json"
    if os.path.exists(existing_path):
        record = load_json(existing_path)
        print(f"[VOICES-2V-AUDIO-CONT1][comment-regen] 既存{existing_path}を再利用します"
              f"(再実行のため、追加LLM呼び出しなし)。")
        return record["new_texts"], record["changed_flags"], record

    sections = b1prod.split_five_voice_sections(article_text)
    if sections is None:
        raise RuntimeError("[COMMENT_REGEN] split_five_voice_sections()がNoneを返しました"
                            "(記事構造が5 section想定と異なります、既存Gate、緩和不可)。")
    with open(LEDGER_PATH, encoding="utf-8") as f:
        ledger_text = f.read()

    attempts_log = []
    final_result = None
    for attempt in range(1, COMMENT_CONTRACT_MAX_ATTEMPTS + 1):
        out_dir = f"{COMMENT_REGEN_DIR}/attempt{attempt}"
        print(f"[VOICES-2V-AUDIO-CONT1][comment-regen] attempt={attempt} "
              f"run_comment_contract_for_new_theme(num_voices=2)...")
        result = runner_mod.run_comment_contract_for_new_theme(
            article_text, sections, 2, ledger_text, out_dir)
        overall = result["deviation"].get("overall_status")
        attempts_log.append({
            "attempt": attempt, "out_dir": out_dir,
            "support_status": result["support_status"],
            "deviation_overall_status": overall,
        })
        final_result = result
        if overall == "LEDGER_COMPLIANT":
            break
        print(f"[VOICES-2V-AUDIO-CONT1][comment-regen] attempt={attempt} "
              f"deviation_overall_status={overall}(LEDGER_COMPLIANTではないため、上限まで再試行)")

    new_support_texts = {k: (final_result["support"][k].get("text") or "") for k in COMMENT_KEYS}
    changed_flags = {k: (new_support_texts[k] != old_support_texts.get(k)) for k in COMMENT_KEYS}

    regeneration_record = {
        "reason": ("comment_2のTTSが挿入句 \"one after the other. Each\" を3回とも読み飛ばし"
                   "TRUE_CONTENT_MISMATCH -> Human Review Cost Guardで停止(前回run到達点)。"
                   "記事本文は変更せず、Comment 1-4+Preview(補助生成テキスト)を既存の接続済み"
                   "Comment Contract経路で再生成し、読み飛ばしを誘発した文言を解消できるか確認する。"
                   "同一テキストの再試行ではなく、既存経路による新規テキスト生成である"
                   "(Human Review Lockはcanonical_text_sha256差分により新版として扱われる、"
                   "approve_regenerate()は呼んでいない)。"),
        "max_attempts": COMMENT_CONTRACT_MAX_ATTEMPTS,
        "attempts": attempts_log,
        "attempts_used": len(attempts_log),
        "old_texts": {k: old_support_texts.get(k) for k in COMMENT_KEYS},
        "new_texts": new_support_texts,
        "changed_flags": changed_flags,
        "changed_segments": [k for k, v in changed_flags.items() if v],
        "unchanged_segments": [k for k, v in changed_flags.items() if not v],
    }
    save_json(f"{OUT_BASE}/comment_2_regeneration.json", regeneration_record)
    assert_budget_ok("after Comment Contract regeneration (preview/comment_1-4)")
    return new_support_texts, changed_flags, regeneration_record


# ============================================================
# Step 2: 変更されたsegmentのみ再TTS(run1と同一の呼び出し規約、
# style_prefix_override/disfluency_qa無変更)。未変更segmentは
# 既存wav・既存lock記録をそのまま再利用する(API呼び出しなし)。
# ============================================================
_SEGMENT_OUTER_RETRY_MAX = 2  # run1と同じ「初回+最大2回=合計3回」規約


def _call_with_segment_retry(name: str, gen_fn, *args, **kwargs) -> dict:
    attempts = []
    for outer_attempt in range(0, _SEGMENT_OUTER_RETRY_MAX + 1):
        r = gen_fn(*args, **kwargs)
        attempts.append({"outer_attempt": outer_attempt, "status": r.get("status")})
        if r.get("status") == "OK":
            if outer_attempt > 0:
                r["outer_retry_log"] = attempts
                print(f"[VOICES-2V-AUDIO-CONT1][segment-retry] {name}: outer_attempt={outer_attempt}でOK")
            return r
        print(f"[VOICES-2V-AUDIO-CONT1][segment-retry] {name}: outer_attempt={outer_attempt} status="
              f"{r.get('status')} reason={r.get('reason')}")
    r["outer_retry_log"] = attempts
    return r


def _lock_entry_if_already_resolved(name: str, text: str) -> dict | None:
    """冪等性: review_lock_state.json中のsegment=nameが、渡されたtextと同じ
    canonical_text_sha256でstate=RESOLVED/final_status=OKならそのまま返す
    (本scriptがAssembly以降で例外停止し再実行された場合に、既に成功して
    いるTTS呼び出しを不要に繰り返さないための安全網、API呼び出しなし)。
    ハッシュは@review_lock.guarded_generateが実際に見るtext(tts_safe変換後、
    generate_charon_englishへ渡すのと同一の文字列)で計算する(生の
    canonical_textでハッシュすると、変換で変わる文字[curly quote等]を含む
    segmentで誤って不一致になる)。"""
    lock_path = f"{OUT_B1B_DIR}/audit/review_lock_state.json"
    if not os.path.exists(lock_path):
        return None
    lock = load_json(lock_path)
    entry = lock.get(name)
    if not entry:
        return None
    transformed_text = tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(text))
    if entry.get("state") == "RESOLVED" and entry.get("final_status") == "OK" \
            and entry.get("canonical_text_sha256") == sha(transformed_text):
        return entry
    return None


def step_tts_changed_segments(new_support_texts: dict, changed_flags: dict, old_segments: dict) -> dict:
    results = {}
    for name in COMMENT_KEYS:
        if not changed_flags[name]:
            old_entry = dict(old_segments.get(name) or {})
            old_entry["reused_from_previous_run"] = True
            old_entry["canonical_text"] = new_support_texts[name]
            results[name] = old_entry
            print(f"[VOICES-2V-AUDIO-CONT1] {name}: テキスト変化なし、既存wav/lock記録を再利用(API呼び出しなし)")
            continue
        text = new_support_texts[name]
        already = _lock_entry_if_already_resolved(name, text)
        if already is not None:
            print(f"[VOICES-2V-AUDIO-CONT1] {name}: 新テキストで既にRESOLVED/OK(前回の本run実行分)、"
                  f"再実行のためAPI呼び出しをスキップし既存wavを再利用します。")
            last_attempts_log = already.get("last_attempts_log") or []
            last_attempt = last_attempts_log[-1] if last_attempts_log else {}
            results[name] = {"status": "OK", "path": already.get("wav_path"),
                              "canonical_text": text, "reused_from_this_run_prior_attempt": True,
                              "cumulative_tts_attempts": already.get("cumulative_tts_attempts"),
                              "cumulative_asr_calls": already.get("cumulative_asr_calls"),
                              "disfluency_checked": last_attempt.get("disfluency_checked"),
                              "attempts_log": last_attempts_log}
            continue
        print(f"[VOICES-2V-AUDIO-CONT1] {name}生成(Charon、新テキスト、既存generate_charon_english)...")
        with cl.segment_context(name):
            r = _call_with_segment_retry(
                name, voice01.generate_charon_english,
                tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(text)), f"{NARRATION_DIR}/{name}.wav",
                style_prefix_override=tts_gen.B1_PREVIEW_STYLE_PREFIX_CALM, disfluency_qa=True)
        r["canonical_text"] = text
        results[name] = r
    assert_budget_ok("after re-TTS of changed comment/preview segments")
    return results


def step_finalize_tts(comment_results: dict, old_full_segments: dict, kp_results: dict) -> dict:
    """run1が書いたtts_generation_results.jsonを、comment/preview分だけ
    差し替えて再保存する(他9 segment[topic_intro/headings/point_one/two/
    full_story_part1/2/tension_reflection/in_one_line]はComment再生成の
    対象外のため無変更、既存記録をそのまま維持)。key_phrasesは本タスクで
    実際に生成したkp_results(run1はstatus="OK"を実体生成なしに書いていた
    欠落があったため、実測結果で上書きする)。"""
    merged_segments = dict(old_full_segments)
    for name in COMMENT_KEYS:
        merged_segments[name] = comment_results[name]
    key_phrases_section = {
        str(rank): {"en": v["english"], "ja_charon": v["japanese"]}
        for rank, v in kp_results.items()
    }
    data = {"segments": merged_segments, "key_phrases": key_phrases_section}
    save_json(f"{OUT_B1B_DIR}/audit/tts_generation_results.json", data)
    all_status = {k: v.get("status") for k, v in merged_segments.items()}
    save_json(f"{OUT_B1B_DIR}/run_summary_tts.json", {"segment_status": all_status})
    print(f"[VOICES-2V-AUDIO-CONT1] TTS(差し替え分)完了。comment/preview segment_status="
          f"{ {k: all_status[k] for k in COMMENT_KEYS} }")
    return data, all_status


# ============================================================
# Step 3: Assembly(run1のstep_assemblyと同一primitive呼び出し、無変更)
# ============================================================
def step_assembly(voice_a: str, voice_b: str) -> tuple:
    os.makedirs(f"{OUT_B1B_DIR}/assembled", exist_ok=True)
    os.makedirs(f"{OUT_B1B_DIR}/audit", exist_ok=True)

    gate_record = {"gate": "verify_episode_audio_validation_gate", "result": None, "error": None}
    try:
        sources = asm.load_b1_sources(THEME)  # Production、無変更(Gate検証・shared assets copy含む)
        gate_record["result"] = "PASS"
    except RuntimeError as e:
        gate_record["result"] = "BLOCKED"
        gate_record["error"] = str(e)
        save_json(f"{OUT_BASE}/audio_validation.json", gate_record)
        raise

    mono, sr, _, _ = common.read_wav_float(f"{NARRATION_DIR}/{b1prod.EXTRA_SEGMENT_NAME}.wav")
    assert sr == common.SAMPLE_RATE
    sources["b1_segments"][b1prod.EXTRA_SEGMENT_NAME] = mono

    parts = asm.apply_b1_gain(sources)  # Production、無変更
    seq = b1prod.build_b1_voices_timeline(parts, voice_a, voice_b)  # Production、無変更
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

    tts_data = load_json(f"{OUT_B1B_DIR}/audit/tts_generation_results.json")
    segment_gate_statuses = {
        name: ("VALIDATED" if entry.get("status") == "OK" else entry.get("status"))
        for name, entry in tts_data.get("segments", {}).items()
    }
    gate_record["segment_statuses"] = segment_gate_statuses
    save_json(f"{OUT_BASE}/audio_validation.json", gate_record)

    print(f"[VOICES-2V-AUDIO-CONT1] Assembly status={summary['status']} duration={summary['duration_seconds']} "
          f"peak={summary['peak']} clipping={summary['clipping_detected']} gate={gate_record['result']}")
    return summary, result["timeline"]


# ============================================================
# Step 4: mp3変換(run1と同一、soundfile.write format=MP3、pip installなし)
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
# Step 5: player.html(run1のbuild_player_htmlと同一行構成ロジック、
# Statusノートにcomment_2再生成の事実を追記)
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
        return {"text": shared_narration_fixed_texts()["welcome"], "voice": charon,
                "audio": "welcome_charon", "sfx": False}
    if label == "Topic intro (Charon)":
        return {"text": f"Today's topic is {parts['title']}.", "voice": charon, "audio": "topic_intro", "sfx": False}
    if label == "Preview intro (Charon)":
        return {"text": shared_narration_fixed_texts()["preview_intro"], "voice": charon,
                "audio": "preview_intro_charon", "sfx": False}
    if label == "Preview (Charon)":
        return {"text": support_texts["preview"], "voice": charon, "audio": "preview", "sfx": False}
    if label == "Key phrases intro (Charon)":
        return {"text": shared_narration_fixed_texts()["key_phrases_intro"], "voice": charon,
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
        return {"text": shared_narration_fixed_texts()["full_story_intro"], "voice": charon,
                "audio": "full_story_intro_charon", "sfx": False}
    if label.startswith("Comment 1 "):
        return {"text": support_texts["comment_1"], "voice": charon, "audio": "comment_1", "sfx": False}
    if label.startswith("Comment 2 "):
        return {"text": support_texts["comment_2"] + " 【内部記録: comment_2はComment Contract経路で"
                        "再生成された新テキスト(下記comment_2_regeneration.json参照)】",
                "voice": charon, "audio": "comment_2", "sfx": False}
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


def shared_narration_fixed_texts():
    import er006_audio_cost_pilot_02_shared_narration as shared_narration
    return shared_narration.FIXED_ENGLISH_TEXTS


def rel_seg_url(stem: str) -> str:
    return f"./web/segments/{stem}.mp3"


def build_player_html(assemble_summary: dict, timeline: list, parts: dict, support_texts: dict,
                       voice_a: str, voice_b: str, comment_regen_record: dict) -> str:
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

    episode_url = "./web/episode.mp3"
    changed_note = "変更segment: " + ", ".join(comment_regen_record["changed_segments"]) if \
        comment_regen_record["changed_segments"] else "変更なし"
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>USER-TEST-AUDIO-COMPLETION-01-VOICES player(B1 2V, CONT1)</title>
<style>
{player_common.PLAYER_STANDARD_CSS}
</style>
<script>
{player_common.SEEK_SCRIPT}
</script>
</head><body>
<h1>Voices / Is personalized news good for us? — B1 2V 完成episode候補(CONT1)</h1>
<p class="note">
<b>Status: PARTIAL / USER TEST READY(Analytical Leakage残存)。PRODUCTION_WIRED未承認。</b><br>
2V(2 Voices)構成、完成episode(1本化wav、Standard同期)。管理ID:
USER-TEST-AUDIO-COMPLETION-01-VOICES(OPEN-151、継続CONT1)。duration={assemble_summary['duration_seconds']}s
peak={assemble_summary['peak']} clipping={assemble_summary['clipping_detected']}
headroom_safety_valve_applied={assemble_summary['headroom_safety_valve']['applied']}。
voice_a={voice_a} / voice_b={voice_b}(Narrator見出しは全てAoede固定)。<br>
<b>今回の変更点:</b> 前回run到達点でcomment_2がHuman Review Cost Guardにより停止していたため、
既存の接続済みComment Contract経路(run_comment_contract_for_new_theme、無変更)でComment
1-4+Previewを再生成した({changed_note})。記事本文(2V canonical candidate)は変更していない。
詳細: <a href="./comment_2_regeneration.json">comment_2_regeneration.json</a>。<br>
<b>既知の限界:</b> Analytical Leakage Check(voice_b/tension)が3attempt上限到達後もflagged
残存のまま採用している(ユーザー承認: Prompt改善・Gate緩和は行わずPARTIALのままユーザー
実検証へ進める)。詳細原文は
<a href="./comment_fact_safety_evidence.json">comment_fact_safety_evidence.json</a>参照。
</p>

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
# Step 6: 記事⇔音声一致確認 + Comment/Fact Safety evidence
# ============================================================
def step_consistency_and_evidence(article_text: str, parts: dict, support_texts: dict,
                                   tts_results: dict, timeline: list,
                                   comment_regen_record: dict) -> tuple:
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
        "note": ("Comment 1-4/Previewは記事本文(article_text)そのものではなく、記事本文を"
                 "context入力として生成された補助テキスト(Comment Contract経路)であり、"
                 "article_text中への逐語一致は仕様上想定していない(run1と同じ扱い)。"),
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
            "source": ("er012_b_family_production_runner_01.py::run_comment_contract_for_new_theme"
                       "(既存経路、無変更)による再生成(本タスクCONT1、comment_2のTTS読み飛ばし対応)。"
                       "詳細: comment_2_regeneration.json"),
            "support_status_at_generation": comment_regen_record["attempts"][-1]["support_status"],
            "deviation_overall_status_at_generation": comment_regen_record["attempts"][-1][
                "deviation_overall_status"],
            "regeneration_attempts_used": comment_regen_record["attempts_used"],
            "changed_segments": comment_regen_record["changed_segments"],
            "unchanged_segments": comment_regen_record["unchanged_segments"],
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

    article_text = open(ARTICLE_PATH, encoding="utf-8").read()
    parts = load_json(f"{OUT_B1B_DIR}/parts.json")  # run1既存生成、無変更のため再利用
    old_support_texts = load_json(OLD_SUPPORT_TEXTS_PATH)
    old_full_segments = load_json(f"{OUT_B1B_DIR}/audit/tts_generation_results.json")["segments"]
    voice_resolution = load_json(f"{OUT_BASE}/audit/voice_resolution.json")
    voice_a, voice_b = voice_resolution["voice_a"], voice_resolution["voice_b"]

    new_support_texts, changed_flags, comment_regen_record = step_comment_regeneration(
        article_text, old_support_texts)

    comment_results = step_tts_changed_segments(new_support_texts, changed_flags, old_full_segments)
    kp_results = step_key_phrase_audio()
    tts_data, all_status = step_finalize_tts(comment_results, old_full_segments, kp_results)

    assemble_summary, timeline = step_assembly(voice_a, voice_b)
    web_result = step_web_delivery(assemble_summary)
    player_path = build_player_html(assemble_summary, timeline, parts, new_support_texts,
                                     voice_a, voice_b, comment_regen_record)
    consistency, evidence = step_consistency_and_evidence(
        article_text, parts, new_support_texts, tts_data["segments"], timeline, comment_regen_record)

    jpy, by_provider = compute_cost_jpy_so_far()
    cost_summary = {
        "budget_jpy_cap_new_spend_only": BUDGET_JPY_CAP,
        "new_spend_jpy_total": round(jpy, 2),
        "new_spend_by_provider_jpy": by_provider,
        "note": ("Comment Contract再生成LLM(preview+comment_1-4、Ledger Deviation Check含む)+"
                 "変更segmentのみ再TTS一式。未変更segment(既存OK)はAPI呼び出しなし。"),
    }
    save_json(f"{OUT_BASE}/cost_summary_audio.json", cost_summary)

    print(f"[VOICES-2V-AUDIO-CONT1] DONE player={os.path.abspath(player_path)} "
          f"episode_mp3={web_result['episode_mp3']} duration={assemble_summary['duration_seconds']}s "
          f"new_spend_jpy={jpy:.2f}")


if __name__ == "__main__":
    main()
