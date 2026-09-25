# ============================================================
# er018_fiction_core_provocation_random_dna_trial_01.py
# 管理ID: FICTION-CORE-PROVOCATION-RANDOM-DNA-TRIAL-01
# ============================================================
# 目的: 旧Future(er013_family_c_future_provocation_08.py /
# er013_family_c_future_writer_08.py、Trial-08)の良かった設計 --
# 「先にCore Provocationを1-3案作り、最も面白いものを選んでからStoryを書く」
# 「分かりやすく、先が気になるStoryにする」 -- を残しつつ、Future限定
# ("about the future"/"imagined-future story"等)を外してFictionへ拡張する。
# 同時に、コード側乱数で選ぶStory DNA(5軸中2-3軸)を「発想をずらす刺激」
# として与え、LLM任せの毎回似たテイストになる問題への対処を確認する
# (Trialのみ。Production変更なし)。
#
# 既存er013_family_c_future_*.py・er013_output/family_c_future_trial_*/は
# 一切変更しない(read-onlyでのimport/参照のみ)。
# Status: Trial専用、未承認draft実装(`APPROVED_FOR_PRODUCTION`ではない)。
# 到達上限: VALIDATED(Production採用は本タスクの対象外)。
#
# 実行方法(root直下、4 step):
#   .venv/Scripts/python.exe er018_fiction_core_provocation_random_dna_trial_01.py \
#       --out-dir er018_output/fiction_core_provocation_random_dna_trial_01 \
#       --step dna --seed-base 20260925
#   ...--step generate --budget-jpy 30
#   ...--step analyze
#   ...--step assemble
# ============================================================
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import re
import sys
from collections import Counter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er003_v1_en_direct_vfl_01_generate as vfl01  # get_client()のみ再利用(read-only import)

PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0  # er005_cost_logger.pyのUSD_JPYと同一値(参考、記録用)

# ------------------------------------------------------------
# Story DNA定義(5軸、日本語+英語併記。委任文の定義を逐語で反映)
# ------------------------------------------------------------
AXIS_DEFS = {
    "A": {
        "name_en": "Relationship", "name_ja": "関係性",
        "values": [
            ("family", "家族"), ("friends", "友人"), ("lovers", "恋人"),
            ("colleagues", "同僚"), ("strangers", "見知らぬ人"), ("oneself", "自分自身"),
        ],
    },
    "B": {
        "name_en": "Emotional tone", "name_ja": "感情トーン",
        "values": [
            ("warm", "温かい"), ("unsettling", "不穏"), ("bittersweet", "切ない"),
            ("black comedy", "ブラックユーモア"), ("exhilarating", "爽快"), ("strange/odd", "奇妙"),
        ],
    },
    "C": {
        "name_en": "Central drama", "name_ja": "中心となるドラマ",
        "values": [
            ("a choice", "選択"), ("a secret", "秘密"), ("a misunderstanding", "誤解"),
            ("a reversal", "逆転"), ("a loss", "喪失"), ("a discovery", "発見"),
            ("a prohibition", "禁止"), ("an exchange", "交換"),
        ],
    },
    "D": {
        "name_en": "Setting/place", "name_ja": "舞台",
        "values": [
            ("home", "家"), ("school", "学校"), ("a workplace", "職場"), ("a shop", "店"),
            ("a hospital", "病院"), ("a trip destination", "旅先"),
            ("a public space", "公共空間"), ("a special place", "特殊な場所"),
        ],
    },
    "E": {
        "name_en": "World / distance from reality", "name_ja": "世界設定/現実との距離",
        "values": [
            ("contemporary everyday life", "現代の日常"),
            ("a near future", "少し先の未来"),
            ("a greatly changed future", "大きく変わった未来"),
            ("a world with technology or institutions that do not exist in reality", "現実にはない技術・制度がある世界"),
            ("a supernatural or fantastical world", "超自然・幻想的な世界"),
            ("a world almost identical to reality except one rule is different", "現実とほぼ同じだが、1つだけルールが違う世界"),
        ],
    },
}
AXIS_ORDER = ["A", "B", "C", "D", "E"]
# 委任文のRun5(Future Coverage Run)用: E軸をFuture系3値(少し先の未来/
# 大きく変わった未来/現実にはない技術・制度がある世界)へ限定するためのindex。
E_FUTURE_VALUE_INDICES = [1, 2, 3]

THEME_LABEL_EN = "memory"
THEME_LABEL_JA = "記憶"

