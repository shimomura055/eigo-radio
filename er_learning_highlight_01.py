"""SLOT-23-CONSUMER-DESIGN-01 委任_04A: 本文ハイライト(①太字+二重下線 / ②太字+下線 / ③下線のみ)の共通解決器・描画・CSS定数。

純関数のみ(API 0・ファイル書込 0・環境変数/flagを読まない)。配線(X/Y/Z runner・page builderからの呼出)は別班(C/D/E)。
common(`er_user_listening_page_common_01`)は本moduleを import するが、本moduleは common を import しない(循環回避)。

用語
- DisplayUnit: {"key": str, "texts": [str,...], "joiner": " "} 表示テキストの単位列(公開順)。X=段落/Y=台本ブロック/Z=クリップ群。
- 解決: 候補doc(kp_candidates.json)の source_sentence_id/source_span/occurrence_sentence_ids と確定レコードのitemsから、
  表示テキスト上の文字範囲(unit_key, text_index, start, end)を決定論的に求める。特定不能はISSUE(fail-closed)、停止しない事象はNOTICE。
"""
from __future__ import annotations

import hashlib
import html as _html
import re
import unicodedata
from typing import Any, Optional

esc = _html.escape

# ============================================================
# CSS(単一定数。Y/Z共通CSS・X player CSS・X公開ページCSSが同じ定数を使う)
# font-size/color継承、背景なし、記号追加なし。
# ============================================================
HIGHLIGHT_CSS = (
    ".lk1,.lk2,.lk3{font-size:inherit;color:inherit;background:none}"
    ".lk1{font-weight:700;text-decoration-line:underline;text-decoration-style:double;"
    "-webkit-text-decoration-line:underline;-webkit-text-decoration-style:double;"
    "text-underline-offset:3px}"
    ".lk2{font-weight:700;text-decoration-line:underline;text-decoration-style:solid;"
    "-webkit-text-decoration-line:underline;-webkit-text-decoration-style:solid;"
    "text-underline-offset:2px}"
    ".lk3{font-weight:inherit;text-decoration-line:underline;text-decoration-style:solid;"
    "-webkit-text-decoration-line:underline;-webkit-text-decoration-style:solid;"
    "text-underline-offset:2px}"
    "ul.lk-meaning{margin:4px 0 8px 1.2em;padding:0;font-size:.9em}"
    "p.lk-legend{font-size:.85em;margin:4px 0}"
)

KIND_TAG = {1: "strong", 2: "strong", 3: "span"}
KIND_CLASS = {1: "lk1", 2: "lk2", 3: "lk3"}
CLASS_KIND = {v: k for k, v in KIND_CLASS.items()}

# 凡例/訳リストの文言: Z lint禁止語(英語:|日本語:|EN:|JA:)・「(A2)」を使わない
LEGEND_TEXT = ("本文の下線: ", "太字+二重下線", " = 重要表現 / ", "太字+下線", " = 追加の解説つき表現 / ", "下線のみ", " = 意味を下の一覧で確認")

# ============================================================
# 正規化(er128._norm_ws と同一規約: NFKC・曲線引用符→直線・空白畳み。大文字小文字は保持)
# ============================================================
_QUOTE_MAP = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"'})


def norm_ws(s: Optional[str]) -> str:
    return " ".join(unicodedata.normalize("NFKC", s or "").translate(_QUOTE_MAP).split())


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _sid_num(sid: Any) -> int:
    m = re.fullmatch(r"S(\d+)", str(sid or ""))
    return int(m.group(1)) if m else 10 ** 9


# ============================================================
# 文分割(候補生成と同一: er030.build_sentence_units / er029.build_sentence_units_v4 と同一実装)
# er030はwordfreq(重い外部依存)をimportするため、importできない環境では下の同一実装コピーを使う。
# 同一性の担保: 実データで候補docのsource_sentenceと全件一致すること(offline_resolve_01 / test)。
# ============================================================
_QUOTE_AWARE_SPLIT_RE = re.compile(r'[.!?]+[)\]"\']{0,2}(?=\s|$)')
_WORD_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")


