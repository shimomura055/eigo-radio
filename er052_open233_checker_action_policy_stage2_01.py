# -*- coding: utf-8 -*-
"""OPEN-233-CHECKER-ACTION-POLICY-STAGE2-01 委任_02: Trial専用の新規ロジック(全スイッチ既定OFF、Production未配線)。

A. ②読者信念テスト(`OPEN233_STAGE2_READER_BELIEF=1`): guard_target決定論付与 / Stage2 prompt追記(V7c) / belief schema /
   同一call内整合チェック(c) / 2nd opinion 2回目(文を見せずreader_beliefとLedgerのみ、O1) / 再利用禁止判定(e)。
B. ①構造要素Rewrite規則(`OPEN233_STRUCTURAL_REWRITE_RULES=1`): 構造要素の4照合(主体部分集合・極性・数値・形式)。
runnerの関数は遅延importで参照する(循環import回避)。設計: docs/pm/checker_action_policy_01/design_02.md。
"""
from __future__ import annotations

import copy
import json
import os
import re
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_stage2_hook_01 as s2h
import er052_open233_self_recovery_stage2_production_01 as s2p

SW_READER_BELIEF = "OPEN233_STAGE2_READER_BELIEF"
SW_STRUCT_RULES = "OPEN233_STRUCTURAL_REWRITE_RULES"
SW_SAVE_R3 = "OPEN233_SAVE_R3_SUPPORT_IDS"
RUBRIC_VERSION_ENV = "OPEN233_STAGE2_BELIEF_RUBRIC_VERSION"  # "v1"(既定)/"v2"(rubric調整1版目)

BELIEF_VALUES = ("contradicts", "unsupported_new_claim", "consistent", "unclear")
BELIEF_NA = "not_applicable"


def switch_on(name: str) -> bool:
    return os.environ.get(name, "0").strip() in ("1", "true", "True", "ON", "on")


# ----------------------------------------------------------------------------------------------
# A-(a) guard_target: 決定論(API無し)。型→重大度にはしない(Stage2に読者信念テストを必須にするだけ)。
# 規則=段階0-B危険文規則v0のNEG/UNIV/NUMのEN版 + Stage1 devフラグ(極性: changed_negation / 方向: changed_comparison /
# 主体: changed_actor / 数値: changed_number) + 主体の新規出現(Ledger・本文に無い固有名詞)。DIRWORD(方向語彙)は採用しない(設計§4-3)。
# ----------------------------------------------------------------------------------------------
UNIV_EN = re.compile(r"\b(all|every|everyone|everything|everybody|always|entire|whole|any|anyone|anything|no one|each|"
                     r"completely|totally|fully|nobody|nothing|never)\b", re.I)
_NUM_DIGIT = re.compile(r"\d")
_CAP_TOKEN = re.compile(r"(?<![A-Za-z0-9])([A-Z][A-Za-z0-9&\-]{1,})(?:[’']s)?(?![A-Za-z0-9])")
_ALLCAPS = re.compile(r"\b[A-Z]{2,}[A-Za-z0-9]*\b")
_PRONOUNS = frozenset({"i", "we", "you", "they", "he", "she", "me", "us", "them", "my", "our", "your", "their", "his", "her"})
_SENT_END = re.compile(r"(?<=[.!?])\s+")
_EN_COMMON_CAPS = frozenset(
    "the a an this that these those it he she they we i you but and so then however meanwhile in on at for as if when while because "
    "even also still now here there what why how one some many most all each every not nor no yet although though after before once "
    "soon today together monday tuesday wednesday thursday friday saturday sunday january february march april may june july august "
    "september october november december".split())


def _neg_a(text: str) -> bool:
    import er052_open233_stage1_coverage_checker_01 as cov
    return bool(cov._unit_neg_a(text or ""))