TOTAL_RUNS = 5
COVERAGE_RUN_NUMBER = 5  # Run5がFuture Coverage Run


# ------------------------------------------------------------
# 乱数によるStory DNA選定(LLMには渡さず、コード側random.Randomで決定)
# ------------------------------------------------------------
def select_dna(seed: int, is_coverage_run: bool) -> dict:
    """random.Random(seed)による決定的選定。
    通常run: 軸数k∈{2,3}を等確率で選び、5軸からk軸を非復元抽出、各軸1値をランダム選択。
    Run5(is_coverage_run): E軸を必須で含め、Eの値はFuture系3値からのみ選択。
    残り(k-1)軸はA/B/C/Dから通常どおりランダム抽出。"""
    rng = random.Random(seed)
    k = rng.choice([2, 3])
    values = {}
    if not is_coverage_run:
        axes = sorted(rng.sample(AXIS_ORDER, k))
        for axis in axes:
            idx = rng.randrange(len(AXIS_DEFS[axis]["values"]))
            values[axis] = list(AXIS_DEFS[axis]["values"][idx])
    else:
        other_count = k - 1
        other_axes = sorted(rng.sample(["A", "B", "C", "D"], other_count))
        axes = sorted(["E"] + other_axes)
        e_idx = rng.choice(E_FUTURE_VALUE_INDICES)
        values["E"] = list(AXIS_DEFS["E"]["values"][e_idx])
        for axis in other_axes:
            idx = rng.randrange(len(AXIS_DEFS[axis]["values"]))
            values[axis] = list(AXIS_DEFS[axis]["values"][idx])
    unused_axes = [a for a in AXIS_ORDER if a not in axes]
    return {
        "seed": seed, "is_coverage_run": is_coverage_run, "k": k,
        "axes": axes, "values": values, "unused_axes": unused_axes,
    }


def build_dna_log(seed_base: int) -> dict:
    runs = []
    for run_number in range(1, TOTAL_RUNS + 1):
        seed = seed_base + run_number
        is_coverage = (run_number == COVERAGE_RUN_NUMBER)
        entry = select_dna(seed, is_coverage)
        entry["run"] = run_number
        runs.append(entry)
    return {
        "seed_base": seed_base, "theme_label_en": THEME_LABEL_EN,
        "theme_label_ja": THEME_LABEL_JA, "total_runs": TOTAL_RUNS,
        "coverage_run_number": COVERAGE_RUN_NUMBER, "runs": runs,
    }


def format_dna_lines(dna_entry: dict) -> str:
    lines = []
    for axis in dna_entry["axes"]:
        name_en = AXIS_DEFS[axis]["name_en"]
        name_ja = AXIS_DEFS[axis]["name_ja"]
        val_en, val_ja = dna_entry["values"][axis]
        lines.append(f"- {name_en} / {name_ja}: {val_en} / {val_ja}")
    return "\n".join(lines)


# ------------------------------------------------------------
# 共通原則(委任文の逐語)
# ------------------------------------------------------------
COMMON_PRINCIPLES = (
    "A good premise here makes the listener want to know what happens next. Prefer "
    "concrete events over abstract or literary implication. Keep to a small cast, one "
    "time frame, and few places. Meaning may come at the end, but the story itself "
    "must be clear first."
)

DNA_BLOCK_TEMPLATE = (
    "[Story DNA — a creative nudge, not a contract]\n"
    "Use the following elements as a nudge to move your thinking away from your "
    "default story. You may interpret them freely. Do not force them; if an element "
    "does not fit naturally, let it stay in the background.\n"
    "{dna_lines}\n"
    "Everything not listed here is yours to decide."
)


def build_dna_block(dna_entry: dict) -> str:
    return DNA_BLOCK_TEMPLATE.format(dna_lines=format_dna_lines(dna_entry))


# ------------------------------------------------------------
# Core Provocation Prompt(旧Trial-08 provocation_08.pyを逐語ベースに、
# Future限定語句のみ置換。差分はprompt_diff_provocation.mdへ別途記録)
# ------------------------------------------------------------
CORE_PROVOCATION_DEVELOPER_MESSAGE = (
    "You are brainstorming Core Provocations for a short fiction story in an "
    "English-learning magazine's Fiction article family. A Core Provocation is a "
    "single central idea or question -- regardless of whether the story takes place "
    "in the real world, the future, an unreal/fantastical setting, or an "
    "imagined/speculative world -- that would make a reader feel 'I want to know what "
    "happens next' and 'I have never thought about it this way before'. Come up with 1 "
    "to 3 promising central ideas for the given theme (fewer, stronger ideas are "
    "better than three weak ones -- do not pad to 3 just to fill the list). Do NOT "
    "classify ideas by scale (intimate/personal vs societal vs radical) or by any "
    "other fixed category -- just judge which idea is most genuinely interesting and "
    "story-worthy. Then pick the single most interesting one to write as the article."
)

