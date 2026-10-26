# -*- coding: utf-8 -*-
"""KP-CONFIRMED-CONTENT-PROTECTION-01 委任_02A: 確定内容(英語表現・日本語訳・区分)の不変性 共通核(決定論・API 0)。

承認根拠: ユーザー追加指示② (docs/pm/delegation_log/2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_USER_02.md:16-29,37-41)
設計: docs/research/KP-CONFIRMED-CONTENT-PROTECTION-01/DESIGN_02.md (Opus条件Aレビュー M1〜M9 反映)。

役割:
  - 確定レコード <kp_dir>/confirmed_selection.json (正本) と <run>/<lv>/audit/confirmed_selection.json (ミラー)
  - G0(finalize直前/直後)・G1(消費者入口 require_final_consistent の末尾)の検査関数
  - 操作ガード(確定済みレコードがあれば AI/CLI による再選定系操作を拒否)
  - 明示CLI: confirm --from-form / --from-review / --adopt-existing、confirm-revise、revoke、restore、status
runnerは load/verify だけを呼ぶ(レコードの書込みは CLI と finalize 直前の G0 のみ)。

保護対象(protected): 英語(used_form/display_phrase/key_phrase)・日本語訳 japanese_gloss(ユーザーが見て確定した表示値)・区分(category/slot/kind)。
派生物(derived): japanese_gloss_tts は 決定論変換 convert_display_gloss_to_tts_text(japanese_gloss) の結果である限り許容(M2-a)。
参考(reference): AI理由・AI順位。userコメントは user_note_sha256 で改変検出のみ。

使い方:
  py er128_kp_confirmed_content_01.py status --run <run>
  py er128_kp_confirmed_content_01.py confirm --from-form <payload.json> --run <run> --level b1b --by <名> --user-ref <delegation_log path>
  py er128_kp_confirmed_content_01.py confirm --from-review --run <run> --level a2 --by <名> --user-ref <path>
  py er128_kp_confirmed_content_01.py confirm --adopt-existing --run <run> --level a2 --by <名> --user-ref <path> [--apply]
  py er128_kp_confirmed_content_01.py confirm-revise --run <run> --level b1b --by <名> --user-ref <path> --reason ... --gloss <candidate_id>=<新訳>
  py er128_kp_confirmed_content_01.py revoke --run <run> --level b1b --by <名> --user-ref <path> --reason ...
  py er128_kp_confirmed_content_01.py restore --run <run> --level b1b --by <名> --reason ...
"""
from __future__ import annotations

import argparse
import functools
import hashlib
import inspect
import json
import logging
import os
import sys
from typing import Any, Optional

import er119_kp_human_review_01 as rv

_log = logging.getLogger("er128_kp_confirmed_content")

SCHEMA = "eigo_radio_confirmed_selection_v1"
SCHEMA_GRAMMAR = "eigo_radio_confirmed_grammar_v1"
FLAG_NAME = "EIGO_KP_CONFIRMED_PROTECTION"
FILE_RECORD = "confirmed_selection.json"
FILE_GRAMMAR = "confirmed_grammar.json"
DIR_SOURCE = "confirmed_selection_source"
FILE_ISSUE_JSON = "confirmed_content_issue.json"
FILE_ISSUE_MD = "confirmed_content_issue.md"
FILE_LEGACY = "confirmed_content_legacy_drift.json"
FILE_DISABLED = "confirmed_protection_disabled.json"

STATE_LIVE = "live"
STATE_RECONFIRM = "reconfirm_required"   # 確定集合のRedundancy QAがNG→reviewがPENDINGへ戻った(ユーザーの選び直し待ち。黙って別候補へ差し替えない)
STATE_REVOKED = "revoked"
ACTOR_USER = "user"
ACTOR_AUTO = "auto"                       # 明示の不在宣言によるAUTO。ユーザー確定ではない(再確認要求の対象外。英語/区分は不変検査)

PROTECTED_ITEM_FIELDS = ("candidate_id", "kind", "category", "slot", "used_form", "display_phrase", "key_phrase", "japanese_gloss")
ENGLISH_FIELDS = ("used_form", "display_phrase", "key_phrase")
_HUMAN_IGNORED_BY = ("runner", "finalize", "restore", "er128")   # review.historyでこれ以外のbyは人間(または人間の代理)の操作


# ============================================================
# flag(単一読取関数。承認済み仕様=既定ON。kill switchはユーザー指示+user_refがある場合のみ運用する)
# ============================================================
def protection_enabled() -> bool:
    """EIGO_KP_CONFIRMED_PROTECTION=0 のときだけOFF。この関数が唯一の読取点(mode・引数・設定dictからは迂回不可)。"""
    return os.environ.get(FLAG_NAME, "1") != "0"


# ============================================================
# 基本helper
# ============================================================
@functools.lru_cache(maxsize=1)
def converter_id() -> str:
    """japanese_gloss→japanese_gloss_tts 変換規則の版識別(変換関数+委譲先のsourceのsha)。レコードへ記録する(M2-a)。"""
    import er003_audio_tts_asr_safety as safety
    import er003_key_words_canonicalization as kwc
    src = inspect.getsource(kwc.convert_display_gloss_to_tts_text) + inspect.getsource(safety.normalize_tilde_placeholder_ja)
    return "convert_display_gloss_to_tts_text/" + hashlib.sha256(src.encode("utf-8")).hexdigest()[:12]


def convert_gloss_tts(gloss: Optional[str]) -> str:
    import er003_key_words_canonicalization as kwc
    return kwc.convert_display_gloss_to_tts_text(gloss)


def _run_dir_of(kp_dir: str) -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(kp_dir)))


def paths_of(kp_dir: str) -> dict:
    base = os.path.abspath(kp_dir)
    run = _run_dir_of(kp_dir)
    level = os.path.basename(base) if os.path.basename(os.path.dirname(base)) == "key_phrases" else os.path.basename(os.path.dirname(base))
    mirror_dir = os.path.join(run, level, "audit")
    return {"record": os.path.join(kp_dir, FILE_RECORD), "mirror": os.path.join(mirror_dir, FILE_RECORD),
            "source_dir": os.path.join(kp_dir, DIR_SOURCE), "issue_json": os.path.join(kp_dir, FILE_ISSUE_JSON),
            "issue_md": os.path.join(kp_dir, FILE_ISSUE_MD), "legacy": os.path.join(kp_dir, FILE_LEGACY),
            "disabled": os.path.join(kp_dir, FILE_DISABLED)}


def _jsha(obj: Any) -> str:
    return rv.jsha(obj)


def _read(path: str):
    return rv._read_json(path)


def _write(path: str, obj: Any) -> None:
    rv._write_json_atomic(path, obj)


