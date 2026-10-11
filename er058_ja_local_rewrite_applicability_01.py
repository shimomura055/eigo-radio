# -*- coding: utf-8 -*-
"""委任_04D 作業5: 日本語Local Rewrite適用性Trial(Trial専用、TTS生成なし、Production非経由)。
既存LR(er020)の候補生成promptを日本語向けに最小限だけ適応し、Phase 0/SCGの日本語NG実例5件で候補文を各1回生成(n=3候補)。
機械チェック(原稿差分・Fact語保持)を行う。Production telemetry/queue/Master Storeへ書かない。
モデル: Production LRと同一(routing.WRITER_MODEL=gpt-6-luna、reasoning=Production同一)。費用上限JPY3。"""
import os, sys, json, re, difflib
sys.path.insert(0, os.getcwd())
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = f"{ROOT}/er058_output/ja_local_rewrite_applicability_01"
os.makedirs(OUT, exist_ok=True)
import er020_tts_retry_local_rewrite_01 as lr
import er003_v1_b1_scaffold_01_generate as b1s

CASES = [
    {"id": "g8", "role": "KEY_PHRASE(JA意味、LR対象外role)", "type": "読み(熟->じく)+濁点(ガ->カ)",
     "canonical": "熟すと出るガス", "asr": "じくすと出るカス。", "note": "Azure/whisperは正解転写。TTSは正しかった可能性が高い(Primary誤認)"},
    {"id": "g5", "role": "KEY_PHRASE(JA意味、LR対象外role)", "type": "同形異音語/漢字誤認(所->勝、程->亭)",
     "canonical": "名所を中心にした旅程", "asr": "名勝を中心にした旅亭。", "note": "SCGでC2(heterophone)除外された例"},
    {"id": "g6", "role": "KEY_PHRASE(JA意味、LR対象外role)", "type": "脱落(なり)",
     "canonical": "形になり始める", "asr": "形に始める。", "note": "Primary/Azureとも「形に始める」(真の脱落の可能性)"},
    {"id": "g21", "role": "COMMENT(LR対象role)", "type": "数詞表記(二->2)+固有語誤認(続き->鈴木)",
     "canonical": "世界市場の価格は下がりましたが、米国のコーヒー価格は前年同月より高いままでした。この二つは比べる期間が違い、豆の値下がりが店頭価格に表れるまでには時間がかかります。こうした違いをふまえて、続きに耳を傾けてみましょう。",
     "asr": "世界市場の価格は下がりましたが、米国のコーヒー価格は前年同月より高いままでした。この2つは比べる期間が違い、豆の値下がりが店頭価格に表れるまでには時間がかかります。こうした違いを踏まえて、鈴木に耳を傾けてみましょう。",
     "note": "Azureは「続き」を正しく転写。Production方式の「最初のdiff」は表記差(二->2)を選ぶ"},
    {"id": "g36", "role": "COMMENT(LR対象role)", "type": "記号読み(％->パーセント)",
     "canonical": "まず、20％という計画が発表されたあと、支払い方法など何がまだ決まっていなかったのかに注目してください。",
     "asr": "まず、20パーセントという計画が発表された後、支払い方法など何がまだ決まっていなかったのかに注目してください。",
     "note": "表記差のみ(TTSは正しい)。Azure=20%"},
]

SYSTEM = (
    "You are a careful audio-script editor for a Japanese-language podcast segment. "
    "You are given a short spoken JAPANESE segment and a specific short span inside it that a speech recognizer keeps mis-transcribing "
    "(the canonical text and what the recognizer actually heard are both given to you). "
    "Propose exactly {n} different LOCAL rewrite candidates for the minimal problematic span only, NOT a rewrite of the whole segment. Each candidate must: "
    "(a) avoid the exact wording that keeps causing the ASR mismatch; (b) preserve the exact original meaning; (c) preserve the segment's role: {role}; "
    "(d) sound like natural, idiomatic spoken Japanese that a native speaker would actually say in this context (keep the register: polite/plain, same as the segment); "
    "(e) change only the minimal span needed; (f) introduce no new fact and drop no existing fact, and keep all numbers, names and key content words unchanged. "
    "CRITICAL FORMAT REQUIREMENT: 'rewritten_segment' MUST be the ENTIRE original segment reproduced VERBATIM character-for-character with ONLY the problem span replaced. "
    "'changed_span_before' is the exact original phrase replaced (a substring of the segment); 'changed_span_after' is the replacement wording. "
    "Return STRICT JSON only via the provided schema."
)