def proper_noun_vocab(ledger_text: str, article_text: str) -> set:
    """固有名詞語彙(小文字)。本文(`#`行除外)は文頭以外の大文字語+全大文字語、Ledger(JA主体)は全ての英大文字始まり語。"""
    vocab: set = set()
    for ln in (article_text or "").split("\n"):
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        for sent in _SENT_END.split(s):
            words = list(_CAP_TOKEN.finditer(sent))
            for k, m in enumerate(words):
                if m.start() == 0 or sent[:m.start()].strip(" \"'“‘(") == "":
                    continue
                vocab.add(m.group(1).lower())
        for m in _ALLCAPS.finditer(s):
            vocab.add(m.group(0).lower())
    for m in _CAP_TOKEN.finditer(ledger_text or ""):
        vocab.add(m.group(1).lower())
    for m in _ALLCAPS.finditer(ledger_text or ""):
        vocab.add(m.group(0).lower())
    return {w for w in vocab if w not in _EN_COMMON_CAPS}


def guard_target(claim_text: str, dev: dict | None, ledger_text: str = "") -> dict:
    """戻り値 {"target": bool, "types": [...]}。claim_text=Stage1が指摘した英語文。決定論・API無し。"""
    dev = dev or {}
    t = (claim_text or "")
    types = []
    if _neg_a(t) or dev.get("changed_negation"):
        types.append("negation_absence_or_polarity")
    if UNIV_EN.search(t):
        types.append("universal")
    if dev.get("changed_comparison"):
        types.append("direction")
    if dev.get("changed_actor"):
        types.append("subject_flag")
    else:
        led_low = (ledger_text or "").lower()
        words = re.findall(r"[A-Za-z][A-Za-z\-]*", t)
        title_case = len(words) >= 4 and sum(1 for w in words if w[0].isupper()) / len(words) >= 0.6
        if led_low and not title_case:  # Title Case(タイトル型)は大文字語が固有名詞を意味しないため、このルールは使わない(changed_actorフラグのみ)
            for m in _CAP_TOKEN.finditer(t):
                w = m.group(1)
                if w.lower() in _EN_COMMON_CAPS or w.lower() in _PRONOUNS or m.start() == 0:
                    continue
                if w.lower() not in led_low:
                    types.append("subject_new_proper_noun")
                    break
    if _NUM_DIGIT.search(t) or dev.get("changed_number"):
        types.append("number")
    return {"target": bool(types), "types": types}


# ----------------------------------------------------------------------------------------------
# A-(b) Stage2 prompt追記(V7c)とschema
# ----------------------------------------------------------------------------------------------
READER_BELIEF_ADDENDUM_V1 = """
【読者信念テスト(入力のguard_targetがtrueのclaimだけに適用)】
1. まず、英語学習者がこの文だけを読んだとき、世界について何を信じるかを、1文のreader_belief(日本語)として書いてください。文の言い回しではなく、「世界の事実として何が述べられたと受け取るか」を書きます。
2. reader_beliefをVerified Fact Ledgerの各factと照合し、belief_vs_ledgerを次から1つ選んでください。
   - contradicts: Ledgerの肯定的なfactと矛盾する(Ledgerが別の主体・値・方向・否定/肯定を明記している)。矛盾するfact_idをcontradicting_fact_idsへ入れてください。
   - unsupported_new_claim: 矛盾はしないが、Ledgerに無い新しい世界についての主張である。
   - consistent: Ledgerと矛盾せず、Ledgerのfactで支えられる(または語順・言い換えだけの違い)。
   - unclear: 判断できない。
3. belief_vs_ledgerがcontradictsなら、materialityはBLOCKINGにしてください(QUALITY/ACCEPTABLEにしないでください)。
4. 語り手の枠(I/we/youによる語りかけ・問いかけ・体験の演出。例: 「I followed ...」型)は、それ自体を世界についての主張として扱わないでください。枠そのものを根拠にunsupported_new_claim/contradictsにせず、枠の中で述べられる世界の事実の部分だけをreader_beliefにしてください。
5. guard_targetがfalseのclaimには、この手順は不要です(reader_beliefは空文字、belief_vs_ledgerはnot_applicable、contradicting_fact_idsは空配列)。guard_targetは私(システム)が決めて渡します。あなたが対象かどうかを判断する必要はありません。
"""

# rubric調整1版目(v2): 初回replayの結果を見たうえで追記・変更する場合の置き場。変更点は eval/STAGE2_RESULT.md に記録する(未使用時は v1 と同一)。
READER_BELIEF_ADDENDUM_V2 = READER_BELIEF_ADDENDUM_V1


