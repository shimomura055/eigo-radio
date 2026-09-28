# ============================================================
# er045_family_x_no_heading_segmentation_trial_01.py
# FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01
# ============================================================
# Trial(text限定、TTS/ASR呼び出しなし)。Family X(Entertainment News)の
# 本文途中の見出しを廃止し、日本語完成記事(AN3-T0 R2)をほぼそのまま
# 忠実に英訳した上で、段落境界のみを使った決定論的アルゴリズムで
# Part1/Part2/Part3へ3分割する構成を検証する。詳細仕様は
# `docs/pm/design_family_x_no_heading_segmentation_trial_01.md`を参照。
#
# Production code(`er003_v1_n3_01_advanced_adaptation_generate.py`他)は
# 一切編集しない。本ファイルはそれらをimportし、既存Production primitive
# (`vfl01.run_writer_no_search`/`vfl01.run_deviation_check`/
# `vfl01.get_client`/`routing.require_model_or_override`)をそのまま
# 呼び出すのみ。Production Prompt定数(`ADVANCED_VOCAB_RULE_V2_BLOCK`)は
# importして逐語のまま流用する(コピペしない、sha256はimport元モジュールが
# fail-closedで検証済み)。
#
# 新しい記事生成・Source取得は行わない。入力はAN3-T0で既に生成済みの
# JA R2最終テキスト(disk上の`ja_writer/revision2.md`)。Baseline
# English(見出しあり、現行Advanced)は、Meta はdisk上の`b1b/article.md`
# (REPORT転記とdiff一致確認済み)、Hormuz はdisk上のarticle.mdが
# AN3-T0後の別run生成物で上書きされているため(diffで非一致を確認)、
# `FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_REPORT.md`の
# `## 記事本文全文`セクションからプログラム的に抽出する。
#
# 実行方法:
#   .venv/Scripts/python.exe er045_family_x_no_heading_segmentation_trial_01.py \
#       --article hormuz \
#       --source-dir er019_output/family_x_entertainment_production_runner_01/an3_t0_wiring_regression_01 \
#       --out-dir er045_output/family_x_no_heading_segmentation_trial_01/hormuz \
#       --budget-jpy 30
# ============================================================
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import re
import time

from dotenv import load_dotenv

import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_advanced_adaptation_generate as adv_gen
import er006_model_routing_contract_01 as routing
import er039_family_xy_concreteness_control_trial_02 as t2

load_dotenv()

REPORT_PATH = "FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_REPORT.md"

# FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01 修正1回目(委任_02)で
# 追加: v1実行で使ったsource-dirの既定値(v2系--stage呼び出しは
# --source-dir省略時にこれを使う。v1実行時と同一パス、read-onlyで参照する
# だけで値自体は変更しない)。
SOURCE_DIR = "er019_output/family_x_entertainment_production_runner_01/an3_t0_wiring_regression_01"

# Baseline English(見出しあり)の取得元。Hormuzのみdisk article.mdを使わず
# REPORT転記から抽出する理由は本ファイル冒頭コメント参照。
BASELINE_SOURCE = {
    "hormuz": {"mode": "report", "report_heading": "Hormuz"},
    "meta": {"mode": "disk", "relpath": "meta/b1b/article.md"},
}

# 既存Baseline Deviation Check結果(追加API呼び出しをせずreuseする)。
BASELINE_DEVIATION_PATH = {
    "hormuz": "hormuz/b1b/audit/deviation_checks/advanced_attempt2.json",
    "meta": "meta/b1b/audit/deviation_checks/advanced_attempt1.json",
}

# 既存Comment1-4(B1B/English/Charon)。直近のFamily X B1B scaffold runから
# reuse(新規LLM呼び出しなし)。設計書§1-6の既知の制約(AN3-T0本体とは
# 別runのCommentであること)を参照。
COMMENT_SOURCE_PATH = {
    "hormuz": ("er019_output/family_x_audio_production_wiring_01/"
               "family_x_b3_diversity_trial_01/hormuz__run_06_flashlite_full_kp/"
               "b1b/b1_support_texts.json"),
    "meta": "er019_output/family_x_b3_diversity_trial_01/meta/scaffold_text/b1b/b1_support_texts.json",
}

PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0


# ------------------------------------------------------------
# 小道具(既存er019系ファイルと同型のローカルヘルパー、共有utilはimportしない)
# ------------------------------------------------------------
def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def save_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load_pricing():
    with open(PRICING_SNAPSHOT_PATH, encoding="utf-8") as f:
        prices = json.load(f)["prices"]

    def price(provider, model, meter):
        return next(p["price"] for p in prices
                    if p["provider"] == provider and p["model"] == model and p["meter"] == meter
                    and p.get("tier", "Standard") == "Standard")
    return price


def compute_cost_jpy(price_fn, model: str, usage: dict) -> tuple:
    input_tokens = (usage or {}).get("input_tokens") or 0
    cached_tokens = (usage or {}).get("cached_input_tokens") or 0
    output_tokens = (usage or {}).get("output_tokens") or 0
    billable_in = max(input_tokens - cached_tokens, 0)
    cost_usd = 0.0
    try:
        cost_usd += (billable_in / 1_000_000) * price_fn("openai", model, "input_tokens")
    except StopIteration:
        pass
    if cached_tokens:
        try:
            cost_usd += (cached_tokens / 1_000_000) * price_fn("openai", model, "cached_input_tokens")
        except StopIteration:
            pass
    if output_tokens:
        try:
            cost_usd += (output_tokens / 1_000_000) * price_fn("openai", model, "output_tokens")
        except StopIteration:
            pass
    cost_jpy = cost_usd * USD_JPY
    return round(cost_usd, 6), round(cost_jpy, 4)


class CostTracker:
    def __init__(self, budget_jpy: float):
        self.budget_jpy = budget_jpy
        self.calls = []
        self.total_jpy = 0.0

    def add(self, label: str, model: str, usage: dict, price_fn) -> float:
        cost_usd, cost_jpy = compute_cost_jpy(price_fn, model, usage)
        self.total_jpy += cost_jpy
        self.calls.append({"label": label, "model": model, "usage": usage,
                            "cost_usd": cost_usd, "cost_jpy": cost_jpy,
                            "running_total_jpy": round(self.total_jpy, 4)})
        print(f"[COST] {label}: model={model} cost_jpy={cost_jpy} "
              f"running_total_jpy={round(self.total_jpy, 4)} (budget={self.budget_jpy})")
        return cost_jpy


# ------------------------------------------------------------
# 入力読み込み
# ------------------------------------------------------------
def load_ja_final_text(source_dir: str, article: str) -> str:
    path = os.path.join(source_dir, article, "ja_writer", "revision2.md")
    return load_text(path).strip()


def load_verified_ledger_text(source_dir: str, article: str) -> str:
    path = os.path.join(source_dir, article, "research_ledger", "verified_fact_ledger.txt")
    return load_text(path)