def _local_build_sentence_units(article_markdown: str) -> list:
    lines = article_markdown.splitlines()
    blocks, current = [], []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            if current:
                blocks.append(" ".join(current))
                current = []
            blocks.append(stripped.lstrip("#").strip())
        else:
            current.append(stripped)
    if current:
        blocks.append(" ".join(current))
    units = []
    for block in blocks:
        joined = unicodedata.normalize("NFKC", block).translate(_QUOTE_MAP)
        for raw_sentence in _QUOTE_AWARE_SPLIT_RE.split(joined):
            raw_sentence = raw_sentence.strip()
            if not raw_sentence:
                continue
            if raw_sentence[0] in "\"'":
                raw_sentence = raw_sentence[1:].strip()
            if raw_sentence and raw_sentence[-1] in "\"'":
                raw_sentence = raw_sentence[:-1].strip()
            if not raw_sentence:
                continue
            toks = _WORD_TOKEN_RE.findall(raw_sentence)
            if not toks:
                continue
            units.append({"tokens": toks, "raw_text": raw_sentence})
    return units


def split_sentence_units(article_text: str) -> list:
    try:
        import er030_key_phrase_db_hybrid_core_01 as core
    except ImportError:
        return _local_build_sentence_units(article_text)
    return core.build_sentence_units(article_text)


# ============================================================
# 表示テキストの正規化ストリーム(文字ごとに元位置へ戻せる)
# ============================================================
def build_stream(display_units: list) -> tuple:
    """全DisplayUnit/textsを順に連結し、(norm_str, pos_map)を返す。pos_map[i]=(unit_index, text_index, char_index) または None(区切り空白)。
    正規化: 文字ごとにNFKC+引用符統一、連続空白は1個に畳む(先頭文字の位置を保持)。単位/text間は空白1個で区切る。"""
    out: list = []
    pmap: list = []

    def _sep():
        if out and out[-1] != " ":
            out.append(" ")
            pmap.append(None)

    for ui, u in enumerate(display_units):
        for ti, t in enumerate(u.get("texts") or []):
            _sep()
            for ci, ch in enumerate(t or ""):
                n = unicodedata.normalize("NFKC", ch).translate(_QUOTE_MAP)
                for nc in n:
                    if nc.isspace():
                        if out and out[-1] != " ":
                            out.append(" ")
                            pmap.append((ui, ti, ci))
                    else:
                        out.append(nc)
                        pmap.append((ui, ti, ci))
    return "".join(out), pmap


def _is_word(ch: str) -> bool:
    return ch.isalnum()


def align_sentences(units: list, stream: str) -> dict:
    """文単位(build_sentence_units結果)→ストリーム位置の単調整列。{sentence_index: (start, end)}。見つからない文は含めない(カーソルは進めない)。"""
    spans: dict = {}
    cursor = 0
    for i, u in enumerate(units):
        s = norm_ws(u["raw_text"])
        if not s:
            continue
        pos = cursor
        while True:
            pos = stream.find(s, pos)
            if pos < 0:
                break
            end = pos + len(s)
            before_ok = pos == 0 or not (_is_word(stream[pos - 1]) and _is_word(s[0]))
            after_ok = end >= len(stream) or not (_is_word(stream[end]) and _is_word(s[-1]))
            if before_ok and after_ok:
                break
            pos += 1
        if pos >= 0:
            spans[i] = (pos, pos + len(s))
            cursor = pos + len(s)
    return spans


def _pieces_of(stream_span: tuple, pmap: list) -> list:
    """ストリーム範囲→[{unit_index, text_index, start, end}](text単位の連続片)。"""
    a, b = stream_span
    pieces: list = []
    cur = None
    for k in range(a, b):
        p = pmap[k]
        if p is None:
            continue
        ui, ti, ci = p
        if cur and cur["unit_index"] == ui and cur["text_index"] == ti and ci in (cur["end"] - 1, cur["end"]):
            cur["end"] = max(cur["end"], ci + 1)
        else:
            cur = {"unit_index": ui, "text_index": ti, "start": ci, "end": ci + 1}
            pieces.append(cur)
    return pieces


# ============================================================
# 項目の収集
# ============================================================
def items_from_record(record: dict) -> list:
    """確定レコード(confirmed_selection.json)→ハイライト対象items [{candidate_id, category(=kind 1|2|3), used_form, japanese_gloss}]。
    items(slot kp/vocab)と unconsumed のうち category が1〜3のものを結合(重複candidate_idは最初を採用)。"""
    out, seen = [], set()
    for src in (record.get("items") or [], record.get("unconsumed") or []):
        for it in src:
            cat = it.get("category")
            cid = it.get("candidate_id")
            if cat in (1, 2, 3) and cid and cid not in seen:
                seen.add(cid)
                out.append({"candidate_id": cid, "category": cat, "used_form": it.get("used_form"), "japanese_gloss": it.get("japanese_gloss")})
    return out


