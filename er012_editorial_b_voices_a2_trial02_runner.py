# ============================================================
# er012_editorial_b_voices_a2_trial02_runner.py
# 管理ID: EDITORIAL-B-FAMILY-VOICES-A2-FREE-ADDRESS-COMPLETION-TRIAL-02(Lane B)
# ============================================================
# Step 1で生成したA2記事(er012_editorial_b_voices_a2_trial02_writer.py)
# を対象に、Step 2(Comment/Preview/Key Phrase生成、TTS、Assembly、
# player.html)を実装する。
#
# 既存Production関数の組み合わせ方針(ユーザー決定2026-09-08、Step 2指示):
#   - Voice A/Voice B本文: er012_b_family_voices_production_01
#     (b1prod).generate_voice_body_wide_margin() を使用(Phase 1と同一
#     関数。EDITORIAL-B-FAMILY-VOICES-A2-SLOWDOWN-AND-KEYPHRASE-REGEN-04
#     [ユーザー決定2026-09-08、B-A2-9への回答]以降は、標準A2の既存6%
#     slowdown仕様[style_prefix_override=n3_tts.A2_ENGLISH_STYLE_PREFIX_
#     SLOWER + n3_tts.apply_a2_slowdown_postprocessによる6% time-stretch]
#     を適用する[generate_voice_body_wide_margin_with_a2_slowdown()参照、
#     下記]。b1prodへは完全後方互換の追加引数[style_prefix_override、
#     既定None]のみを追加し、既存Production呼び出し[Phase 1含む]の挙動は
#     無変更)。
#   - Hook Part1/2・Narrator見出し(One Voice/Another Voice heading)・
#     Closing: er003_v1_n3_01_tts_generate(n3_tts)
#     .generate_a2_segment_with_slowdown()を無変更のまま使用(標準A2の
#     full_story_part1/2・point_one_heading/two_heading・in_one_lineと
#     同じ関数・同じA2_ENGLISH_STYLE_PREFIX_SLOWER)。
#   - Tension: 同関数を使うが、Phase 1のB1 Tension同様、connected
#     speech equivalence layer・repetition QAは対象拡張しない
#     (承認済み4segment集合[Hook Part1/2・Voice A・Voice B相当]を
#     超えない、Phase 1 runnerの既存判断を踏襲)。
#   - Comment 1〜4・Preview: er012_b_family_editorial_type_registry_01
#     (registry)のFINALIZE-11 Comment Role定義(無変更)を、
#     er003_v1_iran01_a2_generate(a2gen)の日本語Support生成経路
#     (run_support_text、SUPPORT_JA_PRINCIPLE使用)へ通す(役割定義は
#     FINALIZE-11のまま、出力言語だけを標準A2規約[日本語]に合わせる、
#     ユーザー決定B-A2-6)。Previewはa2gen.PREVIEW_ROLE(既存A2 Prompt、
#     無変更)をそのまま使う。
#   - Key Phrase: 選定(used_form/japanese_gloss)はPhase 1 B1と同一
#     (ユーザー決定B-A2-5、選定は変えない)。英語Componentは既にAoede
#     voiceで生成済みのPhase 1 B1音声ファイルをそのまま複製(再生成
#     しない、コスト削減)。日本語glossのみ、標準A2のAoede経路
#     (n3_tts.generate_a2_japanese_with_reading_safety)で新規生成する
#     (Phase 1のkp_ja_charon.wavはCharon音声のため、A2規約[Aoede]には
#     使えない)。
#
# Assembly: er003_v1_n3_01_assemble(asm)の低レベルprimitive
# (assemble_with_timeline/apply_headroom_safety_valve/apply_b1_gain/
# build_b1_key_phrase_blocks/verify_episode_audio_validation_gate)は
# 無変更で再利用する。asm.load_b1_sources()自体はB1固定のファイル名
# 規約(_charon suffix・"b1b"サブディレクトリ)にhard-codeされており
# A2のファイル名規約と非互換なため、本ファイル内に新規のA2版ローダー
# (load_a2_sources_for_b_family)を追加する(asm.pyは無変更)。
#
# Audio Validation Gateのlevel引数には、標準の"A2"文字列ではなく
# "B_FAMILY_A2"を渡す。理由: asm.verify_episode_audio_validation_gate()の
# 「A2 slowdown必須」チェックはlevel=="A2"の場合のみ発火し、segment名
# point_one/point_twoに対しslowdown証跡を要求する。しかしB-Familyの
# point_one/point_two相当はVoice A/B(Algieba/Erinome、上記の通り
# slowdown非対象)であり、標準A2のPoint本文とは別物である。level文字列を
# "A2"以外にすることで、この誤爆する必須チェックだけを回避し、他の
# 安全機構(VALIDATED/HUMAN_APPROVED状態チェック・asset hash staleness
# チェック)は無変更のまま有効にする。
from __future__ import annotations

import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

import audio_review_player as player_common
import er002_common as common
import er003_b1_p9a_audio as p9a
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_iran01_a2_generate as a2gen
import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_tts_generate as n3_tts
import er005_cost_logger as cl
import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er006_model_routing_contract_01 as routing
import er012_b_family_editorial_type_registry_01 as registry
import er012_b_family_voices_production_01 as b1prod
import er012_editorial_b_voices_a2_trial02_writer as writer

# EDITORIAL-B-FAMILY-VOICES-A2-CROSS-AUDIT-AND-FIX-03(Lane B): 既存
# writer.OUT_DIR("..._02")は変更しない(_02は保持のまま既存Trial-02
# 出力として残す)。本タスクの再生成先(_03)だけを環境変数で明示的に
# 上書きできるようにする(未指定時は従来どおりwriter.OUT_DIRのまま=
# 既存関数・既存呼び出し元の挙動は無変更)。
OUT_DIR = os.environ.get("A2_TRIAL02_OUT_DIR_OVERRIDE", writer.OUT_DIR)
A2_DIR = f"{OUT_DIR}/a2"
NARRATION_DIR = f"{A2_DIR}/narration"
KP_DIR = f"{A2_DIR}/key_phrases"
AUDIT_DIR = f"{A2_DIR}/audit"
COST_LOG_PATH = f"{AUDIT_DIR}/raw_usage_log.jsonl"
PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0
BUDGET_JPY_CAP = 150.0  # LLM(Step1)+TTS(Step2)合計。委任元指示の上限。

