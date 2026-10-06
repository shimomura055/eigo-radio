# -*- coding: utf-8 -*-
"""gen_notes_p04: 多義語注意Note TRIAL-04用の追加モード(DEV/Trial専用、Production非接続)。
gen_notes_p03の部品(fill_prompt/quote_in_ledger/build_s15_input等)を流用し、Opus必須修正1〜9を反映した流れを提供する。
 stage1(既存notes伏せ・1〜2回) -> R lint -> [素通り判定: predicate_direction_explicit=false かつ polarity] -> [P3: 見出し要約call]
 -> 判定役(固定基準+blocking_word、限定語blockingはlow->medium昇格) -> cover call(既存notesが採用Rを既に禁じているか)
 -> stage2(r_echo照合・vague語lint・表記形式・英語は台帳実在語のみ)
対象fact_idはprompt・生成ロジックに一切含めない(評価はeval_notes_p04.py/targets.jsonのみ)。"""
import json
import re
import gen_notes_p03 as G

COMPONENT_ORDER = ["polarity", "stage", "subject_object", "interim_final", "cause_effect"]
CODEMODES = ("p04_gate", "p04_stable")

# 修正2: 向き・結果が曖昧な語(R・「変化後の状態」から排除)
VAGUE_WORDS = ["戻す", "元に戻", "復元", "ロールバック", "rollback", "変更", "見直し", "見直す", "改める", "改め", "調整"]
# 修正5: 限定語(blocking_wordがこれに当たればlow->medium)
LIMIT_WORDS = ["当面", "一時", "計画", "予定", "模擬", "試験", "暫定", "一部", "将来", "仮", "当初", "現時点", "期間限定"]
QUOTED_HYO = re.compile(r"表記['’‘「]([^'’‘」]+)['’‘」]")
URL_PAREN = re.compile(r"\s*\(\[[^\]]*\]\([^)]*\)\)")
ENG = re.compile(r"[A-Za-z][A-Za-z0-9\-]{2,}")
R_COVERAGE_MIN = 0.5


def _norm(s):
    return "".join((s or "").split())


KANJI = re.compile(r"[一-鿿々]")


def _word_hit(text, w):
    """vague語wがtextに『語として』出現するか(H13b)。直前と直後の両方が漢字の出現(例: 複合名詞の内部)は語内一致として除外する。
    英字語は前後が英字なら語内一致として除外する。"""
    low, lw = text.lower(), w.lower()
    start = 0
    while True:
        i = low.find(lw, start)
        if i < 0:
            return False
        j = i + len(lw)
        before = text[i - 1] if i > 0 else ""
        after = text[j] if j < len(text) else ""
        if lw.isascii():
            embedded = bool(before and before.isascii() and before.isalpha()) or bool(after and after.isascii() and after.isalpha())
        else:
            embedded = bool(before and KANJI.match(before)) and bool(after and KANJI.match(after))
        if not embedded:
            return True
        start = i + 1


def vague_hits(text, amb=None, strip_quoted=False):
    """textに含まれるvague語(および当該factの曖昧表記ambそのもの)のリスト。strip_quoted=Trueのとき、表記'...'の引用部分は検査対象から外す。"""
    t = text or ""
    if strip_quoted:
        t = QUOTED_HYO.sub("表記", t)
    hits = [w for w in VAGUE_WORDS if _word_hit(t, w)]
    if amb and _norm(amb) and _norm(amb) in _norm(t):
        hits.append("amb:" + amb)
    return hits


def is_limit_word(w):
    w = (w or "").strip()
    return bool(w) and any(lw in w for lw in LIMIT_WORDS)


def clean_existing_notes(s):
    """既存notes_for_writerからURL出典括弧を除いた本文(「既に禁じ済み」一覧・cover入力用)。"""
    return URL_PAREN.sub("", s or "").strip()


def _amb(j, item):
    a = (j or {}).get("ambiguous_expression")
    if isinstance(a, str) and a.strip() and _norm(a) in _norm(item.get("claim")):
        return a.strip()
    return ""