def _issue(code: str, cid: Optional[str], detail: str, **kw) -> dict:
    d = {"code": code, "candidate_id": cid, "detail": detail}
    d.update(kw)
    return d


# ============================================================
# 解決器
# ============================================================
def resolve_highlights(article_text: str, cands_doc: dict, items: list, display_units: list, *,
                       units: Optional[list] = None, lr_rebound: bool = False) -> dict:
    """純関数。returns {"status": "OK"|"ISSUE", "highlights": [...], "meanings": [...], "notices": [...], "issues": [...], "stats": {...}}.

    highlights[i] = {candidate_id, kind(1|2|3), used_form, gloss, surface(=pieces本文の連結), pieces:[{unit_key,text_index,start,end,text}],
                     decorate(bool), sentence_id, relocated_from(None|sid), stream_span}
    meanings = ③全件 [{candidate_id, used_form, japanese_gloss, unit_key(None=節末)}] (装飾省略・表示範囲外でも訳は残す)
    lr_rebound=True: Local Rewrite後など、文が書き換わっても語句不変なら隣接文の間で語句を再束縛する(NOTICE HL_LR_REBOUND)。
    """
    import er105_kp_fulltext_selector_01 as sel   # 遅延import(既存の本文一致規約_phrase_patternを再利用)
    notices: list = []
    issues: list = []
    highlights: list = []
    meanings: list = []

    # (1) 本文sha
    want_sha = (cands_doc or {}).get("text_sha256")
    if want_sha and sha256_text(article_text) != want_sha:
        issues.append(_issue("HL_TEXT_SHA_MISMATCH", None, f"sha256(article_text)={sha256_text(article_text)[:12]}… != cands.text_sha256={str(want_sha)[:12]}…"))
        return _result(highlights, meanings, notices, issues)

    cands = {c.get("candidate_id"): c for c in ((cands_doc or {}).get("candidates") or []) if isinstance(c, dict)}
    if units is None:
        units = split_sentence_units(article_text)
    stream, pmap = build_stream(display_units)
    spans = align_sentences(units, stream)

    resolved: list = []
    for it in items:
        cid = it["candidate_id"]
        kind = int(it["category"])
        used_form = it.get("used_form")
        gloss = it.get("japanese_gloss")
        base_meaning = {"candidate_id": cid, "used_form": used_form, "japanese_gloss": gloss, "unit_key": None}
        c = cands.get(cid)
        if c is None:
            issues.append(_issue("HL_CANDIDATE_UNKNOWN", cid, "候補docに無いcandidate_id"))
            if kind == 3:
                meanings.append(base_meaning)
            continue
        ci = c.get("item") or {}
        span_txt = ci.get("source_span") or c.get("selection_phrase")
        sid = c.get("source_sentence_id") or ci.get("source_sentence_id")
        if not span_txt:
            issues.append(_issue("HL_SPAN_MISSING", cid, "source_spanが無い"))
            if kind == 3:
                meanings.append(base_meaning)
            continue
        # (2) 文の特定と逐語照合
        sidx = _sid_num(sid) - 1
        if not (0 <= sidx < len(units)):
            issues.append(_issue("HL_SENTENCE_ID_UNKNOWN", cid, f"source_sentence_id={sid} が文数{len(units)}の範囲外"))
            if kind == 3:
                meanings.append(base_meaning)
            continue
        want_sent = c.get("source_sentence") or ci.get("source_sentence")
        if want_sent is not None and norm_ws(want_sent) != norm_ws(units[sidx]["raw_text"]):
            issues.append(_issue("HL_SENTENCE_MISMATCH", cid, f"{sid}: 候補doc source_sentence != 本文の文", candidate_sentence=want_sent, article_sentence=units[sidx]["raw_text"]))
            if kind == 3:
                meanings.append(base_meaning)
            continue
        # (3)(4) 出現の順序: 特定出現を先頭、以降は occurrence_sentence_ids の番号順(範囲内最初の出現へ再配置)
        occ = list(ci.get("occurrence_sentence_ids") or c.get("occurrence_sentence_ids") or [])
        order = [sid] + [o for o in sorted(occ, key=_sid_num) if o != sid]
        pat = sel._phrase_pattern(span_txt)
        chosen = None
        any_in_display = False
        for o in order:
            oi = _sid_num(o) - 1
            if oi not in spans:
                continue
            any_in_display = True
            a, b = spans[oi]
            m = pat.search(stream, a, b)
            if m:
                chosen = (o, (m.start(), m.end()))
                break
        if chosen is None and lr_rebound:
            # (7) LR後: 特定文の前後で整列できた隣接文の間に語句が残っていれば再束縛
            lo = max([spans[j][1] for j in spans if j < sidx], default=0)
            hi = min([spans[j][0] for j in spans if j > sidx], default=len(stream))
            m = pat.search(stream, lo, hi)
            if m:
                chosen = (sid, (m.start(), m.end()))
                notices.append(_issue("HL_LR_REBOUND", cid, f"{sid}: 文が書換えられたが語句不変のため隣接文の間で再束縛"))
        if chosen is None:
            if kind == 3:
                meanings.append(base_meaning)
            if any_in_display:
                issues.append(_issue("HL_SPAN_NOT_IN_SENTENCE", cid, f"{sid}/{order}: 表示範囲内の文に語句 {span_txt!r} が無い"))
            elif kind == 3:
                notices.append(_issue("HL_NOT_IN_DISPLAY_MEANING_ONLY", cid, f"{order} は表示範囲外。訳リストのみ"))
            else:
                issues.append(_issue("HL_NOT_IN_DISPLAY", cid, f"{order} のいずれも表示範囲(Full Story本文)に無い"))
            continue
        used_sid, sspan = chosen
        relocated = None
        if used_sid != sid:
            relocated = sid
            notices.append(_issue("HL_OCCURRENCE_RELOCATED", cid, f"{sid}→{used_sid}(表示範囲外のため範囲内最初の出現へ)"))
        pcs = _pieces_of(sspan, pmap)
        if not pcs:
            issues.append(_issue("HL_UNRESOLVED", cid, "表示位置へ写像できない(区切り空白のみ)"))
            if kind == 3:
                meanings.append(base_meaning)
            continue
        pieces = []
        for p in pcs:
            u = display_units[p["unit_index"]]
            txt = (u["texts"][p["text_index"]])[p["start"]:p["end"]]
            pieces.append({"unit_key": u["key"], "text_index": p["text_index"], "start": p["start"], "end": p["end"], "text": txt})
        hl = {"candidate_id": cid, "kind": kind, "used_form": used_form, "gloss": gloss, "surface": "".join(p["text"] for p in pieces),
              "pieces": pieces, "decorate": True, "sentence_id": used_sid, "relocated_from": relocated, "stream_span": sspan}
        resolved.append(hl)
        if kind == 3:
            meanings.append({**base_meaning, "unit_key": pieces[0]["unit_key"]})

    # (6) 重なり: 優先 ①>②>③、同優先は広い方が先
    resolved_sorted = sorted(resolved, key=lambda h: (h["kind"], -(h["stream_span"][1] - h["stream_span"][0]), h["stream_span"][0]))
    accepted: list = []
    for h in resolved_sorted:
        a, b = h["stream_span"]
        verdict = None
        for y in accepted:
            ya, yb = y["stream_span"]
            if b <= ya or yb <= a:
                continue   # 交差なし(隣接含む)
            inside = ya <= a and b <= yb       # h ⊆ y
            contains = a <= ya and yb <= b     # h ⊇ y
            if inside or contains:
                verdict = ("contained", y)
                break
            if h["kind"] == 3 and y["kind"] == 3:
                verdict = ("partial3", y)
            else:
                verdict = ("partial_issue", y)
                break
        if verdict is None:
            accepted.append(h)
            highlights.append(h)
            continue
        kindv, y = verdict
        h["decorate"] = False
        highlights.append(h)
        if kindv == "contained":
            notices.append(_issue("HL_CONTAINED", h["candidate_id"], f"{y['candidate_id']}(区分{y['kind']})と完全包含のため下位の装飾を省略。訳リスト(③)は残す"))
        elif kindv == "partial3":
            notices.append(_issue("HL_PARTIAL_OVERLAP_3", h["candidate_id"], f"③同士の部分交差({y['candidate_id']}を装飾)。訳リストは両方"))
        else:
            issues.append(_issue("HL_PARTIAL_OVERLAP", h["candidate_id"], f"{y['candidate_id']}(区分{y['kind']})と部分的に交差(①②が関わる)。どちらかを別表現へ"))
    order_idx = {it["candidate_id"]: i for i, it in enumerate(items)}
    highlights.sort(key=lambda h: order_idx.get(h["candidate_id"], 10 ** 6))
    return _result(highlights, meanings, notices, issues)


