# -*- coding: utf-8 -*-
"""eval_notes_p04: TRIAL-04用の評価(DEV/Trial専用、API非呼出)。eval_notes_p03の指標に加えて
 (1) rollback別枠Gate(targets.jsonのgate_fact。機械チェックはPASS候補/FAIL候補。最終はFable/人手ラベル。3値定義は eval/rollback_gate_labels.md)
 (2) 安定性(同一台帳の2回の付与集合のJaccard/一致率。--rerun-dirを渡した場合のみ)
 (3) holdout誤付与(厳密=targets外の付与数、期待超過=expected_maxを超えた付与数)
 (4) 機械判定可能な合格条件の要約(捕捉>=9/14・付与率<=25%・holdout誤付与<=1。内容一致・捏造・迎合はSonnet仮ラベル(--labels)で集計)
 (5) 副指標: 和集合(生成note + 既存notes禁止文の機械転記)、段別ファネル(--tag指定時 <tag>funnel.md)
を出力する。"""
import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRIAL = HERE.parent
sys.path.insert(0, str(HERE))
import eval_notes_p03 as E  # noqa: E402

# ---- rollback別枠Gate: 機械チェックの条件(逐語は報告にも転記) ----
WITHDRAW = re.compile(r"取り下げ|引っ込め|停止|提供をやめ|機能のない状態")
REVIVE = re.compile(r"復活|再提供|再開|復旧")
NEGATION = re.compile(r"意味ではない|ではない")
FORBIDDEN_NEG = re.compile(r"復元ではない|元に戻したのではない|元の状態に戻していない")
REVIVE_WINDOW = 30  # 復活系語から、この文字数以内に否定(ではない)が続くこと
SPLIT = re.compile(r"[。\n]")


def rollback_gate_check(note):
    """note(日本語本文)に対する機械チェック。戻り値: {"result": "PASS_CANDIDATE"|"FAIL_CANDIDATE", "reasons": [...]}。
    (A)取り下げ系の語を含む AND (B)復活・再提供・再開・復旧の直後(30字以内)に「ではない」「意味ではない」がある
    AND (C)「復元ではない」「元に戻したのではない」「元の状態に戻していない」を含まない
    AND (D)否定している文が「全体」だけを対象にしていない(否定文に「全体」があり「機能」がない場合はFAIL)。"""
    note = note or ""
    reasons = []
    if not WITHDRAW.search(note):
        reasons.append("A:取り下げ系の語がない")
    neg_seg = None
    for seg in SPLIT.split(note):
        for m in REVIVE.finditer(seg):
            tail = seg[m.end(): m.end() + REVIVE_WINDOW]
            if NEGATION.search(tail):
                neg_seg = seg
                break
        if neg_seg:
            break
    if neg_seg is None:
        reasons.append("B:復活・再提供・再開・復旧を否定する表現がない")
    if FORBIDDEN_NEG.search(note):
        reasons.append("C:導入前状態への復帰まで禁じる表現を含む")
    if neg_seg is not None and "全体" in neg_seg and "機能" not in neg_seg:
        reasons.append("D:否定が『全体』だけを対象にしている")
    return {"result": "PASS_CANDIDATE" if not reasons else "FAIL_CANDIDATE", "reasons": reasons}


def gate_eval(notes, gate_fact):
    """gate_factについて(A)捕捉の有無、(B)note全文、(C)機械チェック。"""
    n = next((x for x in notes if x["fact_id"] == gate_fact), None)
    if n is None:
        return {"gate_fact": gate_fact, "captured": False, "note": None, "check": {"result": "FAIL_CANDIDATE", "reasons": ["未捕捉"]}}
    return {"gate_fact": gate_fact, "captured": True, "note": n["note"], "check": rollback_gate_check(n["note"])}