def extract_hormuz_baseline_from_report() -> str:
    report = load_text(REPORT_PATH)
    m = re.search(
        r"### Hormuz — Advanced\(English、最終、`LEDGER_COMPLIANT`\)\n\n```\n(.*?)\n```",
        report, re.S)
    if not m:
        raise RuntimeError("[ER-045] REPORTからHormuz Advanced最終テキストを抽出できませんでした")
    return m.group(1).strip()


def load_baseline_english(source_dir: str, article: str) -> dict:
    cfg = BASELINE_SOURCE[article]
    if cfg["mode"] == "report":
        text = extract_hormuz_baseline_from_report()
        origin = REPORT_PATH
    else:
        path = os.path.join(source_dir, cfg["relpath"])
        text = load_text(path).strip()
        origin = path
    return {"text": text, "origin": origin}


def load_baseline_deviation_check(source_dir: str, article: str) -> dict:
    path = os.path.join(source_dir, BASELINE_DEVIATION_PATH[article])
    data = load_json(path)
    return {"origin": path, "parsed": data.get("parsed"), "raw": data}


def load_comments(article: str) -> dict:
    path = COMMENT_SOURCE_PATH[article]
    data = load_json(path)
    return {"origin": path, "comments": data}


# ------------------------------------------------------------
# (a) 忠実英訳(Trial限定Prompt)
# ------------------------------------------------------------
TRIAL_DEVELOPER_MESSAGE = (
    "You are a translator who turns a finished Japanese feature article "
    "into natural English for listeners who are learning English. Your "
    "task is translation, not editorial rewriting."
)

TRIAL_FAITHFUL_TRANSLATION_INSTRUCTION = (
    "Translate the Japanese article below into English, paragraph by "
    "paragraph, staying as close to the original as natural English "
    "allows.\n"
    "\n"
    "Do not add new ideas, claims, background, general observations, "
    "examples, or facts that are not in the Japanese article. Do not "
    "remove any fact, claim, or causal link that is in the Japanese "
    "article. Keep the same order of information and the same paragraph "
    "structure: the English article must have exactly the same number of "
    "paragraphs as the Japanese article, in the same order, each English "
    "paragraph translating the corresponding Japanese paragraph. Do not "
    "merge, split, or reorder paragraphs.\n"
    "\n"
    "Do not add section headings, subheadings, or any Markdown heading "
    "markup (\"#\", \"##\", \"###\") inside the body. Do not add a "
    "concluding one-line summary; that is handled separately by another "
    "step.\n"
    "\n"
    "Output format: first output a title line starting with \"# \" "
    "followed by an English title that translates the Japanese title, "
    "then a blank line, then the body paragraphs (one blank line between "
    "paragraphs, same count and order as the Japanese article). Output "
    "nothing else (no commentary about the translation itself).\n"
    "\n"
    "Use short, simple, natural English that a learner could understand "
    "by listening once."
)

TRIAL_IN_ONE_LINE_INSTRUCTION_TEMPLATE = (
    "Below is a finished English news feature article (already "
    "translated from Japanese, no section headings). Write ONE short, "
    "natural sentence that captures the core of the story -- its central "
    "point or twist.\n"
    "\n"
    "Do not add any new fact, conclusion, or lesson that is not already "
    "stated in the article below. Do not summarize with a generic moral "
    "unless the article itself states it. Output only the sentence "
    "itself, nothing else (no quotation marks, no label like \"In one "
    "line:\").\n"
    "\n"
    "[Article]\n{article_text}"
)

_JA_TITLE_RE = re.compile(r"^(.+?)\n\n(.+)$", re.S)
_TRIAL_TITLE_RE = re.compile(r"^#\s+(.+?)\s*\n\n(.+)$", re.S)


def split_ja_title_and_body(ja_text: str) -> tuple:
    m = _JA_TITLE_RE.match(ja_text.strip())
    if not m:
        raise RuntimeError("[ER-045] JAテキストからタイトル/本文を分離できませんでした")
    return m.group(1).strip(), m.group(2).strip()


def ja_paragraph_count(ja_body: str) -> int:
    return len([p for p in ja_body.split("\n\n") if p.strip()])


def generate_trial_translation(client, model: str, ja_text: str) -> dict:
    prompt = (TRIAL_FAITHFUL_TRANSLATION_INSTRUCTION + "\n\n" +
              adv_gen.ADVANCED_VOCAB_RULE_V2_BLOCK +
              "\n\n[Japanese article]\n" + ja_text)
    t0 = time.time()
    result = vfl01.run_writer_no_search(client, prompt, model=model, developer=TRIAL_DEVELOPER_MESSAGE)
    elapsed = round(time.time() - t0, 3)
    raw_text = result["raw_text"].strip()
    m = _TRIAL_TITLE_RE.match(raw_text)
    if not m:
        raise RuntimeError(f"[ER-045] Trial翻訳の出力形式が想定外です(先頭200字): {raw_text[:200]!r}")
    title, body = m.group(1).strip(), m.group(2).strip()
    return {"prompt": prompt, "raw_text": raw_text, "title": title, "body": body,
            "model": result["model"], "response_id": result["response_id"],
            "usage": result.get("usage"), "elapsed_seconds": elapsed}


# ------------------------------------------------------------
# (a-2) 修正1回目(委任_02): Meta忠実英訳へのmust-fix retry(Production
# 同等・1回のみ)。`er003_v1_n3_01_advanced_adaptation_generate.
# build_must_fix_block()`(Production定数・関数、読み取りのみimport)を
# そのまま流用する。ここでの新規追加は「Trial翻訳Promptの末尾へ同じ
# ブロックを付加する」受け口のみで、must-fix文言自体はProduction関数を
# 呼ぶだけ(コピペしない)。
# ------------------------------------------------------------
def _must_fix_from_major_deviations(major_devs: list) -> list:
    """er012_e_family_entertainment_two_level_runner_01.py::
    _must_fix_from_deviations()と同じ形(fact_id/claim_in_article/issue/
    explanationを、related_fact_id/claim_in_article/issue/explanationから
    組み立てる)。Productionファイルは読み取りのみで一切編集していない。"""
    return [
        {
            "fact_id": d.get("related_fact_id", ""),
            "claim_in_article": d.get("claim_in_article", ""),
            "issue": d.get("issue", ""),
            "explanation": d.get("explanation", ""),
        }
        for d in major_devs
    ]


def build_must_fix_retry_prompt(ja_text: str, must_fix: list) -> str:
    return (TRIAL_FAITHFUL_TRANSLATION_INSTRUCTION + "\n\n" +
            adv_gen.ADVANCED_VOCAB_RULE_V2_BLOCK +
            "\n\n[Japanese article]\n" + ja_text +
            "\n\n" + adv_gen.build_must_fix_block(must_fix))


