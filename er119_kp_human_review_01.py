# -*- coding: utf-8 -*-
"""KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_02: KP Human Review 共通核(APPROVED_FOR_PRODUCTION、DESIGN_02参照)。

この核は決定論(API 0)。LLM呼出は注入関数(generate_fn / redundancy_fn)経由でのみ行う。
設計不変条件(DESIGN_02 / Opus M-1〜M-9):
  - <kp_dir>/keywords_canonicalized.json と vocab_confirmed.json と kp_selection_final.json を書けるのは finalize だけ(M-1)。
    候補生成は <kp_dir>/kp_candidates/round_<n>/work/ で行う(canonicalization等の既存関数が書く場所)。
  - 自動確定(UNREVIEWED_AUTO_ADOPTED)は「明示宣言」(read_mode_declaration、単一読取点)が有効なときだけ(M-6)。
    環境変数・設定dict・関数既定値・.envから auto にすることはできない(本moduleは環境変数を一切参照しない)。
  - 再選定は reselect(CLI)だけ。resume/regenerate/外側retry は確定済みreviewを再選定しない(M-3b)。
  - NG registry は run ではなく family+slug+level 単位の共有store(M-5)。
  - 共通核は kind 非依存("kp" / "grammar")。grammar は fixture test のみで Production 配線なし(G-1)。
共有関数 sc.run_key_phrases は本moduleから呼ばない/変更しない(A/B/C・Y Trial不変)。
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import time
import unicodedata
from typing import Any, Callable, Optional

SCHEMA_CANDIDATES = "kp_candidates_v1"
SCHEMA_REVIEW = "kp_human_review_v1"
SCHEMA_FINAL = "kp_selection_final_v1"

KIND_KP = "kp"
KIND_GRAMMAR = "grammar"   # fixture testのみ(G-1: Part 2 Production採用の確認まで配線しない)

ST_PENDING = "PENDING_REVIEW"
ST_REVIEWED = "REVIEWED"
ST_AUTO = "UNREVIEWED_AUTO_ADOPTED"
ST_RESELECT = "RESELECTION_REQUESTED"
ST_STALE = "STALE"
FORWARD_STATUSES = (ST_REVIEWED, ST_AUTO)

EXIT_CODE_PENDING = 4          # KP_REVIEW_PENDING(失敗ではなく待機)。ZではRUN_LOCK(rc=4)と共有 -> stdoutの[KP_REVIEW_PENDING]で区別する
PENDING_MARKER = "[KP_REVIEW_PENDING]"

KP_CANDIDATE_MAX = 8
KP_FINAL_MAX = 3
VOCAB_COUNT_MAX = 5
RESELECT_MAX = 2               # 再選定上限(レベル/run)
AUTO_QA_ADVANCE_MAX = 3        # AUTOで確定集合のRedundancy QAがNGのとき、次候補へ繰り上げる上限
LOCK_STALE_SEC = 600

STORE_ROOT = os.path.join("er119_output", "kp_human_review_store_01")   # 共有store(NG registry・範囲宣言)。testはここを差し替える

_AI_BY_PREFIXES = ("fable", "claude", "ai", "sonnet", "opus", "haiku", "agent", "assistant")

SLOT_RULES = {
    KIND_KP: {"kp": {"min": 1, "max": KP_FINAL_MAX}, "vocab": {"min": 0, "max": VOCAB_COUNT_MAX}},
    KIND_GRAMMAR: {"grammar": {"min": 0, "max": 1}},
}
FILE_PREFIX = {KIND_KP: "kp", KIND_GRAMMAR: "grammar"}


# ============================================================
# 例外
# ============================================================
class KpReviewError(RuntimeError):
    """review核の不整合・不正操作(fail-closed)。"""


class KpReviewPending(RuntimeError):
    """Human確認待ち(失敗ではなく待機。rc=4)。pending=[{level,kp_dir,request_md,...}]"""

    def __init__(self, message: str, pending: Optional[list] = None):
        super().__init__(message)
        self.pending = pending or []


class ReviewLockHeld(KpReviewError):
    pass


class ReviewConflict(KpReviewError):
    pass


class KpReviewInconsistent(KpReviewError):
    pass


class KpReviewNotConfirmed(KpReviewInconsistent):
    """Human確認待ち/再選定待ち等で、まだ後段へ進めない状態(失敗ではなく待機。rc=4)。"""


# ============================================================
# 基本helper
# ============================================================
_JST = datetime.timezone(datetime.timedelta(hours=9))


def _now() -> str:
    return datetime.datetime.now(_JST).isoformat(timespec="microseconds")


def _today_jst() -> str:
    return datetime.datetime.now(_JST).date().isoformat()


def sha256_text(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def jsha(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _write_json_atomic(path: str, obj: Any) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = f"{path}.tmp{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def _read_json(path: str) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _write_text_atomic(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = f"{path}.tmp{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def phrase_key(phrase: str) -> str:
    """er105.phrase_keyと同じ正規化(NFKC・空白正規化・小文字化)。coreを軽くするため再実装せず同式を使う。"""
    p = unicodedata.normalize("NFKC", phrase or "")
    p = p.translate(str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"'}))
    return re.sub(r"\s+", " ", p).strip().lower()


_POSSESSIVE_RE = re.compile(r"\b(one's|someone's|somebody's|your|his|her|their|my|our|its)\b")


def used_form_key(used_form: str) -> str:
    """R-2: 所有格代名詞(one's/your/his/her/their/my/...)を同じプレースホルダへ正規化したキー。"""
    k = phrase_key(used_form)
    return _POSSESSIVE_RE.sub("<poss>", k)


def _is_subseq_tokens(a: list, b: list) -> bool:
    """aがbの連続部分列か。"""
    if not a or len(a) > len(b):
        return False
    for i in range(len(b) - len(a) + 1):
        if b[i:i + len(a)] == a:
            return True
    return False


def candidate_id_for(selection_phrase: str) -> str:
    return "p_" + hashlib.sha1(phrase_key(selection_phrase).encode("utf-8")).hexdigest()[:10]


def paths(kp_dir: str, kind: str = KIND_KP) -> dict:
    pre = FILE_PREFIX[kind]
    return {
        "candidates": f"{kp_dir}/{pre}_candidates.json",
        "review": f"{kp_dir}/{pre}_human_review.json",
        "lock": f"{kp_dir}/{pre}_human_review.lock",
        "request": f"{kp_dir}/{pre}_human_review_request.md",
        "final": f"{kp_dir}/{pre}_selection_final.json",
        "kp": f"{kp_dir}/keywords_canonicalized.json",
        "vocab": f"{kp_dir}/vocab_confirmed.json",
        "rounds": f"{kp_dir}/kp_candidates",
    }


def candidates_sha256(doc: dict) -> str:
    d = {k: v for k, v in doc.items() if k != "candidates_sha256"}
    return jsha(d)


# ============================================================
# 排他lock + 版番号比較更新(R-3)
# ============================================================
class review_lock:
    """O_EXCLの排他lockファイル。保持中は他者が更新を拒否される(ReviewLockHeld)。stale(LOCK_STALE_SEC超)は引き継ぐ。"""

    def __init__(self, kp_dir: str, kind: str = KIND_KP, who: str = ""):
        self.path = paths(kp_dir, kind)["lock"]
        self.who = who
        self.fd = None

    def __enter__(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
        for _ in range(2):
            try:
                self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(self.fd, json.dumps({"pid": os.getpid(), "who": self.who, "at": time.time()}).encode("utf-8"))
                return self
            except FileExistsError:
                try:
                    age = time.time() - os.path.getmtime(self.path)
                except OSError:
                    continue
                if age > LOCK_STALE_SEC:
                    try:
                        os.remove(self.path)
                    except OSError:
                        pass
                    continue
                raise ReviewLockHeld(f"review更新lockが保持されています({self.path})。並行操作を拒否しました。少し待って再実行してください") from None
        raise ReviewLockHeld(f"review更新lockを取得できません({self.path})")

    def __exit__(self, *exc):
        if self.fd is not None:
            try:
                os.close(self.fd)
            except OSError:
                pass
            try:
                os.remove(self.path)
            except OSError:
                pass
        return False


def load_review(kp_dir: str, kind: str = KIND_KP) -> Optional[dict]:
    p = paths(kp_dir, kind)["review"]
    if not os.path.exists(p):
        return None
    return _read_json(p)


def load_candidates(kp_dir: str, kind: str = KIND_KP) -> Optional[dict]:
    p = paths(kp_dir, kind)["candidates"]
    if not os.path.exists(p):
        return None
    return _read_json(p)


def save_review(kp_dir: str, review: dict, *, expected_revision: Optional[int], kind: str = KIND_KP) -> dict:
    """版番号比較更新+os.replace原子書換。expected_revision=None は新規作成(既存があれば拒否)。呼出側がreview_lockを保持していること。"""
    p = paths(kp_dir, kind)["review"]
    cur = _read_json(p) if os.path.exists(p) else None
    if expected_revision is None:
        if cur is not None:
            raise ReviewConflict("reviewが既に存在します(新規作成を拒否)")
        review["revision"] = 1
    else:
        if cur is None or cur.get("revision") != expected_revision:
            raise ReviewConflict(f"review版番号が一致しません(期待={expected_revision}, 現在={None if cur is None else cur.get('revision')})。"
                                 "他の操作が先に更新しました。statusを確認して再実行してください")
        review["revision"] = expected_revision + 1
    review["selection_signature"] = selection_signature(review) if review.get("status") in FORWARD_STATUSES else None
    _write_json_atomic(p, review)
    return review


# ============================================================
# NG registry(family+slug+level の共有store。M-5)とNG照合(R-2)
# ============================================================
def _slugsafe(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", s or "x")


def store_ng_path(family: str, slug: str, level: str) -> str:
    return os.path.join(STORE_ROOT, "ng", f"{_slugsafe(family)}__{_slugsafe(slug)}__{_slugsafe(level)}.json")


def store_load_ng(family: str, slug: str, level: str) -> list:
    p = store_ng_path(family, slug, level)
    if not os.path.exists(p):
        return []
    return [e for e in (_read_json(p).get("entries") or []) if e.get("active", True)]


def _store_all(family: str, slug: str, level: str) -> dict:
    p = store_ng_path(family, slug, level)
    if os.path.exists(p):
        return _read_json(p)
    return {"schema": "kp_ng_registry_v1", "family": family, "slug": slug, "level": level, "entries": []}


def store_add_ng(family: str, slug: str, level: str, entry: dict) -> None:
    doc = _store_all(family, slug, level)
    for e in doc["entries"]:
        if e.get("active", True) and e["candidate_id"] == entry["candidate_id"]:
            return
    e2 = dict(entry)
    e2["active"] = True
    doc["entries"].append(e2)
    _write_json_atomic(store_ng_path(family, slug, level), doc)


def store_remove_ng(family: str, slug: str, level: str, *, candidate_id: str = None, phrase: str = None, reason: str, by: str) -> list:
    """unng: 理由・記録必須。解除は削除でなくactive=falseとremovedの記録を残す。"""
    if not (reason or "").strip() or not (by or "").strip():
        raise KpReviewError("unngは --reason と --by が必須です(記録必須)")
    doc = _store_all(family, slug, level)
    removed = []
    for e in doc["entries"]:
        if not e.get("active", True):
            continue
        if (candidate_id and e["candidate_id"] == candidate_id) or (phrase and e.get("phrase_key") == phrase_key(phrase)):
            e["active"] = False
            e["removed"] = {"at": _now(), "by": by, "reason": reason}
            removed.append(e["candidate_id"])
    if removed:
        _write_json_atomic(store_ng_path(family, slug, level), doc)
    return removed


def make_ng_entry(cand: dict, reason: str, by: str) -> dict:
    return {"candidate_id": cand["candidate_id"], "phrase_key": phrase_key(cand.get("selection_phrase") or ""),
            "used_form_key": used_form_key(cand.get("used_form") or ""), "phrase": cand.get("selection_phrase"),
            "used_form": cand.get("used_form"), "reason": reason, "by": by, "at": _now()}


def match_ng(cand: dict, ng_entries: list) -> Optional[str]:
    """returns "exact"(candidate_id/phrase_key/used_form_keyのいずれか一致) / "similar"(NG句を含む/含まれる、R-2) / None。"""
    cid = cand.get("candidate_id")
    pk = phrase_key(cand.get("selection_phrase") or "")
    uk = used_form_key(cand.get("used_form") or "")
    sim = False
    for n in ng_entries:
        if n.get("candidate_id") == cid or (pk and n.get("phrase_key") == pk) or (uk and n.get("used_form_key") == uk):
            return "exact"
        for a, b in ((uk, n.get("used_form_key") or ""), (pk, n.get("phrase_key") or "")):
            ta, tb = a.split(), b.split()
            if ta and tb and ta != tb and (_is_subseq_tokens(ta, tb) or _is_subseq_tokens(tb, ta)):
                sim = True
    return "similar" if sim else None


def ng_entries_of(review: Optional[dict], family: str = None, slug: str = None, level: str = None) -> list:
    """reviewのng(run内コピー)と共有storeのactive NGの和(candidate_idで重複排除)。"""
    out, seen = [], set()
    src = list((review or {}).get("ng") or [])
    if family and slug and level:
        src += store_load_ng(family, slug, level)
    for e in src:
        if e.get("active", True) and e["candidate_id"] not in seen:
            seen.add(e["candidate_id"])
            out.append(e)
    return out


# ============================================================
# 不在宣言(M-6 / R-7)。mode読取の単一関数 read_mode_declaration
# ============================================================
def _requires_user_ref(by: str) -> bool:
    toks = [t for t in re.split(r"[^a-z]+", (by or "").strip().lower()) if t]
    return bool(toks) and toks[0] in _AI_BY_PREFIXES


def _run_key(run_dir: str) -> str:
    return os.path.normcase(os.path.abspath(run_dir))


def declarations_path(run_dir: str) -> str:
    return os.path.join(run_dir, "kp_review_mode.json")


def scoped_declarations_dir() -> str:
    return os.path.join(STORE_ROOT, "declarations")


def add_declaration(*, run_dirs: Optional[list] = None, scope: Optional[dict] = None, by: str, reason: str,
                    user_ref: str = "", source: str = "declare_absent_cli", until: Optional[str] = None,
                    rounds: Optional[list] = None, candidates_sha256: Optional[str] = None) -> list:
    """明示的な不在宣言を記録する(自動確定の唯一の入口)。declared_by・reasonは必須。AI(Fable等)が宣言する場合はユーザー発言の参照(user_ref)が必須。
    run_dirs=個別run宣言 / scope={"family":"x|z","date":"YYYY-MM-DD"}=範囲宣言(date か until のどちらかが必須=時間境界)。"""
    if not (by or "").strip():
        raise KpReviewError("不在宣言には --by(宣言者)が必須です")
    if not (reason or "").strip():
        raise KpReviewError("不在宣言には --reason が必須です")
    if _requires_user_ref(by) and not (user_ref or "").strip():
        raise KpReviewError("AIが宣言する場合は --user-ref(ユーザー発言の参照)が必須です(AIの『不在とみなした』を自動確定の経路にしない)")
    if bool(run_dirs) == bool(scope):
        raise KpReviewError("run_dirs か scope のどちらか一方だけを指定してください")
    if scope:
        if not scope.get("family"):
            raise KpReviewError("範囲宣言には scope.family が必須です")
        if not scope.get("date") and not until:
            raise KpReviewError("範囲宣言には scope.date か until のどちらか(時間境界)が必須です")
    rec = {"mode": "auto", "declared_by": by, "declared_at": _now(), "source": source, "reason": reason,
           "user_ref": user_ref or "", "until": until, "rounds": list(rounds) if rounds else [1],
           "candidates_sha256": candidates_sha256}
    ids = []
    if run_dirs:
        for rd in run_dirs:
            r = dict(rec)
            r["declaration_id"] = "d_" + jsha([rec, _run_key(rd), time.time()])[:12]
            r["scope"] = {"run": _run_key(rd)}
            path = declarations_path(rd)
            doc = _read_json(path) if os.path.exists(path) else {"schema": "kp_review_mode_v1", "declarations": []}
            doc["declarations"].append(r)
            _write_json_atomic(path, doc)
            ids.append(r["declaration_id"])
    else:
        r = dict(rec)
        r["declaration_id"] = "d_" + jsha([rec, scope, time.time()])[:12]
        r["scope"] = dict(scope)
        _write_json_atomic(os.path.join(scoped_declarations_dir(), r["declaration_id"] + ".json"), r)
        ids.append(r["declaration_id"])
    return ids


def _decl_valid(d: dict, *, run_dir: str, family: str, level: str, review: Optional[dict], round_no: int,
                cands_sha: Optional[str], now_iso: str) -> bool:
    if d.get("mode") != "auto" or not d.get("declared_by") or not d.get("reason"):
        return False
    if _requires_user_ref(d.get("declared_by")) and not d.get("user_ref"):
        return False
    sc = d.get("scope") or {}
    if "run" in sc:
        if sc["run"] != _run_key(run_dir):
            return False
    else:
        if sc.get("family") != family:
            return False
        if sc.get("date") and sc["date"] != _today_jst():
            return False
    if d.get("until") and now_iso > d["until"]:
        return False
    if d.get("rounds") and round_no not in d["rounds"]:
        return False
    if d.get("candidates_sha256") and d["candidates_sha256"] != cands_sha:
        return False
    # M-6: Humanの操作(select/reselect/ng/unng/resolve-gloss)があった時点で、それ以前の宣言は失効する
    last_human = (review or {}).get("last_human_op_at")
    if last_human and d.get("declared_at", "") <= last_human:
        return False
    return True


def read_mode_declaration(run_dir: str, *, family: str, level: str, review: Optional[dict], round_no: int,
                          cands_sha: Optional[str]) -> Optional[dict]:
    """自動確定モードの**単一読取点**。有効な宣言があればそのdictを返し、無ければNone(=待機)。
    環境変数・関数引数・設定dict・hooks・既定値は読まない(宣言ファイルのみ)。"""
    now_iso = _now()
    cands = []
    p = declarations_path(run_dir)
    if os.path.exists(p):
        try:
            cands += list(_read_json(p).get("declarations") or [])
        except (OSError, ValueError):
            pass
    sd = scoped_declarations_dir()
    if os.path.isdir(sd):
        for fn in sorted(os.listdir(sd)):
            if fn.endswith(".json"):
                try:
                    cands.append(_read_json(os.path.join(sd, fn)))
                except (OSError, ValueError):
                    continue
    for d in cands:
        if _decl_valid(d, run_dir=run_dir, family=family, level=level, review=review, round_no=round_no,
                       cands_sha=cands_sha, now_iso=now_iso):
            return d
    return None


# ============================================================
# 選択の検証(select時とfinalize時で同じ関数。b-3)
# ============================================================
def sel_ids(selection: dict, slot: str) -> list:
    return list((selection or {}).get(slot) or [])


def _cand_map(cands: dict) -> dict:
    return {c["candidate_id"]: c for c in cands.get("candidates") or []}


def _pairs(cands: dict) -> set:
    out = set()
    for c in cands.get("candidates") or []:
        for other in (c.get("flags") or {}).get("redundant_with") or []:
            out.add(frozenset((c["candidate_id"], other)))
    return out


def validate_selection(cands: dict, selection: dict, *, level: str, kind: str = KIND_KP, accepted_qa_fail: Optional[list] = None,
                       ng_entries: Optional[list] = None, allow_similar_ng: bool = True) -> list:
    """returns エラー文のlist(空=合格)。select時とfinalize時の両方で呼ぶ。"""
    errs = []
    cm = _cand_map(cands)
    accepted_qa_fail = set(accepted_qa_fail or [])
    ng_entries = ng_entries or []
    rules = SLOT_RULES[kind]
    chosen_all = []
    for slot, rule in rules.items():
        ids = sel_ids(selection, slot)
        if len(ids) != len(set(ids)):
            errs.append(f"{slot}: 同じ候補が重複して選ばれています")
        if len(ids) > rule["max"]:
            errs.append(f"{slot}: 最大{rule['max']}件です(指定{len(ids)}件)")
        if len(set(ids)) < rule["min"] and not (kind == KIND_KP and slot == "vocab"):
            errs.append(f"{slot}: 最低{rule['min']}件が必要です")
        for i in ids:
            if i not in cm:
                errs.append(f"{slot}: 候補{i}が存在しません")
        chosen_all += [i for i in ids if i in cm]
    if kind == KIND_KP:
        kp, vocab = sel_ids(selection, "kp"), sel_ids(selection, "vocab")
        if level == "a2" and vocab:
            errs.append("vocab(単語解説5件)はAdvanced(b1b)のみです。Standardでは指定できません")
        if level == "b1b":
            if not vocab:
                errs.append("vocab: Advancedでは単語解説(vocab)の選択が必要です(KP3件を含む最大5件)")
            elif not set(kp) <= set(vocab):
                errs.append("vocab: KPに選んだ候補をすべて含めてください(KP ⊂ vocab)")
    pairs = _pairs(cands)
    seen = list(dict.fromkeys(chosen_all))
    for i, a in enumerate(seen):
        c = cm.get(a)
        if c is None:
            continue
        if not c.get("human_selectable", True):
            errs.append(f"候補{c['ai_rank']}({c.get('used_form')})は選択できません(Gate不合格)")
        if c.get("flags", {}).get("qa_fail") and a not in accepted_qa_fail:
            errs.append(f"候補{c['ai_rank']}({c.get('used_form')})はcanonicalization QA FAIL(REVIEW_REQUIRED)です。採用するなら --accept-qa-fail {c['ai_rank']} を明示してください")
        if c.get("flags", {}).get("gloss_hr_pending"):
            errs.append(f"候補{c['ai_rank']}({c.get('used_form')})はgloss HR待ちです。resolve-gloss後に選択してください")
        m = match_ng(c, ng_entries)
        if m == "exact":
            errs.append(f"候補{c['ai_rank']}({c.get('used_form')})はNGに指定済みです(選択できません)")
        elif m == "similar" and not allow_similar_ng:
            errs.append(f"候補{c['ai_rank']}({c.get('used_form')})はNG句に類似しています")
        for b in seen[i + 1:]:
            if frozenset((a, b)) in pairs:
                cb = cm.get(b, {})
                errs.append(f"候補{c['ai_rank']}と候補{cb.get('ai_rank')}は意味・用法が重複しています(Redundancy QA)。どちらか一方にしてください")
    return errs


def auto_eligible_now(c: dict, ng_entries: list) -> bool:
    if not c.get("auto_eligible", False):
        return False
    return match_ng(c, ng_entries) is None


def auto_select(cands: dict, *, level: str, kind: str = KIND_KP, ng_entries: Optional[list] = None,
                excluded_ids: Optional[list] = None) -> dict:
    """決定論のAUTO規則: auto_eligibleかつNG/類似NGでなく、既採用候補とredundancy pairを持たない候補をai_rank順に走査。
    KP=先頭3、vocab(Advのみ)=先頭5(KPを含む)。不足は不足のまま(数合わせなし)。grammar=先頭1。"""
    ng_entries = ng_entries or []
    excluded = set(excluded_ids or [])
    pairs = _pairs(cands)
    chosen = []
    for c in sorted(cands.get("candidates") or [], key=lambda x: x["ai_rank"]):
        cid = c["candidate_id"]
        if cid in excluded or not auto_eligible_now(c, ng_entries):
            continue
        if any(frozenset((cid, x)) in pairs for x in chosen):
            continue
        chosen.append(cid)
    if kind == KIND_GRAMMAR:
        return {"grammar": chosen[:1]}
    kp = chosen[:KP_FINAL_MAX]
    vocab = chosen[:VOCAB_COUNT_MAX] if level == "b1b" else []
    return {"kp": kp, "vocab": vocab}


def selection_signature(review: dict) -> str:
    sel = review.get("selection") or {}
    ng = sorted(f"{e['candidate_id']}|{e.get('phrase_key')}" for e in (review.get("ng") or []) if e.get("active", True))
    return jsha({"kind": review.get("kind", KIND_KP), "text_sha256": review.get("text_sha256"),
                 "candidates_sha256": review.get("candidates_sha256"),
                 "selection": {k: sorted(v) for k, v in sel.items()}, "ng": ng, "status": review.get("status")})


# ============================================================
# review生成・操作(CLI/runner共通。lock+版番号)
# ============================================================
def new_review(cands: dict, *, kind: str = KIND_KP, article_key: Optional[dict] = None, prev: Optional[dict] = None) -> dict:
    r = {"schema": SCHEMA_REVIEW, "kind": kind, "level": cands["level"], "text_sha256": cands["text_sha256"],
         "candidates_sha256": cands["candidates_sha256"], "round": cands.get("round", 1), "status": ST_PENDING,
         "revision": 0, "article_key": article_key or (prev or {}).get("article_key"),
         "selection": {}, "accepted_qa_fail": [], "accept_ai_default": False, "accept_ai_shown_candidates_sha256": None,
         "verdicts": {c["candidate_id"]: None for c in cands.get("candidates") or []},
         "ng": list((prev or {}).get("ng") or []), "reselect_count": int((prev or {}).get("reselect_count") or 0),
         "last_human_op_at": (prev or {}).get("last_human_op_at"), "mode_used": None, "final_qa": None,
         "published_selection_signature": (prev or {}).get("published_selection_signature"),
         "history": list((prev or {}).get("history") or []), "selection_signature": None}
    r["history"].append({"at": _now(), "event": "candidates_generated", "by": "runner",
                         "detail": {"round": r["round"], "candidates_sha256": r["candidates_sha256"]}})
    return r


def _event(review: dict, event: str, by: str, detail: Optional[dict] = None) -> None:
    review.setdefault("history", []).append({"at": _now(), "event": event, "by": by, "detail": detail or {}})


def _rank_to_cid(cands: dict, ranks: list) -> list:
    by_rank = {c["ai_rank"]: c["candidate_id"] for c in cands.get("candidates") or []}
    out = []
    for r in ranks:
        if r not in by_rank:
            raise KpReviewError(f"番号{r}の候補がありません(表のai_rank)")
        out.append(by_rank[r])
    return out


def op_select(kp_dir: str, *, kp_ranks: list, vocab_ranks: Optional[list] = None, ng: Optional[dict] = None,
              accept_qa_fail: Optional[list] = None, by: str, accept_ai: bool = False, shown_candidates_sha256: Optional[str] = None,
              kind: str = KIND_KP) -> dict:
    """Humanの選択(CLI)。ng={ai_rank: reason}。検証→REVIEWED。PENDING_REVIEW(または確定済みの事後Review)からのみ。"""
    if not (by or "").strip():
        raise KpReviewError("--by(操作者)が必須です")
    with review_lock(kp_dir, kind, by):
        review = load_review(kp_dir, kind)
        cands = load_candidates(kp_dir, kind)
        if review is None or cands is None:
            raise KpReviewError("候補/reviewがありません(まず制作を実行して候補を生成してください)")
        if review["status"] in (ST_RESELECT, ST_STALE):
            raise KpReviewError(f"status={review['status']}のためselectできません(候補の再生成後に選択してください)")
        if review["candidates_sha256"] != cands["candidates_sha256"]:
            raise KpReviewError("reviewと候補ファイルのcandidates_sha256が一致しません")
        level = review["level"]
        ng = ng or {}
        ng_cids = {}
        for rk, reason in ng.items():
            (cid,) = _rank_to_cid(cands, [rk])
            if not (reason or "").strip():
                raise KpReviewError(f"NG指定には理由が必要です(番号{rk})")
            ng_cids[cid] = reason
        cm = _cand_map(cands)
        # NG登録(run内コピー+共有store)を先に反映して検証に含める
        ak = review.get("article_key") or {}
        new_ng = []
        for cid, reason in ng_cids.items():
            ent = make_ng_entry(cm[cid], reason, by)
            new_ng.append(ent)
        review_ng = list(review.get("ng") or []) + [e for e in new_ng if e["candidate_id"] not in {x["candidate_id"] for x in review.get("ng") or []}]
        if accept_ai:
            if shown_candidates_sha256 != cands["candidates_sha256"]:
                raise KpReviewError("--accept-aiは、表示した候補(candidates_sha256)に対してのみ使えます(未表示の候補への了承は拒否)")
            selection = auto_select(cands, level=level, kind=kind, ng_entries=ng_entries_of({"ng": review_ng}, ak.get("family"), ak.get("slug"), level))
            accepted_qf = list(accept_qa_fail or [])
        else:
            kp_ids = _rank_to_cid(cands, list(kp_ranks or []))
            v_ids = _rank_to_cid(cands, list(vocab_ranks or [])) if vocab_ranks else []
            if kind == KIND_KP and level == "b1b" and vocab_ranks is None:
                raise KpReviewError("Advancedでは --vocab(単語解説。KP3件を含む最大5件)の指定が必要です")
            selection = {"kp": kp_ids, "vocab": v_ids} if kind == KIND_KP else {"grammar": kp_ids}
            accepted_qf = _rank_to_cid(cands, list(accept_qa_fail or []))
        errs = validate_selection(cands, selection, level=level, kind=kind, accepted_qa_fail=accepted_qf,
                                  ng_entries=ng_entries_of({"ng": review_ng}, ak.get("family"), ak.get("slug"), level))
        if errs:
            raise KpReviewError("選択が検証に失敗しました:\n- " + "\n- ".join(errs))
        # 反映
        prev_status = review["status"]
        review["ng"] = review_ng
        for e in new_ng:
            if ak.get("family"):
                store_add_ng(ak["family"], ak["slug"], level, e)
        selected = set(sum((list(v) for v in selection.values()), []))
        kp_set = set(sel_ids(selection, "kp")) | set(sel_ids(selection, "grammar"))
        verdicts = {}
        ng_all_ids = {e["candidate_id"] for e in review_ng}
        for cid in cm:
            if cid in kp_set:
                verdicts[cid] = "SELECTED_KP" if kind == KIND_KP else "SELECTED"
            elif cid in selected:
                verdicts[cid] = "SELECTED_VOCAB"
            elif cid in ng_all_ids:
                verdicts[cid] = "NG"
            else:
                verdicts[cid] = "NOT_SELECTED"
        review.update(selection=selection, accepted_qa_fail=accepted_qf, accept_ai_default=bool(accept_ai),
                      accept_ai_shown_candidates_sha256=(shown_candidates_sha256 if accept_ai else None),
                      verdicts=verdicts, status=ST_REVIEWED, last_human_op_at=_now(), mode_used=None, final_qa=None)
        _event(review, "select" if not accept_ai else "accept_ai", by,
               {"from": prev_status, "selection": selection, "ng": list(ng_cids), "accepted_qa_fail": accepted_qf})
        out = save_review(kp_dir, review, expected_revision=review["revision"], kind=kind)
        invalidate_gloss_snapshot(kp_dir)   # M-2: 選び直し時に未消費のgloss HR snapshot(旧選定)を失効させる
        return out


def op_reselect(kp_dir: str, *, ng: Optional[dict] = None, note: str = "", by: str, kind: str = KIND_KP) -> dict:
    """再選定要求。ng={ai_rank: reason}をNGへ。上限RESELECT_MAX/レベル/run。status=RESELECTION_REQUESTED(次回起動で候補再生成)。"""
    if not (by or "").strip():
        raise KpReviewError("--by(操作者)が必須です")
    with review_lock(kp_dir, kind, by):
        review = load_review(kp_dir, kind)
        cands = load_candidates(kp_dir, kind)
        if review is None or cands is None:
            raise KpReviewError("候補/reviewがありません")
        if review["status"] in (ST_RESELECT, ST_STALE):
            raise KpReviewError(f"status={review['status']}です(既に再選定要求済み/無効)")
        if review.get("reselect_count", 0) >= RESELECT_MAX:
            raise KpReviewError(f"再選定の上限({RESELECT_MAX}回/レベル/run)に達しています。Fableへ報告してください(推測で続行しません)")
        cm = _cand_map(cands)
        ak = review.get("article_key") or {}
        for rk, reason in (ng or {}).items():
            (cid,) = _rank_to_cid(cands, [rk])
            if not (reason or "").strip():
                raise KpReviewError(f"NG指定には理由が必要です(番号{rk})")
            ent = make_ng_entry(cm[cid], reason, by)
            if cid not in {e["candidate_id"] for e in review.get("ng") or []}:
                review.setdefault("ng", []).append(ent)
            if ak.get("family"):
                store_add_ng(ak["family"], ak["slug"], review["level"], ent)
            review["verdicts"][cid] = "NG"
        prev = review["status"]
        review.update(status=ST_RESELECT, reselect_count=review.get("reselect_count", 0) + 1, last_human_op_at=_now(),
                      selection={}, mode_used=None, final_qa=None)
        _event(review, "reselect", by, {"from": prev, "note": note, "ng": [cid for cid in review["verdicts"] if review["verdicts"][cid] == "NG"]})
        out = save_review(kp_dir, review, expected_revision=review["revision"], kind=kind)
        invalidate_gloss_snapshot(kp_dir)   # M-2
        return out


def op_ng(kp_dir: str, *, ng: dict, by: str, kind: str = KIND_KP) -> dict:
    """候補をNGにする(選択はしない)。以後の宣言は失効する(last_human_op_at更新)。"""
    with review_lock(kp_dir, kind, by):
        review, cands = load_review(kp_dir, kind), load_candidates(kp_dir, kind)
        if review is None or cands is None:
            raise KpReviewError("候補/reviewがありません")
        cm = _cand_map(cands)
        ak = review.get("article_key") or {}
        for rk, reason in ng.items():
            (cid,) = _rank_to_cid(cands, [rk])
            if not (reason or "").strip():
                raise KpReviewError("NG指定には理由が必要です")
            ent = make_ng_entry(cm[cid], reason, by)
            if cid not in {e["candidate_id"] for e in review.get("ng") or []}:
                review.setdefault("ng", []).append(ent)
            if ak.get("family"):
                store_add_ng(ak["family"], ak["slug"], review["level"], ent)
            review["verdicts"][cid] = "NG"
        review["last_human_op_at"] = _now()
        if review["status"] in FORWARD_STATUSES:
            sel = review.get("selection") or {}
            bad = [cid for cid in sum((list(v) for v in sel.values()), []) if cid in {e["candidate_id"] for e in review["ng"]}]
            if bad:
                review.update(status=ST_PENDING, selection={}, final_qa=None, mode_used=None)
                _event(review, "ng_removed_selection", by, {"ids": bad})
        _event(review, "ng", by, {"ids": [_rank_to_cid(cands, [r])[0] for r in ng]})
        return save_review(kp_dir, review, expected_revision=review["revision"], kind=kind)


def op_unng(kp_dir: str, *, rank: Optional[int] = None, phrase: Optional[str] = None, reason: str, by: str, kind: str = KIND_KP) -> list:
    """NG解除。理由・記録必須(R-2)。共有storeとrun内コピーの両方を更新。"""
    with review_lock(kp_dir, kind, by):
        review, cands = load_review(kp_dir, kind), load_candidates(kp_dir, kind)
        if review is None:
            raise KpReviewError("reviewがありません")
        cid = _rank_to_cid(cands, [rank])[0] if rank is not None else None
        ak = review.get("article_key") or {}
        removed = []
        if ak.get("family"):
            removed = store_remove_ng(ak["family"], ak["slug"], review["level"], candidate_id=cid, phrase=phrase, reason=reason, by=by)
        else:
            if not (reason or "").strip():
                raise KpReviewError("unngは --reason が必須です")
        for e in review.get("ng") or []:
            if (cid and e["candidate_id"] == cid) or (phrase and e.get("phrase_key") == phrase_key(phrase)):
                e["active"] = False
                e["removed"] = {"at": _now(), "by": by, "reason": reason}
                removed.append(e["candidate_id"])
        for r in removed:
            if review["verdicts"].get(r) == "NG":
                review["verdicts"][r] = None
        review["last_human_op_at"] = _now()
        _event(review, "unng", by, {"removed": sorted(set(removed)), "reason": reason})
        save_review(kp_dir, review, expected_revision=review["revision"], kind=kind)
        return sorted(set(removed))


def op_mark_published(kp_dir: str, *, by: str, kind: str = KIND_KP) -> dict:
    """R-5: 公開した時点の確定署名を別保存する。以後の事後Review(AUTO->REVIEWED等)で確定版が変わっても、公開版は自動では差し替えない
    (status/verifyが『公開版と確定版の差』として表示するだけ。差替えは別の明示操作)。"""
    if not (by or "").strip():
        raise KpReviewError("--by(操作者)が必須です")
    with review_lock(kp_dir, kind, by):
        review = load_review(kp_dir, kind)
        if review is None or review["status"] not in FORWARD_STATUSES:
            raise KpReviewError("確定済み(REVIEWED/UNREVIEWED_AUTO_ADOPTED)のreviewだけ公開済みとして記録できます")
        review["published_selection_signature"] = review["selection_signature"]
        _event(review, "mark_published", by, {"selection_signature": review["selection_signature"], "status": review["status"]})
        return save_review(kp_dir, review, expected_revision=review["revision"], kind=kind)


def published_diff(kp_dir: str, kind: str = KIND_KP) -> dict:
    """公開版(published_selection_signature)と現在の確定版の関係。差があっても自動差替えはしない(R-5)。"""
    r = load_review(kp_dir, kind)
    if r is None:
        return {"published": None, "current": None, "differs": False}
    pub, cur = r.get("published_selection_signature"), r.get("selection_signature")
    return {"published": pub, "current": cur, "differs": bool(pub and cur and pub != cur),
            "note": ("公開版と確定版が異なります(自動では差し替えません。差替えは明示操作)" if pub and cur and pub != cur else "")}


GLOSS_HR_SNAPSHOT = "gloss_alignment_pending_result.json"


def invalidate_gloss_snapshot(kp_dir: str) -> Optional[str]:
    """M-2: select/reselect等でHumanが選び直した時点で、未消費のgloss HR snapshot(旧選定を含みうる)を失効させる。"""
    p = f"{kp_dir}/{GLOSS_HR_SNAPSHOT}"
    if os.path.exists(p):
        return archive_if_exists(p, "INVALIDATED")
    return None


def op_resolve_gloss(kp_dir: str, *, rank: int, gloss: str, by: str, kind: str = KIND_KP) -> dict:
    """候補段階のgloss HR解消(既存ga.resolve_glossを再利用)。PENDING_REVIEWの間だけ可。候補sha更新→reviewの候補shaも更新。
    以後の宣言は失効する(last_human_op_at)。HR解消後、その候補は選択可能(AUTO対象になりうる)。"""
    import er003_key_words_gloss_alignment as ga
    with review_lock(kp_dir, kind, by):
        review, cands = load_review(kp_dir, kind), load_candidates(kp_dir, kind)
        if review is None or cands is None:
            raise KpReviewError("候補/reviewがありません")
        if review["status"] != ST_PENDING:
            raise KpReviewError(f"resolve-glossはPENDING_REVIEWの間だけ使えます(現在{review['status']})")
        c = next((x for x in cands["candidates"] if x["ai_rank"] == rank), None)
        if c is None:
            raise KpReviewError(f"番号{rank}の候補がありません")
        tmp = f"{kp_dir}/.resolve_gloss_tmp.json"
        doc = {"items": [json.loads(json.dumps(c["item"]))]}
        doc["items"][0]["rank"] = rank
        _write_json_atomic(tmp, doc)
        try:
            ga.resolve_gloss(tmp, rank, gloss, by)
            new_item = _read_json(tmp)["items"][0]
        finally:
            for pth in (tmp, f"{kp_dir}/GLOSS_ALIGNMENT_HUMAN_RESOLUTIONS_01.jsonl"):
                if pth == tmp and os.path.exists(pth):
                    os.remove(pth)
        new_item["rank"] = c["item"].get("rank", rank)
        c["item"] = new_item
        c["japanese_gloss"] = new_item.get("japanese_gloss")
        c["flags"]["gloss_hr_pending"] = False
        c["gates"]["gloss"] = "HUMAN_RESOLVED"
        c["auto_eligible"] = bool(not c["flags"].get("qa_fail") and not c["flags"].get("similar_to_ng"))
        cands = save_candidates(kp_dir, cands, kind)
        review["candidates_sha256"] = cands["candidates_sha256"]
        review["last_human_op_at"] = _now()
        _event(review, "resolve_gloss", by, {"rank": rank})
        save_review(kp_dir, review, expected_revision=review["revision"], kind=kind)
        invalidate_gloss_snapshot(kp_dir)
        return c


# ============================================================
# 候補ファイルの保存(runner/生成側が呼ぶ)
# ============================================================
def archive_if_exists(path: str, tag: str) -> Optional[str]:
    if not os.path.exists(path):
        return None
    base, ext = os.path.splitext(path)
    n = 1
    while os.path.exists(f"{base}.{tag}_{n}{ext}"):
        n += 1
    dst = f"{base}.{tag}_{n}{ext}"
    os.replace(path, dst)
    return dst


def save_candidates(kp_dir: str, doc: dict, kind: str = KIND_KP) -> dict:
    doc = dict(doc)
    doc["schema"] = SCHEMA_CANDIDATES
    doc["kind"] = kind
    doc["candidates_sha256"] = candidates_sha256(doc)
    pth = paths(kp_dir, kind)
    _write_json_atomic(pth["candidates"], doc)
    rd = f"{pth['rounds']}/round_{doc.get('round', 1)}"
    _write_json_atomic(f"{rd}/{FILE_PREFIX[kind]}_candidates.json", doc)
    return doc


def retire_final_outputs(kp_dir: str, tag: str) -> list:
    """本文変更(STALE)/再選定時: 旧確定物をSUPERSEDEDへ退避し、後段が旧KPを読めないようにする(M-1の不変条件)。"""
    out = []
    pth = paths(kp_dir)
    for key in ("kp", "vocab", "final"):
        d = archive_if_exists(pth[key], tag)
        if d:
            out.append(d)
    return out


# ============================================================
# finalize(M-8: 確定集合へのRedundancy QA再適用。M-1: 本名ファイルを書けるのはここだけ)
# ============================================================
def _final_items(cands: dict, ids: list) -> list:
    cm = _cand_map(cands)
    items = []
    for n, cid in enumerate(sorted(ids, key=lambda i: cm[i]["ai_rank"]), start=1):
        c = cm[cid]
        it = json.loads(json.dumps(c["item"]))
        it["rank"] = n
        it["candidate_id"] = cid
        it["ai_rank"] = c["ai_rank"]
        items.append(it)
    return items


def _qa_key(sel: dict) -> str:
    return jsha({k: sorted(v) for k, v in sel.items()})


def _run_final_qa(cands: dict, selection: dict, level: str, redundancy_fn: Optional[Callable]) -> dict:
    """確定KP集合(Advはvocab集合も)に対するRedundancy QA。returns {"status","ng_pairs":[(candidate_id_a, candidate_id_b)], "results":{...}}。"""
    res = {"status": "REDUNDANCY_PASS", "ng_pairs": [], "results": {}, "key": _qa_key(selection)}
    sets = [("kp", sel_ids(selection, "kp"))]
    if level == "b1b" and set(sel_ids(selection, "vocab")) != set(sel_ids(selection, "kp")):
        sets.append(("vocab", sel_ids(selection, "vocab")))
    cm = _cand_map(cands)
    for name, ids in sets:
        if len(ids) < 2:
            res["results"][name] = {"status": "REDUNDANCY_PASS", "skipped": "ペアが無い(2件未満)"}
            continue
        if redundancy_fn is None:
            raise KpReviewError("finalizeにはRedundancy QA関数(redundancy_fn)が必要です(確定集合へのQA再適用=M-8。省略しません)")
        items = _final_items(cands, ids)
        r = redundancy_fn(items, name)
        st = r.get("status")
        res["results"][name] = {"status": st, "duplicate_pairs": r.get("duplicate_pairs") or [], "model_id": r.get("model_id")}
        if st == "REDUNDANCY_NG":
            res["status"] = "REDUNDANCY_NG"
            rank_to_cid = {it["rank"]: it["candidate_id"] for it in items}
            for p in r.get("duplicate_pairs") or []:
                a, b = rank_to_cid.get(p.get("rank_a")), rank_to_cid.get(p.get("rank_b"))
                if a and b:
                    res["ng_pairs"].append((a, b))
        elif st != "REDUNDANCY_PASS":
            raise KpReviewError(f"確定集合のRedundancy QAが判定不能です(status={st}, set={name})。fail-closedで停止します")
    return res


def finalize_kp(kp_dir: str, *, level: str, redundancy_fn: Optional[Callable] = None, ng_scope: Optional[dict] = None) -> dict:
    """review(REVIEWED/UNREVIEWED_AUTO_ADOPTED)から確定物を書く。idempotent: 署名が同じなら本名ファイルは書き直さない
    (後段のgloss修復・SRC D1・resolve_glossの編集を壊さない)。returns {"review","items","vocab_items","signature","wrote"}。
    Humanの確定が確定集合のRedundancy QAでNGなら PENDING_REVIEW に戻して KpReviewPending。"""
    pth = paths(kp_dir)
    with review_lock(kp_dir, KIND_KP, "finalize"):
        review, cands = load_review(kp_dir), load_candidates(kp_dir)
        if review is None or cands is None:
            raise KpReviewError("finalize: 候補/reviewがありません")
        if review["status"] not in FORWARD_STATUSES:
            raise KpReviewError(f"finalize: status={review['status']}は確定できません(REVIEWED/UNREVIEWED_AUTO_ADOPTEDのみ)")
        if review["candidates_sha256"] != cands["candidates_sha256"]:
            raise KpReviewInconsistent("finalize: reviewと候補のcandidates_sha256が不一致(手編集の疑い)。fail-closed")
        ak = review.get("article_key") or {}
        ng_ent = ng_entries_of(review, ak.get("family"), ak.get("slug"), level)
        sel = review.get("selection") or {}
        errs = validate_selection(cands, sel, level=level, accepted_qa_fail=review.get("accepted_qa_fail"), ng_entries=ng_ent)
        if errs:
            raise KpReviewInconsistent("finalize: 選択が再検証に失敗しました:\n- " + "\n- ".join(errs))
        # M-8
        fq = review.get("final_qa")
        dirty = review.get("selection_signature") is None
        if not fq or fq.get("key") != _qa_key(sel) or fq.get("status") != "REDUNDANCY_PASS":
            dirty = True
            if review["status"] == ST_AUTO:
                excluded = list((review.get("auto_qa_excluded") or []))
                for _ in range(AUTO_QA_ADVANCE_MAX + 1):
                    fq = _run_final_qa(cands, sel, level, redundancy_fn)
                    if fq["status"] == "REDUNDANCY_PASS":
                        break
                    # AUTO: 重複ペアの下位(ai_rankが大きい方)を除外して次候補へ繰り上げ、再判定
                    cm = _cand_map(cands)
                    drop = [max(p, key=lambda i: cm[i]["ai_rank"]) for p in fq["ng_pairs"][:1]]
                    excluded += drop
                    review["auto_qa_excluded"] = excluded
                    _event(review, "auto_advance_final_redundancy_ng", "runner", {"excluded": drop})
                    sel = auto_select(cands, level=level, ng_entries=ng_ent, excluded_ids=excluded)
                    if not sel_ids(sel, "kp"):
                        raise KpReviewError("AUTO: 確定集合のRedundancy QAで採用可能な候補が尽きました(STOP)")
                else:
                    raise KpReviewError(f"AUTO: 確定集合のRedundancy QAが{AUTO_QA_ADVANCE_MAX}回の繰り上げでも解消しません(STOP)")
                review["selection"] = sel
                review["final_qa"] = fq
            else:
                fq = _run_final_qa(cands, sel, level, redundancy_fn)
                if fq["status"] != "REDUNDANCY_PASS":
                    review.update(status=ST_PENDING, selection={}, final_qa=None, mode_used=None)
                    _event(review, "final_redundancy_ng", "runner", {"pairs": [list(p) for p in fq["ng_pairs"]]})
                    save_review(kp_dir, review, expected_revision=review["revision"])
                    raise KpReviewPending("確定集合のRedundancy QAがNGでした。選び直してください", [
                        {"level": level, "kp_dir": kp_dir, "reason": "final_redundancy_ng", "request_md": pth["request"]}])
                review["final_qa"] = fq
        if dirty:
            review = save_review(kp_dir, review, expected_revision=review["revision"])
        sig = review["selection_signature"]
        kp_ids, vocab_ids = sel_ids(review["selection"], "kp"), sel_ids(review["selection"], "vocab")
        items = _final_items(cands, kp_ids)
        vocab_items = _final_items(cands, vocab_ids) if level == "b1b" else []
        for it in items + vocab_items:
            if it["candidate_id"] in set(review.get("accepted_qa_fail") or []):
                it["human_accepted_qa_fail"] = True
        wrote = []
        cur = _read_json(pth["kp"]) if os.path.exists(pth["kp"]) else None
        if cur is None or cur.get("kp_selection_signature") != sig:
            overall = "PASS" if not any(it.get("human_accepted_qa_fail") for it in items) else "REVIEW_REQUIRED_HUMAN_ACCEPTED"
            _write_json_atomic(pth["kp"], {"items": items, "overall_status": overall, "kp_selection_signature": sig,
                                           "kp_review_status": review["status"]})
            wrote.append("keywords_canonicalized.json")
        if level == "b1b":
            curv = _read_json(pth["vocab"]) if os.path.exists(pth["vocab"]) else None
            if curv is None or curv.get("kp_selection_signature") != sig:
                _write_json_atomic(pth["vocab"], {"items": vocab_items, "kp_selection_signature": sig, "kp_review_status": review["status"]})
                wrote.append("vocab_confirmed.json")
        elif os.path.exists(pth["vocab"]):
            os.replace(pth["vocab"], pth["vocab"] + ".removed")
        final = {"schema": SCHEMA_FINAL, "level": level, "review_status": review["status"], "selection_signature": sig,
                 "text_sha256": review["text_sha256"], "candidates_sha256": review["candidates_sha256"],
                 "round": review.get("round", 1), "selection": review["selection"],
                 "ng_candidate_ids": sorted(e["candidate_id"] for e in ng_ent), "final_redundancy_qa": review.get("final_qa"),
                 "mode_used": review.get("mode_used"), "finalized_at": _now()}
        curf = _read_json(pth["final"]) if os.path.exists(pth["final"]) else None
        if curf is None or curf.get("selection_signature") != sig:
            _write_json_atomic(pth["final"], final)
            wrote.append("kp_selection_final.json")
        return {"review": review, "items": items, "vocab_items": vocab_items, "signature": sig, "wrote": wrote}


# ============================================================
# 消費側の検査(全消費者の入口)
# ============================================================
def has_review(kp_dir: str) -> bool:
    p = paths(kp_dir)
    return os.path.exists(p["review"]) or os.path.exists(p["candidates"])


def _consumer_checks(items: list, *, require_src_contract: bool) -> list:
    """M-9: vocab itemにも既存の消費側検査を適用する(collect_unresolved / select_consumer_unevaluated / Z SRC has_contract)。"""
    problems = []
    import er003_key_words_gloss_alignment as ga
    unres = ga.collect_unresolved({"items": items})
    if unres:
        problems.append(f"gloss HR待ちitemが残っています(rank={[x.get('rank') for x in unres]})")
    uneval = ga.select_consumer_unevaluated(items) if ga.flag_enabled() else ga.select_fulltext_gloss_missing(items)
    if uneval:
        problems.append(f"gloss未評価/未生成itemがあります(rank={[x.get('rank') for x in uneval]})")
    if require_src_contract:
        import er026_family_z_src_posthoc_01 as srcz
        if not srcz.has_contract({"items": items}):
            problems.append("Z SRC D1(source_reference_contract)が未適用のitemがあります")
    return problems


def require_final_consistent(kp_dir: str, *, level: Optional[str] = None, require_src_contract: bool = False) -> Optional[dict]:
    """全消費者の入口で呼ぶ(DESIGN c-2)。review/候補が無い旧run=None(旧run互換)。reviewがあるのに不整合ならKpReviewInconsistent(次コマンド付き)。
    (i)statusが前進可 (ii)selection_signature再計算が一致 (iii)keywords_canonicalized.jsonのcandidate_id集合=selection.kp (iv)vocab_confirmed.json=selection.vocab(Adv)
    (v)NG交差0 (vi)vocab itemにも消費側検査(M-9)。"""
    pth = paths(kp_dir)
    if not has_review(kp_dir):
        return None
    nxt = "(次の一手: 制作コマンドを再実行して確定させる/ er119_kp_human_review_cli_01.py status --run <run>)"
    review, cands = load_review(kp_dir), load_candidates(kp_dir)
    if review is None or cands is None:
        raise KpReviewInconsistent(f"KP_REVIEW_INCONSISTENT: review/候補ファイルのどちらかが欠落しています{nxt}")
    if review["status"] not in FORWARD_STATUSES:
        raise KpReviewNotConfirmed(f"KP_REVIEW_NOT_CONFIRMED: status={review['status']}。Human確認(select)か明示の不在宣言が必要です{nxt}")
    lv = level or review["level"]
    if selection_signature(review) != review.get("selection_signature"):
        raise KpReviewInconsistent(f"KP_REVIEW_SIGNATURE_MISMATCH: kp_human_review.jsonの署名が不一致(手編集の疑い){nxt}")
    if review["candidates_sha256"] != cands["candidates_sha256"] or candidates_sha256(cands) != cands["candidates_sha256"]:
        raise KpReviewInconsistent(f"KP_CANDIDATES_SIGNATURE_MISMATCH: 候補ファイルが改変されています{nxt}")
    for p in (pth["final"], pth["kp"]) + ((pth["vocab"],) if lv == "b1b" else ()):
        if not os.path.exists(p):
            raise KpReviewInconsistent(f"KP_FINAL_MISSING: {p}がありません(確定前、または退避済み){nxt}")
    final = _read_json(pth["final"])
    if final.get("selection_signature") != review["selection_signature"]:
        raise KpReviewInconsistent(f"KP_FINAL_SIGNATURE_MISMATCH: kp_selection_final.jsonがreviewと不一致{nxt}")
    kp_doc = _read_json(pth["kp"])
    sel = review["selection"]
    if sorted(it.get("candidate_id") for it in kp_doc.get("items") or []) != sorted(sel_ids(sel, "kp")):
        raise KpReviewInconsistent(f"KP_SELECTION_MISMATCH: keywords_canonicalized.jsonの候補がreview.selection.kpと一致しません(旧KPの混入の疑い){nxt}")
    if lv == "b1b":
        vdoc = _read_json(pth["vocab"])
        if sorted(it.get("candidate_id") for it in vdoc.get("items") or []) != sorted(sel_ids(sel, "vocab")):
            raise KpReviewInconsistent(f"KP_VOCAB_MISMATCH: vocab_confirmed.jsonがreview.selection.vocabと一致しません{nxt}")
        problems = _consumer_checks(vdoc.get("items") or [], require_src_contract=require_src_contract)
        if problems:
            raise KpReviewInconsistent("KP_VOCAB_CONSUMER_CHECK_FAILED: " + " / ".join(problems))
    ak = review.get("article_key") or {}
    ng_ids = {e["candidate_id"] for e in ng_entries_of(review, ak.get("family"), ak.get("slug"), lv)}
    used = set(sel_ids(sel, "kp")) | set(sel_ids(sel, "vocab"))
    if used & ng_ids:
        raise KpReviewInconsistent(f"KP_NG_INTERSECTION: NG候補が確定集合に含まれています({sorted(used & ng_ids)})")
    return review


def part1_items(kp_dir: str) -> list:
    """Part 1(単語解説)の入力の単一アクセサ(M-9)。reviewが存在するならvocab_confirmed.jsonが必須(fail-closed、
    3件へ黙って戻らない)。reviewが無い旧runだけ keywords_canonicalized.json(従来)。KPと同じcandidateのitemは
    後段修復(gloss/SRC)後のKP artifactを正としてoverlayする(rankはvocab側の連番を保つ)。KP側rankで他ファイルと結合しない。"""
    pth = paths(kp_dir)
    if not has_review(kp_dir):
        if not os.path.exists(pth["kp"]):
            raise KpReviewError(f"[STOP][Part 1] {pth['kp']}がありません(KP stage未完了)")
        items = _read_json(pth["kp"]).get("items") or []
        if not items:
            raise KpReviewError(f"[STOP][Part 1] {pth['kp']}のitemsが空です")
        return sorted(items, key=lambda x: x["rank"])
    if not os.path.exists(pth["vocab"]):
        raise KpReviewError(f"[STOP][Part 1] {pth['vocab']}がありません。KP Human Reviewが未確定、または生成漏れです(旧KP3件へは戻しません)")
    vdoc = _read_json(pth["vocab"])
    vitems = sorted(vdoc.get("items") or [], key=lambda x: x["rank"])
    if not vitems:
        raise KpReviewError(f"[STOP][Part 1] {pth['vocab']}のitemsが空です")
    kp_by_cid = {}
    if os.path.exists(pth["kp"]):
        kp_by_cid = {it.get("candidate_id"): it for it in _read_json(pth["kp"]).get("items") or []}
    out = []
    for n, v in enumerate(vitems, start=1):
        base = kp_by_cid.get(v.get("candidate_id"))
        it = json.loads(json.dumps(base if base is not None else v))
        it["rank"] = n   # vocab側の連番(KP側rankは使わない)
        it["candidate_id"] = v.get("candidate_id")
        out.append(it)
    return out


def verify_selection_matches_outputs(kp_dir: str, *, level: str, tts_results_path: Optional[str] = None,
                                     study_text_json: Optional[str] = None, page_paths: Optional[list] = None,
                                     vocab_page_paths: Optional[list] = None, require_src_contract: bool = False) -> dict:
    """検証5(DESIGN d): 選定結果=実際に音声化・公開された内容。決定論・API 0。不一致=KpReviewInconsistent。
    確定JSON(review/kp_selection_final) <-> keywords_canonicalized.json <-> TTS結果のkp英語text <-> study_text(Part 1の行) <-> 公開ページHTML。
    reviewが無い旧runは対象外(report={"legacy": True})。"""
    import html as _html
    review = require_final_consistent(kp_dir, level=level, require_src_contract=require_src_contract)
    if review is None:
        return {"legacy": True, "ok": True}
    pth = paths(kp_dir)
    kp_items = sorted(_read_json(pth["kp"]).get("items") or [], key=lambda x: x["rank"])
    problems = []
    if tts_results_path:
        if not os.path.exists(tts_results_path):
            problems.append(f"TTS結果がありません: {tts_results_path}")
        else:
            kps = _read_json(tts_results_path).get("key_phrases") or {}
            want = [it["used_form"] for it in kp_items]
            got = [((kps.get(str(it["rank"])) or {}).get("english") or {}).get("text") for it in kp_items]
            if len(kps) != len(kp_items):
                problems.append(f"TTSのKP件数({len(kps)})が確定KP({len(kp_items)})と一致しません")
            if got != want:
                problems.append(f"TTSのKP英語text {got} が確定KP {want} と一致しません")
    vocab_items = []
    if level == "b1b":
        vocab_items = part1_items(kp_dir)
        if study_text_json:
            if not os.path.exists(study_text_json):
                problems.append(f"study_text(Part 1)がありません: {study_text_json}")
            else:
                rows = _read_json(study_text_json).get("rows") or []
                want_v = [it["used_form"] for it in vocab_items]
                got_v = [r.get("english_expression") for r in rows]
                if got_v != want_v:
                    problems.append(f"Part 1の英語表現 {got_v} が確定vocab {want_v} と一致しません")
    def _page_text(pg):
        with open(pg, encoding="utf-8") as f:
            return _html.unescape(f.read())
    for pg in page_paths or []:   # KPを表示するページ
        if not os.path.exists(pg):
            problems.append(f"公開ページがありません: {pg}")
            continue
        hv = _page_text(pg)
        for it in kp_items:
            if it["used_form"] not in hv:
                problems.append(f"{os.path.basename(pg)}にKP「{it['used_form']}」がありません")
    for pg in vocab_page_paths or []:   # Part 1(単語解説)を表示するページ(訳欄の判断記録が無い間はページに描画されないので、呼出側が渡すかを決める)
        if not os.path.exists(pg):
            problems.append(f"公開ページがありません: {pg}")
            continue
        hv = _page_text(pg)
        for it in vocab_items:
            if it["used_form"] not in hv:
                problems.append(f"{os.path.basename(pg)}にPart 1の表現「{it['used_form']}」がありません")
    if problems:
        raise KpReviewInconsistent("KP_SELECTION_OUTPUT_MISMATCH: " + " / ".join(problems))
    return {"legacy": False, "ok": True, "signature": review["selection_signature"], "kp": [it["used_form"] for it in kp_items],
            "vocab": [it["used_form"] for it in vocab_items]}


# ============================================================
# 提示(kp_human_review_request.md)
# ============================================================
def cli_prefix() -> str:
    return "py er119_kp_human_review_cli_01.py"


def render_request_md(cands: dict, review: dict, *, run_hint: str, ng_entries: Optional[list] = None) -> str:
    level = cands["level"]
    ng_entries = ng_entries or []
    rec = auto_select(cands, level=level, ng_entries=ng_entries)
    top_kp = {cid for cid in sel_ids(rec, "kp")}
    top_vocab = {cid for cid in sel_ids(rec, "vocab")}
    lines = [f"# KP Human Review 依頼({level}) round {cands.get('round', 1)}", "",
             f"- 状態: {review.get('status')} / candidates_sha256: `{cands['candidates_sha256'][:16]}` / 本文sha: `{cands['text_sha256'][:12]}`",
             "- あなたの作業: KPに使う最大3件" + ("と、単語解説に使う最大5件(KP3件を含む)" if level == "b1b" else "") + "を選びます。",
             "- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。", "",
             "| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |", "|---|---|---|---|---|---|---|"]
    for c in sorted(cands.get("candidates") or [], key=lambda x: x["ai_rank"]):
        cid = c["candidate_id"]
        mark = "KP" if cid in top_kp else ("単語" if cid in top_vocab else "")
        flags = []
        f = c.get("flags") or {}
        if f.get("qa_fail"):
            flags.append("QA FAIL(採用には --accept-qa-fail)")
        if f.get("gloss_hr_pending"):
            flags.append("gloss HR待ち(resolve-gloss必要)")
        if f.get("redundant_with"):
            flags.append("重複: " + ",".join(str(next((x['ai_rank'] for x in cands['candidates'] if x['candidate_id'] == o), '?')) for o in f["redundant_with"]))
        m = match_ng(c, ng_entries)
        if m == "exact":
            flags.append("NG済み")
        elif m == "similar":
            flags.append("NG句に類似(AUTO対象外)")
        if not c.get("auto_eligible"):
            flags.append("AUTO対象外")
        cell = lambda s: (s or "").replace("|", "/").replace("\n", " ")   # noqa: E731
        lines.append(f"| {c['ai_rank']} | {mark} | {cell(c.get('used_form'))} | {cell(c.get('japanese_gloss'))} | {cell(c.get('source_sentence'))} | {cell(c.get('reason_ja'))} | {' / '.join(flags)} |")
    d = cands.get("dropped") or []
    if d:
        lines += ["", "## Gateで除外された候補(参考)", ""]
        for x in d:
            lines.append(f"- {x.get('phrase')} : {x.get('stage')} : {' / '.join(x.get('reasons') or [])}")
    p = cli_prefix()
    lines += ["", "## 操作(コマンド)", "",
              f"- 状況確認: `{p} status --run {run_hint}`",
              f"- AI推奨を了承: `{p} select --run {run_hint} --level {level} --accept-ai --candidates-sha {cands['candidates_sha256']} --by <名前>`",
              f"- 選択: `{p} select --run {run_hint} --level {level} --kp 1,2,3" + (" --vocab 1,2,3,4,5" if level == "b1b" else "") + " [--ng 6:理由] --by <名前>`",
              f"- 選び直し(NG付き): `{p} reselect --run {run_hint} --level {level} --ng 4:理由 --by <名前>`(上限{RESELECT_MAX}回)",
              f"- 不在として進める(明示宣言): `{p} declare-absent --runs {run_hint} --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`",
              "", "再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。"]
    return "\n".join(lines) + "\n"


# ============================================================
# 状態一覧(CLI status / 運用)
# ============================================================
def discover_kp_dirs(run_dir: str) -> list:
    """X: <run>/<level>/key_phrases / Z: <run>/key_phrases/<level>。review/候補ファイルのあるdirだけ返す。"""
    out = []
    for lv in ("a2", "b1b"):
        for d in (f"{run_dir}/{lv}/key_phrases", f"{run_dir}/key_phrases/{lv}"):
            if os.path.isdir(d) and has_review(d):
                out.append(d)
    return out


def status_of(kp_dir: str) -> dict:
    review, cands = load_review(kp_dir), load_candidates(kp_dir)
    if review is None:
        return {"kp_dir": kp_dir, "status": "NO_REVIEW" if cands is None else "NO_REVIEW_FILE"}
    return {"kp_dir": kp_dir, "level": review.get("level"), "status": review["status"], "round": review.get("round"),
            "reselect_count": review.get("reselect_count"), "candidates_sha256": review.get("candidates_sha256"),
            "selection": review.get("selection"), "accept_ai_default": review.get("accept_ai_default"),
            "mode_used": review.get("mode_used"), "revision": review.get("revision"),
            "published": published_diff(kp_dir)}


def pending_summary(kp_dir: str, level: str) -> dict:
    return {"level": level, "kp_dir": kp_dir, "request_md": paths(kp_dir)["request"], "status": (load_review(kp_dir) or {}).get("status")}


# ============================================================
# 確定フロー全体(runner共通。LLM呼出は注入関数のみ)
# ============================================================
def ensure_kp_review(kp_dir: str, *, run_dir: str, family: str, slug: str, level: str, text: str,
                     generate_fn: Callable, redundancy_fn: Optional[Callable], run_hint: Optional[str] = None) -> dict:
    """候補生成→(Human確認 or 明示宣言のAUTO)→finalize。
    returns {"state":"FINALIZED","final":{...}} / {"state":"PENDING","pending":{...}} / {"state":"FAILED","status":..,"detail":..}
    generate_fn(round_no, ng_entries) -> {"ok":True,"doc":cands_doc_without_sha} | {"ok":False,"status":"OUTER_RETRY_EXHAUSTED",...}。
    resume(候補sha一致)は再選定せずAPI 0。確定済みreviewは再選定しない(reselectのみ)。"""
    pth = paths(kp_dir)
    os.makedirs(kp_dir, exist_ok=True)
    text_sha = sha256_text(text)
    article_key = {"family": family, "slug": slug, "level": level}
    run_hint = run_hint or run_dir
    cands, review = load_candidates(kp_dir), load_review(kp_dir)
    # 候補/reviewの整合(片方だけ・本文変更)
    if cands is not None and review is None:
        raise KpReviewInconsistent("候補ファイルだけがあり、reviewがありません(手動削除の疑い)。fail-closed。状況をFableへ報告してください")
    if cands is not None and cands.get("text_sha256") != text_sha:
        # 本文が変わった(Writer再生成): 旧候補/review/確定物をSUPERSEDEDへ退避しNGは保持して候補を再生成(STALE)
        tag = "SUPERSEDED"
        archive_if_exists(pth["candidates"], tag)
        old_rv = archive_if_exists(pth["review"], tag)
        retire_final_outputs(kp_dir, tag)
        prev = dict(review or {})
        prev["history"] = list(prev.get("history") or []) + [{"at": _now(), "event": "stale_text_changed", "by": "runner",
                                                              "detail": {"old": cands.get("text_sha256"), "new": text_sha}}]
        prev["reselect_count"] = 0
        cands, review = None, None
        carry = prev
    else:
        carry = None
    generated = False
    if cands is None or review is None or review["status"] == ST_RESELECT:
        prev_review = review or carry
        round_no = (review.get("round", 1) + 1) if (review and review["status"] == ST_RESELECT) else 1
        ng_entries = ng_entries_of(prev_review, family, slug, level)
        if review and review["status"] == ST_RESELECT:
            archive_if_exists(pth["candidates"], "SUPERSEDED")
            retire_final_outputs(kp_dir, "SUPERSEDED")
        gen = generate_fn(round_no, ng_entries)
        if not gen.get("ok"):
            return {"state": "FAILED", "status": gen.get("status", "OUTER_RETRY_EXHAUSTED"), "detail": gen}
        doc = dict(gen["doc"])
        doc["level"], doc["text_sha256"], doc["round"] = level, text_sha, round_no
        doc = save_candidates(kp_dir, doc)
        with review_lock(kp_dir, KIND_KP, "runner"):
            if review is not None:   # RESELECTION_REQUESTED -> 新round
                rv = new_review(doc, article_key=article_key, prev=review)
                rv["revision"] = review["revision"]
                rv = save_review(kp_dir, rv, expected_revision=review["revision"])
            else:
                rv = new_review(doc, article_key=article_key, prev=carry)
                rv = save_review(kp_dir, rv, expected_revision=None)
        cands, review, generated = doc, rv, True
    # PENDING: 明示宣言があればAUTO
    if review["status"] == ST_PENDING:
        decl = read_mode_declaration(run_dir, family=family, level=level, review=review, round_no=review.get("round", 1),
                                     cands_sha=review["candidates_sha256"])
        if decl is not None:
            ng_ent = ng_entries_of(review, family, slug, level)
            sel = auto_select(cands, level=level, ng_entries=ng_ent)
            if not sel_ids(sel, "kp"):
                raise KpReviewError("AUTO: 採用可能な候補が0件です(OUTER_RETRY_EXHAUSTED相当のSTOP)。Humanが選ぶか再生成が必要です")
            with review_lock(kp_dir, KIND_KP, "runner"):
                review = load_review(kp_dir)
                review.update(status=ST_AUTO, selection=sel, mode_used={"declaration_id": decl.get("declaration_id"),
                                                                       "declared_by": decl.get("declared_by"), "source": decl.get("source"),
                                                                       "reason": decl.get("reason"), "user_ref": decl.get("user_ref")},
                              verdicts={c["candidate_id"]: None for c in cands["candidates"]})
                _event(review, "auto_adopted", "runner", {"declaration_id": decl.get("declaration_id"), "selection": sel})
                review = save_review(kp_dir, review, expected_revision=review["revision"])
        else:
            ng_ent = ng_entries_of(review, family, slug, level)
            _write_text_atomic(pth["request"], render_request_md(cands, review, run_hint=run_hint, ng_entries=ng_ent))
            return {"state": "PENDING", "pending": pending_summary(kp_dir, level), "generated": generated}
    if review["status"] in FORWARD_STATUSES:
        try:
            fin = finalize_kp(kp_dir, level=level, redundancy_fn=redundancy_fn)
        except KpReviewPending:
            rv2 = load_review(kp_dir)
            ng_ent = ng_entries_of(rv2, family, slug, level)
            _write_text_atomic(pth["request"], render_request_md(cands, rv2, run_hint=run_hint, ng_entries=ng_ent))
            return {"state": "PENDING", "pending": pending_summary(kp_dir, level), "generated": generated}
        return {"state": "FINALIZED", "final": fin, "generated": generated}
    raise KpReviewError(f"想定外のstatus={review['status']}")


def raise_if_pending(results: dict) -> None:
    """複数レベルの結果をまとめ、1つでもPENDINGなら1回だけKpReviewPendingを送出する(レベル往復を最小化)。"""
    pend = [r["pending"] for r in results.values() if r.get("state") == "PENDING"]
    if pend:
        raise KpReviewPending(f"{PENDING_MARKER} KP Human Review待ち: " + ", ".join(p["level"] for p in pend), pend)