def schema(n):
    return {"name": "ja_local_rewrite_candidates_trial", "strict": True, "schema": {"type": "object", "additionalProperties": False, "required": ["candidates"], "properties": {
        "candidates": {"type": "array", "minItems": n, "maxItems": n, "items": {"type": "object", "additionalProperties": False,
            "required": ["id", "rewrite_type", "rewritten_segment", "changed_span_before", "changed_span_after", "rationale"], "properties": {
            "id": {"type": "string"}, "rewrite_type": {"type": "string", "enum": ["single_word_swap", "short_phrase_rewrite"]},
            "rewritten_segment": {"type": "string"}, "changed_span_before": {"type": "string"}, "changed_span_after": {"type": "string"},
            "rationale": {"type": "string"}}}}}}}


PUNCT = "。、．，！？!?「」『』（）() 　"


def norm(t):
    return "".join(c for c in t if c not in PUNCT)


def ja_ng_span(canon, asr, ctx=3):
    """日本語用(文字単位)のNG span特定。Production identify_ng_spanと同じ『最初のdiff op + 前後context』方式の文字版(Trial用)。"""
    a, b = norm(canon), norm(asr)
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    ops = [o for o in sm.get_opcodes() if o[0] != "equal"]
    if not ops:
        return {"found": False}
    out = []
    for tag, i1, i2, j1, j2 in ops:
        out.append({"tag": tag, "canon": a[i1:i2], "asr": b[j1:j2], "range": [i1, i2], "ctx": a[max(0, i1 - ctx):i2 + ctx]})
    return {"found": True, "first": out[0], "all": out}


NUM_RE = re.compile(r"\d+(?:[.,]\d+)?|[〇一二三四五六七八九十百千万億]+")
RUN_RE = re.compile(r"[一-鿿]+|[゠-ヿ]+|[A-Za-z]+|\d+")


def machine_checks(canon, cand, before, after, ng):
    ratio_chars = difflib.SequenceMatcher(None, canon, cand, autojunk=False).ratio()
    sm = difflib.SequenceMatcher(None, canon, cand, autojunk=False)
    ops = [o for o in sm.get_opcodes() if o[0] != "equal"]
    unchanged = sum(b.size for b in sm.get_matching_blocks()) / max(1, len(canon))
    changed_chars = sum(max(o[2] - o[1], o[4] - o[3]) for o in ops)
    # 申告span整合(日本語は空白分割ができないため文字列として原文1箇所に適用した結果が候補全文と一致するか)
    span_ok = bool(before) and canon.count(before) >= 1 and any(canon[:i] + after + canon[i + len(before):] == cand for i in [m.start() for m in re.finditer(re.escape(before), canon)])
    # 局所性: 変更範囲が最初のNG spanの前後window内か(Production同様 ±window。ここでは文字±6)
    loc = None
    if ng.get("found"):
        lo, hi = ng["first"]["range"]
        # canon(punct除去)座標ではなく原文座標でbeforeの位置を使う
        pos = canon.find(before) if before else -1
        loc = {"before_pos": pos}
    # Fact語保持: 原文の数詞・漢字/カタカナ連続語のうち、changed_span_beforeに含まれないものが候補に残るか
    keep_src = canon.replace(before, "\u0000", 1) if before else canon
    need = [r for r in RUN_RE.findall(keep_src)]
    missing = [r for r in need if r not in cand]
    nums_src = sorted(NUM_RE.findall(keep_src))
    nums_cand = sorted(NUM_RE.findall(cand.replace(after, "\u0000", 1) if after else cand))
    return {"char_unchanged_ratio": round(unchanged, 3), "changed_chars": changed_chars, "length_ratio": round(len(cand) / len(canon), 3),
            "span_declaration_consistent": span_ok, "missing_content_runs_outside_span": missing,
            "numbers_outside_span_preserved": nums_src == nums_cand,
            "terminal_punct_same": canon[-1:] == cand[-1:], "identical_to_original": cand == canon,
            "before_in_original": (before in canon) if before else False}


