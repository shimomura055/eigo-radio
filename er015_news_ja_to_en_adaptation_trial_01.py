# ============================================================
# er015_news_ja_to_en_adaptation_trial_01.py
# NEWS-JA-TO-EN-ADAPTATION-TRIAL-01 (ユーザー指示、2026-09-24)
# ============================================================
# 目的: 完成済みの日本語R2(Meta Muse「AI電話代行の裏に人間コンシェルジュ」)
# を新しく書き直すのではなく、Editorial design(見立て・主題・情報順序・
# 結び)を維持したまま英語へAdaptする方式を検証する。Faithful/Balanced/
# Natural Englishの3 armで、Adaptationの自由度を変えたときにEntertainment
# 性がどこまで残るかを観察する。
#
# 固定: 日本語R2は逐語再利用(新規生成しない)/各Armは1 callのみ(Original
# ->R1->R2連鎖なし)/previous_response_idなし/Web Searchなし/Ledgerなし/
# Production contract(Point One/Two/In one line/Key Phrase/Audio)なし/
# Title+Body onlyの英語出力/model=gpt-5.6-luna, effort=high(全arm同一)。
#
# Production実装ではない。Production code/SSOTは変更しない。
#
# 依存(いずれも無変更・import再利用のみ):
#   - er003_v1_en_direct_vfl_01_generate (vfl01): get_client
#   - er005_cost_logger (cl): usage log install
#   - er015_news_core_idea_editorial_trial_01 (er015base): _load_pricing,
#     _price, USD_TO_JPY
#   - er015_news_iterative_entertainment_trial_02 (trial02): call_fresh
#     (単発call、previous_response_idは使わない)。call_freshは内部で
#     trial02自身のTHEME_TAG("NEWS_ITERATIVE_ENTERTAINMENT_TRIAL_02")を
#     cl.logging_contextへ渡すため、raw_usage_log.jsonlの3 callはその
#     themeで記録される(NEWS-META-ENGLISH-PROMPT-VARIATION-TRIAL-01と
#     同一の既知挙動。out_dirごとにログファイルが分かれるため混線しない)。
#   - er015_news_original_baseline_repro_01 (repro01): WRITER_MODEL,
#     WRITER_EFFORT
#
# Arm 1/2/3のPrompt(developer・共通制約ブロック・arm別ブロック)はFable
# 固定(delegation_log記載の逐語)。本ファイルはそれを定数として保持する
# のみ。
#
# サブコマンド:
#   --arms arm1,arm2,arm3 --out-dir <OUT> [--force]
#       : 入力日本語R2のsha256確認 -> 各armへ1 call(冪等、--forceで再生成)
#   --assemble-only --out-dir <OUT>
#       : 生成済み3 armからtitles/metrics/fact_diff_machine/structure_map/
#         unmatched_sentences/blind.md/blind_key.json/comparison_all.md/
#         cost.jsonを組み立て
# ============================================================
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import time

import er005_cost_logger as cl
import er015_news_core_idea_editorial_trial_01 as er015base
import er015_news_iterative_entertainment_trial_02 as trial02
import er015_news_original_baseline_repro_01 as repro01
import er003_v1_en_direct_vfl_01_generate as vfl01

THEME_TAG_LOCAL = "NEWS_JA_TO_EN_ADAPTATION_TRIAL_01"  # 参考表示用(実ログはtrial02.THEME_TAG)

WRITER_MODEL = repro01.WRITER_MODEL       # "gpt-5.6-luna"
WRITER_EFFORT = repro01.WRITER_EFFORT     # "high"

ALL_ARMS = ["arm1", "arm2", "arm3"]

# ------------------------------------------------------------
# 入力: 日本語R2(逐語再利用、sha256で一致確認)
# ------------------------------------------------------------
IN_PATH = os.path.join(
    "docs", "evidence", "news_iterative_r2_adoption_2026-09-24", "articles",
    "ai_phone_revision2.md")
IN_EXPECTED_SHA256 = (
    "474c2a1669b6f90f835d3901cbe6b4fd80f556edf440f0c610fb3589767b1a48")

# 比較参考(生成完了後にのみ読み込む): B/C2のR2
REF_B_R2_PATH = os.path.join(
    "er015_output", "news_meta_english_prompt_variation_trial_01", "arms", "B",
    "revision2.md")
REF_C2_R2_PATH = os.path.join(
    "er015_output", "news_meta_english_prompt_variation_trial_01", "arms", "C2",
    "revision2.md")