def belief_addendum() -> str:
    return READER_BELIEF_ADDENDUM_V2 if os.environ.get(RUBRIC_VERSION_ENV, "v1") == "v2" else READER_BELIEF_ADDENDUM_V1


_BELIEF_PROPS = {
    "reader_belief": {"type": "string"},
    "belief_vs_ledger": {"type": "string", "enum": list(BELIEF_VALUES) + [BELIEF_NA]},
    "contradicting_fact_ids": {"type": "array", "items": {"type": "string"}},
}


def _belief_schema(base_schema: dict, name: str) -> dict:
    sch = copy.deepcopy(base_schema)
    sch["name"] = name
    item = sch["schema"]["properties"]["judgments"]["items"]
    item["properties"].update(copy.deepcopy(_BELIEF_PROPS))
    item["required"] = list(item["required"]) + list(_BELIEF_PROPS)
    return sch


BODY_BELIEF_SCHEMA = _belief_schema(s2p.BATCH_JSON_SCHEMA, "open233_stage2_belief_body_v1")
HOOK_BELIEF_SCHEMA = _belief_schema(s2h.HOOK_BATCH_JSON_SCHEMA, "open233_stage2_belief_hook_v1")

# 2回目(O1): 文を見せず、reader_beliefとLedgerだけで判定する。
BELIEF_ONLY_DEVELOPER_MESSAGE = (
    "あなたはVerified Fact Ledgerとの整合を判定する独立監査担当です。記事の文は見えません。"
    "与えられるのは、読者が信じる内容(reader_belief)の記述とLedgerだけです。"
)
BELIEF_ONLY_PROMPT_TEMPLATE = """以下の【Verified Fact Ledger(全文)】と、読者が信じる内容の記述(reader_belief)の配列があります。
各reader_beliefがLedgerとどういう関係かを、itemごとに独立に判定してください(記事の文は提示しません)。

【Verified Fact Ledger(全文)】
{verified_ledger_text}

【reader_belief配列】
{items_block}

【判定】belief_vs_ledgerを次から1つ選んでください。
- contradicts: Ledgerの肯定的なfactと矛盾する(Ledgerが別の主体・値・方向・否定/肯定を明記している)。矛盾するfact_idをcontradicting_fact_idsへ。
- unsupported_new_claim: 矛盾はしないが、Ledgerに無い新しい世界についての主張。
- consistent: Ledgerと矛盾せず、Ledgerのfactで支えられる。
- unclear: 判断できない。
item_indexを付けて、同じ順序・同じ件数で返してください。"""
BELIEF_ONLY_SCHEMA = {
    "name": "open233_stage2_belief_only_v1",
    "schema": {
        "type": "object",
        "properties": {"judgments": {"type": "array", "items": {
            "type": "object",
            "properties": {"item_index": {"type": "integer"},
                           "belief_vs_ledger": {"type": "string", "enum": list(BELIEF_VALUES)},
                           "contradicting_fact_ids": {"type": "array", "items": {"type": "string"}}},
            "required": ["item_index", "belief_vs_ledger", "contradicting_fact_ids"],
            "additionalProperties": False}}},
        "required": ["judgments"],
        "additionalProperties": False,
    },
    "strict": True,
}


def _claims_block_body(claims: list) -> str:
    blocks = []
    for i, c in enumerate(claims):
        blocks.append(
            f"[claim_index={i}]\nclaim: {c['claim_text']}\n"
            f"ローカル文脈(段落±1): {c.get('local_context', '')}\n"
            f"origin: {c.get('origin') or '(不明)'}\n"
            f"related_fact_id: {c.get('related_fact_id') or '(不明)'}\n"
            f"section_type(title/hook/in_one_line/body): {c.get('section_type') or 'body'}\n"
            f"guard_target: {'true' if c.get('guard_target') else 'false'}")
    return "\n\n".join(blocks)


def _claims_block_hook(claims: list) -> str:
    blocks = []
    for i, c in enumerate(claims):
        blocks.append(
            f"[claim_index={i}]\nclaim: {c['claim_text']}\n"
            f"origin: {c.get('origin') or '(不明)'}\n"
            f"related_fact_id: {c.get('related_fact_id') or '(不明)'}\n"
            f"guard_target: {'true' if c.get('guard_target') else 'false'}")
    return "\n\n".join(blocks)


