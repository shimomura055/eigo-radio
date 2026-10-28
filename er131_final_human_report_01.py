"""LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 委任_09(Phase B / B5): 最終Human報告用資料 生成器(読取専用CLI、未配線)。

目的(ユーザー正式決定、`docs/pm/delegation_log/2026-10-28_LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01_USER.md` §2・§6):
  TTS・ASR・組立の完了後に、ユーザーが最終確認する資料(Local Rewrite=赤、Fallback=濃い青、注記付き)を1 run=1資料(Std/Adv別HTML)で作る。
  赤・青・注記・変更履歴は、この資料にだけ存在する。制作スクリプト・TTS入力・ASR正解・学習者向け公開ページ・KP/文法表示・Style Promptには出さない。

性質(厳守):
  - 読取専用。入力は`er129_lr_display_reflection_01.build_lr_ledger`(+採用take解決`resolve_adopted_take`)が**唯一**。独自の読取規則を持たない
    (INTEGRATION_01 F-3)。run dirは書き換えない。書込みは出力先(既定`final_human_report/`、`user_test/`・`er0*_output/`・run dir配下は拒否)のみ。
  - **未配線**: どのProductionコード・公開ページ生成器・TTS・ASR・E2E_STAGESからもimportされない(testで固定)。有料API 0・LLMなし。
  - 既存Family(A/B/C等)はFallback有無のみ/記録不足で表示不可を明記(音声方式は不変)。
CLI: python er131_final_human_report_01.py --run <run dir> --family X|Y|Z|A|B|C [--level a2|b1b|both] [--slug S] [--out-root DIR]
"""
from __future__ import annotations

import argparse
import datetime
import html
import json
import os
import re
import sys
from typing import Any

import er129_lr_display_reflection_01 as er129   # 唯一の読取入力(採用take解決・LR差分・三者一致)

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT_ROOT = os.path.join(REPO_ROOT, "final_human_report")

LEVEL_FILE = {"a2": "standard.html", "b1b": "advanced.html"}
LEVEL_LABEL = {"a2": "Standard", "b1b": "Advanced"}

# ----------------------------------------------------------------------------- 混入防止の識別子(この資料の専用語。他へ出たらNG)
FHR_CLASS_PREFIX = "fhr-"
FHR_MARKER = "<!--FINAL_HUMAN_REPORT-->"
LABEL_LR_NOTE = "Local Rewrite発動(最終採用音声に反映)"
LABEL_FB_NOTE = "最終採用音声はFallback Style"
LABEL_FB_FROM = "切替元Style:"
STYLE_JA = {
    er129.KIND_MINIMAL_EN: "英語短文Style(Minimal)",
    er129.KIND_MINIMAL_JA: "日本語短文Style(Minimal)",
    er129.KIND_ENGLISH_LOCK: "ENGLISH_LOCK",
    er129.KIND_LEGACY_DIALOGUE: "従来Dialogue Style(Z Dialogue切替)",
}
# 公開HTML・TTS入力・ASR正解・Style Prompt・KP表示・study_textに0件でなければならない語(厳密)
FHR_TOKENS = (
    FHR_CLASS_PREFIX, "FINAL_HUMAN_REPORT", "LR_REWRITTEN", "LR_APPLIED", "FALLBACK_APPLIED",
    LABEL_LR_NOTE, LABEL_FB_NOTE, LABEL_FB_FROM, STYLE_JA[er129.KIND_MINIMAL_EN], STYLE_JA[er129.KIND_MINIMAL_JA], STYLE_JA[er129.KIND_LEGACY_DIALOGUE],
)
# 既存の公開ページ注記(Z公開ページのLR注記、INTEGRATION F-9で撤去予定=B3)。FHR資料の語ではなく、既存の未是正混入として別集計する
LEGACY_PUBLIC_NOTE_TOKENS = ("Local Rewrite採用(音声は原稿から変更",)
FORBIDDEN_OUT_COMPONENTS = ("user_test",)
FORBIDDEN_IMPORT_PREFIXES = ("er019_family_x_listening_page", "er063_family_z_audio", "er_user_listening_page_common", "er121_family_y", "er003_", "er127_",
                             "er120_part2_wiring", "er128_kp_", "er078_")


# ----------------------------------------------------------------------------- 出力先制約(層3)
def check_out_dir(out_dir: str, run_dir: str | None = None) -> str | None:
    """出力先として不可なら理由文字列を返す(OKならNone)。`user_test/`配下、`er<数字>_output`配下、run dir配下は書かない。"""
    p = os.path.normcase(os.path.abspath(out_dir))
    parts = re.split(r"[\\/]+", p)
    for part in parts:
        if part in FORBIDDEN_OUT_COMPONENTS:
            return f"出力先に`{part}/`は使えません(学習者向け公開領域): {out_dir}"
        if re.fullmatch(r"er\d+(_[a-z0-9]+)*_output", part) or re.fullmatch(r"er\d+_output", part):
            return f"出力先に制作成果物dir(`{part}`)は使えません: {out_dir}"
    if run_dir:
        r = os.path.normcase(os.path.abspath(run_dir))
        if p == r or p.startswith(r + os.sep):
            return f"出力先がrun dir配下です(run dirは書き換えません): {out_dir}"
    return None


