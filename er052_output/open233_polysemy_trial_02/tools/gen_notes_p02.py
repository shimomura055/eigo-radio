# -*- coding: utf-8 -*-
"""gen_notes_p02: 多義語注意notes生成(DEV/Trial専用、Production非接続)。
入力draft/verificationを固定し、notes_for_writerへ決定論的に連結する(他フィールド不変)。
LLM出力は{fact_id, note, source_quote, source_url}のみ。既存notesは書き換えさせない。"""
import argparse, copy, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PREFIX = "注意(多義): "
MAX_LEN = 80
AMBIG_NOTE = PREFIX + "原資料も曖昧。断定しない。"
SEP = " / "
DEFAULT_BUDGET_JPY = 5.0

RULES = """1. 取り違えると事実が逆・反対になる表現(撤回/復元・状態変化・方向・因果・主体・対象・時系列・完了か予定か)に限り、1 factあたり1件まで付ける。該当しなければ付けない。
2. 形式「注意(多義): 原語'<英語原表現>'=<原資料が示す意味(何が・何の状態へ)>。<逆の読み>ではない。」
3. 原資料で確定できない場合は「原資料も曖昧。断定しない」とだけ書く。
4. 80字以内・改行なし・他フィールドは変えない。
5. 「高確度」とは、注意深い読者でも現実に採りうる逆の読みが存在し、その読みを採ると事実が逆転または重大変質する場合のみ。単に抽象的・要約的・多義な語があるだけでは対象外。数値の分母、程度、仮定、評価語、hedge表現(may/could/reportedly等)は対象外。
6. 各候補には、逆の読みを1文で書いた reverse_reading と、重大度 severity(1=軽微〜3=事実が完全に逆転)を必ず付ける。
7. 該当が無ければ空配列を返す。無理に見つけない。典型的な台帳では0〜3件程度であり、多数付けるのは過剰である。"""

PROMPT_TEMPLATE = """あなたはFact台帳の注意書き(notes)作成担当です。下記のFact一覧について、Writerが原語の多義性を誤読すると事実の方向・状態・主体・対象・時系列・因果等が逆転または重大変質する、高確度のFactにだけ注意書きを1件付けてください。該当しないFactには何も付けず、該当なしなら空配列を返してください。

【規則】
{rules}

【検索の制限】
Web検索は、各Factのsource_url(下記にあるもの)およびverification_notes内に現れるURLの原資料の確認に限定してください。それ以外の探索的検索はしないでください。

【出力】
JSONのみ。{{"notes":[{{"fact_id":..,"note":..,"source_quote":..,"source_url":..,"reverse_reading":..,"severity":1〜3の整数}}]}}。source_quoteは原資料の英語原表現(見つからなければ空文字。その場合noteは「注意(多義): 原資料も曖昧。断定しない。」の形にする)。

【Fact一覧】
{facts_json}"""

NOTES_SCHEMA = {
    "name": "polysemy_notes",
    "schema": {
        "type": "object",
        "properties": {"notes": {"type": "array", "items": {
            "type": "object",
            "properties": {**{k: {"type": "string"} for k in ("fact_id", "note", "source_quote", "source_url", "reverse_reading")},
                           "severity": {"type": "integer"}},
            "required": ["fact_id", "note", "source_quote", "source_url", "reverse_reading", "severity"],
            "additionalProperties": False}}},
        "required": ["notes"], "additionalProperties": False},
    "strict": True,
}
DEV_MSG = "あなたはFact台帳の多義語注意notes作成担当です。台帳本文は変更せず、注意書きだけを返してください。"


