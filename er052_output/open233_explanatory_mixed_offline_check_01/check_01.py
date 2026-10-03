# -*- coding: utf-8 -*-
"""OPEN-233-SELF-RECOVERY-TRIAL-01 委任_56 作業3: Checker引用への説明文混入の対策案P・Qの¥0オフライン検証。

LLM/API/TTS/Web Searchは一切使わない。runnerはimportしない(標準ライブラリのみ)。既存の実行記録
(er052_output/open233_self_recovery_flow_runner_01_*/instances_*/*.json)・委任_53の生の応答
(er052_output/open233_checker_spans_format_compare_01/calls/*.json)・同記事の本文の写し
(fixtures_snapshot_01.json、runnerの`build_target_instances()`から転記)を読むだけ。既存ファイルは編集しない。

照合ロジック(L0〜L5・単語境界・label_only・L4・merge)は、runnerの`vs_*`/`_resolve_claim_string`
(aggregate_01.py・replay_01.pyの元実装と同一)を、このファイル内へコピーして使う(`BASE_*`)。
VS_MATCH_EXT=ON(L5・単語境界・label_only)を主、OFFも参考。コピーの正しさは、委任_49の再生結果
(er052_output/open233_match_ext_replay_01/cases_01.csv)の「ON側の確定/確定不能」と346行全件で一致することで
自己検証する(selfcheck_vs_replay49)。

案P(Prompt・schema不変、後段のみ): 現行の照合(L0〜L5・L4)で確定不能(説明文混在/不一致)の文字列に対し、
  (1)引用符(“ ” 「 」 『 』 " ")で囲まれた断片を全部取り出す
  (2)各断片を同じ言語の本文で既存照合(L0〜L3・L5・単語境界)により「ちょうど1箇所」に確定
  (3)引用符の外の残りの各区間が、本文に逐語で存在しない(存在すれば確定不能。接続語・構造ラベルを除く)ことを確認
  (4)全断片が確定し、残りが全部「記事に無い文字列(説明文・位置ラベル・接続語)」のときだけ採用
  (5)引用符が無い文字列は、再推測せず確定不能のまま
案Q: 案P + 説明文が位置だけで指した別箇所を、同じdeviationの`same_fact_id_locations`の逐語から補う
  (逐語で本文にちょうど1箇所のもののみ。位置語[headline/title/見出し/one-line/in one line/summary/opening 等]
   が説明文に出たときだけ補う。AIでの再推測なし)。
"""
import csv
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ER = os.path.join(ROOT, "er052_output")
TARGET_NAMES = re.compile(r"(iter[5-8]|rep(7|8|9|1\d|2[01]))$")  # aggregate_01.py・replay_01.pyと同一

# ====================================================================== 既存照合のコピー(BASE_*)
QUOTE_PAIRS = [("“", "”"), ('"', '"'), ("‘", "’"), ("「", "」"), ("『", "』")]
CURLY_MAP = {"’": "'", "‘": "'", "‚": "'", "‛": "'", "“": '"', "”": '"', "„": '"'}
FRAG_RE = re.compile(r"“([^”]+)”|「([^」]+)」|『([^』]+)』")
CONNECT_RE = re.compile(r"\b(and|or)\b|[&,;、，；と/／.。:：]|および|\s", re.I)
STRUCTURAL_LABELS = frozenset({"in one line"})
EDGE_PUNCT = ".,;:!?"


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


def wordch(text, i):
    if i < 0 or i >= len(text):
        return False
    ch = text[i]
    if ch.isalnum() or ch == "_":
        return True
    if ch in ("'", "’") and 0 < i < len(text) - 1 and text[i - 1].isalnum() and text[i + 1].isalnum():
        return True
    return False


def word_boundary_ok(text, span):
    a, b = span
    if a >= b:
        return False
    if wordch(text, a) and wordch(text, a - 1):
        return False
    if wordch(text, b - 1) and wordch(text, b):
        return False
    return True


def match_levels(cand, text, lang, ext):
    e = ext and lang == "EN"
    raw = cand.strip()
    stripped = strip_one_pair(raw)
    for label, v, st in (("L0", raw, False), ("L1", stripped, True)):
        if v:
            occ = find_all(text, v)
            if len(occ) == 1:
                if not e or word_boundary_ok(text, occ[0]):
                    return "ok", label, st, occ
            elif len(occ) >= 2:
                return "multi", label, st, occ
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
                s, e2 = occ[0]
                sp = (nm[s][0], nm[e2 - 1][1])
                if not e or word_boundary_ok(text, sp):
                    return "ok", label, st, [sp]
            elif len(occ) >= 2:
                return "multi", label, st, [(nm[a][0], nm[b - 1][1]) for a, b in occ]
    return "none", None, False, []


def edge_punct_match(claim, text, lang, ext):
    if not ext or lang != "EN":
        return None
    raw = claim.strip()
    for v, st in ((raw, False), (strip_one_pair(raw), True)):
        if not v:
            continue
        core = v.strip()
        core2 = core.lstrip(EDGE_PUNCT + " ")
        core3 = core2.rstrip(EDGE_PUNCT + " ")
        if not core3 or core3 == core:
            continue
        lead = core[:len(core) - len(core2)]
        trail = core2[len(core3):]
        stt, _lv, _s, spans = match_levels(core3, text, lang, ext)
        if stt == "ok":
            return {"status": "ok", "spans": spans, "stripped": st, "edge_removed": (lead, trail)}
        if stt == "multi":
            return {"status": "multi", "spans": spans, "stripped": st, "edge_removed": (lead, trail)}
    return None


def split_fragments(claim):
    frags = [next(g for g in m.groups() if g is not None) for m in FRAG_RE.finditer(claim)]
    rest = FRAG_RE.sub("", claim)
    return frags, rest, CONNECT_RE.sub("", rest)