def reading(t):
    try:
        import pykakasi
        kks = pykakasi.kakasi()
        return "".join(x["hira"] for x in kks.convert(t))
    except Exception as e:
        return f"(n/a:{e})"


def main():
    client = b1s.get_client()
    n = 3
    res = []
    tin = tout = 0
    for c in CASES:
        ng = ja_ng_span(c["canonical"], c["asr"])
        # (1) 既存英語LR実装を日本語入力へそのまま使うとどうなるか(機械的流用の影響)
        eng = {"identify_ng_span_found": lr.identify_ng_span(c["canonical"], c["asr"]).get("found"),
               "compute_unchanged_ratio_self": lr.compute_unchanged_ratio(c["canonical"], c["canonical"]),
               "compute_unchanged_ratio_near": lr.compute_unchanged_ratio(c["canonical"], c["canonical"].replace(c["canonical"][2:4], "X" if len(c["canonical"]) > 5 else "")) }
        span_txt = ng["first"]["ctx"] if ng.get("found") else ""
        prompt = (f"Segment role: {c['role']}\n\nFull segment (contains the problem span):\n\"{c['canonical']}\"\n\n"
                  f"Problem span (a speech recognizer repeatedly mis-transcribes it; it heard {ng['first']['asr']!r} instead of {ng['first']['canon']!r}):\n\"{span_txt}\"\n\n"
                  "Propose the candidates as described in the system instructions. Return the JSON object.")
        resp = client.responses.create(model=b1s.MODEL, reasoning={"effort": b1s.REASONING_EFFORT},
                                       text={"format": {"type": "json_schema", **schema(n)}},
                                       input=[{"role": "developer", "content": SYSTEM.format(n=n, role=c["role"])}, {"role": "user", "content": prompt}])
        u = resp.usage
        tin += u.input_tokens
        tout += u.output_tokens
        cands = json.loads(resp.output_text)["candidates"]
        recs = []
        for k in cands:
            mc = machine_checks(c["canonical"], k["rewritten_segment"], k["changed_span_before"], k["changed_span_after"], ng)
            recs.append({**k, "checks": mc, "reading_before": reading(k["changed_span_before"]), "reading_after": reading(k["changed_span_after"]),
                         "en_full_segment_gate": lr.diagnose_candidate_full_segment(c["canonical"], k["rewritten_segment"], changed_span_before=k["changed_span_before"],
                                                                                    changed_span_after=k["changed_span_after"], check_span=True),
                         "en_unchanged_ratio_gate7": lr.compute_unchanged_ratio(c["canonical"], k["rewritten_segment"])})
        res.append({**c, "ng_span_ja": ng, "existing_en_funcs_on_ja": eng, "model_returned": resp.model, "candidates": recs, "usage": {"in": u.input_tokens, "out": u.output_tokens}})
        usd = tin * 0.10 / 1e6 + tout * 0.50 / 1e6
        print(c["id"], "tokens", u.input_tokens, u.output_tokens, "cum JPY", round(usd * 160, 2), flush=True)
        if usd * 160 > 2.2:
            print("cost guard stop"); break
    usd = tin * 0.10 / 1e6 + tout * 0.50 / 1e6
    cost = {"model_requested": b1s.MODEL, "reasoning_effort": b1s.REASONING_EFFORT, "calls": len(res), "input_tokens": tin, "output_tokens": tout,
            "est_usd": round(usd, 6), "est_jpy": round(usd * 160, 3), "basis": "gpt-6-luna 単価 $0.10/$0.50 per 1M(routing/pricing_snapshot登録値)、USD_JPY=160。請求画面未確認"}
    json.dump({"cases": res, "cost": cost}, open(f"{OUT}/ja_lr_trial_results.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(cost)


if __name__ == "__main__":
    main()