# 完成episode wavのファイル名も同様に環境変数で上書き可能にする(未指定
# 時は従来どおり"...Trial02.wav"のまま、既存_02の挙動は無変更)。
EPISODE_OUTPUT_BASENAME = os.environ.get(
    "A2_TRIAL02_EPISODE_BASENAME_OVERRIDE", "B_Family_A2_Free_Address_Trial02.wav")

# Phase 1 B1(承認済み、同一記事のKey Phrase選定元)。選定は変えない
# (ユーザー決定B-A2-5)。英語Componentも同一音声(Aoede)のため複製で再利用。
KP_SOURCE_DIR = "er012_output/editorial_b_family_production_phase1_02/b1b"

THEME = {"theme_id": "b_voices_a2_free_address_02", "out_dir": OUT_DIR}
EDITORIAL_TYPE = registry.get_editorial_type("b_family_voices")

AUDIO_GATE_LEVEL = "B_FAMILY_A2"  # 標準"A2"文字列は使わない(理由は上部コメント参照)

# EDITORIAL-B-FAMILY-VOICES-A2-CROSS-AUDIT-AND-FIX-03 B-2: 既存A2標準
# (er003_v1_n3_01_tts_generate.JAPANESE_TITLESパターン、及び動的タイトル
# 記事向けの既存前例er011_open112_trend_theme2_b_full_audio_trial_13.py
# の手法[原文タイトルの直訳、新しい主張・数字を追加しない]を踏襲)。
# TRIAL-02にはこのJapanese title segmentが欠落していた(横断監査で判明、
# 既存仕様どおり追加する)。
JAPANESE_TITLE_TEXT = "一つのオフィスに、働く場所についての二つの考え方"


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


# ============================================================
# コスト計測(Phase 1 runnerと同一ロジック)
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
    print(f"[A2-TRIAL02-RUNNER][cost] so far={jpy:.2f} JPY by_provider={by_provider} ({note})")
    if jpy > BUDGET_JPY_CAP:
        raise RuntimeError(f"[BUDGET_GUARD] cost so far {jpy:.2f} JPY > cap {BUDGET_JPY_CAP} JPY. Stopping ({note}).")
    return jpy


# ============================================================
# Step 2-1: Voice可用性確認(Phase 1と同一、b1prod無変更)
# ============================================================
def voice_check(parts: dict) -> dict:
    sample_text = b1prod.first_n_sentences(parts["point_one_body"], 3)
    sample_dir = f"{OUT_DIR}/audit/voice_samples"
    results = b1prod.run_voice_availability_check(sample_text, sample_dir)
    save_json(f"{sample_dir}/voice_sample_results.json", {"sample_text": sample_text, "results": results})
    voice_a, voice_b, reasons = b1prod.resolve_voice_names(results)
    save_json(f"{AUDIT_DIR}/voice_resolution.json", {"voice_a": voice_a, "voice_b": voice_b, "reasons": reasons})
    return {"voice_a": voice_a, "voice_b": voice_b, "reasons": reasons}


# ============================================================
# Step 2-2: Key Phrase(選定はPhase 1 B1と同一、英語Componentは複製、
# 日本語glossのみ標準A2 Aoede経路で新規生成)
# ============================================================
def reuse_key_phrases() -> dict:
    import shutil
    os.makedirs(KP_DIR, exist_ok=True)
    os.makedirs(NARRATION_DIR, exist_ok=True)
    shutil.copyfile(f"{KP_SOURCE_DIR}/key_phrases/keywords_canonicalized.json",
                     f"{KP_DIR}/keywords_canonicalized.json")
    kp = load_json(f"{KP_DIR}/keywords_canonicalized.json")

    results = {}
    for item in kp["items"]:
        rank = item["rank"]
        used_form = item["used_form"]
        ja_gloss = item["japanese_gloss"]
        ja_gloss_tts, ja_gloss_tts_fallback = n3_tts.resolve_key_phrase_ja_gloss_tts(item)

        # 修正(初回assemble Gate失敗を受けて): raw file copyではQA証跡
        # (disfluency_checked等)が失われ、Audio Validation Gateが
        # MISSING_MANDATORY_DISFLUENCY_QAでblockする(実測で確認)。標準
        # Production関数(shared_narration.ensure_key_phrase_english_
        # component、無変更)を呼ぶことで、同一used_form/voice=Aoede/
        # level=NoneならMaster Audio Store経由でcache hitし、QA証跡ごと
        # 正しく復元される(新規TTSは走らない想定、B-A2-5の「選定・音声は
        # 無変更」という前提とも整合する)。
        print(f"[A2-TRIAL02-RUNNER] Key Phrase {rank} 英語Component(Aoede、Master Audio Store経由、無変更経路)...")
        with cl.segment_context(f"kp{rank}_english"):
            en_r = shared_narration.ensure_key_phrase_english_component(
                n3_tts.tts_safe_kp_en(used_form), f"{NARRATION_DIR}/kp{rank}_en.wav")
        en_r["used_form"] = used_form

        print(f"[A2-TRIAL02-RUNNER] Key Phrase {rank} 日本語gloss生成(Aoede、標準A2経路): "
              f"表示用={ja_gloss!r} TTS用={ja_gloss_tts!r}...")
        with cl.segment_context(f"kp{rank}_japanese"):
            ja_r = n3_tts.generate_a2_japanese_with_reading_safety(
                ja_gloss_tts, f"{NARRATION_DIR}/kp{rank}_ja_aoede.wav", n3_tts.expected_substring_ja(ja_gloss_tts),
                max_extra_chars=30, known_key_phrase_terms=[used_form])
        ja_r["display_gloss"] = ja_gloss
        ja_r["japanese_gloss_tts_fallback_derived"] = ja_gloss_tts_fallback
        results[rank] = {"english": en_r, "japanese": ja_r}

    save_json(f"{AUDIT_DIR}/key_phrase_reuse_and_regen.json", results)
    return results