def valid_rs(j, item, lint_log=None, run=None):
    """changes_conclusion=true かつ ledger_quoteが台帳(claim/scope/conditions)に部分一致 かつ R lint合格のRを出現順に列挙。
    lint違反Rは lint_log へ記録して除外する。"""
    out = []
    amb = _amb(j, item)
    pred = (j or {}).get("predicate_direction_explicit")
    pred = pred if isinstance(pred, bool) else None
    for i, e in enumerate((j or {}).get("reverse_propositions") or []):
        if isinstance(e, dict) and e.get("changes_conclusion") is True and G.quote_in_ledger(e.get("ledger_quote"), item):
            hits = vague_hits(e.get("R"), amb)
            if hits:
                if lint_log is not None:
                    lint_log.append({"stage": "stage1_R", "run": run, "fact_id": (j or {}).get("fact_id"), "R": e.get("R"), "words": hits})
                continue
            out.append({"R": e.get("R"), "flipped_component": e.get("flipped_component"), "ledger_quote": e.get("ledger_quote"),
                        "conclusion_change_reason": e.get("conclusion_change_reason"), "idx": i,
                        "predicate_direction_explicit": pred, "ambiguous_expression": amb})
    return out


def _rank_key(e, pos):
    fc = e.get("flipped_component")
    comp_rank = COMPONENT_ORDER.index(fc) if fc in COMPONENT_ORDER else len(COMPONENT_ORDER)
    return (comp_rank, pos)


def pick_from_entries(entries):
    """R採用規則: flipped_componentの優先順(polarity>stage>subject_object>interim_final>cause_effect) > 出現順。
    (既存notesはstage1から伏せたため、existing_note_coversは使わない)"""
    if not entries:
        return None
    return min(enumerate(entries), key=lambda t: _rank_key(t[1], t[0]))[1]


def pick_reverse_p04(j, item):
    if (j or {}).get("reversible") is not True:
        return None
    return pick_from_entries(valid_rs(j, item))


def stage1_result(j, item, lint_log=None, run=None):
    """1回分のstage1判定jをfact単位に整理。passed=reversibleかつ採用R成立(R lint合格)。"""
    if j is None:
        return {"passed": False, "why": ["judgment_missing"], "entries": [], "best": None, "compressed_claim": None}
    cc = j.get("compressed_claim")
    if j.get("reversible") is not True:
        return {"passed": False, "why": ["reversible=false"], "entries": [], "best": None, "compressed_claim": cc}
    before = len(lint_log) if lint_log is not None else 0
    ents = valid_rs(j, item, lint_log, run)
    if not ents:
        props = [x for x in (j.get("reverse_propositions") or []) if isinstance(x, dict)]
        if lint_log is not None and len(lint_log) > before:
            why = ["R_lint_rejected"]
        elif not any(x.get("changes_conclusion") is True for x in props):
            why = ["no_R_changes_conclusion"]
        else:
            why = ["ledger_quote_not_in_ledger"]
        return {"passed": False, "why": why, "entries": [], "best": None, "compressed_claim": cc}
    return {"passed": True, "why": [], "entries": ents, "best": pick_from_entries(ents), "compressed_claim": cc}


def is_bypass(entry):
    """修正1: predicate_direction_explicit=false(明示的なfalse)かつ採用Rがpolarity型なら判定役を素通りする。"""
    return bool(entry) and entry.get("flipped_component") == "polarity" and entry.get("predicate_direction_explicit") is False


