# ============================================================
# er015_news_natural_advanced_standard_a2_trial_01.py
# NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01 (ユーザー指示、2026-09-24)
# ============================================================
# 目的: News Entertainment英語記事を2段階(Advanced=CEFR B1 Natural English
# Adaptation / Standard=CEFR A2)として成立させられるか検証する。中心仮説:
# "Simplify the English, not the story."
#
# Article A(下水道): 既存日本語R2(docs/evidence/news_iterative_r2_adoption_
# 2026-09-24/articles/sewer_revision2.md)をNEWS-JA-TO-EN-ADAPTATION-TRIAL-01
# arm3(Natural English)のPromptを流用しAdvancedへAdapt(A-1)、続けて
# Advanced→Standard A2共通Promptで簡略化(A-2)。
# Article B(Meta AI Call): 既存採用済みNatural English版
# (er015_output/news_ja_to_en_adaptation_trial_01/arms/arm3/output.md、
# 改変禁止のBaseline)を Advanced→Standard A2共通Promptで簡略化(B-1)。
#
# 固定: 3 call合計(A-1/A-2/B-1)、previous_response_idなし、Web Searchなし、
# Ledgerは生成材料として使わない(Fact drift照合参照のみ)、model=
# gpt-5.6-luna effort=high、Production Prompt/routing/retry/fallback/Audio
# 配線は変更しない。Production実装ではない。
#
# 依存(いずれも無変更・import再利用のみ):
#   - er003_v1_en_direct_vfl_01_generate (vfl01): get_client
#   - er005_cost_logger (cl): usage log install
#   - er015_news_core_idea_editorial_trial_01 (er015base): _load_pricing,
#     _price, USD_TO_JPY
#   - er015_news_iterative_entertainment_trial_02 (trial02): call_fresh
#     (単発call、previous_response_idは使わない)
#   - er015_news_original_baseline_repro_01 (repro01): WRITER_MODEL,
#     WRITER_EFFORT
#
# サブコマンド (--step):
#   sources  : 下水道日本語R2 / Meta Advanced Baselineのsha256確認 ->
#              sources.json
#   generate : A-1 -> A-2 -> B-1 の順に1 callずつ実行(冪等、--forceで再生成)
#              --budget-jpy で累計コスト上限をチェック(超過見込みならSTOP)
#   analyze  : level_metrics.json/.md, fact_diff_machine.json を機械算出
#   assemble : cost.json を組み立て
# ============================================================
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time

import er005_cost_logger as cl
import er015_news_core_idea_editorial_trial_01 as er015base
import er015_news_iterative_entertainment_trial_02 as trial02
import er015_news_original_baseline_repro_01 as repro01
import er003_v1_en_direct_vfl_01_generate as vfl01

THEME_TAG_LOCAL = "NEWS_NATURAL_ADVANCED_STANDARD_A2_TRIAL_01"  # 参考表示用(実ログはtrial02.THEME_TAG)

WRITER_MODEL = repro01.WRITER_MODEL     # "gpt-5.6-luna"
WRITER_EFFORT = repro01.WRITER_EFFORT   # "high"

# ------------------------------------------------------------
# 入力source path(逐語再利用、sha256で一致確認)
# ------------------------------------------------------------
SEWER_JA_PATH = os.path.join(
    "docs", "evidence", "news_iterative_r2_adoption_2026-09-24", "articles",
    "sewer_revision2.md")
# 実測値(2026-09-24, .venv hashlib):
SEWER_JA_EXPECTED_SHA256 = "a7fa4fd7dcd02b5570521eff361153eef24885de7ec79edeb518740386040769"

META_ADVANCED_PATH = os.path.join(
    "er015_output", "news_ja_to_en_adaptation_trial_01", "arms", "arm3",
    "output.md")
META_ADVANCED_EXPECTED_SHA256 = (
    "20b7ac01ffc962b55cdb9246425f54fa12e3d68f96a3328924d123dbefc3e481")

