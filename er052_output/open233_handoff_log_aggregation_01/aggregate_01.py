# -*- coding: utf-8 -*-
"""OPEN-233-SELF-RECOVERY-TRIAL-01 委任_41: 既存ログの無料集計(分析専用)。

【性質】このスクリプトは既存の er052_output/open233_self_recovery_flow_runner_01_*/instances_*/*.json
を「読むだけ」の分析物であり、どこからも呼ばれない。受け渡し修正の実装ではない。
runner等の既存モジュールをimportしない(import時の副作用・API設定依存を避けるため)。
LLM/API/TTS/Web Searchは一切使わない(標準ライブラリのみ)。出力は同ディレクトリの
results_01.json と claims_detail_01.csv。

【「新しい受け渡し方式」の機械的な定義】(委任_41の「集計の定義」に厳密に従う)
Checkerが返したclaim_in_articleだけを入力とし、文字単位の照合L0〜L4のみ試す。
  L0 そのまま記事に含まれる
  L1 文字列全体を囲む1組の引用符・括弧(“ ” " ‘ ’ 「 」 『 』)を外すと含まれる
  L2 空白・改行の連続を1個の空白とみなす/曲線引用符・アポストロフィと直線を同一視
  L3 大文字小文字を同一視
  L4 引用断片(“…”「…」『…』)が2つ以上で、断片以外の残りがつなぎ語・句読点・空白だけの場合に限り、
     各断片を別々の範囲候補にしてL0〜L3で照合(残りに説明文があれば分解せず確定不能)
「確定」= 照合後の文字列が記事本文にちょうど1箇所出現。0箇所=不一致、2箇所以上=複数箇所一致。
使わないもの: 類似度・単語重なり・位置比・Stage 2(判定役)のhint引用・Ledger語彙・文全体への拡張。
(例外: 確定不能の「原因ラベル付け」と「参考値(hint引用で拾える件数)」だけは診断目的で類似度/hintを
 使うが、範囲の確定には一切使わない。)
"""
import csv
import difflib
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_NAMES = re.compile(r"(iter[5-8]|rep(7|8|9|1\d|2[01]))$")

# ---------------------------------------------------------------- 文字照合
QUOTE_PAIRS = [("“", "”"), ('"', '"'), ("‘", "’"), ("「", "」"), ("『", "』")]
CURLY_MAP = {"’": "'", "‘": "'", "‚": "'", "‛": "'", "“": '"', "”": '"', "„": '"'}


def find_all(text, sub):
    out, i = [], 0
    if not sub:
        return out
    while True:
        j = text.find(sub, i)
        if j < 0:
            return out
        out.append((j, j + len(sub)))
        i = j + len(sub)


def norm_with_map(text, lower):
    chars, spans = [], []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch.isspace():
            j = i
            while j < n and text[j].isspace():
                j += 1
            chars.append(" ")
            spans.append((i, j))
            i = j
            continue
        ch2 = CURLY_MAP.get(ch, ch)
        if lower:
            lo = ch2.lower()
            ch2 = lo if len(lo) == 1 else ch2
        chars.append(ch2)
        spans.append((i, i + 1))
        i += 1
    return "".join(chars), spans


def norm_str(s, lower):
    return norm_with_map(s.strip(), lower)[0]


def strip_one_pair(s):
    s = s.strip()
    if len(s) >= 2:
        for o, c in QUOTE_PAIRS:
            if s[0] == o and s[-1] == c:
                return s[1:-1].strip()
    return None


def match_levels(cand, text):
    """cand をL0〜L3で text に照合。返値 (status, level, stripped_used, spans)
    status: 'ok'(ちょうど1箇所)/'multi'(2箇所以上)/'none'"""
    raw = cand.strip()
    stripped = strip_one_pair(raw)
    # L0
    for label, v, st in (("L0", raw, False), ("L1", stripped, True)):
        if v:
            occ = find_all(text, v)
            if len(occ) == 1:
                return "ok", label, st, occ
            if len(occ) >= 2:
                return "multi", label, st, occ
    # L2 / L3 (生・括弧除去の両方)
    for label, lower in (("L2", False), ("L3", True)):
        nt, nm = norm_with_map(text, lower)
        for v, st in ((raw, False), (stripped, True)):
            if not v:
                continue
            nv = norm_str(v, lower)
            if not nv:
                continue
            occ = find_all(nt, nv)
            if len(occ) == 1:
                s, e = occ[0]
                return "ok", label, st, [(nm[s][0], nm[e - 1][1])]
            if len(occ) >= 2:
                return "multi", label, st, [(nm[a][0], nm[b - 1][1]) for a, b in occ]
    return "none", None, False, []


FRAG_RE = re.compile(r"“([^”]+)”|「([^」]+)」|『([^』]+)』")
CONNECT_RE = re.compile(r"\b(and|or)\b|[&,;、，；と/／.。:：]|および|\s", re.I)


def split_fragments(claim):
    frags = [next(g for g in m.groups() if g is not None) for m in FRAG_RE.finditer(claim)]
    rest = FRAG_RE.sub("", claim)
    rest_clean = CONNECT_RE.sub("", rest)
    return frags, rest, rest_clean


JA_RE = re.compile(r"[぀-ゟ゠-ヿ一-鿿]")


def is_ja(s):
    t = re.sub(r"\s", "", s)
    return bool(t) and len(JA_RE.findall(t)) / len(t) >= 0.15


# ---------------------------------------------------------------- 文分割(分類専用)
SENT_END = re.compile(r"[.!?。！？][\"”’」』)]*(?=\s|$)|\n\s*\n")


def sentence_segments(text):
    segs, pos = [], 0
    for m in SENT_END.finditer(text):
        end = m.start() if m.group(0).strip() == "" else m.end()
        segs.append((pos, end))
        pos = m.end()
    segs.append((pos, len(text)))
    out = []
    for a, b in segs:
        while a < b and text[a].isspace():
            a += 1
        while b > a and text[b - 1].isspace():
            b -= 1
        if b > a:
            out.append((a, b))
    return out


