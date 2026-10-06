# -*- coding: utf-8 -*-
"""gen_notes_p03: 多義語注意Note自動生成の要素Trial用ハーネス(DEV/Trial専用、Production非接続)。
gen_notes_p02の後処理/txt追記/LLM基盤を流用し、patterns/<name>/のpromptで一体型/2段階型を切替える。
対象fact_idはprompt・生成ロジックに一切含めない(評価はeval_notes_p03.pyのtargets.jsonのみ)。"""
import argparse, hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRIAL = HERE.parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "er052_output" / "open233_polysemy_trial_02" / "tools"))
import gen_notes_p02 as P02  # noqa: E402

DEFAULT_PREFIX = P02.PREFIX
DEFAULT_MAX_CHARS = 120
DEV_MSG = "あなたはFact台帳の多義語注意notes作成担当です。台帳本文は変更せず、指示されたJSONのみを返してください。"


def sha256(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def load_pattern(name, base=None):
    d = Path(base or TRIAL / "patterns") / name
    s1 = d / "stage1_prompt.txt"
    if not s1.exists():
        raise FileNotFoundError("stage1_prompt.txt required: %s" % s1)
    rd = lambda n: (d / n).read_text(encoding="utf-8") if (d / n).exists() else None
    prefix = rd("prefix.txt")
    meta = json.loads(rd("pattern.json")) if (d / "pattern.json").exists() else {}
    stage2 = rd("stage2_prompt.txt")
    stage1_5 = rd("stage1_5_prompt.txt")
    mode = meta.get("mode") or ("twostage" if stage2 else "onepass")
    return {"name": name, "stage1": rd("stage1_prompt.txt"), "stage2": stage2, "mode": mode,
            "stage1_5": stage1_5, "stage1_repeats": int(meta.get("stage1_repeats", 1)),
            "max_chars": meta.get("max_chars"), "fallback": meta.get("fallback"),
            "self_check_policy": meta.get("self_check_policy", "both"),
            "stage2_existing_notes": bool(meta.get("stage2_existing_notes", True)),
            "examples": (rd("examples.txt") or "").strip("\n"),
            "prefix": prefix.rstrip("\r\n") if prefix is not None else DEFAULT_PREFIX}


def fact_items(draft, verif, include_existing_notes=True):
    vmap = {v["fact_id"]: v for v in verif["verifications"]}
    items = []
    for f in draft["facts"]:
        v = vmap.get(f["fact_id"], {})
        if v.get("verdict") == "REJECTED":
            continue
        it = {"fact_id": f["fact_id"], "claim": f["claim"], "scope": f.get("scope"), "conditions": f.get("conditions"),
              "date_or_period": f.get("date_or_period"), "source_url": f.get("source_url"),
              "notes_for_writer": f.get("notes_for_writer"), "verification_notes": v.get("verification_notes")}
        if not include_existing_notes:
            it.pop("notes_for_writer")  # ablation: 既存notes_for_writerを入力から除く
        items.append(it)
    return items


def format_facts(items):
    return json.dumps(items, ensure_ascii=False, indent=1)


def fill_prompt(tmpl, items, max_chars, examples="", candidates=None):
    """プレースホルダを単純置換(JSON波括弧と衝突しないようstr.replace)。LEDGER_FACTSは最後に置換(factsの中身を再置換しない)。"""
    out = tmpl.replace("{MAX_CHARS}", str(max_chars)).replace("{EXAMPLES}", examples or "")
    if candidates is not None:
        out = out.replace("{CANDIDATES}", json.dumps(candidates, ensure_ascii=False, indent=1))
    return out.replace("{LEDGER_FACTS}", format_facts(items))


def is_two_stage(pat):
    return bool(pat.get("stage2")) or pat.get("mode") in ("twostage", "twostage_gate")


def validate_note(note, prefix, max_chars):
    if not isinstance(note, str) or not note:
        return "empty"
    if "\n" in note or "\r" in note:
        return "newline"
    if not note.startswith(prefix):
        return "bad_prefix"
    if len(note) > max_chars:
        return "too_long(%d)" % len(note)
    return None


_WS = " 　	"


def normalize_prefix(note, prefix):
    """H1: 接頭辞比較を空白正規化(全角/半角空白・末尾空白を無視)。接頭辞が一致すれば、
    接頭辞直後の空白はコード側で正規化(prefix自身の末尾空白に統一)して返す。不一致は原文のまま。"""
    if not isinstance(note, str):
        return note
    p = prefix.strip(_WS)
    n = note.lstrip(_WS)
    if p and n.startswith(p):
        trail = prefix[len(prefix.rstrip(_WS)):]
        return prefix.rstrip(_WS) + trail + n[len(p):].lstrip(_WS)
    return note


def postprocess(raw_notes, fact_ids, prefix, max_chars):
    acc, rej = {}, []
    for n in raw_notes:
        fid, note = n.get("fact_id"), normalize_prefix((n.get("note") or "").strip(), prefix)
        if fid not in fact_ids:
            why = "unknown_fact_id"
        elif fid in acc:
            why = "duplicate_for_fact"
        else:
            why = validate_note(note, prefix, max_chars)
        if why:
            rej.append({"fact_id": fid, "note": n.get("note"), "reason": why})
        else:
            acc[fid] = note
    return acc, rej


def select_candidates(cands, fact_ids, max_notes=None):
    """stage1候補を既知factに限定・重複除去し、max_notesがあればseverity降順で切る。"""
    seen, out = set(), []
    for c in cands:
        fid = c.get("fact_id")
        if fid in fact_ids and fid not in seen:
            seen.add(fid)
            out.append(c)
    if max_notes is not None and len(out) > max_notes:
        pos = {c["fact_id"]: i for i, c in enumerate(out)}
        out = sorted(out, key=lambda c: (-int(c.get("severity") or 0), pos[c["fact_id"]]))[:max_notes]
    return out


def _norm(s):
    return "".join((s or "").split())


def quote_in_ledger(quote, item):
    """ledger_quoteが当該factのclaim/scope/conditionsに(空白正規化で)部分一致するか。空は不一致。"""
    q = _norm(quote)
    if not q:
        return False
    return any(q in _norm(item.get(k)) for k in ("claim", "scope", "conditions"))


def onepass_pass(j, item):
    """A_onepassのpass_rule(コード側評価)。(通過bool, 落ちた条件のリスト)を返す。"""
    why = []
    if j.get("reversible") is not True:
        why.append("reversible=false")
    if (j.get("flipped_component") or "none") == "none":
        why.append("flipped_component=none")
    if (j.get("contradicts_ledger_field") or "none") == "none":
        why.append("contradicts_ledger_field=none")
    if j.get("changes_conclusion") is not True:
        why.append("changes_conclusion=false")
    if not quote_in_ledger(j.get("ledger_quote"), item):
        why.append("ledger_quote_not_in_ledger")
    if not (j.get("note") or "").strip():
        why.append("note_null")
    return (not why), why


def screen_pass(j, item):
    """B stage1通過条件: reversible && ledger_quoteが台帳に部分一致。"""
    return j.get("reversible") is True and quote_in_ledger(j.get("ledger_quote"), item)


def pick_reverse(j, item):
    """H3: reverse_propositions(最大2)から「changes_conclusion=trueのうち先頭(かつledger_quoteが台帳に部分一致)」を採用。
    (採用entry or None)。旧形式(reverse_proposition単体)には対応しない。"""
    for e in (j.get("reverse_propositions") or []):
        if isinstance(e, dict) and e.get("changes_conclusion") is True and quote_in_ledger(e.get("ledger_quote"), item):
            return e
    return None


def screen2(j, item):
    """reverse_propositions型のstage1通過条件。(ok, 落ちた条件, 採用entry)。"""
    if j.get("reversible") is not True:
        return False, ["reversible=false"], None
    e = pick_reverse(j, item)
    if e is None:
        props = [x for x in (j.get("reverse_propositions") or []) if isinstance(x, dict)]
        why = ["no_R_changes_conclusion"] if not any(x.get("changes_conclusion") is True for x in props) else ["ledger_quote_not_in_ledger"]
        return False, why, None
    return True, [], e


def _compact(s, n=40):
    return (s or "")[:n]


def build_s15_input(runs_cands):
    """H5/H6: stage1各回のscreen2通過entryの和集合を、fact_idごとの[{cid,compressed_claim,R}]にする(claim全文・scope・notesは渡さない)。
    runs_cands: [{fact_id: {"R","compressed_claim",...}}, ...] (run順)。同一R(空白正規化)は1つに統合。cidは出現順にA,B,..。"""
    order, per = [], {}
    for rc in runs_cands:
        for fid, e in rc.items():
            if fid not in per:
                per[fid] = []
                order.append(fid)
            if any(_norm(x["R"]) == _norm(e.get("R")) for x in per[fid]):
                continue
            per[fid].append({"cid": "ABCDEFG"[len(per[fid])], "compressed_claim": e.get("compressed_claim"), "R": e.get("R"), "_entry": e})
    return order, per


def s15_prompt_items(order, per):
    return [{"fact_id": fid, "candidates": [{k: c[k] for k in ("cid", "compressed_claim", "R")} for c in per[fid]]} for fid in order]


def apply_s15(order, per, verdicts):
    """H5: likelihood=highのRのみ通過(複数highなら出現順の先頭)。medium/low/欠落は落とす。
    戻り値: (採用entry map {fact_id: (cid, entry)}, 判定記録 {fact_id: {...}})"""
    vm = {}
    for v in verdicts or []:
        if isinstance(v, dict):
            vm[(v.get("fact_id"), str(v.get("cid") or "A"))] = v
    chosen, rec = {}, {}
    for fid in order:
        rows, pick, levels = [], None, []
        for c in per[fid]:
            v = vm.get((fid, c["cid"]))
            lv = (v.get("likelihood") if v else None)
            lv = lv if lv in ("high", "medium", "low") else "missing"
            levels.append(lv)
            rows.append({"cid": c["cid"], "R": c["R"], "likelihood": lv, "reason": (v or {}).get("reason")})
            if lv == "high" and pick is None:
                pick = c
        if pick is not None:
            chosen[fid] = (pick["cid"], pick["_entry"])
            why = []
        elif "medium" in levels:
            why = ["stage1_5_medium"]
        else:
            why = ["stage1_5_low" if "low" in levels else "stage1_5_missing"]
        rec[fid] = {"passed": pick is not None, "dropped_by": why, "verdicts": rows, "adopted_cid": pick["cid"] if pick else None}
    return chosen, rec


def jaccard(a, b):
    a, b = set(a), set(b)
    return (len(a & b) / len(a | b)) if (a | b) else 1.0


def call_llm(prompt, web_search="none"):
    sys.path.insert(0, str(ROOT))
    from dotenv import load_dotenv
    load_dotenv()
    vfl01 = P02._vfl()
    import er003_v1_n3_01_advanced_adaptation_generate as g
    client = vfl01.get_client()
    kw = {"tools": [{"type": "web_search"}]} if web_search == "url_only" else {}
    total, retried = 0.0, False
    while True:  # json_object。parse失敗時のみ1回再試行(費用は合算)
        r = client.responses.create(
            model=vfl01.MODEL, reasoning={"effort": vfl01.REASONING_EFFORT}, text={"format": {"type": "json_object"}},
            input=[{"role": "developer", "content": DEV_MSG}, {"role": "user", "content": prompt}], **kw)
        u = r.usage
        cached = getattr(getattr(u, "input_tokens_details", None), "cached_tokens", 0) or 0
        _, jpy = g._compute_cost_jpy(g._load_pricing(), vfl01.MODEL, u.input_tokens, cached, u.output_tokens)
        total += jpy
        try:
            parsed = json.loads(r.output_text)
            break
        except json.JSONDecodeError:
            if retried:
                raise
            retried = True
    return {"parsed": parsed, "model": r.model, "response_id": r.id, "cost_jpy": total, "parse_retried": retried,
            "search_usage": vfl01.r3.extract_web_search_usage(r) if kw else {"web_search_call_count": 0},
            "input_tokens": u.input_tokens, "output_tokens": u.output_tokens}


def _jdump(out, name, obj):
    (out / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def run_onepass(pat, items, max_chars, llm, web_search, out, tag="stage1"):
    """全fact判定→pass_ruleをコード側で評価。(raw_notes, judgments_all, llm結果, prompt)を返す。"""
    p1 = fill_prompt(pat["stage1"], items, max_chars, pat["examples"])
    (out / ("%s_prompt.txt" % tag)).write_text(p1, encoding="utf-8")
    r = llm(p1, web_search)
    _jdump(out, "%s_raw.json" % tag, r["parsed"])
    jmap = {j.get("fact_id"): j for j in (r["parsed"].get("judgments") or []) if isinstance(j, dict)}
    raw, jall = [], []
    for it in items:
        j = jmap.get(it["fact_id"])
        if j is None:
            jall.append({"fact_id": it["fact_id"], "passed": False, "dropped_by": ["judgment_missing"], "judgment": None})
            continue
        ok, why = onepass_pass(j, it)
        jall.append({"fact_id": it["fact_id"], "passed": ok, "dropped_by": why, "judgment": j})
        if ok:
            raw.append({"fact_id": it["fact_id"], "note": j.get("note"), "source_quote": j.get("ledger_quote"),
                        "reverse_reading": j.get("reverse_proposition"), "severity": None, "origin": pat["name"]})
    return raw, jall, r, p1


def run_gate(pat, items, fids, p1, a, llm, out, prov, max_chars):
    """B3(twostage_gate): stage1をstage1_repeats回 -> reversible通過の和集合 -> stage1.5(圧縮文+Rのみで読者誤読見込みhigh/medium/low) -> highのみstage2。
    予算ガードは「per-call」予算(累計費用 <= budget x 実行call数)。"""
    (out / "stage1_prompt.txt").write_text(p1, encoding="utf-8")
    reps = max(1, pat.get("stage1_repeats") or 1)
    imap = {i["fact_id"]: i for i in items}
    runs_c, runs_j, sets = [], [], []
    prov["calls"], prov["cost_jpy"] = 0, 0.0
    for k in range(reps):
        r1 = llm(p1, a.web_search)
        prov["calls"] += 1
        prov["cost_jpy"] += r1["cost_jpy"]
        prov["model"] = r1.get("model")
        _jdump(out, "stage1_raw_r%d.json" % (k + 1), r1["parsed"])
        jmap = {j.get("fact_id"): j for j in (r1["parsed"].get("judgments") or []) if isinstance(j, dict)}
        rc = {}
        for it in items:
            j = jmap.get(it["fact_id"])
            if j is None:
                continue
            if "reverse_propositions" in j:
                ok2, _, e = screen2(j, it)
                if ok2:
                    rc[it["fact_id"]] = {"R": e.get("R"), "compressed_claim": j.get("compressed_claim"), "source_quote": e.get("ledger_quote"),
                                         "flipped_component": e.get("flipped_component"), "conclusion_change_reason": e.get("conclusion_change_reason")}
            elif screen_pass(j, it):  # 旧形式(reverse_proposition単体)の互換
                rc[it["fact_id"]] = {"R": j.get("reverse_proposition"), "compressed_claim": j.get("compressed_claim"), "source_quote": j.get("ledger_quote"),
                                     "flipped_component": j.get("flipped_component"), "conclusion_change_reason": None}
        runs_c.append(rc)
        runs_j.append(jmap)
        sets.append(sorted(rc))
    prov["stage1_run_pass_sets"] = sets
    prov["stage1_jaccard"] = jaccard(sets[0], sets[1]) if len(sets) >= 2 else None
    order, per = build_s15_input(runs_c)
    prov["stage1_union_count"] = len(order)
    chosen, rec = {}, {}
    if order and prov["cost_jpy"] <= a.budget_jpy * prov["calls"]:
        p15 = pat["stage1_5"].replace("{S15_INPUT}", json.dumps(s15_prompt_items(order, per), ensure_ascii=False, indent=1))
        (out / "stage1_5_prompt.txt").write_text(p15, encoding="utf-8")
        r15 = llm(p15, a.web_search)
        prov["calls"] += 1
        prov["cost_jpy"] += r15["cost_jpy"]
        _jdump(out, "stage1_5_raw.json", r15["parsed"])
        chosen, rec = apply_s15(order, per, r15["parsed"].get("verdicts"))
    jall = []
    for it in items:
        fid = it["fact_id"]
        d = {"fact_id": fid, "passed": False, "dropped_by": [], "judgment": runs_j[0].get(fid) if runs_j else None,
             "stage1_run_pass": [fid in rc for rc in runs_c]}
        if reps >= 2:
            d["judgment_r2"] = runs_j[1].get(fid)
        if fid not in per:
            d["dropped_by"] = ["stage1_not_reversible_in_any_run"]
        else:
            x = rec.get(fid)
            if x is None:
                d["dropped_by"] = ["stage1_5_not_run"]
            else:
                d.update({"passed": x["passed"], "dropped_by": x["dropped_by"], "stage1_5": x["verdicts"]})
                if x["dropped_by"] == ["stage1_5_medium"]:
                    d["warnings"] = ["stage1_5_medium"]
        jall.append(d)
    prov["stage1_candidate_count"] = len(chosen)
    raw_notes, rejected_extra = [], []
    cands = []
    for fid in [i["fact_id"] for i in items if i["fact_id"] in chosen]:
        _, e = chosen[fid]
        cands.append({"fact_id": fid, "source_quote": e.get("source_quote"), "reverse_reading": e.get("R"),
                      "flipped_component": e.get("flipped_component"), "conclusion_change_reason": e.get("conclusion_change_reason")})
    cands = select_candidates(cands, set(fids), a.max_notes)
    if cands and prov["cost_jpy"] <= a.budget_jpy * prov["calls"]:
        sel = {c["fact_id"] for c in cands}
        s2_items = [dict(i) for i in items if i["fact_id"] in sel]
        if pat["stage2_existing_notes"]:
            for c in cands:
                c["existing_notes_hint"] = imap[c["fact_id"]].get("notes_for_writer")
        else:
            for i in s2_items:
                i.pop("notes_for_writer", None)
        p2 = fill_prompt(pat["stage2"], s2_items, max_chars, pat["examples"], cands)
        (out / "stage2_prompt.txt").write_text(p2, encoding="utf-8")
        r2 = llm(p2, a.web_search)
        prov["calls"] += 1
        prov["cost_jpy"] += r2["cost_jpy"]
        prov["stage2_prompt_sha256"] = sha256(p2)
        _jdump(out, "stage2_raw.json", r2["parsed"])
        cmap = {c["fact_id"]: c for c in cands}
        jmap2 = {j["fact_id"]: j for j in jall}
        for n in r2["parsed"].get("notes", []):
            c = cmap.get(n.get("fact_id"))
            if c is None:
                rejected_extra.append({"fact_id": n.get("fact_id"), "note": n.get("note"), "reason": "not_a_candidate"})
                continue
            sc = n.get("self_check") or {}
            warns = []
            ok = sc.get("correct_statement_derivable_from_ledger") is True  # derivable_only
            if n.get("note") and ok and sc.get("R_is_natural_reading") is not True:
                warns.append("R_is_natural_reading=false")
            if warns:
                jmap2[n["fact_id"]]["warnings"] = warns
            if n.get("note") and not ok:
                rejected_extra.append({"fact_id": n["fact_id"], "note": n.get("note"), "reason": "self_check_false"})
                jmap2[n["fact_id"]].update({"dropped_by": ["stage2_self_check_false"], "passed": False})
                continue
            if not n.get("note"):
                jmap2[n["fact_id"]].update({"dropped_by": ["stage2_note_null"], "passed": False})
                continue
            raw_notes.append({"fact_id": n["fact_id"], "note": n["note"], "source_quote": c["source_quote"],
                              "reverse_reading": c["reverse_reading"], "severity": None, "origin": pat["name"], "warnings": warns})
    return raw_notes, jall, rejected_extra


def run(a, llm=call_llm):
    pat = load_pattern(a.pattern, a.patterns_dir)
    no_ex = bool(getattr(a, "no_existing_notes", False))
    max_chars = a.max_chars or pat.get("max_chars") or DEFAULT_MAX_CHARS
    mode = pat["mode"]
    if mode == "promote" and no_ex:
        raise SystemExit("promote型は既存notes_for_writerが入力そのものなので--no-existing-notesは不可")
    if a.draft and a.verif:
        draft = json.loads(Path(a.draft).read_text(encoding="utf-8"))
        verif = json.loads(Path(a.verif).read_text(encoding="utf-8"))
        if a.ledger_txt:  # txt収録factに限定
            tids = {f["fact_id"] for f in P02.draft_from_ledger_txt(a.ledger_txt)[0]["facts"]}
            draft["facts"] = [f for f in draft["facts"] if f["fact_id"] in tids]
    elif a.ledger_txt:
        draft, verif = P02.draft_from_ledger_txt(a.ledger_txt)
    else:
        raise SystemExit("--ledger-txt か --draft/--verif が必要")
    items = fact_items(draft, verif, not no_ex)
    fids = [i["fact_id"] for i in items]
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    pro_items = [i for i in items if (i.get("notes_for_writer") or "").strip()] if mode == "promote" else items
    s1_items = pro_items
    p1 = fill_prompt(pat["stage1"], s1_items, max_chars, pat["examples"])
    prov = {"pattern": pat["name"], "mode": mode, "two_stage": is_two_stage(pat), "fact_count": len(items), "self_check_policy": pat["self_check_policy"], "stage2_existing_notes": pat["stage2_existing_notes"],
            "stage1_input_count": len(s1_items), "max_chars": max_chars, "no_existing_notes": no_ex,
            "max_notes": a.max_notes, "web_search": a.web_search, "prefix": pat["prefix"], "dry_run": a.dry_run,
            "budget_jpy": a.budget_jpy, "stage1_prompt_sha256": sha256(p1),
            "stage2_prompt_sha256": sha256(pat["stage2"]) if pat["stage2"] else None, "stage1_repeats": pat.get("stage1_repeats"), "stage1_5_prompt_sha256": sha256(pat["stage1_5"]) if pat.get("stage1_5") else None, "calls": 0, "cost_jpy": 0.0}
    if a.dry_run:
        (out / "stage1_prompt.txt").write_text(p1, encoding="utf-8")
        _jdump(out, "provenance_dryrun.json", prov)
        return prov
    rejected_extra, jall, raw_notes = [], [], []
    if mode == "onepass":
        raw_notes, jall, r1, _ = run_onepass(pat, items, max_chars, llm, a.web_search, out)
        prov["calls"], prov["cost_jpy"], prov["model"] = 1, r1["cost_jpy"], r1.get("model")
        prov["stage1_candidate_count"] = len(raw_notes)
    elif mode == "twostage":
        (out / "stage1_prompt.txt").write_text(p1, encoding="utf-8")
        r1 = llm(p1, a.web_search)
        prov["calls"], prov["cost_jpy"], prov["model"] = 1, r1["cost_jpy"], r1.get("model")
        _jdump(out, "stage1_raw.json", r1["parsed"])
        jl = [j for j in (r1["parsed"].get("judgments") or []) if isinstance(j, dict)]
        if jl:
            jmap = {j.get("fact_id"): j for j in jl}
            cands = []
            for it in items:
                j = jmap.get(it["fact_id"])
                if j and "reverse_propositions" in j:  # H3: R最大2つ列挙型
                    ok2, why2, e = screen2(j, it)
                    jall.append({"fact_id": it["fact_id"], "passed": ok2, "dropped_by": why2, "judgment": j})
                    if ok2:
                        cands.append({"fact_id": it["fact_id"], "source_quote": e.get("ledger_quote"),
                                      "reverse_reading": e.get("R"), "flipped_component": e.get("flipped_component"),
                                      "conclusion_change_reason": e.get("conclusion_change_reason")})
                    continue
                ok = bool(j) and screen_pass(j, it)
                if ok:
                    why = []
                elif not j:
                    why = ["judgment_missing"]
                else:
                    why = [k for k, c in (("reversible=false", j.get("reversible") is not True),
                                          ("ledger_quote_not_in_ledger", not quote_in_ledger(j.get("ledger_quote"), it))) if c]
                jall.append({"fact_id": it["fact_id"], "passed": ok, "dropped_by": why, "judgment": j})
                if ok:
                    cands.append({"fact_id": it["fact_id"], "source_quote": j.get("ledger_quote"),
                                  "reverse_reading": j.get("reverse_proposition"), "flipped_component": j.get("flipped_component")})
        else:  # candidatesキーへの互換フォールバック
            cands = select_candidates(r1["parsed"].get("candidates", []), set(fids))
            cids = {c["fact_id"] for c in cands}
            for it in items:
                jall.append({"fact_id": it["fact_id"], "passed": it["fact_id"] in cids, "dropped_by": [], "judgment": None})
        cands = select_candidates(cands, set(fids), a.max_notes)
        prov["stage1_candidate_count"] = len(cands)
        if cands and prov["cost_jpy"] <= a.budget_jpy:
            sel = {c["fact_id"] for c in cands}
            s2_items = [dict(i) for i in items if i["fact_id"] in sel]
            if pat["stage2_existing_notes"]:  # B2: 既存notes_for_writerを「誤読リスクの手がかり」として渡す(独立判定の後に参照)
                for c in cands:
                    c["existing_notes_hint"] = next((i.get("notes_for_writer") for i in s2_items if i["fact_id"] == c["fact_id"]), None)
            else:  # B2n: 渡さない(依存度測定)
                for i in s2_items:
                    i.pop("notes_for_writer", None)
            p2 = fill_prompt(pat["stage2"], s2_items, max_chars, pat["examples"], cands)
            (out / "stage2_prompt.txt").write_text(p2, encoding="utf-8")
            r2 = llm(p2, a.web_search)
            prov["calls"] = 2
            prov["cost_jpy"] += r2["cost_jpy"]
            prov["stage2_prompt_sha256"] = sha256(p2)
            _jdump(out, "stage2_raw.json", r2["parsed"])
            cmap = {c["fact_id"]: c for c in cands}
            jmap2 = {j["fact_id"]: j for j in jall}
            for n in r2["parsed"].get("notes", []):
                c = cmap.get(n.get("fact_id"))
                if c is None:
                    rejected_extra.append({"fact_id": n.get("fact_id"), "note": n.get("note"), "reason": "not_a_candidate"})
                    continue
                sc = n.get("self_check") or {}
                warns = []
                if pat["self_check_policy"] == "derivable_only":  # H2: R不自然は警告のみ。却下は捏造ガード(導出可能性)だけ
                    ok = sc.get("correct_statement_derivable_from_ledger") is True
                    if n.get("note") and ok and sc.get("R_is_natural_reading") is not True:
                        warns.append("R_is_natural_reading=false")
                else:
                    ok = sc.get("R_is_natural_reading") is True and sc.get("correct_statement_derivable_from_ledger") is True
                if warns:
                    jmap2[n["fact_id"]]["warnings"] = warns
                if n.get("note") and not ok:
                    rejected_extra.append({"fact_id": n["fact_id"], "note": n.get("note"), "reason": "self_check_false"})
                    jmap2[n["fact_id"]]["dropped_by"] = ["stage2_self_check_false"]
                    jmap2[n["fact_id"]]["passed"] = False
                    continue
                if not n.get("note"):
                    jmap2[n["fact_id"]]["dropped_by"] = ["stage2_note_null"]
                    jmap2[n["fact_id"]]["passed"] = False
                    continue
                raw_notes.append({"fact_id": n["fact_id"], "note": n["note"], "source_quote": c["source_quote"],
                                  "reverse_reading": c["reverse_reading"], "severity": None, "origin": pat["name"], "warnings": warns})
    elif mode == "twostage_gate":
        if not (pat.get("stage1_5") and pat.get("stage2")):
            raise SystemExit("twostage_gate needs stage1_5_prompt.txt and stage2_prompt.txt")
        raw_notes, jall, rejected_extra = run_gate(pat, items, fids, p1, a, llm, out, prov, max_chars)
    elif mode == "promote":
        (out / "stage1_prompt.txt").write_text(p1, encoding="utf-8")
        if pro_items:
            r1 = llm(p1, a.web_search)
            prov["calls"], prov["cost_jpy"], prov["model"] = 1, r1["cost_jpy"], r1.get("model")
            _jdump(out, "stage1_raw.json", r1["parsed"])
            pmap = {p.get("fact_id"): p for p in (r1["parsed"].get("promotions") or []) if isinstance(p, dict)}
            for it in pro_items:
                pr = pmap.get(it["fact_id"])
                if pr is None:
                    jall.append({"fact_id": it["fact_id"], "passed": False, "dropped_by": ["promotion_missing"], "judgment": None})
                    continue
                if not (pr.get("note") or "").strip():
                    jall.append({"fact_id": it["fact_id"], "passed": False, "dropped_by": ["note_null"], "judgment": pr})
                    continue
                sp = _norm(pr.get("source_prohibition"))
                if not sp or sp not in _norm(it.get("notes_for_writer")):
                    rejected_extra.append({"fact_id": it["fact_id"], "note": pr.get("note"), "reason": "source_prohibition_not_verbatim"})
                    jall.append({"fact_id": it["fact_id"], "passed": False, "dropped_by": ["source_prohibition_not_verbatim"], "judgment": pr})
                    continue
                jall.append({"fact_id": it["fact_id"], "passed": True, "dropped_by": [], "judgment": pr})
                raw_notes.append({"fact_id": it["fact_id"], "note": pr["note"], "source_quote": pr["source_prohibition"],
                                  "reverse_reading": pr.get("reverse_proposition"), "severity": None, "origin": pat["name"]})
        prov["stage1_candidate_count"] = len(raw_notes)
        fb_items = [i for i in items if i not in pro_items]
        prov["fallback_input_count"] = len(fb_items)
        if fb_items and pat.get("fallback") and prov["cost_jpy"] <= a.budget_jpy:
            fpat = load_pattern(pat["fallback"], a.patterns_dir)
            fb_notes, fb_j, rf, _ = run_onepass(fpat, fb_items, max_chars, llm, a.web_search, out, tag="fallback")
            prov["calls"] += 1
            prov["cost_jpy"] += rf["cost_jpy"]
            prov["fallback_pattern"] = pat["fallback"]
            raw_notes += fb_notes
            for x in fb_j:
                x["via_fallback"] = True
            jall += fb_j
    else:
        raise SystemExit("unknown mode: %s" % mode)
    _jdump(out, "judgments_all.json", jall)
    acc, rej = postprocess(raw_notes, set(fids), pat["prefix"], max_chars)
    rej = rej + rejected_extra
    trimmed = []
    if a.max_notes is not None and len(acc) > a.max_notes:
        acc, trimmed = P02.trim_notes(raw_notes, acc, fids, a.max_notes)
    srcmap = {n.get("fact_id"): n for n in raw_notes}
    notes = [{"fact_id": f, "note": acc[f], "source_quote": srcmap[f].get("source_quote"),
              "reverse_reading": srcmap[f].get("reverse_reading"), "severity": srcmap[f].get("severity"),
              "origin": srcmap[f].get("origin"), "warnings": srcmap[f].get("warnings") or []} for f in fids if f in acc]
    _jdump(out, "notes.json", notes)
    _jdump(out, "rejected.json", rej)
    _jdump(out, "trimmed.json", trimmed)
    prov.update({"warning_count": sum(len(n["warnings"]) for n in notes), "attached_count": len(acc), "rejected_count": len(rej), "trimmed_count": len(trimmed),
                 "over_budget": prov["cost_jpy"] > a.budget_jpy})
    if a.append_to_txt:
        orig = Path(a.append_to_txt).read_bytes()
        (out / "verified_fact_ledger_control.txt").write_bytes(orig)
        nbtxt, done = P02.append_notes_to_txt(orig.decode("utf-8"), acc)  # p02の決定論追記を流用
        (out / "verified_fact_ledger_nb.txt").write_bytes(nbtxt.encode("utf-8"))
        prov["appended_facts"] = done
    _jdump(out, "provenance.json", prov)
    return prov


def build_parser():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pattern", required=True)
    ap.add_argument("--patterns-dir", default=None)
    ap.add_argument("--ledger-txt")
    ap.add_argument("--draft")
    ap.add_argument("--verif")
    ap.add_argument("--append-to-txt")
    ap.add_argument("--max-chars", type=int, default=None)  # 未指定: pattern.json -> 120
    ap.add_argument("--max-notes", type=int, default=None)
    ap.add_argument("--web-search", choices=["none", "url_only"], default="none")
    ap.add_argument("--budget-jpy", type=float, default=5.0)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-existing-notes", action="store_true")
    ap.add_argument("--out-dir", required=True)
    return ap


def main(argv=None):
    prov = run(build_parser().parse_args(argv))
    print(json.dumps({k: prov.get(k) for k in ("pattern", "two_stage", "fact_count", "calls", "cost_jpy", "attached_count", "dry_run")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
