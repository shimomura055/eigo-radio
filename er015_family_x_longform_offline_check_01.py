# ============================================================
# er015_family_x_longform_offline_check_01.py
# NEWS-FAMILY-X-LONGFORM-OFFLINE-CHECK-01 (Offline本文生成→内容・長さ確認のみ)
# ============================================================
# 目的: Family Xの3分割を検証する前に、「Point構造なしで、News本文を
# 十分な長さへ長文化すること自体」に品質問題がないかをOfflineで隔離確認
# する。Family A契約(### 見出し2つ + ## In one line)は使わない。
#
# 本スクリプトはOffline確認専用であり、Production line(3分割・Comment
# 生成・scaffold・TTS・assemble・Family X E2E・Production Prompt変更)を
# 一切行わない。ここで生成した本文はOnline Production Runへ流用しない。
#
# Prompt: Production Advanced Natural English Adaptation prompt
# (er015_news_ja_to_en_adaptation_trial_01.py の arm3文言 = COMMON_BLOCK +
# ARM3_BLOCK)を、contract suffix (### x2 / ## In one line) なしのまま
# 逐語再利用し、長さ指示のみを追加する(語彙ルールは追加しない)。
#
# 依存(いずれも無変更・import再利用のみ):
#   - er003_v1_en_direct_vfl_01_generate (vfl01): get_client
#   - er005_cost_logger (cl): usage log install
#   - er015_news_core_idea_editorial_trial_01 (er015base): _load_pricing,
#     _price, USD_TO_JPY
#   - er015_news_iterative_entertainment_trial_02 (trial02): call_fresh
#   - er015_news_original_baseline_repro_01 (repro01): WRITER_MODEL,
#     WRITER_EFFORT
#   - er015_news_ja_to_en_adaptation_trial_01 (ja2en): DEVELOPER,
#     COMMON_BLOCK, ARM3_BLOCK, IN_PATH, IN_EXPECTED_SHA256 (逐語流用のみ、
#     ja2en自体は無変更)
#   - er015_news_natural_advanced_standard_a2_trial_01 (levelmod):
#     _level_metrics (word/sentence/FK grade計測コードの流用)
#
# 予算: ¥5上限。1 call生成。語数が260-340語を外れた場合のみ1回再生成
# (合計2 call以内)。web_search禁止。
# ============================================================
from __future__ import annotations

import hashlib
import json
import os
import re
import time

import er005_cost_logger as cl
import er015_news_core_idea_editorial_trial_01 as er015base
import er015_news_iterative_entertainment_trial_02 as trial02
import er015_news_original_baseline_repro_01 as repro01
import er015_news_ja_to_en_adaptation_trial_01 as ja2en
import er015_news_natural_advanced_standard_a2_trial_01 as levelmod
import er003_v1_en_direct_vfl_01_generate as vfl01

THEME_TAG_LOCAL = "NEWS_FAMILY_X_LONGFORM_OFFLINE_CHECK_01"  # 参考表示用

WRITER_MODEL = repro01.WRITER_MODEL       # "gpt-5.6-luna"
WRITER_EFFORT = repro01.WRITER_EFFORT     # "high"

OUT_DIR = os.path.join("er015_output", "family_x_longform_offline_check_01")

# 長さ指示(Fable指示、逐語固定。語彙ルールは追加しない)
LENGTH_BLOCK = (
    "Write the full story as continuous prose in 4–7 paragraphs, "
    "roughly 260–340 words. No section headings, no bullet points, no "
    "summary line. Do not pad: every sentence must carry information or "
    "move the story forward."
)

MIN_WORDS = 260
MAX_WORDS = 340
MAX_CALLS = 2
BUDGET_JPY = 5


def out_path(*parts: str) -> str:
    return os.path.join(OUT_DIR, *parts)