CORE_PROVOCATION_PROMPT_TEMPLATE = """[Theme]
{theme_label}

{dna_block}

[Common principles for this story family]
{common_principles}

[Task]
1. Propose 1 to 3 candidate Core Provocations for this theme. For each, give a short
   core_provocation (1-2 sentences) and why_interesting (1 sentence).
2. Pick the single one that would make the best short story for a reader who wants to
   keep reading and feel some excitement and a little tension. Set chosen_index to
   that candidate's 0-based index in the candidates array and give a short
   reason_for_choice."""

CORE_PROVOCATION_JSON_SCHEMA = {
    "name": "fiction_core_provocation_random_dna",
    "schema": {
        "type": "object",
        "properties": {
            "candidates": {
                "type": "array",
                "minItems": 1,
                "maxItems": 3,
                "items": {
                    "type": "object",
                    "properties": {
                        "core_provocation": {
                            "type": "string",
                            "description": "1-2 sentences: the central idea/question this story would explore.",
                        },
                        "why_interesting": {
                            "type": "string",
                            "description": "1 short sentence: why this would genuinely excite a reader.",
                        },
                    },
                    "required": ["core_provocation", "why_interesting"],
                    "additionalProperties": False,
                },
            },
            "chosen_index": {
                "type": "integer",
                "description": "0-based index into candidates array of the selected candidate.",
            },
            "reason_for_choice": {
                "type": "string",
                "description": "1-2 sentences: why this candidate is the most interesting to write as a story.",
            },
        },
        "required": ["candidates", "chosen_index", "reason_for_choice"],
        "additionalProperties": False,
    },
    "strict": True,
}


def build_core_provocation_prompt(dna_entry: dict) -> str:
    theme_label = f"{THEME_LABEL_EN} ({THEME_LABEL_JA})"
    return CORE_PROVOCATION_PROMPT_TEMPLATE.format(
        theme_label=theme_label, dna_block=build_dna_block(dna_entry),
        common_principles=COMMON_PRINCIPLES,
    )