def resolve_in_text_core(claim, text, lang, ext):
    st, lv, strp, spans = match_levels(claim, text, lang, ext)
    if st == "ok":
        return {"status": "ok", "level": lv, "spans": spans, "stripped": strp}
    if st == "multi":
        return {"status": "multi", "level": lv, "spans": spans, "stripped": strp}
    frags, _rest, rest_clean = split_fragments(claim)
    if len(frags) >= 2 and rest_clean == "":
        sp, lvs, bad = [], [], None
        for f in frags:
            s2, l2, _st2, spans2 = match_levels(f, text, lang, ext)
            if s2 != "ok":
                bad = (f, s2)
                break
            sp.append(spans2[0])
            lvs.append(l2)
        if bad:
            return {"status": "frag_unresolved", "level": "L4", "spans": [], "bad_fragment": bad[0], "bad_status": bad[1]}
        return {"status": "ok", "level": "L4", "spans": sp, "frag_levels": lvs, "stripped": False}
    if len(frags) >= 1 and rest_clean != "":
        return {"status": "explanatory", "level": None, "spans": []}
    return {"status": "none", "level": None, "spans": []}


def resolve_in_text(claim, text, lang, ext):
    res = resolve_in_text_core(claim, text, lang, ext)
    if res["status"] in ("none", "explanatory", "frag_unresolved"):
        e = edge_punct_match(claim, text, lang, ext)
        if e is not None:
            return {"status": e["status"], "level": "L5_edge_punct", "spans": e["spans"], "stripped": e["stripped"],
                    "edge_removed": e["edge_removed"]}
    return res


def merge_spans(spans, text):
    merged = []
    for a, b in sorted(set(spans)):
        if merged:
            pa, pb = merged[-1]
            gap = text[pb:a] if a > pb else ""
            if a <= pb or (gap.strip() == "" and "\n\n" not in gap):
                merged[-1] = (pa, max(pb, b))
                continue
        merged.append((a, b))
    return merged


def is_structural_label_range(text, span):
    a, b = span
    seg = text[a:b]
    if "\n" in seg.strip():
        return False
    ls = text.rfind("\n", 0, a) + 1
    le = text.find("\n", b)
    le = len(text) if le < 0 else le
    line_core = text[ls:le].strip().lstrip("#").strip().lower()
    seg_core = seg.strip().lstrip("#").strip().lower()
    return bool(seg_core) and line_core == seg_core and seg_core in STRUCTURAL_LABELS


def base_resolve(claim, en, ja, ext=True):
    """runnerの`_resolve_claim_string`(委任_42+委任_49)のコピー。返値dict(status/reason/lang/level/spans/ranges)。"""
    claim = (claim or "").strip()
    out = {"status": "unverified", "reason": None, "lang": None, "level": None, "spans": [], "ranges": []}
    if not claim:
        out["reason"] = "empty_claim"
        return out
    results = {}
    if en is not None:
        results["EN"] = resolve_in_text(claim, en, "EN", ext)
    if ja is not None:
        results["JA"] = resolve_in_text(claim, ja, "JA", ext)
    if not results:
        out["reason"] = "no_text"
        return out
    ok_langs = [k for k, v in results.items() if v["status"] == "ok"]
    if ok_langs:
        lang = "EN" if "EN" in ok_langs else "JA"
        r = results[lang]
        text = en if lang == "EN" else ja
        merged = merge_spans(r["spans"], text)
        out.update({"status": "resolved", "lang": lang, "level": r["level"], "spans": merged,
                    "ranges": [text[a:b] for a, b in merged]})
        if ext and lang == "EN":
            lab = [text[a:b] for a, b in merged if is_structural_label_range(text, (a, b))]
            if lab:
                out.update({"status": "unverified", "reason": "label_only", "lang": None, "level": None,
                            "ranges": [], "spans": []})
        return out
    sts = [v["status"] for v in results.values()]
    if "multi" in sts:
        out["reason"] = "multi_match"
    elif "explanatory" in sts:
        out["reason"] = "explanatory_mixed"
    elif "frag_unresolved" in sts:
        out["reason"] = "mismatch"
    else:
        out["reason"] = "mismatch"
    return out


# ====================================================================== 案P・案Qの新ロジック
# 引用符の対。単一引用符(‘ ’ ' ')はアポストロフィと区別できないため対象外。直線の " は交互に開閉とみなす。
OPEN_CLOSE = {"“": "”", "「": "」", "『": "』"}
CONNECTIVE_WORDS = frozenset({"and", "or", "also", "&", "および", "と", "かつ", "また"})
POSITION_WORDS_RE = re.compile(
    r"\b(headline|title|heading|in one line|one-line|one line|summary|opening|lead|hook|paragraph|section|subheading)\b"
    r"|見出し|タイトル|冒頭|要約|段落", re.I)
SEG_EDGE = " \t\r\n.,;:、，；。:()（）[]【】—–-/…\"'“”‘’「」『』"


def extract_quoted_fragments(claim):
    """引用符で囲まれた断片を、出現順に取り出す。返値 (frags[(start,end,inner)], balanced, remainder_segments[str])。
    “”「」『』は入れ子なしの単純対応。直線"は交互。閉じ忘れ・閉じだけが残る場合は balanced=False。"""
    frags, i, n = [], 0, len(claim)
    balanced = True
    segs, last = [], 0
    while i < n:
        ch = claim[i]
        if ch in OPEN_CLOSE:
            close = OPEN_CLOSE[ch]
            j = claim.find(close, i + 1)
            if j < 0:
                balanced = False
                break
            frags.append((i, j + 1, claim[i + 1:j]))
            segs.append(claim[last:i])
            last = j + 1
            i = j + 1
            continue
        if ch == '"':
            j = claim.find('"', i + 1)
            if j < 0:
                balanced = False
                break
            frags.append((i, j + 1, claim[i + 1:j]))
            segs.append(claim[last:i])
            last = j + 1
            i = j + 1
            continue
        if ch in "”」』":
            balanced = False
            break
        i += 1
    segs.append(claim[last:])
    return frags, balanced, segs


MIN_WORDS_VERBATIM = 3  # 残りの区間が「記事の文字列」とみなされる最小語数(日本語は8文字以上)。感度は results の sensitivity 参照


def _long_enough(s):
    if re.search(r"[぀-ヿ一-鿿]", s):
        return len(s) >= 8
    return len(s.split()) >= MIN_WORDS_VERBATIM