# ----------------------------------------------------------------------------- 読取(er129のみ)
_ROLE_JA = {
    "TOPIC_INTRO": "トピック紹介(英語)", "FULL_STORY": "本文", "COMMENT": "コメント", "PREVIEW": "Preview", "IN_ONE_LINE": "in_one_line",
    "KEY_PHRASE": "Key Phrase英語", "KP_EXPL_EN": "Key Phrase英語解説", "english": "Key Phrase英語", "japanese_meaning": "Key Phrase日本語の意味",
}


def role_label(clip: dict, clip_id: str) -> str:
    r = clip.get("role") or ""
    cid = clip_id
    if r in _ROLE_JA:
        base = _ROLE_JA[r]
    elif cid.startswith("topic_intro"):
        base = "トピック紹介"
    elif cid.startswith("japanese_title"):
        base = "日本語タイトル"
    elif cid.startswith("preview"):
        base = "Preview"
    elif cid.startswith("comment"):
        base = "コメント"
    elif cid.startswith("in_one_line"):
        base = "in_one_line"
    elif cid.startswith("full_story") or cid.startswith("y_voice"):
        base = "本文"
    elif cid.startswith("y_"):
        base = "Y 導入/結び"
    elif re.match(r"kp\d+_en", cid):
        base = "Key Phrase英語"
    elif "explanation" in cid:
        base = "Key Phrase英語解説"
    elif "japanese" in cid:
        base = "Key Phrase日本語の意味"
    else:
        base = r or "その他"
    if r == "FULL_STORY" and "dialogue" in cid:
        base = "本文(Dialogue)"
    return base


def load_entries(run_dir: str, level: str, results_path: str | None = None, level_dir: str | None = None) -> dict:
    ld = level_dir or os.path.join(run_dir, level)
    rp = results_path or os.path.join(ld, "audit", "tts_generation_results.json")
    res = er129._jl(er129._abs(rp)) or {}
    return {sid: e for sid, e, _ in er129._iter_entries(res)}


def build_model(run_dir: str, level: str, family: str, *, results_path: str | None = None, level_dir: str | None = None) -> dict:
    """1 run×level の資料モデル。X/Y/Z=er129の台帳(全clip)、A/B/C=Fallback有無のみ(記録形式不足は表示不可)。"""
    entries = load_entries(run_dir, level, results_path, level_dir)
    if family.upper() in ("A", "B", "C", "LEGACY"):
        return _legacy_model(run_dir, level, family, entries, results_path)
    ledger = er129.build_lr_ledger(run_dir, level, results_path=results_path, level_dir=level_dir, only_events=False)
    parents = {c.get("chunk_parent") for c in ledger["clips"] if c.get("chunk_parent")}
    cards = []
    for clip in ledger["clips"]:
        cid = clip["clip_id"]
        if cid in parents:
            continue                      # 連結親(子chunkの集合)。子単位で表示する
        e = entries.get(cid, {})
        cards.append(_card(clip, e))
    return {"family": family.upper(), "level": level, "run_dir": run_dir, "ledger_results_sha": ledger.get("results_sha256"),
            "cards": cards, "parents_skipped": sorted(p for p in parents if p), "legacy": False}


def _style_label(take: dict, fb: dict) -> str:
    kind = fb.get("kind") or take.get("kind")
    base = STYLE_JA.get(kind, kind or "記録なし")
    name = take.get("style_name")
    sha = take.get("style_sha")
    extra = []
    if name and name not in (kind, "ROLE_STYLE") and not re.search(r"[\\/]", str(name)):
        extra.append(str(name))
    if sha:
        extra.append("sha " + str(sha)[:8])
    return base + (" / " + " ".join(extra) if extra else "")


def _from_label(fb: dict) -> str:
    f = fb.get("from_style") or "ROLE_STYLE"
    return "通常Style(Role Style" + (f.replace("ROLE_STYLE", "")) + ")" if f.startswith("ROLE_STYLE") else str(f)


