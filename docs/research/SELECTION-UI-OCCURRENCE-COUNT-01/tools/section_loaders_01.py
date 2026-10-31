# -*- coding: utf-8 -*-
"""SELECTION-UI-OCCURRENCE-COUNT-01 委任_01: Family X/Y/Z のrun dirから、出現回数の集計対象4区分(+title)の英語本文を読むloader(試作。読み取り専用・API 0)。

区分と正式テキスト所在(選定フォーム生成時点=KP review待機点で既に全て存在する。X: er019 runner scaffold内 support->KP の順 / Y: STAGES text->translate->support->kp / Z: E2E_STAGES writer->std_adjust->plan->support->kp):
  X: <out>/<lv>/parts.json {title, part1..3, in_one_line} + <out>/<lv>/{b1_support_texts|a2_support_texts}.json {preview, comment_1..4}
  Y: <out>/translate/<lv>.md (title行 + 本文。Story=本文全段落[Lead/Voice紹介/Voice/Closing]) + <out>/support/<lv>_support.json {preview, comment_1..3}
  Z: <out>/writer/{r2.md(b1b)|std.md(a2)} (title行 + 本文) + <out>/support/<lv>_support.json {preview, comments{1..3}}
  Standard(a2)のPreview/Commentは日本語(Listening Support)。英語tokenを含まないため自然に0。In One LineはXのみ。
本文が見つからない区分は None(=未取得 unavailable)で返し、0とは区別する。
"""
from __future__ import annotations

import json
import os
import re


def _read(path: str):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _paras(body: str) -> list:
    return [" ".join(p.split()) for p in re.split(r"\n\s*\n", body.replace("\r\n", "\n")) if p.strip()]


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


def out_dir_of(family: str, cand_path: str) -> str:
    """source_kp_candidates_path(例 X: <out>/<lv>/key_phrases/kp_candidates.json / Y,Z: <out>/key_phrases/<lv>/kp_candidates.json)からrun出力dirを導出。"""
    return os.path.dirname(os.path.dirname(os.path.dirname(cand_path))).replace("\\", "/")


def load_sections(family: str, cand_path: str, level: str, roots: list) -> tuple:
    """returns (sections: dict[str, list|None], sources: dict[str,str|None])。"""
    out = out_dir_of(family, cand_path)
    sec = {"story": None, "comment": None, "preview": None, "oneline": None, "title": None}
    src = {k: None for k in sec}

    def rd(rel):
        p = _first_existing(roots, rel)
        return (p, _read(p)) if p else (None, None)

    if family == "X":
        p, txt = rd(f"{out}/{level}/parts.json")
        if txt:
            d = json.loads(txt)
            sec["story"] = [x for k in ("part1", "part2", "part3") for x in _paras(d.get(k) or "")]
            sec["title"] = [d.get("title") or ""]
            if (d.get("in_one_line") or "").strip():
                sec["oneline"] = _paras(d["in_one_line"])
            else:
                sec["oneline"] = []
            src["story"] = src["title"] = src["oneline"] = p
        sp, st = rd(f"{out}/{level}/{'b1_support_texts' if level == 'b1b' else 'a2_support_texts'}.json")
        if st:
            d = json.loads(st)
            sec["preview"] = [d["preview"]] if d.get("preview") else []
            sec["comment"] = [d[k] for k in sorted(d) if re.fullmatch(r"comment_\d+", k) and d[k]]
            src["preview"] = src["comment"] = sp
    else:
        if family == "Y":
            p, txt = rd(f"{out}/translate/{level}.md")
        else:
            p, txt = rd(f"{out}/writer/{'r2.md' if level == 'b1b' else 'std.md'}")
        if txt:
            title, body = _md_title_body(txt)
            sec["story"] = _paras(body)
            sec["title"] = [title]
            sec["oneline"] = []          # Y/Zにはリスナー向けIn One Lineが無い(enduser page実測: X以外にoneline kindなし)
            src["story"] = src["title"] = p
            src["oneline"] = "(none: family has no In One Line)"
        sp, st = rd(f"{out}/support/{level}_support.json")
        if st:
            d = json.loads(st)
            sec["preview"] = [d["preview"]] if d.get("preview") else []
            cm = []
            if isinstance(d.get("comments"), dict):
                cm = [v for _, v in sorted(d["comments"].items()) if isinstance(v, str) and v]
            cm += [d[k] for k in sorted(d) if re.fullmatch(r"comment_\d+", k) and d[k]]
            sec["comment"] = cm
            src["preview"] = src["comment"] = sp
    return sec, src


def load_enduser_sections(article_json_path: str, level: str) -> dict:
    """公開済みenduser page(enduser_article_v1)のparts[kind]からの区分別本文(照合用。Story=kind story全て)。level: std|adv。"""
    with open(article_json_path, encoding="utf-8") as f:
        d = json.load(f)
    kmap = {"story": "story", "comment": "comment", "preview": "preview", "oneline": "oneline", "topic": "title"}
    out = {"story": [], "comment": [], "preview": [], "oneline": [], "title": []}
    for p in d["levels"][level]["parts"]:
        k = kmap.get(p.get("kind"))
        if not k:
            continue
        for para in p.get("paragraphs") or []:
            txts = []
            for s in para:
                if isinstance(s, dict) and s.get("text"):
                    txts.append(s["text"])
            if txts:
                out[k].append(" ".join(txts))
    return out