def segment_clean(seg, text, min_words=None):
    """残りの区間が「記事の文字列ではない」と言えるか。返値 (ok, kind, stripped)。
    kind: empty/connective/label/not_in_article/short_in_article/verbatim_in_article。
    本文に逐語で存在し、かつ十分長い(3語以上)区間は「記事の文かもしれない」ので確定不能にする。
    1〜2語が偶然本文に出る(headline等)だけなら説明語として捨てる(`short_in_article`)。"""
    s = seg.strip(SEG_EDGE).strip()
    if not s:
        return True, "empty", s
    if s.lower() in CONNECTIVE_WORDS:
        return True, "connective", s
    nt, _ = norm_with_map(text, True)
    ns = norm_str(s, True)
    if ns and ns in nt:
        if s.lower().lstrip("#").strip() in STRUCTURAL_LABELS:
            return True, "label", s
        long_ok = _long_enough(s) if min_words is None else (len(s.split()) >= min_words or (re.search(r"[぀-ヿ一-鿿]", s) and len(s) >= 8))
        if long_ok:
            return False, "verbatim_in_article", s
        return True, "short_in_article", s
    return True, "not_in_article", s


def p_resolve(claim, en, ja, ext=True):
    """案P。現行照合の結果は呼び出し側が先に決める(ここは引用符の断片処理だけ)。返値dict:
    status(resolved/unverified)、reason、lang、spans、ranges、fragments(各断片の状況)、segments(残り)。"""
    claim = (claim or "").strip()
    out = {"status": "unverified", "reason": None, "lang": None, "spans": [], "ranges": [], "fragments": [],
           "segments": []}
    frags, balanced, segs = extract_quoted_fragments(claim)
    if not frags:
        out["reason"] = "p_no_quote"
        return out
    if not balanced:
        out["reason"] = "p_unbalanced_quote"
        return out
    out["fragments"] = [f[2] for f in frags]
    per_lang = {}
    texts = {"EN": en, "JA": ja}
    for lang in ("EN", "JA"):
        text = texts[lang]
        if text is None:
            continue
        res, bad = [], None
        for (_s, _e, inner) in frags:
            r = resolve_in_text(inner, text, lang, ext)
            if r["status"] != "ok":
                bad = (inner, r["status"])
                break
            res.append(r)
        if bad:
            per_lang[lang] = {"ok": False, "bad": bad}
            continue
        spans = [sp for r in res for sp in r["spans"]]
        per_lang[lang] = {"ok": True, "spans": spans, "levels": [r["level"] for r in res]}
    ok_langs = [l for l, v in per_lang.items() if v["ok"]]
    if not ok_langs:
        bads = [v["bad"] for v in per_lang.values() if not v["ok"]]
        multi = any(b[1] == "multi" for b in bads)
        out["reason"] = "p_fragment_multi_match" if multi else "p_fragment_not_in_article"
        out["detail"] = [list(b) for b in bads]
        return out
    lang = "EN" if "EN" in ok_langs else "JA"
    text = texts[lang]
    seg_info = []
    for sg in segs:
        ok, kind, s = segment_clean(sg, text)
        seg_info.append({"seg": sg.strip(), "ok": ok, "kind": kind})
    out["segments"] = seg_info
    badseg = next((x for x in seg_info if not x["ok"]), None)
    if badseg is not None:
        out["reason"] = "p_remainder_verbatim_in_article"
        out["detail"] = badseg["seg"]
        return out
    merged = merge_spans(per_lang[lang]["spans"], text)
    if ext and lang == "EN":
        lab = [text[a:b] for a, b in merged if is_structural_label_range(text, (a, b))]
        if lab:
            out["reason"] = "label_only"
            return out
    out.update({"status": "resolved", "lang": lang, "spans": merged, "ranges": [text[a:b] for a, b in merged],
                "levels": per_lang[lang]["levels"]})
    return out


HEAD_WORDS_RE = re.compile(r"\b(headline|title|heading)\b|見出し|タイトル", re.I)
ONELINE_WORDS_RE = re.compile(r"in one line|one-line|one line|\bsummary\b|要約", re.I)


def structure_elements(text):
    """記事の構造から決定論的に取れる要素: 見出し行(最初の`# `行)と`## In one line`直下の1行(段落)。"""
    out = {}
    m = re.search(r"(?m)^#\s+(.+?)\s*$", text)
    if m:
        out["headline"] = (m.start(1), m.end(1))
    m = re.search(r"(?mi)^##[ \t]*In one line[ \t]*\n(.+?)(?:\n[ \t]*\n|\Z)", text, re.S)
    if m:
        out["one_line"] = (m.start(1), m.start(1) + len(m.group(1).rstrip()))
    return out


def q_supplement(claim, p_res, same_fact_locs, en, ja, require_same_fact=True):
    """案Q: 説明文(残りの区間)に「見出し」「In one line」を指す語が出たときだけ、その構造要素
    (見出し行・In one line直下)を範囲へ補う。require_same_fact=Trueなら、さらにそのdeviationの
    `same_fact_id_locations`に、その要素の逐語(先頭の#を除く)が入っている場合に限る(案Q=Checker自身の別欄で裏付けた
    ときだけ。案Q'=Falseは構造だけで補う、より広い)。位置語がopening/paragraph等で構造から1つに決まらない場合は
    補わない(note=unmappable_position_word)。返値 (spans, added[逐語], note)。"""
    if p_res["status"] != "resolved":
        return [], [], "p_not_resolved"
    expl = " ".join(x["seg"] for x in p_res["segments"] if x["kind"] in ("not_in_article", "short_in_article"))
    if not expl or not POSITION_WORDS_RE.search(expl):
        return [], [], "no_position_word"
    lang = p_res["lang"]
    if lang != "EN":
        return [], [], "non_en"
    text = en
    el = structure_elements(text)
    want = []
    if HEAD_WORDS_RE.search(expl):
        want.append("headline")
    if ONELINE_WORDS_RE.search(expl):
        want.append("one_line")
    added, add_spans, notes = [], [], []
    for w in want:
        if w not in el:
            notes.append(w + ":no_such_element")
            continue
        a, b = el[w]
        if any(sa < b and a < sb for sa, sb in p_res["spans"]):
            notes.append(w + ":already_covered_by_fragment")
            continue  # Checkerが既にその要素の中を引用している(断片と重なる)ので補わない
        verb = text[a:b]
        if require_same_fact and verb.strip() not in [(x or "").strip().lstrip("#").strip() for x in (same_fact_locs or [])]:
            notes.append(w + ":not_in_same_fact_id_locations")
            continue
        add_spans.append((a, b))
        added.append(verb)
    others = [m.group(0) for m in re.finditer(r"\b(opening|lead|hook|paragraph \d+|section)\b|冒頭|段落", expl, re.I)]
    if others:
        notes.append("unmappable_position_word:" + ",".join(others))
    return add_spans, added, ("supplemented" if added else "no_supplement") + ("|" + ";".join(notes) if notes else "")