def save_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def _sha256_of_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def _check_input_sha256() -> str:
    actual = _sha256_of_file(ja2en.IN_PATH)
    if actual != ja2en.IN_EXPECTED_SHA256:
        stop = {
            "stop_reason": "入力日本語R2(Meta R2)を正確に再利用できない(sha256不一致)",
            "expected_sha256": ja2en.IN_EXPECTED_SHA256,
            "actual_sha256": actual,
            "source_path": ja2en.IN_PATH,
        }
        save_json(out_path("stop_reason.json"), stop)
        print(f"[STOP] sha256 mismatch: expected={ja2en.IN_EXPECTED_SHA256} actual={actual}")
        raise SystemExit(1)
    return actual


def build_user_prompt(ja_text: str) -> str:
    # Production Advanced Natural English Adaptation prompt(arm3文言)を
    # contract suffixなしのまま逐語流用し、長さ指示のみ追加する。
    return (ja2en.COMMON_BLOCK + "\n\n" + ja2en.ARM3_BLOCK + "\n\n" +
            LENGTH_BLOCK + "\n\n" +
            "[Japanese article]\n" + ja_text)


def _word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z']+", text))


def _paragraph_count(text: str) -> int:
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    return len(paras)


def _first_line_title(text: str) -> str:
    for line in text.split("\n"):
        line = line.strip()
        if line:
            return line.lstrip("#").strip()
    return ""