def stability(ids_a, ids_b):
    """2回の付与集合の一致率(Jaccard。両方空なら1.0)と共通/片方のみの件数。"""
    a, b = set(ids_a), set(ids_b)
    j = (len(a & b) / len(a | b)) if (a | b) else 1.0
    return {"jaccard": j, "both": len(a & b), "only_a": len(a - b), "only_b": len(b - a)}


def holdout_over(attached, expected_max):
    return max(0, attached - expected_max) if expected_max is not None else None


def _load(p, default=None):
    return E._load(p, default)


def summarize_criteria(core_rows, hold_rows, hold_over=None):
    """機械判定可能な合格条件(捕捉>=9/14・付与率<=25%・holdout誤付与<=1)。内容一致・捏造・迎合は別行(Sonnet仮ラベル)。"""
    agg = E.aggregate(core_rows) if core_rows else None
    out = {}
    if agg:
        out["recall"] = "%d/%d (>=9/14: %s)" % (agg["hit"], agg["targets"], "OK" if agg["hit"] >= 9 else "NG")
        out["attach_rate"] = "%s (<=0.25: %s)" % (E.fmt(agg["attach_rate"]), "OK" if (agg["attach_rate"] is not None and agg["attach_rate"] <= 0.25) else "NG")
    strict = sum(r["extra"] for r in hold_rows)
    out["holdout_attach_over_expected_max"] = "%d (<=1: %s)" % (sum(hold_over or []), "OK" if sum(hold_over or []) <= 1 else "NG") if hold_over is not None else "-"
    out["holdout_false_attach_strict(参考: targets外の全付与)"] = "%d" % strict
    return out


# ---- TRIAL-04追加: 既存notes禁止文の機械転記(副指標: 和集合)・段別ファネル ----
PROHIBIT = re.compile(r"書かない|扱わない|補わない|言わない|断定しない|区別|厳密に分|ではなく|Do not|do not|not detected|禁止")
URL_PAREN = re.compile(r"\s*\(\[[^\]]*\]\([^)]*\)\)")


def existing_prohibition_ids(txt_path):
    """台帳txtの既存notes_for_writerのうち、禁止文(書かない等)を含むfact_idを機械的に抽出する(内容の適否は評価しない)。"""
    import gen_notes_p03 as G
    draft, _ = G.P02.draft_from_ledger_txt(txt_path)
    out = {}
    for f in draft["facts"]:
        s = URL_PAREN.sub("", f.get("notes_for_writer") or "").strip()
        if s and PROHIBIT.search(s):
            out[f["fact_id"]] = s
    return out