def resolve_additive(claim, en, ja, ext=True):
    """案P(追加方式): 現行照合で確定すればそのまま(現行と同じ)。確定不能(説明文混在・不一致)のときだけPを試す。
    multi_match・label_only・empty_claim・no_textは現行のまま(Pを試さない)。"""
    b = base_resolve(claim, en, ja, ext)
    if b["status"] == "resolved" or b["reason"] not in ("explanatory_mixed", "mismatch"):
        return b, None
    p = p_resolve(claim, en, ja, ext)
    if p["status"] == "resolved":
        merged = {"status": "resolved", "reason": None, "lang": p["lang"], "level": "P:" + ",".join(map(str, p["levels"])),
                  "spans": p["spans"], "ranges": p["ranges"]}
        return merged, p
    return b, p


OPENING_WORDS_RE = re.compile(r"\b(opening|lead|hook)\b|冒頭", re.I)


def opening_element(text):
    """見出し行の次の最初の段落(空行まで)。"""
    m = re.search(r"(?m)^#[ \t]+.+?$", text)
    if not m:
        return None
    mm = re.search(r"\S.*?(?:\n[ \t]*\n|\Z)", text[m.end():], re.S)
    if not mm:
        return None
    a = m.end() + mm.start()
    b = m.end() + mm.end()
    return (a, b)


def dangling_elements(p_res, en):
    """案P-strict用: 残りの説明文が名指しした構造要素(headline/one_line/opening)のうち、どの断片とも重ならないもの。
    説明文は範囲を広げるためではなく、「断片だけでは足りない可能性」を検出して確定不能にするためだけに読む。"""
    if p_res["status"] != "resolved" or p_res["lang"] != "EN":
        return []
    expl = " ".join(x["seg"] for x in p_res["segments"] if x["kind"] in ("not_in_article", "short_in_article"))
    if not expl:
        return []
    el = structure_elements(en)
    op = opening_element(en)
    if op:
        el["opening"] = op
    want = []
    if HEAD_WORDS_RE.search(expl):
        want.append("headline")
    if ONELINE_WORDS_RE.search(expl):
        want.append("one_line")
    if OPENING_WORDS_RE.search(expl):
        want.append("opening")
    out = []
    for w in want:
        if w not in el:
            continue
        a, b = el[w]
        if not any(sa < b and a < sb for sa, sb in p_res["spans"]):
            out.append(w)
    return out


MODES = ("P_lenient", "P_strict", "P_strict_Q", "P_strict_Qp")


def resolve_mode(claim, en, ja, same_fact, mode, ext=True):
    """追加方式(現行で確定するものは現行のまま)の、案Pの4つの運用方式。返値 (res, note)。
    P_lenient: 断片だけを採用(説明文が別箇所を名指ししていても無視)。
    P_strict: 説明文が名指しした見出し/In one line/冒頭のうち断片と重ならないものがあれば確定不能(fail-closed)。
    P_strict_Q: 上のうち、同じdeviationのsame_fact_id_locationsが逐語で裏付ける見出し/In one lineだけを補い、残りが無ければ採用。
    P_strict_Qp: 上のうち、構造(見出し行・In one line直下)で補えるものも補う(裏付け不要)。"""
    b, p = resolve_additive(claim, en, ja, ext)
    if p is None or b["status"] != "resolved" or not str(b.get("level", "")).startswith("P:"):
        return b, (p or {}).get("reason")
    if mode == "P_lenient":
        return b, "adopted"
    dang = dangling_elements(p, en)
    if not dang:
        return b, "adopted(no_dangling)"
    if mode == "P_strict":
        return {"status": "unverified", "reason": "p_dangling_position:" + ",".join(dang), "lang": None, "level": None,
                "spans": [], "ranges": []}, "dangling:" + ",".join(dang)
    sp, added, note = q_supplement(claim, p, same_fact, en, ja, require_same_fact=(mode == "P_strict_Q"))
    el = structure_elements(en)
    op = opening_element(en)
    if op:
        el["opening"] = op
    covered_spans = list(p["spans"]) + sp
    still = [w for w in dang if not any(sa < el[w][1] and el[w][0] < sb for sa, sb in covered_spans)]
    if still:
        return {"status": "unverified", "reason": "p_dangling_position:" + ",".join(still), "lang": None, "level": None,
                "spans": [], "ranges": []}, "dangling_after_q:" + ",".join(still)
    merged = merge_spans(covered_spans, en)
    return {"status": "resolved", "reason": None, "lang": "EN", "level": "P+Q", "spans": merged,
            "ranges": [en[a:b] for a, b in merged]}, "adopted_with_supplement:" + "|".join(a[:30] for a in added)



def resolve_p_first(claim, en, ja, ext=True):
    """ストレステスト用(推奨しない順序): 引用符を含む文字列はまずPで試し、不能なら現行照合へ。"""
    if extract_quoted_fragments((claim or "").strip())[0]:
        p = p_resolve(claim, en, ja, ext)
        if p["status"] == "resolved":
            return {"status": "resolved", "reason": None, "lang": p["lang"], "level": "P-first",
                    "spans": p["spans"], "ranges": p["ranges"]}, p
    return base_resolve(claim, en, ja, ext), None


# ====================================================================== 記録の読み込み
def load_runs():
    runs = []
    for dd in sorted(glob.glob(os.path.join(ER, "open233_self_recovery_flow_runner_01_*"))):
        name = os.path.basename(dd).split("_01_", 1)[1]
        if not TARGET_NAMES.match(name):
            continue
        for f in sorted(glob.glob(os.path.join(dd, "instances_*", "*.json"))):
            with open(f, encoding="utf-8") as fh:
                d = json.load(fh)
            if "cycles" not in d:
                continue
            rel = os.path.relpath(f, ER).replace("\\", "/").replace("open233_self_recovery_flow_runner_01_", "")
            runs.append({"path": rel, "dir": name, "d": d})
    return runs