def classify_span(span, text):
    a, b = span
    segs = sentence_segments(text)
    hit = [(i, s) for i, s in enumerate(segs) if s[0] < b and s[1] > a]
    if len(hit) >= 2:
        return "A2", len(hit), None
    if len(hit) == 1:
        s = hit[0][1]
        core = text[a:b].strip().strip("“”\"‘’「」『』").strip()
        seg = text[s[0]:s[1]].strip().strip("“”\"‘’「」『』").strip()
        return "A1", 1, ("whole" if core == seg else "part")
    return "A1", 1, "part"


# ---------------------------------------------------------------- 解決(新しい受け渡し方式)
def resolve_in_text(claim, text):
    """1つの記事本文(EN or JA)に対し claim の範囲を確定する。
    返値 dict: status(ok/multi/none/explanatory), level, spans[(a,b)], frag_info"""
    st, lv, strp, spans = match_levels(claim, text)
    if st == "ok":
        return {"status": "ok", "level": lv, "spans": spans, "stripped": strp}
    if st == "multi":
        return {"status": "multi", "level": lv, "spans": spans, "stripped": strp}
    frags, rest, rest_clean = split_fragments(claim)
    if len(frags) >= 2 and rest_clean == "":
        sp, lvs, bad = [], [], None
        for f in frags:
            s2, l2, _st2, spans2 = match_levels(f, text)
            if s2 != "ok":
                bad = (f, s2)
                break
            sp.append(spans2[0])
            lvs.append(l2)
        if bad:
            return {"status": "frag_unresolved", "level": "L4", "spans": [], "bad_fragment": bad[0],
                    "bad_status": bad[1]}
        return {"status": "ok", "level": "L4", "spans": sp, "frag_levels": lvs, "stripped": False}
    if len(frags) >= 1 and rest_clean != "":
        return {"status": "explanatory", "level": None, "spans": []}
    return {"status": "none", "level": None, "spans": []}


def best_sentence_ratio(claim, text):
    sents = re.split(r"(?<=[。.!?])", text)
    sents = [s.strip() for s in sents if s.strip()]
    if not sents:
        return 0.0
    c = claim.strip().strip("“”\"‘’「」『』")
    return max(difflib.SequenceMatcher(None, c, s).ratio() for s in sents)


POSITIONAL_RE = re.compile(r"^(the\s+)?(paragraph|title|heading|headline|in one line|hook|section|lead|opening|"
                           r"closing|final|first|second|third|last|point|body|summary|whole|entire)\b", re.I)


def diagnose_mismatch(claim, en, ja):
    if "…" in claim or "..." in claim:
        return "省略記号"
    if POSITIONAL_RE.match(claim.strip().strip("“”\"")):
        return "説明文・位置指示(引用なし)"
    texts = [t for t in (ja if is_ja(claim) else en, ) if t]
    if not texts:
        return "その他"
    r = max(best_sentence_ratio(claim, t) for t in texts)
    if r >= 0.6:
        return "言い換え・要約(類似文あり、診断のみ)"
    return "その他(類似文なし)"


def resolve_claim(claim, en, ja):
    """EN/JA両方に対して確定を試みる。返値: dict(category, ...)
    category: A1/A2/A3/A4/UNDET"""
    claim_s = (claim or "").strip()
    if not claim_s:
        return {"cat": "A4", "a4": "other", "cause": "空文字", "lang": None, "spans": []}
    ja_claim = is_ja(claim_s)
    results = {}
    if en is not None:
        results["EN"] = resolve_in_text(claim_s, en)
    if ja is not None:
        results["JA"] = resolve_in_text(claim_s, ja)
    if not results:
        return {"cat": "UNDET", "undet": "no_text", "lang": None, "spans": []}
    ok_langs = [k for k, v in results.items() if v["status"] == "ok"]
    if ok_langs:
        lang = "EN" if "EN" in ok_langs else "JA"
        r = results[lang]
        txt = en if lang == "EN" else ja
        spans = r["spans"]
        out = {"lang": lang, "level": r["level"], "spans": spans, "both_ok": len(ok_langs) == 2,
               "stripped": r.get("stripped", False), "frag_levels": r.get("frag_levels")}
        if r["level"] == "L4":
            out["cat"] = "A3"
            gaps = []
            order = sorted(spans)
            for (a1, b1), (a2, b2) in zip(order, order[1:]):
                between = txt[b1:a2]
                if between.strip() == "":
                    gaps.append("adjacent")
                else:
                    n_between = max(0, len([1 for s in sentence_segments(txt) if s[0] >= b1 and s[1] <= a2]))
                    gaps.append(f"separated({n_between}文挟む)")
            out["gaps"] = gaps
            out["span_classes"] = [classify_span(s, txt)[0:3] for s in spans]
        else:
            c, n, sub = classify_span(spans[0], txt)
            out["cat"] = c
            out["n_sent"] = n
            out["sub"] = sub
        return out
    # 確定せず
    # JA文字列だがJA本文の記録がない -> 判定不能
    if ja_claim and ja is None:
        return {"cat": "UNDET", "undet": "ja_text_missing", "lang": None, "spans": []}
    if (not ja_claim) and en is None:
        return {"cat": "UNDET", "undet": "no_text", "lang": None, "spans": []}
    sts = [v["status"] for v in results.values()]
    base = {"lang": None, "spans": [], "cat": "A4"}
    if "multi" in sts:
        base["a4"] = "multi"
        base["cause"] = "複数箇所一致"
        return base
    if "explanatory" in sts:
        base["a4"] = "explanatory"
        nfr = len(split_fragments(claim_s)[0])
        base["cause"] = "L4条件を満たさない説明文混在" + ("(断片2つ以上+説明文)" if nfr >= 2 else "(断片1つ+説明文)")
        return base
    if "frag_unresolved" in sts:
        base["a4"] = "mismatch"
        base["cause"] = "L4断片が記事に1箇所で一致しない"
        return base
    base["a4"] = "mismatch"
    base["cause"] = diagnose_mismatch(claim_s, en, ja)
    return base


