# -*- coding: utf-8 -*-
"""END-USER-LISTENING-PAGE-PRODUCTION-WIRING-01 委任_02B: End User向け視聴ページ(`<既存dir>/enduser/index.html`)の生成・検証。

位置づけ(WIRING_DESIGN_01 §1/§4/§5/§7 + Opus条件Aレビュー反映M1-M8): Production code・flagなし
(ユーザー正式採用APPROVED_FOR_PRODUCTION済み。runner hook=WP-E完了までPRODUCTION_WIRED前)。API呼出0。
 - 入力 : 最終dev `index.html`(HTMLパーサで解析。正規表現でHTMLを解析しない=M1) + family別補助(X: 承認済み日本語原稿) + 同期json(`enduser_sync_v1`。
          生成は02A `er135_enduser_sync_01.py`。本moduleは同期を呼ばず、rowsを渡し同期jsonを受ける側のみ)
 - 出力 : `<dev_dir>/enduser/{index.html,app.js,style.css,data/article.json,data/sync_<lv>.json,build_info.json}`。audioは`../`の既存mp3を参照(複製0)
 - 失敗 : `EnduserPageStop(ENDUSER_*)`。一時dirへ生成→一括renameなので失敗時は`enduser/`を書かない(M4)。既存`enduser/`は失敗時に削除しない(stale検出=M6)
 - DEV/Trial資産(試作ページ・試作script)のpathはimport・読込しない(静的testで検査)。

公開API: parse_dev_page / build_rows_from_dev_html / compute_kp_audio / build_enduser_data / validate_output / write_enduser_page /
         verify_consistency / build_enduser(一括) / main(CLI: build | verify-consistency | verify-only)
"""
from __future__ import annotations

import argparse
import datetime as _dt
import difflib
import hashlib
import html as _html
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

import er135_enduser_dom_01 as D
import er135_enduser_rules_01 as R
from er135_enduser_dom_01 import EnduserPageStop, Node, parse_html, stop

ROOT = Path(__file__).resolve().parent
ASSET_DIR = ROOT / "enduser_page_assets" / R.ASSET_BUILD_ID
ASSET_FILES = ("index.html", "app.js", "style.css")
ASSET_MANIFEST = "ASSET_SHA256.json"
ENDUSER_DIRNAME = "enduser"
KP_METHOD = "silencedetect -40dB d=0.2: 発話ブロック2番目(ブロック数>=4)=最初の英語発話。ASR転写でKP表現と一致確認"
JA_CHAR = re.compile(r"[ぁ-んァ-ヶ一-龠]")
TIME_TOL = 0.05


# ------------------------------------------------------------
# 汎用
# ------------------------------------------------------------
def sha256_file(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_text_bytes(b: bytes) -> str:
    """テキスト(HTML/JS/CSS/JSON)のsha。改行(CRLF/LF)の違いで変わらない(Windowsのautocrlfでcheckoutされても整合検査が偽陽性にならない)。"""
    return sha256_bytes(b.replace(b"\r\n", b"\n"))


def sha256_text_file(p) -> str:
    return sha256_text_bytes(Path(p).read_bytes())


def canon_sha(obj) -> str:
    return sha256_bytes(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8"))


def _ws(s: str) -> str:
    return re.sub(r"\s+", "", s or "")


def _has_ja(s: str) -> bool:
    return bool(JA_CHAR.search(s or ""))


def _ffmpeg() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        w = shutil.which("ffmpeg")
        if not w:
            stop("ENDUSER_FFMPEG_MISSING", "ffmpegが見つかりません")
        return w


def _mp3_duration(path) -> float:
    o = subprocess.run([_ffmpeg(), "-hide_banner", "-i", str(path)], capture_output=True, text=True, errors="replace").stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", o)
    if not m:
        stop("ENDUSER_AUDIO_UNREADABLE", f"音声の長さを取得できません: {path}")
    return round(int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]), 3)


def make_probe(dev_dir):
    """dev_dir相対のmp3 path -> {'sha256','duration'}(無ければNone)。"""
    base, cache = Path(dev_dir), {}

    def probe(rel: str):
        p = base / rel
        if not p.is_file():
            return None
        if rel not in cache:
            cache[rel] = {"sha256": sha256_file(p), "duration": _mp3_duration(p)}
        return cache[rel]
    return probe


# ------------------------------------------------------------
# dev HTML解析(M1: HTMLパーサ。X/Y/Zの現行builder出力の構造契約)
# ------------------------------------------------------------
_KIND_PATTERNS = [
    (r"^Intro$", "sfx"), (r"^Notification \d+$", "sfx"),
    (r"^(Welcome|Preview intro|Key phrases intro|Full story intro|Outro)$", "fixed"),
    (r"^Topic intro$", "topic"), (r"^Japanese title$", "jtitle"), (r"^Preview$", "preview"),
    (r"^Key Phrase \d+$", "kp"), (r"^Comment \d+$", "comment"), (r"^In One Line$", "oneline"),
]
_STORY_PATTERN = {
    "x": r"^Full Story Part \d+$",
    "z": r"^Full Story Part \d+$",
    "y": r"^Full Story: (Lead|Voice \d+ Introduction|Voice \d+|Closing)$",
}
Y_SEG_OF_LABEL = [
    (r"^Full Story: Lead$", lambda m: "y_lead"),
    (r"^Full Story: Voice (\d+) Introduction$", lambda m: f"y_intro_{m.group(1)}"),
    (r"^Full Story: Voice (\d+)$", lambda m: f"y_voice_{m.group(1)}"),
    (r"^Full Story: Closing$", lambda m: "y_closing"),
]
_BADGE_RE = re.compile(r"^\s*TTS ")


def classify_label(label_raw: str, family: str) -> tuple:
    label = re.sub(r"\s*\(.*\)\s*$", "", label_raw.strip())
    for pat, kind in _KIND_PATTERNS:
        if re.match(pat, label):
            return label, kind
    if re.match(_STORY_PATTERN[family], label):
        return label, "story"
    stop("ENDUSER_UNKNOWN_ROW_LABEL", f"未知の行label: {label_raw!r}(family={family})。黙って捨てない")


def _rich_html(node: Node) -> str:
    """学習ブロックdd/ja内の許可markup(p,b,i,strong,em,br。属性なし)を再serializeする。未知tag・属性はSTOP。"""
    out = []
    for c in node.children:
        if isinstance(c, str):
            out.append(_html.escape(c, quote=False))
        elif c.tag in ("p", "b", "i", "strong", "em"):
            if c.attrs:
                D.stop("ENDUSER_UNKNOWN_MARKUP", f"学習ブロック内の<{c.tag}>に属性: {c.attrs}")
            out.append(f"<{c.tag}>{_rich_html(c)}</{c.tag}>")
        elif c.tag == "br":
            out.append("<br>")
        else:
            D.stop("ENDUSER_UNKNOWN_MARKUP", f"学習ブロック内の未知tag <{c.tag}>")
    return "".join(out)


def _parse_kp_table(table: Node) -> tuple:
    header, items = [], []
    for tr in table.find_all("tr"):
        ths = [c for c in tr.elements() if c.tag == "th"]
        tds = [c for c in tr.elements() if c.tag == "td"]
        if ths:
            header = [t.text().strip() for t in ths]
        elif len(tds) in (2, 3):                        # 2列=英語/意味(または英語での解説)、3列=英語/日本語の意味/英語での説明(Z Adv)
            it = {"en": tds[0].text().strip(), "text": tds[1].text().strip()}
            if len(tds) == 3:
                it["text2"] = tds[2].text().strip()
            items.append(it)
        else:
            stop("ENDUSER_DEV_HTML_STRUCTURE", "KP表の行が2列または3列でない")
    if not items or len(header) < 2 or any(len(header) != (3 if "text2" in it else 2) for it in items):
        stop("ENDUSER_DEV_HTML_STRUCTURE", "KP表に見出しまたは項目が無い、または見出しと列数が不一致")
    return header, items


def _merge_marks(marks: list) -> list:
    """文境界で分割された同一下線span(同じdata-hl・lk)を連結して比較できる形にする。"""
    out = []
    for hl, lk, t in marks:
        if out and out[-1][0] == hl and out[-1][1] == lk and hl:
            out[-1] = (hl, lk, out[-1][2] + t)
        else:
            out.append((hl, lk, t))
    return out


def _kp_key(k: dict) -> tuple:
    return (k["en"], k["text"], k.get("text2"))


def _skip_chunk_mark(n: Node) -> bool:
    return n.tag == "span" and ("chunk-mark" in n.classes())


def _parse_row(tr: Node, lv: str, idx: int, family: str) -> dict:
    tds = [c for c in tr.elements() if c.tag == "td"]
    if len(tds) != 3:
        stop("ENDUSER_DEV_HTML_STRUCTURE", f"行のtd数が3でない(level={lv} idx={idx})")
    b = tds[0].find("b")
    label_raw = b.text().strip()
    label, kind = classify_label(label_raw, family)
    jump = tds[0].find("button", cls="jump")
    audio = tds[1].find("audio")
    if jump is None or audio is None or not audio.attrs.get("src"):
        stop("ENDUSER_DEV_HTML_STRUCTURE", f"行にdata-tまたはaudio srcが無い: {label}")
    try:
        data_t = float(jump.attrs["data-t"])
    except (KeyError, ValueError):
        stop("ENDUSER_DEV_HTML_STRUCTURE", f"data-tが数値でない: {label}")
    seg = audio.attrs["src"]
    if seg.startswith(("/", "http", "..")) or ":" in seg or "\\" in seg:
        stop("ENDUSER_DEV_HTML_STRUCTURE", f"audio srcが公開dir内の相対pathでない: {seg}")
    row = {"idx": idx, "key": f"{lv}_{idx:02d}", "label": label, "label_raw": label_raw, "kind": kind, "data_t": data_t, "seg": seg}
    scripts, ja_blocks, meanings, kp = [], [], [], None
    for c in tds[2].elements():
        cl = c.classes()
        if c.tag == "div" and cl == ["script"]:
            scripts.append(c)
        elif c.tag == "div" and cl == ["rpt-notes"]:
            continue                                   # 開発者向け注記(LR赤/Fallback青)。End Userには出さない
        elif c.tag == "div" and not cl and all(e.tag == "span" for e in c.elements()) and _BADGE_RE.match(c.text()):
            continue                                   # 開発者向けTTS分割バッジ
        elif c.tag == "span" and cl == ["sec"]:
            continue
        elif c.tag == "ul" and cl == ["lk-meaning"]:
            meanings = [li.text().strip() for li in c.find_all("li")]
        elif c.tag == "table" and cl == ["kp"]:
            kp = _parse_kp_table(c)
        elif c.tag == "details" and not cl:
            sm = c.find("summary")
            jd = c.find("div", cls="ja")
            if sm is None or jd is None or sm.text().strip() != "日本語の元原稿":
                stop("ENDUSER_UNKNOWN_CELL_CONTENT", f"未知のdetails(label={label})")
            ja_blocks.append(jd.text().strip())
        else:
            stop("ENDUSER_UNKNOWN_CELL_CONTENT", f"行'{label}'に未知の要素 <{c.tag}> class={cl}")
    if kind in R.TEXT_KINDS:
        if not scripts:
            stop("ENDUSER_DEV_HTML_STRUCTURE", f"本文行'{label}'にdiv.scriptが無い")
        row["_scripts"] = scripts
        row["_ref_text"] = _ws("".join(s.text(skip=_skip_chunk_mark) for s in scripts))
        row["_ref_marks"] = _merge_marks([(sp.attrs.get("data-hl", ""), [k for k in sp.classes() if k in D.LK_CLASSES][0], _ws(sp.text()))
                                          for s in scripts for sp in s.find_all(pred=lambda x: x.tag in ("span", "strong") and any(k in D.LK_CLASSES for k in x.classes()))])
        if kind == "story":
            row["meanings"] = meanings
        if ja_blocks:
            row["ja_blocks"] = ja_blocks
    elif kind == "kp":
        if kp is None:
            stop("ENDUSER_DEV_HTML_STRUCTURE", f"KP行'{label}'にtable.kpが無い")
        row["kp_header"], row["kp"] = kp
    return row


