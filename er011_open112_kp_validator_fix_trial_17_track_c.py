# ============================================================
# er011_open112_kp_validator_fix_trial_17_track_c.py
# 管理ID: OPEN-112-TREND-THEME2-B-KEYPHRASE-VALIDATOR-FIX-TRIAL-17
# Track C: 選定Prompt規約(隔離Trial、Production Prompt/schemaは無変更)
# ============================================================
# Trial-13 B1の実際のcanonicalization入力(er011_output/.../b1b/key_phrases/
# canonicalization_prompt.txtに保存済みの、実際にLLMへ送った完全なprompt
# テキスト)へ、Trial専用の追加規約(A: gloss数字は漢数字/B: ～〜…禁止/
# C: 1語の機能語終端2語以下KP回避)を付け足したTrial用コピーPromptで、
# 同じLLM設定(er003_key_words_production.SELECTOR_MODEL="gpt-5.6-sol"、
# reasoning effort="high"、Production定数を値だけ再利用し変更はしない)を
# 使って**1回だけ**再生成する。Production関数
# (er003_key_words_canonicalization.make_canonicalization_fn等)や
# Production JSON Schemaは一切変更しない。本Trialは独自のTrial専用
# JSON Schema(japanese_gloss/track_c_short_function_word_ending_flaggedを
# 追加)を使うため、そのままProduction経路へは配線できない(意図的)。
# ============================================================
from __future__ import annotations

import json
import os

import er003_key_words_canonicalization as kc
import er003_key_words_production as prod

ORIGINAL_PROMPT_PATH = (
    "er011_output/open112_trend_theme2_b_full_audio_trial_13/b1b/key_phrases/canonicalization_prompt.txt"
)
ORIGINAL_RESULT_PATH = (
    "er011_output/open112_trend_theme2_b_full_audio_trial_13/b1b/key_phrases/keywords_canonicalized.json"
)
OUT_DIR = "er011_output/open112_kp_validator_fix_trial_17"

TRIAL_ADDENDUM_TEMPLATE = """

【本Trialでの追加規約(Track C、Production Promptには存在しない検証用ルール。
このTrialでのみ有効、Production Promptは別途無変更のまま維持される)】
以下の3点を追加で厳守してください。

参考情報: 各候補には、この工程より前の別工程(方式L選定)で既に決定
済みの日本語訳(japanese_gloss)があります(この工程の対象outsideの
既存データ、参考としてrank対応で示します)。
{gloss_reference_block}

A. 数字表記: 出力にも各候補ごとに"japanese_gloss"フィールドを含め、上記の
   既存の日本語訳に数字が含まれる場合は算用数字(1、2、3…)ではなく
   漢数字(一、二、三…)を使って書き直してください(意味は変えないこと)。
   数字を含まない場合は、既存のjapanese_glossをそのまま出力してください。

B. プレースホルダー記号の禁止: key_phraseにも出力するjapanese_glossにも、
   「～」「〜」「…」の3文字を一切使わないでください。動詞句などで目的語
   を省略した言い方にしたい場合は、日本語として自然な言い切りの形(例:
   「～を示す」ではなく「示す、指し示す」のように)へ書き換えてください。

C. 短い機能語終端のKey Phraseの回避: key_phraseが2語以下で、かつ末尾が
   前置詞・不定詞のto・接続詞などの1語の機能語だけで終わり、その機能語の
   直後に目的語や補語が来なければ意味が完結しない形(例: "point to"）に
   なっている場合は、出力の"track_c_short_function_word_ending_flagged"を
   trueにしてください。該当する場合、Listening Blockerとしての学習価値を
   保ったまま、source_span内で利用可能な語を使って意味が完結する形に修正
   できないか検討し、修正した場合はkey_phraseへその結果を反映してくださ
   い。修正が難しい、または元の学習価値を落とす場合は無理に変更せず、
   reasoningにその判断根拠を明記した上でtrue のままにしてください。
   該当しない場合は"track_c_short_function_word_ending_flagged"をfalseに
   してください。

出力JSONの各item要素には、Production schemaの既存フィールド(rank/
key_phrase/changed_from_display_phrase/normalization_reason/reasoning/
qa_*)に加えて、"japanese_gloss"(文字列)と
"track_c_short_function_word_ending_flagged"(真偽値)を必ず含めてください。
"""

TRIAL_JSON_SCHEMA = {
    "name": "key_words_canonicalization_track_c_trial",
    "schema": {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        **kc._ITEM_SCHEMA_PROPERTIES,
                        "japanese_gloss": {"type": "string"},
                        "track_c_short_function_word_ending_flagged": {"type": "boolean"},
                    },
                    "required": list(kc._ITEM_REQUIRED_FIELDS) + [
                        "japanese_gloss", "track_c_short_function_word_ending_flagged"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["items"],
        "additionalProperties": False,
    },
    "strict": True,
}