# ---------------------------------------------------------------- 現行(記録上の実際)の再現
BRACKET_PATTERNS = [re.compile(r"“([^”\n]{8,220})”"), re.compile(r"「([^」\n]{4,220})」"),
                    re.compile(r"『([^』\n]{4,220})』")]


def hint_candidates(hint):
    cands = []
    for pat in BRACKET_PATTERNS:
        for m in pat.finditer(hint or ""):
            f = m.group(1).strip()
            if f:
                cands.append(f)
    parts = (hint or "").split('"')
    for i in range(1, len(parts), 2):
        f = parts[i].strip()
        if len(f) >= 8:
            cands.append(f)
    return cands


def all_quoted_fragments(text):
    found = []
    for pat in BRACKET_PATTERNS:
        for m in pat.finditer(text or ""):
            f = m.group(1).strip()
            if f and f not in found:
                found.append(f)
    return found


def er010_split(text):
    flat = " ".join(l.strip() for l in text.splitlines() if l.strip() and not l.strip().startswith("#"))
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z“\"])", flat) if s.strip()]


def replay_locate(claim, hint, text):
    """runner.locate_targetの順序の再現(ENのみ)。返値(target_str|None, method_token)。
    ※再現であり記録そのものではない。記録のmethod文字列と照合して忠実度を確認する。"""
    c = hint_candidates(hint)
    if c:
        longest = max(c, key=len)
        if longest in text:
            return longest, "rewrite_hint_quote"
        # 実runnerは最長1件のみ判定する(追記されるquality constraint内の引用が最長の場合は不一致)。
        # 本再現ではconstraint文言を持たないため、最長が不在でも他の在る候補は採用しない(runner同様)。
    frs = all_quoted_fragments(claim)
    if len(frs) >= 2:
        pos = []
        okf = True
        for f in frs:
            i = text.find(f)
            if i < 0:
                okf = False
                break
            pos.append((i, i + len(f)))
        if okf:
            a, b = min(p[0] for p in pos), max(p[1] for p in pos)
            if b > a and (b - a) <= 600 and "\n\n" not in text[a:b]:
                return text[a:b], "multi_quote_span"
    cs = (claim or "").strip()
    if cs and cs in text:
        return cs, "exact_substring"
    sents = [s.strip() for s in re.split(r"(?<=[。.!?])", text) if s.strip()]
    if sents:
        scored = sorted(((difflib.SequenceMatcher(None, claim, s).ratio(), s) for s in sents),
                        key=lambda x: x[0], reverse=True)
        br, best = scored[0]
        sr = scored[1][0] if len(scored) > 1 else 0.0
        if br >= 0.5 and (br - sr) >= 0.08:
            return best, f"sequence_matcher(ratio={round(br, 2)})"
    # er010 word overlap
    if cs and cs in text:
        return cs, "er010_exact"
    cw = set(re.findall(r"[a-z']+", (claim or "").lower()))
    best, bs = None, 0.0
    for s in er010_split(text):
        sw = set(re.findall(r"[a-z']+", s.lower()))
        if not sw or not cw:
            continue
        ov = len(cw & sw) / len(cw | sw)
        if ov > bs:
            best, bs = s, ov
    if best is not None and bs >= 0.25:
        return best, f"er010_word_overlap(sentence_fallback(overlap={round(bs, 2)}))"
    return None, "not_found"


def method_token(method):
    m = method or ""
    for t in ("rewrite_hint_quote", "multi_quote_span", "exact_substring", "sequence_matcher",
              "er010_word_overlap"):
        if t in m:
            return t
    return None


def short_token(tok):
    if not tok:
        return None
    for t in ("rewrite_hint_quote", "multi_quote_span", "exact_substring", "sequence_matcher",
              "er010_word_overlap"):
        if tok.startswith(t) or (t == "exact_substring" and tok == "er010_exact"):
            return t
    return None


def rel_cur_new(T, new_spans):
    """T=(a,b) 現行の対象、new_spans=新方式の範囲リスト(同じ記事座標)。"""
    a, b = T
    if len(new_spans) == 1 and new_spans[0] == (a, b):
        return "same(同じ)"
    covers_all = all(a <= s and e <= b for s, e in new_spans)
    if covers_all:
        return "current_wider(現行が拡大: 現行⊃新)"
    inside = any(s <= a and b <= e for s, e in new_spans)
    if inside:
        return "current_narrower(現行が縮小: 現行⊂新)"
    overlap = any(min(b, e) > max(a, s) for s, e in new_spans)
    if overlap:
        return "partial_overlap(一部重なり)"
    return "elsewhere(別の箇所)"


# ---------------------------------------------------------------- 本体
def load_runs():
    runs, dirs = [], []
    for dd in sorted(glob.glob(os.path.join(ROOT, "er052_output", "open233_self_recovery_flow_runner_01_*"))):
        name = os.path.basename(dd).split("_01_", 1)[1]
        if not TARGET_NAMES.match(name):
            continue
        fs = sorted(glob.glob(os.path.join(dd, "instances_*", "*.json")))
        dirs.append((name, len(fs)))
        for f in fs:
            with open(f, encoding="utf-8") as fh:
                d = json.load(fh)
            if "cycles" not in d:
                continue
            rel = os.path.relpath(f, os.path.join(ROOT, "er052_output")).replace("\\", "/")
            rel = rel.replace("open233_self_recovery_flow_runner_01_", "")
            runs.append({"path": rel, "dir": name, "d": d})
    return runs, dirs


def cycle_texts(cycles, i):
    c = cycles[i]
    en = c.get("en_text_before_rewrite")
    ja = c.get("ja_text_before_rewrite")
    src_en = "same_cycle_before" if en is not None else None
    src_ja = "same_cycle_before" if ja is not None else None
    if i > 0:
        p = cycles[i - 1]
        if en is None and p.get("en_text_after_rewrite") is not None:
            en, src_en = p["en_text_after_rewrite"], "prev_cycle_after"
        if ja is None and p.get("ja_text_after_rewrite") is not None:
            ja, src_ja = p["ja_text_after_rewrite"], "prev_cycle_after"
        # 仮定の検証用: 両方あるとき一致するか
        mism = (c.get("en_text_before_rewrite") is not None and p.get("en_text_after_rewrite") is not None
                and c["en_text_before_rewrite"] != p["en_text_after_rewrite"])
    else:
        mism = False
    return en, ja, src_en, src_ja, mism