def _result(highlights, meanings, notices, issues) -> dict:
    return {"status": "ISSUE" if issues else "OK", "highlights": highlights, "meanings": meanings, "notices": notices, "issues": issues,
            "stats": {"resolved": len(highlights), "decorated": sum(1 for h in highlights if h["decorate"]),
                      "notices": len(notices), "issues": len(issues)}}


# ============================================================
# 描画入力の取り出し
# ============================================================
def highlights_for_text(result: dict, unit_key: str, text_index: int = 0) -> list:
    """script_block(..., highlights=)へ渡すlist。装飾する片のみ [{kind,start,end,candidate_id,surface}] を start昇順で返す。"""
    out = []
    for h in result.get("highlights") or []:
        if not h.get("decorate"):
            continue
        for p in h["pieces"]:
            if p["unit_key"] == unit_key and p["text_index"] == text_index:
                out.append({"kind": h["kind"], "start": p["start"], "end": p["end"], "candidate_id": h["candidate_id"], "surface": p["text"]})
    out.sort(key=lambda x: (x["start"], x["end"]))
    return out


def meanings_for_unit(result: dict, unit_key: Optional[str]) -> list:
    """③の訳 [{used_form, japanese_gloss}]。unit_key=None は表示範囲外の③(節末に置く)。"""
    return [m for m in (result.get("meanings") or []) if m.get("unit_key") == unit_key]


