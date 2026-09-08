# ============================================================
# er012_b_family_production_runner_01.py
# 管理ID: EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01
# ============================================================
# B-Family(Voices)専用のProduction正式初回経路(runner)。Trialスクリプト
# (er012_editorial_b_voices_trial_*.py)を一切importせず、以下のみを使う:
#   - er012_b_family_editorial_type_registry_01(Editorial Type registry)
#   - er012_b_family_voices_production_01(parser・Voice A/B TTS・
#     B-Family専用timeline builder)
#   - 既存Production共有関数(b1s.run_support_text/PREVIEW_ROLE、
#     voice01.generate_charon_english、point_headings.generate、
#     news_tail_fix.generate_news_narration_wide_margin、
#     shared_narration.ensure_all_shared_narration_b1、
#     asm.load_b1_sources/apply_b1_gain/assemble_with_timeline/
#     apply_headroom_safety_valve、vfl01.run_deviation_check)
#
# 入力: 既存の承認済み記事(Trial-07で生成・ユーザーが試聴確認済みの記事、
# er012_output/editorial_b_voices_trial_07/.../article.md)を読み取り専用の
# データとして使う(記事生成[Writer]自体はPhase 2待ちのためこのrunnerの
# 範囲外、Lane A共有Writerは一切呼ばない)。Key Phrase選定・カノニカライズ
# ("Key Phrase位置は現状維持のため変更なし"というユーザー承認どおり、本
# Phase 1では新規のKey Phrase選定ロジックを追加しない)は、同一記事に対して
# 既に検証済みのTrial-08出力(hash一致を都度検証したうえで再利用、Key
# Phrase選定自体はこのrunnerが新規に書くコードではないため対象外)を
# データとしてコピーする。Hook/Voice A/B/Tension/Closingの本文音声は、
# このrunnerが実際にProduction関数を呼んで新規生成する(Trial音声の
# コピー流用はしない)。
#
# cost > 200円でSTOP。Human Review Lockが発動した場合は承認代行せずSTOP
# して報告する(overrideしない)。
from __future__ import annotations

import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

# PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01: 正式リリース前はStandard同期を使う。
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

import hashlib

import audio_review_player as player_common
import er002_common as common
import er003_b1_p9a_audio as p9a
import er003_v1_b1_scaffold_01_generate as b1s
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_tts_generate as tts_gen
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er003_v1_sing01_point_headings_aoede as point_headings
import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl
import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er006_model_routing_contract_01 as routing
import er012_b_family_editorial_type_registry_01 as registry
import er012_b_family_voices_production_01 as b1prod

ARTICLE_PATH = "er012_output/editorial_b_voices_trial_07/b1b_run02_attempt2/article.md"
LEDGER_PATH = "er012_output/editorial_b_voices_trial_07/research/verified_fact_ledger.txt"
# Key Phrase選定+カノニカライズ済みの既存Production出力(同一記事、Trial-08で
# 生成)。Key Phraseの選定ロジック自体は本Phase 1の対象外(現状維持)のため、
# 同一記事であることをhash照合したうえでデータのみ再利用する。
KP_SOURCE_DIR = "er012_output/editorial_b_voices_trial_08_audio/p1/b1b"
KP_SOURCE_ARTICLE_PATH = f"{KP_SOURCE_DIR}/article.md"


# EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01 修正指示1回目:
# OPEN-121/OPEN-122安全機構配線後のruntime evidence再取得用に出力先を
# phase1_02へ切り替える(phase1_01ディレクトリは変更・上書きせず保持)。
OUT_DIR = "er012_output/editorial_b_family_production_phase1_02"
OUT_B1_DIR = f"{OUT_DIR}/b1b"
NARRATION_DIR = f"{OUT_B1_DIR}/narration"
COST_LOG_PATH = f"{OUT_DIR}/audit/raw_usage_log.jsonl"
PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0
BUDGET_JPY_CAP = 100.0