def _card(clip: dict, entry: dict) -> dict:
    cid = clip["clip_id"]
    take = clip.get("adopted_take") or {}
    fb = clip.get("fallback") or {}
    lr = clip.get("lr")
    warnings = list(clip.get("warnings") or [])
    text = ""
    lr_view = None
    if lr:
        text = lr["after"] if lr.get("adopted_in_final") else (entry.get("canonical_text") if isinstance(entry.get("canonical_text"), str) else lr["before"])
        if lr.get("adopted_in_final"):
            ops = clip.get("_ops") or []
            lr_view = {"before": lr["before"], "after": lr["after"], "ops": _op_spans(lr["before"], lr["after"], ops),
                       "reason": lr.get("reason"), "reason_source": lr.get("source"), "applied": True}
        else:
            lr_view = {"before": lr["before"], "after": lr["after"], "ops": [], "reason": lr.get("reason"), "applied": False,
                       "superseded_by_human": True}
    else:
        text = entry.get("canonical_text") if isinstance(entry.get("canonical_text"), str) and entry.get("canonical_text").strip() else (entry.get("text") or "")
    fixed = take.get("source") == "fixed_asset"
    state = fb.get("state")
    est = str(entry.get("status") or "")
    skipped = est.startswith("SKIPPED") or est == "CHUNKS_NOT_ALL_VALIDATED"
    if skipped:                       # このrunでTTS未実行(evidence runの対象外clip等)。記録欠落ではない
        state = "SKIPPED"
        warnings = [w for w in warnings if not w.startswith("RECORD_INCOMPLETE")]
    fb_view = None
    if state == "USED":
        fb_view = {"style": _style_label(take, fb), "from": _from_label(fb), "slot": take.get("slot"),
                   "range": cid if not clip.get("chunk_parent") else f"{clip['chunk_parent']} の chunk {cid}",
                   "human": take.get("source") == "human_approval", "kind": fb.get("kind")}
    history = []
    if entry.get("fallback_used") and state == "NOT_USED":
        history.append("元の記録にFallback Styleの試行が残っていますが、最終採用音声のStyleではないため、Fallbackとして表示しません。")
    if lr_view and lr_view.get("applied") and not fixed:
        history.append("LR前の元ブロックの試行は不採用。最終採用音声はLR後ブロックの採用take。")
    if lr_view and lr_view.get("superseded_by_human"):
        history.append("LR案は選ばれましたが、ユーザー個別承認で「LR前の原文音声」を採用したため、最終音声にはLRは反映されていません(赤は付けません)。")
    gaps = []
    if any(w.startswith("STYLE_RECORD_CONFLICT") for w in warnings):
        history = [x for x in history if not x.startswith("元の記録にFallback")]
        gaps.append("記録衝突(採用attemptはrole Style): 保存記録の一部(entry直下)はFallbackを示しますが、採用attemptの送信時記録はrole Styleです。"
                    "送信時記録を正として「Fallback 発動なし」と表示します(青にはしません)。")
    if state == "UNKNOWN":
        gaps.append("最終採用音声のStyle(Fallbackか通常Styleか)を保存記録から確定できません。断定しません。")
    if any(w.startswith("RECORD_MISMATCH") for w in warnings):
        gaps.append("採用takeの記録とBlockProgressの記録が一致しません(記録不一致)。")
    if lr_view and lr_view.get("applied") and lr_view.get("reason") is None:
        gaps.append("LRの変更理由は保存記録にありません(記録なし)。")
    return {"id": cid, "role": role_label(clip, cid), "chunk_parent": clip.get("chunk_parent"), "text": text, "fixed": fixed,
            "lr": lr_view, "fb_state": state, "fb": fb_view, "history": history, "gaps": gaps,
            "skipped": skipped, "skip_status": est if skipped else None,
            "verdict": clip.get("verdict"), "parity": (clip.get("text_parity") or {}).get("verdict"),
            "overlap": {k: (v or {}).get("status") for k, v in (clip.get("overlap") or {}).items()} if clip.get("overlap") else None,
            "how": take.get("how"), "text_empty": not (text or "").strip()}


def _op_spans(before: str, after: str, ops: list) -> list:
    tb, ta = er129.tokens(before), er129.tokens(after)
    out = []
    for op in ops:
        b = (tb[op["core_i1"]][1], tb[op["core_i2"] - 1][2]) if op["core_i2"] > op["core_i1"] else None
        a = (ta[op["core_j1"]][1], ta[op["core_j2"] - 1][2]) if op["core_j2"] > op["core_j1"] else None
        out.append({"before_span": b, "after_span": a, "before_text": op.get("core_before_text"), "after_text": op.get("core_after_text"), "kind": op.get("kind")})
    return out


