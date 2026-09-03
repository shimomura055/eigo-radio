# ============================================================
# er011_a2_reading_resolver_01.py
# ER-011-NO18-CONNECTED-SPEECH-READING-RESOLVER-PRODUCTION-WIRING-08
# ============================================================
# ER-011-CONNECTED-SPEECH-AND-A2-READING-TRIAL-07 Track BでVALIDATEDと
# 判定された、A2 Reading ResolverのProduction版(方式はTrial07から
# 無変更で移植)。A2(日本語)専用。B1へは適用しない。
#
#   canonical / ASR
#     -> 既存機械かな変換(pykakasi)
#     -> 差分箇所を機械的に特定(difflib)
#     -> 対象漢字の読み候補をpykakasi内蔵辞書(kanwadict)から取得
#        (「後=あと」のような個別hardcodeは一切しない)
#     -> LLMは全文文脈を参照しつつ「与えられた候補から1つ選ぶだけ」
#        (JSON Schemaのenumで候補外を選べない、自由生成もさせない)
#     -> 再比較
#
# fail-safe(ユーザー正式決定§2、いずれの場合もresolved_match=Falseで
# 返し、呼び出し側はPASSさせないこと):
#   - 読み候補が取得できない(辞書に登録が無い) -> そのchunkは未解決のまま
#   - LLMが候補外を返す                        -> 例外化してcatch
#   - LLM応答が不正(パース不能等)              -> 例外化してcatch
#   - Resolver後もcanonical/ASRが一致しない     -> resolved_match=False
#   - その他あらゆる例外                        -> catchしresolved_match=False
# 「LLMが何か選んだからPASS」は絶対にしない。resolved_matchが厳密に
# Trueになった場合のみ呼び出し側でPASS候補として扱ってよい。

from __future__ import annotations

import difflib
import json
import re

import pykakasi
from pykakasi.kanji import Kanwa

_HALFWIDTH_PUNCT = "、。・「」『』（）()!?!?…—―‥～〜/／,.　 \n\t"
_KATAKANA_TO_HIRAGANA = {chr(c): chr(c - 0x60) for c in range(0x30A1, 0x30F7)}

_kks = pykakasi.kakasi()
_kanwa = Kanwa()

CJK_RE = re.compile(r"[一-鿿]")

_client = None
_resolver_model = None


def _get_client():
    global _client
    if _client is None:
        import er003_v1_en_direct_vfl_01_generate as vfl01
        _client = vfl01.get_client()
    return _client


def _get_resolver_model():
    global _resolver_model
    if _resolver_model is None:
        import er006_model_routing_contract_01 as routing
        _resolver_model = routing.require_model_or_override(
            "A2_SUPPORT", routing.SUPPORT_MODEL, override_reason=None)
    return _resolver_model


def contains_kanji_char(ch: str) -> bool:
    return bool(CJK_RE.match(ch))


def mechanical_chunks(text: str):
    return _kks.convert(text)


def hira_string(chunks) -> str:
    return "".join(c["hira"] for c in chunks)


def normalize_kana_for_compare(text: str) -> str:
    """比較専用の軽量正規化: 句読点・空白除去、カタカナ->ひらがな変換のみ。"""
    if not text:
        return ""
    out = []
    for ch in text:
        if ch in _HALFWIDTH_PUNCT:
            continue
        out.append(_KATAKANA_TO_HIRAGANA.get(ch, ch))
    return "".join(out)


def _chunk_offsets(chunks):
    offsets = []
    pos = 0
    for c in chunks:
        h = c["hira"]
        offsets.append((pos, pos + len(h), c))
        pos += len(h)
    return offsets


def single_char_candidates(ch: str) -> list[str]:
    """pykakasi内蔵のkanwadictから、1文字chの読み候補一覧をそのまま返す
    (個別単語の正解を決め打ちしない、辞書由来の候補のみ)。"""
    if not contains_kanji_char(ch):
        return []
    table = _kanwa.load(ch)
    if not table:
        return []
    entry = table.get(ch)
    if not entry:
        return []
    seen = []
    for yomi, con in entry:
        if yomi not in seen:
            seen.append(yomi)
    return seen


def _chunks_overlapping(offsets, start, end):
    return [(idx, c) for idx, (s, e, c) in enumerate(offsets) if not (e <= start or s >= end)]


