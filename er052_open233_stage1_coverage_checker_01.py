# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_stage1_coverage_checker_01.py
# OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 (委任_06、Trial専用、Production未配線・APPROVED_FOR_PRODUCTIONではない)
# Opus#16を受けたFable確定構成の実装: Stage 1を「文ID網羅の3'-R(記事->Ledger)+Ledger逆照合の5-lite(Ledger->記事)」の
# 2経路の和集合(coverage_union)へ置き換えるTrial候補。LLM呼び出しは`call_fn`注入(偽LLMで¥0検証可能、runnerが実client接続を担う)。
# 本moduleはrunnerをimportしない(循環回避)。文分割はrunnerの`vs_sentence_segments_l6`を`segment_fn`で受け取る。
# 重大度(MAJOR/MINOR)はStage 1で決めない。候補は全てStage 2へ。Checker V0/V4A promptの既存定数は変更しない(新promptは本module)。
# ============================================================
from __future__ import annotations

import hashlib
import json
import re
import unicodedata

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_precheck_01 as precheck

MODULE_VERSION = "stage1_coverage_v1"
FLAG_KEYS = list(vfl01.DEVIATION_FLAG_KEYS)  # 既存10フラグ(changed_fact..unsupported_new_claim)
ROUTES_ALL = ("both", "r3_only", "r5_only")
SUB_REASONS = ("model", "coverage_gap", "quote_missing", "quote_not_in_ledger", "unknown_fact_id", "number_not_in_fact",
               "causal_not_in_fact", "negation_polarity_mismatch", "group_inconsistent", "duplicate_conflict",
               "unknown_unit_id")

# 関係単位の文頭語(因果・照応)。runnerの`CAUSAL_SENTENCE_INITIAL_EN`(following)は呼び出し側が`initial_extra`で渡す。
RELATION_INITIAL_WORDS = (
    "so", "this is why", "that is why", "that's why", "which is why", "as a result", "as a consequence", "therefore",
    "thus", "hence", "consequently", "accordingly", "for this reason", "because of this", "because of that",
    "this is because", "that is because", "that's because", "as such", "this means", "that means",
    "this led to", "that led to", "this caused", "that caused", "this made", "that made",
)
_LEAD_JUNK = r"[\s\"'“”‘’\(\[—–\-]*"


def build_relation_initial_re(initial_extra=()) -> "re.Pattern":
    words = sorted(set(RELATION_INITIAL_WORDS) | {w.lower() for w in (initial_extra or ())}, key=len, reverse=True)
    body = "|".join(re.escape(w).replace(r"\ ", r"\s+") for w in words)
    return re.compile(r"^" + _LEAD_JUNK + r"(?:" + body + r")\b", re.I)


_QUOTE_MAP = str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'"})
_ALNUM_RE = re.compile(r"[A-Za-z0-9぀-ヿ一-鿿]")


def norm_sentence(s: str) -> str:
    """同文判定用の正規化(空白・引用符・大小文字、前後の句読点・引用符を除去)。"""
    t = unicodedata.normalize("NFKC", s or "").translate(_QUOTE_MAP)
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t.strip(" .,!?;:\"'—–-")


def norm_for_quote(s: str) -> str:
    """逐語引用の実在検査用(NFKC・引用符統一・全空白除去・小文字)。"""
    t = unicodedata.normalize("NFKC", s or "").translate(_QUOTE_MAP)
    return re.sub(r"\s+", "", t).lower()


