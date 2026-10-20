# -*- coding: utf-8 -*-
"""FAMILY-X-WRITER-DETECTIVE-WORD-AVOIDANCE-TRIAL-01 harness lib (Trial専用/DEV path)。

Production Writer(er053 W-1 R0/R1/R2、er003 Advanced英訳/In One Line、er003 Standard A2)の
Prompt・コード・実行経路は変更しない。Trial script内で**process内のruntime monkeypatch**により、
本文proseを生成/改稿する全LLM工程のuser promptへ同一の追加指示(Pattern A/B/C)を挿入する。
実行後は finally で元の関数/定数へ必ず復元する(Production module定数の不変はtestで確認)。
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
TRIAL_ID = "FAMILY-X-WRITER-DETECTIVE-WORD-AVOIDANCE-TRIAL-01"
OUT_ROOT = os.path.join(ROOT, "er086_output", "writer_detective_avoidance_trial_01")
DOC_DIR = os.path.join(ROOT, "docs", "research", TRIAL_ID)
USER_MD = os.path.join(ROOT, "docs", "pm", "delegation_log", "2026-10-21_" + TRIAL_ID + "_USER.md")

# ユーザー原文§3のPattern文(byte単位でそのまま。改変禁止。testで原文ファイルと一致を機械確認)
PATTERN_TEXT = {
    "A": 'Do not use the word "detective" anywhere in the article.',
    "B": ('Do not use the word "detective" anywhere in the article. However, this restriction does not prohibit a '
          'mystery-like narrative structure or a detective-like progression of the news story, as long as it '
          'remains faithful to the verified facts.'),
    "C": ('Do not use the word "detective" anywhere in the article. Create an engaging news story through the actual '
          'events, surprising developments, decisions, consequences, and connections between verified facts. Avoid '
          'relying on a detective metaphor to make the story entertaining. A mystery-like narrative structure is '
          'acceptable when it naturally follows the facts.'),
}

# 注入対象工程(本文proseを生成/改稿する全LLM工程。Risk Flagger/IOL検査/記号Validator等の検査系は対象外)
INJECTED_STAGES = ["r0", "r1", "r2", "adv_translation", "adv_in_one_line", "standard"]


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def read_text(p):
    with open(p, encoding="utf-8", errors="replace", newline="") as f:
        return f.read()


def write_text(p, s):
    os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)


def write_json(p, o):
    write_text(p, json.dumps(o, ensure_ascii=False, indent=2))


def insert_before_marker(prompt: str, marker: str, addition: str) -> str:
    """marker(記事本文の直前の見出し)の直前に addition を挿入。markerが無ければ末尾に追記。"""
    i = prompt.find(marker)
    if i < 0:
        return prompt + "\n\n" + addition
    return prompt[:i] + "\n\n" + addition + prompt[i:]


class PromptDumper:
    def __init__(self, dump_dir: str, pattern: str):
        self.dir, self.pattern, self.counts, self.records = dump_dir, pattern, {}, []

    def dump(self, stage: str, text: str):
        n = self.counts.get(stage, 0) + 1
        self.counts[stage] = n
        name = f"{self.pattern}_{stage}" + ("" if n == 1 else f"_{n}") + ".txt"
        write_text(os.path.join(self.dir, name), text)
        self.records.append({"stage": stage, "file": name, "sha256": sha256_text(text), "chars": len(text),
                             "contains_pattern_text": PATTERN_TEXT.get(self.pattern, "\0") in text})


@contextlib.contextmanager
def injected(pattern: str, dumper: PromptDumper = None):
    """Pattern A/B/C を全対象工程へ挿入するcontext manager。exit時にProduction側を必ず復元する。"""
    import er003_v1_n3_01_advanced_adaptation_generate as adv_gen
    import er003_v1_n3_01_standard_a2_generate as std_gen
    import er053_family_x_factlock_ja_writer_01 as w1

    add = PATTERN_TEXT[pattern]
    orig = {
        "w1.build_r0_prompt": w1.build_r0_prompt,
        "w1.USER_TMPL": w1.USER_TMPL,
        "w1.call_luna_r0": w1.call_luna_r0,
        "w1.call_astra": w1.call_astra,
        "adv.build_translation": adv_gen.build_family_x_faithful_translation_prompt,
        "adv.build_iol": adv_gen.build_family_x_in_one_line_prompt,
        "std.build_prompt": std_gen.build_family_x_no_heading_prompt,
    }
    o_r0, o_luna, o_astra = orig["w1.build_r0_prompt"], orig["w1.call_luna_r0"], orig["w1.call_astra"]
    o_tr, o_iol, o_std = orig["adv.build_translation"], orig["adv.build_iol"], orig["std.build_prompt"]
    stage_tag_map = {"w1_r0": "r0", "w1_r0_symbol_regen": "r0_symbol_regen",
                     "w1_astra_r1": "r1", "w1_astra_r2": "r2", "w1_astra_r2_symbol_rerun": "r2_symbol_rerun"}

    def build_r0(storyline_line, brief_facts_text):
        return o_r0(storyline_line, brief_facts_text) + "\n\n" + add

    def call_luna(client, user, stage):
        if dumper:
            dumper.dump(stage_tag_map.get(stage, stage), user)
        return o_luna(client, user, stage)

    def call_astra(client, user, stage, retries=2):
        if dumper:
            dumper.dump(stage_tag_map.get(stage, stage), user)
        return o_astra(client, user, stage, retries)

    def build_tr(ja_article_text, must_fix=None):
        # 指示ブロック末尾(記事本文[Japanese article]の直前)へ挿入。must_fix(技術retry)は従来通り末尾。
        base = o_tr(ja_article_text, must_fix=None)
        p = insert_before_marker(base, "\n\n[Japanese article]\n", add)
        if must_fix:
            p += "\n\n" + adv_gen.build_must_fix_block(must_fix)
        if dumper:
            dumper.dump("adv_translation", p)
        return p

    def build_iol(title, body, *, ja_text=None, ledger_text=None, must_fix=None):
        base = o_iol(title, body, ja_text=ja_text, ledger_text=ledger_text, must_fix=None)
        p = insert_before_marker(base, "\n\n[Japanese source article]\n", add)
        if must_fix:
            p += "\n\n" + adv_gen.build_must_fix_block(must_fix)
        if dumper:
            dumper.dump("adv_in_one_line", p)
        return p

    def build_std(advanced_article, must_fix=None):
        base = o_std(advanced_article, must_fix=None)
        p = insert_before_marker(base, "\n\n[Article]\n", add)
        if must_fix:
            p += "\n\n" + std_gen.build_must_fix_block(must_fix)
        if dumper:
            dumper.dump("standard", p)   # er012はsha計算用にも本関数を呼ぶ(API呼出ではない)ため同名で連番になり得る
        return p

    w1.build_r0_prompt = build_r0
    w1.USER_TMPL = orig["w1.USER_TMPL"] + "\n\n" + add
    w1.call_luna_r0 = call_luna
    w1.call_astra = call_astra
    adv_gen.build_family_x_faithful_translation_prompt = build_tr
    adv_gen.build_family_x_in_one_line_prompt = build_iol
    std_gen.build_family_x_no_heading_prompt = build_std
    try:
        yield orig
    finally:
        w1.build_r0_prompt = orig["w1.build_r0_prompt"]
        w1.USER_TMPL = orig["w1.USER_TMPL"]
        w1.call_luna_r0 = orig["w1.call_luna_r0"]
        w1.call_astra = orig["w1.call_astra"]
        adv_gen.build_family_x_faithful_translation_prompt = orig["adv.build_translation"]
        adv_gen.build_family_x_in_one_line_prompt = orig["adv.build_iol"]
        std_gen.build_family_x_no_heading_prompt = orig["std.build_prompt"]


# ---- 決定論Grep ----
DET_RE = re.compile(r"detective", re.I)
DET_WORD_RE = re.compile(r"\bdetective\b", re.I)
DET_DERIV_RE = re.compile(r"detectives|detective[a-z]+", re.I)
JA_DET_RE = re.compile(r"探偵")
SIMILAR_RE = re.compile(
    r"\b(investigat\w*|clues?|mystery|mysteries|case file|sleuth\w*|whodunit|culprit|suspect\w*|inspector|magnifying glass)\b",
    re.I)
JA_SIMILAR_RE = re.compile(r"(捜査|推理|謎解き|手がかり|名探偵|虫眼鏡|真犯人|犯人|事件簿|調査)")


def count_detective(text: str) -> dict:
    return {"substring_ci": len(DET_RE.findall(text)), "word_ci": len(DET_WORD_RE.findall(text)),
            "derivatives_ci": len(DET_DERIV_RE.findall(text)), "ja_tantei": len(JA_DET_RE.findall(text))}


def context_snips(text: str, rx, width: int = 60) -> list:
    out = []
    for m in rx.finditer(text):
        s, e = max(0, m.start() - width), min(len(text), m.end() + width)
        out.append(text[s:e].replace("\n", " "))
    return out
