# -*- coding: utf-8 -*-
"""ユーザー試聴ページ標準フォーマット(Family X / Z / 将来Y 共通、2026-10-18 FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_19)。

正本=ユーザー受入済みFamily Xページ(user_test/boredom_aggression_bape_e2e_01/index.html、2026-10-17試聴PASS)の構成の明文化。
新仕様の創作ではない。構成:
  1ページに Standard / Advanced の2節。各節: 全編通し再生(assembled音声)ボタン -> Key Phrases(英語+日本語意味等)
  -> 再生順の全スクリプト表(パート/音声/Script。効果音・内部情報は載せない) 。
  ASR警告(PASS_WITH_WARNING)等の補助情報は全レベル節の後ろ(補助表示)に置く。

本moduleは (1) render_standard_page: 共通builder  (2) check_page: 標準適合check(page_verify系/Regression共通) を提供する。
API呼出・音声生成は一切しない(HTML文字列の生成と解析のみ)。
"""
from __future__ import annotations

import html as _html
import json
import os
import re
from html.parser import HTMLParser

esc = _html.escape

CSS = ("<style>body{font-family:sans-serif;max-width:1100px;margin:1em auto;padding:0 1em;line-height:1.5}"
       "table{border-collapse:collapse;width:100%;margin-bottom:1.5em}th,td{border:1px solid #ccc;padding:6px;vertical-align:top;text-align:left}"
       "td.play{min-width:340px}td.play audio,audio{width:100%}.sec{color:#666;font-size:.85em}"
       ".script{background:#f6f6f6;padding:4px;margin:3px 0;font-size:.95em;white-space:pre-wrap}"
       ".kp td,.kp th{border:1px solid #ccc;padding:4px 10px}"
       ".combo{background:#eef6ff;padding:10px;border:1px solid #99c;margin-bottom:1em}"
       ".playall{font-size:1.1em;padding:8px 18px;margin-bottom:8px;cursor:pointer}"
       ".note{background:#fff8e0;padding:8px;border:1px solid #cb8;margin-bottom:1em}"
       "nav a{margin-right:1.2em;font-weight:bold}details.aux{background:#fafafa;border:1px solid #ddd;padding:6px 10px;margin:1em 0}"
       "</style>")

_JS = ("<script>document.querySelectorAll('button.playall').forEach(b=>b.onclick=()=>{const a=document.getElementById(b.dataset.target);"
       "a.play();});"
       "document.querySelectorAll('button.jump').forEach(b=>b.onclick=()=>{const a=document.getElementById(b.dataset.target);"
       "a.currentTime=parseFloat(b.dataset.t);a.play();});</script>")


def script_block(text: str) -> str:
    return "<div class='script'>" + esc(text or "") + "</div>"


def kp_block(headers, cells) -> str:
    """headers/cells=同長のlist(例: ['英語','日本語の意味'] / [en, ja])。"""
    return ("<table class='kp'><tr>" + "".join(f"<th>{esc(h)}</th>" for h in headers) + "</tr><tr>"
            + "".join(f"<td>{esc(c)}</td>" for c in cells) + "</tr></table>")