def generate_trial_translation_must_fix_retry(client, model: str, ja_text: str, must_fix: list) -> dict:
    prompt = build_must_fix_retry_prompt(ja_text, must_fix)
    t0 = time.time()
    result = vfl01.run_writer_no_search(client, prompt, model=model, developer=TRIAL_DEVELOPER_MESSAGE)
    elapsed = round(time.time() - t0, 3)
    raw_text = result["raw_text"].strip()
    m = _TRIAL_TITLE_RE.match(raw_text)
    if not m:
        raise RuntimeError(f"[ER-045] must-fix retry翻訳の出力形式が想定外です(先頭200字): {raw_text[:200]!r}")
    title, body = m.group(1).strip(), m.group(2).strip()
    return {"prompt": prompt, "raw_text": raw_text, "title": title, "body": body,
            "model": result["model"], "response_id": result["response_id"],
            "usage": result.get("usage"), "elapsed_seconds": elapsed, "must_fix_used": must_fix}


# ------------------------------------------------------------
# (a-3) 修正1回目(委任_02): In One Line v2(ユーザー仕様「短く自然な一文/
# 一回聞いて理解できる/論点を詰め込みすぎない」+ Trial限定の目安語数)。
# 見出し生成の指示は含まない(§Trial全体でTRIAL_FAITHFUL_TRANSLATION_
# INSTRUCTIONと同様、本文再構成・見出し生成は行わない)。
# ------------------------------------------------------------
TRIAL_IN_ONE_LINE_V2_INSTRUCTION_TEMPLATE = (
    "Below is a finished English news feature article (already "
    "translated from Japanese, no section headings). Write ONE short, "
    "natural sentence that captures the core of the story, in a way a "
    "listener can understand by hearing it just once.\n"
    "\n"
    "Requirements:\n"
    "- Exactly one sentence.\n"
    "- Understandable on a single listen.\n"
    "- Do not pack in multiple separate points; focus on the single most "
    "important point or twist of the story.\n"
    "- Do not add any new fact, conclusion, or lesson that is not already "
    "stated in the article below.\n"
    "\n"
    "As a rough guide only (Trial-only guidance, not a strict rule): aim "
    "for one main clause with at most one subordinate clause, roughly "
    "12-18 words.\n"
    "\n"
    "Output only the sentence itself, nothing else (no quotation marks, "
    "no label like \"In one line:\", no Markdown heading markup).\n"
    "\n"
    "[Article]\n{article_text}"
)


def generate_trial_in_one_line_v2(client, model: str, trial_title: str, trial_body: str) -> dict:
    article_text = f"# {trial_title}\n\n{trial_body}"
    prompt = TRIAL_IN_ONE_LINE_V2_INSTRUCTION_TEMPLATE.format(article_text=article_text)
    t0 = time.time()
    result = vfl01.run_writer_no_search(client, prompt, model=model, developer=TRIAL_DEVELOPER_MESSAGE)
    elapsed = round(time.time() - t0, 3)
    text = result["raw_text"].strip()
    return {"prompt": prompt, "text": text, "model": result["model"],
            "response_id": result["response_id"], "usage": result.get("usage"),
            "elapsed_seconds": elapsed}


def generate_trial_in_one_line(client, model: str, trial_title: str, trial_body: str) -> dict:
    article_text = f"# {trial_title}\n\n{trial_body}"
    prompt = TRIAL_IN_ONE_LINE_INSTRUCTION_TEMPLATE.format(article_text=article_text)
    t0 = time.time()
    result = vfl01.run_writer_no_search(client, prompt, model=model, developer=TRIAL_DEVELOPER_MESSAGE)
    elapsed = round(time.time() - t0, 3)
    text = result["raw_text"].strip()
    return {"prompt": prompt, "text": text, "model": result["model"],
            "response_id": result["response_id"], "usage": result.get("usage"),
            "elapsed_seconds": elapsed}


# ------------------------------------------------------------
# (b) 決定論的3分割(LLM不使用)
# ------------------------------------------------------------
def _word_count_en(s: str) -> int:
    return len(re.findall(r"[A-Za-z']+", s or ""))


def deterministic_three_way_split(body: str) -> dict:
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    n = len(paragraphs)
    if n < 3:
        return {"status": "TOO_FEW_PARAGRAPHS", "paragraph_count": n, "paragraphs": paragraphs}

    counts = [_word_count_en(p) for p in paragraphs]
    total = sum(counts)
    target = total / 3.0

    best = None
    for i, j in itertools.combinations(range(1, n), 2):
        c1 = sum(counts[:i])
        c2 = sum(counts[i:j])
        c3 = sum(counts[j:])
        cost = (c1 - target) ** 2 + (c2 - target) ** 2 + (c3 - target) ** 2
        key = (cost, i, j)
        if best is None or key < best[0]:
            best = (key, i, j, c1, c2, c3)

    _, i, j, c1, c2, c3 = best
    part1 = "\n\n".join(paragraphs[:i])
    part2 = "\n\n".join(paragraphs[i:j])
    part3 = "\n\n".join(paragraphs[j:])
    return {
        "status": "OK", "paragraph_count": n, "boundary_i": i, "boundary_j": j,
        "part1": part1, "part2": part2, "part3": part3,
        "word_counts": {"part1": c1, "part2": c2, "part3": c3, "total": total},
        "balance_pct": {
            "part1": round(100.0 * c1 / total, 1) if total else None,
            "part2": round(100.0 * c2 / total, 1) if total else None,
            "part3": round(100.0 * c3 / total, 1) if total else None,
        },
    }


# ------------------------------------------------------------
# (d) 評価: Deviation Check(Trialのみ新規実行) + 決定論指標 + Rubric
# ------------------------------------------------------------
def run_trial_deviation_check(client, model: str, ledger_text: str, trial_full_text: str,
                               ja_text: str) -> dict:
    result = vfl01.run_deviation_check(client, ledger_text, trial_full_text, model=model,
                                        hook_aware=False, include_related_fact_id=True,
                                        source_article_text=ja_text)
    return result


def compute_deterministic_metrics(ja_body: str, trial_body: str, split_result: dict,
                                   in_one_line_before: str, in_one_line_after: str) -> dict:
    ja_para_count = ja_paragraph_count(ja_body)
    trial_para_count = len([p for p in trial_body.split("\n\n") if p.strip()])

    ja_entities = t2.extract_entities_ja_improved(ja_body)
    trial_entities = t2.extract_entities_en_improved(trial_body)

    def sentence_count(s: str) -> int:
        return len([x for x in re.split(r"(?<=[.!?])\s+", s.strip()) if x.strip()])

    return {
        "ja_paragraph_count": ja_para_count,
        "trial_en_paragraph_count": trial_para_count,
        "paragraph_count_match": ja_para_count == trial_para_count,
        "ja_entity_count_improved": len(ja_entities),
        "trial_en_entity_count_improved": len(trial_entities),
        "ja_entities_improved": sorted(ja_entities),
        "trial_en_entities_improved": sorted(trial_entities),
        "split": {k: v for k, v in split_result.items() if k not in ("part1", "part2", "part3")},
        "in_one_line_before": {
            "text": in_one_line_before, "word_count": _word_count_en(in_one_line_before),
            "sentence_count": sentence_count(in_one_line_before)},
        "in_one_line_after": {
            "text": in_one_line_after, "word_count": _word_count_en(in_one_line_after),
            "sentence_count": sentence_count(in_one_line_after)},
    }


