"""LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 委任_11(B-wire、ユーザー原文_02 §3・§4): 試聴・確認フォーム(報告資料)の共通表示部品。

ユーザー原文_02: 「報告資料」=現在の試聴・確認フォーム(`user_test/`配下の試聴ページ)。全Family・全レベル共通で次を表示する。
  (1) Chunk境界 `⏸`: 実際にChunk分割した位置(chunk plan記録)にだけ。分割方法・語数・追加ポーズは変更しない。
  (2) Local Rewrite(LR): 変更箇所を赤色、変更前/変更後の英文と適用範囲を注記。
  (3) Fallback: 適用されたテキスト全体を濃い青色、適用Style名と適用範囲を注記。
  LR+Fallbackが同じ区間: 青の中に赤が入り、注記は双方を別行で示す。「何が発動したか/何が変わったか/どこに適用されたか」の3点。
  制作本文・TTS入力・ASR正解・Style Prompt・KP学習用表示・study_textには一切混入しない(表示は試聴ページHTMLの装飾と注記のみ)。

設計:
  - 入力は`er129.build_lr_ledger`(採用take解決・LR差分)が唯一(独自の採用attempt規則を持たない)。カード生成は`er131._card`(最終Human報告資料と同一の描画根拠)を部品として流用する。
  - 装飾は`<span class='rpt-lr' style=...>`/`<span class='rpt-fb' style=...>`で本文テキストを変えない(textContentは装飾なしと同一)。注記は`div.script`の外の兄弟`div.rpt-notes`。
    ⏸は既存の`chunk-mark`機構(共通`er_user_listening_page_common_01`)を使う。色は`style`属性で持つのでページ固有CSSに依存しない。
  - 位置が特定できない場合は推定位置に出さず、注記だけを出す(誤った位置に色を付けない)。表示専用でrun dirは読み取りのみ・API 0。
"""
from __future__ import annotations

import html
import os
import re
from typing import Any

import er129_lr_display_reflection_01 as er129
import er131_final_human_report_01 as er131

RED = "#c00000"
BLUE = "#0a2a6b"   # 濃い青
LR_STYLE = f"color:{RED};font-weight:700;text-decoration:underline"
FB_STYLE = f"color:{BLUE};font-weight:600"
LR_BEFORE_STYLE = f"color:{RED};text-decoration:line-through"
CLASS_LR, CLASS_FB, CLASS_NOTES = "rpt-lr", "rpt-fb", "rpt-notes"


def _esc(s: Any) -> str:
    return html.escape(str(s if s is not None else ""), quote=True)


def legend_html() -> str:
    """凡例1行(試聴ページに⏸/赤/青のいずれかがある場合だけページ側が挿入する)。"""
    return ("<p class='rpt-legend' style='font-size:12px;color:#444;margin:6px 0'>"
            "表示の見方: &#9208;=音声のChunk分割位置 / "
            f"<span style='{LR_STYLE}'>赤</span>=Local Rewrite(変更箇所。変更前後の英文は下の注記) / "
            f"<span style='{FB_STYLE}'>濃い青</span>=Fallback(適用範囲全体。Style名は下の注記)</p>")


# ----------------------------------------------------------------------------- 台帳→イベント
def load_events(run_dir: str, level: str, *, level_dir: str | None = None, results_path: str | None = None) -> dict:
    """{clip_id: card}。LR採用(最終音声に反映)またはFallback採用のclipだけ(er131のcard形)。台帳を作れない/結果が無い=空(マーク無し)。
    子chunkにイベントがある連結親は除く(子単位で表示)。"""
    ld = level_dir or os.path.join(run_dir, level)
    rp = results_path or os.path.join(ld, "audit", "tts_generation_results.json")
    if not os.path.exists(rp):
        return {}
    ledger = er129.build_lr_ledger(run_dir, level, results_path=rp, level_dir=ld, only_events=True)
    entries = er131.load_entries(run_dir, level, rp, ld)
    parents_with_child_event = {c.get("chunk_parent") for c in ledger["clips"] if c.get("chunk_parent")}
    out = {}
    for clip in ledger["clips"]:
        cid = clip["clip_id"]
        if cid in parents_with_child_event:
            continue
        card = er131._card(clip, entries.get(cid, {}))
        if card.get("fixed"):
            continue
        lr_on = bool(card.get("lr") and card["lr"].get("applied"))
        fb_on = card.get("fb_state") == "USED"
        if lr_on or fb_on:
            card["_lr_on"], card["_fb_on"] = lr_on, fb_on
            out[cid] = card
    return out


