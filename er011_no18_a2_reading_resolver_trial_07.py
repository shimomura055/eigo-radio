# ============================================================
# er011_no18_a2_reading_resolver_trial_07.py
# ER-011-CONNECTED-SPEECH-AND-A2-READING-TRIAL-07 Track B
# ============================================================
# OPEN-111(A2 comment_1「通知音のあとに」がASRで「後」と書き起こされ続けて
# TRUE_CONTENT_MISMATCHになる問題)への別方式Trial。
#
# Trial-06(前回)は「全文をLLMで自由にひらがな生成」する方式だったため、
# OPEN-111自体は解決できたが、対象語と無関係な箇所(「変化」→「しんか」、
# 正常segmentの「スマートフォン」→「すまあとふぉん」)にLLM自身の新しい
# 読み違いを持ち込んでしまい、REJECTEDと判定した。
#
# 本Trial(07)は、既存の機械かな変換(pykakasi)を土台として維持したまま、
#   1. canonical本文とASR本文をそれぞれ既存のpykakasiでかな変換
#   2. 変換結果(ひらがな文字列)を突き合わせて差分位置だけを検出
#   3. 差分位置に漢字が含まれる場合のみ、その漢字の読み候補を
#      pykakasi自身の内蔵辞書(kanwadict、Kanwa.load())から取得する
#      (「後」=「あと」のような正解の決め打ちではなく、辞書が持つ
#      候補一覧をそのまま使う)
#   4. LLMには、全文文脈と、その漢字の候補一覧だけを渡し、
#      候補の中から1つを選ばせる(JSON Schemaのenumで候補外を選べなく
#      している)。自由生成はさせない。
#   5. 選ばれた候補で該当箇所だけを置き換えて再比較する。
#
# この設計により、差分が出ない箇所(「変化」「スマートフォン」等、
# canonicalとASRの機械変換結果が既に一致している語)にはLLMが一切
# 触れない。Trial-06の副作用(無関係語の新規誤読)が構造的に起こり得ない
# ことを確認するのが本Trialの目的の一つ。
#
# 新規TTS呼び出しは行わない。ASR側も、既存の実運用ASR結果(標準経路の
# 実際の書き起こしテキスト)をそのまま再利用する(新規ASR呼び出しなし、
# 課金対象はReading Resolver LLM呼び出しのみ)。
#
# Production配線は一切行わない。本Trialの結果だけではProduction採用を
# 決定しない。

from __future__ import annotations

import difflib
import json
import os
import re
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import pykakasi
from pykakasi.kanji import Kanwa

import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er011_no18_a2_reading_trial_06 as t06  # normalize_kana_for_compare / contains_kanji を再利用

OUT_DIR = "er011_output/open111_a2_reading_resolver_trial_07"
os.makedirs(OUT_DIR, exist_ok=True)

cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")

client = vfl01.get_client()

RESOLVER_MODEL = routing.require_model_or_override(
    "A2_SUPPORT", routing.SUPPORT_MODEL,
    override_reason=None,  # SUPPORT_MODELとWRITER_MODELは同一Approved Modelのため素通り、overrideなし
)

kks = pykakasi.kakasi()
kanwa = Kanwa()

CJK_RE = re.compile(r"[一-鿿]")


def contains_kanji_char(ch: str) -> bool:
    return bool(CJK_RE.match(ch))


def mechanical_chunks(text: str):
    return kks.convert(text)


def hira_string(chunks) -> str:
    return "".join(c["hira"] for c in chunks)


def chunk_offsets(chunks):
    offsets = []
    pos = 0
    for c in chunks:
        h = c["hira"]
        offsets.append((pos, pos + len(h), c))
        pos += len(h)
    return offsets


def single_char_candidates(ch: str):
    """pykakasi内蔵のkanwadict(kanwa辞書)から、1文字の漢字chの
    読み候補一覧を取得する。ここで返す候補は辞書がそのまま持っている
    ものであり、個別単語の正解を決め打ちしたものではない。"""
    if not contains_kanji_char(ch):
        return []
    table = kanwa.load(ch)
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