def _legacy_model(run_dir: str, level: str, family: str, entries: dict, results_path: str | None) -> dict:
    """A/B/C等: 保存形が`attempts_log`+`fallback_used`を持つ範囲でFallback有無のみ。LRは記録形式なし。無ければ表示不可(音声方式は不変)。"""
    cards = []
    has_log = any(isinstance(e.get("attempts_log"), list) for e in entries.values())
    for sid, e in entries.items():
        if isinstance(e.get("attempts_log"), list) and "fallback_used" in e:
            used = bool(e.get("fallback_used"))
            cards.append({"id": sid, "role": role_label({}, sid), "chunk_parent": None, "text": e.get("canonical_text") or e.get("text") or "", "fixed": False,
                          "lr": None, "fb_state": "USED" if used else "NOT_USED",
                          "fb": {"style": "記録なし(既存Familyは有無のみ)", "from": "記録なし", "slot": None, "range": sid, "human": False, "kind": None} if used else None,
                          "history": [], "gaps": ["採用attemptのStyle名は既存Familyの保存形に無いため「記録なし」。entry単位の`fallback_used`のみを表示します。"] if used else [],
                          "verdict": None, "parity": None, "overlap": None, "how": "legacy:fallback_used", "text_empty": False})
        else:
            cards.append({"id": sid, "role": role_label({}, sid), "chunk_parent": None, "text": e.get("canonical_text") or e.get("text") or "", "fixed": False,
                          "lr": None, "fb_state": "UNREADABLE", "fb": None, "history": [], "gaps": ["表示不可: この音声の記録形式(attempts_log/fallback_used)が未対応です。"],
                          "verdict": None, "parity": None, "overlap": None, "how": None, "text_empty": False})
    return {"family": family.upper(), "level": level, "run_dir": run_dir, "cards": cards, "parents_skipped": [], "legacy": True,
            "legacy_readable": has_log}


# ----------------------------------------------------------------------------- 描画
CSS = """:root{--lr:#c00000;--fb:#0a2a6b;--ink:#1d2430;--mut:#667085;--line:#d8dde6;--bg:#f6f7f9}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.8 -apple-system,"Segoe UI","Yu Gothic",Meiryo,sans-serif}
.wrap{max-width:900px;margin:0 auto;padding:24px 16px 80px}
h1{font-size:20px} h2{font-size:17px;margin:34px 0 8px;border-bottom:2px solid var(--line);padding-bottom:4px}
.card{background:#fff;border:1px solid var(--line);border-radius:8px;padding:12px 16px;margin:14px 0}
.meta{color:var(--mut);font-size:13px}
table{border-collapse:collapse;width:100%;font-size:13px} th,td{border:1px solid var(--line);padding:4px 8px;text-align:left;vertical-align:top} th{background:#eef1f6}
.fhr-chip{display:inline-block;font-size:12px;font-weight:700;border-radius:4px;padding:0 6px;margin-right:6px;border:1px solid}
.fhr-chip-lr{color:var(--lr);border-color:var(--lr);background:#fff0f0}
.fhr-chip-fb{color:var(--fb);border-color:var(--fb);background:#eef3ff}
.fhr-chip-none{color:var(--mut);border-color:var(--line);background:#fafafa}
.fhr-chip-gap{color:#7a4b00;border-color:#d8a200;background:#fff8e0}
.fhr-lr-after{color:var(--lr);font-weight:700;text-decoration:underline double}
.fhr-lr-before{color:var(--lr);text-decoration:line-through}
.fhr-fb-block{color:var(--fb);border-left:5px solid var(--fb);padding:2px 0 2px 10px;margin:8px 0}
.fhr-fb-note{color:var(--fb);font-size:13px}
.fhr-hist{color:#555;font-size:13px;background:#f3f4f6;border-radius:6px;padding:6px 10px;margin:8px 0}
.fhr-gap{background:#fff8e0;border:1px dashed #d8a200;border-radius:6px;padding:6px 10px;margin:8px 0;font-size:13px;color:#5c3b00}
.fhr-warnband{background:#fff8e0;border:2px solid #d8a200;border-radius:6px;padding:8px 12px;margin:12px 0;font-weight:700;color:#5c3b00}
"""


def _esc(s: Any) -> str:
    return html.escape(str(s if s is not None else ""), quote=True)


def _spans_html(text: str, spans: list, cls: str) -> str:
    """textの[(s,e)]をspanで包んで返す(span外はそのまま)。素の文字列は変えない(装飾除去で元と一致)。"""
    out, pos = [], 0
    for s, e in sorted(spans):
        if s < pos:
            continue
        out.append(_esc(text[pos:s]))
        out.append(f'<span class="{cls}">{_esc(text[s:e])}</span>')
        pos = e
    out.append(_esc(text[pos:]))
    return "".join(out)