def _spans(text: str, spans: list, cls: str, style: str) -> str:
    """textの[(s,e)]をstyle付きspanで包む(span外はそのまま。素の文字列は変えない)。"""
    out, pos = [], 0
    for s, e_ in sorted(spans):
        if s < pos:
            continue
        out.append(_esc(text[pos:s]))
        out.append(f"<span class='{cls}' style='{style}'>{_esc(text[s:e_])}</span>")
        pos = e_
    out.append(_esc(text[pos:]))
    return "".join(out)


def _nat(cid: str) -> list:
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", cid)]


def select(events: dict, *, ids=(), block: str | None = None) -> list:
    """行/ブロックに属するイベント(idの完全一致、またはblockそのもの・blockの子chunk `<block>_k<N>`)。自然順。"""
    out = []
    for cid in sorted(events, key=_nat):
        if cid in ids or (block is not None and (cid == block or re.fullmatch(re.escape(block) + r"_k\d+", cid))):
            out.append(events[cid])
    return out


def range_label(card: dict) -> str:
    cid = card["id"]
    m = re.fullmatch(r"full_story_part(\d+)(?:_c(\d+))?(?:_k(\d+))?", cid)
    if m:
        lab = f"Full Story Part {m.group(1)}"
        if m.group(2):
            lab += f" の clip {m.group(2)}"
        if m.group(3):
            lab += f" の Chunk {m.group(3)}"
        return lab
    m = re.fullmatch(r"kp(\d+)_(.+)", cid)
    if m:
        sub = {"en": "英語", "explanation": "英語での解説", "explanation_en": "英語での解説", "japanese_meaning": "日本語の意味", "phrase_repeat": "英語(繰り返し)"}.get(m.group(2), m.group(2))
        return f"Key Phrase {m.group(1)} {sub}"
    m = re.fullmatch(r"comment_(\d+)", cid)
    if m:
        return f"Comment {m.group(1)}"
    return {"topic_intro": "Topic intro", "preview": "Preview", "in_one_line": "In One Line", "japanese_title": "日本語タイトル"}.get(cid, cid)


# ----------------------------------------------------------------------------- 本文中の位置
_TRAIL = set(".,;:!?\"'”’)]」』…—-")
_LEAD = set("\"'“‘([「『")


def _locate(text: str, clip_text: str) -> tuple | None:
    """clip本文のtext内範囲(start, end, 先頭token index)。曲引用符・句読点・空白差・数詞/数字の差に依存しないtoken列の連続一致(er129.tokensと同じ正規化)で特定する。
    見つからない(一致が無い/複数ある)=None(推定位置には色を付けない)。範囲は最初のtokenの手前の開き引用符・最後のtokenの後の句読点/閉じ引用符までを含める。"""
    if not clip_text or not clip_text.strip():
        return None
    tt, ct = er129.tokens(text), er129.tokens(clip_text)
    if not ct:
        return None
    hay, needle = [t[0] for t in tt], [t[0] for t in ct]
    hits = er129._find_all(hay, needle)
    if len(hits) != 1:
        return None
    k0 = hits[0]
    s, e_ = tt[k0][1], tt[k0 + len(needle) - 1][2]
    while s > 0 and text[s - 1] in _LEAD:
        s -= 1
    while e_ < len(text) and text[e_] in _TRAIL:
        e_ += 1
    return s, e_, k0