def route_facts(results, items):
    """results: [ {fact_id: stage1_result}, ... ] (run順)。
    bypass: 採用Rがpolarity+pred false(判定役を素通り) / judge: 判定役へ / drop: どの回でもpassedでない。
    stable: 全回passed。run_entries: 各回のbest entry(判定役候補)。"""
    out = {}
    for it in items:
        fid = it["fact_id"]
        rs = [r.get(fid) or {"passed": False, "entries": [], "best": None, "why": ["judgment_missing"], "compressed_claim": None} for r in results]
        flags = [bool(r["passed"]) for r in rs]
        if not any(flags):
            out[fid] = {"route": "drop", "entry": None, "run_entries": [], "runs_pass": flags, "stable": False, "why": rs[0]["why"] if rs else ["no_run"]}
            continue
        run_entries = [dict(r["best"], compressed_claim=r["compressed_claim"], run=k + 1) for k, r in enumerate(rs) if r["passed"]]
        adopted = pick_from_entries(run_entries)
        out[fid] = {"route": "bypass" if is_bypass(adopted) else "judge", "entry": adopted, "run_entries": run_entries,
                    "runs_pass": flags, "stable": all(flags) and len(flags) >= 2, "why": []}
    return out


def apply_gate_levels(order, per, verdicts, pass_levels, stable=None, medium_requires_stable=False):
    """判定役の結果を適用(修正3・5)。blocking_wordが限定語ならlow->medium。mediumはmedium_requires_stable時、stable[fid]=Trueのfactのみ通過。
    戻り値: (採用 {fact_id: (cid, entry)}, 記録 {fact_id: {...}})"""
    vm = {}
    for v in verdicts or []:
        if isinstance(v, dict):
            vm[(v.get("fact_id"), str(v.get("cid") or "A"))] = v
    chosen, rec = {}, {}
    stable = stable or {}
    for fid in order:
        rows, pick, pick_rank, saw_unstable = [], None, 9, False
        levels = []
        for c in per[fid]:
            v = vm.get((fid, c["cid"]))
            raw = v.get("likelihood") if v else None
            raw = raw if raw in ("high", "medium", "low") else "missing"
            bw = (v or {}).get("blocking_word")
            bw = bw.strip() if isinstance(bw, str) else None
            lv, promoted = raw, False
            if raw == "low" and is_limit_word(bw):
                lv, promoted = "medium", True
            levels.append(lv)
            ok = lv in pass_levels
            if lv == "medium" and medium_requires_stable and not stable.get(fid):
                ok, saw_unstable = False, True
            rows.append({"cid": c["cid"], "R": c["R"], "likelihood": lv, "likelihood_raw": raw, "promoted_low_to_medium": promoted,
                         "blocking_word": bw, "blocking_word_missing": (raw in ("medium", "low") and not bw), "reason": (v or {}).get("reason"),
                         "compressed_claim": c.get("compressed_claim")})
            rk = {"high": 0, "medium": 1}.get(lv, 9)
            if ok and rk < pick_rank:
                pick, pick_rank = c, rk
        why = []
        if pick is None:
            if saw_unstable:
                why = ["stage1_5_medium_unstable"]
            elif "medium" in levels:
                why = ["stage1_5_medium"]
            else:
                why = ["stage1_5_low"] if "low" in levels else ["stage1_5_missing"]
        else:
            chosen[fid] = (pick["cid"], pick["_entry"])
        rec[fid] = {"passed": pick is not None, "dropped_by": why, "verdicts": rows, "adopted_cid": pick["cid"] if pick else None}
    return chosen, rec


def missing_verdict_keys(order, per, verdicts):
    """判定役の出力に有効なverdict(high/medium/low)が無い (fact_id, cid) のリスト。"""
    have = {(v.get("fact_id"), str(v.get("cid") or "A")) for v in verdicts or []
            if isinstance(v, dict) and v.get("likelihood") in ("high", "medium", "low")}
    return [(f, c["cid"]) for f in order for c in per[f] if (f, c["cid"]) not in have]


def subset_order_per(order, per, keys):
    ks = set(keys)
    o2, p2 = [], {}
    for f in order:
        cs = [c for c in per[f] if (f, c["cid"]) in ks]
        if cs:
            o2.append(f)
            p2[f] = cs
    return o2, p2


def headline_items(items, fids):
    keep = set(fids)
    return [{"fact_id": i["fact_id"], "claim": i["claim"]} for i in items if i["fact_id"] in keep]