def chunks_overlapping(offsets, start, end):
    return [(idx, c) for idx, (s, e, c) in enumerate(offsets) if not (e <= start or s >= end)]


def call_resolver(full_text_context: str, target_word: str, candidates: list[str]):
    schema = {
        "type": "object",
        "properties": {
            "selected_reading": {"type": "string", "enum": candidates},
        },
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
    response = client.responses.create(
        model=RESOLVER_MODEL,
        reasoning={"effort": "low"},
        text={
            "format": {
                "type": "json_schema",
                "name": "reading_resolver_output",
                "schema": schema,
                "strict": True,
            }
        },
        input=[
            {"role": "developer", "content": developer},
            {"role": "user", "content": user},
        ],
    )
    parsed = json.loads(response.output_text)
    return {
        "selected_reading": parsed["selected_reading"],
        "response_id": response.id,
        "model": response.model,
    }


def resolve_side(text: str, other_side_hira: str, side_label: str, log: list):
    """text側(canonicalまたはASR)を機械変換し、other_side_hiraとの
    差分位置のうち、text側チャンクに漢字が含まれる箇所だけをReading
    Resolverで解決する。差分がない/漢字がない箇所はLLMを一切呼ばない。"""
    chunks = mechanical_chunks(text)
    offsets = chunk_offsets(chunks)
    hira = hira_string(chunks)

    sm = difflib.SequenceMatcher(None, hira, other_side_hira, autojunk=False)
    diff_spans = [op for op in sm.get_opcodes() if op[0] != "equal"]

    resolved_chunk_hira = {c_idx: c["hira"] for c_idx, (s, e, c) in enumerate(offsets)}
    calls_made = 0

    for tag, i1, i2, j1, j2 in diff_spans:
        overlapping = chunks_overlapping(offsets, i1, i2)
        for c_idx, c in overlapping:
            orig = c["orig"]
            if not orig or not contains_kanji_char(orig[0]):
                continue  # 差分箇所に漢字がない(=読み候補による解決の対象外)
            leading_kanji = orig[0]
            candidates = single_char_candidates(leading_kanji)
            if not candidates:
                continue  # 辞書に候補がない
            trailing = orig[1:]
            trailing_hira = hira_string(mechanical_chunks(trailing)) if trailing else ""

            result = call_resolver(text, orig, candidates)
            calls_made += 1
            selected = result["selected_reading"]
            # 「二」→「ふたつ」のように、1文字の候補自体が後続のかな
            # (「つ」)まで含む複数モーラの読みになっている場合、
            # 末尾のtrailing_hiraをそのまま連結すると二重になる
            # (「ふたつ」+「つ」=「ふたつつ」)。候補が既にtrailing_hira
            # で終わっている場合はtrailing_hiraを連結しない。
            if trailing_hira and selected.endswith(trailing_hira):
                new_hira = selected
            else:
                new_hira = selected + trailing_hira
            resolved_chunk_hira[c_idx] = new_hira
            log.append({
                "side": side_label,
                "chunk_orig": orig,
                "chunk_index": c_idx,
                "mechanical_hira": c["hira"],
                "candidates": candidates,
                "selected_reading": result["selected_reading"],
                "resolved_chunk_hira": new_hira,
                "response_id": result["response_id"],
                "model": result["model"],
            })

    resolved_hira = "".join(resolved_chunk_hira[i] for i in range(len(offsets)))
    return {
        "mechanical_hira": hira,
        "resolved_hira": resolved_hira,
        "diff_span_count": len(diff_spans),
        "resolver_calls": calls_made,
    }


def run_case(case_id: str, canonical_text: str, asr_text: str, log: list):
    canonical_chunks_hira = hira_string(mechanical_chunks(canonical_text))
    asr_chunks_hira = hira_string(mechanical_chunks(asr_text))

    canonical_result = resolve_side(canonical_text, asr_chunks_hira, "canonical", log)
    asr_result = resolve_side(asr_text, canonical_chunks_hira, "asr", log)

    mech_expected = t06.normalize_kana_for_compare(canonical_result["mechanical_hira"])
    mech_actual = t06.normalize_kana_for_compare(asr_result["mechanical_hira"])
    resolved_expected = t06.normalize_kana_for_compare(canonical_result["resolved_hira"])
    resolved_actual = t06.normalize_kana_for_compare(asr_result["resolved_hira"])

    return {
        "case_id": case_id,
        "canonical_text": canonical_text,
        "asr_text": asr_text,
        "mechanical_match": mech_expected == mech_actual,
        "resolved_match": resolved_expected == resolved_actual,
        "mechanical_expected": mech_expected,
        "mechanical_actual": mech_actual,
        "resolved_expected": resolved_expected,
        "resolved_actual": resolved_actual,
        "canonical_resolver_calls": canonical_result["resolver_calls"],
        "asr_resolver_calls": asr_result["resolver_calls"],
        "total_resolver_calls": canonical_result["resolver_calls"] + asr_result["resolver_calls"],
    }


def main():
    A2_AUDIT_PATH = "er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2/a2/audit/tts_generation_results.json"
    audit = json.load(open(A2_AUDIT_PATH, encoding="utf-8"))
    segs = audit["segments"]

    def last_asr_text(seg_id):
        seg = segs[seg_id]
        log_ = seg.get("standard_attempts_log") or seg.get("attempts_log") or []
        for a in reversed(log_):
            if a.get("asr_text"):
                return a["asr_text"]
        return None

    cases = []
    resolver_log = []

    # comment_1: OPEN-111本体(の後に → のちに 誤り)
    c1_canonical = segs["comment_1"]["canonical_text"]
    c1_asr = last_asr_text("comment_1")
    cases.append(("comment_1", c1_canonical, c1_asr))

    # 正常segment(既存canonical / 既存ASR、新規TTS/ASR呼び出しなし)
    for seg_id in ["comment_2", "comment_3", "comment_4", "japanese_title", "preview"]:
        canonical = segs[seg_id]["canonical_text"]
        asr = last_asr_text(seg_id)
        if asr:
            cases.append((seg_id, canonical, asr))

    # 複数読みがあり得る語を含む追加テキスト例(新規TTS/ASRなし、
    # テキストのみのResolverロジック検証: 「後」が別文脈で
    # 「のち」に解決されるべきケースを、実際に存在する日本語文で確認する)
    synthetic_cases = [
        (
            "synthetic_go_ato",
            "彼はスマホの通知を消したあとに、静かに机へ戻った。",
            "彼はスマホの通知を消した後に、静かに机へ戻った。",
        ),
        (
            "synthetic_go_nochi",
            "彼はこのとき無名だったが、後に大きな発見をした研究者として知られるようになった。",
            "彼はこのとき無名だったが、のちに大きな発見をした研究者として知られるようになった。",
        ),
    ]
    cases.extend(synthetic_cases)

    results = {}
    for case_id, canonical_text, asr_text in cases:
        t0 = time.time()
        r = run_case(case_id, canonical_text, asr_text, resolver_log)
        r["elapsed_seconds"] = round(time.time() - t0, 2)
        results[case_id] = r
        print(case_id, "mech_match=", r["mechanical_match"], "resolved_match=", r["resolved_match"],
              "calls=", r["total_resolver_calls"])

    with open(f"{OUT_DIR}/resolver_trial_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/resolver_call_log.json", "w", encoding="utf-8") as f:
        json.dump(resolver_log, f, ensure_ascii=False, indent=2)

    print("done. resolver total calls:", sum(r["total_resolver_calls"] for r in results.values()))


if __name__ == "__main__":
    main()
