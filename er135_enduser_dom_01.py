# -*- coding: utf-8 -*-
"""END-USER-LISTENING-PAGE-PRODUCTION-WIRING-01 委任_02B: 軽量DOMと文分割(er135_enduser_page_01.pyの部品)。

 - HTMLは`html.parser`でtreeにする。dev HTMLを正規表現で解析しない(Opus M1)。
 - 文分割は文字列のHTMLを経由せずtoken列で行う。規則(引用符閉じ・略語・小文字継続・日本語。！？)はDEV試作の決定論規則と同一。
DEV/Trial資産のpath・moduleは参照しない。
"""
from __future__ import annotations

import html as _html
import re
from html.parser import HTMLParser


class EnduserPageStop(Exception):
    """End Userページ生成の停止(fail-closed)。codeは`ENDUSER_*`。dev index.htmlは不変、`enduser/`は書かれない。"""

    def __init__(self, code: str, message: str = ""):
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}" if message else code)


def stop(code: str, message: str = ""):
    raise EnduserPageStop(code, message)


# ------------------------------------------------------------
# 軽量DOM
# ------------------------------------------------------------
VOID_TAGS = {"br", "img", "hr", "input", "meta", "link", "wbr", "source", "col"}


class Node:
    __slots__ = ("tag", "attrs", "children", "parent")

    def __init__(self, tag, attrs=None, parent=None):
        self.tag, self.attrs, self.children, self.parent = tag, dict(attrs or {}), [], parent

    def classes(self) -> list:
        return (self.attrs.get("class") or "").split()

    def has_class(self, c) -> bool:
        return c in self.classes()

    def elements(self) -> list:
        return [c for c in self.children if isinstance(c, Node)]

    def iter(self):
        for c in self.children:
            if isinstance(c, Node):
                yield c
                yield from c.iter()

    def find_all(self, tag=None, cls=None, pred=None) -> list:
        out = []
        for n in self.iter():
            if tag and n.tag != tag:
                continue
            if cls and not n.has_class(cls):
                continue
            if pred and not pred(n):
                continue
            out.append(n)
        return out

    def find(self, tag=None, cls=None, pred=None):
        r = self.find_all(tag, cls, pred)
        return r[0] if r else None

    def text(self, skip=None) -> str:
        parts = []
        for c in self.children:
            if isinstance(c, str):
                parts.append(c)
            elif skip is None or not skip(c):
                parts.append(c.text(skip))
        return "".join(parts)

    def inside(self, tag=None, cls=None) -> bool:
        p = self.parent
        while p is not None:
            if (tag is None or p.tag == tag) and (cls is None or p.has_class(cls)):
                return True
            p = p.parent
        return False


class _Builder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root")
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        n = Node(tag, {k: (v if v is not None else "") for k, v in attrs}, self.stack[-1])
        self.stack[-1].children.append(n)
        if tag not in VOID_TAGS:
            self.stack.append(n)

    def handle_startendtag(self, tag, attrs):
        n = Node(tag, {k: (v if v is not None else "") for k, v in attrs}, self.stack[-1])
        self.stack[-1].children.append(n)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        ch = self.stack[-1].children
        if ch and isinstance(ch[-1], str):
            ch[-1] += data
        else:
            ch.append(data)


def parse_html(text: str) -> Node:
    b = _Builder()
    b.feed(text)
    b.close()
    return b.root


# ------------------------------------------------------------
# 文分割
# ------------------------------------------------------------
ABBR = re.compile(r"(?:\b(?:Mr|Mrs|Ms|Dr|St|vs|etc|No|Inc|Jr|Sr)|\b[A-Z])\.$")
_CUT_RE = re.compile(r"([.!?]+[\"”’')]*)(\s+|$)|([。！？]+[」』）)\"”]*)")


def find_cuts(text: str) -> list:
    """平文を文末位置(文字index)のlistへ。略語のピリオド・小文字で続く場合は切らない。"""
    cuts = []
    for m in _CUT_RE.finditer(text):
        end = m.end(1) if m.group(1) else m.end(3)
        if m.group(1):
            if ABBR.search(text[: m.end(1)]):
                continue
            rest = text[m.end():]
            if rest and rest[0].islower():
                continue
        if end < len(text.rstrip()):
            cuts.append(end)
    return cuts


_KEEP_INLINE = {"span", "strong", "b", "i", "em"}
LK_CLASSES = ("lk1", "lk2", "lk3")


def inline_tokens(node: Node, out: list) -> None:
    """script要素の子をtoken列 [('t',str)|('o',tag,attrs)|('c',tag)] に平坦化する。
    chunk-markは除去、rpt-*(LR赤/Fallback青)は展開(本文テキストは不変)、未知markupはSTOP。"""
    for c in node.children:
        if isinstance(c, str):
            out.append(("t", c))
            continue
        cl = c.classes()
        if c.tag == "span" and "chunk-mark" in cl:
            continue
        if c.tag == "span" and cl and all(x.startswith("rpt-") for x in cl):
            inline_tokens(c, out)
            continue
        if c.tag == "br":
            out.append(("t", "\n"))
            continue
        if c.tag in _KEEP_INLINE:
            keep = [x for x in cl if x in LK_CLASSES]
            if c.tag == "span" and (len(keep) != 1 or len(cl) != 1):
                stop("ENDUSER_UNKNOWN_MARKUP", f"script内の未知のspan class={cl}")
            if c.tag != "span" and cl and len(keep) != len(cl):
                stop("ENDUSER_UNKNOWN_MARKUP", f"script内の未知の{c.tag} class={cl}")
            attrs = []
            if keep:
                attrs.append(("class", keep[0]))
                if "data-hl" in c.attrs:
                    attrs.append(("data-hl", c.attrs["data-hl"]))
            out.append(("o", c.tag, tuple(attrs)))
            inline_tokens(c, out)
            out.append(("c", c.tag))
            continue
        stop("ENDUSER_UNKNOWN_MARKUP", f"script内の未知のtag <{c.tag}> class={cl}")