# ---------- stage2検証(修正2・6・7) ----------
def _bigrams(s):
    s = re.sub(r"[\s。、,.「」『』()（）'\"・:：]", "", s or "")
    return {s[i:i + 2] for i in range(len(s) - 1)}


def r_in_note(note, R):
    """noteの「<R>ではない」部分(最後の『ではない』を含む文)が採用Rの主要語を保持しているか。bigram被覆率>=R_COVERAGE_MIN。(ok, 被覆率)"""
    sents = [s for s in re.split(r"[。\n]", note or "") if s.strip()]
    neg = [s for s in sents if "ではない" in s or "でない" in s]
    if not neg:
        return False, 0.0
    rb = _bigrams(R)
    if not rb:
        return False, 0.0
    cov = len(rb & _bigrams(neg[-1])) / len(rb)
    return cov >= R_COVERAGE_MIN, cov


def english_not_in_ledger(note, item):
    led = (" ".join(str(item.get(k) or "") for k in ("claim", "scope", "conditions", "notes_for_writer", "verification_notes"))).lower()
    # H13d: 大文字略語(FW25・AIなど、英字がすべて大文字)は許可する
    return [w for w in ENG.findall(note or "") if w.lower() not in led and w != w.upper()]


def _norm_echo(s):
    """H13a: r_echo照合の正規化(空白除去+末尾の句読点・記号を除く)。"""
    return _norm(s).rstrip("。.．、,!！?？")


def check_stage2(n, c, item):
    """stage2の1noteを検証。戻り値: (ok, reason, detail)。reasonは却下理由(okならNone)。"""
    det = {}
    sc = n.get("self_check") or {}
    note = n.get("note")
    if not note:
        return False, "stage2_note_null", det
    det["self_check"] = {"R_is_natural_reading": sc.get("R_is_natural_reading"), "derivable": sc.get("correct_statement_derivable_from_ledger")}
    if sc.get("correct_statement_derivable_from_ledger") is not True:
        return False, "self_check_false", det
    det["r_echo_match"] = _norm_echo(n.get("r_echo")) == _norm_echo(c.get("reverse_reading")) and bool(_norm_echo(n.get("r_echo")))
    if not det["r_echo_match"]:
        return False, "r_echo_mismatch", det
    ok_r, cov = r_in_note(note, c.get("reverse_reading"))
    det["r_in_note"], det["r_coverage"] = ok_r, round(cov, 2)
    if not ok_r:
        return False, "r_not_in_note", det
    amb = c.get("ambiguous_expression") or ""
    hits = vague_hits(note, amb, strip_quoted=True) + [h + "(correct_state)" for h in vague_hits(n.get("correct_state"), amb)] + \
        [h + "(r_echo)" for h in vague_hits(n.get("r_echo"), amb)]
    det["lint_hits"] = hits
    if hits:
        return False, "lint_rejected", det
    eng = english_not_in_ledger(note, item)
    det["english_not_in_ledger"] = eng
    if eng:
        return False, "english_not_in_ledger", det
    bad_q = [q for q in QUOTED_HYO.findall(note) if not G.quote_in_ledger(q, item)]
    det["quote_not_in_ledger"] = bad_q
    if bad_q:
        return False, "hyoki_not_in_ledger", det
    return True, None, det