def call_resolver(full_text_context: str, target_word: str, candidates: list[str]) -> dict:
    schema = {
        "type": "object",
        "properties": {"selected_reading": {"type": "string", "enum": candidates}},
        "required": ["selected_reading"],
        "additionalProperties": False,
    }
    developer = (
        "あなたは日本語の読み解決だけを行う専門役割です。Writer(記事執筆)ではありません。\n"
        "与えられた全文の文脈から、指定された単語(漢字を含む語)の、その文脈における\n"
        "自然な読みを判断してください。\n"
        "必ず、与えられた候補一覧の中から1つだけを選んでください。候補にない読みを\n"
        "新しく作ってはいけません。単語だけを見て機械的に決めるのではなく、\n"
        "文中でその単語がどう使われているか(時間の前後関係を表す語か、位置を表す語か等)\n"
        "を判断材料にしてください。"
    )
    user = f"全文:\n{full_text_context}\n\n対象語: {target_word}\n候補一覧: {candidates}"
    response = _get_client().responses.create(
        model=_get_resolver_model(),
        reasoning={"effort": "low"},
        text={"format": {"type": "json_schema", "name": "reading_resolver_output",
                          "schema": schema, "strict": True}},
        input=[{"role": "developer", "content": developer}, {"role": "user", "content": user}],
    )
    parsed = json.loads(response.output_text)
    selected = parsed["selected_reading"]
    if selected not in candidates:
        # 構造的にはJSON Schema enumで防がれているはずだが、fail-safeとして
        # 二重に確認する(ユーザー正式決定§2: 候補外応答はNG/STOP)。
        raise ValueError(f"resolver returned reading outside candidates: {selected!r} not in {candidates!r}")
    return {"selected_reading": selected, "response_id": response.id, "model": response.model}


def _resolve_side(text: str, other_side_hira: str, side_label: str, log: list) -> dict:
    chunks = mechanical_chunks(text)
    offsets = _chunk_offsets(chunks)
    hira = hira_string(chunks)

    sm = difflib.SequenceMatcher(None, hira, other_side_hira, autojunk=False)
    diff_spans = [op for op in sm.get_opcodes() if op[0] != "equal"]

    resolved_chunk_hira = {c_idx: c["hira"] for c_idx, (s, e, c) in enumerate(offsets)}
    calls_made = 0

    for tag, i1, i2, j1, j2 in diff_spans:
        overlapping = _chunks_overlapping(offsets, i1, i2)
        for c_idx, c in overlapping:
            orig = c["orig"]
            if not orig or not contains_kanji_char(orig[0]):
                continue
            leading_kanji = orig[0]
            candidates = single_char_candidates(leading_kanji)
            if not candidates:
                continue  # 辞書に候補がない -> このchunkは未解決のまま(fail-safe)
            trailing = orig[1:]
            trailing_hira = hira_string(mechanical_chunks(trailing)) if trailing else ""

            result = call_resolver(text, orig, candidates)
            calls_made += 1
            selected = result["selected_reading"]
            if trailing_hira and selected.endswith(trailing_hira):
                new_hira = selected
            else:
                new_hira = selected + trailing_hira
            resolved_chunk_hira[c_idx] = new_hira
            log.append({
                "side": side_label, "chunk_orig": orig, "chunk_index": c_idx,
                "mechanical_hira": c["hira"], "candidates": candidates,
                "selected_reading": selected, "resolved_chunk_hira": new_hira,
                "response_id": result["response_id"], "model": result["model"],
            })

    resolved_hira = "".join(resolved_chunk_hira[i] for i in range(len(offsets)))
    return {"resolved_hira": resolved_hira, "resolver_calls": calls_made}


def resolve_reading_diff(canonical_text: str, asr_text: str) -> dict:
    """canonical_text/asr_textの機械かな変換が不一致の場合に呼ぶ。
    差分箇所のみ辞書候補+LLM選択で解決し、再比較した結果を返す。
    resolved_match=Trueの場合のみ、呼び出し側はPASS候補として扱ってよい。
    それ以外(False)は、理由(error等)に関わらず一律non-PASSとして
    既存のTRUE_CONTENT_MISMATCH処理へfall throughすること。"""
    result = {
        "used_resolver": False, "resolved_match": False, "resolver_calls": 0,
        "call_log": [], "error": None,
        "mechanical_canonical_hira": None, "mechanical_asr_hira": None,
        "resolved_canonical_hira": None, "resolved_asr_hira": None,
    }
    try:
        canonical_chunks_hira = hira_string(mechanical_chunks(canonical_text))
        asr_chunks_hira = hira_string(mechanical_chunks(asr_text))
        result["mechanical_canonical_hira"] = normalize_kana_for_compare(canonical_chunks_hira)
        result["mechanical_asr_hira"] = normalize_kana_for_compare(asr_chunks_hira)

        log: list = []
        canonical_result = _resolve_side(canonical_text, asr_chunks_hira, "canonical", log)
        asr_result = _resolve_side(asr_text, canonical_chunks_hira, "asr", log)
        result["resolver_calls"] = canonical_result["resolver_calls"] + asr_result["resolver_calls"]
        result["used_resolver"] = result["resolver_calls"] > 0
        result["call_log"] = log

        resolved_expected = normalize_kana_for_compare(canonical_result["resolved_hira"])
        resolved_actual = normalize_kana_for_compare(asr_result["resolved_hira"])
        result["resolved_canonical_hira"] = resolved_expected
        result["resolved_asr_hira"] = resolved_actual
        result["resolved_match"] = bool(resolved_expected) and resolved_expected == resolved_actual
    except Exception as exc:
        # fail-safe: どんな例外でも「解決できなかった」として扱い、
        # 呼び出し側でのPASSを一切許可しない。
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["resolved_match"] = False
    return result