def render_tokens(toks: list) -> str:
    out = []
    for t in toks:
        if t[0] == "t":
            out.append(_html.escape(t[1], quote=False))
        elif t[0] == "o":
            out.append("<" + t[1] + "".join(f' {k}="{_html.escape(v, quote=True)}"' for k, v in t[2]) + ">")
        else:
            out.append("</" + t[1] + ">")
    return "".join(out)


def tokens_plain(toks) -> str:
    return "".join(t[1] for t in toks if t[0] == "t")


def merge_text(toks: list) -> list:
    out = []
    for t in toks:
        if t[0] == "t" and t[1] == "":
            continue
        if t[0] == "t" and out and out[-1][0] == "t":
            out[-1] = ("t", out[-1][1] + t[1])
        else:
            out.append(t)
    return out


_PARA_RE = re.compile(r"\n[ \t\r\f\v]*\n\s*")


def split_paragraphs(toks: list) -> list:
    """空行でparagraph分割。開いたtagが跨る場合は閉じて再開する。空paragraphは捨てる。"""
    paras, cur, stack = [], [], []
    for t in toks:
        if t[0] == "o":
            stack.append(t)
            cur.append(t)
        elif t[0] == "c":
            if stack:
                stack.pop()
            cur.append(t)
        else:
            for i, p in enumerate(_PARA_RE.split(t[1])):
                if i > 0:
                    paras.append(cur + [("c", s[1]) for s in reversed(stack)])
                    cur = list(stack)
                cur.append(("t", p))
    paras.append(cur)
    out = []
    for p in paras:
        p = merge_text(p)
        if tokens_plain(p).strip():
            out.append(p)
    return out


def newline_to_space(toks: list) -> list:
    return [("t", t[1].replace("\n", " ")) if t[0] == "t" else t for t in toks]


def _trim(toks: list) -> list:
    toks = merge_text(list(toks))
    for i, t in enumerate(toks):
        if t[0] == "t":
            s = t[1].lstrip()
            toks[i] = ("t", s)
            if s:
                break
    for i in range(len(toks) - 1, -1, -1):
        if toks[i][0] == "t":
            s = toks[i][1].rstrip()
            toks[i] = ("t", s)
            if s:
                break
    return [t for t in toks if not (t[0] == "t" and t[1] == "")]


def split_sentences(toks: list) -> list:
    """paragraph(token列) -> 文(token列)のlist。切れ目直後の閉じtagは直前の文へ含める(空spanを次の文へ送らない)。"""
    cutset = set(find_cuts(tokens_plain(toks)))
    sents, cur, stack, pos, pending = [], [], [], 0, False

    def flush():
        nonlocal cur, pending
        sents.append(cur + [("c", s[1]) for s in reversed(stack)])
        cur = list(stack)
        pending = False

    for t in toks:
        if t[0] == "c":
            cur.append(t)
            if stack:
                stack.pop()
            continue
        if pending:
            flush()
        if t[0] == "o":
            cur.append(t)
            stack.append(t)
            continue
        for ch in t[1]:
            if pending:
                flush()
            cur.append(("t", ch))
            pos += 1
            if pos in cutset:
                pending = True
    if pending:
        flush()
    elif tokens_plain(cur).strip():
        sents.append(cur)
    out = []
    for s in sents:
        s = _trim(s)
        if tokens_plain(s).strip():
            out.append(s)
    return out


def paragraphs_of_divs(divs: list, sid_start: int, key: str) -> tuple:
    """div.script群 -> (paragraphs [[{sid,html,text}]], 次のsid連番)。
    1 div内の空行はparagraph分割(X)、複数div(Zの話者別clip)はdiv単位で独立(話者divをまたぐ文を結合しない)。"""
    paragraphs, n = [], sid_start
    for d in divs:
        toks: list = []
        inline_tokens(d, toks)
        for para in split_paragraphs(merge_text(toks)):
            sents = []
            for s in split_sentences(newline_to_space(para)):
                sents.append({"sid": f"{key}-s{n:03d}", "html": render_tokens(s), "text": tokens_plain(s)})
                n += 1
            if sents:
                paragraphs.append(sents)
    return paragraphs, n


def lk_spans(html_fragment: str) -> list:
    """文HTML断片内の下線対象span/strong(class=lk1/lk2/lk3, data-hl) -> [(data_hl, lk, 平文)]。HTMLParserで解析する。"""
    root = parse_html(html_fragment)
    out = []
    for n in root.find_all(pred=lambda x: x.tag in ("span", "strong") and any(c in LK_CLASSES for c in x.classes())):
        lk = [c for c in n.classes() if c in LK_CLASSES][0]
        out.append((n.attrs.get("data-hl", ""), lk, n.text()))
    return out