def render_standard_page(title: str, levels: list, intro_html: str = "", aux_html: str = "") -> str:
    """levels=[{id:'std', label:'Standard', full_src, duration, rows:[{part,start,dur,src,blocks:[html...]}]}] (再生順)。
    aux_html=ASR警告等の補助情報(全レベル節の後ろに置かれる)。"""
    nav = "<nav>" + "".join(f"<a href='#{lv['id']}'>{esc(lv['label'])}</a>" for lv in levels) + "</nav>"
    body = []
    for lv in levels:
        mid = f"main_{lv['id']}"
        rows = []
        for r in lv["rows"]:
            rows.append(
                f"<tr><td><b>{esc(r['part'])}</b><br><span class='sec'>{r['start']:.1f}秒〜 ({r['dur']:.1f}秒)</span><br>"
                f"<button class='jump' data-target='{mid}' data-t='{r['start']}'>全編のこの位置へ</button></td>"
                f"<td class='play'><audio controls preload='none' src='{esc(r['src'])}'></audio></td>"
                f"<td>{''.join(r['blocks'])}</td></tr>")
        body.append(
            f"<h2 id='{lv['id']}'>{esc(lv['label'])}(通し全編 {lv['duration']:.0f}秒)</h2>"
            f"<div class='combo'><button class='playall' data-target='{mid}'>&#9654; {esc(lv['label'])} 全編を通し再生</button><br>"
            f"<audio id='{mid}' controls preload='none' src='{esc(lv['full_src'])}'></audio></div>"
            "<table><thead><tr><th>パート</th><th>音声</th><th>Script / Key Phrase</th></tr></thead><tbody>"
            + "".join(rows) + "</tbody></table>")
    pg = (f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>{esc(title)}</title>"
          f"<meta name='viewport' content='width=device-width, initial-scale=1'>{CSS}</head><body>"
          f"<h1>{esc(title)}</h1>{nav}{intro_html}" + "".join(body) + aux_html + _JS + "</body></html>")
    assert "file:///" not in pg and "C:\\" not in pg and "C:/" not in pg
    return pg


# ============================================================
# 標準適合check(Regression / page_verify共通)
# ============================================================
class _Node:
    __slots__ = ("tag", "attrs", "children", "text", "idx", "parent")

    def __init__(self, tag, attrs, parent, idx):
        self.tag, self.attrs, self.children, self.text, self.idx, self.parent = tag, dict(attrs), [], [], idx, parent

    def cls(self):
        return (self.attrs.get("class") or "").split()

    def all_text(self):
        return "".join(x if isinstance(x, str) else x.all_text() for x in self.text)


