# ============================================================
# er011_open117_keyphrase_display_tts_separation_trial_02.py
# OPEN-117-KEYPHRASE-DISPLAY-TTS-SEPARATION-TRIAL-02 (Phase 2)
# ============================================================
# 目的: Phase 1(VALIDATED、OPEN-117-KEYPHRASE-DISPLAY-TTS-SEPARATION-
# TRIAL-01_REPORT.md)で確認した「表示用(japanese_gloss、辞書的な「～」表記を
# 許可)/TTS用(「なになに」変換)」の分離方式を、Theme 2(若者の旅行、B条件)の
# A2/B1で、Key Phrase選定から完成音声Assemblyまで、Production正式経路+
# Trialアダプタで確認する。
#
# Production変更: なし。Production関数(bk.build_user_message/bk.make_
# selector_fn/prod.run_production_selection_gate/sc.run_key_phrase_
# canonicalization/sc.run_key_phrase_redundancy_qa/tts_gen.generate_charon_
# japanese_with_reading_safety/tts_gen.generate_a2_japanese_with_reading_
# safety/shared_narration.ensure_key_phrase_english_component/asm.stage_
# assemble_b1/asm.stage_assemble_a2)はすべて無変更のまま直接呼び出す。
#
# Trialアダプタの範囲(このscript内だけの処理、Production非変更):
#   1. 選定Prompt(er003_v1_translator_briefs/b1_p2_keywords_l_prompt_
#      template.txt)のTrialコピーを実行時に構築する。gloss側の
#      placeholder禁止規約のうち「～」「〜」だけをTTS用変換の対象として
#      明示的に許可し(「…」は禁止のまま維持)、規約A(算用数字禁止・
#      漢数字使用)・key_phrase(英語)側の規約・他の選定基準はすべて
#      無変更のまま残す。sc.run_key_phrase_selection()自体はテンプレート
#      pathを引数化していないため、bk.load_prompt_template(path=...)の
#      path引数を使い、bk/prod配下のProduction関数を直接同じ手順で呼ぶ
#      薄いTrial限定wrapper(trial_run_key_phrase_selection/trial_run_
#      key_phrases)を用意する(monkeypatchは使わない)。
#   2. 選定・canonicalization結果のjapanese_gloss(表示用)から、規則変換
#      (文頭または読点「、」直後の「～」「〜」→「なになに」、Phase 1で
#      検証済みの変換)でTTS用テキストを導出し、対応表を保存する。それ
#      以外の位置に「～」「〜」「…」が残っていれば変換せず、Production
#      のplaceholder gate(er003_audio_tts_asr_safety.detect_gloss_
#      placeholder_notation、既存のtts_gen.generate_*_with_reading_safety
#      内部で自動的に適用される)にそのまま渡してブロックさせる(ゲートを
#      弱めない)。
#   3. 記事本文が変わらない13/14 non-Key-Phrase segment(Preview・
#      Comment1-4・Full Story・Point・In One Line・topic_intro・
#      [A2のみ]japanese_title)は、Trial-13(review_lock RESOLVED確認済み)
#      のwavファイル+tts_generation_results.jsonエントリをそのまま
#      コピー再利用し、生成関数の呼び出し自体を行わない(再TTSしない)。
#      Key Phrase(英語Component・日本語gloss)は、選定が変わるため常に
#      新規生成する。
#
# 到達してよいStatus: VALIDATED / REJECTED / USER_DECISION_REQUIRED
# (+完成音声はUSER_FINAL_AUDIO_REVIEW_REQUIRED)。APPROVED_FOR_PRODUCTION・
# PRODUCTION_WIRED禁止。Gate/Human Review Lockで停止した場合、override・
# fallback追加・上限緩和は一切行わずSTOPする(D4。片方のlevelが止まっても
# 他方は独立実行可)。

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er003_audio_tts_asr_safety as safety
import er003_b1_p2_keywords as bk
import er003_key_words_production as prod
import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_tts_generate as tts_gen
import er005_cost_logger as cl
import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er006_model_routing_contract_01 as routing
import er011_key_phrase_set_redundancy_qa_01 as redundancy_qa

THEME_ID = "open117_keyphrase_display_tts_separation_trial_02"
OUT_DIR = f"er011_output/{THEME_ID}"