def sha256_text(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


# ------------------------------------------------------------
# 1. 文ID分割(決定論)
# ------------------------------------------------------------
def _default_segment_fn(text: str) -> list:
    import er052_open233_self_recovery_flow_runner_01 as runner  # 遅延import(通常はrunnerが`segment_fn`を渡す)
    return runner.vs_sentence_segments_l6(text)


def _blocks(text: str) -> list:
    """行単位で title/heading/oneline_marker/paragraph のブロックへ分ける(offsetは元本文の座標)。"""
    out, pos, cur, seen_title = [], 0, None, False

    def flush():
        nonlocal cur
        if cur is not None:
            out.append({"kind": "paragraph", "start": cur[0], "end": cur[1]})
            cur = None

    for line in text.split("\n"):
        ls = pos + (len(line) - len(line.lstrip()))
        le = pos + len(line.rstrip())
        pos += len(line) + 1
        s = line.strip()
        if not s:
            flush()
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            flush()
            lvl, title = len(m.group(1)), m.group(2)
            if lvl == 1 and not seen_title:
                seen_title = True
                out.append({"kind": "title", "start": ls, "end": le})
            elif re.match(r"(?i)^in one line", title):
                out.append({"kind": "oneline_marker", "start": ls, "end": le})
            else:
                out.append({"kind": "heading", "start": ls, "end": le})
            continue
        cur = [ls, le] if cur is None else [cur[0], le]
    flush()
    return out


def split_units(article_text: str, segment_fn=None, initial_extra=()) -> dict:
    """本文を単位へ分割しIDを付ける。
    ID規則: T=タイトル / H{n}=見出し / S{p}.{s}=本文p段落のs文(p=1はhook段落、role=hook) / L{s}=「In one line」の文 /
    P{p}=段落(構造のみ、判定対象外) / R:{直前文ID}+{当該文ID}=関係単位(文頭が因果・照応語の文と直前文の組)。
    判定対象(judged)=文・タイトル・見出し・関係単位。同文グループ=正規化後に同一の文が複数IDにあるもの。"""
    seg = segment_fn or _default_segment_fn
    rel_re = build_relation_initial_re(initial_extra)
    units, order = [], []
    section, para_no = "body", 0
    for b in _blocks(article_text):
        k = b["kind"]
        if k == "oneline_marker":
            section = "oneline"
            continue
        if k in ("title", "heading"):
            n = sum(1 for u in units if u["type"] == k) + 1
            uid = "T" if k == "title" else f"H{n}"
            units.append({"id": uid, "type": k, "section": section, "para": None, "role": k,
                          "start": b["start"], "end": b["end"], "text": article_text[b["start"]:b["end"]], "judged": True})
            continue
        if section == "body":
            para_no += 1
            pid = f"P{para_no}"
        else:
            pid = "PL"
        ptext = article_text[b["start"]:b["end"]]
        sent_ids = []
        for (a, e) in seg(ptext):
            t = ptext[a:e]
            if not _ALNUM_RE.search(t):
                continue
            if section == "body":
                uid = f"S{para_no}.{len(sent_ids) + 1}"
            else:
                uid = f"L{sum(1 for u in units if u['id'].startswith('L') and u['type'] == 'sentence') + 1}"
            role = "hook" if (section == "body" and para_no == 1) else ("oneline" if section == "oneline" else "body")
            units.append({"id": uid, "type": "sentence", "section": section, "para": pid, "role": role,
                          "start": b["start"] + a, "end": b["start"] + e, "text": t, "judged": True})
            sent_ids.append(uid)
        units.append({"id": pid, "type": "paragraph", "section": section, "para": pid, "role": "paragraph",
                      "start": b["start"], "end": b["end"], "text": ptext, "judged": False, "sentence_ids": sent_ids})
    sents = [u for u in units if u["type"] == "sentence"]
    rels = []
    for prev, cur in zip(sents, sents[1:]):
        if prev["section"] == cur["section"] and rel_re.search(cur["text"]):
            rels.append({"id": f"R:{prev['id']}+{cur['id']}", "type": "relation", "section": cur["section"],
                         "para": cur["para"], "role": "relation", "prev_id": prev["id"], "cur_id": cur["id"],
                         "start": prev["start"], "end": cur["end"], "text": f"{prev['text']} {cur['text']}",
                         "claim_text": cur["text"], "judged": True})
    units.extend(rels)
    groups: dict = {}
    for u in units:
        if u["type"] in ("sentence", "title", "heading"):
            groups.setdefault(norm_sentence(u["text"]), []).append(u["id"])
    same_groups = [ids for ids in groups.values() if len(ids) > 1]
    return {"units": units, "judged_ids": [u["id"] for u in units if u["judged"]], "relation_ids": [r["id"] for r in rels],
            "same_sentence_groups": same_groups}


def unit_claim_text(u: dict) -> str:
    """Stage 2/Rewriteへ渡す箇所の逐語テキスト(関係単位は『当該(後ろの)文』のみ。前文は文脈)。"""
    return u.get("claim_text") or u["text"]


# ------------------------------------------------------------
# 2. Ledger fact block(逐語引用の実在検査・決定論検査の入力)
# ------------------------------------------------------------
def ledger_fact_blocks(ledger_text: str) -> dict:
    """{fact_id: factブロック全文}。`precheck.parse_ledger_text`と同じ見出し規則(V1/V2)・SRC除外で、factの生ブロックを返す。"""
    out: dict = {}
    for block in (ledger_text or "").split("\n\n"):
        lines = [ln for ln in block.split("\n") if ln.strip() != ""]
        if not lines:
            continue
        m1 = precheck.FACT_HEADER_V1.match(lines[0])
        m2 = None if m1 else precheck.FACT_HEADER_V2.match(lines[0])
        fid = m1.group(2) if m1 else (m2.group(1) if m2 else None)
        if not fid or fid.upper().startswith(precheck.NON_FACT_ID_PREFIXES):
            continue
        out.setdefault(fid, "\n".join(lines))
    return out


# ------------------------------------------------------------
# 3. prompt・schema(新規。既存V0/V4A定数は変更しない)
# ------------------------------------------------------------
FLAG_DESCRIPTIONS = """【flagsの10種類】(該当するものをtrue、複数可。SUPPORTED/MATCHでは全てfalse)
- changed_fact: Ledgerに無い、またはLedgerと矛盾する具体的事実
- changed_scope: Ledgerが確認した対象(誰が・どこで・いつ・どの集団か)を超えた一般化・拡張
- changed_causality: 相関を因果に変える、または因果の方向・結び付けを変える(Ledgerが述べていない因果の付与を含む)
- changed_certainty: 仮説・自己申告・解釈にすぎないものを断定に強める
- changed_number: 数値・割合・件数をLedgerと異なる値にする
- changed_actor: 発言主体・調査主体・行為者をLedgerと異なる主体に変える
- changed_negation: 肯定・否定の反転
- changed_comparison: 比較の方向の反転・変更
- changed_time: 時期・年代・順序をLedgerと異なるものにする
- unsupported_new_claim: Ledgerに全く無い新しい具体的主張の追加"""

R3_DEVELOPER_MESSAGE = (
    "あなたはLedger Fact Safetyの検証担当です。記事の面白さやスタイルは評価せず、記事の各単位(文・見出し・関係単位)が"
    "Verified Fact Ledgerで支えられているかだけを、全単位について1件ずつ判定してください。重大度の判定は行いません。"
    "少しでも疑いがあれば候補(CANDIDATE)にしてください。"
)

R3_PROMPT_TEMPLATE = """以下の【単位ID付き記事】の判定必須の単位全てについて、Verified Fact Ledgerで支えられているかを1件ずつ判定してください(記事からLedgerへの全件判定)。

【Verified Fact Ledger】
{ledger_text}

【単位ID付き記事】
{units_block}

【判定必須の単位ID(全{n_required}件)】
{required_ids}

【判定の規則】
1. 判定必須の単位IDの全てについて、unit_verdictsへ必ず1件ずつ出力すること。1件も省略してはならない(省略は機械検査で検出され再実行される)。
2. verdict=SUPPORTED: その単位が述べる全ての主張(数値・割合・件数、主体[誰が・どの組織が]、時期、対象範囲、因果関係、確信度、否定・肯定、比較の方向)が、Ledgerのfactで直接支えられていると確信できる場合だけ選ぶ。SUPPORTEDでは、根拠のfact_idをsupport_fact_idsへ、そのfactの本文からの逐語引用(一字一句そのまま。翻訳・要約・言い換え・省略記号は禁止)をledger_quotesへ必ず入れる。
3. verdict=CANDIDATE: 少しでも疑いがあれば必ずCANDIDATEにする(迷えば候補)。重大度(MAJOR/MINOR)はここでは判定しない(後段が判定する)。次のいずれかなら候補: Ledgerに無い具体的主張がある/数値・主体・時期・範囲がLedgerと違う/因果・確信度・否定・比較がLedgerより強い、または違う/因果や照応を表す語(So、This is why、As a result、Therefore等)で文同士を結んでいるが、その因果関係をLedgerが述べていない。
4. CANDIDATEでは、issue(何が問題か)、claim_in_article(記事内の該当箇所の逐語引用)、related_fact_id(最も関係するfact_id。無ければ空文字)、flags(下記10種類)を埋める。SUPPORTEDでは、issue・claim_in_article・related_fact_idは空文字、flagsは全てfalse。
5. 「R:」で始まる関係単位は、直前の文と当該文を結ぶ因果・照応(So、This is why等)そのものを判定する。各文単体がLedgerと合っていても、結び付けた関係をLedgerが述べていなければCANDIDATE。
6. 文体・言い換え・平易化そのものは問題にしない。意味(Factと関係)が変わるかだけを見る。タイトル・見出し・Hook(冒頭段落)・「In one line」の要約文も同じ基準で判定する。

{flag_descriptions}
{rerun_note}"""

R3_RERUN_NOTE = ("\n【再実行の注意】前回の出力で、上記の判定必須の単位IDの一部が欠落していました。今回は上記の判定必須の単位ID"
                 "(欠落分のみ)の全てについて、省略なく1件ずつ出力してください。")


R5_DEVELOPER_MESSAGE = (
    "あなたはLedger Fact Safetyの検証担当です。Verified Fact Ledgerの各factについて、記事のどの単位が対応しているかを全て挙げ、"
    "各単位がそのfactと一致するか逸脱しているかを判定してください。重大度の判定は行いません。少しでも疑いがあれば逸脱(DEVIATION)にしてください。"
)

R5_PROMPT_TEMPLATE = """Verified Fact Ledgerの各factについて、【単位ID付き記事】のどの単位が対応しているかを全て挙げ、各単位がそのfactと一致するか逸脱しているかを判定してください(Ledgerから記事への逆照合)。

【Verified Fact Ledger】
{ledger_text}

【単位ID付き記事】
{units_block}

【factID一覧(全{n_facts}件)】
{fact_ids}

【規則】
1. factsへ、上記factID一覧の全factを1件ずつ出力する。
2. matches: そのfactの内容に言及している(数値・主体・時期・主張が重なる)単位IDを全て列挙する。文だけでなく関係単位(R:)も対象。同じfactへ複数箇所で言及していれば全て列挙する。言及する単位が無いfactはmatchesを空配列にしてよい。
3. 各matchのverdict: MATCH=その単位の当該factに関する記述がLedgerと一致している / DEVIATION=数値・主体・時期・範囲・因果・確信度・否定・比較のいずれかがLedgerと違う、またはLedgerに無い主張・因果の結び付けがある。少しでも疑えばDEVIATION(迷えば逸脱)。重大度(MAJOR/MINOR)は判定しない。
4. DEVIATIONでは、issue、claim_in_article(記事内の該当箇所の逐語引用)、flags(下記10種類)を埋める。MATCHでは、issueとclaim_in_articleは空文字、flagsは全てfalse。
5. 文体・言い換え・平易化そのものは逸脱としない。意味(Factと関係)が変わるかだけを見る。

{flag_descriptions}
"""


def _flags_schema() -> dict:
    return {"type": "object", "properties": {k: {"type": "boolean"} for k in FLAG_KEYS},
            "required": list(FLAG_KEYS), "additionalProperties": False}


R3_JSON_SCHEMA = {
    "name": "open233_stage1_r3_unit_verdicts_v1",
    "schema": {"type": "object", "properties": {"unit_verdicts": {"type": "array", "items": {
        "type": "object",
        "properties": {
            "unit_id": {"type": "string"}, "verdict": {"type": "string", "enum": ["CANDIDATE", "SUPPORTED"]},
            "support_fact_ids": {"type": "array", "items": {"type": "string"}},
            "ledger_quotes": {"type": "array", "items": {"type": "string"}},
            "issue": {"type": "string"}, "claim_in_article": {"type": "string"}, "related_fact_id": {"type": "string"},
            "flags": _flags_schema()},
        "required": ["unit_id", "verdict", "support_fact_ids", "ledger_quotes", "issue", "claim_in_article",
                     "related_fact_id", "flags"],
        "additionalProperties": False}}}, "required": ["unit_verdicts"], "additionalProperties": False},
    "strict": True,
}

R5_JSON_SCHEMA = {
    "name": "open233_stage1_r5lite_fact_matches_v1",
    "schema": {"type": "object", "properties": {"facts": {"type": "array", "items": {
        "type": "object",
        "properties": {"fact_id": {"type": "string"}, "matches": {"type": "array", "items": {
            "type": "object",
            "properties": {"unit_id": {"type": "string"}, "verdict": {"type": "string", "enum": ["MATCH", "DEVIATION"]},
                           "issue": {"type": "string"}, "claim_in_article": {"type": "string"},
                           "flags": _flags_schema()},
            "required": ["unit_id", "verdict", "issue", "claim_in_article", "flags"],
            "additionalProperties": False}}},
        "required": ["fact_id", "matches"], "additionalProperties": False}}},
        "required": ["facts"], "additionalProperties": False},
    "strict": True,
}

# --- r5-V(委任_11、Trial専用: `STAGE1_R5_MODE=verify_supported`。既定はfull=5-lite、上記定数は不変) ---
# 入力: 記事全文(文脈として。r3の引用・判定は一切渡さない)+Ledger全文+検証対象単位(r3がSUPPORTEDにした単位と関係単位のみ)。
# 方向はfact->記事(5-liteと同じ)。schemaは5-liteと同形(R5_JSON_SCHEMAを共用)。
R5V_DEVELOPER_MESSAGE = (
    "あなたはLedger Fact Safetyの検証担当です。Verified Fact Ledgerの各factについて、【検証対象の単位】のうちどれがそのfactに言及しているかを挙げ、"
    "各単位がそのfactと一致するか逸脱しているかを判定してください。重大度の判定は行いません。少しでも疑いがあれば逸脱(DEVIATION)にしてください。"
)

R5V_PROMPT_TEMPLATE = """Verified Fact Ledgerの各factについて、【検証対象の単位】のどれが当該factに言及しているかを挙げ、各単位がそのfactと一致するか逸脱しているかを判定してください(Ledgerから記事への逆照合)。【記事全文】は文脈を理解するための参考であり、判定の対象は【検証対象の単位】だけです。

【Verified Fact Ledger】
{ledger_text}

【記事全文(文脈)】
{article_text}

【検証対象の単位(IDつき。これらのIDだけをmatchesに使う)】
{units_block}

【factID一覧(全{n_facts}件)】
{fact_ids}

【規則】
1. factsへ、上記factID一覧の全factを1件ずつ出力する。
2. matches: そのfactの内容に言及している(数値・主体・時期・主張が重なる)【検証対象の単位】のIDを全て列挙する。【検証対象の単位】に無いID(記事全文中の他の文)は列挙しない。関係単位(R:)も対象。言及する単位が無いfactはmatchesを空配列にしてよい。
3. 各matchのverdict: MATCH=その単位の当該factに関する記述がLedgerと一致している / DEVIATION=数値・主体・時期・範囲・因果・確信度・否定・比較のいずれかがLedgerと違う、またはLedgerに無い主張・因果の結び付けがある。少しでも疑えばDEVIATION(迷えば逸脱)。特に否定の有無・極性(あった/なかった、増えた/増えていない等)をfactと照合する。重大度(MAJOR/MINOR)は判定しない。
4. DEVIATIONでは、issue、claim_in_article(単位内の該当箇所の逐語引用)、flags(下記10種類)を埋める。MATCHでは、issueとclaim_in_articleは空文字、flagsは全てfalse。
5. 文体・言い換え・平易化そのものは逸脱としない。意味(Factと関係)が変わるかだけを見る。

{flag_descriptions}
"""

R5_MODES = ("full", "verify_supported")
REASONING_EFFORTS = ("high", "medium", "low")

PROMPT_SHA256 = {
    "R3_PROMPT_TEMPLATE": sha256_text(R3_PROMPT_TEMPLATE), "R3_DEVELOPER_MESSAGE": sha256_text(R3_DEVELOPER_MESSAGE),
    "R3_RERUN_NOTE": sha256_text(R3_RERUN_NOTE), "R5_PROMPT_TEMPLATE": sha256_text(R5_PROMPT_TEMPLATE),
    "R5_DEVELOPER_MESSAGE": sha256_text(R5_DEVELOPER_MESSAGE), "FLAG_DESCRIPTIONS": sha256_text(FLAG_DESCRIPTIONS),
    "R3_JSON_SCHEMA": sha256_text(json.dumps(R3_JSON_SCHEMA, sort_keys=True, ensure_ascii=False)),
    "R5_JSON_SCHEMA": sha256_text(json.dumps(R5_JSON_SCHEMA, sort_keys=True, ensure_ascii=False)),
    "R5V_PROMPT_TEMPLATE": sha256_text(R5V_PROMPT_TEMPLATE), "R5V_DEVELOPER_MESSAGE": sha256_text(R5V_DEVELOPER_MESSAGE),
}


def render_units_block(units: list) -> str:
    """単位ID付き記事の表示。段落は構造として括り、文/見出し/タイトル行に[ID]を付ける。関係単位は末尾に別掲。"""
    lines, cur_para = [], None
    for u in units:
        if u["type"] in ("relation", "paragraph"):
            continue
        if u["type"] in ("title", "heading"):
            lines.append(f"[{u['id']}] {u['text']}")
            cur_para = None
            continue
        if u["para"] != cur_para:
            cur_para = u["para"]
            tag = " : hook段落" if u["role"] == "hook" else (" : In one line" if u["role"] == "oneline" else "")
            lines.append(f"({cur_para}{tag})")
        lines.append(f"  [{u['id']}] {u['text']}")
    rels = [u for u in units if u["type"] == "relation"]
    if rels:
        lines.append("(関係単位: 因果・照応語で始まる文と直前文の組)")
        for r in rels:
            lines.append(f"  [{r['id']}] {r['text']}")
    return "\n".join(lines)


def build_r3_prompt(ledger_text: str, units: list, required_ids: list, rerun: bool = False) -> str:
    return R3_PROMPT_TEMPLATE.format(
        ledger_text=ledger_text, units_block=render_units_block(units), n_required=len(required_ids),
        required_ids=", ".join(required_ids), flag_descriptions=FLAG_DESCRIPTIONS,
        rerun_note=R3_RERUN_NOTE if rerun else "")


def build_r5_prompt(ledger_text: str, units: list, fact_ids: list) -> str:
    return R5_PROMPT_TEMPLATE.format(
        ledger_text=ledger_text, units_block=render_units_block(units), n_facts=len(fact_ids),
        fact_ids=", ".join(fact_ids), flag_descriptions=FLAG_DESCRIPTIONS)


def r5v_target_units(units: list, r3_status: dict) -> list:
    """r5-Vの検証対象=r3の最終状態がSUPPORTEDの文・見出し・タイトル単位+関係単位(r3の状態は問わない)。r3の引用・判定は含めない。"""
    out = []
    for u in units:
        if u["type"] == "paragraph":
            continue
        if u["type"] == "relation" or (u.get("judged") and (r3_status or {}).get(u["id"]) == "SUPPORTED"):
            out.append(u)
    return out


def render_target_units_block(targets: list) -> str:
    """検証対象単位の表示(IDと本文のみ。r3の判定・引用・issueは渡さない)。"""
    return "\n".join(f"[{u['id']}] {u['text']}" for u in targets)


def build_r5v_prompt(ledger_text: str, article_text: str, targets: list, fact_ids: list) -> str:
    return R5V_PROMPT_TEMPLATE.format(
        ledger_text=ledger_text, article_text=article_text, units_block=render_target_units_block(targets),
        n_facts=len(fact_ids), fact_ids=", ".join(fact_ids), flag_descriptions=FLAG_DESCRIPTIONS)


# ------------------------------------------------------------
# 4. 決定論検査(SUPPORTED判定の検査。候補生成ではなく「OK判定を覆す」検査)
#    (i)数値 (ii)因果 (iii)否定の極性 + 引用の実在検査。(iv)同文グループ内不一致は後段`apply_group_consistency`。
#    主体名照合は対象外(Fable確定)。いずれも不一致なら候補(CANDIDATE)へ戻す=誤って候補にしても後段(Stage 2)が重大度を決める。
# ------------------------------------------------------------
_NUM_RE = re.compile(r"(?<![A-Za-z0-9_.])(\d[\d,]*(?:\.\d+)?)(\s*(?:million|billion|thousand)\b)?", re.I)
_SCALE = {"million": 1e6, "billion": 1e9, "thousand": 1e3}

CAUSAL_UNIT_RE = re.compile(
    r"(?<![\w'-])(?:because(?:\s+of)?|therefore|thus|hence|consequently|accordingly|as\s+a\s+result|as\s+a\s+consequence|"
    r"led\s+to|leads\s+to|leading\s+to|lead\s+to|resulted\s+in|results\s+in|result\s+in|caused|causes|causing|due\s+to|"
    r"owing\s+to|that\s+is\s+why|this\s+is\s+why|that's\s+why|for\s+this\s+reason|which\s+is\s+why)(?![\w-])"
    r"|(?:^|[.!?]\s+|[\"“”]\s*|,\s*)so\b", re.I)
# 引用factの因果記述の有無(日本語Ledger)。否定・相関の記述は「因果記述なし」として扱う。
CAUSAL_JA_RE = re.compile(r"因果|原因|引き起こ|もたらし|を受けて|を受け、|影響を(?:与え|及ぼ)|によって|により|結果|ため、|ためで|ことで|せい|理由|CAUSAL_STATED")
CAUSAL_DENIAL_JA_RE = re.compile(
    r"因果関係[はをも]?[^。]{0,20}(?:確認できない|示されて(?:い)?ない|不明|主張しない|断定しない|書かない|記述しない)"
    r"|原因として[^。]{0,12}(?:記述|扱|書)[^。]{0,6}(?:しない|わない|ない)|因果[^。]{0,15}(?:書かない|断定しない)|相関")
# 否定語: 日本語はer003_audio_tts_asr_safetyの`_NEGATION_MARKERS_JA`+「なかっ」、英語はprecheck.NEGATION_WORDS+短縮形等
NEGATION_MARKERS_JA = ("ない", "じゃない", "ではない", "でない", "せず", "未", "非", "無", "なく", "なかっ")
NEGATION_EN_RE = re.compile(
    r"(?<![\w'-])(?:" + "|".join(re.escape(w).replace(r"\ ", r"\s+") for w in sorted(
        set(precheck.NEGATION_WORDS) | {"no", "nor", "none", "neither", "cannot", "nobody", "nothing", "no longer"},
        key=len, reverse=True)) + r")(?![\w-])|n't\b", re.I)


def numeric_mentions(text: str) -> list:
    """本文中の数値言及ごとの候補値集合(scale語[million等]付きは換算値のみ、それ以外は素の値+百分率)。"""
    t = unicodedata.normalize("NFKC", text or "")
    out = []
    for m in _NUM_RE.finditer(t):
        try:
            v = float(m.group(1).replace(",", ""))
        except ValueError:
            continue
        sc = (m.group(2) or "").strip().lower()
        out.append({v * _SCALE[sc]} if sc else {v})
    return out


def numeric_value_set(text: str) -> set:
    t = unicodedata.normalize("NFKC", text or "")
    vals = set()
    for m in _NUM_RE.finditer(t):
        try:
            v = float(m.group(1).replace(",", ""))
        except ValueError:
            continue
        sc = (m.group(2) or "").strip().lower()
        vals.add(v)
        if sc:
            vals.add(v * _SCALE[sc])
    return vals | set(precheck.extract_percentages(t)) | set(precheck.extract_counts(t))


def numbers_not_in_facts(unit_text: str, fact_text: str) -> list:
    """(i) unit内の数値言及のうち、引用fact内に(一致・自然な四捨五入のいずれでも)見つからないもの(値のlist)。"""
    fact_vals = numeric_value_set(fact_text)
    bad = []
    for cand in numeric_mentions(unit_text):
        if not any(c == f or precheck.is_natural_rounding(f, c) for c in cand for f in fact_vals):
            bad.append(sorted(cand)[0])
    return bad


def unit_has_causal(unit: dict) -> bool:
    return unit["type"] == "relation" or bool(CAUSAL_UNIT_RE.search(unit_claim_text(unit)))


def facts_have_causal(blocks: list) -> bool:
    return any(CAUSAL_JA_RE.search(b) and not CAUSAL_DENIAL_JA_RE.search(b) for b in blocks)


def negation_mismatch(unit: dict, blocks: list) -> bool:
    """(iii) 単位が否定、引用factのclaim行が全て肯定(または単位が肯定で引用factのclaim行が全て否定)なら不一致。"""
    u_neg = bool(NEGATION_EN_RE.search(unit_claim_text(unit)))
    f_negs = [any(m in b.split("\n")[0] for m in NEGATION_MARKERS_JA) for b in blocks]
    if not f_negs:
        return False
    return (u_neg and not any(f_negs)) or ((not u_neg) and all(f_negs))


# --- 否定是正案a(委任_11、Trial専用スイッチ。既定legacy=従来挙動不変) ---
# fact側=claim行(1行目)のみ。対比構文(ほどなく/ではなく/でなく/意図せず等)は除外、「なし」を追加。英語Ledger行は英語否定語で判定。
# 単位側の英語は'not only'のみ除外(「only」を広く除外語にしない=Opus#17条件)、dislike/lack/fail to/unableを追加。
NEGATION_MODES = ("legacy", "a")
BENIGN_JA_RE = re.compile(r"ほどなく|ではなく|でなく|意図せず|思いがけず|図らずも|知らず|にもかかわらず")
_KANA_RE = re.compile(r"[ぁ-んァ-ヶ]")
NEGATION_EXTRA_JA = ("なし",)
UNIT_EN_EXTRA_RE = re.compile(r"(?<![\w'-])(?:dislik(?:e|es|ed)|lack(?:s|ed)?|fail(?:s|ed)\s+to|unable)(?![\w-])", re.I)
NOT_ONLY_RE = re.compile(r"not\s+only\b", re.I)


def _unit_neg_a(text: str) -> bool:
    t = NOT_ONLY_RE.sub(" ", text or "")
    return bool(NEGATION_EN_RE.search(t) or UNIT_EN_EXTRA_RE.search(t))


def _fact_neg_a(block: str) -> bool:
    line = block.split(chr(10))[0]
    if not _KANA_RE.search(line[:80]):
        return bool(NEGATION_EN_RE.search(line))
    s = BENIGN_JA_RE.sub("", line)
    return any(m in s for m in NEGATION_MARKERS_JA + NEGATION_EXTRA_JA)


def negation_mismatch_a(unit: dict, blocks: list) -> bool:
    """是正案aの(iii)。fact blockが無ければFalse。"""
    if not blocks:
        return False
    u_neg = _unit_neg_a(unit_claim_text(unit))
    f_negs = [_fact_neg_a(b) for b in blocks]
    return (u_neg and not any(f_negs)) or ((not u_neg) and all(f_negs))


def verify_supported(unit: dict, item: dict, blocks_by_id: dict, negation_mode: str = "legacy") -> list:
    """SUPPORTED 1単位の検査。戻り値=候補へ戻す理由(sub_reason)のlist。空ならSUPPORTEDのまま。"""
    reasons = []
    ids = [x for x in (item.get("support_fact_ids") or []) if isinstance(x, str) and x.strip()]
    quotes = [q for q in (item.get("ledger_quotes") or []) if isinstance(q, str) and q.strip()]
    known = [i for i in ids if i in blocks_by_id]
    if not ids or len(known) != len(ids):
        reasons.append("unknown_fact_id")
    if not quotes:
        reasons.append("quote_missing")
    else:
        pool = norm_for_quote("\n".join(blocks_by_id[i] for i in known))
        if any(len(norm_for_quote(q)) < 4 or norm_for_quote(q) not in pool for q in quotes):
            reasons.append("quote_not_in_ledger")
    if known:
        blocks = [blocks_by_id[i] for i in known]
        if numbers_not_in_facts(unit_claim_text(unit), "\n".join(blocks)):
            reasons.append("number_not_in_fact")
        if unit_has_causal(unit) and not facts_have_causal(blocks):
            reasons.append("causal_not_in_fact")
        neg_fn = negation_mismatch_a if negation_mode == "a" else negation_mismatch
        if neg_fn(unit, blocks):
            reasons.append("negation_polarity_mismatch")
    return reasons


# ------------------------------------------------------------
# 5. 経路ごとの評価(3'-R / 5-lite)
# ------------------------------------------------------------
def _flags_from(d: dict) -> dict:
    f = (d or {}).get("flags") or {}
    return {k: bool(f.get(k)) for k in FLAG_KEYS}


def source_of(route: str, sub_reason: str) -> str:
    """M/D区分(委任_11、Opus#17: Safety合格数にD検出を入れない)。model_r3/model_r5=モデル判定(M)、deterministic=決定論検査(D)、coverage_gap=欠落補填。"""
    if sub_reason in ("model", "unknown_unit_id"):
        return "model_" + route
    if sub_reason == "coverage_gap":
        return "coverage_gap"
    return "deterministic"


def _candidate(u: dict, units_by_id: dict, route: str, sub_reason: str, issue: str, flags: dict, related: str,
               model_claim: str = "") -> dict:
    target = units_by_id.get(u.get("cur_id")) if u.get("type") == "relation" else u
    target = target or u
    return {"unit_id": u["id"], "unit_ids": [u["id"]], "claim_text": unit_claim_text(u), "span": [target["start"], target["end"]],
            "routes": [route], "sub_reasons": [sub_reason], "sources": [source_of(route, sub_reason)],
            "issues": [issue] if issue else [], "flags": dict(flags),
            "related_fact_ids": [related] if related else [], "model_claim": model_claim}


def _orphan_candidate(route: str, item: dict, article_text: str) -> dict | None:
    """未知の単位IDで返った候補。モデルの引用が本文に逐語で実在する場合のみ箇所として保持(`unknown_unit_id`)。"""
    claim = (item.get("claim_in_article") or "").strip()
    if not claim:
        return None
    pos = article_text.find(claim)
    return {"unit_id": None, "unit_ids": [], "claim_text": claim, "span": [pos, pos + len(claim)] if pos >= 0 else None,
            "routes": [route], "sub_reasons": ["unknown_unit_id"], "sources": [source_of(route, "unknown_unit_id")],
            "issues": [item.get("issue") or ""],
            "flags": _flags_from(item), "related_fact_ids": [item.get("related_fact_id")] if item.get("related_fact_id") else [],
            "model_claim": claim}


def evaluate_r3(items: list, units_by_id: dict, required_ids: list, blocks_by_id: dict, article_text: str,
                negation_mode: str = "legacy") -> dict:
    """3'-Rの出力itemsを検査し、単位ごとの状態・候補・欠落IDを返す(LLM非依存・決定論)。"""
    first: dict = {}
    conflicts, unknown = set(), []
    for it in items or []:
        uid = it.get("unit_id") if isinstance(it, dict) else None
        if uid in units_by_id:
            if uid in first and first[uid].get("verdict") != it.get("verdict"):
                conflicts.add(uid)
            first.setdefault(uid, it)
        else:
            unknown.append(it)
    status, cands = {}, []
    for uid, it in first.items():
        u = units_by_id[uid]
        if uid in conflicts:
            status[uid] = "SUPPORTED->CANDIDATE(duplicate_conflict)"
            cands.append(_candidate(u, units_by_id, "r3", "duplicate_conflict", "同一IDに矛盾する判定", _flags_from(it), ""))
        elif it.get("verdict") == "CANDIDATE":
            status[uid] = "CANDIDATE"
            cands.append(_candidate(u, units_by_id, "r3", "model", it.get("issue") or "", _flags_from(it),
                                    it.get("related_fact_id") or "", it.get("claim_in_article") or ""))
        else:
            reasons = verify_supported(u, it, blocks_by_id, negation_mode)
            if reasons:
                status[uid] = "SUPPORTED->CANDIDATE(" + ",".join(reasons) + ")"
                cands.append(_candidate(u, units_by_id, "r3", reasons[0], "決定論検査で戻した: " + ",".join(reasons),
                                        _flags_from(it), (it.get("support_fact_ids") or [""])[0] if it.get("support_fact_ids") else ""))
                cands[-1]["sub_reasons"] = list(reasons)
                cands[-1]["sources"] = ["deterministic"]
            else:
                status[uid] = "SUPPORTED"
    orphans = [c for c in (_orphan_candidate("r3", it, article_text) for it in unknown if it.get("verdict") == "CANDIDATE") if c]
    return {"status": status, "candidates": cands + orphans,
            "missing": [i for i in required_ids if i not in first], "unknown_unit_ids": [it.get("unit_id") for it in unknown]}


def apply_group_consistency(status: dict, cands: list, groups: list, units_by_id: dict) -> int:
    """(iv) 同文グループ内でCANDIDATE系とSUPPORTEDが混在するとき、SUPPORTEDのIDを候補へ戻す。戻した件数を返す。"""
    n = 0
    for g in groups:
        st = {i: status.get(i) for i in g if status.get(i)}
        if len({s == "SUPPORTED" for s in st.values()}) < 2:
            continue
        for i, s in st.items():
            if s == "SUPPORTED":
                status[i] = "SUPPORTED->CANDIDATE(group_inconsistent)"
                cands.append(_candidate(units_by_id[i], units_by_id, "r3", "group_inconsistent",
                                        "同文グループ内で判定が不一致", {k: False for k in FLAG_KEYS}, ""))
                n += 1
    return n


def evaluate_r5(facts_out: list, units_by_id: dict, fact_ids: list, article_text: str, scope_ids=None) -> dict:
    """5-liteの出力を検査し、単位ごとの状態(DEVIATION/MATCH/UNMENTIONED)・候補を返す。fact未対応は許容。"""
    status, cands, returned, unknown = {}, [], set(), []
    for f in facts_out or []:
        if not isinstance(f, dict):
            continue
        fid = f.get("fact_id") or ""
        returned.add(fid)
        for m in f.get("matches") or []:
            uid = m.get("unit_id")
            if uid not in units_by_id:
                unknown.append(m)
                continue
            if m.get("verdict") == "DEVIATION":
                status[uid] = "DEVIATION"
                cands.append(_candidate(units_by_id[uid], units_by_id, "r5", "model", m.get("issue") or "", _flags_from(m),
                                        fid, m.get("claim_in_article") or ""))
            else:
                status.setdefault(uid, "MATCH")
    orphans = [c for c in (_orphan_candidate("r5", m, article_text) for m in unknown if m.get("verdict") == "DEVIATION") if c]
    for u in units_by_id.values():
        if u["judged"] and (scope_ids is None or u["id"] in scope_ids):
            status.setdefault(u["id"], "UNMENTIONED")
    return {"status": status, "candidates": cands + orphans, "facts_missing": [i for i in fact_ids if i not in returned],
            "unknown_unit_ids": [m.get("unit_id") for m in unknown]}


def union_candidates(cands: list) -> list:
    """∪: 正規化した箇所の本文(=同文グループ・関係単位と後続文の重複を含む)をキーに重複排除して合流する。"""
    merged: dict = {}
    order: list = []
    for c in cands:
        key = norm_sentence(c["claim_text"]) or ("id:" + ",".join(c["unit_ids"]))
        if key not in merged:
            merged[key] = {"claim_text": c["claim_text"], "span": c.get("span"), "unit_ids": [], "routes": [], "sub_reasons": [], "sources": [],
                           "issues": [], "flags": {k: False for k in FLAG_KEYS}, "related_fact_ids": [], "model_claims": []}
            order.append(key)
        m = merged[key]
        for fld in ("unit_ids", "routes", "sub_reasons", "sources", "related_fact_ids"):
            for v in c.get(fld) or []:
                if v and v not in m[fld]:
                    m[fld].append(v)
        for v in c.get("issues") or []:
            if v and v not in m["issues"]:
                m["issues"].append(v)
        if c.get("model_claim") and c["model_claim"] not in m["model_claims"]:
            m["model_claims"].append(c["model_claim"])
        for k in FLAG_KEYS:
            m["flags"][k] = m["flags"][k] or bool(c["flags"].get(k))
    return [merged[k] for k in order]


# ------------------------------------------------------------
# 6. オーケストレーション(call_fn注入)と、Stage 2へ渡す形への変換
#    call_fn(label, developer_message, prompt, schema) -> (parsed_dict | None, meta_dict)。None=API失敗/JSON不正。
# ------------------------------------------------------------
def _call_with_one_retry(call_fn, label: str, developer: str, prompt: str, schema: dict, calls: list):
    """API失敗(None)なら1回だけ再実行(H1: 再実行1回)。各callのmetaを`calls`へ記録。両方失敗ならNone。"""
    for attempt, suffix in enumerate(("", "_retry")):
        parsed, meta = call_fn(label + suffix, developer, prompt, schema)
        calls.append({"label": label + suffix, **(meta or {}), "ok": parsed is not None})
        if parsed is not None:
            return parsed
    return None


def _run_r3(call_fn, split: dict, fixture: dict, blocks: dict, units_by_id: dict, negation_mode: str = "legacy") -> dict:
    required = list(split["judged_ids"])
    calls: list = []
    out = {"route": "r3", "calls": calls, "api_failure": False, "rerun_used": False}
    parsed = _call_with_one_retry(call_fn, "r3", R3_DEVELOPER_MESSAGE,
                                  build_r3_prompt(fixture["ledger_text"], split["units"], required), R3_JSON_SCHEMA, calls)
    if parsed is None:
        out.update(api_failure=True, status={}, candidates=[], missing_first=required, missing_after_rerun=required)
        return out
    items = list(parsed.get("unit_verdicts") or [])
    ev = evaluate_r3(items, units_by_id, required, blocks, fixture["article_text"], negation_mode)
    out["missing_first"] = list(ev["missing"])
    if ev["missing"]:
        out["rerun_used"] = True
        p2, meta = call_fn("r3_rerun", R3_DEVELOPER_MESSAGE,
                           build_r3_prompt(fixture["ledger_text"], split["units"], ev["missing"], rerun=True), R3_JSON_SCHEMA)
        calls.append({"label": "r3_rerun", **(meta or {}), "ok": p2 is not None})
        if p2 is not None:
            items = items + list(p2.get("unit_verdicts") or [])
            ev = evaluate_r3(items, units_by_id, required, blocks, fixture["article_text"], negation_mode)
    out["missing_after_rerun"] = list(ev["missing"])
    for uid in ev["missing"]:  # なお欠落 -> 当該単位をCANDIDATE(coverage_gap)としてStage 2へ
        ev["status"][uid] = "MISSING->CANDIDATE(coverage_gap)"
        ev["candidates"].append(_candidate(units_by_id[uid], units_by_id, "r3", "coverage_gap",
                                           "3'-Rが当該単位の判定を返さなかった(再実行後も欠落)", {k: False for k in FLAG_KEYS}, ""))
    returned_back = apply_group_consistency(ev["status"], ev["candidates"], split["same_sentence_groups"], units_by_id)
    out.update(status=ev["status"], candidates=ev["candidates"], unknown_unit_ids=ev["unknown_unit_ids"],
               group_returned=returned_back)
    return out


def _run_r5(call_fn, split: dict, fixture: dict, blocks: dict, units_by_id: dict, r5_mode: str = "full",
            r3_status: dict | None = None) -> dict:
    """r5_mode=full: 5-lite(従来、全単位)。verify_supported: r5-V(r3がSUPPORTEDにした単位+関係単位のみ、記事全文は文脈)。"""
    calls: list = []
    fact_ids = list(blocks.keys())
    out = {"route": "r5", "calls": calls, "api_failure": False, "rerun_used": False, "r5_mode": r5_mode}
    scope = None
    if r5_mode == "verify_supported":
        targets = r5v_target_units(split["units"], r3_status or {})
        scope = {u["id"] for u in targets}
        out["r5v_target_ids"] = sorted(scope)
        out["n_r5v_targets"] = len(targets)
        if not targets:  # 検証対象なし(全単位がr3候補)=r5-Vは呼ばない(費用0)。
            out.update(status={}, candidates=[], facts_missing=[], unknown_unit_ids=[], skipped_no_targets=True)
            return out
        label, dev, prompt = "r5v", R5V_DEVELOPER_MESSAGE, build_r5v_prompt(fixture["ledger_text"], fixture["article_text"], targets, fact_ids)
    else:
        label, dev, prompt = "r5", R5_DEVELOPER_MESSAGE, build_r5_prompt(fixture["ledger_text"], split["units"], fact_ids)
    parsed = _call_with_one_retry(call_fn, label, dev, prompt, R5_JSON_SCHEMA, calls)
    if parsed is None:
        out.update(api_failure=True, status={}, candidates=[], facts_missing=fact_ids)
        return out
    ev = evaluate_r5(parsed.get("facts") or [], units_by_id, fact_ids, fixture["article_text"], scope)
    out.update(status=ev["status"], candidates=ev["candidates"], facts_missing=ev["facts_missing"],
               unknown_unit_ids=ev["unknown_unit_ids"])
    return out


def run_stage1_coverage(fixture: dict, call_fn, routes: str = "both", segment_fn=None, initial_extra=(),
                        negation_mode: str = "legacy", r5_mode: str = "full", r3_precomputed: dict | None = None) -> dict:
    """Stage 1(coverage_union)本体。`routes`=both/r3_only/r5_only。戻り値: candidates(∪、重複排除済み)・api_failure・failed_routes・audit。
    経路のAPI失敗(再実行1回後も失敗)は`api_failure=True`(呼び出し側がfail-closedでSTOP)。"""
    if routes not in ROUTES_ALL:
        raise ValueError(f"unknown routes: {routes!r}")
    if negation_mode not in NEGATION_MODES:
        raise ValueError(f"unknown negation_mode: {negation_mode!r}")
    if r5_mode not in R5_MODES:
        raise ValueError(f"unknown r5_mode: {r5_mode!r}")
    if r5_mode == "verify_supported" and routes == "r5_only" and not r3_precomputed:
        raise ValueError("r5_mode=verify_supported requires r3 result (routes=both or r3_precomputed)")
    article = fixture["article_text"]
    split = split_units(article, segment_fn, initial_extra)
    units_by_id = {u["id"]: u for u in split["units"]}
    blocks = ledger_fact_blocks(fixture["ledger_text"])
    res = {}
    if r3_precomputed:  # 保存済みr3出力の再利用(r3を再実行しない。費用0、r5-Vの見積・測定用)
        pre = dict(r3_precomputed)
        pre.setdefault("route", "r3")
        pre.setdefault("status", pre.get("unit_status") or {})  # 保存audit(per_route)は`unit_status`キー
        pre.setdefault("calls", [])
        pre.setdefault("api_failure", False)
        pre["candidates"] = [dict(c, sources=c.get("sources") or [source_of((c.get("routes") or ["r3"])[0], (c.get("sub_reasons") or [""])[0])])
                             for c in pre.get("candidates") or []]
        pre["reused_from_stored"] = True
        res["r3"] = pre
    elif routes in ("both", "r3_only"):
        res["r3"] = _run_r3(call_fn, split, fixture, blocks, units_by_id, negation_mode)
    if routes in ("both", "r5_only"):
        res["r5"] = _run_r5(call_fn, split, fixture, blocks, units_by_id, r5_mode, (res.get("r3") or {}).get("status"))
    failed = [k for k, v in res.items() if v["api_failure"]]
    pre_union = [c for v in res.values() for c in v["candidates"]]
    merged = union_candidates(pre_union)
    ids = {k: {u for c in v["candidates"] for u in c["unit_ids"]} for k, v in res.items()}
    audit = {
        "module_version": MODULE_VERSION, "routes": routes, "prompt_sha256": PROMPT_SHA256,
        "negation_mode": negation_mode, "r5_mode": r5_mode, "r3_reused": bool(r3_precomputed),
        "n_units": len(split["units"]), "n_judged_units": len(split["judged_ids"]), "n_relation_units": len(split["relation_ids"]),
        "relation_ids": split["relation_ids"], "same_sentence_groups": split["same_sentence_groups"], "n_facts": len(blocks),
        "per_route": {k: {"candidate_unit_ids": sorted(ids[k]), "unit_status": v.get("status", {}),
                          "calls": v["calls"], "api_failure": v["api_failure"], "rerun_used": v.get("rerun_used", False),
                          "missing_first": v.get("missing_first"), "missing_after_rerun": v.get("missing_after_rerun"),
                          "group_returned": v.get("group_returned", 0), "facts_missing": v.get("facts_missing"),
                          "reused_from_stored": v.get("reused_from_stored", False), "r5_mode": v.get("r5_mode"),
                          "r5v_target_ids": v.get("r5v_target_ids"), "n_r5v_targets": v.get("n_r5v_targets"),
                          "skipped_no_targets": v.get("skipped_no_targets", False),
                          "unknown_unit_ids": v.get("unknown_unit_ids", []),
                          "candidates": v["candidates"]} for k, v in res.items()},
        "overlap": ({"both": sorted(ids["r3"] & ids["r5"]), "r3_only": sorted(ids["r3"] - ids["r5"]),
                     "r5_only": sorted(ids["r5"] - ids["r3"])} if routes == "both" else None),
        "returned_by_check": {k: sum(1 for s in v.get("status", {}).values() if s.startswith("SUPPORTED->CANDIDATE"))
                              for k, v in res.items() if k == "r3"},
        "union_candidates": merged, "n_union_candidates": len(merged),
        # M/D区分: Safety判定(gold検出の合否)はM(model_r3/model_r5)だけで数える。決定論(D)・coverage_gapのみの候補は別欄。
        "n_model_candidates": sum(1 for c in merged if any(x.startswith("model_") for x in c.get("sources") or [])),
        "n_deterministic_only_candidates": sum(1 for c in merged if not any(x.startswith("model_") for x in c.get("sources") or [])),
        "total_cost_jpy": round(sum(c.get("cost_jpy", 0.0) or 0.0 for v in res.values() for c in v["calls"]), 4),
        "n_calls": sum(len(v["calls"]) for v in res.values()),
    }
    return {"candidates": merged, "api_failure": bool(failed), "failed_routes": failed, "audit": audit}


def candidates_to_deviations(cands: list) -> list:
    """∪候補をStage 2へ渡すdeviation形式へ。重大度はStage 1で決めないため、全件`severity=MAJOR`相当(後段の入口を通す印)で渡し、
    実際の重大度判定(BLOCKING/QUALITY)はStage 2が行う。`claim_in_article`は箇所の逐語テキスト(モデルの引用ではなく単位本文)。"""
    import er051_open233_checker_trial_variant_01 as trial
    out = []
    for c in cands:
        issue = " / ".join(c["issues"]) or ("Stage 1 candidate: " + ",".join(c["sub_reasons"]))
        d = {"claim_in_article": c["claim_text"], "issue": issue, "severity": "MAJOR", **{k: bool(c["flags"].get(k)) for k in FLAG_KEYS},
             "explanation": f"stage1 coverage candidate (routes={','.join(c['routes'])}, sub_reason={','.join(c['sub_reasons'])}, "
                            f"units={','.join(c['unit_ids'])}); severity is decided by Stage 2",
             "related_fact_id": (c["related_fact_ids"] or [""])[0], "origin": None, "auto_downgraded": False,
             "stage1_coverage": {"routes": c["routes"], "sub_reasons": c["sub_reasons"], "unit_ids": c["unit_ids"],
                                 "related_fact_ids": c["related_fact_ids"]}}
        out.append(trial.classify_deviation_trial(d, "V4A"))
    return out


def to_stage1_parsed(result: dict) -> dict:
    """run_stage1_coverageの戻り値を、runnerのStage 1戻り値(overall_status/deviations)の形へ。"""
    devs = candidates_to_deviations(result["candidates"])
    parsed = {"overall_status": "LEDGER_DEVIATION" if devs else "LEDGER_COMPLIANT", "deviations": devs,
              "variant": "coverage_union", "stage1_coverage_audit": result["audit"]}
    if result["api_failure"]:
        parsed = {"overall_status": "LEDGER_DEVIATION", "deviations": [], "_stage1_api_failure": True,
                  "variant": "coverage_union", "stage1_coverage_audit": result["audit"]}
    return parsed