def funnel_block(pat, slug, fid, d, attached_note):
    """1factの段別ファネルをMarkdown行にする。d=judgments_all.jsonの当該要素。"""
    L = ["- **%s/%s %s**" % (pat, slug, fid)]
    if d is None:
        return L + ["  - (judgments_allなし)"]
    rs = []
    for k, key in (("run1", "judgment"), ("run2", "judgment_r2")):
        j = d.get(key)
        if j is None:
            continue
        rps = ["%s[%s%s]" % (r.get("R"), r.get("flipped_component"), "" if r.get("changes_conclusion") else ",結論不変")
               for r in (j.get("reverse_propositions") or []) if isinstance(r, dict)]
        pr = [("%s|有:%s|無:%s" % (x.get("paraphrase"), x.get("reading_exists"), x.get("reading_none"))) for x in (j.get("paraphrase_readings") or []) if isinstance(x, dict)]
        pol = any(isinstance(r, dict) and r.get("flipped_component") == "polarity" for r in (j.get("reverse_propositions") or []))
        rs.append("%s: reversible=%s pred_explicit=%s amb=%r 極性型R含む=%s 言い換え=%s R=%s" % (k, j.get("reversible"), j.get("predicate_direction_explicit"), j.get("ambiguous_expression"), pol, pr or "-", rps or "-"))
    L.append("  - stage1: " + " / ".join(rs))
    if d.get("lint_rejected_R"):
        L.append("  - R lint却下: " + "; ".join("%s(%s)" % (e.get("R"), ",".join(e.get("words"))) for e in d["lint_rejected_R"]))
    L.append("  - R採用: %s [%s] route=%s run_pass=%s" % (d.get("adopted_R"), d.get("adopted_flipped_component"), d.get("route"), d.get("stage1_run_pass")))
    if d.get("bypass_judge"):
        L.append("  - 判定役: 素通り(pred=false+polarity)")
    for v in d.get("stage1_5") or []:
        L.append("  - 判定役 %s: %s%s blocking_word=%r reason=%s" % (v["cid"], v["likelihood_raw"], "->medium(限定語昇格)" if v.get("promoted_low_to_medium") else "", v.get("blocking_word"), v.get("reason")))
    if d.get("existing_note"):
        en = d["existing_note"]
        L.append("  - cover: 既存notesあり=%s covers_R=%s dup_of_existing=%s (%s)" % (en.get("has"), en.get("covers_R"), en.get("dup_of_existing"), en.get("reason")))
    if d.get("stage2"):
        s2 = d["stage2"]
        L.append("  - stage2: result=%s r_echo一致=%s R被覆=%s lint=%s 台帳外英語=%s" % (s2.get("result"), s2.get("r_echo_match"), s2.get("r_coverage"), s2.get("lint_hits"), s2.get("english_not_in_ledger")))
    L.append("  - 最終: %s" % (("付与: " + attached_note) if attached_note else "付与なし dropped_by=%s" % d.get("dropped_by")))
    return L