# ============================================================
# 描画
# ============================================================
def open_tag(kind: int, cid: str) -> str:
    return f'<{KIND_TAG[kind]} class="{KIND_CLASS[kind]}" data-hl="{esc(str(cid), quote=True)}">'


def render_script_html(text: str, highlights: Optional[list] = None, boundary_positions=None, marker_html: str = "") -> str:
    """台本textをHTMLエスケープし、highlight(非重複・start昇順)を平坦なタグで包む。boundary_positions(=dev時のChunk境界、text上の文字位置)
    には marker_html を挿入するが、マーカーは常にハイライトの外(タグを閉じてから置き、続きがあれば再度開く)。
    highlightsが空なら esc(text) と(境界が無ければ)同一。各highlightは surface があれば text[start:end]==surface をassert。"""
    text = text or ""
    hls = sorted(highlights or [], key=lambda x: (x["start"], x["end"]))
    prev_end = 0
    for h in hls:
        assert 0 <= h["start"] < h["end"] <= len(text), f"highlight範囲不正: {h}"
        assert h["start"] >= prev_end, f"highlightが重なっている: {h}"
        if h.get("surface") is not None:
            assert text[h["start"]:h["end"]] == h["surface"], f"surface不一致: {text[h['start']:h['end']]!r} != {h['surface']!r}"
        prev_end = h["end"]
    bset = {b for b in (boundary_positions or []) if 0 <= b <= len(text)}
    cuts = sorted({0, len(text)} | bset | {h["start"] for h in hls} | {h["end"] for h in hls})
    out: list = []
    open_hl = None
    for a, b in zip(cuts, cuts[1:]):
        hl = next((h for h in hls if h["start"] <= a and b <= h["end"]), None)
        if hl is not open_hl:
            if open_hl is not None:
                out.append(f"</{KIND_TAG[open_hl['kind']]}>")
            if hl is not None:
                out.append(open_tag(hl["kind"], hl["candidate_id"]))
            open_hl = hl
        out.append(esc(text[a:b]))
        if b in bset and marker_html:
            if open_hl is not None:
                out.append(f"</{KIND_TAG[open_hl['kind']]}>")
                open_hl = None
            out.append(marker_html)
    if open_hl is not None:
        out.append(f"</{KIND_TAG[open_hl['kind']]}>")
    # 0位置の境界(先頭)があればマーカーを先頭へ(通常は発生しない)
    if 0 in bset and marker_html:
        out.insert(0, marker_html)
    return "".join(out)