# ------------------------------------------------------------
# A-1 Prompt: NEWS-JA-TO-EN-ADAPTATION-TRIAL-01 arm3 Promptを逐語再利用。
# DEVELOPER / ARM3_BLOCK は無変更。COMMON_BLOCKのみ、Meta固有の
# Preserve列挙6項目を下水道R2の編集設計に合わせた同形式の6項目へ置換
# (prompt_diff_a1.mdに差分保存)。
# ------------------------------------------------------------
DEVELOPER_A1 = (
    "You are an editor who adapts finished Japanese feature articles into "
    "natural English for listeners who are learning English.")

# 元(Meta固有、置換前。差分保存用に保持)
COMMON_BLOCK_ORIGINAL_META = (
    "Adapt the Japanese article below into English.\n"
    "\n"
    "Do not rewrite the article from scratch. Do not add new ideas, claims, "
    "background, general observations, examples, or facts that are not in "
    "the Japanese article. Preserve the Japanese article's editorial angle, "
    "structure, and sense of surprise:\n"
    "- the opening expectation of a convenient \"AI makes the phone call\" "
    "future;\n"
    "- the reversal that a human was actually working behind the scenes;\n"
    "- the framing of lead role / backstage / understudy;\n"
    "- the theme fixed on \"there was a human behind the AI phone call\";\n"
    "- privacy treated as necessary later information, not as the main "
    "theme;\n"
    "- the ending that returns to the image of the stage and what is behind "
    "the curtain.\n"
    "Keep every fact exactly as in the Japanese article. Use short, simple "
    "English that a learner could understand by listening once.\n"
    "\n"
    "Output only the English title and the English body."
)

# 置換後(下水道用、Meta固有列挙6項目だけを差替え。それ以外は一字も変えない)
COMMON_BLOCK_SEWER = (
    "Adapt the Japanese article below into English.\n"
    "\n"
    "Do not rewrite the article from scratch. Do not add new ideas, claims, "
    "background, general observations, examples, or facts that are not in "
    "the Japanese article. Preserve the Japanese article's editorial angle, "
    "structure, and sense of surprise:\n"
    "- the opening expectation triggered by the word \"merger,\" that towns "
    "or municipalities might be the ones merging;\n"
    "- the reversal that it is not towns merging, but a household's own "
    "toilet, kitchen, and bath water that are being treated together, near "
    "the home;\n"
    "- the framing of the sewer as the town's invisible main artery, versus "
    "the shift to small, household-level water treatment;\n"
    "- the theme fixed on \"you can protect convenience without making the "
    "system bigger, by moving water treatment closer to home\";\n"
    "- installation, inspection, and cleaning treated as necessary later "
    "information, not as the main theme;\n"
    "- the ending that returns to the idea that the future of sewers may "
    "arrive in a surprisingly familiar, nearby place.\n"
    "Keep every fact exactly as in the Japanese article. Use short, simple "
    "English that a learner could understand by listening once.\n"
    "\n"
    "Output only the English title and the English body."
)

ARM3_BLOCK = (
    "Adaptation level: NATURAL ENGLISH.\n"
    "Make the piece read like a natural English news feature. Keep the "
    "central metaphor, the theme, the facts, the selection of information, "
    "and the conclusion. You may reorder, merge, or reshape paragraphs, and "
    "adjust the wording of metaphors where English needs it. Still add "
    "nothing that is not in the Japanese article."
)

# ------------------------------------------------------------
# Standard共通Prompt(記事非依存、A-2/B-1で完全同一、Fable逐語指定)
# ------------------------------------------------------------
DEVELOPER_STD = (
    "You are an editor who rewrites English feature articles for learners "
    "of English at CEFR A2 level, while keeping the article just as "
    "enjoyable as the original.")

