# -*- coding: utf-8 -*-
"""選定フォームv3 出現回数集計(er140_selection_occurrence_count_01)の入力 loader: Family X/Y/Z の run dir から 4区分(+title)の英語本文を読む(読み取り専用・API 0)。

SELECTION-UI-OCCURRENCE-COUNT-01 委任_02。委任_01の試作 `docs/research/SELECTION-UI-OCCURRENCE-COUNT-01/tools/section_loaders_01.py` の昇格版。
区分と正式テキスト所在(選定フォーム生成時点=KP review待機点で既に全て存在する):
  X: <out>/<lv>/parts.json {title, part1..3, in_one_line} + <out>/<lv>/{b1_support_texts|a2_support_texts}.json {preview, comment_1..4}
  Y: <out>/translate/<lv>.md (title行 + 本文。Story=本文全段落) + <out>/support/<lv>_support.json {preview, comment_1..3}
  Z: <out>/writer/{r2.md(b1b)|std.md(a2)} (title行 + 本文) + <out>/support/<lv>_support.json {preview, comments{1..3}}
  Standard(a2)のPreview/Commentは日本語(Listening Support)。英語tokenを含まないため自然に0(別処理しない)。In One LineはXのみ。
本文が見つからない区分は None(=未取得 unavailable)で返し、0とは区別する。

単位(unit)は「空行区切りの段落」ではなく「1行」: 段落内の改行を空白に潰すと、Yの見出し・話者ラベル行(`First to speak is ...`)と本文の1行目が連結し、
改行をまたぐ一致が成立してしまう(集計規則は改行をまたがない)。実データ(Y 240段落・X 1733段落)の複数行段落は全行が文末記号で終わる=
行途中で折り返した本文は無く、行単位に分けても取りこぼしは生じない(`EVIDENCE_01.md`)。
"""
from __future__ import annotations

import hashlib
import json
import os
import re

_EXPECT = ("story", "comment", "preview", "oneline", "title")


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def units(body: str) -> list:
    """本文を1行=1 unit のlistにする(空行は捨てる。行内の連続空白は1つに正規化)。"""
    return [" ".join(ln.split()) for ln in (body or "").replace("\r\n", "\n").split("\n") if ln.strip()]


def _md_title_body(md: str) -> tuple:
    t = md.replace("\r\n", "\n").strip()
    m = re.match(r"^#\s+(.+?)[ \t]*\n+(.*)$", t, re.S)
    return (m.group(1).strip(), m.group(2)) if m else ("", t)


def _first_existing(roots: list, rel: str):
    for r in roots:
        p = os.path.join(r, rel)
        if os.path.exists(p):
            return p
    return None


def out_dir_of(cand_path: str) -> str:
    """source_kp_candidates_path(X: <out>/<lv>/key_phrases/kp_candidates.json / Y,Z: <out>/key_phrases/<lv>/kp_candidates.json)からrun出力dirを導出。"""
    return os.path.dirname(os.path.dirname(os.path.dirname(cand_path))).replace("\\", "/")


def load_sections(family: str, cand_path: str, level: str, roots: list | None = None) -> tuple:
    """returns (sections: dict[str, list|None], sources: dict[str,str|None])。
    cand_pathが絶対pathならそのまま、相対pathなら roots(既定=[cwd])の各rootの下を探す。"""
    out = out_dir_of(cand_path)
    roots = list(roots) if roots else [os.getcwd()]
    if os.path.isabs(out):
        roots = [""]
    sec = {k: None for k in _EXPECT}
    src = {k: None for k in sec}

    def rd(rel):
        p = _first_existing(roots, rel) if roots != [""] else (rel if os.path.exists(rel) else None)
        return (p, _read(p)) if p else (None, None)

    if family == "X":
        p, txt = rd(f"{out}/{level}/parts.json")
        if txt:
            d = json.loads(txt)
            sec["story"] = [u for k in ("part1", "part2", "part3") for u in units(d.get(k) or "")]
            sec["title"] = [d.get("title") or ""]
            sec["oneline"] = units(d.get("in_one_line") or "")
            src["story"] = src["title"] = src["oneline"] = p
        sp, st = rd(f"{out}/{level}/{'b1_support_texts' if level == 'b1b' else 'a2_support_texts'}.json")
        if st:
            d = json.loads(st)
            sec["preview"] = units(d.get("preview") or "")
            sec["comment"] = [u for k in sorted(d) if re.fullmatch(r"comment_\d+", k) and d[k] for u in units(d[k])]
            src["preview"] = src["comment"] = sp
    else:
        if family == "Y":
            p, txt = rd(f"{out}/translate/{level}.md")
        else:
            p, txt = rd(f"{out}/writer/{'r2.md' if level == 'b1b' else 'std.md'}")
        if txt:
            title, body = _md_title_body(txt)
            sec["story"] = units(body)
            sec["title"] = [title]
            sec["oneline"] = []          # Y/Zにはリスナー向けIn One Lineが無い(enduser page実測: X以外にoneline kindなし)
            src["story"] = src["title"] = p
            src["oneline"] = "(none: family has no In One Line)"
        sp, st = rd(f"{out}/support/{level}_support.json")
        if st:
            d = json.loads(st)
            sec["preview"] = units(d.get("preview") or "")
            cm = []
            if isinstance(d.get("comments"), dict):
                cm = [v for _, v in sorted(d["comments"].items()) if isinstance(v, str) and v]
            cm += [d[k] for k in sorted(d) if re.fullmatch(r"comment_\d+", k) and d[k]]
            sec["comment"] = [u for c in cm for u in units(c)]
            src["preview"] = src["comment"] = sp
    return sec, src


def sections_meta(sections: dict, sources: dict, root: str | None = None) -> dict:
    """occurrence_meta用: 区分ごとに数えた本文のsha256・unit数・出所(root相対)。未取得は unavailable に区分名を入れる。"""
    secs, unavailable = {}, []
    for k in _EXPECT:
        v = sections.get(k)
        if v is None:
            if k != "title":
                unavailable.append(k)
            continue
        s = sources.get(k)
        if s and root and os.path.isabs(s):
            try:
                s = os.path.relpath(s, root)
            except ValueError:
                pass
        secs[k] = {"sha256": hashlib.sha256("\n".join(v).encode("utf-8")).hexdigest(), "units": len(v), "source": (s or "").replace("\\", "/")}
    return {"v": "occ-v1", "sections": secs, "unavailable": unavailable}