def meaning_list_html(items: list) -> str:
    """③の「<used_form> ＝ <japanese_gloss>」ul(空なら"")。JS不要。"""
    if not items:
        return ""
    lis = "".join(f"<li>{esc(str(i.get('used_form') or ''))} ＝ {esc(str(i.get('japanese_gloss') or ''))}</li>" for i in items)
    return f'<ul class="lk-meaning">{lis}</ul>'


def legend_html() -> str:
    """凡例1行(①②③の見本。本文と同じCSS。data-hlなし=G3の集計対象外)。"""
    t = LEGEND_TEXT
    return ('<p class="lk-legend">' + esc(t[0]) + '<strong class="lk1">' + esc(t[1]) + "</strong>" + esc(t[2])
            + '<strong class="lk2">' + esc(t[3]) + "</strong>" + esc(t[4]) + '<span class="lk3">' + esc(t[5]) + "</span>" + esc(t[6]) + "</p>")


def strip_decoration(html_fragment: str) -> str:
    """装飾タグ(strong.lk1/lk2・span.lk3)とその閉じタグだけを剥がしたHTML(本文不変の検査用)。他のタグ(chunk-mark等)は残す。"""
    out, stack = [], []
    for tok in re.split(r"(<[^>]+>)", html_fragment):
        m = re.fullmatch(r"<(strong|span)\b([^>]*)>", tok)
        if m:
            deco = bool(re.search(r'class="lk[123]"', m.group(2)))
            stack.append(deco)
            if not deco:
                out.append(tok)
            continue
        m = re.fullmatch(r"</(strong|span)>", tok)
        if m:
            deco = stack.pop() if stack else False
            if not deco:
                out.append(tok)
            continue
        out.append(tok)
    return "".join(out)


# ============================================================
# CONTRACT_03 §2 形式への変換ビュー(アダプタ互換用。解決は resolve_highlights 1箇所のまま)
# ============================================================
CONTRACT_CODE_ALIASES = {
    "HL_NOT_IN_DISPLAY": "HL_SENTENCE_NOT_IN_DISPLAY",
    "HL_PARTIAL_OVERLAP": "HL_OVERLAP_PARTIAL",
    "HL_CONTAINED": "HL_CONTAINED_SKIPPED",
    "HL_PARTIAL_OVERLAP_3": "HL_OVERLAP_RANKED",
    "HL_NOT_IN_DISPLAY_MEANING_ONLY": "HL_MEANING_ONLY",
}


def contract_view(result: dict) -> dict:
    """{"highlights": {unit_key: [Highlight]}, "meanings": {unit_key: [{used_form, gloss}]}, "notices": [Notice]}。
    Highlight={candidate_id,kind,surface(片の本文),unit_key,start,end,gloss_short,used_form}+text_index(text単位のoffset。joiner込み連結offsetではない)。
    原因コードはCONTRACT_03 §4の名称へ変換(CONTRACT_CODE_ALIASES)。ISSUEは issues に残る(送出はしない=呼出側がfail-closed)。"""
    hls: dict = {}
    for h in result.get("highlights") or []:
        if not h.get("decorate"):
            continue
        for p in h["pieces"]:
            hls.setdefault(p["unit_key"], []).append({"candidate_id": h["candidate_id"], "kind": h["kind"], "surface": p["text"], "unit_key": p["unit_key"],
                                                      "start": p["start"], "end": p["end"], "text_index": p["text_index"], "gloss_short": h.get("gloss"), "used_form": h["used_form"]})
    ms: dict = {}
    for m in result.get("meanings") or []:
        ms.setdefault(m.get("unit_key"), []).append({"used_form": m["used_form"], "gloss": m["japanese_gloss"]})
    notices = [{**n, "code": CONTRACT_CODE_ALIASES.get(n["code"], n["code"])} for n in (result.get("notices") or [])]
    issues = [{**n, "code": CONTRACT_CODE_ALIASES.get(n["code"], n["code"])} for n in (result.get("issues") or [])]
    return {"highlights": hls, "meanings": ms, "notices": notices, "issues": issues}