def run_p04(pat, items, fids, p1, a, llm, out, prov, max_chars):
    meta = pat.get("meta") or {}
    reps = max(1, int(pat.get("stage1_repeats") or 1))
    pass_levels = tuple(meta.get("judge_pass") or ["high"])
    mrs = bool(meta.get("medium_requires_stable"))
    compress_source = meta.get("compress_source", "stage1")
    imap = {i["fact_id"]: i for i in items}
    lint_log = []
    (out / "stage1_prompt.txt").write_text(p1, encoding="utf-8")
    hashes = {"stage1_template": G.sha256(pat["stage1"]), "stage1_assembled": G.sha256(p1)}
    for k in ("stage1_5", "cover", "stage2", "headline"):
        if pat.get(k):
            hashes[k + "_template"] = G.sha256(pat[k])
    prov.update({"calls": 0, "cost_jpy": 0.0, "judge_pass": list(pass_levels), "medium_requires_stable": mrs, "compress_source": compress_source,
                 "prompt_sha256": hashes})
    G._jdump(out, "prompt_hashes.json", hashes)
    results, runs_j = [], []
    for k in range(reps):
        r1 = llm(p1, a.web_search)
        prov["calls"] += 1
        prov["cost_jpy"] += r1["cost_jpy"]
        prov["model"] = r1.get("model")
        G._jdump(out, "stage1_raw_r%d.json" % (k + 1), r1["parsed"])
        jmap = {j.get("fact_id"): j for j in (r1["parsed"].get("judgments") or []) if isinstance(j, dict)}
        runs_j.append(jmap)
        results.append({it["fact_id"]: stage1_result(jmap.get(it["fact_id"]), it, lint_log, k + 1) for it in items})
    sets = [sorted(f for f, r in rc.items() if r["passed"]) for rc in results]
    prov["stage1_run_pass_sets"] = sets
    prov["stage1_jaccard"] = G.jaccard(sets[0], sets[1]) if len(sets) >= 2 else None
    routes = route_facts(results, items)
    bypass = {f: x["entry"] for f, x in routes.items() if x["route"] == "bypass"}
    judge_fids = [i["fact_id"] for i in items if routes[i["fact_id"]]["route"] == "judge"]
    prov["bypass_count"], prov["judge_input_count"] = len(bypass), len(judge_fids)
    ok_budget = lambda: prov["cost_jpy"] <= a.budget_jpy * prov["calls"]
    headlines = {}
    if compress_source == "headline" and judge_fids and ok_budget():
        hp = pat["headline"].replace("{HEADLINE_INPUT}", json.dumps(headline_items(items, judge_fids), ensure_ascii=False, indent=1))
        (out / "headline_prompt.txt").write_text(hp, encoding="utf-8")
        rh = llm(hp, a.web_search)
        prov["calls"] += 1
        prov["cost_jpy"] += rh["cost_jpy"]
        G._jdump(out, "headline_raw.json", rh["parsed"])
        for h in rh["parsed"].get("headlines") or []:
            if isinstance(h, dict) and (h.get("headline") or "").strip():
                headlines[h.get("fact_id")] = h["headline"].strip()
    runs_c = []
    for k in range(reps):
        rc = {}
        for fid in judge_fids:
            e = next((x for x in routes[fid]["run_entries"] if x.get("run") == k + 1), None)
            if e is None:
                continue
            e = dict(e)
            e["stage1_compressed_claim"] = e.get("compressed_claim")
            if compress_source == "headline":
                if fid not in headlines:
                    continue
                e["compressed_claim"] = headlines[fid]
            rc[fid] = e
        runs_c.append(rc)
    order, per = G.build_s15_input(runs_c)
    prov["stage1_union_count"] = len(order)
    chosen, rec = {}, {}
    if order and ok_budget():
        p15 = pat["stage1_5"].replace("{S15_INPUT}", json.dumps(G.s15_prompt_items(order, per), ensure_ascii=False, indent=1))
        (out / "stage1_5_prompt.txt").write_text(p15, encoding="utf-8")
        r15 = llm(p15, a.web_search)
        prov["calls"] += 1
        prov["cost_jpy"] += r15["cost_jpy"]
        G._jdump(out, "stage1_5_raw.json", r15["parsed"])
        verdicts = list(r15["parsed"].get("verdicts") or [])
        miss = missing_verdict_keys(order, per, verdicts)  # H13e: verdict欠落は1回だけ再問合せ
        prov["judge_missing_first"] = len(miss)
        if miss and ok_budget():
            order2, per2 = subset_order_per(order, per, miss)
            p15b = pat["stage1_5"].replace("{S15_INPUT}", json.dumps(G.s15_prompt_items(order2, per2), ensure_ascii=False, indent=1))
            (out / "stage1_5_requery_prompt.txt").write_text(p15b, encoding="utf-8")
            r15b = llm(p15b, a.web_search)
            prov["calls"] += 1
            prov["cost_jpy"] += r15b["cost_jpy"]
            G._jdump(out, "stage1_5_requery_raw.json", r15b["parsed"])
            verdicts += [v for v in (r15b["parsed"].get("verdicts") or []) if isinstance(v, dict)]
            prov["judge_missing_after_requery"] = len(missing_verdict_keys(order, per, verdicts))
        chosen, rec = apply_gate_levels(order, per, verdicts, pass_levels,
                                        {f: routes[f]["stable"] for f in order}, mrs)
    jall = []
    for it in items:
        fid = it["fact_id"]
        x = routes[fid]
        d = {"fact_id": fid, "passed": False, "dropped_by": [], "judgment": runs_j[0].get(fid), "route": x["route"],
             "stage1_run_pass": x["runs_pass"], "stage1_stable": x["stable"]}
        if reps >= 2:
            d["judgment_r2"] = runs_j[1].get(fid)
        d["lint_rejected_R"] = [e for e in lint_log if e.get("fact_id") == fid]
        if x["entry"]:
            e = x["entry"]
            d.update({"adopted_R": e.get("R"), "adopted_flipped_component": e.get("flipped_component"),
                      "predicate_direction_explicit": e.get("predicate_direction_explicit"), "ambiguous_expression": e.get("ambiguous_expression")})
        if fid in bypass:
            d["passed"] = True
            d["bypass_judge"] = True
        elif x["route"] == "drop":
            d["dropped_by"] = list(x["why"]) or ["stage1_not_reversible"]
        elif compress_source == "headline" and fid not in headlines:
            d["dropped_by"] = ["headline_missing"]
        else:
            y = rec.get(fid)
            if y is None:
                d["dropped_by"] = ["stage1_5_not_run"]
            else:
                d.update({"passed": y["passed"], "dropped_by": y["dropped_by"], "stage1_5": y["verdicts"]})
                if y["passed"] and any(v["likelihood"] == "medium" for v in y["verdicts"] if v["cid"] == y["adopted_cid"]):
                    d["warnings"] = ["stage1_5_passed_as_medium"]
        if fid in headlines:
            d["headline"] = headlines[fid]
        jall.append(d)
    jmap2 = {j["fact_id"]: j for j in jall}
    final = dict(bypass)
    final.update({f: ce[1] for f, ce in chosen.items()})
    prov["stage1_candidate_count"] = len(final)
    # ---- cover call: 既存notesが採用Rを既に禁じているか(別の小さなcall) ----
    cov_in = [{"fact_id": f, "R": final[f].get("R"), "existing_notes": clean_existing_notes(imap[f].get("notes_for_writer"))}
              for f in [i["fact_id"] for i in items if i["fact_id"] in final] if clean_existing_notes(imap[f].get("notes_for_writer"))]
    covers = {}
    if cov_in and ok_budget():
        cp = pat["cover"].replace("{COVER_INPUT}", json.dumps(cov_in, ensure_ascii=False, indent=1))
        (out / "cover_prompt.txt").write_text(cp, encoding="utf-8")
        rcv = llm(cp, a.web_search)
        prov["calls"] += 1
        prov["cost_jpy"] += rcv["cost_jpy"]
        G._jdump(out, "cover_raw.json", rcv["parsed"])
        for v in rcv["parsed"].get("covers") or []:
            if isinstance(v, dict) and isinstance(v.get("existing_note_covers"), bool):
                covers[v.get("fact_id")] = v
    skipped = []
    for fid in list(final):
        has = bool(clean_existing_notes(imap[fid].get("notes_for_writer")))
        c = covers.get(fid)
        jmap2[fid]["existing_note"] = {"has": has, "covers_R": (c or {}).get("existing_note_covers") if has else False, "reason": (c or {}).get("reason")}
        if has and c and c.get("existing_note_covers") is True and meta.get("cover_record_only"):
            jmap2[fid]["existing_note"]["dup_of_existing"] = True  # H12: 除外せず、重複を記録だけする(副指標)
            prov.setdefault("cover_dup_ids", []).append(fid)
        elif has and c and c.get("existing_note_covers") is True:
            skipped.append(fid)
            jmap2[fid].update({"passed": False, "dropped_by": ["existing_note_covers_R"]})
            del final[fid]
    prov["cover_skipped"] = skipped
    raw_notes, rejected_extra, cands = [], [], []
    for fid in [i["fact_id"] for i in items if i["fact_id"] in final]:
        e = final[fid]
        cands.append({"fact_id": fid, "source_quote": e.get("ledger_quote"), "reverse_reading": e.get("R"),
                      "flipped_component": e.get("flipped_component"), "conclusion_change_reason": e.get("conclusion_change_reason"),
                      "ambiguous_expression": e.get("ambiguous_expression") or "",
                      "already_prohibited": [t for t in [clean_existing_notes(imap[fid].get("notes_for_writer"))] if t]})
        if meta.get("stage2_already_prohibited") is False:
            cands[-1].pop("already_prohibited")
    cands = G.select_candidates(cands, set(fids), a.max_notes)
    if cands and ok_budget():
        sel = {c["fact_id"] for c in cands}
        s2_items = []
        for i in items:
            if i["fact_id"] in sel:
                i2 = dict(i)
                i2.pop("notes_for_writer", None)  # 既存notesは「既に禁じ済み」一覧(already_prohibited)としてのみ渡す
                s2_items.append(i2)
        p2 = G.fill_prompt(pat["stage2"], s2_items, max_chars, pat["examples"], cands)
        (out / "stage2_prompt.txt").write_text(p2, encoding="utf-8")
        r2 = llm(p2, a.web_search)
        prov["calls"] += 1
        prov["cost_jpy"] += r2["cost_jpy"]
        prov["stage2_prompt_sha256"] = G.sha256(p2)
        G._jdump(out, "stage2_raw.json", r2["parsed"])
        cmap = {c["fact_id"]: c for c in cands}
        seen = set()
        for n in r2["parsed"].get("notes", []):
            c = cmap.get(n.get("fact_id"))
            if c is None:
                rejected_extra.append({"fact_id": n.get("fact_id"), "note": n.get("note"), "reason": "not_a_candidate"})
                continue
            if n["fact_id"] in seen:
                continue
            seen.add(n["fact_id"])
            ok, why, det = check_stage2(n, c, imap[n["fact_id"]])
            jmap2[n["fact_id"]]["stage2"] = dict(det, r_echo=n.get("r_echo"), correct_state=n.get("correct_state"), result=why or "ok")
            sc = n.get("self_check") or {}
            warns = []
            if ok and sc.get("R_is_natural_reading") is not True:
                warns.append("R_is_natural_reading=false")
                jmap2[n["fact_id"]]["warnings"] = (jmap2[n["fact_id"]].get("warnings") or []) + warns
            if not ok:
                if why == "stage2_note_null":
                    jmap2[n["fact_id"]].update({"dropped_by": ["stage2_note_null"], "passed": False})
                    continue
                rejected_extra.append({"fact_id": n["fact_id"], "note": n.get("note"), "reason": why})
                if why in ("lint_rejected", "english_not_in_ledger", "hyoki_not_in_ledger"):
                    lint_log.append({"stage": "stage2", "fact_id": n["fact_id"], "note": n.get("note"), "reason": why, "detail": det})
                jmap2[n["fact_id"]].update({"dropped_by": ["stage2_" + why], "passed": False})
                continue
            raw_notes.append({"fact_id": n["fact_id"], "note": n["note"], "source_quote": c["source_quote"],
                              "reverse_reading": c["reverse_reading"], "severity": None, "origin": pat["name"], "warnings": warns})
    G._jdump(out, "lint_rejected.json", lint_log)
    prov["lint_rejected_count"] = len(lint_log)
    prov["promoted_low_to_medium"] = sum(1 for y in rec.values() for v in y["verdicts"] if v.get("promoted_low_to_medium"))
    return raw_notes, jall, rejected_extra