def _file_sha(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ============================================================
# レコードのsha・履歴チェーン(M5c)
# ============================================================
def content_sha256(items: list) -> str:
    """保護フィールドのみのsha(sort_keysのみの正規化。値のUnicode正規化はしない=「～」と「〜」は別物)。"""
    rows = sorted(({k: it.get(k) for k in PROTECTED_ITEM_FIELDS} for it in items), key=lambda r: (r["slot"] or "", r["candidate_id"] or ""))
    return _jsha(rows)


def user_note_sha256(comment: Optional[str]) -> str:
    return rv.sha256_text(comment or "")


def record_sha256(rec: dict) -> str:
    return _jsha({k: v for k, v in rec.items() if k != "record_sha256"})


def _entry_sha(entry: dict) -> str:
    return _jsha({k: v for k, v in entry.items() if k != "entry_sha256"})


def _append_history(rec: dict, *, event: str, by: str, reason: str = "", user_ref: str = "", extra: Optional[dict] = None) -> None:
    hist = rec.setdefault("history", [])
    e = {"revision": rec["revision"], "at": rv._now(), "event": event, "by": by, "reason": reason, "user_ref": user_ref,
         "content_sha256": rec.get("content_sha256"), "prev_entry_sha256": (hist[-1]["entry_sha256"] if hist else None)}
    if extra:
        e["extra"] = extra
    e["entry_sha256"] = _entry_sha(e)
    hist.append(e)


def _problems_self(rec: dict) -> list:
    """レコード自身の整合(自己sha・履歴チェーン・内容sha・ユーザーコメントsha)。"""
    out = []
    if rec.get("schema") != SCHEMA:
        out.append(f"schema不正({rec.get('schema')!r})")
    if record_sha256(rec) != rec.get("record_sha256"):
        out.append("record_sha256が不一致(レコードが手編集された疑い)")
    prev = None
    for i, e in enumerate(rec.get("history") or []):
        if e.get("prev_entry_sha256") != prev or _entry_sha(e) != e.get("entry_sha256"):
            out.append(f"履歴チェーンが不整合(index={i}, event={e.get('event')})")
            break
        prev = e.get("entry_sha256")
    hist = rec.get("history") or []
    if hist and hist[-1].get("content_sha256") != rec.get("content_sha256"):
        out.append("履歴の最新エントリの content_sha256 がレコードと一致しません(履歴を伴わない内容変更の疑い)")
    if content_sha256(rec.get("items") or []) != rec.get("content_sha256"):
        out.append("content_sha256が不一致(保護フィールドが書換えられた疑い)")
    if user_note_sha256(rec.get("comment")) != rec.get("user_note_sha256"):
        out.append("user_note_sha256が不一致(ユーザーコメントが書換えられた疑い)")
    return out


# ============================================================
# レコードI/O
# ============================================================
def load_record(kp_dir: str) -> Optional[dict]:
    p = paths_of(kp_dir)["record"]
    return _read(p) if os.path.exists(p) else None


def save_record(kp_dir: str, rec: dict) -> dict:
    """正本とミラーを同時に書く。record_shaを再計算する。呼出側が review_lock を保持していること。"""
    rec["record_sha256"] = record_sha256(rec)
    p = paths_of(kp_dir)
    _write(p["record"], rec)
    _write(p["mirror"], rec)
    for k in ("issue_json", "issue_md"):   # 状態を更新した時点で、それ以前のISSUE/INTEGRITY診断は解消済み扱い(新しいISSUEは呼出側が保存の後に書く)
        if os.path.exists(p[k]):
            os.replace(p[k], p[k] + ".resolved")
    return rec


def live_user_record(kp_dir: str) -> Optional[dict]:
    """保護が効いているユーザー確定レコード(live かつ actor=user)。flag OFF時は None。"""
    if not protection_enabled():
        return None
    p = paths_of(kp_dir)["record"]
    if not os.path.exists(p):
        return None
    try:
        rec = _read(p)
    except (OSError, ValueError):
        return None
    if rec.get("state") == STATE_LIVE and (rec.get("confirmed_by") or {}).get("actor") == ACTOR_USER:
        return rec
    return None


# ============================================================
# レコード構築(値の出所=候補doc。AI理由はreference)
# ============================================================
def _cand_map(cands: dict) -> dict:
    return {c["candidate_id"]: c for c in cands.get("candidates") or []}


def _item_from_cand(c: dict, category: int, slot: str) -> dict:
    it = c.get("item") or {}
    gloss = it.get("japanese_gloss")
    tts = it.get("japanese_gloss_tts")
    conv = convert_gloss_tts(gloss)
    return {"candidate_id": c["candidate_id"], "kind": c.get("kind") or "phrase", "category": category, "slot": slot,
            "used_form": it.get("used_form"), "display_phrase": it.get("display_phrase"), "key_phrase": it.get("key_phrase"),
            "japanese_gloss": gloss, "gloss_status": it.get("gloss_alignment_status") or (c.get("gates") or {}).get("gloss"),
            "source_sentence_id": it.get("source_sentence_id"),
            "derived": {"japanese_gloss_tts": tts if tts is not None else conv, "converter_id": converter_id(),
                        "matches_converter": (tts is None) or tts == conv},
            "reference": {"ai_reason_ja": c.get("reason_ja"), "ai_rank": c.get("ai_rank")}}


def build_items(cands: dict, kp_ids: list, vocab_ids: list) -> list:
    """kp_ids=区分①(slot=kp)、vocab_ids のうち kp でないもの=区分②(slot=vocab)。順序はai_rank。"""
    cm = _cand_map(cands)
    out = []
    for cid in sorted(kp_ids, key=lambda i: cm[i]["ai_rank"]):
        out.append(_item_from_cand(cm[cid], 1, "kp"))
    for cid in sorted((i for i in vocab_ids if i not in set(kp_ids)), key=lambda i: cm[i]["ai_rank"]):
        out.append(_item_from_cand(cm[cid], 2, "vocab"))
    return out


def _new_record(*, kp_dir: str, review: dict, cands: dict, items: list, actor: str, origin: dict, by: str, attestation: str,
                user_ref: str, comment: str = "", unconsumed: Optional[list] = None, prev: Optional[dict] = None,
                event: str = "confirmed", reason: str = "", confirmation_id: Optional[str] = None) -> dict:
    ak = review.get("article_key") or {}
    rec = {"schema": SCHEMA, "revision": ((prev or {}).get("revision") or 0) + 1, "state": STATE_LIVE,
           "confirmation_id": confirmation_id or ("cr_" + content_sha256(items)[:16]),
           "article": {"family": ak.get("family"), "slug": ak.get("slug"), "level": review.get("level"), "text_sha256": review.get("text_sha256")},
           "origin": dict(origin, candidates_sha256=review.get("candidates_sha256"), review_selection_signature=review.get("selection_signature")),
           "confirmed_by": {"actor": actor, "attestation": attestation, "by": by, "user_ref": user_ref, "at": rv._now()},
           "items": items, "unconsumed": unconsumed or [], "comment": comment or "", "user_note_sha256": user_note_sha256(comment),
           "content_sha256": content_sha256(items), "history": list((prev or {}).get("history") or [])}
    if (prev or {}).get("grammar"):
        rec["grammar"] = prev["grammar"]
    _append_history(rec, event=event, by=by, reason=reason, user_ref=user_ref)
    return rec


def _actor_for(review: dict) -> str:
    return ACTOR_USER if review.get("status") == rv.ST_REVIEWED else ACTOR_AUTO


def _review_human_by(review: dict) -> str:
    for e in reversed(review.get("history") or []):
        if e.get("event") in ("select", "accept_ai"):
            return e.get("by") or ""
    return ""


# ============================================================
# 違反の記録と例外
# ============================================================
def _write_issue(kp_dir: str, *, kind: str, summary: str, diffs: list, next_steps: list, proposal: Optional[list] = None) -> str:
    doc = {"kind": kind, "at": rv._now(), "summary": summary, "diffs": diffs, "next": next_steps, "proposal": proposal or []}
    p = paths_of(kp_dir)
    try:
        _write(p["issue_json"], doc)
        lines = [f"# 確定内容の{'確認依頼 (CONFIRMED_CONTENT_ISSUE)' if kind == 'CONFIRMED_CONTENT_ISSUE' else '不整合 (INTEGRITY_VIOLATION)'}", "", summary, ""]
        for d in diffs:
            lines.append(f"- {d.get('candidate_id') or '-'} / {d.get('field')}: 確定値=`{d.get('confirmed')}` / 観測値=`{d.get('observed')}` ({d.get('where')})")
        if proposal:
            lines += ["", "## 修正案(確定内容は変更していません。ユーザーの再確認が必要です)"] + [f"- {x}" for x in proposal]
        lines += ["", "## 次の一手"] + [f"- {x}" for x in next_steps]
        rv._write_text_atomic(p["issue_md"], "\n".join(lines) + "\n")
    except OSError as e:   # 記録の失敗で本来の例外を隠さない
        _log.warning("confirmed_content_issue write failed: %s", e)
    return p["issue_json"]


def _cli(kp_dir: str, cmd: str) -> str:
    return f"py er128_kp_confirmed_content_01.py {cmd} --run {_run_dir_of(kp_dir)}"


def raise_integrity(kp_dir: str, level: str, diffs: list, summary: str) -> None:
    nxt = [f"原因がパイプライン側の変更なら: {_cli(kp_dir, 'restore')} --level {level} --by <名> --reason <理由> (確定値で再finalize。API 0)",
           f"確定内容そのものを変えたい場合: {_cli(kp_dir, 'confirm-revise')} --level {level} --by <名> --user-ref <ユーザー発言> --reason ... (ユーザー確認済みの変更のみ)"]
    path = _write_issue(kp_dir, kind="INTEGRITY_VIOLATION", summary=summary, diffs=diffs, next_steps=nxt)
    brief = "; ".join(f"{d.get('candidate_id') or '-'}.{d.get('field')} 確定=`{d.get('confirmed')}` 観測=`{d.get('observed')}`" for d in diffs[:4])
    raise rv.ConfirmedContentIntegrityViolation(
        f"CONFIRMED_CONTENT_INTEGRITY_VIOLATION({level}): {summary} {brief}。詳細={path}。次の一手: {nxt[0]}")


def raise_issue(kp_dir: str, level: str, summary: str, diffs: list, proposal: Optional[list] = None, next_steps: Optional[list] = None) -> None:
    nxt = next_steps or [f"{_cli(kp_dir, 'confirm-revise')} --level {level} --by <名> --user-ref <ユーザー発言> --reason ... (修正案を採用)",
                         f"{_cli(kp_dir, 'revoke')} --level {level} --by <名> --user-ref <ユーザー発言> --reason ... (確定を取り消して選び直す)"]
    path = _write_issue(kp_dir, kind="CONFIRMED_CONTENT_ISSUE", summary=summary, diffs=diffs, next_steps=nxt, proposal=proposal)
    raise rv.ConfirmedContentIssue(f"CONFIRMED_CONTENT_ISSUE({level}): {summary} 詳細={path}。再確認が必要です(AIは黙って変更しません)", kp_dir=kp_dir, issue_path=path)


def request_notice(kp_dir: str) -> str:
    """依頼書(request_md)の先頭に置く『確定内容の確認依頼』節(ISSUEがあるときのみ。無ければ空)。"""
    p = paths_of(kp_dir)["issue_md"]
    if not protection_enabled() or not os.path.exists(p):
        return ""
    try:
        jp = paths_of(kp_dir)["issue_json"]
        if os.path.exists(jp) and _read(jp).get("kind") != "CONFIRMED_CONTENT_ISSUE":
            return ""
        with open(p, encoding="utf-8") as f:
            return f.read() + "\n---\n\n"
    except (OSError, ValueError):
        return ""


# ============================================================
# 検査(G0/G1)
# ============================================================
def _item_diffs(rec_item: dict, art_item: Optional[dict], where: str, *, enforce_gloss: bool) -> tuple:
    """(blocking_diffs, warn_diffs)。art_itemがNoneなら欠落。"""
    cid = rec_item["candidate_id"]
    if art_item is None:
        return [{"candidate_id": cid, "field": "(item)", "confirmed": rec_item.get("used_form"), "observed": None, "where": where + ":欠落"}], []
    block, warn = [], []
    for f in ENGLISH_FIELDS:
        if rec_item.get(f) != art_item.get(f):
            block.append({"candidate_id": cid, "field": f, "confirmed": rec_item.get(f), "observed": art_item.get(f), "where": where})
    gl = []
    if rec_item.get("japanese_gloss") != art_item.get("japanese_gloss"):
        gl.append({"candidate_id": cid, "field": "japanese_gloss", "confirmed": rec_item.get("japanese_gloss"),
                   "observed": art_item.get("japanese_gloss"), "where": where})
    if "japanese_gloss_tts" in art_item:
        tts = art_item.get("japanese_gloss_tts")
        if tts != (rec_item.get("derived") or {}).get("japanese_gloss_tts") and tts != convert_gloss_tts(rec_item.get("japanese_gloss")):
            gl.append({"candidate_id": cid, "field": "japanese_gloss_tts(派生物契約: 確定訳の決定論変換でなければならない)",
                       "confirmed": convert_gloss_tts(rec_item.get("japanese_gloss")), "observed": tts, "where": where})
    (block if enforce_gloss else warn).extend(gl)
    return block, warn


def _doc_items_by_id(path: str) -> Optional[dict]:
    if not os.path.exists(path):
        return None
    return {it.get("candidate_id"): it for it in (_read(path).get("items") or [])}


def _artifact_diffs(kp_dir: str, level: str, rec: dict, *, assets_json: Optional[str] = None) -> tuple:
    """レコードと実artifact(kp/vocab/assets copy)の保護フィールド突合。"""
    actor = (rec.get("confirmed_by") or {}).get("actor")
    enforce_gloss = actor == ACTOR_USER
    pth = rv.paths(kp_dir)
    block, warn = [], []
    kp_by = _doc_items_by_id(pth["kp"]) or {}
    vocab_by = _doc_items_by_id(pth["vocab"]) if level == "b1b" else None
    for ri in rec.get("items") or []:
        if ri["slot"] == "kp":
            b, w = _item_diffs(ri, kp_by.get(ri["candidate_id"]), "keywords_canonicalized.json", enforce_gloss=enforce_gloss)
            block += b
            warn += w
        if level == "b1b":
            b, w = _item_diffs(ri, (vocab_by or {}).get(ri["candidate_id"]), "vocab_confirmed.json", enforce_gloss=enforce_gloss)
            block += b
            warn += w
        if assets_json and ri["slot"] == "kp" and os.path.exists(assets_json):
            ab = _doc_items_by_id(assets_json) or {}
            if ri["candidate_id"] in ab:   # copyに無い(古い/未install)場合はrunner側のKP_ASSETS_STALE検査の担当(同一メッセージを維持)。内容がずれたcopyだけここで止める
                b, w = _item_diffs(ri, ab[ri["candidate_id"]], "assets copy(" + os.path.basename(os.path.dirname(os.path.dirname(assets_json))) + ")", enforce_gloss=enforce_gloss)
                block += b
                warn += w
    return block, warn


def _cand_diffs(rec: dict, cands: dict) -> list:
    """M5b: レコードの保護フィールド==候補doc(自己sha検査済み)の値。"""
    cm = _cand_map(cands)
    out = []
    for ri in rec.get("items") or []:
        c = cm.get(ri["candidate_id"])
        if c is None:
            out.append({"candidate_id": ri["candidate_id"], "field": "(candidate)", "confirmed": ri.get("used_form"), "observed": None, "where": "kp_candidates.json:欠落"})
            continue
        cur = _item_from_cand(c, ri["category"], ri["slot"])
        for f in PROTECTED_ITEM_FIELDS:
            if cur.get(f) != ri.get(f):
                out.append({"candidate_id": ri["candidate_id"], "field": f, "confirmed": ri.get(f), "observed": cur.get(f), "where": "kp_candidates.json"})
    return out


def _grammar_problems(kp_dir: str, level: str, rec: dict) -> list:
    g = rec.get("grammar")
    if not g:
        return []
    out = []
    run = _run_dir_of(kp_dir)
    p = os.path.join(run, g["path_rel"])
    if not os.path.exists(p):
        return [f"confirmed_grammar.json が消えています({g['path_rel']})"]
    doc = _read(p)
    if _jsha({k: v for k, v in doc.items() if k != "sidecar_sha256"}) != doc.get("sidecar_sha256") or doc.get("sidecar_sha256") != g.get("sidecar_sha256"):
        out.append("confirmed_grammar.json のshaが不一致(文法の確定内容が書換えられた疑い)")
    if doc.get("confirmation_id") != rec.get("confirmation_id"):
        out.append("confirmed_grammar.json の confirmation_id が確定レコードと一致しません")
    return out


def _form_source_problems(kp_dir: str, rec: dict) -> list:
    o = rec.get("origin") or {}
    if o.get("kind") != "form_submission":
        return []
    sp = os.path.join(paths_of(kp_dir)["source_dir"], f"rev{o.get('source_revision', rec['revision'])}_payload.json")
    if not os.path.exists(sp):
        return [f"フォーム送信原文({os.path.basename(sp)})が消えています"]
    if _file_sha(sp) != o.get("form_payload_sha256"):
        return ["フォーム送信原文のshaがレコードと不一致"]
    return []


def verify_g1(kp_dir: str, level: str, review: dict, cands: dict, *, assets_json: Optional[str] = None) -> None:
    """G1(消費者入口)。require_final_consistentの末尾から呼ぶ。読取専用(診断ファイルを除きレコードを書かない)。
    レコード無し=旧run(read-only検証でWARN+confirmed_content_legacy_drift.json。M7)。違反=INTEGRITY(rc=3相当)。"""
    if not protection_enabled():
        _note_disabled(kp_dir)
        return
    p = paths_of(kp_dir)
    if not os.path.exists(p["record"]):
        _legacy_drift(kp_dir, level, review, cands, assets_json)
        return
    rec = _read(p["record"])
    problems = _problems_self(rec)
    if not os.path.exists(p["mirror"]) or _read(p["mirror"]) != rec:
        problems.append("ミラー(audit/confirmed_selection.json)が欠落または正本と不一致")
    problems += _form_source_problems(kp_dir, rec)
    problems += _grammar_problems(kp_dir, level, rec)
    if problems:
        raise_integrity(kp_dir, level, [{"candidate_id": None, "field": "record", "confirmed": "(自己整合)", "observed": x, "where": "confirmed_selection.json"} for x in problems],
                        "確定レコード自体の整合が崩れています。")
    if rec.get("state") == STATE_REVOKED:
        _legacy_drift(kp_dir, level, review, cands, assets_json)   # 取消済み=保護なし(次の確定で新レコード)
        return
    if rec.get("state") == STATE_RECONFIRM:
        raise_issue(kp_dir, level, "確定集合がRedundancy QAでNGになり、ユーザーの選び直し待ちです。", [], proposal=[
            "kp_human_review_request.md の候補から選び直してください(旧確定は履歴に保存されています)"],
            next_steps=["py er119_kp_human_review_cli_01.py select ... (選び直し)"])
    diffs = []
    o = rec.get("origin") or {}
    if o.get("candidates_sha256") != review.get("candidates_sha256") or rec["article"].get("text_sha256") != review.get("text_sha256"):
        diffs.append({"candidate_id": None, "field": "candidates_sha256/text_sha256", "confirmed": f"{str(o.get('candidates_sha256'))[:12]}/{str(rec['article'].get('text_sha256'))[:12]}",
                      "observed": f"{str(review.get('candidates_sha256'))[:12]}/{str(review.get('text_sha256'))[:12]}", "where": "kp_human_review.json(候補docの差替え/本文変更の疑い)"})
    if o.get("review_selection_signature") != review.get("selection_signature"):
        diffs.append({"candidate_id": None, "field": "review_selection_signature", "confirmed": o.get("review_selection_signature"),
                      "observed": review.get("selection_signature"), "where": "kp_human_review.json"})
    sel = review.get("selection") or {}
    want = set(rv.sel_ids(sel, "kp")) | set(rv.sel_ids(sel, "vocab"))
    have = {it["candidate_id"] for it in rec.get("items") or []}
    kp_have = {it["candidate_id"] for it in rec.get("items") or [] if it["slot"] == "kp"}
    if want != have or kp_have != set(rv.sel_ids(sel, "kp")):
        diffs.append({"candidate_id": None, "field": "selection", "confirmed": sorted(have), "observed": sorted(want), "where": "kp_human_review.json"})
    if diffs:
        raise_integrity(kp_dir, level, diffs, "確定レコードと review の確定集合/候補docが一致しません。")
    cd = _cand_diffs(rec, cands)
    if cd:
        raise_integrity(kp_dir, level, cd, "確定レコードの値が候補doc(正本)と異なります。")
    block, warn = _artifact_diffs(kp_dir, level, rec, assets_json=assets_json)
    if warn:
        _log.warning("confirmed content (actor=auto) drift warn: %s", warn)
        try:
            _write(p["legacy"], {"kind": "auto_actor_gloss_drift_warn", "at": rv._now(), "diffs": warn})
        except OSError:
            pass
    if block:
        raise_integrity(kp_dir, level, block, "確定内容と成果物(artifact)が一致しません(確定後に書換えられた)。")


def _note_disabled(kp_dir: str) -> None:
    msg = f"[WARN] {FLAG_NAME}=0: 確定内容保護が無効です(kill switch。ユーザー指示+user_refがある場合のみ運用すること)"
    print(msg, file=sys.stderr)
    try:
        _write(paths_of(kp_dir)["disabled"], {"flag": FLAG_NAME, "value": "0", "at": rv._now(), "note": msg})
    except OSError:
        pass


def _legacy_drift(kp_dir: str, level: str, review: dict, cands: dict, assets_json: Optional[str]) -> None:
    """レコードの無い(機能有効化前に確定した)run: 候補doc値とartifactを read-only で突合し、ずれはWARN+診断ファイルのみ(BLOCKしない。M7)。"""
    sel = review.get("selection") or {}
    items = build_items(cands, rv.sel_ids(sel, "kp"), rv.sel_ids(sel, "vocab") if level == "b1b" else [])
    pseudo = {"items": items, "confirmed_by": {"actor": ACTOR_USER}}
    block, warn = _artifact_diffs(kp_dir, level, pseudo, assets_json=assets_json)
    drift = block + warn
    p = paths_of(kp_dir)["legacy"]
    if drift:
        _log.warning("confirmed content legacy drift (record無し、WARNのみ): %s", [(d["candidate_id"], d["field"]) for d in drift])
        try:
            _write(p, {"kind": "legacy_drift", "at": rv._now(), "note": "確定レコード無し(機能有効化前に確定)。保護下に置くには `confirm --adopt-existing`", "diffs": drift})
        except OSError:
            pass
    elif os.path.exists(p):
        try:
            rec = _read(p)
            if rec.get("kind") == "legacy_drift":
                os.replace(p, p + ".resolved")
        except (OSError, ValueError):
            pass


# ============================================================
# G0(finalize_kp 直前: レコード作成/照合。finalize_kp の review_lock 内から呼ぶ)
# ============================================================
def on_finalize_pre_write(kp_dir: str, review: dict, cands: dict, level: str, *, fresh: bool) -> None:
    """成果物を書く前に呼ぶ。fresh=今回成果物を(再)書込みする。freshでない(既にfinalize済みのidempotent再実行)でレコードが無ければ
    旧run扱いで何も作らない(遅延生成しない。M7)。"""
    if not protection_enabled():
        return
    if not fresh:
        return
    sel = review.get("selection") or {}
    build = build_items(cands, rv.sel_ids(sel, "kp"), rv.sel_ids(sel, "vocab") if level == "b1b" else [])
    actor = _actor_for(review)
    sig = review.get("selection_signature")
    p = paths_of(kp_dir)["record"]
    rec = _read(p) if os.path.exists(p) else None
    by = _review_human_by(review) if actor == ACTOR_USER else "runner"
    origin = {"kind": "hr_cli" if actor == ACTOR_USER else "auto_declared"}
    if rec is not None and rec.get("state") == STATE_LIVE:
        a_prev = (rec.get("confirmed_by") or {}).get("actor")
        same = content_sha256(build) == rec.get("content_sha256") and (rec.get("origin") or {}).get("review_selection_signature") == sig
        if a_prev == ACTOR_USER:
            if not same:
                raise_integrity(kp_dir, level, [{"candidate_id": None, "field": "review_selection_signature", "confirmed": (rec.get("origin") or {}).get("review_selection_signature"),
                                                 "observed": sig, "where": "finalize(reviewがユーザー確定レコードと異なる確定集合になっている)"}],
                                "ユーザー確定済みのレコードと異なる確定集合をfinalizeしようとしました(再選定は revoke 後のみ)。")
            return
        if a_prev == ACTOR_AUTO and same and actor == ACTOR_AUTO:
            return
        # auto→(auto繰上げ/ユーザー確認)
        ev = "confirmed" if actor == ACTOR_USER else "auto_updated"
        new = _new_record(kp_dir=kp_dir, review=review, cands=cands, items=build, actor=actor, origin=origin, by=by or "runner",
                          attestation=("cli --by " + by) if actor == ACTOR_USER else "declare-absent", user_ref="", prev=rec, event=ev)
        save_record(kp_dir, new)
        return
    ev = "confirmed" if actor == ACTOR_USER else "auto_adopted"
    if rec is not None and rec.get("state") == STATE_RECONFIRM and actor == ACTOR_AUTO:
        ev = "auto_adopted_after_reconfirm_required"
    new = _new_record(kp_dir=kp_dir, review=review, cands=cands, items=build, actor=actor, origin=origin, by=by or "runner",
                      attestation=("cli --by " + by) if actor == ACTOR_USER else "declare-absent", user_ref="", prev=rec, event=ev)
    save_record(kp_dir, new)


def on_finalize_post_write(kp_dir: str, level: str) -> None:
    """成果物を書いた直後: 書いた成果物がレコードと一致することを確認(G0)。レコード無し/保護OFFは何もしない。"""
    if not protection_enabled():
        return
    rec = load_record(kp_dir)
    if rec is None or rec.get("state") != STATE_LIVE:
        return
    block, _warn = _artifact_diffs(kp_dir, level, rec)
    if block:
        raise_integrity(kp_dir, level, block, "finalizeが書いた成果物が確定レコードと一致しません(G0)。")


def on_final_redundancy_ng(kp_dir: str, ng_pairs: list) -> None:
    """確定集合のRedundancy QA NG(reviewがPENDINGへ戻る)。ユーザー確定レコードは reconfirm_required にして履歴へ残す(黙って差し替えない)。"""
    rec = load_record(kp_dir) if protection_enabled() else None
    if rec is None or rec.get("state") != STATE_LIVE:
        return
    rec["state"] = STATE_RECONFIRM
    _append_history(rec, event="redundancy_ng_reconfirm_required", by="runner", reason="確定集合のRedundancy QAがNG(ユーザーの選び直し待ち)",
                    extra={"ng_pairs": [list(p) for p in ng_pairs]})
    save_record(kp_dir, rec)
    raise_issue_nowait(kp_dir, rec, ng_pairs)


def raise_issue_nowait(kp_dir: str, rec: dict, ng_pairs: list) -> None:
    pairs = []
    cm = {it["candidate_id"]: it for it in rec.get("items") or []}
    for a, b in ng_pairs:
        pairs.append(f"{(cm.get(a) or {}).get('used_form', a)} と {(cm.get(b) or {}).get('used_form', b)} が重複(Redundancy QA NG)")
    _write_issue(kp_dir, kind="CONFIRMED_CONTENT_ISSUE", summary="確定した集合がRedundancy QAでNGになりました。選び直しが必要です(AIは自動で差し替えません)。",
                 diffs=[{"candidate_id": None, "field": "redundancy", "confirmed": "(旧確定)", "observed": x, "where": "final_redundancy_qa"} for x in pairs],
                 next_steps=["kp_human_review_request.md の候補から選び直す(旧確定はconfirmed_selection.jsonのhistoryに保存)"],
                 proposal=["重複ペアの片方を別候補に替えて再選択してください"])


def stale_issue(kp_dir: str, new_text_sha: str) -> Optional[str]:
    """本文が変わったがユーザー確定レコードがある場合: 候補の再生成(有料・確定の消失)へ進む前にISSUEで止める(再バインドは委任_02B)。
    ISSUEの要約文を返す(無ければNone)。"""
    rec = live_user_record(kp_dir)
    if rec is None or (rec.get("article") or {}).get("text_sha256") == new_text_sha:
        return None
    msg = (f"本文(text_sha256)が変わりました({str(rec['article'].get('text_sha256'))[:12]}→{new_text_sha[:12]})が、ユーザー確定済みの選定があります。"
           "確定内容を黙って破棄/再選定しません。")
    _write_issue(kp_dir, kind="CONFIRMED_CONTENT_ISSUE", summary=msg,
                 diffs=[{"candidate_id": it["candidate_id"], "field": "used_form", "confirmed": it["used_form"], "observed": "(新本文での存在は未検証)", "where": "text_sha256変更"}
                        for it in rec.get("items") or []],
                 next_steps=[f"{_cli(kp_dir, 'revoke')} --level {rec['article'].get('level')} --by <名> --user-ref <ユーザー発言> --reason '本文変更に伴う選び直し' (その後に制作を再実行→候補再生成)"],
                 proposal=["確定表現が新本文にも逐語で存在するなら、確定を維持したまま本文shaを再バインドする案(委任_02Bで自動化。現段階では revoke→再選択)"])
    return msg


# ============================================================
# 操作ガード(M4)
# ============================================================
def guard(kp_dir: str, op: str) -> None:
    """ユーザー確定レコードがあれば、選定を書き換え得る操作(select/accept-ai/reselect/ng/unng/resolve-gloss)を拒否する。"""
    rec = live_user_record(kp_dir)
    if rec is None:
        return
    lv = (rec.get("article") or {}).get("level")
    raise rv.ConfirmedContentLocked(
        f"CONFIRMED_CONTENT_LOCKED: {op} は拒否されました。ユーザー確定済みの選定があります(revision={rec['revision']}, 確定者={((rec.get('confirmed_by') or {}).get('by'))})。"
        f"変更は `{_cli(kp_dir, 'confirm-revise')} --level {lv} --by <名> --user-ref <ユーザー発言> --reason ...`(訳の修正)または"
        f"`{_cli(kp_dir, 'revoke')} --level {lv} --by <名> --user-ref <ユーザー発言> --reason ...`(確定の取消→選び直し)のみ(ユーザー確認済みの操作)。")


def guard_declaration(run_dirs: list) -> None:
    for rd in run_dirs:
        for d in rv.discover_kp_dirs(rd):
            guard(d, "declare-absent")


# ============================================================
# 単一アクセサ契約(今後の消費者は検証してから返すこのアクセサだけを使う)
# ============================================================
def load_verified_items(kp_dir: str, *, level: str, which: str = "kp", require_src_contract: bool = False) -> list:
    """G1を通してから確定itemを返す単一アクセサ。which="kp"|"vocab"。reviewの無い旧runは従来のartifactを返す(検証なし)。"""
    rv.require_final_consistent(kp_dir, level=level, require_src_contract=require_src_contract)
    pth = rv.paths(kp_dir)
    p = pth["vocab"] if which == "vocab" else pth["kp"]
    return sorted(_read(p).get("items") or [], key=lambda x: x["rank"])


# ============================================================
# CLI
# ============================================================
class CliError(RuntimeError):
    pass


def _kp_dir_for(run: str, level: str) -> str:
    for d in rv.discover_kp_dirs(run):
        r = rv.load_review(d)
        if r and r.get("level") == level:
            return d
    raise CliError(f"{run}に level={level} のKP review/候補が見つかりません")


def _need_user_ref(user_ref: str) -> str:
    if not (user_ref or "").strip():
        raise CliError("--user-ref(ユーザー発言原文の delegation_log パス)が必須です(--by は認証ではないため)")
    if not os.path.exists(user_ref):
        raise CliError(f"--user-ref のファイルが存在しません: {user_ref}")
    return user_ref


def _need_by(by: str) -> str:
    if not (by or "").strip():
        raise CliError("--by(操作者)が必須です")
    return by


def _flat_selection_ids(groups: dict) -> dict:
    return {"cat1": [i.get("candidate_id") for i in groups.get("key_phrase") or []],
            "cat2": [i.get("candidate_id") for i in groups.get("extra_explanation") or []],
            "cat3": [i.get("candidate_id") for i in groups.get("meaning_display") or []]}


def cmd_from_form(run: str, level: str, payload_path: str, by: str, user_ref: str) -> dict:
    by, user_ref = _need_by(by), _need_user_ref(user_ref)
    kp_dir = _kp_dir_for(run, level)
    with open(payload_path, "rb") as f:
        raw = f.read()
    payload = json.loads(raw.decode("utf-8"))
    if payload.get("schema_version") != 2:
        raise CliError(f"schema_version=2 のフォーム送信データのみ受け付けます(受信={payload.get('schema_version')!r})")
    cands = rv.load_candidates(kp_dir)
    guard(kp_dir, "confirm --from-form(既にユーザー確定済み)")
    art = payload.get("article") or {}
    if art.get("level") not in (None, level):
        raise CliError(f"payloadのlevel={art.get('level')!r} と --level={level!r} が異なります")
    sha = art.get("candidates_sha256")
    if not sha:
        raise_issue(kp_dir, level, "フォーム送信データに候補集合sha256(article.candidates_sha256)がありません(取得不可の候補で作られたフォーム)。確定を受け付けられません。", [],
                    proposal=["Production候補doc(kp_candidates.json)由来のフォームデータで選び直してください"], next_steps=["フォームを現在の候補docから作り直して再送信"])
    if sha != cands["candidates_sha256"]:
        raise_issue(kp_dir, level, "フォームの候補集合sha256が現在の候補docと一致しません(フォームが古い/別の候補集合)。", [
            {"candidate_id": None, "field": "candidates_sha256", "confirmed": sha[:16], "observed": cands["candidates_sha256"][:16], "where": "payload vs kp_candidates.json"}],
            proposal=["現在の候補docでフォームを作り直して再送信してください"], next_steps=["フォームを作り直して再送信"])
    if art.get("text_sha256") and art["text_sha256"] != cands.get("text_sha256"):
        raise_issue(kp_dir, level, "フォームの本文shaが現在の候補docと一致しません。", [], next_steps=["フォームを作り直して再送信"])
    cm = _cand_map(cands)
    groups = payload.get("selection") or {}
    ids = _flat_selection_ids(groups)
    seen = set()
    diffs = []
    for gname in ("key_phrase", "extra_explanation", "meaning_display"):
        for it in groups.get(gname) or []:
            cid = it.get("candidate_id")
            if not cid or cid not in cm:
                raise CliError(f"payloadの candidate_id={cid!r}(term={it.get('term')!r}) が候補docにありません(termでの対応付けはしません)")
            if cid in seen:
                raise CliError(f"candidate_id={cid} が複数区分に重複しています")
            seen.add(cid)
            c = cm[cid]
            if (it.get("kind") or None) != (c.get("kind") or "phrase"):
                raise CliError(f"candidate_id={cid} の kind が候補docと異なります(payload={it.get('kind')!r} / doc={c.get('kind') or 'phrase'!r})")
            if it.get("term") != (c.get("item") or {}).get("used_form"):
                diffs.append({"candidate_id": cid, "field": "used_form", "confirmed": it.get("term"), "observed": (c.get("item") or {}).get("used_form"), "where": "payload vs 候補doc"})
            if it.get("ja_gloss") != (c.get("item") or {}).get("japanese_gloss"):
                diffs.append({"candidate_id": cid, "field": "japanese_gloss", "confirmed": it.get("ja_gloss"), "observed": (c.get("item") or {}).get("japanese_gloss"), "where": "payload vs 候補doc"})
            if it.get("ja_gloss_status") != "official":
                diffs.append({"candidate_id": cid, "field": "ja_gloss_status", "confirmed": it.get("ja_gloss_status"), "observed": "official(正式訳)が必要", "where": "payload"})
    if diffs:
        raise_issue(kp_dir, level, "フォームで確定された表現/日本語訳が、候補docの正式値と一致しない、または正式訳ではありません。黙って採用・置換しません。", diffs,
                    proposal=["候補docの正式な値(日本語訳を含む)を確認し、フォームを作り直すか、訳の修正を明示して `confirm-revise` で確定してください"],
                    next_steps=["候補docの値でフォームを作り直して再送信(または gloss HR 解消後に再確認)"])
    kp_ids = ids["cat1"]
    vocab_ids = (ids["cat1"] + ids["cat2"]) if level == "b1b" else None
    by_rank = {cid: cm[cid]["ai_rank"] for cid in seen}
    # 既存検証(Redundancy/NG/gloss_hr_pending/qa_fail/件数)を全て通す op_select。失敗=何も書かない
    review = rv.op_select(kp_dir, kp_ranks=[by_rank[i] for i in kp_ids], vocab_ranks=([by_rank[i] for i in vocab_ids] if vocab_ids is not None else None), by=by)
    unconsumed = [{"candidate_id": i["candidate_id"], "kind": i.get("kind"), "category": 3, "used_form": i.get("term"), "japanese_gloss": i.get("ja_gloss"),
                   "reason": "CATEGORY3_NO_CONSUMER"} for i in groups.get("meaning_display") or []]
    if level != "b1b":
        unconsumed += [{"candidate_id": i["candidate_id"], "kind": i.get("kind"), "category": 2, "used_form": i.get("term"), "japanese_gloss": i.get("ja_gloss"),
                        "reason": "STD_CATEGORY2_NO_SLOT"} for i in groups.get("extra_explanation") or []]
    with rv.review_lock(kp_dir, rv.KIND_KP, by):
        items = build_items(cands, kp_ids, vocab_ids or [])
        prev = load_record(kp_dir)
        rev_no = ((prev or {}).get("revision") or 0) + 1
        os.makedirs(paths_of(kp_dir)["source_dir"], exist_ok=True)
        sp = os.path.join(paths_of(kp_dir)["source_dir"], f"rev{rev_no}_payload.json")
        with open(sp, "wb") as f:
            f.write(raw)
        origin = {"kind": "form_submission", "form_schema": payload.get("schema"), "form_schema_version": 2, "form_payload_sha256": hashlib.sha256(raw).hexdigest(),
                  "source_revision": rev_no, "user_ref": user_ref}
        rec = _new_record(kp_dir=kp_dir, review=review, cands=cands, items=items, actor=ACTOR_USER, origin=origin, by=by, attestation="form_submit", user_ref=user_ref,
                          comment=payload.get("comment") or "", unconsumed=unconsumed, prev=prev, event="confirmed",
                          confirmation_id="cf_" + hashlib.sha256(raw).hexdigest()[:16])
        rec.pop("grammar", None)
        grammar = (groups.get("grammar") or [])
        if grammar:
            rec["grammar"] = _write_grammar_sidecar(run, rec, grammar)
        save_record(kp_dir, rec)
    return {"record": paths_of(kp_dir)["record"], "revision": rec["revision"], "items": [(i["candidate_id"], i["category"], i["used_form"]) for i in items],
            "unconsumed": [(u["candidate_id"], u["reason"]) for u in unconsumed], "grammar": len(grammar),
            "next": "制作コマンドを同じまま再実行してください(finalize→後続が進みます)"}


def _write_grammar_sidecar(run: str, rec: dict, grammar: list) -> dict:
    import er119_grammar_review_01 as gr
    dirs = gr.discover_dirs(run)
    if not dirs:
        raise CliError("文法(Part 2)の候補/reviewがまだありません(制作を実行して候補を生成してから、文法を含むフォームを送信してください)")
    sd = dirs[0]
    doc = {"schema": SCHEMA_GRAMMAR, "confirmation_id": rec["confirmation_id"],
           "items": [{k: g.get(k) for k in ("id", "title", "explanation_full", "explanation_status", "example")} for g in grammar]}
    doc["content_sha256"] = _jsha(doc["items"])
    doc["sidecar_sha256"] = _jsha({k: v for k, v in doc.items() if k != "sidecar_sha256"})
    p = os.path.join(sd, FILE_GRAMMAR)
    _write(p, doc)
    return {"path_rel": os.path.relpath(p, run).replace(os.sep, "/"), "sidecar_sha256": doc["sidecar_sha256"], "count": len(grammar),
            "explanation_source": ["form_displayed" if g.get("explanation_status") == "provided" else "stepB_generated_frozen" for g in grammar]}


def cmd_from_review(run: str, level: str, by: str, user_ref: str, *, adopt_existing: bool = False, apply: bool = False) -> dict:
    by, user_ref = _need_by(by), _need_user_ref(user_ref)
    kp_dir = _kp_dir_for(run, level)
    with rv.review_lock(kp_dir, rv.KIND_KP, by):
        review, cands = rv.load_review(kp_dir), rv.load_candidates(kp_dir)
        if review["status"] not in rv.FORWARD_STATUSES:
            raise CliError(f"status={review['status']}: 確定済み(REVIEWED/UNREVIEWED_AUTO_ADOPTED)のreviewからのみレコードを作れます")
        prev = load_record(kp_dir)
        if prev is not None and prev.get("state") == STATE_LIVE and not adopt_existing:
            raise CliError(f"確定レコードは既にあります(revision={prev['revision']})。変更は confirm-revise / revoke")
        sel = review["selection"]
        items = build_items(cands, rv.sel_ids(sel, "kp"), rv.sel_ids(sel, "vocab") if level == "b1b" else [])
        actor = _actor_for(review)
        pseudo = {"items": items, "confirmed_by": {"actor": ACTOR_USER}}
        block, warn = _artifact_diffs(kp_dir, level, pseudo)
        out = {"adopt_existing": adopt_existing, "actor": actor, "items": [(i["candidate_id"], i["category"], i["used_form"], i["japanese_gloss"]) for i in items],
               "artifact_drift": block + warn}
        if adopt_existing and not apply:
            out["dry_run"] = True
            out["note"] = "差分を提示しました。保護下に置くには --apply を付けて再実行(ずれがある場合は適用後 restore が必要)"
            return out
        rec = _new_record(kp_dir=kp_dir, review=review, cands=cands, items=items, actor=actor,
                          origin={"kind": "adopt_existing" if adopt_existing else ("hr_cli" if actor == ACTOR_USER else "auto_declared"), "user_ref": user_ref},
                          by=by, attestation=f"cli --by {by}", user_ref=user_ref, prev=prev, event="adopted_existing" if adopt_existing else "confirmed")
        save_record(kp_dir, rec)
        out["record"] = paths_of(kp_dir)["record"]
        out["revision"] = rec["revision"]
        return out


def cmd_revoke(run: str, level: str, by: str, user_ref: str, reason: str) -> dict:
    by, user_ref = _need_by(by), _need_user_ref(user_ref)
    if not (reason or "").strip():
        raise CliError("--reason が必須です")
    kp_dir = _kp_dir_for(run, level)
    with rv.review_lock(kp_dir, rv.KIND_KP, by):
        rec = load_record(kp_dir)
        if rec is None or rec.get("state") == STATE_REVOKED:
            raise CliError("取り消す確定レコードがありません")
        rec["state"] = STATE_REVOKED
        rec["revision"] += 1
        _append_history(rec, event="revoked", by=by, reason=reason, user_ref=user_ref, extra={"revoked_items": [i["candidate_id"] for i in rec["items"]]})
        save_record(kp_dir, rec)
        return {"revoked": True, "revision": rec["revision"], "next": "選び直しは `py er119_kp_human_review_cli_01.py select|reselect ...`(レコードは履歴として残ります)"}


def cmd_revise(run: str, level: str, by: str, user_ref: str, reason: str, gloss: list) -> dict:
    """ユーザー確認済みの訳の修正。候補doc(正本)の該当itemを更新→review候補sha更新→確定物を退避→再finalize(API 0)の連鎖を決定論で行う。"""
    by, user_ref = _need_by(by), _need_user_ref(user_ref)
    if not (reason or "").strip():
        raise CliError("--reason が必須です")
    changes = {}
    for g in gloss or []:
        if "=" not in g:
            raise CliError(f"--gloss は <candidate_id>=<新訳> の形式です(指定: {g!r})")
        cid, new = g.split("=", 1)
        if not new.strip():
            raise CliError("新訳が空です")
        changes[cid.strip()] = new
    if not changes:
        raise CliError("変更内容がありません(--gloss <candidate_id>=<新訳>)")
    kp_dir = _kp_dir_for(run, level)
    with rv.review_lock(kp_dir, rv.KIND_KP, by):
        rec = load_record(kp_dir)
        if rec is None or rec.get("state") != STATE_LIVE:
            raise CliError("確定レコード(live)がありません")
        review, cands = rv.load_review(kp_dir), rv.load_candidates(kp_dir)
        cm = _cand_map(cands)
        for cid in changes:
            if cid not in {i["candidate_id"] for i in rec["items"]}:
                raise CliError(f"candidate_id={cid} は確定レコードにありません")
        before = {i["candidate_id"]: i["japanese_gloss"] for i in rec["items"] if i["candidate_id"] in changes}
        for cid, new in changes.items():
            c = cm[cid]
            c["item"]["japanese_gloss"] = new
            c["item"]["japanese_gloss_tts"] = convert_gloss_tts(new)
            c["item"]["gloss_alignment_status"] = "HUMAN_RESOLVED"
            c["japanese_gloss"] = new
            c["gates"]["gloss"] = "HUMAN_RESOLVED"
        cands = rv.save_candidates(kp_dir, cands)
        review["candidates_sha256"] = cands["candidates_sha256"]
        rv._event(review, "confirm_revise", "er128", {"candidate_ids": sorted(changes), "by": by})
        review = rv.save_review(kp_dir, review, expected_revision=review["revision"])
        sel = review["selection"]
        items = build_items(cands, rv.sel_ids(sel, "kp"), rv.sel_ids(sel, "vocab") if level == "b1b" else [])
        new_rec = _new_record(kp_dir=kp_dir, review=review, cands=cands, items=items, actor=ACTOR_USER, origin=dict(rec["origin"]), by=by, attestation=f"cli --by {by}",
                              user_ref=user_ref, comment=rec.get("comment") or "", unconsumed=rec.get("unconsumed"), prev=rec, event="revised", reason=reason,
                              confirmation_id=rec["confirmation_id"])
        new_rec["history"][-1]["extra"] = {"gloss_before": before, "gloss_after": changes}
        new_rec["history"][-1]["entry_sha256"] = _entry_sha(new_rec["history"][-1])
        save_record(kp_dir, new_rec)
        archived = _archive_final_outputs(kp_dir, "REVISE_SUPERSEDED")
    refinal = _try_refinalize(kp_dir, level)
    return {"revised": sorted(changes), "revision": new_rec["revision"], "archived": archived, "refinalized": refinal,
            "next": "制作コマンドを同じまま再実行してください(派生物は新しい訳から再生成されます)" if not refinal else "再finalize済み。制作コマンドを再実行してください"}


def _archive_final_outputs(kp_dir: str, tag: str) -> list:
    pth = rv.paths(kp_dir)
    out = []
    for k in ("kp", "vocab", "final"):
        a = rv.archive_if_exists(pth[k], tag)
        if a:
            out.append(a)
    return out


def _try_refinalize(kp_dir: str, level: str) -> bool:
    """確定物を候補docから決定論で再finalize(API 0)。確定集合のRedundancy QAが未実施で関数が要るときは諦め、次回のrunner起動に委ねる。"""
    try:
        rv.finalize_kp(kp_dir, level=level, redundancy_fn=None)
        return True
    except rv.ConfirmedContentIntegrityViolation:
        raise   # 再finalizeで確定レコードとずれたなら隠さない
    except rv.KpReviewError:
        return False


def cmd_restore(run: str, level: str, by: str, reason: str) -> dict:
    """INTEGRITY_VIOLATIONの復元(確定値を守る操作)。条件(i)原因が人間操作でないこと (ii)復元内容を報告 (iii)退避→候補docから再finalize。"""
    by = _need_by(by)
    if not (reason or "").strip():
        raise CliError("--reason が必須です")
    kp_dir = _kp_dir_for(run, level)
    with rv.review_lock(kp_dir, rv.KIND_KP, by):
        rec = load_record(kp_dir)
        if rec is None or rec.get("state") != STATE_LIVE:
            raise CliError("復元の対象となる確定レコード(live)がありません")
        probs = _problems_self(rec)
        if probs:
            raise CliError("確定レコード自体が壊れています。復元できません: " + "; ".join(probs))
        review, cands = rv.load_review(kp_dir), rv.load_candidates(kp_dir)
        at = (rec.get("confirmed_by") or {}).get("at") or ""
        human = [e for e in review.get("history") or [] if e.get("at", "") > at and (e.get("by") or "") not in _HUMAN_IGNORED_BY and e.get("event") != "candidates_generated"]
        if human:
            raise_issue(kp_dir, level, "確定後に人間の操作(review履歴)があります。パイプライン不具合ではない可能性があるため自動復元しません。", [
                {"candidate_id": None, "field": "review.history", "confirmed": at, "observed": f"{e.get('event')} by {e.get('by')} at {e.get('at')}", "where": "kp_human_review.json"} for e in human],
                proposal=["新しい値を採用するなら confirm-revise、確定値へ戻すなら revoke 後に再選択"], next_steps=None)
        if (rec.get("origin") or {}).get("candidates_sha256") != cands.get("candidates_sha256") or rv.candidates_sha256(cands) != cands.get("candidates_sha256"):
            raise_issue(kp_dir, level, "候補doc自体が確定時と異なります。復元では直せません。", [], proposal=["確定を revoke して選び直す"], next_steps=None)
        block, warn = _artifact_diffs(kp_dir, level, rec)
        restored = block + warn
        archived = _archive_final_outputs(kp_dir, "RESTORE_SUPERSEDED")
        rec["revision"] += 1
        _append_history(rec, event="restored", by=by, reason=reason, extra={"restored_fields": [(d["candidate_id"], d["field"]) for d in restored], "archived": archived})
        save_record(kp_dir, rec)
    refinal = _try_refinalize(kp_dir, level)
    return {"restored_fields": [(d["candidate_id"], d["field"], d["confirmed"], d["observed"]) for d in restored], "archived": archived, "refinalized": refinal,
            "note": "復元内容は完了報告に必ず列挙すること(黙って直さない)", "next": "制作コマンドを同じまま再実行してください(Zはassets copy/SRC D1も再実行されます)"}


def cmd_status(run: str) -> dict:
    rows = []
    for d in rv.discover_kp_dirs(run):
        review = rv.load_review(d)
        rec = load_record(d)
        row = {"kp_dir": d, "level": (review or {}).get("level"), "review_status": (review or {}).get("status"),
               "record": None if rec is None else {"state": rec.get("state"), "revision": rec.get("revision"), "actor": (rec.get("confirmed_by") or {}).get("actor"),
                                                   "origin": (rec.get("origin") or {}).get("kind"), "items": [(i["candidate_id"], i["category"], i["used_form"]) for i in rec["items"]],
                                                   "unconsumed": [(u["candidate_id"], u["reason"]) for u in rec.get("unconsumed") or []],
                                                   "self_problems": _problems_self(rec)},
               "legacy_drift_file": os.path.exists(paths_of(d)["legacy"]), "issue_file": os.path.exists(paths_of(d)["issue_json"])}
        rows.append(row)
    return {"run": run, "flag_enabled": protection_enabled(), "levels": rows}


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p, level=True):
        p.add_argument("--run", required=True)
        if level:
            p.add_argument("--level", required=True, choices=("a2", "b1b"))
    p = sub.add_parser("status")
    common(p, level=False)
    p = sub.add_parser("confirm")
    common(p)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--from-form", default=None)
    g.add_argument("--from-review", action="store_true")
    g.add_argument("--adopt-existing", action="store_true")
    p.add_argument("--apply", action="store_true", help="--adopt-existing: 差分提示のみ(既定)ではなく適用する")
    p.add_argument("--by", default=None)
    p.add_argument("--user-ref", default="")
    p = sub.add_parser("confirm-revise")
    common(p)
    p.add_argument("--gloss", action="append", default=[], help="<candidate_id>=<新訳>")
    p.add_argument("--reason", default="")
    p.add_argument("--by", default=None)
    p.add_argument("--user-ref", default="")
    p = sub.add_parser("revoke")
    common(p)
    p.add_argument("--reason", default="")
    p.add_argument("--by", default=None)
    p.add_argument("--user-ref", default="")
    p = sub.add_parser("restore")
    common(p)
    p.add_argument("--reason", default="")
    p.add_argument("--by", default=None)
    return ap


def run(argv=None) -> int:
    a = build_parser().parse_args(argv)
    try:
        if a.cmd == "status":
            out = cmd_status(a.run)
        elif a.cmd == "confirm":
            if a.from_form:
                out = cmd_from_form(a.run, a.level, a.from_form, a.by, a.user_ref)
            elif a.from_review:
                out = cmd_from_review(a.run, a.level, a.by, a.user_ref)
            else:
                out = cmd_from_review(a.run, a.level, a.by, a.user_ref, adopt_existing=True, apply=a.apply)
        elif a.cmd == "confirm-revise":
            out = cmd_revise(a.run, a.level, a.by, a.user_ref, a.reason, a.gloss)
        elif a.cmd == "revoke":
            out = cmd_revoke(a.run, a.level, a.by, a.user_ref, a.reason)
        else:
            out = cmd_restore(a.run, a.level, a.by, a.reason)
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0
    except rv.ConfirmedContentIssue as e:
        print(f"[CONFIRMED_CONTENT][ISSUE] {e}", file=sys.stderr)
        return rv.EXIT_CODE_PENDING
    except (CliError, rv.KpReviewError, ValueError) as e:
        print(f"[CONFIRMED_CONTENT][REFUSED] {type(e).__name__}: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(run())
