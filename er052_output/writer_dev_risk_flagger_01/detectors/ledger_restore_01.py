# -*- coding: utf-8 -*-
"""台帳(verified_fact_ledger.txt)の解析と、casebankケースの『当該記事の全台帳』の復元(委任_02 P0)。
DEV専用。ラベルは一切読まない(読むのはfact.src=台帳ファイルのパスとfact本文のみ)。
復元優先順: (1) fact.srcが指す台帳ファイル / (2) 他ケースで解決済みの台帳プールから、同一fact_idかつ同一本文の台帳 /
(3) 単一Factのみ(ledger_complete=False)。LLMへ渡すfactsは fact_id と text(ブロック全文、[VERIFIED] ID:接頭辞なし)のみ。
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
_HDR = re.compile(r"^\[(?P<st>[A-Z_]+)\]\s+(?P<id>[^\s:]+):\s*(?P<text>.*)$")
_PREFIX = re.compile(r"^\[[A-Z_]+\]\s+[^\s:]+:\s*")


def strip_prefix(text):
    return _PREFIX.sub("", (text or "").strip(), count=1)


def parse_ledger_text(txt):
    """台帳テキスト -> [{fact_id, text}]。textはブロック全文(1行目の接頭辞は除去)。"""
    facts, cur = [], None
    for ln in txt.splitlines():
        m = _HDR.match(ln)
        if m:
            cur = dict(fact_id=m.group("id"), lines=[m.group("text")])
            facts.append(cur)
        elif cur is not None and ln.strip():
            cur["lines"].append(ln.rstrip())
        elif cur is not None and not ln.strip():
            cur = None
    return [dict(fact_id=f["fact_id"], text="\n".join(f["lines"])) for f in facts]


def parse_ledger_file(path):
    with open(path, encoding="utf-8") as f:
        return parse_ledger_text(f.read())


def _src_path(src):
    """'path L74' / 'path:74' / 'path' -> 相対path。ledger .txt のみ採用。"""
    if not src:
        return None
    s = src.strip()
    m = re.match(r"^(\S+?\.txt)(?:[ :]|$)", s)
    if not m:
        return None
    p = os.path.join(REPO, m.group(1))
    return p if os.path.isfile(p) else None


def _first_line(text):
    return strip_prefix(text).split("\n")[0].strip()


class LedgerPool(object):
    def __init__(self):
        self.pool = {}  # path -> facts

    def load(self, path):
        if path not in self.pool:
            self.pool[path] = parse_ledger_file(path)
        return self.pool[path]

    def find_by_fact(self, fact_id, text):
        want = _first_line(text)
        for path in sorted(self.pool):
            for f in self.pool[path]:
                if f["fact_id"] == fact_id and (not want or _first_line(f["text"]) == want):
                    return path
        # 2nd pass: 同一fact_idで本文の先頭40字が一致(翻訳・整形差の吸収)
        for path in sorted(self.pool):
            for f in self.pool[path]:
                if f["fact_id"] == fact_id and want and _first_line(f["text"])[:40] == want[:40]:
                    return path
        return None


def restore_for_cases(cases):
    """cases: casebank['cases'] 形式のlist -> {case_id: dict(ledger=[...], ledger_complete=bool, origin=str)}。"""
    pool = LedgerPool()
    resolved = {}
    for c in cases:
        p = _src_path((c.get("fact") or {}).get("src"))
        if p:
            pool.load(p)
            resolved[c["case_id"]] = p
    out = {}
    for c in cases:
        fact = c.get("fact") or {}
        fid, ftext = fact.get("id"), strip_prefix(fact.get("text") or "")
        p = resolved.get(c["case_id"])
        origin = "src" if p else None
        if not p and fid:
            p = pool.find_by_fact(fid, fact.get("text") or "")
            origin = "pool" if p else None
        if p:
            facts = [dict(f) for f in pool.pool[p]]
            if fid and ftext and not any(f["fact_id"] == fid for f in facts):
                facts.append(dict(fact_id=fid, text=ftext))
            out[c["case_id"]] = dict(ledger=facts, ledger_complete=True,
                                     origin="%s:%s" % (origin, os.path.relpath(p, REPO).replace("\\", "/")))
        else:
            facts = [dict(fact_id=fid or "F", text=ftext)] if ftext else []
            out[c["case_id"]] = dict(ledger=facts, ledger_complete=False, origin="single")
    return out