def render_card(c: dict) -> str:
    h = ['<div class="card">']
    rng = f'{_esc(c["id"])}' + (f' / 親={_esc(c["chunk_parent"])}' if c.get("chunk_parent") else "")
    h.append(f'<div class="meta">{_esc(c["role"])} / {rng}</div>')
    chips = []
    lr = c.get("lr")
    st = c.get("fb_state")
    if c.get("fixed"):
        chips.append('<span class="fhr-chip fhr-chip-none">対象外(固定殻/固定MP3、TTS生成なし)</span>')
    else:
        if lr and lr.get("applied"):
            chips.append('<span class="fhr-chip fhr-chip-lr">LR</span>')
        elif lr and lr.get("superseded_by_human"):
            chips.append('<span class="fhr-chip fhr-chip-none">LR 最終音声に反映なし(人間承認)</span>')
        elif st not in ("UNREADABLE", "SKIPPED"):
            chips.append('<span class="fhr-chip fhr-chip-none">LR 発動なし</span>')
        elif st == "SKIPPED":
            pass
        else:
            chips.append('<span class="fhr-chip fhr-chip-gap">LR 記録形式なし</span>')
        if st == "USED":
            chips.append('<span class="fhr-chip fhr-chip-fb">Fallback</span>')
        elif st == "NOT_USED":
            chips.append('<span class="fhr-chip fhr-chip-none">Fallback 発動なし</span>')
        elif st == "UNKNOWN":
            chips.append('<span class="fhr-chip fhr-chip-gap">Fallback 記録なし</span>')
        elif st == "SKIPPED":
            chips.append(f'<span class="fhr-chip fhr-chip-none">TTS未実行(このrunの対象外: {_esc(c.get("skip_status"))})</span>')
        elif st == "NOT_ADOPTED":
            chips.append('<span class="fhr-chip fhr-chip-gap">採用なし(終端NG)</span>')
        elif st == "UNREADABLE":
            chips.append('<span class="fhr-chip fhr-chip-gap">記録なし(表示不可)</span>')
    h.append("<p>" + "".join(chips) + "</p>")
    text = c.get("text") or ""
    if c.get("text_empty") and not c.get("fixed"):
        h.append('<p class="meta">(この音声単位の本文は保存記録にありません)</p>')
    body = ""
    if lr and lr.get("applied"):
        after_spans = [o["after_span"] for o in lr["ops"] if o.get("after_span")]
        body = _spans_html(lr["after"], after_spans, "fhr-lr-after")
        h.append(f'<p><b>{LABEL_LR_NOTE}</b><br>変更後の英文(最終表示本文・TTS入力・ASR正解原稿で一致):<br>' + _wrap_fb(body, c) + "</p>")
        before_spans = [o["before_span"] for o in lr["ops"] if o.get("before_span")]
        h.append('<p class="meta">変更前: ' + _spans_html(lr["before"], before_spans, "fhr-lr-before") + "</p>")
        changes = " / ".join(f'{_esc(o.get("before_text") or "(なし)")} → {_esc(o.get("after_text") or "(削除)")}' for o in lr["ops"])
        h.append(f'<p class="meta">変更語句: {changes}({len(lr["ops"])}箇所)。理由: ' + (_esc(lr["reason"]) if lr.get("reason") else '<span class="fhr-chip fhr-chip-gap">記録なし</span>') + "</p>")
    elif text.strip() and not c.get("fixed"):
        body = _esc(text)
        if st == "USED":
            h.append("<p><b>" + LABEL_FB_NOTE + "</b></p>" + _wrap_fb(body, c) + "")
        else:
            h.append(f"<p>{body}</p>")
    if lr and lr.get("superseded_by_human"):
        h.append('<p class="meta">LR案(最終音声には反映なし): <span style="text-decoration:line-through;color:#667085">' + _esc(lr["before"]) + "</span> → " + _esc(lr["after"]) + "</p>")
    for g in c.get("gaps") or []:
        label = "記録衝突" if g.startswith("記録衝突") else "記録なし"
        h.append(f'<div class="fhr-gap"><span class="fhr-chip fhr-chip-gap">{label}</span>{_esc(g)}</div>')
    if c.get("history"):
        h.append('<div class="fhr-hist"><b>実行履歴(最終採用とは別。色の意味なし)</b><br>' + "<br>".join(_esc(x) for x in c["history"]) + "</div>")
    if c.get("parity") or c.get("overlap"):
        ov = c.get("overlap") or {}
        h.append('<table><tr><th>照合</th><th>結果</th></tr>'
                 f'<tr><td>表示本文=TTS入力=ASR正解原稿</td><td>{_esc(c.get("parity") or "-")}</td></tr>'
                 f'<tr><td>確定内容との重なり(T1/T2/T3)</td><td>{_esc("/".join(str(ov.get(k) or "-") for k in ("T1", "T2", "T3")))}</td></tr></table>')
    h.append("</div>")
    return "\n".join(h)


def _fb_note(c: dict) -> str:
    f = c["fb"]
    human = "(ユーザー個別承認の採用take)" if f.get("human") else ""
    return (f'<div class="fhr-fb-note">{LABEL_FB_NOTE}: {_esc(f["style"])}{human} / {LABEL_FB_FROM} {_esc(f["from"])} → {_esc(f["style"])}'
            f' / 範囲: {_esc(f["range"])}' + (f" / slot {_esc(f['slot'])}" if f.get("slot") else "") + "</div>")


def _wrap_fb(body_html: str, c: dict) -> str:
    """Fallback採用clipは対象テキスト全体+注記を濃い青の塊にする(LRの赤語句はその内側に残る=重複表示)。"""
    if c.get("fb_state") != "USED":
        return body_html
    return f'<div class="fhr-fb-block">{body_html}{_fb_note(c)}</div>'