def cycle_texts(cycles, i):
    c = cycles[i]
    en, ja = c.get("en_text_before_rewrite"), c.get("ja_text_before_rewrite")
    if i > 0:
        p = cycles[i - 1]
        if en is None and p.get("en_text_after_rewrite") is not None:
            en = p["en_text_after_rewrite"]
        if ja is None and p.get("ja_text_after_rewrite") is not None:
            ja = p["ja_text_after_rewrite"]
    return en, ja


def build_borrow_map(runs):
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


def collect_rows(runs):
    """BLOCKING行(委任_41・49と同じ346行)と、非BLOCKINGのK1行(参考)を返す。"""
    borrow = build_borrow_map(runs)
    blocking, nonblocking = [], []
    for run in runs:
        d = run["d"]
        cycles = d["cycles"]
        iid = d["instance_id"]
        for ci, c in enumerate(cycles):
            en, ja = cycle_texts(cycles, ci)
            if ci == 0:
                if en is None and iid in borrow["en"]:
                    en = borrow["en"][iid]
                if ja is None and iid in borrow["ja"]:
                    ja = borrow["ja"][iid]
            for k, s in enumerate(c["stage2_results"]):
                dev = s["dev"]
                if s.get("detected_by") == "precheck":
                    kind = "K3"
                elif dev.get("enumeration_source_claim"):
                    kind = "K2"
                else:
                    kind = "K1"
                claim = s.get("claim_text") or dev.get("claim_in_article", "")
                row = {"run": run["path"], "dir": run["dir"], "instance": iid, "cycle": c["cycle"], "k": k, "kind": kind,
                       "fact": s.get("related_fact_id"), "materiality": s["materiality"], "claim": claim, "en": en,
                       "ja": ja, "issue": dev.get("issue", ""), "explanation": dev.get("explanation", ""),
                       "same_fact": dev.get("same_fact_id_locations"), "enum_src": dev.get("enumeration_source_claim")}
                (blocking if s["materiality"] == "BLOCKING" else nonblocking).append(row)
    return blocking, nonblocking


def rng(r):
    return r["ranges"]


def trans(b, a):
    if b["status"] == "resolved" and a["status"] != "resolved":
        return "確定→確定不能"
    if b["status"] != "resolved" and a["status"] == "resolved":
        return "確定不能→確定"
    if b["status"] == "resolved" and a["status"] == "resolved":
        if b["spans"] != a["spans"] or b["lang"] != a["lang"]:
            return "確定→確定(範囲が変わった)"
        return "確定→確定(同じ範囲)"
    if b["reason"] != a["reason"]:
        return "確定不能→確定不能(理由が変わった)"
    return "確定不能→確定不能(同じ)"


def short(s, n=140):
    s = (s or "").replace("\n", " ⏎ ")
    return s if len(s) <= n else s[:n] + "…"



# 目視判定(私): 各件のissueが指す箇所と、案P/Q/Q'の確定範囲の一致。委任_45 §2-1・§3の記事側の記述に基づく。
INTENT = {
    "U01": "P=一致(issueが指す冒頭段落と、次段落の『produced exactly this kind of surprise.』の2箇所。第2断片はChecker自身が文の後半だけを引用)",
    "U02": "P=一致(本文の文と冒頭の文の2箇所。『および冒頭の』は位置語で捨てられる)。Q/Q'は不要",
    "U06": "P=概ね一致だが不確実(断片は冒頭の1文。説明文『The opening also presents…』は冒頭段落全体を指す可能性があり、1文より広い意図かは決定論では判別不能)",
    "U08": "P=一致(見出しの前半と冒頭の2文の2箇所。位置ラベルは捨てられる)",
    "U09": "P=一致(本文の文と見出しの2箇所。両方とも末尾句読点はL5で吸収、範囲は句読点を除く)",
    "U10": "P=一致(見出し1箇所。『Headline:』は捨てられる)",
    "U11": "P単独=一部のみ(本文の1箇所。issueが指すのは本文+見出し+in one lineの3箇所)。Q=一致(同じdeviationのsame_fact_id_locationsが裏付ける見出しとin one lineを補い3箇所)。Q'も同じ",
    "U12": "P単独=一部のみ(本文とin one lineの2箇所。(also reflected in the headline)の見出しが欠ける)。Q=補えない(rep9のRecheck出力にsame_fact_id_locationsが無い)。Q'=構造から見出しを補い一致",
    "U13": "P=一致(見出しの末尾とin one lineの2箇所。括弧の位置ラベルは捨てられる。『headline』は記事に偶然出る1語だが2語以下は説明語として扱う)。Q/Q'は不要",
}


def synthetic_tests():
    """合成記事での安全性テスト(fail-closedの確認)。返値: [{name, claim, status, reason, ranges, expect}]"""
    NL = chr(10)
    en = NL.join(["# Headline Here About Oil", "", "The first sentence is here. The second sentence repeats. The second sentence repeats.", "",
                  "Another paragraph has a unique line. It also says 'oil stayed high' once.", "", "## In one line", "Oil stayed high today."])
    cases = [
        ("1 引用が記事に1箇所+説明語", 'The headline says “Headline Here About Oil”.', "resolved"),
        ("2 引用が記事に2箇所(複数一致)", 'See “The second sentence repeats.” for the problem.', "unverified"),
        ("3 引用は1箇所、外側に記事の3語以上の文(逐語)", 'The first sentence is here. “Another paragraph has a unique line.”', "unverified"),
        ("4 閉じ忘れの引用符", 'Problem is “Another paragraph has a unique line.', "unverified"),
        ("5 引用符なしの言い換え", 'Another paragraph has one special line.', "unverified"),
        ("6 引用が記事に無い(言い換え)", 'Reason: “Another paragraph has one special line.”', "unverified"),
        ("7 引用が構造ラベルだけ", 'See “In one line”: also unsupported.', "unverified"),
        ("8 2断片+説明文", 'First “Another paragraph has a unique line.” then also “Oil stayed high today.” per summary', "resolved"),
        ("9 入れ子の引用(外側“…”の中に“…”)", '“He said “Another paragraph has a unique line.” loudly”', "unverified"),
        ("10 引用符内が記事の文の一部(部分語句)", 'Problem: “unique line”', "resolved"),
    ]
    out = []
    for name, claim, expect in cases:
        b, p = resolve_additive(claim, en, None, True)
        out.append({"name": name, "claim": claim, "status": b["status"], "reason": b.get("reason") or (p or {}).get("reason"),
                    "ranges": b["ranges"], "expect": expect, "ok": b["status"] == expect})
    return out

