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
      (文法: payload の selection.grammar[] [原則1件・0件可・2件同時選択禁止。提示はTop1/Top2のみ]を、そのlevelの事前生成物[grammar_candidates.json / grammar_explanations.json]と逐語照合する。
       不一致=ISSUE[rc=4・修正案つき・何も書かない]。事前生成が未完了なら grammar-pregen を案内して拒否。0件は文法reviewをomitで確定[文法なしの確定も記録]。
       呼出順: 全検証 -> KPロック -> 文法ロック[gr.apply_form_selection] -> level別sidecar -> KPレコード保存[確定点]。同じ入力の再送は冪等。
       設計: docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/SCHEMA_CONTRACT_01.md §4/§5、IMPLEMENTATION_04.md)
  py er128_kp_confirmed_content_01.py confirm --from-form <payload.json> --grammar-pending --run <run> --level b1b --by <名> --user-ref <path>
      (KP先行確定: KP/KWだけを確定・保護し、文法は選定待ち[sidecar status=pending=0件確定ではない]のまま。payloadのgrammar[]は使わず無視を記録する)
  py er128_kp_confirmed_content_01.py confirm --grammar-from-form <payload.json> --run <run> --level b1b --by <名> --user-ref <path>
      (後から文法だけを確定。KPレコードの保護項目は不変。Top1/Top2のpresented_ids・解説全文逐語一致・1件以下。0件はomit。冪等)
  py er128_kp_confirmed_content_01.py confirm --from-review --run <run> --level a2 --by <名> --user-ref <path>
  py er128_kp_confirmed_content_01.py confirm --adopt-existing --run <run> --level a2 --by <名> --user-ref <path> [--apply]
  py er128_kp_confirmed_content_01.py confirm-revise --run <run> --level b1b --by <名> --user-ref <path> --reason ... --gloss <candidate_id>=<新訳>
  py er128_kp_confirmed_content_01.py revoke --run <run> --level b1b --by <名> --user-ref <path> --reason ...
  py er128_kp_confirmed_content_01.py reconsume --run <run> --level a2|b1b --by <名> --user-ref <path>
      (SLOT-23 委任_04B: 確定済みの既存記事を新表示仕様[display_spec=LEARNING_ITEMS_123_V1]へ明示的に移行する。ユーザー選定[①②③の候補ID・区分・件数]は変えない。
       a2: STD_CATEGORY2_NO_SLOTの②をitemsへ・reviewのstd_part1マークとselection.vocab[=①+②]を更新・確定Redundancy QAは次回runner起動で走る。b1b: record側のみ)
  py er128_kp_confirmed_content_01.py restore --run <run> --level b1b --by <名> --reason ...
