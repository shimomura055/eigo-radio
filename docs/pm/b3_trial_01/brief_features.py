#!/usr/bin/env python3
"""brief_features.py: B3 brief 36本の特徴量(決定論・標準ライブラリのみ・API/生成なし)。
usage: python brief_features.py [--runs DIR] [--ledgers DIR] [--out FILE]
出力 eval/brief_features.json: {"<slug>|<variant>|b<i>": {...}}
"""
import argparse, glob, json, os, re

SLUGS = ["meta", "hormuz", "space_weapons"]
VARIANTS = ["V0", "V1", "V2", "V3", "V5", "V6"]
FID = re.compile(r"\b(?:HC|HF|CONTROL|F)-\d+\b")
BUL = re.compile(r"^\s*(?:[・･•\-\*]|\d+[\.\)）])\s*")
SENT_END = re.compile(r"[。\.!?！？]")


def norm(s):
    return re.sub(r"[\s　、。，．,.・「」『』（）()\[\]:：;；/／\-－]", "", s)


def ledger_text(ledgers, slug):
    for c in (os.path.join(ledgers, slug, "control", "research_ledger", "verified_fact_ledger.txt"),
              os.path.join(ledgers, slug, "verified_fact_ledger.txt")):
        if os.path.isfile(c):
            body = []
            for ln in open(c, encoding="utf-8").read().splitlines():
                if ln.strip().startswith("notes_for_writer"):
                    continue
                body.append(ln)
            return norm("\n".join(body))
    return None


NEG = re.compile(r"とは書かない|と書かない|とは書かず|書かない|しない|とは書か")


def notes_text(ledgers, slug):
    """notes_for_writer行の本文を(全体, 否定形「〜とは書かない/しない」を含む文のみ)で返す(正規化済み)。"""
    for c in (os.path.join(ledgers, slug, "control", "research_ledger", "verified_fact_ledger.txt"),
              os.path.join(ledgers, slug, "verified_fact_ledger.txt")):
        if os.path.isfile(c):
            allv, negv = [], []
            for ln in open(c, encoding="utf-8").read().splitlines():
                t = ln.strip()
                if t.startswith("notes_for_writer"):
                    body = t.split(":", 1)[-1]
                    allv.append(body)
                    for sent in re.split(r"(?<=[。])", body):
                        if NEG.search(sent):
                            negv.append(sent)
            return norm("\n".join(allv)), norm("\n".join(negv))
    return None, None


def units(text):
    """M6の評価単位: 箇条書き1項目、または句点で区切った1文(Selected Facts本文のみ。Storyline節(別掲)と、Selected Facts内に複写された
    『Storyline：…』の最初の1文は単位に含めない=Storylineは cross_fact_qualifier で別途判定。見出し・注意行も除く)。"""
    out, sec = [], None
    for l in text.splitlines():
        m = re.match(r"^#+\s*(.*)$", l)
        if m:
            sec = "story" if "Storyline" in m.group(1) else ("facts" if "Selected Facts" in m.group(1) else None)
            continue
        if sec != "facts" or not l.strip() or re.match(r"^\s*注意", l):
            continue
        if BUL.match(l):
            out.append(BUL.sub("", l).strip())
        else:
            ss = [x.strip() for x in re.split(r"(?<=[。])", l) if x.strip()]
            if ss and re.match(r"^\s*Storyline\s*[:：]", ss[0]):
                ss = ss[1:]  # 複写されたStoryline文は単位外
            out += ss
    return out


def gram_hit(q, ref, n=12):
    if ref is None or len(q) < n:
        return 0
    return sum(1 for k in range(len(q) - n + 1) if q[k:k + n] in ref)


def find_brief(runs, slug, v, i):
    base = os.path.join(runs, slug, "nb", v, "b%d" % i)
    cands = [os.path.join(base, "storyline_b3", "selected_brief.md")]
    cands += sorted(glob.glob(os.path.join(base, "w*", "storyline_b3", "selected_brief.md")))
    for c in cands:
        if os.path.isfile(c):
            return c
    return None


def features(text, led, notes=None, negnotes=None):
    lines = text.splitlines()
    nonblank = [l for l in lines if l.strip()]
    in_facts = False
    facts, story_in_facts, bullets = [], False, 0
    quoted = []  # 12字率の対象: Storyline行・見出し・注意行を除く本文
    for l in lines:
        if re.match(r"^#+\s*Selected Facts", l):
            in_facts = True
            continue
        if re.match(r"^#+\s", l):
            in_facts = False
            continue
        if not in_facts or not l.strip():
            continue
        if re.match(r"^\s*Storyline\s*[:：]", l):
            story_in_facts = True
            continue
        if re.match(r"^\s*注意", l):
            continue
        if BUL.match(l):
            bullets += 1
            facts.append(l)
            quoted.append(l)
        else:
            quoted.append(l)
    n_fact = len(facts)
    if n_fact == 0:  # 箇条書きなし(段落/ID行形式): fact_id数で代替
        n_fact = len(set(FID.findall("\n".join(quoted))))
    q = norm("\n".join(BUL.sub("", l) for l in quoted))
    rate = None
    if led is not None and len(q) >= 12:
        grams = len(q) - 11
        hit = sum(1 for k in range(grams) if q[k:k + 12] in led)
        rate = round(hit / grams, 3)
    us = units(text)
    qn = norm("\n".join(us))
    nrate = None
    if notes is not None and len(qn) >= 12:
        nrate = round(gram_hit(qn, notes) / (len(qn) - 11), 3)
    neg_derived = sum(1 for u in us if len(norm(u)) >= 12 and negnotes and gram_hit(norm(u), negnotes) > 0)
    neg_form = sum(1 for u in us if NEG.search(u))
    return {
        "n_units": len(us),
        "notes_12gram_rate": nrate,
        "neg_note_derived_units": neg_derived,
        "neg_form_units": neg_form,
        "n_fact": n_fact,
        "lines": len(nonblank),
        "chars": len(text),
        "fact_id": bool(FID.search(text)),
        "storyline_line_in_facts": story_in_facts,
        "bullets": bullets,
        "ledger_12gram_rate": rate,
        "n_notes_lines": sum(1 for l in lines if re.match(r"^\s*注意", l)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="er052_output/open233_b3_trial_01/runs")
    ap.add_argument("--ledgers", default="er052_output/open233_polysemy_trial_02/ledgers")
    ap.add_argument("--out", default="er052_output/open233_b3_trial_01/eval/brief_features.json")
    ns = ap.parse_args()
    res, missing = {}, []
    for s in SLUGS:
        led = ledger_text(ns.ledgers, s)
        notes, negnotes = notes_text(ns.ledgers, s)
        for v in VARIANTS:
            for i in (1, 2):
                p = find_brief(ns.runs, s, v, i)
                if not p:
                    missing.append("%s|%s|b%d" % (s, v, i))
                    continue
                d = features(open(p, encoding="utf-8").read(), led, notes, negnotes)
                d["path"] = p.replace("\\", "/")
                res["%s|%s|b%d" % (s, v, i)] = d
    os.makedirs(os.path.dirname(os.path.abspath(ns.out)), exist_ok=True)
    with open(ns.out, "w", encoding="utf-8") as fh:
        json.dump({"briefs": res, "missing": missing}, fh, ensure_ascii=False, indent=2, sort_keys=True)
    print("briefs=%d (期待36) missing=%d out=%s" % (len(res), len(missing), ns.out))


if __name__ == "__main__":
    main()
