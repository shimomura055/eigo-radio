# ============================================================
# er011_theme2_b1_preview_shorten_trial_01.py
# OPEN-112-THEME2-AUDIO-REVIEW-FIX-02 / サブタスクB
# ============================================================
# 目的: B1 Preview(現行Production Prompt=er003_v1_b1_scaffold_01_generate.
# PREVIEW_ROLE、実際にer003_v1_n3_01_scaffold_generate.py経由でTheme2
# B1へ使われている)を、A2日本語Previewと同じ「短い導入」思想で
# 1/2〜1/3程度へ圧縮できるかをTrialする。
#
# Production安全性:
# - er003_v1_b1_scaffold_01_generate.py(Production PREVIEW_ROLE定義元)・
#   er003_v1_n3_01_scaffold_generate.py(実際の呼び出し元)は一切変更しない。
# - 本ファイルはTrial専用のPromptコピー(TRIAL_PREVIEW_ROLE)を独自に定義し、
#   Production関数run_support_text()(無変更)をそのTrial Promptで1回だけ
#   呼び出す(LLM呼び出しは小額、実API)。
# - 呼び出すarticle本文・comment_1/comment_2はTheme2 B1(Trial-12
#   b1b_run01/article.md、Production full_audio_trial_13で実際に使われた
#   ものと内容一致をdiffで確認済み)の既存Production生成物をそのまま使う
#   (再生成しない、既存のcomment_1/2は無変更のまま比較の土台として固定)。
#
# 実行方法:
#   .venv/Scripts/python.exe er011_theme2_b1_preview_shorten_trial_01.py

from __future__ import annotations

import json
import os
import re

from dotenv import load_dotenv

import er003_v1_b1_scaffold_01_generate as b1s

load_dotenv()

ARTICLE_PATH = "er011_output/open112_trend_theme2_b_a2_b1_text_trial_12/b1b_run01/article.md"
CURRENT_SUPPORT_TEXTS_PATH = "er011_output/open112_trend_theme2_b_full_audio_trial_13/b1b/b1_support_texts.json"
CURRENT_SUPPORT_GENERATION_PATH = "er011_output/open112_trend_theme2_b_full_audio_trial_13/b1b/audit/b1_support_generation.json"
OUT_DIR = "er011_output/theme2_b1_preview_shorten_trial_01"

# ------------------------------------------------------------
# Trial用Prompt: Production PREVIEW_ROLE(b1s.PREVIEW_ROLE)をベースに、
# A2 PREVIEW_ROLE(er003_v1_iran01_a2_generate.py)にある「分量目安」段落
# と同じ思想(hard limitではない目安、律儀に4要素を書き並べない)を、
# B1向け(英語・現行の1/2〜1/3・2〜3文)に言い換えて追加する。
# Production原則(答え・数字・結論・turning pointの先出し禁止、Comment1/2
# との重複回避)はそのまま維持し削除しない。
# ------------------------------------------------------------
TRIAL_QUANTITY_NOTE = (
    "\n\n【重要・分量(Trial)】現在のB1 Previewの目安は約1/2〜1/3にしてください"
    "(目安2〜3文)。theme/problem/value/questionの4要素を律儀にすべて別の文で"
    "書き並べる必要はありません。「何を聞く回か」が短く伝わることを優先し、"
    "要素を尽くそうとして冗長にならないよう注意してください。あくまで目安であり、"
    "絶対的なhard limitではありません(記事の内容により多少の増減は許容します)。"
)

TRIAL_PREVIEW_ROLE = b1s.PREVIEW_ROLE + TRIAL_QUANTITY_NOTE


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    with open(ARTICLE_PATH, encoding="utf-8") as f:
        article_text = f.read()

    with open(CURRENT_SUPPORT_TEXTS_PATH, encoding="utf-8") as f:
        current_support = json.load(f)
    comment_1 = current_support["comment_1"]
    comment_2 = current_support["comment_2"]
    current_preview = current_support["preview"]

    with open(CURRENT_SUPPORT_GENERATION_PATH, encoding="utf-8") as f:
        current_generation = json.load(f)
    current_preview_prompt = current_generation["preview"]["prompt"]

    client = b1s.get_client()

    trial_role = TRIAL_PREVIEW_ROLE.format(comment_1=comment_1, comment_2=comment_2)
    trial_context = f"【エピソード全文(参考、新しいFactの追加禁止)】\n{article_text}"

    print("[TRIAL-B1-PREVIEW] Trial Preview生成開始(Production run_support_text、1回のみ)...")
    trial_result = b1s.run_support_text(client, trial_role, trial_context)

    with open(f"{OUT_DIR}/trial_preview_attempts.json", "w", encoding="utf-8") as f:
        json.dump(trial_result["attempts"], f, ensure_ascii=False, indent=2, default=str)
    with open(f"{OUT_DIR}/trial_prompt_full.txt", "w", encoding="utf-8") as f:
        f.write(trial_result["prompt"])
    with open(f"{OUT_DIR}/current_production_prompt_full.txt", "w", encoding="utf-8") as f:
        f.write(current_preview_prompt)

    trial_preview_text = trial_result.get("text")

    def stats(text: str) -> dict:
        if text is None:
            return {"chars": None, "words": None, "sentence_end_count": None}
        return {
            "chars": len(text),
            "words": len(text.split()),
            "sentence_end_count": len(re.findall(r"[.!?]", text)),
        }

    comparison = {
        "article_source": ARTICLE_PATH,
        "current_production": {
            "status": "OK",
            "text": current_preview,
            "stats": stats(current_preview),
        },
        "trial": {
            "status": trial_result["status"],
            "text": trial_preview_text,
            "stats": stats(trial_preview_text),
        },
        "comment_1_unchanged": comment_1,
        "comment_2_unchanged": comment_2,
    }
    if trial_preview_text and current_preview:
        cur_words = comparison["current_production"]["stats"]["words"]
        trial_words = comparison["trial"]["stats"]["words"]
        comparison["ratio_trial_over_current_words"] = round(trial_words / cur_words, 3) if cur_words else None
        cur_chars = comparison["current_production"]["stats"]["chars"]
        trial_chars = comparison["trial"]["stats"]["chars"]
        comparison["ratio_trial_over_current_chars"] = round(trial_chars / cur_chars, 3) if cur_chars else None

    with open(f"{OUT_DIR}/comparison.json", "w", encoding="utf-8") as f:
        json.dump(comparison, f, ensure_ascii=False, indent=2)

    print(f"[TRIAL-B1-PREVIEW] status={trial_result['status']}")
    print(f"[TRIAL-B1-PREVIEW] current: {comparison['current_production']['stats']}")
    print(f"[TRIAL-B1-PREVIEW] trial:   {comparison['trial']['stats']}")
    if "ratio_trial_over_current_words" in comparison:
        print(f"[TRIAL-B1-PREVIEW] ratio(words)={comparison['ratio_trial_over_current_words']} "
              f"ratio(chars)={comparison['ratio_trial_over_current_chars']}")
    print(f"[TRIAL-B1-PREVIEW] trial text: {trial_preview_text}")


if __name__ == "__main__":
    main()