STANDARD_USER_TEMPLATE = (
    "Rewrite this English article for an A2-level English learner (CEFR "
    "A2).\n"
    "Simplify the language, not the story.\n"
    "\n"
    "Preserve the same story structure.\n"
    "Preserve the same interesting angle.\n"
    "Preserve the same surprise, in the same place in the story.\n"
    "Preserve the important metaphor or storytelling device.\n"
    "Preserve the ending logic.\n"
    "Do not turn the article into a summary.\n"
    "Do not remove entertaining details only because they are harder to "
    "express. Use simpler vocabulary and grammar instead.\n"
    "Do not add new facts or explanations.\n"
    "Keep every fact exactly as it is: names, numbers, who did what, cause "
    "and effect, the order of events, negations, and words of scope such as "
    "\"some\" or \"all\".\n"
    "Use simple, common words. Prefer short sentences, mostly one idea per "
    "sentence. Split long clauses. Avoid heavy relative clauses, heavy "
    "passive forms, and abstract noun phrases; say what people do "
    "instead.\n"
    "The English must still sound natural when read aloud. Do not write "
    "like a children's book, and do not write a flat list of short "
    "sentences.\n"
    "The article may be a little longer or shorter than the original, but "
    "do not shorten it into a summary.\n"
    "\n"
    "Output only the English title and the English body.\n"
    "\n"
    "[Article]\n"
    "{advanced_article}"
)


# ------------------------------------------------------------
# 共通ヘルパー
# ------------------------------------------------------------
def out_path(out_dir: str, *parts: str) -> str:
    return os.path.join(out_dir, *parts)


def save_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


def load_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _sha256_of_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def install_logger(out_dir: str) -> None:
    cl.install(out_path(out_dir, "raw_usage_log.jsonl"))


