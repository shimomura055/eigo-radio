"""SLOT-23-CONSUMER-DESIGN-01 委任_04A: G3 本文ハイライト検査(純関数)。

`verify_highlights(level_section_html, expected)` はページHTMLのlevel節を検査し、結果dictを返す(例外は投げない。呼出側が status で
fail-closed(rc=3 INTEGRITY)に接続する=C/D/E班の配線)。er128本体は遅延importで kill switch(`EIGO_KP_CONFIRMED_PROTECTION=0`)の読取点
`protection_enabled()` を参照するだけ。表示の有効化判断(display_spec/std_part1)は本moduleでは行わない(呼出側が確定レコードを直接読む)。
"""
from __future__ import annotations

import re
from html.parser import HTMLParser

CHUNK_MARK = "⏸"


class _Collector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack: list = []            # [(tag, attrs, capture_idx or None)]
        self.hl: list = []               # [{cid, tag, cls, text}]
        self.scripts: list = []          # div.script のtextContent(chunk-mark本体を除く)
        self.meaning: list = []          # ul.lk-meaning の li text
        self.html_mark_count = 0
        self._cur_script = None
        self._cur_li = None
        self._in_mark = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        node = {"tag": tag, "cls": cls}
        if "data-hl" in a:
            node["hl"] = {"cid": a["data-hl"], "tag": tag, "cls": cls, "text": ""}
            self.hl.append(node["hl"])
        if tag == "div" and "script" in cls:
            node["script"] = True
            self._cur_script = []
        if tag == "li" and any(n.get("meaning_ul") for n in self.stack):
            node["li"] = True
            self._cur_li = []
        if tag == "ul" and ("lk-meaning" in cls or "hl-meaning" in cls):   # hl-meaning=CONTRACT_03表記も受理
            node["meaning_ul"] = True
        if CHUNK_MARK_CLASS in cls:
            node["mark"] = True
            self._in_mark += 1
            self.html_mark_count += 1
        self.stack.append(node)

    def handle_endtag(self, tag):
        for k in range(len(self.stack) - 1, -1, -1):
            if self.stack[k]["tag"] == tag:
                node = self.stack[k]
                del self.stack[k:]
                if node.get("script") and self._cur_script is not None:
                    self.scripts.append("".join(self._cur_script))
                    self._cur_script = None
                if node.get("li") and self._cur_li is not None:
                    self.meaning.append("".join(self._cur_li))
                    self._cur_li = None
                if node.get("mark"):
                    self._in_mark -= 1
                break

    def handle_data(self, data):
        for n in self.stack:
            if "hl" in n:
                n["hl"]["text"] += data
        if self._cur_script is not None and not self._in_mark:
            self._cur_script.append(data)
        if self._cur_li is not None:
            self._cur_li.append(data)


CHUNK_MARK_CLASS = "chunk-mark"


def _ws(s: str) -> str:
    return " ".join((s or "").replace(CHUNK_MARK, "").split())


def verify_highlights(level_section_html: str, expected: dict) -> dict:
    """expected = {"result": resolve_highlights結果, "script_texts": [従来の台本テキスト(表示順。省略可)], "audience": "public"|"dev"}。
    returns {"status": "PASS"|"FAIL"|"SKIPPED_DISABLED", "problems": [{code,candidate_id,detail}], "disabled_marker": bool, "counts": {...}}。"""
    import er128_kp_confirmed_content_01 as er128   # 遅延import(kill switchの読取点だけを参照)
    if not er128.protection_enabled():
        return {"status": "SKIPPED_DISABLED", "problems": [], "disabled_marker": True, "counts": {}}
    result = expected.get("result") or {}
    audience = expected.get("audience", "public")
    probs: list = []

    def P(code, cid, detail):
        probs.append({"code": code, "candidate_id": cid, "detail": detail})

    col = _Collector()
    col.feed(level_section_html)
    by_cid: dict = {}
    for h in col.hl:
        by_cid.setdefault(h["cid"], []).append(h)

    notice_ids = {n["candidate_id"] for n in (result.get("notices") or [])}
    exp_ids = set()
    for h in result.get("highlights") or []:
        cid = h["candidate_id"]
        exp_ids.add(cid)
        els = by_cid.get(cid, [])
        if h.get("decorate"):
            if not els:
                P("G3HL_MISSING", cid, "装飾要素が無い")
                continue
            want_cls = {"lk1": 1, "lk2": 2, "lk3": 3}
            for e in els:
                kinds = {want_cls[c] for c in e["cls"] if c in want_cls}
                if kinds != {h["kind"]}:
                    P("G3HL_WRONG_KIND", cid, f"class={e['cls']} 期待区分={h['kind']}")
                exp_tag = "span" if h["kind"] == 3 else "strong"
                if e["tag"] != exp_tag:
                    P("G3HL_WRONG_TAG", cid, f"<{e['tag']}> 期待<{exp_tag}>")
            got = "".join(e["text"] for e in els)
            if got != h["surface"]:
                P("G3HL_TEXT_MISMATCH", cid, f"textContent={got!r} 期待={h['surface']!r}")
            if len(els) < len(h["pieces"]):
                P("G3HL_PIECES_FEWER", cid, f"要素{len(els)}個 < 片{len(h['pieces'])}個")
        else:
            if els:
                P("G3HL_UNEXPECTED_DECORATION", cid, "装飾省略(NOTICE)の項目が装飾されている")
            if cid not in notice_ids:
                P("G3HL_NO_NOTICE_FOR_OMISSION", cid, "装飾を省いたがNOTICE理由が無い")
    # ISSUEの項目は装飾の網羅対象外(解決失敗=ページ生成前STOPが先)。ここでの余剰=期待に無いdata-hl
    for cid in by_cid:
        if cid not in exp_ids:
            P("G3HL_EXTRA", cid, "期待に無い装飾要素")
    # ③訳リスト
    want_m = sorted(f"{m.get('used_form') or ''} ＝ {m.get('japanese_gloss') or ''}" for m in (result.get("meanings") or []))
    got_m = sorted(" ".join(t.split()) for t in col.meaning)
    if want_m != got_m:
        P("G3HL_MEANING_MISMATCH", None, f"期待={want_m} 実際={got_m}")
    # 本文不変
    st = expected.get("script_texts")
    if st is not None:
        wants = [_ws(t) for t in st]
        gots = [_ws(t) for t in col.scripts]
        k = 0
        for g in gots:
            if k < len(wants) and g == wants[k]:
                k += 1
        if k != len(wants):
            P("G3HL_BODY_CHANGED", None, f"台本テキストが従来と一致しない(一致{k}/{len(wants)}ブロック)")
    # public混入
    if audience == "public" and (CHUNK_MARK in level_section_html or "&#9208;" in level_section_html or "chunk-mark" in level_section_html):
        P("G3HL_PUBLIC_MARKER", None, "public出力に⏸/chunk-markが混入")
    return {"status": "FAIL" if probs else "PASS", "problems": probs, "disabled_marker": False,
            "counts": {"decorated_elements": len(col.hl), "candidates": len(by_cid), "meaning_items": len(col.meaning), "script_blocks": len(col.scripts)}}