# ====================================================================== main
def main():
    runs = load_runs()
    blocking, nonblocking = collect_rows(runs)
    uid_map = {}
    p35 = os.path.join(ER, "open233_handoff_log_aggregation_01", "unverified35_classification_01.csv")
    with open(p35, encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            uid_map.setdefault(r["claim"].strip(), r["unique_id"])
    result = {}
    result["synthetic_tests"] = synthetic_tests()

    # ---------- 自己検証: 委任_49の再生(ON側)と346行で一致するか
    p49 = os.path.join(ER, "open233_match_ext_replay_01", "cases_01.csv")
    with open(p49, encoding="utf-8-sig") as fh:
        r49 = list(csv.DictReader(fh))
    self_mis = []
    n_cmp = 0
    # 委任_49のcases_01.csvは「本文記録なし」を含む346行・同じ順序。BLOCKING行を同じ順序で並べる必要があるため、
    # collect_rowsの順(runs順×cycle×k)がreplay_01と同一であることを前提に比較し、不一致があれば報告する。
    for i, (a, b) in enumerate(zip(blocking, r49)):
        if a["en"] is None and a["ja"] is None:
            continue
        n_cmp += 1
        res = base_resolve(a["claim"], a["en"], a["ja"], True)
        want = b["on_status"]
        if (res["status"] == "resolved") != (want == "resolved") or (res["status"] == "resolved" and res["level"] != b["on_level"]):
            self_mis.append({"i": i, "claim": short(a["claim"], 80), "mine": [res["status"], res["level"]], "r49": [want, b["on_level"]]})
    result["selfcheck_vs_replay49"] = {"n_blocking_rows": len(blocking), "n_r49_rows": len(r49), "n_compared": n_cmp,
                                        "n_mismatch": len(self_mis), "mismatch_examples": self_mis[:10]}

    # ---------- (b) BLOCKING 346行
    rows_b = []
    for a in blocking:
        if a["en"] is None and a["ja"] is None:
            rows_b.append({**a, "tr_add": "本文記録なし", "tr_first": "本文記録なし"})
            continue
        base = base_resolve(a["claim"], a["en"], a["ja"], True)
        add, p_add = resolve_additive(a["claim"], a["en"], a["ja"], True)
        first, p_first = resolve_p_first(a["claim"], a["en"], a["ja"], True)
        base_off = base_resolve(a["claim"], a["en"], a["ja"], False)
        rows_b.append({**a, "base": base, "add": add, "p_add": p_add, "first": first, "p_first": p_first,
                       "base_off": base_off, "tr_add": trans(base, add), "tr_first": trans(base, first)})
    cnt_add = Counter(r["tr_add"] for r in rows_b)
    cnt_first = Counter(r["tr_first"] for r in rows_b)
    cnt_base = Counter(("resolved" if r["base"]["status"] == "resolved" else "unverified:" + str(r["base"]["reason"]))
                       for r in rows_b if "base" in r)
    worsen_first = [r for r in rows_b if r["tr_first"] in ("確定→確定不能", "確定→確定(範囲が変わった)")]
    worsen_add = [r for r in rows_b if r["tr_add"] in ("確定→確定不能", "確定→確定(範囲が変わった)")]
    newly = [r for r in rows_b if r["tr_add"] == "確定不能→確定"]
    result["b_blocking346"] = {
        "n_rows": len(rows_b), "base_on_status": dict(cnt_base),
        "P_additive_transitions": dict(cnt_add), "P_first_transitions(推奨しない順序のストレステスト)": dict(cnt_first),
        "P_additive_worsen_rows_ALL": [{"run": r["run"], "claim": r["claim"], "base": [r["base"]["status"], r["base"]["ranges"]],
                                        "add": [r["add"]["status"], r["add"]["ranges"]]} for r in worsen_add],
        "P_first_worsen_rows_ALL": [{"run": r["run"], "cycle": r["cycle"], "kind": r["kind"], "claim": r["claim"],
                                     "base": [r["base"]["status"], r["base"]["level"], r["base"]["ranges"]],
                                     "first": [r["first"]["status"], r["first"]["level"], r["first"]["ranges"]]} for r in worsen_first],
        "P_additive_newly_resolved_ALL": [{"uid": uid_map.get(r["claim"].strip()), "run": r["run"], "cycle": r["cycle"], "k": r["k"],
                                           "kind": r["kind"], "fact": r["fact"], "claim": r["claim"],
                                           "base_reason": r["base"]["reason"], "level": r["add"]["level"],
                                           "ranges": r["add"]["ranges"]} for r in newly],
        "P_additive_still_unverified": [{"uid": uid_map.get(r["claim"].strip()), "run": r["run"], "cycle": r["cycle"],
                                         "claim": r["claim"], "base_reason": r["base"]["reason"],
                                         "p_reason": (r["p_add"] or {}).get("reason")} for r in rows_b
                                        if "add" in r and r["add"]["status"] != "resolved"],
    }

    # ---------- (a) 12件(説明文混入)
    a12 = [r for r in rows_b if "base" in r and r["base"]["reason"] == "explanatory_mixed"]
    result["a_explanatory_mixed_count_in_346"] = len(a12)
    table_a = []
    seen_claims = {}
    for r in a12:
        uid = uid_map.get(r["claim"].strip(), "?")
        p = r["p_add"] or p_resolve(r["claim"], r["en"], r["ja"], True)
        qspans, qadded, qnote = q_supplement(r["claim"], p, r["same_fact"], r["en"], r["ja"], True)
        qpspans, qpadded, qpnote = q_supplement(r["claim"], p, r["same_fact"], r["en"], r["ja"], False)
        text = r["en"] if p.get("lang") != "JA" else r["ja"]
        qranges = [text[a:b] for a, b in merge_spans(p["spans"] + qspans, text)] if p["status"] == "resolved" else []
        qpranges = [text[a:b] for a, b in merge_spans(p["spans"] + qpspans, text)] if p["status"] == "resolved" else []
        sib = [x["claim"] for x in blocking + nonblocking if x["kind"] == "K2" and x["run"] == r["run"]
               and x["cycle"] == r["cycle"] and (x["enum_src"] or "").strip() == r["claim"].strip()]
        table_a.append({"uid": uid, "k2_siblings_same_cycle": sib, "intent_judgement(目視・私)": INTENT.get(uid, "?"),
                        "run": r["run"], "cycle": r["cycle"], "k": r["k"], "fact": r["fact"], "claim": r["claim"],
                        "issue": r["issue"], "same_fact": r["same_fact"],
                        "p_status": p["status"], "p_reason": p.get("reason"), "fragments": p.get("fragments"),
                        "segments": p.get("segments"), "p_ranges": p.get("ranges"),
                        "q_added": qadded, "q_note": qnote, "q_ranges": qranges,
                        "qprime_added": qpadded, "qprime_note": qpnote, "qprime_ranges": qpranges})
    result["a_table"] = table_a
    # 運用4方式の比較(13件): 採用/確定不能と範囲
    modes_a = []
    for r, t in zip(a12, table_a):
        row = {"uid": t["uid"], "run": r["run"], "cycle": r["cycle"]}
        for m in MODES:
            res, note = resolve_mode(r["claim"], r["en"], r["ja"], r["same_fact"], m, True)
            row[m] = {"status": res["status"], "reason": res.get("reason"), "ranges": res["ranges"], "note": note}
        modes_a.append(row)
    result["a_modes"] = modes_a
    mode_b = {}
    for m in MODES:
        c = Counter()
        for a in blocking:
            if a["en"] is None and a["ja"] is None:
                continue
            base = base_resolve(a["claim"], a["en"], a["ja"], True)
            res, _ = resolve_mode(a["claim"], a["en"], a["ja"], a["same_fact"], m, True)
            c[trans(base, res)] += 1
        mode_b[m] = dict(c)
    result["b_modes"] = mode_b
    mode_d = {}
    for m in MODES:
        c = Counter()
        for a in nonblocking:
            if a["kind"] != "K1" or (a["en"] is None and a["ja"] is None):
                continue
            base = base_resolve(a["claim"], a["en"], a["ja"], True)
            if base["status"] == "resolved":
                continue
            res, _ = resolve_mode(a["claim"], a["en"], a["ja"], a["same_fact"], m, True)
            c[trans(base, res)] += 1
        mode_d[m] = dict(c)
    result["d_nonblocking_modes"] = mode_d
    mode_c = {}
    for m in MODES:
        c = Counter()
        for fn in sorted(os.listdir(os.path.join(ER, "open233_checker_spans_format_compare_01", "calls"))):
            d = json.load(open(os.path.join(ER, "open233_checker_spans_format_compare_01", "calls", fn), encoding="utf-8"))
            if d["arm"] != "ctl":
                continue
            fxa = json.load(open(os.path.join(HERE, "fixtures_snapshot_01.json"), encoding="utf-8"))[d["article"]]
            for dev in d.get("final_deviations") or []:
                claim = dev.get("claim_in_article") or ""
                base = base_resolve(claim, fxa["article_text"], fxa["source_article_text"], True)
                res, _ = resolve_mode(claim, fxa["article_text"], fxa["source_article_text"], dev.get("same_fact_id_locations"), m, True)
                c[trans(base, res)] += 1
        mode_c[m] = dict(c)
    result["c_ctl_modes"] = mode_c

    # ---------- (d) 非BLOCKINGの確定不能7行(K1)
    rows_d = []
    for a in nonblocking:
        if a["kind"] != "K1" or (a["en"] is None and a["ja"] is None):
            continue
        base = base_resolve(a["claim"], a["en"], a["ja"], True)
        if base["status"] == "resolved":
            continue
        add, p = resolve_additive(a["claim"], a["en"], a["ja"], True)
        qs = q_supplement(a["claim"], p, a["same_fact"], a["en"], a["ja"]) if p and p["status"] == "resolved" else ([], [], "-")
        rows_d.append({"run": a["run"], "cycle": a["cycle"], "materiality": a["materiality"], "claim": a["claim"],
                       "base_reason": base["reason"], "p_status": (p or {}).get("status"), "p_reason": (p or {}).get("reason"),
                       "p_ranges": (p or {}).get("ranges"), "fragments": (p or {}).get("fragments"),
                       "segments": (p or {}).get("segments"), "q_added": qs[1]})
    result["d_nonblocking_unresolved_K1"] = rows_d

    # ---------- (d) K2で捨てられたsame_fact_id_locations 14件
    dropped = []
    for a in blocking + nonblocking:
        if a["kind"] == "K2" or a["en"] is None:
            continue
        for loc in a["same_fact"] or []:
            if isinstance(loc, str) and loc.strip() not in a["en"]:
                base = base_resolve(loc, a["en"], a["ja"], True)
                add, p = resolve_additive(loc, a["en"], a["ja"], True)
                dropped.append({"run": a["run"], "cycle": a["cycle"], "materiality": a["materiality"], "loc": loc,
                                "base": [base["status"], base["reason"], base["ranges"]],
                                "P": [add["status"], add["reason"], add["ranges"]],
                                "p_fragments": (p or {}).get("fragments"), "p_segments": (p or {}).get("segments")})
    result["d_dropped_same_fact_locations"] = dropped

    # ---------- (c) 委任_53の対照腕(現行形式、18 call)
    fx = json.load(open(os.path.join(HERE, "fixtures_snapshot_01.json"), encoding="utf-8"))
    cdir = os.path.join(ER, "open233_checker_spans_format_compare_01", "calls")
    rows_c = []
    for fn in sorted(os.listdir(cdir)):
        d = json.load(open(os.path.join(cdir, fn), encoding="utf-8"))
        if d["arm"] != "ctl":
            continue
        en = fx[d["article"]]["article_text"]
        ja = fx[d["article"]]["source_article_text"]
        for dev in d.get("final_deviations") or []:
            claim = dev.get("claim_in_article") or ""
            base = base_resolve(claim, en, ja, True)
            add, p = resolve_additive(claim, en, ja, True)
            first, _ = resolve_p_first(claim, en, ja, True)
            rows_c.append({"article": d["article"], "k": d["k"], "sev": dev.get("severity"),
                           "enum": bool(dev.get("detected_by_enumeration")), "claim": claim,
                           "base": base["status"], "add": add["status"], "tr_add": trans(base, add),
                           "tr_first": trans(base, first), "ranges_same_first": base["spans"] == first["spans"]})
    result["c_ctl_arm"] = {"n_deviations": len(rows_c), "base_status": dict(Counter(r["base"] for r in rows_c)),
                           "P_additive_transitions": dict(Counter(r["tr_add"] for r in rows_c)),
                           "P_first_transitions": dict(Counter(r["tr_first"] for r in rows_c)),
                           "n_calls": 18, "n_with_quote_chars": sum(1 for r in rows_c if extract_quoted_fragments(r["claim"])[0])}

    # ---------- 型の集計(説明文混入17行[12+非BLOCKING5] の文字列構造: 引用符で囲まれているか)
    result["type_quote_enclosed"] = [{"uid": t["uid"], "n_fragments": len(t["fragments"] or []),
                                      "segments_kind": [s["kind"] for s in (t["segments"] or [])]} for t in table_a]

    # ---------- 感度: 残り区間を「記事の文字列」とみなす最小語数(1/2/3/4)
    global MIN_WORDS_VERBATIM
    sens = {}
    keep = MIN_WORDS_VERBATIM
    for mw in (1, 2, 3, 4, 6):
        MIN_WORDS_VERBATIM = mw
        newly_n, worsen_n, still_mixed = 0, 0, 0
        for a in blocking:
            if a["en"] is None and a["ja"] is None:
                continue
            base = base_resolve(a["claim"], a["en"], a["ja"], True)
            add, p = resolve_additive(a["claim"], a["en"], a["ja"], True)
            t = trans(base, add)
            newly_n += t == "確定不能→確定"
            worsen_n += t in ("確定→確定不能", "確定→確定(範囲が変わった)")
            still_mixed += (base["reason"] == "explanatory_mixed" and add["status"] != "resolved")
        sens[str(mw)] = {"newly_resolved": newly_n, "worsen": worsen_n, "explanatory_mixed_still_unverified": still_mixed}
    MIN_WORDS_VERBATIM = keep
    result["sensitivity_min_words"] = sens

    # ---------- 保存
    json.dump(result, open(os.path.join(HERE, "results_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(os.path.join(HERE, "cases_01.csv"), "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["block", "id", "run", "cycle", "kind", "fact", "base_status", "base_reason", "base_level", "tr_add(案P追加方式)",
                    "tr_first(P先行ストレス)", "p_reason", "p_ranges", "claim"])
        for r in rows_b:
            if "base" not in r:
                w.writerow(["b346", uid_map.get(r["claim"].strip(), ""), r["run"], r["cycle"], r["kind"], r["fact"],
                            "no_text", "", "", r["tr_add"], r["tr_first"], "", "", r["claim"]])
                continue
            pa = r["p_add"] or {}
            w.writerow(["b346", uid_map.get(r["claim"].strip(), ""), r["run"], r["cycle"], r["kind"], r["fact"],
                        r["base"]["status"], r["base"]["reason"], r["base"]["level"], r["tr_add"], r["tr_first"],
                        pa.get("reason"), " || ".join(r["add"]["ranges"]) if r["add"]["status"] == "resolved" else "", r["claim"]])
        for t in rows_c:
            w.writerow(["c_ctl", "", t["article"], t["k"], "enum" if t["enum"] else "primary", "", t["base"], "", "",
                        t["tr_add"], t["tr_first"], "", "", t["claim"]])
        for t in rows_d:
            w.writerow(["d_nonblocking", "", t["run"], t["cycle"], "K1", "", "unverified", t["base_reason"], "", t["p_status"], "",
                        t["p_reason"], " || ".join(t["p_ranges"] or []), t["claim"]])
        for t in dropped:
            w.writerow(["d_dropped_loc", "", t["run"], t["cycle"], "K1-loc", "", t["base"][0], t["base"][1], "", t["P"][0], "",
                        t["P"][1], " || ".join(t["P"][2] or []), t["loc"]])

    # ---------- 標準出力(要約)
    for t in result["synthetic_tests"]:
        print("  SYN", json.dumps(t, ensure_ascii=False))
    print("selfcheck:", json.dumps(result["selfcheck_vs_replay49"], ensure_ascii=False))
    print("b: base_on_status:", dict(cnt_base))
    print("b: P追加方式:", dict(cnt_add))
    print("b: P先行(ストレス):", dict(cnt_first))
    print("b: 追加方式 悪化(確定→不能/範囲変化):", len(worsen_add))
    print("b: P先行 悪化:", len(worsen_first))
    for x in result["b_blocking346"]["P_first_worsen_rows_ALL"]:
        print("   FIRST-worse:", json.dumps(x, ensure_ascii=False))
    print("b: 追加方式で確定不能→確定:", len(newly))
    for x in result["b_blocking346"]["P_additive_newly_resolved_ALL"]:
        print("   NEW:", json.dumps(x, ensure_ascii=False))
    print("b: 追加方式でも確定不能(件数):", len(result["b_blocking346"]["P_additive_still_unverified"]))
    for x in result["b_blocking346"]["P_additive_still_unverified"]:
        print("   STILL:", json.dumps(x, ensure_ascii=False))
    print("a: 12件(BLOCKING・explanatory_mixed):", len(a12))
    for t in table_a:
        print("  A", json.dumps(t, ensure_ascii=False))
    print("c:", json.dumps(result["c_ctl_arm"], ensure_ascii=False))
    print("modes b:", json.dumps(result["b_modes"], ensure_ascii=False))
    print("modes c:", json.dumps(result["c_ctl_modes"], ensure_ascii=False))
    print("modes d:", json.dumps(result["d_nonblocking_modes"], ensure_ascii=False))
    for x in result["a_modes"]:
        print("  MODE", json.dumps({k: (v if k in ("uid","run","cycle") else [v["status"], v["note"], [q[:45] for q in v["ranges"]]]) for k, v in x.items()}, ensure_ascii=False))
    print("d非BLOCKING確定不能K1:", len(rows_d))
    for t in rows_d:
        print("  D", json.dumps(t, ensure_ascii=False))
    print("d捨てられたloc:", len(dropped))
    for t in dropped:
        print("  L", json.dumps(t, ensure_ascii=False))


if __name__ == "__main__":
    main()