"""
from __future__ import annotations

import argparse
import copy
import difflib
import unicodedata
import functools
import hashlib
import html as _htmlmod
import inspect
import json
import logging
import os
import re
import sys
from typing import Any, Optional

import er119_kp_human_review_01 as rv

_log = logging.getLogger("er128_kp_confirmed_content")

SCHEMA = "eigo_radio_confirmed_selection_v1"
SCHEMA_GRAMMAR = "eigo_radio_confirmed_grammar_v1"
SCHEMA_GRAMMAR_V2 = "eigo_radio_confirmed_grammar_v2"   # level別sidecar(level・explanation_sha_by_id付き。新規書込みはv2、v1は読取互換)
GRAMMAR_MAX = 1                                         # 文法の確定上限(er120.GRAMMAR_MAXと同値。突合test。2026-10-27ユーザー正式決定: 原則1件・0件可・2件同時選択禁止。旧2=撤去)
GRAMMAR_PENDING = "pending"                             # 文法の選定待ち(KPだけ先行確定。0件確定とは別。grammar_state=None=文法の保護なし)
VALID_LEVELS = ("a2", "b1b")
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
ACTOR_EVIDENCE = "evidence"               # 02B: runtime evidence用(ユーザー確定ではない)。保護の強度はuserと同じ(英語・訳・区分・文法を守る)が、記録上は明示的に区別する
ENFORCING_ACTORS = (ACTOR_USER, ACTOR_EVIDENCE)
ACTOR_AUTO = "auto"                       # 明示の不在宣言によるAUTO。ユーザー確定ではない(再確認要求の対象外。英語/区分は不変検査)

DISPLAY_SPEC_V1 = "LEARNING_ITEMS_123_V1"   # 確定レコードの表示仕様マーク(SLOT-23。新規作成=reviewのstd_part1から導出/継承、既存記事=reconsumeでのみ明示移行)
KNOWN_DISPLAY_SPECS = (DISPLAY_SPEC_V1,)
REASON_C3_HIGHLIGHT = "CATEGORY3_HIGHLIGHT"      # display_spec付きの③(本文の下線+短い日本語訳。消費者あり)
REASON_C3_NO_CONSUMER = "CATEGORY3_NO_CONSUMER"  # 旧(マーク無し)の③
REASON_C2_NO_SLOT = "STD_CATEGORY2_NO_SLOT"      # 旧(マーク無し)のStd②(Part 1が無かった)。display_spec付きでは0件でなければならない

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
    if rec.get("state") == STATE_LIVE and (rec.get("confirmed_by") or {}).get("actor") in ENFORCING_ACTORS:
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


def _display_spec_for_new(prev: Optional[dict], review: Optional[dict]) -> Optional[str]:
    """新レコードのdisplay_spec。前レコードがlive(確定中)ならそれを継承(遡及なし。マーク無しはマーク無しのまま)、
    前レコードが無い/取消済み/reconfirm_requiredなら新規扱いでreviewのstd_part1マークから導出する(マークはnew_reviewだけが発行する)。"""
    if prev is not None and prev.get("state") == STATE_LIVE:
        return prev.get("display_spec")
    return DISPLAY_SPEC_V1 if (review or {}).get("std_part1") else None


def _new_record(*, kp_dir: str, review: dict, cands: dict, items: list, actor: str, origin: dict, by: str, attestation: str,
                user_ref: str, comment: str = "", unconsumed: Optional[list] = None, prev: Optional[dict] = None,
                event: str = "confirmed", reason: str = "", confirmation_id: Optional[str] = None,
                display_spec: Optional[str] = None) -> dict:
    """display_spec引数=reconsume専用の明示指定(それ以外はNone=_display_spec_for_newの継承/導出)。レコードへ付与する付与点はここだけで、
    マーク自体の発行は(reviewの)new_reviewだけ。"""
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
    spec = display_spec if display_spec is not None else _display_spec_for_new(prev, review)
    if spec:   # マーク無しのレコードにはキーを作らない(旧レコードのrecord_sha256・バイトを変えない)
        rec["display_spec"] = spec
    _append_history(rec, event=event, by=by, reason=reason, user_ref=user_ref)
    return rec


def _rec_level(rec: dict) -> str:
    """確定レコードのlevel(a2|b1b)。無い/不正は暗黙のb1bにせずINTEGRITY(levelは必須。pathや既定値から推定しない)。"""
    lv = ((rec or {}).get("article") or {}).get("level")
    if lv not in VALID_LEVELS:
        raise rv.ConfirmedContentIntegrityViolation(f"CONFIRMED_CONTENT_INTEGRITY_VIOLATION: 確定レコードのlevelが不正です({lv!r})。a2|b1b のみ。levelから推定しません")
    return lv


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
    enforce_gloss = actor in ENFORCING_ACTORS
    pth = rv.paths(kp_dir)
    block, warn = [], []
    kp_by = _doc_items_by_id(pth["kp"]) or {}
    vocab_on = level == "b1b" or bool(rec.get("display_spec"))   # Std Part 1(display_spec付きa2)もvocab_confirmed.jsonと突合する
    vocab_by = _doc_items_by_id(pth["vocab"]) if vocab_on else None
    for ri in rec.get("items") or []:
        if ri["slot"] == "kp":
            b, w = _item_diffs(ri, kp_by.get(ri["candidate_id"]), "keywords_canonicalized.json", enforce_gloss=enforce_gloss)
            block += b
            warn += w
        if vocab_on:
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
    if rec.get("display_spec"):   # ③(本文の下線+短い日本語訳)の確定訳も保護する(display_spec付きレコードのみ。遡及なし)
        for u in rec.get("unconsumed") or []:
            if u.get("category") != 3:
                continue
            c = cm.get(u.get("candidate_id"))
            if c is None:
                out.append({"candidate_id": u.get("candidate_id"), "field": "(candidate:category3)", "confirmed": u.get("used_form"), "observed": None, "where": "kp_candidates.json:欠落"})
            elif ((c.get("item") or {}).get("japanese_gloss")) != u.get("japanese_gloss"):
                out.append({"candidate_id": u.get("candidate_id"), "field": "japanese_gloss(category3)", "confirmed": u.get("japanese_gloss"),
                            "observed": (c.get("item") or {}).get("japanese_gloss"), "where": "kp_candidates.json"})
    return out


def _display_spec_diffs(rec: dict, level: str, review: dict) -> list:
    """G1不変条件(SLOT-23 M8): display_spec ⇔ std_part1(a2は厳密一致、b1bはstd_part1付きならdisplay_spec必須)・display_spec付きなら
    STD_CATEGORY2_NO_SLOT/CATEGORY3_NO_CONSUMERの旧reasonが0件・未知のdisplay_specは拒否。マーク無し(旧run)は何も検査しない。"""
    out = []
    spec = rec.get("display_spec")
    mark = bool(review.get("std_part1"))
    if spec and spec not in KNOWN_DISPLAY_SPECS:
        out.append({"candidate_id": None, "field": "display_spec", "confirmed": spec, "observed": f"未知のdisplay_spec(既知={list(KNOWN_DISPLAY_SPECS)})", "where": "confirmed_selection.json"})
    if level == "a2" and bool(spec) != mark:
        out.append({"candidate_id": None, "field": "display_spec<=>std_part1", "confirmed": spec, "observed": f"review.std_part1={mark}",
                    "where": "confirmed_selection.json vs kp_human_review.json(a2はdisplay_specとstd_part1が一致していなければならない。移行は reconsume)"})
    if level == "b1b" and mark and not spec:
        out.append({"candidate_id": None, "field": "display_spec<=>std_part1", "confirmed": spec, "observed": f"review.std_part1={mark}",
                    "where": "confirmed_selection.json vs kp_human_review.json(std_part1付きreviewの確定レコードにdisplay_specが必要)"})
    if spec:
        for u in rec.get("unconsumed") or []:
            if u.get("reason") in (REASON_C2_NO_SLOT, REASON_C3_NO_CONSUMER):
                out.append({"candidate_id": u.get("candidate_id"), "field": "unconsumed.reason", "confirmed": u.get("reason"),
                            "observed": "display_spec付きでは旧reason(②はitemsへ、③は" + REASON_C3_HIGHLIGHT + ")", "where": "confirmed_selection.json"})
    return out


def display_spec_of(run: str, level: str) -> Optional[str]:
    """表示有効化判断用の純関数(委任_04B。flag非経由=protection_enabled()を見ない、書込みなし、load_record直読み)。
    そのrun・levelの確定レコードのdisplay_spec(取消済み/レコード無し=None)。未知の値はValueError(fail-closed)。"""
    for d in (f"{run}/{level}/key_phrases", f"{run}/key_phrases/{level}"):
        rec = load_record(d)
        if rec is None or rec.get("state") == STATE_REVOKED:
            continue
        if ((rec.get("article") or {}).get("level")) not in (None, level):
            continue
        spec = rec.get("display_spec")
        if spec and spec not in KNOWN_DISPLAY_SPECS:
            raise ValueError(f"未知のdisplay_spec: {spec!r}")
        return spec or None
    return None


def _grammar_problems(kp_dir: str, level: str, rec: dict) -> list:
    g = rec.get("grammar")
    if not g:
        return []
    if not g.get("path_rel"):   # 文法選定待ち(pending)でsidecar無し(文法のstudy dirがまだ無い)
        return [] if g.get("status") == GRAMMAR_PENDING else ["rec.grammarにpath_relがありません"]
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
    register_active_kp_dir(kp_dir)
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
    diffs += _display_spec_diffs(rec, level, review)
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
    items = build_items(cands, rv.sel_ids(sel, "kp"), rv.sel_ids(sel, "vocab") if rv.vocab_enabled(level, review) else [])
    pseudo = {"items": items, "confirmed_by": {"actor": ACTOR_USER}, "display_spec": _display_spec_for_new(None, review)}
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
    build = build_items(cands, rv.sel_ids(sel, "kp"), rv.sel_ids(sel, "vocab") if rv.vocab_enabled(level, review) else [])
    actor = _actor_for(review)
    sig = review.get("selection_signature")
    p = paths_of(kp_dir)["record"]
    rec = _read(p) if os.path.exists(p) else None
    by = _review_human_by(review) if actor == ACTOR_USER else "runner"
    origin = {"kind": "hr_cli" if actor == ACTOR_USER else "auto_declared"}
    if rec is not None and rec.get("state") == STATE_LIVE:
        a_prev = (rec.get("confirmed_by") or {}).get("actor")
        same = content_sha256(build) == rec.get("content_sha256") and (rec.get("origin") or {}).get("review_selection_signature") == sig
        if a_prev in ENFORCING_ACTORS:
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
# 02B-1: 稼働中の確定レコード登録(LR重なり警告用。プロセス内のみ・読取専用。挙動は変えない)
# ============================================================
_ACTIVE_KP_DIRS: dict = {}


def register_active_kp_dir(kp_dir: str) -> None:
    try:
        _ACTIVE_KP_DIRS[os.path.abspath(kp_dir)] = True
    except Exception:   # noqa: BLE001  登録失敗で本処理を止めない
        pass


# ============================================================
# 02B-2: M8 STALE再バインド(本文が変わったがユーザー確定itemの出典文が新本文に逐語で残る場合、API 0で連鎖更新)
# ============================================================
_QUOTE_MAP = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"'})


def _norm_ws(s: Optional[str]) -> str:
    """出典文の逐語照合用の正規化: NFKC・引用符(曲線→直線。候補docのsource_sentenceは直線引用符に正規化されている)・空白。大文字小文字は保持(逐語)。"""
    return " ".join(unicodedata.normalize("NFKC", s or "").translate(_QUOTE_MAP).split())


def _source_sentence_of(c: Optional[dict]) -> Optional[str]:
    it = (c or {}).get("item") or {}
    return it.get("source_sentence") or (c or {}).get("source_sentence")


def _grammar_sentences(kp_dir: str, rec: dict) -> list:
    """確定レコードに文法(sidecar)があれば [(grammar candidate_id, 選定文)]。候補docが読めなければ []。"""
    g = rec.get("grammar")
    if not g or not g.get("path_rel") or g.get("status") == GRAMMAR_PENDING:
        return []
    try:
        import er119_grammar_review_01 as gr
        run = _run_dir_of(kp_dir)
        side = _read(os.path.join(run, g["path_rel"]))
        sd = os.path.dirname(os.path.join(run, g["path_rel"]))
        doc = gr.load_candidates(sd) or {}
    except (OSError, ValueError, KeyError):
        return []
    by_id = {c.get("candidate_id"): c for c in doc.get("candidates") or []}
    out = []
    for it in side.get("items") or []:
        c = by_id.get(it.get("id"))
        if c and c.get("sentence"):
            out.append((it.get("id"), c["sentence"]))
    return out


def stale_or_rebind(kp_dir: str, text: str, new_text_sha: str) -> Optional[str]:
    """本文が変わった(text_sha256不一致)場面の入口。ユーザー確定レコードが無ければ None(従来のSTALE再生成)。
    各確定itemの出典文(と文法の選定文)が新本文に逐語で存在 → 候補doc.text_sha256→candidates_sha256→review署名→レコードを API 0 で連鎖更新して "REBOUND"。
    1つでも存在しない → ISSUE(確定内容は何も変更しない)の要約文を返す。"""
    rec = live_user_record(kp_dir)
    if rec is None or (rec.get("article") or {}).get("text_sha256") == new_text_sha:
        return None
    level = rec["article"].get("level")
    cands = rv.load_candidates(kp_dir)
    ntext = _norm_ws(text)
    missing = []
    if cands is None or cands.get("text_sha256") != (rec.get("article") or {}).get("text_sha256"):
        missing.append({"candidate_id": None, "field": "candidates.text_sha256", "confirmed": (rec.get("article") or {}).get("text_sha256"),
                        "observed": (cands or {}).get("text_sha256"), "where": "kp_candidates.json(確定時の本文と候補docが一致しない=再バインド不可)"})
    else:
        cm = _cand_map(cands)
        for it in rec.get("items") or []:
            sent = _source_sentence_of(cm.get(it["candidate_id"]))
            if not sent or _norm_ws(sent) not in ntext:
                missing.append({"candidate_id": it["candidate_id"], "field": "source_sentence", "confirmed": sent, "observed": "(新本文に逐語で存在しない)",
                                "where": "text_sha256変更"})
        for gid, sent in _grammar_sentences(kp_dir, rec):
            if _norm_ws(sent) not in ntext:
                missing.append({"candidate_id": gid, "field": "grammar.sentence", "confirmed": sent, "observed": "(新本文に逐語で存在しない)", "where": "text_sha256変更"})
    if missing:
        msg = (f"本文(text_sha256)が変わり({str((rec['article'] or {}).get('text_sha256'))[:12]}→{new_text_sha[:12]})、ユーザー確定済みの出典文が新本文に逐語で残っていない項目があります。"
               "確定内容を黙って破棄/再選定しません。")
        _write_issue(kp_dir, kind="CONFIRMED_CONTENT_ISSUE", summary=msg, diffs=missing,
                     next_steps=[f"{_cli(kp_dir, 'revoke')} --level {level} --by <名> --user-ref <ユーザー発言> --reason '本文変更に伴う選び直し' (その後に制作を再実行→候補再生成)"],
                     proposal=["出典文を変更した項目は、新しい出典文で選び直す(revoke→再選択)か、本文の当該文を元に戻してください"])
        return msg
    with rv.review_lock(kp_dir, rv.KIND_KP, "er128"):
        review, cands = rv.load_review(kp_dir), rv.load_candidates(kp_dir)
        old_c, old_t, old_sig = cands["candidates_sha256"], cands["text_sha256"], review.get("selection_signature")
        pth = rv.paths(kp_dir)
        rv.archive_if_exists(pth["candidates"], "REBOUND_SUPERSEDED")
        doc = dict(cands)
        doc["text_sha256"] = new_text_sha
        doc = rv.save_candidates(kp_dir, doc)
        review["text_sha256"], review["candidates_sha256"] = new_text_sha, doc["candidates_sha256"]
        rv._event(review, "rebind_text", "er128", {"old_text_sha256": old_t, "new_text_sha256": new_text_sha, "old_candidates_sha256": old_c,
                                                    "new_candidates_sha256": doc["candidates_sha256"], "note": "確定itemの出典文が新本文に逐語で存在(API 0)"})
        review = rv.save_review(kp_dir, review, expected_revision=review["revision"])
        rv.retire_final_outputs(kp_dir, "REBOUND_SUPERSEDED")
        rec2 = copy.deepcopy(rec)
        rec2["article"]["text_sha256"] = new_text_sha
        rec2["origin"]["candidates_sha256"] = doc["candidates_sha256"]
        rec2["origin"]["review_selection_signature"] = review["selection_signature"]
        rec2["revision"] += 1
        _append_history(rec2, event="rebound_text", by="er128", reason="本文変更(確定itemの出典文は新本文に逐語で存在)",
                        extra={"old_text_sha256": old_t, "new_text_sha256": new_text_sha, "old_candidates_sha256": old_c,
                               "new_candidates_sha256": doc["candidates_sha256"], "old_review_selection_signature": old_sig,
                               "new_review_selection_signature": review["selection_signature"]})
        save_record(kp_dir, rec2)
    return "REBOUND"


# ============================================================
# 02B-3: G2(TTS record)・G3(ページHTML/Part 1行)。verify_selection_matches_outputs の末尾から呼ぶ(読取専用・API 0)
# ============================================================
def _tts_text(ent: Optional[dict]) -> Optional[str]:
    """TTS recordの読み上げ元text。Master Store再利用recordは`text`を持たないことがあるので`canonical_text`で比較する(誤BLOCK回避)。両方無ければNone。"""
    if not isinstance(ent, dict):
        return None
    return ent.get("text") if ent.get("text") is not None else ent.get("canonical_text")


def _page_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return _htmlmod.unescape(f.read())


def verify_outputs(kp_dir: str, level: str, *, tts_results_path: Optional[str] = None, study_text_json: Optional[str] = None,
                   page_paths: Optional[list] = None, vocab_page_paths: Optional[list] = None, gloss_page_paths: Optional[list] = None) -> None:
    """G2/G3(AND追加・fail-closed)。レコードが無い/保護OFF/取消済み=何もしない。違反はINTEGRITY(rc=3)。actor=autoのgloss差はWARNのみ(英語は常にBLOCK)。
    G2: TTS record。英語=used_form、Std日本語=派生物契約(japanese_gloss_tts または convert(japanese_gloss))。
    G3: ページHTML。Std=表示用japanese_glossがページに出ること、Adv=Part 1が描画されているときPart 1の行(meaning_in_text_ja)と描画。"""
    if not protection_enabled():
        return
    rec = load_record(kp_dir)
    if rec is None or rec.get("state") != STATE_LIVE:
        return
    enforce = (rec.get("confirmed_by") or {}).get("actor") in ENFORCING_ACTORS
    pth = rv.paths(kp_dir)
    kp_art = {it.get("candidate_id"): it for it in (_read(pth["kp"]).get("items") or [])} if os.path.exists(pth["kp"]) else {}
    block, warn = [], []

    def _put(d, is_gloss=True):
        (block if (enforce or not is_gloss) else warn).append(d)

    if tts_results_path and os.path.exists(tts_results_path):
        kps = _read(tts_results_path).get("key_phrases") or {}
        for ri in rec.get("items") or []:
            if ri["slot"] != "kp":
                continue
            art = kp_art.get(ri["candidate_id"])
            if art is None:
                continue   # artifact欠落はG1の担当
            ent = kps.get(str(art.get("rank"))) or {}
            en = _tts_text(ent.get("english"))
            if en is not None and en != ri["used_form"]:
                block.append({"candidate_id": ri["candidate_id"], "field": "used_form(TTS英語)", "confirmed": ri["used_form"], "observed": en, "where": "tts_generation_results.json"})
            pr = _tts_text(ent.get("phrase_repeat"))   # 委任_03: Adv/X のKP復唱(phrase_repeat)も同じ確定英語でなければならない(英語の二重読み上げの片方だけ改変を見逃さない)
            if pr is not None and pr != ri["used_form"]:
                block.append({"candidate_id": ri["candidate_id"], "field": "used_form(TTS復唱 phrase_repeat)", "confirmed": ri["used_form"], "observed": pr, "where": "tts_generation_results.json"})
            jm = _tts_text(ent.get("japanese_meaning")) if level == "a2" else None
            if jm is not None:
                ok = {(ri.get("derived") or {}).get("japanese_gloss_tts"), convert_gloss_tts(ri.get("japanese_gloss"))}
                if jm not in ok:
                    _put({"candidate_id": ri["candidate_id"], "field": "japanese_meaning(TTS日本語。派生物契約: 確定訳の決定論変換でなければならない)",
                          "confirmed": convert_gloss_tts(ri.get("japanese_gloss")), "observed": jm, "where": "tts_generation_results.json"})
    if level == "a2":
        # Std日本語訳の表示ページ。gloss_page_pathsが無ければ page_paths とその同じdirの index.html(Zの詳細確認ページは読み上げ用scriptを載せるため、利用者向けの表示は index.html)のどれかに出ていればよい
        pages = list(gloss_page_paths or [])
        if not pages:
            for pg in page_paths or []:
                pages.append(pg)
                idx = os.path.join(os.path.dirname(pg), "index.html")
                if idx not in pages and os.path.exists(idx):
                    pages.append(idx)
        texts = [_page_text(pg) for pg in pages if os.path.exists(pg)]   # ページの存在自体はverify_selection_matches_outputs本体の検査
        if texts:
            for ri in rec.get("items") or []:
                if ri["slot"] == "kp" and ri.get("japanese_gloss") and not any(ri["japanese_gloss"] in t for t in texts):
                    _put({"candidate_id": ri["candidate_id"], "field": "japanese_gloss(ページ表示)", "confirmed": ri["japanese_gloss"], "observed": "(ページに表示されていない)",
                          "where": ",".join(os.path.basename(pg) for pg in pages)})
    if (level == "b1b" or rec.get("display_spec")) and vocab_page_paths:   # (elifではない: display_spec付きa2はStd訳検査に加えPart 1も検査する)。Part 1が描画されているページに限る(描画されていなければ検査しない)。Std Part 1(display_spec付きa2)もlevel化(委任_05M)
        texts = [_page_text(pg) for pg in vocab_page_paths if os.path.exists(pg)]
        if texts:
            for ri in rec.get("items") or []:
                if ri.get("japanese_gloss") and not any(ri["japanese_gloss"] in t for t in texts):
                    _put({"candidate_id": ri["candidate_id"], "field": "japanese_gloss(Part 1表示)", "confirmed": ri["japanese_gloss"], "observed": "(Part 1に表示されていない)",
                          "where": ",".join(os.path.basename(pg) for pg in vocab_page_paths)})
        if study_text_json and os.path.exists(study_text_json):
            rows = {r.get("english_expression"): r for r in (_read(study_text_json).get("rows") or [])}
            for ri in rec.get("items") or []:
                row = rows.get(ri["used_form"])
                if row is not None and row.get("meaning_in_text_ja") != ri.get("japanese_gloss"):
                    _put({"candidate_id": ri["candidate_id"], "field": "japanese_gloss(Part 1行 meaning_in_text_ja)", "confirmed": ri.get("japanese_gloss"),
                          "observed": row.get("meaning_in_text_ja"), "where": os.path.basename(study_text_json)})
    if warn:
        _log.warning("confirmed content (actor=auto) output drift warn: %s", warn)
    if block:
        raise_integrity(kp_dir, level, block, "確定内容と音声/ページ/Part 1の出力が一致しません(G2/G3: 確定後に書換えられた、または別訳が表示/読み上げられた)。")


# ============================================================
# 02B-4: M6/G4 Part 2(文法)の凍結。確定レコード(confirmed_grammar.json)がある文法は、再抽出・再解説せず凍結した解説全文を使う
# ============================================================
FILE_GRAMMAR_FROZEN = "confirmed_grammar_frozen.json"
SCHEMA_GRAMMAR_FROZEN = "eigo_radio_confirmed_grammar_frozen_v1"      # 読取互換のみ(新規書込みはv2)
SCHEMA_GRAMMAR_FROZEN_V2 = "eigo_radio_confirmed_grammar_frozen_v2"   # items[](最大1件=GRAMMAR_MAX。v2形式は維持)
_TRANSLATION_RE = re.compile(r"【日本語訳】\s*(.*?)(?=\n\s*【|\Z)", re.S)


def translation_from_explanation_full(text: Optional[str]) -> Optional[str]:
    """`explanation_full`の【日本語訳】節を決定論で取り出す(無ければNone)。"""
    m = _TRANSLATION_RE.search(text or "")
    return m.group(1).strip() if m and m.group(1).strip() else None


def frozen_sha(candidate_id: str, sentence: str, explanation_md: str, translation_ja: Optional[str]) -> str:
    return hashlib.sha256(json.dumps([candidate_id, sentence, explanation_md, translation_ja], ensure_ascii=False).encode("utf-8")).hexdigest()


def frozen_token(fz: dict) -> str:
    return "frozen:" + fz["frozen_sha256"][:16]


def grammar_state(study_dir: str) -> Optional[dict]:
    """sidecar(confirmed_grammar.json)+ユーザー確定レコード(live)。無い/保護OFF/取消済み=None。sidecar自己整合違反=INTEGRITY。"""
    if not protection_enabled():
        return None
    sp = os.path.join(study_dir, FILE_GRAMMAR)
    if not os.path.exists(sp):
        return None
    side = _read(sp)
    rel = side.get("kp_dir_rel")
    if not rel or side.get("status") == GRAMMAR_PENDING:   # 選定待ち(pending)は『文法の確定』ではない=保護しない(0件確定と区別)
        return None
    kp_dir = os.path.normpath(os.path.join(study_dir, rel))
    rec = load_record(kp_dir)
    if rec is None or rec.get("state") != STATE_LIVE or not rec.get("grammar") or rec["grammar"].get("status") == GRAMMAR_PENDING:
        return None
    level = _rec_level(rec)
    bad = []
    if _jsha({k: v for k, v in side.items() if k != "sidecar_sha256"}) != side.get("sidecar_sha256") or side.get("sidecar_sha256") != rec["grammar"].get("sidecar_sha256"):
        bad.append("confirmed_grammar.json のshaが不一致(文法の確定内容が書換えられた疑い)")
    if side.get("confirmation_id") != rec.get("confirmation_id"):
        bad.append("confirmed_grammar.json の confirmation_id が確定レコードと一致しません")
    if side.get("schema") == SCHEMA_GRAMMAR_V2 and side.get("level") != level:
        bad.append(f"confirmed_grammar.json のlevel({side.get('level')!r})が確定レコードのlevel({level!r})と一致しません(別levelのsidecarの混入)")
    if bad:
        raise_integrity(kp_dir, level, [{"candidate_id": None, "field": "grammar", "confirmed": "(自己整合)", "observed": x, "where": FILE_GRAMMAR} for x in bad],
                        "文法の確定内容(sidecar)の整合が崩れています。")
    return {"sidecar": side, "rec": rec, "kp_dir": kp_dir, "level": level}


def _single(items: Optional[list]) -> Optional[dict]:
    """v1互換API用: 凍結が1件ならそのitem。2件以上(旧仕様の凍結)は複数対応のAPI(*_items)で読む(黙って先頭だけを返さない)。新仕様の新規確定は1件以下。"""
    if not items:
        return None
    if len(items) > 1:
        raise rv.KpReviewError("確定した文法が複数(2件)あります。複数対応のAPI(load_frozen_grammar_items / freeze_*_items / verify_part2_items)を使ってください")
    return items[0]


def _side_ids(st: dict) -> list:
    return [it.get("id") for it in st["sidecar"].get("items") or []]


def _fz_items_of(fz: dict) -> list:
    """凍結ファイルのitem列。v2=items[]、v1(トップレベルに単一item)=長さ1として読む(読取互換。書き換えない)。"""
    if isinstance(fz.get("items"), list):
        return list(fz["items"])
    return [fz]


def load_frozen_grammar_items(study_dir: str) -> Optional[list]:
    """凍結済みの解説item列(confirmed_grammar_frozen.json。v2=items[]、v1=長さ1)。確定レコードが無い/凍結がまだ無い=None。
    自己sha・confirmation_id・各item sha・確定した文法集合との一致(全件揃い・過不足なし)が崩れていればINTEGRITY(G4)。"""
    st = grammar_state(study_dir)
    if st is None:
        return None
    p = os.path.join(study_dir, FILE_GRAMMAR_FROZEN)
    if not os.path.exists(p):
        return None
    fz = _read(p)
    items = _fz_items_of(fz)
    ids = set(_side_ids(st))
    bad = []
    if _jsha({k: v for k, v in fz.items() if k != "file_sha256"}) != fz.get("file_sha256"):
        bad.append("凍結した解説(confirmed_grammar_frozen.json)のshaが不一致(書換えられた疑い)")
    if fz.get("confirmation_id") != st["rec"].get("confirmation_id"):
        bad.append("凍結した解説が確定レコードと対応していません(confirmation_id不一致)")
    seen = []
    for it in items:
        cid = it.get("candidate_id")
        if cid not in ids or cid in seen:
            bad.append(f"凍結した解説に確定した文法にない/重複した項目があります({cid})")
        seen.append(cid)
        if frozen_sha(cid, it.get("sentence"), it.get("explanation_md"), it.get("translation_ja")) != it.get("frozen_sha256"):
            bad.append(f"凍結した解説の内容shaが不一致({cid})")
    if set(seen) != ids:
        bad.append(f"凍結した解説が確定した文法集合と一致しません(凍結={sorted(x for x in seen if x)} / 確定={sorted(ids)})")
    if bad:
        raise_integrity(st["kp_dir"], st["level"], [{"candidate_id": None, "field": "grammar_explanation", "confirmed": "(凍結値)", "observed": x,
                                                      "where": FILE_GRAMMAR_FROZEN} for x in bad], "文法解説の凍結値の整合が崩れています(G4)。")
    return items


def load_frozen_grammar(study_dir: str) -> Optional[dict]:
    """v1互換(単一item)。2件以上の凍結は load_frozen_grammar_items を使う。"""
    return _single(load_frozen_grammar_items(study_dir))


def _write_frozen_items(study_dir: str, st: dict, specs: list) -> list:
    """凍結値(v2: items[])を全件まとめて1ファイルへ書く(all-or-nothing)。specs=[{candidate_id,sentence,construct_ja,explanation_md,sections,translation_ja,ref_ja,source}]。"""
    items = [{"candidate_id": s["candidate_id"], "sentence": s["sentence"], "construct_ja": s.get("construct_ja"), "explanation_md": s["explanation_md"],
              "sections": s.get("sections") or {}, "translation_ja": s.get("translation_ja"), "ref_ja_at_freeze": s.get("ref_ja"), "source": s["source"],
              "frozen_sha256": frozen_sha(s["candidate_id"], s["sentence"], s["explanation_md"], s.get("translation_ja"))} for s in specs]
    fz = {"schema": SCHEMA_GRAMMAR_FROZEN_V2, "confirmation_id": st["rec"]["confirmation_id"], "items": items, "frozen_at": rv._now()}
    fz["file_sha256"] = _jsha({k: v for k, v in fz.items() if k != "file_sha256"})
    _write(os.path.join(study_dir, FILE_GRAMMAR_FROZEN), fz)
    return items


def _result_items_norm(result: Optional[dict]) -> list:
    """Part 2結果(v2=items[] / v1=単一)を [{candidate_id,sentence,construct_ja,explanation_md,sections,translation_ja,ref_ja}] へ。ZERO/結果なし=[]。"""
    if not result or result.get("status") != "SELECTED":
        return []
    raw = result.get("items") if isinstance(result.get("items"), list) else None
    if raw is None:
        raw = [result] if result.get("selection") else []
    out = []
    for it in raw:
        sel = it.get("selection") or {}
        out.append({"candidate_id": sel.get("candidate_id"), "sentence": sel.get("sentence"), "construct_ja": sel.get("construct_ja"), "explanation_md": it.get("explanation_md"),
                    "sections": it.get("sections") or {}, "translation_ja": it.get("translation_ja"), "ref_ja": it.get("ref_ja")})
    return out


def freeze_part2_result_items(study_dir: str, result: dict) -> Optional[list]:
    """確定レコードのある文法で、まだ凍結が無ければ現在の(通常の検査を通った)Part 2結果(v2 items[])を全件凍結する(出所=stepB_generated_frozen)。
    凍結済み=既存を返す(上書きしない)。ZERO/確定レコード無し/確定が0件=None。結果の文法集合が確定した集合と異なればINTEGRITY(G4)。"""
    st = grammar_state(study_dir)
    items = _result_items_norm(result)
    if st is None or not items:
        return None
    cur = load_frozen_grammar_items(study_dir)
    if cur is not None:
        return cur
    ids = set(_side_ids(st))
    got = [i["candidate_id"] for i in items]
    if set(got) != ids or len(set(got)) != len(got):
        raise_integrity(st["kp_dir"], st["level"], [{"candidate_id": None, "field": "grammar_id", "confirmed": sorted(ids), "observed": got, "where": "part2_result.json"}],
                        "Part 2の選定が確定した文法と異なります(G4)。")
    return _write_frozen_items(study_dir, st, [dict(i, source="stepB_generated_frozen") for i in items])


def freeze_part2_result(study_dir: str, result: dict) -> Optional[dict]:
    """v1互換(単一item)。"""
    return _single(freeze_part2_result_items(study_dir, result))


def freeze_from_sidecar_items(study_dir: str, selected_candidates: list) -> Optional[list]:
    """sidecarに`explanation_status=provided`(フォームで見せた解説全文)があれば、Step Bを呼ばずそれを凍結値にする(出所=form_displayed。全件揃っている場合のみ)。
    構造が不正なら ISSUE(再確認)。provided無し/選定0件/確定レコード無し=None、凍結済み=既存。選定が確定した文法集合と異なればINTEGRITY。"""
    st = grammar_state(study_dir)
    if st is None:
        return None
    cur = load_frozen_grammar_items(study_dir)
    if cur is not None:
        return cur
    if not selected_candidates:
        return None
    ids = set(_side_ids(st))
    got = [c["candidate_id"] for c in selected_candidates]
    if set(got) != ids or len(set(got)) != len(got):
        raise_integrity(st["kp_dir"], st["level"], [{"candidate_id": None, "field": "grammar_id", "confirmed": sorted(ids), "observed": got, "where": "part2 selection"}],
                        "Part 2の選定が確定した文法と異なります(G4)。")
    side_by = {it.get("id"): it for it in st["sidecar"].get("items") or []}
    if any(side_by[i].get("explanation_status") != "provided" or not (side_by[i].get("explanation_full") or "").strip() for i in got):
        return None
    import er120_part2_grammar_production_01 as g
    specs = []
    for c in selected_candidates:
        full = side_by[c["candidate_id"]]["explanation_full"].strip()
        try:
            secs = g.split_sections(full)
        except (g.Part2Error, g.Part2StructureError) as e:
            raise_issue(st["kp_dir"], st["level"], "フォームで確認した文法解説全文がPart 2の構造(【日本語訳】【仕組み】【意味】)に合わず、そのまま採用できません。", [
                {"candidate_id": c["candidate_id"], "field": "explanation_full", "confirmed": full[:60], "observed": str(e)[:120], "where": FILE_GRAMMAR}],
                proposal=["解説全文の構造を修正した上で再確認してください(AIは解説を作り直して差し替えません)"])
        specs.append({"candidate_id": c["candidate_id"], "sentence": c["sentence"], "construct_ja": c.get("construct_ja"), "explanation_md": full, "sections": secs,
                      "translation_ja": secs.get("日本語訳"), "ref_ja": None, "source": "form_displayed"})
    return _write_frozen_items(study_dir, st, specs)


def freeze_from_sidecar(study_dir: str, candidate: dict) -> Optional[dict]:
    """v1互換(単一item)。"""
    return _single(freeze_from_sidecar_items(study_dir, [candidate]))


def _review_shown_sha_diffs(study_dir: str, st: dict) -> list:
    """確定時にreviewへ記録した『提示した解説のid別sha』(decision.explanation_sha_by_id)が、sidecarの解説shaと一致すること(フォーム提示=確定=公開の一致)。"""
    try:
        import er119_grammar_review_01 as gr
        review = gr.load_review(study_dir)
    except (OSError, ValueError):
        return []
    shown = ((review or {}).get("decision") or {}).get("explanation_sha_by_id") or {}
    out = []
    for it in st["sidecar"].get("items") or []:
        sha = it.get("explanation_sha256")
        if sha and shown and shown.get(it.get("id")) not in (None, sha):
            out.append({"candidate_id": it.get("id"), "field": "explanation_sha256", "confirmed": sha[:16], "observed": str(shown.get(it.get("id")))[:16],
                        "where": "grammar_human_review.json decision.explanation_sha_by_id"})
    return out


def verify_part2_items(study_dir: str, result: Optional[dict]) -> None:
    """G4: Part 2結果(part2_result.json。v2=items[] / v1=単一)が確定した文法集合・凍結した解説全文と一致すること(AND追加・fail-closed)。確定レコード無し=何もしない。
    確定した文法が1件以上あるのに結果がZERO/別の集合ならBLOCK。確定が0件(フォームで文法なし)なのに結果が文法を持つ場合もBLOCK。
    凍結がまだ無い(確定直後)場合は文法idだけ照合する(freeze_part2_result_itemsが次の通過点で凍結する)。"""
    st = grammar_state(study_dir)
    if st is None:
        return
    ids = set(_side_ids(st))
    norm = _result_items_norm(result)
    diffs = _review_shown_sha_diffs(study_dir, st)
    if not ids:
        if norm:
            diffs.append({"candidate_id": None, "field": "grammar", "confirmed": [], "observed": [i["candidate_id"] for i in norm], "where": "part2_result.json(フォームで文法なしを確定済み)"})
    elif not norm:
        diffs.append({"candidate_id": None, "field": "grammar", "confirmed": sorted(ids), "observed": (result or {}).get("status") or "(Part 2結果なし)", "where": "part2_result.json"})
    else:
        got = [i["candidate_id"] for i in norm]
        for cid in sorted(ids - set(got)):
            diffs.append({"candidate_id": cid, "field": "grammar_id", "confirmed": sorted(ids), "observed": f"{cid}が結果にない", "where": "part2_result.json"})
        for cid in sorted(set(got) - ids):
            diffs.append({"candidate_id": cid, "field": "grammar_id", "confirmed": sorted(ids), "observed": cid, "where": "part2_result.json"})
        if len(set(got)) != len(got):
            diffs.append({"candidate_id": None, "field": "grammar_id", "confirmed": sorted(ids), "observed": got, "where": "part2_result.json(重複)"})
        fz_by = {f["candidate_id"]: f for f in (load_frozen_grammar_items(study_dir) or [])}
        for n in norm:
            fz = fz_by.get(n["candidate_id"])
            if fz is None:
                continue
            if n["sentence"] != fz["sentence"]:
                diffs.append({"candidate_id": n["candidate_id"], "field": "grammar_sentence", "confirmed": fz["sentence"], "observed": n["sentence"], "where": "part2_result.json"})
            if n["explanation_md"] != fz["explanation_md"]:
                diffs.append({"candidate_id": fz["candidate_id"], "field": "explanation_md(解説全文)", "confirmed": fz["explanation_md"][:80], "observed": str(n["explanation_md"])[:80],
                              "where": "part2_result.json"})
            if fz.get("translation_ja") is not None and n["translation_ja"] != fz["translation_ja"]:
                diffs.append({"candidate_id": fz["candidate_id"], "field": "translation_ja(日本語訳)", "confirmed": fz["translation_ja"], "observed": n["translation_ja"], "where": "part2_result.json"})
    if diffs:
        raise_integrity(st["kp_dir"], st["level"], diffs, "Part 2が確定した文法・解説全文と一致しません(G4: 確定後に書換えられた、または別の解説が生成された)。")


def verify_part2(study_dir: str, result: Optional[dict]) -> None:
    """v1互換(同じ検査。単一結果もitems[]もverify_part2_itemsで検査する)。"""
    verify_part2_items(study_dir, result)


def guard_grammar(study_dir: str, op: str, *, candidate_id: Optional[str] = None, candidate_ids: Optional[list] = None) -> None:
    """確定した文法(sidecar)がある間は、選定を書き換え得る操作(reselect/omit/reextract/ng/unng/--regenerate-stage part2_cand_b1b)を拒否する(revoke必須)。
    確定した文法集合と**完全に同じ**候補を選ぶ pick/top1/top2(candidate_ids=確定集合、または確定が1件のときのcandidate_id)は許可する(確定を実際のreviewへ反映する操作で、書換えではない)。
    確定が0件(フォームで文法なし)の場合、許可されるのは同じ0件(candidate_ids=[])のみ。"""
    st = grammar_state(study_dir)
    if st is None:
        return
    ids = set(_side_ids(st))
    if candidate_ids is not None and set(candidate_ids) == ids and len(candidate_ids) == len(ids):
        return
    if candidate_id is not None and ids == {candidate_id}:
        return
    lv = st["level"]
    raise rv.ConfirmedContentLocked(
        f"CONFIRMED_CONTENT_LOCKED: 文法(Part 2)の {op} は拒否されました。ユーザー確定済みの文法があります(candidate_id={sorted(ids)})。"
        f"変更は `{_cli(st['kp_dir'], 'revoke')} --level {lv} --by <名> --user-ref <ユーザー発言> --reason ...`(確定の取消→選び直し)のみ(ユーザー確認済みの操作)。")


def pool_ref_ja_issue(study_dir: str, fz: dict, pool_value: Optional[str]) -> Optional[str]:
    """M6: 新しいPart 1訳poolの値が、確定(凍結)時点の訳(translation_ja / 凍結時のref_ja)と異なる場合のみISSUEを記録して要約を返す(一致・poolに無い=None)。
    確定した解説を黙って作り直さない(再生成しない)。"""
    if not pool_value or pool_value in {fz.get("translation_ja"), fz.get("ref_ja_at_freeze")}:
        return None
    st = grammar_state(study_dir)
    msg = (f"Part 1の日本語訳(参考訳pool)が、確定した文法解説の日本語訳({str(fz.get('translation_ja'))[:30]}…)と異なります。"
           "確定した解説を黙って作り直さず、ユーザーの再確認を待ちます。")
    if st is not None:
        _write_issue(st["kp_dir"], kind="CONFIRMED_CONTENT_ISSUE", summary=msg,
                     diffs=[{"candidate_id": fz.get("candidate_id"), "field": "ref_ja(Part 1訳pool)", "confirmed": fz.get("translation_ja"), "observed": pool_value, "where": "Part 1訳pool"}],
                     next_steps=[f"{_cli(st['kp_dir'], 'revoke')} --level {st['level']} --by <名> --user-ref <ユーザー発言> --reason ... (文法の確定を取り消して選び直す)"],
                     proposal=["Part 1の訳を変更したのなら、文法解説の【日本語訳】を新しい訳に合わせるかどうかをユーザーが確認してください"])
    return msg


# ============================================================
# 02B-5: Z `_gloss_person_gate`(人称整合の自動修復)がユーザー確定itemに触れる場合は、修復LLMを呼ばずISSUE
# ============================================================
def person_gate_issue(kp_dir: str, level: str, mismatches: list) -> None:
    """ユーザー確定レコード(live, actor=user)のitemが人称不整合として検出された場合、gloss再整合(有料LLM)をせずISSUE(rc=4相当)。
    該当なし(レコード無し/AUTO/他item)=何もしない(従来の自動修復へ)。mismatches=ga.select_person_mismatches(items)の戻り(candidate_id付き)。"""
    rec = live_user_record(kp_dir)
    if rec is None:
        return
    import er003_key_words_gloss_alignment as ga
    by_id = {i["candidate_id"]: i for i in rec.get("items") or []}
    hit = [m for m in mismatches if m.get("candidate_id") in by_id]
    if not hit:
        return
    diffs, props = [], []
    for m in hit:
        ri = by_id[m["candidate_id"]]
        reason = ga.person_reference_mismatch(m.get("key_phrase"), m.get("japanese_gloss"))
        diffs.append({"candidate_id": ri["candidate_id"], "field": "japanese_gloss(人称整合)", "confirmed": ri["japanese_gloss"], "observed": f"人称不整合の疑い: {reason}",
                      "where": "stage_kp(_gloss_person_gate)"})
        props.append(f"{ri['used_form']}: 確定訳「{ri['japanese_gloss']}」を、指示対象が不定の人称なら人称語を含まない訳へ直す案(例: confirm-revise --gloss {ri['candidate_id']}=<人称語を除いた訳>)。"
                     "現状のまま使う場合は、その旨をユーザーが確認してください(AIは確定した訳を自動で書き換えません)")
    raise_issue(kp_dir, level, "ユーザー確定済みの日本語訳に人称・指示対象の不整合の疑いがあります。確定した訳を自動修復(LLM再生成)せず、ユーザーの再確認を待ちます。", diffs, proposal=props)


# ============================================================
# 02B-6: LR(Local Rewrite)重なり警告(記録のみ。LRの挙動・候補選定は不変)
# ============================================================
def _toks(s: str) -> list:
    return re.findall(r"[A-Za-z0-9']+", s or "")


def lr_overlap(rec_items: list, before: str, after: str) -> list:
    """LRで書き換わった語範囲と、確定KPの本文出現位置(display_phrase/used_form/key_phrase)の重なりを返す(純関数)。"""
    tb, ta = _toks(before), _toks(after)
    lb, la = [t.lower() for t in tb], [t.lower() for t in ta]
    changed = set()
    for tag, i1, i2, _j1, _j2 in difflib.SequenceMatcher(None, lb, la, autojunk=False).get_opcodes():
        if tag != "equal":
            changed.update(range(i1, max(i2, i1 + 1)))   # 挿入(i1==i2)は直前語を含む位置として扱う
    out = []
    for it in rec_items:
        found = False
        for form in dict.fromkeys(x for x in (it.get("display_phrase"), it.get("used_form"), it.get("key_phrase")) if x):
            ft = [t.lower() for t in _toks(form)]
            if not ft or found:
                continue
            for i in range(0, len(lb) - len(ft) + 1):
                if lb[i:i + len(ft)] == ft:
                    hit = sorted(set(range(i, i + len(ft))) & changed)
                    if hit:
                        out.append({"candidate_id": it["candidate_id"], "form": form, "before_span": " ".join(tb[i:i + len(ft)]),
                                    "changed_token_positions": hit, "before_snippet": " ".join(tb[max(0, i - 4):i + len(ft) + 4])})
                        found = True
                        break
    return out


def note_lr_fired(segment_id: str, before: str, after: str) -> None:
    """LR発火時にer020から呼ばれる(記録のみ・例外は握る)。稼働中(このプロセスでG1を通った)確定レコードのKPと本文の重なりを
    `<run>/<lv>/audit/confirmed_kp_lr_overlap.json` に追記する。LRの挙動・採用/不採用には一切影響しない。"""
    if not protection_enabled():
        return
    for kp_dir in list(_ACTIVE_KP_DIRS):
        try:
            rec = load_record(kp_dir)
            if rec is None or rec.get("state") != STATE_LIVE:
                continue
            hits = lr_overlap(rec.get("items") or [], before, after)
            if not hits:
                continue
            outp = os.path.join(os.path.dirname(paths_of(kp_dir)["mirror"]), "confirmed_kp_lr_overlap.json")
            doc = _read(outp) if os.path.exists(outp) else {"kind": "confirmed_kp_lr_overlap", "note": "記録のみ(LR挙動は不変)。確定KPの出現位置とLRの書換え範囲が重なった",
                                                              "events": []}
            doc["events"].append({"at": rv._now(), "segment_id": segment_id, "confirmation_id": rec.get("confirmation_id"), "overlaps": hits})
            _write(outp, doc)
        except Exception as e:   # noqa: BLE001  記録失敗でLRを止めない
            _log.warning("lr overlap note failed: %s", type(e).__name__)


# ============================================================
# 02B-7: 単一アクセサ(part1/public_study_html 経由)
# ============================================================
def verify_items_against_record(kp_dir: str, items: list, *, which: str = "part1") -> None:
    """Part 1等の消費者が受け取る item 列が、ユーザー確定レコードの保護値と一致すること(英語は常に、glossはactor=user)。レコード無し=何もしない。"""
    if not protection_enabled():
        return
    rec = load_record(kp_dir)
    if rec is None or rec.get("state") != STATE_LIVE:
        return
    enforce = (rec.get("confirmed_by") or {}).get("actor") in ENFORCING_ACTORS
    by_id = {it.get("candidate_id"): it for it in items}
    block = []
    for ri in rec.get("items") or []:
        if which == "part1" and ri["slot"] not in ("kp", "vocab"):
            continue
        b, w = _item_diffs(ri, by_id.get(ri["candidate_id"]), f"accessor:{which}", enforce_gloss=enforce)
        block += b
    if block:
        level = _rec_level(rec)
        raise_integrity(kp_dir, level, block, f"消費者({which})が受け取る項目が確定レコードと一致しません。")


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
    """G1を通してから確定itemを返す単一アクセサ。which="kp"|"vocab"|"part1"。reviewの無い旧runは従来のartifactを返す(検証なし)。
    契約(02B): 今後の消費者(Part 1・公開ページ builder・ハイライト等)はこのアクセサ経由で確定itemを受け取る。part1=Part 1入力(vocab最大5件、rankはvocab側連番)。"""
    rv.require_final_consistent(kp_dir, level=level, require_src_contract=require_src_contract)
    if which == "part1":
        return rv.part1_items(kp_dir)   # part1_items自身が確定レコードとの照合(verify_items_against_record)を行う
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


def _pending_study_dir(run: str, level: str) -> Optional[str]:
    """pendingモード用: そのlevelの文法study dir(候補docがあるときだけ。無ければNone=sidecarは作らずrecordの印だけ)。曖昧(複数)はエラー。"""
    import er119_grammar_review_01 as gr
    import er120_part2_grammar_production_01 as g
    try:
        dirs = gr.discover_dirs(run, level)
    except (g.Part2Error, ValueError) as e:
        raise CliError(f"文法(Part 2)のstudy dirを確認できません(level={level}): {e}") from e
    if len(dirs) > 1:
        raise CliError(f"level={level} の文法study dirが複数あります({dirs})。どれか1つにしてください(pathから推定しません)")
    return dirs[0] if dirs else None


def cmd_from_form(run: str, level: str, payload_path: str, by: str, user_ref: str, *, actor: str = ACTOR_USER, grammar_pending: bool = False) -> dict:
    """grammar_pending=True(KP先行確定モード): KP/KW(区分①②③)だけを確定・保護する。文法は『選定待ち』のまま=0件として確定しない
    (文法reviewは触らない。sidecarはstatus=pendingで作る/無ければrecordの印だけ。payloadのgrammar[]は使わず、無視した件数を出力に残す)。
    後から `cmd_grammar_from_form` で文法だけを確定する。"""
    if actor not in ENFORCING_ACTORS:
        raise CliError(f"--actor は user|evidence のみ(指定: {actor!r})")
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
    review0 = rv.load_review(kp_dir) or {}
    spec = _display_spec_for_new(load_record(kp_dir), review0)   # display_spec付き=Std②をitemsへ(unconsumedへ落とさない)・③はCATEGORY3_HIGHLIGHT
    vocab_on = rv.vocab_enabled(level, review0)
    if level != "b1b" and bool(spec) != vocab_on:
        raise CliError(f"display_spec={spec!r} とreview.std_part1={bool(review0.get('std_part1'))} が一致しません。既存記事の新表示仕様への移行は "
                       f"`{_cli(kp_dir, 'reconsume')} --level {level} --by <名> --user-ref <path>`(ユーザー選定は変わりません)")
    groups = payload.get("selection") or {}
    ids = _flat_selection_ids(groups)
    if grammar_pending:
        gp = groups.get("grammar")
        gv = {"study_dir": _pending_study_dir(run, level), "doc": None, "items": [], "presented_ids": [], "pending": True,
              "ignored": len(gp) if isinstance(gp, list) else 0}
    else:
        gv = _validate_form_grammar(run, kp_dir, level, groups.get("grammar"))   # 文法の照合(何も書かない。不一致=ISSUE rc=4)。KP/文法のどれも書く前に全て検証する(Opus O-4)
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
    vocab_ids = (ids["cat1"] + ids["cat2"]) if vocab_on else None
    by_rank = {cid: cm[cid]["ai_rank"] for cid in seen}
    # 既存検証(Redundancy/NG/gloss_hr_pending/qa_fail/件数)を全て通す op_select。失敗=何も書かない
    review = rv.op_select(kp_dir, kp_ranks=[by_rank[i] for i in kp_ids], vocab_ranks=([by_rank[i] for i in vocab_ids] if vocab_ids is not None else None), by=by)
    unconsumed = [{"candidate_id": i["candidate_id"], "kind": i.get("kind"), "category": 3, "used_form": i.get("term"), "japanese_gloss": i.get("ja_gloss"),
                   "reason": REASON_C3_HIGHLIGHT if spec else REASON_C3_NO_CONSUMER} for i in groups.get("meaning_display") or []]
    if level != "b1b" and not spec:
        unconsumed += [{"candidate_id": i["candidate_id"], "kind": i.get("kind"), "category": 2, "used_form": i.get("term"), "japanese_gloss": i.get("ja_gloss"),
                        "reason": REASON_C2_NO_SLOT} for i in groups.get("extra_explanation") or []]
    with rv.review_lock(kp_dir, rv.KIND_KP, by):
        # 呼出順(Opus O-4): 検証済み -> KPロック(本ブロック) -> 文法ロック(apply_form_selection内) -> (1)文法review -> (2)sidecar -> (3)KPレコード保存(commit点)
        grammar_review = None if gv.get("pending") else _apply_form_grammar_review(gv, by=by, user_ref=user_ref)
        items = build_items(cands, kp_ids, vocab_ids or [])
        prev = load_record(kp_dir)
        rev_no = ((prev or {}).get("revision") or 0) + 1
        os.makedirs(paths_of(kp_dir)["source_dir"], exist_ok=True)
        sp = os.path.join(paths_of(kp_dir)["source_dir"], f"rev{rev_no}_payload.json")
        with open(sp, "wb") as f:
            f.write(raw)
        origin = {"kind": "form_submission", "form_schema": payload.get("schema"), "form_schema_version": 2, "form_payload_sha256": hashlib.sha256(raw).hexdigest(),
                  "source_revision": rev_no, "user_ref": user_ref}
        rec = _new_record(kp_dir=kp_dir, review=review, cands=cands, items=items, actor=actor, origin=origin, by=by,
                          attestation=("form_submit" if actor == ACTOR_USER else "EVIDENCE_RUN(ユーザー確定ではない。runtime evidence用にフォーム送信を再現した記録。user_refは委任文)"), user_ref=user_ref,
                          comment=payload.get("comment") or "", unconsumed=unconsumed, prev=prev, event="confirmed",
                          confirmation_id="cf_" + hashlib.sha256(raw).hexdigest()[:16])
        rec.pop("grammar", None)
        if gv.get("pending"):
            rec["grammar"] = _pending_grammar_mark(run, rec, kp_dir, study_dir=gv["study_dir"], level=level, ignored=gv["ignored"])
            _append_history_note(rec, "grammar_pending", by, user_ref, {"grammar_payload_ignored": gv["ignored"]})
        elif gv["study_dir"] is not None:
            rec["grammar"] = _write_grammar_sidecar(run, rec, gv["items"], kp_dir, study_dir=gv["study_dir"], level=level, presented_ids=gv.get("presented_ids"))   # 0件も記録(文法なしの確定)
        save_record(kp_dir, rec)   # 確定点(ここまで失敗なら確定レコードは作られない。同じ入力の再送は冪等)
    return {"record": paths_of(kp_dir)["record"], "revision": rec["revision"], "items": [(i["candidate_id"], i["category"], i["used_form"]) for i in items],
            "unconsumed": [(u["candidate_id"], u["reason"]) for u in unconsumed], "grammar": len(gv["items"]),
            "grammar_review": grammar_review,
            "grammar_status": GRAMMAR_PENDING if gv.get("pending") else "confirmed",
            "grammar_payload_ignored": gv.get("ignored", 0),
            "next": ("KP/KWを確定しました。文法は選定待ちです(0件確定ではありません)。文法の選定後に `confirm --grammar-from-form <payload>` で文法だけを確定してください"
                     if gv.get("pending") else "制作コマンドを同じまま再実行してください(finalize→後続が進みます)")}


def _grammar_next(run: str, level: str) -> str:
    return (f"py er119_kp_human_review_cli_01.py grammar-pregen --run {run} --level {level}"
            "(文法解説の事前生成が未完了/失敗の場合。制作コマンドを同じまま再実行しても未生成分だけ作られます)")


def _validate_form_grammar(run: str, kp_dir: str, level: str, grammar: Any) -> dict:
    """フォームの文法(payload selection.grammar[])を、そのlevelの事前生成物(grammar_candidates.json / grammar_explanations.json)と**逐語**照合する(何も書かない。ISSUE記録を除く)。
    照合: id が現候補docにある / title == construct_ja / explanation_status == provided / explanation_full == explanations[id].explanation_md(バイト一致) /
          (あれば)explanation_sha256・example が一致 / 件数 <= 1(GRAMMAR_MAX。2件同時選択は禁止) / idがTop1/Top2の提示範囲(presented_ids)内 / 重複なし。不一致は黙って採用・置換せずISSUE(rc=4。修正案=正しい値を提示)。
    戻り: {"study_dir": str|None, "doc": dict|None, "items": [正規化済みitem]}。study_dir=None は文法のstudy dir自体が無い場合(文法0件のときだけ許す=文法を見せていないフォーム)。"""
    import er119_grammar_review_01 as gr
    import er120_part2_grammar_production_01 as g
    grammar = [] if grammar is None else grammar
    if not isinstance(grammar, list):
        raise CliError("payloadの selection.grammar は配列である必要があります")
    try:
        dirs = gr.discover_dirs(run, level)
    except (g.Part2Error, ValueError) as e:
        raise CliError(f"文法(Part 2)の候補docを確認できません(level={level}): {e}。次の一手: 制作コマンドを同じまま再実行して候補/解説の事前生成を済ませてください") from e
    if len(dirs) > 1:
        raise CliError(f"level={level} の文法study dirが複数あります({dirs})。どれか1つにしてください(pathから推定しません)")
    if not dirs:
        if grammar:
            raise CliError(f"文法(Part 2)の候補/reviewがまだありません(level={level})。次の一手: 制作を実行して候補を生成し、解説を事前生成してから、文法を含むフォームを送信してください")
        return {"study_dir": None, "doc": None, "items": []}
    sd = dirs[0]
    doc = gr.load_candidates(sd)
    ex = None
    if doc.get("candidates"):
        try:
            ex = gr.require_explanations(sd, doc, level=level)   # 事前生成が不完全/失敗/不整合ならデータなしでエラー(フォームに出した解説=確定=公開の前提)
        except rv.KpReviewError as e:
            raise CliError(f"文法解説の事前生成が完了していないため、確定を受け付けません: {e}。次の一手: {_grammar_next(run, level)}") from e
    cand_by = {c["candidate_id"]: c for c in doc.get("candidates") or []}
    presented_ids = [c["candidate_id"] for c in (doc.get("candidates") or [])[:g.PREGEN_MAX]]   # 提示=Trial-08順位のTop1/Top2のみ(rank順)
    ex_by = {i["candidate_id"]: i for i in (ex or {}).get("items") or []}
    diffs, proposal, norm, seen = [], [], [], set()

    def d(cid, field, confirmed, observed, where="payload.selection.grammar vs 事前生成物"):
        diffs.append({"candidate_id": cid, "field": field, "confirmed": confirmed, "observed": observed, "where": where})

    if len(grammar) > GRAMMAR_MAX:
        d(None, "count", len(grammar), f"{GRAMMAR_MAX}件以内", "payload.selection.grammar")
        proposal.append(f"文法は{GRAMMAR_MAX}件だけ選べます(2件同時選択は禁止。適切な候補が無ければ0件)。フォームで{GRAMMAR_MAX}件以内に選び直して再送信してください")
    for it in grammar:
        if not isinstance(it, dict):
            raise CliError("payloadの selection.grammar の要素はオブジェクトである必要があります")
        cid, alt = it.get("id"), it.get("candidate_id")
        if cid and alt and cid != alt:
            d(cid, "id/candidate_id", cid, alt)
        cid = cid or alt
        if cid in seen:
            d(cid, "duplicate", "重複なし", "同じidが複数")
            continue
        seen.add(cid)
        c, e = cand_by.get(cid), ex_by.get(cid)
        if c is None:
            d(cid, "id", "(現在の文法候補docにあるid)", cid)
            proposal.append(f"id={cid} は現在の文法候補にありません。現在の候補でフォームを作り直して再送信してください(idの対応付け以外の推測はしません)")
            continue
        if cid not in presented_ids:
            d(cid, "id(提示範囲)", cid, f"Top1/Top2のみ提示: {presented_ids}")
            proposal.append(f"id={cid} はTop1/Top2(提示範囲 {presented_ids})にありません。現在の提示候補でフォームを作り直して再送信してください")
            continue
        title = it.get("title") if it.get("title") is not None else it.get("name")
        if title != c.get("construct_ja"):
            d(cid, "title(文法名)", title, c.get("construct_ja"))
            proposal.append(f"id={cid}: 文法名を『{c.get('construct_ja')}』に合わせる")
        if e is None:
            d(cid, "explanation(事前生成物)", "(事前生成された解説)", "(解説なし。事前生成の対象外=Top1/Top2以外)")
            proposal.append(f"id={cid}: 解説が事前生成されていない候補は確定できません。解説のある候補から選んでください")
        else:
            if it.get("explanation_status") != "provided":
                d(cid, "explanation_status", it.get("explanation_status"), "provided(解説全文を見せた)が必要")
            if it.get("explanation_full") != e["explanation_md"]:
                d(cid, "explanation_full(解説全文)", str(it.get("explanation_full"))[:80], e["explanation_md"][:80])
                proposal.append(f"id={cid}: 解説全文を現在の事前生成物(sha={e['explanation_sha256'][:12]})に合わせてフォームを作り直す(AIは解説を書き換えて採用しません)")
            if it.get("explanation_sha256") is not None and it["explanation_sha256"] != e["explanation_sha256"]:
                d(cid, "explanation_sha256", it["explanation_sha256"][:16], e["explanation_sha256"][:16])
        if it.get("example") is not None and it["example"] != c.get("sentence"):
            d(cid, "example(英文)", it["example"], c.get("sentence"))
        norm.append({"id": cid, "title": c.get("construct_ja"), "explanation_full": it.get("explanation_full"), "explanation_status": it.get("explanation_status"),
                     "example": c.get("sentence"), "explanation_sha256": (e or {}).get("explanation_sha256")})
    if diffs:
        raise_issue(kp_dir, level, "フォームで確定された文法が、事前生成された文法候補/解説全文と一致しません(件数・id・文法名・解説全文)。黙って採用・置換しません。", diffs,
                    proposal=proposal or ["現在の文法候補/解説でフォームを作り直して再送信してください"], next_steps=["現在の事前生成物でフォームを作り直して再送信(文法はTop1/Top2から1件・0件も可。2件同時選択は不可)"])
    return {"study_dir": sd, "doc": doc, "items": norm, "presented_ids": presented_ids}


def _apply_form_grammar_review(gv: dict, *, by: str, user_ref: str) -> Optional[str]:
    """(KPロック保持中)文法ロックを取って文法reviewへフォーム選択を適用する(0件=同ロック内でomit)。冪等。study dir無し(文法を見せていないフォーム)=何もしない。
    失敗はCliError(KPの確定レコードはまだ作られていない=何も確定していない)。戻り=文法reviewのstatus。"""
    if gv["study_dir"] is None:
        return None
    import er119_grammar_review_01 as gr
    import er120_part2_grammar_production_01 as g
    try:
        rvw = gr.apply_form_selection(gv["study_dir"], ids=[i["id"] for i in gv["items"]], by=by, user_ref=user_ref, candidates_sha256=gv["doc"]["candidates_sha256"])
    except (g.Part2Error, g.Part2ReviewError, rv.KpReviewError) as e:
        raise CliError(f"文法reviewへの適用に失敗しました(確定レコードは作っていません。同じコマンドの再実行は安全です): {type(e).__name__}: {e}") from e
    return rvw.get("status")


def _archive_prior_grammar_files(study_dir: str) -> None:
    """再確認(revoke後)/旧仕様の確定の上書き前に、前の凍結値・sidecarを退避する。pending sidecar(選定待ちの印。文法の確定ではない)は退避せず上書きする。"""
    rv.archive_if_exists(os.path.join(study_dir, FILE_GRAMMAR_FROZEN), "RECONFIRM_SUPERSEDED")
    sp = os.path.join(study_dir, FILE_GRAMMAR)
    if os.path.exists(sp) and (_read(sp).get("status") != GRAMMAR_PENDING):
        rv.archive_if_exists(sp, "RECONFIRM_SUPERSEDED")


def _write_grammar_sidecar(run: str, rec: dict, grammar: list, kp_dir: str, *, study_dir: str, level: str, presented_ids: Optional[list] = None,
                           pending: bool = False, from_pending: bool = False) -> dict:
    """level別sidecar `<study_dir>/confirmed_grammar.json`(v2: level・explanation_sha_by_id付き。0件=items空で『文法なしの確定』を記録)。
    再確認(revoke後)の場合は、前の確定の凍結値・sidecarを退避してから書く(confirmation_idが違う凍結値でINTEGRITYにならないように)。
    study_dirは呼出側がlevel指定で決める(先頭dirへの暗黙決定はしない)。"""
    _archive_prior_grammar_files(study_dir)
    items = [{k: g.get(k) for k in ("id", "title", "explanation_full", "explanation_status", "example", "explanation_sha256")} for g in grammar]
    doc = {"schema": SCHEMA_GRAMMAR_V2, "level": level, "status": GRAMMAR_PENDING if pending else "confirmed", "confirmation_id": rec["confirmation_id"], "items": items,
           "explanation_sha_by_id": {i["id"]: i.get("explanation_sha256") for i in items}, "presented_ids": list(presented_ids or []), "max_select": GRAMMAR_MAX}
    if from_pending:
        doc["confirmed_after_pending"] = True
    doc["kp_dir_rel"] = os.path.relpath(os.path.abspath(kp_dir), os.path.abspath(study_dir)).replace(os.sep, "/")   # 文法側(study_dir)から確定レコードを辿る相対path(runごとコピーしても有効)
    doc["content_sha256"] = _jsha(doc["items"])
    doc["sidecar_sha256"] = _jsha({k: v for k, v in doc.items() if k != "sidecar_sha256"})
    p = os.path.join(study_dir, FILE_GRAMMAR)
    _write(p, doc)
    return {"path_rel": os.path.relpath(p, run).replace(os.sep, "/"), "sidecar_sha256": doc["sidecar_sha256"], "count": len(items), "level": level, "schema": SCHEMA_GRAMMAR_V2,
            "explanation_source": ["form_displayed" for _ in items]}


def _append_history_note(rec: dict, event: str, by: str, user_ref: str, extra: Optional[dict] = None) -> None:
    """履歴チェーンへ追記(revisionは呼出側が決める。保護項目content_sha256は変えない)。"""
    _append_history(rec, event=event, by=by, user_ref=user_ref, extra=extra)


def _pending_grammar_mark(run: str, rec: dict, kp_dir: str, *, study_dir: Optional[str], level: str, ignored: int) -> dict:
    """rec["grammar"]の『選定待ち』印。study dirがあればstatus=pendingのsidecarも作る(0件確定と区別。既存の確定sidecarは退避)。
    grammar_state()はpendingでNone=文法の保護なし・guard_grammarは効かない(選び直し可)。"""
    if study_dir is not None:
        info = _write_grammar_sidecar(run, rec, [], kp_dir, study_dir=study_dir, level=level, pending=True)
    else:
        info = {"path_rel": None, "sidecar_sha256": None, "count": 0, "level": level, "schema": SCHEMA_GRAMMAR_V2}
    info.update(status=GRAMMAR_PENDING, pending_since=rv._now(), reason="grammar_reselection_pending(新仕様 Top1/Top2・1件選択の選定待ち。0件確定ではない)", payload_grammar_ignored=ignored)
    return info


def cmd_grammar_from_form(run: str, level: str, payload_path: str, by: str, user_ref: str) -> dict:
    """KP先行確定済み(grammar pending)のレコードへ、文法だけを後から確定する。KPの保護項目(items/content_sha256/confirmation_id)は不変。
    検証(何も書かない前に全て): payloadのlevel/候補shaがKP確定と矛盾しない・文法はTop1/Top2のpresented_idsの1件以下・解説全文が事前生成物と逐語一致。
    0件はomit(zero_reason=form_submission_no_grammar。『適切な候補なし』をユーザーが選んだ確定)。冪等: 既に同じ文法で確定済みなら変更しない。
    別の文法で確定済みは拒否(確定後不変。変更はrevoke)。"""
    by, user_ref = _need_by(by), _need_user_ref(user_ref)
    kp_dir = _kp_dir_for(run, level)
    with open(payload_path, "rb") as f:
        raw = f.read()
    payload = json.loads(raw.decode("utf-8"))
    if payload.get("schema_version") != 2:
        raise CliError(f"schema_version=2 のフォーム送信データのみ受け付けます(受信={payload.get('schema_version')!r})")
    rec = load_record(kp_dir)
    if rec is None or rec.get("state") != STATE_LIVE or (rec.get("confirmed_by") or {}).get("actor") not in ENFORCING_ACTORS:
        raise CliError("文法を後から確定できるKP確定レコード(live)がありません。先に `confirm --from-form <payload> --grammar-pending` でKP/KWを確定してください")
    art = payload.get("article") or {}
    if art.get("level") not in (None, level):
        raise CliError(f"payloadのlevel={art.get('level')!r} と --level={level!r} が異なります")
    cands = rv.load_candidates(kp_dir)
    if art.get("candidates_sha256") and art["candidates_sha256"] != cands["candidates_sha256"]:
        raise CliError("payloadの候補集合sha256が現在のKP候補docと一致しません(別の候補集合のフォーム)。KP区分は確定済みで変更できません")
    groups = payload.get("selection") or {}
    got = {"cat1": [i.get("candidate_id") for i in groups.get("key_phrase") or []], "cat2": [i.get("candidate_id") for i in groups.get("extra_explanation") or []],
           "cat3": [i.get("candidate_id") for i in groups.get("meaning_display") or []]}
    _all = list(rec["items"]) + list(rec.get("unconsumed") or [])
    have = {f"cat{n}": [i["candidate_id"] for i in _all if i.get("category") == n] for n in (1, 2, 3)}
    for k in ("cat1", "cat2", "cat3"):
        if got[k] and sorted(got[k]) != sorted(have[k]):
            raise CliError(f"payloadのKP/KW区分({k})が確定済みレコードと異なります(payload={sorted(got[k])} / 確定={sorted(have[k])})。KP/KWは確定済みで変更できません(文法のみを送るか、同じKP/KWを含めてください)")
    gmark = rec.get("grammar") or {}
    if not gmark:
        raise CliError("このレコードは文法選定待ち(pending)ではありません。文法を含めたKP確定は `confirm --from-form` を使ってください")
    if gmark.get("status") != GRAMMAR_PENDING:
        # 既に文法確定済み: 同じ内容なら冪等、違えば拒否(確定後不変)
        gv0 = _validate_form_grammar(run, kp_dir, level, groups.get("grammar"))
        side = _read(os.path.join(run, gmark["path_rel"])) if gmark.get("path_rel") else {"items": []}
        if sorted(i.get("id") for i in side.get("items") or []) == sorted(i["id"] for i in gv0["items"]):
            return {"record": paths_of(kp_dir)["record"], "revision": rec["revision"], "grammar": len(gv0["items"]), "grammar_status": "confirmed", "unchanged": True,
                    "next": "既に同じ文法で確定済みです(変更なし)"}
        raise CliError("文法は既に別の内容で確定済みです。確定後は変更できません(変更は revoke → 選び直し)")
    gv = _validate_form_grammar(run, kp_dir, level, groups.get("grammar"))   # 文法の照合(何も書かない。不一致=ISSUE rc=4)
    if gv["study_dir"] is None:
        raise CliError(f"文法の候補/解説がまだ生成されていません(level={level})。次の一手: 制作を実行して候補を生成し、Top1/Top2の解説を事前生成してからフォームを送信してください")
    with rv.review_lock(kp_dir, rv.KIND_KP, by):
        rec = load_record(kp_dir)
        if (rec.get("grammar") or {}).get("status") != GRAMMAR_PENDING:
            raise CliError("文法選定待ちの状態が変わりました。再実行してください")
        grammar_review = _apply_form_grammar_review(gv, by=by, user_ref=user_ref)
        os.makedirs(paths_of(kp_dir)["source_dir"], exist_ok=True)
        rev_no = rec["revision"] + 1
        sp = os.path.join(paths_of(kp_dir)["source_dir"], f"rev{rev_no}_grammar_payload.json")
        with open(sp, "wb") as f:
            f.write(raw)
        rec["revision"] = rev_no
        rec["grammar"] = _write_grammar_sidecar(run, rec, gv["items"], kp_dir, study_dir=gv["study_dir"], level=level, presented_ids=gv.get("presented_ids"), from_pending=True)
        rec["grammar"]["status"] = "confirmed"
        _append_history_note(rec, "grammar_confirmed", by, user_ref, {"grammar_ids": [i["id"] for i in gv["items"]], "presented_ids": gv.get("presented_ids"),
                                                                      "grammar_payload_sha256": hashlib.sha256(raw).hexdigest(), "after_pending": True})
        save_record(kp_dir, rec)
    return {"record": paths_of(kp_dir)["record"], "revision": rec["revision"], "grammar": len(gv["items"]), "grammar_ids": [i["id"] for i in gv["items"]],
            "grammar_status": "confirmed", "grammar_review": grammar_review, "unchanged": False,
            "next": "制作コマンドを同じまま再実行してください(文法finalize→後続が進みます)"}


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
        items = build_items(cands, rv.sel_ids(sel, "kp"), rv.sel_ids(sel, "vocab") if rv.vocab_enabled(level, review) else [])
        actor = _actor_for(review)
        pseudo = {"items": items, "confirmed_by": {"actor": ACTOR_USER}, "display_spec": _display_spec_for_new(prev, review)}
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
        c3 = {u["candidate_id"]: u for u in rec.get("unconsumed") or [] if u.get("category") == 3}   # ③(本文の下線+短い日本語訳)の訳も修正できる(SLOT-23 M10)
        for cid in changes:
            if cid not in {i["candidate_id"] for i in rec["items"]} and cid not in c3:
                raise CliError(f"candidate_id={cid} は確定レコード(items/③)にありません")
            if cid not in cm:
                raise CliError(f"candidate_id={cid} が候補docにありません")
        before = {i["candidate_id"]: i["japanese_gloss"] for i in rec["items"] if i["candidate_id"] in changes}
        before.update({cid: c3[cid].get("japanese_gloss") for cid in changes if cid in c3})
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
        items = build_items(cands, rv.sel_ids(sel, "kp"), rv.sel_ids(sel, "vocab") if rv.vocab_enabled(level, review) else [])
        new_unconsumed = copy.deepcopy(rec.get("unconsumed") or [])
        for u in new_unconsumed:
            if u.get("category") == 3 and u.get("candidate_id") in changes:
                u["japanese_gloss"] = changes[u["candidate_id"]]
        new_rec = _new_record(kp_dir=kp_dir, review=review, cands=cands, items=items, actor=(rec.get("confirmed_by") or {}).get("actor") or ACTOR_USER, origin=dict(rec["origin"]), by=by, attestation=f"cli --by {by}",
                              user_ref=user_ref, comment=rec.get("comment") or "", unconsumed=new_unconsumed, prev=rec, event="revised", reason=reason,
                              confirmation_id=rec["confirmation_id"])
        new_rec["history"][-1]["extra"] = {"gloss_before": before, "gloss_after": changes}
        new_rec["history"][-1]["entry_sha256"] = _entry_sha(new_rec["history"][-1])
        save_record(kp_dir, new_rec)
        archived = _archive_final_outputs(kp_dir, "REVISE_SUPERSEDED")
    refinal = _try_refinalize(kp_dir, level)
    return {"revised": sorted(changes), "revision": new_rec["revision"], "archived": archived, "refinalized": refinal,
            "next": "制作コマンドを同じまま再実行してください(派生物は新しい訳から再生成されます)" if not refinal else "再finalize済み。制作コマンドを再実行してください"}


def cmd_reconsume(run: str, level: str, by: str, user_ref: str) -> dict:
    """既存記事の確定内容を新表示仕様(display_spec=LEARNING_ITEMS_123_V1)へ明示的に移行する(SLOT-23 委任_04B。confirm-revise同型のレコード版数+1)。
    ユーザー選定(①②③の候補ID・区分・件数)は変えない。confirmation_id/originは保持、履歴hash chainは継続、同一入力の再実行は冪等。
    a2: unconsumedのSTD_CATEGORY2_NO_SLOT(②)をitems(category2, slot=vocab)へ移し、reviewのselection.vocab(=①+②)とstd_part1をreview_lock下で更新、
        validate_selection(KP⊂vocab・Redundancy pair・NG・Gate)を通す。NGならISSUE(rc=4)で移行しない。確定物(vocab_confirmed.json等)は退避して
        _try_refinalizeに委ねる(ここでは書かない)。確定集合のRedundancy QA(LLM 1 call)は次回のrunner起動で走る。
    b1b: record側のみ(display_spec付与・③をCATEGORY3_HIGHLIGHTへ)。items/review/成果物は不変。"""
    by, user_ref = _need_by(by), _need_user_ref(user_ref)
    kp_dir = _kp_dir_for(run, level)
    with rv.review_lock(kp_dir, rv.KIND_KP, by):
        rec = load_record(kp_dir)
        if rec is None or rec.get("state") != STATE_LIVE:
            raise CliError("確定レコード(live)がありません。移行できるのはユーザー確定済みのレコードだけです")
        probs = _problems_self(rec)
        if probs:
            raise CliError("確定レコード自体(hash chain/sha)が壊れています。移行しません: " + "; ".join(probs))
        review, cands = rv.load_review(kp_dir), rv.load_candidates(kp_dir)
        if review is None or cands is None:
            raise CliError("review/候補docがありません")
        if review["status"] not in rv.FORWARD_STATUSES:
            raise CliError(f"status={review['status']}: 確定済みreviewからのみ移行できます")
        if rv.selection_signature(review) != review.get("selection_signature"):
            raise CliError("reviewの署名が不一致です(手編集の疑い)。移行しません")
        cm = _cand_map(cands)
        old_unc = rec.get("unconsumed") or []
        c2 = [u for u in old_unc if u.get("reason") == REASON_C2_NO_SLOT]
        c3_old = [u for u in old_unc if u.get("reason") == REASON_C3_NO_CONSUMER]
        want_unc = [dict(u, reason=REASON_C3_HIGHLIGHT) if u.get("reason") == REASON_C3_NO_CONSUMER else u for u in old_unc if u.get("reason") != REASON_C2_NO_SLOT]
        sel = review.get("selection") or {}
        kp_ids = rv.sel_ids(sel, "kp")
        if level == "a2":
            c2_ids = [u["candidate_id"] for u in c2]
            for cid in c2_ids:
                if cid not in cm:
                    raise CliError(f"②のcandidate_id={cid} が候補docにありません")
            new_vocab = list(dict.fromkeys(list(kp_ids) + list(rv.sel_ids(sel, "vocab")) + c2_ids))
            new_sel = dict(sel, kp=list(kp_ids), vocab=new_vocab)
            ak = review.get("article_key") or {}
            errs = rv.validate_selection(cands, new_sel, level=level, accepted_qa_fail=review.get("accepted_qa_fail"),
                                         ng_entries=rv.ng_entries_of(review, ak.get("family"), ak.get("slug"), level), std_part1=True)
            if errs:
                raise_issue(kp_dir, level, "②を加えたStd Part 1の選定が既存の検証に通りません(移行していません。確定内容は変更していません)。",
                            [{"candidate_id": None, "field": "validate_selection", "confirmed": "(現行確定)", "observed": e, "where": "reconsume"} for e in errs],
                            proposal=["ユーザー選定は変更できません。重複(Redundancy)等がある場合はユーザー判断が必要です(revoke後の選び直し)"],
                            next_steps=[f"{_cli(kp_dir, 'status')}", f"{_cli(kp_dir, 'revoke')} --level {level} --by <名> --user-ref <ユーザー発言> --reason ... (選び直す場合)"])
            items = build_items(cands, kp_ids, new_vocab)
        else:
            new_sel = sel
            items = build_items(cands, kp_ids, rv.sel_ids(sel, "vocab"))
        already = (rec.get("display_spec") == DISPLAY_SPEC_V1 and not c2 and not c3_old
                   and (level != "a2" or bool(review.get("std_part1"))) and content_sha256(items) == rec.get("content_sha256"))
        if already:
            return {"reconsumed": False, "unchanged": True, "revision": rec["revision"], "display_spec": rec.get("display_spec"),
                    "note": "既に新表示仕様へ移行済みです(冪等)"}
        archived = []
        if level == "a2":
            review["std_part1"] = True
            review["selection"] = new_sel
            vd = dict(review.get("verdicts") or {})
            for cid in new_vocab:
                if cid not in kp_ids:
                    vd[cid] = "SELECTED_VOCAB"
            review["verdicts"] = vd
            review["final_qa"] = None   # ①+②の集合に対する確定Redundancy QAを次回起動で必ず走らせる(M-8)
            rv._event(review, "reconsume", "er128", {"by": by, "user_ref": user_ref, "category2_to_items": [u["candidate_id"] for u in c2],
                                                     "display_spec": DISPLAY_SPEC_V1})
            review = rv.save_review(kp_dir, review, expected_revision=review["revision"])   # 署名はsave_reviewが再計算(std_part1を含む)
            rv.invalidate_gloss_snapshot(kp_dir)
        new_rec = _new_record(kp_dir=kp_dir, review=review, cands=cands, items=items, actor=(rec.get("confirmed_by") or {}).get("actor") or ACTOR_USER,
                              origin=dict(rec["origin"]), by=by, attestation=f"cli --by {by}", user_ref=user_ref, comment=rec.get("comment") or "",
                              unconsumed=want_unc, prev=rec, event="reconsumed", reason="新表示仕様(LEARNING_ITEMS_123_V1)への明示移行(ユーザー選定は不変)",
                              confirmation_id=rec["confirmation_id"], display_spec=DISPLAY_SPEC_V1)
        new_rec["history"][-1]["extra"] = {"display_spec": DISPLAY_SPEC_V1, "category2_to_items": [u["candidate_id"] for u in c2],
                                           "category3_reason_to": REASON_C3_HIGHLIGHT if c3_old else None}
        new_rec["history"][-1]["entry_sha256"] = _entry_sha(new_rec["history"][-1])
        save_record(kp_dir, new_rec)
        if level == "a2":
            archived = _archive_final_outputs(kp_dir, "RECONSUME_SUPERSEDED")
    refinal = _try_refinalize(kp_dir, level) if level == "a2" else None
    return {"reconsumed": True, "level": level, "revision": new_rec["revision"], "display_spec": DISPLAY_SPEC_V1,
            "category2_moved_to_items": [u["candidate_id"] for u in c2], "category3_reason_changed": [u["candidate_id"] for u in c3_old],
            "archived": archived, "refinalized": refinal,
            "next": ("確定集合(①+②)のRedundancy QA(LLM 1 call)は次回のrunner起動(制作コマンドを同じまま再実行)で走り、PASSならvocab_confirmed.jsonがfinalize_kpだけで書かれます。"
                     "その後Std Part 1(①+②)を生成します。QAがNGならreviewはPENDINGへ戻り、選び直しが必要です(自動では差し替えません)。"
                     if level == "a2" else "record側のみ更新しました(成果物・review・音声は不変)")}


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
                                                   "origin": (rec.get("origin") or {}).get("kind"), "display_spec": rec.get("display_spec"), "items": [(i["candidate_id"], i["category"], i["used_form"]) for i in rec["items"]],
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
    g.add_argument("--grammar-from-form", default=None, help="KP先行確定済み(--grammar-pending)のレコードへ文法だけを後から確定する(KPは不変・冪等)")
    g.add_argument("--from-review", action="store_true")
    g.add_argument("--adopt-existing", action="store_true")
    p.add_argument("--apply", action="store_true", help="--adopt-existing: 差分提示のみ(既定)ではなく適用する")
    p.add_argument("--grammar-pending", action="store_true",
                   help="--from-form のみ。KP/KWだけを確定し、文法は選定待ち(0件確定ではない)のままにする。payloadのgrammar[]は使わない")
    p.add_argument("--actor", default="user", choices=("user", "evidence"),
                   help="--from-form のみ。evidence=runtime evidence用(ユーザー確定ではないと記録に明記。保護の強度はuserと同じ)")
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
    p = sub.add_parser("reconsume")
    common(p)
    p.add_argument("--by", default=None)
    p.add_argument("--user-ref", default="")
    return ap


def run(argv=None) -> int:
    a = build_parser().parse_args(argv)
    try:
        if a.cmd == "status":
            out = cmd_status(a.run)
        elif a.cmd == "confirm":
            if a.grammar_pending and not a.from_form:
                raise CliError("--grammar-pending は --from-form と一緒に指定してください")
            if a.grammar_from_form:
                out = cmd_grammar_from_form(a.run, a.level, a.grammar_from_form, a.by, a.user_ref)
            elif a.from_form:
                out = cmd_from_form(a.run, a.level, a.from_form, a.by, a.user_ref, actor=a.actor, grammar_pending=a.grammar_pending)
            elif a.from_review:
                out = cmd_from_review(a.run, a.level, a.by, a.user_ref)
            else:
                out = cmd_from_review(a.run, a.level, a.by, a.user_ref, adopt_existing=True, apply=a.apply)
        elif a.cmd == "confirm-revise":
            out = cmd_revise(a.run, a.level, a.by, a.user_ref, a.reason, a.gloss)
        elif a.cmd == "revoke":
            out = cmd_revoke(a.run, a.level, a.by, a.user_ref, a.reason)
        elif a.cmd == "reconsume":
            out = cmd_reconsume(a.run, a.level, a.by, a.user_ref)
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