# ============================================================
# Step 2-3: Comment 1-4 + Preview(FINALIZE-11役割 + 標準A2日本語経路)
# ============================================================
def run_scaffold(parts: dict, article_text: str, ledger_text: str) -> dict:
    client = a2gen.get_client()
    model = routing.require_model("A2_SUPPORT", routing.SUPPORT_MODEL)
    comment_roles = EDITORIAL_TYPE["comment_roles"]

    print("[A2-TRIAL02-RUNNER] Comment 1(FINALIZE-11 role、標準A2日本語経路)生成開始...")
    c1_context = f"【これから聞く本文(The Question)】\n{parts['part1']}\n{parts['part2']}"
    c1 = a2gen.run_support_text(client, comment_roles["comment_1"], c1_context, model=model)

    print("[A2-TRIAL02-RUNNER] Comment 2(FINALIZE-11 role、標準A2日本語経路)生成開始...")
    c2_context = (f"【すでに聞いた本文(The Question)】\n{parts['part1']}\n{parts['part2']}\n\n"
                  f"【これから聞く声の見出しのみ(内容は伏せる、この時点でこの文言を言わないこと)】\n"
                  f"One Voice heading: {parts['point_one_heading']}\n"
                  f"Another Voice heading: {parts['point_two_heading']}")
    c2 = a2gen.run_support_text(client, comment_roles["comment_2"], c2_context, model=model)

    print("[A2-TRIAL02-RUNNER] Comment 3(FINALIZE-11 role、標準A2日本語経路)生成開始...")
    c3_context = (f"【One Voice(聞き終えた内容)】\n{parts['point_one_heading']}\n{parts['point_one_body']}\n\n"
                  f"【Another Voice(聞き終えた内容)】\n{parts['point_two_heading']}\n{parts['point_two_body']}\n\n"
                  f"【これから聞く内容の見出しのみ(内容は伏せる)】\n{parts['tension_heading']}")
    c3 = a2gen.run_support_text(client, comment_roles["comment_3"], c3_context, model=model)

    print("[A2-TRIAL02-RUNNER] Comment 4(FINALIZE-11 role、標準A2日本語経路)生成開始...")
    c4_context = (f"【聞き終えた内容(視点の違いの深掘り)】\n{parts['tension_body']}\n\n"
                  f"【これから聞く結びの見出しのみ(内容は伏せる)】\nClosing")
    c4 = a2gen.run_support_text(client, comment_roles["comment_4"], c4_context, model=model)

    print("[A2-TRIAL02-RUNNER] Preview(既存A2 Prompt a2gen.PREVIEW_ROLE、無変更)生成開始...")
    preview_role = a2gen.PREVIEW_ROLE.format(
        comment_1=c1.get("text") or "(生成失敗)", comment_2=c2.get("text") or "(生成失敗)")
    preview_context = f"【エピソード全文(参考、新しいFactの追加禁止)】\n{article_text}"
    preview = a2gen.run_support_text(client, preview_role, preview_context, model=model)

    results = {"preview": preview, "comment_1": c1, "comment_2": c2, "comment_3": c3, "comment_4": c4}
    os.makedirs(f"{A2_DIR}/audit", exist_ok=True)
    with open(f"{A2_DIR}/a2_support_texts.json", "w", encoding="utf-8") as f:
        json.dump({k: v.get("text") for k, v in results.items()}, f, ensure_ascii=False, indent=2)
    with open(f"{AUDIT_DIR}/a2_support_generation.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    support_concat = "\n\n".join(t for t in (v.get("text") for v in results.values()) if t)
    print("[A2-TRIAL02-RUNNER] Support Ledger Deviation Check(vfl01.run_deviation_check、無変更、monitoring専用)実行...")
    deviation = vfl01.run_deviation_check(client, ledger_text, support_concat)
    save_json(f"{AUDIT_DIR}/support_ledger_deviation.json", deviation["parsed"])

    return {"support": results, "support_status": {k: v.get("status") for k, v in results.items()},
            "deviation": deviation["parsed"]}


# ============================================================
# EDITORIAL-B-FAMILY-VOICES-A2-SLOWDOWN-AND-KEYPHRASE-REGEN-04:
# Voice A/B本文(point_one/point_two)へ標準A2の既存6% slowdown仕様を
# 適用する新規合成関数(ユーザー決定2026-09-08、B-A2-9への回答)。
#
# 既存関数を2つ、無変更のまま順に呼ぶだけの新規関数(新しいTTS/ASR/
# time-stretchロジックは一切追加しない):
#   1. b1prod.generate_voice_body_wide_margin(...): Voice A/B固有の声・
#      既存の全安全機構(ASR Cascade・disfluency gate・repetition QA・
#      connected speech equivalence layer・Human Review Lock)込みで
#      通常ペース音声を生成する(Phase 1と同一関数、本タスクで追加した
#      style_prefix_override引数のみ、標準A2と同じn3_tts.
#      A2_ENGLISH_STYLE_PREFIX_SLOWERを渡す)。
#   2. n3_tts.apply_a2_slowdown_postprocess(...): 標準A2のfull_story_
#      part1/2・point_one・point_two・in_one_line等と全く同じ関数
#      (無変更)。6% time-stretch(er008_a2_postprocess_slowdown_01.
#      A2_SLOWDOWN_PERCENT=6.0、無変更)+ post-process後のASR再検証を行う
#      (status!="OK"の場合は何もしない、既存の同関数のガードのまま)。
def generate_voice_body_wide_margin_with_a2_slowdown(name: str, tts_input: str, out_path: str,
                                                       voice_name: str) -> dict:
    result = b1prod.generate_voice_body_wide_margin(
        tts_input, out_path, voice_name,
        style_prefix_override=n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER,
        enable_connected_speech_equivalence_layer=True, enable_repetition_qa=True)
    return n3_tts.apply_a2_slowdown_postprocess(name, NARRATION_DIR, tts_input, result)


# ============================================================
# Step 2-4: TTS(既存Production関数 + 標準A2 slowdown関数の組み合わせ)
# ============================================================
def run_tts(parts: dict, support_texts: dict, voice_a: str, voice_b: str) -> dict:
    shared_narration.ensure_all_shared_narration_a2(NARRATION_DIR)  # Production、無変更(Master Audio Store経由)

    results = {}
    topic_intro_text = f"Today's topic is {parts['title']}."
    print("[A2-TRIAL02-RUNNER] topic_intro生成(Charon、B-Family Navigator規約維持)...")
    with cl.segment_context("topic_intro"):
        import er003_v1_sing01_voice01_generate as voice01
        results["topic_intro"] = voice01.generate_charon_english(
            n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(topic_intro_text)), f"{NARRATION_DIR}/topic_intro.wav")
    results["topic_intro"]["canonical_text"] = topic_intro_text
    assert_budget_ok("after topic_intro TTS")

    # EDITORIAL-B-FAMILY-VOICES-A2-CROSS-AUDIT-AND-FIX-03 B-2: 既存A2標準
    # (Topic intro英語タイトルの直後にJapanese titleを読み上げる、Aoede・
    # 日本語、n3_tts.generate_a2_japanese_with_reading_safetyは標準A2の
    # japanese_title生成と同一関数)。TRIAL-02で欠落していた分の追加。
    print(f"[A2-TRIAL02-RUNNER] japanese_title生成(Aoede、標準A2経路): {JAPANESE_TITLE_TEXT!r}...")
    with cl.segment_context("japanese_title"):
        results["japanese_title"] = n3_tts.generate_a2_japanese_with_reading_safety(
            JAPANESE_TITLE_TEXT, f"{NARRATION_DIR}/japanese_title.wav",
            n3_tts.expected_substring_ja(JAPANESE_TITLE_TEXT), max_extra_chars=30)
    assert_budget_ok("after japanese_title TTS")

    for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
        text = support_texts[name]
        print(f"[A2-TRIAL02-RUNNER] {name}生成(Aoede、日本語、標準A2経路)...")
        with cl.segment_context(name):
            results[name] = n3_tts.generate_a2_japanese_with_reading_safety(
                text, f"{NARRATION_DIR}/{name}.wav", n3_tts.expected_substring_ja(text))
    assert_budget_ok("after preview/comment TTS")

    for name in ("point_one_heading", "point_two_heading"):
        text = parts[name]
        import er003_v1_n3_01_scaffold_generate as sc
        sc.assert_no_point_number_label(text, name)
        tts_input = n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(text))
        print(f"[A2-TRIAL02-RUNNER] {name}生成(Narrator=Aoede、標準A2 slowdown経路)...")
        with cl.segment_context(name):
            results[name] = n3_tts.generate_a2_segment_with_slowdown(
                tts_input, f"{NARRATION_DIR}/{name}.wav", n3_tts.first_words(text, 3), max_extra_chars=20,
                style_prefix_override=n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER, disfluency_qa=True)
        results[name]["canonical_text"] = text
    assert_budget_ok("after Narrator heading TTS")

    for name, text, voice_name in (
        ("point_one", parts["point_one_body"], voice_a),
        ("point_two", parts["point_two_body"], voice_b),
    ):
        import er003_v1_n3_01_scaffold_generate as sc
        sc.assert_no_point_number_label(text, name)
        print(f"[A2-TRIAL02-RUNNER] {name}生成({voice_name}、Phase 1 b1prod関数+標準A2 6% "
              f"slowdown[EDITORIAL-B-FAMILY-VOICES-A2-SLOWDOWN-AND-KEYPHRASE-REGEN-04])...")
        with cl.segment_context(name):
            results[name] = generate_voice_body_wide_margin_with_a2_slowdown(
                name, n3_tts.tts_safe_news_en(text), f"{NARRATION_DIR}/{name}.wav", voice_name)
        results[name]["canonical_text"] = text
    assert_budget_ok("after Voice A/B TTS")

    for name, text, extend_qa in (
        ("full_story_part1", parts["part1"], True), ("full_story_part2", parts["part2"], True),
        (b1prod.EXTRA_SEGMENT_NAME, parts["tension_body"], False),
        ("in_one_line", parts["in_one_line"], False),
    ):
        tts_input = n3_tts.tts_safe_news_en(text)
        print(f"[A2-TRIAL02-RUNNER] {name}生成(Aoede、標準A2 slowdown経路)...")
        with cl.segment_context(name):
            results[name] = n3_tts.generate_a2_segment_with_slowdown(
                tts_input, f"{NARRATION_DIR}/{name}.wav", n3_tts.first_words(text),
                style_prefix_override=n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER,
                disfluency_qa=(name == "in_one_line"),
                enable_connected_speech_equivalence_layer=extend_qa,
                enable_repetition_qa=extend_qa)
        results[name]["canonical_text"] = text
    assert_budget_ok("after Hook/Tension/Closing TTS")

    return results