def _finish(response, prompt: str, t0: float) -> dict:
    parsed = json.loads(response.output_text)
    usage = s2p._extract_usage(response)
    return {"prompt_sha256": s2p.sha256_text(prompt), "parsed": parsed, "model": response.model,
            "response_id": response.id, "usage": usage, "cost_jpy": round(s2p.official_cost_jpy(usage), 4),
            "elapsed_seconds": round(time.time() - t0, 3)}


def run_belief_batch_body(client, ledger_text: str, source_article_text, claims: list, rubric_text: str, model: str) -> dict:
    prompt = s2p.BATCH_PROMPT_TEMPLATE.format(
        verified_ledger_text=ledger_text, source_article_text=source_article_text or "(なし)",
        claims_block=_claims_block_body(claims), materiality_rubric=rubric_text + belief_addendum(),
        rewrite_hint_instruction=s2p.REWRITE_HINT_INSTRUCTION)
    t0 = time.time()
    resp = client.responses.create(
        model=model, reasoning={"effort": vfl01.REASONING_EFFORT},
        text={"format": {"type": "json_schema", **BODY_BELIEF_SCHEMA}},
        input=[{"role": "developer", "content": s2p.STAGE2_PROD_DEVELOPER_MESSAGE}, {"role": "user", "content": prompt}])
    return _finish(resp, prompt, t0)


def run_belief_batch_hook(client, ledger_text: str, source_article_text, title_hook_text: str, claims: list,
                          hook_rubric_text: str, model: str) -> dict:
    prompt = s2h.HOOK_BATCH_PROMPT_TEMPLATE.format(
        verified_ledger_text=ledger_text, source_article_text=source_article_text or "(なし)",
        title_hook_text=title_hook_text or "(なし)", claims_block=_claims_block_hook(claims),
        hook_rubric=hook_rubric_text + belief_addendum(), rewrite_hint_instruction=s2p.REWRITE_HINT_INSTRUCTION)
    t0 = time.time()
    resp = client.responses.create(
        model=model, reasoning={"effort": vfl01.REASONING_EFFORT},
        text={"format": {"type": "json_schema", **HOOK_BELIEF_SCHEMA}},
        input=[{"role": "developer", "content": s2h.HOOK_DEVELOPER_MESSAGE}, {"role": "user", "content": prompt}])
    return _finish(resp, prompt, t0)


def run_belief_only(client, ledger_text: str, beliefs: list, model: str) -> dict:
    """O1: 文を見せない2回目。beliefs=list[str](reader_belief)。"""
    items = "\n".join(f"[item_index={i}] reader_belief: {b}" for i, b in enumerate(beliefs))
    prompt = BELIEF_ONLY_PROMPT_TEMPLATE.format(verified_ledger_text=ledger_text, items_block=items)
    t0 = time.time()
    resp = client.responses.create(
        model=model, reasoning={"effort": vfl01.REASONING_EFFORT},
        text={"format": {"type": "json_schema", **BELIEF_ONLY_SCHEMA}},
        input=[{"role": "developer", "content": BELIEF_ONLY_DEVELOPER_MESSAGE}, {"role": "user", "content": prompt}])
    return _finish(resp, prompt, t0)


# ----------------------------------------------------------------------------------------------
# A-(c)(d)(e) 決定論の分岐(純関数)
# ----------------------------------------------------------------------------------------------
def consistency_invalid(is_guard: bool, belief: str | None, materiality: str) -> bool:
    """(c) 同一call内整合: guard_targetでbelief_vs_ledger==contradictsなのに非BLOCKINGの出力は無効。"""
    return bool(is_guard and belief == "contradicts" and materiality != "BLOCKING")


def downgrade_established_first_call(is_guard: bool, belief: str | None) -> bool:
    """(d)前半: guard_targetの格下げは1回目callのbelief_vs_ledgerがconsistentのときのみ成立しうる。guard対象外は常にTrue(=従来)。"""
    return (not is_guard) or belief == "consistent"