THEME = {"theme_id": "b_family_production_phase1_02", "out_dir": OUT_DIR}
EDITORIAL_TYPE = registry.get_editorial_type("b_family_voices")


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


def sha(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


# ============================================================
# コスト計測(既存Trialスクリプトと同一計算ロジック、本runner専用ログへ適用)
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
    print(f"[B-FAMILY-PROD-RUNNER][cost] so far={jpy:.2f} JPY by_provider={by_provider} ({note})")
    if jpy > BUDGET_JPY_CAP:
        raise RuntimeError(f"[BUDGET_GUARD] cost so far {jpy:.2f} JPY > cap {BUDGET_JPY_CAP} JPY. Stopping ({note}).")
    return jpy


# ============================================================
# Step 0: prepare(記事読み取り、5区切りparse)
# ============================================================
def prepare() -> dict:
    with open(ARTICLE_PATH, encoding="utf-8") as f:
        article_text = f.read()
    parts = b1prod.build_parts(article_text)
    os.makedirs(f"{OUT_B1_DIR}/audit", exist_ok=True)
    with open(f"{OUT_B1_DIR}/article.md", "w", encoding="utf-8") as f:
        f.write(article_text)
    save_json(f"{OUT_B1_DIR}/parts.json", parts)
    return {"article_text": article_text, "parts": parts}


# ============================================================
# Step 1: Voice可用性確認 + 解決(承認済み2声のみ、5声比較はしない)
# ============================================================
def voice_check(parts: dict) -> dict:
    sample_text = b1prod.first_n_sentences(parts["point_one_body"], 3)
    sample_dir = f"{OUT_DIR}/audit/voice_samples"
    results = b1prod.run_voice_availability_check(sample_text, sample_dir)
    save_json(f"{sample_dir}/voice_sample_results.json", {"sample_text": sample_text, "results": results})
    voice_a, voice_b, reasons = b1prod.resolve_voice_names(results)
    save_json(f"{OUT_DIR}/audit/voice_resolution.json",
              {"voice_a": voice_a, "voice_b": voice_b, "reasons": reasons})
    return {"voice_a": voice_a, "voice_b": voice_b, "reasons": reasons, "sample_results": results}


# ============================================================
# Step 2: Key Phrase(現状維持、既存Production出力を再利用。同一記事か
# text hashで確認したうえでのみコピーする)
# ============================================================
def reuse_key_phrases(article_text: str) -> dict:
    os.makedirs(f"{OUT_B1_DIR}/key_phrases", exist_ok=True)
    with open(KP_SOURCE_ARTICLE_PATH, encoding="utf-8") as f:
        source_article_text = f.read()
    hash_match = sha(article_text) == sha(source_article_text)
    if not hash_match:
        raise RuntimeError(
            "[TEXT_HASH_MISMATCH] Key Phrase再利用元(Trial-08)のarticle.mdと本runnerの入力記事の"
            "text hashが一致しないため、Key Phraseの再利用を中止します。")
    import shutil
    for name in os.listdir(f"{KP_SOURCE_DIR}/key_phrases"):
        shutil.copyfile(f"{KP_SOURCE_DIR}/key_phrases/{name}", f"{OUT_B1_DIR}/key_phrases/{name}")
    kp = load_json(f"{OUT_B1_DIR}/key_phrases/keywords_canonicalized.json")
    os.makedirs(NARRATION_DIR, exist_ok=True)
    for item in kp["items"]:
        rank = item["rank"]
        for wav_name in (f"kp{rank}_en", f"kp{rank}_ja_charon"):
            shutil.copyfile(f"{KP_SOURCE_DIR}/narration/{wav_name}.wav", f"{NARRATION_DIR}/{wav_name}.wav")
    result = {"hash_match": hash_match, "kp_ranks": [it["rank"] for it in kp["items"]],
              "reused_from": f"{KP_SOURCE_DIR} (EDITORIAL-B-FAMILY-VOICES-TRIAL-08-AUDIO、Key Phrase選定"
                              "自体はPhase 1の対象外、現状維持のためデータのみ再利用)"}
    save_json(f"{OUT_DIR}/audit/key_phrase_reuse.json", result)
    print(f"[B-FAMILY-PROD-RUNNER] Key Phrase再利用: hash_match={hash_match} kp_ranks={result['kp_ranks']}")
    return result


# ============================================================
# Step 3: Comment 1-4 + Preview(registryのComment Role辞書を使用、既存
# Production共有関数 b1s.run_support_text/PREVIEW_ROLE 経由、無変更)
# ============================================================
def run_scaffold(parts: dict, article_text: str, sections: dict, ledger_text: str) -> dict:
    client = b1s.get_client()
    model = routing.require_model("B1_SUPPORT", routing.SUPPORT_MODEL)
    comment_roles = EDITORIAL_TYPE["comment_roles"]

    print("[B-FAMILY-PROD-RUNNER] Comment 1(registry Role)生成開始...")
    c1_context = f"【これから聞く本文(The Question)】\n{sections['hook_body']}"
    c1 = b1s.run_support_text(client, comment_roles["comment_1"], c1_context, model=model)

    print("[B-FAMILY-PROD-RUNNER] Comment 2(registry Role)生成開始...")
    c2_context = (f"【すでに聞いた本文(The Question)】\n{sections['hook_body']}\n\n"
                  f"【これから聞く声の見出しのみ(内容は伏せる、この時点でこの文言を言わないこと)】\n"
                  f"One Voice heading: {parts['point_one_heading']}\n"
                  f"Another Voice heading: {parts['point_two_heading']}")
    c2 = b1s.run_support_text(client, comment_roles["comment_2"], c2_context, model=model)

    print("[B-FAMILY-PROD-RUNNER] Comment 3(registry Role)生成開始...")
    c3_context = (f"【One Voice(聞き終えた内容)】\n{parts['point_one_heading']}\n{parts['point_one_body']}\n\n"
                  f"【Another Voice(聞き終えた内容)】\n{parts['point_two_heading']}\n{parts['point_two_body']}\n\n"
                  f"【これから聞く内容の見出しのみ(内容は伏せる)】\n{sections['tension_heading']}")
    c3 = b1s.run_support_text(client, comment_roles["comment_3"], c3_context, model=model)

    print("[B-FAMILY-PROD-RUNNER] Comment 4(registry Role)生成開始...")
    c4_context = (f"【聞き終えた内容(視点の違いの深掘り)】\n{parts['tension_body']}\n\n"
                  f"【これから聞く結びの見出しのみ(内容は伏せる)】\n{sections['closing_heading']}")
    c4 = b1s.run_support_text(client, comment_roles["comment_4"], c4_context, model=model)

    print("[B-FAMILY-PROD-RUNNER] Preview(既存Production Prompt、無変更)生成開始...")
    preview_role = b1s.PREVIEW_ROLE.format(
        comment_1=c1.get("text") or "(生成失敗)", comment_2=c2.get("text") or "(生成失敗)")
    preview_context = f"【エピソード全文(参考、新しいFactの追加禁止)】\n{article_text}"
    preview = b1s.run_support_text(client, preview_role, preview_context, model=model)

    results = {"preview": preview, "comment_1": c1, "comment_2": c2, "comment_3": c3, "comment_4": c4}
    os.makedirs(f"{OUT_B1_DIR}/audit", exist_ok=True)
    with open(f"{OUT_B1_DIR}/b1_support_texts.json", "w", encoding="utf-8") as f:
        json.dump({k: v.get("text") for k, v in results.items()}, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_B1_DIR}/audit/b1_support_generation.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    support_concat = "\n\n".join(t for t in (v.get("text") for v in results.values()) if t)
    print("[B-FAMILY-PROD-RUNNER] Support Ledger Deviation Check(既存Production vfl01.run_deviation_check、"
          "無変更、monitoring専用)実行...")
    deviation = vfl01.run_deviation_check(client, ledger_text, support_concat)
    save_json(f"{OUT_B1_DIR}/audit/support_ledger_deviation.json", deviation["parsed"])

    return {"support": results, "support_status": {k: v.get("status") for k, v in results.items()},
            "deviation": deviation["parsed"]}


# ============================================================
# Step 4: TTS(既存Production関数 + 新規Voice A/B関数)
# ============================================================
def run_tts(parts: dict, support_texts: dict, voice_a: str, voice_b: str) -> dict:
    shared_narration.ensure_all_shared_narration_b1(NARRATION_DIR)  # Production、無変更(Master Audio Store経由)

    results = {}
    topic_intro_text = f"Today's topic is {parts['title']}."
    print("[B-FAMILY-PROD-RUNNER] topic_intro生成(Charon)...")
    with cl.segment_context("topic_intro"):
        results["topic_intro"] = voice01.generate_charon_english(
            tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(topic_intro_text)), f"{NARRATION_DIR}/topic_intro.wav")
    results["topic_intro"]["canonical_text"] = topic_intro_text
    assert_budget_ok("after topic_intro TTS")

    for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
        text = support_texts[name]
        print(f"[B-FAMILY-PROD-RUNNER] {name}生成(Charon、registry Comment Contract)...")
        with cl.segment_context(name):
            results[name] = voice01.generate_charon_english(
                tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(text)), f"{NARRATION_DIR}/{name}.wav",
                style_prefix_override=tts_gen.B1_PREVIEW_STYLE_PREFIX_CALM, disfluency_qa=True)
        results[name]["canonical_text"] = text
    assert_budget_ok("after preview/comment TTS")

    for name in ("point_one_heading", "point_two_heading"):
        text = parts[name]
        sc.assert_no_point_number_label(text, name)
        print(f"[B-FAMILY-PROD-RUNNER] {name}生成(Narrator=Aoede、Production point_headings.generate、無変更)...")
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
        print(f"[B-FAMILY-PROD-RUNNER] {name}生成({voice_name}、新規Voice A/B body関数)...")
        with cl.segment_context(name):
            results[name] = b1prod.generate_voice_body_wide_margin(
                tts_gen.tts_safe_news_en(text), f"{NARRATION_DIR}/{name}.wav", voice_name,
                # EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01 修正指示1回目:
                # point_one/point_two相当(Voice A/B本文)はA-Family既存Production
                # (er003_v1_n3_01_tts_generate.py 745-754行目)と同じOPEN-121/
                # OPEN-122対象4segmentの一員のため明示的にTrueを渡す(既定値と
                # 同じだが、呼び出し規約をここでも明示し監査可能にする)。
                enable_connected_speech_equivalence_layer=True, enable_repetition_qa=True)
        results[name]["canonical_text"] = text
    assert_budget_ok("after Voice A/B TTS")

    for name, text in (
        ("full_story_part1", parts["part1"]), ("full_story_part2", parts["part2"]),
        (b1prod.EXTRA_SEGMENT_NAME, parts["tension_body"]), ("in_one_line", parts["in_one_line"]),
    ):
        print(f"[B-FAMILY-PROD-RUNNER] {name}生成(Aoede、既存Production "
              "news_tail_fix.generate_news_narration_wide_margin、無変更)...")
        with cl.segment_context(name):
            results[name] = news_tail_fix.generate_news_narration_wide_margin(
                tts_gen.tts_safe_news_en(text), f"{NARRATION_DIR}/{name}.wav",
                # ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19: 既存A-Family B1と同じ
                # 呼び出し規約(in_one_lineのみdisfluency_qa対象、
                # er003_v1_n3_01_tts_generate.py 744行目と同一分岐)。これを渡さないと
                # asm.verify_episode_audio_validation_gate()のMISSING_MANDATORY_
                # DISFLUENCY_QAでAssemblyがブロックされる(実測、本Phase 1実行中に発見)。
                disfluency_qa=(name == "in_one_line"),
                # EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01 修正指示1回目:
                # er003_v1_n3_01_tts_generate.py 745-754行目と同一規約(OPEN-121/
                # OPEN-122の承認済み対象=full_story_part1/2・point_one・point_two の
                # 4segmentのみ)。B-FamilyのHook part1/2はA-Familyのfull_story_part1/2
                # に相当するためTrue。Tension(A-Familyに存在しない新規segment)と
                # Closing(in_one_line、A-Familyでも対象外)はA-Familyとの対称性を
                # 保つためFalseのまま(適用範囲を独自拡張しない)。
                enable_connected_speech_equivalence_layer=(
                    name in ("full_story_part1", "full_story_part2")),
                enable_repetition_qa=(
                    name in ("full_story_part1", "full_story_part2")))
        results[name]["canonical_text"] = text
    assert_budget_ok("after Hook/Tension/Closing TTS")

    return results