# ------------------------------------------------------------
# STEP: sources
# ------------------------------------------------------------
def cmd_sources(out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    sewer_actual = _sha256_of_file(SEWER_JA_PATH)
    meta_actual = _sha256_of_file(META_ADVANCED_PATH)

    problems = []
    if sewer_actual != SEWER_JA_EXPECTED_SHA256:
        problems.append(
            f"sewer sha256 mismatch: expected={SEWER_JA_EXPECTED_SHA256} "
            f"actual={sewer_actual}")
    if meta_actual != META_ADVANCED_EXPECTED_SHA256:
        problems.append(
            f"meta sha256 mismatch: expected={META_ADVANCED_EXPECTED_SHA256} "
            f"actual={meta_actual}")

    if problems:
        stop = {
            "stop_reason": "sourceファイルのsha256不一致",
            "problems": problems,
        }
        save_json(out_path(out_dir, "stop_reason.json"), stop)
        print("[STOP] " + "; ".join(problems))
        raise SystemExit(1)

    sewer_text = load_text(SEWER_JA_PATH)
    sewer_title = sewer_text.splitlines()[0].strip()
    meta_text = load_text(META_ADVANCED_PATH)
    meta_title = meta_text.splitlines()[0].strip()

    sources = {
        "sewer_ja_r2": {
            "management_id_of_origin": "NEWS-ITERATIVE-R2-PRODUCTION-WIRING-01 (adoption evidence) / NEWS-ITERATIVE-ENTERTAINMENT-TRIAL-01 (元Trial)",
            "path": SEWER_JA_PATH,
            "title": sewer_title,
            "sha256": sewer_actual,
            "status": "APPROVED_FOR_PRODUCTION (配線未完了)",
        },
        "meta_advanced_baseline": {
            "management_id_of_origin": "NEWS-JA-TO-EN-ADAPTATION-TRIAL-01 (arm3, Natural English)",
            "path": META_ADVANCED_PATH,
            "title": meta_title,
            "sha256": meta_actual,
            "status": "APPROVED_FOR_PRODUCTION (配線未完了、本Trialでは改変禁止のBaseline)",
        },
    }
    save_json(out_path(out_dir, "sources.json"), sources)
    print(f"[OK] sources.json written. sewer_sha256={sewer_actual[:16]}... "
          f"meta_sha256={meta_actual[:16]}...")


# ------------------------------------------------------------
# STEP: generate (A-1 -> A-2 -> B-1)
# ------------------------------------------------------------
def _call_and_record(client, pricing, developer: str, user_prompt: str,
                      stage_label: str, dst_output: str, dst_meta: str,
                      force: bool) -> dict:
    if os.path.exists(dst_output) and not force:
        print(f"[SKIP] existing: {dst_output}")
        return load_json(dst_meta)

    luna_in = er015base._price(pricing, "openai", "gpt-5.6-luna", "input_tokens")
    luna_cached = er015base._price(pricing, "openai", "gpt-5.6-luna", "cached_input_tokens")
    luna_out = er015base._price(pricing, "openai", "gpt-5.6-luna", "output_tokens")

    retried = False
    t0 = time.time()
    response = trial02.call_fresh(client, developer, user_prompt, WRITER_EFFORT, stage_label)
    text = (response.output_text or "").strip()
    if not text:
        retried = True
        print(f"[RETRY] stage={stage_label}: empty output, retrying once")
        response = trial02.call_fresh(client, developer, user_prompt, WRITER_EFFORT, stage_label)
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

    fallback_detected = (response.model != WRITER_MODEL)

    meta = {
        "stage": stage_label,
        "model_requested": WRITER_MODEL,
        "response_model_actual": response.model,
        "fallback_detected": fallback_detected,
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
        "retried": retried,
        "prompt_developer_char_count": len(developer),
        "prompt_user_char_count": len(user_prompt),
        "chain_method": "fresh_single_call",
        "previous_response_id": None,
        "web_search_used": False,
    }
    save_text(dst_output, text)
    save_json(dst_meta, meta)
    print(f"[OK] stage={stage_label}: {len(text)}字/chars "
          f"model={meta['response_model_actual']} id={response.id} "
          f"elapsed={elapsed}s cost_jpy={meta['cost_jpy']} retried={retried} "
          f"fallback={fallback_detected}")
    return meta


def cmd_generate(out_dir: str, budget_jpy: float, force: bool) -> None:
    os.makedirs(out_dir, exist_ok=True)
    sewer_ja_text = load_text(SEWER_JA_PATH)
    meta_advanced_text = load_text(META_ADVANCED_PATH)

    # prompt files (Fable指定artifact)
    save_text(out_path(out_dir, "prompt_advanced_a1.txt"),
              "DEVELOPER:\n" + DEVELOPER_A1 + "\n\n"
              "USER (COMMON_BLOCK[sewer置換版] + ARM3_BLOCK + [Japanese article]):\n" +
              COMMON_BLOCK_SEWER + "\n\n" + ARM3_BLOCK +
              "\n\n[Japanese article]\n" + sewer_ja_text)
    save_text(out_path(out_dir, "prompt_standard_common.txt"),
              "DEVELOPER:\n" + DEVELOPER_STD + "\n\n"
              "USER TEMPLATE ({advanced_article} is substituted):\n" +
              STANDARD_USER_TEMPLATE)
    diff_md = (
        "# prompt_diff_a1.md — A-1 Prompt Meta固有列挙 -> 下水道用列挙 置換差分\n\n"
        "DEVELOPER / ARM3_BLOCK / COMMON_BLOCKの冒頭2文・末尾2文・全体構成は"
        "一字も変えていない。変更したのはCOMMON_BLOCK内の "
        "\"Preserve the Japanese article's editorial angle, structure, and "
        "sense of surprise:\" に続く6項目の箇条書きのみ。\n\n"
        "## 置換前(Meta固有、NEWS-JA-TO-EN-ADAPTATION-TRIAL-01 arm3 逐語)\n\n"
        "```\n" + COMMON_BLOCK_ORIGINAL_META + "\n```\n\n"
        "## 置換後(下水道用、本Trialで使用)\n\n"
        "```\n" + COMMON_BLOCK_SEWER + "\n```\n\n"
        "## 対応関係\n\n"
        "| Meta(元) | 下水道(置換後) |\n"
        "|---|---|\n"
        "| opening expectation of \"AI makes the phone call\" | opening expectation triggered by the word \"merger\" (towns merging) |\n"
        "| reversal: a human was working behind the scenes | reversal: it's not towns merging, but household toilet/kitchen/bath water treated together near the home |\n"
        "| framing: lead role / backstage / understudy | framing: sewer as invisible main artery vs. small household-level treatment |\n"
        "| theme: \"a human behind the AI phone call\" | theme: \"protect convenience without making the system bigger, by moving treatment closer to home\" |\n"
        "| privacy as necessary later information | installation/inspection/cleaning as necessary later information |\n"
        "| ending: stage / behind the curtain | ending: sewer's future may arrive in a surprisingly familiar, nearby place |\n"
    )
    save_text(out_path(out_dir, "prompt_diff_a1.md"), diff_md)

    install_logger(out_dir)
    client = vfl01.get_client()
    pricing = er015base._load_pricing()

    total_jpy = 0.0
    metas = {}

    # --- A-1: 下水道 Advanced ---
    a1_user = COMMON_BLOCK_SEWER + "\n\n" + ARM3_BLOCK + "\n\n[Japanese article]\n" + sewer_ja_text
    a1_output = out_path(out_dir, "a1_advanced_sewer.md")
    a1_meta = out_path(out_dir, "a1_advanced_sewer.meta.json")
    m = _call_and_record(client, pricing, DEVELOPER_A1, a1_user, "a1_advanced_sewer",
                          a1_output, a1_meta, force)
    metas["a1_advanced_sewer"] = m
    total_jpy += m.get("cost_jpy", 0.0)
    if total_jpy > budget_jpy:
        stop = {"stop_reason": "budget exceeded after A-1", "total_jpy": total_jpy,
                "budget_jpy": budget_jpy}
        save_json(out_path(out_dir, "stop_reason.json"), stop)
        print(f"[STOP] budget exceeded after A-1: {total_jpy} > {budget_jpy}")
        raise SystemExit(1)

    # --- A-2: 下水道 Standard(A-1出力を入力に使う) ---
    a1_text = load_text(a1_output)
    a2_user = STANDARD_USER_TEMPLATE.format(advanced_article=a1_text)
    a2_output = out_path(out_dir, "a2_standard_sewer.md")
    a2_meta = out_path(out_dir, "a2_standard_sewer.meta.json")
    m = _call_and_record(client, pricing, DEVELOPER_STD, a2_user, "a2_standard_sewer",
                          a2_output, a2_meta, force)
    metas["a2_standard_sewer"] = m
    total_jpy += m.get("cost_jpy", 0.0)
    if total_jpy > budget_jpy:
        stop = {"stop_reason": "budget exceeded after A-2", "total_jpy": total_jpy,
                "budget_jpy": budget_jpy}
        save_json(out_path(out_dir, "stop_reason.json"), stop)
        print(f"[STOP] budget exceeded after A-2: {total_jpy} > {budget_jpy}")
        raise SystemExit(1)

    # --- B-1: Meta Standard(Meta Advanced Baselineを入力に使う、改変禁止) ---
    b1_user = STANDARD_USER_TEMPLATE.format(advanced_article=meta_advanced_text)
    b1_output = out_path(out_dir, "b1_standard_meta.md")
    b1_meta = out_path(out_dir, "b1_standard_meta.meta.json")
    m = _call_and_record(client, pricing, DEVELOPER_STD, b1_user, "b1_standard_meta",
                          b1_output, b1_meta, force)
    metas["b1_standard_meta"] = m
    total_jpy += m.get("cost_jpy", 0.0)
    if total_jpy > budget_jpy:
        stop = {"stop_reason": "budget exceeded after B-1 (all 3 calls already made)",
                "total_jpy": total_jpy, "budget_jpy": budget_jpy}
        save_json(out_path(out_dir, "stop_reason.json"), stop)
        print(f"[STOP] budget exceeded after B-1: {total_jpy} > {budget_jpy}")
        raise SystemExit(1)

    print(f"[DONE] generate complete. total_cost_jpy={round(total_jpy, 4)} "
          f"budget_jpy={budget_jpy}")


# ------------------------------------------------------------
# STEP: analyze (level metrics + fact diff machine, 標準ライブラリのみ)
# ------------------------------------------------------------
VOWELS = "aeiouy"


def _strip_title(text: str) -> tuple:
    lines = text.strip().splitlines()
    title = lines[0].strip() if lines else ""
    body = "\n".join(lines[1:]).strip()
    return title, body


def _count_syllables(word: str) -> int:
    word = word.lower()
    word = re.sub(r"[^a-z]", "", word)
    if not word:
        return 0
    groups = re.findall(r"[aeiouy]+", word)
    n = len(groups)
    if word.endswith("e") and n > 1:
        n -= 1
    return max(n, 1)


SUBORDINATORS = [
    "that", "which", "who", "whom", "whose", "although", "though", "while",
    "if", "because", "since", "whereas", "unless", "whether", "when",
]


def _level_metrics(text: str) -> dict:
    title, body = _strip_title(text)
    words = re.findall(r"[A-Za-z']+", body)
    word_count = len(words)
    # 文分割(簡易): .!? の後の空白を境界とする
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", body) if s.strip()]
    sentence_count = len(sentences)
    avg_sentence_len = round(word_count / sentence_count, 2) if sentence_count else 0
    syllables = sum(_count_syllables(w) for w in words)
    avg_syllables_per_word = round(syllables / word_count, 3) if word_count else 0
    long_sentences = 0
    for s in sentences:
        sw = re.findall(r"[A-Za-z']+", s)
        if len(sw) >= 20:
            long_sentences += 1
    long_sentence_ratio = round(long_sentences / sentence_count, 3) if sentence_count else 0
    subordinator_count = 0
    lower_body = body.lower()
    for sub in SUBORDINATORS:
        subordinator_count += len(re.findall(r"\b" + re.escape(sub) + r"\b", lower_body))
    subordinators_per_100_words = round(subordinator_count / word_count * 100, 2) if word_count else 0
    # 簡易Flesch-Kincaid Grade(標準ライブラリのみ、textstat未導入のため参考値)
    fk_grade = None
    if sentence_count and word_count:
        fk_grade = round(0.39 * (word_count / sentence_count) +
                          11.8 * (syllables / word_count) - 15.59, 2)

    return {
        "title": title,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_sentence_length_words": avg_sentence_len,
        "avg_syllables_per_word_heuristic": avg_syllables_per_word,
        "long_sentence_ratio_ge20words": long_sentence_ratio,
        "subordinator_relative_count": subordinator_count,
        "subordinators_per_100_words": subordinators_per_100_words,
        "flesch_kincaid_grade_heuristic": fk_grade,
        "cefr_estimate": "なし(textstat等の既存CEFR推定手段が.venvに無く、新規install未実施のためN/A。上記はstd libのみによる参考ヒューリスティック値)",
    }


def cmd_analyze_levels(out_dir: str) -> None:
    files = {
        "sewer_advanced_a1": out_path(out_dir, "a1_advanced_sewer.md"),
        "sewer_standard_a2": out_path(out_dir, "a2_standard_sewer.md"),
        "meta_advanced_baseline": META_ADVANCED_PATH,
        "meta_standard_b1": out_path(out_dir, "b1_standard_meta.md"),
    }
    metrics = {}
    for key, path in files.items():
        text = load_text(path)
        metrics[key] = _level_metrics(text)
    save_json(out_path(out_dir, "level_metrics.json"), metrics)

    md_lines = ["# level_metrics.md — Level比較(参考値、機械判定は最終判断に用いない)\n",
                "| 記事 | words | sentences | avg words/sent | avg syll/word | long-sent(>=20w)率 | subordinator/100w | FK grade(heuristic) |",
                "|---|---|---|---|---|---|---|---|"]
    label_map = {
        "sewer_advanced_a1": "下水道 Advanced(A-1)",
        "sewer_standard_a2": "下水道 Standard(A-2)",
        "meta_advanced_baseline": "Meta Advanced(Baseline)",
        "meta_standard_b1": "Meta Standard(B-1)",
    }
    for key in ["sewer_advanced_a1", "sewer_standard_a2", "meta_advanced_baseline", "meta_standard_b1"]:
        m = metrics[key]
        md_lines.append(
            f"| {label_map[key]} | {m['word_count']} | {m['sentence_count']} | "
            f"{m['avg_sentence_length_words']} | {m['avg_syllables_per_word_heuristic']} | "
            f"{m['long_sentence_ratio_ge20words']} | {m['subordinators_per_100_words']} | "
            f"{m['flesch_kincaid_grade_heuristic']} |")
    md_lines.append("\nCEFR推定: なし(既存の.venvにtextstat等の推定ツールが無く、"
                     "新規install未実施のためN/A。上記は標準ライブラリのみによる"
                     "簡易ヒューリスティック参考値であり、機械判定を最終判断には"
                     "用いない)。")
    save_text(out_path(out_dir, "level_metrics.md"), "\n".join(md_lines))
    print("[OK] level_metrics.json / level_metrics.md written")


SCOPE_WORDS = ["some", "all", "every", "only", "part", "parts"]
NEGATION_WORDS = ["not", "no", "never", "n't"]


def _fact_tokens(text: str) -> dict:
    _, body = _strip_title(text)
    numbers = sorted(set(re.findall(r"\b\d[\d,]*\b", body)))
    proper_nouns = sorted(set(re.findall(r"\b[A-Z][a-z]+\b", body)))
    quoted = sorted(set(re.findall(r"[“\"]([^”\"]+)[”\"]", body)))
    negations = {}
    lower = body.lower()
    for w in NEGATION_WORDS:
        negations[w] = len(re.findall(r"\b" + re.escape(w) + r"\b", lower))
    scope = {}
    for w in SCOPE_WORDS:
        scope[w] = len(re.findall(r"\b" + re.escape(w) + r"\b", lower))
    return {
        "numbers": numbers,
        "proper_nouns": proper_nouns,
        "quoted_phrases": quoted,
        "negation_counts": negations,
        "scope_word_counts": scope,
    }


def cmd_analyze_fact_diff(out_dir: str) -> None:
    pairs = {
        "sewer_A1_to_A2": (out_path(out_dir, "a1_advanced_sewer.md"),
                            out_path(out_dir, "a2_standard_sewer.md")),
        "meta_advanced_to_B1": (META_ADVANCED_PATH,
                                 out_path(out_dir, "b1_standard_meta.md")),
    }
    result = {}
    for key, (adv_path, std_path) in pairs.items():
        adv = _fact_tokens(load_text(adv_path))
        std = _fact_tokens(load_text(std_path))
        result[key] = {
            "advanced": adv,
            "standard": std,
            "numbers_missing_in_standard": sorted(set(adv["numbers"]) - set(std["numbers"])),
            "numbers_added_in_standard": sorted(set(std["numbers"]) - set(adv["numbers"])),
            "proper_nouns_missing_in_standard": sorted(set(adv["proper_nouns"]) - set(std["proper_nouns"])),
            "proper_nouns_added_in_standard": sorted(set(std["proper_nouns"]) - set(adv["proper_nouns"])),
        }
    save_json(out_path(out_dir, "fact_diff_machine.json"), result)
    print("[OK] fact_diff_machine.json written")


def cmd_analyze(out_dir: str) -> None:
    cmd_analyze_levels(out_dir)
    cmd_analyze_fact_diff(out_dir)


# ------------------------------------------------------------
# STEP: assemble (cost.json)
# ------------------------------------------------------------
def cmd_assemble(out_dir: str) -> None:
    stages = ["a1_advanced_sewer", "a2_standard_sewer", "b1_standard_meta"]
    calls = []
    total_jpy = 0.0
    for s in stages:
        meta_path = out_path(out_dir, f"{s}.meta.json")
        if not os.path.exists(meta_path):
            print(f"[WARN] missing meta: {meta_path}")
            continue
        m = load_json(meta_path)
        calls.append(m)
        total_jpy += m.get("cost_jpy", 0.0)
    cost = {
        "calls": calls,
        "total_cost_jpy": round(total_jpy, 4),
        "budget_jpy": 5,
        "within_budget": total_jpy <= 5,
    }
    save_json(out_path(out_dir, "cost.json"), cost)
    print(f"[OK] cost.json written. total_cost_jpy={round(total_jpy, 4)} "
          f"within_budget={cost['within_budget']}")


# ------------------------------------------------------------
# main
# ------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--step", required=True,
                     choices=["sources", "generate", "analyze", "assemble"])
    ap.add_argument("--budget-jpy", type=float, default=5.0)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if args.step == "sources":
        cmd_sources(args.out_dir)
    elif args.step == "generate":
        cmd_generate(args.out_dir, args.budget_jpy, args.force)
    elif args.step == "analyze":
        cmd_analyze(args.out_dir)
    elif args.step == "assemble":
        cmd_assemble(args.out_dir)


if __name__ == "__main__":
    main()