def _body_only(text: str) -> str:
    lines = text.strip().splitlines()
    return "\n".join(lines[1:]).strip() if lines else ""


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    _check_input_sha256()
    ja_text = load_text(ja2en.IN_PATH)
    save_text(out_path("input_ja_r2.md"), ja_text)

    cl.install(out_path("raw_usage_log.jsonl"))
    client = vfl01.get_client()

    pricing = er015base._load_pricing()
    luna_in = er015base._price(pricing, "openai", "gpt-5.6-luna", "input_tokens")
    luna_cached = er015base._price(pricing, "openai", "gpt-5.6-luna", "cached_input_tokens")
    luna_out = er015base._price(pricing, "openai", "gpt-5.6-luna", "output_tokens")

    user_prompt = build_user_prompt(ja_text)
    save_text(out_path("prompt_used.txt"),
              "[developer]\n" + ja2en.DEVELOPER + "\n\n[user]\n" + user_prompt)

    calls = []
    total_usd = 0.0
    total_input = total_cached = total_output = total_reasoning = 0
    chosen_text = None
    chosen_meta = None

    for attempt in range(1, MAX_CALLS + 1):
        t0 = time.time()
        response = trial02.call_fresh(client, ja2en.DEVELOPER, user_prompt,
                                       WRITER_EFFORT, "family_x_longform_offline_check_01")
        text = (response.output_text or "").strip()
        elapsed = round(time.time() - t0, 3)

        usage = getattr(response, "usage", None)
        input_tokens = getattr(usage, "input_tokens", None) if usage else None
        output_tokens = getattr(usage, "output_tokens", None) if usage else None
        cached_tokens = None
        reasoning_tokens = None
        if usage is not None:
            in_details = getattr(usage, "input_tokens_details", None)
            if in_details is not None:
                cached_tokens = getattr(in_details, "cached_tokens", None)
            out_details = getattr(usage, "output_tokens_details", None)
            if out_details is not None:
                reasoning_tokens = getattr(out_details, "reasoning_tokens", None)

        billable_in = max((input_tokens or 0) - (cached_tokens or 0), 0)
        cost_usd = 0.0
        if luna_in is not None:
            cost_usd += (billable_in / 1_000_000) * luna_in
        if luna_cached is not None and cached_tokens:
            cost_usd += (cached_tokens / 1_000_000) * luna_cached
        if luna_out is not None and output_tokens:
            cost_usd += (output_tokens / 1_000_000) * luna_out
        cost_jpy = cost_usd * er015base.USD_TO_JPY

        body = _body_only(text)
        wc = _word_count(body)
        pc = _paragraph_count(body)

        meta = {
            "attempt": attempt,
            "model_requested": WRITER_MODEL,
            "response_model_actual": response.model,
            "response_id": response.id,
            "effort_requested": WRITER_EFFORT,
            "usage": {
                "input_tokens": input_tokens,
                "cached_input_tokens": cached_tokens,
                "output_tokens": output_tokens,
                "reasoning_tokens": reasoning_tokens,
            },
            "elapsed_seconds": elapsed,
            "cost_usd": round(cost_usd, 6),
            "cost_jpy": round(cost_jpy, 4),
            "word_count": wc,
            "paragraph_count": pc,
            "in_range_260_340": MIN_WORDS <= wc <= MAX_WORDS,
        }
        save_text(out_path(f"attempt{attempt}_output.md"), text)
        save_json(out_path(f"attempt{attempt}_api_meta.json"), meta)
        calls.append(meta)
        total_usd += cost_usd
        total_input += input_tokens or 0
        total_cached += cached_tokens or 0
        total_output += output_tokens or 0
        total_reasoning += reasoning_tokens or 0

        print(f"[OK] attempt={attempt}: words={wc} paragraphs={pc} "
              f"in_range={meta['in_range_260_340']} cost_jpy={meta['cost_jpy']}")

        if chosen_text is None or meta["in_range_260_340"]:
            chosen_text = text
            chosen_meta = meta
        if meta["in_range_260_340"]:
            break

    save_text(out_path("offline_longform_meta_advanced.md"), chosen_text)

    title, body = chosen_text.strip().splitlines()[0], _body_only(chosen_text)
    words = re.findall(r"[A-Za-z']+", body)
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", body) if s.strip()]
    lm = levelmod._level_metrics(chosen_text)

    metrics = {
        "chosen_attempt": chosen_meta["attempt"],
        "title": title.lstrip("#").strip(),
        "word_count": len(words),
        "paragraph_count": _paragraph_count(body),
        "sentence_count": len(sentences),
        "avg_sentence_length_words": lm["avg_sentence_length_words"],
        "flesch_kincaid_grade_heuristic": lm["flesch_kincaid_grade_heuristic"],
        "avg_syllables_per_word_heuristic": lm["avg_syllables_per_word_heuristic"],
        "in_range_260_340": chosen_meta["in_range_260_340"],
        "comparison_reference": {
            "family_a_main_story_127w": {
                "path": os.path.join(
                    "er012_output", "e_family_two_level_wiring_01", "meta", "b1b",
                    "article.md"),
                "note": "###見出し前の本文(参考、入力には使っていない)",
            },
            "arm3_natural_english_338w": {
                "path": os.path.join(
                    "er015_output", "news_ja_to_en_adaptation_trial_01", "arms",
                    "arm3", "output.md"),
                "note": "contract suffixなし・長さ指示なし版(参考、入力には使っていない)",
            },
        },
    }
    save_json(out_path("metrics.json"), metrics)

    cost = {
        "theme_local_label": THEME_TAG_LOCAL,
        "raw_log_theme_actual": trial02.THEME_TAG,
        "calls": len(calls),
        "per_call": calls,
        "total_input_tokens": total_input,
        "total_cached_input_tokens": total_cached,
        "total_output_tokens": total_output,
        "total_reasoning_tokens": total_reasoning,
        "total_usd": round(total_usd, 6),
        "total_jpy": round(total_usd * er015base.USD_TO_JPY, 2),
        "usd_to_jpy": er015base.USD_TO_JPY,
        "budget_jpy": BUDGET_JPY,
        "within_budget": round(total_usd * er015base.USD_TO_JPY, 2) <= BUDGET_JPY,
    }
    save_json(out_path("cost.json"), cost)

    print(f"[DONE] calls={len(calls)} total_jpy={cost['total_jpy']} "
          f"within_budget={cost['within_budget']} chosen_words={metrics['word_count']}")


if __name__ == "__main__":
    main()