def build_trial_prompt(original_prompt_text: str, original_result: dict) -> str:
    """元のprompt本文の中で、記事本文セクションが始まる直前に追加規約を
    挿入する(記事本文・Key Phrase候補JSON自体は一切変更しない)。既存の
    japanese_gloss(この工程の入力JSONには元々含まれていない、方式L選定
    工程で既に決定済みの別データ)は、rank対応の参考情報として追加規約
    テキスト内に埋め込む(元のprompt本文・JSON構造自体は書き換えない)。"""
    gloss_lines = [f"  rank {it['rank']}: key_phrase={it['key_phrase']!r} / 既存japanese_gloss={it['japanese_gloss']!r}"
                   for it in original_result["items"]]
    gloss_reference_block = "\n".join(gloss_lines)
    addendum = TRIAL_ADDENDUM_TEMPLATE.format(gloss_reference_block=gloss_reference_block)

    marker = "【記事本文"
    idx = original_prompt_text.find(marker)
    if idx == -1:
        # 想定外(marker不在)の場合は安全側で末尾に追加する。
        return original_prompt_text + addendum
    return original_prompt_text[:idx] + addendum.strip() + "\n\n" + original_prompt_text[idx:]


def main():
    with open(ORIGINAL_PROMPT_PATH, encoding="utf-8") as f:
        original_prompt_text = f.read()
    with open(ORIGINAL_RESULT_PATH, encoding="utf-8") as f:
        original_result = json.load(f)

    trial_prompt_text = build_trial_prompt(original_prompt_text, original_result)

    from dotenv import load_dotenv
    load_dotenv()
    from openai import OpenAI
    client = OpenAI()

    model = prod.SELECTOR_MODEL
    reasoning_effort = prod.SELECTOR_REASONING_EFFORT
    print(f"[Track C] 1回だけLLM呼び出し(model={model}, reasoning_effort={reasoning_effort})")

    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        text={"format": {"type": "json_schema", **TRIAL_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": kc.DEVELOPER_MESSAGE},
            {"role": "user", "content": trial_prompt_text},
        ],
    )
    raw_text = response.output_text
    parsed = json.loads(raw_text)
    usage = getattr(response, "usage", None)
    usage_dict = {
        "input_tokens": getattr(usage, "input_tokens", None),
        "output_tokens": getattr(usage, "output_tokens", None),
        "input_tokens_cached": getattr(getattr(usage, "input_tokens_details", None), "cached_tokens", None),
    } if usage is not None else None

    print(f"[Track C] response.model={response.model} response.id={response.id}")
    print(f"[Track C] usage={usage_dict}")

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(f"{OUT_DIR}/track_c_trial_prompt.txt", "w", encoding="utf-8") as f:
        f.write(trial_prompt_text)
    with open(f"{OUT_DIR}/track_c_raw_response.json", "w", encoding="utf-8") as f:
        json.dump({"model": response.model, "response_id": response.id, "usage": usage_dict,
                   "parsed": parsed}, f, ensure_ascii=False, indent=2)

    # 原本(Trial-13正式)との比較表を作る
    original_by_rank = {it["rank"]: it for it in original_result["items"]}
    comparison = []
    for it in parsed["items"]:
        rank = it["rank"]
        orig = original_by_rank.get(rank, {})
        placeholder_chars_found = [ch for ch in ("～", "〜", "…") if ch in it.get("key_phrase", "") + it.get("japanese_gloss", "")]
        comparison.append({
            "rank": rank,
            "original_key_phrase": orig.get("key_phrase"),
            "track_c_key_phrase": it.get("key_phrase"),
            "key_phrase_changed": orig.get("key_phrase") != it.get("key_phrase"),
            "original_japanese_gloss": orig.get("japanese_gloss"),
            "track_c_japanese_gloss": it.get("japanese_gloss"),
            "japanese_gloss_changed": orig.get("japanese_gloss") != it.get("japanese_gloss"),
            "track_c_short_function_word_ending_flagged": it.get("track_c_short_function_word_ending_flagged"),
            "placeholder_chars_found_in_track_c_output": placeholder_chars_found,
            "track_c_reasoning": it.get("reasoning"),
        })

    with open(f"{OUT_DIR}/track_c_comparison.json", "w", encoding="utf-8") as f:
        json.dump({"comparison": comparison, "usage": usage_dict, "model": response.model}, f,
                   ensure_ascii=False, indent=2)

    print("\n=== Track C 原本 vs 規約追加版 比較 ===")
    for c in comparison:
        print(f"rank={c['rank']}: key_phrase {c['original_key_phrase']!r} -> {c['track_c_key_phrase']!r} "
              f"(changed={c['key_phrase_changed']}) | gloss {c['original_japanese_gloss']!r} -> "
              f"{c['track_c_japanese_gloss']!r} (changed={c['japanese_gloss_changed']}) | "
              f"flagged={c['track_c_short_function_word_ending_flagged']} | "
              f"placeholder_chars={c['placeholder_chars_found_in_track_c_output']}")

    print(f"\nwrote {OUT_DIR}/track_c_trial_prompt.txt")
    print(f"wrote {OUT_DIR}/track_c_raw_response.json")
    print(f"wrote {OUT_DIR}/track_c_comparison.json")


if __name__ == "__main__":
    main()