def summarize(model: dict) -> dict:
    cards = model["cards"]
    by_role: dict = {}
    for c in cards:
        r = by_role.setdefault(c["role"], {"units": 0, "lr": 0, "fb": 0, "gap": 0, "fixed": 0, "skipped": 0})
        r["units"] += 1
        if c.get("skipped"):
            r["skipped"] += 1
            continue
        if c.get("fixed"):
            r["fixed"] += 1
            continue
        if c.get("lr") and c["lr"].get("applied"):
            r["lr"] += 1
        if c.get("fb_state") == "USED":
            r["fb"] += 1
        if c.get("fb_state") in ("UNKNOWN", "UNREADABLE", "NOT_ADOPTED") or c.get("gaps"):
            r["gap"] += 1
    return {"units": len(cards), "lr": sum(r["lr"] for r in by_role.values()), "fb": sum(r["fb"] for r in by_role.values()),
            "skipped": sum(r["skipped"] for r in by_role.values()),
            "gap_units": sum(1 for c in cards if c.get("fb_state") in ("UNKNOWN", "UNREADABLE", "NOT_ADOPTED")), "by_role": by_role}


def render_report(model: dict, *, slug: str, run_name: str, date: str) -> str:
    s = summarize(model)
    lv = LEVEL_LABEL.get(model["level"], model["level"])
    h = ["<!doctype html>", '<html lang="ja"><head><meta charset="utf-8">', '<meta name="viewport" content="width=device-width,initial-scale=1">',
         '<meta name="robots" content="noindex,nofollow">', f"<title>最終Human報告用資料 {_esc(slug)} {lv}</title>", FHR_MARKER, f"<style>{CSS}</style></head><body><div class=\"wrap\">",
         f'<h1>最終Human報告用資料: {_esc(slug)} / {lv}<br><span class="meta">Family {_esc(model["family"])} / run={_esc(run_name)} / 作成日 {_esc(date)}。'
         "TTS・ASR・組立の完了後にだけ作る確認資料です。学習者向けページではなく、この資料の注記は読み上げ対象ではありません。</span></h1>"]
    h.append('<div class="card"><b>凡例</b><br>'
             '<span class="fhr-chip fhr-chip-lr">LR</span>Local Rewrite(英文の言い換え)。変更後=<span class="fhr-lr-after">赤・太字・二重下線</span> / 変更前=<span class="fhr-lr-before">赤・取消線</span><br>'
             '<span class="fhr-chip fhr-chip-fb">Fallback</span><span style="color:var(--fb)">対象テキスト全体と注記を濃い青</span>(左に青い太線)<br>'
             '<span class="fhr-chip fhr-chip-none">発動なし</span>灰色。最終採用に影響しない実行履歴は灰色の枠(色の意味を持たない)<br>'
             '<span class="fhr-chip fhr-chip-gap">記録なし</span>保存記録が足りず断定できない項目。推測で埋めずそのまま明示します<br>'
             "色が見えにくい場合も、文字ラベル(LR / Fallback / 発動なし / 記録なし)で区別できます。時刻・cooldown・pathは表示しません。</div>")
    if model.get("legacy"):
        h.append('<div class="fhr-warnband">既存Family(A/B/C等)の資料: Fallbackの有無のみ表示可能です(Style名・LRは記録形式がなく「記録なし」)。音声方式は変更していません。'
                 + ("" if model.get("legacy_readable") else " このrunは記録形式が未対応のため表示不可です。") + "</div>")
    if s["gap_units"]:
        h.append(f'<div class="fhr-warnband">記録なし/採用なしの音声単位が{s["gap_units"]}件あります。該当カードの「記録なし」を確認してください(推測では埋めていません)。</div>')
    h.append(f'<h2>0. 要約表(音声単位 {s["units"]} 件 / LR {s["lr"]} 件 / Fallback {s["fb"]} 件 / TTS未実行 {s["skipped"]} 件)</h2><table><tr><th>Role</th><th>単位数</th><th>LR</th><th>Fallback</th><th>記録なし</th><th>対象外(固定)</th><th>TTS未実行</th></tr>')
    for role, r in s["by_role"].items():
        h.append(f'<tr><td>{_esc(role)}</td><td>{r["units"]}</td><td>{r["lr"] or "発動なし"}</td><td>{r["fb"] or "発動なし"}</td><td>{r["gap"] or 0}</td><td>{r["fixed"] or 0}</td><td>{r["skipped"] or 0}</td></tr>')
    h.append("</table>")
    if model.get("parents_skipped"):
        h.append('<p class="meta">連結親(子chunkの集合)は子chunk単位で表示: ' + _esc(", ".join(model["parents_skipped"])) + "</p>")
    h.append(f"<h2>1. 音声単位ごとの確認({lv})</h2>")
    for c in model["cards"]:
        h.append(render_card(c))
    h.append('<p class="meta">この資料は学習者向けページ・TTS入力・ASR正解原稿・Style Promptには使用しません。KP/文法の学習用表示は転載していません。</p>')
    h.append("</div></body></html>")
    return "\n".join(h)


