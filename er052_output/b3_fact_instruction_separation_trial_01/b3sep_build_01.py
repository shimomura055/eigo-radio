# -*- coding: utf-8 -*-
"""B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX-TRIAL-01 Phase2 Trial module(DEV/Trial専用・Production不変更)。
決定論の Fact/制約 組立。LLM不使用。台帳(ledger.txt)の欄をそのまま使う。
  assemble_D(ledger_text, selected_ids, storyline, variant)   variant in {"Dmin","Dfull","Dtag"}
  assemble_Aprime(ledger_text, selected_ids, storyline, llm_brief)  A'腕: Factはlbrief(LLM)、制約は決定論
  compose_news_field(facts_text, constraints_text)            R0ニュース欄の唯一の連結関数(P-out)
"""
import re

LINK = re.compile(r"\s*\(\[[^\]]*\]\(https?://[^)]*\)\)|\s*\(https?://[^)]*\)")
HEAD = re.compile(r"^\[(VERIFIED|AMBIGUOUS[^\]]*)\]\s+([A-Za-z0-9_\-]+): (.*)$")
FLD = re.compile(r"^  (\w+): (.*)$")
# 指示・禁止調(Writer向け命令)の検出。E1の検出器・D-fullの欄振り分けの両方で使う(PREREGISTRATION_02 6節)。
IMP = re.compile(r"(ないこと|こと[。]?$|書かない|断定しない|付け加えない|補わない|混同しない|扱わない|分けて扱う|区別する|区別して|"
                 r"として扱う|言い換えない|一般化しない|帰属させない|結び付けない|同一視しない|しない[。]?$|とは書|と断定|"
                 r"位置付ける|してはならない|使わない|転用しない|比較はしない)")
AMB_QUALIFIER = "この点は確定していない。"          # R1: AMBIGUOUS Factの決定論の固定限定文
AMB_TAG_ORIGINAL = "[AMBIGUOUS - 断定禁止、曖昧さを保持すること] "   # Dtag変種(台帳タグ原文保持。Facts側に指示調が入るため比較用)
CONS_HEADING = "Writerへの注意(事実ではありません)："


def clean(s):
    return LINK.sub("", s or "").strip()


def parse_ledger(text):
    facts, order, cur = {}, [], None
    for ln in text.replace("\r\n", "\n").split("\n"):
        m = HEAD.match(ln)
        if m:
            cur = m.group(2)
            facts[cur] = {"tag": m.group(1), "ambiguous": m.group(1).startswith("AMBIGUOUS"), "claim": m.group(3)}
            order.append(cur)
            continue
        m = FLD.match(ln)
        if m and cur:
            facts[cur][m.group(1)] = m.group(2)
    return facts, order


def _strip_period(s):
    return clean(s).rstrip("。 ")


def _ordered(order, selected_ids, how):
    """並び順。既定 how='selected'=B3の選定順(selected_fact_ids順)。'ledger'=台帳順。"""
    if how == "ledger":
        return [f for f in order if f in set(selected_ids)]
    return [f for f in selected_ids if f in set(order)]


def compose_news_field(facts_text, constraints_text):
    """R0ニュース欄(=Writerが読む文字列)の唯一の組立。Facts部(注記済みでも可)+制約ブロック。制約が空ならFacts部のみ。"""
    if not constraints_text:
        return facts_text
    return facts_text.rstrip("\n") + "\n\n" + constraints_text.rstrip("\n") + "\n"


def build_constraints(items):
    """items = [(label, text), ...]。label は 'N' 付き表記済みの文頭(例 '事実2について')。ID・【】は使わない(R5)。"""
    if not items:
        return ""
    return CONS_HEADING + "\n" + "\n".join(f"- {lab}：{t}" for lab, t in items) + "\n"


def assemble_D(ledger_text, selected_ids, storyline, variant="Dmin", order_how="selected"):
    facts, order = parse_ledger(ledger_text)
    sel = _ordered(order, selected_ids, order_how)
    lines, cons, moved, amb_info = [], [], [], []
    for n, fid in enumerate(sel, 1):
        f = facts[fid]
        body = clean(f["claim"])
        if f["ambiguous"]:
            body = (AMB_TAG_ORIGINAL if variant == "Dtag" else "") + body + ("" if variant == "Dtag" else AMB_QUALIFIER)
            amb_info.append({"fact_id": fid, "n": n})
        if variant == "Dfull":
            parts = []
            for key, lab in (("scope", "範囲"), ("conditions", "条件")):
                v = _strip_period(f.get(key, ""))
                if not v:
                    continue
                if IMP.search(v):
                    cons.append((f"事実{n}の{lab}について", clean(f[key])))
                    moved.append({"fact_id": fid, "n": n, "field": key, "text": v})
                else:
                    parts.append(f"{lab}：{v}")
            if parts:
                body += "（" + "。".join(parts) + "）"
        lines.append(f"- {body}")
        if f.get("notes_for_writer"):
            cons.append((f"事実{n}について", clean(f["notes_for_writer"])))
        if f.get("ambiguity_note"):
            cons.append((f"事実{n}について", clean(f["ambiguity_note"])))
    facts_text = "\n".join(lines) + "\n"
    cons_text = build_constraints(cons)
    brief_md = "# Selected Fact Brief\n\n## Storyline\n" + storyline + "\n\n## Selected Facts\n" + facts_text
    return {"variant": variant, "ordered_ids": sel, "facts_text": facts_text, "constraints_text": cons_text,
            "news_field": compose_news_field(facts_text, cons_text), "brief_md": brief_md,
            "constraint_items": cons, "moved_to_constraints": moved, "ambiguous_facts": amb_info,
            "evidence": {"selected_storyline": storyline, "selected_fact_ids": sel, "selected_fact_brief_text": facts_text,
                         "writer_constraints_text": cons_text, "writer_news_field_text": compose_news_field(facts_text, cons_text)}}


def assemble_Aprime(ledger_text, selected_ids, storyline, llm_brief):
    """A'腕: Facts=LLM(Trialコピー版Prompt)の記述文。制約は決定論転記(【事実N】対応は取れないため文頭ラベル無し)。"""
    facts, order = parse_ledger(ledger_text)
    sel = _ordered(order, selected_ids, "selected")
    t = llm_brief
    if storyline and t.startswith(storyline):
        t = t[len(storyline):].lstrip("\n")
    t = t.strip("\n") + "\n"
    cons = []
    for fid in sel:
        f = facts[fid]
        if f.get("notes_for_writer"):
            cons.append(("注意", clean(f["notes_for_writer"])))
        if f.get("ambiguity_note"):
            cons.append(("注意", clean(f["ambiguity_note"])))
    cons_text = build_constraints(cons)
    brief_md = "# Selected Fact Brief\n\n## Storyline\n" + storyline + "\n\n## Selected Facts\n" + t
    return {"variant": "Aprime", "ordered_ids": sel, "facts_text": t, "constraints_text": cons_text,
            "news_field": compose_news_field(t, cons_text), "brief_md": brief_md, "constraint_items": cons,
            "moved_to_constraints": [], "ambiguous_facts": [{"fact_id": f} for f in sel if facts[f]["ambiguous"]],
            "evidence": {"selected_storyline": storyline, "selected_fact_ids": sel, "selected_fact_brief_text": t,
                         "writer_constraints_text": cons_text, "writer_news_field_text": compose_news_field(t, cons_text)}}