def build_borrow_map(runs):
    """補助集計用: 同一instance(fixture)のcycle1本文(記録あり)が全run一致で1種類のときだけ借用する。"""
    en_t, ja_t = defaultdict(set), defaultdict(set)
    for run in runs:
        if not run["d"]["cycles"]:
            continue
        c0 = run["d"]["cycles"][0]
        if c0.get("en_text_before_rewrite") is not None:
            en_t[run["d"]["instance_id"]].add(c0["en_text_before_rewrite"])
        if c0.get("ja_text_before_rewrite") is not None:
            ja_t[run["d"]["instance_id"]].add(c0["ja_text_before_rewrite"])
    return {"en": {k: next(iter(v)) for k, v in en_t.items() if len(v) == 1},
            "ja": {k: next(iter(v)) for k, v in ja_t.items() if len(v) == 1}}


def analyze(borrow_map, runs, dirs):
    rows = []  # 指摘ごとの明細
    run_flags = {}
    assumption_mismatch = 0
    assumption_checked = 0
    discarded_locs = []  # K2展開で捨てられたsame_fact_id_locations要素
    seen_loc = set()
    replay_val = Counter()
    for run in runs:
        d = run["d"]
        cycles = d["cycles"]
        iid = d["instance_id"]
        for ci, c in enumerate(cycles):
            en, ja, src_en, src_ja, mism = cycle_texts(cycles, ci)
            if borrow_map and ci == 0:
                if en is None and iid in borrow_map["en"]:
                    en, src_en = borrow_map["en"][iid], "borrowed_same_fixture"
                if ja is None and iid in borrow_map["ja"]:
                    ja, src_ja = borrow_map["ja"][iid], "borrowed_same_fixture"
            if ci > 0 and c.get("en_text_before_rewrite") is not None and cycles[ci - 1].get(
                    "en_text_after_rewrite") is not None:
                assumption_checked += 1
                assumption_mismatch += 1 if mism else 0
            stage2 = c["stage2_results"]
            blocking_idx = [k for k, s in enumerate(stage2) if s["materiality"] == "BLOCKING"]
            rr = c.get("rewrite_records")
            rr_map = {}
            if rr is not None and len(rr) == len(blocking_idx):
                rr_map = {k: rr[j] for j, k in enumerate(blocking_idx)}
            for k, s in enumerate(stage2):
                dev = s["dev"]
                if s.get("detected_by") == "precheck":
                    kind = "K3"
                elif dev.get("enumeration_source_claim"):
                    kind = "K2"
                else:
                    kind = "K1"
                claim = dev.get("claim_in_article", "")
                row = {
                    "run": run["path"], "dir": run["dir"], "instance": iid, "cycle": c["cycle"], "k": k,
                    "kind": kind, "phase": "stage1" if c["cycle"] == 1 else "recheck",
                    "origin": s.get("origin"), "fact": s.get("related_fact_id"),
                    "materiality": s["materiality"], "claim": claim,
                    "claim_text_eq": (s.get("claim_text") == claim),
                    "blocking": s["materiality"] == "BLOCKING",
                    "final_state": d["final_state"], "stage4_reason": d["stage4_reason"],
                }
                if kind == "K1":
                    # K2展開で捨てられたlocation要素
                    locs = dev.get("same_fact_id_locations")
                    if isinstance(locs, list):
                        for loc in locs:
                            if not isinstance(loc, str):
                                continue
                            ls = loc.strip()
                            if not ls or ls == claim.strip():
                                continue
                            key = (iid, ci, ls)
                            if key in seen_loc:
                                continue
                            seen_loc.add(key)
                            if en is None:
                                continue
                            if ls not in en:
                                rl = resolve_claim(ls, en, ja)
                                discarded_locs.append({"run": run["path"], "cycle": c["cycle"], "loc": ls[:120],
                                                       "would_be": rl["cat"] + (":" + str(rl.get("a4") or rl.get("undet") or "")),
                                                       "level": rl.get("level")})
                    res = resolve_claim(claim, en, ja)
                    row.update({
                        "cat": res["cat"], "level": res.get("level"), "lang": res.get("lang"),
                        "sub": res.get("sub"), "n_sent": res.get("n_sent"), "gaps": res.get("gaps"),
                        "a4": res.get("a4"), "cause": res.get("cause"), "undet": res.get("undet"),
                        "spans": res.get("spans"), "span_classes": res.get("span_classes"),
                        "frag_levels": res.get("frag_levels"), "both_ok": res.get("both_ok"),
                        "text_src_en": src_en, "text_src_ja": src_ja,
                    })
                    txt = en if res.get("lang") == "EN" else ja
                    if res.get("spans") and txt is not None:
                        row["new_ranges"] = [txt[a:b] for a, b in res["spans"]]
                    # Stage 2 hint引用による救済(参考値のみ)
                    if res["cat"] == "A4" and row["blocking"]:
                        hint = s.get("rewrite_hint") or ""
                        cands = hint_candidates(hint)
                        hit = None
                        for tname, tx in (("EN", en), ("JA", ja)):
                            if tx is None:
                                continue
                            present = [x for x in cands if x in tx]
                            if present:
                                best = max(present, key=len)
                                hit = (tname, tx.count(best) == 1, best[:100])
                                break
                        row["hint_rescue"] = (hit[1] if hit else False)
                        row["hint_rescue_text"] = hit[2] if hit else None
                    # 現行との比較(BLOCKINGでRewrite実行)
                    if row["blocking"]:
                        rec = rr_map.get(k)
                        row["rewrite_executed"] = rec is not None
                        if rec is not None:
                            row["rr_method"] = rec["method"]
                            row["rr_ladder"] = rec.get("ladder_level_used")
                            row["rr_guard_ok"] = rec.get("guard_ok")
                            row["rr_n_blocking_in_cycle"] = len(blocking_idx)
                            tok = method_token(rec["method"])
                            row["rr_token"] = tok
                            T, rtok = (None, "no_en_text")
                            if en is not None:
                                T, rtok = replay_locate(claim, s.get("rewrite_hint") or "", en)
                            row["replay_token"] = rtok
                            if tok is not None:
                                agree = short_token(rtok) == tok
                                if tok == "sequence_matcher" or tok == "er010_word_overlap":
                                    mm = re.search(r"(ratio|overlap)=([\d.]+)", rec["method"])
                                    mr = re.search(r"(ratio|overlap)=([\d.]+)", rtok or "")
                                    agree = agree and bool(mm and mr and mm.group(2) == mr.group(2))
                                replay_val["agree" if agree else "disagree"] += 1
                                row["replay_agree"] = agree
                            else:
                                row["replay_agree"] = None
                            if T is not None and en is not None:
                                p = en.find(T)
                                row["cur_target"] = T[:300]
                                row["cur_span"] = (p, p + len(T)) if p >= 0 else None
                            if rec["method"] and any(x in rec["method"] for x in (
                                    "target_not_found", "target_not_locatable", "j1_failed")) and tok is None:
                                row["cur_nolocate"] = True
                            # 関係
                            if res["cat"] in ("A1", "A2", "A3") and res.get("lang") == "EN":
                                if row.get("cur_span"):
                                    row["relation"] = rel_cur_new(row["cur_span"], res["spans"])
                                    if row["relation"].startswith("current_narrower"):
                                        # 新の範囲が2文以上/離れた複数箇所なら「文の取りこぼし」型、
                                        # 1文以内なら「語句・句レベルに絞った」型(最小修正優先ルールと整合しうる)
                                        row["relation"] = ("current_narrower_drops_sentence(現行⊂新、新が2文以上/複数箇所: 一部の文のみ対象)"
                                                           if res["cat"] in ("A2", "A3") else
                                                           "current_narrower_within_one_sentence(現行⊂新、新は1文以内: 語句・句に絞った対象)")
                                elif row.get("cur_nolocate"):
                                    row["relation"] = "current_no_target(現行は対象特定不能/全文fallback)"
                                elif tok is None and T is None:
                                    row["relation"] = "record_insufficient(記録不足)"
                                else:
                                    row["relation"] = "record_insufficient(記録不足)"
                            elif res["cat"] in ("A1", "A2", "A3"):
                                row["relation"] = "new_resolved_in_JA_only(EN比較不可)"
                            elif res["cat"] == "A4":
                                row["relation"] = "new_unresolved(新で確定不能)"
                            else:
                                row["relation"] = "undetermined(本文記録なし)"
                        else:
                            row["relation"] = "rewrite_not_executed"
                rows.append(row)
        # run単位フラグはあとで集計
    # ---- 以降: 集計
    k1 = [r for r in rows if r["kind"] == "K1"]
    kcount = Counter(r["kind"] for r in rows)
    kcount_blocking = Counter(r["kind"] for r in rows if r["blocking"])

    def uniq_first(rs):
        seen = {}
        incons = 0
        for r in rs:
            key = (r["instance"], r["claim"])
            if key not in seen:
                seen[key] = r
            else:
                if seen[key].get("cat") != r.get("cat"):
                    incons += 1
        return list(seen.values()), incons

    def table(rs):
        t = Counter()
        for r in rs:
            cat = r["cat"]
            if cat == "A1":
                t[f"A1:{r['sub']}"] += 1
            elif cat == "A4":
                t[f"A4:{r['a4']}"] += 1
            elif cat == "UNDET":
                t[f"UNDET:{r['undet']}"] += 1
            else:
                t[cat] += 1
        return dict(t)

    def level_table(rs):
        t = Counter()
        for r in rs:
            if r["cat"] in ("A1", "A2", "A3"):
                t[r["level"]] += 1
        return dict(t)

    def a4_cause(rs):
        return dict(Counter(r["cause"] for r in rs if r["cat"] == "A4"))

    def summarize(rs):
        det = [r for r in rs if r["cat"] != "UNDET"]
        res_n = len([r for r in det if r["cat"] in ("A1", "A2", "A3")])
        return {"n_rows": len(rs), "n_determinable": len(det), "table": table(rs), "levels": level_table(rs),
                "a4_cause": a4_cause(rs),
                "resolved": res_n,
                "resolved_rate": round(res_n / len(det), 4) if det else None,
                "unresolved": len(det) - res_n,
                "unresolved_rate": round((len(det) - res_n) / len(det), 4) if det else None}

    out = {}
    out["scope"] = {
        "dirs": dirs, "n_dirs": len(dirs), "n_files_with_cycles": len(runs),
        "n_files_total": sum(n for _, n in dirs),
        "rows_total": len(rows), "kind_counts": dict(kcount), "kind_counts_blocking": dict(kcount_blocking),
        "K1_claim_text_neq_claim_in_article": sum(1 for r in k1 if not r["claim_text_eq"]),
        "assumption_check_prev_after_vs_this_before": {"pairs_checked": assumption_checked,
                                                        "mismatches": assumption_mismatch},
        "replay_validation_vs_recorded_method_token": dict(replay_val),
    }
    k1_blk = [r for r in k1 if r["blocking"]]
    k1_nonblk = [r for r in k1 if not r["blocking"]]
    u_all, inc_all = uniq_first(k1)
    u_blk, inc_blk = uniq_first(k1_blk)
    out["A"] = {
        "K1_all_rows": summarize(k1), "K1_all_unique": summarize(u_all), "K1_unique_inconsistent_class": inc_all,
        "K1_blocking_rows": summarize(k1_blk), "K1_blocking_unique": summarize(u_blk),
        "K1_blocking_unique_inconsistent_class": inc_blk,
        "K1_nonblocking_rows": summarize(k1_nonblk),
        "K1_by_phase_rows": {p: summarize([r for r in k1 if r["phase"] == p]) for p in ("stage1", "recheck")},
        "K1_blocking_by_phase_rows": {p: summarize([r for r in k1_blk if r["phase"] == p])
                                     for p in ("stage1", "recheck")},
        "A3_gaps": dict(Counter(g for r in k1 if r["cat"] == "A3" for g in r["gaps"])),
        "A3_gaps_blocking": dict(Counter(g for r in k1_blk if r["cat"] == "A3" for g in r["gaps"])),
        "resolved_lang": dict(Counter(r["lang"] for r in k1 if r["cat"] in ("A1", "A2", "A3"))),
        "both_ok_count": sum(1 for r in k1 if r.get("both_ok")),
    }
    by_inst = defaultdict(list)
    for r in k1:
        by_inst[r["instance"]].append(r)
    out["A"]["by_instance_rows"] = {i: summarize(rs) for i, rs in sorted(by_inst.items())}
    out["A"]["by_instance_blocking_rows"] = {
        i: summarize([r for r in rs if r["blocking"]]) for i, rs in sorted(by_inst.items())}
    out["A"]["by_instance_blocking_unique"] = {
        i: summarize(uniq_first([r for r in rs if r["blocking"]])[0]) for i, rs in sorted(by_inst.items())}
    # meta_run03_standard 内訳(全/rep19-21)
    meta = [r for r in k1 if r["instance"] == "meta_run03_standard"]
    out["A"]["meta_all_rows"] = summarize(meta)
    out["A"]["meta_rep19_21_rows"] = summarize([r for r in meta if r["dir"] in ("rep19", "rep20", "rep21")])
    out["A"]["meta_rep19_21_unique"] = summarize(
        uniq_first([r for r in meta if r["dir"] in ("rep19", "rep20", "rep21")])[0])
    out["A"]["meta_blocking_rows"] = summarize([r for r in meta if r["blocking"]])
    out["A"]["meta_rep19_21_blocking_rows"] = summarize(
        [r for r in meta if r["blocking"] and r["dir"] in ("rep19", "rep20", "rep21")])

    # K2/K3
    k2 = [r for r in rows if r["kind"] == "K2"]
    k3 = [r for r in rows if r["kind"] == "K3"]
    out["K2K3"] = {
        "K2_rows": len(k2), "K2_blocking_rows": sum(1 for r in k2 if r["blocking"]),
        "K2_unique": len({(r["instance"], r["claim"]) for r in k2}),
        "K3_rows": len(k3), "K3_blocking_rows": sum(1 for r in k3 if r["blocking"]),
        "K3_unique": len({(r["instance"], r["claim"]) for r in k3}),
        "discarded_same_fact_id_locations_count(K1由来、(instance,cycle,loc)重複除外)": len(discarded_locs),
        "discarded_examples": discarded_locs[:12],
        "discarded_unique_strings": len({x["loc"] for x in discarded_locs}),
        "discarded_would_be_class(新方式の照合を当てた場合)": dict(Counter(x["would_be"] for x in discarded_locs)),
        "discarded_paragraph_beginning": [x for x in discarded_locs if x["loc"].startswith("Paragraph beginning")],
    }

    # 現行との比較(K1 BLOCKINGでRewrite実行)
    exe = [r for r in k1_blk if r.get("rewrite_executed")]
    rel_t = Counter(r["relation"] for r in exe)
    meth_t = defaultdict(Counter)
    for r in exe:
        key = r.get("rr_token") or ("paired/other:" + re.sub(r"[\d.]+", "N", r.get("rr_method") or ""))
        meth_t[key][r["relation"]] += 1
    exe_u, _ = uniq_first(exe)
    out["compare_current"] = {
        "k1_blocking_rows": len(k1_blk), "executed_rows": len(exe),
        "not_executed_rows": len([r for r in k1_blk if r.get("relation") == "rewrite_not_executed"]),
        "relation_rows": dict(rel_t),
        "relation_unique_first": dict(Counter(r["relation"] for r in exe_u)),
        "by_method_token": {k: dict(v) for k, v in meth_t.items()},
        "multi_blocking_in_cycle_rows": sum(1 for r in exe if r.get("rr_n_blocking_in_cycle", 1) > 1),
        "ladder_levels": dict(Counter(r.get("rr_ladder") for r in exe)),
        "replay_validation": dict(replay_val),
        "replay_agree_by_token": {t: dict(Counter(r.get("replay_agree") for r in exe if r.get("rr_token") == t))
                                  for t in ("rewrite_hint_quote", "exact_substring", "sequence_matcher",
                                            "er010_word_overlap", "multi_quote_span")},
    }

    # D: 確定不能BLOCKING・hint救済(参考)
    unres_blk = [r for r in k1_blk if r["cat"] == "A4"]
    unres_blk_u, _ = uniq_first(unres_blk)
    out["D"] = {
        "A4_blocking_rows": len(unres_blk), "A4_blocking_unique": len(unres_blk_u),
        "A4_blocking_rows_hint_rescuable(参考・採用しない)": sum(1 for r in unres_blk if r.get("hint_rescue")),
        "A4_blocking_unique_hint_rescuable": sum(1 for r in unres_blk_u if r.get("hint_rescue")),
        "A4_blocking_cause_rows": dict(Counter(r["cause"] for r in unres_blk)),
        "A4_blocking_cause_unique": dict(Counter(r["cause"] for r in unres_blk_u)),
        "undetermined_blocking_rows": len([r for r in k1_blk if r["cat"] == "UNDET"]),
        "undetermined_blocking_by_reason": dict(Counter(r["undet"] for r in k1_blk if r["cat"] == "UNDET")),
    }
    # run単位
    by_run = defaultdict(list)
    for r in rows:
        by_run[r["run"]].append(r)
    run_info = {}
    for run in runs:
        rs = [r for r in by_run[run["path"]] if r["kind"] == "K1"]
        d = run["d"]
        blk = [r for r in rs if r["blocking"]]
        info = {
            "dir": run["dir"], "instance": d["instance_id"], "final_state": d["final_state"],
            "stage4_reason": d["stage4_reason"], "n_cycles": len(d["cycles"]),
            "has_blocking_k1": bool(blk),
            "has_blocking_unresolved": any(r["cat"] == "A4" for r in blk),
            "has_blocking_undetermined": any(r["cat"] == "UNDET" for r in blk),
            "n_blocking_unresolved": sum(1 for r in blk if r["cat"] == "A4"),
            "relations": dict(Counter(r.get("relation") for r in blk)),
            "has_diff_target": any((r.get("relation") or "").startswith((
                "current_wider", "current_narrower_drops_sentence", "partial_overlap", "elsewhere")) for r in blk),
            "has_diff_target_incl_within_sentence": any((r.get("relation") or "").startswith((
                "current_wider", "current_narrower", "partial_overlap", "elsewhere")) for r in blk),
            "has_current_no_target": any(r.get("relation", "").startswith("current_no_target") for r in blk),
        }
        run_info[run["path"]] = info
    is_stage4 = lambda i: i["final_state"] == "STAGE4_ESCALATION"
    all_runs = list(run_info.values())

    def run_summary(infos):
        n = len(infos)
        s4 = [i for i in infos if is_stage4(i)]
        res = [i for i in infos if not is_stage4(i)]
        flagged = [i for i in infos if i["has_blocking_unresolved"]]
        return {
            "n_runs": n, "n_stage4": len(s4),
            "stage4_reasons": dict(Counter(i["stage4_reason"] for i in s4)),
            "runs_with_blocking_unresolved": len(flagged),
            "rate_of_runs": round(len(flagged) / n, 4) if n else None,
            "flagged_final_states": dict(Counter(i["final_state"] for i in flagged)),
            "flagged_stage4_reasons": dict(Counter(i["stage4_reason"] for i in flagged if is_stage4(i))),
            "upper_bound_increase(現行解消→新で確定不能あり)": len([i for i in flagged if not is_stage4(i)]),
            "stage4_runs_with_diff_target(減りうる側の上限)": len([i for i in s4 if i["has_diff_target"]]),
            "stage4_runs_with_diff_target_incl_within_sentence": len(
                [i for i in s4 if i["has_diff_target_incl_within_sentence"]]),
            "stage4_runs_with_diff_target_or_no_target": len(
                [i for i in s4 if i["has_diff_target"] or i["has_current_no_target"]]),
            "runs_with_blocking_undetermined": len([i for i in infos if i["has_blocking_undetermined"]]),
            "runs_with_blocking_k1": len([i for i in infos if i["has_blocking_k1"]]),
            "stage4_and_unresolved_and_diff": len([i for i in s4 if i["has_blocking_unresolved"]
                                                    and i["has_diff_target"]]),
        }
    out["D"]["runs_all"] = run_summary(all_runs)
    out["D"]["runs_iter8_s1_29"] = run_summary([i for p, i in run_info.items()
                                                 if i["dir"] == "iter8" and "instances_s1" in p])
    out["D"]["runs_iter8_all"] = run_summary([i for i in all_runs if i["dir"] == "iter8"])
    out["D"]["runs_rep16plus"] = run_summary([i for i in all_runs if i["dir"] in (
        "rep16", "rep17", "rep18", "rep19", "rep20", "rep21")])
    out["D"]["runs_meta_all"] = run_summary([i for i in all_runs if i["instance"] == "meta_run03_standard"])
    out["D"]["runs_meta_rep16plus"] = run_summary([i for i in all_runs if i["instance"] == "meta_run03_standard"
                                                    and i["dir"] in ("rep16", "rep17", "rep18", "rep19", "rep20", "rep21")])
    # 明細: Stage4 runの一覧(iter8 + rep16+)
    out["E_stage4_list"] = [
        {"run": p, **{k: v for k, v in i.items() if k in (
            "instance", "stage4_reason", "n_cycles", "has_blocking_unresolved", "has_diff_target",
            "has_diff_target_incl_within_sentence", "has_current_no_target", "relations")}}
        for p, i in run_info.items()
        if is_stage4(i) and (i["dir"] == "iter8" or i["dir"] in (
            "rep16", "rep17", "rep18", "rep19", "rep20", "rep21"))
    ]
    # 傍証: 複数文(A2/A3)BLOCKINGで現行が全範囲を渡した(同じ/拡大)実績と、次周回での再発
    ev = []
    for r in exe:
        if r["cat"] in ("A2", "A3") and r["relation"] in ("same(同じ)", "current_wider(現行が拡大: 現行⊃新)"):
            run = next(x for x in runs if x["path"] == r["run"])
            cycles = run["d"]["cycles"]
            nxt = cycles[r["cycle"]] if r["cycle"] < len(cycles) else None
            same_fact_next = None
            if nxt is not None:
                same_fact_next = any(
                    s["materiality"] == "BLOCKING" and s.get("related_fact_id") == r["fact"]
                    for s in nxt["stage2_results"])
            ev.append({"run": r["run"], "cycle": r["cycle"], "cat": r["cat"], "fact": r["fact"],
                       "relation": r["relation"], "guard_ok": r.get("rr_guard_ok"),
                       "ladder": r.get("rr_ladder"), "next_cycle_exists": nxt is not None,
                       "next_cycle_same_fact_BLOCKING": same_fact_next, "final_state": r["final_state"],
                       "stage4_reason": r["stage4_reason"]})
    out["F_evidence_multi_sentence_passed_whole"] = {
        "n": len(ev), "next_cycle_none": sum(1 for e in ev if not e["next_cycle_exists"]),
        "next_cycle_same_fact_blocking": sum(1 for e in ev if e["next_cycle_same_fact_BLOCKING"]),
        "next_cycle_same_fact_not_blocking": sum(1 for e in ev if e["next_cycle_exists"]
                                                  and e["next_cycle_same_fact_BLOCKING"] is False),
        "guard_ok_false": sum(1 for e in ev if e["guard_ok"] is False),
        "final_states": dict(Counter(e["final_state"] for e in ev)),
        "detail": ev,
    }

    # meta_run03_standard ケース明細(rep16〜21とiter8)
    meta_cases = {}
    for run in runs:
        d = run["d"]
        if d["instance_id"] != "meta_run03_standard":
            continue
        cyc = []
        for ci, c in enumerate(d["cycles"]):
            crow = [r for r in by_run[run["path"]] if r["cycle"] == c["cycle"]]
            cyc.append({
                "cycle": c["cycle"], "blocking_count": c["blocking_count"],
                "recheck": c.get("recheck_overall_status"), "recheck_resolved": c.get("recheck_all_prior_issues_resolved"),
                "ja_recheck": c.get("ja_recheck_overall_status"),
                "ja_equiv": c.get("ja_en_equivalence_verdict"),
                "ja_ok_blocked_by_equiv": c.get("ja_ok_blocked_by_equivalence"),
                "ja_ok_blocked_by_guard": c.get("ja_ok_blocked_by_guard"),
                "extra_cycle_granted": c.get("extra_cycle_granted"),
                "extra_cycle_reason": c.get("extra_cycle_reason"),
                "repeat_claim_ids": c.get("repeat_claim_ids"),
                "full_recheck_required_reasons": c.get("full_recheck_required_reasons"),
                "claims": [{
                    "k": r["k"], "kind": r["kind"], "origin": r["origin"], "fact": r["fact"],
                    "materiality": r["materiality"], "claim": r["claim"],
                    "cat": r.get("cat"), "level": r.get("level"), "lang": r.get("lang"),
                    "new_ranges": r.get("new_ranges"), "undet": r.get("undet"), "cause": r.get("cause"),
                    "rr_method": r.get("rr_method"), "rr_ladder": r.get("rr_ladder"),
                    "rr_guard_ok": r.get("rr_guard_ok"), "cur_target": r.get("cur_target"),
                    "relation": r.get("relation"), "replay_agree": r.get("replay_agree"),
                    "gaps": r.get("gaps"),
                } for r in crow],
            })
        meta_cases[run["path"]] = {"final_state": d["final_state"], "stage4_reason": d["stage4_reason"],
                                   "cycles": cyc}
    out["B_meta_cases"] = meta_cases

    # 検算
    sc = {}
    for r in k1:
        if (r["run"].startswith("rep21/instances_s1/meta_run03") and r["cycle"] == 1
                and r["claim"].startswith("“It said human staff")):
            sc["i_rep21_s1_fixed_stage1_dev1"] = {"cat": r["cat"], "level": r["level"], "n_sent": r.get("n_sent"),
                                                   "stripped": r.get("stripped")}
        if (r["run"].startswith("rep20/instances_s2/meta_run03") and "They could not tell if it was AI or a person" in r["claim"]
                and r["claim"].count("“") >= 2):
            sc.setdefault("ii_rep20_s2_multi_fragment", []).append(
                {"cycle": r["cycle"], "claim": r["claim"][:140], "cat": r["cat"], "level": r["level"],
                 "gaps": r.get("gaps"), "ranges": [x[:80] for x in (r.get("new_ranges") or [])]})
        if r["claim"].lstrip().startswith("Paragraph beginning"):
            sc.setdefault("iii_paragraph_beginning", []).append(
                {"run": r["run"], "cycle": r["cycle"], "claim": r["claim"][:140], "cat": r["cat"], "a4": r.get("a4")})
    sc["iv_meta_rep19_21_K1_rows"] = len([r for r in meta if r["dir"] in ("rep19", "rep20", "rep21")])
    sc["iv_meta_rep19_21_K1_rows_determinable"] = len(
        [r for r in meta if r["dir"] in ("rep19", "rep20", "rep21") and r["cat"] != "UNDET"])
    out["selfcheck"] = sc

    # 10件無作為(固定seed)の明細
    import random
    rnd = random.Random(41)
    det = [r for r in k1 if r["cat"] != "UNDET"]
    sample = rnd.sample(det, 10)
    out["sample10"] = [{"run": r["run"], "cycle": r["cycle"], "claim": r["claim"][:200], "cat": r["cat"],
                        "level": r.get("level"), "sub": r.get("sub"), "lang": r.get("lang"),
                        "a4": r.get("a4"), "cause": r.get("cause"),
                        "new_ranges": [x[:200] for x in (r.get("new_ranges") or [])]} for r in sample]
    out["run_info"] = run_info

    return out, rows