# ----------------------------------------------------------------------------- 素の本文の復元(装飾除去で元と一致=層6)
def strip_decoration(card_html: str) -> str:
    t = re.sub(r"<[^>]+>", "", card_html)
    return html.unescape(t)


# ----------------------------------------------------------------------------- 混入検査(層4/5)
def find_tokens(text: str, tokens: tuple = FHR_TOKENS) -> list:
    return [t for t in tokens if t in (text or "")]


_RPT_NOTES_OPEN = re.compile(r"<div class=['\"]rpt-notes['\"][^>]*>")


def strip_listening_page_notes(page_html: str) -> str:
    """試聴ページ(er133、USER_02 §4)の注記ブロック`<div class='rpt-notes'>…</div>`(入れ子divを含む)を取り除く。
    試聴ページは報告資料として赤/濃青の⏸・span・注記(「Local Rewrite 適用」「Fallback 適用」「切替元Style:」等)を`div.script`の外に表示するのが承認済み仕様。"""
    out, pos = [], 0
    while True:
        m = _RPT_NOTES_OPEN.search(page_html, pos)
        if not m:
            out.append(page_html[pos:])
            break
        out.append(page_html[pos:m.start()])
        depth, i = 1, m.end()
        for t in re.finditer(r"<(/?)div\b[^>]*>", page_html[m.end():]):
            depth += -1 if t.group(1) else 1
            i = m.end() + t.end()
            if depth == 0:
                break
        pos = i
    return "".join(out)


def check_page_fhr_contamination(page_html: str) -> list:
    """公開pageに最終Human報告専用の語(class接頭辞`fhr-`・マーカー・内部コード・注記文言・Style名)が含まれたらNG。
    委任_15(B10) D5: 旧規則`fhr_color_pair`(赤#c00000+濃青#0a2a6b の併存=NG)は撤去。試聴ページのLR(赤)/Fallback(濃青)表示(USER_02 §4)と矛盾するため。
    試聴ページ注記ブロック`div.rpt-notes`内の注記文言は表示仕様として許容し、それ以外(本文・他領域)への注記文言・専用語の混入は従来どおりNG。"""
    return find_tokens(strip_listening_page_notes(page_html))


_TTS_TEXT_KEYS = {"text", "canonical_text", "audio_text_after", "tts_input", "expected_text", "asr_expected", "instruction_text", "text_before",
                  "canonical_text_before_local_rewrite", "rewritten_segment"}


def _walk_text_fields(o: Any, out: list, key: str = "") -> None:
    if isinstance(o, dict):
        for k, v in o.items():
            _walk_text_fields(v, out, k)
    elif isinstance(o, list):
        for v in o:
            _walk_text_fields(v, out, key)
    elif isinstance(o, str) and key in _TTS_TEXT_KEYS:
        out.append(o)


def scan_run_contamination(run_dir: str, level_dirs: tuple = ("a2", "b1b")) -> dict:
    """保存run内の「混入してはならない先」を走査して、FHR語の件数を返す(読取のみ)。
    categories: tts_input(tts_generation_results text系フィールド)/asr_expected(resolve_expected_text)/style_prompt(attempt json instruction_text)/
    kp_study(key_phrases・study_text・support)/scripts(parts.json・article.md・*_support_texts.json・script*.md)。"""
    res = {"tts_input": [0, 0], "asr_expected": [0, 0], "style_prompt": [0, 0], "kp_study": [0, 0], "scripts": [0, 0], "hits": []}

    def add(cat, text, where):
        res[cat][0] += 1
        h = find_tokens(text)
        if h:
            res[cat][1] += len(h)
            res["hits"].append({"cat": cat, "where": where, "tokens": h})

    for lv in level_dirs:
        ld = os.path.join(run_dir, lv)
        rp = os.path.join(ld, "audit", "tts_generation_results.json")
        r = er129._jl(rp)
        if r:
            fields: list = []
            _walk_text_fields(r, fields)
            for s in fields:
                add("tts_input", s, rp)
            for sid, e, _ in er129._iter_entries(r):
                ct = e.get("canonical_text") if isinstance(e.get("canonical_text"), str) else (e.get("text") or "")
                info = er129._lr_info(e, ct)       # ASR正解の唯一の参照点(er020.resolve_expected_text_after_local_rewrite)はer129経由
                exp = info["asr_expected"] if info else ct
                add("asr_expected", exp or "", f"{rp}#{sid}")
        for root, _d, files in os.walk(ld):
            for fn in files:
                p = os.path.join(root, fn)
                rel = os.path.relpath(p, ld).replace("\\", "/")
                if fn.endswith(".json") and "/attempts/" in "/" + rel:
                    d = er129._jl(p)
                    if d:
                        f2: list = []
                        _walk_text_fields(d, f2)
                        for s in f2:
                            add("style_prompt", s, p)
                elif fn in ("parts.json", "article.md") or fn.endswith("support_texts.json") or (fn.startswith("script") and fn.endswith(".md")):
                    add("scripts", _read(p), p)
    for sub in ("key_phrases", "study_text", "support"):
        d = os.path.join(run_dir, sub)
        if os.path.isdir(d):
            for root, _dd, files in os.walk(d):
                for fn in files:
                    if fn.endswith((".json", ".md", ".html", ".txt")):
                        add("kp_study", _read(os.path.join(root, fn)), os.path.join(root, fn))
    return res