TRIAL13_DIR = "er011_output/open112_trend_theme2_b_full_audio_trial_13"

# Trial-13スクリプト(er011_open112_trend_theme2_b_full_audio_trial_13.py)
# で実行時にtts_gen.JAPANESE_TITLESへ追記された値をそのまま複製する
# (japanese_titleは記事本文以外の独立ソースが無いため、再利用segmentの
# canonical_text検証にのみ使う。tts_gen.JAPANESE_TITLESへの追記は行わない
# = このsegmentは新規生成せずコピー再利用するだけなので不要)。
JAPANESE_TITLE_A2 = "「ゆっくりした旅」を求める若い世代、旅の計画はまだ短い"

LEVELS = {
    "b1b": {
        "source_level": "B1-B(N3-01, direct generation)",
        "process": "B1_SUPPORT",
        "support_file": "b1_support_texts.json",
        "reused_segments": [
            "topic_intro", "preview", "comment_1", "comment_2", "comment_3", "comment_4",
            "point_one_heading", "point_two_heading", "full_story_part1", "full_story_part2",
            "point_one", "point_two", "in_one_line",
        ],
    },
    "a2": {
        "source_level": "A2(V2改1, N3-01)",
        "process": "A2_SUPPORT",
        "support_file": "a2_support_texts.json",
        "reused_segments": [
            "topic_intro", "japanese_title", "preview", "comment_1", "comment_2", "comment_3",
            "comment_4", "point_one_heading", "point_two_heading", "full_story_part1",
            "full_story_part2", "point_one", "point_two", "in_one_line",
        ],
    },
}


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def sha(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


# ============================================================
# Step 0: Trial選定Prompt(gloss側のplaceholder禁止のうち「～」「〜」だけ許可)
# ============================================================
_ORIGINAL_GLOSS_RULE_LINE = (
    "日本語グロスには「～」「〜」「…」のようなプレースホルダー記号を一切使わないでください。"
    "動詞句などで目的語を省略した言い方にしたい場合は、日本語として自然な言い切りの形"
    "(例: 「～を示す」ではなく「示す、指し示す」)へ書き換えてください。日本語グロスに数字を"
    "含める場合は、算用数字(1、2、3…)ではなく漢数字(一、二、三…)で書いてください。"
)
_TRIAL_GLOSS_RULE_LINE = (
    "日本語グロスでは、動詞句などで目的語を省略した言い方にしたい場合、「～」「〜」を使った"
    "辞書的な表記(例: 「～を示す」)を使ってもかまいません(OPEN-117-KEYPHRASE-DISPLAY-TTS-"
    "SEPARATION-TRIAL-02: 表示用とTTS読み上げ用テキストを分離する検証のため、この記号だけ"
    "許可します。実際の読み上げでは別途変換されます)。「…」のようなプレースホルダー記号は"
    "これまでどおり使わないでください。日本語グロスに数字を含める場合は、算用数字"
    "(1、2、3…)ではなく漢数字(一、二、三…)で書いてください。"
)


def build_trial_selector_prompt_template() -> str:
    """Production選定Prompt(bk.PROMPT_TEMPLATE_PATH)を読み込み、gloss側の
    placeholder禁止規約1文だけをTrial用に差し替えたコピーを返す(規約A
    [漢数字]・他の選定基準・英語key_phrase側の規約は無変更)。ファイル
    自体は書き換えず、メモリ上の文字列だけを差し替える。"""
    original = bk.load_prompt_template()
    if _ORIGINAL_GLOSS_RULE_LINE not in original:
        raise RuntimeError(
            "Production選定Prompt(b1_p2_keywords_l_prompt_template.txt)の想定文言が"
            "見つかりません。テンプレートが変更された可能性があるためSTOPします。")
    trial_template = original.replace(_ORIGINAL_GLOSS_RULE_LINE, _TRIAL_GLOSS_RULE_LINE, 1)
    assert trial_template != original
    # 差分がこの1文の置換だけであることを機械的に確認する(str.replace(old,new,1)は
    # 構造的に最初の1箇所だけを置換するため、置換箇所を取り除いた残り全体が
    # 完全に一致することを確認すれば十分。difflibのSequenceMatcherは置換前後の
    # テキストに共通の部分文字列があると内部でさらに細かくchunk分割することが
    # あり、この用途には不向きなため使わない)。
    if original.replace(_ORIGINAL_GLOSS_RULE_LINE, "", 1) != trial_template.replace(_TRIAL_GLOSS_RULE_LINE, "", 1):
        raise RuntimeError("Trial選定Promptの差分が想定外です(gloss規約1文の置換以外に差分がある"
                           "可能性)。STOPします。")
    return trial_template


# ============================================================
# Step 1: Key Phrase選定(Trial限定の薄いwrapper、Production関数を直接
# 同じ手順で呼ぶ。monkeypatchは使わない)+ canonicalization + redundancy QA
# (canonicalization/redundancy QAはProduction関数[sc.*]をそのまま呼ぶ)
# ============================================================
def trial_run_key_phrase_selection(article_text: str, out_dir: str, article_id: str, source_level: str,
                                    trial_template: str, process: str = None,
                                    diagnostic_note: str = None) -> dict:
    """sc.run_key_phrase_selection()と同一の手順(bk.build_user_message→
    prod.run_production_selection_gate→runtime_metadata保存)だが、
    template引数だけをTrialコピーに差し替える。sc.run_key_phrase_selection()
    自体がtemplateを外部から選べない(bk.load_prompt_template()を内部で
    無引数のまま呼ぶ)ため、この呼び出しに限りsc.run_key_phrase_selection()
    を経由せず、bk/prod配下のProduction関数を直接同じ順序で呼ぶ。"""
    os.makedirs(out_dir, exist_ok=True)
    user_message = bk.build_user_message(article_text, template=trial_template)
    if diagnostic_note:
        user_message = user_message + "\n\n" + diagnostic_note
    with open(f"{out_dir}/keywords_selector_prompt.txt", "w", encoding="utf-8") as f:
        f.write(user_message)

    def make_selector_factory():
        model = routing.require_model(process, routing.SUPPORT_MODEL) if process else None
        return bk.make_selector_fn(user_message, model=model)

    parsed, status, attempts, model_id, response_id = prod.run_production_selection_gate(
        article_id, make_selector_factory, article_text,
        strategy_id=prod.STANDARD_STRATEGY_ID, max_attempts=1,
    )
    runtime_metadata = {
        "article_id": article_id, "strategy_id": prod.STANDARD_STRATEGY_ID, "source_level": source_level,
        "record_status": "PROTOTYPE", "approval_status": "NOT_APPROVED",
        "model": bk.SELECTOR_MODEL, "reasoning_effort": bk.SELECTOR_REASONING_EFFORT,
        "final_status": status, "model_id": model_id, "response_id": response_id,
        "attempts_detail": [{k: v for k, v in a.items() if k != "raw_text"} for a in attempts],
        "trial_note": "OPEN-117-KEYPHRASE-DISPLAY-TTS-SEPARATION-TRIAL-02: 選定Prompt"
                      "(Trialコピー)は、gloss側のplaceholder禁止規約のうち「～」「〜」だけを"
                      "明示的に許可している(「…」は禁止のまま、規約A[漢数字]・他の選定基準は"
                      "無変更)。選定ロジック本体(bk.make_selector_fn/prod.run_production_"
                      "selection_gate)はProduction関数のまま無変更。",
    }
    with open(f"{out_dir}/keywords_runtime_metadata.json", "w", encoding="utf-8") as f:
        json.dump(runtime_metadata, f, ensure_ascii=False, indent=2)

    result = {"status": status, "parsed": parsed}
    if status != "KEY_WORDS_STRUCTURE_PASS":
        return result
    result["original_items"] = parsed["items"]
    return result


def trial_run_key_phrases(article_text: str, out_dir: str, article_id: str, source_level: str,
                           trial_template: str, process: str = None) -> dict:
    """sc.run_key_phrases()と同一のretryループ構造(選定→canonicalization→
    redundancy QA、NGなら選定からやり直し、最大sc.KEY_PHRASE_REDUNDANCY_
    RETRY_MAX回)だが、選定にtrial_run_key_phrase_selection()を使う点だけ
    異なる。canonicalization・redundancy QAはsc.*(Production関数)を
    無変更のまま呼ぶ。"""
    redundancy_retry_log = []
    diagnostic_note = None
    for attempt in range(0, sc.KEY_PHRASE_REDUNDANCY_RETRY_MAX + 1):
        sel = trial_run_key_phrase_selection(article_text, out_dir, article_id, source_level, trial_template,
                                              process=process, diagnostic_note=diagnostic_note)
        if sel["status"] != "KEY_WORDS_STRUCTURE_PASS":
            return {"selection": sel, "canonicalization": None, "redundancy_qa": None,
                    "redundancy_retry_log": redundancy_retry_log}
        canon = sc.run_key_phrase_canonicalization(article_text, sel["original_items"], out_dir, article_id,
                                                    process=process)
        if canon["status"] not in ("CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
            return {"selection": sel, "canonicalization": canon, "redundancy_qa": None,
                    "redundancy_retry_log": redundancy_retry_log}

        merged_items = canon["merged"]["items"]
        redundancy = sc.run_key_phrase_redundancy_qa(article_text, merged_items, out_dir, article_id,
                                                       process=process)
        redundancy_retry_log.append({"attempt": attempt, "status": redundancy["status"],
                                      "duplicate_pairs": redundancy["duplicate_pairs"]})

        if redundancy["status"] != "REDUNDANCY_NG":
            return {"selection": sel, "canonicalization": canon, "redundancy_qa": redundancy,
                    "redundancy_retry_log": redundancy_retry_log, "redundancy_retry_attempts": attempt}

        if attempt >= sc.KEY_PHRASE_REDUNDANCY_RETRY_MAX:
            return {"selection": sel, "canonicalization": canon, "redundancy_qa": redundancy,
                    "redundancy_retry_log": redundancy_retry_log, "redundancy_retry_attempts": attempt,
                    "status": "NG_REVIEW_REQUIRED"}

        items_by_rank = {it["rank"]: it for it in merged_items}
        diagnostic_note = redundancy_qa.build_redundancy_diagnostic_note(
            redundancy["duplicate_pairs"], items_by_rank)
        print(f"[OPEN117-TRIAL-02] Key Phrase Set Redundancy QA NG(重複ペア: "
              f"{redundancy['duplicate_pairs']})。選定からやり直します"
              f"(retry {attempt + 1}/{sc.KEY_PHRASE_REDUNDANCY_RETRY_MAX})...")

    raise RuntimeError("trial_run_key_phrases: 予期しないループ終了")


# ============================================================
# Step 2: 表示用gloss -> TTS用テキストへの規則変換(Phase 1で検証済み)
# ============================================================
# 文頭、または読点「、」の直後にある「～」「〜」だけを「なになに」へ変換する。
# それ以外の位置の「～」「〜」、および「…」は変換しない(Productionの
# placeholder gate[detect_gloss_placeholder_notation]へそのまま渡し、
# 既存どおりブロックさせる。ゲートを弱めない)。
_LEADING_TILDE_RE = re.compile(r"(?:^|(?<=、))[～〜]")


def convert_display_gloss_to_tts_text(display_gloss: str) -> str:
    return _LEADING_TILDE_RE.sub("なになに", display_gloss or "")


def build_kp_display_tts_map(merged_items: list) -> list:
    rows = []
    for item in sorted(merged_items, key=lambda it: it["rank"]):
        display_gloss = item["japanese_gloss"]
        tts_text = convert_display_gloss_to_tts_text(display_gloss)
        placeholder_check = safety.detect_gloss_placeholder_notation(tts_text)
        rows.append({
            "rank": item["rank"], "key_phrase": item["key_phrase"], "used_form": item["used_form"],
            "display_gloss": display_gloss, "tts_text": tts_text,
            "converted": tts_text != display_gloss,
            "residual_placeholder_found": placeholder_check["has_placeholder"],
            "residual_placeholder_chars": placeholder_check["found_chars"],
        })
    return rows


# ============================================================
# Step 3: 記事本文非依存の13/14 segmentをTrial-13から再利用
# ============================================================
def prepare_level_inputs(level: str) -> dict:
    meta = LEVELS[level]
    src_dir = f"{TRIAL13_DIR}/{level}"
    dst_dir = f"{OUT_DIR}/{level}"
    os.makedirs(f"{dst_dir}/audit", exist_ok=True)
    os.makedirs(f"{dst_dir}/narration", exist_ok=True)
    os.makedirs(f"{dst_dir}/key_phrases", exist_ok=True)

    shutil.copyfile(f"{src_dir}/article.md", f"{dst_dir}/article.md")
    with open(f"{src_dir}/article.md", encoding="utf-8") as f:
        src_text = f.read()
    with open(f"{dst_dir}/article.md", encoding="utf-8") as f:
        dst_text = f.read()
    assert src_text == dst_text, f"article.mdコピー時に内容が変化しました: {level}"

    shutil.copyfile(f"{src_dir}/parts.json", f"{dst_dir}/parts.json")
    shutil.copyfile(f"{src_dir}/{meta['support_file']}", f"{dst_dir}/{meta['support_file']}")

    return {"article_text": src_text, "parts": load_json(f"{dst_dir}/parts.json"),
            "support": load_json(f"{dst_dir}/{meta['support_file']}")}


def _expected_canonical_text(name: str, parts: dict, support: dict):
    if name == "topic_intro":
        return f"Today's topic is {parts['title']}."
    if name == "japanese_title":
        return None  # 記事本文以外の独立ソースが無いため、Trial-13記録値をそのまま信頼する
    if name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
        return support[name]
    if name in ("point_one_heading", "point_two_heading"):
        return parts[name]
    if name == "full_story_part1":
        return parts["part1"]
    if name == "full_story_part2":
        return parts["part2"]
    if name == "point_one":
        return parts["point_one_body"]
    if name == "point_two":
        return parts["point_two_body"]
    if name == "in_one_line":
        return parts["in_one_line"]
    raise ValueError(f"未知のsegment名: {name}")


def reuse_non_kp_segments(level: str, parts: dict, support: dict) -> dict:
    """Trial-13の13/14 segment(記事本文非依存の共有shell音声[welcome等]は
    含まない、それらはProduction Assembly側[copy_b1_shared_assets/
    A01_NARRATION_DIR]が別経路で自動供給する)を、生成関数を一切呼ばず、
    wavファイル+tts_generation_results.jsonエントリをそのままコピー
    再利用する。前提(wav存在+review_lock RESOLVED+canonical text sha256
    一致)を満たさない場合はSTOPする(D4、自動的な緩和をしない)。"""
    meta = LEVELS[level]
    src_dir = f"{TRIAL13_DIR}/{level}"
    dst_dir = f"{OUT_DIR}/{level}"
    src_results = load_json(f"{src_dir}/audit/tts_generation_results.json")
    src_lock = load_json(f"{src_dir}/audit/review_lock_state.json")

    reused_results = {}
    reuse_report = []
    for name in meta["reused_segments"]:
        entry = src_results["segments"].get(name)
        if entry is None:
            raise RuntimeError(f"Trial-13の{level}/{name}がtts_generation_results.jsonに"
                               "見つかりません(STOP)。")
        lock_entry = src_lock.get(name)
        if not lock_entry or lock_entry.get("state") != "RESOLVED":
            raise RuntimeError(f"Trial-13の{level}/{name}はreview_lock RESOLVEDではありません"
                               f"(state={lock_entry}、STOP)。再利用の前提を満たさないため、"
                               "手動確認が必要です。")
        wav_path = f"{src_dir}/narration/{name}.wav"
        if not os.path.exists(wav_path):
            raise RuntimeError(f"Trial-13の{level}/{name}.wavが存在しません(STOP)。")

        expected_text = _expected_canonical_text(name, parts, support)
        # topic_introはvoice01.generate_charon_english()がcanonical_textキーを
        # 付与せず、代わりに"text"キーに同じ値を保持する(実データで確認済み、
        # comment_1-4/point_headings/full_story/point/in_one_lineはいずれも
        # canonical_textを明示的に持つ)。
        recorded_text = entry.get("canonical_text")
        if recorded_text is None:
            recorded_text = entry.get("text")
        if expected_text is not None:
            if sha(expected_text) != sha(recorded_text):
                raise RuntimeError(
                    f"Trial-13の{level}/{name}のcanonical text hashが、本Trialが読み込んだ"
                    "article.md/parts.json/support textsから独立に再構成した期待値と一致"
                    f"しません(STOP、再利用不可)。expected_sha256={sha(expected_text)!r} "
                    f"recorded_sha256={sha(recorded_text)!r}")
            text_check = "VERIFIED_MATCH"
        else:
            text_check = "TRUSTED_FROM_TRIAL13_RECORD(no_independent_source)"

        for suffix in ("", "_original"):
            src_wav = f"{src_dir}/narration/{name}{suffix}.wav"
            if os.path.exists(src_wav):
                shutil.copyfile(src_wav, f"{dst_dir}/narration/{name}{suffix}.wav")

        reused_results[name] = entry
        reuse_report.append({
            "segment": name, "lock_state": lock_entry.get("state"), "status": entry.get("status"),
            "canonical_text_sha256": sha(recorded_text), "text_check": text_check,
        })
    return {"segments": reused_results, "reuse_report": reuse_report}


# ============================================================
# Step 4: Key Phrase音声(英語Component+日本語gloss)の新規生成
# (Production関数を直接呼ぶ、review_lock/gateはこれらのProduction関数
# 内部でそのまま自動的に動作する)
# ============================================================
def generate_kp_audio_b1(level_out_dir: str, kp_map: list) -> dict:
    narration_dir = f"{level_out_dir}/narration"
    kp_results = {}
    for row in kp_map:
        rank = row["rank"]
        used_form = row["used_form"]
        tts_text = row["tts_text"]
        print(f"[OPEN117-TRIAL-02][b1b] Key Phrase {rank} 英語Component生成: {used_form!r}...")
        with cl.segment_context(f"kp{rank}_english"):
            en_r = shared_narration.ensure_key_phrase_english_component(
                tts_gen.tts_safe_kp_en(used_form), f"{narration_dir}/kp{rank}_en.wav")
        print(f"[OPEN117-TRIAL-02][b1b] Key Phrase {rank} 日本語(TTS用テキスト)生成: {tts_text!r} "
              f"(表示用: {row['display_gloss']!r})...")
        with cl.segment_context(f"kp{rank}_japanese"):
            ja_r = tts_gen.generate_charon_japanese_with_reading_safety(
                tts_text, f"{narration_dir}/kp{rank}_ja_charon.wav",
                tts_gen.expected_substring_ja(tts_text), known_key_phrase_terms=[used_form])
        ja_r["display_gloss_trial"] = row["display_gloss"]
        kp_results[rank] = {"english": en_r, "japanese": ja_r}
    return kp_results


def generate_kp_audio_a2(level_out_dir: str, kp_map: list) -> dict:
    narration_dir = f"{level_out_dir}/narration"
    kp_results = {}
    for i, row in enumerate(kp_map, start=1):
        rank = row["rank"]
        used_form = row["used_form"]
        tts_text = row["tts_text"]
        print(f"[OPEN117-TRIAL-02][a2] Key Phrase {rank} 英語Component生成: {used_form!r}...")
        with cl.segment_context(f"kp{rank}_english"):
            en_r = shared_narration.ensure_key_phrase_english_component(
                tts_gen.tts_safe_kp_en(used_form), f"{narration_dir}/kp{rank}_en.wav")
        print(f"[OPEN117-TRIAL-02][a2] meaning_{i}(TTS用テキスト)生成: {tts_text!r} "
              f"(表示用: {row['display_gloss']!r})...")
        with cl.segment_context(f"kp{rank}_japanese_meaning"):
            ja_r = tts_gen.generate_a2_japanese_with_reading_safety(
                tts_text, f"{narration_dir}/meaning_{i}.wav",
                tts_gen.expected_substring_ja(tts_text), max_extra_chars=30,
                known_key_phrase_terms=[used_form])
        ja_r["display_gloss_trial"] = row["display_gloss"]
        kp_results[rank] = {"english": en_r, "japanese_meaning": ja_r}
    return kp_results


# ============================================================
# Level単位のオーケストレーション
# ============================================================
def run_level(level: str, trial_template: str) -> dict:
    meta = LEVELS[level]
    level_out_dir = f"{OUT_DIR}/{level}"
    inputs = prepare_level_inputs(level)
    article_text = inputs["article_text"]

    article_id = f"ER011_OPEN117_TRIAL02_{level.upper()}"
    kp_dir = f"{level_out_dir}/key_phrases"
    print(f"[OPEN117-TRIAL-02][{level}] Key Phrase選定+Canonicalization+Redundancy QA "
          "(Trial選定Prompt、gloss側「～」許可)開始...")
    with cl.logging_context(THEME_ID, f"keyphrase_{level}"):
        kp = trial_run_key_phrases(article_text, kp_dir, article_id, meta["source_level"], trial_template,
                                    process=meta["process"])

    sel_status = kp["selection"]["status"]
    canon_status = (kp.get("canonicalization") or {}).get("status")
    redundancy_status = (kp.get("redundancy_qa") or {}).get("status")
    print(f"[OPEN117-TRIAL-02][{level}] Key Phrase結果: selection={sel_status} "
          f"canonicalization={canon_status} redundancy={redundancy_status} "
          f"overall_status={kp.get('status')}")

    if kp.get("canonicalization") is None or canon_status not in (
            "CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
        return {"level": level, "status": "STOP_KEY_PHRASE_PIPELINE_FAILED", "kp": kp}

    merged_items = kp["canonicalization"]["merged"]["items"]
    kp_map = build_kp_display_tts_map(merged_items)
    with open(f"{level_out_dir}/audit/kp_display_tts_map.json", "w", encoding="utf-8") as f:
        json.dump(kp_map, f, ensure_ascii=False, indent=2)

    print(f"[OPEN117-TRIAL-02][{level}] 本文{len(meta['reused_segments'])}segmentをTrial-13(review_lock "
          "RESOLVED確認済み)から再利用(再TTSしない)...")
    reused = reuse_non_kp_segments(level, inputs["parts"], inputs["support"])

    print(f"[OPEN117-TRIAL-02][{level}] Key Phrase音声(英語+日本語、TTS用テキスト)を新規生成...")
    with cl.logging_context(THEME_ID, f"kp_tts_{level}"):
        if level == "b1b":
            kp_results = generate_kp_audio_b1(level_out_dir, kp_map)
        else:
            kp_results = generate_kp_audio_a2(level_out_dir, kp_map)

    all_results = {"segments": reused["segments"], "key_phrases": kp_results}
    with open(f"{level_out_dir}/audit/tts_generation_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)

    if level == "b1b":
        kp_audio_status = {r: {"en": v["english"].get("status"), "ja": v["japanese"].get("status")}
                            for r, v in kp_results.items()}
    else:
        kp_audio_status = {r: {"en": v["english"].get("status"), "ja": v["japanese_meaning"].get("status")}
                            for r, v in kp_results.items()}
    print(f"[OPEN117-TRIAL-02][{level}] Key Phrase音声status={kp_audio_status}")

    theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}
    assemble_fn = asm.stage_assemble_b1 if level == "b1b" else asm.stage_assemble_a2
    try:
        with cl.logging_context(THEME_ID, f"assemble_{level}"):
            assemble_result = assemble_fn(theme)
    except RuntimeError as e:
        assemble_result = {"status": "GATE_BLOCKED", "error": str(e)}
        print(f"[OPEN117-TRIAL-02][{level}] Assemble GATE_BLOCKED: {e}")

    return {
        "level": level, "status": "DONE", "kp_selection_status": sel_status,
        "kp_canonicalization_status": canon_status, "kp_redundancy_status": redundancy_status,
        "kp_overall_status": kp.get("status"), "kp_map": kp_map, "reuse_report": reused["reuse_report"],
        "kp_audio_status": kp_audio_status, "assemble_result": assemble_result,
    }


def main() -> dict:
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log_open117_trial02.jsonl")

    trial_template = build_trial_selector_prompt_template()
    with open(f"{OUT_DIR}/audit/keywords_l_trial_prompt_template.txt", "w", encoding="utf-8") as f:
        f.write(trial_template)

    results = {}
    for level in ["b1b", "a2"]:
        print(f"===== [OPEN117-TRIAL-02] level={level} 開始 =====")
        results[level] = run_level(level, trial_template)

    with open(f"{OUT_DIR}/trial02_summary.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print("[OPEN117-TRIAL-02] 完了。")
    return results


if __name__ == "__main__":
    main()