RUBRIC_ITEMS = [
    ("faithfulness_to_ja", "日本語原文への忠実性"),
    ("fact_preservation", "Fact保持"),
    ("causal_preservation", "因果保持"),
    ("zero_new_facts", "新規Fact 0"),
    ("order_preservation", "順序保持"),
    ("no_meaning_added_or_removed", "意味の追加・削除がないか"),
    ("readability", "読みやすさ"),
    ("listenability", "聞きやすさ"),
    ("entertainment_value", "Entertainment性"),
    ("three_way_split_naturalness", "3分割の自然さ"),
    ("length_balance", "長さバランス"),
    ("comment_connection_naturalness", "Commentとの接続自然さ"),
    ("in_one_line_conciseness_accuracy", "In One Lineの簡潔さ・要旨正確性"),
    ("no_monotony_without_headings", "見出しをなくした結果、内容が単調になりすぎないか(Trialのみ採点、Baselineはnull)"),
]

RUBRIC_JSON_SCHEMA = {
    "name": "no_heading_trial_rubric_v1",
    "schema": {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string"},
                        "baseline_score_1_to_5": {"type": ["integer", "null"]},
                        "baseline_reasoning": {"type": ["string", "null"]},
                        "trial_score_1_to_5": {"type": ["integer", "null"]},
                        "trial_reasoning": {"type": ["string", "null"]},
                    },
                    "required": ["key", "baseline_score_1_to_5", "baseline_reasoning",
                                 "trial_score_1_to_5", "trial_reasoning"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["items"],
        "additionalProperties": False,
    },
    "strict": True,
}

RUBRIC_DEVELOPER_MESSAGE = (
    "You are an editorial reviewer comparing two English adaptations of "
    "the same Japanese news feature article: a Baseline (with two section "
    "headings and a generated one-line summary) and a Trial (no headings, "
    "faithful translation, deterministic 3-way split, short summary "
    "sentence)."
)


def build_rubric_prompt(ja_text: str, baseline_text: str, trial_text: str,
                         in_one_line_before: str, in_one_line_after: str,
                         comments: dict, split_result: dict) -> str:
    items_desc = "\n".join(f"- {k}: {label}" for k, label in RUBRIC_ITEMS)
    comment_block = (
        f"[Comment 1 -- plays right before Part 1 / before the first section heading]\n"
        f"{comments.get('comment_1', '')}\n\n"
        f"[Comment 2 -- plays between Part 1 and Part 2 / right before the first heading]\n"
        f"{comments.get('comment_2', '')}\n\n"
        f"[Comment 3 -- plays between Part 2 and Part 3 / right before the second heading]\n"
        f"{comments.get('comment_3', '')}\n\n"
        f"[Comment 4 -- plays right after Part 3, right before In One Line]\n"
        f"{comments.get('comment_4', '')}\n"
    )
    trial_layout = (
        f"Comment 1 -> Part 1 -> Comment 2 -> Part 2 -> Comment 3 -> Part 3 -> "
        f"Comment 4 -> In One Line (no headings anywhere)."
    )
    baseline_layout = (
        f"Comment 1 -> Part 1 (Title + intro, no heading) -> Comment 2 -> "
        f"heading 1 + Part 2 -> Comment 3 -> heading 2 + Part 3 -> Comment 4 -> "
        f"In One Line."
    )
    return (
        "Score both the Baseline and the Trial English article on each of "
        "the 14 criteria below, using a 1-5 scale (5=best) with a short "
        "reasoning for each score. For the criterion "
        "'no_monotony_without_headings', Baseline has headings so score "
        "it as null with null reasoning (not applicable); only score the "
        "Trial for that one criterion. For 'comment_connection_naturalness', "
        "judge whether each Comment (below) connects naturally to the audio "
        "segment immediately following/preceding it, for the Baseline layout "
        "and the Trial layout respectively (the same four Comments are reused "
        "in both, only the body split position differs -- see layouts below).\n\n"
        f"Baseline layout: {baseline_layout}\n"
        f"Trial layout: {trial_layout}\n\n"
        f"Criteria:\n{items_desc}\n\n"
        f"[Japanese original article]\n{ja_text}\n\n"
        f"[Baseline English article]\n{baseline_text}\n\n"
        f"[Trial English article]\n{trial_text}\n\n"
        f"[Baseline In One Line]\n{in_one_line_before}\n\n"
        f"[Trial In One Line]\n{in_one_line_after}\n\n"
        f"[Comments reused as-is for both Baseline and Trial]\n{comment_block}\n\n"
        "Return exactly one JSON object with an 'items' array containing "
        "one entry per criterion key listed above, in the same order."
    )