def scan_public_html(dirs: list) -> dict:
    out = {"files": 0, "hits": [], "legacy_note_hits": []}
    for d in dirs:
        for root, _dd, files in os.walk(d):
            for fn in files:
                if fn.endswith(".html"):
                    p = os.path.join(root, fn)
                    t = _read(p)
                    out["files"] += 1
                    h = check_page_fhr_contamination(t)
                    if h:
                        out["hits"].append({"file": p, "tokens": h})
                    lh = find_tokens(t, LEGACY_PUBLIC_NOTE_TOKENS)
                    if lh:
                        out["legacy_note_hits"].append({"file": p, "tokens": lh})
    return out


def _read(p: str) -> str:
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


# ----------------------------------------------------------------------------- 生成(CLI本体)
def derive_slug(run_dir: str) -> str:
    base = os.path.basename(os.path.normpath(run_dir))
    parent = os.path.basename(os.path.dirname(os.path.normpath(run_dir)))
    if "__" in base:
        return base.split("__")[0]
    return parent


def _normrun(run_dir: str) -> tuple:
    base = os.path.basename(os.path.normpath(run_dir))
    return (base.split("__", 1)[1] if "__" in base else base)


def generate(run_dir: str, family: str, levels: tuple = ("a2", "b1b"), out_root: str | None = None, slug: str | None = None, date: str | None = None,
             results_paths: dict | None = None) -> list:
    """資料を書く。戻り値=書いたfileのリスト。出力先制約違反は例外(何も書かない)。run dirは読むだけ。"""
    out_root = out_root or DEFAULT_OUT_ROOT
    slug = slug or derive_slug(run_dir)
    run_name = _normrun(run_dir)
    out_dir = os.path.join(out_root, family.upper(), slug, run_name)
    why = check_out_dir(out_dir, run_dir)
    if why:
        raise PermissionError(why)
    date = date or datetime.date.today().isoformat()
    written = []
    for lv in levels:
        lvdir = os.path.join(run_dir, lv)
        rp = (results_paths or {}).get(lv)
        if not rp and not os.path.isfile(os.path.join(lvdir, "audit", "tts_generation_results.json")):
            continue
        model = build_model(run_dir, lv, family, results_path=rp)
        os.makedirs(out_dir, exist_ok=True)
        p = os.path.join(out_dir, LEVEL_FILE[lv])
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(render_report(model, slug=slug, run_name=run_name, date=date))
        written.append(p)
    return written


def write_index(out_root: str | None = None) -> str:
    """`final_human_report/index.html`(ユーザーの最終確認用の目次。noindex。学習者向けindexからはリンクしない)。"""
    out_root = out_root or DEFAULT_OUT_ROOT
    items = []
    for root, _d, files in os.walk(out_root):
        for fn in sorted(files):
            if fn in LEVEL_FILE.values():
                items.append(os.path.relpath(os.path.join(root, fn), out_root).replace("\\", "/"))
    items.sort()
    rows = "".join(f'<li><a href="{_esc(i)}">{_esc(i)}</a></li>' for i in items)
    p = os.path.join(out_root, "index.html")
    os.makedirs(out_root, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write('<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow">'
                f'<title>最終Human報告用資料 一覧</title>{FHR_MARKER}</head><body><h1>最終Human報告用資料 一覧</h1>'
                '<p>TTS・ASR・組立の完了後のユーザー最終確認資料です(学習者向けページではありません)。</p>'
                f"<ul>{rows}</ul></body></html>")
    return p


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(description="最終Human報告用資料(読取専用・未配線)")
    ap.add_argument("--run", required=True)
    ap.add_argument("--family", required=True, choices=["X", "Y", "Z", "A", "B", "C", "x", "y", "z", "a", "b", "c"])
    ap.add_argument("--level", default="both", choices=["a2", "b1b", "both"])
    ap.add_argument("--slug")
    ap.add_argument("--out-root")
    ap.add_argument("--date")
    a = ap.parse_args(argv)
    levels = ("a2", "b1b") if a.level == "both" else (a.level,)
    try:
        files = generate(a.run, a.family, levels, a.out_root, a.slug, a.date)
    except PermissionError as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2
    for f in files:
        print(f)
    if not files:
        print("no level data found", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