def _parse_study_section(sec: Node) -> tuple:
    h3 = sec.find("h3")
    head = h3.text().strip() if h3 is not None else ""
    if head == R.NUANCE_ABOLISHED_HEADING:   # 廃止済みコーナー(見出しh3の構造一致)。旧devページからの再deriveを防ぐ
        stop("ENDUSER_NUANCE_CORNER_ABOLISHED", "devページに廃止済みの『ニュアンス解説』ブロックがあります(2026-10-30廃止)。devページを再生成してから実行してください")
    if head not in R.STUDY_HEADINGS:
        stop("ENDUSER_UNKNOWN_STUDY_HEADING", f"未知の学習ブロック見出し: {head!r}")
    items = []
    for it in sec.find_all("div", cls="study-item"):
        h4 = it.find("h4")
        dl = it.find("dl")
        if dl is None:
            continue
        fields, cur = [], None
        for c in dl.elements():
            if c.tag == "dt":
                cur = c.text().strip()
            elif c.tag == "dd" and cur is not None:
                fields.append({"label": cur, "html": _rich_html(c)})
                cur = None
            else:
                stop("ENDUSER_DEV_HTML_STRUCTURE", "学習ブロックのdl構造が不正")
        items.append({"heading": h4.text().strip() if h4 is not None else None, "fields": fields})
    if not items:
        stop("ENDUSER_EMPTY_STUDY_SECTION", f"空の学習ブロック: {head}(0件コーナーは出力しない契約)")
    return R.STUDY_HEADINGS[head], items


def parse_dev_page(dev_html: str, family: str) -> dict:
    """最終dev index.html -> {'levels': {lv: {'main', 'rows': [...], 'study': {vocab/grammar: items}}}, 'notice', 'h1'}。"""
    family = family.lower()
    if family not in _STORY_PATTERN:
        stop("ENDUSER_FAMILY_UNSUPPORTED", f"family={family}")
    root = parse_html(dev_html)
    body = root.find("body")
    if body is None:
        stop("ENDUSER_DEV_HTML_STRUCTURE", "bodyが無い")
    levels, cur, notice = {}, None, None
    h1 = body.find("h1")
    for n in body.iter():
        if n.tag == "h2":
            cur = R.LEVEL_IDS.get(n.attrs.get("id", ""))
            if cur is not None:
                if cur in levels:
                    stop("ENDUSER_DEV_HTML_STRUCTURE", f"levelが重複: {cur}")
                levels[cur] = {"main": None, "rows": [], "study": {}}
            continue
        if n.tag == "div" and n.has_class("y-ai-notice") and cur is None:
            notice = n.text().strip()
            continue
        if cur is None:
            continue
        L = levels[cur]
        if n.tag == "audio" and n.attrs.get("id", "").startswith("main_"):
            L["main"] = n.attrs.get("src")
        elif n.tag == "tr":
            tds = [c for c in n.elements() if c.tag == "td"]
            if tds and tds[0].elements() and tds[0].elements()[0].tag == "b" and not n.inside("td"):
                L["rows"].append(_parse_row(n, cur, len(L["rows"]), family))
        elif n.tag == "ul" and n.classes() == ["lk-meaning"] and not n.inside("td"):
            # 行の外(level節の台本表の直後)に置かれる③本文中の意味一覧(Yの`highlight_meaning_html`、Xの表示範囲外HL_MEANING_ONLY)。
            L.setdefault("level_meanings", []).extend(li.text().strip() for li in n.find_all("li"))
        elif n.tag == "section" and n.has_class("study"):
            kind, items = _parse_study_section(n)
            if kind in L["study"]:
                stop("ENDUSER_DEV_HTML_STRUCTURE", f"{cur}: 学習ブロック'{kind}'が複数ある")
            L["study"][kind] = items
    if not levels:
        stop("ENDUSER_DEV_HTML_STRUCTURE", "level見出し(h2 id=std|adv|standard|advanced)が無い")
    for lv, L in levels.items():
        if not L["main"] or not L["rows"]:
            stop("ENDUSER_DEV_HTML_STRUCTURE", f"{lv}: 全編audioまたは行が無い")
    return {"levels": levels, "notice": notice, "h1": h1.text().strip() if h1 is not None else "", "family": family}


def _sync_rows_for(lv: str, rows: list, dev_dir) -> list:
    """sentencesを付け、同期module(02A)へ渡す形(row_id,kind,audio_path,sentences + data_t,label,level)へ整える。"""
    sid_n, out = 0, []
    for r in rows:
        o = {"row_id": r["key"], "level": lv, "kind": r["kind"], "label": r["label"], "label_raw": r["label_raw"], "data_t": r["data_t"],
             "audio_rel": r["seg"], "audio_path": str(Path(dev_dir) / r["seg"]) if dev_dir else r["seg"], "sentences": []}
        if "_scripts" in r:
            paras, sid_n = D.paragraphs_of_divs(r["_scripts"], sid_n, r["key"])
            r["paragraphs"] = paras
            o["paragraphs"] = paras
            o["sentences"] = [{"sid": s["sid"], "text": s["text"]} for pa in paras for s in pa]
        for k in ("meanings", "kp_header", "ja_blocks", "_ref_text", "_ref_marks"):
            if k in r:
                o[k] = r[k]
        if "kp" in r:
            o["kp_table"] = r["kp"]                                        # 表示用のKP表(英語/意味/英語での説明)
            o["kp"] = {"expressions": [k["en"] for k in r["kp"]]}          # 同期module(02A)への入力形
        out.append(o)
    return out


def build_rows_from_dev_html(dev_index_html: str, run_ctx: dict) -> tuple:
    """最終dev index.html -> (rows_by_level, study_by_level, meta)。
    rows_by_level[lv] = [{row_id, kind, audio_path, sentences:[{sid,text}], ...}](同期module用に必要な4キー+表示用の追加キー)。X/Y/Z共通。"""
    family = str(run_ctx["family"]).lower()
    dev_dir = run_ctx.get("dev_dir")
    dev_index_html = dev_index_html.replace("\r\n", "\n")      # 改行はLFへ正規化(Windows生成/checkoutのCRLFが本文textに混ざらない)
    parsed = parse_dev_page(dev_index_html, family)
    rows_by_level, study_by_level = {}, {}
    for lv, L in parsed["levels"].items():
        rows_by_level[lv] = _sync_rows_for(lv, L["rows"], dev_dir)
        study_by_level[lv] = L["study"]
    title_ja, topic_en = None, ""
    for lv in ("std", "adv"):
        for r in rows_by_level.get(lv, []):
            if r["kind"] == "jtitle" and title_ja is None:
                title_ja = "".join(s["text"] for s in r["sentences"]).strip()
            if r["kind"] == "topic" and not topic_en:
                topic_en = re.sub(r"^Today's topic is\s*", "", " ".join(s["text"] for s in r["sentences"]).strip())
    title_ja = title_ja or re.sub(r"\s*試聴.*$", "", parsed["h1"]).strip()
    if not title_ja:
        stop("ENDUSER_DEV_HTML_STRUCTURE", "日本語タイトルを特定できない")
    meta = {
        "id": run_ctx.get("id") or (Path(dev_dir).name if dev_dir else "article"),
        "family": family.upper(), "title_ja": title_ja, "topic_en": topic_en, "notice": parsed["notice"],
        "level_main": {lv: L["main"] for lv, L in parsed["levels"].items()},
        "level_meanings": {lv: L.get("level_meanings", []) for lv, L in parsed["levels"].items()},
        "dev_index_sha256": run_ctx.get("dev_index_sha256") or sha256_bytes(dev_index_html.encode("utf-8")),
    }
    return rows_by_level, study_by_level, meta


TIMELINE_CANDIDATES = ("{sub}/audit/timeline.json", "{sub}/assembly/timeline.json")


def load_timeline(run_dir, sub: str):
    for pat in TIMELINE_CANDIDATES:
        p = Path(run_dir) / pat.format(sub=sub)
        if p.is_file():
            d = json.load(open(p, encoding="utf-8"))
            tl = d["timeline"] if isinstance(d, dict) else d
            return [x for x in tl if not str(x.get("part", "")).startswith(("pause_", "_silence"))], str(p)
    return None, None


def match_rows_to_timeline(lv: str, rows: list, tl: list, strict_count: bool) -> dict:
    """dev行のdata-tとtimeline項目(start_seconds)を順序どおり照合(<=0.01秒)。不一致はSTOP。"""
    if strict_count and len(tl) != len(rows):
        stop("ENDUSER_TIMELINE_MISMATCH", f"{lv}: 行数 dev={len(rows)} timeline={len(tl)}")
    k = 0
    for r in rows:
        while k < len(tl) and abs(tl[k]["start_seconds"] - r["data_t"]) > 0.01:
            k += 1
        if k >= len(tl):
            stop("ENDUSER_TIMELINE_MISMATCH", f"{lv}: dev行'{r['label_raw']}'(data-t={r['data_t']})に開始時刻が一致するtimeline項目が無い(順序どおり)")
        k += 1
    return {"checked": True, "rows": len(rows), "timeline_entries": len(tl)}


def check_against_timeline(rows_by_level: dict, run_dir, strict_count_families=("X",), family: str = "") -> dict:
    """中間データ照合(M1): `<run>/<a2|b1b>/{audit|assembly}/timeline.json`(pause/_silenceを除く)の開始時刻とdev行のdata-tを順序どおり突き合わせる
    (labelはZでFamily別に表記が違うため時刻で照合)。X(行==timeline)は行数も一致を要求。見つからないlevelはskip(結果に記録)。不一致はSTOP。"""
    res = {}
    for lv, sub in (("std", "a2"), ("adv", "b1b")):
        if lv not in rows_by_level:
            continue
        tl, _path = load_timeline(run_dir, sub) if run_dir else (None, None)
        if tl is None:
            res[lv] = {"checked": False, "reason": "timeline.json not found"}
            continue
        res[lv] = match_rows_to_timeline(lv, rows_by_level[lv], tl, family.upper() in strict_count_families)
    return res


# ------------------------------------------------------------
# KP英語のみ区間(M-KP: ブロック数>=4で2番目。ASR転写で一致確認。不一致・3ブロック以下はSTOP)
# ------------------------------------------------------------
def speech_blocks(path, d=0.2, noise="-40dB") -> list:
    o = subprocess.run([_ffmpeg(), "-hide_banner", "-i", str(path), "-af", f"silencedetect=noise={noise}:d={d}", "-f", "null", "-"],
                       capture_output=True, text=True, errors="replace").stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", o)
    if not m:
        stop("ENDUSER_AUDIO_UNREADABLE", f"{path}")
    dur = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
    sil, st = [], None
    for mm in re.finditer(r"silence_(start|end): ([\d.]+)", o):
        if mm[1] == "start":
            st = float(mm[2])
        elif st is not None:
            sil.append((st, float(mm[2])))
    sp, t = [], 0.0
    for s, e in sil:
        if s > t + 0.02:
            sp.append((t, s))
        t = e
    if dur > t + 0.02:
        sp.append((t, dur))
    return [b for b in sp if b[1] - b[0] >= 0.25]


_PLACEHOLDER = {"one's", "someone's", "somebody's", "sb's", "one", "someone", "somebody", "something", "sth", "sb", "oneself"}


def _kp_tokens(s: str) -> list:
    return [t.replace("’", "'") for t in re.findall(r"[a-z0-9]+(?:['’][a-z]+)?", (s or "").lower())]


def kp_asr_matches(expected: str, heard: str) -> bool:
    exp = [t for t in _kp_tokens(expected) if t not in _PLACEHOLDER]
    got = _kp_tokens(heard)
    if not exp:
        return bool(got)
    if all(t in got for t in exp):
        return True
    return difflib.SequenceMatcher(None, " ".join(exp), " ".join(got)).ratio() >= 0.85