def run_rubric(client, model: str, ja_text: str, baseline_text: str, trial_text: str,
               in_one_line_before: str, in_one_line_after: str, comments: dict,
               split_result: dict) -> dict:
    prompt = build_rubric_prompt(ja_text, baseline_text, trial_text,
                                  in_one_line_before, in_one_line_after,
                                  comments, split_result)
    t0 = time.time()
    response = client.responses.create(
        model=model,
        reasoning={"effort": vfl01.REASONING_EFFORT},
        text={"format": {"type": "json_schema", **RUBRIC_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": RUBRIC_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    elapsed = round(time.time() - t0, 3)
    parsed = json.loads(response.output_text)
    usage = getattr(response, "usage", None)
    usage_dict = None
    if usage is not None:
        in_details = getattr(usage, "input_tokens_details", None)
        usage_dict = {
            "input_tokens": getattr(usage, "input_tokens", None),
            "output_tokens": getattr(usage, "output_tokens", None),
            "cached_input_tokens": getattr(in_details, "cached_tokens", None) if in_details else None,
        }
    return {"prompt": prompt, "parsed": parsed, "model": response.model,
            "response_id": response.id, "usage": usage_dict, "elapsed_seconds": elapsed}


# ------------------------------------------------------------
# 修正1回目(委任_02)の3ステージ: must-fix-retry / in-one-line-v2 /
# rubric-v2。いずれもv1の`trial_result.json`を入力として読み込み、
# `{out_dir}/v2/`配下へ新規artifactを追加保存する(v1のファイルは一切
# 上書きしない、透明性のため併載)。
# ------------------------------------------------------------
def run_must_fix_retry_stage(article: str, source_dir: str, out_dir: str, budget_jpy: float) -> dict:
    """Meta本文の忠実英訳Deviation Check MAJORへの、Production同様の
    must-fix retry(1回のみ、上限回避なし)。MAJORが無い場合(Hormuz)は
    API呼び出しをせずSKIPPEDを記録する。"""
    trial_result_v1 = load_json(f"{out_dir}/trial_result.json")
    deviation_v1 = trial_result_v1["trial_deviation"]["parsed"]
    major_devs = [d for d in deviation_v1.get("deviations", []) if d.get("severity") == "MAJOR"]
    if not major_devs:
        print(f"[ER-045][must-fix-retry] article={article}: MAJOR deviationなし。retryせずSKIP。")
        result = {"article": article, "status": "SKIPPED_NO_MAJOR"}
        save_json(f"{out_dir}/v2/must_fix_retry_result.json", result)
        return result

    client = vfl01.get_client()
    model = routing.require_model_or_override("B1_WRITER", routing.WRITER_MODEL)
    price_fn = _load_pricing()
    tracker = CostTracker(budget_jpy)

    must_fix = _must_fix_from_major_deviations(major_devs)
    ja_text_full = trial_result_v1["ja_text"]
    ledger_text = load_verified_ledger_text(source_dir, article)

    trial_translation_v2 = generate_trial_translation_must_fix_retry(client, model, ja_text_full, must_fix)
    tracker.add("trial_translation_v2_must_fix_retry", trial_translation_v2["model"],
                trial_translation_v2["usage"], price_fn)

    split_result_v2 = deterministic_three_way_split(trial_translation_v2["body"])
    trial_full_text_v2 = f"# {trial_translation_v2['title']}\n\n{trial_translation_v2['body']}"

    deviation_v2 = vfl01.run_deviation_check(client, ledger_text, trial_full_text_v2, model=model,
                                              hook_aware=False, include_related_fact_id=True,
                                              source_article_text=ja_text_full, prior_issues=must_fix)
    tracker.add("trial_deviation_check_v2", deviation_v2.get("model", model),
                deviation_v2.get("usage"), price_fn)

    status_v2 = deviation_v2["parsed"].get("overall_status")
    all_resolved = deviation_v2["parsed"].get("all_prior_issues_resolved", False)
    # Production(er012_e_family_entertainment_two_level_runner_01.py)と同じ
    # 上限: 1回だけ再生成し、なおMAJOR/未解消があってもそれ以上retryせず記録する。
    result = {
        "article": article, "status": "OK",
        "must_fix_used": must_fix,
        "trial_translation_v2": trial_translation_v2,
        "split_result_v2": split_result_v2,
        "deviation_check_v2": {"parsed": deviation_v2.get("parsed"), "model": deviation_v2.get("model"),
                                "usage": deviation_v2.get("usage")},
        "overall_status_v2": status_v2,
        "all_prior_issues_resolved": all_resolved,
        "retry_success": (status_v2 == "LEDGER_COMPLIANT"),
        "cost": {"total_jpy": round(tracker.total_jpy, 4), "calls": tracker.calls,
                 "budget_jpy": budget_jpy, "over_budget": tracker.total_jpy > budget_jpy},
    }
    save_json(f"{out_dir}/v2/trial_translation_v2.json", trial_translation_v2)
    save_json(f"{out_dir}/v2/trial_split_v2.json", split_result_v2)
    save_json(f"{out_dir}/v2/deviation_check_trial_v2.json", vfl01.deviation_audit_record(deviation_v2))
    save_json(f"{out_dir}/v2/must_fix_retry_result.json", result)
    print(f"[ER-045][must-fix-retry] article={article} status_v2={status_v2} "
          f"all_resolved={all_resolved} cost_jpy={round(tracker.total_jpy, 4)}")
    return result


def run_in_one_line_v2_stage(article: str, out_dir: str, budget_jpy: float) -> dict:
    """両記事共通。Metaはmust-fix retry後のv2本文(存在する場合)、
    Hormuzはv1本文(不変)を対象にIn One Line v2を1回生成する。"""
    trial_result_v1 = load_json(f"{out_dir}/trial_result.json")
    v2_translation_path = f"{out_dir}/v2/trial_translation_v2.json"
    if os.path.exists(v2_translation_path):
        base = load_json(v2_translation_path)
        source_label = "trial_translation_v2 (must-fix retry後)"
    else:
        base = trial_result_v1["trial_translation"]
        source_label = "trial_translation (v1、must-fix retry対象外)"

    client = vfl01.get_client()
    model = routing.require_model_or_override("B1_WRITER", routing.WRITER_MODEL)
    price_fn = _load_pricing()
    tracker = CostTracker(budget_jpy)

    in_one_line_v2 = generate_trial_in_one_line_v2(client, model, base["title"], base["body"])
    tracker.add("trial_in_one_line_v2", in_one_line_v2["model"], in_one_line_v2["usage"], price_fn)

    sentence_count = len([x for x in re.split(r"(?<=[.!?])\s+", in_one_line_v2["text"].strip()) if x.strip()])
    result = {
        "article": article, "status": "OK", "source_body_used": source_label,
        "in_one_line_v2": in_one_line_v2,
        "word_count": _word_count_en(in_one_line_v2["text"]),
        "sentence_count": sentence_count,
        "cost": {"total_jpy": round(tracker.total_jpy, 4), "calls": tracker.calls,
                 "budget_jpy": budget_jpy, "over_budget": tracker.total_jpy > budget_jpy},
    }
    save_json(f"{out_dir}/v2/in_one_line_v2.json", result)
    print(f"[ER-045][in-one-line-v2] article={article} word_count={result['word_count']} "
          f"sentence_count={sentence_count} cost_jpy={round(tracker.total_jpy, 4)}")
    return result


def run_rubric_v2_stage(article: str, out_dir: str, budget_jpy: float) -> dict:
    """変更した要素(Meta本文v2、In One Line v2)についてv1と同じ14項目
    rubricを再評価する。Hormuzは本文がv1のまま(must-fix retry対象外)
    なので、本文自体の再評価は目的ではなく、In One Line v2反映後の
    in_one_line_conciseness_accuracy項目を得るために同じ1 callを実行する
    (14項目のうち本文関連13項目は参考値、実質的な変化点はIn One Line関連)。
    """
    trial_result_v1 = load_json(f"{out_dir}/trial_result.json")
    ja_text_full = trial_result_v1["ja_text"]
    baseline_text = trial_result_v1["baseline"]["text"]
    baseline_in_one_line = trial_result_v1["baseline_in_one_line"]
    comments = trial_result_v1["comments"]["comments"]
    split_result = trial_result_v1["split_result"]

    v2_translation_path = f"{out_dir}/v2/trial_translation_v2.json"
    if os.path.exists(v2_translation_path):
        base = load_json(v2_translation_path)
        body_label = "v2(must-fix retry後)"
    else:
        base = trial_result_v1["trial_translation"]
        body_label = "v1(不変、must-fix retry対象外)"
    trial_full_text_v2 = f"# {base['title']}\n\n{base['body']}"

    in_one_line_v2_data = load_json(f"{out_dir}/v2/in_one_line_v2.json")
    in_one_line_v2_text = in_one_line_v2_data["in_one_line_v2"]["text"]

    client = vfl01.get_client()
    model = routing.require_model_or_override("B1_WRITER", routing.WRITER_MODEL)
    price_fn = _load_pricing()
    tracker = CostTracker(budget_jpy)

    rubric_v2 = run_rubric(client, model, ja_text_full, baseline_text, trial_full_text_v2,
                            baseline_in_one_line, in_one_line_v2_text, comments, split_result)
    tracker.add("rubric_v2", rubric_v2.get("model", model), rubric_v2.get("usage"), price_fn)

    result = {
        "article": article, "status": "OK", "body_used": body_label,
        "rubric_v2": rubric_v2,
        "cost": {"total_jpy": round(tracker.total_jpy, 4), "calls": tracker.calls,
                 "budget_jpy": budget_jpy, "over_budget": tracker.total_jpy > budget_jpy},
    }
    save_json(f"{out_dir}/v2/rubric_v2.json", result)
    print(f"[ER-045][rubric-v2] article={article} body_used={body_label} "
          f"cost_jpy={round(tracker.total_jpy, 4)}")
    return result


# ------------------------------------------------------------
# メイン
# ------------------------------------------------------------
def run_trial(article: str, source_dir: str, out_dir: str, budget_jpy: float) -> dict:
    client = vfl01.get_client()
    model = routing.require_model_or_override("B1_WRITER", routing.WRITER_MODEL)
    price_fn = _load_pricing()
    tracker = CostTracker(budget_jpy)

    ja_text_full = load_ja_final_text(source_dir, article)
    ja_title, ja_body = split_ja_title_and_body(ja_text_full)
    baseline = load_baseline_english(source_dir, article)
    ledger_text = load_verified_ledger_text(source_dir, article)
    baseline_deviation = load_baseline_deviation_check(source_dir, article)
    comments = load_comments(article)

    trial_translation = generate_trial_translation(client, model, ja_text_full)
    tracker.add("trial_translation", trial_translation["model"], trial_translation["usage"], price_fn)

    split_result = deterministic_three_way_split(trial_translation["body"])
    if split_result["status"] != "OK":
        result = {
            "article": article, "status": "STOP_TOO_FEW_PARAGRAPHS",
            "ja_text": ja_text_full, "baseline": baseline,
            "trial_translation": trial_translation, "split_result": split_result,
            "cost": {"total_jpy": round(tracker.total_jpy, 4), "calls": tracker.calls},
        }
        save_json(f"{out_dir}/trial_result.json", result)
        return result

    trial_in_one_line = generate_trial_in_one_line(
        client, model, trial_translation["title"], trial_translation["body"])
    tracker.add("trial_in_one_line", trial_in_one_line["model"], trial_in_one_line["usage"], price_fn)

    trial_full_text = f"# {trial_translation['title']}\n\n{trial_translation['body']}"
    trial_deviation = run_trial_deviation_check(client, model, ledger_text, trial_full_text, ja_text_full)
    tracker.add("trial_deviation_check", trial_deviation.get("model", model),
                trial_deviation.get("usage"), price_fn)

    baseline_in_one_line_match = re.search(
        r"^##\s+In [Oo]ne [Ll]ine[…\.]*\s*\n(.+)", baseline["text"], flags=re.MULTILINE | re.DOTALL)
    baseline_in_one_line = baseline_in_one_line_match.group(1).strip() if baseline_in_one_line_match else ""

    metrics = compute_deterministic_metrics(
        ja_body, trial_translation["body"], split_result,
        baseline_in_one_line, trial_in_one_line["text"])

    rubric = run_rubric(client, model, ja_text_full, baseline["text"], trial_full_text,
                         baseline_in_one_line, trial_in_one_line["text"],
                         comments["comments"], split_result)
    tracker.add("rubric", rubric.get("model", model), rubric.get("usage"), price_fn)

    result = {
        "article": article, "status": "OK",
        "ja_text": ja_text_full, "ja_title": ja_title, "ja_body": ja_body,
        "baseline": baseline, "baseline_deviation": baseline_deviation,
        "baseline_in_one_line": baseline_in_one_line,
        "comments": comments,
        "trial_translation": trial_translation,
        "split_result": {k: v for k, v in split_result.items()},
        "trial_in_one_line": trial_in_one_line,
        "trial_deviation": {"parsed": trial_deviation.get("parsed"),
                             "model": trial_deviation.get("model"),
                             "usage": trial_deviation.get("usage")},
        "metrics": metrics,
        "rubric": rubric,
        "cost": {"total_jpy": round(tracker.total_jpy, 4), "calls": tracker.calls,
                 "budget_jpy": budget_jpy,
                 "over_budget": tracker.total_jpy > budget_jpy},
    }

    save_json(f"{out_dir}/trial_translation.json", trial_translation)
    save_json(f"{out_dir}/trial_split.json", split_result)
    save_json(f"{out_dir}/trial_in_one_line.json", trial_in_one_line)
    save_json(f"{out_dir}/deviation_check_trial.json", vfl01.deviation_audit_record(trial_deviation))
    save_json(f"{out_dir}/deviation_check_baseline_reused.json", baseline_deviation)
    save_json(f"{out_dir}/metrics.json", metrics)
    save_json(f"{out_dir}/rubric.json", rubric)
    save_json(f"{out_dir}/trial_result.json", result)
    print(f"[ER-045] article={article} status=OK total_cost_jpy={round(tracker.total_jpy, 4)}")
    return result


# ------------------------------------------------------------
# 成果物ページ生成(API呼び出しなし、既存trial_result.jsonから組み立てるのみ)
# ------------------------------------------------------------
def _html_escape(s: str) -> str:
    import html
    return html.escape(s or "", quote=False)


def _para_html(text: str) -> str:
    paras = [p.strip() for p in (text or "").split("\n\n") if p.strip()]
    return "".join(f"<p>{_html_escape(p)}</p>\n" for p in paras)


def _word_diff_html(baseline_text: str, trial_text: str) -> str:
    import difflib
    a = re.findall(r"\S+|\s+", baseline_text or "")
    b = re.findall(r"\S+|\s+", trial_text or "")
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    out = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            out.append(_html_escape("".join(a[i1:i2])))
        elif tag == "delete":
            out.append(f'<del style="background:#ffe0e0">{_html_escape("".join(a[i1:i2]))}</del>')
        elif tag == "insert":
            out.append(f'<ins style="background:#e0ffe0">{_html_escape("".join(b[j1:j2]))}</ins>')
        elif tag == "replace":
            out.append(f'<del style="background:#ffe0e0">{_html_escape("".join(a[i1:i2]))}</del>')
            out.append(f'<ins style="background:#e0ffe0">{_html_escape("".join(b[j1:j2]))}</ins>')
    return f'<div style="white-space:pre-wrap;line-height:1.7">{"".join(out)}</div>'


def _strip_headings_for_diff(baseline_text: str) -> str:
    lines = [ln for ln in baseline_text.split("\n")
             if not ln.startswith("### ") and not ln.startswith("## ") and not ln.startswith("# ")]
    return "\n".join(lines)


RUBRIC_LABELS = dict(RUBRIC_ITEMS)


def _rubric_table_html(rubric_items: list) -> str:
    rows = []
    for item in rubric_items:
        label = RUBRIC_LABELS.get(item["key"], item["key"])
        b = item.get("baseline_score_1_to_5")
        t = item.get("trial_score_1_to_5")
        rows.append(
            f"<tr><td>{_html_escape(label)}</td>"
            f"<td style='text-align:center'>{b if b is not None else '-'}</td>"
            f"<td style='text-align:center'>{t if t is not None else '-'}</td>"
            f"<td style='font-size:0.85em;color:#444'>{_html_escape(item.get('baseline_reasoning') or '')}</td>"
            f"<td style='font-size:0.85em;color:#444'>{_html_escape(item.get('trial_reasoning') or '')}</td></tr>"
        )
    return (
        "<table border='1' cellpadding='6' cellspacing='0' style='border-collapse:collapse;width:100%'>"
        "<tr><th>評価項目</th><th>Baseline</th><th>Trial</th>"
        "<th>Baseline根拠</th><th>Trial根拠</th></tr>" + "".join(rows) + "</table>"
    )


def _attach_v2(result: dict, result_dir: str) -> None:
    """修正1回目(委任_02)。API呼び出しなし、既存v2/*.jsonがあれば
    result['v2']へ添付する(なければNoneのまま、v1のみのページになる)。"""
    v2 = {}
    must_fix_path = f"{result_dir}/v2/must_fix_retry_result.json"
    in_one_line_v2_path = f"{result_dir}/v2/in_one_line_v2.json"
    rubric_v2_path = f"{result_dir}/v2/rubric_v2.json"
    if os.path.exists(must_fix_path):
        v2["must_fix_retry"] = load_json(must_fix_path)
    if os.path.exists(in_one_line_v2_path):
        v2["in_one_line_v2"] = load_json(in_one_line_v2_path)
    if os.path.exists(rubric_v2_path):
        v2["rubric_v2"] = load_json(rubric_v2_path)
    result["v2"] = v2 or None


def _render_v2_section(article_key: str, result: dict) -> str:
    v2 = result.get("v2")
    if not v2:
        return ""

    must_fix = v2.get("must_fix_retry")
    must_fix_html = ""
    if must_fix and must_fix.get("status") == "OK":
        dev2 = must_fix["deviation_check_v2"]["parsed"]
        mf_items = "".join(
            f"<li>Fact ID: {_html_escape(item.get('fact_id',''))} | "
            f"該当箇所: {_html_escape(item.get('claim_in_article',''))} | "
            f"指摘: {_html_escape(item.get('issue',''))}</li>"
            for item in must_fix["must_fix_used"]
        )
        must_fix_html = f"""
<h3>Meta must-fix retry(Production同等・1回のみ)</h3>
<p>指摘{len(must_fix['must_fix_used'])}件:</p>
<ul>{mf_items}</ul>
<div style="background:#e6ffe6;padding:12px;border-radius:6px">
<p><b># {_html_escape(must_fix['trial_translation_v2']['title'])}</b></p>
{_para_html(must_fix['trial_translation_v2']['body'])}
</div>
<p>再生成後Deviation Check: overall_status=<b>{_html_escape(dev2.get('overall_status',''))}</b>
(deviations={len(dev2.get('deviations', []))}, all_prior_issues_resolved=
{must_fix.get('all_prior_issues_resolved')})</p>
"""
    elif must_fix and must_fix.get("status") == "SKIPPED_NO_MAJOR":
        must_fix_html = "<h3>Meta must-fix retry</h3><p>MAJOR deviationなし。retry対象外(v1のまま)。</p>"

    ioL_v2 = v2.get("in_one_line_v2")
    ioL_html = ""
    if ioL_v2:
        ioL_v1 = result["trial_in_one_line"]
        m1 = result["metrics"]["in_one_line_after"]
        ioL_html = f"""
<h3>In One Line: v1 → v2(簡潔化Prompt+参考ガイド12-18語)</h3>
<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;width:100%">
<tr><th>v1</th><th>v2</th></tr>
<tr>
<td>{_html_escape(ioL_v1['text'])}<br>
<span style="font-size:0.8em;color:#888">{m1['word_count']}語 / {m1['sentence_count']}文</span></td>
<td>{_html_escape(ioL_v2['in_one_line_v2']['text'])}<br>
<span style="font-size:0.8em;color:#888">{ioL_v2['word_count']}語 / {ioL_v2['sentence_count']}文
(使用本文: {_html_escape(ioL_v2['source_body_used'])})</span></td>
</tr>
</table>
"""

    rubric_v2 = v2.get("rubric_v2")
    rubric_html = ""
    if rubric_v2:
        rubric_html = f"""
<h3>Rubric v2(変更要素反映後の再評価、body_used={_html_escape(rubric_v2['body_used'])})</h3>
{_rubric_table_html(rubric_v2['rubric_v2']['parsed']['items'])}
"""

    return f"""
<section style="margin-top:24px;border-top:2px dashed #999;padding-top:12px">
<h3 style="color:#a30">修正1回目(2026-09-28、NH1B)</h3>
{must_fix_html}
{ioL_html}
{rubric_html}
</section>
"""


def render_article_section(article_key: str, label: str, result: dict) -> str:
    comments = result["comments"]["comments"]
    split = result["split_result"]
    baseline_text_no_heading = _strip_headings_for_diff(result["baseline"]["text"])
    trial_full = f"# {result['trial_translation']['title']}\n\n{result['trial_translation']['body']}"
    diff_html = _word_diff_html(baseline_text_no_heading, trial_full)

    metrics = result["metrics"]
    dev_trial = result["trial_deviation"]["parsed"]
    dev_baseline = result["baseline_deviation"]["parsed"]

    return f"""
<section id="{article_key}" style="margin-bottom:56px;border-top:4px solid #333;padding-top:16px">
<h2>{_html_escape(label)}</h2>

<h3>JA原文(AN3-T0 R2最終、忠実英訳の入力)</h3>
<div style="background:#f7f7f7;padding:12px;border-radius:6px">
<p><b>{_html_escape(result['ja_title'])}</b></p>
{_para_html(result['ja_body'])}
</div>

<h3>Baseline(現行Advanced、見出しあり)出典: {_html_escape(result['baseline']['origin'])}</h3>
<div style="background:#fff7e6;padding:12px;border-radius:6px">
{_para_html(result['baseline']['text'])}
</div>
<p>Baseline In One Line: <i>{_html_escape(result['baseline_in_one_line'])}</i></p>
<p>Baseline Deviation Check(既存artifact reuse、出典: {_html_escape(result['baseline_deviation']['origin'])}):
overall_status=<b>{_html_escape(dev_baseline.get('overall_status',''))}</b>
(deviations={len(dev_baseline.get('deviations', []))})</p>

<h3>Trial(見出し廃止・忠実英訳・決定論的3分割)</h3>
<div style="background:#e6f3ff;padding:12px;border-radius:6px">
<p><b># {_html_escape(result['trial_translation']['title'])}</b></p>
<p style="color:#0a6">[Comment 1]<br>{_html_escape(comments.get('comment_1',''))}</p>
<div style="border-left:4px solid #0a6;padding-left:10px">
<p style="font-size:0.8em;color:#888">Part 1(全体の{split['balance_pct']['part1']}%、{split['word_counts']['part1']}語)</p>
{_para_html(split['part1'])}
</div>
<p style="color:#0a6">[Comment 2]<br>{_html_escape(comments.get('comment_2',''))}</p>
<div style="border-left:4px solid #0a6;padding-left:10px">
<p style="font-size:0.8em;color:#888">Part 2(全体の{split['balance_pct']['part2']}%、{split['word_counts']['part2']}語)</p>
{_para_html(split['part2'])}
</div>
<p style="color:#0a6">[Comment 3]<br>{_html_escape(comments.get('comment_3',''))}</p>
<div style="border-left:4px solid #0a6;padding-left:10px">
<p style="font-size:0.8em;color:#888">Part 3(全体の{split['balance_pct']['part3']}%、{split['word_counts']['part3']}語)</p>
{_para_html(split['part3'])}
</div>
<p style="color:#0a6">[Comment 4]<br>{_html_escape(comments.get('comment_4',''))}</p>
<p><b>[In One Line]</b> {_html_escape(result['trial_in_one_line']['text'])}</p>
</div>
<p style="font-size:0.85em;color:#888">注: Comment1〜4は{_html_escape(result['comments']['origin'])}からのreuse
(AN3-T0本体とは別runの本文から生成、字句は完全一致しない)。</p>
<p>Trial Deviation Check(新規実行): overall_status=<b>{_html_escape(dev_trial.get('overall_status',''))}</b>
(deviations={len(dev_trial.get('deviations', []))})</p>

<h3>In One Line: Before(Baseline) / After(Trial)</h3>
<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;width:100%">
<tr><th>Before(Baseline)</th><th>After(Trial)</th></tr>
<tr>
<td>{_html_escape(result['baseline_in_one_line'])}<br>
<span style="font-size:0.8em;color:#888">{metrics['in_one_line_before']['word_count']}語 /
{metrics['in_one_line_before']['sentence_count']}文</span></td>
<td>{_html_escape(result['trial_in_one_line']['text'])}<br>
<span style="font-size:0.8em;color:#888">{metrics['in_one_line_after']['word_count']}語 /
{metrics['in_one_line_after']['sentence_count']}文</span></td>
</tr>
</table>

<h3>決定論指標</h3>
<ul>
<li>JA段落数 = Trial EN段落数: {metrics['ja_paragraph_count']} = {metrics['trial_en_paragraph_count']}
({'一致' if metrics['paragraph_count_match'] else '不一致'})</li>
<li>固有名詞・数字(改良カウンタ): JA={metrics['ja_entity_count_improved']}件 /
Trial EN={metrics['trial_en_entity_count_improved']}件</li>
<li>3分割の境界(段落index): {split['boundary_i']} / {split['boundary_j']}
(全{split['paragraph_count']}段落)</li>
</ul>

<h3>Rubric(1〜5点、Baseline/Trial比較、LLM 1 call)</h3>
{_rubric_table_html(result['rubric']['parsed']['items'])}

<h3>Baseline(見出し除去後) vs Trial 差分(word-level diff)</h3>
{diff_html}

<p style="font-size:0.85em;color:#888">Cost: 総額 ¥{result['cost']['total_jpy']}
(予算¥{result['cost']['budget_jpy']}、超過={result['cost']['over_budget']})</p>
{_render_v2_section(article_key, result)}
</section>
"""


def build_comparison_page(hormuz_result: dict, meta_result: dict, out_path: str) -> None:
    html_doc = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>Family X 見出し廃止Trial: Baseline vs Trial比較(Hormuz/Meta)</title>
<style>
body {{ font-family: -apple-system, "Segoe UI", sans-serif; max-width: 980px; margin: 24px auto; padding: 0 16px; }}
h1 {{ font-size: 1.4em; }}
h2 {{ font-size: 1.2em; }}
h3 {{ font-size: 1.05em; margin-top: 20px; }}
table {{ font-size: 0.9em; }}
</style>
</head>
<body>
<h1>FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01</h1>
<p>本文途中の見出しを廃止し、日本語完成記事を忠実英訳した上で、段落境界のみを
使った決定論的アルゴリズムでPart1/Part2/Part3へ3分割する構成のTrial結果です。
音声化(TTS)は行っておらず、text比較のみです。判定は<b>USER_DECISION_REQUIRED</b>
(ユーザー試読待ち)です。</p>
<ul>
<li><a href="#hormuz">Hormuz比較</a></li>
<li><a href="#meta">Meta比較</a></li>
</ul>
{render_article_section("hormuz", "Hormuz(石油価格ニュース)", hormuz_result)}
{render_article_section("meta", "Meta(Muse人間代行ニュース)", meta_result)}
</body>
</html>
"""
    save_text(out_path, html_doc)
    print(f"[ER-045] page written: {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--article", choices=["hormuz", "meta"])
    parser.add_argument("--source-dir")
    parser.add_argument("--out-dir")
    parser.add_argument("--budget-jpy", type=float, default=30.0)
    parser.add_argument("--build-page", action="store_true",
                         help="API呼び出しなし。既存trial_result.jsonから比較ページを組み立てる")
    parser.add_argument("--hormuz-result-dir")
    parser.add_argument("--meta-result-dir")
    parser.add_argument("--page-out")
    # 修正1回目(委任_02)で追加。--source-dir省略時はv1実行と同じSOURCE_DIRを使う。
    parser.add_argument("--stage", choices=["must-fix-retry", "in-one-line-v2", "rubric-v2"],
                         help="v1の trial_result.json を入力に、out-dir/v2/ へ新規artifactを追加する")
    args = parser.parse_args()

    if args.build_page:
        hormuz_result = load_json(f"{args.hormuz_result_dir}/trial_result.json")
        meta_result = load_json(f"{args.meta_result_dir}/trial_result.json")
        _attach_v2(hormuz_result, args.hormuz_result_dir)
        _attach_v2(meta_result, args.meta_result_dir)
        build_comparison_page(hormuz_result, meta_result, args.page_out)
        return

    if args.stage:
        if not (args.article and args.out_dir):
            parser.error("--article/--out-dirは--stage指定時も必須です")
        source_dir = args.source_dir or SOURCE_DIR
        if args.stage == "must-fix-retry":
            run_must_fix_retry_stage(args.article, source_dir, args.out_dir, args.budget_jpy)
        elif args.stage == "in-one-line-v2":
            run_in_one_line_v2_stage(args.article, args.out_dir, args.budget_jpy)
        elif args.stage == "rubric-v2":
            run_rubric_v2_stage(args.article, args.out_dir, args.budget_jpy)
        return

    if not (args.article and args.source_dir and args.out_dir):
        parser.error("--article/--source-dir/--out-dirは--build-page/--stage未指定時は必須です")
    run_trial(args.article, args.source_dir, args.out_dir, args.budget_jpy)


if __name__ == "__main__":
    main()