# ------------------------------------------------------------
# Prompt(Fable固定・逐語。変更禁止)
# ------------------------------------------------------------
DEVELOPER = (
    "You are an editor who adapts finished Japanese feature articles into "
    "natural English for listeners who are learning English.")

COMMON_BLOCK = (
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

ARM1_BLOCK = (
    "Adaptation level: FAITHFUL.\n"
    "Keep the same paragraph order, the same order of information, the same "
    "metaphors, and the same ending. Follow the Japanese sentence by "
    "sentence as closely as natural English allows. Change wording only "
    "where a literal rendering would be clearly unnatural in English. Do "
    "not merge, split, or reorder paragraphs."
)

ARM2_BLOCK = (
    "Adaptation level: BALANCED.\n"
    "Keep the editorial angle, the story structure, the metaphors, the "
    "selection of information, and the logic of the ending exactly as in "
    "the Japanese. Within that, you may reconstruct sentences, adjust "
    "paragraph rhythm, and avoid repetition so that the piece reads as if "
    "it had been written in English. Do not change what makes the piece "
    "interesting."
)

ARM3_BLOCK = (
    "Adaptation level: NATURAL ENGLISH.\n"
    "Make the piece read like a natural English news feature. Keep the "
    "central metaphor, the theme, the facts, the selection of information, "
    "and the conclusion. You may reorder, merge, or reshape paragraphs, and "
    "adjust the wording of metaphors where English needs it. Still add "
    "nothing that is not in the Japanese article."
)

ARM_BLOCKS = {"arm1": ARM1_BLOCK, "arm2": ARM2_BLOCK, "arm3": ARM3_BLOCK}
ARM_LABELS = {"arm1": "Faithful", "arm2": "Balanced", "arm3": "Natural English"}

# ------------------------------------------------------------
# 構造対応推定用: 日本語R2 10段落の主要名詞アンカー(英語訳語candidate)。
# Fable指示「文の主要名詞の一致で推定」に基づき、各JA段落の中心概念を
# 事前に英語へ翻訳したキーワード集合として用意し、英語出力の段落ごとに
# 出現回数を機械的にカウントして最尤の対応段落を推定する(判定はFable)。
# ------------------------------------------------------------
JA_PARAGRAPH_ANCHORS = [
    # (index, 日本語段落の要約, 英語キーワード候補)
    (1, "AIに電話を任せる未来イメージ",
     ["ai", "phone", "call", "future", "convenient", "handle"]),
    (2, "主役はMuse、電話代行機能",
     ["muse", "agent", "meta", "lead", "main role"]),
    (3, "舞台裏をのぞくと意外な光景",
     ["backstage", "behind the scenes", "curtain", "peek", "unexpected"]),
    (4, "社内試験で人間の契約スタッフ・人間コンシェルジュ",
     ["human", "contract staff", "concierge", "internal test", "trial"]),
    (5, "看板はAI電話代行、実は人間の代役",
     ["sign", "billboard", "understudy", "stand-in", "stage"]),
    (6, "面白さの核: ピアノに別演奏者が隠れていた比喩",
     ["piano", "hidden", "player", "interesting", "surprising"]),
    (7, "人間が手伝うこと自体は自然という一呼吸",
     ["help", "natural", "not bad", "weak point", "assist"]),
    (8, "プライバシー懸念(後半情報)",
     ["privacy", "leak", "employee", "concern", "outside"]),
    (9, "Reuters確認、幹部が機能取りやめ",
     ["reuters", "executive", "rolled back", "internal post", "paused"]),
    (10, "結び: 舞台の上/幕の後ろ、安心して任せられる",
     ["stage", "curtain", "trust", "explanation", "behind"]),
]


# ------------------------------------------------------------
# 共通ヘルパー
# ------------------------------------------------------------
def out_path(out_dir: str, *parts: str) -> str:
    return os.path.join(out_dir, *parts)


def arm_dir(out_dir: str, arm: str) -> str:
    return out_path(out_dir, "arms", arm)


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


def _check_input_sha256(out_dir: str) -> str:
    actual = _sha256_of_file(IN_PATH)
    if actual != IN_EXPECTED_SHA256:
        stop = {
            "stop_reason": "入力日本語R2を正確に再利用できない(sha256不一致)",
            "expected_sha256": IN_EXPECTED_SHA256,
            "actual_sha256": actual,
            "source_path": IN_PATH,
        }
        save_json(out_path(out_dir, "stop_reason.json"), stop)
        print(f"[STOP] sha256 mismatch: expected={IN_EXPECTED_SHA256} actual={actual}")
        raise SystemExit(1)
    return actual


def install_logger(out_dir: str) -> None:
    cl.install(out_path(out_dir, "raw_usage_log.jsonl"))


def build_user_prompt(arm: str, ja_text: str) -> str:
    return (COMMON_BLOCK + "\n\n" + ARM_BLOCKS[arm] + "\n\n"
            "[Japanese article]\n" + ja_text)


# ------------------------------------------------------------
# 生成
# ------------------------------------------------------------
def cmd_generate(out_dir: str, arms: list, force: bool) -> None:
    os.makedirs(out_dir, exist_ok=True)
    _check_input_sha256(out_dir)
    ja_text = load_text(IN_PATH)
    save_text(out_path(out_dir, "input_ja_r2.md"), ja_text)
    save_json(out_path(out_dir, "input_ja_r2.sha256.json"),
              {"path": IN_PATH, "sha256": IN_EXPECTED_SHA256})

    install_logger(out_dir)
    client = vfl01.get_client()

    pricing = er015base._load_pricing()
    luna_in = er015base._price(pricing, "openai", "gpt-5.6-luna", "input_tokens")
    luna_cached = er015base._price(pricing, "openai", "gpt-5.6-luna", "cached_input_tokens")
    luna_out = er015base._price(pricing, "openai", "gpt-5.6-luna", "output_tokens")

    for arm in arms:
        if arm not in ARM_BLOCKS:
            print(f"[SKIP] unknown arm (not arm1/arm2/arm3): {arm}")
            continue
        dst = arm_dir(out_dir, arm)
        os.makedirs(dst, exist_ok=True)

        user_prompt = build_user_prompt(arm, ja_text)
        save_text(out_path(dst, "prompt_developer.txt"), DEVELOPER)
        save_text(out_path(dst, "prompt_user.txt"), user_prompt)

        output_path = out_path(dst, "output.md")
        meta_path = out_path(dst, "api_meta.json")
        if os.path.exists(output_path) and not force:
            print(f"[SKIP] existing: {output_path}")
            continue

        retried = False
        stage_label = arm
        t0 = time.time()
        response = trial02.call_fresh(client, DEVELOPER, user_prompt, WRITER_EFFORT, stage_label)
        text = (response.output_text or "").strip()
        if not text:
            retried = True
            print(f"[RETRY] arm={arm}: empty output, retrying once")
            response = trial02.call_fresh(client, DEVELOPER, user_prompt, WRITER_EFFORT, stage_label)
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

        meta = {
            "arm": arm,
            "adaptation_level": ARM_LABELS[arm],
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
            "retried": retried,
            "prompt_developer_char_count": len(DEVELOPER),
            "prompt_user_char_count": len(user_prompt),
            "chain_method": "fresh_single_call",
            "previous_response_id": None,
            "web_search_used": False,
        }
        save_text(output_path, text)
        save_json(meta_path, meta)
        print(f"[OK] arm={arm} ({ARM_LABELS[arm]}): {len(text)}字/chars "
              f"model={meta['response_model_actual']} id={response.id} "
              f"elapsed={elapsed}s cost_jpy={meta['cost_jpy']} retried={retried}")


# ------------------------------------------------------------
# assemble-only
# ------------------------------------------------------------
def _first_line_title(text: str) -> str:
    for line in text.split("\n"):
        line = line.strip()
        if line:
            return line.lstrip("#").strip()
    return ""


def _body_paragraphs(text: str) -> list:
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paras:
        return []
    return paras[1:] if len(paras) > 1 else []


def _word_count(text: str) -> int:
    return len(text.split())


def _paragraph_count(text: str) -> int:
    return len(_body_paragraphs(text))


NUMBER_RE = re.compile(r"\d[\d,\.]*")
CAP_WORD_RE = re.compile(r"\b[A-Z][A-Za-z]*\b")
QUOTE_RE = re.compile(r'["“]([^"”]{1,200})["”]')

ALLOWED_REFERENCE_TOKENS = {
    "Meta", "Muse", "Reuters", "Human", "Concierge", "Contract", "Staff",
    "Privacy", "Understudy", "Stage", "Backstage", "AI", "Behind", "Curtain",
}


def _fact_diff_for_text(text: str) -> dict:
    numbers = sorted(set(NUMBER_RE.findall(text)))
    cap_words = sorted(set(CAP_WORD_RE.findall(text)))
    quotes = QUOTE_RE.findall(text)
    cap_words_not_reference = [w for w in cap_words if w not in ALLOWED_REFERENCE_TOKENS]
    return {
        "numbers": numbers,
        "capitalized_words": cap_words,
        "capitalized_words_not_in_reference_list": cap_words_not_reference,
        "quoted_spans": quotes,
        "note": ("capitalized_words_not_in_reference_listは文頭の通常語も含む機械的"
                 "抽出であり、Fact追加の断定ではない(観察のみ、判定はFable)。"),
    }


SENTENCE_SPLIT_RE = re.compile(r'(?<=[.!?])\s+(?=[A-Z"“])')


def _split_sentences(text: str) -> list:
    body = "\n\n".join(_body_paragraphs(text))
    sentences = []
    for para in body.split("\n\n"):
        for s in SENTENCE_SPLIT_RE.split(para.strip()):
            s = s.strip()
            if s:
                sentences.append(s)
    return sentences


def _structure_map_for_text(text: str) -> dict:
    body_paras = _body_paragraphs(text)
    result = {}
    for idx, summary_ja, keywords in JA_PARAGRAPH_ANCHORS:
        hits_per_para = []
        for p_i, para in enumerate(body_paras):
            low = para.lower()
            hits = sum(low.count(kw) for kw in keywords)
            hits_per_para.append(hits)
        best = max(range(len(hits_per_para)), key=lambda i: hits_per_para[i]) if hits_per_para else None
        best_hits = hits_per_para[best] if best is not None else 0
        result[f"ja_para_{idx}"] = {
            "ja_summary": summary_ja,
            "anchor_keywords": keywords,
            "best_match_en_paragraph_index": best if best_hits > 0 else None,
            "best_match_hit_count": best_hits,
            "all_paragraph_hit_counts": hits_per_para,
        }
    return result


def _unmatched_sentences_for_text(text: str) -> list:
    all_keywords = []
    for _, _, keywords in JA_PARAGRAPH_ANCHORS:
        all_keywords.extend(keywords)
    unmatched = []
    for s in _split_sentences(text):
        low = s.lower()
        if not any(kw in low for kw in all_keywords):
            unmatched.append(s)
    return unmatched


def cmd_assemble(out_dir: str) -> None:
    arm_texts = {}
    arm_metas = {}
    for arm in ALL_ARMS:
        d = arm_dir(out_dir, arm)
        p = out_path(d, "output.md")
        mp = out_path(d, "api_meta.json")
        if not os.path.exists(p) or not os.path.exists(mp):
            print(f"[STOP] missing arm output/meta for {arm}; run generation first")
            raise SystemExit(1)
        arm_texts[arm] = load_text(p)
        arm_metas[arm] = load_json(mp)

    titles = {arm: _first_line_title(t) for arm, t in arm_texts.items()}
    save_json(out_path(out_dir, "titles.json"), titles)

    metrics = {arm: {"char_count": len(t), "word_count": _word_count(t),
                      "paragraph_count": _paragraph_count(t)}
               for arm, t in arm_texts.items()}
    save_json(out_path(out_dir, "metrics.json"), metrics)

    fact_diff = {arm: _fact_diff_for_text(t) for arm, t in arm_texts.items()}
    save_json(out_path(out_dir, "fact_diff_machine.json"), fact_diff)

    structure_map = {arm: _structure_map_for_text(t) for arm, t in arm_texts.items()}
    save_json(out_path(out_dir, "structure_map.json"), structure_map)

    unmatched = {arm: _unmatched_sentences_for_text(t) for arm, t in arm_texts.items()}
    save_json(out_path(out_dir, "unmatched_sentences.json"), unmatched)

    # comparison_all.md(生成完了後にのみ、日本語R2/参考B・C2を参照)
    ja_r2_path = out_path(out_dir, "input_ja_r2.md")
    ja_r2 = load_text(ja_r2_path) if os.path.exists(ja_r2_path) else "(ファイルなし)"
    ref_b = load_text(REF_B_R2_PATH) if os.path.exists(REF_B_R2_PATH) else "(ファイルなし)"
    ref_c2 = load_text(REF_C2_R2_PATH) if os.path.exists(REF_C2_R2_PATH) else "(ファイルなし)"

    lines = ["# comparison_all.md (NEWS-JA-TO-EN-ADAPTATION-TRIAL-01)", "",
             "## 日本語R2(Original、Meta Muse AI電話代行)", "", ja_r2, "", "---", ""]
    for arm in ALL_ARMS:
        t = arm_texts[arm]
        lines += [f"## {arm} ({ARM_LABELS[arm]})", "", t, "", "---", ""]
    lines += ["## 参考B(NEWS-META-ENGLISH-PROMPT-VARIATION-TRIAL-01、日本語Prompt逐語+英語出力指定)",
              "", ref_b, "", "---", ""]
    lines += ["## 参考C2(NEWS-META-ENGLISH-PROMPT-VARIATION-TRIAL-01、意味強調英語Prompt)",
              "", ref_c2, "", "---", ""]
    save_text(out_path(out_dir, "comparison_all.md"), "\n".join(lines))

    # blind.md / blind_key.json(3 armをX/Y/Zでランダム化、arm名なし)
    symbols = ["X", "Y", "Z"]
    arms_shuffled = list(ALL_ARMS)
    random.shuffle(arms_shuffled)
    mapping = dict(zip(symbols, arms_shuffled))  # symbol -> arm
    reverse_mapping = {arm: sym for sym, arm in mapping.items()}
    save_json(out_path(out_dir, "blind_key.json"), {
        "symbol_to_arm": mapping,
        "arm_to_symbol": reverse_mapping,
        "note": "先にblind.mdを読み、このファイルは参考評価の後に開く想定。",
    })
    blind_lines = ["# blind.md (NEWS-JA-TO-EN-ADAPTATION-TRIAL-01)", "",
                   "3つの英語版をランダムな記号で提示する(arm名・adaptation levelは書かない)。", ""]
    for sym in symbols:
        arm = mapping[sym]
        blind_lines += [f"## {sym}", "", arm_texts[arm], "", "---", ""]
    save_text(out_path(out_dir, "blind.md"), "\n".join(blind_lines))

    # cost.json(3 call合計。api_meta.jsonのcost_usd/cost_jpyを集計)
    per_call = []
    total_usd = 0.0
    total_input = total_cached = total_output = total_reasoning = 0
    any_retry = False
    for arm in ALL_ARMS:
        m = arm_metas[arm]
        u = m.get("usage", {})
        per_call.append({
            "arm": arm,
            "response_model_actual": m.get("response_model_actual"),
            "response_id": m.get("response_id"),
            "usage": u,
            "elapsed_seconds": m.get("elapsed_seconds"),
            "cost_usd": m.get("cost_usd"),
            "cost_jpy": m.get("cost_jpy"),
            "retried": m.get("retried"),
            "prompt_developer_char_count": m.get("prompt_developer_char_count"),
            "prompt_user_char_count": m.get("prompt_user_char_count"),
        })
        total_usd += m.get("cost_usd") or 0.0
        total_input += u.get("input_tokens") or 0
        total_cached += u.get("cached_input_tokens") or 0
        total_output += u.get("output_tokens") or 0
        total_reasoning += u.get("reasoning_tokens") or 0
        any_retry = any_retry or bool(m.get("retried"))

    result = {
        "theme_local_label": THEME_TAG_LOCAL,
        "raw_log_theme_actual": trial02.THEME_TAG,
        "calls": len(ALL_ARMS),
        "per_call": per_call,
        "total_input_tokens": total_input,
        "total_cached_input_tokens": total_cached,
        "total_output_tokens": total_output,
        "total_reasoning_tokens": total_reasoning,
        "total_usd": round(total_usd, 6),
        "total_jpy": round(total_usd * er015base.USD_TO_JPY, 2),
        "usd_to_jpy": er015base.USD_TO_JPY,
        "budget_jpy": 10,
        "within_budget": round(total_usd * er015base.USD_TO_JPY, 2) <= 10,
        "any_retry_occurred": any_retry,
    }
    save_json(out_path(out_dir, "cost.json"), result)

    print(f"[OK] assemble complete: titles/metrics/fact_diff_machine/structure_map/"
          f"unmatched_sentences/comparison_all.md/blind.md/blind_key.json/cost.json "
          f"written. calls={result['calls']} total_jpy={result['total_jpy']} "
          f"within_budget={result['within_budget']} any_retry={any_retry}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--arms", default=None,
                         help="comma-separated arm labels among arm1,arm2,arm3")
    parser.add_argument("--assemble-only", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.assemble_only:
        cmd_assemble(args.out_dir)
        return

    os.makedirs(args.out_dir, exist_ok=True)
    arms = [a.strip() for a in args.arms.split(",") if a.strip()] if args.arms else ALL_ARMS
    cmd_generate(args.out_dir, arms, args.force)


if __name__ == "__main__":
    main()