def generate_core_provocation(client, model: str, effort: str, prompt: str) -> dict:
    response = client.responses.create(
        model=model,
        reasoning={"effort": effort},
        text={"format": {"type": "json_schema", **CORE_PROVOCATION_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": CORE_PROVOCATION_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    if not text or not text.strip():
        raise RuntimeError("Core Provocation応答が空です")
    parsed = json.loads(text)
    candidates = parsed["candidates"]
    chosen_index = parsed["chosen_index"]
    if not isinstance(chosen_index, int) or not (0 <= chosen_index < len(candidates)):
        raise RuntimeError(
            f"chosen_index({chosen_index})が候補範囲外です(candidates数={len(candidates)})")
    return {
        "parsed": parsed, "chosen_index": chosen_index,
        "selected": candidates[chosen_index],
        "reason_for_choice": parsed["reason_for_choice"],
        "model": response.model, "response_id": response.id,
    }


# ------------------------------------------------------------
# Story Prompt(旧Trial-08 writer_08.pyを逐語ベースに、Future限定語句を
# 置換。IMAGINEDマーカー/CURRENT FACT禁止ブロックは、Future family固有の
# 技術的安全機構であり単純な語句置換では一般Fictionへ持ち越せないため
# 削除[このTrialにFact Safety層・マーカー再試行は実装しない、10 call予算とも
# 整合]。詳細差分はprompt_diff_writer.mdへ記録。
# Characters/Length/Listening-friendliness各ブロックはv8を逐語のまま維持
# (Future限定語句を含まないため)。
# ------------------------------------------------------------
WRITER_DEVELOPER_MESSAGE = (
    "You are the Writer for an English-learning magazine's Fiction article family. "
    "Your single most important job is to make the reader genuinely feel the Core "
    "Provocation given to you -- excitement, a little tension, and a question that "
    "stays with them, so they want to keep reading. Write it as a story: a vivid scene "
    "built around the Core Provocation, not a summary of studies or an abstract essay. "
    "The setting can be realistic, near-future, far-future, or entirely "
    "unreal/speculative -- whatever fits the Core Provocation best. Do not force the "
    "story into any fixed template, fixed number of scenes, fixed number of emotional "
    "turns, or a fixed ending shape -- choose whatever shape makes this particular Core "
    "Provocation land most strongly."
)

MAX_CHARACTERS = 3  # v8踏襲(基本1-2人・最大3人、主人公のみ固有名可)
WORD_TARGET = 350
WORD_ACCEPTABLE_RANGE = (280, 420)  # 委任文の目安どおり(v8は300-420、今回は280-420)

WRITER_PROMPT_TEMPLATE = """[Core Provocation -- this must drive the whole article]
{core_provocation}

[Theme]
{theme_label}

{dna_block}

[Common principles for this story family]
{common_principles}

[Your single job]
Write a short story built around the Core Provocation above, in whatever kind of \
setting fits it best (real, future, unreal, or an imagined/speculative world). Make \
a reader genuinely feel something, want to keep reading, and feel some excitement and \
a little tension along the way. Do not follow any fixed structure, fixed number of \
scenes, fixed number of emotional turns, or a fixed ending shape -- choose whatever \
narrative shape makes THIS Core Provocation land most strongly.

[Characters -- keep it simple]
Use 1 or 2 characters as the core of the story; {max_characters} at the absolute most \
if truly needed. Only the main character (the protagonist) may be given a personal \
name. Every other person should be referred to through their relationship to the main \
character (for example: her mother, his father, her friend, their daughter, his \
neighbor) instead of a separate name. Do not add named characters that are not \
necessary for the story.

[Length and level]
- Write for an A2-level English learner: short, clear sentences, common vocabulary, \
simple hedging like "might"/"could"/"If ... , ...".
- Target length for the reader-facing text is about {word_target} words (roughly \
{range_low}-{range_high} words is fine).

[Listening-friendliness -- an editorial goal, not a hard rule]
This article will also be listened to as audio. Try to keep it easy for a listener to \
follow: avoid introducing more named people than necessary, avoid jumping between many \
different times or places, avoid long strings of abstract explanation, and try to keep \
it reasonably clear at each point whose perspective the reader/listener is in.

Write the article now. Do not add a title unless it helps the story -- if you do, keep \
it short."""


def build_story_prompt(core_provocation: str, dna_entry: dict) -> str:
    theme_label = f"{THEME_LABEL_EN} ({THEME_LABEL_JA})"
    return WRITER_PROMPT_TEMPLATE.format(
        core_provocation=core_provocation, theme_label=theme_label,
        dna_block=build_dna_block(dna_entry), common_principles=COMMON_PRINCIPLES,
        max_characters=MAX_CHARACTERS, word_target=WORD_TARGET,
        range_low=WORD_ACCEPTABLE_RANGE[0], range_high=WORD_ACCEPTABLE_RANGE[1],
    )


def generate_story(client, model: str, effort: str, prompt: str) -> dict:
    response = client.responses.create(
        model=model,
        reasoning={"effort": effort},
        input=[
            {"role": "developer", "content": WRITER_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    if not text or not text.strip():
        raise RuntimeError("Story応答が空です")
    return {"raw_text": text, "model": response.model, "response_id": response.id}


# ------------------------------------------------------------
# 空出力・schema失敗時の同一条件再試行(最大1回、委任文どおり)
# ------------------------------------------------------------
def call_with_retry(fn, max_attempts: int = 2) -> tuple:
    attempts = []
    last_exc = None
    for attempt in range(1, max_attempts + 1):
        try:
            result = fn()
            attempts.append({"attempt": attempt, "success": True})
            return result, attempts
        except (RuntimeError, ValueError, KeyError) as exc:
            attempts.append({"attempt": attempt, "success": False, "error": str(exc)[:500]})
            print(f"[retry] attempt {attempt} failed: {exc}")
            last_exc = exc
    raise RuntimeError(
        f"{max_attempts}回の試行でも成功しませんでした(同一条件再試行上限到達): {last_exc}"
    ) from last_exc


# ------------------------------------------------------------
# 費用計算(pricing_snapshot.jsonのluna単価をraw_usage_log.jsonlへ適用)
# ------------------------------------------------------------
def load_luna_pricing() -> dict:
    with open(PRICING_SNAPSHOT_PATH, encoding="utf-8") as f:
        snapshot = json.load(f)
    pricing = {}
    for entry in snapshot["prices"]:
        if entry.get("model") == "gpt-5.6-luna":
            pricing[entry["meter"]] = entry["price"]
    return pricing


def compute_cost_jpy(log_path: str) -> dict:
    if not os.path.exists(log_path):
        return {"total_usd": 0.0, "total_jpy": 0.0, "record_count": 0}
    pricing = load_luna_pricing()
    total_usd = 0.0
    record_count = 0
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            record_count += 1
            if not rec.get("success", True):
                continue
            if rec.get("model_id") != "gpt-5.6-luna":
                continue
            input_tokens = rec.get("input_tokens") or 0
            cached = rec.get("cached_input_tokens") or 0
            output_tokens = rec.get("output_tokens") or 0
            non_cached_input = max(input_tokens - cached, 0)
            total_usd += (non_cached_input / 1_000_000) * pricing["input_tokens"]
            total_usd += (cached / 1_000_000) * pricing["cached_input_tokens"]
            total_usd += (output_tokens / 1_000_000) * pricing["output_tokens"]
    return {
        "total_usd": round(total_usd, 6), "total_jpy": round(total_usd * USD_JPY, 2),
        "record_count": record_count,
    }


def budget_guard(stage_label: str, log_path: str, hard_cap_jpy: float) -> dict:
    cost = compute_cost_jpy(log_path)
    print(f"[budget_guard][{stage_label}] 累計={cost['total_jpy']} JPY (上限{hard_cap_jpy})")
    if cost["total_jpy"] > hard_cap_jpy:
        raise RuntimeError(
            f"[budget_guard][{stage_label}] 累計{cost['total_jpy']} JPYが上限{hard_cap_jpy} JPYを"
            "超過しました。STOP(以降のAPI呼び出しは行わない)。")
    return cost


# ------------------------------------------------------------
# ファイルI/Oヘルパー
# ------------------------------------------------------------
def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def save_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def load_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


STORY_MD_SEPARATOR = "\n---\n\n"


def build_story_md(run_number: int, dna_entry: dict, core_provocation: str, raw_text: str) -> str:
    header = [
        f"# Run {run_number}",
        "",
        f"**Seed**: {dna_entry['seed']}",
        f"**Selected DNA axes**: {', '.join(dna_entry['axes'])}"
        + (" (Future Coverage Run)" if dna_entry["is_coverage_run"] else ""),
        f"**DNA values**: {format_dna_lines(dna_entry).replace(chr(10), ' / ')}",
        f"**Core Provocation**: {core_provocation}",
    ]
    return "\n".join(header) + STORY_MD_SEPARATOR + raw_text.strip() + "\n"


def extract_reader_text(story_md: str) -> str:
    if STORY_MD_SEPARATOR in story_md:
        return story_md.split(STORY_MD_SEPARATOR, 1)[1].strip()
    return story_md.strip()


# ------------------------------------------------------------
# Step: dna
# ------------------------------------------------------------
def step_dna(out_dir: str, seed_base: int) -> None:
    dna_log = build_dna_log(seed_base)
    save_json(f"{out_dir}/dna_log.json", dna_log)
    for entry in dna_log["runs"]:
        save_json(f"{out_dir}/runs/run{entry['run']}/dna.json", entry)
    print(f"[step_dna] DONE. seed_base={seed_base} runs={len(dna_log['runs'])} -> {out_dir}/dna_log.json")


# ------------------------------------------------------------
# Step: generate(LLM呼び出し。5 Run x (Core Provocation 1 call + Story 1 call))
# ------------------------------------------------------------
def process_one_run(client, out_dir: str, run_number: int, dna_entry: dict,
                     log_path: str, budget_jpy: float) -> dict:
    run_dir = f"{out_dir}/runs/run{run_number}"
    theme_id_for_log = f"fiction_core_provocation_random_dna_trial_01_run{run_number}"

    provocation_model = routing.require_model_or_override(
        "A2_WRITER", routing.WRITER_MODEL,
        override_reason="FICTION-CORE-PROVOCATION-RANDOM-DNA-TRIAL-01: 自由生成Core "
                         "Provocation(Fiction、1-3案+選定)にA2_WRITER Approved Model"
                         "(Luna)を転用(新規process未定義、コスト影響なし、DEV/Trial限定)")
    provocation_prompt = build_core_provocation_prompt(dna_entry)
    save_text(f"{run_dir}/provocation_prompt.txt", provocation_prompt)

    def _call_provocation():
        with cl.logging_context(theme_id_for_log, "core_provocation"):
            return generate_core_provocation(client, provocation_model, "medium", provocation_prompt)

    prov_result, prov_attempts = call_with_retry(_call_provocation, max_attempts=2)
    save_json(f"{run_dir}/provocation.json", {
        "parsed": prov_result["parsed"], "chosen_index": prov_result["chosen_index"],
        "selected": prov_result["selected"], "reason_for_choice": prov_result["reason_for_choice"],
        "model": prov_result["model"], "response_id": prov_result["response_id"],
        "attempts": prov_attempts,
    })
    budget_guard(f"run{run_number}_after_provocation", log_path, budget_jpy)

    core_provocation = prov_result["selected"]["core_provocation"]

    story_model = routing.require_model_or_override(
        "A2_WRITER", routing.WRITER_MODEL,
        override_reason="FICTION-CORE-PROVOCATION-RANDOM-DNA-TRIAL-01: 自由生成Story"
                         "(Fiction、Story DNAナッジ付き)にA2_WRITER Approved Model(Luna)"
                         "を転用(新規process未定義、コスト影響なし、DEV/Trial限定)")
    story_prompt = build_story_prompt(core_provocation, dna_entry)
    save_text(f"{run_dir}/story_prompt.txt", story_prompt)

    def _call_story():
        with cl.logging_context(theme_id_for_log, "story"):
            return generate_story(client, story_model, "high", story_prompt)

    story_result, story_attempts = call_with_retry(_call_story, max_attempts=2)
    story_md = build_story_md(run_number, dna_entry, core_provocation, story_result["raw_text"])
    save_text(f"{run_dir}/story.md", story_md)
    budget_guard(f"run{run_number}_after_story", log_path, budget_jpy)

    api_meta = {
        "run": run_number,
        "core_provocation": {
            "model": prov_result["model"], "response_id": prov_result["response_id"],
            "effort": "medium", "attempts": prov_attempts,
        },
        "story": {
            "model": story_result["model"], "response_id": story_result["response_id"],
            "effort": "high", "attempts": story_attempts,
        },
    }
    save_json(f"{run_dir}/api_meta.json", api_meta)

    word_count = len(extract_reader_text(story_md).split())
    print(f"[step_generate][run{run_number}] DONE. word_count={word_count} "
          f"core_provocation_model={prov_result['model']} story_model={story_result['model']}")
    return {"api_meta": api_meta, "word_count": word_count}


def step_generate(out_dir: str, budget_jpy: float) -> None:
    dna_log_path = f"{out_dir}/dna_log.json"
    if not os.path.exists(dna_log_path):
        raise SystemExit(f"{dna_log_path}が存在しません。先に--step dnaを実行してください。")
    dna_log = load_json(dna_log_path)

    log_path = f"{out_dir}/raw_usage_log.jsonl"
    cl.install(log_path)
    budget_guard("start", log_path, budget_jpy)

    client = vfl01.get_client()

    results = []
    for entry in dna_log["runs"]:
        result = process_one_run(client, out_dir, entry["run"], entry, log_path, budget_jpy)
        results.append(result)

    final_cost = compute_cost_jpy(log_path)
    save_json(f"{out_dir}/cost.json", final_cost)
    print(f"[step_generate] ALL DONE. runs={len(results)} cost={final_cost}")


# ------------------------------------------------------------
# Step: analyze(機械参考指標。最終判断はFable/ユーザー)
# ------------------------------------------------------------
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_PROPER_NOUN_RE = re.compile(r"\b[A-Z][a-z]+\b")
_PAST_MARKERS_RE = re.compile(
    r"\b(was|were|had|said|went|knew|felt|could|would|did|got|took|came|saw|thought"
    r"|\w+ed)\b", re.IGNORECASE)
_PRESENT_MARKERS_RE = re.compile(
    r"\b(is|are|am|says|feels|knows|can|will|does|gets|takes|comes|sees|thinks)\b",
    re.IGNORECASE)
_EXCLUDE_PROPER_NOUNS = {"I"}


def count_words(text: str) -> int:
    return len(text.split())


def count_sentences(text: str) -> int:
    parts = [p for p in _SENTENCE_SPLIT_RE.split(text.strip()) if p.strip()]
    return len(parts)


def count_proper_nouns(text: str) -> dict:
    """文頭語を除外した、大文字始まり語の異なり数(登場人物数の参考ヒューリスティック)。
    委任文の定義(『固有名詞数/登場人物数(大文字名の異なり数)』)どおり、両指標を
    同一のヒューリスティックで算出する(参考指標、厳密なNLPではない)。"""
    sentences = [s for s in _SENTENCE_SPLIT_RE.split(text.strip()) if s.strip()]
    found = set()
    for sentence in sentences:
        words = sentence.split()
        for i, word in enumerate(words):
            if i == 0:
                continue  # 文頭語は除外(単なる大文字化の可能性)
            m = _PROPER_NOUN_RE.match(word.strip("\"'.,!?;:()"))
            if m and m.group(0) not in _EXCLUDE_PROPER_NOUNS:
                found.add(m.group(0))
    return {"distinct_proper_nouns": sorted(found), "count": len(found)}


def compute_tense_reference(text: str) -> dict:
    past = len(_PAST_MARKERS_RE.findall(text))
    present = len(_PRESENT_MARKERS_RE.findall(text))
    return {"past_marker_count": past, "present_marker_count": present,
            "note": "参考指標のみ(簡易正規表現、厳密な時制解析ではない)"}


def analyze_one_text(label: str, text: str) -> dict:
    proper_nouns = count_proper_nouns(text)
    return {
        "label": label,
        "word_count": count_words(text),
        "sentence_count": count_sentences(text),
        "proper_noun_count": proper_nouns["count"],
        "proper_nouns": proper_nouns["distinct_proper_nouns"],
        "character_count_heuristic": proper_nouns["count"],
        "tense_reference": compute_tense_reference(text),
    }


_TOKEN_RE = re.compile(r"[a-zA-Z']+")


def tokenize(text: str) -> list:
    return [t.lower() for t in _TOKEN_RE.findall(text)]


def compute_tfidf_vectors(docs: dict) -> dict:
    """標準ライブラリのみによる簡易TF-IDF(参考指標)。docs: {label: text}"""
    tokenized = {label: tokenize(text) for label, text in docs.items()}
    n_docs = len(tokenized)
    df = Counter()
    for tokens in tokenized.values():
        for term in set(tokens):
            df[term] += 1
    idf = {term: math.log((n_docs + 1) / (freq + 1)) + 1 for term, freq in df.items()}
    vectors = {}
    for label, tokens in tokenized.items():
        tf = Counter(tokens)
        total = sum(tf.values()) or 1
        vectors[label] = {term: (count / total) * idf[term] for term, count in tf.items()}
    return vectors


def cosine_similarity(vec_a: dict, vec_b: dict) -> float:
    common_terms = set(vec_a) & set(vec_b)
    dot = sum(vec_a[t] * vec_b[t] for t in common_terms)
    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


REFERENCE_DOCS = {
    "ref_trial08_memory": "er013_output/family_c_future_trial_08/memory/reader_facing_article.txt",
    "ref_episode10_memory_normalized": "er013_output/family_c_episode_trial_10/memory_a2/article_normalized.txt",
}


def sha256_of_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def step_analyze(out_dir: str) -> None:
    dna_log = load_json(f"{out_dir}/dna_log.json")
    run_texts = {}
    per_run_metrics = []
    for entry in dna_log["runs"]:
        run_number = entry["run"]
        story_md = load_text(f"{out_dir}/runs/run{run_number}/story.md")
        reader_text = extract_reader_text(story_md)
        label = f"run{run_number}"
        run_texts[label] = reader_text
        metrics = analyze_one_text(label, reader_text)
        metrics["run"] = run_number
        metrics["seed"] = entry["seed"]
        metrics["axes"] = entry["axes"]
        metrics["is_coverage_run"] = entry["is_coverage_run"]
        save_json(f"{out_dir}/runs/run{run_number}/metrics.json", metrics)
        per_run_metrics.append(metrics)

    reference_texts = {}
    reference_meta = []
    for label, path in REFERENCE_DOCS.items():
        text = load_text(path)
        reference_texts[label] = text
        reference_meta.append({
            "label": label, "path": path, "sha256": sha256_of_file(path),
            "word_count": count_words(text),
        })

    all_docs = {**run_texts, **reference_texts}
    vectors = compute_tfidf_vectors(all_docs)
    labels = list(all_docs.keys())
    matrix = {}
    for a in labels:
        matrix[a] = {}
        for b in labels:
            matrix[a][b] = round(cosine_similarity(vectors[a], vectors[b]), 4)

    save_json(f"{out_dir}/similarity_matrix.json", {"labels": labels, "matrix": matrix})
    save_json(f"{out_dir}/machine_metrics_summary.json", {
        "per_run_metrics": per_run_metrics, "reference_docs": reference_meta,
    })
    print(f"[step_analyze] DONE. runs={len(per_run_metrics)} "
          f"reference_docs={[m['label'] for m in reference_meta]}")


# ------------------------------------------------------------
# Step: assemble(stories_all.md / blind.md / blind_key.json)
# ------------------------------------------------------------
BLIND_SYMBOLS = ["Story-P", "Story-Q", "Story-R", "Story-S", "Story-T"]
BLIND_SEED_OFFSET = 999  # dna生成用seedと衝突しない専用offset


def step_assemble(out_dir: str, seed_base: int) -> None:
    dna_log = load_json(f"{out_dir}/dna_log.json")
    runs = dna_log["runs"]

    all_parts = [
        "# FICTION-CORE-PROVOCATION-RANDOM-DNA-TRIAL-01 -- stories_all.md\n",
        "Trial専用、Production採用ではない。最大Status: VALIDATED。\n",
    ]
    blind_texts = {}
    for entry in runs:
        run_number = entry["run"]
        run_dir = f"{out_dir}/runs/run{run_number}"
        story_md = load_text(f"{run_dir}/story.md")
        provocation = load_json(f"{run_dir}/provocation.json")
        reader_text = extract_reader_text(story_md)
        blind_texts[run_number] = reader_text

        all_parts.append(f"\n## Run {run_number}"
                          + (" (Future Coverage Run)" if entry["is_coverage_run"] else "") + "\n")
        all_parts.append(f"**Seed**: {entry['seed']}\n")
        all_parts.append(f"**Selected DNA axes**: {', '.join(entry['axes'])}\n")
        all_parts.append(f"**DNA values**:\n{format_dna_lines(entry)}\n")
        all_parts.append(f"**Core Provocation**: {provocation['selected']['core_provocation']}\n")
        all_parts.append(f"**why_interesting**: {provocation['selected']['why_interesting']}\n")
        all_parts.append(f"**reason_for_choice**: {provocation['reason_for_choice']}\n")
        all_parts.append("```\n" + reader_text + "\n```\n")

    save_text(f"{out_dir}/stories_all.md", "\n".join(all_parts))

    # ブラインド用シャッフル(専用seed、dna選定とは独立)
    rng = random.Random(seed_base + BLIND_SEED_OFFSET)
    run_numbers = [entry["run"] for entry in runs]
    shuffled = run_numbers[:]
    rng.shuffle(shuffled)
    blind_key = {
        "seed": seed_base + BLIND_SEED_OFFSET,
        "mapping": {BLIND_SYMBOLS[i]: shuffled[i] for i in range(len(shuffled))},
    }
    save_json(f"{out_dir}/blind_key.json", blind_key)

    blind_parts = [
        "# FICTION-CORE-PROVOCATION-RANDOM-DNA-TRIAL-01 -- blind.md\n",
        "DNA/Core Provocationを伏せた5本(記号はランダム、blind_key.jsonで対応確認)。\n",
    ]
    for symbol in BLIND_SYMBOLS:
        run_number = blind_key["mapping"][symbol]
        blind_parts.append(f"\n## {symbol}\n")
        blind_parts.append("```\n" + blind_texts[run_number] + "\n```\n")
    save_text(f"{out_dir}/blind.md", "\n".join(blind_parts))

    print(f"[step_assemble] DONE. stories_all.md/blind.md/blind_key.json -> {out_dir}")


# ------------------------------------------------------------
# main
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--step", required=True, choices=["dna", "generate", "analyze", "assemble"])
    parser.add_argument("--seed-base", type=int, default=20260925)
    parser.add_argument("--budget-jpy", type=float, default=30.0)
    args = parser.parse_args()

    if args.step == "dna":
        step_dna(args.out_dir, args.seed_base)
    elif args.step == "generate":
        step_generate(args.out_dir, args.budget_jpy)
    elif args.step == "analyze":
        step_analyze(args.out_dir)
    elif args.step == "assemble":
        step_assemble(args.out_dir, args.seed_base)


if __name__ == "__main__":
    main()