def build_marks(text: str, cards: list, whole: bool = False) -> dict:
    """表示本文textに対するマーク。{red:[(s,e)], blue:[(s,e)], notes_html:str, unlocated:[card id]}。cards=select()の結果。
    cardsが空=notes_html空・red/blue空(装飾なし)。whole=True: このtextが当該clip1つ分そのもの(コメント・Preview・KPセル等)。Fallbackの青はtext全体
    (表示用の訳など、TTS入力と文字列が異なる表示でも範囲は表示全体=clip全体)。LRの赤は変更後語句をtoken位置で特定できた場合だけ。"""
    red, blue, notes, unlocated = [], [], [], []
    text = text or ""
    ttoks = er129.tokens(text)
    for c in cards:
        loc = _locate(text, c.get("text") or "")
        rng = (0, len(text)) if (whole and text) else ((loc[0], loc[1]) if loc else None)
        label = _esc(range_label(c))
        full = bool(rng) and rng[0] == 0 and rng[1] >= len(text.rstrip())
        where = ("この行の本文全体" if full else "本文中の該当箇所(色付き部分)") if rng else "本文中の位置を特定できません(推定位置には色を付けません)"
        if not rng:
            unlocated.append(c["id"])
        lr = c.get("lr") if c.get("_lr_on") else None
        if lr:
            ops = lr.get("ops") or []
            after = lr["after"]
            k0 = loc[2] if loc else (0 if (whole and [t[0] for t in ttoks] == [t[0] for t in er129.tokens(after)]) else None)
            if k0 is not None:
                atoks = er129.tokens(after)
                # opのafter span(after内の文字範囲)→after token index→表示token index
                for o in ops:
                    sp = o.get("after_span")
                    if not sp:
                        continue
                    j1 = next((i for i, t in enumerate(atoks) if t[1] == sp[0]), None)
                    j2 = next((i for i, t in enumerate(atoks) if t[2] == sp[1]), None)
                    if j1 is None or j2 is None or k0 + j2 >= len(ttoks):
                        continue
                    red.append((ttoks[k0 + j1][1], ttoks[k0 + j2][2]))
            before_spans = [o["before_span"] for o in ops if o.get("before_span")]
            changes = " / ".join(f"{_esc(o.get('before_text') or '(なし)')} → {_esc(o.get('after_text') or '(削除)')}" for o in ops)
            before_html = _spans(lr["before"], before_spans, "rpt-lr-before", LR_BEFORE_STYLE)
            after_html = _spans(after, [o["after_span"] for o in ops if o.get("after_span")], CLASS_LR, LR_STYLE)
            notes.append(
                f"<div class='rpt-note rpt-note-lr' style='color:{RED};margin:2px 0'><b>Local Rewrite 適用</b>(範囲: {label}。{where})<br>"
                f"変更前: {before_html}<br>変更後: {after_html}<br>変更語句: {changes}</div>")
        if c.get("_fb_on") and c.get("fb"):
            if rng:
                blue.append(rng)
            f = c["fb"]
            human = "(個別承認の採用take)" if f.get("human") else ""
            notes.append(
                f"<div class='rpt-note rpt-note-fb' style='color:{BLUE};margin:2px 0'><b>Fallback 適用</b>(範囲: {label}。{where})<br>"
                f"適用Style: {_esc(f['style'])}{human} / 切替元Style: {_esc(f['from'])}</div>")
    html_notes = f"<div class='{CLASS_NOTES}' style='font-size:12px;margin:2px 0 8px'>" + "".join(notes) + "</div>" if notes else ""
    return {"red": sorted(set(red)), "blue": sorted(set(blue)), "notes_html": html_notes, "unlocated": unlocated}


def marks_for(events: dict, text: str, *, ids=(), block: str | None = None, whole: bool = False) -> dict | None:
    """(events, 表示本文, 行のclip ids/block) → マーク(無ければNone=従来描画とバイト同一)。"""
    cards = select(events, ids=ids, block=block)
    if not cards:
        return None
    return build_marks(text, cards, whole=whole)


def notes_of(marks_iter) -> str:
    """複数マーク(KP表のセル毎)の注記HTMLを連結(Noneは無視)。無ければ空文字。"""
    return "".join((m or {}).get("notes_html", "") for m in marks_iter)


def cell_html(text: str, marks: dict | None) -> str:
    """KP表のセル等、台本div以外の短い文字列にred/blueを適用したHTML(marksがNone=esc(text)のみ)。"""
    import er_user_listening_page_common_01 as uc
    if not marks:
        return uc.esc(text)
    return uc.render_marked_script(text, None, [], "", marks["red"], marks["blue"])