def finalize_tts_results(new_results: dict) -> dict:
    kp = load_json(f"{OUT_B1_DIR}/key_phrases/keywords_canonicalized.json")
    data = {"segments": new_results, "key_phrases": {}}
    for item in kp["items"]:
        rank = item["rank"]
        data["key_phrases"][str(rank)] = {
            "en": {"status": "OK", "reused_from": "Key Phrase reuse (Phase 1対象外、現状維持)"},
            "ja_charon": {"status": "OK", "reused_from": "Key Phrase reuse (Phase 1対象外、現状維持)"},
        }
    save_json(f"{OUT_B1_DIR}/audit/tts_generation_results.json", data)
    all_status = {k: v.get("status") for k, v in new_results.items()}
    save_json(f"{OUT_B1_DIR}/run_summary_tts.json", {"segment_status": all_status})
    print(f"[B-FAMILY-PROD-RUNNER] TTS完了。segment_status={all_status}")
    return data


# ============================================================
# Step 5: Assembly(B-Family専用timeline builder経由、既存Production
# primitiveは無変更)
# ============================================================
def run_assembly(voice_a: str, voice_b: str) -> dict:
    os.makedirs(f"{OUT_B1_DIR}/assembled", exist_ok=True)
    os.makedirs(f"{OUT_B1_DIR}/audit", exist_ok=True)

    try:
        sources = asm.load_b1_sources(THEME)  # Production、無変更(Gate検証・shared assets copy含む)
    except RuntimeError as e:
        print(f"[B-FAMILY-PROD-RUNNER] Assembly GATE_BLOCKED(override無し、報告のみ): {e}")
        summary = {"status": "GATE_BLOCKED", "error": str(e), "voice_a": voice_a, "voice_b": voice_b}
        save_json(f"{OUT_B1_DIR}/run_summary_assemble.json", summary)
        return summary

    mono, sr, _, _ = common.read_wav_float(f"{NARRATION_DIR}/{b1prod.EXTRA_SEGMENT_NAME}.wav")
    assert sr == common.SAMPLE_RATE
    sources["b1_segments"][b1prod.EXTRA_SEGMENT_NAME] = mono  # apply_b1_gain()はdictをgenericにiterateする

    parts = asm.apply_b1_gain(sources)  # Production、無変更
    seq = b1prod.build_b1_voices_timeline(parts, voice_a, voice_b)  # 新規Production(B-Family専用)
    result = asm.assemble_with_timeline(seq)  # Production、無変更
    headroom = asm.apply_headroom_safety_valve(result["assembled"], seq)  # Production、無変更
    assembled = headroom["assembled"]

    out_path = f"{OUT_B1_DIR}/assembled/B_Family_Production_Phase1_B1B.wav"
    save_json(f"{OUT_B1_DIR}/audit/gain_report.json", parts["gain_report"])
    save_json(f"{OUT_B1_DIR}/audit/timeline.json", result["timeline"])
    save_json(f"{OUT_B1_DIR}/audit/headroom_report.json", headroom["report"])
    common.write_wav_float(out_path, assembled, asm.SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], asm.SR)

    summary = {
        "status": "OK", "out_path": out_path, "duration_seconds": result["total_duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": asm.SR, "channels": 2, "headroom_safety_valve": headroom["report"],
        "voice_a": voice_a, "voice_b": voice_b,
    }
    save_json(f"{OUT_B1_DIR}/run_summary_assemble.json", summary)
    print(f"[B-FAMILY-PROD-RUNNER] Assembly status={summary['status']} duration={summary['duration_seconds']} "
          f"peak={summary['peak']} clipping={summary['clipping_detected']}")
    return summary


# ============================================================
# Step 6: 標準player.html(Gate 7 (a)〜(l)準拠、audio_review_player.py経由)
# ============================================================
def _row_info(label: str, parts: dict, support_texts: dict, voice_a: str, voice_b: str, kp_by_rank: dict) -> dict:
    charon = "Charon"
    if label == "Intro":
        return {"text": "音楽ジングル(ナレーションなし、読み上げなし)。Intro.mp3をそのまま再生。",
                "voice": None, "audio": None, "sfx": True}
    if label == "Outro (Charon)":
        return {"text": "音楽ジングル(ナレーションなし、読み上げなし)。outro.mp3をそのまま再生。"
                        "ラベルに(Charon)とあるが実際はTTS読み上げではない固定音源。",
                "voice": None, "audio": None, "sfx": True}
    if label.startswith("Notification ") or label.startswith("Point Notification"):
        return {"text": "効果音(読み上げなし)", "voice": None, "audio": None, "sfx": True}
    if label == "Welcome (Charon)":
        return {"text": shared_narration.FIXED_ENGLISH_TEXTS["welcome"], "voice": charon,
                "audio": f"{NARRATION_DIR}/welcome_charon.wav", "sfx": False}
    if label == "Topic intro (Charon)":
        return {"text": f"Today's topic is {parts['title']}.", "voice": charon,
                "audio": f"{NARRATION_DIR}/topic_intro.wav", "sfx": False}
    if label == "Preview intro (Charon)":
        return {"text": shared_narration.FIXED_ENGLISH_TEXTS["preview_intro"], "voice": charon,
                "audio": f"{NARRATION_DIR}/preview_intro_charon.wav", "sfx": False}
    if label == "Preview (Charon)":
        return {"text": support_texts["preview"], "voice": charon,
                "audio": f"{NARRATION_DIR}/preview.wav", "sfx": False}
    if label == "Key phrases intro (Charon)":
        return {"text": shared_narration.FIXED_ENGLISH_TEXTS["key_phrases_intro"], "voice": charon,
                "audio": f"{NARRATION_DIR}/key_phrases_intro_charon.wav", "sfx": False}
    if label.startswith("Key Phrase "):
        rank = int(label.split(" ")[-1])
        kp = kp_by_rank[rank]
        en = kp["used_form"]
        ja = kp["japanese_gloss"]
        ja_tts = kp.get("japanese_gloss_tts", ja)
        text = f"EN: {en}<br>JA(表示): {ja}" + ("" if ja_tts == ja else f"<br>JA(TTS用): {ja_tts}")
        return {"text": text, "voice": "Aoede(EN)/Charon(JA)",
                "audio": (f"{NARRATION_DIR}/kp{rank}_en.wav", f"{NARRATION_DIR}/kp{rank}_ja_charon.wav"),
                "sfx": False}
    if label == "Full story intro (Charon)":
        return {"text": shared_narration.FIXED_ENGLISH_TEXTS["full_story_intro"], "voice": charon,
                "audio": f"{NARRATION_DIR}/full_story_intro_charon.wav", "sfx": False}
    if label.startswith("Comment 1 "):
        return {"text": support_texts["comment_1"], "voice": charon, "audio": f"{NARRATION_DIR}/comment_1.wav", "sfx": False}
    if label.startswith("Comment 2 "):
        return {"text": support_texts["comment_2"], "voice": charon, "audio": f"{NARRATION_DIR}/comment_2.wav", "sfx": False}
    if label.startswith("Comment 3 "):
        return {"text": support_texts["comment_3"], "voice": charon, "audio": f"{NARRATION_DIR}/comment_3.wav", "sfx": False}
    if label.startswith("Comment 4 "):
        return {"text": support_texts["comment_4"], "voice": charon, "audio": f"{NARRATION_DIR}/comment_4.wav", "sfx": False}
    if label.startswith("Hook Part 1"):
        return {"text": parts["part1"], "voice": "Aoede", "audio": f"{NARRATION_DIR}/full_story_part1.wav", "sfx": False}
    if label.startswith("Hook Part 2"):
        return {"text": parts["part2"], "voice": "Aoede", "audio": f"{NARRATION_DIR}/full_story_part2.wav", "sfx": False}
    if label.startswith("Narrator: One Voice heading"):
        return {"text": parts["point_one_heading"], "voice": "Aoede (Narrator)",
                "audio": f"{NARRATION_DIR}/point_one_heading.wav", "sfx": False}
    if label.startswith("Voice A body"):
        return {"text": parts["point_one_body"], "voice": voice_a, "audio": f"{NARRATION_DIR}/point_one.wav", "sfx": False}
    if label.startswith("Narrator: Another Voice heading"):
        return {"text": parts["point_two_heading"], "voice": "Aoede (Narrator)",
                "audio": f"{NARRATION_DIR}/point_two_heading.wav", "sfx": False}
    if label.startswith("Voice B body"):
        return {"text": parts["point_two_body"], "voice": voice_b, "audio": f"{NARRATION_DIR}/point_two.wav", "sfx": False}
    if label.startswith("Tension:"):
        return {"text": parts["tension_body"], "voice": "Aoede",
                "audio": f"{NARRATION_DIR}/{b1prod.EXTRA_SEGMENT_NAME}.wav", "sfx": False}
    if label.startswith("Closing:"):
        return {"text": parts["in_one_line"], "voice": "Aoede", "audio": f"{NARRATION_DIR}/in_one_line.wav", "sfx": False}
    return {"text": "【未取得】このラベルに対応するscript textを本スクリプトのマッピングで特定できませんでした。",
            "voice": None, "audio": None, "sfx": False}


def build_player_html(assemble_summary: dict, timeline: list, parts: dict, support_texts: dict,
                       voice_a: str, voice_b: str, voice_resolution_reasons: dict) -> str:
    kp_data = load_json(f"{OUT_B1_DIR}/key_phrases/keywords_canonicalized.json")
    kp_by_rank = {item["rank"]: item for item in kp_data["items"]}
    abs_url = player_common.abs_file_url

    rows = []
    for entry in timeline:
        label = entry["part"]
        if label.startswith("pause_"):
            continue
        info = _row_info(label, parts, support_texts, voice_a, voice_b, kp_by_rank)
        sec = entry["start_seconds"]
        voice_disp = info["voice"] or ("SFX" if info["sfx"] else "—")
        if info["sfx"]:
            audio_html = "—"
        elif isinstance(info["audio"], tuple):
            audio_html = player_common.render_single_audio_html(tuple(abs_url(p) for p in info["audio"]))
        elif info["audio"]:
            audio_html = player_common.render_single_audio_html(abs_url(info["audio"]))
        else:
            audio_html = "—"
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

    episode_audio_url = abs_url(assemble_summary["out_path"])
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01 player</title>
<style>
{player_common.PLAYER_STANDARD_CSS}
</style>
<script>
{player_common.SEEK_SCRIPT}
</script>
</head><body>
<h1>EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01(B-Family Production Phase 1候補)</h1>
<p class="note">
完成episode(1本化wav、Standard同期、B1のみ)。Production正式runner
(er012_b_family_production_runner_01.py、Trialスクリプト非経由)による生成。
duration={assemble_summary['duration_seconds']}s peak={assemble_summary['peak']}
clipping={assemble_summary['clipping_detected']}
headroom_safety_valve_applied={assemble_summary['headroom_safety_valve']['applied']}。
voice_a={voice_a} / voice_b={voice_b}(Narrator見出しは全てAoede固定)。
一人称"I"はPhase 2待ち(機械的未保証、記事自体は既存承認済みTrial-07記事を再利用)。
各行に「Seek」「Segment名+voice」「実際に読み上げられたscript」「個別音声」を
同一行に配置(標準player形式、PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-FORMAT-11)。
</p>
{reason_note}

<h2>Episode audio</h2>
<audio id="episode_audio" class="main" controls preload="none" src="{episode_audio_url}"></audio>

<h2>タイムライン・全スクリプト(収録順、同一行にSeek+voice+script)</h2>
{timeline_table}

<h2>Key Phrase表(詳細、英語+日本語gloss)</h2>
{kp_table}

</body></html>
"""
    out_path = f"{OUT_DIR}/player.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path


# ============================================================
# main
# ============================================================
def main() -> None:
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    cl.install(COST_LOG_PATH)

    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    needs_prep = stage in ("prepare", "voice_check", "kp_reuse", "scaffold", "tts", "all")
    needs_voice_resolution = stage in ("tts", "assemble", "player", "all")

    if stage in ("prepare", "all"):
        prep = prepare()
    elif needs_prep:
        prep = {"article_text": open(ARTICLE_PATH, encoding="utf-8").read()}
        prep["parts"] = load_json(f"{OUT_B1_DIR}/parts.json")

    if stage in ("voice_check", "all"):
        vc = voice_check(prep["parts"])
        voice_a, voice_b, reasons = vc["voice_a"], vc["voice_b"], vc["reasons"]
    elif needs_voice_resolution:
        resolution = load_json(f"{OUT_DIR}/audit/voice_resolution.json")
        voice_a, voice_b, reasons = resolution["voice_a"], resolution["voice_b"], resolution["reasons"]

    if stage in ("kp_reuse", "all"):
        reuse_key_phrases(prep["article_text"])

    if stage in ("scaffold", "all"):
        sections = b1prod.split_five_voice_sections(prep["article_text"])
        with open(LEDGER_PATH, encoding="utf-8") as f:
            ledger_text = f.read()
        scaffold_result = run_scaffold(prep["parts"], prep["article_text"], sections, ledger_text)
        save_json(f"{OUT_DIR}/audit/scaffold_summary.json",
                  {"support_status": scaffold_result["support_status"],
                   "deviation_overall_status": scaffold_result["deviation"].get("overall_status")})
        assert_budget_ok("after scaffold")

    if stage in ("tts", "all"):
        support_texts = load_json(f"{OUT_B1_DIR}/b1_support_texts.json")
        new_results = run_tts(prep["parts"], support_texts, voice_a, voice_b)
        finalize_tts_results(new_results)

    if stage in ("assemble", "all"):
        assemble_summary = run_assembly(voice_a, voice_b)

    if stage in ("player", "all"):
        parts = load_json(f"{OUT_B1_DIR}/parts.json")
        support_texts = load_json(f"{OUT_B1_DIR}/b1_support_texts.json")
        assemble_summary = load_json(f"{OUT_B1_DIR}/run_summary_assemble.json")
        timeline_path = f"{OUT_B1_DIR}/audit/timeline.json"
        timeline = load_json(timeline_path) if os.path.exists(timeline_path) else []
        if assemble_summary.get("status") == "OK":
            player_path = build_player_html(assemble_summary, timeline, parts, support_texts, voice_a, voice_b, reasons)
            print(f"[B-FAMILY-PROD-RUNNER] player.html: {os.path.abspath(player_path)}")
        else:
            print(f"[B-FAMILY-PROD-RUNNER] Assembly未完了(status={assemble_summary.get('status')})のため"
                  "player.htmlは生成しません。")

    jpy, by_provider = compute_cost_jpy_so_far()
    print(f"[B-FAMILY-PROD-RUNNER] 完了(stage={stage})。累積cost={jpy:.2f} JPY by_provider={by_provider}")


if __name__ == "__main__":
    main()