def sha256(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def build_prompt(draft, verif):
    vmap = {v["fact_id"]: v for v in verif["verifications"]}
    items = []
    for f in draft["facts"]:
        v = vmap.get(f["fact_id"], {})
        if v.get("verdict") == "REJECTED":
            continue
        items.append({"fact_id": f["fact_id"], "claim": f["claim"], "source_url": f.get("source_url"),
                      "notes_for_writer": f.get("notes_for_writer"),
                      "verification_notes": v.get("verification_notes")})
    return PROMPT_TEMPLATE.format(rules=RULES, facts_json=json.dumps(items, ensure_ascii=False, indent=1))


def validate_note(note):
    """違反理由を返す(OKならNone)。"""
    if not isinstance(note, str) or not note:
        return "empty"
    if "\n" in note or "\r" in note:
        return "newline"
    if not note.startswith(PREFIX):
        return "bad_prefix"
    if len(note) > MAX_LEN:
        return "too_long(%d)" % len(note)
    return None


def postprocess(raw_notes, fact_ids):
    """1 fact 1件・形式検証。戻り: (accepted{fid:note}, rejected[list])"""
    acc, rej = {}, []
    for n in raw_notes:
        fid, note = n.get("fact_id"), (n.get("note") or "").strip()
        if fid not in fact_ids:
            why = "unknown_fact_id"
        elif fid in acc:
            why = "duplicate_for_fact"
        else:
            why = validate_note(note)
        if why:
            rej.append({"fact_id": fid, "note": n.get("note"), "reason": why})
        else:
            acc[fid] = note
    return acc, rej


def trim_notes(raw_notes, accepted, fact_order, max_notes):
    """severity降順(同点は台帳先頭fact優先)で上限max_notes件に切る。戻り: (kept{fid:note}, trimmed[list])"""
    if max_notes is None or len(accepted) <= max_notes:
        return dict(accepted), []
    sev = {}
    for n in raw_notes:
        if n.get("fact_id") in accepted and n.get("fact_id") not in sev:
            try:
                sev[n["fact_id"]] = int(n.get("severity") or 0)
            except (TypeError, ValueError):
                sev[n["fact_id"]] = 0
    pos = {f: i for i, f in enumerate(fact_order)}
    ranked = sorted(accepted, key=lambda f: (-sev.get(f, 0), pos.get(f, 10**9)))
    keep = set(ranked[:max_notes])
    kept = {f: accepted[f] for f in accepted if f in keep}
    trimmed = [{"fact_id": f, "note": accepted[f], "severity": sev.get(f, 0)} for f in ranked[max_notes:]]
    return kept, trimmed


def concat_notes(draft, accepted):
    """notes_for_writerのみ変更した新draftを返す(deepcopy)。"""
    out = copy.deepcopy(draft)
    for f in out["facts"]:
        note = accepted.get(f["fact_id"])
        if note:
            ex = f.get("notes_for_writer")
            f["notes_for_writer"] = (ex + SEP + note) if ex else note
    return out


def _vfl():
    sys.path.insert(0, str(ROOT))
    import er003_v1_en_direct_vfl_01_generate as vfl01
    return vfl01


def rebuild_ledger_text(draft, verif):
    txt, counts, _ = _vfl().build_verified_ledger_text(draft, verif)
    return txt, counts


def draft_from_ledger_txt(path):
    """fallback: txtから擬似draft/verifを作る(再構築一致は保証しない)。"""
    sys.path.insert(0, str(ROOT / "er052_output" / "open233_ledger_clarity_p_trial_01" / "tools"))
    import ledger_diff_p01 as L
    B, order, _ = L.parse(path)
    facts, vs = [], []
    for fid in order:
        b = B[fid]
        k = b["keys"]
        facts.append({"fact_id": fid, "claim": b["claim"], "scope": k.get("scope"), "conditions": k.get("conditions"),
                      "numeric_value": None, "numeric_scope": None, "date_or_period": k.get("date_or_period"),
                      "causal_strength": k.get("causal_strength", "NOT_APPLICABLE"), "ambiguity": k.get("ambiguity_note"),
                      "notes_for_writer": k.get("notes_for_writer"), "source_url": None})
        vs.append({"fact_id": fid, "verdict": "VERIFIED" if b["tag"] == "VERIFIED" else "AMBIGUOUS", "verification_notes": ""})
    return {"facts": facts}, {"verifications": vs}


def append_notes_to_txt(text, accepted):
    """元txtへ決定論追記(txt追記方式)。notes_for_writer行末に' / <note>'、行が無ければfactブロック末尾へ
    '  notes_for_writer: <note>'を追加。他行は一切変更しない。戻り: (新text, 追記されたfact_id list)"""
    import re
    head = re.compile(r"^\[(?P<tag>[^\]]*)\]\s*(?P<id>[^:\s]+):")
    lines = text.split("\n")
    out, i, done = [], 0, []
    while i < len(lines):
        m = head.match(lines[i])
        if not m:
            out.append(lines[i]); i += 1; continue
        fid = m["id"]
        j = i
        while j < len(lines) and lines[j].strip() != "":
            j += 1
        block = lines[i:j]
        note = accepted.get(fid)
        if note:
            idx = next((k for k, ln in enumerate(block) if re.match(r"^\s+notes_for_writer:", ln)), None)
            if idx is not None:
                eol = "\r" if block[idx].endswith("\r") else ""
                block[idx] = block[idx][:len(block[idx]) - len(eol)] + SEP + note + eol
            else:
                eol = "\r" if block[-1].endswith("\r") else ""
                block.append("  notes_for_writer: " + note + eol)
            done.append(fid)
        out.extend(block)
        i = j
    return "\n".join(out), done


def call_llm(prompt):
    sys.path.insert(0, str(ROOT))
    from dotenv import load_dotenv
    load_dotenv()
    vfl01 = _vfl()
    import er003_v1_n3_01_advanced_adaptation_generate as g
    client = vfl01.get_client()
    r = client.responses.create(
        model=vfl01.MODEL, reasoning={"effort": vfl01.REASONING_EFFORT}, tools=[{"type": "web_search"}],
        text={"format": {"type": "json_schema", **NOTES_SCHEMA}},
        input=[{"role": "developer", "content": DEV_MSG}, {"role": "user", "content": prompt}])
    u = r.usage
    cached = getattr(getattr(u, "input_tokens_details", None), "cached_tokens", 0) or 0
    _, jpy = g._compute_cost_jpy(g._load_pricing(), vfl01.MODEL, u.input_tokens, cached, u.output_tokens)
    usage = vfl01.r3.extract_web_search_usage(r)
    return {"parsed": json.loads(r.output_text), "model": r.model, "response_id": r.id, "cost_jpy": jpy,
            "search_usage": usage, "input_tokens": u.input_tokens, "output_tokens": u.output_tokens}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft")
    ap.add_argument("--verif")
    ap.add_argument("--ledger-txt")
    ap.add_argument("--append-to-txt", help="元txt(出力台帳は必ずこのtxtベース。nb=決定論追記、control=バイトコピー)")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--budget-jpy", type=float, default=DEFAULT_BUDGET_JPY)
    ap.add_argument("--reuse-raw", action="store_true", help="既存notes_raw_response.json/notes_provenance.jsonを再利用しLLMを再呼び出ししない(再適用のみ、¥0)")
    ap.add_argument("--max-notes", type=int, default=None, help="1台帳あたりの付与上限(severity降順・同点は先頭fact優先)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    if a.append_to_txt:
        draft, verif = draft_from_ledger_txt(a.append_to_txt)
        src = "append_to_txt(facts from txt)"
        if a.draft and a.verif:
            d2 = json.loads(Path(a.draft).read_text(encoding="utf-8"))
            v2 = json.loads(Path(a.verif).read_text(encoding="utf-8"))
            tids = {f["fact_id"] for f in draft["facts"]}
            d2["facts"] = [f for f in d2["facts"] if f["fact_id"] in tids]
            draft_ctx, verif_ctx = d2, v2
            src += "+draft/verif context"
        else:
            draft_ctx, verif_ctx = draft, verif
        prompt = build_prompt(draft_ctx, verif_ctx)
        (out / "notes_prompt.txt").write_text(prompt, encoding="utf-8")
        orig_bytes = Path(a.append_to_txt).read_bytes()
        orig_text = orig_bytes.decode("utf-8")
        (out / "verified_fact_ledger_control.txt").write_bytes(orig_bytes)
        result = {"input_source": src, "append_to_txt": str(a.append_to_txt), "prompt_sha256": sha256(prompt),
                  "control_sha256": hashlib.sha256(orig_bytes).hexdigest(), "dry_run": a.dry_run, "budget_jpy": a.budget_jpy}
        if a.dry_run:
            print(json.dumps(result, ensure_ascii=False)); return 0
        if a.reuse_raw:
            prev = json.loads((out / "notes_provenance.json").read_text(encoding="utf-8"))
            res = {"parsed": json.loads((out / "notes_raw_response.json").read_text(encoding="utf-8")),
                   **{k: prev[k] for k in ("model", "response_id", "cost_jpy", "search_usage")}}
        else:
            res = call_llm(prompt)
        fids = {f["fact_id"] for f in draft["facts"]}
        acc, rej = postprocess(res["parsed"].get("notes", []), fids)
        cand_count = len(acc)
        acc, trimmed = trim_notes(res["parsed"].get("notes", []), acc, [f["fact_id"] for f in draft["facts"]], a.max_notes)
        (out / "trimmed.json").write_text(json.dumps(trimmed, ensure_ascii=False, indent=2), encoding="utf-8")
        nbtxt, done = append_notes_to_txt(orig_text, acc)
        (out / "verified_fact_ledger_nb.txt").write_bytes(nbtxt.encode("utf-8"))
        (out / "rejected.json").write_text(json.dumps(rej, ensure_ascii=False, indent=2), encoding="utf-8")
        (out / "notes_raw_response.json").write_text(json.dumps(res["parsed"], ensure_ascii=False, indent=2), encoding="utf-8")
        srcmap = {n.get("fact_id"): n for n in res["parsed"].get("notes", [])}
        result.update({"model": res["model"], "response_id": res["response_id"], "cost_jpy": res["cost_jpy"],
                       "search_usage": res["search_usage"], "attached_facts": sorted(acc), "attached_count": len(acc),
                       "candidate_count_before_cap": cand_count, "trimmed_count": len(trimmed), "max_notes": a.max_notes,
                       "appended_facts": done, "rejected_count": len(rej), "over_budget": res["cost_jpy"] > a.budget_jpy,
                       "nb_sha256": sha256(nbtxt),
                       "source_quotes": {f: {"source_quote": srcmap[f].get("source_quote"), "source_url": srcmap[f].get("source_url"),
                                             "reverse_reading": srcmap[f].get("reverse_reading"), "severity": srcmap[f].get("severity")} for f in acc}})
        (out / "notes_provenance.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        tbl = ["| fact_id | note | source_quote |", "|---|---|---|"] + ["| %s | %s | %s |" % (f, acc[f], srcmap[f].get("source_quote") or "(なし)") for f in sorted(acc)]
        (out / "notes_table.md").write_text("\n".join(tbl), encoding="utf-8")
        print(json.dumps({k: result[k] for k in ("cost_jpy", "attached_count", "rejected_count", "over_budget")}))
        return 0
    if a.draft and a.verif:
        draft = json.loads(Path(a.draft).read_text(encoding="utf-8"))
        verif = json.loads(Path(a.verif).read_text(encoding="utf-8"))
        src = "draft+verif"
    elif a.ledger_txt:
        draft, verif = draft_from_ledger_txt(a.ledger_txt)
        src = "ledger_txt_fallback"
    else:
        ap.error("--draft/--verif か --ledger-txt が必要")
    prompt = build_prompt(draft, verif)
    (out / "notes_prompt.txt").write_text(prompt, encoding="utf-8")
    control, counts = rebuild_ledger_text(draft, verif)
    (out / "verified_fact_ledger_control.txt").write_text(control, encoding="utf-8")
    result = {"input_source": src, "prompt_sha256": sha256(prompt), "control_sha256": sha256(control),
              "verdict_counts": counts, "dry_run": a.dry_run, "budget_jpy": a.budget_jpy}
    if a.draft:
        orig = Path(a.draft).parent / "verified_fact_ledger.txt"
        if orig.exists():
            result["control_matches_original"] = sha256(orig.read_text(encoding="utf-8")) == result["control_sha256"]
            result["original_path"] = str(orig)
    if a.dry_run:
        (out / "notes_provenance_dryrun.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False))
        return 0
    res = call_llm(prompt)
    fids = {f["fact_id"] for f in draft["facts"]}
    acc, rej = postprocess(res["parsed"].get("notes", []), fids)
    nb = concat_notes(draft, acc)
    (out / "draft_nb.json").write_text(json.dumps(nb, ensure_ascii=False, indent=2), encoding="utf-8")
    nbtxt, _ = rebuild_ledger_text(nb, verif)
    (out / "verified_fact_ledger_nb.txt").write_text(nbtxt, encoding="utf-8")
    (out / "rejected.json").write_text(json.dumps(rej, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "notes_raw_response.json").write_text(json.dumps(res["parsed"], ensure_ascii=False, indent=2), encoding="utf-8")
    result.update({"model": res["model"], "response_id": res["response_id"], "cost_jpy": res["cost_jpy"],
                   "search_usage": res["search_usage"], "attached_facts": sorted(acc), "attached_count": len(acc),
                   "rejected_count": len(rej), "over_budget": res["cost_jpy"] > a.budget_jpy})
    (out / "notes_provenance.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("cost_jpy", "attached_count", "rejected_count", "over_budget")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