def finalize_tts_results(new_results: dict, kp_results: dict) -> dict:
    data = {"segments": new_results, "key_phrases": kp_results}
    save_json(f"{AUDIT_DIR}/tts_generation_results.json", data)
    all_status = {k: v.get("status") for k, v in new_results.items()}
    kp_status = {r: {"english": v["english"].get("status"), "japanese": v["japanese"].get("status")}
                 for r, v in kp_results.items()}
    save_json(f"{A2_DIR}/run_summary_tts.json", {"segment_status": all_status, "key_phrase_status": kp_status})
    print(f"[A2-TRIAL02-RUNNER] TTS完了。segment_status={all_status} kp_status={kp_status}")
    return data


# ============================================================
# Step 2-5: Assembly(A2版ローダーを新規追加、asm.py低レベルprimitiveは
# 無変更のまま再利用)
# ============================================================
def load_a2_sources_for_b_family(kp: dict) -> dict:
    asm.verify_episode_audio_validation_gate(A2_DIR, AUDIO_GATE_LEVEL)
    narration_dir = NARRATION_DIR

    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    notification = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    point_notification = p9a.load_and_resample_to_target(asm.POINT_NOTIFICATION_MP3_PATH)
    outro = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)

    narration = {}
    for name in ("welcome", "preview_intro", "key_phrases_intro", "full_story_intro"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono
    for name in ("num_one", "num_two", "num_three", "num_four", "num_five"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono
    mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/topic_intro.wav")
    assert sr == common.SAMPLE_RATE
    narration["topic_intro"] = mono
    # B-2(横断監査fix-03): 既存A2標準どおりTopic intro直後にJapanese titleを追加。
    mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/japanese_title.wav")
    assert sr == common.SAMPLE_RATE
    narration["japanese_title"] = mono

    b1_segments = {}
    for name in ("full_story_part1", "full_story_part2", "point_one", "point_two",
                  b1prod.EXTRA_SEGMENT_NAME, "in_one_line",
                  "comment_1", "comment_2", "comment_3", "comment_4", "preview",
                  "point_one_heading", "point_two_heading"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        b1_segments[name] = mono

    kp_items = sorted(kp["items"], key=lambda it: it["rank"])
    key_phrase_components, key_phrase_meanings = {}, {}
    for item in kp_items:
        rank = item["rank"]
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/kp{rank}_en.wav")
        assert sr == common.SAMPLE_RATE
        key_phrase_components[rank] = mono
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/kp{rank}_ja_aoede.wav")
        assert sr == common.SAMPLE_RATE
        key_phrase_meanings[rank] = mono

    return {"intro": intro, "notification": notification, "point_notification": point_notification, "outro": outro,
            "narration": narration, "b1_segments": b1_segments,
            "key_phrase_components": key_phrase_components, "key_phrase_meanings": key_phrase_meanings,
            "kp_items": kp_items}


def build_a2_voices_timeline(parts: dict, voice_a: str, voice_b: str) -> list:
    """b1prod.build_b1_voices_timeline()と同じ順序・同じpause定数を使うが、
    Comment/Preview/Key Phrase日本語glossがCharonではなくAoede(日本語)に
    なったことを反映し、ラベル文言のみ差し替えた新規関数(Lane B新規追加、
    既存build_b1_voices_timeline()自体は無変更)。pause秒数は標準A2の
    「Comment、英語→日本語」1.0秒・「日本語→英語」0.8秒(CURRENT_SPEC.md
    L356-357)と同じ値であるため、asm.AOEDE_TO_CHARON_PAUSE_SECONDS/
    CHARON_TO_AOEDE_PAUSE_SECONDSの数値をそのまま流用する(値は変更しない、
    ラベル名の意味だけがA2文脈では「Aoede英語→Aoede日本語」に読み替わる)。"""
    key_phrase_blocks = asm.build_b1_key_phrase_blocks(parts)
    b1 = parts["b1_segments"]

    seq = [
        ("Intro", parts["intro"]),
        ("Welcome (Charon)", parts["welcome"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Topic intro (Charon)", parts["topic_intro"]),
        ("pause_0.65", p9a.silence_stereo(0.65)),
        # B-2(横断監査fix-03): 既存A2標準(Hanshin/Health/Household等の
        # timeline.json実データで確認)どおり、英語タイトル直後に
        # Japanese title(Aoede、日本語)を追加。pause秒数も標準A2と同じ
        # (Topic intro→JP title: 0.65秒、JP title→Notification 1: 0.5秒)。
        ("Japanese title (Aoede, Japanese, A2)", parts["japanese_title"]),
        ("pause_0.5_title", p9a.silence_stereo(0.5)),
        ("Notification 1", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Preview intro (Charon)", parts["preview_intro"]),
        ("pause_0.65", p9a.silence_stereo(0.65)),
        ("Preview (Aoede, Japanese, A2)", b1["preview"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Notification 2", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Key phrases intro (Charon)", parts["key_phrases_intro"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
    ]
    kp_labels = tuple(f"Key Phrase {i}" for i in range(1, len(key_phrase_blocks) + 1))
    for label, block in zip(kp_labels, key_phrase_blocks):
        seq.append((label, block))

    seq += [
        ("Notification 3", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Full story intro (Charon)", parts["full_story_intro"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 1 (Aoede, Japanese, A2)", b1["comment_1"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Hook Part 1: The Question (Aoede, English, A2 slowdown, no heading)", b1["full_story_part1"]),
        ("pause_0.25_hook_internal", p9a.silence_stereo(0.25)),
        ("Hook Part 2: The Question (Aoede, English, A2 slowdown, no heading)", b1["full_story_part2"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 2 (Aoede, Japanese, A2, bridge to Voices)", b1["comment_2"]),
        ("pause_0.5_notification_entry", p9a.silence_stereo(asm.NOTIFICATION_ENTRY_PAUSE_SECONDS)),
        ("Point Notification (Voice A cue, existing SFX reuse)", parts["point_notification"]),
        ("Narrator: One Voice heading (Aoede, English, A2 slowdown)", b1["point_one_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(asm.HEADING_TO_BODY_PAUSE_SECONDS_B1)),
        (f"Voice A body ({voice_a}, A2 slowdown)", b1["point_one"]),
        ("pause_0.5_notification_entry", p9a.silence_stereo(asm.NOTIFICATION_ENTRY_PAUSE_SECONDS)),
        ("Point Notification (Voice B cue, existing SFX reuse)", parts["point_notification"]),
        ("Narrator: Another Voice heading (Aoede, English, A2 slowdown)", b1["point_two_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(asm.HEADING_TO_BODY_PAUSE_SECONDS_B1)),
        (f"Voice B body ({voice_b}, A2 slowdown)", b1["point_two"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 3 (Aoede, Japanese, A2)", b1["comment_3"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Tension: Where the Difference Comes From (Aoede, English, A2 slowdown, no heading)",
         b1[b1prod.EXTRA_SEGMENT_NAME]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 4 (Aoede, Japanese, A2)", b1["comment_4"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Closing: What the Seat Really Means (Aoede, English, A2 slowdown, no heading, In One Line)",
         b1["in_one_line"]),
        ("pause_0.8_in_one_line_to_outro", p9a.silence_stereo(asm.IN_ONE_LINE_TO_OUTRO_PAUSE_SECONDS)),
        ("Outro (Charon)", parts["outro"]),
    ]
    return seq


def run_assembly(voice_a: str, voice_b: str) -> dict:
    os.makedirs(f"{A2_DIR}/assembled", exist_ok=True)
    kp = load_json(f"{KP_DIR}/keywords_canonicalized.json")

    try:
        sources = load_a2_sources_for_b_family(kp)
    except RuntimeError as e:
        print(f"[A2-TRIAL02-RUNNER] Assembly GATE_BLOCKED(override無し、報告のみ): {e}")
        summary = {"status": "GATE_BLOCKED", "error": str(e), "voice_a": voice_a, "voice_b": voice_b}
        save_json(f"{A2_DIR}/run_summary_assemble.json", summary)
        return summary

    parts = asm.apply_b1_gain(sources)  # Production、無変更(preview/full_story_part1のRMSでgain合わせ)
    seq = build_a2_voices_timeline(parts, voice_a, voice_b)
    result = asm.assemble_with_timeline(seq)
    headroom = asm.apply_headroom_safety_valve(result["assembled"], seq)
    assembled = headroom["assembled"]

    out_path = f"{A2_DIR}/assembled/{EPISODE_OUTPUT_BASENAME}"
    save_json(f"{AUDIT_DIR}/gain_report.json", parts["gain_report"])
    save_json(f"{AUDIT_DIR}/timeline.json", result["timeline"])
    save_json(f"{AUDIT_DIR}/headroom_report.json", headroom["report"])
    common.write_wav_float(out_path, assembled, asm.SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], asm.SR)

    import er003_b1_p9a_audio as p9a_local
    summary = {
        "status": "OK", "out_path": out_path, "duration_seconds": result["total_duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a_local.peak(assembled), 5),
        "sample_rate": asm.SR, "channels": 2, "headroom_safety_valve": headroom["report"],
        "voice_a": voice_a, "voice_b": voice_b,
    }
    save_json(f"{A2_DIR}/run_summary_assemble.json", summary)
    print(f"[A2-TRIAL02-RUNNER] Assembly status={summary['status']} duration={summary['duration_seconds']} "
          f"peak={summary['peak']} clipping={summary['clipping_detected']}")
    return summary


# ============================================================
# Step 2-6: player.html(標準player形式、audio_review_player.py経由)
# ============================================================
def _row_info(label: str, parts: dict, support_texts: dict, voice_a: str, voice_b: str, kp_by_rank: dict) -> dict:
    charon = "Charon"
    if label == "Intro":
        return {"text": "音楽ジングル(ナレーションなし)。", "voice": None, "audio": None, "sfx": True}
    if label == "Outro (Charon)":
        return {"text": "音楽ジングル(ナレーションなし)。outro.mp3、固定音源。", "voice": None, "audio": None, "sfx": True}
    if label.startswith("Notification ") or label.startswith("Point Notification"):
        return {"text": "効果音(読み上げなし)", "voice": None, "audio": None, "sfx": True}
    if label == "Welcome (Charon)":
        return {"text": shared_narration.FIXED_ENGLISH_TEXTS["welcome"], "voice": charon,
                "audio": f"{NARRATION_DIR}/welcome.wav", "sfx": False}
    if label == "Topic intro (Charon)":
        return {"text": f"Today's topic is {parts['title']}.", "voice": charon,
                "audio": f"{NARRATION_DIR}/topic_intro.wav", "sfx": False}
    if label.startswith("Japanese title"):
        return {"text": JAPANESE_TITLE_TEXT, "voice": "Aoede(JA)",
                "audio": f"{NARRATION_DIR}/japanese_title.wav", "sfx": False}
    if label == "Preview intro (Charon)":
        return {"text": shared_narration.FIXED_ENGLISH_TEXTS["preview_intro"], "voice": charon,
                "audio": f"{NARRATION_DIR}/preview_intro.wav", "sfx": False}
    if label.startswith("Preview "):
        return {"text": support_texts["preview"], "voice": "Aoede(JA)",
                "audio": f"{NARRATION_DIR}/preview.wav", "sfx": False}
    if label == "Key phrases intro (Charon)":
        return {"text": shared_narration.FIXED_ENGLISH_TEXTS["key_phrases_intro"], "voice": charon,
                "audio": f"{NARRATION_DIR}/key_phrases_intro.wav", "sfx": False}
    if label.startswith("Key Phrase "):
        rank = int(label.split(" ")[-1])
        kp = kp_by_rank[rank]
        en = kp["used_form"]
        ja = kp["japanese_gloss"]
        ja_tts = kp.get("japanese_gloss_tts", ja)
        text = f"EN: {en}<br>JA(表示): {ja}" + ("" if ja_tts == ja else f"<br>JA(TTS用): {ja_tts}")
        return {"text": text, "voice": "Aoede(EN)/Aoede(JA)",
                "audio": (f"{NARRATION_DIR}/kp{rank}_en.wav", f"{NARRATION_DIR}/kp{rank}_ja_aoede.wav"),
                "sfx": False}
    if label == "Full story intro (Charon)":
        return {"text": shared_narration.FIXED_ENGLISH_TEXTS["full_story_intro"], "voice": charon,
                "audio": f"{NARRATION_DIR}/full_story_intro.wav", "sfx": False}
    if label.startswith("Comment 1 "):
        return {"text": support_texts["comment_1"], "voice": "Aoede(JA)", "audio": f"{NARRATION_DIR}/comment_1.wav", "sfx": False}
    if label.startswith("Comment 2 "):
        return {"text": support_texts["comment_2"], "voice": "Aoede(JA)", "audio": f"{NARRATION_DIR}/comment_2.wav", "sfx": False}
    if label.startswith("Comment 3 "):
        return {"text": support_texts["comment_3"], "voice": "Aoede(JA)", "audio": f"{NARRATION_DIR}/comment_3.wav", "sfx": False}
    if label.startswith("Comment 4 "):
        return {"text": support_texts["comment_4"], "voice": "Aoede(JA)", "audio": f"{NARRATION_DIR}/comment_4.wav", "sfx": False}
    if label.startswith("Hook Part 1"):
        return {"text": parts["part1"], "voice": "Aoede(EN, A2 slowdown)", "audio": f"{NARRATION_DIR}/full_story_part1.wav", "sfx": False}
    if label.startswith("Hook Part 2"):
        return {"text": parts["part2"], "voice": "Aoede(EN, A2 slowdown)", "audio": f"{NARRATION_DIR}/full_story_part2.wav", "sfx": False}
    if label.startswith("Narrator: One Voice heading"):
        return {"text": parts["point_one_heading"], "voice": "Aoede (Narrator, A2 slowdown)",
                "audio": f"{NARRATION_DIR}/point_one_heading.wav", "sfx": False}
    if label.startswith("Voice A body"):
        return {"text": parts["point_one_body"], "voice": voice_a, "audio": f"{NARRATION_DIR}/point_one.wav", "sfx": False}
    if label.startswith("Narrator: Another Voice heading"):
        return {"text": parts["point_two_heading"], "voice": "Aoede (Narrator, A2 slowdown)",
                "audio": f"{NARRATION_DIR}/point_two_heading.wav", "sfx": False}
    if label.startswith("Voice B body"):
        return {"text": parts["point_two_body"], "voice": voice_b, "audio": f"{NARRATION_DIR}/point_two.wav", "sfx": False}
    if label.startswith("Tension:"):
        return {"text": parts["tension_body"], "voice": "Aoede(EN, A2 slowdown)",
                "audio": f"{NARRATION_DIR}/{b1prod.EXTRA_SEGMENT_NAME}.wav", "sfx": False}
    if label.startswith("Closing:"):
        return {"text": parts["in_one_line"], "voice": "Aoede(EN, A2 slowdown)", "audio": f"{NARRATION_DIR}/in_one_line.wav", "sfx": False}
    return {"text": "【未取得】", "voice": None, "audio": None, "sfx": False}


def build_player_html(assemble_summary: dict, timeline: list, parts: dict, support_texts: dict,
                       voice_a: str, voice_b: str, voice_resolution_reasons: dict,
                       # EDITORIAL-B-FAMILY-VOICES-A2-SLOWDOWN-AND-KEYPHRASE-REGEN-04:
                       # 既定None(既存の02/03呼び出しはこの引数を渡さないため無変更)。
                       # 04呼び出しのみ、Key Phrase「stay put」の旧/新比較行を追加する。
                       stay_put_comparison: dict = None) -> str:
    kp_data = load_json(f"{KP_DIR}/keywords_canonicalized.json")
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

    stay_put_row_html = ""
    if stay_put_comparison:
        old_url = abs_url(stay_put_comparison["old_path"])
        new_url = abs_url(stay_put_comparison["new_path"])
        adopted = stay_put_comparison["adopted"]
        adopted_label = "新版(v2)を採用" if adopted == "new" else "旧版(v1)を維持"
        stay_put_row_html = f"""
<h2>Key Phrase 4「stay put」旧/新比較(EDITORIAL-B-FAMILY-VOICES-A2-SLOWDOWN-AND-KEYPHRASE-REGEN-04)</h2>
<table class="kp"><thead><tr><th>Key Phrase</th><th>旧(v1)/新(v2)、同一行に両方の再生ボタン</th>
<th>旧QA</th><th>新QA</th><th>採用</th></tr></thead>
<tbody>
<tr><td>{stay_put_comparison.get("used_form")}</td>
<td>旧: <audio controls preload="none" src="{old_url}"></audio> 新: <audio controls preload="none" src="{new_url}"></audio></td>
<td>{stay_put_comparison.get("old_qa_summary")}</td>
<td>{stay_put_comparison.get("new_qa_summary")}</td>
<td>{adopted_label}(承認記録: {stay_put_comparison.get("approval_record_path")})</td></tr>
</tbody></table>
"""

    episode_audio_url = abs_url(assemble_summary["out_path"])
    is_fix03 = "free_address_03" in OUT_DIR
    is_regen04 = "free_address_04" in OUT_DIR
    title_suffix = "-CROSS-AUDIT-AND-FIX-03" if is_fix03 else ("-SLOWDOWN-AND-KEYPHRASE-REGEN-04" if is_regen04 else "")
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>EDITORIAL-B-FAMILY-VOICES-A2-FREE-ADDRESS-COMPLETION-TRIAL-02{title_suffix} player</title>
<style>
{player_common.PLAYER_STANDARD_CSS}
</style>
<script>
{player_common.SEEK_SCRIPT}
</script>
</head><body>
<h1>EDITORIAL-B-FAMILY-VOICES-A2-FREE-ADDRESS-COMPLETION-TRIAL-02{title_suffix}(B-Family A2、Trial)</h1>
<p class="note">
<b>これはTrial出力であり、APPROVED_FOR_PRODUCTIONではない。</b>
完成episode(1本化wav、Standard同期、B-Family A2版のみ)。
duration={assemble_summary['duration_seconds']}s peak={assemble_summary['peak']}
clipping={assemble_summary['clipping_detected']}
headroom_safety_valve_applied={assemble_summary['headroom_safety_valve']['applied']}。
voice_a={voice_a} / voice_b={voice_b}
{("(標準A2の既存6% slowdown仕様を適用済み: style instruction[A2_ENGLISH_STYLE_"
  "PREFIX_SLOWER]+6% time-stretch post-process。ユーザー決定2026-09-08[B-A2-9への"
  "回答]により本rerunで新規適用した。)" if is_regen04 else
  "(標準ペース、A2 slowdown非対象、既存B-A2-9のUSER_DECISION_REQUIREDが未回答の"
  "ためVoice A/Bへのslowdown適用は本rerunでも実施していない)。")}
Narrator見出し・Hook・Tension・Closingは全てAoede英語(標準A2 slowdown適用)。
Comment 1-4・PreviewはAoede日本語(標準A2規約)。B1(Phase 1)との違いは声・言語の
み(5区切り構造・Voice A/B自体はB1と共通)。
{"横断監査(EDITORIAL-B-FAMILY-VOICES-A2-CROSS-AUDIT-AND-FIX-03)により、Topic "
 "intro(英語タイトル)直後のJapanese title(Aoede、日本語)を既存A2標準どおり"
 "追加した(Trial-02では欠落)。Key Phrase「stay put」の語末/t/が聞こえにくい"
 "件は、既存の標準Production Key Phrase経路[Master Audio Store・trim margin "
 "0.30秒・ASR false-rejection cascade済み]を正しく通過した状態[status=OK、"
 "asr_text=&quot;Stay put.&quot;、disfluency_checked=true]であることを確認済みで、"
 "既存の配線漏れではなく新failure mode疑いとしてSTOP(個別patch未実施、詳細は"
 "Report参照)。" if is_fix03 else ""}
{"EDITORIAL-B-FAMILY-VOICES-A2-SLOWDOWN-AND-KEYPHRASE-REGEN-04(ユーザー決定"
 "2026-09-08): (1)Voice A/Bへ標準A2の既存6% slowdownを適用し対象segmentを"
 "再生成。(2)Key Phrase「stay put」を既存の承認済み再生成経路で1回だけ"
 "再生成し、旧/新を下記で比較試聴可能にした。(3)Fact Checker REVIEW_REQUIRED"
 "(複合Voice帰属)は今回のA2に限りユーザー確認済みとして扱った(恒久運用では"
 "ない、承認記録は監査ディレクトリ参照)。" if is_regen04 else ""}
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
{stay_put_row_html}
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
    os.makedirs(AUDIT_DIR, exist_ok=True)
    cl.install(COST_LOG_PATH)

    stage = sys.argv[1] if len(sys.argv) > 1 else "all"

    parts = load_json(f"{A2_DIR}/parts.json")
    article_text = writer.load_text(f"{A2_DIR}/article.md")
    ledger_text = writer.load_text(writer.LEDGER_PATH)

    if stage in ("voice_check", "all"):
        vc = voice_check(parts)
        voice_a, voice_b, reasons = vc["voice_a"], vc["voice_b"], vc["reasons"]
    else:
        resolution = load_json(f"{AUDIT_DIR}/voice_resolution.json")
        voice_a, voice_b, reasons = resolution["voice_a"], resolution["voice_b"], resolution["reasons"]

    if stage in ("kp", "all"):
        kp_results = reuse_key_phrases()
    elif stage in ("tts", "assemble", "player"):
        kp_results = load_json(f"{AUDIT_DIR}/key_phrase_reuse_and_regen.json")
        kp_results = {int(k): v for k, v in kp_results.items()}

    if stage in ("scaffold", "all"):
        scaffold_result = run_scaffold(parts, article_text, ledger_text)
        save_json(f"{AUDIT_DIR}/scaffold_summary.json",
                  {"support_status": scaffold_result["support_status"],
                   "deviation_overall_status": scaffold_result["deviation"].get("overall_status")})
        assert_budget_ok("after scaffold")

    if stage in ("tts", "all"):
        support_texts = load_json(f"{A2_DIR}/a2_support_texts.json")
        new_results = run_tts(parts, support_texts, voice_a, voice_b)
        finalize_tts_results(new_results, kp_results)

    if stage in ("assemble", "all"):
        assemble_summary = run_assembly(voice_a, voice_b)

    if stage in ("player", "all"):
        support_texts = load_json(f"{A2_DIR}/a2_support_texts.json")
        assemble_summary = load_json(f"{A2_DIR}/run_summary_assemble.json")
        timeline_path = f"{AUDIT_DIR}/timeline.json"
        timeline = load_json(timeline_path) if os.path.exists(timeline_path) else []
        if assemble_summary.get("status") == "OK":
            player_path = build_player_html(assemble_summary, timeline, parts, support_texts, voice_a, voice_b, reasons)
            print(f"[A2-TRIAL02-RUNNER] player.html: {os.path.abspath(player_path)}")
        else:
            print(f"[A2-TRIAL02-RUNNER] Assembly未完了(status={assemble_summary.get('status')})のためplayer.html未生成")

    jpy, by_provider = compute_cost_jpy_so_far()
    print(f"[A2-TRIAL02-RUNNER] 完了(stage={stage})。累積cost={jpy:.2f} JPY by_provider={by_provider}")


if __name__ == "__main__":
    main()