class _Tree(HTMLParser):
    VOID = {"meta", "br", "img", "input", "link", "hr", "source"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = _Node("root", {}, None, 0)
        self.cur = self.root
        self.flat = []
        self.n = 0

    def handle_starttag(self, tag, attrs):
        self.n += 1
        node = _Node(tag, attrs, self.cur, self.n)
        self.cur.children.append(node)
        self.cur.text.append(node)
        self.flat.append(node)
        if tag == "br":
            self.cur.text.append(" | ")
        if tag not in self.VOID:
            self.cur = node

    def handle_endtag(self, tag):
        c = self.cur
        while c is not None and c.tag != tag:
            c = c.parent
        if c is not None and c.parent is not None:
            self.cur = c.parent

    def handle_data(self, data):
        self.cur.text.append(data)


# 「音楽」は単独/括弧内/ラベル形式のみ内部情報(効果音注記)として検出し、本文中の語(音楽や動画…)は誤検知しない(FXN2-E2E-02 委任_02)
_INTERNAL_RE = re.compile(
    r"Voice:|Style:|base_sha|fx_20\d{6}|SUPPORT_JA|SUPPORT_|(?:^|[\s(（\[【「『])音楽(?:$|[\s)）\]】」』:：])|通知音|効果音|読み上げなし|fallback_used|"
    r"\(A2\)|\(B1\)|B1B|PD06|\bK2\b|\bP8\b|\bP7\b|\bE1\b|\bS3\b|style_profile|slowdown|6%減速|tts_backend")
_RAW_ID_RE = re.compile(r"^(full_story_part\d+_c\d+|key_phrase_\d+|kp\d+_en|comment_\d+|[a-z]+(_[a-z0-9]+)+)$")
_JP_RE = re.compile(r"[ぁ-んァ-ヶ一-龥]")
_START_RE = re.compile(r"([0-9]+(?:\.[0-9]+)?)秒〜")
_AUX_MARK_RE = re.compile(r"PASS_WITH_WARNING|事後試聴|ASR警告")
_SFX_LABEL_RE = re.compile(r"^(Intro|Outro|Notification\s*\d*)$", re.I)


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def check_page(html_text: str, base_dir: str | None = None, levels=("Standard", "Advanced")) -> dict:
    """ユーザー試聴ページ標準適合check。戻り値={'overall':'PASS'|'FAIL','checks':{name:{ok,detail}},'levels':{...}}。
    levels=この頁に必須のレベル節(1レベル単独頁なら ('Standard',))。base_dir指定時は音声ファイル実在も確認。"""
    t = _Tree()
    t.feed(html_text)
    flat = t.flat
    checks = {}

    def put(name, ok, detail=""):
        checks[name] = {"ok": bool(ok), "detail": detail}

    h2 = [n for n in flat if n.tag == "h2"]
    sect = {}
    for i, h in enumerate(h2):
        m = re.match(r"^(Standard|Advanced)", _norm(h.all_text()), re.I)
        if m:
            end = h2[i + 1].idx if i + 1 < len(h2) else 10 ** 9
            sect[m.group(1).capitalize()] = (h, [n for n in flat if h.idx < n.idx < end])
    put("levels_present", all(l in sect for l in levels), f"required={list(levels)} found={list(sect)}")

    last_level_end = 0
    lvl_report = {}
    for lv in levels:
        if lv not in sect:
            continue
        h, nodes = sect[lv]
        rep = {}
        # C1 全編通し再生: 見出し後、最初のtableより前にcontrols付きaudio
        first_table = next((n.idx for n in nodes if n.tag == "table"), 10 ** 9)
        main = next((n for n in nodes if n.tag == "audio" and n.idx < first_table), None)
        src = (main.attrs.get("src") or "") if main else ""
        ok = bool(main) and "controls" in main.attrs and bool(re.search(r"\.(mp3|wav|m4a|ogg)(\?.*)?$", src, re.I))
        if ok and base_dir and not re.match(r"https?://", src):
            ok = os.path.exists(os.path.join(base_dir, src))
        put(f"{lv}:full_play_audio", ok, f"src={src}")
        rep["full_src"] = src
        # C2 スクリプト(再生順)
        rows = []
        for tr in [n for n in nodes if n.tag == "tr" and not _in_kp_table(n)]:
            tds = [c for c in tr.children if c.tag == "td"]
            if len(tds) < 3:
                continue
            label_node = next((x for x in _walk(tds[0]) if x.tag == "b"), None)
            label = _norm(label_node.all_text()) if label_node else ""
            m = _START_RE.search(tds[0].all_text())
            scripts = [_norm(x.all_text()) for x in _walk(tds[2]) if x.tag == "div" and "script" in x.cls()]
            kp_tabs = [x for x in _walk(tds[2]) if x.tag == "table" and "kp" in x.cls()]
            rows.append({"label": label, "start": float(m.group(1)) if m else None, "scripts": scripts, "kp": bool(kp_tabs),
                         "row_audio": any(x.tag == "audio" for x in _walk(tds[1]))})
        starts = [r["start"] for r in rows]
        mono = all(s is not None for s in starts) and all(a <= b + 1e-6 for a, b in zip(starts, starts[1:]))
        put(f"{lv}:script_rows_in_play_order", len(rows) >= 5 and mono, f"rows={len(rows)} monotonic_start={mono}")
        lab = [r["label"] for r in rows]
        prev_i = next((i for i, l in enumerate(lab) if re.match(r"^Preview(\s*\(.*\))?$", l)), None)
        fs_i = next((i for i, l in enumerate(lab) if l.lower().startswith("full story part") or l.lower().startswith("full_story")), None)
        prev_ok = prev_i is not None and bool(rows[prev_i]["scripts"]) and any(rows[prev_i]["scripts"])
        fs_ok = fs_i is not None and bool(rows[fs_i]["scripts"]) and any(rows[fs_i]["scripts"])
        put(f"{lv}:preview_and_full_story_scripts", prev_ok and fs_ok and prev_i < fs_i,
            f"preview_row={prev_i} full_story_row={fs_i}")
        cm = [r for r in rows if re.match(r"^Comment\s*\d", r["label"])]
        put(f"{lv}:comment_scripts", all(any(r["scripts"]) for r in cm), f"comment_rows={len(cm)}")
        # C3 Key Phrases
        kps = []
        for tab in [n for n in nodes if n.tag == "table" and "kp" in n.cls()]:
            for tr in [x for x in _walk(tab) if x.tag == "tr"]:
                tds = [c for c in tr.children if c.tag == "td"]
                if len(tds) >= 2:
                    kps.append([_norm(c.all_text()) for c in tds])
        kp_ok = len(kps) >= 1 and all(r[0] and r[1] for r in kps)
        if lv == "Standard":
            kp_ok = kp_ok and all(_JP_RE.search(r[1]) for r in kps)
        put(f"{lv}:key_phrases_en_ja", kp_ok, f"kp_rows={len(kps)}")
        # C4 内部情報・効果音をスクリプトに含めない
        leaks = [s for r in rows for s in r["scripts"] if _INTERNAL_RE.search(s)]
        raw_labels = [r["label"] for r in rows if _RAW_ID_RE.match(r["label"])]
        sfx_scripts = [r["label"] for r in rows if _SFX_LABEL_RE.match(r["label"]) and any(r["scripts"])]
        put(f"{lv}:no_internal_info_in_script", not leaks and not raw_labels and not sfx_scripts,
            f"leaks={leaks[:2]} raw_id_labels={raw_labels[:2]} sfx_with_script={sfx_scripts[:2]}")
        # 範囲末尾(補助表示位置判定用)
        last_level_end = max(last_level_end, max((n.idx for n in nodes), default=0))
        lvl_report[lv] = rep
    # C5 補助表示(ASR警告等)は全レベル節の後ろ
    aux_nodes = [n for n in flat if _AUX_MARK_RE.search(" ".join([n.attrs.get("id", "")] + ["".join(x for x in n.text if isinstance(x, str))]))
                 and n.tag in ("h1", "h2", "h3", "h4", "summary", "section", "details", "p", "div", "span")]
    h2_levels_end = last_level_end
    bad_aux = [n.tag for n in aux_nodes if n.idx <= h2_levels_end and n.tag in ("h1", "h2", "h3", "summary", "section", "details")]
    put("asr_warning_is_auxiliary_after_levels", not bad_aux, f"aux_nodes={len(aux_nodes)} misplaced={bad_aux[:3]}")
    # C6 file:scheme / レベルラベル漏れ
    visible = re.sub(r"<[^>]+>", " ", html_text)
    put("no_file_scheme", not ("file:///" in html_text or "C:\\" in html_text or "C:/" in html_text))
    put("no_A2_B1_label", not re.search(r"\(A2\)|\(B1\)|B1B", visible))
    # C7 音声実在
    if base_dir:
        miss = [n.attrs.get("src") for n in flat if n.tag == "audio" and n.attrs.get("src")
                and not re.match(r"https?://", n.attrs["src"]) and not os.path.exists(os.path.join(base_dir, n.attrs["src"]))]
        put("audio_files_exist", not miss, f"missing={miss[:3]} total_audio={sum(1 for n in flat if n.tag == 'audio')}")
    overall = "PASS" if all(c["ok"] for c in checks.values()) else "FAIL"
    return {"overall": overall, "checks": checks, "levels_checked": list(levels)}


def _in_kp_table(node) -> bool:
    p = node.parent
    while p is not None:
        if p.tag == "table" and "kp" in p.cls():
            return True
        p = p.parent
    return False


def _walk(node):
    for c in node.children:
        yield c
        yield from _walk(c)


def check_file(path: str, levels=("Standard", "Advanced"), out: str | None = None) -> dict:
    with open(path, encoding="utf-8") as f:
        txt = f.read()
    res = check_page(txt, base_dir=os.path.dirname(os.path.abspath(path)), levels=levels)
    res["page"] = path.replace("\\", "/")
    if out:
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2)
    return res