def write_csv(rows):
    cols = ["run", "dir", "instance", "cycle", "k", "kind", "phase", "origin", "fact", "materiality", "cat",
            "level", "sub", "n_sent", "lang", "a4", "cause", "undet", "relation", "rr_method", "rr_ladder",
            "rr_guard_ok", "hint_rescue", "final_state", "stage4_reason", "claim"]
    with open(os.path.join(OUT_DIR, "claims_detail_01.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in rows:
            w.writerow([str(r.get(c, "")) if r.get(c) is not None else "" for c in cols])


def main():
    runs, dirs = load_runs()
    out, rows = analyze(None, runs, dirs)
    bm = build_borrow_map(runs)
    out_s, rows_s = analyze(bm, runs, dirs)
    out["supplement_borrowed_cycle1_text"] = {
        "note": "補助集計(定義外): cycle1の記事本文が未記録のrunについて、同一fixtureのcycle1本文(記録あり・全run一致で1種類)を借用して再集計",
        "borrow_instances_en": sorted(bm["en"]), "borrow_instances_ja": sorted(bm["ja"]),
        "A": {k: out_s["A"][k] for k in ("K1_all_rows", "K1_all_unique", "K1_blocking_rows", "K1_blocking_unique",
                                         "K1_blocking_by_phase_rows", "meta_blocking_rows",
                                         "by_instance_blocking_rows", "by_instance_blocking_unique")},
        "compare_current": out_s["compare_current"], "D": out_s["D"],
        "E_stage4_list": out_s["E_stage4_list"],
        "F_evidence": {k: v for k, v in out_s["F_evidence_multi_sentence_passed_whole"].items() if k != "detail"},
        "B_meta_cases": out_s["B_meta_cases"],
    }
    with open(os.path.join(OUT_DIR, "results_01.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, default=str)
    write_csv(rows)
    print("done", len(rows), "rows;", len(runs), "files; supplement rows", len(rows_s))


if __name__ == "__main__":
    main()