def load_labels(path):
    """labels json: {"<pat>/<slug>/<fid>": {"match":"Y|P|N|-","type":"V|D|H|X|-","fab":bool,"vague":bool,"why":""},
    "<slug>/<fid>/existing": {"match":"Y|N"}, "<pat>/gate": {"label":"合格|軸ずれ|誤禁止","why":""}}"""
    return _load(path, {}) if path else {}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--patterns", required=True)
    ap.add_argument("--runs-dir", default=str(TRIAL / "runs"))
    ap.add_argument("--rerun-dir", default=None, help="同一台帳の2回目のruns dir(安定性。未指定なら出さない)")
    ap.add_argument("--targets", default=str(TRIAL / "eval" / "targets.json"))
    ap.add_argument("--holdout", default=str(TRIAL / "eval" / "holdout.json"))
    ap.add_argument("--eval-dir", default=str(TRIAL / "eval"))
    ap.add_argument("--tag", default="", help="出力ファイル名prefix(例: t04_)")
    ap.add_argument("--labels", default=None, help="Sonnet仮ラベルjson")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    ROOT = TRIAL.parents[1]
    tj = _load(a.targets)["themes"]
    hold = (_load(a.holdout, {"themes": {}}) or {"themes": {}})["themes"]
    themes = dict(tj)
    for k, v in hold.items():
        themes.setdefault(k, v)
    labels = load_labels(a.labels)
    lines, funnel = [], ["# t04 段別ファネル(対象fact+rollback gate_fact。機械出力)", ""]
    ex_cache = {}
    for pat in a.patterns.split(","):
        core_rows, hold_rows = [], []
        lines.append("## %s" % pat)
        lines.append("| theme | recall | extra | attach | rate | holdout_over_expected | stability | warnings | bypass/promote/lint/cover_skip | cost |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|")
        gate = None
        sheet = ["# content label sheet: %s" % pat, "", "| theme | fact_id | 対象/対象外 | note(逐語) | 既知誤読 | 一致 | 型 | 捏造 | 曖昧語流用 | 根拠 |", "|---|---|---|---|---|---|---|---|---|---|"]
        gen_hit, ex_hit, union_hit, total_cost = [], [], [], 0.0
        union_attached = union_facts = 0
        lab = {"Y": 0, "P": 0, "N": 0, "n_t": 0, "V": 0, "D": 0, "H": 0, "X": 0, "n_x": 0, "fab": 0, "vague": 0, "unlabeled": 0, "hold_wrong": 0}
        for slug, th in themes.items():
            d = Path(a.runs_dir) / pat / slug
            notes = _load(d / "notes.json")
            if notes is None:
                lines.append("| %s | (no run) |" % slug)
                continue
            prv = _load(d / "provenance.json", {})
            jall = _load(d / "judgments_all.json", [])
            total_cost += prv.get("cost_jpy", 0.0)
            r = E.eval_theme(notes, th["targets"], _load(d / "rejected.json", []), prv, jall, prv.get("prefix"))
            (hold_rows if slug in hold else core_rows).append(r)
            stab = "-"
            if a.rerun_dir:
                n2 = _load(Path(a.rerun_dir) / pat / slug / "notes.json")
                if n2 is not None:
                    s = stability([n["fact_id"] for n in notes], [n["fact_id"] for n in n2])
                    stab = "%.2f/%d/%d/%d" % (s["jaccard"], s["both"], s["only_a"], s["only_b"])
            elif prv.get("stage1_jaccard") is not None:
                stab = "stage1 %.2f" % prv["stage1_jaccard"]
            ho = holdout_over(r["attached"], th.get("expected_max")) if slug in hold else None
            mix = "%s/%s/%s/%s" % (prv.get("bypass_count", "-"), prv.get("promoted_low_to_medium", "-"), prv.get("lint_rejected_count", "-"), len(prv.get("cover_skipped") or []))
            lines.append("| %s | %d/%d | %d | %d/%s | %s | %s | %s | %d | %s | %s |" % (
                slug, r["hit"], r["targets"], r["extra"], r["attached"], E.fmt(r["fact_count"]), E.fmt(r["attach_rate"]),
                "-" if ho is None else ho, stab, r["warnings"], mix, E.fmt(prv.get("cost_jpy"))))
            if th.get("gate_fact"):
                gate = gate_eval(notes, th["gate_fact"])
            for n in notes:
                t = th["targets"].get(n["fact_id"])
                lb = labels.get("%s/%s/%s" % (pat, slug, n["fact_id"]), {})
                if slug not in hold:
                    if t:
                        lab["n_t"] += 1
                        if lb:
                            lab[lb.get("match", "N")] = lab.get(lb.get("match", "N"), 0) + 1
                        else:
                            lab["unlabeled"] += 1
                    else:
                        lab["n_x"] += 1
                        if lb:
                            lab[lb.get("type", "H")] = lab.get(lb.get("type", "H"), 0) + 1
                        else:
                            lab["unlabeled"] += 1
                    if lb.get("fab"):
                        lab["fab"] += 1
                    if lb.get("vague"):
                        lab["vague"] += 1
                elif lb.get("type") in ("H", "X"):
                    lab["hold_wrong"] += 1
                sheet.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                    slug, n["fact_id"], "対象" if t else "対象外", n["note"].replace("|", "\\|"), t["known_misreading"] if t else "-",
                    lb.get("match", ""), lb.get("type", ""), "有" if lb.get("fab") else ("無" if lb else ""), "有" if lb.get("vague") else ("無" if lb else ""), lb.get("why", "")))
            jm = {x["fact_id"]: x for x in jall}
            nm = {n["fact_id"]: n["note"] for n in notes}
            if slug not in hold:
                if th["txt"] not in ex_cache:
                    ex_cache[th["txt"]] = existing_prohibition_ids(str(ROOT / th["txt"]))
                exi = ex_cache[th["txt"]]
                att = {n["fact_id"] for n in notes}
                union_facts += r["fact_count"] or 0
                union_attached += len(att | set(exi))
                for f in th["targets"]:
                    k = "%s/%s" % (slug, f)
                    g_ok = f in att and labels.get("%s/%s/%s" % (pat, slug, f), {}).get("match") == "Y"
                    e_ok = f in exi and labels.get("%s/%s/existing" % (slug, f), {}).get("match") == "Y"
                    if g_ok:
                        gen_hit.append(k)
                    if e_ok:
                        ex_hit.append(k)
                    if g_ok or e_ok:
                        union_hit.append(k)
                    funnel += funnel_block(pat, slug, f, jm.get(f), nm.get(f))
        Path(a.eval_dir).mkdir(parents=True, exist_ok=True)
        (Path(a.eval_dir) / ("%s%s_content_label_sheet.md" % (a.tag, pat))).write_text("\n".join(sheet), encoding="utf-8")
        agg = E.aggregate(core_rows) if core_rows else None
        lines.append("")
        lines.append("### rollback Gate(別枠。機械チェックは候補判定。最終はFable。3値定義は eval/rollback_gate_labels.md)")
        if gate is None:
            lines.append("gate_fact対象テーマのrunなし")
        else:
            lines.append("- gate_fact=%s captured=%s result=%s reasons=%s" % (gate["gate_fact"], gate["captured"], gate["check"]["result"], gate["check"]["reasons"]))
            lines.append("- note全文: %s" % gate["note"])
            gl = labels.get("%s/gate" % pat, {})
            lines.append("- 3値仮ラベル(Sonnet): %s / 根拠: %s" % (gl.get("label", "(未)"), gl.get("why", "")))
        lines.append("")
        lines.append("### 合格条件(機械判定分+Sonnet仮ラベル分)")
        hov = [holdout_over(r["attached"], themes[s].get("expected_max")) for r, s in zip(hold_rows, [k for k in themes if k in hold and (Path(a.runs_dir) / pat / k / "notes.json").exists()])]
        hov = [x for x in hov if x is not None]
        for k, v in summarize_criteria(core_rows, hold_rows, hov if hold_rows else None).items():
            lines.append("- %s: %s" % (k, v))
        if agg:
            lines.append("- 総費用(この表のrun合計): %.2f円 / 平均字数 %.1f / 最大字数 %d / 警告 %d" % (total_cost, agg["avg_len"], agg["max_len"], agg["warnings"]))
        lines.append("- holdout 誤り(型H/X)ラベル数: %d(<=1が基準はholdout誤付与の方)" % lab["hold_wrong"])
        if lab["n_t"]:
            y, pp = lab.get("Y", 0), lab.get("P", 0)
            lines.append("- 内容一致(主=生成noteのみ, 対象付与%d件中): Y=%d P=%d N=%d → Y率=%.0f%% / (Y+P)率=%.0f%% / 未ラベル=%d" % (
                lab["n_t"], y, pp, lab.get("N", 0), 100.0 * y / lab["n_t"], 100.0 * (y + pp) / lab["n_t"], lab["unlabeled"]))
            lines.append("- 対象外付与%d件の内訳: 妥当(V)=%d / 変質止まり(D)=%d / 誤り(H+X)=%d ; 捏造=%d ; 曖昧語流用=%d" % (
                lab["n_x"], lab.get("V", 0), lab.get("D", 0), lab.get("H", 0) + lab.get("X", 0), lab["fab"], lab["vague"]))
            lines.append("- 副指標(和集合: 生成note+既存notes禁止文転記) 対象のY一致数: 生成のみ=%d, 既存のみ=%d, 和集合=%d / 14 ; 和集合付与率=%.0f%%" % (
                len(gen_hit), len(ex_hit), len(union_hit), 100.0 * union_attached / union_facts if union_facts else 0))
        lines.append("")
    txt = "\n".join(lines)
    (Path(a.out) if a.out else Path(a.eval_dir) / ("%seval_table_p04.md" % a.tag)).write_text(txt, encoding="utf-8")
    if a.tag:
        (Path(a.eval_dir) / ("%sfunnel.md" % a.tag)).write_text("\n".join(funnel), encoding="utf-8")
    print(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
