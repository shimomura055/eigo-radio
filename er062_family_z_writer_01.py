# -*- coding: utf-8 -*-
"""FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_04B: Family Z Writer鎖・Standard調整・Story分割・
Dialogue話者判定・Preview/Comment/KP・来歴(provenance)。

【位置づけ】Family Z(Fiction) Production正式path用module。ただしPRODUCTION_WIRED未達
(er026 runnerへの統合は後続)。本moduleはTrial(er059)をimportしない。
【構成】構造処理(純粋関数・課金0)は er062_family_z_structure_01.py。本fileはLLM呼出・stage管理・CLI。
【Prompt】R0/R1/R2/Std調整はTrial②(er059 Sol only)のPrompt/effort/developer文を正式化(B3Zなし)。
  Advanced化のための差分(最小): Length and levelをA2→Advanced(B1-B2相当・400-560語)、Seed変換計画の
  A2/語数文言の置換、原作保持条件・Story Type metadata・タイトル行の追加。
【Model】routing key経由(FAMILY_Z_WRITER_ADV_R0/R1/R2, FAMILY_Z_STD_ADJUST=gpt-6.1-sol、
  FAMILY_Z_STORY_SPLIT, FAMILY_Z_DIALOGUE_ATTRIBUTION=gpt-6-luna)。返却model不一致はSTOP。
【R2固定】retry/regenerationは明示 --regenerate-stage のみ。親sha不一致はSTOP(FamilyZProvenanceMismatchStop)。
【語数Guardrail(OPEN-302、未承認)】Adv 400-560 / Std 300-500かつAdv比85-110% は WARN。再生成は明示指定時のみ。
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import json
import os
import re
import sys
import time

import er006_model_routing_contract_01 as routing
import er062_family_z_structure_01 as st
from er062_family_z_structure_01 import (  # noqa: F401  (公開再export)
    FamilyZDialogueMismatchStop, FamilyZLintStop, FamilyZPlanStop, FamilyZProvenanceMismatchStop,
    FamilyZSplitStop, FamilyZStop, sha,
)

ROOT = os.path.dirname(os.path.abspath(__file__))
RUN_ROOT = "er026_output/family_z_production_e2e_01"
PRICING = os.path.join(ROOT, "er005_output", "cost_baseline_01", "pricing_snapshot.json")
USD_JPY = 160.0
THEME_TAG = "FAMILY_Z_MELOS_SOL_PRODUCTION_E2E_01_WRITER"

LEVEL_DIR = {"a2": "a2", "b1b": "b1b"}          # a2=Standard, b1b=Advanced
WRITER_EFFORT = "high"                            # Trial②と同じ(温度は推論モデルのため指定しない)
SPLIT_EFFORT = "medium"
ATTRIBUTION_EFFORT = "medium"

ADV_WORD_RANGE = (400, 560)                       # OPEN-302(未承認Guardrail)
STD_WORD_RANGE = (300, 500)
STD_ADV_RATIO_RANGE = (0.85, 1.10)
STD_AVG_SENT_FACTOR = 0.85                        # soft gate(WARN)
STD_IDENTICAL_FAIL = 0.50                         # M8: 一致文率>=50%でFAIL

CHAIN_STAGES = ("r0", "r1", "r2", "std_adjust")
STAGE_KEY = {"r0": "FAMILY_Z_WRITER_ADV_R0", "r1": "FAMILY_Z_WRITER_ADV_R1",
             "r2": "FAMILY_Z_WRITER_ADV_R2", "std_adjust": "FAMILY_Z_STD_ADJUST"}
STAGE_FILE = {"r0": "r0.md", "r1": "r1.md", "r2": "r2.md", "std_adjust": "std.md"}
# 依存(親→子)。regenerate時は推移的な子孫をstale扱いにする。
DEPENDENTS = {
    "r0": ["r1"], "r1": ["r2"], "r2": ["std_adjust", "plan_b1b", "kp_b1b"],
    "std_adjust": ["plan_a2", "kp_a2"], "plan_b1b": ["plan_a2", "support_b1b"], "plan_a2": ["support_a2"],
}
ALL_STAGE_NAMES = ("r0", "r1", "r2", "std_adjust", "plan_b1b", "plan_a2",
                   "support_b1b", "support_a2", "kp_b1b", "kp_a2")

# ------------------------------------------------------------
# Prompt(Trial②正式化)
# ------------------------------------------------------------
# Trial②(er059 -> er018 e_axis.WRITER_DEVELOPER_MESSAGE)逐語。testでsha照合する。
WRITER_DEVELOPER_MESSAGE = (
    "You are the Writer for an English-learning magazine's Fiction article family. "
    "Your single most important job is to make the reader genuinely feel the Core "
    "Provocation given to you -- excitement, a little tension, and a question that "
    "stays with them, so they want to keep reading. Write it as a story: a vivid scene "
    "built around the Core Provocation, not a summary of studies or an abstract essay. "
    "Do not force the story into any fixed template, fixed number of scenes, fixed "
    "number of emotional turns, or a fixed ending shape -- choose whatever shape makes "
    "this particular Core Provocation land most strongly."
)

# Trial②のR0 Promptのうち、Advanced化で変更しないブロック(逐語。testでTrial r0_prompt.txtと照合)。
R0_BLOCK_COMMON = """[Common principles for this story family]
A good premise here makes the listener want to know what happens next. Prefer concrete events over abstract or literary implication. Keep to a small cast, one time frame, and few places. Meaning may come at the end, but the story itself must be clear first.

[Your single job]
Write a short story inspired by the Story Seed above. Make a reader genuinely feel something, want to keep reading, and feel some excitement and a little tension along the way. Do not follow any fixed structure, fixed number of scenes, fixed number of emotional turns, or a fixed ending shape -- choose whatever narrative shape makes THIS Story Seed land most strongly. Do not just retell the original source with no changes at all, but also do not force superficial changes for their own sake -- a faithful, simplified retelling of the real event is welcome here.