def _default_asr(path, start, end) -> str:
    """既定ASR: faster-whisper medium int8 CPU(ローカル・API 0)。KP区間だけを転写する。"""
    import numpy as np
    from faster_whisper import WhisperModel
    global _WHISPER
    try:
        _WHISPER
    except NameError:
        _WHISPER = WhisperModel("medium", device="cpu", compute_type="int8")
    raw = subprocess.run([_ffmpeg(), "-v", "error", "-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", str(path), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True).stdout
    audio = np.frombuffer(raw, dtype=np.float32)
    segs, _ = _WHISPER.transcribe(audio, language="en", beam_size=5, condition_on_previous_text=False, vad_filter=False)
    return " ".join(s.text.strip() for s in segs)


def compute_kp_audio(rows_by_level: dict, dev_dir, asr=None, blocks_fn=None) -> dict:
    """KP clipごとの英語区間 {row_id: {start,end,blocks,asr_text}}。asr(path,start,end)->str を注入可(testはfake)。"""
    asr = asr or _default_asr
    blocks_fn = blocks_fn or speech_blocks
    out = {}
    for lv, rows in rows_by_level.items():
        for r in rows:
            if r["kind"] != "kp":
                continue
            p = Path(dev_dir) / r["audio_rel"]
            b = blocks_fn(p)
            if len(b) < 4:
                stop("ENDUSER_KP_BLOCKS", f"{r['row_id']}: 発話ブロック{len(b)}(<4)。KP音声の構成[番号,英語,意味/解説,英語再掲]を満たさない")
            s, e = b[1]
            s2, e2 = round(max(0.0, s - 0.08), 3), round(e + 0.15, 3)
            heard = asr(p, s2, e2)
            for k in r["kp_table"]:
                if not kp_asr_matches(k["en"], heard):
                    stop("ENDUSER_KP_ASR_MISMATCH", f"{r['row_id']}: KP='{k['en']}' ASR='{heard}'(区間{s2}-{e2})")
            out[r["row_id"]] = {"start": s2, "end": e2, "method": KP_METHOD, "blocks": len(b), "asr_text": heard.strip()}
    return out


# ------------------------------------------------------------
# 同期json(`enduser_sync_v1`=02A出力)の受け入れ検査
# ------------------------------------------------------------
SYNC_TIME_BASES = ("row_local_seconds", "episode_seconds")


def rows_for_sync(rows: list) -> list:
    """同期module(02A `er135_enduser_sync_01.sync_level`)へ渡す行。本文行(sentencesあり)とKP行のみ(音声だけの行は渡さない)。"""
    keys = ("row_id", "kind", "audio_path", "sentences", "kp")
    return [{k: r[k] for k in keys if k in r} for r in rows if r["sentences"] or r["kind"] == "kp"]


def check_sync(lv: str, rows: list, sync: dict, probe) -> dict:
    """02Aの`enduser_sync_v1`(model/params/rows[{row_id,mp3_sha256,sentences[{sid,text,start,end}],kp_en?}]/gate.status。時刻は
    params.time_base=row_local_seconds=各行mp3内の秒)を検査し、全編内の秒へ換算した {sid:(start,end)} とprovenanceを返す。違反は`ENDUSER_SYNC_*`でSTOP。"""
    if not isinstance(sync, dict) or sync.get("schema") != R.SCHEMA_SYNC_IN:
        stop("ENDUSER_SYNC_SCHEMA", f"{lv}: schema!={R.SCHEMA_SYNC_IN}")
    params, model = sync.get("params"), sync.get("model")
    for k, v in list(sync.items()) + list((params or {}).items() if isinstance(params, dict) else []):
        if k in ("rows", "gate", "params", "cost"):
            continue
        if isinstance(v, str) and re.search(r"dummy|proportional|placeholder", v, re.I):
            stop("ENDUSER_SYNC_DUMMY", f"{lv}: {k}='{v}'(ダミー同期)")
    if not isinstance(params, dict) or "whisper" not in str(params.get("engine", "")).lower() or not str(model or "").strip():
        stop("ENDUSER_SYNC_PROVENANCE", f"{lv}: ASR由来の記録(model, params.engine=faster-whisper)が無い")
    base = params.get("time_base")
    if base not in SYNC_TIME_BASES:
        stop("ENDUSER_SYNC_SCHEMA", f"{lv}: params.time_base={base!r}(想定: {SYNC_TIME_BASES})")
    gate = sync.get("gate")
    if not isinstance(gate, dict) or gate.get("status") != "PASS":
        stop("ENDUSER_SYNC_GATE", f"{lv}: gate.status={gate.get('status') if isinstance(gate, dict) else gate}")
    cost = sync.get("cost") or {}
    if cost.get("api_calls", 0) != 0:
        stop("ENDUSER_COST", f"{lv}: 同期のapi_calls={cost.get('api_calls')}")
    srows = sync.get("rows")
    if not isinstance(srows, list):
        stop("ENDUSER_SYNC_SCHEMA", f"{lv}: rowsが無い")
    by_id = {}
    for sr in srows:
        if not isinstance(sr, dict) or "row_id" not in sr or sr["row_id"] in by_id:
            stop("ENDUSER_SYNC_SCHEMA", f"{lv}: row_idが欠落または重複")
        by_id[sr["row_id"]] = sr
    text_rows = [r for r in rows if r["sentences"]]
    kp_rows = [r for r in rows if r["kind"] == "kp"]
    tids, kids = {r["row_id"] for r in text_rows}, {r["row_id"] for r in kp_rows}
    if not (tids <= set(by_id) <= (tids | kids)):
        stop("ENDUSER_SYNC_COVERAGE", f"{lv}: syncのrow集合が本文行+KP行と不一致 extra={sorted(set(by_id) - tids - kids)} missing={sorted(tids - set(by_id))}")
    times, kp_en, prev_end = {}, {}, -1.0
    for r in rows:
        sr = by_id.get(r["row_id"])
        if sr is None:
            continue
        pr = probe(r["audio_rel"])
        if pr is None:
            stop("ENDUSER_AUDIO_MISSING", f"{r['row_id']}: {r['audio_rel']}")
        if sr.get("mp3_sha256") != pr["sha256"]:
            stop("ENDUSER_SYNC_PROVENANCE", f"{r['row_id']}: syncのmp3_sha256が実mp3と不一致(古い/別音声のsync)")
        off = r["data_t"] if base == "row_local_seconds" else 0.0
        if r["kind"] == "kp":
            ke = sr.get("kp_en")
            ok = isinstance(ke, dict) and all(isinstance(ke.get(x), (int, float)) and math.isfinite(ke[x]) for x in ("start", "end")) and isinstance(ke.get("blocks"), int)
            if not ok or not (0 <= ke["start"] < ke["end"] <= pr["duration"] + TIME_TOL) or ke["blocks"] < 4:
                stop("ENDUSER_SYNC_RANGE", f"{r['row_id']}: kp_enが不正(範囲0..{pr['duration']}・blocks>=4) {ke}")
            kp_en[r["row_id"]] = {"start": round(float(ke["start"]), 3), "end": round(float(ke["end"]), 3), "blocks": ke["blocks"],
                                  "method": "enduser_sync kp_en: " + str(ke.get("source")), **({"token_match": ke["token_match"]} if isinstance(ke.get("token_match"), (int, float)) else {})}
            continue
        ss = sr.get("sentences")
        if not isinstance(ss, list) or [s.get("sid") for s in ss] != [s["sid"] for s in r["sentences"]]:
            stop("ENDUSER_SYNC_COVERAGE", f"{r['row_id']}: sidの集合/順序がdev本文と不一致")
        lo, hi = (0.0, pr["duration"] + TIME_TOL) if base == "row_local_seconds" else (r["data_t"] - TIME_TOL, r["data_t"] + pr["duration"] + TIME_TOL)
        first = True
        for s in ss:
            a, b = s.get("start"), s.get("end")
            if not all(isinstance(x, (int, float)) and math.isfinite(x) for x in (a, b)) or not (0 <= a < b):
                stop("ENDUSER_SYNC_RANGE", f"{s.get('sid')}: start/end不正 {a},{b}")
            if a < lo or b > hi:
                stop("ENDUSER_SYNC_RANGE", f"{s['sid']}: [{a},{b}]が行の範囲[{lo:.3f},{hi:.3f}]({base})外")
            A, B = off + a, off + b
            if A < prev_end - (TIME_TOL if first else 1e-6):
                stop("ENDUSER_SYNC_MONOTONIC", f"{s['sid']}: 前の文と重なる/逆行 start={A:.3f} prev_end={prev_end:.3f}")
            first = False
            prev_end = B
            times[s["sid"]] = (round(A, 3), round(B, 3))
    tm = (gate.get("token_match") or {}) if isinstance(gate, dict) else {}
    return {"times": times, "kp_en": kp_en, "model": str(model), "engine": str(params["engine"]), "params": params, "gate_status": gate["status"],
            "source_sha256": canon_sha(sync), "rows": len(text_rows), "sentences": len(times), "cost": cost,
            "min_row_ratio": tm.get("min_row_ratio") if isinstance(tm.get("min_row_ratio"), (int, float)) else None,
            "low_conf_rows": len((gate.get("warnings") or [])) if isinstance(gate.get("warnings"), list) else 0}


# ------------------------------------------------------------
# 日本語訳(承認済みのみ。Opus M-JA)
# ------------------------------------------------------------
def load_x_manuscript(path) -> dict | None:
    """X: 承認済み日本語原稿(ja_writer/revision2.md 等)。先頭=日本語タイトル段落を除いた段落listを返す。無ければNone(訳なし=非表示)。"""
    if not path or not Path(path).is_file():
        return None
    txt = Path(path).read_text(encoding="utf-8").strip()
    paras = [x.strip() for x in re.split(r"\n\s*\n", txt) if x.strip()]
    return {"paragraphs": paras[1:], "title": paras[0] if paras else "", "sha256": sha256_file(path), "name": Path(path).name}


def _y_segment_id(label: str):
    for pat, fn in Y_SEG_OF_LABEL:
        m = re.match(pat, label)
        if m:
            return fn(m)
    return None


def attach_translations(lv: str, parts: list, family: str, ja: dict | None) -> dict:
    """story行へ承認済み訳のみ付与。返り値=translation_coverage(種別ごと{blocks,translated,source})。"""
    ja = ja or {}
    manus = ja.get("x_manuscript")
    stories = [p for p in parts if p["kind"] == "story" and not p.get("ja_blocks")]
    if manus and family == "x":
        need = sum(len(p["paragraphs"]) for p in stories)
        if need != len(manus["paragraphs"]):
            stop("ENDUSER_JA_PARAGRAPH_MISMATCH", f"{lv}: story段落数={need} 日本語原稿段落数={len(manus['paragraphs'])}(承認済み2成果物の不整合。黙って落とさない)")
        k = 0
        for p in stories:
            n = len(p["paragraphs"])
            p["ja"], p["ja_source"] = manus["paragraphs"][k:k + n], "approved_ja_manuscript"
            k += n
    ysegs = ja.get("y_segments")
    for p in parts:
        blocks = p.pop("ja_blocks", None)
        if blocks:
            if p["kind"] != "story":
                stop("ENDUSER_JA_SOURCE_INVALID", f"{p['label']}: story以外に日本語の元原稿がある")
            paras = [x.strip() for x in re.split(r"\n\s*\n", "\n\n".join(blocks)) if x.strip()]
            if ysegs is not None:
                sid = _y_segment_id(p["label"])
                if sid is None or sid not in ysegs or _ws(ysegs[sid]) != _ws("".join(paras)):
                    stop("ENDUSER_JA_MISMATCH", f"{p['label']}: dev ページの日本語の元原稿が承認済み原稿(split_y_article)と不一致")
            p["ja"], p["ja_source"] = paras, "approved_ja_original_in_dev_page"
    cov = {}
    for p in parts:
        if p["kind"] not in ("story", "comment", "oneline", "preview", "topic"):
            continue
        en = not _has_ja("".join(s["text"] for pa in p["paragraphs"] for s in pa))
        if not en:
            continue                                    # 日本語本文=訳不要
        c = cov.setdefault(p["kind"], {"blocks": 0, "translated": 0, "source": None})
        c["blocks"] += 1
        if p.get("ja"):
            c["translated"] += 1
            c["source"] = p["ja_source"]
    for c in cov.values():
        if c["source"] is None:
            c["source"] = "none_approved_translation_hidden"
    return cov


# ------------------------------------------------------------
# 「覚えておきたい表現」(glossary): display_spec付きlevel(本文にlk1/lk2/lk3 spanあり)のみ。assertは必須(違反=STOP)
# ------------------------------------------------------------
def _plain_html(h: str) -> str:
    return parse_html(h).text()


def _norm_en(s: str) -> str:
    return re.sub(r"^(the|a|an)\s+", "", s.lower().strip())


_POSS_TOKENS = frozenset({"my", "your", "his", "her", "our", "their", "its", "one's", "one’s", "someone's", "someone’s", "somebody's", "somebody’s"})


def _gl_stem(t: str) -> str:
    if t in _POSS_TOKENS:
        return "<p>"
    return re.sub(r"(ing|ed|es|s|e)$", "", t) if len(t) > 3 else t


def _gl_score(a: str, b: str) -> float:
    """下線(本文の語形)と『本文中の意味』一覧の見出し語の対応度。文字列比と、語形・人称(my/one's)の違いを吸収した語幹列比の大きい方
    (例: let my son go<->let one's son go / giving something up<->give something up / adjusting<->adjust)。"""
    char = difflib.SequenceMatcher(None, _norm_en(a), _norm_en(b)).ratio()
    ta = [_gl_stem(t) for t in re.findall(r"[\w'’]+", _norm_en(a))]
    tb = [_gl_stem(t) for t in re.findall(r"[\w'’]+", _norm_en(b))]
    tok = difflib.SequenceMatcher(None, ta, tb).ratio() if ta and tb else 0.0
    return max(char, tok)


def build_glossary(lv: str, parts: list, vocab: list, level_meanings: list | None = None) -> str:
    """glossaryを各story/oneline行へ付与。戻り値='applied'|'not_applicable_no_display_spec'。
    level_meanings=行の外(level節の台本表の直後)にある③本文中の意味一覧。行内の一覧に無い下線(lk3)はこの共有poolから1回だけ対応づける。poolに未使用が残ればSTOP。"""
    have_lk = False
    for p in parts:
        if p["kind"] in ("story", "oneline"):
            for pa in p["paragraphs"]:
                for s in pa:
                    if D.lk_spans(s["html"]):
                        have_lk = True
    if not have_lk:
        return "not_applicable_no_display_spec"
    quotes, means = [], []
    for v in vocab:
        f = {x["label"]: x["html"] for x in v["fields"]}
        quotes.append(_plain_html(f.get("本文の英文", "")).lower())
        means.append(_plain_html(f.get("本文中の意味", "")).strip())
    seen, used_v = set(), set()
    pool = []
    for w in (level_meanings or []):
        if "＝" not in w:
            stop("ENDUSER_GLOSSARY_ASSERT", f"{lv}: 本文中の意味(level一覧)の書式が'英語＝意味'でない: {w!r}")
        a, b = w.split("＝", 1)
        pool.append((a.strip(), b.strip()))
    used_pool = set()
    for p in parts:
        p.pop("glossary", None)
        if p["kind"] not in ("story", "oneline"):
            continue
        spans = []
        for pa in p["paragraphs"]:
            for s in pa:
                spans.extend(D.lk_spans(s["html"]))
        lk3 = []
        for w in p.get("meanings", []):
            if "＝" not in w:
                stop("ENDUSER_GLOSSARY_ASSERT", f"{lv} {p['label']}: 本文中の意味の書式が'英語＝意味'でない: {w!r}")
            a, b = w.split("＝", 1)
            lk3.append((a.strip(), b.strip()))
        used_m, ents = set(), []
        for key, lk, txt in spans:
            if key in seen:
                continue
            txt = txt.strip()
            if lk in ("lk1", "lk2"):
                cand = [i for i, q in enumerate(quotes) if txt.lower() in q]
                if not cand:
                    stop("ENDUSER_GLOSSARY_ASSERT", f"{lv} {p['label']}: 下線対象'{txt}'に対応するVocabularyが無い")
                # 本文の英文に下線語を含むVocabularyが複数あるとき(例: 'bandit'はconstableの例文にも現れる)は、見出し語が下線語に対応する項目を優先する
                # (先頭候補固定だと藪の中Std『bandit』のVocabularyが一覧に載らずSTOPした=FZLR委任_07)。見出し一致が無ければ従来どおり先頭候補。
                i = min(cand, key=lambda c: (0 if _gl_score(txt, vocab[c]["heading"]) >= 0.8 else 1, c in used_v, c))
                ents.append({"key": key, "lk": lk, "en": vocab[i]["heading"], "ja": means[i], "vi": i, "form": txt})
                used_v.add(i)
            else:
                best, bi = 0.0, None
                for j, (e, _jm) in enumerate(lk3):
                    r = _gl_score(txt, e)
                    if r > best:
                        best, bi = r, j
                src = lk3
                if (best < 0.8 or bi in used_m) and pool:       # 行内の一覧に無ければlevel一覧(共有pool)から1回だけ
                    pbest, pj = 0.0, None
                    for j, (e, _jm) in enumerate(pool):
                        if j in used_pool:
                            continue
                        r = _gl_score(txt, e)
                        if r > pbest:
                            pbest, pj = r, j
                    if pbest >= 0.8:
                        src, best, bi = pool, pbest, pj
                        used_pool.add(pj)
                if best < 0.8 or (src is lk3 and bi in used_m):
                    stop("ENDUSER_GLOSSARY_ASSERT", f"{lv} {p['label']}: 下線'{txt}'が本文中の意味一覧に一意に対応しない(best={best:.2f})")
                if src is lk3:
                    used_m.add(bi)
                e0 = src[bi][0]
                ents.append({"key": key, "lk": lk, "en": (e0[:1].lower() + e0[1:]) if txt[:1].islower() else e0, "ja": src[bi][1], "vi": None, "form": txt})
            seen.add(key)
        if used_m != set(range(len(lk3))):
            stop("ENDUSER_GLOSSARY_ASSERT", f"{lv} {p['label']}: 本文中の意味{len(lk3)}件のうち未使用あり")
        if ents:
            p["glossary"] = [{"en": e["en"], "ja": e["ja"], "vi": e["vi"]} for e in ents]
    if used_pool != set(range(len(pool))):
        stop("ENDUSER_GLOSSARY_ASSERT", f"{lv}: level一覧の本文中の意味{len(pool)}件のうち、下線に対応しない項目あり({sorted(set(range(len(pool))) - used_pool)})")
    if used_v != set(range(len(vocab))):
        stop("ENDUSER_GLOSSARY_ASSERT", f"{lv}: Vocabulary{len(vocab)}件のうち一覧に載らない項目あり({sorted(set(range(len(vocab))) - used_v)})")
    glos = [g["en"] for p in parts for g in p.get("glossary", [])]
    kp_heads = [k["en"] for p in parts if p["kind"] == "kp" for k in p["kp"]]
    for h in kp_heads:
        if h not in glos:
            stop("ENDUSER_GLOSSARY_ASSERT", f"{lv}: Key Phrase '{h}'が一覧に載らない")
    if len(glos) != len(set(glos)):
        stop("ENDUSER_GLOSSARY_ASSERT", f"{lv}: 一覧に重複あり")
    return "applied"


# ------------------------------------------------------------
# End Userデータの組立
# ------------------------------------------------------------
def build_enduser_data(rows_by_level: dict, sync_by_level: dict, study_by_level: dict, ja: dict | None, meta: dict, *,
                       kp_audio: dict | None = None, probe=None, extra_build_info: dict | None = None) -> tuple:
    """(article, sync_public_by_level, build_info)を返す。検査(sync受入・glossary assert・validate_output)をすべて通ったときだけ返る。"""
    if probe is None:
        stop("ENDUSER_PROBE_MISSING", "probe(音声sha/長さ)が必要")
    family = meta["family"].lower()
    kp_audio = kp_audio or {}
    levels, sync_public, sync_info, trans_cov, gloss_info, sync_cost = {}, {}, {}, {}, {}, {}
    audio_sha: dict = {}
    for lv, rows in rows_by_level.items():
        if lv not in sync_by_level:
            stop("ENDUSER_SYNC_COVERAGE", f"{lv}: 同期jsonが渡されていない")
        si = check_sync(lv, rows, sync_by_level[lv], probe)
        main = meta["level_main"][lv]
        pm = probe(main)
        if pm is None:
            stop("ENDUSER_AUDIO_MISSING", f"{lv}: {main}")
        audio_sha[main] = pm["sha256"]
        parts, sent_n = [], 0
        for r in rows:
            pr = probe(r["audio_rel"])
            if pr is None:
                stop("ENDUSER_AUDIO_MISSING", f"{r['row_id']}: {r['audio_rel']}")
            audio_sha[r["audio_rel"]] = pr["sha256"]
            p = {"idx": r["idx"] if "idx" in r else len(parts), "key": r["row_id"], "label": r["label"], "kind": r["kind"],
                 "start": round(r["data_t"], 3), "dur": pr["duration"], "seg": r["audio_rel"]}
            if "paragraphs" in r:
                p["paragraphs"] = r["paragraphs"]
                sent_n += len(r["sentences"])
            if r["kind"] == "story":
                p["meanings"] = r.get("meanings", [])
            if r["kind"] == "kp":
                p["kp_header"] = r["kp_header"]
                ka = si["kp_en"].get(r["row_id"]) or kp_audio.get(r["row_id"])      # 同期moduleのkp_en(優先)、無ければcompute_kp_audioの結果
                if ka is None:
                    stop("ENDUSER_KP_AUDIO_MISSING", f"{r['row_id']}: KP英語区間が算出されていない")
                ea = {kk: ka[kk] for kk in ("start", "end", "method", "blocks", "asr_text", "token_match") if kk in ka}
                p["kp"] = [{**{kk: k[kk] for kk in ("en", "text", "text2") if kk in k}, "en_audio": dict(ea)} for k in r["kp_table"]]
            if r.get("ja_blocks"):
                p["ja_blocks"] = r["ja_blocks"]
            parts.append(p)
        for i, p in enumerate(parts):
            p["idx"] = i
        trans_cov[lv] = attach_translations(lv, parts, family, ja)
        study = study_by_level.get(lv, {})
        vocab, grammar = study.get("vocab", []), study.get("grammar", [])
        gloss_info[lv] = build_glossary(lv, parts, vocab, (meta.get("level_meanings") or {}).get(lv))
        levels[lv] = {"level": lv, "main": main, "parts": parts, "vocab": vocab, "grammar": grammar,
                      "total_sec": pm["duration"], "sentence_count": sent_n}
        sync_public[lv] = {"schema": R.SCHEMA_SYNC_PUBLIC, "level": lv,
                           "sentences": sorted(({"sid": sid, "start": a, "end": b} for sid, (a, b) in si["times"].items()), key=lambda x: x["start"])}
        sync_info[lv] = {k: si[k] for k in ("engine", "model", "params", "gate_status", "source_sha256", "rows", "sentences", "min_row_ratio", "low_conf_rows")}
        sync_cost[lv] = si["cost"]
    article = {"schema": R.SCHEMA_ARTICLE, "id": meta["id"], "family": meta["family"], "title_ja": meta["title_ja"], "topic_en": meta["topic_en"],
               "notice": meta["notice"], "audio_base": "../", "levels": levels}
    build_info = {
        "schema": R.SCHEMA_BUILD_INFO, "id": meta["id"], "family": meta["family"], "asset_build": R.ASSET_BUILD_ID,
        "dev_index_sha256": meta["dev_index_sha256"], "audio_sha256": dict(sorted(audio_sha.items())),
        "assets": {}, "files": {}, "sync": sync_info, "translation_coverage": trans_cov, "glossary": gloss_info,
        "ja_manuscript": ({"name": ja["x_manuscript"]["name"], "sha256": ja["x_manuscript"]["sha256"]} if ja and ja.get("x_manuscript") else None),
        "warnings": [f"{lv}: 低信頼度境界を持つ行 {v['low_conf_rows']}件(記録のみ)" for lv, v in sync_info.items() if v["low_conf_rows"]],
        "cost": {"api_calls": 0, "model": next(iter(sync_info.values()))["model"] if sync_info else "",
                 "asr_wall_s": round(sum(float(c.get("wall_s", 0) or 0) for c in sync_cost.values()), 1), "build_wall_s": 0.0,
                 "cached_segments": int(sum(int(c.get("cached_segments", 0) or 0) for c in sync_cost.values()))},
    }
    if extra_build_info:
        for k, v in extra_build_info.items():
            if k == "cost":
                build_info["cost"].update(v)
            elif k == "warnings":
                build_info["warnings"].extend(v)
            else:
                build_info[k] = v
    validate_output(article, sync_public, build_info, rows_by_level, study_by_level, meta, probe=probe)
    return article, sync_public, build_info


# ------------------------------------------------------------
# schema(additionalProperties=false。jsonschema非依存の最小実装)とvalidator(M5/M-VAL)
# ------------------------------------------------------------
def _t(**kw):
    return kw


S_STR, S_INT, S_NUM, S_BOOL = _t(type="string"), _t(type="integer"), _t(type="number"), _t(type="boolean")
S_STR_OR_NULL = _t(type=["string", "null"])


def _obj(props: dict, required=None):
    return {"type": "object", "properties": props, "required": list(props if required is None else required), "additionalProperties": False}


def _arr(items):
    return {"type": "array", "items": items}


_S_SENT = _obj({"sid": S_STR, "html": S_STR, "text": S_STR})
_S_FIELD = _obj({"label": S_STR, "html": S_STR})
_S_ITEM = _obj({"heading": S_STR_OR_NULL, "fields": _arr(_S_FIELD)})
_S_PART = _obj({
    "idx": S_INT, "key": S_STR, "label": S_STR, "kind": {"type": "string", "enum": ["sfx", "fixed", "topic", "jtitle", "preview", "kp", "comment", "story", "oneline"]},
    "start": S_NUM, "dur": S_NUM, "seg": S_STR,
    "paragraphs": _arr(_arr(_S_SENT)), "meanings": _arr(S_STR), "glossary": _arr(_obj({"en": S_STR, "ja": S_STR, "vi": _t(type=["integer", "null"])})),
    "ja": _arr(S_STR), "ja_source": {"type": "string", "enum": list(R.JA_SOURCES)},
    "kp_header": _arr(S_STR),
    "kp": _arr(_obj({"en": S_STR, "text": S_STR, "text2": S_STR, "en_audio": _obj({"start": S_NUM, "end": S_NUM, "method": S_STR, "blocks": S_INT, "asr_text": S_STR, "token_match": S_NUM}, required=["start", "end", "method", "blocks"])}, required=["en", "text", "en_audio"])),
}, required=["idx", "key", "label", "kind", "start", "dur", "seg"])
# `nuance`は廃止(2026-10-30)=新規出力にキー無し。公開済みスナップショットの`nuance: []`は読取互換(任意キー)。中身ありはvalidate_outputがENDUSER_NUANCE_CORNER_ABOLISHEDでSTOP
_S_LEVEL = _obj({"level": {"type": "string", "enum": ["std", "adv"]}, "main": S_STR, "parts": _arr(_S_PART), "vocab": _arr(_S_ITEM), "grammar": _arr(_S_ITEM),
                 "nuance": _arr(_S_ITEM), "total_sec": S_NUM, "sentence_count": S_INT}, required=["level", "main", "parts", "vocab", "grammar", "total_sec", "sentence_count"])
SCHEMA_ARTICLE_SPEC = _obj({
    "schema": {"type": "string", "enum": [R.SCHEMA_ARTICLE]}, "id": S_STR, "family": {"type": "string", "enum": ["X", "Y", "Z"]},
    "title_ja": S_STR, "topic_en": S_STR, "notice": S_STR_OR_NULL, "audio_base": {"type": "string", "enum": ["../"]},
    "levels": {"type": "object", "properties": {"std": _S_LEVEL, "adv": _S_LEVEL}, "required": [], "additionalProperties": False},
})
SCHEMA_SYNC_SPEC = _obj({"schema": {"type": "string", "enum": [R.SCHEMA_SYNC_PUBLIC]}, "level": {"type": "string", "enum": ["std", "adv"]},
                         "sentences": _arr(_obj({"sid": S_STR, "start": S_NUM, "end": S_NUM}))})
_S_COV = _obj({"blocks": S_INT, "translated": S_INT, "source": S_STR})
SCHEMA_BUILD_INFO_SPEC = _obj({
    "schema": {"type": "string", "enum": [R.SCHEMA_BUILD_INFO]}, "id": S_STR, "family": S_STR, "asset_build": S_STR, "dev_index_sha256": S_STR,
    "audio_sha256": {"type": "object", "additionalProperties": S_STR}, "assets": {"type": "object", "additionalProperties": S_STR},
    "files": {"type": "object", "additionalProperties": S_STR},
    "sync": {"type": "object", "additionalProperties": _obj({"engine": S_STR, "model": S_STR, "params": {"type": "object"}, "gate_status": S_STR, "source_sha256": S_STR, "rows": S_INT, "sentences": S_INT,
                                                                 "min_row_ratio": _t(type=["number", "null"]), "low_conf_rows": S_INT})},
    "translation_coverage": {"type": "object", "additionalProperties": {"type": "object", "additionalProperties": _S_COV}},
    "glossary": {"type": "object", "additionalProperties": S_STR},
    "ja_manuscript": _t(type=["object", "null"], properties={"name": S_STR, "sha256": S_STR}, required=["name", "sha256"], additionalProperties=False),
    "warnings": _arr(S_STR),
    "cost": _obj({"api_calls": S_INT, "model": S_STR, "asr_wall_s": S_NUM, "build_wall_s": S_NUM, "cached_segments": S_INT}),
    "timeline_check": {"type": "object"},
    "episode_check": {"type": "object"},
}, required=["schema", "id", "family", "asset_build", "dev_index_sha256", "audio_sha256", "assets", "files", "sync", "translation_coverage", "glossary", "ja_manuscript", "warnings", "cost"])

_TYPE_MAP = {"string": str, "integer": int, "number": (int, float), "boolean": bool, "array": list, "object": dict, "null": type(None)}


def check_schema(obj, spec, path="$") -> None:
    """違反は`ENDUSER_SCHEMA`でSTOP(未知key・欠落key・型・enum)。"""
    t = spec.get("type")
    if t is not None:
        ts = t if isinstance(t, list) else [t]
        ok = False
        for x in ts:
            py = _TYPE_MAP[x]
            if isinstance(obj, py) and not (x in ("integer", "number") and isinstance(obj, bool)):
                ok = True
        if not ok:
            stop("ENDUSER_SCHEMA", f"{path}: 型違反 (期待{ts} 実際{type(obj).__name__})")
    if "enum" in spec and obj not in spec["enum"]:
        stop("ENDUSER_SCHEMA", f"{path}: enum違反 {obj!r}")
    if isinstance(obj, dict):
        props = spec.get("properties", {})
        for k in spec.get("required", []):
            if k not in obj:
                stop("ENDUSER_SCHEMA", f"{path}: 必須key欠落 '{k}'")
        ap = spec.get("additionalProperties", True)
        for k, v in obj.items():
            if k in props:
                check_schema(v, props[k], f"{path}.{k}")
            elif ap is False:
                stop("ENDUSER_SCHEMA", f"{path}: 未知のkey '{k}'(additionalProperties=false)")
            elif isinstance(ap, dict):
                check_schema(v, ap, f"{path}.{k}")
    elif isinstance(obj, list) and "items" in spec:
        for i, v in enumerate(obj):
            check_schema(v, spec["items"], f"{path}[{i}]")


def _walk_strings(o, path="$"):
    if isinstance(o, str):
        yield path, o
    elif isinstance(o, dict):
        for k, v in o.items():
            yield from _walk_strings(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from _walk_strings(v, f"{path}[{i}]")


def scan_forbidden_text(obj, label: str) -> None:
    for pth, s in _walk_strings(obj):
        for w in R.FORBIDDEN_OUTPUT:
            if w in s:
                stop("ENDUSER_FORBIDDEN_WORD", f"{label}{pth}: 禁止語'{w}'")
        for pat in R.FORBIDDEN_PATH_PATTERNS:
            if re.search(pat, s):
                stop("ENDUSER_FORBIDDEN_WORD", f"{label}{pth}: 絶対path/内部dir名の露出(/{pat}/)")


def _y_notice_text():
    try:
        import er121_family_y_structure_01 as ys
    except Exception as e:                              # noqa: BLE001
        stop("ENDUSER_NOTICE_MISMATCH", f"承認済みVoice説明文の正本(er121_family_y_structure_01)を読めない: {e}")
    return ys.PAGE_NOTICE_JA


def validate_output(article: dict, sync_public: dict, build_info: dict, rows_by_level: dict, study_by_level: dict, meta: dict, *, probe=None) -> None:
    """生成の最終ゲート。違反は`ENDUSER_*`でSTOP(部分生成なし)。"""
    check_schema(article, SCHEMA_ARTICLE_SPEC, "article")
    for lv, sp in sync_public.items():
        check_schema(sp, SCHEMA_SYNC_SPEC, f"sync_{lv}")
    check_schema(build_info, SCHEMA_BUILD_INFO_SPEC, "build_info")
    scan_forbidden_text(article, "article")
    scan_forbidden_text(sync_public, "sync")
    scan_forbidden_text({k: v for k, v in build_info.items() if k not in ("audio_sha256", "files", "assets", "sync")}, "build_info")
    for pth, s in _walk_strings(article):
        if re.search(r"<(?!/?(?:p|b|i|strong|em|br|span)\b)[a-zA-Z]", s):
            stop("ENDUSER_FORBIDDEN_WORD", f"article{pth}: 想定外のHTML tag")
    # 訳の出所(承認済み2値のみ。partsにja_sourceが無いjaは不可)
    for lv, L in article["levels"].items():
        for p in L["parts"]:
            if ("ja" in p) != ("ja_source" in p):
                stop("ENDUSER_JA_SOURCE_INVALID", f"{p['key']}: jaとja_sourceが対になっていない")
            if p.get("ja_source") not in (None, *R.JA_SOURCES):
                stop("ENDUSER_JA_SOURCE_INVALID", f"{p['key']}: ja_source={p.get('ja_source')}")
    # 本文一致(dev行のDOM平文とバイト一致。空白除去後)・下線span一致
    for lv, L in article["levels"].items():
        rows = rows_by_level[lv]
        if len(rows) != len(L["parts"]):
            stop("ENDUSER_TEXT_MISMATCH", f"{lv}: 行数 dev={len(rows)} out={len(L['parts'])}")
        n_sent = 0
        for r, p in zip(rows, L["parts"]):
            if r["row_id"] != p["key"] or r["label"] != p["label"] or r["kind"] != p["kind"] or abs(r["data_t"] - p["start"]) > 0.0005:
                stop("ENDUSER_TEXT_MISMATCH", f"{lv}: 行{r['label']}のlabel/kind/開始時刻がdevと不一致")
            if "_ref_text" in r:
                got = _ws("".join(s["text"] for pa in p["paragraphs"] for s in pa))
                if got.encode("utf-8") != r["_ref_text"].encode("utf-8"):
                    stop("ENDUSER_TEXT_MISMATCH", f"{lv} {p['label']}: End User本文がdev行の本文と不一致")
                marks = _merge_marks([(m[0], m[1], _ws(m[2])) for pa in p["paragraphs"] for s in pa for m in D.lk_spans(s["html"])])
                if marks != r["_ref_marks"]:
                    stop("ENDUSER_TEXT_MISMATCH", f"{lv} {p['label']}: 下線/太字対象がdevと不一致")
                n_sent += sum(len(pa) for pa in p["paragraphs"])
            if r["kind"] == "kp" and [_kp_key(k) for k in p["kp"]] != [_kp_key(k) for k in r["kp_table"]]:
                stop("ENDUSER_TEXT_MISMATCH", f"{lv} {p['label']}: KP表がdevと不一致")
        if n_sent != L["sentence_count"]:
            stop("ENDUSER_TEXT_MISMATCH", f"{lv}: sentence_count不一致")
        sids = {s["sid"] for p in L["parts"] for pa in p.get("paragraphs", []) for s in pa}
        if sids != {s["sid"] for s in sync_public[lv]["sentences"]}:
            stop("ENDUSER_SYNC_COVERAGE", f"{lv}: 本文のsid集合と同期のsid集合が不一致")
        # 学習ブロック: devのsection.study数・項目と一致。ニュアンス解説は廃止=キー無しまたは空配列のみ許容(中身ありはSTOP)
        st = study_by_level.get(lv, {})
        if L.get("nuance"):
            stop("ENDUSER_NUANCE_CORNER_ABOLISHED", f"{lv}: article.jsonのnuanceに中身があります(ニュアンス解説は廃止)")
        for kind in ("vocab", "grammar"):
            if [(i["heading"], [f["label"] for f in i["fields"]]) for i in L[kind]] != [(i["heading"], [f["label"] for f in i["fields"]]) for i in st.get(kind, [])]:
                stop("ENDUSER_STUDY_MISMATCH", f"{lv}: {kind}がdevの学習ブロックと不一致")
            if any(not i["fields"] for i in L[kind]):
                stop("ENDUSER_STUDY_MISMATCH", f"{lv}: {kind}に空の項目")
    # 音声一致(参照音声が実在しshaがbuild_infoと一致)
    if probe is not None:
        for rel, sha in build_info["audio_sha256"].items():
            pr = probe(rel)
            if pr is None:
                stop("ENDUSER_AUDIO_MISSING", rel)
            if pr["sha256"] != sha:
                stop("ENDUSER_AUDIO_MISMATCH", f"{rel}: sha256がbuild_infoと不一致")
    refs = {L["main"] for L in article["levels"].values()} | {p["seg"] for L in article["levels"].values() for p in L["parts"]}
    if not refs <= set(build_info["audio_sha256"]):
        stop("ENDUSER_AUDIO_MISSING", f"build_infoにshaが無い音声参照: {sorted(refs - set(build_info['audio_sha256']))[:3]}")
    # Voice説明文(Y): devにある⇔End Userにある、文言==承認済み定数
    if meta["notice"] is not None:
        if meta["family"] != "Y" or article["notice"] != meta["notice"] or article["notice"] != _y_notice_text():
            stop("ENDUSER_NOTICE_MISMATCH", "Voice説明文が承認済み文言(PAGE_NOTICE_JA)と一致しない、またはY以外にある")
    elif article["notice"] is not None:
        stop("ENDUSER_NOTICE_MISMATCH", "devページに無いVoice説明文がEnd Userにある")
    if build_info["cost"]["api_calls"] != 0:
        stop("ENDUSER_COST", "api_calls!=0")


# ------------------------------------------------------------
# assets(M5: DEVの機械的派生。sha256一致+禁止語0)
# ------------------------------------------------------------
def load_asset_manifest(assets_dir=ASSET_DIR) -> dict:
    p = Path(assets_dir) / ASSET_MANIFEST
    if not p.is_file():
        stop("ENDUSER_ASSET_MISMATCH", f"{ASSET_MANIFEST}が無い: {assets_dir}")
    return json.load(open(p, encoding="utf-8"))


def check_assets(assets_dir=ASSET_DIR) -> dict:
    man = load_asset_manifest(assets_dir)
    shas = {}
    for name in ASSET_FILES:
        p = Path(assets_dir) / name
        if not p.is_file():
            stop("ENDUSER_ASSET_MISMATCH", f"asset欠落: {name}")
        shas[name] = sha256_text_file(p)
        if shas[name] != man.get("files", {}).get(name):
            stop("ENDUSER_ASSET_MISMATCH", f"{name}: sha256がmanifestと不一致(production assetが書き換えられている)")
        txt = p.read_text(encoding="utf-8")
        for w in R.FORBIDDEN_ASSET:
            if w in txt:
                stop("ENDUSER_ASSET_MISMATCH", f"{name}: 禁止語'{w}'(DEV/確認用/他記事の残存)")
    return shas


# ------------------------------------------------------------
# 書込(M4: 一時dir→一括rename。失敗時にenduser/を書かない・既存enduser/を失敗時に削除しない)
# ------------------------------------------------------------
def write_enduser_page(out_dir, data: tuple, assets_dir=ASSET_DIR) -> dict:
    """data=build_enduser_data()の戻り値 (article, sync_public_by_level, build_info)。"""
    article, sync_public, build_info = data
    out_dir = Path(out_dir)
    shas = check_assets(assets_dir)                     # 失敗=ここでSTOP(何も書かない)
    parent = out_dir.parent
    if not parent.is_dir():
        stop("ENDUSER_WRITE_FAILED", f"出力親dirが無い: {parent}")
    tmp = parent / f".enduser.tmp.{os.getpid()}.{uuid.uuid4().hex[:8]}"
    old = parent / f".enduser.old.{os.getpid()}.{uuid.uuid4().hex[:8]}"
    swapped = False
    try:
        (tmp / "data").mkdir(parents=True)
        for name in ASSET_FILES:
            (tmp / name).write_bytes((Path(assets_dir) / name).read_bytes().replace(b"\r\n", b"\n"))   # 常にLFで書く
        files = {}

        def put(rel, obj):
            b = (json.dumps(obj, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
            (tmp / rel).write_bytes(b)
            files[rel] = sha256_bytes(b)
        put("data/article.json", article)
        for lv, sp in sync_public.items():
            put(f"data/sync_{lv}.json", sp)
        bi = json.loads(json.dumps(build_info))
        bi["assets"] = dict(shas)
        bi["files"] = {**files, **{n: shas[n] for n in ASSET_FILES}}
        check_schema(bi, SCHEMA_BUILD_INFO_SPEC, "build_info")
        scan_forbidden_text({k: v for k, v in bi.items() if k not in ("audio_sha256", "files", "assets", "sync")}, "build_info")
        (tmp / "build_info.json").write_bytes((json.dumps(bi, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
        if out_dir.exists():
            os.rename(out_dir, old)
            swapped = True
        os.rename(tmp, out_dir)
        if swapped:
            shutil.rmtree(old, ignore_errors=True)
        return {"out_dir": str(out_dir), "files": sorted(list(bi["files"]) + ["build_info.json"]), "build_info": bi}
    except EnduserPageStop:
        raise
    except Exception as e:                              # noqa: BLE001
        if swapped and old.exists() and not out_dir.exists():
            os.rename(old, out_dir)                     # 置換に失敗したら元のenduser/へ戻す
        raise EnduserPageStop("ENDUSER_WRITE_FAILED", f"{type(e).__name__}: {e}") from e
    finally:
        if tmp.exists():
            shutil.rmtree(tmp, ignore_errors=True)


# ------------------------------------------------------------
# 一括(build)
# ------------------------------------------------------------
def build_enduser(dev_dir, family: str, sync_by_level: dict, *, run_dir=None, ja_manuscript=None, kp_audio=None, asr=None, probe=None,
                  assets_dir=ASSET_DIR, y_article_ja=None, out_dir=None, extra_build_info=None) -> dict:
    t0 = time.time()
    dev_dir = Path(dev_dir).resolve()    # 相対pathだと音声pathが二重結合になる(runnerのctx.pages_dirは相対)
    idx = dev_dir / "index.html"
    if not idx.is_file():
        stop("ENDUSER_DEV_HTML_STRUCTURE", f"dev index.htmlが無い: {idx}")
    raw_dev = idx.read_bytes()   # shaは実ファイルのbyteで取る(改行変換の影響を受けない)
    dev_html = raw_dev.decode("utf-8")
    rows_by_level, study_by_level, meta = build_rows_from_dev_html(dev_html, {"family": family, "dev_dir": dev_dir, "dev_index_sha256": sha256_text_bytes(raw_dev)})
    probe = probe or make_probe(dev_dir)
    tl = check_against_timeline(rows_by_level, run_dir, family=family) if run_dir else {}
    ja = {"x_manuscript": load_x_manuscript(ja_manuscript) if ja_manuscript else None}
    if y_article_ja:
        import er121_family_y_structure_01 as ys
        ja["y_segments"] = ys.split_y_article(Path(y_article_ja).read_text(encoding="utf-8"))["segments"]
    if kp_audio is None:      # 同期moduleのkp_enが全KP行に揃っていれば、本moduleでの再ASRは不要(コスト・時間を増やさない)
        have = {lv: {sr.get("row_id") for sr in (sync_by_level.get(lv) or {}).get("rows", []) if isinstance(sr, dict) and sr.get("kp_en")} for lv in rows_by_level}
        need = {lv: [r for r in rows if r["kind"] == "kp" and r["row_id"] not in have[lv]] for lv, rows in rows_by_level.items()}
        kp_audio = compute_kp_audio({lv: rs for lv, rs in need.items() if rs}, dev_dir, asr=asr) if any(need.values()) else {}
    extra = dict(extra_build_info or {})
    if tl:
        extra["timeline_check"] = tl
    article, sync_public, build_info = build_enduser_data(rows_by_level, sync_by_level, study_by_level, ja, meta, kp_audio=kp_audio, probe=probe, extra_build_info=extra)
    build_info["cost"]["build_wall_s"] = round(time.time() - t0, 2)
    res = write_enduser_page(out_dir or (dev_dir / ENDUSER_DIRNAME), (article, sync_public, build_info), assets_dir)
    res["article"] = article
    return res


# ------------------------------------------------------------
# 公開dirの整合検査(M6: dev行=enduser本文、音声sha、asset sha、stale検出)
# ------------------------------------------------------------
def verify_consistency(public_dir, assets_dir=ASSET_DIR) -> dict:
    """公開dir(dev index.html + enduser/)を検査。違反を列挙して返す(例外にしない)。{'ok','violations':[{code,message}],'checked':{}}"""
    public_dir = Path(public_dir)
    V, checked = [], {}

    def bad(code, msg):
        V.append({"code": code, "message": msg})
    ed = public_dir / ENDUSER_DIRNAME
    idx = public_dir / "index.html"
    if not idx.is_file():
        bad("ENDUSER_DEV_HTML_STRUCTURE", "dev index.htmlが無い")
        return {"ok": False, "violations": V, "checked": checked}
    if not ed.is_dir():
        bad("ENDUSER_NOT_BUILT", f"{ENDUSER_DIRNAME}/が無い")
        return {"ok": False, "violations": V, "checked": checked}
    for stray in list(public_dir.glob(".enduser.tmp.*")) + list(public_dir.glob(".enduser.old.*")):
        bad("ENDUSER_STALE_TMP", f"書込途中の残骸: {stray.name}")
    try:
        bi = json.load(open(ed / "build_info.json", encoding="utf-8"))
        art = json.load(open(ed / "data" / "article.json", encoding="utf-8"))
        check_schema(bi, SCHEMA_BUILD_INFO_SPEC, "build_info")
        check_schema(art, SCHEMA_ARTICLE_SPEC, "article")
    except EnduserPageStop as e:
        bad(e.code, e.message)
        return {"ok": False, "violations": V, "checked": checked}
    except Exception as e:                              # noqa: BLE001
        bad("ENDUSER_UNREADABLE", f"{type(e).__name__}: {e}")
        return {"ok": False, "violations": V, "checked": checked}
    raw_dev = idx.read_bytes()
    dev_html = raw_dev.decode("utf-8")
    if sha256_text_bytes(raw_dev) != bi["dev_index_sha256"]:
        bad("ENDUSER_STALE_DEV_CHANGED", "dev index.htmlがenduser生成後に変更されている(再生成が必要)")
    # ファイルsha
    for rel, sha in bi["files"].items():
        p = ed / rel
        if not p.is_file():
            bad("ENDUSER_FILE_MISSING", rel)
        elif sha256_text_file(p) != sha:
            bad("ENDUSER_FILE_SHA_MISMATCH", rel)
    # asset sha(production assetと一致)
    try:
        want = check_assets(assets_dir)
        for n in ASSET_FILES:
            if (ed / n).is_file() and sha256_text_file(ed / n) != want[n]:
                bad("ENDUSER_ASSET_MISMATCH", f"{n}がproduction assetと不一致")
    except EnduserPageStop as e:
        bad(e.code, e.message)
    # 音声sha
    nb = 0
    for rel, sha in bi["audio_sha256"].items():
        p = public_dir / rel
        if not p.is_file():
            bad("ENDUSER_AUDIO_MISSING", rel)
        elif sha256_file(p) != sha:
            bad("ENDUSER_AUDIO_MISMATCH", rel)
        nb += 1
    checked["audio_files"] = nb
    # dev行 = enduser本文(再解析して比較)
    try:
        rows_by_level, study_by_level, meta = build_rows_from_dev_html(dev_html, {"family": bi["family"], "dev_dir": public_dir, "id": bi["id"]})
        for lv, rows in rows_by_level.items():
            if lv not in art["levels"]:
                bad("ENDUSER_TEXT_MISMATCH", f"{lv}: End Userデータに無いlevel")
                continue
            parts = art["levels"][lv]["parts"]
            if len(parts) != len(rows):
                bad("ENDUSER_TEXT_MISMATCH", f"{lv}: 行数 dev={len(rows)} enduser={len(parts)}")
                continue
            for r, p in zip(rows, parts):
                if r["label"] != p["label"] or r["kind"] != p["kind"] or abs(r["data_t"] - p["start"]) > 0.0005 or r["audio_rel"] != p["seg"]:
                    bad("ENDUSER_TEXT_MISMATCH", f"{lv} {r['label']}: label/kind/開始時刻/audioがdevと不一致")
                if "_ref_text" in r:
                    got = _ws("".join(s["text"] for pa in p.get("paragraphs", []) for s in pa))
                    if got != r["_ref_text"]:
                        bad("ENDUSER_TEXT_MISMATCH", f"{lv} {r['label']}: 本文がdevと不一致")
                if r["kind"] == "kp" and [_kp_key(k) for k in p["kp"]] != [_kp_key(k) for k in r["kp_table"]]:
                    bad("ENDUSER_TEXT_MISMATCH", f"{lv} {r['label']}: KP表が不一致")
            if art["levels"][lv].get("nuance"):
                bad("ENDUSER_NUANCE_CORNER_ABOLISHED", f"{lv}: article.jsonのnuanceに中身があります(ニュアンス解説は廃止)")
            for kind in ("vocab", "grammar"):
                if [(i["heading"], [(f["label"], f["html"]) for f in i["fields"]]) for i in art["levels"][lv][kind]] != \
                        [(i["heading"], [(f["label"], f["html"]) for f in i["fields"]]) for i in study_by_level[lv].get(kind, [])]:
                    bad("ENDUSER_STUDY_MISMATCH", f"{lv}: {kind}がdevと不一致")
        if set(art["levels"]) != set(rows_by_level):
            bad("ENDUSER_TEXT_MISMATCH", "levelの集合がdevと不一致")
        if (meta["notice"] or None) != art["notice"]:
            bad("ENDUSER_NOTICE_MISMATCH", "Voice説明文がdevと不一致")
        checked["levels"] = sorted(rows_by_level)
    except EnduserPageStop as e:
        bad(e.code, e.message)
    # 出力内の禁止語・訳の出所
    try:
        scan_forbidden_text(art, "article")
        for L in art["levels"].values():
            for p in L["parts"]:
                if p.get("ja_source") not in (None, *R.JA_SOURCES):
                    bad("ENDUSER_JA_SOURCE_INVALID", f"{p['key']}: ja_source={p.get('ja_source')}")
    except EnduserPageStop as e:
        bad(e.code, e.message)
    return {"ok": not V, "violations": V, "checked": checked}


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------
# ------------------------------------------------------------
# WP-E: 正式経路(runner hook)用の一括生成 `produce_enduser` と未実装ゲート§6-2(4)(5)
# ------------------------------------------------------------
EPISODE_OFFSET_TOL_S = 0.05      # 設計§6-2(4): segmentが全編mp3内data-t位置に一致(1秒窓の相互相関ずれ)
EPISODE_LEN_TOL_S = 0.15         # 設計§6-2(5): 全編音声長とtimeline合計の差
EPISODE_CORR_MIN = 0.97         # 相関の下限(別音声/位置ずれの検出用)。実測(月X・全44行)は最小0.9885、lagは全行0.000s。mp3再エンコード差で1.0にはならない
_EP_SR = 16000


def _best_lag(x, y, max_lag):
    """x(1秒窓)とy(前後max_lag余白付き)の正規化相互相関の最大(lag_samples, corr)。"""
    import numpy as np
    n = len(x)
    xv = (x - x.mean()).astype(np.float64)
    xn = float(np.sqrt((xv * xv).sum()))
    if xn < 1e-9:
        return None
    yv = y.astype(np.float64)
    nfft = 1 << (len(yv) + n).bit_length()
    corr = np.fft.irfft(np.fft.rfft(yv, nfft) * np.conj(np.fft.rfft(xv, nfft)), nfft)[: len(yv) - n + 1]
    c1 = np.concatenate([[0.0], np.cumsum(yv)])
    c2 = np.concatenate([[0.0], np.cumsum(yv ** 2)])
    m = len(yv) - n + 1
    s1 = c1[n:n + m] - c1[:m]
    s2 = c2[n:n + m] - c2[:m]
    yn = np.sqrt(np.maximum(s2 - s1 * s1 / n, 1e-12))
    ncc = corr / (xn * yn)
    k = int(np.argmax(ncc))
    return k - max_lag, float(ncc[k])


def timeline_total(run_dir, sub: str):
    """run配下の組立timeline(`<sub>/audit/timeline.json`|`<sub>/assembly/timeline.json`。pause/_silenceも含む全項目)の終端秒。無ければNone。
    ZのdevページはIntro/Notification/Outro行を持たないため、全編長との照合はdevの行ではなくこの完全なtimelineで行う。"""
    if not run_dir:
        return None
    for pat in TIMELINE_CANDIDATES:
        p = Path(run_dir) / pat.format(sub=sub)
        if p.is_file():
            d = json.load(open(p, encoding="utf-8"))
            tl = d["timeline"] if isinstance(d, dict) else d
            return max(float(x["start_seconds"]) + float(x["duration_seconds"]) for x in tl)
    return None


def episode_checks(dev_dir, rows_by_level: dict, meta: dict, probe, run_dir=None) -> dict:
    """§6-2(4)(5): (4)各segmentの1秒窓が全編mp3の`data-t`位置にあること(相関ずれ<=0.05s)、(5)全編音声長とrunのtimeline終端の差<=0.15s
    (timelineが無い場合のみdevページの最終行終端で代替し、`length_basis`に記録)。
    違反は`ENDUSER_EPISODE_OFFSET` / `ENDUSER_EPISODE_LENGTH`でSTOP。設計値は緩和しない。"""
    import numpy as np
    import er135_enduser_sync_01 as S
    out = {}
    max_lag = int(0.3 * _EP_SR)
    for lv, rows in rows_by_level.items():
        main = meta["level_main"][lv]
        pm = probe(main)
        if pm is None:
            stop("ENDUSER_AUDIO_MISSING", f"{lv}: {main}")
        total = timeline_total(run_dir, {"std": "a2", "adv": "b1b"}[lv])
        basis = "run_timeline"
        if total is None:
            total, basis = max((r["data_t"] + (probe(r["audio_rel"]) or {"duration": 0.0})["duration"]) for r in rows), "dev_last_row_end"
        dlen = abs(pm["duration"] - total)
        if dlen > EPISODE_LEN_TOL_S:
            stop("ENDUSER_EPISODE_LENGTH", f"{lv}: 全編音声長{pm['duration']:.3f}s とtimeline合計{total:.3f}sの差{dlen:.3f}s > {EPISODE_LEN_TOL_S}s")
        ep = S.load_audio(str(Path(dev_dir) / main), _EP_SR)
        n_ok, skipped, worst, min_corr = 0, 0, 0.0, 1.0
        for r in rows:
            seg = S.load_audio(str(Path(dev_dir) / r["audio_rel"]), _EP_SR)
            w = _EP_SR
            start = None
            for off in range(0, max(1, len(seg) - w + 1), _EP_SR // 4):      # 先頭から0.25秒刻みで、音のある最初の1秒窓
                if float(np.sqrt(np.mean(seg[off:off + w] ** 2))) > 0.01:
                    start = off
                    break
            if start is None or len(seg) < w:
                skipped += 1
                continue
            x = seg[start:start + w]
            a = int(round(r["data_t"] * _EP_SR)) + start - max_lag
            lo = max(a, 0)
            y = ep[lo: a + w + 2 * max_lag]
            if len(y) < w:
                stop("ENDUSER_EPISODE_OFFSET", f"{r['row_id']}: data-t={r['data_t']}が全編音声の外")
            bl = _best_lag(x, y, max_lag - (lo - a))
            if bl is None:
                skipped += 1
                continue
            lag, c = bl
            lag_s = lag / _EP_SR
            worst, min_corr = max(worst, abs(lag_s)), min(min_corr, c)
            if abs(lag_s) > EPISODE_OFFSET_TOL_S or c < EPISODE_CORR_MIN:
                stop("ENDUSER_EPISODE_OFFSET", f"{r['row_id']}: segmentが全編音声のdata-t={r['data_t']}位置と一致しない lag={lag_s:+.3f}s corr={c:.4f}"
                                              f"(許容 lag<={EPISODE_OFFSET_TOL_S}s corr>={EPISODE_CORR_MIN})")
            n_ok += 1
        out[lv] = {"rows_checked": n_ok, "rows_skipped_silent": skipped, "max_abs_lag_s": round(worst, 4), "min_corr": round(min_corr, 5),
                   "episode_dur_s": round(pm["duration"], 3), "timeline_total_s": round(total, 3), "length_diff_s": round(dlen, 3), "length_basis": basis}
    return out


def proper_nouns_for_run(run_dir, family: str, rows_by_level: dict | None = None, meta: dict | None = None) -> dict:
    """FZ-DIALOGUE-LR-ADOPTION-01 委任_07: runから機械的に得られる固有名詞(Whisper initial_prompt + 既知名正規化用。ページ表示の名前は不変)。
    戻り値 {"en":[...], "ja":[...]}。Production rosterを読み取るだけ(書込なし)。
     - Z: `<run_dir>/voice_assignment.json`のspeakersのうち、writer原稿(`<run_dir>/writer/*.md`)で大文字始まり形のみ現れる話者名(Tajomaru等。woodcutter等の一般名詞は除く)。
     - X/Y: 記事タイトル語(meta.topic_en)の大文字始まり語 + KP表現(rows_by_levelのkp.expressions)。"""
    en, ja = [], []

    def add(lst, w):
        w = (w or "").strip()
        if w and w not in lst:
            lst.append(w)
    fam = str(family).lower()
    if fam == "z" and run_dir:
        rd = Path(run_dir)
        va = rd / "voice_assignment.json"
        text = ""
        for f in sorted((rd / "writer").glob("*.md")) if (rd / "writer").is_dir() else []:
            text += f.read_text(encoding="utf-8", errors="replace") + "\n"
        if va.is_file():
            for sp in json.loads(va.read_text(encoding="utf-8")).get("speakers", []):
                name = str(sp.get("speaker", "")).strip()
                if not name or "_" in name:
                    continue
                cap = name[:1].upper() + name[1:]
                if re.search(r"(?<![A-Za-z])" + re.escape(cap) + r"(?![A-Za-z])", text) and not re.search(r"(?<![A-Za-z])" + re.escape(name) + r"(?![A-Za-z])", text):
                    add(en, cap)
    else:
        for w in re.findall(r"[A-Z][A-Za-z'\-]+", (meta or {}).get("topic_en", "") or ""):
            add(en, w)
        for lv_rows in (rows_by_level or {}).values():
            for r in lv_rows:
                for ex in (r.get("kp") or {}).get("expressions", []) if isinstance(r.get("kp"), dict) else []:
                    add(en, ex)
    return {"en": en, "ja": ja}


def produce_enduser(dev_dir, family: str, *, run_dir=None, cache_dir, ja_manuscript=None, y_article_ja=None, model="medium",
                    out_dir=None, align_mode="direct") -> dict:
    """正式経路の一括生成(API 0): dev index.html -> 行抽出 -> 02A `sync_level`(ローカルfaster-whisper。tts_textは渡さず直接整列=Fable決定)
    -> §6-2(4)(5) -> build_enduser(validator込み・atomic書込)。失敗は`EnduserPageStop(ENDUSER_*)`(dev index.htmlと既存enduser/は不変)。
    再実行時は`cache_dir`(segment mp3 sha256単位のASR生出力)によりASR 0回。"""
    import er135_enduser_sync_01 as S
    t0 = time.time()
    dev_dir = Path(dev_dir).resolve()
    idx = dev_dir / "index.html"
    if not idx.is_file():
        stop("ENDUSER_DEV_HTML_STRUCTURE", f"dev index.htmlが無い: {idx}")
    raw_dev = idx.read_bytes()
    rows_by_level, _study, meta = build_rows_from_dev_html(raw_dev.decode("utf-8"), {"family": family, "dev_dir": dev_dir, "dev_index_sha256": sha256_text_bytes(raw_dev)})
    probe = make_probe(dev_dir)
    sync_by_level, sync_wall = {}, {}
    pn = proper_nouns_for_run(run_dir, family, rows_by_level, meta)
    os.makedirs(cache_dir, exist_ok=True)
    for lv, rows in rows_by_level.items():
        t1 = time.time()
        try:
            sync_by_level[lv] = S.sync_level(str(dev_dir), rows_for_sync(rows), cache_dir=str(cache_dir), model=model, align_mode=align_mode,
                                             proper_nouns=pn)
        except S.EnduserSyncError as e:
            raise EnduserPageStop(e.code, e.message) from e
        sync_wall[lv] = round(time.time() - t1, 1)
    ep = episode_checks(dev_dir, rows_by_level, meta, probe, run_dir=run_dir)
    res = build_enduser(dev_dir, family, sync_by_level, run_dir=run_dir, ja_manuscript=ja_manuscript, y_article_ja=y_article_ja, probe=probe,
                        out_dir=out_dir, extra_build_info={"episode_check": ep})
    res["sync_by_level"] = {lv: {"gate": s["gate"]["status"], "min_row_ratio": s["gate"]["token_match"]["min_row_ratio"], "cost": s["cost"],
                                 "wall_s": sync_wall[lv]} for lv, s in sync_by_level.items()}
    res["episode_check"] = ep
    res["total_wall_s"] = round(time.time() - t0, 1)
    return res


def find_x_ja_manuscript(source_dir):
    """X: 承認済み日本語原稿の優先順(`derive_japanese_title`と同じ: revision2 > revision1 > original)。無ければNone(訳なし=非表示)。"""
    for name in ("revision2.md", "revision1.md", "original.md"):
        p = Path(source_dir) / "ja_writer" / name
        if p.is_file():
            return str(p)
    return None


def hook_run(dev_dir, family: str, *, run_dir, cache_dir, ja_manuscript=None, y_article_ja=None, result_json=None, browser_verify=True, model="medium") -> dict:
    """runner hook共通入口: 生成 -> verify_consistency -> Playwright検証(PC+モバイル模擬)。失敗は`EnduserPageStop(ENDUSER_*)`。
    成功時は要約dictを返し、result_jsonへ保存する(公開dirには置かない)。"""
    res = produce_enduser(dev_dir, family, run_dir=run_dir, cache_dir=cache_dir, ja_manuscript=ja_manuscript, y_article_ja=y_article_ja, model=model)
    vc = verify_consistency(dev_dir)
    if not vc["ok"]:
        raise EnduserPageStop("ENDUSER_CONSISTENCY", "生成直後のverify_consistencyが不合格: " + json.dumps(vc["violations"], ensure_ascii=False)[:600])
    summary = {"ok": True, "family": family.upper(), "enduser_dir": res["out_dir"], "files": res["files"], "consistency": "ok",
               "sync": res["sync_by_level"], "episode_check": res["episode_check"], "translation_coverage": res["build_info"]["translation_coverage"],
               "dev_index_sha256": res["build_info"]["dev_index_sha256"], "enduser_index_sha256": res["build_info"]["files"]["index.html"],
               "total_wall_s": res["total_wall_s"], "api_calls": 0, "browser_verify": None}
    if browser_verify:
        import er135_enduser_page_verify_01 as V
        out = (str(Path(result_json).with_name(Path(result_json).stem + "_browser.json")) if result_json else None)
        rc = V.run(dev_dir, out=out)
        summary["browser_verify"] = {"rc": rc, "result": out}
        if rc != 0:
            if result_json:
                Path(result_json).write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
            raise EnduserPageStop("ENDUSER_BROWSER_VERIFY", f"Playwright検証が不合格(rc={rc}): {out}")
    if result_json:
        Path(result_json).write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    return summary


def publish_copy(pages_dir, public_dir, *, browser_verify=True, backup_root=None) -> dict:
    """Y公開手順の補助(Opus M6): `<pages_dir>/enduser/`だけを公開dirへcopy(devページ・音声は触らない)し、copy先で
    verify_consistency(+Playwright)を実行。公開dirのdev index.htmlがpages_dirのものと異なる(stale)場合は、copy前に不合格にして公開dirを一切変更しない。
    copyは一時名->renameで原子的。copy後の検査に落ちたら元のenduser/へ戻す。"""
    pages_dir, public_dir = Path(pages_dir), Path(public_dir)
    src = pages_dir / ENDUSER_DIRNAME
    if not src.is_dir():
        stop("ENDUSER_NOT_BUILT", f"{src}が無い(pages/page_verifyを先に実行)")
    if not public_dir.is_dir() or not (public_dir / "index.html").is_file():
        stop("ENDUSER_DEV_HTML_STRUCTURE", f"公開dir/index.htmlが無い: {public_dir}")
    bi = json.load(open(src / "build_info.json", encoding="utf-8"))
    pub_sha = sha256_text_bytes((public_dir / "index.html").read_bytes())
    if pub_sha != bi["dev_index_sha256"]:
        return {"ok": False, "public_dir": str(public_dir), "copied": False,
                "consistency": {"ok": False, "checked": {}, "violations": [{"code": "ENDUSER_STALE_DEV_CHANGED",
                                "message": "公開dirのdev index.htmlがenduser生成時のものと異なる(公開後に手編集された等)。公開dirは変更していない。"
                                           "`produce --dev-dir <公開dir>`で公開dirのdev HTMLから再生成する"}]}}
    tmp = public_dir / f".enduser.tmp.{os.getpid()}.{uuid.uuid4().hex[:8]}"
    # 旧enduser/の退避先は公開dir外(OPEN-606: 公開dir内に残すとverifyがENDUSER_STALE_TMPでrollbackする)
    bk_root = Path(backup_root) if backup_root else pages_dir.parent / "enduser_publish_backup"
    old = bk_root / (time.strftime("%Y%m%d_%H%M%S") + f"_{os.getpid()}_{uuid.uuid4().hex[:6]}") / ENDUSER_DIRNAME
    dst = public_dir / ENDUSER_DIRNAME
    swapped = False
    try:
        shutil.copytree(src, tmp)
        if dst.exists():
            old.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(dst), str(old))
            swapped = True
        os.rename(tmp, dst)
    except Exception as e:                                  # noqa: BLE001
        if swapped and old.exists() and not dst.exists():
            shutil.move(str(old), str(dst))
        raise EnduserPageStop("ENDUSER_WRITE_FAILED", f"{type(e).__name__}: {e}") from e
    finally:
        if tmp.exists():
            shutil.rmtree(tmp, ignore_errors=True)
    vc = verify_consistency(public_dir)
    if not vc["ok"] and swapped and old.exists():           # copy後の検査に落ちた: 元のenduser/へ戻す
        shutil.rmtree(dst, ignore_errors=True)
        shutil.move(str(old), str(dst))
        return {"ok": False, "public_dir": str(public_dir), "copied": False, "rolled_back": True, "consistency": vc}
    # 成功時も旧版は公開dir外のbackupに保持(削除しない)
    out = {"ok": vc["ok"], "public_dir": str(public_dir), "copied": True, "consistency": vc}
    if vc["ok"] and browser_verify:
        import er135_enduser_page_verify_01 as V
        out["browser_rc"] = V.run(public_dir)
        out["ok"] = out["browser_rc"] == 0
    return out


def _load_sync_args(items: list) -> dict:
    out = {}
    for it in items:
        lv, path = (it.split("=", 1) if "=" in it and not os.path.exists(it) else (None, it))
        j = json.load(open(path, encoding="utf-8"))
        lv = lv or j.get("level")
        if lv not in ("std", "adv"):
            stop("ENDUSER_SYNC_SCHEMA", f"{path}: levelを特定できない(--sync-json std=PATH のように指定)")
        out[lv] = j
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="End User視聴ページ生成・検証(API 0)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--family", required=True, choices=["x", "y", "z"])
    b.add_argument("--dev-dir", required=True)
    b.add_argument("--run-dir")
    b.add_argument("--sync-json", nargs="+", required=True, help="enduser_sync_v1のjson(level指定: std=PATH adv=PATH、またはjson内のlevel)")
    b.add_argument("--ja-manuscript", help="X: 承認済み日本語原稿(ja_writer/revision2.md等)")
    b.add_argument("--y-article-ja", help="Y: 承認済み日本語原稿(text/article_ja.md)。指定時はdevの日本語の元原稿と照合")
    b.add_argument("--kp-audio-json", help="KP英語区間のjson(省略時はffmpeg+ローカルASRで算出)")
    v = sub.add_parser("verify-consistency")
    v.add_argument("--public-dir", required=True)
    o = sub.add_parser("verify-only")
    o.add_argument("--public-dir", required=True)
    o.add_argument("--base-url", help="既に配信中のURL(省略時はローカルRange対応サーバを起動)")
    o.add_argument("--out", help="結果jsonの保存先")
    o.add_argument("--shots", help="スクリーンショットの保存先dir")
    pr = sub.add_parser("produce", help="正式経路と同じ一括生成(同期ASR込み・API 0)。公開済みdirへの後付け(backfill)にも使う")
    pr.add_argument("--family", required=True, choices=["x", "y", "z"])
    pr.add_argument("--dev-dir", required=True)
    pr.add_argument("--run-dir")
    pr.add_argument("--cache-dir", required=True, help="ASR生出力キャッシュ(公開dirには置かない)")
    pr.add_argument("--ja-manuscript")
    pr.add_argument("--y-article-ja")
    pr.add_argument("--result-json")
    pr.add_argument("--no-browser", action="store_true")
    pc = sub.add_parser("publish-copy", help="Y公開手順の補助: pages_dirのenduser/を公開dirへcopyしコピー先で検証")
    pc.add_argument("--pages-dir", required=True)
    pc.add_argument("--public-dir", required=True)
    pc.add_argument("--no-browser", action="store_true")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "produce":
            r = hook_run(a.dev_dir, a.family, run_dir=a.run_dir, cache_dir=a.cache_dir, ja_manuscript=a.ja_manuscript, y_article_ja=a.y_article_ja,
                         result_json=a.result_json, browser_verify=not a.no_browser)
            print(json.dumps(r, ensure_ascii=False, indent=1))
            return 0
        if a.cmd == "publish-copy":
            r = publish_copy(a.pages_dir, a.public_dir, browser_verify=not a.no_browser)
            print(json.dumps(r, ensure_ascii=False, indent=1))
            return 0 if r["ok"] else 3
        if a.cmd == "build":
            kp = json.load(open(a.kp_audio_json, encoding="utf-8")) if a.kp_audio_json else None
            r = build_enduser(a.dev_dir, a.family, _load_sync_args(a.sync_json), run_dir=a.run_dir, ja_manuscript=a.ja_manuscript, kp_audio=kp, y_article_ja=a.y_article_ja)
            print(json.dumps({"ok": True, "out_dir": r["out_dir"], "files": r["files"]}, ensure_ascii=False))
            return 0
        if a.cmd == "verify-consistency":
            r = verify_consistency(a.public_dir)
            print(json.dumps(r, ensure_ascii=False, indent=1))
            return 0 if r["ok"] else 3
        if a.cmd == "verify-only":
            import er135_enduser_page_verify_01 as V
            return V.run(a.public_dir, base_url=a.base_url, out=a.out, shots=a.shots)
    except EnduserPageStop as e:
        print(json.dumps({"ok": False, "code": e.code, "message": e.message}, ensure_ascii=False))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