def downgrade_confirmed_by_second(first_belief: str | None, second_belief: str | None) -> bool:
    """(d)後半: 2nd opinion両call(1回目=文あり / 2回目=文を伏せreader_beliefのみ)がconsistentのときのみ成立。"""
    return first_belief == "consistent" and second_belief == "consistent"


def reuse_forbidden(is_guard: bool) -> bool:
    """(e) cycle2での前回判定再利用はguard_targetで禁止(スイッチON時のみ呼ばれる)。"""
    return bool(is_guard)


# ----------------------------------------------------------------------------------------------
# B. 構造要素の4照合
# ----------------------------------------------------------------------------------------------
def _tokens(text: str) -> list:
    return re.findall(r"[A-Za-z][A-Za-z0-9’'\-]*", text or "")


def subject_set(text: str, vocab: set) -> set:
    """主体・代名詞集合: 代名詞(I/we/you/they等) ∪ 固有名詞語彙に属する語 ∪ 主体クラス(users/employees等)。"""
    out: set = set()
    for tok in _tokens(text):
        w = re.sub(r"[’']s$", "", tok).lower()
        if w in _PRONOUNS:
            out.add(w)
        elif w in vocab:
            out.add(w)
    import er052_open233_self_recovery_flow_runner_01 as runner
    for cls in runner.actor_classes_in_text(text or ""):
        out.add("class:" + cls)
    return out


def numbers_of(text: str) -> set:
    import er052_open233_stage1_coverage_checker_01 as cov
    return set(cov.numeric_value_set(text or ""))


_MD_HEAD = re.compile(r"^(#{1,6})\s")


def format_ok(kind: str, before: str, after: str) -> tuple:
    """形式保存: 記法(`# `等)と長さ上限。戻り値=(ok, reason)。"""
    b, a = (before or "").strip(), (after or "").strip()
    mb, ma = _MD_HEAD.match(b), _MD_HEAD.match(a)
    if kind in ("title", "heading"):
        if bool(mb) != bool(ma) or (mb and ma and mb.group(1) != ma.group(1)):
            return False, "markup_changed"
        if "\n" in a and "\n" not in b:
            return False, "multiline"
        cap = 120 if kind == "title" else 100
        if len(a) > max(cap, int(len(b) * 1.5)) :
            return False, "too_long"
    else:
        if ma and not mb:
            return False, "markup_added"
        if len(a) > int(len(b) * 1.6) + 30:
            return False, "too_long"
    if not a:
        return False, "empty"
    return True, None


def four_checks(kind: str, before: str, after: str, vocab: set, body_text: str) -> dict:
    """設計§1-2の4照合(決定論)。戻り値 {"ok": bool, "violations": [...], 詳細}。
    1 主体: 出力の主体・代名詞集合が元の部分集合(主体語の差し替え=不通過)
    2 極性: 否定語・不在語の有無が元と同じ
    3 数値: 出力の数値が本文の数値の部分集合
    4 形式: 記法・長さ上限"""
    viol = []
    sb, sa = subject_set(before, vocab), subject_set(after, vocab)
    new_subj = sorted(sa - sb)
    if new_subj:
        viol.append("subject")
    if _neg_a(before) != _neg_a(after):
        viol.append("polarity")
    body_nums = numbers_of(body_text) | numbers_of(before)
    bad_nums = sorted(numbers_of(after) - body_nums)
    if bad_nums:
        viol.append("number")
    f_ok, f_reason = format_ok(kind, before, after)
    if not f_ok:
        viol.append("format:" + str(f_reason))
    return {"ok": not viol, "violations": viol, "kind": kind, "new_subjects": new_subj,
            "subjects_before": sorted(sb), "subjects_after": sorted(sa), "bad_numbers": [str(x) for x in bad_nums]}


REGEN_NOTE_TEMPLATE = (
    "\n\n【再生成の指示】前回の出力は次の照合に通りませんでした: {viol}。"
    "元の要素に無かった主体・代名詞(例: I→Meta のような差し替え)を入れず、否定/肯定の向きと数値を変えず、"
    "元の記法・長さを保ち、元の要素を最小限に直してください(限定語が足りない場合は1語足すだけでよい)。")