[Characters -- keep it simple]
Use 1 or 2 characters as the core of the story; 3 at the absolute most if truly needed. Only the main character (the protagonist) may be given a personal name. Every other person should be referred to through their relationship to the main character (for example: her mother, his father, her friend, their daughter, his neighbor) instead of a separate name. Do not add named characters that are not necessary for the story."""

R0_BLOCK_LISTENING = """[Listening-friendliness -- an editorial goal, not a hard rule]
This article will also be listened to as audio. Try to keep it easy for a listener to follow: avoid introducing more named people than necessary, avoid jumping between many different times or places, avoid long strings of abstract explanation, and try to keep it reasonably clear at each point whose perspective the reader/listener is in."""

# Advanced化の差分ブロック(Trialは「A2・約350語(280-420)」だった)
R0_BLOCK_LENGTH_ADV = """[Length and level]
- Write natural, fluent English for an upper-intermediate learner (around CEFR B1-B2): varied sentence structures, richer but common vocabulary, natural rhythm. It must still be easy to follow by ear.
- Target length for the reader-facing text is about 480 words (roughly 400-560 words is fine)."""

# 追加ブロック(Trialに無い。原作保持条件・Story Type metadata)
R0_BLOCK_PRESERVATION = """[Preservation conditions -- the original's identity]
- Keep every Story Seed element above, in the same order of events.
- Keep the central story, the relationships between the characters (who threatens, who trusts, who waits for whom), and the ending's outcome (what finally happens to each main character) as stated in the Seed. Do not invent a different ending.
- Do not add new named people, new places, or new events that change the cause-and-effect of the story."""

R0_BLOCK_STORY_TYPE = """[Story Type]
{story_type} (a Public Domain literature adaptation; do not describe it as news or as a true story)."""

R0_BLOCK_FINAL = ('Write the article now. Begin with a short title on the first line as a Markdown heading ("# Title"), '
                  'then the story.')

R0_TEMPLATE = (
    "[Story Seed -- inspired by a real, rights-cleared source, freely reimagined;\n"
    "this is NOT a summary to reproduce, just raw material]\n{seed_bullets}\n\n"
    "[How to convert it]\n{conversion}\n\n"
    + R0_BLOCK_PRESERVATION + "\n\n"
    + R0_BLOCK_STORY_TYPE + "\n\n"
    + R0_BLOCK_COMMON + "\n\n"
    + R0_BLOCK_LENGTH_ADV + "\n\n"
    + R0_BLOCK_LISTENING + "\n\n"
    + R0_BLOCK_FINAL
)

# Seed変換計画のAdvanced化置換(A2・語数文言のみ。見つからなければ末尾に上書き指示を追加)
_CONVERSION_SUBSTITUTIONS = (
    (re.compile(r"simple third-person English at about 300[–-]350 words"), "natural third-person English at about 480 words"),
    (re.compile(r"while simplifying the language and minor details for A2 learners"),
     "while keeping minor details light, for upper-intermediate (B1-B2) learners"),
)
_CONVERSION_OVERRIDE = ("\nLevel and length override: write natural upper-intermediate (B1-B2) English, about 480 words "
                        "(roughly 400-560); ignore any earlier A2 / word-count instruction.")

# R1/R2(Trial②のREVISE_USER_TMPLのAdvanced化: A2・280-420語 -> B1-B2相当・400-560語)
REVISE_USER_TMPL = ("Here is a short story:\n\n{body}\n\n"
                    "Without changing the events, the characters, or the cause-and-effect, please revise it into a more engaging story. "
                    "Keep it at a natural upper-intermediate level (CEFR B1-B2), about 400-560 words, in third person, "
                    "and only Melos may have a personal name. Output the title and the story only.")

# Std調整(Z専用): X共有ブロックはimport(STANDARD_A2_NEW_VOCAB_BLOCK/STANDARD_A2_DEVELOPER)。
# 「## In one line」要求と見出し構造の記述は含めない。段落整列契約・同一本文禁止を追加。
STD_PROMPT_HEAD = """Rewrite this entire story for CEFR A2 learners.
Simplify the English, not the story.

Rebuild the sentences. Do not just replace difficult words. Write every sentence again using simpler grammar and shorter structures. Do not leave a sentence unchanged just because it is already simple enough; the result must not be the same text as the source.
Aim for an average sentence length clearly shorter than the source (about 9-11 words across the whole story). Some sentences may be longer or shorter; do not force every sentence to the same length.
Use mostly one main idea per sentence. Split long clauses. Do not pack a cause, an extra detail, an exception, and a result into one sentence.
"""
STD_PROMPT_TAIL = """

Preserve the same story, the same order of events, the same surprise in the same place, the important metaphor or storytelling device, and the same ending.
Do not turn the story into a summary.
Do not remove an entertaining detail only because it is harder to express. Say it in simpler English instead.
Do not add new facts, new explanations, new characters, or new general observations.
Keep every fact exactly as it is: who did what, cause and effect, the order of events, negations, and limitations.

The result must still sound natural when read aloud. Do not write like a children's book, and do not write a flat list of short sentences.

Paragraph alignment (required): the source story below has exactly {n_paragraphs} paragraphs. Your output must have exactly {n_paragraphs} paragraphs, in the same order, one for each source paragraph. Do not merge, split, add, remove, or reorder paragraphs. A paragraph that is dialogue stays dialogue.
Length: about {target_words} words in the body (between {lo_words} and {hi_words}).
Keep the title as a single "# " line first. Do not add section headings, subheadings, a closing summary, or any "In one line" section.

Output only the English title and the English body.

[Story]
{advanced_story}"""

# ------------------------------------------------------------
# Split / Dialogue Prompt
# ------------------------------------------------------------
SPLIT_DEVELOPER = ("You are an editor who divides a short English story into three listening parts for an audio "
                   "program. You only choose among the allowed boundary options you are given.")
SPLIT_USER_TMPL = """Below is a short story, split into numbered paragraphs. Each paragraph shows its index and word count.
The story will be played as three consecutive parts with a short spoken comment between the parts.
Choose where Part 2 starts and where Part 3 starts, so that each part ends at a natural scene change or a turning point of meaning (not in the middle of an exchange or an action), and so that the three parts feel balanced.

Allowed options (you MUST choose from these; any other pair is rejected):
{options}
Meaning: "part2_starts_at_paragraph" = b1, "part3_starts_at_paragraph" = b2. For each b1, the allowed b2 values are the ranges shown.

Give a short reason in Japanese (1-3 sentences) that explains the scene or turning point at each boundary.

[Story]
{numbered_story}"""
SPLIT_SCHEMA = {
    "name": "z_split_choice",
    "schema": {"type": "object",
               "properties": {"part2_starts_at_paragraph": {"type": "integer"},
                              "part3_starts_at_paragraph": {"type": "integer"},
                              "reason_ja": {"type": "string"}},
               "required": ["part2_starts_at_paragraph", "part3_starts_at_paragraph", "reason_ja"],
               "additionalProperties": False},
    "strict": True,
}
SPLIT_RETRY_TMPL = ("\n\nYour previous answer ({prev}) is not one of the allowed options ({why}). "
                    "Choose again, strictly from the allowed options above.")

ATTR_DEVELOPER = ("You identify who speaks each quoted line in a short English story. Use the meaning of the story, "
                  "not just which name is nearby.")
ATTR_USER_TMPL = """Below is a short story. Every quoted line is marked with a tag of the form [[Q:id]] right before the opening quotation mark.
For EVERY tagged quote, decide the speaker:
- "melos": the main character, Melos (including when he speaks to the king or to his friend)
- "king": the ruler / tyrant / king
- "friend": Melos's friend
- "other": any other speaker (a guard, bandits, a sister, a crowd, etc.)
- "narrator": the line is not spoken by a character (e.g. a quoted phrase used by the narrator)
Be careful: a name or role that appears NEAR a quote is not always the speaker (for example, in '"I will return," Melos told the king.' the speaker is melos, not king; in '"I am here," he said to his friend.' decide who "he" is from the story).
Return one entry per tag, exactly once, using exactly the id written inside the tag.

[Story]
{tagged_story}"""
ATTR_SCHEMA = {
    "name": "z_dialogue_attribution",
    "schema": {"type": "object",
               "properties": {"attributions": {"type": "array", "items": {
                   "type": "object",
                   "properties": {"quote_id": {"type": "string"},
                                  "speaker": {"type": "string", "enum": list(st.SPEAKERS)},
                                  "basis": {"type": "string"}},
                   "required": ["quote_id", "speaker", "basis"], "additionalProperties": False}}},
               "required": ["attributions"], "additionalProperties": False},
    "strict": True,
}

NOT_NEWS_NOTE = ("【注意】この本文はニュースではなく短い物語です。出力には「news」「In One Line」「Point」「Part」など、"
                 "制作内部の構造ラベルや番組構成を示す語を含めないでください。")


# ------------------------------------------------------------
# 基本I/O・費用
# ------------------------------------------------------------
def wt(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def wj(path, obj):
    wt(path, st.dumps(obj))


def rd(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def rj(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def file_sha(path):
    with open(path, "rb") as f:
        return sha(f.read())


def load_pricing(model):
    d = rj(PRICING)
    out = {}
    for e in d["prices"]:
        if e.get("provider") == "openai" and e.get("model") == model and e.get("tier") == "Standard":
            out[e["meter"]] = e["price"]
    for k in ("input_tokens", "cached_input_tokens", "output_tokens"):
        if k not in out:
            raise FamilyZStop(f"[STOP] 単価未登録 {model} {k}")
    return out


def cost_jpy(model, usage):
    p = load_pricing(model)
    inp = getattr(usage, "input_tokens", 0) or 0
    det = getattr(usage, "input_tokens_details", None)
    cached = (getattr(det, "cached_tokens", 0) or 0) if det is not None else 0
    outp = getattr(usage, "output_tokens", 0) or 0
    usd = (max(inp - cached, 0) * p["input_tokens"] + cached * p["cached_input_tokens"]
           + outp * p["output_tokens"]) / 1e6
    return usd * USD_JPY


class Budget:
    """1call前に 累計+次call見積 > 上限 ならSTOP。"""

    def __init__(self, cap_jpy: float, est_by_key: dict | None = None, default_est: float = 6.0):
        self.cap, self.spent, self.est, self.default_est = cap_jpy, 0.0, est_by_key or {}, default_est
        self.calls = []

    def before(self, key, label):
        e = self.est.get(key, self.default_est)
        if self.spent + e > self.cap:
            raise FamilyZStop(f"[STOP] 費用上限: 累計{self.spent:.2f}円+次call見積{e:.2f}円 > 上限{self.cap}円 ({label})")

    def add(self, v, rec=None):
        self.spent += v
        if rec is not None:
            self.calls.append(rec)


DEFAULT_EST = {"FAMILY_Z_WRITER_ADV_R0": 6.0, "FAMILY_Z_WRITER_ADV_R1": 8.0, "FAMILY_Z_WRITER_ADV_R2": 8.0,
               "FAMILY_Z_STD_ADJUST": 8.0, "FAMILY_Z_STORY_SPLIT": 1.0, "FAMILY_Z_DIALOGUE_ATTRIBUTION": 1.0}


class LLM:
    """routing key経由のResponses API呼出。技術失敗(例外/空出力)のみ最大1回retry。返却model不一致はSTOP。"""

    def __init__(self, client, budget: Budget):
        self.client, self.budget = client, budget

    def call(self, key, label, user, *, developer=None, effort, schema=None) -> dict:
        requested = routing.require_model(key, routing.PROCESS_MODEL_MAP[key])
        msgs = ([{"role": "developer", "content": developer}] if developer else []) + [{"role": "user", "content": user}]
        kw = {"model": requested, "reasoning": {"effort": effort}, "input": msgs}
        if schema is not None:
            kw["text"] = {"format": {"type": "json_schema", **schema}}
        last = None
        for attempt in (1, 2):
            self.budget.before(key, f"{label}#{attempt}")
            t0 = time.time()
            try:
                r = self.client.responses.create(**kw)
            except Exception as e:  # noqa: BLE001
                last = e
                continue
            c = cost_jpy(requested, r.usage)
            u = r.usage
            rec = {"label": label, "routing_key": key, "attempt": attempt, "requested_model": requested,
                   "actual_model_id": str(r.model), "response_id": r.id, "effort": effort,
                   "elapsed_sec": round(time.time() - t0, 1), "input_tokens": getattr(u, "input_tokens", None),
                   "output_tokens": getattr(u, "output_tokens", None),
                   "reasoning_tokens": getattr(getattr(u, "output_tokens_details", None), "reasoning_tokens", None),
                   "cost_jpy": round(c, 4)}
            self.budget.add(c, rec)
            if not str(r.model).startswith(requested):
                raise FamilyZStop(f"[STOP] 返却modelが{requested}で始まらない: {r.model} ({label})")
            if not (r.output_text or "").strip():
                last = RuntimeError("empty output")
                continue
            return {"text": r.output_text, "meta": rec, "attempts": attempt}
        raise FamilyZStop(f"[STOP] {label}: 技術失敗(2回): {last!r}")


# ------------------------------------------------------------
# Prompt組立
# ------------------------------------------------------------
def build_r0_prompt(seed: dict, story_type: str = "literature") -> tuple:
    """(prompt, substitutions_applied)。Seed(seed.json)からR0 Promptを作る。"""
    bullets = "\n".join(f"- {e}" for e in seed["seed_elements"])
    conv = seed.get("conversion_plan", "")
    applied = []
    for rx, rep in _CONVERSION_SUBSTITUTIONS:
        new, n = rx.subn(rep, conv)
        if n:
            applied.append(rx.pattern)
            conv = new
    if len(applied) < len(_CONVERSION_SUBSTITUTIONS):
        conv = conv + _CONVERSION_OVERRIDE
        applied.append("override_appended")
    return R0_TEMPLATE.format(seed_bullets=bullets, conversion=conv, story_type=story_type), applied


def build_revise_prompt(body: str) -> str:
    return REVISE_USER_TMPL.format(body=body.strip())


def std_developer() -> str:
    import er003_v1_n3_01_standard_a2_generate as sa2     # X共有ブロック(import only)
    return sa2.STANDARD_A2_DEVELOPER


def build_std_prompt(adv_text: str) -> str:
    import er003_v1_n3_01_standard_a2_generate as sa2     # X共有ブロック(import only)
    title, body = st.split_title_body(adv_text)
    paras = st.clean_body_paragraphs(body)
    n_words = sum(st.para_word_counts(paras))
    target = int(round(n_words * 0.95))
    lo = max(STD_WORD_RANGE[0], int(n_words * STD_ADV_RATIO_RANGE[0]))
    hi = min(STD_WORD_RANGE[1], int(n_words * STD_ADV_RATIO_RANGE[1]))
    tail = STD_PROMPT_TAIL.format(n_paragraphs=len(paras), target_words=target, lo_words=lo, hi_words=hi,
                                  advanced_story=adv_text.strip())
    return STD_PROMPT_HEAD + sa2.STANDARD_A2_NEW_VOCAB_BLOCK + tail


# ------------------------------------------------------------
# Guardrail(WARN/FAIL)
# ------------------------------------------------------------
def check_adv_guardrails(text: str, forbidden_names=None) -> dict:
    forbidden = forbidden_names or st.STORY_LINT_CONFIG["melos"]["forbidden_names"][:4]
    wc = st.body_word_count(text)
    title, body = st.split_title_body(text)
    warns, fails = [], []
    if not (ADV_WORD_RANGE[0] <= wc <= ADV_WORD_RANGE[1]):
        warns.append(f"ADV_WORDS_OUT_OF_RANGE:{wc} (Guardrail {ADV_WORD_RANGE}, OPEN-302未承認)")
    if title is None:
        warns.append("ADV_NO_TITLE_LINE")
    low = text.lower()
    for nm in forbidden:
        if nm.lower() in low:
            fails.append(f"NAME_RULE_VIOLATION:{nm}")
    return {"word_count": wc, "warnings": warns, "failures": fails}


def check_std_guardrails(std_text: str, adv_text: str) -> dict:
    _t, sbody = st.split_title_body(std_text)
    _a, abody = st.split_title_body(adv_text)
    sp, ap = st.clean_body_paragraphs(sbody), st.clean_body_paragraphs(abody)
    swc, awc = sum(st.para_word_counts(sp)), sum(st.para_word_counts(ap))
    ratio = swc / awc if awc else 0.0
    ident = st.identical_sentence_ratio(sp, ap)
    s_len, a_len = st.avg_sentence_len(sp), st.avg_sentence_len(ap)
    warns, fails = [], []
    if not (STD_WORD_RANGE[0] <= swc <= STD_WORD_RANGE[1]):
        warns.append(f"STD_WORDS_OUT_OF_RANGE:{swc} (Guardrail {STD_WORD_RANGE}, OPEN-302未承認)")
    if not (STD_ADV_RATIO_RANGE[0] <= ratio <= STD_ADV_RATIO_RANGE[1]):
        warns.append(f"STD_ADV_RATIO_OUT_OF_RANGE:{ratio:.3f} (Guardrail {STD_ADV_RATIO_RANGE})")
    if a_len and s_len > a_len * STD_AVG_SENT_FACTOR:
        warns.append(f"STD_AVG_SENT_LEN_NOT_SHORTER:{s_len:.2f} vs adv {a_len:.2f}x{STD_AVG_SENT_FACTOR} (soft gate)")
    match = len(sp) == len(ap)
    if not match:
        warns.append(f"STD_ADV_PARAGRAPH_COUNT_MISMATCH:{len(sp)} vs {len(ap)} (独自分割に回る)")
    if ident >= STD_IDENTICAL_FAIL:
        fails.append(f"STD_SAME_AS_ADV:identical_sentence_ratio={ident:.3f}>={STD_IDENTICAL_FAIL}")
    if _t is None:
        fails.append("STD_NO_TITLE_LINE")
    return {"std_words": swc, "adv_words": awc, "ratio": round(ratio, 4), "identical_sentence_ratio": round(ident, 4),
            "avg_sentence_len_std": round(s_len, 2), "avg_sentence_len_adv": round(a_len, 2),
            "paragraph_count_std": len(sp), "paragraph_count_adv": len(ap), "std_adv_paragraph_count_match": match,
            "warnings": warns, "failures": fails}


# ------------------------------------------------------------
# 来歴(provenance)とstage管理
# ------------------------------------------------------------
class Provenance:
    def __init__(self, path: str, story_key: str, seed_sha: str):
        self.path = path
        if os.path.exists(path):
            self.data = rj(path)
            if self.data.get("seed_sha256") != seed_sha:
                raise FamilyZProvenanceMismatchStop(
                    f"seed_sha256不一致: provenance={self.data.get('seed_sha256')} 現在={seed_sha}")
        else:
            self.data = {"story_key": story_key, "seed_sha256": seed_sha, "chain": [], "downstream_stale": [],
                         "downstream_stages": {}, "regenerations": [], "audio_text_deviations": [],
                         "reference_only": {}}

    def chain_entry(self, stage):
        for e in self.data["chain"]:
            if e["stage"] == stage:
                return e
        return None

    def stage_entry(self, name):
        return self.chain_entry(name) if name in CHAIN_STAGES else self.data["downstream_stages"].get(name)

    def set_entry(self, name, entry):
        if name in CHAIN_STAGES:
            old = self.chain_entry(name)
            if old is not None:
                self.data["regenerations"].append({"stage": name, "replaced_at": _now(), "old": old})
                self.data["chain"] = [e for e in self.data["chain"] if e["stage"] != name]
            self.data["chain"].append(entry)
            self.data["chain"].sort(key=lambda e: CHAIN_STAGES.index(e["stage"]))
        else:
            if name in self.data["downstream_stages"]:
                self.data["regenerations"].append({"stage": name, "replaced_at": _now(),
                                                   "old": self.data["downstream_stages"][name]})
            self.data["downstream_stages"][name] = entry
        if name in self.data["downstream_stale"]:
            self.data["downstream_stale"].remove(name)

    def mark_stale_descendants(self, name):
        seen, todo = [], list(DEPENDENTS.get(name, []))
        while todo:
            n = todo.pop(0)
            if n not in seen:
                seen.append(n)
                todo.extend(DEPENDENTS.get(n, []))
        for n in seen:
            if self.stage_entry(n) is not None and n not in self.data["downstream_stale"]:
                self.data["downstream_stale"].append(n)

    def save(self):
        r2, sd = self.chain_entry("r2"), self.chain_entry("std_adjust")
        if r2:
            self.data["adv_final_sha256"] = r2["output_sha256"]
        if sd:
            self.data["std_sha256"] = sd["output_sha256"]
        wj(self.path, self.data)


def _now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def ensure_stage(prov: Provenance, name: str, input_sha: str, out_path: str, runner, *, regenerate: bool = False) -> dict:
    """resume/regenerate制御の中核。
    - 出力+entryがあり input_sha/output_shaが一致 -> 再利用(reused)。
    - entryはあるが親sha(input_sha)不一致 / 出力sha不一致 / 出力があるのにentryが無い -> STOP。
    - stale指定のstageは、明示 regenerate でない限りSTOP。
    - regenerate=True -> runner実行・置換・子孫をstale化。
    runner() -> (output_text, entry_fields dict)。戻り値: {"status": "reused"|"generated", "entry": entry, "path": out_path}"""
    entry = prov.stage_entry(name)
    exists = os.path.exists(out_path)
    if name in prov.data["downstream_stale"] and not regenerate:
        raise FamilyZProvenanceMismatchStop(
            f"{name}はstale(親の再生成後)。明示 --regenerate-stage {name} が必要(自動再生成しない)")
    if not regenerate:
        if exists and entry is None:
            raise FamilyZProvenanceMismatchStop(f"{out_path} が存在するが来歴entryが無い({name})。STOP")
        if exists and entry is not None:
            if entry["input_sha256"] != input_sha:
                raise FamilyZProvenanceMismatchStop(
                    f"{name}: 親sha不一致 entry.input={entry['input_sha256'][:12]} 現在={input_sha[:12]}")
            if file_sha(out_path) != entry["output_sha256"]:
                raise FamilyZProvenanceMismatchStop(
                    f"{name}: 出力ファイルsha不一致(固定された本文が変更された) {out_path}")
            return {"status": "reused", "entry": entry, "path": out_path}
    text, fields = runner()
    entry = {"stage": name, "input_sha256": input_sha, "output_sha256": sha(text), "generated_at": _now(), **fields}
    wt(out_path, text)
    prov.set_entry(name, entry)
    if regenerate:
        prov.mark_stale_descendants(name)
    prov.save()
    return {"status": "generated", "entry": entry, "path": out_path}


def _chain_fields(stage, prompt_sha, res: dict, extra=None) -> dict:
    m = res["meta"]
    d = {"routing_key": STAGE_KEY[stage], "requested_model": m["requested_model"],
         "actual_model_id": m["actual_model_id"], "effort": m["effort"], "response_id": m["response_id"],
         "attempts": res["attempts"], "cost_jpy": m["cost_jpy"], "prompt_sha256": prompt_sha,
         "input_tokens": m["input_tokens"], "output_tokens": m["output_tokens"],
         "reasoning_tokens": m["reasoning_tokens"]}
    d.update(extra or {})
    return d


def run_writer_chain(llm: LLM, out_dir: str, seed_dir: str, *, stages=("r0", "r1", "r2"),
                     regenerate_stage: str | None = None, story_key: str = "melos") -> dict:
    """Sol R0->R1->R2(+std_adjust)。stagesで実行対象を限定。出力は <out_dir>/writer/。"""
    wdir = f"{out_dir}/writer"
    seed_path = f"{seed_dir}/seed.json"
    seed_sha = file_sha(seed_path)
    pinfo = rj(f"{seed_dir}/SEED_PROVENANCE.json")
    if pinfo["files"]["seed.json"]["sha256"] != seed_sha:
        raise FamilyZProvenanceMismatchStop("seed.json shaがSEED_PROVENANCE.jsonと不一致(Seed凍結違反)")
    seed = rj(seed_path)
    prov = Provenance(f"{wdir}/provenance.json", story_key, seed_sha)
    results = {}
    prev_sha, prev_text = seed_sha, None
    for stage in CHAIN_STAGES:
        if stage not in stages:
            # 実行対象外でも親shaを後続に引き継ぐため、既存出力があれば読む
            e = prov.chain_entry(stage)
            if e and os.path.exists(f"{wdir}/{STAGE_FILE[stage]}"):
                prev_sha, prev_text = e["output_sha256"], rd(f"{wdir}/{STAGE_FILE[stage]}")
            continue
        regen = regenerate_stage == stage
        if stage != "r0":
            parent = CHAIN_STAGES[CHAIN_STAGES.index(stage) - 1] if stage != "std_adjust" else "r2"
            pe = prov.chain_entry(parent)
            pf = f"{wdir}/{STAGE_FILE[parent]}"
            if pe is None or not os.path.exists(pf):
                raise FamilyZProvenanceMismatchStop(f"{stage}の親{parent}が未生成")
            if file_sha(pf) != pe["output_sha256"]:
                raise FamilyZProvenanceMismatchStop(f"親{parent}の本文sha不一致(固定本文が変更された)")
            if parent in prov.data["downstream_stale"]:
                raise FamilyZProvenanceMismatchStop(f"親{parent}がstale")
            prev_sha, prev_text = pe["output_sha256"], rd(pf)
        out_path = f"{wdir}/{STAGE_FILE[stage]}"
        if stage == "r0":
            prompt, applied = build_r0_prompt(seed)
            dev, user = WRITER_DEVELOPER_MESSAGE, prompt
            extra = {"conversion_substitutions": applied}
        elif stage in ("r1", "r2"):
            dev, user, extra = None, build_revise_prompt(prev_text), {}
        else:
            dev, user, extra = std_developer(), build_std_prompt(prev_text), {}
        prompt_sha = sha((dev or "") + "\n\n---\n\n" + user)
        wt(f"{wdir}/{stage}_prompt.txt", (dev + "\n\n---\n\n" if dev else "") + user)

        def runner(stage=stage, dev=dev, user=user, prompt_sha=prompt_sha, extra=extra):
            res = llm.call(STAGE_KEY[stage], f"z_{stage}", user, developer=dev, effort=WRITER_EFFORT)
            text = res["text"].strip() + "\n"
            fields = _chain_fields(stage, prompt_sha, res, extra)
            if stage == "std_adjust":
                if not re.match(r"^\s*#\s+\S", text):
                    raise FamilyZStop("[STOP] Std調整出力が『# 』Title行で始まらない(明示 --regenerate-stage std_adjust で再生成)")
            return text, fields

        r = ensure_stage(prov, stage, prev_sha, out_path, runner, regenerate=regen)
        text = rd(out_path)
        if stage == "std_adjust":
            g = check_std_guardrails(text, prev_text)
        else:
            g = check_adv_guardrails(text) if stage == "r2" else {"word_count": st.body_word_count(text)}
        r["guardrails"] = g
        e = prov.chain_entry(stage)
        e["guardrails"] = g
        prov.save()
        results[stage] = r
        if g.get("failures"):
            raise FamilyZStop(f"[STOP] {stage} guardrail FAIL: {g['failures']}(明示 --regenerate-stage {stage} のみ再生成)")
        prev_sha, prev_text = e["output_sha256"], text
    return {"provenance": prov.data, "stages": results}


# ------------------------------------------------------------
# Story 3分割(決定論候補列挙 -> LLM選択)
# ------------------------------------------------------------
def build_split_prompt(paragraphs, cands) -> str:
    wcs = st.para_word_counts(paragraphs)
    ranges = st.candidates_as_ranges(cands)
    options = "\n".join(
        f"b1={b1}: b2 in " + ", ".join(f"{a}..{b}" if a != b else f"{a}" for a, b in runs)
        for b1, runs in sorted(ranges.items()))
    numbered = "\n\n".join(f"[{i}] ({wcs[i]} words) {p}" for i, p in enumerate(paragraphs))
    return SPLIT_USER_TMPL.format(options=options, numbered_story=numbered)


def select_split(llm: LLM, paragraphs, *, label="z_split") -> dict:
    """決定論で全列挙した候補から、LLM(FAMILY_Z_STORY_SPLIT)が1ペアを選ぶ。候補外は1回再提案->STOP。
    候補が空ならSTOP(固定語数フォールバックしない)。"""
    wcs = st.para_word_counts(paragraphs)
    cands = st.enumerate_split_candidates(wcs)
    if not cands:
        raise FamilyZSplitStop("SPLIT_NO_CANDIDATES: 各Part20〜45%を満たす段落境界ペアが無い"
                                   "(固定語数フォールバックしない=STOP)")
    base = build_split_prompt(paragraphs, cands)
    user, attempts, calls = base, [], []
    for n in (1, 2):
        res = llm.call("FAMILY_Z_STORY_SPLIT", f"{label}_{n}", user, developer=SPLIT_DEVELOPER,
                       effort=SPLIT_EFFORT, schema=SPLIT_SCHEMA)
        calls.append(res["meta"])
        try:
            obj = json.loads(res["text"])
            pair = (obj["part2_starts_at_paragraph"], obj["part3_starts_at_paragraph"])
        except Exception as e:  # noqa: BLE001
            obj, pair = None, None
            ok, why = False, f"JSON:{e}"
        else:
            ok, why = st.validate_split_choice(pair, cands)
        attempts.append({"attempt": n, "answer": pair, "ok": ok, "why": why})
        if ok:
            return {"boundaries": [int(pair[0]), int(pair[1])], "reason_ja": obj["reason_ja"],
                    "candidates": [list(c) for c in cands], "attempts": attempts, "calls": calls,
                    "split_model_id": calls[-1]["actual_model_id"], "prompt_sha256": sha(base)}
        user = base + SPLIT_RETRY_TMPL.format(prev=pair, why=why)
    raise FamilyZSplitStop(f"SPLIT_CHOICE_OUT_OF_CANDIDATES(再提案後も候補外): attempts={attempts}")


# ------------------------------------------------------------
# Dialogue話者判定
# ------------------------------------------------------------
def tag_story_with_quotes(paragraphs, quotes) -> str:
    by_p = {}
    for q in quotes:
        by_p.setdefault(q["paragraph_index"], []).append(q)
    out = []
    for i, para in enumerate(paragraphs):
        pos, buf = 0, []
        for q in by_p.get(i, []):
            buf.append(para[pos:q["start"]])
            buf.append(f"[[Q:{q['quote_id']}]]")
            pos = q["start"]
        buf.append(para[pos:])
        out.append("".join(buf))
    return "\n\n".join(out)


def llm_attribute_quotes(llm: LLM, paragraphs, quotes, *, label="z_dialogue_attr") -> dict:
    """全引用を1callでLLM判定。{quote_id: speaker}とmeta。形式不正は1回retry、なお不正は返してreconcileに任せる。"""
    if not quotes:
        return {"llm": {}, "calls": [], "prompt_sha256": ""}
    user = ATTR_USER_TMPL.format(tagged_story=tag_story_with_quotes(paragraphs, quotes))
    calls, mapping = [], {}
    for n in (1, 2):
        res = llm.call("FAMILY_Z_DIALOGUE_ATTRIBUTION", f"{label}_{n}", user, developer=ATTR_DEVELOPER,
                       effort=ATTRIBUTION_EFFORT, schema=ATTR_SCHEMA)
        calls.append(res["meta"])
        try:
            arr = json.loads(res["text"])["attributions"]
            mapping = {a["quote_id"]: a["speaker"] for a in arr}
            bases = {a["quote_id"]: a.get("basis", "") for a in arr}
        except Exception:  # noqa: BLE001
            mapping, bases = {}, {}
        if set(mapping) == {q["quote_id"] for q in quotes}:
            return {"llm": mapping, "bases": bases, "calls": calls, "prompt_sha256": sha(user)}
    return {"llm": mapping, "bases": {}, "calls": calls, "prompt_sha256": sha(user)}


def attribute_dialogue(llm: LLM, paragraphs, *, voice_keywords=None, label="z_dialogue_attr",
                       raise_on_mismatch=True) -> dict:
    quotes = st.extract_quotes(paragraphs)
    det = st.deterministic_attribution(paragraphs, quotes, voice_keywords)
    la = llm_attribute_quotes(llm, paragraphs, quotes, label=label)
    rec = st.reconcile_attribution(paragraphs, quotes, det, la["llm"])
    for row in rec["rows"]:
        row["basis"] = la.get("bases", {}).get(row["quote_id"], "")
    rec["calls"] = la["calls"]
    rec["prompt_sha256"] = la["prompt_sha256"]
    rec["quotes"] = quotes
    if raise_on_mismatch and not rec["ok"]:
        raise FamilyZDialogueMismatchStop(
            f"DIALOGUE_ATTRIBUTION_MISMATCH: mismatches={[r['quote_id'] for r in rec['mismatches']]} "
            f"problems={rec['problems']}(dialogue_override.jsonに記録、自動採用しない)")
    return rec


# ------------------------------------------------------------
# plan(分割+話者+clip計画)
# ------------------------------------------------------------
def apply_human_confirmed_override(att: dict, out_dir: str, level: str) -> dict:
    """人間(PM)が確定したmismatch解決を適用する(委任_07)。決定論/LLM判定ロジックは変更しない。
    {out_dir}/dialogue_override.json の "human_confirmed"[level][quote_id] = {"speaker","text",...} を読み、
    status==mismatch かつ quote_id・引用textが完全一致する行だけ final に採用する(status=human_override)。
    problems(欠落/不正speaker)は解消しない。適用外のmismatchが残れば ok=False のまま(STOP)。"""
    path = f"{out_dir}/dialogue_override.json"
    if att.get("ok") or not os.path.exists(path):
        return att
    conf = (rj(path).get("human_confirmed") or {}).get(level) or {}
    if not conf or att.get("problems"):
        return att
    remaining, applied = [], []
    for row in att["rows"]:
        c = conf.get(row["quote_id"])
        if row["status"] == "mismatch" and c and c.get("text") == row["text"] and c.get("speaker") in st.SPEAKERS:
            row["status"] = "human_override"
            row["human_speaker"] = c["speaker"]
            att["final"][row["quote_id"]] = c["speaker"]
            applied.append(row["quote_id"])
        elif row["status"] == "mismatch":
            remaining.append(row)
    att["mismatches"] = remaining
    att["human_overrides_applied"] = applied
    att["ok"] = not remaining and not att["problems"] and len(att["final"]) == len(att["rows"])
    return att


def run_plan(llm: LLM, level: str, text: str, out_dir: str, slug: str, run: str, *, adv_plan: dict | None = None,
             story_key: str = "melos") -> dict:
    """segment_plan_{level}.json 相当dictを返す(書き込みは呼出側)。
    a2でadv_planがあり、段落数が一致しAdvの境界を写像してもPart比が20-45%内ならそれを使う(整列)。
    そうでなければ独自分割(理由を記録)。"""
    title, body = st.split_title_body(text)
    paras = st.clean_body_paragraphs(body)
    wcs = st.para_word_counts(paras)
    cands = st.enumerate_split_candidates(wcs)
    split_info, origin, note = None, "llm_select", None
    if adv_plan is not None and level == "a2":
        if adv_plan.get("paragraph_count") == len(paras):
            b = adv_plan["boundaries"]
            if tuple(b) in set(cands):
                split_info = {"boundaries": list(b), "reason_ja": adv_plan.get("split_reason_ja", "") + "(Advの境界を段落整列で写像)",
                              "candidates": [list(c) for c in cands], "attempts": [], "calls": [],
                              "split_model_id": adv_plan.get("split_model_id", ""), "prompt_sha256": ""}
                origin = "mapped_from_advanced"
            else:
                note = "Adv境界の写像がStdのPart比20-45%を満たさないため独自分割"
        else:
            note = f"段落数不一致(std={len(paras)}, adv={adv_plan.get('paragraph_count')})のため独自分割"
    if split_info is None:
        split_info = select_split(llm, paras, label=f"z_split_{level}")
    b1, b2 = split_info["boundaries"]
    att = attribute_dialogue(llm, paras, label=f"z_dialogue_attr_{level}", raise_on_mismatch=False)
    att = apply_human_confirmed_override(att, out_dir, level)
    wj(f"{out_dir}/dialogue_attribution_{level}.json", {k: v for k, v in att.items() if k != "quotes"})
    if not att["ok"]:
        _ovp = f"{out_dir}/dialogue_override.json"
        _prev_conf = (rj(_ovp).get("human_confirmed") if os.path.exists(_ovp) else None)
        _rec = {"level": level, "mismatches": att["mismatches"], "problems": att["problems"],
                "note": "人間判断が必要。自動採用しない"}
        if _prev_conf:
            _rec["human_confirmed"] = _prev_conf   # 既存の人間確定を消さない
        wj(_ovp, _rec)
        raise FamilyZDialogueMismatchStop(
            f"DIALOGUE_ATTRIBUTION_MISMATCH({level}): {[r['quote_id'] for r in att['mismatches']]} "
            f"problems={att['problems']}(dialogue_override.json)")
    narration_dir = f"{RUN_ROOT}/{slug}/{run}/{LEVEL_DIR[level]}/narration"
    clips = st.plan_clips(paras, att["final"], b1, b2, level, narration_dir)
    plan = {
        "story_key": story_key, "level": level, "split_method": "deterministic_candidates_llm_select",
        "split_origin": origin, "split_note": note,
        "candidate_boundaries": split_info["candidates"], "boundaries": [b1, b2],
        "split_reason_ja": split_info["reason_ja"], "split_model_id": split_info["split_model_id"],
        "paragraph_count": len(paras), "title": title,
        "parts": st.part_stats(wcs, b1, b2), "clips": clips,
        "std_adv_paragraph_count_match": (adv_plan.get("paragraph_count") == len(paras)) if adv_plan else None,
        "comment_after_segment_id": st.comment_after_segment_ids(clips),
        "source_text_sha256": sha(text),
        "dialogue_summary": {"quotes": len(att["rows"]),
                             "agree": sum(1 for r in att["rows"] if r["status"] == "agree"),
                             "llm_only": sum(1 for r in att["rows"] if r["status"] == "llm_only")},
        "llm_calls": split_info["calls"] + att["calls"],
    }
    for p in plan["parts"]:
        lo, hi = st.PART_RATIO_RANGE
        if not (lo - 1e-9 <= p["ratio"] <= hi + 1e-9):
            raise FamilyZPlanStop(f"PART_RATIO_OUT_OF_RANGE: {p}")
    return plan


# ------------------------------------------------------------
# Preview / Comment / lint
# ------------------------------------------------------------
def generate_with_lint(gen, lint, retries: int = 1) -> tuple:
    """gen(attempt_index)->text。lint(text)->違反list。NGならretry(既定1回)、なおNGならFamilyZLintStop。"""
    attempts = []
    for i in range(retries + 1):
        text = (gen(i) or "").strip()
        v = lint(text)
        attempts.append({"attempt": i + 1, "text": text, "violations": v})
        if not v:
            return text, attempts
    raise FamilyZLintStop(f"SUPPORT_LINT_FAILED(retry {retries}回後もNG): {attempts}")


COMMENT3_FACT_RATIO = 0.40     # Fable判断(委任_08): Comment3のcontent_factsはPart3の前半(先頭約40%、最低2段落)に限定
COMMENT3_FACT_MIN_PARAGRAPHS = 2


def limit_comment3_part(part3_text: str) -> str:
    """Comment3(Part3紹介)へ渡す事実をPart3前半の段落に限定する(結末ネタバレ防止)。段落数が少なければ全段落。"""
    paras = [p for p in part3_text.split("\n\n") if p.strip()]
    k = max(COMMENT3_FACT_MIN_PARAGRAPHS, int(round(len(paras) * COMMENT3_FACT_RATIO)))
    return "\n\n".join(paras[:min(k, len(paras))])


def _support_text(fn, client, role, context, model):
    r = fn(client, role, context, model=model)
    if r.get("status") != "OK":
        raise FamilyZStop(f"SUPPORT_GENERATION_FAILED: {r.get('status')}")
    return r["text"]


def run_support_std(client, parts: dict, full_text: str, *, ja_support_fn=None, story_key="melos", prior: dict = None) -> dict:
    """Std: JA Preview + JA Comment1〜3(実LLM呼出。E2Eで実施。本委任ではmockのみ)。
    Comment n は「これから聞くPart n」に実在する事実のみ(content_facts)。lint NG -> retry1 -> STOP。"""
    import er003_v1_iran01_a2_generate as a2gen
    import er013_family_c_production_01 as fam_c
    fn = ja_support_fn or a2gen.run_support_text
    model = routing.require_model("A2_SUPPORT", routing.SUPPORT_MODEL)
    lint = lambda t: st.lint_support_text(t, "ja", story_key)  # noqa: E731
    out = {"comments": {}, "attempts": {}}
    transitions = {1: "", 2: "ここまでの場面を聞き終えたところで、物語の続きに入ります。",
                   3: "さらに物語が進み、次の場面に入ります。"}
    for n in (1, 2, 3):
        if prior and n in (1, 2):      # 再生成時はComment1/2を再利用(Comment3のみ再生成)
            out["comments"][str(n)] = prior["comments"][str(n)]
            out["attempts"][f"comment_{n}"] = prior["attempts"][f"comment_{n}"]
            continue
        content_facts = ("これから聞く英文(下の【これから聞く部分】)に実際に書かれている事実のみ。場所・状況、人物関係、"
                         "場面の変化、次の行動、選択や対立点のうち必要なもの。【これから聞く部分】に書かれていない事実・"
                         "人物・結末は使わない。")
        listen = limit_comment3_part(parts[n]) if n == 3 else parts[n]    # Comment3はPart3前半のみ
        art = f"【これから聞く部分】\n{listen}"
        if n > 1:
            art += f"\n\n【すでに聞いた部分(流れの参考のみ。ここの事実を再説明しない)】\n{parts[n - 1]}"

        def gen(i, n=n, art=art, content_facts=content_facts):
            res = fam_c.generate_family_c_a2_comment(
                client, n, art, content_facts, scene_transition=transitions[n],
                label_prefix=f"family_z_std_comment_try{i + 1}", model=model, run_support_text_fn=fn)
            return res["text"]

        text, att = generate_with_lint(gen, lint)
        out["comments"][str(n)] = text
        out["attempts"][f"comment_{n}"] = att
    import er026_family_z_fiction_production_runner_01 as er026   # Z既存Previewのrole(lazy: 循環import回避)
    role = er026.build_family_z_preview_prompt() + (
        f"\n\n【重複回避】直前に流れるComment 1は次の通りです。これと内容が重複しないようにしてください。\n{out['comments']['1']}")
    ctx = f"【物語全文(参考、新しい設定・事実の追加禁止)】\n{full_text}"

    def gen_p(i):
        return _support_text(fn, client, role, ctx, model)

    if prior and prior.get("preview"):
        out["preview"], out["attempts"]["preview"] = prior["preview"], prior["attempts"]["preview"]
        return out
    text, att = generate_with_lint(gen_p, lint)
    out["preview"], out["attempts"]["preview"] = text, att
    return out


def run_support_adv(client, parts: dict, full_text: str, *, en_support_fn=None, story_key="melos", prior: dict = None) -> dict:
    """Adv: EN Preview + EN Comment1〜3。X B1のCOMMENT_1_ROLE/COMMENT_2_ROLE/PREVIEW_ROLEを無改変で再利用
    (Comment2とComment3は同じCOMMENT_2_ROLE。Comment4・COMMENT_3_ROLE[Point橋渡し]は呼ばない)。"""
    import er003_v1_b1_scaffold_01_generate as b1s
    fn = en_support_fn or b1s.run_support_text
    model = routing.require_model("B1_SUPPORT", routing.SUPPORT_MODEL)
    lint = lambda t: st.lint_support_text(t, "en", story_key)  # noqa: E731
    out = {"comments": {}, "attempts": {}}
    ctxs = {
        1: f"【本文(これから聞く部分)】\n{parts[1]}\n\n{NOT_NEWS_NOTE}",
        2: f"【すでに聞いた本文(前半)】\n{parts[1]}\n\n【これから聞く本文(後半)】\n{parts[2]}\n\n{NOT_NEWS_NOTE}",
        3: f"【すでに聞いた本文(前半)】\n{parts[1]}\n\n{parts[2]}\n\n【これから聞く本文(後半)】\n{limit_comment3_part(parts[3])}\n\n{NOT_NEWS_NOTE}",
    }
    roles = {1: b1s.COMMENT_1_ROLE, 2: b1s.COMMENT_2_ROLE, 3: b1s.COMMENT_2_ROLE}
    for n in (1, 2, 3):
        if prior and n in (1, 2):
            out["comments"][str(n)] = prior["comments"][str(n)]
            out["attempts"][f"comment_{n}"] = prior["attempts"][f"comment_{n}"]
            continue

        def gen(i, n=n):
            return _support_text(fn, client, roles[n], ctxs[n], model)
        text, att = generate_with_lint(gen, lint)
        out["comments"][str(n)] = text
        out["attempts"][f"comment_{n}"] = att
    if prior and prior.get("preview"):
        out["preview"], out["attempts"]["preview"] = prior["preview"], prior["attempts"]["preview"]
        return out
    prole = b1s.PREVIEW_ROLE.format(comment_1=out["comments"]["1"], comment_2=out["comments"]["2"])

    def gen_p(i):
        return _support_text(fn, client, prole, f"【本文】\n{full_text}\n\n{NOT_NEWS_NOTE}", model)

    text, att = generate_with_lint(gen_p, lint)
    out["preview"], out["attempts"]["preview"] = text, att
    return out


def run_kp_stage(level: str, text: str, out_dir: str, slug: str, *, kp_fn=None) -> dict:
    """Key Phrases: Strategy Lで両レベル別々に再選定(Std/Advで本文が異なる)。実呼出はE2Eで実施。"""
    import er003_v1_n3_01_scaffold_generate as scaffold
    fn = kp_fn or scaffold.run_key_phrases
    src_level, process = ("A2", "A2_SUPPORT") if level == "a2" else ("B1", "B1_SUPPORT")
    kp_dir = f"{out_dir}/key_phrases/{LEVEL_DIR[level]}"
    os.makedirs(kp_dir, exist_ok=True)
    res = fn(text, kp_dir, f"family_z_{slug}_{LEVEL_DIR[level]}", src_level, process=process)
    return res


def english_phrase_sharing_allowed(std_text: str, adv_text: str) -> bool:
    """KPの英語Phrase共通化は両レベルの本文が同一テキストのときのみ許可。"""
    return sha(std_text) == sha(adv_text)


# ------------------------------------------------------------
# Mock client(offline test / --mode mock)
# ------------------------------------------------------------
class _Resp:
    def __init__(self, text, model):
        self.output_text, self.id, self.model = text, "mock_resp", model
        self.usage = type("U", (), {"input_tokens": 1000, "output_tokens": 500, "input_tokens_details": None,
                                    "output_tokens_details": None})()


class MockResponses:
    def __init__(self, hook=None):
        self.hook, self.calls = hook, []

    def create(self, **kw):
        self.calls.append(kw)
        if self.hook:
            r = self.hook(kw)
            if r is not None:
                return _Resp(r, kw["model"])
        fmt = (kw.get("text") or {}).get("format", {})
        user = kw["input"][-1]["content"]
        if fmt.get("name") == "z_split_choice":
            m = re.search(r"b1=(\d+): b2 in (\d+)", user)
            return _Resp(json.dumps({"part2_starts_at_paragraph": int(m.group(1)),
                                     "part3_starts_at_paragraph": int(m.group(2)), "reason_ja": "mock理由"}), kw["model"])
        if fmt.get("name") == "z_dialogue_attribution":
            ids = re.findall(r"\[\[Q:(q\d+_\d+)\]\]", user)
            return _Resp(json.dumps({"attributions": [{"quote_id": i, "speaker": "melos", "basis": "mock"} for i in ids]}),
                         kw["model"])
        n, w = 8, "word"
        if "Rewrite this entire story for CEFR A2" in user:
            n, w = int(re.search(r"exactly (\d+) paragraphs", user).group(1)), "easy"
        paras = "\n\n".join(" ".join([w] * 55) for _ in range(n))
        return _Resp("# Mock Title\n\n" + paras, kw["model"])


class MockClient:
    def __init__(self, hook=None):
        self.responses = MockResponses(hook)


# ------------------------------------------------------------
# smoke(分割選択1回 + 話者判定1回 + lint。Writer鎖/Std調整/Preview/Comment/KPは呼ばない)
# ------------------------------------------------------------
SMOKE_LINT_SAMPLES = (
    ("ja", "羊飼いのメロスは、人を疑って処刑する王の前に立たされています。妹の結婚式が近く、気がかりです。", False),
    ("ja", "このニュースでは羊飼いが登場します。", True),
    ("ja", "ここがポイントです。聞いてみましょう。", True),
    ("ja", "メロスは最後に間に合います。", True),
    ("en", "A shepherd stands before a ruler who trusts no one. What will he do about his sister's wedding?", False),
    ("en", "In this news story, Part 2 begins and Point One is next. In One Line, he arrives just in time.", True),
)


def run_smoke(text_path: str, out_dir: str, client, budget: Budget) -> dict:
    text = rd(text_path)
    llm = LLM(client, budget)
    title, body = st.split_title_body(text)
    paras = st.clean_body_paragraphs(body)
    wcs = st.para_word_counts(paras)
    split = select_split(llm, paras, label="smoke_split")
    b1, b2 = split["boundaries"]
    att = attribute_dialogue(llm, paras, label="smoke_dialogue", raise_on_mismatch=False)
    plan = None
    if att["ok"]:
        clips = st.plan_clips(paras, att["final"], b1, b2, "b1b", "SMOKE/b1b/narration")
        plan = {"clip_count": len(clips), "comment_after_segment_id": st.comment_after_segment_ids(clips),
                "clips": [{k: c[k] for k in ("id", "part", "speaker", "voice_role", "word_count", "text")} for c in clips]}
    lint = [{"lang": lg, "text": t, "expected_ng": ng, "violations": st.lint_support_text(t, lg)}
            for lg, t, ng in SMOKE_LINT_SAMPLES]
    result = {
        "source_text": text_path, "source_sha256": sha(text), "title": title, "paragraph_count": len(paras),
        "word_count": sum(wcs), "candidate_count": len(split["candidates"]),
        "split": {"boundaries": [b1, b2], "reason_ja": split["reason_ja"], "split_model_id": split["split_model_id"],
                  "attempts": split["attempts"], "parts": st.part_stats(wcs, b1, b2)},
        "dialogue": {"ok": att["ok"], "rows": att["rows"], "mismatches": att["mismatches"], "problems": att["problems"],
                     "model_ids": sorted({c["actual_model_id"] for c in att["calls"]})},
        "plan": plan, "lint": lint,
        "lint_all_as_expected": all(bool(x["violations"]) == x["expected_ng"] for x in lint),
        "llm_calls": budget.calls, "spent_jpy": round(budget.spent, 4),
    }
    wj(f"{out_dir}/smoke_result.json", result)
    lines = ["# er062 smoke結果(Trial②R2テキスト、委任_04B)", "",
             f"- 分割境界: Part2は段落{b1}から、Part3は段落{b2}から / 理由: {split['reason_ja']}",
             "- Part: " + ", ".join(f"Part{p['part']}={p['word_count']}語({p['ratio']*100:.1f}%)" for p in result["split"]["parts"]),
             f"- 費用: {result['spent_jpy']}円 / model: {result['split']['split_model_id']}", "",
             "| quote_id | 引用 | 決定論 | LLM | 状態 |", "|---|---|---|---|---|"]
    for r in att["rows"]:
        lines.append(f"| {r['quote_id']} | {r['text'][:40]} | {r['deterministic']} | {r['llm']} | {r['status']} |")
    wt(f"{out_dir}/smoke_result.md", chr(10).join(lines) + chr(10))
    return result


def smoke_main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mode", choices=("mock", "real"), default="mock")
    ap.add_argument("--approved-budget-jpy", type=float, default=0.0)
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    if a.mode == "real":
        if a.approved_budget_jpy <= 0:
            sys.exit("STOP: real は --approved-budget-jpy(>0)必須")
        client, cl = _setup_real(a.out)
        ctx = cl.logging_context(THEME_TAG, "smoke")
        budget = Budget(a.approved_budget_jpy, DEFAULT_EST)
    else:
        client, ctx, budget = MockClient(_attr_mock_hook), contextlib.nullcontext(), Budget(1e9)
    with ctx:
        r = run_smoke(a.text, a.out, client, budget)
    print(json.dumps({"boundaries": r["split"]["boundaries"], "dialogue_ok": r["dialogue"]["ok"],
                      "lint_all_as_expected": r["lint_all_as_expected"], "spent_jpy": r["spent_jpy"]}, ensure_ascii=False))
    return 0


def _attr_mock_hook(kw):
    return None


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------
def out_dir_for(slug, run):
    return f"{RUN_ROOT}/{slug}/{run}"


def seed_dir_for(slug):
    return f"{RUN_ROOT}/{slug}/seed"


def level_text_path(out_dir, level):
    return f"{out_dir}/writer/{'r2.md' if level == 'b1b' else 'std.md'}"


def stage_plan(llm, out_dir, slug, run, level, prov, regenerate):
    text = rd(level_text_path(out_dir, level))
    adv_plan = None
    if level == "a2":
        ap = f"{out_dir}/segment_plan_b1b.json"
        if os.path.exists(ap):
            adv_plan = rj(ap)
    in_sha = sha(text + "\n##ADV_PLAN##" + (adv_plan["source_text_sha256"] + str(adv_plan["boundaries"]) if adv_plan else ""))
    path = f"{out_dir}/segment_plan_{level}.json"

    def runner():
        plan = run_plan(llm, level, text, out_dir, slug, run, adv_plan=adv_plan)
        return st.dumps(plan), {"routing_keys": ["FAMILY_Z_STORY_SPLIT", "FAMILY_Z_DIALOGUE_ATTRIBUTION"],
                                "cost_jpy": round(sum(c["cost_jpy"] for c in plan["llm_calls"]), 4)}

    return ensure_stage(prov, f"plan_{level}", in_sha, path, runner, regenerate=regenerate)


def _setup_real(out_dir):
    from dotenv import load_dotenv
    load_dotenv()
    import er005_cost_logger as cl
    import er003_v1_en_direct_vfl_01_generate as vfl01
    cl.install(os.path.join(out_dir, "raw_usage_log.jsonl"))
    return vfl01.get_client(), cl


def main(argv=None):
    ap = argparse.ArgumentParser(description="Family Z Writer/Std/分割/話者判定/Support (委任_04B)")
    ap.add_argument("--story", default="melos")
    ap.add_argument("--run", required=True)
    ap.add_argument("--stage", choices=("writer", "std_adjust", "plan", "support", "kp"), required=True)
    ap.add_argument("--level", choices=("a2", "b1b", "both"), default="both")
    ap.add_argument("--mode", choices=("dry-run", "mock", "real"), default="dry-run")
    ap.add_argument("--regenerate-stage", choices=ALL_STAGE_NAMES, default=None,
                    help="明示指定したstageだけ再生成(R2等は自動retryしない)")
    ap.add_argument("--approved-budget-jpy", type=float, default=0.0)
    a = ap.parse_args(argv)
    out_dir = out_dir_for(a.story, a.run)
    levels = ("b1b", "a2") if a.level == "both" else (a.level,)
    if a.mode == "dry-run":
        print(json.dumps({"dry_run": True, "story": a.story, "run": a.run, "stage": a.stage, "levels": list(levels),
                          "regenerate_stage": a.regenerate_stage, "out_dir": out_dir,
                          "note": "副作用なし(ファイル作成・API呼出なし)"}, ensure_ascii=False, indent=1))
        return 0
    if a.mode == "real" and a.approved_budget_jpy <= 0:
        sys.exit("STOP: real は --approved-budget-jpy(>0)必須")
    if a.mode == "mock":
        out_dir += "_mock"
        client, ctx = MockClient(), contextlib.nullcontext()
        budget = Budget(1e9)
    else:
        os.makedirs(out_dir, exist_ok=True)
        client, cl = _setup_real(out_dir)
        ctx = cl.logging_context(THEME_TAG, a.stage)
        budget = Budget(a.approved_budget_jpy, DEFAULT_EST)
    llm = LLM(client, budget)
    sdir = seed_dir_for(a.story)
    with ctx:
        if a.stage in ("writer", "std_adjust"):
            stages = ("r0", "r1", "r2") if a.stage == "writer" else ("std_adjust",)
            res = run_writer_chain(llm, out_dir, sdir, stages=stages, regenerate_stage=a.regenerate_stage,
                                   story_key=a.story)
            print(json.dumps({k: {"status": v["status"], "guardrails": v["guardrails"]} for k, v in res["stages"].items()},
                             ensure_ascii=False, indent=1))
        else:
            seed_sha = file_sha(f"{sdir}/seed.json")
            prov = Provenance(f"{out_dir}/writer/provenance.json", a.story, seed_sha)
            if a.stage == "plan":
                for lv in levels:
                    r = stage_plan(llm, out_dir, a.story, a.run, lv, prov, a.regenerate_stage == f"plan_{lv}")
                    print(lv, r["status"])
            else:
                for lv in levels:
                    text = rd(level_text_path(out_dir, lv))
                    if a.stage == "kp":
                        def runner(lv=lv, text=text):
                            kp = run_kp_stage(lv, text, out_dir, a.story,
                                              kp_fn=(lambda *x, **k: {"mock": True}) if a.mode == "mock" else None)
                            return st.dumps(kp), {}
                        r = ensure_stage(prov, f"kp_{lv}", sha(text), f"{out_dir}/key_phrases/{lv}_result.json", runner,
                                         regenerate=a.regenerate_stage == f"kp_{lv}")
                    else:
                        plan = rj(f"{out_dir}/segment_plan_{lv}.json")
                        _t, body = st.split_title_body(text)
                        paras = st.clean_body_paragraphs(body)
                        pt = st.part_texts(paras, *plan["boundaries"])

                        def runner(lv=lv, pt=pt, text=text):
                            fn = run_support_std if lv == "a2" else run_support_adv
                            return st.dumps(fn(client, pt, text)), {}
                        r = ensure_stage(prov, f"support_{lv}", sha(text + file_sha(f"{out_dir}/segment_plan_{lv}.json")),
                                         f"{out_dir}/support/{lv}_support.json", runner,
                                         regenerate=a.regenerate_stage == f"support_{lv}")
                    print(lv, r["status"])
    print(json.dumps({"spent_jpy": round(budget.spent, 4), "calls": len(budget.calls)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "smoke":
        sys.exit(smoke_main(sys.argv[2:]))
    sys.exit(main())
